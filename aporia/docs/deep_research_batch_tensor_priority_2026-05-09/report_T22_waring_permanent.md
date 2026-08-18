# T#22 — Waring Rank of the Permanent

## Brief summary

T#22 asks for the exact Waring (symmetric) rank of perm_n viewed as a degree-n homogeneous form in n^2 variables. **Solved completely only for n=2 (R_W=4 trivially) and n=3 (R_W(perm_3)=16, Shitov 2021, SIAGA, matching prior upper bound).** For n>=4 only bounds exist: lower bounds via apolarity / catalecticants / syzygies (Shafiei 2015 — apolar ideal of perm_n is generated in degree 2; Boij-Teitler 2019 — cactus rank of perm_3 >= 14 via syzygies of apolar ideal); upper bounds inherited from polarization of Glynn's tensor-rank formula but no clean closed form. **No analogue of Houston-Goucher-Johnston 2024's Bell-number determinant formula exists for the permanent — this asymmetry is itself substrate-grade information.** Landsberg-Manivel-Ressayre 2013 prove a quadratic lower bound on dc̄(perm_n) >= n^2/2, which is determinantal-border-complexity, not Waring-rank-direct (PATTERN_RANK_PARITY_LEAK trap). Mulmuley-Sohoni GCT relevance: T#22 sits inside the T#92 (VP vs VNP) program. Maps to Tier-C `SecantVarietyEquation` with proposed `WaringRankWitness` companion.

## Flagged findings

