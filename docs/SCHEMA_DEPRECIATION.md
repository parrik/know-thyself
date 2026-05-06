# Schema depreciation (honest)

Typed knowledge graphs depreciate faster than the raw notes underneath. In every reviewed retrospective, the *typed structure* was the part that decayed. And as of 2026, the structural work the typing did — entity extraction, provenance attribution, confidence weighting, temporal-validity dating — is something a frontier model performs on the fly from messy notes in a single prompt. The schema is a frozen synthesis of an inference-time operation that is no longer scarce.

- **Niklas Luhmann** — 90,000 cards, 40 years. Gave up on proximity-based organization by ~card 20,000 and reframed the failure as "serendipity."
- **Andy Matuschak** — never released his evergreen-notes tooling, citing maintenance burden and conceptual debt as note count grew.
- **Roam Research** users (Dan Shipper retrospective) — bidirectional links produced placement anxiety without producing revisit.
- **Gordon Brander's Subconscious** (decentralized notes protocol, 2020–2024) — shut down because "if I want to amplify my intelligence today, I reach for Claude." LLM-in-loop reset the hypothesis space the typed-graph protocol was answering.
- **Simon Willison's TIL** — zero schema, 576 entries over 6 years. Outlasted every typed-graph project in this comparison.

Implications baked into this scaffold:

1. **Resist minting new node types.** Extend via sub-categories (see `SCHEMA.md`).
2. **Measure revisit, not growth.** A `NOW` node + auto-render loop creates a daily revisit surface.
3. **The LLM is both why this works now and why the typed structure isn't a moat.** Brander's shutdown showed one half: LLM-in-loop reset the hypothesis space the protocol-graph was answering, making curation tractable. The other half: frontier models now identify entities, attribute claims, weight confidence, and date temporal validity from raw text on the fly — the structural work the schema was solving for. Per-node, a hand-curated graph is more reliable than what a model would synthesize from the same notes — because a human chose what landed there. But the *capability* of producing typed-with-provenance structure from messy text is no longer scarce. The schema is a virtue, not a moat. Virtues get copied; moats compound.
4. **Flat markdown is the honest fallback — and stronger every model generation.** If the schema stops being fun to maintain, Willison-style TILs are an acceptable regression. The model can re-derive structure on read.
5. **The durable thing is the discipline, not the schema.** If frontier models do the typing, then what this scaffold actually scaffolds is the practice of refusing to let them write the graph. The hard rule that nodes are hand-curated. The provenance chain a human can stand behind in front of another human. The willingness to mark a claim *open* and leave it open. Discipline doesn't get inferred from messy notes — it gets practiced. Build for the practice; the typed structure is the trace of the practice, not the product.
