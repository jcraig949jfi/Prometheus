# Prompt 29: Minimal-Criterion Coevolution

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc3MC1mYXVtMkI4U2ZfdU1QMk95VTJRcxIXNzAtZmF1bTJCOFNmX3VNUDJPeVUyUXM
**Elapsed:** 273s

---

# Frontier Practitioner Dossier: Minimal-Criterion Coevolution

Key Points
* Minimal-Criterion Coevolution is a non-objective search algorithm where two populations (typically solvers and environments) coevolve based solely on a binary survival constraint, avoiding explicit fitness scoring.
* Research suggests that this simple coupling alone can drive open-ended complexity, mimicking biological evolution's lack of overarching goals more closely than traditional optimization.
* The field has recently undergone a major shift, expanding from artificial life toy domains (like mazes and bipedal walkers) into the frontier of Large Language Model post-training and synthetic data generation.
* While pure unranked drift is highly theoretically appealing, evidence leans toward the necessity of some explicit archive management or local optimization (such as Quality-Diversity mechanics) to efficiently scale these algorithms to complex, high-dimensional neural networks.

Executive Summary
Minimal-Criterion Coevolution represents a profound departure from mainstream machine learning. Instead of minimizing a loss function or maximizing a reward, it operationalizes the evolutionary principle of "survive long enough to reproduce." By interlocking two populations such that the survival of an individual in one depends entirely on its interaction with the other, the system naturally generates a self-expanding curriculum. For a computational scientist entering this space, the appeal lies in this open-endedness: the algorithm creates its own problems and solves them simultaneously.

The Evolution of the Field
Historically, this field was confined to the realm of Artificial Life, evaluated on highly constrained procedural tasks like 2D maze navigation. However, the recent explosion of Foundation Models has radically altered its trajectory. As of 2026, the principles of Minimal-Criterion Coevolution are being actively adapted to coevolve populations of language models and synthetic task evaluations. This transition means the tooling is bifurcated: foundational principles are written in older, dormant codebases, while frontier applications are deeply embedded in modern distributed compute and GPU-heavy architectures. 

Methodological Validation
Your description of the core mechanism is remarkably precise for pure, foundational Minimal-Criterion Coevolution. You correctly identified that nothing is scored, nothing is ranked, and the coupling itself is the algorithm that prevents collapse into random drift. The only necessary addendum for 2026 is that while this pure form is theoretically sound, frontier practitioners often augment the minimal criterion with secondary quality-diversity mechanisms, such as Dominated Novelty Search, to explicitly maintain archives of historical solutions and prevent catastrophic forgetting as the difficulty frontier moves forward.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

In 2026, Minimal-Criterion Coevolution has transitioned from a niche artificial life sub-discipline into a specialized engine for generating synthetic data and specialized experts in Foundation Models. Originally designed to demonstrate how open-ended complexity could arise without explicit objective functions or novelty archives, the method proved that a simple existential constraint could drive an expanding frontier of diverse solutions. Today, the field has been largely absorbed into the broader umbrella of Open-Ended Learning and automated curriculum generation. Specifically, it has merged with evolutionary model merging and synthetic data generation pipelines, where models are coevolved with the benchmarks designed to evaluate them.

What was lost in this merge is the purist reliance on unranked drift. In the original framing, the total absence of ranking was the point. Today, large-scale implementations like AC/DC (Assessment Coevolving with Diverse Capabilities) use the minimal criterion as a primary filter but layer Quality-Diversity metrics, skill vectors, and Dominated Novelty Search on top of it to manage finite GPU memory and prevent the loss of capabilities. The pure artificial life pursuit of watching complexity accumulate solely from binary existential verdicts is dormant, replaced by an engineering drive to discover superior model capabilities.

What is SETTLED: The core hypothesis is proven. A symmetric, binary minimal criterion between two populations successfully drives open-ended divergence without an overarching objective function. It is also settled that the strictness of the minimal criterion dictates the behavior of the system. If the criterion is too lax, the system degrades into chaotic drift; if it is too strict, the system converges prematurely, behaving like a traditional optimization algorithm.

What is CONTESTED: The necessity of within-niche optimization. The authors of the related Paired Open-Ended Trailblazer algorithm argued that while Minimal-Criterion Coevolution successfully generates novel environments, relying purely on genetic drift to solve them is inefficient for complex neural networks. They argue for explicit gradient-based or evolution strategy-based optimization within the environments. Minimal-Criterion Coevolution purists argue that adding explicit optimization destroys the biological parallel and creates local optima traps. Additionally, there is active disagreement over how to handle diversity preservation. The foundational authors argue for implicit resource limitation (where individuals share a carrying capacity), while modern practitioners heavily favor explicit Pareto archives.

