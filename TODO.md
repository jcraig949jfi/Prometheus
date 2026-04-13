# Prometheus — Master TODO List
## Updated: 2026-04-13

---

## URGENT: PostgreSQL Setup (needs admin PowerShell)

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
