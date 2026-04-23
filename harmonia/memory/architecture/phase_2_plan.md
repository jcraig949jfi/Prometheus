# Phase 2 plan — canonicalizer architecture + first instances

**Author:** Harmonia_M2_sessionA, 2026-04-23
**Status:** plan, v0.1. Driven by James's 2026-04-23 reviewer pass on the v0.1 whitepaper.
**Spirit:** experiment. Ship, learn from what breaks, iterate. Failure is data, not cost.

---

## Thesis

Phase 1 established the canonicalizer as a first-class substrate primitive with one active instance (`tensor_decomp@v1`) carrying a declared insufficiency, and one pending (`tensor_decomp@v2`). The v0.1 whitepaper compiled the argument.

The reviewer's strongest observation: the primitive as currently framed conflates two distinct operations — *canonical identity* (deterministic quotient under a declared group) and *preferred representative* (optimization for some secondary property within an already-identified orbit). Without an explicit split, future instances will drift.

Phase 2's primary move is to split the primitive's contract into two types, ship the first instances under each type, add the first non-tensor instance, and name the cross-cutting discipline formally. Downstream consumers (gen_12, DAG, zoo, Pattern 30) then compose against a clean two-type registry.

---

## Workstreams

### W1 — canonicalizer.md v0.2: Type A / Type B split + reviewer rigor edits

**Changes:**
- Split the primitive into Type A (canonical identity) and Type B (preferred representative). Each instance declares its type.
- Tighten theorem language on "all rank-7 decompositions form a single orbit" — replace with operational wording about the pilot's specific seeds.
- Strengthen failure semantics: failure must be *stable under tolerance*, not just returned.
- Move SHA-256 + decimal-precision choices to an implementation note; contract specifies deterministic serialization + namespaced versioning + tolerance pinning, not the hash primitive.
- Clarify Pattern 30 integration: algebraic rearrangement is a *separate instance* of the same contract, not a second-name for the tensor canonicalizer.
- Add rank-6 residual normalization caveat.
- Define "orbit discipline" formally as a coined term.
- Tighten v1-retained-despite-anchor-failure justification (only admissible because failure is declared + reproducible + used as regression target).

**Exit:** canonicalizer.md v0.2 pushed.

### W2 — `tensor_decomp_identity@v2`: Type A instance for 2×2 matmul

**Strategy:** multi-invariant canonical-form derivation. After v1 canonicalization (scale + sign + permutation), compute basis-independent numerical invariants of the `(A, B, C)` triple — singular-value spectra of each factor, eigenvalue spectra of Gramians `A^T A`, pairwise slice-interaction invariants, and multi-trace invariants of tensor unfoldings. Hash the sorted concatenation of those invariants. The claim this primitive tests: invariants are sufficient to collapse the `(GL(2)³ × S_7 × scale-gauge)` orbit to a single hash.

**Calibration:** the four machine-precision ALS seeds from the 2×2 pilot + Strassen's integer representative. Pass condition: all five hash identically.

**Known risk:** GL-invariants are harder than orthogonal-invariants. The strategy may fail to collapse the full orbit (two orbits with identical invariants collide; OR basis-dependent inputs produce different hashes for the same orbit). Either is data.

**Exit:** v2 canonicalizer implemented + tested on pilot data + result documented honestly (passes or falsifies the strategy).

### W3 — `tensor_decomp_integer_rep@v1`: Type B instance

**Strategy:** takes a v2-canonicalized orbit (Type A output, a canonical representative + hash), searches the `GL(2)³` stabilizer for the orbit member minimizing `1 - integer_fraction` (equivalently: maximizing fraction of near-integer entries). Output is the *preferred* representative, not a canonical one — uniqueness is NOT guaranteed, ties are possible, perturbations may flip which representative wins.

**Calibration:** given any of the 4 ALS seeds as input, after v2 identity canonicalization, recover something close to Strassen's integer decomposition (integer-fraction > 0.9).

