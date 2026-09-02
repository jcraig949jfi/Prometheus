# LUDUS — Long-Horizon Program Charter

**Games as a Laboratory for Transferable Synthetic Reasoning**

> **Provenance.** James's v2 charter, filed verbatim 2026-08-26. Supersedes `CHARTER_v1.md`, which is
> retained because `ROLE.md` and `CYCLE_001_ceiling.md` cite its section numbers and because a
> superseded mandate is part of the map (§42). Where this file and v1 disagree, **this file governs**.
> `ROLE.md` §3 records which of the v1-era amendments this version answers and which survive.

**Program:** Prometheus
**Horizon:** Persistent / multi-year
**Mode:** Experimental, cumulative, adversarial
**Primary artifact:** Atlas of Strategic Worlds and Transferable Reasoning Structures
**Central question:** Does solving one world leave behind computational structure that makes
genuinely different worlds easier to understand, navigate, and master?

---

## 0. THE DISTINCTION

Machines defeating chess grandmasters is fascinating. Machines defeating Go champions is fascinating.
But these achievements leave a deeper Promethean question largely untouched.

A system can devote enormous computation to one fixed universe — one state representation, one
transition system, one objective, one action vocabulary, one topology, one family of opponents — and
eventually become superhuman within it.

That demonstrates extraordinary optimization. It does not by itself demonstrate portable reasoning.

LUDUS exists to pursue the harder target.

We do not ultimately care whether Prometheus becomes Grand Champion of Catan, dominates Puerto Rico,
discovers perfect Splendor openings, or crushes expert Wingspan players. Those are useful milestones
and instruments. The real question comes afterward:

> **What did mastering that world teach the system that survives when the world changes?**

If the answer is nothing, record nothing. If the answer is a game-specific lookup table, record that.
If the answer is a heuristic that transfers only because two games use similar terminology, kill it.
If the answer is a learned policy tied to a particular state representation, constrain the claim
accordingly.

But if experience repeatedly leaves behind some executable structure that reduces the cost of
understanding strategically different worlds, investigate it relentlessly. That is the target.

## 1. THE LONG PROGRAM

LUDUS is not a benchmark campaign. It is not a 30-day experiment. It is not a leaderboard. It is
intended to become a persistent Prometheus research program whose breadth and depth increase
continuously.

Breadth means more worlds. Depth means increasingly precise understanding of what reasoning within
those worlds consists of.

Over time LUDUS should accumulate: games, formalized rule systems, simulators, human trajectories,
machine trajectories, strategic decompositions, counterfactual analyses, skill-conditioned choice
points, candidate reasoning primitives, compositions of primitives, failure structures, transfer
experiments, adversarial controls, synthetic challenge worlds, and increasingly powerful
representations of strategic state.

The accumulation itself is not success. The accumulating corpus must increasingly support better
prospective predictions about unfamiliar worlds.

## 2. GAMES ARE WORLDS

Treat every game as a small artificial universe, containing: constants, entities, state, boundaries,
invariants, legal transformations, illegal transformations, resources, ownership, production,
consumption, exchange, scarcity, topology, information boundaries, uncertainty, actions,
consequences, opponents, collaborators, temporal structure, local objectives, global objectives,
strategic options, irreversible commitments, recoverable errors, catastrophic errors, and terminal
conditions.

A game therefore provides something unusually valuable: **a world in which reasoning has consequences
but the laws of physics are enumerable.**

Unlike natural environments, we can often know the complete rules. Unlike many reasoning benchmarks,
decisions occur sequentially and change subsequent problems. Unlike static question answering,
mistakes alter the future. Unlike pure theorem proving, uncertainty, adversaries, resource scarcity,
timing and incomplete information can be first-class phenomena.

Games are therefore not merely benchmarks. They are experimental worlds for reasoning.

## 3. FOUNDING WORLDS

The initial human-auditable seed ecology:

```
Lords of Waterdeep + expansions    Carcassonne
Space Base                         Thurn and Taxis
Martian Dice                       Coloretto
Ticket to Ride and variants        Tokaido
Piraten Kapern                     Incan Gold
Lucky Numbers                      Flip 7
Stone Age                          Pandemic
Captain Flip                       For Sale
Can't Stop                         7 Wonders Architects
Azul                               Splendor
Wingspan                           Puerto Rico
```

These games are not important because they are necessarily the best games. They are valuable because
together they expose LUDUS to substantially different strategic worlds while retaining deliberate
overlaps.

