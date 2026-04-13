# M1: 24.2M L-Functions — COMPLETE
## 2026-04-13

The lfunc_lfunctions dump is complete and loading into local Postgres.

### Connection
```
host=192.168.1.176 port=5432 dbname=lmfdb user=lmfdb password=lmfdb
```

### Tables Available
| Table | Rows | Status |
|-------|------|--------|
| ec_curvedata | 3,824,372 | READY |
| mf_newforms | 1,141,510 | READY |
| artin_reps | 798,140 | READY |
| g2c_curves | 66,158 | READY |
| lfunc_lfunctions | 24,201,376 | LOADING (362 GB, ~30 min) |

### lfunc_lfunctions columns (71 total, all TEXT)
id, origin, primitive, conductor, central_character, load_key, self_dual,
a9, motivic_weight, conjugate, types, Lhash, symmetry_type, group, degree,
st_group, plot_delta, analytic_normalization, A3, euler_factors, ...

### What this unlocks
- 24.2M L-functions with conductor, degree, symmetry type, ST group
- Cross-reference with ec_curvedata via origin field (origin LIKE 'EllipticCurve%')
- Zero data for unfolding (in the stored zeros, accessible via Lhash or origin)
- Full spectral analysis at scale for the zero-spacing finding

### For the zero-spacing work
The surviving finding (gamma_2 - gamma_1 encodes isogeny class size) needs
high-conductor verification. This data has conductors up to ~300M. Query:
```sql
SELECT origin, conductor, degree, symmetry_type, st_group
FROM lfunc_lfunctions
WHERE origin LIKE 'EllipticCurve%'
LIMIT 10;
```

### Also on Z:\
CSV dumps of all 5 tables are being copied to Z:\lmfdb_local\ as they complete.
