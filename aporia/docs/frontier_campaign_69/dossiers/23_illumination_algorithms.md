# Prompt 23: Illumination Algorithms

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdpVXVmYXNENEc4amdfdU1QMTQ2TThRSRIXaVV1ZmFzRDRHOGpnX3VNUDE0Nk04UUk
**Elapsed:** 364s

---

# FRONTIER PRACTITIONER DOSSIER: Illumination Algorithms

The field of illumination algorithms, now formally recognized as Quality-Diversity optimization, has transitioned from a specialized niche within evolutionary robotics into a foundational primitive for modern artificial intelligence search methodologies. Your understanding of the anchoring method is precise and conceptually sound. The process of discretizing a behavior space into a grid, retaining a single elite solution per bin, and utilizing those elites as a genetic stepping-stone gradient to illuminate a search space describes the canonical Multi-dimensional Archive of Phenotypic Elites algorithm [cite: 1, 2]. However, this foundational mechanism has been massively expanded. The field has moved beyond scalar performance and simple genomes into differentiable continuous spaces, hardware-accelerated tensor operations, and qualitative domains where Large Language Models act as both mutators and evaluators [cite: 3, 4, 5]. This dossier synthesizes the specific software stacks, essential literature, required tooling, and standing critiques necessary to run frontier experiments today.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER
Quality-Diversity optimization in 2026 operates at the intersection of evolutionary computation, deep reinforcement learning, and generative artificial intelligence. The core premise remains unchanged: rather than seeking a single global optimum, the objective is to illuminate the entire search space by finding the highest-performing solution for every distinct behavioral niche [cite: 2, 6]. The field has successfully proven that maintaining a diverse archive of high-quality solutions prevents premature convergence and solves highly deceptive fitness landscapes that trap traditional gradient descent or reinforcement learning agents [cite: 7, 8].

What is SETTLED: The foundational architecture of Quality-Diversity is settled. The separation of a solution's representation (its genome) from its behavioral descriptor (its niche) and its fitness (its quality) is the universally accepted operational model [cite: 2, 9]. Furthermore, it is settled that the Multi-dimensional Archive of Phenotypic Elites algorithm, and its covariance matrix adaptation variants, outperform simple multi-objective optimization algorithms in maintaining diversity [cite: 8, 10].

What is CONTESTED: The primary live disagreement concerns the integration of gradients. On one side, researchers advocating for Differentiable Quality-Diversity argue that when objective and measure functions are differentiable, ignoring exact gradients is computationally wasteful. They champion algorithms like Covariance Matrix Adaptation MAP-Elites via a Gradient Arborescence, which uses gradient ascent to rapidly fill archives [cite: 3, 11]. On the opposing side, purists and reinforcement learning practitioners argue that exact gradients are rarely available in real-world stochastic environments or discrete domains, and that approximating gradients introduces catastrophic noise [cite: 12]. This side favors hardware-accelerated, derivative-free evolution strategies heavily parallelized on graphics processing units [cite: 5, 13].

What is OPEN: The field is currently grappling with qualitative and unbounded search spaces. Traditional Quality-Diversity relies on algorithmically defined, low-dimensional behavioral descriptors. However, frontier research is attempting to illuminate spaces where behavior cannot be easily quantified, such as creative writing, subjective image generation, or semantic adversarial attacks [cite: 4, 14]. How to dynamically define and scale behavior spaces without succumbing to the curse of dimensionality remains an open frontier.

