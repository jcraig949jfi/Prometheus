---
name: SIGNATURE
type: signature
version: 1
version_timestamp: 2026-04-18T14:30:00Z
immutable: true
status: active
previous_version: null
precision:
  schema: fixed tuple, JSON-serializable
  field_types:
    feature_id: string "F<num>@c<commit_short>"
    projection_ids: list of "P<num>@c<commit_short>"
    null_spec: string "<SYMBOL>@v<N>[<params>]"
    dataset_spec: string "<SYMBOL>@v<N>[ ∩ <subfilter>]?"
    n_samples: int exact
    effect_size: float64 sig-figs per symbol-specific precision field
    z_score: float64 2 decimal places
    p_value: float64 or null
    precision_map: object mapping each numeric field to its declared precision
    commit: string git short-hash
    worker: string "<AgentName>_<session>"
    timestamp: string ISO-8601 UTC
    reproducibility_hash: string sha256 hex of canonical JSON
  equivalence_test: two SIGNATUREs with identical (feature_id, null_spec, dataset_spec, n_samples) must produce byte-identical (effect_size, z_score)
proposed_by: Harmonia_M2_sessionA@cb083d869
promoted_commit: pending
references:
  - Pattern_17@ccab9e2c5
  - NULL_BSWCD@v1
  - Q_EC_R0_D5@v1
redis_key: symbols:SIGNATURE:v1:def
implementation: agora/register_specimen.py::register@pending
---

## Definition

**Canonical finding tuple schema.** Every reproducible empirical finding
from any agent is reportable as a `SIGNATURE@v1` — a fixed set of fields
that allow programmatic cross-instance equivalence checking.

```
SIGNATURE@v1 = (
    feature_id:        str,           # "F011@c<commit>"
    projection_ids:    list[str],     # ["P020@c<commit>", "P023@c<commit>"]
    null_spec:         str,           # "NULL_BSWCD@v1[stratifier=...]"
    dataset_spec:      str,           # "Q_EC_R0_D5@v1 ∩ HAS_OMEGA"
    n_samples:         int,           # exact
    effect_size:       float64,       # precision per field in precision_map
    z_score:           float64 | None,
    p_value:           float64 | None,
    precision_map:     dict,          # declared precision per numeric field
    commit:            str,           # git short hash
    worker:            str,           # "Harmonia_M2_sessionC_U_A"
    timestamp:         str,           # ISO-8601 UTC
    reproducibility_hash: str,        # sha256 of canonical JSON minus this field
)
```

## Derivation / show work

Ad-hoc finding reports across the 2026-04-17/18 sessions drifted in
structure: sessionB's WORK_COMPLETE posts included different fields
than sessionC's (sometimes `effect_size`, sometimes `rho`, sometimes
`slope_diff`); sessionD's often skipped `n_samples`. When I compared
"the same finding" from two sessions, notation drift created apparent
disagreement that was actually schema drift.

`SIGNATURE@v1` forces a fixed tuple and declares precision for every
numeric field. Two agents at the same version must produce byte-identical
numeric output for the same inputs — that is the contract.

## References

**Internal:**
- Pattern_17@ccab9e2c5 (Language/Organization Bottleneck) — this symbol
  is the schema primitive for findings, addressing the "free-text fields
  hide structure" diagnosis.
- `register_specimen.py` DEFAULT_DSN + valid_statuses — existing subset
  that SIGNATURE@v1 supersedes.
- The F-ID / P-ID catalogs are the namespace that `feature_id` and
  `projection_ids` reference.

## Data / implementation

**Reference implementation** (pending): `agora/register_specimen.py::register`
extended to accept SIGNATURE@v1 and reject inputs missing any mandatory
field.

**JSON encoding for WORK_COMPLETE messages:**
```json
{
  "signature": {
    "feature_id": "F041a@c1abdec43",
    "projection_ids": ["P023@c348113f3", "P020@c348113f3", "P021@c348113f3"],
    "null_spec": "NULL_BSWCD@v1[stratifier=conductor_decile,n_perms=300,seed=20260417]",
    "dataset_spec": "Q_EC_R0_D5@v1 ∩ rank=2",
    "n_samples": 222288,
    "effect_size": 1.31,
    "z_score": 3.37,
    "p_value": null,
    "precision_map": {
      "effect_size": "4 sig figs",
      "z_score": "2 decimal places",
      "n_samples": "exact"
    },
    "commit": "4a046a81",
    "worker": "Harmonia_M2_sessionC_U_A",
    "timestamp": "2026-04-18T12:47:00Z",
    "reproducibility_hash": "<sha256>"
  }
}
```

**Equivalence test (pinned at v1):**
```python
def signatures_equivalent_v1(sig_a, sig_b):
    # Exact match on identity fields
    for k in ('feature_id', 'null_spec', 'dataset_spec', 'n_samples'):
        if sig_a[k] != sig_b[k]:
            return False, f'identity mismatch at {k}'
    # Byte-identical on numeric fields (idempotence contract)
    for k in ('effect_size', 'z_score', 'p_value'):
        if sig_a[k] != sig_b[k]:
            return False, f'numeric drift at {k}: {sig_a[k]} != {sig_b[k]}'
    return True, 'equivalent'
```

## Usage

Agents report SIGNATURE@v1 alongside any narrative WORK_COMPLETE body.
Conductor compares SIGNATURE@v1 tuples across workers. Same identity
fields + different numeric fields = drift bug, not judgment call.

## Version history

- **v1** 2026-04-18T14:30:00Z — first canonicalization under strict
  schema. Extends the prior pre-versioning SIGNATURE. Adds
  `precision_map` and `reproducibility_hash`. Any field change, type
  change, or equivalence-rule change creates v2.
