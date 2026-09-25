# eta2 -- does the cost-line boundary sampler earn its place? -- PREREGISTRATION

Written 2026-09-23 ~15:27Z, before running. Charter s X: "A sophisticated boundary sampler that cannot
beat simple baselines is not yet earned complexity." C0 found the kernel ACTIVE sampler unearned
(ties random). C1/C2 then used COST LINES (bisection along matched cost lines) without measuring them.

Design (prometheus/cosmos/eta2.py): pools of 600 worlds per visible family (seed 20260930); a private
oracle labels every pool world. Per seed (1, 2, 3), two arms with MATCHED query counts per family:
  RANDOM   q random pool worlds
  LINES    3 random pool worlds as line bases -> costlines() (~17 queries each), topped up with random
           pool worlds to the same q as RANDOM (q = the LINES count, computed per family per seed)
Law: Miner.search on the arm's rows (v4 coordinates; LOLO over families; no null -- same as the C0
eta protocol), refit on all rows. Metrics: (1) balanced accuracy of the law on the oracle pool;
(2) location offsets via locate() (4 bases/family, 800 episodes) -- worst family |offset|.
Prediction (conf 0.4): LINES beats RANDOM by >= 0.02 mean oracle BA OR by >= 0.05 lower mean worst
|offset|; otherwise cost lines are NOT earned by this test. Three seeds only: this is a small test and
is reported as such.

## RESULT (2026-09-23T15:35Z; ETA2.json)
Matched queries per family (~105 rows per arm): mean oracle BA RANDOM 0.946 vs LINES 0.767 (every
seed: .938/.850, .965/.613, .936/.839); mean worst location offset RANDOM 0.376 vs LINES 0.364 (both
poor at this data size; several families INDETERMINATE). Prediction LOST: cost lines alone are NOT
earned as a sampler -- three bases' worth of lines buys boundary detail and loses coverage.
Consequence for C2: C2 used cost lines ON TOP OF 80 random worlds per family; whether the lines or the
location-aware selection produced the well-located law is NOT isolated (ablation: campaigns/c2abl).
