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
| [NULL_BSWCD@v1](NULL_BSWCD.md) | Block-Shuffle Within Conductor Decile null. Defaults: n_bins=10, n_perms=300, seed=20260417. | v1 promoted |

### Shapes (structural pattern descriptors)

| Symbol | One-line | Status |
|---|---|---|
| [LADDER@v1](LADDER.md) | Monotone slope-vs-axis structure. Diagnostic thresholds: corr ≥ 0.9, amp ≥ 1.5×, block_null_z ≥ 3, min_n ≥ 100. | v1 promoted |

### Constants (numerical values with CI + provenance)

| Symbol | One-line | Status |
|---|---|---|
| [EPS011@v1](EPS011.md) | F011 rank-0 residual asymptote. Canonical: 22.90 ± 0.78 % (classical 1/log(N) ansatz). | v1 promoted |

### Datasets (SQL queries / data slices)

| Symbol | One-line | Status |
|---|---|---|
| [Q_EC_R0_D5@v1](Q_EC_R0_D5.md) | EC rank 0, conductor [10⁵, 10⁶), bsd_joined with leading_term>0. n=559,386 exact. | v1 promoted |

### Signatures (tuple schemas)

| Symbol | One-line | Status |
|---|---|---|
| [SIGNATURE@v1](SIGNATURE.md) | Finding tuple schema. Adds precision_map + reproducibility_hash vs pre-v1 ad-hoc form. | v1 promoted |

## By reference (versioned)

**F011@cb083d869 ← referenced by:** NULL_BSWCD@v1, EPS011@v1, Q_EC_R0_D5@v1

**F041a@c1abdec43 ← referenced by:** LADDER@v1, NULL_BSWCD@v1

**P021@c348113f3 ← referenced by:** LADDER@v1

**Pattern_20@ccab9e2c5 ← referenced by:** NULL_BSWCD@v1, LADDER@v1

**Pattern_21@c9335b7c2 ← referenced by:** NULL_BSWCD@v1

**NULL_BSWCD@v1 ← referenced by:** EPS011@v1, LADDER@v1, SIGNATURE@v1

**Q_EC_R0_D5@v1 ← referenced by:** EPS011@v1, SIGNATURE@v1

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

- **CLIFF** — step-change at a single stratum boundary (non-ladder)
- **SUBFAMILY** — tail enrichment/depletion signature (anchor: T4 / F042 / F043)
- **NULL_BSWR** — block-shuffle-within-rank variant
- **Q_EC_R12_D5** — rank {1, 2} version of Q_EC_R0_D5
- **ZBLOCK** — z-score computed via NULL_BSWCD
- **BATCH** — a set of findings grouped for literature audit

Add via PR when an agent hits friction that a missing symbol would have
prevented.
