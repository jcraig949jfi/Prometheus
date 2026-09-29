# W-R PLAN (E-ANANKE-W-R, T-INS-9, successor of T-INS-6/8, thr-8c7342a7d513, MWO-0004)

Frozen 2026-09-29 ~12:35Z, BEFORE any census run. Thresholds below are not changed after results.

## Question
Does stratifying the SINGLE-trial carrier-swap census (prometheus/ananke/lens_swap.py) by the
update-clock phase of the swap tick change carrier classifications, and for which physics?

## s0 How phase dependence is determined (done before this plan; LOG A1)
- engine.py step 3 WAKE (lines 292-296): if `ph.update_mode == "sync"`, every site is awake at tick t
  iff `t mod ph.update_period == 0` (one global clock, same for all sites and worlds). Otherwise (async)
  awake = hash(world seed, WAKE stream, t, site) < update_p: memoryless, no periodic schedule.
- No other periodic update exists: the mailbox slot `t mod LM` is ring-buffer indexing (arrival = emit
  tick + delay; delivery does not depend on t mod LM), decay acts every tick, rng streams are hashed.
- Asleep sites keep accumulating their inbox (Acc_sum/Acc_cnt are zeroed only for awake sites), do not
  run the program and do not emit. So in sync period p a delivered packet can wait in the inbox (a SITE
  array) up to p-1 ticks.
- probe_physics.py (out/physics.json): 2dccdaa5, c16d5231, 78f3b0ec, 8c37f32e, e06701a5, 4781b0a1, E1,
  E2 are sync update_period 2 -> PHASE-DEPENDENT. 369f5a5b is async (update_p .8) -> NOT
  phase-dependent: NEGATIVE CONTROL.
- Trial period Pd: 11 (2dcc, c16d, 8c37, e067), 19 (78f3, 369f, 4781) are ODD, so t0 = k*Pd alternates
  parity across trials 1..11 (6 trials t0 odd: k=1,3,5,7,9,11; 5 trials t0 even: k=2,..,10). E1 Pd 12
  and E2 Pd 16 are EVEN: all trials share one phase, so one stratum is empty (UNDEFINED) and the other
  stratum IS the pooled census (degenerate, stated as a bookkeeping prediction).

## s1 Design
- Specimens loaded exactly as W-M/apply.py spec() (cells via c1b_run.load; E1/E2 via designed_echoes).
- Worlds: assays.world_seeds(0x620, 256) (M = 256 = 128 mirror pairs) for every spec and plant.
- Offsets o = 0 .. ro_off-1 (o = -1 omitted; identity-broken by construction). Trials 1..11.
- Arms: site_all / channel_all, SINGLE (only trial k swapped and scored), as lens_swap.mixture_scan mode
  'single'. Runner: a forked equivalent of lens_swap.run_arms (fork.py): one normal run of M worlds;
  at trial k the state after tick k*Pd + o_min is tiled into 2 x n_offsets arm blocks, swaps are applied
  after tick k*Pd + o, run to trial k's readout. It MUST be bit-identical to lens_swap.run_arms (check
  KA-F below) before any census is run with it.
- Phase of a (pair, trial, offset): q = (t0 + o) mod p, t0 = k*Pd, p = update_period (the parity of the
  tick after which the swap is applied; q = 0 means the swap tick was a wake tick). For the async
  control q := (t0 + o) mod 2 (pseudo-phase, same split as the period-2 cells).
- Per (spec, offset): frozen census() + frozen classify() (MIN_ELIGIBLE 20, MIN_IDENTITY .90, not
  changed) on (a) pooled trials 1..11, (b) trials with q = 0, (c) trials with q = 1. 99% pair-bootstrap
  CIs (2000 draws, lens_swap.census). Secondary (as W-M deviation D1, labelled): census_follow +
  classify for the abstainers 78f3b0ec, e06701a5 whose frozen census is UNDEFINED.
- Phase-difference statistic: dfX = fX(q=1) - fX(q=0), X in {S, C, N}, 99% pair bootstrap (same resampled
  pairs for both strata, 2000 draws).

## s2 Decision rules (frozen)
- PHASE EFFECT at (spec, offset): both strata defined (>= 20 eligible each) and for some X the 99% CI of
  dfX excludes 0 AND |dfX| >= 0.10.
- CLASS CHANGE: a defined per-phase class differs from the pooled class. It is SUPPORTED if the offset
  also has a PHASE EFFECT; otherwise it is "threshold jitter".
