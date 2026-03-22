# Project AETHON — Autonomous Unsupervised Reasoning Archaeology

**Evolving novel reasoning architectures in local LLMs and detecting emergent cognitive properties.**

Project AETHON uses evolutionary search (MAP-Elites) to explore the space of possible reasoning configurations for large language models. Rather than optimizing for a known objective, it maximizes *structured novelty* — discovering diverse reasoning strategies that produce qualitatively different outputs. A self-monitoring layer detects when the system surprises itself, capturing anomalous configurations for characterization as potential emergent behaviors.

## Why This Exists

Emergence in complex systems produces properties not predictable from components. Any research program that pre-specifies what it's looking for will miss genuinely emergent phenomena. AETHON takes a different approach: evolve reasoning architectures under novelty-driven selection pressure, instrument the system to detect its own surprises, and characterize captured anomalies through transfer, ablation, and reproducibility testing.

The core genome encodes ordered sequences of reasoning modules — chain-of-thought, adversarial debate, Socratic questioning, Bayesian updating, and six others — with parameters controlling depth, iteration count, and temperature. Evolution discovers combinations that produce outputs no individual module could generate alone. The self-monitoring layer learns the system's own input→output mapping and flags configurations where actual behavior diverges from predicted behavior, triggering a four-tier characterization battery that classifies anomalies as noise, input-specific, module-reducible, or candidate-emergent.

This is not consciousness research in the traditional sense. It's an empirical search for structured regularities in how reasoning systems deviate from expected behavior — phenomena that may represent internal dynamics we are not currently modeling.

## Quick Start

```bash
# Clone and install
git clone <repo-url> && cd Aethon
pip install -e .

# Pull models via Ollama
ollama pull qwen2.5:7b
ollama pull llama3.1:8b

# Run your first experiment (MVP-1, 10 generations for a quick test)
python -m aethon.evolution --generations 10 --pop-size 10

# Run with a YAML config
python -m aethon.evolution --config configs/default.yaml

# Run MVP-2 with self-monitoring
python -m aethon.evolution_v2 --config configs/mvp2_default.yaml --generations 10

# Generate a dashboard from results
python -m aethon.dashboard --run-dir archive/ --output reports/dashboard.html

# Analyze results
python -m aethon.analyze --archive-path archive/map_elites.json --embedding-path archive/embeddings.npz --skip-mlflow
```

## Current Status (March 2026)

**Phase 3 — Calibration and Validation.** Running a 4-seed replication study on two model substrates (Llama 3.1 8B, Qwen 2.5 7B) to test whether convergent reasoning motifs replicate across independent evolutionary runs. Llama series (4 seeds) complete. Qwen series: seeds 1–2 complete, seed 3 in progress, seed 4 pending.

| Metric | Value |
|---|---|
| Source modules | 23 files, ~7,700 lines |
| Test files | 18 files, ~3,600 lines |
| Tests collected | 256 |
| Experiment configs | 18 (10 real, 4 null, 2 threshold variants, 2 specialty) |
| Completed archives | 7 (4 Llama, 2 Qwen, 1 null baseline) |
| Active runs | 1 (qwen_seed3) |

See `docs/AETHON_OPERATIONS.md` for daily routines, monitoring commands, and the full experiment registry.

## Architecture

```
src/aethon/
├── genome.py           # Genome representation: ModuleType enum, ReasoningModuleGene dataclass
├── execution.py        # Ollama execution pipeline: prompt chain rendering, API calls
├── fitness.py          # Novelty + coherence fitness, embedding engine, ArchiveStore
├── archive.py          # MAP-Elites quality-diversity archive with behavioral descriptors
├── evolution.py        # MVP-1 DEAP evolutionary loop with MAP-Elites
├── evolution_v2.py     # MVP-2 loop with self-monitoring and anomaly detection
├── monitor.py          # ExecutionMonitor, SelfPredictor, AnomalyDetector, AnomalyCapture
├── characterization.py # Transfer, ablation, reproducibility tests; 4-tier classification
├── prompts.py          # Curated 80+ prompt library across 8 domains
├── config.py           # YAML-based RunConfig dataclass, load/save
├── compare.py          # Comparative analysis: two-run HTML reports with statistics
├── dashboard.py        # Self-contained HTML dashboard with inline SVG charts
├── batch.py            # Sequential batch runner for experiment sweeps
├── export.py           # ZIP packaging for reproducible run sharing
├── analyze.py          # CLI archive inspector, diversity reports, MLflow viewer
├── transfer.py         # Cross-substrate transfer testing
├── baselines.py        # Null baseline executors (Markov, shuffle, fixed)
├── synthetic.py        # Synthetic ground-truth genomes for instrument validation
├── descriptors.py      # Behavioral descriptor computation
├── manifest.py         # Run manifest and metadata
├── logging_cfg.py      # Logging configuration
└── genome_viz.py       # SVG genome flowchart renderer
```


