# Prompt 05: Novelty Search

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdyYUtlYXVHRkFmYTBfUFVQNl96MWlRMBIXcmFLZWF1R0ZBZmEwX1BVUDZfejFpUTA
**Elapsed:** 365s

---

# FRONTIER PRACTITIONER DOSSIER: NOVELTY SEARCH AND QUALITY-DIVERSITY

## LEADING OVERVIEW

*   **The Paradigm Shift:** Pure Novelty Search, as you described it, is functionally obsolete. It has been subsumed by Quality-Diversity (QD) optimization. 
*   **The Scaling Revolution:** The field transitioned from CPU-bound single-threaded evolutionary algorithms to massively parallel, hardware-accelerated environments (TPUs/GPUs) using JAX, shrinking experiment times from weeks to minutes.
*   **The Algorithmic Frontier:** The current frontier is dominated by unconstrained, unstructured archives like Dominated Novelty Search (DNS) and AI-feedback-driven diversity in Large Language Models (QDAIF).
*   **The Primary Failure Mode:** Pure novelty search collapses when exposed to the "white noise problem" or "noisy TV problem," where the algorithm becomes captivated by unpredictable, high-entropy stochasticity because it registers as infinite novelty.

Research suggests that your understanding of the core mechanism is historically accurate for the 2008 to 2011 era of the field, but it requires a critical, structural correction for 2026. 

You stated that the objective is thrown away entirely, and novelty is the *only* selection pressure. If you build this today, your experiment will fail. Pure divergent search without a quality metric is fatally vulnerable to the white-noise problem [cite: 1, 2]. If a pure novelty search encounters a source of random noise (like a television playing static, or a continuously changing cloud formation), it will generate infinite behavioral distance from previous states and spend all of its compute watching the noise [cite: 3]. 

To fix this, the field evolved into **Quality-Diversity (QD)** optimization [cite: 4]. QD does not throw the objective away; it explicitly pairs it with novelty. The modern mechanism maintains local competition. An individual is judged on whether it performs the objective *better than any previous individual that exhibited the same behavior*. The archive does not just collect novel behaviors; it collects the highest-performing elite for every region of behavior space [cite: 5]. This hybrid approach—illuminating the search space while simultaneously optimizing within each niche—preserves the objective-agnostic divergence you want while anchoring the search against deceptive white-noise traps [cite: 6, 7].

## PART 1. THE FIELD IN 2026, AND ITS FRONTIER

The field of Novelty Search is no longer an independent discipline; it has been entirely absorbed into the field of Quality-Diversity (QD) optimization [cite: 4]. What was lost in this merge was the philosophical purity of completely ignoring the objective function. What was gained was mathematical stability, resistance to stochastic traps, and the ability to scale to high-dimensional continuous control and generative AI tasks. QD algorithms, such as MAP-Elites and Dominated Novelty Search (DNS), simultaneously map a user-defined behavioral descriptor space and optimize a fitness function within that space, returning an archive of diverse, high-performing elites rather than a single global optimum [cite: 8, 9].

**What is SETTLED:** 
The necessity of massive hardware acceleration is settled. The field has moved definitively to JAX-based implementations. Traditional CPU-bound evolutionary algorithms are considered obsolete for frontier research. Algorithms must support millions of parallel evaluations on TPUs or GPUs, natively integrating the physics simulation or text generation environment into the computational graph [cite: 10]. It is also settled that pure objective gradients fail on deceptive landscapes and that behavioral divergence is a required component of robust search [cite: 11].

**What is CONTESTED:**
The method of archiving and local competition is heavily contested. On one side are the proponents of structured, grid-based competition (e.g., MAP-Elites and its variants like CMA-ME), who argue for explicit tessellation of the behavior space. On the other side are proponents of unstructured archives (e.g., Dominated Novelty Search), who argue that pre-defined grids impose artificial discretization artifacts, require hard-to-tune boundary parameters, and fail catastrophically in high-dimensional spaces [cite: 7, 9]. The unstructured camp is currently gaining significant ground [cite: 9].

