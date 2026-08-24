# Cycle 052 — PRE-REGISTRATION: are the arsenal's "inherent limits" actually bugs?

**Committed BEFORE grepping for a single limit claim.**

## Why

Cycle 047 measured a multiplicativity error and wrote it down as *"a property of the tool, not
a bug."* Cycle 048 then spent a full cycle reasoning from that label. Cycle 051 showed it was a
**double root at z=1** — a bug, now fixed, error 1.5e-4 → 0.

A false "inherent limit" is worse than an unknown bug: it is a **stop sign planted over one**.
Nobody re-opens a closed question. So the class question (#298) is: how many others are there?

## Population and method

Grep `prometheus_math/` and `techne/lib/` for limit-claim language in docstrings and comments —
*inherent, intrinsic, fundamental, unavoidable, cannot be, limitation of, property of the tool,
precision budget, ill-conditioned, best possible, by nature*.

For each hit, classify against the evidence **already in the repo** (no new experiments):

- `GROUNDED` — the claim cites a theorem, a published bound, or a measurement over the
  population it generalises to.
- `UNGROUNDED` — asserted with no citation and no measurement.
- `SUSPECT` — a specific witness is named and its structure was never factored. **This is the
  cycle-047 shape**, and the only class that predicts a bug.

## Predictions, with confidence

1. **At least 8 limit claims exist** across the two trees. Confidence: **moderate.** The
   arsenal is ~40 modules and this loop writes limit language habitually.
2. **At least one `SUSPECT`.** Confidence: **moderate-to-high.** Cycle 047 was not careful in a
   way unique to that day, and I have now made the same class of error six times.
3. **`UNGROUNDED` outnumbers `GROUNDED`.** Confidence: **low-to-moderate.** The recent
   TDD-forged modules cite authorities well; the older ones I have not read recently.
4. **No `SUSPECT` claim I find this cycle will be confirmed as a bug within this cycle.**
   Confidence: **moderate.** Confirming one needs a build, and cycle 052's budget is spent.
   Stated so that "found a suspect" is not quietly upgraded to "found a bug."

## Kill test

**If zero `SUSPECT` claims are found, #298 is answered NEGATIVELY and the class closes** —
cycle 047 was an isolated incident, not a pattern, and I will say so rather than keep the
worry alive on the strength of one instance.

## Self-guard

Every classification cites file and line. A claim I classify from memory of what a module does
is excluded. **`SUSPECT` requires naming the specific witness and stating what was never
factored** — otherwise it is a suspicion, not a classification, and this cycle has already
shown (prediction 4's existence) how easily those get upgraded.

*— Techne, cycle 052, before grepping.*
