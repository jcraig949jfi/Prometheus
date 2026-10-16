# Archaeon Phase 2-B SFE Beta -- campaign update 13 (2026-10-16 ~20:30Z)

Since update 12 (2026-10-16 ~05:00Z). This update is for compression, not permission. Numbers are in
archaeon/beta/results/; reasoning is in JOURNAL.md; summary in BETA_FINDINGS.md Finding 5. The review packet
REVIEW_PACKET_FINAL_BETA_F5_COMMUNICATION.txt now runs to section 7h.

## 1. Kin selection is a second, ensemble-invariant route to communication (B106b, B110)
Clonal 4-groups (each genome scored in a group of its own copies) at NORMAL mutation load:

| world | seeded signallers persist | signal re-evolves from one word away |
|---|---|---|
| world 1 (B106b) | 4/4 (random groups: 0/4) | 1/4 (random groups: 0/12) |
| world 2 (B110) | 4/4 | 1/4 |

- The kin route gives identical results in both worlds.
- The group-reward route replicates in direction across worlds (pooled 8/24 vs 0/18), but its RATE is world-dependent
  (7/12 vs 1/12, p ~ .015; B107/B107b). Holding, restore supply, listener decay and the pool lattice are all equal
  across the worlds, so the gap is unexplained (parked).

## 2. Communication does NOT evolve from scratch (B111-B116)
| probe | test | result |
|---|---|---|
| B111 | kin, random gen 0, world 1 | preregistered readout 0/6 (FAILED) |
| B113 | decode the B111 codes | **copy-and-hash**: the scout copies pool 0's raw value; the world reads action % 3; pool values sit on a lattice whose residues carry ~1 bit |
| B114 | pools jittered off the lattice | hash codes vanish (.11 -> .02); hand code keeps .21 (prediction met) |
| B114b | earlier group-selection positives off-lattice | keep their value (.17/.06/.19) -- not exploits |
| B112-NL | kin, random gen 0, jittered world | 0/5 on both readouts (prediction <= 1/6 met; 1 cell lost to a host memory reap) |
| B116 | 300 more kin gens from the one sub-threshold proto-code (11214, info .046) | final best byte-identical in 2/2: strict local optimum |

Verdict: communication evolves from precursors (1-3 opcode words away) under group or kin selection. It does not evolve
from random gen 0 (group 0/12, kin off-lattice 0/5).

## 3. Instrument / process (mine)
- **Self-ablation measures dependence, not information.** B111 11106 dropped .35 under ablation off-lattice, but its
  full reward was BELOW the no-signal baseline. Repaired by B115, a constant-twin information readout (full minus the
  best fixed signal word). It was calibrated and declared for B112-NL before any result. Calibration ledger row added.
- **Lattice worlds admit hash codes.** Future communication worlds will be jittered.
- **B108b over-correction:** I called the world gap 'not established'; B107b's extra seeds reversed that.
- **B106 at E=4 was an instrument failure** (zero signal value in training). New rule: check training-side signal value
  before any evolution run.
- **Two estimates corrected from receipts:** B111 cost (~6.7 core-h, not ~14) and two journal timestamps.

## 4. Compute / leases
- **Window 10 (from 2026-10-16 00:30Z):** ~46/48.
- All leases released with tokens.
- **Host event:** Claude Code reaped B112-NL at ~18:35Z for low system memory (4.6 of 32.5 GB free). It was not
  relaunched. Later runs were sized to memory headroom.

## 5. Active experiments
None. B117 is staged for window 11.

## 6. Next branches
1. **B117 (prereg committed, control passes):** ORDER-free memory read, Finding 3 open question 1. On the L3o VM the
   tag sits in r0 at tick start, so the solution is the L2 read plus exactly one register coupling. Prediction:
   >= 7/8 keyed with median first solve <= 30 (L2-like). If not, the read-chain cost is per coupling, not specific to
   order.
2. **The world rate gap** for the group-reward route (parked; no lead left after the lattice check).
3. **Finding 2 open question 3:** randomise reward semantics to push the foraging rule beyond its generator family.
