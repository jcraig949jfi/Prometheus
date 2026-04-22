---
name: NULL_MODEL
type: operator
version: 1
version_timestamp: 2026-04-20T23:55:00Z
immutable: true
status: active
previous_version: null
precision:
  n_samples_default: 10000
  seed_default: 20260420
  output_dtype: float64
  determinism: seeded_parametric_draw
  model_spec_required: true
  z_score_reporting: 2 decimal places
  null_mean_std_reporting: 4 sig figs
proposed_by: Harmonia_M2_sessionA@gen_02
promoted_commit: pending
references:
  - Pattern_21@c9335b7c2
  - NULL_BSWCD@v2
  - SIGNATURE@v2
redis_key: symbols:NULL_MODEL:v1:def
implementation: harmonia/nulls/model.py::model_null@pending
---

## Definition

**Parametric-model null.** Generates synthetic data from a pre-specified
probability model (GUE, Poisson, Gaussian-process, Katz-Sarnak
ensemble, etc.), recomputes the statistic on each draw, and compares
observed to the model null distribution.

**Role in the null family (gen_02):** NULL_BSWCD and NULL_PLAIN are
*nonparametric* nulls — they make no distributional assumption. NULL_MODEL
bakes a specific theoretical distribution into the null. This is the
right lens when the claim is explicitly "the data behaves like <model>"
or "the data deviates from <model> in direction D." The F011 GUE
deviation (z=-19 observed vs GUE expectation) is a NULL_MODEL claim,
not a NULL_BSWCD claim.

**Signature:**
```
NULL_MODEL@v1(
    observed_statistic: float,   # already computed from data
    model: str,                  # named model, e.g. "GUE", "Poisson", "KS_U"
    model_params: dict,          # per-model parameters (degree, n, etc.)
    n_samples: int = 10000,
    seed: int = 20260420,
    statistic_sampler: Callable, # function(model_params, rng) -> float
) -> {
    "null_mean": float64,
    "null_std": float64,
    "null_p99": float64,
    "observed": float64,
    "z_score": float64,
    "verdict": "DURABLE" if |z| >= 3 else "COLLAPSES",
    "model": str,
    "model_params": dict,
    "n_samples": int,
    "seed": int,
}
```

**`model` and `model_params` are MANDATORY.** The whole point is to
pin the theoretical distribution; a generic call is meaningless.

## Derivation / show work

F011's GUE deviation is the canonical anchor. The observed first-gap
statistic on rank-0 EC L-function low-zeros sits ~19 sigma below the
GUE expectation — a claim that is only meaningful relative to GUE as a
null. Shuffling labels (NULL_BSWCD) doesn't answer this question; the
question is whether the data matches a *theoretical* distribution, not
whether pairings are informative.

gen_02 makes NULL_MODEL a first-class family member because (a) the
F011 GUE anchor demands it, (b) Katz-Sarnak universality claims across
domains will demand it, (c) null_protocol_v1.md §Class 4 lists
model-based nulls as one of the two Class-4-appropriate options (the
other being frame-based).

**Important asymmetry:** for NULL_MODEL, "the data is the null" —
observed z=-19 is the *signal*, not the noise. A "DURABLE" verdict under
NULL_MODEL means the data rejects the model, which may be either
"signal" (the data has new structure the model misses) or
"model-wrong" (the model is the wrong baseline). The conductor decides
which interpretation applies via domain knowledge; the null only
reports the z-score.

## References

**Internal:**
- Pattern_21@c9335b7c2 — null-model selection matters
- F011@cb083d869 — canonical anchor; GUE deviation
- NULL_BSWCD@v2 — nonparametric counterpart in the family

**Papers:**
- Katz & Sarnak (1999) *Random Matrices, Frobenius Eigenvalues, and
  Monodromy* — the canonical L-function random matrix ensembles.
- Mehta (2004) *Random Matrices*, ch. 6 (GUE derivation).

## Data / implementation

**Reference implementation (pending):** `harmonia/nulls/model.py::model_null`.
Per-model samplers live in `harmonia/nulls/models/<model_name>.py`:

```python
from harmonia.nulls.model import model_null
from harmonia.nulls.models.gue import gue_first_gap_sampler

result = model_null(
    observed_statistic=obs_first_gap,
    model="GUE",
    model_params={"degree": 2, "n_zeros": 30},
    n_samples=10000,
    seed=20260420,
    statistic_sampler=gue_first_gap_sampler,
)
```

## Claim-class applicability

| Class | Applies? | Notes |
|---|---|---|
| 1 (moment/ratio ∘ conductor) | sometimes | if claim is "moment matches model M," yes. |
| 2 (rank-slope interaction) | rarely | most rank-slope claims are nonparametric |
| 3 (stratum-uniform) | rarely | most stratum-uniform claims are nonparametric |
| 4 (construction-biased) | sometimes | model-based null is one of the two Class-4 options |
| 5 (algebraic-identity) | N/A | refuse all nulls |

**Discipline:** NULL_MODEL applies only when the claim references a
specific theoretical distribution. A NULL_MODEL z-score on a claim that
doesn't cite a model is meaningless noise.

## Usage

```
F011 GUE deviation:
  NULL_MODEL@v1[model=GUE,model_params={degree:2,n_zeros:30}] → z=-19.26
  (observed = GUE_expect - 14% first-gap deficit; DURABLE rejection of GUE)
```

## Version history

- **v1** 2026-04-20T23:55:00Z — initial promotion. Model + model_params
  REQUIRED. Implementation scaffold ships; per-model samplers
  authored per-case.
