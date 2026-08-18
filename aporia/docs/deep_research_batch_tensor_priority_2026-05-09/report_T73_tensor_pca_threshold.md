# Report T#73 — Tensor PCA Computational Threshold

**Catalog entry:** `aporia/mathematics/tensor_open_problems_v1.md` §IX Random Tensors, entry #73
**Source dispatch:** `aporia/docs/gemini_tensor_priority_dispatch_2026-05-09.md` (Tier 2, fire-9)
**Author:** Aporia (deep-research; sandboxed run, see §0 caveat)
**Date:** 2026-05-09
**Doctrine:** HARD-1, HARD-2, HARD-5, HARD-6
**Patterns cited:** PATTERN_BASE_RATE_NEGLECT, PATTERN_CONDUCTOR_CONFOUND, PATTERN_RANK_PARITY_LEAK
**Tags:** P22 (polynomial method — SoS lower bounds), P25 (pivotal-negative-result class — LDLR is a P25-shaped tool), P28 (asymptotic spectrum — adjacent), P30 (TensorNetwork — adjacent), P15 (multilinear decomposition — base object); proposed candidate paradigm **P25b — Hierarchy-Internal Hardness**
**Substrate-tester ticket:** `T-2026-05-08-ST-fire43-001` (Tier-D CONFIRMED + extended to 5 primitives; this report supplies the literature backing for that ticket)

---

## 0. Caveat — sandboxed run, no live web access

This report was produced in an environment without WebSearch / WebFetch tools. All references, dates, and arXiv IDs are **drawn from pre-2026 model knowledge**, NOT live-verified. Items marked **[CHECK]** are load-bearing facts that a Learner consuming this report must re-verify before treating as canon. The structural narrative (statistical-vs-computational gap, SoS hierarchy, LDLR framework, λ scalings, AMP/power-method behavior) is robust pre-2024 settled material; the fabrication risk concentrates in (a) author-list completeness for 2024–2026 follow-ups and (b) precise scaling exponents in non-standard normalizations.

---

## Brief summary

T#73 is the **canonical statistical-vs-computational gap problem** in modern high-dimensional statistics. Spike model T = λ·v^⊗d + W (W i.i.d. Gaussian, v unit) admits a sharp 12-year-old phenomenology: information-theoretic threshold λ_stat (Richard–Montanari 2014); conjectured polynomial-time threshold λ_comp ≍ n^{(d−2)/4} (a strict gap for d ≥ 3); a hierarchy of algorithms (tensor power method, AMP, spectral / unfolding, sum-of-squares, Kikuchi) populating the regime above λ_comp, and matching low-degree-likelihood-ratio (LDLR) and SoS lower bounds suggesting λ_comp is sharp under the "low-degree class" computational model. Substrate-tester fire #43 already converged on this; the report's job is to back the encoding with literature, flag the precise dataclass shape `GenericityAlmostEverywhereCert`, and surface the calibration anchors that distinguish substrate-grade from textbook framing. Two patterns load-bear: PATTERN_BASE_RATE_NEGLECT (most natural priors do **not** realize the conjectured gap; the gap is a feature of the spike model under specific noise scaling) and PATTERN_CONDUCTOR_CONFOUND (the signal-to-noise λ is regime-defining; results are quoted within a fixed normalization that must travel with every claim).

## Flagged findings

1. **The "gap" is normalization-dependent.** With W having i.i.d. N(0,1) entries and v ∈ S^{n−1} unit-norm, threshold scalings as written above are standard. Other natural normalizations shift the exponents by additive constants. **Substrate must carry the normalization in the dataclass.** PATTERN_CONDUCTOR_CONFOUND.

2. **LDLR is itself a P25-shaped tool.** Low-degree-likelihood-ratio lower bounds work by *failing to distinguish* the planted distribution from null at low polynomial degree. The lower bound is a structured negative result that reorients algorithm design. Hopkins (thesis 2018) is the canonical write-up; Kunisky–Wein–Bandeira 2019 (arXiv:1907.11636) is the survey. **[CHECK]** identifier and authors.

