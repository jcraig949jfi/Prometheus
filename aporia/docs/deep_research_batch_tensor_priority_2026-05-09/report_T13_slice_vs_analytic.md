# Report T#13 — Slice Rank vs Analytic Rank Gap

**Catalog entry:** `aporia/mathematics/tensor_open_problems_v1.md` §II #13
**Source dispatch:** `aporia/docs/gemini_tensor_priority_dispatch_2026-05-09.md` (Tier 3, fire-13)
**Substrate-tester linkage:** Tier-A++ rank-zoo calibration anchor (P27 paradigm core); cross-coupled with proposed `RankZooSignature` meta-primitive
**Author:** Aporia (deep-research)
**Date:** 2026-05-09
**Doctrine:** HARD-1, HARD-2, HARD-5, HARD-6
**Patterns cited:** PATTERN_RANK_PARITY_LEAK, PATTERN_CONDUCTOR_CONFOUND, PATTERN_BASE_RATE_NEGLECT
**Tags:** P27 (primary), P28 (asymptotic-spectrum dual), P25 (pivotal-negative-result via Lampert-Moshkovitz determinant separation), P24 (regularization-style relative rank)

---

## Brief summary

T#13 is the **rank-zoo coupling problem**: over a fixed finite field 𝔽_q, the analytic rank A(T), slice rank S(T), partition rank PR(T), and geometric rank GR(T) of an order-d tensor are now known to satisfy `S(T), PR(T) ≤ poly(A(T), d)` with the polynomial dependence improving across a 2018–2025 sequence (Lovett exponential → Janzer/Milicevic polynomial → Cohen-Moshkovitz linear for d=3 → Moshkovitz-Zhu quasi-linear all d → Baily-Lampert 2024 linear for d>3 over number/function fields). The **central open question** is whether the polynomial dependence collapses to a **constant factor independent of d** over arbitrary 𝔽_q. **Sept 2025 Lampert-Moshkovitz determinant result (arXiv:2509.06294)** is a negative-direction landmark: det_n exhibits PR/A → ∞ with d, giving the **first asymptotic separation** between partition rank and analytic rank — random constructions could not produce this, so the substrate's rank-zoo calibration must include the determinant family as a positive-control anchor for separation.

## Flagged findings

1. **The conjecture has been partially negated (Sept 2025).** Lampert-Moshkovitz arXiv:2509.06294 prove det_n witnesses `PR/A → ∞` as n → ∞. So a uniform constant ratio `PR(T) ≤ C·A(T)` independent of d **cannot hold**. The substrate must record this as canonical — a Learner that asserts "partition rank and analytic rank are equivalent up to a constant" without the d-dependence caveat is wrong as of Sept 2025.

2. **Slice rank vs analytic rank for d=3 has constant factor (post-2021).** Cohen-Moshkovitz (arXiv:2102.04657) and Adiprasito-Kazhdan-Ziegler independently. Lampert 2025 (*Discrete Analysis*) gives an **elementary, Derksen-free** proof — slice-rank decomposition has additional **coordinate-restriction** structure the substrate currently has no field for.

3. **For d > 3 the answer depends on the field.** Baily-Lampert 2024 (arXiv:2410.00248) — **linear bound** strength ≤ C(d, trdeg)·BirchRank over number / function fields. Over 𝔽_q, only **quasi-linear** (Moshkovitz-Zhu 2022, refined). PATTERN_CONDUCTOR_CONFOUND is acute: same tensor, different field, different attainable bound.

4. **Substrate gap — `RankZooSignature` primitive missing.** No current substrate primitive records the **5-tuple** `(R, SR, PR, AR, GR)` with inequality witnesses. This is the canonical PATTERN_RANK_PARITY_LEAK calibration test.

5. **Two new ticket proposals:** `T-ST-T13-001` (RankZooSignature 5-tuple probe with d-dependence carve-out — must record `field: 𝔽_q | num_field | func_field`); `T-ST-T13-002` (DeterminantSeparation positive-control — any "PR ≤ C·A uniformly" claim auto-checked against det_n at n ≥ 5).

