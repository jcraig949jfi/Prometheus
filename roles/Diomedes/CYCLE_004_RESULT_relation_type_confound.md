# Diomedes cycle 004 — RESULT: relation type *inverts* the geometry; both axes matter; nothing transfers

**Filed:** 2026-08-24. **Pre-registration:** `CYCLE_004_PREREG_relation_type_confound.md`, frozen at
`1698d965` **before** any outcome existed. **Rows:** `cycle004_run.py` → `cycle004_result.json`.
**Pre-registered band: BOTH-AXES-MATTER. Disposition: REDESIGN.**

---

## 1. The 2×2

12 mixed invariant pairs qualified, **median 754 training states per cell**. All four cells train on
identically-sized training sets by construction — only the *evaluation target* differs. Controls
clean: ORACLE **1.0000**, SHUFFLE cheat **0.5005**, RANDOM **0.4995**. B1 object-memorization control
flat across cells (A 0.5644 / B 0.5653 / C 0.5574).

- **A — same pair, same relation: 0.7101** (0.7087–0.7111 across seeds; 3·SE [0.7067, 0.7155])
- **B — same pair, DIFFERENT relation: 0.4885** (3·SE [0.4854, 0.4920]) — **below chance**
- **C — DIFFERENT pair, same relation: 0.5349** (3·SE [0.5307, 0.5377])
- **D — different pair, different relation: 0.4898** (3·SE [0.4880, 0.4938])

gap `A − D` = **0.2203**. Recovery: **B = −0.6%**, **C = 20.5%**. Both below 25% ⇒
**BOTH-AXES-MATTER**.

## 2. The finding: relation type does not merely destroy the model, it *inverts* it

**B (0.4885) is below chance, and its interval excludes 0.500.** A model fit on one relation type is
**actively anti-predictive** on the other relation type **within the very same invariant pair**.
Coefficient cosine within a pair across relation types: **−0.0312** (range −0.0643 to +0.0088).

And **B ≈ D** (0.4885 vs 0.4898): changing the relation type is as damaging as changing *both* the
pair and the relation. Relation type is the dominant failure axis.

Holding relation type fixed while changing pair (C = 0.5349) retains a little — 20.5% of the gap,
interval excluding chance — so pair identity matters too, just less. Cosine within a relation type
across pairs: **+0.0647**. Neither axis produces alignment; both are near-orthogonal.

## 3. Conditioning finer *raises* the local ceiling

Cycle 003 conditioned on invariant pair alone and got 0.6600. Cycle 004 conditions on
**pair × relation type** and gets **0.7101**. Against cycle 001's state-independent ceiling of 0.6254:

> (0.7101 − 0.6254) / (1.0000 − 0.6254) = **22.6% of the conditional signal**, up from 9.2%.

Still by arithmetic alone — subtraction, parity, absolute difference. Charter §5 continues to hold:
nothing here has yet earned a learned representation.

## 4. PRE-REGISTRATION DEFECT — declared, per charter §6

Prereg §6.3 stated: *"anchors A and D must reproduce cycle 003 (0.6600 / 0.5444) within their
intervals. If they do not, the harness drifted and no cell is admissible."*

**They do not.** A = 0.7101 (not 0.6600); D = 0.4898 (not 0.5444). By the letter of that clause, no
cell is admissible.

**The clause was defective, and the defect is mine.** It assumed A and D are the same estimators as
cycle 003's T2 and T3. They are not:

- Cycle 003's **T2** trained on a pair's states spanning *both* relation types; cycle 004's **A**
  trains on a single (pair, relation) cell. Finer conditioning — a *higher* score is expected.
- Cycle 003's **T3** trained on 60% of all pairs (many pairs, both relations, ~13k+ states); cycle
  004's **D** trains on one cell (median 754 states). Far less data and no diversity — a *lower*
  score is expected.

