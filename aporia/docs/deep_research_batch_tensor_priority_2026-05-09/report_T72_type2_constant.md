# Report T#72 — Type-2 Constant of Tensors (Bandeira-Dmitriev / Lucca)

**Catalog entry:** `aporia/mathematics/tensor_open_problems_v1.md` §IX entry #72
**Source dispatch:** `aporia/docs/gemini_tensor_priority_dispatch_2026-05-09.md` (Tier 3, fire-17)
**Author:** Aporia (deep-research, 2026-05-09, WebSearch+WebFetch live-verified)
**Doctrine:** HARD-1, HARD-2, HARD-5, HARD-6
**Patterns cited:** PATTERN_CONDUCTOR_CONFOUND, PATTERN_BASE_RATE_NEGLECT, PATTERN_RANK_PARITY_LEAK, PATTERN_VRAM_TRUNCATION_ARTIFACT
**Tags:** P28 adjacent, P15 base, P30 adjacent, P25 (volumetric-barrier-as-pivotal-negative-result), candidate P32 (Geometric/Covering-Number Concentration)
**Substrate-tester ticket bridges:** `T-ST-fire43-001` (Tier-D recovery sister), `T-ST-fire45-001` (CP identifiability adjacent); new ticket recommended `T-ST-fire-T72-001`.

## Brief summary

T#72 is **Conjecture 16** of *Randomstrasse101: Open Problems of 2025* (arXiv:2603.29571, Bandeira-Dmitriev-Lucca-Nizić-Nikolac-Rödder; conjecture proposed by **Lucca**, not Bandeira-Dmitriev jointly — they are editors of the volume). The conjecture asserts the tensor analogue of matrix Bernstein: for symmetric deterministic tensors `T_1,…,T_n ∈ (R^d)^⊗r` and i.i.d. Gaussians, `E ‖Σ g_i T_i‖_{I_p} ≤ Õ_{r,p}(d^{1/2−1/p} · (Σ ‖T_i‖²_{I_p})^{1/2})` for `p ≥ 2`. The matrix base case `r=p=2` was settled by **Tomczak-Jaegermann (1974)** and given clean form by **Ahlswede-Winter (2002)**: `√log(d+1)·(Σ‖M_i‖²₂)^{1/2}`. The conjecture is **resolved for `p ≥ 2r`** by Bandeira-Gopi-Jiang-Lucca-Rothvoss (arXiv:2411.10633, STOC 2025) via a covering-number / Dudley-entropy argument with a Ball-Pisier ℓ_p inequality, and **open for `p < 2r`** because of an explicit *volumetric barrier* in the covering proof. The matrix-state-of-the-art (Bandeira-Boedihardjo-van Handel, *Inventiones* 2024) handles `r=2` via a free-probability noncommutative model that has no current `r ≥ 3` analogue. Lucca explicitly identifies five-application convergence: coding-theoretic LDC lower bounds, dispersive-PDE Strichartz estimates, tensor-PCA SoS hardness (T#73 sister), Banach-space type-2 geometry, and Gaussian-process supremum control. T#72 is a **Tier-D distributional primitive** sister to T#73 and the sharpest single substrate-grade lever for tightening sister conjectures #24, #71, #73 simultaneously.

## Flagged findings

1. **Attribution correction.** The catalog entry says "Bandeira-Dmitriev"; the actual proposer of Conjecture 16 inside arXiv:2603.29571 is **Kevin Lucca**. Five document authors (Bandeira, Dmitriev, Lucca, Nizić-Nikolac, Rödder). A Learner consuming the catalog literally will fabricate "Bandeira-Dmitriev jointly conjectured" — false. Substrate must record proposer separately from editor / paper-author. **PATTERN_CONDUCTOR_CONFOUND.**

