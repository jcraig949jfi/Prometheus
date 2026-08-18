# Report T#43 — Existence of Best Rank-r Tensor Approximations

**Catalog entry:** `aporia/mathematics/tensor_open_problems_v1.md` §VI #43
**Source dispatch:** `aporia/docs/gemini_tensor_priority_dispatch_2026-05-09.md` (Tier 1, fire-3)
**Author:** Aporia (deep-research)
**Date:** 2026-05-09
**Doctrine:** HARD-1, HARD-2, HARD-5, HARD-6
**Patterns cited:** PATTERN_VRAM_TRUNCATION_ARTIFACT, PATTERN_BASE_RATE_NEGLECT, PATTERN_RANK_PARITY_LEAK
**Tags:** P15 (tensor decomposition), P29 (border apolarity), P30 (tensor networks), P31 (secant variety geometry)

---

## Brief summary

T#43 is the foundational ill-posedness result for numerical CP tensor decomposition: for tensors of order ≥ 3 and target rank r ≥ 2, the set S_r of tensors of CP rank ≤ r is **not topologically closed**, so the best-rank-r approximation problem may have no minimizer (de Silva–Lim 2008). The phenomenon is structural, not numerical — it survives every norm and every algorithm, and manifests empirically as the "diverging components" / "swamp" / "PARAFAC degeneracy" failure modes. Stable substitutes exist: border-rank closure σ_r(Seg) (P31), Tucker / multilinear rank (Hackbusch), hierarchical Tucker, and TT (Hackbusch–Kühn, Oseledets) — all give closed parameter sets where best approximation is well-posed. The **right theoretical replacement** is P29 border apolarity (Buczyńska–Buczyński); the **right computational replacement** is P30 tensor networks. The substrate's existing primitive set does not encode "open vs closed" parameter-set status, so a `LimitWitness` subtype of the Tier-B `ConstructiveExistenceWitness` meta-primitive is required to prevent the substrate from silently fabricating "best rank-r approximations" on ill-posed instances.

## Flagged findings

1. **Substrate gap (substantive):** No current substrate primitive distinguishes open S_r (CP rank, order ≥ 3) from closed S_r (Tucker / TT / σ_r). A naïve "best rank-r approximation" call on order-3 tensors can return a near-optimal point on a diverging-norm trajectory whose limit has rank > r. **Proposed ticket:** `T-ST-T43-001` LimitWitness probe under Tier-B `ConstructiveExistenceWitness`.

2. **PATTERN_VRAM_TRUNCATION_ARTIFACT alignment:** Float-precision truncation actively masks the structural ill-posedness — ALS halts when diverging components hit float ceilings, which looks like convergence. Substrate must check factor-norm divergence as a separate signal from residual stationarity.

3. **PATTERN_BASE_RATE_NEGLECT trap:** The ill-posed set is measure-zero in many measures but topologically dense — every neighborhood of every rank-r tensor contains both well-posed and ill-posed instances. Statistical-CP framings (Han 2025) hide this density behind base-rate language.

4. **Rank-zoo confusion (FM-08 anchor + PATTERN_RANK_PARITY_LEAK):** Ill-posedness applies ONLY to CP rank. Border rank, multilinear rank, TT rank, hierarchical Tucker rank are all CLOSED. Symmetric rank IS open (Comon–Lim–Mourrain). Cactus rank is scheme-theoretic. A Learner that conflates any two of these fails calibration.

5. **Calibration signature:** Substrate-grade response asserts the obstruction is **inherent to the tensor space** and names stable substitutes; textbook-trivial response says "use regularization" or "ALS sometimes fails — restart." de Silva–Lim's contribution is precisely that the failure survives every norm and Brègman divergence — it is topological, not numerical.

6. **Canonical attribution at risk:** de Silva, Lim (2008 SIAM JMAA 30:1084–1127, DOI 10.1137/06066518X, arXiv:math/0607647) is the citation; Hackbusch *Tensor Spaces and Numerical Tensor Calculus* (Springer SCM 42, 2012/2019) is the canonical text for stable substitutes; Comon–Golub–Lim–Mourrain 2008 SIAM JMAA 30:1254–1279 for the symmetric case; Stegeman 2013 for the diverging-components-nearly-proportional theorem; Kolda 2001 SIAM JMAA for orthogonal-decomposition Eckart–Young counterexample.

## Full report content

### 1. Problem statement

For tensors of order ≥ 3 and target rank r ≥ 2, the optimization

