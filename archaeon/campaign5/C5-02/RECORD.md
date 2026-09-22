# C5-02 -- fair lateral ecology (screened worlds, equal total compute, attribution)

## A. STARTUP (preregistration; sealed sha256:93aa5b87b66ef2406dd356488eb82a04cefaad37baec7833dd3b0050726c66f6)

- experiment ID: C5-02
- parents: C4-09, C4-10
- QUESTION: Does lateral rescue produce reproducible improvement attributable to lateral entry, at EQUAL TOTAL COMPUTE, on worlds screened for headroom against every starting parent? Or is it takeover without improvement, or no effect?
- PARENT EVIDENCE: C4-09: rescues 335-460/seed, survival .30-.55, takeover, one live world improved in 1/3 seeds, extra compute .65-.74 not equalized; C4-10: three worlds pre-solved.
- WHY THIS SLOT IS STILL WORTH SPENDING: Phase A's second live signal, with only the identified defects repaired.
- ASSAY CAPABILITY REQUIREMENT: screen re-measured at run time equals the receipt ({'W2_K2d1': 0.5104, 'W2_K2_rand': 0.5417, 'W3_K3': 0.3819, 'W4_K4': 0.3021}; all < 0.70: True); B=0 lateral equals control (self-test); cheat; determinism; control total evaluations within one generation of the lateral arm's
- POSITIVE CONTROL: controls arm: screen_ok >= 1.0
- REACHABILITY ESTIMATE:
    {"note": "screened worlds; per-world lookups not applied"}
- ARMS:
    - lateral
    - control
    - controls
- COMMON-RANDOM-NUMBERS POLICY: identical seeds, starting subsamples and rng streams per world; the control's extra generations use the same streams continued
- BUDGET:
    {"B": 24, "E": 16, "G_lateral": 100, "N": 50, "heldout": 48, "screen_receipt": "archaeon/campaign5/WORLD_SCREEN_2026-09-18.json", "screen_sha256": "cbd74d4a560467e3eda57b815099215b3fc0e46405c72251dfc39b1118d12b5f", "seeds": [1, 2, 3, 4, 5, 6], "worlds": ["W2_K2d1", "W2_K2_rand", "W3_K3", "W4_K4"]}
- PRIMARY OBSERVABLE: per world: improvement (lateral - control final held-out >= 1/16) and attribution (elite carries rescued origin; first improvement probe at or after the first rescue into that world); outcome classes A/B/C; rescued share; compute equality per seed
- CLAIM CEILING: 6 seeds x 4 screened worlds at equal total compute; a count of attributable improvements; no mechanism
- FALSIFICATION CONDITION: B requires attributable improvement in >= 4 of 6 seeds on some world; else A (takeover) or C
- KILL CONDITION: screen mismatch or control failure -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
    - UNDERPOWERED
- EXPECTED MACHINE TELEMETRY:
    - per-world probes with elite origin
    - transfer matrix
    - first rescue generation
    - compute counts per arm
- MACHINE CHANGES EXERCISED:
    - equal-total-compute control
    - origin-based attribution with timing
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (Phase A, slot 2)
- decl (machine-read by archaeon.wse.states): {"n_min": 6, "positive_control": {"arm": "controls", "metric": "screen_ok", "min": 1.0, "min_rows": 1}, "primary": {"control": "control", "metric": "worlds_improved", "min_effect": 1.0, "treatment": "lateral"}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a01); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=UNDERPOWERED
- engine: live; worlds 1; artifacts 2; imports 0; records 12; errors 0
- timings (s): control_s=286.35, lateral_s=201.54, startup_s=0.06, teardown_s=0.01, total_s=491.3
- decisions: D5-006: control generations G_c = ceil(T_lateral / (4 x N)) per seed, computed from the lateral run's measured total; lateral runs first
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / rescues               s1      s2      s3      s4      s5      s6   sNone    mean    n
    control                      0       0       0       0       0       0       -   0.000    6
    controls                     -       -       -       -       -       -       -       -    0
    lateral                     24      12       1      63      24       9       -  22.167    6

    arm / worlds_improved       s1      s2      s3      s4      s5      s6   sNone    mean    n
    control                      0       0       0       0       0       0       -   0.000    6
    controls                     -       -       -       -       -       -       -       -    0
    lateral                      0       0       0       0       0       0       -   0.000    6

    arm / worlds_attributable      s1      s2      s3      s4      s5      s6   sNone    mean    n
    control                      0       0       0       0       0       0       -   0.000    6
    controls                     -       -       -       -       -       -       -       -    0
    lateral                      0       0       0       0       0       0       -   0.000    6

    arm / total_evals           s1      s2      s3      s4      s5      s6   sNone    mean    n
    control                  34800   35800   33200   36000   36000   32400       -  34700.000    6
    controls                     -       -       -       -       -       -       -       -    0
    lateral                  34667   35744   33086   35921   35903   32342       -  34610.500    6

- typed states fired: ['UNDERPOWERED']
    UNDERPOWERED  {"arms_below": {"controls": 1}, "n_min": 6}
- disposition candidate (machine): UNDERPOWERED -- fewer rows than the preregistered minimum
- claim ceiling (machine): none; preregistered ceiling: 6 seeds x 4 screened worlds at equal total compute; a count of attributable improvements; no mechanism

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"fair-ecology": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C5-02

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: UNDERPOWERED (machine candidate UNDERPOWERED). 
