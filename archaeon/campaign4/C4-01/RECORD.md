# C4-01 -- damage-boundary census

## A. STARTUP (preregistration; sealed sha256:fa448c85f5d898e287512c026bf2ff136e30976e9c77c7770adc0d7f1e5e516f)

- experiment ID: C4-01
- parents: C3-SFE-01, C3-SFE-03, C3-SFE-04
- QUESTION: Where does the frozen substrate destroy variation? For each of the 12 grammar operators applied once to each of the 57 starting program variants (8 draws), the distribution over D0..D7 and the behavioral displacement conditional on executing.
- PARENT EVIDENCE: Campaigns 1-3: repeated boundaries where edits stop producing informative phenotypes (unreachable summits, inert shelves). The interpreter is TOTAL (D4-002): D1 cannot fire; D0 is post-edit validation only.
- WHY THIS SLOT IS STILL WORTH SPENDING: Establishes the actual damage boundary before any attempt to move it (C4-03, C4-07, C4-08); fills the first column of the damage geometry map.
- ASSAY CAPABILITY REQUIREMENT: controls: identity edit 57/57 D5 with displacement 0; whole-genome randomization >= 45/57 destroyed (D2 or D3); the D7 detector reads D7 on a hand-set reward (cheat); one parent's rows reproduce byte-for-byte on rerun
- POSITIVE CONTROL: control_randomize_all arm: destroyed (D2+D3 share) >= 1.0 on >= 45 of 57 parents
- REACHABILITY ESTIMATE:
    {"note": "not a search; no reachability lookup applies (evaluation census)"}
- ARMS:
    - insertion
    - deletion
    - duplication
    - movement
    - replacement
    - operand_perturbation
    - reference_redirection
    - region_swap
    - splice
    - randomization
    - unreachable_removal
    - config_perturbation
    - control_identity
    - control_randomize_all
- COMMON-RANDOM-NUMBERS POLICY: one fixed episode set per environment (family train, index 1, E=16) shared by every parent and child; edits seeded from (campaign_seed, organism_id, operator, draw)
- BUDGET:
    {"E": 16, "band": 0.0625, "draws": 8, "environments": ["W0", "W0_heldout", "W1_d1", "W1_d4", "W2_K2"], "floor": 0.1875, "operators": 12, "other_envs": ["W0_heldout", "W1_d1", "W1_d4", "W2_K2"], "parent_env": {"delay_general": "W1_d4", "gen0_random": "W0", "shelf": "W2_K2", "w0_solver": "W0"}, "parents": 57}
- PRIMARY OBSERVABLE: P(Dk | operator), P(Dk | operator, stratum), P(Dk | region) with Wilson bands and eligible counts; displacement histogram by operator; pairwise total-variation distance between operators' D-distributions
- CLAIM CEILING: a measured map at 8 draws per (parent, operator) on one frozen substrate; no mechanism; no evolvability claim
- FALSIFICATION CONDITION: every operator pair has TVD < 0.05 (all classes look alike), or region UNKNOWN for > 20% of applied edits, or D0 > 50% of edits (the instrument cannot say where loss occurs) -> NEGATIVE, recorded, nothing fixed in C4-01
- KILL CONDITION: a control fails -> INSTRUMENT_INVALID; the slot stops and the defect is recorded
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
    - UNDERPOWERED
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - flow table D0..D7 by operator / stratum / region
    - displacement histograms
    - per-child raw evaluate() dicts on 4 environments
    - structural descriptors before/after
    - operator args with touched positions
- MACHINE CHANGES EXERCISED:
    - campaign-4 harness (D4-001)
    - classifier D4-003
    - total-interpreter accounting (D1 eligible 0)
- REPLACEMENT CONDITION: none: first slot
- ANCESTRY (original | replacement): original (queue slot 1)
- decl (machine-read by archaeon.wse.states): {"n_min": 57, "positive_control": {"arm": "control_randomize_all", "metric": "destroyed", "min": 1.0, "min_rows": 45}, "primary": {"control": "operand_perturbation", "metric": "loss_rate", "min_effect": 0.05, "treatment": "randomization"}, "readout_control": {"arm": "control_identity", "chance": 0.0, "metric": "identity_ok", "min_above": 0.99}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a02); resumed_from: 1; replayed steps on the attempt of record: 803
    a02  errors=0 replayed=803 engine=True purpose=engine disposition_candidate=WEAK_POSITIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 798; errors 0
