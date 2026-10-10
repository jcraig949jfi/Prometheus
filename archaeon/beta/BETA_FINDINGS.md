# Archaeon Phase 2-B SFE Beta -- findings (2026-10-06 .. 2026-10-09)

**Scope.** Proteus v0 player VM organisms (plus variant VMs built from its source with asserted single-branch patches),
evolved by the CMP3 search (archaeon.wse.evolve) in WSE event worlds and C6 composed worlds. All probes, results and
reasoning are on branch archaeon/p2b-sfe-2026-10-06:
- archaeon/beta/ (b01..b64, results/)
- JOURNAL.md
- CAMPAIGN_UPDATE_*.md
- METHODS_NOTE.md
- controls.py

Every claim below survived the controls named with it. Retractions are listed at the end.

## Finding 1 -- the 2026-09-18..22 Deep Frontier showed no perception of world content

The re-audit covered 130 frontier experiments, read-only on the off-repo runs (B23/B23b/B23c/B24).

| scope | what it found |
|---|---|
| WSE W0 worlds | 41/76 competent final organisms are TIMING EXPLOITS (delay lines; 0-7 jitter) |
| C6 composed worlds | 62/102 elites do not beat the best constant program |
| W-artifacts | the 1.000 elites equal an echo of input word 0 |
| best P-boom survivor | a lap counter comparing the tick word with its own position |

Consequence: the frontier's detector firings were computed over populations whose "competence" was timing, echo or
clock.

## Finding 2 -- content sensing evolves when the clock word is removed, and transfers under a world distribution

1. **Removing tick/position from the observation (NoClock) produces content sensors.** There are 6 sensors in two worlds
   (P-boom 3/6, B-scatter 3/3).
   - Controls: blind twin collapse, re-scored at 64 episodes x 4 world seeds (B25/B26/B27, B46).
   - Mechanisms: dwell-by-reversal with a one-register direction memory (B31), and stop-when-food.
2. **Fixed-world foragers do not transfer.**
   - B28: home lift +.23 vs off-home -.02.
   - B29: training on two worlds yields blind held-out behaviour.
3. **Training on a fresh procedural world each generation (echo-free) transfers within the family.** On 29 unfiltered,
   echo-free held-out worlds the paired lift vs specific foragers is +.050 (23/5 worlds, p = .0009); specific foragers
   score .002 (B35/B36).
   - 6/8 such foragers implement the INVARIANT rule "harvest the non-empty pool by position; move when empty"
     (harvest index = position on .77-.92 of single-food ticks; B39).
4. **Boundaries:**
   - no transfer to named worlds outside the family (B33/B38);
   - adding delayed-action worlds destroys transfer (B37);
   - the P-boom obstacle is mapped (B42): rare departures from regenerating food, then a wander, then hazard deaths.

## Finding 3 -- the memory law and its mechanism

1. **Law.** Write-once state is reliably reachable: a one-value store, a write-once guard, a latch (B08J, B16,
   B44/B45). Update-on-condition and keyed state are not reached at a usable rate. This holds across:
   - VM (SEL B10/B49, queue B13, KV organ B53);
   - world (K-distribution B40, evidence B45, switching latent B47);
   - incentive (write credit B22, B22b);
   - selection (lexicase B50);
   - mutation (coupled-pair B51);
   - founding configuration (B19, B52).
2. **The latch is evolution's preferred memory.** 28/50 genuine one-value organisms stop reading input (B16). The best
   "evidence integrators" latch onto the first hint (B45).
3. **Mechanism -- a graded wiring wall.** On a VM that writes keyed memory automatically, keyed recall depends on the
   number of coupled instructions in the read (B55/B56, gen-0 scrubbed):

   | read chain | keyed | first solve |
   |---|---|---|
   | 1 link | 8/8 | gen ~1 |
   | 2 links | 8/8 | gen ~8 |
   | 3 links | 2-3/8 | gen 44-203 |

   - Waiting time grows ~10x per link.
   - Freeing one REGISTER coupling lifts the 3-link read to 6/8, median gen ~72 (B57). The remaining cost is
     instruction ORDER.
   - Every unreached memory solution in this campaign needs a longer coupled chain.
4. **One rare exception.** A self-modifying-code state machine that rewrites its own genome per tick solved
   two-value memory at .971, and .062 when locked (B51). It was not reproduced in 8 writable runs (B52).

