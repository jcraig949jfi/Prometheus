# Session Summary for External Review — 2026-04-25
## Canonicalizer substrate primitive, Phase 2 second pass

**Author:** Harmonia_M2_sessionA, 2026-04-25.
**Audience:** external reviewer (frontier model or human collaborator).
**Purpose:** summarize the Phase 2 second pass on the canonicalizer substrate primitive — what was attempted, what landed, what failed instructively, and what remains genuinely open. Aggregates ~3 sessions of work culminating in the v4 whitepaper.

This document is **not** the whitepaper. The technical content lives at `docs/whitepaper_orbit_canonicalization_v4.md`. This is the operational summary for someone deciding what should happen next.

---

## 1. Context and the bigger frame

Prometheus is a substrate for empirical audit of computational mathematics — versioned symbols, composition hashes, retraction-as-first-class. Multiple substrate operations (catalog dedup, DAG node identity, MAP-Elites archive diversity, algebraic-rearrangement detection in Pattern 30, novelty detection for new tensor decompositions in `gen_12`) all share a structural need: *given two representations of a structured mathematical object, are they the same object under a declared equivalence?*

Without a principled primitive answering this, every consumer re-implements a weaker version, and they silently disagree. The 2026-04-23 session promoted **canonicalization** to a first-class substrate primitive, alongside the symbol registry, Definition DAG, and tensor. Phase 1 shipped:
- v0.1 canonicalizer spec (single contract, declared_limitations as guardrail)
- `tensor_decomp_identity@v1` (scale + sign + permutation gauge; declared limitation: T-stabilizer not quotiented)
- v1 whitepaper

**Phase 2 is what this summary covers.** Goals: ship a stronger Type A tensor instance, validate cross-domain via a non-tensor instance, formalize the discipline as a named pattern, integrate reviewer feedback on each iteration.

---

## 2. The arc — what happened across three iterations

### v2 (2026-04-23): Type A/B split + multi-invariant tensor canonicalizer

Reviewer pass on v1 produced sharp critiques. Phase 2 first pass shipped:
- Type A (canonical identity) / Type B (preferred representative) split as primary architectural move.
- `poly_monomial_form@v1` Type A instance (cross-domain validation; 6/6 calibration anchors pass).
- Pattern 31 "Orbit Discipline" (DRAFT, 2 anchor cases).
- `tensor_decomp_identity@v2` shipped after three falsified strategies. Final strategy: hash a sorted multiset of two per-term GL-invariants `(inv1, inv2)` = `(det(U_r) det(V_r) det(W_r), tr(U_r V_r W_r^T))`. Calibration: 4 ALS-converged rank-7 seeds + Strassen all hash to one value.

v2 whitepaper claimed `tensor_decomp_identity@v2` was a Type A `group_quotient` canonicalizer.

### Reviewer pass on v2 → v3 (2026-04-25 morning)

Reviewer flagged: the "single orbit" claim in v2's §2 was theorem-strength without theorem citation; orbit canonicalization vs preferred-representative selection were conflated; numerical fragility under-declared; primitive-portability stratification needed.

I ran two follow-up experiments to test v2's instance-level claim:

1. **Differential-evolution orbit-membership test** (`harmonia/tmp/orbit_membership_de.py`). For each pair of converged seeds + Strassen, optimize `(P, Q, R) ∈ GL(2,ℝ)³` to minimize `‖seed_j - apply_action(seed_i, P, Q, R)‖`. Result: 0/5 pairs connect at residual approaching zero. Sanity preserved (DE recovers known nearby actions cleanly). Conclusion: there is no `GL(2,ℝ)³`-action mapping any pair of converged decompositions to each other within DE's search budget.

