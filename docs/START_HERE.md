# START HERE — paste the rest into a Claude conversation

---

Help me build a knowledge graph of what you remember about me. The goal: separate observations from interpretations, flag tentative claims, surface insights that only appear at intersections.

Read these instructions carefully, then proceed in phases.

## The invariant — every node and edge carries provenance

Every node and every edge carries a provenance triple: *(attribution, evidence, derivation)*. A claim without provenance is indistinguishable from noise.

> **Claim:** Provenance is the structural invariant; nodes without it are not nodes.
> **Grounds:** Definitional, mirrors SCHEMA.md's invariant.
> **Status:** stipulated
> **Leans on:** every phase below; SCHEMA.md.

## The core rule — attribution is not confidence

**Attribution ≠ confidence.** A claim restated five times across conversations is one derivation repeated, not five confirmations. Real confidence requires multiple **independent** derivations — different episodes, different contexts, different evidence types.

> **Claim:** Repetition does not accumulate confidence; only independent derivations do.
> **Grounds:** Stated as the discipline's core rule; rationale matches the README's flat-list critique.
> **Status:** stipulated
> **Leans on:** Phase 2 (overlap requires ≥2 independent episodes); Phase 3 (single-derivation claims must be marked tentative).

## Node types — the eight typed shapes a claim can take

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

> **Claim:** Eight typed node shapes are the only legal node kinds.
> **Grounds:** Enumeration; matches SCHEMA.md's node-types section.
> **Status:** stipulated
> **Leans on:** Phases 1–6.5 (each phase produces nodes of specific types); SCHEMA.md.

## Edge relations — the eight typed connections

`derives_from`, `grounds`, `grounded_in`, `generalizes`, `instantiates`, `qualifies`, `contradicts`, `emergent_from`. Each edge carries its own provenance.

> **Claim:** Eight relation types cover the structural moves between nodes.
> **Grounds:** Enumeration; matches SCHEMA.md's edge-relations table.
> **Status:** stipulated
> **Leans on:** Phase 7 validation (`edges[].to` must resolve); SCHEMA.md.

## Evidence types — the five-tier strength ladder

`self-report` (I said it), `external-record` (document/data/third-party), `pattern-across-cases` (repeated instances), `natural-experiment` (same variable, different context, different outcome — strongest), `derived-inference` (you inferred it; weakest, must be flagged).

> **Claim:** Evidence type encodes claim strength on a discrete five-tier ladder.
> **Grounds:** Enumeration matches SCHEMA.md's evidence-types table.
> **Status:** stipulated
> **Leans on:** Phase 3 (flag `derived-inference`-only novels); SCHEMA.md.

## HANDLING directives — sensitive content stays load-bearing without being casually surfaced

For sensitive content that's structurally load-bearing but shouldn't be casually surfaced, include an inline directive: `HANDLING: do not raise unprompted`. Ask before assuming. When in doubt, flag.

> **Claim:** Sensitive content needs an operational handling directive, not removal.
> **Grounds:** Operating rule; matches SCHEMA.md's `handling:` field.
> **Status:** stipulated
> **Leans on:** Phase 1 (ask which observations need HANDLING); SAFETY.md.

---

## Phases — do not jump ahead

**1. Inventory — pull facts and episodes; defer interpretation.** Pull biographical facts (`reference`) and specific episodes (`observation`) from what you remember. Don't interpret yet. Show the list. Let me correct, add, remove. Ask which observations need `HANDLING:`.

> **Claim:** Inventory phase produces only `reference` and `observation` nodes; interpretation is deferred.
> **Grounds:** Phase definition; sequencing rationale (interpretation requires a confirmed substrate).
> **Status:** stipulated
> **Leans on:** Phases 2–4 (which depend on a settled inventory); HANDLING discipline.

**2. Patterns — promote to `overlap` only on ≥2 independent episodes.** Which patterns are grounded in two or more **independent** episodes? Those become `overlap`. Two restatements of the same claim do not count as two groundings.

> **Claim:** A pattern qualifies as `overlap` only when grounded in ≥2 independent episodes.
> **Grounds:** Phase rule; restates the core attribution-≠-confidence rule.
> **Status:** stipulated
> **Leans on:** Phase 1's inventory; SCHEMA.md validation rule 9.

**3. Novels — single-derivation interpretations, marked tentative with caveats.** Single-derivation interpretations get `novel`, with `tentative: true` and `caveats:`. Include claims I've repeated often that actually rest on one episode — they feel settled and aren't.

> **Claim:** Single-derivation interpretations are `novel`, mandatory `tentative: true` and `caveats:`.
> **Grounds:** Phase rule; matches SCHEMA.md validation rule 7.
> **Status:** stipulated
> **Leans on:** the felt-settled-but-isn't failure mode; Phase 8's reflection step.

**4. Emergents — claims that only appear at the intersection of ≥2 parents.** Claims not present in any single observation but precipitating only when 2+ nodes are held together. Both parents go in `derivation.from`. If one parent alone produces the claim, it's not emergent.

