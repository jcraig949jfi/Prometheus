# W2-19: H1 re-score (A) and D8 vs E-3 (B)

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Files:** `rescore_h1.py/.json`, `d8_vs_e3.py/.json`.
> - **Compute:** about 50 CPU-s, `python -B`. No world evolution, no git writes.
> - **Window:** 2026-10-01 01:22:42Z–01:42:59Z (from `date -u`).

## Answer
- **(A)** The recorded H1 "competence" is a cached single draw. Every H1-cell genome on disk guesses the answer before reading the cue: recorded held 1.0, true held about 0.50.
  - C9-H1R, X-H1-GRADIENT and X-H1-TRANSPLANT saved NO genomes. That is itself a finding.
  - The only H1-cell genomes on disk are C9's 12 H1 `first_cross` genomes. All 4 C9 H1 arms are the same simulation (C9-D16), equivalent to ungated VM.
- **(B)** E-3's depth 2 is not a D8 artifact. Both chains are two distinct interactions in consecutive epochs, with no mutual acceptance and no padding. D8 fires once in 1,031 runs, and only on the predecessor-criterion depth.

## Verdicts

| verdict | recorded | W2-19 |
|---|---|---|
| **X-H1-GRADIENT** | WEAK_SIGNAL ("guessers carry ungated competence") | **W2-15's relabel confirmed, and stronger.** The composition fact stands: no reader ever appears. The competence reading is invalid: a 0.5 echo floor plus cached luck. |
| **C9-H1R** | COST_INTERACTION_ONLY | **DEGENERATE / ARTIFACT-RISK** (W2-15's label). On true scores I ≤ 0.142 (generous) or ≈ 0.125 (strict), both below the 0.15 threshold, so the result would read NO_DETECTED_EFFECT. Robust fact: gated+VM 0/60. The gate cancels the guess floor by construction (exact 0.000 for 11/12 guessers). |
| **X-H1-TRANSPLANT** | SIGNAL | **Fragile, on the SIGNAL/WEAK_SIGNAL boundary, and mechanical.** Strict I ≥ 0.15 in only 2 of 4 transforms. What transplants is "the gate removes the 0.5 echo floor". |
| **E-3** | max P-11 depth 2 (2 runs) | **Stands.** D8 does not apply. |
| A-1 D8 cell | B+ | **Real but negligible.** 1 false depth-2 in 1,031 runs. |

## (A) Numbers

**Re-score method.**
- The world's `tasks.competence`/`score`, with matching specs.
- `val_cache` bypassed.
- 100 fresh 6-episode draws (600 episodes) per genome.
- Exact expected score over all 512 (v, r) inputs.

**Results for the 12 genomes:**

| class | n | recorded held | recorded comp | fresh held | exact ungated | exact gated |
|---|---|---|---|---|---|---|
| answer-before-read | 12 | 1.000 (all) | 0.569 | 0.496 | 0.495 (11 at 0.500, 1 at 0.4375) | 0.0003 |
| reader | 0 | | | | | |

**Single draw.**
- Each recorded held = 1.0 is reproduced exactly by one validation-epoch seed (`run_seed*7919 + e`).
- P(held ≥ 0.90) on fresh draws = 0.01, about 1/64.
- `_competence` returns the same stale object at epoch 600 as at epoch 6. In 11/12 cases it differs from the true draw.

**All 30 answering C9 H1 runs.**
- In every run the best organism has probe < 2, so it answers before reading. There are 0 readers.
- 6 runs at 0.1667 are constant outputters (true score about 1/256).
- 24 runs echo v, with final comp_mean 0.60–0.88. That is above the hard ceiling of 0.5 for any genome that answers before reading.

**X-H1-GRADIENT.**
- 11/20 ungated runs end with ≥ 85% of organisms answering before reading.
- 5 of these record comp 0.72–0.91, which is impossible as true competence. The other 6 are at 0.12–0.14.
- reader_share = 0.0 at all 240 checkpoints.

**Analytic inflation for a 0.5 guesser scored on one 6-episode draw.**
- P(1.0) = 1/64; P(≥ 0.833) = 0.109.
- Expected max over N draws: N=2: 0.61; N=5: 0.73; N=10: 0.80; N=20: 0.86.
- P(any crossing in 100 validation epochs) = 0.79.
- This alone explains held_max_final values of 0.67–1.0.

**I true-score bounds:**

| arm | recorded | generous | strict |
|---|---|---|---|
| H1R | 0.200 | 0.142 | **0.125** |
| TRANSPLANT XOR1 | 0.300 | 0.233 | 0.167 |
| TRANSPLANT XOR15 | 0.200 | 0.167 | **0.117** |
| TRANSPLANT XOR5A | 0.339 | 0.250 | 0.217 |
| TRANSPLANT ADD37 | 0.256 | 0.183 | **0.133** |

## (B) Numbers

These were read only from gitignored per-event files in the `nestor-s1-forensics` worktree. Nothing was written there.

| run | chain | first step | second step | literal reading |
|---|---|---|---|---|
| Run 1 (7ae3…s54765) | 337 → 388 → 391 | epoch 1746, pair 32, 2/3 draws | epoch 1747, pair 148, 3/3 draws | depth 2, still 2 after the D8 correction |
| Run 2 (c2a8…s80949) | 391 → 392 → 393 | epoch 2455, pair 342 | epoch 2456, pair 178 | P-11 passes, literal depth 0 |

- No two events share an (epoch, pair).
- Genomes are a full 64 bytes, so there is no padding.
- Across all 1,031 runs:
  - one same-interaction double birth (860dec…s39457, epoch 2137, pair 382, predecessor depth only);
  - 0 recompute mismatches.

## Ledger entry (W2-19)

- **Inference.**
  - (A) The ungated arm's real competence is the 0.5 echo floor. H1R's I = 0.20 clears the 0.15 threshold only through cache inflation; the true I is 0.125–0.142. The gate effect is mechanical. X-H1-GRADIENT keeps only its composition reading. TRANSPLANT is 2–4 of 4.
  - (B) E-3 stands. D8 on A-1 is negligible.
- **Confidence.**
  - High: the re-scores, the single-draw reproductions, and (B).
  - Moderate: the H1R and TRANSPLANT bounds, because their populations are inferred from C9's identical cell and GRADIENT's probes.
- **Strongest objection.**
  - The C9 genomes come from different seeds than H1R, and `first_cross` is a lucky sample.
  - Class and exact score are independent of luck, and GRADIENT's reader_share = 0 across 20 seeds. So a missed reader in H1R is unlikely, but not excluded.
- **Next.**
  - Re-run H1R with P1 (cache key = genome + spec), a fresh or exact readout, and saved genomes.
  - Should held_max_final (a maximum over single draws) be replaced everywhere it is used (A-2, X-TASK-GATE)?
  - Does any cell give an ungated-VM reader a gradient?
