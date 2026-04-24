#!/usr/bin/env python3
"""
render_dashboard.py — generate the Alex interactive dashboard HTML.

Reads:
  - example-graph.yaml     (nodes + provenance)
  - alex-vocab.md          (glossary)
  - alex-actions.md        (open threads / live-work cards)
  - alex-needs-eyes.md     (items needing external review)

Writes:
  - example-graph-dashboard.html  (single self-contained file, inline CSS/JS/data)

Layout: concentric mandala — NOW at center, rings outward by type.
  Ring 0  NOW
  Ring 1  practice  (PR* / P* / KT*)
  Ring 2  emergent  (E*)
  Ring 3  overlap   (O*)
  Ring 4  novel     (N*)
  Ring 5  observation
  Ring 6  equivalency (EQ*)
  Ring 7  reference (R*)
  Ring 8  open questions (OQ*)

Interactions (vanilla JS, no libs):
  - mandala SVG with zoom (wheel), pan (drag empty), dbl-click to reset
  - hover node → tooltip + edge highlight
  - click node → right-rail swaps to detail view (related subgraph)
  - Esc / click empty → deselect, right rail back to "Today"
  - live search filters nodes
  - toggle mandala ↔ force-directed (Fruchterman-Reingold, ~200 iters)
  - localStorage persistence of layout choice

Requires: pyyaml only.
"""

import json
import math
import re
import sys
from collections import defaultdict, deque
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("ERROR: install pyyaml — pip install pyyaml")


# ──────────────────────────────────────────────────────────────────────────
#  Paths
# ──────────────────────────────────────────────────────────────────────────
HERE         = Path(__file__).resolve().parent
YAML_PATH    = HERE / "example-graph-extended.yaml"
VOCAB_PATH   = HERE / "alex-vocab.md"
ACTIONS_PATH = HERE / "alex-actions.md"
EYES_PATH    = HERE / "alex-needs-eyes.md"
OUT_PATH     = HERE / "example-graph-extended.html"
MIRROR_PATH  = Path("/Users/parrik/Documents/parrik/public/alex-case-study.html")


# ──────────────────────────────────────────────────────────────────────────
#  Schema — rings, colors, labels, notes
# ──────────────────────────────────────────────────────────────────────────
TYPE_RING = {
    "now":         0,
    "practice":    1,
    "emergent":    2,
    "overlap":     3,
    "novel":       4,
    "observation": 5,
    "equivalency": 6,
    "reference":   7,
    "open":        8,
}

# Pixel radii per ring, in SVG user units (before viewBox zoom).
RING_RADIUS = [0, 120, 220, 320, 420, 520, 610, 690, 760]

RING_LABEL = {
    0: "NOW",
    1: "PRACTICE",
    2: "EMERGENT",
    3: "OVERLAP",
    4: "NOVEL",
    5: "OBSERVATION",
    6: "EQUIVALENCY",
    7: "REFERENCE",
    8: "OPEN QUESTION",
}

# Legend ordering (top-to-bottom).
LEGEND_ORDER = [
    "now", "practice", "emergent", "overlap", "novel",
    "observation", "equivalency", "reference", "open",
]

# Short notes surfaced in the node-detail explainer.
TYPE_NOTE = {
    "now":         "the orienting pointer. Everything else is context for what this node puts in front of you.",
    "practice":    "a derived rule you actually act on. Operational output of the graph; protected against erosion.",
    "emergent":    "a claim produced by the intersection of parents. Not present in any single input.",
    "overlap":     "a pattern corroborated across independent instances. Stronger evidence than any single observation.",
    "novel":       "a tentative interpretation. Single derivation, held lightly. Promoted to Overlap only when a second independent instance shows.",
    "observation": "a dated event. The raw material the rest of the graph is built from.",
    "equivalency": "two things naming the same underlying shape. Useful for detecting when a category is really a proxy.",
    "reference":   "a biographical fact or external lens. Load-bearing and stable; treat as input, not conclusion.",
    "open":        "an unresolved edge of the map. Marked so it is not quietly absorbed into an assumed answer.",
}

RISK_PIVOT  = "O01-first-three-months"
LEVER_NODE  = "KT01-know-thyself"   # for "single lever" link in Today panel


# ──────────────────────────────────────────────────────────────────────────
#  YAML loading
# ──────────────────────────────────────────────────────────────────────────
def load_nodes(path: Path):
    with open(path) as f:
        nodes = yaml.safe_load(f)
    if not isinstance(nodes, list):
        sys.exit("YAML must be a top-level list of nodes.")
    # Drop shelved nodes if any
    nodes = [n for n in nodes if not n.get("shelved")]
    return nodes


def derivation_sources(node):
    deriv = (node.get("provenance") or {}).get("derivation") or {}
    return [s for s in (deriv.get("from") or []) if s]


def evidence_references(node):
    ev = (node.get("provenance") or {}).get("evidence") or {}
    refs = ev.get("references") or []
    return [r for r in refs if r]


def outgoing_edges(node):
    out = []
    for edge in node.get("edges") or []:
        tgt = edge.get("to")
        if tgt:
            out.append((tgt, edge.get("relation", "")))
    return out


def node_date(node):
    attr = (node.get("provenance") or {}).get("attribution") or {}
    return attr.get("date") or ""


# ──────────────────────────────────────────────────────────────────────────
#  Edges: derivation + declared + text-mentions
# ──────────────────────────────────────────────────────────────────────────
ID_RE = re.compile(r"\b([A-Z]{1,3}\d+)(?:-[A-Za-z0-9\-]+)?\b")


def build_short_to_full(id_set):
    """Map short id (R05) to full id (R05-sister). First-seen wins for ambiguity."""
    m = {}
    for fid in id_set:
        short = fid.split("-", 1)[0]
        m.setdefault(short, fid)
    return m


def mentions_in_text(text: str, id_set: set, short_to_full: dict):
    """Ordered unique ids mentioned in text. Either full or short form accepted."""
    if not text:
        return []
    out = []
    seen = set()
    for m in ID_RE.finditer(text):
        short = m.group(1)
        tail = text[m.start():]
        tail_match = re.match(r"[A-Z]{1,3}\d+(?:-[A-Za-z0-9]+)+", tail)
        cand = tail_match.group(0) if tail_match else short
        full = cand if cand in id_set else short_to_full.get(short)
        if full and full not in seen:
            seen.add(full)
            out.append(full)
    return out


def collect_edges(nodes):
    id_set = {n["id"] for n in nodes}
    short_to_full = build_short_to_full(id_set)
    seen = set()
    edges = []

    for n in nodes:
        nid = n["id"]
        ntype = n.get("type", "")

        # Derivation parents → this node
        for parent in derivation_sources(n):
            if parent in id_set and parent != nid and (parent, nid) not in seen:
                seen.add((parent, nid))
                kind = "emergent" if ntype == "emergent" else "grounds"
                edges.append({"from": parent, "to": nid, "kind": kind})

        # Declared outgoing edges
        for tgt, relation in outgoing_edges(n):
            if tgt in id_set and tgt != nid and (nid, tgt) not in seen:
                seen.add((nid, tgt))
                kind = "emergent" if relation == "emergent_from" else "grounds"
                edges.append({"from": nid, "to": tgt, "kind": kind})

        # Evidence references
        for ref in evidence_references(n):
            if ref in id_set and ref != nid and (nid, ref) not in seen:
                seen.add((nid, ref))
                edges.append({"from": nid, "to": ref, "kind": "grounds"})

        # Mentions in statement
        stmt = n.get("statement") or ""
        for ref in mentions_in_text(stmt, id_set, short_to_full):
            if ref != nid and (nid, ref) not in seen and (ref, nid) not in seen:
                seen.add((nid, ref))
                edges.append({"from": nid, "to": ref, "kind": "grounds"})

    return edges


# ──────────────────────────────────────────────────────────────────────────
#  Mandala placement — rings by type, angular ordering by neighbor pull
# ──────────────────────────────────────────────────────────────────────────
def compute_positions(nodes, edges):
    adj = defaultdict(set)
    for e in edges:
        adj[e["from"]].add(e["to"])
        adj[e["to"]].add(e["from"])

    ring_buckets = defaultdict(list)
    for n in nodes:
        ring = TYPE_RING.get(n.get("type", ""), 7)
        ring_buckets[ring].append(n)
    for ring in ring_buckets:
        ring_buckets[ring].sort(key=lambda nd: nd["id"])

    positions = {}  # id -> (x, y, angle, ring)
    rings_present = sorted(ring_buckets.keys())

    for ring in rings_present:
        r = RING_RADIUS[ring] if ring < len(RING_RADIUS) else 800
        bucket = ring_buckets[ring]
        count = len(bucket)
        if count == 0:
            continue

        if ring == 0:
            if count == 1:
                positions[bucket[0]["id"]] = (0.0, 0.0, 0.0, 0)
            else:
                for i, n in enumerate(bucket):
                    ang = -math.pi / 2 + 2 * math.pi * i / count
                    positions[n["id"]] = (60 * math.cos(ang), 60 * math.sin(ang), ang, 0)
            continue

        # Order nodes by the angle of their already-placed neighbors
        prefs = []
        for n in bucket:
            nid = n["id"]
            neighbor_angles = [positions[m][2] for m in adj.get(nid, ()) if m in positions]
            if neighbor_angles:
                sx = sum(math.cos(a) for a in neighbor_angles)
                sy = sum(math.sin(a) for a in neighbor_angles)
                pref = None if sx == 0 and sy == 0 else math.atan2(sy, sx)
            else:
                pref = None
            prefs.append((nid, pref, n))

        def sort_key(item):
            _, pref, _ = item
            return (pref is None, pref if pref is not None else 0.0, item[0])

        prefs.sort(key=sort_key)
        ordered = [item[2] for item in prefs]
        for i, n in enumerate(ordered):
            ang = -math.pi / 2 + 2 * math.pi * i / count
            positions[n["id"]] = (r * math.cos(ang), r * math.sin(ang), ang, ring)

    return positions


