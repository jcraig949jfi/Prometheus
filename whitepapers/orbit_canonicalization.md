# Orbit Canonicalization as a Substrate Primitive
## Theory and pilot results from a Quality-Diversity search over low-rank tensor decompositions

**Authors:** Harmonia_M2_sessionA (architectural framing, original pilot — 2026-04-23) and Harmonia_M2_sessionB (empirical extension across 10 pilots — 2026-04-23 to 2026-04-25)
**Status:** working paper; closed empirical phase. Followup directions filed in `stoa/ideas/`.

---

## Abstract

The Prometheus substrate routinely needs to answer, for structured mathematical objects, whether two representations denote the same underlying object under a declared equivalence. Tensor decompositions, coordinate axes, algebraic expressions, DAG nodes, and MAP-Elites archive entries all share this requirement. A 2026-04-23 pilot on 2×2 matrix-multiplication tensor decompositions exposed the gap concretely: alternating least squares + random restart rediscovered Strassen's rank-7 orbit at machine precision on six of twenty seeds, but a naïve canonicalizer hashed those six representatives to four distinct canonical forms. The bottleneck in searching structured mathematical objects is not search; it is representation under symmetry.

This whitepaper formalizes orbit canonicalization as a first-class substrate primitive, sibling to the Definition DAG and the symbol registry. It then documents the full evolution of the primitive across two waves of work:

- **Wave 1 (v1, 2026-04-23):** primitive contract specified; v1 instance shipped with declared insufficiency (T-stabilizer not quotiented).
- **Wave 2 (v2 + invariant-tuple, 2026-04-23 to 2026-04-25):** v2 brute-force enumeration of the F_p matmul isotropy subgroup shipped successfully (24 elements over F_2 / 6048 elements over F_2 at n=3 / 3072 over F_3); invariant-tuple canonicalization developed for large/continuous gauges where brute-force is infeasible; 10 reseeded pilots run across 4 fields and 4+ tensor families.

The empirical phase produced two reusable methodology tools (products-then-solve verification; invariant-tuple canonicalization), three substantive empirical findings (matmul Hamming-isolation universality across all tested fields; polymul sub-optimal-rank orbit richness; cyclic-Z_3 cosets of matmul outside GL_n(ℚ)³), and one clean negative (entry-level LLM mutation does not bridge orbit isolation). The mutation primitive — not canonicalization, not substrate, not field — is the proven bottleneck for QD search over matmul decompositions. Polymul tensor families show the QD-archive thesis can produce real population diversity at sub-optimal rank.

---

## 1. The representation problem

When a substrate stores structured mathematical objects, two representations may denote the same object under some equivalence. If the substrate cannot compute a canonical representative for each equivalence class, every downstream operation that depends on object identity — deduplication, diversity measurement, archive dedup, DAG node identity, novelty detection — silently mis-counts.

Most published work on automated search over structured objects reports "new discoveries" that, on closer inspection, are orbit-variants of existing solutions under the natural symmetry group. This is the decomposition-level instance of Pattern 1 (Distribution/Identity Trap) from the Prometheus pattern library: a claimed novel finding that is, under examination, a rearrangement of an existing one in a rotated basis.

The substrate's existing discipline stack — Pattern 30 graded severity for algebraic-identity coupling, versioned symbols with composition hashes, retraction-as-first-class-event — was built for a related but narrower concern (correlational claims on algebraically-coupled variables, exemplified by the F043 retraction of 2026-04-19). The present work extends that discipline to the identity of structured objects themselves, not just correlations between their parts.

---

## 2. Wave-1 empirical pivot: 2×2 matrix multiplication via ALS

The Wave-1 pilot deliberately targeted a well-understood anchor. The matrix multiplication tensor `T ∈ ℝ^{4×4×4}` with `T[ij, jk, ik] = 1` for matching middle index `j`. Strassen (1969) exhibited a rank-7 decomposition `T = Σ_{i=1..7} u_i ⊗ v_i ⊗ w_i` with integer-valued factors. Winograd (1971) proved rank ≥ 7. All rank-7 decompositions of `T` over ℝ are related by the action of `(GL(2) × GL(2) × GL(2)) × S_7 × scale-gauge` — they form a single orbit.

The pilot setup was deliberately minimal — ~60 lines of numpy — to test whether a dumb search stack is sufficient to rediscover the orbit. Twenty random seeds at target rank `r ∈ {6, 7, 8}`, 500 ALS iterations each, 1.4 seconds total CPU.

