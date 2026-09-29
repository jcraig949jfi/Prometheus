# PREREG -- S8 stack route on BEE's VM (EXPLORATORY)

Written 2026-09-28 BEFORE any run of s8.py and before any control was executed. Odysseus disposable spike worker,
ubu001, worktree /home/jcraig/Prometheus-worktrees/odysseus-base-role (HEAD c7958e9f2). Pure ASCII.
Everything here is EXPLORATORY. No engine claim, no campaign. This file is never edited after the run;
amendments go to AMENDMENTS.md.
Budget: <= 40 min wall, ONE process (host shared with a 3-process job), stdlib only.

## 1. Question

PILOT_RESULT.md left open: does a GENERIC fast write path (a Z80-PUSH-like op; no instruction whose semantics move a
byte from memory to memory) restore self-copier density on BEE's VM toward L0 (LDIR present, ~2.8e-5 per random
64-byte tape) from L2 (LDIR removed, 5.3e-9) and L3 (LDIR and LDI removed, byte moves only: 0 at 256 steps)?
If yes, the affordance threshold is "a fast write path plus reset self-location", not "a copy instruction".

## 2. The added op (vm_stack.py; a copy of vm.py; the original is not edited)

ONE opcode, PUSH_A = 0x17. Slot 0x17 is undefined (= NOP) in BEE; 0x16 (COPYALL) is left alone. Defined-opcode
density rises by 1/256 (one NOP value lost), which is the only change to the random-tape byte statistics.
PUSH_A writes REGISTER A to memory at an auto-moving pointer. It never reads memory. A copy still needs a load
(LD A,(S) or LD A,(T)), a source-pointer step (INC S / INC T) and a loop (JR / DJNZ / JP): the same 4 pieces as the
L3 byte-move loop, minus the separate INC T. This is the Z80 PUSH class (register -> (SP), SP moves), not LDI/LDIR.
Three modes (arms below):
- sp_up (arm L3s, PRIMARY): new register SP, reset to L = 0x40 (partner/window start) at every execution;
  PUSH_A: mem[SP] = A; SP += 1. This is Z80 PUSH with the direction mirrored to BEE's increment-only pointers
  (BEE has INC S / INC T and no DEC), and with a reset destination into the partner, as in Cicala 2026 (SP = 0xFF
  resolves into the partner). It bundles two gifts: fast write, and a free destination pointer.
