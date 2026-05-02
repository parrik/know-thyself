#!/usr/bin/env python3
"""
render_dashboard.py — generate the Alex interactive dashboard HTML.

Apple-inspired tabbed layout (refresh, May 2 2026):

  - Today     curated single-column hero + multi-column responsive cards-grid
              with sub-nav pill filter (All / Frame / Week / Threads / Eyes /
              Canaries / Recent). Every card item is actionable — Done /
              Snooze 7d buttons persist in localStorage.
  - Fractal   the concentric-ring mandala (vanilla SVG, no library deps),
              click any node to open it in the slide-over drawer.
  - Sources   the bundle index — links to alex-actions.md / alex-needs-eyes.md /
              alex-vocab.md / SCHEMA.md / SAFETY.md / README.md.
  - Vocab     the glossary.

Reads:
  - example-graph-extended.yaml   (graph: nodes + provenance)
  - alex-vocab.md                 (glossary)
  - alex-actions.md               (open threads cards)
  - alex-needs-eyes.md            (items needing review)

Writes:
  - example-graph-extended.html   (single self-contained file)

Requires: pyyaml only.

Run: python3 render_dashboard.py
Open: example-graph-extended.html in any browser.
"""
import json
import math
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("ERROR: install pyyaml — pip install pyyaml")


HERE         = Path(__file__).resolve().parent
YAML_PATH    = HERE / "example-graph-extended.yaml"
VOCAB_PATH   = HERE / "alex-vocab.md"
ACTIONS_PATH = HERE / "alex-actions.md"
EYES_PATH    = HERE / "alex-needs-eyes.md"
OUT_PATH     = HERE / "example-graph-extended.html"


# ──────────────────────────────────────────────────────────────────────────
#  Schema — rings, type names, colors
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
    "open-question": 8,
}

RING_RADIUS = [0, 130, 235, 340, 445, 550, 645, 730, 810]

TYPE_COLOR = {
    "now":         "#fbbf24",
    "practice":    "#ef4444",
    "emergent":    "#8b5cf6",
    "overlap":     "#10b981",
    "novel":       "#f59e0b",
    "observation": "#0ea5e9",
    "equivalency": "#14b8a6",
    "reference":   "#3b82f6",
    "open":        "#6b7280",
    "open-question": "#6b7280",
}

TYPE_LABEL = {
    "now":         "Now",
    "practice":    "Practice",
    "emergent":    "Emergent",
    "overlap":     "Overlap",
    "novel":       "Novel · tentative",
    "observation": "Observation",
    "equivalency": "Equivalency",
    "reference":   "Reference",
    "open":        "Open question",
    "open-question": "Open question",
}


# ──────────────────────────────────────────────────────────────────────────
#  Parsing
# ──────────────────────────────────────────────────────────────────────────

def parse_vocab(path):
    """Lines like `- **term** — definition`."""
    entries = []
    if not path.exists():
        return entries
    for line in path.read_text().splitlines():
        m = re.match(r'^-\s+\*\*([^*]+?)\*\*\s*[—-]\s*(.+)$', line)
        if m:
            entries.append({"term": m.group(1).strip(), "def": m.group(2).strip()})
    return entries


def parse_action_cards(path):
    """Markdown of the form:
        ## Heading text
        Body text spanning one or more lines.

        ## Next heading
        ...
    Returns [{title, body}, ...] in document order.
    """
    if not path.exists():
        return []
    text = path.read_text()
    cards = []
    current = None
    for line in text.splitlines():
        h = re.match(r'^##\s+(.+)$', line)
        if h:
            if current and (current["body"].strip() or current["title"]):
                cards.append(current)
            current = {"title": h.group(1).strip().rstrip('.'), "body": ""}
        elif current is not None:
            if line.strip():
                current["body"] += (" " if current["body"] else "") + line.strip()
    if current and (current["body"].strip() or current["title"]):
        cards.append(current)
    return cards


def extract_now_section(now_text, heading_pattern):
    """From a NOW.statement, extract `## heading_pattern` body until next `## ` or end."""
    if not now_text:
        return ""
    pat = r'^##\s+' + heading_pattern + r'.*?\n(.*?)(?=\n##\s|\Z)'
    m = re.search(pat, now_text, re.S | re.M)
    return m.group(1).strip() if m else ""


def extract_bullets(text):
    items = []
    for line in text.splitlines():
        m = re.match(r'^\s*[•\-\*]\s+(.+)$', line)
        if m:
            items.append(m.group(1).strip())
    return items


# ──────────────────────────────────────────────────────────────────────────
#  Graph parsing + ring layout
# ──────────────────────────────────────────────────────────────────────────

NODE_ID_RE = re.compile(r"\b((?:R|O|N|E|P|PR|OQ|EQ|KT)\d+(?:-[A-Za-z0-9-]+)?)\b")


def normalize_type(t):
    if not t:
        return "reference"
    t = t.strip().lower()
    if t in ("open question", "openquestion"):
        return "open"
    return t


def parse_graph(yaml_path):
    raw = yaml.safe_load(yaml_path.read_text())
    if not isinstance(raw, list):
        sys.exit("ERROR: example-graph-extended.yaml must be a top-level YAML list")

    nodes = []
    edges = set()
    for entry in raw:
        if not isinstance(entry, dict) or "id" not in entry:
            continue
        if entry.get("shelved") is True:
            continue
        nid = str(entry["id"])
        ntype = normalize_type(entry.get("type"))
        name = entry.get("name", nid)
        statement = entry.get("statement", "") or ""
        caveats = entry.get("caveats", "") or ""
        tentative = bool(entry.get("tentative", False))
        horizon = entry.get("horizon")

        prov = entry.get("provenance") or {}
        deriv = (prov.get("derivation") or {}) if isinstance(prov, dict) else {}
        attribution = (prov.get("attribution") or {}) if isinstance(prov, dict) else {}
        evidence = (prov.get("evidence") or {}) if isinstance(prov, dict) else {}

        related_to = entry.get("related_to") or []
        derives_from = deriv.get("from") or []
        evidence_refs = evidence.get("references") or []

        if not isinstance(related_to, list): related_to = [related_to]
        if not isinstance(derives_from, list): derives_from = [derives_from]
        if not isinstance(evidence_refs, list): evidence_refs = [evidence_refs]

        nodes.append({
            "id": nid,
            "name": str(name),
            "type": ntype,
            "statement": str(statement),
            "caveats": str(caveats),
            "tentative": tentative,
            "horizon": horizon,
            "attribution": attribution,
            "evidence": evidence,
            "derivation": deriv,
            "related_to": [str(x) for x in related_to],
            "derives_from": [str(x) for x in derives_from],
            "evidence_refs": [str(x) for x in evidence_refs],
        })

        for r in related_to: edges.add((nid, str(r)))
        for r in derives_from: edges.add((nid, str(r)))
        for r in evidence_refs: edges.add((nid, str(r)))
        for m in NODE_ID_RE.finditer(statement + " " + caveats):
            ref = m.group(1)
            if ref != nid:
                edges.add((nid, ref))

    known = {n["id"] for n in nodes}
    edges_list = [{"from": a, "to": b} for (a, b) in edges if a in known and b in known]

    # Ring positions
    by_type = {}
    for n in nodes:
        if n["id"] == "NOW":
            n["x"] = 0
            n["y"] = 0
            continue
        by_type.setdefault(n["type"], []).append(n)

    for ntype, ring_nodes in by_type.items():
        ring = TYPE_RING.get(ntype, len(RING_RADIUS) - 1)
        radius = RING_RADIUS[ring]
        def k(n):
            m = re.search(r'\d+', n["id"])
            return int(m.group(0)) if m else 0
        ring_nodes.sort(key=k)
        count = len(ring_nodes)
        if count == 1:
            ring_nodes[0]["x"] = 0
            ring_nodes[0]["y"] = -radius if radius else 0
            continue
        for i, n in enumerate(ring_nodes):
            angle = -math.pi / 2 + 2 * math.pi * i / count
            n["x"] = round(radius * math.cos(angle), 1)
            n["y"] = round(radius * math.sin(angle), 1)

    backlinks = {}
    for e in edges_list:
        backlinks[e["to"]] = backlinks.get(e["to"], 0) + 1
    for n in nodes:
        n["backlink_count"] = backlinks.get(n["id"], 0)

    return {"nodes": nodes, "edges": edges_list}


