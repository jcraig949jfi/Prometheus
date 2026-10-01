# C4 R-STAT: notes to carry into the FINAL (Ananke; not a review; no Cosmos/Bellerophon review read)

## N1 (2026-10-01): A4 magnitude correction
- The INTERIM (ded6f5729) A4 gives "~1 - .95^10 = .40" for a universal law failing S2 (c). That is an
  independence bound for (c) alone, so it is an OVERSTATEMENT. The 10 per-family CIs are compared with a
  pooled fit that includes each family, so they are positively dependent and individually less likely
  to exclude it.
- A synthetic simulation by Wave-2 worker W2-H, read by me:
  - code roles/Ananke/research/harvest/wave2/W2-H/c4_s2_sim.py, output out/c4_s2.json;
  - logistic universal law, 5 families with shifted coordinates, literal 95% readings, 400 reps;
  - arm (c) alone false-fails 14-22%; any S2 arm 26% (n = 160) and 31% (n = 240); 21-23% with a 1-SE
    margin;
  - arm (e) CMH is miscalibrated 3-5x;
  - corrected rule (family-wise .05, Bonferroni, BA noise allowance): 3.5-4%.
- FINAL wording: "a universal law false-fails S2 in ~21-31% of simulated studies (literal readings);
  still BLOCKING against the target pass rate >= .80". Cite the simulation, and report the correction of
  the INTERIM's .40 explicitly.
- Caveat: synthetic, no C4 data; power against family-specific laws not yet simulated (W2-H next
  question 4).
