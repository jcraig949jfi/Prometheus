# Orbit Canonicalization as a Substrate Primitive (v4)
## A whitepaper on tensor identity search in Prometheus
### 2026-04-25 — Harmonia_M2_sessionA

*v4 supersedes v3 (`whitepaper_orbit_canonicalization_v3.md`). v1, v2, v3 retained for audit. v4 integrates the reviewer's answers to v3's twelve embedded questions and removes the questions section accordingly.*

> **v2 tried to prove we had a canonicalizer. v3 proves we have a taxonomy of identity. That's the bigger win.** — paraphrased from reviewer feedback on v3.

---

## Abstract

Many Prometheus substrate operations — catalog dedup, DAG node identity, MAP-Elites archive diversity, algebraic-rearrangement detection — require answering *"are these two representations the same object under a declared equivalence?"* Without a principled primitive for that question, every consumer re-implements a weaker version and they silently disagree.

A 2026-04-23 pilot on 2×2 matrix-multiplication tensor decompositions made the gap concrete. A minimal search stack rediscovered Strassen's rank-7 orbit at machine precision in 6 of 20 random seeds. Four naïve canonical hashes on machine-precision seeds produced four distinct values; Strassen's added a fifth. After three falsified strategies, a two-scalar `(inv1, inv2)` invariant fingerprint collapsed all five to one hash. v2 of this whitepaper called that ship a Type A `group_quotient` canonicalizer.

Two follow-up experiments at 2026-04-25 reframed the v2 claim. (a) Differential-evolution global search over `GL(2,ℝ)³` failed to connect any pair of converged seeds at residuals approaching zero — sanity-checked by recovering small known actions cleanly. (b) The `(inv1, inv2)` multiset structure is *algebraic*: every rank-7 decomposition of the 2×2 matmul tensor has exactly one full-rank rank-1 term and six rank-deficient terms, so the invariants are constant on the variety `V_T(7)` by construction.

The corrected claim: **the v2 instance is a class-function of `(T, rank)`, not a quotient under a group action**. It identifies "this is a rank-r decomposition of T" — a useful tensor-rank fingerprint, but not a true orbit canonicalizer. The architectural primitive claim survives intact; the instance's classification changes.

This whitepaper formalizes orbit canonicalization as a substrate primitive in **four subclasses** (group-quotient, partition-refinement, ideal-reduction, and the new variety-fingerprint surfaced by the v2 correction); registers `tensor_decomp_identity@v2` honestly under variety-fingerprint; documents `poly_monomial_form@v1` as the cross-domain Type A group-quotient instance; pins gen_12's catalog semantics at variety-level dedup with orbit-level dedup as a labeled future upgrade; and sets up Strategy 4 (explicit-stabilizer parameterization) as the next high-leverage experiment that, if it succeeds, would yield the missing true Type A group-quotient instance for tensors.

---

## 1. The representation problem

When a substrate stores structured mathematical objects, two representations may denote the same object under some equivalence. If the substrate cannot compute a canonical representative for each class, every downstream operation that depends on identity — deduplication, diversity measurement, archive keys, DAG nodes, novelty detection — silently mis-counts.

A recurring failure mode in recent automated-discovery work (AlphaTensor being the prominent anchor) is reporting "new discoveries" that on examination are orbit-variants of existing solutions under the natural symmetry group. This is the decomposition-level instance of Pattern 1 (Distribution/Identity Trap) in the Prometheus pattern library.

Prometheus's existing discipline — Pattern 30 graded severity for algebraic-identity coupling, versioned symbols with composition hashes, retraction-as-first-class-event — was built for a narrower concern: correlational claims on algebraically-coupled variables (F043 retraction, 2026-04-19). The present work extends that discipline to identity of structured objects themselves under declared equivalence, formalized as a substrate primitive with four subclasses.

---

## 2. The empirical pivot: 2×2 matrix multiplication

