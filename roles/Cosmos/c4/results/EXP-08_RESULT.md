# EXP-08 RESULT -- surrogate one-step GAIN (INSTRUMENT; 2026-10-11)

Prereg: prereg/EXP-08_SURROGATE_GAIN.md (14def4110; includes a disclosed one-system peek before commit, rules
unchanged). Run 06:31Z-06:35:45Z under supervise (DONE, 0 restarts). 38 planted systems. Data
EXP-08_planted_gain.jsonl (sha256 be90df2b453e6fac...).

VERDICT (by rule): **H-GAIN REJECTED**. Median (rho_fit - a) at a .95 = +.071 (rule needs <= -.01);
Spearman(shortfall, EXP-07 O1 error) over a >= .85 cells = -.44 (rule needs >= .50).
Median gap by a: .50 +.192 | .70 +.138 | .85 +.101 | .95 +.071.

Measurement caveat (recorded, not used to soften the verdict): the gap is LARGEST at a .5, where the composed
surrogate is accurate (EXP-06/07 SE ~0). So the median local-Jacobian spectral radius of a random-ReLU-feature map
measures local ROUGHNESS of the fitted map, not its effective gain. H-GAIN is rejected as stated; a valid gain
measurement (e.g. regression of the composed k-step response on the start state) would be needed to revisit it.

Status of the surrogate after EXP-06..08: dominant defect = start-state mismatch (EXP-07, descriptive); residual
~-.04 at high memory UNEXPLAINED; instrument UNQUALIFIED. Line of inquiry PAUSED here: further instrument work on
a surrogate that no current law depends on has low value; recorded in the backlog.
