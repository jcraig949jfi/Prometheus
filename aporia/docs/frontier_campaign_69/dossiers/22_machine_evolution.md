# Prompt 22: Machine Evolution

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdpVXVmYXFpREdfYWI5TW9QanN6eG1RcxIXaVV1ZmFxaURHX2FiOU1vUGpzenhtUXM
**Elapsed:** 334s

---

# FRONTIER PRACTITIONER DOSSIER: MACHINE EVOLUTION

Key Points:
* The field of Machine Evolution has bifurcated. Traditional node-and-weight topology evolution (like NEAT) has largely hit a scaling wall and been absorbed into niche control theory applications.
* The frontier is now defined by two massive paradigm shifts: hardware-accelerated massive parallelization using JAX, and the use of Large Language Models as intelligent mutation and crossover operators.
* To run frontier experiments today, a practitioner must master vectorized environment simulations on TPUs/GPUs and engineer pipelines where LLMs iteratively rewrite code, prompts, or reward functions.
* The computational bottleneck has shifted from physics engine CPU cycles to GPU memory bounds and LLM API rate limits.

The intersection of evolutionary computation and deep learning is undergoing a renaissance. For decades, the field was defined by algorithms that slowly grew neural network structures or perturbed connection weights, evaluating each individual in a population sequentially on a CPU. This approach yielded fascinating results in artificial life and simple control tasks but was utterly eclipsed by the efficiency of gradient descent for training large, fixed-topology networks. Today, the field has been resurrected by recognizing that evolution is an algorithm of massive parallelism and discrete search. By running thousands of environments simultaneously on modern accelerators, and by replacing blind random mutations with the semantic intuition of language models, evolutionary algorithms are now solving problems that gradient descent cannot touch: discrete prompt optimization, automated reward function design, and open-ended code generation. 

Treating you as a competent computational scientist ready to build in this space, this dossier strips away the theoretical padding and focuses on the stack, the code, the unresolved tensions, and the tacit knowledge required to push the frontier in 2026.

## PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Machine Evolution today is fundamentally about bypassing the limitations of gradient descent in discrete, non-differentiable, or open-ended search spaces. The field has largely split from its biological mimicry roots and is now driven by computational pragmatism. In one or two paragraphs, the current reality is this: traditional Neuroevolution, where algorithms painstakingly add nodes and connections to a minimal network genome, is effectively a dormant subfield. It has been absorbed into the broader category of Neural Architecture Search, and in the merge, the field lost its focus on emergent complexity in favor of marginal accuracy gains on image classifiers. The true spiritual successor to early Machine Evolution lives at the intersection of Quality-Diversity algorithms, JAX-based hardware acceleration, and Large Language Models acting as genetic operators.

What is SETTLED:
Hardware acceleration is mandatory. Running population-based evolutionary algorithms on CPU clusters is dead. If your environment and evolutionary loop are not written in JAX (or equivalently compiled to GPU/TPU), you are operating at least three orders of magnitude too slowly (cite: 16, 40). Second, the superiority of Quality-Diversity (illuminating a search space to find many diverse, high-performing solutions) over pure objective-driven optimization is settled (cite: 29). Single-objective evolution collapses into local optima too easily.

What is CONTESTED:
The role of the Large Language Model in the evolutionary loop is fiercely debated. One camp, represented by the Evolution through Large Models programme, argues that LLMs should directly mutate the code of the agents or the artifacts themselves, acting as an intelligent crossover mechanism (cite: 51, 54). Another camp, represented by the Eureka programme, argues that LLMs are too slow and expensive to be inside the agent's action loop; instead, the LLM should evolve the reward function, while standard reinforcement learning trains the actual agent (cite: 31, 32). A third camp argues that evolution should be used to optimize the LLMs' own reasoning prompts in a self-referential loop, creating a meta-learning system (cite: 41, 1). 

