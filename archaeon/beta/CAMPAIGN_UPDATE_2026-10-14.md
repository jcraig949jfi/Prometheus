# Archaeon Phase 2-B SFE Beta -- campaign update 10 (2026-10-14 ~07:05Z)

Since update 9 (2026-10-12 ~05:10Z). This update is for compression, not permission. Numbers are in
archaeon/beta/results/; reasoning is in JOURNAL.md; summary in BETA_FINDINGS.md (Finding 3). The review packet
REVIEW_PACKET_FINAL_BETA_F3_DISTANCE_WALL.txt now has section 7b and a retraction.

## 1. Strongest new evidence -- the distance wall holds for the KEYED class too (B86)
Keyed two-slot recall had never been reached on the stock VM (B49-B53: 0/8). Two hand precursors on the same fitness
plateau (no gradient):

| precursor | distance from the hand SOLVER | held-out | keyed recall |
|---|---|---|---|
| SLOT_A (SOLVER with slot B's two fill instructions NOPed) | 2 edits | .531 | 4/8 runs, held-out 1.000, first solve at gens 3-14 |
| SHELF (one-value store) | far | .535 | 0/8 |

Distance, not fitness, decides it. Caveat: the precursor is the hand solution minus two instructions, so this is a
statement about distance, not about open-ended discovery.

## 2. The stepping-stone question -- five probes, no simple predictor, PARKED
Question: why does one latch convert to update-on-condition (RESET) and another not? Pooled conversion rates
differ sharply between latches (H_6913 5/6 vs H_6923 1/6 at near-equal quality).

| probe | candidate | result |
|---|---|---|
| B80 | latch quality | NOT supported (HIGH 4/12, LOW 1/11) |
| B81 | persist mode (swap) | NOT the variable (unchanged 3/6 and 0/7) |
| B82 | one-step neighbourhood | H_6913 has 15/1000 improving one-step mutants, all RESET-like |
| B83 | one-step density over 10 latches | does NOT predict conversion (rho .43) -- see retraction below |
| B84 | short neutral reach | also fails (rho .43); probably underpowered vs evolution's ~60k selected offspring |
| B85 | recombination between the two hand variants | NOT required: a single hand latch converts 6/6 |

## 3. Retraction (mine)
- **What I claimed.** B82's reading 'a latch is a stepping stone iff RESET is one coupled edit away'. It was drawn from
  n = 3 and posted as comms #2243.
- **What killed it.** B83 (n = 10, prediction committed first). The two most reliable convertors have zero improving
  one-step mutants.
- **Where it is recorded.** JOURNAL, BETA_FINDINGS, the review packet, comms #2245, and a calibration-ledger row. New
  rule: a mechanism read from one positive case is reported as a CASE until tested across the population it would
  explain.

## 4. Clean nulls
| probe | prediction | result |
|---|---|---|
| B80 | HIGH >= 8/12 | FAILED |
| B81 | both parts | FAILED |
| B83 | rho >= .6 | FAILED |
| B84 | rho >= .6 | FAILED |
| B85 | SINGLE <= 2/6 | FAILED |

Each was preregistered and is reported in full.

## 5. Process
- **Tail-cell policy adopted.** A cell running more than 2x the median that cannot change a verdict is stopped and its
  lease released. Applied to B80 (7.5 h tail) and B81. It was not applied while a tail cell could still change the
  verdict (B81 L_6931 until it became impossible).
- **Heartbeat cron renewed** (7b2796f5); next renewal reminder 2026-10-18.
- **Compute.** Window 7 ~34/48; window 8 ~43/48. All leases released with captured tokens.

## 6. Active long-running experiments
None. B87 (graded keyed distance d = 2/4/6/8, 32 cells, prediction committed) launches in window 9
(~2026-10-15 00:30Z).

## 7. Next branches
1. **B87 graded keyed distance.** Does the keyed rate fall with edit distance, mirroring the B55-B57 per-link slope?
2. **Population-scale route.** What population process carries a latch with no improving neighbours to RESET? Needs
   lineage logging in a converting run (an instrument build).
3. **Budget from random.** B75 at G = 600-900: does RESET ever appear from scratch?
