# Prior art checked for this design

Architect: FABLE-5.1 (seat Dionysus). Searches run 2026-10-01, about
14:58Z to 15:05Z, after the requirements freeze (a0e3a4d03).

Why this file exists. The design leans on a number of published results.
The base role asks for citations with evidence tiers, and the record shows
what happens when prior-art lists come from unlogged queries or from a
model's memory (Tityos T15). So every reference the package cites is listed
here with the query that checked it and what was checked.

What "VERIFIED" means here: a web search returned the paper, and the title,
authors and venue or identifier in the result match what I cite. I did not
read the papers in full during this session. What each paper shows is
stated from the search summary and from my prior knowledge of it, and is
marked where that matters. This is a citation check, not a literature
review. It has no recall measurement, so it supports no claim that an idea
in this design is new (requirement ANTI-06).

Tracked doctrine HARD-2 permits prior literature "as data". That is the
only use made of it here.

## References, with the query used

| # | reference | identifier | status | bears on |
|---|---|---|---|---|
| 1 | Raventos, Paul, Chen, Ganguli. Pretraining task diversity and the emergence of non-Bayesian in-context learning for regression. NeurIPS 2023. | arXiv:2306.15063 | VERIFIED | P4 transition mapper: a task-diversity threshold between memorising the training tasks and learning in context, in transformers |
| 2 | Chan, Santoro, Lampinen and others. Data distributional properties drive emergent in-context learning in transformers. NeurIPS 2022. | arXiv:2205.05055 | VERIFIED | P4: in-context against in-weights learning traded off, and depended on data statistics; reported for transformers and not for recurrent models |
| 3 | Deletang and others. Neural networks and the Chomsky hierarchy. ICLR 2023. | arXiv:2207.02098 | VERIFIED | world families with formal memory classes; 20,910 models, 15 tasks; memory structure bounds generalisation class |
| 4 | Real, Liang, So, Le. AutoML-Zero: evolving machine learning algorithms from scratch. ICML 2020. | arXiv:2003.03384 | VERIFIED | existence proof that evolution over a register-program space can find learning algorithms, with a setup/predict/learn scaffold |
| 5 | Ellis and others. DreamCoder: bootstrapping inductive program synthesis with wake-sleep library learning. PLDI 2021. | arXiv:2006.08381 | VERIFIED | the designed form of COMPOSE and RECURSE: a library that deepens and a search policy that co-adapts; the natural positive control |
| 6 | Geiger, Lu, Icard, Potts. Causal abstractions of neural networks. NeurIPS 2021. | arXiv:2106.02997 | VERIFIED | interchange interventions (CAUS-03) |
| 7 | Hampton. Rhesus monkeys know when they remember. PNAS 98(9):5359-5362, 2001. | PNAS 2001 | VERIFIED | the opt-out design behind the carrier-noise test (CAUS-07) |
| 8 | Wang and others. Alchemy: a benchmark and analysis toolkit for meta-reinforcement learning agents. 2021. | arXiv:2102.02926 | VERIFIED | a meta-learning benchmark with resampled latent causal structure and an ideal-observer analysis; agents fell short |
| 9 | Lenski, Ofria, Pennock, Adami. The evolutionary origin of complex features. Nature 423:139-144, 2003. | Nature 2003 | VERIFIED | complex functions evolved only by building on simpler rewarded functions: stepping stones (H3) |
| 10 | Dunlap, Stephens. Components of change in the evolution of learning and unlearned preference. Proc R Soc B 276, 2009. | doi:10.1098/rspb.2009.0602 | VERIFIED | experimental evolution of learning against environmental change and reliability: the timescale argument behind DEV-08 |
| 11 | Zador. A critique of pure learning and what artificial neural networks can learn from animal brains. Nature Communications, 2019. | doi:10.1038/s41467-019-11786-6 | VERIFIED | the genomic bottleneck (DEV-08) |
| 12 | Ortega and others. Meta-learning of sequential strategies. 2019. | arXiv:1905.03030 | VERIFIED | memory-based meta-learners amortise Bayes-optimal adaptation in their state dynamics: why ADAPT in fast state is the conventional case |
| 13 | Duan and others. RL^2: fast reinforcement learning via slow reinforcement learning. 2016. | arXiv:1611.02779 | VERIFIED | same; the reference arm's recurrent learner |
| 14 | Wang and others. Learning to reinforcement learn. 2016. | arXiv:1611.05763 | VERIFIED | same |
| 15 | Miconi, Clune, Stanley. Differentiable plasticity: training plastic neural networks with backpropagation. ICML 2018. | arXiv:1804.02464 | VERIFIED | PN substrate; gradient through the lifetime as an optimiser arm |
| 16 | Najarro, Risi. Meta-learning through Hebbian plasticity in random networks. NeurIPS 2020. | arXiv:2007.02686 | VERIFIED | PN substrate; evolved synapse-specific local rules that build weights during life from random starts |
| 17 | Romera-Paredes and others. Mathematical discoveries from program search with large language models. Nature, 14 December 2023. | Nature 2023 | VERIFIED | model-guided generation with an automated evaluator (P8; ANTI-01) |
| 18 | AlphaEvolve (Google DeepMind, announced 14 May 2025). | DeepMind blog | VERIFIED as an announcement; no paper identifier checked | same |
| 19 | Aguera y Arcas and others. Computational life: how well-formed, self-replicating programs emerge from simple interaction. 2024. | arXiv:2406.19108 | VERIFIED | S0 soups: self-replicators arise without a fitness function; no cognition claimed |
| 20 | Fontana, Buss. What would be conserved if "the tape were played twice"? 1994. | title and year VERIFIED; venue (PNAS 91:757-761) from memory, not confirmed by the search | PARTLY VERIFIED | function chemistry as an open arm |
| 21 | Lake, Baroni. Human-like systematic generalization through a meta-learning neural network. Nature, 2023. | Nature 2023 | VERIFIED | RECOMBINE and CHAIN: compositional generalisation as a trained-in property |
| 22 | Keysers and others. Measuring compositional generalization: a comprehensive method on realistic data. ICLR 2020. | arXiv:1912.09713 | VERIFIED | splits that hold atoms fixed and maximise compound divergence: the construction RECOMBINE needs |
| 23 | Morad and others. POPGym: benchmarking partially observable reinforcement learning. ICLR 2023. | arXiv:2303.01859 | VERIFIED | nearest existing benchmark family for HOLD; no restricted-class certificates that I know of (unchecked) |
| 24 | Osband and others. Behaviour suite for reinforcement learning. ICLR 2020. | arXiv:1908.03568 | VERIFIED | a memory-length task with a dial; same remark |
| 25 | Shalizi, Crutchfield. Computational mechanics: pattern and prediction, structure and simplicity. J Stat Phys 104:817-879, 2001. | arXiv:cond-mat/9907176 | VERIFIED | causal states as the minimal sufficient memory: the TRACK family's certificate |
| 26 | Stoudenmire, Schwab. Supervised learning with tensor networks. NeurIPS 2016. | arXiv:1605.05775 | VERIFIED | tensor-network learners; bond dimension as a capacity dial (open arm) |
| 27 | Spector, Martin, Harrington, Helmuth. Tag-based modules in genetic programming. GECCO 2011. | GECCO 2011 | VERIFIED | inexact tag reference lets modules evolve without a pre-specified architecture: the addressing affordance in ORG-03 and H4 |
| 28 | Wang, Lehman, Clune, Stanley. Paired open-ended trailblazer (POET). 2019. | arXiv:1901.01753 | VERIFIED | co-evolving worlds and agents (WLD-14); named in the North Star as a reference arm |
| 29 | Schmidhuber. PowerPlay: training an increasingly general problem solver by continually searching for the simplest still unsolvable problem. 2011. | arXiv:1112.5309 | VERIFIED | self-ordered curriculum (DEV-10) |

