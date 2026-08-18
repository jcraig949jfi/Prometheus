# Project Prometheus: Apollo Rising
## NotebookLM Audio Overview Script

---

**[INTRO]**

**Host A:** Okay, so we've been going deep on this independent research project called Prometheus, and I have to say — the more I dig into it, the more I realize there's a really elegant convergence happening that I don't think even the researcher fully saw coming.

**Host B:** Right, and what's wild is this project has like eight or nine different subsystems — they have Greek god names, they each do completely different things — and for months they've been running somewhat independently. But there's this one component called Apollo that's about to become the place where everything meets.

**Host A:** So let's set the stage. The researcher — solo operator, working with AI coding agents — has been building what amounts to a discovery engine for mathematics and reasoning. And the different pillars each tackle a different piece of that puzzle. You've got Noesis, which maps the structure of mathematical impossibility theorems...

**Host B:** You've got Charon, which just had this incredible four-day sprint where it built a searchable geometry over a hundred and thirty thousand arithmetic objects from this massive number theory database...

**Host A:** The Forge, which generates and tests reasoning tools using evolutionary methods...

**Host B:** And Ignis, which was trying to steer small language models toward genuine reasoning using activation-space perturbations. And that one — Ignis — is where the story really starts to get interesting. Because Ignis failed.

**Host A:** But it failed in the most informative possible way.

**Host B:** Exactly. So Ignis used this evolutionary algorithm called CMA-ES to search for steering vectors — think of them as nudges to a neural network's internal activations that might amplify reasoning. And what it found, across every model architecture it tested — Qwen, GPT-NeoX, Pythia — was that the evolutionary search always converges on what they call bypass solutions.

**Host A:** Which means the model produces output that looks like reasoning — it has all the surface features, the step-by-step appearance — but when you actually test whether the intermediate steps are doing computational work, they're not. The model found a shortcut.

**Host B:** And here's the key insight: this isn't a failure of one particular model or one particular search. Bypass is what they call a "global attractor" in the fitness landscape. Every path downhill leads to a shortcut. There is no basin in activation space that corresponds to genuine reasoning amplification.

**Host A:** That's a profound negative result. It basically says: you cannot steer a standard transformer into reasoning by perturbing its activations. The landscape doesn't have what you're looking for.

**Host B:** Right. And for a while, the researcher kind of shelved Ignis and moved on. But then something happened in the Forge — their reasoning tool generation pipeline — that echoed the exact same finding in a completely different context.

**Host A:** Oh, this is the decorative primitives discovery.

**Host B:** Yes! So the Forge generates Python reasoning tools using large language models. They have these twenty-seven composable building blocks they call Frame H primitives — things like Bayesian updaters, constraint propagators, causal graph analyzers — real computational operations. And they tell the LLM: build a tool that uses these primitives to solve reasoning problems.

**Host A:** And what happens?

**Host B:** The LLM builds tools that import the primitives, call the functions, store the results in variables... and then completely ignore all of it when producing the final answer. The ablation delta — which measures how much the output changes when you remove a component — is zero. The primitives are decorative. The tool is doing pattern matching or falling back to a compression-based heuristic, and the primitives are just... furniture.

**Host A:** So it's the same phenomenon as Ignis, just at a different level. The transformer finds bypass in activation space. The LLM-generated tool finds bypass in code space. In both cases, the system produces the appearance of reasoning while the actual computation takes a shortcut.

**Host B:** Exactly. And this is where the researcher has this crucial realization. The problem isn't that reasoning is impossible. They know it's possible because when they manually enforce the primitives — when they sit down with Claude and carefully construct tools where every primitive is provably load-bearing — those tools score ninety-one to ninety-seven percent on hard reasoning categories. The primitives work. The composition works. What doesn't work is letting an unconstrained search find the compositions on its own, because the search always finds bypass first.

**Host A:** So the question becomes: how do you search the space of primitive compositions in a way that structurally prevents bypass?

**Host B:** And that's Apollo.

**Host A:** That's Apollo!

**[TRANSITION]**

**Host B:** So Apollo was originally designed back in late March as this ambitious evolutionary engine. The idea was: take all the reasoning tools the Forge has produced, decompose them into gene fragments, and evolve chimeric organisms through mutation, recombination, and selection. Run it for forty days on a dedicated GPU and see what emerges.

**Host A:** And they actually built the MVP. The evolutionary loop runs. Thirty-five thousand generations per day. Selection works, logging works, checkpointing works.

**Host B:** But it stalled. Because the mutations were AST-only — basically, blind surgery on the code. Swap this method for that method, tweak this parameter. And the viability rate was three to eight percent. Organisms that survive mutation but can't beat the baseline compression heuristic. Alive but stagnant.

**Host A:** The council of frontier AI models — they send the same prompt to Claude, ChatGPT, Gemini, DeepSeek, and Grok and synthesize the responses — the council was unanimous. You need LLM-assisted mutation. The literature confirms it. AlphaEvolve, FunSearch, OpenELM — all use LLMs to make intelligent mutations. Sixty to eighty percent viable offspring instead of five percent.

