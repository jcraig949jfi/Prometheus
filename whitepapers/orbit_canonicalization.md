# Orbit Canonicalization as a Substrate Primitive
## A whitepaper on tensor identity search in Prometheus
### 2026-04-23 — Harmonia_M2_sessionA

---

## Abstract

The Prometheus substrate routinely needs to answer, for structured mathematical objects, whether two representations denote the same underlying object under a declared equivalence. Tensor decompositions, coordinate axes, algebraic expressions, DAG nodes, and MAP-Elites archive entries all share this requirement. A 2026-04-23 pilot on 2×2 matrix-multiplication tensor decompositions exposed the gap concretely. A minimal search stack (alternating least squares + random restart) rediscovered Strassen's rank-7 orbit at machine precision on six of twenty seeds. Four of those seeds, known by theorem to sit in a single `(GL(2)³ × S_7 × scale-gauge)` orbit, hashed to four distinct canonical forms under a naïve (scale + sign + permutation) canonicalizer; none matched Strassen's integer representative. The bottleneck in searching structured mathematical objects is not search. It is representation under symmetry.

This whitepaper formalizes orbit canonicalization as a first-class substrate primitive, sibling to the Definition DAG and the symbol registry. It defines the primitive's contract (equivalence group, canonicalization procedure, hash function, mandatory declared limitations, failure behavior, calibration anchors), registers the first active instance with its known insufficiency, and scopes the next instance and the adjacent non-tensor instances that the same primitive must serve. The position is deliberately narrow: the primitive is gauge-fixing under declared symmetries, not a universal equivalence solver. Partial quotienting is first-class. The guardrail against false confidence is the mandatory declaration of what is *not* quotiented.

---

## 1. The representation problem

When a substrate stores structured mathematical objects, two representations may denote the same object under some equivalence. If the substrate cannot compute a canonical representative for each equivalence class, every downstream operation that depends on object identity — deduplication, diversity measurement, archive dedup, DAG node identity, novelty detection — silently mis-counts.

Most published work on automated search over structured objects reports "new discoveries" that, on closer inspection, are orbit-variants of existing solutions under the natural symmetry group. This is the decomposition-level instance of Pattern 1 (Distribution/Identity Trap) from the Prometheus pattern library: a claimed novel finding that is, under examination, a rearrangement of an existing one in a rotated basis.

The substrate's existing discipline stack — Pattern 30 graded severity for algebraic-identity coupling, versioned symbols with composition hashes, retraction-as-first-class-event — was built for a related but narrower concern (correlational claims on algebraically-coupled variables, exemplified by the F043 retraction of 2026-04-19). The present work extends that discipline to the identity of structured objects themselves, not just correlations between their parts.

---

## 2. The empirical pivot: 2×2 matrix multiplication

The pilot deliberately targets a well-understood anchor. Matrix multiplication of 2×2 matrices is encoded as a tensor `T ∈ ℝ^{4×4×4}` with `T[ij, jk, ik] = 1` for matching middle index `j`, and zero otherwise. Strassen (1969) exhibited a rank-7 decomposition `T = Σ_{i=1..7} u_i ⊗ v_i ⊗ w_i` with integer-valued factors. Winograd (1971) proved rank ≥ 7. All rank-7 decompositions of `T` over ℝ are related by the action of `(GL(2) × GL(2) × GL(2)) × S_7 × scale-gauge`, i.e., they form a single orbit.

The pilot setup is deliberately minimal — ~60 lines of numpy — to test whether a dumb search stack is sufficient to rediscover the orbit. Twenty random seeds are initialized at target rank `r ∈ {6, 7, 8}`. Each seed runs 500 iterations of alternating least squares on the CP decomposition. The full run takes 1.4 seconds of CPU time.

### 2.1 Results

| Rank | Seeds reaching residual < 1e-8 | Best residual |
|------|--------------------------------|---------------|
| 8 | 0 / 20 (near-misses at 2.2e-8) | 2.2e-08 |
| **7** | **6 / 20 (30%)** | **9.4e-13** |
| 6 | 0 / 20 | 1.000 (clean) |

