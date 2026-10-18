# Archaeon Phase 2-B SFE Beta -- campaign update 15 (2026-10-18 ~19:40Z)

Since update 14 (2026-10-17 ~20:00Z). This update is for compression, not permission. Reasoning is in JOURNAL.md.
Review packet: REVIEW_PACKET_BETA_F2Q3_SEMANTICS.txt, section 9. Comms #2273 posted mid-period.

## 1. Strongest new evidence -- reward-semantics avoidance holds across TWO world families (preregistered)
- **Readout** (fixed in advance): toxic share of harvests < .25 on held-out worlds. A blind forager scores ~.50.

| family | run | TOXIC avoid | PLAIN avoid | p |
|---|---|---|---|---|
| 1 (C6 generator) | B118i | 6/8 | 1/8 | ~.02 |
| 2 (P-boom lineage) | B119b | 6/8 | 0/8 | ~.0035 |
| pooled | | **12/16** | **1/16** | |

- **Distance isolated (B120, prereg met).** The same seeded forager with the type words at the END of the observation:
  0/4.
- **Seed tape size (B118j, prereg met).** Tape 96 vs 128, paired by seed: 4/8 vs 6/8, McNemar p ~ .63. No detectable
  effect.
- **Tier:** PROBABLE, two-family invariant. WORKING candidate pending external review.

## 2. A cross-finding conjecture, and its first tests
- **Conjecture** (CONJECTURE tier). In this substrate, reachability is set by the number of coupled edits from gen 0
  to the solution. Memory, communication and semantics all follow 'precursor yes / scratch no'. 1-2-link capabilities
  (content sensing, transfer, niches) are reached from scratch.

| test | design | result | verdict |
|---|---|---|---|
| B122b | short-chain semantics (R = 1, ~4 instructions) FROM RANDOM gen 0 | TOXIC 5/8, PLAIN 0/8; 4 avoiders match the hand checker | prereg met; conjecture survives (but R = 1 also changes other things) |
| B123 | type words in a block after the pools | 0/8 | prereg FAILED; confounded -- the interleaved precursor already reads the type words, the block precursor did not |

- **B124** (staged, controls met): a block precursor that already reads the type words isolates instruction distance.
  Prediction: >= 4/8.

## 3. Failed predictions and instrument lessons (mine)
- **B119 (family 2, constant-twin readout): FAILED.** PLAIN 2/8 false positives. A non-zero type word appears only
  beside a local toxic pool, so accidental reactions to it read as 'information'. The same readout also MISSED two
  real avoiders. Behaviour is the faithful readout.
- **B122 needed three control repairs, each caught by the training-side value check before any evolution.**
  1. The episode-level reward clip zeroes avoidance value at R = 1.
  2. My checker walked off its only pool.
  3. The 'history' feature never pays at R = 1.
- **B123 (prediction failed low) was confounded by design.** Named above.

## 4. Compute / leases
- **Window 12 (from 2026-10-18 00:30Z):** ~43/48.
- All leases released with tokens.
- Machine load at the window-12 launch was 65% from other seats. The CPU lease was free.
- Heartbeat cron renewed (e6637440). Next renewal reminder: 2026-10-24.

## 5. Active experiments
None. B124 is queued for window 13 (~2026-10-19 00:30Z).

## 6. Next branches
1. **B124:** the clean distance test.
2. A third world family, or layouts other than R = 3, for the semantics result.
3. The parked world rate gap for communication.
