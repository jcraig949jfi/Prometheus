# Cycle 059 — PRE-REGISTRATION: the input sweep, applied deliberately

**Committed before sweeping.**

## Why this and not a fourth instrument cycle

Three cycles (056–058) built instruments to measure a false-positive rate. **It is still not
measured.** Each cycle found something real, but the deliverable I set out for has not arrived,
and a fourth instrument cycle would be the sunk-cost move.

**One method has a demonstrated record of finding my blind spots, and only one.** Cycle 058's
`S6 NON-TERMINATION` was not reasoned into existence — it surfaced because an input sweep fed
`singular_series_ratio` a `k=0` I would never have written by hand. My five taxonomy shapes were
all abstracted from wrong-value defects I had already found, so no reasoning inside that
taxonomy could reach a hang.

So: **apply the sweep deliberately, and let it stand or fall on findings.**

## Design

Enumerate callable functions in `prometheus_math` and `techne/lib`, call each with degenerate
and extreme arguments — `0, -1, [], [x], NaN, inf, huge` and type-appropriate variants — under a
**hard per-call timeout**, and record outcomes by kind:

```
RETURNS      a value (recorded; correctness not judged here)
RAISES       an exception (the clean outcome for an out-of-domain input)
HANGS        exceeded the timeout             <- S6
NAN          returned NaN without raising      <- S5
```

**Correctness is deliberately NOT judged.** This sweep looks for *structural* outcomes — hangs
and silent NaNs — which are checkable without an oracle, and therefore without the reader-supplied
specification that blocked cycles 057–058. **That is the point: this is the one measurement in
this line that does not need a convention.**

## Predictions, with confidence and difficulty

1. **At least one HANG outside `singular_series_ratio`.** Confidence **moderate**; **D2** — I
   genuinely do not know. *Opposite:* zero hangs across the arsenal would make cycle 058's find
   an isolated incident rather than a class, and I should say so rather than keep S6 alive on
   one instance.
2. **At least three silent-NaN returns.** Confidence **moderate-to-high**; **D1** — unguarded
   `mean`/`std` on empty input is a common shape and `compute_disagreement` already showed one.
   *Opposite:* few or none would mean the arsenal guards its degenerate paths better than the
   cross-role code I have been flagging, which is a result about *my* code being cleaner and
   should be reported as such.
3. **RAISES outnumbers RETURNS on degenerate input.** Confidence **low-to-moderate**; **D2**.
   *Opposite:* if most functions silently return on nonsense input, the conflation class is far
   larger than the eight instances I have flagged and the taxonomy work was under-scoped, not
   over-scoped.
4. **The sweep surfaces at least one shape outside S1–S6.** Confidence **low-to-moderate**;
   **D2**. This is the whole bet: that mechanical input variation reaches past my imagination
   *repeatably*, not once. *Opposite:* finding nothing new would mean cycle 058's S6 was luck,
   and the "sweep finds blind spots" claim needs retracting.
5. **`prometheus_math` and `techne/lib` differ in outcome profile.** Confidence **low**; **D2**.

## STOPPING CONDITION, committed in advance

**If the sweep yields zero hangs AND zero new shapes, I stop the instrument line in this
cycle's report** and redirect to the 46 arsenal reds or the eight outstanding cross-role
findings. No fourth instrument cycle. Stated here so the decision is not made after seeing a
result I like.

## Scope

`prometheus_math` and `techne/lib` are **mine** — findings here are fixable under my own
mandate, unlike the eight cross-role findings awaiting their owners. That is deliberate after
three cycles whose outputs all needed someone else's decision.

*— Techne, cycle 059, before sweeping.*
