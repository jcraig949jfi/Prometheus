# Intake of the 15 crosswalk templates Archaeon mapped toward ludus/ (2026-09-11)

Currency: 2026-09-11. Source: archaeon/docs/expansion/CROSSWALK.md at
57533fa76 (the 15 entries whose "Adjacent Prometheus home" names ludus/).
Nothing is ingested. Each template is classified by WHAT IT WOULD
CONTRIBUTE to the World Foundry: WORLD, WORLD GENERATOR, FITNESS
FUNCTION, CURRICULUM OPERATOR, WORLD PRIMITIVE, QUALIFICATION
INSTRUMENT, or INSPIRATION only. A template may contribute more than
one. The "Next action" column is what Ludus would do, not a commitment;
committed work is in BACKLOG_H0H5.md.

Legend for the fit column: EXISTS = the arena/bench already has the
piece; GAP = missing and buildable in ludus/; EXTERNAL = Herakles's
backend route; NOT-LUDUS = belongs to another seat.

## interacting_landscapes

coevolution.parasites.v0 (Hillis host/parasite)
- contributes: WORLD GENERATOR (the parasite population IS a generator
  of test cases) + FITNESS FUNCTION (pairwise interaction rule) +
  QUALIFICATION INSTRUMENT (the held-out iid set that breaks the
  selection relation is exactly the control the bench doctrine
  requires).
- fit: GAP for the two-population chaining (R-SUBSTRATE, Vivarium/
  Archaeon); EXISTS for "a world with a held-out evaluation set" once
  W8 exists for any world.
- Ludus next: supply the held-out evaluator and the interaction rule
  as a world; leave population chaining to Archaeon.

hide_and_seek_autocurriculum.v0
- contributes: INSPIRATION only at this scale (continuous physics,
  two trainable teams under self-play). The transferable idea is the
  CURRICULUM OPERATOR "opponent as curriculum" and the change-point
  detector over strategy regimes.
- fit: EXTERNAL (physics world) ; the arena has SIMULTANEOUS movers
  but no continuous physics and no affordance richness.
- Ludus next: none until a discrete affordance-rich world exists.

maml_few_shot.v0
- contributes: WORLD PRIMITIVE "task distribution with SHARED
  STRUCTURE and support/query splits" (a family knob the grammar
  needs: how much structure is shared across members).
- fit: NOT-LUDUS for the meta-learner (C-4 autodiff backend);
  GAP for a world family with a declared shared-structure parameter.
- Ludus next: the shared-structure knob is a candidate primitive
  (section 4 rules apply: needs a perturbation).

mcc.bipartite.v0 (minimal criterion coevolution)
- contributes: WORLD GENERATOR (an evolvable environment
  representation whose difficulty can genuinely increase) + FITNESS
  FUNCTION (the existential minimal criterion, no ranking).
- fit: GAP; the closest existing object is FOUNDRY-DECAY (a family
  with a knob) but its knob is not mutated by anything.
- Ludus next: a mutable (seed, params) environment representation
  with a distance; the solver side is Proteus's; the coupling is
  Archaeon's. Second-closest to the machinery the operator wants after
  POET.

poet_paired_coevolution.v0
- contributes: WORLD GENERATOR (parameterised environment family with
  a MUTATION OPERATOR and a DISTANCE) + CURRICULUM OPERATOR (minimal
  criterion admission: not too easy, not too hard, adjudicated against
  the whole agent population) + FITNESS FUNCTION (transfer vs direct
  optimisation on the same environment).
- fit: GAP on every piece except "a family of worlds with an arena";
  FOUNDRY[gate,decay,k,cap,h] is already a parameterised family and is
  the cheapest place to add mutate() and distance().
- Ludus next: THIS is the vertical-slice candidate (LUDUS-06):
  family + mutate + distance + minimal-criterion admission over a
  cheap-baseline population; the agent side comes from Proteus's
  registry through a Ludus-authored binding. The operator singled it
  out; the crosswalk says the same.

## population_ecology

creativity.v0 and novelty.search.v0 (novelty search, two entries)
- contributes: FITNESS FUNCTION (k-NN novelty over a persistent
  archive; objective-blind selection) + QUALIFICATION INSTRUMENT (the
  descriptor-degeneracy check with positive and negative controls) +
  WORLD PRIMITIVE "deceptive domain" (a fitness-driven control at
  matched budget FAILS where novelty succeeds).
