# ENSORAIN E1 "KNIFE FIGHT" -- preregistration, part 1 (design, gates, seeds)

Currency: 2026-09-23. Seat Ensorain[m2-14baf7d5]. Authority: operator E1
authorization, roles/Ensorain/prompts/2026-09-23_e1_authorization/
(rulings R1-R8). Committed BEFORE any E1 code runs. Part 2 (constants
frozen after dev engineering) may set constants only; it may not touch
any gate, threshold, arm list, seed split or the verdict rule below.
E0 is FROZEN (R1); nothing in E1 reuses E0 rows as evidence.

## 0. Question and stance

Under severe memory pressure, when survival requires retaining fine
latent structure across contexts, does a tensor-structured (TT) memory
achieve materially more transferable competence per stored parameter
and per unit compute than simpler representations, when every arm gets
the same charged batch consolidation, the same scratch allowance, the
same tuning budget and the same compute budget?

Hostile by construction. Two tautology risks are declared up front:
(1) the hidden world IS a tensor train, so a TT memory has the matching
inductive bias; a TT win therefore shows the premise CAN be realised by
bounded organisms under survival pressure, not that TT is better in
general. (2) With 4 modes there are only 24 mode orders, so order search
is easy; E1 does not test order discovery. What E1 tests is whether any
simpler representation -- including a non-TT TENSOR memory (CP) and a
matrix unfolding with a TUNED mode partition -- gets within 10%.

## 1. World (one small world class)

- Latent: 4 modes (call them A, B, C, D), 8 values each; 4096 cells.
  Hidden field X = TT in latent order A-B-C-D with ranks (3,3,3), random
  normal cores, scaled to sd 1 (no centring). The organism sees the four
  address coordinates in a fixed scrambled order (a law of the class).
- HELD-OUT REGION: 25% of the 64 (A,C) index pairs are UNSEEN. No
  observation ever touches a cell with an unseen (A,C) pair. A memory
  that stores coordinates cannot answer there; a memory that stores
  factors can (A (x) C is never co-observed for those pairs).
- Event stream (identical for every arm on a given instance; paired):
  1,200 events. Phase 1 (events 0-599): 90% observation chambers, 10%
  locks. Phase 2 (600-1199): 30% observation, 70% locks. Observations
  therefore precede most locks by hundreds of events (delayed relevance).
- Observation chambers ("different projections"): a noisy (sd 0.1) FIBER
  of 8 values along mode B or along mode D (50/50) at a random seen
  address. Fibers along A or C are never shown (they would cross into the
  held-out region).
- Locks (the answer is never visible locally; two locks at the same local
  position differ only by latent address = latent context):
    L1 entry X[a,b,c,d] at a seen (A,C) pair, not previously observed
    L2 entry at an UNSEEN (A,C) pair                 (held-out transfer)
    L3 contraction sum_d X[a,b,c,d] w_d, w a random unit vector
       ("transformed D"), at a seen or unseen pair (50/50)
  Mix L1 30% / L2 40% / L3 30%. A lock pays reward g only if
  |answer - truth| < tau * sd(query type over the world); otherwise 0.
  tau is TIGHT (constant in part 2, chosen on dev so that R^2 ~ 0.5
  models mostly fail and R^2 ~ 0.99 models mostly pass).
- Economy: metabolism per event, start energy, death at 0 (constants in
  part 2). Compute charged per unit (s3).
- WORLD R (negative control): same instance, the 4096 values permuted
  over cells; same event stream, same held-out region.

## 2. Memory, scratch, consolidation (R3)

- Persistent memory: cap C floats (audited as in E0; the E0 MemoryAudit
  pattern, smuggled state refused).
- Scratch allowance (declared, identical for every arm, NOT persistent):
  S = 128 samples (address + value). Every observed value enters scratch.
  When scratch is full the organism CONSOLIDATES: refits its persistent
  memory from scratch with a warm start and a proximal term toward its
  current parameters, then scratch is cleared. Predictions read only
  persistent memory.
