Operator message to Atlas, 2026-10-02 (verbatim). First line as sent: "Theres likely a series of experiments here:"

Theres likely a series of experiments here:

Yes. There is a genuinely useful idea here for Prometheus, but I would borrow the search architecture rather than adopt AutoDiscovery unchanged.

AutoDiscovery takes a structured dataset, generates hypotheses, designs and executes statistical experiments, interprets the results, and then uses Bayesian surprise—how much the evidence changes its prior belief—as the reward signal for deciding which part of hypothesis space to explore next. It uses MCTS with progressive widening to balance following promising branches against opening new ones. The original work reports 5–29% more surprising discoveries than alternative search strategies under a fixed hypothesis budget across 21 datasets. 

That is remarkably close to something Prometheus presently needs: a search policy above the individual engines/lenses.

Where I think it fits

Right now Prometheus has increasingly good machinery for producing worlds, mechanisms, rulers, perturbations, assays, and forensic artifacts. Phase 3 is pushing especially hard on ruler certification and distinguishing signal from hallucination. What we don’t yet have as cleanly is:

Given everything Prometheus has already observed, what experiment should it perform next?

AutoDiscovery provides one possible answer: pursue the branches producing the largest epistemic change.

That would turn the thing we’ve been calling findings into more than a reporting metric. A finding becomes a unit that changes the system’s current model of the search space. Then Prometheus can optimize something roughly like:

useful epistemic change / compute / inference / human attention

rather than simply experiments/run, flags/run, or candidate mechanisms/run.

This also fits your recent intuition that the rate at which we can throw cognitive architectures into the Phase 3 RSO should become measurable.

But there is an important catch.

I would not use AutoDiscovery’s LLM prior as Prometheus’s primary prior

This is almost perfectly aimed at one of your standing concerns about Prometheus: LLM gravity.

AutoDiscovery asks the language model how probable it thinks a hypothesis is before the experiment, gives it the evidence, asks again, and rewards the belief shift. Ai2 explicitly describes the prior as coming from knowledge in the underlying LLM. 

That makes sense for ordinary science. For Prometheus, it is dangerous.

Suppose an alien computational mechanism appears that bears little resemblance to known ML, CA, evolutionary computation, reservoir computing, etc. An LLM’s epistemic state is exactly the thing we don’t want defining the shape of interestingness. It could either massively over-reward superficial weirdness or suppress mechanisms because its conceptual vocabulary doesn’t represent them well.

And Ai2 has already run into a version of this problem. In the UW challenge you linked, AutoDiscovery performed badly on 24,000 synthetic nuclear-reactor configurations: about half the generated hypotheses were judged illogical and none worth pursuing. The investigators attributed the failure to the fact that its surprise machinery was calibrated around real-world measurements and behaved poorly on synthetic data. With real reactor measurements it did substantially better. 

Prometheus is practically the pathological test case for that weakness: synthetic universes are the point.

So I’d invert the idea.

Prometheus Surprise should be empirical, not primarily linguistic

Imagine a new layer—I wouldn’t even make it another big engine initially—sitting over Atlas/findings and the experimental fabric.

Instead of:

LLM prior → experiment → LLM posterior → surprise

use something more like:

Prometheus evidence state → candidate experiment → certified measurement → evidence-state change

The evidence state could contain world-family statistics, mechanism lineage, ruler calibration envelopes, null/control behavior, previous perturbations, transfer results, known failure classes and prior findings.

Then the reward needn’t be a single naïve surprise number. Conceptually:

Discovery value ≈ epistemic surprise × ruler trust × replication × transfer × novelty ÷ cost

with hard vetoes for things like uncalibrated rulers and known confound signatures.

The LLM prior can still be one observer—perhaps an interesting one—but not the observer. We could deliberately maintain multiple observers:

* empirical Prometheus prior derived only from experimental history;
* null-model prior;
* world-family/local prior;
* predictor trained on previous results;
* LLM prior;
* deliberately memory-starved or alien-prior observer.

Disagreement among those observers could itself become an anomaly detector.

That starts sounding very Prometheus-like.

And interestingly, Ai2 themselves have already discovered that static surprise is insufficient. Their June 2026 follow-up updates beliefs using previous experimental evidence and uses retrieval over past discoveries. They report that 37.5% of static-surprise events were spurious and that modifying the search to account for evolving beliefs plus diversity increased accumulated non-stationary surprise by about 30.6% across their five tested domains. 

That is directly relevant to our library-learning / Sagacity direction: the searcher should become harder to surprise by things it has already learned.

There is an unusually good experiment we could run immediately

I would not start by wiring AutoDiscovery into a live Prometheus engine.

Use Prometheus’s own history as a forensic benchmark.

Construct one table from historical runs across NPE, BEE, Ensorain, Cosmos, SFE, etc., containing enough metadata to generate hypotheses but deliberately preserving the important historical traps. Then let an AutoDiscovery-like searcher explore it.

We already know where several landmines are. For example, it should encounter things corresponding to:

* NPE’s seeded-witness/transplanted-lineage “spontaneous replication” false signal;
* Ensorain’s marks/running-mean phenomenon and constant-baseline kill;
* Cosmos’s location bias;
* genuine control signals and surviving anomalies.

Then ask a very strong question:

Does surprise-guided open-ended search independently converge on the anomalies that mattered, distinguish the confounds, and produce useful next experiments—or does it simply become an efficient machine for chasing our historical artifacts?

That would be a beautiful Phase 3 assay because we know quite a bit of the hidden answer already.

We could compare four search policies under exactly the same budget: random exploration, diversity search, original AutoDiscovery-style static surprise, and Prometheus evidence-conditioned surprise.

The outcome I care about wouldn’t be “number of surprising hypotheses.” It would be certified findings per unit search budget, plus false-finding burden and human-review burden.

If the Prometheus version wins, then we have something much bigger than an imported tool.

We have the beginnings of a discovery scheduler.

And the implementation barrier is low

Ai2 has published the code, and the current Asta AutoDiscovery repository is Apache-2.0 licensed. Their standalone interface already supports local structured datasets, experiment budgets, MCTS parameters and even an optional search intent, so we don’t have to reconstruct the whole system merely to study it.  The older research implementation is also explicitly designed for bring-your-own datasets and resumable MCTS searches. 

So I think this deserves a bounded Prometheus probe, not just a reading note.

The more I look at it, the most important idea isn’t AutoDiscovery itself. It’s that we may be able to give the entire Phase 3 ecology a work-conserving experimental attention mechanism:

observe → find contradiction/surprise → allocate experiments → certify → update shared evidence state → search somewhere newly informative.

That could eventually sit underneath the seats and eliminate a fair amount of today’s human/agent micromanagement about what should be investigated next, while still leaving the actual scientific rulers to keep it honest.

And that is much closer to a primitive for Sagacity than “another science agent.”