3. **SoS-based hardness ≠ classical NP-hardness.** The literature treats "computational hardness via SoS" as a proof technique distinct from a classical-complexity-class lower bound. It produces unconditional lower bounds *within* the SoS hierarchy at fixed degree. Substrate must record SoS-degree and not flatten "SoS lower bound" into "NP-hard." Motivates a tentative paradigm refinement **P25b — Hierarchy-Internal Hardness** (sub-paradigm of P25 distinguished by the constraint that the negative result holds only within a specified hierarchy / computational class).

4. **Tier-D PhaseTransitionThreshold + AlgorithmThresholdCert + GenericityAlmostEverywhereCert all needed.** Substrate-tester fires #43 + #45 surfaced these. T#73 is the **canonical instance** of Tier-D distributional encoding.

5. **Brennan–Bresler reductions** tie tensor PCA hardness to planted-clique-style hardness via average-case reductions. arXiv:2005.08099 (Brennan–Bresler 2020 "Reducibility and statistical-computational gaps from secret leakage"). **[CHECK]**

6. **Kikuchi hierarchy** (Wein–El Alaoui–Moore arXiv:1904.03858) gives subexponential-time algorithms above the spectral-but-below-SoS threshold; not polynomial but informs the gap structure. **[CHECK]**

7. **2024–2025 frontier:** SoS / LDLR refinements continue (Bafna–Hopkins; Barak–Hopkins–Hu line). **Specific 2024–2025 results not pre-loaded in this sandbox**; flagged for live verification.

