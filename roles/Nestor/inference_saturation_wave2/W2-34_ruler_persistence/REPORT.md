# W2-34: the zero-register ruler in a carried-register world (C-A3 post-takeover "collapse")

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Files:** `mut_regime.py/.json`, `mut_regime_lfixed.py/.json`, `q4_reading_b.py/.json`.
> - **Run:** started 02:29Z, finished 02:36Z. Each script under 5 CPU-s. No processes killed.

## Answer
The requested re-screens **cannot run**. No genome bytes or registers were saved for any C-A3 run. Deciding statically instead:

1. **"L stays at 1.0" is uninformative.**
   - The pair-tape population is closed: 256 organisms at every checkpoint in all 26 X-MAT replays, with no placements.
   - Once L_share = 1.0 there is no non-L writer left, so it cannot fall. 11 C-A3 runs reach L = 1.0, and **0/11 ever drop back**.
2. **Run 52's collapse looks material, not a ruler artifact** (moderate-low confidence). The world's own material tags change regime at the same moment the zero-context competent count reaches 0:
   - The MUT share falls between epochs 1200 and 1600 (mean −0.0145 per 100 epochs). That is the purging seen in copier sweeps.
   - It then rises after 1600 (+0.031, +0.043, +0.033, +0.023; mean +0.032). That matches runs with no zero-competent genomes (residual +0.0006, 0.07 SD).
   - The rise exceeds every competent-class 4-interval block (0/15) and 33/35 blocks from L-fixed persistent runs (P = 0.057).
   - A weaker artifact reading is not excluded: carried-register copiers that persist but no longer purge.
3. **In the other takeovers, the world's own carried-register ruler agrees with the zero screen in 3 of 4.**
   - P-11 runs on the actual pre-interaction registers (`world.py:792-793`).
   - Its maximum causal depth bounds any hidden carried-state copiers: 7ae3 27000000 depth 5; 27000009 depth 5; ffa6 27000053 depth 11, never out of zero-competent genomes (8–33).
   - 7ae3 27000008 (depth 86) is undecidable: it has no tag replay.
4. **Reading (b) changes neither verdict.**
   - X-A3-SFLINEAGE stays SIGNAL (3/3 under every reading).
   - X-DD-ESTABLISH stays SIGNAL: its `last_competent_member` field is not verdict-bearing (NO_COPY 20/25).
   - **New validity defect in X-DD-ESTABLISH:** "ESTABLISHED" means world causal depth ≥ 20 in *any* lineage.
     - The D0 lineage keeps a live competent member at the end in 0/23 ESTABLISHED runs.
     - 8/23 have zero D0 causal births.
     - If ESTABLISHED had to hold at the end, the verdict would be WEAK_SIGNAL (NO_COPY 28/48 = 0.58). This is the worker's extension, not reading (b).

## What is on disk

| source | contents | genomes or registers? |
|---|---|---|
| `c_a3_internalize/results/*.json` (144) | depth, d0_epoch, d0_free[]; per 100 epochs: L_share and distinct-genome counts (competent, free, free_in_L) | no |
| `x_mat_internalize/results/*.json` (26; includes 52; excludes 7ae3 0000/0008/0009 and ffa6 0053) | the same, plus per-checkpoint tag-class byte counts (D0, PRE, MKL, MKN, MUT, OTHER) | tags only |
| `W2-14 banks.pkl` | 7ae3-cell contexts | wrong cell and wrong VM for ffa6 |
| lineage, P-11 records, caches | memory only | — |

Note: "112 at 1200" is the **free** count. At that point there are 120 competent distinct genomes, carried by 150 free organisms in L.

## Run 52 (ffa6)

| epochs | zero-context competent | MUT share | Δ per 100 epochs |
|---|---|---|---|
| 1200→1600 | 120, 92, 68, 10, 12 | 0.598→0.540 | −0.020, −0.051, +0.043, −0.030 |
| 1600→2000 | 12, 0, 0, 0, 0 | 0.540→0.672 | +0.031, +0.043, +0.033, +0.023 |

**Reference intervals** (ffa6, MUT level 0.45–0.72):

| class | intervals | mean Δ | Δ < 0 |
|---|---|---|---|
| no competent genomes | 27 (8 runs) | +0.034 | 0.04 |
| ≥ 50 competent | 31 (8 runs) | −0.022 | 0.61 |
| ≥ 50 competent and L = 1.0 | 18 | +0.0085 | |

## Q2 takeovers

| run | depth | L | zero-competent | reading |
|---|---|---|---|---|
| 7ae3 0000 | 5 | 0.72 | 0, 0 | no heredity by either ruler |
| 7ae3 0009 | 5 | 0.58–0.78 | 0 in 17/18 | the zero screen's blank is correct |
| 7ae3 0008 | 86 | 1.0 from 700 | 114 → 3 → 0 (×11) | **undecidable** |
| ffa6 0052 | 39 | 1.0 from 1000 | 120 → 0 after 1600 | material regime change |
| ffa6 0053 | 11 | creeps 0.18 → 1.0 | 8–33 throughout | absorbing label |

## Adversarial round
1. **Neutral copying would not lower MUT either.** Fair. But L-fixed copier populations hold MUT nearly flat (+0.0085), and run 52 leaves that band. This narrows the artifact reading; it does not kill it.
2. **The reference classes are zero-screen-defined.** The argument rests on a regime change *within* the run.
3. **Level confound.** Saturation would lower the expected Δ, which strengthens the match.
4. **D12 flicker.** No: `run_de.competent` seeds on sha256, so the result is deterministic per genome.
5. **n = 1, and checkpoints are autocorrelated.** The P values are descriptive.
6. **Depth bounds only chains**, which is why 0008 stays undecided.

## Ledger entry (W2-34)
- **Inference.**
  - Run 52's collapse coincides with a material regime change, so it is not a pure ruler artifact.
  - In 3 of 4 other cases the carried-register ruler also shows no deep heredity.
  - **Withdraw "L stays at 1.0" as evidence everywhere.**
  - Neither verdict changes under (b).
  - X-DD-ESTABLISH's ESTABLISHED describes the world, not the D0 lineage.
- **Confidence.**
  - High: absorption, the inventory, Q4.
  - Moderate-low: run 52 is material.
  - Low: 0008.
- **Strongest objection.** Carried-register copiers might persist without purging; the tags cannot see neutral copying.
- **Next.**
  - Replay ffa6 52 (epochs 1600–2000) and 7ae3 0008 with genome and register dumps, deterministically, about 5–8 CPU-min each.
  - Add the absorbing-L note to N13.
  - File the X-DD-ESTABLISH defect in the W2-15 matrix.
