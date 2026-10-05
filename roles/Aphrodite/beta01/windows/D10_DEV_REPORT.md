# DEV-10 REPORT (C-006 Beta-01, cycle 10)

Opened 2026-10-05T13:12Z, after TEST-9 closed. Closed 13:20Z with T10 frozen.

## 1. Starting point (the actual T09 result)
T09 was MEASURED and not R7-positive; the NULL gate passed.
- g0 and g10 select the same schema in 14/15 seeds.
- The empty seeds split into:
  - **candidacy** failures in 4 seeds: 0, 7 and 12 derive nothing; 9 derives the wrong class;
  - **validation content** in 1 seed (14).
- No seed shows criterion failure.
- On the fresh draw, g0 reaches 93, against 76 on T08's draw. **The R3 criterion is not the dominant limit on fresh
  supply.**

## 2. The first broken rung
**R2, candidacy.** In 3 of 15 seeds the improver's 4 OBSERVE families yield 1-3 observations at escrow 30k. That is
too few for class certification, so no candidate exists for any rule to select.

## 3. One discriminating experiment (operator order s17: one fix at a time)
**T10:** OBSERVE 4 -> 10, with fresh families. Everything else is fixed at T09 (the g10 rule, the validation draw,
TRANSFER, escrow, the endpoint).
- It separates observation quantity from the derivation step itself. If more observations do not create candidates
  in the starved seeds, the limit is LGG/certification (the derivation representation). That direction is
  W5P-adjacent and stays design-only without authorisation.
- Not chosen:
  - seed 14 (validation content): a single seed;
  - a second criterion change: excluded by T09;
  - seed 9's wrong class: it rides along in T10's readout.

## 4. Pre-freeze controls
- **Supply:** 6/6 fresh OBSERVE families in 15/15 seeds. No name collisions; the roles are OBSERVE 10, VALIDATE 12,
  TRANSFER 32.
- **Known-answer continuity:** the new runner, applied to T09's roles, reproduces T09's g10 rows exactly in seeds 0
  and 3 (6 fields).

## 5. Frozen
beta01/windows/T10_OBS_SPEC.md. Runner t10_observe.py, sha256 9ced6b98....