What is OPEN:
The total automation of the evolutionary pipeline remains open. Currently, humans must still write the domain-specific mutation prompts, define the behavioral descriptors for Quality-Diversity grids, and manually verify that LLM-generated code does not exploit physics engine bugs. Closing this loop to achieve true, open-ended, self-improving machine evolution without human oversight is the defining challenge of the next three years.

## PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Kenneth O. Stanley and Risto Miikkulainen
Year: 2002
Title: Evolving Neural Networks through Augmenting Topologies
Venue: Evolutionary Computation
Identifier: DOI 10.1162/106365602320169811
Why you must read it: This is the anchor method you referenced. It defines the grammar of historical markings, speciation, and complexification from a minimal starting point (cite: 46, 48). While you will not use it to train vision models today, you must understand its mechanisms because every modern structural evolution paper defines itself in reaction to NEAT.

Authors: Jean-Baptiste Mouret and Jeff Clune
Year: 2015
Title: Illuminating search spaces by mapping elites
Venue: arXiv
Identifier: arXiv:1504.04909
Why you must read it: This introduces MAP-Elites, the algorithm that shifted the field from "finding the best solution" to "finding the best solution for every possible combination of features." (cite: 29). It is the backbone of all modern Quality-Diversity research.

CURRENT SOURCES AT THE FRONTIER

Authors: Yujin Tang, Yingtao Tian, David Ha
Year: 2022
Title: EvoJAX: Hardware-Accelerated Neuroevolution
Venue: GECCO 2022
Identifier: arXiv:2202.05008
Why you must read it: This paper is the watershed moment separating modern neuroevolution from the past (cite: 16, 40). By proving that the algorithm, the policy, and the task can all be compiled in JAX to run entirely on accelerators, it drops iteration times from days on CPU clusters to minutes on a single GPU.

Authors: Bryan Lim, Maxime Allard, Luca Grillotti, Antoine Cully
Year: 2022
Title: Accelerated Quality-Diversity for Robotics through Massive Parallelism
Venue: arXiv
Identifier: arXiv:2202.06991
Why you must read it: This is the conceptual foundation for QDax. It demonstrates how to combine the illumination of MAP-Elites with hardware acceleration, establishing the standard for how diverse populations of controllers are evaluated today.

Authors: Joel Lehman, Jonathan Gordon, Shawn Jain, Kamal Ndousse, Cathy Yeh, Kenneth O. Stanley
Year: 2022
Title: Evolution through Large Models
Venue: Handbook of Evolutionary Machine Learning
Identifier: arXiv:2206.08896
Why you must read it: This paper bridges language models and genetic programming (cite: 51, 54). It proves that LLMs trained on code are the ultimate mutation operators, because they understand the semantics of what human programmers would change, side-stepping the fragility of random syntax mutation.

Authors: Chrisantha Fernando, Dylan Banarse, Henryk Michalewski, Simon Osindero, Tim Rocktaschel
Year: 2023
Title: Promptbreeder: Self-Referential Self-Improvement Via Prompt Evolution
Venue: arXiv
Identifier: arXiv:2309.16797
Why you must read it: Shows how evolutionary algorithms can operate entirely in text space. Crucially, it evolves both the task prompts and the mutation prompts simultaneously, creating a self-referential improvement loop (cite: 41, 42). 

Authors: Qingyan Guo, Rui Wang, Junliang Guo, Bei Li, Kaitao Song, Xu Tan, Guoqing Liu, Jiang Bian, Yujiu Yang
Year: 2023
Title: EvoPrompt: Connecting LLMs with Evolutionary Algorithms Yields Powerful Prompt Optimizers
Venue: arXiv
Identifier: arXiv:2309.08532
Why you must read it: An alternative to Promptbreeder that maps traditional algorithms like Differential Evolution and Genetic Algorithms directly onto discrete language tasks (cite: 1, 2). It proves that classic continuous-space evolutionary math can be simulated via LLM text generation.

