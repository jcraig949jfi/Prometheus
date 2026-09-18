# WSE/SSF design v0.2 -- SELECTIVE STATE FORMATION, cycle 1 (preregistration)

Archaeon[m2-411504ab], 2026-09-16. Directive:
roles/Archaeon/prompts/2026-09-16_selective_state/00_OPERATOR_DIRECTIVE.md
(extends 2026-09-16_workspace_ecology/). Committed BEFORE any v0.2 row.
Carries the v01 lessons (READOUT_v01.md s8): costs ramp after a foothold;
lagged-echo nulls; random query timing; property-keyed classes; transfer
branch; smaller value alphabet for a search foothold.

## 0. Substrate

Unchanged: Proteus player VM + grammar + lineage (nothing under proteus/
edited). archaeon/wse/ gains: stream-world knobs (worlds.py), a cost RAMP
(economics.py), a learning curve and experience ledger (evolve.py), three
hand-written boundary organisms + lagged-echo nulls (controls.py), and a
runner ssf.py. No organism-side machinery is added: state dimensionality
(n_regs, tape_words), lifetime (persist policy), update rules, gating,
decay, routing, exact vs lossy storage, event-triggered computation and
conditional persistence are all expressible by the existing 25 opcodes
and the evolvable manifest; nothing names them.

## 1. The stream world (one episode)

T ticks; one event per tick (plus optional trailing NOISE words):
  PUT    [1, tag, v]       tracked or distractor entity `tag` gets v.
                           op_mode replace: s_tag := v (UPDATE / STATE
                           REVERSAL); op_mode add: s_tag := s_tag + v
                           (COMPOSE, fold)
  RETIRE [9, tag]          s_tag := 0 from now on (FORGET: keeping the old
                           value is actively wrong)
  ASK    [2, tag]          expect s_tag  (EXACT RECALL)
  ASK2   [4, tagA, tagB, c] expect combine_c(s_A, s_B)  (COMPOSE)
  NOISE  [8, r1, r2]
Entities: K TRACKED tags (each asked at least once) and Kd DISTRACTOR
tags (never asked; DISTRACT, DELAYED RELEVANCE: the organism cannot tell
them apart until an ASK arrives). INTERFERENCE knob: distractor tags share
the top 12 bits of a tracked tag (differ in the low 4). TIMESCALE: each
tracked tag's ask is placed a delay after its LAST relevant event, the
delay drawn per tag per episode from the cell's set (e.g. {4,16,64}); ask
ticks are therefore never at a fixed offset (guard: fixed query timing).
D events per tracked tag (UPDATE when replace), retire_rate = probability
a tracked tag is RETIREd after its last PUT and asked afterwards.
GENERALIZE: training tags are drawn from [1, 2^15); the held-out
"vocabulary" family draws from [2^15, 2^16); kind codes are fixed syntax.
Values: uniform in [0, 2^value_bits), value_bits = 4 in v0.2 (a smaller
alphabet so partial strategies score above zero; the W0 needle of v01
was at 8 bits).
Every identity is redrawn per episode; families (train / heldout /
heldout_vocab / intervention / curves) never overlap.

## 2. Economics with a RAMP (v01 Shape A)

  fitness = reward - m_g * (alpha*ops/1000 + beta*persistent_words/64
                            + gamma*(in_reads+out_writes)/100)
  m_g = min(1, best_train_reward_so_far / 0.30), monotone in g.
Costs are zero until the population has any foothold and full once the
best organism answers 30 % of asks. Regimes:
  S0  alpha 0     beta 0     gamma 0       (reference: reward only)
  S1  alpha 0.02  beta 0.05  gamma 0.02    (storage dear: a 1024-word
                                            persistent tape costs 0.80;
                                            64 words 0.05; 16 regs 0.0125)
  S2  alpha 0.02  beta 0.20  gamma 0.02    (storage very dear)
  S3  alpha 0.10  beta 0.05  gamma 0.02    (compute dear: rereading
                                            history costs)
Falsifier of the ramp: if S1 goes extinct as E1 did (persist=none share
> 0.9 by generation 10 with best reward 0), the cost SCALE is wrong, not
its timing; report and do not tune mid-run.

## 3. The boundary map (CRITICAL CONTROL, computed before evolution)

Three hand-written organisms, run on every cell's control family:
  FULL_LOG   persist=all, tape 1024: appends every (tag, v) it sees; on
             ASK scans the log backwards for the tag (re-reads history);
             RETIRE appends (tag, 0). Memorises history.
  SELECTIVE  persist=all, tape 64: one (tag, last value) slot per entity
             seen, overwritten on update, zeroed on RETIRE. Maintains
             state about history.
  TRIVIAL    persist=regs: the last value seen. Overcompression.
Their reward, ops, persistent words and reads/writes are recorded per
cell, and their FITNESS under S0-S3 and under a beta sweep
{0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5} x alpha {0, 0.02, 0.1}. The regime
where SELECTIVE beats BOTH by >= 0.10 fitness is "selectivity pays"; the
region where FULL_LOG wins is "too little cost"; the region where
TRIVIAL wins is "too much cost / too much forgetting". A cell x regime
pair enters evolution ONLY if it lies in the selectivity-pays region
(directive: "find the regime in which selectivity pays"). Note the
hand-written organisms are NOT seeds for evolution and never appear in a
population; they map the economics.
Nulls (all must score < 0.10 or the cell is void): CONST0, ECHO_LAST
(current tick), ECHO_PREV_1/2/3 (a word of the previous k ticks; every
word position tried; the max is reported), ECHO_FIRST (first word of the
episode).

