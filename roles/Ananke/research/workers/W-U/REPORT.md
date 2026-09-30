<!-- DEPOSITED VERBATIM by Ananke for worker W-U; sha256(report)=85496175d2c8c9b5; delimited; see REPORT.provenance.json -->
W-U T-SWAP-REL3 (E-ANANKE-W-U, successor of T-SWAP-REL2 thr-5df816e9b844, MWO-0004)

**WHAT I TESTED**
- **PLAN frozen before any candidate was simulated.** PLAN.md was frozen at 15:04:28Z, sha256 58255ac1ee466821…. The simulations launched at 15:05:06Z. The header of PLAN.md says "~15:15Z", which is wrong. I left it unedited so the hash still matches (LOG A3b).
- **Context read before the PLAN** (declared in LOG A0):
  - W-Q's REPORT and code, which contain W-Q's false-certificate numbers.
  - I did not read any SYNTHESIS, C1B_REVIEW or ENGINE_CARD file.
- **Five candidate intervals**, each applied to DF and DN at 99% two-sided:
  - PCT: the REL2 percentile bootstrap.
  - BCA: bias-corrected and accelerated bootstrap.
  - BOOTT: studentized pair bootstrap (bootstrap-t).
  - TINT: t-interval on the pair statistics.
  - XPCT: expanded percentile, i.e. a P-dependent level, alpha'/2 = Phi(-sqrt(P/(P-1)) t_{P-1,.995}).
  - Must-fail control: T90, the t-interval at 90%.
  - All bootstrap candidates use W-Q's seed-0 resample counts (B=2000).
- **Grid:** 18 designs (P in {8,16,32,64,128,256} × K in {3,11,12}), 3 models (worst, realistic, hetero), the 12 W-Q normal values p = .50 to .99, and the boundary truths z = ±1/2 (z = 0 at p = .50).
  - Sample size: n = 20,000 per point. A point where any candidate estimate fell in (0.8%, 1.2%] got 60,000 more draws (80,000 total).
  - A point passes if the pooled false-certificate (FC) rate is ≤ 1.00%. "Robust" means the Wilson 99% upper bound is also ≤ 1%.
- **Power:**
  - Selection power: P=64 K=11, exact truths, p in {.60, .65, .70, .75}, worst and realistic models, n = 4000.
  - REACH curves for p_min: n = 1000 on W-Q's POW_GRID.
- **Re-application and checks:**
  - The rule was re-applied to W-O's 733 verdicts.
  - Engine-plant known-answer checks used W-Q rep-1 arrays, W-Q rep-1 split into disjoint pair blocks, and W-N rep-0 noiseless arrays with post-hoc flip noise.

**THE FROZEN RULE (selected by the PLAN s4 rule): REL3 = W-U/swap_rel3.py, pure numpy + math**
1. **Interval: BOOTT.** Studentized pair bootstrap with B=2000 and seed-0 counts.
   - t*_b = (m*_b - m) / (sd*_b / sqrt P), with sd computed at ddof 1.
   - If sd*_b = 0, t*_b = ±inf.
   - The interval is [m - t*_.995·se, m - t*_.005·se], with se = sd / sqrt P.
   - If sd = 0, the interval is the single point m.
2. **Certificates, on DF = (s-.5)+(a-.5)/2 and DN = (s-.5)-(a-.5)/2:**
   - FLIP_REL if hi(DF) < 0.
   - NO_EFFECT_REL if lo(DN) > 0.
   - CHANCE_REL if lo(DF) > 0 and hi(DN) < 0.
3. **Minimum-P floor: P_FLOOR = 32.** Below 32 pairs, every verdict is NOT_ELIGIBLE. No candidate met the 1% target at P = 8 or 16.
4. **Unchanged from REL2 in structure:**
   - Identification guard: lo99(normal) > .50, now computed with BOOTT.
   - Per verdict V: CERT_OK_V (P ≥ floor and FC_V max ≤ 1%), REACH_V (lo99(normal) ≥ p_min_V), ATTAIN_V (guard and CERT_OK_V and REACH_V).
   - Label: a certificate V becomes V if CERT_OK_V, else NOT_ELIGIBLE. With no certificate, the label is INDETERMINATE if any verdict is attainable, else NOT_ELIGIBLE.
   - STRICT variant: a certificate also needs REACH_V.
