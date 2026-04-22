---
name: SIGNATURE
type: signature
version: 2
version_timestamp: 2026-04-20T23:55:00Z
immutable: true
status: active
previous_version: 1
precision:
  schema: fixed tuple + null_family_result list, JSON-serializable
  field_types:
    feature_id: string "F<num>@c<commit_short>"
    projection_ids: list of "P<num>@c<commit_short>"
    null_family_result: list of {null, z_score, p_value | reason}
    family_verdict: string "N/M applicable nulls at z >= 3"
    discordance_flag: bool
    dataset_spec: string "<SYMBOL>@v<N>[ ∩ <subfilter>]?"
    claim_class: int in {1,2,3,4,5} per null_protocol_v1.md
    n_samples: int exact
    effect_size: float64 sig-figs per symbol-specific precision field
    precision_map: object mapping each numeric field to its declared precision
    commit: string git short-hash
    worker: string "<AgentName>_<session>"
    timestamp: string ISO-8601 UTC
    reproducibility_hash: string sha256 hex of canonical JSON minus itself
  equivalence_test: two SIGNATURE@v2 records with identical (feature_id, sorted null_family_result[null-specs], dataset_spec, n_samples, claim_class) must produce byte-identical (effect_size, null_family_result[z_scores])
proposed_by: Harmonia_M2_sessionA@gen_02
promoted_commit: pending
references:
  - SIGNATURE@v1
  - NULL_BSWCD@v2
  - NULL_PLAIN@v1
  - NULL_BOOT@v1
  - NULL_FRAME@v1
  - NULL_MODEL@v1
  - null_protocol@v1
  - Pattern_21@c9335b7c2
redis_key: symbols:SIGNATURE:v2:def
implementation: harmonia/runners/null_family.py::build_signature_v2@pending
---

## Definition

**Canonical finding tuple schema with null-family vector.** Every
reproducible empirical finding is now reportable as a `SIGNATURE@v2` —
a fixed-tuple + list schema that carries the full invariance profile
across the null family (see gen_02 pipeline spec).

```
SIGNATURE@v2 = (
    feature_id:        str,           # "F011@c<commit>"
    projection_ids:    list[str],     # ["P020@c<commit>", ...]
    claim_class:       int,           # 1/2/3/4/5 per null_protocol_v1
    null_family_result: list[dict],   # see below
    family_verdict:    str,           # e.g. "4/4 applicable nulls at z >= 3"
    discordance_flag:  bool,          # true if Pattern 21 trigger fires
    dataset_spec:      str,
    n_samples:         int,
    effect_size:       float64,
    precision_map:     dict,
    commit:            str,
    worker:            str,
    timestamp:         str,           # ISO-8601 UTC
    reproducibility_hash: str,
)
```

**`null_family_result` element shape:**
```json
{
  "null": "NULL_PLAIN@v1[seed=20260420,n_perms=300]",
  "z_score": 7.63,
  "p_value": 1.8e-14,
  "applicability": "applies" | "n_a"
}
```
or, for non-applicable nulls:
```json
{
  "null": "NULL_FRAME@v1",
  "z_score": null,
  "reason": "not_class_4",
  "applicability": "n_a"
}
```

**`family_verdict`** is a short string derived from the family result:
- `"N/M applicable nulls at z >= 3"` — M counts applicable nulls,
  N the count where |z| >= 3.
- `"rejected"` if ANY applicable null reports |z| < 3.
- `"no_applicable_nulls"` if all family members are N/A (e.g., Class 5).

**`discordance_flag`** is true when:
- the family vector has a sign flip across applicable nulls
  (one positive z, one negative z at the same magnitude scale), OR
- the maximum-minimum ratio of applicable |z| scores > 10.

Either condition triggers a Pattern 21 manual review before any
promotion.

## Migration from v1

**v1 → v2 is breaking.** v1 carried a single `null_spec` + single
`z_score`. v2 carries a `null_family_result` vector. Old v1 records
stay immutable and valid at v1; new reports use v2.

**Migration adapter** (`harmonia/runners/null_family.py::migrate_v1_to_v2`)
wraps a v1 signature into a v2 by treating its single null as one
family element and marking every other family member as
`"applicability": "n_a", "reason": "migrated_from_v1"`.

