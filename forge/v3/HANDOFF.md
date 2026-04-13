# Forge v3 Handoff — Start Here
## For the next Claude Code session
### 2026-04-13

---

## What exists

### Forge v3 (just built, operational)
- `forge/v3/gene_schema.py` — Hypothesis dataclass, 3.1B search space, mutation/crossover
- `forge/v3/kill_taxonomy.py` + `.db` — 21 kills in SQLite, queryable constraints
- `forge/v3/executor.py` — Hypothesis → data → coupling → permutation null → result
- `forge/v3/archive.py` — MAP-Elites grid (domain × measurement type)
- `forge/v3/autonomous_explorer.py` — Main loop, tested at 9.3 hyp/sec

### Harmonia tensor infrastructure (M1 built)
- `harmonia/src/domain_index.py` — 1769 lines, loads 27 domains into tensor
- `harmonia/src/coupling.py` — 298 lines, 4 coupling scorers
- `harmonia/src/phonemes.py` — 562 lines, 5D phoneme projection
- `harmonia/src/tensor_falsify.py` — 480 lines, tensor-speed battery (6 tests)
- `harmonia/src/engine.py` — 271 lines, TT-Cross engine
- `harmonia/src/landscape.py` — 351 lines, MAP-Elites explorer
- `harmonia/src/adversarial.py` — 471 lines, adversarial attack generator

### Battery (the Nemesis)
- `cartography/shared/scripts/battery_v2.py` — 1608 lines, F15-F32 + F25b/c + primitive tagger
- `cartography/shared/scripts/falsification_battery.py` — F1-F14
- `cartography/shared/scripts/cross_domain_protocol.py` — 7-layer automated gauntlet

### Data
- `charon/data/charon.duckdb` — 31K EC, 102K MF, 120K L-function zeros
- Live Postgres on M1: 3.8M EC (connection details in harmonia code)
- `cartography/*/data/` — 21+ mathematical datasets

---

## What to build

### The tensor-native executor

The current `forge/v3/executor.py` loads CSVs and computes features from scratch for every hypothesis. This is slow (9.3/sec) and CPU-bound.

**The goal:** Put ALL data in a single precomputed tensor so the executor becomes a tensor index operation (microseconds, not seconds).

**Architecture:**
1. `forge/v3/tensor_builder.py` — Pre-compute feature tensor:
   - For each active domain, extract all features from `gene_schema.ACTIVE_FEATURES`
   - Stack into one big matrix: (n_objects_total × n_features_total)
   - Store domain boundaries so you can index domain_a[feature_a]
   - Save as numpy .npz or torch tensor

2. `forge/v3/tensor_executor.py` — Replace the CSV-loading executor:
   - Load the precomputed tensor ONCE at startup
   - Each hypothesis maps to tensor indices: `tensor[domain_a_start:domain_a_end, feature_a_idx]`
   - Coupling = correlation/MI between two tensor slices
   - Permutation null = shuffle one slice, recompute (still in-memory, fast)
   - Battery tests become tensor operations

3. Wire the full F1-F38 battery into the tensor executor (currently only 3 tests)

4. Add F35 (Megethos kill) to automatically reject log_conductor × anything signals

5. Add kill taxonomy pre-filter: check hypothesis against 21 known kill patterns BEFORE executing

**Expected speedup:** 9.3/sec → 100+/sec (10x). Everything stays in RAM. No disk I/O per hypothesis.

**Memory estimate:** 7 domains × ~10K objects × ~7 features × 4 bytes ≈ 2 MB. Trivial. Even 100K objects × 51 features = 20 MB. The tensor fits easily.

### Scale targets
- Tonight: 1000 generations × 20 hyp = 20,000 hypotheses
- Tomorrow: 10,000 generations = 200,000 hypotheses
- This week: expand to all 24 domains, 51 features

---

## Key files to read first

1. `forge/v3/gene_schema.py` — The hypothesis format (start here)
2. `forge/v3/executor.py` — Current executor to replace with tensor version
3. `harmonia/src/domain_index.py` — How M1 loads domains into tensors (reuse this)
4. `cartography/shared/scripts/battery_v2.py` — The full battery to integrate

## Key documents
- `harmonia/docs/autonomous_explorer_architecture.md` — Full architecture design
- `harmonia/docs/local_intelligence_architecture.md` — Local 7B model plan
- `harmonia/docs/exploration_protocol_reform.md` — Why the battery must be separated from exploration
- `cartography/docs/meta_analysis_20260412.md` — Complete project state
- `roles/CrossDomainCartographer/journal_20260413_complete.md` — Today's full session

## The calibration bar
- 7 theorems at 100.000% on 3.8M objects
- 21 kills (every novel claim killed)
- 1 survivor (spectral tail z=-25.7, alpha=0.464)
- 40-test battery (F1-F38 + 5 layers)
