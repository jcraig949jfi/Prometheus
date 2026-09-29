# RESULT -- S8 stack route on BEE's VM (EXPLORATORY)

Run 2026-09-28, ubu001, ONE process, wall 283 s (cap 40 min), stdlib only. Worktree HEAD c7958e9f2.
Prereg: PREREG.md (written before any run; not edited; no amendments were needed). Script s8.py, VM vm_stack.py,
data s8_result.json, log s8_run.log. Nothing was truncated. Every number is EXPLORATORY.

## 1. What was added (vm_stack.py; vm.py untouched)

One opcode, PUSH_A = 0x17 (an undefined = NOP slot in BEE). It writes REGISTER A to memory through an auto-moving
pointer and never reads memory, so it is the Z80 PUSH class, not a memory-to-memory move. A copier still needs a
load, a source-pointer increment and a loop. Three modes:
- L3s (primary), sp_up: new SP reset to L = 0x40 each run; mem[SP] = A; SP += 1. That is a fast write plus a free
  destination into the partner, like Cicala's SP = 0xFF. The direction is mirrored because BEE has no DEC.
- L3t, t_up: mem[T] = A; T += 1. This is the fast write alone. T resets to 0, so the program must set LD T,64.
- L3z, sp_dn: the literal Z80 direction. SP resets to 2L, then SP -= 1; mem[SP] = A.
E0: vm_stack equals vm.execute with the defaults (ldir on/off/cost4) and equals the pilot's vmx for L3 on
1,000 tapes each: 0 mismatches.

## 2. Instrument (D1: PASS, every clause)

F passes per 100 plants: PC_LDIR3 L0 100; PC_LDI5 L2 100; PC_PUT5 (10 24 17 33 FB) L3s 100, L3 0, L3t 0, L3z 0;
PC_TPUT7 L3t 100; PC_ZPUSH9 L3z 0 at 256 and 100 at 512; PC_MOV8 L3 0 and L3s 0; PC_LDIR3 L3s 0.
All three painters (PAINTER, PPAINT, TPAINT) pass F 100/100 in every arm tested, and CVT-2 gives them TB2 = 0.00
(h2 0) in all 7 cases. The information criterion rejects them. Copier controls: TB2 7.38-7.52 (h2 0.86-0.95).
Every estimator pass checked by CVT-2 is a self-copier: 20/20 per arm, TB2 7.13-7.55. The self-copier share is 1.0.

## 3. Densities (route-conditional estimator, density ~ |C| 256^-k r, 95% CI on r only)

| arm | route (k essential bytes) | configs C | r | density [95% CI] | log10 |
|---|---|---|---|---|---|
| L0 | LD T,64 .. LDIR (3) | 1,953 | 230/1000 | 2.68e-5 [2.39e-5, 2.99e-5] | -4.57 |
| L2 | LD T,64 .. LDI + back-jump (5) | 31,335 | 270/1500 | 5.13e-9 [4.60e-9, 5.71e-9] | -8.29 |
| L3 | byte-move loop (8) | -- | pilot 0/2000 | 0 at 256 (structural) | -inf |
| L3s | LD A,(X); INC X; PUSH_A; jump (5) | 720 | 963/3000 | 2.10e-10 [1.99e-10, 2.21e-10] | -9.68 |
| L3t | LD T,64 .. LD A,(S); INC S; PUSH_A; jump (7) | 10,266 | 355/3000 | 1.69e-14 [1.53e-14, 1.86e-14] | -13.77 |
| L3z | backwards-read push loop | -- | control 0/100 | 0 at 256 (6 steps/byte; structural) | -inf |

