# CANONICALIZER — substrate primitive

**Status:** substrate-primitive spec, v0.2 (2026-04-23, Phase 2).
**Architectural slot:** first-class primitive, alongside the symbol registry, the tensor, Definition DAG, and signals.specimens. Not a generator.
**Audience:** gen_12 (tensor decomposition), gen_11 (coordinate invention), Definition DAG authors, symbol-registry curators, any module that dedup's or displays structured objects.

---

*In one sentence:* **a canonicalizer instance is either (Type A) a deterministic quotient map producing stable hashable identity under a declared equivalence group, OR (Type B) an optimization inside an already-identified orbit producing a preferred representative for a declared secondary objective.**

---

## Two types (load-bearing — added v0.2)

The v0.1.1 spec conflated two distinct operations. v0.2 splits them:

- **Type A — canonical identity.** A deterministic quotient map that produces a hashable canonical representative for each equivalence class under a declared group. Answers *"are these the same object under G?"* Uniqueness of the canonical representative per class is a hard requirement. Hash equality iff orbit equality (modulo the separation bound on H).
- **Type B — preferred representative.** An optimization inside an already-identified orbit against a declared secondary objective (integer-proximity, minimum description length, sparsity, symmetry score). Answers *"which element of this orbit is the most useful one to display?"* Uniqueness is NOT required — ties are permitted, perturbations may flip which representative wins, and Type B output is not stable enough to hash for identity.

**Composition rule.** Type B always operates on Type A output. Running Type B alone — on raw input not first Type-A-canonicalized — is forbidden, because the "orbit" the Type B is optimizing within is not well-defined without Type A's quotient.

**Why split.** Mixing the two produces silent drift: an optimization-for-integers layer that looks like a quotient map will return different outputs for the same orbit under small perturbations, breaking hash invariance at Type-A consumer sites. Downstream consumers that dedup against hash equality will then count orbit-duplicates as distinct. The Type A / Type B distinction is the architectural guardrail; the `type:` field in every instance's frontmatter is mandatory and checked at registration.

Every instance declares exactly one type. Instance names conventionally carry a suffix for readability: `<name>_identity@vN` for Type A, `<name>_<objective>@vN` for Type B (e.g., `tensor_decomp_identity@v2`, `tensor_decomp_integer_rep@v1`).

---

## Why this exists

Many substrate operations — catalog dedup, DAG node identity, MAP-Elites diversity, Pattern-30 equivalence — assume they can answer "are these the same object?" for structured objects that admit multiple representations of the same underlying thing. They can't, today, without a common primitive.

A 2026-04-23 tensor-decomposition pilot made the gap concrete. Four ALS-converged rank-7 decompositions of 2×2 matmul, known by theorem to be in one `(GL(2)³ × S_7 × scale-gauge)` orbit, hashed to four different canonical forms under a naive (scale + sign + permutation) canonicalizer; none matched Strassen's integer representative. The evidence is preserved in `harmonia/memory/architecture/orbit_vs_representative.md` (the empirical-anchor companion to this doc).

The same shape recurs across substrate concerns:

- **Tensor decomposition** (gen_12): orbit of a decomposition under symmetry group.
- **Definition DAG nodes:** a derived quantity re-expressed in another basis is the same node; fragmented nodes leak through Pattern 30 checks.
- **MAP-Elites archives:** "diversity" over coordinate artifacts fills cells with orbit duplicates.
- **Pattern 30 algebraic coupling:** two expressions related by a ring identity are the same claim; Level-3 REARRANGEMENT is the same pattern as "different gauge of the same decomposition."
- **gen_11 coordinate invention:** the inverse problem — explore *different* representations that happen to resolve a feature. Still needs a canonicalizer to reject re-parameterizations.
- **Symbol registry:** promotes primitives; without canonicalization, two equivalent primitives get different names and references fragment.

Across all of these, the common question is: *given two representations of a structured object, are they the same object under a declared equivalence?* That question is what this primitive answers — narrowly, explicitly, and with declared limits.