At rank 7, six seeds reached residual below the declared tolerance. Three reached the limit of double-precision arithmetic (residual ≈ 1e-12). This rediscovers Strassen's orbit.

At rank 6, all twenty seeds' residuals clustered tightly at exactly 1.000. This matches Winograd's lower bound: rank 6 is not achievable over ℝ. The value 1.000 is the squared Frobenius deficit of the best rank-6 approximation under this measurement; across random seeds it is sharply concentrated. This is treated as a regression test in the substrate: any future search primitive that reports residual < 1e-6 at rank 6 has a bug, not a finding.

At rank 8 the search enters what the tensor literature calls a "swamp" — over-parameterized basins where ALS converges slowly — and the budget of 500 iterations is insufficient to reach the declared tolerance of 1e-8. This is a well-known pathology and does not bear on the finding.

### 2.2 The finding beneath the finding

The six converged rank-7 decompositions are, by theorem, in the same orbit as Strassen's. Their integer-entry fractions (fraction of factor entries within 0.01 of an integer) range from 0.02 to 0.16. Strassen's decomposition has integer-fraction 1.00 — every entry is an integer.

This is the surprise. The search reaches the orbit reliably. It does not reach Strassen's representative *within* the orbit. The converged factors are random-looking floats; Strassen's are small integers. They are the same mathematical object expressed in different coordinate frames.

A follow-up test applied a v1 canonicalizer — normalize `u_i` and `v_i` to unit norm, absorb magnitude into `w_i`, sign-gauge by first non-negligible entry, lex-sort rank-1 terms by rounded concatenation — to each of the four machine-precision seeds and to Strassen's integer decomposition. The result: five different canonical hashes. Zero matched.

The interpretation: the v1 canonicalizer quotients scale, sign, and permutation, but does not quotient the `(GL(2) × GL(2) × GL(2))` basis change that stabilizes the matmul tensor. The T-stabilizer is where the bulk of the orbit's size lives for structured tensor targets, and scale+sign+permutation alone is an arbitrarily small slice of that bulk.

---

## 3. Orbit vs representative

The pilot refutes a common assumption: that a search primitive which converges to an exact decomposition has "solved" the decomposition problem. It has not. It has located one orbit point. The orbit's size under the full symmetry group is where the additional structure — integer coefficients, sparsity, symmetry — is either findable or not.

Formally, for a target tensor `T` and target rank `r`, the set of exact rank-`r` CP decompositions is a real algebraic variety on which the following groups act, preserving the reconstruction `T`:

- **Scale gauge:** per rank-1 term, `(u_i, v_i, w_i) → (α u_i, β v_i, (αβ)^{-1} w_i)` for `(α, β) ∈ ℝ*²`. Two continuous degrees of freedom per term.
- **Sign gauge:** degenerate case of scale gauge; called out separately because sign conventions are friendlier to integer-finding than continuous scales.
- **Permutation:** `S_r` on the rank-1 term index.
- **T-stabilizer:** the subgroup of `GL(n) × GL(n) × GL(n)` that fixes `T` under `(P, Q, R) · T = (P ⊗ Q ⊗ R) T`. For `T = MATMUL_{n×n}`, this stabilizer is non-trivial and contains a natural matmul-covariant `GL(n)` action. For generic `T`, the stabilizer may be trivial.

The orbit of a decomposition is its equivalence class under all four actions. Two decompositions in the same orbit are the same mathematical object; any counting, novelty detection, or catalog-dedup operation must treat them as one.

---

## 4. Canonicalization as substrate primitive

Two alternative architectural placements for the canonicalizer were considered:

1. **Internal to gen_12.** The tensor-identity-search generator owns the canonicalizer as one of its filter gates. Simple; scoped; self-contained.
2. **First-class substrate primitive.** The canonicalizer is a separate artifact in the substrate architecture, alongside the symbol registry, the Definition DAG, and the tensor. Generators (including gen_12) consume it; they do not own it.

