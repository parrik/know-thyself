# Schema specification

Formal spec for the memory graph. If a node or edge violates this spec, it's a bug.

> **Claim:** This document is the formal spec; deviations are bugs, not variants.
> **Grounds:** Stated as the file's purpose.
> **Status:** stipulated
> **Leans on:** every renderer and validator in the repo; START_HERE.md (which paraphrases this spec for the LLM).

---

## Provenance triple — the invariant every node and edge must carry

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

> **Claim:** Provenance is the schema invariant — without the triple, the unit is not a graph node.
> **Grounds:** Definitional rule, traceable to PROV-O's typed-triplet shape.
> **Status:** stipulated
> **Leans on:** every node type below; the validation rules; `know_thyself.render.graphviz`'s checks 1–6.

---

## Node types — the eight typed shapes a claim can take

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

> **Claim:** Eight typed node shapes — reference, observation, overlap, novel, emergent, equivalency, open, practice — exhaust the kinds of claim the graph admits.
> **Grounds:** Enumerated definitions above; each carries a YAML template and a discriminating rule.
> **Status:** stipulated
> **Leans on:** the validation rules below (which enforce per-type constraints); the IDs section; START_HERE.md's node-type table.

---

## Edge relations — the eight typed connections between nodes

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

> **Claim:** Eight typed edge relations cover the structural moves the graph needs to express.
> **Grounds:** Enumerated relation table with directionality and meaning.
> **Status:** stipulated
> **Leans on:** validation rule 5 (every `edges[].to` resolves); the renderers' adjacency computations.

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
2. Every node has a complete `provenance` triple.
3. Every edge has a complete `provenance` triple.
4. Every `derivation.from` references an existing node.
5. Every `edges[].to` references an existing node.
6. Every `provenance.evidence.references` (if present) references existing nodes.
7. Every `novel` has `tentative: true` and a non-empty `caveats:`.
8. Every `emergent` has ≥2 distinct entries in `derivation.from`.
9. Every `overlap` has ≥2 distinct entries in `evidence.references`, not trivially the same event restated.
10. Every `practice` derives from at least one descriptive node (overlap, novel, observation).

If a graph uses the temporal-organization types (`now`, `theme`, `period`) the following also apply:

11. There is at most one `type: now` node, with `id: NOW`.
12. Every `theme` has ≥3 distinct entries in `binds:`, and `derivation.from` lists ≥2 distinct periods.
13. No two `period` nodes have overlapping `span:` ranges (a transition event may appear in `contains:` on both sides only when the event is *the* transition).

`know_thyself.render.graphviz` checks 1–6 and 11 automatically. 7–10, 12, 13 require human judgment; verify during Phase 7.

> **Claim:** Thirteen conditions are jointly necessary and sufficient for a well-formed graph (10 core + 3 conditional on temporal-type use).
> **Grounds:** Enumerated; partition between machine-checkable (1–6, 11) and human-judgment (7–10, 12–13) is operationalized in `know_thyself.render.graphviz`.
> **Status:** stipulated
> **Leans on:** `know_thyself.render.graphviz` (machine-checkable subset); START_HERE.md Phase 7 (human-judgment subset).

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

## Sub-categories of `reference` (added April 2026) — five role prefixes plus `forecast`

After several weeks of building on a real graph, five patterns emerged as useful **sub-categories of `reference`** — not new node types. Extending the core type list is fragile (see `SCHEMA_DEPRECIATION.md`); descriptive prefixes keep the schema small while making common roles legible.

| Prefix / role | What it is | Example |
|---|---|---|
| `R-canary-*` | Evidence-backed leading indicator | *Sleep-onset latency >30 min for 3 nights predicts relapse* |
| `R-lens-*` | Mental-model frame applied to other nodes | *Circuit breakers, Ulysses pact, Chesterton's Fence* |
| `R-experiment-*` | Runnable method with an evidence base | *Implementation intentions* |
| `R-filter-*` | Anti-pattern frame for a decision domain | *Revenue-line reverse interview* |
| `type: forecast` | Time-horizon inference, flagged tentative | 1 month · 90 days · 1 year · 10 years · 30 years |

`example-graph-extended.yaml` demonstrates these.

