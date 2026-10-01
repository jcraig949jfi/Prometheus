<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-M; sha256(report)=98083b9d4f7a149c; delimited; see REPORT.provenance.json -->
W2-M REPORT: A MAJ INTEGRATION PLANT FAMILY, AND PLACING THE MAJ ROWS
Worker W2-M (Opus) for Ananke, Wave 2. Directory: roles/Ananke/research/harvest/wave2/W2-M/
Run conditions: CPU only (CUDA_VISIBLE_DEVICES=-1, CUDA asserted unavailable), 2 threads, eager evaluation through H-PLANT hp_common.evaluate. assays.evaluate was never used. No search. No git writes. Nothing was edited outside W2-M/.

Files:
- w2m_common.py: guards, exact Bayes table, row and seed helpers.
- w2m_plants.py: the plant family.
- lc_maj.py: k-sensor light cone plus realized placement.
- ka.py and ka_mh.py: known answers.
- score_rows.py: per-row scoring.
- override_check.py, econ_check.py, diag_fded.py, diag2.py: targeted checks.
- attain.py: ruler attainability.
- classify.py: row classification.
- finalize.py: writes the decompiled listing.
- out/*.json and out/*.log; out/plants_decompiled.txt holds every member.

## 0. KNOWN ANSWERS [V] (python ka.py; python ka_mh.py; 512 fresh worlds, namespace 0x57324D)

The exact majority-vote accuracy for k=5 votes, each flipped with p=.3, with ties scoring .5, is computed by w2m_common.bayes_table():

| votes that arrive, m | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| best accuracy | .5 | .70 | .70 | .784 | .784 | .83692 |

So a readout must see at least 3 votes to beat a single sensor.

Known-answer physics:
- KA-1H: ring of 64 sites, radius 3, d=3, so every sensor is one hop away. Lossless, sync with period 1, latency 1, no jitter, decay or noise. All votes arrive together.
- KA-1S: the same, but lat_hop=1, so one-hop arrivals are staggered by distance.
- KA-MH: ring of 64 sites, radius 1, d=2. Realized sensor distances are (1,1,2,2,3), so up to 3 hops.

| physics | member | acc [99% CI] | expected |
|---|---|---|---|
| KA-1H | INT_CO / INT_1 / INT_1G / INT_2 | .8415 [.826,.856] | Bayes .8369 |
| KA-1H | FIRST | .8415 | equals the integrator when all votes arrive together; the first wave already holds every vote |
| KA-1H | INT_1, zero_comm | .5000 | .5 |
| KA-1H | INT_1, DICT (only sensor 0 is cued) | .6960 [.678,.716] | .70 |
| KA-1S | INT_1 / INT_1G | .8415 | .837 |
| KA-1S | FIRST (must fail) | .6992 | at most .70: PASS |
| KA-1S | INT_CO (latest wave only; must fail) | .6976 | at most .70: PASS |
| KA-MH | INT_1 or FIRST (lane 1 only) | .6971 | 2 sensors one hop away: about .70 |
| KA-MH | INT_2 (2 relay lanes) | .7811 [.768,.795] | Bayes(4) = .784, since 4 sensors are within 2 hops |
| KA-MH | INT_3 (3 lanes, unweighted) | .8158 | below .837: echoes give one-hop votes 4 times the weight |
| KA-MH | INT_3NB (3 lanes, weights -2,1,1; 19 lines) | .8415 [.826,.856] | identical to KA-1H on the same seeds, so integration is exact |
| KA-MH | INT_3NB, zero_comm / DICT | .5000 / .6960 | .5 / .70 |

Gate: PASS. Every integrator reaches the Bayes rate where its lanes cover every sensor once. A single sensor gives .70, cutting communication gives .5, and the first-arrival and latest-wave readouts fall to about .70 once arrivals are staggered.

Defect found and fixed during the gate: in the first relay gate (EMIT = cue + CNT0), relays kept forwarding zero packets forever, so the tally never reset. The KA-MH multi-lane rows in out/ka.json are therefore void (flagged in the file). out/ka_mh.json supersedes them.

## 1. THE PLANT (decompiled; full listing in out/plants_decompiled.txt)

Every site runs the same program and acts as sensor, relay and readout. Nothing depends on position.

- **Sensor.** On a cue it emits its signed cue: PAY0 = SENSE, EMIT = SENSE^2. The gated member (INT_1G) emits only on the first awake cue tick, so each sensor casts one vote.
- **Relay, hop-limited lanes.** Lane i is forwarded as lane i+1 (PAY{i+1} = IN0_i). The relay emits only when lane content is non-zero (EMIT = cue^2 + IN0_i^2), so zero packets never circulate.
  - Forwarding sums is linear, so no sensor identity is needed. Deduplication comes from the hop limit.
  - On a radius-1 ring the walk counts are fixed, so the weights (-2,1,1) cancel the backtracking echoes exactly.
- **Readout.** S0 is the signed sum of all lanes over the current arrival run. A wake that sees arrivals after a silent wake starts a new run. That is a clock-free cue-onset detector; decay-sensitive counters do not work under C1's decay settings.
  - 'prev' members (INT_1, INT_2): S1 is the arrival flag of the previous wake.
  - 'age' members (INT_1A6, INT_2A6): S1 = max(arrival*256, S1>>1), and the run is kept while S1>>6 > 0.

INT_1 (11 lines, needs 2 state registers):
```
 0 MULQ T2 = MULQ(SENSE, SENSE)
 1 MOV  PAY0 = SENSE
 2 MOV  EMIT = T2
 3 GT   T0 = GT(CNT0, ZERO)
 4 MOV  T1 = S1
 5 SEL  T1 = (T1 > 0) ? S0 : ZERO
 6 ADD  T1 = ADD(T1, IN0_0)
 7 SUB  T1 = SUB(T1, S0)
 8 MULQ T1 = MULQ(T1, T0)
 9 ADD  S0 = ADD(S0, T1)
10 MOV  S1 = T0
```
INT_2 inserts `MOV PAY1 = IN0_0; MULQ T3 = IN0_0*IN0_0; ADD EMIT = T2+T3` and `ADD T1 += IN0_1` (14 lines, payload width at least 2).

Other members:
- INT_CO (6 lines, fits prog_len 8): S0 is the latest arrival wave only.
- INT_LEAK (3 lines): `EMIT = SENSE^2; PAY0 = SENSE; S0 += IN0_0`. It is energy-cheap and leaves forgetting to the physics decay.

Must-fail controls: FIRST (first-arrival readout), zero_comm, and DICT (a schedule ablation in which only sensor 0 is cued, with the plant unchanged).

## 2. FINDINGS

### F1 [V] The k-sensor light cone and realized placement for all 162 MAJ evolve rows (lc_maj.py, held worlds)
- The method extends H-PLANT's lightcone.py: m is the number of the 5 cues that can be processed at the actuator by readout under the fastest transport. The bound on any program is the mean over trials of Bayes(m).
- Placement reproduces W2-A2 c6c: 106 one-hop rows (19 SIGNAL) and 56 multi-hop rows (55 multi_all plus 1 multi_some; 0 SIGNAL).

| | n | bound < .60 (P) | bound <= .70 (no INTEGRATION possible) |
|---|---|---|---|
| SIGNAL (all one-hop) | 19 | 0 | 0 |
| NULL one-hop | 87 | 4 | 5 |
| NULL multi-hop | 56 | 25 | 33 |

- So 25 of the 56 multi-hop MAJ NULLs are physics-capped below SIGNAL level for any program, and 33 can never earn INTEGRATION.
- Confidence: high.
- Objection: the bound is optimistic. It ignores energy, ALOHA caps, sampled fanout, and global topology's random destinations (F6, F7), so it caps nothing more than it states.

### F2 [V] At the 19 SIGNAL rows (score_rows.py signal; member chosen on 32 dev worlds, scored on the row's own 64 held worlds)
- Validity checks:
  - All 19 champions reproduce their recorded held accuracy exactly on CPU.
  - zero_comm gives .500 for every plant.
- Plant at SIGNAL level (lo99 > .55): 18 of 19.
  - 14 are dev-selected members with a paired integration certificate (integrator minus DICT, lo > 0).
  - 4 economy cells (fded1681, 3c3d996a, 626aa72f, e341694d) pass only with the post-hoc INT_LEAK: .663–.704, lo .610–.652 (F6).
  - 613162a3 (global topology) is UNDECIDED: plant .590 against champion .682.
- Does the plant beat the champion? Paired 99% CI over the same held worlds:
  - Plant above: 8 rows. 57650798 +[.034,.115], 4ecdfb3f +[.151,.224], 8ccf6c72, 88f94654, 26f9428b, 8e1caf6b, 84c8c1d1, 8743da7f +[.121,.183].
  - Indistinguishable: 10 rows.
  - Champion above: 1 row (613162a3).
  - The 4 economy champions (.578–.589) sit well below INT_LEAK, but that comparison is unpaired.
- Can a single-sensor relay match the champion? I used the plant under DICT: the same transport carrying one cue.
  - It is not excluded at 11 rows: 57650798, fded1681, 4ecdfb3f, 8ccf6c72, 26f9428b, 8e1caf6b, 84c8c1d1, 3c3d996a, 626aa72f, e341694d, 8743da7f. Those champions' SIGNALs do not demonstrate integration.
  - The champion beats the single-sensor transport at 8 rows: 88a1a041, 88f94654, 0a23398f, f6b623cd, 613162a3, 4781b0a1 [-.204,-.066], 18c218f5, 1a86071f.
  - Every champion falls under DICT, to .500–.605. All of them depend on more than one cue, which fits H-CHK's count-threshold reading.
- 4781b0a1 is the only C1 row with the INTEGRATION label (lo99 .742).
  - The plant (INT_2) reaches .772 with lo .719. Plant minus champion is [-.056,.030], so they match.
  - The single-sensor transport (.651) cannot match the champion. The champion under DICT gives exactly .500.
  - So the label is genuine at this cell.
- Confidence: high for the numbers.
- Objection: with 64 held worlds the resolution is about ±.05. DICT changes the input statistics, so it is an achievable single-sensor program, not the optimal one.

### F3 [V] INTEGRATION ruler attainability (attain.py)
- With 32 pairs × 12 trials and a percentile bootstrap, passing lo99 > .70 needs:
  - Mean .76 for a 50% pass rate and .78–.80 for 87–98% when twins are identical, which is the plant case.
  - Mean .74–.76 when twins are independent.
  - The empirical plant mean minus lo99 has median .048.
  - So INTEGRATION needs a held mean of about .75–.78, against a ceiling of .837 (a margin of about .06–.09).
- Expected integrator accuracy E(q), when each vote arrives in time with probability q: E(.55) = .749, E(.60) = .759, E(.70) = .779. So the effective per-vote delivery must be at least about .6–.7, with nothing else lost.
- The 13 SIGNAL rows at ring of 100, radius 3, async with update probability .8, latency 4 = delta 4, loss .3:
  - A vote counts only if the sensor wakes at t0 (.8), the copy survives (.7), and the actuator is awake at the readout tick (.8). A two-hop path takes 8 ticks, longer than delta.
  - The ceiling for ANY program is .8·E(.56) + .1 = .701. The single-sensor ceiling is .590.
  - The plant scores .67–.73 there, and its DICT .57–.62, as predicted.
  - So INTEGRATION is unattainable by construction at the physics that produced 13 of 19 MAJ SIGNALs.
- Attainable at 3 SIGNAL physics, where the plant passes:
  - 4781b0a1 and 8743da7f: q = 1-(1-.9/6)^8 = .728, E = .784. Plant lo .719 / .746.
  - 4ecdfb3f: plant lo .721.
- Confidence: high, being analytic and matching measurement.
- Objection: the ceiling assumes no information in S0 when the actuator is asleep at readout. That holds because no packet can arrive before t0+4.

### F4 [V] The 30 stratified NULL rows (15 one-hop, 15 multi-hop, rng 0x57324D)
One-hop:
- PLANT-SOLVED (strict: dev-selected, lo99 > .55, paired integrator minus DICT lo > 0): 4 rows.
  - 48dbe2a1: .711/.669 against champion .564.
  - 1448cd7d: .694/.645.
  - 8051dc5e: .599/.557.
  - 15e58864: .708/.664.
- PLANT-SOLVED (weak): 4 rows.
  - 437ca0ac: .750/.695, but integration is not shown; DICT .692.
  - 070257d7, 13a086e9, 3d20243a: post-hoc INT_LEAK, .656–.697 with lo .587–.637.
- UNDECIDED: 7 rows.
  - 6 are global topology. b518e997, a5c7b8e0, 2bf18393, 3dfdd714, 23cd5528 are uncapped; 15d2a3e9 is light-cone capped (bound .500, latency 5 > delta 4).
  - 8c5eba06 has ALOHA collisions with cap 2.

Multi-hop:
- 0 of 15 solved inside the genome space. Most of these rows have payload width 1 or prog_len 8–12, so INT_2 does not fit.
- INT_2 with a genome override reaches .702 at c7ec8097 (prog_len 12→14, payload width 1→2) and .576 at 5c35b832. Both are outside the genome space, so they are R-candidates.
- 6 are light-cone capped (P) and 3 more have a bound of at most .70.

- Confidence: medium-high.
- Objection: the 30 rows are a sample. The INT_LEAK rows were added after I saw the failures.

### F5 [V] Single-sensor ceiling and FIRST at C1 physics
- FIRST scores .50–.74, always at or below the integrator.
- Plant DICT is .53–.66, always at or below .70.
- The must-fail controls behave at C1 physics too.

### F6 [V] The energy economy is a binding MAJ constraint that the light cone ignores (diag_fded.py, econ_check.py)
- 60 of 162 MAJ rows have e_income 4, e_max 100, c_emit 4 per copy, c_op 1 per non-NOP line per wake, c_mem 1 per non-zero S register per tick.
- At fded1681, INT_1 (11 lines) drained sensor energy below the 32 needed for an 8-copy emission. Sensors went silent after about 2 trials (traced: no emitters at t=22).
- The 3-line INT_LEAK restores emission and scores .704 against the champion's .584.
- Program length and active state are energy-limited at these cells. A per-trial emission budget (income × period ≥ emission cost + ops + memory) belongs in the bound.
- Confidence: high for the mechanism.

### F7 [I] Structural limits the plant cannot beat
- ALOHA cap c: more than c arriving packets wipe the inbox. With cap 2 or less, three or more votes cannot be counted in the same tick, so co-arrival integration is impossible (8c5eba06 .529 against .711 at the otherwise identical 48dbe2a1).
- Global topology with sampled fanout: a copy reaches the actuator only with probability about F/(N-1). Integration there needs epidemic relay, and this family has no global relay member, so 7 global rows stay UNDECIDED.

## 3. PROPOSED FIXES
- No changes to frozen material.
- NEUTRAL, for C2 design only:
  - Report MAJ INTEGRATION with a per-cell attainability ceiling (F3). Never read "no INTEGRATION" as a negative where the ceiling is below .78.
  - Add energy and cap terms to the light cone (F6, F7).
- No diff was produced.

## 4. DISAGREEMENTS
- W2-D, "H6-MAJ unplaceable (no plant)": superseded for one-hop. 18 of 19 SIGNAL cells and 8 of 15 sampled one-hop NULLs now have a SIGNAL-level plant.
- W2-A2 F3: I agree the 0/55 multi-hop SIGNAL count is forced by placement. I add that 25 of 56 multi-hop NULLs are physics-capped (P) and 33 can never reach INTEGRATION, so the 0/55 is not evidence about search.
- The prereg's INTEGRATION threshold (lo99 > .70) is sound, since .70 is an absolute single-sensor ceiling. But it was structurally unattainable at 13 of the 19 cells where MAJ found SIGNAL, so the absence of INTEGRATION there carries no information.

## 5. REVISED H6-MAJ
- **H6-MAJ one-hop:** R and P are excluded for SIGNAL-level competence at 18 of 19 SIGNAL cells and at 8 of 15 sampled one-hop NULLs (4 of them strict).
  - At 8 SIGNAL cells a plant beats the champion (paired), so those champions are below a reachable integrating plant (S-partial, like RELAY).
  - For the 8 solved NULLs the failure is on the search side. U and V are untested.
  - Global topology and ALOHA cells remain UNPLACED, because the plant family is inadequate there.
- **H6-MAJ multi-hop:** P binds for 25 of 56 rows (light cone below .60). The rest are UNPLACED: no in-genome plant was found, and the one override plant (c7ec8097, .702) marks an R-candidate.
- **INTEGRATION:** unattainable for any program at 13 of 19 SIGNAL-cell physics (ceiling .701), and at 33 of 56 multi-hop cells. It is attainable and plant-certified at 4781b0a1, 8743da7f and 4ecdfb3f. Only 4781b0a1 holds the label, and there the plant matches the champion while a single-sensor transport cannot.
- **Falsifier for "search-limited" at a MAJ cell:** a plant-seeded GA loses INT_1, or no in-genome plant passes.

## 6. NEXT QUESTIONS (ranked)
1. Seeded-GA retention of INT_1 at 8743da7f (plant .788 against champion .636). Would the GA keep it? That would locate S at a MAJ cell.
2. A global-topology epidemic integrator (TTL lanes) to place the 34 global MAJ rows, including SIGNAL row 613162a3.
3. Run INT_LEAK and other energy-cheap members at all 60 economy rows, and add an emission-energy term to the light cone.
4. A staggered-emission integrator (random delay via RAND) for ALOHA-cap rows, with the bound that at most c votes can be counted per tick.
5. Score the remaining 113 NULLs. That needs about 0.6 more core-hours.
6. A multi-hop MAJ test cell where INT_2 is in the genome space (payload width ≥ 2, prog_len ≥ 14, light cone above .8), with W2-A2's geometry guard: does search reach multi-hop integration?
7. At 4781b0a1, accuracy against the number of cued sensors (DICT-k, k = 1..5): does it separate sum-integration from a count threshold?

## 7. INFERENCE LEDGER
question | evidence | result | confidence | strongest objection | unresolved | next
- Does the plant integrate at known physics? | KA 512 worlds; INT_3NB equals KA-1H exactly; DICT .696; zero .5 | yes, at Bayes | high | clean physics only | — | —
- Light cone for k=5 | lc_maj.py, 162 rows | 25/56 multi-hop P; 0 SIGNAL capped | high | optimistic: ignores energy and caps | energy term | Q3
- Plant at SIGNAL rows | score_signal.json | 18/19 SIGNAL-level; beats champion at 8 | high | 64-world resolution | U at those cells | Q1
- Can a single-sensor relay match the champion? | DICT-plant minus champion | yes at 11/19; no at 8 (incl. 4781b0a1) | medium-high | DICT is not the optimal single-sensor program | — | Q7
- Can INTEGRATION be attained? | attain.py plus measurements | needs mean ≈ .75–.78; ceiling .701 at 13/19 cells | high | assumes S0 is uninformative at an asleep readout | — | prereg note
- Placing the NULLs | 30 stratified rows | one-hop 4 strict + 4 weak solved; multi-hop 0/15 | medium-high | sample of 30; INT_LEAK post hoc | 113 rows | Q5
- Hidden constraints | diag_fded trace, econ_check | energy and ALOHA bind | high (energy) / medium (ALOHA) | — | bound form | Q3, Q4

## 8. COMPUTE
About 2,000 CPU-s, or about 0.56 core-hours (cap 0.6), measured as process CPU time at 2 threads.
- Light cone 55; known answers 272 + 102; scoring 750 (SIGNAL rows) + 654 (NULL rows); override 64; economy check 58; diagnostics and benchmark about 15; attainability about 30.
- No GPU, no search, no leases. No background processes remain.
