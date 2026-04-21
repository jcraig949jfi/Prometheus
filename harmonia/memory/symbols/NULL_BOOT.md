---
name: NULL_BOOT
type: operator
version: 1
version_timestamp: 2026-04-20T23:55:00Z
immutable: true
previous_version: null
precision:
  n_boot_default: 1000
  seed_default: 20260420
  n_bins_default: 10
  output_dtype: float64
  determinism: seeded_bootstrap_resample
  z_score_reporting: 2 decimal places
  null_mean_std_reporting: 4 sig figs
  degeneracy_warning_threshold: 0.20
proposed_by: Harmonia_M2_sessionA@gen_02
promoted_commit: pending
references:
  - Pattern_21@c9335b7c2
  - NULL_BSWCD@v2
  - SIGNATURE@v2
redis_key: symbols:NULL_BOOT:v1:def
implementation: harmonia/nulls/bootstrap.py::boot_null@pending
---

## Definition

**Stratified bootstrap-with-replacement null.** Resample rows with
replacement *within each stratum*, recompute the statistic,
build the null distribution. Preserves the stratifier marginal
exactly; tests whether the observed statistic is stable under
sample-variance perturbation of the same population.

**Role in the null family (gen_02):** NULL_BSWCD permutes labels; it
asks whether the pairing was informative. NULL_BOOT resamples rows; it
asks whether the statistic would be the same if we drew a fresh sample
from the same frame. Together they separate "the pairing is real" from
"the estimate is stable" — two distinct idempotence claims.

**Signature:**
```
NULL_BOOT@v1(
    data: DataFrame with stratifier column,
    stratifier: str = "conductor",
    n_bins: int = 10,
    n_boot: int = 1000,
    seed: int = 20260420,
    statistic: Callable = mean('value'),
) -> {
    "null_mean": float64,
    "null_std": float64,
    "null_p99": float64,
    "observed": float64,
    "z_score": float64,
    "verdict": "DURABLE" if |z| >= 3 else "COLLAPSES",
    "n_strata_used": int,
    "stratifier": str,
    "n_bins": int,
    "n_boot": int,
    "seed": int,
    "degeneracy_warning": str | absent
}
```

## Derivation / show work

Bootstrap is a distinct null from permutation. Permutation answers "is
the pairing informative?" — it destroys couplings. Bootstrap answers
"is the estimate stable under resampling from the same source?" — it
preserves couplings but perturbs the sample. The two can disagree:

- Strong pairing, small sample → high permutation-z, low bootstrap
  stability (sample-variance dominates).
- Weak pairing, large sample → low permutation-z, high bootstrap
  stability (tight CI around a null-coincident estimate).

A claim requires both: informative pairing AND stable estimate. gen_02
makes the joint test automatic.

**Stratified (not naive) bootstrap** because naive bootstrap breaks the
stratifier marginal — resampling across strata with replacement yields
unbalanced stratum representation that confounds the stratification
contract. `stratifier=conductor_decile` means we resample within each
decile with replacement, preserving decile cardinality.

## References

**Internal:**
- Pattern_21@c9335b7c2 — null-model selection matters
- NULL_BSWCD@v2 — permutation counterpart in the family
- SIGNATURE@v2 — consumes the family vector
- Pattern 26 (DRAFT) — degeneracy guard reused from NULL_BSWCD

**Papers:**
- Efron & Tibshirani (1993) *An Introduction to the Bootstrap*, §8
  (stratified bootstrap).
- Good (2005) *Permutation, Parametric and Bootstrap Tests of
  Hypotheses*, §5 (bootstrap vs permutation contrasts).

## Data / implementation

**Reference implementation (pending):** `harmonia/nulls/bootstrap.py::boot_null`.

```python
from harmonia.nulls.bootstrap import boot_null

result = boot_null(
    data=df,
    stratifier="conductor",
    n_bins=10,
    n_boot=1000,
    seed=20260420,
    statistic=my_stat,
)
```

## Claim-class applicability

Per `null_protocol_v1.md`:

| Class | Applies? | Notes |
|---|---|---|
| 1 (moment/ratio ∘ conductor) | yes | companions NULL_BSWCD with sample-stability lens |
| 2 (rank-slope interaction) | yes | stratifier=rank_bin |
| 3 (stratum-uniform) | yes | stratifier=the-stratum-being-tested |
| 4 (construction-biased) | N/A | resample can't fix non-representative frame |
| 5 (algebraic-identity) | N/A | refuse |

## Usage

```
F011 rank-0 residual:
  NULL_BSWCD@v2[stratifier=conductor_decile] → z=111.78
  NULL_BOOT@v1[stratifier=conductor_decile,n_boot=1000] → z=8.92 DURABLE
  ⇒ pairing informative AND estimate stable; family-verdict passes.
```

## Version history

- **v1** 2026-04-20T23:55:00Z — initial promotion. Seed pinned at
  20260420. Stratified-bootstrap semantics declared (not naive).
  Degeneracy guard reused from NULL_BSWCD per Pattern 26.
