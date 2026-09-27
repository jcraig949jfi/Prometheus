# z80atlas adversarial audit (read-only)

Code: `D:\Prometheus-worktrees\bellerophon-post-campaign-forensics\prometheus\z80atlas\` (identical modulo CRLF to
`C:\Users\James\z80atlas_campaign_2026-09-19\code\prometheus\z80atlas\`; checked file by file).
Evidence: `C:\Users\James\z80atlas_campaign_2026-09-19\` (63,247 runs; ticks 500, cells 256, seed 20260919; no resume
decision was ever logged; every runs.jsonl row has a complete run directory).
Scratch scripts (all executed): `C:\Users\James\AppData\Local\Temp\claude\D--prometheus\9e74888e-eb5f-4aeb-a9e2-53ac5b98f3b9\scratchpad\audit\`
(r_vm.py, r_world.py, r_gated.py, r_solver.py, r_geo_paired.py, a1..a14*.py). Run them from any directory; each
inserts the worktree root on sys.path.

Flag counts in flags.json: REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK 600, REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY 493,
REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL 393, REACHED_INCREMENTAL_NOT_ATOMIC 136, RESERVOIR_CROSSED_MOAT 7.
My re-implementation of the flag logic reproduces 393/136/7 exactly (a2_symmetry.py), and it reproduces the
beneficial-density gain for 147/150 flagged runs (a8_geo.py).

Bottom line: I can explain every one of the five high-value flag families with an implementation defect or
measurement artifact that is enough to produce it on its own. No flag survived an attack that I could run.

---------------------------------------------------------------------------------------------------------------
## Summary table

| ID | Sev | Status | One line |
|----|-----|--------|----------|
| C1 | CRITICAL | CONFIRMED | "Tail" metrics are read from the last 20 ticks before EXTINCTION, so seeded solvers alive before collapse count as "reached". 90/393 ENDO flags come from arms that went extinct. |
| C2 | CRITICAL | CONFIRMED | "Solver" means score_ema >= 0.85, not "solves". INCREMENTAL accepts answers off by up to 19. ATOMIC half-right programs reach 0.85 about 5% of the time by luck. |
| C3 | CRITICAL | CONFIRMED | REACHED_INCREMENTAL_NOT_ATOMIC compares a near-miss metric with an exact one. 24/31 flagged runs examined contain no exact solver. |
| C4 | CRITICAL | CONFIRMED | The RESERVOIR arm alone has an easy ECHO niche 0, and its solvers are counted there. 6/7 RESERVOIR_CROSSED_MOAT flags are ECHO solvers in niche 0. The 7th is an ECHO witness getting lucky on COND_MULTI. |
| C5 | CRITICAL | CONFIRMED | moat_crossing fires when the crossing happened on a different, easier task (RESERVOIR, PER_NICHE, SHIFT), on CONST under FORCED, and on seeded solvers. The trigger fires in 48% of all runs. |
| C6 | CRITICAL | CONFIRMED | Beneficial density is not paired and rests on 3 inputs. Scanning the SAME tape with the runner's two seeds gives a "gain" > 0.1 in 82/150 flagged contexts. |
| C7 | CRITICAL | CONFIRMED | REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK is a seeded hybrid taking over from a random first replicator that had a long pc_max excursion: 579/600 have seed_lineage_share >= 0.9 and 531/600 have an unseeded first replicator. |
| C8 | CRITICAL | CONFIRMED | Capture births: writing 1 byte into an occupied partner (PARTIAL/PAIR, and OVERWRITE at L/2) counts as the writer's birth, with fidelity measured against the TARGET (0.984, which is "hifi"). The target is also rejuvenated. |
| C9 | CRITICAL | CONFIRMED | spontaneous_replication fires on transplant and environment-swap interventions (vec init RANDOM plus init_tapes): 42/544, most with seed_lineage_share = 1.0. |
| M1 | MAJOR | CONFIRMED | Copy fidelity is measured against the writer's POST-execution tape. Self-smearing makes constant or periodic tapes score fidelity 1.0. 59 first replicators in spontaneous runs are constant tapes. |
| M2 | MAJOR | CONFIRMED | LDIR with C=0 does a 256-byte wrap copy of the whole address space, and writes are counted even when the byte is unchanged. A single LDIR at reset "writes" all L window bytes while changing nothing. |
| M3 | MAJOR | CONFIRMED | The endogenous-vs-EXTERNAL arms are not one-axis flips: EXTERNAL offspring get 4x mutation, and there is no task selection under IMPLICIT/NOVELTY/QD/METABOLIC/EXPLOIT. 383/393 ENDO flags are in those pressures, and 361/393 are seeded inits. |
| M4 | MAJOR | CONFIRMED | Flags use any() over unequal run counts with no seed pairing. The reverse direction (EXT solved, ENDO not) occurs 1596 times against 393 forward. 227/393 flags rest on a single run. |
| M5 | MAJOR | CONFIRMED | Family id (vec_id) ignores init_tapes, so transplant runs are pooled into ordinary families. 2224 families are mixed. 13 INCR flags are solved only by transplant runs. |
| M6 | MAJOR | CONFIRMED | Late-stage matched controls are seeded with specs[0], which is another family's seed: 5156/6859. |
| M7 | MAJOR | CONFIRMED | GATED_INTERACTION: organisms that skip interaction never age or pay costs. Result: 0 deaths in 120 ticks. |
| M8 | MAJOR | CONFIRMED | Promotion triggers are near-universal or noise: cross_niche_transport 91% of NICHES runs, novel_architecture 92% of endo replicating runs, escape 96% without sustained solvers. 63% of families were promoted. |
| M9 | MAJOR | CONFIRMED | Geometry is measured on the task at the END of the run and in niche 0 (ECHO for RESERVOIR/PER_NICHE, a shifted task under SHIFT). The isolated "replicates" test is trivially met by near-zero tapes under PARTIAL. |
| m1 | MINOR | CONFIRMED | 48 (vec, seed) pairs were submitted twice or more (49 extra runs), all byte-identical simulations counted as replicates. config_sha256 hashes id/parents/reason, so it cannot detect this. |
| m2 | MINOR | CONFIRMED | COPYALL overruns the budget (budget 3 gives 11 steps). |
| m3 | MINOR | CONFIRMED | SEPARATED layout drops tr2.pc_max, so the recorded repro span covers only the first half (it can be 1). |
| m4 | MINOR | CONFIRMED | Two positive controls share one family id and the grading loop keeps only the last run. The witness_const check is vacuous. |
| m5 | MINOR | CONFIRMED | 80% of opcodes are NOPs. The PC leaves its own tape in 69% of random tapes and executes the IO region in 53%, so organisms run partner or input bytes. Only a small share of flagged solvers depend on this. |
| m6 | MINOR | CONFIRMED | Extinct runs still fire the replication trigger (28 runs). |
| s1 | MINOR | SUSPECTED | A newborn can act in the tick it is born (chain births within one tick). |
| s2 | MINOR | SUSPECTED | Trigger values depend on ingest order (imap_unordered; control summary and archive are read at ingest time). |
| s3 | MINOR | SUSPECTED (latent) | Resume path: in-flight run directories get reused or overwritten, promotions are not replayed, and a truncated runs.jsonl line breaks resume. Not exercised in this campaign. |
| s4 | MINOR | SUSPECTED | The FORCED gate only counts IN_A as a read. LD A,(S) reading the input region directly is scored 0 (a false negative). |
| s5 | MINOR | SUSPECTED | high_value_flags builds the control vec without repair() while _control_summary uses repair(), so control identity is inconsistent. |

Checked and found OK: replay from config.json alone is byte-identical for 3 runs (r000100 EXTERNAL,
r030000 PAIR_EXECUTION, r048779 intervention with 4 init_tapes; a3_replay.py). The 9 reservoir replays in a9 also
reproduced the stored solvers_tail. No parent/offspring bytearray aliasing (every child, migrant copy and seed is
a fresh bytearray). World RNG use is deterministic (the standing-variation RNG is separate). No integer-width
problems (8-bit registers are masked, seeds are Python ints). state.json is written atomically. Evidence set is
complete (63247 rows = 63247 dirs, sampled dirs have every core file).

---------------------------------------------------------------------------------------------------------------
## CONFIRMED findings

### C1 CRITICAL: tail metrics are read from the pre-extinction window
- Where: world.py:672-678 (run() breaks at extinction), world.py:686-701 (`tail = logs[-20:]`, `solvers_tail = mean("solvers")`), observatory.py:283 (task_score), observatory.py:318-319 (solved()).
- Mechanism: when a run goes extinct at tick t, the "tail" is ticks t-20..t, not the end of the 500-tick horizon. Under ENDOGENOUS physics a seeded witness does not replicate, so it lives until lifespan 40. Its last 20 ticks count as a sustained solver. The EXTERNAL control can never go extinct, because the manager refills it, and in it the seeded witnesses are diluted by drift.
- Evidence (a1/a2 plus an inline query): 616 runs have solvers_tail >= 1 and extinct = True, and all 616 fire task_score. In 90/393 REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL flags, every solving treatment run ended EXTINCT, while in all 393 every control run survived. Examples are ENDOGENOUS_COPY + SEEDED_WITNESS: r000031, r000536, r001028, r003480, r004063 (solvers_tail 3-15, final_alive 0, endogenous_births 0).
- Contaminates: REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL, REACHED_INCREMENTAL_NOT_ATOMIC (5), task_score, task_reproduction_coupling, replication (28 extinct runs).
- Test that would fail today: build a World with ENDOGENOUS_COPY, SEEDED_WITNESS, ticks=200. Assert that `summary["extinct"]` implies `summary["solvers_tail"] in (0, None)` (or that the tail spans the configured horizon).

### C2 CRITICAL: a "solver" is not a solver
- Where: world.py:346 (EMA 0.7/0.3), world.py:619 (`solvers = #score_ema >= 0.85`), world.py:357 (first_crossing), tasks.py:82-83 (INCREMENTAL credit `1 - d/128`).
- Mechanism: (a) under INCREMENTAL, an output within 19 of the target scores >= 0.852, so a constant off by 19 is a "solver". On COND_ONE the plain ECHO program scores >= 0.992 on every input. On COND_MULTI it averages 0.75. (b) Under ATOMIC, a program that is right on half the inputs (ECHO or INC on COND_ONE, ECHO on COND_MULTI) hits 6 lucky inputs in a row often enough to have score_ema >= 0.85 in about 5% of organism-ticks. With about 200 such organisms that is about 10 "solvers" per tick, and solvers_tail >= 1 only needs one.
- Repro (r_solver.py, 200k interactions): P(ema >= 0.85) = 0.049 (ECHO/COND_ONE), 0.048 (INC/COND_ONE), 0.051 (ECHO/COND_MULTI); first "crossing" came after 26-106 interactions. INCREMENTAL: x+19 scores 0.852 and counts as a solver.
- Evidence (a4_moat.py): among 492 sampled first-crossing tapes on a configured hard task (COND_ONE/COND_MULTI/SUM2), only 126 are exact (>= 0.99 isolated accuracy). 291 are 0.4-0.99 and 75 are below 0.4.
- Contaminates: every flag that uses solved(), plus task_score, task_reproduction_coupling, moat_crossing and first_crossing.
- Test: `score_ema` process for `vm.witness_echo()` on Task("COND_ONE") under ATOMIC over 256 cells x 200 ticks. Assert solvers_tail < 1. Also assert `score(Task("ECHO"), [x+19], [x], "INCREMENTAL", ...) < solver threshold`.

