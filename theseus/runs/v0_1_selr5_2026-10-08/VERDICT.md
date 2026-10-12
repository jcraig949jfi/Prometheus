# THESEUS-27 verdict (prereg roles/Theseus/prereg/2026-10-08_structure_selection/, 0b8e3740b)

Runs (PYTHONHASHSEED=0, ecology-only, --pop-cap 300 --elite-grids pca --dark-protect-gens 3):
  SEL-REP v0_1_selrep_2026-10-08 (--quality rep): ecology wall 1290 s
  SEL-R5  v0_1_selr5_2026-10-08  (--quality r5)

VERDICT: VOID by the frozen rule -- the cap did not bind to the preregistered standard
(max active <= 300 + one generation's births = 345). Max active 390 in both runs.
Primary outcome (H1) therefore NOT computed.

Failure shape (POPULATION_HISTORY.jsonl): the cap held at 300 from generation 11 to ~20
(fossilised 618 / 608 in total), then the protected pca-elite set itself outgrew the cap
(275 -> 305 occupied cells); protected entities cannot be fossilised, so active rose to
390. QD elite protection and a fixed cap are incompatible once the archive fills.
Manipulation check also FAILED: median R5 of viable deep children SEL-R5 .727 vs SEL-REP
.773 (difference -.045 [-.045, .045]); rho(generation, R5) -0.002 vs -0.001
(R5_TREND_vs_selrep.json).

Why selection could not move R5 (descriptive, post hoc): R5 is weakly heritable through
collisions -- Spearman(parent mean R5, child R5) .142 [.066, .203], slope .22 (v0_1);
.182 [.111, .249], slope .30 (SEL-R5). Selection acted only through which entity stays
elite per cell, never through parent choice, so the selection differential was small.

Predictions: S1 (cap binds) WRONG; S2 (manipulation passes) WRONG; S3, S4 unscorable (VOID).
Successor THESEUS-27b: cap that counts elites (protect only the top-k elites by quality,
k <= cap/2) + selection at parent choice (coalition seed weight by quality rank).