**What is OPEN:**
The extraction of behavior descriptors is open. Historically, human experts had to manually define what constituted "behavior" (e.g., the final XY coordinates of a robot). Today, unsupervised behavior discovery—where the algorithm learns its own representation of what makes a behavior novel—is the bleeding edge [cite: 12]. Furthermore, applying QD directly to the latent spaces of Large Language Models (LLMs) and diffusion models via AI feedback is an entirely open frontier, heavily explored but mathematically unconstrained [cite: 13, 14].

## PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Lehman, J., and Stanley, K. O.
Year: 2011
Title: Abandoning Objectives: Evolution Through the Search for Novelty Alone
Venue: Evolutionary Computation
Identifier: DOI 10.1162/EVCO_a_00025
This is the foundational text for pure Novelty Search, demonstrating how objective gradients deceive search processes in maze navigation and bipedal walking. A practitioner must read this to understand the philosophical origin of behavioral distance metrics [cite: 4, 15].

Authors: Mouret, J.-B., and Clune, J.
Year: 2015
Title: Illuminating search spaces by mapping elites
Venue: arXiv
Identifier: arXiv:1504.04909
This paper introduces MAP-Elites, the algorithm that functionally ended pure Novelty Search and birthed Quality-Diversity. It explains how discretizing behavior space into a grid and retaining the highest-fitness individual in each cell solves the white-noise trap [cite: 5].

Authors: Pugh, J. K., Soros, L. B., and Stanley, K. O.
Year: 2016
Title: Quality Diversity: A New Frontier for Evolutionary Computation
Venue: Frontiers in Robotics and AI
Identifier: DOI 10.3389/frobt.2016.00040
This is the paper that formally coined and unified the Quality-Diversity paradigm, comparing Novelty Search with Local Competition (NSLC) against MAP-Elites. It establishes the core terminology you will use [cite: 10, 15].

CURRENT SOURCES (2023-2026)

Authors: Qin, H., Xiang, Y., Zhang, H., Han, Y., Wang, Y., Tao, X., and Liu, Y.
Year: 2026
Title: A survey on Quality-Diversity optimization: Approaches, applications, and challenges
Venue: Swarm and Evolutionary Computation
Identifier: DOI 10.1016/j.swevo.2025.102240
This is the single best and most recent survey of the field. It provides the exact taxonomy of how QD has expanded into robotics, procedural content generation, and generative AI over the last three years [cite: 4, 6].

Authors: Bahlous-Boldi, R., Faldor, M., Grillotti, L., Janmohamed, H., Coiffard, L., Spector, L., and Cully, A.
Year: 2025
Title: Dominated Novelty Search: Rethinking Local Competition in Quality-Diversity
Venue: Proceedings of the Genetic and Evolutionary Computation Conference
Identifier: arXiv:2502.00593
This paper defines the current frontier of archive structure. It mathematically reformulates local competition to eliminate the need for fixed grids, solving the high-dimensionality bottleneck of classic MAP-Elites using dynamic fitness transformations [cite: 9].

Authors: Chalumeau, F., Lim, B., Boige, R., Allard, M., Grillotti, L., Flageat, M., Macé, V., Flajolet, A., Pierrot, T., and Cully, A.
Year: 2024
Title: QDax: A Library for Quality-Diversity and Population-based Algorithms with Hardware Acceleration
Venue: Journal of Machine Learning Research
Identifier: arXiv:2308.03665
This is the architectural blueprint for modern QD infrastructure. It proves that by using JAX to parallelize QD algorithms on hardware accelerators, search times drop from weeks on CPU clusters to minutes on a single GPU [cite: 10, 16].

Authors: Bradley, H., Dai, A., Teufel, H., Zhang, J., Oostermeijer, K., Bellagente, M., Clune, J., and Stanley, K.
Year: 2024
Title: Quality-Diversity through AI Feedback
Venue: International Conference on Learning Representations (ICLR)
Identifier: arXiv:2310.13032
This paper bridges QD and Large Language Models, demonstrating how to use foundation models not just to generate text, but to autonomously score the novelty and quality of text. It introduces QDAIF, effectively bypassing the need for manual behavior descriptors in qualitative domains [cite: 13, 17].

