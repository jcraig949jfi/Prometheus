# Report T#79 — SLOCC Entanglement Classification for n ≥ 5 Qubits

**Catalog entry:** `aporia/mathematics/tensor_open_problems_v1.md` §X #79
**Source dispatch:** `aporia/docs/gemini_tensor_priority_dispatch_2026-05-09.md` (Tier 2, fire-5)
**Author:** Aporia (deep-research)
**Date:** 2026-05-09
**Doctrine:** HARD-1, HARD-2, HARD-5, HARD-6
**Patterns cited:** PATTERN_BASE_RATE_NEGLECT, PATTERN_CONDUCTOR_CONFOUND, PATTERN_RANK_PARITY_LEAK
**Tags:** P03 (symmetry exploitation; R-GIT-product sub-tactic candidate), P22 (polynomial method), P28 (asymptotic spectrum), P29 (border apolarity), P31 (secant variety geometry)

---

## Brief summary

T#79 (SLOCC entanglement classification for n ≥ 5 qubits) is the canonical reductive-group orbit-classification problem on (ℂ²)^⊗n: SLOCC equivalence = orbit equivalence under SL(2,ℂ)^n. Verified arc: n=2 trivial, n=3 has 6 orbits (Dür–Vidal–Cirac PRA 62 062314, arXiv:quant-ph/0005115), n=4 has 9 continuous families (Verstraete–Dehaene–De Moor–Verschelde PRA 65 052112, arXiv:quant-ph/0109033) reorganized as 8 mod permutation (Lamata–León–Salgado–Solano PRA 75 022318, arXiv:quant-ph/0610233), and for n ≥ 5 the orbit space is (2^n − 3n − 1)-dimensional — no finite parameterization. Substrate-grade reframes pivot on (i) the Luque–Thibon 5-qubit invariant ring (J. Phys. A 39 (2006) 371), (ii) the Holweck–Luque–Thibon "geometric atlas" (arXiv:1306.6816 / 1606.05569), (iii) the Walter–Doran–Gross–Christandl entanglement polytopes (Science 340 1205, arXiv:1208.0365), and (iv) the 2025 AME-at-n=5 classification (arXiv:2507.02185, separates LU classes by 3 invariants and proves every 5-qubit AME ≡_LU the unique ((5,2,3)) QECC). T#79 directly anchors `T-2026-05-07-ST-fire1-002` (homotopy-class gap) as its algebraic-geometric sibling — both are continuous-moduli equivalence relations the substrate's current EQUIV witness types cannot encode. Recommend a unified **Structured-Equivalence-Class** meta-primitive subsuming `OrbitWitness` (algebraic-geometric, T#79), `HomotopyWitness` (topological, fire1-002), and `ArityGradedOperationFamily` (higher-algebraic, fire21-002).

## Flagged findings

1. **Orbit ≠ class — the canonical PATTERN_CONDUCTOR_CONFOUND.** Two distinct meanings for "how many SLOCC classes": (a) discrete count of *components / families up to continuous deformation* (n=4: 9 families VDDV / 8 mod permutation Lamata; n=4 nullcone: 47 components / 15 mod permutation per Holweck–Luque–Thibon); (b) cardinality of the *orbit space*, which is uncountable / positive-dimensional for n ≥ 4.

2. **n=4 is already the wall.** Dür–Vidal–Cirac noted "infinitely many SLOCC classes for four qubits" once orbits — not families — are counted. Textbook "GHZ vs W" framing is correct only for n=3. PATTERN_BASE_RATE_NEGLECT trap.

3. **n=5 dimension count is the substrate-grade headline.** dim ℙ((ℂ²)^⊗5) = 31; dim SL(2,ℂ)^5 = 15; expected GIT-quotient dimension = 16. n=6 → 45; n=8 → 231. Formal statement of "no finite parameterization."

4. **AME/QECC anchor at n=5 is the closest thing to a complete sub-classification (arXiv:2507.02185, 2025).** Every 5-qubit AME is local-unitary-equivalent to a point in the unique ((5,2,3)) QECC, with 3 invariant polynomials separating LU classes. AME exists for n ∈ {2,3,5,6}, **does not** exist for n=4 or n=7 (Huber–Gühne–Siewert PRL 118 200502, arXiv:1608.06228).

5. **GIT / moment-polytope reframe is the route.** Walter–Doran–Gross–Christandl 2013 (Science 340 1205, arXiv:1208.0365) replace "list orbits" with "for each orbit closure, compute its entanglement polytope" — the polytope of one-body marginal spectra. Finite combinatorial object even when the orbit space is positive-dimensional, computable from local data only.