> minimize ‖T − T̂‖ subject to rank_CP(T̂) ≤ r

is **not well-posed in general**: the infimum may not be attained.

Concretely (de Silva & Lim 2008):

- The set S_r := { T : rank_CP(T) ≤ r } is **not topologically closed** for r ≥ 2 in any tensor space of order ≥ 3.
- There exist sequences T_n ∈ S_r whose CP rank-1 components diverge in norm (cancelling pairs blowing up to ±∞) while T_n → T* with rank_CP(T*) > r.
- Equivalently: clos(S_r) = σ_r(Seg) (the r-th secant variety of the Segre variety = border-rank-r set).
- The failure is **norm-independent** (any reasonable norm or Brègman divergence) and **not a numerical artifact**.

This is exactly the "diverging components" / "swamp" / PARAFAC degeneracy empirically observed since the 1970s; de Silva–Lim closed the loop by exhibiting the obstruction as structural.

### 2. Status & bounds

**Unconditional results:**

| Result | Authors | Year |
|---|---|---|
| Non-closure of S_r for r ≥ 2 in order ≥ 3 | de Silva–Lim | 2008 |
| Diverging-components nearly-proportional | Krijnen–Dijkstra–Stegeman; Stegeman | 2008–13 |
| Symmetric S_r,sym non-closed for r ≥ 2 | Comon–Golub–Lim–Mourrain | 2008 |
| **Border-rank set σ_r(Seg) is closed** | Bini; Landsberg | 1980, 2012 |
| **Tucker / multilinear-rank set is closed** | de Lathauwer–De Moor–Vandewalle; Hackbusch | 2000, 2012 |
| **HT / TT-rank sets are closed** | Hackbusch–Kühn; Oseledets | 2009, 2011 |
| Rank-1 set is closed | folk / De Lathauwer | — |
| Odeco tensors: SVD-like decomposition exists | Kolda; Robeva | 2001, 2016 |
| PD tensors: best rank-r exists under conditions | Qi–Comon–Lim; Yang | 2010s–2022 |

**Conditional / regularization-based existence** (changes the problem):
1. Bounded-norm constraint ‖a_i^(k)‖ ≤ B
2. Non-negativity (PARAFAC-NN)
3. Bounded inner-product |⟨a_i, a_j⟩| ≤ 1−ε
4. Mode-orthogonality
5. Tucker compression with fixed multilinear rank

**Open subproblems active 2024–2026:**
- Sharp measure-theoretic characterization of the ill-posed set (μ for natural ensembles).
- Tightness of regularization gap vs border-rank infimum.
- Yang et al. 2022 (10.1137/22M1494178) extends well-posedness to PD tensors.
- Han et al. 2025 (arXiv:2505.23046) statistical-CP optimality.

### 3. Literature

**Canonical (calibration anchors per HARD-4):**
- de Silva, V. & Lim, L.-H. (2008). "Tensor rank and the ill-posedness of the best low-rank approximation problem." SIAM J. Matrix Anal. Appl. 30(3):1084–1127. DOI 10.1137/06066518X. arXiv:math/0607647. **THE foundational paper.**
- Hackbusch, W. (2012, 2nd ed. 2019). *Tensor Spaces and Numerical Tensor Calculus.* Springer SCM 42. **Canonical text** for HT / Tucker stable substitutes; Theorem 8.6 (best multilinear-rank approximation always exists).
- Comon, P., Golub, G., Lim, L.-H., Mourrain, B. (2008). "Symmetric tensors and symmetric tensor rank." SIAM JMAA 30(3):1254–1279.
- Kolda, T. G. (2001, 2003). "Orthogonal tensor decompositions." SIAM JMAA 23(1) and counterexamples paper — explicit Eckart–Young counterexample.
- Kolda & Bader (2009). "Tensor decompositions and applications." SIAM Review 51(3):455–500. Standard survey; §3.3 covers ill-posedness.
- Landsberg, J. M. (2012). *Tensors: Geometry and Applications.* AMS GSM 128. Border rank, secant varieties.
- Krijnen, Dijkstra, Stegeman (2008). Psychometrika 73:431–439. Non-existence and degeneracy in CANDECOMP/PARAFAC.
- Stegeman series (2006–2013) on diverging-components-nearly-proportional theorem.

**Recent stability work (2020s):**
- Evert et al. 2022 (10.1137/22M1494178) PD tensor approximation.
- Yang 2024 TASD (Tucker-based Approximation with Simultaneous Diagonalization).
- Han et al. 2025 arXiv:2505.23046 statistical CP.
- arXiv:2402.02890 black-box HT decomposition.