---

## The contract

A **canonicalizer instance** is a tuple

```
(name, type, equivalence_group G, procedure C, hash H (Type A only),
 secondary_objective (Type B only),
 declared_limitations, calibration_anchors, canonicalizer_version)
```

where:

- `type` ∈ {`A`, `B`}. Mandatory. Determines which of the other fields are required and which invariants apply. Type A instances require `G` + `C` + `H` + `declared_limitations` + `calibration_anchors`. Type B instances require `G` (the orbit their input is Type-A-canonicalized under) + `C` (the optimization procedure) + `secondary_objective` + `declared_limitations` + `calibration_anchors`. Type B does NOT have a hash; Type B output is for display, not identity.

- `G` is the equivalence group the instance quotients, specified as a list of generator types (e.g., `scale_gauge`, `sign_gauge`, `permutation(S_r)`, `T_stabilizer_GL_n^3`). **Generator types in `G` must have executable semantics within the instance.** If a subgroup is known to be part of the object's symmetry but is not computationally realized by this instance (e.g., a stabilizer that only exists on paper), it must appear in `declared_limitations`, not in `G`. The line between `G` and `declared_limitations` is implementation, not intent.
- `C : Representation → CanonicalRepresentative` is a deterministic map satisfying, for all `x, y` in the representation space:
  - **Invariance.** `x ~_G y ⟹ C(x) = C(y)`.
  - **Separation (probabilistic).** `x ~_G y is false ⟹ C(x) ≠ C(y)` with probability close to 1. Collisions are permitted; instance must declare the collision model.
  - **Asymmetry warning (load-bearing).** Canonical inequality does **NOT** imply non-equivalence. Under partial quotienting — which is the default, per `declared_limitations` — two inputs may be equivalent under the object's full symmetry group but hash differently because the canonicalizer did not quotient the un-declared subgroup. Consumers MUST treat `H(C(x)) ≠ H(C(y))` as *"not the same under THIS canonicalizer's declared group"*, never as *"not the same object."* This is the single most common misuse and must be caught at the call site.
  - **Tolerance.** For numerical representations, `‖x − y‖ < ε_tol ⟹ C(x) = C(y)` via pinned rounding before hashing.
  - **Complexity.** `C` runs in `O(poly(|x|))`.
  - **Failure behavior.** If `C` cannot produce a stable representative within declared tolerance or resource bounds, it must return `(failure, reason)`. Consumers MUST treat failures as non-canonicalized inputs — not as canonical-class members, and not comparable by hash. "Best-effort on failure" is explicitly forbidden; silent best-effort produces cross-instance hash divergence that is indistinguishable from real non-equivalence.
  - **Failure stability (added v0.2).** Failure itself must be stable under tolerance. If `C(x) = failure` and `‖x − y‖ < ε_tol`, then either `C(y) = failure` with the same reason, or `C(y) = canonical` but not unpredictably oscillating between the two across nearby inputs. An instance where one input succeeds and a near-identical input fails is a bug, not a design choice — it produces archive fragmentation indistinguishable from real non-equivalence. Test: apply `C` to an ε-perturbed batch of inputs; the failure/success partition must be coherent (all in, all out, or a cleanly separated boundary with no mode-switching inside a tolerance ball).
- `H : CanonicalRepresentative → bytes` is a hash function (Type A only). The contract requires: (1) deterministic serialization of the canonical representative, (2) namespacing by `(name, canonicalizer_version)`, (3) tolerance pinning (ε-close representatives hash identically). The choice of cryptographic hash primitive (SHA-256 etc.) and the exact decimal-pinning precision are **implementation details**, not part of the contract. See "Implementation notes" below. Different instances and different versions live in disjoint hash namespaces and are never compared directly.
- `declared_limitations` is an **explicit list of equivalences NOT removed.** Mandatory. Without this declaration the instance is rejected from the primitive registry. The declaration is the guardrail against false-confidence: downstream consumers must know what the canonicalizer does not quotient, so they don't assume equivalences it didn't touch.
- `calibration_anchors` are test cases with known equivalence-class structure — at least one "same-class → same hash" anchor and one "different-class → different hash" anchor. Anchors are run on every version bump.
- `canonicalizer_version` is an integer; hash namespaces change on version bump.