Authors: Yecheng Jason Ma, William Liang, Guanzhi Wang, De-An Huang, Osbert Bastani, Dinesh Jayaraman, Yuke Zhu, Linxi Fan, Anima Anandkumar
Year: 2023
Title: Eureka: Human-Level Reward Design via Coding Large Language Models
Venue: ICLR 2024
Identifier: arXiv:2310.12931
Why you must read it: The most impressive application of evolutionary search in modern robotics (cite: 31, 32). Instead of evolving the neural network, Eureka uses an LLM to evolve the reward function code in Python, evaluates it by training an RL agent, and reflects on the logs to mutate better rewards.

## PART 3. SOFTWARE I CAN ACTUALLY RUN

neat-python
https://github.com/codereclaimers/neat-python
Implementation: Python
Licence: 3-clause BSD
Recent Activity: 2023
Maturity: DORMANT
Experiment: You can run the classic XOR solver or simple OpenAI Gym cart-pole tasks. It perfectly replicates the 2002 NEAT paper (cite: 11, 14).
Gotchas: It relies heavily on standard Python objects and sequential evaluation. It is highly educational but entirely useless for modern scale. Published results on anything larger than a toy environment will not reproduce simply because it takes too long to run.

NEAT C++
https://github.com/unibe-cns/NEAT
Implementation: C++
Licence: Apache 2.0 (historically GPL)
Recent Activity: 2021
Maturity: DORMANT
Experiment: The original reference implementation by Kenneth Stanley, wrapped and updated over the years (cite: 22, 50). Can run double pole balancing.
Gotchas: The canonical implementation is brittle on modern toolchains without containerization. The community largely abandoned this for neat-python for teaching, and JAX for research.

EvoJAX
https://github.com/google/evojax
Implementation: Python (JAX)
Licence: Apache 2.0
Recent Activity: 2025
Maturity: MAINTAINED
Experiment: Training a ConvNet on MNIST to 98 percent accuracy in 5 minutes on a single GPU, or evolving a continuous control policy for the Brax locomotion tasks (cite: 16, 36, 40).
Gotchas: Requires deep familiarity with JAX's functional programming constraints. If you accidentally trigger CPU-GPU memory transfers within the evolutionary loop, your performance will silently degrade by orders of magnitude. Many environments require custom rewrites to be strictly vectorized.

QDax
https://github.com/adaptive-intelligent-robotics/qdax
Implementation: Python (JAX)
Licence: MIT
Recent Activity: 2024
Maturity: MAINTAINED
Experiment: Running Policy-Gradient Assisted MAP-Elites on Brax environments to generate an archive of thousands of diverse, walking robotic gaits in minutes (cite: 6, 8, 9).
Gotchas: It is a framework for Quality-Diversity, not a generalized optimization library. You must be able to mathematically define the behavioral descriptors of your environment, which can be non-trivial for custom tasks.

Eureka
https://github.com/eureka-research/eureka
Implementation: Python
Licence: MIT
Recent Activity: 2024
Maturity: MAINTAINED
Experiment: Evolving a reward function for the Isaac Gym shadow hand to perform dexterous pen-spinning (cite: 33, 35).
Gotchas: Heavy reliance on the OpenAI GPT-4 API. Replicating the paper requires extensive compute for the inner reinforcement learning loop (which uses Isaac Gym) and a non-trivial budget for API calls. If the API model changes, the exact evolutionary trajectory is unreproducible.

Promptbreeder (Community Implementations)
https://github.com/shivamsuchak/Promptbreeder
https://github.com/vaughanlove/PromptBreeder
Implementation: Python
Licence: MIT
Recent Activity: 2023
Maturity: ABANDONED (or highly brittle)
Experiment: Evolving zero-shot prompts for solving the GSM8K math word problem dataset (cite: 73, 75).
Gotchas: DeepMind never released the official Promptbreeder code. These community implementations are valiant efforts but suffer from hardcoded dependencies on specific API versions (like Cohere or older OpenAI endpoints). They are starting points for your own code, not drop-in tools.

