# W-M PLAN: T-INS-6 carrier-swap mixture test (E-ANANKE-W-M, thr-8c7342a7d513, MWO-0001)

Frozen 2026-09-29T03:40Z, BEFORE any analysis run. Thresholds below are not
changed after results are seen; any deviation is logged in LOG.md as a
deviation, with the reason.

Context read before this plan (raw evidence only): COMMON_RULES*.md,
prometheus/ananke/{lens,envs,plants}.py (+ engine checkpoint API), W-I traj.py,
identity_check.py, main.py, out/identity_check.json, out/traj_table.csv (the
reader/phys letter columns), out/traj_<7 JOINT cells>.json (phi per offset),
designed_echoes/{PLAN.md, design.py, run.log, instruments.json}. NOT read:
W-I REPORT.md/LOG.md/PLAN.md, designed_echoes/RESULT.md, any research/*.md
synthesis. (traj_table.csv's letter columns are W-I's labels, i.e. W-I's
interpretation; noted as mild contamination.)

## 0. Algebra (why the sum is forced, and what is not)

Mirror pair (A, B): shared exogenous draws, negated cues, ans_B = -ans_A.
Site swap:    A' = (site_B, chan_A), B' = (site_A, chan_B).
Channel swap: A''= (site_A, chan_B), B''= (site_B, chan_A).
So A'' == B' and B'' == A' as states. If NO mirror-different input arrives
between the swap and the readout, the chimera trajectories are identical, so
out(A, chan) == out(B, site) and out(B, chan) == out(A, site) (IDENTITY).
Per (pair, trial) there are then only two chimeras, X=(site_A,chan_B) and
Y=(site_B,chan_A), and four patterns:
  S (site-follow):    X->ans_A, Y->ans_B   site swap wrong in A and B, chan right
  C (channel-follow): X->ans_B, Y->ans_A   chan swap wrong in A and B, site right
  N (neither):        X == Y (both give ans_A, or both ans_B): the chimera
                      output is fixed by something other than either carrier
                      alone (interaction / bias); in world terms one partner
                      reads (0,0) and the other (1,1).
Pair-level site_acc = fC + fN/2, chan_acc = fS + fN/2, sum = 1 always under
identity. Therefore site_acc = chan_acc = 0.5 ("M" / both CHANCE) is produced
EQUALLY by a 50/50 per-trial S/C mixture and by 100% N. The sum cannot
separate them; the pattern census (fS, fC, fN) and phi can.
phi = corr over (world, trial) cells with normal correct of
x = site-swap wrong, y = channel-swap wrong. S and C cells are (1,0), (0,1);
N contributes (0,0)+(1,1). Mixture of S and C -> phi strongly negative;
S or C plus N -> phi positive; pure S (or pure C) -> phi undefined (constant).

## 1. Instruments to build (lens_ins6.py, tested)

(i) Batched arms (promoted from W-I traj.run_arms): blocks of 64 worlds per arm
    in one World; swaps act inside a block only. Modes: EVERY (swap at t0+o in
    every trial; W-I's design) and SINGLE (swap at t0_k+o in trial k only; the
    block's run may stop at trial k's readout). Must be bit-identical to
    lens.run with the same hooks (selfcheck test).
(ii) census(): per (pair, trial) with BOTH partners normal-correct and
    decisive arms: identity fraction (outcome identity and raw S0 readout
    identity), pattern fractions fS/fC/fN, ties/broken counts, world-level 2x2
    table and phi, with 99% pair-bootstrap CIs (resampling pairs, 2000 draws,
    fixed seed).
(iii) classify() (FROZEN decision rule; eligible = pair-trials in census):
    UNDEFINED  eligible < 20, or identity fraction < 0.90 (patterns are not
               interpretable when the chimeras are not shared; reported as
               IDENTITY-BROKEN with the world-level phi only)
    SITE       fS >= 0.80
    CHANNEL    fC >= 0.80
    MIXTURE    fS >= 0.15 and fC >= 0.15 and fS + fC >= 0.70 and phi hi99 < -0.30
    NEITHER    fN >= 0.50
    UNRESOLVED otherwise
(iv) twin_profile promoted unchanged in semantics (two-axis physical axis).

## 2. Known-answer tests (pytest, CPU, fast) and their must-fail inputs

KA1 SITE latch: plants.hold_latch on c1b_echo_physics(prog_len 12, pw 1),
    HOLD, SINGLE, offset mid-gap: classify == SITE, identity == 1.0.
    Must-fail input: echo_hold plant (bit in flight) -> classify != SITE.
KA2 CHANNEL echo: plants.echo_hold, mid-gap offset: classify == CHANNEL.
    Must-fail input: hold_latch -> != CHANNEL.
KA3 no memory (plants 'null'): no normal-correct cells -> UNDEFINED; never
    MIXTURE/SITE/CHANNEL. Must-fail input: latch (-> not UNDEFINED).
KA4 statistic: synthetic 50/50 S/C table -> MIXTURE, phi ~ -1; synthetic 100% N
    table with the SAME pair-level site_acc = chan_acc = 0.5 -> NEITHER (phi
    > 0). Pure-S table with 5% C noise -> SITE, not MIXTURE (phi may be
    negative there: the fraction rule, not phi, must stop it).
KA5 identity: SINGLE swap after the cue in RELAY (relay_flood on
    c1b_da_physics or echo) -> identity == 1.0. Must-fail input: swap at
    o = -1 (before the cue; mirror-different cue arrives after the swap) ->
    identity < 1 (on a specimen that reads the cue).
KA6 batched == lens.run bit-identity for EVERY and SINGLE modes; must-fail:
    comparing with lens.run hooked at a different tick -> not equal.
KA7 designed handoff (E2_pipe2, design.build, HOLD gap 11, ro offset 13):
    predicted from the design (echo out, relay, return, sensor inbox, S2 ->
    S1 -> S0 pipeline at update_period 2): EARLY offsets channel-dominant,
    LATE offsets site. Frozen pass rule: (a) some offset o in [2, 7] has
    fC >= 0.60 (channel-dominant) OR classify CHANNEL; (b) every offset
    o in [9, 12] (lags -4..-1) is SITE; (c) the last channel-dominant offset
    < the first offset of the final SITE run; (d) the handoff (first offset of
    the final SITE run) lies at lag -8..-4 (o in [5, 9]).
    Must-fail input: the same rule applied to E1_canon (pipeline 0: bit
    enters S0 only at the last wake) must fail (b) (lags -4, -3 channel per
    instruments.json) and to hold_latch (never channel) must fail (a).
    If E2 fails KA7 that is reported as a failed known-answer test (the
    instrument, or my reading of the design, is wrong), not repaired.

## 3. Application (after all KA tests pass)

Cells: 2dccdaa5 c16d5231 78f3b0ec 8c37f32e e06701a5 369f5a5b 4781b0a1
(census-JOINT, W-I retested) + E2_pipe2 at gap 11. Seeds
assays.world_seeds(0x5EE, 64) (W-I's reader seeds) for the cells; 0x5F1 for E2.
Offsets -1 .. ro_off-1 (W-I's). Arms site_all and channel_all (W-I's SITE /
FLIGHT). Both modes: EVERY (all trials >= 1 scored, trial 0 excluded like W-I)
and SINGLE (trials: all k >= 1 if compute allows, else k in {2,4,..} fixed by
timing BEFORE any result is looked at). Per (cell, offset, mode): census +
classify.

Predictions (frozen):
P1 SINGLE mode: identity fraction = 1.00 at every offset o >= cue_len - 1 for
   RELAY/MAJ (no input between swap and readout by construction). Any
   departure = a hidden exogenous difference between partners (an instrument
   defect) and is reported.
P2 EVERY mode: identity < 0.90 somewhere for 369f5a5b (W-I: ~0.65) and ~1 for
   the rest.
P3 The W-I "M"/"J" offsets (both-CHANCE) resolve mostly as NEITHER rather than
   MIXTURE (weak prior: W-I's phi at those offsets is mostly None or mildly
   positive; 2dccdaa5 o5 phi -0.94 and 78f3b0ec o9-15 ~-0.6 are the MIXTURE
   candidates).
P4 SINGLE vs EVERY: classifications agree at >= 80% of (cell, offset) where
   both are defined; disagreements concentrate in 369f5a5b.
Decision: "single-trial changes a classification" = a (cell, offset) whose
class differs between modes with both classes not UNDEFINED/UNRESOLVED, OR
flips between MIXTURE and any other class. Reported cell by cell.

Compute: CPU only, torch threads 2 per process. If > 2 threads total for
> 5 min is needed, acquire `python -m fabric lease acquire skullport:cpu8`
first; BUSY/UNAVAILABLE -> QUEUE.md. Wall budget ~3 h.
