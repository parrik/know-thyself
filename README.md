# know-thyself

**A typed personal-knowledge-graph schema for LLM context, ~100-node scale, for anyone using an LLM as a long-running thinking partner.**

Ten typed node shapes plus a center node. Eight typed edge relations. Four-scale confidence. `valid_at` temporal validity. Hand-curated YAML — every claim carries who derived it, from what evidence, when. Built so an LLM can pick up your context in one paste, and so confidence stacks honestly: repetition is not evidence.

[See a graph in motion](https://parrik.com/alex-case-study.html#tab-spine) — 87 nodes of a fictional life, opened to the spine view. If a graph that shape would be useful for you, this scaffold is for you.

This repo is the schema. [know-thyself-search](https://github.com/parrik/know-thyself-search) ships the dashboard, renderers, retrieval, and MCP server.

## the schema in 5 nodes

A minimal example showing the spine: a biographical reference, an episode grounded in it, a pattern across independent episodes (`overlap`), a tentative single-source hypothesis (`novel`), and a higher-order claim that emerges from two parent nodes (`emergent`).

```yaml
- id: R04-move
  type: reference          # biographical fact, no derivation
  name: "Moved to a new city in August 2024 for a new job"
  said_by: "Alex, self-report"
  said_when: "2025"
  evidence_kind: self-report
  derives_from: []
  how_it_follows: "direct"

- id: O01-first-three-months
  type: observation        # a specific episode, grounded in a reference
  name: "First three months — isolation and overwhelm"
  said_by: "Alex, self-report"
  said_when: "2024-12"
  evidence_kind: self-report
  derives_from: [R04-move]
  how_it_follows: "direct"

- id: P01-routine-as-regulation
  type: overlap            # ≥2 independent evidence_refs — independence, not repetition
  name: "Physical routine is load-bearing for Alex's stability"
  said_by: "Pattern across episodes"
  evidence_kind: pattern-across-cases
  evidence_refs: [O01-first-three-months, O02-running-group, O04-daughter-grades-recovered]
  derives_from: [O01-first-three-months, O02-running-group, O04-daughter-grades-recovered]
  how_it_follows: "induction across independent instances"

- id: N01-isolation-is-early-warning
  type: novel              # single-source interpretation — tentative + caveats required
  name: "Isolation is an early warning signal, not a neutral state"
  tentative: true
  caveats: "One detailed episode only; isolation may be coincident rather than causal."
  said_by: "Surfaced in conversation May 2025"
  evidence_kind: derived-inference
  derives_from: [O01-first-three-months]
  how_it_follows: "inductive from one case; no counterfactual on record"

- id: E01-child-stability-depends-on-alex-stability
  type: emergent           # ≥2 parents — claim is the intersection, not in either alone
  name: "Child's stability in the new city depends on Alex's routine stability"
  said_by: "Surfaced May 2025"
  evidence_kind: derived-inference
  derives_from: [P01-routine-as-regulation, O04-daughter-grades-recovered]
  how_it_follows: "intersection of P01 and O04 — neither alone yields the claim"
```

The spine: `reference` grounds `observation`; `overlap` lifts when ≥2 independent observations point at the same pattern; `novel` is interpretation marked tentative when grounded in only one; `emergent` is what falls out of the intersection of two existing nodes. The 87-node case study at parrik.com is this same shape, larger. The full schema (all ten node types, edge relations, validation rules) lives in `docs/SCHEMA.md`.

## quick start

Paste `docs/START_HERE.md` into an LLM chat that's accumulated some memory of you. Follow the seven phases. Save the YAML it produces. The graph is now portable: paste it at the start of any future conversation, with any model, to bootstrap context.

```bash
$ cat docs/START_HERE.md  # then paste into your LLM chat
```

Tested on Claude (Sonnet, Opus); the prompt is model-agnostic and should work on ChatGPT, Gemini, or a local model with sufficient context length, though fidelity to the seven-phase structure varies. Claude Code users: the `/know-thyself` slash command does the same thing. The model doesn't remember — the graph does.

## what's in here

```
docs/
├── SAFETY.md              read first (5 min)
├── START_HERE.md          the prompt
├── SCHEMA.md              formal spec — node types, edges, validation
├── RELATED_FRAMEWORKS.md  PROV-O, Toulmin, Zettelkasten, epistemic-status, PKG
└── DEPRECATION.md         why typed graphs decay
examples/
├── example-graph.yaml             18-node minimal
└── example-graph-extended.yaml    96-node case study (periods, themes, source_kind)
skill.md                            Claude Code slash-command definition
```

For tooling — dashboard, renderers, retrieval, MCP server — see [know-thyself-search](https://github.com/parrik/know-thyself-search).

## what's different

Three schema-level moves no other personal-memory project ships together:

1. **Repetition is not evidence.** Confidence promotion requires *independent* derivations — different episodes, different evidence types. Not repetition from the same source.
2. **Observation kept separate from interpretation.** Episodes don't collapse into the patterns derived from them. The first three months mean one thing in November and another in May; both readings live as distinct nodes.
3. **`valid_at` decays unless re-grounded.** Personal claims aren't permanently true. New episodes refresh; absence doesn't.

None ship the three primitives together. Anthropic Memory synthesizes a prose profile every 24 hours — no typed observation/interpretation, no independence check, no decay. Mem0 attaches metadata but doesn't track independence. Cognee has source lineage but doesn't check independence. Letta has agentic memory blocks without temporal-validity decay. Graphiti has stronger validity windows but contradiction-driven invalidation, not decay-without-regrounding. [Aura SDK](https://github.com/teolex2020/AuraSDK) is the closest cousin (autonomous-adaptive vs hand-curated here). Anthropic users have asked for this primitive ([claude-code#30039](https://github.com/anthropics/claude-code/issues/30039)); Anthropic punted to the application layer. This is that layer.

## ack

W3C [RDF](https://www.w3.org/TR/rdf11-concepts/) and [PROV-O](https://www.w3.org/TR/prov-overview/); Patrick McCarthy's [open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph); Miller (1956) and Cowan (2001) on working memory; [Aura SDK](https://github.com/teolex2020/AuraSDK) (closest schema cousin). Adjacent prior art surveyed in `docs/RELATED_FRAMEWORKS.md` and the [companion essay](https://parrik.com/essays/know-thyself/).

## license

MIT.
