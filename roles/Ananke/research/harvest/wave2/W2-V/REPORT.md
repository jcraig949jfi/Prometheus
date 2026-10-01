<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-V; sha256(report)=9587e95a8a914562; delimited; see REPORT.provenance.json -->
W2-V REPORT: representation vs search for the six XOR rows W2-J called PLANT-SOLVED (Ananke Wave-2, worker W2-V, Opus)

Directory: roles/Ananke/research/harvest/wave2/W2-V/ (scripts; outputs in out/*.json; summary in out/verdicts.json).
Run conditions:
- CPU only (CUDA hidden; hp_common asserts it), 2 threads, eager engine.
- Every plant was evaluated at the row's UNMODIFIED physics and genome. asm() asserts len(lines) <= prog_len.
- Runs that changed genome fields are labelled OVERRIDE and are diagnostics only.
- No evolutionary search of any kind.
- World namespaces: design W2VD = 0x57325644, scoring W2VS = 0x57325653 (disjoint from C1, C1b, H-PLANT, W2-B and W2-J).

## 0. Verdicts

| row | sampled genome | verdict | key evidence |
|---|---|---|---|
| 4222a5f7 | L12 D8 P1 C4, rules 4 | SEARCH-LIMITED (by construction) | 12/12-line plant: fresh .850 [lo99 .819]; C1's own held-out worlds .832 [.798] against the C1 champion's .503 [.474]; must-fail .500 |
| 48256f59 | L8 D4 P2 C1 | REPRESENTATION-LIMITED for parity (strongly argued, not proven) | line accounting has zero slack; scale lemma; exhaustive readout enumeration finds 0; the 8-line program scores .504 [.500] |
| 1974a9cf | same | same | same |
| 333d6b2b | same, cap1 saturate | same | same |
| e2fd1e07 | L8 D1 P1 C2, rules 4, SETRULE, WIMM | UNRESOLVED (leans representation) | the best family tops out at .573 on DEV even with an override |
| 84cf905d | L16 D8 P1 C1, 4 fixed rules, WIMM | UNRESOLVED (leans representation) | 16-line candidates .516 on DEV; 18-21-line override diagnostics .51-.61 |

Answer to the question: yes, at least one C1 XOR NULL (4222a5f7) is genuinely search-limited at its own sampled genome.

## 1. Findings

### F1 [V] 4222a5f7: a 12-line parity plant exists inside the row's own genome. Confidence: high.

The plant (SBF = sensor broadcast plus one-shot forwarding on a second channel; file sbf.py, call sbf(100, 3)):
```
 0 ADD   S3 = S3 + SENSE        sensor's signed, decaying latch (only sensors ever write S3)
 1 MULQ  PAY0 = S3*ENERGY       ENERGY = e_max = 1000, a free constant at economy-off rows
 2 ADD   PAY0 = PAY0 + IN0_0    forward whatever arrived on ch0, once
 3 MULQ  EMIT = PAY0*PAY0       emit iff |PAY0| >= 16
 4 MOV   CHAN = CNT0            forwarded traffic leaves on ch>=1, so it is never re-forwarded
 5 ADD   T3 = IN0_0 + IN1_0
 6 MAX   S1 = S1, T3            '+'-cue amplitude latch
 7 SUB   T0 = ZERO - T3
 8 MAX   S2 = S2, T0            '-'-cue amplitude latch
 9 MULQ  T1 = S1*S2
10 CONST T2 = 100<<3
11 SUB   S0 = T2 - T1           '-' iff both amplitudes are large
```

Why it works:
- Payload amplitude decays at the sender at the same rate as the receiver's latch, so the latch value at readout encodes time since the cue. Stale values from the previous trial are about 0.079 of fresh ones.
- One-hop forwarding roughly quadruples the effective fanout (direct reach about .59 per sensor), and the channel tag prevents re-forwarding cascades.
- Collisions stay small: 1,318 collided against 512,543 delivered.

Checks:
- Fresh W2VS, 32 pairs: .850 [.819, .879].
- Must-fail (sensor 2 zeroed): .500.
- The same number (.8503) comes out of hc.evaluate and out of prometheus.ananke.assays.evaluate, the C1 search's own evaluator.
- C1's own held-out worlds (search.HELD_NS from the row's search_seed): .832 [.798]. The C1 champion scored .503 [.474], so the plant would have passed SIGNAL.
- Every genome field lies in C1's random-genome ranges: fields 0..255, imm in [-128, 127].
- Single-line NOP ablation: every line is essential (each ablation gives <= .58 on DEV). Removing CHAN raises collisions from 326 to 246,942.
- Accuracy .85 is above W2-B's .75 ceiling for non-parity readouts, so the plant must use both inputs.

Strongest objection: the threshold was picked from 7 values on 8 DEV pairs. Answer: the scores above are on disjoint fresh worlds and on C1's own held-out worlds.

Commands:
- `python score_v.py A 4222_sbf_c800` (out/score_A.json)
- `python xcheck_4222.py`
- `python c1held.py`
- `python sbf_ablate.py`

### F2 [V/I] L8/C1 rows: lower-bound argument that no 8-line parity program works

Engine facts the argument uses:
- Each line writes exactly one register.
- T, EMIT, CHAN, RPORT, RVAL and PAY are rebuilt as 0 every tick. Only S persists, with S -= S>>3 every tick (values 1..7 are fixed points).
- The inbox holds SUMS of payloads per (channel, lane) since the last awake tick, plus counts. Noise of ±64 is added per copy.
- SENSE is ±256 at the two sensors only, for two ticks, and only when the sensor is awake.
- The actuator is never a sensor.

Obligations, in order of strength:
- (a) [V, proved] S0 must be written; otherwise acc = .5 exactly.
- (b) [V, proved] EMIT must be written. Without packets the actuator's trajectory is identical in mirror twins, so each pair scores exactly .5.
- (c) [I] Sensor memory, at least 1 line. Without it, emission happens only during the 2 cue ticks. Direct reach is then ≤ 1-(1-.9·8/99)^2 ≈ .14 per sensor, so P(both) ≈ .02. Relays need state as well.
- (d) [I] At least 1 payload write. With C=1, sign coding must ride in the payload.
- (e) [I] Two-sided latching, at least 3 lines. A single-line update S ← f(S, IN) cannot hold an idempotent two-flag OR-latch under summed arrivals (MAX keeps one sign; ADD and XOR are not idempotent and cancel mixed signs). So the minimum is MAX(P) + negate + MAX(Q), or equivalently a second sender lane.
- (f) [I] Readout, at least 2 lines: one to combine the latches and one sign-flipping comparison against a threshold.

Total: 2 + 1 + 1 + 1 + 3 = 8. That is the whole budget, with zero slack for a gain or a threshold constant.

Scale lemma [V]:
- With zero slack, the only nonzero constant register is ENERGY = 1000.
- The sensor latch is ≤ 2·256. One MULQ by ENERGY gives a payload ≤ 1953.
- The fresh latch at readout is about 135-300 (≤ 600 with 2-packet sums). The product/256 never reaches 1000, so the readout is pinned at '+'.
- Measured: the 8-line program (sb8.py) scores .504 [.500, .513] on 64 fresh worlds at 48256f59, and .500/.505 on DEV at the other two rows.
- Adding the missing 9th line (a gain or a constant) gives only .55-.59 on DEV (sb_grid.py, OVERRIDE). The sensor-only family is reach-limited (ceiling ≈ .5 + .5·.56²).

Exhaustive readout enumeration [V] (readout_enum_ctrl.py):
- Every feedback-free 2-instruction suffix over the full ISA (all ops except RAND; all readable registers at the actuator; imm -128..127; every shift).
- Applied to latch values fresh ∈ {130..320}, stale ∈ {0..25}: 1,941 distinct line-1 outputs × all line-2 instructions, about 4M programs.
- Result: 0 programs give the XOR sign pattern with ENERGY = 1000.
- Positive control: with a free constant 50 in place of ENERGY, it finds the known MULQ/SUB pair (1 hit). So the checker can fire.
- Sanity case: on an over-wide grid even a free constant fails, because the product cannot separate those ranges.

Confidence: high that the sign-coded latch family cannot work in 8 lines; medium that no 8-line parity program exists at all.

Not excluded:
- Readouts that use S0 as state (feedback). These were excluded because reading S0_old as an operand is an oracle in a static model; out/readout_enum.json and readout_enum.py are that superseded oracle run.
- Presence/timing codes. Their Bayes ceiling is about .62 under sensor-only reach.
- Relay structures outside this accounting.

### F3 [V] L8 rows, SIGNAL-level non-parity: a near-miss, not a pass

A one-flag (NOR) cheat in only 6 lines (sbnor.py) scores on fresh worlds:
- 48256f59: .591 [.547]
- 1974a9cf: .582 [.537]
- 333d6b2b: .578 [.534]

On C1's own held-out worlds it scores .547 / .591 / .551 (lo99 .51-.54). All are just under C1's SIGNAL bar of lo99 > .55.

This matches the analytic ceiling .25 + .5f + .25(1-f)^2 ≈ .58 at reach f ≈ .56.

So the C1 NULL at these rows is close to search-limited in the SIGNAL sense, but this is not shown. Confidence: high (`python score_v.py B ...`).

### F4 [V] The binding constraint at the L8 rows is the genome, not just 8 lines

Giving these rows prog_len 12 and channels 2 does NOT make SBF work (.50-.59 on DEV; sbf_l8_override.py, OVERRIDE). The causes are async .8, noise 64, loss and saturate dilution. W2-J's 16-line plant with 2 channels is the smallest known working plant there. Confidence: medium (DEV only, small grid).

### F5 [V] 84cf905d: no 16-line plant found; the line accounting gives ≥ 18-20 for the clocked-flood family

What is needed:
- A Kp counter as a non-decaying clock: ADDI reads imm + Kp0, WIMM writes it (2 lines).
- Phase: a constant and MOD (2 lines). The reset indicator needs 2 more.
- Latch: 4. Renormalisation: 2. Readout: 2. EMIT + PAY: 2. An emission window against in-flight leakage: 2-3.

Measured:
- 16-line variants ('split' relay roles by r0, and 'diff'): .516 on DEV.
- Diagnosis by trace: a sensor whose role does not match its cue never broadcasts; persistent emission leaks across the reset.
- 18- and 21-line OVERRIDE diagnostics (window plus random multiplexing): .51-.61 on DEV (k16w.py, k20.py).

Why clockless TTL is excluded [I]: decay 1 halves S, so a timer dies within 15 ticks, which is less than the 19-tick period. Late cross-links then re-trigger relearning.

A count-decoding trick is valid at this noiseless row and would remove multiplexing: payload ±1 per flag, a both-flag site sends 0, and nP and nQ follow from (IN, CNT). Even so the design still totals about 18 lines.

No plant is known at channels = 1 at any length; W2-J's plant needs channels 2. Confidence: medium.

### F6 [V] e2fd1e07: unresolved

- D=1 means the only decaying register is the readout itself.
- The SBF family scores only .54-.573 on DEV even with an override to D4 / L14 (sbf_e2.py).
- W2-J's 22-line TTL reached .643.
- Not enumerated: the 4 rules × 8 lines with SETRULE as a flag state machine, and Kp storage.

Confidence: low-medium that it is representation-limited.

## 2. Enumeration design (step 2)

Raw 8-line genome space:
- About 2.3e7 distinct effective lines (16 ops × 14 destinations × 20 × 20 sources × imm), so about 7e58 programs.
- A reduced alphabet (9 ops × 9 destinations × 12 × 12 sources, no imm) is about 1.2e4 per line, so about 4e32 programs.
- Simulation runs at about 20 candidates per second. Brute force is infeasible.

What I ran instead:
- (i) An exact-semantics, exhaustive enumeration of the readout suffix (F2): about 4M programs in 0.3 s, with a positive control.
- (ii) Constructive and family probes, batched as several genomes per World.
- (iii) A single-line NOP-ablation closure on the found plant.

## 3. Proposed fixes

- No code defects found, so no diff.
- NEUTRAL instrument: adopt the sbf.py plant (with xcheck_4222.py) as a strict-genome XOR known-answer at 4222a5f7-like physics.
- NEUTRAL accounting: reclassify 4222a5f7 in the H6 XOR ledger as search-limited at its sampled genome.

## 4. Disagreements

1. W2-J F3 / F9 / REPORT s3 say no plant fits a row's own genome and the solved NULLs are representation-or-search. This is false for 4222a5f7: a 12/12-line plant at the row's own fields scores .850 [.819].
2. W2-J (as relayed by the principal) says the smallest working plants need 16 lines plus 2 channels. At 4222a5f7 a 12-line plant on its native 4 channels works. The 9-line sensor-only SB scores .635 on DEV there, but sensor-only is not enough at the L8 rows.
3. W2-J F9 says the C-wave NULLs are at least as consistent with representation. That holds for 48256f59, 1974a9cf and 333d6b2b (F2), not for 4222a5f7.

## 5. Next questions (ranked)

1. Screen SBF-type designs (sensor broadcast plus channel-tagged one-hop forwarding) on every C1 row with global topology, channels ≥ 2, prog_len ≥ 12 and economy off, across all families. Of W2-J's 21 uncapped XOR rows only 4222a5f7 qualifies; FLIP, RELAY and MAJ rows are unscreened.
2. Close the remaining L8 loopholes with a dynamic enumeration that allows S0-feedback readouts (iterate S0 over ticks), and bound presence/timing codes.
3. 84cf905d: a dataflow/SAT model of a clocked flood with ≤ 16 lines, or a design that uses the 4 fixed rules plus count decoding.
4. e2fd1e07: can a 4-rule × 8-line flag state machine (SETRULE state, S0 as signed timer, channel-coded counts) exceed .6?
5. Search diagnostics at 4222a5f7: how far is the SBF plant from C1's mutation operator? Seed evolution from SB-9 (search allowed in a later brief) to separate budget-limited from landscape-limited.
6. Run XOR_PIVOT / XOR_SYM on the SBF plant as a ruler validation case at accuracy .85.
7. Firm up the 6-line NOR near-miss (lo99 .534-.547) with more worlds.

## 6. Inference ledger
```
Q: plant at 4222a5f7 own genome? | sbf.py; score_v A; xcheck; c1held; ablate | yes 12/12 lines .850[.819]; C1 held .832[.798]; mf .500 | high | threshold chosen on DEV | minimality below 12 | NQ1,NQ5
Q: 8-line parity at L8/C1 rows? | accounting (a-f); sb8 .504[.500]; readout_enum_ctrl 0 hits (+control 1 hit) | no in sign-coded latch family | med-high | feedback/presence codes not excluded | exotic codes | NQ2
Q: SIGNAL-level cheat at L8 genome? | sbnor.py fresh + C1 held | 6 lines .578-.591, lo99 .534-.547 < .55 | high | 2 spare lines unexplored | NOR with forwarding | NQ7
Q: is the L8 binding constraint just length? | sbf_l8_override (L12, C2) | no, .50-.59; physics (async/noise/loss) also binds | medium | DEV 8 pairs | - | -
Q: 84cf905d at 16 lines? | k16 .516; k16w/k20 override .51-.61; accounting | none found; family needs ~18-20 | medium | count-decoding not fully built | SAT model | NQ3
Q: e2fd1e07 at 8 lines x4 rules? | sbf_e2 override capacity .573 | none found | low-med | rule state machines untested | - | NQ4
```

## 7. Compute
- About 600 CPU-s ≈ 0.17 core-hours of the 0.6 cap: 358 s recorded across out/*.json, plus about 240 s untimed (imports, debugging, one killed oracle run).
- No GPU, no leases, no git writes, nothing written outside W2-V/.
