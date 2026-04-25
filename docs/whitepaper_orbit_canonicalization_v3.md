# Orbit Canonicalization as a Substrate Primitive (v3)
## A whitepaper on tensor identity search in Prometheus
### 2026-04-25 — Harmonia_M2_sessionA

*v3 supersedes v2 (`whitepaper_orbit_canonicalization_v2.md`). v2 retained for audit. v3 incorporates: (a) reviewer feedback on v2 (theorem language, hash spec, Pattern 30 boundary, AlphaTensor framing, primitive-portability stratification); (b) substantive empirical findings from continued Phase 2 work that materially changed what v2 claimed about the shipped `tensor_decomp_identity@v2` instance.*

**Note to reviewer:** v2 made a strong claim about v2-the-instance that the empirical follow-up does not support. v3 is the correction. The correction is large enough to call out at the top: **v2-the-instance is not an orbit canonicalizer in the strict group-theoretic sense — it is a tensor-rank fingerprint**. The whitepaper-level architectural claim (canonicalizer as substrate primitive, Type A / Type B split, declared-limitations as guardrail) survives; the specific instance's standing changes.

Inline `**[Q: ...]**` markers and §15 aggregated questions for review.

---

## Abstract

Many Prometheus substrate operations — catalog dedup, DAG node identity, MAP-Elites archive diversity, algebraic-rearrangement detection — require answering *"are these two representations the same object under a declared equivalence?"* Without a principled primitive for that question, every consumer re-implements a weaker version and they silently disagree.

A 2026-04-23 pilot on 2×2 matrix-multiplication tensor decompositions made the gap concrete. A minimal search stack rediscovered Strassen's rank-7 orbit at machine precision in 6 of 20 random seeds. Four v1 canonical hashes (scale + sign + permutation gauge) on those seeds produced four distinct values; Strassen's added a fifth. Three more strategies were attempted; the third — a two-scalar `(inv1, inv2)` invariant fingerprint — collapsed all five to one hash. v2 of this whitepaper called that ship a Type A canonicalizer.

Two follow-up experiments at 2026-04-25 reframed the v2 claim. (a) Differential-evolution global search over `GL(2,ℝ)³` failed to connect any pair of converged seeds (or any seed to Strassen) at residuals approaching zero — sanity-checked by recovering small known actions cleanly. (b) The `(inv1, inv2)` multiset structure is *algebraic*: every rank-7 decomposition of the 2×2 matmul tensor has exactly one full-rank rank-1 term and six rank-deficient terms, so the invariants are constant on the variety `V_T(7)` by construction.

The corrected claim: **v2-the-instance is a class-function of `(T, rank)`, not a quotient under a group action**. It identifies "this is a rank-r decomposition of T" — a useful tensor-rank fingerprint, but not an orbit canonicalizer. The substrate-primitive whitepaper claim survives; the instance's contract was over-narrowed.

This whitepaper formalizes orbit canonicalization as a substrate primitive in three subclasses (group-quotient, partition-refinement, ideal-reduction); registers `tensor_decomp_identity@v2` honestly as a Type A *fingerprint* under the variety equivalence rather than the GL-orbit equivalence; documents `poly_monomial_form@v1` as the cross-domain Type A group-quotient instance; and names the open architectural question that the pilot evidence raises: do rank-r decompositions of `T` over ℝ form a single connected component under `GL(n,ℝ)³`, or multiple? The pilot empirics suggest multiple. v3 names the question rather than answering it.

---

## 1. The representation problem

When a substrate stores structured mathematical objects, two representations may denote the same object under some equivalence. If the substrate cannot compute a canonical representative for each class, every downstream operation that depends on identity — deduplication, diversity measurement, archive keys, DAG nodes, novelty detection — silently mis-counts.

A recurring failure mode in recent automated-discovery work (AlphaTensor being the prominent anchor; see §11) is reporting "new discoveries" that on examination are orbit-variants of existing solutions under the natural symmetry group. This is the decomposition-level instance of Pattern 1 (Distribution/Identity Trap) in the Prometheus pattern library.

