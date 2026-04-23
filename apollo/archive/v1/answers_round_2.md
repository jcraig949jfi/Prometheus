These are excellent questions and this is exactly the kind of rigor that prevents a 40-day run from producing 40 days of garbage. Let me take them in order.

---

## 1. The `self` Problem

Your proposed solution is correct. Rewrite `self.param_name` into `self.params['gene_XX_param_name']` during gene extraction. The parameter vector becomes the evolvable genome in the classical sense — a flat list of floats that CMA-ES or point mutation can operate on directly. The compiler assembles `__init__` from the union of all gene parameter requirements.

This also gives you something valuable for free. You can log the parameter vector alongside the wiring graph in the lineage JSONL. When you see a fitness jump between parent and child, you can immediately check whether the jump came from a parameter change or a structural change. That distinction matters enormously for understanding what's actually driving evolution.

One additional detail: when two genes from different tools both have a parameter called `lambda_balance`, the gene_id prefix prevents collision. But also track the original parameter name in the gene metadata. If evolution converges on similar values for `gene_03_lambda_balance` and `gene_07_lambda_balance`, that's a signal that those two genes are doing related work and might be candidates for merging in a future version.

## 2. Two Methods, One Wiring Graph

Option (a). Auto-generate confidence from evaluate. This is the right call for three reasons.

It matches what the forge tools actually do. It eliminates an entire class of compilation failures. And if an organism eventually needs a more sophisticated confidence method, that capability can emerge through a SCORER gene at the end of the pipeline that explicitly maps raw scores to calibrated probabilities — which is functionally the same thing but expressed within the single wiring graph rather than as a separate method.

The CONFIDENCE gene type from the original spec becomes a CALIBRATOR gene — a scorer that takes other scores as input and outputs a probability. It lives within the evaluate pipeline. The `confidence()` method on the compiled class is just a thin wrapper that calls evaluate on a single candidate.

## 3. What Data Type Flows Through the Wires

Option (b) — the shared context dict. This is the right architecture and it has a critical secondary benefit you didn't mention.

The context dict is observable. You can log it at each gene boundary during evaluation. When an organism produces an unexpected result, you can inspect the context dict after each gene fired and see exactly where the reasoning went wrong. This is the organism's "residual stream" — directly analogous to what Prometheus tracks in transformer layers.

The initial context is:
```python
ctx = {'prompt': prompt, 'candidate': candidate, 'raw_text': prompt + ' ' + candidate}
```

Each gene reads what it needs, writes what it produces, and passes the full dict downstream. The compiler validates that every gene's required input keys exist somewhere upstream in the wiring graph. If not, the organism fails compilation.

One addition: the compiler should inject a `ctx['_gene_trace'] = []` that each gene appends to. This gives you the reasoning trace for free, and it's the foundation for `evaluate_trace()` when you're ready for it post-MVP.

## 4. NCD: Infrastructure or Gene

Margin-over-NCD as the fitness metric. Inherit the Hephaestus approach. This is non-negotiable for preventing NCD monoculture.

Here's the specific implementation: every organism's raw accuracy is computed, then NCD baseline accuracy is subtracted. An organism that scores 40% raw but NCD scores 30% on the same tasks gets a fitness of 10%. An organism that IS just NCD with decoration scores 0%. This makes NCD a floor that provides zero selective advantage.

NCD still exists as a gene in the library — organisms can use it as a component. But they get zero credit for the part of their score that NCD alone would have achieved. They're evaluated purely on their added value.

This is the single most important decision for preventing the convergence trap that killed every previous attempt at evolving code evaluators.

## 5. How Novelty Enters Selection

Option (a) — novelty as a third NSGA-II objective. Making it a full Pareto dimension gives it real teeth. An organism that scores zero on accuracy but has a completely novel behavioral signature is Pareto non-dominated by an organism with 30% accuracy and zero novelty. Both survive. This is exactly the mechanism that preserves stepping-stone organisms that are currently bad but structurally interesting.

Three objectives is still fine for NSGA-II. You don't need NSGA-III until you hit 4+ objectives. The three dimensions are: margin-over-NCD accuracy, calibration, and novelty. Each is a genuine axis that the others can't substitute for.