The primitive deliberately **does not** require:
- Completeness (quotienting the full automorphism group of the object)
- Symbolic computer-algebra power
- Proof of non-equivalence for distinct classes
- Domain universality

v1 is scoped as *gauge fixing under declared symmetries*, not a universal equivalence solver. Partial quotienting is first-class; the declared-limitations field is how partial-ness is expressed honestly.

---

## Declared-limitations — mandatory field

This is the single most important field in a canonicalizer instance.

Every instance's MD declares:

```yaml
declared_limitations:
  - name: <symmetry-type-not-quotiented>
    severity: partial | total
    workaround: <how a consumer can still act correctly under this limitation>
```

Example (tensor decomposition v1):
```yaml
declared_limitations:
  - name: T_stabilizer_basis_change
    severity: total
    workaround: use canonicalizer v2 when it ships; until then, do not treat
      same-hash as "same orbit under the full symmetry group" — only as "same
      under scale+sign+permutation."
```

Without this field, downstream code that assumes "same hash ⟹ same object" will be wrong in ways that are invisible at the call site. The 2026-04-23 pilot is the anchor failure mode: a consumer that naively treated v1 hashes as orbit identities would count five distinct orbits where there is one.

A canonicalizer that claims zero limitations must justify it in the MD body with an argument that the equivalence group it quotients *equals* the automorphism group of the object under the declared operation. That argument is checkable; unchecked "complete" claims are rejected.

---

## Instance registry (extensible)

The canonicalizer primitive is a registry of named instances. At v0.1, one instance is active, one is pending, and several are identified as future needs.

### Active: `CANONICALIZER:tensor_decomp_identity@v1` (Type A)

- **Type:** A (canonical identity).
- **Equivalence group:** `scale_gauge × sign_gauge × permutation(S_r)`. Applies to CP-rank-r decompositions of order-3 tensors.
- **Procedure:** normalize `‖u_i‖ = ‖v_i‖ = 1`, absorb magnitude into `w_i`; canonical sign (first entry above tolerance of each `u_i, v_i` is positive, partner sign absorbed); lex-sort rank-1 terms by rounded concatenated `(u_i, v_i, w_i)`.
- **Hash:** see Implementation notes.
- **Declared limitations:**
  - `T_stabilizer_basis_change` (total). For structured target tensors (matmul, Pfaffian, etc.) this is where most of the orbit's size lives. Consumers must NOT treat same-hash-under-v1 as same-orbit-under-full-symmetry-group.
- **Calibration anchors:**
  - Same-class: FAILS by construction (see Empirical anchor). v1 is retained in the registry *only because* the failure is declared, reproducible, and used as the regression target for v2 development — not because anchor-failing instances are generally admissible. The license for retention is narrow and single-instance.
  - Different-class: rank-7 Strassen hash ≠ rank-8 naive decomposition hash (trivially holds).
- **Empirical anchor:** 2026-04-23, `harmonia/tmp/canonicalize_test.py`. 4 ALS-converged rank-7 decompositions of 2×2 matmul, understood to lie in the same equivalence class under the natural symmetry action (see `orbit_vs_representative.md` §"On theorem claims"), hashed to 4 distinct v1 canonical forms; none matched Strassen's v1 hash.

### Active: `CANONICALIZER:tensor_decomp_identity@v2` (Type A) — SHIPPED 2026-04-23

