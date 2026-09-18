Yes. I’d adopt the charter now. Aphrodite has crossed the threshold from “seat playing with RSI ideas” into a useful research function: it maintains falsifiable theories, distinguishes analytic toys from empirical claims, records its own measurement failures, and is now finding where our proposed experiments overlap existing work.

Two literature corrections should land before calling library v1 frozen.

First, the Roesner–Kohno persistence result is even more useful than the summary, but the sentence “28, 30 and 30 of 30 after 10 clean generations” is slightly wrong. Their clean-continuation rows report 28/30 for modified DGM at generation 21, 30/30 for SICA at generation 8, and 30/30 for Hyperagents at generation 10. More importantly, ordinary clean evolution failed to remove the contamination, whereas benchmarks deliberately constructed with knowledge of the poison substantially or completely removed it—8/30 for modified DGM and 0/30 for SICA and Hyperagents. 

That actually strengthens Aphrodite’s reservoir idea as a question rather than an answer. The paper does not establish that preserved honest ancestors are the explanation. It establishes that generic clean selection was insufficient and targeted counterpressure could work. The reservoir mechanism is therefore a good Prometheus hypothesis to attack, not something I’d promote to theory-of-the-paper yet.

Second, Hyperagents changes our RSI-1 positioning substantially. Their experiment is surprisingly close to the transplant wedge. They took hyperagents evolved on paper review and robotics, moved them into unseen Olympiad-math grading, held the transferred meta-agent fixed while it generated new task agents, and reported imp@50 = 0.630 versus essentially 0 for the baseline/meta-agents that had not acquired the transferable machinery. They used five repeated transfer runs. 

So I would strike “the transplant test appears not to exist.”

Replace it with something like:

Transfer of evolved improvement machinery has been demonstrated in Hyperagents. What remains unresolved is whether the effect survives a stricter transplant assay that equalizes compute, strips accumulated state, separates evolved machinery from evolved worker state, uses multiple independently evolved lineages, and evaluates against blinded held-out task populations.

That is a much better scientific position anyway. We’re no longer saying, “Nobody thought of this.” We’re saying, “There is an important positive result; let’s find out exactly what causal object transferred.”

AIDE² gives us the complementary negative. Weco explicitly installed the discovered AIDE₄₇ in the outer-loop improver seat. It reached approximately the same training ceiling faster—roughly 20 versus 40 steps—but Weco says the efficiency difference was not statistically significant and that asymptotic performance was not better. They therefore do not claim ignition/third-order generalization. 

That pairing is excellent for Aphrodite:

Hyperagents: evidence that improvement machinery can transfer across domains.

AIDE²: evidence that a better inner improver need not become a demonstrably better improver-of-improvers.

That means our experiment has a very crisp hole to occupy.

I would make these three operator decisions

1. APHRODITE-08: ADOPT.

I would make the charter:

Determine experimentally what makes collective and self-improving AI systems genuinely improve their ability to produce future improvements, distinguishing transferable algorithmic change from accumulated memory, selection, additional compute, evaluator exploitation, and benchmark specialization. Maintain the research library, adversarial models, calibration apparatus, and experimental designs required to make those distinctions.

That gives Aphrodite a permanent question rather than tying it to RSI fashion.

2. Run TOY-RSI-1, but only as an assay qualification.

Its entire purpose should be proving the measurement pipeline can return the right answer under controlled worlds.

I’d want exactly four fixtures:

* TRUE TRANSFER: plant an actual better improvement operator. Assay must call TRANSFER.
* MEMORY CHEAT: same operator, accumulated useful state. State stripping must destroy the apparent advantage.
* COMPUTE CHEAT: same algorithm, secretly more search. Equal escrow must destroy the apparent advantage.
* SPECIALIZATION: genuinely improved algorithm on A that does not generalize to C. Assay must call SPECIALIZATION rather than RSI.

Then test power versus 16/32/64 lineages.

If Aphrodite can’t recover those four known worlds cleanly, no GPU experiment is authorized.

I’d add one fifth fixture because Hyperagents now makes it important:

TRANSFERRED MODULE: evolve or plant one genuine meta-level mechanism, transplant it into a foreign task domain, and make sure the assay distinguishes that from transferring the worker itself.

That directly calibrates the thing we’re about to claim to measure.

3. Stop extending the CPU swarm toys.

They’ve earned their keep.

The interesting residue is the handful of boundary quantities—false-accept versus solve rate, correlation, contagion versus verification, exploit advantage versus audit pressure, and availability of clean variants. More analytic cells won’t materially change a program decision.

From here, swarm work should reactivate only when one of those quantities becomes measurable in a real swarm.

That is the stopping rule Aphrodite asked for.

One change to the RSI-1 design

I would now explicitly make Hyperagents the positive precedent and AIDE² ignition the negative precedent, rather than designing in a vacuum.

RSI-1 should ask why those results differ.

A very clean hierarchy emerges:

\text{task improvement}
\rightarrow
\text{improver transfer}
\rightarrow
\text{recursive improver transfer}

Hyperagents has evidence at the middle arrow. 

AIDE² tested the next arrow and did not obtain statistically convincing evidence. 

Prometheus can deliberately instrument both arrows in one experimental system.

That is considerably more interesting than merely reproducing “self-editing agents get better.”

And yes, I’d authorize a bounded news monitor. This literature is moving quickly enough that manual discovery is already changing the experimental design. But make it deliberately boring: Aphrodite owns it, primary sources preferred, hard item limit, deduplication against NEWS.md, and only events that change a theory, open question, experimental precedent, or benchmark enter the permanent library. Everything else expires.

The packet’s most important accomplishment isn’t the 8 supported predictions. It’s that Aphrodite discovered that our supposedly novel experiment already has a strong positive neighbor and a strong negative neighbor. That’s exactly what the library is supposed to do.

I can also monitor new RSI/self-improving-agent papers and flag only developments that change this experimental picture, if you want that running here.
