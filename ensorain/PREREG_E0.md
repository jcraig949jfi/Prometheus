# ENSORAIN E0 "CHOO CHOO" -- preregistration, part 1 (design, gates, seeds)

Currency: 2026-09-23. Seat: Ensorain[m2-14baf7d5]. Authority: the founding
directive, roles/Ensorain/prompts/2026-09-23_charter/ (TRUNCATED inside
s12; see 00_README.md there). This file is committed BEFORE any
confirmatory run. Part 2 (economy constants frozen after dev-seed
engineering) is a separate, later commit; it may set constants, it may NOT
touch any gate, threshold, seed split or population defined here.

## 0. The question E0 answers, and the one it does not

E0 asks the cheapest discriminating question: in a navigable world larger
than an organism's persistent memory, does a bounded TT memory whose
ORGANISATION is under selection (mode order, rank profile, capacity split,
update constants) turn experience into competence that (a) a matched
randomised world does not support and (b) strong non-structural and
fixed-structure baselines at the same storage cap do not reach?

E0 does NOT test: communication, contraction-order puzzles (P4), spectral
gates (P5), within-life rank adaptation, compute amortisation on repeat
exposure. They are E1 candidates only if E0 returns A.

Prior risk stated up front (the seat's own dissent): a TT learner beating
caches on a world GENERATED as a low-rank TT is close to a tautology
(tensor completion works on low-rank tensors). Passing H1 is therefore
NECESSARY and NOT SUFFICIENT for verdict A. The non-trivial content must
come from H2 (selection discovers organisation a designer was not told)
and H3 (the C-vs-R separation persists as the world outgrows memory).

## 1. World (E0)

- Latent address space: D=6 modes, n=4 values each; N = 4^6 = 4096 cells.
  Every cell is one graph node. The organism observes the node's address
  as a 6-tuple, in an OBSERVED mode order that is a fixed scramble of the
  latent order (a law of the world class, unknown to the organism and to
  every hand-built baseline).
- Hidden field X. World C: a tensor train in the LATENT order with ranks
  (1,3,3,3,3,3,1), random cores, standardised to mean 0 / sd 1 over all
  cells. World R: X_C with its 4096 values randomly permuted over cells
  (identical value histogram, graph, economy, noise, action space, local
  difficulty; latent relations destroyed). Mixture worlds M_lambda for
  the dose-response: the cell values of X_C, a random subset of fraction
  lambda of cells permuted among themselves, lambda in {0, .25, .5, .75, 1}
  (M_0 = C, M_1 = R).
- Graph: directed. Each node has 4 exits to nodes differing from it in
  exactly one coordinate (chosen at random, fixed per world), plus with
  probability 0.1 a fifth one-way long jump to a uniform random node.
- Sensing: on arrival the organism observes y = X[v] + noise(sd 0.1) and
  its address; it sees exit ADDRESSES, never exit values.
- Economy (constants frozen in part 2): energy decays by a metabolic
  cost per step; entering v harvests g * max(0, X[v] - theta) unless v was
  harvested within the last T_regrow steps (then 0); compute is charged
  per flop-proxy unit (s2); death at energy <= 0; horizon L steps.

## 2. Compute proxy (charged to energy)

  TT entry evaluation      sum_k r_{k-1} r_k
  TT SGD update            3 x evaluation
  cache / hash probe       1
  kNN / linear scan        entries x D
  random-feature predict   weights
  buffer replay            cost of one update per replayed sample
Consistent proxy, not joules (directive s7).

## 3. Organisms and baselines (same policy skeleton, same cap C floats)

Policy skeleton, identical for all memory types: at each node, predict the
value of each exit's destination from memory, pick argmax with an
epsilon-random exploration; a fixed 8-entry transient tabu of recent nodes
(scratch, identical for all, not persistent memory). The memory is the
only difference between arms.

Storage accounting: every float in persistent state counts 1; a stored
address counts 1 (packed). A MemoryAudit walks the organism object and
refuses any persistent container not declared (cheat control, s5).

Arms:
  RANDOM      random exit
  NOMEM       predict 0 everywhere (explores via epsilon only)
  LRU         address->value cache, C/2 entries, LRU eviction; unseen = mean
  HASH        C-slot direct-mapped table, collisions overwrite
  KNN         LRU store, prediction = mean of stored entries at minimum
              Hamming distance
  ADDITIVE    per-(mode,value) biases (D*n floats), SGD
  RF          C random ReLU features of the one-hot address, SGD on weights
  LOWRANK     matrix unfolding (modes 1-3 x modes 4-6, 64x64), rank to cap, SGD
  TT_FIXED    TT in OBSERVED order, uniform rank filling the cap, fixed
              constants (no structural organisation)
  TT_TUNED    TT_FIXED with constants hand-tuned on dev seeds (the
              "literature" arm: what a competent designer ships)
  TT_EVOLVED  genome = (mode order, rank profile, lr, init scale, buffer
              fraction, replay count, epsilon); evolved on training
              seeds, frozen, then tested on held-out seeds
  DICT_UNCAP  uncapped exact dict of visited cells (upper-bound control)
  ORACLE      true X (positive control / ceiling)
  CHEAT       TT_FIXED plus a smuggled dict (must be REFUSED by the audit)

Caps C in {48 (tiny), 96 (small), 168 (the true TT's parameter count in
the latent order: "barely sufficient"), 384 (generous), 4096 (control)}.

## 4. Measurements

- Primary: lifetime harvest (energy earned) over the horizon, per organism,
  with survival time beside it.
- Secondary: exit-choice accuracy (chose the exit whose destination had the
  highest X) over decisions with >=2 distinct-valued exits; world
  reconstruction R^2 of the memory over ALL 4096 cells and over UNVISITED
  cells, computed by external instrumentation after death (the organism
  never sees it).
- INTERIM efficiency measure (the directive's s12 is truncated): useful
  information retained = R^2 over unvisited cells (deletion scores 0;
  memorisation of visited cells scores ~0 on unvisited ones), reported
  beside C and beside compute spent. Replaced or annotated when s12's
  remainder arrives. No gate below uses it.
- Chance floors published beside every number: RANDOM and NOMEM arms.

## 5. Controls (all three required; failure = instrument broken, no verdict)

- NEGATIVE: in R, every structural learner's unvisited-cell R^2 is within
  0.05 of 0 and no learner beats LRU on harvest by more than the
  run-to-run sd.
- POSITIVE: ORACLE has the top harvest in C and R; TT given the latent
  order and true ranks (planted) reaches R^2_unvisited >= 0.5 in C at
  C=168 with the dev-tuned constants.
- CHEAT: the CHEAT arm is refused by the MemoryAudit (test must fail
  loudly); a second cheat -- ORACLE values injected into a legal TT (TT-SVD
  of true X at cap) -- must score within 10% of ORACLE, proving the
  harvest channel can see a correct memory.

## 6. Hypotheses and preregistered gates (thresholds fixed now)

Confirmatory seeds: world instances 10000-10039 (40), organism seeds per
instance 0-1. Dev/engineering seeds: 0-999. Evolution training seeds:
1000-1999. No confirmatory seed is touched before part 2 is committed.

H1 (premise). At C in {96, 168}, in world C, TT_TUNED harvest exceeds the
  best non-TT bounded arm (LRU, HASH, KNN, ADDITIVE, RF, LOWRANK) by >=10%
  (paired over instances, 95% bootstrap CI lower bound > 0), AND the
  interaction holds: (TT_TUNED - best non-TT) in C minus the same in R
  > 0 with CI lower bound > 0.
H2 (selection discovers organisation). On held-out C instances, TT_EVOLVED
  beats TT_TUNED by >=10% harvest at C=96 or C=168 (CI lower bound > 0),
  AND the evolved mode order recovers the latent order better than chance:
  its TT rank requirement for X under the evolved order (numerical TT-SVD
  ranks at tol 1e-8) is lower than the median over 200 random orders.
  Cross-class control: the genome evolved on class C1 tested on a class C2
  with a different latent order must lose its H2 advantage (>=50% of the
  gain gone); otherwise the advantage is generic tuning, not discovered
  physics.
H3 (outgrowing memory). Dose-response: TT_TUNED's harvest advantage over
  the best non-TT arm decreases monotonically in lambda over
  M_0..M_1 (Spearman rho <= -0.9 over the five points, and M_1 advantage
  CI includes 0 or is negative).

## 7. Verdict rule (precommitted, written to be losable)

  Controls fail            -> INDETERMINATE; repair instrument, rerun.
  H1 fails                 -> B (premise does not produce a gap worth
                              a tensor world; bounded TT is not better
                              than cheap memories here).
  H1 passes, H2 fails      -> B-MUNDANE: the phenomenon is "tensor
                              completion works with designer constants";
                              recommend B unless H3 plus a named E1
                              mechanism gives a specific reason.
  H1, H2 pass, H3 passes   -> A.
  H1, H2 pass, H3 fails    -> A-WEAK; state the failure shape.

Give-it-a-chance clause (directive s0): if TT arms underperform because the
LEARNER fails (planted-order TT cannot fit X from its own samples:
positive control fails) that is B2 (search/learner insufficiency), not B1
(the world does not reward structure). Up to three engineering rounds on
the learner are permitted on DEV seeds only, each journaled; gates do not
move.

Seat's predictions (written to be lost): H1 PASS (expected; weak evidence).
H2 FAIL on the 10% harvest margin but PASS on order recovery (selection
finds the order; the harvest gain is smaller because TT_TUNED in the
wrong order still fits with rank to spare at C=168). H3 PASS. Net
prediction: B-MUNDANE is the single most likely outcome (p ~ 0.5).
