# BEL-RD-72 -- pilots and design probes (all excluded from every analysis; seeds 78e6-79e6)

| when (UTC) | probe | runs | result | design consequence |
|---|---|---|---|---|
| 2026-10-10 ~10:05 | K XY_AL 1,000 ticks, one per operator regime | 3 | extinct 3/3 (25-70 s), no competent organism | K seeds doubled to 60; exposure recorded |
| ~10:12 | X/Y survival 300 ticks, LOCAL/WELL_MIXED x K40/K100 | 8 | 7/8 alive at 300; no competence | K setting kept at historical K40 LOCAL |
| ~10:30 | single COND_ONE halves run, 500 ticks | 1 | extinct; 39 s | -- |
| ~10:45 | mutation MED / LOW / VLOW, seeded copiers, COND_ONE ON, 1,000 ticks | 9 | extinct 2/3, 3/3, 2/3: ERROR-CATASTROPHE HYPOTHESIS FALSIFIED (extinction does not follow mutation rate). The surviving MED world held 77 LO half-solvers (68 FUNC) and 1 HI at tick 1,000 -- the first rung of the in-task ladder climbed spontaneously | accumulation runs need a persistence setting found by evidence, not by mutation rate |
| ~11:06 | persistence: LOCAL/WELL_MIXED x lifespan 40/80 x base income 40/64, plain World, 1,000 ticks | 16 | extinct 9/16. Per cell (2 runs each): LOCAL 40/40 1/2, 40/64 1/2, 80/40 1/2, 80/64 2/2; WELL_MIXED 40/40 2/2, 40/64 2/2, 80/40 0/2 (alive 155, 90), 80/64 0/2 (alive 113, 256). Extinction ticks 113-923 | long-horizon runs use WELL_MIXED, lifespan 80, income 40 (4/4 survived; n is small, so survival is recorded and analysed as a covariate, and exposure is reported) |
| 15:21 | E1 (not a pilot; stopped at 16/80): WELL_MIXED / life 80 / income 40 | 16 | 15/16 alive at 2,000 but 0 FUNC from tick 100 on in every world | the persistence probe measured the wrong thing; FUNC-persistence probe launched |
| 15:22 | FUNC persistence: LOCAL/WELL_MIXED x life 40/80 x MED/LOW x income 40/64, 3 seeds, 800 ticks | 48 | (running) | |
