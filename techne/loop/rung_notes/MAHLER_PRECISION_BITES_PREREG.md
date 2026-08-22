# Pre-registration: does the 5.1e-6 Mahler precision limit BITE a real consumer?

Cycle 048. Written and committed **before reading the band constants or any consumer's data**.

## The question

Cycle 047 measured `mahler_measure`'s relative error at **1.2e-15 in well-conditioned cases,
reaching 5.1e-6** when root-finding displaces a root. Lehmer's constant is 1.17628…, and searches
for a smaller measure work at fine resolution, so the error *could* mis-rank a candidate.

**"Could" is not "does".** This cycle settles it, and a NULL closes a live worry rather than
leaving it to be re-raised every cycle.

## What I already knew when writing this (disclosed)

- The repo-wide grep has run. It surfaced
  `aporia/experiments/reasoning_steering/stage0b/` as the only consumer that appears to both
  **RANK** by the measure (`states.sort(key=lambda s: (s.mahler_measure, s.coeffs))`) and apply a
  **THRESHOLD** (`BAND_LOW < s.mahler_measure < BAND_HIGH`).
- `charon/agents/erebos/generators/g24_symmetry_twist.py` says it *"would call
  techne.lib.mahler_measure"* — prose describing an intended call, not an executed one.
- Other hits are analogy tables and weight dictionaries that mention the NAME `mahler_measure` as
  a string token, not the function.
- **I have NOT read `BAND_LOW` / `BAND_HIGH`, and have not checked whether stage0b's stored
  `mahler_measure` values were produced by my function or by something else.** Those are the
  measurements.

## Feasibility, verified before sampling

The stage0b modules are importable Python in the repo; the band constants are module-level
literals; the corpus is a data file on disk. **No service, no database, no optional dependency**
(#242 unruled, so nothing may be installed). Measurable population: **every stage0b call site
plus its corpus file**, plus any other consumer the repo-wide grep resolves to an actual call.

## Definitions, fixed in advance

**BITES** — at least one of:
1. A consumer **ranks or sorts** by the measure AND two distinct candidates in its live data lie
   within **5.1e-6** of one another (so the worst-case error could swap them);
2. A consumer applies a **threshold** and at least one live value lies within **5.1e-6** of that
   threshold (so the error could flip its side);
3. A consumer compares a measure against **Lehmer's constant** (1.17628…) at a tolerance tighter
   than 5.1e-6.

**DOES NOT BITE** — no consumer satisfies any of the three, i.e. every live gap and every distance
to a threshold exceeds 5.1e-6 by a comfortable margin, OR the stored values were never produced by
my function.

**INCONCLUSIVE** — the consumer's live data cannot be read without running its pipeline. Reported
as unmeasured, NOT as null. (Cycle 043's lesson: a null on unmeasurable data is an absence dressed
as a result.)

## Predictions, committed

1. **stage0b's band is NOT near Lehmer's constant.** Confidence: **low.** "In-band" for a
   reasoning-steering corpus over polynomials plausibly means exactly the small-measure region
   near 1.17628, which is why this is worth checking rather than assuming.
2. **The sort DOES have ties or near-ties within 5.1e-6.** Confidence: **moderate.** Mahler
   measures of small-height integer polynomials cluster, and the sort key falls back to `coeffs`,
   which suggests the author already met exact ties.
3. **Overall verdict: DOES NOT BITE.** Confidence: **low-to-moderate**, and I am deliberately
   recording that I expect the reassuring answer, so that finding it is less persuasive than
   finding the alarming one.

## Decision rule and the DECISION CONSEQUENCE

- **BITES** → fix what I own: either the measure's precision on the affected inputs, or ship a
  precision-aware comparison helper in my tree with the measured budget baked in, and document
  the limit at the call site's doorstep. Postcondition measured by name-diff.
- **DOES NOT BITE** → **say so plainly and close the worry.** The precision limit stays documented
  in `test_mahler_authority.py` as a property of the tool, HITL #266 is answered "documenting is
  enough", and the loop stops carrying it as an open thread. **This is a real result, and it is
  the one that stops future cycles re-litigating a hypothetical.**
- **INCONCLUSIVE** → report as unmeasured and state exactly what would be needed.

## Constraints

Read-only outside `techne/` and `prometheus_math/` — aporia and charon are **not mine to patch**,
so if it bites there, the fix must land in my tree or become a HITL item, not a patch to theirs.
No dependency installed. Tolerances from measured budgets, never guesses.
