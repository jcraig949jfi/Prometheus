## A. STARTUP (preregistration; sealed sha256:db60e6c40c72149e927ff9aafc2c327a4e84833d5332a68b918b89ca654fa6a9)

- experiment ID: C5-07
- parents: C5-06, C5-05
- QUESTION: What does skipping an executed fault cost the recovered program: compute, second-edit fragility, function elsewhere?
- PARENT EVIDENCE: C5-06 a02: 229 replicated recoveries of 1449 executed-crossing children
- WHY THIS SLOT IS STILL WORTH SPENDING: The directive's conditional cost-of-insulation slot; C5-06 read REAL_LOCAL_RECOVERY.
- ASSAY CAPABILITY REQUIREMENT: the parent's second-edit neutral share here equals C5-05's grammar-B FIZZLE neutral share for the same parent (same seeds); determinism
- POSITIVE CONTROL: controls arm: pass >= 1.0
- REACHABILITY ESTIMATE:
    {"note": "not a reach experiment"}
- ARMS:
    - controls
    - children
    - parents
- COMMON-RANDOM-NUMBERS POLICY: second edits seeded seed_from('c5.05.edit', 20260922, key, 'B', op, draw) with key = child digest / parent id
- BUDGET:
    {"c5_05_attempt": "a01", "c5_06_attempt": "a02", "draws": 8, "parents": 44, "recovered_children": 229}
- PRIMARY OBSERVABLE: K1 median ratio and > 1.10 share; K2 pooled diff and per-child counts; K3 share; reading INSULATION_COSTLY / INSULATION_CHEAP
- CLAIM CEILING: costs of single-edit recovery on 57 parents' lineages; no evolution
- FALSIFICATION CONDITION: K2 cost or K1 > 1.10 share >= .50 -> INSULATION_COSTLY
- KILL CONDITION: parent control mismatch -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
- EXPECTED MACHINE TELEMETRY:
    - per-child K1/K3
    - per-child second-edit label counts
- MACHINE CHANGES EXERCISED:
    - second_edit_neutral
    - costs
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (Phase B, slot 5)
- decl (machine-read by archaeon.wse.states): {"n_min": 10, "positive_control": {"arm": "controls", "metric": "pass", "min": 1.0, "min_rows": 1}, "primary": {"control": "parents", "metric": "share", "min_effect": -0.0625, "treatment": "children"}}