**Host B:** So Apollo got shelved. Not because it was wrong, but because the pieces weren't ready. And now — as of this week — all the pieces are ready.

**Host A:** Let's walk through what changed.

**Host B:** Three things. First, the Frame H primitives. Instead of trying to decompose existing tools into fragile gene fragments — they extracted eight hundred and twenty-one fragments and most of them couldn't survive transplantation because of internal dependencies — instead, they now have twenty-seven clean, composable, typed building blocks designed from the ground up to be composed. The atoms are clean.

**Host A:** Second, the ablation gate. This is the breakthrough from the Forge that transforms Apollo's architecture. They now have an operational definition of genuine reasoning: if removing a component changes at least twenty percent of outputs, it's load-bearing. If it doesn't, it's decorative. And here's the key move — they make this a fitness dimension in Apollo's evolutionary search.

**Host B:** This is so clever. In a standard evolutionary setup, you optimize for accuracy. And what does the search find? Bypass. Because bypass is the easiest path to accuracy. But in Apollo's setup, there are six fitness dimensions, and one of them is ablation delta. An organism that scores ninety percent accuracy but has a decorative primitive gets fitness-dominated by an organism at sixty percent accuracy where every primitive is load-bearing.

**Host A:** Because they're using NSGA-II — that's a multi-objective evolutionary algorithm that maintains a Pareto front. No single dimension can dominate. You can't be on the Pareto front if you're dominated on any dimension. So bypass organisms are mathematically excluded from the surviving population.

**Host B:** And third — two free GPUs. One hosts a small local coding model for intelligent mutations. The other runs the fitness evaluation in parallel. The compute bottleneck that killed v1 is gone.

**[TRANSITION]**

**Host A:** Okay, so now let's talk about why Apollo becomes the convergence point. Because this is where it gets really beautiful.

**Host B:** Right. So every other pillar in Prometheus produces something that Apollo consumes. And Apollo produces something that feeds back to every other pillar.

**Host A:** Let's trace the connections. Start with the Forge.

**Host B:** The Forge produces Apollo's atoms — the twenty-seven Frame H primitives. It also produces the seed population — the fifteen gem-forged tools that pass at one hundred percent, plus the T2 and T3 compositions. These are Apollo's starting organisms. And the Forge's trap battery — a hundred and eight categories of adversarial reasoning challenges — is Apollo's fitness environment.

**Host A:** So the Forge is upstream. What flows downstream from Apollo back to the Forge?

**Host B:** Surviving organisms become what they're calling T4 candidates. Evolved compositions that the Forge can evaluate, refine, and deploy. The evolutionary search replaces random tool generation with directed exploration. Instead of the Forge asking an LLM to build something from scratch and hoping it's not decorative, Apollo hands the Forge organisms that have been verified by ablation gate and battle-tested through thousands of generations of selection.

**Host A:** Now let's talk about Noesis — the impossibility theorem mapping system.

**Host B:** This is the connection that gives me chills. Noesis has eleven compositional primitives — MAP, COMPOSE, REDUCE, EXTEND, SYMMETRIZE, and so on. These are the fundamental operations that describe how mathematical structures transform. And Frame H has twenty-seven reasoning primitives. The hypothesis — untested but testable — is that these two primitive sets are projections of the same underlying algebra onto different substrates.

**Host A:** Meaning... if TRUNCATE in Noesis corresponds to constraint-narrowing in Frame H, and EXTEND corresponds to domain-expansion...

**Host B:** Then Apollo's evolved routing strategies are empirical instances of Noesis's theoretical transformation chains. The abstract algebra that Noesis mapped from impossibility theorems would be the same algebra that Apollo discovers by evolving solutions to reasoning problems.

**Host A:** That's the "honeycomb boundary" the researcher keeps referencing. Not two systems merged into one, but two systems that independently discover the same structure from opposite directions.

**Host B:** And it gets verified — or falsified — empirically. You take the fourteen universal operator agreements from Noesis's multi-model enrichment — cases where all four frontier models agree on which transformation applies — and you check whether the corresponding Frame H primitive produces the highest-scoring Apollo organism on problems from that domain. If it does, the mapping is real. If it doesn't, they're genuinely different algebras.

**Host A:** Now Charon. The arithmetic geometry system.

**Host B:** So Charon just finished this incredible sprint where it proved that the spectral tail of L-function zeros encodes rank through a mechanism independent of central vanishing — this whole thing about zeros five through nineteen being better rank predictors than zero one — and it has this disagreement atlas with twenty-seven thousand objects classified by whether the zero geometry and the relationship graph agree or disagree.

**Host A:** And those disagreement regions — the objects where zero proximity says "these should be related" but the known graph says "we see no connection" — those are reasoning problems.