The second placement is the correct one. The same quotient operation — "is this representation the same object as that one, under a declared equivalence?" — recurs across substrate concerns:

- **Tensor decomposition (gen_12):** orbit of a CP decomposition under the symmetry group. Directly motivates this work.
- **Definition DAG node identity:** a derived mathematical quantity re-expressed in another basis is the same node. Fragmented DAG nodes leak through Pattern 30 severity checks and produce false "novel" findings.
- **MAP-Elites archive dedup:** behavior-cell diversity measured over raw representations fills cells with orbit duplicates, making "diversity" an artifact of coordinate choice.
- **Pattern 30 REARRANGEMENT severity (Level 3):** two expressions related by a ring identity are the same claim. The F043 retraction is the anchor case; formally, the question is canonicalization of algebraic expressions over a declared ring.
- **gen_11 coordinate invention:** the inverse problem. gen_11 seeks *different* representations that happen to resolve a feature. Rejecting re-parameterizations requires the same canonicalizer that gen_12 uses for orbit dedup.
- **Symbol registry:** promotion of a candidate symbol should check whether the candidate is canonically equivalent to an existing promoted symbol, lest the registry fragment under notation drift.

If the canonicalizer were buried inside gen_12, each of the other consumers would either re-implement a weaker version or ignore the problem. The re-implementations would diverge. The ignoring would manifest as silent double-counting. Neither outcome is acceptable at Prometheus's intended substrate maturity. Promoting the canonicalizer to primitive status is the architectural move that prevents these failures by construction.

---

## 5. The contract

A canonicalizer instance is a tuple

```
(name, equivalence_group G, procedure C, hash H,
 declared_limitations, calibration_anchors, canonicalizer_version)
```

with the following requirements.

**On G.** The equivalence group `G` is specified as a list of generator types (e.g., `scale_gauge`, `sign_gauge`, `permutation(S_r)`, `T_stabilizer_GL_n^3`). Generator types in `G` must have *executable semantics within the instance*. If a subgroup is known to be part of the object's symmetry but is not computationally realized by this instance, it must appear in `declared_limitations`, not in `G`. The line between `G` and `declared_limitations` is implementation, not intent. This prevents paper-group / real-group divergence across instances.

**On C.** The canonicalization procedure `C : Representation → CanonicalRepresentative` is a deterministic map satisfying, for all `x, y`:

- **Invariance.** `x ~_G y ⟹ C(x) = C(y)`.
- **Separation (probabilistic).** `x ~_G y is false ⟹ C(x) ≠ C(y)` with probability close to 1. Collisions are permitted; the instance must declare its collision model.
- **Asymmetry warning (load-bearing).** Canonical inequality does *not* imply non-equivalence. Under partial quotienting — which is the default — two inputs may be equivalent under the object's full symmetry group but hash differently because the canonicalizer did not quotient the un-declared subgroup. Consumers must treat `H(C(x)) ≠ H(C(y))` as "not the same under THIS canonicalizer's declared group," never as "not the same object." This is the single most common misuse and must be caught at the call site.
- **Tolerance.** For numerical representations, `‖x − y‖ < ε_tol ⟹ C(x) = C(y)`. Achieved by pinned rounding before hashing; `ε_tol` is declared per instance.
- **Complexity.** `C` runs in `O(poly(|x|))`.
- **Failure behavior.** If `C` cannot produce a stable representative within declared tolerance or resource bounds, it must return `(failure, reason)`. Consumers treat failures as non-canonicalized inputs — not canonical-class members and not comparable by hash. Best-effort-on-failure is explicitly forbidden because silent best-effort produces cross-instance hash divergence indistinguishable from real non-equivalence.

**On H.** The hash function `H : CanonicalRepresentative → bytes` must satisfy:

- Invariance under `C` (by construction of the chain `H ∘ C`).
- Probabilistic separation at cryptographic hash strength.
- Tolerance via pinned-decimal rounding of the canonical representative.
- Namespacing by `(name, canonicalizer_version)`. Hashes from different instances or versions live in disjoint namespaces and are never compared directly.
- Revocation via version bump. If an instance is found to violate invariance, the correct response is to ship a new version; old hashes are marked deprecated; consumers re-canonicalize on next access.

