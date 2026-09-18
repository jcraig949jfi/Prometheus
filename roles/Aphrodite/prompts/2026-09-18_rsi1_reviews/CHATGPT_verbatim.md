This is now close to an execution-grade preregistration. The main architecture is right, but I would change several things before freezing Genesis, because a few of the current rules can accidentally manufacture either a positive or a null.

The biggest issue is R=\Delta C/\mathbb C as the primary statistic. Ratios are nasty: an improver can look spectacular because the denominator happens to be small, and task difficulty creates heteroskedasticity. Keep R as a descriptive efficiency metric, but make the primary experiment a compute-matched capability comparison:

\Delta_{\text{RSI}}
=
C(I_8(A); B)-C(I_0(A); B)

with exactly the same escrow B.

Then repeat at several preregistered budgets B_1,B_2,B_3. The strongest evidence is not merely R_8>R_0; it is that the capability-vs-compute frontier has moved outward:

C_{I_8}(B) > C_{I_0}(B)

over a useful range of budgets.

That distinguishes “shifted the scaling curve” from “chose another point on the curve” much more cleanly.

Second, I would not define failure as “CI contains zero, therefore H0 is true.” That is too strong statistically. A null result can mean insufficient power. Instead preregister an equivalence region.

For example:

|\Delta_{\text{RSI}}| < \delta

where \delta is the smallest improvement worth calling scientifically meaningful. Then the interesting null is:

the confidence interval lies entirely inside [-\delta,+\delta].

That lets Aphrodite say EQUIVALENT rather than merely “failed to reject.”

Likewise, I would drop Cohen’s d<0.2 as a universal gate. The meaningful effect size should live in the experiment’s own units: additional solved tasks per fixed compute, improvement probability, regret reduction, etc.

The third important correction concerns what gets stripped in the transplant.

You don’t only want:

I_8 + \text{no memory}

You want a factorial transplant.

Run at least:

\begin{array}{c|cc}
& M_0 & M_8\\
\hline
I_0 & I_0M_0 & I_0M_8\\
I_8 & I_8M_0 & I_8M_8
\end{array}

where M denotes accumulated/distilled state.

Now you can separate:

* value of evolved machinery;
* value of accumulated knowledge;
* interaction between machinery and its native knowledge.

I’d do the same with the worker substrate:

I_0(A_0),\quad I_8(A_0),\quad I_0(A_8),\quad I_8(A_8)

if workers themselves are allowed to evolve.

Otherwise you can easily credit the improver for a better worker.

Your four-module object model is a good I₀, but I would add a fifth component:

5. Experiment / Evidence Policy

This decides what the improver measures before deciding how to mutate itself.

Baseline I₀ gets only aggregate outcome statistics.

Its descendants can potentially learn to run controlled comparisons, estimate uncertainty, identify bottlenecks, construct probes, and decide which hypothesis deserves compute.

That matters because one of the deepest forms of improvement may not be better search or better verification. It may be:

becoming better at determining why it failed.

If RSI is real in an interesting sense, I would expect experimental competence itself to evolve.

There is another subtle problem with the “module mutated most → lobotomize it” control. Lines changed is not causal importance.

Instead of choosing the largest diff after the fact, preregister a complete causal decomposition:

* replace Search₈ with Search₀;
* replace Verify₈ with Verify₀;
* replace Memory₈ with Memory₀;
* replace Allocator₈ with Allocator₀;
* replace Evidence₈ with Evidence₀;
* then selected pairwise replacements if the first-order effects suggest interactions.

And perform the complementary operation:

transplant one evolved module at a time into I₀.

That gives you necessity and sufficiency.

If

I_8-\text{Verify}_8 \rightarrow \text{large loss}

and

I_0+\text{Verify}_8 \rightarrow \text{large gain},

then you have a very strong causal claim about an evolved mechanism.

That is much more compelling than interpreting a source-code diff.

There are also two engineering points I’d change.

Harmonia should not trust Python call stacks for attribution. The evolving program can accidentally or deliberately distort them. Give every permitted capability an unforgeable resource handle:

search_budget, verify_budget, memory_budget, etc.

Calls travel through those capabilities, and Harmonia records the handle that authorized the operation. The hard global budget still lives below everything.

And don’t pretend \alpha T_{in}+\beta T_{out} is literally FLOPs unless you’re controlling inference hardware. For heterogeneous hosted models, call it something like Standardized Inference Cost. If Prometheus controls the GPU stack, then you can measure actual accelerator time / energy / FLOP estimates. Otherwise, exact token counts plus fixed model-specific tariffs are more defensible than pretending \beta=3 represents physics.

The future-entropy Vault design is excellent, with one wording correction.

The instances do not yet exist. The task distribution does.

That distinction matters. I₈ can still learn properties of the committed generator family if information about that family leaks. So C should probably have two layers:

C₁ — future instances, known committed families. Tests instance memorization.

C₂ — future instances from sealed families never exposed to the evolutionary process. Tests distribution transfer.

And perhaps eventually:

C₃ — post-freeze task families written independently after the evolution concludes.

C₃ is exceptionally hard to explain away if the result transfers.

I’d also make the entire experiment hierarchical rather than treating “30 seeds” as 30 iid observations. There will be variance from lineage, task family, generated instance, model sampling, and transplant seed.

Conceptually:

\text{outcome}
\sim
I_t
+
\text{task family}
+
\text{lineage}
+
I_t\times\text{family}
+
\epsilon

Otherwise thirty runs of essentially one world can give extremely narrow confidence intervals around an extremely narrow claim.

And I would change one philosophical point in the proposed conclusion.

A null here would not prove that current industry RSI is merely search and memory. That’s broader than this experiment supports.

It would establish something stronger scientifically because it is narrower:

Under the specified substrate, task ecology, mutation language, compute regime, and evolutionary horizon, observed cumulative capability gains did not produce a detectable transferable improvement in the improvement operator.

Then we can alter one dimension and try again.

That creates a research program rather than a one-shot referendum on RSI.

The result I’d consider genuinely extraordinary

Not merely:

C_8>C_0

or even:

I_8(A_0)>I_0(A_0).

I would want to see this chain:

I_8(A_0,C_2) > I_0(A_0,C_2)

under identical resource escrow;

then the same relationship across multiple budgets;

then removal of one or more evolved mechanisms destroys the effect;

then transplanting those mechanisms into I₀ partially recreates it;

then I_8, given another improvement cycle, generates an I'_8 whose transplant advantage exceeds its parent’s;

and ideally some portion survives a model-substrate transplant.

At that point the most economical explanation starts becoming:

the system discovered reusable machinery for producing better cognitive machinery.

That’s the phenomenon we’re actually hunting.

So I would promote this from “Aphrodite’s next experiment” to an actual RSI experimental program. The first campaign should probably stop at second-order transfer. Don’t run the third-order crucible until we’ve demonstrated that the transplant assay itself gives stable positive, negative, equivalence, and contamination controls.

The toy work becomes Campaign 0: instrument calibration.

This becomes Campaign 1: Does the improvement operator transfer?

And only if Campaign 1 survives do we earn Campaign 2:

Can the improved improver recursively improve its transferable improvement capacity?
