# Archaeon Phase 2-B SFE Beta -- campaign update 12 (2026-10-16 ~05:00Z)

Since update 11 (2026-10-15 ~09:40Z). This update is for compression, not permission. Numbers are in
archaeon/beta/results/; reasoning is in JOURNAL.md; summary in BETA_FINDINGS.md Finding 5. The review packet
REVIEW_PACKET_FINAL_BETA_F5_COMMUNICATION.txt now has sections 7b-7d.

## 1. Strongest new evidence -- FIRST EVOLVED COMMUNICATION, and it needs GROUP selection (B103/B103b/B103c)
- **World.** Non-rival information world: only a scout sees which pool is richest; the others see a shared signal word.
  Concurrent 4-groups.
- **Start.** Gen 0 = 200 genomes one opcode word from full communication.
- **Search.** CMP3 with 85% of offspring cloned, which puts the mutation load below the error threshold.

| reward | B103 | B103b (replication) | pooled |
|---|---|---|---|
| SHARED (group mean) | 4/6 | 3/6 | **7/12** |
| INDIVIDUAL | 0/6 | 0/6 | **0/12** |

- **Significance.** Fisher one-sided p ~ .002.
- **Constant-twin control (B103c).** The evolved signals beat the best constant redirect by +.05 to +.29, so they are
  informative.
- **Content metric.** Writes equal to richest+1: one signaller .84, two low. That prediction part FAILED.

## 2. The mechanism that blocked communication -- an ERROR THRESHOLD (B96-B99)
- **B96.** Fixing the scout, immigrating listeners, or both: 0/6 x 3.
- **B96b.** The selection coefficient of a restored signaller is s ~ .019 under both scout schemes, so 'dilution' was
  WRONG (mine).
- **B97.** A higher-headroom world doubles s (.046): still 0/6.
- **B97b / B98b.** A clean one-word restore arises in ~1e-4 of offspring. A full communicator's children break the signal
  31% of the time and listening 40%.
- **B98.** Signallers seeded at 1-20% go EXTINCT in 12/12 runs.
- **B99 (causal).** Cloning 80-95% of offspring turns extinction into a SWEEP (0/4 -> 4/4, 10/10 of the top 10
  signalling).

## 3. Bounds
| probe | test | result |
|---|---|---|
| B100-B102 | the same low-load lever on the MEMORY walls | does NOT move them: keyed d6 1/28 vs 0/32; RESET from random 0/8 vs 0/12. Memory is distance-limited, communication threshold-limited. Cross-lane hypothesis withdrawn (comms #2260). |
| B104 | communication from RANDOM gen 0 below the threshold | 0/12 |
| B105 | from 1/2/3 opcode words away | 3/6, 1/6, 2/6 -- roughly flat in word distance; monotone prediction FAILED |

## 4. Instrument / process (mine)
- **'Dilution' was a conceptual error** (B96b).
- **B103 did not dump genomes**; repaired in B103b.
- **The SIGNALS readout lacked a constant-twin control** until B103c.
- **B97's s-prediction was not receipted** (written before the measurement, committed after).
- **B100's single d6 success was a fluke** (B101 0/16).

## 5. Compute / leases
- **Window 9:** ~46/48.
- **Window 10 (from 2026-10-16 00:30Z):** ~17.5/48.
- All leases released with tokens.

## 6. Active experiments
None.

## 7. Next branches
1. **Second world** for the evolved-communication result (ensemble invariance).
2. **Kin structure** (clonal groups) at normal mutation load -- an alternative to group reward.
3. **What the evolved codes are:** decode the partial codes of 10311/10312.
