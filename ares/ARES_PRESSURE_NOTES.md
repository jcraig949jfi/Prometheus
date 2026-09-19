# ARES_PRESSURE_NOTES -- abstract pressures extracted from biology (cycle 0)

Currency: 2026-09-19. Ares, initial cycle, Phase 1. Timeboxed: this
pass exists to generate executable toys, not to be complete.

## Reading rules for this file

- Every entry is a PRESSURE PATTERN, not a biological story. The
  biological phenomenon is named only so the abstraction can be
  checked against it.
- Source words follow the library convention Aphrodite uses:
  VERIFIED (read the primary source this cycle), PARTIAL, SECONDARY,
  FROM MEMORY (a remembered author/year; not checked this cycle; may
  be misattributed), NOT FOUND. Nothing in this cycle was checked
  against a primary source, so every citation below is FROM MEMORY.
  No DOI is given because none was verified; a remembered DOI is
  worse than none.
- Each entry carries the six fields the charter asks for:
  phenomenon; abstract pressure; why it might create machinery;
  minimum toy; obvious confound; falsifier. The falsifier is the
  result that would show the pressure is NOT a useful accelerator.
- The machine-readable form is PRESSURE_CATALOG.json beside this file.

## The framing that drives the toys

Fitness in the toys is always plain world reward. A pressure is
"useful" only if it changes what KIND of machinery selection finds,
against three controls: the pressure ABSENT (same world, the pressure's
defining feature neutralised), the pressure SHUFFLED (the feature is
present but decoupled from anything the organism could observe, so the
same variance exists with no exploitable structure), and where relevant
ABUNDANT (the resource limit lifted). "Fitness rose under pressure" is
not a result; "the pressure-present champions carry structure X that
absent and shuffled champions do not, and ablating X removes the
behaviour" is.

Two pressures share one machinery hypothesis when the toy that tests
them would look the same; those are merged below rather than
duplicated.

## P01 catastrophic asymmetry (W1)

- Phenomenon: predation, injury, poisoning. A forager makes many
  small errors per day and survives them; one class of error ends the
  lineage. Risk-sensitive foraging theory (Caraco; Stephens & Krebs;
  FROM MEMORY) treats variance in outcome as a fitness quantity in its
  own right, not a nuisance.
- Abstract pressure: the loss distribution has a heavy left tail whose
  events are cued only weakly and whose cost exceeds the sum of all
  ordinary rewards in a lifetime.
- Why machinery: an organism that treats all uncertainty the same
  either abstains everywhere (starves) or acts everywhere (dies). A
  policy that separates "uncertain and cheap" from "uncertain and
  fatal" needs SOME structure that conditions action on the
  catastrophe cue and not on the ordinary cue: a second pathway, a
  gate, a veto.
- Minimum toy: two noisy channels; acting pays +1 when channel A > 0,
  costs -1 otherwise; when a latent danger variable (leaking into
  channel B) is high, acting wipes accumulated reward. No detector is
  given; channel B is just another input.
- Confound: the organism may simply lower its action rate (fixed
  conservatism) and gain most of the benefit; that is not machinery.
  Measure the conditional action rate given the danger cue, not the
  overall rate. A second confound: the penalty size alone (not its
  rarity) drives the result; the ABSENT control keeps the expected
  penalty and removes the tail.
- Falsifier: present, absent and shuffled champions are structurally
  indistinguishable (same op histogram, same ablation profile) and the
  behavioural gap is explained by the overall action rate alone.

## P02 rare override / extreme opportunity asymmetry (W2)

- Phenomenon: mating opportunities, rare rich patches, mast years.
  Sexual selection is used ONLY as the example of a rare event whose
  payoff dwarfs the daily budget and justifies risk that would be
  suicidal otherwise (Zahavi handicap, costly signalling: FROM
  MEMORY; used only as a pressure pattern).
- Abstract pressure: a conservative action dominates almost always; a
  risky action has negative expectation except in rare cued windows
  where its payoff is two orders of magnitude above baseline.
- Why machinery: fixed conservatism forgoes the windfall; fixed
  recklessness dies. Only a CONDITIONAL switch captures both; the
  switch must be keyed to the window cue and robust to its noise.
- Minimum toy: safe action +1; risky action -3 except in rare windows
  (cue channel elevated, noisy) where it pays +200.