What changed in the last three years: The most significant shift since 2023 has been the absorption of Quality-Diversity into the Large Language Model ecosystem. Frameworks like Quality-Diversity through AI Feedback and Red Queen have replaced traditional mutation operators with language model prompting, and replaced hardcoded fitness functions with language model evaluators [cite: 4, 15]. Consequently, a large segment of the field has pivoted from evolving robotic gaits to evolving semantic attack strategies and generating synthetic training data [cite: 16, 17]. The field has not been entirely absorbed, but its center of mass has definitively shifted from robotics to artificial intelligence safety and automated red-teaming.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Mouret, J. B., and Clune, J.
2015
Illuminating search spaces by mapping elites
arXiv:1504.04909
This is the original paper that defines the Multi-dimensional Archive of Phenotypic Elites algorithm you described in your query. A practitioner must read this to understand the core mechanics of grid-based behavior discretization and elite archiving [cite: 7, 18].

Pugh, J. K., Soros, L. B., and Stanley, K. O.
2016
Quality Diversity: A New Frontier for Evolutionary Computation
DOI 10.3389/frobt.2016.00040
This paper formally coined the term Quality-Diversity and unified various illumination algorithms under one conceptual umbrella. It introduced the QD-score metric, which is still the standard for measuring the total quality of an illuminated archive [cite: 1].

Fontaine, M. C., Togelius, J., Nikolaidis, S., and Hoover, A. K.
2020
Covariance Matrix Adaptation for the Rapid Illumination of Behavior Space
DOI 10.1145/3377930.3390232
This paper introduces Covariance Matrix Adaptation MAP-Elites, merging the quality-diversity archive with adaptive search. It is highly load-bearing because it proves that emitting solutions via continuous adaptation is orders of magnitude faster than naive random mutation [cite: 10, 19].

Fontaine, M. C., and Nikolaidis, S.
2021
Differentiable Quality Diversity
arXiv:2106.03894
This establishes the Differentiable Quality-Diversity problem formulation and the Covariance Matrix Adaptation MAP-Elites via a Gradient Arborescence algorithm. It is required reading for anyone operating in continuous spaces where exact gradients are available, such as latent space illumination [cite: 11].

CURRENT SOURCES

Chalumeau, F., Lim, B., Boige, R., et al.
2023
QDax: A Library for Quality-Diversity and Population-based Algorithms with Hardware Acceleration
arXiv:2308.03665
This paper defines the modern hardware standard for the field. It demonstrates how just-in-time compilation and massive parallelization can reduce algorithm runtimes from weeks on CPU clusters to minutes on single hardware accelerators [cite: 13, 20].

Bradley, H., Dai, A., Teufel, H., et al.
2023
Quality-Diversity through AI Feedback
arXiv:2310.13032
This marks the frontier of qualitative search. It replaces traditional mutation and evaluation with Large Language Models, allowing Quality-Diversity to run on creative writing and text generation domains where explicit metrics cannot be programmed [cite: 4, 21].

Mitra, S.
2026
Quality-Diversity Evolution for Discovering Diverse Vulnerabilities in LLM Safety
arXiv:2606.00801
This paper introduces the Red Queen framework, applying Quality-Diversity to adversarial red-teaming. It is crucial because it demonstrates that operating at the semantic strategy level rather than the token level avoids mode collapse and discovers distinct vulnerability profiles in frontier models [cite: 14, 16].

Fontaine, M. C., and Nikolaidis, S.
2023
Covariance Matrix Adaptation MAP-Annealing
arXiv:2211.03181
This paper addresses a critical flaw in previous algorithms: distortion in high-dimensional measure spaces. It introduces a discount function that dynamically updates as the archive fills, representing the current state-of-the-art for black-box continuous Quality-Diversity optimization [cite: 22, 23].

Flageat, M., Lim, B., Grillotti, L., et al.
2022
Benchmarking Quality-Diversity Algorithms on Neuroevolution for Reinforcement Learning
arXiv:2211.02193
This is the definitive text on the challenges of applying these algorithms in stochastic environments. It introduces corrected metrics for maximum fitness and coverage, which a practitioner must understand to avoid reporting illusory performance due to noise [cite: 24, 25].

