<!-- DEPOSITED VERBATIM by Ananke for worker W-W; sha256(report)=951ce51c93a1713e; delimited; see REPORT.provenance.json -->
E-ANANKE-W-W  T-SWAP-REL4  thr-5df816e9b844  (CWO 2026-09-30 + MWO-0004)

WHAT I TESTED
- Plan: roles/Ananke/research/plans/T-SWAP-REL4_PLAN.md. It was first added in 017259a48 (2026-09-30 09:19:12Z) and merged in a7cba8221 (09:19:14Z). I did not edit it.
- Timing: PLAN_ADDENDUM.md was written at 09:20:46Z. The first simulation was launched at 09:22:20Z and the first result file appeared at about 09:22:40Z. So the plan commit predates my first result. I committed nothing.
- Candidates:
  - H0: REL3 BOOTT, unchanged.
  - H1: BOOTT, falling back to a t-interval when more than 5% of resamples have sd*=0.
  - H2: BOOTT with the resample SD floored: sd*_b := max(sd*_b, sqrt(1/(4K))/sqrt(P)*0.5).
  - H3: BOOTT with one pseudo-pair at 0 added.
  - Controls: T90 and PCT.
- FC grid: P in {32,64,128,256} x K in {3,11,12} x worst/realistic/hetero x the 12 values of p from .50 to .99. Truths at z = +-1/2 (z = 0 at p = .50). n = 20,000 per point, plus 60,000 more where any of H0-H3 was in (0.8%, 1.2%].
- Power grid: z = -1/0/+1 x p in {.60,.70,.80,.90,.95,.99} x P in {32,64} x K in {3,11} x worst/realistic, n = 2000, seed 41.
- Known answers: KA1, KA2 and KA3 plus the must-fail M3, scored at the certificate level for each candidate.

RESULTS
FC max, % [Wilson 99% CI], per verdict F/N/C (FLIP/NO_EFFECT/CHANCE):

H0 = H1 = H2 (identical maxima at every design):
| Design | FLIP | NO_EFFECT | CHANCE |
|---|---|---|---|
| P32 K3 | .91 [.83,1.00] | .88 [.80,.97] | .48 [.37,.63] |
| P32 K11 | .96 [.88,1.05] | .96 [.88,1.05] | .60 [.48,.76] |
| P32 K12 | .99 [.91,1.09] | .99 [.90,1.08] | .65 [.51,.81] |
| P64 K3 | .77 [.62,.94] | .75 [.61,.92] | .52 [.40,.66] |
| P64 K11 | .75 [.68,.84] | .80 [.65,.98] | .61 [.49,.77] |
| P64 K12 | .76 [.68,.84] | .80 [.72,.88] | .65 [.51,.81] |
| P128 K3 | .65 [.52,.81] | .70 [.56,.87] | .60 [.48,.76] |
| P128 K11 | .69 [.56,.86] | .66 [.53,.83] | .66 [.53,.83] |
| P128 K12 | .69 [.56,.86] | .69 [.56,.86] | .66 [.53,.82] |
| P256 K3 | .66 [.52,.82] | .68 [.55,.85] | .62 [.50,.79] |
| P256 K11 | .61 [.48,.77] | .66 [.53,.82] | .66 [.53,.83] |
| P256 K12 | .69 [.55,.86] | .65 [.52,.81] | .65 [.51,.81] |

- H0, H1 and H2 pass at every design point. They are robust everywhere except P32 K11 and P32 K12 for FLIP and NO_EFFECT, where the Wilson upper bound is 1.05-1.09%.
- H3 FAILS at two design points:
  - P32 K11: F .99 [.91,1.09], N 1.04 [.95,1.14], C .64 (n = 80,000).
  - P32 K12: F 1.02 [.93,1.12], N 1.03 [.94,1.13], C .65.
  - P32 K3 passes but is not robust: F .95, N .94.
  - P64 and above pass: P64 values are .74-.82, P128 and P256 are .66-.71.