- timings (s): census_s=41.87, startup_s=0.0, teardown_s=0.01, total_s=44.7
- decisions: D4-001..D4-004 applied; the census refuses while the gate is RED; controls are rows in the same table
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / loss_rate          sNone    mean    n
    config_perturbation      0.250   0.250    1
    control_identity         0.000   0.000    1
    control_randomize_all    1.000   1.000    1
    deletion                 0.750   0.750    1
    duplication                  -       -    0
    insertion                    -       -    0
    movement                 0.875   0.875    1
    operand_perturbation     0.625   0.625    1
    randomization            0.875   0.875    1
    reference_redirection    0.000   0.000    1
    region_swap              1.000   1.000    1
    replacement              0.750   0.750    1
    splice                   0.833   0.833    1
    unreachable_removal          -       -    0

    arm / neutral_rate       sNone    mean    n
    config_perturbation      0.625   0.625    1
    control_identity         1.000   1.000    1
    control_randomize_all    0.000   0.000    1
    deletion                 0.250   0.250    1
    duplication                  -       -    0
    insertion                    -       -    0
    movement                 0.125   0.125    1
    operand_perturbation     0.375   0.375    1
    randomization            0.125   0.125    1
    reference_redirection    1.000   1.000    1
    region_swap              0.000   0.000    1
    replacement              0.250   0.250    1
    splice                   0.167   0.167    1
    unreachable_removal          -       -    0

    arm / improved_rate      sNone    mean    n
    config_perturbation      0.000   0.000    1
    control_identity         0.000   0.000    1
    control_randomize_all    0.000   0.000    1
    deletion                 0.000   0.000    1
    duplication                  -       -    0
    insertion                    -       -    0
    movement                 0.000   0.000    1
    operand_perturbation     0.000   0.000    1
    randomization            0.000   0.000    1
    reference_redirection    0.000   0.000    1
    region_swap              0.000   0.000    1
    replacement              0.000   0.000    1
    splice                   0.000   0.000    1
    unreachable_removal          -       -    0

    arm / exaptive_rate      sNone    mean    n
    config_perturbation      0.125   0.125    1
    control_identity         0.000   0.000    1
    control_randomize_all    0.000   0.000    1
    deletion                 0.000   0.000    1
    duplication                  -       -    0
    insertion                    -       -    0
    movement                 0.000   0.000    1
    operand_perturbation     0.000   0.000    1
    randomization            0.000   0.000    1
    reference_redirection    0.000   0.000    1
    region_swap              0.000   0.000    1
    replacement              0.000   0.000    1
    splice                   0.000   0.000    1
    unreachable_removal          -       -    0

    arm / displacement_mean   sNone    mean    n
    config_perturbation      0.355   0.355    1
    control_identity         0.000   0.000    1
    control_randomize_all    0.938   0.938    1
    deletion                 0.711   0.711    1
    duplication                  -       -    0
    insertion                    -       -    0
    movement                 0.824   0.824    1
    operand_perturbation     0.602   0.602    1
    randomization            0.844   0.844    1
    reference_redirection    0.000   0.000    1
    region_swap              0.926   0.926    1
    replacement              0.711   0.711    1
    splice                   0.823   0.823    1
    unreachable_removal          -       -    0

- typed states fired: none
- disposition candidate (machine): WEAK_POSITIVE -- effect >= min_effect but n < 10 or a declared falsification attack failed or was not run
    evidence: {"control_mean": 0.3772, "effect": 0.3794, "min_effect": 0.05, "n_control": 57, "n_treatment": 57, "paired": 1, "paired_wins": 1, "treatment_mean": 0.7566}
    battery: {"attacked": 0, "declared": 0, "survived": 0}
- claim ceiling (machine): weak; not for propagation; preregistered ceiling: a measured map at 8 draws per (parent, operator) on one frozen substrate; no mechanism; no evolvability claim

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"census": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C4-01

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: WEAK_POSITIVE (machine candidate WEAK_POSITIVE). 
