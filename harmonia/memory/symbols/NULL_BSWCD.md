---
name: NULL_BSWCD
type: operator
version: 1
version_timestamp: 2026-04-18T14:30:00Z
immutable: true
previous_version: null
precision:
  n_perms_default: 300
  seed_default: 20260417
  n_bins_default: 10
  output_dtype: float64
  determinism: seeded_permutation_MC
  z_score_reporting: 2 decimal places
  null_mean_std_reporting: 4 sig figs
proposed_by: Harmonia_M2_sessionB@e1252f55
promoted_commit: pending
references:
  - P104@c348113f3
  - F010@c1fc83060
  - F011@cb083d869
  - F013@c1abdec43
  - F015@c43fb1b12
  - F041a@c1abdec43
  - Pattern_20@ccab9e2c5
  - Pattern_21@c9335b7c2
redis_key: symbols:NULL_BSWCD:v1:def
implementation: harmonia/nulls/block_shuffle.py::bswcd_null@pending
---

## Definition

**Block-Shuffle Within Conductor Decile null.** A permutation null that
preserves the per-conductor-decile marginal distribution of the response
variable, and shuffles only within each decile. Used to test whether a
finding is an honest within-stratum coupling vs an artifact of
between-stratum conductor drift.

**Signature:**
```
NULL_BSWCD@v1(
    data: DataFrame with columns [conductor, value, ...],
    n_bins: int = 10,                    # conductor deciles
    n_perms: int = 300,                  # permutations
    seed: int = 20260417,                # reproducibility
    statistic: Callable = default,       # what to recompute on each shuffle
) -> {
    "null_mean": float64,    # 4 sig figs meaningful
    "null_std": float64,     # 4 sig figs meaningful
    "null_p99": float64,
    "observed": float64,
    "z_score": float64,      # 2 decimal places meaningful
    "verdict": "DURABLE" if |z| >= 3 else "COLLAPSES"
}
```

## Derivation / show work

Born from the F010@c1fc83060 block-shuffle audit (sessionC
`wsw_F010_alternative_null`, commit 711f8325, 2026-04-17). F010's
decontaminated ρ=0.27 gave z=2.38 under plain label-permute null but
z=-0.86 under block-shuffle-within-degree null — signal was
degree-marginal, not within-degree coupling. This established
"null-model selection matters as much as projection selection"
(Pattern_21@c9335b7c2).

Applied to F011 and F013 via `audit_P028_findings_block_shuffle`
(sessionB, commit 24b41571):
- F011@cb083d869: z_block = 111.78 (observed 7.63% spread vs null p99 0.27%)
- F013@c1abdec43: z_block = 15.31 (slope diff z=13.68 vs null p99 1.47)

Applied to F015@c43fb1b12 via `audit_F014_F015_block_shuffle` (sessionC,
4a28471f):
- F015 k-stratum z_block ∈ [-24.03, -3.48] — every stratum durable

**Stratifier choice caveat** (sessionB recursion-3, commit 71ff1d47): the
stratifier must be well-balanced. `class_size` stratification on F011
gave null_std=0 (one value covers 59% of data) → spurious z=168757.
Honest stratifier needs 5–20 balanced strata. See Pattern 26 (DRAFT).

## References

**Internal:**
- Pattern_20@ccab9e2c5 — pooled-is-projection
- Pattern_21@c9335b7c2 — null-model selection
- Pattern 26 (DRAFT) — confound selection discipline
- P104@c348113f3 — block-shuffle-null as catalog projection
- Anchor cases: F010@c1fc83060 (kill), F011@cb083d869, F013@c1abdec43,
  F015@c43fb1b12, F041a@c1abdec43 (survive)

**Papers:**
- No direct paper — application of standard stratified permutation
  inference (Good 2005, *Permutation, Parametric and Bootstrap Tests of
  Hypotheses*, §3.4 "Block Permutation Tests") adapted for conductor
  stratification on EC L-functions.

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
    nm, ns = float(np.mean(null_vals)), float(np.std(null_vals))
    z = (observed - nm) / ns if ns > 1e-12 else float('inf')
    return {
        "null_mean": nm,
        "null_std": ns,
        "null_p99": float(np.percentile(null_vals, 99)),
        "observed": float(observed),
        "z_score": float(z),
        "verdict": "DURABLE" if abs(z) >= 3 else "COLLAPSES"
    }
```

Defaults pinned at v1: `n_bins=10`, `n_perms=300`, `seed=20260417`.
Agents requesting different parameters must declare them in the call
signature (e.g. `NULL_BSWCD@v1[n_perms=1000,seed=42]`). Defaults match
the audit that established F011/F013 durability claims.

## Usage

```
F011@cb083d869 rank-0 residual: NULL_BSWCD@v1[stratifier=conductor_decile, n_perms=300] → z=10.46
                                NULL_BSWCD@v1[stratifier=class_size] → DEGENERATE (null_std=0)
                                NULL_BSWCD@v1[stratifier=torsion_bin] → z=4.19 DURABLE
```

## Version history

- **v1** 2026-04-18T14:30:00Z — promoted under strict schema. Defaults
  pinned; signature and output precision declared. Frontier work
  continues at `NULL_BSWCD@v1`; any precision or default change creates v2.
