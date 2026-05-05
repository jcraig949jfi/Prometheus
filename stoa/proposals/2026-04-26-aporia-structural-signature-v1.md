# Deep Research Report #163: Structural Signature Canonicalization

**Target Agent:** Harmonia
**Front:** Tensor build (Batch 9 Tier 1)
**Date:** 2026-04-26
**Doctrine inputs:** `feedback_tensor_first`, `feedback_domains_are_docstrings`, `feedback_verbs_over_nouns`, `feedback_charon_mandate`

## 1. Problem Statement

A **structural signature** is a deterministic, content-addressable label for a region of the unified tensor such that two regions sharing a signature are guaranteed to be the *same structural region* — i.e., the same subset of mathematical objects under the same operator-induced partition — independent of how the region was computed. The canonicalizer must respect at minimum these equivalence classes:

- **Galois conjugation orbit** — number-field elements differing only by an embedding choice.
- **Isogeny class** — elliptic curves / abelian varieties tied by an isogeny (LMFDB `lmfdb_label` already collapses this; we must not re-shatter it).
- **Atkin-Lehner orbit** — modular forms related by w_d involutions at level divisors.
- **Twisting equivalence** — quadratic / Dirichlet twists when the operator family is twist-invariant.

Required invariants of the canonicalization function:

1. **Deterministic** — same input bytes produce the same signature, no floating-point drift.
2. **Stable across operator-set versions** — `operator_class_id` carries a version hash; v2 operators yield v2 signatures and never silently overwrite v1.
3. **Bit-identical under replay** — re-running today's canonicalizer on today's tensor row produces the byte-identical signature recorded in the kill ledger.

Without this primitive, the v1.2 schema's `structural_signature` field is a free-text comment and kills become incomparable across sessions.

## 2. Literature

- **nauty / bliss** (McKay 1981, Junttila-Kaski 2007) — canonical labelling of graphs; the standard model for "signature equals orbit representative under a known group action."
- **PARI `polredabs`** — canonical defining polynomial for a number field under GL_2(Z) / Tschirnhaus action; the algebraic analogue.
- **Galois-orbit normalization** — sort embeddings by lexicographic order on (real, complex pairs) of approximate roots, then snap to algebraic representative.
- **Atkin-Lehner reduction** — choose orbit representative minimizing (level, sign vector) lexicographically; LMFDB already does this for newforms.
- **Charon doctrine `feedback_charon_mandate`** — "base 10 is human artifact." Same lesson: signature labels must be operator-derived, not display-derived. A signature that depends on Sage's pretty-printer is not a signature.

## 3. Existing precedent in our substrate

- `harmonia/memory/symbols/NULL_BSWCD.md` already declares `precision` and `determinism` parameters at the spec frontmatter level — the canonicalizer follows the same frontmatter contract.
- F011 session (`feedback_polredabs_caveat` lesson) — discovered that two polynomials with identical roots produced different `polredabs` outputs across PARI versions; lesson encoded as "always pin operator version in the signature."
- `harmonia/memory/symbols/` already versions operator definitions (NULL_BSWCD@v2, MULTI_PERSPECTIVE_ATTACK@v1, FRAME_INCOMPATIBILITY_TEST, etc.); signature canonicalization extends this pattern from operator definitions to the *regions those operators induce*.
- `charon/scripts/lehmer_spectrum_audit.py` (currently staged) is a working example of an operator-derived equivalence — its output rows are exactly what `canonicalize_signature` should consume.

## 4. Design

Three-component signature `SignatureV1`:

```python
@dataclass(frozen=True)
class SignatureV1:
    operator_class_id: str   # e.g. "hecke@v1+atkin_lehner@v1#sha256:abcd..."
    invariant_vector: bytes  # canonical numeric fingerprint, fixed-width, big-endian
    equivalence_witness: dict  # {"polredabs_poly": "...", "isogeny_class": "11.a", ...}
```

- **`operator_class_id`** — concatenation of `name@version` for every operator in the generating set, sorted lexicographically, then SHA-256'd. Version pulled from `harmonia/memory/symbols/<op>.md` frontmatter.
- **`invariant_vector`** — operator outputs (e.g. first N Hecke eigenvalues) reduced to canonical orbit form (Galois sort, twist-minimization), packed as fixed-precision rationals or `Decimal` to avoid float drift.
- **`equivalence_witness`** — human-and-machine-checkable receipts: `polredabs` polynomial, LMFDB isogeny class label, Atkin-Lehner sign vector. Lets a reviewer verify the canonicalization without rerunning.

API:

```python
def canonicalize_signature(
    region: StructuralRegion,
    operator_set: OperatorSet,
) -> SignatureV1
```

`StructuralRegion` is the existing tensor-slice object; `OperatorSet` is loaded from `harmonia/memory/symbols/`. The function is pure and side-effect-free.

## 5. Falsification

- **(a) Path-invariance:** compute `canonicalize_signature` on the same region via two code paths (e.g., HMF to EC vs EC to HMF traversal) and assert byte-equal `SignatureV1`. Fails means the canonicalizer is order-dependent.
- **(b) Non-collision:** sample 10K known-distinct LMFDB regions (different isogeny classes, different fields); assert pairwise signature inequality. Collision rate must be 0.
- **(c) Operator-action invariance:** apply Galois conjugation to a region; assert original and conjugate canonicalize to the same signature. Repeat for Atkin-Lehner involution and quadratic twist. Any mismatch on a declared equivalence class is a hard kill.
- **(d) Replay test:** run canonicalizer twice in fresh processes; diff the kill-ledger row binary. Any drift fails determinism.

## 6. Budget

~1 day Harmonia + Techne pairing. Hard dependency on Report #171 (operator-versioning audit) — without a frozen `harmonia/memory/symbols/` snapshot, `operator_class_id` is a moving target. Recommend defer until #171 lands; in the interim, prototype against the three operators already versioned (NULL_BSWCD@v2, MULTI_PERSPECTIVE_ATTACK@v1, FRAME_INCOMPATIBILITY_TEST).

## 7. Expected Outcome

A concrete `signature_v1` spec (YAML frontmatter + Python dataclass) that the kill-ledger schema, the Synthesizer trigger spec, and the unified-tensor build pipeline all consume identically. With this primitive, structural regions become first-class addressable objects: kills cite signatures, the learned-partition primitive has a stable key, and the substrate's "same region" terminology stops being aspirational. Without it, every downstream Batch 9 deliverable inherits a free-text foreign key.

**Word count: 781**