2. **Resolved-vs-open within the same conjecture (FM-08 calibration trap).** Resolved for `p ≥ 2r` (BGJLR 2024 / STOC 2025); open for `p < 2r`; matrix case `r = 2` settled tight (BBvH 2023, *Inventiones* 2024). Encoding "type-2-constant-of-tensors is resolved" is FM-08-shaped wrong. The substrate must encode the regime split as a first-class field, not a single status boolean.

3. **The volumetric barrier is mechanistically identified.** BGJLR explicitly state: covering-number estimates on the ℓ_p ball lose at small `p` because the ball's volume relative to the natural Gaussian-process metric is too large for Dudley's entropy integral. This is a real obstruction (mechanism-limited, not technique-limited in the standard sense). Resolving it requires generic chaining (Talagrand `γ_2`), PAC-Bayesian, or a higher-order free-probability noncommutative model — none currently sufficient as of mid-2025.

4. **Worst-gap regime is `r ≥ 3, p = 2` (operator norm).** The polynomial gap there is `d^{(r−1)/(2r)}` — the largest unresolved gap in the conjecture and the cell where most applications cluster (SoS lower bounds, tensor PCA, dispersive PDE).

5. **The matrix `r = p = 2` case has a `d^{1/4} · log d` slack between BGJLR's geometric bound and the sharp BBvH free-probability bound** — the matrix case is the calibration baseline for measuring how far the geometric covering technique is from optimal in the tensor case. **PATTERN_RANK_PARITY_LEAK** (the matrix-vs-tensor jump at `r = 2` vs `r ≥ 3` is parametrized by `r`; flattening to a single bound exponent leaks rank/order information).

6. **Five-application convergence makes T#72 a Tier-D substrate primitive sister to T#73.** Lucca explicitly lists: (a) coding theory (LDC lower bounds), (b) dispersive PDEs, (c) tensor PCA, (d) Banach-space type-2 geometry, (e) Gaussian process supremum control. Resolving Conjecture 16 simultaneously tightens all five. **PATTERN_BASE_RATE_NEGLECT**: the base rate of "single conjectures with five-application convergence" is small; treating each application as independent will under-prioritize.

7. **Boedihardjo (arXiv:2412.21193, 2024) is sibling-not-competitor.** It bounds the injective norm of a random tensor with i.i.d. entries — a strict subcase of Conjecture 16 (which is sums of *deterministic* tensors with Gaussian weights). Substrate must record both: independent-entry bound = special case; Conjecture 16 = full statement.

8. **Substrate gap (closed by this report).** Tier-D `RandomTensorConcentrationCert` dataclass spec needed: `(order_r, dim_d, p_norm, n_summands, upper_bound_exponent, upper_bound_polylog, lower_bound_exponent, regime ∈ {matrix_r2, p_geq_2r, p_lt_2r, p_eq_infty}, status ∈ {resolved_tight, resolved_log_slack, resolved_poly_slack, open}, source_anchor, proposer, technique, MC_estimate, MC_sample_size, MC_seed)`. Add to Techne T038 classification ticket.

9. **Substrate-grade empirical contribution available.** Monte Carlo scaling-exponent estimation for `r ∈ {3,4}, d ∈ {20, 50, 100}, p ∈ {2, 3, 4}, n = d^r` could surface whether the conjectural `1/2 − 1/p` or the BGJLR-tight `1/2 − 1/(2r)` matches the empirical curve in the open `p < 2r` regime. Schedule on M2 CPU under replicate-seeds protocol (≥ 5 seeds/cell). **PATTERN_VRAM_TRUNCATION_ARTIFACT alert**: at `d=50, r=3, n=d^r`, one Gaussian sample ≈ 125k floats; 1000 samples ≈ 1 GB working memory; will OOM a 17 GB GPU when run alongside TransformerLens.

10. **Paradigm refinement candidate P32.** BGJLR's geometric-covering-number / Dudley / Ball-Pisier-on-Schatten technique is currently subsumed under P15+P08 in the active taxonomy. **Recommendation: hold** until a second large-scale problem is solved by the same technique. One application (T#72 partial resolution) is not enough to motivate a new paradigm slot; substrate-tester should monitor BGJLR follow-up papers 2025-2027.