**Software (per HARD-6):**
- TensorLy: `decomposition.parafac`, `constrained_parafac` (AO-ADMM, since v0.7), `non_negative_parafac`, `tucker` (always well-posed).
- TT-Toolbox (Oseledets), T3F, ITensor, TenPy.
- Macaulay2 SecantVarieties / Apolarity (P29, P31).
- htucker (MATLAB, Kressner–Tobler).

### 4. Attack vectors

**4.1 Bypass routes (practitioner):**
1. Border-rank closure (P31, P29) — replace S_r with σ_r(Seg). Always well-posed; computational cost is the σ_r equations (Salmon problem partial).
2. Format change (P30) — Tucker / HT / TT. HOSVD is √d-quasi-optimal: ‖T − HOSVD_r(T)‖ ≤ √d · ‖T − T*_r‖.
3. Regularization (textbook-trivial) — bounded-norm, L1/L2, non-negativity. TensorLy `constrained_parafac` AO-ADMM.
4. Special-class restriction — odeco (Robeva), PD (Yang), Kruskal-identifiable.

**4.2 P29 border apolarity = the "right" theoretical framework:**
- Apolarity (Macaulay's inverse system) — symmetric F has border rank ≤ r iff there's a saturated apolar 0-d Gorenstein scheme of length r in F^⊥.
- B-invariant ideal enumeration (Buczyńska–Buczyński–Galązka) for minimal-border-rank tensors.
- Hilbert-function bookkeeping (Landsberg–Michałek R̲(M⟨3⟩) ≥ 17).

Substrate-friendly because witnesses are CONSTRUCTIVE (specific schemes, auditable by substrate-tester); pairs with TriangulationProtocol.

**4.3 P30 tensor networks = preferred substrate representation:**
For HARD-3's unified-tensor build, TT / HT / MPS / PEPS are the natural representation precisely because rank-bounded approximation is well-posed. TensorNetwork primitive in CoordinateChart system.

**4.4 New attack patterns surfaced:**
- Yang 2024 TASD is a hybrid P15+P30 (sub-paradigm note worth filing).
- Statistical-CP (Han 2025) is conditional on a generative model — a P15 + concentration-of-measure hybrid that reframes existence as statistical-event probability rather than topological closure. **This is exactly the trap PATTERN_BASE_RATE_NEGLECT warns against:** the ill-posed set is measure-zero but topologically dense, so statistical framing makes the failure look benign while hiding its density.

### 5. Substrate encoding

**Current gap:** Substrate primitives don't distinguish open S_r (CP, order ≥ 3) from closed S_r (Tucker / TT / σ_r). Every primitive operating on tensors implicitly assumes a closed parameter set. On unwitnessed-open S_r, this assumption silently degrades.

**Required primitive (Tier-B `ConstructiveExistenceWitness` → `LimitWitness` subtype):**

```
LimitWitness {
  set_S: TensorParameterSet           // e.g. S_r CP-rank-r tensors
  ambient: TensorAmbientSpace         // R^{n1×...×nd} with norm
  closure_status: {OPEN, CLOSED, UNKNOWN}
  closure_witness: optional<{
    witness_type: {DIVERGING_SEQUENCE, BORDER_RANK_LIMIT, TANGENT_POINT}
    sequence: optional<Iterator<TensorObject>>
    limit: TensorObject
    rank_at_limit: Integer
  }>
  stable_substitute: optional<TensorParameterSet>  // σ_r(Seg) or Tucker-r
  substitute_proof: optional<ApolarSchemeWitness | TuckerSVDWitness>
}
```

A naïve substrate "best rank-r approximation" call on order-3 tensors must EITHER (a) decline with `UNKNOWN` and a CapabilityGapTicket, or (b) return a `LimitWitness` with `closure_status = OPEN` and a `stable_substitute` that was actually used.

**Coordinate-chart hint (per `feedback_substrate_v2_lockins` lock-in #2):** the SAME tensor registers different CoordinateCharts depending on encoding (CP vs Tucker vs TT cores). Closure status is a property of the chart, not the tensor — clean instance of the chart-dependence the lock-in anticipated.

**Capability-gap tickets:**
- `T-ST-fire41-001` (Border-rank variety membership) — direct support.
- `T-ST-fire41-002` ConstructiveExistenceWitness root flag — direct support.
- **Proposed new:** `T-ST-T43-001` LimitWitness probe — substrate-tester should fail any "best rank-r approximation" claim on order ≥ 3, r ≥ 2 lacking LimitWitness or stable-substitute proof.

### 6. Calibration anchor notes

**Substrate-grade response:**
- States S_r is **not closed** for r ≥ 2 in order ≥ 3 (de Silva–Lim 2008).
- States obstruction is **inherent to the tensor space**, not a numerical artifact.
- Names stable substitutes: σ_r(Seg) (P31), Tucker (Hackbusch), HT/TT (Hackbusch–Kühn, Oseledets).
- Distinguishes structural (closure) from algorithmic (ALS swamping), notes the latter is the empirical face of the former.
- Notes diverging-components-nearly-proportional theorem (Stegeman) as operational fingerprint.
- Acknowledges symmetric case (Comon–Lim–Mourrain).
- Cites de Silva, Lim, Hackbusch, Comon, Landsberg, Kolda properly.

**Textbook-trivial response (FAIL signal):**
- "Use regularization." (Bypasses the structural question.)
- "Just use Tucker / HOSVD." (Right substitute, wrong reasoning — must state WHY: multilinear-rank set is closed.)
- "ALS sometimes fails — restart." (Confuses algorithmic stall with structural ill-posedness.)
- "This is a numerical issue." (FALSE per de Silva–Lim — obstruction survives every norm.)

**Trivial-vs-open within the rank-zoo (FM-08 + PATTERN_RANK_PARITY_LEAK):**
- Rank → **OPEN** (S_r not closed)
- Border rank → CLOSED (σ_r is a variety)
- Multilinear rank → CLOSED (Hackbusch)
- Symmetric rank → OPEN (S_r,sym not closed for r ≥ 2)
- Symmetric border rank → CLOSED
- Cactus rank → scheme-theoretic, neither rank nor border rank
- Slice/partition/analytic/geometric rank → different problems entirely (P27)

T#43 is specifically about CP rank; the ill-posedness does NOT carry to multilinear or border rank.

**Pattern citations:**
- **PATTERN_VRAM_TRUNCATION_ARTIFACT.** 32-bit-float ALS halts on ill-posed instances because diverging-component magnitudes hit float ceilings — not because the infimum was attained. Substrate must check factor-norm divergence as a separate signal.
- **PATTERN_BASE_RATE_NEGLECT.** Ill-posed set is measure-zero in some measures but topologically DENSE (every rank-r tensor on the boundary has nearby tensors with no best rank-r approximation). For structured tensors (physics, representation theory), the ill-posed set may be the relevant one. Reporting only "almost surely fine" is the misuse.
- **PATTERN_RANK_PARITY_LEAK.** The rank-zoo word-collision is the clearest exemplar in tensor mathematics. T#43 is a leakage test.

**HARD-5 (domains-as-docstrings) note:** CP-rank set non-closure is a structural property of the tensor space's secant geometry — equally indexable as algebraic geometry, real analysis, numerical analysis, engineering. All four domain labels are docstrings on the same node; the substrate should index by operator signature (Segre embedding fails to be proper on rank-r locus) rather than discipline.

### 7. Cross-references

**Within `tensor_open_problems_v1.md`:** #19 (cactus rank), #20 (border Comon's), #26 (defective Segre-Veronese), #34 (border-rank variety membership), #44 (tensor nuclear norm), #45 (ALS convergence), #47 (Gauss-Newton basins), #50 (Tucker compression), #51 (Hackbusch HT conjectures).

**Within `attack_angle_taxonomy.md`:** P15 (parent paradigm whose naïve form T#43 declares ill-posed); P29 (right theoretical replacement — border apolarity); P30 (right computational replacement — tensor networks); P31 (right geometric replacement — secant variety closure).

**Substrate-tester capability-gap tickets:** `T-ST-fire41-001`, `T-ST-fire41-002`, `T-ST-fire42-002`, `T-ST-fire43-002`, `T-ST-fire44-002`, `T-ST-fire45-002`; **proposed new** `T-ST-T43-001` LimitWitness probe.

**Forward links:** Feeds `aporia/docs/tensor_priority_synthesis_2026-05-09.md` (forthcoming). Direct dependency for **Techne T038 classification** — T#43 specifies the LimitWitness subtype any tensor-decomposition Techne component must register. Pairs with **T#28** (asymptotic spectrum) — T#28 organizes the rank-zoo at large; T#43 is the concrete numerical-side instance motivating ConstructiveExistenceWitness machinery.

---

*Aporia, 2026-05-09*
