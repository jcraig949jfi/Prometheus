# Theophrastus round-2 specimens (2026-09-14)

Harvest gate: roles/Theophrastus/crucible/ROUND2_DISSECTION_PLAN_2026-09-14.md
s3, frozen before Step A. Evidence: roles/Theophrastus/crucible/round2/
(per_ic.jsonl 29,800 rows; per_ic_round2.jsonl; stepA_tests.json;
ADAPTIVE_RECORD_01/02.json; ROUND2_SCORE.json) and ledgers/rows.jsonl
(phase round2, 21 rows). Every number below is recomputable from those
files; the prose is not the evidence.

================================================================================
SPECIMEN THEO-SPEC-001  MARGIN_RESPONSE          disposition: MECHANISM_SPECIMEN
================================================================================
MECHANISM:
    For a radius-3 density-classification rule R on an odd ring of N
    cells, the success of one initial condition depends on the IC only
    through its realised one-count k (signed margin s = k/N - 1/2). An
    ensemble acts on accuracy only through its k-distribution:
        acc(R, N, ensemble) = sum_k P_ens(k) * c_{R,N}(k).
    c_{R,N} (the SIGNED-MARGIN RESPONSE CURVE) is a phenotype of (R, N).
INPUT CONDITIONS:
    ICs drawn iid Bernoulli(p) per cell (any p, any mixture of p); the
    executor ca_density_v0 / herakles.evca.core; odd N >= 7; the horizon
    long enough for convergence (see INVARIANCES).
TRANSFORMATION:
    (a) PRESSURE PRIMITIVE: a density ensemble is a margin distribution.
        Single-density cells P_d = ic_density_set [d] and mixtures are
        graded difficulty knobs, expressible today in the kind contract.
    (b) PHENOTYPE INSTRUMENT: from any fossil (repeat seeds + payload) the
        per-IC (k, success) table is re-derived offline and binned into
        c_{R,N}; theophrastus/dissect.py + curves.py (validated: 59/59
        rows re-derived bit-exactly; CHEAT-A perturbed seed fails).
EXPECTED EFFECT:
    Accuracy of any Bernoulli-mixture ensemble is predicted from c_{R,N}
    applied to the ensemble's realised margins. Where the curve bin holds
    >= ~100 ICs the prediction lands within 2 SE (7/7 cells: exp W599
    d=.60 1.000 vs 1.000; exp W149 d=.40/.60; par W599 d=.48/.52; GKL W599
    d=.48/.52). Where the bin holds < 50 ICs it misses by 2-3 SE in the
    predicted direction (3/3: maj W149 d=.20 .576 vs .529; maj W599 d=.20
    .130 vs .155; exp W599 d=.40 .348 vs .304).
NECESSARY CONDITIONS (experimentally supported):
    Ensemble invariance at fixed margin: P_iid vs P_unif success at equal
    m, 8/8 (rule, N) with no bin |z| >= 3 (chi2 ~ dof); the same on the
    held-out rule particle1, 2/2. (For Bernoulli generators this is also
    exact by exchangeability; the test is the instrument check.)
SUFFICIENT CONDITIONS:
    Constructing an ensemble with a chosen margin distribution reproduces
    the accuracy the curve predicts (Step B above), within the resolution
    envelope stated.
INVARIANCES (tested):
    Horizon: halving steps (1198 -> 599 at N=599) under P_unif gives
    BIT-IDENTICAL results for exp and par (digests equal); 320 vs 298 and
    1198 vs 1286 identical under P_iid (founding C-RES). Criterion at_T vs
    stable: identical (criteria_agree 67/67 rows). Reflection: exact.
    Collapse variable across worlds: relative margin m, NOT absolute count
    |2k-N| (by_m chi2 41-127 / 27 vs by_abs_count 208-614 / 28, all rules).
FAILURE BOUNDARY (tested):
    The curve is (R, N)-specific: at fixed m it moves with N in a rule-
    specific direction (GKL/par sharpen: z -3.9 at m=.01/.03; GKL keeps
    sharpening to N=999, z -2.8; exp saturates into one-class collapse by
    N=599, curve unchanged 599 -> 999, chi2 12.4/23; maj's success
    boundary moves outward, m* ~.27 at 149 -> >.30 at 599). A curve from
    one N does NOT predict another N quantitatively (GKL W999 P_iid .7925
    observed vs .7236 predicted from the 599 curve).
COUNTEREXAMPLES (preserved):
    The three under-resolved-bin misses above; GKL/exp W999 quantitative
    misses from the 599 curve (ROUND2_SCORE.json cells E).
TRANSPORT EVIDENCE:
    Rule held out from hypothesis formation: particle1 (EvEmComp only):
    invariance holds at W149 and W599 (chi2 2.1/4, 3.7/2). Across
    worlds: transports as a FORM (curve exists, collapses on m), not as
    values. To other kinds: UNTESTED (needs a scalar sufficient statistic
    of the input; eca_rule_eval_v1 has no classification task).
COMPOSITION AFFORDANCES:
    UNKNOWN. Composition of rules is not executable (THEO-REQ-003).
PROVENANCE:
    Founding rows (seeds 20260913/14, 16 coverage + stencils) and round-2
    rows theo:*:rou1..rou21; contrasts C-PRESS x8 (founding); Step A tests
    stepA_tests.json; Step B/C/D/E ADAPTIVE_RECORD_01 + ROUND2_SCORE.json;
    ADAPTIVE_RECORD_02.