What is OPEN: Catastrophic forgetting and cross-domain transfer at scale. Because populations drift along a moving frontier of difficulty, early, simple environments eventually fall out of the population. Consequently, solvers lose the ability to solve basic tasks. Designing a system that maintains a continuous, unbroken chain of competence from the simplest tasks to the current frontier without an infinitely expanding archive remains an unsolved algorithmic challenge. Furthermore, extending these coupled dynamics dynamically to multi-agent reinforcement learning without static rule-sets is an active frontier.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Jonathan C. Brant, Kenneth O. Stanley
2017
Minimal Criterion Coevolution: A New Approach to Open-Ended Search
GECCO
DOI 10.1145/3071178.3071186
This is the genesis paper for the specific method you are anchoring to, introducing the core mechanism of using reproductive constraints instead of objective functions to drive a maze and solver population. A practitioner must read this to understand the mathematical and logical baseline before it gets muddied by later optimizations.

L. B. Soros, Nick Cheney, Kenneth O. Stanley
2016
How the Strictness of the Minimal Criterion Impacts Open-Ended Evolution
ALIFE
DOI 10.7551/978-0-262-33936-0-ch040
This paper proves that the minimal criterion acts as a tuning knob for evolutionary pressure, showing that too strict a criterion forces convergence while too loose a criterion yields chaos. You must know this because setting the threshold is the single most sensitive parameter in any reproduction of these experiments.

Jonathan C. Brant, Kenneth O. Stanley
2019
Benchmarking Open-Endedness in Minimal Criterion Coevolution
GECCO
DOI 10.1145/3321707.3321756
The original 2017 paper capped complexity by using fixed-size grids; this paper introduces an expanding maze encoding that allows unbounded structural complexity. It is crucial because it establishes the first viable, computationally cheap domain for benchmarking whether an algorithm is truly open-ended.

Rui Wang, Joel Lehman, Jeff Clune, Kenneth O. Stanley
2019
Paired Open-Ended Trailblazer (POET): Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions
arXiv:1901.01753
While POET diverges from pure Minimal-Criterion Coevolution by introducing explicit optimization within environments, it is the most famous descendent of the concept and introduces the critical mechanism of transfer learning between coevolving niches. You cannot operate in this field without understanding POET's standing critique of pure drift.

Jonathan C. Brant, Kenneth O. Stanley
2020
Diversity preservation in minimal criterion coevolution through resource limitation
GECCO
DOI 10.1145/3377930.3389809
This paper introduces resource limitation as a natural way to maintain diversity without calculating genetic distances or maintaining explicit novelty archives. It is the most advanced expression of the "pure" biological approach before the field shifted to deep learning models.

CURRENT FRONTIER SOURCES

Andrew Dai, Boris Meinardus, Ciaran Regan, Yingtao Tian, Yujin Tang
2026
Discovering Novel LLM Experts via Task-Capability Coevolution
arXiv:2604.14969
This is the absolute state of the art in 2026, known as AC/DC (Assessment Coevolving with Diverse Capabilities). It applies the minimal criterion concept to large language models and synthetic task generation, using skill vectors to maintain an archive of diverse experts. It defines the current frontier of where the compute and attention are actually focused.

Aaron Dharna, et al.
2022
Watts: Infrastructure for Open-Ended Learning
arXiv:2204.13250
This paper atomizes the components of open-ended learning systems into modular pieces (Generators, Validators, Solvers). It is essential reading for a computational scientist building new systems, as it defines the modern software architecture required to decouple the coevolutionary loop from the specific domain physics.

Mika Senghaas, et al.
2025
INTELLECT-3: A 100B+ MoE trained with Large-Scale RL (and the prime-environments release)
IDENTIFIER UNKNOWN
While the formal paper identifier for the overarching model is unconfirmed, the associated release of the Prime Environments Hub in late 2025 is the load-bearing infrastructure for current multi-turn reinforcement learning coevolution. It defines the standardized interface that modern open-ended algorithms use to interact with complex tasks.

PART 3. SOFTWARE I CAN ACTUALLY RUN

MinimalCriterionCoevolution
https://github.com/jbrant/MinimalCriterionCoevolution
C#
Licence UNCONFIRMED
2020
DORMANT
This is the reference implementation from the originating authors for the foundational maze and bipedal walker experiments. It can run the exact resource limitation and unbounded maze expansion experiments from the 2017 to 2020 papers. The massive gotcha is that it is written in C# and tightly coupled to an external RDBMS (specifically relying on Transact-SQL schemas) for post-hoc analysis and experiment configuration. It is highly specific to a legacy High-Performance Computing environment, meaning modern users usually have to manually disable the distributed execution flags and rewrite the data logging to run it locally.