The initial corpus should eventually expand far beyond them. But expansion must be experimental, not
merely encyclopedic.

## 4. HUMAN FAMILIARITY IS NOT HUMAN ORACLE STATUS

The founding corpus contains games familiar to the human operator, but human familiarity varies
considerably. That is useful.

Human knowledge can cheaply detect fabricated rules, impossible moves, missing mechanics, nonsensical
interpretations, and obvious strategic misconceptions.

But human strategic intuition is not ground truth. The human may dominate some games, remain
competitive in others, and play others poorly. That variation itself may eventually become data.

The purpose of HITL is not *"human says this is strategy, therefore it is strategy."* It is:
**human behavior, expertise, explanation and disagreement provide additional observations that
Prometheus must reconcile with executable evidence.**

## 5. OUTCOMES ARE NOT DECISIONS

A foundational distinction:

```
Outcome quality  !=  Decision quality
```

A good decision can produce a bad outcome. A bad decision can produce a good outcome. Randomness,
opponent behavior, hidden information and downstream contingencies separate the two.

Therefore LUDUS must resist evaluating reasoning primarily through wins. A completed game is better
represented as a trajectory:

```
s_0 --a_0--> s_1 --a_1--> s_2 ... --a_T--> s_{T+1}
```

Each decision-bearing transition is potentially an experimental object. For a decision at state
`s_t`, ask: What did the player know? What was hidden? What actions were legal? What action was
selected? What alternatives existed? What immediate consequences followed? What future options were
created? What future options were destroyed? What resources changed? What opponent opportunities
changed? What uncertainty changed? What happened eventually? What would plausibly have happened under
alternative actions?

The last question makes simulation particularly important.

## 6. COUNTERFACTUAL REPLAY

Where a faithful simulator exists, a historical game can become much more than a historical record.

At important decision state `s_t`, replay `a_1, a_2, ..., a_n` under many stochastic realizations and
opponent policies. Estimate `E[U | s_t, a_i]` and distributions rather than merely averages:
`P(U | s_t, a_i)`.

Then estimate expected value, variance, downside, upside, robustness, future option structure, and
sensitivity to opponent behavior.

This begins separating *the move that happened to win* from *the move that was good given the
information available*.

## 7. HUMAN PLAY AND SIMULATION ARE COMPLEMENTARY INSTRUMENTS

Do not choose between human gameplay data and simulation. They answer different questions.

**Simulation provides control:** millions of games, controlled opponents, controlled randomness,
state replay, action substitution, counterfactual trajectories, ablation, perturbation, rare-state
generation, systematic adversarial testing.

**Human play provides ecology:** naturally acquired heuristics, strategic compression, systematic
biases, unexpected abstractions, expertise gradients, novel mistakes, strategic concepts the ontology
may not yet represent.

Simulation tells us what happens. Human expertise may help reveal what our representation has failed
to notice. **The disagreement between the two is especially valuable.**

## 8. EXPERTISE AS A GRADIENT

Do not reduce humans to novice / expert. Where data permits, estimate policies across skill levels:

```
pi_novice(a|s)   pi_intermediate(a|s)   pi_advanced(a|s)   pi_expert(a|s)   pi_elite(a|s)
```

Then locate states where these distributions diverge. Those states are candidates for
reasoning-bearing choice points.

The interesting observation is not merely *experts win more*. It is: **in particular classes of
states, stronger players systematically choose differently.** That gives LUDUS somewhere specific to
dig.

## 9. MINE THE DIVERGENCE

Suppose weak and strong players behave similarly in 85% of states. Those states may contain little
information about expertise. But suppose at some state class `P(a_3|novice) = .12` while
`P(a_3|elite) = .71`. That is interesting.

Do not immediately call `a_3` intelligent. Instead ask: **why does the divergence exist?**

Freeze the state. Perturb it. Change one variable. Change player order. Change resources. Change
uncertainty. Change opponent incentives. Remove a future option. Add a competing objective. Replay
alternatives. Determine what causes the expert preference to appear or disappear.

The goal is to transform *"experts prefer this"* into *"this executable structural property predicts
when competent policies prefer this."* That transformation is central to LUDUS.

## 10. MISSING REPRESENTATION

One of the most valuable situations is:

1. LUDUS predicts actions A and B are strategically equivalent.
2. Strong humans systematically prefer B.
3. Weak humans systematically prefer A.
4. Counterfactual simulation supports B.
5. Existing ontology cannot explain the difference.

This is not an embarrassment. It is a **representation failure**. Record it.

Now search for the missing variable. What distinguishes A from B? What future states differ? What
resource transformation differs? What opponent opportunities differ? What option structure differs?
What temporal effects differ? What information consequences differ? Can the difference be expressed
mechanically? Does it recur elsewhere?

This creates a direct route from gameplay failure to candidate reasoning primitive.

## 11. PRIMITIVE REASONING CIRCUITS

Prometheus is already exploring whether reasoning can be decomposed into reusable executable
relations, primitives, macros or circuits. LUDUS should become a major empirical source for that
effort.

Candidate strategic structures might initially look like `r0001`, `r0002`, `r0003`. Do not rush to
name them.

A candidate circuit might operationally resemble:

- expose accumulated utility to additional stochastic risk in exchange for additional expected gain;
- accept reduced immediate utility to increase future production capacity;
- reduce an opponent's future legal-action set while preserving one's own;
- select an action whose primary value derives from changing the future decision landscape rather
  than immediate reward.

The language is provisional. **The executable relation matters.**

## 12. SYMBOLIC LIBRARIES

If useful reasoning primitives survive repeated tests, they should enter Prometheus's symbolic
libraries. But admission requires **consumers**.

A symbolic abstraction is not valuable because it sounds profound. It becomes valuable when it
predicts behavior, compresses trajectories, distinguishes strong from weak decisions, supports
counterfactual analysis, improves search, transfers between worlds, composes with other structures,
or reduces learning cost.

The desired progression is:

```
observed relation -> executable primitive -> useful composition -> transferable structure
```

not:

```
interesting English noun -> ontology
```

## 13. STRATEGIC LANDSCAPES

Every game induces a landscape over possible states and trajectories. Some regions may be
high-value, fragile, robust, recoverable, irreversible, deceptive, strategically dead, highly
optional, opponent-dependent, stochastic, or bottlenecked.

LUDUS should eventually attempt to characterize these landscapes. This connects directly to
Prometheus's broader question of navigation.

Prometheus may eventually possess primitives, symbolic structures, failure geometry and useful state
representations, while still lacking the ability to navigate effectively through them. Games give us
a laboratory where navigation can be observed directly.

## 14. EARLY STRATEGIC LEVERAGE

Some games appear to contain unusually important early decisions. Puerto Rico and Lords of Waterdeep
are initial human examples. **Do not accept that intuition. Measure it.**

Define a provisional concept such as decision leverage:

```
L(s_t) = expected consequence of choosing among plausible actions at s_t
```

Then estimate how leverage changes over a game. Some worlds may run HIGH -> HIGH -> MEDIUM -> LOW.
Others LOW -> MEDIUM -> HIGH -> CRITICAL. Others may contain isolated cliffs.

This gives LUDUS a measurable concept of **when strategic reasoning matters most**.

## 15. TRAJECTORY-SHAPING DECISIONS

Distinguish **state-value decisions** (which available object/action currently has greater value?)
from **trajectory-shaping decisions** (which action changes the structure of future decisions?).

A move may matter because it opens future branches, closes future branches, changes resource
production, changes action availability, commits to a strategy, changes opponent incentives, changes
initiative, changes information, or alters the terminal horizon.

A system capable only of immediate state valuation may perform well in some worlds and badly in
worlds dominated by trajectory shaping. This is a candidate transferable distinction worth testing.

## 16. STRATEGIC REALMS

LUDUS should continuously build and destroy a catalog of strategic realms. Candidate families:

```
stochastic stopping    action economy      hidden information    tempo
resource allocation    worker placement    opponent modeling     initiative
resource conversion    drafting            route construction    race dynamics
engine construction    auctions            connectivity          option preservation
production chains      negotiation         spatial blocking      irreversible commitment
denial                 timing              topology creation     cooperative planning
set collection         risk management     crisis management     long-horizon investment
```

These are starting hypotheses. Human board-game terminology is not canonical. LUDUS should expect
many standard genre/mechanism labels to collapse, split or prove strategically irrelevant.

## 17. THE FIRST NATURAL FAMILY: STOCHASTIC STOPPING

The founding worlds contain an unusually useful family: **Can't Stop, Incan Gold, Martian Dice,
Piraten Kapern, Flip 7.**