# ──────────────────────────────────────────────────────────────────────────
#  Derived metrics
# ──────────────────────────────────────────────────────────────────────────
def compute_spine(nodes, top_n=4):
    ref_count = defaultdict(int)
    by_id = {n["id"]: n for n in nodes}
    for n in nodes:
        for parent in derivation_sources(n):
            ref_count[parent] += 1
        for tgt, _ in outgoing_edges(n):
            ref_count[tgt] += 1
    obs = [
        (nid, c) for nid, c in ref_count.items()
        if nid in by_id and by_id[nid].get("type") == "observation"
    ]
    obs.sort(key=lambda kv: (-kv[1], kv[0]))
    return [{"id": nid, "count": c} for nid, c in obs[:top_n]]


def compute_risk_corridor(nodes, pivot_id=RISK_PIVOT):
    id_set = {n["id"] for n in nodes}
    if pivot_id not in id_set:
        return pivot_id, []
    children_of = defaultdict(set)
    for n in nodes:
        nid = n["id"]
        for parent in derivation_sources(n):
            children_of[parent].add(nid)
        for tgt, _ in outgoing_edges(n):
            children_of[nid].add(tgt)
    seen = set()
    q = deque([pivot_id])
    while q:
        cur = q.popleft()
        for ch in children_of.get(cur, ()):
            if ch != pivot_id and ch not in seen:
                seen.add(ch)
                q.append(ch)
    return pivot_id, sorted(seen)


def compute_related(nodes, edges):
    """For each node, the set of node ids it is related to (undirected)."""
    id_set = {n["id"] for n in nodes}
    short_to_full = build_short_to_full(id_set)
    related = {nid: set() for nid in id_set}

    for e in edges:
        if e["from"] in related and e["to"] in id_set:
            related[e["from"]].add(e["to"])
        if e["to"] in related and e["from"] in id_set:
            related[e["to"]].add(e["from"])

    for n in nodes:
        nid = n["id"]
        for ref in evidence_references(n):
            if ref in id_set and ref != nid:
                related[nid].add(ref)
                related[ref].add(nid)
        for ref in mentions_in_text(n.get("statement", "") or "", id_set, short_to_full):
            if ref != nid:
                related[nid].add(ref)
                related[ref].add(nid)

    type_order = ["now", "practice", "emergent", "overlap", "novel",
                  "observation", "equivalency", "reference", "open"]
    type_rank = {t: i for i, t in enumerate(type_order)}
    by_id = {n["id"]: n for n in nodes}
    result = {}
    for nid, rs in related.items():
        result[nid] = sorted(
            rs,
            key=lambda r: (type_rank.get(by_id.get(r, {}).get("type", ""), 99), r)
        )
    return result


# ──────────────────────────────────────────────────────────────────────────
#  Companion markdown parsing
# ──────────────────────────────────────────────────────────────────────────
def parse_vocab(path: Path):
    """Parse alex-vocab.md into [{term, def}]."""
    if not path.exists():
        return []
    entries = []
    for line in path.read_text().splitlines():
        m = re.match(r"^-\s+\*\*([^*]+?)\*\*\s*[—\-–]\s*(.+)$", line)
        if m:
            entries.append({"term": m.group(1).strip(), "def": m.group(2).strip()})
    return entries


def parse_action_cards(path: Path):
    """Parse alex-actions.md. Each `## Heading` + following lines until next
    heading becomes {title, body}."""
    if not path.exists():
        return []
    text = path.read_text()
    cards = []
    cur = None
    for raw in text.splitlines():
        line = raw.rstrip()
        h = re.match(r"^##\s+(.+)$", line)
        if h:
            if cur and cur["body"].strip():
                cards.append(cur)
            cur = {"title": h.group(1).strip(), "body": ""}
            continue
        if cur is None:
            continue
        if not line.strip():
            if cur["body"]:
                cur["body"] += "\n"
            continue
        cur["body"] += (" " if cur["body"] and not cur["body"].endswith("\n") else "") + line.strip()
    if cur and cur["body"].strip():
        cards.append(cur)
    # Trim trailing whitespace in bodies
    for c in cards:
        c["body"] = c["body"].strip()
    return cards


def parse_needs_eyes(path: Path):
    """Parse alex-needs-eyes.md into [{title, body}] entries per `##`."""
    return parse_action_cards(path)


# ──────────────────────────────────────────────────────────────────────────
#  NOW-statement section extraction (## This week / ## Canaries etc.)
# ──────────────────────────────────────────────────────────────────────────
def extract_sections(text: str):
    """Return dict: heading (lower) -> list of bullet-line strings.
    Recognizes `## Heading` and subsequent ` • ...` / ` - ...` / ` * ...` lines.
    """
    out = {}
    if not text:
        return out
    lines = text.splitlines()
    cur_name = None
    cur_buf = []
    for ln in lines + [""]:
        h = re.match(r"^\s*##\s+(.+?)\s*$", ln)
        if h:
            if cur_name is not None:
                out[cur_name.lower()] = cur_buf
            cur_name = h.group(1)
            cur_buf = []
            continue
        if cur_name is None:
            continue
        # bullet (• * -) possibly indented
        b = re.match(r"^\s*[•\*\-]\s+(.+)$", ln)
        if b:
            cur_buf.append(b.group(1).strip())
            continue
        # continuation line (indented, no bullet) — append to last bullet
        if ln.strip() and cur_buf and re.match(r"^\s{2,}\S", ln):
            cur_buf[-1] += " " + ln.strip()
    if cur_name is not None:
        out[cur_name.lower()] = cur_buf
    return out


# ──────────────────────────────────────────────────────────────────────────
#  Payload assembly
# ──────────────────────────────────────────────────────────────────────────
def build_payload(nodes):
    edges = collect_edges(nodes)
    positions = compute_positions(nodes, edges)
    related = compute_related(nodes, edges)

    out_nodes = []
    for n in nodes:
        nid = n["id"]
        pos = positions.get(nid, (0.0, 0.0, 0.0, 7))
        is_forecast = bool(n.get("inferencer")) or bool(n.get("horizon"))
        out_nodes.append({
            "id": nid,
            "type": n.get("type", ""),
            "name": (n.get("name") or "").strip(),
            "statement": (n.get("statement") or "").strip(),
            "tentative": bool(n.get("tentative", False)),
            "is_forecast": is_forecast,
            "horizon": n.get("horizon") or "",
            "caveats": (n.get("caveats") or "").strip(),
            "handling": (n.get("handling") or "").strip(),
            "derived_from": derivation_sources(n),
            "evidence_refs": evidence_references(n),
            "related": related.get(nid, []),
            "date": node_date(n),
            "x": round(pos[0], 2),
            "y": round(pos[1], 2),
            "ring": pos[3],
        })

    pivot, downstream = compute_risk_corridor(nodes)
    spine = compute_spine(nodes)

    counts = defaultdict(int)
    for n in out_nodes:
        counts[n["type"]] += 1

    now_node = next((n for n in out_nodes if n["type"] == "now"), None)
    now_date = now_node["date"] if now_node else ""
    now_sections = extract_sections(now_node["statement"]) if now_node else {}

    return {
        "nodes": out_nodes,
        "edges": edges,
        "risk_source": pivot,
        "risk_downstream": downstream,
        "spine": spine,
        "counts": dict(counts),
        "now_id": now_node["id"] if now_node else "",
        "now_date": now_date,
        "now_sections": now_sections,
        "rendered": date.today().isoformat(),
        "type_notes": TYPE_NOTE,
        "type_ring": TYPE_RING,
        "ring_radius": RING_RADIUS,
        "ring_label": {str(k): v for k, v in RING_LABEL.items()},
        "legend_order": LEGEND_ORDER,
        "lever_id": LEVER_NODE,
    }


