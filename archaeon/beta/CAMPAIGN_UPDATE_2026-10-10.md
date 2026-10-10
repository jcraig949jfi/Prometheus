# Archaeon Phase 2-B SFE Beta -- campaign update 8 (2026-10-10 ~04:45Z)

Since update 7 (2026-10-09 ~08:10Z). This update is for compression, not permission. Numbers are in
archaeon/beta/results/; reasoning is in JOURNAL.md; summary in BETA_FINDINGS.md (Findings 3 and 4). The review packet for
Finding 4 is REVIEW_PACKET_FINAL_BETA_F4_NICHES.txt, with addenda.

## 1. Strongest new evidence
**Finding 4 (niche partitioning under competition) replicates on 3/3 worlds and has a crowding threshold.**
- **Third world (B71).** A minimal procedural ecology from outside the C6 named set, chosen by a rule fixed before any
  run. Hardened rare-type test: CONC 6/6 wins, bootstrap lower bounds .10-.16 (the strongest of the three worlds);
  SOLO 0/4 and SHAM 0/2 testable.
- **Hardened test on the first two worlds (B70).** Niches >= 10 members, 48 groups, bootstrap lower bound > 0 in both
  compositions: CONC 4/6 on each world; controls 0/15 testable. The earlier control 'wins' were small-niche sampling luck.
- **Crowding threshold (B66, B72).**

  | group size k | entropy | hardened rare-type wins | mixed-pair advantage |
  |---|---|---|---|
  | 1 | .99 | 0/5 | 2/5 |
  | 2 | 1.19 | 0/6 | 2/6 |
  | 4 | 1.23 | 4/6 | 6/6 |
  | 8 | 1.32 | 4/6 | -- |

  Negative frequency dependence switches on between k=2 and k=4. Entropy rises gently throughout and does not mark the
  threshold.
- **Mechanism (B65).** 33/36 specialists depend on exactly one observation word, their own pool's: niches are
  perceptual restrictions.

## 2. Most interesting weak signal
**Where state pays decisively, the search reaches it, in three forms, and sometimes beats the hand design.**
- **The world (B68).** Pulse world: a harvest empties a pool and pools refill every 4 ticks. The hand 'found-my-pool'
  latch earns 3.6x a stateless forager. In the standard world it earns 0.000 more.
- **Preregistered test (B69c, new seeds).** Latch-like populations SOLO 3/6, CONC 5/6. Two CONC populations beat the hand
  latch (.121, .139 vs .119).
- **Full census (B69e, 48 populations, exploratory).** State is used in SOLO 13/24 and CONC 17/24 populations, as:
  - register latches;
  - register PATROLS that visit all pools on the refill cycle (SOLO only);
  - SELF-MODIFYING-CODE latches (the best genome in 5/48 populations, vs ~1/28 in the earlier memory worlds).
- **Competition raising the latch rate: NOT SUPPORTED (B69d).** The count criterion was met (6 vs 3 of 12) but the
  reward criterion failed (p = .22).

## 3. Clean nulls
| probe | question | result |
|---|---|---|
| B67 | do competition-trained organisms use state more? | no (opposite signs on two worlds) |
| B68 | does competition amplify state's absolute value? | 0/3: it halves every reward, so the absolute advantage shrinks |
| B69 | preregistered mean-dependence readout | FAILED; the latch shows up only in the census (B69b/c) |
| B69d | competition -> latch rate | NOT SUPPORTED |
| B61 | | dropped before running (redundant with B41) |

## 4. Instrument / engine repairs (mine)
- **Persist ablation misses code-stored state.** 'persist = none' does not remove state that an organism stores in its own
  genome. A CONC elite keeps its latch in self-modified code: locked .028, persist-none .135. The full readout is
  code-lock + persist-none (B69e). B67's readout has the same gap; low priority because B68 shows state is worthless in
  that world.
- **Latch-shape census misses patrols.** The census undercounts state use; it is a lower bound.
- **B68 prediction not receipted.** The prediction was committed with its result, so B68 is treated as exploratory.
  Every probe since (B70, B72, B69c, B69d) committed its prediction before running.
- **Lease process fixed.** The token is captured to a file, and leases were released or renewed explicitly
  (lse-c2ed7edd7dc3 released; lse-66beba5c83b5 renewed twice).

## 5. Active long-running experiments
- B71's last cell (SHAM 7103) is still running. It cannot change any B71 criterion.
- Window 4 (from 2026-10-10 00:29Z): ~39 of 48 core-h, re-derived from wall-clock receipts. My earlier running
  estimate of ~23 undercounted B71 and B69d. No more heavy runs this window.

## 6. Next branches
1. **Rank vs proportional selection.** Does the competition -> latch hint (pooled preregistered SOLO 6/18 vs CONC 11/18)
   come from rank-based selection seeing the larger RATIO advantage?
2. **Patrols vs competition.** Are patrols absent under competition because patrols collide? Hand-control ladder:
   patrol vs latch, solo vs group.
3. **Self-modifying code as a state carrier.** Why does it appear 5/48 here vs ~1/28 before? Is it reached where the
   latch must GATE behaviour?
4. **Cross-lane note.** Nestor (NPE) reports that function persistence needs DIRECTIONAL coupling; here coupling needed
   SIMULTANEITY. Both say that coupling must be configured before it bites. A pattern note only, not a claim.