## 1. Problem Statement

For order `r ≥ 2`, dimension `d`, real `p ∈ [2, ∞]`, the **injective ℓ_p norm** of `T ∈ (R^d)^⊗r` is `‖T‖_{I_p} = sup{⟨T, u_1⊗…⊗u_r⟩ : ‖u_j‖_p ≤ 1}`.

**Conjecture 16 (Lucca, in Bandeira-Dmitriev-Lucca-Nizić-Nikolac-Rödder, arXiv:2603.29571).** For symmetric deterministic `T_1,…,T_n ∈ (R^d)^⊗r` and i.i.d. standard Gaussians `g_i`, with `p ≥ 2`,

  `E ‖Σ g_i T_i‖_{I_p} ≤ Õ_{r,p}( d^{1/2 − 1/p} · (Σ‖T_i‖²_{I_p})^{1/2} )`

(constants depending on `(r,p)`, polylog factors in `(d,n)`).

**Equivalent type-2-constant form.** `C_{r,p}(d)` = smallest constant making the inequality hold; conjecture asserts `C_{r,p}(d) ≲_{r,p} d^{1/2−1/p}` polylog. Recovers Tomczak-Jaegermann / Ahlswede-Winter `√log d` for `r = p = 2`.

## 2. Status & Bounds

| Regime | Status | Best upper bound | Best lower bound | Gap |
|---|---|---|---|---|
| `r=2, p=2` | resolved tight | `√log d` (Ahlswede-Winter 2002; tight via BBvH 2023) | `√log d` | tight |
| `r=2, p≥2` | resolved log-slack | `d^{1/2−1/p} log d` (Tropp 2015) | `d^{1/2−1/p}` | log only |
| `r≥3, p≥2r` | resolved log-slack | `d^{1/2−1/p} log d` (BGJLR 2024) | `d^{1/2−1/p}` | log only |
| `r≥3, p<2r` | **OPEN** | `d^{1/2−1/(2r)} log d` (BGJLR 2024) | `d^{1/2−1/p}` | `d^{1/p−1/(2r)}` polynomial |
| `r≥3, p=2` (operator norm) | **OPEN — worst gap** | `d^{1/2−1/(2r)} log d` | `1` | `d^{(r−1)/(2r)}` polynomial |

Volumetric / second-moment lower bound `d^{1/2−1/p} ≲ C_{r,p}(d)` holds in all regimes — gap is purely on upper-bound side. No conditional impossibility known; conjecture plausibly true.

**Theorem 1.2 of BGJLR (arXiv:2411.10633):** `d^{1/2−1/p} ≲_{r,p} C_{r,p}(d) ≲_{r,p} d^{1/2−1/max{p,2r}} log d`.

## 3. Literature

**Foundational matrix:**
- Tomczak-Jaegermann 1974 (Banach-Mazur dist between trace classes); monograph: *Banach-Mazur Distance and Finite-Dimensional Operator Ideals*, Pitman 1989.
- Ahlswede-Winter 2002 (IEEE Trans. Inf. Theory 48(3)) — clean matrix-Chernoff.
- Pisier 1998 (Astérisque) — non-commutative Khintchine framework.
- Tropp 2015, *An Introduction to Matrix Concentration Inequalities*, NOW Publishers (arXiv:1501.01571).

**Modern matrix line:**
- **Bandeira-Boedihardjo-van Handel 2023**, *Matrix Concentration Inequalities and Free Probability*, *Inventiones Mathematicae* 234 (2024), arXiv:2108.06312. **Current matrix state-of-the-art.**
- Brailovskaya-van Handel 2024, *GAFA*, arXiv:2201.05142 (universality companion).

