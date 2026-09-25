# C-SELFLOC -- CONFIRM lane (fresh, frozen)

Experiment id `C-SELFLOC`, parent `X-SELFLOC-SEEDED` (EXPLORE, classified
PHYSICS_SUPPORTS). **Nothing below may change after this file and `run_c.py` are
committed:** not the cells, the seeds, the arms, the endpoint, the threshold or the
allocation.

**Claim under test.** In the FREE non-pair physics, with in-place per-epoch mutation, an
implanted ALLOC;LDIR;BIRTH copier sustains causal replication lineages when
self-location is provided (HL = own base, BC = own length at each slice). Removing that
self-location abolishes the replication. Exploratory evidence: causal depth >= 3 in 5 of
23 cells with self-location against 0 of 23 without; maximum depth 11.

**Fresh sample.**
- Cells: for each of ENDOGENOUS_COPY, ENDOGENOUS_PARTIAL and CONSTRUCTIVE, the first 12
  tier-M, copy_primitive BLOCK cells in `REPLAY_SELECTION.json` order that the EXPLORE
  experiments did NOT use. That is 36 cells.
- Seeds: 9,800,000 + k (never used before). Tier M, full length.

**Arms (shared seed per cell):**
- SEED_LOC: search, free self-location and the implant (as in X-SELFLOC-SEEDED);
- SEED_ONLY: search and the implant, with no free self-location (the causal ablation).

**Primary endpoint:** per run, `max_causal_replication_depth` >= 3.

**Decision rule (frozen):** CONFIRMED iff all three of
1. SEED_LOC reaches depth >= 3 in >= 4 of 36 cells;
2. SEED_ONLY reaches depth >= 3 in 0 cells;
3. the one-sided Fisher exact test of depth >= 1 counts (SEED_LOC > SEED_ONLY) gives
   p < 0.01.

Otherwise NOT_CONFIRMED, reported with the exploratory numbers beside it. The counts at
depth >= 1 and >= 5 are secondary readouts.

**Scope of any confirmed claim:** the implanted copier only. It says nothing about
spontaneous discovery.