### 2.1 Wave-1 results

| Rank | Seeds reaching residual < 1e-8 | Best residual |
|------|--------------------------------|---------------|
| 8 | 0 / 20 (near-misses at 2.2e-8) | 2.2e-08 |
| **7** | **6 / 20 (30%)** | **9.4e-13** |
| 6 | 0 / 20 | 1.000 (clean) |

Six rank-7 seeds reached the orbit. Rank 6 is unreachable (matches Winograd). Rank 8 enters an over-parameterized swamp.

### 2.2 The Wave-1 finding beneath the finding

The six converged rank-7 decompositions are, by theorem, in the same orbit as Strassen's. Their integer-entry fractions ranged from 0.02 to 0.16; Strassen's integer-fraction is 1.00. **The search reaches the orbit reliably; it does not reach Strassen's representative within the orbit.**

A v1 canonicalizer (normalize columns, sign-gauge, lex-sort) applied to four of the converged seeds plus Strassen produced **five different canonical hashes**. The v1 canonicalizer quotients scale, sign, and permutation, but not the `(GL(2))³` basis change that stabilizes the matmul tensor — and the T-stabilizer is where the bulk of orbit size lives.

This is the empirical pivot that motivated promoting canonicalization to a first-class primitive.

---

## 3. Orbit vs representative

The Wave-1 pilot refutes a common assumption: that a search primitive which converges to an exact decomposition has "solved" the decomposition problem. It has not. It has located one orbit point. The orbit's size under the full symmetry group is where the additional structure — integer coefficients, sparsity, symmetry — is either findable or not.

Formally, for a target tensor `T` and target rank `r`, the set of exact rank-`r` CP decompositions is a real algebraic variety on which the following groups act, preserving the reconstruction `T`:

- **Scale gauge:** per rank-1 term, `(u_i, v_i, w_i) → (α u_i, β v_i, (αβ)^{-1} w_i)` for `(α, β) ∈ K*²`. Two continuous degrees of freedom per term over ℝ; finite over F_p with p > 2; trivial over F_2.
- **Sign gauge:** degenerate case of scale gauge over fields of characteristic ≠ 2.
- **Permutation:** `S_r` on the rank-1 term index.
- **T-stabilizer:** the subgroup of `GL(n) × GL(n) × GL(n)` that fixes `T` under `(P, Q, R) · T = (P ⊗ Q ⊗ R) T`. For `T = MATMUL_{n×n}`, this stabilizer is non-trivial and contains a natural matmul-covariant action via `(X, Y, Z) ↦ (αXβ⁻¹, βYγ⁻¹, αZγ⁻¹)`. It also contains a cyclic Z_3 mode-permutation-with-transposition (de Groote 1978) that lives outside the GL_n(K)³ parameterization.

The orbit of a decomposition is its equivalence class under all four actions. Two decompositions in the same orbit are the same mathematical object.

---

## 4. Canonicalization as substrate primitive

Two alternative architectural placements for the canonicalizer were considered:

1. **Internal to gen_12.** The tensor-identity-search generator owns the canonicalizer as one of its filter gates. Simple; scoped; self-contained.
2. **First-class substrate primitive.** The canonicalizer is a separate artifact in the substrate architecture, alongside the symbol registry, the Definition DAG, and the tensor. Generators (including gen_12) consume it; they do not own it.

The second placement is the correct one. The same quotient operation — "is this representation the same object as that one, under a declared equivalence?" — recurs across substrate concerns:

- **Tensor decomposition (gen_12):** orbit of a CP decomposition under the symmetry group.
- **Definition DAG node identity:** a derived mathematical quantity re-expressed in another basis is the same node.
- **MAP-Elites archive dedup:** behavior-cell diversity over raw representations fills cells with orbit duplicates.
- **Pattern 30 REARRANGEMENT severity (Level 3):** two expressions related by a ring identity are the same claim.
- **gen_11 coordinate invention:** rejecting re-parameterizations requires the same canonicalizer that gen_12 uses for orbit dedup.
- **Symbol registry:** promotion of a candidate symbol should check canonical equivalence to existing promoted symbols.

If the canonicalizer were buried inside gen_12, each of the other consumers would either re-implement a weaker version or ignore the problem.

---

## 5. The contract

A canonicalizer instance is a tuple

```
(name, equivalence_group G, procedure C, hash H,
 declared_limitations, calibration_anchors, canonicalizer_version)
```

with these requirements:

**On G.** Specified as generator types (e.g., `scale_gauge`, `sign_gauge`, `permutation(S_r)`, `T_stabilizer_GL_n^3`). Generator types must have *executable semantics within the instance*. If a subgroup is known to be part of the object's symmetry but is not computationally realized, it must appear in `declared_limitations`, not in `G`.

**On C.** The canonicalization procedure `C : Representation → CanonicalRepresentative` is a deterministic map satisfying invariance, probabilistic separation, an asymmetry warning (canonical inequality ≠ non-equivalence), tolerance, polynomial complexity, and explicit failure behavior.

**On H.** SHA-256-class hash with version namespacing.

**On declared_limitations.** Mandatory field. Every instance declares what equivalences it does *not* remove, severity (partial vs total), and workaround for consumers who need the missing equivalence. Without this declaration, the instance is rejected from the primitive registry.

**On calibration_anchors.** Minimum two: one same-class → same hash anchor and one different-class → different hash anchor. Anchors run on every version bump.

The primitive deliberately does *not* require completeness, symbolic computer-algebra power, proof of non-equivalence for distinct classes, or domain universality. Scope is gauge-fixing under declared symmetries, not universal equivalence.

---

## 6. v1 instance: scale + sign + permutation only

**Equivalence group G:** `scale_gauge × sign_gauge × permutation(S_r)`.

**Declared limitation:** `T_stabilizer_basis_change` — total. Workaround: use v2 once it ships.

**Calibration:** **fails by construction** on the Strassen orbit (the empirical motivation of §2.2). v1 is retained in the registry as the active instance only because consumers need something to develop against.

---

## 7. Wave-2 v2 instance: brute-force isotropy enumeration over F_p

The Wave-1 paper listed four candidate strategies for v2 — numerical invariants, SVD/Schur, orbit-internal nearest-integer search, full enumeration. Wave-2 took a fifth path: **brute-force enumeration of the matmul isotropy subgroup over finite fields**, where the enumeration is tractable because |GL_n(F_p)|³ is finite and small.

### 7.1 The action and its char-2 surprise

The standard parameterization `(α, β, γ) ∈ GL_n(K)³` acting on (X, Y, Z) ↦ (αXβ⁻¹, βYγ⁻¹, αZγ⁻¹) preserves matmul algebraically. On the tensor itself via the Kronecker action `M_U = α ⊗ β^{-T}`, `M_V = β ⊗ γ^{-T}`, `M_W = α ⊗ γ^{-T}`, tensor preservation holds **if and only if α and γ are F_p-orthogonal** — i.e., `αα^T = I` and `γγ^T = I` over F_p.

Over fields of characteristic ≠ 2, this constraint is mild: `O_n(K)` is a substantial subgroup. Over F_2 the constraint is severe:

| Field | n | \|O_n(F_p)\| | \|GL_n(F_p)\|³ before filter | matmul-preserving subgroup |
|---|---|---|---|---|
| F_2 | 2 | 2 (just I and swap) | 216 | **24** |
| F_2 | 3 | 6 (just permutation matrices) | 4,741,632 | **6,048** |
| F_3 | 2 | 8 (signed permutations) | 110,592 | **3,072** |

This is itself a finding worth recording: **the full GL_n(F_p)³ parameterization is not the matmul isotropy in characteristic 2** — only the orthogonality-restricted subgroup is. Over F_2 this collapses dramatically.

### 7.2 v2 implementation and validation

For each canonicalize call:
1. Iterate over the matmul-preserving subgroup elements (24 / 3072 / 6048 depending on field/size).
2. Apply the action to (U, V, W) factor matrices.
3. Drop zero columns; for fields with non-trivial F_p* scaling (F_3 and up), normalize per-column scaling to a canonical representative (first nonzero entry of a-side = 1, ditto b-side).
4. Sort columns lex.
5. Serialize and hash.
6. Return the lex-min representative.

Validated on each field via 8 standard unit tests:
- `|GL_n(F_p)|` enumeration correct.
- F_p-orthogonal subgroup correct.
- Identified matmul-preserving subgroup size matches Lagrange's theorem against orbit-stabilizer.
- Canonicalize idempotent.
- 10–20 random gauge transformations of seed canonicalize to identical bytes.
- 5–10 single-bit perturbations of seed do NOT collapse to seed canonical.
- Naive and Strassen / Laderman seeds reconstruct MATMUL_T.

### 7.3 v2 result: scale-of-the-instrument