## 4. Cells (cycle 1)

  name          K  D  op       Kd  retire  delays      interfere  ask
  A_remember    1  1  replace   8  0       {4,16,64}   no         ASK
  B_update      1  4  replace   4  0       {4,16}      no         ASK
  C_forget      1  2  replace   4  0.5     {4,16}      no         ASK
  D_bind2       2  2  replace   8  0       {4,16}      no         ASK
  E_bind4       4  2  replace   8  0       {4,16}      no         ASK
  F_compose     2  2  add       4  0       {4,16}      no         ASK2
  G_interfere   2  2  replace   8  0       {4,16}      yes        ASK
  H_timescale   2  1  replace   8  0       {4,64}      no         ASK
Regimes: S0 and S1 on every cell that passes s3; S2 and S3 on A and D.
Seeds 1,2,3. Branches: B1 naive (gen-0 random, genome 1..16 instr); B2
transfer on A, B, D (gen-0 = the seven v01 solver elites + their final
populations' top-4, padded with randoms) -- directive X "what transfers".
Loop: N=256, G=120, E=16, elitism 4, tournament 4, fresh episodes per
generation. Learning curve: every 10 generations the elite is scored on
24 held-out episodes; experience = cumulative episodes evaluated by the
lineage (N*E*(g+1)) and cumulative ticks.

## 5. Measurements per row (directive MEASUREMENTS)

experience_episodes, experience_ticks; competence_heldout;
competence_heldout_vocab (transfer: unseen tag range); competence on
changed worlds (Kd doubled; delay doubled; K doubled); persistent_words;
peak_state (max non-zero non-code tape words + regs used);
reads_writes; ops (compute); fitness; learning curve [(experience,
competence)]; slope over the last three curve points; derived:
competence/experience, transfer/experience, competence/persistent_words,
competence/ops; and across generations d(competence)/d(experience) per
window (change in learning efficiency).

## 6. Interventions and ablations (unchanged battery + curves)

Battery of v0.1 s6 (nine interventions, erase ceiling reported). Curves
on every elite with held-out >= 0.3: Kd in {0,4,8,16,32}; delay in
{4,16,64,128}; K in {1,2,4,8}; vocabulary swap. "Freeze state" =
ERASE_* at the intervention tick; "randomise update rule" is not
expressible without editing the genome and is NOT done in v0.2.

## 7. Classes (property-keyed from the start)

  NO_ADAPTATION   heldout - floor < 0.10
  LAST_VALUE      ERASE_REGS >= 0.10, ERASE_TAPE < 0.05, and the K-curve
                  at K=2 <= 0.6 x K=1
  SELECTIVE_STATE heldout >= 0.5 at Kd >= 8 with persistent_words <= 64
                  and competence at Kd doubled >= 0.8 x heldout
  HISTORY_REPLAY  ops grow with Kd at slope >= 2 ops per distractor and
                  persistent_words >= 256
  UNRESOLVED      otherwise, full vector printed
No class is a cell property unless 3/3 seeds agree.

## 8. Self-falsifiers

- Boundary map has no selectivity-pays region for a cell: the cell's
  economics are misposed; it does not run; the map is the result.
- Any null >= 0.10 on a cell: void.
- S1 extinction by generation 10 (s2 falsifier).
- Determinism: timing-free digest reproduces across launches.
- A transfer branch that beats naive on training but not on held-out
  vocabulary is memorisation of the tag range, not transfer.

## 9. Not in v0.2

50,000-step timescales (episode length is bounded by ops budget: 128
ticks max); within-lifetime learning (the VM organism is a fixed program;
"experience -> competence" is measured across the LINEAGE; the operator's
"organisms that become better at learning" needs a substrate where a
single organism's competence changes with its own experience -- recorded
as a candidate substrate requirement, NOT filed yet: v0.2 first asks
whether lineages become cheaper per unit competence); randomised update
rules; communication costs.

## Annotation v0.2.1 (2026-09-16, BEFORE any evolutionary run; after the control check only)

1. SELECTIVE's tape is 512 words, not 64: the hand-written program alone
   is ~230 words and the VM's persistent footprint counts the whole tape,
   so at 256 the slot table held 6 entries and lost on E_bind4 (0.859).
   The boundary organisms are therefore PESSIMISTIC about footprint
   (FULL_LOG 2048, SELECTIVE 512, TRIVIAL 8 registers); evolved organisms
   with 1-16 instructions carry 16-256-word tapes.
2. The void rule uses STATELESS nulls only: CONST0 (except on retire
   cells, where it is the retire floor and reward is also reported split
   by retired / non-retired asks) and ECHO_PREV_0 (current tick), each
   against chance + 0.10 where chance = 2^-value_bits = 0.0625. Lagged
   echoes and ECHO_FIRST need a register to carry a word across ticks:
   they are STATEFUL shortcut floors and are reported beside every cell,
   never a void. (On A_remember ECHO_FIRST ~0.17 = the chance that the
   tracked tag's PUT is the episode's first event; a "remember the first
   value" organism earns that; it is a partial strategy, not a leak.)
3. F_compose has no hand-written positive control (ASK2 with the combine
   codes); by s3 it does not evolve in cycle 1 and is recorded as
   NOT_EXAMINED, not as a result.
