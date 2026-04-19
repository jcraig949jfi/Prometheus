---
name: NULL_BSWCD
type: operator
version: 2
version_timestamp: 2026-04-19T01:25:00Z
immutable: true
previous_version: 1
precision:
  n_perms_default: 300
  seed_default: 20260417
  n_bins_default: 10
  output_dtype: float64
  determinism: seeded_permutation_MC
  z_score_reporting: 2 decimal places
  null_mean_std_reporting: 4 sig figs
  degeneracy_warning_threshold: 0.20
proposed_by: Harmonia_M2_sessionD_reauditor@1a18421d
promoted_commit: 043ba782
references:
  - P104@c348113f3
  - F010@c1fc83060
  - F011@cb083d869
  - F013@c1abdec43
  - F015@c43fb1b12
  - F041a@c1abdec43
  - F043@c9fc25706
  - Pattern_20@ccab9e2c5
  - Pattern_21@c9335b7c2
redis_key: symbols:NULL_BSWCD:v2:def
implementation: harmonia/nulls/block_shuffle.py::bswcd_null@043ba782
---

## Definition

**Block-Shuffle Within Conductor Decile null.** A permutation null that
preserves the per-conductor-decile marginal distribution of the response
variable, and shuffles only within each decile. Used to test whether a
finding is an honest within-stratum coupling vs an artifact of
between-stratum conductor drift.

**Signature (v2, identical to v1 + one return field):**
```
NULL_BSWCD@v2(
    data: DataFrame with columns [<stratifier>, <shuffle_col>, ...],
    stratifier: str = "conductor",       # column to decile-bin
    n_bins: int = 10,                    # target stratum count
    n_perms: int = 300,                  # permutations
    seed: int = 20260417,                # reproducibility
    statistic: Callable = default,       # what to recompute on each shuffle
    shuffle_col: str = "value",          # column permuted within strata
) -> {
    "null_mean": float64,    # 4 sig figs meaningful
    "null_std": float64,     # 4 sig figs meaningful
    "null_p99": float64,
    "observed": float64,
    "z_score": float64,      # 2 decimal places meaningful
    "verdict": "DURABLE" if |z| >= 3 else "COLLAPSES",
    "n_strata_used": int,    # after duplicates='drop'
    "stratifier": str,
    "n_bins": int,
    "n_perms": int,
    "seed": int,
    "degeneracy_warning": str | absent  # present if dominant stratum > 20%
}
```

## What v2 changes vs v1

**v1 → v2 is backward-compatible additive.** No previous caller breaks.

1. **Implementation pointer resolved.** `implementation` field was
   `@pending` in v1 (symbol promoted before code shipped). v2 pins to
   `harmonia/nulls/block_shuffle.py::bswcd_null@043ba782` — the live
   reference implementation.
2. **Stratifier parameterized explicitly.** v1's signature implicitly
   assumed `data['conductor']`; v2 accepts `stratifier: str = "conductor"`
   so the same operator handles `torsion`, `rank`, `num_bad_primes`, etc.
   without rewrites. Default matches v1 behavior.
3. **Shuffle column parameterized.** v1 implicitly shuffled
   `data['value']`; v2 accepts `shuffle_col: str = "value"` for the same
   semantic (default unchanged).
4. **Pattern 26 degeneracy guard wired in.** `degeneracy_warning` field
   appears in output when the dominant stratum covers >20% of data
   (`degeneracy_warning_threshold: 0.20`). v1 logged this verbally in
   the MD; v2 emits it programmatically. No effect on z-score or
   verdict — purely advisory.
5. **Audit-trail fields added.** Return dict now includes
   `n_strata_used`, `stratifier`, `n_bins`, `n_perms`, `seed` so every
   call result is fully self-describing (SIGNATURE@v1 no longer needs
   to track them separately).

All default values are identical to v1. Any caller that used v1 with
defaults gets byte-identical behavior under v2.

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