### C3 CRITICAL: REACHED_INCREMENTAL_NOT_ATOMIC compares incommensurate metrics
- Where: observatory.py:333-337 with solved() at observatory.py:318-319.
- Mechanism: the treatment arm's "solved" accepts answers within 19 of the target (C2a). The ATOMIC arm needs exact answers. The flag fires when near-misses exist and exact answers do not, which is exactly what partial credit produces by definition.
- Evidence (a14_incr.py): in 31 flagged runs (SHARED, non-reservoir, non-shift), 24 have NO exact solver among the final snapshot's top-12 tapes. Among incremental-solver tape copies, 346 are not exact and 237 of those are below 10% exact. Also 13/136 flags are solved only by transplant intervention runs (M5), and 5 by extinct arms (C1).
- Test: for each INCREMENTAL "solved" run, re-score the solver tapes under ATOMIC. Assert the flag fires only when ATOMIC accuracy is >= 0.99.

### C4 CRITICAL: RESERVOIR_CROSSED_MOAT counts ECHO solvers in the reservoir niche
- Where: world.py:121-123 (`env.tasks[0] = Task("ECHO")` only when spatial == RESERVOIR), world.py:619 (solvers counted over ALL alive organisms, in every niche), observatory.py:339-343 (control = NICHES_ISOLATED, which has no ECHO niche). Also world.py:185/188: SEEDED_WITNESS and SEEDED_HYBRID use `self.env.task_for(0)`, which is ECHO for RESERVOIR, so a COND_MULTI or SUM2 reservoir family is seeded with the ECHO witness.
- Repro (a9_reservoir.py): I replayed each flagged treatment run and attributed tail solvers to niches. The replays reproduce the stored solvers_tail.
  - r016318 COND_MULTI: niche0:ECHO 1.0 (all of it)
  - r017514: niche0:ECHO 3.1, COND_MULTI 0.3
  - r019986 SUM2: niche0:ECHO 1.0
  - r033424: niche0:ECHO 19.25 of 20.9
  - r036574: niche0:ECHO 9.35 of 10.3
  - r038218 SUM2: niche0:ECHO 22.35 of 22.35
  - r023606 SEEDED_HYBRID COND_MULTI: 1.3 COND_MULTI solvers. Its seed is the ECHO witness (the hybrid uses task_for(0) = ECHO), so these are ECHO programs meeting the 0.85 EMA by luck (C2b).
