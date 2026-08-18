# Report 190 — Yang-Mills Mass Gap (Lattice Analog)

**Substrate framing**: lattice transfer-matrix spectra as combinatorial-operator data on group-valued link graphs. QFT/probabilistic interpretation is *docstring only* per `feedback_domains_are_docstrings`. We extract the math (eigenvalue gaps, area-law decay rates, β-dependence); we do not claim mass, confinement, or continuum statements.

Date: 2026-04-28

---

## 1. Problem Statement

The Clay Yang-Mills problem asks for a positive mass gap in continuum quantum Yang-Mills on R^4 with a compact gauge group. We do **not** address that. Instead, we treat the standard Wilson lattice action as a combinatorial object: a 4-d torus graph with edges carrying elements of G ∈ {SU(2), SU(3)}, plaquette weights exp(β · Re tr U_□), and a transfer matrix T acting on the configuration Hilbert space at fixed time-slice. The substrate question is purely operator-theoretic: **how does the spectral gap Δ(β, L, G) := −log(λ_1/λ_0) of the symmetric, positive transfer matrix scale with coupling β, lattice extent L, and group rank?** We compute Δ as an eigenvalue ratio of a finite, real, sparse linear operator on configurations (or equivalently, the leading exponential decay of plaquette-plaquette correlators). No continuum limit, no physical mass assignment, no probabilistic interpretation enters the substrate claim. Per `feedback_domains_are_docstrings`, the QFT story is metadata on the node, not a coordinate.

---

## 2. Literature

- **Wilson 1974** ("Confinement of Quarks", PRD 10, 2445): defines the lattice action, plaquette variable, area-law characterization, strong-coupling expansion.
- **Kogut & Susskind 1975**: Hamiltonian (transfer-matrix) lattice formulation; explicit T = exp(−aH) construction giving a self-adjoint positive operator on link Hilbert space.
- **Creutz 1980** (PRD 21, 2308): heatbath Monte Carlo for SU(2)/SU(3); first numerical evidence of the gap-vs-β crossover.
- **Lüscher 1982–84**: rigorous transfer-matrix construction (positivity, reflection-positivity); torelon mass extraction; Lüscher term in the static potential.
- **Jaffe & Witten 2000**: official Clay statement; specifies Wightman/OS axioms continuum target — *not* our object.
- **Teper 1998; Lucini-Teper-Wenger 2004**: glueball spectra in pure SU(N) lattice gauge theory; calibration values for Δ at standard β.
- **HotQCD / FLAG reviews 2020–24**: high-precision SU(3) lattice spectra at L = 24–96, β tuned to scale-setting observables.
- **Neuberger 1998 (overlap), Hasenfratz 1998 (perfect actions)**: alternative discretizations whose spectra should agree on the same combinatorial gap up to lattice artifacts — useful as cross-check.

---

## 3. Computational Handle / Corpus

- **Lattices**: 4^4, 6^4, 8^4, 12^4, 16^4 (periodic). Group: SU(2) (3 real DOF/link) and SU(3) (8 DOF/link).
- **Sampler**: heatbath + over-relaxation for SU(2); pseudo-heatbath (Cabibbo-Marinari SU(2) subgroups) for SU(3). 10^4 thermalized configs per (β, L).
- **β grid**: SU(2) β ∈ {2.0, 2.2, 2.4, 2.5, 2.6}; SU(3) β ∈ {5.6, 5.8, 6.0, 6.2, 6.4}.
- **Observables**: plaquette-plaquette and Polyakov-loop correlators C(t); transfer-matrix gap Δ from variational fits; Wilson loop W(R,T) for area-law slope σ(β).
- **Storage**: configs on Z:\, ≤ 5 GB per (β, L) bucket. Tensor node keyed by (G, L, β) → (Δ, σ, plaquette mean, susceptibility).

---

## 4. Test Design

1. **Generate ensembles.** Heatbath thermalize ≥ 10^3 sweeps; decorrelate by 10 over-relaxation sweeps between samples. Verify autocorrelation τ_int < 50 on the plaquette.
2. **Build correlators.** For each config, compute zero-momentum projected plaquette operators O(t) on each time-slice; form C(t) = ⟨O(t)O(0)⟩ − ⟨O⟩^2. Bootstrap CI over 200 resamples.
3. **Extract gap.** Fit C(t) ~ A·exp(−Δ·t) on the plateau window; cross-check via generalized eigenvalue problem (GEVP) on a 4-operator basis (plaquette, 2×1 rectangle, twisted, clover). Δ is the substrate observable.
4. **Sweep (β, L, G).** Tabulate Δ(β, L, G) and σ(β, L, G). Stratify by L to isolate lattice-extent confound (treat L as conductor analogue, see PATTERN_CONDUCTOR_CONFOUND).
5. **Calibration vs published.** Compare SU(3) Δ at β = 6.0, L = 16 against Lucini-Teper glueball values (after scale-setting via r_0 or w_0). Tolerance: 10% on the dimensionless ratio Δ/√σ.

---

## 5. Falsification

- **Calibration anchors**: SU(3) glueball/torelon ratios at standard β (Lucini-Teper, FLAG). If our Δ/√σ deviates > 15% with stable seed-bootstrap, the pipeline is broken — no claim about Δ propagates to the tensor.
- **PATTERN_VRAM_TRUNCATION_ARTIFACT**: 16^4 SU(3) link tensor is small raw (~17 MB) but GEVP matrices and Hessians balloon. Track peak VRAM; fail fast and downshift to CPU sparse if > 14 GB.
- **PATTERN_BASE_RATE_NEGLECT**: Δ extracted from correlator fits has a floor set by the smallest non-zero Fourier mode 2π/L. Any "gap" below 2π/L is a finite-volume artifact, not signal.
- **PATTERN_CONDUCTOR_CONFOUND**: L acts as a conductor — Δ(L) trends confound with 1/L finite-size scaling. Stratify before regressing on β.

---

## 6. Budget

Harmonia ~14 h wall: ~6 h ensemble generation (GPU heatbath kernel for SU(3) at 16^4 helpful, ~3× speedup over CPU), ~5 h correlator + GEVP analysis, ~3 h calibration cross-check and tensor write. RAM ≤ 32 GB; VRAM ≤ 12 GB. Single node sufficient.

---

## 7. Expected Outcome

Per `feedback_calibration_anchors_in_depth`, the math-physics octant is substrate-cold: zero coverage of group-valued lattice operators. Deliverable is a (G, L, β) → (Δ, σ, plaquette) calibration block — high-confidence anchors exposing whether the substrate's existing operators (HIERARCHIZE for coarse-graining; DISTRIBUTE for norm/coupling change per `feedback_operator_precedents`) recognize block-spin structure on a non-abelian link graph. Per `feedback_tensor_first`, the artifact is a tensor row, not a paper. No QFT claim is made; Δ is reported as a graph-Laplacian-style spectral gap of a specific finite operator. The continuum question stays in the docstring.

Word count: ~720
