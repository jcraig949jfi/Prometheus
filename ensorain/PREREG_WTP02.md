# ENSORAIN WTP-02 -- preregistration (necessity-gated foundry search)

Currency: 2026-09-24. Seat Ensorain[m2-14baf7d5]. Authority: operator
WTP-02 authorization, roles/Ensorain/prompts/2026-09-24_wtp02_authorization/
(verbatim). Committed BEFORE any WTP-02 world runs. WTP-01 is frozen
exactly as recorded (verdict REDESIGN, 092577f21); its engine stays
replayable at 93998df6f. WTP-02 uses a new package, ensorain/wtp2/, that
reuses WTP-01's registry, genome grammar, field generators, geometries
and memory substrates, and REPLACES the executor's measurement, randomness
and admission. Anything below marked "fixed" cannot move after data.

## 1. Repairs (each maps to a WTP-01 defect)

R1 METRIC (fixed). Reference variance V0 = variance of the field at world
   birth, never updated. Absolute competence AC = -log10(MSE / V0),
   clipped to [-3, 6], on a fixed battery of 256 cells. The battery is
   split at end of life into SEEN (cells the organism observed) and UNSEEN.
   CG = AC(organism) - AC(zero predictor), same battery, same V0 (an
   immutable baseline: the trivial predictor, not the organism's birth).
   CGu = CG on UNSEEN cells only (memorisation cannot produce it).
   AC and CGu are reported separately and never merged.
R2 DEGENERACY (fixed). A world whose field variance falls below 0.05 V0
   at any checkpoint, whose reachable node set falls below 5% of nodes,
   or whose rewarding cells vanish, is labelled DEGENERATE WORLD at that
   point and not scored.
R3 RNG STREAMS (fixed). numpy SeedSequence(seed).spawn into named streams:
   world_gen, world_dyn, noise, policy, learner, mutation, transplant,
   controls; each child seed recorded. Environmental stochasticity
   (drift, catastrophes, rewiring, observation noise) draws only from
   world_dyn / noise, pre-drawn per step, so a transplant or ablation
   replays the identical environment with a different organism state.
R4 MEMORY PRESSURE (fixed). Memory cap = band x cells, band drawn from
   {0.01, 0.03, 0.10, 0.25}; external marks are capped at the same number
   of entries (FIFO). A substrate that cannot fit is illegal.
R5 LONGER LIVES. Lifetime 1,000-3,000 steps (was 200-600).
R6 NULL PER DETECTOR and structure dependence (s4-s5).

## 2. Necessity preflight (fixed; a world is ADMITTED only if all pass)

N1 memory pressure: organism persistent floats <= 0.25 x cells (by R4),
   and external mark capacity likewise.
N2 no-learning loses: a memoryless random walker AND a frozen birth
   organism, 300-step preflight lives, 2 seeds each: net energy U < 0 in
   all four. Any prosperity without learning -> reject.
N3 learnable: best of a planted-learner panel (DCT least squares with
   <= cap coefficients; low-rank ALS on the balanced unfolding at the cap;
   additive per-mode means), fitted from n = min(2 x lifetime, cells / 2)
   noisy random samples, reaches R^2 >= 0.10 on held-out cells.
N4 structure matters: the same panel on the shuffled field (values
   permuted over cells) reaches held-out R^2 <= 0.05 AND <= 0.5 x its real
   value.
N5 noncollapsed: an organism-free dry run of the world's transition laws
   for the full lifetime keeps variance >= 0.1 V0, reachable nodes >= 30%,
   and >= 1% of cells rewarding.
Candidates are drawn until 1,500 are admitted (or 30,000 candidates are
exhausted); rejection counts per gate are reported.

## 3. Observables per life (vector; never merged)

AC, CG, CGu; U and U_gain = U - U(frozen twin); survival steps;
RG reachability gain: after the life, two 40-step excursions from the
same node with identical environment streams, one with the trained
memory frozen, one with the birth memory frozen, both greedy on their own
predictions; RG = (rewarding top-10% nodes reached, trained - birth) / 40;
CA compute amortization: (gain per compute unit, last third of life) /
(first third); RR representation reorganization: effective-rank change,
family conversion, sparsity change, each with CGu before vs after;
compression = CGu per persistent float.

## 4. Detectors and their nulls (fixed)

Each life runs three twins on the same seed: SHUFFLED (field values
permuted), FROZEN (no learning), RANDOM (memoryless random walk).
  D1 competence        CGu >= 0.10                       null SHUFFLED
  D2 jump              one-checkpoint rise in unseen AC
                       >= 0.30 and >= 5x the median step null SHUFFLED
  D3 compression       CGu/float in the top 1% and CGu >= 0.05  null SHUFFLED
  D4 anti-learning     CG <= -1                          null FROZEN
  D5 disagreement      U_gain in top 5% with CG <= 0, or CGu >= 0.10
                       with U_gain <= 0                  null RANDOM
  D6 survival          steps >= 1.5 x FROZEN steps and died-vs-alive
                       differs                           null FROZEN
  D7 reorganization    RR event with CGu rising by >= 0.10 after it
                                                         null SHUFFLED
  D8 reachability      RG >= 0.10                         null SHUFFLED
  D9 amortization      CA >= 3 with CGu >= 0.05          null SHUFFLED
Structure dependence SD = statistic(real) - statistic(null twin).

## 5. Statuses (fixed)

Wave B, per anomaly, 5 fresh seeds each with its null twin:
  REPLICATED       detector fires in >= 3/5 real seeds
  FALSIFIED        <= 1/5
  STRUCTURE-DEPENDENT  REPLICATED and the null fires in <= 1/5 and the
                   median SD >= 0.10 (>= 50% of the median statistic for
                   D1/D3/D7/D8/D9)
  STRUCTURE-INDEPENDENT REPLICATED and the null fires in >= 3/5
  MECHANICAL       D4/D6 REPLICATED with the FROZEN null firing >= 3/5
  METRIC ARTEFACT  any firing seed also DEGENERATE or clip-bound
  UNRESOLVED       otherwise
  DEGENERATE WORLD R2 fires in >= 3/5 seeds
Wave C (STRUCTURE-DEPENDENT only): single-dial interventions (memory
  band x1/3 and x3, credit delay 0 / +16, drift 0 / +0.3, door-close 0 /
  0.3, rewiring off / on, observation cell <-> fiber, policy -> random,
  rule -> none, marks off), 3 seeds each; a dial is CAUSAL if its
  intervention removes the phenomenon in >= 2/3 seeds. CAUSAL SUPPORT =
  >= 1 causal dial and >= 1 non-causal dial. Then sweep the causal dials
  (never memory by default): 7 levels x 4 seeds, bracket present/absent,
  refine midpoints twice. PHASE BOUNDARY = adjacent levels whose means
  differ by > 3 x pooled within-level sd, same sign in both seed halves,
  phenomenon present on one side and absent on the other.
Wave D (CAUSAL SUPPORT): freeze learning, reset memory, ablate half the
  factors, destroy marks, shuffle modes, reskin graph, transplant the
  learned memory into the same world (identical environment streams),
  transplant the learning law into a fresh organism, freeze world
  dynamics, remove irreversibility, change credit delay. ARTIFACT CARRIER
  identified if transplanted memory keeps >= 50% of CGu while reset
  memory keeps <= 20%.
Wave E (Wave-D survivors): transplanted memory's CGu gain over a fresh
  organism in new seeds, reskinned, related (local mutation), modified
  topology, altered basis. TRANSFERRED if >= 50% of native CGu survives
  in >= 2 of those.
Wave F (only if CAUSAL SUPPORT exists): up to 100 recombinants of
  surviving genomes with unrelated niche elites; RECOMBINED SUPPORT if a
  recombinant is itself STRUCTURE-DEPENDENT on replication.
FAILURE-FOSSIL LANE: WTP-01 specimen b235013022100e1f in the WTP-01
  engine (its native physics): 2^4 factorial over {Hebbian vs SGD, credit
  delay vs 0, irreversibility vs none, drifting vs frozen world} x 3
  seeds, logging the jump, rank trace and parameter norm. Small; reported
  separately.

## 6. Verdict (fixed)

FOUND CANDIDATE INTELLIGENCE PHYSICS -- EXPAND iff >= 1 phenomenon is
  REPLICATED + STRUCTURE-DEPENDENT + CAUSAL SUPPORT + ARTIFACT CARRIER
  (Wave D) + one of {PHASE BOUNDARY, TRANSFERRED, D9 amortization,
  D7 reorganization, D8 reachability} holding on the same specimen.
FOUNDRY WORKS, SIGNAL STILL SPARSE -- CONTINUE SEARCH iff the instruments
  validate (s7) and >= 1 STRUCTURE-DEPENDENT phenomenon exists without
  the full chain.
SEARCH SPACE REMAINS DEGENERATE -- PARK/REDESIGN otherwise.
Also reported (s21 of the authorization): the fraction of admitted worlds
with CGu >= 0.10 AND SD >= 0.10 -- does WTP-01's 1.1% collapse to 0?

## 7. Instrument validation (fixed; run before Wave A, reported)

V1 a world forced to collapse (catastrophe rate 1) is labelled DEGENERATE,
   never scored; V2 a table memory in an admitted world has CGu ~ 0
   (memorisation cannot reach unseen cells); V3 a transplant with the same
   seed reproduces the identical environment event stream; V4 each
   detector's null fires on a planted-positive twin as expected (shuffled
   twin removes D1 in a structured world).

