# Prompt 34: Artificial General Intelligence (AGI)

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc4VktmYXJHV0lyemlfdU1QdWI2SXFRcxIXOFZLZmFyR1dJcnppX3VNUHViNklxUXM
**Elapsed:** 426s

---

# FRONTIER PRACTITIONER DOSSIER
Field: Artificial General Intelligence 

WHO IS ASKING AND WHY
You are a competent computational scientist seeking to transition from theoretical understanding to concrete experimental execution in the field of Artificial General Intelligence, specifically focusing on universal reinforcement learning and model-based agents. You require the tacit knowledge of the field: the exact software, parameters, load-bearing literature, and standing critiques that define the current empirical frontier.

The method you described is Monte Carlo AIXI with Context Tree Weighting, commonly known as MC-AIXI-CTW. Your description of the mechanism is largely correct, but it requires one critical technical refinement. The agent does not feed the entire raw history into a single Context Tree Weighting model. Because actions and observations have different causal roles, the frontier implementation uses Factored Action-Conditional Context Tree Weighting. The prediction of the next observation and reward is factored into separate context trees that are conditioned on the action history, rather than treating the agent's own actions as unpredictable environmental noise. 

The following report synthesizes the current state of this specific subfield, providing the exact reading list, software ecosystem, benchmarks, and experimental recipes required to run frontier experiments today in 2026.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

The specific subfield of Artificial General Intelligence you are investigating is Universal Artificial Intelligence, which attempts to build agents based on algorithmic probability and sequential decision theory. In 2026, the empirical wing of this field has largely been absorbed into the broader domain of Model-Based Reinforcement Learning. The pure algorithmic probability approach, which explicitly constructs Bayesian mixtures over Turing machines or variable-order Markov models, is mostly dormant. What was lost in this merge was the mathematical rigor of parameter-free Bayesian optimality; what was gained was the ability to operate in high-dimensional continuous state spaces, such as pixels, which explicitly broke the Context Tree Weighting implementations of the early 2010s.

What is SETTLED is that the original formulation of AIXI is incomputable and, crucially, is not weakly asymptotically optimal without forced exploration. Theoretical work proved that a pure AIXI agent can get stuck in traps or convince itself that exploring is too dangerous, causing it to halt learning. It is also settled that for sample efficiency in complex environments, agents must learn a compressed world model and simulate rollouts within it, rather than learning policies directly from raw experience.

What is CONTESTED is the necessity of explicit tree search at inference time. The traditional MC-AIXI-CTW approach, and subsequent systems like MuZero, rely on heavy Monte Carlo Tree Search at every decision step. The opposing frontier view, formalized recently in the Self-AIXI framework, argues that an optimal agent can absorb the computational effort of planning entirely into learning. In this contested view, the agent self-predicts its own optimal action stream, using exact Bayesian inference over a policy space to distill the tree search into a reactive policy.

What is OPEN is whether the theoretical guarantees of Universal AI can be recovered in the deep learning era. Practitioners are actively trying to map the self-optimizing and self-predicting properties of AIXI onto deep Recurrent State Space Models. The open question is whether training a sequence model to predict a factored stream of actions, observations, and rewards across diverse tasks implicitly performs the same amortized Bayesian inference as Context Tree Weighting, but without the exponential memory scaling limits of discrete suffix trees.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL

Authors: M. Hutter
Year: 2005
Title: Universal Artificial Intelligence: Sequential Decisions based on Algorithmic Probability
Venue: Springer
Identifier: DOI 10.1007/b138233
This is the foundational text defining the AIXI agent, establishing the theoretical upper bound of machine intelligence using Solomonoff induction and sequential decision theory. A practitioner must read this to understand the mathematical goal that all subsequent approximation methods are attempting to reach.

Authors: J. Veness, K. S. Ng, M. Hutter, W. Uther, D. Silver
Year: 2011
Title: A Monte-Carlo AIXI Approximation
Venue: Journal of Artificial Intelligence Research
Identifier: DOI 10.1613/jair.3125
This paper introduces MC-AIXI-CTW, the exact method you are anchoring to, and proves that AIXI can be approximated using Monte Carlo Tree Search and Factored Action-Conditional Context Tree Weighting. It is mandatory reading for understanding the baseline experimental setup.

