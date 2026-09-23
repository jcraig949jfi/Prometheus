# C5-03 -- representation qualification (narrow encoding, FAIL/FIZZLE, fixtures without fitness)

## A. STARTUP (preregistration; sealed sha256:c0863125295f2ffe4422c74824b879c1586ffd39d8ec14f7b515b343fa5f9b89)

- experiment ID: C5-03
- parents: C4-01, C4-03
- QUESTION: Is representation B (narrow in-table encoding, FAIL/FIZZLE) a qualified instrument: does it preserve the old programs' meaning, and do raw, generator-valid and controlled-invalid populations separate WITHOUT fitness, with countable recovery?
- PARENT EVIDENCE: C4-01: total interpreter, 932/932 out-of-table words reinterpreted; C4-03: REPRESENTATION_BLOCKED, proxy only.
- WHY THIS SLOT IS STILL WORTH SPENDING: Phase B cannot start without a representation in which a local failure exists.
- ASSAY CAPABILITY REQUIREMENT: positive control (hand-made fault program) and cheat control (relabelled valid population) as in DESIGN.md
- POSITIVE CONTROL: controls arm: pass >= 1.0
- REACHABILITY ESTIMATE:
    {"note": "not a reach experiment"}
- ARMS:
    - controls
    - F1
    - F2
    - F3
    - F4
    - F5
    - F6
    - F7
    - F8
- COMMON-RANDOM-NUMBERS POLICY: fixed population seed 1, evaluation seed 3, four W0 episodes
- BUDGET:
    {"grammar_children": 1200, "n_per_population": 200, "parents": 57, "populations": ["raw", "valid", "injected_k1", "injected_k2", "injected_k4"]}
- PRIMARY OBSERVABLE: fixtures F1-F6 pass, F7 > 0 (F8 recorded); disposition REPRESENTATION_QUALIFIED / REPRESENTATION_FAILURE
- CLAIM CEILING: an instrument qualification; nothing about evolution, discovery or robustness
- FALSIFICATION CONDITION: any of F1-F6 failing its fixed threshold, or F7 = 0
- KILL CONDITION: control failure -> INSTRUMENT_INVALID; old VM digest changed -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - REPRESENTATION_FAILURE
    - INSTRUMENT_INVALID
- EXPECTED MACHINE TELEMETRY:
    - static validity counts
    - fault counts and sites
    - trap positions
    - grammar crossing by operator
- MACHINE CHANGES EXERCISED:
    - PlayerB
    - evaluate_b
    - gen_b
    - grammar_b
- REPLACEMENT CONDITION: none: a REPRESENTATION_FAILURE is a result (directive)
- ANCESTRY (original | replacement): original (Phase B, slot 1)
- decl (machine-read by archaeon.wse.states): {"n_min": 1, "positive_control": {"arm": "controls", "metric": "pass", "min": 1.0, "min_rows": 1}, "primary": {"control": "F2", "metric": "pass", "min_effect": 0.0, "treatment": "F3"}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a02); resumed_from: 1; replayed steps on the attempt of record: 11
    a01  errors=2 replayed=0 engine=True purpose=engine disposition_candidate=ENGINE_FAILURE
    a02  errors=0 replayed=11 engine=True purpose=engine disposition_candidate=WEAK_POSITIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 8; errors 0
- timings (s): startup_s=0.0, teardown_s=0.03, total_s=1.4
- decisions: D5-008: a02 AMENDMENT (post-hoc, a01 preserved): F3 raw-vs-injected2 measured on distinct fault SITES; F6 compares results with volatile timings stripped; failing fixtures recorded FALSIFIED, D5-007: representation B boundary = encoding only (opcode word < 25, read register fields < n_regs); addresses and offsets stay modulo tape; FAIL = whole evaluation
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / pass               sNone    mean    n
    F1                       1.000   1.000    1
    F2                       1.000   1.000    1
    F3                       1.000   1.000    1
    F4                       1.000   1.000    1
    F5                       1.000   1.000    1
    F6                       1.000   1.000    1
    F7                       1.000   1.000    1
    controls                 1.000   1.000    1

    arm / trap_share         sNone    mean    n
    F1                           -       -    0
    F2                           -       -    0
    F3                       1.000   1.000    1
    F4                           -       -    0
    F5                           -       -    0
    F6                           -       -    0
    F7                           -       -    0
    controls                     -       -    0

    arm / tvd_min            sNone    mean    n
    F1                           -       -    0
    F2                           -       -    0
    F3                       0.420   0.420    1
    F4                           -       -    0
    F5                           -       -    0
    F6                           -       -    0
    F7                           -       -    0
    controls                     -       -    0

- typed states fired: none
- disposition candidate (machine): WEAK_POSITIVE -- effect >= min_effect but n < 10 or a declared falsification attack failed or was not run
    evidence: {"control_mean": 1.0, "effect": 0.0, "min_effect": 0.0, "n_control": 1, "n_treatment": 1, "paired": 1, "paired_wins": 0, "treatment_mean": 1.0}
    battery: {"attacked": 0, "declared": 0, "survived": 0}
- claim ceiling (machine): weak; not for propagation; preregistered ceiling: an instrument qualification; nothing about evolution, discovery or robustness

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"representation-qualification": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C5-03

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: REPRESENTATION_QUALIFIED (machine candidate WEAK_POSITIVE). 
