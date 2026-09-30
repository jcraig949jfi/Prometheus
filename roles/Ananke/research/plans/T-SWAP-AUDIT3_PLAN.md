# T-SWAP-AUDIT3 PLAN (frozen by commit before any AUDIT3 run)

Thread thr-5df816e9b844, experiment E-ANANKE-W-Z (delegated worker; must NOT
edit this file; deviations go in its own PLAN_ADDENDUM.md before the affected
run). Authority: CWO 2026-09-30 ANANKE queue + MWO-0004 R2. Cap: 8 CPU
core-hours. No GPU (CUDA_VISIBLE_DEVICES=). COMMON_RULES_ARC3 s5 applies: a
failed known-answer gate stops the item before any specimen run.

## 1 Purpose
Apply the promoted relative swap verdict (prometheus/ananke/swap_rel.py, REL4
"H2") to the audited CHANCE verdicts with PAIR ARRAYS SAVED, to (a) resolve
the 64 rows W-U could only bound from W-O's saved marginals
(workers/W-U/out/rel3_733.csv, status AMBIGUOUS; 31 groups), and (b) produce a
group-level carrier table (unit = source x specimen x offset group, not arm;
Harmonia/W-Q: arms in a group share the normal run).

## 2 Scope (in this order, stop launching at 7.5 core-h)
1. All 31 groups containing an AMBIGUOUS row (all arms of each group).
2. Remaining groups in ascending sha256(source|specimen|offset) order.
Report coverage (groups and rows done).

## 3 Runs
Exactly W-O's specimen loading, arm definitions and recorded offsets
(workers/W-O/{runner.py, audit.py, inventory.py}), SINGLE-trial swaps only,
M = 512 worlds, NEW namespace assays.world_seeds(0x680, 512), all scored
trials of the recorded design. Save per (group, arm): pair-mean arrays a
(normal) and s (swap) per trial (npz, compact). Label with
swap_rel.from_pairs (REL3 p_min passed as W-W's module documents), plus the
paired z CI transfer class (COMPLETE/PARTIAL/OVERSHOOT) for every FLIP_REL.

## 4 Frozen outputs and predictions
- Row table: new label per row next to W-O absolute, W-Q REL2 and W-U REL3
  bounds. Prediction Pa: >= 70% of the 64 AMBIGUOUS rows resolve to their
  REL2 label (W-U showed each could only drop to INDETERMINATE).
- Group table: per group, the set of arms with FLIP_REL, and the group class:
  CARRIER-NAMED (>= 1 FLIP_REL arm, COMPLETE), CARRIER-PARTIAL (FLIP_REL only
  PARTIAL), NO-CARRIER-FOUND (no FLIP_REL; >= 1 NO_EFFECT_REL or CHANCE_REL),
  UNDECIDED (only INDETERMINATE / NOT_ELIGIBLE). Prediction Pb: CARRIER-NAMED
  in 25-45% of covered groups.
- Consistency check: for rows that were DETERMINED in W-U, the new label must
  equal W-U's REL3 label in >= 95% of rows (different seeds; disagreement
  beyond that is reported as an instrument or seed-sensitivity finding, not
  fixed).

## 5 Known answers (before any specimen run)
- swap_rel test suite passes (prometheus/ananke/tests/test_swap_rel.py).
- One W-L champion (W-N: FLIP, S carrier, z ~ -1) must read FLIP_REL COMPLETE
  on S; a pure latch plant (prometheus/ananke/plants.py hold_latch) must read
  NO_EFFECT_REL on channel_all. Must-fail: the latch's site_all fed to the
  NO_EFFECT check reads FLIP_REL.

## 6 Resources
<= 8 CPU core-hours, Fabric lease skullport:cpu8 for > 2 threads (else <= 2
threads unleased), outputs <= 8 MB.
