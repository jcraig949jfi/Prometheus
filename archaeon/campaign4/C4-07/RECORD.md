# C4-07 -- the cost of insulation (REPRESENTATION_BLOCKED)

## A. STARTUP (preregistration; sealed sha256:ff8b154eadc35e650267dfe353f64372ca4f9f16e298fdf6da3e6ca08bd2e448)

- experiment ID: C4-07
- parents: C4-03
- QUESTION: Is graceful degradation useful only when it is free? Cost only the recovery/fizzle event. On this substrate no such event is distinguishable from ordinary execution (C4-03), so the frontier cannot be placed.
- PARENT EVIDENCE: C4-03 (D4-007): 932/932 parent instruction words out of the opcode table; P(would-be-fatal) = 1.000 on 7,146 children; the modulo decode is the instruction set.
- WHY THIS SLOT IS STILL WORTH SPENDING: The directive requires an attempted disposition for every experiment; this one is REPRESENTATION_BLOCKED and says why.
- ASSAY CAPABILITY REQUIREMENT: none: no assay is run
- POSITIVE CONTROL: none (no measurement)
- REACHABILITY ESTIMATE:
    {"note": "no search"}
- ARMS:
    - blocked
- COMMON-RANDOM-NUMBERS POLICY: n/a
- BUDGET:
    {"rows": 0}
- PRIMARY OBSERVABLE: none; the design digest and the C4-03 vacuity numbers are recorded
- CLAIM CEILING: a representation fact; the cost frontier is a Campaign 5 question on a substrate with a distinguishable insulation event
- FALSIFICATION CONDITION: n/a
- KILL CONDITION: n/a
- TYPED FAILURE CONDITIONS:
    - REPRESENTATION_BLOCKED
- EXPECTED MACHINE TELEMETRY:
    - one record carrying the design digest
- MACHINE CHANGES EXERCISED:
    - none
- REPLACEMENT CONDITION: none: the directive forbids converting REPRESENTATION_BLOCKED into a substrate change
- ANCESTRY (original | replacement): original (queue slot 7)
- decl (machine-read by archaeon.wse.states): {"n_min": 1}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a01); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=INCONCLUSIVE
- engine: live; worlds 1; artifacts 1; imports 0; records 1; errors 0
- timings (s): startup_s=0.03, teardown_s=0.01, total_s=0.3
- decisions: D4-011: C4-07 REPRESENTATION_BLOCKED; costing reduced operands or addresses would price the representation itself (a forbidden reward term); recommendation for Campaign 5 recorded in DESIGN.md
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / blocked            sNone    mean    n
    blocked                      1   1.000    1

- typed states fired: none
- disposition candidate (machine): INCONCLUSIVE -- no primary comparison declared or no rows
- claim ceiling (machine): none; preregistered ceiling: a representation fact; the cost frontier is a Campaign 5 question on a substrate with a distinguishable insulation event

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"blocked": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C4-07

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: REPRESENTATION_BLOCKED (machine candidate INCONCLUSIVE). 
