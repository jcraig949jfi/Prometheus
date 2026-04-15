# Prometheus — Master TODO List
## Updated: 2026-04-14

---

## ACTIVE: Database Architecture Deployment

Branch `data-layer-architecture` is pushed to GitHub. M1 needs to pull and set up.

### Overview

Three Postgres databases + Redis. One Python package (`prometheus_data/`) for all access.
Full design: `docs/database_architecture.md`

| Database | Purpose | Status |
|----------|---------|--------|
| **lmfdb** | Raw LMFDB mirror (existing) | RUNNING (read-only, 612 tables) |
| **prometheus_sci** | Normalized scientific data (knots, physics, chemistry, etc.) | NOT CREATED |
| **prometheus_fire** | Working data (results, kills, shadows, cross-refs, tensors) | NOT CREATED |
| **Redis** | Fast cache for tensor slices and kill lookups | NOT INSTALLED |

### Step 1: Pull branch on M1
```bash
cd ~/Prometheus
git fetch origin
git checkout data-layer-architecture
```

### Step 2: Run database setup on M1
```bash
sudo -u postgres psql -f scripts/db_setup.sql
```
This creates both databases, all schemas, all tables, roles, and users.
**Change the passwords** — search `CHANGE_ME` in the SQL file.

### Step 3: Update pg_hba.conf on M1
Add these lines to allow remote access from M2:
```
host prometheus_sci  all  0.0.0.0/0  scram-sha-256
host prometheus_fire all  0.0.0.0/0  scram-sha-256
```
Then: `sudo systemctl reload postgresql`

### Step 4: Install Redis on M1
```bash
sudo apt install redis-server
sudo systemctl enable redis-server
```
Edit `/etc/redis/redis.conf`:
```
bind 0.0.0.0
requirepass <choose-a-password>
maxmemory 512mb
maxmemory-policy allkeys-lru
```
Then: `sudo systemctl restart redis-server`

Open firewall: `sudo ufw allow 6379/tcp`

### Step 5: Create credentials on BOTH machines
Create `~/.prometheus/credentials.toml`:
```toml
[sci]
password = "<the password you set>"

[fire]
password = "<the password you set>"

[redis]
password = "<the password you set>"
```

### Step 6: Test from M2
```python
from prometheus_data import get_fire, get_sci, get_redis

with get_fire() as conn:
    cur = conn.cursor()
    cur.execute("SELECT 1")
    print("Fire:", cur.fetchone())

with get_sci() as conn:
    cur = conn.cursor()
    cur.execute("SELECT 1")
    print("Sci:", cur.fetchone())

r = get_redis()
print("Redis:", r.ping() if r else "not available")
```

### Step 7: Populate PrometheusSci
After databases are running, migrate data from JSON/CSV:
- Knots -> `topology.knots`
- Superconductors -> `physics.superconductors`
- QM9 -> `chemistry.qm9`
- Space groups -> `algebra.space_groups`
- etc.

Script: `prometheus_data/migrate.py` (to be written in Phase 2)

### Database Management

**Backups** (run on M1):
```bash
pg_dump -U postgres prometheus_sci > ~/backups/prometheus_sci_$(date +%Y%m%d).sql
pg_dump -U postgres prometheus_fire > ~/backups/prometheus_fire_$(date +%Y%m%d).sql
```

**Monitor connections**:
```sql
SELECT datname, usename, state, query_start FROM pg_stat_activity WHERE datname LIKE 'prometheus%';
```