5. **Transfer class beside every FLIP_REL.** z = (s-.5)/(a-.5) with a paired 99% delta-method CI using t_{P-1}.
   - COMPLETE if the CI contains -1.
   - PARTIAL if lo > -1.
   - OVERSHOOT if hi < -1.
6. **Selection outcome (floor first, then power, then simplicity):**

| Candidate | Floor (P) |
|---|---|
| BOOTT | 32 |
| XPCT | 64 |
| PCT | 128 |
| BCA | 128 |
| TINT | 128 |
| T90 | none |

   - BOOTT is the only candidate in the lowest tier, so power did not decide.
   - Power at P=64 K=11: PCT .841, BCA .841, XPCT .831, BOOTT .829, TINT .828 (T90 .934).
   - BOOTT costs about 1.2 percentage points of power against PCT.

**RESULTS**
- **Maximum FC (%) per design, taken over all 3 models and all p (F / N / C; worst-case Wilson 99% CI):**

| Design | BOOTT (the rule) | PCT (REL2) | TINT | XPCT |
|---|---|---|---|---|
| P8, all K | 2.0-2.5 / 2.1-2.5 / ≤ .56: FAIL | 5.9-7.8: FAIL | 2.5-4.3: FAIL | 3.5-4.6: FAIL |
| P16, all K | 1.36-1.58: FAIL | 2.6-3.0: FAIL | 1.7-2.4: FAIL | 1.6-1.9: FAIL |
| P32 K3 | .91 [.83, 1.00] / .88 / .47: PASS, robust | 1.65 [1.54, 1.77]: FAIL | 1.51: FAIL | 1.21: FAIL |
| P32 K11 | .96 [.88, 1.05] / .96 / .55: PASS, not robust | 1.59: FAIL | 1.27: FAIL | 1.11: FAIL |
| P32 K12 | .99 [.91, 1.09] / .99 / .59: PASS, not robust | 1.47-1.55: FAIL | 1.26-1.28: FAIL | 1.05-1.11: FAIL |
| P64 | .71-.80: PASS, robust | 1.04-1.11: FAIL | K3 1.09-1.12 FAIL; K11/K12 .97-1.00 pass | .85-.93: PASS |
| P128 | .65-.70: PASS, robust | .82-.87: PASS | .80-.90: PASS | .74-.79: PASS |
| P256 | .61-.69: PASS, robust | .74-.79: PASS | .75-.79: PASS | .73-.77: PASS |

  - BCA fails at P ≤ 32 and at P64 K11/K12 (1.00-1.01%). It passes from P128.
  - The realistic (coupled mixture) model is the one that binds almost everywhere. Its skewed pair statistics also push the t-interval and percentile bootstrap above the nominal 0.5% even at P256 (.75-.79%).
- **p_min for BOOTT (F / N / C):**

| Design | FLIP | NO_EFFECT | CHANCE |
|---|---|---|---|
| P256 K11 | .58 | .58 | .59 |
| P256 K12 | .57 | .57 | .58 |
| P128 K11 | .61 | .60 | .62 |
| P64 K12 | .64 | .64 | .66 |
| P64 K11 | 1.0 | 1.0 | .67 |
| P32 (all K) | 1.0 | 1.0 | .74 (K11) |

  - **Weakness: BOOTT's power collapses when normal accuracy is near 1.** At p = .99, FLIP power is .23 at P32 K11 (realistic) and .72 at P64 K11, while TINT has 1.00 at both.
    - Cause: most resamples of near-constant pairs have sd* = 0, so t* is infinite and no certificate is issued.
    - The frozen p_min rule ("80% power at every p' ≥ p") then gives p_min = 1.0 for FLIP and NO_EFFECT at P32-P64 (and at K3 up to P128/P256 for NO_EFFECT).
    - This affects REACH, STRICT and the INDETERMINATE/NOT_ELIGIBLE split. It does not affect CERT_OK.
    - POST HOC (out/pmin_posthoc.txt): capping the power curve at p ≤ .95 brings BOOTT's p_min to within .01 of TINT/PCT.
