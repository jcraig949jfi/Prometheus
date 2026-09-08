# Prompt 89: Phenotypic Plasticity and the Baldwin Effect

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdvN3VmYXRXVUFfMnNfUFVQb01ERTRBSRIXbzd1ZmF0V1VBXzJzX1BVUG9NREU0QUk
**Elapsed:** 456s

---

# FRONTIER PRACTITIONER DOSSIER: Phenotypic Plasticity and the Baldwin Effect

Key Points:
* The Baldwin effect demonstrates how lifetime learning accelerates evolutionary search by smoothing fitness landscapes, eventually allowing learned traits to become genetically hardcoded (assimilated) without Lamarckian inheritance [cite: 1, 2].
* While foundational models relied on contrived needle-in-a-haystack landscapes, modern frontier research has absorbed this mechanism into Deep Meta-Learning and Neuroevolution, evaluating it on complex robotic morphologies and physics-informed neural networks [cite: 3, 4, 5].
* A standing controversy remains over whether genetic assimilation requires an explicit metabolic cost for learning, or if implicit costs such as learning time and network capacity are sufficient [cite: 6, 7].
* For a computational practitioner in 2026, the frontier involves bi-level optimization frameworks (typically using JAX) where outer evolutionary loops search for inductive biases and inner gradient-based loops execute lifetime learning [cite: 8, 9].

This dossier provides a comprehensive, skeptical, and computationally grounded map of the field of Phenotypic Plasticity and the Baldwin Effect as it stands in 2026. It is written specifically for a computational scientist looking to build and execute frontier in-silico experiments. The report strictly anchors to the mechanism of genetic assimilation via lifetime learning, detailing the theoretical constraints, software realities, and experimental recipes required to push the boundary of the field.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

In 2026, the study of the Baldwin effect and phenotypic plasticity has largely been absorbed into the broader disciplines of Meta-Learning, Neuroevolution, and Embodied Artificial Intelligence. As a distinct, standalone domain of Artificial Life, the field is effectively dormant; what was lost in this merge is the purely biological focus on population genetics and abstract theoretical models. In its place, the field has gained massive computational scale. Today, the Baldwin effect is treated as a practical bi-level optimization strategy. The outer loop (Darwinian evolution) evolves the hyperparameters, initial weights, or physical morphology of an agent. The inner loop (lifetime learning) uses reinforcement learning or gradient descent to adapt those priors to specific tasks. Because the inner loop gradients do not need to be backpropagated into the outer loop, Baldwinian meta-learning bypasses the severe memory and horizon limitations of gradient-based meta-learning algorithms like Model-Agnostic Meta-Learning [cite: 3, 10].

What is SETTLED: It is computationally proven that lifetime learning smooths rugged fitness landscapes. By allowing individuals to learn, the evolutionary search process is provided with a gradient toward optimal solutions that would otherwise be invisible to random mutation. It is also settled that Baldwinian evolution outperforms both pure Darwinian evolution (which is too slow) and pure Lamarckian evolution (which overfits) when the environment is highly dynamic or the task distribution is broad. Lamarckian transfer works well for static tasks, but Baldwinian genetic assimilation yields superior robustness and generalization [cite: 3].

What is CONTESTED: The primary live disagreement revolves around the necessity of a "cost of learning" for genetic assimilation to occur. The classical biological view, championed historically by Giles Mayley, dictates that assimilation will only happen if learning incurs a direct fitness penalty, forcing the population to hardcode the trait to avoid the penalty [cite: 6, 11]. If learning is free, the phenotype masks genetic deficits, halting evolution entirely in what is known as the "Hiding Effect". Conversely, modern deep learning practitioners (such as the authors of the DERL framework and Baldwinian-PINN) argue that implicit costs—such as the number of epochs required to reach a reward threshold or the computational capacity of a neural network—are sufficient to drive assimilation [cite: 4, 8, 12]. 

What is OPEN: The frontier is currently focused on "Phenotype-first" evolution and open-ended morphological co-adaptation. Researchers are investigating "Natural Induction," where complex gene-regulation networks remember poses and behaviors discovered during a lifetime, fundamentally questioning whether random genetic variation is the sole driver of evolutionary memory [cite: 13, 14]. Additionally, scaling Baldwinian meta-learning to massive foundation models without triggering catastrophic forgetting remains a wide-open engineering challenge.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Hinton, G. E., and Nowlan, S. J.
1987
How Learning Can Guide Evolution
Complex Systems
IDENTIFIER UNKNOWN
This is the genesis paper for computational Baldwin effect research. It introduces the needle-in-a-haystack landscape, proving combinatorially that allowing alleles to be plastic (learnable) dramatically accelerates evolutionary search by smoothing the fitness landscape [cite: 15, 16]. A practitioner must know this to understand the baseline mechanism, but must also understand its limitations.