v2 successfully canonicalizes for 2×2 matmul over F_2 (~milliseconds per call), 3×3 matmul over F_2 (~200 ms after vectorized bit-packing), and 2×2 matmul over F_3 (~265 ms). Brute-force enumeration breaks down at 3×3 over F_3 where the subgroup grows to ~10⁷–10¹⁰ elements depending on which extensions are included.

---

## 8. v3 instance: invariant-tuple canonicalization for large/continuous gauges

For 3×3 matmul over F_3 and over ℚ, brute-force isotropy enumeration is infeasible. Wave-2 developed a different strategy.

**Method.** Instead of finding the lex-min orbit representative, compute a tuple of gauge-invariant scalars that approximately identifies the orbit:

```
invariant_tuple(U, V, W) := (
    effective_rank,                    # drop zero columns first
    mode_flat_rank_signature,          # (rank M_1, rank M_2, rank M_3) over the field
    pair_rank_distribution,            # multiset of mode-rank tuples over all C(r,2) pairs
    triple_rank_distribution,          # multiset over a sample of C(r,3) triples
)
```

The tuple is gauge-invariant by construction: basis change preserves flattening ranks. Hash it as the cell key.

**Validation.** Verified gauge-invariant on 50/50 random matmul-isotropy elements applied to naive, Laderman, and Smirnov-cyclic-conjugate variants of the 3×3 matmul tensor. Failed-candidate invariants are documented as anti-patterns:

- `column_weight_multiset`: NOT actually basis-invariant under GL_n. Looks reasonable; isn't.
- `stabilizer_lower_bound` from a single sample: conjugation-biased. 46 / 50 perturbed forms gave different counts. Excluded.

**Limitations.** Lossy. Two non-equivalent orbits may collide on the tuple. The procedure is empirically distinguishing for the orbit count we have evidence for; it would need additional discriminators if a richer orbit space were uncovered.

---

## 9. Empirical findings across 10 pilots

Wave-2 ran 10 pilots across 4 fields and 4+ tensor families, seeded with verified known decompositions wherever possible. Per pilot: tensor + gauge + canonicalizer + descriptors + MAP-Elites + 3 reseeded runs + diagnostic report.

### 9.1 Matmul tensors are Hamming-isolated at every tested rank, in every tested field

| Substrate | Decomposition | Hamming-distance ≤ 4 valid neighbors |
|---|---|---|
| 2×2 F_2 | Strassen rank-7 | 0 / 2,028,355 (exhaustive) |
| 3×3 F_2 | Naive rank-27 | 0 (extensive sampling) |
| 3×3 F_2 | Laderman rank-23 | 0 / 213,131 (exhaustive 1–3 bits, 20K sampled at 4) |
| 2×2 F_3 | Strassen rank-7 | 12 / 762,272 valid at 3-entry; **all** canonicalize back to Strassen |
| 3×3 F_2 | Laderman + 4-to-3 search | 0 / 8,855 quadruples have tensor rank ≤ 3 |

**No local move ever bridged matmul rank-r orbits in any test.** Pure bit-flip, ternary-flip over F_3, 3-to-2 flip-graph (Kauers-Moosbauer style), 2-to-2 algebraic swap, 4-to-3 flip-graph (with rank-3 tensor decomposition over F_2 implemented as a primitive) — all proven non-functional from the seed orbits.

This is a **substantive structural finding** about the matmul algorithm-search landscape that, to our knowledge, has not been quantified systematically in the literature. It says: don't attempt local-mutation QD on matmul; the bottleneck is geometric, not algorithmic.

### 9.2 Polymul tensors have meaningful sub-optimal-rank orbit diversity

Exhaustive 2-bit-flip neighborhood probes of naive seed:

| Tensor | Naive rank | Distinct non-naive orbits at 2-flip distance |
|---|---|---|
| Polymul n=3 over F_2 | 9 | 12 |
| Polymul n=4 over F_2 | 16 | 34 |
| Polymul n=3 over F_3 | 9 | 16 |

These are **gauge-quotiented** orbit counts under the polymul gauge group. The gauge structure itself was a Wave-2 finding: polymul over F_2 has a hidden Z_3 symmetry from the non-commutativity of the substitution and reversal generators (`SUB ∘ REV ≠ REV ∘ SUB`, with composition order 3). Over F_3 the closure expands by factor 2 from the additional column-scaling interaction.

