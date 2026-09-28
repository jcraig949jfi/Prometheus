# PILOT RESULT -- BEE affordance-threshold pilot (EXPLORATORY)

Run 2026-09-28, ubu001, 4 worker processes on a shared host (load ~36), wall 535 s. Worktree commit
7720539d4. Preregistration: PREREG.md (written before any run). Script: pilot.py, variant VM: vmx.py.
Output: pilot_result.json. Log: pilot_run.log.
Deviation, disclosed: the first launch crashed while computing a confidence interval (float overflow in
the Poisson CI helper at k ~ 2000; pilot_run_crashed.log). The helper was replaced (exact Poisson in log
space for k <= 30, Wilson above) and the whole deterministic pilot was rerun from the start. No result had
been read before the fix. Nothing else changed.
Every number here is EXPLORATORY. BEE's own claims are unaffected.

## 1. Gates and controls

- E0: vmx.execute equals vm.execute (memory, steps, provenance, writes, opcodes, halts) on 1,500 random
  tapes each for ldir on / off / cost4. 0 mismatches. PASS.
- Functional detector F: pass counts per 200 plants:

| control | A0 on | A1 cost4 | A2 off | A3 no LDIR/LDI (256) | A3b same (512) | A4 no writes |
|---|---|---|---|---|---|---|
| PC_REP8 (8-byte LDIR replicator) | 200 | 200 | 0 | 0 | 0 | 0 |
| PC_LDIR3 (LD T,64; LDIR) | 200 | 200 | 0 | 0 | 0 | 0 |
| PC_LDI5 (LD T,64; LDI; JR -3) | 200 | 200 | 200 | 0 | 0 | 0 |
| PC_MOV8 (byte-move loop) | 0 | 0 | 0 | 0 | 200 | 0 |
| PAINTER (paints 0x40, 58/64 match) | 200 | 200 | 200 | 200 | 200 | 0 |

  BEE's own-copy-op rule O agrees with F on every LDIR/LDI copier and is blind, as expected, to the
  byte-move copier (PC_MOV8 at 512: F 200, O 0) and to the painter (F 200, O 0).
- A4 (negative): 3,000 sampled tapes, 0 window writes, 0 F passes; every control fails. PASS.
- CVT-2 heredity bits (TB2, max log2(193) = 7.59; h2 = share of the 192 variants transmitted twice):
  PC_REP8 7.47-7.50, PC_LDIR3 7.52, PC_LDI5 7.48-7.49, PC_MOV8 (A3b) 7.40 (h2 0.875);
  PAINTER 0.0 in A1, A2, A3, A3b, but 1.0 in A0 (1 of 192 variants).
- The PAINTER A0 case, diagnosed: the variant is site 5, INC T (0x25) -> LDI (0x14). That single
  substitution turns the painter into a real LDI-loop copier of its own tape, and the new sequence
  re-transmits in generation 2. The certificate is right and my prediction was wrong. The painter is
  one mutation away from a copier wherever LDI exists. Whether this variant gets drawn depends on the
  seeded random variant per site, which is why A1 and A2 show 0. This matches the sensitivity note in
  Artemis's P-11 RESULT: a painter that one substitution turns into a reproducer carries 1 bit.
- D1 (mechanical): the clause "PAINTER TB2 = 0" FAILS in A0, so the prereg label is INSTRUMENT_FAIL.
  Every other D1 clause passes. The failure comes from a true transmitted bit, not from a detector
  error, so the readings below are reported, but only as conditional on this disclosed exception.

## 2. Copying: density per rung

Route-conditional importance estimator: density ~ |C| * 256^-k * r (95% CI on r only).

| rung / arm | route (essential bytes k) | configs C | r (pass / plants) | density estimate | log10 |
|---|---|---|---|---|---|
| L0 A0 | LD T,64 ... LDIR (3) | 1,953 | 481/2000 = 0.24 | 2.8e-5 [2.6e-5, 3.0e-5] | -4.55 |
| L1 A1 | same (3) | 1,953 | 237/2000 = 0.12 | 1.4e-5 [1.2e-5, 1.6e-5] | -4.86 |
| L2 A2 | LD T,64 ... LDI + back-jump (5) | 31,335 | 557/3000 = 0.19 | 5.3e-9 [4.9e-9, 5.7e-9] | -8.28 |
| L3 A3 (256 steps) | byte-move loop (8) | 4,959 | 0/2000 | 0 (<= 5e-19); structurally infeasible | -- |
| L3 A3b (512 steps) | byte-move loop (8) | 4,959 | 645/2000 = 0.32 | 8.7e-17 [8.1e-17, 9.2e-17] | -16.06 |

