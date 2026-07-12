# know-thyself

A typed, provenance-tagged personal-knowledge-graph schema. Ten typed shapes plus a center node, eight typed edge relations, four-scale confidence, `valid_at` temporal validity. Plain YAML — every claim carries who derived it, from what evidence, when. The model writes the record on its own; the one thing it may not save is a `practice` — a rule you live by waits for your explicit yes. Built so an LLM can pick up your context in one paste, and so confidence stacks honestly: repetition is not evidence.

[See a graph in motion](https://parrik.com/alex-case-study.html#tab-spine) — 87 nodes of a fictional life, opened to the spine view. If a graph that shape would be useful for you, this scaffold is for you.

This repo is the schema. [know-thyself-search](https://github.com/parrik/know-thyself-search) ships the dashboard, renderers, retrieval, and MCP server.

## quick start

Paste `docs/START_HERE.md` into a Claude conversation that's accumulated some memory. Follow the seven phases. Save the YAML it produces. The graph is now portable: paste it at the start of any future conversation, with any model, to bootstrap context.

```bash
$ cat docs/START_HERE.md  # then paste into a Claude chat
```

The model doesn't remember — the graph does. Claude Code: `/know-thyself` slash command does the same thing.

## what's in here

```
docs/
├── SAFETY.md              read first (5 min)
├── START_HERE.md          the prompt
├── SCHEMA.md              formal spec — node types, edges, validation
├── RELATED_FRAMEWORKS.md  PROV-O, Toulmin, Zettelkasten, epistemic-status, PKG
└── DEPRECATION.md         why typed graphs decay
examples/
└── example-graph.yaml             26-node fictional example — every node and evidence type in use
skill.md                            Claude Code slash-command definition
```

For tooling — dashboard, renderers, retrieval, MCP server — see [know-thyself-search](https://github.com/parrik/know-thyself-search).

## what's different

Four schema-level moves no other personal-memory project ships together:

1. **The practice gate.** The model writes the record — observations, patterns, guesses — autonomously. A `practice`, a rule you live by, is the one node type that waits for your explicit yes. Wrong nodes are cheap to fix; wrong rules get acted on. See *The write gate* in `docs/SCHEMA.md`.
2. **Repetition is not evidence.** Confidence promotion requires *independent* derivations — different episodes, different evidence types. Not repetition from the same source.
3. **Observation kept separate from interpretation.** Episodes don't collapse into the patterns derived from them. The first three months mean one thing in November and another in May; both readings live as distinct nodes.
4. **`valid_at` decays unless re-grounded.** Personal claims aren't permanently true. New episodes refresh; absence doesn't.

None ship the four primitives together. Anthropic Memory synthesizes a prose profile every 24 hours — no typed observation/interpretation, no independence check, no decay. Mem0 attaches metadata but doesn't track independence. Cognee has source lineage but doesn't check independence. Letta has agentic memory blocks without temporal-validity decay. Graphiti has stronger validity windows but contradiction-driven invalidation, not decay-without-regrounding. [Aura SDK](https://github.com/teolex2020/AuraSDK) is the closest cousin (autonomous-adaptive vs hand-curated here). Anthropic users have asked for this primitive ([claude-code#30039](https://github.com/anthropics/claude-code/issues/30039)); Anthropic punted to the application layer. This is that layer.

## ack

W3C [RDF](https://www.w3.org/TR/rdf11-concepts/) and [PROV-O](https://www.w3.org/TR/prov-overview/); Patrick McCarthy's [open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph); Miller (1956) and Cowan (2001) on working memory; [Aura SDK](https://github.com/teolex2020/AuraSDK) (closest schema cousin). Adjacent prior art surveyed in `docs/RELATED_FRAMEWORKS.md` and the [companion essay](https://parrik.com/essays/know-thyself/).

## license

MIT.
