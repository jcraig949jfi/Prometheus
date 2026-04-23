# Apollo

Apollo is the model-training arm of Prometheus — an evolutionary pipeline for training small LLMs against novel fitness functions.

## Current version

This directory holds the **v2d** generation (current). Design, code, configs, dashboard, and launcher all refer to v2d.

- **Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md)
- **Roadmap:** [`ROADMAP.md`](ROADMAP.md)
- **Launch:** `launch.bat`
- **Code:** `src/`
- **Configs:** `configs/`

## History

Earlier generations live under [`archive/`](archive/):

| Version | Location | Notes |
|---------|----------|-------|
| v1 | `archive/v1/` | Original apollo — design docs v1/v2/v3, Q&A rounds, council feedback, seed-candidate sweeps, first src tree |
| v2-beta | `archive/v2-beta/` | First v2 iteration (M2 beta setup) |
| v2b | `archive/v2b/` | Second v2 iteration |
| v2c | `archive/v2c/` | Third v2 iteration |
| v2d | `archive/v2d/` | Past run directories for v2d (code itself is promoted to `src/`) |

Runtime outputs (reports, logs, lineage) from past runs are under `archive/reports/`, `archive/logs/`, `archive/lineage/`.
