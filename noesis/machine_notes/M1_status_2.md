# M1 Status Update 2 — 2026-03-28 ~17:10

## Noesis Tournament (CPU) — 8.9 hours in

| Metric | Status 1 (6.8h) | Now (8.9h) | Trend |
|--------|-----------------|------------|-------|
| Cycles | ~4,300 | 5,800 | +35% |
| Chains tested | ~86,000 | 116,000 | +35% |
| Total cracks | 7,382 | 9,271 | +26% |
| Cracks/hour | 1,090 | 1,041 | slight decline (novelty saturation) |
| Max quality | 0.659 | 0.659 | unchanged (scoring ceiling confirmed) |
| MAP-Elites cells | 4/64 | 4/64 | flat |

### Strategy Leaderboard (updated)

| Strategy | Cracks | Share | cpc | vs Random |
|----------|--------|-------|-----|-----------|
| Mutation | 3,699 | 39.9% | ~3.0 | 2.9x |
| Random baseline | 1,905 | 20.5% | 1.03 | 1.0x (control) |
| **Tensor top-K** | **1,752** | **18.9%** | **3.55** | **3.4x** |
| Temperature anneal | 1,701 | 18.3% | ~2.5 | 2.4x |
| Epsilon-greedy | 200 | 2.2% | ~0.5 | 0.5x |
| Frontier seeking | 14 | 0.2% | ~0 | dead |

### Key Changes Since Status 1

1. **Tensor top-K overtook mutation as the best cpc strategy** (3.55 vs ~3.0). Mutation saturated its local optima; tensor's systematic coverage keeps finding new regions. This is the signal the experiment was designed to detect — tensor guidance durably outperforms both random AND local search over time.

2. **Mutation declining from 46% → 40% share.** Its hall-of-fame is saturating. Expected behavior — mutation refines known chains but can't discover new corridors.

3. **All strategies still hit the 0.659 ceiling.** Confirmed as a scoring formula artifact (M2 broke it with compression+sensitivity fixes). M1 daemon uses the original scoring weights.

4. **Rate stable at ~13K chains/hour.** Will test ~390K chains over 30 hours total.

### Top Discovery Corridors

| Organism Pair | Cracks | What It Means |
|---------------|--------|---------------|
| scipy_special → numpy | 1,127 | Special functions → array transforms (most productive corridor) |
| scipy_special → scipy_signal | 390 | Special functions → signal processing |
| numpy → statistics | 365 | Array transforms → statistical summaries |
| chaos_theory → numpy | 250 | Chaos dynamics → array operations |
| numpy → statistical_mechanics | 206 | Array transforms → physics |

### Top 5 Unique Compositions

| Quality | Chain |
|---------|-------|
| 0.659 | `scipy_special.u_roots → signal_processing.autocorrelation` |
| 0.659 | `network_science.community_detection_simple → numpy.tanh` |
| 0.659 | `topology.euler_characteristic → statistics.erf` |
| 0.659 | `statistics.median → math.sin` |
| 0.659 | `numpy.isposinf → signal_processing.autocorrelation` |

### Observations

- **Tensor guidance is durable.** After 116K chains, tensor_topk still beats random 3.4x. This isn't noise.
- **Mutation's decline was predicted.** It exploits known-good chains but can't discover new corridors. Tensor and temperature anneal are the exploration engines.
- **MAP-Elites stuck at 4/64** — strategies are only producing length-2 chains with scalar/array outputs and low organism diversity. Need length-3+ chains to fill more cells. Could be addressed by adding a chain-length annealing strategy (Strategy 20 from mega-prompt).
- **Frontier seeking is dead** (14 cracks in 9 hours). Its curiosity bonus decays too slowly — by the time it explores an unpopulated region, the chain usually fails on type mismatch. It needs the scoring fix from M2 to be useful.

---

## Ignis Stage D — CMA-ES Evolution

| Metric | Value |
|--------|-------|
| Status | **Stalled or not started** |
| Stage D directory | Empty (created but no checkpoints) |
| GPU processes | Not visible in task list |

Stage D may have crashed or never launched. The directory exists but contains no output. Need to investigate and restart if the GPU is free.

---

## What M1 Needs From Other Machines

1. **M2's scoring fix** — The compression+sensitivity scoring that broke the 0.659 ceiling. If we port it to M1's daemon, the strategies can differentiate on quality, not just execution.
2. **M3's building blocks** — The 3,814 amplified cracks from BB transfer. If we feed M3's top building blocks into M1's mutation strategy, mutation gets fresh seed material.
3. **M4 results** — The 2×2 factorial answer: are scoring fix + building blocks multiplicative?

---

## Projection

At current rates:
- **30h total**: ~390K chains, ~14K cracks, tensor_topk as long-term winner
- **Main bottleneck**: scoring ceiling (0.659) limits quality discrimination
- **Main opportunity**: port M2 scoring fix → unlock quality stratification → strategies can compete on quality not just execution rate
