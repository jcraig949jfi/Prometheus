## A. STARTUP (preregistration; sealed sha256:07aa70486fcd99f66797738090b90a20c74b22aaebe38269e9cef0df2b1aac9e)

- experiment ID: C5-09
- parents: C5-02, C5-05
- QUESTION: At equal total compute on screened worlds with headroom, does evolution under representation B discover more than under the old representation, and is any gain the representation's or the grammar's?
- PARENT EVIDENCE: C5-02 (elite flat at the starting parent, 0/24 cells); C5-05 geometry under B; C5-03 F8 crossing 9.3%.
- WHY THIS SLOT IS STILL WORTH SPENDING: The directive's reach/discovery test; feeds C5-10's committed rule.
- ASSAY CAPABILITY REQUIREMENT: determinism of OLD_v04 seed 1; identical gen-0 programs across arms (digest); starting best <= screen receipt
- POSITIVE CONTROL: controls arm: pass >= 1.0
- REACHABILITY ESTIMATE:
    {"note": "screened worlds (WORLD_SCREEN_2026-09-18.json)"}
- ARMS:
    - OLD_v04
    - OLD_B
    - B_FAIL
    - B_FIZZLE
    - controls
- COMMON-RANDOM-NUMBERS POLICY: same seeds, same starting subsample, same evolver rng streams per world in every arm; only (evaluator, grammar) differ
- BUDGET:
    {"E": 16, "G": 100, "N": 50, "evals_per_arm_seed": 20000, "seeds": [1, 2, 3, 4, 5, 6], "worlds": ["W2_K2d1", "W2_K2_rand", "W3_K3", "W4_K4"]}
- PRIMARY OBSERVABLE: per-cell WON/LOST/TIED vs OLD_v04 on final held-out (band 1/16); net per arm; DISCOVERY_GAIN / GRAMMAR_GAIN / NO_GAIN
- CLAIM CEILING: 24 cells per arm; a count; C5-10 replicates any selection on held-out worlds
- FALSIFICATION CONDITION: prediction NO_GAIN is lost if any B arm reaches net >= +4 with OLD_B < +4
- KILL CONDITION: control failure -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
- EXPECTED MACHINE TELEMETRY:
    - probes per 10 generations with crossing/trapped/faulted shares
    - elite length and fault sites
- MACHINE CHANGES EXERCISED:
    - EvolutionB (pluggable evaluator and grammar)
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (Phase B, slot 7)
- decl (machine-read by archaeon.wse.states): {"n_min": 6, "positive_control": {"arm": "controls", "metric": "pass", "min": 1.0, "min_rows": 1}, "primary": {"control": "OLD_v04", "metric": "heldout_final", "min_effect": 0.0625, "treatment": "B_FIZZLE"}}
