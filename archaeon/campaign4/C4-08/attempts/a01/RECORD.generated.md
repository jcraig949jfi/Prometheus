# C4-08 -- can robustness be constructed rather than given (re-premised)

## A. STARTUP (preregistration; sealed sha256:470b8bbe280127272d2e9251de3c8e2c478e6f419467ff55699a2496cfdcae91)

- experiment ID: C4-08
- parents: C4-05, C4-06, C4-01
- QUESTION: Under selection with elevated mutation load (two frozen-weight edits per birth), do descendants change their own single-edit D-transition probabilities relative to their ancestors and to descendants under ordinary load, and is an evolved structural difference responsible? (The 'free insulation removed' arm is REPRESENTATION_BLOCKED, D4-007.)
- PARENT EVIDENCE: C4-01: single-edit loss .29-.64 per operator; C4-02: radius-2 loss .66; C4-05: 188 depth-16 walkers; C4-06: mutation_only runs (traces committed).
- WHY THIS SLOT IS STILL WORTH SPENDING: The directive's construction-vs-given question, on the part of it this substrate can pose.
- ASSAY CAPABILITY REQUIREMENT: ancestral loss under the fresh assay within .10 of C4-01's shelf rates; the ordinary reruns' traces equal C4-06's committed traces (negative control); determinism; cheat
- POSITIVE CONTROL: ordinary arm: trace_equal_c406 >= 1.0 on every seed
- REACHABILITY ESTIMATE:
    {"note": "descendant sampling; no reachability claim"}
- ARMS:
    - ancestral
    - ordinary
    - perturbed
    - insulation_removed
- COMMON-RANDOM-NUMBERS POLICY: same cell seeds and init_pop as C4-06; the perturbed arm differs only in n_ops=2 per birth; assay edits seeded by (campaign_seed, program digest, operator, draw)
- BUDGET:
    {"E": 16, "G": 100, "N": 200, "draws": 4, "seeds": [1, 2, 3, 4, 5, 6], "top": 32, "walkers": 188}
- PRIMARY OBSERVABLE: per population: single-edit loss / neutral / coherent / improved shares with Wilson bands, mean length, category shares; P1 perturbed loss < ancestral by >= .10; P2 ordinary loss NOT < ancestral by >= .10; suspected categories (share diff >= .10); ablation loss delta on perturbed elites
- CLAIM CEILING: a population comparison under one perturbation regime on one substrate; the ablation is prospective but static (NOP-out), not mechanistic
- FALSIFICATION CONDITION: P1 lost -> NEGATIVE
- KILL CONDITION: control failure -> INSTRUMENT_INVALID
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_INVALID
    - REPRESENTATION_BLOCKED (insulation_removed arm)
    - NOT_EXAMINED (ablation, when no category differs)
- EXPECTED MACHINE TELEMETRY:
    - traces
    - assay rows per program
    - population tables
    - ablation table
- MACHINE CHANGES EXERCISED:
    - descend n_ops=2
    - NOP-out ablation
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (queue slot 8)
- decl (machine-read by archaeon.wse.states): {"n_min": 1, "positive_control": {"arm": "ordinary", "metric": "trace_equal_c406", "min": 1.0, "min_rows": 6}, "primary": {"control": "ancestral", "metric": "loss_p", "min_effect": -0.1, "treatment": "perturbed"}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a01); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 4; errors 0
- timings (s): assay_s=189.47, evolve_s=230.0, startup_s=0.04, teardown_s=0.03, total_s=439.4
- decisions: D4-012: perturbation regime = descend(n_ops=2, mate=None) per birth; descendant sample = top-32 of each final population; the ordinary arm is RERUN (C4-06 saved traces, not manifests) and its traces are the negative control; suspected structures chosen only after the assay
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / loss_p                s1      s2      s3      s4      s5      s6   sNone    mean    n
    ancestral                    -       -       -       -       -       -   0.419   0.419    1
    insulation_removed           -       -       -       -       -       -       -       -    0
    ordinary                     -       -       -       -       -       -   0.185   0.185    1
    perturbed                    -       -       -       -       -       -   0.125   0.125    1

    arm / neutral_p             s1      s2      s3      s4      s5      s6   sNone    mean    n
    ancestral                    -       -       -       -       -       -   0.538   0.538    1
    insulation_removed           -       -       -       -       -       -       -       -    0
    ordinary                     -       -       -       -       -       -   0.789   0.789    1
    perturbed                    -       -       -       -       -       -   0.863   0.863    1

    arm / coherent_p            s1      s2      s3      s4      s5      s6   sNone    mean    n
    ancestral                    -       -       -       -       -       -   0.149   0.149    1
    insulation_removed           -       -       -       -       -       -       -       -    0
    ordinary                     -       -       -       -       -       -   0.077   0.077    1
    perturbed                    -       -       -       -       -       -   0.044   0.044    1

    arm / mean_len              s1      s2      s3      s4      s5      s6   sNone    mean    n
    ancestral                    -       -       -       -       -       -  19.133  19.133    1
    insulation_removed           -       -       -       -       -       -       -       -    0
    ordinary                     -       -       -       -       -       -  40.057  40.057    1
    perturbed                    -       -       -       -       -       -  62.458  62.458    1

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.4187, "effect": -0.2941, "min_effect": -0.1, "n_control": 1, "n_treatment": 1, "paired": 1, "paired_wins": 0, "treatment_mean": 0.1246}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: a population comparison under one perturbation regime on one substrate; the ablation is prospective but static (NOP-out), not mechanistic

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"robust": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C4-08

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). 