**Tensor case (this conjecture's direct line):**
- Latała 2006 — covering-number bounds for injective ℓ_2 norm of structured tensors.
- **Boedihardjo 2024**, arXiv:2412.21193 — independent-entries sibling.
- **Bandeira-Gopi-Jiang-Lucca-Rothvoss 2024**, *A Geometric Perspective on the Injective Norm of Sums of Random Tensors*, arXiv:2411.10633. **Conference: STOC 2025, DOI:10.1145/3717823.3718188.** **Best partial resolution.**
- **Bandeira-Dmitriev-Lucca-Nizić-Nikolac-Rödder 2026**, *Randomstrasse101: Open Problems of 2025*, arXiv:2603.29571. **Source for Conjecture 16.**

**Adjacent:**
- Vershynin 2018, *High-Dimensional Probability*, CUP.
- Talagrand 2014, *Upper and Lower Bounds for Stochastic Processes*, Springer.
- Hopkins thesis Cornell 2018 (SoS lower bound application).

**Tools:** `TensorLy` (numerical injective ℓ_p), `numpy/scipy` (MC), `Pari/GP/Magma/M2` flagged HARD-2 — *not* the right tools here (problem is analytic-probabilistic, not algebraic-geometric).

## 4. Attack Vectors

**(A) Geometric covering / Dudley chaining (P15+P08; candidate P32).** BGJLR workhorse; pushed to its limit in `p ≥ 2r`; volumetric barrier blocks `p < 2r`. Substrate-relevant — covering numbers are MC-estimable.

**(B) Generic chaining / Talagrand `γ_2` majorizing measures (P15+P08).** Natural next attempt for `p < 2r`. **Open as of mid-2025.**

**(C) PAC-Bayesian (P08).** Bandeira-Boedihardjo style; works for independent-entries subcase (Boedihardjo 2024); does not yet extend to deterministic-`T_i`-with-Gaussian-weights setting.

**(D) Free-probability noncommutative model (P04+P28).** BBvH 2023 *Inventiones* settled `r=2` via free probability matching. **Open for `r ≥ 3`.** PATTERN_RANK_PARITY_LEAK: matrix free-probability captures `r=2` rank-2 structure; higher-rank operator-algebra extension undeveloped.

**(E) Explicit type-2-witness construction (P09+P15).** Saturating ensembles; Section 5 of BGJLR discusses LDC-related constructions.

**(F) SoS hierarchy hardness as driver (P25+P28-adjacent).** SoS lower bounds for tensor PCA invoke type-2-constant bounds; sharp Conjecture 16 → tighter SoS hardness by `d^{1/p−1/(2r)}` factors. Quoted in Bandeira-Dmitriev document: *"any improvement would result in better lower bounds for SoS hierarchies."*

**(G) Dispersive-PDE Strichartz (P05+P15).** Bourgain-style space-time Strichartz estimates have type-2-constant-shaped bounds.

**(H) Coding-theoretic LDC (P09+P15).** LDC query-complexity lower bounds go through type-2 inequalities on codeword tensor (BGJLR §5.4).

**No purely algebraic-geometric (P29/P31) path is currently active** (HARD-2 self-correction: substrate's reflex toward σ_r equations is wrong here).

**Candidate P32 (Geometric / Covering-Number Concentration).** BGJLR technique has internal coherence sufficient to motivate a paradigm slot; **hold** until a second problem solved by same technique.

## 5. Substrate Encoding

**Tier-D distributional primitive `RandomTensorConcentrationCert`:**

```python
@dataclass
class RandomTensorConcentrationCert:
    order_r: int                     # ≥ 2; r=2 is matrix
    dim_d: int
    p_norm: float                    # injective ℓ_p exponent (p ≥ 2)
    n_summands: int

    upper_bound_exponent: Fraction   # current best: 1/2 - 1/max(p, 2r)
    upper_bound_polylog: int
    lower_bound_exponent: Fraction   # 1/2 - 1/p (volumetric)

    regime: Literal["matrix_r2", "p_geq_2r", "p_lt_2r", "p_eq_infty"]
    status: Literal["resolved_tight", "resolved_log_slack",
                    "resolved_poly_slack", "open"]

    source_anchor: str               # e.g. "arXiv:2411.10633 Theorem 1.2"
    proposer: Optional[str]          # "Lucca" for Conjecture 16
    technique: Literal[
        "ahlswede_winter", "non_commutative_khintchine",
        "free_probability", "covering_number_dudley",
        "generic_chaining", "pac_bayesian", "explicit_witness",
    ]

    monte_carlo_estimate: Optional[float]
    monte_carlo_sample_size: Optional[int]
    monte_carlo_seed: Optional[int]
```

Sister to T#73's `PhaseTransitionThreshold + AlgorithmThresholdCert + GenericityAlmostEverywhereCert` triple. T#72 = concentration framing; T#73 = recovery framing; both share `(d, n)` axis enabling cross-conjecture queries on the unified tensor (HARD-3).

**Cross-link to T#1, T#28** via probabilistic bounds on `M⟨n⟩` (asymptotic-rank functionals).

**Verifier hooks:** MC estimation of `E ‖Σ g_i T_i‖_{I_p}` for `(r,d,p,n)`; PATTERN_VRAM_TRUNCATION_ARTIFACT alarm at `d=50, r=3, n=d^r` (~1 GB MC sweep — schedule on CPU). **Substrate-grade empirical contribution available**: scaling-exponent measurement in open `p < 2r` regime to discriminate conjectural `1/2−1/p` vs BGJLR-tight `1/2−1/(2r)`.

## 6. Calibration Anchor Notes

**Substrate-grade response:** cite arXiv:2603.29571 Conjecture 16; identify proposer Lucca (not Bandeira-Dmitriev); state `d^{1/2−1/p}` polylog; identify resolved (`p≥2r`, BGJLR 2024) and open (`p<2r`, volumetric barrier) regimes; name technique (Dudley + Ball-Pisier); name matrix baselines (TJ 1974, AW 2002, BBvH 2024 Inventiones); record both bounds with polylog factors; flag `r≥3, p=2` as worst-gap cell.

**Fabrications to catch:**
1. "Bandeira and Dmitriev jointly proposed Conjecture 16." **False — Lucca proposed.**
2. "Conjecture 16 has been proven by BGJLR." **Half-true — proven for `p≥2r` only.**
3. "Tensor type-2 constant scales like `√log d`." **False — that's matrix; tensor is `d^{1/2−1/p}` polylog.**
4. "Volumetric barrier means conjecture is false." **False — technique limit, not true ceiling.**
5. "Banach-space-geometry only." **Misleading — five-application convergence.**

**Canonicality risks:** Ahlswede-Winter (info-theory canonical, not Tropp); Tomczak-Jaegermann (functional analysis canonical, not Pisier); BBvH (rapidly becoming canonical for matrix free-probability); BGJLR (full author list important — Gopi and Rothvoss often dropped in informal cites).

**FM-08 trap:** Encoding "type-2-constant-of-tensors is resolved" is FM-08-shaped wrong. Regime split is load-bearing.

## 7. Cross-References

**`tensor_open_problems_v1.md`:** #24 (operator norm, special case `p=2`), #71 (log-factor elimination sister), #73 (tensor PCA, SoS-hardness application), #1 (matrix mult exponent, asymptotic-rank cousin), #2/#7/#8 (asymptotic spectrum P28), #43 (best rank-r approximation, stability adjacent).

**`deep_research_batch_tensor_priority_2026-05-09/`:** `report_T73_tensor_pca_threshold.md` (Tier-D sister; this report's §4(F) is the concentration side feeding T#73's SoS lower bounds), `report_T1_matrix_multiplication_exponent.md`, `report_T28_asymptotic_spectrum.md`, `report_T26_defective_segre_veronese.md`.

**`attack_angle_taxonomy.md`:** P15 (base), P08 (probabilistic family), P04 (free probability for `r=2` only), P25 (volumetric barrier as pivotal-negative-result), P28 (asymptotic spectrum adjacent), P30 (TensorNetwork adjacent normalization).

**Substrate-tester:** existing `T-ST-fire43-001`, `T-ST-fire45-001`; new `T-ST-fire-T72-001` recommended (encode dataclass + populate §2 table + flag `r≥3, p=2` as MC priority).

## 8. Doctrine adherence

- **HARD-1:** No paper framing. Substrate-grade work-product.
- **HARD-2:** Suppressed "use Macaulay2" reflex (problem is analytic, not algebraic). Engaged literature as data only.
- **HARD-5:** Used "structural region" / "operator over `(r,p,d,n)` parameter region" framing. Five-application convergence as "same operator surfaces in five regions," not bridge narrative.
- **HARD-6:** Type-2 constant is load-bearing for HARD-3 tensor build; volumetric-barrier failure mode guides primitive shape; substrate-grade Monte Carlo contribution is on-mission.

## 9. Pattern citation explanations

- **PATTERN_CONDUCTOR_CONFOUND** — regime / normalization confound; `p ≥ 2r` vs `p < 2r` flip + injective-vs-Schatten-vs-HS choice.
- **PATTERN_BASE_RATE_NEGLECT** — five-application convergence is rare; Learner trained on textbook matrix Bernstein hallucinates `√log d` for tensors.
- **PATTERN_RANK_PARITY_LEAK** — `r=2` vs `r≥3` parity is load-bearing; bound exponent flip at `p=2r` parametrized by `r`.
- **PATTERN_VRAM_TRUNCATION_ARTIFACT** — MC verification at `d≥50, r≥3` saturates 17 GB GPU; CPU dispatch required.

## 10. Substrate-impact summary

- **Tier:** Tier-D distributional primitive (sister to T#73).
- **Encoded gap closed:** `RandomTensorConcentrationCert` dataclass spec.
- **Empirical contribution target:** MC scaling-exponent sweep `r∈{3,4}, d∈{20,50,100}, p∈{2,3,4}, n=d^r`, ≥5 seeds/cell, M2 CPU.
- **P19 (cross-region operator transport) candidate of strongest kind:** five-region operator simultaneity (coding / dispersive PDE / tensor PCA / Banach geometry / Gaussian process).
- **P32 paradigm refinement:** holding pending second large-scale problem solved by BGJLR-style geometric covering.

---

**Sources verified (live):**
- [Randomstrasse101: Open Problems of 2025 — arXiv:2603.29571](https://arxiv.org/abs/2603.29571)
- [Randomstrasse101 HTML — Conjecture 16](https://arxiv.org/html/2603.29571)
- [Randomstrasse101 blog: Tensor Concentration / Problem 16](https://randomstrasse101.math.ethz.ch/posts/tensor-concentration/)
- [BGJLR: A Geometric Perspective on the Injective Norm of Sums of Random Tensors — arXiv:2411.10633](https://arxiv.org/abs/2411.10633)
- [BGJLR STOC 2025: Tensor Concentration Inequalities: A Geometric Approach (DOI:10.1145/3717823.3718188)](https://dl.acm.org/doi/10.1145/3717823.3718188)
- [Boedihardjo: Injective Norm of Random Tensors with Independent Entries — arXiv:2412.21193](https://arxiv.org/pdf/2412.21193)
- [Bandeira-Boedihardjo-van Handel: Matrix Concentration and Free Probability — arXiv:2108.06312](https://arxiv.org/abs/2108.06312)
- [Brailovskaya-van Handel: Universality and Sharp Matrix Concentration — arXiv:2201.05142](https://arxiv.org/abs/2201.05142)
