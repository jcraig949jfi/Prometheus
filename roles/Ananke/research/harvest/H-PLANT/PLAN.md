# H-PLANT worker PLAN (concrete design; written before any run)

Frozen parent plan: roles/Ananke/research/plans/H-PLANT_PLAN.md (01234c0ad), not edited.
Deviations from it: PLAN_ADDENDUM.md (written before the affected runs).
Design formed from engine code (engine.py, envs.py, physics.py, topology.py, plants.py,
campaign.py, c1b.py, assays.py) and raw C1 rows (roles/Ananke/pte/c1_rows/cells.jsonl.gz) only.

## 0. Common machinery
- CPU only: CUDA_VISIBLE_DEVICES=-1 set in os.environ before torch import (asserted
  torch.cuda.is_available() is False), World(device="cpu"), torch.set_num_threads(<=8).
- Evaluator: same semantics as c1b.evaluate (mirror pairs share physics seeds; world b+1
  gets negated inputs), eager ticks, envs.score.
- SCORING worlds: 256 = 128 mirror pairs, seeds assays.world_seeds(0x48504C54, 256)
  ("HPLT"; a namespace no C1/C1b/worker code uses). DEV/screen worlds: world_seeds(0x48504C44, 32).
- CI: 99% percentile bootstrap over the 128 pairs (assays.pair_ci: 2000 resamples, rng seed 0)
  -- the house method (pairs are the independent unit).
- Reading per task (from the parent plan): PHYSICS ALLOWS if lo99 > .60 at the chosen
  physics AND at >= 1 C1-sampled physics point; ONLY OFF-CENSUS if only at unsampled physics;
  NOT SHOWN otherwise. Must-fail: key operand zeroed -> lo99 <= .55.

## 1. Known-answer gate (first; stop if any fails by > .02)
- G1a relay_flood, C1 plant_viability row, cell 29b7e63a5fa4a78b (A0, RELAY d3 delta16, physics
  digest d9ccb6a71d986501): recorded plant.acc 0.9609375. Re-run campaign.plant_viability(ph, env,
  search_seed, device="cpu") exactly.
- G1b relay_flood, C1b fixture F_DA (c1b_da_physics, relay_da env, DEV_NS 0xDE7, 64 worlds):
  recorded normal 1.0 (roles/Ananke/pte/c1b/FIXTURES_dev.json).
- G2 echo_hold, C1b fixture F_echo (c1b_echo_physics, HOLD gap 8 cue 2 trials 12, DEV_NS, 64
  worlds): recorded normal 1.0.
Pass = |reproduced - recorded| <= .02 for all three.

## 2. Plants (hand-written, <= 16 instructions = C1's max prog_len; no search)

