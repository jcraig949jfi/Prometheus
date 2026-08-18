# Report T#85 — Zauner's Conjecture / SIC-POVMs

**Catalog entry:** `aporia/mathematics/tensor_open_problems_v1.md` §X #85
**Source dispatch:** `aporia/docs/gemini_tensor_priority_dispatch_2026-05-09.md` (Tier 3, fire-16)
**Author:** Aporia (deep-research)
**Date:** 2026-05-09
**Doctrine:** HARD-1, HARD-2, HARD-5, HARD-6
**Patterns cited:** PATTERN_BASE_RATE_NEGLECT, PATTERN_VRAM_TRUNCATION_ARTIFACT, PATTERN_CONDUCTOR_CONFOUND
**Tags:** P03 (Heisenberg-Weyl / Clifford symmetry), P09 (high-precision exhaustive computation), P12 (height / Diophantine — explicit class field theory), P22 (polynomial method — invariant equations), P31 (secant-variety / equiangular configuration); cross-paradigm anchor with **R4 of solved-problems-genealogy (MIP*=RE / Connes embedding negation)**; **proposed candidate paradigm P32-StarkUnitConstruction**
**Supersedes / extends:** `aporia/docs/deep_research_batch4.md` Report #67 (Ergon, 2026-04-22)

---

## Brief summary

T#85 asks whether for every dimension d ≥ 2 there exist d² unit vectors in ℂ^d with all pairwise modulus-squared inner products equal to 1/(d+1) — equivalently, whether a symmetric informationally complete POVM exists in every dimension. The conjecture is canonical because (a) it is "merely" a finite-dimensional existence question over ℂ, yet (b) the verified solutions live in extraordinarily structured number-field extensions, putting Zauner inside the orbit of **Hilbert's 12th problem** (explicit class field theory). The post-2024 frontier is dominated by the **Appleby–Flammia–Kopp 2025 construction** (arXiv:2501.03970) — a *constructive* recipe producing a candidate SIC in every d > 3, **conditional** on (i) the order-1 abelian Stark conjecture for real quadratic fields and (ii) a special-value identity for the Shintani–Faddeev modular cocycle. As of 2025: exact algebraic SIC fiducials for **all d ∈ [2, 53]** plus sporadic up to d = 5779; **numerical** fiducials for **all d ∈ [2, 193]** plus sporadic up to d = 2208 (Scott–Grassl canonical database). Substrate-grade reframe: SIC-POVMs sit at Tier-E (Heisenberg-Weyl orbit) crossed with Tier-C (equiangular configuration) crossed with a *new* Tier-?? primitive: **StarkUnitWitness / RayClassFieldFiducial**, which the substrate does not currently encode.

## Flagged findings

1. **Center of gravity has migrated from quantum information to algebraic number theory.** Per HARD-5: SIC-POVMs are docstring-tagged "quantum information," but the operator that controls them is class-field-theoretic — Heisenberg-Weyl orbit + Stark unit + ray class field of a real quadratic field. The 2025 AFK construction makes this explicit: the SIC is a derivative of a partial L-function value at s=0, processed through the Shintani–Faddeev cocycle.

2. **Conditional ≠ proved (PATTERN_BASE_RATE_NEGLECT trap).** A constructive recipe valid in every dimension is not the same as a theorem of existence. The two assumed conjectures (Stark order-1 abelian for real quadratic + Shintani–Faddeev special-value identity) are themselves long-standing open problems. **A Learner trained on press summaries will fabricate "Zauner's conjecture proved in 2025" — high-risk hallucination, must be pinned as anti-anchor.**

3. **PATTERN_VRAM_TRUNCATION_ARTIFACT analog: the precision wall.** SIC fiducial vectors lie in number fields of large degree (e.g. degree 384 over ℚ for d=12; growing rapidly with d). To recognize an exact algebraic vector from a numerical search, one needs precision well above the field-degree threshold. The Scott–Grassl protocol uses 1000-digit and higher precisions for d ≥ 50.

