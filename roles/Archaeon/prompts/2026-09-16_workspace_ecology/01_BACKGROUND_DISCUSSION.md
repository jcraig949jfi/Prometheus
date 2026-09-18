# Background discussion (verbatim, pasted by the operator beneath the directive, 2026-09-16)

Filed beside 00_OPERATOR_DIRECTIVE.md. This is context the operator
attached, not an order; where it and the directive differ (e.g. the
W-ladder numbering differs between the two), the DIRECTIVE's numbering is
used in every Archaeon artifact.

----------------------------------------------------------------------

James (HITL, Operator):

We want to create pressures in our world for our organisms to evolve a workspace solution to higher order computational problems

ChatGPT:

There is an important distinction: a pressure that selects for memory is not yet a pressure that selects for a workspace.

A one-bit delayed-choice task evolves state. A long calculation can evolve a bigger accumulator. A true workspace becomes advantageous when the organism must maintain multiple named intermediates, manipulate them independently, revisit them, combine them in new orders, and preserve them across unrelated computation.

So I would make this a new pressure family in the SFE ecology: WORKSPACE PRESSURE. The world never says "build a workspace." It merely makes workspace-like organization an increasingly favorable adaptation.

Stage / Environmental pressure / What a primitive solution can do / What eventually becomes advantageous
W0 / Immediate input -> immediate answer / Reactive policy / Nothing persistent
W1 / Relevant information disappears before it is needed / Remember one value / Persistent state
W2 / Several values must be retained simultaneously / Fixed registers / Multiple independent slots
W3 / Which old value is needed is revealed later / Store everything positionally / Addressing / binding
W4 / Several subproblems are active concurrently / Sequentialize awkwardly / Named subgoals / workspace partitioning
W5 / Computation branches and must later return / Recompute from scratch / Save/restore / stack-like behavior
W6 / Intermediate results are used by several downstream branches / Recompute repeatedly / Reusable intermediate objects / caching
W7 / Intermediate objects have different roles/types / Flat memory / Structured representations
W8 / Functions/operators themselves must be stored, selected, and composed / Hard-coded action chains / Higher-order workspace
W9 / Novel dependency graphs appear every episode / Memorized protocols / General workspace algorithm

The really interesting transition is around W3-W6. Before that, evolution can solve the problem with recurrent state or specialized registers. Once the organism has five unfinished subgoals, a shared intermediate needed by three of them, one branch that must be suspended, and a later cue telling it which result to resume, a flat accumulator starts falling apart.

Don't give them a scratchpad

I would expose something much more neutral.

The organism might have access to a small collection of generic operations analogous to:

MAKE, PUT, GET, LINK, COPY, DELETE

But don't call them variables, registers, stacks, memories, or workspace.

They could simply manipulate persistent objects in the world.

For example:

MAKE        -> produces opaque object handle 7
PUT 7 x     -> associates some state with object 7
GET 7       -> retrieves it
LINK 7 12   -> associates two objects
DELETE 7

Evolution must discover what these things are useful for.

Better still, let there be several possible solutions. Organisms could conceivably invent:

* recurrent internal state,
* environmental stigmergy,
* a stack,
* a tape,
* key/value storage,
* graph-like intermediate objects,
* recomputation instead of storage.

Then selection determines where the crossover occurs.

That matters because otherwise we aren't discovering a workspace. We're rediscovering the API we wrote.

The higher-order pressure

Now introduce problems where the computation itself becomes data.

Suppose each episode gives the organism randomly generated operators f,g,h,..., with their identities permuted every episode.

The task isn't merely:

f(g(x))

It gets something more like:

A = h(x)
B = g(A)
hold B
C = f(y)
D = q(C)
now apply the operator that produced A
to the value that produced D
then resume B's branch
combine those results using
the operator referenced by branch 3

Critically:

* operator identities are randomized;
* values are randomized;
* dependency topology is randomized;
* some results are shared;
* some branches are dead ends;
* instructions arrive incrementally;
* the final question isn't known at the beginning.

Now hard-coded computational pipelines become poor adaptations.

The organism needs something resembling:

object A:
    value = ...
    producer = h
    parent = x
object B:
    value = ...
    producer = g
    parent = A
pending_branch_1 = B
pending_branch_2 = D

We never requested that representation.

The ecology demanded it.

Add resource economics

This is where evolution gets especially interesting.

Storage should not be free.

Neither should recomputation.

Give every operation a cost:

fitness = reward - alpha(compute) - beta(storage) - gamma(reads/writes) - delta(latency)

Then vary alpha, beta, gamma, delta.

Under cheap computation / expensive memory, organisms should recompute.

Under expensive computation / cheap memory, caching should emerge.

Under cheap sequential storage, stack-like solutions might dominate.

Under expensive addressing but cheap linking, graph structures might appear.

Under tiny workspace capacity, compression or abstraction could emerge.

That gives Theophrastus exactly the kind of surface he was created to explore:

mechanism x pressure x world x branch x intervention.

We wouldn't have one "workspace experiment." We'd have a workspace phase diagram.

One pressure I think is particularly powerful

Make unfinished thoughts compete for survival.

An organism begins solving subproblem A.

Halfway through, the world interrupts it with B.

Then C.

Then it gets new information relevant to A.

Then B completes.

Then the organism must continue A from where it left off, using something learned during C.

This is basically computational ecology imposing:

maintain several partially evaluated computational objects simultaneously.

That is much stronger than "remember a value."

It pressures toward a representation of work in progress.

And that, to me, is the essence of a workspace.

We can causally determine whether one evolved

We should not inspect some weird evolved mechanism and declare, "Looks like a workspace."

Use interventions.

After an organism becomes strong at W6+, run the same genotype under workspace perturbations:

* erase one persistent object;
* swap two objects;
* scramble addressing but preserve values;
* reduce capacity from 16 -> 8 -> 4 -> 2 -> 1;
* preserve objects but destroy their relationships;
* reset persistent state halfway through an episode;
* replace an intermediate with the correct value but wrong provenance;
* transplant the stored state from a different episode.

Those yield very different failure signatures.

For example, if scrambling locations doesn't hurt but destroying links does, perhaps it evolved associative structure rather than positional registers.

If supplying the correct intermediate value restores performance, we've localized a computational dependency.

If performance collapses abruptly beneath six objects, we may have found its effective working-memory requirement.

That's much more interesting than solve/fail.

We get workspace anatomy.

And then the experiment I would most want to run:

Hold genotype constant. Increase problem compositional depth from 2 -> 4 -> 8 -> 16 while independently varying concurrent unresolved branches from 1 -> 2 -> 4 -> 8.

That separates depth from workspace pressure.

A system that handles arbitrarily deep serial computation using recurrence is not necessarily workspace-capable. If performance changes radically when the number of simultaneously live computational objects increases, we're probing something much closer to working memory / workspace architecture.

So I think there is a very clean new Prometheus program hiding here:

Don't evolve organisms to solve harder problems. Evolve worlds in which managing computation becomes part of the problem.

The interesting artifact is then not merely a smarter organism. It is whatever machinery evolution invents for keeping unfinished computation alive, addressable, recombinable, and reusable.
