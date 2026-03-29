# M4 Status Report #2
**Machine:** M4 (Combined Scoring + Building Blocks)
**Date:** 2026-03-28 ~17:05
**Status:** RUNNING -- 2.1 hours into 30-hour run

---

## Headline Result

**M4 max quality: 0.7282 -- breaks M2's 0.7137 ceiling.**

M2's scoring fix and M3's building blocks are confirmed additive. The entire top 10 is BB-powered chains. Every non-BB chain caps at 0.7095.

---

## Current Numbers (Cycle ~1,082)

| Metric | Value |
|--------|-------|
| Total cracks | 2,699 |
| Max quality | **0.7282** |
| BB cracks | 513 (19.0%) |
| Sensitivity > 0 | 98.0% |
| Mean quality | 0.5858 |
| Median quality | 0.5782 |
| Above 0.65 | 336 |
| Above 0.70 | 99 |
| Above 0.72 | 33 |
| Chains tested | ~54,000 |
| Organisms | 47 (26 base + 1 OEIS + 20 BB) |
| Operations | 600 |
| Compatible pairs | 117,432 |

---

## Bug Fix at Launch

`types_compatible()` did not handle the `"any"` type that building blocks use. BBs had only 380 compatible pairs (BB-to-BB) instead of 22,580 (BB-to-everything). Added: `if out_type == "any" or in_type == "any": return True`. This was critical -- the previous partial run (845 cracks) had 0% BB usage because of this bug. That data was backed up and a fresh run started.

---

## The 2x2 Factorial Answer

| | No BB | BB |
|---|---|---|
| **Baseline scoring** | M1: 0.659 | M3: 0.660 |
| **Fixed scoring (compression + sensitivity)** | M2: 0.7137 | **M4: 0.7282** |

- **Scoring fix effect:** +0.055 (dominant)
- **BB effect alone:** +0.001 (invisible without scoring fix)
- **Combined effect:** +0.069
- **Interaction:** +0.014

**Interpretation:** The scoring fix is the primary breakthrough. BBs provide real additional lift, but only when scoring can discriminate quality. M3's ceiling (0.660) was almost identical to M1 (0.659) because the old scoring formula couldn't see that BB compositions are genuinely better. M2's compression-primary + sensitivity scoring makes the BB quality visible.

---

## Which Building Blocks Work

Only 3 of 20 BBs appear in cracks:

| Building Block | Crack Count | % of BB Cracks |
|---|---|---|
| `bb_topology_euler_characteristic__statistical_mechanics_ising_model_1d` | 332 | 64.7% |
| `bb_topology_euler_characteristic__probabilistic_number_theory_random_integer_gcd_probability` | 149 | 29.0% |
| `bb_chaos_theory_tent_map__statistical_mechanics_partition_function` | 32 | 6.2% |

The topology -> stat_mech pair that M1 discovered as dominant is still dominant as a building block. The topology -> number theory pair is a strong second. Both share the `topology.euler_characteristic` front end. The chaos -> stat_mech pair is a distant third.

The other 17 BBs produce 0 cracks. They either fail execution or score below the 0.5 crack threshold.

---

## Top 10 Chains (All BB-Powered)

All tied at 0.7282:

| # | Chain |
|---|---|
| 1 | `topology.connected_components -> bb_topo_euler__stat_mech_ising.chain` |
| 2 | `signal_processing.autocorrelation -> bb_topo_euler__stat_mech_ising.chain` |
| 3 | `signal_processing.autocorrelation -> bb_topo_euler__prob_nt_gcd.chain` |
| 4 | `scipy_stats.wilcoxon -> bb_topo_euler__prob_nt_gcd.chain` |
| 5 | `scipy_stats.skew -> bb_topo_euler__stat_mech_ising.chain` |
| 6 | `scipy_special.softmax -> bb_topo_euler__stat_mech_ising.chain` |
| 7 | `scipy_signal.spectrogram -> bb_topo_euler__prob_nt_gcd.chain` |
| 8 | `scipy_linalg.tanm -> bb_topo_euler__stat_mech_ising.chain` |
| 9 | `scipy_linalg.pinv -> bb_topo_euler__stat_mech_ising.chain` |
| 10 | `numpy.radians -> bb_topo_euler__stat_mech_ising.chain` |