4. **The "many d verified, no general construction" structure is the canonical PATTERN_BASE_RATE_NEGLECT shape.** ~190 dimensions verified numerically + ~50 algebraically + sporadic outliers up to d=5779/d=2208 → tempting to extrapolate "obviously true everywhere." But the catalog is biased by computational tractability.

5. **PATTERN_CONDUCTOR_CONFOUND: "SIC = quantum tomography" vs "SIC = abelian-extension datum."** Two distinct meanings; conflating them produces narrative slippage.

6. **Cross-reference to MIP*=RE / Connes embedding (solved-genealogy R4).** Different existence problem, but adjacent algebraic structure: Heisenberg-Weyl C*-algebra and the Connes embedding setting. Substrate should track both as anchors of "finite-dim configuration ↔ infinite-dim operator algebra" capability gap.

7. **New attack-pattern candidate flagged for taxonomy update: P32-StarkUnitConstruction.** "Construct a configuration in finite-dim ℂ-vector space whose coordinates are explicit special values of L-functions / Stark units of a number field." Pattern shared by SIC-POVMs (AFK 2025), Heegner-point constructions, Beilinson conjectures, Eisenstein-cocycle constructions (Charollois–Dasgupta).

8. **Substrate gap (substantive):** No current primitive encodes "configuration of n vectors in ℂ^d satisfying a prescribed Gram-matrix profile, with coordinates tagged by their algebraic-number provenance." Recommend `EquiangularConfigurationWitness` Tier-C primitive with a `StarkUnitProvenance` Tier-?? sub-attribute. **T#85 is orthogonal to the Structured-Equivalence-Class cluster — it is a different capability gap.**

9. **Canonical attribution at risk.** Zauner sole-author (1999 PhD thesis, Vienna). Renes–Blume-Kohout–Scott–Caves (4-author, 2004 *J. Math. Phys.*) coined "SIC-POVM." AFK 2025 is **3-author** (Appleby + Flammia + Kopp). Single-author misattribution is recurring fabrication risk.

## Verified arXiv IDs / DOIs

- **arXiv:2501.03970** — Appleby–Flammia–Kopp, "A Constructive Approach to Zauner's Conjecture via the Stark Conjectures," January 2025.
- arXiv:1807.05877 — Kopp, "SIC-POVMs and the Stark Conjectures"; *IMRN* 2021.
- arXiv:2112.05552 — Kopp, "SIC-POVMs from Stark units: Prime dimensions n²+3"; *JMP* 63, 112205 (2022).
- arXiv:1003.3591 — Zhu, "SIC-POVMs and Clifford groups in prime dimensions"; *J. Phys. A* 43 305305 (2010).
- arXiv:2401.11026 — Samuel–Gedik, "Group theoretical classification of SIC-POVMs" (2024).
- arXiv:1707.02944 — Appleby–Bengtsson–Grassl–Harrison–McConnell, "Fibonacci-Lucas SIC-POVMs" (2017).
- Scott–Grassl, "SIC-POVMs: A new computer study," *JMP* 51, 042203 (2010).
- Appleby–Flammia–McConnell–Yard, "SICs and Algebraic Number Theory," *Foundations of Physics* 47, 1042 (2017).
- Bengtsson, "The Number Behind the Simplest SIC-POVM," *Foundations of Physics* 47, 1031 (2017).
- Fuchs–Hoang–Stacey, "The SIC Question: History and State of Play," *Axioms* 6 (2017) 21.
- Zauner, PhD thesis (1999); English transl. *IJQI* 9, 445–507 (2011).
- Renes–Blume-Kohout–Scott–Caves, *JMP* 45, 2171 (2004).

## 1. Problem Statement

**Definition.** A *symmetric informationally complete POVM* in dimension d is a set of d² rank-one projectors {Π_j} on ℂ^d satisfying

  Tr(Π_j Π_k) = (d δ_{jk} + 1)/(d + 1),