**Check table sizes**:
```sql
\connect prometheus_fire
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema') ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Redis monitoring**:
```bash
redis-cli -a <password> info memory
redis-cli -a <password> info keyspace
redis-cli -a <password> dbsize
```

---

## ACTIVE: Ergon Overnight Run Results

Run completed (or completing) around 5:30 AM 2026-04-14.

### Check results
```bash
cd ergon
python monitor.py                    # Quick status
```

### Key output files
- `ergon/results/archive_*.json` — MAP-Elites survivors (bridge to Harmonia)
- `ergon/results/shadow_*.json` — Negative space map (dead zones, gradients)
- `ergon/results/bridge_*.json` — Harmonia falsification results
- `ergon/logs/ergon_*.jsonl` — Structured run log

### For the next Ergon run
The constrained operators (`constrained_operators.py`) are wired in and will
eliminate ~40% `data_unavailable` waste. Just run `run_overnight.bat` again.

---

## ACTIVE: Ergon Data Expansion (4 phases)

Full plan: `ergon/docs/data_expansion_plan.md`

| Phase | What | Status | Depends On |
|-------|------|--------|------------|
| 1 | CSV fallback for Harmonia Postgres loaders | NOT STARTED | Database setup |
| 2 | Upgrade data scale (3.8M EC, 1.1M MF, 798K Artin) | NOT STARTED | Phase 1 |
| 3 | Wire Ergon tensor_builder to Harmonia loaders | NOT STARTED | Phase 2 |
| 4 | Add new domains from share | NOT STARTED | Phase 3 |

---

## WARNING: Phoneme Framework

The 5-axis phoneme system in Harmonia (complexity, rank, symmetry, arithmetic,
spectral) is an **unvalidated construction**. Megethos (complexity) was explicitly
killed. Do NOT extend `DOMAIN_PHONEME_MAP` for new domains. Use `distributional`
scorer, not `phoneme`/`kosmos`. See `ergon/docs/phoneme_warning.md`.

Stale documentation may reference phonemes, islands, and Megethos/Arithmos axes
as established fact. Treat as historical hypothesis, not current truth.

---

## REFERENCE: Existing PostgreSQL Setup (M1 LMFDB mirror)

This section documents the EXISTING setup. The new databases (prometheus_sci,
prometheus_fire) are separate from this.

### LMFDB Mirror Setup (already done)

### Step 1: Install PostgreSQL
Open **admin PowerShell** (right-click -> Run as Administrator):
```powershell
F:\pg17_installer.exe --mode unattended --superpassword prometheus --serverport 5432 --datadir F:\pgdata --install_runtimes 0 --enable_acledit 1
```

### Step 2: Open firewall for M2
Same admin PowerShell:
```powershell
netsh advfirewall firewall add rule name="PostgreSQL" dir=in action=allow protocol=tcp localport=5432
```

### Step 3: Configure remote access
Edit `F:\pgdata\pg_hba.conf` — add this line at the end:
```
host    all    all    0.0.0.0/0    md5
```

Edit `F:\pgdata\postgresql.conf` — find `listen_addresses` and change to:
```
listen_addresses = '*'
```

### Step 4: Restart PostgreSQL
```powershell
net stop postgresql-x64-17
net start postgresql-x64-17
```

### Step 5: Create lmfdb database and user
```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql" -U postgres -c "CREATE DATABASE lmfdb;"
& "C:\Program Files\PostgreSQL\17\bin\psql" -U postgres -c "CREATE USER lmfdb WITH PASSWORD 'lmfdb';"
& "C:\Program Files\PostgreSQL\17\bin\psql" -U postgres -c "GRANT ALL ON DATABASE lmfdb TO lmfdb;"
```

### Step 6: Tell Claude Code to load data
Once Postgres is running, Claude Code will:
- Load the CSV dumps from `F:\lmfdb_local\` into the database
- The 5 target tables: g2c_curves, artin_reps, mf_newforms, ec_curvedata, lfunc_lfunctions
- Give M2 the connection string: `host=<M1_IP> port=5432 dbname=lmfdb user=lmfdb password=lmfdb`

---

## LMFDB Data Dump Status (pulling from devmirror.lmfdb.xyz)

| Table | Rows | File | Status |
|-------|------|------|--------|
| g2c_curves | 66K | 40 MB | DONE |
| artin_reps | 793K | 445 MB | DONE |
| mf_newforms | 1.1M | 8.0 GB | DONE |
| ec_curvedata | 3.8M | 1.8 GB | DONE |
| lfunc_lfunctions | 24.2M | ~43 GB est | IN PROGRESS (~6 hrs) |

Files at: `F:\lmfdb_local\`
Completed files also pushed to: `Z:\lmfdb_local\` for M2

---

## New Data Already Downloaded

| Dataset | Location | Size | Objects |
|---------|----------|------|---------|
| Exoplanets | cartography/physics/data/exoplanets/ | 694 KB | 6,158 |
| GW events | cartography/physics/data/gravitational_waves/ | 405 KB | 219 |
| Pulsars | cartography/physics/data/pulsars/ | 5.3 MB | 4,351 (511 columns!) |
| QM9 molecules | cartography/physics/data/qm9/ | 43 MB | 134K |

All pushed to Z:\ for M2.

---

## Push to Z:\ when done

These files need copying to Z:\ when they finish:
```powershell
copy F:\lmfdb_local\mf_newforms.csv Z:\lmfdb_local\
copy F:\lmfdb_local\ec_curvedata.csv Z:\lmfdb_local\
copy F:\lmfdb_local\lfunc_lfunctions.csv Z:\lmfdb_local\
```

---

## Session Summary (2026-04-12 to 2026-04-13)

### Infrastructure Built
- Dissection tensor v7: 601K objects x 182 dims, 19 domains, GPU-resident
- 15 strategy groups (the IPA features)
- 3 explorers (MAP-Elites, random walk, GA) + relay walker
- Tensor reasoner (local ollama + NemoClaw cloud)
- Geometric analysis suite (PCA, ICA, rotation, topology, Grassmannian, curvature)
- GPU tensor battery (F24/F25/F1 in 10 seconds)
- Kill-with-fire adversarial suite (8 tests)
- Base-e calibration pipeline
- Megethos large conductor sieve (LMFDB 85K curves)

### Key Findings
- Megethos b/a -> e^2 at 0.39% precision (85K curves to conductor 1.4M)
- 6,019 topological loops (rotation-invariant, real structure)
- 25 Grassmannian bridges between domain pairs
- Particle-EC bridge KILLED (6/8 adversarial kills — sparsity artifact)
- Alpha is projection-dependent, not universal (3 spaces, 3 values)
- PC1 of raw tensor is "fingerprint complexity" not Megethos (r=0.017)
- Mantel r=0.94 between 41D tensor and 5D phonemes (94% same geometry)
- ORC = 0.596 in 41D (positively curved manifold confirmed in both cameras)
- Euler chi = -30,687 (locally spherical, globally hyperbolic)
- Curvature FACILITATES transfer (r=+0.271, prediction was backwards)
- Island phonemes are genuinely independent (Topos, Auxesis = NEW VOICES)
- Every domain is a camera angle on the same positively-curved manifold