5. **A behaviour-gating latch IS reached where it pays (B68/B69/B69c).**
   - World: a pulse world, where a harvest empties the pool and pools refill every 4 ticks. There the hand latch
     ('found my pool -> wait when empty') earns 3.6x the stateless forager.
   - Result: latch-like organisms (stay-when-own-pool-empty >= .9 AND state dependence >= .02) evolve in SOLO 3/6 and
     CONC 5/6 populations (preregistered, B69c). Pooled with the exploratory B69b: 6/12 and 9/12.
   - Two CONC populations beat the hand latch (.121, .139 vs .119).
   - The memory law's reachable class therefore includes a latch that gates control, not only a stored value -- when
     the world makes it decisive.
   - Competition raising the rate: NOT SUPPORTED (B69d: count CONC 6/12 vs SOLO 3/12, but reward p = .22).
   - Some elites beat the hand latch with no latch-like genomes (another strategy class, uncharacterised).

## Finding 4 -- concurrent competition evolves negative-frequency-dependent niche partitioning (2/2 worlds)

1. **Sequential coupling has no teeth (B59).** Organisms evaluated one after another on a shared pool see the
   in-episode regeneration equilibrium. Rewards: .2948, then .2895 x19. Its null says nothing about niches.
2. **Concurrent coupling (B60).**
   - Setup: 4 organisms act in the same episode on the same pools. The evaluator equals the standard one at k=1;
     4 identical foragers earn about 1/4 each.
   - Result: the population diversifies its dominant pool (+.24 bits mean, 4/6 seeds >= .2).
3. **Attacks survived (B62, B63 on P-boom; B64 on B-scatter):**

   | test | P-boom | B-scatter |
   |---|---|---|
   | entropy CONC > noise-matched SHAM by >= .2 | 4/6 | 5/6 |
   | mixed-niche groups out-earn same-niche groups (CONC) | 6/6 | 5/5 testable |
   | rare-type advantage both ways, CONC / SOLO / SHAM | 4 / 1 / 0 | 4 / 1 / 1 |
   | hardened (B70: niches >= 10, 48 groups, bootstrap lo > 0), CONC / SOLO / SHAM | 4/6 / 0/5 / 0/5 | 4/6 / 0/4 / 0/1 |

   - SHAM = residual-shuffle null: same fitness signal/noise as CONC, but the competition component is detached
     from the organism.
   - Re-runs reproduce B60 cell-for-cell (determinism).
4. **Shape.**
   - CONC organisms are pool-identity specialists (fidelity .95-1.0) in two balanced niches.
   - Solo and noise-matched populations are monomorphic or dominated by one niche.
   - Their rare-vs-common pattern is DOMINANCE: one type wins both as rare and as common.
5. **Mechanism (B65).** 33/36 specialist genomes depend on exactly one observation word, their own pool's (every
   other word's ablation drop is 0.0). A niche is a perceptual restriction: sense only pool i, harvest it, else move.
6. **Crowding threshold (B66).** Under pair competition (k=2), entropy is as high as at k=4 (1.19 vs 1.23) but
   the hardened rare-type test finds 0/6 wins: every population shows dominance. Negative frequency dependence needs
   crowding; entropy alone does not detect it. At pair level (B72) the same holds: mixed pairs beat same-niche pairs
   in 2/6 k=2 populations (solo-like) vs 6/6 k=4 populations.
   At k=8 (B66) the hardened rare-type test gives 4/6, as at k=4: NFD switches on between k=2 and k=4 (a crowding
   threshold), while entropy rises gently (.99 / 1.19 / 1.23 / 1.32 for k = 1/2/4/8).
7. **Limits.** Two worlds; a third (procedural) world pending (B71).

## Retractions (mine; the calibration ledger has rows for the process errors)

| claim | what happened |
|---|---|
| B08 "second slot reachable" | the solvers were delay lines (B08b) |
| B44 "7/8 evolved evidence integrators" | a shared 8-episode held-out sample with lucky first hints; 0/8 at 64 x 4 (B45) |
| B25-B31 composed-world magnitudes | scored on TRAINING episodes; ~halved on new ones (B46); C6-unable sensing and the open-loop "beats constant" claim withdrawn |
| B32 "strong transfer" | inflated by a filtered held-out set (B33); the supported claim is B34/B36 |
| "composition wall" name (update 1) | withdrawn after the 11-instruction indexed solver (B20) |
| update 1 claim that GENERAL memory needs a loop (B05) | withdrawn after the same solver |
| process: compute | the first 4 h ran unleased over the R2 envelope (ledger 2026-10-07) |

## Open questions
1. Does a representation that removes ORDER coupling as well (e.g. reads addressed by input position) make the 3-link
   read L2-like?
2. Is self-modifying code a systematic chain-shortener, or a rare accident?
3. Can the invariant foraging rule be pushed beyond the generator family by randomising reward semantics (which pool
   pays) rather than dynamics?
