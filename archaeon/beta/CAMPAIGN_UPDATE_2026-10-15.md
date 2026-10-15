# Archaeon Phase 2-B SFE Beta -- campaign update 11 (2026-10-15 ~09:40Z)

Since update 10 (2026-10-14 ~07:05Z). This update is for compression, not permission. Numbers are in
archaeon/beta/results/; reasoning is in JOURNAL.md; summary in BETA_FINDINGS.md (Finding 3 items 6-7; new Finding 5).
The review packet REVIEW_PACKET_FINAL_BETA_F3_DISTANCE_WALL.txt has section 7c for the keyed class.

## 1. Strongest new evidence -- the keyed distance wall, fully mapped (B86-B90)
Precursors are the hand keyed solver with d instructions missing. All sit on the same fitness plateau as a one-value
shelf, so there is no gradient.

| d | keyed reach | notes |
|---|---|---|
| 2 | 9/16 | first solves gens 1-37 |
| 4 | 4/16 | no late success even at 3x budget (B88) |
| 4 + immigration | 6/8 | 10% fresh precursor copies per generation; one solve at gen 132 (B89, p ~ .02) |
| 6 | 0/32 | across every condition, incl. immigration at 3x budget (B90) |
| 8 | 0/8 | |
| shelf start | 0/8 | |

Reading:
- **d4** is limited by BASIN CAPTURE (drift onto the shelf plateau); keeping the basin occupied removes the limit.
- **d6+** is beyond this search.
- **Caveat.** Precursors are hand solutions minus instructions; this measures reachability by distance, not discovery.

## 2. Second result -- communication does not evolve in this search (new Finding 5, B92-B95b)
- **B92/B93.** In a regeneration-limited world a scout's signal is zero-sum: it redistributes, group +.008.
- **B93b.** A NON-RIVAL world (static pools) makes honest signalling free and valuable (+.13 for listeners).
- **B94.** From random gen 0: no signalling, no listening, not even scouting; 0/6 under both individual and SHARED
  reward.
- **B95/B95b.** One edit -- and then, after a design repair, one WORD -- from full communication: the signal is never
  restored (0/6, 0/6), and the listener half DECAYS.
- **Reading.** Two-sided coupling, plus weak, diluted selection on a signal mutant (it signals in 2/8 episodes), plus
  neutral decay of the unused half. Contrast the keyed precursor, where every part is selected in one individual.

## 3. Clean nulls / killed hypotheses
| probe | hypothesis | result |
|---|---|---|
| B88 | basin capture (count) | FAILED by the letter on the d4 count; timing parts held |
| B90 | d6 reachable with immigration + time | FAILED |
| B91 | RESET genome-specificity (H_6923 1/6) is basin capture | KILLED: immigration leaves it at 1/6 |
| B94 / B95 / B95b | communication evolves | all FAILED |

## 4. Instrument / design repairs (mine)
- **B95 MUTE** zeroed all four words of the signal OUT, so a 'one edit' restore needed several coordinated mutations.
  Repaired as B95b (opcode-only NOP). The negative held.

## 5. Process
- **Compute.** Window 9 (from 2026-10-15 00:30Z): ~39 of 48 core-h. All leases released with tokens.
- **Heartbeat.** The heartbeat cron and its 2026-10-18 renewal reminder are in place.

## 6. Active long-running experiments
None.

## 7. Next branches
1. **Communication with fixed roles.** A dedicated scout lineage removes the 2/8 dilution: does signalling then evolve
   under SHARED reward?
2. **Protecting the unused half.** Does immigration of listeners keep listening alive long enough for a signal mutation
   to be selected?
3. **Consolidation.** A Beta synthesis document across Findings 1-5 for Harmonia/Aporia review.
