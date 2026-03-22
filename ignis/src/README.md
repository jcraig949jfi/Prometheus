# Ignis Pipeline Quick Reference

**Docs:** See parent project docs in `../docs/` for deeper analysis notes.

## 1) Run lifecycle overview

1. Launch run from `seti_orchestrator.py` or your deployment script.
2. Run cleanup/restart with `archive_run.py` when stopping or fixing.
3. Use `night_watchman.py` to parse data and build scientific digest.
4. Use `review_watchman.py` for narrative summaries and run comparisons.

## 2) Archive modes (`archive_run.py`)

- `python archive_run.py preserve "note"`
  - Use after a complete run to archive as a final scientific record.
  - Moves model outputs, `discovery_log.jsonl`, and related files into `results/ignis/archives/run_*`.
  - Renames log to `logs/ignis_run_YYYY-MM-DD.log`.
  - Deletes model `state.json` so next run starts clean.

- `python archive_run.py restart "note"`
  - Use when stopping to fix code/config and then restart.
  - Archives into `results/ignis/archives/restart_*`.
  - Renames log to `logs/ignis_restart_YYYY-MM-DD_<slug>.log`.
  - Deletes model `state.json`, `orchestrator.pid`, and `STOP` semaphore.

## 3) Discovery log semantics

- `discovery_log.jsonl` is append-only, one line per genome evaluation.
- Each record includes meta fields:
  - `gen` (generation index),
  - `genome_idx` (index in generation),
  - `fitness`, `trap_scores`, `logit_score`, etc.
- Genome count in watchman = number of lines in `discovery_log.jsonl` (total evaluations).
- `gen` may remain constant across many evaluations (e.g. 0/40 per generation).

## 4) Analysis tools

Full guide with ELI5 output explanations: **[`../docs/analysis_tools_guide.md`](../docs/analysis_tools_guide.md)**

### night_watchman.py — background analysis daemon
- Runs alongside the orchestrator in a second terminal.
- Snapshots live files (MD5 copy), runs 7 analysis passes, writes digest.
- Outputs: `results/ignis/watchman/digest_latest.md`, `digest_history.jsonl`, `alerts.log`.
- Stop: `python stop_ignis.py` (writes semaphore, watchman does final cycle and exits).

### eval_rph_survivors.py — post-run RPH proxy evaluator
- Loads archived `best_genome.pt` files, scores them on three RPH criteria (Δ_cf, MI_step, Δ_proj).
- Runs on CPU by default — safe to run during a live GPU search.
- Classifies each vector as PRECIPITATION_CANDIDATE, WEAK_SIGNAL, or NULL.
- Outputs: console table + `results/rph_eval_YYYYMMDD_HHMMSS.json`.

### review_watchman.py — narrative report builder
- Reads `digest_history.jsonl` and prints human-readable scientific narratives.
- Automatically integrates RPH eval JSON if present (four RPH narrative paragraphs).
- Use `--latest` for full narrative, `--cycles N` for history, `--table` for per-gen data.

## 5) Quick commands

Start run + watchman:
```bash
python seti_orchestrator.py ...
python night_watchman.py --once
python night_watchman.py --interval 300
python review_watchman.py --latest
```

Archive restart during debug:
```bash
python archive_run.py restart "marker fixes"
```

Archive final data:
```bash
python archive_run.py preserve "gen 30 complete best 0.61"
```

## 6) Troubleshooting

- If watchman shows stale `genomes` but no progress, check orchestrator is still running and `discovery_log.jsonl` is being appended.
- If CMA-ES is stuck near plateau, this is expected; check `watchman` signals and `trap_coupling`.
- Use `review_watchman.py --table` to inspect per-generation values.


---

Keep this README as the canonical quick reference for run lifecycle and monitoring.