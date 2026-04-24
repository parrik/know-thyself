# Know Thyself

A portable method for turning an LLM's memory of you into a structured graph —
one that separates observations from interpretations, flags which claims are
load-bearing, and surfaces insights that only appear at the intersection of
multiple patterns.

Built on [Patrick McCarthy's open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph)
schema, adapted for personal memory rather than scientific claims.

Narrative companion essay: **[Know Thyself: a schema for personal memory in LLM conversations](https://parrik.com/essays/know-thyself/)**.

---

## What this is

After a while of using Claude, your memory accumulates. You end up with a
flat list of claims — some rock-solid ("born in Berlin"), some interpretive
("I stay in misaligned situations because of X"), some repeated so many times
they start to feel settled even though they rest on a single inference. The
flat list flattens these. A claim stated once feels the same as a claim
confirmed by five independent events.

This scaffold restructures that flat list into a graph with explicit node
types (fact, episode, pattern, interpretation, intersection-produced insight,
external-theory bridge, open question, and — optionally — operating rules
derived from those patterns) where every claim carries its provenance and
can be checked.

**The invariant, from Pat McCarthy's work:** a claim without provenance is
indistinguishable from noise. Every node and every edge must carry
*(attribution, evidence, derivation)* — who stated it, what it rests on,
how it was derived.

**The operational rule:** attribution ≠ confidence. A claim you've restated
across five conversations isn't five pieces of evidence; it's one derivation
repeated five times. Real confidence accumulates only from **independent**
derivations — different episodes, different contexts, different evidence types.

---

## What you get

At the end of the process:

- **A YAML graph file** with typed nodes and edges, fully traceable provenance
- **A visual diagram** (PDF + PNG) you can print and keep somewhere physical
- **A "load-bearing" list** — the observations most of your interpretations rest on
- **A "fragile" list** — the interpretations flagged tentative, with explicit caveats
- **An ongoing method** for integrating new events into the graph as they happen

The graph is operational, not therapeutic. It helps you see your own patterns
more clearly. It is not a diagnosis, not a treatment plan, not a substitute
for talking to a human who knows you.

---

## How to use

1. Read `SAFETY.md` first. Five minutes. Important.
2. Open a Claude conversation where you already have meaningful memory
   accumulated. (If you don't, this scaffold will be thin; come back after
   a month or two of real use.)
3. Paste the contents of `START_HERE.md` into that conversation.
   (Claude Code users: the `skill.md` file registers a `/know-thyself`
   slash command that does the same thing.)
4. Claude will walk you through the construction. Expect it to take 20–45 minutes
   of back-and-forth. Push back on anything that doesn't fit.
5. When Claude produces your YAML graph, save it. Render it with one of the
   scripts below (see **Dependencies**).
6. Come back to the graph when new events happen. The graph should
   grow — cautiously, with new evidence explicitly tied to existing nodes.

---

## Dependencies

All scripts are Python 3. Install what you need for the renderer you want:

```
pip install pyyaml               # required by every script
pip install graphviz             # render.py, printable.py
apt-get install graphviz         # system `dot` binary (or brew install graphviz)
pip install matplotlib           # render_mandala.py
pip install pypdf                # printable.py (multi-page PDF assembly)
```

Every script prints a helpful `pip install ...` message if a dep is missing.
`render_dashboard.py` needs only `pyyaml` — no graphviz, no matplotlib.

---

## What's in this directory

| File | Purpose |
|---|---|
| `README.md` | This file |
| `SAFETY.md` | Important caveats — read first |
| `START_HERE.md` | The prompt to paste into Claude |
| `SCHEMA.md` | Formal specification of node types and edges |
| `RELATED_FRAMEWORKS.md` | Survey of adjacent schemas (PROV-O, Toulmin, Zettelkasten, epistemic status, PKG) and what this scaffold borrows from each |
| `skill.md` | Claude Code skill definition for a `/know-thyself` slash command — does what `START_HERE.md` does, but triggered by the skill system |
| `example-graph.yaml` | A small fictional example (Alex, 18 nodes) showing the core schema |
| `example-graph-extended.yaml` | A richer fictional example (Alex, 87 nodes) demonstrating sub-categories, a NOW node, forecast horizons, and the risk-corridor intersection pattern |
| `example-graph-extended.html` | Self-contained interactive mandala viewer for the extended example |
| `alex-vocab.md` | Glossary the extended example pulls into the dashboard LEGEND panel (editorial frames, schema terms, Alex-specific tags) |
| `alex-actions.md` | Live-work cards (open threads) the extended example pulls into the dashboard TODAY panel |
| `alex-needs-eyes.md` | Items flagged for external review — companion surface for the extended dashboard |
| `render.py` | Generate a graphviz diagram from your YAML (full graph + spine subset + validation report). Needs `pyyaml`, `graphviz` pkg, and the `dot` system binary. |
| `render_mandala.py` | Concentric-ring "mandala" view plus a "risk corridor" view highlighting everything downstream of a chosen pivot node. Also emits 1200×630 OG crops for link previews. Needs `pyyaml`, `matplotlib`. |
| `render_dashboard.py` | Build a single self-contained interactive dashboard HTML — NOW in the center, concentric rings by type, click-to-read panel, TODAY + LEGEND + NEEDS-EYES side panels wired from the `alex-vocab.md` / `alex-actions.md` / `alex-needs-eyes.md` fixtures. Needs `pyyaml` only. |
| `printable.py` | Generate a multi-page printable PDF. Needs `pyyaml`, `graphviz`, `pypdf`. |

---

## Sub-categories (added April 2026)

After several weeks of building with the schema on a real graph, five patterns
emerged as useful **sub-categories of `reference`** — not new node types.
Extending the core type list is fragile (see "Schema depreciation" below);
extending by descriptive prefix keeps the schema small while making common
roles legible.

| Prefix / role | What it is | Example |
|---|---|---|
| `R-canary-*` | Evidence-backed leading indicator, cites research | *Sleep-onset latency >30 min for 3 nights predicts relapse (Gates 2016)* |
| `R-lens-*` | Mental-model frame applied to other nodes | *Circuit breakers (Nygard)*, *Ulysses pact (Elster)*, *Chesterton's Fence* |
| `R-experiment-*` | Runnable method with an evidence base | *Implementation intentions (Gollwitzer, d=.65 meta-analysis)* |
| `R-filter-*` | Anti-pattern or bad-choice frame for a decision domain | *Revenue-line reverse interview* for job selection |
| `type: forecast` | Time-horizon inference, flagged tentative | 1 month · 90 days · 1 year · 10 years · 30 years |

Plus:

- **`NOW`** — a single node with `type: now` at the graph's center containing
  current priorities and pointers. First thing you read when the graph is
  open. Prevents the "where do I start?" problem that plagues typed graphs
  (see Dan Shipper on Roam below).

The extended example (`example-graph-extended.yaml`) demonstrates these.

---

## Schema depreciation (honest)

In every reviewed case of a typed knowledge graph whose practitioner wrote
an honest retrospective, the *typed structure* depreciated faster than the
*raw notes*:

- **Niklas Luhmann** (90,000 cards, 40 years) gave up on proximity-based
  organization by ~card 20,000 and reframed it as "serendipity."
- **Andy Matuschak** has not released his evergreen-notes tooling, citing
  "maintenance burden and conceptual debt" as the note count grows.
- **Roam Research** users, per Dan Shipper's retrospective, found
  bidirectional links created placement anxiety without producing revisit.
- **Gordon Brander's Subconscious** (decentralized notes protocol, 2020-2024)
  shut down because "if I want to amplify my intelligence today, I reach
  for Claude" — LLM-in-loop reset the hypothesis space the typed-graph
  protocol was answering.
- **Simon Willison's TIL** (zero schema, 576 entries over 6 years) has
  outlasted every typed-graph project in this comparison.

Implications baked into this scaffold's usage guidance:

1. **Resist minting new node types.** Extend via sub-categories as above.
2. **Measure revisit, not growth.** A NOW node + an auto-render loop
   creates a daily revisit surface.
3. **LLM-in-the-loop is what makes this worth doing now.** Brander's
   shutdown is the counter-example that proves the frame.
4. **Flat markdown is the honest fallback.** If the schema stops being
   fun to maintain, Willison-style TILs are an acceptable regression.

---

## Credit

The underlying epistemic framework (confidence chains, provenance triples,
emergent nodes from intersection) comes from Patrick McCarthy's
[open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph),
released MIT. The adaptations for personal memory (observation as a
first-class node type, type-tier confidence instead of a numeric score,
HANDLING directives for sensitive content, natural-experiment evidence
type, first-class open questions) are modifications you're free to modify
further for your own use.