6. **P27 tactics list refinement (not new paradigm).** Add **Strength**, **Birch rank**, **Schmidt rank**, **local rank** (Moshkovitz-Zhu 2022), and **coordinate-restriction slice rank** (Lampert 2025) as named tactics under P27 in `attack_angle_taxonomy.md`.

7. **PATTERN_BASE_RATE_NEGLECT trap:** "typical" tensors over 𝔽_q have all four ranks coincident up to lower-order terms. Constant-ratio claims may be true generically and fail on the measure-zero structured locus (det_n, perm_n, GTLMS counterexample).

## 1. Problem statement

Let 𝔽 = 𝔽_q be a finite field. For an order-d multilinear T : V_1 × ... × V_d → 𝔽:

- **Tensor rank R(T)** = min count of full simple tensors summing to T.
- **Slice rank S(T)** (Tao 2016) = min count of `f(x_j)·g(x_{≠j})` terms.
- **Partition rank PR(T)** (Naslund 2017, *J. Combin. Theory Ser. A* 174, 2020) = min count of `f(x_S)·g(x_{S^c})` over arbitrary nontrivial bipartitions.
- **Analytic rank A(T)** (Gowers-Wolf; Lovett 2018) = `−log_q E_x ψ(T(x))` for nontrivial additive char ψ.
- **Geometric rank GR(T)** (Kopparty-Moshkovitz-Zuiddam 2020) = codim of `{(x_1,...,x_{d−1}) : T(x_1,...,x_{d−1},·) ≡ 0}`.

**Known unconditionally:**
```
S(T) ≤ PR(T) ≤ R(T)
A(T) ≤ GR(T)
A(T) ≤ PR(T)        [Lovett 2018]
```

**T#13 question:** is there `C = C(q)` (independent of d) such that `PR(T) ≤ C·A(T)` and `S(T) ≤ C·A(T)` for every order-d tensor over 𝔽_q?

For d=3: **YES** (Cohen-Moshkovitz 2021; Adiprasito-Kazhdan-Ziegler; Lampert 2025). For d≥4 over 𝔽_q: best is **quasi-linear with d-dependent polylog**. **For partition rank, uniform-in-d constant cannot exist** (Lampert-Moshkovitz Sept 2025).

## 2. Status & bounds

| Year | Authors | Bound | Regime |
|---|---|---|---|
| 2016 | Tao (blog) | Slice rank defined; SR-method for cap-sets | 𝔽_3, d=3 |
| 2017 | Naslund | Partition rank | 𝔽_q, all d |
| 2018 | Lovett (arXiv:1806.09179) | A subadditive; converse `S ≤ f(A,d)` Ackermann-type | 𝔽_q, all d |
| 2019 | Janzer (arXiv:1902.09830, GAFA); Milicevic (arXiv:1902.11207) | `PR ≤ A^{2^{poly(d)}}` polynomial-in-A | 𝔽_q, all d |
| 2020 | Kopparty-Moshkovitz-Zuiddam (arXiv:2002.09472) | GR introduced; `A ≤ GR ≤ R`; GR≃A const for d=3 | finite, alg-closed |
| 2021 | Cohen-Moshkovitz (arXiv:2102.04657, *Discrete Analysis* 2022) | **For d=3, S,A,GR equal up to absolute constant** | any 𝔽_q, d=3 |
| 2021 | Cohen-Moshkovitz (arXiv:2102.10509, *Duke* 2023) | `PR ≤ C·A` over 𝔽_q with |𝔽_q| > Q(A) | "large fields" all d |
| 2022 | Moshkovitz-Zhu (arXiv:2211.05780) | **Quasi-linear** `PR ≤ A·log^{O(1)}(A)` all d, all 𝔽_q. Local rank | any 𝔽_q, all d |
| 2024 | Karam (LIPIcs ITCS 2024) | Sunflower structure of slice-rank decomps | 𝔽_q, all d |
| 2024 | Sauermann (Surveys in Combinatorics) | 80-ref state-of-art survey | survey |
| 2024 | Adiprasito-Kazhdan-Ziegler (arXiv:2409.04034) | Linear Schmidt ≤ const·analytic for d=3; rank stability | finite |
| 2024 | Baily-Lampert (arXiv:2410.00248) | **Linear** strength ≤ C(d,trdeg K)·BirchRank for K=number/function field | num/func: linear; 𝔽_q: quasi-linear |
| 2025 | Lampert (*Discrete Analysis*) | **Elementary Derksen-free** S ≤ const·A for d=3 | any 𝔽_q, d=3 |
| 2025 | Lampert-Moshkovitz (arXiv:2509.06294, Sept 2025) | **S(det_n) = n exactly**; **PR(det_n) ≥ log_2(n)+1**; **first asymptotic separation PR(det_n)/A(det_n) → ∞** | ℂ, ℚ, finite |