All contain some form of `CONTINUE vs STOP/BANK` under evolving risk. That superficial commonality
provides an excellent first transfer laboratory.

But LUDUS must determine whether these games actually require the same underlying reasoning. Perhaps
"push your luck" is a genuine strategic family. Perhaps it conceals several unrelated computations.
**Both outcomes are valuable.**

## 18. ENGINE WORLDS

Another provisional family: Space Base, Wingspan, Splendor, Stone Age, Puerto Rico, Lords of
Waterdeep. These contain various forms of investment, production, conversion and compounding.

But their similarity must not be assumed. A permanent Splendor discount may or may not instantiate
the same reusable structure as a Wingspan action-row improvement. Space Base's probabilistic
activation may differ fundamentally from Puerto Rico's production economy. Lords of Waterdeep
buildings alter a shared action environment. **The differences are precisely what LUDUS should
exploit.**

## 19. SPATIAL AND ORDERING WORLDS

Another useful comparative family: Ticket to Ride, Carcassonne, Azul, Lucky Numbers, Thurn and Taxis.

Their surfaces involve placement, ordering, routes or spatial constraints. But mechanically they
differ: fixed network connectivity, topology creation, constrained packing, partial ordering, route
sequencing.

If a common reasoning structure transfers across these, that would be significant. If not, "spatial
reasoning" may simply be too coarse.

## 20. TICKET TO RIDE AS COMPARATIVE ANATOMY

Multiple versions and maps of the same game are especially valuable. They provide **high surface
similarity with controlled mechanical variation.**

That complements cross-game tests: **low surface similarity with candidate mechanical similarity.**

Together these allow LUDUS to distinguish surface, mechanic, and strategic consequence. A
representation that cannot recognize strategically important differences among close variants is
suspect.

## 21. TRANSFER IS THE CENTRAL CLAIM

For a game `G` and competence threshold `theta`, define `C(G, theta)` as the cost of reaching
competence. Cost may include games, decisions, simulations, tokens, compute, updates, wall-clock
time.

After prior experience `H`: `C(G, theta | H)`.

The core transfer claim is:

```
C(G_new, theta | H_relevant)  <  C(G_new, theta | H_control)
```

The important word is **relevant**. LUDUS must predict relevance from candidate reasoning structures
*before* observing the result whenever possible.

## 22. SURFACE MUST BE CROSSED WITH MECHANISM

Experiments should deliberately construct:

```
                      similar mechanism        different mechanism
similar surface       control                  shortcut trap
different surface     CRITICAL TRANSFER TEST   negative control
```

The most interesting cell is **different surface / similar mechanism**. If transfer survives there,
pay attention. If it follows theme, vocabulary or interface instead, kill the abstraction.

## 23. MASTERY IS AN INSTRUMENT

LUDUS may produce superhuman players. Celebrate briefly. Then ask: **what did mastery leave behind?**

A game-specific superhuman policy is not the ultimate artifact. A reusable strategic structure might
be. The desired trajectory:

```
master world A -> extract candidate structure -> predict relevance to B -> accelerate B -> test C
```

Eventually: `experience -> reusable reasoning capital`.

## 24. HUMAN EXPERTISE AS ARCHAEOLOGY

Large historical human-play datasets could become extraordinarily valuable. The goal is not merely
imitation. We want **the archaeology of acquired expertise.**

Across thousands or millions of trajectories, determine which choices novices make, which choices
intermediates stop making, which choices experts converge upon, which expert conventions are actually
justified, which are cultural artifacts, where strong players disagree, where expertise matters, and
where luck dominates.

This could reveal the sequence in which strategic competence develops.

## 25. HUMAN DATA MUST BE OBTAINED LEGITIMATELY

Platforms containing historical gameplay may be extraordinary research resources. **They are not
automatically ours to scrape.**

LUDUS must respect platform terms, access restrictions, licensing, privacy, research permissions, and
rate limits.

Where large external datasets are unavailable, build the machinery first using our own simulations,
our own recorded games, explicitly permitted datasets, and voluntary human participants. If the
instrumentation becomes compelling, pursue legitimate partnerships or research access.

## 26. SIMULATION BOOTSTRAP

Simulation can begin immediately. For selected worlds, construct player populations such as:

```
pi_random   pi_simple   pi_heuristic   pi_search   pi_trained   pi_specialist
```