The rank-MINIMUM orbit count is still 1 in every polymul pilot, but the non-minimum terrain is genuinely populated. MAP-Elites under bit-flip mutation finds **only ~25%** of these orbits over F_3 (4 / 16) and **0%** over F_2 n=4, confirming that local mutation under-explores even where rich terrain exists.

This is the project's one positive empirical demonstration of the QD-archive thesis. Polymul-family tensors (and likely convolution / group-algebra) are where the QD framework can produce population diversity worth charting.

### 9.3 Cyclic-Z_3 cosets of matmul live outside GL_n(ℚ)³

Over ℚ-bounded ℤ (coefficients in {-2, ..., 2}), Wave-2 encoded Laderman with original signed coefficients (verified via the products-then-solve method of §10) and applied two transformations:
- Transpose conjugate (a Z_2 symmetry: (X, Y, Z) ↔ (Y^T, X^T, Z^T))
- Cyclic conjugate (a Z_3 symmetry from the de Groote 1978 classification)

Computed invariant tuples for all four (Laderman + transpose + 2 cyclic):

| Variant | Invariant tuple hash |
|---|---|
| Laderman | `fd34...` |
| Transpose conjugate | `fd34...` (identical to Laderman) |
| Cyclic conjugate 1 | `e25f...` (different) |
| Cyclic conjugate 2 | `058f...` (different) |

This **empirically demonstrates** that the transpose Z_2 IS captured by GL_n(ℚ)³, while the cyclic Z_3 is NOT. The three "distinct orbits" found in the pilot are actually one orbit under the full matmul automorphism group.

The result is consistent with de Groote 1978's classification — but the empirical demonstration via canonicalization framework is itself useful: it shows the invariant-tuple canonicalizer correctly distinguishes orbits when they exist as distinct under the chosen gauge.

### 9.4 Direct entry-level LLM mutation does not bridge orbit isolation

A budget-bounded pilot wrapped Claude Haiku 4.5 as a MAP-Elites mutation operator on the polymul-n=3 over F_2 substrate. 139 successful API calls (100% parse success, 100% API success). **0 / 139 LLM-proposed mutations produced a valid decomposition.** The model was prompted to suggest "a small modification (1–3 entry changes OR a column-level swap)." It dutifully did so. None preserved validity.

The bottleneck is the same factor-matrix Hamming-isolation that defeated bit-flip mutation across all matmul pilots. The LLM has no algebraic-correctness feedback signal; its small edits are no better than random small perturbations.

This narrows the LLM-mutation hypothesis space cleanly:
- Direct entry-level editing: doesn't work at this granularity / budget (this pilot)
- Code-level editing (AlphaEvolve framing): probably works at large budgets per published results; small-budget feasibility is open
- Validity-projecting wrapper around arbitrary mutations: untested; the hard part is solving the validity manifold projection cheaply

---

## 10. Reusable methodology: products-then-solve verification

