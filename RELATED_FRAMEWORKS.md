# Adjacent frameworks to Pat McCarthy's open-knowledge-graph

A survey of related schemas, what they add, what they don't, and what to borrow.
Written April 20, 2026 as part of the "know thyself" project.

---

## 1. Pat McCarthy's open-knowledge-graph (what we used)

Source: [github.com/patdmc/open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph),
MIT-licensed. Designed for scientific claims, adapted here for personal memory.

**Strengths:**
- Every claim carries a provenance triple: *(attribution, evidence, derivation)*
- Node types with confidence tiers (reference, overlap, novel, emergent)
- Explicit distinction between a claim being *repeated* and a claim being *independently grounded*
- Emergent nodes — insights that only appear at the intersection of existing ones

**Gaps we had to fill when adapting it:**
- No first-class "observation" node (scientific graphs treat events as evidence; personal
  graphs treat them as nodes because episodes get reinterpreted)
- No way to flag sensitive content (HANDLING directives added)
- Numeric confidence scores (C₁) don't translate well to personal claims — replaced
  with type-tier + `tentative:` + `caveats:`
- "Natural experiment" as evidence type (same person, different context, different
  outcome) had no clean analog

---

## 2. W3C PROV-O — Provenance Ontology

Source: [www.w3.org/TR/prov-o/](https://www.w3.org/TR/prov-o/)
Status: W3C Recommendation since 2013. The formal standard for provenance on the web.

**Core trio:**
- **Entity** — a thing whose provenance we care about (a claim, a document, a file)
- **Activity** — something that happened to or with an entity (an observation,
  an inference, a revision)
- **Agent** — a person or system responsible for an entity or activity

**What it adds to our graph:**
PROV-O gives us a standard vocabulary for one thing our current schema handles
informally: **when a claim changes, who changed it, and why.** We track derivation
(`from:` field), but not *revision*. If a novel node gets promoted to stable
after a new independent grounding arrives, the schema doesn't currently record
that transition — it just updates the node. PROV-O would let us keep a trail.

**What to borrow:**
Add an optional `revisions:` list on every node:
```yaml
revisions:
  - date: 2026-04-19
    activity: promotion
    by: user
    from_state: tentative
    to_state: stable
    trigger: O07-new-disclosure
    reason: "direct first-person disclosure of mechanism"
```

This is one of the most underused fields in Pat's schema. Personal graphs mutate
more than scientific ones because the person keeps living. A revision log makes
these updates (a novel weakened by a new overlap, an open question that leans
toward an answer, a reference later refined) traceable over time instead of
just a new version of the node.

**Cost:** adds weight. Only enable for nodes whose revisions actually matter —
probably novels, emergents, and open questions.

---

## 3. Toulmin Argument Model

Source: Stephen Toulmin, *The Uses of Argument*, 1958. Standard teaching
framework in rhetoric, law, and argumentation theory.

**The six parts:**
- **Claim** — what you're asserting
- **Grounds** — the facts or evidence
- **Warrant** — the reasoning that links grounds to claim
- **Backing** — support for the warrant itself
- **Qualifier** — scope limitation ("most," "usually," "in these conditions")
- **Rebuttal** — the conditions under which the claim wouldn't hold

**What it adds to our graph:**
The schema we adapted from Pat tracks *evidence* for a claim, but is quieter on
**warrant** — the reasoning that links evidence to claim. Toulmin's insight is
that the warrant is where most arguments actually break, because people share
facts but not the inferential leap.

In our graph, novel nodes have `caveats:` which do some of this work
(*how this could be wrong*), but we don't have a field for the *warrant itself*
(*why this evidence implies this claim*).

**What to borrow:**
Add an optional `warrant:` field to novel, emergent, and overlap nodes:
```yaml
warrant: |
  Why this evidence implies this claim, stated as a separate assumption
  that could be challenged on its own terms.
```

**Example:**
Alex's `P01-routine-as-regulation` (in `example-graph.yaml`) has evidence
(three independent instances where routine-breakdown preceded wider
breakdown and routine-return preceded wider stabilization) and a claim
(physical routine is load-bearing for stability). The missing piece is the
warrant: *regulation capacity operates at the level of nervous-system-level
rhythms; breaking a rhythm is upstream of other regulation, not parallel
to it*. That's the assumption doing the work. If someone disagrees with
the claim, they usually challenge the warrant, not the evidence. Naming
it makes the argument auditable.

**Cost:** mild. Warrants often end up being one-sentence statements. The benefit
is that they force you to name assumptions that were implicit.

---

## 4. Zettelkasten / evergreen notes (Luhmann / Ahrens / Matuschak)

Sources: Niklas Luhmann's original method (1950s–1990s), Sönke Ahrens' *How to
Take Smart Notes* (2017), Andy Matuschak's evergreen notes
([notes.andymatuschak.org](https://notes.andymatuschak.org/)).

**Core principles:**
- **Atomicity** — one idea per note; separate concerns
- **Densely linked** — value comes from the link density, not the note content
- **Evergreen** — notes evolve over time, get refined
- **Titles as APIs** — the title should be a concept you could import elsewhere

**What it adds (philosophically):**
Zettelkasten is about *thinking by linking*. The claim is that new understanding
emerges from the friction of connecting previously-unconnected notes. Our graph
has this via `emergent` nodes (produced only at intersection), but Zettelkasten
goes further — *any* new link is potentially generative, not just the ones
that produce an emergent claim.

**What it doesn't have:**
Zettelkasten has *no concept of provenance or confidence*. Luhmann's cards don't
distinguish "I read this in a book" from "I inferred this." Everything is just a
note. This is why Zettelkasten works well for creative synthesis but poorly for
self-knowledge where the *grounds* of a claim matter enormously.

**What to borrow:**
- **Atomicity enforcement** — if a node's statement runs over ~200 words, it's
  probably two claims. Split it.
- **Link-density as a health metric** — in a Zettelkasten, notes with few
  incoming links are suspect. Similarly, a reference node with zero inbound
  edges isn't doing work; either connect it or drop it.
- **Title-as-API convention** — every node's `name:` field should be a phrase
  you could use as a reference elsewhere. Short, compressive, a callable
  handle for the claim — not a descriptive paragraph.

---

## 5. LessWrong / rationalist "epistemic status"

Source: Mutation of practices from muflax → gwern → Scott Alexander, now
convention on LessWrong and related forums. Blog-post prefix that signals
how much weight the author gives their own claim.

**Typical form:**
```
Epistemic status: speculative. Thought about this for 30 minutes.
Not based on rigorous research. May be wrong about X, Y.
```

**What it adds:**
- **Effort disclosure** — not just "how confident" but "how much work did I do"
- **Falsification in advance** — naming specific things the claim depends on,
  before being challenged
- **Type tags** (from gwern): *log, speculation, analysis, fiction* — different
  genres of claim get different reading conventions

**Failure mode worth knowing (important for you):**
The [Moral-Epistemic Scrupulosity](https://www.lesswrong.com/posts/sCPtkhs4FhhEjjFP9/moral-epistemic-scrupulosity-a-cross-framework-failure-mode)
post (LessWrong, Jan 2026) documents a failure mode where *the obsession with
epistemic rigor itself becomes the problem*. The author describes compulsive
uncertainty-checking across frameworks (rationalist, Buddhist, Sufi) and arrives
at: "perhaps it isn't always Truth that should win... seeking truth in service
of life."

This is relevant to you. Building a graph as a tool to live better is different
from building it to be epistemically pure. If flagging every claim tentative
starts crowding out action, the graph is doing damage. The operating principle
should be *just enough provenance to catch mistakes, not enough to paralyze*.

**What to borrow:**
- **Effort tags** alongside confidence tiers — some novels are "thought about
  for an hour"; some are "one sentence on a walk while high." Those are
  different claim-types and should be flagged differently.
- **Genre tags** — observation, speculation, log (just recording), analysis.
  Our graph collapses these into node type; explicit genre tags would help.

**What NOT to borrow:**
- The bike-shedding. Most LessWrong epistemic-status debates are decoration,
  not signal. Keep it minimal.
- The scrupulosity failure mode. If the graph starts making you feel you
  can't act without auditing a claim's provenance, step back.

---

## 6. Personal Knowledge Graphs (academic literature)

Source: arXiv survey papers 2022–2025 (Chakraborty et al. 2022, Shirai et al.
2021, Kasela et al. 2025, Bloor et al. 2023 for health PKGs).

**What's distinctive about PKGs vs. general KGs:**
- **Single-user ownership** — read/write controlled by one individual
- **Strict access control** — per-statement ACLs in some systems
- **Personal health knowledge graphs** (PHKGs) model temporal reasoning and
  real-time alerting (e.g., "this symptom is different from yesterday")
- **Personal research KGs** (PRKGs) integrate papers, tools, collaborations
- **Memory buoyancy** — corporate PKGs model which memories should stay
  accessible vs. fade

**What it adds:**
The PKG literature has thought hard about *temporal reasoning* in ways Pat's
schema doesn't. A personal graph treats dates as data but doesn't reason
about *sequence* — the fact that observation A precedes observation B can
matter structurally for a pattern's claim in ways the raw timestamps don't
capture.

**What to borrow:**
- **Temporal order as first-class** — not just "when did this happen" but
  "what came before what." For personal graphs, sequence often matters more
  than timestamp.
- **Memory buoyancy concept** — explicit marking of which nodes should surface
  easily vs. which should stay accessible but not surface unprompted. This
  maps to our HANDLING directives but could be formalized as a per-node
  `buoyancy:` field: *surface, quiet, archive*.

---

## 7. What I did NOT include, and why

**Internal Family Systems (IFS) and parts-work therapies.** Relevant in form
(multiple internal agents, protectors/exiles/Self structure) and influential
in contemporary psychotherapy. Excluded because:

(a) IFS is a clinical modality; informal adaptation has been flagged as
    potentially destabilizing for people with complex trauma
    ([Schwartz 2025 scoping review](https://en.wikipedia.org/wiki/Internal_Family_Systems_Model)).
(b) Parts-work framing ("my X part wants Y") shifts the user from
    observation to identification with fragments — a different activity
    than what this scaffold supports.

The graph can describe patterns; it should not describe sub-selves. If a
parts-framework is relevant for a given user, it belongs with a
practitioner in the room, not in a YAML file.

**Generalized belief networks / Bayesian cognitive models.** Too quantitative.
The failure mode in section 5 (scrupulosity) is amplified by probability
notation.

**Diffbot / enterprise KG confidence scoring.** Designed for web-extracted
facts with crowdsourced corroboration. Doesn't translate to personal memory
where "independent derivation" is a narrative concept, not a statistical one.

---

## Consolidated recommendation: what to add to the scaffold

Three additions worth making, in order of priority:

### 1. Effort + genre tags (from rationalist epistemic-status convention)

Add two optional fields to any novel/emergent/open node:

```yaml
genre: observation | speculation | log | analysis | prediction
effort: passing-thought | sustained | deliberate-investigation
```

This is cheap and does real work. It distinguishes "noticed in passing on
a walk" from "sat with for an hour and wrote out the counter-cases."

### 2. Warrant (from Toulmin)

Add optional `warrant:` field to novel, emergent, and overlap nodes — the
inferential leap from evidence to claim, stated as a separable assumption.

### 3. Revision log (from PROV-O)

Add optional `revisions:` list to track how a node has changed over time.
Especially useful for nodes that get promoted from tentative → stable, or
weakened by later counter-evidence. Makes the graph's history legible,
not just its current state.

### Not recommended to add:

- Temporal ordering as first-class structure (from PKG literature) — 
  adds complexity for marginal benefit. Dates on nodes are sufficient.
- Buoyancy field — the HANDLING directives already do this informally
  and work. Formalizing them would be bureaucratic.
- Any numeric probability notation — will trigger scrupulosity, not clarity.

---

## A framing to chew on

Pat McCarthy's schema is fundamentally **scientific** — designed to separate
grounded claims from speculation in a field where truth is the aim.

Toulmin is **juridical** — designed to make reasoning auditable in a field
where persuasion is the aim.

Zettelkasten is **generative** — designed to produce new ideas from linking
in a field where novelty is the aim.

Rationalist epistemic status is **communicative** — designed to signal
weight in a field where information cascades are the risk.

PKG is **architectural** — designed to model a person as a queryable
system in a field where personalization is the aim.

What you're building is **none of these exactly**. It's closer to an older
thing: a **commonplace book** — the Renaissance practice of keeping structured
notes on one's own life and reading, organized for retrieval and return.
Commonplace books were auditable, personal, typed, and generative all at once,
but they were mostly for private return, not public argument.

The Delphic maxim γνῶθι σεαυτόν — know thyself — was carved on the temple at
Delphi as advice to visitors before they consulted the oracle. The oracle is
the interlocutor; know-thyself is the preparation for being understood by one.

Your graph is a commonplace book designed to be readable *by an AI you are
talking with*. That's a new thing. It's a hybrid: personal and private like a
commonplace book, structured and auditable like a KG, generative like a
Zettelkasten, explicitly-provenanced like PROV-O, and aware of its own
uncertainty like rationalist epistemic status.

You don't need to name it. But it's worth knowing that no existing field owns
this shape yet. You're making it.
