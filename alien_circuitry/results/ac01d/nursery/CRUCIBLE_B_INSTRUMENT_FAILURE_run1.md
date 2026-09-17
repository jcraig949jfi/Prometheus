# CRUCIBLE-B run 1: INSTRUMENT FAILURE (infeasible control), preserved

Filed 2026-09-14. No held result was ever written or read.

## What happened

`crucible_b.py` (executing PREREG_C_B.md section B, frozen at d3b9533) started 2026-09-13 18:55:28 and ran for about
11 hours at 100% CPU with an empty log (`run_log_crucible_b.txt`, 0 bytes). Two `py-spy dump` samples of the live
process (PID 24972), taken minutes apart on 2026-09-14, both showed the main thread at:

    random_macros (alien_circuitry\nursery\crucibles\crucible_b.py:47)
    run (alien_circuitry\nursery\crucibles\crucible_b.py:157)

The no-macros and mined arms had been evaluated in memory; their results were never written (the runner writes only
at the end), so no held number was observed by anyone.

## Why (proof)

`results/ac01d/nursery/crucible_b_mining_and_control_feasibility.json`, recomputed from FIT problems only:

- mined macros (k = 6): (1,0), (0,2), (0,1), (0,0), (2,1), (2,0), i.e. swap-cycle, cycle-collapse, cycle-swap,
  cycle-cycle, collapse-swap, collapse-cycle; counts 9044, 5869, 5310, 4996, 4453, 1822 over 2,000 FIT oracle paths
  (mean path length 16.7);
- all six are length 2, because the frozen no-prefix/no-suffix rule excludes every frequent length-3 and length-4
  subsequence once its length-2 prefix or suffix is chosen;
- over the 3-generator alphabet there are 9 length-2 sequences; 6 are mined, 3 remain;
- the preregistered control requires 6 random sequences of the same lengths excluding the mined set: 6 > 3, so the
  rejection sampler in `random_macros` can never terminate.

The control as written is infeasible in this world. This is a specification defect in the preregistration, not a
scientific result about macros.

## Disposition

- Hung processes terminated after identity check (`crucible_b_hung_processes_killed.json`).
- The frozen runner and this failure are preserved unchanged.
- Repair follows as a preregistration ADDENDUM committed before any rerun, sized by a timing diagnostic run on VAL
  problems only.
