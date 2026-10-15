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
   - Full state census (B69e; dependence with code locked AND persist none; 48 populations, exploratory): state is
     used in SOLO 13/24, CONC 17/24 populations, in three forms -- register latch, register patrol (SOLO only), and
     self-modifying-code latch (best genome in 5/48). B67/B69's persist-only readout missed code-stored state
     (instrument gap, mine).

6. **The memory law survives its most direct test (B74/B75).**
   - World: a relocating pulse world (48 ticks; refill every 4; every 16 ticks each pool jumps to a random node).
     There the update-on-condition RESET latch (unlatch after 4 empties, re-search) is the best hand strategy: 1.66x
     the write-once LATCH.
   - Result (12 populations, preregistered): 8/12 best genomes use write-once state (LATCH-like re-finding); 0/12
     reach the update-on-condition RESET.
   - The wall is specific to the update class, not to the world -- from a RANDOM start.
   - **Revision (B76/B76b): it is a graded DISTANCE wall.** RESET-like populations:
     - from random gen 0: 0/12;
     - from the stateless forager: 2/6 (preregistered census), 3/6 (best genome), 4/6 with every above-LATCH genome
       classified (B77) -- but with median 3.5 RESET-like genomes per population vs ~102 from the latch;
     - from the write-once latch: 6/6, with best .075-.082 beating the hand RESET .065.
   - Update-on-condition memory is reachable when its write-once precursor is present. The law's 'not reached'
     holds from scratch, not in principle.
   - **A natural curriculum mostly does NOT cross (B78).** Plain pulse first, then relocation: write-once state is
     reached in 10/12 populations and survives the switch, but only 1/12 reach >= 5 RESET-like genomes. Evolved
     latches (16-95 instructions, diverse) are a weaker stepping stone than 200 copies of the compact hand latch.
   - **What makes a latch a stepping stone (B79):** NOT compactness. Seeded with evolved latches, a 16-instruction
     (.120) latch converts 4/6, a 32-instruction (.098) latch 6/6, and a 46-instruction (.053) latch 0/6. The latch's
     QUALITY as a forager tracks conversion (n = 3 latches; tentative).
   - **B80 (4 latches per band x 3 seeds): quality NOT supported as stated.** HIGH-quality latches convert 4/12, LOW
     1/11. Conversion from a good latch is stochastic (~1/3 per run). The persist mode lines up better (persist 'regs'
     5/15 vs persist 'all' 0/8, p ~ .08; flagged as a confound before running).
   - **B81 persist swap: persist mode is NOT the variable.** HIGH latches forced to 'all' convert 3/6 (same as under
     'regs'); LOW latches forced to 'regs' 0/7. Conversion is a property of SPECIFIC latch genomes: H_6913 5/6 vs
     H_6923 1/6 at near-equal quality (pooled B80+B81).
   - **Mechanism (B82): distance in mutation space.** In H_6913, 15/1000 one-step mutants improve on the latch, and
     ALL 15 are RESET-like. One example re-gates a single branch onto a different register (JNZ r0 -> JNZ r6). H_6923
     has no improving mutant within two steps.
   - **RETRACTED (B83): 'stepping stone iff RESET is a coupled edit or two away'.** Over 10 latches, one-step density
     does not predict conversion (rho .43). The hand latch (6/6) and H_6929 (7/9) have NO improving one-step mutant
     and convert via multi-step paths. Conversion stays genome-specific and unexplained by quality, length, persist
     mode or one-step density.
   - **B84/B85:** short neutral walks do not find RESET from the reliable convertors (probably underpowered). A single
     hand latch converts 6/6 without a second variant (recombination between variants not required). The
     stepping-stone property is real and genome-specific but still unexplained. PARKED.
   - **B91:** latch immigration does not raise H_6923's conversion (1/6 -> 1/6), so the genome-specific RESET
     conversion is not basin capture (unlike the keyed d4 wall, B89).
7. **The distance wall holds for the KEYED class too (B86).** On the stock VM, keyed two-slot recall is reached in
   4/8 runs from a precursor two edits from the hand solver (SLOT_A, held-out .531, no fitness gradient). It is reached
   in 0/8 runs from the equally fit one-value shelf (.535). Caveat: the precursor is the hand solution minus two
   instructions.
   **Graded (B87):** precursors with d instructions missing, all on the same plateau, reach keyed recall in d2 5/8
   (9/16 with B86), d4 1/8, d6 0/8, d8 0/8. The reach rate falls steeply with edit distance and successes come early or
   not at all: the B55-B57 per-link slope, for a full keyed solver.
   **Budget (B88):** at 3x the generations (G=900) no success appears after gen 300 (d4 3/8, all by gen 12; d6 0/8). The
   wall is basin capture, not a waiting time. Pooled reach: d2 9/16, d4 4/16, d6 0/16, d8 0/8.
   **Immigration (B89):** re-seeding 10% fresh precursor copies each generation lifts d4 from 4/16 to 6/8 (p ~ .02)
   and allows late successes (gen 132), but d6 stays 0/8. The wall is basin capture (removable) times distance (not,
   at this budget). **B90:** d6 with immigration at G=900 is still 0/8 (pooled d6 0/32). Six missing coupled
   instructions are beyond this search; two are easy, four are reachable if the basin is protected.

## Finding 4 -- concurrent competition evolves negative-frequency-dependent niche partitioning (3/3 worlds)

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
7. **Third world (B71).** A minimal procedural ecology from outside the C6 named set, chosen by a pre-set rule:
   hardened rare-type CONC 6/6 (bootstrap lo .10-.16), SOLO 0/4, SHAM 0/2 testable; entropy and function criteria also
   met.
8. **Limits.** C6-generator worlds only; one VM and one search; no cooperation or communication (signal unused).

## Finding 5 -- communication does not evolve in this search, even one word away (B92-B95b)

1. **Regeneration-limited worlds are zero-sum for information (B92/B93).** A scout's signal only redistributes reward
   (group +.008) and costs the scout ~.2.
2. **A non-rival world makes honest signalling free and valuable (B93b).** With static pools, a hand scout lifts three
   blind listeners .869 -> 1.000 at zero cost to itself.
3. **No signalling evolves (B94).** From random gen 0 it is 0/6 under both individual and SHARED (group-mean) reward;
   genomes do not even scout.
4. **Even one word from full communication, the signal is not restored (B95/B95b).** It stays 0/6 under both rewards,
   and the listener half DECAYS when no one signals.
5. **Mechanism (reading).** Two-sided coupling; selection on a signal mutant is weak and diluted (a rotating scout
   signals in 2/8 episodes), while the complementary half is neutral and drifts away. This is unlike single-individual
   structures such as the keyed precursor, where every part is under selection.
   **Revised (B96/B96b/B97/B97b):** removing dilution (fixed scout) and decay (listener immigration) does not help
   (0/6 x 3). The measured selection coefficient of a restored signaller is s ~ .019 under BOTH scout schemes, so
   'dilution' was wrong. Raising the headroom doubles s (.046) and still gives 0/6. A clean one-word restore arises in
   only ~10^-4 of offspring. The barrier is quantitative: low mutation supply x weak selection, against neutral decay
   of the listener half.
   **Revised again (B98/B98b): the dominant term is MUTATIONAL LOAD.** Seeded signallers go extinct even at 20%
   (0/12 runs keep any). One-step children of a full communicator break the signal 31% of the time and listening
   40%, far above s ~ .046. Communication sits above an error threshold under this search's mutation pressure.

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
