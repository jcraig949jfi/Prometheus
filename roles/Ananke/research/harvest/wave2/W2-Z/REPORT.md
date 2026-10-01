<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-Z; sha256(report)=8ca0a2dbf191bb74; delimited; see REPORT.provenance.json -->
W2-Z REPORT: Can economy-feasible plants solve the energy-economy rows, or does the budget make them physically impossible (P)?
Worker: W2-Z (Opus) for Ananke, Wave 2. Directory: roles/Ananke/research/harvest/wave2/W2-Z/

**Run conditions**
- CPU only: `CUDA_VISIBLE_DEVICES=-1`, and cuda is asserted unavailable.
- 1 thread, using W2-S `w2s_common` (imported read-only).
- Eager `hp_common.evaluate` and W2-S `flip_eval` only. `graph=True` was never used. No search.
- No git writes. Nothing written outside W2-Z/.

**Files**
- `econ.py`: exact single-site energy chain.
- `econ_rows.py`, `econ_all.py`: per-row budget tables.
- `econ_verify.py`: engine check of the chain.
- `xor_peco.py`: DP plus held-world LC2 bound.
- `plants_wz.py`: plant definitions.
- `run_flip.py`, `ka_flip.py`, `ka3.py`: FLIP plants and the known-answer (KA) gate.
- `run_maj.py`, `tab_maj.py`: MAJ sweep.
- `decompile_all.py` → `out/plants_decompiled.txt`.
- `out/*.json`, `out/*.log`, `out/maj_table.md`, `out/classification.json`.

**Void outputs (SHR bug, see below)**
- `out/flip_t0.json`, `scrA.log`, `scrB.log`, `scrC.log`, `flip_scrC.json`.
- Cause: the first plant draft put the SHR shift in the imm field. The engine takes the shift from the b field (`sh_r = f_bf & 15`).
- Fixed before any reported number.

## 1. FINDINGS

### F1 [V] The budget: what the engine actually charges (engine.py steps 4–5)

Per site and per tick:

`E(t+1) = clip(E(t) + I − a(t)·c_op·k_r − c_mem·m(t) − w(t)·c_emit·F, 0, E_max)`, with `E(0) = E_max`.

| term | meaning |
|---|---|
| I | income per tick (4 at every economy row) |
| a(t) | 1 if the site is awake this tick |
| k_r | number of lines with op ≠ 0 in the site's current rule r. Static per rule. Charged on every awake tick whatever the data, SEL outcomes or use of the result. SETRULE and WIMM count. |
| m(t) | number of non-zero S registers after RUN |
| w(t) | emission indicator. Needs a(t), EMIT > 0, and E(t) ≥ c_emit·F before spending. |
| F | `copies()` = fanout for sample/global; table width for dest=all (ring 2r, torus 2r(r+1), random k_random, smallworld 4) |

Consequences:
1. **Only emission is energy-gated.** Every line still executes at E = 0, and deficits below 0 are forgiven by the clip. A site that never emits pays nothing that matters: the actuator of FLIP, MAJ and XOR is economy-free.
2. **Gating cannot reduce cost.** SEL-gating or "skipping the long branch" (brief option b) is impossible by construction. NOP lines are free, so prog_len is irrelevant; only the non-NOP count matters. The only way to run fewer charged lines is SETRULE to a shorter rule. That takes effect next tick and costs one line itself.
3. **Long-run sustainability for an emitting site**, with n_a awake ticks and e emissions per trial of period Pd:
   - `e·c_emit·F ≤ Pd·(I − c_mem·m̄) − c_op·k·n_a`, plus forgiven deficits.
   - Activity A = p·c_op·k + c_mem·m (p = 1/P for sync). Steady emission needs A < I. The rate is then at most (I − A)/(c_emit·F) per tick.
   - With I = 4 and c_op = c_mem = 1, the maximum sustainable activity is p·k + m < 4. In lines:

| update mode | max sustainable k |
|---|---|
| sync P=1 | ≤ 3 − m (k = 4 − m is break-even: no surplus, so no emission) |
| sync P=2 | ≤ 7 − 2m |
| async p=.5 | < 8 − 2m |
| async p=.8 | < 5 − 1.25m |

