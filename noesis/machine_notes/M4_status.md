# M4 Status Report
**Machine:** M4 (Combined Scoring + Building Blocks)
**Date:** 2026-03-28
**Status:** RUNNING (30-hour daemon launched ~15:00)

---

## Bug Fix Applied at Launch

The `types_compatible()` function did not handle `"any"` type. Building block organisms declare `input_type: "any"` and `output_type: "any"`, but `"any"` only matched itself — not `"scalar"`, `"array"`, etc. This meant BBs had only 380 compatible pairs (BB-to-BB only) instead of the correct 22,580 (BB-to-everything).

**Fix:** Added `if out_type == "any" or in_type == "any": return True` to `types_compatible()`.

Before fix: 89,357 compatible pairs, 380 involving BBs (0.4%)
After fix: 117,432 compatible pairs, 22,580 involving BBs (19.2%)

A partial run (152 cycles, 845 cracks, 0% BB usage) was backed up as `cracks_live_pre_bbfix.jsonl` and `noesis_state_pre_bbfix.duckdb`. Fresh run started after fix.

---

## Early Results (Cycle ~350, ~290 cracks)

| Metric | Value | vs M2 | vs M1 |
|--------|-------|-------|-------|
| Max quality | **0.7282** | +0.0145 (breaks M2's 0.7137 ceiling) | +0.0692 |
| Total cracks | 290 | -- | -- |
| BB cracks | 3 (1.0%) | N/A | N/A |
| Sensitivity > 0 | 87% | matches M2 | -- |
| Strategies | 6 | same | same |
| Organisms | 47 (26 base + 1 OEIS + 20 BB) | -- | -- |
| Operations | 600 | -- | -- |
| Compatible pairs | 117,432 | -- | -- |

### Key Finding: M2 + M3 Are Additive

**M4's max quality (0.7282) exceeds M2's ceiling (0.7137).** The scoring fix and building blocks are complementary improvements.

### Top 3 Chains (all BB-powered)

| Quality | Chain |
|---------|-------|
| 0.7282 | `numpy.radians -> bb_topology_euler_characteristic__statistical_mechanics_ising_model_1d.chain` |
| 0.7282 | `numpy.degrees -> bb_topology_euler_characteristic__statistical_mechanics_ising_model_1d.chain` |
| 0.7282 | `numpy.arctan -> bb_topology_euler_characteristic__statistical_mechanics_ising_model_1d.chain` |

The topology->stat_mech building block (the dominant pair from M1) is the one breaking the ceiling, but only when M2's scoring is applied. M3 had the same BB but couldn't see its quality because it used M1's broken scoring.

### Top Non-BB Chains

| Quality | Chain |
|---------|-------|
| 0.7095 | `math.exp -> statistics.sqrt` |
| 0.7095 | `analytic_number_theory.riemann_zeta_partial -> math.cbrt` |
| 0.7095 | `statistics.exp -> chaos_theory.lyapunov_exponent` |

Non-BB chains cap at 0.7095 — below M2's 0.7137 because the BB bonus (+0.10) isn't available.

### BB Usage Note

BB usage is low (1%) because BB organisms only work on array/matrix inputs (4 of 12 test inputs). Scalar/integer inputs fail with "tuple index out of range" from the underlying topology.euler_characteristic operation. This limits BB chains to 25-33% success rate. Despite this, the BB chains that do work score highest thanks to the +0.10 BB bonus and real computational content.

---

## Strategy Performance

| Strategy | Cracks | Notes |
|----------|--------|-------|
| mutation | 159 | Dominant — mutates successful chains |
| random_baseline | 59 | Sacred baseline |
| frontier_seeking | 30 | Exploring unseen regions |
| temperature_anneal | 27 | Softmax with annealing |
| epsilon_greedy | 14 | 80/20 exploit/explore |
| tensor_topk | 1 | Sequential top-K |

---

## 2x2 Factorial Summary (Preliminary)

| | No BB | BB |
|---|---|---|
| **Baseline scoring** | M1: 0.659 | M3: 0.660 |
| **Fixed scoring** | M2: 0.7137 | **M4: 0.7282** |

- Scoring fix alone: +0.0547 (M2 - M1)
- BB alone: +0.001 (M3 - M1) -- BBs invisible without scoring fix
- Both combined: +0.0692 (M4 - M1)
- Interaction: 0.0692 - 0.0547 - 0.001 = +0.0135

**The interaction is positive but small.** The scoring fix is the dominant effect. BBs add a bonus on top, but only visible when scoring can discriminate quality. This is closer to "additive" than "multiplicative."

---

## Files

- `organisms/noesis_state.duckdb` — live (locked by daemon)
- `organisms/cracks_live.jsonl` — append-only crack log
- `organisms/noesis_state_pre_bbfix.duckdb` — pre-fix partial run backup
- `organisms/cracks_live_pre_bbfix.jsonl` — pre-fix partial run backup

## Runtime

- Python 3.11.9 at `C:\Program Files\Python311\python.exe`
- 4 worker processes
- Batch size: 50
- Deadline: 30 hours from ~15:00 on 2026-03-28
