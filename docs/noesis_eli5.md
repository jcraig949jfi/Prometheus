# What Is James Working On? — Noesis Explained

## The Big Idea

Imagine you have a giant box of LEGO bricks, but instead of normal bricks, each one is a **math operation** — one brick calculates averages, another finds prime numbers, another does signal processing, another measures chaos. You have **555 of these special bricks**.

Now here's the question: **what happens when you snap them together?** If you connect the "find prime numbers" brick to the "measure chaos" brick, does the result tell you something cool that neither brick could tell you alone? That's what Noesis is trying to find out — by trying *millions* of combinations and keeping the ones that produce something surprising and useful.

The tricky part is that most combinations don't work. It's like trying to plug a round LEGO into a square hole — the math types don't match. And even when they do fit together, most combinations produce boring junk (just zeros, or infinity, or nonsense). **The rare ones that actually produce something interesting are called "cracks"** — like finding a crack in a wall that lets you peek into a room you didn't know existed.

## How It Works

James built a system that runs **27 different search strategies** at the same time, like 27 scouts sent into a dark forest, each with a different method for finding treasure. One scout picks paths randomly. Another always follows the most promising-looking trail. Another deliberately goes where nobody else has gone yet. They all report back, and the system gives **more resources to the scouts who are finding the most cracks** and fewer to the ones who aren't finding anything.

There's also a **"quality judge"** that scores every combination on seven different criteria — did it actually run without crashing? Is the output novel (never seen before)? Does it compress information (find hidden patterns)? Is it connecting different fields of math (like topology to statistics)? The combination of all seven scores determines whether something counts as a "crack."

## The Dream Result

The ultimate prize would be if the system discovers — completely on its own, without being told — a two-step combination where **one operation builds something and a second operation checks or fixes the first one's work**. This is like if your LEGO robot independently invented quality control. James has seen this "construct-then-check" pattern show up in other parts of his research, and if the search engine rediscovers it from scratch, that's a huge deal.

## Early Results

The system is already working! In the first 30 minutes it was finding **23 cracks per minute** and discovered combinations nobody would have thought to try — like connecting a topology measurement (the shape of a surface) to a statistics function (error curves). Five different AI advisors reviewed the early data and all agreed: the core idea is working, the search space has real structure, and the system is showing genuine evolutionary dynamics — meaning it's not just randomly stumbling, it's actually *learning* which regions of the space are productive.

---

## The 27 Search Strategies

Each strategy is like a different philosophy for exploring the unknown. Think of it as 27 different players in a video game, each with a different playstyle, all competing to find the best loot.