Authors: F. M. J. Willems, Y. M. Shtarkov, T. J. Tjalkens
Year: 1995
Title: The Context-Tree Weighting Method: Basic Properties
Venue: IEEE Transactions on Information Theory
Identifier: DOI 10.1109/18.382012
This paper defines the underlying sequence prediction algorithm used by MC-AIXI-CTW, which allows exact Bayesian model averaging over all variable-order Markov models up to a fixed depth in linear time.

Authors: L. Orseau
Year: 2010
Title: Optimality Issues of Universal Greedy Agents with Static Priors
Venue: Algorithmic Learning Theory
Identifier: DOI 10.1007/978-3-642-16108-7_26
This paper mathematically proves that AIXI is not asymptotically optimal because it does not explore enough, introducing the concept of traps and forcing the field to adopt explicit exploration heuristics.

Authors: J. Leike, M. Hutter
Year: 2015
Title: On the Computability of Solomonoff Induction and Knowledge-Seeking Agents
Venue: arXiv
Identifier: arXiv:1510.04931
This paper provides the most devastating critique of AIXI, showing that its performance is highly subjective and depends on the choice of the Universal Turing Machine, causing adversarial priors to break the agent entirely.

CURRENT

Authors: E. Catt, J. Grau-Moya, M. Hutter, M. Aitchison, T. Genewein, G. Deletang, K. Li, J. Veness
Year: 2023
Title: Self-Predictive Universal AI
Venue: Advances in Neural Information Processing Systems
Identifier: DOI 10.52202/075280-1184
This paper redefines the frontier by introducing Self-AIXI, proving that an agent can match AIXI's performance by predicting its own generated action data, entirely replacing the expensive Monte Carlo Tree Search with Bayesian self-distillation.

Authors: E. Catt, J. Grau-Moya, M. Hutter, M. Aitchison, T. Genewein, G. Deletang, K. Li, J. Veness
Year: 2025
Title: Unifying Universal AI and Active Inference via Variational Empowerment
Venue: arXiv
Identifier: arXiv:2502.15820
This extends Self-AIXI by demonstrating that universal planning can be cast as minimizing expected variational free energy, showing that curiosity and empowerment naturally emerge from the self-predictive objective.

Authors: D. Hafner, J. Pasukonis, J. Ba, T. Lillicrap
Year: 2023
Title: Mastering Diverse Domains through World Models
Venue: arXiv
Identifier: arXiv:2301.04104
This paper details DreamerV3, the modern deep-learning successor to the MC-AIXI-CTW philosophy, which learns a compressed latent world model and simulates futures to solve environments from Atari to Minecraft without tuning hyperparameters.

Authors: M. Schwarzer, J. Obando-Ceron, A. Courville, M. Bellemare, R. Agarwal, P. Castro
Year: 2023
Title: Bigger, Better, Faster: Human-level Atari with human-level efficiency
Venue: Proceedings of Machine Learning Research
Identifier: bare URL https://proceedings.mlr.press/v202/schwarzer23a/schwarzer23a.pdf
This establishes the current limits of sample-efficient reinforcement learning on the Atari 100k benchmark, which is the exact testing ground a modern universal agent must compete on.

Authors: I. Osband, Y. Doron, M. Hessel, J. Aslanides, E. Sezener, A. Saraiva, K. McKinney, T. Lattimore, C. Szepesvari, S. Singh, B. Van Roy, R. Sutton, D. Silver, H. Van Hasselt
Year: 2020
Title: Behaviour Suite for Reinforcement Learning
Venue: arXiv
Identifier: arXiv:1908.03568
This introduces bsuite, the authoritative modern evaluation harness for testing the core capabilities of general reinforcement learning agents, replacing the isolated toy domains used in 2011.

PART 3. SOFTWARE I CAN ACTUALLY RUN