Do NOT decay novelty weight over time. The review suggests 40% early and 20% later. But the whole point of novelty search is that it prevents convergence at every stage, not just early on. Keep it as a full Pareto dimension throughout. If the population becomes diverse enough that novelty is easy to achieve, that's fine — it just stops being the binding constraint and accuracy takes over naturally.

## 6. Gene Deletion

Include it at 10%. You're right that without it, genomes grow monotonically. But more importantly, deletion is how evolution discovers which genes are actually load-bearing.

When deletion removes a gene and the organism's fitness stays the same, that gene was dead weight. When deletion removes a gene and fitness drops, that gene was essential. The lineage log captures both cases. Over hundreds of generations, the pattern of deletion-survival and deletion-death maps the functional architecture of each organism — which genes matter and which are passengers.

This is also how simplification happens. A 15-gene organism that evolved from bloated ancestors but had 10 genes deleted and survived is a distilled version of whatever reasoning strategy the lineage discovered. Those simplified organisms are more interpretable and more likely to generalize.

Four mutation operators was too few. Make it five: point mutate, splice, duplicate, rewire, delete. Rates: 40% point mutate, 25% splice, 15% duplicate, 15% rewire, 10% delete. These don't need to be exclusive — multiple mutations can stack per offspring, which is already in the spec.

## 7. The Viability Spike

Yes, absolutely do this. It's the single most valuable afternoon you can spend before building anything.

50 lines. Extract methods from 10 forge tools. Create 100 random chimeras via AST method swapping. Test how many produce valid Python that runs on 1 trap without crashing. This gives you the empirical viability rate.

If it's above 40%, AST-only is viable for MVP.

If it's between 10-40%, you need the warm start (seeding with working tools, mild mutations only for the first 200 generations) to give evolution a gradient to follow.

If it's below 10%, the review is right and you need LLM-assisted mutation for MVP, not post-MVP. At that point, the cheapest path is a local StarCoder 1B as a mutation operator — no API calls, no network, fits on the card. The viability spike result determines whether this is needed now or later.

Run the spike first. Everything else depends on the number.

## 8. Held-Out Validation

Yes. Generate a held-out trap battery with a different seed. Use the standard 20 tasks for fitness evaluation during evolution. Use the held-out set exclusively for success criterion validation.

This is free — the trap generator is already built. Use seed 42 for evolution tasks and seed 137 for held-out validation. Never let the held-out set influence selection. Report fitness on both sets in the generation logs so you can track the gap between training and held-out performance. A growing gap means overfitting to the evolution tasks.

Revise success criterion 1: beat the best forge tool's accuracy on the **held-out** trap battery, not the evolution battery.

## 9. NCD Monoculture in Seed Population

Yes, enforce diversity in the seed population. Your proposal is exactly right: top 30 by accuracy plus 20 most structurally diverse by gene composition.

To measure structural diversity, after gene extraction, represent each tool as a binary vector: which gene types does it contain? Compute pairwise Hamming distance. Select the 20 tools that maximize the minimum distance to the already-selected set (a maximin diversity criterion). This guarantees the seed population covers as much of the gene composition space as possible.

If 87% of tools share NCD as a fallback, the structural diversity selection will naturally favor the 13% that don't. Those NCD-free tools are the most valuable seeds even if they score lower on accuracy, because they represent alternative evolutionary lineages that can't converge back to NCD.

## 10. Phase 0: Parameter Evolution as Warmup

Yes. Do this. Two days of CMA-ES over the parameter vectors of the top 50 forge tools is the cheapest possible win and it validates the entire fitness evaluation pipeline.

Here's the specific value. Each forge tool has 15-25 evolvable float parameters. CMA-ES over those parameters with margin-over-NCD as the objective might push a 67% tool to 72% purely through parameter tuning. If it does, you've already beaten the baseline before structural evolution starts and you have a stronger seed population for Apollo proper.

If parameter evolution produces zero improvement, that tells you something important too — the tools are already at their parametric optimum and all future gains must come from structural recombination. Either result is informative.

The implementation is approximately 100 lines using pymoo. Run it as Phase 0 before Apollo's main loop launches. The Phase 0 output becomes the seed population for Phase 1.