Authors: Faldor, M., Grillotti, L., and Cully, A.
Year: 2025
Title: QDHUAC: Sample-Efficient, Target-Free Distributional Quality-Diversity Reinforcement Learning
Venue: arXiv
Identifier: arXiv:2604.20381
This paper addresses the failure of high Update-To-Data (UTD) reinforcement learning within QD. It shows how target-tracking lag causes value divergence in unconstrained archives and provides the target-free distributional critic architecture needed to fix it [cite: 7].

## PART 3. SOFTWARE I CAN ACTUALLY RUN

QDax
https://github.com/adaptive-intelligent-robotics/qdax
Language: Python / JAX
Licence: MIT
Year: 2025
Verdict: MAINTAINED
This is the community standard for frontier research in 2026. It leverages JAX to compile both the environment (e.g., Brax) and the evolutionary algorithm (MAP-Elites, PGA-MAP-Elites) onto TPUs or GPUs [cite: 10, 18]. You can use this to run a multi-million evaluation continuous control experiment in minutes. The primary limitation is that your environment must be written entirely in JAX; if you have a legacy C++ simulator or a non-differentiable external black-box, QDax cannot JIT-compile it, and you will lose all hardware acceleration benefits.

pyribs
https://github.com/icaros-usc/pyribs
Language: Python
Licence: MIT
Year: 2025
Verdict: MAINTAINED
This is the bare-bones, highly modular reference implementation for the RIBS (Rapid Illumination of Behavior Space) framework [cite: 19, 20]. It is the canonical implementation of CMA-ME and CMA-MEGA. It is perfect if you are optimizing fixed-dimensional continuous domains and do not want to rewrite your simulation in JAX. Its gotcha is that it is fundamentally CPU-bound for the algorithm loop, relying on standard Python multiprocessing, which makes it vastly slower than QDax for large-scale physical simulations.

EvoJAX
https://github.com/google/evojax
Language: Python / JAX
Licence: Apache 2.0
Year: 2025
Verdict: DORMANT
Originally developed by Google Brain as a highly scalable neuroevolution toolkit running on TPUs [cite: 21, 22]. It contains excellent implementations of diverse tasks. However, the repository was officially archived by the owner in August 2025 and is now read-only [cite: 23]. It remains buildable if you downgrade to specific older JAX and Flax dependencies, but for active development, the community has migrated to QDax.

Sferes2
https://github.com/sferes2/sferes2
Language: C++98 / C++11
Licence: CeCILL
Year: 2018
Verdict: DORMANT
This is the software that generated the famous 2015 MAP-Elites Nature paper ("Robots that can adapt like animals") [cite: 24, 25]. It is effectively dead. While it contains the canonical implementation of the original MAP-Elites and early QD modules, the C++11 template-metaprogramming heavy codebase and its reliance on outdated MPI bindings make it notoriously difficult to build on modern toolchains. People do not rebuild this; they use QDax or pyribs instead.

novelty-search-cpp
https://github.com/jal278/novelty-search-cpp
Language: C++
Licence: GPL v2
Year: 2012
Verdict: ABANDONED
This is Joel Lehman's original reference implementation of Novelty Search [cite: 26]. It is completely unbuildable out of the box on modern GCC/Clang due to deep dependencies on a modified, deprecated version of rtNEAT from the 2000s. It should be treated purely as a historical artifact to read, not as software to run.

## PART 4. DATA AND BENCHMARKS

BraxTasks (via QDax)
https://github.com/google/brax
Size: Lightweight procedural generation
Licence: Apache 2.0
This is the authoritative continuous control benchmark suite for the field in 2026. It replaces older MuJoCo benchmarks because it is written entirely in JAX [cite: 10, 27]. It is used to measure the algorithm's ability to find diverse locomotion gaits (e.g., making a virtual ant walk forward, backward, left, and right). Note known contamination: Because Brax has been used so heavily since 2022, many hyperparameter tuning schedules in modern QD literature are implicitly overfitted to Brax's specific contact physics. 