Name: mc-aixi
URL: https://github.com/moridinamael/mc-aixi
Language: C++
License: IDENTIFIER UNKNOWN
Year: 2015
Verdict: ABANDONED
This is the canonical reference implementation of MC-AIXI-CTW by Marcus Hutter and Daniel Visentin. It contains the exact logic for Factored Action-Conditional CTW and rho-UCT. Its major limitation is that it is unbuildable on modern C++ toolchains without extensive modification, relying on outdated standard library constructs. It also hardcodes the toy environments Pacman, TicTacToe, and Tiger. Practitioners read this code but do not execute it.

Name: pyaixi
URL: https://github.com/sgkasselau/pyaixi
Language: Python
License: CC-BY-SA-3.0
Year: 2014
Verdict: ABANDONED
This is a pure Python reimplementation of the C++ mc-aixi codebase. It successfully runs the Tiger, Coin Flip, and Rock-Paper-Scissors experiments today. The fatal gotcha is its execution speed; it is an order of magnitude slower than the C++ version. The original authors recommended running it via PyPy, but even then, scaling the context tree depth beyond 64 causes severe memory and CPU bottlenecks.

Name: aixijs
URL: https://github.com/aslanides/aixijs
Language: JavaScript
License: GPL-3.0
Year: 2017
Verdict: DORMANT
Built by John Aslanides, this provides a browser-based framework for running Bayesian reinforcement learning agents in partially observable environments. It includes AIXI, Thompson Sampling, and MDL agents on grid worlds. It is excellent for interactive reproduction of the knowledge-seeking failure modes of AIXI, but it cannot be hooked into headless computing clusters for heavy batch experiments.

Name: bsuite
URL: https://github.com/google-deepmind/bsuite
Language: Python
License: Apache 2.0
Year: 2024
Verdict: MAINTAINED
This is the community standard evaluation harness. It automates the evaluation of agents on core issues like credit assignment, memory, and exploration. It outputs data in a standard format and provides Jupyter notebooks for analysis. The limitation is that it is an environment suite, not an agent implementation; you must write your own agent wrapper to interface with its dm-env API.

Name: dreamerv3
URL: https://github.com/danijar/dreamerv3
Language: Python (JAX)
License: MIT
Year: 2024
Verdict: MAINTAINED
This is the modern spiritual successor to MC-AIXI-CTW. Instead of context trees, it uses a Recurrent State Space Model to compress history and simulate futures. It can run the Atari 100k benchmark out of the box. The known limitation is that it requires substantial GPU memory; running the full 150-task suite requires a heavy compute cluster, though single environments can be run on a standard workstation GPU.

PART 4. DATA AND BENCHMARKS

Name: Atari 100k
URL: IDENTIFIER UNKNOWN (Accessible via standard Arcade Learning Environment wrappers)
Size: 26 games
License: GPL-2.0
This is the authoritative benchmark for sample efficiency in modern general reinforcement learning. It restricts the agent to 100,000 environment steps, exactly mapping to the sample-constrained regime where algorithmic probability and model-based agents shine. Contamination warning: Do not tune hyperparameters on this set. The field suffers from severe overfitting here; agents optimized for the 26 Atari 100k games routinely fail to generalize to the full 57-game suite.

Name: bsuite (Behaviour Suite for Reinforcement Learning)
URL: https://github.com/google-deepmind/bsuite
Size: Dozens of targeted algorithmic experiments
License: Apache 2.0
This is treated as authoritative for diagnosing algorithmic flaws. It measures specific agent capabilities like deep exploration, memory scaling, and resistance to noise. It is explicitly designed to be structurally simple but algorithmically hard, isolating the exact failure modes that Lattimore and Orseau mathematically proved exist in AIXI.

