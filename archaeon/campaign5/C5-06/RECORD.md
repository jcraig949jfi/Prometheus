# C5-06 -- local failure versus local recovery (matched perturbations, held-out replication)

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

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a02); resumed_from: 1; replayed steps on the attempt of record: 0
    a02  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=WEAK_POSITIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 4; errors 0
- timings (s): replicate_s=14.38, startup_s=0.05, teardown_s=0.05, total_s=15.6
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / count              sNone    mean    n
    BOTH_DIE                   467  467.000    1
    BOTH_LIVE                  591  591.000    1
    INSULATION_LOSS            157  157.000    1
    RECOVERY                   234  234.000    1
    controls                     -       -    0

    arm / replicated         sNone    mean    n
    BOTH_DIE                     0   0.000    1
    BOTH_LIVE                    0   0.000    1
    INSULATION_LOSS            154  154.000    1
    RECOVERY                   229  229.000    1
    controls                     -       -    0

- typed states fired: none
- disposition candidate (machine): WEAK_POSITIVE -- effect >= min_effect but n < 10 or a declared falsification attack failed or was not run
    evidence: {"control_mean": 154.0, "effect": 75.0, "min_effect": 0.0, "n_control": 1, "n_treatment": 1, "paired": 1, "paired_wins": 1, "treatment_mean": 229.0}
    battery: {"attacked": 0, "declared": 0, "survived": 0}
- claim ceiling (machine): weak; not for propagation; preregistered ceiling: counts of single-edit events on 57 parents; no evolution

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"local-recovery": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C5-06

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: REAL_LOCAL_RECOVERY (machine candidate WEAK_POSITIVE). 