Mayley, G.
1996
Landscapes, Learning Costs, and Genetic Assimilation
Evolutionary Computation
DOI 10.1162/evco.1996.4.3.213
This paper formalizes the absolute necessity of a cost of learning. It introduces the Hiding Effect, demonstrating that without a cost, learning shields suboptimal genotypes from selection pressure, stalling evolution. It establishes the "Goldilocks principle" of environmental variability [cite: 6, 11, 17].

Fernando, C., Sygnowski, J., Osindero, S., Wang, J., Schaul, T., Teplyashin, D., Sprechmann, P., Pritzel, A., and Rusu, A.
2018
Meta-Learning by the Baldwin Effect
Proceedings of the Genetic and Evolutionary Computation Conference
DOI 10.1145/3205651.3208249
This paper bridges the gap between historical ALife and modern deep learning. It proves that Baldwinian evolution can evolve few-shot learning mechanisms by shaping hyperparameters and initial weights, rivaling MAML without requiring second-order gradients, and highlights why Baldwinian search beats Lamarckian search in broad task distributions [cite: 3, 10].

CURRENT SOURCES (2021 TO 2026)

Gupta, A., Savarese, S., Ganguli, S., and Fei-Fei, L.
2021
Embodied Intelligence via Learning and Evolution
Nature Communications
DOI 10.1038/s41467-021-25874-z
This paper introduces Deep Evolutionary Reinforcement Learning (DERL) and the UNIMAL design space. It is the first large-scale demonstration of a morphological Baldwin effect, showing that complex environments foster morphological intelligence, and that evolution selects bodies that learn faster over generations [cite: 4, 18, 19].

Wong, J. C., Ooi, C. C., Gupta, A., Chiu, P. H., Low, J. S. Z., Dao, M. H., and Ong, Y. S.
2026
Evolutionary Optimization of Physics-Informed Neural Networks: Advancing Generalizability by the Baldwin Effect
IEEE Transactions on Evolutionary Computation
DOI 10.1109/TEVC.2026.3650792
This is the current state-of-the-art implementation of Baldwinian meta-learning. It uses evolutionary selection pressure combined with lifetime learning to create Physics-Informed Neural Networks that generalize across entire families of partial differential equations, achieving massive speedups over gradient-based meta-learning [cite: 8, 20].

Watson, R. A., Levin, M., Buckley, C. L., et al.
2025
Evolution by natural induction
Royal Society Interface
DOI 10.1098/rsfs.2025.0025
This paper defines the theoretical frontier of "phenotype-first" evolution. It argues that adaptive phenotypic plasticity acts as a natural induction mechanism, discovering adaptive phenotypes which genetic evolution subsequently canalizes, effectively bypassing the need for neural cognition in the Baldwin effect [cite: 13, 14].

Ao, S., Zhou, T., Long, G., Song, X., and Jiang, J.
2023
Curriculum Reinforcement Learning via Morphology-Environment Co-Evolution
arXiv:2310.18956
This paper builds on the UNIMAL framework, demonstrating that optimizing an agent and its morphology through co-evolution provides superior transferability to unseen variations, highlighting the continuing relevance of morphological plasticity [cite: 21].

Wong, J. C., Gupta, A., Ooi, C. C., Chiu, P. H., Liu, J., and Ong, Y. S.
2025
Evolutionary Optimization of Physics-Informed Neural Networks: Evo-PINN Frontiers and Opportunities
IEEE Computational Intelligence Magazine
DOI 10.1109/MCI.2025.3607749
This serves as the best modern survey bridging evolutionary computation with deep scientific machine learning, explicitly detailing how the Baldwin effect addresses the training bottlenecks and narrow generalization of conventional Physics-Informed Neural Networks [cite: 22].

PART 3. SOFTWARE I CAN ACTUALLY RUN

DERL (Deep Evolutionary Reinforcement Learning)
https://github.com/agrimgupta92/derl
Python
MIT License
2021
DORMANT
This is the reference implementation for the UNIMAL morphological evolution experiments. It can run asynchronous tournament-based evolution of robot morphologies (using Proximal Policy Optimization for inner-loop lifetime learning) across flat, variable, and manipulation terrains [cite: 23, 24]. 
Gotchas and Limitations: The software is effectively dormant and highly coupled to older versions of PyTorch, MuJoCo, and MPI for parallelization. Building the canonical implementation on modern toolchains is notoriously difficult due to MuJoCo licensing and API changes since 2021. Practitioners today typically do not run this directly; instead, they reimplement the UNIMAL XML generation logic inside modern JAX-based physics simulators like Brax or MJX to avoid the severe CPU bottlenecks of the original implementation.