CONFIDENCE:
    High for the decomposition (exact + instrument-verified) and for
    ensemble/horizon/criterion invariance (exact digests). Medium for
    constructive prediction (7/10 within 2 SE; envelope stated). The
    literature knew the direction (Mitchell, Crutchfield & Das 1996: GA
    fitness on uniform-density ICs vs performance on unbiased ICs); the
    per-IC curve, its invariances, its N-collapse variable and an
    executable instrument are new to Prometheus. DUPLICATE check: Nyx
    catalogue (no density/margin bit), Herakles C1-e (ensemble effect at
    N=149 only), Techne (none) -- not a duplicate.
COST:
    Zero new executions for the instrument (offline from fossils; ~2 min
    for 59 rows). A single-density cell at N=599 costs ~12 s executor +
    ~5 s engine round trip for 800 ICs.

================================================================================
SPECIMEN THEO-SPEC-002  ONE_CLASS_COLLAPSE (exp)   disposition: MECHANISM_BOUNDED
================================================================================
MECHANISM:
    The block-expanding rule `exp` (GA-evolved, hex 0505408305c9...) on
    rings N >= 599 answers "all ones" for essentially every IC with
    signed margin s > -0.10, regardless of the true majority: success is
    0.99-1.00 on majority-1 ICs at every m and 0.00-0.04 on majority-0
    ICs out to m ~ .05, 0.35 at m ~ .10 (Step B retry), recovering to
    ~.76 at m ~ .20 and 1.0 by m ~ .30. Its balanced-ensemble accuracy of
    .55 (599) / .53 (999) is the majority-1 half of the ensemble, not a
    noisy classifier: published "P_599 = .515, P_999 = .503" is a
    constant classifier's score.
INPUT CONDITIONS:
    exp's table; N >= 599 (at N=149 the asymmetry exists but is partial:
    .37 vs .67 at m=0); any density ensemble.
TRANSFORMATION:
    A failure-geometry detector: balanced accuracy near 1/2 AND signed-
    margin asymmetry |z| >= 10 AND one side at ~1.0 => one-class collapse.
    Distinguishes "degrades to chance" from "collapses to a constant".
EXPECTED EFFECT:
    Inverting the class side of a single-density ensemble swings accuracy
    from 1.00 (d=.60) to .35 (d=.40) at N=599 (predicted; observed 1.000
    and .3475). The curve is unchanged from 599 to 999 (saturated).
NECESSARY / SUFFICIENT CONDITIONS:
    UNKNOWN at the rule-table level: which entries of exp's table produce
    the collapse cannot be tested without a table-level ablation/
    substitution intervention (THEO-REQ-005). Horizon is NOT an
    ingredient (bit-identical at half the steps).
INVARIANCES: horizon; criterion; reflection (exact). FAILURE BOUNDARY:
    the zero-side boundary m_0(N): >= .10 at 599 (success .35), ~ .20
    (.76); at 149 the boundary is ~.04. Emergence between N=149 and 599;
    saturation by 999.
COUNTEREXAMPLES: par is asymmetric the OTHER way (d<1/2 favoured,
    z +10 at 599, m=0) and does not collapse (.72 balanced); particle1
    (same branch) is SYMMETRIC (max |z| 2.1): the asymmetry is rule-
    specific, and the claim "GA-evolved rules are complement-asymmetric"
    is TRANSPORT_FAILED and killed.
TRANSPORT EVIDENCE: none across rules (each rule has its own geometry);
    the DETECTOR transports (it is a function of any per-IC table).
PROVENANCE: stepA_tests.json H6 exp/N149, exp/N599; ROUND2_SCORE cells B
    exp W599 P_d60, W149 P_d40/P_d60, E exp W999 (H6_at_999 |z| 19.6);
    ADAPTIVE_RECORD_02.
CONFIDENCE: high for the geometry (z 20-30 on hundreds of ICs per bin,
    replicated across seeds and three worlds); UNKNOWN for cause.
COST: same as SPEC-001.

================================================================================
CANDIDATE THEO-CAND-003  MAJ_BOUNDARY_SHIFT        disposition: MECHANISM_CANDIDATE
================================================================================
Observation: maj (local majority) succeeds only beyond a margin threshold
m*(N) that moves OUTWARD with N (m*~.27 at 149: .42 success; ~.30 at 599:
.15; 1.0 by m~.39 at both). Consistent with "more cells = more chance of
a locally-majority minority block" (the opportunity-count form, in
RELATIVE terms). Constructive predictions at the boundary missed 2/2 by
2-3 SE (curve resolution). Not isolated; no intervention beyond N; kept as
a candidate with its counterexamples. Stop reason: expected discrimination
below binomial resolution without ~10x more ICs at m in [.25,.35].

================================================================================
REJECTED  "P_unif x W599 interaction"             disposition: ECOLOGICAL_CORRELATION_ONLY
================================================================================
The founding cluster of nine NEW_TO_RECORD contrasts is fully accounted
for by (H2) the nominal-p parameterisation delivering a narrower realised
margin distribution at larger N (arithmetic: sd sqrt(p(1-p)/N)) plus (H3)
the rule-specific N-response of c_{R,N} above. No separate mechanism
remains; the description is retired.