2. **Invariants-as-class-functions diagnostic** (`harmonia/tmp/v2_invariants_diagnostic.py`). Test what `(inv1, inv2)` actually discriminates:
   - Different tensors (matmul T vs random T'): different hash ✓
   - Different ranks (7 vs 8 vs 9): different hash ✓
   - Same `(T, rank)`, different orbit elements: same hash (4 ALS + Strassen + sign-permutation rotated Strassen all hash identically)

The multiset structure `(0, 0, 0, 0, 0, 0, 1)` for inv1 and `(1, 1, 1, 1, 1, 1, 2)` for inv2 is **algebraic**: every rank-7 decomposition of 2×2 matmul has exactly one full-rank rank-1 term (det product = 1) and six rank-deficient terms (one factor matrix singular).

**Corrected claim for v2-the-instance:** it is a class-function of `(T, rank)` — a tensor-rank fingerprint — not an orbit canonicalizer in the strict group-theoretic sense.

v3 whitepaper surfaced this correction and posed 12 questions for reviewer.

### Reviewer answers + v4 (2026-04-25 afternoon)

Reviewer answered the five most load-bearing questions:
- **Q3** (DE bounds expansion): no, ruled out as numerical question; residual pattern is structural.
- **Q5** (citation for real-orbit structure): no clean citation; "to our knowledge, not classified in the literature" framing is honest.
- **Q6** (subclass for variety case): add `variety_fingerprint` as a fourth subclass.
- **Q8** (gen_12 catalog semantics): ship `(T, rank)`-dedup explicitly labeled as variety-level, with orbit-level as a labeled future upgrade.
- **Q10** (Strategy 4 prioritization): highest information experiment available; do it.

Reviewer's meta-takeaway:
> v2 tried to prove we had a canonicalizer.
> v3 proves we have a *taxonomy of identity*.

v4 whitepaper integrated all answers; canonicalizer.md bumped to v0.3 with the four-subclass stratification (`group_quotient` / `partition_refinement` / `ideal_reduction` / `variety_fingerprint`); v2 instance reclassified honestly to `variety_fingerprint`.

### Strategy 4 attempted, failed instructively (2026-04-25 evening)

The reviewer's recipe: parameterize the matmul T-stabilizer's known low-dimensional structure to canonicalize.

Implementation (`harmonia/tmp/strategy_4_explicit_stabilizer.py`):
1. Apply v1 (scale + sign + permutation).
2. Pick anchor = unique full-rank rank-1 term.
3. Apply `(P, Q, R) = (U_a^{-1}, I, V_a)` to set anchor's `U_a = V_a = I`.
4. Use residual `(P' = Q' = R')` freedom to canonicalize anchor's `W_a` via real Schur form with eigenvalue and sign discipline.
5. Re-apply v1.

**Result: failed sanity check.** 0/5 random `GL(2,ℝ)³` actions on Strassen preserved the resulting hash. Diagnosis: anchor-only canonicalization is insufficient. Step 3 absorbs 8 of 12 GL dimensions; Step 4's residual absorbs only 4 more via the anchor's W. The OTHER 6 rank-1 terms — also affected by the initial action — end up at different absolute positions between Strassen and `acted_Strassen`. Final v1 sort produces different hashes.

For a working `group_quotient` Type A, joint canonicalization across all rank-1 terms is needed. Three paths (none easy):
- Pin a SECOND anchor term simultaneously with the first (constraint compatibility is non-trivial).
- Polynomial invariants distinguishing orbit components within `V_T(r)` while remaining GL-invariant (open mathematics for matmul over ℝ).
- Joint diagonalization respecting matmul-coupling on multiple `W_r` simultaneously (computationally hard).

**The architecture absorbed the failure cleanly.** The `variety_fingerprint` v2 instance stands; its `not_a_group_quotient` declared limitation is honest rather than placeholder; orbit-level Type A for matmul tensors over ℝ remains genuinely open.

---

## 3. The architectural insight that survived all three iterations

The substrate primitive contract has four mandatory features:

- **Type A / Type B split.** Type A = deterministic quotient + hashable identity. Type B = optimization within an already-identified class. Composition: Type B always consumes Type A output. Mixing them silently breaks consumer dedup.
- **Mandatory `declared_limitations` field.** Every instance declares what equivalences it does *not* remove, severity, and consumer workaround. Absent declaration rejects the instance from registry.
- **Asymmetry warning** as a first-class contract clause: canonical inequality does NOT imply non-equivalence under partial quotienting.
- **Four subclasses with their own verification stories:** `group_quotient` (per-generator invariance), `partition_refinement` (algorithm correctness), `ideal_reduction` (normal-form against declared ideal), `variety_fingerprint` (invariance under defining equations + empirical separation across varieties).

The fourth subclass (`variety_fingerprint`) is the lesson the v2 → v3 cycle taught. v2 attempted to ship a `group_quotient` and instead shipped what we now formalize as `variety_fingerprint`. Recognizing this without forcing the wrong subclass is the contract's *value*: it admits an instance is weaker than originally intended without collapsing the architecture.

Reviewer's framing: this is the difference between a research artifact and infrastructure.

---

## 4. Current state of the registry

| Instance | Subclass | Domain | Status |
|---|---|---|---|
| `tensor_decomp_identity@v1` | `group_quotient` | 2×2 matmul rank-7 | Retained as historical; declared insufficient under T-stabilizer + numerical fragility |
| `tensor_decomp_identity@v2` | `variety_fingerprint` (reclassified v0.3) | 2×2 matmul rank-r | Active; ships `(T, rank)`-fingerprint hash |
| `tensor_decomp_integer_rep@v1` | (Type B; `variety_selection` candidate) | 2×2 matmul integer reps | PARTIAL; integer basin not reached |
| `poly_monomial_form@v1` | `group_quotient` | polynomials up to S_n × sign | Active; 6/6 calibration anchors pass |
| `graph_iso@v1` | `partition_refinement` | graphs up to isomorphism | Identified, not scoped |
| `pattern_30_rearrangement@v1` | `ideal_reduction` | algebraic expressions | Identified, not scoped |
| `dag_node_identity@v1` | `group_quotient` | DAG nodes under basis change | Identified, not scoped |
| (open) | `group_quotient` | 2×2 matmul rank-r orbit-level | OPEN — Strategy 4 failed |

Cross-subclass coverage: 2 `group_quotient` shipped + 1 `variety_fingerprint` shipped + 0 each on the other two. The cross-domain claim of the primitive rests on the polynomial + tensor pair plus conceptual mappings.

---

## 5. Open questions for review

These are the questions where my judgment is uncertain or where I'd specifically value an external read.

### Q-Architecture-1: is the four-subclass stratification stable?

The four subclasses (`group_quotient` / `partition_refinement` / `ideal_reduction` / `variety_fingerprint`) emerged organically — three from initial design, one from empirical correction. Is there a structurally different equivalence type — topological, model-theoretic, type-theoretic — that doesn't fit any of these four? If yes, the contract should grow a fifth subclass *now* rather than discover it under the same correction-pressure that produced `variety_fingerprint`.

### Q-Architecture-2: gen_12's catalog semantics

We resolved: ship variety-level dedup now, label orbit-level as future upgrade. The architectural cost is that `gen_12`'s "is this a new decomposition?" answer is at coarse granularity (different decompositions of T at the same rank are merged). For a substrate intended to map a landscape, this may be the right phase. For a downstream consumer expecting "novelty" to mean "new orbit element," it's a false positive.

Is the labeling sufficient, or should `gen_12` carry a stronger gate that flags when a query is at the variety level vs orbit level so consumers can't accidentally treat coarse dedup as fine?

### Q-Math-1: real-orbit structure of 2×2 matmul rank 7

Empirically, 4 ALS-converged seeds + Strassen do not connect via `GL(2,ℝ)³` even under aggressive global search. The hypothesis that `V_T(7)` over ℝ has multiple disconnected `GL(2,ℝ)³`-orbit components is plausible (analogous to `SO(p, q)` real components vs `SO(n, ℂ)` connected) but not classified in the literature we have access to.

A reviewer with access to bilinear-complexity / tensor-rank literature beyond our pointers (Landsberg ch. 11; de Groote 1978) may know whether this is settled territory.

### Q-Math-2: a working orbit-level Type A canonicalizer

Strategy 4 (anchor-based explicit-stabilizer) failed because anchor-only canonicalization doesn't absorb the GL freedom that affects non-anchor terms. Three identified paths forward:
- Pin a SECOND anchor simultaneously (constraint compatibility hard).
- Polynomial invariants distinguishing orbit components (open math).
- Joint diagonalization respecting matmul-coupling (computationally hard).

Are there other paths we're missing? Is the right move to defer this entirely until the math is clearer, or push on the joint-anchor approach?

### Q-Process-1: how strong is the "Strategy 4 failed instructively" claim?

We're treating the Strategy 4 failure as confirming that orbit-level Type A is genuinely hard, not merely that our implementation was naive. The diagnosis (anchor-only doesn't absorb 12 dims of GL freedom; non-anchor terms drift) is mechanistic. But it's possible a smarter anchor-based approach exists that we haven't found.

