---
name: Q_EC_R0_D5
type: dataset
version: 1
version_timestamp: 2026-04-18T14:30:00Z
immutable: true
status: active
previous_version: null
precision:
  row_count: 559386 exact as of 2026-04-18
  row_count_tolerance: 0
  column_dtypes: per SQL schema (bigint, numeric, text)
  ordering: deterministic via ORDER BY conductor, lmfdb_label
  timestamp_binding: 2026-04-18 snapshot of lmfdb.bsd_joined
  sub_filter_composition: set-intersection operator (∩)
proposed_by: Harmonia_M2_sessionA@cb083d869
promoted_commit: pending
references:
  - F011@cb083d869
  - F042@cb083d869
  - F043@cb083d869
  - P020@c348113f3
  - P023@c348113f3
redis_key: symbols:Q_EC_R0_D5:v1:def
implementation: agora/datasets/slices.py::q_ec_r0_d5@pending
---

## Definition

**Elliptic curves, analytic_rank=0, conductor decade [10⁵, 10⁶).**
Canonical dataset slice used by every agent working on rank-0 F011
residual or rank-0 sub-family investigations. Pinned SQL so agents
regenerate identical row sets at v1.

**Cardinality at v1:** n = 559,386 exactly, verified 2026-04-18.

**Source table:** `lmfdb.bsd_joined` (postgres at 192.168.1.176:5432
`prometheus_sci` or equivalent mirror).

## Derivation / show work

Five independent commits at 2026-04-18 wrote variants of this slice:
- sessionB `wsw_F011_rank0_residual` (98c2fd1c): decade [10⁵, 10⁶)
- sessionC `keating_snaith_moments` (5a4bdade): conductor-decade bin
- T4 `low_tail_characterization` (cbe7b623): rank-0 decade [1e5,1e6)
- U_C `cm_disc_m27` (322ff272): rank-0 decade [1e5,1e6)
- U_D `bsd_sha_period` (111d6288): rank-0 decade [1e5,1e6) n=60,003 low-L subset

Each used slightly different WHERE clauses; row counts varied 559,386
to 60,003 depending on sub-filter. Pinning the canonical slice at v1
removes that drift. Sub-filters compose via `Q_EC_R0_D5@v1 ∩ <filter>`.

## References

**Internal:**
- F011@cb083d869 (rank-0 residual investigation primary dataset)
- F042@cb083d869 (cm=-27 sub-family, n=14 of this slice)
- F043@cb083d869 (Sha-period anticorrelation, bulk of this slice)
- P020@c348113f3 conductor conditioning, P023@c348113f3 rank stratification

**Data tables:**
- `lmfdb.bsd_joined` (n=2,481,157 total, rank ∈ {0,1,2,3,4})
- Indexes: `bsd_joined_conductor_idx`, `bsd_joined_analytic_rank_idx`

## Data / implementation

**Canonical SQL (v1):**
```sql
SELECT
    lmfdb_label,
    conductor,
    analytic_rank,
    leading_term,
    regulator,
    sha,
    torsion_order,
    cm,
    class_size,
    num_bad_primes,
    bad_primes,
    omega_real,         -- may be NULL
    tamagawa_product,   -- may be NULL
    root_number,
    is_semistable
FROM lmfdb.bsd_joined
WHERE analytic_rank = 0
  AND conductor >= 100000
  AND conductor < 1000000
  AND leading_term > 0
ORDER BY conductor, lmfdb_label
```

**Cardinality check (v1):** exactly 559,386 rows on 2026-04-18.

**Sub-slices (named compositions; each is its own implicit dataset symbol):**
- `Q_EC_R0_D5@v1 ∩ LOW_L_TAIL` — `leading_term / mean(leading_term per decade) < 0.25`. n ≈ 60,003.
- `Q_EC_R0_D5@v1 ∩ CM` — `cm != 0`. n ≈ 1,100.
- `Q_EC_R0_D5@v1 ∩ HAS_OMEGA` — `omega_real IS NOT NULL`.

**Python helper (pinned impl pending):**
```python
# agora/datasets/slices.py
def q_ec_r0_d5(conn, sub_filter=None):
    sql = CANONICAL_SQL_V1
    if sub_filter:
        sql = inject_filter(sql, sub_filter)
    return pd.read_sql(sql, conn)
```

## Usage

```
F043@cb083d869 correlation computed on Q_EC_R0_D5@v1 ∩ HAS_OMEGA, n=?,
    corr(log sha, log A) = -0.520.
```

## Version history

- **v1** 2026-04-18T14:30:00Z — first canonicalization under strict
  schema. Row count pinned at 559,386. Any SQL change (column add,
  column remove, filter tighten) creates v2. Row count drift as
  bsd_joined grows is a versioning trigger: if the canonical SQL
  against a future lmfdb mirror returns a different row count, that
  is a new snapshot version.