6. **New attack-pattern candidate flagged for taxonomy update:** **R-GIT-product** as a P03 sub-tactic — reductive-group GIT quotient of a representation of a *product* of SL_2's. Recurs across qubits, fermionic Fock space, supergravity black-hole charge configurations (Lévay–Sárosi line), multi-leg tensor networks.

7. **Substrate gap (substantive):** No current primitive encodes "orbit-equivalence under continuous group action with positive-dimensional moduli." `T-ST-fire1-002` flags the homotopy-class gap; SLOCC at n ≥ 5 is the algebraic-geometric sibling. Recommend co-design of unified Structured-Equivalence-Class meta-primitive (per Aporia recommendation in `T-2026-05-08-ST-fire35-001`) covering all 5 capability gaps in the cluster.

8. **Canonical attribution at risk.** Verstraete + Dehaene + De Moor + Verschelde (4-author, 2002 PRA 65 052112). Dür + Vidal + Cirac (3-author, 2000 PRA 62 062314). Lamata + León + Salgado + Solano (4-author, 2007 PRA 75 022318; 2006 inductive arXiv:quant-ph/0603243). Walter + Doran + Gross + Christandl (4-author, Science 340 1205, 2013). Holweck + Luque + Thibon (3-author, "geometric atlas" series 2013/2016).

## Verified arXiv IDs / DOIs

`quant-ph/0005115` (Dür–Vidal–Cirac n=3, 2000, PRA 62 062314); `quant-ph/0109033` (Verstraete–Dehaene–De Moor–Verschelde n=4 nine families, 2002, PRA 65 052112); `quant-ph/0603243` (Lamata et al. inductive SLOCC, 2006); `quant-ph/0610233` (Lamata et al. four-qubit complete classification, PRA 75 022318, 2007); `1208.0365` (Walter–Doran–Gross–Christandl entanglement polytopes, Science 340 1205, 2013); `1306.6816` (Holweck–Luque–Thibon Atlas I, 2013); `1606.05569` (Holweck–Luque–Thibon Atlas II, 2016); `quant-ph/0507070` (Lévay 2005); `quant-ph/0605151` (Lévay 2006); `2111.05488` (4-qubit stabilisers under SLOCC, 2021); `2507.02185` (4-qubit pure codes + 5-qubit AME, 2025); `2411.04096` (LU-AME from orthogonal arrays, 2024); `2508.04777` (AME multipartite, 2025); `1608.06228` (Huber–Gühne–Siewert n=7 AME impossibility, PRL 118 200502, 2017); `1306.2879` (Helwig AME graph states, 2013).

---

## 1. Problem Statement

Let H_n = (ℂ²)^⊗n be the n-qubit Hilbert space (dim 2^n). Two pure states |ψ⟩, |ϕ⟩ ∈ H_n are **SLOCC-equivalent** iff there exist invertible local operators A_1, …, A_n ∈ GL(2,ℂ) with

|ϕ⟩ = (A_1 ⊗ A_2 ⊗ … ⊗ A_n) |ψ⟩.

Restricting to projective states gives the action of **G_n = SL(2,ℂ)^n** (or G_n ⋊ S_n with qubit permutations) on ℙ(H_n). **SLOCC equivalence = G_n-orbit equivalence.**

**Catalog problem T#79:** classify the G_n-orbits on ℙ(H_n) for n ≥ 5, equivalently describe the GIT quotient ℙ(H_n) // G_n, equivalently determine a complete set of SLOCC invariants distinguishing orbits.

| n | dim ℙ(H_n) | dim G_n | expected moduli dim |
|---|---|---|---|
| 2 | 3 | 6 | < 0 (single open orbit + Schmidt-rank stratum) |
| 3 | 7 | 9 | < 0 (finite orbit poset, 6 orbits — DVC) |
| 4 | 15 | 12 | 3 (3-parameter generic family) |
| 5 | 31 | 15 | **16** |
| 6 | 63 | 18 | **45** |
| 7 | 127 | 21 | **106** |
| 8 | 255 | 24 | **231** |

For n ≥ 4 the moduli is positive-dimensional; for n ≥ 5 it grows as 2^n − 3n − 1.

## 2. Status & Bounds

**Unconditional results:**

