<!-- DEPOSITED VERBATIM by Ananke for worker W-X; sha256(report)=bab62407961174ce; delimited; see REPORT.provenance.json -->
E-ANANKE-W-X  T-SWAP-REL5  thr-5df816e9b844  (CWO 2026-09-30 + MWO-0004)

WHAT I TESTED
- Plan: roles/Ananke/research/plans/T-SWAP-REL5_PLAN.md, frozen at 22b9bbd51 (2026-09-30T10:34:50Z). I did not edit it.
- Timing, all UTC, all after the plan commit:
  - PLAN_ADDENDUM.md written 10:36:40, before any code or simulation.
  - degen.py 10:36:55, run5.py 10:37:14.
  - First result (degeneracy validation) 10:38:03.
  - FC grid ran 10:38:26 to 10:43:00.
- Candidates:
  - H2: W-W intervals4 H2, imported unchanged.
  - H0: REL3 BOOTT, intervals4 H0.
  - ZW: H0 with t*_b := 0 wherever sd*_b <= 1e-9, instead of +-inf.
- Harness check: my H0 and H2 verdicts equal W-W intervals4 bitwise (P32 K11, P64 K3, 2000 datasets each).
- DEGEN model (addendum D1): each pair is deterministic with probability d, otherwise it follows W-Q's realistic model at normal p.
  - A deterministic pair has a = 1, and its swap arm is constant across the K trials (s in {0,1}).
  - s uses the realistic model's own coupling at accuracy 1: flip (s=0) with prob t, same (s=1) with prob u, otherwise a constant fair coin.
  - So every pair type sits exactly at the boundary: E[DF] = 0 at z = -1/2 and E[DN] = 0 at z = +1/2. Checked empirically: |mean| < 2.4e-4 on 20k datasets.
  - I rejected the reading "one common swap constant for all deterministic pairs", because it cannot put the truth at the boundary for K in {3,11} or for d >= .75.
- Grid: P {32,64} x K {3,11} x d {.5,.8,.95} x p {.90,.95,.99} = 36 points.
  - n = 20,000 per truth per point.
  - Stage 2 (+60,000 where H2 FC is in (0.8%,1.2%]) never triggered.
  - Seeds: [0x660, stage, P, K, d, p, z].

DEGENERACY VALIDATION (stage-0 draw, n = 2000 per truth; the grid data agrees)
The model does produce near-degenerate resamples, but only at P32.

Grid values per truth, n = 20,000:
| Point | Mean resample sd*=0 share | Datasets with any sd*=0 resample | Datasets with >= 0.5% sd*=0 resamples | H2 interval != H0 | ZW interval != H0 |
|---|---|---|---|---|---|
| P32 K3 d.95 (p .90-.99) | 2.1-2.7e-3 | 31-34% | 6.9-8.4% | 6.8-8.4% | 13.7-14.4% |
| P32 K11 d.95 | 1.6-2.3e-3 | 26-32% | 5.0-7.3% | 6.0-7.6% | 13.0-14.4% |
| P32 d.80 | 1.0e-4 to 1.1e-3 | — | 0.4-3.9% | — | — |
| P32 d.50 | <= 2.2e-4 | — | <= 0.7% | — | — |
| P64, all points | <= 5.4e-6 | — | <= 4 datasets in 20,000 | <= 4 datasets | <= 43 datasets |

- Mechanism: at z = -1/2 a pair has DF = -.25 with probability about .75. When a P32 sample has 28 or more such pairs, (j/32)^32 >= 1.4% of resamples are all-equal.
- At P64 about 61 of 64 equal pairs would be needed, which is essentially unreachable.
- So the check is informative at P32 and nearly vacuous at P64. I did not tune the model.

RESULTS: FC %, [Wilson 99% CI], per verdict (F = FLIP at z = -1/2; N = NO_EFFECT at z = +1/2; C = CHANCE, max of the two truths)
Full 36-point tables are in out/analysis.txt; excerpt below.

H2:
| Point | F | N | C |
|---|---|---|---|
| P32 K3 d.95 p.90 | .05 [.02,.11] | .08 [.04,.15] | .04 [.02,.10] |
| P32 K3 d.95 p.95 | .07 [.04,.14] | .11 [.07,.20] | .10 [.06,.18] |
| P32 K3 d.95 p.99 | .07 [.04,.14] | .10 [.05,.17] | .09 [.05,.16] |
| P32 K11 d.95 p.90 | .03 [.01,.09] | .03 [.01,.08] | .08 |
| P32 K11 d.95 p.95 | .02 [.01,.07] | .01 [.00,.06] | .12 |
| P32 K11 d.95 p.99 | .01 [.00,.06] | .01 [.00,.05] | .08 |
| P32 K3 d.80 (all p) | .02-.03 | .03-.07 | .10-.11 |

- Maximum over all 36 points: F .19 [.13,.29] (P64 K11 d.5 p.90), N .22 [.15,.33] (P64 K11 d.5 p.95), C .40 [.30,.53] (P64 K11 d.5 p.99).
- Those maxima are all at d = .5 points, where H2 equals H0.

H0:
| Point | F | N | C |
|---|---|---|---|
| P32 K3 d.95 p.90 | .01 [.00,.05] | .00 [.00,.03] | .04 |
| P32 K3 d.95 p.95 | .01 [.00,.06] | .01 [.00,.05] | .10 |
| P32 K3 d.95 p.99 | .01 [.00,.04] | .01 [.00,.06] | .09 |
| P32 K11 d.95 (all p) | .00-.01 | .01 | .08-.12 |