Calibration (D2): the L0 re-check is 2.68e-5, in [1e-5, 1e-4], and matches the pilot's 2.8e-5 and BASIN's 3.0e-5.
CALIBRATED. The L2 re-check of 5.13e-9 matches the pilot's 5.3e-9.
Uniform sampling, 0 hits and 0 screen passes in every arm (95% upper bounds): L3s 0/150,000 (2.5e-5); L3t
0/40,000 (9.2e-5); L3z 0/30,000 (1.2e-4); L3 0/20,000 (1.8e-4). With the op, L3s tapes write into the window
often (30,707/150,000 = 20%, against L3's 430/20,000 = 2%), but none of those writes form a copy.
Walks in L3s: 10 x 2,000 steps, 0 hits. Per-step hazard <= 1.8e-4. Uninformative, as preregistered.

## 4. Verdict (D3, mechanical)

L3s: d = -9.68. RESTORES needs d >= d(L0) - 1 = -5.57. PARTIAL needs d >= max(d(L2), d(L3)) + 1 = -7.29.
Neither holds. The CI (-9.70, -9.66) is far from both boundaries.
-> "NO (feasibility restored, below the L2 level + 1 decade)". L3s is 5.1 decades below L0 and 1.4 decades below
   L2, and it is > 0 where L3 is 0 at 256 steps.
L3t: -13.77 -> "NO (feasibility restored, below the L2 level + 1 decade)". L3z: 0 at 256 -> "NO".
Predictions: L3s was predicted at -10 to -11 and came out -9.7, because r = 0.32 was higher than expected. L3t was
predicted at ~-14 and came out -13.8. Every control and structural prediction held.

## 5. Lengths (D6)

The hand-built L3s copier PC_PUT5 is 5 bytes (LD A,(S); INC S; PUSH_A; JR -5). It copies all 64 bytes in 255 of
256 steps, with no setup. The shortest L0 copier is 3 bytes (LD T,64; LDIR). L3t needs 7 bytes. The literal-direction
L3z copier needs 9 bytes and 512 steps.

## 6. Reading (exploratory)

- On BEE, a generic fast write path does not substitute for the copy instruction. At the same k = 5, even the
  most favourable version (fast write plus a reset destination) is 1.4 decades rarer than the LDI route.
- Decomposition (D5):
  - The free destination pointer is worth 4.1 decades (L3s vs L3t).
  - The fast write alone turns L3's structural zero into 1.7e-14. Its value is budget feasibility (4 steps per
    byte instead of 5), not density.
  - The literal Z80 direction is unusable on BEE's increment-only pointers.
- Density follows the number of essential bytes, about 2.4 decades per byte, times the number of placements.
  LDIR wins because it is 1 byte and its loop is implicit (C = 0 sweeps to the budget). The NOP slide lets its setup
  sit anywhere. The push loop needs 5 contiguous bytes (any gap breaks the 256-step budget), so it has only 720
  placements against LDI's 31,335.
- On this evidence, the threshold on BEE is not "a fast write path plus reset self-location". It is the essential-byte
  cost of the copy loop. An op that implicitly loops (LDIR) or merges load, advance and store (LDI) removes 2-3 of
  those bytes. PUSH removes one byte and one step.
- Why Z80 soups still get PUSH copiers first is not explained by per-tape density here. Candidates, all untested:
  pair interaction and selection (Knierim: appearance is not spread); 2-byte PUSH on a real Z80; 16-32-byte
  programs; straight-line self-describing Load-Push (the "01 c5" pattern), which fills the tape and is close to a
  periodic painter.

## 7. Limits

- The estimator is route-conditional and counts only the enumerated routes. Uniform sampling bounds all routes in
  L3s at <= 2.5e-5 (95%). That excludes a full L0-level density but not "within 1 decade of L0" (>= 2.7e-6) from
  unknown routes. No unknown route showed up in 150,000 tapes or 20,000 walk steps.
- One VM, L = 64, budget 256, one input, isolation only: no world, pairs or selection. PUSH_A is 1 byte, 1 step,
  single-byte.
- The direction was mirrored in L3s to match BEE's pointers. A DEC S op would give the Z80 direction a 7-byte route
  (LD S,64 plus a 4-step loop) that was not run. From the L3t analogue, expect roughly 1e-14.