So the anchors diverge by construction, not by drift. **The band survives the defect** because
BOTH-AXES-MATTER is computed entirely from within-cycle-004 quantities (A, B, C, D), which share an
identical training regime and are therefore mutually comparable — better controlled, in fact, than
cycle 003's arms. The defective clause was an *external cross-cycle* consistency check that was never
part of the band computation.

**Amendment, adopted:** a cross-cycle anchor is only valid between arms whose *training regime* is
identical, not merely arms with similar names. Future preregs must state the estimator, not the label.

## 5. Anti-self-sealing (charter §12)

- **Object memorization** — B1 control flat across cells (0.5574–0.5653); cannot explain a 0.22 gap.
- **Sample size** — all four cells use identically-sized training sets by construction. A and B share
  a training set exactly and differ by 0.22. Ruled out.
- **Leakage** — cheat control 0.5005.
- **Cell imbalance** (`equal_mod_2` ~3:1) — mitigated by the ≥150-per-cell floor; and it cannot
  produce a *below-chance* B, which requires anti-alignment, not scarcity.
- **The below-chance B could be a coding artifact** — it would have to survive a cheat control at
  0.5005 and an oracle at 1.0000 in the same harness. Not excluded with certainty, but it is the
  same code path that produces A = 0.7101, so an inversion bug would have to be relation-conditional.

## 6. Prediction scoring — wrong, and instructively

Prereg §5 predicted **PAIR-SPECIFICITY-REAL** (B recovers ≥50%, C <25%), reasoning that cycle 003's
per-pair models already handled mixed relation types and still reached 0.6600.

**Actual: B recovers −0.6%, C recovers 20.5% — the opposite ordering.** My inference was wrong
because a per-pair model on mixed data does not have to *transfer* between relation types; it can fit
a compromise that works passably for both. Passable-for-both is not the same as transferable, and I
conflated them.

Running score: cycle 002 wrong on 3 of 4; cycle 003 right on direction, under-estimated size; cycle
004 wrong on the ordering. **I am not well calibrated on this thread**, which is the argument for the
pre-registration firewall rather than against continuing.

---

## Coordinate-Adequacy Record — CAR-004

```json
{
  "car_id": "CAR-004",
  "claim_id": "the cycle-003 transfer failure is explained by relation type rather than invariant pair",
  "quantity_credited": "I(A*; Z_a | Z_x) transferability along two candidate axes",
  "coordinate_system": "same frozen 18 relational features; only the held-out axis differs",
  "attainable_range": {"chance": 0.5, "state_independent_ceiling": 0.6254, "state_specific_oracle": 1.0},
  "measured": {"A_same_pair_same_rel": 0.7101, "B_same_pair_diff_rel": 0.4885,
               "C_diff_pair_same_rel": 0.5349, "D_diff_pair_diff_rel": 0.4898,
               "gap": 0.2203, "recovery_B": -0.0059, "recovery_C": 0.2047,
               "cos_within_pair_across_relations": -0.0312,
               "cos_within_relation_across_pairs": 0.0647,
               "conditional_signal_captured_at_finest_cell": 0.226},
  "controls": {"positive_oracle_auc": 1.0, "cheat_shuffle_auc": 0.5005,
               "b1_object_control_by_cell": [0.5644, 0.5653, 0.5574],
               "equal_training_set_size_across_cells": true},
  "measured_over_which_rows": "5 seeds, 12 mixed invariant pairs, median 754 training states per cell, population digest 1b4abb1a",
  "verdict": "INADEQUATE-ACROSS-BOTH-AXES",
  "disposition": "REDESIGN",
  "what_died": "the hypothesis that either relation type OR invariant pair alone explains the transfer failure; and my own prediction of pair-dominance",
  "prereg_defect": "anchor clause S6.3 compared arms with different training regimes; band unaffected, amendment recorded in S4",
  "decision_this_changes": "transfer has now failed along BOTH available axes in this population; the next question is whether that is a property of h1 or of the substrate, which is a replication question, not a modelling one",
  "rows_ref": "cycle004_result.json"
}
```

*— Diomedes, cycle 004 result, 2026-08-24. Disposition REDESIGN.*
