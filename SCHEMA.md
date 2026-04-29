# Schema specification

Formal spec for the memory graph. If a node or edge violates this spec, it's a bug.

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

A node without this triple is not a node. Non-negotiable.

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
# the reference.

# ── Observation: a specific episode ─────────────────────────────
- id: O01-example
  type: observation
  name: "Event name with date"
  statement: |
    What happened. Concrete. Directly witnessed or lived.
  handling: do-not-raise-unprompted   # Optional structured field.
  # Or inline: "HANDLING: do not raise unprompted" in the statement.
  # Structured form preferred when a tool reads it; inline is fine
  # for human-only reading.
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
      references: [O01, O02, O03]       # ≥2 INDEPENDENT observations
    derivation:
      from: [O01, O02, O03]
      method: "induction across independent instances"
  implication: |                        # Optional but recommended.
    The actionable payload. An overlap without an implication tends
    to drift back into a restated observation.

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
      from: [parent1, parent2]          # ≥2 parents
      method: "Neither parent alone produces this claim"

# ── Equivalency: bridge to external theory ──────────────────────
- id: EQ01-example
  type: equivalency
  name: "External framework — what it grounds here"
  statement: |
    How the external framework applies to this graph.
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
    claims. Not descriptive — normative.
    "Don't X before Y." "Always ask directly." "Finish threads."
  provenance:
    attribution: { source: "Self-articulated rule" }
    evidence:
      type: pattern-across-cases
      references: [P01-example, O01-example]
    derivation:
      from: [P01-example]
      method: "normative rule derived from descriptive overlap"
```

`practice` is a personal-graph extension. Use when the graph has grown rules the user explicitly lives by (a no-screens-after-X rule, a job-filter rule, a commitment to ask directly). A practice should `derive_from` a descriptive node so the normative claim stays traceable. Floating rules with no descriptive grounding belong in a sibling goals/actions doc, not here.

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

| Relation | Direction | Meaning |
|---|---|---|
| `grounds` | child → parent | Provides grounding for the target |
| `grounded_in` | child → parent | Grounded in the target (inverse) |
| `derives_from` | child → parent | Follows from the target |
| `generalizes` | specific → general | Generalization of the target |
| `instantiates` | general → specific | Specific case of the target |
| `qualifies` | refinement → original | Adds scope restriction |
| `contradicts` | claim → counter-claim | Conflicts from shared premises |
| `emergent_from` | intersection → parent | Precipitated from target (pairs with another parent) |

---

## Evidence types

| Type | Strength | When |
|---|---|---|
| `external-record` | Strongest | Document, data, verifiable third-party |
| `natural-experiment` | Strong | Same variable, different context, different outcome |
| `pattern-across-cases` | Strong | Repeated instances converging |
| `self-report` | Medium | User stated it directly |
| `derived-inference` | Weakest | Inferred in conversation; flag if used alone |

A `novel` grounded only in `derived-inference` is the weakest claim class in the graph. Treat it accordingly.

---

## Validation rules

A graph is well-formed iff:

1. Every node has a unique `id`.
2. Every node has a complete `provenance` triple.
3. Every edge has a complete `provenance` triple.
4. Every `derivation.from` references an existing node.
5. Every `edges[].to` references an existing node.
6. Every `provenance.evidence.references` (if present) references existing nodes.
7. Every `novel` has `tentative: true` and a non-empty `caveats:`.
8. Every `emergent` has ≥2 distinct entries in `derivation.from`.
9. Every `overlap` has ≥2 distinct entries in `evidence.references`, not trivially the same event restated.
10. Every `practice` derives from at least one descriptive node (overlap, novel, observation).

`render.py` checks 1–6 automatically. 7–10 require human judgment; verify during Phase 7.

---

## IDs

- `R##` — reference
- `O##` — observation
- `P##` — overlap (pattern)
- `N##` — novel
- `E##` — emergent
- `EQ##` — equivalency
- `OQ##` — open question
- `PR##` — practice

Use descriptive slugs: `O01-first-day-of-job` over `O01`. Helps when the YAML is hand-edited.

---

## Sub-categories of `reference` (added April 2026)

After several weeks of building on a real graph, five patterns emerged as useful **sub-categories of `reference`** — not new node types. Extending the core type list is fragile (see `SCHEMA_DEPRECIATION.md`); descriptive prefixes keep the schema small while making common roles legible.

