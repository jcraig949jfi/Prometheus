# PREREG -- Z80 affordance-threshold pilot on BEE's VM (EXPLORATORY)

Written 2026-09-28 BEFORE any pilot run. Odysseus worker, ubu001, worktree 7720539d4. Pure ASCII.
Everything this pilot produces is EXPLORATORY: no confirmatory claim, no engine claim, no campaign.
Wall budget: <= 40 min total; stdlib only; 4 worker processes on a shared host (load ~36 at start).

## 1. Question

On BEE's VM (prometheus/z80atlas/vm.py), how does the density of functional self-copiers among random
tapes, the random-walk time to the first copier, and the heredity information those copiers carry change
along the first ladder rungs of DESIGN.md: L0 LDIR on, L1 LDIR cost4, L2 LDIR off, L3 LDIR and LDI off?

## 2. Arms (all: L = 64, entry 0, input byte 42 at IN_BASE and inputs [42], undefined = NOP)

| arm | VM | budget |
|---|---|---|
| A0 | ldir on | 256 |
| A1 | ldir cost4 | 256 |
| A2 | ldir off (LDI, LD (T),A remain) | 256 |
| A3 | ldir off + LDI decoded as NOP (only byte moves remain) | 256 |
| A3b | as A3 | 512 (budget probe; controls and importance only) |
| A4 | NEGATIVE: LDIR, LDI, LD (T),A, LD (S),A all NOP (no window write possible) | 256 |

A1-A4 use vmx.py, a copy of vm.execute with one added line (opcodes in `disabled` decode as NOP).
Gate E0: vmx.execute must equal vm.execute (memory, steps, win_prov, writes) on 1,500 random tapes for
each of ldir on / off / cost4 with disabled = {}. If E0 fails, the pilot stops.

## 3. Detectors

F (functional, op-agnostic): window [64,128) filled with random bytes; run once; child = window after
the run; fid = share of the 64 positions where child == tape. PASS iff fid >= 0.9 in 3 independent
random windows (screen with window 1; confirm with windows 2, 3).
O (BEE own-copy-op rule, as probe.py run()): >= 0.9 L window bytes last written by LDI/LDIR/COPYALL from
source < L, >= 90% from own code, fid >= 0.9. Recorded on window 1 for every F pass (comparability only).
CVT-2 (Artemis certs.py semantics, re-implemented for BEE): per site i, variants x^0x01, x^0x80 and one
seeded random value; lineage = 2 generations; step = run the tape against a seeded random window (draw
k, generation g; common to base and variants); signature = offspring difference vs base lineage;
defined = same non-empty signature in >= 2 of 3 draws. CVT-2 accepted variant = defined in gen 1 AND gen
2. TB2 = log2(1 + distinct gen-2 classes among accepted variants); h2 = accepted / all variants.
PAINTER = F pass with TB2 = 0. Dominant-byte share recorded as a diagnostic only.

## 4. Parts and sample sizes

P0 controls (per arm, 200 plants each, planted at position 0, rest of the tape random unless stated):
- PC_REP8 = vm.replicator(64) (LD S,0; LD T,64; LD C,64; LDIR; HALT)
- PC_LDIR3 = 08 40 15 (LD T,64; LDIR)
- PC_LDI5 = 08 40 14 33 FD (LD T,64; LDI; JR -3)
- PC_MOV8 = 08 40 10 11 24 25 33 FA (LD T,64; LD A,(S); LD (T),A; INC S; INC T; JR -6)
- PAINTER = 01 40 08 40 11 25 33 FC + 56 x 0x40 (paints 0x40; not random background)
  CVT-2 on one instance of each control per arm where F passes.
P1 BASIN specimens: the 6 Z80_64 hits in roles/Bellerophon/forensics_2026-09-23/receipts/BASIN.json:
  F in A0, A1, A2; rule O; CVT-2 in A0.
