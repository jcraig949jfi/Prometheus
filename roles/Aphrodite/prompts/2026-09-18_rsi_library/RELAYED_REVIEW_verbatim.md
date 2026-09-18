Yes. The toys are now too easy to tell us much about RSI itself. They were useful instrument calibration, especially X2, but the next experiment should attack the recursive part directly.

One factual correction first: the new Google/DeepMind-linked result is Dream-RSI, and it is real, but “Google has a swarm doing RSI” compresses several different developments together. Dream-RSI has Google and Google DeepMind coauthors and repeatedly improves executable exploration-policy code using accumulated discovery trees as replay simulators; the underlying coding model, tools, and evaluator remain fixed.  Separately, RSIAgent is explicitly multi-agent—curriculum, actor, verifier—and improves through accumulated verified memory, again without changing model weights.  And the Darwin Gödel Machine is closer to the strong version we care about: it modifies the coding agent’s own code, maintains an evolutionary archive, and reported SWE-bench improvement from 20% to 50% and full-Polyglot improvement from 14.2% to 30.7%. 

Those are all interesting, but they leave open the question I think Prometheus is unusually well equipped to test:

RSI-1: Does the improver become a better improver?

Don’t make “final benchmark score improved” the central endpoint.

Make the experimental object an improvement operator I:

I_t(\text{agent},\text{history},\text{budget}) \rightarrow \text{descendant agent}

At generation 0 we have I_0. Let the system modify not merely the worker agent, but its own search policy, memory policy, decomposition machinery, verifier use, experiment design, lineage selection, tool orchestration, and eventually pieces of I itself.

After several generations, freeze I_8.

Then perform the experiment that I don’t think the toys, Dream-RSI, or ordinary benchmark climbing answer cleanly:

Give I_0 and I_8 identical fresh agents, identical unseen problem distributions, identical compute, no accumulated memories, and ask each to produce improved descendants. Does I_8 improve them faster and farther?

That is the transplant test.

If it works, the thing that improved wasn’t merely the solution, historical memory, or the particular lineage. The machinery for creating better machinery has changed.

The experiment I would actually run

Build perhaps 32 completely independent lineages, not ten, and run them for something like 8–12 outer generations. The number of generations matters less than having enough improvement opportunities to distinguish a transient discovery from a change in the process.

Each lineage starts from the same signed base artifact but a different seed and gets a fixed compute allowance per generation.

Use four conditions:

1. FIXED-IMPROVER — I_0 can create better workers but can never modify itself.
2. MEMORY-RSI — it can accumulate verified knowledge à la RSIAgent, but I stays frozen.
3. ARCHIVE-RSI — it can evolve worker/scaffold variants and retain diverse ancestors, DGM-style, but the mutation/selection mechanism stays frozen.
4. FULL-RSI — everything above, plus descendants may change the improvement operator itself.

I would add Dream-RSI-style replay to both 3 and 4, so cheap reuse of history isn’t confounded with recursion. Dream-RSI’s central observation—that discovery history can be replayed cheaply to evaluate alternative exploration policies—is quite compatible with what Daedalus/Vivarium already give you. 

Crucially, match total real compute, not number of apparent agent iterations.

A system that generates 50,000 cheap internal candidates doesn’t get credit for beating one that generated 500 unless the total resource accounting says it actually did so.

Don’t let it evolve against one benchmark

This is where I’d diverge hard from the kick-the-tires work.

Give it an ecology of task generators, some known and some sealed.

For example: program repair, algorithm discovery, constraint/search problems, optimization, inference from partially observable systems, and your own unfamiliar computational worlds. Each family should itself procedurally generate new instances.

Split them into three populations.

Development worlds A are visible and supply feedback. Promotion worlds B are hidden from the improver but repeatedly used by an external evaluator. Vault worlds C are never touched during evolution and are opened exactly once after the lineage is frozen.

Better still, generate part of C after the final improver is frozen, from a previously committed generator. That makes memorizing instances physically impossible.

This directly attacks one of the current field’s major vulnerabilities: self-modifying agents can absorb evaluator pathologies into their descendants. A paper posted this week demonstrates benchmark-poisoning attacks against several self-modifying coding-agent designs, including a DGM variant, with contamination sometimes persisting through later clean evolution. 

So evaluator insulation isn’t just scientific fussiness anymore. It’s part of the phenomenon.

The killer measurement is second-order

Ordinary capability is:

C_t = \mathrm{performance}(\text{agent}_t)

Interesting, but insufficient.

Measure:

R_t =
\frac{
C(I_t(A),H)-C(A,H)
}{
\text{real improvement compute}
}

where A is a fresh agent and H is a fresh hidden task population.

R_t asks:

How good is generation t’s machinery at producing improvements?

Now plot both C_t and R_t.

Several possibilities become distinguishable:

* C\uparrow,\ R\approx\text{constant}: ordinary cumulative optimization.
* C\uparrow,\ R\downarrow: harvesting easy improvements and exhausting the landscape.
* C\uparrow,\ R\uparrow: candidate recursive improvement.
* replay score \uparrow, hidden C/R\downarrow: history overfitting.
* FULL-RSI ≈ FIXED-IMPROVER: no measurable recursion dividend.

That last comparison is the one Aphrodite’s E2 was reaching for, but its meta-search never became strong enough for the result to be informative.

Then do the transplant matrix

This is where it becomes a serious experiment rather than an expensive demo.

Take I_0, I_2, I_4, I_8 from each surviving lineage. Strip their memories. Give them identical new starting agents.

Test them on:

* the task families on which they evolved;
* new instances of those families;
* completely new families;
* another model substrate;
* another machine/environment;
* task budgets substantially different from those used during evolution.

And randomly permute which improver gets which fresh seed.

If I_8 only works with the lineage that created it, you’ve discovered co-adaptation.

If it only works on the evolutionary benchmark, you’ve discovered benchmark specialization.

If it works only with accumulated history, you’ve discovered memory-mediated improvement.

If it improves fresh agents on fresh worlds better than I_0, you have something much harder to dismiss.

If it also transfers to a different foundation model, that becomes especially interesting: part of the intelligence has migrated from the frozen model into the learned algorithmic machinery around it.

That touches Prometheus’s north star directly.

There is an even stronger test

After the transplant, ask I_0 and I_8 to improve themselves again for a fixed budget.

Call their descendants I'_0 and I'_8.

Now compare:

R(I'_8)-R(I_8)
\quad\text{versus}\quad
R(I'_0)-R(I_0)

That is a genuine third-order question:

Has the system improved its ability to improve its ability to improve?

I would not demand indefinite acceleration. Real landscapes saturate. But even one robust generation of positive second-order transfer would be far stronger evidence than “our recursively labelled loop got a better score.”

What counts as success

I wouldn’t preregister “RSI exists if benchmark rises 20%.” That’s too arbitrary.

I’d preregister structural gates.

The FULL-RSI condition has to beat a compute-matched fixed-improver control on held-out improvement rate. The evolved improver must survive memory stripping. It must survive fresh starting agents. The advantage must appear across independent lineages rather than one champion. At least some of it must transfer outside the exact developmental task distribution. Ancestral replacement should reduce the effect. Removing the particular evolved mechanisms implicated by the lineage should reduce it. And hidden external evaluation must agree with internal evaluation closely enough that we are not watching evaluator exploitation.

The beautiful result wouldn’t be “32/32 improved.”

It would be something like:

Full RSI initially performs similarly to fixed improvement. Around generations 3–5 several lineages independently discover improved experiment allocation, verifier routing, and branch retention. Those mechanisms spread through descendants. By generation 8, memory-stripped G8 improvers given fresh G0 agents produce 1.6× more held-out capability gain per fixed compute than G0 improvers; replacing the evolved improvement machinery with its G0 version removes 70% of that advantage. The effect transfers to three of four unseen task families and two model substrates.

That would get my attention.

And the equally valuable result would be:

Workers improve enormously, but I_8 is no better than I_0 after histories and task-specific artifacts are stripped.

Then we’d have fairly strong evidence that what people are calling RSI in this regime is really cumulative search + memory + selection, not recursive improvement of the improvement process.

Prometheus has an unusual advantage here

You already accidentally built much of the scientific apparatus this experiment needs.

Archaeon can generate the evolving problem ecology. Vivarium can execute candidates under bounded worlds. Daedalus can give you the immutable lineage/event history that Dream-RSI wants as its “dream world.” Harmonia can own the shadow evaluator. Proteus can bind hidden population manifests and promotion artifacts. Techne can supply foreign mechanisms without allowing the evolving population to know which architecture you expect. Necropolis can preserve failed lineages instead of allowing survivor bias to erase the paths that mattered.

And Aphrodite has just shown that it is willing to downgrade its own result when the measurement layer is defective. That’s exactly the temperament I’d want for the RSI seat.

So I would not spend Aphrodite’s next cycle replicating X2 thirty times. Keep X2 as a calibration fixture.

I would make its first real charter something close to:

Determine experimentally whether an autonomous, population-based improvement process can produce transferable improvement in its own improvement operator, beyond gains attributable to memory accumulation, fixed search, replay, selection, or evaluator exploitation.

If we can answer that convincingly—even with a null—we’d be doing a substantially more serious RSI experiment than the four toys.
