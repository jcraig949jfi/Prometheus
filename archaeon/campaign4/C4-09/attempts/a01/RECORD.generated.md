# C4-09 -- lateral exaptation / paired ecology

## A. STARTUP (preregistration; sealed sha256:b49dc8e5020a80f67abd760c15caea1696431298e279839b3a2a15e9935bbc49)

- experiment ID: C4-09
- parents: C4-05, C4-06
- QUESTION: Are useful stepping stones destroyed merely because they are bad at the environment that produced their parent? Four fixed worlds; a below-floor non-degenerate child is evaluated on the other three (bounded budget B=24 per world per generation) and enters a world only because of its measured reward there.
- PARENT EVIDENCE: C4-01: D6 exaptive 34/5,472 single edits (30 shelf); C4-05: depth-16 walkers exaptive .043; C4-06: no crossing at G=100.
- WHY THIS SLOT IS STILL WORTH SPENDING: The campaign's POET-like test without assuming POET is the answer; the only slot that lets a failure in one world be a success in another.
- ASSAY CAPABILITY REQUIREMENT: self-test: determinism; B=0 lateral equals control trace for trace; cheat; walker digests equal C4-05's (188/188)
- POSITIVE CONTROL: control arm: every world reaches the shelf (train >= .45) in >= 2 of 3 seeds (the walkers start on or near it)
- REACHABILITY ESTIMATE:
    {"note": "four-world ecology; per-world reachability lookups not applied"}
- ARMS:
    - control
    - lateral
- COMMON-RANDOM-NUMBERS POLICY: identical seeds, identical starting subsamples per world, identical rng streams; the arms differ only in the lateral step
- BUDGET:
    {"B": 24, "E": 16, "G": 100, "N": 50, "heldout": 48, "seeds": [1, 2, 3], "walkers": 188, "worlds": ["W0", "W1_d1", "W1_d4", "W2_K2"]}
- PRIMARY OBSERVABLE: rescues and the transfer matrix; rescue survival at G=100; per-world held-out best vs control; distinct held-out elite values; extra compute ratio; P1 and P2 as stated; the overhead failure shape
- CLAIM CEILING: n=3 seeds; a count of rescues and their fates on four fixed worlds; no mechanism
- FALSIFICATION CONDITION: overhead: rescue survival < .10 AND no world improved by >= 1/16 in >= 2 seeds
- KILL CONDITION: control failure -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
    - UNDERPOWERED
- EXPECTED MACHINE TELEMETRY:
    - per-world traces and probes
    - transfer matrix
    - rescue log
    - compute counts
- MACHINE CHANGES EXERCISED:
    - multi-world evolver loop
    - inject() as the lateral entry path
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (queue slot 9)
- decl (machine-read by archaeon.wse.states): {"n_min": 3, "primary": {"control": "control", "metric": "worlds_improved", "min_effect": 1.0, "treatment": "lateral"}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a01); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 6; errors 0
- timings (s): ecology_s=174.47, startup_s=0.04, teardown_s=0.02, total_s=194.2
- decisions: D4-013: lateral entry rule = measured reward on the receiving world >= floor AND fitness >= that world's current median; candidates in organism-id order (no ranking), at most B per world per generation; inject replaces the receiving world's worst members
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / rescues               s1      s2      s3    mean    n
    control                      0       0       0   0.000    3
    lateral                    460     446     335  413.667    3

    arm / rescue_survival       s1      s2      s3    mean    n
    control                      -       -       -       -    0
    lateral                  0.404   0.305   0.546   0.419    3

    arm / extra_compute_ratio      s1      s2      s3    mean    n
    control                  0.000   0.000   0.000   0.000    3
    lateral                  0.739   0.728   0.646   0.704    3

    arm / worlds_improved       s1      s2      s3    mean    n
    control                      0       0       0   0.000    3
    lateral                      1       0       0   0.333    3

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.0, "effect": 0.3333, "min_effect": 1.0, "n_control": 3, "n_treatment": 3, "paired": 3, "paired_wins": 1, "treatment_mean": 0.3333}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: n=3 seeds; a count of rescues and their fates on four fixed worlds; no mechanism

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"ecology": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C4-09

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). 
