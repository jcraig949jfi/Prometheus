# M1 Status — 2026-03-28 ~15:00

## Noesis Tournament (CPU)

| Metric | Value |
|--------|-------|
| Runtime | 6.8 hours |
| Total cracks | 7,382 |
| Cracks/hour | 1,090 |
| Max quality | **0.659** (ceiling confirmed — M2 broke it at 0.7137) |
| MAP-Elites cells | 4/64 |

### Strategy Leaderboard

| Strategy | Cracks | Share | Avg Quality | Max Quality |
|----------|--------|-------|-------------|-------------|
| Mutation | 3,420 | 46.3% | 0.561 | 0.659 |
| Random baseline | 1,604 | 21.7% | 0.554 | 0.659 |
| Temperature anneal | 1,405 | 19.0% | 0.554 | 0.659 |
| Tensor top-K | 763 | 10.3% | 0.533 | 0.659 |
| Epsilon-greedy | 176 | 2.4% | 0.555 | 0.659 |
| Frontier seeking | 14 | 0.2% | 0.532 | 0.576 |

### Observations
- Mutation declining from 52% → 46% (archive saturating as predicted)
- Tensor top-K gaining share: 5% → 10.3% (improving as density increases)
- Temperature anneal steady at 19% (exploitation phase hasn't fully kicked in)
- Frontier seeking effectively dead (14 cracks in 6.8 hours)
- All strategies hit identical 0.659 ceiling — confirmed as scoring function artifact by M2

---

## Ignis Stage D — CMA-ES on Corpus-Trained Seed (GPU)

| Metric | Value |
|--------|-------|
| Status | Running, ~5 hours in |
| Generation | ~25-30 (estimated, no checkpoint yet) |
| Fitness at gen 10 | 2.566 (steep climb from 0.606 at gen 1) |
| Speed | ~18 min/gen (EvoTorch CMA-ES params on CPU, model on GPU) |
| ETA gen 50 | Tonight (~21:00) |
| ETA gen 100 | Tomorrow morning |
| Target | Beat SR=0.417 from base model evolution |

### What this tests
Does CMA-ES converge faster on a corpus-trained seed than on the vanilla model?
The corpus-first experiment proved:
- Metacognition +21.4% from training alone (no evolution)
- Self-correction +15.4%
- Ejection profile structurally UNCHANGED (basins are hardware)

Stage D tests whether a model that reasons better within basins gives evolution better signal to find the doorways between basins.

---

## Corpus-First Results (Completed)

| Pillar | Baseline | Post-Corpus | Delta |
|--------|----------|-------------|-------|
| Tier A | 46.7% | 46.7% | 0% |
| Tier B | 50.0% | 50.0% | 0% |
| Tier C (far-transfer) | 42.9% | **52.4%** | **+9.5%** |
| Metacognition | 35.7% | **57.1%** | **+21.4%** |
| Self-correction | 38.5% | **53.8%** | **+15.4%** |
| Composite | 0.335 | **0.427** | **+27.5%** |

Ejection profile: L* median=26 (unchanged). Basins are structural. Performance improves within them.

---

## Cross-Machine Comparison (as of ~15:00)

| Machine | Scoring | Building Blocks | Max Quality | Cracks | Key Finding |
|---------|---------|----------------|-------------|--------|-------------|
| M1 | Baseline | No | 0.659 | 7,382 | Tensor 3x random, ceiling in formula |
| M2 | Fixed | No | **0.7137** | ~1,500 | **Ceiling broken** by compression+sensitivity |
| M3 | Baseline | Yes | 0.660 | ~10,000 | **BB transfer confirmed** (13→3,814 amplification) |
| M4 | Fixed | Yes | ??? | Starting | 2×2 factorial: are improvements multiplicative? |

---

## Files on this machine

- `organisms/cracks_live.jsonl` — 7,382 cracks (M1 tournament data)
- `organisms/noesis_state.duckdb` — tournament database (locked by running daemon)
- `ignis/results/corpus_first/` — all corpus-first stages A-D
- Stage D running, checkpoints at gen 50, 100, 150...
