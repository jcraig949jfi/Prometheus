# W2-38: replays of ffa6 27000052 and 7ae3 27000008 with genome and register dumps

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Run window:** 02:38:08Z–02:57:00Z. At most about 26.5 CPU-min.
> - **Processes:** PIDs 150259 and 150260 were started and recorded, and both exited normally. Nothing was killed.
> - **Files:** `replay_dump.py`, `rescreen.py`, `cross_context.py`, `replay_*.json.gz`, `rescreen_*.json`, `cross_context.json`, `log_*.txt`, `pids.txt`. All are under 100 KB.
> - **Search disclosure:** one early `find . -type d -name c_a3_internalize` ran from the worktree root before the exclusion rule arrived. It walked directory names only, read no contents and listed no holdout paths. Nestor appended this to comms #1218.

## Answer
**Both collapses are real.** When the zero-register count reaches 0 for good, competence is gone under every context. The world's own P-11 counter, which scores every interaction in its actual carried registers, also stops. L stays at 1.0 over a population that has stopped copying.

- **Run 52 (ffa6): no ruler artifact at any checkpoint.**
  - The zero, own-register and realized-register screens agree.
  - From epoch 1700, competent = 0 under every context, and conversion is 0/512.
  - World P-11 events: 400 in 1600→1700, then 0, 0, 0. This confirms W2-34.
- **Run 0008 (7ae3): one artifact checkpoint (900), then a real collapse by 1000.**
  - At 900 the zero screen sees 1/64, while carried or realized contexts find 29 more competent organisms.
  - Conversion at 900 is 92/504 among organisms that fail the zero screen.
  - World P-11 events: 3,602 in 800→900 and 2,147 in 900→1000, while the recorded zero-competent count reads 3 and then 0.
  - From 1000, every context gives 0/64 and conversion is 0/512. World P-11 events per 100 epochs are then 3, 0, 0, 0, 1, 0, 2, 0, 0, 0.
- **N13.**
  - The mechanism exists: carried-state copiers invisible to the zero screen occur (0008 @900).
  - It does not sustain the lineage. The zero-context collapse lags or matches a real end of heredity by at most one checkpoint.
  - N13(iii) is refuted for run 52. N13(ii) is unsupported in both runs.
- **C-A3's "transient" events.** Run 52's transience is a real end of copying. After it, the population has 256 distinct genomes and about 0 causal births.

## Bit-exactness: PASS
- Both replays are byte-identical to `c_a3_internalize/results/*.json`.
  - ffa6 52: depth 39, 19 checkpoints, 844.9 s wall.
  - 7ae3 0008: depth 86, 16 checkpoints, 635.7 s wall.
- The reimplemented screen matches the world's cache on all 768 screened organisms, with 0 mismatches.

## Table 1: the world's carried-register ruler (P-11 events per 100 epochs)

| ffa6 52 (epochs) | 1100–1200 | –1300 | –1400 | –1500 | –1600 | –1700 | –1800 | –1900 | –2000 |
|---|---|---|---|---|---|---|---|---|---|
| P-11 events | 5241 | 5962 | 4464 | 1803 | 1825 | 400 | 0 | 0 | 0 |
| zero-competent (recorded) | 120 | 92 | 68 | 10 | 12 | 0 | 0 | 0 | 0 |

| 7ae3 0008 (epochs) | 600–700 | –800 | –900 | –1000 | –1100 | 1100–2000 (each) |
|---|---|---|---|---|---|---|
| P-11 events | 4337 | 3268 | 3602 | **2147** | 3 | 0–2 |
| zero-competent (recorded) | 97 | 114 | **3** | **0** | 0 | 0 |

## Table 2: re-screen of 64 L organisms per checkpoint (L = 256/256 throughout)

Context columns:
- **ZERO:** zero registers on both sides.
- **OWN:** the organism's own carried registers, zero partner.
- **REAL:** own registers against a realized partner.
- **INHER:** both drawn from the population.
- **hidden:** fails ZERO but passes some other context.

