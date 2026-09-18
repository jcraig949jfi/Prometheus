# C4-10 -- held-out evolvability trial

## A. STARTUP (preregistration; sealed sha256:f67271efb47aab42cdea2c97f6ca565f61592ba3d09bc2cc0ee179186e5bfc09)

- experiment ID: C4-10
- parents: C4-01, C4-02, C4-05, C4-06, C4-08, C4-09
- QUESTION: On a held-out family of four worlds never used to develop any C4 condition, do the conditions selected by the preregistered rule (NONE qualified) lose less at the damage boundary, recover non-trivial variation, and reach further than the frozen baseline at equal budget?
- PARENT EVIDENCE: {"mutation_load": {"ancestral_loss": {"band95": [0.4081, 0.4294], "k": 3463, "p": 0.4187}, "perturbed_loss": {"band95": [0.118, 0.1315], "k": 1138, "p": 0.1246}, "ancestral_coherent": {"band95": [0.1417, 0.1571], "k": 1234, "p": 0.1492}, "perturbed_coherent": {"band95": [0.0396, 0.048], "k": 398, "p": 0.0436}, "loss_decreased_bands_apart": true, "coherent_increased": false, "qualifies": false}, "lateral": {"P1": {"held": true, "stated": "rescue survival >= .25", "values": [0.4043, 0.3049, 0.5463]}, "P2": {"held": false, "per_world": {"W0": 0, "W1_d1": 0, "W1_d4": 0, "W2_K2": 1}, "stated": "some world improved by >= 1/16 in >= 2 of 3 seeds"}, "qualifies": false}}
- WHY THIS SLOT IS STILL WORTH SPENDING: The decisive experiment; its rule was fixed before C4-08/C4-09 reported.
- ASSAY CAPABILITY REQUIREMENT: starting best held-out < 0.75 on every family world (measured {'W1_d2': 1.0, 'W1_d3': 1.0, 'W2_K2d1': 0.5312, 'W0_8b': 1.0}; worlds at or above are dropped: ['W1_d2', 'W1_d3', 'W0_8b']); baseline shelf on W1_d2 in >= 2 of 4 seeds; determinism; cheat
- POSITIVE CONTROL: baseline: shelf on W1_d2 in >= 2 of 4 seeds
- REACHABILITY ESTIMATE:
    {"note": "held-out family; no prior rows"}
- ARMS:
    - baseline
- COMMON-RANDOM-NUMBERS POLICY: identical seeds, identical starting subsamples, identical rng streams per world; conditions differ only in their operator (n_ops=2) or the lateral step
- BUDGET:
    {"E": 16, "G": 60, "N": 200, "family": ["W1_d2", "W1_d3", "W2_K2d1", "W0_8b"], "heldout": 48, "lateral_B": 24, "novel_min": 0.75, "seeds": [1, 2, 3, 4]}
- PRIMARY OBSERVABLE: per condition: fatal mutation mass and nontrivial yield per birth (Wilson), behavioural diversity, lineage depth, cross-world transfer, novel-capability cells, compute, useful descendants per birth; the three-part claim rule
- CLAIM CEILING: n=4 seeds x 4 worlds; a comparison at one budget on one substrate
- FALSIFICATION CONDITION: no condition satisfies part 1 -> NEGATIVE or NO_CONDITION_SELECTED; the baseline rows stand regardless
- KILL CONDITION: control failure -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
    - NO_CONDITION_SELECTED
    - ROBUST_BUT_INERT
    - LOCALITY_WITHOUT_EVOLVABILITY
- EXPECTED MACHINE TELEMETRY:
    - per (condition, seed, world) births/fatal/nontrivial/diversity/depth/transfer/probes
    - selection evidence
- MACHINE CHANGES EXERCISED:
    - condition selection from committed tables
    - family worlds W1_d3 / W2_K2d1 / W0_8b first runs
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (queue slot 10)
- decl (machine-read by archaeon.wse.states): {"n_min": 4, "positive_control": {"arm": "baseline", "metric": "shelf_W1_d2", "min": 1, "min_rows": 2}, "primary": {"control": "baseline", "metric": "fatal_mass", "min_effect": -0.05, "treatment": "baseline"}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a01); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=WEAK_POSITIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 4; errors 0
- timings (s): startup_s=0.03, teardown_s=0.02, total_s=186.6, trial_s=184.29
- decisions: D4-014: conditions selected by the preregistered rule from committed tables: NONE; evidence recorded in the sealed preregistration
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / fatal_mass            s1      s2      s3      s4    mean    n
    baseline                 0.260   0.265   0.259   0.258   0.260    4

    arm / nontrivial_yield      s1      s2      s3      s4    mean    n
    baseline                 0.740   0.735   0.742   0.742   0.740    4

    arm / novel_cells           s1      s2      s3      s4    mean    n
    baseline                     3       3       3       3   3.000    4

    arm / heldout_mean          s1      s2      s3      s4    mean    n
    baseline                 0.883   0.880   0.888   0.883   0.883    4

- typed states fired: none
- disposition candidate (machine): WEAK_POSITIVE -- effect >= min_effect but n < 10 or a declared falsification attack failed or was not run
    evidence: {"control_mean": 0.2603, "effect": 0.0, "min_effect": -0.05, "n_control": 4, "n_treatment": 4, "paired": 4, "paired_wins": 0, "treatment_mean": 0.2603}
    battery: {"attacked": 0, "declared": 0, "survived": 0}
- claim ceiling (machine): weak; not for propagation; preregistered ceiling: n=4 seeds x 4 worlds; a comparison at one budget on one substrate

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"trial": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C4-10

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: WEAK_POSITIVE (machine candidate WEAK_POSITIVE). 