The pilot targets a well-understood anchor. Matrix multiplication of 2×2 matrices is encoded as `T ∈ ℝ^{4×4×4}` with `T[ij, jk, ik] = 1` for matching middle index, zero otherwise. Strassen (1969) exhibited a rank-7 decomposition with integer factors. Winograd (1971) proved rank ≥ 7. Whether all rank-7 real decompositions of `T` lie in a single `GL(2,ℝ)³` orbit is, to our knowledge, not explicitly classified in the literature — existing results (de Groote 1978; Landsberg, *Tensors: Geometry and Applications*, ch. 11) are primarily over ℂ. Real-orbit splitting analogous to `SO(p, q)` having multiple components while `SO(n, ℂ)` is connected is the relevant phenomenon to look for. The present empirics suggest splitting; §6 documents the evidence.

Pilot setup: twenty random ALS seeds at target rank `r ∈ {6, 7, 8}`; 500 iterations; total runtime 1.4 seconds.

### 2.1 Results (ranks 6, 7, 8 over ℝ)

| Rank | Seeds reaching residual < 1e-8 | Best residual | Interpretation |
|---|---|---|---|
| 8 | 0/20 (near-misses at 2e-8) | 2.24e-08 | Over-parameterized; known ALS swamp |
| 7 | 6/20 (30%) | 9.4e-13 | Strassen orbit reached at machine precision |
| 6 | 0/20 | 1.000 (sharp clustering) | Matches Winograd lower bound |

Rank-6 residual concentration at 1.000 depends on tensor normalization (`‖T‖_F = 2√2 ≈ 2.83`); the value 1.000 is the squared-Frobenius deficit floor under this measurement, not a universal constant. Frozen as a regression test.

### 2.2 Orbit, not representative

Six rank-7 ALS-converged decompositions have integer-fractions in 0.02–0.16; Strassen's has 1.00. ALS from Gaussian initialization has Lebesgue-measure-zero chance of landing on an integer-valued representative within a continuous orbit, so the absence of integer structure is tautological, not surprising.

The substantive claim: reaching the orbit is not the same as reaching a representative. A generator that claims "novelty" from the first without fixing the second is measuring coordinate artifacts. This is the architectural thesis the canonicalizer primitive enforces.

### 2.3 v1 canonical-hash collision test (2026-04-23)

v1 canonicalizer (scale + sign + permutation gauge) applied to four machine-precision seeds + Strassen produced **five distinct hashes**. v1 is strictly insufficient as a Type A canonicalizer for the 2×2 matmul rank-7 case under the GL action. The cause was investigated in §6.

---

## 3. Orbit vs representative

For a target tensor `T` and rank `r`, the exact rank-`r` CP decompositions form a real algebraic variety `V_T(r)`. Several groups act on this variety and preserve `T`:

- **Scale gauge** — per term: `(u_i, v_i, w_i) → (α u_i, β v_i, (αβ)^{-1} w_i)` for `(α, β) ∈ ℝ*²`.
- **Sign gauge** — degenerate scale; called out separately because integer bases prefer it.
- **Permutation** — `S_r` on the rank-1 term index.
- **Connected `GL(n,ℝ)³` matmul-covariant action** — `A → PAQ⁻¹, B → QBR⁻¹, C → P⁻ᵀCRᵀ`. The `P⁻ᵀCRᵀ` form on the third factor (not `PCR⁻¹`) preserves the Frobenius pairing `⟨AB, C⟩` that defines matmul. Empirically verified to preserve T at residual ~1e-15 for random `(P, Q, R) ∈ GL(2,ℝ)³`.

v2 additionally invoked a `Z₂ × Z₃` discrete component (transpose, factor-role cyclic permutation). 2026-04-25 follow-up empirics showed this is incorrect at the decomposition-factor level: cyclic rotation of `(A, B, C)` factors does not preserve T (residual 3.46 against original T); transpose likewise. These discrete operations act on the *tensor space* (relabeling modes gives a different labeled tensor), not on decompositions of fixed-labeled `T`. v3 corrected the framing; v4 retains.

So under fixed-label T, the relevant group is `(GL(n,ℝ)³ × scale_gauge × S_r)`. Whether `V_T(r)` is a single orbit under this group is the empirical question §6 returns to. The literature does not, to our knowledge, settle it for the matmul rank-7 case over ℝ specifically.

---

## 4. The contract (v0.3 stratified, four subclasses)

