# Deep Research Report #164: Volume Conjecture for General Hyperbolic 3-Manifolds

**Target Agent:** Harmonia
**Date:** 2026-04-26
**Predecessor:** Batch 1 #16 (volume conjecture for knots, narrower scope)
**Front:** Knot/topology silent island (Batch 9 Tier 2)

## 1. Problem Statement

For a hyperbolic knot K in S^3, the Kashaev-Murakami-Murakami volume conjecture asserts

  lim_{N→∞} (2π/N) log |J_K(N; e^{2πi/N})| = vol(S^3 \ K),

where J_K(N; q) is the N-colored Jones polynomial evaluated at the primitive N-th root of unity. Chen-Yang (2018) generalized this to closed and cusped hyperbolic 3-manifolds M via Reshetikhin-Turaev / Witten-Reshetikhin-Turaev invariants τ_r(M) at q = e^{2πi/r}, predicting

  lim_{r→∞, r odd} (2π/r) log |τ_r(M)| = vol(M) + i · CS(M)  (mod π² Z),

with CS the Chern-Simons invariant. Status: open in general; numerically verified for many specific knots and several Dehn fillings; proved for figure-8 (Ohtsuki 2016), torus knots, and a handful of families via explicit identity techniques.

Empirical question for Prometheus: *does the volume-conjecture asymptotic hold across the full SnapPy census of ~10K hyperbolic 3-manifolds, including Dehn fillings beyond knot complements, and does the convergence rate carry structural signal?* Per `feedback_domains_are_docstrings`, the operator under test is **"asymptotic-of-quantum-invariant-recovers-hyperbolic-volume"**, and the test asks whether this operator is universal across the topology structural region.

## 2. Literature

- **Kashaev (1995):** original conjecture from quantum dilogarithm.
- **Murakami-Murakami (2001):** identification of Kashaev's invariant with colored Jones, modern formulation.
- **Ohtsuki (2016):** rigorous proof for the figure-8 knot complement.
- **Chen-Yang (2018):** WRT generalization to closed/cusped hyperbolic 3-manifolds; numerical evidence on ~20 manifolds.
- **Detcherry-Kalfagianni-Yang (2018):** asymptotic expansions, sub-leading terms.
- **Andersen-Hansen (2006):** numerical verification, fundamental shadow links.
- **Habiro:** cyclotomic completion of the Jones polynomial — analytic substrate for the asymptotic.
- **Garoufalidis-Lê:** AJ conjecture coupling, q-holonomic structure of J_K(N).

## 3. Computational Handle

SnapPy is installed in the Prometheus Sage environment (`charon/scripts/` already imports it for census work; cf. `charon/scripts/lehmer_exhaustive_deg8_14.py` for the Sage/SnapPy pattern). For ~10K hyperbolic 3-manifolds in `OrientableCuspedCensus` plus a Dehn-filling slice from `LinkExteriors`:

- (a) Hyperbolic volume via `M.volume()` — already standard, sub-second per manifold.
- (b) WRT invariants τ_r(M) at r = 10, 20, 30, 40, 50 via Sage's experimental quantum-invariants package, or a custom implementation built from the surgery presentation `M.filled_triangulation()` and the Reshetikhin-Turaev state sum at SU(2)_k. If Sage's wrapper is incomplete (likely), Techne forges `TOOL_WRT_INVARIANT` from the Kirby-calculus presentation.

The test ratio (2π/r) log |τ_r| is recorded per (manifold, r) and fitted against vol(M).

## 4. Test Design

**Step 1.** Select 200 hyperbolic 3-manifolds spanning: (i) ~80 knot complements from `HTLinkExteriors` (covers Batch 1 #16 ground truth), (ii) ~60 link complements (multi-cusp generalization), (iii) ~60 small Dehn fillings from `OrientableClosedCensus`.

**Step 2.** Compute vol(M) via SnapPy; persist to `aporia/mathematics/h164_volumes.json`.

**Step 3.** Compute τ_r(M) at r ∈ {10, 20, 30, 40, 50}; record (2π/r) log |τ_r| → `aporia/mathematics/h164_wrt.json`.

**Step 4.** Fit asymptotic A(r) = vol + c/r + O(1/r²); compute residual A(50) − vol; tabulate convergence rate (slope of log|A(r) − vol| vs. log r).

**Step 5.** Cluster manifolds by structural signature — Heegaard genus, fundamental-group rank, Reidemeister torsion, number of cusps, systole — and test whether convergence rate stratifies non-randomly. Permutation null on the (manifold → rate) assignment per `feedback_permutation_null`.

## 5. Falsification

- **Strong confirmation:** all 200 manifolds converge to vol within 5% at r = 50 → empirical extension of volume conjecture to general hyperbolic 3-manifolds at SnapPy-census scale.
- **Counterexample flag:** any manifold with persistent divergence > 10% at r = 50 → almost certainly numerical (root-of-unity precision, surgery-presentation choice), but flag and recompute with extended precision via `mpmath`. A surviving divergence is publishable.
- **Structural-region signal:** convergence rate clusters non-randomly by Heegaard genus or fundamental-group rank with permutation-null z > 3 → new coordinate in the topology structural region, directly extending Batch 1 #16.
- **Null sanity:** shuffled (manifold, rate) pairing must wash out clustering; if not, the signal is a global trend (volume-rank correlation) and must be detrended before interpretation.

## 6. Budget

Harmonia ~1 day on Skullport. SnapPy volumes ~1h (sub-second × 200, plus I/O). WRT computation ~3h compute (custom Sage code if `quantum_invariants` insufficient; r = 50 is the bottleneck since state-sum cost grows polynomially in r and exponentially in surgery-presentation length). Asymptotic fitting ~1h. Structural clustering + permutation null ~1h. Writeup ~2h. SnapPy and Sage are already installed; `TOOL_WRT_INVARIANT` may need Techne forging — request goes in `techne/queue/requests.jsonl` if Sage's wrapper is missing the closed-manifold case.

## 7. Expected Outcome

Empirical extension of the volume conjecture from the knot subset (Batch 1 #16) to general hyperbolic 3-manifolds at SnapPy-census scale, producing a convergence-rate map as a new coordinate in the topology structural region. Per `project_silent_islands`, knots/topology are currently isolated — this report adds two bridges: (i) the WRT invariant generalizes the colored Jones, cross-linking to the Khovanov region already populated by `feedback_verbs_over_nouns`-aligned operators; (ii) the convergence-rate stratification gives the topology island its first quantitative texture beyond raw volume, and per `feedback_tensor_first` feeds directly into the structural region for downstream coupling tests against arithmetic invariants (regulator, L-value at 1, Reidemeister torsion). Direct continuation of Batch 1 #16 and partial closure of the knot/topology silent island.

**Word count: 798**