Rojas, L., Yepes, V., and Garcia, J.
2026
A survey on Quality-Diversity optimization: Approaches, applications, and challenges
DOI 10.1016/j.swevo.2026.102240
This is the most recent and authoritative survey available. It synthesizes the shift from robotic motion planning toward discrete combinatorial domains and deep neural network integration [cite: 8].

PART 3. SOFTWARE I CAN ACTUALLY RUN

QDax
https://github.com/adaptive-intelligent-robotics/qdax
Python and JAX
MIT License
2024
MAINTAINED
This is the community standard for hardware-accelerated algorithms. It can run massively parallel Multi-dimensional Archive of Phenotypic Elites and policy gradient hybrid experiments on Brax robotic environments in minutes instead of days. Its primary limitation is that it requires environments to be entirely written in JAX; you cannot plug in a standard Python or C++ simulator without rewriting it or enduring massive memory transfer bottlenecks between the central processing unit and the graphics processing unit [cite: 13, 18].

pyribs
https://github.com/icaros-usc/pyribs
Python
MIT License
2025
MAINTAINED
This is the bare-bones, highly modular community standard for logic and orchestration. It provides the archive, emitter, and scheduler primitives necessary to run Covariance Matrix Adaptation MAP-Elites, its annealing variant, and gradient-based derivatives. It runs linear projection benchmarks and latent space illumination on generative models out of the box. Its limitation is that it does not handle parallel evaluation environments inherently; users must write their own orchestration layer using Dask or Ray to distribute the fitness evaluations [cite: 19, 26].

Red Queen
https://github.com/bassrehab/red-queen
Python
MIT License
2026
MAINTAINED
This is the frontier reference implementation for semantic adversarial testing of Large Language Models. Today, it can run multi-model evolutionary jailbreak campaigns against models like GPT-4o-mini and Claude 3.5. A known gotcha is its heavy reliance on application programming interface calls to proprietary models for both generation and fitness evaluation, which can incur significant financial costs and rate-limiting bottlenecks during large evolutionary runs [cite: 27, 28].

EvoJAX
https://github.com/google/evojax
Python and JAX
Apache 2.0 License
2025
MAINTAINED
While primarily a neuroevolution toolkit, it serves as a sister project to QDax and implements several evolutionary strategies that are highly relevant. It can run hardware-accelerated continuous control tasks. A known limitation is its steep learning curve for users unfamiliar with JAX vectorization paradigms [cite: 29].

dqd and dqd-rl
https://github.com/icaros-usc/dqd
Python
MIT License
2022
DORMANT
This was the canonical implementation of the original Differentiable Quality-Diversity algorithms. It is effectively dead as a standalone repository because its core components have been refactored and merged upstream into pyribs. Practitioners should not build on this repository; they should use the gradient emitters now native to pyribs [cite: 3].

PART 4. DATA AND BENCHMARKS

Deep Neuroevolution Reinforcement Learning Benchmark Suite
Access via QDax repository
Less than 100 megabytes for environment definitions
MIT License
This is the authoritative benchmark for continuous control tasks. It contains standardized environments, behavior descriptor definitions, and fitness functions based on the Brax physics engine. It is used to measure an algorithm's ability to navigate high-dimensional parameter spaces while confronting environmental stochasticity [cite: 24].

Sphere and Rastrigin Linear Projections
Generated dynamically in pyribs
Negligible size
MIT License
These are the canonical analytical benchmarks for continuous optimization and differentiable algorithms. They project high-dimensional solution spaces into two-dimensional behavior spaces. They are used to test the basic plumbing and scaling properties of new emitters before deploying them on expensive domains. They are fully solved by modern covariance matrix algorithms, so they serve as unit tests rather than research frontiers [cite: 3, 30].

StyleGAN and MNIST Latent Space Illumination
Pretrained models via PyTorch Hub and StyleGAN repositories
Roughly 500 megabytes
Various open-source licenses
These are the standard visual domains for testing generative illumination. The objective is to navigate the latent space of a generative adversarial network to produce images that maximize a classifier's confidence while varying defined visual traits. Overfitting is a known problem here; algorithms often exploit the classifier's artifacts rather than producing genuinely diverse images [cite: 3, 30].