OpenELM
https://github.com/CarperAI/OpenELM
Implementation: Python
Licence: MIT
Recent Activity: 2023
Maturity: DORMANT
Experiment: Evolving Python code to generate functional 2D ambulatory robots in a simulated Sodarace environment (cite: 55).
Gotchas: Designed during the transition period of open-source LLMs. It works, but the diff models and mutation logic are tuned for older models. You will likely need to gut the model interface and replace it with a modern vLLM backend.

## PART 4. DATA AND BENCHMARKS

Brax
Access route: https://github.com/google/brax
Size: Lightweight physics engine, environments are procedurally generated.
Licence: Apache 2.0
Used to measure: The speed and convergence of hardware-accelerated evolutionary policies in continuous control (locomotion).
Authoritative status: Highly authoritative. It is the de facto standard replacing MuJoCo for population-based methods because the physics step is written in JAX.

Sodarace (via OpenELM)
Access route: Integrated into OpenELM repository.
Size: Lightweight 2D physics environments.
Licence: MIT
Used to measure: The capability of an LLM to evolve functional code (Python scripts that define springs and masses) rather than just text.
Authoritative status: Niche, but load-bearing for the Evolution through Large Models (ELM) subfield.

Isaac Gym (NVIDIA)
Access route: NVIDIA Developer program.
Size: Heavyweight 3D physics simulator.
Licence: Proprietary / Restricted academic use.
Used to measure: Complex dexterous manipulation, used heavily by Eureka to validate evolved reward functions.
Authoritative status: Authoritative for robotic control tasks. Contamination is rare because the environments are strictly physical simulations.

GSM8K (Grade School Math 8K)
Access route: HuggingFace Datasets.
Size: 8,500 high-quality grade school math problems.
Licence: MIT
Used to measure: Reasoning capabilities of evolved prompts (as seen in Promptbreeder and EvoPrompt).
Authoritative status: Popular, but suffering from massive saturation and contamination. Almost all modern LLMs have ingested this dataset during pre-training. Any evolutionary prompt method tested here must be scrutinized to ensure the LLM isn't simply recalling the answer.

BIG-Bench Hard (BBH)
Access route: HuggingFace Datasets.
Size: 23 challenging tasks requiring multi-step reasoning.
Licence: Apache 2.0
Used to measure: Generalization of prompt evolution frameworks across diverse linguistic and logical tasks (cite: 1, 2).
Authoritative status: Highly authoritative for current prompt engineering research, less prone to direct memorization than GSM8K.

Kheperax
Access route: https://github.com/qdax-project/kheperax
Size: Small library of 2D maze navigation tasks.
Licence: MIT
Used to measure: Exploration capabilities of Quality-Diversity algorithms.
Authoritative status: Merely popular, largely a sanity-check benchmark to ensure an algorithm isn't failing on simple non-convex search spaces before moving to Brax.

## PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment that validates the modern field is running the MAP-Elites algorithm on the Brax Walker environment using QDax. This proves the transition from sequential CPU evaluation to massively parallel GPU evolution.

Exact Software and Version:
Python 3.10
JAX 0.4.13 (with CUDA 11.8 support)
Brax 0.9.1
QDax 0.2.3 (install via pip install qdax) (cite: 10).

Dataset/Generator:
The Brax "walker2d" environment. No external dataset is required; the environment generates states dynamically.

Parameters:
Algorithm: MAP-Elites
Population (Batch) Size: 2048
Grid resolution (Number of niches): 1024
Emitter type: MixingEmitter (Crossover and Mutation)
Mutation standard deviation: 0.05
Number of iterations: 2000
Episode length: 1000 steps

Replicates and Seeding:
Run 5 independent replicates. Seed with JAX PRNG keys using integer seeds 42 through 46.

Compute Cost:
Approximately 0.5 to 1 GPU hour on a single NVIDIA A100 or V100 GPU.