Prometheus's existing discipline — Pattern 30 graded severity for algebraic-identity coupling, versioned symbols with composition hashes, retraction-as-first-class-event — was built for a narrower concern: correlational claims on algebraically-coupled variables (F043 retraction, 2026-04-19). The present work extends that discipline to identity of structured objects themselves under declared symmetry, formalized as a substrate primitive.

---

## 2. The empirical pivot: 2×2 matrix multiplication

The pilot targets a well-understood anchor. Matrix multiplication of 2×2 matrices is encoded as `T ∈ ℝ^{4×4×4}` with `T[ij, jk, ik] = 1` for matching middle index, zero otherwise. Strassen (1969) exhibited a rank-7 decomposition with integer factors. Winograd (1971) proved rank ≥ 7. Whether all rank-7 real decompositions of `T` lie in a single `GL(2,ℝ)³` orbit is an open question for this whitepaper — de Groote (1978) and follow-ups establish single-orbit results over ℂ, but real orbits can in principle split into multiple components even when the complex orbit is irreducible. The present empirics suggest splitting; §6 names this as the unresolved question.

Pilot setup: twenty random ALS seeds at target rank `r ∈ {6, 7, 8}`; 500 iterations; total runtime 1.4 seconds.

### 2.1 Results (ranks 6, 7, 8 over ℝ)

| Rank | Seeds reaching residual < 1e-8 | Best residual | Interpretation |
|---|---|---|---|
| 8 | 0/20 (near-misses at 2e-8) | 2.24e-08 | Over-parameterized; known ALS swamp |
| 7 | 6/20 (30%) | 9.4e-13 | Strassen orbit reached at machine precision |
| 6 | 0/20 | 1.000 (sharp clustering) | Matches Winograd lower bound |

Rank-6 residual concentration at 1.000 depends on tensor normalization (`‖T‖_F = 2√2 ≈ 2.83`). The specific value 1.000 is not universal — it is the squared-Frobenius deficit floor under this measurement. Frozen as a regression test: any future search primitive reporting rank-6 residual < 1e-6 has a bug, not a finding.

### 2.2 Orbit, not representative

Six rank-7 ALS-converged decompositions have integer-fractions in 0.02–0.16. Strassen's has 1.00. ALS from Gaussian initialization has Lebesgue-measure-zero chance of landing on an integer-valued representative within a continuous orbit, so the absence of integer structure in ALS output is tautological, not surprising.

The substantive claim: reaching the orbit is not the same as reaching a representative. A generator that claims "novelty" from the first without fixing the second is measuring coordinate artifacts. This is the architectural thesis the canonicalizer primitive is designed to enforce.

### 2.3 v1 canonical-hash collision test (2026-04-23)

A v1 canonicalizer (scale + sign + permutation gauge, no basis alignment) applied to four machine-precision seeds and Strassen produced **five distinct hashes**. v1 is therefore strictly insufficient as a Type A canonicalizer for the 2×2 matmul rank-7 case.

What v1's failure does *not* establish, the v2 whitepaper drew tighter conclusions than the evidence supports. The five-hash result is consistent with: (a) v1 not quotienting the T-stabilizer subgroup; (b) the seeds being numerically slightly off-orbit; (c) the four seeds residing in genuinely distinct GL(2,ℝ)³-orbit components even at machine precision. v2 implicitly assumed (a). v3 §6 documents follow-up tests that ruled out (a) and (b) and made (c) the live hypothesis.

---

## 3. Orbit vs representative

For a target tensor `T` and rank `r`, the exact rank-`r` CP decompositions form a real algebraic variety `V_T(r)`. Several groups act on this variety and preserve `T`:

- **Scale gauge** — per term: `(u_i, v_i, w_i) → (α u_i, β v_i, (αβ)^{-1} w_i)` for `(α, β) ∈ ℝ*²`.
- **Sign gauge** — degenerate scale; called out separately because integer bases prefer it.
- **Permutation** — `S_r` on the rank-1 term index.
- **Connected `GL(n,ℝ)³` matmul-covariant action** — `A → PAQ⁻¹, B → QBR⁻¹, C → P⁻ᵀCRᵀ`. The `P⁻ᵀCRᵀ` form on the third factor (not `PCR⁻¹`) preserves the Frobenius pairing `⟨AB, C⟩` that defines matmul. Empirically verified to preserve T at residual ~1e-15 for random `(P, Q, R) ∈ GL(2,ℝ)³`.

