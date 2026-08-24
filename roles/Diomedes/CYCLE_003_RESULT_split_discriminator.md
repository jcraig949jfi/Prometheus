# Diomedes cycle 003 — RESULT: the signal is real and beats the ceiling; it just doesn't transfer

**Filed:** 2026-08-24. **Pre-registration:** `CYCLE_003_PREREG_split_discriminator.md`, frozen at
`1fbc2133` **before** any outcome existed. **Rows:** `cycle003_run.py` → `cycle003_result.json`.
**Pre-registered band: TRANSFER-FAILURE-CONFIRMED. Disposition: REDESIGN.**

---

## 1. Headline — and it crosses the ceiling

Controls clean: ORACLE **1.0000**, SHUFFLE cheat **0.5000**, RANDOM **0.4999**.

- **T2_WITHIN — 0.6600** (per-seed 0.6589–0.6610, intervals ~±0.004)
- **T3_ACROSS — 0.5444** (replicates cycle 002 exactly)
- **Δ = 0.1156**, with complete separation: every seed's T2 lower bound exceeds every T3 upper bound.
- **B1_T2 control — 0.5581 vs B1_T3 0.5626, a rise of −0.0045.** The break-rate baseline went
  *down*. The T2 gain is **not** object memorization.
- **T0_INSAMPLE — 0.6611 ≈ T2_WITHIN 0.6600.** No overfitting gap; within a pair the family is at its
  own expressivity ceiling and generalises to held-out states essentially perfectly.

**The number that matters most: 0.6600 exceeds the state-independent information ceiling of 0.6254.**

Cycle 001 established 0.6254 as the hard ceiling for *anything* that ignores the current state.
Cheap relational coordinates — subtraction, parity, absolute difference — clear it. They capture

> (0.6600 − 0.6254) / (1.0000 − 0.6254) = **9.2% of the conditional signal**

which is modest, but it is the **first positive demonstration in this thread that state-conditional
navigational information is recoverable by arithmetic.** Prometheus's own recorded coordinates
(0.5560) do not reach even the state-independent ceiling.

## 2. The mechanism, observed directly rather than inferred

Per-pair coefficient vectors over 22 invariant pairs (median **1,002** training states each — so
these are well-determined fits, not noise), 1,155 pairwise comparisons:

> **mean pairwise cosine similarity = 0.0652** — the learned relationships are essentially
> **orthogonal** across invariant pairs.

Sign agreement with the modal sign, per feature (1.0 = same direction everywhere):

- `parity_match_0` — **0.864** (the most informative feature from cycle 002, and the most consistent)
- `absdelta_0` — 0.809 · `parity_match_2` — 0.773 · `delta_0` — 0.773
- most features — 0.53–0.74, i.e. **near coin-flip**
- `absdiff_le3_2` — **0.091**, almost perfectly anti-consistent

A global model must average coefficients whose directions disagree pair-to-pair. That is exactly why
PHI_REL scored *below its own best single feature* in cycle 002. The score gap was a symptom; this is
the disease, measured.

## 3. What this changes

- **Cycle 002's KILL stands and is now correctly scoped.** What died was a *global* relational model
  transferring across invariant pairs. Cycle 003 shows the coordinates themselves were never the
  problem.
- **E2 (genuine coordinate inadequacy) is falsified for this feature family.** Learned transition
  representations are **not** yet defensible — the cheap thing works, it simply does not transfer.
  Charter §5 holds: subtraction wins where subtraction suffices.
- **H3 is partially rehabilitated, narrowly.** Relational coordinates `Z(x,a)` do preserve
  state-conditional information within an invariant pair. Prometheus's *recorded* coordinates still
  do not — that finding is untouched.
- **The problem relocates from H3 to H4.** The open question is no longer "can cheap coordinates see
  it" but "does what is seen in one region say anything about another."

## 4. The least-interesting interpretation — and it is not yet excluded (charter §12)

Ruled out by design:
- **Object memorization** — B1_T2 control fell by 0.0045.
- **Overfitting** — T0 ≈ T2 to within 0.0011.
- **Leakage** — cheat control at exactly 0.5000; no arm reads the tested invariant.
- **Noise-limited per-pair fits** — median 1,002 training states per pair.

**Not excluded, and now the leading competing explanation: relation-type confounding.** The
population contains two relation types (`equal_mod_2`, `abs_diff_le_3`), and the *right* feature
differs between them — parity for one, bounded difference for the other. Within an invariant pair the
relation type may be near-constant; across pairs it varies. If so, the "pair-specific geometry" is
really **relation-type-specific geometry with only two values**, and the fix is trivial: fit one model
per relation type. That is much less interesting than 22 genuinely distinct local geometries, and it
is cheap to test.

**This is the boring explanation and it must be tested before any claim about local geometry.** It
becomes cycle 004.

## 5. Prediction scoring

Prereg §6 predicted TRANSFER-FAILURE-CONFIRMED, T2 in **0.58–0.65**, Δ ≈ 0.04–0.10, cosine near zero
or negative, B1 rising only slightly. Band: **correct**. T2 0.6600 — **just above** my interval.
Δ 0.1156 — **above** my interval. Cosine 0.0652 — **correct** (near zero). B1 control — **correct**
(fell). So: right on direction and mechanism, and I *under*-estimated the effect size, having been
wrong in the opposite direction in cycle 002.

## 6. Deviations

None. Frozen family, scorer, seeds, thresholds, bands and controls ran exactly as registered.

---

## Coordinate-Adequacy Record — CAR-003

```json
{
  "car_id": "CAR-003",
  "claim_id": "cycle 002's KILL was caused by transfer failure, not coordinate inadequacy",
  "quantity_credited": "I(A*; Z_a | Z_x) recoverable within an invariant pair",
  "coordinate_system": "same frozen 18 relational features; only the split differs",
  "attainable_range": {"chance": 0.5, "state_independent_ceiling": 0.6254, "state_specific_oracle": 1.0},
  "measured": {"T2_WITHIN": 0.6600, "T3_ACROSS": 0.5444, "delta": 0.1156,
               "T0_INSAMPLE": 0.6611, "B1_T2": 0.5581, "B1_T3": 0.5626,
               "conditional_signal_captured": 0.0924,
               "mean_pairwise_coefficient_cosine": 0.0652},
  "controls": {"positive_oracle_auc": 1.0, "cheat_shuffle_auc": 0.5000,
               "object_memorization_control_rise": -0.0045,
               "overfitting_gap_T0_minus_T2": 0.0011},
  "measured_over_which_rows": "5 seeds, 22 invariant pairs, median 1002 training states per pair, 1155 coefficient comparisons, population digest 1b4abb1a",
  "verdict": "ADEQUATE-WITHIN-REGION, INADEQUATE-ACROSS-REGIONS",
  "disposition": "REDESIGN",
  "what_earned_promotion": "cheap relational coordinates exceed the state-independent ceiling (0.6600 > 0.6254), capturing 9.2% of the conditional signal by arithmetic alone",
  "decision_this_changes": "learned transition representations remain NOT defensible; the open problem moves from H3 (coordinate adequacy) to H4 (transfer). Relation-type confounding must be excluded first.",
  "rows_ref": "cycle003_result.json"
}
```

*— Diomedes, cycle 003 result, 2026-08-24. Disposition REDESIGN. Next: cycle 004, the relation-type confound.*
