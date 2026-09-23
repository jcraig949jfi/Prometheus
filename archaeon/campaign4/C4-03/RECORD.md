# C4-03 -- local failure vs global death (static proxy; HARD executed = REPRESENTATION_BLOCKED)

## A. STARTUP (preregistration; sealed sha256:f480bae71126726f696a19c95d651b9d1cd0a142b2a8fd50fa06f2c26ca0c333)

- experiment ID: C4-03
- parents: C4-01, C4-02
- QUESTION: When one edited operation becomes invalid, is search better served by killing the program variant (HARD) or by letting the invalid operation do nothing (FIZZLE)? HARD cannot be executed on this substrate (D4-002); the static proxy reads what FIZZLE made of would-be-fatal children.
- PARENT EVIDENCE: C4-01 (54ce467f2): 5,472 single edits, D7 = 0, displacement bimodal; C4-02 (300f9d4e4): loss monotone in radius. D4-002: total interpreter, no fault status.
- WHY THIS SLOT IS STILL WORTH SPENDING: The directive's critical distinction -- does insulation preserve coherent variation or merely convert fatal to inert -- is answerable on the committed rows without a substrate change; the executed HARD arm is recorded REPRESENTATION_BLOCKED, not converted into an ISA change.
- ASSAY CAPABILITY REQUIREMENT: positive 57/57 injected fatal detected; negative 57/57 identity predicates equal parent's; integrity: every regenerated child digest equals the committed child_digest (5,472 + 2,280); cheat: a D7 fatal row counts coherent
- POSITIVE CONTROL: arm parents_control: injected_fatal_detected >= 1.0 on 57/57
- REACHABILITY ESTIMATE:
    {"note": "no search; static proxy over committed rows"}
- ARMS:
    - hard_executed
    - proxy_fatal_reachable
    - proxy_fatal_present
    - parents_control
- COMMON-RANDOM-NUMBERS POLICY: no evaluation; children regenerated from the C4-01/C4-02 seeds
- BUDGET:
    {"c401_children": 5472, "c402_children": 2280, "fatal_definition": "opcode word >= 25 at an instruction start", "parents": 57}
- PRIMARY OBSERVABLE: P(fatal_present), P(fatal_reachable) per operator/stratum/radius; among reachable would-be-fatal children the FIZZLE class distribution, coherent share (D3/D4/D6/D7 or D5 with displacement > 0) with Wilson band, to_D2 and to_D3_D7 masses; the same among non-fatal children
- CLAIM CEILING: what share of the substrate's measured variation sits on fizzled operations, and of what kind; NOT what a real HARD interpreter would do to search (static proxies over-count)
- FALSIFICATION CONDITION: INERT_CONVERSION: coherent share among reachable would-be-fatal children < 0.10 or Wilson lower bound < 0.05
- KILL CONDITION: any control or integrity failure -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
    - REPRESENTATION_BLOCKED (hard_executed arm, by construction)
- EXPECTED MACHINE TELEMETRY:
    - fatal predicates per child and parent
    - share tables by operator/stratum/radius
    - integrity counts
- MACHINE CHANGES EXERCISED:
    - deterministic child regeneration from committed seeds (no evaluation)
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (queue slot 3)
- decl (machine-read by archaeon.wse.states): {"n_min": 1, "positive_control": {"arm": "parents_control", "metric": "injected_fatal_detected", "min": 1.0, "min_rows": 1}, "primary": {"control": "proxy_nonfatal", "metric": "coherent_share", "min_effect": -0.1, "treatment": "proxy_fatal_reachable"}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a01); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=INCONCLUSIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 18; errors 0
- timings (s): startup_s=0.03, teardown_s=0.02, total_s=1.5
- decisions: D4-007: HARD executed arm REPRESENTATION_BLOCKED (D4-002); proxy = static out-of-table opcode word (present / reachable); operands and addresses excluded because their reduction is published semantics
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / p_fatal_reachable   sNone    mean    n
    hard_executed                -       -    0
    parents_control              -       -    0
    proxy_fatal_reachable    1.000   1.000    1
    proxy_nonfatal               -       -    0

    arm / coherent_share_fatal   sNone    mean    n
    hard_executed                -       -    0
    parents_control              -       -    0
    proxy_fatal_reachable    0.109   0.109    1
    proxy_nonfatal               -       -    0

    arm / coherent_share_nonfatal   sNone    mean    n
    hard_executed                -       -    0
    parents_control              -       -    0
    proxy_fatal_reachable        -       -    0
    proxy_nonfatal               -       -    0

    arm / to_D2_fatal        sNone    mean    n
    hard_executed                -       -    0
    parents_control              -       -    0
    proxy_fatal_reachable    0.476   0.476    1
    proxy_nonfatal               -       -    0

- typed states fired: none
- disposition candidate (machine): INCONCLUSIVE -- an arm of the primary comparison has no rows
- claim ceiling (machine): none; preregistered ceiling: what share of the substrate's measured variation sits on fizzled operations, and of what kind; NOT what a real HARD interpreter would do to search (static proxies over-count)

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"proxy": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C4-03

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: INCONCLUSIVE (machine candidate INCONCLUSIVE). 