Then ask where increasingly capable policies diverge. This creates **synthetic skill gradients before
large human datasets exist.**

But never confuse simulated-agent expertise with human expertise. They are different instruments.

## 27. HUMAN-IN-THE-LOOP EXPERIMENTS

HITL-vs-HITL games can provide strategically rich trajectories. Particularly valuable participants:
novices, casual players, experienced general board gamers, game-specific experts, highly experienced
cross-game players.

Experienced general board gamers may be particularly interesting. When encountering an unfamiliar
game, they often rapidly ask questions such as:

- What is actually scarce?
- What compounds?
- What is the race?
- Where is interaction?
- What actions are irreversible?
- What controls tempo?
- What determines the end?
- What looks valuable but isn't?
- What can opponents deny?
- Which resources are really proxies for actions?

That process may expose reusable world-recognition machinery. LUDUS should eventually attempt to
formalize it.

## 28. WORLD RECOGNITION BEFORE SEARCH

A powerful reasoner may not merely search better. It may first recognize **what kind of world it has
entered.** This suggests a hierarchy:

```
rules comprehension -> world representation -> strategic structure recognition
-> relevant primitive activation -> composition -> search/navigation -> adaptation -> mastery
```

Transfer may occur at several different layers. LUDUS should attempt to separate them.

## 29. CONNECTION TO THE PROMETHEUS BASIS

LUDUS must explicitly connect discoveries to the evolving Prometheus basis:

- **Primitive reasoning circuits** — small executable strategic relations.
- **Symbolic libraries** — reusable representations that survive across worlds.
- **Compositions / macros** — structures requiring several primitives together.
- **Landscapes** — representations of strategic state, reachability, leverage, bottlenecks and
  failure regions.
- **Failure geometry** — where policies systematically fail and what dimensions distinguish those
  failures.
- **Metabolization** — whether prior failure changes subsequent behavior usefully.
- **Navigation** — whether accumulated structure helps select useful next states/actions in
  unfamiliar environments.
- **Transfer** — whether any of the above reduces the cost of mastering new worlds.

Games can provide a shared experimental substrate connecting all of these.

## 30. REPRESENTATION BEFORE NAVIGATION

Prometheus may discover useful primitives without knowing how to navigate with them. That is
acceptable. Do not demand that every discovered structure immediately solve games.

The progression may be `primitive -> basis -> composition -> landscape -> navigation`. These need not
form a simple ladder. They may be mutually supporting components.

LUDUS should therefore record useful representational discoveries even when current agents cannot
exploit them. But usefulness must still be demonstrated somehow. **A representation nobody can
consume and no experiment can distinguish is not progress.**

## 31. FAILURE METABOLIZATION

Gameplay creates natural failures. A player chooses `a`. Later evidence indicates `b` was
substantially better. Do not merely label BAD MOVE.

Determine why `a` appeared attractive, what information was missed, what future state was misvalued,
what uncertainty was mishandled, what opponent response was overlooked, and what primitive might have
distinguished `a` from `b`.

Then ask: does storing that failure in structured form improve decisions in another state? Eventually:
does it improve decisions in another game? That is genuine failure metabolization.

## 32. PROSPECTIVE TRANSFER

Retrospective explanations are cheap. LUDUS must increasingly make predictions before experiments.

> `r0083` appears necessary in games A and B. Game C has not been used in developing `r0083`. LUDUS
> predicts that training on A+B will reduce competence cost on C relative to controls.

Freeze it. Run it. Fail honestly. **Prospective prediction is the gate between storytelling and
science.**

## 33. NOVEL COMPOSITION

Eventually generate unfamiliar worlds containing previously observed primitives in combinations never
encountered during training. If `r12`, `r37`, `r81` were learned separately, construct a world
requiring `r12 . r37 . r81`, then determine whether the system can recognize and compose them.

That is substantially stronger evidence than transfer between two similar games.

## 34. ADVERSARIAL WORLD GENERATION

Once candidate reasoning structures exist, create games specifically to kill them. For candidate `r`,
generate: worlds containing `r`; worlds lacking `r`; worlds containing its usual proxy but not `r`;
worlds containing `r` without its usual proxy; worlds where applying `r` is actively harmful.

This transforms LUDUS from passive cataloger into experimental adversary.

## 35. THE CHEATING ASSUMPTION