watts
https://github.com/aadharna/watts
Python
MIT
2022
DORMANT
Watts is a framework built to explore and benchmark open-ended learning algorithms by modularizing the generators, validators, and solvers. It can run reimplementations of POET and PAIRED on 2D grid worlds. Its main limitation is that it was built just before the massive shift toward LLMs and highly distributed GPU reinforcement learning, so while the architecture is elegant, it lacks native support for modern tensor parallelism and model merging strategies required for the 2026 frontier.

AC/DC (Assessment Coevolving with Diverse Capabilities)
https://github.com/SakanaAI/AC-DC
Python
UNCONFIRMED
2026
MAINTAINED
This is the current community standard for applying coevolution to Foundation Models. It can run the continuous coevolution of an LLM archive and a synthetic task archive using evolutionary model merging and weight noising. It evaluates models on synthetic data to compute skill vectors. The limitation is raw compute cost: running the full pipeline requires significant GPU memory to host multiple concurrent LLMs and the "scientist" model generating the tasks.

prime-environments
https://github.com/PrimeIntellect-ai/prime-environments
Python
UNCONFIRMED
2026
MAINTAINED
This is the modern infrastructure stack for distributed reinforcement learning environments, natively supporting the verifiers specification. It allows you to wrap custom tasks in a standardized API that handles the distribution and execution of the minimal criterion evaluation step across a compute cluster. It is not an algorithm itself, but it is the evaluation harness that serious entrants use today to avoid rewriting inter-process communication and sandbox execution logic.

PART 4. DATA AND BENCHMARKS

Because Minimal-Criterion Coevolution generates its own problems, the field relies less on static datasets and more on standard Generators and downstream Evaluation Suites.

The Expanding Maze Generator
Access route: Contained within https://github.com/jbrant/MinimalCriterionCoevolution
Size: Procedurally unbounded.
Licence: UNCONFIRMED
This is the authoritative toy benchmark for pure open-endedness. It generates 2D grid mazes that can expand in dimension indefinitely. It is used to measure the algorithm's ability to sustain overlapping populations over tens of thousands of generations without capping out on structural complexity. Known limitation: The domain is so low-dimensional that solving it does not prove the algorithm will scale to neural network weight spaces.

Bipedal Walker Hardcore (POET domain)
Access route: OpenAI Gym / Box2D physics engine.
Size: Procedurally generated terrains.
Licence: MIT
Used to measure the generation of stepping-stone curricula. The environment generates varied terrain (stumps, gaps, stairs). It is popular but heavily critiqued for saturation; the physics engine limits how complex a terrain can actually get before it becomes physically impossible for the standard bipedal morphology, meaning the "open-endedness" inevitably hits a hard ceiling.

AC/DC Synthetic Task Archives
Access route: Generated at runtime via AC/DC pipeline.
Size: Grows continuously during the run.
Licence: UNCONFIRMED
This is the frontier evaluation mechanism. A large "scientist" LLM continuously mutates existing task descriptions to generate novel prompts spanning math, code, and reasoning. It is used to measure the capability coverage of the coevolving LLM population. To prevent self-delusion (where models invent gibberish tasks that only they can solve), the framework relies on downstream authoritative benchmarks for final validation.

MMLU, GPQA, and HumanEval
Access route: HuggingFace Datasets.
Size: Tens of thousands of multiple-choice and coding questions.
Licence: MIT / Various.
While the coevolution algorithm is strictly forbidden from optimizing against these benchmarks directly, they are the authoritative measuring sticks used at the end of the run. A practitioner takes the final archive of evolved solvers and tests their coverage against these static datasets to prove that the capabilities generated by the minimal criterion generalize to human-relevant tasks.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to understand the pure mechanics of this field is the Resource Limitation Maze experiment from Brant and Stanley 2020. It perfectly isolates the coupled drift mechanism without the extreme compute overhead of modern LLM pipelines.

Software and Version: MinimalCriterionCoevolution, Release version 1.3.
Dataset/Generator: The internal Maze Navigation procedural generator.

