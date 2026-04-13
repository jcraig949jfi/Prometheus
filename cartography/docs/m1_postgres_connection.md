# M1 Local PostgreSQL — Connection Info
## 2026-04-13

### Connection String
```
host=192.168.1.176 port=5432 dbname=lmfdb user=lmfdb password=lmfdb
```

### Python
```python
import psycopg2
conn = psycopg2.connect(host='192.168.1.176', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
```

### Tables Available

| Table | Rows | Status |
|-------|------|--------|
| g2c_curves | 66,158 | READY |
| artin_reps | 798,140 | READY |
| mf_newforms | 1,141,510 | READY |
| ec_curvedata | 3,824,372 | READY |
| lfunc_lfunctions | 24,201,376 | LOADING (dump in progress, ~6 hrs from start) |

All columns are TEXT type (loaded from CSV). Cast as needed.

### Superuser (for admin only)
```
user=postgres password=prometheus
```