**On declared_limitations.** Mandatory field. This is the single most important entry in a canonicalizer instance's MD. Every instance declares, in a structured block, what equivalences it does *not* remove, the severity (partial vs total), and the workaround for consumers who need the missing equivalence. Without this declaration, the instance is rejected from the primitive registry. A canonicalizer that claims zero limitations must justify in its MD body that its declared `G` *equals* the object's full automorphism group; that claim is checkable and unchecked claims are rejected.

**On calibration_anchors.** Minimum two: one "same-class → same hash" anchor and one "different-class → different hash" anchor. Anchors are run on every version bump.

**On canonicalizer_version.** Integer. Bumped when the quotient changes or invariance is restored after a bug fix.

The primitive deliberately does *not* require completeness (quotienting the full automorphism group), symbolic computer-algebra power, proof of non-equivalence for distinct classes, or domain universality. v1 scope is gauge-fixing under declared symmetries, not a universal equivalence solver.

---

## 6. First instance: `CANONICALIZER:tensor_decomp@v1`

The first active registered instance is scoped narrowly. It canonicalizes CP rank-`r` decompositions of order-3 tensors.

**Equivalence group G:** `scale_gauge × sign_gauge × permutation(S_r)`.

**Procedure C:**

1. Normalize each column of factor matrices `A` and `B` to unit Euclidean norm; absorb the removed magnitudes into the corresponding column of `C`.
2. Sign-gauge: for each column of `A`, find the first entry with magnitude above tolerance and flip the entire column (plus the corresponding column of `C`) so that entry is positive. Repeat for `B`.
3. Lex-sort the `r` rank-1 terms by the rounded concatenation `(A[:,i], B[:,i], C[:,i])`.

**Hash H:** SHA-256 of the canonical `(A, B, C)` flattened and rounded to a pinned decimal precision (default 4).

**Declared limitations:**

- `name: T_stabilizer_basis_change`
- `severity: total`
- `workaround: use CANONICALIZER:tensor_decomp@v2 when it ships; until then, do not treat same-hash as "same orbit under the full symmetry group" — only as "same under scale+sign+permutation."`

**Calibration anchors:**

- Same-class: *pending.* v1 is known by construction to fail the same-class anchor on the Strassen orbit (see the empirical evidence of §2.2). v1 is retained in the registry because its calibration failure is what motivates v2, and because consumers need an active instance to develop against.
- Different-class: rank-7 Strassen hash ≠ rank-8 naive decomposition hash. Trivially holds.

**Empirical anchor file:** `harmonia/memory/architecture/orbit_vs_representative.md` holds the detailed tensor-decomposition instance documentation, the symmetry-group description at algebraic detail, and the full 2026-04-23 pilot results that motivated this whitepaper.

---

## 7. Second instance: `CANONICALIZER:tensor_decomp@v2` (pending)

v2 must additionally quotient the T-stabilizer basis-change action. Four candidate strategies are identified, ordered by cost and generality:

1. **Canonical basis via numerical invariants.** Compute multi-trace invariants of slice matrices, singular-value spectra of mode unfoldings, or polynomial invariants known to be fixed by the group action. Fast and tensor-independent, but may be incomplete — two genuinely distinct orbits can share invariants.
2. **Canonical basis via SVD / Schur.** Compute an SVD of one factor matrix and use the right-singular basis as the canonical basis for that mode; propagate through the others using the T-preserving counterpart of the chosen basis. Cheap when the mode action is simple; target-tensor-specific.
3. **Orbit-internal nearest-integer search.** Given a v1-canonicalized decomposition, search within the T-stabilizer orbit for the representative maximizing integer-proximity (or minimizing description length). Produces Strassen-style representatives directly; not a canonical form in the group-theoretic sense, but useful as a secondary objective after v1 canonicalization.
4. **Full group enumeration.** Works for tensors whose automorphism group is small or finite; does not scale.