- t_up (arm L3t, decomposition): no new register; PUSH_A: mem[T] = A; T += 1. Fast write path WITHOUT a free
  destination (T resets to 0 like every BEE register, so LD T,64 is needed, as for L0's LDIR copier).
- sp_dn (arm L3z, Z80-literal direction): new SP reset to 2L = 0x80; PUSH_A: SP -= 1; mem[SP] = A. Writes go
  backwards; a copy then needs a backwards read, which BEE can do only via LD A,S; DEC A; LD S,A (6 steps/byte).
  Prediction: structurally infeasible at 256 steps for L = 64 (58 bytes x 6 > 256), as L3's byte-move loop.
Gate E0: vm_stack.execute (stack="none", disabled={}) equals vm.execute (memory, steps, win_prov, writes, opcodes,
halted) on 1,000 random tapes each for ldir on / off / cost4; and equals the pilot's vmx.execute with disabled={LDI}
on 1,000 tapes. Any mismatch -> stop.

## 3. Arms (all L = 64, entry 0, input byte 42 at IN_BASE, inputs [42], undefined = NOP, COPYALL not allowed)

| arm | VM settings | budget |
|---|---|---|
| L0 | ldir on (all BEE gifts; reference) | 256 |
| L2 | ldir off (LDI, byte moves remain) | 256 |
| L3 | ldir off, LDI disabled (byte moves only) | 256 |
| L3s | L3 + PUSH_A sp_up | 256 |
| L3t | L3 + PUSH_A t_up | 256 |
| L3z | L3 + PUSH_A sp_dn | 256 |
| L3z512 | as L3z (budget probe; controls only) | 512 |

## 4. Self-copy criterion (functional + information)

F (as pilot): window [64,128) filled with random bytes; run once; child = window after the run; fid = share of the
64 positions where child == tape. F PASS iff fid >= 0.9 in 3 independent random windows.
Information criterion: CVT-2 as in pilot.py (Artemis certs.py semantics; per site variants x^0x01, x^0x80, one
seeded random; 3 draws, 2 generations; TB2 = log2(1 + distinct gen-2 classes), max 7.59 bits; h2 = accepted share).
SELF-COPIER = F pass AND TB2 >= 5 bits. PAINTER = F pass with TB2 = 0 (homopolymer painters must land here).
The F, CVT-2, estimator and CI code is imported/copied from ../pilot.py unchanged except that run() calls
vm_stack.execute with the arm's settings.

## 5. Parts and sample sizes (single process, deterministic seeds)

P0 controls, 100 plants each (code at position 0, rest random; painters are fixed tapes), F pass counts:
- PC_LDIR3 = 08 40 15 (LD T,64; LDIR) in L0, L3s.
- PC_LDI5 = 08 40 14 33 FD in L2, L3.
- PC_MOV8 = 08 40 10 11 24 25 33 FA in L3, L3s.
- PC_PUT5 = 10 24 17 33 FB (LD A,(S); INC S; PUSH_A; JR -5) -- the hand-built L3s copier -- in L3s (must pass
  >= 0.9), L3 (must fail: 0x17 is NOP there), L3t, L3z.
- PC_TPUT7 = 08 40 10 24 17 33 FB (LD T,64; then the same loop) in L3t (must pass >= 0.9).
- PC_ZPUSH9 = 07 40 49 23 47 10 17 33 F9 (LD S,64; LD A,S; DEC A; LD S,A; LD A,(S); PUSH_A; JR -7) in L3z
  (predicted fail) and L3z512 (predicted pass).
- PAINTER (pilot) = 01 40 08 40 11 25 33 FC + 56 x 0x40, in L3, L3s, L3t, L3z.
- PPAINT = 01 40 17 33 FD + 59 x 0x40 (LD A,0x40; PUSH_A; JR -3), in L3s, L3z.
- TPAINT = 08 40 01 40 17 33 FD + 57 x 0x40, in L3t.
CVT-2 on the first F-passing instance of each (control, arm) with F >= 1 pass.
P2 route-conditional importance estimator (pilot's, density ~ |C| * 256^-k * r, 95% CI on r only):
- L0 R_LDIR (k 3, |C| 1953): 1,000 plants (re-check of the pilot's calibrated 2.8e-5).
- L2 R_LDI (k 5, |C| 31,335): 1,500 plants (re-check of the pilot's 5.3e-9).
- L3s R_PUT (k 5): contiguous body at q..q+2 in order (LD A,(X); INC X; PUSH_A) or (LD A,(X); PUSH_A; INC X),
  X in {S, T} (both reset to 0), then a back-jump at q+3..q+4 to q: JR d (0x33), DJNZ d (0x34) or JP q (0x30);
  q in [0, 59]. |C| = 60 x 2 x 2 x 3 = 720. 3,000 plants. (A gap inside the loop costs a step per byte, which
  makes 58 bytes x 5 steps > 256, so contiguity is forced, not assumed.)
- L3t R_TPUT (k 7): "08 40" at p, body at q >= p + 2 in order (LD A,(S); INC S; PUSH_A) or (LD A,(S); PUSH_A;
  INC S), back-jump at q+3..q+4 (3 kinds), q + 4 <= 63. |C| enumerated by the script. 3,000 plants.
- L3 R_MOV at 256 is not re-run (pilot: 0/2000, structurally infeasible); its density is taken as 0.
- CVT-2 on up to 20 F-passing plants per estimator arm; the reported density is multiplied by the SELF-COPIER
  share among them (TB2 >= 5).
P3 uniform sampling (F screen with window 1, confirm with 2 more; CVT-2 on up to 6 hits per arm):
  L3s 150,000; L3t 40,000; L3z 30,000; L3 20,000. Unknown-route bound only (predicted 0 hits everywhere).
P4 mutation walks (Knierim baseline) in L3s: 10 walks x 2,000 steps. Uninformative by design unless a hit occurs.
Calibration of the estimator: the pilot's L0 R_LDIR estimate 2.8e-5 [2.6e-5, 3.0e-5] matched BASIN's direct
count 3.0e-5 (6/200,000, own-copy rule). Here: CALIBRATED iff the L0 re-check lies in [1e-5, 1e-4].
Order: E0, P0, P0-CVT, P2, P2-CVT, P3, P4. Wall rule: if 33 min pass, the running part stops at its last
finished chunk and is reported as truncated.

## 6. Decision rules (mechanical; EXPLORATORY labels)

D1 INSTRUMENT: PASS iff E0 passes; PC_PUT5 passes F >= 0.9 in L3s; PC_TPUT7 >= 0.9 in L3t; PC_LDIR3 >= 0.9 in L0;
   PC_PUT5 = 0 in L3; PPAINT, TPAINT and PAINTER have TB2 = 0 wherever they pass F (a painter with TB2 > 0 is
   diagnosed as in the pilot: if the transmitted variant turns it into a real copier, report and continue);
   PC_PUT5 (L3s) and PC_TPUT7 (L3t) have TB2 >= 5. Otherwise INSTRUMENT_FAIL, no verdict.
D2 CALIBRATION: L0 estimate in [1e-5, 1e-4] -> CALIBRATED; else the pilot's calibrated L0 value 2.8e-5 is used
   as the reference and the discrepancy reported.
D3 VERDICT for L3s (primary), and in the same way for L3t and L3z, with d(X) = log10 of the point estimate
   (self-copier-corrected), d(L3) = -inf at 256, reference d(L0) and d(L2) from this run's re-check (pilot values
   if D2 fails):
   - "L3s RESTORES COPYING"  iff d(L3s) >= d(L0) - 1;
   - "PARTIAL"               iff not the above and d(L3s) >= max(d(L2), d(L3)) + 1;
   - "NO"                    otherwise. If L3s density > 0 while L3 = 0 at 256, the label is written
                              "NO (feasibility restored, below the L2 level + 1 decade)".
   If the 95% CI of d(L3s) crosses the boundary that decides the label, the label gets the suffix "(BOUNDARY)".
D4 THRESHOLD READING: RESTORES -> the threshold is "fast write + reset self-location/destination", not a copy op.
   PARTIAL -> the push route is a real but smaller affordance than LDIR. NO -> on BEE, a generic fast write does not
   substitute for the copy op in single-tape appearance density.
D5 DECOMPOSITION (descriptive): d(L3s) - d(L3t) = the value of the free destination pointer (reset SP) given the
   fast write; d(L3t) vs L3 = 0 = the value of the fast write alone (4 vs 5 steps per byte). L3z: whether the
   Z80-literal direction is usable at all on BEE's increment-only pointers.
D6 LENGTH: hand-built L3s copier length (PC_PUT5, 5 bytes) vs the shortest L0 copier (LD T,64; LDIR = 3 bytes,
   BASIN/POST_CAMPAIGN_FORENSICS s2.6).

## 7. Predictions (to be wrong about)

- PC_PUT5: 100/100 in L3s (64 bytes in exactly 255 steps); 0 in L3; PC_ZPUSH9 0 at 256, 100 at 512.
- d(L3s) ~ -10 to -11 (720 configs, 5 essential bytes, r ~ 0.05-0.2): about 5.5-6.5 decades below L0 and 1-2
  decades BELOW L2 -> verdict "NO (feasibility restored ...)". d(L3t) ~ -14. L3z: 0 at 256.
- Every estimator pass is a self-copier (TB2 ~7.4-7.5); every painter TB2 = 0; sampling 0 hits in every arm.
