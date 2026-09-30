# W-W LOG (E-ANANKE-W-W, T-SWAP-REL4, thr-5df816e9b844; CWO 2026-09-30 + MWO-0004)

A0 09:20Z context. Read frozen PLAN plans/T-SWAP-REL4_PLAN.md (first added 017259a48 2026-09-30T05:19:12-04:00
= 09:19:12Z; merged a7cba8221 09:19:14Z), COMMON_RULES.md, COMMON_RULES_ARC3.md, W-U code (fc_sim, intervals,
reach_sim, swap_rel3, validate3), W-U PLAN.md, LOG.md, out/fc_maxima.txt, out/pmin_posthoc.txt, W-Q swap_rel2
simulate/boot_counts. Did NOT read W-U REPORT.md, SYNTHESIS*, C1B_REVIEW*, PTE_ENGINE_CARD, ARC3_PRIORITIES.
Fabric lease status 09:20Z: skullport:cpu8 held by Nestor (lse-e39dab75e9bd, expires 11:48Z) -> run <= 2
single-thread processes, no lease.
A1 09:25Z PLAN_ADDENDUM.md written (D1-D7, post-freeze readings) BEFORE any simulation.
A2 09:27Z intervals4.py. Harness identity (not an FC result): on one 2000-dataset draw at P32 K11 and P256 K3,
H0 verdicts == W-U intervals.verdicts BOOTT, PCT == W-U PCT, T90 == W-U T90 bitwise. ~1.0 s / 2000 datasets
(all 6 intervals, 1 thread). Projected: FC stage 1 ~2.3 core-h + stage-2 top-ups ~2-3.5 + power ~0.05.
A2b TIMESTAMP CORRECTION: A1/A2 clock labels above were estimates. Actual file mtimes (UTC): PLAN_ADDENDUM.md
09:20:46 (sha256 c118e9e69de5d2a9...), intervals4.py 09:21:05, sim4.py 09:22:16; plan first commit 09:19:12Z.
A3 09:22:20Z launched sim4.py w0 (PID 2228) and w1 (PID 14052), 1 thread each (OMP/OPENBLAS/MKL=1), no lease;
Win32_Process check: exactly these 2 sim4 processes. Job queue: 8 POW jobs, then 36 FC jobs (P256 first).
A4 09:24Z POW jobs (8) done, ~20 s each. First look (analyze4 partial, 1 s process): H0 P64 K11 realistic p=.99
FLIP .700 / NO_EFFECT .724 (W-U REL3 reported .72 FLIP with n=1000 seed 31: consistent). s4.2 scores (min F,N at
p .95/.99): H0 .700, H1 .744, H2 1.000, H3 .835. H1 fallback fires in 4.5% of those datasets (DF). Eligibility
awaits the FC grid; no decision taken.
A5 09:34Z 4 P256 FC jobs done (~295 s each); H0 counts == W-U BOOTT counts exactly at 144/144 (point,verdict) so far.
A6 10:02Z Nestor lease gone (status []); lease lse-658bd3b24ea0 ACQUIRED (token ed4b2091..., expires 11:02Z).
Win32 check: 2 sim4 procs (2228, 14052). Launched w2-w7 (PIDs 27176 5672 18244 13720 16800 8144), 1 thread each
-> 8 single-thread processes total (checked: Count 8). P256 9/9 and P128 6/9 FC jobs done at launch.
A7 10:29Z all 44 jobs DONE (8 workers exited; Win32 check: 0 sim4 processes). analyze4.py -> out/analysis.{json,txt}.
FC (max over 3 models x 12 p, per verdict): H0, H1, H2 PASS at all 12 designs (not robust at P32 K11/K12 F,N:
Wilson upper 1.05-1.09%). H3 FAILS at P32 K11 (N 1.04%, 80000) and P32 K12 (F 1.02%, N 1.03%). T90 fails at all
12 designs; PCT fails at P32 and P64 (all K), passes P128/P256 -> controls as required.
H0 reproduction: 810/810 (point, verdict) counts bitwise equal to W-U BOOTT where n equal; 486 comparisons where
W-U ran stage 2 and I did not (W-U's PCT/TINT/XPCT/BCA triggered it): max |z| 3.07 (P32 K11 worst p=.50 N:
my stage-1 .395% vs W-U pooled .573%; = W-U's own stage-1 vs stage-2 difference; same data, not a harness defect).
STRUCTURAL FINDING: H1 and H2 counts equal H0 at 1296/1296 and 1295/1296 point-verdicts; H1 fallback fired on
1 DF + 1 DN dataset out of 19.44M simulated. The FC boundary truths (z=+-1/2) never generate degenerate resamples,
so the plan's FC grid cannot see the region where H1/H2 act. H3 differs at 1096/1296 (it shifts every interval).
A8 10:30Z validate4.py (1 thread, ~few s): KA1/KA2 P32,64,128/KA3: H0, H1, H2 0 false certificates and 0 lost
vs H0; H3 0 false certificates but loses 6/49/24/12/3 exact-truth certificates (q=0 point-mass cells: the
pseudo-pair creates variance). M3 swapped-truth must-fail: 40 false certs for H0/H1/H2 (36 H3) -> OK.
DECISION (PLAN s4, frozen): eligible {H0, H1, H2}; s4.2 scores min(F,N) at p .95/.99 P64 K11 realistic:
H0 .700, H1 .744, H2 1.000 (H3 .835, ineligible). Chosen H2. s4.3: H2 FLIP 1.000 / NO_EFFECT 1.000 at p=.99
(>= .80) and KA PASS -> PROMOTABLE. On all 144 power points H2 >= H0 (min diff 0.000, max +.843).
A9 10:31Z swap_rel4.py (clean H2 rule module; nested-in-REL3 property documented) + test_swap_rel4.py:
`python -m pytest -q -p no:cacheprovider roles/Ananke/research/workers/W-W/test_swap_rel4.py` -> 11 passed, RC=0
(out/pytest.txt). Cross-check: swap_rel4.certificate == intervals4 H2 verdicts on 3 x 500 simulated datasets.
A10 10:32Z lease lse-658bd3b24ea0 RELEASED (status: []). Compute: 44 jobs process_time 15441 s = 4.29 core-h
(+ analysis/KA/pytest < 0.02) -> ~4.31 core-h <= 8. Max concurrency 8 single-thread procs under the lease
(10:03-10:29Z), 2 before. Outputs 702 KB. No background processes left.