Sequence: viability spike (afternoon) → Phase 0 parameter evolution (2 days) → structural evolution (37 days).

## 11. LLM Mutation

AST-only for MVP. The viability spike (question 7) determines whether this holds.

If viability is above 40%, AST works. Proceed with the plan.

If viability is below 10%, add a local StarCoder 1B as a mutation operator before launch. No API calls, no network. It runs on the card alongside the sandbox. The mutation prompt is simple: "Here is a Python method that scores reasoning. Modify it to [splice in this other scoring approach / add a self-checking step / change the parsing strategy]." The LLM produces a candidate method, AST validates it, the sandbox tests it.

The threshold for reconsidering is 10% viability. Below that, you don't have enough viable offspring per generation for selection to work. The math: 50 offspring at 10% viability = 5 viable organisms per generation. That's not a population — that's a lottery. You need at least 20 viable offspring per generation for selection to have meaningful signal, which means you need at least 40% viability at 50 offspring.

Don't pre-commit to the LLM path. Run the spike. Let the data decide.

## 12. Crossover on a Directed Graph

Your proposed algorithm is correct. Topological sort with cycle-breaking, number by topo order, single crossover point, child gets the front of parent A and the back of parent B, new wire connects A's last kept gene to B's first inherited gene.

One refinement: when cycles exist, the topological sort must break them deterministically. Use the gene with the lowest gene_id in the cycle as the break point. This makes crossover reproducible given the same parents and crossover point, which matters for debugging lineage.

If the junction wire is type-incompatible (A's last gene outputs a `float` key, B's first gene expects a `list` key), the child fails compilation and dies. This is fine. It's selection pressure toward type-compatible gene arrangements, which will naturally emerge.

## 13. Self-Referential Emergence Rate

Add the compound "duplicate-and-wire-back" operator. This doesn't violate the "let it emerge" philosophy — it violates the "let it emerge *slowly*" philosophy, which is a different thing and not worth defending on a 40-day timeline.

The compound operator doesn't guarantee self-reference helps. Selection still decides whether self-referential organisms survive. All the compound operator does is ensure the building block appears often enough for selection to evaluate it. Without it, at 3% per organism per generation, you might wait 500 generations before you have 10 self-referential organisms to compare against the non-self-referential population. With the compound operator at 10%, you have that comparison within 50 generations.

Set it at 10% alongside the other mutation operators. Log every organism that has self-referential wiring with a flag in the JSONL. Track the fitness differential between self-referential and non-self-referential organisms per generation. That curve is the primary signal you're watching for.

If self-referential organisms consistently underperform by generation 500, reduce the compound operator to 5%. If they consistently outperform, increase it to 15%. Let the data tune the rate.

## The Nemesis Grid vs Trap Battery Question

Use the held-out trap battery as the success criterion, not the Nemesis grid and not the evolution battery. The Nemesis grid is adversarial — it's a different distribution and a different difficulty level. Comparing against it conflates "did evolution improve reasoning evaluation" with "did evolution improve adversarial robustness," which are separate questions.

Post-MVP, once Apollo has produced organisms that beat the trap battery, THEN test them against the Nemesis grid as a generalization check. That's a second success criterion for a later phase: do evolved organisms generalize to adversarial tasks they never saw during evolution?

## Summary of Decisions

1. `self` → `self.params['gene_XX_param']` with parameter vectors in lineage logs
2. Auto-generate confidence from evaluate (option a)
3. Shared context dict (option b) with `_gene_trace` injection
4. Margin-over-NCD as fitness metric
5. Novelty as 3rd NSGA-II objective (option a), no decay
6. Gene deletion included at 10%
7. Run the viability spike before building anything
8. Held-out trap battery with different seed
9. Top 30 by accuracy + 20 most structurally diverse for seed population
10. Phase 0 parameter evolution as 2-day warmup
11. AST-only unless viability spike is below 10%
12. Topological sort crossover with deterministic cycle-breaking
13. Compound duplicate-and-wire-back operator at 10%
14. Success criterion targets held-out battery, not Nemesis grid

Build sequence: viability spike (afternoon) → Phase 0 parameter CMA-ES (2 days) → full structural evolution (37 days).

Review these and create another list of questions in a new file.