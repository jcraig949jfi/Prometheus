# W2-D test (b) plan: plant-seeded C1 GA at 6f82f9c7 (written BEFORE the run)

Written 2026-10-01 after tests (a) and (c) and before any seeded GA run.

Design
- Cell 6f82f9c7d51bcef1 (FLIP d3 at d9cc), its own SearchSpec (pop 96, M 8, elite 4, trunc .25, p_field .04,
  p_instr .15, p_swap .10, p_cross .30, M_final 16, M_held 64, w_contrast .10, w_any .02), CPU, 2 threads.
- Loop = verbatim copy of search.evolve (gens loop, truncation/elitism, mutate/crossover, final re-evaluation,
  champion by training accuracy, held-out on HELD_NS) with two changes only:
  (1) gen-0 population = search.random_genomes(rng, 96, ph) with index 0 overwritten by the H-PLANT P-FLIP plant
      (same RNG consumption as C1, so seed A's other 95 genomes are C1's own gen-0 genomes);
  (2) gens reduced 36 -> 4 because one generation costs ~86 s wall / ~157 CPU-s at 2 threads on CPU, and
      4 gens + final + held fits the 10 min per-run cap. twin_assay is skipped (not needed for retention).
- Runs: A = C1's own search_seed 1501831517; B = H_int(1501831517, 0x5732). Two runs, not three (CPU cap 1.0 h).
- Logged per gen: plant exact-present?, plant fitness rank, #genomes with train acc >= .90, best_acc, max_acc,
  mean_acc, and the 4th-best non-plant fitness.

Predictions (from (a), (c) and H-PLANT flip_score pairs)
- P1: the exact plant stays in the elite every generation in both runs (shaped-fitness gap ~.4; P(plant 4-pair
  mean < .80) = .00025 by bootstrap of H-PLANT's 128 pairs, and a non-plant would need acc > ~.70).
- P2: final champion is the plant or a neutral descendant, held acc >= .90.
- P3: the count of acc >= .90 genomes grows slowly (mutate() keeps function in ~6% of offspring, test (a)).
Readings
- P1 and P2 hold in both runs -> U (instability under selection) is EXCLUDED for this plant at this cell for
  the tested horizon; extrapolation to 36 gens is by the per-generation loss bound, stated as inference.
- Plant lost in any run -> U is a live link; report the generation and the displacing genomes' accuracy.

## Deviation logged after run A (before run B)
Run A took 847 s wall / 1455 CPU-s (host shared with other processes; ~110-150 s per generation), so it
exceeded the 10 min cap by ~4 min. To stay inside the 1.0 CPU core-hour cap, run B is cut to gens=2
(not 4). No third run.
