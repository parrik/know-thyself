# START HERE — paste the rest into a Claude conversation

---

Help me build a knowledge graph of what you remember about me. The goal: separate observations from interpretations, flag tentative claims, surface insights that only appear at intersections.

Read these instructions carefully, then proceed in phases.

## The invariant

Every node and every edge carries a provenance triple: *(attribution, evidence, derivation)*. A claim without provenance is indistinguishable from noise.

## The core rule

**Attribution ≠ confidence.** A claim restated five times across conversations is one derivation repeated, not five confirmations. Real confidence requires multiple **independent** derivations — different episodes, different contexts, different evidence types.

## Node types

| Type | Meaning | Confidence basis |
|---|---|---|
| `reference` | Biographical fact | Single-source but verifiable |
| `observation` | Specific episode I lived | Direct event |
| `overlap` | Pattern from 2+ independent episodes | Multiple groundings |
| `novel` | Single-derivation interpretation | **Tentative — must flag** |
| `emergent` | Only appears at intersection of 2+ nodes | Most valuable, most speculative |
| `equivalency` | Bridge to external framework | External grounding |
| `open` | Unresolved question, first-class | N/A |
| `practice` | Operating rule derived from descriptive claims | Must `derive_from` overlap/novel/observation |

Novel nodes MUST carry `tentative: true` and a `caveats:` field listing how they could be wrong. Open questions stay open — do not collapse them into novel interpretations.

## Edge relations

`derives_from`, `grounds`, `grounded_in`, `generalizes`, `instantiates`, `qualifies`, `contradicts`, `emergent_from`. Each edge carries its own provenance.

## Evidence types

`self-report` (I said it), `external-record` (document/data/third-party), `pattern-across-cases` (repeated instances), `natural-experiment` (same variable, different context, different outcome — strongest), `derived-inference` (you inferred it; weakest, must be flagged).

## HANDLING directives

For sensitive content that's structurally load-bearing but shouldn't be casually surfaced, include an inline directive: `HANDLING: do not raise unprompted`. Ask before assuming. When in doubt, flag.

---

## Phases — do not jump ahead

**1. Inventory.** Pull biographical facts (`reference`) and specific episodes (`observation`) from what you remember. Don't interpret yet. Show the list. Let me correct, add, remove. Ask which observations need `HANDLING:`.

**2. Patterns.** Which patterns are grounded in two or more **independent** episodes? Those become `overlap`. Two restatements of the same claim do not count as two groundings.

**3. Novels — tentatively.** Single-derivation interpretations get `novel`, with `tentative: true` and `caveats:`. Include claims I've repeated often that actually rest on one episode — they feel settled and aren't.

**4. Emergents.** Claims not present in any single observation but precipitating only when 2+ nodes are held together. Both parents go in `derivation.from`. If one parent alone produces the claim, it's not emergent.

**5. Open questions.** What have I wondered about without resolution? Each is its own `open` node. Resist folding these into novels.

**6. Equivalency bridges (optional).** If my behavior instantiates a formal framework I work within, add `equivalency` nodes. Skip if no strong external framework applies.

**6.5. Practices (optional).** Have I adopted operating rules derived from the patterns? Each must `derive_from` a descriptive node — a floating rule belongs in goals.md, not here. Skip if none apply.

**7. Validate.** Produce the YAML. Check: every node has provenance, every edge has provenance, every `derivation.from` points to an existing node, every HANDLING-flagged observation carries its directive. Compute in-degree — tell me which observations are most load-bearing.

**8. Reflect.** What had I been treating as settled that turns out to be tentative? What did the intersection actually produce? What open questions had I been quietly answering with novels?

---

## Avoid

- **No diagnosis.** No "you have X" or "you are Y."
- **No psychoanalysis past a derivation you can state.** If you can't produce clean parents and method, drop the node.
- **Novels don't propagate.** An emergent derived from a tentative novel is doubly tentative — flag that.
- **No reassurance in graph content.** Warmth belongs in your conversational response, not the YAML.
- **Don't fill gaps.** Thin memory → thin graph.

---

## Output

- A complete YAML graph.
- A short summary: load-bearing observations (top 5–10 by in-degree), fragile claims (all novels with caveats), emergent nodes, open questions, anything flagged for HANDLING and why.

Begin with Phase 1.

---

## Credit

Provenance-triple shape draws on W3C [RDF](https://www.w3.org/TR/rdf11-concepts/) and [PROV-O](https://www.w3.org/TR/prov-overview/), and Patrick McCarthy's [open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph) (MIT) for the personal-graph framing. This scaffold extends them for personal memory specifically.
