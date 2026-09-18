# C5-01 -- deep neutral walk (depth 64)

## A. STARTUP (preregistration; sealed sha256:8e96396d1d8613bebd2d354abd054d172a6502c34fccc7a5a8195f4a446fa6b1)

- experiment ID: C5-01
- parents: C4-05
- QUESTION: Does held-out exaptation continue increasing materially beyond neutral depth 16, or has the network entered a yield plateau? Marginal discovery yield per accepted step and per evaluation, not monotonicity.
- PARENT EVIDENCE: C4-05: depths 2/4/8/16 = .016/.032/.037/.043 (single edit .006); 188/188 walkers reached 16; acceptance ~.55.
- WHY THIS SLOT IS STILL WORTH SPENDING: Phase A of the substrate-decision campaign: the first of the two live C4 signals, closed cheaply.
- ASSAY CAPABILITY REQUIREMENT: walkers 1-4 reproduce C4-05's depth-16 steps digest for digest; identity walker depth 64 in 64; randomize-all stalls; determinism; cheat
- POSITIVE CONTROL: controls arm: positive_ok >= 1.0
- REACHABILITY ESTIMATE:
    {"note": "acceptance walk; no search"}
- ARMS:
    - viable
    - degenerate_gen0
    - controls
- COMMON-RANDOM-NUMBERS POLICY: C4-05's episode sets and walker seeds (campaign_seed 20260921 for the walks, so walkers 1-4 ARE C4-05's); walkers 5-6 new draws from the same rule
- BUDGET:
    {"E": 16, "archive_depths": [0, 16, 32, 48, 64], "depth": 64, "max_proposals": 32, "parents": 57, "walkers": 6}
- PRIMARY OBSERVABLE: exaptation rate by depth with Wilson bands; yield per evaluation by depth; marginal rate per accepted step between archives; acceptance by bin; the three branches; PRESERVE rule (continued gradient AND Y_64 >= 2 x .0012)
- CLAIM CEILING: a rate curve at 6 walkers x 64 steps per competent parent on one substrate; no mechanism
- FALSIFICATION CONDITION: PLATEAU or DEGRADATION or MIXED -> the neutral mechanism is not preserved for Phase A's disposition
- KILL CONDITION: control failure -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
    - UNDERPOWERED
- EXPECTED MACHINE TELEMETRY:
    - steps with proposals per walker
    - archived exposures at 5 depths
    - yield table
- MACHINE CHANGES EXERCISED:
    - C4-05 walk reused with a deeper archive set
    - yield-per-evaluation accounting
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (Phase A, slot 1)
- decl (machine-read by archaeon.wse.states): {"n_min": 1, "positive_control": {"arm": "controls", "metric": "positive_ok", "min": 1.0, "min_rows": 1}, "primary": {"control": "degenerate_gen0", "metric": "exaptation_64", "min_effect": 0.02, "treatment": "viable"}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a01); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=WEAK_POSITIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 57; errors 0
- timings (s): startup_s=0.03, teardown_s=0.01, total_s=51.7, walk_s=48.22
- decisions: D5-003 applied: 6 walkers, depth 64, archives 0/16/32/48/64; walkers 1-4 = C4-05's seeds; yield per evaluation counts proposals + 5 exposures per archived walker
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / connected_depth    sNone    mean    n
    controls                     -       -    0
    degenerate_gen0             64  64.000    1
    viable                      64  64.000    1

    arm / exaptation_64      sNone    mean    n
    controls                     -       -    0
    degenerate_gen0          0.000   0.000    1
    viable                   0.167   0.167    1

    arm / ref_break_share    sNone    mean    n
    controls                     -       -    0
    degenerate_gen0          0.078   0.078    1
    viable                   0.112   0.112    1

- typed states fired: none
- disposition candidate (machine): WEAK_POSITIVE -- effect >= min_effect but n < 10 or a declared falsification attack failed or was not run
    evidence: {"control_mean": 0.0, "effect": 0.0816, "min_effect": 0.02, "n_control": 10, "n_treatment": 47, "paired": 1, "paired_wins": 1, "treatment_mean": 0.0816}
    battery: {"attacked": 0, "declared": 0, "survived": 0}
- claim ceiling (machine): weak; not for propagation; preregistered ceiling: a rate curve at 6 walkers x 64 steps per competent parent on one substrate; no mechanism

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"deepwalk": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C5-01

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: WEAK_POSITIVE (machine candidate WEAK_POSITIVE). 