Baldwinian-PINN
https://github.com/chiuph/Baldwinian-PINN
Python
MIT License
2025
MAINTAINED
This is the community standard for running Baldwinian meta-learning on neural physics solvers. It evaluates whether initial neural network weights and hyperparameters evolved across a distribution of physics tasks can rapidly assimilate to new tasks via lifetime learning. It leverages JAX and EvoJAX for hardware-accelerated neuroevolution [cite: 25].
Gotchas and Limitations: The software requires precise version matching for JAX and EvoJAX. The outer loop uses Covariance Matrix Adaptation Evolution Strategy, which scales well but can suffer from population collapse if the physics-informed loss landscapes have extreme discontinuities. The inner loop solves new linear partial differential equations using a pseudoinverse operation rather than gradient descent, meaning you must carefully adapt the code if you want to test standard reinforcement learning environments instead of physics models [cite: 5].

PredPreyGrass
https://github.com/doesburg11/PredPreyGrass
Python
MIT License
2025
MAINTAINED
A multi-agent deep reinforcement learning environment designed explicitly to test the Baldwin effect, co-evolution, and phenotypic plasticity. It evolves a speed trait while agents use reinforcement learning within their lifetimes to survive [cite: 26].
Gotchas and Limitations: It is built on Ray RLlib, which is currently undergoing massive API deprecations. The repository has known issues regarding RLlib new API stack false deprecation warnings [cite: 27]. It is highly useful for spatial ecosystem experiments, but the underlying multi-agent framework requires significant overhead to tune.

BaldwinianMetaLearning
https://github.com/shawnbeaulieu/BaldwinianMetaLearning
Python
MIT License
2018
ABANDONED
This was a reimplementation of Fernando et al. 2018. It tests whether evolution can find initial weights for a network that allow a reinforcement learning algorithm to continually adapt during the agent's lifetime [cite: 28]. 
Gotchas and Limitations: It was written for Python 3.6 and uses outdated deep learning libraries. It is unbuildable on modern toolchains without heavy refactoring. Its primary value today is purely as structural reference for implementing inner-loop local updates within an outer-loop Natural Evolution Strategy.

AttractorScaffolding
https://github.com/ABRG-Models/AttractorScaffolding
C++
Unspecified License
2024
DORMANT
A boolean network model used to explore genetics and the Baldwin effect in developmental dynamics [cite: 29].
Gotchas and Limitations: It requires CMake, MPIR, and JSONCPP. It is highly abstract and not suited for deep learning integration, but it remains the most accurate topological model for studying pure attractor landscape dynamics in gene regulation networks.

PART 4. DATA AND BENCHMARKS

UNIMAL Design Space Benchmark
Access: https://github.com/agrimgupta92/derl
Size: 100 training morphologies, 100 test morphologies
License: MIT
This is the authoritative benchmark for morphological intelligence and the morphological Baldwin effect. It provides an expressive hierarchy of 3D rigid parts connected via motor-actuated hinge joints. It is used to measure zero-shot generalization and learning speed over generations [cite: 30, 31].
Known Issues: Saturation is a problem. Modern transformer-based universal controllers (like MetaMorph or HyperDistill) can heavily overfit the training morphologies, achieving high performance without genuinely generalizing to structurally novel test morphologies [cite: 31, 32].

PINN PDE Meta-Learning Task Families
Access: https://github.com/chiuph/Baldwinian-PINN
Size: Procedurally generated batches
License: MIT
This benchmark suite generates families of partial differential equations (e.g., 1D transient wave equations, 2D Navier-Stokes, diffusion-reaction equations). It is used to measure the generations required to reach a specific physics-informed loss threshold, comparing Baldwinian initialization against Model-Agnostic Meta-Learning [cite: 8, 33].
Known Issues: Contamination can occur if the sampling distribution for the outer evolutionary loop is too narrow, resulting in a model that memorizes a specific boundary condition rather than generalizing to the PDE family.

Needle-in-a-Haystack (Hinton & Nowlan) Landscape
Access: Procedurally generated (historically 20-bit strings)
Size: Trivial
This is the historical toy problem where only one specific genetic string has high fitness, and all others have baseline fitness. 
Known Issues: This benchmark is considered fully saturated and highly artifactual. It has been proven that if the population is sufficiently large, standing genetic variation will find the needle without learning. If resources are limited, the population gets permanently stuck at the plateau. It should not be used for modern publication [cite: 34, 35].

H-IFF (Hierarchical If-and-only-If)
Access: Procedurally generated
Size: Scalable bit-strings
Used as a modern replacement for the needle-in-a-haystack. It contains multiple fitness peaks and requires the discovery of hierarchical modules. It accurately measures whether learning can guide evolution to combine low-level modules into high-level solutions where crossover alone fails [cite: 35].

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment at the frontier of this field in 2026 is the Baldwinian Physics-Informed Neural Network (Baldwinian-PINN) evaluation on the diffusion-reaction equation by Wong et al.

Software and Version:
Clone https://github.com/chiuph/Baldwinian-PINN (commit state as of January 2026). Ensure you are running Python 3.8 or higher, jax 0.3.23, and evojax 0.2.15 [cite: 25].

Dataset / Generator:
The internal PDE generator for the 1D diffusion-reaction task family. The generator varies the diffusion coefficient and the reaction rate across the task distribution [cite: 8].