The original v2 whitepaper additionally invoked a `Z₂ × Z₃` discrete component (transpose, factor-role cyclic permutation). 2026-04-25 follow-up empirics show this is incorrect at the decomposition-factor level: cyclic rotation of `(A, B, C)` factors does NOT preserve T (residual 3.46 against original T); transpose likewise. These discrete operations act on the *tensor space* (relabeling modes gives a different labeled tensor), not on decompositions of fixed-labeled `T`. **[Q1: this is a correction from v2. The discrete symmetry framing in v2 was a wrong-pointer; please confirm the corrected reading.]**

So under the *fixed-label* T, the relevant group acting on decompositions is `(GL(n,ℝ)³ × scale_gauge × S_r)`. Whether `V_T(r)` is a single orbit under this group action is the open structural question §6 returns to.

---

## 4. The contract (v0.3 stratified)

A canonicalizer instance is a tuple

```
(name, type, subclass, equivalence E, procedure C, hash H (Type A only),
 secondary_objective (Type B only),
 declared_limitations, calibration_anchors, canonicalizer_version)
```

### 4.1 Two types (Type A / Type B)

- **Type A — canonical identity.** Deterministic quotient producing a hashable canonical representative for each equivalence class. Hash equality iff equivalence class equality (modulo separation bound on H).
- **Type B — preferred representative.** Optimization inside an already-identified class against a declared secondary objective. Output is for display, not identity. Uniqueness not required.

**Composition rule.** Type B always consumes Type A output. Running Type B alone on raw input is forbidden because the class Type B optimizes within is not well-defined without Type A's quotient.

### 4.2 Three subclasses (new in v3 per James 2026-04-24 design)

The contract is shaped by what kind of structure the equivalence has. Three subclasses, each with its own verification story:

- **`group_quotient`** — equivalence `E = G·x` for an executable group `G` with named generators. Verification: per-generator invariance check on `C`. Examples: `tensor_decomp_identity@v1` (declared `G` = scale × sign × permutation; declared limitation: T-stabilizer not quotiented), `poly_monomial_form@v1` (declared `G` = variable-permutation × sign), `dag_node_identity@v1` (basis change on input atoms).
- **`partition_refinement`** — equivalence by an algorithm that terminates at a unique-by-construction representative, not necessarily expressible as a group quotient. Verification: algorithm-correctness proof or appeal to a published canonical-form algorithm. Examples: `graph_iso@v1` (nauty/Bliss partition refinement + lex labeling).
- **`ideal_reduction`** — equivalence by ideal membership in a declared ring. Verification: reduction-to-normal-form correctness against a Gröbner basis (or equivalent). Examples: `pattern_30_rearrangement@v1` (algebraic expressions over a declared ring).

Each subclass carries its verification semantics. The base contract requires every instance to declare which subclass applies. Cross-subclass instance comparisons are forbidden — a `group_quotient` hash is never directly compared to a `partition_refinement` hash; namespacing by `(subclass, name, version)` enforces this.

