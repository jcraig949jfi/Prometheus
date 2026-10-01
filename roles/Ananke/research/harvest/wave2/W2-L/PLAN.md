# W2-L plan (written before any Task-1/Task-2 scoring run; gate already run)
Gate (done first): P-FLIP at 6f82f9c7 on the row's own held seeds (32 pairs) = .943 [.888,.984]
(= W2-D t_v_ruler held value bit-for-bit; H-PLANT's ~.97-.98 is on 128 other pairs). relay_flood .6016
[.5495,.6497], comm_delta lo99 .0378 (= W2-D F6 bit-for-bit). PASS.

Scoring protocol (all runs): hp_common.evaluate (eager, CPU, 2 threads), the row's own HELD seeds
(H_int(search_seed, HELD_NS), M=64 = 32 mirror pairs), pair-bootstrap 99% CI (assays.pair_ci).
Variant screens may use the first 32 worlds (16 pairs); any variant reading used for a class is re-scored at 64.

Task 1 classification (frozen now):
- EXACT space = row's own Physics unchanged (P-FLIP needs state_dim>=2, prog_len>=16).
- PLANT-SOLVED: P-FLIP or one of <=2 pre-declared variants, in the EXACT space and physics,
  reaches lo99 > .55 (the C1 SIGNAL bar). Reading: not R, not P => S or U.
- R-CANDIDATE: no in-space success because the plant does not fit (prog_len/state_dim too small),
  AND the override-scored plant (genome-space fields raised to the minimum the plant needs; physics
  otherwise unchanged; labelled OVERRIDE) reaches lo99 > .55.
- UNDECIDED: everything else (plant + variants fail even with any needed override). Diagnosis attached.
Variants (pre-declared): V1 'refresh' = P-FLIP + sign-normalise S0,S1 every awake tick (against decay);
V2 'thin' = V1 with emission thinned by RAND (against caps/collisions). Variants need prog_len > 16, so
for rows with prog_len < their length they are OVERRIDE readings.

Task 2: relay_flood (plants.relay_flood; prog_len raised to 12 where smaller, labelled, as C1's
plant_viability did) at each selected row's physics/env on its held seeds, with zero-comm delta.
"Matches" = relay acc >= recorded held acc - (its own 99% half-width); "exceeds" = relay acc >= recorded acc.

## Addendum A1 (after base results, before any variant run)
Base P-FLIP: in-space success at 3/58 (6f82f9c7 .943, 996716ac 1.000, 64d33b89 .854). 49/58 rows have decay_shift>0.
Refresh placement fixed to the START of each awake tick (before T1 = S0*S1): with end placement, positive
values decay to 1 between sparse async wakes and the MULQ chain truncates to 0. Variants screened at M=32
(16 pairs, first half of the held seeds); any variant with screen lo99 > .52 is re-scored at M=64.

## Addendum A2 (after refresh screen, before thin)
Compute is tight (~1440 CPU-s used of 2160). Thin (V2 = refresh + RAND-thinned relay emission, sensors
always emit) is screened at M=16 (8 pairs, first quarter of held seeds) on the 42 rows where refresh
screen lo99 <= .52; rows with thin screen acc >= .65 are re-scored at M=64. Refresh passes (screen
lo99 > .52, 16 rows) are completed to M=64 by scoring only worlds 32..63 and pooling pairs.
FLIP_FEEDBACK (W2-B ruler) on rows crossing SIGNAL: teachers-removed run on the first 32 worlds, diff vs
the same 32 worlds' normal pairs (16 pairs; stated).