- **Type:** A.
- **Equivalence group:** `scale_gauge × sign_gauge × permutation(S_r) × GL(2)³ matmul-covariant action × discrete Aut(T)` (transpose + factor-role permutation).
- **Procedure:** multi-invariant numerical canonical form using two provably `Aut(T)`-invariant per-term scalars:
  - `inv1_r = det(U_r) · det(V_r) · det(W_r)`
  - `inv2_r = tr(U_r V_r W_r^T)`
  where `U_r, V_r, W_r` are the 2×2 reshapes of the r-th rank-1 term's factor columns. Both scalars verified invariant under the matmul-covariant action `(A → PAQ⁻¹, B → QBR⁻¹, C → P⁻ᵀCRᵀ)`. Both also invariant under the discrete `Aut(T)` symmetries (det preserved by transpose; trace-UVW is cyclic-invariant). The sorted tuples `(sorted(inv1_1..r), sorted(inv2_1..r))` form the canonical fingerprint; SHA-256 hash of their JSON serialization (with `-0.0 → 0.0` normalization) is the canonical hash. Implementation: `agora/canonicalizer/tensor_decomp_identity_v2.py`.
- **Hash:** SHA-256 of `{inv1_det_prod: [...], inv2_trace_uvw: [...]}` (deterministic JSON, ordered keys, `-0.0` normalized to `0.0`).
- **Declared limitations:**
  - `orbit_completeness_not_proven` (partial) — invariants pass the 2×2 calibration but are not proven orbit-complete in general; separation is probabilistic. Workaround: consumers needing separation on other tensors add per-target calibration anchors.
  - `fixed_to_2x2_matmul_shape` (total) — factors must reshape into 2×2 matrices; `n × n` matmul requires a separate instance.
  - `probabilistic_separation` (partial) — distinct orbits sharing `(inv1, inv2)` tuples collide; not exhaustively tested. 2-dim invariant is a low-dim fingerprint.
- **Calibration anchors:**
  - Same-class: **PASS**. 4 ALS-converged rank-7 decompositions + Strassen's integer rep all hash identically. 6/6 pair-agreements.
  - GL invariance: **PASS**. 10/10 random `GL(2)³` actions on Strassen preserve the hash.
  - Different-class: **PASS**. Rank-8 naive decomposition hashes distinctly from rank-7 Strassen.
  - Evidence: `harmonia/tmp/tensor_gl2_invariants_minimal_results.json`.
- **Path to v2:** three prior strategies were falsified before this one succeeded. The falsifications are retained as data.
  - *Falsified — Strategy 1 (multi-invariant SV / Gramian / Frobenius).* Root cause: these are *orthogonal*-invariants, not GL-invariants. The T-stabilizer for matmul acts as GL, not O, so orthogonal invariants don't collapse it. Mode-unfolding SVs are tensor-of-T invariants (same across all rank-r decomps of T), so they don't discriminate orbits either.
  - *Falsified — Strategy 2 (QR reduction of first rank-1 term).* Canonicalizing only the first term leaves the remaining GL freedom uncollapsed. 0/6 pair-agreements.
  - *Not tried — Strategy 4 (full group enumeration).* Superseded by the v2 analytic invariants; retained for a future tensor target where invariant derivation may be harder.

### Replaced: `CANONICALIZER:tensor_decomp_identity@v1` (superseded 2026-04-23)

v1 is superseded by v2 in the same calibration. Retained in the registry as the historical record of the scale+sign+permutation-only quotient; any consumer referencing v1 hashes should migrate to v2 (different namespace; cross-version comparison is forbidden per the hash contract).

### Pending: `CANONICALIZER:tensor_decomp_integer_rep@v1` (Type B)

