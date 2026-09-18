## A. STARTUP (preregistration; sealed sha256:ef5a72a231893b1ab30df6d77e74dfddec6b8fe66cc7214358447ff6a11a3a6c)

- experiment ID: C5-05
- parents: C4-01, C5-03, C5-04
- QUESTION: Under representation B, does a real local failure boundary change how programs die (a TRAP bin absorbing D2/D3 death) while leaving the neutral and exaptive bins of non-crossing children where they were?
- PARENT EVIDENCE: C4-01 (D-taxonomy on the total interpreter; D7 = 0; cliff); C5-03 F8 (grammar B crosses in 9.3% of children); C5-04 (P1-P4 hold).
- WHY THIS SLOT IS STILL WORTH SPENDING: The directive's damage geometry replication with predefined bins; matched perturbations feed C5-06.
- ASSAY CAPABILITY REQUIREMENT: arm R equals C4-01 a02 label for label and digest for digest; identity/randomize/cheat controls as in DESIGN.md
- POSITIVE CONTROL: controls arm: pass >= 1.0
- REACHABILITY ESTIMATE:
    {"note": "not a reach experiment"}
- ARMS:
    - controls
    - R
    - v04 x OLD
    - v04 x B_FAIL
    - v04 x B_FIZZLE
    - B x OLD
    - B x B_FAIL
    - B x B_FIZZLE
- COMMON-RANDOM-NUMBERS POLICY: one child per (parent, grammar, operator, draw) from seed_from('c5.05.edit', 20260922, ...); the same child under all three interpreters; episodes as C4-01
- BUDGET:
    {"E": 16, "draws": 8, "grammars": ["v04", "B"], "interpreters": ["OLD", "B_FAIL", "B_FIZZLE"], "operators": 12, "parents": 57}
- PRIMARY OBSERVABLE: bin distributions per grammar x interpreter (x operator); T1-T6; controls; R replication receipt
- CLAIM CEILING: single-edit geometry on 57 parents; no evolution; no claim about discovery
- FALSIFICATION CONDITION: T1 < .50 (boundary mostly unexecuted) or T2 fails (boundary disturbs non-crossing children) -> the boundary is not what it was designed to be
- KILL CONDITION: R arm mismatch or control failure -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
- EXPECTED MACHINE TELEMETRY:
    - per-child rows with three interpreter readings
    - crossing flag
    - faults and sites
- MACHINE CHANGES EXERCISED:
    - classify_b (DT/DF before the C4 classifier)
    - grammar B census
    - matched-perturbation rows
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (Phase B, slot 3; C4-01 replayed)
- decl (machine-read by archaeon.wse.states): {"n_min": 57, "positive_control": {"arm": "controls", "metric": "pass", "min": 1.0, "min_rows": 1}, "primary": {"control": "B x OLD", "metric": "d6_rate", "min_effect": -0.0625, "treatment": "B x B_FAIL"}}