- Confound: if windows are frequent enough, always-risky wins by
  expectation and no conditionality is needed; keep windows rare
  enough that always-risky is strictly worse than always-safe.
- Falsifier: champions under present are either fixed-safe or
  fixed-risky by the action-rate-given-cue measure; or the shuffled
  control produces the same conditional structure (then the structure
  is a cue-following reflex, not a risk override).

## P03 nonstationarity within a lifetime (W3)

- Phenomenon: seasons, moving prey, learned foraging; the case for
  learning over inherited policy when the environment changes faster
  than generations (Stephens 1991 on environmental predictability and
  learning; Baldwin effect: FROM MEMORY).
- Abstract pressure: the map from observation to correct action flips
  at unpredictable times inside one lifetime; an inherited fixed map
  is right half the time.
- Why machinery: to be right more than half the time an organism must
  change its own input-output map during life. The substrate offers
  only generic routes to that (recurrent state, leaky nodes, a local
  plasticity rate that starts at zero); which route, if any, is the
  measurement.
- Minimum toy: obs channel x; correct action = sign(x) before the flip,
  -sign(x) after; reward +1/-1; last reward is visible as a channel.
- Confound: the organism can encode "act on sign(x * last_reward)"
  as a single gate with no persistent state at all. That IS
  within-lifetime adaptation of a degenerate kind; the design must
  measure whether the champion's behaviour after a flip depends on
  more than the immediately preceding reward (recovery curve length).
- Falsifier: recovery after the flip is one step long in every
  champion (pure reflex on last reward) and no persistent-state
  usage differs from the absent control.

## P04 hidden state / hidden regime (W4)

- Phenomenon: cryptic predators, hidden patch quality; the organism
  must infer an unobservable variable from history. Partially
  observable decision problems in behavioural ecology (FROM MEMORY).
- Abstract pressure: two regimes produce identical per-step
  observations and demand opposite actions; the only evidence is a
  brief cue early in life (or the reward history).
- Why machinery: with no persistent internal state the organism is
  at chance after the cue passes. Anything above chance late in life
  requires SOMETHING carrying the cue forward: a recurrent loop, a
  leaky node, a plasticity-modified weight, or a behavioural mark
  (an action pattern that re-creates the evidence).
- Minimum toy: regime bit drawn per episode; cue channel shows it for
  the first 3 steps only; thereafter obs is regime-independent noise;
  reward +1 for the regime's action.
- Confound: reward feedback channel leaks the regime every step (the
  organism can re-infer it from last reward). Run W4 WITHOUT the
  reward channel so the cue is the only evidence; that is the point.
- Falsifier: late-life accuracy at chance in every present champion
  (the pressure is simply too hard for this substrate: "makes search
  harder without creating structure"), or the no-persistent-state
  ablation performs identically (the structure is not carrying the
  cue).

## P05 delayed consequence / delayed revelation (W5)

- Phenomenon: caching, seasonal preparation, developmental decisions
  whose payoff is realised much later; credit assignment across delay.
- Abstract pressure: a token early in life determines which of two
  actions pays at a much later step; the interval carries distractor
  input; there is no intermediate reward.
- Why machinery: same as P04 but the delay is long and the interval
  is noisy, so a leaky carrier decays and a reflex is useless; the
  machinery must be robust to the distractor.
- Minimum toy: token at step 2 (channel value +1 or -1); at step T-2
  choose action 1 or 2 matching the token sign for +50; distractor
  noise on the same channel in between.
- Confound: delay length and noise amplitude tune difficulty; the
  ABSENT control has delay 0 (token and choice at the same step).
- Falsifier: no present champion exceeds chance at the choice step.

## P06 resource scarcity (W6)

- Phenomenon: metabolic constraint on brains (the expensive-tissue
  hypothesis, Aiello & Wheeler: FROM MEMORY); small nervous systems
  (C. elegans 302 neurons) solving real problems; compression as a
  selective outcome.
- Abstract pressure: the same task under a tight budget of ticks,
  nodes, and lifetime, versus an abundant budget.
- Why machinery: with abundant compute, a sprawling redundant solution
  is as fit as a compact one; under scarcity only compact, reused,
  composed structure fits. The prediction is that scarcity changes
  the KIND of solution, not merely its performance.
- Minimum toy: W3 (changing rules) with n_max=6, ticks=1, versus
  n_max=24, ticks=4. Both have the same lifetime.
- Confound: scarcity may simply cap performance; a lower fitness with
  identical structural motifs is "harder", not "different". Compare
  motif profiles at matched fitness quantiles.
- Falsifier: scarce champions are subgraphs of abundant champions
  (same motifs, fewer of them) with no motif unique to scarcity.

## P07 incompatible regimes (W7)

- Phenomenon: alternation between environments favouring opposite
  behavioural syndromes (bold/shy; explore/exploit); no fixed
  personality is optimal; phenotypic plasticity as the answer
  (West-Eberhard: FROM MEMORY).
- Abstract pressure: regime A rewards switching among options; regime
  B punishes any deviation from one option heavily; regimes alternate
  in blocks with no regime bit.
- Why machinery: a single fixed bias loses badly in one regime. Two
  behaviours plus something that arbitrates between them is the
  minimal solution; whether the arbitration is a separate structure
  (specialisation + gate) or a single tuned dynamical system is the
  measurement. MoE-ness is NOT scored.
- Minimum toy: three options; regime A: the paying option rotates
  every 4 steps, +2 for hitting it, 0 otherwise; regime B: option 0
  pays +1, others -5; blocks of 20 steps; obs = last reward, last
  action one-hot.
- Confound: the reward signal alone can distinguish regimes in one
  step (a -5 is only possible in B); the toy must keep that, since
  removing all evidence makes the task impossible; the measurement is
  whether the champion's structure has separable parts (ablation
  removes A-competence but not B-competence).
