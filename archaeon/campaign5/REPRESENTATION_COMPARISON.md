+=====================================================================+
|  OLD versus NEW REPRESENTATION -- the comparison the directive asked  |
|  Archaeon[m2-49ee5a4d]   Campaign 5   2026-09-18                     |
+=====================================================================+

OLD  proteus.foundry.vm.Player: total interpreter. Opcode word mod 25,
     register fields mod n_regs. Every word sequence is a program;
     932/932 out-of-table words were reinterpreted in C4-01; D1 cannot
     fire; no local failure exists.
NEW  archaeon/campaign5/repb.PlayerB: narrow in-table encoding. Opcode
     word defined iff < 25; register field the opcode reads defined iff
     < n_regs; anything else is a FAULT. FAIL ends the evaluation
     (reward 0); FIZZLE skips the instruction and counts it. Addresses
     from register contents and jump offsets stay modulo tape; unread
     fields cannot fault. canonicalize(P) carries every old program's
     meaning across exactly (57/57 parents, reward/ops/statuses).
     Grammar B = v0.4 with in-range redraws; operand_perturbation kept
     raw (the crossing operator). Proteus's VM untouched.

-----------------------------------------------------------------------
                                  OLD (total)    NEW FAIL      NEW FIZZLE
-----------------------------------------------------------------------
sampled programs (C5-04, W0, no selection, viable share)
  raw uniform words                 .170          .000          .000
  generator-valid                   .152          .150          .152
  valid + 2 injected faults         .170          .017          .118
  reach the floor (any generator)   .000          .000          .000

single edits of 57 competent parents (C5-05; grammar v0.4 / grammar B)
  crossing share of children        --            .386 / .055   .386 / .055
  executed (trap) among crossing    --            .84 / .86     (faults)
  D5 neutral, all children          .439 / .435   .311 / .410   .311 / .410
  D5 neutral, non-crossing only     .442 / .429   .441 / .428   .441 / .428
  D2+D3 death, all children         .538 / .546   .348 / .517   .348 / .517
  DT trapped / DF faulted           --            .327 / .057   .327 / .057
  D6 exaptation                     .008 / .007   .006 / .006   .006 / .006
  D7 improvement on own environment .000          .000          .000
  C4-01 replication (arm R)         5,586/5,586   --            --

matched crossing children with an executed fault (C5-06; n = 1,449)
  competent under this interpreter  .436 (OLD)    .000 (DT)     .506
  RECOVERY (NEW live, OLD dead)     --            --            234 (229 replicated)
  INSULATION_LOSS (OLD live, NEW dead) --         --            157 (154 replicated)
  by fault kind: opcode faults recover (209 vs 15); register faults are
  lost when skipped (142 vs 25).

cost of recovery (C5-07, 229 recovered children)
  ops ratio to parent               --            --            median 1.00; 2% > 1.10x
  second-edit neutrality vs parent  --            --            +.023 (inside the band)
  lost function elsewhere           --            --            4.4%

robustness mechanism (C5-08; neutral share, 57 parents / dead code removed)
  R (full / ablated)                .435 / .409   .410 / .384   .431 / .405
  boundary's own GAP (FIZZLE-FAIL)  --            .021 (full) = .021 (ablated)
  length bins 1-8 / 9-16 / 17-32 / 33+ (OLD, full): .17 / .46 / .57 / .71

evolution at equal total compute (C5-09; 4 screened worlds x 6 seeds,
N=50, G=100, E=16; cells vs OLD+v0.4 by 1/16)   OLD+B    NEW FAIL   NEW FIZZLE
  won / lost / tied of 24                        0/0/24   1/0/23     1/0/23
  first held-out gain over the starting best     none     none       none
  population crossing share at the end (mean)    .65-.94  .44-.72    .61-.93
  population with an executed fault at the end   .00      .07-.10    .46-.80
  reading                                        NO_GAIN  NO_GAIN    NO_GAIN

-----------------------------------------------------------------------
IN ONE PARAGRAPH
-----------------------------------------------------------------------
The new representation creates the local failure boundary the old one
lacked, and it is real: sampled raw programs die on it, single edits
cross it at a measured rate, and when the fault is executed the two
representations fail in OPPOSITE directions -- a broken opcode word is
lethal when reinterpreted and harmless when skipped, a broken register
field is harmless when wrapped and lethal when skipped. Skipping is free
for the program that survives it. None of this changes what the
representation can discover: on worlds with headroom, at equal compute,
no arm under either representation moved an elite's held-out reward by
a band in 96 cells, and the geometry of children that do not touch the
boundary is the old geometry to the third decimal.
+=====================================================================+
