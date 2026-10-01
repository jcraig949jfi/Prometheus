# W2-AK plan for test (b), plant-seeded GA (frozen before any seeded run; deviations appended below)
Written 2026-10-01 ~03:35Z, after the known-answer gate and test (c), before any GA run.

Script: t_b_seeded.py (W2-D's verbatim copy of search.evolve with gen-0 index 0 := plant; only additions are
logging and a third seed C = H(seed, 0x5733)). Cell SearchSpec unchanged except `gens`. CPU eager, 1 thread.

Bench (1 thread, host at 100% load): one 96x8 generation = 128 CPU-s at 8743da7f, 31 CPU-s at f29ca123.
Final 96x16 re-evaluation = 2 generations' cost. Cap 0.8 core-h = 2880 CPU-s total for all W2-AK work.

Planned runs (each must stay under 10 min wall):
- 8743da7f (INT_1 plant): gens 36 -> 2 (one selection+mutation round; final eval alone costs ~256 s).
  Runs A, B first; C only if the CPU ledger leaves >= 600 CPU-s after A, B and all f29c runs.
- f29ca123 (LEAK3 plant): gens 36 -> 6. Runs A, B, C.
Retention criterion (W2-D section 2, U): champion == plant, or a neutral descendant with held lo99 > .55.
I additionally record the champion's line distance to the plant.
Predictions: P1 plant rank 0 (or within elite 4) at every generation; P2 champion = plant or descendant with
held lo99 > .55; P3 at 8743 the margin is smaller than at FLIP (plant f .76-.80 vs champion f ~.67-.70 on
8 worlds), so the truncated horizon is a WEAK test of U there: random gen-0 genomes are at ~.5, the threat is
later champion-like competitors, which the per-generation loss bound (t_v_ruler.py) must cover.
F-U (W2-D): loss of the plant (champion held lo99 <= .55) in >= 1 of 3 seeds => link U.