**Frontier subdivision (post-Sept-2025):**
- T#13(a) SR vs A uniform-in-d gap — **OPEN**
- T#13(b) PR vs A uniform-in-d gap — **CLOSED NEGATIVE** (Lampert-Moshkovitz)
- T#13(c) SR vs A best constant for d=3 — **OPEN QUANTITATIVE**
- T#13(d) PR vs A over 𝔽_q linear-vs-quasi-linear — **OPEN QUANTITATIVE**

## 3. Literature

Canonical refs:
- Tao 2016 blog (slice rank origin); Croot-Lev-Pach 2017 *Annals*; Ellenberg-Gijswijt 2017 *Annals*; Naslund 2020 *JCTA* (partition rank); Lovett 2018/19 *Discrete Analysis* (analytic rank framework); Janzer 2020 *GAFA* and Milicevic 2019 (polynomial bound); Kopparty-Moshkovitz-Zuiddam 2020 (geometric rank); Cohen-Moshkovitz 2022 *Discrete Analysis* and 2023 *Duke* (linear for d=3 / large fields); Moshkovitz-Zhu 2022 (quasi-linear, local rank); Adiprasito-Kazhdan-Ziegler series 2021–2024; Karam ITCS 2024; Sauermann *Surveys in Combinatorics 2024*; Baily-Lampert 2024 (strength ≤ Birch); Lampert 2025 (elementary d=3); Lampert-Moshkovitz Sept 2025 (det_n separation); Briët et al. 2022 (random restrictions); Juvekar 2022 Rochester thesis.

**Named tools:** No dedicated software ecosystem for analytic-rank at scale; case-by-case in Sage/Magma. **TensorLy / TensorToolbox are inappropriate** here — they target real/complex CP rank, structurally different from finite-field combinatorial ranks. PATTERN_RANK_PARITY_LEAK at architecture level if a primitive is built on TensorLy and labelled "tensor rank."

## 4. Attack vectors

**Primary paradigm: P27** (Slice Rank / Polynomial Method on 𝔽_q). Recommend extending the tactics list to include: **local rank** (Moshkovitz-Zhu), **strength**, **Birch rank**, **Schmidt rank**, **coordinate-restriction slice rank** (Lampert 2025).

**Active attack vectors:**
1. Sharpening Lovett's exponential proof — superseded 2019 (historical only).
2. Improving Janzer/CM/MZ bounds — active; current state quasi-linear over 𝔽_q.
3. Constructing extremal-ratio families — **Lampert-Moshkovitz det_n settles direction for PR**; open question is whether any explicit family separates **slice rank from analytic rank**.
4. Tensor-product slice-rank constructions — more central to T#15.
5. Gowers-norm / higher-order Fourier connections — **active**; the Lampert-Moshkovitz result connects to Green-Tao-Lovett-Meshulam-Samorodnitsky counterexample to Gowers Inverse in low char.
6. Random-restriction / regularity-style proofs (Briët et al. arXiv:2212.13728) — P24-flavored.
7. Field-extension stability (AKZ 2024 arXiv:2409.04034) — PATTERN_CONDUCTOR_CONFOUND directly.