- Falsifier: no champion shows separable ablation profiles; all
  competence degrades uniformly under every node removal.

## P08 transplantation / recombination (W8)

- Phenomenon: horizontal gene transfer, symbiogenesis, gene
  duplication and co-option (Ohno; Margulis: FROM MEMORY); modules
  that survive transfer are the ones with clean interfaces.
- Abstract pressure: subgraphs are periodically cut out of one
  lineage and spliced into another (or into another world's
  population); machinery that only works in its original context is
  destroyed by the move.
- Why machinery: if transplant is frequent, structure whose function
  depends on few external connections has a selective advantage
  over structure tangled with its host. That is a pressure toward
  interface cleanliness without rewarding modularity by name.
- Minimum toy: two populations on two worlds; every k generations a
  random subgraph of each champion is spliced into random members of
  the other population; measure whether transplanted subgraphs are
  retained above the rate of random subgraphs of equal size.
- Confound: transplant of ANY structure may act as a generic macro-
  mutation with benefit unrelated to reuse; the random-subgraph
  control isolates that.
- Falsifier: retention of evolved subgraphs equals retention of
  random subgraphs of equal size and edge count.

## P09 ecological coupling (W9)

- Phenomenon: predator-prey and host-parasite coevolution; the Red
  Queen (Van Valen: FROM MEMORY); coevolution can either ratchet
  complexity or cycle forever.
- Abstract pressure: another evolving population sets part of the
  payoff surface; the surface moves as fast as the other side adapts.
- Why machinery: a static world can be solved by a static reflex; a
  moving opponent can, in principle, favour organisms that model or
  anticipate the opponent. In practice the trivial outcome is a cycle
  of counter-reflexes (Red Queen) with no machinery gain.
- Minimum toy: matching-pennies with memory: population A wins when
  it matches B's choice, B wins when it differs; each sees the other's
  last two choices. Cycle detector: autocorrelation of population
  mean strategy over generations.
- Confound: the Red Queen cycle itself. If the cycle detector fires,
  W9 is recorded as a null for machinery and the POET-style
  world-setter variant (ARES-18) is opened.
- Falsifier: cycle detector fires and coupled champions carry no
  structure absent from static-opponent champions.

## P10 developmental construction (W10)

- Phenomenon: genomes encode developmental programs, not organisms;
  regularity and repeated structure come cheaply from generative
  encodings (Stanley's CPPN / HyperNEAT argument; Lindenmayer
  systems: FROM MEMORY).
- Abstract pressure: the hereditary object is a small set of graph
  rewrite rules applied for a fixed number of developmental steps;
  selection acts on the grown organism.
- Why machinery: repeated or scaled structure that direct encoding
  must discover piece by piece can be found as one rule; conversely
  the rule space may be too coarse. The question is search speed to
  a fitness threshold, not the final fitness.
