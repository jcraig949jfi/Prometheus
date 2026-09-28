# W-L LOG

Context: read before PLAN only COMMON_RULES*.md, the brief, the engine/envs/search/
assays/lens/plants/physics code, c1b_run.load, W-G wg.py (code), and
instruments/INSTRUMENT_CARRIER_SWAP.md. No context contamination from
SYNTHESIS*/C1B_REVIEW*/PTE_ENGINE_CARD/ARC3_PRIORITIES/REPORT.md files.

## Attempt 0 (2026-09-28) PLAN.md frozen
Physics = M2 (4ab2ba014aac967e) unchanged. Search spec = M2 row's spec.
GPU lease status at start: held by W-J (E6, until ~1790579986). cpu8 held by W-I.

## Attempt 1 checks.py (CPU, 2 threads) -> out/checks.json
Plants at M2 physics (state_dim 2, prog_len 16), 64 worlds, both 0x5F2 and 0x5F3:
  P1S (n=1, 9 lines)   acc 1.000 [1.000, 1.000] both namespaces
  P1K (n=1, 13 lines)  acc 1.000 [1.000, 1.000] both
  P2S (n=2, 16 lines)  acc 1.000 [1.000, 1.000] both  -> no fallback physics needed
  LAG0 on n=0 (HOLD)   1.000; NULL .500 everywhere
  LAG0 n=1: .474 [.398,.545] / .517 [.446,.585]; LAG0 n=2: .531 [.453, .609] / .519 [.444,.591]
  P1S on n=2: .500 [.438,.563] / .503 [.434,.575]
T2 (mirror) PASS; T3 host exhaustive PASS (max over 16 functions of the other
lags .502-.504); T4 PASS.
FAILS AS WRITTEN (both are check-design defects, not task defects; reported
as deviations):
 - T1 FAIL: (i) the distractor comparison used sign(sum of 8 +-1 draws), which
   is 0 with p = C(8,4)/256 = .27, so agreement ~.36 by construction (y is never
   0). (ii) the per-trial min/max band [.47,.53] is ~3 SD for 2048 independent
   pairs, and one per-trial min (.468, n=0 j=1) fell just outside.
 - T3 engine: LAG0 on n=2 analysis ns hi99 = .609 > .60 (CI contains .5; 32
   pairs x 10 trials cannot resolve a .60 bound reliably).

## Attempt 2 checks_v2.py (deviation, fresh samples) -> out/checks_v2.json
T1 v2 (pooled-over-trials per lag, distractor conditional on nonzero sum, fresh
4096 worlds, key 0x8): PASS for n = 0, 1, 2 (all non-target lags .487-.514;
distractor agreement .500 / .500 / .505).
T3 engine recheck, 512 fresh worlds: LAG0 n=1 .509 [.488,.531], LAG0 n=2 .495
[.470,.521], P1S n=2 .498 [.472,.523]: PASS. Conclusion: no sequential exploit;
the lag-n target is independent of every other visible quantity.

## Attempt 3 carriers.py on plants (CPU) -> out/carriers_plants.json
Swap before cue k (k = 4, 6, 8), trial k scored, 64 worlds (0x5F2 key 0xCA):
  P1S: S FLIP (0.00), site_all FLIP; Kp/w/inbox/channel/pay0/pay1 NO-EFFECT; reset_S -> .50
  P1K: Kp FLIP (0.00), site_all FLIP; S and all others NO-EFFECT; reset_Kp -> .50
  P2S: S FLIP (0.00), site_all FLIP; others NO-EFFECT; reset_S -> .50
Instrument known answers PASS (PLAN s3c). The plant question is well posed:
n=1 and n=2 are solvable at M2 physics / prog_len 16 by site-state and by Kp stores.

## Attempt 4 preregistered searches (GPU lease c1aec189c26a, 07:11-07:41Z, released)
run_all.sh -> out/search_n<n>_s<s>.json, out/log_*.txt. ~62 s per search (pop 96 x 36 gens).
Held-out 0x5F3 (64 worlds) acc [lo99, hi99]; best no-memory baseline; diff lo99; zero_comm:
  n1_s0 .686 [.642,.737] LAG0 .528  diff lo .104  zc .686  SUCCESS
  n1_s1 .513 [.460,.562]            diff lo -.125           fail
  n1_s2 .629 [.581,.675] NULL .500  diff lo .081  zc .619  fail (lo99 < .60)
  n1_s3 .737 [.695,.783] LAG0 .517  diff lo .155  zc .737  SUCCESS
  n2_s0 .620 [.558,.680] NULL .500  diff lo .058           fail (lo99 < .60)
  n2_s1 .671 [.617,.723] P1S .522   diff lo .075  zc .672  SUCCESS
  n2_s2 .691 [.639,.744] P1S .547   diff lo .078  zc .691  SUCCESS
  n2_s3 .489 [.441,.536]                                    fail
  n0_s0 (control) .672 [.637,.702]; n0_s1 .512 [.493,.528]
PLAN defect found: for n=0 criterion (b) is unsatisfiable (LAG0 IS the n=0
solution, 1.000), so the pipeline control is read on (a) only: 1/2 reach lo99 > .60.
Arm readings (as preregistered): n=1 REACHED 2/4, n=2 REACHED 2/4 (not robust).

## Attempt 5 carriers_champs.py (GPU, same lease) -> out/carriers_champs.json
All SUCCESS champions + n1_s2: S swap acc .32-.39 (normal .58-.61 on trials 4/6/8),
site_all identical to S; Kp, w, inbox, channel_all, pay0, pay1 NO-EFFECT (exactly
normal); reset_S -> .44-.53, all other resets/flush -> normal. n=2 back1 swap: S
again the only effect. zero_comm = normal in every SUCCESS champion.
Formal verdict CHANCE, not FLIP: with normal ~.6, a complete transfer gives ~.4,
so hi99 < .40 is unattainable (eligibility defect of the verdict rule at low
accuracy, not evidence of a split carrier). Swap acc <= 1 - normal in all four.

## Attempt 6 lagprofile.py (POST-HOC, not preregistered) -> out/lagprofile.json
P(sign S0 at readout k == c_{k-j}), j = 0..4, k >= 4, 256 fresh worlds (0x5F3 key 0x1A6):
  plants: P1S peak j=1 only (1.0 / ~.5); P2S j=2 only; INTEGRATOR (S0 += SENSE) flat .63-.65
  n1_s0 flat .63-.65 ; n2_s1 flat .60-.62 ; n2_s2 flat .60-.62 (n2_s0 identical) ;
  n0_s0 flat .62-.65  -> integrators (answer = sign of summed cue history)
  n1_s3 .588 / .694 / .599 / .513 / .603 -> weighted integrator, partial lag-1 preference
  n1_s2 .513 / .635 / .510 / .384 / .487 -> the only lag-selective one (negative weight at lag 3)
Decompiled programs (carriers_champs.json) agree: n2_s2 has S0 += SENSE twice
(lines 6, 10); n1_s0 has S1 := SENSE + c; S0 += S1.
