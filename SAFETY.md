# Safety — read this first

This scaffold is a tool for organizing what Claude remembers about you. It
is not a clinical instrument, not a therapist, and not a friend. Please
read these limits before you start.

---

## What this scaffold is good at

- Separating observations (things that happened) from interpretations
  (theories about why they happened).
- Making it visible which observations most of your thinking rests on, so
  a wrong observation doesn't quietly corrupt many downstream claims.
- Flagging the difference between a claim that's been restated across
  many conversations (one derivation repeated) and a claim that has
  genuinely independent grounding (multiple evidence sources).
- Surfacing emergent insights that only appear when two or more patterns
  are held simultaneously.
- Giving you a visual, printable artifact of where you are right now that
  you can return to when you're not in a clear-headed state.

---

## What this scaffold is not

- **Not therapy.** If you are in acute distress, having thoughts of harming
  yourself, or working through trauma that is actively destabilizing, please
  do not use this as a substitute for human support. Graph-building is a
  clarifying activity, not a regulating one. If you are dysregulated, build
  the graph later, or build it with someone in the room.
- **Not a diagnosis.** None of the novel or emergent nodes Claude produces
  should be read as saying "you have X" or "you are Y." They are tentative
  interpretations of a limited set of observations, flagged as such.
- **Not objective.** The graph is built from what Claude has been told and
  what Claude has inferred. Both are partial. The graph reflects one
  perspective on your life — yours, filtered through Claude. Treat it as
  a working model, not ground truth.
- **Not permanent.** Graphs should be revised. Claims should fall when
  better evidence arrives. Interpretations should update. If a claim in
  your graph feels wrong when you read it, it probably is — trust that
  signal over the structure.

---

## Sensitive content

Some of what ends up in a personal memory graph is sensitive — past harm,
trauma, substance use, relationship difficulty. The schema allows you to
preserve these observations (they may be load-bearing for other claims)
while flagging them with `HANDLING:` directives inline — for example,
"HANDLING: do not raise unprompted" on a node about past trauma.

This is genuinely important. The whole point of the graph is that Claude
can reference it in future conversations. Without handling directives,
Claude might casually mention a trauma in an unrelated context. With
them, the structural claim is preserved but the content stays protected.

**You control which observations get HANDLING flags.** Claude should ask
before assuming. If you're unsure, err on the side of flagging — it's
easier to remove a flag later than to unsay something Claude shouldn't
have surfaced.

---

## When to stop

Stop and close the file if:
- You notice the graph is producing interpretations that feel more
  confident than they should. Flag them tentative or drop them.
- You find yourself reading the graph to feel bad about yourself. The
  graph is not a report card. It's a map of structural claims.
- Claude starts asserting emergent insights that feel uncomfortably
  personal without clear derivation. Ask for the derivation. If it can't
  produce one, drop the claim.
- You're high, drunk, or in a low mood. Build when clear. It holds
  when you're not.

---

## Privacy

The YAML graph contains everything in it in plain text. Treat the file
like you'd treat a journal. Don't paste it into untrusted systems.
Don't share it publicly without redacting what you don't want public.

Claude's memory is account-scoped — it doesn't leak across users. But
the YAML file you generate lives wherever you save it and is your
responsibility.

---

## One more thing

The graph is scaffolding. It is not you. At best, it is an accurate
partial map of some of the structural features of your past. It is not
your present, not your future, and not the whole of what you are.

Build it; use it; modify it; discard it when it stops being useful. The
method is the point, not the artifact.
