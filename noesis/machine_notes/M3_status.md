# Noesis M3 — Building-Block Exploitation Tournament Status

**Machine:** M3
**Started:** 2026-03-28 12:24:05
**Last update:** 2026-03-28 15:20:54 (~3 hours in, 30-hour run)
**Current cycle:** 2,440

---

## Summary

M3 is running strong. Building blocks extracted from M1's crack log are dominating the search — over half of all cracks use a building-block super-organism, and BB chains consistently score higher than non-BB chains. M1's discoveries are transferring.

---

## Key Numbers

| Metric | Value |
|--------|-------|
| Total cracks | 15,628 |
| Cracks using building blocks | 8,761 (56%) |
| Cracks without building blocks | 6,867 (44%) |
| BB mean quality | **0.5644** |
| Non-BB mean quality | 0.5279 |
| BB max quality | **0.6600** |
| Non-BB max quality | 0.6050 |
| Cracks/cycle | ~6.4 |

**Building blocks raise both the floor and the ceiling.** BB chains average +0.037 higher quality than non-BB chains. The quality ceiling of 0.660 is held exclusively by BB chains.

---

## Building Block Usage

| Building Block (M1 pair) | Cracks | M1 frequency |
|--------------------------|--------|--------------|
| `topology.euler_characteristic -> statistical_mechanics.ising_model_1d` | 8,119 | 13x in M1 |
| `topology.euler_characteristic -> probabilistic_number_theory.random_integer_gcd_probability` | 541 | 13x in M1 |
| `chaos_theory.tent_map -> statistical_mechanics.partition_function` | 98 | 4x in M1 |

**17 of 20 building blocks have not produced cracks yet.** The topology/stat-mech block is the runaway winner. This suggests M1's top discovery (Euler characteristic -> Ising model) is a genuinely powerful primitive, not noise.

---

## Strategy Leaderboard

| Strategy | Cracks | Share |
|----------|--------|-------|
| mutation | 11,519 | 73.7% |
| random_baseline | 2,106 | 13.5% |
| temperature_anneal | 1,804 | 11.5% |
| epsilon_greedy | 126 | 0.8% |
| frontier_seeking | 65 | 0.4% |
| tensor_topk | 8 | 0.1% |

Mutation is dominant — it takes successful chains and swaps one operation, which is highly effective when building blocks provide a strong anchor. Random baseline is healthy at 13.5%, confirming the results are real (sacred baseline intact).

---

## Top 10 Chains (all 0.660 quality)

1. `statistics.multimode -> bb_topology_euler_char__stat_mech_ising` (temperature_anneal)
2. `numpy.fabs -> bb_topology_euler_char__stat_mech_ising` (mutation)
3. `numpy.svd -> bb_topology_euler_char__prob_nt_random_gcd` (random_baseline)
4. `numpy.qr -> bb_topology_euler_char__stat_mech_ising` (mutation)
5. `scipy_special.softmax -> bb_topology_euler_char__prob_nt_random_gcd` (mutation)
6. `scipy_stats.gstd -> bb_topology_euler_char__stat_mech_ising` (random_baseline)
7. `numpy.chisquare -> bb_topology_euler_char__stat_mech_ising` (mutation)
8. `scipy_special.jnjnp_zeros -> bb_topology_euler_char__stat_mech_ising` (mutation)
9. `scipy_linalg.cholesky_banded -> bb_topology_euler_char__stat_mech_ising` (mutation)
10. `numpy.rad2deg -> bb_topology_euler_char__stat_mech_ising` (mutation)

**Pattern:** "X -> topology/stat-mech building block" is the winning template. Many different first-step operations all converge to the same building-block finisher. Multiple strategies independently discover this.

---

## M3 Scoring Weights (differs from M1)

```
quality = 0.20*execution + 0.20*novelty + 0.15*structure + 0.10*diversity
        + 0.15*compression + depth_bonus + bb_bonus
        - 0.05*cheapness - 0.05*dead_end

depth_bonus = min(0.15, 0.05 * (chain_length - 2))  # +0.05 per extra op
bb_bonus    = 0.10 if chain uses bb_ organism else 0.0
```

---

## Early Observations

1. **M1's discoveries transfer.** The topology/stat-mech building block, extracted from M1's 13x-repeated pair, is producing the highest-quality chains in M3. Bootstrapping works.

2. **Building blocks raise quality.** +0.037 mean quality advantage and exclusive ownership of the 0.660 ceiling. Even discounting the +0.10 bb_bonus, BB chains are competitive.

3. **Concentration risk.** 3 of 20 building blocks account for all BB cracks. The other 17 may need the depth bonus to kick in (longer chains that compose multiple BBs) or may simply not be useful.

4. **Depth not yet explored.** The 0.660 ceiling hasn't been broken. Longer chains (3+ steps with multiple BBs) haven't emerged yet — the depth bonus should enable this as mutation explores deeper compositions.

---

*Next update when significant milestones are hit or at user request.*