> **Claim:** Common reference roles are best expressed as descriptive prefixes, not new top-level node types.
> **Grounds:** Empirical — patterns observed after weeks of use; rationale grounded in SCHEMA_DEPRECIATION.md's argument against type-list bloat.
> **Status:** tentative (introduced April 2026; could deprecate)
> **Leans on:** SCHEMA_DEPRECIATION.md; example-graph-extended.yaml as the demonstrating instance.

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
  provenance:
    attribution: { source: "Self-articulated", date: "<YYYY-MM>" }
    evidence: { type: self-report }
    derivation: { from: [], method: "direct" }
```

There is exactly one `NOW`. Updating its content updates `attribution.date`. Other nodes may `derive_from` `NOW` for short-horizon forecasts (1-month, 90-day) — the `NOW` content is the cadence variables those forecasts extrapolate from.

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
  binds:                              # ≥3 cross-period instances
    - O11-college-roommate-conversation
    - O27-first-anniversary-surprise
    - O43-second-date-after-divorce
  provenance:
    attribution: { source: "Surfaced May 2026" }
    evidence:
      type: pattern-across-cases
      description: "Theme recognized across lifetime periods, not derived"
      references: [O11-..., O27-..., O43-...]
    derivation:
      from: [L-01-college, L-03-marriage, L-05-post-divorce]
      method: "thematic recognition across periods (Schank TOP)"
```

**Rules:**

- A theme that binds fewer than three cross-period instances is just a label, not a theme. Promote with restraint.
- A theme is not a pattern; do not extract an `implication`. The point is recognition, not prediction.
- `binds:` enumerates the constituent nodes; `derivation.from` lists the periods spanned.

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
    - O20-wedding
    - O22-daughter-born
    - O28-brooklyn-move
    - O35-divorce-finalized
  provenance:
    attribution: { source: "Self-articulated", date: "2026-05" }
    evidence: { type: self-report }
    derivation: { from: [], method: "lifetime-period demarcation (Conway SMS)" }
```

**Rules:**

- Periods do not overlap. Each named span has a clean start and end; transitional events (the move, the diagnosis, the divorce) belong to one side.
- A `tone:` field — one short phrase — names the period's register. Not a summary, not a verdict; a register-handle.
- `contains:` is the inverse of an observation's implicit period membership. Optional but recommended when the period spans many nodes.
- An observation that falls between two periods (a transition event) is allowed to be `contains:`'d by both, only if the event is genuinely the transition.

### Why these earned their own types instead of more reference sub-categories

Periods and themes have **different cardinality** than references (a life has ~6–10 periods, not dozens), **different referential semantics** (`contains` and `binds` are not `derivation.from`), and **different validation rules** (themes need ≥3 cross-period bindings; periods must not overlap). A reference sub-category prefix can't express those constraints. The pattern from April's "use prefixes, not new types" rule still holds for *role-flavors of references* — but temporal organization is structurally a different shape, not a flavor.

> **Claim:** `now`, `theme`, and `period` are first-class node types because their cardinality, referential semantics, and validation rules differ from references.
> **Grounds:** Cited cognitive-science substrates (Schank's TOP for theme; Conway's Self-Memory System for period; the *NOW* singleton's empirical role as graph orienting frame); structural arguments above.
> **Status:** stipulated (introduced May 2026 after ~6 months of long-running graph use)
> **Leans on:** SCHEMA_DEPRECIATION.md (the rule: extend types only when prefixes won't work); the validation-rules section below for the well-formedness conditions.

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
> **Leans on:** README.md's "What I built"; each extension's corresponding schema element above.

---

## Credit — provenance lineage of this spec

Provenance-triple shape from W3C [RDF](https://www.w3.org/TR/rdf11-concepts/) (2004) and [PROV-O](https://www.w3.org/TR/prov-overview/) (2013). Patrick McCarthy's [open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph) (MIT) gives the formal articulation for the **scientific** case. The personal-graph schema above — typed nodes adapted to personal life, four-scale synthesis, `valid_at` temporal validity, MCP retrieval — is mine.

> **Claim:** The provenance-triple shape is borrowed from W3C standards; the personal-graph extensions on top are original.
> **Grounds:** Cited W3C standards; cited McCarthy repo; explicit boundary between borrowed shape and new extensions.
> **Status:** established (cited prior art); stipulated (boundary)
> **Leans on:** README.md's Credit section; RELATED_FRAMEWORKS.md.