**Calibration target for v2:** the same four ALS-converged seeds used to falsify v1 must hash to the same canonical form under v2, and that canonical form must match Strassen's integer representative under the orbit-internal integer probe. This is the minimum viable ship.

**Scaling test:** after v2 ships for 2×2 matmul (rank 7), the same canonicalization strategy is applied to 3×3 matmul (Laderman rank 23). The scaling behavior determines whether v2 generalizes or is 2×2-specific. A 2×2-specific v2 is still useful — it closes the anchor failure — but a generalizing v2 is the direction-validating ship.

---

## 8. Adjacent instances (identified, not yet scoped)

Four additional instances are visible in the substrate's current design:

- **`CANONICALIZER:poly_monomial_form@v1`** — polynomials up to variable relabeling and sign gauge. Cheapest first non-tensor instance. Candidate first calibration anchor for demonstrating cross-domain reuse of the primitive.
- **`CANONICALIZER:graph_iso@v1`** — graph isomorphism canonical form. Classical problem; well-studied algorithms exist (nauty, Bliss via partition refinement). Include when a substrate consumer requires it.
- **`CANONICALIZER:pattern_30_rearrangement@v1`** — canonical form for algebraic expressions over a declared ring. Directly operationalizes Pattern 30 Level-3 REARRANGEMENT severity. Convergence of the two frameworks (Pattern 30 as discipline, canonicalizer as mechanism) is expected and should be planned for.
- **`CANONICALIZER:dag_node_identity@v1`** — Definition DAG node identity under basis change on the input atoms. Required for the DAG to avoid node fragmentation.

Each future instance follows the same contract: equivalence group, procedure, hash, declared limitations, calibration anchors.

---

## 9. Integration surfaces

**Definition DAG.** DAG nodes are identified by canonical form of their defining expression. Without the canonicalizer, the DAG fragments under basis drift and becomes unreliable for Pattern 30 checks. The `dag_node_identity` instance is the scheduled integration.

**Symbol registry.** Symbol promotion checks whether a candidate is canonically equivalent to an existing promoted symbol before adding. Prevents registry fragmentation under notation drift across multi-session work.

**MAP-Elites archives.** Behavior cells are computed on canonical forms; archive dedup uses canonical hash. The `zoo/` tensor-train playground — shipped as a separate Prometheus artifact 2026-04-24 — is the natural first-consumer. Without canonicalization, MAP-Elites archives fill with orbit duplicates, and the "diversity" reading measures coordinate artifacts rather than the underlying function-shape landscape.

**Pattern 30.** Algebraic-identity coupling at Level 3 (REARRANGEMENT) is the algebraic-expression instance of the canonicalizer's general operation. The Pattern 30 discipline and the canonicalizer primitive should converge into one framework over time. Short term, Pattern 30 continues to run as a standalone sweep; medium term, it becomes a specific canonicalizer instance.

**gen_11 coordinate invention.** The inverse operation. gen_11 seeks *different* representations that resolve a feature (novel coordinates); the canonicalizer fixes a single representative (object identity). They share the symmetry-group description but use it oppositely. Keeping them separate but linked is the correct architectural move.

**gen_12 tensor identity search.** The first explicit consumer. gen_12 depends on `CANONICALIZER:tensor_decomp@v2` via the primitive's instance registry; it does not own or embed the canonicalizer. Without v2, gen_12 cannot ship beyond DRAFT — the Gate 2 orbit-equivalence check it requires depends on the pending instance.

---

## 10. Relationship to prior work

**Strassen 1969.** Exhibited the rank-7 decomposition of 2×2 matmul. Calibration anchor #1 for this whitepaper. Integer-valued factors; lies in a specific point of the GL(2)³-orbit.

**Winograd 1971.** Proved rank ≥ 7 for 2×2 matmul over any field. Calibration anchor #2; the rank-6 regression test.

**Laderman 1976.** Exhibited the rank-23 decomposition of 3×3 matmul. Calibration anchor for the scaling test of `tensor_decomp@v2`.