def extract_now_panels(graph):
    now = next((n for n in graph["nodes"] if n["id"] == "NOW"), None)
    if not now:
        return {"frame": "", "week": [], "month": [], "quarter": [], "rules": [], "canaries": []}
    txt = now["statement"]
    return {
        "frame":    extract_now_section(txt, r'Frame'),
        "week":     extract_bullets(extract_now_section(txt, r'This week')),
        "month":    extract_bullets(extract_now_section(txt, r'This month')),
        "quarter":  extract_bullets(extract_now_section(txt, r'This quarter')),
        "rules":    extract_bullets(extract_now_section(txt, r'Standing rules')),
        "canaries": extract_bullets(extract_now_section(txt, r'Canaries')),
    }


# ──────────────────────────────────────────────────────────────────────────
#  HTML template
# ──────────────────────────────────────────────────────────────────────────

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Alex · know-thyself</title>
<style>
  * { box-sizing: border-box; }
  :root {
    --bg: #fbfaf7;
    --bg-elev: #ffffff;
    --text: #1d1d1f;
    --text-2: #525258;
    --text-3: #8e8e93;
    --line: rgba(0,0,0,0.09);
    --line-strong: rgba(0,0,0,0.16);
    --accent: #1e6fd9;
    --warm: #b8873e;
    --serif: "Charter","Iowan Old Style","Georgia",ui-serif,serif;
    --sans: -apple-system,BlinkMacSystemFont,"SF Pro Text","SF Pro Display","Segoe UI",Roboto,sans-serif;
    --mono: "SF Mono","Menlo",monospace;
  }
  html,body { margin:0; padding:0; background:var(--bg); color:var(--text); font-family:var(--sans); -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale; }
  a { color:var(--accent); text-decoration:none; }
  a:hover { text-decoration:underline; }

  /* Tab bar — segmented control */
  .tabbar { position:sticky; top:0; z-index:100; background:rgba(251,250,247,0.86); -webkit-backdrop-filter:saturate(180%) blur(14px); backdrop-filter:saturate(180%) blur(14px); border-bottom:1px solid var(--line); padding:10px 24px; height:56px; display:flex; align-items:center; justify-content:space-between; }
  .tabbar .brand { font-size:13px; color:var(--text-2); font-weight:500; }
  .tabbar .seg { display:flex; gap:0; background:rgba(0,0,0,0.05); border-radius:9px; padding:2px; }
  .tabbar button { background:transparent; border:none; cursor:pointer; font-family:var(--sans); font-size:13px; color:var(--text-2); padding:5px 14px; border-radius:7px; font-weight:500; transition:background 0.15s, color 0.15s, box-shadow 0.15s; }
  .tabbar button:hover { color:var(--text); }
  .tabbar button.active { background:var(--bg-elev); color:var(--text); box-shadow:0 1px 2px rgba(0,0,0,0.06); font-weight:590; }
  .tabbar .meta { font-size:11.5px; color:var(--text-3); font-variant:tabular-nums; font-family:var(--mono); }

  .tab-panel { display:none; }
  .tab-panel.active { display:block; }
  .container { max-width:720px; margin:0 auto; padding:56px 32px 120px; }

  /* Card filter pills */
  .card-filter { display:flex; gap:2px; flex-wrap:wrap; margin:32px 0 22px; padding:3px; background:rgba(0,0,0,0.05); border-radius:9px; width:fit-content; max-width:100%; }
  .card-filter button { background:transparent; border:none; cursor:pointer; font-family:var(--sans); font-size:13px; color:var(--text-2); padding:6px 14px; border-radius:7px; font-weight:500; transition:background 0.12s, color 0.12s, box-shadow 0.12s; }
  .card-filter button:hover { color:var(--text); }
  .card-filter button.active { background:var(--bg-elev); color:var(--text); box-shadow:0 1px 2px rgba(0,0,0,0.06); font-weight:590; }

  /* Multi-column card grid */
  .cards-grid { column-count:1; column-gap:18px; margin-top:8px; }
  .cards-grid > * { break-inside:avoid; -webkit-column-break-inside:avoid; page-break-inside:avoid; display:block; }
  .cards-grid > .card, .cards-grid > div > .card { margin-bottom:18px; }
  .cards-grid > div:empty { display:none; }
  .cards-grid.filtered { column-count:1 !important; }
  .cards-grid.filtered > * { display:none; }
  .cards-grid.filtered > .focus-card { display:block; }

  /* Hero */
  .hero { max-width:720px; }
  .hero .eyebrow { font-size:13px; color:var(--text-3); font-variant:tabular-nums; letter-spacing:0.04em; text-transform:uppercase; font-weight:500; }
  .hero .lead { font-family:var(--serif); font-size:28px; line-height:1.35; color:var(--text); margin:14px 0 0; letter-spacing:-0.005em; }
  .hero .twogoals { margin-top:18px; font-size:13px; color:var(--text-3); }
  .hero .twogoals strong { color:var(--text-2); font-weight:500; }

  /* Card */
  .card { padding:30px 34px; border:1px solid var(--line); border-radius:16px; background:var(--bg-elev); margin-bottom:16px; }
  .card-label { font-size:13px; color:var(--text-3); margin-bottom:6px; font-weight:400; font-style:italic; font-family:var(--serif); }
  .card h2 { font-size:24px; font-weight:600; margin:0 0 16px; letter-spacing:-0.012em; color:var(--text); line-height:1.25; font-family:var(--serif); }
  .card h3 { font-size:17px; font-weight:600; margin:20px 0 10px; color:var(--text); }
  .card p { font-size:16px; line-height:1.7; color:var(--text); margin:0 0 14px; max-width:60ch; font-family:var(--serif); }
  .card .sub { font-size:14px; color:var(--text-2); line-height:1.6; max-width:60ch; }

  .card.frame { border-left:3px solid var(--text); padding-left:31px; }
  .card.canary { border-color:rgba(184,135,62,0.35); background:rgba(184,135,62,0.04); border-left:3px solid var(--warm); padding-left:31px; }
  .card.canary .card-label { color:var(--warm); font-style:normal; font-family:var(--sans); font-size:11px; text-transform:uppercase; letter-spacing:0.14em; font-weight:600; margin-bottom:14px; }
  .card.canary h2 { color:#5a3f12; }

  /* Actionable items */
  .act-item { padding:20px 0; border-top:1px solid var(--line); }
  .act-item:first-of-type { border-top:none; padding-top:6px; }
  .card.canary .act-item { border-top-color:rgba(184,135,62,0.18); }
  .act-item .a-text { font-family:var(--serif); font-size:16px; line-height:1.65; color:var(--text); max-width:62ch; }
  .act-item .a-text strong { font-weight:600; color:var(--text); }
  .act-item .a-hint { margin-top:8px; font-size:13px; color:var(--text-2); font-family:var(--sans); max-width:62ch; display:flex; align-items:center; gap:6px; }
  .act-item .a-hint::before { content:"→"; color:var(--text-3); font-weight:600; }
  .act-item .a-actions { margin-top:12px; display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
  .act-item button, .act-item a.btn { background:var(--bg-elev); border:1px solid var(--line-strong); color:var(--text-2); font-size:12.5px; font-family:var(--sans); padding:6px 14px; border-radius:8px; cursor:pointer; font-weight:500; transition:all 0.12s; display:inline-flex; align-items:center; gap:5px; text-decoration:none; }
  .act-item button:hover, .act-item a.btn:hover { background:rgba(0,0,0,0.04); color:var(--text); border-color:var(--text); }
  .act-item button.primary { background:var(--text); color:#fff; border-color:var(--text); font-weight:600; }
  .act-item button.primary:hover { background:#000; border-color:#000; color:#fff; }
  .card.canary .act-item button.primary { background:var(--warm); color:#fff; border-color:var(--warm); }
  .card.canary .act-item button.primary:hover { background:#a37733; border-color:#a37733; }
  .show-resolved { margin-top:20px; padding-top:14px; border-top:1px solid var(--line); font-size:13px; color:var(--text-2); font-family:var(--sans); }
  .show-resolved a { color:var(--accent); cursor:pointer; }
  .card-empty { text-align:center; padding:24px 0 8px; font-style:italic; font-family:var(--serif); color:var(--text-2); font-size:15px; }
  .card-empty::before { content:"✓ "; color:#10b981; font-style:normal; font-weight:700; }

  /* Recent */
  .recent .ritem { padding:13px 0; border-top:1px solid var(--line); font-size:15px; color:var(--text); line-height:1.5; }
  .recent .ritem:first-child { border-top:none; padding-top:4px; }
  .recent .rid { font-family:var(--mono); color:var(--accent); font-size:13px; margin-right:12px; cursor:pointer; }
  .recent .rid:hover { text-decoration:underline; }
  .recent .rtag { color:var(--warm); font-size:11px; text-transform:uppercase; letter-spacing:0.14em; margin-left:10px; font-weight:600; }

  /* Footer */
  .wisdom-footer { margin-top:64px; padding-top:24px; border-top:1px solid var(--line); text-align:center; font-size:13px; color:var(--text-3); line-height:1.7; }
  .wisdom-footer strong { color:var(--text-2); font-weight:500; }
  .wisdom-footer a { color:var(--accent); cursor:pointer; }

  /* Fractal */
  #network-wrap { position:relative; height:calc(100vh - 56px); overflow:hidden; }
  #network { width:100%; height:100%; background:var(--bg); cursor:grab; user-select:none; }
  #network:active { cursor:grabbing; }
  #network svg { width:100%; height:100%; }
  #fractal-controls { position:absolute; top:24px; left:24px; background:rgba(255,255,255,0.94); -webkit-backdrop-filter:blur(10px); backdrop-filter:blur(10px); padding:14px 16px; border-radius:12px; border:1px solid var(--line); font-size:13px; max-width:260px; z-index:5; }
  #fractal-controls .ctitle { font-size:11px; color:var(--text-3); text-transform:uppercase; letter-spacing:0.14em; margin-bottom:8px; font-weight:600; }
  #fractal-controls .legend-item { display:flex; align-items:center; padding:4px 6px; cursor:pointer; border-radius:5px; user-select:none; font-size:13px; color:var(--text); }
  #fractal-controls .legend-item:hover { background:rgba(0,0,0,0.04); }
  #fractal-controls .legend-item.dim { opacity:0.4; }
  #fractal-controls .swatch { width:9px; height:9px; border-radius:50%; margin-right:8px; }
  #fractal-controls input[type=text] { width:100%; padding:7px 10px; border:1px solid var(--line-strong); border-radius:7px; font-size:13px; margin-top:10px; font-family:var(--sans); background:var(--bg-elev); color:var(--text); }
  #fractal-controls .toggle-row { margin-top:12px; padding-top:10px; border-top:1px solid var(--line); display:flex; align-items:center; gap:8px; font-size:12.5px; color:var(--text-2); }
  #fractal-controls .stats { margin-top:10px; font-size:11px; color:var(--text-3); font-variant:tabular-nums; }
  #fractal-zoom { position:absolute; top:24px; right:24px; display:flex; flex-direction:column; gap:4px; z-index:5; }
  #fractal-zoom button { width:32px; height:32px; background:rgba(255,255,255,0.94); border:1px solid var(--line); border-radius:7px; cursor:pointer; font-size:17px; color:var(--text); }
  #fractal-zoom button:hover { border-color:var(--accent); color:var(--accent); }

  .node circle { transition:opacity 0.2s, r 0.15s; }
  .node text { font-family:var(--sans); font-size:11px; fill:var(--text); pointer-events:none; user-select:none; paint-order:stroke; stroke:var(--bg); stroke-width:3px; stroke-linejoin:round; }
  .node.tentative circle { stroke:var(--warm); stroke-width:2; }
  .node.now circle { stroke:#fde68a; stroke-width:3; }
  .node:hover circle { r:14; cursor:pointer; }
  .edge { stroke:rgba(0,0,0,0.15); stroke-width:0.7; fill:none; pointer-events:none; }
  .node.dim { opacity:0.18; }
  .node.dim circle { pointer-events:none; }

  /* Drawer */
  #drawer-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.16); opacity:0; pointer-events:none; transition:opacity 0.2s; z-index:199; }
  #drawer-overlay.open { opacity:1; pointer-events:auto; }
  #drawer { position:fixed; top:0; right:-620px; width:600px; max-width:96vw; height:100vh; background:var(--bg-elev); border-left:1px solid var(--line); box-shadow:-1px 0 0 var(--line), 0 12px 40px rgba(0,0,0,0.08); transition:right 0.25s cubic-bezier(0.16, 1, 0.3, 1); z-index:200; display:flex; flex-direction:column; }
  #drawer.open { right:0; }
  #drawer .dhead { padding:14px 22px; border-bottom:1px solid var(--line); display:flex; align-items:center; justify-content:space-between; flex-shrink:0; }
  #drawer .dtype { font-size:11px; text-transform:uppercase; letter-spacing:0.14em; color:var(--text-3); font-weight:600; }
  #drawer .dhead .controls { display:flex; gap:6px; align-items:center; }
  #drawer .dhead button { background:none; border:1px solid var(--line-strong); border-radius:7px; padding:5px 12px; cursor:pointer; font-size:13px; color:var(--text-2); font-family:var(--sans); }
  #drawer .dhead button:hover { color:var(--text); border-color:var(--text); }
  #drawer .dhead .esc-hint { font-size:11px; color:var(--text-3); font-family:var(--mono); }
  #drawer .dbody { padding:32px 40px 64px; overflow-y:auto; flex:1; }
  #drawer h1 { font-size:30px; margin:0 0 6px; font-weight:600; letter-spacing:-0.015em; line-height:1.2; color:var(--text); font-family:var(--serif); }
  #drawer .dmeta { font-family:var(--mono); font-size:12px; color:var(--text-3); margin-bottom:24px; }
  #drawer .dmeta .tent { color:var(--warm); font-weight:600; margin-right:6px; }
  #drawer .stmt { font-family:var(--serif); font-size:17px; line-height:1.7; color:var(--text); }
  #drawer .stmt p { margin:0 0 14px; }
  #drawer .stmt ul { padding-left:1.2em; margin:0 0 14px; list-style:none; }
  #drawer .stmt li { padding-left:1em; position:relative; margin:6px 0; }
  #drawer .stmt li::before { content:"·"; color:var(--text-3); position:absolute; left:0; font-weight:700; }
  #drawer .stmt strong { color:var(--text); font-weight:600; }
  #drawer .stmt em { color:var(--text); font-style:italic; }
  #drawer .stmt code { font-family:var(--mono); font-size:14px; background:rgba(0,0,0,0.04); color:var(--text); padding:1px 6px; border-radius:4px; }
  #drawer .ref { color:var(--accent); cursor:pointer; font-family:var(--mono); font-size:0.92em; font-style:normal; }
  #drawer .ref:hover { text-decoration:underline; }
  #drawer .caveats { margin:20px 0; padding:14px 16px; background:rgba(184,135,62,0.08); border-left:3px solid var(--warm); border-radius:0 8px 8px 0; font-family:var(--sans); font-size:14px; line-height:1.6; color:#4a4030; }
  #drawer .caveats .clab { font-size:11px; text-transform:uppercase; letter-spacing:0.14em; color:var(--warm); margin-bottom:8px; font-weight:600; }
  #drawer .related { margin-top:36px; padding-top:24px; border-top:1px solid var(--line); }
  #drawer .relgroup { margin-bottom:16px; }
  #drawer .rlab { font-family:var(--sans); font-size:11px; text-transform:uppercase; letter-spacing:0.14em; color:var(--text-3); margin-bottom:10px; font-weight:600; }
  #drawer .relnode { padding:11px 14px; margin:5px 0; background:var(--bg); border:1px solid var(--line); border-radius:9px; cursor:pointer; transition:all 0.15s; }
  #drawer .relnode:hover { background:rgba(30,111,217,0.04); border-color:var(--accent); }
  #drawer .relnode .rhead { display:flex; align-items:baseline; gap:8px; }
  #drawer .relnode .rid { font-family:var(--mono); font-size:12px; color:var(--accent); font-weight:500; }
  #drawer .relnode .rname { font-size:14px; color:var(--text); font-weight:500; }
  #drawer .relnode .rsum { font-size:13px; color:var(--text-2); margin-top:4px; line-height:1.5; }
  #drawer .provenance { margin-top:20px; padding:12px 14px; background:rgba(0,0,0,0.025); border-radius:9px; font-family:var(--sans); font-size:13px; color:var(--text-2); line-height:1.6; }
  #drawer .provenance .plab { font-size:11px; text-transform:uppercase; letter-spacing:0.14em; color:var(--text-3); margin-bottom:6px; font-weight:600; }
  #drawer .mentioned { margin-top:24px; padding-top:18px; border-top:1px solid var(--line); }
  #drawer .mentioned .ref { margin-right:10px; line-height:1.9; font-size:13px; }

  /* Sources / vocab */
  .source-list, .vocab-list { margin-top:24px; }
  .source-item { display:block; padding:18px 0; border-bottom:1px solid var(--line); text-decoration:none; color:var(--text); cursor:pointer; }
  .source-item:hover .stitle { color:var(--accent); }
  .source-item .stitle { font-size:17px; font-weight:500; transition:color 0.15s; letter-spacing:-0.005em; }
  .source-item .sdesc { font-size:14px; color:var(--text-2); margin-top:4px; line-height:1.5; }
  .vocab-row { padding:14px 0; border-bottom:1px solid var(--line); }
  .vocab-row .vterm { font-weight:600; color:var(--text); font-size:15px; }
  .vocab-row .vdef { color:var(--text-2); font-size:14px; line-height:1.6; margin-top:4px; }
  .panel-hero h1 { font-size:34px; font-weight:600; letter-spacing:-0.02em; margin:0 0 4px; line-height:1.1; }
  .panel-hero .sub { font-size:14px; color:var(--text-2); }

  ::-webkit-scrollbar { width:9px; height:9px; }
  ::-webkit-scrollbar-track { background:transparent; }
  ::-webkit-scrollbar-thumb { background:rgba(0,0,0,0.13); border-radius:5px; }
  ::-webkit-scrollbar-thumb:hover { background:rgba(0,0,0,0.25); }

  @media (max-width: 640px) {
    .container { padding:36px 18px 80px; }
    .hero .lead { font-size:22px; }
    .card { padding:20px 18px; }
    .card h2 { font-size:20px; }
    #drawer { width:100vw; }
  }
  @media (min-width: 1100px) {
    .container { max-width:1080px; padding:64px 36px 120px; }
    .cards-grid { column-count:2; }
  }
  @media (min-width: 1600px) {
    .container { max-width:1520px; padding:72px 48px 140px; }
    .cards-grid { column-count:3; }
  }
</style>
</head>
<body>
<nav class="tabbar">
  <div class="brand">Alex · know-thyself</div>
  <div class="seg">
    <button data-tab="today" class="active">Today</button>
    <button data-tab="fractal">Fractal</button>
    <button data-tab="sources">Sources</button>
    <button data-tab="vocab">Vocab</button>
  </div>
  <div class="meta"><span id="nodecount">0</span> nodes · <span id="edgecount">0</span> edges</div>
</nav>

<section id="tab-today" class="tab-panel active">
  <div class="container">
    <header class="hero">
      <div class="eyebrow" id="hero-eyebrow"></div>
      <p class="lead" id="hero-lead"></p>
      <div class="twogoals">Two goals: <strong>know thyself</strong> · <strong>reveal thyself</strong></div>
    </header>

    <div class="card-filter" id="card-filter">
      <button data-card="all" class="active">All</button>
      <button data-card="frame">Frame</button>
      <button data-card="week">Week</button>
      <button data-card="threads">Threads</button>
      <button data-card="eyes">Eyes</button>
      <button data-card="canaries">Canaries</button>
      <button data-card="recent">Recent</button>
    </div>

    <div class="cards-grid" id="cards-grid">
      <div id="frame-card" class="card frame" data-card="frame"></div>
      <div id="week-card" class="card" data-card="week"></div>
      <div id="threads-card" class="card" data-card="threads"></div>
      <div id="eyes-slot" data-card="eyes"></div>
      <div id="canaries-slot" data-card="canaries"></div>
      <div id="recent-card" class="card" data-card="recent"></div>
    </div>

    <footer class="wisdom-footer">
      <div><strong>Spine</strong> · <strong>provenance</strong> · <strong>reveal thyself monthly</strong></div>
      <div style="margin-top:14px;"><a onclick="openDrawer('NOW')">Open the full NOW node →</a></div>
    </footer>
  </div>
</section>

<section id="tab-fractal" class="tab-panel">
  <div id="network-wrap">
    <div id="network"></div>
    <div id="fractal-controls">
      <div class="ctitle">Filter by type</div>
      <div class="legend-item" data-type="practice"><span class="swatch" style="background:#ef4444;"></span>Practice</div>
      <div class="legend-item" data-type="emergent"><span class="swatch" style="background:#8b5cf6;"></span>Emergent</div>
      <div class="legend-item" data-type="overlap"><span class="swatch" style="background:#10b981;"></span>Overlap</div>
      <div class="legend-item" data-type="novel"><span class="swatch" style="background:#f59e0b;"></span>Novel · tentative</div>
      <div class="legend-item" data-type="observation"><span class="swatch" style="background:#0ea5e9;"></span>Observation</div>
      <div class="legend-item" data-type="reference"><span class="swatch" style="background:#3b82f6;"></span>Reference</div>
      <div class="legend-item" data-type="open"><span class="swatch" style="background:#6b7280;"></span>Open question</div>
      <input type="text" id="search" placeholder="search id or name…" />
      <div class="toggle-row">
        <input type="checkbox" id="declutter" checked>
        <label for="declutter">Hide thin reference nodes (≤1 link in)</label>
      </div>
      <div class="stats" id="fractal-stats"></div>
    </div>
    <div id="fractal-zoom">
      <button title="Zoom in (+)" onclick="zoomBy(1.25)">+</button>
      <button title="Zoom out (−)" onclick="zoomBy(0.8)">−</button>
      <button title="Fit all (0)" onclick="fitMandala()">⟲</button>
    </div>
  </div>
</section>

<section id="tab-sources" class="tab-panel">
  <div class="container">
    <header class="panel-hero">
      <h1>Sources</h1>
      <div class="sub">Underlying files in the example bundle.</div>
    </header>
    <div class="source-list" id="source-list"></div>
  </div>
</section>

<section id="tab-vocab" class="tab-panel">
  <div class="container">
    <header class="panel-hero">
      <h1>Vocab</h1>
      <div class="sub" id="vocab-count"></div>
    </header>
    <div class="vocab-list" id="vocab-list"></div>
  </div>
</section>

<div id="drawer-overlay" onclick="closeDrawer()"></div>
<aside id="drawer">
  <div class="dhead">
    <div class="dtype" id="drawer-type"></div>
    <div class="controls">
      <button id="drawer-back" style="display:none;" onclick="drawerBack()">← back</button>
      <span class="esc-hint">esc</span>
      <button onclick="closeDrawer()">Done</button>
    </div>
  </div>
  <div class="dbody">
    <h1 id="drawer-title"></h1>
    <div class="dmeta" id="drawer-meta"></div>
    <div class="stmt" id="drawer-stmt"></div>
  </div>
</aside>

<script>
const GRAPH = __DATA__;
const VOCAB = __VOCAB__;
const THREADS = __THREADS__;
const EYES = __EYES__;
const NOW_PANELS = __NOW_PANELS__;
const TYPE_COLOR = __TYPE_COLOR__;
const TYPE_LABEL = __TYPE_LABEL__;

document.getElementById('nodecount').textContent = GRAPH.nodes.length;
document.getElementById('edgecount').textContent = GRAPH.edges.length;

document.querySelectorAll('.tabbar button').forEach(btn => {
  btn.addEventListener('click', () => switchTab(btn.dataset.tab));
});
function switchTab(name) {
  document.querySelectorAll('.tabbar button').forEach(b => b.classList.toggle('active', b.dataset.tab === name));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.toggle('active', p.id === 'tab-' + name));
  if (name === 'fractal') {
    if (!mandalaInited) initMandala();
    setTimeout(fitMandala, 30);
  }
  history.replaceState(null, '', '#' + name);
}

function escapeHtml(s) { return String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
function inlineFormat(s) {
  let t = escapeHtml(s);
  t = t.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  t = t.replace(/\*([^*\s][^*]*?[^*\s]|\S)\*/g, '<em>$1</em>');
  t = t.replace(/`([^`]+)`/g, '<code>$1</code>');
  t = t.replace(/\b((?:R|O|N|E|P|PR|OQ|EQ|KT)\d{1,3}(?:-[A-Za-z0-9-]+)?)\b/g, '<span class="ref" onclick="openDrawer(\'$1\')">$1</span>');
  t = t.replace(/\bNOW\b/g, '<span class="ref" onclick="openDrawer(\'NOW\')">NOW</span>');
  return t;
}
function renderMarkdown(text) {
  if (!text) return '';
  const lines = text.split(/\r?\n/);
  const out = []; let inList = false; let para = [];
  function flushPara() { if (para.length) { out.push('<p>' + inlineFormat(para.join(' ')) + '</p>'); para = []; } }
  function closeList() { if (inList) { out.push('</ul>'); inList = false; } }
  for (let raw of lines) {
    const line = raw.replace(/\s+$/, '');
    if (!line.trim()) { flushPara(); closeList(); continue; }
    const h = line.match(/^#{1,3}\s+(.+)$/);
    if (h) { flushPara(); closeList(); out.push('<h3 style="font-family:var(--sans);font-size:11px;text-transform:uppercase;letter-spacing:0.14em;color:var(--text-3);font-weight:600;margin:18px 0 10px;">' + escapeHtml(h[1]) + '</h3>'); continue; }
    const b = line.match(/^\s*[•\*\-]\s+(.+)$/);
    if (b) { flushPara(); if (!inList) { out.push('<ul>'); inList = true; } out.push('<li>' + inlineFormat(b[1]) + '</li>'); continue; }
    closeList(); para.push(line.trim());
  }
  flushPara(); closeList();
  return out.join('\n');
}
function resolveRef(ref) {
  const tok = (ref || '').match(/^((?:R|O|N|E|P|PR|OQ|EQ|KT)\d{1,3}[a-z]?(?:-[A-Za-z0-9-]+)?|NOW)/);
  if (!tok) return null;
  const k = tok[0];
  return GRAPH.nodes.find(x => x.id === k) || GRAPH.nodes.find(x => x.id.startsWith(k + '-')) || null;
}
function summaryOf(n) {
  if (!n || !n.statement) return '';
  const f = n.statement.split(/\n\s*\n/)[0].trim().replace(/\s+/g, ' ');
  return f.length > 160 ? f.slice(0,160) + '…' : f;
}

// Action state — localStorage per item
function _hash(s) { let h = 0; for (let i = 0; i < s.length; i++) h = (h*31 + s.charCodeAt(i)) | 0; return Math.abs(h).toString(36); }
function actKey(text) { return 'a:' + _hash(text); }
function getAct(text) { try { return JSON.parse(localStorage.getItem(actKey(text)) || 'null'); } catch(e) { return null; } }
function setAct(text, state) { if (state === null) localStorage.removeItem(actKey(text)); else localStorage.setItem(actKey(text), JSON.stringify(state)); }
function isHiddenItem(text) {
  const s = getAct(text);
  if (!s) return false;
  if (s.status === 'done') return true;
  if (s.status === 'daily-done') return s.day === new Date().toDateString();
  if (s.status === 'deferred' && s.until > Date.now()) return true;
  return false;
}
let _itemRegistry = [];
function regItem(text) { _itemRegistry.push(text); return _itemRegistry.length - 1; }
window.act = function(idx, kind, days) {
  const text = _itemRegistry[idx]; if (!text) return;
  let state;
  if (kind === 'done')  state = { status:'done', at:Date.now() };
  if (kind === 'daily') state = { status:'daily-done', day:new Date().toDateString() };
  if (kind === 'defer') state = { status:'deferred', until:Date.now() + (days||7)*86400000 };
  if (kind === 'undo')  state = null;
  setAct(text, state);
  buildToday();
};
window.showAllResolved = function() {
  const keys = [];
  for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); if (k && k.startsWith('a:')) keys.push(k); }
  keys.forEach(k => localStorage.removeItem(k));
  buildToday();
};

function actItem(text, hint, opts) {
  opts = opts || {};
  const idx = regItem(text);
  if (isHiddenItem(text)) return '';
  const buttons = (opts.buttons || []).map(b => {
    if (b.href) return `<a class="btn ${b.kind||''}" href="${b.href}">${escapeHtml(b.label)}</a>`;
    return `<button class="${b.kind||''}" onclick="act(${idx},'${b.action}'${b.days?','+b.days:''})">${escapeHtml(b.label)}</button>`;
  }).join('');
  return `<div class="act-item">
    <div class="a-text">${opts.formatted || inlineFormat(text)}</div>
    ${hint ? `<div class="a-hint">${escapeHtml(hint)}</div>` : ''}
    ${buttons ? `<div class="a-actions">${buttons}</div>` : ''}
  </div>`;
}
function countHidden(items) { return items.filter(t => isHiddenItem(t)).length; }
function showResolvedLine(visible, total) {
  if (visible >= total) return '';
  const hidden = total - visible;
  return `<div class="show-resolved">${hidden} hidden (done / snoozed) · <a onclick="showAllResolved()">show all</a></div>`;
}

function buildToday() {
  _itemRegistry = [];
  const now = new Date();
  const dStr = now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
  document.getElementById('hero-eyebrow').textContent = `Today · ${dStr}`;

  const framePara = (NOW_PANELS.frame || '').split(/\n\s*\n/)[0].trim();
  document.getElementById('hero-lead').innerHTML = inlineFormat(framePara || 'No NOW.Frame section found.');

  document.getElementById('frame-card').innerHTML = `
    <div class="card-label">Where Alex is right now</div>
    <h2>Frame</h2>
    ${renderMarkdown(NOW_PANELS.frame || '')}
    <div class="show-resolved" style="border-top:none;padding-top:6px;">
      <a onclick="openDrawer('NOW')">open the full NOW node →</a>
    </div>
  `;

  const weekItems = NOW_PANELS.week || [];
  const weekHtml = weekItems.map(it => actItem(it,
    'Pick a slot, mark done after. Reset at midnight.',
    { buttons: [
        { label: '✓ Did today', action: 'daily', kind: 'primary' },
        { label: '⏱ Skip today', action: 'defer', days: 1 },
    ]})).join('');
  document.getElementById('week-card').innerHTML = `
    <div class="card-label">This week — pick a slot to commit</div>
    ${weekHtml || '<div class="card-empty">All this-week items handled today.</div>'}
    ${showResolvedLine(weekItems.length - countHidden(weekItems), weekItems.length)}
  `;

  const threadsHtml = THREADS.map(t => {
    const formatted = `<strong>${escapeHtml(t.title)}</strong><div style="margin-top:6px;font-size:14.5px;color:var(--text-2);font-family:var(--serif);line-height:1.65;">${inlineFormat(t.body || '')}</div>`;
    return actItem(t.title, 'Take one step today, or close it, or defer.', {
      formatted: formatted,
      buttons: [
        { label: '✓ Acted today', action: 'daily', kind: 'primary' },
        { label: '✓ Closed', action: 'done' },
        { label: '⏱ 7d', action: 'defer', days: 7 },
      ]
    });
  }).join('');
  document.getElementById('threads-card').innerHTML = `
    <div class="card-label">Open threads — pick one to advance</div>
    ${threadsHtml || '<div class="card-empty">All open threads handled today.</div>'}
    ${showResolvedLine(THREADS.length - countHidden(THREADS.map(t => t.title)), THREADS.length)}
  `;

  const eyesSlot = document.getElementById('eyes-slot');
  if (EYES.length) {
    const eyesHtml = EYES.map(e => {
      const formatted = `<strong>${escapeHtml(e.title)}</strong><div style="margin-top:6px;font-size:14.5px;color:var(--text-2);font-family:var(--serif);line-height:1.65;">${inlineFormat(e.body || '')}</div>`;
      return actItem(e.title, 'Pick a call: done means resolved on the underlying file; snooze hides for a week.', {
        formatted: formatted,
        buttons: [
          { label: '✓ Done', action: 'done', kind: 'primary' },
          { label: '⏱ 7d', action: 'defer', days: 7 },
        ]
      });
    }).join('');
    eyesSlot.innerHTML = `
      <div class="card canary">
        <div class="card-label">Needs eyes — make a call</div>
        ${eyesHtml || '<div class="card-empty">All needs-eyes items handled.</div>'}
        ${showResolvedLine(EYES.length - countHidden(EYES.map(e => e.title)), EYES.length)}
      </div>`;
  } else {
    eyesSlot.innerHTML = '';
  }

  const canaryItems = NOW_PANELS.canaries || [];
  const canarySlot = document.getElementById('canaries-slot');
  if (canaryItems.length) {
    const canaryHtml = canaryItems.map(it => actItem(it,
      'If true, pause and look. Mark seen if not active.',
      { buttons: [
          { label: '✓ Seen / not active', action: 'done', kind: 'primary' },
          { label: '⏱ Check in 7d', action: 'defer', days: 7 },
      ]})).join('');
    canarySlot.innerHTML = `
      <div class="card canary">
        <div class="card-label">Canaries — watch</div>
        ${canaryHtml || '<div class="card-empty">All canaries handled today.</div>'}
        ${showResolvedLine(canaryItems.length - countHidden(canaryItems), canaryItems.length)}
      </div>`;
  } else {
    canarySlot.innerHTML = '';
  }

  const recent = GRAPH.nodes.filter(n => n.id !== 'NOW').slice(-7).reverse();
  document.getElementById('recent-card').innerHTML = `
    <div class="card-label">Recently in the graph · click to open</div>
    <div class="recent">
      ${recent.map(n => `<div class="ritem">
        <span class="rid" onclick="openDrawer('${n.id}')">${escapeHtml(n.id)}</span>${escapeHtml(n.name)}${n.tentative ? '<span class="rtag">tentative</span>' : ''}
      </div>`).join('')}
    </div>
  `;
}

function setCardFilter(card) {
  document.querySelectorAll('#card-filter button').forEach(b => b.classList.toggle('active', b.dataset.card === card));
  const grid = document.getElementById('cards-grid');
  if (card === 'all') {
    grid.classList.remove('filtered');
    grid.querySelectorAll('[data-card]').forEach(el => el.classList.remove('focus-card'));
  } else {
    grid.classList.add('filtered');
    grid.querySelectorAll('[data-card]').forEach(el => el.classList.toggle('focus-card', el.dataset.card === card));
  }
  try { localStorage.setItem('today-filter', card); } catch(e) {}
}
document.querySelectorAll('#card-filter button').forEach(btn => {
  btn.addEventListener('click', () => setCardFilter(btn.dataset.card));
});

// === Mandala — vanilla SVG ===
let mandalaInited = false;
let mandalaSvg = null;
let viewBox = { x: -900, y: -900, w: 1800, h: 1800 };
const hiddenTypes = new Set();

function initMandala() {
  if (mandalaInited) return;
  mandalaInited = true;
  const wrap = document.getElementById('network');
  const declutter = document.getElementById('declutter').checked;
  const visible = GRAPH.nodes.filter(n => n.type !== 'now' && !(declutter && n.type === 'reference' && (n.backlink_count || 0) < 2));
  const visibleSet = new Set(visible.map(n => n.id));
  const edges = GRAPH.edges.filter(e => visibleSet.has(e.from) && visibleSet.has(e.to));

  let svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-900 -900 1800 1800" preserveAspectRatio="xMidYMid meet">';
  svg += '<g id="mandala-g">';
  for (const e of edges) {
    const a = GRAPH.nodes.find(x => x.id === e.from);
    const b = GRAPH.nodes.find(x => x.id === e.to);
    if (!a || !b || a.x === undefined || b.x === undefined) continue;
    svg += `<line class="edge" x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}"></line>`;
  }
  for (const n of visible) {
    if (n.x === undefined) continue;
    const cls = `node ${n.type}${n.tentative ? ' tentative' : ''}${n.id === 'NOW' ? ' now' : ''}`;
    const color = TYPE_COLOR[n.type] || '#888';
    const slug = n.id.split('-').slice(1).join('-') || n.id;
    svg += `<g class="${cls}" data-id="${escapeHtml(n.id)}" transform="translate(${n.x},${n.y})">`;
    svg += `<title>${escapeHtml(n.name)} (${escapeHtml(n.id)})</title>`;
    svg += `<circle r="10" fill="${color}" stroke="#fff" stroke-width="1"></circle>`;
    svg += `<text dy="22" text-anchor="middle">${escapeHtml(slug.length > 18 ? slug.slice(0,18)+'…' : slug)}</text>`;
    svg += `</g>`;
  }
  svg += '</g></svg>';
  wrap.innerHTML = svg;
  mandalaSvg = wrap.querySelector('svg');

  wrap.querySelectorAll('.node').forEach(node => {
    node.addEventListener('click', e => { e.stopPropagation(); openDrawer(node.dataset.id); });
  });

  let panning = false; let panStart = null; let vbStart = null;
  wrap.addEventListener('mousedown', e => {
    if (e.target.closest('.node')) return;
    panning = true; panStart = { x: e.clientX, y: e.clientY }; vbStart = { ...viewBox };
  });
  window.addEventListener('mousemove', e => {
    if (!panning) return;
    const rect = wrap.getBoundingClientRect();
    const dx = (e.clientX - panStart.x) * (viewBox.w / rect.width);
    const dy = (e.clientY - panStart.y) * (viewBox.h / rect.height);
    viewBox.x = vbStart.x - dx;
    viewBox.y = vbStart.y - dy;
    applyViewBox();
  });
  window.addEventListener('mouseup', () => { panning = false; });
  wrap.addEventListener('wheel', e => { e.preventDefault(); zoomBy(e.deltaY < 0 ? 1.1 : 0.9); }, { passive: false });

  document.getElementById('fractal-stats').textContent = `${visible.length} of ${GRAPH.nodes.length} nodes · ${edges.length} edges`;
  fitMandala();
}
function applyViewBox() {
  if (!mandalaSvg) return;
  mandalaSvg.setAttribute('viewBox', `${viewBox.x} ${viewBox.y} ${viewBox.w} ${viewBox.h}`);
}
window.zoomBy = function(f) {
  const cx = viewBox.x + viewBox.w / 2;
  const cy = viewBox.y + viewBox.h / 2;
  viewBox.w /= f;
  viewBox.h /= f;
  viewBox.x = cx - viewBox.w / 2;
  viewBox.y = cy - viewBox.h / 2;
  applyViewBox();
};
window.fitMandala = function() {
  viewBox = { x: -900, y: -900, w: 1800, h: 1800 };
  applyViewBox();
};
document.getElementById('declutter').addEventListener('change', () => {
  mandalaInited = false;
  document.getElementById('network').innerHTML = '';
  initMandala();
});
document.getElementById('search').addEventListener('input', e => {
  if (!mandalaInited) return;
  const q = e.target.value.trim().toLowerCase();
  document.querySelectorAll('#network .node').forEach(node => {
    const id = node.dataset.id.toLowerCase();
    const matches = !q || id.includes(q);
    node.classList.toggle('dim', !matches);
  });
});
document.querySelectorAll('#fractal-controls .legend-item').forEach(item => {
  item.addEventListener('click', () => {
    const t = item.dataset.type;
    if (hiddenTypes.has(t)) { hiddenTypes.delete(t); item.classList.remove('dim'); }
    else { hiddenTypes.add(t); item.classList.add('dim'); }
    if (!mandalaInited) return;
    document.querySelectorAll('#network .node').forEach(node => {
      const id = node.dataset.id;
      const n = GRAPH.nodes.find(x => x.id === id);
      if (!n) return;
      node.classList.toggle('dim', hiddenTypes.has(n.type));
    });
  });
});

// === Drawer ===
const DRAWER_HISTORY = [];
function openDrawer(id, opts) {
  opts = opts || {};
  const n = GRAPH.nodes.find(x => x.id === id) || GRAPH.nodes.find(x => x.id.startsWith(id + '-'));
  if (!n) return;
  const cur = document.getElementById('drawer').dataset.cur;
  if (cur && cur !== n.id && !opts.noPush) DRAWER_HISTORY.push(cur);
  document.getElementById('drawer').dataset.cur = n.id;

  document.getElementById('drawer-type').innerHTML =
    (n.tentative ? '<span class="tent">tentative</span>' : '') + escapeHtml(TYPE_LABEL[n.type] || n.type);
  document.getElementById('drawer-title').textContent = n.name;
  document.getElementById('drawer-meta').textContent = n.id + (n.horizon ? ' · horizon ' + n.horizon : '');

  let html = renderMarkdown(n.statement);
  if (n.caveats && n.caveats.trim()) {
    html += '<div class="caveats"><div class="clab">Caveats</div>' + renderMarkdown(n.caveats) + '</div>';
  }

  if (n.attribution || n.evidence || n.derivation) {
    const att = n.attribution || {};
    const ev = n.evidence || {};
    const dv = n.derivation || {};
    let provHtml = '<div class="provenance"><div class="plab">Provenance</div>';
    if (att.source) provHtml += `<div><strong>Attribution:</strong> ${escapeHtml(att.source)}${att.date ? ' · ' + escapeHtml(att.date) : ''}</div>`;
    if (ev.type) provHtml += `<div><strong>Evidence:</strong> ${escapeHtml(ev.type)}${ev.description ? ' — ' + escapeHtml(ev.description) : ''}</div>`;
    if (dv.method) provHtml += `<div><strong>Derivation:</strong> ${escapeHtml(dv.method)}</div>`;
    provHtml += '</div>';
    html += provHtml;
  }

  const groups = [
    { label: 'Related to (bidirectional)', items: n.related_to || [] },
    { label: 'Derives from (parents)', items: n.derives_from || [] },
    { label: 'Evidence references', items: n.evidence_refs || [] },
  ].filter(g => g.items && g.items.length);
  if (groups.length) {
    html += '<div class="related">';
    groups.forEach(g => {
      html += '<div class="relgroup"><div class="rlab">' + escapeHtml(g.label) + '</div>';
      g.items.forEach(item => {
        const t = resolveRef(item);
        if (t) {
          html += `<div class="relnode" onclick="openDrawer('${t.id}')">
            <div class="rhead"><span class="rid">${escapeHtml(t.id)}</span><span class="rname">${escapeHtml(t.name||'')}</span></div>
            <div class="rsum">${escapeHtml(summaryOf(t))}</div></div>`;
        } else {
          html += `<div class="relnode" style="cursor:default;border-style:dashed;background:transparent;"><div class="rsum" style="margin-top:0;">${escapeHtml(item)}</div></div>`;
        }
      });
      html += '</div>';
    });
    html += '</div>';
  }

  const mentioned = mentionedBy(n.id);
  if (mentioned.length) {
    html += '<div class="mentioned"><div class="rlab">Mentioned by — ' + mentioned.length + '</div>';
    html += mentioned.map(m => `<span class="ref" onclick="openDrawer('${m.id}')" title="${escapeHtml(m.name||'')}">${escapeHtml(m.id)}</span>`).join('');
    html += '</div>';
  }

  document.getElementById('drawer-stmt').innerHTML = html;
  document.getElementById('drawer-back').style.display = DRAWER_HISTORY.length ? 'inline-block' : 'none';
  document.getElementById('drawer').classList.add('open');
  document.getElementById('drawer-overlay').classList.add('open');
  document.querySelector('#drawer .dbody').scrollTop = 0;
}
function drawerBack() {
  if (!DRAWER_HISTORY.length) return;
  const id = DRAWER_HISTORY.pop();
  openDrawer(id, { noPush: true });
}
function closeDrawer() {
  document.getElementById('drawer').classList.remove('open');
  document.getElementById('drawer-overlay').classList.remove('open');
  document.getElementById('drawer').dataset.cur = '';
  DRAWER_HISTORY.length = 0;
}
function mentionedBy(targetId) {
  const shortM = targetId.match(/^[A-Z]+\d+/);
  const needles = new Set([targetId]);
  if (shortM) needles.add(shortM[0]);
  const hits = [];
  for (const n of GRAPH.nodes) {
    if (n.id === targetId) continue;
    const hay = (n.statement || '') + ' ' + (n.name || '');
    for (const needle of needles) {
      const re = new RegExp('\\b' + needle + '\\b');
      if (re.test(hay)) { hits.push(n); break; }
    }
  }
  return hits.slice(0, 30);
}
document.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
  if (e.key === 'Escape') closeDrawer();
  else if (e.key === '/' && document.getElementById('tab-fractal').classList.contains('active')) {
    e.preventDefault(); document.getElementById('search').focus();
  }
  else if ((e.key === '+' || e.key === '=') && mandalaInited) zoomBy(1.25);
  else if ((e.key === '-' || e.key === '_') && mandalaInited) zoomBy(0.8);
  else if (e.key === '0' && mandalaInited) fitMandala();
});

// === Sources ===
const SOURCES = [
  { name: 'NOW node', click: () => openDrawer('NOW'), desc: 'Top-of-stack: frame, this week / month / quarter, standing rules, canaries.' },
  { name: 'README.md', file: 'README.md', desc: 'Project overview. Schema-as-taxonomy, how to use the scaffold.' },
  { name: 'SCHEMA.md', file: 'SCHEMA.md', desc: 'Formal spec — node types, edges, provenance triple. Non-negotiable invariant.' },
  { name: 'SAFETY.md', file: 'SAFETY.md', desc: 'Caveats. Read first.' },
  { name: 'SCHEMA_DEPRECIATION.md', file: 'SCHEMA_DEPRECIATION.md', desc: 'Why typed knowledge graphs decay, and what this scaffold does about it.' },
  { name: 'RELATED_FRAMEWORKS.md', file: 'RELATED_FRAMEWORKS.md', desc: 'What this borrows from PROV-O, Toulmin, Zettelkasten, PKG.' },
  { name: 'alex-actions.md', file: 'alex-actions.md', desc: 'Open threads cards source.' },
  { name: 'alex-needs-eyes.md', file: 'alex-needs-eyes.md', desc: 'Items needing review source.' },
  { name: 'alex-vocab.md', file: 'alex-vocab.md', desc: 'Glossary source.' },
  { name: 'example-graph-extended.yaml', file: 'example-graph-extended.yaml', desc: 'The graph itself — Alex, the worked example.' },
];
const sourceList = document.getElementById('source-list');
SOURCES.forEach(s => {
  const a = document.createElement('a');
  a.className = 'source-item';
  if (s.click) { a.href = '#'; a.onclick = (e) => { e.preventDefault(); s.click(); }; }
  else { a.href = s.file; a.target = '_blank'; }
  a.innerHTML = `<div class="stitle">${escapeHtml(s.name)}</div><div class="sdesc">${escapeHtml(s.desc)}</div>`;
  sourceList.appendChild(a);
});

// === Vocab ===
const vlist = document.getElementById('vocab-list');
document.getElementById('vocab-count').textContent = `${VOCAB.length} terms in the working vocabulary.`;
VOCAB.forEach(v => {
  const row = document.createElement('div');
  row.className = 'vocab-row';
  row.innerHTML = `<div class="vterm">${escapeHtml(v.term)}</div><div class="vdef">${escapeHtml(v.def)}</div>`;
  vlist.appendChild(row);
});

// === Boot ===
buildToday();
try {
  const savedFilter = localStorage.getItem('today-filter');
  if (savedFilter && document.querySelector(`#card-filter button[data-card="${savedFilter}"]`)) {
    setCardFilter(savedFilter);
  }
} catch(e) {}
const initialTab = (location.hash || '').replace('#', '');
if (['fractal','sources','vocab'].includes(initialTab)) switchTab(initialTab);
</script>
</body>
</html>
"""


# ──────────────────────────────────────────────────────────────────────────
#  Main
# ──────────────────────────────────────────────────────────────────────────

def main():
    if not YAML_PATH.exists():
        sys.exit(f"ERROR: graph file not found: {YAML_PATH}")

    graph = parse_graph(YAML_PATH)
    vocab = parse_vocab(VOCAB_PATH)
    threads = parse_action_cards(ACTIONS_PATH)
    eyes = parse_action_cards(EYES_PATH)
    now_panels = extract_now_panels(graph)

    html = (
        HTML_TEMPLATE
        .replace("__DATA__",       json.dumps(graph, ensure_ascii=False))
        .replace("__VOCAB__",      json.dumps(vocab, ensure_ascii=False))
        .replace("__THREADS__",    json.dumps(threads, ensure_ascii=False))
        .replace("__EYES__",       json.dumps(eyes, ensure_ascii=False))
        .replace("__NOW_PANELS__", json.dumps(now_panels, ensure_ascii=False))
        .replace("__TYPE_COLOR__", json.dumps(TYPE_COLOR))
        .replace("__TYPE_LABEL__", json.dumps(TYPE_LABEL))
    )
    OUT_PATH.write_text(html)
    print(f"Wrote {OUT_PATH}")
    print(f"  nodes: {len(graph['nodes'])}  edges: {len(graph['edges'])}")
    print(f"  vocab: {len(vocab)}  threads: {len(threads)}  eyes: {len(eyes)}")
    print(f"  now-panels: frame={len(now_panels['frame'])}c · week={len(now_panels['week'])} bullets · canaries={len(now_panels['canaries'])} bullets")


if __name__ == "__main__":
    main()