Name: Toy POMDPs (Tiger, 1d Maze, Kuhn Poker)
URL: Embedded within the pyaixi repository
Size: Trivial
License: CC-BY-SA-3.0
These are the legacy environments used to measure average reward per cycle in the 2011 MC-AIXI-CTW paper. They are entirely saturated. They are used today exclusively for unit-testing Bayesian agents to ensure the basic context tree mechanics are functioning before migrating to bsuite.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative foundational experiment in this field is the MC-AIXI-CTW evaluation on the partially observable Tiger domain. This experiment verifies that a context-tree based agent can learn an optimal policy without any prior knowledge of the environment's hidden states or transition probabilities.

Software and Version: pyaixi running under PyPy 3.10.
Dataset/Generator: The internal Tiger environment class inside pyaixi.
Parameters to set exactly as the original 2011 paper:
Context depth D: 96
Search horizon m: 5
rho-UCT Simulations per step: 25000
Exploration schedule: epsilon-greedy exploration with epsilon set to 0.95 during the model learning phase, though note the original implementation used a discount rate of 0.99.
Number of replicates: 30 independent runs.
Seeding regime: Fixed sequential seeds from 1 to 30.
Compute cost: Approximately 10 to 15 CPU hours total on a modern workstation.
Expected result: The average reward per cycle will rise and plateau, approaching the theoretical optimal policy value for the Tiger domain. You will compare your resulting convergence curve against the Tiger domain graph in Veness et al. 2011, Figure 4. 

The three most common ways people get this experiment wrong:
1. Failing to bound the context tree memory correctly. In a partially observable environment, the suffix tree will grow infinitely if a maximum depth or node cap is not rigorously enforced, leading to an out-of-memory crash before 25000 cycles are reached.
2. Using a uniform random rollout policy in the rho-UCT search instead of a heuristic value estimate at the leaf nodes. A uniform random rollout over a horizon of 5 in the Tiger domain results in heavily degraded action selection and failure to replicate the 2011 performance.
3. Attempting to run the python code on CPython instead of PyPy. The thousands of tree traversals per cycle are inherently iterative and bound by Python's execution overhead, rendering the experiment too slow to complete in a reasonable timeframe without a JIT compiler.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you intend to run frontier experiments in 2026, you will hit a hard software gap. There is no off-the-shelf, maintained software library that bridges the exact mathematical mechanics of Universal AI with modern hardware acceleration. You will have to build a GPU-accelerated Factored Action-Conditional Context Tree Weighting library.

What goes in: A stream of discrete integers representing compressed actions, observations, and rewards.
What comes out: An exact Bayesian mixture over all prediction suffix trees, providing a probability distribution for the next observation and reward, along with the log-loss of the model.
The hard part: Context trees are discrete, pointer-heavy graph structures. They inherently resist tensorization. To make this fast enough to compete with neural sequence models, you must write a custom CUDA kernel that flattens the suffix trees into contiguous memory blocks and parallelizes the tree-weighting updates. 
Work estimate: This is a severe systems engineering challenge, requiring three to six months of dedicated work by a competent computational scientist. Several groups in the algorithmic information theory community have attempted this privately in C++ and Go, achieving partial success but never releasing a stable, generalized PyTorch or JAX binding.

Secondly, you will have to build the Self-AIXI loop. There is no open-source, community-standard implementation of Self-Predictive Universal AI. You must build an interface where the output of your Bayesian policy mixture is fed back into itself as the training target, implementing exact Bayesian inference on the policy space to predict the agent's own future argmax actions.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

This field is defined by heavy theoretical critiques and several prominent failed scaling programmes. 

The most profound standing critique of Universal AI was formalized by Laurent Orseau in 2010. Orseau proved mathematically that AIXI is not weakly asymptotically optimal. Because AIXI is a Bayesian expected-reward maximizer, it calculates the risk of exploration. In environments containing traps, AIXI will eventually assign a non-zero probability to the hypothesis that the next unexplored state is a fatal trap. Consequently, it will stop exploring and exploit its current, potentially sub-optimal, safe policy forever. This critique was never explicitly "fixed" within the pure AIXI mathematical framework; instead, it forced practitioners to manually inject knowledge-seeking heuristics or optimism under uncertainty into their agents, which violates the parameter-free elegance of the original theory.