- **W-O's 733 verdicts under REL3.** Only saved marginals exist; W-O saved no pair arrays. I bounded the result over the unknown pair correlation rho and endpoint noise. For BOOTT at P256 I used the t normal-approximation (LOG A5).
  - 669 are determined: every one is identical to REL2.
  - 64 are ambiguous; each could drop from its REL2 certificate to INDETERMINATE: CHANCE_REL 44, NO_EFFECT_REL 17, FLIP_REL 3 (one of the 3, V0166, could also become NOT_ELIGIBLE).
  - 0 are inconsistent.

| Verdict | REL2 | REL3 determined | REL3 ambiguous |
|---|---|---|---|
| FLIP_REL | 170 | 167 | 3 |
| NO_EFFECT_REL | 81 | 64 | 17 |
| CHANCE_REL | 376 | 332 | 44 |
| INDETERMINATE | 105 | 105 | 0 |
| NOT_ELIGIBLE | 1 | 1 (V0081) | 0 |

  - STRICT: 32 rows go from NOT_ELIGIBLE to FLIP_REL: 23 determined, 8 ambiguous FLIP|NOT_ELIGIBLE and 1 ambiguous FLIP|INDETERMINATE|NOT_ELIGIBLE. The cause is the BOOTT p_min at P256 K12 (.57) combined with the approximate lo99 of the normal arm.
  - The 42 (absolute CHANCE, W-N gated FLIP_REL): 41 FLIP_REL and 1 ambiguous. They form 20 groups.
  - The 53: 52 FLIP_REL and 1 ambiguous. They form 28 groups. STRICT gives FLIP_REL 23, NOT_ELIGIBLE 21, ambiguous 9.
- **z class for the 170 FLIP_REL.** A class is determined only if it is the same for every rho in [-1, 1].
  - 101 COMPLETE, 33 PARTIAL, 21 COMPLETE|PARTIAL, 12 COMPLETE|OVERSHOOT.
  - By family: RELAY 45 COMPLETE, 27 PARTIAL, 6 ambiguous. MAJ 35 COMPLETE, 6 PARTIAL, 7 ambiguous. HOLD 21 COMPLETE, 20 ambiguous.
  - The 42: 19 COMPLETE, 18 PARTIAL, 5 ambiguous.
  - Specimens with PARTIAL flips: 369f5a5b 5, 9bbe8637 4, dcc7afb7 3, a8544b2d 3, 86fc0105 3, and 9 others.
- **Counts by specimen × source × offset group:** 249 groups in total.

| Verdict | Groups |
|---|---|
| FLIP_REL | 86 (56 specimens) |
| CHANCE_REL | 120 |
| INDETERMINATE | 53 |
| NO_EFFECT_REL | 42 |
| NOT_ELIGIBLE | 1 |

  - FLIP groups by z class: 50 all COMPLETE, 10 all PARTIAL, 26 mixed or ambiguous.
  - Among the absolute CHANCE verdicts, the FLIP_REL arms fall in 47 groups.

**KNOWN-ANSWER CHECKS (+ must-fail inputs)**

| Check | False certificates | Recovery | Result |
|---|---|---|---|
| KA1: W-Q rep 1 engine arrays, P256, 80 cells | 0 | 59/59 attainable exact-truth cells (STRICT also 59/59) | PASS |
| KA1: FLIP_REL z class | — | 30/30 COMPLETE (exact transfers) | — |
| KA2: disjoint blocks P32 (640 block-cells) | 0 | .73 | PASS |
| KA2: disjoint blocks P64 (320) | 0 | .98 | PASS |
| KA2: disjoint blocks P128 (160) | 0 | 1.00 | PASS |
| KA3: W-N rep-0 noiseless + flip noise (shared mask), q = 0 to .4 | 0 | 19/19 | PASS |

- KA2 P32 recovery below .80 is reported only; the PLAN criterion for KA2 is false certificates. The misses are CHANCE on S1_half blocks. PCT recovers .76 on the same blocks.
- Must-fail inputs (each was run and failed as required):
  - M1: PCT FAILS at P32 in my own simulation, up to 1.65% [1.54, 1.77].
  - M2: T90 FAILS at all 18 of 18 designs (5.6-10.9%).
  - M3: KA1 with FLIP and NO_EFFECT truth labels swapped gives 40 false certificates.
  - M4: with the floor disabled, BOOTT gives 1.58% at P16 and 2.46% at P8.
