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
    arm / site_drop_share_of_margin      s1      s2      s3      s4      s5      s6      s7      s8    mean    n
    GKL                      0.448   1.192   1.040   1.394       -       -   0.808       -   0.976    5
    particle1                1.069   0.957   0.872   0.918   0.814       -   1.038   1.065   0.962    7
    particle2                1.677   1.169   0.563   0.756   0.965   0.922   0.729   0.947   0.966    8

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

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.9764, "effect": -0.0105, "min_effect": 0.1, "n_control": 5, "n_treatment": 8, "paired": 5, "paired_wins": 1, "treatment_mean": 0.966}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: an executable hypothesis for particle2 at d=2 on this catalogue; n=8 seeds

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

The campaign asked for one evolved computational effect reduced to a falsifiable local mechanism. The reduction was performed and it dissolved the effect. Primary: the share of the margin carried by a single site is 0.966 for particle2 and 0.976 for GKL (effect -0.011 against a declared 0.1), so the localization campaign 2 reported (k50 = 1 in 11 of 12 rows) is reproduced exactly and is NOT distinctive -- a hand-designed rule that was never selected for delayed recall is just as localized. Mechanism classes: local storage fires in 0 of 8 seeds, routing in 2 of 8, against a declared threshold of 3 in 4, so the preregistered falsification fires and the mechanism is neither of the named classes. The decisive numbers are the one-step-earlier clamps: 0.000-0.034 (the site itself at t*-1) and 0.000-0.086 (its whole radius-3 neighbourhood at t*-1), against full single-site drops of 0.45-1.68 of the margin. Nothing measurable arrives at that site one step before it matters. Coincidence: the site-alone readout survives permuting the reset lattice in 5 of 8 particle2 seeds (0.53-0.57 permuted against 0.49-0.63 true), below the declared 3-in-4 threshold for killing the computation reading outright but a majority, and the same probe fires in 3 of 5 GKL seeds. Read together: the frozen readout is reading position-keyed reset structure at a single site, and campaign 2's 0.54-0.61 against a 0.50 baseline is consistent with that without any delayed-recall computation. This closes the CA line the way the directive asked -- with an executable hypothesis that a later run can falsify, namely that particle2's margin at d=2 requires no information transport and can be reproduced by a position-keyed reset readout alone. Must NOT be claimed: that particle2 computes nothing anywhere (this tests one task, one delay, one frozen readout, one lattice size); that the coincidence probe settles it (5 of 8 is a majority, not the declared 3 in 4); that GKL and particle2 are the same mechanism (only their LOCALIZATION and their failure to fit the named classes match).

## D. TEARDOWN (generated)

- worlds: {"ca": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C3-SFE-09

Four attempts (a01/a02 dry, a03 engine crashed, a04 of record, resumed from a03 and replaying its 29 verified steps). Two harness defects were found and fixed by this slot. (1) ClampedCA.step combined the clamp sets with an operator-precedence error that produced None on any step with no clamp at that time; found in the first dry run, fixed before any engine attempt. (2) a03 crashed inside the SHARED disposition code: rows whose margin is below the interrogation floor return early WITHOUT the primary metric, and the paired-comparison built its per-seed maps by indexing the metric directly, raising KeyError. With 4 seeds every row was informative so the dry runs never saw it; with 8 seeds three GKL rows were uninformative. Fixed in archaeon/wse/states.py: rows that do not carry the metric are skipped, never read as zero -- reading a missing measurement as zero would have inflated the treatment contrast (L3-038). 39 s for 24 genome x seed jobs; 24 records, 0 errors on the attempt of record. The run used 8 seeds rather than the parent's 4 because the probe is cheap and UNDERPOWERED is a declared failure mode.

## F. LANDSCAPE / GRADIENT NOTES

The delayed-recall margin is localized, and localization turns out to be uninformative. In particle2 one site carries 56-168% of the whole margin (site 3 in 7 of 8 seeds, site 9 in the eighth), and the minimum causal lesion is 1-5 clamped (site, time) pairs, usually 2-3. But the same is true of GKL, which was never evolved for this task: its single site carries 45-139% of its margin. Localization is a property of this readout-plus-substrate arrangement, not a signature of an evolved mechanism. The storage-versus-routing dissection comes back empty on both candidates. Clamping the responsible site one step BEFORE its critical phase removes 0.000-0.034 of the margin, and clamping its entire radius-3 neighbourhood one step before removes 0.000-0.086, against full single-site drops an order of magnitude larger. Whatever the site contributes, it does not arrive there one step earlier from itself or from its neighbours, which rules out both preregistered classes. The coincidence probe explains why. Reading the target from the responsible site ALONE gives 0.486-0.629 accuracy; reading it from the same site alone with the reset lattice PERMUTED across streams gives 0.530-0.573. In 5 of 8 particle2 seeds the permuted reading is as good as the true one. The site's apparent delayed-recall signal is largely position-keyed reset structure that the readout can exploit without any information flowing through the dynamics. Refitting the readout after lesioning the site recovers 13-74% of the margin, so the arrangement is partly redundant as well.

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). Assay capable: particle2's frozen-readout margin cleared the 0.02 interrogation floor in 8 of 8 seeds and the single-site lesion reproduced campaign 2's localization (site drop 0.56-1.68 of the margin). The preregistered primary -- particle2 minus GKL on the share of the margin carried by one site, minimum effect 0.1 -- is 0.966 vs 0.976, effect -0.011. The evolved particle rule is no more localized than the hand-designed GKL rule. The preregistered falsification also fires: neither named mechanism class holds in 3 of 4 seeds (local storage 0/8, routing 2/8), so the mechanism is not one of the two classes the slot was built to distinguish, and that is reported rather than relabelled.