Red Queen Safety Prompts Taxonomy
https://github.com/bassrehab/red-queen
Tens of thousands of prompt variants
MIT License
This is the emerging frontier task collection for semantic adversarial testing. It contains archives of evolved attack strategies across various behavioral dimensions such as encoding methods and roleplay personas. It is used to measure a model's vulnerability profile. Contamination is a minor risk as base models constantly update their safety filters, making static baseline numbers difficult to reproduce months later [cite: 16, 28].

PART 5. THE REPRODUCTION RECIPE

The most reproducible, informative, and structurally representative experiment in this field is the hardware-accelerated illumination of a robotic locomotion task using QDax. It completely bypasses the cluster orchestration headaches of previous eras by executing entirely on a single graphics processing unit.

Exact software and version: QDax version 0.3.1 running on Python 3.11 with the corresponding JAX and JAXlib versions installed for your specific graphics processing unit.
Exact dataset or generator: The Brax Walker continuous control environment, accessed natively through QDax task wrappers.
Parameters:
Algorithm: MAP-Elites
Behavior Descriptors: Proportion of time spent with the left foot touching the ground versus the right foot.
num_param_dimensions: 100
init_batch_size: 100
batch_size: 1024
num_iterations: 50
grid_shape: 100 by 100
Number of independent replicates: 5 independent runs.
Seeding regime: Fixed random keys ranging from 42 to 46.
Approximate compute cost: Less than 15 minutes in total on a single NVIDIA A100 or V100 graphics processing unit.
Expected result: A coverage metric approaching 1.0 and a densely populated quality-diversity score heatmap. The exact baseline numbers to compare against are found in Chalumeau et al 2023, Figure 4, which demonstrates MAP-Elites baseline performance on Brax tasks [cite: 13, 20].

The three most common ways people get this experiment wrong are:
First, failing to compile the evaluation step. If the JAX just-in-time compiler decorator is missing or forces recompilation on every loop due to dynamic batch sizes, the experiment will take days instead of minutes.
Second, evaluating stochastic environments with a single seed and treating the resulting fitness as absolute. Because the Brax physics engine involves slight initial state variations, high-performing outliers in the archive are often just lucky evaluations that fail catastrophically upon re-evaluation [cite: 24].
Third, grid dimension mismatch. Users often attempt to add a third or fourth behavior descriptor without realizing that grid bins scale exponentially, leaving the archive effectively empty and preventing the algorithm from crossing local optima.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

A Stochastic Re-evaluation Scheduler Layer
No off-the-shelf tool gracefully handles the illusion of performance in stochastic environments. If you use pyribs or QDax in an environment with noise, the archive will slowly fill with solutions that received luckily high scores. A serious entrant must build a scheduler wrapper that periodically samples incumbents from the archive, re-evaluates them with new random seeds, updates their moving average fitness, and evicts them if their true performance falls below a threshold. The interface takes an instantiated archive and a stochastic evaluation function, and outputs a corrected archive. The hard part is balancing the compute budget between exploring new solutions and re-evaluating old ones. This has been rebuilt privately by at least three different labs focusing on reinforcement learning.

Heterogeneous Cluster Orchestrator for Large Language Model Evaluation
While pyribs handles the algorithmic logic, it outputs a batch of candidate solutions that must be evaluated. If you are doing frontier work like Quality-Diversity through AI Feedback, generating variations and scoring them requires querying large parameter models. You must build an asynchronous dispatcher that takes the array of genome strings, batches them to a vLLM or TensorRT-LLM inference server, handles rate limits, parses the unstructured text outputs back into scalar fitness and behavior descriptor coordinates, and returns them to the pyribs teller. The hard part is handling silent failure modes where the model refuses to output proper formatting, which crashes the evolutionary loop.

