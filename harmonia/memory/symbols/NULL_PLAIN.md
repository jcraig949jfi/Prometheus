---
name: NULL_PLAIN
type: operator
version: 1
version_timestamp: 2026-04-20T23:55:00Z
immutable: true
status: active
previous_version: null
precision:
  n_perms_default: 300
  seed_default: 20260420
  output_dtype: float64
  determinism: seeded_permutation_MC
  z_score_reporting: 2 decimal places
  null_mean_std_reporting: 4 sig figs
proposed_by: Harmonia_M2_sessionA@gen_02
promoted_commit: pending
references:
  - Pattern_21@c9335b7c2
  - NULL_BSWCD@v2
  - SIGNATURE@v2
redis_key: symbols:NULL_PLAIN:v1:def
implementation: harmonia/nulls/plain.py::plain_null@pending
---

## Definition

**Plain label-permutation null.** The baseline coarse lens: permute the
response variable across the entire dataset, recompute the statistic,
compare observed to the null distribution. Preserves only the marginal
of the shuffled variable; destroys pairings and all stratification
structure.

**Role in the null family (gen_02):** this is the *cheapest* null and
the one most likely to report "signal" because it preserves nothing. A
claim that fails NULL_PLAIN cannot survive the stricter family members.
A claim that passes NULL_PLAIN at high z but fails NULL_BSWCD means the
signal was between-stratum drift, not within-stratum structure. The
Pattern 21 diagnostic compares the two.

**Signature:**
```
NULL_PLAIN@v1(
    data: DataFrame,
    n_perms: int = 300,
    seed: int = 20260420,
    statistic: Callable = mean('value'),
    shuffle_col: str = "value",
) -> {
    "null_mean": float64,    # 4 sig figs meaningful
    "null_std": float64,     # 4 sig figs meaningful
    "null_p99": float64,
    "observed": float64,
    "z_score": float64,      # 2 decimal places meaningful
    "verdict": "DURABLE" if |z| >= 3 else "COLLAPSES",
    "n_perms": int,
    "seed": int,
}
```

## Derivation / show work

Established as the baseline in the F010 audit chain (sessionC
`wsw_F010_alternative_null`, 2026-04-17): F010's decontaminated ρ=0.27
gave z=2.38 under plain label-permute but z=-0.86 under block-shuffle-
within-degree. The spread between the two nulls *is* the Pattern 21
diagnostic — plain null holds nothing fixed, block-shuffle holds the
stratification fixed, discordance localizes the signal.

Named explicitly in gen_02 (2026-04-20) as a family member so every
new +1/+2 cell carries a plain-null reading alongside its stratified
reading. The pair makes discordance visible automatically.

## References

**Internal:**
- Pattern_21@c9335b7c2 — null-model selection matters
- NULL_BSWCD@v2 — stratified counterpart; family member
- SIGNATURE@v2 — consumes the family vector

**Papers:**
- Good (2005) *Permutation, Parametric and Bootstrap Tests of
  Hypotheses*, §2.1 (standard unrestricted permutation baseline).

## Data / implementation

**Reference implementation (pending):** `harmonia/nulls/plain.py::plain_null`.

```python
from harmonia.nulls.plain import plain_null

result = plain_null(
    data=df,
    n_perms=300,
    seed=20260420,
    statistic=my_stat,
    shuffle_col="value",
)
```

## Claim-class applicability

Per `null_protocol_v1.md`:

| Class | Applies? | Notes |
|---|---|---|
| 1 (moment/ratio ∘ conductor) | yes | baseline coarse |
| 2 (rank-slope interaction) | yes | baseline coarse |
| 3 (stratum-uniform) | yes | baseline coarse |
| 4 (construction-biased) | N/A | sample is not representative; plain null does not address the bias |
| 5 (algebraic-identity) | N/A | refuse all nulls |

NULL_PLAIN is never *sufficient* for Class 1-3 promotion; it is the
baseline companion that makes discordance visible.

## Usage

```
F011 rank-0 residual:
  NULL_PLAIN@v1[n_perms=300,seed=20260420] → z=7.63
  NULL_BSWCD@v2[stratifier=conductor_decile] → z=111.78
  ⇒ discordance 14.6× — conductor-stratification is the resolving lens.
```

## Version history

- **v1** 2026-04-20T23:55:00Z — initial promotion as gen_02 family
  member. Seed pinned at 20260420 (gen_02 promotion date). Signature
  and output precision declared per VERSIONING.md rules 1-4.