| # | Strategy Name | What It Does |
|---|--------------|-------------|
| 1 | **Random Baseline** | Picks completely random type-compatible combinations. This is the "control" — every other strategy has to beat this or it's useless. Think of it as the player who just mashes buttons and sometimes gets lucky. |
| 2 | **Tensor Top-K** | Uses a big math map (the "tensor") that scores how promising each pair of operations looks based on novelty, complementarity, and type compatibility. Picks the highest-scoring pairs. Like having a treasure map that highlights the most interesting spots. |
| 3 | **Frontier Seeking** | Keeps track of which combinations have already been tried, then deliberately targets the ones in unexplored territory. It's the explorer who always walks toward the blank parts of the map. |
| 4 | **Framed Traversal** | Actually 5 sub-strategies in a trenchcoat. Each one looks at the same map through a different "lens" — one prioritizes simplicity, another prioritizes surprise, another looks for boundary effects. Like wearing different colored glasses that highlight different things. |
| 5 | **Epsilon-Greedy** | 80% of the time it picks the best-known option (exploit), 20% of the time it picks randomly (explore). Simple but classic — it's the player who mostly farms the best dungeon but occasionally wanders off to check a weird cave. |
| 6 | **Temperature Anneal** | Groups operations into clusters, then uses a "temperature" dial. Starts hot (exploring wildly across all clusters) and slowly cools down (focusing on the best clusters). Periodically reheats to escape ruts. Like a metal detector that starts scanning the whole beach, then gradually zeroes in on the hot spots. |
| 7 | **Island MAP-Elites** | Runs 4 separate "islands," each with its own strategy and its own collection grid. The best finds from the strongest island occasionally migrate to the weakest. Like 4 competing research labs that share their best discoveries. |
| 8 | **Failure Geometry** | Instead of ignoring failures, this strategy studies *how* things fail. A crash from number overflow at a domain boundary is interesting — it means you're near something powerful. A type mismatch is boring. This scout goes toward the interesting explosions. |
| 9 | **Novelty Seeking** | Completely ignores quality scores and only chases outputs that are *different from everything seen before*. It doesn't care if the result is good, only that it's new. The explorer who always takes the road less traveled, even if it leads nowhere. |
| 10 | **Longest Chain** | Most strategies favor short 2-step combos because they're more likely to work. This one specifically goes for 3, 4, or 5-step chains. Higher failure rate, but potentially deeper discoveries — like trying to build a longer LEGO tower when everyone else is building short ones. |
| 11 | **Bridge Building** | Finds the two most distant clusters of operations (fields of math that are furthest apart) and specifically tries to build chains connecting them. It's the diplomat who introduces strangers from opposite sides of the party. |
| 12 | **Island Reset** | Runs 4 islands and every 100 rounds, wipes the bottom 2 and replaces them with copies of the top 2's best work. Harsh but effective — it's natural selection applied to the search strategies themselves. |
| 13 | **Curiosity-Driven** | Gives a bonus to combinations that open up *new regions* of the quality map, even if the immediate result is mediocre. A mediocre result in uncharted territory is more valuable than a great result in a well-explored area. Like a game that gives you XP for discovering new map tiles. |
| 14 | **NSLC (Novelty + Local Competition)** | Combines novelty (be different!) with local quality competition (but also be good compared to your neighbors!). Prevents the collection from collapsing to one "best" region while still caring about quality. |
| 15 | **CMA-ME** | Learns the *shape* of success. Instead of random mutations, it figures out which directions of change tend to produce better results and proposes new candidates along those learned directions. Like a basketball player who learns their own shooting sweet spots. |
| 16 | **Differential Evolution** | Takes three existing good combinations (A, B, C), computes what makes A different from B, and applies that difference to C to create something new. It's analogical reasoning — "A is to B as ??? is to C." |
| 17 | **Surprise Admission** | Trains a small predictor that guesses what a combination will produce. Then it specifically looks for combinations that *violate* the prediction — results the system didn't expect. It's the strategy that seeks out "wait, that shouldn't have happened" moments. |
| 18 | **Two-Step Validation** | Directly hunts for the "dream result." Takes a good single operation, then searches for a second operation that *checks, fixes, or improves* the first one's output. This is looking for construct-then-check on purpose. |
| 19 | **Mutation** | Takes the best chain in the collection, swaps out one operation for a similar one, and tests if the result is better. Pure hill-climbing — take what works and tweak it slightly. Currently the #1 crack-finder because small improvements on known-good chains are the easiest wins. |
| 20 | **Chain-Length Annealing** | Starts by focusing on short safe chains, then gradually shifts toward longer riskier ones as the collection fills up. Build a solid foundation before reaching for the sky. |
| 21 | **Building-Block Reuse** | Scans the database for operation pairs that keep showing up in good chains — these are "building blocks." Then forces new chains to start with those proven pairs and adds a third step. It's exploiting discovered primitives — "this two-step combo keeps working, what can we add to it?" |
| 22 | **Failure-as-Feature** | When combinations crash in interesting ways (NaN, overflow), this strategy collects those operations and tries them again with *different input sizes*. An explosion at one scale might be a discovery at another. Like a chemist who notices a reaction was too violent and tries it with less reagent. |
| 23 | **Cross-Family Bridge** | Pre-calculates which organism families (groups of related operations) have *never* produced a good chain together, then specifically targets those gaps. "Topology and signal processing have never connected — let's force them to try." |
| 24 | **Hall-of-Fame Local Search** | Keeps an elite list of the 50 best chains ever found. Each round, picks one randomly and makes a tiny tweak. The simplest possible "refine what works" strategy — and often surprisingly competitive. |
| 25 | **Autoencoder Search** | Hunts for chains that compress then expand: Big → Small → Big. If the output reconstructs the input after passing through a bottleneck, the system has discovered algorithmic compression — a chain that found the essential structure in the data. |
| 26 | **Type-Coercion Bridge** | Takes a great chain, intentionally breaks one connection (wrong type), then searches for a single "bridge" operation that fixes the mismatch. Finds hidden connections between fields that the type system said were incompatible. |
| 27 | **Inspiration Crossover** | The ONLY strategy that asks an AI for help. Shows 2-3 good chains to an LLM and asks "what would combine these?" Used very sparingly (once per 100 rounds) because it's expensive. It's the outside consultant you bring in occasionally for a fresh perspective. |