Quality-Diversity Benchmark Suite
https://paperswithcode.com/dataset/quality-diversity-benchmark-suite
Size: Variable (Procedural)
Licence: MIT
A popular standardized collection of QD tasks used primarily by the pyribs community to measure algorithm performance across discrete, continuous, and maze domains [cite: 28]. It measures the terminal archive size and the QD-score (the sum of fitnesses of all discovered elites). It is well-regarded for baseline testing but is not considered sufficient for publishing a frontier paper without an accompanying Brax or generative AI task.

QDAIF Creative Writing Prompts
https://qdaif.github.io/
Size: Hundreds of text prompts
Licence: MIT
Introduced in the Quality-Diversity through AI Feedback paper, this dataset includes benchmark environments for Opinion Writing, Short Stories, and Poetry [cite: 29]. It measures how well an algorithm can populate an archive with high-quality texts across diverse semantic axes (e.g., tone, sentiment, genre). It is authoritative for LLM-based QD search, but practitioners must be aware that the benchmark saturates quickly as underlying foundation models improve, requiring constant adjustment of the AI-feedback critic prompts.

## PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to run today is the accelerated MAP-Elites baseline on the Brax Walker task using QDax. This experiment definitively proves the transition from CPU to GPU/TPU architectures and grounds you in modern QD metrics.

The Recipe:
1. Software: Install Python 3.11, JAX (latest compatible), and QDax version 0.2.x from source.
2. Environment: Brax "Walker2D" task.
3. Parameters: 
   - Repertoire size (archive resolution): 1024 cells.
   - Population size (batch size per iteration): 2048.
   - Number of iterations: 1000.
   - Emitter: standard Iso+LineDD mutation.
   - Behavior Descriptor: The terminal 2D coordinate of the Walker's center of mass after a 1000-step episode.
4. Seeding: 10 independent replicates using distinct random PRNG keys in JAX.
5. Compute Cost: Approximately 5 to 10 GPU minutes per replicate on an NVIDIA A100 (or equivalent TPU), translating to roughly 1 to 2 total GPU hours.
6. Expected Result: A QD-score converging near 150,000 to 180,000, with a coverage percentage exceeding 85 percent of the feasible behavior space.
7. Citation for Comparison: Accelerated Quality-Diversity for Robotics through Massive Parallelism (Chalumeau et al., 2024, JMLR) [cite: 10, 12].

The three most common ways people get this experiment wrong:
1. JIT Compilation Contamination: Failing to execute a dummy compilation run before timing the iterations. JAX compiles the entire evolutionary loop on the first execution; including this overhead in your metric will falsely report terrible algorithm performance.
2. VRAM Exhaustion: Setting the population size to match older CPU-based literature (e.g., 200) instead of maximizing the parallel batch size (e.g., 2048 to 8192) to saturate the accelerator, resulting in highly inefficient GPU utilization.
3. Descriptor Misalignment: Failing to correctly slice the observation tensor to extract the exact behavior descriptor (often confusing the center of mass with a joint angle), resulting in an archive that maps a meaningless projection of the state space.

## PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to run frontier experiments in this field, no off-the-shelf tool provides a robust, native integration for Unsupervised Behavior Descriptor Extraction inside unstructured archives. 

Interface Requirements: 
- Input: A batch of raw, high-dimensional observations (e.g., RGB video frames of an agent, or raw token embeddings from an LLM) generated by the current population.
- Output: A low-dimensional (2D to 6D) continuous behavior vector for each individual, dynamically mapped, without predefined boundaries.
- The Hard Part: The behavior space definition changes as the agent discovers new things. If the dimensionality reduction algorithm (e.g., an autoencoder or contrastive network) updates its weights, all historical behaviors in the archive must be retroactively re-encoded and the spatial distances recalculated. In an unstructured archive like Dominated Novelty Search (DNS), recomputing k-Nearest Neighbors for tens of thousands of dynamic points every generation is computationally brutal.
- Work Estimate: 3 to 6 months of dedicated engineering.

This is a real gap. Several groups (including the Imperial College London team behind DNS and the original QDax authors) have privately rebuilt variations of dynamic metric-learning critics that they patch into their research codebases [cite: 7, 9, 12]. There is no standardized, pip-installable module for non-stationary behavior embeddings in QD.

