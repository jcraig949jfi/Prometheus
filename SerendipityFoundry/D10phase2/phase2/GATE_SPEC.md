# D-10 Phase 2 -- FROZEN CAPACITY-GATE SPECIFICATION

Frozen BEFORE any evaluation on the gate set. The gate set has not been
touched by any construction, screening, or diagnostic run up to this point;
all PP2 construction used the disjoint DEV set.

## 1. Frozen material
- Corpus: `d10/phase2/dataset.json` field `corpus_hex`, 4110 content-deduped
  genotypes, built by the frozen Phase-1 corpus rule with the repaired
  harness. Never regenerated for the gate.
- Gate tasks: `dataset.json` field `gate_tasks`, 24 tasks = 8 seen families
  x 3 members, generated with `GEN_SEED=8181`, members 7..9 of each family.
  Disjoint from history members 0..3 and dev members 4..6.
- Acquisition seeds: `derive_seed(9301, "gate", str(task_index), str(s))`
  for s in 0..3. Identical across every arm.
- Retrieval tie-break seed: `derive_seed(9302, "gateret", str(task_index))`.
- k = 4 injected genotypes; POP_SIZE = 24; B_EVAL = 400 evaluations.
- KA/KQ step limit: `organizer.KEY_MAX_STEPS = 300`, wall backstop
  `KEY_WALL_S = 3600` (D7: can never bind first).
- Genotype bound: `acquire.MAX_GENOTYPE_BYTES = 1024` (D4).
- R2 derangement: `family_block_derangement(gate_families,
  derive_seed(9303, "sigma", "gate"))` -- a permutation with
  `family[sigma(i)] != family[i]` for every i, asserted at run time and
  recorded. Realised same-family rate MUST be exactly 0.

## 2. Arms (all at identical seeds, budget and population size)
- `U`        k uniform corpus samples
- `R2(PP2)`  PP2's own artifact keys; each task's query key replaced by
             `sigma(task)`'s query key. Identical machinery, task-conditional
             coupling destroyed.
- `PP2`      the single pre-declared PP2 candidate
- `PP1`      privileged oracle calibration anchor (top-k by true train
             fitness). Reported, never admissible as evidence.
- `PN`       planted negative (below)

## 3. Pre-declared PP2 candidate
The candidate is fixed before the gate runs and is named in
`d10/phase2/pp2_selection.json`, chosen by best DEV `PP2 - R2`. No further
tuning after selection.

## 4. Planted negative (mechanism-matched)
`PN = (KA of the chosen PP2, KQ = constant)`: identical artifact-side
organization, identical retrieval machinery, identical key width and
geometry, but the query side is `PUSH1 0`, so retrieval is
query-independent by construction. It preserves superficial key/retrieval
mechanics while lacking any task-conditional relevance. It MUST fail the
gate.

## 5. Unit of analysis and statistic
- Unit: the GATE TASK (n = 24). Trials within a task are not independent.
- Per task t: `d_t = rate_PP2(t) - rate_R2(t)` over the 4 matched seeds.
- Test: exact one-sided sign-flip permutation test over {d_t}, all 2^24
  sign vectors approximated by 200000 draws with a fixed seed, alpha = 0.05,
  direction PP2 > R2 pre-declared.
- Reported alongside: mean d, bootstrap CI over tasks, and per-arm rates.

## 6. PASS CRITERIA -- all must hold
1. `mean(d_t) >= DELTA_MIN` with `DELTA_MIN = 0.03` absolute test-exact
   solve rate. Justification, fixed in advance: the measured conditional
   headroom on DEV is `ORACLE_COND - ORACLE_UNCOND = 0.1979 - 0.0729
   = 0.125`; the gate requires PP2 to capture at least 25% of it
   (0.25 x 0.125 = 0.031), the same 25% rule Phase 1 pre-registered.
2. One-sided permutation p < 0.05.
3. No boundary violation: `test_boundary.py`, `test_query_firewall.py` and
   `test_repairs.py` all pass, and no `NondeterministicKey` is raised.
4. No cost violation: KA and KQ each within KEY_MAX_STEPS; every arm's
   realised acquisition evaluations <= B_EVAL (cap-parity); VM steps
   reported per arm.
5. The planted negative does NOT satisfy criteria 1 and 2.
6. If criteria 1-5 hold, a nuisance check must additionally show the effect
   is not reproduced by a key built from the reconstructible nuisance
   variables alone.

## 7. Invalidation conditions
- Realised same-family rate of sigma is not 0.
- Any arm's realised evaluations exceed B_EVAL.
- A `NondeterministicKey` is raised.
- The gate tasks are found to intersect the history or dev pools.
- PP1 fails to exceed U on the gate set (the assay has lost its headroom).

## 8. Diagnostics permitted ONLY after the primary result is frozen
- Reinterpretation of the identical PP2 keys under at most two alternative
  supplied comparisons (unsigned 64-bit numeric distance; common-prefix
  length). No redesign, no retraining, and these may not rescue a failed
  Hamming PP2.
- A shared 64-bit permutation of bit positions, which must leave Hamming
  results invariant.
