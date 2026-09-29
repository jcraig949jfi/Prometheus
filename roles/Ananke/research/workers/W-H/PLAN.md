# W-H PLAN: what does dynamic rule switching (SETRULE) do in PTE champions?

Worker W-H, namespace 0x5ED (analysis worlds = assays.world_seeds(0x5ED, 64),
32 mirror pairs, 99% pair bootstrap via lens.ci). Frozen 2026-09-28 BEFORE any
counterfactual run. Only static disassembly and a CPU timing probe preceded it.

Context read before this plan: COMMON_RULES*.md, my brief, engine.py, lens.py,
plants.py, envs.py, search.py, assays.evaluate, c1b.ticks; W-B scripts and
W-B out/*.json (raw census/deepdive/phase/gate numbers). NOT read: W-B
REPORT/PLAN/LOG, SYNTHESIS*, C1B_REVIEW*, PTE_ENGINE_CARD, ARC3_PRIORITIES,
PRIOR_ART (brief s4/s6 pointer noted, to be read only after results).

## Engine facts that frame the question (from engine.py)
- r[site] selects which of R program variants runs this tick. SETRULE sets
  r_next := A mod R (last executed SETRULE wins), applied after the program.
- r is a per-site register that (a) never decays (S decays when
  decay_shift>0), (b) costs no energy (S costs c_mem per non-zero word),
  (c) is invisible to the program except through WHICH variant runs.
- Therefore a switching genome is, formally, a single program of R*L text
  with an L-instruction per-tick budget plus a free log2(R)-bit state. A
  rules=1 program of the same L must hold that state in S (decaying, costed)
  or Kp (via WIMM, only if wimm=1) and must compute the dispatch with its own
  instructions. So EXPANSION is possible in principle at equal L; the
  question is whether these champions use it.

## Specimens (chosen to discriminate mechanisms, from W-B raw numbers + disasm)
S1 b59e6c3afebce00a RELAY d1 delta16, smallworld async, R4 L12, decay 0.
   Readout-site rule leaves 0 only in +cue trials, phases 3-10; its rule 0
   ramps S0 down every tick, rule 1 writes a positive constant. Candidate
   role: EVENT-TRIGGERED CONDITIONAL BRANCH (condition = packet count).
S2 311c465fd5a624cb HOLD gap4, torus sync period 2, R2 L8, decay 3.
   Only rule 1 writes S0 (from SENSE); readout-site rule is cue-sign
   independent and phase-locked. Candidate role: PHASE SELECTION /
   WRITE-ENABLE (sample-and-hold gate).
S3 95649e2c29e72d45 RELAY d1 delta16, ring async, R4 L12, decay 0.
   Rule 2 does not write S0; readout-site rule 2 occupancy depends on y sign
   across all phases. Candidate role: WRITE-PROTECT / STATE held in r.
Optional S4 faafa5b049e1d4b4 (HOLD, decay 1) only if time remains.
The candidate roles above are HYPOTHESES from static reading; Part 0 decides.

## Part 0: observation (normal runs only; no interventions)
Per specimen, 64 analysis worlds, record r, S0, SENSE, CNT/Acc at the
readout site and sensor, every tick. Decompile the branch: which SETRULE
instruction(s) fire, what their A operand is, what the selected variant
writes to S0/EMIT. Output: out/obs_<id>.json + a mechanism sketch in LOG.md.
Then, BEFORE any counterfactual, append "ADDENDUM A: instantiation" to this
file fixing the exact site class, tick window and forced value for CF1/CF2
and the hand-compiled fixed-rule program design (CF3). The decision rules
below do not change.

## Part 1: targeted counterfactuals (between-tick hooks only; lens-style)
Paired arm-minus-normal difference per pair, 99% CI.
CF1 FORBID: at the identified site class/window, pin r to its pre-switch
    value after every tick. Verdict NECESSARY if diff hi99 < 0;
    NOT-NECESSARY if diff lo99 > -0.05; else UNRESOLVED.
CF2 FORCE: impose the switch where it normally does not occur (the other
    cue sign or other phase). Accuracy on the affected trials:
    SUFFICIENT-FLIP if hi99 < 0.40; SUFFICIENT-CHANCE if CI contains 0.5 and
    hi99 < normal lo99; NO-EFFECT if lo99 >= normal lo99 - 0.05.
CF3 FIXED-RULE REPLACEMENT: see Part 2 (hand compile).
Predictions: S1 CF1 NECESSARY, CF2 flips -cue trials; S2 CF1 (hold r=0 at
the write phase) NECESSARY, CF2 (force r=1 during the gap) hurts
(distractor overwrite); S3 CF1 (forbid rule 2) hurts, CF2 weaker.

## Part 2: EXPANSION vs COMPRESSION (pre-stated criterion)
"Same length" := same per-tick program length L, rules=1, same physics
otherwise (setrule is moot at R=1). Competence reference = the champion's
accuracy on my 64 analysis worlds; target = its lo99 (call A*).
Evidence arms per specimen:
 (H) hand-compiled rules=1, length-L program implementing the Part-0
     mechanism: one design + at most 3 logged debug iterations.
 (B) bounded search, rules=1, prog_len L: search.evolve with the champion
     cell's own SearchSpec (pop 96, gens 36, same shaping), 4 seeds.
 (A) reproduction control, original R and L, same budget, 4 seeds.
 (C) rules=1, prog_len R*L (equal genome text), 4 seeds.
Each searched champion is re-scored on the 64 analysis worlds.
Verdicts (per specimen):
 COMPRESSION: any (H) or (B) program has mean acc >= A* on analysis worlds.
   Switching is then a representation of something a fixed program of the
   same length can do.
 EXPANSION (bounded): no (H) or (B) program reaches A*, AND (A) reaches A*
   in >= 1/4 seeds (the budget can find switching solutions), AND the (H)
   failure has an identified cause (instruction count, storage decay,
   dispatch cost). Stated as "not found within this bound", never as
   impossibility.
 INCONCLUSIVE: (A) reaches A* in 0/4 seeds and no (H)/(B) success.
Secondary readout (evolvability, not capability): best-acc distributions
of A vs B vs C, and whether (C) succeeds where (B) fails (text budget,
not switching, is the binding constraint).
Overall answer = per-specimen verdict tally; no pooling across specimens.

## Compute
CPU probe: one generation 96x8 worlds = 19 s at 2 threads -> a search is
~11 min CPU, ~1 min GPU. Searches run on GPU under a lease
(owner W-H, smallest ttl); if BUSY, queue in QUEUE.md and do Part 0/1/H on
CPU (2 threads). Part 0/1 on CPU, torch.set_num_threads(2).
Stop at 4 h wall from start (start ~ plan time).

## ADDENDUM A: instantiation (written after Part 0 observation, BEFORE any counterfactual)
Part 0 decompilation (details in LOG.md Attempt 2):
- S1 b59e6c3a: rule 0 at every site: EMIT = max(SENSE,0) (sensor emits on +cue
  only); S0 := S0 - S1 - 60 (ramp down); SETRULE r := CNT0 mod 4 (exact, 0
  exceptions in the observed readout-site table). Rule 1: S0 := 776 (97<<3);
  r := S1_prev mod 4 (=1 once), then S1 := 0 -> back to rule 0 after 2 ticks.
  Role: EVENT-TRIGGERED BRANCH (packet count selects the "set" variant).
- S2 311c465f: S0 written ONLY in rule 1 (S0 := SENSE ^ E); rule 1 lasts one
  awake tick (r := IN2_2 mod 2, inbox empty -> 0). Rule 0: S2 ^= SENSE,
  r := S2 mod 2; rule 1 resets S2 := 256*(S3 > SENSE); decay (shift 3)
  changes S2's parity after a fixed number of ticks -> a decay-driven
  oscillator, reset by the cue XOR, that opens the S0 write-enable near the
  cue. Role: PHASE SELECTION / WRITE-ENABLE CLOCK (sample-and-hold).
- S3 95649e2c: rule 0: S0 := CNT0 (never negative: answer is + or tie);
  r := IN0_0 mod 4 (payload -110 or 146 -> rule 2). Rule 2: no S0 write
  (hold), EMIT := ENERGY (forward), r := 0 next. Role: TEMPORARY
  SPECIALIZATION as one-tick forwarder + readout hold; state_dim=2 with both
  S registers used by rule 0, so r is the only spare per-site register.

CF instantiation (t0 = trial start, ro = readout tick, hooks after tick t):
S1 CF1 FORBID: readout site r := 0 after every tick (all trials).
   Control CF1c: same pin on one random non-sensor non-readout site per world.
   CF2 FORCE: in trials where the world's y = -1, readout r := 1 after tick
   t0+5 (scored on those trials only).
S2 CF1 FORBID: readout r := 0 after ticks t0-1 and t0 (rule 1 cannot run on
   the cue phases 0,1), all trials k >= 1.
   CF2 FORCE: readout r := 1 after ticks t0+2 and t0+3 (rule 1 runs in the
   gap, samples a distractor), all trials k >= 1.
S3 CF1 FORBID (global): after every tick t >= 2*Pd-1, every site with r==2
   gets r := 0. CF1r: same, readout site only.
   CF2 FORCE: in y = -1 trials, every site r := 2 after tick t0+3 (one
   forced forwarding step), scored on those trials.
Decision rules exactly as in Part 1.

Part 2 (H) designs, rules=1, same L:
 H1 (S1, L12): MAX EMIT SENSE ZERO; CONST PAY0 90<<7; MOV T0 CNT0;
    CONST T1 97<<3; ADDI T2 S0 -60; SEL T0 T1 T2; MOV S0 T0.
 H2 (S2, L8): MULQ T0 SENSE SENSE; ADDI T0 T0 -100; SEL T0 SENSE S0;
    MOV S0 T0 (write-enable from |SENSE| instead of a rule clock).
 H3 (S3, L12): role-faithful forwarder: S1 flag = (+cue at me) or (packet
    arrived); EMIT := previous flag once; S0 := CNT0 (with the same
    non-negative code). Plus H3-alt = H1 run on S3's physics (a different
    mechanism; reported separately as "any fixed L program", counts for
    COMPRESSION per Part 2 wording "any (H) or (B) program").
Scored on the 64 analysis worlds against A* = champion lo99 there:
 S1 A* = .707, S2 A* = .715, S3 A* = .648.

## ADDENDUM B (before running anything on S4): optional S4 faafa5b0
Purpose: the only specimen where S decays fast (decay_shift 1: S halves
each tick; HOLD gap 16), i.e. where r's decay-free storage could matter.
No CFs (time); Part 2 H arm only, A* = champion lo99 on analysis worlds.
 H4a (plain S0 latch, as H2): expected to keep only + signs (positive S
   floors at 1 under S - S>>1, negative decays to 0) -> predicted ~.75.
 H4b (Kp latch via WIMM, decay-free, no rules): on |SENSE|>128 write SENSE
   into Kp[j]; instruction j = ADDI S0 ZERO 0 reads it every tick.
Verdict rule unchanged (COMPRESSION if any H >= A*). If both fail, S4 is
reported as an EXPANSION candidate only if a cause is identified.

## ADDENDUM C (before running): S5 ed884172 mini-check
Raw C1 scan: of the 42 qualifying SETRULE cells, ed884172 (HOLD, decay 1,
wimm 0, plastic_route 0) is the one where r is the ONLY decay-free
per-site store besides E. W-B census raw: FA EQUIV (rule use ends at boot).
Test only H4a (plain S0 latch; predicted .75 from the positive floor) vs
A* = champion lo99 on analysis worlds. Same verdict rule.