(The LDI route in A0 and A1: 4.9e-9 and 4.8e-9. It is negligible next to LDIR there.)

Uniform sampling (F screen plus confirm): A0 0/30,000 (95% upper 1.2e-4); A1 0/50,000 (7.4e-5);
A2 0/50,000 (7.4e-5); A3 0/10,000 (3.7e-4); A4 0/3,000. Zero screen passes in every arm. The A0 zero
is compatible with BASIN's 3.0e-5 (expected ~0.8 hits; P(0) ~ 0.4), because the random-window detector
is stricter than BASIN's zero window.
Random walks (10 walks x 3,000 steps per arm; one byte substituted per step): 0 hits in A0, A1 and A2.
The per-step hazard is <= 1.2e-4 (95%). This was uninformative, as preregistered (D7).

## 3. Decisions (PREREG s6, applied mechanically)

- D1 INSTRUMENT: INSTRUMENT_FAIL on one clause (see s1). Everything else passes.
- D2 CALIBRATION: A0 estimate 2.8e-5 lies within [1e-5, 1e-4], and BASIN measured 3.0e-5 (n = 200,000).
  CALIBRATED.
- D3 BLOCK-OP >= 100x: the estimator gives A2/A0 = 1.9e-4 (removing LDIR costs ~5,300x, 3.7 decades).
  The prereg, however, also requires the A2 sampling upper bound (7.4e-5) to be <= A0/100 (2.8e-7), and
  it is not. So D3 does NOT pass mechanically. The magnitude rests on the calibrated estimator alone.
- D4 COST: A1/A0 = 0.49, "costing is partial removal". In isolation the LDIR copier still finishes
  under cost4 if it starts early (BASIN specimens: 2 of 6 pass under cost4, 0 of 6 without LDIR).
  BEE's in-world cost4 arm gave 0/300 worlds (P8). The gap between isolation and world is therefore a
  world-level effect (copy cost / viability / lifespan), not an ISA fact.
- D5 BUDGET GATE: PC_MOV8 passes 0/200 at 256 steps and 200/200 at 512. The route is budget-gated
  (>= 5 steps per byte x 64 bytes > 256). At L3 the rung that matters is the step budget.
- D6 HEREDITY: every functional copier is informative, at 7.40-7.52 bits: the 4 control copiers, and all
  6 BEE spontaneous random copiers from BASIN.json (7.46-7.52 bits, h2 0.91-0.95; the first CVT
  measurement of BEE's random copiers). No non-control F pass occurred, so PAINTER_PRESENT is not
  triggered at any arm.
- D7 WALK: no hits; nothing to decide.

## 4. Reading (exploratory)

On BEE's VM, for single-tape appearance, each removal costs roughly:
- L0 -> L1 (price the block op x4): 2x.
- L1/L0 -> L2 (remove the block op, keep LDI): about 3.7 decades.
- L2 -> L3 (remove LDI, keep byte moves): infeasible at the native 256-step budget. At 512 steps the
  density is 8.7e-17, another ~7.8 decades.
With LDIR present, copiers are far more common per tape than with LDI alone (the 3.7 decades above).
In every rung the heredity they carry is the same when they exist (~7.5 of 7.6 possible bits), so the
affordances buy appearance, not heredity quality. Every rung below L0 is beyond uniform sampling and
beyond 3e4-step walks here. The estimator is the only instrument that reaches it, and it is
route-conditional: it counts the enumerated route, not routes nobody thought of. It is a lower-bound-type
estimate for each rung; the unknown-route share is exactly what sampling at L0 bounds (BASIN: all 6
hits were the enumerated LDIR route).
The painter-to-copier single step (s1) is a concrete example of a cheap stepping stone: where LDI
exists, a zero-bit painter sits one mutation from a 7-bit copier.

## 5. Limits

- One VM, L = 64, one input value, isolation only. There is no world, no interaction and no
  selection: Knierim's point that appearance is not spread applies.
- The estimator's CIs cover only r. They assume configurations are rare enough that their union equals
  their sum (true at these rates) and ignore routes outside C.
- The walk and sampling budgets were set by a 40-min cap; the zero hits carry no rung comparison.
- Not tested: the stack route (L3s), reset removal (L4) and everything above. None of the three VMs has
  PUSH; building it is a VM-variant task.
