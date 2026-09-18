## A. STARTUP (preregistration; sealed sha256:222115bb859cddf71b23773fd1fd614415c44bfc46d69fcbfa3495ebf2e08977)

- experiment ID: C5-04
- parents: C5-03, C4-01
- QUESTION: Generator or representation: which one decides whether a sampled program lives or dies, measured without selection?
- PARENT EVIDENCE: C5-03 fixtures (static and dynamic separation); C4-01 total interpreter.
- WHY THIS SLOT IS STILL WORTH SPENDING: The directive's control before any damage geometry is read on representation B.
- ASSAY CAPABILITY REQUIREMENT: positive control injected(2) x B_FAIL trapped >= .50; identity control valid x OLD == valid x B_FAIL program for program (non-writable)
- POSITIVE CONTROL: controls arm: pass >= 1.0
- REACHABILITY ESTIMATE:
    {"note": "not a reach experiment"}
- ARMS:
    - raw x OLD
    - raw x B_FAIL
    - raw x B_FIZZLE
    - valid x OLD
    - valid x B_FAIL
    - valid x B_FIZZLE
    - injected2 x OLD
    - injected2 x B_FAIL
    - injected2 x B_FIZZLE
    - controls
- COMMON-RANDOM-NUMBERS POLICY: population seed s gives the same programs to every interpreter; W0 train index 1, rng 0
- BUDGET:
    {"cells": 27, "n": 200, "seeds": [1, 2, 3]}
- PRIMARY OBSERVABLE: viable and floor shares per cell; predictions P1-P4 (DESIGN.md)
- CLAIM CEILING: a 3 x 3 table under no selection; no mechanism
- FALSIFICATION CONDITION: P1 failing means the old generator was not neutral under OLD (affects every C4 census)
- KILL CONDITION: control failure -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
- EXPECTED MACHINE TELEMETRY:
    - per-cell shares
    - per-program rewards
- MACHINE CHANGES EXERCISED:
    - gen_b.population
    - evaluate_b
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (Phase B, slot 2)
- decl (machine-read by archaeon.wse.states): {"n_min": 3, "positive_control": {"arm": "controls", "metric": "pass", "min": 1.0, "min_rows": 1}, "primary": {"control": "raw x OLD", "metric": "viable", "min_effect": -0.0625, "treatment": "raw x B_FIZZLE"}}
