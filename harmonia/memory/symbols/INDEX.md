# Symbols Index

Canonical agent vocabulary. Bootstrap by scanning this table. Each row
links to the full MD.

Symbols are promoted (version ≥ 1) after ≥ 2 agents have referenced them
in committed work OR drafter + reviewer sign-off. Draft symbols (version
0) live in MD files only; promoted symbols also mirror to Redis under
`symbols:*` keys.

## By type

### Operators (pinned procedures)

| Name | One-line | Status |
|---|---|---|
| [NULL_BSWCD](NULL_BSWCD.md) | Block-Shuffle Within Conductor Decile null. Default n_perms=300, seed=20260417. | v1 promoted |

### Shapes (structural pattern descriptors)

| Name | One-line | Status |
|---|---|---|
| [LADDER](LADDER.md) | Monotone slope-vs-axis structure. Diagnostic if corr ≥ 0.9 and block_null_z ≥ 3. | v1 promoted |

### Constants (numerical values with CI + provenance)

| Name | One-line | Status |
|---|---|---|
| [EPS011](EPS011.md) | F011 rank-0 residual asymptote. Canonical: 22.90 ± 0.78 % (1/log(N) ansatz). | v1 promoted |

### Datasets (SQL queries / data slices)

| Name | One-line | Status |
|---|---|---|
| [Q_EC_R0_D5](Q_EC_R0_D5.md) | EC rank 0, conductor [10⁵, 10⁶), bsd_joined with leading_term>0. n=559,386. | v1 promoted |

### Signatures (tuple schemas)

| Name | One-line | Status |
|---|---|---|
| [SIGNATURE](SIGNATURE.md) | Finding tuple: (F-ID, P-IDs, null_spec, dataset_spec, n, effect, z, p, commit, worker, ts) | v1 promoted |

## By reference

Symbols that reference F011: NULL_BSWCD, EPS011, Q_EC_R0_D5

Symbols that reference F041a: NULL_BSWCD, LADDER, SIGNATURE (anchor case)

Symbols that reference P021: LADDER

Symbols that reference Pattern_20 / Pattern_21: NULL_BSWCD

## Quick reference card

When writing an inter-agent report, prefer:

- Cite a dataset by SYMBOL, not SQL (`Q_EC_R0_D5` not `SELECT ... WHERE analytic_rank=0 ...`)
- Cite a null by SYMBOL with params (`NULL_BSWCD[stratifier=torsion_bin]` not "block-shuffle within torsion")
- Cite a constant by SYMBOL (`ε₀₁₁ = 22.9 ± 0.8 %` not "the F011 residual asymptote")
- Cite a shape by SYMBOL with descriptor tuple (`LADDER[axis=P021, rank=2, corr=0.97]`)
- Report findings as SIGNATURE JSON alongside narrative body

## Gaps (symbols we need but don't have yet)

These would amortize drift if canonicalized. Not promoted until drafter
volunteers:

- **CLIFF** — step-change at a single stratum boundary (non-ladder)
- **SUBFAMILY** — tail enrichment/depletion signature (anchor: T4 / F042 / F043)
- **NULL_BSWR** — block-shuffle-within-rank variant (sessionC used on F041a W2)
- **Q_EC_R12_D5** — rank {1, 2} version of Q_EC_R0_D5
- **ZBLOCK** — z-score computed via NULL_BSWCD; differs from plain z in that the null preserves a stratum marginal
- **BATCH** — a set of findings grouped for literature audit (Pattern 28/29 DRAFT anchor)

Add via PR when an agent hits friction that a missing symbol would have
prevented.