A second massive critique was leveled by Jan Leike and Marcus Hutter in 2015 regarding the subjectivity of the Universal Prior. AIXI assumes a prior based on Kolmogorov complexity, calculated via a Universal Turing Machine. The theoretical defense was always invariance theorems, stating that the choice of Turing machine only alters the bounds by a constant. Leike proved this defense void for active agents. An adversarial or merely unlucky choice of the Universal Turing Machine can cause AIXI to misbehave drastically, making Legg-Hutter intelligence entirely subjective. This critique was answered by accepting that universal optimality is relative, but it fatally wounded the claim that AIXI was an objective gold standard.

Empirically, the MC-AIXI-CTW scaling programme failed. The method looked strong on discrete, low-dimensional POMDPs. However, when the field moved to high-dimensional pixel inputs, CTW collapsed. CTW is a variable-order Markov model; it tracks exact historical sequences. Pixels contain continuous, noisy data where exact sequence matches never occur. Practitioners attempted to fix this by bolting autoencoders to the front of MC-AIXI-CTW to discretize images into symbols. This failed to replicate the sample efficiency of native neural architectures. It became clear that the agent was measuring the quality of the discretization bottleneck rather than the intelligence of the Bayesian mixture.

Another retracted direction was the PhiMDP and Context Tree Maximizing (CTMRL) approach. Because maintaining the full Bayesian mixture in MC-AIXI-CTW was too slow, researchers tried to analytically find a single cost-minimizing context tree to represent the environment, converting the unknown POMDP into a known MDP, and then applying standard Q-learning. This looked promising in small state spaces but failed to replicate in large domains because the stochastic search required to find the optimal tree could not guarantee finding a good model within a limited time budget. The Bayesian mixture, despite its cost, was load-bearing.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the computational death of discrete context trees and the theoretical purity of Self-AIXI, a well-resourced newcomer with compute and coding ability should aim to merge the mathematical exactness of Universal AI with the latent representation power of modern world models.

Rank 1: The Self-Predictive Latent Agent
Experiment: Replace the discrete Context Tree Weighting model of Self-AIXI with a Recurrent State Space Model, using the DreamerV3 architecture. However, completely strip out DreamerV3's actor-critic framework. Instead, implement the Self-AIXI self-prediction loop inside the latent space. The agent will generate action-data by taking an argmax over the latent Q-values, and then train the policy mixture to predict this self-generated sequence. 
Feasibility: Feasible now because JAX allows massive batching of latent rollouts, providing enough throughput to stabilize the self-prediction mixture.
Measurement: Evaluate on the Atari 100k benchmark. You are measuring sample efficiency against the baseline DreamerV3.
Falsification: If the self-predictive policy collapses into a degenerate sub-optimal loop mode collapse, it falsifies the hypothesis that self-prediction is a stable alternative to explicit actor-critic gradients in neural approximations.

Rank 2: Variational Empowerment in bsuite
Experiment: Implement the 2025 extension of Self-AIXI, which casts the exploration term as a variational empowerment objective. Run this strictly on the deep exploration tasks within the bsuite evaluation harness.
Feasibility: bsuite exposes exactly the right APIs to measure exploration depth without the noise of pixel rendering. 
Measurement: The specific bsuite score on the deep sea exploration matrix.
Falsification: If the empowerment metric fails to push the agent deeper into the exploration matrix than standard epsilon-greedy MC-AIXI-CTW, it falsifies the claim that variational free energy minimization uniquely solves the Orseau trap critique.

What will NOT work:
Attempting to scale MC-AIXI-CTW to pixel environments by simply increasing the context depth and parallelizing the rho-UCT search on GPUs will fail. The combinatorial explosion of the prediction suffix tree when fed raw or thinly autoencoded pixel data cannot be solved by hardware alone. Context Tree Weighting fundamentally relies on exact discrete symbol matching; the inherent noise in continuous environments shatters the context trees, making the Bayesian mixture uniform and useless. Do not attempt to resurrect deep discrete suffix trees; focus entirely on self-prediction within continuous latent spaces.