# ──────────────────────────────────────────────────────────────────────────
#  HTML template
# ──────────────────────────────────────────────────────────────────────────
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Alex — knowledge fractal · dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+Pro:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #f4ecd9;
    --bg-panel: #f9f2dd;
    --bg-panel-2: #ebe2cc;
    --border: #d4c7a8;
    --border-soft: #dfd4b6;
    --ink: #2b2520;
    --ink-soft: #4a4438;
    --muted: #6a5f50;
    --muted-2: #9a8d76;
    --accent: #8a3420;
    --accent-soft: #e8d8c2;
    --link: #8a3420;
    --link-hover: #6a2818;
    --warn: #a06a1e;
    --warn-soft: rgba(160,106,30,0.10);

    --c-reference:  #8798ae;
    --c-observation:#4a75b5;
    --c-overlap:    #5a9a6a;
    --c-novel:      #e19b3d;
    --c-emergent:   #8b5fa8;
    --c-emergent-gold:#d5a23a;
    --c-equivalency:#d8a07a;
    --c-practice:   #c9453a;
    --c-open:       #d66a7a;
    --c-now:        #d5a23a;

    --serif: "Source Serif Pro", Georgia, ui-serif, serif;
    --sans:  "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --mono:  "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace;
  }
  /* Light-only: dashboard always uses the warm-paper site palette.
     (Removed prefers-color-scheme: dark override — matches essay tone.) */

  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; height: 100%; background: var(--bg); color: var(--ink); font-family: var(--sans); }

  /* Header */
  header.page {
    padding: 14px 24px 12px;
    border-bottom: 1px solid var(--border);
    background: var(--bg-panel);
    display: flex; align-items: baseline; gap: 18px; flex-wrap: wrap;
  }
  header.page .brand {
    font-family: var(--sans);
    font-size: 13px; font-weight: 600; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--ink);
  }
  header.page .ver {
    font-family: var(--mono); font-size: 11.5px; color: var(--muted);
    letter-spacing: 0.04em;
  }
  header.page .ver b { color: var(--ink-soft); font-weight: 500; }
  header.page .hints {
    margin-left: auto;
    font-family: var(--mono); font-size: 10.5px; color: var(--muted);
    letter-spacing: 0.04em;
  }
  header.page .hints kbd {
    font-family: var(--mono); font-size: 10px;
    border: 1px solid var(--border); border-radius: 2px;
    padding: 0 4px; background: var(--bg); color: var(--ink-soft);
    margin: 0 2px;
  }

  /* Main 3-column grid */
  main {
    display: grid;
    grid-template-columns: 240px minmax(0, 1fr) 360px;
    gap: 0;
    min-height: calc(100vh - 54px);
  }
  @media (max-width: 1100px) {
    main { grid-template-columns: 210px minmax(0, 1fr) 320px; }
  }
  @media (max-width: 920px) {
    main { grid-template-columns: 1fr; }
  }

  /* Left sidebar */
  aside.leftbar {
    border-right: 1px solid var(--border);
    background: var(--bg-panel);
    padding: 18px 14px 28px;
    overflow-y: auto;
    max-height: calc(100vh - 54px);
  }
  aside.leftbar h3 {
    font-family: var(--sans); font-size: 10px; font-weight: 600;
    color: var(--accent); letter-spacing: 0.18em; text-transform: uppercase;
    margin: 18px 0 8px; padding-bottom: 4px;
    border-bottom: 1px solid var(--border-soft);
  }
  aside.leftbar h3:first-child { margin-top: 0; }

  #search {
    width: 100%; padding: 7px 10px;
    border: 1px solid var(--border);
    background: var(--bg); color: var(--ink);
    border-radius: 3px; font-family: var(--sans); font-size: 12.5px;
    outline: none;
  }
  #search:focus { border-color: var(--accent); }
  #search::placeholder { color: var(--muted-2); }

  .legend-row {
    display: flex; align-items: center; gap: 8px;
    padding: 4px 6px; font-size: 12px; cursor: pointer;
    border-radius: 3px; color: var(--ink-soft);
    transition: background 0.1s;
  }
  .legend-row:hover { background: rgba(138, 131, 118, 0.08); }
  .legend-row.dim { opacity: 0.3; }
  .swatch {
    width: 10px; height: 10px; border-radius: 50%;
    flex-shrink: 0; border: 1px solid rgba(0,0,0,0.18);
  }
  .swatch.now          { background: var(--c-now); }
  .swatch.practice     { background: var(--c-practice); }
  .swatch.emergent     { background: var(--c-emergent); }
  .swatch.overlap      { background: var(--c-overlap); }
  .swatch.novel        { background: var(--c-novel); }
  .swatch.observation  { background: var(--c-observation); }
  .swatch.equivalency  { background: var(--c-equivalency); }
  .swatch.reference    { background: var(--c-reference); }
  .swatch.open         { background: var(--c-open); }
  .swatch.forecast     { background: var(--c-emergent-gold); border: 1px solid #e8b958; }
  .legend-count {
    margin-left: auto; font-family: var(--mono);
    font-size: 10.5px; color: var(--muted); font-variant-numeric: tabular-nums;
  }

  #type-counts {
    font-family: var(--mono); font-size: 10px; line-height: 1.55;
    color: var(--muted); padding: 4px 2px;
  }
  #type-counts b { color: var(--ink-soft); font-weight: 500; }

  #toggle-layout {
    width: 100%; padding: 7px 8px;
    background: var(--bg); color: var(--ink-soft);
    border: 1px solid var(--border); border-radius: 3px;
    font-family: var(--mono); font-size: 10.5px; letter-spacing: 0.05em;
    cursor: pointer;
  }
  #toggle-layout:hover { border-color: var(--accent); color: var(--accent); }

  .vocab-list {
    font-size: 11.5px; color: var(--ink-soft); line-height: 1.55;
    max-height: 260px; overflow-y: auto; padding-right: 4px;
  }
  .vocab-list .v-term {
    font-family: var(--mono); font-size: 10.5px;
    color: var(--ink); font-weight: 600;
  }
  .vocab-list .v-item { padding: 4px 0; border-bottom: 1px dotted var(--border-soft); }
  .vocab-list .v-item:last-child { border-bottom: none; }
  .vocab-list .v-def { display: block; margin-top: 2px; color: var(--muted); }

  details.collapsible summary {
    cursor: pointer; color: var(--accent);
    font-family: var(--sans); font-size: 10px; font-weight: 600;
    letter-spacing: 0.18em; text-transform: uppercase;
    margin: 18px 0 8px; padding-bottom: 4px;
    border-bottom: 1px solid var(--border-soft);
    list-style: none;
  }
  details.collapsible summary::-webkit-details-marker { display: none; }
  details.collapsible summary::before { content: "▸ "; font-size: 9px; color: var(--muted); }
  details[open].collapsible summary::before { content: "▾ "; }

  /* Stage (mandala) */
  section.stage {
    position: relative;
    overflow: hidden;
    background: var(--bg);
    min-height: calc(100vh - 54px);
  }
  svg#mandala {
    width: 100%; height: 100%; display: block;
    font-family: var(--sans);
    user-select: none; cursor: grab;
    touch-action: none;
  }
  svg#mandala.panning { cursor: grabbing; }
  svg#mandala .ring-bg {
    fill: none; stroke: var(--border-soft);
    stroke-width: 1; stroke-dasharray: 2 4;
  }
  svg#mandala .ring-label {
    font-family: var(--sans); font-size: 9.5px;
    fill: var(--muted-2); letter-spacing: 0.18em; text-transform: uppercase;
  }
  svg#mandala .edge {
    fill: none; stroke: var(--muted-2); stroke-width: 0.9;
    opacity: 0.25;
    transition: opacity 0.15s, stroke 0.15s, stroke-width 0.15s;
    pointer-events: none;
  }
  svg#mandala .edge.emergent { stroke-dasharray: 4 3; }
  svg#mandala.has-selection .edge { opacity: 0.06; }
  svg#mandala.has-selection .edge.active {
    opacity: 0.95; stroke: var(--accent); stroke-width: 1.6;
  }
  svg#mandala .node circle {
    stroke: var(--bg); stroke-width: 2; cursor: pointer;
    transition: stroke 0.14s, stroke-width 0.14s;
  }
  svg#mandala .node:hover circle,
  svg#mandala .node.active circle {
    stroke: var(--ink); stroke-width: 2.5;
  }
  svg#mandala .node.active circle {
    filter: drop-shadow(0 0 6px rgba(138, 90, 42, 0.45));
  }
  svg#mandala.has-selection .node { opacity: 0.22; }
  svg#mandala.has-selection .node.active,
  svg#mandala.has-selection .node.neighbor { opacity: 1; }
  svg#mandala .node text.nid {
    font-family: var(--mono); font-size: 9.5px;
    fill: var(--muted); pointer-events: none;
    text-anchor: middle; dominant-baseline: middle;
  }
  svg#mandala .node:hover text.nid,
  svg#mandala .node.active text.nid { fill: var(--ink); font-weight: 600; }
  svg#mandala .node.search-miss { opacity: 0.15; }

  .zoom-controls {
    position: absolute; right: 18px; bottom: 18px;
    display: flex; flex-direction: column; gap: 4px;
    background: var(--bg-panel); border: 1px solid var(--border);
    border-radius: 4px; padding: 4px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    z-index: 15;
  }
  .zoom-controls button {
    width: 28px; height: 26px; background: none; border: none;
    color: var(--ink-soft); font-family: var(--sans); font-size: 16px; font-weight: 500;
    cursor: pointer; border-radius: 2px; line-height: 1; padding: 0;
  }
  .zoom-controls button:hover { background: var(--accent-soft); color: var(--accent); }
  .zoom-controls button.reset { font-size: 10.5px; letter-spacing: 0.08em; text-transform: uppercase; }

  .tooltip {
    position: fixed; pointer-events: none;
    background: var(--bg-panel); border: 1px solid var(--border);
    border-radius: 4px; padding: 9px 11px;
    font-family: var(--sans); font-size: 12px; line-height: 1.5;
    color: var(--ink); max-width: 320px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.12);
    opacity: 0; transition: opacity 0.12s; z-index: 50;
  }
  .tooltip.visible { opacity: 1; }
  .tooltip .tt-id {
    font-family: var(--mono); font-size: 10.5px; color: var(--muted);
    letter-spacing: 0.08em; margin-bottom: 3px;
  }
  .tooltip .tt-name { font-weight: 600; color: var(--ink); margin-bottom: 4px; }
  .tooltip .tt-summary { color: var(--ink-soft); font-size: 11.5px; }

  /* Right sidebar */
  aside.rightbar {
    border-left: 1px solid var(--border);
    background: var(--bg-panel);
    padding: 24px 22px 56px;
    overflow-y: auto;
    max-height: calc(100vh - 54px);
  }
  aside.rightbar h2 {
    font-family: var(--sans); font-size: 11px; font-weight: 600;
    color: var(--warn); letter-spacing: 0.18em; text-transform: uppercase;
    margin: 22px 0 10px; padding-bottom: 6px;
    border-bottom: 1px solid var(--border-soft);
  }
  aside.rightbar h2:first-of-type { margin-top: 0; }

  .tb-today-line {
    font-family: var(--serif); font-size: 26px; font-weight: 600;
    color: var(--ink); line-height: 1.2; margin: 0 0 4px;
  }
  .tb-today-line em {
    font-family: var(--serif); font-style: italic; font-weight: 400;
    color: var(--muted); font-size: 16px;
  }
  .tb-subcaps {
    font-family: var(--mono); font-size: 10px; color: var(--muted);
    letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 14px;
  }
  .tb-pill {
    display: inline-block; padding: 3px 10px;
    background: var(--warn-soft); border: 1px solid rgba(160,106,30,0.25);
    color: var(--warn); font-family: var(--mono); font-size: 10.5px;
    letter-spacing: 0.14em; border-radius: 3px; margin-bottom: 12px;
  }

  .goals-frame {
    padding: 14px 16px;
    background: var(--warn-soft);
    border-left: 3px solid var(--warn);
    border-radius: 2px;
    font-family: var(--sans); font-size: 13.5px; line-height: 1.65;
    color: var(--ink-soft); margin-bottom: 4px;
  }
  .goals-frame .g-line { margin: 3px 0; }
  .goals-frame strong { color: var(--ink); }
  .goals-frame .g-lever {
    font-size: 11.5px; color: var(--muted); margin-top: 10px;
  }

  .bullets { margin: 0; padding-left: 1.1em; list-style: none; }
  .bullets li {
    margin: 9px 0; padding-left: 0.9em; position: relative;
    color: var(--ink-soft); font-size: 14px; line-height: 1.6;
  }
  .bullets li::before {
    content: "·"; color: var(--warn); position: absolute; left: 0;
    font-weight: 700;
  }

  .thread-card {
    background: var(--bg-panel-2);
    border: 1px solid var(--border-soft);
    border-left: 2px solid var(--link);
    border-radius: 3px;
    padding: 10px 12px; margin: 8px 0;
  }
  .thread-card .tc-title {
    font-size: 13.5px; color: var(--ink); font-weight: 600; margin-bottom: 3px;
  }
  .thread-card .tc-body {
    font-size: 12.5px; color: var(--ink-soft); line-height: 1.55;
  }

  .eyes-card {
    border-left: 2px solid var(--border);
    padding: 6px 12px; margin: 6px 0;
  }
  .eyes-card:hover { border-left-color: var(--warn); }
  .eyes-card .ec-title {
    font-size: 12.5px; color: var(--ink); font-weight: 500;
  }
  .eyes-card .ec-body {
    font-size: 12px; color: var(--ink-soft); line-height: 1.55; margin-top: 3px;
  }

  .ref-chip {
    font-family: var(--mono); font-size: 11px;
    color: var(--link); cursor: pointer;
    padding: 0 2px; border-radius: 2px;
  }
  .ref-chip:hover {
    color: var(--link-hover); text-decoration: underline;
    background: rgba(46,74,138,0.08);
  }

  /* Node detail view */
  .nd-top { display: flex; gap: 8px; align-items: center; margin-bottom: 10px; flex-wrap: wrap; }
  .nd-btn {
    padding: 4px 10px; font-family: var(--mono); font-size: 10.5px;
    letter-spacing: 0.1em; text-transform: uppercase;
    border: 1px solid var(--border); background: var(--bg);
    color: var(--ink-soft); border-radius: 3px; cursor: pointer;
  }
  .nd-btn:hover { border-color: var(--warn); color: var(--warn); }
  .nd-btn.primary {
    background: var(--warn-soft); border-color: rgba(160,106,30,0.25); color: var(--warn);
  }
  .nd-type {
    display: inline-block; padding: 2px 8px; font-family: var(--mono);
    font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase;
    border-radius: 2px; color: #fff;
  }
  .nd-type.now         { background: var(--c-now); color: #5a4018; }
  .nd-type.practice    { background: var(--c-practice); }
  .nd-type.emergent    { background: var(--c-emergent); }
  .nd-type.overlap     { background: var(--c-overlap); }
  .nd-type.novel       { background: var(--c-novel); color: #4a2f10; }
  .nd-type.observation { background: var(--c-observation); }
  .nd-type.equivalency { background: var(--c-equivalency); color: #4a2f18; }
  .nd-type.reference   { background: var(--c-reference); color: #1e2638; }
  .nd-type.open        { background: var(--c-open); color: #4a1e24; }
  .nd-tent {
    display: inline-block; padding: 2px 8px; font-family: var(--mono);
    font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase;
    border-radius: 2px; border: 1px solid var(--warn); color: var(--warn);
    background: var(--warn-soft);
  }
  .nd-title {
    font-family: var(--serif); font-size: 22px; line-height: 1.25;
    color: var(--ink); font-weight: 600; margin: 4px 0 3px;
  }
  .nd-id {
    font-family: var(--mono); font-size: 11px; color: var(--muted);
    letter-spacing: 0.08em; margin-bottom: 12px;
  }
  .nd-caveats {
    padding: 10px 12px; background: var(--bg-panel-2);
    border-left: 3px solid var(--muted-2); border-radius: 2px;
    font-size: 12.5px; color: var(--ink-soft); line-height: 1.55;
    margin: 12px 0;
  }
  .nd-handling {
    padding: 10px 12px; background: var(--warn-soft);
    border-left: 3px solid var(--warn); border-radius: 2px;
    font-size: 12.5px; color: var(--ink-soft); line-height: 1.55;
    margin: 12px 0;
  }
  .nd-handling .hlabel {
    font-family: var(--mono); font-size: 9.5px; color: var(--warn);
    letter-spacing: 0.16em; text-transform: uppercase; margin-bottom: 4px;
  }
  .nd-explain {
    padding: 12px 14px; background: rgba(46,74,138,0.06);
    border-left: 3px solid var(--link); border-radius: 2px;
    font-size: 12.5px; color: var(--ink-soft); line-height: 1.55;
    margin: 14px 0 6px;
  }
  .nd-explain strong { color: var(--ink); }
  .nd-statement {
    font-family: var(--serif); font-size: 14.5px; line-height: 1.7;
    color: var(--ink); margin: 10px 0;
  }
  .nd-statement p { margin: 0 0 12px; }
  .nd-statement h3, .nd-statement h4 {
    font-family: var(--sans); font-size: 10.5px; color: var(--warn);
    letter-spacing: 0.14em; text-transform: uppercase; font-weight: 600;
    margin: 18px 0 8px; padding-bottom: 4px;
    border-bottom: 1px solid var(--border-soft);
  }
  .nd-statement ul { padding-left: 1.1em; list-style: none; margin: 6px 0 14px; }
  .nd-statement li { margin: 6px 0; padding-left: 0.8em; position: relative; color: var(--ink-soft); }
  .nd-statement li::before { content: "·"; color: var(--warn); position: absolute; left: 0; font-weight: 700; }
  .nd-statement strong { color: var(--ink); font-weight: 600; }
  .nd-statement em { color: var(--warn); font-style: italic; }
  .nd-statement code {
    font-family: var(--mono); font-size: 12.5px;
    background: var(--bg-panel-2); color: var(--accent);
    padding: 1px 5px; border-radius: 2px;
  }
  .nd-sub-h { /* RELATED SUBGRAPH heading */
    font-family: var(--sans); font-size: 10px; font-weight: 600;
    color: var(--warn); letter-spacing: 0.18em; text-transform: uppercase;
    margin: 18px 0 8px; padding-bottom: 4px;
    border-bottom: 1px solid var(--border-soft);
  }
  .nd-sub-h2 {
    font-family: var(--mono); font-size: 10px; color: var(--muted);
    letter-spacing: 0.12em; text-transform: uppercase; margin: 12px 0 6px;
  }
  .rel-card {
    padding: 8px 10px; margin: 5px 0;
    background: var(--bg-panel-2); border: 1px solid var(--border-soft);
    border-radius: 3px; cursor: pointer;
    transition: border-color 0.12s, background 0.12s;
  }
  .rel-card:hover { border-color: var(--warn); background: var(--bg); }
  .rel-card .rc-head {
    display: flex; gap: 8px; align-items: baseline; margin-bottom: 2px; flex-wrap: wrap;
  }
  .rel-card .rc-id {
    font-family: var(--mono); font-size: 11px; color: var(--link); font-weight: 500;
  }
  .rel-card .rc-type {
    font-family: var(--mono); font-size: 9.5px; color: var(--muted);
    letter-spacing: 0.1em; text-transform: uppercase;
    padding: 1px 5px; border-radius: 2px; background: var(--bg);
    border: 1px solid var(--border-soft);
  }
  .rel-card .rc-name { font-size: 12.5px; color: var(--ink); font-weight: 500; }
  .rel-card .rc-summary {
    font-size: 11.5px; color: var(--muted); line-height: 1.5; margin-top: 3px;
  }
  .vocab-footer {
    margin-top: 28px; font-family: var(--mono); font-size: 10px; color: var(--muted);
    letter-spacing: 0.1em;
  }
  .vocab-footer a { color: var(--link); cursor: pointer; }
</style>
</head>
<body>

<header class="page">
  <span class="brand">ALEX — KNOWLEDGE FRACTAL</span>
  <span class="ver">example-graph · <b>__NODE_COUNT__ nodes</b> · <b>__EDGE_COUNT__ edges</b> · mandala (concentric rings)</span>
  <span class="hints">hover · click · <kbd>scroll</kbd> zoom · <kbd>drag</kbd> pan · <kbd>esc</kbd> deselect · <kbd>/</kbd> search</span>
</header>

<main>
  <aside class="leftbar">
    <h3>Search</h3>
    <input id="search" placeholder="search id, name, text…" />

    <h3>Legend</h3>
    <div id="legend"></div>
    <div class="legend-row" style="cursor:default;">
      <span class="swatch forecast"></span>
      <span>Forecast (gold, E-ring)</span>
    </div>

    <h3>Layout</h3>
    <button id="toggle-layout">toggle → force-directed</button>

    <h3>Type counts</h3>
    <div id="type-counts"></div>

    <details class="collapsible" id="vocab-panel" open>
      <summary>Vocab</summary>
      <div class="vocab-list" id="vocab-list"></div>
    </details>
  </aside>

  <section class="stage">
    <svg id="mandala"></svg>
    <div class="tooltip" id="tooltip"></div>
    <div class="zoom-controls">
      <button id="zoom-in"  title="zoom in (+)">+</button>
      <button id="zoom-out" title="zoom out (−)">−</button>
      <button id="zoom-fit" class="reset" title="fit (0)">fit</button>
    </div>
  </section>

  <aside class="rightbar" id="rightbar"><!-- populated by JS --></aside>
</main>

<script id="graph-data" type="application/json">__DATA_JSON__</script>
<script id="vocab-data" type="application/json">__VOCAB_JSON__</script>
<script id="actions-data" type="application/json">__ACTIONS_JSON__</script>
<script id="eyes-data" type="application/json">__EYES_JSON__</script>

<script>
(function () {
  "use strict";

  // ---- Data ----
  const DATA    = JSON.parse(document.getElementById("graph-data").textContent);
  const VOCAB   = JSON.parse(document.getElementById("vocab-data").textContent);
  const ACTIONS = JSON.parse(document.getElementById("actions-data").textContent);
  const EYES    = JSON.parse(document.getElementById("eyes-data").textContent);

  const nodes = DATA.nodes;
  const edges = DATA.edges;
  const byId  = new Map(nodes.map(n => [n.id, n]));
  const idSet = new Set(byId.keys());

  // Short-form -> full-form lookup
  const shortToFull = {};
  for (const id of idSet) {
    const short = id.split("-")[0];
    if (!(short in shortToFull)) shortToFull[short] = id;
  }
  function resolveId(token) {
    if (!token) return null;
    if (idSet.has(token)) return token;
    const short = token.split("-")[0];
    if (shortToFull[token]) return shortToFull[token];
    if (shortToFull[short]) return shortToFull[short];
    return null;
  }

  // ---- DOM refs ----
  const svg       = document.getElementById("mandala");
  const tooltip   = document.getElementById("tooltip");
  const searchEl  = document.getElementById("search");
  const rightbar  = document.getElementById("rightbar");
  const btnLayout = document.getElementById("toggle-layout");
  const legendEl  = document.getElementById("legend");
  const countsEl  = document.getElementById("type-counts");
  const vocabEl   = document.getElementById("vocab-list");

  // ---- Colors / utility ----
  const COLOR = {
    now: "#d5a23a", practice: "#c9453a", emergent: "#8b5fa8",
    overlap: "#5a9a6a", novel: "#e19b3d", observation: "#4a75b5",
    equivalency: "#d8a07a", reference: "#8798ae", open: "#d66a7a",
  };
  const FORECAST_COLOR = "#d5a23a";

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  }

  function summaryOf(n) {
    if (!n || !n.statement) return "";
    const first = n.statement.split(/\n\s*\n/)[0].replace(/\s+/g, " ").trim();
    return first.length > 160 ? first.slice(0, 160) + "…" : first;
  }

  // Inline format for small text: linkify node IDs, **bold**, `code`.
  function inlineFormat(s) {
    if (!s) return "";
    let t = escapeHtml(s);
    t = t.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    t = t.replace(/`([^`]+)`/g, "<code>$1</code>");
    t = t.replace(/\b([A-Z]{1,3}\d+(?:-[a-z0-9\-]+)?)\b/g, (m) => {
      const full = resolveId(m);
      if (!full) return m;
      return '<span class="ref-chip" data-goto="' + full + '">' + m + '</span>';
    });
    return t;
  }

  // Render a subset of markdown (used for node statements).
  function renderStatement(text) {
    if (!text) return "";
    const lines = text.split(/\r?\n/);
    const out = [];
    let inList = false, para = [];
    const flushPara = () => {
      if (para.length) { out.push("<p>" + inlineFormat(para.join(" ")) + "</p>"); para = []; }
    };
    const closeList = () => { if (inList) { out.push("</ul>"); inList = false; } };

    for (const raw of lines) {
      const line = raw.replace(/\s+$/, "");
      if (!line.trim()) { flushPara(); closeList(); continue; }

      const h = line.match(/^#{1,4}\s+(.+)$/);
      if (h) { flushPara(); closeList(); out.push("<h3>" + escapeHtml(h[1]) + "</h3>"); continue; }

      const b = line.match(/^\s*[•\*\-]\s+(.+)$/);
      if (b) {
        flushPara();
        if (!inList) { out.push("<ul>"); inList = true; }
        out.push("<li>" + inlineFormat(b[1]) + "</li>");
        continue;
      }
      // continuation of current bullet
      if (inList && /^\s{2,}\S/.test(raw)) {
        const idx = out.length - 1;
        if (out[idx].startsWith("<li>")) {
          out[idx] = out[idx].replace(/<\/li>$/, " " + inlineFormat(line.trim()) + "</li>");
          continue;
        }
      }

      closeList();
      para.push(line.trim());
    }
    flushPara(); closeList();
    return out.join("\n");
  }

  function wireGotoLinks(container) {
    container.querySelectorAll("[data-goto]").forEach(el => {
      el.addEventListener("click", e => {
        e.stopPropagation();
        const id = el.getAttribute("data-goto");
        if (id) selectNode(id);
      });
    });
  }

  // ─────────────────────────────────────────────────────────────────────
  //  Mandala SVG
  // ─────────────────────────────────────────────────────────────────────
  const VIEW_SIZE = 1800;  // logical viewBox dimension
  const SVG_NS = "http://www.w3.org/2000/svg";

  function nodeColor(n) {
    if (n.is_forecast && n.type === "emergent") return FORECAST_COLOR;
    return COLOR[n.type] || "#888";
  }
  function nodeRadius(n) {
    if (n.id === DATA.now_id) return 22;
    if (n.is_forecast) return 14;
    if (n.type === "practice") return 12;
    return 11;
  }

  // Build all SVG once
  svg.setAttribute("viewBox", `${-VIEW_SIZE/2} ${-VIEW_SIZE/2} ${VIEW_SIZE} ${VIEW_SIZE}`);
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");

  // Layer groups
  const gRings   = document.createElementNS(SVG_NS, "g");
  const gEdges   = document.createElementNS(SVG_NS, "g");
  const gNodes   = document.createElementNS(SVG_NS, "g");
  svg.appendChild(gRings);
  svg.appendChild(gEdges);
  svg.appendChild(gNodes);

  // Ring backgrounds
  for (let i = 1; i < DATA.ring_radius.length; i++) {
    const r = DATA.ring_radius[i];
    const c = document.createElementNS(SVG_NS, "circle");
    c.setAttribute("class", "ring-bg");
    c.setAttribute("cx", 0); c.setAttribute("cy", 0); c.setAttribute("r", r);
    gRings.appendChild(c);
    const lbl = document.createElementNS(SVG_NS, "text");
    lbl.setAttribute("class", "ring-label");
    lbl.setAttribute("x", 0); lbl.setAttribute("y", -r - 6);
    lbl.setAttribute("text-anchor", "middle");
    lbl.textContent = DATA.ring_label[String(i)] || "";
    gRings.appendChild(lbl);
  }

  // Edges
  const edgeEls = [];
  const edgesByNode = new Map();  // id -> [edge indexes]
  edges.forEach((e, i) => {
    const a = byId.get(e.from), b = byId.get(e.to);
    if (!a || !b) return;
    const ln = document.createElementNS(SVG_NS, "line");
    ln.setAttribute("class", "edge" + (e.kind === "emergent" ? " emergent" : ""));
    ln.setAttribute("x1", a.x); ln.setAttribute("y1", a.y);
    ln.setAttribute("x2", b.x); ln.setAttribute("y2", b.y);
    ln.dataset.idx = i;
    gEdges.appendChild(ln);
    edgeEls.push(ln);
    if (!edgesByNode.has(e.from)) edgesByNode.set(e.from, []);
    if (!edgesByNode.has(e.to)) edgesByNode.set(e.to, []);
    edgesByNode.get(e.from).push(i);
    edgesByNode.get(e.to).push(i);
  });

  // Nodes
  const nodeEls = new Map();  // id -> {group, circle, text}
  nodes.forEach(n => {
    const g = document.createElementNS(SVG_NS, "g");
    g.setAttribute("class", "node");
    g.setAttribute("transform", `translate(${n.x},${n.y})`);
    g.dataset.id = n.id;

    const c = document.createElementNS(SVG_NS, "circle");
    c.setAttribute("r", nodeRadius(n));
    c.setAttribute("fill", nodeColor(n));
    if (n.tentative) {
      c.setAttribute("stroke", "#e19b3d");
      c.setAttribute("stroke-dasharray", "2 2");
      c.setAttribute("stroke-width", 2);
    }
    g.appendChild(c);

    // label (outside the node)
    const t = document.createElementNS(SVG_NS, "text");
    t.setAttribute("class", "nid");
    const r = nodeRadius(n);
    const ang = Math.atan2(n.y, n.x);
    const labelR = r + 10;
    const lx = Math.cos(ang) * labelR;
    const ly = Math.sin(ang) * labelR;
    t.setAttribute("x", lx);
    t.setAttribute("y", ly);
    if (n.id === DATA.now_id) {
      t.textContent = "▶ NOW";
    } else {
      const parts = n.id.split("-");
      t.textContent = parts.length > 1 ? parts.slice(1).join("-") : n.id;
    }
    g.appendChild(t);

    gNodes.appendChild(g);
    nodeEls.set(n.id, { group: g, circle: c, text: t });

    g.addEventListener("mouseenter", e => showTooltip(n, e));
    g.addEventListener("mousemove", e => moveTooltip(e));
    g.addEventListener("mouseleave", () => hideTooltip());
    g.addEventListener("click", e => { e.stopPropagation(); selectNode(n.id); });
  });

  // Click on empty SVG → deselect
  svg.addEventListener("click", e => {
    if (e.target === svg || e.target.classList.contains("ring-bg") || e.target.classList.contains("ring-label")) {
      deselectNode();
    }
  });

  // ─────────────────────────────────────────────────────────────────────
  //  Zoom / pan
  // ─────────────────────────────────────────────────────────────────────
  let view = { cx: 0, cy: 0, w: VIEW_SIZE, h: VIEW_SIZE };
  const MIN_SCALE = 0.5, MAX_SCALE = 4;
  function applyView() {
    svg.setAttribute("viewBox", `${view.cx - view.w/2} ${view.cy - view.h/2} ${view.w} ${view.h}`);
  }
  function currentScale() { return VIEW_SIZE / view.w; }
  function zoomAt(factor, clientX, clientY) {
    const rect = svg.getBoundingClientRect();
    const nx = clientX == null ? rect.width/2 : clientX - rect.left;
    const ny = clientY == null ? rect.height/2 : clientY - rect.top;
    // world coords of cursor
    const wx = view.cx - view.w/2 + (nx / rect.width) * view.w;
    const wy = view.cy - view.h/2 + (ny / rect.height) * view.h;
    const newScale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, currentScale() * factor));
    const newW = VIEW_SIZE / newScale, newH = VIEW_SIZE / newScale;
    // keep world point under cursor fixed
    view.cx = wx - (nx / rect.width - 0.5) * newW;
    view.cy = wy - (ny / rect.height - 0.5) * newH;
    view.w = newW; view.h = newH;
    applyView();
  }
  function resetView() {
    view = { cx: 0, cy: 0, w: VIEW_SIZE, h: VIEW_SIZE };
    applyView();
  }
  applyView();

  svg.addEventListener("wheel", e => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.12 : 1 / 1.12;
    zoomAt(factor, e.clientX, e.clientY);
  }, { passive: false });

  let panning = false, panStart = null;
  svg.addEventListener("mousedown", e => {
    if (e.target !== svg && !e.target.classList.contains("ring-bg") && !e.target.classList.contains("ring-label")) return;
    panning = true;
    panStart = { x: e.clientX, y: e.clientY, cx: view.cx, cy: view.cy };
    svg.classList.add("panning");
  });
  window.addEventListener("mousemove", e => {
    if (!panning) return;
    const rect = svg.getBoundingClientRect();
    const dx = (e.clientX - panStart.x) / rect.width * view.w;
    const dy = (e.clientY - panStart.y) / rect.height * view.h;
    view.cx = panStart.cx - dx;
    view.cy = panStart.cy - dy;
    applyView();
  });
  window.addEventListener("mouseup", () => {
    if (panning) { panning = false; svg.classList.remove("panning"); }
  });
  svg.addEventListener("dblclick", () => resetView());

  document.getElementById("zoom-in").addEventListener("click", () => zoomAt(1.2));
  document.getElementById("zoom-out").addEventListener("click", () => zoomAt(1/1.2));
  document.getElementById("zoom-fit").addEventListener("click", () => resetView());

  // ─────────────────────────────────────────────────────────────────────
  //  Tooltip
  // ─────────────────────────────────────────────────────────────────────
  function showTooltip(n, e) {
    tooltip.innerHTML =
      '<div class="tt-id">' + escapeHtml(n.id) + (n.tentative ? " · tentative" : "") + (n.is_forecast ? " · forecast" : "") + '</div>' +
      '<div class="tt-name">' + escapeHtml(n.name) + '</div>' +
      '<div class="tt-summary">' + escapeHtml(summaryOf(n)) + '</div>';
    tooltip.classList.add("visible");
    moveTooltip(e);
  }
  function moveTooltip(e) {
    const pad = 14;
    let x = e.clientX + pad, y = e.clientY + pad;
    const rect = tooltip.getBoundingClientRect();
    if (x + rect.width > window.innerWidth - 10) x = e.clientX - rect.width - pad;
    if (y + rect.height > window.innerHeight - 10) y = e.clientY - rect.height - pad;
    tooltip.style.left = x + "px";
    tooltip.style.top  = y + "px";
  }
  function hideTooltip() { tooltip.classList.remove("visible"); }

  // ─────────────────────────────────────────────────────────────────────
  //  Selection / highlighting
  // ─────────────────────────────────────────────────────────────────────
  let selected = null;
  const history = [];

  function neighborsOf(id) {
    const s = new Set([id]);
    (edgesByNode.get(id) || []).forEach(i => {
      const e = edges[i];
      s.add(e.from); s.add(e.to);
    });
    return s;
  }

  function clearHighlight() {
    svg.classList.remove("has-selection");
    nodeEls.forEach(o => {
      o.group.classList.remove("active");
      o.group.classList.remove("neighbor");
    });
    edgeEls.forEach(ln => ln.classList.remove("active"));
  }

  function highlightSubgraph(id) {
    const neighbors = neighborsOf(id);
    svg.classList.add("has-selection");
    nodeEls.forEach((o, nid) => {
      o.group.classList.toggle("active", nid === id);
      o.group.classList.toggle("neighbor", neighbors.has(nid) && nid !== id);
    });
    edgeEls.forEach((ln, i) => {
      const e = edges[i];
      ln.classList.toggle("active", e.from === id || e.to === id);
    });
  }

  function selectNode(id, opts) {
    opts = opts || {};
    const full = resolveId(id);
    if (!full) return;
    if (!opts.noPush && selected && selected !== full) history.push(selected);
    selected = full;
    highlightSubgraph(full);
    renderNodeDetail(full);
  }

  function deselectNode() {
    selected = null;
    history.length = 0;
    clearHighlight();
    renderToday();
  }

  function goBack() {
    if (!history.length) return;
    const id = history.pop();
    selectNode(id, { noPush: true });
  }

  // ─────────────────────────────────────────────────────────────────────
  //  Right-rail: Today (default)
  // ─────────────────────────────────────────────────────────────────────
  function prettyDate(iso) {
    if (!iso) return null;
    const m = iso.match(/^(\d{4})-(\d{1,2})(?:-(\d{1,2}))?/);
    if (!m) return { weekday: "", pretty: iso, iso };
    const d = new Date(
      parseInt(m[1], 10),
      parseInt(m[2], 10) - 1,
      m[3] ? parseInt(m[3], 10) : 1
    );
    const weekday = d.toLocaleDateString("en-US", { weekday: "long" });
    const pretty  = d.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });
    return { weekday, pretty, iso };
  }

  function renderToday() {
    const src = DATA.now_date || DATA.rendered;
    const p = prettyDate(src) || { weekday: "Today", pretty: src, iso: src };

    const now = byId.get(DATA.now_id);
    const sections = (DATA.now_sections || {});
    const thisWeek = sections["this week"] || [];
    const standing = sections["standing rules"] || [];
    const canaries = (sections["canaries — watch for"] || sections["canaries"] || []);

    const lever = byId.get(DATA.lever_id);
    const leverChip = lever
      ? `<span class="ref-chip" data-goto="${lever.id}">${escapeHtml(lever.id.split("-")[0])} →</span>`
      : `<span class="ref-chip" data-goto="${escapeHtml(DATA.lever_id)}">${escapeHtml(DATA.lever_id.split("-")[0])} →</span>`;
    const nowChip = now
      ? `<span class="ref-chip" data-goto="${now.id}">${escapeHtml(now.id)} →</span>`
      : '';

    const weekHtml = thisWeek.length
      ? '<ul class="bullets">' + thisWeek.map(b => '<li>' + inlineFormat(b) + '</li>').join('') + '</ul>'
      : '<p style="color:var(--muted);font-style:italic;">No `## This week` section in NOW node.</p>';

    const threadsHtml = ACTIONS.length
      ? ACTIONS.map(t =>
          '<div class="thread-card">' +
            '<div class="tc-title">' + escapeHtml(t.title) + '</div>' +
            '<div class="tc-body">' + inlineFormat(t.body) + '</div>' +
          '</div>'
        ).join('')
      : '<p style="color:var(--muted);font-style:italic;">No open threads file.</p>';

    const eyesHtml = EYES.length
      ? EYES.map(e =>
          '<div class="eyes-card">' +
            '<div class="ec-title">' + escapeHtml(e.title) + '</div>' +
            '<div class="ec-body">' + inlineFormat(e.body) + '</div>' +
          '</div>'
        ).join('')
      : '<p style="color:var(--muted);font-style:italic;">No needs-eyes file.</p>';

    const canariesHtml = canaries.length
      ? '<ul class="bullets">' + canaries.map(b => '<li>' + inlineFormat(b) + '</li>').join('') + '</ul>'
      : '<p style="color:var(--muted);font-style:italic;">No canaries declared in NOW.</p>';

    const standingHtml = standing.length
      ? '<ul class="bullets">' + standing.map(b => '<li>' + inlineFormat(b) + '</li>').join('') + '</ul>'
      : '';

    rightbar.innerHTML = `
      <div class="tb-today-line">Today <em>· ${escapeHtml(p.weekday)}, ${escapeHtml(p.pretty)}</em></div>
      <div class="tb-subcaps">DASHBOARD · TWO GOALS: KNOW THYSELF, CUT THE FOREST</div>
      <div class="tb-pill">▸ TODAY</div>

      <h2>Two goals</h2>
      <div class="goals-frame">
        <div class="g-line">1. <strong>Know thyself</strong> — the graph, this dashboard, the reading. Inward.</div>
        <div class="g-line">2. <strong>Cut the forest</strong> — ship, break ground, move. Outward.</div>
        <div class="g-lever">Single lever where they meet: ${leverChip} &middot; frame: ${nowChip}</div>
      </div>

      <h2>Cut the forest today</h2>
      ${weekHtml}

      <h2>Open threads — live work</h2>
      ${threadsHtml}

      <h2>Needs eyes</h2>
      ${eyesHtml}

      <h2>Canaries — watch for</h2>
      ${canariesHtml}

      ${ standingHtml ? '<h2>Standing rules</h2>' + standingHtml : '' }

      <div class="vocab-footer">
        <a onclick="document.getElementById('vocab-panel').open = true; document.getElementById('vocab-panel').scrollIntoView({behavior:'smooth'});">↙ vocab glossary</a>
        &nbsp;·&nbsp; rendered ${escapeHtml(DATA.rendered)}
      </div>
    `;
    wireGotoLinks(rightbar);
  }

  // ─────────────────────────────────────────────────────────────────────
  //  Right-rail: node detail
  // ─────────────────────────────────────────────────────────────────────
  function typeLabel(t) { return t; }

  function renderNodeDetail(id) {
    const n = byId.get(id);
    if (!n) return renderToday();

    const typeBadge = '<span class="nd-type ' + escapeHtml(n.type) + '">' + escapeHtml(typeLabel(n.type)) + '</span>';
    const tentBadge = n.tentative ? ' <span class="nd-tent">[tentative]</span>' : '';
    const forecastBadge = n.is_forecast
      ? ' <span class="nd-tent" style="border-color:var(--warn);color:var(--warn);">[forecast]</span>'
      : '';

    const backBtn = history.length
      ? '<button class="nd-btn" id="nd-back">← back</button>'
      : '';

    const explain = buildExplainer(n);
    const caveats = (n.caveats || "").trim()
      ? '<div class="nd-caveats">' + inlineFormat(n.caveats) + '</div>' : '';
    const handling = (n.handling || "").trim()
      ? '<div class="nd-handling"><div class="hlabel">Handling</div>' + inlineFormat(n.handling) + '</div>' : '';

    const stmtHtml = '<div class="nd-statement">' + renderStatement(n.statement) + '</div>';

    // Related subgraph
    const related = (n.related || []).map(rid => byId.get(rid)).filter(Boolean);
    let relHtml = '';
    if (related.length) {
      relHtml += '<div class="nd-sub-h">Related subgraph</div>';
      relHtml += '<div class="nd-sub-h2">Related to (bidirectional) · ' + related.length + '</div>';
      relHtml += related.map(r =>
        '<div class="rel-card" data-goto="' + r.id + '">' +
          '<div class="rc-head">' +
            '<span class="rc-id">' + escapeHtml(r.id) + '</span>' +
            '<span class="rc-type">' + escapeHtml(r.type) + (r.tentative ? " · tentative" : "") + '</span>' +
            '<span class="rc-name">' + escapeHtml(r.name) + '</span>' +
          '</div>' +
          '<div class="rc-summary">' + escapeHtml(summaryOf(r)) + '</div>' +
        '</div>'
      ).join('');
    }

    rightbar.innerHTML = `
      <div class="nd-top">
        ${typeBadge}${tentBadge}${forecastBadge}
        <button class="nd-btn primary" id="nd-today">▸ Today</button>
        ${backBtn}
      </div>
      <div class="nd-title">${escapeHtml(n.name)}</div>
      <div class="nd-id">${escapeHtml(n.id)}${n.date ? ' · ' + escapeHtml(n.date) : ''}${n.horizon ? ' · horizon ' + escapeHtml(n.horizon) : ''}</div>
      ${handling}
      ${caveats}
      ${explain}
      ${stmtHtml}
      ${relHtml}
    `;
    wireGotoLinks(rightbar);
    const bToday = document.getElementById("nd-today");
    if (bToday) bToday.addEventListener("click", deselectNode);
    const bBack = document.getElementById("nd-back");
    if (bBack) bBack.addEventListener("click", goBack);
    rightbar.scrollTop = 0;
  }

  function buildExplainer(n) {
    const note = (DATA.type_notes || {})[n.type] || "";
    const tentNote = n.tentative
      ? " <strong>Tentative</strong> — single derivation, hold lightly. Promoted to Overlap only when a second independent instance shows."
      : "";
    const relCount = (n.related || []).length;
    const forecastNote = n.is_forecast
      ? ` Forecast (${escapeHtml(n.horizon || "horizon")}) — revisit at horizon, not before.`
      : "";
    return '<div class="nd-explain">' +
      '<strong>' + escapeHtml(n.id) + '</strong> is a <strong>' + escapeHtml(n.type) + '</strong> node — ' +
      escapeHtml(note) + tentNote + forecastNote +
      ' The fractal around it: <strong>' + relCount + '</strong> related.' +
      '</div>';
  }

  // ─────────────────────────────────────────────────────────────────────
  //  Legend & counts
  // ─────────────────────────────────────────────────────────────────────
  const hidden = new Set();
  (DATA.legend_order || []).forEach(t => {
    const count = (DATA.counts || {})[t] || 0;
    const row = document.createElement("div");
    row.className = "legend-row";
    row.dataset.type = t;
    row.innerHTML =
      '<span class="swatch ' + t + '"></span>' +
      '<span>' + t + '</span>' +
      '<span class="legend-count">' + count + '</span>';
    row.addEventListener("click", () => {
      if (hidden.has(t)) { hidden.delete(t); row.classList.remove("dim"); }
      else                { hidden.add(t); row.classList.add("dim"); }
      applyHidden();
    });
    legendEl.appendChild(row);
  });

  function applyHidden() {
    nodes.forEach(n => {
      const el = nodeEls.get(n.id);
      if (!el) return;
      el.group.style.display = hidden.has(n.type) ? "none" : "";
    });
    edges.forEach((e, i) => {
      const a = byId.get(e.from), b = byId.get(e.to);
      edgeEls[i].style.display = (a && b && !hidden.has(a.type) && !hidden.has(b.type)) ? "" : "none";
    });
  }

  // type counts line
  countsEl.innerHTML = (DATA.legend_order || []).map(t =>
    '<b>' + t[0].toUpperCase() + '</b>:' + ((DATA.counts || {})[t] || 0)
  ).join(' · ');

  // Vocab list
  if (VOCAB.length) {
    vocabEl.innerHTML = VOCAB.map(v =>
      '<div class="v-item">' +
        '<span class="v-term">' + escapeHtml(v.term) + '</span>' +
        '<span class="v-def">' + inlineFormat(v.def) + '</span>' +
      '</div>'
    ).join('');
    wireGotoLinks(vocabEl);
  } else {
    vocabEl.innerHTML = '<p style="color:var(--muted);font-style:italic;font-size:11px;">No vocab file.</p>';
  }

  // ─────────────────────────────────────────────────────────────────────
  //  Search
  // ─────────────────────────────────────────────────────────────────────
  function applySearch(q) {
    q = (q || "").trim().toLowerCase();
    nodes.forEach(n => {
      const el = nodeEls.get(n.id); if (!el) return;
      if (!q) { el.group.classList.remove("search-miss"); return; }
      const hay = (n.id + " " + (n.name || "") + " " + (n.statement || "")).toLowerCase();
      el.group.classList.toggle("search-miss", !hay.includes(q));
    });
  }
  searchEl.addEventListener("input", e => applySearch(e.target.value));

  // ─────────────────────────────────────────────────────────────────────
  //  Layout toggle — mandala ↔ force-directed
  // ─────────────────────────────────────────────────────────────────────
  let layoutMode = "mandala";
  const mandalaPositions = {};
  nodes.forEach(n => { mandalaPositions[n.id] = { x: n.x, y: n.y }; });

  function updateLayoutButton() {
    btnLayout.textContent = layoutMode === "mandala" ? "toggle → force-directed" : "toggle → mandala";
  }

  function applyPositions() {
    nodes.forEach(n => {
      const el = nodeEls.get(n.id); if (!el) return;
      el.group.setAttribute("transform", `translate(${n.x},${n.y})`);
      // label
      const ang = Math.atan2(n.y || 0.0001, n.x || 0.0001);
      const r = nodeRadius(n);
      const labelR = r + 10;
      el.text.setAttribute("x", Math.cos(ang) * labelR);
      el.text.setAttribute("y", Math.sin(ang) * labelR);
    });
    edges.forEach((e, i) => {
      const a = byId.get(e.from), b = byId.get(e.to);
      if (!a || !b) return;
      edgeEls[i].setAttribute("x1", a.x); edgeEls[i].setAttribute("y1", a.y);
      edgeEls[i].setAttribute("x2", b.x); edgeEls[i].setAttribute("y2", b.y);
    });
  }

  function runForceDirected() {
    // Simple Fruchterman-Reingold over current mandala positions.
    const area = 2000 * 2000;
    const k = Math.sqrt(area / nodes.length);
    const adj = new Map();
    edges.forEach(e => {
      if (!adj.has(e.from)) adj.set(e.from, new Set());
      if (!adj.has(e.to)) adj.set(e.to, new Set());
      adj.get(e.from).add(e.to);
      adj.get(e.to).add(e.from);
    });
    // Start from mandala layout (already set)
    let t = 120;
    const iters = 200;
    for (let it = 0; it < iters; it++) {
      const disp = new Map(nodes.map(n => [n.id, { x: 0, y: 0 }]));
      // repulsive
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i], b = nodes[j];
          let dx = a.x - b.x, dy = a.y - b.y;
          const d2 = dx*dx + dy*dy + 0.01;
          const d = Math.sqrt(d2);
          const f = (k*k) / d;
          dx /= d; dy /= d;
          disp.get(a.id).x += dx * f;
          disp.get(a.id).y += dy * f;
          disp.get(b.id).x -= dx * f;
          disp.get(b.id).y -= dy * f;
        }
      }
      // attractive (neighbors)
      edges.forEach(e => {
        const a = byId.get(e.from), b = byId.get(e.to);
        if (!a || !b) return;
        let dx = a.x - b.x, dy = a.y - b.y;
        const d = Math.sqrt(dx*dx + dy*dy) + 0.01;
        const f = (d*d) / k;
        dx /= d; dy /= d;
        disp.get(a.id).x -= dx * f;
        disp.get(a.id).y -= dy * f;
        disp.get(b.id).x += dx * f;
        disp.get(b.id).y += dy * f;
      });
      // apply + cool
      nodes.forEach(n => {
        if (n.id === DATA.now_id) { n.x = 0; n.y = 0; return; }
        const d = disp.get(n.id);
        const len = Math.sqrt(d.x*d.x + d.y*d.y) + 0.01;
        const dx = (d.x / len) * Math.min(len, t);
        const dy = (d.y / len) * Math.min(len, t);
        n.x = Math.max(-780, Math.min(780, n.x + dx));
        n.y = Math.max(-780, Math.min(780, n.y + dy));
      });
      t *= 0.97;
    }
  }

  function restoreMandala() {
    nodes.forEach(n => {
      const p = mandalaPositions[n.id];
      if (p) { n.x = p.x; n.y = p.y; }
    });
  }

  function setLayout(mode) {
    layoutMode = mode;
    if (mode === "force") runForceDirected(); else restoreMandala();
    applyPositions();
    updateLayoutButton();
    try { localStorage.setItem("alex-graph-layout", mode); } catch (_) {}
  }

  btnLayout.addEventListener("click", () => {
    setLayout(layoutMode === "mandala" ? "force" : "mandala");
  });

  try {
    const saved = localStorage.getItem("alex-graph-layout");
    if (saved === "force") setLayout("force");
  } catch (_) {}
  updateLayoutButton();

  // ─────────────────────────────────────────────────────────────────────
  //  Keyboard
  // ─────────────────────────────────────────────────────────────────────
  document.addEventListener("keydown", e => {
    if (e.target === searchEl) {
      if (e.key === "Escape") { searchEl.value = ""; applySearch(""); searchEl.blur(); }
      return;
    }
    if (e.key === "Escape") { deselectNode(); }
    else if (e.key === "/") { e.preventDefault(); searchEl.focus(); }
    else if (e.key === "+" || e.key === "=") { e.preventDefault(); zoomAt(1.2); }
    else if (e.key === "-" || e.key === "_") { e.preventDefault(); zoomAt(1/1.2); }
    else if (e.key === "0")                   { e.preventDefault(); resetView(); }
  });

  // Initial right rail
  renderToday();

  // Debug hook
  window.__alex = { selectNode, deselectNode, setLayout, DATA };
})();
</script>
</body>
</html>
"""


def emit_html(payload, out_path: Path, vocab, actions, eyes):
    def dump(obj):
        return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")

    node_count = len(payload["nodes"])
    edge_count = len(payload["edges"])

    html = HTML_TEMPLATE
    html = html.replace("__NODE_COUNT__", str(node_count))
    html = html.replace("__EDGE_COUNT__", str(edge_count))
    html = html.replace("__DATA_JSON__",    dump(payload))
    html = html.replace("__VOCAB_JSON__",   dump(vocab))
    html = html.replace("__ACTIONS_JSON__", dump(actions))
    html = html.replace("__EYES_JSON__",    dump(eyes))

    out_path.write_text(html, encoding="utf-8")


def main():
    if not YAML_PATH.exists():
        sys.exit(f"Not found: {YAML_PATH}")
    nodes = load_nodes(YAML_PATH)
    payload = build_payload(nodes)

    vocab   = parse_vocab(VOCAB_PATH)
    actions = parse_action_cards(ACTIONS_PATH)
    eyes    = parse_needs_eyes(EYES_PATH)

    emit_html(payload, OUT_PATH, vocab, actions, eyes)

    # Mirror to parrik.com if the target directory exists
    if MIRROR_PATH.parent.exists():
        MIRROR_PATH.write_text(OUT_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"  mirrored → {MIRROR_PATH}")

    size = OUT_PATH.stat().st_size
    print(f"Rendered: {OUT_PATH}  ({size:,} bytes)")
    print(f"  nodes: {len(payload['nodes'])}  edges: {len(payload['edges'])}")
    print(f"  risk corridor downstream: {len(payload['risk_downstream'])} nodes")
    print(f"  spine top-{len(payload['spine'])}: " +
          ", ".join(s["id"] + " (x" + str(s["count"]) + ")" for s in payload["spine"]))
    print(f"  counts by type: {payload['counts']}")
    print(f"  vocab entries: {len(vocab)}  threads: {len(actions)}  needs-eyes: {len(eyes)}")


if __name__ == "__main__":
    main()