High-Dimensional Codebook Generators
Standard grids fail beyond three dimensions. Centroidal Voronoi Tessellations are used to discretize higher-dimensional spaces by generating thousands of reference centroids, but computing these via k-means clustering in spaces with hundreds of dimensions is extraordinarily slow. You would need to build a graphics processing unit-accelerated centroid generator that interfaces directly with the archive initialization phase to dynamically cut the behavior space based on the distribution of early evaluations.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

Using Performance as a Behavior Descriptor
A historically common mistake by newcomers is to include the objective fitness score as one of the behavior descriptor axes, reasoning that they want a diverse spread of low to high-performing solutions. This completely destroys the algorithm. The fundamental mechanism relies on separating what a solution is from how good it is. By making performance a spatial dimension, the map naturally clusters its best solutions at one extreme end of the axis, defeating the purpose of uniform exploration and trapping the search in a narrow corridor [cite: 9].

The Stochasticity Illusion
A standing methodological critique of the field is that many highly cited papers from the late 2010s reported archive maximum fitnesses that were entirely artefactual. Because algorithms like MAP-Elites query the environment millions of times and only save the maximum observed score in each bin, they act as highly efficient noise-maximization engines. When independent researchers attempted to replicate the gaits of evolved simulated robots, they found the policies failed instantly. Flageat et al formally addressed this critique by introducing corrected metric protocols, but many benchmark tables in older literature remain uncorrected and non-reproducible [cite: 24, 25].

Dimensionality Collapse in Differentiable Quality-Diversity
When Differentiable Quality-Diversity was introduced, it was assumed that having exact gradients for the measure functions would solve high-dimensional spaces. However, early programs attempting to scale Covariance Matrix Adaptation MAP-Elites via a Gradient Arborescence to high-dimensional measure spaces failed. The gradient descent step caused solutions to warp and cluster into tiny, dense regions of the behavior space, leaving the rest of the archive empty. This distortion artifact required the invention of the annealing variant, which dynamically updates cell acceptance thresholds to force the gradient search outward [cite: 22].

Mode Collapse in Red-Teaming
Prior to the introduction of illumination algorithms, the standard method for automated adversarial testing was using one Large Language Model as an attacker to iteratively prompt a target model. This program failed to generalize because the attacker model exhibited severe mode collapse, repeatedly exploiting a single discovered vulnerability and ignoring the rest of the target's attack surface. The critique stands that automated red-teaming without a quality-diversity archive measures the attacker model's bias rather than the target model's true robustness [cite: 27, 31].

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Ranked experiments for a well-resourced newcomer:

1. Cross-Generational Semantic Transfer Attacks on Proprietary Models
Build on the Red Queen framework. Do not just evolve attacks against a single model; run the algorithm across different quantized sizes of the same model family simultaneously. It is now feasible because open-weight models and inference engines have democratized massive batch generation. This experiment would measure the non-monotonic safety alignment across generations. You are looking to falsify the assumption that newer, larger models are strictly safer than their predecessors. Finding a behavior bin where a mid-generation model fails but older and newer models succeed would prove that safety regressions are localized and structural [cite: 32].

2. Grounded Synthetic Data Generation for Alignment
Use Quality-Diversity through AI Feedback to illuminate the latent space of a reasoning model. Instead of generating adversarial prompts, generate diverse, high-quality reasoning traces for mathematical or logic puzzles. This is feasible now due to the drop in inference costs. It would measure whether an explicitly diverse archive of synthetic data fine-tunes a student model better than a homogenous dataset generated by standard top-k sampling. It would be falsified if the student model trained on the diverse archive shows no performance gain over the baseline on out-of-distribution reasoning benchmarks [cite: 17].

