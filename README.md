# Know Thyself

**Turn an LLM's memory of you into a structured graph that knows what it knows — and what it's just guessing.**

A flat memory list treats a claim repeated five times as five pieces of evidence. It isn't. This scaffold restructures that list into typed nodes — fact, episode, pattern, interpretation, open question — where every claim carries provenance *(attribution, evidence, derivation)* and confidence accumulates only from independent derivations.

> Companion essay: **[Know Thyself](https://parrik.com/essays/know-thyself/)** — the full argument lives there.

---

## Quickstart

1. Read `SAFETY.md` (5 minutes).
2. In a Claude conversation that has accumulated real memory, paste `START_HERE.md`. (Claude Code: a `/know-thyself` slash command does the same thing.)
3. Save the YAML Claude produces. Render it:

```bash
pip install pyyaml graphviz
python render_dashboard.py your-graph.yaml   # interactive HTML, NOW node centered
```

`render.py` builds a static graphviz diagram, `render_mandala.py` does concentric rings, `printable.py` builds a multi-page PDF. Each script tells you which `pip install` it needs.

---

## What's here

| File | Purpose |
|---|---|
| `START_HERE.md` | The prompt to paste into Claude |
| `SCHEMA.md` | Node types, edges, sub-categories, optional fields |
| `SAFETY.md` | Caveats — read first |
| `RELATED_FRAMEWORKS.md` | What this borrows from PROV-O, Toulmin, Zettelkasten, PKG |
| `SCHEMA_DEPRECIATION.md` | Why typed knowledge graphs decay, and what this scaffold does about it |
| `example-graph-extended.yaml` | 87-node fictional example demonstrating sub-categories, the NOW node, forecast horizons |
| `example-graph-extended.html` | Self-contained interactive viewer for the extended example |
| `skill.md` | Claude Code skill definition |

---

## What this scaffold extends

The provenance-triple shape is older — RDF and PROV-O ship it as W3C standards; Patrick McCarthy's [open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph) gives a contemporary articulation with formal necessity arguments for the **scientific** case. This work takes that shape and extends it structurally for **personal** memory:

1. **Observation as a first-class node type.** In a scientific graph, observations recede after grounding a proposition. In a personal graph they get *reinterpreted* — the first three months mean one thing in November and another in May. Keeping the episode separate stops interpretations collapsing back into the events that generated them.
2. **A `valid_at` axis.** Propositions about a person aren't permanently valid the way physical-law propositions are; every claim carries a validity window that decays unless re-grounded.
3. **Inverted edge-density prediction.** Mature scientific graphs become edge-dense. Personal graphs don't — new life events spawn new nodes, cross-time edges stay sparse. A mature personal graph is node-dense with sparse adjacency.

Smaller extensions: type-tier confidence (no replication, no external ground truth, so a numeric score is dishonest); HANDLING directives for sensitive content; natural-experiment evidence type for life events that function like A/B tests; open questions as first-class nodes.

---

## Credit

- W3C [RDF](https://www.w3.org/TR/rdf11-concepts/) (2004) and [PROV-O](https://www.w3.org/TR/prov-overview/) (2013) — the typed-triplet shape as web standards.
- George Miller (1956) and Nelson Cowan (2001) — working-memory bounds that motivate why a graph beats a flat list.
- [Patrick McCarthy's open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph) — formal necessity arguments for the scientific case. McCarthy's repo is unlicensed at time of writing; the schema as a structural taxonomy is treated here as uncopyrightable, and this repository's MIT license covers the specific implementation, prose, and renderers — not the underlying ideas.

Adjacent prior art (Anthropic's citations API, Park et al.'s *Generative Agents*, MCP Knowledge Graph Memory, Mem0, Graphiti, and others) is surveyed in the [companion essay](https://parrik.com/essays/know-thyself/).