4. **Forgiveness floor.**
   - Sync: emission at every wake whatever k if (P−1)(I − c_mem·m) ≥ c_emit·F. No assigned row meets this.
   - Async: from E = 0, a run of ⌈cE/(I − c_mem·m)⌉ asleep ticks refills. So "pinned at 0, never recovers" is false: emission continues at a k-independent residual rate.
5. **Initial store.** E(0) = E_max, so any program emits about E_max/cE times before the budget binds.

**Exact computation.** `econ.site_rates` propagates the full E distribution exactly: deterministically for sync, as a Markov chain for async. It gives expected emissions per trial for a site wishing to emit in its 2-tick cue window (e_cue) or at any time in the trial (e_any).
- Engine check (`econ_verify.py`, k-line cue emitters on held worlds): sync rows match exactly at every k, e.g. d01883ed .333/.25/.167/.083/.083 for k = 1/2/3/5/8. Async rows match within Monte Carlo noise (89a6: .448 vs .446 at k = 12; 247e: .661 vs .603 at k = 5, 16 worlds).
- kmax90 = largest k with e_cue ≥ 90% of k = 0, at m = 0 (optimistic). Full per-row tables for all 152 c_op = 1 evolve rows are in `out/econ_all.json`.

| family | kmax90 distribution |
|---|---|
| FLIP | 3–7 |
| XOR | 0–8 |
| MAJ | 3 at 42 of 60 rows |

Rows where one emission costs more than a trial's income (cE > I·Pd):

| row | family | cE | income per trial |
|---|---|---|---|
| d01883ed | XOR | 96 | 44 |
| 4ca24b85 | XOR | 48 | 44 |
| 266f3584 | MAJ | 48 | 28 |
| 00c5d3b6 | HOLD | 96 | 84 |
| 34f84c6b | FLIP | 96 | 52 |

- Confidence: high.
- Objection: m is treated as constant, and m = 0 is optimistic. That makes kmax an upper bound, which is the safe direction for P claims.

### F2 [V] The plants (decompiled in out/plants_decompiled.txt)

**(a) FLIP two-rule plant.** The FLIP actuator is marked by its teacher SENSE (±128), so sites can specialise by input.
- Relay rule (even rules), k = 5, m = 0:
  - `ADD T0 = SENSE + IN0_0`
  - `SHR PAY0 = T0 >> 1`
  - `MULQ EMIT = PAY0·PAY0`
  - `SHR T1 = SENSE >> 7`
  - `SETRULE T1`
  - The teacher gives ±1, an odd rule. A cue gives ±2, a relay rule.
  - Variant: the dedup relay (relay_flood semantics) plus dispatch, k = 11, m = 1.
- Actuator rule (odd rules), 29 lines, never emits, so it is free under the economy:
  - S2 = sign of the last cue wave.
  - S1 = m·256 ± 1. Kept odd so the site stays in an odd rule.
  - S0 = MULQ(S2, S1).
  - Keep-alive: m known, teacher present, or E < 100 (a dispatched actuator has just paid for the teacher echo; an initial-rule site still has E = E_max). Never on a cue, so sensors leave.
  - Bootstrap bugs found and fixed:
    - v1 needed the actuator awake on both teacher ticks. Under sync P=2 that never happens.
    - A sensor initialised in the actuator rule was treated as a teacher.
    - v2's leaky x memory let negative values decay to 0.
- Must-fail controls:
  - `nom`: the readout ignores m.
  - The budget itself: a relay rule with k above kmax.
  - Unshown for `nom`: zero_comm.

**(b) Gated / NOP-padded plants.** Not buildable as a cost saving (F1.2).

**(c) MAJ 3–5-line forms** (homogeneous, all rules):
- LEAK3 = W2-M INT_LEAK.
- LEAK4s1/s2: own leak, `S0 = (S0 >> s) + IN0_0`.
- LEAK5: `S0 −= S0 >> 2; S0 += IN0_0`.
- Member chosen on 16 DEV worlds (namespace 0x57325A44), then scored on the row's 64 HELD worlds.

### F3 [V] Known-answer gate: the budget predicts plant pass/fail (ka3.py → out/ka3.json)

Clean physics: ring64 r1, dest all, d = 3, δ = 16, 32 worlds. "lite" = c_emit 1 with no op/mem cost (the economy can never bind). "full" = the row economy.