- fit: GAP for a deceptive world; the archive is H3's object
  (Archaeon's retention harness already holds behavioural-grid
  policies).
- Ludus next: a world whose behaviour descriptor is computed from a
  RUN (endpoint), plus the degeneracy check as an instrument. Ties to
  openended.novelty.v0 below.

## spatial_stateful

agi.mc.aixi.ctw.v0
- contributes: QUALIFICATION INSTRUMENT (random-policy and optimal-
  policy scores per environment for normalisation) -- the bench's
  solve()/optimal_actions() already supply this for LOOM/WEIR/TITHE
  and the arena supplies it for TTT/Nim.
- fit: EXISTS (normalisation baselines); EXTERNAL for the agent
  (reference MC-AIXI-CTW backend via Herakles); GAP for a step
  interface across thousands of cycles inside one spec
  (EXPANSION_REQUESTS #29).
- Ludus next: expose (random, optimal) baseline scores as a standard
  field of every W7 world.

artificial_curiosity.v0, curiosity.v0, intrinsic.v0 (three entries)
- contributes: WORLD PRIMITIVE "irreducibly stochastic region beside a
  learnable region" (the noisy-television trap; required, not
  decoration) and "three regions of differing learnability".
- fit: GAP; no existing world has a designed unlearnable region; the
  arena's CHANCE mover is the mechanism to build one.
- Ludus next: a small grid world with declared learnability regions
  (learnable / hard-learnable / noise) is a generated family with one
  primitive knob; the learner side is C-4.

empowerment.v0
- contributes: QUALIFICATION INSTRUMENT candidate (channel capacity
  from actions to future state, evaluated at many states) as a WORLD
  STATISTIC: a world that is fully controllable everywhere has no
  landscape and is degenerate for control questions. Needs a
  permutation null (feedback_mi_bias).
- fit: GAP (a resettable simulator with re-roll from identical state
  exists in the arena's seeded replay; the estimator does not).
- Ludus next: a candidate instrument for question 1 of the charter
  ("what does this environment reward") on action-interface worlds;
  build only with its permutation null.

l2s.dagger.v0
- contributes: WORLD PRIMITIVE "queryable expert oracle" + the
  covariate-shift horizon knob.
- fit: EXISTS partly (the arena's optimal players are queryable
  experts for TTT/Nim); GAP for per-step state/action emission as a
  fossil.
- Ludus next: none standalone; the expert-oracle capability is a
  field on the interface (P1) when migration happens.

machineevol.neat.v0
- contributes: WORLD (cart-pole / pole balancing, a stepped control
  task with real dynamics) -- no such code exists in the repo.
- fit: GAP; a continuous-state world under the arena interface would
  be a new cell (continuous state topology).
- Ludus next: candidate world for the "continuous state" cell once
  the grammar names it empty; INSPIRATION until then.

openended.novelty.v0
- contributes: WORLD (2-D maze with range sensors, fixed start, step
  limit; endpoint as descriptor) + QUALIFICATION INSTRUMENT (the
  endpoint-cloud degeneracy check with sqrt(steps) null).
- fit: GAP; the crosswalk names ludus/ as the home.
- Ludus next: the cheapest deceptive domain to build; pairs with the
  novelty entries above. Candidate for the second vertical slice.

## Tally

- WORLD: machineevol.neat (cart-pole), openended.novelty (maze).
- WORLD GENERATOR: poet, mcc.bipartite, coevolution.parasites.
- FITNESS FUNCTION: novelty (x2), poet (transfer contrast), mcc
  (minimal criterion), coevolution.parasites (interaction rule).
- CURRICULUM OPERATOR: poet (minimal-criterion admission),
  hide_and_seek (opponent-as-curriculum), mcc.
- WORLD PRIMITIVE: maml (shared structure), curiosity x3 (learnability
  regions / noise region), l2s.dagger (expert oracle), novelty
  (deceptive domain).
- QUALIFICATION INSTRUMENT: empowerment (with null), novelty
  degeneracy check, aixi (random/optimal normalisation),
  coevolution.parasites (held-out set).
- INSPIRATION only: hide_and_seek at current scale.

Nothing here is admitted to the bench by this document.
