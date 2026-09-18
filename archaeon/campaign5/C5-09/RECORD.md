# C5-09 -- reach / discovery at equal total compute: OLD_v04, OLD_B, B_FAIL, B_FIZZLE

## A. STARTUP (preregistration; sealed sha256:07aa70486fcd99f66797738090b90a20c74b22aaebe38269e9cef0df2b1aac9e)

- experiment ID: C5-09
- parents: C5-02, C5-05
- QUESTION: At equal total compute on screened worlds with headroom, does evolution under representation B discover more than under the old representation, and is any gain the representation's or the grammar's?
- PARENT EVIDENCE: C5-02 (elite flat at the starting parent, 0/24 cells); C5-05 geometry under B; C5-03 F8 crossing 9.3%.
- WHY THIS SLOT IS STILL WORTH SPENDING: The directive's reach/discovery test; feeds C5-10's committed rule.
- ASSAY CAPABILITY REQUIREMENT: determinism of OLD_v04 seed 1; identical gen-0 programs across arms (digest); starting best <= screen receipt
- POSITIVE CONTROL: controls arm: pass >= 1.0
- REACHABILITY ESTIMATE:
    {"note": "screened worlds (WORLD_SCREEN_2026-09-18.json)"}
- ARMS:
    - OLD_v04
    - OLD_B
    - B_FAIL
    - B_FIZZLE
    - controls
- COMMON-RANDOM-NUMBERS POLICY: same seeds, same starting subsample, same evolver rng streams per world in every arm; only (evaluator, grammar) differ
- BUDGET:
    {"E": 16, "G": 100, "N": 50, "evals_per_arm_seed": 20000, "seeds": [1, 2, 3, 4, 5, 6], "worlds": ["W2_K2d1", "W2_K2_rand", "W3_K3", "W4_K4"]}
- PRIMARY OBSERVABLE: per-cell WON/LOST/TIED vs OLD_v04 on final held-out (band 1/16); net per arm; DISCOVERY_GAIN / GRAMMAR_GAIN / NO_GAIN
- CLAIM CEILING: 24 cells per arm; a count; C5-10 replicates any selection on held-out worlds
- FALSIFICATION CONDITION: prediction NO_GAIN is lost if any B arm reaches net >= +4 with OLD_B < +4
- KILL CONDITION: control failure -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
- EXPECTED MACHINE TELEMETRY:
    - probes per 10 generations with crossing/trapped/faulted shares
    - elite length and fault sites
- MACHINE CHANGES EXERCISED:
    - EvolutionB (pluggable evaluator and grammar)
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (Phase B, slot 7)
- decl (machine-read by archaeon.wse.states): {"n_min": 6, "positive_control": {"arm": "controls", "metric": "pass", "min": 1.0, "min_rows": 1}, "primary": {"control": "OLD_v04", "metric": "heldout_final", "min_effect": 0.0625, "treatment": "B_FIZZLE"}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a02); resumed_from: 1; replayed steps on the attempt of record: 29
    a01  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=POSITIVE_CONTROL_FAILED
    a02  errors=0 replayed=29 engine=True purpose=engine disposition_candidate=UNDERPOWERED
- engine: live; worlds 1; artifacts 2; imports 0; records 24; errors 0
- timings (s): arms_s=333.0, startup_s=0.0, teardown_s=0.05, total_s=467.1
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / heldout_final         s1      s2      s3      s4      s5      s6   sNone    mean    n
    B_FAIL                   0.297   0.302   0.297   0.302   0.302   0.297       -   0.299    6
    B_FIZZLE                 0.323   0.297   0.302   0.302   0.297   0.297       -   0.303    6
    OLD_B                    0.323   0.302   0.297   0.302   0.297   0.297       -   0.303    6
    OLD_v04                  0.297   0.297   0.297   0.302   0.297   0.297       -   0.298    6
    controls                     -       -       -       -       -       -       -       -    0

    arm / first_gain_gen        s1      s2      s3      s4      s5      s6   sNone    mean    n
    B_FAIL                       -       -       -       -       -       -       -       -    0
    B_FIZZLE                     -       -       -       -       -       -       -       -    0
    OLD_B                        -       -       -       -       -       -       -       -    0
    OLD_v04                      -       -       -       -       -       -       -       -    0
    controls                     -       -       -       -       -       -       -       -    0

    arm / levels_passed         s1      s2      s3      s4      s5      s6   sNone    mean    n
    B_FAIL                       1       2       1       0       1       1       -   1.000    6
    B_FIZZLE                     3       0       1       0       1       1       -   1.000    6
    OLD_B                        2       2       0       0       3       2       -   1.500    6
    OLD_v04                      0       2       0       1       2       1       -   1.000    6
    controls                     -       -       -       -       -       -       -       -    0

    arm / crossing_final        s1      s2      s3      s4      s5      s6   sNone    mean    n
    B_FAIL                   0.780   1.000   1.000   0.500   0.700   0.340       -   0.720    6
    B_FIZZLE                 1.000   0.800   1.000   1.000   1.000   0.560       -   0.893    6
    OLD_B                    1.000   0.720   1.000   0.880   1.000   0.980       -   0.930    6
    OLD_v04                  1.000   1.000   1.000   1.000   1.000   1.000       -   1.000    6
    controls                     -       -       -       -       -       -       -       -    0

- typed states fired: ['UNDERPOWERED']
    UNDERPOWERED  {"arms_below": {"controls": 1}, "n_min": 6}
- disposition candidate (machine): UNDERPOWERED -- fewer rows than the preregistered minimum
- claim ceiling (machine): none; preregistered ceiling: 24 cells per arm; a count; C5-10 replicates any selection on held-out worlds

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"reach-discovery-b": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C5-09

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: UNDERPOWERED (machine candidate UNDERPOWERED). 