**Pattern:** Diverse front-end operations (numpy, scipy, signal processing, topology, stats) all feeding into the same 2 topology-based BBs. The front-end doesn't matter much -- it's the BB that provides the quality. This suggests the topology.euler_characteristic -> stat_mech/number_theory pathway is a genuine computational motif, not an artifact.

### Best Non-BB Chains (capped at 0.7095)

| Quality | Chain |
|---------|-------|
| 0.7095 | `math.exp -> statistics.sqrt` |
| 0.7095 | `analytic_number_theory.riemann_zeta_partial -> math.cosh` |
| 0.7095 | `numpy.log2 -> scipy_stats.kstatvar` |
| 0.7095 | `statistics.exp -> chaos_theory.lyapunov_exponent` |

---

## Strategy Performance

| Strategy | Cracks | Notes |
|----------|--------|-------|
| mutation | 1,921 (71%) | Dominant -- mutates successful chains |
| temperature_anneal | 297 (11%) | Softmax with periodic reset |
| random_baseline | 292 (11%) | Sacred baseline, 1.4-1.6 cpc |
| frontier_seeking | 139 (5%) | Exploring unseen regions |
| epsilon_greedy | 49 (2%) | 80/20 exploit/explore |
| tensor_topk | 1 (<1%) | Sequential top-K, nearly exhausted |

Mutation strategy dominates because once a BB crack is found, mutation generates variants by swapping the front-end operation while keeping the BB.

---

## Observations

1. **The quality ceiling at 0.7282 looks firm.** 33 chains all tie at exactly 0.7282. This is likely the mathematical maximum of the scoring formula for 2-step chains with BB bonus (+0.10) and max sensitivity (1.0). To break higher, we'd need 3+ step chains with depth bonus, or a scoring formula change.

2. **BB usage ramped from 0% to 19%.** After the type compatibility fix, BBs went from invisible to comprising nearly 1 in 5 cracks. The mutation strategy amplifies: once one BB crack is found, it mutates it into many variants.

3. **3 of 20 BBs work, 17 don't.** The working BBs all involve `topology.euler_characteristic` as the first operation. The non-working BBs likely fail on the test input distribution (most test inputs are scalar, but topology ops need arrays).

4. **Sensitivity is nearly universal.** 98% of cracks have sensitivity > 0, up from 87% early in the run. The two-pass scoring (only compute sensitivity for quality > 0.4) is working efficiently.

5. **QD grid fill is low (3/64).** The MAP-Elites grid only has 3 cells filled out of 64. This suggests most cracks cluster in the same behavioral region (2-step chains with similar output types). Longer chains or different chain structures would fill more cells.

---

## What's Left (27.9 hours remaining)

The daemon will continue for ~28 more hours. Expected:
- More BB crack variants (mutation will keep exploring front-end permutations)
- Possible new BB discoveries as random/frontier strategies sample the full 117k pair space
- Unlikely to break 0.7282 without 3+ step chains hitting the depth bonus

---

## Files on This Machine

| File | Description |
|------|-------------|
| `organisms/noesis_state.duckdb` | Live DB (locked by daemon) |
| `organisms/cracks_live.jsonl` | Append-only crack log (2,700+ entries) |
| `organisms/noesis_state_pre_bbfix.duckdb` | Pre-fix run backup |
| `organisms/cracks_live_pre_bbfix.jsonl` | Pre-fix run backup (845 cracks, 0% BB) |

**Python:** 3.11.9 at `C:\Program Files\Python311\python.exe`
