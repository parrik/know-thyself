# Schema specification

Formal spec for the memory graph. Adapted from Patrick McCarthy's
[open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph) (MIT).
If a node or edge in your graph violates this spec, it's a bug.

---

## Provenance triple (the invariant)

Every node and every edge carries:

```yaml
provenance:
  attribution:
    source: "who stated this — a person, a document, a conversation"
    date: "when (YYYY-MM-DD or approximate)"
  evidence:
    type: self-report | external-record | pattern-across-cases | natural-experiment | derived-inference
    description: "what the claim rests on"
    references: [list of node-ids, optional]
  derivation:
    from: [list of parent node-ids]
    method: "how the claim follows from the parents — one short sentence"
```

A node without this triple is not a node, it's noise. The rule is
non-negotiable.

---

## Node types

```yaml
# ── Reference: a biographical fact ──────────────────────────────
- id: R01-example                 # IDs: R##, O##, P##, N##, E##, EQ##, OQ##, PR##
  type: reference
  name: "Short human-readable name"
  statement: |
    The fact itself. Single-source, verifiable in principle.
  provenance: {...}               # Attribution usually "self-report"

# Prefer pure references. If a reference accretes episode detail,
# extract the episode as a separate observation that `derives_from`
# the reference — this keeps interpretation-surviving-reinterpretation
# traceable.

# ── Observation: a specific episode ─────────────────────────────
- id: O01-example
  type: observation
  name: "Event name with date"
  statement: |
    What happened. Concrete. Directly witnessed or lived.
  handling: do-not-raise-unprompted   # Optional structured field.
  # Or keep inline: "HANDLING: do not raise unprompted" in the
  # statement. Structured form is preferred when a tool needs to
  # read it; inline is fine when the statement is read by a human.
  provenance: {...}

# ── Overlap: pattern across 2+ independent episodes ─────────────
- id: P01-example
  type: overlap
  name: "The pattern"
  statement: |
    The general claim, phrased so it could be falsified.
  provenance:
    evidence:
      type: pattern-across-cases
      references: [O01, O02, O03]       # Must be ≥2 INDEPENDENT observations
    derivation:
      from: [O01, O02, O03]
      method: "induction across independent instances"
  implication: |                        # Optional but recommended.
    The actionable payload. What the pattern implies for choice, not
    just description. An overlap without an implication tends to drift
    back into a restated observation.

# ── Novel: single-derivation interpretation (TENTATIVE) ─────────
- id: N01-example
  type: novel
  tentative: true                       # MANDATORY for novel
  name: "The interpretation"
  statement: |
    PROPOSED: the single-derivation reading.
  provenance: {...}
  caveats: |                            # MANDATORY for novel
    How this could be wrong:
    (1) alternative reading one
    (2) alternative reading two
    (3) what evidence would falsify it

# ── Emergent: produced by intersection ──────────────────────────
- id: E01-example
  type: emergent
  name: "The intersection-produced insight"
  statement: |
    The claim that doesn't exist in any single parent alone.
  provenance:
    evidence:
      type: derived-inference
      description: "Emerges only from the intersection of parents"
      references: [parent1, parent2]
    derivation:
      from: [parent1, parent2]          # Must be ≥2 parents
      method: "Neither parent alone produces this claim"

# ── Equivalency: bridge to external theory ──────────────────────
- id: EQ01-example
  type: equivalency
  name: "External framework — what it grounds here"
  statement: |
    How the external theoretical framework applies to this graph.
  provenance:
    attribution:
      author: "External theorist name"
      source: "Paper, book, framework title"
    evidence:
      type: external-record
      description: "Where the formal grounding lives"

# ── Open: unresolved question, first-class ──────────────────────
- id: OQ01-example
  type: open
  name: "The question"
  statement: |
    What remains unresolved. Do not let this be quietly absorbed
    into a novel interpretation.
  provenance: {...}

# ── Practice: a normative operating rule ────────────────────────
- id: PR01-example
  type: practice
  name: "The rule"
  statement: |
    A commitment about how to operate, derived from descriptive
    claims in the graph. Not itself descriptive — normative.
    "Don't X before Y." "Always ask directly." "Finish threads."
  provenance:
    attribution: { source: "Self-articulated rule" }
    evidence:
      type: pattern-across-cases
      references: [P01-example, O01-example]    # What it rests on
    derivation:
      from: [P01-example]                       # Usually derives from
      method: "normative rule derived from descriptive overlap"
```