1. **Substrate gap — `WaringRankWitness` subtype absent.** Tier-C `SecantVarietyEquation` (proposed in T#26 report) needs a symmetric-rank-specialized companion. Schema below.
2. **Sister-cluster coupling.** T#22 / T#86 / T#92 form a coupled GCT-permanent-rank evidence cluster.
3. **PATTERN_RANK_PARITY_LEAK is the primary trap** — six distinct invariants for perm_n (R, R̄, R_W, R̄_W, cR, dc, dc̄) are routinely conflated in casual writing.
4. **PATTERN_BASE_RATE_NEGLECT** — Generic Waring rank by Alexander-Hirschowitz is the baseline; for n=3, generic ≈ 19, perm_3 = 16, so symmetry only buys ~16% for n=3. For n=4, generic ≈ 243; whether perm_4 sits near generic or much lower is open.
5. **PATTERN_CONDUCTOR_CONFOUND** — The stabilizer (GL_n × GL_n) ⋊ Z/2 is the conductor on every published bound. Bounds proved without exploiting stabilizer-equivariance are massively weak.
6. **Asymmetry det vs perm.** Most Waring-rank-side progress concentrates on det_n; the permanent literature is markedly thinner. This *is* substrate-grade information about where the GCT toolkit has and hasn't acquired tools.
7. **Two candidate paradigm extensions:** "Apolar-quadric stabilizer-equivariant lower bound" (Shafiei / Boij-Teitler) and "Singular locus codim Waring lower bound" (Landsberg-Teitler 2009). Neither cleanly reduces to existing P29 or P31.

## 1. Problem statement

For n >= 2, perm_n(X) = sum over sigma in S_n of prod_i x_{i,sigma(i)} is a degree-n homogeneous form in N = n^2 variables. The Waring rank R_W(F) = min r such that F = sum_{i=1}^r lambda_i * ell_i^d for linear forms ell_i. Equivalently, [F] in sigma_r(nu_d(P^{N-1})). T#22: determine R_W(perm_n) for all n >= 4 (n <= 3 settled); equivalent asymptotic form: growth rate of R_W(perm_n).

## 2. Status & bounds

**Exact values:**
- n=1: R_W = 1 trivial.
- n=2: R_W = 4 (Sylvester / classical: 2x_{11}x_{22} + 2x_{12}x_{21}).
- **n=3: R_W(perm_3) = 16 (Shitov 2021, SIAGA 5(4)).** Lower bound 14 from Shafiei 2015 / Boij-Teitler 2019 cactus rank; Shitov closed to 16 via tailored apolarity.
- n >= 4: OPEN.

**Lower bound techniques:** catalecticant rank; apolarity / Ranestad-Schreyer; syzygies of apolar ideal (Boij-Teitler 2019); singularity-codim (Landsberg-Teitler 2009); Young flattenings (Landsberg-Ottaviani 2013); LMR 2013 (dc̄(perm_n) >= n^2/2 — note: this is determinantal-border-complexity, not Waring-rank-direct).

**Upper bound techniques:** direct symmetric expansion of n! monomials (R_W <= n! * 2^{n-1}); polarization of Glynn's R(perm_n) <= 2^{n-1}; Jelisiejew 2014 universal R_W(F) <= binom(n+d-2, d-1) - binom(n+d-6, d-3); generic AH baseline. **No Houston-Goucher-Johnston-style explicit Bell-number formula known for permanents** (HGJ 2024 is determinant-only; the alternating-sign structure of det is essential to the construction).

**Generic baseline (PATTERN_BASE_RATE_NEGLECT compliance):** R_W^{generic}(degree n in N=n^2 vars) ≈ binom(n^2+n-1, n)/n^2. n=3: ~19. n=4: ~243. n=5: ~1700. perm_n's "symmetry buy factor" = generic_baseline / R_W is the substrate-grade metric.

**Rank zoo for perm_n (PATTERN_RANK_PARITY_LEAK compliance):**
- R(perm_n) tensor rank: <= 2^{n-1} (Glynn); n=3 OPEN (~16-19).
- R_W(perm_n): n<=3 closed; n>=4 OPEN.
- cR(perm_n) cactus rank: n=3 >= 14 (Boij-Teitler); general n polynomial.
- R̄(perm_n), R̄_W(perm_n): mostly OPEN.
- dc(perm_n): conjectured exponential (Valiant); current best n^2/2 (Mignon-Ressayre, LMR).
- dc̄(perm_n): n^2/2 (LMR 2013); Valiant conjectures exponential.
- R_W^{sym}(perm_n) symmetry-respecting Waring rank: exponential lower bound (Landsberg-Ressayre 2017).

## 3. Literature

**Foundational:** Sylvester catalecticant; Aronhold invariant theory; Iarrobino-Kanev 1999 *Power Sums*; Ranestad-Schreyer 2011 (J. Algebra 346).

**Permanent-specific lower bounds:**
- Shafiei (arXiv:1212.0515, 2012/2015 J. Commut. Alg.) — apolar ideal of perm_n generated in degree 2.
- Shafiei (arXiv:1303.1860, 2013) — symmetric-matrix variant.
- Boij-Teitler (arXiv:1908.08896, 2019, J. Algebra 540) — cactus rank perm_3 >= 14 via syzygies; Waring rank det_3 >= 15.
- Jabbusch-Teitler (J. Algebraic Combin. 50(2)) — syzygies of apolar ideals of det/perm.
- **Shitov 2021 SIAGA 5(4)** — R_W(perm_3) = 16 (closes n=3).

**Singularity-based:** Landsberg-Teitler arXiv:0901.0487 (FoCM 2009) — codim(Sing(V(F))) lower bound; explicit for det, perm, monomials.

**GCT / determinantal complexity (LMR line):**
- Landsberg-Manivel-Ressayre arXiv:1004.4802 (Comment. Math. Helv. 88, 2013) — dc̄(perm_n) >= n^2/2.
- Landsberg-Ressayre arXiv:1508.05788 (2017) — exponential lower bound on dc(perm_n) under symmetry restriction.
- Mulmuley-Sohoni GCT I (SICOMP 2001) / GCT II (SICOMP 2008).
- Bürgisser-Ikenmeyer arXiv:1011.1350; STOC 2011/2013.
- Kumar (LIPIcs CCC 2021.4) — lower bound on determinantal complexity.

**Border Waring / debordering:**
- Dutta-Gesmundo-Ikenmeyer-Jindal-Lysikov arXiv:2401.07631 (STACS 2024) — fixed-parameter debordering.
- Dutta-Lysikov arXiv:2510.13049 (2025) — survey.
- Debordering+GCT for Waring rank arXiv:2211.07055.

**Determinant-side recent (no permanent analogue):** Houston-Goucher-Johnston arXiv:2301.06586 (Combin. Probab. Comput. 2024) — R_W(det_n) <= 2^{n-1} B_n. Bremner-Hu arXiv:2004.06158. Krishna-Makam (emis 2017).

**General upper bounds:** Jelisiejew arXiv:1305.6957 (Arch. Math. 2014).

**Recent (2023-2025):** Brešar et al. (Bull. London Math. Soc. 2023); Pacific J. Math. 334(1) (2025); Algebraic Cost of Boolean Sum arXiv:2502.02442.

**Tools:** Macaulay2 (`Apolarity`, `PowerSums`, `SecantVarieties`); Bertini, HomotopyContinuation.jl; Singular; LiE / Symmetrica; TensorLy.

## 4. Attack vectors

**P29 Border apolarity (primary lower-bound).** Compute Ann(perm_n) ⊂ C[∂_{i,j}]; A = C[∂]/Ann(perm_n) is graded Artinian Gorenstein, socle degree n. R_W bounded below by Hilbert-function constraints, count of degree-2 generators (Shafiei 2015), Ranestad-Schreyer.

**P31 Symmetric flattening / catalecticant.** Cat_k(perm_n) has S_n-equivariant kernel; Schur-functor decomposition gives polynomial-in-n lower bounds, generally loose.

**Singularity codim (Landsberg-Teitler).** R_W(F) >= codim(Sing(V(F))); for perm_n, Sing(V(perm_n)) determined by simultaneous vanishing of all (n-1)x(n-1) sub-permanents.

**Symmetry-restricted bound (Landsberg-Ressayre 2017).** Stabilizer-respecting decompositions give exponential lower bound on R_W^{sym}, geometrically informative even when not bounding R_W directly.

**Young flattenings (Landsberg-Ottaviani 2013).** Border-rank lower bounds via Koszul-Young flattenings; for perm_n yields symmetric border rank bounds.

**P09 Computer-algebra.** Macaulay2 + Apolarity for n <= 4 tractable; n=5 borderline; n>=6 explodes (binom(n^2+n-1, n) monomials in degree n).

**P25 Kill-as-product.** Failed candidate decompositions encode the structural obstruction; this is how Shitov's 2021 lower bound was constructed (ruling out length-15).

**Sister attacks:** T#86 (R(perm_n) <= 2^{n-1} via Glynn); T#92 (GCT separation lifts to rank-zoo statements); T#21 (A-H stratification refines generic baseline); T#23 (Strassen-additivity for forms; if true, gives orbit-decomposition arithmetic for perm_n).

## 5. Substrate encoding

Tier-C `SecantVarietyEquation` (primary) + proposed `WaringRankWitness` companion.

```
WaringRankWitness {
  form_descriptor: {
    form_family:           {PERMANENT, DETERMINANT, MONOMIAL, GENERIC_FORM,
                            POWER_SUM, ELEMENTARY_SYMMETRIC, GENERIC_INVARIANT}
    n_or_degree:           Integer
    ambient_dim_N:         Integer
    field, characteristic: ...
  }
  rank_invariant_kind:     {WARING_RANK, SYMMETRIC_BORDER_RANK, CACTUS_RANK,
                            GENERIC_RANK, SYMMETRY_RESPECTING_WARING_RANK,
                            DETERMINANTAL_COMPLEXITY, DETERMINANTAL_BORDER_COMPLEXITY}
  status:                  {EXACT, LOWER_BOUND_ONLY, UPPER_BOUND_ONLY, INTERVAL,
                            OPEN, OPEN_AT_THIS_PRECISION}
  exact_value, lower_bound, upper_bound:  optional<Integer>
  generic_baseline:        Integer       // MANDATORY (PATTERN_BASE_RATE_NEGLECT gate)
  symmetry_buy_factor:     Float
  witness_type:            {EXPLICIT_DECOMPOSITION, APOLAR_QUADRIC_COUNT,
                            SYZYGY_BASED, CATALECTICANT_RANK, SINGULARITY_CODIM,
                            YOUNG_FLATTENING, COMPUTER_ALGEBRA_CERTIFIED,
                            SHITOV_TAILORED_APOLARITY, BELL_NUMBER_FORMULA, UNRESOLVED}
  apolar_witness:          optional<{annihilator_ideal, apolar_algebra_dim,
                                     socle_degree, quadric_generator_count,
                                     hilbert_function, is_quadric_generated,
                                     schur_decomposition}>
  decomposition_witness:   optional<{linear_forms, coefficients, rank,
                                     numerical_residual, precision_floor,
                                     verification_certificate}>
  catalecticant_witness, singularity_witness, young_flattening_witness: optional
  stabilizer:              {group_description, is_decomposition_stabilizer_respecting,
                            sym_restricted_bound}
  cross_invariant_links:   {related_R, related_Rbar, related_RW_bar,
                            related_cR, related_dc_bar}    // PATTERN_RANK_PARITY_LEAK
  references, canonical_attribution: ...
}
```

**Composition:** `WaringRankWitness` is the symmetric specialization of `BorderRankWitness` (T#34). Apolar witness consumes `DefectivityCertificate.fat_point_witness` (T#26). For perm_n with `rank_invariant_kind == DETERMINANTAL_BORDER_COMPLEXITY` it is the substrate-side handle for T#92.

**Tickets proposed:**
- `T-ST-T22-001` WaringRankWitness probe — perm_n n=2,3 reproducibility; n>=4 honest-interval (Learner must NOT fake exact values).
- `T-ST-T22-002` RankInvariantConsistency probe — enforce R_W >= cR >= R̄_W chain compliance.
- `T-ST-T22-003` GenericBaselineMandate probe — empty `generic_baseline` field is automatic FAIL (PATTERN_BASE_RATE_NEGLECT gate).

## 6. Calibration anchor notes

**Substrate-grade response must:**
- Distinguish R, R̄, R_W, R̄_W, cR, dc, dc̄ explicitly.
- Cite Shitov 2021 = 16 for perm_3 with prior history (14-18).
- Cite Shafiei 2015 for "apolar ideal of perm_n generated in degree 2."
- Cite Boij-Teitler 2019 for cR(perm_3) >= 14.
- Cite LMR 2013 dc̄(perm_n) >= n^2/2 (NOT as Waring rank bound).
- Acknowledge no exact R_W known for n >= 4; no HGJ-style permanent upper-bound formula.
- Record generic AH baseline so symmetry-buy is measurable.
- Acknowledge det vs perm asymmetry as substrate information.

**Textbook-trivial / Learner FAIL responses:**
- "Waring rank of perm_n is exactly known." (only n <= 3)
- "Mulmuley-Sohoni proved R_W(perm_n) >= n^2/2." (it's LMR's dc̄ bound)
- "Glynn's formula gives R_W(perm_n) <= 2^{n-1}." (Glynn is tensor rank, not Waring)
- "Houston-Goucher-Johnston gives R_W(perm_n) <= 2^{n-1} B_n." (HGJ is det-only)
- "Boij-Teitler proved R_W(perm_3) >= 14." (they proved CACTUS rank >= 14)
- "Shitov proved R_W(perm_n) = 16." (only n=3)

**Pattern citations:** PATTERN_RANK_PARITY_LEAK (primary — six distinct invariants); PATTERN_BASE_RATE_NEGLECT (generic baseline must be recorded); PATTERN_CONDUCTOR_CONFOUND (stabilizer is the conductor).

**Canonical attribution at risk:** Landsberg, Manivel, Ressayre, Mulmuley, Sohoni, Bürgisser, Ikenmeyer, Teitler, Shitov, Boij, Shafiei, Iarrobino, Ranestad, Schreyer, Jelisiejew. Common fabrications: (a) attributing n=3 closure to Boij-Teitler instead of Shitov; (b) attributing apolar-degree-2 generation to Boij-Teitler instead of Shafiei (BT used it; Shafiei proved it); (c) collapsing three distinct LMR-style papers into one citation; (d) inventing nonexistent HGJ-permanent bound; (e) using Glynn's formula for Waring rather than tensor rank.

## 7. Cross-references

**Within `tensor_open_problems_v1.md`:** #21 (UPSTREAM, generic baseline via A-H), #23 (STRONGLY COUPLED, Strassen additivity gives orbit-decomposition arithmetic), #26 (parent secant-variety framework), #28 (Terracini loci), #34 (sister `BorderRankWitness`), #39 (maximal Waring rank), #40 (identifiability — low R_W means non-identifiable), #43 (ill-posedness), #56 (NP-hardness), **#86 SISTER (tensor rank det/perm)**, **#92 SISTER (GCT VP vs VNP)**, #93 (orbit closure containment), #95-99 (Kronecker / plethysm / Foulkes / Saxl — rep-theoretic engines).

**Within `attack_angle_taxonomy.md`:** P31 (primary), P29 (dual), P02 (cohomological), P15 (parent), P09 (computation), P25 (kill-as-product). New paradigm candidates: "Apolar-quadric stabilizer-equivariant lower bound" (Shafiei / Boij-Teitler); "Singular-locus codim Waring lower bound" (Landsberg-Teitler).

**Prior reports in batch:** T#1, T#26 (parent — `DefectivityCertificate` is the parent class of `WaringRankWitness`), T#28, T#34 (sister Tier-B), T#43, T#56, T#73, T#79, T#84, T#85, T#95.

**Forward dependency Techne T038:** T#22 is THE permanent-side calibration anchor for `SecantVarietyEquation`. `WaringRankWitness` should land in the same contract-change window as `BorderRankWitness`, `DefectivityCertificate`, `LimitWitness`. Without it the substrate cannot honestly distinguish "R_W(perm_3) = 16 (Shitov, exact, Waring)" from "cR(perm_3) >= 14 (Boij-Teitler, lower, cactus)" from "dc̄(perm_n) >= n^2/2 (LMR, lower, determinantal-border-complexity)" — three true canonical statements that a Learner will collapse without this primitive.

**Sources:**
- [arXiv:1004.4802 — LMR 2013](https://arxiv.org/abs/1004.4802)
- [arXiv:1212.0515 — Shafiei 2015](https://arxiv.org/abs/1212.0515)
- [arXiv:1908.08896 — Boij-Teitler 2019](https://arxiv.org/abs/1908.08896)
- [arXiv:1508.05788 — Landsberg-Ressayre 2017](https://arxiv.org/abs/1508.05788)
- [arXiv:0901.0487 — Landsberg-Teitler 2009](https://arxiv.org/abs/0901.0487)
- [arXiv:1305.6957 — Jelisiejew 2014](https://arxiv.org/abs/1305.6957)
- [arXiv:2301.06586 — Houston-Goucher-Johnston 2024](https://arxiv.org/abs/2301.06586)
- [arXiv:2401.07631 — Dutta-Gesmundo-Ikenmeyer-Jindal-Lysikov 2024](https://arxiv.org/abs/2401.07631)
- [arXiv:2510.13049 — Dutta-Lysikov 2025](https://arxiv.org/abs/2510.13049)
- [arXiv:2211.07055 — Debordering+GCT for Waring](https://arxiv.org/abs/2211.07055)
- [arXiv:2004.06158 — Bremner-Hu 2020](https://arxiv.org/abs/2004.06158)
- [arXiv:1011.1350 — Bürgisser-Ikenmeyer 2010](https://arxiv.org/abs/1011.1350)
- [SIAGA 2021 — Shitov, 3x3 permanent](https://epubs.siam.org/doi/abs/10.1137/20M1349254)
- [SICOMP 2001 — Mulmuley-Sohoni GCT I](https://epubs.siam.org/doi/10.1137/S009753970038715X)
- [Cambridge 2024 — HGJ determinant formula](https://www.cambridge.org/core/journals/combinatorics-probability-and-computing/article/new-formula-for-the-determinant-and-bounds-on-its-tensor-and-waring-ranks/E33F5E0726A0691B250C3BB6CE3816F5)
- [STACS 2024 — Fixed-parameter debordering](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.STACS.2024.30)
- [LIPIcs CCC 2021.4 — Kumar determinantal complexity](https://drops.dagstuhl.de/storage/00lipics/lipics-vol200-ccc2021/LIPIcs.CCC.2021.4/LIPIcs.CCC.2021.4.pdf)
- [PJM 2025 — Tensor rank computation](https://msp.org/pjm/2025/334-1/pjm-v334-n1-p06-s.pdf)
