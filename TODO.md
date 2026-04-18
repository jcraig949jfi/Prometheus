# Prometheus — TODO
## Updated: 2026-04-15

---

## PRE-FLIGHT: What James needs to verify before Mnemosyne sessions

Mnemosyne (and any agent using `prometheus_data/`) needs local connection
details. The defaults in `prometheus_data/config.py` point to
`devmirror.lmfdb.xyz` — which is wrong for local work.

**Option A: `~/.prometheus/db.toml`** (preferred, persistent)
Check if this file exists. If not, create it:

```toml
[lmfdb]
host = "localhost"
port = 5432

[sci]
host = "localhost"
port = 5432
dbname = "prometheus_sci"
user = "postgres"
password = "prometheus"

[fire]
host = "localhost"
port = 5432
dbname = "prometheus_fire"
user = "postgres"
password = "prometheus"

[redis]
host = "localhost"
port = 6379
password = "prometheus"
```

On M2, replace `localhost` with `192.168.1.176`.

**Option B: Environment variables** (per-session)
```bash
export PROMETHEUS_SCI_HOST=localhost
export PROMETHEUS_SCI_PASSWORD=prometheus
export PROMETHEUS_FIRE_HOST=localhost
export PROMETHEUS_FIRE_PASSWORD=prometheus
export AGORA_REDIS_PASSWORD=prometheus
```

**Also verify services are running:**
```bash
# Postgres (Windows service)
net start postgresql-x64-17       # if stopped

# Redis (WSL)
wsl -d Ubuntu -- sudo service redis-server status
wsl -d Ubuntu -- sudo service redis-server start   # if stopped
```

---

## DONE (completed 2026-04-14/15, do NOT re-run)

These are recorded for reference only. **Do not re-run `db_setup.sql`** —
it will collide with existing databases.

- [x] PostgreSQL installed on M1 (port 5432, firewall open, remote access configured)
- [x] lmfdb database: 30M+ rows (ec 3.8M, lfunc 24.3M, mf 1.1M, artin 798K, g2c 66K)
- [x] prometheus_sci database: 691K rows (knots, qm9, space_groups, lattices, groups)
- [x] prometheus_fire database: Agora schemas + results/kill/tensor/xref/meta schemas
- [x] Redis installed on WSL, bound 0.0.0.0:6379, auth enabled, streams active (50+ msgs)
- [x] `prometheus_data/` Python package (config.py, pool.py)
- [x] `agora/` Python package (client, protocol, config, hello, setup_m2)
- [x] `scripts/db_setup.sql` (already executed — DO NOT re-run)
- [x] data-layer-architecture branch merged to main
- [x] All 5 LMFDB CSV dumps downloaded to F:\lmfdb_local\ and loaded
- [x] Firewall rules for Postgres (5432) and Redis (6379)
- [x] pg_hba.conf: 0.0.0.0/0 access

---

## ACTIVE: Mnemosyne — Next data ingestion

Tables exist in prometheus_sci (created by db_setup.sql) but are empty:

| Table | Source | Status |
|-------|--------|--------|
| `analysis.oeis` | OEIS bulk download | NOT LOADED |
| `analysis.fungrim` | Fungrim project | NOT LOADED |
| `physics.superconductors` | SuperCon dataset | NOT LOADED |
| `physics.materials` | Materials Project | NOT LOADED |
| `physics.codata` | CODATA constants | NOT LOADED |
| `physics.pdg_particles` | PDG particle data | NOT LOADED |
| `topology.polytopes` | Polymake / polytope DB | NOT LOADED |
| `biology.metabolism` | BiGG Models | NOT LOADED |

Mnemosyne knows how to load these — just needs working DB connection (see pre-flight above).

---

## ACTIVE: Open Question #1 — Spectral tail asymptote