## 8. Seat predictions (losable)

Admission rate 5-20%. The CGu >= 0.10 & SD >= 0.10 fraction is small but
nonzero (0.2-2%), dominated by low-rank/DCT/CP learners in low-rank or
spectral fields. Verdict CONTINUE SEARCH (p .5), PARK/REDESIGN (p .35),
EXPAND (p .15).

## 9. Addendum before any WTP-02 campaign row (dev smoke only; seeds
## 9,000,000+ / 7,000,000+, not campaign seeds)

A1 N2b ECONOMIC POSITIVE CONTROL. First admitted lives (dev) all died in
   100-500 of 1,000-3,000 steps: N2 showed no-learning loses, nothing
   showed learning CAN pay. Added: an ORACLE organism (reads the true
   current field; same policy and costs) must end with positive energy.
A2 ECONOMY CALIBRATION. With random economic constants the oracle itself
   lost in 34 of 36 N2-passing worlds. Each candidate is therefore
   calibrated: income rates (metabolism 0, ample energy, 600 steps) of the
   random walker, the frozen organism (2 seeds each) and the oracle
   (2 seeds). Reject (gate N2c) unless oracle_min > 0 and
   gap = oracle_min - max(base) > 0.02 and > 0.2 x |max(base)|
   ("information must pay"). Metabolism := max(base) + 0.5 gap, written into
   the genome (resource.calibrated = true). Then N2 (random and frozen lose,
   300 steps, 2 seeds) and N2b (oracle wins) are VERIFIED with the
   calibrated economy. This places every admitted world on the edge where
   only competence survives; it does not make any world easier.
