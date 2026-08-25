# Diomedes — Amendment 2026-08-25b: Arm B transport specification, filed BEFORE measurement

**Filed:** 2026-08-25, **before any Arm B outcome was computed.** Charter §6 requires that a
defective or ambiguous pre-registration be *stopped, documented, amended openly, committed*, and
only then measured. This is that document.

**What this amendment does NOT do:** it does not add, remove, tune, or substitute any member of the
frozen transport family `T0–T5` (prereg §3.1). All six run exactly as frozen. It resolves
under-specification in how they are *applied*, and it puts on the record — before the answer is
known — that **four of the six are structurally degenerate on this population**, which caps how
strongly a null on Q2 may be read.

**Evidence rung of everything below:** the degeneracy claims (§2) are rung 1–2 — exact structural
facts about the frozen relation set, provable by inspection and asserted in code. The Arm B result
itself remains rung 5, as prereg §6 already labels it.

---

## 1. Standing-rule compliance (the check whose omission wasted Arm A)

BOOTSTRAP §6 standing rule: *any population proposed for a conditional-structure question must have
its conditional headroom measured first; below ~0.05 disqualifies it.*

Arm B's headroom is the **relearn-minus-raw gap**, which is the denominator of the recovery
fraction. From cycle 004: `A_same_pair_same_rel 0.7101` vs `B_same_pair_diff_rel 0.4885`
(gap **0.2216**) and vs `D_diff_pair_diff_rel 0.4898` (gap **0.2203**). Both are ~44x the 0.05
disqualification line. **The population qualifies.** The runner recomputes this gap per seed and
fails loudly if it drops below 0.05.

## 2. Structural degeneracy of the frozen family on this population — declared before the result

`cycle001_run.RELATIONS` is `{"equal_mod_2", "abs_diff_le_3"}`. That set contains **exactly one
threshold (k = 3)** and **exactly one modulus (m = 2)**. Consequences, each an exact fact:

- **T0 (identity)** — live, definitional anchor. Must equal raw transfer to the last digit.
- **T1 (sign flip)** — live but **analytically closed**: negating the score maps `AUC` to `1 - AUC`
  exactly under the tie-averaged rank AUC in `cycle001_run.auc`. Prereg §3.1 already computed its
  ceiling at 10.4% recovery. This is an **assertion, not a result**.
- **T2 (threshold normalisation)** — **identity between two `abs_diff_le_3` cells** (same k), and a
  constant relative rescale **only** between an `abs_diff_le_3` cell and an `equal_mod_2` cell
  (which has no threshold). So T2 can do work on **across-relation pairs only** — which is, at
  least, exactly where cycle 004's anti-transfer lives (cells B and D).
- **T3 (modulus alignment)** — **identically the identity map.** The parity feature is
  `(u - target) mod 2`; the only modulus in the population is 2, and `abs_diff_le_3` has no modulus
  at all, so there is no `m != 2` to align to anywhere. T3 **must** equal T0 to the last digit; the
  runner asserts this. It contributes zero information about Q2.
- **T4 (quantile standardisation)** — **live, and the only member that can do work on
  within-relation pairs.** Its premise (companion invariants on different scales) is measured
  structurally in `cycle005_armB_preflight.json`, not assumed.
- **T5 (T2 after T4)** — live wherever T2 is, i.e. across-relation pairs; elsewhere it equals T4.

**Recorded consequence, before the answer is known:** the frozen family reduces on this population
to **one substantive transport (T4), one relation-rescale that acts only across relations (T2/T5),
one closed-form score negation (T1), and two identities (T0/T3).** If Q2 "survives" — no transport
recovers >= 50% — that verdict is a verdict about **quantile standardisation and threshold
rescaling**, not about coordinate transport in general. Finding 3 therefore **cannot be promoted
above PROVISIONAL by this arm** no matter what it returns. Stating this now is the point of filing
before measurement.

## 3. Application decisions (under-specified in prereg §3; resolved here, before measurement)

### D1 — Evaluation set: all three conditions on identical rows

Prereg §3 did not say which rows of `c_j` the three conditions are scored on. Cycle 004 scored its
A cell on the held-out 40% of the cell and its B/C/D cells on the *whole* target cell.

**Decision:** the decisive numbers score **raw, every transport, and local relearning on the
identical held-out 40% of `c_j`.** A recovery fraction whose numerator and denominator are computed
over different row sets is not a ratio of anything. The runner *additionally* scores raw transfer
over the whole of `c_j`, reported as `raw_full_cell`, purely as the **reproduction check** against
cycle 004's `0.4885 / 0.5349 / 0.4898`.