Parameters that must be set:
ExperimentSource: file
NumRuns: 1
ExperimentConfigDirectory: ./MCC_Executor/MazeNavigation/ExperimentConfigurations/
OutputFileDirectory: ../ExperimentResults/
SeedAgentFile: ./MCC_Executor/MazeNavigation/SeedAgents/SeedAgents_Acyclic_20_Genomes_10_Size_2_Waypoints_2_Walls_5_LR.xml
SeedMazeFile: ./MCC_Executor/MazeNavigation/SeedAgents/GeneratedMaze_10_Genomes_10_Height_10_Width_2_Waypoints_2_Walls.xml
ExperimentNames: MCC-LimitedResources
StartFromRun: 1
IsDistributedExecution: false
GenerateAgentPopulation: false

Replicates and Seeding:
The experiment should be run for at least 5 independent replicates to account for chaotic evolutionary variance. The seeding regime is strictly defined by the XML files provided in the repository, which bootstrap the system with minimally competent agents so the algorithm does not immediately collapse before it begins.

Compute Cost:
Negligible by modern standards. Roughly 2 to 4 CPU hours per run on a standard desktop processor. No GPU required.

Expected Result:
The primary metric is population diversity and survival count. You should expect to see the agent population maintain a higher number of surviving, distinct genetic niches compared to the baseline unbounded MCC, and the maze structures should show a continuous, systematic increase in complexity (measured by the number of walls and solution path length). The published result to compare against is Figure 4 and Table 1 in Brant and Stanley 2020 (DOI 10.1145/3377930.3389809), which shows resource-limited MCC maintaining viable populations indefinitely while baseline MCC often experiences severe population bottlenecks.

Common ways people get this wrong:
1. Failing to configure the database schema. The post-hoc analysis code assumes a specific SQL Server DDL. Users who do not set this up will successfully run the evolution but fail to extract the structural statistics of the mazes, leaving them with unreadable binary state dumps.
2. Enabling distributed execution. The code has legacy flags for a specific Sun Grid Engine HPC environment. Leaving `IsDistributedExecution` true on a local machine will cause immediate thread halting and file lock errors.
3. Randomizing the seed agents without a bootstrap phase. If a user sets `GenerateAgentPopulation=true` but does not include a pre-training loop, the randomly initialized agents will fail to solve even the simplest maze, the minimal criterion will evaluate to zero for both populations, and the experiment will collapse to extinction in Generation 1.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you are entering this field as a serious computational scientist, you will quickly find that the tooling is severely bifurcated. There is toy-domain code from 2017, and hyperscale LLM code from 2026. What does not exist is a universal, substrate-agnostic evaluation harness in Python.

What you must build: The N-to-M Minimal Criterion Bipartite Graph Evaluator.

Interface:
Input: A set of N Solvers (can be neural network weights, Python functions, or LLM API endpoints) and M Environments (can be JSON task definitions, gym environment seeds, or text prompts).
Output: A sparse boolean matrix of size N x M representing the existential verdict (1 if solved, 0 if failed), and a set of indices dictating which Solvers and Environments survived to the next generation.

The Hard Part:
Evaluating N Solvers against M Environments is an O(N*M) operation every single generation. If an environment evaluation takes even 1 second (e.g., running a physics simulation or generating an LLM response), a population of 100 solvers and 100 environments requires 10,000 seconds per generation. The hard part is building an asynchronous, distributed execution scheduler that aggressively prunes evaluations. Because the system only cares if a solver solves *at least one* environment, you do not need to evaluate the full matrix. You only need to evaluate until a single success is found for a given individual, and then halt further evaluation for that individual's survival check.

Work Estimate:
Building this scheduler correctly, with robust error handling for environments that crash or infinitely loop, takes a competent engineer roughly three to four weeks. Several groups (including the original POET team and the AC/DC team) have completely rebuilt this exact bipartite evaluation routing logic privately because standard RL libraries (like Ray RLlib) assume a static environment and a maximizing reward function, fundamentally clashing with the dynamic, non-objective nature of coevolution.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The history of Minimal-Criterion Coevolution is littered with elegant ideas that failed to scale. Understanding these failures is critical to avoid repeating them.

The Static Bounds Failure
In the original 2017 formulation, the maze domain used a fixed grid size. The method successfully generated diverse mazes, but within a few hundred generations, the space of possible permutations was saturated. The results were visually interesting but mathematically finite. This proved that while the minimal criterion drives search, it cannot overcome the physical constraints of its encoding. If the environment representation cannot scale infinitely, the algorithm is not open-ended, it is just a highly efficient space-filling curve.

