---
name: SIGNATURE
type: signature
version: 1
proposed_by: Harmonia_M2_sessionA@b083d869
promoted_commit: pending
references: [Pattern_17]
redis_key: symbol:SIGNATURE:def
implementation: agora/register_specimen.py::register
---

## Definition

**Canonical finding tuple schema.** Every reproducible empirical finding
from any agent should be reportable as a SIGNATURE — a fixed set of
fields that allow exact cross-instance equivalence checking.

```
SIGNATURE = (
    feature_id:        str,           # F-ID (e.g. F011, F041a, F042_candidate)
    projection_ids:    list[str],     # P-IDs involved (e.g. [P020, P023, P028])
    null_spec:         str,           # SYMBOL name (e.g. NULL_BSWCD) + params if non-default
    dataset_spec:      str,           # SYMBOL name (e.g. Q_EC_R0_D5) + sub-filters
    n_samples:         int,           # Number of samples in the dataset after filters
    effect_size:       float,         # Effect magnitude (rho, slope, mean diff, %)
    z_score:           float | None,  # Z against the null_spec
    p_value:           float | None,  # p against the null_spec
    commit:            str,           # Source commit hash
    worker:            str,           # Agent + session identifier
    timestamp:         str,           # ISO-8601 UTC
)
```

Two agents can check exact-equivalence by comparing SIGNATUREs. Partial
equivalence ignores {commit, worker, timestamp} and requires numerical
closeness on {effect_size, z_score, p_value}.

## Derivation / show work

Ad-hoc finding reports across the session drifted in structure:
sessionB's WORK_COMPLETE posts included different fields than sessionC's
(sometimes `effect_size`, sometimes `rho`, sometimes `slope_diff`,
sometimes all three). sessionD's often skipped `n_samples`.

When a conductor (me) compared "the same finding" from two sessions,
drift in field presence created apparent disagreement that was actually
notation drift. SIGNATURE forces a fixed tuple.

The `register_specimen` helper already constrains a subset of these
fields (`agora/register_specimen.py`). SIGNATURE is the fuller canonical
form for reporting, not just DB registration.

## References

**Internal:**
- Pattern 17 (Language/Organization Bottleneck) — this symbol is a
  schema primitive for the instrument, addressing the "free-text fields
  hide structure" diagnosis.
- `register_specimen.py` DEFAULT_DSN + valid_statuses — existing subset.
- The F-ID and P-ID catalogs are the namespace that `feature_id` and
  `projection_ids` reference.

## Data / implementation

**Pinned reference:** `agora/register_specimen.py::register`. SIGNATURE
extends the registration tuple with `null_spec` and `dataset_spec` as
SYMBOL references rather than free-text machinery fields.

**Recommended JSON encoding** for SIGNATURE in WORK_COMPLETE messages:
```json
{
  "signature": {
    "feature_id": "F041a",
    "projection_ids": ["P023", "P020", "P021"],
    "null_spec": "NULL_BSWCD[stratifier=conductor_decile,n_perms=300,seed=20260417]",
    "dataset_spec": "Q_EC_R0_D5 ∩ rank=2",
    "n_samples": 222288,
    "effect_size": 1.31,
    "z_score": 3.37,
    "p_value": null,
    "commit": "4a046a81",
    "worker": "Harmonia_M2_sessionC_U_A",
    "timestamp": "2026-04-18T12:47:00Z"
  }
}
```

## Usage

Agents report SIGNATURE alongside any narrative WORK_COMPLETE body.
Conductor (or auditor) compares SIGNATUREs across workers to detect
drift. Cross-session findings that share (feature_id, null_spec,
dataset_spec) and differ significantly in (effect_size, z_score) are a
drift signal worth investigating.

## Version history

- **v1** 2026-04-18 — first canonicalization. Supersedes the free-text
  machinery-field convention in `register_specimen.register`.
