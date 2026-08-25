# Diomedes cycle 005 ARM B — RESULT: transport recovers 6% of the relearning gap, and the gate it missed was reachable

**Filed:** 2026-08-25. **Pre-registration:** `CYCLE_005_PREREG_terminal.md` §3, as applied by
`AMENDMENT_2026-08-25b_armB_specification.md` (filed before measurement, commit `e1d7b9ab`).
**Runner committed unrun** at `6213ec52`. **Rows:** `cycle005_armB_run.py` →
`cycle005_armB_result.json`, `cycle005_armB_handcheck_rows.json`.

**Disposition: PARK.** Q2 survives — but only for the two transports that were live, and the
amendment said so before the number existed.

---

## 1. The numbers

5 seeds · 12 mixed invariant pairs · 24 cells · **552 ordered cell pairs per seed** ·
population digest `1b4abb1a…` · ~38,000 states per seed.

Local relearning **0.7392**. Raw transfer **0.5068**. **Headroom 0.2325.**

Transfer AUC and recovery `(transfer − raw) / (relearn − raw)`, mean over seeds, SE over seeds:

- **T0** identity — 0.5068 — recovery 0.0000 (definitional)
- **T1** sign flip — 0.4932 — recovery **−0.0582** (SE 0.0032)
- **T2** threshold normalisation — 0.5115 — recovery **+0.0204** (SE 0.0011)
- **T3** modulus alignment — 0.5068 — recovery 0.0000 (identity, asserted)
- **T4** quantile standardisation — 0.5194 — recovery **+0.0543** (SE 0.0022)
- **T5** T2 ∘ T4 — 0.5208 — recovery **+0.0603** (SE 0.0015)

**Best transport T5 at 6.03% of the relearning gap.** The Q2-FAILS gate is 50%; the MIXED band
starts at 25%. 6.03% with SE 0.0015 is **127 standard errors below the MIXED band**, so this is not
a threshold that measurement error could plausibly have crossed.

## 2. The gate was reachable — checked, not assumed

A null against a gate that could not have fired is not a null. The relevant question is whether
each chart *preserves local learnability*, because a chart that destroys the signal would make
transport failure a property of the chart rather than of locality.

**Relearn AUC measured within each chart:** T0 0.7392 · T2 0.7392 · T3 0.7392 · **T4 0.7265** ·
T5 0.7265 · T1 0.2608 (`= 1 − 0.7392`, as a sign flip must be).

T4's chart costs only **0.0127** of local learnability. So a T4 transport that worked as well as
local relearning would have scored ≈0.7265, i.e. recovery **≈94.5%**. **The 50% gate sat well
inside the attainable range and the decision was eligible to go the other way.** It did not.

## 3. What transport did, where, and why it is the right direction

Recovery by pair type (T0 → transported), mean over seeds:

- **B, same invariant pair, different relation** — raw 0.4888 → T4 0.4719, recovery **−0.068**
- **C, different pair, same relation** — raw 0.5549 → T4 0.5702, recovery **+0.083**
- **D, different pair, different relation** — raw 0.4603 → T4 0.4729, recovery **+0.045**

This is exactly the sign pattern T4's premise predicts, and it is worth stating because it is the
one piece of evidence that the transport was doing real work rather than nothing. Quantile
standardisation exists to fix **scale mismatch between invariants**. Cell B holds the *same
invariant pair* — the same scales — so there is no mismatch to fix and rescaling only loses
information. Cells C and D cross invariant pairs, where the pre-flight measured median
`absdiff_target` spreads of up to **2587×**, and there T4 helps. The instrument moved the number in
the direction its own mathematics predicts, in the cells where its premise applies, and the
magnitude was ~8% of the gap.

**The honest reading is not "transport does nothing."** It is: *transport does a little, in exactly
the cells where its premise holds, and a little is about 6% of what local relearning achieves.*

## 4. Declared: four of six transports were structurally degenerate, and that was known first

`AMENDMENT_2026-08-25b` §2, filed before measurement, established from the frozen relation set
`{equal_mod_2, abs_diff_le_3}` — **one threshold, one modulus** — that:

- **T3 is identically the identity map.** Asserted in code and confirmed: T3 = T0 to the last digit
  on every one of the 552 pairs, every seed. It carries **zero** information about Q2.
- **T2 is the identity within-relation** and acts only across relations. Confirmed: its C-cell
  recovery is exactly 0.0000, since C is same-relation.
- **T1 is closed-form** `AUC → 1 − AUC`. Confirmed exactly.
- **T0 is definitional.**