Practice is a scaffold extension for personal graphs — Pat McCarthy's
scientific-claims schema doesn't include it. Use it when the graph has
grown operating rules the user explicitly lives by (a daytime-sobriety
rule, a job-filter rule, a commitment to ask deliberately rather than
hope-to-be-seen). A practice should `derive_from` an overlap or novel
that justifies it, so the normative claim is traceable to the descriptive
claims that motivated it. If your practices have no descriptive
grounding, they belong in a sibling goals/actions document, not here.

---

## Edge relations

Every node can have an optional `edges` list:

```yaml
edges:
  - to: target-node-id
    relation: grounds | grounded_in | derives_from | generalizes |
              instantiates | qualifies | contradicts | emergent_from
    provenance: {...}               # Edges carry provenance too
```

**Meanings:**

| Relation | Direction | Meaning |
|---|---|---|
| `grounds` | child → parent | This node provides grounding for the target |
| `grounded_in` | child → parent | This node is grounded in the target (inverse) |
| `derives_from` | child → parent | This node follows from the target |
| `generalizes` | specific → general | This node is a generalization of the target |
| `instantiates` | general → specific | This node is a specific case of the target |
| `qualifies` | refinement → original | This node adds scope restriction to target |
| `contradicts` | claim → counter-claim | This node conflicts with target from shared premises |
| `emergent_from` | intersection → parent | This node precipitated from target (pairs with another parent) |

---

## Evidence types

| Type | Strength | When to use |
|---|---|---|
| `external-record` | Strongest | Document, data, verifiable third-party source |
| `natural-experiment` | Strong | Same variable, different context, different outcome |
| `pattern-across-cases` | Strong | Repeated instances converging |
| `self-report` | Medium | User stated it directly |
| `derived-inference` | Weakest | Inferred in conversation; must be flagged if used alone |

A `novel` node grounded only in `derived-inference` is the weakest class
of claim in the graph. Treat it accordingly.

---

## Validation rules

A graph is well-formed iff:

1. Every node has a unique `id`.
2. Every node has a complete `provenance` triple.
3. Every edge has a complete `provenance` triple.
4. Every `derivation.from` references an existing node.
5. Every `edges[].to` references an existing node.
6. Every `provenance.evidence.references` (if present) references existing nodes.
7. Every `novel` node has `tentative: true` and a non-empty `caveats:` field.
8. Every `emergent` node has ≥2 distinct entries in `derivation.from`.
9. Every `overlap` node has ≥2 distinct entries in `evidence.references`
   AND these references are not trivially the same event restated.
10. Every `practice` node's `derivation.from` points to at least one
    descriptive node (overlap, novel, observation) — a practice with no
    descriptive grounding is a floating rule that belongs in goals.md,
    not here.

The `render.py` script checks rules 1-6 automatically. Rules 7-10 require
human judgment; Claude should verify them during Phase 7 of construction.

---

## IDs

Prefix conventions:

- `R##` — reference
- `O##` — observation
- `P##` — overlap (pattern)
- `N##` — novel
- `E##` — emergent
- `EQ##` — equivalency
- `OQ##` — open question
- `PR##` — practice (operating rule)

Use descriptive slugs after the number: `O01-first-day-of-job` is better
than `O01`. Slugs help when the YAML is edited by hand.

---