- Contaminates: all 7 RESERVOIR_CROSSED_MOAT flags, and moat_crossing for RESERVOIR runs.
- Test: in a RESERVOIR world with SEEDED_WITNESS and task COND_MULTI, assert the seeded witness is the COND_MULTI witness. Assert the solvers metric excludes niche 0, or that the control also has an ECHO niche 0.

### C5 CRITICAL: moat_crossing is mostly not a moat crossing
- Where: observatory.py:284, world.py:357-359, tasks.py:96-98 (PER_NICHE: niche 0 of a COND family is ECHO), tasks.py:110-117 (SHIFT cycles ECHO->INC->COND_ONE->COND_MULTI), tasks.py:58-59 and 70 (CONST ignores FORCED).
- Mechanism: first_crossing is recorded on whatever task the crossing organism's niche has at that tick. The trigger checks only the vec's configured task or read_gate. It also accepts CONST+FORCED (no gate applies to CONST) and seeded solvers.
- Evidence (a4_moat.py, a13, plus an inline query): moat_crossing fires in 30470/63247 runs (48%).
  - In a 1500-run sample, 259 crossed on a task other than the configured one (ECHO 198, INC 23, COND_ONE 22, COND_MULTI 10).
  - 3361 fired with task CONST.
  - 18083 have SEEDED_WITNESS or SEEDED_HYBRID init.
  - Even on-task crossings are mostly partial solvers (C2).
