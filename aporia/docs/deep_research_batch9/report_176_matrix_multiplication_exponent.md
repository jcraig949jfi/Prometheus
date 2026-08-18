# Deep Research Report #176: Matrix Multiplication Exponent ω

**Target Agent:** Charon
**Date:** 2026-04-26
**Front:** Computational complexity (Batch 9 Tier 3)
**Doctrine:** feedback_tensor_first, feedback_domains_are_docstrings, feedback_assume_wrong

## 1. Problem Statement

The matrix multiplication exponent ω is the infimum over real numbers c such that two n×n matrices over a field can be multiplied with O(n^{c+ε}) arithmetic operations for every ε > 0. Equivalently, ω = inf { log_n R(T<n,n,n>) } where T<n,n,n> ∈ F^{n²} ⊗ F^{n²} ⊗ F^{n²} is the matrix multiplication tensor and R(·) is tensor rank (or asymptotic/border rank under standard equivalences).

Output cardinality forces ω ≥ 2. Strassen (1969) shattered the cubic barrier with R(T<2,2,2>) ≤ 7, giving ω ≤ log_2 7 ≈ 2.807. The current world record is **ω < 2.371552** (Williams-Xu-Xu-Zhou 2024) via refinements of the Coppersmith-Winograd laser method on powers of a structured starting tensor. Alman and Vassilevska Williams (2018, 2021) proved **structural barrier results**: a wide class of laser-method instantiations cannot reach ω = 2, and any further laser-method gain is bounded below an explicit constant > 2. The conjecture ω = 2 is widely cited but with no proof and decreasing consensus that the existing toolkit can attain it.

## 2. Literature

- **Strassen (1969):** ω ≤ 2.807; founding tensor decomposition.
- **Pan (1978), Bini-Capodaglio-Lotti-Romani (1979):** border rank, approximate algorithms.
- **Schönhage (1981):** τ-theorem (asymptotic sum inequality).
- **Strassen (1986, 1987):** laser method; ω ≤ 2.479.
- **Coppersmith-Winograd (1990):** ω < 2.376 via the CW tensor at q = 6.
- **Stothers (2010), Williams (2012):** higher tensor powers; ω < 2.3729.
- **Le Gall (2014):** ω < 2.37286 with systematic power optimization.
- **Alman-Vassilevska Williams (2021):** ω < 2.37286 (refined); same authors (2018) proved the laser-method barrier.
- **Duan-Wu-Zhou (2022):** ω < 2.371866 via asymmetric hashing.
- **Williams-Xu-Xu-Zhou (2024):** ω < 2.371552, current record.
- **Cohn-Umans (2003), Cohn-Kleinberg-Szegedy-Umans (2005):** group-theoretic / CKSU framework — ω = 2 reducible to existence of abelian groups satisfying a triple-product (USP / strong USP) condition.
- **Blasiak-Church-Cohn-Grochow-Naslund-Sawin-Umans (2017):** several CKSU candidate constructions ruled out by cap-set bounds.

## 3. Computational Handle

Matrix-mult tensors at small n have tractable rank-decomposition search. R(T<2,2,2>) = 7 (Strassen, optimal proven by Landsberg). R(T<3,3,3>) is bounded between 19 and 21 (Smirnov, Heun, AlphaTensor); R(T<4,4,4>) ≤ 47 over F_2 (AlphaTensor 2022), ≤ 49 over Z. SDP relaxations (Bürgisser-Ikenmeyer) and the support-rank framework give upper bounds on ω asymptotically without exhibiting decompositions. The **Alman-Vassilevska Williams 2018 barrier** is structural: it proves any laser-method instantiation on a fixed starting tensor of CW-type cannot give ω < 2.16805, regardless of which tensor power is used. This argues ω = 2 needs a fundamentally different construction (CKSU group, geometric, or unknown).

## 4. Test Design

**Step 1.** Enumerate small-rank decompositions of T<n,n,n> for n ∈ {2, 3, 4, 5} via constraint-solving and AlphaTensor-style local search; verify Strassen rank 7 and reproduce Smirnov's R(T<3,3,3>) ≤ 23, AlphaTensor's R(T<4,4,4>) ≤ 47/F_2.

**Step 2.** Implement the CKSU group-product framework for small abelian groups (Z_n^k, n ≤ 16, k ≤ 6); test the strong-USP condition; record which groups admit non-trivial USP families and which are ruled out by cap-set / slice-rank bounds.

**Step 3.** Cluster matrix-mult tensors by rank-decomposition signature (multiplicity of structured slices, symmetry orbit, border-rank gap). Identify the **structural region** whose decomposition class achieves the lowest known ω contribution per unit of decomposition complexity.

**Step 4.** Megethos signature on the time-series of ω upper bounds {2.807, 2.479, 2.376, 2.3729, 2.37286, 2.371866, 2.371552}. Fit decay forms (exponential, double-exponential, power, plateau-with-jumps); estimate posterior on next-bound location and on the asymptote.

## 5. Falsification

- **Extraordinary outcome:** any new ω upper bound — direct publication.
- **Strong:** structural pattern in the laser-method barrier matching cap-set or slice-rank exponents → publishable narrowing of the obstruction class.
- **Medium:** ω-improvement series fits a clean decay form with predictive value (next bound within a CI of width < 10⁻³) → calibration tool for tracking the field.
- **Strong:** novel CKSU group passing the strong-USP condition not ruled out by 2017 cap-set bounds → direct ω = 2 path candidate.
- **Null:** small-tensor enumeration recovers known ranks, no new CKSU group survives, decay fit is flat → confirms barrier and hardens the conjecture that current toolkit is exhausted.

## 6. Budget

Charon ~6 hours. Tensor-rank enumeration code (~2h, Sage + numpy + SAT/ALS hybrid). CKSU framework + USP search (~2h). Structural-region clustering and Megethos rate fit (~1h). Writeup (~1h).

## 7. Expected Outcome

Empirical map of small-tensor decompositions cross-referenced against published optima; structural data on the laser-method barrier as a function of starting-tensor symmetry; rate analysis of the ω-improvement series with explicit posterior on the next bound. Most likely: confirms the barrier and produces a calibrated tracker, no new bound. Real prize: a CKSU group surviving the 2017 elimination, or a structural invariant separating "barrier-bound" from "barrier-evading" decompositions. Connects complexity theory to the unified tensor's algebraic-geometry region (border rank, secant varieties of Segre, GIT stability of T<n,n,n>) — a natural bridge to the rest of Prometheus's tensor substrate.

**Word count: 766**
