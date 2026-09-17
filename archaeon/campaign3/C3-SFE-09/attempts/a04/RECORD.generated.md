# C3-SFE-09 -- CA mechanism, not usefulness

## A. STARTUP (preregistration; sealed sha256:ff205e03facd9d6a8569a2b59e217104a1a63cbed5c53a10fa94e4be6bd8b7e5)

- experiment ID: C3-SFE-09
- parents: C2-SFE-09, SFE-04
- QUESTION: Which site and time step of particle2 carry its delayed-recall (d=2) margin, and does that site STORE the delayed bit (clamping it one step earlier removes the margin) or EXPOSE information computed by its radius-3 predecessors (clamping them one step earlier removes it)? Same probes on particle1 and GKL.
- PARENT EVIDENCE: C2-SFE-09 (n=4): particle2 0.54-0.61 vs random 0.50; not a reset artifact (reset-only < chance), not a dynamical bias (time shuffle removes it), input-dependent; LOCALIZED with k50 = 1 in 11/12 rows.
- WHY THIS SLOT IS STILL WORTH SPENDING: Usefulness has been measured twice; the campaign asks for one evolved computational effect reduced to a falsifiable local mechanism, and the single-site localization makes this the cheapest such reduction available.
- ASSAY CAPABILITY REQUIREMENT: the frozen readout's margin on the confirmation set >= 0.02 for particle2 in >= 3 of 8 seeds (rows below are marked uninformative)
- POSITIVE CONTROL: the full single-site lesion drop reproduces campaign 2's localization (site_drop >= 0.5 x margin)
- REACHABILITY ESTIMATE:
    {"note": "not a WSE cell; the reachability table does not apply"}
- ARMS:
    - particle2
    - particle1
    - GKL
- COMMON-RANDOM-NUMBERS POLICY: per seed one partition and reset root shared by every genome; permutation for the coincidence probe drawn once per seed
- BUDGET:
    {"delay": 2, "horizon": 8, "min_lesion_max": 6, "n_cells": 31, "reset_density": 0.5, "seeds": [1, 2, 3, 4, 5, 6, 7, 8]}
- PRIMARY OBSERVABLE: per genome x seed: site s*, phase t*, self_tm1_drop vs neighbour_set_tm1_drop (storage vs routing), site-alone readout with and without reset permutation (coincidence), minimum causal lesion, recovery after refit; primary: particle2 - GKL on site_drop_share_of_margin (are the two mechanisms equally localized?)
- CLAIM CEILING: an executable hypothesis for particle2 at d=2 on this catalogue; n=8 seeds
- FALSIFICATION CONDITION: if neither flag_local_storage nor flag_routed holds in >= 3/4 seeds for particle2, the mechanism is not one of the two named classes (reported as such); flag_coincidence in >= 3/4 seeds kills the 'computation' reading
- KILL CONDITION: margin < 0.02 in > 1 seed for particle2 (assay uninformative)
- TYPED FAILURE CONDITIONS:
    - UNDERPOWERED
    - INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - single-site drops
    - phase drops
    - neighbour drops
    - minimum lesion sets
    - site-alone readouts
    - recovery after refit
- MACHINE CHANGES EXERCISED:
    - H (probes)
    - I
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (queue slot 9)
- decl (machine-read by archaeon.wse.states): {"n_min": 8, "primary": {"control": "GKL", "metric": "site_drop_share_of_margin", "min_effect": 0.1, "treatment": "particle2"}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a04); resumed_from: 3; replayed steps on the attempt of record: 29
    a02  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=WEAK_POSITIVE
    a04  errors=0 replayed=29 engine=True purpose=engine disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 1; artifacts 1; imports 0; records 24; errors 0
- timings (s): mechanism_s=38.47, records_s=0.01, startup_s=0.0, teardown_s=0.2, total_s=38.9
- decisions: D3-012: storage vs routing decided by clamps ONE STEP BEFORE the critical phase (self at t*-1 vs radius-3 neighbours at t*-1), each against the full single-site drop; coincidence by the site-alone readout under a permuted reset lattice
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / base_acc              s1      s2      s3      s4      s5      s6      s7      s8    mean    n
    GKL                      0.538   0.534   0.533   0.543   0.516   0.503   0.534   0.497   0.525    8
    particle1                0.576   0.560   0.561   0.579   0.591   0.510   0.568   0.560   0.563    8
    particle2                0.540   0.600   0.592   0.612   0.574   0.566   0.591   0.599   0.584    8

    arm / site                  s1      s2      s3      s4      s5      s6      s7      s8    mean    n
    GKL                         28      28      30       2       -       -      27       -  23.000    5
    particle1                    6       6       3       9       3       -       3       9   5.571    7
    particle2                    3       3       3       3       3       9       3       3   3.750    8

    arm / t_star                s1      s2      s3      s4      s5      s6      s7      s8    mean    n
    GKL                          0       1       4       1       -       -       4       -   2.000    5
    particle1                    1       3       1       1       1       -       1       2   1.429    7
    particle2                    3       0       0       2       0       5       1       3   1.750    8

    arm / self_tm1_drop         s1      s2      s3      s4      s5      s6      s7      s8    mean    n
    GKL                      0.000   0.000   0.012   0.013       -       -  -0.006       -   0.004    5
    particle1                0.013   0.010   0.022   0.018   0.025       -   0.016   0.021   0.018    7
    particle2                0.022   0.000   0.000   0.034   0.000   0.013   0.018   0.025   0.014    8

    arm / neighbour_set_tm1_drop      s1      s2      s3      s4      s5      s6      s7      s8    mean    n
    GKL                      0.000  -0.003   0.013   0.023       -       -   0.023       -   0.011    5
    particle1                0.031   0.046   0.069   0.059   0.083       -   0.068   0.027   0.055    7
    particle2                0.044   0.000   0.000   0.086   0.000   0.027   0.069   0.039   0.033    8

    arm / alone_acc             s1      s2      s3      s4      s5      s6      s7      s8    mean    n
    GKL                      0.548   0.529   0.547   0.505       -       -   0.495       -   0.525    5
    particle1                0.490   0.516   0.596   0.577   0.557       -   0.561   0.573   0.553    7
    particle2                0.530   0.566   0.486   0.536   0.560   0.629   0.574   0.590   0.559    8

    arm / alone_permuted_reset_acc      s1      s2      s3      s4      s5      s6      s7      s8    mean    n
    GKL                      0.553   0.581   0.534   0.505       -       -   0.519       -   0.539    5
    particle1                0.490   0.521   0.568   0.581   0.551       -   0.564   0.544   0.545    7
    particle2                0.530   0.561   0.551   0.538   0.548   0.573   0.568   0.560   0.554    8

    arm / recovery_share        s1      s2      s3      s4      s5      s6      s7      s8    mean    n
    GKL                      0.793   0.385   0.480   0.182       -       -   0.269       -   0.422    5
    particle1                0.310   0.413   0.021   0.000   0.114       -   0.269  -0.022   0.158    7
    particle2                0.194   0.130   0.211   0.500   0.298   0.176   0.743   0.355   0.326    8

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.9764, "effect": -0.0105, "min_effect": 0.1, "n_control": 5, "n_treatment": 8, "paired": 5, "paired_wins": 1, "treatment_mean": 0.966}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: an executable hypothesis for particle2 at d=2 on this catalogue; n=8 seeds

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"ca": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C3-SFE-09

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). 
