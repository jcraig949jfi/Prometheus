# W2-Q plan (written 2026-10-01 ~01:45Z, BEFORE any run)

Namespace 0x5751 ("W2Q"), fresh worlds, mirror pairs (assays.evaluate semantics), CPU eager,
graph=False, 2 threads, 16 pairs (32 worlds) per condition. Conditions for one cell are batched
into ONE World (schedules tiled along the world axis; same world seeds per block) so every edit is
paired against normal on identical worlds.

## Task 1: distractor-strobed HOLD memory, 86 champions (held lo99 > .60, as W2-E a9)
Conditions (applied to the schedule only):
- N  normal.
- A  first awake gap tick silenced (W2-E a10 definition: sync -> first gap tick with t % P == 0;
     async -> first raw gap tick).
- B  timing jitter. NOTE: HOLD writes a distractor on EVERY gap tick, so "same count, jittered
     timing" is infeasible at full occupancy. Closest count-fixed jitter: per trial, exactly
     k = ceil(n/2) of the n awake gap ticks (sync) or raw gap ticks (async) keep their distractor,
     positions uniform at random; the rest are silent. Per-trial attribution is recorded (was the
     first awake slot silent?), so B can be split into "first slot present" vs "first slot silent".
- C  magnitudes randomised: |distractor| ~ U{1..255} per tick, sign kept.
- Z  amp_dist 0 (reference, replicates a9 on my seeds).
Collapse := paired hi99(cond - N) < 0 AND acc(cond) < .60.

Predictions:
- P1. The 5 W2-E distractor-dependent cells (2c300c47, 0c18ce5e, 0a3f6b87, 311c465f, 41fcb232)
  collapse under A or B. Specifically 2c300c47 and 0c18ce5e collapse under A and (partly) under B;
  311c465f collapses under B and C (parity clock entrained by train size), not necessarily A.
  0a3f6b87 (.935 -> .750 at Z) may not fall below .60 under any edit (significant drop, no collapse).
- P2. 0-3 further cells collapse (cells that a9 saw as distractor-neutral because a9 removed ALL
  distractors, which some cells may tolerate while failing on partial trains).
- P3. Fraction of HOLD SIGNAL that is schedule-triggered/clocked: about 5-8 / 86 (6-9%).
- P4. C (magnitude randomisation) collapses 2c300c47/0c18ce5e only partially (they failed at
  specific amplitudes 63/65/128, so random magnitudes hit failing patterns on a minority of ticks).

## Task 2: rule-mosaic lottery (setrule=0, rules>1)
Cells: 8 C1 SIGNAL evolve rows with setrule=0, rules>1 (0187372b, 8d1c8213, b32bbf91, 7ca102eb,
83d0ff56, cdf60380, b4e404f6, 4ecdfb3f) + 7 near-SIGNAL (held acc >= .56, lo99 > .515).
Conditions: normal; r pinned to each k in 0..rules-1 at all sites (World.r and World.r0 overwritten
after construction; setrule=0 so r never changes). Covariates: actuator r0 per world (computed
from the SAME mirrored world seeds the run uses).
Pre-check found in code: W2-E a1 computed r0 with UNMIRRORED seeds while the run used mirrored
seeds (engine draws r from ws via rng.INIT), so W2-E's acc_by_r0 split assigned wrong r0 to every
odd world. Prediction: the corrected split is sharper than .834/.592.

Predictions:
- P5. In 0187372b and 8d1c8213 one pin reaches >= .90 and is unimodal; the other pin ~.5.
- P6. Most (>= 5/8) SIGNAL cells in this class have a best pin >= normal + .10, i.e. a large
  share of their measured accuracy variance is lottery.
- P7. Some cells use the mosaic (mixed rules) as a resource: best pin < normal for >= 1 cell
  (e.g. one rule senses, the other relays); these are NOT pure lottery.
- P8. Lottery cells are over-represented among C1 fragile/failed reproductions (0187372b census
  change; any D replicate or W-O/W-Z flip cell in this class).

Compute plan: cap 0.5 core-h total (1800 CPU-s). Timing probe first; scale pairs down to 16 if needed.
