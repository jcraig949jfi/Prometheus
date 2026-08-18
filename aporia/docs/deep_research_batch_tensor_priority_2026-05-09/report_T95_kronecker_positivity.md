# Report T#95 — Kronecker Coefficient Vanishing / Positivity

**Catalog entry:** `aporia/mathematics/tensor_open_problems_v1.md` § XII, entry 95
**Tier mapping:** Tier-E meta-primitive (`RepresentationTheoreticInvariant`)
**Substrate-tester anchor:** Fire #44 (2026-05-08), `T-2026-05-08-ST-fire44-001`
**Dispatch:** `aporia/docs/gemini_tensor_priority_dispatch_2026-05-09.md`, Tier-2 pick #6
**Doctrine:** HARD-1, HARD-2, HARD-5, HARD-6
**Author:** Aporia, 2026-05-09
**Patterns cited:** PATTERN_BASE_RATE_NEGLECT, PATTERN_RANK_PARITY_LEAK, PATTERN_CONDUCTOR_CONFOUND
**Tags:** P03, P22, P27, P28, P30 + candidate **Modular Saturation / Decomposition-Matrix Lifting** (P32 candidate — synthesis must reconcile with T#1 and T#56's P32 candidates)

---

## Brief summary

T#95 (Kronecker coefficient vanishing/positivity) is `#P`-hard to compute, `NP`-hard to test for positivity (Ikenmeyer–Mulmuley–Walter 2017), and the related `S_n`-character positivity is `PH`-hard (Ikenmeyer–Pak–Panova 2024) — falsifying Mulmuley's GCT `PH1` conjecture. Special-shape polynomial cases exist (two-row × two-row Briand–Orellana–Rosas; Barvinok-style fixed-rank Christandl–Doran–Walter), and Pak–Panova–Swanson 2025 give new restricted positive rules. **Saxl (T#99) is resolved unconditionally (Sellke 2025/2026).** Ikenmeyer–Panova 2024 (Forum Math Pi) collapsed reduced Kronecker into ordinary Kronecker complexity-wise.

## Flagged findings

- **F-T95-01** Tier-E primitive specification ready (dataclasses for `PartitionObject` / `IrreducibleSnRep` / `KroneckerInvariant` / `PositivityWitness` / `VanishingCertificate`); ready for Techne T038 ingestion.
- **F-T95-02 — calibration update required:** T#99 Saxl status flips `open` → `resolved (Sellke 2025)`. `tensor_open_problems_v1.md` and any prompts citing Saxl-as-open are stale.
- **F-T95-03 — calibration update required:** Mulmuley's `PH1` (Kronecker positivity in P) is dead since IMW 2017; any agent prompt using it as a working assumption is in HARD-2 territory.
- **F-T95-04** Reduced ≡ ordinary Kronecker in complexity (Ikenmeyer–Panova 2024) — should not encode as a separate substrate primitive.
- **F-T95-05 — P32 candidate** "Modular Saturation / Decomposition-Matrix Lifting" not in P01–P31; recommend taxonomy review.
- **F-T95-06** Bravyi et al. 2025 quantum polynomial-precision multiplicity result motivates a `precision_class` axis on `KroneckerInvariant`.
- **F-T95-07** PATTERN_RANK_PARITY_LEAK risk: Kronecker / Littlewood–Richardson confusion is the primary Learner failure mode for any downstream agent ingesting this report.
- **F-T95-08** Tier-E primitive bundle unblocks 9 catalog entries (#92, #94–100) simultaneously — high leverage per filing cost.

---

## 1. Problem Statement

Let `S_n` be the symmetric group on `n` letters and let `χ^λ` denote the irreducible complex character of `S_n` indexed by an integer partition `λ ⊢ n`. The **Kronecker coefficient** `g(λ, μ, ν)` is the multiplicity of `χ^ν` in the pointwise (tensor) product `χ^λ · χ^μ`, equivalently the multiplicity of `V_ν` inside `V_λ ⊗ V_μ` as `S_n`-representation under diagonal action.

The **decision problems** of interest are:

- **VANISH(λ, μ, ν)** — decide whether `g(λ, μ, ν) = 0`.
- **POS(λ, μ, ν)** — decide whether `g(λ, μ, ν) > 0`.
- **COMPUTE(λ, μ, ν)** — output the integer `g(λ, μ, ν)`.

Two structural variants:
- **Stretched Kronecker:** `k ↦ g(kλ, kμ, kν)` (T#97).
- **Reduced (stable) Kronecker:** Murnaghan's stabilization (T#96).

The headline open problem: **find a non-negative combinatorial rule** analogous to Littlewood–Richardson tableaux. **No such rule is known in general** after a century of effort.

## 2. Status & Bounds

### 2.1 Complexity (unconditional)

| Problem | Class | Reference |
|---|---|---|
| `COMPUTE(g)` | `#P`-hard | Bürgisser–Ikenmeyer 2008 |
| `POS(g) > 0?` | `NP`-hard | Ikenmeyer–Mulmuley–Walter 2017 |
| `VANISH(g) = 0?` | `coNP`-hard | same |
| `χ^λ(μ)` positivity | `PP`-complete; vanishing `C_=P`-complete; both `PH`-hard | **Ikenmeyer–Pak–Panova 2024** (IMRN) |

The IMW result **falsifies** Mulmuley's GCT-positivity conjecture (PH1).

### 2.2 Polynomial / tractable special cases

- **Two two-row shapes:** Briand–Orellana–Rosas (2009, arXiv 0812.0861) — quadratic quasi-polynomial formulas.
- **Hook + arbitrary, two-row + arbitrary:** classical formulas (Remmel; Rosas).
- **Stretched Kronecker is quasi-polynomial** in special shapes.
- **Christandl–Doran–Walter** (2014) — finite-difference / Barvinok algorithm, polynomial-time for fixed-rank input.
- **All Kronecker = reduced Kronecker:** Ikenmeyer–Panova 2024, Forum Math Pi.

### 2.3 Recent positivity / asymptotic landmarks

- **Pak–Panova 2023** (J. Algebra 629): bounds on Kronecker coefficients.
- **Pak–Panova–Swanson 2025** (preprint): new restricted positive combinatorial rules.
- **Saxl (T#99) — proved 2025/2026:** Sellke, *Staircase Minimality and a Proof of Saxl's Conjecture* (arXiv 2512.15035) — full unconditional resolution.
- **Ikenmeyer–Omar–Tsintsilidas 2025** (arXiv 2509.10069): field-independent Kronecker–plethysm isomorphisms.
- **GCT obstructions:** Bürgisser–Ikenmeyer–Panova 2019 (JAMS) — no occurrence obstructions; Dörfler–Ikenmeyer–Panova 2020 — multiplicity > occurrence.

### 2.4 Computational tools

Sage `kronecker_coefficient`; Symmetrica; LiE; Macaulay2 SchurRings; `qi-rub/kronecker` Maple package.

## 3. Literature

### Foundational
- Murnaghan (1938) — stability theorem origin.
- Littlewood (1958).
- Stanley, *Positivity problems and conjectures in algebraic combinatorics* (2000).

### Complexity
- Mulmuley–Narayanan–Sohoni — *GCT III* (LR positivity in P; **NOT Kronecker**).
- Bürgisser–Ikenmeyer 2008 — `#P`-hardness.
- Ikenmeyer–Mulmuley–Walter, comput. complex. 26 (2017) 949–992 (arXiv 1507.02955) — Kronecker positivity NP-hard, falsifies PH1.
- Ikenmeyer–Pak–Panova, IMRN 2024 — character positivity PH-hard.
- Christandl–Doran–Walter (FOCS 2012; SICOMP 2017).

### Asymptotics and stability
- Briand–Orellana–Rosas; Vallejo; Sam–Snowden; Manivel; Pak–Panova.

### GCT and obstructions
- Mulmuley–Sohoni; Bürgisser–Ikenmeyer–Panova JAMS 2019; Dörfler–Ikenmeyer–Panova ICALP 2019.

### Saxl / staircase
- Pak–Panova–Vallejo Adv. Math. 2016; Ikenmeyer 2014; Luo–Sellke 2017; **Sellke arXiv 2512.15035 (2025)** full proof.

## 4. Attack Vectors

- **P03** Symmetry exploitation (canonical fit) — `S_n`-rep theory, branching, Murnaghan-Nakayama.
- **P28** Asymptotic spectrum (organizing meta-paradigm) — stretched Kronecker functionals.
- **P22** Polynomial method on character ring — Pak-Panova-Swanson 2025.
- **P27** Rank-zoo on representation rings — occurrence vs multiplicity vs reduced (multiplicity strictly stronger).
- **P30** Tensor network framing — character-table contraction; bond dim ↔ branching multiplicity.
- **(P32 candidate) Modular Saturation / Decomposition-Matrix Lifting** — Sellke's lever for Saxl; not in P01-P31; recommend filing for taxonomy review. **Numbering note:** T#1 flagged P32 = Evolutionary-LLM; T#56 flagged P32 = Existential-Theory Reduction. Synthesis must renumber.

### Active 2024-2025 patterns
- Reduction to reduced Kronecker (Ikenmeyer–Panova 2024).
- Field-independent / categorical attack (Ikenmeyer–Omar–Tsintsilidas 2025).
- Quantum-algorithmic (Bravyi et al., comput. complex. 2025) — `1/poly` additive precision.
- Modular / decomposition-matrix arguments — saturation via diagonal `d_{μμ} = 1`.

## 5. Substrate Encoding

### 5.1 Tier-E primitive (the proposal)

Per substrate-tester fire #44, Kronecker positivity surfaced **all four encoding-failure modes** that motivated Tier-E:

| Encoding attempt | Failure mode |
|---|---|
| Partitions as `bootstrap_symbol` | no `PartitionObject` |
| Tier-A `TensorObject` for `V_λ ⊗ V_μ` | no `IrreducibleRepresentation` |
| Tier-B existence witness for `g > 0` | extends Tier-B as `RepresentationTheoreticWitness` subtype |
| Plethysm `s_a[s_b]` as substrate object | no `SymmetricFunction` primitive |

### 5.2 Proposed dataclass

```python
@dataclass(frozen=True)
class PartitionObject:
    parts: tuple[int, ...]
    n: int
    docstring_domain: tuple[str, ...] = ("symmetric_group", "representation_theory")

@dataclass(frozen=True)
class IrreducibleSnRep:
    partition: PartitionObject
    dim: Optional[int] = None
    character_id: Optional[str] = None

@dataclass(frozen=True)
class KroneckerInvariant(RepresentationTheoreticInvariant):
    lambda_: PartitionObject
    mu: PartitionObject
    nu: PartitionObject
    value: Optional[int] = None
    status: Literal["known", "computed", "bounded", "open",
                    "vanishing_certified", "positivity_certified"] = "open"
    computation_method: Literal[
        "character_table", "barvinok_polytope", "two_row_quasipoly",
        "reduced_kronecker_lift", "tableau_combinatorial",
        "obstruction_only", "quantum_estimate", "unknown"] = "unknown"
    vanishing_certificate: Optional["VanishingCertificate"] = None
    positivity_witness: Optional["PositivityWitness"] = None
    precision_class: Literal["exact", "polynomial_additive", "asymptotic"] = "exact"
    canonical_attribution: Optional[str] = None

@dataclass(frozen=True)
class PositivityWitness:
    witness_kind: Literal["semistandard_pair", "tableau_bijection",
                          "schur_functor_construction", "barvinok_lattice_point",
                          "modular_lift", "stable_lift"]
    witness_data: bytes
    verifier: str

@dataclass(frozen=True)
class VanishingCertificate:
    cert_kind: Literal["dominance_obstruction", "semigroup_obstruction",
                       "moment_polytope_exclusion", "character_inner_product"]
    cert_data: bytes
    verifier: str
```

### 5.3 Catalog refs the Tier-E primitive unblocks

- **#92** GCT VP vs VNP (plethysm obstructions are `KroneckerInvariant`-shaped)
- **#94** moment polytopes (membership in NP ∩ coNP via `BarvinokKernel`)
- **#95** this report
- **#96** Kronecker stability
- **#97** stretched Kronecker
- **#98** Foulkes' conjecture (companion `PlethysmInvariant`)
- **#99** Saxl's conjecture (now resolved — calibration anchor)
- **#100** orbit-closure invariant theory

**One Tier-E bundle resolves the encoding gap for nine catalog entries simultaneously.**

## 6. Calibration Anchor Notes

### 6.1 Substrate-grade response

A response is **substrate-grade** iff it:
1. Distinguishes the three layers — general `#P`-hard, special-shape polynomial, GCT-positivity (FM-08).
2. Names canonical authors at canonicality-correct levels.
3. Refuses to claim a combinatorial rule exists in general (PATTERN_BASE_RATE_NEGLECT).
4. Refuses to merge Kronecker with Littlewood–Richardson (PATTERN_RANK_PARITY_LEAK).
5. Cites IMW 2017 for Mulmuley `PH1` falsification in any GCT discussion.

### 6.2 Likely Learner fabrications to firewall

- "Sohoni proved Kronecker positivity is in P." (FALSE)
- "Saxl is still open." (FALSE — Sellke 2025)
- "There is a Littlewood–Richardson-style rule for Kronecker (Stanley)." (FALSE)
- "GCT proved P ≠ NP via Kronecker positivity." (FALSE)
- "Reduced Kronecker is easier than ordinary." (FALSE — Ikenmeyer-Panova 2024)
- Hallucinated arXiv numbers in 2024–2025 window.

## 7. Pattern Citations

### PATTERN_BASE_RATE_NEGLECT (primary)

Combinatorial-rule searches for Kronecker have been "almost there" for 30+ years. Trajectory is "more restricted families," not "convergence to a general rule."

### PATTERN_RANK_PARITY_LEAK (primary)

Kronecker `g(λ, μ, ν)` and Littlewood–Richardson `c^ν_{λμ}` are **different multiplicity-counting operators**:
- LR: induced product, outer / external, `|λ|+|μ|=|ν|`.
- Kronecker: pointwise product, inner, `|λ|=|μ|=|ν|=n`.

LR positivity in `P` (MNS 2005); Kronecker positivity `NP`-hard (IMW 2017). A Learner that conflates them will leak `P` claims onto `NP`-hard problems.

### PATTERN_CONDUCTOR_CONFOUND (secondary)

Lurking `n` plays a confounder role: results that look impressive at small `n` (verified Saxl up to `n = 50` numerically) routinely fail to scale. Christandl–Doran–Walter is in `P` *for fixed number of parts* — the parameter regime is the conductor.

## 8. Cross-References

### Tensor open-problem catalog
- **#92** GCT VP vs VNP — plethystic obstructions encoded as `KroneckerInvariant`.
- **#94** Moment polytopes — `NP ∩ coNP` membership.
- **#96** Kronecker stability — reduced ≡ ordinary (IP 2024).
- **#97** Stretched Kronecker — quasi-polynomiality conjecture.
- **#98** Foulkes' conjecture — plethysm operator (companion primitive).
- **#99** Saxl's conjecture — **resolved 2025 (Sellke)**. Calibration anchor.
- **#100** Invariant theory of orbit closures.

### Paradigm taxonomy
- P03, P28, P22, P27, P30
- **(P32 candidate)** Modular Saturation / Decomposition-Matrix Lifting

### Substrate-tester tickets
- `T-2026-05-08-ST-fire44-001` — capability gap → Techne. Tier-E proposal; this report supplies the encoding.
- `T-2026-05-08-ST-fire44-002` — strategic-coordination supplement → Aporia.

### Existing reports in this batch
- `report_T1_matrix_multiplication_exponent.md` — P28 anchor.
- `report_T28_asymptotic_spectrum.md` — meta-organizer.
- `report_T43_best_rank_r_existence.md` — orthogonal direction.
- `report_T56_symmetric_rank_nphard.md` — sister NP-hardness.
- `report_T79_slocc_entanglement.md` — sister Tier-B/Tier-E primitive.

---

*Aporia, 2026-05-09. Substrate-grade. Fires Tier-E meta-primitive backing.*