| relay rule | update | economy | acc | B (mean of same- and changed-cue) [lo99] | budget says |
|---|---|---|---|---|---|
| stateless, k=5 | sync P=2 | full | **.924** | .934 [.902] | k=5 ≤ 7 → feasible |
| stateless, k=5 | sync P=1 | full | .500 (changed-cue .000) | .5 | k=5 > 3 → starves |
| stateless, k=5 | sync P=1 | lite | .969 | .973 [.946] | — |
| dedup, k=11 | sync P=2 | lite | .794 | .809 [.676] | — |
| dedup, k=11 | sync P=2 | full | .526 | .517 | k=11 > 7 → starves |
| stateless / dedup | async .5 | lite or full | .62–.65 | ≤ .655 | design limit, not economy |

- An economy-feasible FLIP plant exists in principle (.924, B certificate passed).
- Its failure exactly at k > kmax is the economy must-fail.
- Objection: the async limit is a property of my relays. It does not bound all plants.

### F4 [V] FLIP: 9 economy rows; no plant solves them, and the budget does not prove P

M = 16 screens (8 pairs) at row physics. The OVR tier = prog_len 29, plus setrule = 1 at the 4 rows with setrule = 0. Economy is never changed.
- Two-rule stateless (v3s) overall accuracy: 4b84 .458, 6037 .495, d3f3 .635, 5006 .602, 56cd .508 (v2), d998 .516 (v2), f476 .570, f4e5 .448, fc69 .484.
- Every row shows a copy-like pattern (same-cue ≫ changed-cue).
- The E-light control fails just as badly: 5006 .625/.625, f476 .562, fc69 .523, 56cd .508. The economy is not what kills this plant; the rows' caps, jitter, noise and async do. This matches W2-S, where 6 of these rows also need the five timing/loss dials removed.
- Dedup two-rule (k = 11, above kmax at all 9 rows): fails everywhere (≤ .613).
- Best: d3f3 at 32 pairs, .593 [.525], B .601 [.539]. The `nom` must-fail gives .505 / B .497, so some m-information is carried, but it is below SIGNAL and below the B certificate.

The budget cannot prove P, because short emitters are affordable (e_cue(1–3) is at maximum at all 9 rows). So all 9 are UNDECIDED, with three sharper sub-cases:
- **4b848d80, 603723a7, f4e59e61** (kmax90 4/3/4, async p = .8): the relay rule must fit in 3–4 non-NOP lines including a dispatch of at least 2 lines. That leaves 1–2 relay lines, and no dedup or attenuated relay of that size exists in my family. Lean P-ECONOMY [I].
- **d3f36006, 56cdba0a, d99833cb** (setrule = 0 in genome, kmax90 5) [I]:
  - Without setrule, rules are random and fixed per site.
  - A mixed-rule plant has acc ≤ .5 + .5·q(1−q)^h ≤ .625 (q = share of long rules, h ≥ 1 short emitters), so B certification is impossible.
  - A homogeneous FLIP plant would need ≤ 5 lines at every site.
  - Caveat: long rules still emit at about .1–.25 per trial under forgiveness, which loosens this bound.
- **50060cf9, f476a3ca, fc6972d4** (setrule = 1, kmax90 5–7): an economy-feasible two-rule design space exists. My member fails for non-economy reasons. Open.

- Confidence: high for the measurements; medium for the lean-P arguments.

### F5 [V] XOR: 7 economy rows; 2 are P-ECONOMY for any program, 1 is not economy-capped (xor_peco.py, econ_verify.py)

**d01883ed: P-ECONOMY.**
- cE = 96 exceeds the 44 income per trial, and any emitter needs at least 1 non-NOP line (EMIT is zeroed every tick).
- A DP over all emission policies gives at most 4 of 12 trials in which a sensor can emit (k = 1; 3 at k = 2). Greedy reaches the same maximum.
- With sync wake the emission schedule is deterministic, so it is independent of the loss and latency draws.
- On the row's own held worlds: acc ≤ .5 + .5·(4/12)·f_LC2, with f_LC2 = .531 measured by W2-J's `reach_trial` (R = 4). That gives .589. With f at its pair-CI top the bound is .625.
- LC2 also lets relays flood for free, so the true cap is lower.

**4ca24b85: P-ECONOMY, marginal.** cE = 48 > 44; DP maximum 9 of 12 trials; f = .265; bound .599 (point), .663 at the CI top.