**Known risk:** the orbit-internal search may have many local optima; may not converge to Strassen reliably. This is the correct failure mode for a Type B (it's an optimization, not a quotient). Declared in the Type B contract.

**Exit:** integer_rep@v1 implemented + tested + result documented (recovers Strassen reliably, sometimes, or never).

### W4 — `poly_monomial_form@v1`: first non-tensor Type A instance

**Strategy:** polynomials `p(x_1, ..., x_n)` up to variable relabeling and sign gauge. Canonical form:
1. Enumerate monomials with non-zero coefficients.
2. Choose a canonical variable ordering: for each variable, compute a signature (sum of absolute coefficients of monomials containing it, weighted by monomial degree). Sort variables by signature (tie-breaking by index if signatures tie).
3. Normalize sign: force leading coefficient to be positive; flip signs of all odd-powered terms if needed to canonicalize sign.
4. Lex-sort monomials under the canonical variable ordering.

**Calibration:**
- Same-class: `x² − 1` and `y² − 1` hash identically (variable-relabeling equivalence).
- Same-class: `-(x² − 1)` and `x² − 1` hash identically under sign gauge.
- Different-class: `x² − 1` and `x² + 1` hash differently (not equivalent).
- Different-class: `x² + y` and `x + y²` hash differently (non-symmetric variable usage).

**Known risk:** variable-signature approach can have signature ties that are hard to break canonically; worst case falls back to enumeration (brute-force S_n orbit).

**Exit:** poly_monomial_form implemented + 4 calibration anchors tested + passes or falsifies.

### W5 — Pattern 31: "Orbit Discipline"

**Recognition:** before claiming any structural novelty in a substrate object, the claim must be made modulo a *declared symmetry group*. Silent identity claims on raw representations are the decomposition-level manifestation of Pattern 1 (Distribution/Identity Trap).

**Anchor cases:**
1. F043 retraction (2026-04-19): correlation measured on algebraically-coupled variables; the "correlation" was a rearrangement of the BSD identity. Orbit discipline would have required declaring the algebraic equivalence group and checking the correlation is modulo it — Pattern 30 graded severity is the specific operationalization.
2. 2026-04-23 2×2 matmul pilot: four ALS decompositions in one GL(2)³ orbit hashed to four different canonical forms under naive scale+sign+permutation canonicalization. The finding required lifting to orbit-level identity.

**Discipline:**
- Declare the symmetry group before claiming novelty.
- Use a canonicalizer instance whose declared equivalence group includes (at minimum) the subgroup relevant to the claim.
- Treat un-declared group action as a declared limitation, not a silent gap.

**Exit:** Pattern 31 added to `pattern_library.md` with DRAFT tier (2 anchor cases; promotion to FULL when a third accumulates).

### W6 (OUT OF SCOPE this session) — whitepaper v2

Revise the whitepaper after W1-W5 ship. Incorporate:
- Type A / Type B split.
- Tightened theorem language on the orbit claim.
- Hash moved to implementation note.
- Pattern 30 boundary clarified.
- "Orbit discipline" defined in terms of Pattern 31.
- Section reorder (contract → primitive placement).
- Abstract trimmed ~20%.

W6 is deliberately deferred: revising the whitepaper before the substantive Phase 2 work exists to document would be reward-signal capture (polishing an artifact before there's substance to document).

### W7 (OUT OF SCOPE this session) — 3×3 Laderman scaling test

If W2's strategy passes on 2×2 matmul, test whether the same strategy collapses rank-23 Laderman decompositions of 3×3 matmul to a single orbit hash. This determines whether v2 is 2×2-specific or generalizes. Scaling test is out of scope this session because it depends on W2 succeeding AND on a working Laderman reference implementation (~45 minutes of additional setup).

---

## Critical path

```
W1 (canonicalizer v0.2)
  ├── W2 (tensor_decomp_identity@v2)
  │    └── W3 (tensor_decomp_integer_rep@v1)
  ├── W4 (poly_monomial_form@v1)    [independent]
  └── W5 (Pattern 31)                [independent]
```

W1 gates everything structurally. W4 and W5 are independent of the tensor work and can run in parallel. W2 gates W3 (Type B composes on Type A).

## Exit criteria

**MVP:** W1 + W4 + W5 shipped + W2 attempted (pass or falsify documented honestly).
**Strong ship:** MVP + W3 shipped with calibration result documented.
**Full Phase 2:** MVP + W3 + W6 (whitepaper v2). W6 explicitly not this session.

## Discipline for the experiment

- **Log failures as data.** If W2's multi-invariant strategy fails to collapse the orbit, the failure + diagnosis is the deliverable. Phase 2 ships the honest outcome, not a manufactured success.
- **Don't polish the whitepaper.** W6 waits until the substance exists.
- **Test everything against calibration anchors.** Every instance's calibration anchors run before the instance lands in the registry.
- **Commit in workstream order.** Each W-commit names the workstream + the finding (pass/fail). No "mega commit" that hides failure modes inside success claims.
- **Don't hide "didn't work."** Per James's 2026-04-23 direction: learn by trying. An instance that fails its calibration is still a ship — it adds a data point about which strategies don't work, and documents the falsification in its MD.

## What Phase 2 is NOT

- Not a proof that canonicalizers work for all of mathematics. It's empirical validation on two domains (tensor decomposition + polynomial forms).
- Not a guarantee that v2 passes. The strategy is a hypothesis; the calibration test is the falsification instrument.
- Not coupled to publication. Experiment discipline, not paper discipline.

---

## Status log

- **2026-04-23 (Phase 2 MVP first pass):** W1 + W4 + W5 shipped; W2 + W3 falsified with honest documentation.
- **2026-04-23 (Phase 2 second pass):** W2 **SHIPPED** after third-strategy success. The minimal `(inv1, inv2)` pair of GL(2)³-invariants passes all three calibration anchors (same-class 4/4 + GL invariance 10/10 + rank-7 vs rank-8 separation). Implementation at `agora/canonicalizer/tensor_decomp_identity_v2.py`. W3 remains at PARTIAL (GL(2)³ local search improves integer_fraction from 0-0.131 → 0.19-0.29 but does not reach Strassen's 1.0); stronger search primitives (integer enumeration, L-BFGS with integer penalty) deferred.
- **Out of scope this session (unchanged):** W6 whitepaper v2 revision, W7 3×3 Laderman scaling test.

## Version history

- **v0.1** — 2026-04-23 — initial plan drafted after the whitepaper reviewer pass. Shape: Type A/B split as primary architectural move; three first-instance implementations (tensor identity, tensor integer rep, polynomial); one discipline pattern (Orbit Discipline / Pattern 31). W6 (whitepaper v2) and W7 (3×3 scaling) explicitly deferred.