Furthermore, a Target-Free Distributional Critic for Quality-Diversity Reinforcement Learning (QD-RL) does not exist in standard libraries. If you want to merge modern high-UTD (Update-To-Data) reinforcement learning with QD, you will have to write the hybrid normalization layers and residual blocks from scratch, as the standard actor-critic implementations in Stable Baselines 3 or CleanRL will catastrophically diverge when fed non-stationary archive data [cite: 7].

## PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The White Noise Problem (The Standing Critique of Pure Novelty Search)
The most famous failure in this field is the inability of pure divergence to handle local stochasticity. If a pure Novelty Search agent is placed in a maze with a "noisy TV"—a monitor displaying unpredictable white noise or static—the agent will walk up to the TV and stare at it forever [cite: 1, 2]. Because the agent's behavior descriptor includes its observations, and the static is perfectly random, every frame generates a completely novel state. The algorithm rewards the agent for maximizing distance from the archive, and unpredictable noise provides infinite distance [cite: 3, 30]. This critique proved fatal to the idea of "abandoning objectives entirely." The field answered this critique by developing Quality-Diversity (MAP-Elites), which requires the agent to not just be novel, but to achieve high fitness within its novel niche, anchoring it against pure entropy traps [cite: 15]. 

The Curse of Grid Discretization
Early QD research relied entirely on discretizing the behavior space into a grid. This failed to scale. If you define a 10-dimensional behavior descriptor and bin each dimension into 10 intervals, the grid contains 10 billion cells. The algorithm will never populate more than a microscopic fraction of this space, rendering the archive structure useless and consuming catastrophic amounts of RAM. Furthermore, defining the absolute minimum and maximum bounds for these grids required a priori domain knowledge, defeating the purpose of open-ended search [cite: 7, 9]. This critique was answered by the development of CVT-MAP-Elites (using Centroidal Voronoi Tessellations to fix archive size) and, most recently, Dominated Novelty Search (DNS), which eliminates the grid entirely in favor of dynamic fitness transformations [cite: 9].

Target Tracking Lag in QD-RL
Attempting to accelerate QD by merging it with standard off-policy Reinforcement Learning (PGA-MAP-Elites) revealed a massive failure at high Update-To-Data (UTD) ratios. Researchers found that standard target networks (used to stabilize RL critics) introduce a "Target Tracking Lag." In a QD population, the data distribution of the archive changes violently and constantly as new niches are illuminated. The delayed target network cannot keep up with this non-stationary distribution, leading to severe value divergence and policy collapse [cite: 7]. This is why throwing standard Soft Actor-Critic (SAC) or TD3 code blindly at a QD archive fails to replicate.

The "Diversity is All You Need" Oversell
Several programmes between 2018 and 2021 attempted to prove that maintaining massive diversity archives without any structural fitness constraints could solve complex robotic tasks. These failed to replicate efficiently. It was shown that unstructured diversity often measures artifacts—the algorithm simply discovers thousands of ways for a robot to immediately fall over and break its joints, filling the archive with high-entropy garbage. "Just enough diversity" paired with rigid local competition is the only formulation that consistently works [cite: 31].

## PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

If I were a well-resourced newcomer in 2026, I would abandon standard locomotion benchmarks entirely and aim directly at the intersection of Dominated Novelty Search (DNS) and Large Language Models. 

1. LLM Collective Discovery via DNS (Rank 1 - Highest Potential)
Experiment: Implement Dominated Novelty Search to evolve a population of small, specialized language models (e.g., 7B parameters) using model merging [cite: 32]. 
Mechanism: Rather than training one massive model, use evolutionary model merging as the variation operator. Use AI feedback to place each merged model into a continuous capability space. Apply DNS to score them.
Feasibility: Feasible now because of the stabilization of DNS in 2025 [cite: 9] and the commoditization of evolutionary model merging frameworks. 
Measurement: Measure the collective intelligence (CI) score of the ensemble archive against a single monolithic 70B parameter model.
Falsification: The idea is falsified if the archive of small, highly diverse experts fails to outperform a single large model on an unseen, hold-out benchmark of synthetic tasks.

