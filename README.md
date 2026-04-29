# Know Thyself

A scaffold for turning an LLM's accumulated memory of you into a structured graph — one that separates what happened from what you make of it, flags which claims are load-bearing, and surfaces patterns that only appear at the intersection of several others.

Companion essay: **[Know Thyself](https://parrik.com/essays/know-thyself/)**.

---

## What this is

After enough conversations with Claude, your memory accumulates. You end up with a flat list of claims — some rock-solid, some interpretive, some repeated so many times they start to feel settled even though they rest on a single inference. The flat list flattens these. A claim stated once feels the same as a claim confirmed by five independent events.

This scaffold restructures that flat list into a graph with explicit node types — fact, episode, pattern, interpretation, intersection-produced insight, external-theory bridge, open question, and optionally operating rules — where every claim carries its provenance and can be checked.

Two rules carry the design:

- **A claim without provenance is indistinguishable from noise.** Every node and edge records *(attribution, evidence, derivation)* — who said it, what it rests on, how it was derived.
- **Attribution is not confidence.** A claim restated five times is one derivation repeated five times, not five pieces of evidence. Confidence accumulates only from *independent* derivations.

The graph is operational, not therapeutic. It helps you see your own patterns more clearly. It is not a diagnosis, not a treatment plan, not a substitute for talking to a human who knows you.

---

## What you get

- **A YAML graph file** with typed nodes and edges and full provenance.
- **A visual diagram** (PDF + PNG) you can print and keep somewhere physical.
- **A load-bearing list** — the observations most of your interpretations rest on.
- **A fragile list** — the interpretations flagged tentative, with explicit caveats.
- **An ongoing method** for integrating new events into the graph as they happen.

---

## How to use

1. Read `SAFETY.md` first. Five minutes. Important.
2. Open a Claude conversation where you already have meaningful memory accumulated. (If you don't, this scaffold will be thin; come back after a month or two of real use.)
3. Paste the contents of `START_HERE.md` into that conversation. (Claude Code users: the `skill.md` file registers a `/know-thyself` slash command that does the same thing.)
4. Claude will walk you through the construction. Expect 20–45 minutes of back-and-forth. Push back on anything that doesn't fit.
5. When Claude produces your YAML graph, save it. Render it with one of the scripts below.
6. Come back to the graph when new events happen. The graph should grow cautiously, with new evidence explicitly tied to existing nodes.

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

Every script prints a helpful `pip install ...` message if a dep is missing. `render_dashboard.py` needs only `pyyaml` — no graphviz, no matplotlib.

---

## What's in this directory

| File | Purpose |
|---|---|
| `README.md` | This file |
| `SAFETY.md` | Important caveats — read first |
| `START_HERE.md` | The prompt to paste into Claude |
| `SCHEMA.md` | Formal specification of node types and edges |
| `RELATED_FRAMEWORKS.md` | Survey of adjacent schemas (PROV-O, Toulmin, Zettelkasten, epistemic status, PKG) and what this scaffold borrows from each |
| `skill.md` | Claude Code skill definition for a `/know-thyself` slash command |
| `example-graph.yaml` | A small fictional example (18 nodes) showing the core schema |
| `example-graph-extended.yaml` | A richer fictional example (87 nodes) demonstrating sub-categories, a NOW node, forecast horizons, and the risk-corridor intersection pattern |
| `example-graph-extended.html` | Self-contained interactive mandala viewer for the extended example |
| `alex-vocab.md` | Glossary the extended example pulls into the dashboard LEGEND panel |
| `alex-actions.md` | Live-work cards (open threads) the extended example pulls into the dashboard TODAY panel |
| `alex-needs-eyes.md` | Items flagged for external review |
| `render.py` | Generate a graphviz diagram from your YAML (full graph + spine subset + validation report) |
| `render_mandala.py` | Concentric-ring "mandala" view plus a "risk corridor" view highlighting everything downstream of a chosen pivot. Also emits 1200×630 OG crops |
| `render_dashboard.py` | Build a single self-contained interactive dashboard HTML — NOW in the center, concentric rings by type, click-to-read panel, TODAY + LEGEND + NEEDS-EYES side panels |
| `printable.py` | Generate a multi-page printable PDF |

---

## Sub-categories (added April 2026)

After several weeks of building with the schema on a real graph, five patterns emerged as useful **sub-categories of `reference`** — not new node types. Extending the core type list is fragile (see "Schema depreciation" below); extending by descriptive prefix keeps the schema small while making common roles legible.

| Prefix / role | What it is | Example |
|---|---|---|
| `R-canary-*` | Evidence-backed leading indicator, cites research | *Sleep-onset latency >30 min for 3 nights predicts relapse (Gates 2016)* |
| `R-lens-*` | Mental-model frame applied to other nodes | *Circuit breakers (Nygard)*, *Ulysses pact (Elster)*, *Chesterton's Fence* |
| `R-experiment-*` | Runnable method with an evidence base | *Implementation intentions (Gollwitzer, d=.65 meta-analysis)* |
| `R-filter-*` | Anti-pattern or bad-choice frame for a decision domain | *Revenue-line reverse interview* for job selection |
| `type: forecast` | Time-horizon inference, flagged tentative | 1 month · 90 days · 1 year · 10 years · 30 years |

Plus:

- **`NOW`** — a single node with `type: now` at the graph's center, containing current priorities and pointers. First thing you read when the graph is open. Prevents the "where do I start?" problem that plagues typed graphs.

The extended example (`example-graph-extended.yaml`) demonstrates these.

---

## Schema depreciation (honest)

In every reviewed case of a typed knowledge graph whose practitioner wrote an honest retrospective, the *typed structure* depreciated faster than the *raw notes*:

- **Niklas Luhmann** (90,000 cards, 40 years) gave up on proximity-based organization by ~card 20,000 and reframed it as "serendipity."
- **Andy Matuschak** has not released his evergreen-notes tooling, citing "maintenance burden and conceptual debt" as the note count grows.
- **Roam Research** users, per Dan Shipper's retrospective, found bidirectional links created placement anxiety without producing revisit.
- **Gordon Brander's Subconscious** (decentralized notes protocol, 2020-2024) shut down because "if I want to amplify my intelligence today, I reach for Claude" — LLM-in-loop reset the hypothesis space the typed-graph protocol was answering.
- **Simon Willison's TIL** (zero schema, 576 entries over 6 years) has outlasted every typed-graph project in this comparison.

Implications baked into this scaffold's usage guidance:

1. **Resist minting new node types.** Extend via sub-categories as above.
2. **Measure revisit, not growth.** A NOW node + an auto-render loop creates a daily revisit surface.
3. **LLM-in-the-loop is what makes this worth doing now.** Brander's shutdown is the counter-example that proves the frame.
4. **Flat markdown is the honest fallback.** If the schema stops being fun to maintain, Willison-style TILs are an acceptable regression.

---

## What this scaffold extends

The provenance-triple shape — every claim carrying *(attribution, evidence, derivation)* — has older roots. RDF and PROV-O ship it as W3C standards; Anthropic's Claude citations API ships it inside the product surface; Patrick McCarthy's open-knowledge-graph gives a contemporary articulation with formal necessity arguments for the scientific case. This scaffold takes that shape and extends it structurally for personal memory:

1. **Observation as a first-class node type.** In a scientific graph, observations recede after grounding a proposition. In a personal graph, observations get *reinterpreted* — the first three months mean one thing in November and another in May. Calling out the episode separately keeps interpretations from collapsing back into the events that generated them.

2. **A `valid_at` axis the existing frameworks don't supply.** Propositions about a person aren't permanently valid the way physical-law propositions are. Necessity arguments that run through selection-under-competition don't apply; the temporal logic has to come from epistemic humility instead — every claim about a person carries a validity window that decays unless re-grounded.

3. **An inverted edge-density prediction.** Mature scientific graphs become edge-dense over time; new findings keep slotting into existing structure. Personal graphs don't. New life events spawn new nodes — a person, a loss, a pattern — and cross-time edges stay sparse. A mature personal graph is node-dense with sparse adjacency, not edge-dense.

Smaller extensions: type-tier confidence (overlap > novel) instead of a numeric score, since there is no replication and no external ground truth; HANDLING directives for sensitive content; a natural-experiment evidence type for life events that function like A/B tests without being designed as such; open questions as first-class nodes; packaging as a Claude Code skill.

---

## Credit

- W3C [RDF](https://www.w3.org/TR/rdf11-concepts/) (2004) and [PROV-O](https://www.w3.org/TR/prov-overview/) (2013) — the typed-triplet shape as web standards.
- [Anthropic's Claude citations API](https://docs.anthropic.com/en/docs/build-with-claude/citations) — the same triplet inside a product surface.
- [Patrick McCarthy's open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph) — formal necessity arguments for the scientific case. McCarthy's repo is unlicensed at time of writing; the schema as a structural taxonomy is treated here as uncopyrightable, and the MIT license on this repository covers the specific implementation, prose, and renderers — not the underlying ideas.
- Park et al., *Generative Agents* (UIST 2023, [arXiv:2304.03442](https://arxiv.org/abs/2304.03442)) — separating *observation* from *reflection* in LLM memory, with reflections citing the observations they rest on.
- Andrej Karpathy's [LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (Apr 2026) — the cultural pattern for human-curated, LLM-maintained, version-controlled personal knowledge.
- Anthropic's [MCP Knowledge Graph Memory server](https://github.com/modelcontextprotocol/servers/tree/main/src/memory) — `Entity / Relation / Observation` as primitives; this scaffold reads as a typed-evidence extension.
- **Mem0** and **Graphiti** — production substrates for LLM memory. The schema here could ride on either; we've kept it standalone for portability.
