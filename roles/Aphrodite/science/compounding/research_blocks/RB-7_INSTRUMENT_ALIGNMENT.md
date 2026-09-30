# RB-7 -- INSTRUMENT ALIGNMENT: T4 THRESHOLD SENSITIVITY + RULER/TRIBUNAL DOMAIN AGREEMENT
# (threads T26, T29)

Cheap, autonomous, forensic. Estimated 4-8 hours. Read
science/frontier/research_blocks/RB-00_SHARED_BRIEFING.md first. Then read:
engine/tribunal_t4.py (sha 62aecd9a...), science/compounding/rb1/RULER_V2.md,
science/compounding/rb2/TASK_WORLD_T4_DESIGN.md.

WHY
  Two instruments now judge the same objects on different domains:
    - T4 declares a per-family length domain L_max in 20..200, e.g. 25 for products.
    - Ruler v2's trajectory battery (NEW_TRAJ) folds over lengths 2..40 with no domain.
  Result: the ruler calls length-limited product compositions (e.g. ((acc + {H}) *
  first)) "degenerate" while T4 admits them (K9b vs K11). NOVELTY is therefore
  conservative for products.
  Separately, T4's junk thresholds (K_DISTINCT = 5, MODE_MAX = 0.5, SENS_MIN = 0.2,
  COPY_MAX = 0.9, ABSORB_MAX = 0.9) are judgement calls. RB-2 notes that E1's family
  hA_sub_az sits near the line.

TASKS
  1. Ruler v2.1 (a NEW version; v2 stays frozen for A18/A19): the trajectory battery
     respects a declared domain (use T4.family_profile(...)["L_max"] per instantiation
     with a representative init/final, or a schema-level min). Re-score K9b's 17
     schemas and the K11 compositions under v2 and v2.1. Report every flip.
  2. T4 threshold sweep on the RB-2 census rows (regenerate them with rb2_census.py if
     absent): each threshold at 0.5x / 1x / 2x. Report admissible counts, non-G1
     survivor counts and which bridge-panel families flip. Recommend thresholds with a
     stated rationale, or recommend keeping v1.
  3. Q2 name-dependence (RB-2 risk): the Q2 probe pool is seeded by family NAME, so
     near-threshold families can flip under renaming. Measure the flip rate over 200
     families x 5 names each.
DELIVERABLES: science/compounding/rb7/ (scripts, RB7_RESULTS.json, INSTRUMENT_ALIGNMENT.md).
Propose any new instrument version as a draft for Aphrodite to freeze. Never edit
tribunal_t4.py or ruler_v2.py in place.