### Module Descriptions

| Module | Purpose |
|--------|---------|
| `genome.py` | Defines the 10 reasoning module types (chain-of-thought, Socratic questioning, Bayesian updating, etc.) and the `ReasoningModuleGene` dataclass with depth, temperature, iteration count, and anomaly sensitivity parameters. |
| `execution.py` | Builds system prompts from genome sequences, calls Ollama's `/api/generate` endpoint, handles timeouts and retries. |
| `fitness.py` | Computes novelty (cosine distance to k-nearest neighbors in embedding space), coherence (text quality heuristics), and complexity (genome structure penalty). |
| `archive.py` | MAP-Elites grid with pluggable behavioral descriptors (output length, vocabulary diversity). Supports save/load JSON round-trips. |
| `evolution.py` | MVP-1 loop: initialize population → evaluate → update archive → select parents → mutate/crossover → repeat. |
| `evolution_v2.py` | MVP-2 loop: adds `ExecutionMonitor` for logprob/timing capture, `SelfPredictor` that learns input→output mapping, `AnomalyDetector` that flags divergent outputs, and `run_characterization` for anomaly classification. Per-individual anomaly sensitivity is a heritable genome parameter. |
| `monitor.py` | `SelfPredictor` trains a Ridge/MLP regressor on genome+input→output embeddings. `AnomalyDetector` compares predicted vs actual embeddings using cosine distance. `AnomalyCapture` persists snapshots to disk. |
| `characterization.py` | Four-tier battery: transfer testing (does the behavior generalize?), ablation (which module is responsible?), reproducibility (is it consistent?), classification (noise / input-specific / module-reducible / candidate-emergent). |
| `config.py` | `RunConfig` dataclass with 19 parameters. `load_config()` / `save_config()` for YAML. CLI flags override config file values. |
| `compare.py` | Loads two run archives, computes overlap statistics, generates self-contained HTML with behavioral grid comparison, fitness curves, and top-5 unique configurations per run. |

## CLI Reference

### Evolution Runs

```bash
# MVP-1 (novelty search only)
python -m aethon.evolution [--config path.yaml] [--generations N] [--pop-size N]
    [--mutation-prob F] [--crossover-prob F] [--model MODEL] [--base-url URL]
    [--prompt-strategy uniform|random|domain] [--prompt-domain DOMAIN]
    [--save-archive PATH] [--save-embeddings PATH]

# MVP-2 (with self-monitoring)
python -m aethon.evolution_v2 [--config path.yaml] [--generations N] [--pop-size N]
    [--anomaly-threshold F] [--predictor-retrain-interval N] [--predictor-min-samples N]
    [... same flags as MVP-1 ...]
```

### Analysis & Reporting

```bash
# Dashboard
python -m aethon.dashboard --run-dir archive/ --output dashboard.html

# Archive inspector
python -m aethon.analyze --archive-path archive/map_elites.json [--embedding-path archive/embeddings.npz] [--skip-mlflow]

# Compare two runs
python -m aethon.compare --run-a archive/run_qwen/ --run-b archive/run_llama/ --output comparison.html

# Visualize a genome
python -m aethon.genome_viz --genome '{"genes": [...]}' --output genome.svg
```

### Batch & Export

```bash
# Run experiment sweep
python -m aethon.batch --config-dir configs/experiments/ --output-dir archive/batch_results/

# Package a run for sharing
python -m aethon.export --run-dir archive/run_qwen/ --output exports/aethon_run.zip
```

## Experiment Workflow

