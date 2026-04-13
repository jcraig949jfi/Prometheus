# LMFDB Postgres Clone — Both Machines
## Clone the full database. Build loaders directly from Postgres.

### Connection
```
Host: devmirror.lmfdb.xyz
Port: 5432
User: lmfdb
Password: lmfdb
Database: lmfdb
```

### M1: Full clone
```bash
pg_dump -h devmirror.lmfdb.xyz -U lmfdb -d lmfdb -Fc -f lmfdb_full.dump
createdb lmfdb_local
pg_restore -d lmfdb_local lmfdb_full.dump
```

### M2: Targeted tables (clone in parallel)
```bash
# Priority 1: L-functions (22.3M records — the motherlode)
pg_dump -h devmirror.lmfdb.xyz -U lmfdb -d lmfdb -t lfunc_lfunctions -Fc -f lfunc.dump

# Priority 2: Artin representations (790K — Galois to L-functions bridge)
pg_dump -h devmirror.lmfdb.xyz -U lmfdb -d lmfdb -t artin_reps -Fc -f artin.dump

# Priority 3: Full EC data
pg_dump -h devmirror.lmfdb.xyz -U lmfdb -d lmfdb -t ec_curvedata -Fc -f ec_full.dump

# Priority 4: All newforms with Hecke
pg_dump -h devmirror.lmfdb.xyz -U lmfdb -d lmfdb -t mf_newforms -Fc -f mf_newforms.dump

# Priority 5: Full genus-2
pg_dump -h devmirror.lmfdb.xyz -U lmfdb -d lmfdb -t g2c_curves -Fc -f g2c.dump
```

### After clone: build Harmonia loaders
Each table becomes a domain loader in `harmonia/src/domain_index.py` reading from local Postgres instead of JSON files. Pattern:

```python
import psycopg2

def load_lfunctions(host='localhost', limit=100000):
    conn = psycopg2.connect(host=host, dbname='lmfdb_local', user='lmfdb')
    cur = conn.cursor()
    cur.execute('''
        SELECT label, conductor, degree, motivic_weight, ...
        FROM lfunc_lfunctions
        WHERE conductor IS NOT NULL
        LIMIT %s
    ''', (limit,))
    ...
```

### Target table sizes
| Table | Records | Key fields | Domain name |
|-------|---------|-----------|-------------|
| lfunc_lfunctions | 22.3M | conductor, degree, motivic_weight, sign, zeros | lfunctions |
| artin_reps | 790K | dimension, conductor, galois_group, frobenius | artin |
| ec_curvedata | ~400K | conductor, rank, torsion, regulator, sha | ec_full |
| mf_newforms | ~100K | level, weight, dim, char_order, hecke | mf_full |
| g2c_curves | 66K | conductor, disc, st_group, end_alg, igusa | g2c_full |