- Test: a RESERVOIR or PER_NICHE COND_MULTI run whose only solvers are niche-0 ECHO programs must not set moat_crossing. A CONST+FORCED run must not set moat_crossing.

### C6 CRITICAL: beneficial-density gain is unpaired sampling noise
- Where: geometry.py:167-192 (_eval draws 3 fresh inputs from the shared rng on every call), geometry.py:199-216 (base is evaluated once on 3 inputs, then each mutant on 3 different inputs; "better" means a higher 3-input mean), runner.py:298/311/314 (gain = scan(top, seed*31) - scan(first_rep, seed*43)), observatory.py:350 (threshold 0.1).
- Mechanism: one 3-input base draw anchors all 40 comparisons. If the base draw is unlucky, most behaviourally neutral mutants count as "beneficial". Two different tapes are scanned under different seeds, and the difference of two such correlated proportions is compared with 0.1.
- Repro 1 (a8_geo.py, identity null): for 150 flagged runs I scanned the SAME top tape with the runner's two seeds (seed*31 and seed*43). Gain > 0.1 in 82/150, < -0.1 in 39/150. The null ranges from -0.85 to +0.85. In 49/150 flagged runs the first replicator's base score was 0.0.
- Repro 2 (r_geo_paired.py): the ECHO witness padded with HALT, scanned against itself over 200 seeds: beneficial_density ranges from 0.000 to 0.925 (COND_ONE ATOMIC). Same-tape "gain" > 0.1 in 67/200 seeds (COND_ONE) and 70/200 (COND_MULTI).
- Contaminates: all 493 REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY flags, and map.json accessibility_gain.
- Test: `scan(t, cfg, task, s1)["beneficial_density"] - scan(t, cfg, task, s2)["beneficial_density"]` must be 0 for identical t (paired, common inputs). This fails today for the padded ECHO witness on COND_ONE.

