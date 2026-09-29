# W-Q LOG (E-ANANKE-W-Q, T-SWAP-REL2, MWO-0002)

## A0 2026-09-29 11:18Z  boot
- Read COMMON_RULES.md and COMMON_RULES_ARC3.md.
- Read, as the brief directs, W-N REPORT (RESULTS, DISAGREEMENTS) and W-O REPORT
  (RESULTS, DISAGREEMENTS). Read W-N swap_rel.py, attain_table*.py, plants_rel.py
  (header, run_fork, make_fn), run_plants.py; W-O runner.py lines 134-147 and
  summarize.py lines 11-79 (to learn how rel / rel_gated / K / p_min were derived).
- CONTEXT CONTAMINATION (declared): before writing PLAN.md I printed AGGREGATE counts
  of W-O out/rerun_table.csv: K distribution (11: 453, 12: 280), p_min distribution
  (.59: 453, .58: 280) and the (absolute, rel_ungated, rel_gated) triple counts
  (e.g. CHANCE/FLIP_REL/FLIP_REL 42, CHANCE/FLIP_REL/NOT_ELIGIBLE 53). I did NOT look at
  per-verdict rows (normal CIs, specimens, arms) of the 42 or any other case.
  I also saw the first two data rows (V0000, V0001) of rerun_table.csv in a `head`.
- Data check: rerun_s*.jsonl store per arm only P, cells, normal CI, swap CI, abs,
  rel_ungated, z. No per-pair arrays. The W-N certificate (rel_ungated) is saved, and
  the new gate needs only (normal CI, P, K), so no engine re-run of the 733 is needed.
- Lease status at boot: [] (no leases). No python processes with command lines of mine.

## A1 11:20Z  PLAN frozen (sha256 e0bbee84f4d3ce0e...), lease, engine launch
- Fabric lease skullport:cpu8 --as Ananke: lse-55fafa9180cf (token 29dd3a57...), ACQUIRED 11:19:56Z, ttl 5400 s.
- Launched run_plants2.py (rep 1, M=512) as 3 processes, PIDs in out/pids.txt:
  P1S q {0,.1,.2,.3,.4} 3 threads; P1S q {.05,.15,.25,.35,.45} 3 threads; P1SK all 10 q 1 thread.
  Plus simulations at 1 thread -> 8 threads total (lease envelope).
## A2 11:25Z  swap_rel2.py written; certificate == W-N swap_rel.rule on 300 random inputs
  (P in {8,32,256}, K in {3,11}): 300/300 verdict agreement, max |DF/DN diff| 2.2e-16.
## A3 11:26-11:31Z  build_tables.py (gate tables + V1). RC=0, 270 s. out/build_tables.log.
- P256 K11 p_min F/N/C = .57/.58/.59 (worst binds F,N; realistic binds C .59). fc_max .0097/.0090/.0090 -> CERT_OK all.
- P256 K12 p_min .58/.57/.58; fc_max .0077/.0088/.0080 -> CERT_OK all.
- P128 K11 .61/.60/.62, CERT_OK all. P64 K11 .64/.64/.67, fc_max .0110/.0115/.0095 -> CERT_OK F,N FALSE.
- P32 K3 .81/.82/.92, fc_max .0177/.0140/.0080 -> CERT_OK F,N FALSE. P32 K11 fc_max .0168/.0152 -> FALSE.
- PREDICTION P1 MISSED: I predicted FC <= .8% at P >= 32. Percentile-bootstrap FC at the boundary is
  ~.6-.8% at P256 (nominal .5%), ~.8-1.1% at P64, up to 1.8% at P32 (realistic model).
- P2 roughly held (F .57, N .58, C .59 at P256 K11; I predicted .55/.55/.58-.59).
- Hetero (out-of-model) FC max: P256 .85-.88%, P64 .95%, P32K3 1.68% (FLIP).
- Tiny P: P4 FC 13-16%, P8 4-6%, P16K3 2.5-3.1% (percentile bootstrap anti-conservative).
- MUST-FAIL level .80: FC at p=.52 FLIP 11.3% (worst) / 10.9% (realistic) > 1%  -> the check fails as required.
- WEAKNESS NOTED (rule not changed): CERT_OK = max over 24 MC point estimates (n=4000, SE ~.13%)
  vs 1%. At P256 K11 the max is .97% at one point (realistic p=.70); the max of noisy estimates is
  biased up, so CERT_OK at P256 is MC-fragile. Sensitivity run A4 at n=20000 (reported, not a rule change).
