# Know Thyself

**Turn an LLM's memory of you into a structured graph that knows what it knows — and what it's just guessing.**

A flat memory list treats a claim repeated five times as five pieces of evidence. It isn't. This scaffold restructures that list into typed nodes — fact, episode, pattern, interpretation, open question — where every claim carries provenance *(attribution, evidence, derivation)* and confidence accumulates only from independent derivations.

> Companion essay: **[Know Thyself](https://parrik.com/essays/know-thyself/)** — the full argument lives there.

> **Claim:** Restructuring flat LLM memory into a provenance-typed graph yields honest confidence accumulation.
> **Grounds:** Stated thesis of the scaffold; elaborated in the companion essay.
> **Status:** stipulated
> **Leans on:** the schema and prompt below; SCHEMA.md for the typed-node spec.

---

## Quickstart — how to run the scaffold end-to-end

1. Read `SAFETY.md` (5 minutes).
2. In a Claude conversation that has accumulated real memory, paste `START_HERE.md`. (Claude Code: a `/know-thyself` slash command does the same thing.)
3. Save the YAML Claude produces. Render it:

```bash
pip install pyyaml graphviz
python render_dashboard.py your-graph.yaml   # interactive HTML, NOW node centered
```

`render.py` builds a static graphviz diagram, `render_mandala.py` does concentric rings, `printable.py` builds a multi-page PDF. Each script tells you which `pip install` it needs.

> **Claim:** Three steps (safety read → paste prompt → render) are sufficient to produce a usable graph.
> **Grounds:** Operational instructions; verified by the bundled renderers.
> **Status:** stipulated
> **Leans on:** START_HERE.md (the prompt), SCHEMA.md (the YAML shape), the render scripts in this repo.

---

## Retrieval — vectors and an MCP server

A graph YAML fits in a model's context at 200 nodes. At 2,000 it doesn't, and even when it does the model wastes attention scanning irrelevant parts. The retrieval layer turns the YAML into something an agent can actually query.

```bash
pip install pyyaml numpy
python embed.py example-graph-extended.yaml          # → graph-embeddings.json
python search.py "when did Mira's grades start improving"
python compare.py "when have I felt isolated"        # three ranking modes side-by-side
```

`embed.py` vectorizes each node's `statement` (TF-IDF default; OpenAI and `sentence-transformers/local` backends optional) and writes a JSON index. `search.py` accepts a query and returns top-k hits. `compare.py` shows the same query under pure cosine, type-filtered, and provenance-reranked modes — what each layer earns is the lesson.

`mcp_server.py` wraps retrieval as an [MCP](https://modelcontextprotocol.io) tool surface. **IDs-only by default**: `search_graph` and `walk_provenance` return id / type / name / score / tentative + structural edges, never statement text. `get_node` returns full statement and is **hidden** unless `KNOW_THYSELF_ALLOW_FULL_TEXT=1` is set in the server's environment. Once a graph contains personal content and a cloud-LLM client connects, statement text crossing the wire is the leak; the gate exists to keep that decision explicit, per graph.

```bash
pip install "mcp[cli]"
claude mcp add know-thyself -s user \
  -e KNOW_THYSELF_INDEX=/path/to/graph-embeddings.json \
  -e KNOW_THYSELF_GRAPH=/path/to/graph.yaml \
  -- python /path/to/mcp_server.py
```

Setting `KNOW_THYSELF_GRAPH` enables mtime-based auto-rebuild of the index whenever the source YAML is newer.

---

## What's here — the file inventory of this repo

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
| `embed.py` / `search.py` / `compare.py` | Vector retrieval CLIs over a graph YAML |
| `mcp_server.py` | MCP server exposing retrieval to Claude Code et al. |
| `render*.py`, `printable.py` | Static / interactive / PDF renderers |

> **Claim:** These files are the complete public surface of the scaffold.
> **Grounds:** Direct enumeration of the repo contents.
> **Status:** stipulated
> **Leans on:** every cross-reference elsewhere in the README and START_HERE.md.

---

## What I built — the structural extensions for personal memory

I built a personal-graph schema: typed nodes for a single life, four-scale confidence synthesis, temporal validity, MCP retrieval. The provenance-triple shape underneath is older — RDF and PROV-O ship it as W3C standards, and Patrick McCarthy's [open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph) gives a contemporary articulation with formal necessity arguments for the **scientific** case. The structural extensions for **personal** memory below are mine:

1. **Observation as a first-class node type.** In a scientific graph, observations recede after grounding a proposition. In a personal graph they get *reinterpreted* — the first three months mean one thing in November and another in May. Keeping the episode separate stops interpretations collapsing back into the events that generated them.
2. **A `valid_at` axis.** Propositions about a person aren't permanently valid the way physical-law propositions are; every claim carries a validity window that decays unless re-grounded.
3. **Inverted edge-density prediction.** Mature scientific graphs become edge-dense. Personal graphs don't — new life events spawn new nodes, cross-time edges stay sparse. A mature personal graph is node-dense with sparse adjacency.

Smaller extensions: type-tier confidence (no replication, no external ground truth, so a numeric score is dishonest); HANDLING directives for sensitive content; natural-experiment evidence type for life events that function like A/B tests; open questions as first-class nodes.

> **Claim:** The personal-graph schema is a deliberate set of structural extensions on top of an older provenance-triple shape.
> **Grounds:** Builder's account; cross-checked against PROV-O / RDF / open-knowledge-graph as the prior art.
> **Status:** stipulated
> **Leans on:** SCHEMA.md (formal spec of the extensions), the Credit section below.

---

## Credit — where the underlying ideas come from

- W3C [RDF](https://www.w3.org/TR/rdf11-concepts/) (2004) and [PROV-O](https://www.w3.org/TR/prov-overview/) (2013) — the typed-triplet shape as web standards.
- George Miller (1956) and Nelson Cowan (2001) — working-memory bounds that motivate why a graph beats a flat list.
- [Patrick McCarthy's open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph) — formal necessity arguments for the scientific case. McCarthy's repo is unlicensed at time of writing; the schema as a structural taxonomy is treated here as uncopyrightable, and this repository's MIT license covers the specific implementation, prose, and renderers — not the underlying ideas.

Adjacent prior art (Anthropic's citations API, Park et al.'s *Generative Agents*, MCP Knowledge Graph Memory, Mem0, Graphiti, and others) is surveyed in the [companion essay](https://parrik.com/essays/know-thyself/).

> **Claim:** The provenance-triple lineage is W3C-standardized; the personal-graph extensions are the new contribution here.
> **Grounds:** Cited W3C standards (RDF 2004, PROV-O 2013), Miller (1956), Cowan (2001), McCarthy's open-knowledge-graph repo.
> **Status:** established (for the cited prior art); stipulated (for the boundary between borrowed shape and new extensions)
> **Leans on:** RELATED_FRAMEWORKS.md for the broader survey; the companion essay for adjacent prior art.