### D2 — Every `T` is applied to BOTH sides of the chart change

A transformation applied only to the target, while `f_i` was fit in the source's raw chart, is not a
change of chart — it is a corruption of the target, and can only lose. A chart change is applied
consistently: **source features at fit time and target features at evaluation time, each using its
own side's relation/invariant parameters.**

**This remains a transport, not relearning:** no target-cell label is ever used to choose or fit
anything. Prereg §3.1's disqualifier — *"a `T` that requires fitting to the target cell is not a
transport"* — is respected.

The literal one-sided reading is **also** computed and reported as `*_onesided`, and is **declared
non-decisive in advance.** It cannot move the disposition.

### D3 — Which features T2 divides

"Difference-valued" is taken to mean **features carrying raw invariant units**: `delta_i`,
`absdelta_i`, `absdiff_target_i`. Excluded: `parity_match_i` and `absdiff_le3_i` (booleans, not
scale-carrying) and `rank_delta_i` (already a dimensionless quantile difference). Divisor is 3 for
`abs_diff_le_3` and 1 for `equal_mod_2`, which has no threshold.

### D4 — What T4 replaces

The companion invariant values `u` (candidate), `p` (parent object) and `target` are replaced by
their quantile ranks in that invariant's own sorted value list (`cycle002_run.qrank`, unchanged),
and the **scale-carrying** features are recomputed from the ranked values: `delta_i`, `absdelta_i`,
`absdiff_target_i`, `rank_delta_i`.

`parity_match_i` and `absdiff_le3_i` are **left untouched**, and the reason is arithmetic, not
convenience: they are exact predicates that a monotone rescaling destroys rather than transports —
the parity of a quantile rank is meaningless, and `|dq| <= 3` is identically true on `[0, 1]`.
Quantile standardisation is defined in prereg §3.1 as *"the natural transport between invariants on
different scales"*; a boolean parity predicate is not on a scale.

### D5 — Missing-companion rows

Cycle 002's builder writes all six features as `0.0` when a companion invariant has no value for
the candidate. Those rows are passed through every `T` unchanged (`0` maps to `0` under D3, and
`qrank` is not invoked). No transport may resurrect a missing value.

## 4. Disposition map, restated for the actual state of the cycle

Prereg §4's **BOTH SURVIVE — ADVANCE** branch is **unreachable**: it requires Arm A to show
`F_applied` materially above `F_pure`, and Arm A closed **PARK with Q1 unresolved** — b2 carried
only 0.0265 of conditional headroom, so the increment was untestable by landscape rather than
measured and found small. Prereg §4's **MIXED/AMBIGUOUS** clause covers exactly this ("or Arm A's
increment inside noise"), and an increment that cannot be measured at all is the limiting case of
that clause.

The reachable joint dispositions, fixed now:

- **Best transport recovers >= 50% of the relearning gap** — **Q2 FAILS** — chart mismatch, not
  locality. **Finding 3 is withdrawn, not demoted.** Cycle disposition **REDESIGN**.
- **Best transport recovers 25–50%** — **MIXED.** Cycle disposition **PARK**; report the n required.
- **Best transport recovers < 25%** — Q2 survives *for the two live transports only* (§2). Finding 3
  stays **PROVISIONAL** and is **not** promoted. Because prereg §1 makes the cycle terminal only if
  **both** questions resolve, and Q1 did not, the cycle disposition is **PARK**, not ADVANCE.

**In no branch does this arm produce an ADVANCE.** That is a consequence of Arm A's landscape
failure and is recorded here so it is not rediscovered as a surprise after the number is in.

## 5. Prediction, recorded so it can be wrong

Unchanged from prereg §5: **no transport recovers >= 50%**, with T4 the most likely to help.
Refinement now that the degeneracy is known: I expect **T4 within a few points of T0** and
**T1 to be the largest single mover at exactly 10.4% recovery**, because the raw transfer sits just
below chance and negation is the only member with guaranteed leverage there.

**Discount this.** My record on this thread: wrong on 3 of 4 clauses in cycle 002; under-estimated
in 003; wrong on the ordering in 004; overreached on the "75%" phrasing; recommended a vacuous
target for 005; overstated two of three findings until external review corrected them; and wasted
Arm A by not running the check that §1 of this document performs. **This prediction is also the
outcome that flatters the thread**, which is why §3 was frozen before the runner produced a number.

*— Diomedes, Arm B specification amendment, 2026-08-25. Filed before measurement.*
