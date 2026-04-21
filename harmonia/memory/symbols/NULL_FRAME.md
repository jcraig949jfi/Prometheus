---
name: NULL_FRAME
type: operator
version: 1
version_timestamp: 2026-04-20T23:55:00Z
immutable: true
previous_version: null
precision:
  n_perms_default: 300
  seed_default: 20260420
  output_dtype: float64
  determinism: seeded_frame_resample
  frame_spec_required: true
  z_score_reporting: 2 decimal places
  null_mean_std_reporting: 4 sig figs
proposed_by: Harmonia_M2_sessionA@gen_02
promoted_commit: pending
references:
  - Pattern_21@c9335b7c2
  - NULL_BSWCD@v2
  - SIGNATURE@v2
  - null_protocol@v1
redis_key: symbols:NULL_FRAME:v1:def
implementation: harmonia/nulls/frame.py::frame_null@pending
---

## Definition

**Frame-based resample null for construction-biased samples.** Required
when the observed sample is the output of a specific catalogue/search
methodology rather than a representative draw from a mathematically
defined population (Class 4 per `null_protocol_v1.md`). The null
reconstructs a broader sampling frame, re-applies the constructive
methodology (or an inverse of its bias), and measures whether the
claimed property persists.

**Role in the null family (gen_02):** NULL_BSWCD cannot address
construction bias — shuffling within a biased sample preserves the
bias. NULL_FRAME is the only family member that can address Class 4
claims. For Class 1/2/3 claims, NULL_FRAME is typically marked N/A
(sample is already representative).

**Signature:**
```
NULL_FRAME@v1(
    data: DataFrame,
    frame: str,              # named frame spec, e.g. "lmfdb_r0_d5"
    resampler: Callable,     # function(frame, rng) -> DataFrame
    n_perms: int = 300,
    seed: int = 20260420,
    statistic: Callable = default,
) -> {
    "null_mean": float64,
    "null_std": float64,
    "null_p99": float64,
    "observed": float64,
    "z_score": float64,
    "verdict": "DURABLE" if |z| >= 3 else "COLLAPSES",
    "frame": str,
    "n_perms": int,
    "seed": int,
    "frame_applicability": "class_4" | "n_a",
}
```

**`frame` parameter is MANDATORY.** This is not a generic null — it is
specific to a named sampling frame. A call without `frame` fails.
Frame specs live in `harmonia/memory/frames/` (to be populated; today
`lmfdb_r0_d5` and `lmfdb_r4` are the immediate targets).

## Derivation / show work

F044 (rank-4 EC disc=conductor ratio) is the canonical Class 4
anchor. LMFDB's rank-4 list is constructed via isogeny-class walks,
bounded-height searches, and prior-curve extensions. Observing that
2085 / 2086 rank-4 curves in LMFDB satisfy disc = conductor does not
imply absence of exceptions in the population — the search may
systematically miss additive-reduction rank-4 curves. A permutation
null on this sample preserves the construction bias; the null needs to
operate on the *frame*, not the sample.

NULL_FRAME is the symbol that formalizes this operational difference.
The `resampler` callable is the per-frame implementation of "what would
a non-biased draw from this frame look like?" Frame specs declare the
methodology and the resampler pins an inversion or broadening strategy.

Without a frame spec, NULL_FRAME cannot run. This is intentional — it
forces the user to declare the bias being addressed rather than
running a generic null that silently fails to catch construction bias.

## References

**Internal:**
- null_protocol@v1 — defines Class 4 and the NULL_BSWCD insufficiency
- Pattern_21@c9335b7c2 — null-model selection matters
- NULL_BSWCD@v2 — insufficient for Class 4
- F044@cb083d869 — canonical Class 4 anchor case (provisional pending
  frame-based resample)

**Papers:**
- Bhargava & Shankar (2015) on density conjectures for rank — provides
  population-level expectation that a model-based frame can compare to.

## Data / implementation

**Reference implementation (pending):** `harmonia/nulls/frame.py::frame_null`
(scaffold; real per-frame resamplers authored per-case in
`harmonia/nulls/frames/<frame_name>.py`).

```python
from harmonia.nulls.frame import frame_null
from harmonia.nulls.frames.lmfdb_r4 import lmfdb_r4_resampler

result = frame_null(
    data=df,
    frame="lmfdb_r4",
    resampler=lmfdb_r4_resampler,
    n_perms=300,
    seed=20260420,
    statistic=disc_eq_conductor_fraction,
)
```

## Claim-class applicability

| Class | Applies? | Notes |
|---|---|---|
| 1 (moment/ratio ∘ conductor) | N/A | sample is representative; construction bias not primary |
| 2 (rank-slope interaction) | N/A | within-sample interaction; frame not primary |
| 3 (stratum-uniform) | N/A | within-sample; frame not primary |
| 4 (construction-biased) | **REQUIRED** | the only family member that addresses this class |
| 5 (algebraic-identity) | N/A | refuse all nulls |

## Usage

```
F044 rank-4 disc=conductor:
  NULL_BSWCD@v2[stratifier=conductor] → z=<would-report-high> BUT MISLEADING
    (construction bias preserved)
  NULL_FRAME@v1[frame=lmfdb_r4,resampler=<spec>] → deferred pending
    frame spec implementation.
```

## Version history

- **v1** 2026-04-20T23:55:00Z — initial promotion. Frame spec
  REQUIRED. Implementation scaffold ships; per-frame resamplers are
  separate authoring tasks. Only family member that addresses
  null_protocol_v1 Class 4.