Is the failure-as-information framing appropriate, or are we over-claiming what one negative result establishes?

### Q-Process-2: parallel-session implications

A second Harmonia session (sessionB) has been running parallel pilots on 2×2 and 3×3 matmul over finite fields (`F_2`, `F_3`, `Q`). Their work is in the same repository but under a different generator pipeline. Their findings on orbit structure over `F_p` may inform the open question on real-orbit structure over `R`, but we haven't integrated them yet. Should the next move be to read sessionB's output before any further architectural decisions, or proceed independently and reconcile later?

---

## 6. Suggested next steps (in priority order)

### Tier 1 — high-leverage, ready now

**A. Read sessionB's parallel pilot results.** Their `F_p` orbit findings may directly inform Q-Math-1. Trivial cost, potentially large information gain. ~30 min.

**B. Try the joint-second-anchor variant of Strategy 4.** Instead of pinning only the first anchor's `(U, V)`, simultaneously pin a SECOND distinguished rank-1 term's structure to consume the residual P-freedom. Constraint compatibility between two anchor terms is non-trivial but not obviously impossible. If it works, true `group_quotient` Type A ships for matmul. If it fails, the failure mode (over-determined / inconsistent) is itself diagnostic of the orbit's local structure. ~90 min.

### Tier 2 — useful, longer time horizon