3. Unsupervised Skill Discovery via Hybrid Hardware Acceleration
Combine QDax with an unsupervised behavior discovery algorithm. Instead of manually defining the behavior descriptors, use an autoencoder that compresses the agent's observation trajectory into a latent vector, and use that vector as the behavior coordinate. This is feasible now because JAX allows the neural network training and the evolutionary loop to share the same hardware state without transfer penalties. It measures whether completely task-agnostic exploration can pre-train an agent to solve downstream zero-shot reinforcement learning tasks. It is falsified if the discovered skills fail to map to any useful physical action [cite: 2, 5].

What will NOT work:
Attempting to scale standard grid-based Multi-dimensional Archive of Phenotypic Elites to behavior descriptors with more than six dimensions. Even with infinite compute, the geometry of high-dimensional spaces means the volume expands exponentially. A grid with ten bins per axis in ten dimensions requires ten billion evaluations just to put one solution in every cell. Newcomers frequently try to add more descriptors to capture complex behaviors, resulting in a sparse, disconnected archive where local competition completely fails. Unless you use Centroidal Voronoi Tessellations or vector-quantized autoencoders to enforce a low-dimensional manifold, high-dimensional grids are a dead end.

**Sources:**
1. [frontiersin.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAEN_znkePmz5Kfjt6n-e_VTxX0kXK6tWUUValszhi_oqNqJ-pJmx4Vh1pRTRJrQx3sdTVJbNCyU4n7Gs6Ix2ZGyHPyMoRofFmTwmhwVZ1FL2llRRxyMs9qMUYggnChoVxgYYvxKMgzdcXH6zTCmAoWKr0FWCTHb9_InOS2PFz9Tar6ZGQMnoxArAvdLU60sQ=)
2. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuM2YMUAGZ1t9rDw7aIUyYQjEKndAeJxftU5tmRfVDG2I28ES05zm55IKvyNZICKc1tIiHqxadonMOAWe-N7EoQOq4WxM4PXAYKZgGa2WxOITRBXnfNxWDYIKF8KHYNNE6X7A5TWfzc5NmWazthATBEF53QA==)
3. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8rzDzFhYI9YvgLWTfuP6C-50ZzXW5dIGnPpiK7NYMxZ-H8dNTKoq3dQSV-1WNDg5tc2jet7u3tvpYFQ2uv4Gv4uz0L5RX766jndwc363pN48Em-g7sg==)
4. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHI1B22q8HZ1_ZHQk25bbptW7_8hY7ky1Ahf7weAZCj1imTIU-JutnBOMMxdy1vyRl4c1w5UbfTU5J1v0OZ0Tvm3pu9OJakPXlbNI_Bjw==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEHI6oyetIgFGcNujTJf7Uu1OLHiZ9YrUltr1igXXsrLxU_ayEvn6FOvbZGJfYKO2tmSGzf1gpBtdNXnXT4ukpvS17u9AQVl6s13iiv94NC-bgrZnEmiKv)
6. [pyribs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZv4RcgttyRkIJVeP7oYdFl_gHv6p7n7xV12HuAGtNiRT3VxyiJN0jsK3e8uYAD_eZSopqlMZhiAzxQqq22Vlfob0DkPsr11KC4_Aotzk=)
7. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFH1f9L4U8bNvLPp-lkVFhLueZu4EgM6eNHwQudP1VNziYbBdyWcHNhnilLaOnGqZ8okQ8Rx7NzhImr5q0A7YnfsM-aXRziU2YMUDXcMoJqcAyXRZ4RfZ4fVS62k1oHTTVvRrje)
8. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEX6QexqnndT_I93UoQ2Eg96JhSYSYZEPNNRHCOeicESmfjlhJpIVOQJj4bg4QZdlUvPh_fMqnbRMtJYMxWgRgUKbnSwt2gXU82Nye2Lb814kbAeq1YbB8gZfXjaFk=)
9. [parasdahal.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrnI8amrn4fLUNQgoXPyy1mFB0IAaqqO0KKslPpFsu8XI4XR0GPWEOWrD_4SszH34ajRcSzB67OUp0T-5AS-AxgTD1LlyYn-RVdBlcBgnXmOTuTTU2tJ_ougeL3g==)
10. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-7iWmJ7LBjNJE5SZV8Hxzbw3BsQzdQXkMUdhMhhryide3Y9qUxRu102xtiyI1PxgXzZ86i6Z0lu2TwEyZGkJmjNfZVf8d2Mg5xHFoGwS276rxqiXOFSqU7w-w5VvnNNSqrrgVjqiyJCu1ZiMOM37Yqdj4OZJZpks8LBN9CtjUrEkYoQIICSk=)
11. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMxL8JQJMzXCO_D-ZAwL57lfRt5c8y1q06hRDv9prkD8MGqd0Ul9BOnLIu-J3IXF1dfF8uGsJjR2YEiOjjRrl19oaiLTSZhF8peR5x32AjWURz7RZm8GvCkPZg5YL3ov8=)
12. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiGiGHyM6JJd-qF-VqxLL-vLM8Zec_rNy7m3UsA2RzzqgTu-ql5pMRzuORGU0lYgGrNeB8X7PRRMJSTXCQ4mTwu_8McKCearWY9skbYWrqzPvIW-TcmU2_dA==)
13. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJBZZgslRSnmVpOBqw3uPApdjIJGczKamtaiSReJLCt40urMAUW3l4XV7CpPzzfVz9nYlujz_HOiKOT01Wz_9ANFixAjhrloos3jJ1WuqNGxRGw7LClhVnKsAutczQzA3j1UPd6v6SLsud)
14. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEG_YiM6jHbzFVJy2FieoATvPTa6E25sxtUCU8B9gGN1gGaQ5j8j1ZHI1MnNecc9AbbNg9A15De1eaELmeR-VujL05BPHOJbCX-KJQ2YOUc_jf24ufrDZZMkhAdlvA6bQ==)
15. [subhadipmitra.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNQzV6iEIa98Ivhtho9KmWluAdHC-VEeETKoZZcCaSCAMCbPp-nIB3GuukAL9OF80G-NhFxL02SnMTOQAcJWIOcrB1-F-g5wm53ItFhkN39k2UHhikeMquohV-8QJHYoQhY0xSUfCrV9Sq5iZ1BDXz92w=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPJwMopA6M5S_6JOJAoWtvFlR_Foo9uyYRabHtNr7mE4EHqHW8eO6iDj3axzFhon9RL_ESOhicgqhC5AJEmYU9z6HBF_X4q_fn64XY9gED4pmkjg5F)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0hjFZdow-8A_kBJycT0zf6OZQ9Es9t-9LzuWOErSFgmEZxENKMyRhV2iHcpJe5cEkDrmvYPHYnfyWFtGXj18iWVvWXRdUQqZT1mgLpnkMdtzkIDyeIR-P)
18. [modelzoo.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtE4mDWEdONk7DIp4ExmT0xqxXNhSk8AZmunVPcY4VozMCemlV1YI7BuOXKaqmwyJXhvHyGWtClz1hwOgg0iHLJLQ0dlpL0oHBw2m7Ac3nR2hRPA==)
19. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETSFsIkhP4aWryQhcD9133U-1fT2QmX0pCz6kJ_SxBMBPLZN5GsYLlzoNcbNxyAFZzv2vOM1wOTjBk0UEQt5qxO-SLPgOFPu_2DEnOsoWCdO8M4UTythrK-w==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWN8GkOroY1FqUPijgUYoVBAttk7OT_aB7aYaPsSZYYm_OF2KDayQh9A1JFAUBXC-U1iqckO7_LxmW5mjPRRKEr0Qc8uI3p8qx5FLw3Tsfnet8SAOb)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFk8BUfKbM4Y7yp_8jkoyw3mLLO6gYvtArAhvXU5oa9ZFZHuZs6kIOUgNV-9yu0q4vOvqJpjtH2AtUbocdABtOIPffozLIi8UuRVa3tIeE-m_Zv-Kau)
22. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGk-ODstG0xV_-Ks1PNvTXDFwtGz8otgJIFhgNYgF0OW2b_MXGePQfmIui_jyyfXU2k7iVrHOnik1UwVqFyqIWJHUJfgFEorARqEp2JWueRDqJWd1mL9cNShmgseeEWoFiMj9Vf1O_-wVZRcAM5IGSHTTGS65dKgHL35oXmf91sqZtSFIhkfwdXL_KK1XCQchGESg_7bemD5pkudHtW_fXvUO4=)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEW0J4ZA8jkAYDYNU1GizJJuA5fRu2CGWGO1Ru4oHKEDdfOh_b3sK5jVt2qE3vvY5GPBLP3l5A1e2i_RcrNcYrHvksrrOOezQnXrcmR1na2ZWmo0InkCEXFxrntnLc6QSrbDziHoIQFWP-bJU7eCVnNzka6pn3bbMtaKY_ik5D0QuXhQwgbDVYIG2I3Ci4Yx0y1iQ==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqmVo237C3IzH0GQQHKIxkoEg1G5EOU-zS31gVvCo9L5W3m0KW_rAh-H--WLMNxyFMMaRYKDskSsZoG6ZNjFmVpaDAhnnHwO194nqvfiXSrrQFQde7W0iv)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7b_B1UaYpJP9yfcSNWFy_J_6FTwKP8T6SP_IAtmUrcIxvQBhD99wYwdTP-6iMBdFPGfhDH18d90FNjOMqCMnhHYdMUoJdKQ1RW058qveDPzI6tl6b)
26. [pyribs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUe8IuS_MOkIeX0ylv4dTpSDrwenymHl3KiYZ3wCFYQprxygkYQpBc9lc6dmVRhJBtfuJizRKd53vWzHDGl1GGmYxaUapyNTc=)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGr1bsDLHBut3fjh90ko89qyg6AEMrJGNS4EaRNwlOyULV3Mpl7DFRlWG_Ta-akaIuLiu0Lq6ZWHwXonPQfBUKXDjB_mKSFN3RKVYVPUW1wj98bnupZ)
28. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHV5HtMULIB3VHN6L5QNcX0H62ma2yZYU0NQgEYunuiyooKyXUz-dkwhcz9ubWH7sGfWOb1MKWSsyWVMylNNTL9xMiKgEqGCPFfK6vemM9_EPHyuaadXD2wTqYU)
29. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFitJ11nBkNcxBU-tU-X-TEF40WzWMNZWHnJhZgNelCaMUbpT2V-7F3yje04RMqo7O17O8DZkNZN6EsOW7VR2_SUWb2qa8UW5bnkO_vowk4BFu0fCYwxKQtyabD-vzhrJrvtxtD4l1_ips=)
30. [pyribs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFf9rM2U_vmkovcBkSLILTAtrRfpa5ghYRXDo_oa5IhWsVGlbwSXLGr9XXm5H02DUNFGpgbfKVpNNFgj500Wvosu6bdm8cte6Zsvumo5-9o6MhcoX1T7Io_lT1B8ePuI2k6FIUvNA==)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQER5kdU0ce4uRVhbsIu0IV6bNk0Nj4572t8otJI7_kiwJQO7NDhWPr5mLi93krBeLE5tkSZVhi0rPzDvDb7mPV-BAnbzO-XtLg5XlIr-okrt8amCiknBkYI)
32. [subhadipmitra.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAjTbT0ahIGCdVdL57926Lx0aJy1UF1SZtJgcAsmnD1QcIAkzwS-PuqkcQByHMvsY0teO4YvQ4TgO7_wIXcSSKGvrRpNB137GqVd0eJuTLkZ2kQBPAWforRr3jJw==)

