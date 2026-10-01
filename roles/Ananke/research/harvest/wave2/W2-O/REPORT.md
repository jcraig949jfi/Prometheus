<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-O; sha256(report)=3c228f5eb8d0e006; delimited; see REPORT.provenance.json -->
W2-O REPORT: were any recorded C1 NULLs broken experiments rather than real NULLs?
Worker W2-O (Opus) for Ananke, Wave 2. Directory: roles/Ananke/research/harvest/wave2/W2-O/
CPU only, at most 2 threads, eager evaluation (graph=False). No git writes. Nothing outside W2-O was edited.

Files:
- select_cells.py: the stratified sample. The rule and RNG seed 0x57324F were fixed before any evaluation. Output: out/sample.json.
- null_audit.py: the recorded champion re-run on its recorded HELD seeds (normal arm plus zero_comm arm) inside W2-C's guarded() context. It also runs the known-answer gate, a direct G8 check, readout and transport probes, and the feasibility instrument (directed reachability, exact wake recomputation, information ceiling). Output: out/null_audit.jsonl.
- final_check.py: the same champion on its recorded FINAL (selection-ranking) seeds, under the guards. Output: out/final_check.json.
- g12_diag.py: G12 diagnosis (schedule, readout, emission and energy by half, per-trial accuracy by half), plus a negative-control panel of 4 recorded SIGNAL cells. Outputs: out/g12_diag.jsonl, out/g12_signal.jsonl.
- per_arm_guards.py: works out which arm raised an alarm. Output: out/per_arm_guards.jsonl.
- reach_census.py: reachability on the held worlds of every C1 evolve row in XOR/FLIP/RELAY/MAJ, with no engine runs. Output: out/reach_census.json.
- g8_all.py: held seeds against train+final seeds, over all 678 evolve rows. Output: out/g8_all.json.
- summarize.py: builds the table. Output: out/table.json.
- Patch: patches/g12_exempt_controls.NEUTRAL.diff. The patched copy is W2-O/pte_mut/; null_audit.py still imports W2-C's unpatched guards.
- Tests: tests/test_g12_control_exempt.py, and tests/test_guards_w2c_on_patched.py (a copy of W2-C's guard tests run against the patched copy).

## 0. KNOWN-ANSWER GATE: PASS in 16/16 [V]
For every sampled cell, the CPU re-run reproduced every recorded number EXACTLY (|diff| < 1e-12):
- held acc, lo99, hi99, zero_comm, comm_delta, comm_delta_lo99;
- champ_train_final on the FINAL seeds;
- every held_tel field (largest deviation 2.8e-17).

So no cell was stopped. Command: python null_audit.py; python final_check.py.

The feasibility instrument was also checked against the engine: its recomputed wake mask matched the engine's stats["awake"] totals exactly in 16/16 cells.

## 1. PER-CELL TABLE
Column key:
- Alarms: guards that fired, excluding G0. G0 (degenerate zero_comm control) fired in 14/16 cells; it did not fire on the two FLIP cells marked "noG0".
- Imp: graph-impossible worlds out of 64.
- LC: H-PLANT light-cone bound.
- Ceil: wake-loss information ceiling from my instrument. It ignores timing.
- Dead: worlds whose readout S0 is 0 at every scored readout.
- maxacc: highest training max_acc over all 36 generations.

| fam | stratum | cell | topo d hops | held | alarms (excl. G0) | imp | LC | ceil | dead/64 | maxacc | class |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FLIP | d9cc named | 6f82f9c7 | ring d3 h1 | .479 | none | 0 | 1.0 | 1.0 | 0 | .641 | ADMISSIBLE |
| XOR | uncapped, directed | 2a226bec | random d2 h3 | .502 | none | 0 | 1.0 | .969 | 52 | .521 | INERT |
| XOR | uncapped, symmetric | abb5fb81 | torus d1 h2 | .484 | none | 0 | .625 | 1.0 | 2 | .578 | ADMISSIBLE (LC marginal) |
| XOR | capped, directed | 9c941931 | smallworld d1 h4 | .503 | none | 0 | .50 | 1.0 | 61 | .516 | CAPPED |
| XOR | capped, symmetric | 75779d26 | torus d3 h2 | .500 | none | 0 | .50 | 1.0 | 61 | .500 | CAPPED (+ flat) |
| FLIP | random | f30f89b0 | random d2 h2 | .499 | G6 (noG0) | 0 | .50 | 1.0 | 34 | .615 | CAPPED |
| FLIP | smallworld | b3e89ef5 | smallworld d5 h5 | .508 | G6 (noG0) | 0 | .50 | .878 | 50 | .557 | CAPPED |
| FLIP | symmetric | 64d33b89 | torus d1 h1 | .513 | none | 0 | 1.0 | .977 | 0 | .594 | ADMISSIBLE |
| RELAY | multi-hop random | 94ced72f | random d2 h2 | .500 | none | 0 | 1.0 | 1.0 | 26 | .521 | ADMISSIBLE (partly inert) |
| RELAY | multi-hop smallworld | e553999d | smallworld d3 h3 | .500 | G6 | 0 | 1.0 | .99 | 64 | .500 | INERT + flat (never emits) |
| RELAY | multi-hop ring | 3222a6ff | ring d3 h2 | .544 | G12 (zero_comm arm ONLY) | 0 | 1.0 | .874 | 7 | .599 | ADMISSIBLE |
| RELAY | multi-hop torus | 89bd6fdb | torus d5 h3 | .501 | G12 (normal arm) | 0 | 1.0 | 1.0 | 0 | .615 | ADMISSIBLE (champion dies of energy) |
| MAJ | random | c9d2ff6e | random d5 h3 | .500 | G6 | 0 | n/a | 1.0 | 64 | .500 | INERT + flat |
| MAJ | smallworld | 0327a9ab | smallworld d2 h3 | .500 | G6 | 0 | n/a | 1.0 | 64 | .500 | INERT + flat (never emits) |
| MAJ | ring | 6e0ca725 | ring d1 h1 | .497 | G12 (normal arm) | 0 | n/a | 1.0 | 12 | .599 | ADMISSIBLE (transient champion) |
| MAJ | torus | 87216808 | torus d1 h1 | .546 | none | 0 | n/a | 1.0 | 2 | .552 | ADMISSIBLE |

Guards that never fired in any cell, on either the held block or the final-seed evaluation: G1, G2, G3, G4, G5, G7, G9, G10, G11.

G8 in context cannot fire here, because the re-run has no multi-genome call. I replaced it with a direct check: held seeds against all training and final seeds give 0 overlaps in the 16 cells and in all 678 C1 evolve rows.

Controls were applied: the zero_comm arm delivered 0 packets in 16/16 cells, with attempted > 0 wherever the champion emits.

## 2. VERDICT FRACTIONS (n = 16)
- **BROKEN: 0/16.** One-sided 95% upper bound 17% (Clopper-Pearson).
  - Every gate reproduced.
  - No break-indicating guard fired (G1-G5, G7, G8, G9, G10, G11).
  - Schedule live in both halves of the run.
  - Scorer self-test passed.
  - Right genome evaluated.
  - Disjoint seeds.
  - Control applied.
- **DEGRADED (graph-infeasible worlds): 0/16.** 0 of 1024 held worlds have an unreachable actuator.
- **GENUINE (measurement sound, all worlds graph-feasible): 16/16.**

"Genuine" certifies the measurement, not what it means. Applying the admissibility checklist of section 5:
- **CAPPED, 4/16:** light-cone bound .50, so every world is infeasible by timing. The NULL is forced by physics and carries no search information.
- **INERT, 4/16:** the readout is never written in 50-64 of 64 worlds. Three of these (e553999d, c9d2ff6e, 0327a9ab) are also FLAT: no genome in any generation exceeded .5, so selection only ever saw the shaping terms.
- **ADMISSIBLE for an S/U (search/selection) reading, 8/16:** 6f82f9c7, abb5fb81 (LC .625, marginal), 64d33b89, 94ced72f (26/64 worlds dead), 3222a6ff, 89bd6fdb, 6e0ca725, 87216808. Without the marginal abb5fb81, the strict count is 7/16.

**What this means for H6.**
- W2-C F1 says a broken experiment would read as a silent NULL. In this record that risk is real in principle but did not materialize in the sample: the held and final measurement machinery is sound in 16/16 cells.
- The problem with reading C1 NULLs as search-limited or physics-limited is attribution, not breakage:
  - about 1/4 of the sample is timing-capped;
  - about 1/4 has an actuator-inert champion, mostly from flat searches;
  - only about half are NULLs where a feasible task was searched and a program that engages the actuator was found and still failed.
- Population-level H6 statements must therefore be made per cell, after the checklist. The "physics" share comes mostly from the light cone, not from reachability or broken instruments.

## 3. FINDINGS
(Each finding has a tag ([V] verified by me with a check, [I] inferred), a confidence, the strongest objection, and what remains unresolved.)

**F1 [V, high]. No sampled C1 NULL is a broken experiment (0/16; upper bound 17%).**
- Evidence: section 0 and the section 1 alarm set.
- The guarded re-run used the current code and reproduced the recorded rows bit-for-bit, including telemetry and final ranking.
- Objection 1: the guards only detect the corruption classes they model. randomize_source has no in-situ guard (W2-C F9), and G11 counts packets "delivered" at emission, so it misses later destruction (W2-A1).
- Objection 2: a deterministic bug present in both the recording run and the re-run would reproduce. The guards and the feasibility checks are the defence against that, and they were clean.
- Objection 3: the search generations themselves were not re-run. Only the final ranking evaluation and the held block were.
- Unresolved: the 454-NULL population beyond 16 cells. The cost is about 11 CPU-s per cell, so all 454 would take about 1.4 core-hours.

**F2 [V, high]. G12_STATE_LIVE false-alarms on the zero_comm control World.**
- It fired on NULL 3222a6ff and on 2/4 recorded SIGNAL negative controls (1d88af70 RELAY, 0a23398f MAJ), each time from the zero_comm arm only (per_arm_guards.py).
- G12 does not exempt control Worlds; G11 does. Under zero_comm, a comm specimen's readout legitimately goes quiet.
- Fix: NEUTRAL patch, see section 4.
- Objection: one could argue G12 should also watch control arms. Answer: a control is meant to perturb, so its liveness is not an invariant.

**F3 [V, high]. The two normal-arm G12 alarms are champion properties, not broken experiments.**
- 89bd6fdb: emissions 2424 in the first half and 0 in the second; final energy 0. Economy high, c_op 1, readout last changes at about tick 11. This is energy death (W2-A1: ops always cost, energy gates only emission).
- 6e0ca725: emissions continue (304 in the second half), energy .79, readout stops at about tick 28. This is a transient champion.
- In both cells the schedule delivers 12/12 cue ticks in each half, and per-trial accuracy is at chance in BOTH halves (.501/.500 and .486/.508). The dead half hides no competence, so the NULL stands.
- Objection: G12 with this rule cannot tell "frozen by a bug" from "frozen by the champion". The per-half accuracy test is what separates them (checklist item A4).

**F4 [V, high]. Actuator reachability is almost never the problem in C1.**
- In the held worlds of all evolve rows in XOR/FLIP/RELAY/MAJ:
  - impossible worlds: XOR 0/5312, FLIP 0/5248, RELAY 0/9344 (NULL) and 0/3200 (SIGNAL);
  - MAJ NULL: 16/9152 (0.17%), all in 5 of the 15 random-topology MAJ NULL cells (at most 4/64 per cell; each of those actuators has no in-edge).
- Re-scoring those 5 cells on feasible worlds only moves held accuracy by at most .0003.
- W2-A1's XOR reachability hole (envs.py:195) is real in code but never occurs in C1 held worlds. RELAY and FLIP are safe by construction, because _pick_at draws from M[s].
- Objection: W2-A1 measured 2.5% on A0 plant worlds, a different population, so the figures are consistent.
- Check: python reach_census.py.

**F5 [V for the counts, I for the reading]. Wake loss is a feasibility cap that H-PLANT's light cone omits.**
- lightcone.py treats async as "could wake any tick", which is optimistic. In the engine, SENSE is never latched, so a cue that lands while the sensor sleeps is lost.
- Measured cue reception was .747-.77 at update_p .5 and .95-.98 at update_p .8. The analytic value 1-(1-p)^2 gives .75 and .96, so they match.
- Analytic ceilings over C1 NULLs: XOR 15 cells at .781, FLIP 21 at .875, RELAY 18 at .875.
- RELAY SIGNAL appears in 0 of the 18 async update_p .5 RELAY rows, against 50/196 overall [V count]. This is confounded with other levels [I].
- The ceilings stay above the SIGNAL bar, so none of these is CAPPED. But they should be combined with the light cone into one bound.

**F6 [V, high]. "Search failed" means different things across the NULLs.**
- INERT champions in 7/16 sampled cells: readout dead in ≥ 50/64 worlds. Two of them never emit.
- FLAT searches, where training max_acc never exceeded .5 in 36 generations: 4/16 in the sample, and 49/454 C1 NULLs (10.8%): XOR 14, FLIP 2, RELAY 17, MAJ 16.
- In a flat search no genome ever produced input-dependent actuator output, so selection was driven only by the shaping terms (W2-D F7, W2-A2 F1).
- G6 fired in 5 cells: the zero_comm control is a no-op there because the champion is local or silent, so it is NOT_APPLICABLE rather than broken.
- Unresolved: how to tell flat-because-capped from flat-because-search-starved in the uncapped cells.

## 4. PROPOSED FIX
patches/g12_exempt_controls.NEUTRAL.diff: G12 now judges only Worlds whose ctrl.label() == "none". It targets W2-C's guards.py, which is a proposed module, not frozen semantics. Classification: **NEUTRAL**.

Tests:
- tests/test_g12_control_exempt.py:
  - test 1: G12 must stay silent on the held block of SIGNAL 1d88af70; this runs with a known-answer assert;
  - test 2: G12 must still fire on the dead normal arm of 89bd6fdb.
- Results:
  - on current code (`W2O_GUARDS=W2-C python -m pytest tests/test_g12_control_exempt.py`): 1 failed, 1 passed;
  - patched (`python -m pytest tests/test_g12_control_exempt.py tests/test_guards_w2c_on_patched.py`): 17 passed. This includes all 15 of W2-C's must-fire and clean-run guard tests, freeze_state -> G12 among them.

## 5. NULL ADMISSIBILITY CHECKLIST (required before any H6-type reading)

A. Measurement integrity (any failure means BROKEN: the result is not a NULL)
1. Known-answer replay: held acc, lo99, hi99, zero_comm, comm_delta and champ_train_final reproduce exactly from the row and the code.
2. Guards G1-G5, G7, G9, G10 and G11 are silent on the held block (normal plus controls) and on the final-ranking evaluation.
3. Direct G8: held seeds are disjoint from every training-generation and final seed set.
4. G12 runs on the NORMAL arm only (patched). If it fires, compare per-trial accuracy in the first and second halves:
   - first half at chance: the result is admissible, and the champion property (energy death, transient) is recorded;
   - first half above chance: the result is TRUNCATED, i.e. inadmissible as a NULL.
5. Instrument self-checks pass: the wake recomputation equals engine awake counts, and the scorer self-test (G10) passes.

B. Feasibility
6. Directed reachability: count impossible worlds (RELAY/FLIP: the sensor; XOR: both sensors; MAJ: any sensor). If the count is above 0, the cell is DEGRADED; report held accuracy on feasible worlds only.
7. Light-cone bound ≥ SIGNAL bar + margin (suggest ≥ .75); otherwise the cell is CAPPED. Between .57 and .75, flag it as marginal.
8. Combine the wake/cue-reception ceiling with the light cone (async is currently optimistic).

C. Interpretation descriptors (needed to choose between S, U and objective)
9. Champion engagement: readout-dead worlds, emitting worlds, and twin-blind pairs. A cell is INERT if ≥ 75% of worlds are readout-dead.
10. Accuracy gradient: max_acc over all generations. If it is ≤ .5 the search is FLAT. If it is below the selector's chance ceiling (about .57, W2-D F7), any competence was invisible to selection.
11. Control applicability: report G0 (degenerate control) and G6 (no-op control). Do not attribute COMM from a vacuous control.
12. A lower bound for "search-limited" claims: a plant inside the genome space at this cell (link R), plus the number of independent search seeds at the condition (W2-D F1 has n = 1 at d9cc FLIP).

Output classes: BROKEN, TRUNCATED, CAPPED, DEGRADED, INERT, FLAT, ADMISSIBLE. Only ADMISSIBLE NULLs that also have a plant feed an S/U attribution.

## 6. DISAGREEMENTS
- **W2-C F1 / section 5 and P-1 section 6.** The concern was that NULLs might be silently broken. On the sample, 0/16 are broken. H6 should not discount NULLs as possibly broken wholesale; its real exposure is CAPPED, INERT and FLAT cells mixed into the NULL population.
- **W2-C G12 (F9).** G12 was certified only on a tiny fixture and false-alarms on real zero_comm arms: 2/4 SIGNAL cells. It needs the patch before it is promoted to fail-closed.
- **W2-A1 F1, "XOR has the same reachability hole".** It is real in code, but there are 0 cases in C1 held worlds. The MAJ effect on C1 NULL held worlds is 0.17% (16/9152 worlds), not 2.5%, and immaterial to any label.
- **H-PLANT lightcone.py.** It is optimistic on async wake: it assumes a sensor that is always awake. Wake loss alone caps 54 NULL cells at ≤ .875.

## 7. NEXT QUESTIONS (ranked)
1. Run null_audit.py over all 454 NULL evolve cells (about 1.4 core-hours) to turn "0/16 broken" into a population rate, and tally CAPPED/INERT/FLAT/ADMISSIBLE per family.
2. Build one combined light-cone + wake bound per world and trial (extend lightcone.py with the exact wake mask). How many cells currently bounded at 1.0 drop below .75?
3. Among uncapped FLAT cells (about 49 NULLs), is the cause a search starved by the objective (shaping drives selection) or an actuator unreachable within budget? Check whether any random genome at 10x population produces input-dependent actuator output.
4. Energy death (89bd6fdb): how many NULL champions at economy high/low exhaust energy before the second half (an E-trace guard)? Is "economy" a physics cap on competence that C1 reads as search failure?
5. Add a guard for packet provenance (randomize_source) and a delivered-to-inbox counter, then re-audit the same 16 cells.
6. 3222a6ff (held .544, multi-hop ring, async p .5, ceiling .874) is the closest NULL to SIGNAL in the sample. Would a held set of 256 worlds or a 10x search budget cross the bar, i.e. is this a partial-competence cell?
7. Why do the RELAY SIGNALs avoid async update_p .5 entirely (0/18)? Run a controlled transect on update_p with the other levels held fixed.

## 8. INFERENCE LEDGER
(question | evidence | result | confidence | strongest objection | unresolved | next)
- Do sampled NULLs reproduce? | gate on 6 held fields + final + held_tel, 16 cells | 16/16 exact | high | current code vs recorded code_sha | none | -
- Are any sampled NULLs broken? | W2-C guards on held + final, direct G8 | 0/16 (upper bound 17%) | high | guards cover modelled corruptions only | population rate | Q1
- Is G12 trustworthy? | per-arm attribution, 4 SIGNAL negative controls | false-alarms on zero_comm arms (2/4 SIGNAL) | high | control liveness might matter | - | patch applied in copy
- Do normal-arm G12 alarms hide competence? | per-half accuracy, emissions, energy | no; chance in both halves | high | n = 2 | energy-death prevalence | Q4
- Are actuators reachable? | reach census, all evolve rows | XOR/FLIP/RELAY 0; MAJ 0.17% (5 random cells) | high | held worlds only, not training worlds | training-world reachability | -
- Is the light cone tight? | exact wake recomputation, analytic ceilings | optimistic on async; caps .78-.875 | medium-high | ceilings stay above the SIGNAL bar | combined bound | Q2
- What fraction of NULLs is H6-admissible? | checklist on 16 | 8/16 (strict 7/16); 4 CAPPED, 4 INERT (3 also FLAT) | medium | n = 16, stratified rather than random | population | Q1, Q3
- Do flat searches exist? | curve max_acc over all rows | 49/454 NULLs never exceed .5 | high | max over 8 worlds is noisy | cause in uncapped cells | Q3

## 9. COMPUTE
- About 545 CPU-s, about 0.15 core-hours, against a 0.5 cap. Breakdown in out/compute_ledger.json.
- Measured items: audit 172 s, first gate 30 s, final check 45 s, SIGNAL panel 43 s, census 74 s, G8 1 s.
- Estimated items: G12 diagnosis about 50 s, per-arm about 60 s, pytest about 60 s.
- CPU only, torch.cuda.is_available() asserted False, at most 2 threads, eager evaluation, every run under 10 minutes of wall time.
- No leases touched, no GPU used, no files outside W2-O edited, no git writes.
