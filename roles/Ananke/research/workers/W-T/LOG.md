# W-T LOG (E-ANANKE-W-T, T-INS-16, MWO-0004)

A0 14:05Z  Read COMMON_RULES(.md, _ARC3.md), W-S REPORT (RESULTS, DISAGREEMENTS only), W-S PLAN.md (for
           the P8 definitions), W-S probe/analyze/run/posthoc/posthoc_summary, W-R fork/specs/followdiff/
           posthoc code, W-R strat logs (per-offset classes). Context contamination: none beyond the brief.
A1 14:08Z  Prior strata (W-R raw npz, ns 0x620; not my test data): per (offset, phase) S/C/N fractions for
           4781b0a1 (frozen), 78f3b0ec and e06701a5 (follow). 78f3b0ec: S o0-o8, C o11-o14 q0; mixed
           thirds at o9 q0, o10, o11 q1, o14 q1, o15 q1. e06701a5 o5 q0 S.21 C.24 N.55.
A2 14:10Z  wt.py (plants PF/P1/PL, runner reusing W-S probe.fork) + summ.py. Dev plants ns 0x7ff M16 o4,5:
           P1_J1 decisive 1.00 in all 4 strata; PF_J1 decisive .83-.91 -- all 14 errors are pair-trials
           where no first-broadcast (PAY0) copy reached the readout (te1 is then a decoy); PL_J1 fails
           (o5 q1 .21); PF_J0 single classes (errors = the same decoy cases).
A3 14:15Z  Mixed-strata rule (n_SC >= 50, max(fS,fC) < .80) applied to prior data -> unit lists in PLAN s3.
A4 14:13Z  KA-R run: c16d5231 M64 ns 0x632 o4,5 (10 s, RC 0).
A5 14:16Z  KA-R compare: 584/584 eligible rows identical to W-S posthoc_c16d5231_ns632.json (pairs < 32):
           keyset, pattern, P8, n1_held, n1_flight, te1_rel. Must-fail vs ns 0x630 file: keysets differ,
           282/482 common rows mismatch. PASS.
A6 14:20Z  PLAN.md FROZEN.
A7 (correction) Clock times A0-A6 above were estimates; `date -u` gives: prior strata 14:07:59Z, dev plants
           14:10:36-14:11:01Z, PLAN frozen and hashed 14:13:07Z (sha256 e2b5f7de3a51...d5404580).
A8 14:13:07Z Lease: `python -m fabric lease status` -> [] ; acquire skullport:cpu8 --as Ananke ->
           lse-33d3f78d0178 ACQUIRED (expires 15:13:07Z).
A9 14:13:15Z Launch (launch.sh, 4 procs x 2 threads, ns 0x640 M 256). Win32_Process: 7300 (4781b0a1 o0-15),
           20312 (plants chain, first PLANT_P1_J1), 7324 (78f3b0ec o9,10,11,14,15), 15596 (e06701a5 o5).
A10 14:14Z pytest test_wt.py: 10 passed, RC 0 (logs/pytest.log).
A11 14:15Z e06701a5 done (64 s, 957 rows, normal acc .670). Summary out/summary_e06701a5.{txt,json}.
A12 ~14:17Z PLANT_P1_J1 (122 s) and PLANT_P1_J0 (83 s) done RC 0; 78f3b0ec done (178 s, 4975 rows).
           KA-P1 PASS (o4q0, o5q0 decisive 1.00 [1,1], cov .605/.602, P8any 1.00; shuffled dec .465/.467).
           KA-J0 PASS (0 M predictions; decisive S/C one class in every stratum; dec 1.00).
           78f3b0ec: DOES NOT REACH in all 6 mixed units (P8 dec .43-.57 ~ shuffle); te1 = t0+1, source
           re-emits ~4.4 distinct ticks, share re-broadcast .78, no relay copies.
A13 POST HOC (labelled, not in PLAN): posthoc.py -- emission-index predictors E1..E8 / ELAST / ALAST on
           78f3b0ec (same ns/M, re-run) to find which source emission the readout follows.
A14 ~14:21Z PLANT_PF_J1 (68 s) and PLANT_PL_J1 (102 s) done RC 0. KA-PF PASS: P8 decisive 1.00 [1,1] on
           pair-trials where a first-broadcast (PAY0) copy reached the readout (o4q0 n329, o5q0 n390; also
           clean strata); 100% of P8 decisive errors (61/61, 62/62 ...) are no-PAY0 pair-trials (te1 = decoy).
           Rule verdict on PF (all pair-trials): DOES NOT REACH (decisive .844 [.792,.891] o4q0, .863 o5q0).
           KA-PL PASS (must-fail plant): DOES NOT REACH in o4q0 (.700) and o5q0 (.755); o5q1 .406.
A15 ~14:22Z POST HOC 78f3b0ec (posthoc.py, 6 units): no emission-index predictor E1..E6 reaches in
           o9q0/o10/o11q1; ELAST (latest source emission with te <= tau) = ALAST = 1.00 [1,1] at o15q1,
           .751 at o14q1, ~.5 at o9-o11.
A16 14:23:27Z 4781b0a1 done (603 s, 17120 rows, normal acc .768). DOES NOT REACH in all 22 mixed units: P8
           decisive = its shuffle in every unit (o0-o3 .01: P8 says C, truth S; o12/o13 q1 .03-.05; best
           o7q1 .87 [.82,.92], equal to its shuffle .85). ~30 cue-bearing copies to the readout per pair-trial.
A17 14:24-14:26Z POST HOC posthoc_maj.py (offsets 4,5,9,12, same ns/M): MAJ traffic by emitter class. All
           non-sensor-0 copies come from the other 4 sensors (true relays 0); per pair-trial ~6 copies
           from sensor 0 and ~25 from the other sensors, ~7-9 in flight at tau. Counts do not differ by
           S/C/N pattern.
A18 14:26:09Z Win32_Process: 0 W-T python processes. Lease lse-33d3f78d0178 released (--lease --token) ->
           RELEASED; `python -m fabric lease status` -> []. Compute: 4 procs x 2 threads for ~10 min
           plus 2 post hoc runs of about 1 min each; about 0.4 core-hours total. No __pycache__ in W-T.
A19 (correction to A18) Compute recomputed from the run walls: runs 1220 s, post hoc about 350 s, dev and KA-R about 50 s, so about 1620 s x 2 threads = about 0.9 core-hours (A18's 0.4 was an underestimate).
