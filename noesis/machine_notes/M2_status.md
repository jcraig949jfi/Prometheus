# M2 Status — 2026-03-28 ~13:45

## Noesis Tournament — M2 Scoring Variant

| Metric | Value |
|--------|-------|
| Runtime | ~20 minutes (of 30-hour run) |
| Cycle | 4,178 |
| Total cracks | 2,105 |
| Cracks/min | ~105 |
| Max quality | **0.7137** (M1 ceiling was 0.659 — **broken**) |
| Cracks above 0.659 | 95 |
| Avg quality | 0.579 |
| Sensitivity coverage | 98% of cracks have sensitivity > 0 |
| Process status | Stable, PID 1481 + worker subprocess |

### M2 Scoring Weights (vs M1)

```
Adaptive execution weight: 0.10 when baseline > 0.5, else 0.25 (same as M1)
Remaining budget (0.80 when warmed up):
  Compression:  0.31  (M1: 0.19) — PRIMARY signal
  Sensitivity:  0.19  (M1: N/A)  — NEW dimension
  Novelty:      0.19  (M1: 0.31)
  Structure:    0.155 (M1: 0.19)
  Diversity:    0.155 (M1: 0.19)
Penalties: -0.05 cheapness, -0.05 dead_end (unchanged)
```

### Strategy Leaderboard

| Strategy | Cracks | Share | Notes |
|----------|--------|-------|-------|
| Random baseline | 727 | 34.5% | Strongest — M2 weights favor diverse exploration |
| Mutation | 683 | 32.4% | No longer dominant (was 46% on M1) |
| Temperature anneal | 627 | 29.8% | Surging — finds structured chains mutation misses |
| Epsilon-greedy | 35 | 1.7% | |
| Frontier seeking | 20 | 0.9% | |
| Tensor top-K | 13 | 0.6% | |

Key shift from M1: **mutation lost its dominance**. On M1 mutation held 46% of cracks. On M2 with compression+sensitivity weighting, random and temperature_anneal are competitive. This means M1's mutation advantage was partly a scoring artifact — brute-force refinement optimized execution rate (the old primary signal), but with compression as the primary signal, diverse exploration finds equally good chains.

### Top 5 Compositions

| Quality | Chain | Sensitivity | Strategy |
|---------|-------|-------------|----------|
| 0.7137 | scipy_linalg.lu_factor -> math.fsum | 1.00 | random |
| 0.7137 | scipy_signal.qspline1d -> statistics.median_low | 1.00 | random |
| 0.6936 | numpy.i0 -> statistics.median_low | 1.00 | random |
| 0.6936 | numpy.nanmean -> math.radians | 1.00 | random |
| 0.6931 | numpy.norm -> statistics.erf | 1.00 | mutation |

All top compositions have sensitivity=1.0 (output changes fully with 1% input perturbation) and compression=0.5 (array/structured -> scalar reduction). The M2 weights are selecting for chains that do real computation, not lookup/identity.

### Answering the M2 Questions

1. **Does the quality ceiling break past 0.659?** YES. Max quality 0.7137. 95 cracks exceed the M1 ceiling. The 0.659 ceiling was a scoring function artifact, not a compositional limit.

2. **Does mutation still dominate?** NO. Random (34.5%) > Mutation (32.4%) > Temperature anneal (29.8%). With compression+sensitivity as the dominant signals, mutation's brute-force refinement of execution rate no longer confers an advantage.

3. **Does compression become the discriminating signal?** YES. All top compositions score compression=0.5 (the maximum for array->scalar chains). Chains that actually reduce entropy stand out under M2 weights.

### Implementation Notes

- Subprocess worker model: main process handles scoring/DB/tournament, isolated subprocess handles chain execution. Worker auto-restarts on hang/crash (some scipy operations block indefinitely on certain matrix inputs).
- Input sensitivity: for each chain scoring > 0.4, run 2 additional executions with inputs scaled by 0.99x and 1.01x. Compare output hashes. 0 = lookup table, 1 = fully sensitive. Computed via the same subprocess worker.
- DuckDB schema includes `score_sensitivity` and `score_compression` columns for cross-machine autopsy.

---

## Files on M2

- `organisms/cracks_live.jsonl` — live crack log (growing)
- `organisms/noesis_state.duckdb` — tournament database (locked by running daemon)
- `organisms/noesis_daemon.py` — M2-modified daemon
- Daemon terminates ~19:29 March 29 and writes `noesis_tournament_report.json`