| Result | Authors | Year |
|---|---|---|
| n=2: Schmidt-rank classification | Schmidt / standard | 1907 |
| n=3: 6 SLOCC classes — separable, 3 biseparable, GHZ, W | Dür–Vidal–Cirac | 2000 |
| n=4: 9 continuous families ("nine ways to entangle four qubits") | Verstraete–Dehaene–De Moor–Verschelde | 2002 |
| n=4: 8 true SLOCC classes mod S_4 | Lamata–León–Salgado–Solano | 2007 |
| n=4: hyperdeterminant of order 24, full invariant ring | Luque–Thibon, Briand–Luque–Thibon | 2003–2006 |
| n=4: 4-qubit stabilizers under SLOCC, 87 element-conjugacy patterns | various, arXiv:2111.05488 | 2021 |
| n=4: nullcone has 47 components / 15 mod permutation | Holweck–Luque–Thibon Atlas I | 2013 |
| n=4: dual variety stratification ("tame world") | Holweck–Luque–Thibon Atlas II | 2016 |
| n=5: full invariant ring | Luque–Thibon (J. Phys. A 39 371) | 2006 |
| n=5: AME states classified — every 5-qubit AME ≡_LU ((5,2,3)) QECC, 3 separating invariants | arXiv:2507.02185 | 2025 |
| n=6: AME exists | Helwig | 2013 |
| n=7: AME does **not** exist | Huber–Gühne–Siewert PRL 118 200502 | 2017 |
| Entanglement polytope = single-particle marginal-spectrum polytope per orbit closure | Walter–Doran–Gross–Christandl | 2013 |

**Conditional / structural:**
- The number of generic-orbit invariants equals 2^n − 3n − 1 for n ≥ 4 (transcendence degree of the invariant ring under SL(2,ℂ)^n).
- The invariant ring ℂ[H_n]^{G_n} is finitely generated (Hilbert; Mumford GIT) but explicit Hilbert-series / generators are known only for n = 4 (fully) and n = 5 (Luque–Thibon).
- Stable / semistable / null-cone trichotomy (Mumford GIT) applies: stable orbits closed; semistable but unstable orbits collapse in GIT quotient; null-cone vectors form the boundary.