So the family reduced on this population to **one substantive transport (T4) plus one
relation-rescale (T2/T5)**. This is the single most important limitation on the result and it was
recorded before the answer was known, not discovered afterwards.

**Consequence, applied rather than argued around: Finding 3 (locality) stays PROVISIONAL and is not
promoted.** A null about quantile standardisation and threshold rescaling is not a null about
coordinate transport in general.

## 5. Assertions (rung 1) — all passed, none skipped

- Population digest `1b4abb1a…` ✓
- **Builder differential:** the augmented state builder must reproduce `cycle003_run.C2_states`
  exactly. **60,640,200 feature values per seed** streamed into a sha256; identical on all 5 seeds ✓
- **AUC differential:** `batched_auc` vs `cycle001_run.auc`, max absolute difference **exactly 0.0** ✓
- Perfect predictor **1.0** · constant predictor **0.5** · monotone invariance **0.0** ·
  labels permuted within state → **0.5051** ✓
- Sign flip sums to 1.0 — error **exactly 0.0**; effective-weight score ranks identically to
  `predict_proba` — error **exactly 0.0** ✓
- **T3 = T0** to 1e-12 ✓ (the degeneracy proved in advance, asserted rather than assumed)
- Headroom floor 0.05 rechecked per seed; lowest observed 0.2305 ✓
- **v1/v2 semantics preserved** — worst drift 4.69e-05 against the 4-dp anchor ✓ (see §7)

**Hand-checkable rows:** 20 fully expanded rows, `determinant|rank|abs_diff_le_3` →
`crossing_number|tamagawa_product|abs_diff_le_3`, all 18 features under both charts, effective
weights, scores and ranks, at 17 significant digits. The emitter asserts the multiplication closes;
it does, to a relative **1.3e-16**.

## 6. Reproduction check against cycle 004, including where it does not match

Raw transfer scored on the **whole** target cell, the way cycle 004 scored its B/C/D cells:

- **B same pair, diff relation — 0.4884** vs cycle 004's **0.4885**. Reproduced to 0.0001.
- C different pair, same relation — 0.5551 vs 0.5349.
- D different pair, diff relation — 0.4600 vs 0.4898.

**C and D do not reproduce, and the cause is a coverage difference, not a discrepancy.** Cycle 004
drew **one** random other-pair cell per source (`rng.choice(others)`) for its C and D cells; Arm B
enumerates **all 552 ordered pairs**. Cycle 004's C and D are random subsamples of what Arm B
measures completely. B involves no such sampling — same pair, other relation is uniquely determined
— and B is the cell that reproduces. This is the charter's known trap #2 (cross-cycle anchors
between different estimators) appearing again, and the correct statement is the estimator, not the
label: *Arm B's C and D are complete enumerations; cycle 004's were one-draw samples.*

## 7. Declared: a runner defect I caused, found and fixed before the result

The first runner exhausted **16.5 GB** by holding two full sets of Python dicts for the builder
differential test, and was killed mid-seed-2. The rewrite changed **storage layout only** — numpy
arrays instead of dicts, and a streamed digest instead of a simultaneous comparison.

Charter §7 forbids letting an optimisation become an experimental change, so the rewrite is not
merely asserted to be equivalent. Seed 20260824's v1 numbers were recorded **before** the rewrite and
compiled into the runner as `V1_SEED0_ANCHOR`; the v2 run asserts it reproduces all 14 of them.
Worst drift **4.69e-05**, against a 4-dp rounding floor of 5e-05. The optimisation moved nothing.

**A second defect, also mine:** the runner's first hand-check emission rounded to 6 dp, which does
not close on raw-chart features of magnitude ~3200 — the rows were not in fact hand-checkable.
Re-emitted at exact precision by `cycle005_armB_handcheck.py`, which asserts the arithmetic closes
and separately asserts it selected the same state (per-state AUCs must equal the runner's
0.510985 / 0.645641; they do). My first repair set an **absolute** 1e-9 tolerance on a score of
magnitude 3200 — the wrong unit, demanding 6e-13 relative. Corrected to a relative bound.

## 8. Prediction vs outcome — I was right on the headline and wrong on the mechanism

**Predicted (prereg §5):** no transport recovers ≥ 50%, with T4 the most likely to help.
**Outcome:** correct. Best 6.03%, and T4/T5 were indeed the movers.

