# Ergon Handoff — Start Here
## For the next Claude Code session
### 2026-04-14

---

## Current State

### Overnight run (still in progress)
- Run ID: `ergon_20260413_215133`
- 10,000 generations x 20 hyp/gen, seed 31068
- As of gen 6400: 81K tested, 21 cells, 602 dead zones, 1009 gradient zones
- ETA completion: ~5:30 AM, then auto-bridges to Harmonia
- Check status: `python ergon/monitor.py`
- Results will be in: `ergon/results/archive_*.json`, `ergon/results/shadow_*.json`

### What exists and works
- **Tensor executor**: 7 domains, 58K objects, 28 features, ~5 hyp/s with 16-stage battery
- **Shadow archive**: Tracks all failures — dead zones, gradient zones, kill patterns
- **Harmonia bridge**: Promotes survivors to TT-Cross + falsification. All tested pairs show real bond structure.
- **Constrained operators**: `constrained_operators.py` ready but NOT yet active in the run (will eliminate ~40% data_unavailable waste next run)
- **Structured logging**: JSONL per run, checkpoints every 1000 gens
- **Monitor**: `python monitor.py` or `python monitor.py --watch`

### What needs doing (in priority order)

#### 1. Check overnight results
```bash
python ergon/monitor.py
# Look at: shadow archive, final bridge results
```

#### 2. Phase 1: CSV fallback for Harmonia loaders (zero-risk)
Two functions in `harmonia/src/domain_index.py` need CSV fallback:
- `load_ec_rich` (line 1788) — Currently Postgres only. Fallback: `C:\prometheus_share\lmfdb_local\ec_curvedata.csv`
- `load_artin` (line 1849) — Currently Postgres only. Fallback: `C:\prometheus_share\lmfdb_local\artin_reps.csv`

Pattern: `try: postgres except: read CSV with same column mapping`
Same normalization, same DomainIndex output. No behavior change when Postgres is up.

#### 3. Phase 2: Upgrade data scale
Replace 10K extracts with full LMFDB exports:
- EC: 10K → 3.8M (`ec_curvedata.csv`, pipe-delimited)
- MF: 10K → 1.1M (`mf_newforms.csv`)
- G2: 10K → 66K (`g2c_curves.csv`)
- Artin: new domain, 798K (`artin_reps.csv`)

**MUST run calibration check after** (7 known theorems at 100.000%)

#### 4. Phase 3: Wire Ergon to Harmonia loaders
Replace `tensor_builder.py`'s hand-rolled loading with `harmonia.src.domain_index.load_domains()`.

#### 5. Phase 4: New domains from share
`C:\prometheus_share\cartography/` has: maass (335MB), physics (660MB), fungrim, mathlib, polytopes, spacegroups

See `ergon/docs/data_expansion_plan.md` for full details.

---

## WARNINGS

### Phoneme framework is UNVALIDATED
`harmonia/src/phonemes.py` defines 5 universal axes. This was a construction
hypothesis, not validated structure. Megethos (complexity axis) was explicitly killed.
- Do NOT extend `DOMAIN_PHONEME_MAP`
- Use `distributional` scorer, not `phoneme`/`kosmos`
- Stale docs may reference phonemes as fact — treat as historical
- See `ergon/docs/phoneme_warning.md`

### Don't break Harmonia
Harmonia is a nearly flawless instrument. Changes to `harmonia/src/` must:
- Not change any scoring behavior
- Not modify tensor_falsify.py logic
- Pass calibration check (7 theorems) after any data change
- Only add fallback paths, never replace working paths

### Data architecture
- Code: GitHub commits
- Big data: `C:\prometheus_share\` (shared between machines)
- Live DB: Postgres on M1 (`devmirror.lmfdb.xyz`)
- Local DB: `charon/data/charon.duckdb` (small extracts)
- Keep consistency across machines

---

## Key files to read first

1. `ergon/README.md` — Full architecture overview
2. `ergon/docs/data_expansion_plan.md` — The 4-phase plan
3. `ergon/docs/phoneme_warning.md` — What not to trust
4. `harmonia/src/domain_index.py` lines 1788-1898 — The two Postgres loaders to add CSV fallback
5. `C:\prometheus_share\lmfdb_local\` — The CSV data files (check headers with `head -1`)

## Key constraints
- 21 kills, 0 novel bridges, 1 weak survivor (spectral tail z=-25.7)
- 7 theorems at 100.000% on 3.8M objects (calibration anchor)
- Finding hierarchy: 3 conditional laws, 2 constraints, 1 exact identity, 0 universal laws
- Falsification-first: everything assumed false until every kill path exhausted
