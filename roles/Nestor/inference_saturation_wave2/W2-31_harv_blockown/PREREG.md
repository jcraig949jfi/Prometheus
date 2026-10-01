# W2-31 PREREG: Harvard x write confinement, the side-1 CVT-R residual

Frozen at 2026-10-01T02:28:33Z (from `date -u`), worktree HEAD 53bbba00a, BEFORE any VM in this folder was
built and BEFORE any scoring run. Nothing in this folder has been executed at freeze time.

## Question
W2-23: under HARV_HALT, side-1 CVT-R = 10/17 (target >= 14), per-interaction good = 895/1020. The residual is the
side-0 partner changing the copier's half through the DATA path before the copier runs (W2-23 p1b, HARV_HALT):
PRE_DAMAGE_BLOCK 114 events (8 good, 106 bad), PRE_DAMAGE_BYTE 147 events (128 good, 19 bad), CLEAN 759 (759 good).
Bad copies = 125 = 106 (block class) + 19 (byte-only class). Block share of the bad-copy residual = 106/125 = 0.848;
block share of pre-damage events = 114/261 = 0.437.

## Design choice: order-protected, not blanket, confinement
A blanket "own half only" rule (W2-7 BLOCK_OWN, or a STORE_OWN over all writes) also forbids the side-1 copier from
writing its child into side 0, so it removes conversion itself and makes the residual question vacuous (good -> ~0).
Primary arms therefore use ORDER PROTECTION:

  A context may not write into the other half of the pair tape while that half's owner has not yet started running
  in this interaction. Writes into its own half, and into a half whose owner has already run, are unchanged.

- Defined from execution order only; it does not know which side is the copier or which bytes are "genome".
- Symmetric in sides. In world order (side 0 first) it shields side 1 from side 0 and leaves side 1 free to write
  its child into side 0. It is exactly "the partner may not write into the copier's half before the copier runs".
- Known cost, stated in advance: in world order a side-0 copier (first mover) can never write into side 1, so side-0
  conversion is removed. This arm is a causal diagnostic, not a proposed viable physics.
- Implementation: the VM remembers, per tape object, which half-bases have started `run` (the tape is a fresh
  bytearray per interaction in p11.interact and in the residual driver). Protection only applies when
  tape_len == 2 * n (always true here: 128 / 64).

## Arms (all on W2-7 DENSE + HARV_HALT, the W2-23 arm with the 10/17)
- HALT: HARV_HALT alone (control; must reproduce W2-23 exactly).
- BO_OP: HARV_HALT x order-protected BLOCK_OWN (block-copy writes into the not-yet-run half dropped; byte stores pass).
- SO_OP: HARV_HALT x order-protected STORE_OWN (block AND byte writes into the not-yet-run half dropped).
- BO_BL: HARV_HALT x blanket BLOCK_OWN (W2-7 BLOCK_OWN literally: block writes outside own half dropped). Caveat control.
- SO_BL: HARV_HALT x blanket STORE_OWN (all writes outside own half dropped). Caveat control.

## Predictions (scored on the 17 Artemis side-1 copiers, side 1, Artemis certs unchanged; 60 W2-16 victims
sha256("W2-16", key, j), world order, FRESH registers, budget 300, mask 0x2A, as W2-23 p1 / W2-16 s4)
- **P1'.** Side-1 CVT-R accept >= 15/17 under SO_OP.
- **P1''.** Under BO_OP the bad-copy residual drops by the block share: predicted bad = 125 - 106 = 19 of 1020.
  PASS iff observed bad copies in [11, 28] (Poisson 95% band around 19).
  Secondary, reported not scored: pre-damage events (copier half changed before the copier runs) fall by ~114,
  from 261 to ~147.

## Decision question D1 (scored as a decision, not a prediction)
"Once partner writes are confined, does the partner running at all still explain any side-1 failure?"
- NO residual (partner writes into the copier's half are the WHOLE cause) iff SO_OP gives CVT-R 17/17 AND
  1020/1020 good, i.e. equal to the no-partner reference (W2-23 / W2-16: 17/17, 1020/1020).
- Otherwise: every remaining bad SO_OP interaction is listed and classified (partner changed its own half that the
  copier then reads / copies over incompletely; or other).

## Decision rules
- PASS: criterion met AND the HALT control reproduces W2-23 exactly (10/17, 895/1020, class counts 759/114/147).
- FAIL: criterion not met with the control reproducing.
- NOT_VERIFIED: control does not reproduce, a self-test fails, or the run cannot complete. Never counted as a pass.

## Controls / reported, not scored
- C-BLANKET: BO_BL and SO_BL side-1 good copies and CVT-R; expected ~0 (conversion removed). This demonstrates the
  caveat; if it is NOT ~0 the copiers reproduce by some other route and that is reported.
- Side-0 copiers (W2-16 s4 set of 18, side 0) under all arms: expected good ~0 under the OP arms (cost of order
  protection) and under the blanket arms.
- P-11 competence of the 17 under each arm (alien_pair.competent).
- Residual decomposition: per interaction, under SO_OP, count the partner's dropped writes into side 1 that would
  have CHANGED a byte, by kind (block / byte store), cross-tabulated with the HALT outcome of the same interaction.

## Self-tests (must pass before any scoring)
- ST1 bit identity: on random pair tapes (both contexts run, fresh tape per pair), each new arm is bit-identical
  (tape, regs, flags, ops, writes, copy_bytes) to W2-7 alien_vm.build('HARV_HALT') wherever its confinement counter
  stays 0, and differs in some runs where it fires (liveness).
- ST2 composition: BO_BL is bit-identical to alien_vm.build('BLOCK_OWN') wherever the HARV counter stays 0.
- ST3 mechanism: hand-assembled programs: side 0 byte store into side 1 is dropped under SO_OP/SO_BL, passes under
  BO_OP; side 0 LDIR into side 1 dropped under BO_OP and SO_OP; side 1 (second mover) LDIR into side 0 passes under
  BO_OP/SO_OP and is dropped under BO_BL/SO_BL; protection state resets on a new tape.
- ST4 same-physics ruler: p11.assay(vm=X) == alien_pair.assay(vm=X, early=False) on a sample; the CVT-R step
  (adapter.cvt_side -> make_step -> p11.interact) receives the arm module (asserted by a counter firing inside a
  CVT-R lineage for the OP arms).

## Budget
<= 30 CPU-min, python -B, static single interactions and CVT lineages only.
