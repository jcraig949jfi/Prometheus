# Crius calibration ledger

Currency: 2026-09-18. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. Empty at creation:
the seat has made no calls.

date | call made | what was true | corrected by | changed practice
2026-09-19 | P1 (DESIGN_C0 s9): ENUMERATE solves no depth-4 task and its within-depth late/early ratio is ~1 | ENUMERATE solved 3/6 depth-4 held-out tasks (budget 1500 covers depth 1-3 plus ~180 depth-4 sequences, and targets have shorter equivalents); its late/early ratio ranged 0.48-1.97 across seeds (n=10 tasks per depth; the statistic is ordering noise) | crius/runs/search_c0_seeded_s1/REPORT.md (family table; checklist rows) | budgets are quoted with the reachable fraction, never "unreachable"; late/early is reported beside its FRESH noise floor and is not a criterion
2026-09-19 | P2: CACHE_REUSE/ADAPTIVE show late/early < 0.5 at depths 2 and 3 | on the search suite d2 = 1.00/1.03, d3 = 0.74/0.88: acquisition completes in stages A/B, so within-depth cost is flat by stage C; the effect lives in reuse_gain (+3988/+3674) and in stage means (C 2.65 vs 33.1 FRESH), and the RESET clause held exactly (41.6 vs 40.2, 259.8 vs 256.0, 45.7 vs 44.3 on the task after each reset) | crius/runs/baselines_c0/CACHE_REUSE_seed101.json | the primary adaptation statistic is reuse_gain by stage (FRESH minus ACCUMULATED on the same tasks), not a within-depth ratio
2026-09-19 | P3: ENUMERATE solves no depth-4 task | 3/6 | same as P1 | same as P1
2026-09-19 | frozen metric (DESIGN_C0 s4): C0_EFFICIENCY was expected to order reuse > brute force > quitting | it orders quitting (3.00 held-out) above CACHE_REUSE (2.97) and its search optimum after 300 iterations is a program solving 5.5/50 tasks (4.34); a ratio of gained competence to spent budget rewards abstention; partial-credit competence makes near-zero effort score | crius/runs/CAMPAIGN_SUMMARY.md; search_c0_seeded_s1/REPORT.md | Campaign 1 metric charges every unsolved task its full budget and requires competence to be kept (c0x is the exploratory version; report.py guard 0 added the same day)