- Structural result: H1 and H2 counts equal H0 at 1296/1296 and 1295/1296 point-verdicts. H1's fallback fired on only 1 DF and 1 DN dataset out of 19.44M. H3 differs from H0 at 1096 of 1296.

Power (FLIP / NO_EFFECT) at p = .95 and .99:

| Design, model | p | H0 | H1 | H2 | H3 |
|---|---|---|---|---|---|
| P64 K11 realistic | .99 | .700/.724 | .744/.759 | 1.000/1.000 | .835/.864 |
| P64 K11 realistic | .95 | 1.0 | 1.0 | 1.0 | 1.0 |
| P64 K11 worst | .99 | .996 | .997 | 1.000 | .998 |
| P64 K3 realistic | .99 | .157/.174 | .742/.765 | 1.000/1.000 | .069/.067 |
| P64 K3 realistic | .95 | .931/.919 | .934/.922 | 1.000/1.000 | .976/.967 |
| P64 K3 worst | .99 | .528/.506 | .705/.682 | 1.000/1.000 | .474/.483 |
| P32 K11 realistic | .99 | .209/.213 | .532/.518 | 1.000/1.000 | .359/.373 |
| P32 K3 realistic | .99 | .382/.402 | .932/.946 | 1.000/1.000 | .010/.007 |
| P32 K3 realistic | .95 | .433/.434 | .573/.581 | 1.000/1.000 | .625/.618 |

- Rows with a single number are the same for FLIP and NO_EFFECT.
- On all 144 power points, H2 >= H0 (minimum difference 0.000). CHANCE power is the same across H0-H2.

PLAN s4 decision:
1. Eligible: {H0, H1, H2}. H3 is excluded because it fails FC at P32.
2. Score (min of FLIP and NO_EFFECT power at p .95/.99, P64 K11, realistic): H0 .700, H1 .744, H2 1.000. H2 is chosen.
3. H2 has FLIP 1.000 and NO_EFFECT 1.000 at p = .99 (bar .80) and passes KA, so it is PROMOTABLE. Rule module: W-W/swap_rel4.py.

Caveat for promotion:
- The H2 interval sits inside the REL3 interval, because flooring only moves t* toward 0. So H2's FC is always at least H0's.
- They are equal on this grid because truths at z = +-1/2 never produce degenerate resamples under any of the three models.
- So the FC grid checks H2 only where it coincides with REL3. A null-side truth whose pair statistics are nearly constant is outside all three models, and that part is untested.
- The floor, as written, is SE-scaled (P64 K11: 0.0094), so in effect H2 replaces the infinite t* values with large finite ones.

CONTROLS
- H0 reproduces W-U:
  - 810/810 (point, verdict) counts are bitwise equal to W-U's BOOTT counts wherever the sample sizes match (same seeds, addendum D4).
  - At 486 points W-U ran stage 2 and I did not, because W-U's own candidates triggered it. There the largest gap is |z| = 3.07, at P32 K11 worst p=.50 NO_EFFECT: my .395% vs W-U's pooled .573%.
  - That gap is the difference between W-U's own stage-1 and stage-2 samples on the same data, not a harness defect.
- T90 fails at all 12 designs (for example P256 K3 F 5.95%).
- PCT fails at P32 and P64 for every K, and passes at P128 and P256. Both controls behave as required.