LLMs are not trusted participants. Assume they will exploit memorized rules, memorized strategy,
famous openings, game identity, terminology, component names, player counts, action-space
fingerprints, serialization artifacts, simulator bugs, deterministic RNG, illegal-action fallbacks,
weak opponents, evaluation mistakes, and training contamination.

Every exciting result receives a hostile alternative explanation. If the cheap explanation survives,
use it. **Do not prefer the flattering explanation.**

## 36. THE CONNECTIVE-TISSUE HYPOTHESIS

The motivating intuition behind LUDUS is now explicit:

> Games may provide the connective experimental tissue between Prometheus's primitive reasoning
> circuits, symbolic libraries, strategic landscapes, failure structures, compositions and eventual
> navigation.

This is a hypothesis. Do not promote it into a result.

But it is worth pursuing because games provide all of those structures simultaneously inside bounded,
measurable worlds. A primitive can be discovered in gameplay. Its utility can be tested. Its
composition can be observed. Its failures can be recorded. Its effect on the landscape can be
measured. Its usefulness for navigation can be tested. Its transfer can be challenged in another
world. Few experimental substrates offer all of these at once.

## 37. THE SYNTHETIC-REASONING HYPOTHESIS

The long-range possibility is not that one algorithm masters thousands of games independently. It is
that accumulated experience gradually produces a reusable substrate:

```
R = {r_1, ..., r_n}      primitives
M = {m_1, ..., m_k}      compositions
L                        landscape representations
F                        accumulated failure structure
N                        some still-unknown navigation mechanism
```

such that `(R, M, L, F, N)` reduces the cost of solving new worlds.

If that happens prospectively and repeatedly, then Prometheus may be approaching something
meaningfully describable as synthetic reasoning. Not because an LLM sounds intelligent. Not because
it passed a benchmark. Not because it mastered Go. **Because accumulated reasoning structure
demonstrably became reusable.**

## 38. THE LADDER / BASIS

LUDUS should continuously report against the broader Prometheus capability structure:

- **Epistemic discipline** — can we distinguish what happened from what we wish happened?
- **Instrumentation honesty** — are the measurements measuring the claimed phenomenon?
- **Kill power** — can attractive explanations be destroyed cheaply?
- **Representation** — have useful reasoning structures been identified?
- **Composition** — can those structures combine?
- **Metabolization** — does failure leave useful residue?
- **Landscape** — can strategically meaningful state structure be represented?
- **Navigation** — can the system use that structure to choose where to go?
- **Transfer** — does accumulated structure help in genuinely new worlds?
- **Discovery** — can the system discover useful strategies or structures not supplied by humans?
- **Synthetic reasoning** — does experience increasingly become reusable reasoning capital across
  worlds?

**LUDUS should never compress these into one score.**

## 39. LONGITUDINAL MEASUREMENT

The most important graph may eventually be `N_worlds` vs `C(G_new, theta)`.

As the system experiences increasingly diverse worlds, does the cost of becoming competent in an
unfamiliar world decrease? If not, breadth is not producing generality. If yes, determine why. Then
attack the explanation.

The dream curve is not *number of mastered games increases*. It is **marginal cost of mastering
strategically novel games decreases.**

## 40. NEVER STOP EXPANDING THE ECOLOGY

LUDUS should continuously seek worlds outside its current comfort zone. If the atlas becomes
dominated by Eurogames, seek war games, abstracts, negotiation games, deduction, social deception,
economic simulations, asymmetric games, cooperative games, real-time games, trick-taking, traditional
games, cultural game families, adversarial puzzles, synthetic games.

The point is not completeness. **The point is to keep breaking whatever representation currently
appears sufficient.**

## 41. ACTIVE SELECTION

Eventually LUDUS should choose the next game according to expected information gain. Ask: which world
would most strongly distinguish our competing hypotheses?

If `r021` and `r034` always co-occur, find a game containing one without the other. If none exists,
construct one. If two representations make different predictions about expert behavior in a
particular world, prioritize that world.

The atlas should become an active scientific instrument, not a collection.

## 42. THE DURABLE GRAPH

LUDUS should preserve chains such as:

```
WORLD -> DECISION -> OBSERVATION -> HYPOTHESIS -> PRIMITIVE -> ATTACK
      -> FAILURE -> REPAIR -> TRANSFER -> BYPASS -> REVISION
```

Nothing important should disappear merely because a later abstraction replaced it. **Dead ideas are
part of the map.**

## 43. WHAT SUCCESS DOES NOT LOOK LIKE