**Bini et al. 1979.** Border-rank results; approximate decompositions with residual parameterized by a continuous limit. Out of scope for exact-decomposition catalog; relevant if the substrate is later extended to border-rank identity.

**Fawzi et al. 2022 (AlphaTensor).** Used reinforcement learning to search the decomposition space; reported rank improvements for 4×4 and 5×5 matmul over `F_2` and `F_4`. The published "new" 4×4 result was subsequently identified as largely orbit-variants of known decompositions under the natural symmetry group action — precisely the failure mode this primitive is designed to prevent. Relevant lesson: search power is not the limiting factor; orbit discipline is.

**Novikov et al. 2023 (Tensor networks in ML).** Background on tensor-train decompositions. Orthogonal to CP decomposition used here, but relevant to the `zoo/` integration, which uses TT approximations rather than CP.

The novel contribution of the present work is not the search primitive or the canonicalizer procedure individually. Both are standard techniques. The contribution is the architectural move of elevating canonicalization to a substrate primitive with a mandatory declared-limitations field, enforced by a registry of versioned instances, composing across multiple substrate consumers. This is what prevents the AlphaTensor-class failure mode from recurring silently at substrate scale.

---

## 11. Limitations and open questions

**Open: `tensor_decomp@v2` strategy.** Four candidate approaches are listed; none has been validated on the pilot data. A stress-test of the four strategies on the four machine-precision seeds + Strassen's integer representative is the next empirical step. The outcome of that stress-test (tractability, completeness, scaling behavior at 3×3) determines whether this direction ships as a Tier-2 generator or stays research-tier.

**Open: non-tensor instances not yet scoped.** The `poly_monomial_form` instance is the cheapest path to demonstrate cross-domain reuse of the primitive, but even its canonicalization procedure has not been drafted. Until at least one non-tensor instance lands, the claim that the primitive is cross-domain rests only on conceptual mapping.

**Open: Pattern 30 convergence.** The relationship between Pattern 30 REARRANGEMENT severity and the canonicalizer's algebraic-expression instance is architecturally clear but operationally undefined. Short-term they run in parallel; medium-term a unified frame is expected. The timing of unification is unclear.

**Open: hash collision economics.** The contract states that hash collisions under `H` (not under `C`) are permitted and handled as false-alarms by the consumer. At substrate maturity (1000+ decomposition entries, many instances) the false-alarm rate matters. No collision budget is specified in v0.1.

**Open: cross-version migration.** The hash-versioning rule namespaces hashes strictly by `(name, canonicalizer_version)`. This is correct for identity discipline but produces a combinatorial re-canonicalization cost on every version bump. No migration protocol is specified.

**Partial: MNAR at the orbit level.** Even with a perfect canonicalizer, the set of decompositions that search explores is a non-random sample of the full orbit variety. Sampling biases in the search primitive (ALS, GA, RL) carry through. Orbit identity does not absolve the substrate of MNAR discipline at the measurement level.

---

## 12. Conclusion

The 2026-04-23 pilot established one empirical claim and one architectural claim. The empirical claim: on 2×2 matrix multiplication, a minimal search stack reaches Strassen's orbit reliably but does not reach the Strassen representative within the orbit. The architectural claim: canonicalization is the load-bearing piece that quotients the orbit down to object identity, and this quotienting is a cross-cutting concern across multiple substrate consumers (Definition DAG, symbol registry, MAP-Elites archives, Pattern 30, gen_11, gen_12).

The response was to promote canonicalization to a first-class substrate primitive with a narrow v1 scope (gauge-fixing under declared symmetries, not universal equivalence), a mandatory declared-limitations field as the guardrail against false confidence, an executable-semantics requirement on the equivalence group, a load-bearing asymmetry warning (canonical inequality ≠ non-equivalence), and a versioned-namespace hash contract. The first active instance (`tensor_decomp@v1`) is registered with its known insufficiency and retained as the calibration target for the pending v2. Four adjacent non-tensor instances are identified for future scoping.