**No new paradigm needed beyond P27** — refinement of tactics list only.

## 5. Substrate encoding

**Proposed dataclass `RankZooSignature`:** records the 5-tuple `(R, SR, PR, AR, GR)` plus `LocalRank`, `Strength`, `BirchRank`, `SchmidtRank`, with explicit `field: FieldSpec` selector, `bias_seed` for character-sum reproducibility, `decomposition_witnesses` (per rank type), `coordinate_restriction_flag` (Lampert 2025 structural property), and `inequality_chain_verified` list.

```python
@dataclass(frozen=True)
class RankZooSignature:
    tensor_id: str
    field: FieldSpec
    order_d: int
    dims: tuple[int, ...]
    R: Optional[Bound]
    SR: Optional[Bound]
    PR: Optional[Bound]
    AR: Optional[Bound]
    GR: Optional[Bound]
    LR: Optional[Bound]
    Strength: Optional[Bound]
    BirchRank: Optional[Bound]
    SchmidtRank: Optional[Bound]
    bias_seed: Optional[int]
    decomposition_witnesses: dict[str, DecompositionRecord]
    coordinate_restriction_flag: bool
    inequality_chain_verified: list[str]
```

**Calibration probes proposed:**
- `RankZooSignature_random` (𝔽_q^d ensembles) — base-rate baseline.
- `RankZooSignature_determinant` (det_n, n ∈ {3,4,5,6,8}) — **canonical PATTERN_RANK_PARITY_LEAK test**.
- `RankZooSignature_capset_constraint` (δ(x+y+z=0) on 𝔽_3) — Tao 2016 SR ≈ 1.013·n anchor.
- `RankZooSignature_gtlms` — Green-Tao-Lovett-Meshulam-Samorodnitsky counterexample.
- `RankZooSignature_field_extension` — AKZ 2024 stability checks.

**Substrate gaps:**
- No Tier-A++ rank-zoo primitive in tensor primitive catalog.
- No analytic-rank computation tool in Techne inventory.
- No determinant family as positive-control anchor in calibration corpus (HARD-4 anchor-hunt action).

## 6. Calibration anchor notes

**Substrate-grade answer to "what is the relation between SR and AR?"** must include: (i) d-dependence carve-out (uniform-in-d const impossible for PR per Lampert-Moshkovitz Sept 2025); (ii) field carve-out (linear over num/func fields per Baily-Lampert 2024; quasi-linear over 𝔽_q); (iii) d=3 caveat (S,PR,A,GR all coincide up to abs const); (iv) explicit naming of which rank.

**Textbook-trivial answer** ("slice rank and analytic rank are equivalent up to a constant") is **false** as of Sept 2025 unless qualified to d=3 or to "for a generic / random tensor."

**Learner failure modes (canonical attribution risks):**
- Crediting Cohen-Moshkovitz alone for d=3 — AKZ proved independently.
- Crediting Lovett with the polynomial bound — Lovett's is exponential. Polynomial is Janzer + Milicevic, simultaneously and independently.
- Conflating slice rank with partition rank (coincide for d=3, not d=4).
- Using TensorLy / numerical CP-rank for finite-field rank questions.
- Claiming "Moshkovitz-Zhu solved the conjecture" — they proved it up to log; uniform-in-d const factor is OPEN for SR, CLOSED-NEGATIVELY for PR.
- Hallucinating direct ω = 2 implications.

**Canonical authors:** Top tier — Tao, Lovett, Naslund. Specialist — Cohen, Moshkovitz, Zhu, Janzer, Milicevic, Kopparty, Zuiddam, Adiprasito, Kazhdan, Ziegler, Baily, Lampert, Karam, Sauermann. Classical prehistory — Schmidt, Birch, Gowers-Wolf.

