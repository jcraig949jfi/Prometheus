# Noesis M3 — Status Update #2

**Machine:** M3
**Started:** 2026-03-28 12:24:05
**Last update:** 2026-03-28 17:04:58 (~4.7 hours in, 30-hour run)
**Current cycle:** 3,847

---

## Key Numbers

| Metric | Value | Change from Status #1 |
|--------|-------|-----------------------|
| Total cracks | 22,902 | +7,274 |
| BB cracks | 13,218 (58%) | +4,457 (share up from 56%) |
| Non-BB cracks | 9,684 (42%) | |
| BB mean quality | **0.5631** | ~stable |
| Non-BB mean quality | 0.5267 | ~stable |
| BB max quality | **0.6600** | unchanged |
| Non-BB max quality | 0.6050 | unchanged |
| Cracks/cycle | ~5.95 | slight decrease |

---

## Building Block Usage

| Building Block | Cracks | Share of BB cracks |
|----------------|--------|--------------------|
| `topology.euler_char -> stat_mech.ising_model_1d` | 12,466 | 94.3% |
| `topology.euler_char -> prob_nt.random_integer_gcd_prob` | 618 | 4.7% |
| `chaos_theory.tent_map -> stat_mech.partition_function` | 134 | 1.0% |
| Other 17 building blocks | 0 | 0% |

The topology/ising block is increasingly dominant. **17 of 20 building blocks still unused.**

---

## Chain Length Distribution

| Length | Count |
|--------|-------|
| 2 | 22,902 (100%) |

**All chains are length 2.** This is a significant finding — the depth bonus (+0.05 per extra op beyond length 2, max +0.15) has not incentivized longer chains. The strategies are only proposing length-2 chains because that's what the base strategies (random, tensor_topk, mutation, etc.) are wired to produce. The mutation strategy mutates existing length-2 chains, producing more length-2 chains.

**This means the depth bonus is +0.00 for every crack found so far.** The 0.660 ceiling = 0.20*exec + 0.20*novelty + 0.15*structure + 0.10*diversity + 0.15*compression + 0.10*bb_bonus - penalties. Deeper chains would break this ceiling, but the strategies aren't generating them.

---

## Strategy Leaderboard

| Strategy | Cracks | Share |
|----------|--------|-------|
| mutation | 17,262 | 75.4% |
| random_baseline | 2,770 | 12.1% |
| temperature_anneal | 2,539 | 11.1% |
| frontier_seeking | 138 | 0.6% |
| epsilon_greedy | 135 | 0.6% |
| tensor_topk | 58 | 0.3% |

Mutation share growing. tensor_topk finally waking up (8 -> 58).

---

## Quality Trend

| Period | Mean quality |
|--------|-------------|
| First 500 cracks | 0.5481 |
| Last 500 cracks | 0.5471 |

**Quality is flat.** No improvement trend over time. The search has found its groove (BB chains at ~0.56 mean) but isn't pushing higher.

---

## Analysis

### What's working
- **Bootstrapping confirmed.** M1's top discovery transfers cleanly — the topology/ising building block is the strongest single primitive in M3's search space.
- **BB quality advantage holds.** +0.036 mean quality gap is consistent and not just from the +0.10 bb_bonus (that would only account for +0.10 * some_fraction of chains).
- **Volume is good.** 22,900 cracks in 4.7 hours, daemon is stable.

### What's not working
- **No depth exploration.** All chains are length 2. The depth bonus is dead weight. The base strategies don't have a mechanism to propose length 3+ chains. Mutation only swaps operations in existing chains, preserving length.
- **17/20 building blocks unused.** Heavy concentration on one block. The other blocks may have execution issues or type incompatibilities.
- **Quality plateau.** 0.660 ceiling unchanged since early in the run. No upward trend.

### Implication for M3's design thesis
M3 was designed to test: "Do building blocks enable deeper chains?" The answer so far is **no** — not because building blocks can't compose, but because **the strategies don't propose longer chains**. This is an architectural limitation, not a building-block limitation. A future run would need a strategy that explicitly extends successful length-2 chains to length 3+.

---

*~25 hours remaining. Expect continued accumulation at current rate but unlikely to break the 0.660 ceiling without longer chains.*
