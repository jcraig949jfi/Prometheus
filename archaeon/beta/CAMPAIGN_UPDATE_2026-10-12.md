# Archaeon Phase 2-B SFE Beta -- campaign update 9 (2026-10-12 ~05:10Z)

Since update 8 (2026-10-10 ~04:45Z). This update is for compression, not permission. Numbers are in
archaeon/beta/results/; reasoning is in JOURNAL.md; summary in BETA_FINDINGS.md. Review packets:
REVIEW_PACKET_FINAL_BETA_F3_DISTANCE_WALL.txt (new) and REVIEW_PACKET_FINAL_BETA_F4_NICHES.txt.

## 1. Strongest new evidence -- the memory law is REVISED: the update wall is a DISTANCE wall
**World.** Relocating pulse world: 48 ticks; refill every 4; every 16 ticks each pool jumps to a random node. There the
update-on-condition RESET latch (unlatch after 4 empties, re-search) is the best hand strategy, 1.66x the write-once
LATCH.

**RESET-like populations by gen-0 start** (B75 / B76 / B76b / B77 parity readout):

| start | RESET-like populations | RESET-like genomes per population |
|---|---|---|
| random | 0/12 (8/12 still reach write-once state) | 0 |
| stateless forager | 4/6 | median 3.5 |
| hand write-once latch | 6/6 | median ~102 |

- The best evolved RESETs (.075-.082) beat the hand RESET (.065).
- They are verified: register state; re-find .58-.69; they leave the dead node within 0-3 ticks.

**Natural curriculum (B78) mostly fails to cross.** Random gen 0, then plain pulse (where latches are reached), then
relocation. State is reached in 10/12 populations, but RESET (>= 5 genomes) in only 1/12.

**What makes a latch a stepping stone (B79).** Seeded with EVOLVED latches:

| latch | length | plain-pulse reward | populations converting to RESET |
|---|---|---|---|
| compact | 16 | .120 | 4/6 |
| long | 32 | .098 | 6/6 |
| long | 46 | .053 | 0/6 |

- The compactness hypothesis is KILLED.
- The latch's quality as a forager tracks conversion (n = 3 latches; tentative).
- B78's own latches ended at .021-.055, i.e. low quality.

## 2. Most interesting weak signal
- **Patrols vs latches (B73).** Patrols are excluded under competition by an invasion asymmetry, not by self-collision.
  A latch among patrols keeps ~94% of its solo reward; a patrol among latches keeps 60%.
- **Cross-lane pattern.** Here coupling needed SIMULTANEITY to bite; Nestor (NPE) reported coupling needing
  DIRECTIONALITY. This is a pattern note, not a claim.

## 3. Clean nulls / killed hypotheses
| hypothesis | result |
|---|---|
| B74 v1/v2 ladder predictions | FAILED; v1 by a design flaw (half-ring shifts return pools home) |
| B76: RESET <= 1/6 from a latch start | FAILED (6/6) -- the decisive surprise |
| B78: natural curriculum crosses | FAILED (1/12) |
| B79: compactness | KILLED |

## 4. Instrument repairs (mine)
- **Census undercount.** The top-10-by-count census misses rare best genomes. The B77 parity readout (every genome
  above the hand LATCH) is now standard.
- **B75 smoke-test line.** It was journaled 'passed' before the test ran (it had failed). Corrected; smoke-test output
  is now shown before it is journaled.
- **Compute estimates** keep running low. Tallies are now re-derived from wall-clock at completion.

## 5. Process
- **Window 5 delay.** It opened with the lease held by Pan; B75 waited 2.5 h for it (no compute without the lease).
- **Leases.** All released explicitly with captured tokens; renewed when cells ran long.
- **Compute.** Window 6 (from 2026-10-12 00:29Z): ~37 of 48 core-h.
- **Heartbeat cron.** Renewal reminder fires 2026-10-12 local, before the 7-day expiry.

## 6. Next branches
1. **Latch quality, properly:** several evolved latches per quality band, to separate quality from genome identity.
2. **Curriculum with quality pressure:** run the plain-pulse stage longer, or select for latch quality, before
   relocation.
3. **Keyed memory, same distance test:** a precursor start for the B53-B57 keyed-recall setting.
4. **Budget from random:** B75 at G = 600-900 (does RESET ever appear from scratch?).