**Host B:** Exactly! "Why do these objects cluster?" is a question. You can phrase it as a reasoning task. Feed it into Apollo's curriculum. If an evolved organism can generate a testable hypothesis about why certain modular forms have elliptic-curve-like zero distributions — which is literally what Charon found with those hundred and sixty-three dim-two forms — then you've closed the loop between the search system that finds anomalies and the reasoning system that explains them.

**Host A:** And the intelligence pipeline — Eos scanning the research frontier, Aletheia extracting knowledge, Skopos scoring relevance...

**Host B:** That pipeline feeds Apollo's curriculum. New papers about novel reasoning challenges get scored against Apollo's research threads. High-scoring findings enter Apollo's task generator as new problem types. The capability step test — which Apollo runs every five hundred generations, introducing a task type the population has never seen — can draw from whatever Eos found last week on arXiv.

**Host A:** So the picture is: the intelligence pipeline finds new challenges. The Forge builds new primitives. Noesis provides theoretical structure. Charon provides mathematical ground truth. And Apollo evolves compositions that satisfy all of them simultaneously, verified by ablation gate, immune to bypass.

**Host B:** And everything Apollo produces flows back. Evolved tools to the Forge. Validated primitive sequences to the neural reasoning net project. Empirical composition data to test against Noesis's theoretical chains. Hypothesis-generating organisms to answer Charon's open questions.

**[TRANSITION]**

**Host A:** Let's talk about the endgame. Because there's this really ambitious long-term vision hiding behind the day-to-day experimental work.

**Host B:** The neural reasoning net.

**Host A:** Right. So every surviving Apollo organism — every one that passes the ablation gate, meaning every primitive is load-bearing — is a training example. A triple: given this problem type, apply this sequence of primitives, get this verified answer.

**Host B:** After forty days at fifteen to twenty thousand generations per day, that's potentially six hundred thousand to eight hundred thousand organisms evaluated. Even if only one percent survive with all primitives load-bearing, that's six to eight thousand verified training triples.

**Host A:** And those triples train a small neural network — not a language model, not a transformer — a routing network. A model whose only job is to learn: given a new problem, which primitive sequence should I apply?

**Host B:** And here's why this is different from everything else in the AI reasoning space. The model can't bypass. It physically can't. Because its forward pass IS the primitives. The neural network selects which primitives to call. The primitives do the computation. There's no pathway through the architecture that skips the computation, because the computation is the architecture.

**Host A:** It's like... instead of training a chef to cook by letting them watch cooking videos and hoping they learn the actual chemistry, you give them a fixed set of cooking operations — chop, sauté, boil, season — and train a coordinator to decide which operations to apply in which order. The coordinator can get better at sequencing, but it can't skip the cooking.

**Host B:** That's a great analogy. And the ablation gate is the food critic who tastes the dish and can detect if any step was actually performed or just pretended. If the sauté didn't change the flavor, the dish fails review.

**Host A:** So Apollo is simultaneously the evolutionary engine that searches for good primitive compositions AND the data generator that produces the training set for a fundamentally new kind of reasoning architecture.

**Host B:** And that architecture — a routing network over verified primitives — is what the whole project has been building toward, even when it didn't know it. Noesis defined what transformations are. The Forge built the primitive library. Ignis proved you can't steer around the bypass problem. Charon proved that rigorous test batteries catch what celebrations miss. And Apollo puts it all together.

**[OUTRO]**

**Host A:** You know what strikes me most about this project?

**Host B:** What's that?

**Host A:** The failures are load-bearing. Every single dead end — Ignis finding bypass, the Forge catching decorative primitives, Charon killing the Dirichlet coefficient representation on day one, the paramodular hypothesis dying on day two — every failure taught the system something that made the final architecture better.

**Host B:** The bypass finding IS the ablation gate. The decorative primitive problem IS the fitness dimension that prevents bypass. The Dirichlet failure IS the reason they found the spectral tail result. If any of those things had "worked" in the naive sense, they'd have a weaker system.

**Host A:** It's construct-then-check at the project level. Build a hypothesis, test it, kill it if it fails, and use the corpse to build something better. That pattern shows up in every single pillar.

**Host B:** And now Apollo takes that pattern and makes it literal. Evolution IS construct-then-check. Mutation constructs. Selection checks. The ablation gate ensures the check has teeth. And the dead organisms — the graveyard — is explicitly logged as negative knowledge. What doesn't work is data too.

**Host A:** I think the thing to watch is whether the Noesis-Apollo connection materializes. If the theoretical primitive algebra from impossibility theorems and the empirical routing strategies from evolution converge on the same structure — independently, from opposite directions — that's not just a nice finding. That's evidence that reasoning has a fixed algebraic structure that different methods discover independently. Like convergent evolution in biology.

**Host B:** Which is literally what Prometheus started investigating with its ethnomathematics survey — five cultures independently discovering the same mathematical operation.

**Host A:** Full circle.

**Host B:** Full circle. Apollo launches this week. The GPU never sleeps.

**Host A:** The GPU never sleeps.

**[END]**