Parameters:
Outer Loop (Evolution): Covariance Matrix Adaptation Evolution Strategy.
Population Size: 256.
Task Batch Size per Generation: 16 tasks sampled from the PDE family.
Inner Loop (Lifetime Learning): 1-step pseudoinverse operation for the final linear output layer (or Adam optimizer if running the nonlinear configuration).
Hidden Layers: Fixed at birth, defined by the evolved genotype.
Learning Rate (if nonlinear): Evolved alongside the weights.

Replicates and Seeding:
10 independent replicates using fixed random seeds 1 to 10 for JAX PRNG keys to ensure identical task sampling distributions across runs.

Compute Cost:
Approximate cost is 4 hours on a workstation with 2 GPUs (e.g., RTX 3090) [cite: 25].

Expected Result:
You are measuring the relative norm error on unseen test tasks. The Baldwinian-PINN should achieve a 70x improvement in prediction accuracy and a 700x reduction in computational time during the lifetime learning phase compared to a gradient-based MAML baseline on the same diffusion-reaction task [cite: 8, 20, 36].

Citation for Published Number:
Wong, J. C. et al. (2026). Evolutionary Optimization of Physics-Informed Neural Networks: Advancing Generalizability by the Baldwin Effect. IEEE TEVC. DOI 10.1109/TEVC.2026.3650792 [cite: 8].

Three Most Common Ways People Get This Experiment Wrong:
1. Disabling the evolution of the learning hyperparameters. The Baldwin effect relies heavily on evolving the plasticity rate (learning rate) alongside the weights. If you fix the inner-loop learning rate manually, assimilation fails.
2. Under-sampling the task distribution. If the outer loop evaluates individuals on too few tasks per generation (e.g., batch size of 2), the evolutionary algorithm exploits the noise, resulting in catastrophic overfitting and zero generalization to the test set.
3. Using deep backpropagation in the inner loop. The specific massive speedup of this recipe relies on fixing the hidden layers at birth and only applying lifetime learning (via exact pseudoinverse) to the final layer. If you unroll gradients through the whole network in the inner loop, it degrades into a standard Lamarckian/MAML setup and crashes from memory exhaustion [cite: 5].

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

To run frontier experiments on morphological phenotypic plasticity (the trajectory started by DERL), a serious entrant must build a fully JAX-accelerated morphological evolution compiler. 

Currently, no off-the-shelf tool provides an end-to-end differentiable or JAX-jittable pipeline where the outer loop mutates a graph-based morphology (adding/removing limbs) and the inner loop instantly evaluates reinforcement learning on that new body in a hardware-accelerated physics engine. DERL does the outer loop on CPUs and passes data to GPUs, which is massively bottlenecked [cite: 24]. 

Interface Specifications:
Input: A directed acyclic graph representing a kinematic tree (the genotype), where nodes specify geometry (cylinders, spheres) and edges specify joint limits and gear ratios.
Output: A compiled MJX (MuJoCo XLA) environment struct that can be passed directly into an EvoJAX inner-loop reinforcement learning trainer.
The Hard Part: JAX requires static shapes for its compiled computational graphs. Because evolution changes the number of limbs (and thus the state/action space dimensions), you cannot natively JIT-compile the evolutionary loop without heavy padding and masking strategies. You must build a universal state-space tensor where inactive limbs are zero-masked, allowing the JAX compiler to trace the physics steps once while simulating thousands of structurally unique morphologies in parallel [cite: 30, 32]. 
Work Estimate: This is roughly 3 to 5 months of dedicated engineering for a competent computational scientist familiar with JAX and MuJoCo. Several private industry groups have quietly built masked-tensor physics wrappers to solve this exact gap, signaling high value.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The Field's Standing Methodological Critique: The Hinton & Nowlan Artefact
The most famous critique of this field is that the foundational demonstration of the Baldwin effect (Hinton & Nowlan 1987) relies entirely on a contrived fitness landscape—the needle-in-a-haystack. In this model, fitness is flat everywhere except at one specific genetic sequence. Critics (such as the 2014 Egtheory mathematical critique) proved that if a population is large enough to reflect real biological scales, standing genetic variation alone will discover the optimal genotype without any need for learning [cite: 34, 35]. Conversely, if resources are limited and the population is small, the population gets permanently stuck on the flat plateau, learning or not. Thus, any algorithm claiming breakthrough speeds on needle-in-a-haystack landscapes is merely measuring a baseline statistical artifact of small population sizes, not a profound evolutionary dynamic [cite: 34].

The Hiding Effect and the Cost of Learning
Giles Mayley (1996) proved that phenotypic plasticity can actually stall evolution—a phenomenon known as the Hiding Effect [cite: 6, 11]. If an organism can reach optimal fitness through lifetime learning, and learning incurs no metabolic or temporal cost, the selection pressure on the underlying genotype drops to zero. The genetic makeup will remain suboptimal because the plastic phenotype "hides" the genetic deficits. Therefore, any in-silico experiment that does not implement a strict cost of learning (e.g., deducting fitness based on the number of epochs taken to learn, or restricting neural capacity) will fail to observe genetic assimilation [cite: 6]. Many early neuroevolution programmes failed precisely because they allowed infinite, cost-free inner-loop learning, resulting in populations that never genetically assimilated the trait.

