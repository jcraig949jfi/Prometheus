# C5-08 -- robustness mechanism under B (length bins, dead-code ablation)

## A. STARTUP (preregistration; sealed sha256:75d08d0eb43e7a4184394172429a8f615a48d1fc02c911951a53fb5591ba8778)

- experiment ID: C5-08
- parents: C5-05, C4-07
- QUESTION: Under representation B, is single-edit robustness still neutrality plus length (dead code), and is the boundary's own contribution (FIZZLE minus FAIL) independent of dead code and equal to the executed-crossing rate?
- PARENT EVIDENCE: C4-07 (robustness = neutrality + length); C5-05 attempt a01 grammar-B rows
- WHY THIS SLOT IS STILL WORTH SPENDING: The directive's ablatable, length-matched robustness mechanism test.
- ASSAY CAPABILITY REQUIREMENT: ablation preserves OLD behaviour on the parent environment for every included parent; identity edits 100%; determinism
- POSITIVE CONTROL: controls arm: pass >= 1.0
- REACHABILITY ESTIMATE:
    {"note": "not a reach experiment"}
- ARMS:
    - controls
    - full
    - ablated
- COMMON-RANDOM-NUMBERS POLICY: ablated census seeds as C5-05 (seed_from('c5.05.edit', ...)) on the ablated genome; episodes as C4-01
- BUDGET:
    {"E": 16, "c5_05_attempt": "a01", "draws": 8, "full_rows": 5586, "parents": 57}
- PRIMARY OBSERVABLE: R_old/R_fail/R_fizz/GAP for full vs ablated, pooled and by length bin; M1-M4; reading
- CLAIM CEILING: single-edit robustness on 57 parents; the mechanism reading is structural, not evolutionary
- FALSIFICATION CONDITION: M2 failing with a larger ablated GAP -> the boundary adds robustness beyond dead code
- KILL CONDITION: ablation changes behaviour for > 10% of parents or control failure -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
- EXPECTED MACHINE TELEMETRY:
    - dead share per parent
    - per-row three-interpreter labels on ablated parents
- MACHINE CHANGES EXERCISED:
    - ablate (static_reachable)
    - census_parent_b on ablated parents
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (Phase B, slot 6)
- decl (machine-read by archaeon.wse.states): {"n_min": 57, "positive_control": {"arm": "controls", "metric": "pass", "min": 1.0, "min_rows": 1}, "primary": {"control": "full", "metric": "R_old", "min_effect": -0.0625, "treatment": "ablated"}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a01); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=UNDERPOWERED
- engine: live; worlds 1; artifacts 2; imports 0; records 1; errors 0
- timings (s): ablated_census_s=230.22, startup_s=0.05, teardown_s=0.07, total_s=233.2
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / R_old              sNone    mean    n
    ablated                  0.551   0.551    1
    controls                     -       -    0
    full                     0.551   0.551    1

    arm / R_fail             sNone    mean    n
    ablated                  0.493   0.493    1
    controls                     -       -    0
    full                     0.493   0.493    1

    arm / R_fizz             sNone    mean    n
    ablated                  0.565   0.565    1
    controls                     -       -    0
    full                     0.565   0.565    1

    arm / GAP                sNone    mean    n
    ablated                  0.072   0.072    1
    controls                     -       -    0
    full                     0.072   0.072    1

- typed states fired: ['UNDERPOWERED']
    UNDERPOWERED  {"arms_below": {"controls": 1}, "n_min": 57}
- disposition candidate (machine): UNDERPOWERED -- fewer rows than the preregistered minimum
- claim ceiling (machine): none; preregistered ceiling: single-edit robustness on 57 parents; the mechanism reading is structural, not evolutionary

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"robustness-mechanism-b": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C5-08

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: UNDERPOWERED (machine candidate UNDERPOWERED). 
