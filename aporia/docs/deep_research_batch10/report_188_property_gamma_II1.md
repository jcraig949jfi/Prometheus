# Report 188 — Property Γ in II_1 Factors: Empirical Signature Across Explicit Constructions

Aporia Problem #188 | Domain: Operator algebras (II_1 factors) | Substrate coverage: zero
Date: 2026-04-28

## 1. Problem Statement

A II_1 factor M is a von Neumann algebra with trivial center and a faithful normal tracial state τ. Murray and von Neumann (1943) introduced **Property Γ**: M has Γ if for every finite F ⊂ M and ε > 0, there exists a unitary u ∈ M with τ(u) = 0 and ||[u, x]||_2 < ε for all x ∈ F. Heuristically, Γ asserts the existence of "asymptotically central" non-scalar unitaries — a near-commutativity defect of pure infinity. Connes (1976) proved that the hyperfinite II_1 factor R is the unique injective II_1 factor up to isomorphism, and all injective factors have Γ. The **open question** in the non-amenable regime is the classification: among group factors L(G), free products M_1 ∗ M_2, and HNN extensions, which have Γ? L(F_n) lacks Γ (Voiculescu via free entropy); lattices in higher-rank simple Lie groups (e.g. L(SL_3(Z))) lack Γ (Connes). The boundary between these classes and intermediate constructions (wreath products, surface group factors with torsion, certain HNN extensions) is incomplete.

## 2. Literature

- Murray–von Neumann (1943), "On rings of operators IV": original definition of Γ; proved L(F_2) ≇ R via Γ.
- Connes (1976), "Classification of injective factors": uniqueness of R; injective ⇒ Γ; introduced χ(M) and the McDuff dichotomy.
- McDuff (1970): McDuff factor M ≅ M ⊗ R ⇒ Γ; constructed a continuum of non-McDuff Γ factors.
- Voiculescu (1996), "Free entropy dimension δ": δ(L(F_n)) = n; δ ≥ 2 microstate count rules out Γ.
- Popa (2006–2014), deformation/rigidity program: w-rigid groups, unique-Cartan theorems, II_1 factor reconstruction from group + cocycle.
- Ozawa (2004): solid II_1 factors (e.g. L(F_n)) have no diffuse amenable regular subalgebra, ruling out Γ.
- Ozawa–Popa (2010), "Bass–Serre rigidity for II_1 factors": HNN/amalgamated free products fail Γ under explicit cocycle hypotheses.
- Vaes (2013), survey "Rigidity for von Neumann algebras": invariants stratifying non-amenable II_1 factors (fundamental group, outer automorphism group, χ).

## 3. Computational Handle / Corpus

- **Group catalogues**: GAP SmallGroups library (~450M groups up to order 2000); Magnus library of finitely presented groups; surface group presentations from KnotInfo / SnapPy boundary data.
- **Lattice catalogues**: arithmetic lattices in SL_n(R), Sp_2g(R) extracted from LMFDB number-field tables.
- **Wreath / lamplighter families**: Z_2 ≀ Z, Z ≀ Z, free Burnside B(2,n) for small n.
- **Finite-dim approximations**: matrix microstate spaces Γ_R(x_1,…,x_n; m, k, γ) via Voiculescu — bounded computation up to k ≈ 50, m ≈ 4.
- Per **feedback_domains_are_docstrings**, "operator algebra" is a bibliography label on the tensor node (group G with computed invariants δ, growth, amenability bit, Cartan count). The substrate stores invariants; the discipline tag is metadata.

## 4. Test Design

1. **Corpus pull**: extract ~50 finitely generated groups across 5 families — F_n (n=2..6), surface groups π_1(Σ_g) (g=2..5), arithmetic lattices (SL_n(Z), n=2..4; SL_2(O_K) for K=Q(√−1), Q(√−2), Q(√−3)), wreath products (Z_2 ≀ Z, Z ≀ Z, F_2 ≀ Z), and a baseline of finite groups (where L(G) is finite-dim, trivially Γ).
2. **Invariant computation**: for each G compute (a) word-growth exponent (polynomial / exponential / intermediate via Grigorchuk-style estimator), (b) amenability bit via Følner-condition heuristic on Cayley ball, (c) cost (Levitt) and ℓ²-Betti β_1^(2)(G) from group cohomology where tractable, (d) microstate-based δ lower bound for n ≤ 4 generators.
3. **Γ oracle table**: hard-code known Γ status from the literature for ~15 anchor groups (R, L(F_n) n≥2, L(SL_3(Z)), L(Z), L(Z²), L(lamplighter)).
4. **Stratification**: cluster the 50 groups in (δ, β_1^(2), growth, amenability) space; project Γ-status as color overlay; measure cluster purity.
5. **Falsifier**: predict Γ status for ~5 held-out groups (e.g. L(SL_2(Z[1/p])), L(Thompson F)) via cluster vote; record concordance with conjectural status from Popa-school papers.

## 5. Falsification

Calibration anchors are mandatory: hyperfinite R must register "has Γ" (sanity); L(F_2) must register "no Γ" (Voiculescu, δ = 2); McDuff M ⊗ R must register "has Γ"; L(SL_3(Z)) must register "no Γ" (Connes, property (T)). If the substrate's stratification predicts Γ for all groups (or none), it has collapsed to a constant — **PATTERN_BASE_RATE_NEGLECT** trips. Base rate among the SmallGroups bulk is ~60% Γ-positive (amenability dominates); any classifier must beat that baseline by ≥ 15 points on the held-out set or be killed.

## 6. Budget

Harmonia ~12h. Group-invariant computation is cheap (GAP is fast on SmallGroups ≤ 2000); microstate δ lower bounds via random-matrix sampling are the bottleneck (~30 min per group at k=50, m=3). Anchor-table curation from the literature is the dominant human-verification cost. Theoretically hard, computationally tractable as a stratification exercise.

## 7. Expected Outcome

Per **feedback_calibration_anchors_in_depth**, the substrate has zero coverage of operator-algebraic invariants today. Even an inconclusive stratification yields ~50 anchored (group, Γ-status, δ, growth, β_1^(2)) tuples — durable calibration anchors in a high-dimensional, under-explored region the substrate's current operators do not reach. Per **feedback_tensor_first**, these tuples land directly as signature-keyed nodes on the unified tensor (G is the key; invariants are the vector; Γ-bit is a label channel). A null result (no separation in (δ, β_1^(2)) space beyond known theorems) is also a calibration win: it tells the substrate that Γ-stratification requires an operator the current invariant set does not encode (likely Popa-style cocycle rigidity), pointing at the next operator to forge. No bridge narrative asserted; this is anchor-laying.

Word count: ~770