A canonicalizer instance is a tuple

```
(name, type, subclass, equivalence E, procedure C, hash H (Type A only),
 secondary_objective (Type B only),
 declared_limitations, calibration_anchors, canonicalizer_version,
 pre_canonical_storage)
```

### 4.1 Two types (Type A / Type B)

- **Type A — canonical identity.** Deterministic quotient producing a hashable canonical representative for each equivalence class. Hash equality iff equivalence class equality (modulo separation bound on H).
- **Type B — preferred representative.** Optimization inside an already-identified class against a declared secondary objective. Output for display, not identity. Composition rule: Type B always consumes Type A output.

### 4.2 Four subclasses (v0.3, with `variety_fingerprint` added in v4 cycle)

The contract is shaped by what kind of structure the equivalence has. Each subclass carries its own verification story.

- **`group_quotient`** — equivalence `E = G·x` for an executable group `G` with named generators. Verification: per-generator invariance check on `C`. Examples: `tensor_decomp_identity@v1` (declared `G` = scale × sign × permutation; declared limitation: T-stabilizer not quotiented), `poly_monomial_form@v1` (declared `G` = variable-permutation × sign), `dag_node_identity@v1` (basis change on input atoms).

- **`partition_refinement`** — equivalence by an algorithm that terminates at a unique-by-construction representative, not necessarily expressible as a group quotient. Verification: algorithm-correctness proof or appeal to a published canonical-form algorithm. Examples: `graph_iso@v1` (nauty/Bliss partition refinement + lex labeling).

- **`ideal_reduction`** — equivalence by ideal membership in a declared ring. Verification: reduction-to-normal-form correctness against a Gröbner basis (or equivalent). Examples: `pattern_30_rearrangement@v1` (algebraic expressions over a declared ring).

- **`variety_fingerprint`** — equivalence induced by **algebraic constraints defining a variety**, not by an explicit group action. The instance computes class-functions of the variety: scalars constant across the variety by algebraic construction. Verification: invariance under the variety's defining equations + empirical separation across distinct varieties (different `(T, rank)`, different parent objects). Output is a fingerprint of *which variety the input lies on*, not which orbit-component within the variety. Examples: `tensor_decomp_identity@v2` (every rank-r decomp of T has algebraically-determined `(inv1, inv2)` multiset structure; the hash identifies `(T, rank)`, not orbit-component).

The fourth subclass is the architectural lesson the v2 → v3 → v4 cycle taught. v2 attempted to ship a `group_quotient` instance and instead shipped what we now formalize as a `variety_fingerprint`. Recognizing this without forcing the instance into a wrong subclass is the contract's value: it admits an instance is *weaker* than originally intended without collapsing the architecture.

Each subclass instance carries verification semantics. The base contract requires every instance to declare which subclass applies. Cross-subclass instance comparisons are forbidden; namespacing by `(subclass, name, version)` enforces this.

### 4.3 On the equivalence E — declared, possibly non-group

For `group_quotient`: `E = G·x` where `G` has executable semantics. Generator types in `G` must have executable semantics within the instance; subgroups not computationally realized appear in `declared_limitations`, not `G`.

For `partition_refinement`: `E` is the equivalence relation defined by the refinement algorithm's terminal labeling.

For `ideal_reduction`: `E` is membership-in-the-same-coset of the declared ideal.

For `variety_fingerprint`: `E` is the equivalence "lies on the same algebraic variety" — coarser than orbit equivalence in general. Declared by specifying the parent object (e.g., the target tensor) and any rank/structural constraints.

### 4.4 On C, H — invariance, separation, asymmetry, tolerance, failure, failure stability, hash contract

(Unchanged from v2/v3.) Invariance, probabilistic separation, asymmetry warning (canonical inequality does not imply non-equivalence), tolerance, complexity, failure behavior with `(failure, reason)` return, and failure-stability under tolerance. Hash deterministic, namespaced by `(subclass, name, canonicalizer_version)`, tolerance pinning. Specific cryptographic primitive is implementation detail.

### 4.5 On declared_limitations

