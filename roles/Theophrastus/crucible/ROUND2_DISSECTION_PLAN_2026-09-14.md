# Round 2 -- dissection plan for the W599/P_unif carcass (PREREGISTERED)

Currency: 2026-09-14. Committed BEFORE any per-IC re-derivation and before
any new cell. Adaptive steps are appended as dated ADAPTIVE RECORDS at the
end (charter s6: evidence, explanations, question, candidates, selection
rule, chosen experiment, outcome meanings -- frozen before the result).

## 0. The carcass, stated as an observation (not a mechanism)

Founding rows (roles/Theophrastus/ledgers/rows.jsonl, seeds 20260913/14),
accuracy over 800 ICs per cell:

    rule   P_iid W149  P_unif W149   P_iid W599  P_unif W599
    maj      0.0000       0.320        0.0000       0.215
    GKL      0.8125       0.975        0.7550       0.994
    exp      0.6713       0.904        0.5500       0.828
    par      0.7500       0.965        0.7238       0.985

P_unif = ten Bernoulli(d) blocks, d in {.1,.2,.3,.4,.45,.55,.6,.7,.8,.9},
10 ICs each. P_iid = Bernoulli(1/2). Observation: P_unif lifts every rule;
the lift's world-dependence has a rule-specific sign (GKL, par: P_unif
rises with N while P_iid falls; exp, maj: both fall).

## 1. What machinery would have to exist? -- competing explanations

    H1  MARGIN_MEDIATION. Given rule and N, an IC's success depends on
        the IC only through its REALISED one-count k (equivalently its
        margin m = |k/N - 1/2|); an ensemble acts only through its
        k-distribution. Under this, "density diversity", "coverage",
        "avoiding unlucky ICs" and "occupancy" are the same explanation.
        NOTE: for Bernoulli(p) generators this is EXACT by exchangeability
        (conditional on k the configuration is uniform), so the empirical
        test is an INSTRUMENT check that the generator is what the code
        says, not a discovery; the mechanism content is in H2/H3/H6.
    H2  NOMINAL_PARAMETERISATION_ARTIFACT. The rule-specific WORLD
        dependence of the P_unif lift comes from the pressure being
        parameterised by NOMINAL p: the realised margin at nominal 0.45
        has sd sqrt(p(1-p)/N) = 0.041 (149) vs 0.020 (599), so the same
        label delivers a different margin distribution per world.
        Prediction: at FIXED realised m, acc_rule(m; 149) == acc_rule(m; 599)
        within binomial error, for every rule.
    H3  RULE-INTRINSIC FINITE-SIZE RESPONSE (opportunity count). At fixed
        realised m, success changes with N in a rule-specific way (a
        block-expanding rule meets more rogue minority blocks on a longer
        ring). Prediction: curves at fixed m shift with N; the shift may
        collapse under absolute count margin |2k-N| rather than m.
        H2 and H3 are discriminated by the same curve-collapse test and
        can both be partly true (per rule).
    H4  CONVERGENCE_HORIZON. Far-from-threshold ICs converge within the
        horizon, near ones do not; the lift is partly a horizon effect.
        Prediction: halving steps under P_unif changes accuracy. (C-RES
        already showed EXACT step-invariance under P_iid.)
    H5  CRITERION_GEOMETRY. at_T vs stable. ALREADY KILLED: criteria_agree
        true on 46/46 rows including every P_unif row.
    H6  BRANCH/RULE-SPECIFIC RESPONSE SHAPE. GA-evolved rules have a
        differently shaped or complement-ASYMMETRIC margin curve (success
        at density d != success at 1-d); hand-designed rules are symmetric.
        Prediction: signed-margin curves differ between d<1/2 and d>1/2
        for some rules and not others; the `complement` transform is an
        exact null for every rule (by construction) and cannot test this
        -- the SIGNED curve can.
    H7  NO_REUSABLE_MECHANISM. Even if H1 holds, nothing transportable
        remains: the curve of one (rule, N) predicts nothing about another
        ensemble, another N, or another rule.

## 2. Discrimination steps (smallest first)