**89a6a9cd: not economy-capped.**
- cE = 4, so a single asleep tick refills.
- Engine measurement: .43 emissions per sensor per trial even at k = 16, against .96 at k ≤ 5.
- W2-J's F8 claim ("once pinned at 0 it never recovers if p·k > 4", k* = 8) is wrong for async rows. Reclassify as UNDECIDED (non-economy: global fanout 1, async).

**93b9eeeb, 33505249, b3549a65, 247e0d43: UNDECIDED-ECON.**

| row | budget |
|---|---|
| 93b9 | k ≥ 8 (m=0) or ≥ 6 (m=1) emits only from the initial store; rules = 1 and L8, so every program has ≤ 8 lines |
| 3350 | kmax90 = 4 |
| b354 | kmax90 = 3 |
| 247e | kmax90 = 4 |

- The XOR actuator is unmarked, so the input-dispatch trick is unavailable. Only sensors can self-identify.
- No plant was built.
- W2-J's k* = 13 for 93b9 is too lenient: at k = 8 the per-period income equals the op cost and emissions stop after about 6.

- Confidence: high for d01883ed. Medium for 4ca24b85 (marginal, depends on LC2). High for the 89a6 correction.

### F6 [V] MAJ: 60 c_op=1 rows (run_maj.py → out/maj_table.md)

- 10 rows are P by W2-M's light cone (lc_bound < .60) and were not scored.
- Of the 50 scored at 32 pairs (64 held worlds):

| result | count | notes |
|---|---|---|
| PLANT-SOLVED (lo99 > .55) | 31 | 16 of these have a positive integration certificate (plant − DICT, 99% CI lo > 0) |
| zero_comm control | — | .500 at every solved row (16 worlds) |
| UNDECIDED | 19 | 9 global topology (no epidemic member), 8 multi-hop, 2 one-hop torus rows (8e605914 .589 [.543]; aad7e1b3 async, loss .6) |
| P-ECONOMY | 0 | even 266f3584 (cE > income per trial) reaches .600 [.565] |

- W2-M reproduced exactly: fded1681 LEAK3 .704 [.652].
- At most solved rows the champion scores about .50. Examples: f29ca123 plant .739 vs champion .513; acf58f34 .720 vs .536. So these MAJ NULLs are search-limited relative to a 3–5-line economy plant.
- Objections:
  - Member selection uses only 16 DEV worlds.
  - The 4 own-leak members were added by me. They are not preregistered, and W2-M's INT_LEAK was post hoc.
  - "+INT" uses DICT, an achievable single-sensor program but not the optimal one.

### F7 [V] Engine-semantics facts relevant to plant builders
- Shift ops (SHR, CONST) take their shift from the b field, not imm. My first draft got this wrong; it is caught in the void files listed at the top.
- RPORT and CHAN are safe scratch registers when RVAL = 0 and the rule never emits.
- Site mutation (mut_site) rewrites Kp, so immediates (CONST/ADDI) in plants can be corrupted at a rate of mut_site per tick. Minor.

## 2. PROPOSED FIXES
- No code defect found in the engine economy; the semantics are as documented. No diff.
- NEUTRAL (C2 instrument): add the exact energy recursion (`econ.site_rates` / `xor_peco.dp_max`) to every light-cone bound (LC2, lc_maj). Report kmax per row next to any "economy-throttled" claim.
- NEUTRAL (documentation): state in DESIGN that energy gates emission only, that ops are charged per static non-NOP line, and that deficits are forgiven.

## 3. DISAGREEMENTS
- **W2-J F8:**
  - "never recovers" is false under forgiveness for async rows.
  - 89a6a9cd is not economy-capped (engine-verified).
  - k* for 93b9 is too lenient.
  - d01883ed and 4ca24b85 are P for any program, not merely "≥ k* lines".
- **W2-S T2 "PLANT-DESIGN (econ)" for 4b84/6037/d3f3 (and the 6 tentative rows):**
  - Not established. Removing E rescues their 22-line homogeneous plant, but an economy-respecting plant must keep every emitting rule at or below kmax (3–7).
  - None that I built passes. Two of the three rows lean P (kmax 3–4).
  - Correct label: UNDECIDED-ECON.
  - Also: "a 22-line plant starves after its first awake tick" is imprecise. It drains the initial store in about 4–6 awake ticks, and only emission starves.
