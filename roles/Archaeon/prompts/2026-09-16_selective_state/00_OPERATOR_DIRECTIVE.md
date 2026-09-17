# Operator directive (verbatim, chat, 2026-09-16 ~20:10 UTC) -- ARCHAEON: SELECTIVE STATE FORMATION

Received by Archaeon[m2-411504ab] on M2 after the WSE survey v01 review
packet (main da246774f). Wake line was: "Save that off as detailed as
you can, and then do a few iterations of this world building. Do not
stop and ask me to weigh in." followed by the text below.

Authority: the operator's verbatim directive; it extends the
COMPUTATIONAL WORKSPACE ECOLOGY directive of the same day
(roles/Archaeon/prompts/2026-09-16_workspace_ecology/) and is worked in
the same lane (archaeon/wse/). "Do not stop and ask" = run the iteration
loop autonomously; every cycle preregisters before it runs and leaves a
committed record.

----------------------------------------------------------------------

ARCHAEON -- EXPERIMENT DIRECTIVE
SELECTIVE STATE FORMATION

Prometheus working definition:

Intelligence is the efficiency with which experience is converted into transferable competence.

Your task is to build and iterate a world whose economics make selective state formation advantageous and eventually necessary.

Do not implement Mamba, attention, an RNN, a memory system, or any known architecture for the organisms.

Do not reward resemblance to an existing architecture.

We want to know what mechanisms emerge when organisms are forced to solve the underlying problem themselves.

THE PROBLEM

An organism receives a continuing stream of experience.

Some events matter later.

Most events do not.

Some information should be:

* forgotten immediately,
* integrated into an evolving internal state,
* retained exactly,
* replaced when newer evidence arrives,
* combined with other state,
* preserved for a very long time,
* or externalized because computation involving it is unfinished.

The organism cannot afford to remember everything.

It cannot afford to repeatedly reread its full history.

It cannot know in advance exactly what future query will be asked.

Create a world in which organisms therefore face the fundamental problem:

What should I keep, what should I compress, what should I overwrite, and what should I forget?

ECONOMICS

Make information retention and computation costly.

Possible costs include:

* persistent state size,
* number of state variables,
* historical reads,
* memory writes,
* number of computations,
* communication between components,
* latency,
* energy,
* addressable storage,
* reconstruction of discarded information.

Raw task success must not dominate these costs.

A giant organism that remembers the entire stream should lose to a smaller organism that extracts the relevant latent state.

But do not make the bottleneck so severe that the only successful strategy is trivial forgetting.

Find the regime in which selectivity pays.

PRESSURES

Develop tasks containing combinations of at least these pressures:

Remember
A small piece of information becomes relevant after a long delay.

Distract
Large quantities of irrelevant experience intervene.

Update
New evidence changes or invalidates previously useful state.

Forget
Old information becomes actively harmful if retained.

Bind
Several independent entities or variables must be tracked simultaneously.

Compose
Correct behavior requires combining multiple earlier facts into a derived state.

Timescale
Some information matters for 5 steps, some for 500, some for 50,000.

Exact recall
Occasionally an item must be reproduced precisely rather than summarized.

Generalize
Surface symbols, ordering, or world presentation change while the underlying causal rule remains invariant.

Interference
Similar experiences compete for state and can corrupt one another.

Delayed relevance
The organism cannot know immediately whether an observation will matter.

State reversal
A previously correct internal conclusion must be abandoned when evidence changes.

Use combinations of pressures, not isolated toy tasks only.

CRITICAL CONTROL

The world must distinguish:

memorizing history

from

maintaining useful state about history.

Construct adversarial cases where replaying or retaining everything is expensive but possible, so we can measure how much cheaper successful selective state strategies become.

Also construct cases where overcompression fails.

The experiment should expose both boundaries:

* too much memory,
* too much forgetting.

The interesting region is between them.

ORGANISMS

Allow organisms enough primitive machinery to invent multiple strategies.

Do not force a particular topology.

Where technically feasible, allow evolution to vary things such as:

* state dimensionality,
* state lifetime,
* update rules,
* gating,
* decay,
* topology,
* routing,
* multiple state stores,
* local versus global state,
* exact versus lossy storage,
* read/write behavior,
* event-triggered computation,
* recombination of stored state,
* conditional persistence.

Known mechanisms may appear.

That is acceptable.

But they must emerge because they survive the economics, not because we encoded their solution.

WHAT WE ARE SEARCHING FOR

Do not search primarily for the organism with the highest final score.

Search for mechanisms that improve the experience -> competence conversion rate.

A lineage that achieves 70% competence from 500 experiences may be more scientifically valuable than one achieving 95% after 100,000.

Track learning curves.

Track the slope.

Track the cost.

Track transfer.

Especially investigate organisms that show discontinuities such as:

* suddenly needing much less experience,
* retaining competence under larger distractor loads,
* scaling to much longer delays without proportional state growth,
* transferring a learned state strategy to unseen tasks,
* maintaining several independent state variables without interference,
* learning when not to remember.

These are mechanism-harvest candidates.

MEASUREMENTS

At minimum record:

* experience consumed,
* competence on withheld tasks,
* transferable competence on changed worlds,
* persistent state size,
* peak state size,
* memory reads/writes,
* historical accesses,
* compute consumed,
* latency where available,
* survival/fitness,
* learning-curve slope.

Useful derived measures include:

competence gained / experience

transferable competence gained / experience

competence / state size

competence / compute

and especially:

change in learning efficiency across evolutionary generations

We care deeply about organisms that become better at learning, not merely organisms that accumulate more competence.

ABLATIONS

When an interesting organism appears, do not immediately name the mechanism.

Break it.

Remove or constrain individual components.

Freeze its state.

Randomize its update rule.

Reduce state capacity.

Increase distractors.

Increase delay.

Change symbol vocabulary.

Reverse causal relationships.

Move it to another world.

Determine what actually produces the advantage.

The output of Archaeon is not:

"Mamba rediscovered."

The output is something like:

Under pressure combination P, lineage L evolved mechanism M. Removing M destroys its ability to retain task-relevant latent state under distractor load while preserving low memory cost. The effect transfers to unseen task family Q.

That is harvestable.

IMPORTANT FAILURE MODES

Guard against:

* organisms exploiting fixed query timing,
* leaking future relevance into observations,
* memorizing seeds,
* world-specific lookup tables,
* state size hidden inside topology,
* free storage disguised as computation,
* fitness functions that simply reward small organisms,
* trivial tasks solvable without memory,
* tasks where remembering everything is always optimal,
* declaring architecture similarity to be discovery.

Mechanism first.

Analogy second.

ITERATION LOOP

Run this as an exploratory evolutionary program.

1. Build the simplest world that creates a real memory-versus-compression tradeoff.
2. Verify controls.
3. Evolve organisms.
4. Inspect the distribution of strategies, not only the winner.
5. Identify where the current world permits cheap hacks.
6. Modify the economics or pressures.
7. Preserve interesting lineages.
8. Cross them into changed worlds.
9. Ablate promising mechanisms.
10. Feed verified reusable mechanisms back into the broader Prometheus soup.

Do not optimize one benchmark indefinitely.

The world itself should evolve as organisms expose weaknesses in its pressures.

NORTH STAR

The question is not:

Can an organism remember a long sequence?

It is:

Can an organism learn what deserves to become state?

And beyond that:

Can evolution discover mechanisms that let future experience be converted into competence using progressively less memory, computation, and exposure?

Build the world that makes that question unavoidable.

Run it.

Pressure the organisms.

Bring back the mechanisms, the failures, and the evidence.
