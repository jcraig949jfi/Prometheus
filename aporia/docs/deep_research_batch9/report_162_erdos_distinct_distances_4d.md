# Deep Research Report #162: Erdős Distinct Distances in Dimension ≥ 4

**Target Agent:** Ergon
**Date:** 2026-04-26
**Front:** Erdős corpus expansion (Batch 9, Tier 2)
**Doctrine:** feedback_tensor_first, feedback_domains_are_docstrings, feedback_assume_wrong

## 1. Problem Statement

Let g_d(n) denote the minimum, over all n-point sets P ⊂ R^d, of the number of *distinct* pairwise Euclidean distances |{‖x − y‖ : x, y ∈ P, x ≠ y}|. Erdős (1946) conjectured g_2(n) = Ω(n / √(log n)), realized by the √n × √n integer grid. Guth–Katz (2010) settled d = 2 with g_2(n) ≥ c · n / log n via the polynomial partitioning / algebraic method, off by only √(log n).

For d ≥ 3 the conjectured bound is g_d(n) = Ω(n^{2/d}) (or possibly Ω(n^{2/d} / log n)), again realized by [n^{1/d}]^d integer grid sections. What is *proved* is substantially weaker: Solymosi–Vu (2008) gave g_d(n) = Ω(n^{2/d − 2/(d(d+2))}), an exponent strictly below 2/d that decays toward 2/d only as d → ∞. Iliopoulou–Sharir (mid-2010s) refined incidence and joints-type bounds in R^3 and R^4 but did not close the gap. The exact exponent in dimensions 3, 4, 5, 6 is **open**. The structural region: which configurations actually saturate g_d, and is the extremizer always lattice-like?

## 2. Literature

- **Erdős (1946)** — original conjecture, grid lower bound for d = 2.
- **Solymosi–Tóth (2001)** — n^{6/7} bound in d = 2 via crossing-number method; first major post-Erdős advance.
- **Guth–Katz (2010, *Annals*)** — n / log n in d = 2 via polynomial partitioning + ruled-surface flecnode argument; landmark.
- **Solymosi–Vu (2008)** — g_d(n) = Ω(n^{2/d − 2/(d(d+2))}); current best general dimension lower bound.
- **Iliopoulou (2014), Sharir–Solomon (2017)** — incidence bounds for points and curves/surfaces in R^3, R^4 underlying refinements.
- **Zahl, Kollár, Guth** — joints theorem in R^d; relevant infrastructure.
- **Sheffer, *Polynomial Methods and Incidence Theory* (Cambridge, 2022)** — canonical reference unifying the algebraic toolkit.

## 3. Computational Handle

Distinct-distance counts are directly enumerable: for n ≤ ~2000 in dimension ≤ 6 the squared-distance multiset has size ≤ n(n−1)/2 ≈ 2·10^6, a one-pass scipy.spatial.distance.pdist + np.unique with rational rounding (squared distances are integers for lattices, avoiding float collisions). Candidate extremizers: Z^d ∩ B(0, R), hypercubes [k]^d, root lattices A_n, D_n, E_6, E_7, E_8, the Leech lattice section, and shells of these (n-point selections of bounded shells). SDP / Lasserre relaxations of the upper-bound problem (max distinct distances under constraints) are tractable up to n ~ 200 and pin candidate dual certificates.

## 4. Test Design

**Step 1.** Enumerate distinct distances exactly (using squared norms over Z) for structured point sets at n ∈ {50, 100, 200, 500, 1000} in d ∈ {3, 4, 5, 6}: Z^d ∩ ball, hypercubes [k]^d, root-lattice balls (D_4, E_8 sections), and projected lattices. Fit log g(n) vs log n; report exponent α_d and 95% bootstrap interval per family.

**Step 2.** Generate Gaussian and uniform-in-ball random point clouds at matched (n, d). Distinct-distance count is generically n(n−1)/2 (no collisions); use as null and as the *anti-extremizer* baseline.

**Step 3.** Cluster lattice families by distinct-distance density δ(n, d) = g(n) / n^{2/d}. Identify which families minimize δ in each dimension; in particular test whether D_4 beats Z^4 in d = 4 and whether E_8 beats Z^8 in d = 8 (known dense-packing extremizers).

**Step 4.** Compute the Megethos signature (log-magnitude basis-e operator) on g(n, d) treated as a two-variable observable. Check whether the natural exponent of g under Megethos coordinates aligns with the conjectured 2/d, with the proved Solymosi–Vu exponent, or with neither.

## 5. Falsification

- **Strong positive:** an explicit configuration in d = 3 with g(n) measurably below the n^{2/3} grid count (at n = 1000, fitted exponent < 0.66 with bootstrap CI excluding 2/3) → publishable lower-bound improvement / new extremizer family.
- **Structural confirmation:** signature clustering cleanly separates lattice from random with margin > 5σ in distinct-distance density → confirms the conjecture's structural form, justifies grid-as-extremizer doctrine.
- **Operator alignment:** Megethos-natural exponent matches 2/d to within 0.02 across d = 3–6 → operator coordinates align with discrete-geometry conjecture; cross-domain tensor entry earned.
- **Null kill:** if random clouds and lattices share a signature (no separation), the tensor coordinate is uninformative for this front; report and shelve.

## 6. Budget

Ergon ~6 hours: enumeration code with exact squared-norm hashing (~2h), structured-point-set sweep across (n, d, family) grid (~2h), structural / Megethos analysis (~1h), writeup with plots (~1h). NumPy + scipy.spatial sufficient; no GPU, no external data pull.

## 7. Expected Outcome

An empirical map of g_d(n) for d = 3–6 across ~10 structured families, fitted exponents with CIs, and identification of candidate extremizers per dimension (prior: Z^d wins in d = 3, root lattices D_4 / E_8 may compete or win in d = 4, 8). Structural-signature data feeds the unified Prometheus tensor with discrete-geometry coordinates currently absent. Cross-links: lattice arithmetic (theta series, kissing numbers), sphere packing (Cohn–Elkies, Viazovska in d = 8, 24), and the algebraic-method literature already in the Charon corpus. Realistic prior: grid wins, conjecture holds empirically, value is a *calibrated* discrete-geometry coordinate plus a tested null protocol — not a counterexample.

**Word count: 798**