- **W2-M F6:** agree with the mechanism, and extend it: the actuator is energy-exempt, and 31 of 50 scorable MAJ economy rows are solved by 3–5-line plants.
- **Brief option (b)** (SEL-gated skipping): impossible by engine semantics (F1.2).

## 4. NEXT QUESTIONS (ranked)
1. Is there a relay of ≤ 3–4 non-NOP lines, including dispatch, that re-emits at most O(1) times per change? A bounded exhaustive enumeration at a RELAY known-answer cell would settle 4b84/6037/f4e5 as P-ECONOMY or plant-solvable.
2. Why do stateless attenuating relays fail under async (.62 at clean async .5 with no economy)? Can energy itself serve as the refractory period (an excitable medium) to make an async-safe relay of ≤ 5 lines? That would decide 5006/f476/fc69.
3. Is there a ≤ kmax homogeneous XOR readout? Candidate: |sum of signed arrivals| against CNT parity. Test at a KA cell, then at 3350/b354/247e.
4. Add the energy term to LC2 and lc_maj and recompute P counts for RELAY and HOLD economy rows. HOLD 00c5d3b6 also has cE (96) > income per trial (84).
5. Seeded-GA retention of LEAK3 at a MAJ economy row whose champion is about .50 (f29ca123, plant .739). Is the gap search or representation?
6. Formalise the setrule = 0 mixed-rule bound (≤ .625) including forgiveness-rate emission by long rules.
7. An epidemic, economy-cheap MAJ member for the 9 global MAJ rows.

## 5. INFERENCE LEDGER
question | evidence | result | confidence | strongest objection | unresolved | next
- What does the engine charge? | engine.py steps 4–5, read | static non-NOP count per awake tick; only emission gated; deficits forgiven | high | — | — | DESIGN note
- Is the exact chain correct? | econ_verify (sync exact; async within MC) | yes | high | m held constant | variable m | —
- Max sustainable activity? | chain, analytic | p·k + m < 4 (I=4) | high | m=0 optimistic | — | add to LC
- Can gating save energy? | engine line `nonnop += awake & (op != 0)` | no | high | — | — | —
- Do economy-feasible FLIP plants exist? | ka3 sync P=2 .924 / B .934 | yes in principle; starve at k > kmax | high | clean physics only | async | Q2
- FLIP 9 rows | M=16 screens, d3f3 at 32 pairs, E-light control | 0 solved; non-economy failure | high | plant family narrow | relay ≤ kmax | Q1, Q2
- XOR P-ECONOMY | DP + held LC2 | d018 .589, 4ca2 .599 | high / medium | LC2 estimate, .60 bar | 4ca2 CI | —
- 89a6 economy? | engine k=16: .43 emissions/sensor-trial | not capped | high | 16 worlds | — | —
- MAJ economy rows | 50 rows × 32 pairs, DICT, zero_comm | 31 solved (16 +INT), 19 UNDECIDED, 0 P-ECONOMY | high | DEV16 selection; post-hoc members | global/multi-hop | Q5, Q7

## 6. REVISED ECONOMY COUNTS
| family | assigned rows | PLANT-SOLVED | P-ECONOMY | UNDECIDED |
|---|---|---|---|---|
| FLIP | 9 | 0 | 0 | 9 (3 lean P [I]; 3 need setrule; 3 design open) |
| XOR | 7 | 0 | 2 (d01883ed; 4ca24b85 marginal) | 5 (4 economy-binding: 93b9, 3350, b354, 247e; 89a6 reclassified as non-economy) |
| MAJ (c_op=1) | 60 | 31 | 0 (plus 10 P-LC, light-cone capped per W2-M) | 19 (non-economy: global / multi-hop) |

- W2-J totals become CAPPED 64 (was 62) and UNDECIDED 13 (was 15), of which 4 are economy-binding (was 7).
- W2-S FLIP: the 9 "PLANT-DESIGN (economy)" rows become UNDECIDED-ECON.

## 7. COMPUTE
| item | process CPU (s) |
|---|---|
| logged runs | 1235 |
| killed first-round screens | ≈ 240 |
| KA runs | ≈ 100 |
| exact chains / DP / LC2 / engine checks | ≈ 150 |
| imports and debug | ≈ 200 |
| **total** | **≈ 1950 s ≈ 0.54 core-hours** (cap 0.6) |

1 thread per process, at most 3 concurrent processes, each under 4 min wall. No GPU, no search, no leases. No background processes remain.