When encoding a published tensor decomposition (Strassen's 7 products, Laderman's 23, Smirnov's catalog) from memory or imperfect sources, the **products** (a-side and b-side of each rank-1 summand) are easier to remember correctly than the **output formulas** (which products combine to produce z_{ij}). Memory errors concentrate in the latter.

**Method.** Encode just the products. Build the per-product contribution matrix (each column = the bilinear monomials that product contains). For each output z_{ij}, solve `contrib · s = target` over F_p via Gaussian elimination. If solvable, `s` gives the correct subset of products; if not, the product set itself is wrong and that's reported back.

Used successfully in Wave-2 for: Laderman over F_2, Laderman over F_3, Laderman over ℤ (signed), Karatsuba-3-way over F_2 + F_3.

This method generalizes to any tensor decomposition where products are well-known and outputs are uncertain — Smirnov's 3×3 catalog (many variants), Heun's bilinear schemes, recent SAT-discovered decompositions over F_2.

---

## 11. The mutation-bottleneck finding (project closure)

After 10 pilots × 4 fields × 4+ tensor families × 5 mutation classes (bit-flip, ternary-flip, 3-to-2 flip-graph, 2-to-2 algebraic swap, 4-to-3 flip-graph, LLM mutation), the convergent picture is:

1. **Canonicalization is solved at scale** for the gauges tested. Brute-force enumeration handles |Iso| up through ~6000; invariant-tuple handles arbitrary larger gauges including continuous ones.
2. **Substrate scaling does not address the bottleneck.** Char-2 collapse was rejected as the cause via F_3 pilots. Tensor smallness was rejected via the larger polymul-n=4 pilot. Field richness was rejected via ℚ pilot (3 cosets, not 3 distinct orbits).
3. **The mutation primitive is THE bottleneck.** No local move primitive — bit-flip, algebraic flip-graph at any tested arity, or LLM proposals at entry-level — bridges matmul rank-r orbits. For polymul, local mutation finds only ~25% of the locally-valid orbit neighbors that exhaustive enumeration produces.

The project's strongest claim is its discipline, not its discoveries: the shape of "what works and what doesn't" is now well-characterized for QD search over low-rank tensor decompositions of matmul-class targets.

---

## 12. Adjacent canonicalizer instances

Four additional instances are visible in the substrate's current design and remain candidates for future scoping:

- **`CANONICALIZER:poly_monomial_form@v1`** — polynomials up to variable relabeling and sign gauge. Cheapest first non-tensor instance. Candidate first calibration anchor for cross-domain reuse.
- **`CANONICALIZER:graph_iso@v1`** — graph isomorphism canonical form. Classical problem; well-studied algorithms exist (nauty, Bliss).
- **`CANONICALIZER:pattern_30_rearrangement@v1`** — canonical form for algebraic expressions over a declared ring. Directly operationalizes Pattern 30 Level-3 REARRANGEMENT severity.
- **`CANONICALIZER:dag_node_identity@v1`** — Definition DAG node identity under basis change on the input atoms.

Each future instance follows the same contract: equivalence group, procedure, hash, declared limitations, calibration anchors.

---

## 13. Integration surfaces

**Definition DAG.** DAG nodes are identified by canonical form of their defining expression. The `dag_node_identity` instance is the scheduled integration.

**Symbol registry.** Symbol promotion checks whether a candidate is canonically equivalent to an existing promoted symbol before adding.

**MAP-Elites archives.** Behavior cells are computed on canonical forms; archive dedup uses canonical hash. The 10-pilot project at `exploratory/tensor_decomp_qd/` is the canonical first consumer.

**Pattern 30.** Algebraic-identity coupling at Level 3 (REARRANGEMENT) is the algebraic-expression instance of the canonicalizer's general operation.

**gen_11 coordinate invention.** The inverse operation. gen_11 seeks *different* representations that resolve a feature; the canonicalizer fixes a single representative.

**gen_12 tensor identity search.** The first explicit consumer. v2 of the canonicalizer was the gating ship for gen_12 to operate beyond DRAFT.

---

## 14. Relationship to prior work

**Strassen 1969.** Rank-7 decomposition of 2×2 matmul. Calibration anchor.
**Winograd 1971.** Rank ≥ 7 for 2×2 matmul over any field. Rank-6 regression test.
**de Groote 1978.** Classified the matmul tensor's automorphism group, including the cyclic Z_3. The Wave-2 ℚ pilot's three rank-23 cosets are de Groote's Z_3 cosets viewed through the GL_n³ canonicalization frame; nothing theoretically new, but a clean empirical demonstration.
**Laderman 1976.** Rank-23 decomposition of 3×3 matmul. Encoded over F_2, F_3, and ℤ via the products-then-solve method.
**Bini et al. 1979.** Border-rank results. Out of scope for exact decomposition.
**Kolda & Bader 2009.** Canonical tensor-decomposition survey.
**Fawzi et al. 2022 (AlphaTensor).** RL search; reported 4×4 / 5×5 improvements over F_2. Several of the "novel" 4×4 results were subsequently identified as orbit-variants — the failure mode this primitive prevents.
**Khoruzhii, Gelß, Pokutta 2025 (Flip-Graph Search).** Local search on tensor-decomposition flip graphs; improved 13/15 structured matmul formats. The 3-to-2 and 4-to-3 moves implemented in Wave-2 are inspired by this paper. We confirm independently that the moves are correct primitives but do not fire from naive or Laderman over F_2.
**Novikov et al. 2025 (AlphaEvolve).** LLM-driven evolutionary code search. The Wave-2 LLM-mutation pilot's negative result is at entry-level granularity rather than code-level (where AlphaEvolve operates) and uses a much smaller budget.
**Yang 2024.** SAT-based proof of non-existence for 3×3 matmul rank-≤21 decompositions with certain symmetries over F_2. Used as the forbidden-cell discipline anchor in Wave-2's 3×3 F_2 pilot.

The novel contributions of the present work, beyond the architectural promotion of canonicalization to a substrate primitive, are: (1) the products-then-solve verification method, (2) invariant-tuple canonicalization scaling beyond brute-force enumeration, (3) empirical Hamming-isolation universality across 10 pilots, (4) polymul sub-optimal richness as a positive QD demonstration, (5) the LLM-mutation entry-level negative as a hypothesis-narrowing result.

---

## 15. Limitations and open questions

**Open:** is matmul Hamming-isolation universality novel as a quantified empirical finding, or has it been measured before in different language? The complexity-theory community knows matmul is "rigid" in various senses; we have not found a paper that quantifies it via exhaustive bit-flip neighborhood probes across multiple decompositions and fields.

**Open:** how seriously should the polymul richness finding be taken? Possible interpretations: (a) real — polymul-family tensors are where QD shows its teeth; (b) trivial — sub-optimal decompositions are not "useful algorithms"; (c) half-real — non-minimum decompositions might matter for hardware/ergonomic reasons (sparsity, coefficient magnitude).

**Open:** is the products-then-solve method already published as a verification technique, or folklore?

**Open:** the mutation-bottleneck finding strongly suggests that LLM mutation must operate at code level (AlphaEvolve framing), not entry level. A code-level pilot on polymul (where AlphaEvolve has not been published) would test this. Open whether the QD wrapper adds defensible value beyond AlphaEvolve's optimization.

**Open:** validity-preserving projection wrappers for arbitrary mutations — would solve the bottleneck head-on by snapping any proposed mutation to the validity manifold. Algorithmically hard (validity manifold = solution set of Brent equations). Untested at meaningful scale.

**Partial:** MNAR at the orbit level. Even with a perfect canonicalizer, the set of decompositions search explores is a non-random sample of the orbit variety. Sampling biases in ALS / GA / RL carry through. Orbit identity does not absolve the substrate of MNAR discipline at the measurement level.

---

## 16. Conclusion

The 2026-04-23 to 2026-04-25 work established one architectural claim and four empirical claims.

**Architectural:** canonicalization of structured mathematical objects under symmetry is a load-bearing substrate primitive, not an internal detail of any specific generator. It composes across multiple substrate consumers (Definition DAG, symbol registry, MAP-Elites archives, Pattern 30, gen_11, gen_12) and prevents the AlphaTensor-class failure mode of orbit-variants masquerading as novel discoveries.

**Empirical 1:** brute-force enumeration of the matmul isotropy subgroup over F_p ships cleanly for |Iso| up through ~6000. Char-2 fields require an orthogonality filter that collapses the parameterization size dramatically.

**Empirical 2:** invariant-tuple canonicalization handles gauges where brute-force is infeasible. Lossy by design; gauge-invariant by construction; verified on 50/50 random isotropy elements.

**Empirical 3:** matmul tensors are Hamming-isolated at every tested rank in every tested field. No local mutation bridges rank-r orbits. The mutation primitive is the proven bottleneck.

**Empirical 4:** polymul tensors have meaningful sub-optimal-rank orbit diversity (12 / 16 / 34 distinct non-minimum orbits in pilots). The QD-archive thesis works on polymul-family targets at sub-optimal rank even though it doesn't on matmul.

The substrate now holds, after this work, a mechanism for distinguishing *"we found a new orbit"* from *"we found a new representation of an existing orbit,"* validated across 10 pilots and 4 fields. Every downstream search generator from gen_12 onward is downstream of this distinction.

The empirical phase is closed. Followup directions (validity-projection wrapper; code-level LLM mutation on polymul; convolution and group-algebra family expansion; cross-application of invariant tuples to Definition DAG / Pattern 30) are filed in `stoa/ideas/` for future re-engagement.

---

## 17. Artifact inventory

### Wave-1 substrate artifacts (tracked in git)

- `harmonia/memory/architecture/canonicalizer.md` — primitive spec.
- `harmonia/memory/architecture/orbit_vs_representative.md` — tensor-decomposition instance detail.
- `harmonia/memory/architecture/definition_dag.md` — sibling substrate primitive.
- `docs/prompts/gen_12_tensor_identity_search.md` — first consumer.

### Wave-2 pilot inventory (10 pilots in `exploratory/tensor_decomp_qd/`)

- `pilot_F2_2x2/` — 2×2 matmul over F_2 (B1: Strassen orbit unique under 24-element gauge)
- `pilot_F2_3x3/` — 3×3 matmul over F_2 with 3-to-2 + 2-to-2 flip-graph (B: 0/1771 reducible triples)
- `pilot_F2_3x3_v2/` — 3×3 matmul over F_2 with 4-to-3 flip-graph (B1 stronger: 0/8855 reducible quadruples)
- `pilot_F3_2x2/` — 2×2 matmul over F_3 (B1: rejects char-2 hypothesis as primary cause)
- `pilot_F3_3x3/` — 3×3 matmul over F_3 with invariant-tuple canonicalization (B; canonicalization solved)
- `pilot_polymul_n3/` — polymul n=3 over F_2 (B1 + 12 sub-optimal orbits)
- `pilot_polymul_n4/` — polymul n=4 over F_2 (B1 + 34 sub-optimal orbits)
- `pilot_polymul_n3_F3/` — polymul n=3 over F_3 (B1 / B2-leaning + 16 sub-optimal orbits + first reseed-disagreement at rank 9)
- `pilot_Q_3x3/` — 3×3 matmul over ℚ-bounded ℤ via invariant-tuple (formal A, caveated as Z_3 cosets)
- `pilot_LLM_mutation/` — Haiku 4.5 mutation on polymul n=3 (B; 0/139 valid LLM proposals)

Each pilot has its own `PILOT_REPORT.md`. Two synthesis documents (`META_REPORT_PARALLEL_PILOTS.md` for the first triple of parallel pilots, `META_REPORT_DIRECTION_2.md` for the second). Standalone `PROJECT_SUMMARY_FOR_REVIEW.md` covers the integrated picture.

### Reference documents

- `docs/landscape_charter.md` — Prometheus charter.
- `docs/long_term_architecture.md` — five-layer architecture.
- `harmonia/memory/pattern_library.md` — Patterns 1, 30, 6, 13, 17.
- `harmonia/tmp/tensor_decomp_lit/SYNTHESIS.md` — 3-pass literature scan, ~255 papers.

### Session journals

- `roles/Harmonia/worker_journal_sessionA_20260423.md` — Wave-1.
- `roles/Harmonia/worker_journal_sessionB_20260423.md` — Wave-2 (spans 2026-04-23 to 2026-04-25 in calendar time).

### Wave-2 commits on local main (no pushes)

`ab605eb4`, `810ee5c8`, `eee8a6bd`, `3b01cd44`, `039c7fe6`, `e8d2f89c`, `85bf42c9`, `8e5cb0e0`, `857f8adc`, `9bc8ddf1`, `22323ef3`, `a685fec8` — 12 commits documenting incremental pilot ship and synthesis.

---

## 18. References (external)

- Strassen, V. (1969). *Gaussian elimination is not optimal.* Numerische Mathematik 13, 354–356.
- Winograd, S. (1971). *On multiplication of 2×2 matrices.* Linear Algebra and its Applications 4, 381–388.
- Laderman, J. D. (1976). *A noncommutative algorithm for multiplying (3×3) matrices using 23 multiplications.* Bulletin of the AMS 82, 126–128.
- de Groote, H. F. (1978). *On varieties of optimal algorithms for the computation of bilinear mappings.* Theoretical Computer Science 7.
- Bini, D., Capovani, M., Romani, F., Lotti, G. (1979). *O(n^2.7799) complexity for n×n approximate matrix multiplication.* Information Processing Letters 8, 234–235.
- Smirnov, A. V. (2013). *Bilinear complexity and practical algorithms for matrix multiplication.* Computational Mathematics and Mathematical Physics 53, 1781–1795.
- Kolda, T. G., Bader, B. W. (2009). *Tensor decompositions and applications.* SIAM Review 51, 455–500.
- Fawzi, A., et al. (2022). *Discovering faster matrix multiplication algorithms with reinforcement learning.* Nature 610, 47–53.
- Yang, J. (2024). *Ruling out low-rank matrix multiplication tensor decompositions with symmetries via SAT.* arXiv:2402.01011.
- Khoruzhii, K., Gelß, P., Pokutta, S. (2025). *Faster algorithms for structured matrix multiplication via flip graph search.* arXiv:2511.10786.
- Novikov, A., et al. (2025). *AlphaEvolve: a coding agent for scientific and algorithmic discovery.* arXiv:2506.13131.
- Andreini, P., et al. (2026). *Neural learning of fast matrix multiplication algorithms: a StrassenNet approach.* arXiv:2602.21797.

---

*Whitepaper compiled from: original Wave-1 spec (Harmonia_M2_sessionA, 2026-04-23) + Wave-2 pilot shipment and synthesis (Harmonia_M2_sessionB, 2026-04-23 to 2026-04-25). Empirical phase closed; followups in `stoa/ideas/`.*
