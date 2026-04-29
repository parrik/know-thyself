---
name: know-thyself
description: Build a typed, provenance-tagged personal knowledge graph about yourself with the model. Use when the user wants durable, portable memory that survives any single model conversation — or wants to audit/refactor existing scattered memory into a graph. Clinical/diagnostic, not therapeutic.
---

# know-thyself

Open with this frame, verbatim or close:

> The model doesn't remember — the graph does. We'll build a YAML file you can paste into any future conversation, with any model, to bootstrap context about yourself. Typed, provenance-carrying, separates known from guessed. Diagnostic work, not coaching. I won't interpret what you haven't articulated, and I'll flag tentative as tentative.

Then check: does the user have a local copy of the scaffold? If yes, reference `SCHEMA.md` and `example-graph.yaml` throughout. If no, proceed — schema is summarized below — and at the end point them at github.com/parrik/know-thyself.

## Operating rule (quote to user)

**Attribution ≠ confidence.** A claim restated five times is *one derivation repeated*, not five independent confirmations. Stated-repeatedly is not an overlap. Real confidence comes only from multiple independent derivations — different episodes, different contexts, different evidence types. Make this structural in the graph, not just rhetorical.

## Clinical-tone rules

- Don't fill in interpretations the user hasn't articulated. No psychoanalysis. No diagnosis.
- Prefer `open` over `novel` when uncertain. A question preserved beats an answer invented.
- Every `novel` gets `tentative: true` and `caveats:` naming ≥2 alternative readings and one falsifier.
- Don't promote a `novel` to `overlap` without a second independent episode.
- Warmth in conversational response, not in YAML. The YAML is descriptive.
- Thin memory → thin graph. Resist plausible-sounding fill.

## Node types (summary — see `SCHEMA.md`)

| Type | ID | What it is |
|---|---|---|
| `reference` | R## | Biographical fact, single-source verifiable |
| `observation` | O## | Specific dated episode |
| `overlap` | P## | Pattern across 2+ *independent* observations |
| `novel` | N## | Single-derivation interpretation — MUST be `tentative: true` with `caveats:` |
| `emergent` | E## | Claim only at intersection of 2+ parents |
| `equivalency` | EQ## | Bridge to external framework |
| `open` | OQ## | Unresolved question, first-class |
| `practice` | PR## | Operating rule, must `derive_from` a descriptive node |

Provenance triple on every node: `attribution`, `evidence`, `derivation`. Evidence types: `self-report`, `external-record`, `pattern-across-cases`, `natural-experiment`, `derived-inference` (weakest, must flag).

## Phases

### 1 — Inventory
Pull what you remember. Split into `reference` (biographical: where born, what they do, family) and `observation` (specific dated episodes). **Don't interpret.** Show the list. Ask for corrections. Ask which observations need `HANDLING:`.

### 2 — Overlaps
Patterns grounded in two or more *independent* observations. Be strict — restatements don't count. Name evidence episodes in `evidence.references`. If you write "as they've said many times," stop — that's repetition, not overlap. Add an `implication:` so it doesn't drift back to a restated observation.

### 3 — Novels
Single-derivation interpretations get `novel`, with `tentative: true` and `caveats:`. Include claims the user has repeated often that actually rest on one episode — those feel settled and aren't. Every novel needs (a) alternative reading one, (b) alternative reading two, (c) what would falsify it.

### 4 — Emergents
Claims that don't appear in any single observation but precipitate when 2+ are held together. Both parents in `derivation.from`. **Test:** if one parent alone could produce the claim, it's not emergent — it's a novel on that parent. Most valuable, most speculative.

### 5 — Open questions
What has the user wondered about without resolution? Each gets its own `open` node. Resist folding into novels. A held question is structurally its own thing, not an answer in waiting. Often surfaces quietly-filled-in interpretations.

### 6 — Equivalency bridges (optional)
If the user works within a formal framework, note the bridge as `equivalency`. Don't flatten the graph into the framework — equivalency is a pointer, not a reduction. Skip if no strong external framework applies.

### 6.5 — Practices (optional)
Operating rules derived from the patterns above? ("No X after Y." "Only work on things I use." "Ask directly rather than hope to be seen.") Each must `derive_from` an `overlap`, `novel`, or `observation`. Floating commitments belong in goals, not here. Skip if none apply.

### 7 — Validate and emit
- unique id + complete provenance triple per node
- provenance triple per edge
- every `derivation.from` points to existing node
- every `novel` has `tentative: true` and non-empty `caveats:`
- every `emergent` has ≥2 distinct parents
- every `overlap` has ≥2 distinct *independent* evidence references
- every `practice` derives from at least one descriptive node

Compute in-degree per node. Tell the user which observations are most load-bearing — those are where a correction would cascade.

### 8 — Reflect
What had the user been treating as settled that turns out tentative? What did the intersection actually produce? What open questions had been getting quietly answered with novels? Name fragile nodes explicitly.

## Output

Emit YAML as a single code block to save as `graph.yaml`. If a local scaffold is present, mirror `example-graph.yaml`. Then:

> Save this as `graph.yaml`. To see the mandala (full graph) and spine (load-bearing observations), run `python render.py graph.yaml` from inside the scaffold directory. Scaffold at github.com/parrik/know-thyself.

Remind: the graph is portable. Paste at the start of any future conversation with any model. The model does not remember — the graph does.

## Install

Copy this file to `~/.claude/skills/know-thyself.md` for global, or `.claude/skills/know-thyself.md` per-repo. Invoke with `/know-thyself` in Claude Code.
