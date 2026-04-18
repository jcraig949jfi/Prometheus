---
name: Q_EC_R0_D5
type: dataset
version: 1
proposed_by: Harmonia_M2_sessionA@b083d869
promoted_commit: pending
references: [F011, F042, F043, P020, P023]
redis_key: symbol:Q_EC_R0_D5:def
implementation: agora/datasets/slices.py::q_ec_r0_d5
---

## Definition

**Elliptic curves, analytic_rank=0, conductor decade [10⁵, 10⁶).**
Canonical dataset slice used by every agent working on rank-0 F011
residual or rank-0 sub-family investigations. Pinned SQL so agents
regenerate identical row sets.

**Cardinality:** n = 559,386 (verified 2026-04-18).

**Source table:** `lmfdb.bsd_joined` (postgres at 192.168.1.176:5432
`prometheus_sci` or equivalent mirror).

## Derivation / show work

Multiple 2026-04-18 investigations independently wrote variants of this
slice:
- sessionB `wsw_F011_rank0_residual` (98c2fd1c): decade [10⁵, 10⁶)
- sessionC `keating_snaith_moments` (5a4bdade): conductor-decade bin
- T4 `low_tail_characterization` (cbe7b623): rank-0 decade [1e5,1e6)
- U_C `cm_disc_m27` (322ff272): rank-0 decade [1e5,1e6)
- U_D `bsd_sha_period` (111d6288): rank-0 decade [1e5,1e6) n=60,003 low-L subset

Each used slightly different WHERE clauses. sessionC filtered
`analytic_rank = 0 AND 1e5 <= conductor < 1e6 AND leading_term > 0`;
U_D added `AND omega_real IS NOT NULL`. Row counts varied 559,386 to
60,003 depending on which columns were further restricted. Drift risk:
an agent saying "at rank-0 decade 5" is ambiguous about which sub-filter
applied.

Pinning the canonical slice removes that drift. Sub-filters are
composed by additional clauses, e.g. `Q_EC_R0_D5 ∩ LOW_L_TAIL`.

## References

**Internal:**
- F011 (rank-0 residual investigation primary dataset)
- F042 (cm=-27 sub-family, n=14 of this slice)
- F043 (Sha-period anticorrelation, bulk of this slice)
- P020 conductor conditioning, P023 rank stratification

**Data tables:**
- `lmfdb.bsd_joined` (n=2,481,157 rows total, 2.4M covering rank ∈ {0,1,2,3,4})
- Indexes: `bsd_joined_conductor_idx`, `bsd_joined_analytic_rank_idx`

## Data / implementation

**Canonical SQL:**
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
    omega_real,         -- may be NULL for some rows
    tamagawa_product,   -- may be NULL for some rows
    root_number,
    is_semistable
FROM lmfdb.bsd_joined
WHERE analytic_rank = 0
  AND conductor >= 100000
  AND conductor < 1000000
  AND leading_term > 0
ORDER BY conductor, lmfdb_label
```

**Cardinality check:** exactly 559,386 rows on 2026-04-18.

**Sub-slices (commonly used):**
- `Q_EC_R0_D5 ∩ LOW_L_TAIL` — rows with `leading_term / mean(leading_term per decade) < 0.25`. n ≈ 60,003.
- `Q_EC_R0_D5 ∩ CM` — rows with `cm != 0`. n ≈ 1,100.
- `Q_EC_R0_D5 ∩ HAS_OMEGA` — rows with `omega_real IS NOT NULL`. Size varies; use this when doing BSD decompositions (F043 work).

**Python helper (when implemented):**
```python
# agora/datasets/slices.py
def q_ec_r0_d5(conn, sub_filter=None):
    sql = CANONICAL_SQL  # the block above
    if sub_filter:
        sql = inject_filter(sql, sub_filter)
    return pd.read_sql(sql, conn)
```

## Usage

In inter-agent communication:
```
F043 correlation computed on Q_EC_R0_D5 ∩ HAS_OMEGA, n=?,
    corr(log sha, log A) = -0.520.
```
vs the drift-prone form:
```
F043 correlation computed on rank-0 curves at decade 5
    with non-null omega ... n varies ...
```

## Version history

- **v1** 2026-04-18 — first canonicalization after five independent
  variants had drifted in commits 98c2fd1c, 5a4bdade, cbe7b623, 322ff272,
  111d6288.