Lamarckian Fragility in Dynamic Environments
Numerous attempts have been made to simply write learned weights back to the genome (Lamarckian inheritance) to save computational time. While Lamarckian algorithms converge significantly faster than Baldwinian algorithms on static, narrow task distributions, they catastrophically fail in dynamic environments. Fernando et al. (2018) showed that when the goal direction or task distribution changes rapidly, Lamarckian populations suffer from genetic lock-in and die out, whereas Baldwinian populations maintain genetic diversity in their priors and successfully adapt [cite: 3, 10]. Claims that Lamarckian RL is strictly superior to Baldwinian meta-learning have repeatedly failed to replicate outside of completely static benchmarks.

Model-Agnostic Meta-Learning (MAML) Horizons
While MAML is heavily cited, attempts to use it as a substitute for Baldwinian evolution in long-horizon reinforcement learning have largely failed. MAML requires unrolling the computational graph to calculate second-order derivatives. If the lifetime learning process requires hundreds of steps, MAML suffers from exploding gradients and memory exhaustion. Baldwinian evolution sidesteps this by using derivative-free optimization (like Natural Evolution Strategies) for the outer loop, which evaluates fitness purely on the final state of the inner loop, rendering it immune to horizon length and non-differentiable rewards [cite: 5, 37].

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the current frontier, a well-resourced newcomer should bypass historical grid-world models and static neural networks entirely. The highest value lies at the intersection of Baldwinian bi-level optimization and modern foundation models.

Experiment Aim 1 (Highest Priority): Open-Ended Baldwinian Discovery in Large Language Model Agents
What to do: Run a bi-level evolutionary experiment where the outer loop uses an Evolution Strategy to optimize the structural sparsity (or a specific set of prefix-tuning vectors) of a small language model. The inner loop involves the agent interacting with a text-based environment (e.g., NetHack or WebArena) using in-context learning (prompt history) to adapt to the environment. 
Why it is feasible now: JAX-based LLM frameworks and massive context windows allow in-context learning to serve as a highly expressive "lifetime learning" phase. 
What it measures: It measures whether the evolutionary outer loop assimilates behaviors initially discovered via in-context learning into the hardcoded sparsity masks or prefix vectors over generations. 
Falsification: If the model's reliance on in-context examples does not decrease over generations while maintaining performance, the Baldwin effect is not occurring, indicating that in-context learning does not smooth the structural loss landscape.

Experiment Aim 2: Co-evolution of Morphology and Baldwinian RL in JAX
What to do: Build the missing JAX morphological compiler (described in Part 6). Evolve the physical topology of modular robots while they undergo lifetime reinforcement learning in a continuous, dynamic terrain. Measure the genetic assimilation of joint limits—specifically, track whether highly plastic joints (requiring continuous active neural torque control) slowly evolve restricted mechanical limits that passively execute the learned gait without neural intervention.
Why it is feasible now: EvoJAX and MJX now allow millions of physics steps per second on a single GPU, enabling population-level lifetime RL in minutes rather than weeks. 
What it measures: The transition from software control (neural learning) to hardware control (genetic morphology), providing undeniable proof of morphological genetic assimilation.

Experiment Aim 3: Meta-Learning for Non-Stationary Ecosystems
What to do: Deploy a Baldwinian-PINN architecture to control agents in an adversarial, co-evolutionary environment (similar to PredPreyGrass, but using physics-informed continuous control rather than discrete grids). 
Why it is feasible now: The mathematical framework for rapid fine-tuning of PINNs using pseudoinverse layers allows real-time physics-compliant adaptation [cite: 5]. 
What it measures: Whether pre-wired connection strengths can assimilate predator-evasion kinematics without suffering from the Hiding Effect.

What Will NOT Work:
Do not attempt to run pure grid-world Baldwin experiments (like recreating Hinton & Nowlan on larger strings), and do not attempt to use MAML for morphological meta-learning. The former will drown in standing variation artifacts and the Hiding effect, proving nothing new. The latter will immediately fail due to the non-differentiability of changing a robot's discrete node topology (adding or removing a limb cannot be backpropagated). Furthermore, do not build environments where learning is completely cost-free; without a time penalty, energy penalty, or network-capacity limit on the inner loop, genetic assimilation will mathematically fail to initialize [cite: 6, 32].