## What this check does and does not support

- Supports: the references exist and say roughly what the package says they
  say.
- Does not support: any statement that class-exclusion certificates, the
  scaffold-descent method, search-power curves from planted targets, or the
  payoff-times-reach model are new. I know of no work that combines them in
  this way, and that sentence is worth nothing as evidence: it is one
  model's memory with no recall measurement. OPEN_QUESTIONS.md carries a
  proper prior-art pass as a task.
- Two results are close to hypothesis H2 and should be read before the
  transition mapper is preregistered: references 1 and 2. They report, for
  transformers, a threshold between memorising and learning in context that
  depends on task diversity and data statistics. If H2 holds, it would
  extend that kind of threshold across substrates and predict its location.
  If references 1 and 2 already contain a quantitative prediction of the
  threshold, H2 is partly known and should be cited as a replication target.

## Queries, verbatim, in the order run

1. Raventos Paul Chen Ganguli "Pretraining task diversity and the emergence of non-Bayesian in-context learning for regression" arXiv
2. Deletang "Neural Networks and the Chomsky Hierarchy" arXiv 2207.02098 RNN LSTM stack tape generalization
3. Real Liang So Le "AutoML-Zero: Evolving Machine Learning Algorithms From Scratch" ICML 2020 setup predict learn evolutionary search
4. Ellis DreamCoder "wake-sleep" library learning "growing generalizable, interpretable knowledge" program induction
5. Geiger "causal abstraction" interchange intervention neural networks Potts Icard
6. Hampton 2001 "Rhesus monkeys know when they remember" PNAS opt-out prospective memory metacognition
7. Wang "Alchemy: A benchmark and analysis toolkit for meta-reinforcement learning agents" DeepMind ideal observer latent causal structure
8. Lenski Ofria Pennock Adami 2003 "The evolutionary origin of complex features" Nature Avida EQU stepping stones
9. Dunlap Stephens 2009 "Components of change in the evolution of learning and unlearned preference" Proceedings Royal Society B
10. Zador 2019 "A critique of pure learning and what artificial neural networks can learn from animal brains" genomic bottleneck Nature Communications
11. Ortega Wang et al 2019 "Meta-learning of Sequential Strategies" memory-based meta-learning Bayes-optimal amortized arXiv 1905.03030
12. Miconi Clune Stanley 2018 "Differentiable plasticity: training plastic neural networks with backpropagation" ICML; Najarro Risi 2020 "Meta-Learning through Hebbian Plasticity in Random Networks"
13. Romera-Paredes 2023 "Mathematical discoveries from program search with large language models" FunSearch Nature; AlphaEvolve 2025 DeepMind coding agent evolutionary
14. Aguera y Arcas 2024 "Computational Life: How Well-formed, Self-replicating Programs Emerge from Simple Interaction" arXiv; Fontana Buss 1994 "What would be conserved if the tape were played twice"
15. Chan Santoro Lampinen 2022 "Data Distributional Properties Drive Emergent In-Context Learning in Transformers" in-weights vs in-context
16. Lake Baroni 2023 Nature "Human-like systematic generalization through a meta-learning neural network"; Keysers 2020 "Measuring Compositional Generalization" maximum compound divergence
17. Morad "POPGym: Benchmarking Partially Observable Reinforcement Learning" ICLR 2023; Osband "Behaviour Suite for Reinforcement Learning" bsuite memory length
18. Shalizi Crutchfield 2001 "Computational Mechanics: Pattern and Prediction, Structure and Simplicity" causal states epsilon-machine statistical complexity Journal of Statistical Physics
19. Stoudenmire Schwab 2016 "Supervised Learning with Tensor Networks" matrix product state NeurIPS bond dimension
20. Spector Martin Harrington Helmuth 2011 "Tag-based modules in genetic programming" GECCO PushGP
21. Wang Lehman Clune Stanley 2019 "Paired Open-Ended Trailblazer (POET)" ; Schmidhuber "PowerPlay: Training an Increasingly General Problem Solver by Continually Searching for the Simplest Still Unsolvable Problem"
22. Duan Schulman Chen Bartlett Sutskever Abbeel 2016 "RL^2: Fast Reinforcement Learning via Slow Reinforcement Learning" arXiv 1611.02779; Wang "Learning to reinforcement learn" 1611.05763

All searches used the harness web search in standard mode. No query
returned a paper that contradicted how it is cited here.