Conversion columns use world-rule conversion: a realized pair, predecessor-accepted and P-11-passing, with 8 partners each.

| run | epoch | ZERO | OWN | REAL | INHER | hidden | conv (all) | conv (zero-competent) | conv (not zero-competent) |
|---|---|---|---|---|---|---|---|---|---|
| ffa6 52 | 1200 | 42 | 41 | 39 | 42 | 3 | 121/512 | 114/336 | 7/176 |
| | 1500 | 8 | 8 | 8 | 8 | 0 | 18/512 | 18/64 | 0/448 |
| | 1600 | 2 | 2 | 2 | 1 | 0 | 8/512 | 8/16 | 0/496 |
| | 1700 | 0 | 0 | 0 | 0 | 0 | 0/512 | – | 0/512 |
| | 1800 | 0 | 0 | 0 | 0 | 0 | 0/512 | – | 0/512 |
| | 2000 | 0 | 0 | 0 | 0 | 0 | 0/512 | – | 0/512 |
| 7ae3 0008 | 700 | 25 | 23 | 21 | 12 | 0 | 62/512 | 62/200 | 0/312 |
| | 800 | 28 | 25 | 25 | 15 | 3 | 59/512 | 49/224 | 10/288 |
| | **900** | **1** | 15 | **27** | **28** | **29** | **92/512** | 0/8 | **92/504** |
| | 1000 | 0 | 0 | 0 | 0 | 0 | 0/512 | – | 0/512 |
| | 1500 | 0 | 0 | 0 | 0 | 0 | 0/512 | – | 0/512 |
| | 2000 | 0 | 0 | 0 | 0 | 0 | 0/512 | – | 0/512 |

## Table 3: cross-context (INHER rule, 32 genomes)

| genomes | in states @900 | in states @1000 |
|---|---|---|
| 7ae3 @900 | 15/32 | **0/32** |
| 7ae3 @1000 | **0/32** | 0/32 |
| 7ae3 @800 | | 1/32 |

| genomes | in states @1600 | in states @1700 |
|---|---|---|
| ffa6 @1600 | 2/32 | 2/32 |
| ffa6 @1700 | 0/32 | 0/32 |

- In 0008, both the register environment and the genomes changed between 900 and 1000.
  - The 900 copiers depend on carried HL. The modal HL moves from 0x0114 to about 0xFEFF.
  - The 1000 genomes fail even in the 900 environment.
  - The order of the two changes cannot be resolved at 100-epoch resolution.
- After both collapses, 256/256 genomes are distinct. Predecessor-accepted replications fall to 2–10 per 100 epochs.

## Adversarial round
1. **"Sampling 64 organisms could miss rare-context copiers."** Table 1 is exhaustive: the world scores every interaction.
2. **"P-11 misses lower-fidelity heredity."** Partly true. Copying below 0.9 is not measured. Predecessor-accepted replications are also about 0.
3. **"Organisms vs distinct genomes."** Zero is zero in both units.
4. **"0008 at 900 vindicates N13."** It is a lag of about one checkpoint before a real end.
5. **"The screen differs from the world's."** It matches 768/768.
6. **"n = 2, and both are hard cases."** Yes. Generalizing to the other runs relies on W2-34's depth argument.

## Ledger entry (W2-38)
- **Inference:**
  - Both collapses are real.
  - 0008 has one lag-artifact checkpoint.
  - L = 1.0 labels a non-replicating population.
  - Run 52's C-A3 transience is a real end.
  - N13's mechanism exists but is short-lived. N13(iii) is refuted; (ii) is unsupported.
- **Confidence:**
  - high that the collapses are real;
  - moderate that the 900 artifact is only about one checkpoint long.
- **Strongest objection:** heredity below 0.9 fidelity is unmeasured.
- **Next questions:**
  1. Dump 0008 every 10 epochs over 900–1000.
  2. Use the world P-11 counter as the persistence ruler across all 144 C-A3 runs.
  3. Make a per-checkpoint world P-11 column mandatory.
  4. Amend N13.
