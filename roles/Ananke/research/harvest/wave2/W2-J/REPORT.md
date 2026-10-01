<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-J; sha256(report)=c7d88bc5994e36d9; delimited; see REPORT.provenance.json -->
W2-J REPORT: XOR search vs physics across C1 (Ananke Wave-2, worker W2-J, Opus)
Directory: roles/Ananke/research/harvest/wave2/W2-J/ (all scripts; outputs in out/*.json; the full per-row table with complete physics is out/table.md)
Main scripts: wj_common.py, gate.py, lc2.py, check_lc2.py, lc_robust.py, plants_wj.py, known.py, known2.py, screen*.py, score.py, dev_cheat.py, pivot.py, econ_bound.py, classify.py
Run conditions: CPU only, CUDA_VISIBLE_DEVICES=-1 (hp_common asserts torch.cuda.is_available() is False), 2 threads (asserted), eager hc.evaluate. No search of any kind was run (no evolutionary or other).
Namespaces: design worlds W2JD (0x57324A44); scoring worlds W2JS (0x57324A53, +1 for pivotality, +7/+9 for bounds). Both are disjoint from C1, C1b, H-PLANT and W2-B.

## 0. Headline

**Totals over the 83 XOR evolve rows:**

| class | rows | meaning |
|---|---|---|
| PLANT-SOLVED | 6 | a hand-written plant reaches lo99 > .60 on 64 fresh worlds |
| CAPPED-LC1 | 36 | the given H-PLANT light-cone set |
| CAPPED-LC2 | 26 | capped by the new reach bound; 23 robust plus 3 point-only (99% CI straddles .60) |
| UNDECIDED | 15 | 8 where physics permits but my plants failed; 7 economy-throttled |

- Of the 47 rows not capped by the light cone: 6 are solved, 26 are capped by LC2 and 15 are undecided.
- Strict tier (the row's own genome fields, no override): 0 rows are solved.
- C1-genome-space tier (16 lines; only genome fields raised, e.g. prog_len 8 or 12 to 16, channels 1 to 2): 4 rows are solved.
- The one-flag (NOR) cheat passes C1's SIGNAL rule (lo99 > .55) on 5 of the 47 uncapped rows. Those are 5 of the 6 rows where a genuine parity plant passes. No other row could let a one-flag readout pass unless its reach bound is ≥ .60, which is 21 rows at most.

## 1. Findings

### F1 [V] Known-answer gate: PASS
- H-PLANT P-XOR at X0 on 64 W2JS worlds (32 pairs): 1.000 [1.000, 1.000]. Must-fail with sensor 2 zeroed: .500.
- Check: `python gate.py` (out/gate.json).
- My plant families also reach 1.000 at X0-like lossless physics:
  - CLK at update_period 1 and 2 with decay 0/1/6;
  - parity-channel CLK, including jitter 3 and dup .1;
  - TTL under sync.
- Under async .8 at X0 (decay 3/6/1), TTL reaches .93 against an LC2 bound of .97 (`known.py`, `known2.py`, `diag_async.py`).
- Confidence: high.

### F2 [V] A stronger reach bound (LC2) caps 26 of the 47 "uncapped" rows below .60
- LC2 = H-PLANT's light cone plus five things it leaves out:
  - finite fanout (dest sample: F uniform draws; global: F random sites, not all-to-all);
  - per-copy loss (per hop where loss_per_hop is set);
  - asynchronous wake, including the SENSORS: a cue is seen only if the sensor is awake during the 2-tick cue window, because SENSE does not accumulate (engine step 2);
  - dup copies;
  - latency jitter sampled per copy.
- It stays optimistic everywhere else:
  - every informed site emits at every awake tick, and one packet carries both bits;
  - no caps, collisions, noise, economy or decay;
  - for plastic-routing rows, dest sample is also bounded as dest all, and the larger value is used.
- Validity check: in the deterministic limit (loss 0, dup 0, dest all, sync), LC2 equals lightcone.earliest on 768 of 768 trials. Must-fail: with latency 40, f = 0 (`check_lc2.py`).
- Plant vs bound: no scored plant exceeds LC2 beyond world-sampling noise. For example:
  - e7d6ccb0: plant .635 on DEV, bound .628 on the same worlds;
  - 84cf905d: plant .871, LC2 .857 [.767, .937].
- Main mechanisms:
  - 14 global-topology rows with fanout 1-2: H-PLANT's light cone gives 1.0, LC2 gives about .50;
  - async wake (p = .5 means both sensors see their cue in only about 56% of trials);
  - jitter. For example ab3e72d3 drops from .857 at minimum latency to .592 with jitter (`lc2_min.json` vs `lc2.json`).
- Robust run on 64 fresh worlds with a 99% world-bootstrap CI: `lc_robust.py`.
- Confidence: high for the 23 robust rows. For d2b8816c, ab3e72d3 and 74a24d53 the CI straddles .60.
- Strongest objection: it is an expectation bound under the engine's distributions, not per realisation. Per-pair plant scores can exceed it by chance.
- Unresolved: R = 4 MC replicates; the bound for rows near .60 needs more samples.

### F3 [V] Six rows are PLANT-SOLVED on 64 fresh worlds; must-fail = .500 at every one

| row | plant | lines | acc [lo99] | 16-line C1-space plant | LC2 | C1 held lo99 |
|---|---|---|---|---|---|---|
| 84cf905d | clk4 persist | 37 | .871 [.776] | none (needs a k=1 clock) | .857 | .490 |
| 48256f59 | ttl2 persist | 27 | .824 [.802] | .775 [.751] | | .500 |
| 1974a9cf | ttl2 persist | 27 | .798 [.772] | .749 [.717] | | .465 |
| 333d6b2b | ttl2 persist | 27 | .798 [.772] | .695 [.670] | | .467 |
| 4222a5f7 | clk4 once | 39 | .790 [.729] | .670 [.633] | | .474 |
| e2fd1e07 | ttl2 once | 22 | .643 [.607] | .604 [.568], not > .60 | | .485 |

- All constants are representable in C1's genome space (imm in [-128, 127], CONST shift ≤ 7; checked).
- Overrides at the 16-line tier:
  - prog_len 8 to 16 and channels 1 to 2 for 48256f59, 1974a9cf and 333d6b2b;
  - prog_len 12 to 16 for 4222a5f7.
- No plant fits a row's own sampled genome. So "search-limited at the sampled genome" is shown for NO XOR row. These 6 are search- OR representation-limited.
- Confidence: high (fresh disjoint worlds; variant chosen on separate DEV worlds).
- Strongest objection: the plants are tuned per row (windows taken from δ, Pd and decay) and use designer knowledge of the physics.
- Unresolved: whether an 8- or 12-line plant exists at the rows' sampled genome.

### F4 [V] Why P-XOR fails at C1 physics, and what fixes each failure
Each item was found with knock-out diagnostics (`diag_knock.py`, `screen*.py`).
- **update_period 2:** advance the clock by p per awake tick and test the onset as "phase < p". A single line `GT S=S>onset` both resets the flag at onset and renormalises it after decay.
- **decay_shift:**
  - store the clock pre-compensated: k=1 store u·2^p; k=3 store u + floor(37u/256); k=6 needs nothing below 64. All three are exact (verified);
  - or use exogenous decay itself as a timer (TTL). This works under async because decay runs on every tick, awake or asleep.
- **noise and saturate dilution:** payloads scaled to 16256 with threshold 2032, or packet counts per channel (noise never touches counts).
- **jitter and dup:** late packets leak into the next trial; this alone cut ab3e72d3 from .615 to .484. Carrying the trial parity as the packet's CHANNEL and reading only the current parity's channel (clk4) removes the leak.
- **sparse fanout:** single-shot flooding gives too few target draws. Persistent emission inside a phase window (phase ≤ δ − lat_min) is needed (84cf905d: .656 → .911 on DEV).
- **aloha caps:** persistent emission collides (4222a5f7 persist .57 vs once .72 on DEV). Gossip did not rescue any row.
- **async without a clock:** per-site timers cannot stop late learners from holding stale flags into the next trial. This is the residual failure on cd613e2b (lat 4: .54 vs .81 at lat 1, all else equal), 7a16eddd, f8f95cc4 and 2a226bec.
- Confidence: high for each mechanism (each knocked out individually), medium that no simple fix exists for the async residual.

### F5 [V] One-flag (NOR) cheat at C1's real physics
Cheat = same flood, readout "+ iff no + flag", 64 fresh worlds.
- Passes the SIGNAL rule (lo99 > .55) at five rows:

| row | NOR acc [lo99] |
|---|---|
| 84cf905d | .677 [.632] |
| 4222a5f7 | .656 [.598] |
| 333d6b2b | .608 [.568] |
| 48256f59 | .605 [.576] |
| 1974a9cf | .605 [.565] |

- Fails at e2fd1e07 (.546 [.514]) and e7d6ccb0 (.552 [.522]), and on DEV at the 6 undecided rows (≤ .54).
- Analytic: a one-flag readout's accuracy is ≤ .5 + .25·f (W2-B's .75 ceiling times reach). It can pass only where LC2 ≥ .60, which is 21 rows at most.
- So wherever XOR SIGNAL is physically attainable at C1, 5 of 6 rows also admit a non-XOR SIGNAL pass. The XOR SIGNAL ruler is cheatable at nearly all of C1's XOR-feasible physics.
- H-PLANT points (16 worlds):
  - aa2b8d68 strict: P-XOR .667, NOR .630 (lo .562);
  - 4eeca9f1 at_c1: P-XOR .802, NOR .661 (lo .604).
- Confidence: high.

### F6 [V] XOR_PIVOT (W2-B, min_j p_j > .6) has no false positives but false negatives at C1 physics
Measured with W2-B's own per_sensor_pivotality (imported read-only), M = 16 worlds, trials (2, 5, 8).
- **Genuine parity plants that fail XOR_PIVOT:**

| row | min p_j | plant acc |
|---|---|---|
| aa2b8d68 | .479 | .667 |
| 1974a9cf | .458 | .797 |
| 333d6b2b | .458 | .786 |

- **Genuine parity plants that pass:** 48256f59 (.646), 84cf905d (.667), 4222a5f7 (.667), 4eeca9f1 (.708).
- **All six NOR cheats fail:** min p from .271 to .479. Note that 4222a5f7 NOR has p_0 = .667 on one sensor.
- **Mechanism [I]:** under partial reach, a parity readout has p_j ≈ P(both reached) ≈ 2·acc − 1, so XOR_PIVOT certifies parity only above about acc .8. Its threshold depends on reach and latency.
- **Separator that worked in all 9 measured programs:** split p_j by the OTHER sensor's cue sign.
  - Parity is symmetric: 4222a5f7 (.67/.67, .67/.67); 48256f59 (.61/.67, .58/.71); 1974a9cf (.50/.53, .46/.46).
  - NOR is asymmetric: p_j(other +) = .06-.28 vs p_j(other −) = .42-.93.
  - aa2b8d68 P-XOR sensor 0 is .33/.57, which is ambiguous at about 24 samples per cell.
- Confidence: high that the false negatives are real and the mechanism is understood; medium for the conditional ruler (small M; no power analysis).

### F7 [V] The 36 light-cone caps carry world-sampling error
- Recomputed on 64 fresh worlds, several capped rows have fresh lc1 ≥ .60: 312b5cf6 .625, d43ef071 .656, fafa4580 .625, 797c8957 .648, c83ce615 .625. The 99% CIs are about ±.1 where actuator placement dominates.
- All except 312b5cf6 stay below .60 under LC2.
- 312b5cf6 (LC2 .602 [.524, .697]) is not robustly capped. I left it in CAPPED-LC1 per the brief and flag it here.
- Confidence: high.

### F8 [V] Economy rows: conditional caps
- Rows with c_op = 1: E starts at e_max = 100, income is 4 per tick, every awake non-NOP line costs 1, and an emission needs E ≥ c_emit·copies.
- Once E is pinned at 0 it never recovers if p_awake·k > 4.
- Result: any program with ≥ k* non-NOP lines is capped below .60. k* = 5 for 4ca24b85, b3549a65, 33505249 and d01883ed; 6 for 247e0d43; 8 for 89a6a9cd; 13 for 93b9eeeb (`econ_bound.py`; c_mem ignored, which is optimistic).
- My plants emit nothing at these rows (emitters/awake = .000).
- They stay UNDECIDED-ECONOMY unless no XOR program with ≤ k*−1 lines exists.
- Confidence: high for the conditional statement.

### F9 [I] What the rows mean for H6
- C-wave rows 48256f59, 1974a9cf, 333d6b2b and 4222a5f7 searched at prog_len 8 or 12 with channels 1. My smallest working plant needs 16 lines plus 2 channels (or 16 lines with C4).
- The C1 NULL there is therefore at least as consistent with genome-space sampling (representation) as with search failure.
- Confidence: medium.

## 2. Per-row table (all 83 rows)

Column key:
- Physics: topology+N; dest/fanout; update; L = loss; c = cap+collision; k = decay; n = noise; l = lat base+hop~jitter; G = prog_len/state_dim/payload/channels; "eco" = c_op > 0.
- lc1 cen/fresh = H-PLANT census / 64 fresh worlds.
- lc2 = 64 fresh worlds [99% world CI].
- plant = best scored on 64 fresh worlds (tier, family, length) or DEV16 best; C1sp = 16-line plant; NOR = cheat.

```
cell     | class            | physics key                                          | held lo99 | lc1 cen/fresh | lc2 [99%]           | plant                       | C1sp          | NOR
4222a5f7 | PLANT-SOLVED     | glob64 samf4 sync1 L.1 c4al k3 n0 l1+0~3 G12/8/1/4 d1 dl16  | .474 | 1.00/1.00 | 1.000 [1.00,1.00] | ext clk4 L39 .790 [.729] | .670 [.633] | .656 [.598]
333d6b2b | PLANT-SOLVED     | glob100 samf8 async.8 L.1 c1sa k3 n64 l2+0~1 G8/4/2/1 d5 dl16 | .467 | 1.00/1.00 | .968 [.958,.977] | ext ttl2 L27 .798 [.772] | .695 [.670] | .608 [.568]
48256f59 | PLANT-SOLVED     | glob100 samf8 async.8 L.1 c1no k3 n64 l1+0~1 G8/4/2/1 d5 dl16 | .500 | 1.00/1.00 | .959 [.950,.967] | ext ttl2 L27 .824 [.802] | .775 [.751] | .605 [.576]
1974a9cf | PLANT-SOLVED     | glob100 samf8 async.8 L.1 c1no k3 n64 l2+0~1 G8/4/2/1 d5 dl16 | .465 | 1.00/1.00 | .958 [.949,.967] | ext ttl2 L27 .798 [.772] | .749 [.717] | .605 [.565]
84cf905d | PLANT-SOLVED     | rand64 allf8 sync1 L0 c0 k1 n0 l2+1~1 G16/8/1/1 d5 dl16      | .490 | .969/.938 | .857 [.767,.937] | ext clk4 L37 .871 [.776] | -           | .677 [.632]
e2fd1e07 | PLANT-SOLVED     | glob64 samf4 async.5 L0 c2no k3 n64 l1+0~1 G8/1/1/2 d1 dl16  | .485 | 1.00/1.00 | .780 [.761,.801] | ext ttl2 L22 .643 [.607] | .604 [.568] | .546 [.514]
cd613e2b | UNDECIDED        | glob100 samf8 async.8 L.1 c1no k3 n64 l4+0~1 G8/4/2/1 d5 dl16 | .486 | 1.00/1.00 | .962 [.955,.968] | DEV16 ttl2 .54 | - | DEV .52
7a16eddd | UNDECIDED        | tor100 samf8 async.8 L0 c2sa k1 n0 l1+0~3 G8/1/2/1 d5 dl8     | .484 | 1.00/1.00 | .956 [.948,.963] | DEV16 ttl2 .55 | - | DEV .52
f8f95cc4 | UNDECIDED        | tor144 allf1 async.8 L0 c0 k0 n16 l2+0~0 G16/8/1/2 d2 dl8     | .505 | 1.00/1.00 | .946 [.922,.965] | DEV16 ttl2 .58 | - | DEV .54
2a226bec | UNDECIDED        | rand100 samf4 async.8 L.6 c2sa k6 n0 l1+1~1 G16/1/2/4 d2 dl16 | .500 | 1.00/1.00 | .837 [.790,.878] | DEV16 ttl2 .52 | - | DEV .49
e7d6ccb0 | UNDECIDED        | tor144 samf4 sync1 L.1 c4sa k0 n0 l1+0~0 G16/4/2/1 d3 dl4     | .436 | .797/.828 | .828 [.719,.938]* | ext clk4 L35 .576 [.533] | - | .552 [.522]
17dd70fa | UNDECIDED        | tor144 allf8 sync2 L0 c1al k1 n16 l2+1~0 G16/8/2/1 d3 dl16    | .480 | .719/.766 | .766 [.664,.859] | DEV16 clk4 .59 | - | DEV .53
51fa3ee0 | UNDECIDED        | ring144 allf1 sync2 L0 c0 k1 n64 l1+0~3 G8/8/4/1 d2 dl16     | .467 | .617/.641 | .631 [.544,.729] | DEV16 clk4 .56 | - | DEV .52
141c4310 | UNDECIDED        | sw100 samf8 sync2 L.6 c2al k1 n64 l4+0~0 G12/4/2/4 d2 dl16   | .467 | .688/.719 | .628 [.551,.714] | DEV16 clk4 .50 | - | -
93b9eeeb | UNDECIDED-ECON   | glob100 samf4 sync2 L.3 c0 k6 n64 l1+1~0 G8/4/2/1 eco d5 dl16 | .490 | 1.00/1.00 | 1.000 | DEV16 .53 (no emission) k*=13
89a6a9cd | UNDECIDED-ECON   | glob64 samf1 async.8 L0 c4no k3 n16 l2+1~0 G16/8/1/1 eco d5   | .500 | 1.00/1.00 | .818 | DEV16 .50 k*=8
d01883ed | UNDECIDED-ECON   | tor64 allf1 sync1 L0 c1sa k1 n64 l2+1~0 G12/2/4/1 eco d2 dl8  | .493 | .766/.766 | .766 | DEV16 .51 k*=5
33505249 | UNDECIDED-ECON   | sw64 samf2 sync1 L.3 c2sa k3 n0 l2+1~3 G16/8/1/2 eco d3 dl16 | .500 | .984/.984 | .725 | DEV16 .50 k*=5
b3549a65 | UNDECIDED-ECON   | sw100 allf2 sync1 L.6 c4sa k1 n0 l1+1~3 G12/4/1/1 eco d3 dl16| .500 | 1.00/1.00 | .723 | DEV16 .50 k*=5
247e0d43 | UNDECIDED-ECON   | sw144 allf4 async.8 L.1 c1al k1 n16 l2+1~0 G16/1/2/1 eco d2  | .495 | .672/.734 | .667 | - k*=6
4ca24b85 | UNDECIDED-ECON   | tor64 allf8 sync1 L.1 c1no k0 n64 l4+0~1 G8/1/1/1 eco d1 dl8  | .500 | .750/.750 | .614 | DEV16 .50 k*=5
d2b8816c | CAPPED-LC2(pt)   | sw144 allf4 async.5 L.1 k6 n16 l2+0~3 G12/4/1/4 d2 dl16      | .471 | 1.00/1.00 | .595 [.555,.638] | DEV16 ttl1 .53
ab3e72d3 | CAPPED-LC2(pt)   | glob64 samf4 sync1 L0 c1sa k0 n0 l2+1~3 G12/8/1/2 d2 dl8     | .480 | 1.00/1.00 | .592 [.583,.602] | DEV16 clk4 .55
74a24d53 | CAPPED-LC2(pt)   | sw144 samf4 async.5 L.6 k3 n64 l1+1~1 G8/2/1/4 d1 dl16       | .500 | 1.00/1.00 | .561 [.529,.603]
CAPPED-LC2 (lc2 99% upper < .60), cell: lc1 census -> lc2
  11252d52 1.00->.540  c878030f 1.00->.538  4c562c03 .711->.524  a282df19 .820->.522  4e7f932f .922->.521
  02dc972a 1.00->.517  e3fb8737 1.00->.510  74f96e89 .734->.507  e1fc5118 .672->.507  73d733c5 .766->.503
  efc6f7c3 .992->.503  06e19421 .938->.503  abb5fb81 .625->.502  2ccc1a35 1.00->.502  2b867f4f 1.00->.502
  0e99a4bb 1.00->.501  aee70c90 1.00->.501  1916d8e9 1.00->.501  f6c66aaf 1.00->.501  a0edfda5 1.00->.501
  667bb9bd 1.00->.500  cc5f5406 1.00->.500  cd1b61b5 .641->.500
CAPPED-LC1 (given 36), cell: lc1 census / lc1 fresh / lc2 fresh
  312b5cf6 .547/.625/.602[.524,.697]!  d43ef071 .562/.656/.597  fafa4580 .547/.625/.580  87494b3d .531/.594/.576
  975fa549 .516/.547/.547  d64656f2 .531/.555/.540  797c8957 .594/.648/.534  69442376 .531/.531/.528
  7f951945 .531/.547/.520  bc67e194 .500/.531/.511  062b2018, ea36d7b2, 498084da, c83ce615(.547/.625/.503),
  b18077fc, f64aafde, 9c941931, 75c93498, 384b5b8f, d7cd4a5c, 54b1bdf9, 55d449de, 2c62d07a, 58f40dae,
  c91daf4a, db5d60c7, 78725ff5, 5ff7ddf8, 75779d26, d519f4f9, 9ace5d45, 73ec2754, 4b2ca083, 30a22556,
  c7285789, 14e33fce (all lc2 <= .505)
```

Table notes:
- `*` For e7d6ccb0, LC2 uses the dest-all bound because the row has plastic routing; with uniform sampling it is about .58.
- `!` 312b5cf6 is not robustly capped on fresh worlds (F7).

## 3. Revised XOR H6 statement

"Across C1's 83 XOR evolve rows, physics alone (an optimistic reach bound that ignores caps, collisions, noise and economy) holds ANY program below .60 at ≥ 62 rows (75%):
- 36 by light cone and actuator placement;
- 26 more by finite fanout, per-copy loss, asynchronous wake including sensor wake, and latency jitter.

At those rows H6 ('XOR NULL = search') is FALSE.

At 6 rows (7%) hand-written plants reach lo99 .607-.802 on fresh worlds (accuracy .643-.871), so physics allows XOR there:
- at 4 of them a 16-line plant inside C1's genome space suffices (.670-.775);
- none fits the row's own sampled genome (prog_len 8/12, channels 1).

So those NULLs are search- OR representation-limited, and 'search-limited at the sampled genome' is not demonstrated for any XOR row.

15 rows (18%) are undecided:
- 8 are physics-permissive but my plants fail (mostly async: per-site timers cannot expire late learners on time);
- 7 are economy-throttled: any program with ≥ 5-13 non-NOP lines is capped.

Separately, C1's XOR SIGNAL rule is cheatable by a one-flag readout at 5 of the 6 XOR-feasible rows. Any future XOR claim needs a parity control that does not depend on reach (F6)."

## 4. Decompiled plants
S = state, T = temporaries, CONST = imm << shift.

**(a) TTL1: 16 lines, C1 genome space.** Flag type = channel, evidence = packet count (counts are immune to noise). Each flag's timer starts at 256 and decays exogenously; the thresholds below are for decay_shift 3 with δ16: relearn iff timer < 28, i.e. age ≥ 18; fresh iff timer > 27, i.e. age ≤ 17.
```
 0 MAX T0=MAX(SENSE,CNT0)  1 GT T0=T0>ZERO        2 GT T1=CNT1>SENSE      3 CONST T2=28<<0
 4 GT T3=T2>S1             5 MULQ T3=T3*T0 (relearn P)                     6 GT PAY0=T2>S2
 7 MULQ PAY0=PAY0*T1 (relearn Q)  8 ADD EMIT=T3+PAY0  9 SHR CHAN=PAY0>>8 (Q->ch1)
10 MAX S1=MAX(S1,T3)       11 MAX S2=MAX(S2,PAY0) 12 CONST T2=27<<0
13 SUB S0=S1-T2            14 SUB T0=T2-S2        15 SEL S0=(S0>0)?T0:T2   (- iff both fresh)
```

**(b) TTL2 persist: 27 lines (48256f59, 1974a9cf, 333d6b2b).** Payloads are scaled to 16256 with a threshold of 2032. Timers start at 16256 and decay exogenously. The site emits while a flag is younger than 4 ticks.
```
 0 CONST T3=127<<7   1 MULQ T0=SENSE*T3   2 SUB T1=ZERO-T0   3 MAX T0=T0,IN0_0   4 MAX T1=T1,IN0_1
 5 SHR T2=T3>>3      6 GT T0=T0>T2        7 GT T1=T1>T2      8 CONST T2=93<<4 (relearn thr)
 9 GT PAY0=T2>S1    10 MULQ PAY0*=T0     11 GT PAY1=T2>S2   12 MULQ PAY1*=T1   13 MULQ PAY0*=T3
14 MULQ PAY1*=T3    15 MAX S1=S1,PAY0    16 MAX S2=S2,PAY1  17 CONST T2=66<<7 (young thr)
18 GT PAY0=S1>T2    19 GT PAY1=S2>T2     20 ADD EMIT=PAY0+PAY1  21 MULQ PAY0*=T3  22 MULQ PAY1*=T3
23 CONST T2=92<<4 (fresh thr)  24 SUB S0=S1-T2  25 SUB T0=T2-S2  26 SEL S0=(S0>0)?T0:T2
```
TTL2 once (e2fd1e07, 22 lines) is the same through line 12, then `ADD EMIT=PAY0+PAY1`, scale, MAX, and the readout.

**(c) CLK4 once: 39 lines (4222a5f7; sync, decay 3).** The clock runs mod 2·Pd and is decay-compensated. The trial parity goes in S4 and in CHAN, and the site reads only the current parity's channel.
```
 0 CONST T3=37   1 ADDI T1=S3+1   2 MOD T1=T1 mod(T3+1)   3 CONST T3=37   4 MULQ T0=T1*T3   5 ADD T1=T1+T0
 6 CONST T3=18   7 MOD T2=S3 mod 19   8 GT S4=S3>T3 (parity)   9 MOV S3=T1   10 ADDI T2=T2-1
11 CONST EMIT=15 12 GT EMIT=EMIT>T2 (window)  13 GT T3=ZERO>T2 (onset)  14 GT S1=S1>T3  15 GT S2=S2>T3
16 MOV T0=S4  17 SEL T0=(T0>0)?IN1_0:IN0_0  18 MOV T1=S4  19 SEL T1=(T1>0)?IN1_1:IN0_1
20 CONST T3=127<<7  21 MULQ T2=SENSE*T3  22 MAX T0=T0,T2  23 SUB T2=ZERO-T2  24 MAX T1=T1,T2
25 SHR T2=T3>>3  26 GT T0=T0>T2  27 GT T1=T1>T2  28 SHR CHAN=S4>>8  29 GT PAY0=T0>S1  30 GT PAY1=T1>S2
31 ADD T2=PAY0+PAY1  32 MULQ EMIT=EMIT*T2  33 MAX S1=S1,T0  34 MAX S2=S2,T1  35 MULQ PAY0*=T3
36 MULQ PAY1*=T3  37 XOR T0=S1^S2  38 ADDI S0=T0-128
```
CLK4 persist (84cf905d, decay 1, 37 lines) differs in two places:
- the compensation is `ADD T1=T1+T1` instead of lines 3-5;
- the emission is `MAX T2=S1,S2; MULQ EMIT=EMIT*T2; MOV PAY0=S1; MOV PAY1=S2` (the program text is in out/score_A.json).

The NOR cheat replaces the readout with `SUB S0=ZERO-S1; ADDI S0=S0+128` (CLK) or `SUB S0=T2-S1` (TTL).

## 5. Proposed fixes and instruments (no frozen code touched)
- **NEUTRAL, new instrument:** `lc2.py`, a reach bound with wake, loss, fanout, dup and jitter. Its regression test is `check_lc2.py`: equality with lightcone.earliest in the deterministic limit (768/768) plus a must-fail (latency 40 gives f = 0). I propose it replace H-PLANT lc1 for H6 accounting.
- **NEUTRAL, new ruler (proposal):** XOR_SYM. Conditional pivotality p_j(other = ±), with the requirement min_{j,s} p_j(s) > .5·max_{j,s} p_j(s) plus SIGNAL. Computed in `pivot.py` (it reuses W2-B's per_sensor_pivotality). It needs a power analysis before promotion.
- **Documentation:** the H-PLANT census of 36 should be reissued with world CIs (F7).

## 6. Disagreements
1. **H-PLANT REPORT s2 and principal review** ("at C1's other XOR evolve points this test decides nothing"): now decided for 68 of 83 rows (62 capped, 6 solved).
2. **H-PLANT lightcone.py as an H6 bound:**
   - For global topology it lets one hop reach every site regardless of fanout, so it gives 1.0 at 20 global rows, of which LC2 caps most at about .50;
   - async is treated as always awake, including the sensors.
   - 26 of its 47 "uncapped" rows are capped by LC2.
3. **"36 capped" as an exact count:** it is a 64-world sample. On fresh worlds 312b5cf6 is not robustly capped (F7).
4. **W2-B's XOR_PIVOT threshold .6:** 3 of 7 genuine-parity measurements at C1 physics fail it. Parity pivotality scales with reach (F6). W2-B's .75 non-parity ceiling is consistent with my data (cheats max .677).
5. **Reading the solved rows as "search-limited":** at the 6 PLANT-SOLVED rows the plants needed larger genome dimensions than the row sampled, so the evidence supports representation-or-search, not search.
6. **H-PLANT "P-XOR needs update_period 1":** not a limit of the approach. A period-p clock reaches 1.000 at X0 with period 2.

## 7. Next questions (ranked)
1. Is there an XOR plant within each solved row's own genome (L8/C1 for 48256f59, 1974a9cf, 333d6b2b, e2fd1e07; L12 for 4222a5f7; L16/C1 for 84cf905d)? An exhaustive or SAT enumeration of short programs (no evolution) would settle representation vs search.
2. Async undecided rows (cd613e2b .962, 7a16eddd .956, f8f95cc4 .946, 2a226bec .837): does a hop-class or age-stamp plant (channel = hop count, timer start set by hop class) fix late-learner contamination? Or is there a tighter async bound?
3. XOR_SYM: power and size at C1 physics. How many trials separate parity from all 14 non-parity readouts under partial reach?
4. Economy rows: does any XOR program exist with ≤ k*−1 (4-12) non-NOP lines? If not, reclassify the 7 rows as CAPPED-BY-ECONOMY.
5. Apply LC2 to FLIP, RELAY and MAJ evolve rows: how much of H6's other evidence is capped by fanout, async or jitter?
6. Firm up the rows near .60 (312b5cf6, d43ef071, 51fa3ee0, 141c4310, 4ca24b85, d2b8816c, ab3e72d3, 74a24d53) with LC2 at R = 16 and 256 worlds.
7. e7d6ccb0 (plastic routing, dest-all bound .83) and 17dd70fa (aloha cap1): can a routing-learning or collision-avoiding plant reach .60?

## 8. Inference ledger
```
Q: gate P-XOR X0 | gate.py | 1.000, mf .500 | high | 64 worlds only | - | -
Q: is lc1 a tight H6 bound? | lc2.py + check_lc2 (768/768 equal in deterministic limit) | no: 26/47 uncapped rows capped by fanout/async/loss/jitter | high (23 robust) | expectation bound, MC R=4 | 3 point-only rows | NQ6
Q: are the 36 caps robust? | lc_robust.py fresh 64 worlds + bootstrap | 35 yes, 312b5cf6 borderline (.602 [.524,.697]) | high | brief fixes 36 | census CI | NQ6
Q: plant-solvable uncapped rows? | screen*.py DEV16 -> score.py 64 fresh + mf | 6 solved (.643-.871), 4 with 16-line C1-space plant, 0 strict | high | per-row tuned plants; override | sampled-genome plants | NQ1
Q: why P-XOR fails at C1 physics | diag_knock, known*.py, screens | period, decay, noise, jitter leak, sparse fanout, aloha, async staleness; each fixed but async | high/medium | async fix not found | async plant | NQ2
Q: one-flag cheat at C1 physics | score.py nor + analytic .5+.25f | passes SIGNAL at 5/47 (5/6 solved rows); <=21 possible | high | cheat uses my flood | undecided rows | NQ2
Q: XOR_PIVOT at C1 physics | pivot.py (W2-B ruler) M16 | no false positive (6 cheats), 3 false negatives (parity at acc<.8); conditional symmetry separates 9/9 | high/medium | M=16, 48 samples per sensor | power of XOR_SYM | NQ3
Q: economy rows | econ_bound.py | capped for programs >= k*=5-13 lines; plants emit 0 | high (conditional) | c_mem ignored | small-program existence | NQ4
Q: H6 for XOR | all above | FALSE >= 62/83; rep-or-search 6/83; open 15/83 | medium-high | bounds optimistic, plants tuned | sampled-genome plants | NQ1
```

## 9. Compute
- About 2,200 CPU core-seconds, roughly 0.61 core-hours of the 0.75 cap. Recorded cpu_s across out/*.json sum to 2,115 s, plus about 80 s of untimed checks.
- Breakdown:

| item | CPU s |
|---|---|
| screens | 860 |
| scoring | 325 |
| pivotality | 480 |
| reach bounds | 260 |
| known answers and diagnostics | about 180 |

- GPU: none (CUDA hidden and asserted; every World device="cpu").
- No evolutionary search. No leases touched. No git writes. Nothing written outside W2-J/.
