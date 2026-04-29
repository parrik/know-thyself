# Adjacent frameworks

What this scaffold borrows from, what it doesn't, what's worth knowing.

---

## 1. Pat McCarthy's open-knowledge-graph (the starting point)

Designed for **scientific** claims, with formal necessity arguments. I adapted the provenance-triple shape here for personal memory; the personal-graph schema is mine. MIT-licensed.

**Strengths:**
- Provenance triple: *(attribution, evidence, derivation)* on every claim.
- Node types with confidence tiers: reference, overlap, novel, emergent.
- Distinguishes a claim *repeated* from a claim *independently grounded*.
- Emergent nodes — insights that only appear at the intersection of others.

**Gaps when adapting to personal memory:**
- No first-class observation node. Scientific graphs treat events as evidence; personal graphs reinterpret episodes, so the episode itself needs to be a node.
- No way to flag sensitive content. Added HANDLING directives.
- Numeric confidence (C₁) doesn't translate. Replaced with type-tier + `tentative:` + `caveats:`.
- No `natural-experiment` evidence type. Added — same person, different context, different outcome is the strongest evidence available in a personal graph.

---

## 2. W3C PROV-O — Provenance Ontology

The formal web standard for provenance since 2013.

**Core trio:** Entity (a thing whose provenance matters), Activity (something that happened to it), Agent (responsible party).

**What it adds:** when a claim *changes*, who changed it, why. We track derivation; we don't track *revision*. If a novel gets promoted to stable after new grounding, the schema currently just updates the node.

**Borrowed:** optional `revisions:` list per node.

```yaml
revisions:
  - date: 2026-04-19
    activity: promotion
    from_state: tentative
    to_state: stable
    trigger: O07-new-disclosure
    reason: "direct first-person disclosure of mechanism"
```

Personal graphs mutate more than scientific ones — the person keeps living. Revision logs make those updates traceable instead of overwritten.

**Cost:** weight. Enable only on novels, emergents, and open questions.

---

## 3. Toulmin Argument Model

Standard rhetoric/law/argumentation framework (1958).

**The six parts:** claim, grounds, warrant, backing, qualifier, rebuttal.

**What it adds:** the **warrant** — the reasoning that links grounds to claim. Most arguments break here, not at the evidence. People share facts; they don't share the inferential leap.

McCarthy's schema is quiet on warrants. Novel `caveats:` partly cover *how this could be wrong*; warrants cover *why this evidence implies this claim*.

**Borrowed:** optional `warrant:` field on novel, emergent, and overlap nodes.

```yaml
warrant: |
  Why this evidence implies this claim, stated as a separate
  assumption that could be challenged on its own terms.
```

**Example.** A pattern says: *physical routine is load-bearing for stability* (three independent instances). The missing piece is *regulation capacity operates at the level of nervous-system rhythms; breaking rhythm is upstream of other regulation, not parallel to it*. That's the warrant. Disagreement usually lives there, not at the evidence.

---

## 4. Zettelkasten / evergreen notes (Luhmann / Ahrens / Matuschak)

**Principles:** atomicity (one idea per note), dense linking, evergreen evolution, titles-as-APIs.

**What it adds philosophically:** *thinking by linking* — new understanding emerges from connecting previously-unconnected notes. We have this via emergent nodes; Zettelkasten goes further: any new link is potentially generative.

**What it lacks:** any concept of provenance or confidence. Luhmann's cards don't distinguish "I read this" from "I inferred this." This is why Zettelkasten works for creative synthesis but poorly for self-knowledge where the *grounds* of a claim matter.

**Borrowed:**
- **Atomicity** — if a node statement runs over ~200 words, it's probably two claims. Split.
- **Link-density as a health metric** — a reference node with zero inbound edges isn't doing work. Connect or drop.
- **Title-as-API** — every node `name:` should be a callable handle, not a paragraph.

---

## 5. LessWrong / rationalist "epistemic status"

Blog-post prefix that signals how much weight the author gives their own claim. Convention from muflax → gwern → Scott Alexander.

**What it adds:**
- **Effort disclosure** — not just confidence but how much work was done.
- **Falsification in advance** — naming what the claim depends on, before challenge.
- **Genre tags** — log, speculation, analysis, fiction get different reading conventions.

