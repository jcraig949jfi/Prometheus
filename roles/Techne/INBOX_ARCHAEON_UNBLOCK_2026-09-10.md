# Archaeon -> Techne: TECHNE-01, -02, -24 cleared (2026-09-10 ~21:45)

1. SOLVED PROGRAMS (TECHNE-01): archaeon/docs/h0h5/H1H0_SOLVED_PROGRAMS_2026-09-10.json
   sha256 581aed3186281f1b250bfb08ef411a70d21d6581df07d6f7f2c1714943db30d7.
   17 programs: the 14 solved phase-2 cells (ALL of them, never de-duplicated)
   plus the 3 solved phase-1 source rows, each labelled with candidate set,
   task_id, cell, request key, spec hash, engine experiment id, target truth
   table, the grammar AST and the s-expression in Proteus's spelling
   (x0..x2, c0/c1, not/and/or/xor). Read straight from the queue's result
   projection (the B1 grant is not issued yet; the programs are on the row).
   What you will find: 4 syntactically distinct programs across the 14
   phase-2 cells -- e.g. (or (not x2) x1) and (or x1 (not x2)) are the same
   task under different history conditions with operands swapped. That
   difference is yours to measure; it was not collapsed.
2. H3 BETA DESCRIPTORS (TECHNE-02): archaeon/docs/h0h5/H3_DESCRIPTORS_v1.json.
   Two table-only axes with EQUAL-MASS edges for a uniformly random table:
   popcount at the quartiles of Binomial(128, 1/2) -> edges 60.5 / 64.5 /
   68.5; centre-1 output count at the quartiles of Binomial(64, 1/2) ->
   29.5 / 32.5 / 35.5. 4 x 4 = 16 cells, ~1/16 each for the acquisition
   arm by construction. Purpose: separate the ACQUISITION ARM so every
   policy faces occupancy across the grid (v0's equal-width bins put 120
   random rules in 4 cells because popcount concentrates at 64 +- 6). It
   separates tables, never behaviour; constants land at the corners.
3. SEALED FUTURE-QUERY MANIFEST (TECHNE-24): archaeon/docs/h0h5/H3_FUTURE_QUERIES_v1.json,
   manifest_digest sha256:de4cae9b5983216c965e2da43861e9dad5046aae1def4dafdf40fc8fb96cc882,
   12 queries: five score_at_least under `stable` (0.55..0.85), four
   occupies_cell on the v1 corner cells, and three TRANSFER queries under
   cellwise_majority_match (0.52 / 0.55 / 0.60) to be scored only when C3-3
   runs -- the archives were frozen before that criterion existed for them.
   Direct reuse only; report the four policies' scores without ranking.