- **Type:** B (preferred representative — integer-proximity).
- **Equivalence group:** `T_stabilizer_GL_n^3` (the orbit the input is assumed already Type-A-canonicalized in).
- **Procedure:** OPEN. Phase 2 W3 attempted **Strategy A — Gaussian perturbation + ALS refinement.** Perturb factor matrices with Gaussian noise, re-refine to the reconstruction variety via ALS, keep best integer_fraction while residual stays bounded. **FALSIFIED** 2026-04-23 on the pilot anchor: 0/4 ALS seeds reached integer_fraction ≥ 0.9; best improvement was 0.000 from three of four starting points. Diagnosis: Gaussian perturbation + ALS returns to the nearest basin in the same gauge, not to Strassen's integer basin. The integer basin is measure-zero in the continuous orbit; random perturbation does not hit it. Evidence: `harmonia/tmp/tensor_decomp_integer_rep_v1_results.json`.
- **Remaining search-strategy candidates (untested):**
  - Simulated annealing with explicit integer-snap moves.
  - L-BFGS minimization with integer-distance penalty added to reconstruction loss.
  - Enumeration over the matmul-covariant `GL(2)³` action (exploits the specific T-stabilizer structure; may be tractable because 2×2 matmul's stabilizer has known algebraic form).
- **Secondary objective:** `integer_fraction = fraction of entries in (A, B, C) with |x - round(x)| < 0.01`.
- **Declared limitations:**
  - Output is not hash-stable; different calls on equivalent Type-A-canonicalized inputs may return different integer representatives if ties exist.
  - Not unique. Multiple orbit elements may share the same integer-fraction score.
  - Convergence to global max is not guaranteed (local optimization).
- **Calibration target:** given any of the 4 ALS seeds as input, recover a representative with integer_fraction ≥ 0.9 (Strassen has 1.0).
- **Status:** OPEN. Strategy A falsified; next-session candidates listed above.

### Future instances (identified, not yet scoped)

- `CANONICALIZER:poly_monomial_form@v1` (Type A) — polynomials up to variable relabeling and sign gauge. Target for Phase 2 W4 as the first non-tensor Type A instance.
- `CANONICALIZER:graph_iso@v1` (Type A) — graph isomorphism canonical form. Classical; inclusion when a consumer needs it.
- `CANONICALIZER:pattern_30_rearrangement@v1` (Type A) — canonical form for algebraic expressions over a declared ring. This is a *separate instance of the same contract*, not a second-name for the tensor canonicalizer — the computational objects (tensor factor triples vs algebraic expressions) are genuinely different, they share only the primitive contract. Convergence of the Pattern 30 discipline with this instance is expected and planned; the two frameworks run in parallel until unification is concrete.
- `CANONICALIZER:dag_node_identity@v1` (Type A) — Definition DAG node identity under basis change on input atoms.

Each future instance follows the same contract: type declaration + equivalence group + procedure + (hash OR secondary_objective) + declared limitations + calibration anchors.

---

## Implementation notes

These are implementation defaults, not contract requirements. Implementations may choose differently provided the contract (determinism, tolerance, namespacing) is met.

- **Hash primitive.** SHA-256 is the current default. BLAKE3 or other cryptographic hashes with ≥ 128 bits of collision resistance would satisfy the contract equivalently. The choice is not normative.
- **Decimal pinning.** Default precision: 4 decimal places on rounded canonical-representative entries before hashing. Instances whose tolerance requires more or fewer digits should declare `decimal_pinning` in the instance MD frontmatter.
- **Serialization.** Default: `concatenate(flatten(A), flatten(B), flatten(C))` with numpy's native ordering. Other deterministic orderings (row-major vs column-major, factor-triple interleaving) are acceptable if declared.

Instances may migrate between implementations within a single `canonicalizer_version` if the change does not affect hash output on the full anchor set. Implementation changes that DO affect hashes require a `canonicalizer_version` bump.

---

## Orbit discipline (named doctrine — added v0.2)

**Definition:** the requirement that identity claims on structured objects be made modulo declared symmetry groups, with partial quotienting expressed honestly via `declared_limitations`, and with canonical inequality *never* treated as non-equivalence.

Orbit discipline is the substrate-level generalization of Pattern 30 REARRANGEMENT severity. Pattern 30 handles the specific case of algebraic-identity coupling in correlation claims; orbit discipline handles the general case of structured-object identity under any declared symmetry.

See `pattern_library.md` Pattern 31 (DRAFT, 2026-04-23) for the pattern entry with anchor cases (F043 retraction, 2×2 matmul pilot).

---

## Composes with

- **Definition DAG** — DAG nodes identified by canonical form of their defining expression. Without a canonicalizer, nodes fragment under basis drift. With one, DAG edges are between canonical objects, not between representations. The `CANONICALIZER:dag_node_identity@v1` instance (when scoped) is the concrete integration.
- **Symbol registry** — symbol promotion checks whether a candidate is canonically equivalent to an existing promoted symbol before adding. Avoids registry fragmentation under notation-drift.
- **MAP-Elites archives** — behavior cells are computed on canonical forms; archive dedup uses canonical hash. Without this, MAP-Elites fills cells with orbit duplicates masquerading as "diversity."
- **Pattern 30** — algebraic-identity coupling at severity Level 3 (REARRANGEMENT) is the same question the canonicalizer answers for algebraic expressions. Either Pattern 30 is rebuilt as a canonicalizer instance, or the canonicalizer calls into Pattern 30 machinery for its algebraic-expression instances. Convergence of the two frameworks is expected and should be planned for.
- **gen_11 coordinate invention** — the dual operation: gen_11 explores transformations (seeks diversity of useful representations); canonicalizer fixes a representative (seeks identity across representations). They share machinery (symmetry group descriptions) but use it oppositely. Linked but distinct.
- **gen_12 tensor identity search** — the first consumer. The generator depends on `CANONICALIZER:tensor_decomp@vN` but does not own the primitive.

---

## Hash contract (normative)

1. **Invariance.** For the declared equivalence group `G`, `x ~_G y ⟹ H(C(x)) = H(C(y))`. Violations are bugs in the canonicalizer, not in the consumer.
2. **Separation.** `x ~_G y is false ⟹ H(C(x)) ≠ H(C(y))` with probability indistinguishable from a good cryptographic hash. Collisions under the hash (not under `C`) are acceptable as false-alarms to be resolved by the consumer.
3. **Tolerance.** For numerical inputs, ε-close inputs produce identical hashes. ε is declared per instance.
4. **Namespaced.** Hashes are namespaced by `(instance_name, canonicalizer_version)`. A v1 hash and a v2 hash are never compared directly; cross-version dedup requires re-canonicalization through the newer version.
5. **Cheap.** Hash computation is `O(poly(|x|))`.
6. **Revocable via version bump.** If a canonicalizer instance is found to violate invariance (a bug), version bump; old hashes are marked `deprecated_namespace`; consumers re-canonicalize on next access.

---

## What this primitive is NOT

- Not a universal equivalence solver. Symbolic equivalence over rings, homotopy equivalence, bisimulation — all out of scope. Instance-based narrow quotients only.
- Not a symbolic computer-algebra system. It uses symbolic tools (sympy, etc.) inside instances, but the primitive's contract is about canonical forms and hashes, not about computer algebra.
- Not a proof engine for non-equivalence. Separation is probabilistic; two things having different hashes is strong evidence they're different, not proof.
- Not a replacement for Pattern 30. Pattern 30 answers "is this correlation algebraically induced?" — the canonicalizer is one mechanism in service of that answer, not a superset.
- Not a schema for MAP-Elites archive keys. An archive may use canonical hashes as keys; the archive itself is separate infrastructure.

---

## v0.1 exit criteria

To graduate this spec from v0.1 to v1.0:

1. [ ] `CANONICALIZER:tensor_decomp@v2` passes its calibration anchor on 2×2 matmul (4 ALS-converged rank-7 seeds hash same; canonical form recovers Strassen under integer probe).
2. [ ] One additional instance is scoped and drafted (candidate: `CANONICALIZER:poly_monomial_form@v1` — cheapest first example).
3. [ ] The Definition DAG spec is updated to reference this primitive for node identity.
4. [ ] One downstream consumer (gen_12 is the natural first) reports in its own MD that it depends on `CANONICALIZER:<instance>@v<N>`, via a `requires:` field.

Minimum viable ship is item 1 alone: the first instance's first real calibration pass. Items 2–4 compound the value but item 1 is the primitive's proof-of-concept.

---

## Design constraints held

Per 2026-04-23 James directive, narrowly scoped. This primitive deliberately:

- Does not attempt full symbolic equivalence.
- Does not unify all domains in v1.
- Requires explicit equivalence-group declaration per instance.
- Requires explicit limitation declaration per instance.
- Permits partial quotienting as a first-class outcome, not a failure mode.
- Uses hashable outputs for identity and dedup; numerical tolerance built in.

The risk being guarded against is primitive-bloat through ambitious generalization. The abstraction is tight: *gauge fixing under a declared, bounded symmetry group, with explicit statement of what is left un-fixed.*

---

## Version history

- **v0.2.1** — 2026-04-23 (Phase 2 continuation) — `CANONICALIZER:tensor_decomp_identity@v2` SHIPPED after third-strategy success. Two GL(2)³-invariant per-term scalars (det product + tr UVW^T) plus `-0.0 → 0.0` normalization produce a hash that passes all three calibration anchors (same-class 4/4 + 6/6 pairs; GL invariance 10/10; different-class rank-7 vs rank-8 separation). Two prior strategies (SV/Frobenius multi-invariant; first-term QR) were falsified before this one succeeded; falsifications retained in the registry as data. Implementation landed at `agora/canonicalizer/tensor_decomp_identity_v2.py`. v1 is now superseded but retained as historical record.
- **v0.2** — 2026-04-23 (Phase 2) — major: Type A / Type B split added as the primary architectural move in response to James's 2026-04-23 whitepaper review. Every instance now declares `type` in its tuple. Type A = deterministic quotient + hash (identity). Type B = optimization inside an already-identified orbit (display). Composition rule: Type B always consumes Type A output. Supporting changes: (a) tensor_decomp@v1 renamed tensor_decomp_identity@v1 with narrowed justification for retention despite anchor-failure (admissible *only* because failure is declared + reproducible + regression-targeted, not because failing anchors is generally OK); (b) tensor_decomp_identity@v2 and tensor_decomp_integer_rep@v1 registered as pending, split correctly between Type A and Type B; (c) failure-stability clause added to procedure contract — failure must be stable under tolerance; (d) hash primitive (SHA-256) moved to Implementation notes; contract requires determinism + namespacing + tolerance pinning, not a specific cryptographic choice; (e) Pattern 30 integration clarified — pattern_30_rearrangement@v1 is a *separate instance of the same contract*, not a second name for tensor canonicalizer; (f) "orbit discipline" formalized as a named doctrine with cross-reference to pattern_library.md Pattern 31.
- **v0.1.1** — 2026-04-23 (later same day) — three surgical edits to the
  contract per James crispness pass on v0.1 first ~90 lines: (1)
  one-line definition added under the header for instant legibility;
  (2) asymmetry warning added as a load-bearing bullet — canonical
  inequality does NOT imply non-equivalence under partial quotienting,
  must be caught at call site; (3) generator-executability clause
  added to `G` — paper-group vs real-group must go into
  `declared_limitations`, not `G`; (4) failure behavior defined —
  `(failure, reason)` return required, best-effort-on-failure
  explicitly forbidden. No structural changes; only tightening.
- **v0.1** — 2026-04-23 — initial spec. Written after the 2026-04-23 tensor-decomposition pilot exposed canonicalization as a substrate-level (not gen_12-level) primitive. James directive: primitive status, narrow scope, explicit limitations mandatory, one instance active (`tensor_decomp@v1` with known insufficiency) and one pending (`tensor_decomp@v2`). Paired with `orbit_vs_representative.md` (the tensor-decomposition empirical anchor) and a v0.2 reframe of the gen_12 spec to depend on this primitive rather than embed it.
