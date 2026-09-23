# Selective Irreversibility

Verbatim capture, 2026-09-23. Operator note, filed under Physics of Intelligence —
possible fundamentals, rather than under "AI architecture".

---

Intelligence is not thermodynamically efficient forgetting. It is thermodynamically efficient selective irreversibility: destroying distinctions that no longer matter while preserving distinctions that predict, control, or generalize.

That distinction turns the analogy into something we may actually be able to formalize.

Landauer’s principle says that logically irreversible operations—many possible logical states being mapped into fewer states—carry a thermodynamic cost. Reversible computation can in principle avoid that cost until information is actually erased/reset.  Experiments have directly demonstrated the k_BT\ln2 limit for bit erasure, and more general treatments relate the minimum work cost to the information discarded conditional on the output. 

The really interesting connection: abstraction is many-to-one

Suppose an intelligent system observes some gigantic state:

X

and constructs an abstraction

Z=f(X).

Imagine millions of distinct X’s all become:

predator

or

prime number

or

unstable trajectory

or

use this subroutine.

That’s a many-to-one map.

The abstraction deliberately makes distinctions disappear.

If the physical implementation really disposes of those distinctions rather than retaining them somewhere as reversible bookkeeping, then the amount erased is approximately related to

H(X\mid Z)

—the information about the original state that cannot be recovered from the abstraction.

So an idealized cyclic physical learner suggests something like

W_{\text{erase}}
\gtrsim k_BT\ln2\,H(X\mid Z)

with important physical assumptions around how the memory and reset are implemented.

That is already remarkably close to your proposed principle.

But now introduce another variable:

Y = \text{future/task/action-relevant structure}.

A good abstraction doesn’t merely maximize H(X\mid Z). A random shredder could do that.

It tries to make Z very small while preserving

I(Z;Y).

And that’s essentially the territory of the Information Bottleneck: find a compressed representation of X that retains information relevant to Y. 

Combine Landauer + Information Bottleneck, and suddenly we get something much more interesting than either separately:

\boxed{\text{Intelligence} \sim
\text{preserve useful distinctions while irreversibly eliminating useless ones}}

That might be one of our missing dials.

And it changes your four propositions in useful ways

1. Hallucination as the thermodynamic default

I’d weaken the literal claim but keep the deeper insight.

Thermodynamic entropy and semantic incorrectness aren’t the same thing. A system can produce an extremely ordered, low-entropy, completely false story. So Landauer alone doesn’t imply hallucination.

But an intelligent physical system is unquestionably a nonequilibrium system. Maintaining organized internal states against noise requires continued free-energy expenditure. And maintaining truth-correlated organization requires repeated coupling to the environment.

So I’d replace:

intelligence requires energy to prevent thought dissolving into noise

with:

intelligence requires continued expenditure to maintain task-relevant correlations against degradation, perturbation, and irrelevant state proliferation.

That is much more defensible.

And notice the important addition: grounding isn’t merely information coming in. It’s entropy exported while useful correlations are maintained.

⸻

2. Falsification as erasure

Here there’s an important subtlety.

Falsifying a hypothesis doesn’t necessarily erase it. I can retain:

\{H_1:\text{false}, H_2:\text{false}, H_3:\text{true}\}

reversibly forever.

Landauer’s bill arrives when finite memory eventually says:

I no longer need the complete histories of H_1 and H_2.

and resets those states.

So perhaps falsification has two stages:

\text{distinguish} \rightarrow \text{discard}.

The first creates information.

The second destroys distinctions.

And bounded intelligence forces the second step eventually.

That’s fascinating, because an unbounded reasoner could theoretically keep its entire search tree. A bounded reasoner cannot.

Therefore:

Boundedness may be what makes intelligence thermodynamic.

Memory limits force irreversible choices about which distinctions deserve continued physical existence.

That sounds like a serious candidate for our physics-of-intelligence search.

⸻

3. Steering as work

Your intuition survives, but I’d move it from Landauer specifically into nonequilibrium control theory.

There is actual work connecting thermodynamic control to geometries over state spaces; within certain regimes, a metric over thermodynamic states determines dissipation along finite-time trajectories. 

So imagine our intelligence manifold again.

An intelligent trajectory wanders toward some undesirable region.

A steering intervention changes its trajectory:

s_t \rightarrow s'_t.

The right question becomes not merely:

Did steering work?

but:

\frac{\text{capability restored}}
{\text{control work injected}}.

Now we have another dial:

restorative efficiency.