- Minimum toy: rules of the form (match op -> add child with op2,
  edge weight w, optional back-edge); seed = one node; grow k steps;
  run on W4 or W3; compare generations-to-threshold against direct
  encoding at equal evaluations.
- Confound: the rule space may accidentally encode a good prior for
  the specific world; test on two worlds.
- Falsifier: developmental encoding reaches threshold no faster on
  either world, or reaches it only on the world its rule set was
  tuned by.

## P11 partial irreversibility (W11)

- Phenomenon: metamorphosis, sex determination, irreversible
  developmental commitment, diapause; the value of waiting and of
  sampling before committing (optimal stopping in behavioural
  ecology: FROM MEMORY).
- Abstract pressure: one action locks the organism into option A or
  B for the rest of life; a cheap probe action reveals noisy evidence
  about which is right; committing early yields more steps at the
  chosen payoff.
- Why machinery: the optimal policy accumulates evidence to a
  threshold then commits; that needs an accumulator and a threshold,
  neither given. A reflex commits at step 1 on one noisy sample.
- Minimum toy: obs channel = noisy evidence (+/-0.3 mean, sd 1);
  actions: probe (-0.2), commit A, commit B; after commit +3/step if
  right, -3/step if wrong. ABSENT control: commitment reversible
  (switching allowed at no cost).
- Confound: lifetime length tunes the value of waiting; keep it
  fixed and preregistered.
- Falsifier: present champions commit on the first step with the
  same accuracy as the reversible-control champions; no accumulation
  is observable in the hidden-node trajectories.

## P12 dying lineage / state-dependent risk (W12)

- Phenomenon: bet hedging and the asset-protection principle in
  reverse: when the safe path leads to certain death, variance is
  rational (risk-sensitive foraging under an energy floor; Houston &
  McNamara state-dependent life histories: FROM MEMORY).
- Abstract pressure: an energy store declines each step; the safe
  action cannot keep up; the risky action has negative expectation but
  positive variance; fitness is lifetime length.
- Why machinery: the optimal policy is risky when energy is low and
  safe when high; that is a state-dependent switch keyed to an
  observable (energy) whose value is not explicitly encoded as a
  threshold anywhere.
- Minimum toy: energy channel observed; safe +0.6, decay -1.0 per
  step; risky: 30% +6, 70% -2; death at 0; ABSENT: safe +1.2 (safe
  sustains, risk never rational).
- Confound: a fixed mixed strategy (risky with probability p) can do
  well without state dependence; measure P(risky | energy bin).
- Falsifier: P(risky | energy) is flat in present champions.

## P13 sparse revelation (candidate, no world this cycle)

- Abstract pressure: the structure that matters is visible only in
  rare episodes; most of life is uninformative. Overlaps P05 and P02;
  a separate toy is deferred until those report. CANDIDATE.

## P14 inheritance of consequences (candidate, no world this cycle)

- Abstract pressure: a descendant starts life with its parent's
  end-of-life state (weights after plasticity, or energy). Overlaps
  P03 + P10 (Lamarckian inheritance of plastic change). CANDIDATE;
  needs a decision on whether inherited plastic state is in scope.

## P15 variable volatility (candidate, folded into W7 blocks)

- Abstract pressure: the rate of environmental change itself changes.
  In this cycle it is a parameter of W3/W7 (block length), not a
  separate world. CANDIDATE.

## Additional primitives noticed while writing (not in the charter list)

- P16 COST OF SENSING: observations cost something; the organism can
  choose not to look. Creates pressure toward acting on internal
  estimates. CANDIDATE.
- P17 ASYMMETRIC INFORMATION FLOW between lineages (signals that can
  be faked): the costly-signalling pattern as a pressure on receivers
  to discount cheap signals. CANDIDATE, needs a two-population toy.
- P18 SEASONAL BUDGET RESET: accumulated reward is periodically zeroed
  unless converted; pressure toward timing/anticipation. CANDIDATE.

## What the notes deliberately do not do

- They do not argue that any of these pressures produced human
  reasoning. They record the pattern and the toy.
- They do not name the expected machinery in the toys ("memory",
  "accumulator") as a target; those words appear above only inside
  the WHY field to say what the minimal solution needs, and the
  substrate never receives them.
