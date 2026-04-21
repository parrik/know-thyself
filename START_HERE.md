# START HERE — paste the rest of this file into a Claude conversation

---

I would like you to help me build a knowledge graph of what you remember
about me, using a method adapted from Patrick McCarthy's open-knowledge-graph
schema ([github.com/patdmc/open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph), MIT).
The goal is to separate observations from interpretations, flag tentative
claims explicitly, and surface insights that only appear at intersections.

Before you start, read these instructions carefully and follow them closely.

## The invariant

Every node and every edge in the graph must carry a provenance triple:
*(attribution, evidence, derivation)*. A claim without provenance is
indistinguishable from noise.

## The core rule

**Attribution ≠ confidence.** If I've restated a claim five times across
conversations, that's one derivation repeated, not five independent
confirmations. Real confidence comes only from multiple **independent**
derivations — different episodes, different contexts, different evidence
types.

## Node types

Use these eight types, with the shown confidence bases:

| Type | Meaning | Confidence basis |
|---|---|---|
| `reference` | Biographical fact | Single-source but verifiable |
| `observation` | A specific episode I witnessed or lived | Direct event |
| `overlap` | Pattern confirmed by 2+ independent episodes | Multiple groundings |
| `novel` | Single-derivation interpretation | **Tentative — must flag** |
| `emergent` | Produced only by intersection of 2+ existing nodes | Most valuable, most speculative |
| `equivalency` | Bridge to an external theoretical framework | External grounding |
| `open` | Unresolved question preserved as a first-class node | N/A |
| `practice` | Normative operating rule derived from descriptive claims | Must `derive_from` at least one overlap/novel/observation |

Novel nodes MUST carry `tentative: true` and explicit `caveats:` field
listing how the claim could be wrong. Open questions stay open until
independently resolved — do not let them collapse into novel interpretations.

## Edge relations

Use: `derives_from`, `grounds`, `grounded_in`, `generalizes`, `instantiates`,
`qualifies`, `contradicts`, `emergent_from`. Every edge carries its own
provenance triple.

## Evidence types

Use: `self-report` (I said it), `external-record` (document, data, third-party
source), `pattern-across-cases` (repeated instances), `natural-experiment`
(same variable, different context, different outcome — very strong),
`derived-inference` (you inferred it; weakest, must be flagged).

## HANDLING directives

For sensitive content (past harm, trauma, substance use, relationship
difficulty) that is structurally load-bearing but should not be casually
surfaced, include an inline directive in the node's statement field, e.g.
`HANDLING: do not raise unprompted`. Ask me before assuming a directive is
needed. When in doubt, flag — removal is easier than unsaying.

---

## How to proceed

Work through this in phases. Don't jump ahead; each phase uses the output
of the previous.

**Phase 1: Inventory the references and observations.** Look through what
you remember about me. Pull out the biographical facts (`reference` nodes)
and the specific episodes (`observation` nodes). Do not interpret yet. Show
me the list and let me correct it, add to it, or remove things. Ask which
observations need `HANDLING:` directives.

**Phase 2: Identify the patterns.** With the observations cleaned up, which
patterns are grounded by two or more **independent** episodes? Those become
`overlap` nodes. Be strict: two restatements of the same claim don't count
as two groundings. Show me the patterns and their evidence. I'll push back
on any where you're counting a single episode twice.

**Phase 3: Name the novel interpretations — tentatively.** Which
interpretations rest on a single derivation? Those are `novel`, with
`tentative: true` and a `caveats:` field. Do not promote them to overlap
without new evidence. Include any interpretation that I have repeated often
but that actually rests on one episode — these feel settled but aren't.

**Phase 4: Find the emergent nodes.** Which claims are not present in any
single observation but precipitate only when 2+ nodes are held together?
Those are `emergent`, with explicit `derivation.from` listing both parents.
If one parent alone could produce the claim, it's not emergent. Be precise.

**Phase 5: Mark the open questions.** What have I wondered about without
resolution? Make each an `open` node with its own derivation. Resist the
urge to fold these into novel interpretations.

**Phase 6: Add equivalency bridges if relevant.** If some of my behavior
or thinking instantiates a formal framework I already work within (a
theoretical framework from my field, a philosophical tradition I engage
with), add those as `equivalency` nodes. These are optional and usually
only apply if I have a strong intellectual framework I'm embedded in.

**Phase 6.5: Name the practices, if any.** Have I adopted operating
rules derived from the patterns? ("No weed before 9pm" from a
feeling-tolerance overlap; "only companies whose products I use" from
an environment-responsive overlap; "deliberate named asking" from a
visibility pattern.) Each practice must `derive_from` a descriptive
node — a floating rule with no grounding is not a graph node, it's a
sibling-doc commitment. Skip this phase if none apply.

**Phase 7: Validate.** Produce the YAML. Check: every node has a provenance
triple, every edge has one too, every derivation's `from:` points to a
node that exists, every observation I flagged for handling carries its
directive. Compute in-degree per node and tell me which observations are
most load-bearing — those are the ones a correction would cascade from.

**Phase 8: Reflect.** Tell me what you learned in the construction. What
claims were you treating as settled that turn out to be tentative? What
emergent nodes did the intersection actually produce? What open questions
did you notice you had been quietly answering with novel interpretations?

---

## What to avoid

- **Do not diagnose.** No node should read "you have X" or "you are Y."
  Describe episodes, patterns, tentative frames.
- **Do not psychoanalyze past a derivation you can state.** If I ask for
  the derivation of a novel node and you cannot produce clean parents
  and a clean method, drop the node.
- **Do not let novel nodes propagate.** If a novel node is tentative, any
  emergent node derived from it is doubly tentative. Flag that.
- **Do not be encouraging or reassuring in the graph content.** The graph
  is descriptive. Warmth and care belong in your conversational response,
  not in the YAML.
- **Do not assume depth I haven't shown you.** If memory is thin, the
  graph should be thin. Resist filling gaps with plausible-sounding
  inferences.

---

## What to produce at the end

- A YAML file with the complete graph.
- A short summary telling me:
  - Load-bearing observations (top 5-10 by in-degree).
  - Fragile claims (all novel nodes, with their caveats).
  - Emergent nodes (what the intersection produced).
  - Open questions (what remains unresolved).
  - Anything you flagged for HANDLING and why.

When you're ready, begin with Phase 1.