Expected Result:
At the end of 2000 iterations, the archive should contain over 800 distinct walking gaits (niches filled). The maximum fitness (return) should reach approximately 3500 to 4000.
Citation for baseline comparison: Lim et al. (2022), "Accelerated Quality-Diversity for Robotics through Massive Parallelism", Figure 4 (Performance on Brax Walker).

The three most common ways people get this experiment wrong:
1. Compiling the environment incorrectly. If a user passes Python control flow (like a standard if-statement) into the JAX `jit` compiler instead of using `jax.lax.cond`, the compiler will silently unroll the loop, causing memory to explode, or it will throw a tracer error.
2. Under-sizing the batch. JAX incurs an overhead when dispatching to the GPU. If the population size is set to 50 (typical for old CPU-based NEAT), the GPU will starve. The batch size must be in the thousands to amortize the JAX overhead.
3. Memory leaks from saving the repertoire. In QDax, the repertoire of elites grows. If you pull the entire repertoire back to the host CPU as standard NumPy arrays inside the main training loop without asynchronous dispatch, the host-to-device transfer will completely choke the training speed.

## PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you are entering this field today, the most glaring gap is the lack of an integrated framework that bridges massive JAX-based parallel evaluation (like EvoJAX) with LLM-based structural mutation (like ELM or Promptbreeder). Currently, researchers duct-tape these together. 

What you must build: The LLM-to-JAX Evolutionary Bridge.

Interface Details:
What goes in: A population of vectorized genomes (these could be strings of code, discrete prompts, or flattened network weights), and an array of fitness scores and behavioral descriptors returned from a JAX-accelerated simulation environment.
What comes out: A new population of genomes, generated by batch-prompting a local LLM or an API, ready to be pushed back into the JAX environment.

The Hard Part:
Impedance matching. JAX is strictly typed, statically sized, and demands fixed tensor dimensions. LLMs output variable-length strings, make syntax errors, and suffer from high latency. You must build a translation layer that takes variable-length LLM outputs, parses them, throws away invalid mutations without crashing the batch, and pads the successful mutations into fixed-size JAX tensors so they can be compiled and evaluated in parallel. 

Roughly how much work it is:
Three to four months of engineering for a competent computational scientist. You will spend most of this time writing custom JAX `vmap` (vectorizing) wrappers to handle the padding and masking of the generated policies.

Rebuilt Privately:
Both the original DeepMind Promptbreeder team and the authors of EvoPrompt have rebuilt their own private versions of this loop. The CarperAI OpenELM team built a rudimentary version, but it is not optimized for high-frequency environment loops. The fact that no public, optimized, drop-in library exists for "LLM as a mutation operator over simulated environments" is the strongest signal of a real gap.

## PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

What did not work: Evolving Deep Neural Network Topologies.
For years, the field attempted to scale NEAT to deep learning. Methods like HyperNEAT (which evolved CPPNs to paint weights across a substrate) and CoDeepNEAT attempted to evolve convolutional architectures. While technically successful on small datasets, they ultimately lost to differentiable architecture search (DARTS) and the brute force scaling of Transformers. The lesson learned is that evolutionary algorithms are catastrophically inefficient at finding gradient slopes. Using evolution to grow a network node-by-node to millions of parameters is a failed programme. Evolution should only be used where gradients do not exist.

Retracted or Corrected Results:
In the early days of novelty search, there were claims that "abandoning objectives entirely" was universally superior to objective-based search. This was later corrected by the community (and the original authors). Pure novelty search often behaves like a random walk in unbounded spaces. It was corrected by blending the two, resulting in Quality-Diversity (MAP-Elites), which searches for novel behaviors but optimizes for fitness locally within those behaviors.

Claims that failed to replicate:
Several early papers on evolving prompts with LLMs claimed massive performance gains over Chain-of-Thought. Independent reproduction later showed these methods were often overfitting to the exact validation set used in the evolutionary loop. When the evolved, highly idiosyncratic prompts were tested on held-out tasks from the same domain, they fell apart. The prompts had evolved to exploit statistical artifacts of the validation set rather than capturing genuine reasoning structures.

