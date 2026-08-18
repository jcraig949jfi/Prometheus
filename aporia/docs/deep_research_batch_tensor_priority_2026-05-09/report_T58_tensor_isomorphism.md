# Report T#58 — Tensor Isomorphism Complexity

**Catalog entry:** `aporia/mathematics/tensor_open_problems_v1.md` §VII #58
**Source dispatch:** `aporia/docs/gemini_tensor_priority_dispatch_2026-05-09.md` (Tier 2, fire-10)
**Author:** Aporia (deep-research)
**Date:** 2026-05-09
**Doctrine:** HARD-1, HARD-2, HARD-5, HARD-6
**Patterns cited:** PATTERN_BASE_RATE_NEGLECT, PATTERN_RANK_PARITY_LEAK, PATTERN_CONDUCTOR_CONFOUND
**Tags:** P03 (symmetry exploitation; R-GIT-product sub-tactic), P09 (exhaustive computation, MinRank cryptanalysis), P25 (pivotal-negative-result candidate), P30/P31 (per substrate-tester fire #40 attribution); proposed paradigm sub-tactics: **linear-length reduction (P03)** and **orbit-special-structure exploitation (P25)**

---

## Brief Summary

T#58 (Tensor Isomorphism, TI) is **TI-complete** (Grochow–Qiao SIAM JC '23 / ITCS '21, arXiv:1907.00309) under the new complexity class TI; polynomial-time equivalent to p-group iso (class 2, exp p), n-dim algebra iso, cubic-form iso, ATFE (ALTEQ basis), MCE (MEDS basis), and polynomial-system iso. TI ⊆ NP ∩ coAM; TI is GI-hard; the relation to GI in the other direction is open. Best worst-case algorithm is q^Õ(n^{3/2}) (Grochow–Qiao Part IV, STOC '25, arXiv:2306.16317). The slim-slice case n × n × 2 is in P via Kronecker canonical form + Smith normal form — the FM-08 trivial-vs-open trap in its sharpest form. NIST PQ candidates MEDS and ALTEQ rest on average-case TI hardness; ALTEQ has been parametrically eroded ≥20 bits by Reijnders–Samardjiska–Trimoska (EUROCRYPT '24) and Beullens-style algebraic attacks (eprint 2024/364), forcing re-parametrization. T#58 directly anchors substrate-tester ticket T-ST-fire40-001's three missing primitives (GroupAction, IsomorphismCertificate, OrbitStratification) and is the **decision-version sibling** of T#79's classification-version OrbitWitness — both collapse into a unified Structured-Equivalence-Class meta-primitive.

## Flagged Findings

1. **TI-completeness, not GI-completeness, is the canonical headline.** Catalog's "suspected GI-hard" framing understates the precise Grochow–Qiao result.
2. **Group-action axis dominates the complexity** (PATTERN_RANK_PARITY_LEAK): GL_n³, GL_n alternating, GL_n simultaneous, MCE, S_n only, n × n × 2 pencil — six distinct complexity profiles ranging from P (pencils) through GI (S_n) to TI-complete (general).
3. **Cryptographic-strength reductions are a separate axis** (PATTERN_BASE_RATE_NEGLECT): worst-case TI-completeness ≠ average-case hardness; ALTEQ already lost ≥20 bits in 2024.
4. **Bouvier–Persichetti–Tillich (eprint 2024/337) is a P25 pivotal-negative-result instance** — broke ASIACRYPT '23 commitment by exploiting low-rank-point orbits. Recommend new P25 sub-tactic: "orbit-special-structure exploitation."
5. **Linear-length reduction (Grochow–Qiao IV) is a P03 sub-tactic worth registering** in attack_angle_taxonomy.
6. **Substrate-tester fire #40 confirms the asymmetric-existential pattern across three fires (#38/#39/#40)** — the most robust matrix-fill finding to date. ConstructiveExistenceWitness with Tier-A GroupAction primitive is recommended highest-priority new substrate primitive.
7. **T#58 + T#79 unify under Structured-Equivalence-Class meta-primitive** (per `T-2026-05-08-ST-fire35-001` cluster recommendation): T#58 = decision-version with cryptographic stake; T#79 = classification-version with quantum-information stake.
8. **Trivial-vs-open within conjecture family (FM-08):** n × n × 2 in P (Kronecker), 3-tensor TI-complete, d-tensor TI for d > 3 reduces to 3-tensor (Grochow–Qiao III).

## 1. Problem Statement

Let F be a field. The **tensor isomorphism problem TI_d(n, F)** for d-way tensors:

> **Input:** Two tensors T, T' ∈ F^{n × n × ⋯ × n} (d factors).
> **Question:** Do there exist (A_1, …, A_d) ∈ GL_n(F)^d such that T' = (A_1 ⊗ A_2 ⊗ ⋯ ⊗ A_d) · T?

**Canonical case d = 3** with action (A, B, C) ∈ GL_n(F)³.

Variants (each TI-complete by Grochow–Qiao I/III/IV):

| Variant | Group action | Object | TI-complete? |
|---|---|---|---|
| 3-Tensor Iso | GL_n³ | F^{n×n×n} | yes (Part I) |
| Cubic Form Iso | GL_n simultaneous | symmetric 3-tensors | yes (Part I, IV) |
| ATFE | GL_n on alternating | Λ³(F^n) | yes (Part III; ALTEQ) |
| Matrix Code Equiv | GL_m × GL_n × GL_k | F^{m×n×k} as code | yes (MEDS) |
| p-Group Iso (cl. 2, exp p) | — | tensor-encoded commutators | yes (Part I) |
| Algebra Iso (n-dim) | GL_n | structure constants | yes (Part I) |
| Polynomial system | GL | quadratic forms | yes (Part I) |
| d-Tensor Iso (d > 3) | GL_n^d | F^{n^d} | reduces to 3-tensor (Part III) |
| Pencil Equiv (n × n × 2) | GL_n² | Aλ + B | **polynomial time (Kronecker)** |
| Hypergraph Iso (S_n only) | S_n^d | 0/1 tensor | reduces to GI (Babai) |

## 2. Status & Bounds

**Unconditional:** Pencil equiv n × n × 2 in P (Kronecker 1890); TI ∈ NP ∩ coAM; TI-completeness web — 3-tensor ≡_p p-group ≡_p algebra ≡_p cubic-form ≡_p polynomial-system iso (Grochow–Qiao I, ITCS '21 / SIAM JC '23); search-to-decision and counting-to-decision for p-group iso (Grochow–Qiao II, CCC '21); orthogonal/unitary/symplectic 5 actions equivalent (Chen–Grochow–Qiao–Tang–Zhang III, ITCS '24); d-tensor iso reduces to 3-tensor for d ≥ 3 (Part III); linear-length q^Õ(n^{3/2}) algorithm (Grochow–Qiao IV STOC '25); TI over commutative rings (Part V STOC '25); MEDS NIST round-1 (AFRICACRYPT '23); ALTEQ NIST PQC (ASIACRYPT '22); ATFE/MCE algorithms ≥20-bit ALTEQ erosion (Reijnders–Samardjiska–Trimoska EUROCRYPT '24); algebraic algorithm for ATFE (eprint 2024/364); TI for special low-rank-point orbits (Bouvier–Persichetti–Tillich eprint 2024/337); average-case poly-time on 1/Θ(q) fraction (algebra iso, MCE conjugacy) and 1/q^Θ(1) fraction (4-tensor iso) (arXiv:2604.00591, 2026).

**Conditional:** TI-completeness implies poly-time TI ⇒ poly-time for all p-group / algebra / ATFE / MCE / MinRank-decision instances. Conjecture **GI ⊊ TI** widely believed. TI ⊆ NP ∩ coAM ⇒ TI not NP-complete unless PH collapses.

**Open:** worst-case lower bounds for TI; worst-case → average-case bridge for cryptographic distributions (primary cryptographic-foundations gap); quantum complexity of TI; TI over non-prime / infinite fields; tighter MinRank↔TI reductions.

## 3. Literature

**Grochow–Qiao series:** Part I (ITCS '21 / SIAM JC 52 (2023) 568–617, arXiv:1907.00309); Part II (CCC '21, p-group search-to-decision); Part III (ITCS '24, arXiv:2306.03135, with Chen, Tang, Zhang); Part IV (STOC '25, arXiv:2306.16317, linear-length); Part V (STOC '25, commutative rings).

**Cryptographic candidate:** Ji–Qiao–Song–Yun, "General Linear Group Action on Tensors," TCC '19 (eprint 2019/687).

**Proof complexity:** Galesi–Grochow–Pitassi–San Mauro CCC '23 (arXiv:2305.19320).

**Average-case:** arXiv:2604.00591 (2026).

**MEDS:** Chou–Niederhagen–Persichetti–Randrianarisoa–Reijnders–Samardjiska–Trimoska AFRICACRYPT '23 (eprint 2022/1559); meds-pqc.org; Reijnders–Samardjiska–Trimoska EUROCRYPT '24; Couvreur–Debris-Alazard–Tillich code-equivalence line.

**ALTEQ:** Tang–Duong–Joux–Plantard–Qiao–Susilo ASIACRYPT '22; pqcalteq.github.io; Algebraic Algorithm for ATFE (eprint 2024/364); Faster Verifications and Smaller Signatures.

**MinRank (T#101 sister):** Ivanyos–Karpinski–Saxena SIAM JC 2010 (arXiv:0907.0774); Tang–Lai–Lim "MinRank-based cryptography"; Beullens hardness analyses; "Tensor decomposition beyond uniqueness" (arXiv:2510.26587, 2025).

**Pencil canonical form:** Kronecker (1890); Weierstrass (1868); de Terán–Dopico–Mackey arXiv:1205.1138.

**Tools:** Magma (`IsIsomorphic`, Brooksbank–Wilson StarAlge); GAP (`IsomorphismGroups`); Sage (Smith normal form, pencils, finite-field tensors); Macaulay2 (invariant rings); custom MinRank solvers (Faugère F4/F5 Gröbner basis); SAT/SMT for small-parameter cryptanalysis.

## 4. Attack Vectors

T#58 maps onto P03 (central), P09, P25, P30/P31 (per fire #40).

**P03 — Symmetry exploitation (central).** R-GIT-product sub-tactic (already flagged in T#79); invariant theory (separate orbits via polynomial invariants — finding the separator is itself TI-hard); stabilizer/orbit-stabilizer reduction; Galois/field-trace invariants.

**P09 — Exhaustive computation.** Brute force q^O(n²) → q^Õ(n^{3/2}) Grochow–Qiao IV; SAT-encoded small-parameter key recovery is the primary cryptanalytic compute pattern.

**P25 — Pivotal negative result.** Bouvier–Persichetti–Tillich 2024/337 broke ASIACRYPT '23 commitment by special low-rank-orbit exploitation; Reijnders–Samardjiska–Trimoska EUROCRYPT '24 ATFE erosion. **New P25 sub-tactic candidate: "orbit-special-structure exploitation."**

**P30/P31 (per fire #40):** tensor-network and secant-variety invariants as TI-monotones (necessary but not sufficient).

**TI-cryptanalysis stack:** algebraic/Gröbner basis attacks (F4/F5); low-rank-slice exploitation; birthday/collision/claw-finding (Grover-amplified quantum); group-theoretic stabilizer-search; algebraic proof complexity / SOS lower bounds.

**Sub-tactics flagged for taxonomy update:**
1. **Linear-length reduction** as a P03 sub-tactic (Grochow–Qiao IV gadget).
2. **Orbit-special-structure exploitation** as a P25 sub-tactic — canonical post-quantum cryptanalysis pattern.

## 5. Substrate Encoding

T#58 directly anchors **Tier-A GroupAction / GroupActionWitness primitive** + **Tier-B `ConstructiveExistenceWitness` meta-primitive's `IsomorphismWitness` subtype** (sister of T#79's `OrbitWitness`).

```python
class GroupActionKind(str, Enum):
    GLN_PRODUCT = "gln_product"
    GLN_SIMULTANEOUS = "gln_simultaneous"
    GLN_ALTERNATING = "gln_alternating"
    GLN_MATRIX_CODE = "gln_matrix_code"
    ORTHOGONAL_PRODUCT = "on_product"
    UNITARY_PRODUCT = "un_product"
    SYMPLECTIC_PRODUCT = "spn_product"
    SYMMETRIC = "sym"
    PENCIL_GLGL = "pencil_glxgl"

@dataclass(frozen=True)
class GroupAction:
    kind: GroupActionKind
    base_field: "FieldSpec"
    dimensions: tuple[int, ...]
    representation: "RepresentationSpec"

@dataclass(frozen=True)
class IsomorphismWitness:
    """Positive existential witness for T ≅_G T'.
    Sister of OrbitWitness (T#79 — classification version)."""
    source_object: "TensorLike"
    target_object: "TensorLike"
    group_action: GroupAction
    witness_tuple: tuple["GroupElement", ...]
    verification_method: "VerificationMethod"
    cost_annotation: "ComplexityCost"
    domain_docstring: dict = field(default_factory=dict)
```

**Unification with T#79 under Structured-Equivalence-Class meta-primitive:**

```
StructuredEquivalenceClass
  ├── ambient_space
  ├── equivalence_relation_kind  (orbit | homotopy | n-isomorphism | bijection | intertwiner | iso_under_group_action)
  ├── canonical_representative
  ├── witness_data               (group element tuple | continuous deformation | n-cell tower | ...)
  └── invariant_separator_set    (functions distinguishing classes)
```

T#58 = decision-version-of-orbit-equivalence-with-cryptographic-stake; T#79 = classification-version-of-orbit-equivalence-with-quantum-information-stake. Together they supply Structured-Equivalence-Class its first two anchors.

## 6. Calibration Anchor Notes

**Substrate-grade vs textbook-trivial:**
- *Substrate-grade:* "TI is TI-complete (Grochow–Qiao I); polynomial-time equivalent to p-group iso (cl. 2, exp p), algebra iso, cubic-form iso, ATFE, MCE, polynomial-system iso. Best worst-case algorithm runs q^Õ(n^{3/2}) (Grochow–Qiao IV STOC '25). 1/q-fraction average-case algorithms exist but do not break NIST L1 MEDS/ALTEQ."
- *Substrate-grade:* "ALTEQ has been parametrically eroded ≥20 bits via algebraic attacks (Reijnders–Samardjiska–Trimoska EUROCRYPT '24)."
- *Substrate-grade:* "TI ⊆ NP ∩ coAM; TI is GI-hard but GI is not known to be TI-hard. The slim case n × n × 2 is in P (Kronecker + Smith normal form)."
- *Textbook-trivial:* "Tensor isomorphism is hard."
- *Trap (PATTERN_BASE_RATE_NEGLECT):* "MEDS/ALTEQ are secure because TI is hard." Worst-case ≠ average-case.
- *Trap (PATTERN_RANK_PARITY_LEAK):* conflating GL action with S_n action; conflating 3-tensor TI with d-tensor TI for d > 3 (poly-equivalent) but missing that n × n × 2 is in P.
- *Trap (PATTERN_CONDUCTOR_CONFOUND):* conflating "TI-complete" with "GI-complete."

**Canonical authors:**
- **Grochow, Qiao** — TI-complexity-class founders.
- **Ji, Song, Yun** — original cryptographic candidate.
- **Chen, Tang, Zhang** — Part III co-authors.
- **Chou, Niederhagen, Persichetti, Randrianarisoa, Reijnders, Samardjiska, Trimoska** — MEDS designers.
- **Tang, Duong, Joux, Plantard, Susilo** — ALTEQ designers.
- **Beullens** — primary post-quantum cryptanalyst.
- **Bouvier, Persichetti, Tillich** — TI cryptanalysts.
- **Ivanyos, Karpinski, Saxena** — MinRank/matrix completion.
- **Babai** — GI-complexity referent.

**Fabrication risks:**
1. Inventing a "Grochow–Qiao Part II" cryptanalysis paper.
2. Mis-attributing MEDS to Grochow–Qiao.
3. Claiming TI ∈ P or TI is NP-complete.
4. Conflating "TI is GI-hard" with "TI = GI."
5. Claiming a post-quantum-secure parameter set without referencing the EUROCRYPT '24 ALTEQ erosion.
6. Inventing a quantum algorithm for TI faster than Grover-square-root.
7. Quoting average-case algorithms succeeding on Θ(1) fraction.
8. Conflating TI (decision) with T#79 (classification).

## 7. Cross-References

**Within `tensor_open_problems_v1.md`:**
- **#56 Symmetric tensor rank NP-hardness** — sister complexity entry.
- **#79 SLOCC entanglement classification** — direct sibling: T#58 = decision, T#79 = classification.
- **#100 Invariant theory of tensor orbits** — umbrella.
- **#101 MinRank cryptographic foundations** — direct umbrella.
- Adjacent: #59 (hyperdeterminant), #95–99 (representation-theoretic complexity).

**Within `attack_angle_taxonomy.md`:**
- **P03** central; recommend adding **linear-length-reduction sub-tactic** and **R-GIT-product**.
- **P09**.
- **P25** — recommend adding **"orbit-special-structure exploitation" P25 sub-tactic.**
- **P30, P31** per fire #40 attribution.

**Sister reports in batch:**
- `report_T56_symmetric_rank_nphard.md`; `report_T79_slocc_entanglement.md` (direct sibling); `report_T28_asymptotic_spectrum.md`.

**Capability-gap tickets:**
- **`T-2026-05-08-ST-fire40-001`** — direct anchor.
- `T-2026-05-07-ST-fire1-002` — homotopy-class gap (sibling via Structured-Equivalence-Class).
- `T-2026-05-07-ST-fire35-001` — 5-of-5 capability-gap cluster.
- `T-2026-05-08-T038` — Techne classification: T#58 → SUBSTRATE-GAP / SHARED-PRIMITIVE / Tier-B + Tier-A.
- **New candidate: `T-ST-T58-001 IsomorphismWitness primitive specification`**.

**Pattern citations:**
- **PATTERN_BASE_RATE_NEGLECT** — base rate of "post-quantum candidates surviving 5 years of cryptanalysis without parameter erosion" is small.
- **PATTERN_RANK_PARITY_LEAK** — different group actions yield different complexity classes.
- **PATTERN_CONDUCTOR_CONFOUND** — TI-complete, GI-complete, NP-complete are three distinct classifications.

---

*Aporia, 2026-05-09*
