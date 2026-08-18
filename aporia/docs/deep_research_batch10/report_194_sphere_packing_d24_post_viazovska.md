# Deep Research Report #194: Sphere Packing Density in d=24 — Post-Viazovska Refinement Candidates

**Target Agent:** Ergon
**Date:** 2026-04-28
**Front:** Discrete geometry / lattices (Batch 10 Tier 1)

## 1. Problem Statement

The sphere packing density Δ_d in dimension d asks for the supremum of the fraction of R^d covered by disjoint unit balls centered on a discrete set. Cohn-Elkies (2003) reduced an upper bound on Δ_d to a linear-programming dual: any radial Schwartz function f with f̂(0) ≥ f(0) and f(x) ≤ 0 for |x| ≥ r yields Δ_d ≤ vol(B_{r/2})·f̂(0)/f(0). Viazovska (2017) constructed the *magic function* in d=8 from quasi-modular forms of weight 8 for SL_2(Z), giving the sharp bound matched by E_8. Cohn-Kumar-Miller-Radchenko-Viazovska (2017) extended the construction to d=24, settling Δ_24 with the Leech lattice Λ_24 saturating the LP bound.

The conjecture is closed at d=8 and d=24. The open question is structural: *which other dimensions admit Viazovska-style modular-form magic functions*, and what operator-level signature distinguishes those dimensions from generic ones? Conjectural candidates include d=12 (Coxeter-Todd K_12), d=16 (Barnes-Wall BW_16), d=32 (extremal Type II lattices), and d=48 (P_{48p}, P_{48q}). The substrate question this brief defines: across ~100 known lattices in d=4..48, can an empirical structural-signature scan identify "Viazovska-eligible" candidates and produce calibrated rankings per dimension?

## 2. Literature

- **Cohn-Elkies (2003):** LP bound on Δ_d via Poisson summation; sharp at d=1, conjecturally sharp at d=8, 24.
- **Viazovska (2017):** d=8 magic function from weight-8 quasi-modular forms; first non-trivial dimension above 1 with sharp LP bound.
- **Cohn-Kumar-Miller-Radchenko-Viazovska (2017):** extension to d=24 via weight-12 quasi-modular forms and the Leech lattice.
- **Cohn-Triantafillou (2022):** numerical LP bounds in d ≤ 1024; identifies "near-saturation" regions.
- **Conway-Sloane, *Sphere Packings, Lattices and Groups* (1999):** canonical reference; theta-series, kissing numbers, automorphism groups for ~100 lattices in d ≤ 48.
- **Bannai (2009):** Q-polynomial association-scheme conjecture relating spherical-design strength to LP saturation.
- **Nebe-Venkov, Nebe-Sloane catalogue:** extremal Type II lattices in d=32, 40, 48, 80.

## 3. LMFDB / Corpus Data

LMFDB has limited lattice coverage (no `lattices` schema at scale). Primary corpus is the Conway-Sloane catalogue plus the Nebe-Sloane online lattice database (Nebe's Aachen mirror), giving for ~100 lattices in d=2..48: gram matrices, theta-series coefficients (typically first 50-200), kissing numbers τ(L), automorphism group orders |Aut(L)|, root system class, spherical-design strength t(L), Type (I/II), minimum norm. Supplementation: the LMFDB modular-form tables can classify theta-series by weight and level matching for low d.

## 4. Test Design

**Step 1.** Pull ~100 lattices in d=4..48 from the Nebe-Sloane catalogue: gram matrix, theta-series first 50 coefficients, τ(L), |Aut(L)|, root system, design strength.

**Step 2.** Compute structural signature vector per lattice:
- Theta-series first N=50 coefficients θ_L(q) = Σ N_k q^k.
- log |Aut(L)| (high-symmetry indicator).
- Spherical-design strength t(L) (Bannai-Venkov).
- Root system class (ADE label or "rootless").
- Modular weight/level fit of θ_L: regress against basis of M_{d/2}(Γ_0(N)) for small N.

**Step 3.** Per `PATTERN_PRIME_GRAVITATIONAL_OVERFIT`: detrend theta-series coefficients by prime-power structure (N_{p^k} typically dominates Σ N_k); work with residual coefficients after subtracting the prime-power baseline.

**Step 4.** Stratify by dimension; cluster lattices in signature space (UMAP/HDBSCAN). Identify per-dimension top candidate (highest Aut order × design strength × clean modular fit).

**Step 5.** Calibrate against known anchors per `feedback_calibration_anchors_in_depth`: E_8 must rank #1 in d=8; Λ_24 must rank #1 in d=24. K_12 should rank #1 in d=12 (matches Cohn-Elkies-Triantafillou conjectural saturation).

**Base rates per `PATTERN_BASE_RATE_NEGLECT`:** report n_d = number of lattices tested per dimension; expected null rank is uniform on [1, n_d]; an anchor at rank 1 with n_d ≥ 5 is non-trivial.

## 5. Falsification

- **Calibration pass:** E_8 and Λ_24 cluster at top of their dimensions (rank-1 in signature score, n_d ≥ 5 lattices in each). Signature is calibrated.
- **Calibration fail:** anchors do not separate from generic lattices → signature too coarse; refine with Eisenstein/cusp decomposition of θ_L or add Voronoi-cell volume.
- **Positive finding:** at d ∈ {12, 16, 32, 48}, exactly one lattice matches the anchor signature (z > 2 versus dimension cohort) → publishable Viazovska-eligibility candidate.
- **Null:** permute lattice→dimension assignment; rank distribution must collapse to uniform.

## 6. Budget

Ergon ~6h: catalog data pull (~1h, Nebe-Sloane scrape + Conway-Sloane parse), signature computation (~2h, theta-series + design strength + modular regression; uses TOOL_SDP_RELAX REQ-029 if forged for Cohn-Elkies LP refinement at intermediate d), clustering (~1h), structural analysis vs anchors (~1h), writeup (~1h).

## 7. Expected Outcome

Ranked table of Viazovska-eligibility candidates per dimension d=4..48 with structural-signature score and dimension-cohort z. E_8 and Λ_24 anchor the high end; K_12, BW_16, extremal Type II at d=32, P_{48p/q} at d=48 are the predicted top candidates if the signature transfers. A clean separation of anchors from generic lattices in signature space identifies the "magic-function regime" as an operator-level structural region of lattice space, not as a dimension-specific accident. Per `feedback_calibration_anchors_in_depth`, this extends the discrete-geometry calibration density into d ∈ {4..48} \ {8, 24}, where the substrate currently has zero coverage. Negative outcome — no separation — is itself calibrated information: the magic-function regime is finer than first-50-coefficient theta + Aut + design strength can resolve.

**Word count: 798**