Some architectures might need enormous intervention to return to a useful basin. Others might self-correct after a tiny perturbation.

That is measurable.

And it suggests that the geometry of the intelligence region itself matters: basin width, boundary curvature, attractor strength, escape rates, restoration energy.

⸻

4. Compression has a boundary

Here I think you’re onto something especially important, but the boundary likely comes from rate-distortion, not Landauer alone.

Compression itself can be reversible. I can compress a file and retain every bit.

The critical act occurs when we say:

These distinctions aren’t worth keeping.

Then compression becomes lossy.

So imagine moving along:

X\rightarrow Z_1\rightarrow Z_2\rightarrow Z_3\rightarrow\cdots

with increasingly aggressive abstraction.

Initially we erase nuisance variation.

Performance improves.

Then eventually:

I(Z;Y)

starts collapsing.

That’s the abstraction cliff.

And different architectures may have radically different cliffs.

That feels exactly like one of your hidden sliders.

⸻

There is an existing result that makes this even more compelling

Still, Sivak, Bell and Crooks studied physical systems that retain information about their environments and separated remembered information into information useful for predicting the future and information merely about the past.

They found a direct relationship between nonpredictive stored information and thermodynamic inefficiency. Their term for the useless retained past information is particularly memorable: nostalgia. 

That is strikingly close to what we’re circling.

A highly efficient adaptive system should not remember everything.

It should preferentially retain what predicts what comes next.

So perhaps the fundamental isn’t compression.

It’s:

\boxed{\textbf{predictive selective retention}}

Everything else gets progressively released.

This gives us a candidate “Landauer principle of intelligence”

I wouldn’t state it yet as a law. I’d state it as a hypothesis we can try to kill:

Selective Irreversibility Hypothesis

Any bounded physical intelligence operating cyclically must continually compress its accumulated state. When that compression physically erases distinctions, it incurs an irreducible thermodynamic cost. Intelligence is therefore constrained not simply by computation or memory, but by its ability to minimize irreversible destruction of task-relevant information while efficiently disposing of task-irrelevant information.

That gives us three measurable quantities:

D = \text{information discarded}

R = \text{relevant/predictive information retained}

E = \text{physical or computational expenditure}.

And now we can start looking for ratios.

For example, an intelligence thermodynamic efficiency:

\eta_I =
\frac{I(Z;Y)}
{E/(k_BT\ln2)}

roughly: predictively useful bits maintained per Landauer-equivalent unit of expenditure.

Or, independently of actual joules initially:

\eta_A=
\frac{I(Z;Y)}
{I(X;Z)}

useful information per bit retained.

And perhaps:

\eta_F =
\frac{\text{hypothesis-space volume eliminated correctly}}
{\text{irreversible state changes}}

for falsification efficiency.

I wouldn’t become attached to any of these equations yet. They are rulers to attack.

But here’s the part I find most consequential for Prometheus

We have been treating constraints as annoyances or experimental parameters.

Memory caps. Compute caps. Bandwidth. Energy. Organism size. Communication restrictions.

They may be causal ingredients.

Without pressure to forget, there is little pressure to abstract.

Without pressure to abstract, there is less pressure to discover invariants.

Without discarded distinctions, everything can remain episodic.

So one possible progression is:

\text{boundedness}
\rightarrow
\text{forced forgetting}
\rightarrow
\text{selective compression}
\rightarrow
\text{invariants}
\rightarrow
\text{abstraction}
\rightarrow
\text{transfer}.

That is a testable causal chain.

And it produces a rather provocative prediction:

Giving an adaptive system more memory should sometimes make it less intelligent, because it removes the pressure to discover cheaper sufficient representations.

Not always. But there should be regimes where capability peaks at an intermediate resource constraint rather than at maximum memory.

That would be a beautiful thing for Cosmos, Ensorain, Aether, BEE, or Nestor to attack independently.

We could dial memory from effectively infinite down through severe constraint and ask whether there is a phase transition where the organisms suddenly begin inventing reusable abstractions.

Then do the same with compute, bandwidth, communication, replay, falsification cost, and irreversible-update cost.

If the same transition appears across radically different substrates, we have found something much more interesting than another ML trick.

We may have found one of those hidden axes in the control space we were talking about:

\boxed{\text{pressure to eliminate irrelevant distinctions}}

And that might genuinely sit underneath compression, abstraction, generalization, forgetting, falsification, dreaming, and even reasoning itself. 

That is exactly the sort of candidate I would put on the wall under Physics of Intelligence — possible fundamentals, rather than under “AI architecture.”