**Pattern application:** **PATTERN_RANK_PARITY_LEAK** primary trap (rank of T undefined; substrate must always specify which rank, must record the 5-tuple). **PATTERN_CONDUCTOR_CONFOUND** secondary (field q, char(𝔽_q), trdeg(K) are confounders). **PATTERN_BASE_RATE_NEGLECT** tertiary (random tensors satisfy strong rank-equivalence; structured tensors det_n, perm_n, GTLMS violate it).

## 7. Cross-references

**Catalog:**
- **#14** GR vs PR — direct sibling; KMZ 2020 settles d=3. T#14 should inherit determinant-separation.
- **#15** Slice-rank method optimality beyond 𝔽_3 — applications-side companion.
- **#16** Subrank-rank duality / asymptotic spectrum — slice rank IS one of Strassen's monotones.
- **#19** Cactus rank vs rank/border rank — **structurally disjoint** (cactus rank is over alg-closed; SR/AR over 𝔽_q). Substrate primitives must NOT conflate T#13 and T#19.
- **#1** ω matrix multiplication — KMZ 2020 used GR for subrank lower bounds.
- **#56** Symmetric tensor rank NP-hardness — strength = PR/2 for symmetric forms; Baily-Lampert cross-coupling.
- **#95–99** Kronecker/Foulkes/Saxl plethysm.

**Existing reports in batch:** T1, T26, T28, T34, T43, T56, T58, T73, T79, T84, T95, T85.

**Substrate-tester capability-gap tickets (proposed):**
- `T-ST-T13-001` RankZooSignatureProbe (Tier-A++; default-fail without explicit field tag).
- `T-ST-T13-002` DeterminantSeparationProbe (positive-control battery; auto-check det_n at n ∈ {3,4,5,6,8}).
- `T-ST-T13-003` RankZooFieldExtensionProbe (AKZ 2024 stability under 𝔽_q ↪ 𝔽_{q^k}).

**Techne T# tool needs (proposed):**
- `analytic_rank_compute(T, q) → Bound` (Gowers character sum).
- `slice_rank_certificate(T) → (Bound, decomposition)`.
- `determinant_tensor(n, ring)` constructor with "Lampert-Moshkovitz separation anchor" metadata flag.

---

## Appendix A — exact bounds cheat-sheet

For order-d tensor T over 𝔽_q (q = p^k):

```
A ≤ S ≤ PR ≤ R                           [Lovett 2018]
A ≤ GR                                   [KMZ 2020]

d = 3, all 𝔽_q:
  S ≤ C·A      C absolute              [CM 2021, AKZ, Lampert 2025]
  S, PR, A, GR coincide up to abs const [Cohen-Moshkovitz 2021]

d ≥ 4, |𝔽_q| > Q(A):
  PR ≤ C·A     C absolute              [CM Duke 2023]

d ≥ 4, all 𝔽_q:
  PR ≤ A · log^{O(d)}(A)               [Moshkovitz-Zhu 2022, refined Baily-Lampert 2024]

d ≥ 4, K = number / function field:
  Strength ≤ C(d, trdeg K) · BirchRank [Baily-Lampert 2024]

Asymptotic in d:
  PR(det_n)/A(det_n) → ∞  as n → ∞     [Lampert-Moshkovitz Sept 2025]
  ⟹ no uniform-in-d constant PR ≤ C·A.

OPEN:
  S(T) ≤ C·A(T)  with C indep of d, over 𝔽_q.
  PR ≤ A · log(A) (single log not polylog).
```

## Appendix B — recommended anchor families

1. **det_n**, n ∈ {2,3,4,5,6,8} — separation positive control.
2. **perm_n**, n ∈ {2,3,4,5} — sister object.
3. **δ(x+y+z=0)** over 𝔽_3, 𝔽_5, 𝔽_7 — cap-set constraint.
4. **GTLMS counterexample** to Gowers Inverse — known structural separator.
5. **Random tensor ensembles** over 𝔽_q^d — base-rate.
6. **Diagonal tensors** δ_{x_1=...=x_d} — extremal (R=SR=PR=AR=n).
7. **Matrix multiplication tensor** ⟨n,n,n⟩ — interface with T#1.

---

*Aporia, 2026-05-09*