A3 CANDIDATE CAP 30,000 -> 150,000. Dev admission rate with A1-A2 is
   ~1.3% (4/300; rejections N3 93, N5 82, N1 77, N2 29 -- mostly a random
   walker trapped in dead topology, i.e. correctly DEGENERATE -- N2c 13).
   1,500 admitted worlds need ~115k candidates.
A4 START NODE. The dry run (N5) measures reachability from node 0;
   organism 0 now starts at node 0 and one-way / hazard edges are built
   inside world construction, so the dry run and the life share them.
A5 BUG FIX (shared substrate code, ensorain/wtp/organism.py): the TT
   "permute" memory hazard reordered modes of different sizes and crashed
   (likely several of WTP-01's 17 crashes). It now permutes only among
   modes of equal size. WTP-01 remains replayable at its own commit.

### A6 (2026-09-24, pre-data: no Wave A row had been written) — two executor fixes
- **Mutation crash.** Wave A's second batch crashed (`KeyError: lifetime2`) because WTP-01 `mutate` redraws keys a fresh
  genome lacks. `genome2.mutate` is now WTP-02-aware: it redraws only keys present in a normalized fresh genome and drops
  `resource.calibrated` so preflight recalibrates the economy of every child. No gate, threshold or proportion changed.
- **V3 birth digest.** `init_digest` was hashed at END of life from the path-mutated graph, so V3 (same seed, same
  battery+graph) failed for a bookkeeping reason. It is now hashed at birth, before the life loop. Validation is rerun
  from scratch by `campaign2 all`; the first run's V3 fail is kept in the journal.
- Admission is now checkpointed to `waveA_admission.json` after every batch (`partial=true` until the wave closes).

### A7 (2026-09-24, declared while Wave A admission is running, before any Wave A life has been analysed) — lineage clustering
After two batches, 242 of 307 admitted worlds (79%) are mutants, descending from 28 founders; the largest lineage has 25.
The per-candidate admission gates do not see this. The strategy mix (40/25/20/15) is unchanged. However, mutants of admitted
worlds pass the gates far more often than fresh draws, so the admitted population is lineage-clustered.
Substrate-generator spread is still broad: spectral 101, pairwise 65, cp 58, tt 38, lowrank 23, sum 17, sparse 5.
**Added reporting (no gate or threshold changes):** every Wave A fraction, including P(CGu >= .1 & SD >= .1), is reported
two ways. (i) Per world, as preregistered. (ii) Per founder lineage: each world is traced to its root founder through
`meta.parents`, and a lineage counts as positive if any member is positive. The report also gives the median fraction
within each lineage. A specimen claim must hold at the lineage level: two positives from one lineage count as one
specimen, not two.