| Prefix / role | What it is | Example |
|---|---|---|
| `R-canary-*` | Evidence-backed leading indicator | *Sleep-onset latency >30 min for 3 nights predicts relapse* |
| `R-lens-*` | Mental-model frame applied to other nodes | *Circuit breakers, Ulysses pact, Chesterton's Fence* |
| `R-experiment-*` | Runnable method with an evidence base | *Implementation intentions* |
| `R-filter-*` | Anti-pattern frame for a decision domain | *Revenue-line reverse interview* |
| `type: forecast` | Time-horizon inference, flagged tentative | 1 month · 90 days · 1 year · 10 years · 30 years |

Plus:

- **`NOW`** — a single node with `type: now` at the graph's center, holding current priorities and pointers. First thing read when the graph opens. Prevents the "where do I start?" problem.

`example-graph-extended.yaml` demonstrates these.

---

## Optional fields (added Apr 2026)

OPTIONAL. Core schema works without them. Add only on nodes where they help.

### `genre:` and `effort:`

Distinguishes passing thoughts from deliberate investigation:

```yaml
genre: observation | speculation | log | analysis | prediction
effort: passing-thought | sustained | deliberate-investigation
```

**Recommended on every `novel`.** A passing-thought novel deserves different weight than an hour-long one — and novels are the type most prone to being treated as heavier than they are.

### `warrant:`

The inferential leap from evidence to claim:

```yaml
warrant: |
  Why this evidence implies this claim. The assumption doing the work.
  If someone disagrees with the claim, they probably disagree here,
  not with the evidence.
```

Most useful on `overlap`, `novel`, `emergent`. Forces naming assumptions that were implicit.

### `revisions:`

History log for how a node has changed:

```yaml
revisions:
  - date: 2026-04-19
    activity: promotion | weakening | refinement | contradiction | adoption
    from_state: tentative
    to_state: stable
    trigger: O03-new-disclosure
    reason: "direct first-person disclosure of mechanism"
```

Open a revisions log when the node's *truth-state* changes (tentative → stable, overlap → qualified overlap), not when content is edited for clarity. Typo fix: no. Change in belief: yes.

### `handling:`

Structured form of inline HANDLING directive:

```yaml
handling: surface | quiet | do-not-raise-unprompted | archive
```

- `surface` — default; can be referenced freely.
- `quiet` — referenced but not proactively raised.
- `do-not-raise-unprompted` — only engage if user surfaces it.
- `archive` — structurally load-bearing, should not appear day-to-day.

Inline `HANDLING:` lines stay valid for human-read graphs. Structured `handling:` is preferred when a tool reads the graph.

---

## Extensions for personal memory

Personal memory operates under different constraints than scientific knowledge — no replication, no external ground truth, fuzzy temporal validity, node-dense rather than edge-dense growth as life events accumulate.

I make seven deliberate extensions beyond scientific-claims provenance schemas:

1. **`observation` as a first-class node type.** Scientific graphs treat events as evidence for propositions; personal graphs treat them as nodes because episodes get reinterpreted.

2. **Type-tier + `tentative:` + `caveats:` instead of numeric C₁ confidence.** No principled way to assign proof-strength numbers to personal claims. Narrative caveats are more honest than undefended numbers.

3. **HANDLING directives** for sensitive content. Scientific nodes don't need operational handling; personal ones do.

4. **`natural-experiment` as an evidence type.** Same person, different environment, different outcome — strongest evidence available in a personal graph, no clean analog in scientific schemas.

5. **Open questions as systematic first-class nodes** with provenance. In personal graphs, open questions get silently absorbed into confident answers if not structurally protected.

6. **Repurposed `equivalency`** from cross-framework alignment to external-theory bridges. Personal graphs don't have multiple internal frameworks; they may have external bridges worth naming.

7. **`practice` as an eighth node type.** Personal graphs accumulate operating rules. These are normative, not descriptive, but belong in the graph when they `derive_from` descriptive claims — traceability from "this is the pattern" to "therefore this is the rule." A practice with no descriptive grounding belongs in goals.md, not here.

---

## Credit

Provenance-triple shape from W3C [RDF](https://www.w3.org/TR/rdf11-concepts/) (2004) and [PROV-O](https://www.w3.org/TR/prov-overview/) (2013). Patrick McCarthy's [open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph) (MIT) gives the formal articulation for the **scientific** case. The personal-graph schema above — typed nodes adapted to personal life, four-scale synthesis, `valid_at` temporal validity, MCP retrieval — is mine.