P2 route-conditional importance estimator (density ~ |C| * 256^-k * r):
- R_LDIR (k = 3): "08 40" at p, "15" at q, p + 2 <= q <= 63; |C| = 1953. 2,000 plants in A0 and A1.
- R_LDI (k = 5): "08 40" at p; "14" at q >= p + 2; back-jump at j in {q+1, q+2} (kind JR 0x33 / DJNZ 0x34 /
  JP 0x30) to target t in [max(p+2, q-2), q], operand computed; j + 1 <= 63. |C| enumerated by the
  script. 3,000 plants in A2 (and A1, A0 for reference if time allows).
- R_MOV (k = 8): "08 40" at p; body at q..q+3 in one of the 3 legal orders of
  {LD A,(S), LD (T),A, INC S, INC T} (read before write, INC S after read, INC T after write); JR back to
  q at q+4; q >= p + 2, q + 5 <= 63. 2,000 plants in A3 (budget 256) and A3b (512).
P3 uniform random sampling (screen + confirm + O + CVT-2 on every F pass):
  A0 30,000; A1 50,000; A2 50,000; A3 10,000; A4 3,000. Seeded.
P4 mutation random walks (Knierim baseline): arms A0, A1, A2; 10 walks x 3,000 steps each; start uniform
  random; each step one uniform site gets one uniform byte, always accepted; F screen at every step,
  confirm on screen pass; the walk stops at its first confirmed copier. Per-step hazard MLE =
  hits / total steps; 95% CI by exact Poisson.
Order of execution (time rule): E0, P0, P1, P2, P3, P4. If the wall clock passes 35 min, the running part
is cut at its last finished chunk and reported as truncated.

## 5. Predictions (from DESIGN.md s4)

- A0 R_LDIR estimate ~3e-5; A1 ~0.3-0.5 x A0; A2 (R_LDI) 1e-10 to 1e-8; A3 density 0 at 256
  (PC_MOV8 fails structurally at 256, passes at 512); A3b R_MOV <= 1e-15.
- Sampling: A0 ~1 hit expected (30k x 3e-5; random windows are stricter than BASIN's zero window);
  A1-A4 0 expected. Walks: 0-2 hits in A0/A1, 0 in A2.
- Every F-pass copier (controls, BASIN, sampled, walked) has TB2 >= 5 bits; PAINTER passes F in A0-A3
  with TB2 = 0 and fails rule O.

## 6. Decision rules (mechanical; exploratory labels)

D1 INSTRUMENT: PASS iff E0 passes; PC_LDIR3 and PC_LDI5 pass F in >= 0.9 of plants in A0; PAINTER TB2
   = 0; PC_REP8 TB2 >= 5; A4 has 0 F passes and 0 window writes on every sampled tape. Else
   INSTRUMENT_FAIL and no further reading.
D2 CALIBRATION: R_LDIR estimate in A0 within [1e-5, 1e-4] -> CALIBRATED; else the estimator is reported
   but not used for rung comparisons.
D3 BLOCK-OP AFFORDANCE: "LDIR is a >= 100x affordance in BEE (single-tape appearance)" iff the A2
   density estimate (R_LDI) AND the A2 sampling upper 95% bound are both <= A0 estimate / 100. The
   sampling bound alone (3.7/50,000 = 7.4e-5 at 0 hits) cannot pass this; the claim rests on D2.
D4 COST: A1/A0 ratio of R_LDIR estimates: >= 0.1 -> "costing is partial removal"; <= 0.01 -> "costing
   acts as removal"; between -> "intermediate".
D5 BUDGET GATE: PC_MOV8 F pass rate < 0.05 at 256 and >= 0.5 at 512 -> "the byte-move route is
   budget-gated at L = 64".
D6 HEREDITY: all F-pass copiers except the painter TB2 >= 5 -> "BEE copiers are informative"; any
   non-control F pass with TB2 = 0 -> PAINTER_PRESENT at that arm.
D7 WALK: report hazard vs density; no decision (underpowered by design).
No result here changes any engine's claims; all outputs are EXPLORATORY inputs to DESIGN.md.