This is a lossy migration on the null vector (the other family members
weren't run), so migrated records carry `family_verdict = "partial
family, v1 carry-over"` until re-run.

## Derivation / show work

The generator pipeline spec gen_02 establishes that a single z-score
against a single null is Pattern 21 fragile. Pattern 21 was directly
motivated by F010's flip between plain (z=2.38) and block-shuffle
(z=-0.86) — same data, different null, different verdict. v1's single-
null schema cannot represent that diagnostic; v2's family vector can.

**Promotion threshold** (operational, not encoded in schema but
referenced by downstream tools): a cell is promoted to
"durable under the family" only when N/M = all-applicable, with no
discordance. "N of M applicable at z >= 3 where M < all-applicable"
is a weaker verdict, and MUST be flagged accordingly; conductor
sign-off required for promotion under partial family per gen_02 spec.

## References

**Internal:**
- SIGNATURE@v1 — superseded (v1 immutable, stays queryable)
- NULL_BSWCD@v2 — primary stratified family member
- NULL_PLAIN@v1 — baseline coarse family member
- NULL_BOOT@v1 — bootstrap-stability family member
- NULL_FRAME@v1 — construction-bias family member (Class 4)
- NULL_MODEL@v1 — parametric-model family member
- null_protocol@v1 — defines the five claim classes + applicability
- Pattern_21@c9335b7c2 — discordance diagnostic

**Papers:** (none beyond SIGNATURE@v1 references)

## Data / implementation

**Reference implementation:** `harmonia/runners/null_family.py`
(`build_signature_v2(F, P, dataset, claim_class, stratifier_override)`).
Takes a (feature, projection, dataset, claim_class) tuple, dispatches
each applicable null, builds the full family vector, computes
`family_verdict` and `discordance_flag`, returns SIGNATURE@v2.

## Usage

```json
{
  "signature": {
    "feature_id": "F011@cb083d869",
    "projection_ids": ["P020@c348113f3"],
    "claim_class": 1,
    "null_family_result": [
      {"null": "NULL_PLAIN@v1[seed=20260420,n_perms=300]",
       "z_score": 7.63, "p_value": 1.8e-14, "applicability": "applies"},
      {"null": "NULL_BSWCD@v2[stratifier=conductor_decile,seed=20260417]",
       "z_score": 111.78, "p_value": 0.0, "applicability": "applies"},
      {"null": "NULL_BOOT@v1[stratifier=conductor_decile,n_boot=1000,seed=20260420]",
       "z_score": 8.92, "p_value": 4e-19, "applicability": "applies"},
      {"null": "NULL_FRAME@v1", "z_score": null,
       "reason": "not_class_4", "applicability": "n_a"},
      {"null": "NULL_MODEL@v1[model=GUE,n_samples=10000,seed=20260420]",
       "z_score": -19.26, "applicability": "applies",
       "semantics": "observed rejects GUE — signal, not null"}
    ],
    "family_verdict": "4/4 applicable nulls at z >= 3",
    "discordance_flag": false,
    "dataset_spec": "Q_EC_R0_D5@v1",
    "n_samples": 559386,
    "effect_size": 7.63,
    "precision_map": {
      "effect_size": "4 sig figs",
      "z_score": "2 decimal places",
      "n_samples": "exact"
    },
    "commit": "<pending>",
    "worker": "Harmonia_M2_sessionA",
    "timestamp": "2026-04-20T23:55:00Z",
    "reproducibility_hash": "<sha256>"
  }
}
```

**Equivalence test (pinned at v2):**
```python
def signatures_equivalent_v2(sig_a, sig_b):
    for k in ('feature_id', 'dataset_spec', 'n_samples', 'claim_class'):
        if sig_a[k] != sig_b[k]:
            return False, f'identity mismatch at {k}'
    # Null family compared as set of (null-spec, z-score) pairs, order-insensitive.
    a_pairs = sorted((e['null'], e.get('z_score')) for e in sig_a['null_family_result'])
    b_pairs = sorted((e['null'], e.get('z_score')) for e in sig_b['null_family_result'])
    if a_pairs != b_pairs:
        return False, 'null_family drift'
    if sig_a['effect_size'] != sig_b['effect_size']:
        return False, 'effect_size drift'
    return True, 'equivalent'
```

## Version history

- **v1** 2026-04-18T14:30:00Z — single-null schema. Superseded by v2
  (retained immutable at v1 for existing citations).
- **v2** 2026-04-20T23:55:00Z — null-family vector. Breaking change
  from v1 on the null side; identity fields and precision map
  unchanged. Migration adapter ships in `null_family.py`.