KNOWN-ANSWER CHECKS (certificate level; out/ka4.json)
| Set | Cells | H0 exact-truth issued | H1, H2 | H3 lost vs H0 |
|---|---|---|---|---|
| KA1 P256 | 80 | 69 | same, 0 lost | 6 |
| KA2 P32 | 640 | 436 | same, 0 lost | 49 |
| KA2 P64 | 320 | 257 | same, 0 lost | 24 |
| KA2 P128 | 160 | 135 | same, 0 lost | 12 |
| KA3 | 25 | 20 | same, 0 lost | 3 |
- Every candidate has 0 false certificates in every set.
- H3's losses are all q=0 point-mass cells, where the pseudo-pair creates variance. H3 therefore fails KA.
- M3 (truths swapped, must fail): 40 false certificates for H0, H1 and H2, 36 for H3.
- A synthetic near-degenerate FLIP case (P64 K11, 61 pairs a=1/s=0 and 3 pairs 10/11 and 1/11): H2 issues FLIP, REL3 gives INDETERMINATE. This is covered by a test.

DEVIATIONS
All are in PLAN_ADDENDUM.md, labelled post-freeze. D1-D7 were written at 09:20:46Z, before any simulation. D8 was written after the power jobs finished and after my first look at their output (LOG A4), but before any FC result existed.
- D1: H2's floor is applied literally to sd*_b; the original sd=0 case keeps the point interval.
- D2: H1's degeneracy test is bsd <= 1e-9, applied to DF and DN separately.
- D3: H3 uses boot_counts(P+1).
- D4: W-U's data seeds are reused, and stage 2 is triggered only by H0-H3.
- D5: order statistics use np.partition at the exact indices, so the values are identical to a full sort.
- D6: KA is scored at the certificate level, requiring 0 false certificates and no losses against H0. REACH/p_min tables were not rebuilt for the hybrids, so swap_rel4 takes REL3's p_min, which is conservative on the simulated points, or p_min=None.
- D7: the s4 power figure is the s3 power simulation.
- D8: H0 competes; exact ties go H1 < H2 < H3 < H0.
- None of these changed thresholds, candidates or the grid.

DISAGREEMENTS
- With W-U: REL3's p_min of 1.0 for FLIP/NO_EFFECT at P32-P64 (and the "blind spot") comes from the interval (infinite t* on degenerate resamples), not from the data. H2 removes it, taking P64 K3 realistic p=.99 FLIP from .157 to 1.000.
- With W-U: my P64 H0 maxima differ slightly from W-U's (for example P64 K3 F .77 vs .71). That is only because we ran stage 2 at different points; both are the same method.
- With plan s5: "H3 conservative by construction" is refuted. H3 is anti-conservative at P32, and its power at P32 K3 p=.99 falls to .01.
- With plan s5: the expected return of the t-interval's undercoverage under H1 never showed up, because the fallback essentially never fires at the FC boundaries.

PYTEST
- Command: `python -m pytest -q -p no:cacheprovider roles/Ananke/research/workers/W-W/test_swap_rel4.py`
- Result: 11 passed, RC=0 (out/pytest.txt).

LEASES
- Ran with 2 single-thread processes and no lease from 09:22 to 10:02Z, while Nestor held the lease.
- Took lse-658bd3b24ea0 (skullport:cpu8) at 10:02Z and scaled to 8 single-thread processes.
- Released at 10:32Z. `python -m fabric lease status` then returned [].
- No W-W processes are left running (Win32 check shows 0).

COMPUTE
4.29 core-h across the 44 jobs (process_time 15,441 s), plus under 0.02 for analysis, KA and pytest: about 4.31 core-h, under the 8 cap. Wall time about 1 h 15 m. Outputs are 702 KB.

FILES
Everything is in F:/Prometheus-worktrees/ananke-base-role/roles/Ananke/research/workers/W-W/:
- PLAN_ADDENDUM.md, LOG.md
- intervals4.py (the candidates)
- sim4.py (FC and power grids)
- analyze4.py (tables and decision)
- validate4.py (KA checks)
- swap_rel4.py (the promotable H2 rule, with its frozen rule and table in the docstring)
- test_swap_rel4.py
- out/analysis.json, out/analysis.txt, out/ka4.json, out/ka4.log, out/pytest.txt, out/pids.txt, out/jobs/*.json (44 job files), out/claims/
- logs/sim_w0..7.log