- For pooled readings in {MIXTURE, UNRESOLVED, NEITHER} (frozen census; follow census counted separately):
  - RESOLVES: both strata defined and both per-phase classes in {SITE, CHANNEL}.
  - PARTLY RESOLVES: exactly one stratum class in {SITE, CHANNEL} (the other mixed, NEITHER or UNDEFINED).
  - STAYS MIXED: no stratum class in {SITE, CHANNEL}.
  Per-phase NEITHER is reported separately (a pure-N phase), still counted as not clean.
- Negative control passes if 369f5a5b has PHASE EFFECT at <= 1 of its 16 offsets and every per-phase
  class change is threshold jitter.

## s3 Predictions (frozen)
- P1 (bookkeeping) E1/E2: stratum q = o mod 2 equals the pooled census exactly (same pair-trials), the
  other stratum UNDEFINED (0 eligible). So E1/E2 MIXTUREs (W-M: o3, o7) cannot be phase pooling.
- P2 (negative control) 369f5a5b: no phase effect (<= 1 offset flagged), per-phase classes = pooled up to
  threshold jitter.
- P3 4781b0a1: PHASE EFFECT at >= 8 of o1..15. o14 and o15 at least PARTLY RESOLVE (W-P: o14 C 1.00 on
  even ticks; o15 S 1.00 on even ticks); full resolutions in 4781b0a1: 0-2.
- P4 period-2 odd-Pd RELAY cells: the pooled MIXTUREs (2dccdaa5 o5, c16d5231 o4/o5, follow 78f3b0ec
  o9/o14) are phase pooling: >= half of them RESOLVE (SITE in one phase, CHANNEL in the other).
  Offsets that are pooled SITE or CHANNEL keep that class in both phases.
- P5 overall: most pooled UNRESOLVED/NEITHER readings of 4781b0a1 (sync) STAY MIXED or only PARTLY
  RESOLVE (W-P: N concentrated in one phase, not zero in the other).

## s4 Known-answer checks (each with a must-fail input)
- KA-F runner identity: fork.py output (per-trial score and raw S0 of every arm at its trial) is
  bit-identical to lens_swap.run_arms for 4781b0a1 (period 2), 369f5a5b (async) and the plant, M = 16,
  all offsets, trials {1, 2}. MUST-FAIL: forking one tick late (state after tick k*Pd + o_min + 1)
  is not identical.
- KA-B bookkeeping (pytest): phase labels of synthetic trials equal (k*Pd + o) mod p; stratified census
  on a synthetic table where phase-0 trials are all S and phase-1 all C reads SITE / CHANNEL per phase
  and MIXTURE pooled. MUST-FAIL: labels shifted by one tick swap the per-phase classes (asserted);
  a table with S/C assigned independently of phase reads the same class in both strata.
- KA-P plant (phase effect by construction): plants.echo_hold under c1b_echo_physics with
  update_period 2, HOLD gap 11, cue_len 2, iti 3 (Pd 17, odd), trials 12. Hand derivation: the sensor
  emits only on its even (wake) cue tick te; neighbours receive at te+5 (odd, asleep), the bit waits in
  their INBOX (site array) for one tick, relay at te+6, echo reaches the sensor inbox at te+11 (odd),
  S0 written at te+12 <= ro tick t0+13. Predicted classes (A = t0 even, te = t0; B = t0 odd, te = t0+1):
    A: o0-4 CHANNEL, o5 SITE, o6-10 CHANNEL, o11 SITE, o12 SITE
    B: o0 IDENTITY-BROKEN (the waking cue tick arrives after the swap), o1-5 CHANNEL, o6 SITE,
       o7-11 CHANNEL, o12 SITE
  Pooled: o5, o6, o11 MIXTURE (S/C per trial by phase, phi ~ -1); o0 IDENTITY-BROKEN. The check PASSES
  iff (i) the phase-discordant offsets are exactly {0, 5, 6, 11}, (ii) every per-phase class matches the
  table, (iii) o5, o6, o11 pooled MIXTURE and RESOLVE. Normal accuracy must be >= .95 in both phases.
  MUST-FAIL inputs: (a) the same plant/env with update_period 1: the discordant set must be empty, so
  check (i) fails; (b) period 2 with the trial phase labels randomly permuted (seed 0): check (i)
  must fail (no clean per-"phase" split at o5/o6/o11).
- KA-N negative-control check applied to a positive: the "no phase effect" rule of s2 run on 4781b0a1 and
  on the period-2 plant must FAIL (they have effects).

## s5 Budget
- <= 2.5 h wall, CPU only, torch threads 2 per process, at most 4 processes (8 threads) under a Fabric
  skullport:cpu8 lease (acquired before > 2 threads > 5 min). <= 16 CPU core-hours. No GPU.
- If a spec cannot finish in budget, report it as NOT RUN (never lower M below 256).