8. **Substrate gap (closed by fire #43).** The dataclass needed is `GenericityAlmostEverywhereCert` (full-measure subset claim with measure-zero exception locus) plus `PhaseTransitionThreshold` (parameter axis with dual-threshold gap) plus `AlgorithmThresholdCert` (method × threshold × success-probability). T#73 is the canonical instance of all three composing.

## Claimed arXiv IDs (re-verify all)

`1411.1076` Richard–Montanari · `1507.03269` Hopkins–Shi–Steurer · `1604.03423` Hopkins–Schramm–Shi–Steurer · `1610.07477` Ma–Shi–Steurer SoS tensor decomp · `1907.11636` Kunisky–Wein–Bandeira LDLR notes · `1904.03858` Wein–El Alaoui–Moore Kikuchi · `2005.08099` Brennan–Bresler reductions · Hopkins thesis Cornell 2018 (no arXiv). **All [CHECK].**

---

## 1. Problem Statement

Fix integers n ≥ 1 and d ≥ 3 (d = 2 reduces to standard PCA and is excluded — there is no statistical-vs-computational gap at d = 2 in this model). The **spiked tensor model** is

  T = λ · v^{⊗d} + W   ∈ (ℝ^n)^{⊗d}

where v ∈ S^{n−1} is an unknown unit-norm "signal" direction; W is a tensor of i.i.d. N(0, 1) entries; λ > 0 is the **signal-to-noise ratio**.

**Recovery task.** Given T, output v̂ ∈ S^{n−1} with |⟨v̂, v⟩|² above some threshold. The **detection task** is the easier sibling: distinguish H_0 : T = noise from H_1 : T = signal + noise.

**The threshold question (T#73 / sub-Wigner spike model):** characterize sharply

- The **statistical (information-theoretic) threshold** λ_stat(n, d): below it, *no* algorithm can recover v with non-trivial probability.
- The **computational threshold** λ_comp(n, d): below it, *no polynomial-time algorithm* can recover v (under conjectures or in restricted computational models).

For d ≥ 3 the problem is conjectured to exhibit a **strict computational-statistical gap**, λ_comp / λ_stat → ∞ as n → ∞.

## 2. Status & Bounds

**Statistical threshold.** Under standard normalization, λ_stat = Θ(1) (constant order, independent of n) for d = 3. PATTERN_CONDUCTOR_CONFOUND: under alternate normalization, λ_stat ≍ √n.

**Computational threshold (conjectured).** λ_comp ≍ n^{(d−2)/4} relative to natural unrescaled normalization. For d = 3: λ_comp ≍ n^{1/4}; for d = 4: λ_comp ≍ n^{1/2}; for d → ∞ the gap explodes.

**Algorithm zoo:**
1. **Maximum-likelihood / unfolding-spectral** (Richard–Montanari 2014): λ ≳ n^{(d−1)/2}.
2. **Tensor power method** (Richard–Montanari 2014): λ ≳ n^{(d−1)/2}/poly with random init.
3. **AMP / TAP iterations** (Lesieur–Miolane–Krzakala et al.): match the spectral threshold.
4. **Sum-of-squares** (Hopkins–Shi–Steurer 2015; HSSS 2016 STOC; MSS 2016): degree-q SoS gives polynomial-time at λ ≳ n^{d/4}·polylog(n)/q.
5. **Kikuchi hierarchy** (Wein–El Alaoui–Moore 2019): subexponential-time interpolating the gap.
6. **Spectral methods on higher unfoldings** (HSSS 2016 STOC): match SoS at constant degree.

**Lower bounds:**
- **SoS lower bounds** (Hopkins thesis 2018; HKPRSS line): SoS hierarchy at degree O(log n / log log n) does not solve tensor PCA below conjectured threshold. Unconditional within SoS class, not classical NP-hardness.
- **Low-degree likelihood ratio (LDLR)** (Kunisky–Wein–Bandeira 2019 survey): degree-D = O(log n) polynomials of T cannot recover v below conjectured threshold.
- **Reductions** (Brennan–Bresler 2020): average-case reductions from planted clique to tensor PCA.

**Open / unconditional gaps:** No NP-hardness reduction. No matching SoS upper bound at precise constant. The "low-degree conjecture" itself is open. Sharp constants for d ≥ 5 unknown.

## 3. Literature

**Foundational:**
- Richard, Montanari. *A statistical model for tensor PCA.* NeurIPS 2014, arXiv:1411.1076. **[Origin paper.]**
- Anandkumar, Ge, Hsu, Kakade, Telgarsky. *Tensor decompositions for learning latent variable models.* JMLR 2014.

**SoS / spectral algorithms:**
- Hopkins, Shi, Steurer. *Tensor PCA via sum-of-squares proofs.* COLT 2015, arXiv:1507.03269 [CHECK].
- Hopkins, Schramm, Shi, Steurer. *Fast spectral algorithms from sum-of-squares proofs.* STOC 2016, arXiv:1604.03423 [CHECK].
- Ma, Shi, Steurer. *Polynomial-time tensor decompositions with sum-of-squares.* 2016, arXiv:1610.07477 [CHECK].
- Hopkins, Kothari, Potechin, Raghavendra, Schramm, Steurer line; Hopkins thesis Cornell 2018.

**LDLR framework:**
- Hopkins. *Statistical inference and the sum of squares method.* PhD thesis, Cornell 2018.
- Kunisky, Wein, Bandeira. *Notes on computational hardness of hypothesis testing.* 2019, arXiv:1907.11636 [CHECK].

**Subexponential algorithms:**
- Wein, El Alaoui, Moore. *The Kikuchi hierarchy and tensor PCA.* FOCS 2019, arXiv:1904.03858 [CHECK].

**Reductions:**
- Brennan, Bresler. *Reducibility and statistical-computational gaps from secret leakage.* 2020, arXiv:2005.08099 [CHECK].

**Statistical-physics replica predictions:**
- Lesieur, Miolane, Krzakala, Zdeborová. Various 2017–2019 papers giving sharp constants for symmetric tensor PCA at d = 3, 4. Predictions later proved rigorously by Mourrat / Barbier–Macris / Lelarge–Miolane around 2017–2019 [CHECK].

**Recent SoS hierarchy (2024–2025):** Bafna–Hopkins–Hu and Barak–Hopkins–Hu lines. Specific 2024–2025 papers not pre-loaded in this sandbox.

**Tools:** TensorLy; PyTorch / numpy.einsum; SDPA / Mosek / SCS; SoS toolkits (NCSOS.jl); cotengra / opt_einsum.

## 4. Attack Vectors

T#73 is **distributional** (not algebraic).

**Algorithmic attacks (upper bounds on λ_comp):**
- **(A) Tensor power method.** P15. Iterative refinement.
- **(B) AMP / TAP / message passing.** P15 + statistical-physics-import.
- **(C) Spectral methods on unfoldings.** P15 + P04. Achieves λ ≳ n^{(d−1)/2}.
- **(D) Sum-of-squares.** P22-adjacent. Degree-4 SoS achieves conjectured threshold up to polylog.
- **(E) Kikuchi hierarchy / cluster expansions.** Statistical-physics-imported subexponential.

**Lower bounds (within computational class):**
- **(F) SoS lower bounds.** Show degree-d SoS pseudo-distributions exist that are indistinguishable from planted below threshold.
- **(G) Low-degree likelihood ratio.** Show LDLR norm at degree D bounded below threshold.
- **(H) Average-case reductions.** Brennan–Bresler line.

**Cross-paradigm interactions:**
- **P22 (Polynomial method on signed graphs):** SoS arguments are polynomial-method-shaped — pseudo-distributions are signed measures over polynomial space.
- **P25 (Pivotal-Negative-Result):** **DISTINGUISH.** SoS / LDLR lower bounds are *constructive negative results within a fixed computational hierarchy*, not theorem-level NP-hardness. Substrate should encode them as **TIER-D AlgorithmThresholdCert with `success_prob → 0` annotation**, not as P25 reorienting lemmas. **Flag P25b — Hierarchy-Internal Hardness** as candidate paradigm refinement.
- **P28 (Asymptotic spectrum):** scaling exponents live in adjacent space.
- **P30 (TensorNetwork):** algorithmic methods can be re-expressed as contractions.
- **P15 (Multilinear decomposition):** base object.

**Candidate new attack patterns:**
- *Hierarchy-internal hardness (P25b).* SoS / LDLR / low-degree-class hardness statements within a fixed computational hierarchy. Distinct from theorem-level negative results (P25) and from cohomological obstruction (P02). Worth a paradigm slot if more such patterns aggregate (sparse PCA, planted clique, SBM detection share this shape).
- *Replica-symmetry-driven prediction.* The statistical-physics replica method predicts thresholds rigorously verifiable post-hoc. Substrate has no place for "replica-symmetric prediction" as typed claim — possibly a Tier-D specialization.

## 5. Substrate Encoding

**Direct map: Tier-D `GenericityAlmostEverywhereCert` + `PhaseTransitionThreshold` + `AlgorithmThresholdCert` composing.** Substrate-tester fires #43 + #45 already converged.

```python
class ThresholdRegime(str, Enum):
    STATISTICAL = "statistical"
    COMPUTATIONAL = "computational"
    ALGORITHMIC = "algorithmic"
    HIERARCHY_INTERNAL = "hierarchy"

@dataclass(frozen=True)
class PhaseTransitionThreshold:
    parameter_axis: str               # "lambda" / "SNR" / "n^alpha"
    threshold_value_expr: str         # symbolic: "n^{(d-2)/4}", "sqrt(n)", "1"
    regime_below: str
    regime_above: str
    semantic_class: ThresholdRegime
    normalization_id: str             # CRITICAL — names the noise scaling
                                      # PATTERN_CONDUCTOR_CONFOUND firewall
    proof_status: Literal["proved", "conjectured", "predicted_replica"]
    references: tuple[str, ...] = ()

@dataclass(frozen=True)
class AlgorithmThresholdCert:
    method_name: str
    method_spec_ref: str
    threshold: PhaseTransitionThreshold
    success_prob: float
    sample_size_required: Optional[int]
    hierarchy_degree: Optional[int]   # SoS degree, LDLR degree
    proof_status: Literal["proved_upper", "proved_lower",
                          "conjectured", "predicted_replica"]
    references: tuple[str, ...] = ()

@dataclass(frozen=True)
class GenericityAlmostEverywhereCert:
    ambient_distribution: str
    generic_property: str
    measure_zero_exception_locus: str
    recovery_threshold: Optional[PhaseTransitionThreshold] = None
    references: tuple[str, ...] = ()

@dataclass(frozen=True)
class TensorPCAInstance:
    n: int
    d: int
    lambda_snr: float | str
    noise_distribution: str
    normalization_id: str
    spike_direction_distribution: str
    statistical_threshold: PhaseTransitionThreshold
    computational_threshold: PhaseTransitionThreshold
    algorithm_certs: tuple[AlgorithmThresholdCert, ...]
    genericity_cert: Optional[GenericityAlmostEverywhereCert] = None
    domain_docstring: dict = field(default_factory=dict)
```

**Why this shape:**
- Dual-threshold structure (statistical vs computational) is *the* point of T#73; flattening to single threshold is substrate-grade error.
- `normalization_id` is the **conductor firewall** — every threshold quoted must travel with it.
- `hierarchy_degree` distinguishes SoS-degree-4 from SoS-degree-8 from LDLR-degree-D.
- `GenericityAlmostEverywhereCert` records the genericity-of-spike-direction claim with measure-zero exceptional locus.

**Substrate gap closed by this encoding.** Pre-fire-43 substrate had no place for "phase-transition-threshold-with-dual-regime" or "algorithm-success-guarantee-asymptotically." Both now first-class.

**Substrate gap *not* closed.** No substrate primitive for **"hierarchy-internal lower bound"** as typed object. SoS / LDLR lower bounds currently encoded as `AlgorithmThresholdCert` with `success_prob = 0`, but this conflates (a) the algorithm fails, and (b) the algorithm fails *because we proved it cannot succeed within this class*. Worth a follow-up substrate ticket if SoS / LDLR lower bounds appear in 2+ more catalog entries.

**Probe shape for Ergon:**
- Synthetic-spike-tensor generator parametrized by (n, d, λ, normalization).
- Algorithm bench: tensor power method, AMP, unfolding-spectral, degree-4 SoS (small n).
- Probe sweeps λ across the gap; substrate records `AlgorithmThresholdCert` instances; predicts threshold curves and compares to (n, d)-asymptotic scalings.
- **PATTERN_CONDUCTOR_CONFOUND warning:** finite-(n, d) thresholds will not match asymptotic scalings exactly.

## 6. Calibration Anchor Notes

**Substrate-grade vs textbook-trivial:**
- *Substrate-grade:* "Richard–Montanari 2014 (arXiv:1411.1076) introduced the spike model T = λ·v^⊗d + W; established λ_stat threshold scalings via MLE analysis; conjectured λ_comp ≍ n^{(d−2)/4} via tensor-power-method failure analysis."
- *Substrate-grade:* "Hopkins–Shi–Steurer 2015 SoS-degree-4 algorithm achieves λ ≳ n^{d/4} polylog; matched by HSSS 2016 STOC fast spectral methods."
- *Substrate-grade:* "The gap is conjectured-not-proved-NP-hard; SoS lower bounds are unconditional within SoS hierarchy; LDLR lower bounds are unconditional within low-degree polynomial class; classical complexity-theoretic hardness is open."
- *Textbook-trivial:* "Tensor PCA exhibits a statistical-vs-computational gap." True but unanchored.
- *Trap (PATTERN_BASE_RATE_NEGLECT):* treating "the gap" as universal feature. Most natural priors do *not* exhibit polynomial gaps; the spike model is special.
- *Trap (PATTERN_CONDUCTOR_CONFOUND):* quoting threshold scalings without quoting normalization.
- *Trap (PATTERN_RANK_PARITY_LEAK):* tensor PCA at d = 3 vs d = 4 vs d = 5 has different scalings; finite-n parity artifacts.

**Canonical authors:**
- **Montanari** — high canonical-popular (Stanford). Co-author: Richard.
- **Hopkins** — modern canonical for SoS / LDLR; thesis is primary structural reference.
- **Steurer** — co-author of essentially every modern SoS-tensor-PCA paper.
- **Schramm, Shi, Ma** — co-authors of specific SoS papers.
- **Bandeira** — canonical for high-dim probability and LDLR exposition.
- **Kunisky, Wein** — junior-canonical for LDLR notes.
- **El Alaoui, Moore** — canonical for Kikuchi-hierarchy line.
- **Brennan, Bresler** — canonical for average-case reductions.
- **Lesieur, Miolane, Krzakala, Zdeborová** — statistical-physics canonical; replica method.

**Fabrication risks:**
1. Mis-quoting threshold exponent. λ_comp ≍ n^{(d−2)/4} under standard rescaling.
2. Conflating gap with NP-hardness. No NP-hardness reduction exists.
3. Collapsing SoS-degree-4 with general SoS.
4. Inventing arxiv IDs.
5. Adding/dropping authors.
6. Citing 2024–2025 work without verification.
7. Missing the Wigner-vs-asymmetric distinction.
8. Treating replica-method predictions as conjectures (many now proved).

## 7. Cross-References

**Catalog:**
- **#24** Operator norm bounds for random symmetric tensors — supplies noise-term operator-norm bounds.
- **#66** Z-eigenvalue distribution — Z-eigenvalue formulation of tensor PCA.
- **#71** Sharp non-asymptotic operator-norm bounds — chaining program.
- **#72** Type-2 constant of tensors (Bandeira–Dmitriev) — explicitly listed by Bandeira–Dmitriev as resolving "tensor-PCA, Gaussian-process bounds simultaneously."
- **#74** Colored random tensor model continuum limit — adjacent infrastructure.

**Paradigms:**
- **P22** SoS hierarchy is polynomial-method-shaped.
- **P25** **DISTINGUISH.** SoS / LDLR hardness is hierarchy-internal. Flag **P25b (Hierarchy-Internal Hardness)** as candidate paradigm refinement.
- **P28**, **P30**, **P15** adjacent.

**In-repo:**
- `charon/diagnostics/substrate_tester_fire_43_results.json` — surfacing fire.
- `charon/diagnostics/substrate_tester_fire_45_results.json` — `GenericityAlmostEverywhereCert` introduction.
- `pivot/substrate_v3_proposal_stub_2026-05-08.md` — substrate v3 proposal.
- `aporia/meta/queue/techne_inbox.jsonl` ticket `T-2026-05-08-ST-fire43-001`.
- Sister reports: T#1, T#28, T#43, T#56, T#79, T#84, T#95.

**Tickets / open questions for follow-up:**
- **Live-verify all arXiv IDs** flagged [CHECK]. Recommend Gemini deep-research follow-up with web-fetch enabled.
- **2024–2025 SoS / LDLR refinements** specifically: Bafna–Hopkins–Hu and Barak–Hopkins–Hu lines.
- **Hierarchy-Internal Hardness paradigm proposal (P25b candidate).** If 2+ more catalog entries surface SoS-internal lower bounds, file a paradigm proposal in `aporia/docs/attack_angle_taxonomy.md`.

---

*Aporia, 2026-05-09. Sandboxed run — citations [CHECK]'d.*