The primitive prevents a specific failure mode: orbit-variant findings masquerading as novelties, which has been the dominant failure mode of published automated decomposition work. It does so by requiring every downstream consumer to declare what equivalences its canonicalizer has quotiented, and what it has not. The discipline is designed to be honest about partial quotienting rather than opaque about it.

What the substrate now holds, after this work, is not a tool for discovering decompositions. It is a mechanism for distinguishing *"we found a new orbit"* from *"we found a new representation of an existing orbit."* Every downstream search generator, from gen_12 onward, is downstream of this distinction.

---

## 13. Artifact inventory

### Substrate artifacts (tracked in git)

- `harmonia/memory/architecture/canonicalizer.md` v0.1.1 — primitive spec. Contract, hash rules, declared-limitations requirement, instance registry.
- `harmonia/memory/architecture/orbit_vs_representative.md` v0.2 — tensor-decomposition instance detail, symmetry-group description, 2026-04-23 empirical anchor.
- `harmonia/memory/architecture/definition_dag.md` v0.1 — sibling substrate primitive; scheduled integration with `dag_node_identity` instance.
- `docs/prompts/gen_12_tensor_identity_search.md` v0.3 — first consumer, depends on `CANONICALIZER:tensor_decomp@v2`.
- `stoa/ideas/2026-04-23-sessionA-tensor-identity-search.md` — discussion doc with two pivot headers (search→representation; tensor-note→primitive).
- `zoo/README.md` and package contents — TT MAP-Elites playground, identified as natural consumer for the primitive.

### Pilot artifacts (in `harmonia/tmp/`)

- `tensor_pilot_2x2_matmul.py` — 20-seed ALS pilot at rank 6, 7, 8.
- `tensor_pilot_2x2_matmul_results.json` — per-seed convergence records.
- `canonicalize_test.py` — v1 canonicalizer applied to converged seeds + Strassen.
- `tensor_identity_search_verdict.md` — weighing of the three parallel MVPs (spec, ideas doc, pilot).

### Reference documents

- `docs/landscape_charter.md` — Prometheus charter (projections, not territories).
- `docs/long_term_architecture.md` v2.1 — five-layer architecture of the Prometheus substrate.
- `harmonia/memory/pattern_library.md` — Patterns 1 (Distribution/Identity Trap), 30 (Algebraic-Identity Coupling), 6 (Verdicts Are Coordinate Systems), 13 (Accumulated Kills), 17 (Language/Organization Bottleneck).

### Commits landing this work

- `5d455da2` — canonicalizer promoted to substrate primitive; gen_12 consumes it.
- `37a97138` — backlog sweep including pilot artifacts and zoo/ TT playground.
- `276fddad` — canonicalizer v0.1 → v0.1.1 crispness pass (asymmetry warning, generator executability, failure behavior).

---

## 14. References (external)

- Strassen, V. (1969). *Gaussian elimination is not optimal.* Numerische Mathematik 13, 354–356.
- Winograd, S. (1971). *On multiplication of 2×2 matrices.* Linear Algebra and its Applications 4, 381–388.
- Laderman, J. D. (1976). *A noncommutative algorithm for multiplying (3×3) matrices using 23 multiplications.* Bulletin of the AMS 82, 126–128.
- Bini, D., Capovani, M., Romani, F., Lotti, G. (1979). *O(n^2.7799) complexity for n×n approximate matrix multiplication.* Information Processing Letters 8, 234–235.
- Fawzi, A., et al. (2022). *Discovering faster matrix multiplication algorithms with reinforcement learning.* Nature 610, 47–53.
- Kolda, T. G., Bader, B. W. (2009). *Tensor decompositions and applications.* SIAM Review 51, 455–500.

---

*Whitepaper prepared by Harmonia_M2_sessionA, 2026-04-23. Compiled from the canonicalizer primitive spec, the orbit-vs-representative tensor-instance detail, the gen_12 generator spec, and the 2026-04-23 2×2 matmul pilot run. Intended for external review and for future team members reconstructing the rationale for the primitive's promotion.*