**Sources:**
1. [geeksforgeeks.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYQVJN4NswH8LL0F9EU_a_7owHvww4fcAq6jiC7Dxf1xVHiqU3O8cgWJr_mFmwXNG7J6fgNU1AMcMQGqhoGUXxhANrhdVFrx59SoaZlUzqP5-gUD6Yx6LMeFsLEK0V87cXnDqBYfTjABB_On0CCXNCdKLQtG0Ffiv-RGd0PxRZ3DG5lrnfBnB8F828vFNVU_h1ayO48aa7vU8CvchD)
2. [complex-systems.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMZIGC1iqYT501WvQueI-EpILBoF5qZhLhGlWisRmlYafHI0M_Ds7YSLsuZjpglOTfRCycTRhV8M5DZbN6UkzIN1wWtnI-saaG_gBhS69RxRbz2MsgFhCs1LFgToVS8hKzJyu4SdN5j3we7tU=)
3. [polytechnique.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXf8-QeNJMf7TXYP9BWz07WSiMz-uiN4mMuoWKVSldI2-aUeQyhVq7mUTjotzcpOytlASbnaUzhD6A4SDMa2gcghhsYJp7NZa2529fVfhevH7txwNvKN3e8KILoRDCpbnWF-1KGck55ThWig5UeApAX7jK39Q8S7lf1s5WG2MnFOwwIlxvh5rQfqrNwHYx0hs1j8uEXLdjYGPX5966Ru1iLrroN96b0wP4PJc=)
4. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5hv2HEDenFHBYcDBHY0aDWsRon-MkDHIrFNHuVpE78IoTfwl8UfQJGOUYAeF5GGWoCOtADUI4t_-rPP5ZzNZ8rsEKqQROfqxr-aoUBGpAmvCq14dQ1TFyWm0CuP7BdA==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEQI6YOKwlPJM580bVtjQXWuN5OuRKP82z9-5-giVeJHBoI3vlO8h-K2lCUg6aDvGhMyldPY2IpcxNYgJQyz4uzDG3hF9YlDKZ86TfwiKu22-KW6Dzs7fCdg==)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_IAmfFExJLC0B2eI0BeQ7RQ4Ivn-lrkuiu6hcdyIwTFswLEKA4NIUq4d4jnz_JV9cJhXlXIeUHnFc5GdUQQ-VNPe7hmHbUYfyXXFVhY_eIKgSuctnN0ccZztnoqJBKxblPjISvjdhgVgMNa5gQxRPSoJ5qAbHNi0HsXTQCrnBVFobAdaO63AKdI5VDHpp41qq66vXB43e_jg4zWs8xHFyDlE=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHolRFPkXwdywBUEmAUyB5kfcdDABUYmnSDZc48ssUi2cWhAFvX8UzalgH6BZgSXwZQfXPLYj6Vk7Qx3lySV3br-FZ8DmvRtFmE3Npvzbyi-SRT6T_RPg==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4fafBAaLjNhm1cxSPSpoAZFBVKGmIB5M_QiFsxx9kMO_ZXgJmR4s3UxI2WtbXMa5UdsXgvI30sJv8jkta4BNVIHSWH5QrexPT_DRkHssehWlEEEw64wV0OA==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdHc-sIi-P-n9jT4zGW-FVlRoOiQWfd2QLj6et0X4vj2aLcjZyOl0RVT7YbxqolMnISHh5pB46v-_ucgePPcKVo76pDu64iMyusLFC0vdRMLoCVjiNQ264pg==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHS7NsFLO83wLr1LViLt4MP_p24SWsZCXhNYJ4vWTwnL1-6MRtVTV_LaIJ3Fc2e1gG9vpVsjBiTU75P9GLcu6iZs6yM_WCuMLBDXJ3ZTdYgeuuEyc1odQ==)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkU4NFbO_yU-HKI6IFT2vKZ4VcwhTD7oNqNCNk83TIKgmBdkTcVOFl0gziofxJ9OiGzVWUsFmUm3-YOdZQKh7TpeCuaQZtxpabBf6ZoahGMHvKLVbkxlwM5V7APDslygaQLjgiTKkS36gzCm4sYo0-r1tytaymcS_6lnPsOJUBH3E=)
12. [elifesciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiGaOdtjkQfiq-qjHc1DVG8nQpDmAl1pxje1UJAuPH6QC3W6hnaym0JrGG-XAKxLt_2wSk0ItP8_HQPn7K-3dKURVYEGV652jyQgXkSd1JVaxL6K9TynIHrpY_n-PCKUvRwbW_QBZzoS8=)
13. [royalsocietypublishing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGrAslttx5kAr4TXWuquEquFWRO6wFoBza9X9MBB9MUX37NFir4WgtT2R-9rXIR797PH9OeP9Q2hvBB3II4kkA_Q5DETMYsBkbdlLywBDfoC8_cmJ7OZmxkqVaYvIS_JORNoZJEMDKs8gV0egYSVtacK0QBBD8ZQdTlxwzq-m9lCMBT6dU8ZOjLuGOCGsEP_zKvwQCdfB6Ckg=)
14. [cam.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGikJJWnD_spcCiXlwqjKkcWHc_CmzHkzahyNaFu5XghCH13mR30R-skO4aFRDa90AP3XXXRu9cD8ZXRY4khHGr38SLGebQLA1XvZXIQmtOescUFrQF5jNCfWARvS19LUFUBSzYVGWO4kYH5ivJrXKTOU3QGUmP7tXcw3fzesJiYHsn-OZmyy7GCH0i2Dm8IQ==)
15. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtH3R7y99TzBHepoquw3OUW2JgjJSx7MFoGYwJ6ARE_Q1DXW9Onw-MWsLvYFlU4IYk3R4L3C5wEzJSSYVUWCJ5wwT7ufbKkciW1qohcWi1Asm_kVxY4W46JQvXbrrbThd89EE8x_XOC7WXPA6pawk=)
16. [free.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqGjrPZJ_EfYMXBWDGu5NPswhKJGXeKJ0NBxw0ntNp04c_qepibSZmO5K0ofJquzLq0_ql-tg3M0QYAE4n3FLy93ILFLKdC_nzIu6P3jbIsgMxM1lBOpbROqnc5-muDXgWNm6TMbgtMVwFeZ_Lg4rtPg44LmPiiOspCNVha_QifYZUiQ9lIUu_quxnYI7yKX3TOfLBTc71Ng==)
17. [dblp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHv33Eg6TH8VXpouyu49YcHLkWEup_eWgvIcjnKLMErV4fqJ4dlLh4m1_2N1G9WMzFvRQIFYq9-GxxKoGwUE8PEt3HU86PzqsDuUpGDkt2E5Iyk)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGw4D0fUYd_-iDg5EdQ8hyNPxpiG0YLaC8Al3pIdiSWRj78mo5SWT50bEZc1kow-lThV6Rg5_EgvZkSOJH4muOYzlN2yS4axbbAqyUKErm4hCezdD002g==)
19. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRwcDY3bHZFxkxfsMw-3bx0AoYVt9ISYNtdkqluSiWLfl_yT2sSmzdVPVVv7rnDrxEMliWZ78OiRQU3PJoAn9jD3PXuNB7loNKHcIx9T7nJ-fP3h4TKKAgXA9a3I5DFeG4gNOeVTY9IREGhj6s48qghINDBRoLooDxv0U_5Y5uMt-k66chGeBYxNQSyibtZDHiNgrn)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtJCix-MJ5rSXL5xwJkYD9VF6ytgrRd8QuCBnyTeQDg3jprp_JoS_IHnTYgOlhEkB43eDs5AW6Wy5_uBsYi6A2uU1SsHf0FC4diwnFBMn_VJslravNmRmFCKRcC-Ecc24sT45kbgRGCWuoJwcnpkyxN7R4dP-SFPNQlTdcbu8q5dyaAmasyZJBSgJ-mRqpHtquqoyQizjV1mVCgAfQyV6bbvAShqXTx0qF42jv2_kpMebRQNBXpGWL0BfZy76DC7TSstpQ1v9wEdV8L7z48-qOxd73aFxERr8=)
21. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHn8ltJ3dJQPbAOFvUh1MRrgcN0ea8S-RiX1q99J4qjt-FhI--SlyLj9OiydwWsnvFIYN7rIEu0bAPvFqxUhuFRpigVd9t59k24cgGoJvPmkLq44J4oyO51i4-E1Jfs0p-hvNhRAZrLTEpr9mwxmroQU02xwGu1ahWXhkfNdgD2p8YtCwxSy184w4PNclqHwD1j86_tL0N3h5V4ZBV-3fE4jAx-fsaNJChprXRMmV83lRKfuwFxBNqkgmru81I1rsbWyECtCg==)
22. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFyPvTtKL-Fh_RdvaOGL3TrnyfN2VpAuSZ3btcLDLfUGnjYupikQIXlTE5nTZFf1lFaZ0GXrbOxU3PGYsmFx0szqfkXf1eGyeTfMNPgneOYH6xMp1wNrM3WiKRPiQL0jkg-eZ9k47Qp7191d4Y3qNyCpv-7NgnalsP0hTxaa0fhy1H5ipFCTxbc65RJ3Md7CT1y_iyO_BMllTRc-JjedVJb0KKrnTFENIpf_kOIrZjceR6-C4kmzH44Ypd4gwMD3FkOQ==)
23. [eliaszwang.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElm-hEVexST0REkn88SYA_aiKbwuv0WSNoQY5MUePrYcPbCKGfmYlYM_9lCOKbkn0edQmFVchYcxID0bLwSZy8mpzTlemIb69cXKFkBjQslPy587ESMGKIpQUlxo6KJ6nzVi4vQA137IPOUVWIuAf_e-1e0Qw8Vm9_IeCpYsRsH-aNR55lNYH2)
24. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEddo4E-cxmnwZ_XzEp6EfjEbX317OiDxbTh6JMzwv9rRtrLhKXXACILya9ECLUXFMcKBpOiYqMW3Ww9lpV9Dnoos2RNHjHbrYVr472ETfgXIxD16efSmmFhgc=)
25. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUkr5F-0jy3nzdMIxmqbHYURPmcKITZTqcOFfDl7ctOGANp9F63IRDQaYIs4NAPEjSJNe1QIZlSGtQKaG6SQ_A-iREhU5N-Xoe99Cj4Ljv57jNSoGGW6XhA2j50dIllA==)
26. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJaJdbgzLgDN0RUeUhQlb1P3od9mF2l7k45qIcMQoxj2yd_UH4b1FPZf2dEeLo5CgFmZf-dmkXItrC7ubaCfalBEPSmp7U8IDNnkJJcoqIA48xQHPMhkJUigbi-F3guJJ_)
27. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGC8ePs8wn8E5cmgf3LiHMaFSKi-ClYrUJSglK00sv1vYHS2mJ5a81eLIEV2cX8FlJK09t0XVZmPoK1-QTzAOzRJC2Qs9aKLPSPXf1bPcev4b04eFWcvrK5sUKMCiOiukVvR3wmFA==)
28. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUEmA5meeGCrZsE1_aQ7cViR4WT8zM8OCJE4djzWDZYGh9gRg208vluI3EG5E6PNvnGEeCz7klQPbZAO8yXH8xCLPDPJ8fbn18fz3cW-Qmta2Y0xKpDmasEkxMn9JHb997Lp9kqh4AIIyHn3k_)
29. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEeJToqimTyPw-oOeL51BCNX36Bu5vWPBjSSmxmG8yMjBvnewt8rkvyLhZ8u5ZDQKPBz-UOomgqgXE9rvAjHTdVsT5Tmy3PTbtbfP-2DmiyKYaLJAMv3JKtZItoru0d8z9GnN5HofFNfM8=)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdGXHtiAnPeN5i2_ZSF9f3jc6QcTfgdYrm8DUJZyJT5VHZKtyEWpvylXL1MG4VXvwqOxN4FZQNlKRpRxIuL0h3bdaY4987utgiCEdwHv3NY1y_A_yEidFWyQ==)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9tsM1Ys_Y7cHWwX04rzXbyqMKqRN_V3I5KBSvIHAa5Yih0--OYGPfPpO1yWYclMufJ47rJYe96aWCkRsaJj0SQk0WUKV4TmWzrbuE_eoA3hKtInFzNpGncg==)
32. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuYDm-YUxvizRT-AsrEvP6vCFJnr09UliVB_R0gTZ2DKdAEe-Cpd8kJwc7O3pzbOWNBxN-5xvEcFkiY08UUSaI4NYbUjWlInqNLAi-AJZcJBtipfyPKW4rQgca67RXpBdLyOYucNupzA1E4fXdBbYF9r5uCJ1GItXkonx-xA==)
33. [a-star.edu.sg](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQOtmp9A6un7K_oQ6-Gki4YvL75aHPh2XZEw6AERatbCZDHzFZWWgUUVMowALvZ25Dpv3BWfo3zyEZIvQAjma0G3KkHmZjpss3UpeP8AD3k4oGqiUynOsZyYZBvQ3_ex15iQ0xf2mpztsmMuU_ZmW1vX1PcievvjAVKkr_)
34. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElyXH3qRwFPfVoNYbCTvucfTybXO3OpC8RLwDCwnxVS0kFoVddZsDHBaICrHI4STOgqcv7KZS2K_7PQX5tC6-M9QlN-oEqBySjQTRHa8TwupdoU1a7b_SNH9gF7ShDtTxriDoU9lYD-X231ek6_EvgNSyAYfDDFPx2)
35. [ed.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcPVLVhZ_DIIikk7O3biDXUN5NV4eZbl57XPk14pfQ8sCIhVZ-To8mO7-a16X9Y3NlZKkofHdUMMyh71jvnHEZmSLAFswRl6tfwoKJ78dJjkl3TsxzjrKAPj7ZgizUU7ox97G1z3TlFXtfixlUM1sZUhziDQ==)
36. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHcnh9AzzHTfg-TH9f_jiNxdfmgdfwEZBM9N8jiclKNDd5WJoUPRAusjmx5CPZMv51c2YIggutSWGfs4O6ilCSqarFmyWy4xMFjUdb_72mlW8o1xyvFw==)
37. [polytechnique.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsjX4JzUHCfQKT9jgSS-KQhD4VAWBi85V8kez6-PWz16LyNETD27mIBNr_i1844lsRfq8gF9MNzhQuSwEN0cXusy_d45PJ3FPjTTYQb9ibscsoW6H4uh_sRShOAgJ56CClMLZ5Domfxm7ZHjNHHoGpbGW1B6FtplbQ3_80STOttSb3Py2rTKnD6OORzBPTpJ3w6KYx_CiaiEyPtNcg3Hured8_8_kr7utCXnnD)