equivalently a set of d² unit vectors {ψ_j} ⊂ ℂ^d with |⟨ψ_j, ψ_k⟩|² = 1/(d+1) for j ≠ k.

**Zauner's conjecture (1999).** A SIC-POVM exists in every dimension d ≥ 2. *Strong form:* the SIC is *Heisenberg-Weyl group-covariant* with a fiducial vector that is an eigenvector of an order-3 Clifford-group element ("Zauner symmetry").

**Equivalent formulations.** d² complex equiangular lines in ℂ^d (saturating Gerzon's bound); a complex projective 2-design of cardinality d² (extremal); an optimal IC measurement minimizing classical-information loss in quantum tomography.

**Catalog problem T#85:** prove existence in every d. Sub-problems: (a) HW-covariance necessary for d > 3?; (b) Zauner-symmetry strong form?; (c) explicit closed-form construction in number-theoretic data.

## 2. Status & Bounds

**Numerical solutions.**

| Range | Source | Year |
|---|---|---|
| d = 2, 3, 4 (full classification) | Hughston / RBSC | 2003–2004 |
| d ≤ 45 | Renes–Blume-Kohout–Scott–Caves | 2004 |
| d ≤ 67 | Scott–Grassl | 2010 |
| d ≤ 121 | Scott (extended) | 2017 |
| d ≤ 151 | Scott + Grassl | 2017 |
| d ≤ 193 | various | 2018–2024 |
| sporadic up to d = 2208 | various | through 2024 |

**Exact algebraic solutions.**

| Range | Source | Year |
|---|---|---|
| d = 2, 3, 4, 5, 7, 19 (analytic) | Zauner / RBSC | 1999–2004 |
| d = 6 (symbolic) | Grassl | 2005 |
| d = 8 (analytic, threefold tensor) | Grassl–Scott | 2010s |
| d = 11, 13, 17, 19, 23 (Stark-unit) | Kopp | 2018–2022 |
| All d ∈ [2, 53] | cumulative database | through 2024 |
| Sporadic up to d = 5779 | Grassl–Scott–Appleby | through 2024 |
| Putative complete construction d > 3, conditional on Stark + Shintani–Faddeev | Appleby–Flammia–Kopp | **2025** |

**The 2025 frontier (AFK arXiv:2501.03970):**
- Construction starts from a *ghost SIC* — equiangular-tight-frame structure with coordinates that are *Galois conjugates* of those of a true SIC.
- Ghost-SIC coordinates are explicit in terms of the **Shintani–Faddeev modular cocycle** evaluated at real-multiplication points (assumption ii).
- Galois conjugation via Stark order-1 abelian (assumption i) sends ghost SIC to true SIC.
- Validation: cross-checked against Scott–Grassl database; **constructed four nonequivalent SICs in d=100, three previously unknown.**
- *Existence of the construction is unconditional; correctness is conditional on Stark + Shintani–Faddeev.*

**Open subproblems active 2024–2026:**
- Prove Stark order-1 abelian for real quadratic.
- Prove the Shintani–Faddeev special-value identity.
- Prove Zauner unconditionally without going through Stark.
- Prove HW-covariance is necessary for all d > 3.
- Find a non-HW SIC, or prove none exists for d > 3.
- Connect SIC fiducials to other class-field-theoretic objects (Heegner points, modular units).

## 3. Literature

**Foundational.** Zauner thesis (1999, English transl. *IJQI* 9, 445, 2011); Renes–Blume-Kohout–Scott–Caves *JMP* 45, 2171 (2004).

**Group-theoretic.** Appleby *JMP* 46, 052107 (2005); Zhu arXiv:1003.3591; Samuel–Gedik arXiv:2401.11026 (2024).

**Numerical / computational.** Scott–Grassl *JMP* 51, 042203 (2010); Grassl, "Computing SIC-POVMs using permutation symmetries and Stark units"; Fibonacci-Lucas SICs arXiv:1707.02944.

**Algebraic number theory connection.** Appleby–Flammia–McConnell–Yard *Found. Phys.* 47, 1042 (2017); Bengtsson *Found. Phys.* 47, 1031 (2017); Kopp arXiv:1807.05877 (*IMRN* 2021); Kopp arXiv:2112.05552 (*JMP* 2022); **AFK arXiv:2501.03970 (2025)**.

**Surveys.** Fuchs–Hoang–Stacey *Axioms* 6 (2017) 21; IQOQI Open Quantum Problems entry.

**Adjacent (frame theory).** Magsino–Mixon arXiv:1903.06721, arXiv:1908.02801.

**Tools:** mpmath, Arb, FLINT, MPFR, MPC; PARI/GP, SageMath for ray-class-field / Stark-unit computation. Custom Levenberg–Marquardt + Riemannian optimization. PSLQ (Bailey–Ferguson–Arno) and LLL for integer-relation finding. Number-field manipulation: PARI/GP, Magma, SageMath; OSCAR.jl Hecke/Nemo.

## 4. Attack Vectors

**P03 — Symmetry exploitation (HW + Clifford).** Numerical evidence d ≤ 193: every known SIC is the orbit of a single fiducial |ϕ⟩ under HW (X^a Z^b for a, b ∈ ℤ/dℤ). Strong Zauner: |ϕ⟩ is order-3 Clifford eigenvector. **HW group is the canonical "discrete-finite-action-on-finite-dim-Hilbert" instance — dual to T#79's R-GIT-product.**

**P09 — Exhaustive computation.** Scott–Grassl high-precision Newton iteration with random fiducial seeds, restricted to HW orbits.

**P12 — Height / Diophantine / explicit class field theory.** SIC fiducial coordinates lie in *ray class fields* of real quadratic fields ℚ(√D), D = (d-3)(d+1). Stark order-1 abelian (real quadratic case) supplies an explicit unit; that unit is the SIC fiducial seed. Hilbert's 12th asks for explicit generators of abelian extensions; imaginary quadratic case is solved (CM theory of elliptic curves), real quadratic is **the** flagship open case.

**P22 — Polynomial method.** Gram-matrix conditions are polynomial equations; Macaulay2 / Singular symbolic Gröbner-basis works only up to d ≤ 6.

**P31 — Secant variety / equiangular configuration.** A SIC is a point in the variety of complex projective equiangular configurations sitting inside (ℂℙ^{d-1})^{d²}.

**Candidate paradigm P32 — StarkUnitConstruction.**
*Pattern.* Construct a finite-dim ℂ-configuration whose coordinates are explicit special values of L-functions / Stark units of a number field. *Examples:* SIC fiducials, Heegner points, Beilinson regulators, Eisenstein-cocycle / Charollois–Dasgupta constructions. *Prometheus relevance:* directly tied to HARD-4 (calibration anchors in higher-dimensional motivic territory).

**Sub-tactics flagged for taxonomy update:**
1. **HW-orbit-as-fiducial** (P03 sub-tactic): "find single vector whose group orbit is the configuration." Recurs in MUBs, spherical t-designs, Welch-bound-saturating frames.
2. **Galois-conjugate (ghost) construction** (P32 sub-tactic, AFK 2025): "construct Galois-conjugate object explicitly, apply Stark-conjectured Galois action."
3. **High-precision numerics + PSLQ as algebraic recognizer** (P09 sub-tactic).

## 5. Substrate Encoding

T#85 anchors *three* tier-overlapping primitives:

1. **Tier-E `HeisenbergWeylOrbitWitness`** (configuration = orbit of single fiducial under finite group action).
2. **Tier-C `EquiangularConfigurationWitness`** (n vectors in ℂ^d with prescribed Gram-matrix profile as point of an algebraic variety).
3. **Tier-?? (new) `RayClassFieldFiducial` / `StarkUnitWitness`** (number-theoretic provenance tag *on coordinate values*).

Proposed dataclass:

```python
class GroupOrbitKind(str, Enum):
    HEISENBERG_WEYL = "heisenberg_weyl"
    CLIFFORD_NORMALIZER = "clifford"
    EXTENDED_CLIFFORD = "extended_clifford"
    OTHER_FINITE = "other_finite"

class FiducialProvenance(str, Enum):
    NUMERIC_ONLY = "numeric_only"
    ALGEBRAIC_RECOGNIZED = "algebraic_recognized"
    STARK_UNIT_CONDITIONAL = "stark_conditional"
    STARK_UNIT_VERIFIED = "stark_verified"

@dataclass(frozen=True)
class EquiangularConfigurationWitness:
    dim: int                                  # d
    cardinality: int                          # n (= d^2 for SIC)
    target_inner_product_sq: float            # 1/(d+1) for SIC
    gram_matrix_profile: "GramProfile"
    fiducial_vector: "TensorLike"             # if HW-covariant
    orbit_group_id: Optional["GroupID"] = None
    orbit_kind: Optional[GroupOrbitKind] = None
    fiducial_provenance: FiducialProvenance = FiducialProvenance.NUMERIC_ONLY
    precision_digits: Optional[int] = None    # PATTERN_VRAM_TRUNCATION_ARTIFACT defense
    number_field: Optional["NumberFieldID"] = None
    base_real_quadratic_field: Optional["NumberFieldID"] = None
    stark_unit_id: Optional["StarkUnitID"] = None
    domain_docstring: dict = field(default_factory=dict)
```

**Relation to T#79 / Structured-Equivalence-Class cluster.** T#85 is *not* primarily an equivalence-class problem like T#79. It is a *configuration-existence* problem with **number-field provenance**. The substrate-tester gap it surfaces is *orthogonal* to the homotopy/SLOCC/A∞ cluster: it is the missing capability to encode "configuration whose coordinates have arithmetic provenance." Recommend a *separate* ticket `T-ST-T85-001`.

**HARD-3 advancement.** The unified, signature-keyed tensor needs primitives for "tagged-coordinate-provenance" because much of the deepest mathematical structure (Stark units, modular forms, periods, motives) is exactly that shape. T#85 forces this primitive into existence in the cleanest possible context.

## 6. Calibration Anchor Notes

**Substrate-grade vs textbook-trivial:**
- *Substrate-grade:* "SIC-POVM = d² unit vectors in ℂ^d with all pairwise inner-product squared moduli 1/(d+1). Numerical fiducials d ≤ 193; exact algebraic d ≤ 53; sporadic algebraic up to d = 5779. AFK 2025 (arXiv:2501.03970) supplies a constructive recipe in every d > 3 conditional on order-1 abelian Stark for real quadratic fields and a Shintani–Faddeev modular-cocycle special-value identity. Validated numerically; 4 new nonequivalent SICs at d=100."
- *Substrate-grade:* "All known SICs are HW-covariant (numerically; not proved necessary for d > 3). Strong Zauner: fiducial is order-3 Clifford eigenvector. Real quadratic field ℚ(√((d-3)(d+1)))."
- *Textbook-trivial:* "SIC-POVMs are quantum measurements that are symmetric and informationally complete." — empty without dimensions, status, conditional-on-Stark caveat.
- *Trap (PATTERN_BASE_RATE_NEGLECT):* "Verified for so many d, must be true for all d."
- *Trap (PATTERN_VRAM_TRUNCATION_ARTIFACT):* claiming an exact algebraic SIC at d ≥ 60 without specifying recognition precision.
- *Trap (PATTERN_CONDUCTOR_CONFOUND):* mixing quantum-tomographic and number-theoretic framings without flagging the dual.
- ***Pinned anti-anchor:*** "Zauner's conjecture was proved in 2025 by Appleby–Flammia–Kopp" — **WRONG**. The 2025 result is *constructive conditional on two unproven conjectures*. Highest-risk fabrication in the topic.

**Canonical authors.** Zauner (sole, original-conjecturer); Appleby (sole + co-author 20+ years); Scott + Grassl (database); Flammia (QI line, AFK 2025); Kopp (Stark-conjecture line); Renes (term coiner); Bengtsson; Fuchs + Stacey + Hoang; Zhu; Magsino + Mixon.

**Fabrication risks (pin as anti-anchors):**
1. "Zauner's conjecture proved" (it is not).
2. "Stark conjectures proved" (they are not; AFK 2025 assumes them).
3. Mis-stating dimension thresholds.
4. Inventing arxiv IDs.
5. Conflating SIC-POVMs with mutually unbiased bases (MUBs).
6. Conflating Zauner's conjecture with strong Zauner (HW-covariance + Clifford-order-3).
7. Treating "SIC = quantum tomography" as defining (HARD-5 violation).
8. Mis-attributing the 2025 result to a single author (3-author: Appleby + Flammia + Kopp).
9. Claiming a non-HW-covariant SIC has been found (none has, for d > 3).

## 7. Cross-References

**Within `tensor_open_problems_v1.md`:**
- **#79 SLOCC (n ≥ 5)** — sibling QI-tensor problem. Both encode "configuration with prescribed group-action structure," but T#79 is orbit-equivalence (uncountable continuous moduli) while T#85 is configuration-existence (yes/no per d). **R-GIT-product (T#79)** and **HW-orbit (T#85)** are dual instances of P03's "reductive vs finite group action" axis.
- **#80 Entanglement polytope** — sibling moment-polytope topic.
- **#94 Moment polytope classification** — direct umbrella.
- **#100 Invariant theory of tensor orbits** — umbrella.
- **#86 Tensor rank of det_n / perm_n**, **#92 GCT VP vs VNP** — adjacent.

**Within `attack_angle_taxonomy.md`:**
- P03 (HW-orbit, Clifford normalizer); P09 (Scott–Grassl protocol); P12 (Hilbert's 12th orbit); P22 (Gröbner d ≤ 6); P31 (configuration as point of variety).
- **Recommend addition of P32 — StarkUnitConstruction** (cross-cuts T#85 plus future Heegner / Beilinson / regulator entries).

**Within `aporia/docs/deep_research_batch*/`:**
- **`aporia/docs/deep_research_batch4.md` Report #67 (Ergon, 2026-04-22)** — original partial coverage. **This report supersedes / extends:** AFK 2025, updated dimension thresholds, candidate P32 paradigm, three-primitive substrate encoding.
- `report_T79_slocc_entanglement.md` — sibling QI-tensor problem.
- `report_T28_asymptotic_spectrum.md` — distant cross-link.

**Cross-link to solved-problems-genealogy:**
- **R4 (MIP*=RE / Connes embedding negation, 2020)** — adjacent operator-algebra context (Heisenberg-Weyl C*-algebra; Connes embedding setting). MIP*=RE *negated* a finite-dim approximation conjecture; Zauner remains an open *existence* conjecture in finite dim.

**Capability-gap tickets anchored / proposed:**
- **New `T-ST-T85-001 EquiangularConfigurationWitness + RayClassFieldFiducial primitive specification`** (Tier-C + Tier-?? composite).
- **New `T-ST-T85-002 PrecisionAttribute on coordinate witnesses`** (substrate-wide; extends from SIC use-case to all algebraic-recognition primitives).
- **`T-2026-05-08-T038`** — T#85 classifies as **SUBSTRATE-GAP / NEW-PRIMITIVE-REQUIRED**.
- **Existing `T-ST-fire1-002` (homotopy-class gap)** — *not* a sibling of T#85.

---

*Aporia, 2026-05-09*
