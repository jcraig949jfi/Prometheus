# Archaeon Phase 2-B SFE Beta -- campaign update 14 (2026-10-17 ~20:00Z)

Since update 13 (2026-10-16 ~20:30Z). This update is for compression, not permission. Reasoning is in JOURNAL.md. The
new review packet is REVIEW_PACKET_BETA_F2Q3_SEMANTICS.txt.

## 1. Strongest new evidence -- reward SEMANTICS evolves from a working forager (B118 series; comms #2270)
- **World.** Each pool is toxic with p = 1/2, and a toxic harvest costs 2x its value. A type word interleaved after
  each pool word says which pools are toxic.
- **Start and arms.** Gen 0 is a hand forager that ignores types. TOXIC is compared with PLAIN: the same layout, no
  toxicity.

| run | TOXIC readers | PLAIN | note |
|---|---|---|---|
| B118f | 4/8 | 0/8 | mixed seed (one crash rerun) |
| B118g | 4/8 | 0/8 | clean single seed; prereg MET (p ~ .038) |
| pooled | **8/16** | **0/16** | p ~ .001 |

- **Readout.** Constant-twin information: lift minus the best lift with every type word fixed. This measures
  information, not dependence.
- **Behaviour.** Readers take 10-16% of their harvests from toxic pools, vs 52% for blind foragers (B118h).
- **Bounds.** From random gen 0 it is not reached (0/4, 0/4). With the type words at the end of the observation, 0/4.
- **Tier:** PROBABLE within one world family. Same shape as communication: precursors yes, scratch no.

## 2. Memory: the ORDER coupling, isolated (B117)
- **Setup.** The tag is in r0 at tick start, so the read is the 2-link read plus one register coupling.
- **Result.** Keyed 8/8, median first solve ~21 generations (prediction met).

| read | keyed | median first solve (gen) |
|---|---|---|
| 2 links | 8/8 | ~8 |
| order-free (B117) | 8/8 | ~21 |
| order kept (B57) | 6/8 | ~72 |

- **Reading.** Order costs more than one register coupling. Couplings are not equal-weight. Finding 3 open question 1
  is answered.

## 3. Failed predictions (reported as such)
- **B118 controls.** The type-checker value was positive in 8/12 worlds; 9 were needed. That design was not run.
- **B118b (0/4), B118c (0/4), B118d (1/4 against >= 2/4).** These were test-design failures (distance, random gen 0)
  and are kept separate from the law verdict.

## 4. Instrument / process (mine)
- **Hand seed manifest.** It used tape_words 100. The GA's halve/double mutation made an invalid 50 and crashed one
  cell. Repaired with power-of-two tapes. B118g reran the whole design on the fixed seed.
- **B118d readout.** The constant-twin readout was defined after seeing 2 cells. It was fixed in advance for
  B118f/g, and B118d is not counted.

## 5. Compute / leases
- **Window 11 (from 2026-10-17 00:30Z):** ~46.5/48.
- All leases released with tokens.
- No host memory events (free memory 9.5-17 GB at every launch).

## 6. Active experiments
None. Two are queued for window 12 (~2026-10-18 00:30Z), both with predictions committed and controls met.

## 7. Next branches
1. **B119 -- second world family** (P-boom lineage) for the semantics result. Controls 12/12, 12/12, 7/8.
   Prediction: TOXIC >= 3/8, PLAIN <= 1/8.
2. **B120 -- distance isolation.** Seeded forager, type words at the END. Prediction: TOXIC <= 1/4. If it is
   >= 2/4, B118b failed because of gen 0, not distance.
3. **The world-1 vs world-2 group-reward rate gap** for communication (parked).