- In pytest: at P32 K3, T90 FC > 3% and PCT FC > the rule's FC. Disabling the floor gives FLIP_REL at P16, and disabling the guard gives FLIP_REL on a no-bit normal arm.

**DISAGREEMENTS**
1. **With my own prediction Pr3 and with the brief's framing that a simple t-interval or P-dependent level would do.** It would not.
   - TINT fails at P ≤ 32 and at P64 K3; its floor is 128.
   - XPCT fails at P32; its floor is 64.
   - BCA's floor is 128.
   - Only BOOTT holds 1% at P32, and there it is not robust at K11/K12 (upper CI 1.05-1.09%).
   - Pr2 (a floor of 16 or 32) held. Pr1 held for PCT; its claim that TINT/XPCT pass at P ≥ 32 missed. Pr4 half held: there are no determined changes, but 64 rows are ambiguous (predicted fewer than 10 changes).
2. **With W-Q: REL2's percentile interval "holds robustly at P256".** It holds (FC .74-.79%). But the tail inflation above the nominal .5% comes from the skew of the realistic model, not only from small P. It persists at P256 for PCT, TINT and XPCT; only the bootstrap-t removes part of it (.61-.69%).
3. **With W-Q (P64 "genuinely borderline, 1.04%").** At n = 80,000, PCT at P64 fails at every K (up to 1.11% [1.02, 1.21]). It is not borderline.
4. **With W-N's "about 0.5% error at any normal".** No candidate reaches 0.5% at the boundary under the realistic model. The best is BOOTT at about .6-.7%.
5. **With W-Q's split of the 42 (24 complete / 16 partial by point z).** With a paired CI that is conservative over rho, 18 are determined PARTIAL and 19 COMPLETE, with 5 undetermined. The partial-transfer caveat is stronger than W-Q stated.
6. **Caveat on my own rule.** BOOTT loses power near normal accuracy ≈ 1. Before promotion, consider a hybrid: BOOTT, but when resamples are degenerate fall back to the t-interval, or pool sd*. That needs its own frozen FC run. I did not change the frozen rule.

**PYTEST**
- Command, from W-U/: `PYTHONPATH=F:/Prometheus-worktrees/ananke-base-role PYTHONDONTWRITEBYTECODE=1 python -m pytest -q test_swap_rel3.py -p no:cacheprovider`
- Result: 10 passed in 1.96 s, RC=0 (out/pytest.txt).

**LEASES**
- Fabric skullport:cpu8 --as Ananke, lse-b3feff8054ae (token 2114fe8c…).
- Acquired 15:04:51Z; renewed 15:27Z and 15:58Z; released 16:17Z (printed RELEASED).
- `python -m fabric lease status` afterwards shows no cpu8 lease.
- At most 8 single-thread processes at any time. No GPU.
- Final Win32_Process check: 0 W-U python processes.

**COMPUTE**
- About 8.7 CPU core-hours: fc_sim 8.0, reach_sim 0.6, validation and tests about 0.05.
- About 1 h 20 min wall.

**FILES** (all under F:/Prometheus-worktrees/ananke-base-role/roles/Ananke/research/workers/W-U/)
- PLAN.md, LOG.md
- The rule and its tests: swap_rel3.py, test_swap_rel3.py
- Simulation and analysis scripts: intervals.py, fc_sim.py, reach_sim.py, build_table.py, validate3.py, apply733.py
- The rule's table: out/rel3_table.json
- FC and power results: out/fc_table.json, out/fc_maxima.txt, out/fc_w*.json, out/reach_w*.json, out/build_table.log, out/pmin_posthoc.txt
- Known-answer checks: out/ka_plants.json (+ .log)
- 733 re-application: out/rel3_733.csv, out/apply733.json (+ .log)
- Run records: out/pytest.txt, out/pids.txt, logs/

**PROPOSED FOLLOW-UPS**
- A frozen FC run for a BOOTT/TINT hybrid that fixes the degenerate-resample power collapse.
- An engine rerun that saves pair arrays for the 64 ambiguous rows (W-O saved none).
- Report group-level (specimen × offset) counts and z class as the primary evidence unit.
