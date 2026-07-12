# Schema specification

Formal spec for the memory graph. If a node or edge violates this spec, it's a bug.

> **Claim:** This document is the formal spec; deviations are bugs, not variants.
> **Grounds:** Stated as the file's purpose.
> **Status:** stipulated
> **Leans on:** the renderers and validator at [know-thyself-search](https://github.com/parrik/know-thyself-search); START_HERE.md (which paraphrases this spec for the LLM).

---

## Provenance — the paper trail every node carries

Every node carries seven flat fields that together answer three questions about any claim: **who said it, what it rests on, how it follows from prior claims**. The fields are plain English at the YAML level; the concept "provenance" stays as the practice name.

```yaml
# WHO said it
said_by: "who stated this — a person, a document, a conversation"
said_when: "YYYY-MM-DD or approximate"

# WHAT it rests on
evidence_kind: self-report | external-record | pattern-across-cases | natural-experiment | derived-inference
evidence_notes: "what the claim rests on (optional, free text)"
evidence_refs: [list of node-ids that the claim cites]   # optional

# HOW it follows from parents
derives_from: [list of parent node-ids]
how_it_follows: "how this claim follows from its parents — one short sentence"
```

Four of the seven are required on every node — `said_by`, `evidence_kind`, `derives_from`, `how_it_follows` (validation rule 2); `said_when`, `evidence_notes`, and `evidence_refs` are optional but recommended. A node without the required four is not a node. Non-negotiable.

For root nodes (no parents): `derives_from: []` and `how_it_follows: "direct"` is fine.

> **Claim:** Provenance is the schema invariant — without the four required fields, the unit is not a graph node.
> **Grounds:** Definitional rule. The shape is structurally equivalent to PROV-O's three-tuple (attribution / evidence / derivation), flattened to plain English keys for readability. RDF/PROV-O compatibility is available by re-grouping; the schema's primary surface is human-editable YAML.
> **Status:** stipulated
> **Leans on:** every node type below; the validation rules; the validator's mechanical checks (rules 1–10).

---

## Node types — eight core typed shapes for claims, plus three temporal-organization types

```yaml
# ── Reference: a biographical fact ──────────────────────────────
- id: R01-example                 # IDs: R##, O##, P##, N##, E##, EQ##, OQ##, PR##
  type: reference
  name: "Short human-readable name"
  statement: |
    The fact itself. Single-source, verifiable in principle.
  said_by: "Self-report"
  said_when: "2025"
  evidence_kind: self-report
  derives_from: []
  how_it_follows: "direct"

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
  said_by: "Self-report"
  said_when: "2025-03-12"
  evidence_kind: self-report
  derives_from: []
  how_it_follows: "direct"

# ── Overlap: pattern across 2+ independent episodes ─────────────
- id: P01-example
  type: overlap
  name: "The pattern"
  statement: |
    The general claim, phrased so it could be falsified.
  said_by: "Self-report"
  said_when: "2025"
  evidence_kind: pattern-across-cases
  evidence_refs: [O01, O02, O03]        # ≥2 INDEPENDENT observations
  derives_from: [O01, O02, O03]
  how_it_follows: "induction across independent instances"
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
  said_by: "Self-articulated"
  said_when: "2025"
  evidence_kind: derived-inference
  derives_from: [O01]
  how_it_follows: "single-derivation interpretation"
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
  said_by: "Self-articulated"
  said_when: "2025"
  evidence_kind: derived-inference
  evidence_notes: "Emerges only from the intersection of parents"
  evidence_refs: [parent1, parent2]
  derives_from: [parent1, parent2]      # ≥2 parents
  how_it_follows: "Neither parent alone produces this claim"

# ── Equivalency: bridge to external theory ──────────────────────
- id: EQ01-example
  type: equivalency
  name: "External framework — what it grounds here"
  statement: |
    How the external framework applies to this graph.
  said_by: "External theorist name (Paper / book / framework title)"
  said_when: "publication year if known"
  evidence_kind: external-record
  evidence_notes: "Where the formal grounding lives"
  derives_from: []
  how_it_follows: "external framework bridged to this graph"

# ── Open: unresolved question, first-class ──────────────────────
- id: OQ01-example
  type: open
  name: "The question"
  statement: |
    What remains unresolved. Do not let this be quietly absorbed
    into a novel interpretation.
  said_by: "Self-articulated"
  said_when: "2025"
  evidence_kind: self-report
  derives_from: []
  how_it_follows: "direct"

# ── Practice: a normative operating rule ────────────────────────
# HUMAN-GATED: the one type the model must not save on its own.
# Draft it, then wait for the user's explicit yes (see "The write
# gate" section below).
- id: PR01-example
  type: practice
  name: "The rule"
  statement: |
    A commitment about how to operate, derived from descriptive
    claims. Not descriptive — normative.
    "Don't X before Y." "Always ask directly." "Finish threads."
  said_by: "Self-articulated rule"
  said_when: "2025"
  evidence_kind: pattern-across-cases
  evidence_refs: [P01-example, O01-example]
  derives_from: [P01-example]
  how_it_follows: "normative rule derived from descriptive overlap"
```

`practice` is a personal-graph extension. Use when the graph has grown rules the user explicitly lives by (a no-screens-after-X rule, a job-filter rule, a commitment to ask directly). A practice should `derive_from` a descriptive node so the normative claim stays traceable. Floating rules with no descriptive grounding belong in a sibling goals/actions doc, not here.

> **Claim:** Eight typed node shapes — reference, observation, overlap, novel, emergent, equivalency, open, practice — exhaust the kinds of claim the graph admits.
> **Grounds:** Enumerated definitions above; each carries a YAML template and a discriminating rule.
> **Status:** stipulated
> **Leans on:** the validation rules below (which enforce per-type constraints); the IDs section; START_HERE.md's node-type table.

---

## The write gate — who writes what

Every type except `practice` is model-writable: the model authors and saves references, observations, overlaps, novels, emergents, equivalencies, opens, themes, periods, and `NOW` updates on its own. A `practice` is the one type that waits for the human: the model may *draft* a practice candidate, but the node enters the graph only on the user's explicit yes.

| Types | Who saves |
|---|---|
| R / O / P / N / E / EQ / OQ / T- / L- / NOW | model, autonomously |
| PR (`practice`) | human-in-the-loop — explicit yes required |

The asymmetry is deliberate and narrow. A wrong descriptive node is cheap: it sits in the record, marked with its provenance, and gets corrected or contradicted later. A wrong practice is the thing you go and act on. Gating everything doesn't scale (the record stops filling in); gating nothing hands the model your operating rules. Gating exactly the normative layer keeps the human at the one point where an error is expensive.

> **Claim:** Descriptive and organizational nodes are model-writable; practices require explicit human acceptance before entering the graph.
> **Grounds:** Asymmetric cost of error (a wrong node is corrected later; a wrong rule is acted on); ~6 months of two-ring operation on a long-running graph after an earlier gate-everything policy failed to scale.
> **Status:** stipulated (write policy adopted May 2026, superseding full hand-curation)
> **Leans on:** the `practice` type definition above; DEPRECATION.md (the durable thing is the discipline — here, the discipline is the gate).

---

## Edge relations — the eight typed connections between nodes

Every node can have an optional `edges` list:

```yaml
edges:
  - to: target-node-id
    relation: grounds | grounded_in | derives_from | generalizes |
              instantiates | qualifies | contradicts | emergent_from
    # Edges carry provenance only when justification beyond endpoints
    # matters — most edges inherit provenance from the parent node's
    # `derives_from`.
    evidence_kind: derived-inference
    evidence_notes: "why this edge holds (optional)"
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

> **Claim:** Eight typed edge relations cover the structural moves the graph needs to express.
> **Grounds:** Enumerated relation table with directionality and meaning.
> **Status:** stipulated
> **Leans on:** validation rule 4 (every `edges[].to` resolves); the renderers' adjacency computations.

---

## Evidence types — the five-tier strength ladder

| Type | Strength | When |
|---|---|---|
| `external-record` | Strongest | Document, data, verifiable third-party |
| `natural-experiment` | Strong | Same variable, different context, different outcome |
| `pattern-across-cases` | Strong | Repeated instances converging |
| `self-report` | Medium | User stated it directly |
| `derived-inference` | Weakest | Inferred in conversation; flag if used alone |

A `novel` grounded only in `derived-inference` is the weakest claim class in the graph. Treat it accordingly.

> **Claim:** Evidence type maps to claim strength on a discrete five-tier ladder, not a numeric score.
> **Grounds:** Tabulated above; rationale (no replication, no external ground truth) elaborated in the personal-memory extensions section.
> **Status:** stipulated
> **Leans on:** the type-tier-instead-of-numeric-confidence extension; the HANDLING for `novel`-only-on-`derived-inference`.

---

## Validation rules — the well-formedness conditions

A graph is well-formed iff:

1. Every node has a unique `id`.
2. Every node has the four required provenance fields: `said_by`, `evidence_kind`, `derives_from`, `how_it_follows`. (`said_when`, `evidence_notes`, `evidence_refs` are optional but recommended.)
3. Every `derives_from` references an existing node.
4. Every `edges[].to` references an existing node.
5. Every `evidence_refs` (if present) references existing nodes.
6. Every `novel` has `tentative: true` and a non-empty `caveats:`.
7. Every `emergent` has ≥2 distinct entries in `derives_from`.
8. Every `overlap` has ≥2 distinct entries in `evidence_refs`, not trivially the same event restated.
9. Every `practice` derives from at least one descriptive parent (`overlap`, `novel`, `observation`, or a `reference` whose role-prefix is `R-experiment-` / `R-lens-` / `R-filter-`).

If a graph uses the temporal-organization types (`now`, `theme`, `period`) the following also apply:

10. There is at most one `type: now` node, with `id: NOW`.
11. Every `theme` has ≥3 distinct entries in `members:`, and `derives_from` lists ≥2 distinct periods.
12. No two `period` nodes have overlapping `span:` ranges (a transition event may appear in `contains:` on both sides only when the event is *the* transition).

Edges carry `to:` and `relation:` only — they inherit provenance from the parent node's `derives_from` when the edge mirrors that derivation. Explicit edge provenance fields (`evidence_kind`, `evidence_notes`, `how_it_follows`) are allowed but not required.

Rules 1–10 are checked structurally from the YAML alone (the validator at `know-thyself-search` runs them). Rules 7–10 also have a human-judgment layer beyond the structural check — independence of overlap references, sufficiency of novel caveats, whether a practice's parents are genuinely descriptive — verified during Phase 7 of START_HERE.md. Rules 11–12 (theme cardinality, period non-overlap) require human judgment fully.

> **Claim:** Twelve conditions are jointly necessary and sufficient for a well-formed graph (9 core + 3 conditional on temporal-type use).
> **Grounds:** Enumerated; rules 1–10 are checked structurally by the validator at `know-thyself-search`; rules 7–10 also have a human-judgment layer (independence of evidence, caveats sufficiency, whether parents are genuinely descriptive); rules 11–12 are pure human judgment. Rule 9 broadened to admit role-prefixed references after empirical use showed practices regularly derive from `R-lens-` / `R-experiment-` / `R-filter-` nodes. The edge-provenance requirement was dropped after empirical use showed essentially no edges in long-running graphs carry provenance — edges encode structural relationships whose justification lives on the parent node.
> **Status:** stipulated
> **Leans on:** the rule enumeration above; START_HERE.md Phase 7 (human-judgment subset).

---

## IDs — the prefixes and the descriptive-slug convention

Eight core types:

- `R##` — reference
- `O##` — observation
- `P##` — overlap (pattern)
- `N##` — novel
- `E##` — emergent
- `EQ##` — equivalency
- `OQ##` — open question
- `PR##` — practice

Plus three temporal-organization types added May 2026 (see *Temporal organization* section below):

- `T-##` — theme (cross-time organizing packet)
- `L-##` — period (lifetime period container)
- `NOW` — singleton, `type: now`

Use descriptive slugs: `O01-first-day-of-job` over `O01`. Helps when the YAML is hand-edited. Theme and period IDs use a hyphen-after-prefix form (`T-01-...`, `L-01-...`) to keep the prefix legible against an `R##` numeric run.

> **Claim:** ID prefix encodes node type; descriptive slug aids hand-editing.
> **Grounds:** Convention; example contrast; prefix-form rationale (legibility).
> **Status:** stipulated
> **Leans on:** node-type validation (prefix-to-type matching); cross-references throughout the bundle.

---

## Sub-categories of `reference` — role prefixes

Five role-prefix patterns keep common reference flavors legible without minting new top-level types. Extending the core type list is fragile (see `DEPRECATION.md`); prefixes keep the schema small.

| Prefix | Role | Example |
|---|---|---|
| `R-canary-*` | Evidence-backed leading indicator | *Sleep-onset latency >30 min for 3 nights predicts relapse* |
| `R-lens-*` | Mental-model frame applied to other nodes | *Circuit breakers, Ulysses pact, Chesterton's Fence* |
| `R-experiment-*` | Runnable method with an evidence base | *Implementation intentions* |
| `R-filter-*` | Anti-pattern frame for a decision domain | *Revenue-line reverse interview* |
| `R-forecast-*` *(or `E-forecast-*` for intersection-derived forecasts)* | Time-horizon inference, flagged tentative | A 90-day forecast about a deadline; a 5-year forecast about a career arc |

Forecasts may live as prefixed `reference` nodes (`R-forecast-*`) when they extrapolate from a single source, or as prefixed `emergent` nodes (`E-forecast-*`) when they come from the intersection of two or more parents. Either way, mark `tentative: true`.

> **Claim:** Common reference roles are best expressed as descriptive prefixes, not new top-level node types.
> **Grounds:** Empirical — patterns observed after weeks of use; rationale grounded in DEPRECATION.md's argument against type-list bloat.
> **Status:** tentative (introduced April 2026; could deprecate)
> **Leans on:** DEPRECATION.md.

---

## Temporal organization — `now`, `theme`, `period` (added May 2026)

After ~6 months of building on a long-running graph, three temporal-organization types earned promotion to first-class status. They are additive: existing R/O/N/E/P/EQ/OQ/PR nodes need no migration, and a graph that doesn't use them is still well-formed.

The throughline is that the eight core types describe **claims** (facts, episodes, patterns, interpretations, intersections, bridges, questions, rules); the three temporal types describe **organization** of those claims across time. They earn their own types because their cardinality, ID-shape, and validation rules differ from references.

### `now` — the singleton orienting node

A single node, `id: NOW`, `type: now`, holding the graph's current orienting frame: this week, this month, this quarter, standing rules, canaries to watch for. First thing read when the graph opens. Prevents the *where do I start?* problem when a graph grows past ~50 nodes.

```yaml
- id: NOW
  type: now
  name: "NOW — current moves"
  statement: |
    Read this first. Everything else is context for what's in this node.
    Last updated: <date>.

    ## Frame
    <one-paragraph register of the current life stage>

    ## This week
    • <commitment with deadline>
    • <protected slot>

    ## This month
    • <decision due>

    ## This quarter
    • <forcing-function deadline>

    ## Standing rules
    • <protected practice>

    ## Canaries — watch for
    • <signal threshold> → <downstream cascade>
  said_by: "Self-articulated"
  said_when: "<YYYY-MM>"
  evidence_kind: self-report
  derives_from: []
  how_it_follows: "direct"
```

There is exactly one `NOW`. Updating its content updates `said_when`. Other nodes may `derives_from` `NOW` for short-horizon forecasts (1-month, 90-day) — the `NOW` content is the cadence variables those forecasts extrapolate from.

### `theme` (T-prefix) — cross-time organizing packet

A `theme` is a recurring shape of meaning that binds nodes from different *periods* by shared semantic content — what Roger Schank called a Thematic Organization Packet (TOP) in *Dynamic Memory* (1982). Unlike an `overlap` (which generalizes ≥2 independent observations into one pattern), a theme **does not generalize** — it points at a constellation of nodes across time and says *these belong to the same long-running thread*. Themes are the substrate the same person re-encounters in different decades and recognizes as one continuous concern.

```yaml
- id: T-01-relationship-as-mirror
  type: theme
  name: "Relationship-as-mirror — the theme"
  statement: |
    A long-running thread: relationships across multiple lifetime
    periods (L-01 college years, L-03 first marriage, L-05 post-
    divorce dating) function for me primarily as mirrors I read
    myself in, and only secondarily as encounters with another
    person. The theme is not a pattern I've earned by induction;
    it's a constellation I recognize across times.
  members:                            # ≥3 cross-period instances
    - O11-college-roommate-conversation
    - O12-first-anniversary-surprise
    - O13-second-date-after-divorce
  said_by: "Surfaced May 2026"
  said_when: "2026-05"
  evidence_kind: pattern-across-cases
  evidence_notes: "Theme recognized across lifetime periods, not derived"
  evidence_refs: [O11-..., O12-..., O13-...]
  derives_from: [L-01-college, L-03-marriage, L-05-post-divorce]
  how_it_follows: "thematic recognition across periods (Schank TOP)"
```

**Rules:**

- A theme that binds fewer than three cross-period instances is just a label, not a theme. Promote with restraint.
- A theme is not a pattern; do not extract an `implication`. The point is recognition, not prediction.
- `members:` enumerates the constituent nodes; `derives_from` lists the periods spanned.

### `period` (L-prefix) — lifetime period container

A `period` is a named lifetime span with a start, an end, and a tone — what Martin Conway calls a *lifetime period* in his Self-Memory System (Conway 2005). Periods are containers: nodes representing observations and patterns within a stretch of life live inside a period. Roughly 6–10 periods cover a life; more is too granular, fewer is too coarse.

```yaml
- id: L-03-first-marriage
  type: period
  name: "First marriage (2008–2019)"
  span: [2008, 2019]
  tone: "ascendant-then-attenuating"   # one-phrase register of the period
  statement: |
    Eleven years. Married Daniel summer 2008; daughter born 2011;
    moved Brooklyn 2014; divorce finalized 2019. The arc moves
    from generative to attenuating across roughly two halves;
    the household stayed legible from outside throughout but the
    inside register changed in 2014.
  contains:                            # nodes whose timeframe falls inside
    - O08-wedding
    - O09-daughter-born
    - O10-brooklyn-move
    - O14-divorce-finalized
  said_by: "Self-articulated"
  said_when: "2026-05"
  evidence_kind: self-report
  derives_from: []
  how_it_follows: "lifetime-period demarcation (Conway SMS)"
```

**Rules:**

- Periods do not overlap. Each named span has a clean start and end; transitional events (the move, the diagnosis, the divorce) belong to one side.
- A `tone:` field — one short phrase — names the period's register. Not a summary, not a verdict; a register-handle.
- `contains:` is the inverse of an observation's implicit period membership. Optional but recommended when the period spans many nodes.
- An observation that falls between two periods (a transition event) is allowed to be `contains:`'d by both, only if the event is genuinely the transition.

### Why these earned their own types instead of more reference sub-categories

Periods and themes have **different cardinality** than references (a life has ~6–10 periods, not dozens), **different referential semantics** (`contains` and `members` are not `derives_from`), and **different validation rules** (themes need ≥3 cross-period bindings; periods must not overlap). A reference sub-category prefix can't express those constraints. The pattern from April's "use prefixes, not new types" rule still holds for *role-flavors of references* — but temporal organization is structurally a different shape, not a flavor.

> **Claim:** `now`, `theme`, and `period` are first-class node types because their cardinality, referential semantics, and validation rules differ from references.
> **Grounds:** Cited cognitive-science substrates (Schank's TOP for theme; Conway's Self-Memory System for period; the *NOW* singleton's empirical role as graph orienting frame); structural arguments above.
> **Status:** stipulated (introduced May 2026 after ~6 months of long-running graph use)
> **Leans on:** DEPRECATION.md (the rule: extend types only when prefixes won't work); the validation-rules section below for the well-formedness conditions.

---

## Optional fields (added Apr–May 2026) — `genre`, `effort`, `warrant`, `revisions`, `handling`, `source_kind`

OPTIONAL. Core schema works without them. Add only on nodes where they help.

### `genre:` and `effort:` — distinguish passing thoughts from deliberate investigation

Distinguishes passing thoughts from deliberate investigation:

```yaml
genre: observation | speculation | log | analysis | prediction
effort: passing-thought | sustained | deliberate-investigation
```

**Recommended on every `novel`.** A passing-thought novel deserves different weight than an hour-long one — and novels are the type most prone to being treated as heavier than they are.

> **Claim:** Annotating effort prevents passing-thought novels being read as sustained investigations.
> **Grounds:** Observed failure mode — novels accreting unwarranted weight.
> **Status:** tentative
> **Leans on:** the novel node type's `tentative:` requirement; the caveats discipline.

### `warrant:` — the inferential leap from evidence to claim

The inferential leap from evidence to claim:

```yaml
warrant: |
  Why this evidence implies this claim. The assumption doing the work.
  If someone disagrees with the claim, they probably disagree here,
  not with the evidence.
```

Most useful on `overlap`, `novel`, `emergent`. Forces naming assumptions that were implicit.

> **Claim:** Surfacing the warrant exposes the assumption that bears the weight of disagreement.
> **Grounds:** Toulmin-style move; tracks how disagreements actually run.
> **Status:** stipulated
> **Leans on:** RELATED_FRAMEWORKS.md (Toulmin); overlap/novel/emergent as the load-bearing types.

### `revisions:` — log of truth-state changes

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

> **Claim:** A revisions log captures *belief* change, not edit history.
> **Grounds:** Discriminating example (typo vs. promotion); fields enumerated.
> **Status:** stipulated
> **Leans on:** the tentative/stable lifecycle for novels; the temporal-validity (`valid_at`) extension.

### `handling:` — structured form of the inline HANDLING directive

Structured form of inline HANDLING directive:

```yaml
handling: surface | quiet | do-not-raise-unprompted | archive
```

- `surface` — default; can be referenced freely.
- `quiet` — referenced but not proactively raised.
- `do-not-raise-unprompted` — only engage if user surfaces it.
- `archive` — structurally load-bearing, should not appear day-to-day.

Inline `HANDLING:` lines stay valid for human-read graphs. Structured `handling:` is preferred when a tool reads the graph.

> **Claim:** Four-value `handling` enum gives tools a machine-readable surface for the inline HANDLING discipline.
> **Grounds:** Enumeration plus rationale (tool-readable vs. human-only).
> **Status:** stipulated
> **Leans on:** the HANDLING extension below; SAFETY.md's caveats around sensitive content.

### `source_kind:` — distinguish lived from told from inferred from imagined

A four-value tag, applicable to any node type, that records *how the content reached the graph*:

```yaml
source_kind: lived | told | inferred | imagined
```

- `lived` — first-person re-experienced content. Tulving's autonoetic register: the graph-builder remembers being there.
- `told` — heard from someone else (family stories, third-party reports, historical accounts of one's own life that no living memory holds).
- `inferred` — pattern claims without a single experienced moment. The default for `overlap` and most `novel` nodes.
- `imagined` — counterfactual or speculative content not grounded in any actual episode. Useful for `novel` futures explicitly framed as not-yet-occurred.

Defaults: `lived` for `observation` nodes built from first-person memory; `told` for family-history references; `inferred` for pattern claims with no single experienced moment; `imagined` only when the node is explicitly counterfactual.

The distinction comes from Endel Tulving's *autonoetic consciousness* (the subjective sense of personally re-experiencing the past) and Marcia Johnson's *source monitoring* (the cognitive process of discriminating among origins of mental content). For a personal graph, conflating *I lived this* with *I was told this happened to me* is the failure that the tag exists to prevent.

> **Claim:** A four-value `source_kind` distinguishes the four origins of mental content that personal graphs blur if not tagged.
> **Grounds:** Tulving (1985) on autonoetic consciousness; Johnson (1993) on source monitoring; observed failure mode where told-by-family content collapses into lived register.
> **Status:** stipulated
> **Leans on:** RELATED_FRAMEWORKS.md (cognitive-science substrate); the `evidence` ladder (which tags claim *strength*, distinct from origin).

### `valid_at:` — temporal validity (when the claim was last grounded)

```yaml
valid_at: YYYY-MM-DD
# OR for less-precise grounding:
valid_at: YYYY-MM        # month-precision
valid_at: YYYY           # year-precision (range-grounded claims)
```

`valid_at` records **when the claim was last grounded** in lived experience. It overlaps semantically with `said_when` (the provenance attribution date) but answers a different question: not "when was this claim first stated?" but "when was the underlying experience last refreshed?" For freshly-disclosed claims they're the same date; for claims that have been re-grounded by later episodes, `valid_at` advances while `said_when` stays at the original disclosure.

The decay-without-regrounding posture: a personal claim's epistemic standing weakens as `valid_at` ages. New episodes refresh the claim; absence does not refresh. Rendering tools may surface "stale" nodes (those with old `valid_at`) for re-grounding review.

> **Claim:** `valid_at` is a temporal-validity stamp distinct from `said_when` (provenance-attribution date); it tracks lived-experience freshness, not disclosure history.
> **Grounds:** Personal claims aren't permanently true; the stamp lets a graph express "still grounded" vs "potentially stale" without forcing premature retraction.
> **Status:** stipulated
> **Leans on:** README.md's "valid_at decays unless re-grounded" framing; `said_when` (the provenance-fields foreground date).

---

## Extensions for personal memory — the seven deliberate departures from scientific-claims schemas

Personal memory operates under different constraints than scientific knowledge — no replication, no external ground truth, fuzzy temporal validity, node-dense rather than edge-dense growth as life events accumulate.

I make seven deliberate extensions beyond scientific-claims provenance schemas:

1. **`observation` as a first-class node type.** Scientific graphs treat events as evidence for propositions; personal graphs treat them as nodes because episodes get reinterpreted.

2. **Type-tier + `tentative:` + `caveats:` instead of numeric C₁ confidence.** No principled way to assign proof-strength numbers to personal claims. Narrative caveats are more honest than undefended numbers.

3. **HANDLING directives** for sensitive content. Scientific nodes don't need operational handling; personal ones do.

4. **`natural-experiment` as an evidence type.** Same person, different environment, different outcome — strongest evidence available in a personal graph, no clean analog in scientific schemas.

5. **Open questions as systematic first-class nodes** with provenance. In personal graphs, open questions get silently absorbed into confident answers if not structurally protected.

6. **Repurposed `equivalency`** from cross-framework alignment to external-theory bridges. Personal graphs don't have multiple internal frameworks; they may have external bridges worth naming.

7. **`practice` as an eighth node type.** Personal graphs accumulate operating rules. These are normative, not descriptive, but belong in the graph when they `derive_from` descriptive claims — traceability from "this is the pattern" to "therefore this is the rule." A practice with no descriptive grounding belongs in goals.md, not here.

> **Claim:** Seven deliberate extensions adapt the scientific-claims provenance shape to the constraints of personal memory.
> **Grounds:** Enumerated, each tied to a specific constraint (no replication, no ground truth, fuzzy validity, node-dense growth).
> **Status:** stipulated
> **Leans on:** README.md's "what's different"; each extension's corresponding schema element above.

---

## Personal-graph reserved fields — fields the schema permits but doesn't require

Long-running personal graphs accumulate fields beyond the seven provenance fields. These have emerged from real use; the schema reserves them so a personal graph using them is still well-formed. Tools may render or ignore them.

### Lifecycle (graph hygiene over time)

```yaml
shelved: true                          # node demoted but kept for reference
shelved_on: "YYYY-MM-DD"               # when shelved
retire_note: "Why this is shelved..."  # short prose explaining the demotion
```

Shelving is the soft form of node retirement — the node stays referenced from history but is excluded from "live" views. Use when a claim turns out to be wrong, or a stretch ends, or a frame retires.

### Associative graph (relationships not captured by typed edges)

```yaml
related_to:
  - <node-id>      # associative; lighter than a typed edge
  - <node-id>
```

`related_to` lets a graph express "see also" associations that don't fit one of the eight typed edge predicates. Render tools should treat `related_to` entries as undirected, untyped associations. (For directed, typed claim-relationships, use the `edges` block.)

### Free-text grounding (prose evidence not yet extracted to nodes)

```yaml
grounded_by:
  - <node-id>          # if the grounding is a real node, list it here
  - "Episode prose..." # if it isn't yet extracted, prose works as a placeholder
```

`grounded_by` is the field for "this claim's evidence" in mixed shape: node-IDs where evidence is structured, prose where it hasn't been extracted yet. Cleaner long-term: extract prose entries into observation nodes, link via `evidence_refs`. `grounded_by` is the working surface during graph construction.

### Forecast and review scheduling

```yaml
review_cadence: weekly | monthly | quarterly | yearly
next_review: "YYYY-MM-DD"
review_by: "Self" | "<other party>"
```

Useful on `emergent` forecast nodes — formal recurrence reminder.

### Watch and counter-evidence

```yaml
watchpoints:
  - "Specific signal that would falsify or qualify this claim"

counter_evidence:
  - <node-id>          # observation that runs against the pattern
  - "Prose about counter-evidence"
```

`watchpoints` is the falsifier-watch list. `counter_evidence` is the explicit counter — the schema's `contradicts` typed edge does the same job structurally; `counter_evidence` is the human-friendly inline form.

### Practice extensions

```yaml
governs:
  - <domain or node-id>    # what the practice governs
```

### Period extensions

```yaml
sample_residents:
  - <node-id>             # a sampling of nodes whose timeframe falls inside the period
themes:
  - <theme-id>             # themes this period intersects
```

`sample_residents` is the lighter form of `contains:` — when listing every node-in-period would be too many, list a representative sample.

### Source caveat (evidence-quality narrative)

```yaml
source_caveat: "Evidence-source caveat as a short prose hint."
```

This overlaps with `evidence_notes` in the provenance fields. Personal graphs may keep both during transition; new authoring should prefer `evidence_notes`.

### Partial grounding

```yaml
grounded_by_partial:
  - <node-id>             # grounded but acknowledged as incomplete
```

For nodes that are partially grounded — the link is real but doesn't carry the full weight of evidence_refs.

> **Claim:** Personal-graph reserved fields document the working surfaces a long-running graph accumulates; tools may render or ignore them.
> **Grounds:** Empirical — fields surfaced after months of personal-graph use; each ties to a specific operational need (lifecycle, associative graph, prose-staging, scheduled review, falsifier-watch, period-sampling, evidence-quality narrative).
> **Status:** stipulated
> **Leans on:** the seven required provenance fields above (these reserved fields complement, do not replace); render tools that read these fields (dashboards, audit reports).

---

## Credit — provenance lineage of this spec

Provenance-triple shape from W3C [RDF](https://www.w3.org/TR/rdf11-concepts/) (2004) and [PROV-O](https://www.w3.org/TR/prov-overview/) (2013). Patrick McCarthy's [open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph) (MIT) gives the formal articulation for the **scientific** case. The personal-graph schema above — typed nodes adapted to personal life, four-scale synthesis, `valid_at` temporal validity, MCP retrieval — is mine.

> **Claim:** The provenance-triple shape is borrowed from W3C standards; the personal-graph extensions on top are original.
> **Grounds:** Cited W3C standards; cited McCarthy repo; explicit boundary between borrowed shape and new extensions.
> **Status:** established (cited prior art); stipulated (boundary)
> **Leans on:** README.md's Credit section; RELATED_FRAMEWORKS.md.
