# Memory graph scaffold

A portable method for turning Claude's memory of you into a structured graph —
one that separates observations from interpretations, flags which claims are
load-bearing, and surfaces insights that only appear at the intersection of
multiple patterns.

Built on [Patrick McCarthy's open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph)
schema, adapted for personal memory rather than scientific claims.

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
4. Claude will walk you through the construction. Expect it to take 20–45 minutes
   of back-and-forth. Push back on anything that doesn't fit.
5. When Claude produces your YAML graph, save it. Use `render.py` to generate
   a visual, or `printable.py` for a printable PDF.
6. Come back to the graph when new events happen. The graph should
   grow — cautiously, with new evidence explicitly tied to existing nodes.

---

## What's in this directory

| File | Purpose |
|---|---|
| `README.md` | This file |
| `SAFETY.md` | Important caveats — read first |
| `START_HERE.md` | The prompt to paste into Claude |
| `SCHEMA.md` | Formal specification of node types and edges |
| `RELATED_FRAMEWORKS.md` | Survey of adjacent schemas (PROV-O, Toulmin, Zettelkasten, epistemic status, PKG) and what this scaffold borrows from each |
| `example-graph.yaml` | A small fictional example showing the schema |
| `render.py` | Generate a graphviz diagram from your YAML |
| `printable.py` | Generate a multi-page printable PDF |

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