## Optional fields (added Apr 2026, from adjacent frameworks)

These are OPTIONAL. The core schema works without them. Add only on nodes
where they genuinely help.

### `genre:` and `effort:` (from rationalist epistemic-status convention)

Distinguishes passing thoughts from deliberate investigation:

```yaml
genre: observation | speculation | log | analysis | prediction
effort: passing-thought | sustained | deliberate-investigation
```

**Recommended on every `novel` node.** A novel node that's a
passing-thought deserves a different weight than one you've spent an
hour on — and novels are the node type most prone to being treated as
heavier than they are. Tagging effort makes that difference legible.
Optional elsewhere.

### `warrant:` (from Toulmin)

The inferential leap from evidence to claim, stated as a separable
assumption that could be challenged on its own terms:

```yaml
warrant: |
  Why this evidence implies this claim. The assumption doing the work.
  If someone disagrees with this claim, they probably disagree here,
  not with the evidence.
```

Most useful on `overlap`, `novel`, and `emergent` nodes. Forces you to
name assumptions that were implicit.

### `revisions:` (from W3C PROV-O)

History log for how a node has changed over time. Especially useful when
a node is promoted from tentative → stable, or weakened by later counter-
evidence:

```yaml
revisions:
  - date: 2026-04-19
    activity: promotion | weakening | refinement | contradiction | adoption
    from_state: tentative
    to_state: stable
    trigger: O03-new-disclosure     # the node that caused the revision
    reason: "direct first-person disclosure of mechanism"
```

Open a revisions log when the node's *truth-state* changes (tentative →
stable, overlap → qualified overlap), not when its content is edited for
clarity. A typo fix doesn't belong here; a change in what you believe
does.

### `handling:` (structured form of inline HANDLING directive)

For sensitive content, prefer a structured field over inline prose when
any tool reads the graph:

```yaml
handling: surface | quiet | do-not-raise-unprompted | archive
```

- `surface` — default; can be referenced freely.
- `quiet` — can be referenced but not proactively brought up.
- `do-not-raise-unprompted` — only engage if the user surfaces it.
- `archive` — structurally load-bearing but should not appear in
  day-to-day conversation.

Inline `HANDLING: ...` lines in the `statement:` body remain valid for
human-read graphs. Structured `handling:` is preferred when the graph
feeds a tool.

---

## Adaptations from Pat McCarthy's original schema

This personal-memory schema differs from Pat's scientific-claims schema in
seven deliberate ways:

1. **Added `observation` as a first-class node type.** Scientific graphs
   treat events as evidence for propositions; personal graphs treat them
   as nodes themselves because episodes are what get reinterpreted.

2. **Replaced numeric C₁ confidence score with type-tier + `tentative:` + `caveats:`.**
   No principled way to assign proof-strength numbers to personal claims.
   Narrative caveats are more honest than undefended numbers.

3. **Inline `HANDLING:` directives** for sensitive content. Scientific
   nodes don't need operational handling; personal ones do.

4. **Added `natural-experiment` as an evidence type.** Same person,
   different environment, different outcome is the strongest evidence
   available in a personal graph and had no clean analog in Pat's list.

5. **Open questions as systematic first-class nodes** with provenance,
   not just a sparse category. In personal graphs, open questions get
   silently absorbed into confident answers if not structurally protected.

6. **Repurposed `equivalency` type** from cross-framework alignment to
   external-theory bridges. Personal graphs don't have multiple internal
   frameworks; they may have external theoretical bridges worth naming.

7. **Added `practice` as an eighth node type.** Personal graphs naturally
   accumulate operating rules the user lives by (a sobriety rule, a
   filter rule, a commitment to deliberate asking). These are normative,
   not descriptive, but they belong in the graph when they `derive_from`
   descriptive claims — traceability from "this is the pattern" to
   "therefore this is the rule I'm adopting." A practice with no
   descriptive grounding belongs in goals.md, not here.
