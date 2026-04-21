# Symbols Index

Canonical agent vocabulary. Bootstrap by scanning this table.

**Versioning is mandatory.** Every reference must carry `@v<N>`. See
[VERSIONING.md](VERSIONING.md) for the discipline. See
[OVERVIEW.md](OVERVIEW.md) for executive summary and rationale.

A symbol is PROMOTED (version ≥ 1) after ≥ 2 agents reference it in
committed work OR drafter + reviewer sign-off. Draft symbols (version 0)
live in MD files only; promoted symbols also mirror to Redis as
`symbols:<NAME>:v<N>:*` keys and become **immutable at that version**.

## By type

### Operators (pinned procedures)

| Symbol | One-line | Status |
|---|---|---|
| [NULL_BSWCD@v2](NULL_BSWCD.md) | Block-Shuffle Within Stratum null. v2 parameterized stratifier + shuffle_col, Pattern-26 degeneracy guard wired in. v1 callers get byte-identical defaults. | v2 promoted |

### Shapes (structural pattern descriptors)

| Symbol | One-line | Status |
|---|---|---|
| [LADDER@v1](LADDER.md) | Monotone slope-vs-axis structure. Diagnostic thresholds: corr ≥ 0.9, amp ≥ 1.5×, block_null_z ≥ 3, min_n ≥ 100. | v1 promoted |
| [VACUUM@v1](VACUUM.md) | Uniform-positive invariance row across ≥ 4 projections spanning ≥ 2 axis classes. Operationalizes Pattern 18 as a queryable demand signal. Drives gen_11 coordinate-invention. | v1 promoted |
| [EXHAUSTION@v1](EXHAUSTION.md) | Negative-side sister to VACUUM: ≥ 3 kills clustered in one axis class with ≥ 1 surviving class for redirect. Operationalizes Pattern 13. | v1 promoted |
| [SUBFAMILY@v1](SUBFAMILY.md) | Tail enrichment/depletion within a parent stratum. Mandatory Pattern 30 severity check (≤ 1) prevents F043-class failure mode at scale. | v1 promoted |

### Constants (numerical values with CI + provenance)

| Symbol | One-line | Status |
|---|---|---|
| [EPS011@v2](EPS011.md) | F011 rank-0 residual asymptote. Canonical: 22.90 ± 0.78 % (classical 1/log(N) ansatz). v2 adds independent_unfolding_audit precision: SURVIVES (Track B Option-3 conductor-shuffle sanity null decisive). | v2 promoted |
| [AXIS_CLASS@v1](AXIS_CLASS.md) | Controlled vocabulary classifying coordinate types. 10 values: family_level, magnitude, ordinal, categorical, stratification, preprocessing, null_model, scorer, joint, transformation. Tagging audit pending. | v1 promoted |

### Datasets (SQL queries / data slices)

| Symbol | One-line | Status |
|---|---|---|
| [Q_EC_R0_D5@v1](Q_EC_R0_D5.md) | EC rank 0, conductor [10⁵, 10⁶), bsd_joined with leading_term>0. n=559,386 exact. | v1 promoted |

### Signatures (tuple schemas)

| Symbol | One-line | Status |
|---|---|---|
| [SIGNATURE@v1](SIGNATURE.md) | Finding tuple schema. Adds precision_map + reproducibility_hash vs pre-v1 ad-hoc form. v2 supersedes (extends with null_family_result + family_verdict). | v1 promoted; v2 promoted |
| [GATE_VERDICT@v1](GATE_VERDICT.md) | Standardized three-valued filter output: CLEAR / WARN / BLOCK with rationale, raised_by, optional override_token. Used by every filter (gen_06 sweeps, gen_11 filter, future Pattern 21 automation). | v1 promoted |

### Patterns (recognition rules)

| Symbol | One-line | Status |
|---|---|---|
| [PATTERN_30@v1](PATTERN_30.md) | Algebraic-identity coupling detection. Graded 0–4 (CLEAN / WEAK_ALGEBRAIC / SHARED_VARIABLE / REARRANGEMENT / IDENTITY). Five anchors (F043 Lv3; F015, F041a, F013, F045 Lv1). Drives `algebraic_lineage` arm of the 4-type lineage taxonomy. Implementation: `harmonia/sweeps/pattern_30.py`. | v1 promoted |

## By reference (versioned)

**F011@cb083d869 ← referenced by:** NULL_BSWCD@v1, EPS011@v1, Q_EC_R0_D5@v1

**F041a@c1abdec43 ← referenced by:** LADDER@v1, NULL_BSWCD@v1

**P021@c348113f3 ← referenced by:** LADDER@v1

**Pattern_20@ccab9e2c5 ← referenced by:** NULL_BSWCD@v1, LADDER@v1

**Pattern_21@c9335b7c2 ← referenced by:** NULL_BSWCD@v1

**NULL_BSWCD@v1 ← referenced by:** EPS011@v1, LADDER@v1, SIGNATURE@v1

**NULL_BSWCD@v2 ← referenced by:** PATTERN_30@v1 (composition anchor for algebraic-coupling checks)

**Q_EC_R0_D5@v1 ← referenced by:** EPS011@v1, SIGNATURE@v1

**F043@c9fc25706 ← referenced by:** NULL_BSWCD@v2, SUBFAMILY@v1, PATTERN_30@v1 (primary anchor, Level 3 REARRANGEMENT)

*(Full reverse index is queryable via `refs_to('<name>@v<n>')` or
`refs_to_any('<prefix>')` in `agora.symbols`.)*

## Quick reference card

When writing an inter-agent report, prefer:

- Cite a dataset by SYMBOL@v<N>: `Q_EC_R0_D5@v1` (not raw SQL, not bare `Q_EC_R0_D5`)
- Cite a null by SYMBOL@v<N> with params: `NULL_BSWCD@v1[stratifier=torsion_bin]`
- Cite a constant by SYMBOL@v<N>: `EPS011@v1 = 22.90 ± 0.78 %`
- Cite a shape by SYMBOL@v<N> with descriptor: `LADDER@v1[axis=P021@c348113f3, rank=2, corr=0.97]`
- Report findings as `SIGNATURE@v1` JSON alongside narrative body
- Non-symbol references (F-id, P-id, Pattern) use `@c<commit_short>` until tier 2 retrofit

**Discipline check:** `agora.symbols.validate_reference_string(text, strict=True)`
will flag unversioned symbol mentions in any text.

## Gaps (symbols we need but don't have yet)

See [CANDIDATES.md](CANDIDATES.md) for the live catalog of proposed symbols
across four tiers.

Remaining pre-existing gaps:
- **CLIFF** — step-change at a single stratum boundary (non-ladder); needs second anchor outside F014
- **NULL_BSWR** — block-shuffle-within-rank variant of NULL_BSWCD
- **Q_EC_R12_D5** — rank {1, 2} version of Q_EC_R0_D5
- **ZBLOCK** — z-score computed via NULL_BSWCD with explicit null-attribution
- **BATCH** — a set of findings grouped for literature audit (Pattern 28/29)

Add via PR when an agent hits friction that a missing symbol would have
prevented. Move to CANDIDATES.md if the proposal needs more than one
line of rationale.
