# Orbit vs Representative — tensor-decomposition instance detail

**Status:** instance-specific spec, v0.2 (2026-04-23).
**Audience:** gen_12 implementers; anyone building a decomposition catalog.
**Role:** detail + empirical anchor for the `CANONICALIZER:tensor_decomp@v1` / `@v2` instances registered in the general canonicalizer primitive.
**General primitive:** `harmonia/memory/architecture/canonicalizer.md` (v0.1) — authoritative for the contract, hash rules, and declared-limitations requirement. This doc is the tensor-decomposition specific instance detail, including the 2026-04-23 empirical anchor that motivated the primitive's creation.
**Sibling docs:** `harmonia/memory/architecture/definition_dag.md`; `harmonia/memory/architecture/canonicalizer.md`.

---

*Repositioning note (v0.2, 2026-04-23 later same day):* v0.1 of this doc was written as a standalone substrate-primitive note. James's subsequent directive moved the general primitive into its own doc (`canonicalizer.md`) to avoid burying it inside tensor-specific machinery. This doc was retained as the tensor-decomposition instance detail and empirical anchor — the content below is unchanged from v0.1 and still accurate for its narrower role; only the framing at the top has been updated to point at the primitive.

---

## Why this exists

A 2026-04-23 pilot (`harmonia/tmp/tensor_pilot_2x2_matmul.py`) ran 20 random-init ALS seeds at rank 7 on the 2×2 matmul tensor over ℝ. Six seeds reached residual < 1e-8; four reached machine precision (< 1e-10). Theorem (Strassen 1969 + subsequent): every rank-7 decomposition of this tensor is related to Strassen's by the action of `(GL(2) × GL(2) × GL(2)) × S_7 × scale-gauge`. In other words, all 4+1 decompositions are the same mathematical object in five different coordinate frames.

A follow-up test (`canonicalize_test.py`) applied a v1 canonicalizer (scale gauge + sign convention + lexicographic permutation of rank-1 terms) to the four converged seeds and to Strassen's integer representative. All five hash to different canonical forms. None match. Integer-fractions: ALS seeds 0.02–0.16, Strassen 1.00.

**What this exposes:** the object we are searching over is not what we thought. We are searching a *cover* of the decomposition space. Without quotienting by the symmetry group, every downstream move — MAP-Elites cells, diversity metrics, "integer-ness" scores, catalog entries — reads coordinate artifacts instead of invariants.

**The reframe:** search is not the bottleneck; representation is. A substrate for discovering low-rank tensor identities is a substrate for recording and comparing **equivalence classes** of decompositions, not decompositions.

---

## The symmetry group (informally)

For a CP rank-r decomposition `T = Σ_i u_i ⊗ v_i ⊗ w_i` of a 3-tensor T with T_stabilizer Aut(T):

1. **Scaling gauge** — per rank-1 term: `(u_i, v_i, w_i) → (α u_i, β v_i, (αβ)^{-1} w_i)` for `(α, β) ∈ ℝ*²`. Two degrees of freedom per term; `r` terms total.
2. **Sign gauge** — special case of scaling; called out because sign conventions are integer-friendlier than continuous scales.
3. **Permutation of rank-1 terms** — `S_r` acting on column index `i`.
4. **T-stabilizer basis change** — the subgroup of `GL(n) × GL(n) × GL(n)` that fixes T. For 2×2 matmul, this is the simultaneous action `(P, Q, R) · T = (P ⊗ Q ⊗ R) T`, which preserves matmul up to basis conjugation; the stabilizer is non-trivial and contains a `GL(n)` isomorphic to the matmul-covariant action. For generic T, the stabilizer may be trivial; for tensors with structure, it is not.

The *orbit* of a decomposition is its equivalence class under (1)+(2)+(3)+(4). Two decompositions in the same orbit are the same mathematical object.

---

## Canonicalizer scope

### v1 (implemented 2026-04-23)

**Fixes:** scaling gauge (1), sign gauge (2), permutation (3).
**Ignores:** T-stabilizer basis change (4).

Implementation: normalize `‖u_i‖ = ‖v_i‖ = 1`, push magnitude into `w_i`; flip signs so the first non-negligible entry of each `u_i` and `v_i` is positive; lex-sort rank-1 terms by rounded concatenation `(u_i, v_i, w_i)`.

**Empirical verdict on v1:** insufficient. On 2×2 matmul rank 7, v1 produces four different hashes for four decompositions known to be in the same orbit. This confirms that item (4) — the T-stabilizer basis change — is where the orbit's "size" mostly lives for structured tensors.

### v2 (pending)

