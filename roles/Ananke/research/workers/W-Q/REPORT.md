<!-- DEPOSITED VERBATIM by Ananke for worker W-Q; sha256(report)=0fd1efca5c5ceb4f; delimited; see REPORT.provenance.json -->
W-Q T-SWAP-REL2 (E-ANANKE-W-Q, successor of T-SWAP-LOWACC thr-5df816e9b844, MWO-0002)

WHAT I TESTED
- Replaced W-N's single worst-case gate with per-verdict attainability.
  - W-N's gate: NOT_ELIGIBLE for every verdict if lo99(normal) < p_min(P,K), where p_min is the normal at which all three verdicts have at least 80% power.
- PLAN.md was frozen at sha256 e0bbee84f4d3ce0e… before any simulation, engine run or per-row read of W-O's table.
- Context declared in LOG A0: before the PLAN I had seen aggregate counts of rerun_table.csv (the class triples, K and p_min), but no per-case rows of the 42.
- The certificate is W-N's rule, copied. It agrees with W-N's swap_rel.rule on 300 of 300 random inputs (largest difference 2.2e-16).
- Attainability tables come from simulation only (no specimen data), under two dependence models:
  - WORST (W-N's): normal and swap arms are independent.
  - REALISTIC: arms coupled per pair. Each pair is either transferred (swap = 1 - normal), unaffected (swap = normal) or chance. This is how the engine plants behave.
- Validation:
  - Synthetic false-certificate tables, including an out-of-model heterogeneous-pair model and very small P.
  - W-N's saved engine plants (rep 0).
  - A fresh engine replicate (rep 1): P1S and P1SK, M=512, q in {0, .05, …, .45}, with pair-level arrays saved and the certificate recomputed end to end.
- Application: all 733 W-O verdicts, from saved data. P=256 on every arm; K=11 on 552 arms and K=12 on 340.

THE FROZEN RULE (W-Q/swap_rel2.py)
1. CERTIFICATE (W-N's rule)
   - DF = (s-.5)+(a-.5)/2 and DN = (s-.5)-(a-.5)/2, with a 99% pair bootstrap (2000 resamples, seed 0).
   - FLIP_REL if hi(DF)<0; NO_EFFECT_REL if lo(DN)>0; CHANCE_REL if lo(DF)>0 and hi(DN)<0.
2. IDENTIFICATION GUARD: if lo99(normal) <= .50, every verdict is NOT_ELIGIBLE, because at g=0 the three hypotheses coincide.
3. Per verdict V, two conditions:
   - CERT_OK_V: the false-certificate rate at V's boundary truth (z = -1/2, +1/2, or both for CHANCE) is <= 1%.
     - Checked at every normal p in {.50, .51, .52, .55, .58, .60, .65, .70, .80, .90, .95, .99}.
     - Checked under both the worst and realistic models, with n=4000 simulations per point.
   - REACH_V: lo99(normal) >= p_min_V.
     - p_min_V is the smallest p at which power is >= 80% for all p' >= p (V exactly true, n=400).
     - The maximum over the two models is used.
   - ATTAIN_V = guard AND CERT_OK_V AND REACH_V.
4. LABEL (REL2)
   - Certificate V issued: V if CERT_OK_V, else NOT_ELIGIBLE.
   - No certificate: INDETERMINATE if any verdict is attainable, else NOT_ELIGIBLE.
   - Every row also carries NE = the list of unattainable verdicts, whose absence tells you nothing.
   - Why: a certificate's error is its false-certificate rate, which power does not change. Power only matters for reading an absence.
5. REL2-STRICT, a sensitivity variant reported but not the primary rule: a certificate also needs REACH_V.

RESULTS
- Attainability tables (out/attain2_table.json):

| Design | p_min FLIP / NO_EFFECT / CHANCE | CERT_OK |
|---|---|---|
| P256 K11 | .57 / .58 / .59 | all three |
| P256 K12 | .58 / .57 / .58 | all three |
| P128 K11 | .61 / .60 / .62 | all three |
| P64 K11 | .64 / .64 / .67 | CHANCE only |
| P32 K3 | .81 / .82 / .92 | CHANCE only |

  - CHANCE is the verdict that binds W-N's .58-.59 gate. FLIP and NO_EFFECT are attainable 1-2 points lower.
- False-certificate rate at the boundary is ~.6-.9%, not the nominal .5%. The percentile bootstrap errs on the permissive side, and more so as P falls. A precision re-run at n=20000 per point (out/fc_precision.json) gave:

| Design | Mean FC | Max FC (FLIP, realistic) |
|---|---|---|
| P256 K11 | .59-.66% | .79% |
| P256 K12 | .58-.70% | .89% |
| P64 K11 | about .89% | 1.04% |
| P32 K3 | 1.36% | 1.82% |

  - So at P256 the 1% target holds robustly. At P32 and P64, FLIP and NO_EFFECT certificates miss it.
- W-O's 733 verdicts under REL2:

| Verdict | Count | Wilson 99% | Specimen-cluster 99% |
|---|---|---|---|
| FLIP_REL | 170 | [.194, .274] | [.154, .354] |
| NO_EFFECT_REL | 81 | [.084, .144] | [.059, .161] |
| CHANCE_REL | 376 | [.466, .560] | [.424, .594] |
| INDETERMINATE | 105 | [.113, .180] | [.075, .207] |
| NOT_ELIGIBLE | 1 | [0, .012] | [0, .007] |

  - REL2-STRICT: FLIP_REL 117, NO_EFFECT_REL 80, CHANCE_REL 354, INDETERMINATE 105, NOT_ELIGIBLE 77.
- REL2 against W-N's gated verdicts:
  - Every eligible verdict is unchanged.
  - W-N's 81 NOT_ELIGIBLE become FLIP_REL 53, CHANCE_REL 22, INDETERMINATE 4, NO_EFFECT_REL 1 and NOT_ELIGIBLE 1 (V0081, 3c3d996a channel_count, lo .564).
- REL2 against the absolute rule:
  - The 615 absolute CHANCE verdicts become FLIP_REL 95, NO_EFFECT_REL 54, CHANCE_REL 365, INDETERMINATE 100, NOT_ELIGIBLE 1.
    - FLIP_REL share: Wilson [.121, .196], cluster [.084, .290].
  - Absolute FLIP 90 become FLIP_REL 75, CHANCE_REL 10, INDETERMINATE 5.
  - Absolute NO-EFFECT 28 become NO_EFFECT_REL 27, CHANCE_REL 1.
- THE 42 (absolute CHANCE, W-N gated FLIP_REL): REL2 FLIP_REL 42/42, and STRICT FLIP_REL 42/42 too.
  - lo99(normal) ranges .580-.672. Sources: W-F 38, W-I 4. Families: RELAY 19, MAJ 16, HOLD 7.
  - They sit on 14 specimens but only 20 specimen × source × offset groups. Arms of one group share the normal run and often have identical swap values, so they are not independent evidence.
  - By specimen and arm:
    - 26f9428b MAJ: channel_all mid and late, channel_count, joint.
    - 626aa72f MAJ: channel_all, channel_content, joint, pay0 (mid); site_all late.
    - 8e1caf6b MAJ: channel_all mid and late, joint (z -1.00); channel_content and pay3 (z -.64).
    - 8743da7f MAJ: channel_content, pay0 (z -.77).
    - c939c3c7 RELAY: joint mid, site_all mid and late.
    - e2334ea7 RELAY: joint mid.
    - 86fc0105 RELAY: joint (z -1.00); channel_all, channel_content, pay0 (z -.66 to -.70).
    - 9bbe8637 RELAY: channel_all mid and late, channel_content, pay0 (z -.68).
    - dcc7afb7 RELAY: channel_all, channel_content, pay0 (z -.57/-.58).
    - 369f5a5b RELAY (W-I): S at o1 and o14 (z -.58/-.59).
    - 42716814 RELAY (W-I): S o13, site_all o12 (z -.70/-.71).
    - HOLD 688b9f6f: joint mid, site_all mid and late.
    - HOLD faafa5b0: joint mid, site_all mid and late.
    - HOLD 62c6fa31: site_all late.
  - Completeness: z <= -.95 on 24; -.95 to -.75 on 2; -.75 to -.57 on 16. So 16 of the 42 are certified FLIP_REL (closer to 1 - normal than to .5) but not complete transfers.
- THE 53 more (absolute CHANCE, W-N ungated FLIP_REL, gated NOT_ELIGIBLE): REL2 FLIP_REL 53/53, STRICT NOT_ELIGIBLE 53/53.
  - All from W-F; 19 specimens; lo99 .552-.576; z <= -.95 on 45.
  - Any claim resting on these depends on the rule choice in 2.4 (certificate needs only CERT_OK), not on power.
- PLAN predictions:
  - P1 MISSED: I predicted false-certificate rate <= .8% at P >= 32.
  - P2 roughly held.
  - P3: held for the 42 (42/42) and the 53 (53/53, predicted >= 40). Its third part missed by one: 22 of W-N's NOT_ELIGIBLE became CHANCE_REL, not the predicted 21.

KNOWN-ANSWER CHECKS (+ must-fail inputs; each must-fail was run and failed)
- V1 synthetic false certificates (FC in the table is the false-certificate rate):

| Check | Result | Must-fail input and outcome |
|---|---|---|
| FC <= 1% at P256 K11/K12, both models and hetero (max .97%, hetero .88%) | PASS | Same rule at CI level .80, normal .52: FC 11.3% (worst) / 10.9% (realistic), so it FAILS |
| FC at P32/P64 FLIP and NO_EFFECT | FAIL (up to 1.8%) | This one legitimately fails, so CERT_OK is false there |
| Tiny P: FC 13-16% at P4, 4-6% at P8 | — | Shows where the percentile bootstrap breaks |

- V2 identification guard:
  - Input: no-bit normal .50 with a swap biased to .47. The raw certificate is FLIP_REL; REL2 says NOT_ELIGIBLE.
  - Must-fail: with the guard disabled, FLIP_REL is issued.
- V3 engine plants:

| Replicate | False certificates | Attainable exact-truth cells issued | Result |
|---|---|---|---|
| rep 0 (56 cells) | 0 | 38/38 | PASS |
| rep 1 (80 cells) | 0 | 60/60 | PASS |

  - STRICT also passes on both replicates.
  - Truth for S1_half and S1_3q comes from the realized mask fraction f (.484 / .691, same in both reps), giving z_true = +.03 / -.38.
  - At q=.45 (lo99 .52-.53) REL2 issues the correct certificate on every certificate-truth arm; STRICT and W-N refuse.
  - Must-fail (a): with truth labels swapped between FLIP and NO_EFFECT, there are 28 (rep 0) / 40 (rep 1) false certificates, so it FAILS.
  - Must-fail (b): W-N's gated verdicts on the same cells miss the true FLIP_REL (and in rep 1 NO_EFFECT_REL) at q=.40 (lo99 .573-.586 < .59). The check FAILS on NE-consistency.
    - Its hit rate (92-93%) stays above the 80% line, so the frozen rate criterion alone is too blunt to fail it.
  - Caveat: P1SK S/Kp are exact ties with zero swap variance, so their CHANCE_REL tells us nothing about real specimens.
- V4 pytest checks:
  - A true complete transfer at normal .60 with .57 <= lo99 < .59 gives REL2 FLIP_REL; W-N's gate gives NOT_ELIGIBLE (must-fail shown).
  - Computing REACH at the point estimate instead of lo99 hides CHANCE's unreachability (must-fail shown).
  - A P32 K3 FLIP certificate gives NOT_ELIGIBLE; the P256 table would admit it (must-fail shown).
  - End to end on arrays: FLIP and NO_EFFECT are recovered; the NO-EFFECT arm fed to the FLIP check fails.
  - Certificate identity with W-N passes; against a 90% rule it disagrees.
- Known weakness, reported and not changed: CERT_OK is a maximum over noisy simulation estimates, so it is biased upward. At P256 the n=20000 re-run confirms the margin. P64 is genuinely borderline (1.04%).

DISAGREEMENTS
1. With W-N: "the rule's certificates keep about 0.5% error at any normal above .5" is not right.
   - The percentile bootstrap gives ~.6-.9% at P256, ~.9-1.0% at P64, and up to 1.8% at P32 (FLIP, realistic model).
   - At W-L's design (P32 K3), FLIP_REL and NO_EFFECT_REL certificates do not meet a 1% target at any normal. W-N's .91 gate hid this by refusing almost everything there.
2. With W-N: the single gate is too strict in a way that is not only about power.
   - It suppressed 53 FLIP_REL certificates whose false-certificate rate is fine.
   - It suppressed the engine-plant FLIPs at q=.40 in both replicates.
   - CHANCE is the verdict that binds the gate; FLIP and NO_EFFECT reach 80% power at .57-.58.
3. With W-O ("42 … complete transfers, swap about 1 - normal"): only 24 of the 42 have z <= -.95; 16 are partial (z -.57 to -.77).
   - Examples: 369f5a5b S, dcc7afb7 channel arms, 86fc0105 channel/pay0, 9bbe8637, 8743da7f, 42716814.
   - FLIP_REL certifies z < -1/2, not z = -1.
   - The 42 are also 20 dependent groups, not 42 independent findings.
4. With W-O's "the absolute rule can never call these FLIP; W-N's relative rule is needed": correct.
   - The relative rule's reach under per-verdict attainability is wider than W-O reported: 95 of the 615 absolute CHANCE verdicts become FLIP_REL, not 42.
   - 53 of those 95 depend on accepting a certificate without 80% power at lo99.
5. With my own PLAN: P1 missed, and P3's CHANCE_REL count was off by one (22, not 21); see RESULTS.

PYTEST
- Command, from W-Q/: `PYTHONPATH=<worktree> python -m pytest -q test_swap_rel2.py -p no:cacheprovider`
- Result: 10 passed in 3.82 s, RC=0 (out/pytest.txt).
- The first run had 1 failure, caused by a wrong expectation in my test, not the rule (LOG A5): I picked a seed with lo99 < .57, where STRICT correctly refuses.

LEASES
- Fabric skullport:cpu8 --as Ananke, lse-55fafa9180cf (token 29dd3a57…), ttl 5400 s.
- Acquired 11:19:56Z; released 11:44:00Z (printed RELEASED).
- `python -m fabric lease status` afterwards shows no cpu8 lease. The only entry is lse-848b29b24607 skullport:gpu (Ananke FP-001), which is not mine.
- At most 8 threads at any time. No GPU.
- Deviation, order only (LOG A7): I stopped the 1-thread P1SK process after its q=.15 save and relaunched q .20-.45 as 2 processes × 3 threads.
- Final Win32_Process check: 0 W-Q python processes.

FILES (F:/Prometheus-worktrees/ananke-base-role/roles/Ananke/research/workers/W-Q/)
- PLAN.md, LOG.md
- Code: swap_rel2.py, test_swap_rel2.py, build_tables.py, run_plants2.py, validate_plants.py, apply_wo.py
- Tables and checks: out/attain2_table.json, out/v1_fc_checks.json, out/fc_precision.json (+ .log), out/build_tables.log
- Engine rep 1: out/plants_r1_P1S_*.npz/.json and out/plants_r1_P1SK_*.npz/.json (the file named with all 10 q holds q .00-.15 only)
- Engine run logs: out/run_*.log, out/pids.txt
- Validation and application: out/v3_plants.json (+ .log), out/rel2_table.csv, out/apply_summary.json, out/apply_wo.log, out/pytest.txt

PROPOSED FOLLOW-UPS
- Replace the percentile bootstrap with a studentized or BCa interval, or a P-dependent level, so FLIP and NO_EFFECT certificates meet 1% at P32-P64.
- Report z with a paired CI next to every FLIP_REL, so partial and complete transfers are kept apart.
- Count evidence by specimen × offset group, not by arm.
