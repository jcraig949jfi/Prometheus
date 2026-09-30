# W-X LOG (E-ANANKE-W-X, T-SWAP-REL5, thr-5df816e9b844; CWO 2026-09-30 + MWO-0004)

A0 10:36Z context. Frozen plan plans/T-SWAP-REL5_PLAN.md at 22b9bbd51 (2026-09-30T06:34:50-04:00 = 10:34:50Z);
worktree HEAD = 22b9bbd51. Read COMMON_RULES.md, COMMON_RULES_ARC3.md, W-W REPORT.md (as instructed by the
principal's brief: context read before my addendum, noted per ARC3 s2), W-W intervals4/sim4/PLAN_ADDENDUM/LOG,
W-U fc_sim/intervals, W-Q swap_rel2.simulate/boot_counts. Fabric lease status 10:36Z: [] (free). Plan: <= 2
single-thread processes, no lease (projected < 0.5 core-h).
A1 10:37-10:40Z PLAN_ADDENDUM.md (D1-D6, post-freeze readings) written BEFORE any simulation.
A2 ~10:42Z degen.py, run5.py. Harness identity (not a REL5 result; realistic model, seed 123, 2000 datasets):
my H0/H2 verdicts == W-W intervals4 H0/H2 bitwise at P32 K11 and P64 K3. ~0.6 CPU-s per 2000 datasets.
DEGEN truth check (20000 datasets, P64 K11 p=.95, d=.5/.95): mean DF at z=-1/2 and mean DN at z=+1/2 are
0 within 2.4e-4 -> truth at the boundary as D1 requires.
A2b TIMESTAMP CORRECTION: clock labels in A1/A2 were estimates. Actual mtimes (UTC): PLAN_ADDENDUM.md 10:36:40,
degen.py 10:36:55, run5.py 10:37:14, first output out/val_w*.json 10:38:03. Plan commit 10:34:50Z precedes all.
A3 10:37:36Z launched validation (run5.py val 0 2 PID 26772, val 1 2 PID 4624; 1 thread each; Win32 check before
launch: no run5.py processes). DONE 10:38:04Z (26 + 26 CPU-s). Stage-0 seeds, n=2000 per truth per point.
DEGENERACY VALIDATION (D5): the DEGEN model DOES produce near-degenerate resamples, but only at P32:
 P32: datasets with >= 0.5% sd*=0 resamples (deciding statistic) 0-8.3% per truth (max P32 K11 d.95 p.99
 164/2000); mean resample sd*=0 share up to 2.7e-3; H2 interval != H0 in up to 172/2000 datasets; ZW != H0 in
 up to 299/2000. Mechanism: at z=-1/2 a pair has DF=-.25 (a=1,s=0) w.p. ~.75; a sample with >= 28/32 such
 pairs gives (j/32)^32 >= 1.4% of resamples all equal. P64: >= 0.5%-share datasets <= 1/2000 per truth (needs
 >= ~61/64 equal pairs) -> the P64 half of the grid barely probes the degenerate region.
 Stage-0 FC counts already show ZW moving (up to 35/2000 FLIP at P32 K3 d.95 p.95) while H0/H2 stay <= 3/2000.
 Model is informative at P32 -> proceed to the FC grid with the frozen model (no tuning).
A4 10:38:26Z launched FC grid (run5.py fc 0 2 PID 21036, fc 1 2 PID 24968; 1 thread each; Win32 check before
launch: 0 run5.py processes). DONE 10:43:00Z (269 + 269 CPU-s). Win32 check after: 0 run5.py processes.
No point triggered stage 2 (H2 max FC 0.22% << 0.8%). All 36 points n=20000 per truth.
A5 ~10:44Z test_degen.py: `python -m pytest -q -p no:cacheprovider roles/Ananke/research/workers/W-X/test_degen.py`
-> 9 passed, RC=0 (out/pytest.txt). analyze5.py -> out/analysis.{txt,json}.
RESULT: H2 FC <= 0.22% at every point-verdict (max F .19 / N .22 / C .40 all at P64 d.5 where H2 == H0);
H0 0 fails; ZW FAILS at 9 point-verdicts, all P32 d=.95 (F/N 1.07-1.89%); sanity H0 <= H2: 0 violations.
In the degenerate region (P32 K3 d.95) H2 F/N .05-.11% vs H0 .00-.01% (H2 higher, as nesting predicts).
DECISION (PLAN s4, frozen, unchanged): PROMOTE H2. Caveat: the degenerate region is reached only at P32; at P64
<= 4/20000 datasets per truth have >= 0.5% sd*=0 resamples, so P64 is effectively H2 == H0 in this model.
A6 compute: val 53 CPU-s + grid 538 CPU-s + tests/analysis/checks < 20 CPU-s = ~0.17 core-h (cap 3). No lease
(max 2 single-thread processes; Fabric status [] at 10:36Z). No background processes left.