### P-XOR ("clock flood of the sign set"; needs decay_shift 0, sync update_period 1)
Env fact: XOR places s1 random, s2 at env distance d from s1, and the actuator UNIFORMLY among
sites at distance >= max(1, d//2) from both. So "both sensors direct neighbours of the actuator"
cannot be arranged for all worlds by any physics in range (see ADDENDUM A1). The plant floods,
per trial, the SET of cue signs present: flag P = "a + cue exists", Q = "a - cue exists";
y = x1*x2 = -1 iff both flags are set. Registers: S0 readout, S1 = P, S2 = Q (0/256),
S3 = a global clock (all sites start at 0 and wake every tick, so S3 = t).

     1 CONST T3 = Pd-1            (Pd = env period = delta+1+iti; plant is told the env timing)
     2 MOD   T2 = S3 mod Pd       phase
     3 ADDI  S3 = S3 + 1
     4 GT    T2 = (phase > 0)     256 / 0
     5 MULQ  S1 = S1*T2>>8        reset P at trial onset
     6 MULQ  S2 = S2*T2>>8        reset Q
     7 MAX   T0 = max(SENSE, IN0_0)
     8 GT    T0 = (T0 > 0)        + evidence (own + cue, or a P marker arrived)
     9 GT    T1 = (IN0_1 > SENSE) - evidence (own - cue, or a Q marker arrived)
    10 GT    PAY0 = (T0 > S1)     newly P
    11 GT    PAY1 = (T1 > S2)     newly Q
    12 ADD   EMIT = PAY0 + PAY1   emit once per newly learned flag (flood, no reverberation)
    13 MAX   S1 = max(S1, T0)
    14 MAX   S2 = max(S2, T1)
    15 XOR   T3 = S1 ^ S2         256 iff exactly one flag
    16 ADDI  S0 = T3 - 128        +128: one sign present (y=+1); -128: both present (y=-1)

Struct: state_dim 4, payload_width 2, channels 1, rules 1, prog_len 16.
Chosen co-arrival physics X0: torus 64 (8x8) radius 3, dest_mode all, loss 0, lat_base 1,
lat_hop 0, jitter 0, dup 0, noise 0, cap 0, collision none, decay 0, sync period 1, no
economy, no plasticity/setrule/wimm/mut. Every site within 3 hops = 3 ticks of every sensor,
so both flags reach every site before readout. Env: XOR d=3 delta=8 (C1 env levels).
Predicted: ~1.0.
C1-sampled points: (i) d9cc (C1 XOR cell d64656f26736d37c): an analytic LIGHT-CONE bound is
computed first (below); the clock plant needs update_period 1 and d9cc has 2, so the plant is
not run there unless it fits. (ii) SCREEN: every C1 XOR row with update_mode sync,
update_period 1, decay_shift 0, mut_site 0, c_op 0 (clock-compatible transport), physics with
the plant's genome-space fields substituted (c1b.at_specimen convention, PLANT_STRUCT: prog_len,
state_dim, payload_width, channels, rules, setrule, wimm, plastic_route, adapt_shift), env =
the row's env, 32 DEV worlds; the top screen cell (ties: first by cell id) is scored on the 256
fresh HPLT worlds. The reading uses ONLY the fresh score.
Light-cone bound (d9cc XOR): per world, the actuator can be correct above chance only if the
cue information from BOTH sensors can physically arrive by the readout tick. Minimum hop delay
at d9cc = lat_base + lat_hop*dist (jitter >= 0) and sites wake only on even ticks; compute
per world the earliest possible arrival (shortest-delay path, ignoring loss/cap), take
f = fraction of worlds where both arrive in time; accuracy <= .5 + f/2. If this bound < .60 the
d9cc XOR NULL is bounded by physics+env geometry regardless of program (reported as an
ANALYTIC bound, not a plant reading).
Must-fail (MF-XOR-a, the gate): "readout ignoring one sensor" = sensor s2's cue schedule
zeroed (the plant then sees x1 only); predicted .50. Diagnostic MF-XOR-b (reported, not gated):
Q operand zeroed in the readout (line 15 XOR T3 S1 ZERO): readout = "+ iff P", predicted ~.25
(an OR/AND-type readout correlates with XOR at |.25| under this env's mirror; see s4).

### P-FLIP ("relay the cue; carry m*c at the actuator"; needs decay 0; 2 state registers)
Env: cue c (amp 256) at sensor; teacher tau = m*c (amp 128) at the actuator one tick after
readout; target y = m*c; m constant within a block. The plant keeps S1 = last relayed cue sign
(relay_flood semantics with a 128 threshold so the teacher is not relayed) and S0 = m*S1 as an
invariant: each tick S0 := (S0*S1_old>>8)*S1_new>>8 (exact because |S1| = 256), and a teacher
sets S0 := tau.

     1 ADD  T0 = SENSE + IN0_0
     2 CONST T2 = 128
     3 SUB  T3 = 0 - T2
     4 GT   PAY0 = (T0 > 128)
     5 GT   T3 = (-128 > T0)
     6 SUB  PAY0 = PAY0 - T3      v = sign*256 or 0 (teacher +-128 excluded)
     7 SUB  T0 = v - S1           change
     8 MULQ EMIT = T0*v>>8        > 0 iff v != 0 and v != S1 (re-emit only on change)
     9 MULQ T1 = S0*S1>>8         m*|.| using OLD S1
    10 MULQ T2 = v*v>>8           256 iff v != 0
    11 SEL  T2 = T2>0 ? v : S1
    12 MOV  S1 = T2               adopt v where v != 0
    13 MULQ S0 = T1*S1>>8         S0 = m * c_new
    14 MULQ T3 = SENSE*SENSE>>8   > 0 iff SENSE != 0
    15 SEL  T3 = T3>0 ? SENSE : S0
    16 MOV  S0 = T3               teacher: S0 := tau

Struct: state_dim 2, payload_width >= 1, channels >= 1, prog_len 16 -> fits d9cc AS SAMPLED.
Chosen physics F0: d9cc with loss 0, lat_jitter 0, cap 0, collision none (a lossless variant).
C1-sampled point: d9cc exactly (C1 FLIP cell 6f82f9c7d51bcef1: d3 delta16 block4, trials 16).
Env for F0: the same env. Predicted: F0 ~1.0 on scored trials; d9cc high (relay_flood
scored .96 at d9cc RELAY d3 delta16).
Must-fail (MF-FLIP-a, gated): teacher operand zeroed (line 14 MULQ T3 ZERO ZERO): S0 stays 0,
predicted exactly .50. Diagnostic MF-FLIP-b: readout ignores m (line 16 MOV S0 S1):
predicted ~.50.

### P-MULTIHOP
Program: plants.relay_flood unchanged (12 lines + 4 NOP; adopt sign(SENSE+IN0_0), re-emit
only on change: every site that changes is a relay). Env: RELAY d=5 at ring radius 3 (ring
distance 5 > 3: at least 2 hops, forced), delta 16, block 4 = C1 cell fac4aaa23a0bdcb2 (NULL,
held .5). C1-sampled point: d9cc exactly. Chosen physics M0: d9cc lossless variant (loss 0,
jitter 0, cap 0, collision none). Extra (off-census env): d=6 = 2*radius as the parent plan
literally states, at M0 and d9cc.
Must-fail (MF-MH, gated): relay disabled -- EMIT gated to sites with SENSE != 0 (3 appended
lines: MULQ T0 SENSE SENSE; GT T0 T0 ZERO; MULQ EMIT EMIT T0 -> 15 lines), so only the sensor
emits and d=5 > radius is unreachable; predicted .50.

## 3. Budget
Cap 2 CPU core-hours total (process CPU time via time.process_time, logged per run in
LOG.md). <= 8 threads. Design effort <= ~1 core-hour per task. If a plant misses lo99 > .60,
the reading is NOT SHOWN; one documented repair attempt per task is allowed (logged as a new
attempt, with the reason) within the per-task budget.

## 4. What would surprise me / decision notes
- XOR+mirror: y = x1*x2 and the mirror negates x1 only. Any readout f(P) of a single sign-set
  flag contains the x1*x2 term with coefficient 1/2, so it scores .25 or .75, not .5. C1's
  SIGNAL rule (lo99 > .55) could therefore be met by OR-type solutions that never compute XOR.
  Reported as a finding; it does not change any reading here.
- relay_flood is itself a multi-hop plant (every changing site relays). If it scores lo99 > .60
  at d9cc d=5, the C1 multi-hop NULL there is search, not physics.