> **Claim:** Emergent claims require ≥2 parents and disappear if any one parent alone could produce them.
> **Grounds:** Phase rule; matches SCHEMA.md validation rule 8.
> **Status:** stipulated
> **Leans on:** Phases 1–3 (which produce the parents); SCHEMA.md emergent definition.

**5. Open questions — first-class nodes, do not absorb into novels.** What have I wondered about without resolution? Each is its own `open` node. Resist folding these into novels.

> **Claim:** Unresolved questions are first-class `open` nodes; they must not collapse into novels.
> **Grounds:** Phase rule; tracks the personal-memory extension that protects open questions structurally.
> **Status:** stipulated
> **Leans on:** SCHEMA.md extension #5; Phase 8's reflection prompt about novels-as-quiet-answers.

**6. Equivalency bridges (optional) — external framework grounding when one applies.** If my behavior instantiates a formal framework I work within, add `equivalency` nodes. Skip if no strong external framework applies.

> **Claim:** Equivalency nodes are optional and only added when a real external framework applies.
> **Grounds:** Phase rule; conservative-by-default sequencing.
> **Status:** stipulated
> **Leans on:** SCHEMA.md's repurposed-equivalency extension.

**6.5. Practices (optional) — operating rules that derive from descriptive claims.** Have I adopted operating rules derived from the patterns? Each must `derive_from` a descriptive node — a floating rule belongs in goals.md, not here. Skip if none apply.

> **Claim:** Practices are normative rules that must trace to a descriptive parent; floating rules are out of scope.
> **Grounds:** Phase rule; matches SCHEMA.md validation rule 10.
> **Status:** stipulated
> **Leans on:** Phases 2–4 (the descriptive parents); SCHEMA.md practice definition.

**7. Validate — produce the YAML and check well-formedness.** Produce the YAML. Check: every node has provenance, every edge has provenance, every `derivation.from` points to an existing node, every HANDLING-flagged observation carries its directive. Compute in-degree — tell me which observations are most load-bearing.

> **Claim:** Validation enforces the well-formedness rules and surfaces load-bearing observations by in-degree.
> **Grounds:** Phase rule; corresponds to SCHEMA.md validation rules 1–10.
> **Status:** stipulated
> **Leans on:** SCHEMA.md validation section; `know_thyself.render.graphviz` for the machine-checkable subset.

**8. Reflect — what was settled is tentative, what intersection produced, what novels were quiet answers.** What had I been treating as settled that turns out to be tentative? What did the intersection actually produce? What open questions had I been quietly answering with novels?

> **Claim:** Reflection turns the validated graph back on the user's prior beliefs to surface mis-weighted claims.
> **Grounds:** Phase rule; closes the loop on attribution-≠-confidence.
> **Status:** stipulated
> **Leans on:** all prior phases; the core rule.

---

## Avoid — five anti-patterns that collapse the discipline

- **No diagnosis.** No "you have X" or "you are Y."
- **No psychoanalysis past a derivation you can state.** If you can't produce clean parents and method, drop the node.
- **Novels don't propagate.** An emergent derived from a tentative novel is doubly tentative — flag that.
- **No reassurance in graph content.** Warmth belongs in your conversational response, not the YAML.
- **Don't fill gaps.** Thin memory → thin graph.

> **Claim:** Five named anti-patterns reliably collapse the discipline if not refused.
> **Grounds:** Enumerated failure modes; each tied to a specific structural rule (no provenance → no node, etc.).
> **Status:** stipulated
> **Leans on:** the invariant and core rule; SAFETY.md.

---

## Output — the YAML graph plus a load-bearing summary

- A complete YAML graph.
- A short summary: load-bearing observations (top 5–10 by in-degree), fragile claims (all novels with caveats), emergent nodes, open questions, anything flagged for HANDLING and why.

Begin with Phase 1.

> **Claim:** The deliverable is a YAML graph plus a structured summary of load-bearing and fragile content.
> **Grounds:** Operational specification.
> **Status:** stipulated
> **Leans on:** Phase 7 (validation produces in-degree); Phase 3 (caveats); Phase 5 (open questions).

---

## Credit — lineage of the provenance shape and personal-graph adaptation

Provenance-triple shape draws on W3C [RDF](https://www.w3.org/TR/rdf11-concepts/) and [PROV-O](https://www.w3.org/TR/prov-overview/). Patrick McCarthy's [open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph) (MIT) gives the formal articulation for **scientific** claims. The personal-graph adaptation in this prompt — typed nodes for personal memory, four-scale synthesis, temporal validity, MCP retrieval — is mine.

> **Claim:** Provenance-triple shape is borrowed from W3C; personal-graph adaptation in this prompt is original.
> **Grounds:** Cited standards; explicit boundary statement.
> **Status:** established (cited prior art); stipulated (boundary)
> **Leans on:** README.md and SCHEMA.md credit sections.
