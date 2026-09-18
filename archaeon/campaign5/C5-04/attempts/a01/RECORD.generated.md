# C5-04 -- generator x representation control (no selection)

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

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a01); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=UNDERPOWERED
- engine: live; worlds 1; artifacts 2; imports 0; records 27; errors 0
- timings (s): cells_s=0.6, startup_s=0.03, teardown_s=0.03, total_s=2.0
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / viable                s1      s2      s3   sNone    mean    n
    controls                     -       -       -       -       -    0
    injected2 x B_FAIL       0.015   0.020   0.015       -   0.017    3
    injected2 x B_FIZZLE     0.100   0.120   0.135       -   0.118    3
    injected2 x OLD          0.145   0.180   0.185       -   0.170    3
    raw x B_FAIL             0.000   0.000   0.000       -   0.000    3
    raw x B_FIZZLE           0.000   0.000   0.000       -   0.000    3
    raw x OLD                0.160   0.190   0.160       -   0.170    3
    valid x B_FAIL           0.145   0.170   0.135       -   0.150    3
    valid x B_FIZZLE         0.150   0.170   0.135       -   0.152    3
    valid x OLD              0.150   0.170   0.135       -   0.152    3

    arm / floor                 s1      s2      s3   sNone    mean    n
    controls                     -       -       -       -       -    0
    injected2 x B_FAIL       0.000   0.000   0.000       -   0.000    3
    injected2 x B_FIZZLE     0.000   0.000   0.000       -   0.000    3
    injected2 x OLD          0.000   0.000   0.000       -   0.000    3
    raw x B_FAIL             0.000   0.000   0.000       -   0.000    3
    raw x B_FIZZLE           0.000   0.000   0.000       -   0.000    3
    raw x OLD                0.000   0.000   0.000       -   0.000    3
    valid x B_FAIL           0.000   0.000   0.000       -   0.000    3
    valid x B_FIZZLE         0.000   0.000   0.000       -   0.000    3
    valid x OLD              0.000   0.000   0.000       -   0.000    3

    arm / trapped               s1      s2      s3   sNone    mean    n
    controls                     -       -       -       -       -    0
    injected2 x B_FAIL       0.840   0.850   0.805       -   0.832    3
    injected2 x B_FIZZLE     0.000   0.000   0.000       -   0.000    3
    injected2 x OLD          0.000   0.000   0.000       -   0.000    3
    raw x B_FAIL             1.000   1.000   1.000       -   1.000    3
    raw x B_FIZZLE           0.000   0.000   0.000       -   0.000    3
    raw x OLD                0.000   0.000   0.000       -   0.000    3
    valid x B_FAIL           0.010   0.000   0.005       -   0.005    3
    valid x B_FIZZLE         0.000   0.000   0.000       -   0.000    3
    valid x OLD              0.000   0.000   0.000       -   0.000    3

    arm / faulted               s1      s2      s3   sNone    mean    n
    controls                     -       -       -       -       -    0
    injected2 x B_FAIL       0.840   0.850   0.805       -   0.832    3
    injected2 x B_FIZZLE     0.840   0.850   0.805       -   0.832    3
    injected2 x OLD          0.000   0.000   0.000       -   0.000    3
    raw x B_FAIL             1.000   1.000   1.000       -   1.000    3
    raw x B_FIZZLE           1.000   1.000   1.000       -   1.000    3
    raw x OLD                0.000   0.000   0.000       -   0.000    3
    valid x B_FAIL           0.010   0.000   0.005       -   0.005    3
    valid x B_FIZZLE         0.010   0.000   0.005       -   0.005    3
    valid x OLD              0.000   0.000   0.000       -   0.000    3

- typed states fired: ['UNDERPOWERED']
    UNDERPOWERED  {"arms_below": {"controls": 1}, "n_min": 3}
- disposition candidate (machine): UNDERPOWERED -- fewer rows than the preregistered minimum
- claim ceiling (machine): none; preregistered ceiling: a 3 x 3 table under no selection; no mechanism

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"generator-x-representation": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C5-04

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: UNDERPOWERED (machine candidate UNDERPOWERED). 