## A4 11:31-11:38Z  FC precision sensitivity, n=20000 per point (out/fc_precision.json/.log). Not a rule change.
- P256 K11 max FC (worst/realistic): FLIP .69/.79%, NO_EFFECT .75/.75%, CHANCE .66/.54%; means ~.59-.66%.
- P256 K12 max: FLIP .74/.89%, N .71/.77%, C .68/.59%.  -> CERT_OK at P256 is robust, not MC luck.
- P64 K11 max: FLIP .96/1.04%, N .92/1.03% (realistic mean .89%) -> borderline; CERT_OK false stands.
- P32 K3 max: FLIP 1.43/1.82%, N 1.11/1.42%, C .73/.54% -> FLIP/NE certificates miss the 1% target there.
## A5 11:33Z  pytest first run: 9 passed, 1 FAILED - my test expectation: the first seed with lo99<.59
  had lo99 < .57 = p_min_FLIP, so STRICT correctly gave NOT_ELIGIBLE. Fixed the test to pick a seed with
  .57 <= lo99 < .59 (the input the test is about). Rerun: 10 passed, RC=0.
## A6  P = 256 on every W-O arm (892 arms in rerun_s*.jsonl: 552 with 5632 cells = K11, 340 with 6144 = K12;
  1 group line has an error record and no arms). No data column is missing: no engine re-run of the 733.
## A7 11:38-11:44Z  engine rep 1 completed; P1SK process restarted mid-run (deviation, order only)
- P1S (both halves) finished 11:36Z. P1SK single-thread process (PID 47118) was stopped by me with kill
  right after it saved q=.15 (11:38:08Z; file verified to hold q .00-.15 intact), and the remaining q
  {.20,.25,.30} and {.35,.40,.45} were relaunched as 2 processes x 3 threads (<= 8 threads total, nothing
  else of mine running, checked in Win32_Process). All DONE 11:43:56Z. Same seeds, same code: no effect
  on results, only wall time.
- Lease lse-55fafa9180cf RELEASED 11:44:00Z; `python -m fabric lease status` -> [].
## A8 11:44Z  V3 validate_plants.py RC=0 (out/v3_plants.json, out/v3_plants.log)
- rep0 (W-N saved, 56 cells) REL2: 0 false certificates; 38/38 attainable exact-truth cells issued -> PASS.
- rep1 (fresh, 80 cells, certificate recomputed from arrays) REL2: 0 false; 60/60 -> PASS. STRICT: PASS both.
- MUST-FAIL (a) truth labels swapped (FLIP<->NO_EFFECT): 28 (rep0) / 40 (rep1) false certificates -> FAIL as required.
- MUST-FAIL (b) W-N gated verdicts on the same cells: issued 35/38 and 56/60; misses all at q=.40
  (lo99 .573-.586 < .59) -> check (b) not failed on rate (>= 80%) but ne-consistency fails (W-N gives
  NOT_ELIGIBLE where REL2 has an attainable verdict) -> overall FAIL as required.
  Note: (b) at 80% is too blunt to fail on W-N's rate alone; the failing element is per-cell (q=.40 FLIPs).
- Operationalisation (from PLAN wording): (b) counts only cells with z_true within .05 of -1/0/+1
  (S1_3q z=-.38 excluded; S1_half z=+.03 included). S1_half/S1_3q z_true from q=0 noiseless swap:
  f = .484/.691 in both reps (mask depends on pair index only).
- Observed: at q=.45 (lo99 .521-.532) REL2 issues correct FLIP_REL / NO_EFFECT_REL / CHANCE_REL certificates
  that STRICT and W-N refuse; P1SK S/Kp are exact ties (s = .5 with zero variance), so their CHANCE_REL
  is attainable far below the power table (degenerate plant, not evidence about real specimens).
## A9  apply_wo.py RC=0 (out/rel2_table.csv, out/apply_summary.json, out/apply_wo.log)
- 733 rows; REL2: FLIP_REL 170, NO_EFFECT_REL 81, CHANCE_REL 376, INDETERMINATE 105, NOT_ELIGIBLE 1.
  STRICT: 117 / 80 / 354 / 105 / 77.
- The 42: REL2 FLIP_REL 42/42, STRICT 42/42 (lo99 .580-.672; 14 specimens, 20 specimen x offset groups;
  z <= -.95 on 24, -.95..-.75 on 2, -.75..-.57 on 16 -> NOT all complete transfers).
- The 53 (ungated FLIP_REL, W-N NOT_ELIGIBLE): REL2 FLIP_REL 53/53, STRICT NOT_ELIGIBLE 53/53 (lo99 .552-.576).
- P3 held (42/42; >=40 of 53 -> 53). P3's "21 CHANCE_REL" -> 22 (W-N gated NE -> CHANCE_REL).
- Only REL2 NOT_ELIGIBLE: V0081 3c3d996a channel_count, ungated INDETERMINATE, lo99 .564 (< all p_min).
## A10  final pytest: 10 passed, RC=0 (out/pytest.txt). No W-Q python processes running (count 0).
  Lease status shows only lse-848b29b24607 skullport:gpu (Ananke FP-001, not mine); mine released.