**Must additionally fix:** T-stabilizer basis change (4), at least probabilistically.

Candidate strategies, ordered by cost and generality:

- **Canonical basis via numerical invariants.** Compute multi-trace invariants (e.g., traces of products of slice matrices), singular-value spectra of mode unfoldings, or polynomial invariants known to be fixed by the group action. Advantage: fast, tensor-independent. Disadvantage: may not be complete — two genuinely distinct orbits can share invariants (like isospectral non-isomorphic graphs).
- **Canonical basis via SVD / Schur.** Compute an SVD of one factor matrix (say `A`) and use the right-singular basis as the canonical basis for mode-0; apply `A → A V_A` and propagate consistently through `(B, C)` using whatever T-preserving counterpart applies. Cheap when the action on modes is simple; T-specific.
- **Orbit-internal nearest-integer search.** Given a canonicalized-up-to-v1 decomposition, search within the `Aut(T)` orbit for the representative maximizing integer-proximity (or minimizing description length / sparsity). Advantage: directly produces Strassen-style representatives. Disadvantage: the *search* object in an ill-conditioned orbit; not a canonical form in the group-theoretic sense.
- **Full group enumeration.** Works for tensors where `Aut(T)` is small/finite; does not scale.

The MVP target for v2 is the weakest form sufficient to pass the calibration anchor below.

---

## Hash contract

A canonical-form hash `H(A, B, C) → bytes` must satisfy:

1. **Invariance.** `(A, B, C)` and `(A', B', C')` in the same orbit ⇒ `H(A, B, C) == H(A', B', C')`.
2. **Separation.** `(A, B, C)` and `(A', B', C')` in different orbits ⇒ `H(A, B, C) != H(A', B', C')` (with cryptographic probability; collisions under legitimate hashing are acceptable false-alarms).
3. **Tolerance.** Small numerical perturbation (ε ≤ 1e-8 in any entry) ⇒ same hash. Achieved via pinned-decimal rounding before hashing.
4. **Cheap.** `O(poly(n, r))` per decomposition.
5. **Versioned.** The hash carries a `canonicalizer_version` tag. v1 hashes and v2 hashes live in disjoint namespaces; never compare them directly.

A decomposition symbol `decomposition@vN` stores both its raw `(A, B, C)` (at double precision, for reproduction) AND its canonical hash under the project's current canonicalizer. Catalog dedup uses the hash; reproduction uses the raw factors.

---

## Calibration anchor

A canonicalizer passes ⇔ both of the following hold on the 2×2 matmul tensor at rank 7:

1. **Same-orbit collapse.** ≥ 10 ALS-converged rank-7 decompositions from independent random seeds hash to the same canonical form.
2. **Strassen recovery.** The canonical representative, when probed for nearest integer-structured form within its orbit (step 4 of the canonicalizer pipeline), matches Strassen's integer decomposition up to permutation and sign.

Secondary gates:
- Rank-6 decompositions (impossible by Winograd 1971) never produce a valid canonical hash; residual floor ≥ 1.0 is the regression test.
- Applying v1 canonicalizer to Strassen's integer decomposition and to ALS-converged seeds produces different hashes (current status, 2026-04-23) — tracked as the falsification anchor for the "v1 is insufficient" claim.

---

## Implication for gen_12

`docs/prompts/gen_12_tensor_identity_search.md` (v0.1 DRAFT, 2026-04-23 earlier same day) listed orbit equivalence as Gate 2 among four gates. That positioning was wrong. Orbit equivalence is the *central* primitive; every other piece of the generator is organized around it.

Revised positioning:

- The **object** of gen_12 is an orbit-equivalence class, not a decomposition.
- The **MAP-Elites cells** are cells in orbit space (sparsity, integer-ness, symmetry *of the canonical representative*), not of an arbitrary orbit element.
- The **catalog** stores one representative per orbit.
- The **search primitives** produce orbit points; the canonicalizer *always* runs before any cell insertion or catalog lookup.
- The **decomposition symbol** carries `(raw_factors, canonical_hash, canonicalizer_version)`.

Downstream objectives like "integer proximity" and "sparsity" are only meaningful *after* canonicalization (scale + permutation + basis). Running them on raw ALS output produces basis artifacts, which is precisely what the v1 empirical test showed.

---

## Version history

- **v0.1** — 2026-04-23 — initial note, grounded in the 2×2 matmul pilot + canonicalizer v1 multi-seed hash collision test. Falsification-first: the note was written *after* the empirical check showed v1 insufficient, not before. Calibration anchor defined before any v2 strategy was picked. Pairs with a reframed gen_12 spec and a reframed stoa/ideas doc.