- Maxima are the same as H2's: F .19, N .22, C .40.
- 0 point-verdicts exceed 1%.

ZW (must-fail control):
| Point | F | N | C |
|---|---|---|---|
| P32 K3 d.95 p.90 | 1.29 [1.10,1.52] | 1.38 [1.18,1.60] | .04 |
| P32 K3 d.95 p.95 | 1.57 [1.36,1.82] | 1.61 [1.40,1.86] | .10 |
| P32 K3 d.95 p.99 | 1.59 [1.38,1.83] | 1.89 [1.66,2.15] | .09 |
| P32 K11 d.95 p.90 | .85 [.70,1.03] | .81 [.67,1.00] | .08 |
| P32 K11 d.95 p.95 | 1.07 [.90,1.28] | 1.00 [.83,1.20] | .12 |
| P32 K11 d.95 p.99 | 1.68 [1.46,1.93] | 1.50 [1.29,1.74] | .08 |
| P32 K3 d.80 p.99 | .61 [.49,.77] | .60 [.48,.76] | — |

- ZW exceeds 1% at 9 point-verdicts, all at P32 d = .95. The P32 K11 d.95 p.95 N value is exactly 1.00%, so it does not count.
- At P64 ZW is at most .12%, about equal to H0.

Sanity check, H0 FC <= H2 FC: 0 violations over 108 point-verdicts. This matches the nesting argument.

THE PLAN s4 DECISION
**PROMOTE H2.** All three frozen conditions hold:
1. H2 pooled FC <= 1.00% for every verdict at every DEGEN point (max .40%, CHANCE; FLIP/NO_EFFECT max .22%).
2. ZW fails (9 point-verdicts > 1%), so the model probes the degenerate region.
3. H0 FC <= H2 FC at every point.

Scope caveat for the promotion record:
- The probe only reaches P32. The degeneracy validation shows P64 datasets almost never have tail-relevant sd*=0 resamples at the boundary truths.
- So at P64, including P64 K11 where W-W scored H2's power, this item confirms H2 = H0 on the data rather than exercising the floor.
- In the degenerate region H2 does raise FC over REL3: about 7-11x at P32 K3 d.95, from .00-.01% to .05-.11%. It stays far below 1%.
- Heavier-skew nulls (a near-constant block balanced by rare extreme pairs, like W-W's synthetic case) are outside this model and remain untested. No grid expansion was allowed here.

DEVIATIONS
All are in W-X/PLAN_ADDENDUM.md (D1-D6), labelled post-freeze and written before any simulation. They are readings of the plan text only. No candidate, threshold, model family or grid value was changed.
- D1: DEGEN construction, as described above.
- D2: FC per verdict as in W-U/W-W.
- D3: stage-2 trigger uses H2 only; the seed scheme is listed above.
- D4: ZW definition. The original sample with sd = 0 keeps REL3's point interval.
- D5: validation counters on a separate stage-0 draw.
- D6: sanity check done on counts from the same data.
- I did not re-run W-W's power or KA checks; they are not in this plan.

DISAGREEMENTS (with W-W)
- W-W said near-constant null-side pair statistics are "outside all three models". That is true for W-Q's models. But a boundary-truth model with deterministic pairs does reach them at P32: up to 8.4% of datasets have >= 0.5% sd*=0 resamples. At P64 it essentially cannot, which is a structural limit and not just a model gap.
- W-W's REPORT says H2's interval lies inside REL3's, so H2's FC is always at least H0's. Here that holds and becomes visible for the first time: H2 FC > H0 FC by up to +.10 pp at P32 d.95. The effect is real but small. W-W's REL4 grid could not show it.
- No disagreement with the H2 promotion itself.

PYTEST
- Command: `python -m pytest -q -p no:cacheprovider roles/Ananke/research/workers/W-X/test_degen.py`
- Result: 9 passed, RC=0 (out/pytest.txt).
- Covered: truth at the boundary; deterministic arms constant; seed reproducibility; H2 and ZW nested in H0 on near-degenerate data with ZW narrower; ZW = H2 = H0 when there are no degenerate resamples; Wilson known value.

LEASES
- None, <= 2 threads. Fabric status was [] at 10:36Z.
- Runs used at most 2 single-thread processes (PIDs 26772/4624 for validation, 21036/24968 for the grid).
- Win32_Process was checked before each launch and after: 0 run5.py processes remain.

COMPUTE
- Validation 53 CPU-s, FC grid 538 CPU-s, tests/analysis/checks under 20 CPU-s: about 0.17 core-h (cap 3).
- Wall time about 10 min. Outputs 137 KB.

FILES
All in F:/Prometheus-worktrees/ananke-base-role/roles/Ananke/research/workers/W-X/:
- PLAN_ADDENDUM.md, LOG.md
- degen.py (DEGEN model, H0/H2/ZW via W-W intervals4, Wilson)
- run5.py (validation and FC driver)
- analyze5.py (tables and s4 decision)
- test_degen.py
- out/val_w{0,1}.{json,log}, out/fc_w{0,1}.{json,log}, out/analysis.{txt,json}, out/pytest.txt
