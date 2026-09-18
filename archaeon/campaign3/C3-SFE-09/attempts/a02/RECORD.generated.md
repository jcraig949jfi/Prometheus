# C3-SFE-09 -- CA mechanism, not usefulness

## A. STARTUP (preregistration; sealed sha256:c7813b4dbb24e7f3c7f16640b4e99db8ab272047cc6203fd6c2dc0af5a08847a)

- experiment ID: C3-SFE-09
- parents: C2-SFE-09, SFE-04
- QUESTION: Which site and time step of particle2 carry its delayed-recall (d=2) margin, and does that site STORE the delayed bit (clamping it one step earlier removes the margin) or EXPOSE information computed by its radius-3 predecessors (clamping them one step earlier removes it)? Same probes on particle1 and GKL.
- PARENT EVIDENCE: C2-SFE-09 (n=4): particle2 0.54-0.61 vs random 0.50; not a reset artifact (reset-only < chance), not a dynamical bias (time shuffle removes it), input-dependent; LOCALIZED with k50 = 1 in 11/12 rows.
- WHY THIS SLOT IS STILL WORTH SPENDING: Usefulness has been measured twice; the campaign asks for one evolved computational effect reduced to a falsifiable local mechanism, and the single-site localization makes this the cheapest such reduction available.
- ASSAY CAPABILITY REQUIREMENT: the frozen readout's margin on the confirmation set >= 0.02 for particle2 in >= 3 of 1 seeds (rows below are marked uninformative)
- POSITIVE CONTROL: the full single-site lesion drop reproduces campaign 2's localization (site_drop >= 0.5 x margin)
- REACHABILITY ESTIMATE:
    {"note": "not a WSE cell; the reachability table does not apply"}
- ARMS:
    - particle2
    - particle1
    - GKL
- COMMON-RANDOM-NUMBERS POLICY: per seed one partition and reset root shared by every genome; permutation for the coincidence probe drawn once per seed
- BUDGET:
    {"delay": 2, "horizon": 8, "min_lesion_max": 6, "n_cells": 31, "reset_density": 0.5, "seeds": [1]}
- PRIMARY OBSERVABLE: per genome x seed: site s*, phase t*, self_tm1_drop vs neighbour_set_tm1_drop (storage vs routing), site-alone readout with and without reset permutation (coincidence), minimum causal lesion, recovery after refit; primary: particle2 - GKL on site_drop_share_of_margin (are the two mechanisms equally localized?)
- CLAIM CEILING: an executable hypothesis for particle2 at d=2 on this catalogue; n=1 seeds
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
- decl (machine-read by archaeon.wse.states): {"n_min": 1, "primary": {"control": "GKL", "metric": "site_drop_share_of_margin", "min_effect": 0.1, "treatment": "particle2"}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a00); resumed_from: 1; replayed steps on the attempt of record: 0
    a02  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=WEAK_POSITIVE
- engine: dry-run; worlds 0; artifacts 0; imports 0; records 0; errors 0
- timings (s): mechanism_s=24.09, records_s=0.0, total_s=24.5
- decisions: D3-012: storage vs routing decided by clamps ONE STEP BEFORE the critical phase (self at t*-1 vs radius-3 neighbours at t*-1), each against the full single-site drop; coincidence by the site-alone readout under a permuted reset lattice
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / base_acc              s1    mean    n
    GKL                      0.538   0.538    1
    particle1                0.576   0.576    1
    particle2                0.540   0.540    1

    arm / site                  s1    mean    n
    GKL                         28  28.000    1
    particle1                    6   6.000    1
    particle2                    3   3.000    1

    arm / t_star                s1    mean    n
    GKL                          0   0.000    1
    particle1                    1   1.000    1
    particle2                    3   3.000    1

    arm / self_tm1_drop         s1    mean    n
    GKL                      0.000   0.000    1
    particle1                0.013   0.013    1
    particle2                0.022   0.022    1

    arm / neighbour_set_tm1_drop      s1    mean    n
    GKL                      0.000   0.000    1
    particle1                0.031   0.031    1
    particle2                0.044   0.044    1

    arm / alone_acc             s1    mean    n
    GKL                      0.548   0.548    1
    particle1                0.490   0.490    1
    particle2                0.530   0.530    1

    arm / alone_permuted_reset_acc      s1    mean    n
    GKL                      0.553   0.553    1
    particle1                0.490   0.490    1
    particle2                0.530   0.530    1

    arm / recovery_share        s1    mean    n
    GKL                      0.793   0.793    1
    particle1                0.310   0.310    1
    particle2                0.194   0.194    1

- typed states fired: none
- disposition candidate (machine): WEAK_POSITIVE -- effect >= min_effect but n < 10 or a declared falsification attack failed or was not run
    evidence: {"control_mean": 0.4483, "effect": 1.2291, "min_effect": 0.1, "n_control": 1, "n_treatment": 1, "paired": 1, "paired_wins": 1, "treatment_mean": 1.6774}
    battery: {"attacked": 0, "declared": 0, "survived": 0}
- claim ceiling (machine): weak; not for propagation; preregistered ceiling: an executable hypothesis for particle2 at d=2 on this catalogue; n=1 seeds

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: none (dry run)
- all TERMINATED: n/a

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C3-SFE-09

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: WEAK_POSITIVE (machine candidate WEAK_POSITIVE). 
