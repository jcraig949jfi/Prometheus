# Archaeon Phase 2-B SFE Beta -- campaign update 5 (2026-10-08 ~12:30Z)

Since update 4 (~05:00Z). This update is for compression, not permission. Numbers are in archaeon/beta/results/;
reasoning is in JOURNAL.md.

## 1. Strongest new evidence
**Evolution reaches the GENERAL foraging rule once a world distribution removes the payoff of specific mappings.**

- Of the 8 transferable foragers from echo-free world-distribution training, 6 implement the invariant rule "harvest
  the non-empty pool by its position; move when empty" on unseen worlds (B39). That is the hand-generalist's rule.
  - Harvest index = position of the single non-empty pool on 77-92% of 311-503 ticks; chance is about .2-.5.
- Fixed-world training (B28) and paired-world training (B29) never produced it.

**The campaign's MEMORY LAW, now tested five ways.**

| | write-once state (latch, guard) | update-on-condition state |
|---|---|---|
| reached? | yes, reliably | never a reliable advantage; a weak profile in about 1/12 runs |

- The update-on-condition tests were a second slot (B08J), the keyed read (B22b, B40), an evidence filter (B45), and
  an update after a latent switch (B47).
- The reach rate is the same with a straight-line select primitive: SEL VM 1/12 vs stock VM 1/12 (B49).

## 2. Most interesting weak signal
**A genuine filter-and-re-track memory in ~1/12 runs (B48 seed 4807; B49 one per VM).**
- It is more accurate than a reactive policy before the latent switch (.61 vs .56).
- It recovers after the switch (.55 vs the latch's .20).
- It never converts into a reliable reward advantage.

## 3. Important clean nulls
| probe | question | result |
|---|---|---|
| B40 | general keyed memory under a K-distribution | 0/8 |
| B41 | lethal hazards in the training distribution, then transfer to P-boom | P-boom transfer 0/8 |
| B47 | conditional update when the latch is punished | 0/8 above reactive |
| B49 | the SEL instruction-set lever | no effect |

## 4. Mechanisms killed, and RETRACTIONS (mine)
**Retracted:**
- **B44, "7/8 evolved evidence integrators".** The elites were scored on one shared 8-episode held-out sample with lucky
  first hints. At E=64 x 4 the count is 0/8. The best elites latch onto the first hint.
- **B25-B31 composed-world numbers.** They were scored on the elites' TRAINING episodes (B46). Six content sensors
  survive re-scoring (P-boom 3, B-scatter 3).
  - The C6-unable sensor and the "open-loop beats constant" claim are retracted.
  - Magnitudes are about halved on new episodes.

**Killed:**
- The distribution lever crosses an isolated peak (B40).
- Lethal-hazard training removes P-boom's food departures (B41). The obstacle is mapped instead: about 8% departures
  lead to a wander and 7/16 deaths (B42).
- The update wall is about branch structure (B49).

## 5. Instrument / engine repairs
- **New standard (ledger row 2026-10-08).** Held-out = new episodes, at least 64 episodes across at least 4 world seeds.
  The B46 re-score applied it backwards.
- **New probes:**
  - B42: a per-tick behaviour trace of where an organism is and what it does.
  - B48 / B49: switch-recovery profiles (pre, early and late accuracy).
- **Evidence world v1 had a design flaw:** depletion rewarded rotation, so knowing the latent did not pay. The oracle
  control caught it, and v2 uses static pools.

## 6. New players / worlds
- **Worlds:**
  - the evidence-integration world (hint-only observation, static pools);
  - its switching-latent variant;
  - the lethal-hazard family distribution.
- **Players:** hand-written LATCH, STICKY and SEL_STICKY controls.

## 7. Active long-running experiments
None. About 35 of 48 core-h are used in this 24 h window (since 2026-10-08 00:07Z); every lease is released.
Remaining heavy budget ~13 core-h until ~2026-10-09 00:07Z.

## 8. Next branches
1. **Memory beyond write-once needs a different search, not a different VM or world.**
   - Candidates: an incremental-credit world that pays the read half alone (the keyed-memory reopen condition), or
     lexicase-style selection across episode types.
   - This is design work for the next window.
2. **P-boom transfer.** A forager must never leave a regenerating food node.
   - Test: a family where food regenerates and hazards are dense, so parking pays.
3. **Consolidation.**
   - Package the jitter, twin, recovery and held-out standards into controls.py (done for most of them).
   - Write the methods note for other seats: clock words, echo worlds, training-set scoring.