The stratification means v3 adds *one architectural concept* (subclass tagging) rather than two competing contracts. Existing instances slot in by subclass; new instances pick the subclass whose verification story applies. **[Q2: is the three-subclass shape stable, or are there structures (e.g., topological canonical forms, model-theoretic equivalences) that don't fit any of these three?]**

### 4.3 On the equivalence E — declared, possibly non-group

For `group_quotient` instances, `E = G·x` where `G` has executable semantics. Generator types in `G` must have executable semantics within the instance; if a subgroup is part of the object's symmetry but not computationally realized, it must appear in `declared_limitations`, not in `G`.

For `partition_refinement` instances, `E` is the equivalence relation defined by the refinement algorithm's terminal labeling. Explicit description of the relation is required even if the algorithm is the witness.

For `ideal_reduction` instances, `E` is membership-in-the-same-cosrt of the declared ideal. The ideal must be specified (Gröbner basis or generator list).

### 4.4 On C — invariance, separation, asymmetry, tolerance, failure, failure stability

(Unchanged from v2.) Invariance, probabilistic separation, asymmetry warning (canonical inequality does not imply non-equivalence), tolerance, complexity, failure behavior with `(failure, reason)` return, and failure-stability under tolerance.

### 4.5 On H — hash contract

Deterministic serialization, namespacing by `(subclass, name, canonicalizer_version)`, tolerance pinning. Specific cryptographic primitive is implementation detail.

### 4.6 On declared_limitations — the guardrail

Mandatory. Every instance declares what equivalences it does *not* remove, severity (partial vs total), and workaround. Absence rejects the instance from registry.

### 4.7 What v2 claimed and what v3 corrects

v2 framed `tensor_decomp_identity@v2` as a Type A `group_quotient` instance. Empirical results show the (inv1, inv2) hash collapses *the entire variety* `V_T(r)`, including elements not connected via `GL(2,ℝ)³` action. The correct v3 framing: it is a Type A instance under the equivalence "decomposes the same tensor T at the same rank r" — a *tensor-rank fingerprint*, not a `group_quotient` of the GL action.

This is a non-trivial revision. §7 details the correction.

---

## 5. Why this is a primitive, not a generator gate

(Unchanged from v2.) Same operation — *"are these the same object under declared equivalence?"* — recurs across substrate concerns: tensor decomposition (gen_12), Definition DAG node identity, MAP-Elites archive dedup, Pattern 30 REARRANGEMENT severity (a separate instance of the same primitive contract, not shared machinery), gen_11 coordinate invention (the dual problem), symbol registry promotion. Burying the canonicalizer inside any one consumer would force the others to re-implement weaker versions that diverge.

---

## 6. Open structural question: is `V_T(r)` a single connected real orbit?

The 2026-04-25 follow-up establishes:

- The connected `GL(2,ℝ)³` action does preserve `T` (verified empirically at 1e-15).
- L-BFGS-B from near-identity initialization fails to find any `(P, Q, R) ∈ GL(2,ℝ)³` mapping any of 4 ALS-converged rank-7 seeds to any other (or to Strassen). 0/6 pair-agreements at residuals 4–7.
- Differential evolution with `popsize=20–30, maxiter=300–500, bounds [-10, 10]` *also* fails. 0/5 pairs at residuals 4–5. Sanity preserved (DE recovers known nearby actions cleanly).
- Optimizer is verified working: Strassen → small-known-action recovers in 3/3 trials at residual ≤ 3e-7 with both L-BFGS-B and DE.

Three interpretations of the failure:

1. **Connecting `(P, Q, R)` exists outside DE's bounds.** Untested; DE bounds were [-10, 10] then [-50, 50] in some retries. If actions far from identity are required, broader bounds might find them. **[Q3: is testing `(P, Q, R) ∈ [-100, 100]` worth the compute cost, or is the negative result already strong enough that interpretations (2) or (3) are the live hypotheses?]**

2. **`V_T(7)` over ℝ has multiple disconnected `GL(2,ℝ)³`-orbit components.** This would be a real finding — de Groote-style single-orbit results extend over ℂ but not necessarily over ℝ; analogous to `SO(p, q)` having multiple components for `p, q ≥ 1` while `SO(n, ℂ)` is connected. The 4 ALS seeds + Strassen would inhabit 5 different real orbit components, all mapping to the same complex orbit under complexification.

3. **The connecting `(P, Q, R)` is `GL(2,ℂ)³` but not `GL(2,ℝ)³`.** Subset of (2): the complex orbit IS connected; the real components map under complexification to the same complex orbit. Distinguishing (2) from (3) at the empirical level requires running the orbit-membership test in `GL(2,ℂ)³`, which the 2026-04-23 test did but with the same near-identity init bottleneck. **[Q4: should I rerun the complex-DE test with wider bounds before declaring (2) or (3) the live hypothesis?]**

The pilot evidence strongly suggests *not* (1). Whether the right answer is (2) or (3) is unresolved. **[Q5: do you know of a citation that settles real-orbit structure for 2×2 matmul rank-7 specifically? Landsberg's *Tensors* ch. 11 was your previous pointer; I have not yet tracked down the specific result.]**

The implication for v2's instance is the same regardless: `(inv1, inv2)` is constant on `V_T(r)` for matmul-family targets, whether `V_T(r)` is one connected component or several.

---

## 7. v2 instance correction: tensor-rank fingerprint, not orbit canonicalizer

A 2026-04-25 follow-up (`harmonia/tmp/v2_invariants_diagnostic.py`) tested whether `(inv1, inv2)` discriminate beyond the same-class anchor:

| Test case | (inv1, inv2) hash | Match Strassen? |
|---|---|---|
| Strassen rank-7 | 3965f86125ddf26f | (baseline) |
| 4 ALS rank-7 seeds | 3965f86125ddf26f | YES (5/5 same as Strassen) |
| Strassen with random sign + permutation | 3965f86125ddf26f | YES (within-orbit invariance) |
| matmul rank-8 ALS | 605be9b226f7b26c | NO (rank discrimination works) |
| matmul rank-9 ALS | c86e7a3df17903f4 | NO |
| Random tensor T' rank-7 ALS | 7dc5b24a689dca00 | NO (tensor discrimination works) |

`(inv1, inv2)` correctly distinguishes:
- Different tensors (matmul T vs random T').
- Different ranks (7 vs 8 vs 9).

It does *not* distinguish within rank-7 of fixed T. All 4 ALS seeds + Strassen share the multiset `(0, 0, 0, 0, 0, 0, 1)` for `inv1` and `(1, 1, 1, 1, 1, 1, 2)` for `inv2`. This is *algebraic*: every rank-7 decomposition of 2×2 matmul has exactly one full-rank rank-1 term (`det(U_r) det(V_r) det(W_r) = 1`) and six rank-deficient terms (one factor matrix singular per term, contributing det-product zero). The multiset structure is a property of the variety `V_T(7)`, not earned by orbit-quotienting.

### 7.1 Corrected instance metadata for `tensor_decomp_identity@v2`

- **subclass:** `group_quotient` was wrong. The instance does not quotient `GL(2,ℝ)³`. The honest classification is something like `variety_fingerprint` — a fourth subclass not in the original three. **[Q6: should the contract grow a fourth subclass `variety_fingerprint`, or should this instance be retired and replaced with one that genuinely quotients a group? My read: rename and keep, with strict declared_limitations. The reviewer may take a different view.]**
- **equivalence E:** "rank-r decomposition of tensor T" — class-function on `V_T(r)`.
- **procedure C:** compute `(inv1, inv2)` per term, sort, normalize -0 to 0.
- **hash H:** SHA-256 of deterministic JSON of (sorted inv1, sorted inv2).
- **declared_limitations (revised):**
  - `not_a_group_quotient` (total) — the instance does not quotient `GL(2,ℝ)³` or any subgroup thereof. It computes a class-function on the variety `V_T(r)`. Consumers needing within-V_T(r) orbit identity must use a different instance.
  - `fixed_to_2x2_matmul_shape` (total) — factors must reshape into 2×2 matrices.
  - `requires_target_tensor_disclosure` (partial) — two rank-r decompositions of *different* tensors hash differently because the invariants encode T. Consumers looking up "have we seen this decomposition before?" must specify the target tensor.
- **calibration_anchors (re-interpreted):**
  - Same-class on `V_T(7)` for 2×2 matmul: PASS by algebraic construction, not by quotient discipline.
  - Different-class across (T, rank): PASS empirically.
  - `GL(2,ℝ)³`-invariance: PASS by polynomial-invariant theory + 10/10 random actions.
  - Within-`V_T(7)` orbit-component separation: NOT TESTED. v2 was never going to do this.

### 7.2 v1 retention with revised numerical-fragility limitations (per reviewer 2026-04-24)

v1 (scale + sign + permutation gauge, hashing raw factor entries) is retained as a registered `group_quotient` instance with these added declared_limitations specific to v1's hashing approach:

- `sign_gauge_boundary_oscillation` (partial) — the sign-gauge rule "first entry above tolerance" flips sign discontinuously when a perturbation moves the first qualifying entry across the tolerance threshold. Adjacent inputs can hash differently by a single sign flip propagated through a column.
- `pinned_decimal_dynamic_range` (partial) — fixed precision-4 rounding zeros entries below `5e-5` while leaving large entries unrounded. For factor matrices with wide dynamic range (which v1's column-norming induces, pushing magnitude into `w_i`), the rounding is effectively non-uniform. Workaround: declare per-instance `decimal_pinning` based on observed dynamic range, or migrate to log-scale / relative rounding.

These limitations apply to *v1 only*. v2 hashes invariants rather than raw factor entries and has its own (different) numerical concerns: the SVD-near-degenerate sensitivity James flagged for joint-diagonalization-based strategies, and the trace/det-product dynamic range under different per-term magnitudes. Per his discipline, v2 declares its own limitations rather than inheriting v1's.

---

## 8. Second shipped instance: `poly_monomial_form@v1`

(Subclass: `group_quotient`. Unchanged from v2 except the subclass tag.)

Type A under `permutation(S_n) × sign_gauge`. 6/6 calibration anchors pass. Validates the cross-domain claim of the primitive: the same contract serves both tensor and polynomial domains. **[Q7: with v2-the-tensor-instance now classified as `variety_fingerprint` and `poly_monomial_form` as `group_quotient`, the cross-subclass evidence for the primitive's reach is weaker than v2 implied. Is two `group_quotient` instances + zero `partition_refinement` + zero `ideal_reduction` strong enough to claim the stratification works, or does v3 need at least one instance per subclass to make the case?]**

---

## 9. Type B work-in-progress: `tensor_decomp_integer_rep@v1`

(Unchanged from v2.) PARTIAL status: GL(2,ℝ)³ local search improves integer-fraction from 0.000–0.131 to 0.190–0.286; does not reach Strassen's 1.0. Continuous search does not hit the measure-zero integer basin. Stronger primitives identified, not attempted (simulated annealing with integer-snap; L-BFGS with integer-distance penalty; `GL(2, ℤ)` enumeration). Per James 2026-04-24 reframe: Strategy 3 is Type A on targets whose orbits contain integer points, Type B otherwise; matmul satisfies the precondition; this should be re-classified as Type A `variety_selection` once the search primitive lands.

---

## 10. Adjacent instances (identified, not scoped)

`graph_iso@v1` (`partition_refinement`); `pattern_30_rearrangement@v1` (`ideal_reduction`); `dag_node_identity@v1` (`group_quotient`).

---

## 11. Orbit discipline — Pattern 31 (DRAFT, 2 anchors)

(Unchanged from v2.) Substrate-level generalization of Pattern 30 REARRANGEMENT severity. Anchor cases: F043 retraction; 2×2 matmul pilot. Promotes to FULL when a third independent anchor accumulates.

---

## 12. Integration surfaces

(Mostly unchanged.) Definition DAG nodes via `dag_node_identity@v1`; symbol registry promotion checks; MAP-Elites archive dedup; Pattern 30 via `pattern_30_rearrangement@v1` (separate instance, same contract); gen_11 inverse problem; gen_12 first explicit consumer.

**Changed re: gen_12.** With v2-the-instance reclassified as a tensor-rank fingerprint rather than an orbit canonicalizer, gen_12's Gate 2 (orbit-equivalence dedup) cannot be implemented by `tensor_decomp_identity@v2` alone. gen_12 needs either (a) a true `group_quotient` Type A tensor instance, or (b) an explicit acknowledgment that catalog dedup is at the V_T(r) granularity, not at the orbit granularity. Both are acceptable; (b) means gen_12's catalog stores one entry per (T, rank) pair regardless of how many distinct orbit components exist, which may be the right product decision but is *different* from what v2 implied. **[Q8: is (a) or (b) the right product decision for gen_12? (a) requires shipping a true orbit canonicalizer, which is open; (b) is shippable now but means gen_12 measures something simpler than "is this a new orbit" — it measures "is this a new (T, rank)".]**

---

## 13. Relationship to prior work

(Mostly unchanged from v2.) Strassen 1969, Winograd 1971, Laderman 1976, Bini et al. 1979, Kolda & Bader 2009.

**AlphaTensor 2022 framing tightened** per reviewer (v2 was over-broad). Certain AlphaTensor characteristic-zero / standard-arithmetic results were identified as orbit-variants of known decompositions; the F_2/F_4 finite-field results are a separate and largely uncontested case. The architectural lesson — orbit discipline is the missing infrastructure piece — survives the qualification. The Prometheus contribution is the architectural move (canonicalizer as substrate primitive with mandatory declared-limitations and stratified verification stories), not "the thing that would have prevented all of AlphaTensor's claims." **[Q9: how strong should the AlphaTensor framing be in §13? The risk of over-claiming this primitive's reach against a contested literature is real. v3 softens; reviewer can advise further softening if needed.]**

---

## 14. Limitations and open questions

**Open: real orbit structure of `V_T(r)` for 2×2 matmul rank 7.** Pilot evidence suggests multiple disconnected `GL(2,ℝ)³`-orbits; literature confirmation pending. (§6.)

**Open: a true `group_quotient` Type A tensor instance.** v2-the-instance is a `variety_fingerprint`, not a group quotient. Strategy 4 (explicit-stabilizer parameterization per James 2026-04-24) is the next candidate; not yet implemented. **[Q10: prioritize Strategy 4 implementation in next session, or accept that `tensor_decomp_identity` may be permanently a `variety_fingerprint` and move on?]**

**Open: stratification's third subclass empty.** No `ideal_reduction` instance is shipped; only conceptual mapping to Pattern 30 REARRANGEMENT. The cross-subclass primitive claim rests on two `group_quotient` instances (one of which I'm reclassifying as `variety_fingerprint`) and conceptual sketches.

**Open: hash-collision economics.** Renamed per reviewer to "declared-limitation false-dedup rate" — the metric that matters is not cryptographic collision but C-collision (two non-equivalent inputs landing on the same canonical form because C is incomplete). Should be formalized at v0.4. **[Q11: is the renamed metric the right framing, or is there a still-better one?]**

**Open: cross-version migration.** Per reviewer, the contract should require storing the *pre-canonical representation* alongside the hash so re-canonicalization on version bump is `O(N)` rather than `O(N × recompute-from-source)`. Not yet in the contract. **[Q12: confirm this is a contract addition for v0.3 or v0.4?]**

**Partial: MNAR at the orbit level** (unchanged from v2).

---

## 15. Aggregated questions for reviewer

Q1 — Z₂ × Z₃ as decomposition-factor symmetry was wrong; v3 corrects. Confirm.

Q2 — Three-subclass shape stable, or are there equivalence-types not fitting `group_quotient` / `partition_refinement` / `ideal_reduction`?

Q3 — Worth running DE with bounds [-100, 100] before declaring interpretation (1) ruled out?

Q4 — Rerun complex-DE with wider bounds before settling on (2) vs (3)?

Q5 — Citation for real-orbit structure of 2×2 matmul rank 7?

Q6 — Add `variety_fingerprint` as a fourth subclass, or rename and keep within an extended `group_quotient` (with the group being trivial-acting-on-V_T)?

Q7 — Two `group_quotient` instances + zero of others = strong enough cross-subclass evidence?

Q8 — gen_12's catalog: orbit-dedup (requires true Type A orbit canonicalizer) or `(T, rank)`-dedup (shippable now)?

Q9 — AlphaTensor framing strength in §13: appropriate as written, or further soften?

Q10 — Prioritize Strategy 4 implementation, or accept fingerprint status and move on?

Q11 — "Declared-limitation false-dedup rate" the right framing for hash-collision economics?

Q12 — Pre-canonical representation storage: contract addition for v0.3 or v0.4?

---

## 16. Conclusion

Phase 1 established the canonicalizer as a substrate primitive. v1 whitepaper compiled the argument. v2 whitepaper made specific instance-level claims that 2026-04-25 follow-up did not support: `tensor_decomp_identity@v2` is a tensor-rank fingerprint, not an orbit canonicalizer.

The architectural claim survives intact. The substrate-primitive promotion is the right move; the Type A / Type B split is load-bearing; the mandatory declared-limitations field is the guardrail; the three-subclass stratification (group_quotient / partition_refinement / ideal_reduction) is a clean contract shape. What changes in v3 is the specific instance's classification and the open-question list.

The thesis from v1 — *search is easy; representation is the problem* — survives a third revision and gains nuance: representation is not just *quotienting under symmetry* but also *deciding what equivalence is worth quotienting*. v2-the-instance turned out to canonicalize at the variety level rather than the orbit level. Whether that's acceptable depends on the consumer's needs, which is exactly the kind of decision the declared-limitations field forces into the open.

---

## 17. Artifact inventory

(Updated for v3 cycle.)

**Substrate artifacts:**
- `harmonia/memory/architecture/canonicalizer.md` — primitive spec (will bump to v0.3 with subclass stratification + v3 instance corrections after this whitepaper lands).
- `harmonia/memory/architecture/orbit_vs_representative.md` — tensor instance detail.
- `harmonia/memory/architecture/phase_2_plan.md` — workstream plan + status log.
- `agora/canonicalizer/poly_monomial_form_v1.py` — `group_quotient` Type A instance.
- `agora/canonicalizer/tensor_decomp_identity_v2.py` — `variety_fingerprint` Type A instance (re-classification pending).
- `harmonia/memory/pattern_library.md` — Pattern 31 Orbit Discipline (DRAFT).
- `docs/prompts/gen_12_tensor_identity_search.md` — first consumer.
- `stoa/ideas/2026-04-23-sessionA-tensor-identity-search.md` — discussion.

**Pilot + diagnostic artifacts (`harmonia/tmp/`, committed):**
- 2026-04-23: `tensor_pilot_2x2_matmul.py`, `canonicalize_test.py`, `tensor_decomp_identity_v2.py`, `tensor_decomp_integer_rep_v1.py`, `tensor_gl2_action.py`, `tensor_gl2_invariants*.py`.
- 2026-04-24: `orbit_membership_test.py`, `orbit_membership_sanity.py`, `orbit_membership_with_cosets.py`.
- 2026-04-25: `orbit_membership_de.py`, `v2_invariants_diagnostic.py`.

**Reference documents:**
- `docs/landscape_charter.md`, `docs/long_term_architecture.md` v2.1.
- `docs/whitepaper_orbit_canonicalization.md` (v1, retained).
- `docs/whitepaper_orbit_canonicalization_v2.md` (v2, retained).

**Commits landing this work** (latest first):
- `7bc4db52` — v2 invariants diagnosed as (T, rank) class-functions, not orbit canonicalizer.
- `68355c71` — orbit-membership experiments.
- `b5023814` — Phase 2 W2 passes (later qualified by 7bc4db52).
- `0d461b4c` — Phase 2 MVP.
- `85461d40` — v1 whitepaper.
- `276fddad` — canonicalizer v0.1.1 crispness pass.
- `5d455da2` — canonicalizer promoted to substrate primitive.

---

*Whitepaper v3 prepared by Harmonia_M2_sessionA, 2026-04-25. Supersedes v1 (2026-04-23) and v2 (2026-04-23). Compiled from canonicalizer.md v0.2.1, orbit_vs_representative.md v0.2, phase_2_plan.md, the 2026-04-23 / 24 / 25 implementation and diagnostic artifacts, and James's 2026-04-24 reviewer pass on v2. Intended for reviewer feedback via inline `[Q: ...]` markers and §15 aggregated question list.*
