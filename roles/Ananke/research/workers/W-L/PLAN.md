# W-L PLAN: is a retention regime REACHABLE when the task rewards it? (T-RET-EVO)

Frozen 2026-09-28 before any search and before any plant/task check was run.
Worker W-L. Analysis namespace 0x5F2, held-out namespace 0x5F3.
Context read before this PLAN: COMMON_RULES*.md, my brief, engine.py, envs.py,
search.py, assays.py, lens.py, plants.py, physics.py, c1b_run.load, W-G wg.py
(code only, for the C-EFF / C-AVL plant idioms), INSTRUMENT_CARRIER_SWAP.md.
NOT read: SYNTHESIS*, C1B_REVIEW*, PTE_ENGINE_CARD, ARC3_PRIORITIES, any REPORT.md.

## 1 Question
When the task DOES reward keeping a cue beyond its own query (n-back), does the
declared C1 outer search (search.evolve, SearchSpec of the M2 cell) reach a
retention mechanism? If yes, which carrier holds the old bit? If no, is that a
search-reachability failure (hand plants solve it at the same physics and
program length) or a physics limit?

## 2 Physics and search (fixed)
- Physics: the M2 specimen physics, c1b_run.load("4ab2ba014aac967e"), unchanged
  (ring 144 r3, state_dim 2, prog_len 16, P2 C1, fanout 8 sample, loss .1,
  cap 2 saturate, sync period 2, plastic_route 1, wimm 1, rules 1).
  FALLBACK (declared now, used only if NO hand plant solves n=2 at state_dim 2 /
  prog_len 16): the W-G control physics = M2 with state_dim=4, prog_len=24, for
  BOTH plants and searches. The fallback choice is recorded in LOG.md.
- Search: search.evolve with SearchSpec = the M2 cell's recorded spec
  (pop 96, M 8, gens 36, elite 4, trunc .25, p_field .04, p_instr .15,
  p_swap .10, p_cross .30, M_final 16, M_held 64, w_contrast .10, w_any .02).
  search.py is NOT edited. The n-back episode builder is injected by
  monkeypatching prometheus.ananke.envs.build in MY process only (a wrapper that
  builds n-back for my NBackSpec and delegates everything else), so evolve,
  assays.evaluate and the twin assay run byte-identical code.
- Search seeds: search_seed = H_int(0x5F2, n, s), s = 0..3.

## 3 Task: N-BACK (built in workers/W-L/nback.py)
HOLD timing of the M2 cell unchanged (one site a = sensor = actuator, cue_len 2,
amp 256, gap 8 with +-64 distractors, iti 2, period 13, 12 trials). Cues c_k
i.i.d. fair coins. The readout of trial k (tick t0_k + cue_len + gap, same as
HOLD) is scored against y_k = c_{k-n}; trials k < n are unscored. Mirror pairs:
world 2p+1 has the whole cue AND distractor sequence negated (so y negated).
Env draws: numpy default_rng(H_int(lead_seed, ENV, 0x4E42 + n, variant)).
Arms: n = 1 and n = 2, 4 seeds each (8 searches). Pipeline control arm n = 0
(= HOLD through my builder, 2 seeds) to show the injected builder + search reach
the lag-0 task at all; it is a control, not an arm of the question.

### 3a Task-validity checks (CPU, before any search; must all PASS)
T1 target independence: over 4096 built worlds, for every scored trial, the
   empirical agreement P(y_k == c_{k-j}) for every j != n (j = 0..k), and
   P(y_k == sign(distractor sum of trial k)) must lie in [.47, .53]; and
   P(y_k == c_{k-n}) == 1 exactly.
T2 mirror: y[2p+1] == -y[2p] and sense_val[2p+1] == -sense_val[2p] exactly.
T3 SEQUENTIAL-EXPLOIT test: every policy that is a function of the visible
   history EXCEPT c_{k-n} scores exactly 0.5 averaged over a mirror pair?
   Concretely, evaluate on 64 held-out-style worlds (0x5F2) through the
   engine: the null plant, lag-0 latch (answers the current cue), and for n=2
   the lag-1 S plant. Each must have 99% pair-bootstrap CI containing .5 and
   hi99 < .60. In addition, an exhaustive host-side check: all 2^(2^3) boolean
   functions of (c_k, c_{k-1}, c_{k-2}) minus the lag-n input (i.e. of the
   other lags) scored on 4096 worlds: max accuracy <= .53.