The Standing Critiques:
1. The API Dependency Critique. Made loudly by open-source advocates, this critique points out that methods like Eureka and Promptbreeder rely on closed APIs (GPT-4) (cite: 32). Because the model weights and training data of GPT-4 change silently, an experiment run in January 2024 cannot be replicated in 2026. This critique remains unanswered by the originating labs, who simply accept it as the cost of doing business. The only answer is to run these experiments on locally hosted models (e.g., Llama 3), but the reasoning degradation often breaks the evolutionary loop.
2. The Hallucinated Reward Critique. In the Eureka paradigm, LLMs write reward functions. Critics point out that RL agents are notorious reward hackers. If the LLM writes a reward function with a physics loophole, the RL agent will find it and exploit it, leading to a high "fitness" score for a totally degenerate behavior. Eureka answered this by introducing automated "reward reflection," where the LLM reads the training logs to spot and penalize hacking, but it is an arms race that the RL agent often wins in long horizons.
3. The Behavioral Descriptor Bottleneck. MAP-Elites and QDax require a human to define the axes of the grid (e.g., "leg contact time" vs "torso height"). Critics argue this defeats the point of open-ended evolution because the human biases the discovery space. This critique has been partially answered by using Unsupervised Quality Diversity (e.g., using autoencoders to discover the grid axes dynamically), but those methods are notoriously unstable.

## PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the tacit knowledge outlined above, a well-resourced newcomer should abandon traditional weight-and-topology neuroevolution entirely. You should operate exclusively at the intersection of JAX-accelerated environments and LLM-driven semantic mutation.

Experiment 1 (Rank 1): Co-Evolving Task Environments and LLM Prompts.
What to do: Use an LLM to generate code for a continuous control environment in Brax. Simultaneously, evolve discrete text prompts for an LLM-based agent tasked with solving that environment. Use Quality-Diversity to maintain an archive of both novel environments and successful agent prompts.
Why it is feasible now: JAX allows the environment code to be evaluated instantly, and modern open-source LLMs (like Llama 3) can be batched efficiently using vLLM to serve as both the environment generator and the agent.
What it measures: The capacity for open-ended curriculum generation without human intervention.
Falsification: If the system loops endlessly through trivial variations of the same environment, or if the prompts degenerate into nonsensical strings that only work on one specific random seed, the hypothesis that LLMs can drive open-ended co-evolution is falsified.

Experiment 2 (Rank 2): Evolutionary Alignment (Gradient-Free RLHF).
What to do: Replicate the Eureka methodology, but apply it to language model safety rather than robotic dexterity. Use a highly capable LLM as the mutation operator to evolve the system prompt (or reward model) of a smaller, local LLM. The fitness function is a JAX-accelerated evaluation of the smaller LLM's outputs against a safety benchmark.
Why it is feasible now: The release of highly capable open weights models means you can run the "inner loop" (the agent being evaluated) extremely fast locally, reserving the heavy API calls only for the "outer loop" (the mutation operator).
What it measures: Whether discrete prompt evolution can achieve the same alignment performance as DPO (Direct Preference Optimization) or RLHF, without requiring access to the model's weights.
Falsification: If the evolved prompts fail to generalize to adversarial inputs not seen during the evolutionary loop, the method is merely memorizing the training set.

What will NOT work, and why:
Do not attempt to build a system that uses an LLM to evolve the architecture of a deep neural network (e.g., deciding where to place attention heads or convolution layers, like a modern NEAT). This will not work. The search space of modern architectures is too flat and too vast for discrete mutation to navigate efficiently, and evaluating each mutation requires running a full forward/backward pass over large datasets. The compute cost will bankrupt the project before you reach the first generation's evaluation, and standard neural architecture search (NAS) via gradient descent will beat you by miles. Stay in the realm where gradients cannot flow: code generation, discrete text, and programmatic reward functions.