- Consolidation per arm (each arm's natural fitting method):
    TT        ALS sweeps over cores (per slice ridge least squares)
    CP        ALS over factor matrices
    LOWRANK   ALS on a 2-group matrix unfolding (partition is a gene)
    MLP       gradient epochs (one hidden layer, one-hot input)
    LRU       insert scratch samples as raw (key,value); evict oldest
    KNN       LRU store; answer = mean value at minimum Hamming distance
- Compute charge: consolidation = samples x persistent params used x
  sweeps (uniform proxy for every fitting arm); query = the arm's
  per-entry evaluation cost x entries needed (L3 needs 8 entries).
  MATCHED COMPUTE BUDGET: an identical per-life compute ceiling for all
  arms; consolidation is refused once the ceiling is reached (part 2
  sets the ceiling).

## 3. Arms

  NOMEM        predicts 0 (chance floor; energy reference)
  LRU, KNN     raw-sample memories
  CP           CP decomposition, rank to cap
  LOWRANK      matrix unfolding, partition + rank tuned
  MLP          one hidden layer, width to cap
  TT_OBS       TT in the observed order, tuned constants
  TT_TUNED     TT with order, ranks and constants tuned (the experimental
               TT; "best TT" = max of TT_OBS and TT_TUNED by mean EFF)
  TT_LATENT    POSITIVE CONTROL (R6): latent order, true ranks, TT_TUNED's
               learning constants -- same machinery
  TT_INJECT    CHEAT CONTROL: TT-SVD of the true field at cap, latent
               order, no learning
  ORACLE       true field (ceiling)
  SMUGGLER     TT plus a hidden dict (must be refused by the audit)

TUNING (equal budget, hostile to TT): every tunable arm (CP, LOWRANK, MLP,
TT_OBS, TT_TUNED) gets the SAME random-search budget -- 24 configurations
x 4 training worlds per cap -- over its own genes (structure genes
included: TT order+ranks, LOWRANK partition+rank, CP rank, MLP width;
plus proximal strength, sweeps/epochs, learning rate). Selection
objective: mean EFF (s4) on training worlds. KNN/LRU have no genes.

## 4. Metric (R4)

Per life: U = total lock reward earned - compute energy charged.
Reference: U_NOMEM on the same instance (chance-level lock reward).
    EFF = (U - U_NOMEM) / P_used
P_used = persistent floats actually used (>= 1). Reported beside it, per
life: reward on L2+held-out L3 (transfer utility), reward on L1+seen L3
(puzzle utility), compute energy (the compute term), survival steps,
R^2 over held-out-region cells (instrumentation, not in any gate).

## 5. Controls (all must pass or the verdict is INDETERMINATE)

POSITIVE (R6): TT_LATENT at C=192 (the true TT's exact parameter count)
  reaches median L2 success rate >= 0.5 AND median R^2 over held-out
  cells >= 0.5.
CHEAT: SMUGGLER refused by the audit; TT_INJECT at C=192 earns >= 0.9 x
  ORACLE's lock reward.
NEGATIVE: in WORLD R, no arm's L2 success rate exceeds NOMEM's by more
  than 0.05 (absolute) at any gated cap.

## 6. Governing gate G (R5) and the verdict

Gated caps: C in {128, 192} (severe pressure: 192 = exactly the true TT
in the latent order; 128 = below it). Caps 96 and 384 are run and
reported, not gated.

G passes iff at EVERY gated cap, for EVERY non-TT arm X in {LRU, KNN,
CP, LOWRANK, MLP}:
    mean EFF(best TT) >= 1.10 * mean EFF(X)
    AND the paired bootstrap (instances, 10,000 resamples) 2.5% bound of
    mean(EFF_bestTT - 1.10 * EFF_X) > 0.
If ANY non-TT arm at ANY gated cap fails this (comes within 10%), B.

TRANSFER: best TT's L2 success rate exceeds NOMEM's, paired bootstrap
2.5% bound > 0, at C=192.

TRANSPLANT (R7), reported, qualifies A: after a full life on instance k,
the persistent memory is carried into a second life on the SAME latent
factors with every mode's index labels relabeled by an undisclosed random
permutation and the observed mode order reshuffled. Compare L1+L2 success
over the first 400 events of life 2, CARRIED vs FRESH memory, per arm,
paired bootstrap. TRANSPLANT PASS for TT iff carried > fresh with 2.5%
bound > 0.

VERDICT:
  controls fail                 -> INDETERMINATE (no TT claim scored)
  G fails                       -> B (close the branch, R-closing clause)
  G passes, TRANSFER fails      -> B (wins without transfer are not the
                                    claim)
  G, TRANSFER pass, TRANSPLANT pass  -> A (earned E2)
  G, TRANSFER pass, TRANSPLANT fails -> A-BOUND (competence is real but
                                    tied to the coordinate frame; E2 must
                                    address that first)
Secondary (reported, never gated): kappa x0 and x4 sensitivity of G.

## 7. Seeds

dev / engineering 0-999; tuning 1000-1999; confirmatory world instances
20000-20039 (organism seeds 0-1). Class seed 0. Transplant relabel seeds
derived from instance + 7,000,000.

## 8. Engineering allowance (give-it-a-chance, bounded)

Up to three learner-engineering rounds on DEV seeds for the shared
consolidation machinery, journaled, before part 2. Their purpose is the
positive control only; they may not look at any non-TT arm's result for
tuning the TT. World constants (tau, economy, compute ceiling) are set
on dev in part 2 by stated criteria, not by which arm wins.

## 9. Seat predictions (losable)

P1 positive control PASSES (batch ALS with 5,000+ samples is enough).
P2 G FAILS at C=128 or 192: CP (a tensor memory, 4x8xR = 32R floats) or
   LOWRANK with the right partition gets within 10% of TT per parameter.
   Net predicted verdict: B (p ~ 0.6), A-BOUND (p ~ 0.25), A (p ~ 0.05),
   INDETERMINATE (p ~ 0.1).
P3 TRANSPLANT fails for every arm (carried memory is keyed to labels).
