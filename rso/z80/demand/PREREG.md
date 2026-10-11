# C-017-T020 demand-gate decision rule (committed BEFORE the full run)

Pilot already seen (not the evidence): 2 seeds x 60 epochs, /tmp only, showed H_ENDO keeps function, NH_ENDO/BR_ENDO go extinct,
EXT arms keep function without a copier, RANDOM_EXT_GATED found an ECHO solver in 5/24 runs. Rule fixed after seeing that pilot, before
the committed run: 12 seeds/arm (24 for RANDOM), 200 epochs, seeds 17_020_001 + 100*arm + k, command in demand_gate.py.

Per arm: R_D = runs with D (functional copier, generation >= 10, re-derived from bytes); R_F = runs with any F; fF = sum_F / sum_pop.
Four readings, reported separately:
 1. CAPACITY (planted heritable function persists): H_ENDO_GATED R_D >= 10/12.
 2. HEREDITY IS WHAT KEEPS IT (vs non-heritable/broken, endogenous): NH_ENDO_* and BR_ENDO_* R_F <= 2/12 in both pressures.
 3. REWARD SELECTS IT: fF(H_ENDO_GATED) - fF(H_ENDO_IMPL) >= 0.10. Smaller => INDETERMINATE for reward, not "no".
 4. HEREDITY-SPECIFIC vs EXTERNAL reproduction: EXT arms keep F without a copier iff NH_EXT_* R_F >= 10/12 => "any reproduction keeps
    function; endogenous heredity is not NECESSARY, only SUFFICIENT". If EXT also loses F, heredity-specific.
World demands FUNCTIONAL HEREDITY iff 1 and 2 hold AND 4 shows EXT does not keep F. If 1,2 hold and 4 shows EXT keeps F, the world
demands REPRODUCTION of function (retention by any route) and the heredity question must be sharpened to provenance (who wrote the
bytes), not retention. If 1 fails, "not demanded at local budgets". Gate numbers are integers (runs); no float is a gate.
Lottery: RANDOM_ENDO_GATED births_endo expected ~0 (census 9.6e-6 x ~77 tapes x 24 runs ~ 0.02 expected); a nonzero count is reported
with its ancestry, not silently dropped.
