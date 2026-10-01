<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-R; sha256(report)=5f15af6f0b9a5ebb; delimited; see REPORT.provenance.json -->
# W2-R: does the noise-cancelling bonus shape C1 champions, and how much accuracy is left in timing?

Worker: W2-R (Opus), Ananke seat, wave 2. Directory: roles/Ananke/research/harvest/wave2/W2-R/
Everything ran on CPU only, eager, 2 threads (asserted torch.cuda.is_available() == False). No repo file outside my directory was touched. No git writes, no lease actions.

The prediction was written in PLAN.md before any champion was classified or evaluated.

Files in my directory:
- r_common.py: `eval_full` is an exact copy of `assays.evaluate` for P=1 that also returns S0 at the readouts. bench.py checked it bit-equal on acc, sens_act and sens_any for 3 cells.
- static_cls.py, static_check.py, static_tab.py: static classifier, its 8 known-answer sanity checks, and the cross-tabulation.
- dyn.py, dyn_tab.py: dynamic sample.
- curve_tab.py: population-level analysis from the recorded curves (zero compute).
- tune.py, tune_tab.py: timing sweep.
- out/*.json, out/*.log: all outputs.

## 1. Findings

### F1 [V] The noise-cancelling bonus (W2-A1 F4) leaves no detectable footprint on C1 champions. The prediction is refuted.

**Static classes.** Each champion's rules were classified, with each rule weighted 1/rules. Comm families only (RELAY, XOR, MAJ, FLIP):

| noise | label | n | LIN_COMM | LIN_SENSE | THRESH | NONLIN | NOINPUT | majority LIN_COMM |
|---|---|---|---|---|---|---|---|---|
| 0 | NULL | 176 | .139 | .048 | .124 | .257 | .432 | 22 |
| 0 | SIG | 49 | .281 | 0 | .296 | .281 | .143 | 12 |
| 16 | NULL | 117 | .147 | .043 | .156 | .252 | .402 | 17 |
| 16 | SIG | 5 | .200 | 0 | .300 | .400 | .100 | 1 |
| 64 | NULL | 161 | .169 | .042 | .110 | .314 | .365 | 29 |
| 64 | SIG | 15 | .433 | 0 | .067 | .183 | .317 | 7 |

- Among NULL champions, the majority-LINEAR fraction at noise 64 is 29/161, against 22/176 at noise 0: odds ratio 1.54, Fisher p = .17. At noise 16 the odds ratio is 1.19, p = .73.
- Per-family tables are in out/static_weighted.json and in the static_tab.py output. RELAY NULL champions at noise 64 are the least linear of the three noise levels (LIN_COMM .083).

**Dynamic sample.** 91 comm-family champions, stratified by noise × label × static class, on 32 fresh worlds (16 pairs):
- No champion had sens_act ≥ .5 at acc < .6. The highest sens_act among NULL champions was .32.
- NULL champions that are statically LINEAR at noise 64 averaged sens_act −.022 and acc .495. Their readout slice reaches IN, but no signal arrives there, so the twin difference is zero.

**Population level** (recorded curves, all 678 runs). "max_contrast" is the population's maximum sens_act on that generation's 8 worlds. At the final generation of NULL runs at noise 64:
- the median is .104 (RELAY), .073 (XOR), .167 (MAJ), .125 (FLIP);
- the share of runs with max_contrast ≥ .5 and max_acc < .6 is 0% in RELAY, XOR and FLIP, and 5% in MAJ (3/62);
- RELAY NULL is lower at noise 64 than at noise 0 (.104 vs .188).

**Check:** `python static_tab.py; python dyn_tab.py; python curve_tab.py`

**Confidence:** high that F4 has no measurable effect on recorded champions or on the populations' top contrast.

**Strongest objection:** the champion is picked by accuracy alone, and the final population is not stored. A shaped population could still steer the trajectory without leaving high-contrast genomes at the end. The curves argue against this, because max_contrast stays low in every generation; the "any generation ≥ .5" rate for RELAY, XOR and FLIP NULL runs at noise 64 is 0 to 3%.

**Why F4 has nothing to act on (third explanation):** both the predicted reading ("the bonus selects linear sub-noise codes") and its opposite assume the bottleneck is how well the code survives noise. In NULL comm cells the bottleneck is earlier: no signal reaches the actuator at all, so lead − twin = 0 and sens_act = 0 for any readout type. F4 needs a working but sub-noise path. The search rarely builds one, and with ±256 payloads against ±64 noise a working path is usually above noise anyway.

**Unresolved:** the 3 MAJ runs at noise 64; a run with the bonus switched off.

### F2 [V] SIGNAL champions are not mainly thresholded, and a threshold op is not a mechanism marker.

- `envs.score` already applies sign(S0), and S0 = 0 scores .5. A linear S0 is therefore a complete readout.
- SIGNAL comm champions carry more LIN_COMM weight than NULL champions (.28 to .43 against .14 to .17).
  - SIG vs NULL at noise 0, majority-LINEAR: odds ratio .35, p = .004.
  - At noise 64, MAJ SIGNAL champions are predominantly linear sums (LIN_COMM .42). Dynamically they have graded S0 (median 73 distinct values on 8 worlds, top-3 value mass .11) and an odd, antisymmetric code (common-mode ratio CM = .21). A linear sum of noisy packets, scored by sign, is the right majority mechanism.
- Static and dynamic classes agree. Statically LINEAR champions have many distinct S0 values (median 12 to 73); statically THRESH champions have few (median 2 to 14) and top-3 mass ≥ .87.

**Confidence:** high.

**Objection:** the static classifier ignores WIMM/Kp-modified immediates, SETRULE switching, and clamp saturation acting as an implicit threshold. It passed 8 known-answer checks (relay_flood, hold_latch, the W2-A1 linear toy, loop-carried and overwrite cases).

### F3 [V] The bonus excess that is actually paid comes from one-sided codes, not from noise cancellation.

- Define X = sens_act − max(0, 2·acc − 1), the bonus paid beyond what accuracy explains. In the 91-champion sample:
  - X > .2 in 6/38 champions at noise 0, 3/23 at noise 16 and 1/30 at noise 64. That is the opposite trend to F4.
  - The top-X champions (X .23 to .35) are noise-0 RELAY SIGNAL champions with CM = 1.00 exactly and S0 = 0 on .64 to .76 of readouts. One twin reads 0, so it scores .5 while the twin difference still has the right sign.
- Across the sample, sens_act tracks 2·acc − 1 (r = .91, slope 1.13).
- This is the Wave-1 audit's item 0.3 ("the bonus pays one-sided codes"), now measured on real champions. F4's mechanism is not visible.

**Check:** dyn_tab.py and the inline X/frac0/CM listing (out/dyn.json).

**Confidence:** high for the sample; n = 91, with 8 per stratum.

### F4 [V] Timing slack: 4 of the 16 comm champions swept are credibly out of tune by ≥ .03. All 4 sit in one cell family.

Method:
- One change at a time: lat_base −1/+1/+2, then env delta −2/−1/+1/+2 (delta is inert for HOLD).
- Discovery: 16 fresh pairs, paired against native on the same worlds.
- Confirmation (to remove the winner's curse): the best variant against native on a disjoint 16-pair set.

Discovery gains by variant (only rows with a confirmed gain shown):

| cell | parent | native | lat−1 | lat+1 | delta−1 | delta+1 | confirmed gain [99% CI] |
|---|---|---|---|---|---|---|---|
| f7e62fe3 | 62a7fff9 | .836 | −.138 | +.065 | +.057 | −.078 | +.060 [+.031, +.091] |
| 4316f167 | 31cd2a8a | .789 | −.109 | +.083 | +.062 | −.062 | +.086 [+.060, +.112] |
| e9196cae | c16d5231 | .826 | +.016 | −.133 | −.122 | +.075 | +.091 [+.047, +.141] |
| e06701a5 | 31cd2a8a | .673 | −.074 | +.023 | +.038 | −.005 | +.033 [+.003, +.066] |
| 72dd71d8 | 62a7fff9 | .853 | −.033 | −.001 | +.040 | +.021 | +.033 [−.019, +.090] |
| 8c37f32e | c16d5231 | .828 | −.120 | +.055 | +.099 | −.070 | +.042 [−.018, +.099] |
| 023539c4 (MAJ) | 0a23398f | .693 | +.036 | −.197 | −.193 | +.042 | +.034 [−.070, +.128] |

- Not out of tune, best discovery gain < .03: 223acaee, a8f4ea11, e79e72df, 35c721fd, 9e72f9b6, d3c0d182, 8743da7f.
- Discovery gains that failed confirmation: feadc823 (+.083 → −.010) and 544f3d24 (+.064 → −.031).
- Totals over 30 champions (16 comm, 14 HOLD):
  - discovery gain ≥ .03: 9;
  - confirmed point estimate ≥ .03: 7;
  - confirmed with lower 99% bound > 0: 4;
  - winner's curse: mean discovery gain .066 against mean confirmation .037.
- HOLD (12 D/E champions plus 2 adjudicated): the largest |gain| on any lat variant is .0065. HOLD champions are timing-free local latches.
- All 4 credible cases (and 6/9 by point estimate) are in the RELAY cell family ring, d = 3, sync period 2, lat 1/1/1, delta 8, env period 11. This is the cell of 62a7fff9, 31cd2a8a and c16d5231.
- **Mechanism [V for the sign pattern, I for the reading]:** lat+1 (arrival one tick later) and delta−1 (readout one tick earlier) both shorten the arrival-to-readout gap by one tick.
  - They agree in sign in 5/6 mis-tuned rows. e9196cae is the mirror case: its gap is too short, and delta+1 helps.
  - That points to a genuine one-tick gap error rather than noise. W2-E N4 generalises: this is not unique to 62a7fff9, and 62a7fff9 reproduces at +.060.
  - Parity is not excluded. delta±1 also makes the env period even under sync period 2.

**Check:** `python tune_tab.py` (out/tune_part1.json, out/tune_part2.json).

**Objection:** lat_base and delta are physics or task changes, not genome changes. They measure how far the mechanism's timing sits from the cell's timing, not a gain that a mutation is known to reach.

**Coverage gap:** the top-20 SIGNAL evolve champions and 2 MAJ D-replicates (18c218f5, 1a86071f) were NOT swept because the compute cap was reached. The champion list is in tune.py from index 30.

### F5 [I] The selector ceiling does not explain the mis-tuning. Reachability, or simply the 36-generation stop, probably does.

- W2-D F7's ~.57 is a ceiling in the chance band: the noise of the best of 96 genomes evaluated unpaired.
- In the GA, all genomes in a generation share the same 8 worlds, so parent-vs-neighbour comparisons are paired. From the confirmation CIs, the paired standard error at 4 pairs (M = 8) is about .020 to .036. The confirmed gains (.060 to .091) are 2.5 to 4.3 SE at M = 8, so selection could see them. A .033 gain is about 1.3 SE and would only be seen intermittently.
- So for gaps of .06 or more, the persistence of mis-tuned champions argues for "no one-mutation retune exists" (a one-tick delay needs an extra S-register stage, which takes several fields) or for the search ending. It argues against selector blindness.
- Untested: whether a 1-2 field mutation reproduces the effect.

**Implications for reading C1 champions as mechanisms:**
- (a) Whether S0 passes through a threshold op says nothing about competence. Classify champions by the signal path (does signal reach the actuator?), not by readout op.
- (b) Neither the noise F4 bonus nor its absence explains the C1 NULL champions. Where the bonus distorts, it rewards one-sided codes, mostly in SIGNAL cells at noise 0.
- (c) Champion accuracy is a lower bound on the mechanism, by up to .09 in the sync-2 RELAY family.
  - Replicate differences within a cell (for example the 31cd2a8a replicates at held .667 vs .789) partly reflect timing luck.
  - Cross-cell comparisons of champion accuracy mix mechanism with tuning.
  - HOLD champions are exempt.

## 2. Proposed fixes
No code diff: nothing found is a bug in frozen semantics. Two NEUTRAL reporting recommendations for C2 design:
- (i) add a "timing neighbourhood" column (best paired gain over lat ±1 and delta ±1) to SIGNAL champion reports;
- (ii) report X = sens_act − max(0, 2·acc − 1) and CM next to the bonus, so one-sided-code payments are visible.

One SEMANTIC proposal for C2 only, not C1: score each twin's sign separately against y in the contrast bonus. This removes both the common-mode blindness (F4) and the one-sided payment (F3).

## 3. Disagreements
- **With the brief's prediction ("SIGNAL champions are THRESHOLDED"):** refuted (F2). The scorer applies the sign.
- **With W2-A1 F4's stated consequence ("under noise, selection favours linear, sub-noise codes"):** the mechanism is right, but I found no effect in C1 champions or populations (F1). It should be scoped as a potential bias, not an active one. The bonus distortion that did occur is the one-sided-code one (F3).
- **With applying W2-D F7's ~.57 ceiling to timing differences:** F7 concerns unpaired chance-band noise. Paired M = 8 comparisons resolve gains of .06 or more (F5, [I]).
- **With W2-E N4's framing of 62a7fff9 as a single anomaly:** it belongs to a family-wide pattern. The mis-tune direction differs across replicates (e9196cae needs a longer gap).
- **With the brief's task list:** top-20 SIGNAL not swept (cap). I also chose comm-family SIGNAL champions instead of the absolute top 20, which would be all HOLD at 1.0, and HOLD is timing-inert by F4.

## 4. Next questions (ranked)
1. For the 4 credibly mis-tuned champions, does any 1-2 field mutation (or 256 `search.mutate()` offspring) reach a paired gain ≥ .03? This separates "unreachable" from "search ended". Cost: about 4 × 256 × 8 worlds, CPU, roughly 0.3 core-hours.
2. Sweep the top-20 comm SIGNAL champions plus 18c218f5 and 1a86071f (deferred). Prediction: mis-tuning concentrates in sync-period-2 cells with an odd env period.
3. Gap vs parity: split native per-trial accuracy by trial-onset parity for f7e62fe3, 4316f167 and e9196cae. Prediction: if it is a gap error, the loss is spread over both parities; if it is parity, the loss is concentrated on one.
4. Bonus-free rerun (w_contrast = 0) on 2-3 noise-0 RELAY cells whose SIGNAL champions are one-sided. Does champion one-sidedness (frac0, CM = 1) fall, and does held accuracy change?
5. The 3 MAJ noise-64 NULL runs where the population reached max_contrast ≥ .5 at max_acc < .6. They are the only candidate F4 cases. Re-evolve one (bounded) and inspect the high-contrast genomes.
6. Extend the static classifier to WIMM/Kp and SETRULE, and re-check the 21% of champions that are MIXED or NOINPUT.
7. Is RELAY's low SIGNAL rate at noise > 0 a targeting artefact? Wave A gives 2/22, 1/25 and 1/24 by noise, so there is no noise effect; B and B2 targeted noise 0.

## 5. Inference ledger
question | evidence | result | confidence | strongest objection | unresolved | next
- F4 bonus shapes NULL champions? | static_tab.py (678), dyn.py (91), curve_tab.py | no: OR 1.54 p=.17; no NULL champion with sens_act ≥ .5; population max_contrast ≥ .5 at chance in 0-5% of noise-64 NULL runs | high | the final population is not stored | MAJ 3 runs | Q5, Q4
- SIGNAL champions thresholded? | static weights; dynamic distinct/top-3/CM; envs.score | no: SIG more linear (OR .35, p=.004); the scorer applies sign | high | static blind spots (WIMM/SETRULE) | MIXED rules | Q6
- where the bonus excess comes from | X, CM, frac0 over 91 | one-sided codes (CM=1, frac0 ~.7), mostly noise-0 SIGNAL | high | n=8 per stratum | effect on search | Q4
- timing slack | tune.py, 30 champions, discovery + confirmation | 4/16 comm credible ≥ .03 (7 by point estimate), all in the sync-2 delta-8 RELAY family; HOLD 0 | med-high | physics/env change is not a genome change | top-20 not swept | Q1, Q2
- gap vs parity | sign agreement of lat+1 and delta−1 | 5/6 consistent with a one-tick gap | medium | delta also flips period parity | parity split | Q3
- selector ceiling vs tuning | paired SE from confirmation CIs | gains ≥ .06 are 2.5-4 SE at M=8 paired | medium [I] | truncation dynamics not modelled | reachability | Q1

## 6. Compute used
Process CPU time (time.process_time, summed over threads):

| item | core-seconds |
|---|---|
| bench | 15 |
| scaling probe | ~55 |
| static analysis | ~10 |
| dyn.py | 415 |
| tune part 1 | 921 (process ended with exit code 1 and no traceback after champion 23; output saved) |
| tune part 2 | 293 (budget stop) |
| analysis | ~15 |
| **total** | **~1,725 (about 0.48 core-hours, under the 0.5 cap)** |

- CPU only, 2 threads, eager. No GPU, no leases, no background processes left running.
