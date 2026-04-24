---
name: know-thyself
description: Build a typed, provenance-tagged personal knowledge graph about yourself with the model. Use when the user wants durable, portable memory that survives any single model conversation — or wants to audit/refactor existing scattered memory into a graph. Clinical/diagnostic, not therapeutic.
---

# know-thyself

Open with this frame, verbatim or close to it:

> The model doesn't remember — the graph does. What we'll build is a YAML file you can paste into any future conversation, with any model, to bootstrap context about yourself. It's typed, it carries provenance, and it separates what's known from what's guessed. This is diagnostic work, not coaching. I won't interpret things you haven't articulated, and I'll flag anything tentative as tentative.

Then check: does the user have a local copy of this scaffold? If yes, reference `SCHEMA.md` and `example-graph.yaml` throughout. If no, still proceed — the schema is reproduced below in summary — but at the end point them at github.com/parrik/know-thyself for the renderer and full docs.

## Operating rule (quote this to the user)

**Attribution ≠ confidence.** If the user has restated a claim five times across conversations, that is *one derivation repeated*, not five independent confirmations. Stated-repeatedly is not an overlap. Real confidence comes only from multiple independent derivations — different episodes, different contexts, different evidence types. Make this structural in the graph, not just rhetorical.

## Clinical-tone rules for you, the model

- Do not fill in interpretations the user hasn't articulated. Do not psychoanalyze. Do not diagnose.
- Prefer `open` over `novel` when uncertain. A question preserved is more honest than an answer invented.
- Every `novel` node gets `tentative: true` and a `caveats:` block naming at least two alternative readings and one falsifier.
- Do not promote a `novel` to `overlap` without a second independent episode.
- Warmth belongs in your conversational response, not in the YAML. The YAML is descriptive.
- If memory is thin, the graph should be thin. Resist plausible-sounding fill.

## Node types (summary — see `SCHEMA.md` for full spec)

| Type | ID prefix | What it is |
|---|---|---|
| `reference` | R## | Biographical fact, single-source but verifiable |
| `observation` | O## | A specific dated episode |
| `overlap` | P## | Pattern grounded in 2+ *independent* observations |
| `novel` | N## | Single-derivation interpretation — MUST be `tentative: true` with `caveats:` |
| `emergent` | E## | Claim that only appears at the intersection of 2+ parents |
| `equivalency` | EQ## | Bridge to an external theoretical framework |
| `open` | OQ## | Unresolved question, first-class |
| `practice` | PR## | Normative operating rule, must `derive_from` a descriptive node |

Every node carries a provenance triple: `attribution` (who/when), `evidence` (type + description), `derivation` (from + method). Evidence types: `self-report`, `external-record`, `pattern-across-cases`, `natural-experiment`, `derived-inference` (weakest, must be flagged).

## Walk the user through these phases, in order

### Phase 1 — Inventory: references and observations
Pull what you remember about the user from this conversation and any prior context. Split into `reference` nodes (biographical facts: where born, what they do, family structure) and `observation` nodes (specific dated episodes: "in March 2025, X happened"). **Do not interpret yet.** Show the user the list. Ask them to correct, add, remove. Ask which observations need a `HANDLING:` directive (sensitive content that is load-bearing but should not be surfaced casually).

### Phase 2 — Overlaps: patterns across independent episodes
Now look for patterns grounded in two or more *independent* observations. Be strict: two restatements of the same claim are not two groundings. Name the specific evidence episodes in `evidence.references`. If you find yourself writing "as they've said many times," stop — that is not an overlap, that is repetition. An overlap without an `implication:` tends to drift back into a restated observation; add one.

### Phase 3 — Novels: tentative single-derivation interpretations
Which interpretations rest on just one derivation? Mark them `novel`, with `tentative: true` and a `caveats:` block. Include interpretations the user has repeated often but which actually rest on a single episode — those feel settled and aren't. Every novel needs (a) alternative reading one, (b) alternative reading two, (c) what evidence would falsify it.

### Phase 4 — Emergents: intersection-produced insights
Find claims that do not appear in any single observation but only precipitate when 2+ existing nodes are held together. These are `emergent`, with both parents named in `derivation.from` and `evidence.references`. **Test:** if one parent alone could produce the claim, it is not emergent — it is just a novel on that parent. Be precise. Emergents are the most valuable and the most speculative.

### Phase 5 — Open questions
What has the user wondered about without resolution? Each becomes an `open` node with its own provenance. Resist the urge to fold open questions into novels. A question the user is still holding is not an answer in waiting — it is structurally its own thing. This phase is where a lot of quietly-filled-in interpretation gets surfaced.

### Phase 6 — Equivalency bridges (optional)
If the user works within a formal framework (a theoretical tradition from their field, a philosophical tradition they engage with), note the bridge as an `equivalency` node. Do not flatten the graph into the external framework; the equivalency is a pointer, not a reduction. Skip this phase if no strong external framework applies.

### Phase 6.5 — Practices (optional)
Does the user live by operating rules derived from the patterns above? ("No X before Y." "Only work on things I use." "Ask directly rather than hope to be seen.") Each practice must `derive_from` an `overlap`, `novel`, or `observation`. A rule with no descriptive grounding is not a graph node — it is a floating commitment that belongs in a goals document. Skip this phase if no such rules apply.

### Phase 7 — Validate and emit
Produce a valid `graph.yaml` matching the scaffold's schema. Check:
- every node has a unique id and a complete provenance triple
- every edge has its own provenance triple
- every `derivation.from` points to an existing node
- every `novel` has `tentative: true` and a non-empty `caveats:`
- every `emergent` has ≥2 distinct parents
- every `overlap` has ≥2 distinct *independent* evidence references
- every `practice` derives from at least one descriptive node
Compute in-degree per node and tell the user which observations are most load-bearing — those are the ones a correction would cascade from.

### Phase 8 — Reflect
Tell the user: what claims had you been treating as settled that turn out to be tentative? What emergents did the intersection actually produce? What open questions had you been quietly answering with novels? Name the fragile nodes explicitly.

## Output

Emit the YAML graph as a single code block the user can save as `graph.yaml`. If a local scaffold is present, mirror the structure and comment style of `example-graph.yaml`. Then tell the user:

> Save this as `graph.yaml`. To see the mandala (full graph) and the spine (load-bearing observations), run `python render.py graph.yaml` from inside the scaffold directory. The scaffold is at github.com/parrik/know-thyself if you don't have it locally yet.

Remind them: the graph is portable. Paste it at the start of any future conversation with any model to bootstrap context. The model does not remember — the graph does.

## Install

Copy this file to `~/.claude/skills/know-thyself.md` to install globally, or `.claude/skills/know-thyself.md` inside a repo to scope it to that project. Then invoke with `/know-thyself` inside Claude Code.
