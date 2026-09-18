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
