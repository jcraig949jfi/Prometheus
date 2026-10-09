# Archaeon Phase 2-B SFE Beta -- campaign update 7 (2026-10-09 ~08:10Z) -- MAJOR FINDING

Since update 6 (2026-10-09 ~02:45Z). This update is for compression, not permission. Numbers are in
archaeon/beta/results/ (B64 in results/B64_bscatter/); reasoning is in JOURNAL.md; summary in BETA_FINDINGS.md Finding 4.

## 1. Strongest new evidence -- the first ecological interaction in SFE
**Concurrent competition evolves negative-frequency-dependent niche partitioning, on 2/2 worlds.**
- **Setup.** Four organisms forage in the SAME episode on the SAME depleting pools. Fitness is each organism's own
  reward.
- **What evolves.** Pool-identity specialists (fidelity .95-1.0) that coexist at balanced frequencies.
- **Rare-type advantage.** A lone specialist among three of the other type out-earns them in both directions.

| test | P-boom (B62/B63) | B-scatter (B64) |
|---|---|---|
| diversity, CONC > noise-matched SHAM by >= .2 bits | 4/6 | 5/6 |
| mixed-niche groups out-earn same-niche groups (CONC) | 6/6 | 5/5 testable |
| rare-type advantage both ways, CONC / SOLO / SHAM | 4 / 1 / 0 | 4 / 1 / 1 |

Controls behind it:
- **Noise null.** SHAM keeps CONC's exact fitness signal/noise but detaches the competition component from the
  organism (residual shuffle). It does not reproduce the diversity; it is even less diverse than SOLO.
- **Determinism.** Re-runs reproduce B60 cell-for-cell.
- **Contrast shape.** Solo and noise-matched populations are monomorphic or dominated (e.g. 166-191/200 on one
  pool). Their rare/common pattern is plain DOMINANCE.

## 2. Instrument repair that made it possible
- **B59 null was an instrument null (mine).** Sequential "coupling" had no teeth: pools return to the in-episode
  equilibrium between organisms (.2948, then .2895 x19).
- **B60 replaced it** with a concurrent evaluator. It is exactly equal to evaluate_world at k=1, and on B-scatter it
  handles the regime feature centrally (equal on 15 organisms).

## 3. Clean nulls / drops
- B59, as above.
- B61 (regenerating food + lethal hazards for P-boom transfer) was dropped before running: 74% of family worlds
  already regenerate, so it would replicate B41.

## 4. Process
- **Lease token lost (mine).** I truncated the acquire output with tail, so lease lse-78a64fc8d5b2 lapses by TTL at
  10:00Z. A memory note was added.
- **Same lease reused.** It also covered B62/B64, all on <= 12 procs.
- **Compute.** Window 3 used ~42 of 48 core-h.

## 5. Active long-running experiments
None. Next heavy run after the window rolls (~2026-10-10 00:11Z).

## 6. Next branches
1. **Group size:** k=2 and k=8 (does partitioning scale with crowding?).
2. **A third world**, ideally one outside the C6 named set (ensemble invariance).
3. **Mechanism:** read out how a specialist encodes its pool (disassembly + per-word ablation).
4. **Bridge to the memory law:** does competition make STATE pay (e.g. remembering which pools others depleted)?
   The one place the memory wall might be crossed by ecology rather than by representation.
