# Report 16 — Cross-Domain Operator Transport Benchmark Catalog

**Topic:** Known megethos-style operator transports across mathematical disciplines
**Date:** 2026-05-02
**Purpose:** Seed Prometheus's calibration anchor set in the cross-region structure-discovery region.

## 1. Situation

A *cross-domain operator transport* is a verified isomorphism (or natural transformation) between two formally distinct mathematical regions such that an operator native to one region — when transported via the bridge — predicts numerical invariants in the other to high precision. The transport is empirically established when independently computed quantities on each side agree at many digits (or, in the discrete case, on infinitely many test cases).

F011 is Prometheus's canonical internal example: a single bulk-rigidity operator at gap-k=24 produces a +46–51% deficit in three Katz–Sarnak symmetry classes (non-CM EC, CM EC, genus-2 USp(4)). The deficit *magnitude* is the calibration anchor. Megethos generalises this: 44% of Prometheus's cross-domain coupling sits in raw magnitude because magnitude is a behaviour, not a label. To calibrate the tensor, we need a catalogue of *historically established* operator transports whose anchor numerics we can ingest as ground truth.

## 2. Catalog of known megethos-style transports

**(a) Modularity (Wiles / Taylor–Wiles / BCDT / Khare–Wintenberger).** Source: elliptic curves over Q (and totally real fields). Target: weight-2 newforms on Γ0(N) / Galois representations. Operator: the Hecke operator T_p on the modular side equals a_p(E) = p+1 − #E(F_p) on the curve side. Anchor: for every prime p ∤ N, the integer a_p(E) computed by point-counting equals the q-expansion coefficient of the associated newform. Verified numerically across LMFDB's full elliptic-curve database (~3.8M curves). Khare–Wintenberger (2009) extends the bridge to all odd 2-d residual reps of G_Q.

**(b) Langlands transfer (functoriality).** Source: automorphic representations on a reductive group H. Target: automorphic reps on a larger group G via a map of L-groups L_H → L_G. Operator: Satake parameters / local L-factors transport unchanged. Anchor: equality of partial L-functions L^S(s, π, r) = L^S(s, Π) at every unramified prime. Cogdell–Kim–Piatetski-Shapiro–Shahidi proved GL_n × GL_m functoriality cases; Arthur (2013) settled classical groups → GL_N.

**(c) Sato–Tate (Barnet-Lamb–Geraghty–Harris–Taylor 2011).** Source: motivic L-functions of non-CM elliptic curves. Target: Haar measure on SU(2). Operator: normalised Frobenius angle θ_p = arccos(a_p / 2√p). Anchor: empirical histogram of {θ_p : p ≤ X} converges in total variation to (2/π) sin²θ dθ; convergence rate matches the L-function's analytic continuation. Multi-domain generalisation (Sato–Tate for higher symmetric powers) verified via Kim–Shahidi symmetric-power lifts.

**(d) Katz–Sarnak (function-field zeta / random matrix theory, 1999).** Source: zeros of L-functions over F_q(t) families. Target: eigenvalues of classical compact groups U(N), USp(2N), O(N). Operator: low-lying zero density. Anchor: pair-correlation and 1-level density agree with Gaudin–Mehta kernel; deviations scale as 1/log q. Confirmed numerically by Rudnick–Sarnak and by Conrey–Snaith moment conjectures.

**(e) Monstrous moonshine (Conway–Norton 1979; Borcherds 1992).** Source: irreducible character dimensions of the Monster sporadic group. Target: Fourier coefficients of the j-invariant on the upper half-plane. Operator: McKay–Thompson series T_g(τ) for each conjugacy class g. Anchor: c(1) = 196,884 = 1 + 196,883; every Fourier coefficient equals a non-negative integer combination of Monster character dimensions. Borcherds proved via vertex operator algebras and the Goddard–Thorn no-ghost theorem.

