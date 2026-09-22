## A. STARTUP (preregistration; sealed sha256:4ff5b2a5aa1cc504bd05b52f766596ed5d735b979c6b610a7bf5378d57530a9d)

- experiment ID: C5-06
- parents: C5-05
- QUESTION: Does the boundary merely change how crossing programs die, or does skipping an executed fault preserve function that silent reinterpretation lost?
- PARENT EVIDENCE: C5-05 attempt a01 matched rows (OLD / B_FAIL / B_FIZZLE readings of the same child)
- WHY THIS SLOT IS STILL WORTH SPENDING: The directive's local failure vs local recovery test; gates C5-07.
- ASSAY CAPABILITY REQUIREMENT: cheat program reads BOTH_DIE; class assignment deterministic; replication on held-out episodes with three rng seeds
- POSITIVE CONTROL: controls arm: pass >= 1.0
- REACHABILITY ESTIMATE:
    {"note": "not a reach experiment"}
- ARMS:
    - controls
    - RECOVERY
    - BOTH_LIVE
    - INSULATION_LOSS
    - BOTH_DIE
- COMMON-RANDOM-NUMBERS POLICY: held-out family index 2, rng seeds 1-3, 16 episodes on the parent environment
- BUDGET:
    {"c5_05_attempt": "a01", "c5_05_children_digest": "3abf7efe288dc70de2cd5fc4074a2a96585b0563df5ec4861f2db4869597a18c", "c5_05_rows": 11172}
- PRIMARY OBSERVABLE: matched class table; replicated RECOVERY and INSULATION_LOSS counts; the fixed gate (>= 10 replicated recoveries and Wilson lower bound > .01)
- CLAIM CEILING: counts of single-edit events on 57 parents; no evolution
- FALSIFICATION CONDITION: gate fails -> LOCAL_FAILURE_ONLY and C5-07 skipped
- KILL CONDITION: control failure -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
    - LOCAL_FAILURE_ONLY
- EXPECTED MACHINE TELEMETRY:
    - per-event replicate reads
- MACHINE CHANGES EXERCISED:
    - matched-triple classifier
    - held-out replication
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (Phase B, slot 4)
- decl (machine-read by archaeon.wse.states): {"n_min": 1, "positive_control": {"arm": "controls", "metric": "pass", "min": 1.0, "min_rows": 1}, "primary": {"control": "INSULATION_LOSS", "metric": "replicated", "min_effect": 0.0, "treatment": "RECOVERY"}}