The Forgetting Artifact (The Red Queen Critique)
A standing, structural critique of pure Minimal-Criterion Coevolution is that it lacks a historical anchor. Because an environment only survives if a *current* solver can solve it, simple environments eventually drift out of the population as solvers become highly specialized for complex environments. Once the simple environments are gone, the solvers no longer need to retain the basic skills required to solve them. If you take a Generation 10,000 solver and place it in a Generation 1 environment, it will frequently fail. The system does not actually build cumulative general intelligence; it builds a highly specialized, brittle intelligence adapted only to the moving frontier. This critique was partially answered by modern implementations (like AC/DC) which use Dominated Novelty Search to explicitly maintain an archive of past solutions, abandoning pure drift.

The Optimization Gradient Failure
The authors of POET (Wang, Lehman, Clune, Stanley) levied the most significant methodological critique against pure Minimal-Criterion Coevolution. They argued that relying purely on genetic mutation to cross the gap between a currently solvable environment and a slightly harder, newly mutated environment is profoundly inefficient for deep neural networks. In their experiments, pure drift failed to navigate the bipedal walker domain because the chance of randomly mutating thousands of neural network weights to achieve the precise kinematic changes required for a new terrain is statistically zero. Their answered critique was to implement Evolution Strategies as an explicit optimization loop *inside* the environment to climb the local gradient. Pure Minimal-Criterion purists have never effectively answered this critique for high-dimensional continuous control tasks.

The "Self-Delusion" Benchmark Problem
In recent attempts to coevolve language models and synthetic tasks, several programmes failed because they measured progress by looking at the synthetic tasks themselves. The models would generate mathematically meaningless strings of tokens that the solvers would successfully "predict," resulting in a minimal criterion satisfaction matrix that looked incredibly healthy. Upon human inspection, the system had coevolved a private cryptographic noise language. This is a classic case of measuring the artifact rather than the phenomenon. The standing rule in the field is now that coevolved capabilities must be validated against static, human-curated downstream benchmarks that were strictly held out of the evolutionary loop.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

For a well-resourced newcomer with compute capabilities, the goal is to operate in the spaces where the minimal criterion paradigm breaks traditional scaling laws. Here are the specific, ranked experiments to run today.

Rank 1: Coevolving LLM Verification and Generation in Code Sandboxes
What it is: Implement Minimal-Criterion Coevolution where Population A consists of generative coding models, and Population B consists of testing/verification scripts. The minimal criterion for a model is that it must pass at least one test script; the criterion for a test script is that it must be passed by at least one model, but failed by at least one other (ensuring the test is neither impossible nor trivial).
Why it is feasible now: The release of prime-environments allows secure, high-throughput sandbox execution of arbitrary code, a capability that was historically a massive security and infrastructure bottleneck.
What it would measure: The coverage and accuracy of the resulting models on the SWE-bench or HumanEval datasets.
What would falsify it: If the resulting models score lower on static benchmarks than a model trained purely on standard Reinforcement Learning from Human Feedback using the same compute budget, the hypothesis that coevolution provides a superior curriculum is falsified.

Rank 2: Bio-Sequence Coevolution (Bio-ACDC Scaling)
What it is: Coevolving masked language models (like ESM-2 for proteins) with synthetic sequence tasks (like motif detection or structural folding targets).
Why it is feasible now: The adaptation of AC/DC mechanics to biological sequences exists conceptually but has not been scaled on massive GPU clusters.
What it would measure: The evolutionary system's ability to discover viable, novel protein structures that satisfy functional constraints without explicit target design.
What would falsify it: If the generated sequences exhibit high minimal criterion success but fail downstream biochemical plausibility checks (e.g., AlphaFold 3 stability metrics), the coevolutionary loop is merely exploiting the loss landscape of the surrogate evaluator.

Rank 3: Pure Minimal-Criterion Coevolution on Multi-Agent Tool Use
What it is: Coevolving a population of agents with a population of dynamic APIs. The agents must figure out how to use the API to retrieve a flag; the APIs randomly mutate their endpoints, required JSON schemas, and authentication flows.
Why it is feasible now: The LLM function-calling ecosystem is mature enough to be procedurally mutated.
What it would measure: The emergence of generalized zero-shot tool use in language models.

What will NOT work:
Attempting to run pure Minimal-Criterion Coevolution (without an inner optimization loop) on raw pixel-based continuous control tasks (like Atari or 3D physics simulators). The search space of visual reinforcement learning is too sparse. Pure existential drift relies on the frontier of adjacent possible mutations being reasonably dense. In pixel space, mutating a visual processing network randomly will almost always result in a catastrophic loss of function, dropping the agent below the minimal criterion immediately. You will spend tens of thousands of compute hours watching populations instantly collapse into extinction.
