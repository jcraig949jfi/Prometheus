---
name: NULL_BSWCD
type: operator
version: 1
proposed_by: Harmonia_M2_sessionB@e1252f55
promoted_commit: pending
references: [P104, F010, F011, F013, F015, F041a, Pattern_20, Pattern_21]
redis_key: symbol:NULL_BSWCD:def
implementation: harmonia/nulls/block_shuffle.py::bswcd_null
---

## Definition

**Block-Shuffle Within Conductor Decile null.** A permutation null that
preserves the per-conductor-decile marginal distribution of the response
variable, and shuffles only within each decile. Used to test whether a
finding is an honest within-stratum coupling vs an artifact of
between-stratum conductor drift.

**Signature:**
```
NULL_BSWCD(
    data: DataFrame with columns [conductor, value, ...],
    n_bins: int = 10,                    # conductor deciles
    n_perms: int = 300,                  # permutations
    seed: int = 20260417,                # reproducibility
    statistic: Callable = default,       # what to recompute on each shuffle
) -> {
    "null_mean": float,
    "null_std": float,
    "null_p99": float,
    "observed": float,
    "z_score": float,
    "verdict": "DURABLE" if |z| >= 3 else "COLLAPSES"
}
```

## Derivation / show work

Born from the F010 block-shuffle audit (sessionC `wsw_F010_alternative_null`,
commit 711f8325, 2026-04-17). F010's decontaminated ρ=0.27 gave z=2.38
under plain label-permute null but z=-0.86 under block-shuffle-within-
degree null — signal was degree-marginal, not within-degree coupling.
This established "null-model selection matters as much as projection
selection" (Pattern 21).

Applied to F011/F013 via `audit_P028_findings_block_shuffle` (sessionB,
commit 24b41571):
- F011: z_block = 111.78 (observed 7.63% spread vs null p99 0.27%)
- F013: z_block = 15.31 (slope diff z=13.68 vs null p99 1.47)

Applied to F015 via `audit_F014_F015_block_shuffle` (sessionC, 4a28471f):
- F015 k-stratum z_block ∈ [-24.03, -3.48] — every stratum durable

**Stratifier choice caveat** (sessionB recursion-3, commit 71ff1d47): the
stratifier must be well-balanced. `class_size` stratification on F011
gave null_std=0 (one value covers 59% of data) → spurious z=168757.
Honest stratifier needs 5–20 balanced strata. See `Pattern 26 (DRAFT)`.

## References

**Internal:**
- [Pattern 20](../pattern_library.md#pattern-20) — pooled-is-projection
- [Pattern 21](../pattern_library.md#pattern-21) — null-model selection
- [Pattern 26 (DRAFT)](../pattern_library.md#draft-patterns-23-29) — confound selection discipline
- [P104](../coordinate_system_catalog.md) — block-shuffle-null as catalog projection
- Anchor cases: F010 (kill), F011/F013/F015/F041a (survive)

**Papers:**
- No direct paper — this is an application of standard stratified
  permutation inference (Good 2005, *Permutation, Parametric and
  Bootstrap Tests of Hypotheses*, §3.4 "Block Permutation Tests")
  adapted for conductor stratification on EC L-functions.

## Data / implementation

**Pinned code (when implemented):**
```python
# harmonia/nulls/block_shuffle.py
def bswcd_null(data, n_bins=10, n_perms=300, seed=20260417, statistic=None):
    rng = np.random.default_rng(seed)
    deciles = pd.qcut(data['conductor'], q=n_bins, labels=False, duplicates='drop')
    observed = statistic(data)
    null_vals = []
    for _ in range(n_perms):
        shuffled = data.copy()
        for d in deciles.unique():
            mask = deciles == d
            shuffled.loc[mask, 'value'] = rng.permutation(data.loc[mask, 'value'].values)
        null_vals.append(statistic(shuffled))
    nm, ns = np.mean(null_vals), np.std(null_vals)
    z = (observed - nm) / ns if ns > 1e-12 else float('inf')
    return {
        "null_mean": nm,
        "null_std": ns,
        "null_p99": np.percentile(null_vals, 99),
        "observed": observed,
        "z_score": z,
        "verdict": "DURABLE" if abs(z) >= 3 else "COLLAPSES"
    }
```

Pin-down: `n_bins=10`, `n_perms=300`, `seed=20260417`. Agents requesting
different parameters explicitly declare them in the call signature.
Default parameters match the audit that established the F011/F013
durability claims.

## Usage

In inter-agent communication:
```
F011 rank-0 residual: NULL_BSWCD[stratifier=conductor_decile, n_perms=300] → z=10.46
                      NULL_BSWCD[stratifier=class_size] → DEGENERATE (null_std=0)
                      NULL_BSWCD[stratifier=torsion_bin] → z=4.19 DURABLE
```

The per-call parameters are what changed; agents don't need to re-describe
the procedure.

## Version history

- **v0 (draft)** 2026-04-17 — sessionC F010 application (wsw_F010_alternative_null)
- **v1** 2026-04-18 — promoted after anchor-case validation (F010 kill +
  F011/F013/F015 survival + F041a W2 survival). References expanded.
