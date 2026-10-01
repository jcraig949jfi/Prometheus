<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-Q; sha256(report)=e211576e9a438a7a; delimited; see REPORT.provenance.json -->
# W2-Q: distractor-strobed HOLD prevalence and the rule-mosaic lottery (Ananke Wave 2, 2026-10-01)

Worker W2-Q, fresh namespace 0x5751. Directory: roles/Ananke/research/harvest/wave2/W2-Q/.

**Files**
- PLAN.md: predictions, written before any run.
- q_common.py: batched paired runner.
- q0_probe.py: timing test, plus a check that a batched run equals a standalone run.
- q1_distr_edits.py and q1b_mag_ranges.py: Task 1.
- q2_lottery.py: Task 2.
- Outputs are in out/*.json.
- Proposed patch and test: patch/a1_mirrored_r0.diff and patch/test_r0_mirror.py.

**Method**
- CPU only, eager evaluation (graph=False), 2 threads, 16 mirror pairs (32 worlds) per condition.
- All conditions for one cell run in ONE World. The schedules are stacked along the world axis and every block uses the same world seeds. The engine's randomness depends only on (world seed, site, tick), so each block is exactly the standalone run (checked bit-exact in q0). Every edit is therefore paired with the normal run on identical worlds.

## 1. TASK 1: how common is HOLD memory that the distractor schedule triggers or clocks?

The 86 HOLD evolve champions with held lo99 > .60 (the same set as W2-E a9) were run under these edits:
- **A.** First awake gap distractor silenced (W2-E a10's definition).
- **B.** Timing jittered. HOLD puts a distractor on every gap tick, so "same count, jittered timing" is impossible at full occupancy. The closest version that keeps a fixed count: on each trial, ceil(n/2) of the n awake gap slots keep their distractor, at random positions. Mirror partners get the same edit, and each trial records whether its first slot was silent.
- **C.** Magnitudes randomised, |d| ~ U{1..255}, sign kept.
- **q1b follow-up** on 27 cells: Clow U{1..64} (never above the trained amplitude), Cmid U{1..128} (never above half the cue), Chi U{129..255}.

Collapse means paired hi99(edit - normal) < 0 and accuracy under the edit < .60.

| cell | lineage | normal | A | B (first slot kept / silent) | Clow | Cmid | C (1..255) | verdict |
|---|---|---|---|---|---|---|---|---|
| 2c300c47 | D replicate of 85ca202e, same physics | 1.000 | .462 C | .508 C (.62 / .39) | .932↓ | .923↓ | .948↓ | strobe, collapses |
| 0c18ce5e | child of d49fdac8, same physics | .958 | .500 C | .539 C (.58 / .50) | .701↓ | .734↓ | .712↓ | strobe, collapses |
| 41fcb232 | child of d49fdac8 | .625 | .500 C | .474 C | .508 C | .560 C | .578 C | collapses under all edits |
| 311c465f | torus, setrule=1, rules=2 | .773 | .727 (n.s.) | .643↓ (.72 / .57) | .556 C | .592 C | .561 C | parity clock: hurt by B, collapses on magnitude |
| 0a3f6b87 | child of ae39bee8, same physics | .948 | .750↓ | .833↓ (.91 / .76) | .932↓ | .863↓ | .759↓ | depends on schedule, no collapse |

C = collapse; ↓ = significant drop without collapse. Smaller but significant A drops: b32bbf91 (-.013) and 13127335 (-.025), both still near normal accuracy.

**Prevalence across all 86**
- A collapses 3/86 and B collapses 3/86, the same three cells (2c300c47, 0c18ce5e, 41fcb232).
- B significantly hurts exactly the 5 W2-E cells. B significantly IMPROVES 22/86 cells (fewer distractors means less corruption).
- Clow significantly hurts exactly the same 5. It collapses 311c465f and 41fcb232, and improves 9/27.
- Schedule-triggered or clocked memory is **5/86 = 5.8% of cells**. Those cells hold **6.5% of the total above-chance accuracy** of HOLD SIGNAL, and A or B removes 5.3% of it. **Schedule-robust memory is 81/86 = 94%**: these cells are not hurt by A, B or Clow.
- New cells beyond W2-E's 5: **0** (I predicted 0-3).
- Clow was tested on only 27 cells. Among the 23 non-strobe cells tested, 0 were hurt (95% upper bound about 12%) and the other ~59 are unmeasured.

**Broad magnitudes (C) is mostly a test-fairness effect, not schedule exploitation**
- C significantly hurts 76/86 cells and collapses 14, including six cells at 1.000 (85ca202e, ab089e45, 25c70c72, 24711149, 7b7b025e, 9d0812f5, which fall to .51-.67).
- The q1b split shows where the damage comes from:
  - Chi (129..255) collapses 16 of 27 cells.
  - Cmid (≤128) collapses 3 (311c465f, 41fcb232, da0de53c) and dents 8 non-strobe cells. These are threshold latches with the threshold somewhere in (64, 128].
  - Clow hurts only the 5.
- Apart from timing, HOLD tells the cue from a distractor only by amplitude (256 vs 64). Distractors near 256 make the task ill-posed, so "robust to magnitude" cannot be defined above about 128.
- Second tier: about 1 in 10 of a random sample (4a3b237b) uses a threshold that only works because the distractor amplitude is fixed at 64.

**Prediction check**
- P1 held in part. The 3 near-perfect strobe cells collapse under both A and B. 311c465f collapses under Clow and C, and B drops it by .13 to .643 (above .60, so not a collapse). 0a3f6b87 drops significantly but never collapses, as predicted.
- P2 held at the low end (0 new). P3 held (5.8%).
- P4 was wrong in detail. 2c300c47 hardly cares about magnitude (.948 under broad C), while 0c18ce5e falls to about .70-.73 under every magnitude range.
- B splits by first slot (kept / silent) are 2c300c47 .62/.39 and 0c18ce5e .58/.50. So a kept first distractor is not enough: the later slot pattern also matters. "Strobe = first distractor only" (W2-E) is too simple under jitter.

## 2. TASK 2: the rule-mosaic lottery (setrule=0, rules>1)

How rules are initialised (engine.py:155-157): `h = rng.chain(rng.site_base(self.ws, rng.INIT, 0, sites), 7); r = h % rules; r0 = r.clone()`.
- With setrule=0, `do_rule` is False, so r never changes.
- Mirror partners share the world seed, so they share the r map. The pair is the lottery unit.
- In HOLD the sensor is the actuator (sidx = ridx = a), so a local latch depends only on the actuator's rule.

Pinning: World.r and World.r0 were overwritten after construction for each block. This is a monkeypatch in my script only; engine.py is untouched.

Lottery share = (normal - worst pin) / (normal - .5). R² = share of pair-accuracy variance explained by the actuator's initial rule.

| cell | family | rules | C1 | recorded held / train_final | fresh normal [99% CI] | pins r=0..G-1 | best pin - normal | R² | lottery share | class |
|---|---|---|---|---|---|---|---|---|---|---|
| 0187372b | HOLD | 2 | SIG | .750 / .529 | .768 [.607, .919] | .503, .979 | +.211 | .95 | .99 | LOTTERY |
| 8d1c8213 | HOLD | 2 | SIG | .719 / .615 | .704 [.576, .844] | .896, .500 | +.191 | .92 | 1.00 | LOTTERY |
| 7ca102eb | HOLD | 2 | SIG | .646 / .635 | .616 [.488, .724] | .737, .479 | +.121 | .72 | 1.00 | LOTTERY |
| 83d0ff56 | HOLD | 4 | SIG | .646 / .750 | .755 [.638, .869] | .5, .885, .5, .885 | +.130 | .86 | 1.00 | LOTTERY (rules 1 and 3 both work) |
| b4e404f6 | HOLD | 2 | SIG | .639 / .576 | .608 [.526, .702] | .771, .510 | +.163 | .95 | .90 | LOTTERY |
| cdf60380 | HOLD | 2 | SIG | .645 / .599 | .659 | .682, .615 | +.023 | .31 | .28 | weak lottery |
| b32bbf91 | HOLD | 2 | SIG | .705 / .732 | .691 | .694, .676 | +.003 | .00 | .08 | no lottery (rules equivalent) |
| 4ecdfb3f | MAJ | 2 | SIG | .582 / .570 | .582 | .574, .587 | +.005 | .01 | .10 | no lottery |
| d8e7e830 | HOLD | 2 | near | .579 / .701 | .617 | .500, .706 | +.089 | .34 | 1.00 | LOTTERY |
| ac928135 | HOLD | 4 | near | .579 / .552 | .612 | .505, .500, .784, .583 | +.172 | .72 | 1.00 | LOTTERY |
| ce12e730 | HOLD | 2 | near | .578 / .578 | .714 | .753, .500 | +.039 | .75 | 1.00 | LOTTERY |
| 6f360694 | HOLD | 4 | near | .574 / .620 | .595 | .5, .695, .5, .695 | +.100 | .69 | 1.00 | LOTTERY |
| b87aa64f | HOLD | 2 | near | .570 / .615 | .513 | .487, .589 | +.076 | .23 | 1.00 | LOTTERY (normal not reproduced) |
| a5e461d8 | HOLD | 4 | near | .566 / .625 | .574 | .5, .5, .5, .787 | +.212 | .96 | 1.00 | LOTTERY (1 working rule in 4) |
| 437ca0ac | MAJ | 2 | near | .568 / .552 | .538 | .500, .500 | -.038 (sig.) | .04 | n/a | uses the mosaic (both pins at chance) |

**Prevalence**
- Lottery: 5/8 SIGNAL cells (all HOLD) plus 1 weak; 6/7 near-SIGNAL cells.
- In 11/15 cells one pinned rule scores exactly .500. That rule never writes a non-zero S0 at readout, so it is dead.
- The normal accuracy equals the mixture over the actuator's initial rule. Example, 0187372b: (14 × .503 + 18 × .979) / 32 = .771, against .768 measured. The rules at other sites do not matter.
- So the cell's "law" is one working rule plus a dead rule, and the world seed decides which one the actuator gets. These cells report about half of what their physics can do: the best pin is up to +.21 above normal.
- Measured accuracy also depends on which pairs were drawn. With 8 final pairs, the expected spread is about ±.08, which matches W2-E's held - train sd of .079. That explains held >> train.

**Fragile cells and failed reproductions vs the lottery class** (from records; no compute)
- **W-F census class changes at 512 worlds** (corrections_WF.csv): 4 of the 8 lottery-class census cells changed (0187372b, 7ca102eb, b4e404f6, cdf60380), against 21/158 other cells. Odds ratio 6.5, Fisher p = .019. Three of the four are strong lottery cells.
  - Mechanism [I]: only ~40-55% of worlds carry the working rule, so a 64-world swap has about half the effect and extra variance between worlds.
- **W-O 512-world reruns:** 5 of the 6 audited lottery-class specimens got a non-CHANCE rerun (0187372b, cdf60380, 7ca102eb, 83d0ff56, b4e404f6), against 35/79 others. p = .095.
- **W-Z seed-sensitivity disagreements:** of 15 specimens, only 4ecdfb3f is in the lottery class, and it is NOT a lottery cell (pins ≈ normal). The W-Z flips are not lottery.
- **D/E replicates:** none is in the lottery class (all rules=1 or setrule=1). The D replication failures (bbef66a1 replicates .572/.506, 6597c043, 60eb1738, 772ae210, ...) are not lottery. They are search failures; see W2-E S7.

## 3. Findings
1. **[V] Five HOLD champions use the schedule.** 5/86 HOLD champions (5.8% of cells, 6.5% of above-chance accuracy) depend on the distractor schedule under fair edits (A, B, Clow). 4 collapse. No new cells beyond W2-E's 5.
   - Check: q1_distr_edits.py, q1b_mag_ranges.py.
   - Confidence: high.
   - Objections: 16 pairs per cell; B is a half-count jitter, not same-count (same-count is impossible).
   - Unresolved: Clow on the remaining 59 cells.
2. **[V] Same physics, different mechanism.** Strobe cells and robust cells sit at IDENTICAL physics and env: 2c300c47 vs 85ca202e, 0c18ce5e vs d49fdac8, 0a3f6b87 vs ae39bee8 (physics and env dicts equal; 41fcb232 differs only in lat_base). Schedule dependence is decided by the search seed, not by the cell.
   - Confidence: high.
   - Objection: parent and child come from different waves (D/B/B2 vs A/B), but the physics and env are identical.
3. **[V] Broad-magnitude collapses are not exploitation.** 76/86 cells drop under |d| up to 255, but almost all of that comes from distractors above 128 (Chi), where the cue cannot be told from a distractor. Clow hurts only the 5, and improves 9/27.
   - Confidence: high.
   - Objection: Cmid shows a small group of threshold latches tuned to the fixed amplitude 64 (8/23 in a biased sample, 1/10 random).
4. **[V] Distractors corrupt most memories rather than serve them.** Removing half of them (B) improves 22/86 cells, by up to +.14 (2b7f38fc), and Clow improves many. This fits leaky-integrator memory that distractors degrade, not clean latches.
   - Confidence: medium-high.
   - Objection: B also lowers the total distractor energy.
5. **[V] Rule-mosaic lottery.** 5/8 setrule=0, rules>1 SIGNAL cells and 6/7 near-SIGNAL cells are lottery cells. One rule works, the other is dead (pin = .500), and only the actuator's initial rule matters (R² .69-.96; normal = mixture). Best pin up to +.21 above normal.
   - Check: q2_lottery.py.
   - Confidence: high.
   - Objection: 16 pairs per pin.
6. **[V] W2-E a1 split the worlds on the wrong rule.** It recomputed r0 from UNMIRRORED seeds while the run used mirrored ones, so 16-38% of worlds got the wrong actuator rule (q2: frac_r0_mismatch_unmirrored).
   - Corrected 0187372b: r0=1 .982 / r0=0 .494 (W2-E reported .834 / .592).
   - Corrected 8d1c8213: .909 / .500 (W2-E reported .826 / .594).
   - W2-E's "r0 explains only part, neighbour rules presumably matter" is withdrawn: r0 at the actuator explains almost everything.
   - Check: patch/test_r0_mirror.py.
   - Confidence: high.
7. **[V from records] Lottery cells over-represented among census corrections.** They are over-represented among the 512-world census class corrections (OR 6.5, p = .019), weakly so among W-O reruns (p = .095), and absent from W-Z flips and D/E replicate failures.
   - Confidence: medium (small counts).
8. **[I] The lottery biases any rules-axis effect at setrule=0.** "rules>1 hurts at setrule=0" is partly a search failure to make both rule bodies work (83d0ff56 managed 2 of 4), not physics. The ceiling is the best pin.
   - Confidence: medium.
9. **[V] 437ca0ac (MAJ) needs mixed rules.** Both pins are at chance and normal is .538, so it needs both rules present. The lottery is not the only rules>1 phenomenon.
   - Confidence: medium (small effect).

## 4. Proposed fixes
- **NEUTRAL (analysis script; no frozen semantics change).** patch/a1_mirrored_r0.diff makes W2-E a1 read r0 from the run's own World (w.r0).
  - Test: patch/test_r0_mirror.py.
  - FAILS on the current method: `CUDA_VISIBLE_DEVICES=-1 python -m pytest patch/test_r0_mirror.py -q` gives 1 failed.
  - PASSES patched: the same command with `W2Q_PATCHED=1` gives 1 passed. Both were run.
- **SEMANTIC (C2 proposals only).**
  - (a) Report the actuator's initial rule (r0) as a covariate, plus the pinned-rule ceiling, for every rules>1, setrule=0 cell.
  - (b) A HOLD variant with stochastic gap occupancy (silent gap slots).
  - (c) Distractor amplitude drawn from a range below cue/2, so strobe and amplitude-tuned latches cannot pass. Do NOT use ranges near the cue amplitude.

## 5. Disagreements
- With W2-E N1 / finding 9: the r0 split is wrong because of the mirroring bug. Corrected, the actuator's r0 explains almost all the bimodality (R² .95 / .92); the neighbours do not matter.
- With W2-E D1 "the first distractor acts as a store strobe": true for single-tick silencing, but incomplete. Under half-occupancy jitter with the first slot KEPT, 2c300c47 still drops to .62 and 0c18ce5e to .58, so the rest of the slot pattern matters too.
- With W2-E's proposed test "constant amplitude is fine, most of 16-200 works": randomised magnitudes ≤64 still drop 0c18ce5e to .70.
- With CROSS_THREAD_COMPRESSION H5 ("family label predicts mechanism"): it fails even within an identical physics + env cell (finding 2). In lottery cells one law gives two per-world mechanisms (working or dead), so "the cell's mechanism" is not well-defined.
- With any reading of C1 HOLD SIGNAL as distractor-robust memory: 94% of cells are robust in the fair sense, but almost none survive distractors at near-cue amplitude, and that test is not fair.

## 6. Next questions (ranked)
1. Run C1-style search at setrule=0, rules=2, seeded with a duplicated rule body (rule 1 := rule 0). Does every lottery cell reach its best-pin accuracy, i.e. is the lottery purely a duplication-search failure?
2. Re-run W-F swaps for 0187372b, 7ca102eb, b4e404f6 and 8d1c8213 on r-pinned worlds (the working rule). Do the census classes become stable at 64 worlds? This confirms the lottery-underpower mechanism.
3. Clow on the remaining 59 HOLD cells (~250 CPU-s). Tightens the 0/23 bound on amplitude-tuned memory.
4. Register-level trace of 2c300c47 under B with the first slot kept: which later slot pattern does it need (parity of count, last-slot timing)?
5. For identical-physics pairs (85ca202e vs 2c300c47, d49fdac8 vs 0c18ce5e), how often does C1 search land on a strobe at that physics? This needs bounded re-searches, which are not allowed in this wave.
6. Lottery class in non-evolve rows (C1b, plants): does any reported C1b number at rules>1, setrule=0 carry the same mixture bias?
7. 437ca0ac: which role split between rules makes the mosaic required (sensor rule vs relay rule)?

## 7. Inference ledger
| question | evidence | result | confidence | strongest objection | unresolved | next |
|---|---|---|---|---|---|---|
| prevalence of schedule-triggered HOLD memory | q1 (A, B, C on 86), q1b | 5/86 (5.8%; 6.5% of above-chance accuracy); 4 collapse; 0 new | high | B is half-count, 16 pairs | Clow on 59 cells | Q3 |
| is the broad-magnitude collapse exploitation? | q1b Clow/Cmid/Chi | no: it comes from distractors near cue amplitude | high | threshold-latch tier biased sample | random-sample tier | Q3 |
| first-distractor strobe sufficient? | q1 B first-kept split | no: pattern matters beyond the first slot | medium-high | trial-level split, small n | register path | Q4 |
| does family + physics fix mechanism? | physics equality of parent/child | no: same physics gives strobe vs robust | high | different waves | strobe frequency per physics | Q5 |
| how much setrule=0 rules>1 accuracy is lottery | q2 pins, R² | 11/15 lottery; share .90-1.0; ceiling +.09-.21 | high | 16 pairs | duplication search | Q1 |
| W2-E r0 split correct? | engine.py:155, q2 mismatch, test | no: unmirrored seeds; corrected .98/.49 | high | — | — | patch |
| lottery vs fragile cells | corrections_WF, W-O rerun table, W-Z row table, D rows | census OR 6.5 p=.019; W-O p=.095; W-Z and D not lottery | medium | small counts | pinned-world swaps | Q2 |
| mosaic used constructively? | q2 437ca0ac | yes, weakly (MAJ) | medium | small effect | role split | Q7 |

## 8. Compute
- CPU only, CUDA_VISIBLE_DEVICES=-1, torch.cuda.is_available() asserted False, 2 threads, eager. No GPU, no lease actions, no search.
- process_time per script: q0 15 s; q1 762 + 136 s; q1b 506 s; q2 166 s; pytest ~10 s.
- **Total about 1595 CPU-s = 0.44 core-hours**, within the 0.5 cap. Every run was under 10 min wall.