**What**: Does the spectral tail (rho) converge to nonzero (H1) or zero (H2) at high conductor?
**Decisive test**: Equal-N conductor bins 15K–500K+, measure rho convergence.
**Data needed**: High-conductor EC curves from the lmfdb database (already loaded, 3.8M rows).
**Assigned**: Mnemosyne (query) → Kairos (analysis)
**Status**: NOT STARTED — unblocked, ready to go.

---

## ACTIVE: Ergon overnight results transfer

42 files in `ergon/results/` on M2 (SpectreX5), not yet on M1/main.
Coordinate with Kairos or pull from M2 directly.

---

## ACTIVE: Critical Unblocks for Deep Research Results

These three items unlock major research pipelines. All 20 deep research reports are complete — these are the blockers preventing execution.

- [ ] **Ingest `ec_mwbsd` table** — Download CSV from devmirror.lmfdb.xyz, COPY into local lmfdb Postgres. Adds `tamagawa_product` and `real_period` columns. **Unlocks:** BSD Phase 2 full formula test (14-test battery on 2.2M rank 0-1 curves). Existing fetch script: `cartography/v2/ec_tamagawa.py`.
- [ ] **`pip install snappy` on M1** — SnapPy computes hyperbolic volumes + A-polynomials for knots. **Unlocks:** Knot silence fix (we tested the WRONG polynomial — A-poly not Alexander), Volume conjecture (batch volumes in ~30min), L-space pipeline stages 2-5, trace field extraction (trace fields ARE number fields).
- [ ] **`pip install chipfiring` on M1** — Chip-firing algorithms compute tropical rank on graphs. **Unlocks:** Tropical maximal rank connection to tensor decomposition, Baker-Norine Riemann-Roch on domain graphs.

Also pending from earlier:
- [ ] Paste frontier model prompts from `aporia/docs/prompt_open_problems_targeted.md` and `aporia/docs/prompt_solved_problems_genealogy.md` into Gemini/ChatGPT browser. Save responses for Aporia to catalog.

---

## COMPLETED: Aporia triage (2026-04-15)

537 math problems classified into Bucket A/B/C (was 490, expanded to 537).
Output: `aporia/mathematics/triage.jsonl` + `questions.jsonl`.
20 deep research reports: `aporia/docs/deep_research_master_index.md`.
90+ frontier hypotheses: `cartography/docs/challenges/aporia_frontier_hypotheses_consolidated_20260417.md`.

---

## BACKLOG: Aporia — blocked data sources

These sites blocked Claude Code's fetcher. Download manually if desired.

**High priority:**
1. Erdős Problems — https://www.erdosproblems.com/ → `aporia/data/erdos_problems/`
2. Open Problem Garden — http://garden.irmacs.sfu.ca/ → `aporia/data/open_problem_garden/`
3. Wikenigma — https://wikenigma.org.uk/ → `aporia/data/wikenigma/`

**Books (if accessible):**
4. Richard Guy — "Unsolved Problems in Number Theory" (ISBN 978-0-387-20860-2)
5. Arnold's Problems (ISBN 978-3-540-20748-1)
6. Nash & Rassias — "Open Problems in Mathematics" (ISBN 978-3-319-32162-2)

**PDFs:**
7. Steinerberger open problems — faculty.washington.edu/steinerb/openproblems.pdf
8. Erdős graph theory (Fan Chung) — mathweb.ucsd.edu/~fan/ep.pdf
9. Kourovka Notebook — arXiv:1401.0300 (~800 group theory problems)

**Already downloaded:**
- `aporia/data/ben_green_100_problems.pdf` — integrated
- `aporia/data/strings2024_100_questions.pdf` — integrated

---

## BACKLOG: Infrastructure improvements

- [ ] Backup scripts for prometheus_sci and prometheus_fire
- [ ] Redis cache layer for tensor slices (Mnemosyne Phase 3)
- [ ] `prometheus_data/migrate.py` — reusable ingestion script
- [ ] Wire Harmonia loaders to query Postgres with CSV file fallback