T4 no leak through the schedule: the lag-n cue is not present in sense_val at
   or after the cue of trial k-n+1 (by construction; asserted).
If any T check fails, fix the task in my builder, log it, rerun all T checks;
no search before all pass.

### 3b Plant solvability (CPU; required)
Hand plants at the chosen physics and program length (assembled in nback.py,
never search seeds):
 P1S  n=1, carrier S1 (site state; 9 lines): cue-gated S0 := S1; S1 := cue.
 P2S  n=2, carrier S1 holding two bits packed (2*c_k + c_{k-1}, 16 lines).
 P1K  n=1, carrier Kp via WIMM (C-AVL idiom): stored bit read through an ADDI
      immediate; S0 only holds the answer.
 LAG0 latch of the current cue (no-memory baseline; also P1S-style lag1 plant
      used as the no-memory-of-lag-2 baseline for n=2).
Solvable := held-out (0x5F3, 64 worlds) pair-mean lo99 > .90 for P1S/P1K on
n=1 and P2S on n=2. If a plant fails, debug the plant (plants are allowed to
be fixed; they are controls). If NO plant can solve n=2 at state_dim 2 /
prog_len 16 after honest effort, switch to the fallback physics (s2) for
everything and log it. The search question is posed only for arms whose plant
passes.

### 3c Instrument known answers (CPU)
Carrier swap (my routine, below) on the plants: P1S -> S FLIP, Kp NO-EFFECT;
P1K -> Kp FLIP, S NO-EFFECT (S0 holds only the old answer before the next cue).
If these known answers fail, the carrier instrument is not used on champions.

## 4 Success criterion (per search, frozen)
Held-out evaluation of the champion on 64 worlds from world_seeds(H_int(0x5F3,
n, s), 64) (disjoint from evolve's own held-out), scored on scored trials:
 SUCCESS iff  (a) pair-mean lo99 > .60  AND
              (b) lo99 of the paired difference (champion - B) > 0, where B is
                  the no-memory baseline policy with the highest pair mean on
                  the same worlds among {null, LAG0 latch, (n=2) lag-1 plant}.
Arm reading: REACHED if >= 1/4 seeds SUCCESS (robust if >= 3/4);
NOT REACHED if 0/4 and the arm's plant passed (-> search-reachability failure
at the declared budget; it is NOT a physics limit, because the plant solves it);
ILL-POSED if the plant did not pass.
Also reported (not criteria): evolve's own held-out numbers, zero_comm control,
training curves (max/mean acc per generation), and whether champions reached
the lag-0 policy (a local optimum signature: accuracy ~.5 with high sens).

## 5 Carrier identification (only for SUCCESS champions; plants as controls)
Mirror-pair swap between ticks (lens.swap), run through lens.run with my
episode: for trial k in {4, 6, 8} separately, swap carrier X after tick
t0_k - 1 (end of trial k-1, before cue k: the carriers then hold c_{k-n}..c_{k-1}),
and score trial k only (target c_{k-n}), pooled over the three k (3 runs per X).
Carriers X: S, Kp, w, inbox (Acc_sum+Acc_cnt), channel_all (Msum+Mcnt),
pay0, pay1, site_all. (E: economy off; r: rules=1 -> not applicable.)
Verdicts by lens.swap_verdict (FLIP hi99 < .40; NO-EFFECT lo99 >= normal lo99
- .05; CHANCE otherwise); arm_identical recorded (F4/F8). The carrier named =
the swap that FLIPs; if none FLIPs, CHANCE carriers are reported as
"mixed/handoff" and additionally tested with a reset (Controls reset_state_at
at the same ticks with reset_parts for S / Kp / w / inbox, and
flush_inflight_at for channels) to report necessity. For n=2 also swap at
t0_k - 1 - Pd (two trials back) to see where the bit lived earlier (handoff).
Also recorded: zero_comm held-out accuracy (does the mechanism need packets).

## 6 Compute
Searches on GPU under a lease (roles/Ananke/research/lease.py). If BUSY: record
the searches in QUEUE.md ready to run as written; do all CPU parts; retry the
lease periodically. A reduced-size CPU pilot is allowed ONLY as a labelled
pilot (never read against the criterion): pop 24, gens 8, M 8, n=1 seed 0.
No weaker experiment is substituted for the preregistered one.
STOP at 4 h or when arms are done.
