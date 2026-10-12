# THESEUS-27b verdict (prereg roles/Theseus/prereg/2026-10-08_structure_selection_b/, 86fdf67fc)

Runs (PYTHONHASHSEED=0, ecology-only, --pop-cap 300 --elite-grids pca --dark-protect-gens 3
--elite-protect-k 150 --seed-select 1.5): SELB-REP v0_1_selbrep_2026-10-08 (--quality rep),
SELB-R5 v0_1_selbr5_2026-10-08 (--quality r5).

BINDING: max active 300 in both runs (bar 345); fossilised 755 / 666. Cap binds.
MANIPULATION CHECK: median R5 of viable deep children SELB-R5 .773 vs SELB-REP .727,
difference +.045 [.045, .091] -- CI above 0: selection took (R5_TREND_vs_selbrep.json).
PRIMARY (H1, unchanged rule; h1_rescore --d-ref <tag> --a-v1-rows h1_large_A rows; n 175):
  SELB-REP: FAIL. EX(D) pca 24 vs null 29 (p .89), desc 37 vs 35 (p .33), resp 7 vs 8.5
            (p .79); O(D)-O(R) euclid_z -.051 [-.309, .221]. Without A: FAIL.
  SELB-R5:  FAIL. EX(D) pca 23 vs 28 (p .91), desc 30 vs 34 (p .86), resp 4 vs 8 (p .97);
            O(D)-O(R) euclid_z -.089 [-.453, .242], quantile_l1 -.007 [-.013, -.001].
            Without A: FAIL.
VERDICT: NO-HELP. Selection for graded structure takes (R5 rises) but does not make deep
descendants reach niches the one-shot, LLM and random arms do not; under SELB-R5 deep
children are BELOW the permutation null in every grid (selection concentrates them).
Rows: theseus/runs/h1_v0_1_selbrep_2026-10-08/, theseus/runs/h1_v0_1_selbr5_2026-10-08/.
Predictions T1-T4 all RIGHT.
