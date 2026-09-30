# Tyche v2 design -- pressure map of perceptual emergence (draft for prereg)

Currency: 2026-09-30. Directive: roles/Tyche/prompts/2026-09-30_v2_pressure_map/
(db985709e). This is the design; the preregistration freezes it after the
world certificates and a timing pilot.

## 0. Question

Under what ecological pressures do new perceptual capabilities appear, and
what causal path produced them? Output: a phase diagram P(new sense | axes,
difficulty class) plus a causal natural history of every sense that
appears. Mostly-null runs are informative by construction.

## 1. Axes (each an explicit, separable mechanism from v1)

  H  selection harshness
     STRICT  a lens survives / reproduces only with a SIGNIFICANT gain
             (val z >= 2) on some case; no reserve; empty slots are random
             immigrants. "Would have died" is true by construction.
     LEX     eps-lexicase over all cases (v1 V0): noisy survival.
     RES     LEX + explicit utility-free reserve with neutral drift (v1 DE)
  V  ecological diversity
     SOLO    target world alone (+ nothing else)
     RELATED target + 3 worlds of the same class, other parameters
     BROAD   every target class + donor worlds + unrelated worlds
  C  coalition depth: SINGLE | PAIRS | PAIRS+TRIPLES
  M  mutation chemistry: MUT (local ops only) | MUT+GRAFT |
     MUT+GRAFT+LOL (lens-of-lens: a genome may consume the output of
     another living lens; fused compositions b(a(X)))
  Budget: equal evaluation units per world per run, as v1; pair/triple
  screening made cheap (outputs cached; pre-screen by train-split joint
  mutual information before any organism fit) so combination is not
  penalised by construction (v1 F3).

## 2. Difficulty classes (construction hidden from evolution)

  D1 SMOOTH     additive threshold of delayed inputs; each precursor
                individually informative (hill climbing should work)
  D2 DECEPTIVE  a decoy channel agrees with Y 65%; truth is a 2-way
                zero-marginal composition elsewhere
  D3 ORDER-2    xor of two delays (v1's Z; soft footholds allowed --
                the control for "graded footholds")
  D4 ORDER-3/4  secret sharing: Y = (s1 + ... + sk) mod m over delayed /
                accumulated shares; every (k-1)-subset certified to carry
                ZERO information (exact, by truth table)
  D5 EXAPT      Y_target = P xor Q where P is directly rewarded ONLY in a
                separate donor world (Y_donor = P); present only when V
                includes the donor (tests whether exaptation needs niches)
  D6 REPR       useful only after one lens changes representation for a
                second: Y = [S(t) == S(t-d)] with S = hidden accumulator
                state; S(t) and S(t-d) alone are zero-marginal, the
                composition delay(S) needs a lens on top of a lens
  D7 GENERATED  procedural opaque systems: random boolean functions over
                4-6 derived bits (delays, accumulator states, window
                parities) accepted ONLY if exactly first-order correlation-
                immune (every single derived bit and every raw-feature-bank
                feature carries ~0 information) and not parity; the
                generator's grammar differs from the lens chemistry; the
                construction is stored only in the answer key
  Negatives: TARGET_STRUCTURE_DESTROYED twin per class; keyed PRF.

Certificates (computed before freezing, committed): per world, exact
lower-order information of the hidden precursors (truth tables), max MI of
Y with a raw feature bank (all single delays 0..16, window sums 2..8,
accumulators mod 2..5 of every channel) against a permutation null,
oracle deficit, raw-ecology chance.

## 3. Regime change (Block R; the directive's most informative pressure)

Regime worlds switch law at an unannounced generation G*: L1 rewards one
behaviour; L2 needs precursors that were useless (zero-marginal) under L1.
Pairings: L1 smooth -> L2 order-2; L1 smooth -> L2 order-3; L1 order-2 ->
L2 reusing one L1 precursor (retention helps) vs L2 sharing none.
Measures:
  latent option value = generations (and units) after G* until the best
     val gain reaches 50% of the L2 oracle deficit; AUC of post-shift gain
  stored optionality at G* = fraction of living lenses (population and
     reserve) whose outputs carry L2 precursor information (functional MI
     above null), measured on the shift generation
  retention of L1 senses after the shift (admitted lenses stay in the
     ecology)

## 4. Natural history of every sense (answers the directive's 9 questions)

For every world where a lens reaches >= 50% of the oracle deficit
(replicated), from logged genealogy + per-generation evaluations with z:
  carriers of each hidden precursor -- FUNCTIONAL: MI(lens outputs;
     precursor variable) above a permutation null (handles soft/partial
     precursors, v1 F2), not syntactic op matching
  first carrier of each precursor; generations it survived with zero
     target utility (home val z < 2); why it survived: the cases it won
     each generation, marked significant (z >= 2) or noise-level, and the
     reserve / drift / credit events that kept it
  other worlds that valued it (significant cases only)
  arrival of each other precursor; the gain trajectory before the jump
     (weak gradient or flat)
  the phase-transition edge: the parent -> child step with the largest
     home gain increase, its exact operator (point / insert / graft /
     fuse / drift / lens-of-lens) and the donor lineage's valued worlds
  strict-gating counterfactual for every ancestor: had it any case with
     val z >= 2 in its lifetime generations?
  assembly mode: MUTATION | GRAFT | COALITION | EXAPTATION (donor valued
     significantly on another world) | DRIFT-PRESERVED (an ancestor
     carried a precursor only through reserve/drift)

## 5. Design (fractional, budgeted)

Block R: H{STRICT, LEX, RES} x V{SOLO, RELATED, BROAD} = 9 conditions,
  2 seeds = 18 runs; C = PAIRS, M = MUT+GRAFT fixed.
Block M: centre (LEX, BROAD, PAIRS, MUT+GRAFT) + one-axis moves
  H{STRICT, RES}, V{RELATED, SOLO}, C{SINGLE, TRIPLES}, M{MUT, LOL}
  = 9 conditions, 2 seeds = 18 runs; all difficulty classes inside each
  run (SOLO = one small run per target class).
Compute estimate (v1 measured ~0.25 core-h per 13-world run at 6000
units): Block R ~5 core-h, Block M ~6 core-h, certificates + pilot ~1.
Two separate items, each under the 16 core-h envelope; WORK_STATE
`running` committed before each launch.

## 6. Build order

1 z-scores stored in every evaluation (strict gating and the history need
  them) 2 worlds_v2 with hidden precursor variables + certificates
  3 regime switching 4 STRICT / RES arms, SOLO / RELATED / BROAD
  compositions 5 triples + cheap MI pre-screen 6 lens-of-lens
  7 natural-history tracer (functional carriers) 8 phase-diagram report
  9 tests (certificates exact; tracer on a synthetic genealogy with a
  known answer; strict arm cannot keep a zero-gain lens) 10 pilot for
  timing only, then PREREG.