1. **Configure** — Create a YAML config or use a preset from `configs/experiments/`.
2. **Run** — Execute with `python -m aethon.evolution --config your_config.yaml` or batch-run multiple configs with `python -m aethon.batch`.
3. **Analyze** — Generate a dashboard (`python -m aethon.dashboard`) and inspect the archive (`python -m aethon.analyze`).
4. **Compare** — Use `python -m aethon.compare` to generate side-by-side HTML reports between runs.
5. **Export** — Package completed runs into ZIP archives with `python -m aethon.export` for sharing or archival.

### Experiment Configs

18 experiment configs in `configs/experiments/`:

| Category | Configs | Description |
|----------|---------|-------------|
| Replication (Llama) | `llama_uniform`, `llama_seed2`, `llama_seed3`, `llama_seed4` | 4-seed replication, Llama 3.1 8B |
| Replication (Qwen) | `qwen_uniform`, `qwen_seed2`, `qwen_seed3`, `qwen_seed4` | 4-seed replication, Qwen 2.5 7B |
| Random strategy | `llama_random`, `qwen_random` | Random prompt sampling baseline |
| Null baselines | `null_markov`, `null_shuffle`, `null_fixed_cot`, `null_trivial` | Various null models |
| Threshold variants | `qwen_v2_conservative`, `qwen_v2_aggressive` | MVP-2 anomaly threshold comparison |
| Specialty | `anti_aethon`, `trace_novelty` | Anti-aethon control, trace novelty mode |

## Theoretical Motivation

AETHON is grounded in three ideas. First, quality-diversity algorithms (MAP-Elites) are better suited to open-ended exploration than pure fitness optimization — they maintain a diverse archive of solutions across behavioral dimensions rather than converging on a single optimum. Second, novelty search creates selection pressure toward unexplored regions of behavior space, which is exactly what you want when searching for emergent properties you can't define in advance. Third, self-monitoring through learned predictive models provides a principled anomaly detection mechanism: if the system can predict its own behavior and then observes something it didn't predict, that surprise is worth investigating.

The anomaly sensitivity parameter is itself heritable — genomes that set their detection threshold too low waste compute on false positives, while those that set it too high miss genuine anomalies. This creates evolutionary pressure toward self-calibrating detection sensitivity, a form of meta-learning within the evolutionary process.

The characterization battery (transfer, ablation, reproducibility, classification) is designed to distinguish genuine emergent properties from noise. A behavior that transfers across inputs, survives ablation of individual modules, and reproduces consistently is a stronger candidate for emergence than one that appears once on a single prompt.

## Sister Projects

- **Prometheus** (`F:\Prometheus`) — Top-down observation. Classifies AETHON's evolved reasoning traces using rule-based + LLM classifiers against the 10-module vocabulary. Provides independent measurement instrument for cross-project validation.
- **Prometheus** (`F:\Prometheus`) — Umbrella project. Houses Ignis (circuit discovery), Arcanum (waste stream mining), and cross-project theory (RPH).

## Key Documentation

| Document | Purpose |
|----------|---------|
| `docs/AETHON_OPERATIONS.md` | **Start here on context reset.** Daily routines, monitoring commands, experiment registry, file locations. |
| `AETHON_Living_Ideas_Document_v3.md` | Strategic research backlog (32 items across P0–P3 + Parked). |
| `docs/AETHON_Executive_Summary_Technical.md` | Technical summary for external audiences. |
| `docs/aethon_research_brief.md` | Funding pitch / research brief. |

## Contributing & Future Directions

Contributions welcome. Key areas for development:

- **New reasoning modules** — The `ModuleType` enum in `genome.py` is the extension point. Add a new type, write its instruction template in `MODULE_INSTRUCTION_LIBRARY`, and the evolutionary search will automatically explore it.
- **Alternative fitness functions** — The fitness computation in `fitness.py` is modular. Swap in domain-specific coherence metrics or alternative novelty measures.
- **Multi-model evaluation** — Evaluate the same genome across multiple LLMs to test whether emergent properties are model-specific or architecture-general.
- **Distributed evolution** — The evaluation loop is embarrassingly parallel. A distributed version could evaluate population members across multiple Ollama instances.
- **Formal emergence criteria** — Develop quantitative metrics for emergence beyond the current four-tier classification.

## License

See `LICENSE` file for details.