Mandatory. Every instance declares what equivalences it does *not* remove, severity (partial vs total), workaround. Absence rejects the instance. The renamed metric for hash-collision economics — *declared-limitation false-dedup rate* — replaces the earlier "collision budget" framing. The relevant failure is C-collision (two non-equivalent inputs mapping to the same canonical form because C is incomplete), not cryptographic hash collision. Per-instance false-dedup rate target is added at v0.4 once the metric is operationalized.

### 4.6 On pre_canonical_storage (added v0.3)

Per reviewer 2026-04-24: contract requires storing the *pre-canonical representation* alongside the canonical hash, so re-canonicalization on version bump is `O(N)` rather than `O(N × recompute-from-source)`. Implemented as a required field in each registered instance.

---

## 5. Why this is a primitive, not a generator gate

(Unchanged from v2/v3.) Same operation — *"are these the same object under declared equivalence?"* — recurs across substrate concerns: tensor decomposition (gen_12), Definition DAG node identity, MAP-Elites archive dedup, Pattern 30 REARRANGEMENT severity (separate instance of same primitive contract, not shared machinery), gen_11 coordinate invention (the dual problem), symbol registry promotion. Burying the canonicalizer inside any one consumer would force the others to re-implement weaker versions that diverge.

---

## 6. Empirical evidence: real orbit components vs variety fingerprint

The 2026-04-25 follow-up established:

- The connected `GL(2,ℝ)³` action does preserve `T` (verified empirically at 1e-15).
- L-BFGS-B from near-identity initialization fails to find any `(P, Q, R) ∈ GL(2,ℝ)³` mapping any of 4 ALS-converged rank-7 seeds to any other (or to Strassen). 0/6 pair-agreements at residuals 4–7.
- Differential evolution with `popsize=20–30, maxiter=300–500, bounds [-10, 10]` *also* fails. 0/5 pairs at residuals 4–5. Sanity preserved (DE recovers known nearby actions cleanly).
- Optimizer is verified working: Strassen → small-known-action recovers in 3/3 trials at residual ≤ 3e-7 with both L-BFGS-B and DE.

Per reviewer 2026-04-25: residuals 4–7 are not "close misses"; they are *orders of magnitude off*. That pattern is structural, not numerical. Expanding DE bounds to e.g. [-100, 100] would multiply the search volume enormously without increasing the probability of finding a connected solution if components are disconnected. **Interpretation (1) — connecting `(P, Q, R)` exists outside DE bounds — is treated as ruled out.**

The remaining live hypothesis: rank-7 decompositions of `T` over ℝ form multiple disconnected `GL(2,ℝ)³`-orbit components. The 4 ALS seeds + Strassen inhabit different real components, all mapping to the same complex orbit under complexification (analogous to the quadratic-form signature splitting under reality). To our knowledge this is not classified in the literature; the observation is plausible and consistent with known phenomena.

The implication for the v2 instance: regardless of whether `V_T(r)` is one or many components under `GL(2,ℝ)³`, `(inv1, inv2)` is constant on `V_T(r)` — because the multiset structure is determined algebraically by the variety's defining equations, not by the group action. This makes the v2 instance a `variety_fingerprint`.

---

## 7. v2 instance correction: tensor-rank fingerprint, not orbit canonicalizer

A 2026-04-25 follow-up tested whether `(inv1, inv2)` discriminate beyond the same-class anchor:

| Test case | Hash | Match Strassen? |
|---|---|---|
| Strassen rank-7 | 3965f86125ddf26f | (baseline) |
| 4 ALS rank-7 seeds | 3965f86125ddf26f | YES (5/5) |
| Strassen with random sign + permutation | 3965f86125ddf26f | YES (within-orbit invariance) |
| matmul rank-8 ALS | 605be9b226f7b26c | NO (rank discrimination works) |
| matmul rank-9 ALS | c86e7a3df17903f4 | NO |
| Random tensor T' rank-7 ALS | 7dc5b24a689dca00 | NO (tensor discrimination works) |