STEP A -- OFFLINE PER-IC RE-DERIVATION, zero new cells.
    Regenerate every IC of every founding row from (repeat seed, density
    block j -> seed+j, n_ic, n_cells) with herakles.evca.core.make_ics;
    re-run classify offline; INSTRUMENT CHECK: recomputed accuracy and
    mask_digest must equal the fossil's on every row (a cheat with a
    perturbed seed must FAIL the match). Then per (rule, N, ensemble):
    the per-IC table (k, m, signed density, success).
    Tests: H1 (success rate at equal k across ensembles: chi-square /
    binomial z per k-bin, pooled), H2 vs H3 (curve at fixed m across N:
    z per m-bin; collapse under m vs under |2k-N|), H6 (signed asymmetry
    z per |m|-bin).
STEP B -- CONSTRUCTIVE (SUFFICIENCY) + BOUNDARY, new cells, adaptive.
    Single-density pressures P_d (ic_density_set=[d], n_ic=100) chosen
    where Step A's curves are unsampled or where H2/H3 diverge most.
    Out-of-sample prediction: the accuracy of each new cell is PREDICTED
    from the Step-A curve (binomial mixture over the realised k of the
    cell's own regenerated ICs) BEFORE the cell runs; prediction recorded
    in the adaptive record; pass = |observed - predicted| <= 2 SE_pred+obs.
STEP C -- HORIZON (H4): P_unif at halved steps (W149: 149; W599: 599),
    2 rules. Exact-or-not: same digests => killed.
STEP D -- TRANSPORT: a rule NOT used to form the hypotheses (particle1,
    RECOVERED_SPECIMEN, EvEmComp only) at P_iid and P_unif, W149 and
    W599: re-run Steps A-B tests on it blind (predictions frozen first).
STEP E -- SCALING WORLD: W999 (999, 1998) for GKL and exp under P_iid and
    P_unif, to decide the collapse variable (m vs |2k-N|) with 3 worlds.

Budget: 45 executions / 3600 s wall (ledgers/budget_round2.json), and
STOP rules: a step is skipped when an earlier step has already killed or
subsumed the explanation it targets, or when its expected discrimination
is below the binomial resolution at n=800.

## 3. Harvest gate (frozen before Step A)

Candidate object: MARGIN_RESPONSE -- (i) the ensemble-invariant
per-(rule, N) success curve acc(k) as an organism PHENOTYPE, (ii) the
margin-controlled IC ensemble as a graded PRESSURE primitive, (iii) the
N-scaling relation between worlds as the transport law.

    MECHANISM_SPECIMEN         A + B + D + a stated scaling verdict (H2/H3)
                               + counterexamples preserved
    MECHANISM_BOUNDED          A + B; D failed or not run
    MECHANISM_PARTIALLY_ISOLATED  A only (instrument check + invariance)
    PHENOMENON_ONLY            A instrument check passes but H1 invariance
                               fails (curve not ensemble-invariant)
    ECOLOGICAL_CORRELATION_ONLY  B predictions fail on > 4 of the Step-B
                               cells (curve not constructive)
    INSTRUMENT_BLOCKED         the offline re-derivation cannot match the
                               fossils
    DUPLICATE_OR_EQUIVALENT    an equivalent specimen already exists in
                               Prometheus (Nyx catalogue / Herakles /
                               Techne checked and cited)
Prior evidence, stated now: the literature (Mitchell, Crutchfield & Das
1996; Das et al. 1995) KNOWS that density-classification performance
depends on distance from rho=1/2 and that GA fitness used a uniform-over-
density ensemble while reported performance used the unbiased one.
Herakles C1-e s3 measured the ensemble effect at N=149. Neither holds a
per-IC curve, a scaling verdict, or a transportable pressure object in
Prometheus. Nyx catalogue and Techne are checked in Step 0 of execution.

## 4. Controls for this round

    CHEAT-A   perturbed seed in the re-derivation must break the mask match
    CHEAT-B   a Step-B prediction made from the WRONG rule's curve must
              miss (positive control that predictions can fail)
    NULL      Step C horizon halving predicted exact identity
    C1-C10 of the founding round remain in force for every new cell.