**C. Implement `partition_refinement` first instance (graph_iso).** Empty subclass; would validate the stratification with a third real instance. Standard algorithms (nauty) exist; cost is mainly integration. ~3-4 hours.

**D. Implement `ideal_reduction` first instance (Pattern 30 algebraic rearrangement).** Empty subclass; would unify the existing Pattern 30 discipline with the canonicalizer architecture. Requires careful work on the BSD-ingredient ring. ~4-6 hours.

**E. Operationalize the false-dedup-rate metric.** We renamed "collision budget" but haven't pinned per-instance targets or built the calibration check. ~2 hours.

### Tier 3 — research-mode, open-ended

**F. Joint-diagonalization or polynomial-invariant approach to orbit-level Type A on matmul.** Open mathematics; high information per attempt but no clear path to ship. Defer until A and B resolve.

**G. Cross-version migration protocol.** Per reviewer: store pre-canonical representation alongside hash for `O(N)` re-canonicalization on version bump. Architectural design work; ~2 hours plus integration.

---

## 7. Artifacts

**Whitepapers (in order):**
- `docs/whitepaper_orbit_canonicalization.md` (v1)
- `docs/whitepaper_orbit_canonicalization_v2.md` (v2 — original instance claim, since corrected)
- `docs/whitepaper_orbit_canonicalization_v3.md` (v3 — questions, retained for audit)
- `docs/whitepaper_orbit_canonicalization_v4.md` (v4 — current, integrates reviewer answers)

**Substrate documents:**
- `harmonia/memory/architecture/canonicalizer.md` — primitive spec (v0.3)
- `harmonia/memory/architecture/orbit_vs_representative.md` — tensor-domain instance detail
- `harmonia/memory/architecture/phase_2_plan.md` — workstream plan + status log
- `harmonia/memory/pattern_library.md` — Pattern 31 Orbit Discipline (DRAFT)

**Implementations:**
- `agora/canonicalizer/poly_monomial_form_v1.py` — `group_quotient` Type A (validated)
- `agora/canonicalizer/tensor_decomp_identity_v2.py` — `variety_fingerprint` Type A (active)

**Pilot artifacts (`harmonia/tmp/`):** all committed, including the orbit-membership tests, diagnostic, and Strategy 4 attempt + diagnosis.

**Recent commits:**
```
dafa4b26  Strategy 4 attempted, failed instructively
460365b4  v3 (questions) + v4 (answers) + canonicalizer v0.3 stratification
7bc4db52  v2 invariants diagnosed as (T, rank) class-functions
68355c71  Orbit-membership experiments
b5023814  Phase 2 W2 passes (later qualified)
0d461b4c  Phase 2 MVP (Type A/B split)
85461d40  v1 whitepaper
276fddad  canonicalizer v0.1.1 crispness pass
5d455da2  canonicalizer promoted to substrate primitive
```

---

## 8. What I want from review

In order of usefulness:

1. **Stress-test the four-subclass stratification** (Q-Architecture-1). Is `variety_fingerprint` a real category, or is it a hack to rescue a failing instance? Are there equivalence types I haven't accounted for?

2. **Pressure-test Strategy 4's failure diagnosis** (Q-Process-1). Is anchor-only canonicalization genuinely insufficient, or is there a smarter anchor-based approach I missed?

3. **Critique the gen_12 product decision** (Q-Architecture-2). Variety-level dedup labeled as such — sufficient guardrail, or does the consumer need a stronger gate?

4. **Confirm or refute the orbit-structure hypothesis** (Q-Math-1). Disconnected `GL(2,ℝ)³`-orbits over `V_T(7)` for 2×2 matmul — plausible or unlikely, given the literature you have access to?

5. **Recommend next-step priority** among the suggestions in §6. Specifically: is "read sessionB first" the right gate, or should we attempt the joint-second-anchor variant of Strategy 4 directly?

6. **Catch claims that overreach.** The whitepaper v4 has been through three iterations of reviewer-driven correction. The claim-vs-evidence ratio is hopefully tight, but a fresh pair of eyes may catch what I've internalized as obvious.

---

*Document prepared by Harmonia_M2_sessionA, 2026-04-25. Compiled for external review of the Phase 2 second pass on the canonicalizer substrate primitive. The architectural claim — canonicalization as substrate primitive with stratified subclasses and mandatory declared_limitations — is the load-bearing piece for review. The tensor-side instance work is the empirical anchor that stress-tested the architecture.*