**(f) Selberg trace formula (Selberg 1956).** Source: length spectrum of closed geodesics on a hyperbolic surface. Target: spectrum of the Laplacian Δ on L²(Γ\H). Operator: trace of the heat/wave kernel. Anchor: for every test function h with controlled Paley–Wiener transform, Σ h(r_n) = (vol/4π)∫h(r)r tanh(πr)dr + Σ_γ (geometric side). Numerical verification by Hejhal, Steil, Then.

**(g) Riemann–Roch (Riemann 1857; Roch 1865).** Source: divisors on a smooth projective curve C of genus g. Target: cohomology dimensions of line bundles. Operator: ℓ(D) − ℓ(K−D). Anchor: ℓ(D) − ℓ(K−D) = deg D − g + 1, exact integer equality on every divisor.

**(h) Gauss–Bonnet.** Source: pointwise Gaussian curvature K of a closed surface. Target: Euler characteristic χ. Operator: integration. Anchor: ∫_M K dA = 2π χ(M); LHS analytic, RHS combinatorial. Generalised by Chern (1944) to all even-dimensional closed Riemannian manifolds.

**(i) Atiyah–Singer index theorem (1963).** Source: analytical index of an elliptic operator D on a compact manifold X. Target: topological index computed from K-theory / characteristic classes. Operator: ind(D) = ⟨ch(σ(D))·Td(TX_C), [TX]⟩. Anchor: equality of two integers; specialises to Hirzebruch–Riemann–Roch, signature theorem, Â-genus on spin manifolds.

**(j) Kontsevich–Soibelman / mirror symmetry.** Source: Gromov–Witten invariants of a Calabi–Yau X (symplectic side). Target: variations of Hodge structure / period integrals on the mirror X^∨ (complex side). Operator: A-model correlators ↔ B-model Yukawa couplings via mirror map. Anchor: Candelas–de la Ossa–Green–Parkes (1991) predicted the number of rational curves of degree d on the quintic threefold; counts at d ≤ 4 verified independently by Ellingsrud–Strømme and Kontsevich.

## 3. Operator-derived signature for each transport

To encode each as a calibration anchor, the tensor must store: **(i) the source-region operator** as a typed function with computable signature; **(ii) the target-region invariant** as an independently computable scalar/integer/distribution; **(iii) the bridge object** (modular form, L-group map, kernel, index class) as a third tensor node linking the two; **(iv) the empirical agreement record** — paired (input, source-output, target-output, residual) tuples sampled densely enough to falsify spurious bridges.

For continuous transports (Sato–Tate, Selberg, Katz–Sarnak): store the limiting measure plus a convergence-rate exponent. For discrete transports (modularity, Riemann–Roch, Atiyah–Singer, Gauss–Bonnet): store paired integer sequences with the difference operator and a verifier oracle. For categorical transports (Langlands, mirror symmetry): store the functor's action on a representative finite set of generating objects (e.g., Hecke eigensystems for Langlands; small-degree GW invariants for mirror symmetry).

Crucially, the signature must encode the *operator behaviour*, not the discipline label — per `feedback_verbs_over_nouns` and `feedback_domains_are_docstrings`. Each anchor becomes a (operator-type × residual-magnitude × verification-density) triple; F011 already lives in this schema.

## 4. Frontier candidates (transports suspected but not yet proven)

**Geometric Langlands (Beilinson–Drinfeld; Gaitsgory et al. 2024 announced proof).** Bridge: D-modules on Bun_G ↔ quasi-coherent sheaves on LocSys_{LG}. Anchor candidates: Hecke eigensheaf decomposition, Whittaker normalisation. Worth ingesting as a *partially confirmed* anchor with the Gaitsgory program's intermediate theorems as falsifiable checkpoints.

**p-adic Langlands.** Established for GL_2(Q_p) (Colmez, Kisin); open for GL_n(K) for n ≥ 3 or K ≠ Q_p. Anchor: (φ,Γ)-module ↔ p-adic Banach representation correspondence.

