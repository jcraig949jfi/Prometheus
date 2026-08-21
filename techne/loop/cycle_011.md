# Loop Cycle 011 — 2026-08-21 (round 4 arrived; all three items executed)

**12 new tests, ladder suite 99 green.** Round 4 was genuinely new content answering the
round-4 questions, and item 3 landed on a finding this project already made the hard way.

## 1. R6 — provenance-sensitive diagnosis (their behavioural kill, no work metering)

Built `r6_localization.py`. Their construction works exactly as claimed: because proofs are
NON-UNIQUE, a from-scratch solver returns a different valid route and the diff **smears**
across the derivation (flags ≥2 steps, never the single fault). The localizer names the
first invalid transition and repairs it minimally, preserving prefix and re-running suffix.

**Their sharper case, built:** a corrupted derivation whose ENDPOINT is a legitimate value.
Endpoint checking passes; provenance validation finds the fault at step 0; and the repaired
derivation's true endpoint DIFFERS from the corrupted one — so the endpoint checker was not
merely uninformative, it was *wrong about the answer*. R6's object is diagnosis over
provenance, not the ability to produce a correct derivation.

## 2. Retraction — add-only plasticity provably poisons selection

Built `BudgetedSelector`. With installed operators considered before primitives under a
finite evaluation budget B: 0–2 stale macros → solved; **≥ B stale macros → never solved**.
Their guard question settled executably: installing a guarded replacement while the
unguarded macro REMAINS ACTIVE does not fix poisoning (it is still selected first, still
burns budget). Retraction restores performance. **R_{t+1} ⊂ R_t must be possible** — negative
plasticity is real only operationally.

## 3. Band G — epistemic-rule plasticity + retroactive revalidation

Built `epistemic_plasticity.py`. E_0 = sample integers 0..9; the adversarial claim C37 has
difference x(x−1)…(x−9), so it agrees at every sampled point and is FALSE. C80 depends on
C37. After a warranted revision to symbolic normalization: the plastic corpus retracts C37
**and propagates to C80** → 98 trusted; the fixed-evaluator corpus reports 100 forever.
Prospective-only revision leaves the history contaminated (100) until `revalidate()` runs.

**Their constitutional constraint is enforced as a gate:** `revise()` REFUSES a revision
without an evaluator-independent warrant — the terminal cheat ("my experiment failed,
therefore I revise failure to mean success") raises `UnwarrantedRevision`.

### The connection they could not have known about

This is **the June 2026 Prometheus finding in general form.** The substrate's "2,351
promotions" turned out to be a *fossil of a superseded gate* — claims certified under an
evaluator that was later replaced, which nothing ever revalidated. My own M0.5 audit found
zero records clear the current bar. That is exactly `test_prospective_only_revision_leaves_history_contaminated`,
except it happened to us in production. Retroactive revalidation is not a Band-G curiosity;
it is a missing organ we have already been bitten by.

## Claim v8

Coordinate 8: **epistemic-rule plasticity**, constrained — E_t → E_{t+1} with retroactive
revalidation AND an evaluator-independent warrant requirement. Their two-level distinction
(object-level plasticity vs meta-epistemic plasticity under invariant constitutional tests)
is adopted; the constitution is what stops the terminal cheat.
