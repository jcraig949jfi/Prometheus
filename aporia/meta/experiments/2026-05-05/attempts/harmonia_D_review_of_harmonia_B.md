# Review — Harmonia B (Dynamical Systems Batch)

**Reviewer:** Harmonia D
**Date:** 2026-05-05
**Scope:** Critique of B's 5 attempt files plus summary, with per-problem
recommendations for round-two, additional solution angles, and
datasets/tools that would extend the work.

**Files reviewed:**
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_B_01_furstenberg_x2x3.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_B_02_sarnak_mobius.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_B_03_palis.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_B_04_painleve_n_body.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_B_05_kam_stability.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\harmonia_B_summary.md`
- `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\_scratch_B\` (5 Python scripts + 5 JSON result files)

---

## Overall judgment

**Quality tier:** B / B+ for substrate-grade kill data. The batch is honest, calibrated-negative-rich, and includes real numerical experiments (verified by reading two of the five scripts). The summary's "two-class obstruction taxonomy" (A: missing rigidity functional in zero-entropy regime; B: missing sharp finite-dimensional bound) is a genuinely substrate-grade observation worth promoting beyond this batch.

**Strongest deliverables:** Sarnak finite-N indistinguishability (Problem 2 Attack 4) and Hénon-Heiles E* ≈ 0.12 reproduction (Problem 5 Attack 1). Both are real numerical observations with clean substrate implications.

**Weakest deliverables:** Painlevé (Problem 4) — naive symmetric attacks were structurally wrong by B's own admission; the calibration anchor (Xia n=5 reproduction) was sketched but not executed, leaving the n=4 attempts blind. Furstenberg (Problem 1) — the float-precision collapse was discovered post-hoc, not anticipated; no exact-arithmetic substitute was attempted in-session.

---

## Cross-cutting critique (issues spanning all 5 problems)

### C1 — Compressed time budget across the board

B ran ~1.5h per problem instead of the requested 3h, a 50% compression. The pattern is uniform: every attempt has 2-3 executed attacks plus 2-3 "Attack N (sketched, NOT executed)" entries. The honest acknowledgement is correct, but a round-two could literally execute the sketched attacks for substantial gain — they are mostly well-scoped. Estimated round-two effort to execute all sketched attacks: ~12-15 hours of focused compute and writing.

### C2 — Citation discipline: paraphrase-heavy without verification

Across all 5 files there are ~50 citations with [paraphrase] confidence flags. Honest, but B explicitly had WebSearch + WebFetch in the toolset and did not use them to verify even one citation. The Fleischer 2024 Painlevé claim is flagged as "low-confidence recollection" — that is exactly the kind of claim that needed an arXiv check before shipping. A round-two should run a verification pass on every [paraphrase]-tagged reference; ~30 min per problem with arXiv API.

### C3 — Numerical precision: standard float64 throughout

B used DOP853 with `rtol=1e-11` for ODE work and standard numpy float64 for discrete dynamics. Three of the five problems have substantive precision requirements that exceed double precision:

- **Furstenberg:** discrete dynamics on `R/Z` under `T_2`, `T_3` lose ~1 mantissa bit per step. After ~53 steps, all information is gone. B documented this as "Attack 1 failed" — but the right response is to use `fractions.Fraction` or `mpmath` for exact arithmetic, which B sketched as a follow-up but did not implement.
- **Painlevé:** near-singular n-body trajectories require ≥30-50 decimal digits during close encounters. `rtol=1e-11` integration cannot resolve the binary-tightening dynamics that drive Xia/Gerver constructions.
- **KAM Fourier-Newton:** computing radius of convergence of KAM perturbation series at high orders requires high-precision Fourier coefficients; standard double cuts off at ~order 50 truncation.

A round-two should default to `mpmath` for problems 1 and 4, and pick interval arithmetic (CAPD-Python bindings or Sage/CAPD) for problem 4 specifically.

### C4 — Calibration before novelty (Pattern-30-style discipline gap)

The Painlevé attempt jumped to n=4 candidates without first reproducing the n=5 Xia construction (the only known proven case). This is the "novelty before calibration" failure mode — exactly what `feedback_falsification_first.md` and the Prometheus "calibration before novelty" mantras warn against. Concretely: if the integrator cannot reproduce a known-true non-collision singularity in n=5, then a negative result on n=4 candidates is uninformative (the integrator might just be too imprecise). Round-two should ALWAYS calibrate against the proven case first.

### C5 — Statistical testing was informal

The chaos-score distinction (Hénon-Heiles), the visited-fraction analysis (Furstenberg Z/q), and the partial-sum decay rates (Sarnak) were all reported as raw numbers without formal hypothesis testing. A round-two should add chi-squared, Kolmogorov-Smirnov, or bootstrap CIs where applicable. Cost: ~10 min per problem with `scipy.stats`.

### C6 — No use of the existing Prometheus methodology toolkit

`D:\Prometheus\harmonia\memory\methodology_toolkit.md` lists 9 cross-disciplinary scorers (KOLMOGOROV_HAT, CRITICAL_EXPONENT, CHANNEL_CAPACITY, MDL_SCORER, RG_FLOW, FREE_ENERGY, GINI_COEFFICIENT, CONTROLLABILITY_RANK, TT_APPROX_MAP). At minimum:
- KOLMOGOROV_HAT (algorithmic-complexity proxy) on Sarnak Möbius outputs would give an information-theoretic lens on the "indistinguishability at finite N" finding.
- MDL_SCORER on the Hénon-Heiles section data could give a per-orbit chaos certificate sharper than std-of-section-points.
- CHANNEL_CAPACITY between (T_2-action-induced sequence) and (T_3-action-induced sequence) on the same orbit could be a quantitative Furstenberg-rigidity probe.

None of these were attempted. Round-two should explicitly draw from the toolkit shelf.

### C7 — No connection to other batches' work

The Logic / Foundations batch (Harmonia D, this reviewer's prior work) had Painlevé-adjacent independence-flavored discussion of cardinal arithmetic. The Combinatorics batch (Harmonia A, sister) has likely produced extremal-set-theory work that could inform Sarnak (multiplicative-function combinatorics) or Furstenberg (rigidity through pcf-style products). The cross-batch synthesis is Aporia's job per the BATCH_PLAN, but B's summary could have flagged candidate connections — none did.

### C8 — One factual issue worth flagging

In Problem 1's Attack 1, B's writeup claims "the chain absorbed at 0" with KL divergence ~6.9 — but reading `furstenberg_x2x3.py` more carefully, the script does not actually verify the all-mass-near-0 claim by checking which bin holds the mass; it only reports `kl_to_uniform`, `max_bin_density`, `min_bin_density`. The float-underflow story is plausible (and well-known for dyadic dynamics in double precision) but the in-script verification of "absorbed at fixed point 0" is not present. B should either re-instrument the script to log which bin captures the mass or weaken the claim. This is a minor verification gap, not a fabrication — but exactly the kind of thing the falsification-first discipline catches.

---

## Per-problem recommendations

### Problem 1 — Furstenberg ×2 ×3

**B's verdict: NO_PROGRESS_DOCUMENTED_OBSTACLES. Reviewer concur.**

#### Critique

The substantive observations (Z/q joint-orbit fraction = subgroup index for q=23, q=47) are clean and match elementary number theory. Probe B (topological-rigidity calibration) was a sound sanity check that succeeded. Probe A (the float-collapse discovery) is real but underverified in-script as noted in C8. Probe D and Probe E were sketched, not run.

#### Round 2 — yes, with significant return possible

Estimated effort: ~6-10 hours.

**Round 2 Attack 1 — exact-arithmetic random-product orbit on T**

Use Python's `fractions.Fraction` with starting point `Fraction(p, q)` for various non-dyadic, non-ternary `p/q`. Run for `10^6` steps. Now the orbit lives in a finite cyclic group `(Z/q')^×` for `q' = q · 2^a · 3^b` for some `a, b` depending on operations applied. This is essentially the profinite analogue. Histogram over the cyclic group; check rigidity directly. Compute uses bignums but is feasible.

**Round 2 Attack 2 — profinite computation on `Z_p` for p=5,7,11**

The natural setting for the conjecture's "limit of Z/q^n" interpretation. Implement multiplication-by-2 and multiplication-by-3 on `Z_p` via mpmath p-adic arithmetic (or roll a minimal one). Iterate orbits and compute joint-invariant measures.

**Round 2 Attack 3 — Hochman entropy-of-projections actual computation**

Implement Hochman's 2014 entropy-dimension formula for self-similar measures on `[0,1]`. Compute for a specific candidate measure (e.g., a Cantor-like measure with low Hausdorff dimension). Verify Hochman's theorem (positive entropy gap implies absolute continuity if the measure is `T_2`-invariant) on the candidate.

**Round 2 Attack 4 — Bourgain's spectral gap explicit estimate**

Bourgain has explicit `L^2` decay bounds for `T_2 + T_3` averaging operators on `T`. Compute the spectral gap numerically via discretization of the operator on a 2^14-point grid. The gap (if positive) gives a quantitative rigidity statement.

**Round 2 Attack 5 — joinings approach**

Furstenberg's joinings theory: the joint distribution of `T_2^n x` and `T_3^m x` for typical `(n, m)` should equidistribute on `T × T` if Furstenberg's conjecture holds. Compute the joint distribution at moderate `(n, m)` and check.

#### Additional solution angles to leverage

- **Higher-rank diagonalizable actions on homogeneous spaces** (Einsiedler-Katok-Lindenstrauss). The technique that closed the Littlewood-conjecture-up-to-Hausdorff-dimension lifts conceptually to Furstenberg through joining rigidity. Worth surveying their actual proof for transferable structure.
- **Sumset additive combinatorics** (Bourgain-Lindenstrauss-Michel-Venkatesh approach). Sieve methods on `T` connecting equidistribution to multiplicative independence. B mentioned this; not actually examined.
- **Quantum-unique-ergodicity analogy** (Lindenstrauss 2006 Annals). The QUE resolution used measure rigidity in a different setting; the proof technique might transfer.
- **Connection to Furstenberg's joining theorem for `Z`-actions**: any minimal `T_2` × `T_3`-joining of `(T, Lebesgue)` with itself should be the off-diagonal product, by joining rigidity. Computing partial joinings numerically would test this.

#### Datasets / compute tools

- **Exact-arithmetic dynamics library** (~200 LOC Python wrapping `fractions.Fraction` for `R/Z` dynamics; reusable across many problems).
- **p-adic computation library** for profinite-Z_p dynamics. Some support in `sympy.ntheory`; needs extension.
- **Hochman-style self-similar-measure entropy computation engine** (~500 LOC; substantive build).
- **Multi-base-normality test suite**: for transcendental constants (π, e, sqrt(2), Champernowne), compute base-2 and base-3 frequency vectors at high precision and check joint normality. Connects directly to the Attack 4 obstruction in B's writeup.

---

### Problem 2 — Sarnak Möbius Disjointness

**B's verdict: PARTIAL_RESULT. Reviewer concur — strongest of the 5.**

#### Critique

Best-executed problem in the batch. Real Möbius sieve (verified — density 0.6079 matches 6/π² to 4 decimals, sanity check passes), real partial-sum computation across 4 systems plus a positive-entropy null. The "indistinguishability at N=10^6" observation is genuinely substrate-grade and forecloses a class of naive falsification batteries.

Limits: N=10^6 is modest by modern Möbius standards (Matomäki-Radziwiłł routinely use N=10^9; Tao's logarithmic Chowla work uses N=10^{10+}). The "indistinguishability" claim might dissolve at N=10^9 if cleaner separation emerges — would be substrate-grade *progress* either way. The IET candidate (BSZ criterion check on a non-nilpotent zero-entropy system) was sketched but not run.

#### Round 2 — yes, high-priority

Estimated effort: ~10-15 hours.

**Round 2 Attack 1 — extend N to 10^9 or 10^{10}**

Möbius sieve at N=10^9 takes ~10 GB RAM and ~30 min Python (or ~5 min C). Would settle the indistinguishability question at the right asymptotic scale. Pre-computed Möbius tables exist (Project Mobius / OEIS A008683 chunks); could be downloaded rather than recomputed.

**Round 2 Attack 2 — IET BSZ-criterion check (B's sketched Attack 5)**

Implement a 3-IET (3-interval exchange transformation) simulator. For multiplicatively independent primes p, q ≤ 30, compute the BSZ correlation `(1/N) Σ_{n≤N} f(T^{pn}x) f̄(T^{qn}x)` for a continuous test function f. If the correlation goes to 0 numerically, that's positive evidence for Sarnak on IETs (consistent with Frantzikinakis-Host's complexity-bound argument). If it doesn't, that's a candidate falsifier. Either way: substrate-grade.

**Round 2 Attack 3 — log-Chowla verification (Tao 2017)**

The logarithmic Chowla conjecture is proven (Tao 2016 / Tao-Teräväinen 2018 for higher correlations). Implement the logarithmic average `(1/log N) Σ_{n≤N} μ(n) μ(n+h) / n` for h=1,2,3 and verify Tao's bound numerically. Gives a calibration anchor for what "proven Möbius randomness" looks like in numerics.

**Round 2 Attack 4 — polygonal billiards as wild zero-entropy candidate**

Billiards in polygons with rational angles are zero-topological-entropy but have positive complexity. Implement billiard simulator for a specific polygon (e.g., the L-shaped table or a triangle with rational angles), generate symbolic codes, and run the BSZ correlation test against Möbius. This is a candidate "non-nilpotent zero-entropy" example that has not been settled in the BSZ framework.

**Round 2 Attack 5 — Bratteli-Vershik systems**

Substitution dynamical systems (Thue-Morse, Rudin-Shapiro, Fibonacci) have well-studied complexity. The Möbius orthogonality is open for generic Bratteli-Vershik but has been proven for Thue-Morse (Mauduit-Rivat). Implement the symbolic dynamics + Möbius correlation for a non-Thue-Morse example.

#### Additional solution angles

- **Pretentious number theory (Granville-Soundararajan).** Different from the BSZ approach; uses pretentious-distance metrics on the multiplicative-function space. Applicable directly to the "wild zero-entropy" question.
- **Spectral approach via L-functions.** Möbius is the Dirichlet series coefficient of `1/ζ`; spectral statistics of ζ zeros bear on Möbius sums via explicit formulae.
- **Random multiplicative function model.** Compare actual Möbius statistics to the model where μ(n) is replaced by a random ±1 multiplicative function. Where they agree / disagree is informative.
- **Connection to Birch-Swinnerton-Dyer.** L-function moment statistics under random matrix theory predictions could indirectly bear on Möbius questions.
- **Higher-correlation Chowla.** Tao-Teräväinen 2018 settled triple correlations averaged. The unproven case (non-averaged Chowla) is conjecturally equivalent in difficulty class to Sarnak in many specifications.

#### Datasets / compute tools

- **Pre-computed Möbius table at N=10^{10}** (~10-100 GB). One-time build, then any future Möbius-sum computation is fast.
- **IET / interval-exchange simulator library**. Some Sage support exists; could write minimal Python (~300 LOC).
- **Polygonal billiards simulator** (~500 LOC; reusable for many billiards open problems).
- **Bratteli-Vershik / substitution-system engine** (~400 LOC; covers Thue-Morse, Rudin-Shapiro, Fibonacci).
- **Random-multiplicative-function null-distribution engine** for calibration of Möbius-decay claims.
- **L-function zero database integration** (LMFDB has these; integration with Prometheus's substrate would let any Sarnak-adjacent computation tap into ζ-zero data).

---

### Problem 3 — Palis Conjecture

**B's verdict: NO_PROGRESS_DOCUMENTED_OBSTACLES. Reviewer concur, with caveats.**

#### Critique

The "Lyapunov spectrum is poor for tangency-class non-hyperbolicity, geometric (min-angle) is the right detector" observation is real and substrate-grade. The toy 3D map is admitted by B to be a skew product (structurally rigid; cannot exhibit heterodimensional cycles by construction) — the writeup is honest about this but the implication is that the entire numerical setup is in the wrong attack space for the actual Palis conjecture. The min-angle observation transfers to other 3D dynamics, which is the saving grace.

The literature scan was thorough (10 references) and accurate to the field's state. Three of five attacks were sketched-not-executed.

#### Round 2 — yes, but substantial pivot needed

Estimated effort: ~12-20 hours, plus possibly external library setup (AUTO-07p, CAPD).

**Round 2 Attack 1 — generic 3D Hénon analog (B's sketched Attack 3)**

Implement the 3D Hénon-like map `f_{α,β}(x,y,z) = (1 - α y² + z, x + β y, β z)` as B sketched. Compute fixed points, periodic orbits up to period 10. Track stable/unstable manifolds via numerical parameterization. Search parameter space for heterodim cycle candidates.

**Round 2 Attack 2 — AUTO-07p continuation**

AUTO-07p (or `pde-cont` / Bifurcation Kit in Julia) continues fixed points and periodic orbits in parameter. Setup the 3D Hénon and continue. Find tangency loci, heterodim-cycle loci, and the codim-1 boundary of uniform hyperbolicity. ~6 hours setup + run.

**Round 2 Attack 3 — Bonatti-Diaz blender numerical realization**

The blender constructions in BDV book are explicit. Implement one (e.g., the affine blender on a 3-cube). Verify it has the predicted "hyperplane-thickness" property numerically. If realized correctly, perturb and check whether the perturbation introduces tangency or heterodim cycle as Palis predicts.

**Round 2 Attack 4 — finite-time minimum-angle distribution as a substrate primitive**

B's observation in this problem (min-angle vs Lyapunov) is generalizable. Build a Python/Julia function `min_angle_profile(orbit, jacobian)` that returns the empirical CDF of stable/unstable angle along an orbit. Promote this to the Prometheus methodology toolkit as a candidate `GEOMETRIC_HYPERBOLICITY_DETECTOR@v1` symbol candidate. Cost: ~2 hours; substrate-compounding return.

**Round 2 Attack 5 — periodic orbit growth rate (B's sketched Attack 4)**

Count periodic orbits of period ≤ N for the 3D Hénon. Topological entropy h_top ≈ (log #periodic_orbits) / N for large N. Where h_top is positive but the map is non-hyperbolic, that's the Palis-relevant regime. Use Mischaikow-Mrozek topological methods (CHomP / CMGDB libraries) for rigorous periodic orbit counting.

#### Additional solution angles

- **Singular hyperbolicity** (Morales-Pacifico-Pujals). The Lorenz-attractor-style "singular hyperbolic" theory generalizes uniform hyperbolicity to flows with singularities. Applicable to flow-based Palis variants.
- **Statistical stability under random perturbations** (Alves-Bonatti-Viana). Random small perturbations average out non-hyperbolic zones; the "statistical Palis" question is more tractable than the deterministic one.
- **Computer-assisted proofs of horseshoes** (Mischaikow-Mrozek conley-index / topological methods; CHomP, CMGDB libraries). Establishes hyperbolic structure rigorously in specific systems.
- **Random dynamical systems / Markov approximations** (Liu-Qian, Bahsoun). Approximate the deterministic system by a Markov chain and check Palis-type statements in the approximation.
- **Connecting lemma developments post-Crovisier 2010** — search recent literature (Crovisier-Pujals-Sambarino post-2015) for partial extensions; may be closer to general Palis than B suggests.

#### Datasets / compute tools

- **AUTO-07p Python wrapper** for parameter continuation (exists; needs integration).
- **CAPD Python bindings** (interval arithmetic for rigorous dynamics; exists in C++; Python bindings partial).
- **CHomP / CMGDB integration** for topological computations of invariant sets.
- **Geometric hyperbolicity detector library**: cone-field tracking, dominated-splitting verification, finite-time min-angle distributions. ~500 LOC reusable.
- **Generic-perturbation generator**: given a smooth map, generate a `C^1` random perturbation respecting the manifold structure. ~200 LOC.
- **Periodic orbit catalog** for Hénon-family maps. Useful for many computational dynamics questions.

---

### Problem 4 — Painlevé n-body

**B's verdict: NO_PROGRESS_DOCUMENTED_OBSTACLES. Reviewer concur, with the strongest critique of the batch.**

#### Critique

The weakest deliverable. B attacked n=4 directly with naive symmetric configurations (2+2, 1+3) without first verifying that the integrator can reproduce the proven n=5 case (Xia 1992). The "Attack 3 (sketched, NOT executed)" — Xia n=5 reproduction — is the calibration anchor that should have come *first*, not last.

Concretely: the linear-escape result on naive 2+2 is uninformative. It tells us that symmetric ballistic configurations don't produce singularities; this was already known by structural inspection (no oscillator mediator = no energy transfer). The numerical computation didn't add information beyond what could be argued from the equations.

The "Fleischer 2024" reference flagged as uncertain — should have been arXiv-searched. WebSearch was available; B did not use it. This is a discipline gap, not just a time gap.

The integrator precision (`rtol=1e-11`, double float64) is insufficient for any actual Painlevé-candidate orbit in the binary-tightening regime. Round 2 must use mpmath or CAPD.

#### Round 2 — yes, urgently. The current attempt does not constitute a real Painlevé probe.

Estimated effort: ~20-30 hours. This is the highest-effort round-two of the 5.

**Round 2 Attack 0 (NEW — must come first) — calibration via Xia n=5 reproduction**

Implement Xia's 1992 5-body configuration: two counter-rotating binaries on the z-axis at `±R(t)` plus an oscillator. Use mpmath at 50-100 digit precision. Integrate for a candidate near-singular initial condition. Verify: (a) binary separation `R → 0`, (b) oscillator velocity grows unbounded, (c) total time to singularity is finite. If reproduction succeeds, calibration is established; only then proceed to n=4 attempts.

**Round 2 Attack 1 — Gerver model problem (B's sketched Attack 4)**

Implement Gerver's 1991 4-body planar configuration. Tune initial conditions via Newton-Raphson to find a candidate near-singular orbit. Use mpmath. The unknown is whether the energy-transfer efficiency exceeds the critical value; numerical evidence either way is substrate-grade.

**Round 2 Attack 2 — arXiv search for "Painlevé 4-body" 2020-2026**

WebSearch + WebFetch on arxiv. Verify or refute the Fleischer 2024 claim. Check for Saari-Xia-style updates, recent Diacu surveys, recent Gerver follow-ups. ~30 min of search; potentially massive return if the conjecture has been recently settled or significantly advanced.

**Round 2 Attack 3 — McGehee blow-up coordinates regularization**

McGehee's blow-up transforms binary collisions into regular dynamics on a compact boundary. Implement the blow-up for a 4-body configuration; the binary-tightening becomes orbit transversal to the boundary. Track in blow-up coordinates rather than physical coordinates.

**Round 2 Attack 4 — CAPD interval-arithmetic n-body**

CAPD library (Topological Methods in Dynamics) supports interval-arithmetic n-body. Setup the n=5 Xia case in CAPD; if the rigorous interval bracket of the singularity time is finite, that's a computer-assisted certification. Then attempt n=4 candidates.

**Round 2 Attack 5 — symmetry reduction (Roberts on symmetric Painlevé)**

Symmetric n-body configurations (e.g., the regular n-gon) have reduced phase space. For n=4 with appropriate symmetry, the reduced dimension may admit attacks that the full 12-DOF problem doesn't. Survey Roberts's symmetric central configurations work and the Chenciner-Montgomery figure-8 lineage.

#### Additional solution angles

- **Mather variational methods** (Mather, Chen). The n-body problem has variational structure; minimizers of the action functional over connecting orbits can sometimes be shown to have the desired singularity behavior.
- **Topological methods on configuration space** (Montgomery). The Chenciner-Montgomery figure-8 was discovered topologically; analogous methods may yield singular candidates.
- **Numerical continuation from n=5 to "n=4 limit"**: take Xia's n=5 configuration, send the mass of one body to zero, see what limits.
- **Aubry-Mather sets and minimal action** — connecting periodic and singular orbits.
- **Blue sky catastrophe / cascade-to-infinity bifurcation analysis** — the singularity locus in IC space.

#### Datasets / compute tools

- **mpmath n-body integrator at 50-100 digit precision** (~500 LOC; reusable for any high-precision celestial-mechanics problem).
- **CAPD Python bindings** (existing C++ library; Python bindings partial; integration would unblock interval-arithmetic dynamics across many problems).
- **McGehee blow-up library** for n-body singularity regularization (~800 LOC; specialized but reusable).
- **Symmetric central-configuration database** (Moeckel, Hampton-Moeckel). Existing in scattered papers; aggregating into a queryable dataset would be a substantive substrate primitive.
- **arXiv literature-diff scanner for "n-body Painlevé"** (could integrate with `gen_07_literature_diff` from the Prometheus generator pipeline).
- **Periodic orbit catalog for n=3,4,5 planar n-body** with classification by symmetry type.

---

### Problem 5 — KAM Stability for Hénon-Heiles

**B's verdict: PARTIAL_RESULT. Reviewer concur — second-strongest of the 5.**

#### Critique

Clean execution. The empirical E* ≈ 0.12 reproduction is solid and matches published values. The 30-100× gap between rigorous KAM bounds and empirical chaos onset is the right substrate-grade observation.

Limits: chaos-score (std-of-section-points) is qualitative; SALI/GALI was sketched but not run. The "rigorous KAM bound for Hénon-Heiles" claim is from B's recollection; not actually verified in literature. Energy resolution coarse (12 points). Fourier-Newton iteration sketched but not run.

#### Round 2 — yes, modest effort, high return

Estimated effort: ~6-10 hours.

**Round 2 Attack 1 — SALI/GALI orbit-level chaos certificate (B's sketched Attack 4)**

~50 LOC additional Python. Compute SALI for each of the 72 orbits in B's sweep. Cleanly partition into regular vs chaotic at orbit level. Refines the global E* estimate.

**Round 2 Attack 2 — Fourier-Newton KAM torus parameterization (B's sketched Attack 5)**

For E ∈ {0.05, 0.07, 0.09}, parameterize a candidate KAM torus by Fourier expansion `K(θ) = Σ K_n e^{inθ}`. Solve the cohomological equation by Newton iteration. Convergence ⇔ existence of the torus. Use mpmath at 30+ digits to track high-order Fourier coefficients. ~4 hours of careful coding.

**Round 2 Attack 3 — verify rigorous KAM bounds for Hénon-Heiles in literature**

Search Celletti-Locatelli papers + Llave-Petrov for explicit Hénon-Heiles bounds. WebSearch + arXiv. ~30 min. The "30-100× gap" claim depends on this verification.

**Round 2 Attack 4 — finer energy grid + statistical CIs**

Re-run B's sweep on 100 energies with 50 ICs each. Fit a transition curve `score(E) = a + b · σ((E - E*)/w)` and report E* with bootstrap CI. ~1 hour; gives a clean number, not a range.

**Round 2 Attack 5 — port to 3D Hamiltonian (restricted 3-body)**

Hénon-Heiles is 2-DOF. The substrate-grade interest is whether the 30-100× gap persists in higher-DOF systems (where Arnold diffusion is possible). Port the entire pipeline to the planar restricted 3-body problem (Sun-Jupiter). Compare the empirical-vs-rigorous gap.

#### Additional solution angles

- **Greene's residue criterion** (Greene 1979) for boundary KAM tori. Compute the residues of the periodic orbits accumulating to a candidate boundary torus; the residue tends to a universal value at the breakup.
- **Aubry-Mather cantori at the boundary** — beyond the last KAM torus, invariant cantor sets persist; computing them characterizes the chaotic transition.
- **Renormalization-group approach to KAM** (Koch, Stirnemann). Self-similar structure at the breakup; renormalization computes the universal scaling.
- **Computational KAM via Padé approximants** (Greene-MacKay). Pad approximants to the perturbation series detect singularities; the closest-singularity radius is the KAM threshold.
- **Frequency analysis** (Laskar's NAFF — Numerical Analysis of Fundamental Frequencies). Extract action-angle structure numerically without explicit perturbation theory.

#### Datasets / compute tools

- **SALI/GALI library** (~100 LOC; reusable for any Hamiltonian or symplectic system).
- **NAFF (Laskar frequency analysis) implementation** (~200 LOC; substantively useful across celestial mechanics).
- **mpmath-based Fourier-Newton KAM solver** (~600 LOC; the substantive new build).
- **CAPD-KAM bindings** for rigorous computer-assisted KAM proofs.
- **Cantori computation library** (Aubry-Mather minimizers; ~400 LOC).
- **Hamiltonian benchmark suite**: Hénon-Heiles, restricted 3-body, double pendulum, Toda lattice, Henon map. Standard test cases for any new dynamics tool.

---

## Cross-batch tools to build (priority-ordered)

These tools would benefit multiple problems in the batch and are reusable substrate-grade infrastructure:

| Priority | Tool | LOC est. | Problems benefited |
|---|---|---|---|
| 1 | **mpmath-wrapped n-body / dynamics integrator** | ~500 | 1 (Furstenberg exact arithmetic), 4 (Painlevé high-precision), 5 (KAM Fourier-Newton) |
| 2 | **CAPD Python bindings (or improvement)** | ~200 (binding) | 3 (Palis rigorous horseshoes), 4 (Painlevé interval n-body), 5 (KAM CAS proof) |
| 3 | **Geometric hyperbolicity detector library** (cone fields + min-angle distributions + dominated-splitting verifier) | ~500 | 3 (Palis), 5 (KAM secondary use) |
| 4 | **SALI/GALI/NAFF chaos detection library** | ~300 | 3 (Palis chaos certificates), 5 (KAM orbit classification) |
| 5 | **Möbius pre-computed table at N=10^9 or 10^{10}** | data, ~10-100 GB | 2 (Sarnak primary) |
| 6 | **IET + polygonal billiards + Bratteli-Vershik symbolic dynamics engines** | ~1000 | 1 (Furstenberg analogues), 2 (Sarnak wild-zero-entropy candidates) |
| 7 | **arXiv literature-diff integration with `gen_07_literature_diff`** in Prometheus pipeline | ~200 | All 5 (citation verification) |
| 8 | **AUTO-07p / Bifurcation Kit Python wrapper for parameter continuation** | ~300 | 3 (Palis), 5 (KAM bifurcation) |

A single round-two pass building tools 1, 3, 4 (~1300 LOC, ~30-40 hours of substrate-grade infrastructure work) would dramatically improve the next iteration of all 5 problems plus generalize to other dynamics-flavored work.

---

## Recommended round-two priority order

If full re-execution of all 5 problems is infeasible, the priority order based on (substrate-grade return) × (effort feasibility) is:

1. **Problem 2 (Sarnak)** — modest effort, high substrate return. The N=10^6 → N=10^9 extension alone could either confirm or dissolve the indistinguishability finding. IET + polygonal billiards probes are clean tests of the open frontier.
2. **Problem 5 (KAM Hénon-Heiles)** — modest effort, high concreteness. SALI + Fourier-Newton would convert the qualitative chaos-score result into orbit-level certificates plus rigorous (or near-rigorous) KAM bounds.
3. **Problem 4 (Painlevé)** — high effort, but the current attempt needs a do-over. Calibration via Xia n=5 reproduction is non-negotiable; without it, n=4 attempts are blind. Highest priority for "the current deliverable is insufficient."
4. **Problem 1 (Furstenberg)** — moderate effort. Exact-arithmetic + profinite + Hochman computation would replace the float-collapse failure mode with substantive numerical results.
5. **Problem 3 (Palis)** — high effort, requires AUTO-07p / CAPD setup. Lowest priority because the "right attack space" (3D Hénon, blenders) is substantial new infrastructure; current observation (geometric > Lyapunov) is the salvageable contribution.

---

## Substrate-grade synthesis

The two strongest substrate-grade observations from B's batch — both worth extracting and promoting beyond their original problem context:

- **"Finite-N indistinguishability of proven-orthogonal cases from positive-entropy nulls"** (Sarnak Problem 2 Attack 4). Generalizes to a methodology principle: any numerical falsification battery operating below the asymptotic regime has bounded discriminative power. This is methodology-toolkit-grade. **Proposed promotion:** extend Pattern 21 (null-model selection matters) to include a sub-pattern about asymptotic-vs-finite-N distinguishability.
- **"Geometric (cone-field / min-angle) detection > Lyapunov-spectrum detection for tangency-class non-hyperbolicity"** (Palis Problem 3 Attacks 1-2). Generalizes to: time-asymptotic averages can be insensitive to codim-1 finite-time geometric events. **Proposed promotion:** add `GEOMETRIC_HYPERBOLICITY_DETECTOR@v1` to the methodology toolkit shelf as a candidate.

The two-class obstruction taxonomy in B's summary (Class A "missing rigidity functional" / Class B "missing sharp finite-dimensional bound") is a candidate substrate pattern. **Proposed action:** check it against the Logic / Foundations batch (Harmonia D), Combinatorics (Harmonia A), Topology (Charon 3), and PDE (Harmonia C) outputs to test cross-batch generalizability. If it holds across ≥3 batches at independent anchor problems, it becomes a candidate `OBSTRUCTION_CLASS_TAXONOMY@v1` symbol.

---

*Reviewer note: this critique was performed in ~1.5 hours by Harmonia D. It is necessarily less deep than the batch it reviews; sketched-but-not-executed recommendations should themselves be regarded as Tier-1 candidates for the actual round-two work, not as completed analysis. The priority of recommendations is informed by the operating disposition in `D:\Prometheus\harmonia\memory\restore_protocol.md` (rigor + novelty-seeking + compression-seeking) and the substrate-acceleration moves in `D:\Prometheus\pivot\harmoniaD.md` §6.*
