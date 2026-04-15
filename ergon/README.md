# Ergon — Tensor-Native Hypothesis Search Engine

Ergon is the cheap, fast, evolutionary screening layer for Prometheus. It generates
millions of mathematical hypotheses via mutation/crossover, kills 99%+ with a
precomputed tensor and inline battery, and promotes survivors to Harmonia for deep
structural analysis.

## Three-Stage Pipeline

```
Stage 1: ERGON (screening)        Stage 2: HARMONIA (structure)     Stage 3: BATTERY (prosecution)
  Random mutation + MAP-Elites      TT-Cross bond analysis            Full F1-F38 gauntlet
  ~5 hyp/s, kills 50%+ at F1       Ungated distributional scorer     Minutes per candidate
  Shadow archive maps failures      Finds bond dimensions             Only earned survivors
  Cost: electricity only            Cost: seconds per pair            Cost: minutes per pair
```

## Architecture

```
ergon/
  tensor_builder.py        Build (58K, 28) numpy tensor from 7 active domains
  tensor_executor.py       Hypothesis -> tensor slices -> coupling -> battery
  autonomous_explorer.py   Evolutionary loop + structured logging + shadow archive
  constrained_operators.py Domain-aware mutation (no invalid feature/domain combos)
  shadow_archive.py        Negative space map — dead zones, gradient zones, kill patterns
  harmonia_bridge.py       Promote MAP-Elites survivors to Harmonia TT-Cross
  monitor.py               Real-time dashboard for overnight runs
  run_overnight.bat        10K generation batch run + auto-bridge to Harmonia
  tensor.npz               Cached tensor (~305 KB)
  results/                 Archives, shadows, checkpoints, bridge results, JSONL logs
  logs/                    Structured JSONL per run (every generation logged)
  docs/                    Documentation
    phoneme_warning.md     WARNING: phoneme framework is unvalidated, don't extend it
    data_expansion_plan.md Plan for incremental domain growth (4 phases)
```

Imports shared components from `forge/v3/` (gene_schema, archive, kill_taxonomy).
Does not modify forge code.

## Data Pipeline

```
7 domains (58K objects)          tensor_builder.py           tensor.npz
  elliptic_curves (10K)    -->   Extract 28 features    -->  (58111 x 28) float32
  modular_forms (10K)            per domain/feature          ~6 MB in RAM
  number_fields (9K)             pair into columns           305 KB on disk
  genus2_curves (10K)
  maass_forms (5K)
  knots (10K)
  superconductors (4K)
```

Future: Ergon's tensor_builder will call Harmonia's `load_domains()` instead of
rolling its own loaders. This gives access to 43 domains. See `docs/data_expansion_plan.md`.

## Hypothesis Format

Each hypothesis is a fixed-schema JSON with controlled vocabularies (from `forge/v3/gene_schema.py`):

```
domain_a / domain_b:     which mathematical objects to compare
feature_a / feature_b:   which measurement from each domain
coupling:                 spearman / pearson / MI / KS / wasserstein
conditioning:             what to control for (none / log_conductor / rank / ...)
null_model:               how to generate the null distribution
resolution:               sample size (100 / 500 / 2000 / 5000 / 10000)
```

No LLM needed. `random.choice()` from controlled vocabularies. The evolutionary
algorithm (MAP-Elites) IS the intelligence — selection pressure does the thinking.

## Execution Flow

```
Hypothesis(domain_a, feature_a, domain_b, feature_b)
    |
    v
1. Kill taxonomy pre-filter    -- 21 known-dead patterns rejected instantly
2. F35 Megethos pre-filter     -- magnitude features without conditioning rejected
3. Tensor slice extraction     -- O(1) column lookup, no disk I/O
4. Coupling computation        -- spearman/pearson/MI/KS/wasserstein
5. Adaptive permutation null   -- 50 perms with early exit, up to 200 if promising
6. Progressive battery         -- 16 stages, kills early
    |
    v
Result: survival_depth, kill_test, z_score, coupling
    |
    v
Shadow archive records EVERYTHING (survivors AND failures)
MAP-Elites archive keeps best survivor per (domain_category, measurement_type) cell
```

## Shadow Archive

Every failure is data. The shadow archive maps the negative space:

- **Dead zones**: tested 10+ times, always depth 0-1. Confirmed empty.
- **Gradient zones**: high depth variance, boundary between dead and alive. Worth revisiting.
- **Kill heatmap**: which kill mode dominates each domain pair.
- **Confidence**: how many tests, how consistent the results.

## Harmonia Bridge

After an Ergon run, `harmonia_bridge.py` takes the MAP-Elites survivors and:

1. Extracts which domain pairs have survivors (aggregate across cells)
2. Runs Harmonia's TT-Cross on each pair (ungated, distributional scorer)
3. Reports bond dimensions (how many independent coupling axes)
4. Optionally runs falsification battery (6 tensor-speed tests)

Uses `distributional` scorer, NOT `phoneme`/`kosmos`. See `docs/phoneme_warning.md`.

## Usage

```bash
# Build tensor
python tensor_builder.py

# Run explorer (short test)
python autonomous_explorer.py --generations 100 --per-gen 20 --log-interval 10

# Overnight batch (10K generations + auto-bridge)
run_overnight.bat

# Monitor a running session
python monitor.py           # one-shot status
python monitor.py --watch   # refresh every 30s

# Bridge survivors to Harmonia
python harmonia_bridge.py results/archive_YYYYMMDD_HHMMSS.json --top-k 20

# Bridge with explore-only (no falsification, faster)
python harmonia_bridge.py results/archive_*.json --explore-only
```

## Performance

| Metric | forge/v3 | ergon |
|--------|----------|-------|
| Throughput | 9.3 hyp/s | ~5 hyp/s (with 16-stage battery) |
| Data loading | Per hypothesis (disk) | Once at startup (RAM) |
| Battery depth | 3 tests | 16 tests |
| Pre-filters | None | Kill taxonomy + Megethos |
| Memory | Unbounded | 6 MB fixed |
| Failure tracking | None | Shadow archive |

Note: Raw throughput appears lower than forge because Ergon runs 16 battery tests
vs forge's 3. Effective throughput per useful test is higher.

## Dependencies

From forge/v3: gene_schema.py, archive.py, kill_taxonomy.py
From cartography: falsification_battery.py (F1-F14), battery_v2.py (F15-F27)
From harmonia: domain_index.py, engine.py, tensor_falsify.py (via bridge only)

Data: charon/data/charon.duckdb, cartography/*/data/
Future: C:\prometheus_share\lmfdb_local\ (3.8M EC, 1.1M MF, 798K Artin)