Applied to F043@c9fc25706 via `reaudit_F043_2cells` (Harmonia_M2_sessionD
reauditor, commit 9fc25706, 2026-04-19):
- F043 corr(log Sha, log A) rank-0 decade: z_block = -348.05 (observed
  -0.4343 vs null 0 ± 0.0012). Anticorrelation is real within-conductor-
  decile structure.

Applied to F011's seven +1 cells via `reaudit_F011_7cells` (same
session, commit 043ba782, 2026-04-19):
- Six cells DURABLE (z ∈ {5.53, 6.03, 31.26, 38.58, 160.20, 160.20}).
- F011:P024 torsion COLLAPSES at z=1.37 — the cross-torsion-class
  differential is conductor-mediated, not structural.

**Stratifier choice caveat** (sessionB recursion-3, commit 71ff1d47): the
stratifier must be well-balanced. `class_size` stratification on F011
gave null_std=0 (one value covers 59% of data) → spurious z=168757.
Honest stratifier needs 5–20 balanced strata. v2 implementation emits
`degeneracy_warning` programmatically when the dominant stratum is
>20% of data. See Pattern 26.

## References

**Internal:**
- Pattern_20@ccab9e2c5 — pooled-is-projection
- Pattern_21@c9335b7c2 — null-model selection
- Pattern 26 (DRAFT) — confound selection discipline
- P104@c348113f3 — block-shuffle-null as catalog projection
- Anchor cases: F010@c1fc83060 (kill), F011@cb083d869, F013@c1abdec43,
  F015@c43fb1b12, F041a@c1abdec43, F043@c9fc25706 (survive)

**Papers:**
- No direct paper — application of standard stratified permutation
  inference (Good 2005, *Permutation, Parametric and Bootstrap Tests of
  Hypotheses*, §3.4 "Block Permutation Tests") adapted for conductor
  stratification on EC L-functions.

## Data / implementation

**Live reference implementation:** `harmonia/nulls/block_shuffle.py::bswcd_null@043ba782`.

```python
from harmonia.nulls import bswcd_null

result = bswcd_null(
    data=df,
    stratifier="conductor",   # or "rank", "torsion", "num_bad_primes", ...
    n_bins=10,
    n_perms=300,
    seed=20260417,
    statistic=my_stat,        # callable(DataFrame) -> float
    shuffle_col="value",
)
# result["z_score"], result["verdict"], result["null_mean"], ...
```

Defaults pinned at v2 (identical to v1): `n_bins=10`, `n_perms=300`,
`seed=20260417`, `stratifier="conductor"`, `shuffle_col="value"`.
Agents requesting different parameters must declare them in the call
signature (e.g. `NULL_BSWCD@v2[stratifier=torsion,n_perms=1000,seed=42]`).

## Usage

```
F011@cb083d869 rank-0 residual:
  NULL_BSWCD@v2[stratifier=conductor_decile, n_perms=300] → z=10.46
  NULL_BSWCD@v2[stratifier=class_size] → DEGENERATE (degeneracy_warning)
  NULL_BSWCD@v2[stratifier=torsion_bin] → z=4.19 DURABLE

F043@c9fc25706 BSD-Sha anticorrelation:
  NULL_BSWCD@v2[stratifier=conductor, n_perms=300] → z=-348.05 DURABLE
```

## Version history

- **v1** 2026-04-18T14:30:00Z — promoted under strict schema. Defaults
  pinned; signature and output precision declared. `implementation`
  field set to `@pending` (code not yet shipped).
- **v2** 2026-04-19T01:25:00Z — backward-compatible additive upgrade.
  Implementation pinned to `harmonia/nulls/block_shuffle.py::bswcd_null
  @043ba782`. Parameterized `stratifier` and `shuffle_col` (defaults
  preserve v1 behavior). Pattern 26 degeneracy guard wired into return
  dict. Audit-trail fields (`n_strata_used`, etc.) added to output. No
  breaking changes; any v1 caller using defaults gets identical
  behavior at v2.
