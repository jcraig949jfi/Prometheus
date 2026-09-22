## A. STARTUP (preregistration; sealed sha256:2123bdc1c5ecca77db315a90cf8c0fd4ade38361e87124196635370806097679)

- experiment ID: C5-10
- parents: C5-09
- QUESTION: Does the condition C5-09 selected (if any) replicate on two held-out worlds with held-out seeds, against OLD_v04 at equal total compute?
- PARENT EVIDENCE: C5-09 attempt a01: nets {"OLD_B": 0, "B_FAIL": 1, "B_FIZZLE": 1}
- WHY THIS SLOT IS STILL WORTH SPENDING: The directive's held-out trial; NO_CONDITION_SELECTED is a success of the rule.
- ASSAY CAPABILITY REQUIREMENT: held-out worlds unused by every earlier slot (True); rule digest sealed
- POSITIVE CONTROL: controls arm: pass >= 1.0
- REACHABILITY ESTIMATE:
    {"note": "screened held-out worlds (receipt): W3_K3d1 .375, W2_K2d4 .552"}
- ARMS:
    - controls
    - OLD_v04
    - NONE
- COMMON-RANDOM-NUMBERS POLICY: held-out seeds 11-16; starting subsample keyed by seed; same evolver streams in both arms
- BUDGET:
    {"E": 16, "G": 100, "N": 50, "c5_09_attempt": "a01", "rule_sha256": "6414f2f098ceaeb9ec9ebf2f48a0c2ca3efa3a873e39db3528e4f6babc9fdf91", "seeds": [11, 12, 13, 14, 15, 16], "selected": null, "worlds": ["W3_K3d1", "W2_K2d4"]}
- PRIMARY OBSERVABLE: RULE.md: net cells >= 2 of 12 and no cell lost by >= 2/16 -> REPLICATED
- CLAIM CEILING: one selected condition on two held-out worlds
- FALSIFICATION CONDITION: FAILED_TO_REPLICATE
- KILL CONDITION: held-out world previously used -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - NO_CONDITION_SELECTED
    - FAILED_TO_REPLICATE
    - INSTRUMENT_INVALID
- EXPECTED MACHINE TELEMETRY:
    - per-cell held-out finals
- MACHINE CHANGES EXERCISED:
    - rule reader
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (Phase B, slot 8)
- decl (machine-read by archaeon.wse.states): {"n_min": 1, "positive_control": {"arm": "controls", "metric": "pass", "min": 1.0, "min_rows": 1}, "primary": {"control": "OLD_v04", "metric": "heldout_final", "min_effect": 0.0625, "treatment": "NONE"}}