### C7 CRITICAL: REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK is a seeded takeover plus a span artifact
- Where: observatory.py:281 (compression = tail span <= 0.7 x FIRST replication span), observatory.py:282 (coupling = rr >= 0.05 AND solvers_tail >= 1 in the same run, with no fidelity or causal link), observatory.py:345-348 (flag = both). world.py:434 (span = pc_max + 1, the maximum PC over the whole execution, including excursions through the partner window, scratch, IO and wrap). world.py:275-286 (SEPARATED keeps only tr1's pc_max; see m3).
- Evidence (a13_triggers.py plus an inline query) over the 600 flag runs:
  - init: SEEDED_HYBRID 579, SEEDED_REPLICATOR 19, SEEDED_WITNESS 1, RANDOM 1
  - seed_lineage_share >= 0.9 in 579/600
  - first replication NOT seeded in 531/600: a random organism replicated first, with a long span, and the seeded hybrid (span about 10) then took over
  - first-replication span >= 224 (the PC executed the IO region) in 214
  - SEPARATED in 119
  - coupling with mean_fidelity_tail < 0.9 in 39
- The same compression artifact appears in 1323/5710 compression-trigger runs, where span0 >= 224.
- Test: SEEDED_HYBRID with ENDOGENOUS_COPY where a random organism replicates first must not produce reproductive_compression. Span must not include PC excursions outside [0, L).

### C8 CRITICAL: capture births yield "high-fidelity replication" from 1-byte writes
- Where: world.py:406-408 (ENDOGENOUS_PARTIAL is viable with >= 1 byte), world.py:330-337 (PAIR_EXECUTION: ANY change to b is a birth, with no L/2 threshold), world.py:421-433 (if the child resembles the target more, fidelity := fid_target, and the WRITER is credited with replications, fidelity_last and repro_span). world.py:431 (the "child" gets fresh energy and age 0, so being written to rejuvenates the target).
- Repro (r_world.py):
  - R2: under PARTIAL, a writer running `LD T,70; LD (T),A` into an occupied random partner gives births 1, captures 1, writer.fidelity_last 0.984, first_replication.seeded False.
  - R2b: a 4-byte program writing into an EMPTY cell gives an all-zero child with fidelity 0.938, counted as "hifi".
  - R3: under PAIR_EXECUTION a 1-byte change in b gives writer fidelity_last 0.984 and captures 1.
- Evidence (a5_repl.py, 544 spontaneous_replication runs):
  - captures/endogenous_births > 0.5 in 58/201 ENDOGENOUS_PARTIAL runs and 23/62 PAIR_EXECUTION runs
  - material = "target" in 19574 of 55050 PARTIAL copy events and 5993 of 16485 PAIR events (first 400 events per run)
- Contaminates: replication, spontaneous_replication, novel_architecture, task_reproduction_coupling, persistence (targets never age out), and REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK through coupling.
- Test: ENDOGENOUS_PARTIAL, a writer writes 1 byte into an occupied partner. Assert that writer.replications == 0, or that fidelity_last < hifi.

### C9 CRITICAL: spontaneous_replication fires on seeded interventions
- Where: observatory.py:279 checks only `vec["init"] == "RANDOM"` and `first_replication.seeded`. scheduler.py:283-291 creates transplant and environment-swap specs whose vec keeps init RANDOM while init_tapes carries a quarter of the population. world.py:442 checks seed status only for the FIRST replication; the tail rate and fidelity can come entirely from the seeded lineage.
- Evidence (a5, a6): 42/544 spontaneous_replication runs are intervention runs. Their seed_lineage_share is 1.0 in 31 of them and >= 0.5 in 41.
- Test: a World with init RANDOM and init_tapes=(replicator hex,) where the replicator lineage drives the tail. Assert that spontaneous_replication is False.

### M1 MAJOR: fidelity is measured against the writer's post-execution tape
- Where: world.py:341 (`o.tape = mem[:L]` before _apply_reproduction), world.py:414. Also world.py:334-336 for PAIR.
- Repro (r_world.py R4): `LD S,63; LD T,0; LD C,128; LDIR` erases the writer and the window to the same bytes. Result: fidelity 1.000, the writer's tape has 1 unique byte, and the child equals the writer's post-execution tape.
- Evidence (a7_period.py): among the first replicators of non-intervention spontaneous runs, 59 are constant tapes (period 1) and about 60 more are periodic (period 2-32). These are smears that reproduce "exactly" only because both sides were overwritten.
- Test: a tape that overwrites itself and the window with a constant must report fidelity measured against its pre-execution tape (much less than 0.9).

### M2 MAJOR: VM LDIR semantics and write accounting
- Where: vm.py:133-141 (C=0 runs through 256 bytes, the whole address space including own tape and IO), vm.py:100-113 (`writes[addr]` is recorded even when the value is unchanged; neighbour_writes and copy_events count unchanged bytes).
- Repro (r_vm.py R1): a bare `LDIR` at reset registers (S=T=C=0) gives steps 256, all 64/64 window addresses "written", 0 bytes changed, neighbour_writes 64, copy_events 64. The ENDOGENOUS_COPY viability rule (all L written) is met. With an empty target the child is all zeros. R1d: a zero tape runs into the IO region and executes the input byte as an opcode.
- Evidence (a6_spont.py): of the first replicators in non-intervention spontaneous runs, 152/219 (ENDOGENOUS_COPY) and 88/182 (PARTIAL) write at least 200 addresses, i.e. a wrap LDIR. 145/219 of the top ENDOGENOUS_COPY specimens are wrap-LDIRs that also corrupt the input region.
- Test: `execute` of `[LDIR, HALT]` with S=T=0 must not report 64 neighbour writes, or viability must count only changed bytes.

### M3 MAJOR: the endogenous-vs-EXTERNAL control is not a one-axis flip
- Where: world.py:470 (external offspring are mutated at `mut_rate * 4`; endogenous copies are exact bytes plus background), world.py:482-490 (EXTERNAL selection weights are uniform or task-independent under IMPLICIT, METABOLIC, EXPLOIT, NOVELTY, QD), world.py:496-497 (ENDO+EXPLICIT/MINIMAL inflow is 1 + 2s; EXTERNAL+EXPLICIT is 1 + 0.5s plus selection weights).
- Evidence: in REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL the pressures are NOVELTY 117, IMPLICIT 91, QD 65, METABOLIC 64, EXPLOIT 46 (383/393 have no task-based reproduction in the EXTERNAL arm). init is SEEDED_* in 361/393, and among the seeded solved treatment runs seed_lineage_share >= 0.9 in 518/638. So the flag measures "a seeded solver is diluted faster under 4x-mutation uniform resampling". Of the 32 RANDOM-init flags, 27 are INCREMENTAL (C2/C3).
- Test: a SEEDED_WITNESS world, EXTERNAL vs ENDOGENOUS_COPY, IMPLICIT pressure. Assert that offspring mutation rates are equal across arms (or document and pair them).

### M4 MAJOR: flag statistics use any() over unequal, unpaired run sets
- Where: observatory.py:318-319 and 326-343.
- Evidence (a1, a2):
  - ENDO flags: treatment has more runs than control in 261/393; the control has exactly 1 run in 148; a single solving run carries the flag in 227
  - forward (flagged) 393 vs reverse (EXTERNAL solved, ENDO not) 1596
  - INCR: 136 forward vs 76 reverse; RESERVOIR: 7 vs 2
  - replicate disagreement on "solved" within a family is 10.7% (862/8028 families with >= 2 runs), so thousands of pairs guarantee hundreds of one-sided flags
- Test: the flag must be invariant to adding extra fresh-seed replicates to the treatment arm only.

### M5 MAJOR: family identity ignores init_tapes
- Where: grammar.py:109-110 (vec_id hashes AXES only), scheduler.py:104-111 and 283-291 (transplant or swap specs join the family of their vec).
- Evidence (a2, a10): 2224 families mix intervention runs (with init_tapes) and ordinary runs. The treatment is solved only by intervention runs in 13 INCR flags and 5 ENDO flags. 219 ENDO flag controls contain transplant runs; these mostly suppress flags, and 466 ENDO flags appear when interventions are excluded from both arms. _attribution and "fresh seed" verification pool them as well.
- Test: `_spec(v, ..., init_tapes=[x])` and `_spec(v, ...)` must yield different family ids.

### M6 MAJOR: late matched controls get another family's seed
- Where: scheduler.py:280, `seed=specs[0]["seed"]`. specs is the whole batch, so every family after the first in a batch gets the first family's seed.
- Evidence (a10_sched.py): 5156 of 6859 late matched controls are seeded with a seed that is not their own family's fresh-seed value (1703 correct).
- Test: in `_late_batch` with two planned families, assert each control's seed is in that family's own verification seeds.

### M7 MAJOR: GATED_INTERACTION organisms that skip interaction are immortal
- Where: world.py:320-324 (`continue` before age and cost), world.py:360-363.
- Repro (r_gated.py, ENDOGENOUS_COPY, 64 cells, 120 ticks): IMPLICIT had 108 deaths, max age 40, 20 alive. GATED_INTERACTION had 0 deaths, 58 alive, and a max time alive of 120 ticks against lifespan 40.
- Contaminates: persistence, coexistence, alive_fraction comparisons, and the gated_vs_ungated control.
- Test: under GATED_INTERACTION, every organism alive at tick 100 must satisfy (tick - birth) <= lifespan.

### M8 MAJOR: promotion triggers are near-universal or noise, so exposure is unequal
- Where: observatory.py:286 (cross_niche_transport needs >= 0.05 x cells migrations over the whole run), 280 (novel_architecture: >= 3 distinct opcode-position prefixes, true for any mixed population), world.py:626-633 (escape uses EMA-of-max noise), observatory.py:296-302 (novelty: Hamming >= 24 of 64 bytes against the archive; random-bodied tapes are always far), scheduler.py:159 (promote at score >= 2).
- Evidence (a13):
  - cross_niche_transport: 91.4% of NICHES runs with migration
  - novel_architecture given endo and rr >= 0.05: 19253/20830
  - escape: 12872 runs, 12413 of them with solvers_tail < 1
  - novelty_distance: 24.7%
  - promoted families: 31196/49412 (63%)
  - most common promotion reasons: "moat_crossing, cross_niche_transport" 4491 and "escape, cross_niche_transport" 1571
- Test: on a population of random tapes in NICHES_LOW_MIG, assert trigger_score < 2.

### M9 MAJOR: geometry measured on the wrong or post-treatment task, with a trivial "replicates" check
- Where: runner.py:294 (`w.env.task_for(0)` at run END, niche 0), geometry.py:185-190.
- Mechanism: RESERVOIR and PER_NICHE geometry is always ECHO. SHIFT geometry uses the task at tick 500, not the one the lineage was selected on. Under PARTIAL, "replicates" needs 1 written byte plus fidelity >= 0.9 against a zero window, so any tape with at least 58 zero bytes "replicates" in isolation. I confirmed by code and the R2b mechanism. The 3/150 non-reproduced gains in a8 are RESERVOIR runs where env_history[-1] still says the configured task while geometry used ECHO.
- Test: for a RESERVOIR COND_MULTI run, geometry.json's task must be COND_MULTI.

### m1 MINOR: duplicate submissions and a non-identity config hash
- Where: scheduler.py:278-280, runner.py:280-283 (the hash includes id, parents and reason).
- Evidence (a10, a11): 48 (family, seed) groups hold 49 extra runs. Every group is a byte-identical simulation (same solvers_tail) under different run ids, counted as replicates.

### m2 MINOR: COPYALL overruns the budget (vm.py:142-146)
r_vm.py R1b: budget 3 gives steps 11.

### m3 MINOR: SEPARATED span (world.py:275-286)
r_world.py R6: the second half runs the replicator (64 neighbour writes), but the reported pc_max is 0, so the span is 1.

### m4 MINOR: positive-control grading
- known_replicator_replicates and endogenous_invades_when_seeded share vec_id 66a8a32b055dfed1 (a10). scheduler.py:346-349 overwrites `ok` per run, so both verdicts come from the last run in the family.
- controls.py:356: `or name == "const"` makes the witness_const check vacuous.

### m5 MINOR: the PC leaves its own tape (vm.py:89-200, 80% of opcode values are NOP)
- Random 64-byte tapes with an occupied partner: the PC leaves [0, L) in 68.8% and executes the IO region in 52.8%.
- r_vm.py R1c: a zero tape outputs 77 by running the partner's ECHO witness.
- In 54 ENDO-flag runs, only 16 of about 2291 solver copies solve ONLY with a partner in the window (a12_partner_exec.py). It is real but small for solvers, and larger for span (C7).

### m6 MINOR: replication and related triggers fire on runs that ended extinct
28 runs fire replication with extinct = True (same tail mechanism as C1).

## SUSPECTED (read from code, not executed)
- s1 world.py:312-318: `order` is computed before the loop, and a child spawned into cells[j] executes later in the same tick (age 0). This allows chain births within one tick and inflates replication_rate.
- s2 scheduler.py:136-138, 320: `_control_summary` and the specimen archive are read at ingest time under imap_unordered, so persistence_above_control and novelty_distance depend on completion order.
- s3 scheduler.py:66-81 (latent, since no resume ever happened): runs completed but not ingested before a crash keep their directories while next_run_no restarts from state or runs.jsonl, so ids can be reused and files overwritten (geometry.json survives if geometry is skipped). Promotions and specimen-archive updates for runs appended after the last checkpoint are not replayed. A truncated final runs.jsonl line makes json.loads raise.
- s4 tasks.py:70-76 with vm.py:123-126: reading input via LD A,(S) at 0xE0 is not a "read", so FORCED scores it 0 (a false negative, which lowers FORCED solve rates).
- s5 observatory.py:328 builds the control vec without repair(); scheduler.py:169-170 uses repair(). Treatment/control identity is inconsistent between the promotion signal and the flags.

## Suggested minimal failing tests (collected)
1. `extinct => solvers_tail == 0` (C1).
2. ECHO-witness population on COND_ONE ATOMIC gives solvers_tail < 1. INCREMENTAL x+19 is not a solver (C2/C3).
3. A RESERVOIR SEEDED_WITNESS COND_MULTI world seeds the COND_MULTI witness, and niche-0 ECHO solvers do not set solvers/moat_crossing (C4/C5).
4. CONST+FORCED does not set moat_crossing (C5).
5. `scan(t,s1).beneficial_density == scan(t,s2).beneficial_density` for identical t (C6).
6. SEEDED_HYBRID takeover after a random first replicator does not set reproductive_compression (C7).
7. A 1-byte PARTIAL write into an occupied partner gives no hifi replication credit to the writer (C8).
8. init RANDOM plus init_tapes does not set spontaneous_replication (C9).
9. Self-erasing fill gives fidelity < 0.9 (M1). A bare LDIR at reset does not satisfy COPY viability (M2).
10. `_late_batch` controls carry their own family's seed (M6). vec_id differs when init_tapes differ (M5).
11. GATED_INTERACTION: (tick - birth) <= lifespan for all alive organisms (M7).