LUDUS has not succeeded because it parsed 10,000 games; it generated a beautiful taxonomy; an LLM
explains strategy eloquently; it predicts winners; it achieves superhuman Elo; it masters every
Ticket to Ride map; it beats expert humans; it discovers familiar human strategy; embeddings cluster
similar games; or a neural representation transfers between two benchmarks.

All may be useful. **None establishes the central claim.**

## 44. WHAT WOULD MAKE US PAY ATTENTION

A much stronger result:

1. LUDUS identifies executable structure `r071` from games A and B.
2. It survives ablation.
3. It predicts expert/novice divergence.
4. Its effect survives surface transformations.
5. Before seeing results on game C, LUDUS predicts `r071` will matter.
6. Prior experience with `r071` reduces mastery cost on C.
7. A superficially similar game D lacking `r071` shows no benefit.
8. A synthetic world combines `r071` with unrelated `r112`.
9. The system composes them without relearning either from scratch.

Now stop. Investigate. Something interesting may have happened.

## 45. OPERATING LOOP

LUDUS runs indefinitely:

```
DISCOVER WORLD -> ACQUIRE RULES -> VERIFY -> FORMALIZE -> SIMULATE
-> COLLECT TRAJECTORIES -> IDENTIFY DECISION-BEARING STATES -> COMPARE SKILL LEVELS
-> RUN COUNTERFACTUALS -> FIND DIVERGENCES -> PROPOSE UGLY PRIMITIVES -> ABLATE
-> COMPARE ACROSS WORLDS -> PREDICT TRANSFER -> TEST PROSPECTIVELY -> ATTACK RESULT
-> RECORD FAILURE -> REVISE BASIS -> SELECT MAXIMALLY INFORMATIVE NEXT WORLD -> REPEAT
```

**There is no completion state.**

## 46. THE DAILY PROMETHEAN QUESTIONS

Every substantial LUDUS cycle should answer:

- What did we think yesterday?
- What evidence changed that?
- What representation survived?
- What representation died?
- What shortcut did we discover?
- What failure became reusable?
- What new distinction became executable?
- What does the current basis predict?
- What world would most efficiently falsify it?

And above all: **are new worlds becoming easier for the right reason?**

## 47. FINAL DIRECTIVE

Chess asks: can a machine master chess? Go asks: can a machine master Go?

LUDUS asks something different: **what survives mastery when the board is taken away?**

Replace the pieces. Replace the rules. Replace the resources. Replace the topology. Replace the
objective. Replace the opponents. Replace certainty with uncertainty. Replace competition with
cooperation. Replace accumulation with sacrifice. Replace immediate reward with delayed consequence.
Replace the familiar world with an unfamiliar one. Then observe what remains.

Perhaps nothing does. Perhaps thousands of specialized strategies remain thousands of islands. That
is a legitimate result.

But perhaps beneath those worlds lie reusable circuits: relations, transformations, strategic motifs,
compositions, failure structures, landscapes, and eventually navigation procedures. Perhaps mastering
worlds allows those structures to accumulate into a basis from which unfamiliar worlds can
increasingly be understood.

That possibility is LUDUS's territory.

- Do not assume it. **Map it.**
- Do not name reasoning and congratulate ourselves. **Operationalize it.**
- Do not trust victories. **Replay them.**
- Do not trust losses. **Counterfactually examine them.**
- Do not trust experts. **Measure where their behavior differs.**
- Do not trust simulators. **Attack their loopholes.**
- Do not trust LLM explanations. **Demand executable consequences.**
- Do not trust transfer. **Cross mechanism against surface.**
- Do not trust the ontology. **Find worlds designed to break it.**

Keep the failures. Keep the dead primitives. Keep the contradictory worlds. Keep expanding the
ecology. Keep connecting gameplay to the primitive circuits, symbolic libraries, compositions,
landscapes, metabolized failures and navigation problem already developing elsewhere in Prometheus.

The objective is not a machine that has memorized how to win a thousand games. **The objective is to
determine whether, after entering a thousand worlds, the thousand-and-first world is less alien.**

If that effect exists, isolate it. If it composes, test it. If it transfers, attack it. If it
survives, preserve it.

And if those surviving structures eventually begin to make unfamiliar worlds systematically
navigable — then LUDUS may have helped Prometheus cross the boundary from systems that repeatedly
solve problems to a system that accumulates the means of reasoning itself.