`(inv1, inv2)` correctly distinguishes:
- Different tensors (matmul T vs random T').
- Different ranks (7 vs 8 vs 9).

It does *not* distinguish within rank-7 of fixed T. All rank-7 inputs share the multiset `(0, 0, 0, 0, 0, 0, 1)` for `inv1` and `(1, 1, 1, 1, 1, 1, 2)` for `inv2`. This is *algebraic*: every rank-7 decomposition of 2×2 matmul has exactly one full-rank rank-1 term (`det(U_r) det(V_r) det(W_r) = 1`) and six rank-deficient terms (one factor matrix singular, contributing det-product zero). The multiset structure is a property of the variety `V_T(7)`, not earned by orbit-quotienting.

### 7.1 Instance metadata (v0.3)

- **subclass:** `variety_fingerprint`.
- **type:** A.
- **equivalence E:** "rank-r decomposition of tensor T" — class-function on `V_T(r)`.
- **procedure C:** compute `(inv1, inv2)` per term, sort, normalize -0 to 0.
- **hash H:** SHA-256 of deterministic JSON of (sorted inv1, sorted inv2).
- **declared_limitations:**
  - `not_a_group_quotient` (total) — does not quotient `GL(2,ℝ)³` or any subgroup. Computes class-functions on the variety. Consumers needing within-V_T(r) orbit identity must use a different instance (none yet shipped; see §10).
  - `fixed_to_2x2_matmul_shape` (total) — factors must reshape into 2×2 matrices.
  - `requires_target_tensor_disclosure` (partial) — two rank-r decompositions of *different* tensors hash differently because the invariants encode T. Consumers looking up "have we seen this decomposition before?" must specify the target tensor.
- **calibration_anchors:**
  - Same-variety on `V_T(7)`: PASS by algebraic construction.
  - Different-variety across `(T, rank)`: PASS empirically.
  - `GL(2,ℝ)³`-invariance: PASS by polynomial-invariant theory + 10/10 random actions.
  - Within-`V_T(7)` orbit-component separation: NOT TESTED; the instance is not designed to provide this.

### 7.2 v1 retention with revised numerical-fragility limitations

v1 is retained as a registered `group_quotient` instance with these added declared_limitations specific to v1's hashing approach:

- `sign_gauge_boundary_oscillation` (partial) — sign-gauge "first entry above tolerance" rule flips sign discontinuously when a perturbation moves the first qualifying entry across tolerance. Adjacent inputs can hash differently by a single sign flip propagated through a column.
- `pinned_decimal_dynamic_range` (partial) — fixed precision-4 rounding zeros entries below 5e-5 while leaving large entries unrounded. For factor matrices with wide dynamic range (induced by v1's column-norming pushing magnitude into `w_i`), the rounding is effectively non-uniform. Workaround: declare per-instance `decimal_pinning` based on observed dynamic range, or migrate to log-scale / relative rounding.

These limitations apply to *v1 only*. The v2 instance hashes invariants rather than raw factor entries; its numerical concerns differ (trace/det-product dynamic range under per-term magnitudes; near-degenerate-singular-value sensitivity if SVD-based strategies are added later). Per reviewer discipline, each version declares its own numerical story rather than inheriting the previous one's.

---

## 8. Second shipped instance: `poly_monomial_form@v1`

Subclass: `group_quotient`. Type A under `permutation(S_n) × sign_gauge`. 6/6 calibration anchors pass. Validates the cross-domain claim of the primitive: the same contract serves both tensor (variety_fingerprint) and polynomial (group_quotient) domains. The cross-subclass evidence is two `group_quotient` (`tensor_decomp_identity@v1` and `poly_monomial_form@v1`) plus one `variety_fingerprint` (`tensor_decomp_identity@v2`); `partition_refinement` and `ideal_reduction` slots remain to be filled.

---

## 9. Type B work-in-progress: `tensor_decomp_integer_rep@v1`

(Unchanged structure.) PARTIAL. GL(2,ℝ)³ local search improves integer-fraction from 0.000–0.131 to 0.190–0.286; does not reach Strassen's 1.0. Per reviewer 2026-04-24 reframe: Strategy 3 (orbit-internal integer search) is Type A on targets whose orbits contain integer points — `variety_selection` is the closest fit for that case — Type B otherwise. Matmul satisfies the precondition; the eventual reclassification will land alongside Strategy 4's outcome.

---

## 10. Adjacent instances (identified, not scoped)

`graph_iso@v1` (`partition_refinement`, classical canonical form via nauty/Bliss); `pattern_30_rearrangement@v1` (`ideal_reduction`, algebraic rearrangement via Gröbner-basis normal form); `dag_node_identity@v1` (`group_quotient`, basis change on input atoms).

---

## 11. Orbit discipline — Pattern 31 (DRAFT, 2 anchors)

(Unchanged from v2/v3.) Substrate-level generalization of Pattern 30 REARRANGEMENT severity. Anchor cases: F043 retraction; 2×2 matmul pilot. Promotes to FULL when a third independent anchor accumulates.

---

## 12. Integration surfaces

### 12.1 gen_12 catalog semantics — **variety-level dedup, labeled** (resolves v3 Q8)

Per reviewer 2026-04-25: gen_12 ships with `(T, rank)`-dedup explicitly labeled as **variety-level dedup**, with **orbit-level dedup** declared as a future upgrade gated on a true Type A `group_quotient` tensor instance landing.

Variety-level dedup matches what `tensor_decomp_identity@v2` actually computes. It is shippable now, stable, and well-defined. Coarser notion of novelty than orbit-level; honest about what is and isn't being measured. The substrate is mapping a landscape; coarse partitions at this stage are a phase, not a bug. Architecturally clean upgrade path: when Strategy 4 (or a successor) lands an orbit-level instance, gen_12's catalog adds a second column for orbit-hashes alongside the variety-hashes. Existing entries remain valid; new entries can be deduplicated at the finer granularity.

### 12.2 Other consumers

(Unchanged from v2/v3.) Definition DAG nodes via `dag_node_identity@v1`; symbol registry promotion checks; MAP-Elites archive dedup at variety-level until orbit-level lands; Pattern 30 via `pattern_30_rearrangement@v1` (separate instance, same contract); gen_11 inverse problem.

---

## 13. Relationship to prior work

(Mostly unchanged from v2/v3.) Strassen 1969, Winograd 1971, Laderman 1976, Bini et al. 1979, Kolda & Bader 2009. AlphaTensor 2022 framing softened per reviewer: certain characteristic-zero / standard-arithmetic results were identified as orbit-variants of known decompositions; the F_2/F_4 finite-field results are a separate and largely uncontested case. The architectural lesson — orbit discipline is the missing infrastructure piece — survives the qualification. The Prometheus contribution is the architectural move (canonicalizer as substrate primitive with mandatory declared-limitations and stratified verification stories), not "the thing that would have prevented all of AlphaTensor's claims."

---

## 14. Limitations and forward thread

**Open: real orbit structure of `V_T(r)` for 2×2 matmul rank 7.** Pilot evidence suggests multiple disconnected `GL(2,ℝ)³`-orbits over ℝ. Literature does not, to our knowledge, classify this case explicitly. Existing results (de Groote 1978; Landsberg) live in adjacent territory but don't settle the real-orbit question for this specific tensor + rank. The phenomenon is plausible and analogous to known real-vs-complex orbit splittings.

**Open: a true `group_quotient` Type A tensor instance.** The v2 instance is a `variety_fingerprint`. Strategy 4 (explicit-stabilizer parameterization per reviewer 2026-04-24) is the next experiment: parameterize the matmul stabilizer's known low-dimensional structure (coupled action `(P, P^{-T}, I)` for `P ∈ GL(2)` plus discrete factors) and use it to canonicalize via QR-reduction on a reference rank-1 term. If it succeeds, gen_12 upgrades immediately to orbit-level dedup. If it fails, the failure is a direct learning about stabilizer structure that feeds back into theory. The information value is high either way; the cost is bounded (~60 minutes implementation + test).

**Open: `partition_refinement` and `ideal_reduction` subclass instances.** Both are conceptually mapped (graph_iso, Pattern 30 rearrangement) but neither is shipped. Cross-subclass evidence currently rests on two `group_quotient` + one `variety_fingerprint`. Filling at least one of the empty slots is a Phase 3 priority.

**Open: declared-limitation false-dedup rate operationalization.** The renamed metric (was "collision budget") needs a concrete per-instance target and an automated check that runs as a calibration anchor. v0.4 contract addition.

**Partial: MNAR at the orbit level.** Even with a perfect canonicalizer, the set of decompositions a search explores is a non-random sample of the variety. Search biases (ALS, GA, RL) carry through. Variety-level identity does not absolve MNAR discipline at the measurement level.

---

## 15. Conclusion

Phase 1 established the canonicalizer as a substrate primitive. v1 whitepaper compiled the argument. v2 made specific instance-level claims that 2026-04-25 follow-up did not support: `tensor_decomp_identity@v2` is a tensor-rank fingerprint, not an orbit canonicalizer. v3 surfaced the correction and asked twelve questions of the reviewer. v4 integrates the answers and ships the v0.3 contract with four subclasses.

The architectural claim survives intact. The substrate-primitive promotion is the right move; the Type A / Type B split is load-bearing; the mandatory declared-limitations field is the guardrail; the four-subclass stratification (`group_quotient` / `partition_refinement` / `ideal_reduction` / `variety_fingerprint`) is a clean contract shape that the v2 → v3 cycle stress-tested into existence.

The bigger insight, in the reviewer's framing: v2 tried to prove we had a canonicalizer; v3 proved we have a *taxonomy of identity*. The taxonomy admits when an instance is weaker than originally intended without collapsing the architecture. That ability — to honestly downgrade rather than rescue — is what distinguishes infrastructure from a research artifact.

The thesis from v1 — *search is easy; representation is the problem* — survives a fourth revision and gains nuance: representation is not just *quotienting under symmetry* but also *deciding what equivalence is worth quotienting*. Sometimes the right answer is variety-level, not orbit-level. Sometimes it's orbit-level. The contract is there to make the choice explicit.

Strategy 4 is the next experiment. If it lands, the tensor side gets both a `variety_fingerprint` (the v2 instance, now correctly classified) and a `group_quotient` (Strategy 4's output). Together, they would represent the most architecturally complete corner of the canonicalizer registry to date — a subclass-stratified pair on the same domain, each registered at its own granularity, composed via the catalog upgrade path described in §12.1.

---

## 16. Artifact inventory

(Updated for v4 cycle.)

**Substrate artifacts:**
- `harmonia/memory/architecture/canonicalizer.md` — primitive spec (v0.3 with four-subclass stratification; v2-instance reclassified to variety_fingerprint; pre_canonical_storage and false-dedup-rate added).
- `harmonia/memory/architecture/orbit_vs_representative.md` — tensor instance detail.
- `harmonia/memory/architecture/phase_2_plan.md` — workstream plan + status log.
- `agora/canonicalizer/poly_monomial_form_v1.py` — `group_quotient` Type A instance.
- `agora/canonicalizer/tensor_decomp_identity_v2.py` — `variety_fingerprint` Type A instance (instance metadata updated).
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
- `docs/whitepaper_orbit_canonicalization_v3.md` (v3, retained).

**Commits landing this work** (latest first):
- `7bc4db52` — v2 invariants diagnosed as (T, rank) class-functions, not orbit canonicalizer.
- `68355c71` — orbit-membership experiments.
- `b5023814` — Phase 2 W2 passes (later qualified by 7bc4db52).
- `0d461b4c` — Phase 2 MVP.
- `85461d40` — v1 whitepaper.
- `276fddad` — canonicalizer v0.1.1 crispness pass.
- `5d455da2` — canonicalizer promoted to substrate primitive.

---

*Whitepaper v4 prepared by Harmonia_M2_sessionA, 2026-04-25. Supersedes v1 (2026-04-23), v2 (2026-04-23), v3 (2026-04-25). Compiled from canonicalizer.md v0.3, orbit_vs_representative.md, phase_2_plan.md, the 2026-04-23/24/25 implementation and diagnostic artifacts, and reviewer feedback on v1, v2, and v3. v4 integrates the reviewer's five direct answers (Q3, Q5, Q6, Q8, Q10) plus the seven question-resolutions implicit in the whitepaper review (subclass naming, contract additions, instance reclassification, AlphaTensor framing, etc.) into the body of the document. Strategy 4 is the next-experiment forward thread.*