**Failure mode worth knowing.** The [Moral-Epistemic Scrupulosity](https://www.lesswrong.com/posts/sCPtkhs4FhhEjjFP9/moral-epistemic-scrupulosity-a-cross-framework-failure-mode) post documents a state where epistemic-rigor obsession itself becomes the problem. Compulsive uncertainty-checking that eats action.

This matters here. Building a graph as a tool to *live better* differs from building it to be epistemically pure. If flagging every claim tentative crowds out action, the graph is doing damage. The principle: *just enough provenance to catch mistakes, not enough to paralyze*.

**Borrowed:**
- **Effort tags** alongside confidence tiers.
- **Genre tags** — observation, speculation, log, analysis, prediction.

**Not borrowed:** the bike-shedding (most epistemic-status debates are decoration), and the scrupulosity itself.

---

## 6. Personal Knowledge Graphs (academic literature)

Survey papers 2022–2025 (Chakraborty, Shirai, Kasela, Bloor).

**Distinctive vs. general KGs:**
- Single-user ownership, strict access control.
- Personal Health KGs do temporal reasoning ("this symptom is different from yesterday").
- Memory buoyancy — which memories should stay accessible vs. fade.

**What it adds:** *temporal reasoning*. Sequence (A precedes B) often matters structurally for a pattern's claim in ways raw timestamps don't capture.

**Considered but not borrowed:**
- Temporal ordering as first-class structure — adds complexity for marginal benefit.
- Buoyancy field — HANDLING already does this informally; formalizing would be bureaucratic.

---

## 7. NOT included, and why

**Internal Family Systems (IFS) / parts work.** Influential in psychotherapy. Excluded because (a) IFS is a clinical modality; informal adaptation has been flagged as potentially destabilizing for complex trauma, and (b) parts framing ("my X part wants Y") shifts users from observation to identification with fragments — different activity than this scaffold supports. The graph describes patterns; it should not describe sub-selves.

**Bayesian belief networks / generalized cognitive models.** Too quantitative. Amplifies the scrupulosity failure mode.

**Diffbot / enterprise KG confidence scoring.** Designed for crowdsourced web extraction. "Independent derivation" in a personal graph is a narrative concept, not statistical.

---

## What got added to the scaffold

In priority order:

1. **`genre:` + `effort:` tags** — cheap, real work. Distinguishes "noticed in passing" from "sat with for an hour."
2. **`warrant:`** — names the inferential leap as a separable assumption.
3. **`revisions:`** — tracks how a node's truth-state changes over time.

Not added: temporal ordering, buoyancy, numeric probability.

---

## A framing

McCarthy's schema is **scientific** — separating grounded claims from speculation where truth is the aim.

Toulmin is **juridical** — making reasoning auditable where persuasion is the aim.

Zettelkasten is **generative** — producing ideas from linking where novelty is the aim.

Rationalist epistemic status is **communicative** — signaling weight where information cascades are the risk.

PKG is **architectural** — modeling a person as a queryable system where personalization is the aim.

This scaffold is none of these exactly. It's closer to an older thing: a **commonplace book** — the Renaissance practice of structured notes on one's own life and reading, organized for retrieval and return. Auditable, personal, typed, generative — but for private return, not public argument.

The Delphic γνῶθι σεαυτόν — *know thyself* — was carved at the temple at Delphi as advice to visitors before they consulted the oracle. The oracle is the interlocutor; know-thyself is preparation for being understood by one.

This graph is a commonplace book designed to be read *by an AI you are talking with*. That's a new shape: personal and private like a commonplace book, structured like a KG, generative like a Zettelkasten, explicitly-provenanced like PROV-O, aware of its own uncertainty like rationalist epistemic status. No existing field owns it.

---

## Credit

- W3C [RDF](https://www.w3.org/TR/rdf11-concepts/) (2004) and [PROV-O](https://www.w3.org/TR/prov-overview/) (2013).
- Patrick McCarthy, [open-knowledge-graph](https://github.com/patdmc/open-knowledge-graph) (MIT) — formal scientific-claims articulation.
- Stephen Toulmin, *The Uses of Argument* (1958).
- Niklas Luhmann (Zettelkasten); Sönke Ahrens, *How to Take Smart Notes* (2017); Andy Matuschak, [evergreen notes](https://notes.andymatuschak.org/).
- LessWrong epistemic-status convention (muflax → gwern → Scott Alexander).
- PKG survey literature: Chakraborty et al. (2022), Shirai et al. (2021), Kasela et al. (2025), Bloor et al. (2023).