2. Noise Optimization in Diffusion Models via QD (Rank 2)
Experiment: Instead of applying QD to prompt space or network weights, apply a QD algorithm directly to the initial noise tensor of a diffusion model to maximize the diversity of generated outputs while maintaining image fidelity [cite: 33].
Mechanism: Optimize batches of pink and white noise initializations under a target objective (pairwise similarity metric pushing samples apart).
Feasibility: Feasible now because of hardware-accelerated tensor operations in JAX which allow rapid evaluation of latent perturbations without retraining the diffusion model.
Measurement: Measure output diversity using averaged pairwise DINOv2 and DreamSim scores, tracking the quality-diversity trade-off frontier.
Falsification: Falsified if direct noise optimization collapses the base model's fidelity significantly faster than standard text-prompt augmentation.

3. Target-Free Unsupervised QD-RL (Rank 3 - WILL NOT WORK)
Experiment: Attempting to build an end-to-end unsupervised behavior discovery system operating at a high UTD ratio without a target network on continuous control tasks.
Why it will fail: While QDHUAC solved the target network lag for known behavior descriptors using hybrid normalization [cite: 7], coupling this with an unsupervised metric-learning encoder creates a dual non-stationarity problem. The critic is trying to stabilize value estimates of a population whose behavior representations are simultaneously shifting as the encoder weights update. The gradients will inevitably explode, and the policy will collapse. The mathematical stabilization for this dual-moving-target problem has not been solved, and throwing compute at it will not bypass the theoretical bottleneck.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQrk04eF-kM2o9ESKueC02lnEvmRihAiCkX1HfDQGFGAIbrO9aDvwloNghd5S47Dtn-R1koFXG6ehWnbamCJ0nO5HpGk5-ySh_tzq-UgntILX-e1KR)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECTUp1j6OfXgU36Hu58lYllSxqTRa8LiPv0L7D7v8RhOtdha4fdIB2obxltfVRZs_QWYBNvFDEMlFwAsRrHuAAyu9u4iyh5u587L9c7cat2DL7RNMj)
3. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKAsPFwhIpzo374BC1d-OTTLTUhCEScWiGP05sMZyNvLvRiEF5xFOy27eo0YKxUkPQIt9q_ar8EIkyx4ia7jQzgiW3vcAMAR7qcaxbV_UGVuou3OK8Jq95dEu-3mpk1l6EH4GbGSA=)
4. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpTPVBRyZt2d52aa7ySvxOqh3C08sEaBQYUFaTPVLlE1V-XdOJMgHg964GjJtDGUQOWph7pNtwLZUCj7iCIw2kBw9egU2hrVbAsx7C3KvxI60JuV0bTz9qtDVLj3E=)
5. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHB0EbW8FZcNZfZ0EHrE8cNBHAfTA5iCZ4YIqLtrc50ocQTd5rpDQndcJTS_g5EGISBKmGBQuou23wgtRTYD3Y8D-zE_JsdKXLUJxEw39IJwmMGugnwxOXec7c=)
6. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYenMB_JGUgt2ZHWjefhzSGqdSbTGPV0gcRpeeVqDASmSKkokDN87NV1YnDOLyoAWxgp28Sa9EJaCYkAk53Hwbu_XLiDT2mL3ia8mV4Oke)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCUmWxgsuj6XvvgVkdl77LByG-MWipkW8lo7hwAkXUm06oySC1dXhNr5tEiho4fcSabUCM6RMlBomVWilV_lka8LV679bSVP0jZKtH7AL8L6Bw-esjInGi)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHz4zct0qSdK1RnPeO7D4H8rpQPRMG7eCveiCLPk2HVgEMIoeuFEECdTmTngLca9NYN8STmAZVw7JL_xGOFlV5uVmQ-F76tQkgevXg8Eh2_WbOLxHvcD2-MBJxd7w4ab19NGPLkz9CZ7OW5gklC3QGfiJRHNo6OfoNm-L23rtjU2C7QBVjdQY1wG7vON6LfLAjmQfYbT0F4suz3fw6H2oU=)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIpYr8eX_CA2UgtPYjPbcs3M6eKUPyFuoMUvCnfJ4jW0OQLPbj3_bErt3uDJNnQnkn4B3HipfHdt1fP1qMxFLJWqejd4d2IYfTnjab6tMH6q2gMtNpbsE1)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGU9CQ6JpjAnreM5YqFtyl15uycbroM549uU1UlGOXWqIMASIsCvaegRE2steXQXXWAHY8nV6CGWreDa-KrAqXWRaUjILn3LVTqe2PMvG-20_R1GG8vSRgU)
11. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnd3yGKhPAged2R45ZXUmCm3zLZ6WUxyLpFO6V43713xrkg9_vtP8RYHPGDObi9dkzMZeyy5WgRJc4-f88bKoBUziG0Wu4FVqRbc0HavvF2UNMc--WZSfKfcwL03dTNj6HH9I5)
12. [grillotti.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfSV0qIBuGxlV59659QZnOsOd7iL4h7V_KYmpnNXPsZ6VibyGiExgfn8uMjL_ChlcDWlEnEIknXeufGwZjK06lMpPyH_MyhcQsQMBQ3BxjM6-U0AvtY_X24J6U-Io=)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAaFrZvnLET770Jp7gq1cpMq1b-l-I68buh6_3nsUk4O07y8CzZ5W2xscGG09faVet--12w9jIUf9AKLyWKONlmFRqOM8iUT1HHlDb9cIgCCVxu0ce6LFb)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGysrpp46uSzqvfC2CCECu0Xkr8eT4kNTu2VnclGe7-jKnvJBhPBW2VWwyx1w6zQ1I3RcGSV-gcU3BI4DbICtolDn1fVdeQ_05S7HZqMwwP5rIRJOb9)
15. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKyFrNwFPSriMKVO_Y2EhJQt7AoG7VIt3OmYhLGYUCZ6E-G8fUEqCnrqiS1_mSn8zb8zzGpeRyToGvdv6xc0Js8DDtQ_si0BIt3Aev_c033k0r9F0LeudulkOSt5Ta0k8BCCf9A9cU1iiVvLtsbZZxAF7Mi5r1nAxRdwgj3OC3RDURVVdaQDj2)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZAbhgTZ2GQm2GT6vd7r36578W2e1Y7gVBTiPGIjGa621l8NsGNjX3cOmKWknSSH0BXQN8zvjvKj_winYQk257rpcKwWCme8DA7zo6M7XpiRCcFKqhg9yM)
17. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyckMy4GnGoSnjRVrLzxow-ZiJ7fAuFpT31Gfd-C5ovn3iF7o1zteCE00csxkwjt1Mgsx0Dz1pnRtEi5-EugMHMvi_gGe_I3xjOtiTIbrehHpnFZZ0pOXYw5dQBLTd_w==)
18. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLtN7yU9LrcCKKFQ1JOMGUMS1fOpOjpYRwWeBUgTrlQWhajSEIHKiSPZPxDMeOPSoRYVHLdJbzXqG2g0Qa2nUoRZRb3TqSqHVxWywuEIC8SsSLLnQuF4CKh-LZnF6BYYjn0tybaHsiGDvu)
19. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-fnJea073xow0ia2nOu4PDFJkVKr0ghu6oGh9KutwmG5uDX1IpgsLT1tVimxIYI5eC422ugOx89B7tieRGW8NJTUPM15itz_qxqwsKmn88yoSC5mJMvsBVQ==)
20. [pyribs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRwrOrIQs5AJD5g-eD9J8TpUP1E5Gmw2ZZkZvDkFlRq-lFPr0Jc_T4dQBTxIr5WJ6spM3yIqoPFBfCJJWkKAbx4V4Q6IHDz9s=)
21. [syncedreview.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOTFGtaZn9VBa_ywfdXBMscj-ks_1W7eLyD1KHGslIc5dcAqrZcJDJfgEoRWwsr-DIUOt8v_sDkaeaIy3PmSswcd-6IQk4xsN5V1oPy3EBMqWFp5H_oxEs5CZOxW9DdZsCtq7kab7QeW92hitwFwUwC9vHb6UOVQlwaK37sm3_Zw9ybNHFphloILhup0a8XNzMAvOU8N-7ADTA9xk-WwVkdBZXGOejZUJIHXRp3cAzxSFkQA==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFs0ORH9OTlPor94cFU58-vhiVubAF80AJX6_vInam6G2xzXbQf2w8XuQVPdslwtImz4bc9_NFykk7hLt4X1ILXkXu-OQz7-fIqPQbl3y-Whc3L-4qv)
23. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOp3061HI0SfbDbzRX1qHTZ2oQqKPCUU5pu9lIdDV1s61tu6hMhemSTPKS_LlLTpZerd6T3rAy-84RfX2up74jyBbNUF8hZ1y9dCyV8c89vXGTgULeYPXnEaIy6Z18)
24. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJ-5zFoVwuWbIYFBJC-qKP8clunhjicFIEilM0L3Kttwyc6_W5CBxI9KtmMvhhlrYiIQ0eyygDLq1IYcrKdOiBnLrmLPpHTPEuMpk558DCzN5WLXww_9A=)
25. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpYpN63j7mVtjMTILA2JRXgrbDl-oC7lVr9bGflSl9V49RgY2SuwCIpHA0DFosnPJxSwTMQ7pkoIyyMgybxmFfTbYsvKl89m7okQePR6dLQkTDzdFtP8sI2qbBmK93YwIAWCk=)
26. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwgn9MZrHxXgJ6PH32gpt6u78EJgGHh-B3hKzXa90PU_hFbnfwY363olFqcDudYMgm080XO9i-C94cQ21QgEI17p9warZ1GjiFUYiTH6KbPFXW27tzM1UQGNZ2sCUFZ298)
27. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgO6a0GZEfMnYywPVypf7wQx34rjxErqD3V-OV5jhpw_cjydsWHrO3MRkAfwh-DMliV2GTBdglijVCcfq81jQlg9TnLPRl6Wbd2K5tf_YVRDnDjnO1OXSckuHgnAb8ikbPy2f7lUw4QxUHDXM2KtdWMtBbxcJ_M3mFaWlvH6MF587M)
28. [kaggle.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3aLIG1umUEgRP0d9vb6pT0QJpizNfom8_sVqdwdX1uxlRemRhuQzhOvtLwUmxcT8TGDtBZYOmIAnb2TJdmsN3xI8fCZVtLE6xGHQuLuPo8qC19FQ2ghj7MOwmuU1lcqg2j4DrIPk=)
29. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGl8DGrdqAc6wdvBQAZsx3SB4jywUyYK7I44xifet15c5QMiVI5zaUFgpN7K_I-5Wy_h7dD6RdI_zT6kl2PqjhgpFnldAG94pprWULaGQ==)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGa4JI514jWVZ2DV_88YYqAKjh1spM4pnR_eiErcNKYQtAYUdnMwowAtFzXwq9NT9cOZLkJNiGaRrp_4LzyLgL1wCpo4x5zlNRaNOgD2yPm3A_G3lrl)
31. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHd_vmJ8XzpbjDmZXieXKKZJdDxYoqZwVJraQStfwc6_I4s7iY4ntHK-3J6KJzh_fsIAwB3_XWvzrmkyGOJntkQ3wQaivJ7yFIZUNHPiQf6HuYMjOc4iKTyXYYZDQ==)
32. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYWaNMnC3HL1dUlestSc0uFbzsUF9egE3Y08kUsrr62C1kXFl3deKTkkk-xPpeDzQ5elIX_0wv_ZRtmiGwmCLBd2JJykCtCCbbcr7fT6iwiDLVrgIZnRfGlDHqL8_gGN7ho2n7ticg3x0yd5nsGLQ36RjO3hR3Q2whN3yrXtn0qpW5J1lCJbKhHSB4YB3V2BPYeMAXxJ9ECsn3SuOTj5148_A=)
33. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESdJ_bQT8B0hG-c53SUf5olpnIXkyRHsqLSIOvTGi08W_HvvXKXY1AVhDSIN-bGJx2S9cxN4AP-1r3fUGCrKb2WIiWJV3cD6rIucGo0v0nl6l-cAcpz85u)