**Open subproblems active 2024–2026:**
- Explicit invariant ring for n = 6, 7, 8.
- Finite enumeration of "discrete components" of orbit space mod continuous deformation for n = 5, 6 (Holweck–Luque–Thibon atlas program).
- Sharp characterization of stable / semistable orbits.
- Connection to AdS/CFT and holographic states (T#78); link to error-correcting codes (T#80, T#81).
- Computational complexity of orbit-membership testing — closely related to T#58 (tensor isomorphism complexity).

## 3. Literature

**Foundational SLOCC papers:** Bennett–Bernstein–Popescu–Schumacher 1996 PRA 53 2046 (SLOCC framework); Dür–Vidal–Cirac PRA 62 062314 (2000), arXiv:quant-ph/0005115 (n=3); Verstraete–Dehaene–De Moor–Verschelde PRA 65 052112 (2002), arXiv:quant-ph/0109033 (n=4 nine families); Lamata–León–Salgado–Solano arXiv:quant-ph/0603243 (2006, inductive); Lamata et al. PRA 75 022318 (2007), arXiv:quant-ph/0610233.

**Polynomial-invariant series:** Luque–Thibon PRA 67 042303 (2003); Briand–Luque–Thibon J. Phys. A 36 9915 (2003); Luque–Thibon J. Phys. A 39 371 (2006, five-qubit invariants); Holweck–Luque–Thibon J. Math. Phys. 55 012202, arXiv:1306.6816 (2013, Atlas I); Holweck–Luque–Thibon J. Math. Phys. 58 022201, arXiv:1606.05569 (2016, Atlas II); Lévay J. Phys. A 38 9075, arXiv:quant-ph/0507070 (2005); Lévay J. Phys. A 39 9533, arXiv:quant-ph/0605151 (2006).

**Entanglement polytopes / moment-polytope route (P28+P31):** Walter–Doran–Gross–Christandl Science 340 1205, arXiv:1208.0365 (2013); Klyachko J. Phys. Conf. Ser. 36 72 (2006, marginal problem); Aulbach–Markham–Murao NJP 12 073025 (2010); Brion (Lecture Notes 1296); Berenstein–Sjamaar JAMS 13 433 (2000).

**AME / QECC connection:** Helwig arXiv:1306.2879 (2013); Huber–Gühne–Siewert PRL 118 200502, arXiv:1608.06228 (2017, n=7 impossibility); arXiv:2507.02185 (2025, 5-qubit AME = ((5,2,3)) QECC); arXiv:2411.04096 (2024, LU equivalence from orthogonal arrays); arXiv:2508.04777 (2025); arXiv:2501.15477 (2025, max-concurrence criterion).

**Recent (2017–2026):** arXiv:1106.6105 (rank-of-coefficient-matrix); arXiv:1805.01339 (spin-flipping-matrix ranks); arXiv:2111.05488 (four-qubit stabilisers); QIP 2025 (rank-based dichotomy); Quantum 4 (2020) 300 (symmetries of critical states).

**Tools:** Macaulay2 (invariant rings, Hilbert series, GIT-quotient computations); Magma (invariant theory of reductive groups); Singular (Gröbner bases for polynomial invariants); Polymake / Sage (entanglement polytope vertex enumeration; moment-polytope computations); Bertini, HomotopyContinuation.jl (numerical orbit detection); LiE, Symmetrica (representation-theoretic decomposition of invariant-ring graded pieces); Cadabra, FORM (symbolic-tensor algebra for explicit hyperdeterminants).

## 4. Attack Vectors

T#79 sits at the intersection of P03, P22, P28, P29, P31.

**P03 — Symmetry exploitation.** SLOCC equivalence *is* a reductive-group orbit relation. Full attack stack: invariant theory (Hilbert), GIT (Mumford), Luna's slice theorem, Kempf–Ness (stable orbit ↔ moment-map zero), Kirwan–Ness stratification of unstable locus.
**Flag:** *Reductive-group GIT quotient of a representation of a product of SL_2's* — call it **R-GIT-product** — is a recurring shape (qubits, qudits, fermionic Fock, multi-leg networks) worth registering as a P03 sub-tactic.

**P22 — Polynomial method.** Distinguish orbits by evaluating SLOCC-invariant polynomials. The 4-qubit hyperdeterminant of order 24 (Schläfli; Luque–Thibon) is canonical; for n=5, AME orbits separated by 3 invariants (arXiv:2507.02185).

**P28 — Asymptotic spectrum.** Wei–Goldbart geometric measure of entanglement is a real-valued G_n-monotone, candidate spectral point on the SLOCC pre-order. Christandl–Vrana–Zuiddam quantum functionals construct via moment polytopes (per Walter et al.) directly.

**P29 — Border apolarity.** Apolar-scheme / catalecticant obstructions: an orbit's apolar scheme is a SLOCC invariant.

**P31 — Secant variety geometry.** Each H_n embeds via Segre map ℙ¹ × … × ℙ¹ ↪ ℙ(H_n); rank-r SLOCC invariants encode secant-variety membership.

**Sub-tactics flagged for taxonomy update:**
1. **R-GIT-product** (P03 sub-tactic): SL(2,ℂ)^n on ⊗-product representations.
2. **Single-particle marginal polytope as orbit-identity proxy** (Walter et al.) — substrate-grade sub-tactic of P31 with cross-application potential.
3. **Inductive lifting of (n-1)-classification to n-classification** (Lamata 2006 method).

## 5. Substrate Encoding

T#79 directly anchors the **Tier-B `ConstructiveExistenceWitness` meta-primitive**, with subtype **`OrbitWitness`** (and a sibling `HomotopyWitness` for the topological case — `T-ST-fire1-002`).

Proposed dataclass shape:

```python
class GroupActionKind(str, Enum):
    REDUCTIVE_ALGEBRAIC = "reductive_alg"      # SL_n^k, GL_n
    FINITE = "finite"                          # S_n, Coxeter
    LIE_COMPACT = "lie_compact"                # SU, SO, Sp
    HOMOTOPY = "homotopy_higher_groupoid"      # share with HomotopyWitness

class OrbitStability(str, Enum):
    STABLE = "stable_closed"                   # Mumford-stable
    SEMISTABLE = "semistable_nonclosed"        # GIT-quotient point but orbit not closed
    UNSTABLE = "unstable_nullcone"             # in null cone
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class OrbitWitness:
    ambient_space: "AmbientSpaceID"
    group_action: "GroupActionID"
    action_kind: GroupActionKind
    orbit_canonical_representative: "TensorLike"
    invariant_value_tuple: tuple[float, ...]
    invariant_id_tuple: tuple[str, ...]
    equivalence_proof: "EquivalenceProofRef"
    stability: OrbitStability = OrbitStability.UNKNOWN
    moduli_dimension: Optional[int] = None
    parameter_chart: Optional["ParameterChart"] = None
    domain_docstring: dict = field(default_factory=dict)
```

**How this answers `T-2026-05-07-ST-fire1-002`:** the homotopy-class gap and the SLOCC-orbit gap share **structure**, not just intent. Both are equivalence relations with continuous-deformation witnesses. Per `T-2026-05-08-ST-fire35-001`'s Aporia recommendation: **co-design a unified Structured-Equivalence-Class meta-primitive**:

```
StructuredEquivalenceClass
  ├── ambient_space
  ├── equivalence_relation_kind  (orbit | homotopy | n-isomorphism | bijection | intertwiner)
  ├── canonical_representative
  ├── witness_data               (group element | continuous deformation | n-cell tower | ...)
  └── invariant_separator_set    (functions distinguishing classes)
```

T#79 is the canonical algebraic-geometric instance; `T-ST-fire1-002` is the canonical topological instance; `T-ST-fire21-002` (A∞ arity-graded) is the canonical higher-coherent-algebra instance.

## 6. Calibration Anchor Notes

**Substrate-grade vs textbook-trivial:**
- *Substrate-grade:* "n=3: six SLOCC orbits (DVC 2000); n=4: nine continuous families (VDDV 2002) / eight mod permutation (Lamata 2007); n=5: orbit moduli is 16-dim positive-dimensional generic family; explicit invariant ring (Luque–Thibon 2006); AME subspace fully classified (arXiv:2507.02185)."
- *Substrate-grade:* "For n ≥ 5 there is no finite parameterization — orbit space is a (2^n − 3n − 1)-dim variety. Substitute moment-polytope description (Walter–Doran–Gross–Christandl 2013) for finite combinatorial proxy."
- *Textbook-trivial:* "GHZ vs W states." True only for n=3.
- *Trap (PATTERN_BASE_RATE_NEGLECT):* "There are exactly N classes for n qubits" framing.
- *Trap (PATTERN_CONDUCTOR_CONFOUND):* conflating discrete "atlas" enumeration with orbit count.
- *Trap (PATTERN_RANK_PARITY_LEAK):* SLOCC orbit invariants are graded polynomials of even degree.

**Canonical authors at varying canonicality:**
- **Cirac, Vidal, Dür** — n=3 founders, very high canonical-popular.
- **Verstraete** — n=4 founder, also tensor-network co-canonical.
- **Christandl, Walter, Gross, Doran** — entanglement-polytope route.
- **Luque, Thibon, Briand, Holweck** — invariant-theoretic line.
- **Lamata, León, Salgado, Solano** — inductive line.
- **Klyachko** — moment-polytope side.
- **Lévay, Sárosi** — fermionic / black-hole cross-canonicality.
- **Huber, Gühne, Siewert** — n=7 AME impossibility.

**Fabrication risks:**
1. Mis-attributing the n=4 result. VDDV (4-author, 2002).
2. Conflating orbit count with class-family count.
3. Inventing classifications for n ≥ 6.
4. Conflating LU and SLOCC.
5. Inventing "SLOCC functionals."
6. Inventing arxiv IDs.
7. Treating "SLOCC = QI problem only" — per HARD-5: SLOCC is **algebraic-geometric**.

## 7. Cross-References

**Within `aporia/mathematics/tensor_open_problems_v1.md`:**
- **#78 Holographic tensor network correspondence** — SLOCC invariants of cluster / AME states are HaPPY-code building blocks.
- **#80 Entanglement polytope characterization** — directly derived from T#79.
- **#81 Most-entangled state identification** — formulated as maximization over an SLOCC orbit.
- **#92 GCT VP vs VNP via padded permanent** — shares GIT framework. **R-GIT-product sub-tactic applies.**
- **#100 Invariant theory of tensor orbits** — umbrella problem of which T#79 is the n-qubit instance.
- Adjacent: #26, #31, #34, #56, #58, #83.

**Within `aporia/docs/attack_angle_taxonomy.md`:**
- **P03** — central reductive-orbit instance. **Recommend adding sub-tactic R-GIT-product** to P03 entry.
- P22, P28, P29, P31.

**Within `aporia/docs/deep_research_batch_tensor_priority_2026-05-09/`:**
- **`report_T28_asymptotic_spectrum.md`** — quantum-functional construction (CVZ 2017/2023) uses moment polytopes built from SLOCC orbits.
- **`report_T43_best_rank_r_existence.md`** — orbit-closure non-closure (de Silva–Lim 2008) is the rank-side analog.

**Capability-gap tickets anchored:**
- **`T-2026-05-07-ST-fire1-002`** — homotopy-class capability gap. T#79 is the algebraic-geometric sibling; recommend co-design of Structured-Equivalence-Class meta-primitive.
- **`T-2026-05-07-ST-fire21-002`** — A∞-algebra arity-graded operations.
- **`T-2026-05-08-ST-fire38-001`** — M_3 matrix-multiplication tensor encoding.
- **New candidate ticket `T-ST-T79-001 OrbitWitness primitive specification`**.
- **`T-2026-05-08-T038`** — Techne classification of 104 catalog entries. T#79 classifies as **SUBSTRATE-GAP / SHARED-PRIMITIVE**.

---

*Aporia, 2026-05-09*
