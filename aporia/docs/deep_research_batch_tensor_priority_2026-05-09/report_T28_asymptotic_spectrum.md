# Report T#28 — Asymptotic Spectrum of Tensors (Strassen)

**Catalog entry:** `aporia/mathematics/tensor_open_problems_v1.md` §I/II #1, #2, #7, #8, #16, #17 (T#28 = catalog entry #16, "Subrank–rank duality / asymptotic spectrum description")
**Source dispatch:** `aporia/docs/gemini_tensor_priority_dispatch_2026-05-09.md` (Tier 1, fire-2)
**Author:** Aporia (deep-research)
**Date:** 2026-05-09
**Doctrine:** HARD-1, HARD-2, HARD-3, HARD-5, HARD-6
**Patterns cited:** PATTERN_BASE_RATE_NEGLECT, PATTERN_CONDUCTOR_CONFOUND, PATTERN_RANK_PARITY_LEAK
**Tags:** P28 (THE paradigm — this report provides P28's literature backing), P22, P25, P27, P29, P30, P31

---

## Brief summary

T#28 / catalog #16 / paradigm P28 is the **meta-organizer of tensor pre-orders**. Five named monotone-functional families are known over ℂ after 40 years (matrix flattenings; Strassen's 1991 support functionals; Razborov-style rank functions; slice rank and the rank-zoo; Christandl–Vrana–Zuiddam quantum functionals). Quantum functionals (CVZ 2017/2023) are the only family confirmed universal. The 2024 result Christandl–Hoeberechts–Nieuwboer–Vrana–Zuiddam (arXiv:2411.15789, STOC 2025) — title "Asymptotic tensor rank is characterized by polynomials" — is **VERIFIED live**: asymptotic tensor rank is computable from above by evaluating finitely many polynomials, sublevel sets are Zariski-closed (matrix-rank-like), and the value set is well-ordered (any sufficiently-close upper bound on ω "snaps" to ω). PATTERN_BASE_RATE_NEGLECT and PATTERN_CONDUCTOR_CONFOUND are the load-bearing fabrication-firewalls.

## Flagged findings

1. **2024 result confirmed exact, 5-author.** arXiv:2411.15789, Christandl, Hoeberechts, Nieuwboer, Vrana, Zuiddam, Nov 24 2024. Three theorems: polynomial characterization of asymptotic rank from above; Zariski-closed sublevel sets; well-ordered value set (discreteness extended from finite fields to ℂ). Polynomials are non-constructive — the existence proof does not exhibit them. Major fabrication risk: dropping/adding authors.
2. **A 2026 collapse:** arXiv:2601.21553 shows Strassen's support functionals coincide with quantum functionals on the oblique-tensor sub-semiring. The catalog's "5 known families" is structurally 4 (or fewer) on overlapping regions. A Learner reciting "5 independent families" is missing this collapse.
3. **A 2026 separation:** arXiv:2604.18283 (Botero–Christandl–Fraser–Leigh–Nieuwboer) shows lower quantum functionals are *not* universal at order ≥ 4; upper and lower variants disagree generically; they coincide on laminar weightings. Lower-quantum-functional universality is refuted; new spectral points populated on the laminar region.
4. **Universal-sequence handle:** Kaski–Michałek arXiv:2404.06427 (ITCS 2025) constructs explicit zero-one universal sequences whose asymptotic rank captures worst-case σ(d). A constructive route around the spectrum-description problem.
5. **Wigderson–Zuiddam survey** (final draft Oct 2023; 2025 BAMS update) is the canonical modern reference. Recasts Strassen's 1986–1991 series in partially-ordered-semiring generality with full duality theorem.
6. **Strassen original series verified:** *The asymptotic spectrum of tensors* J. Reine Angew. Math. 384 (1988) 102–152 [duality theorem]; *Relative bilinear complexity and matrix multiplication* Crelle 375/376 (1987) 406–443; *Degeneration and complexity of bilinear maps: some asymptotic spectra* Crelle 413 (1991) 127–180 [upper support functionals]. FOCS 1986 conference paper precedes.
7. **Substrate gap:** no existing primitive for "typed family of probes on a pre-order with internal coincidence/separation graph." Proposed `AsymptoticSpectrumMonotone` dataclass detailed in §5. This shape will likely recur for asymptotic-spectrum-of-graphs (Shannon capacity), asymptotic-spectrum-of-communication-complexity, etc. — generalize to `MonotoneFamily[Preorder]` once a second instance is needed.

## Verified arXiv IDs (re-verify any others a Learner emits)

`1709.07851` (CVZ universal points, JAMS 2023) · `1609.07476` (CVZ graph tensors) · `2411.15789` (CHNVZ 2024 polynomial characterization, STOC 2025) · `2404.06427` (Kaski–Michałek universal sequence, ITCS 2025) · `2604.18283` (BCFLN 2026 quantum functionals higher order) · `2601.21553` (support = quantum on oblique, 2026) · `2604.01386` (edge of asymptotic spectrum, 2026).

---

## Full report

### 1. Problem Statement

Let T denote the commutative semiring of complex tensors of fixed order (most often order-3) under direct sum (⊕) and tensor product (⊗), preordered by **restriction** ≤: write S ≤ T if S can be obtained from T by applying linear maps to each factor. Take the **asymptotic restriction** preorder ⪅: S ⪅ T iff S^{⊗n} ≤ T^{⊗(n+o(n))}.

Strassen's **asymptotic spectrum** X(T) is the set of all monotone semiring homomorphisms φ : (T, +, ·, ⪅) → (ℝ_{≥0}, +, ·, ≤). Each such φ is a **spectral point**.

Fundamental duality (Strassen 1988; Wigderson–Zuiddam 2023):

  R̃(T) = max_{φ ∈ X(T)} φ(T) ; Q̃(T) = min_{φ ∈ X(T)} φ(T)

The **explicit-description problem (T#28 / catalog #16):** give an explicit, complete description of all monotone semiring-homomorphisms in X(T) over ℂ.

**Currently known points:** (1) matrix flattenings (Strassen 1986/1988); (2) Strassen's upper/lower support functionals ζ^θ (Crelle 1991, defined on **oblique** tensors); (3) Razborov-style rank functions; (4) slice rank and rank-zoo cousins (Tao 2016 reformulation of Croot–Lev–Pach; Ellenberg–Gijswijt; partition rank Naslund 2017; analytic rank Lovett; geometric rank Kopparty–Moshkovitz–Zuiddam 2020); (5) **quantum functionals** F^θ — Christandl–Vrana–Zuiddam, STOC 2018 / J. Amer. Math. Soc. 36 (2023) 31–79 (arXiv:1709.07851), the first family of universal spectral points over ℂ, defined via quantum entropy / moment-polytope evaluation.

That is the entire structurally-distinct list as of 2026-05-09. **PATTERN_BASE_RATE_NEGLECT:** ~5 named monotones in 40 years; "we know most of the spectrum" framing is wrong.

### 2. Status & Bounds

**Known unconditionally over ℂ (order-3):**
- X(T) is a non-empty compact Hausdorff space (Strassen 1988 duality; Wigderson–Zuiddam 2023 §2–3).
- All five families above are monotone semiring-homomorphisms.
- Strassen support functionals are complete on the **oblique-tensor** sub-semiring; not complete on all of T (Strassen 1991).
- Quantum functionals are **universal** — defined on every tensor; parametric family indexed by probability distributions on subsets of legs (CVZ 2018/2023).
- ω = 2·σ(M⟨2⟩); current best ω ≤ 2.371552 (Vassilevska Williams–Xu–Xu–Zhou 2024). ω = 2 ⇔ Strassen's asymptotic rank conjecture for M⟨2⟩.

**Conditional / structural results (2024–2026 line):**

- **Christandl–Hoeberechts–Nieuwboer–Vrana–Zuiddam, arXiv:2411.15789, Nov 24 2024, STOC 2025.** *Verified.* Three theorems:
  1. **Polynomial characterization:** asymptotic tensor rank computable from above; for any r ∈ ℝ there is an algorithm that decides whether R̃(T) ≤ r by evaluating finitely many polynomials.
  2. **Zariski-closed sublevel sets:** {T : R̃(T) ≤ r} is Zariski-closed, mirroring matrix rank — even though defining polynomials are not exhibited.
  3. **Discreteness:** values of R̃ form a well-ordered subset of ℝ_{≥0}; any monotone-decreasing sequence stabilizes. Extends ITCS 2024 finite-field discreteness to ℂ.
  Operational consequence: any sequence of upper bounds on ω that gets sufficiently close must "snap" to it — the sub-2.5 hunt is asymptotically discrete.
- **Kaski–Michałek arXiv:2404.06427, ITCS 2025.** Explicit zero-one universal sequence 𝒰_d capturing worst-case σ(d) over all order-3 tensors of dim d. Handle for asymptotic rank conjecture from the universal-object side.
- **Botero–Christandl–Fraser–Leigh–Nieuwboer arXiv:2604.18283, 2026.** Upper and lower quantum functionals **do not generally coincide** for order ≥ 4; coincide on laminar weightings. Lower quantum functionals are *not* universal.
- **arXiv:2601.21553, 2026.** Strassen's support functionals coincide with quantum functionals on the oblique-tensor sub-semiring — collapses two of the "5 known points" into one structural family on the overlap.

**Open:** explicit description of *all* spectral points (T#28); Strassen's asymptotic rank conjecture (catalog #2); asymptotic restriction problem (catalog #8); border-rank multiplicativity (catalog #7); asymptotic subrank of small explicit tensors (catalog #17, including T_{cw,2}); whether CHNVZ's polynomials can be exhibited.

### 3. Literature

**Foundational (Strassen 1986–1991, all Crelle):**
- Strassen, *The asymptotic spectrum of tensors and the exponent of matrix multiplication*, Proc. 27th FOCS 1986, 49–54.
- Strassen, *Relative bilinear complexity and matrix multiplication*, J. Reine Angew. Math. 375/376 (1987) 406–443.
- Strassen, *The asymptotic spectrum of tensors*, J. Reine Angew. Math. 384 (1988) 102–152. [Duality theorem.]
- Strassen, *Degeneration and complexity of bilinear maps: some asymptotic spectra*, J. Reine Angew. Math. 413 (1991) 127–180. [Upper support functionals.]

**Modern survey:**
- Wigderson, A. & Zuiddam, J., *Asymptotic spectra: Theory, applications and extensions.* Final draft Oct 2023; updated Bull. Amer. Math. Soc. 2025 version on IAS site. **Canonical modern reference.**

**Quantum functionals / 2017+:**
- Christandl, Vrana, Zuiddam, *Universal points in the asymptotic spectrum of tensors*, arXiv:1709.07851; STOC 2018; J. Amer. Math. Soc. 36 (2023) 31–79.
- Christandl, Vrana, Zuiddam, *Asymptotic tensor rank of graph tensors: beyond matrix multiplication*, arXiv:1609.07476; computational complexity 27 (2018) 551–593.
- Zuiddam PhD thesis, *Algebraic complexity, asymptotic spectra and entanglement polytopes* (UvA 2018).

**2024–2026 frontier:**
- Christandl, Hoeberechts, Nieuwboer, Vrana, Zuiddam, *Asymptotic tensor rank is characterized by polynomials*, **arXiv:2411.15789**, STOC 2025. Verified 2026-05-09 via WebFetch.
- Kaski, Michałek, *A universal sequence of tensors for the asymptotic rank conjecture*, arXiv:2404.06427, ITCS 2025.
- *Discreteness of Asymptotic Tensor Ranks (Extended Abstract)*, LIPIcs ITCS 2024.
- Botero, Christandl, Fraser, Leigh, Nieuwboer, *On quantum functionals for higher-order tensors*, arXiv:2604.18283, 2026.
- *Strassen's support functionals coincide with the quantum functionals*, arXiv:2601.21553, 2026.
- *The edge of the asymptotic spectrum of tensors*, arXiv:2604.01386, 2026.

**Adjacent / applied:**
- Cohn–Umans group-theoretic framework (FOCS 2003).
- Vassilevska Williams; Williams; Duan–Wu–Zhou; VW–Xu–Xu–Zhou 2024 — laser-method ω bounds.
- Fawzi et al., *Discovering faster matrix multiplication algorithms with reinforcement learning*, Nature 2022 (AlphaTensor).
- Probabilistic refinement of asymptotic spectrum of graphs, Combinatorica 2020.

**Tools:** LiE, Symmetrica (rep theory / moment polytopes); SDPA, CVXPY, Mosek (quantum-functional SDPs); Macaulay2 (apolarity / scheme-theoretic obstructions); TensorLy, ITensor, opt_einsum, cotengra (tensor manipulation); PARI/GP (high-precision monotone evaluation).

### 4. Attack Vectors

T#28 *is* paradigm P28; this section provides P28's literature backing.

**Internal P28 attack patterns:**
- (A) **Quantum-entropy construction** (CVZ 2017/2023; BCFLN 2026 extension to laminar weightings on higher order). Active 2017–2026; expect more spectral-point families.
- (B) **Polynomial / Zariski-closure characterization** (CHNVZ 2024). Polynomials non-constructive; making them explicit is the next move.
- (C) **Universal-object construction** (Kaski–Michałek 2024) — explicit universal sequences witnessing worst-case σ(d).
- (D) **Coincidence theorems** (arXiv:2601.21553) — show distinct families coincide on a sub-semiring; reduces apparent richness, focuses search.
- (E) **Separation theorems** (arXiv:2604.18283) — show distinct families fail to coincide, producing new spectral points.

**Cross-paradigm interactions:**
- **P22** (polynomial method on F_q signed graphs) — supplies concrete bounds; P28 supplies the framework those bounds compose in.
- **P27** (slice rank / polynomial method on F_q) — each rank-zoo functional is a candidate spectral point; Lovett bound A ≤ S^d (catalog #13) is a spectrum-internal inequality.
- **P29** (border apolarity) — apolar-scheme obstructions give substrate-auditable lower bounds on candidate spectral-point values.
- **P30** (tensor network contraction) — bond-dimension / TT-rank are upper bounds on rank-like spectral points; reverse direction: spectrum constrains contractibility.
- **P31** (secant variety geometry) — defining equations of σ_r supply explicit polynomial certificates for spectral-point lower bounds; Young flattenings are a specific spectral-point family.
- **P15** (tensor decomposition) — produces witnesses; P28 is the asymptotic structure those witnesses live in.
- **P25** (pivotal negative result) — CHNVZ 2024 discreteness is structurally P25-shaped: a negative-flavored statement (you can't approximate ω arbitrarily closely from above without snapping) with positive structural consequences.

**Candidate new attack patterns (sub-tactics, not yet full paradigms):**
- *P-spectrum-functor hunt:* systematic search for monotone semiring-homomorphisms from candidate functor families (Schur–Weyl, Hecke-algebra invariants, free-probability moments). Track for recurrence across other pre-orders (graph asymptotic spectrum, communication complexity).
- *Discreteness-leveraged search:* use CHNVZ's well-ordering to prune algorithmic ω-improving search — once close enough you're at it. P28 + P09 sub-tactic.

### 5. Substrate Encoding

Proposed dataclass shape (substrate-side):

```python
# aporia/substrate/primitives/asymptotic_spectrum.py (proposed)
from dataclasses import dataclass, field
from typing import Callable, Literal, Optional
from enum import Enum

class PreorderKind(str, Enum):
    RESTRICTION = "restriction"          # Strassen's ≤
    ASYMPTOTIC_RESTRICTION = "asymp"     # ⪅
    DEGENERATION = "degeneration"        # Bini-style
    SUBRANK = "subrank"

class FunctionalStatus(str, Enum):
    KNOWN_MONOTONE = "monotone_proved"
    CONJECTURED_MONOTONE = "monotone_conj"
    PROVEN_UNIVERSAL = "universal_proved"
    OBLIQUE_ONLY = "oblique_only"           # Strassen support functionals
    LAMINAR_ONLY = "laminar_only"           # 2026 quantum functionals
    REFUTED = "refuted"

@dataclass(frozen=True)
class AsymptoticSpectrumMonotone:
    """Typed real-valued functional on a tensor pre-ordered semiring,
    candidate-or-proven member of Strassen's asymptotic spectrum.
    Per HARD-5: domain_docstring is a tag, not a coordinate.
    """
    name: str
    preorder: PreorderKind
    parameter_space: Optional[str]            # e.g. "Delta(2^{[n]})" laminar weightings
    evaluator: Callable[["TensorLike"], float]
    status: FunctionalStatus
    universality_domain: Optional[str]        # "all_complex_tensors" | "oblique" | "laminar" | None
    monotonicity_certificate: Optional[str]   # arxiv id or proof reference
    coincides_with: tuple[str, ...] = ()
    refuted_on: tuple[str, ...] = ()
    domain_docstring: dict = field(default_factory=dict)

@dataclass
class AsymptoticSpectrum:
    """X(T) for fixed tensor pre-ordered semiring. Open by construction."""
    semiring: str
    monotones: list[AsymptoticSpectrumMonotone]
    duality_witnessed: bool
    completeness_status: Literal["unknown", "complete_on_subsemiring",
                                  "incomplete", "complete"] = "unknown"

    def asymptotic_rank_upper_bound(self, T) -> float:
        """max over known monotones; LOWER bound on the true asymptotic
        rank since unknown monotones could be larger.
        PATTERN_BASE_RATE_NEGLECT: do NOT report as 'the' asymptotic rank."""
        return max(m.evaluator(T) for m in self.monotones
                   if m.status != FunctionalStatus.REFUTED)
```

**Why this shape:** spectrum *is* a set of typed functionals, not a number; `universality_domain` distinguishes oblique-only / universal / laminar-only structural roles; `coincides_with` directly encodes 2026 collapse theorems; `monotonicity_certificate` mandatory for substrate-grade promotion (HARD-4).

**Builds on / extends:** CoordinateChart (T030); Tier-D meta-primitive (GenericityAlmostEverywhereCert) — quantum functionals' laminar genericity is Tier-D-shaped; Tier-A++ TensorNetwork meta-primitive — bond-dim bounds upper-bound spectral points; TriangulationProtocol — independent monotones triangulating asymptotic-rank value, substrate-tester to verify non-bypass (per fire-17).

**Gap flagged:** substrate has no existing primitive for **meta-structure-as-typed-family-of-probes**. AsymptoticSpectrum is not a single value, functional, or coordinate chart — it's a typed, growable family with internal coincidence/separation graph. Likely recurs (Shannon-capacity asymptotic spectrum of graphs, communication complexity); generalize to `MonotoneFamily[Preorder]` once a second instance arrives.

**Probe shape for Ergon:** evaluate each registered monotone on fixed battery (M⟨n⟩, T_{cw,2}, T_{cw,q}, GHZ_n, W_n, generic random small-format) → confirm monotonicity / detect coincidences / score candidate monotones. **PATTERN_CONDUCTOR_CONFOUND warning:** finite-N probe values are NOT asymptotic-spectrum values; report finite-N value plus rate-of-convergence (or absence), never collapse.

### 6. Calibration Anchor Notes

**Substrate-grade vs textbook-trivial:**
- *Substrate-grade:* "Strassen 1988 (Crelle 384) duality gives X(T) compact Hausdorff non-empty; R̃(T) = max_{φ ∈ X(T)} φ(T) is a structural identity."
- *Substrate-grade:* "5 known families are not all independent — arXiv:2601.21553 (2026) shows support functionals = quantum functionals on oblique tensors."
- *Substrate-grade:* "CHNVZ arXiv:2411.15789 gives polynomial characterization, Zariski-closed sublevel sets, well-ordered value set." Distinguish from ITCS 2024 (finite-field predecessor).
- *Textbook-trivial:* "ω ≤ 2.371552 (Williams 2024)" — true but doesn't engage the spectrum question.
- *Trap (PATTERN_BASE_RATE_NEGLECT):* treating 5 families as "most" of the spectrum.

**Canonical authors at varying canonicality** (per `SESSION_SYNTHESIS_2026-05-07.md` axis):
- **Strassen** — founder, high canonical-popular.
- **Christandl, Vrana, Zuiddam** — modern co-authors of universality and 2024 polynomial characterization. Christandl carries QI cross-canonicality; Zuiddam thesis (UvA 2018) is primary structural source.
- **Wigderson** — co-author 2023 modern survey; Abel 2021 attaches popular weight; survey is canonical reference.
- **Hoeberechts, Nieuwboer** — junior 2024 co-authors; not yet canonical-popular.
- **Kaski, Michałek** — universal-sequence; canonical-academic, lower popular weight.
- **Bürgisser, Landsberg, Ikenmeyer** — adjacent canonical via algebraic-complexity textbook (BCS) and *Geometry and Complexity Theory*.
- **Cohn, Umans, Williams (Vassilevska Williams), Le Gall, Alman** — ω-bound canonical, asymptotic-spectrum-adjacent.

**Fabrication risks:**
1. **Mis-attributing 2024 result.** Authors exactly Christandl, Hoeberechts, Nieuwboer, Vrana, Zuiddam (5-author). Verified arXiv:2411.15789 WebFetch 2026-05-09. Adding/removing names = fabrication.
2. **Inventing functionals.** Spectrum has named families; do not invent fictitious "Smith functional." Route candidates through monotonicity-test gate.
3. **Conflating finite-N and asymptotic regimes.** PATTERN_CONDUCTOR_CONFOUND.
4. **Treating ω ≤ 2.371552 as a spectrum statement.** It is a *consequence* via duality applied to M⟨2⟩.
5. **Claiming Strassen's asymptotic rank conjecture is "almost proved."** It is not; CHNVZ 2024 gives discreteness and polynomial characterization, does not close the conjecture.
6. **Inventing arxiv IDs.** Verified: 1709.07851, 1609.07476, 2411.15789, 2404.06427, 2604.18283, 2601.21553, 2604.01386.
7. **PATTERN_BASE_RATE_NEGLECT framing inversion:** "the spectrum is well-understood" inverts the actual base rate.

**Per HARD-1/HARD-2:** no paper framing, no "publishable result" / "competitive with state-of-the-art" language. Per HARD-5: tensor / quantum-information / algebraic complexity labels are bibliography metadata; spectral structure is the math.

**Mandatory pattern citations (≥2):**
- **PATTERN_BASE_RATE_NEGLECT** — applied 4× above. Prototypical T#28 failure: ~5 named monotones / 40-year history / unknown spectrum cardinality.
- **PATTERN_CONDUCTOR_CONFOUND** — applied to finite-N vs asymptotic regime distinction. Two-track output mandatory.
- **PATTERN_RANK_PARITY_LEAK** — watch-pattern for rank-zoo numerical experiments (slice / partition / analytic / geometric carry parity / dimension features that can leak across degrees).

### 7. Cross-References

**Within `aporia/mathematics/tensor_open_problems_v1.md`:**
- **#1** matrix multiplication exponent ω — load-bearing instance; ω = 2 ⇔ M⟨2⟩'s spectral max equals 2.
- **#2** Strassen's asymptotic rank conjecture — strongest possible spectrum-collapse statement; implies ω = 2.
- **#7** border-rank multiplicativity under tensor product — characterizes when a candidate border-rank functional behaves multiplicatively (necessary for being a spectral point on the border-rank pre-order extension).
- **#8** asymptotic restriction problem — operational form of spectrum description; deciding S ⪅ T equivalently asks all spectral points satisfy φ(S) ≤ φ(T).
- **#16** subrank-rank duality / asymptotic spectrum description — **same as T#28** (dispatch numbering vs catalog numbering).
- **#17** asymptotic subrank of explicit tensors — concrete probes of unknown spectral points.
- Adjacent: **#3** (T_{cw,2}), **#5** (border rank M⟨n⟩), **#9** (restriction preorder small tensors), **#11** (laser-method limits), **#13–15** (slice-rank zoo, P27), **#18** (subspace rank), **#26–35** (defective Segre-Veronese, P31).

**Within `aporia/docs/attack_angle_taxonomy.md`:**
- **P28 Asymptotic Spectrum (Strassen)** — this report is P28's literature-and-substrate backing. Distinction from P04 (eigenvalue spectrum vs functional spectrum) sharpened by Strassen 1988 duality.
- P22, P27, P29, P30, P31 interactions in §4. P25 (pivotal negative): CHNVZ 2024 discreteness is P25-shaped. P15: P15 produces witnesses, P28 supplies asymptotic-invariant structure.

**Within `aporia/doctrine/critical_memories.md`:** HARD-1 (no paper framing) ✓; HARD-2 (no "publishable" language) ✓; HARD-3 (tensor first; T#28 is the meta-tool); HARD-5 (domains as docstrings; no "bridges QI and complexity" framing); HARD-6 (attacking tools-we-need-most; the failure mode — 40 years, 5 families, no full description — is itself substrate-grade guidance).

**Within `aporia/docs/deep_research_master_index.md`:** T#1 ω report pairs with this (T#28 framework, T#1 instance); T#43 (de Silva-Lim) orthogonal but related — asymptotic spectrum cleanly handles ill-posedness via border-rank closure.

**Capability-gap tickets potentially anchored:** Tier-D (GenericityAlmostEverywhereCert) — quantum-functionals laminar genericity (BCFLN 2026); Tier-A++ (TensorNetwork) — TT/MPS bond-dim upper-bounds spectral points; new candidate **T-ST-T28-001 AsymptoticSpectrumMonotone primitive** (file when Tier-D / A++ tickets need it as dependency).

---

*Aporia, 2026-05-09*