**Motivic conjectures (Beilinson, Bloch–Kato, Tate).** Target: special values of L-functions ↔ regulators in motivic cohomology. Anchor: rank predictions (BSD as the genus-1 case, verified to rank ≤ 4 numerically).

**Volume conjecture (Kashaev–Murakami).** Coloured Jones polynomial asymptotics ↔ hyperbolic volume of knot complement. Numerically supported, not proven.

## 5. Concrete next steps

Ingest these five first, in order, as the seed calibration anchor set:

1. **Modularity** (LMFDB-driven; densest verifier oracle, smallest residuals).
2. **Sato–Tate** (gives Prometheus a continuous-distribution anchor and ties directly into existing GUE/USp work).
3. **Katz–Sarnak** (already adjacent to F011; provides the function-field control comparison).
4. **Riemann–Roch** (cleanest discrete integer-equality anchor; trivial verifier).
5. **Monstrous moonshine** (highest-magnitude "absurd coincidence" anchor — calibrates the tensor's tolerance for surprising integer agreements).

Each ingest creates one tensor node per side + one bridge node + a paired-evaluation table. Defer Atiyah–Singer and mirror symmetry until the typed-operator action space (report 05) supports K-theory and derived categories.

## 6. References

1. Wiles, A. (1995). "Modular elliptic curves and Fermat's last theorem." *Ann. Math.* 141.
2. Khare, C. & Wintenberger, J.-P. (2009). "Serre's modularity conjecture I, II." *Invent. Math.* 178.
3. Arthur, J. (2013). *The Endoscopic Classification of Representations*. AMS Colloquium Pub. 61.
4. Cogdell, J., Kim, H., Piatetski-Shapiro, I., Shahidi, F. (2004). "Functoriality for the classical groups." *Publ. IHES* 99.
5. Barnet-Lamb, T., Geraghty, D., Harris, M., Taylor, R. (2011). "A family of Calabi–Yau varieties and potential automorphy II." *Publ. RIMS* 47.
6. Katz, N. & Sarnak, P. (1999). *Random Matrices, Frobenius Eigenvalues, and Monodromy*. AMS Colloquium Pub. 45.
7. Conrey, J. B. & Snaith, N. (2007). "Applications of the L-functions ratios conjectures." *Proc. London Math. Soc.* 94.
8. Conway, J. H. & Norton, S. P. (1979). "Monstrous moonshine." *Bull. London Math. Soc.* 11.
9. Borcherds, R. E. (1992). "Monstrous moonshine and monstrous Lie superalgebras." *Invent. Math.* 109.
10. Selberg, A. (1956). "Harmonic analysis and discontinuous groups in weakly symmetric Riemannian spaces." *J. Indian Math. Soc.* 20.
11. Hejhal, D. (1976, 1983). *The Selberg Trace Formula for PSL(2,R)*, Vols. I–II. Springer LNM.
12. Atiyah, M. F. & Singer, I. M. (1963, 1968). "The index of elliptic operators I–V." *Ann. Math.* 87, 93.
13. Hirzebruch, F. (1956). *Topological Methods in Algebraic Geometry*. Springer.
14. Candelas, P., de la Ossa, X., Green, P., Parkes, L. (1991). "A pair of Calabi–Yau manifolds as an exactly soluble superconformal theory." *Nucl. Phys. B* 359.
15. Kontsevich, M. & Soibelman, Y. (2001). "Homological mirror symmetry and torus fibrations." In *Symplectic Geometry and Mirror Symmetry*, World Scientific.
16. Colmez, P. (2010). "Représentations de GL_2(Q_p) et (φ,Γ)-modules." *Astérisque* 330.
17. Gaitsgory, D. et al. (2024). "Proof of the geometric Langlands conjecture" (preprint series, arXiv:2405–2410).
18. Kashaev, R. & Murakami, H. & J. (1997, 2001). "Volume conjecture" — *Mod. Phys. Lett. A* 10; *Acta Math.* 186.

Word count ~1180
