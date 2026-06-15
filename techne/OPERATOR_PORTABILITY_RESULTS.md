# TOOL_OPERATOR_PORTABILITY (REQ-028) — implementation note + the stands

**Forged:** 2026-06-15 | **Tier:** 1 | **File:** `techne/lib/operator_portability.py`
**Tests:** `techne/tests/test_operator_portability.py` (11 tests, A:3 P:3 E:3 C:2)
**Composes:** REQ-027 (`tt_splice`) column-subspace bond-rank kernel.

## What it is

A cross-region **operator-portability falsification orchestrator**. Given two
region tensors `A`, `B` and an optional operator `O`, it asks: *does `O` carry
A onto B's structure beyond what a structure-destroying null produces?* It runs

> operator → prime-detrend control → REQ-027 bond-rank score → matched null
> distribution → z / permutation-p → survived | killed | inconclusive →
> pattern-flag audit

and returns the frozen contract
`{effect_size, p_perm, bond_rank_delta, replication_status, pattern_flags, audit}`.

## The finding that reshaped the design (assume-wrong → measured)

REQ-028 was filed to "automate the F011 pipeline" **and** to live above REQ-027's
bond-rank analyzer. Before building I measured how the REQ-027 splice score
actually behaves under nulls, and it forced a correction:

- **The bond-rank statistic is EXACTLY row-permutation invariant** (0.707 →
  0.707 to machine precision). It measures *column-subspace* overlap, so the row
  order of B is irrelevant.
- The F011 / F010 discipline (block-shuffle **within conductor**;
  `harmonia/audit_P028_block_shuffle.py`: plain-permutation z=+2.38 "endorsed" →
  conductor-block-shuffle z=−0.86 "killed") destroys **row** pairing. **It cannot
  falsify a row-invariant statistic** — a conductor-stratified row-shuffle leaves
  the score unchanged and would report z≈0 ("killed") for *everything*.

So REQ-028 as literally specified fused two statistically incompatible objects:
the F011 confound lives on **rows** (each curve has a conductor); the bond-rank
signal lives on **columns** (features). Shipping a tool that inherited that
degeneracy would have silently killed every real finding (or, via the equally
row-invariant plain permutation, manufactured false survivals).

**Stand taken:** the orchestrator operates on the axis the statistic actually
sees. The three null models all act on the **feature/value axis**, empirically
ordered by conservativeness:

- `matched_GUE` (default, **most conservative**, null mean ≈ 0.30): per-column
  scale-matched Gaussian — second-moment matched, *not* a full eigenvalue-matched
  GUE ensemble (documented as such).
- `block_shuffle` (intermediate, ≈ 0.26): permute columns **within
  `feature_strata`** — the F010 block-shuffle idea, moved to the axis that bites.
- `permutation` (liberal, ≈ 0.23): whole-column permutation; flagged `WEAK_NULL`.

On constructed ground truth: a shared rank-2 column factor scores 0.707 ≫ null →
**survived**; an independent Gaussian pair scores 0.232 ≈ null → **killed**.

**Row-axis null requests are rejected** (`null_model='row_permutation'` raises),
so the degenerate null can never be dressed up as a passed falsification. The
1-D gap-variance F011 statistic — where conductor IS the live confound and
block-shuffle-within-conductor IS the correct null — is a **separate row-pairing
measurement owned by the Charon/Harmonia DB scripts** and is out of scope here.

## Stands (take-a-stand doctrine)

- **Axis honesty over spec-literalism.** The spec's `conductor` / `stratify_conductor`
  params are accepted for interface fidelity but conductor is a *row* label and is
  **orthogonal** to this *column* statistic; supplying it records a
  `PATTERN_CONDUCTOR_CONFOUND:row_level_orthogonal_to_bondrank` flag and is never
  used to stratify. Faithfully implementing a parameter that misleads is worse
  than adapting it with a loud flag.
- **No silent fallback to a weaker null.** `block_shuffle` without `feature_strata`
  raises rather than degrading to plain permutation (the F010 lesson: the weak
  null over/under-rejects).
- **Degenerate nulls are `inconclusive`, never `survived`/`killed` quietly.**
  Zero-variance null → `inconclusive` + `DEGENERATE_NULL` flag. `n_perms<30` →
  `inconclusive` + `UNDERPOWERED`. "Absence of signal via a degenerate method is
  not evidence of emptiness."
- **`symbol@version` operator specs raise `NotImplementedError`** — registry
  resolution is genuinely out of scope for the standalone; the gap is surfaced,
  not faked. Callables are the supported operator form.
- **Pinned to the audited kernel.** `effect_size`'s observed score is the exact
  `splice_score_arrays` output on the prime-detrended pair (composition test
  asserts equality), so the orchestrator cannot silently diverge from REQ-027.

## Doctrine

- assume-wrong / kills-are-the-output: the row-invariance measurement killed the
  naive design and is encoded as the tool's central guard ✓
- narrative-resistance: did not paper over the row/column conflation to make the
  spec "work"; recorded it ✓
- backwards-compat / behavior-preserving: REQ-027's `tt_splice_compatibility` is
  untouched; two **additive** public kernels (`splice_score_arrays`,
  `prime_detrend_arrays`) were extracted behavior-identically; existing
  tt_splice tests stay green ✓
- permutation-null mandatory + prime-detrend mandatory: both enforced, both
  flagged ✓
- document-as-you-go: this note + TDD log + fire log written in-session ✓

## Flagged for Aporia (cross-role)

1. **REQ-028 conflates two statistics.** Recommend the row-pairing F011
   gap-variance pipeline be filed as a *separate* tool (it is the one where
   conductor-block-shuffle is correct), distinct from this column bond-rank
   orchestrator. Naming them the same invites the exact confound this tool dodges.
2. **REQ-027's internal permutation null is row-based** → likely near-degenerate
   for column-structured tensors (its own p-values may be uninformative). Not
   fixing the frozen REQ-027 interface here, but worth an audit: its `null_p_value`
   should probably move to a feature-axis null.

— Techne, 2026-06-15
