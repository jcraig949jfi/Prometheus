# CANONICALIZER — substrate primitive

**Status:** substrate-primitive spec, v0.1 (2026-04-23).
**Architectural slot:** first-class primitive, alongside the symbol registry, the tensor, Definition DAG, and signals.specimens. Not a generator.
**Audience:** gen_12 (tensor decomposition), gen_11 (coordinate invention), Definition DAG authors, symbol-registry curators, any module that dedup's structured objects.

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
(name, equivalence_group G, procedure C, hash H,
 declared_limitations, calibration_anchors, canonicalizer_version)
```

where:

- `G` is the equivalence group the instance quotients, specified as a list of generator types (e.g., `scale_gauge`, `sign_gauge`, `permutation(S_r)`, `T_stabilizer_GL_n^3`).
- `C : Representation → CanonicalRepresentative` is a deterministic map satisfying, for all `x, y` in the representation space:
  - **Invariance.** `x ~_G y ⟹ C(x) = C(y)`.
  - **Separation (probabilistic).** `x ~_G y is false ⟹ C(x) ≠ C(y)` with probability close to 1. Collisions are permitted; instance must declare the collision model.
  - **Tolerance.** For numerical representations, `‖x − y‖ < ε_tol ⟹ C(x) = C(y)` via pinned rounding before hashing.
  - **Complexity.** `C` runs in `O(poly(|x|))`.
- `H : CanonicalRepresentative → bytes` is a hash function. Different canonicalizer instances live in disjoint hash namespaces (namespaced by `(name, canonicalizer_version)`).
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

### Active: `CANONICALIZER:tensor_decomp@v1`

- **Equivalence group:** `scale_gauge × sign_gauge × permutation(S_r)`. Applies to CP-rank-r decompositions of order-3 tensors.
- **Procedure:** normalize `‖u_i‖ = ‖v_i‖ = 1`, absorb magnitude into `w_i`; canonical sign (first entry above tolerance of each `u_i, v_i` is positive, partner sign absorbed); lex-sort rank-1 terms by rounded concatenated `(u_i, v_i, w_i)`.
- **Hash:** SHA-256 of pinned-decimal (default 4) rounded concatenation of canonical `(A, B, C)`.
- **Declared limitations:**
  - `T_stabilizer_basis_change` (total). For structured target tensors (matmul, Pfaffian, etc.) this is where most of the orbit's size lives. Consumers must NOT treat same-hash-under-v1 as same-orbit-under-full-symmetry-group.
- **Calibration anchors:**
  - Same-class: pending (requires v2 — v1 fails by construction on the Strassen anchor; see `orbit_vs_representative.md`).
  - Different-class: rank-7 Strassen hash ≠ rank-8 naive decomposition hash. (Trivially holds.)
- **Empirical anchor:** 2026-04-23, `harmonia/tmp/canonicalize_test.py`. 4 ALS-converged rank-7 seeds on 2×2 matmul → 4 distinct v1 hashes; none match Strassen's v1 hash. v1 is *known* to be insufficient for the tensor-decomposition problem as stated; it is retained in the registry as the first declared limitation's calibration target.

### Pending: `CANONICALIZER:tensor_decomp@v2`

- **Equivalence group:** v1 group plus `T_stabilizer_basis_change` (tensor-dependent; for 2×2 matmul, the matmul-covariant GL(2) action on factor spaces).
- **Procedure:** open — candidate strategies tracked in `orbit_vs_representative.md` §"v2 strategies."
- **Calibration target:** same-class anchor passes on the four 2×2 ALS-converged seeds; canonical rep recovers Strassen under a nearest-integer orbit-internal probe.
- **Exit criterion:** calibration passes on 2×2, then the strategy is attempted at 3×3 (rank 23 Laderman) — the scaling test determines whether v2 is a first-class instance or a 2×2-only special case.

### Future instances (not yet scoped)

- `CANONICALIZER:poly_monomial_form@v1` — polynomials up to variable relabeling and sign gauge. Anchor: lexicographic monomial ordering + variable ordering by first-nonzero.
- `CANONICALIZER:graph_iso@v1` — graph isomorphism canonical form. Anchor: nauty / Bliss-style partition refinement. Note: this is graph-canonical-form in the classical sense; inclusion is only worthwhile if a substrate consumer needs it.
- `CANONICALIZER:pattern_30_rearrangement@v1` — the Pattern-30 REARRANGEMENT severity already asks "is Y an algebraic rearrangement of X?" Phrased as a canonicalizer, this would produce a canonical form for the BSD-ingredient family (or more generally, a ring of definitional terms) such that two expressions related by ring identities hash the same.
- `CANONICALIZER:dag_node_identity@v1` — Definition DAG node identity under basis change on the input-atoms.

Each future instance, when claimed, follows the same contract (equivalence group + procedure + hash + declared limitations + calibration anchors).

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

- **v0.1** — 2026-04-23 — initial spec. Written after the 2026-04-23 tensor-decomposition pilot exposed canonicalization as a substrate-level (not gen_12-level) primitive. James directive: primitive status, narrow scope, explicit limitations mandatory, one instance active (`tensor_decomp@v1` with known insufficiency) and one pending (`tensor_decomp@v2`). Paired with `orbit_vs_representative.md` (the tensor-decomposition empirical anchor) and a v0.2 reframe of the gen_12 spec to depend on this primitive rather than embed it.
