# M2 Status Update 2 — 2026-03-28 ~14:15

## Noesis Tournament — M2 Scoring Variant (Running)

| Metric | Value | Delta from Status 1 |
|--------|-------|---------------------|
| Runtime | ~45 minutes | +25 min |
| Cycle | 7,939 | +3,761 |
| Total cracks | 2,647 | +542 |
| Max quality | **0.7137** | unchanged |
| Cracks above M1 ceiling (0.659) | 104 | +9 |
| Cracks above 0.700 | 2 | new |
| Avg quality | 0.577 | steady |
| Sensitivity coverage | 98.7% | steady |
| Process status | Stable, running | no restarts |

### Strategy Leaderboard — Major Shift from M1

| Strategy | Cracks | Share | Recent 500 | Trend |
|----------|--------|-------|------------|-------|
| Random baseline | 955 | 36.1% | 42.2% | rising |
| Temperature anneal | 852 | 32.2% | 40.8% | **surging** |
| Mutation | 768 | 29.0% | 16.2% | **declining** |
| Epsilon-greedy | 39 | 1.5% | 0.8% | |
| Frontier seeking | 20 | 0.8% | 0% | dead |
| Tensor top-K | 13 | 0.5% | 0% | dead |

**The big story: mutation is collapsing.** In the most recent 500 cracks, mutation dropped to 16.2% while temperature_anneal surged to 40.8%. On M1 at the same cycle count, mutation held 46%. The M2 scoring weights (compression primary, sensitivity new) reward structured chains that brute-force mutation struggles to find through single-step refinement. Temperature anneal's softmax exploration is finding these chains more effectively as it cools.

### Quality Distribution

| Range | Count | % |
|-------|-------|---|
| 0.50 - 0.55 | 630 | 23.8% |
| 0.55 - 0.60 | 1,397 | 52.8% |
| 0.60 - 0.65 | 510 | 19.3% |
| 0.65 - 0.70 | 108 | 4.1% |
| 0.70+ | 2 | 0.08% |

The distribution is healthier than M1's — M1 had everything clustered at 0.55-0.659 with a hard wall. M2 has a smooth tail extending to 0.7137. The ceiling is softer but still present — no chain has exceeded 0.7137.

### Top 10 Compositions

| # | Quality | Chain | Sens | Strategy |
|---|---------|-------|------|----------|
| 1 | 0.7137 | scipy_linalg.lu_factor -> math.fsum | 1.00 | random |
| 2 | 0.7137 | scipy_signal.qspline1d -> statistics.median_low | 1.00 | random |
| 3 | 0.6936 | numpy.i0 -> statistics.median_low | 1.00 | random |
| 4 | 0.6936 | numpy.nanmean -> math.radians | 1.00 | random |
| 5 | 0.6931 | numpy.norm -> statistics.erf | 1.00 | mutation |
| 6 | 0.6885 | numpy.permute_dims -> scipy_stats.tvar | 1.00 | random |
| 7 | 0.6812 | scipy_stats.gmean -> math.asinh | 1.00 | temp_anneal |
| 8 | 0.6742 | statistics.stdev -> math.asinh | 1.00 | mutation |
| 9 | 0.6742 | scipy_signal.cspline1d -> scipy_stats.jarque_bera | 1.00 | epsilon_greedy |
| 10 | 0.6742 | scipy_stats.tstd -> math.cbrt | 1.00 | mutation |

Pattern: the highest-quality chains are **array-to-scalar reductions** (compression=0.5) with full input sensitivity (1.0). The winning formula is: take a structured operation (LU factorization, spline interpolation, Bessel function) and reduce it through a scalar summarizer (fsum, median, radians, asinh). These are real computational chains, not accidents.

### Key Findings So Far

1. **0.659 ceiling confirmed as scoring artifact.** M2 breaks it immediately. The compositional space has quality up to at least 0.7137 — M1 just couldn't see it.

2. **Mutation dominance was a scoring artifact too.** When execution rate was the primary signal (M1), mutation's hill-climbing optimized the easy metric. With compression+sensitivity as primary, diverse exploration strategies (random, temperature_anneal) find equally good chains.

3. **Input sensitivity is highly discriminating.** 98.7% of cracks have sensitivity > 0, but 100% of top-10 chains have sensitivity = 1.0. The 1.3% with sensitivity = 0 are likely scoring on other dimensions. Sensitivity separates real computation from trivial chains.

4. **New ceiling at ~0.714.** The M2 ceiling appears to be in the compression score (capped at 0.5 for array->scalar). Chains that achieve higher compression (multi-step reduction, or more complex entropy reduction) could break through. Consider: the compression scoring formula `scalar_out / len(output_types) * 0.5` caps at 0.5 when all outputs are scalar. A richer compression metric (actual entropy measurement) might unlock higher quality.

---

## Process Health

- Main process (PID 1481) + worker subprocess: both alive, no restarts since launch
- Worker subprocess handles all chain execution in isolation — any scipy hang/crash kills only the worker, which auto-restarts
- Deadline: ~19:29 March 29 (29+ hours remaining)
- DuckDB checkpoint every 10 cycles

## Files on M2

- `organisms/cracks_live.jsonl` — 2,647 cracks (growing)
- `organisms/noesis_state.duckdb` — tournament database
- `organisms/noesis_daemon.py` — M2-modified daemon (subprocess worker model)