**Predicted (amendment §5, refined):** T4 within a few points of T0, and **T1 the largest single
mover at exactly 10.4% recovery**.
**Outcome: wrong, and wrong in a way already in my ledger.** T1 was the **worst** performer at
**−0.058**. The 10.4% ceiling was computed from cycle 004's **B cell** raw of 0.4885 — below chance,
where negation helps. But raw transfer averaged over **all 552 ordered pairs** is 0.5068, *above*
chance, so negation loses. I quoted a number measured on one population as a property of another.
That is the same error as `feedback_wrong_population_statistics`, committed inside the very document
whose purpose was to prevent it. The by-type breakdown shows it plainly: T1 recovers **+0.285** on D
and **+0.089** on B, both below chance, and **−0.596** on C, which is above chance.

Running score: cycle 002 wrong on 3 of 4 clauses; 003 right on direction, under-estimated size; 004
wrong on the ordering; synthesis 001 overreached on "75%"; cycle 005 planning recommended a vacuous
target; Arm A wasted by an unmeasured headroom; **Arm B's refined prediction wrong on the wrong
population.** The firewall did its job again — the prediction was on the record before the run.

## 9. Disposition

**PARK**, per `AMENDMENT_2026-08-25b` §4, which fixed this mapping before measurement:

> best transport recovers < 25% ⇒ Q2 survives *for the live transports only*; Finding 3 stays
> PROVISIONAL and is **not** promoted; because prereg §1 makes the cycle terminal only if **both**
> questions resolve, and Q1 did not, the cycle disposition is **PARK**, not ADVANCE.

Recovery 6.03% ⇒ that branch. **No branch of this arm could have produced an ADVANCE**, and that too
was recorded in advance.

**What this does NOT license:** it does not promote locality, it does not establish that
mathematical navigation knowledge is intrinsically local, and it does not justify rebuilding the
instrument on that basis. Two transports failed to move the number. That is what was measured.

---

## Coordinate-Adequacy Record — CAR-005

```json
{
  "car_id": "CAR-005",
  "claim_id": "the anti-transfer of cycles 003-004 is intrinsic locality rather than chart mismatch",
  "quantity_credited": "fraction of the local-relearning gap recovered by mathematically natural coordinate transport",
  "coordinate_system": "frozen 18 relational features under charts T0-T5, applied two-sided (source at fit, target at eval)",
  "attainable_range": {"raw_transfer": 0.5068, "local_relearning": 0.7392, "headroom": 0.2325,
                       "max_attainable_recovery_under_T4": 0.945,
                       "gate_reachable": true},
  "measured": {"T0": 0.0, "T1": -0.0582, "T2": 0.0204, "T3": 0.0, "T4": 0.0543, "T5": 0.0603,
               "best_transport": "T5", "best_recovery": 0.0603, "se_over_seeds": 0.0015,
               "distance_to_MIXED_gate_in_SE": 127,
               "by_pair_type_T4": {"B_same_pair_diff_rel": -0.068,
                                   "C_diff_pair_same_rel": 0.083,
                                   "D_diff_pair_diff_rel": 0.045}},
  "controls": {"perfect_predictor": 1.0, "constant_predictor": 0.5,
               "monotone_invariance_error": 0.0, "permuted_labels": 0.5051,
               "T3_equals_T0_error": 0.0, "sign_flip_identity_error": 0.0,
               "builder_differential_values_hashed_per_seed": 60640200,
               "auc_differential_max_error": 0.0,
               "v1_v2_semantics_worst_drift": 4.69e-05,
               "relearn_within_T4_chart": 0.7265},
  "measured_over_which_rows": "5 seeds, 24 cells, 552 ordered cell pairs per seed, ~38,000 states per seed, population digest 1b4abb1a",
  "verdict": "TRANSPORT-DOES-NOT-RESTORE-ORDERING (for the two live transports)",
  "disposition": "PARK",
  "what_died": "nothing new; and specifically NOT finding 3, which stays PROVISIONAL because four of six frozen transports were structurally degenerate on this population",
  "what_survived": "Q2's answer is negative for quantile standardisation and threshold rescaling, against a gate shown reachable at 94.5%",
  "prereg_defect": "prereg S3.1 froze a transport family whose T2 and T3 are degenerate on a relation set containing one threshold and one modulus; declared in AMENDMENT_2026-08-25b S2 BEFORE measurement, family left unchanged. Two runner defects (16.5 GB memory, 6dp hand-check rounding) declared in S7, both fixed with identity proofs.",
  "decision_this_changes": "the reconnaissance does not get to claim locality, and does not get to claim chart mismatch either; the next test of Q2 needs a population with more than one threshold and more than one modulus, which this corpus does not have",
  "rows_ref": "cycle005_armB_result.json, cycle005_armB_handcheck_rows.json"
}
```

*— Diomedes, cycle 005 Arm B result, 2026-08-25. Disposition PARK.*
