# Prompt 10: Symbolic Regression

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdsNldlYXNERUlKUzBfUFVQZ3N1NWlBRRIXbDZXZWFzREVJSlMwX1BVUGdzdTVpQUU
**Elapsed:** 334s

---

# FRONTIER PRACTITIONER DOSSIER: SYMBOLIC REGRESSION

Key points for the current state of Symbolic Regression:
The field has fundamentally transitioned from classical genetic programming to hybrid architectures combining deep learning, reinforcement learning, and evolutionary search.
The classical approach you described is historically foundational but practically outdated; modern systems evaluate on a Pareto frontier of complexity versus accuracy rather than a single error metric.
A major current controversy centers on Large Language Models and whether they are genuinely discovering mathematical relationships or simply reciting memorized equations from their training data.
For a new practitioner, the most viable path involves integrating the structural priors of neural networks with the raw computational efficiency of modern evolutionary backends like Julia.

The evidence leans toward hybrid systems remaining dominant over pure neural or pure evolutionary approaches. Research suggests that while Large Language Models are highly effective at generating structural hypotheses, they still require rigorous external evaluators to optimize constants and prevent hallucinatory physics. It seems likely that the next major breakthrough will come from tight, compiled integration between these neural priors and evolutionary symbolic search, rather than scaling up either approach in isolation.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Symbolic Regression is the machine learning task of discovering a human-interpretable, tractable mathematical expression that best fits a dataset. Unlike standard neural networks that act as opaque function approximators, or linear regression that fits parameters to a pre-declared function, Symbolic Regression searches both the structure of the equation and its numerical constants simultaneously. You anchored this report on genetic programming, and a correction is required immediately: your description of the mechanism is historically accurate for the 1990s and 2000s but is fundamentally outdated for the 2026 frontier. Today, fitness is almost never taken simply as total error. Instead, models are evaluated on a Pareto frontier that trades off mathematical complexity against mean squared error. Furthermore, simple tournament selection and subtree crossover have been superseded by regularized evolution, simulated annealing, and gradient-based inner loops for constant optimization [cite: 1, 2].

What is SETTLED in this field is that pure, naive genetic programming cannot scale to high-dimensional problems due to the combinatorial explosion of the search space. It is also settled that optimizing the continuous constants within an expression tree is notoriously difficult for evolutionary operators alone; virtually all competitive frontier systems now use a separate non-convex optimizer, such as the Broyden-Fletcher-Goldfarb-Shanno algorithm, to refine constants after the discrete tree structure is proposed [cite: 3]. 

What is CONTESTED is the role of Large Language Models and Transformer architectures in discovering equations. One faction, heavily represented by the architects of End-to-End Symbolic Regression with Transformers, argues that massive autoregressive models trained on synthetic equation datasets can predict complete equations directly from data points in a single forward pass [cite: 3, 4]. The opposing faction argues that Large Language Models are largely executing retrieval rather than discovery. This critique is embodied by the recently introduced LLM-SRBench, which demonstrated that when standard physics equations are transformed into unfamiliar mathematical representations, the performance of Large Language Models collapses to roughly 31 percent symbolic accuracy [cite: 5, 6, 7]. This side argues that models are memorizing the Feynman equations from arXiv training data rather than deducing them from the numerical inputs.

What is OPEN is the seamless integration of non-differentiable physics constraints and background domain knowledge into the search process without heavily biasing the algorithm. In the last three years, the field has seen a massive influx of attention from the deep learning community, effectively absorbing what was once a niche subfield of evolutionary computation into the broader AI-for-Science agenda. While the field has not been entirely absorbed, the pure genetic programming community has been marginalized. What was lost in this merge was the guarantee of deterministic search behavior and the deep theoretical work on genetic bloat, replaced by the stochastic and highly parameterized nature of neural-guided search heuristics.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Schmidt, M., Lipson, H.
Year: 2009
Title: Distilling Free-Form Natural Laws from Experimental Data
Venue: Science
Identifier: DOI 10.1126/science.1165893
This is the paper that introduced Eureqa and proved that symbolic regression could automatically discover invariants like Hamiltonians from raw motion-tracking data [cite: 8]. A practitioner must know this because it defined the ambition of the field and established the Pareto front optimization that every modern tool still uses.

Authors: Cranmer, M., Sanchez-Gonzalez, A., Battaglia, P., Xu, R., Cranmer, K., Spergel, D., Ho, S.
Year: 2020
Title: Discovering Symbolic Models from Deep Learning with Inductive Biases
Venue: Advances in Neural Information Processing Systems
Identifier: arXiv:2006.11287
This paper demonstrated that you can bypass the dimensionality curse by training a Graph Neural Network on complex data, then applying symbolic regression specifically to the low-dimensional message-passing components of the trained network [cite: 9]. It is critical because it bridges deep learning and symbolic regression.

Authors: Petersen, B. K., Landajuela, M., Mundhenk, T. N., Santiago, C. P., Kim, S. K., Kim, J. T.
Year: 2021
Title: Deep Symbolic Regression: Recovering mathematical expressions from data via risk-seeking policy gradients
Venue: International Conference on Learning Representations
Identifier: arXiv:1912.04871
This paper introduces Deep Symbolic Optimization, which uses a Recurrent Neural Network to emit probabilities of mathematical tokens and trains it using a custom reinforcement learning policy gradient [cite: 10, 11]. It established neural-guided search as a viable replacement for purely evolutionary search.

Authors: Udrescu, S. M., Tegmark, M.
Year: 2020
Title: AI Feynman: A physics-inspired method for symbolic regression
Venue: Science Advances
Identifier: DOI 10.1126/sciadv.aay2631
This paper introduced a recursive algorithm that uses neural networks to detect properties like dimensional scaling, symmetry, and separability to break down complex equations before feeding them to a polynomial fitter [cite: 12, 13]. It is essential reading for understanding how physics priors can constrain the search space.

Authors: La Cava, W., Orzechowski, P., Burlacu, B., de Franca, F. O., Virgolin, M., Jin, Y., Kommenda, M., Moore, J. H.
Year: 2021
Title: Contemporary Symbolic Regression Methods and their Relative Performance
Venue: Neural Information Processing Systems Track on Datasets and Benchmarks
Identifier: arXiv:2107.14351
This is the original SRBench paper that standardized the evaluation of symbolic regression algorithms against black-box machine learning models [cite: 14, 15]. It is the benchmark against which all modern claims of superiority must be measured.

CURRENT FRONTIER SOURCES

Authors: Cranmer, M.
Year: 2023
Title: Interpretable Machine Learning for Science with PySR and SymbolicRegression.jl
Venue: arXiv preprint
Identifier: arXiv:2305.01582
This paper details the architecture of PySR, the current community standard, explaining its multi-population evolutionary algorithm, evolve-simplify-optimize loop, and Julia-based SIMD kernel fusion [cite: 1, 16]. It is the technical manual for the most important software tool in the field.

Authors: Kamienny, P. A., d'Ascoli, S., Lample, G., Charton, F.
Year: 2022
Title: End-to-end symbolic regression with transformers
Venue: Advances in Neural Information Processing Systems
Identifier: arXiv:2204.10532
This paper challenges the traditional evolutionary approach by training a Transformer on vast synthetic datasets to directly emit the mathematical expression and its numerical constants in one pass [cite: 3]. It defines the current pure deep-learning frontier.

Authors: de Franca, F. O., Virgolin, M., Kommenda, M., Majumder, M. S., Cranmer, M., Espada, G., Ingelse, L., Fonseca, A., Landajuela, M., Petersen, B., Glatt, R., Mundhenk, N., Lee, C. S., Hochhalter, J. D., Randall, D. L., Kamienny, P., Zhang, H., Dick, G., Simon, A., Burlacu, B., Kasak, J., Machado, M., Wilstrup, C., La Cava, W. G.
Year: 2024
Title: SRBench++: Principled Benchmarking of Symbolic Regression With Domain-Expert Interpretation
Venue: IEEE Transactions on Evolutionary Computation
Identifier: DOI 10.1109/TEVC.2024.3423681
This paper updates the SRBench framework by adding domain-expert interpretation and testing for deceptive shortcuts and feature selection robustness [cite: 17, 18]. It addresses the flaw that accuracy and tree size alone do not equal interpretability.

Authors: Shojaee, P., Nguyen, N. H., Meidani, K., Farimani, A. B., Doan, K. D., Reddy, C. K.
Year: 2025
Title: LLM-SRBench: A New Benchmark for Scientific Equation Discovery with Large Language Models
Venue: International Conference on Machine Learning
Identifier: arXiv:2504.10415
This paper provides the most recent and devastating critique of Large Language Models in this field, demonstrating through transformed and synthetic datasets that these models rely heavily on memorization rather than reasoning [cite: 5, 19]. It is mandatory reading for anyone attempting to use modern foundation models for equation discovery.

For surveys, the most comprehensive recent overview is found in the introductory materials of the Royal Society's 2024 special issue on symbolic regression in the physical sciences, which outlines search-space design, complexity control, and symmetry constraints [cite: 20].

PART 3. SOFTWARE I CAN ACTUALLY RUN

PySR
https://github.com/MilesCranmer/PySR
Language: Julia and Python
Licence: Apache License 2.0
Year: 2026
Maturity: MAINTAINED
Experiment it can run: You can use PySR to load an N-dimensional dataset and run a massively parallel, multi-population evolutionary search with customized operators and complexity penalties, returning a Pareto front of equations [cite: 21, 22].
Limitations and gotchas: While the Python interface is seamless, the actual search engine requires a working Julia installation, and first-time compilation overhead can be frustrating. Furthermore, if you define custom operators that are not carefully constructed to handle NaNs or complex numbers, the Julia backend will silently drop invalid expression trees, stalling the evolutionary process [cite: 1, 23]. This is the community standard.

Deep Symbolic Optimization
https://github.com/dso-org/deep-symbolic-optimization
Language: Python
Licence: BSD-3-Clause
Year: 2025
Maturity: MAINTAINED
Experiment it can run: It can recover tractable mathematical expressions by using an autoregressive neural network guided by a risk-seeking reinforcement learning loop [cite: 24, 25]. 
Limitations and gotchas: The original implementation was heavily tied to an older version of TensorFlow, making it highly brittle on modern hardware. While a PyTorch refactor exists at https://github.com/dso-org/deep-symbolic-optimization-pytorch, the repository is split and lacks the full feature parity of the original [cite: 26, 27]. Hyperparameter tuning for the reinforcement learning reward function is exceptionally finicky compared to evolutionary methods.

AI Feynman
https://github.com/SJ001/AI-Feynman
Language: Python and Fortran
Licence: MIT License
Year: 2020
Maturity: DORMANT
Experiment it can run: It attempts to recursively break down a dataset by identifying translational symmetries and dimensional separability using a neural network, before passing the residuals to a Fortran-based polynomial brute-forcer [cite: 13, 28].
Limitations and gotchas: This software is effectively dead. The canonical implementation relies on Python 3.6, outdated PyTorch versions, and requires compilation of Fortran 90 modules that routinely fail on modern Linux and macOS toolchains [cite: 29, 30]. Published results cannot be reproduced easily with current compilers. Serious entrants rewrite the symmetry-detection logic from scratch rather than fighting this codebase.

SRBench
https://github.com/cavalab/srbench
Language: Python
Licence: GPL-3.0
Year: 2025
Maturity: MAINTAINED
Experiment it can run: It allows you to run a standardized evaluation harness across 25 different symbolic regression algorithms and standard machine learning baselines over hundreds of datasets, generating standardized output metrics for complexity and accuracy [cite: 31, 32].
Limitations and gotchas: The harness orchestrates environments using Docker containers for every individual algorithm. Running the full suite takes hundreds of CPU years, so you must carefully sub-select algorithms and datasets [cite: 15, 33]. 

LLM-SRBench
https://github.com/deep-symbolic-mathematics/llm-srbench
Language: Python
Licence: MIT License
Year: 2025
Maturity: MAINTAINED
Experiment it can run: Evaluates any custom Large Language Model via a local vLLM server to see if it can successfully derive equations from synthetic data that subverts common physics variables [cite: 34].
Limitations and gotchas: You are entirely bounded by the context window and token generation speed of the underlying language model. Because it is highly recent, community adoption is still forming, but it is the reference implementation for the 2025 ICML oral paper [cite: 7, 35].

Eureqa
IDENTIFIER UNKNOWN
Language: C++
Licence: Proprietary
Year: 2017
Maturity: ABANDONED
This was the most famous tool in the field following the 2009 Science paper [cite: 8]. It was acquired by DataRobot and absorbed into their enterprise platform. It is effectively dead for academic practitioners. If you see it cited as a baseline in modern papers, the authors are usually using a historical table of results or have grandfathered academic access. Do not attempt to use it.

PART 4. DATA AND BENCHMARKS

Penn Machine Learning Benchmarks for Symbolic Regression
URL: https://epistasislab.github.io/pmlb/
Size: 252 datasets
Licence: MIT License
Purpose: This is the authoritative benchmark collection used by the SRBench harness. It mixes real-world tabular data where the ground truth is unknown, with synthetic datasets generated from known processes [cite: 14, 15]. 
Known issues: Some of the real-world datasets are hopelessly noisy and no symbolic expression will ever yield a meaningful result, meaning they test the algorithm's ability to gracefully fail to a linear model rather than discover a law.

Feynman Symbolic Regression Database
URL: https://space.mit.edu/home/tegmark/aifeynman.html
Size: 100 equations
Licence: MIT License
Purpose: Created for the AI Feynman paper, this dataset contains 100 equations from the Feynman Lectures on Physics [cite: 12]. It is used to test if an algorithm can recover exact physical laws.
Known issues: This dataset is severely contaminated for modern research. Every Large Language Model has ingested the Feynman Lectures during pre-training. Testing a language model on this dataset measures memory, not regression [cite: 5, 7]. Furthermore, for classical algorithms, the benchmark is saturated; modern tools easily solve the majority of it.

LLM-SRBench Dataset
URL: https://huggingface.co/datasets/nnheui/llm-srbench
Size: 239 challenging problems
Licence: Open access
Purpose: Designed explicitly to measure genuine scientific reasoning by transforming common physical models into less common mathematical representations (LSR-Transform) and introducing purely synthetic discovery-driven problems (LSR-Synth) [cite: 5, 36].
Known issues: It is currently highly difficult, with state-of-the-art models peaking at 31.5 percent accuracy, which may lead to floor effects in evaluation until algorithms improve [cite: 6, 37].

SRBench++ Interpretability Tasks
URL: https://github.com/cavalab/srbench/tree/Competition2022
Size: Task specific subsets
Licence: GPL-3.0
Purpose: Used to measure whether an algorithm avoids deceptive shortcuts and selects only relevant features, rather than just minimizing error with an overly complex tree [cite: 18, 38].

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment you can run to understand this field is to use PySR to rediscover a specific, moderately difficult equation from the Feynman Symbolic Regression Database using the SRBench evaluation methodology.

Exact software and version: PySR version 1.5.0, running in Python 3.9 with Julia 1.9. 
Exact dataset: The Feynman I.8.14 dataset from the PMLB repository, which describes kinetic energy.
Parameters: 
You must configure the PySRRegressor.
populations: 8
population_size: 50
niterations: 1000
ncyclesperiteration: 500
binary_operators: plus, sub, mul, div
unary_operators: square, exp
maxsize: 20
Select the equation using the score metric, which optimizes for the best trade-off between mean squared error and tree size.
Replicates and seeding: Run 30 independent replicates with random seeds from 0 to 29. PySR is stochastic; a single run is not scientifically valid.
Compute cost: Approximately 0.5 CPU hours per replicate on a modern multicore workstation, totaling 15 CPU hours. No GPU is required.
Expected result: The algorithm should achieve exact symbolic recovery of the equation in at least 95 percent of the replicates. The benchmark number to compare against is a 1.0 exact recovery rate as reported in the SRBench paper by La Cava et al. 2021 [cite: 14, 15].

The three most common ways people get this experiment wrong:
1. Failing to separate the structural search from constant optimization. If you do not allow PySR to call the Broyden-Fletcher-Goldfarb-Shanno optimizer on the constants of proposed trees, the evolutionary algorithm will waste generations trying to mutate a constant from 1.1 to 1.14, failing to find the true structure.
2. Inadequate complexity penalization. If you only select the model with the lowest mean squared error, you will select a massively bloated tree that overfits the data noise. You must select the model based on the Pareto front score.
3. Ignoring domain constraints. Permitting operators like division or logarithms without guarding against division by zero or negative domains will cause the Julia backend to aggressively reject trees, shrinking your effective population size to zero and causing the search to stall [cite: 23].

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to operate at the 2026 frontier, you will discover that no off-the-shelf tool successfully merges the structural intuition of Large Language Models with the rigorous, compiled evolutionary search engines like PySR.

What goes in: An arbitrary tabular dataset, a natural language description of the physical priors (such as boundary conditions or known symmetries), and a time budget.
What comes out: A Pareto frontier of mathematically rigorous equations whose constants have been locally optimized and whose structures respect the textual physics priors.

The hard part: You will have to build a high-performance orchestration layer. Large Language Models output strings or abstract syntax trees. Evolutionary algorithms require highly optimized binary tree structures in memory to evaluate millions of candidates per second. Translating the language model's output into a compiled representation that Julia or C++ can rapidly evaluate, and then returning the precise numerical loss gradients back to the language model to guide its next prompt, is structurally complex. If you rely on writing Python code strings via the language model and evaluating them with Python's exec command, the overhead will destroy your throughput and security.

Roughly how much work it is: Building a robust, asynchronous bridge between a local vLLM server running a modern language model and the inner representation of SymbolicRegression.jl will take a competent systems programmer two to three months of heavy engineering. 

Private rebuilds: Several groups, including the architects of Deep Generative Symbolic Regression with Monte-Carlo-Tree-Search and the authors of LLM-SR, have privately rebuilt variations of this pipeline [cite: 37, 39]. They write custom Markov Decision Process translators to turn language model token generation into mathematical expression trees. Because these bridges are often tied to highly specific, undocumented research codebases, no generalized, robust tool exists.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The history of Symbolic Regression is littered with failed assumptions.

The Dimensionality Curse: Pure genetic programming fails entirely when the number of input variables exceeds roughly ten. The search space of expression trees grows superexponentially. Methods that attempted to solve this purely by increasing population sizes or mutation rates failed. This was definitively shown to be a baseline artefact; random search essentially equalled genetic programming on high dimensional tasks until deep learning priors were introduced.

The Skeleton and BFGS Failure: Around 2021, a major research direction attempted to train neural networks to predict only the mathematical skeleton of an equation, leaving all constants as placeholders to be filled by the Broyden-Fletcher-Goldfarb-Shanno optimizer. This looked promising but failed to replicate as a scalable solution. The non-convex optimization of nested constants is too fragile. Kamienny et al. definitively answered this by showing that End-to-End transformers predicting the exact constants directly alongside the structure heavily outperformed the skeleton approach [cite: 3].

The AI Feynman Brittleness: The AI Feynman programme looked extraordinarily strong upon publication in 2020. However, the standing critique is that its symmetry and separability detection relies on neural networks that require perfectly clean data. When realistic observational noise is introduced, the neural networks fail to confidently identify symmetries, causing the entire recursive algorithm to fall back to a brute-force polynomial search, at which point it collapses. This critique has never been successfully answered, which is why the codebase is largely dormant today [cite: 12, 40].

The LLM Memorization Artefact: The most severe standing methodological critique of the field today targets the use of foundation models. Papers routinely claim that GPT-4 or similar models can deduce complex physics equations from data. Shojaee and Reddy mathematically eviscerated these claims in 2025. They proved that these models were merely pattern-matching the dataset to equations heavily represented in their pre-training data. When the benchmark was modified to use mathematically equivalent but syntactically novel representations, performance flatlined [cite: 5, 19]. This is a classic case of measuring the benchmark contamination rather than the phenomenon of discovery.

The Interpretability Fallacy: For a decade, the field assumed that tree size equalled interpretability. The standing critique from domain scientists is that a small, mathematically dense tree using nested trigonometric functions is vastly less interpretable to a physicist than a slightly larger tree that correctly isolates the mass and velocity terms according to physical laws. De Franca et al. attempted to answer this with SRBench++, incorporating human expert evaluation, but the metric remains largely unquantifiable natively within the algorithms [cite: 17, 18].

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given you have compute, can write code, and want to run frontier experiments, you should ignore the classical genetic programming tuning wars and bypass the pure deep-learning synthetic generation architectures. 

Experiment 1: LLM-Guided Evolutionary Initialization and Mutation
What makes it feasible now: Local deployment of instruction-tuned Large Language Models via vLLM, combined with the extreme speed of PySR's backend.
The experiment: Instead of initializing PySR's population randomly, feed a random sample of the dataset and a textual description of the variables to a Large Language Model. Ask it to generate 50 highly probable mathematical hypotheses. Inject these directly into PySR's starting population. Further, replace PySR's random subtree mutation operator with an LLM-mutation operator that reads a stagnant tree and suggests a physically plausible structural change. 
What it measures: You would measure the time-to-solution and the exact recovery rate on the LLM-SRBench synthetic dataset (LSR-Synth) compared to baseline PySR. 
Falsification: If the LLM-guided evolutionary search does not reach the hit criterion significantly faster, or if it converges on local minima worse than random mutation, the idea that LLMs possess actionable structural priors for math is falsified.
Rank: 1

Experiment 2: Symbolic Distillation of Video World Models
What makes it feasible now: The recent emergence of latent physical variables inside large-scale video encoders. 
The experiment: Train a basic video prediction model on simple physical interactions (e.g., rigid body collisions). Extract the latent dimensional vectors from the intermediate depth transition (the Physics Emergence Zone). Feed these low-dimensional latent vectors, rather than raw pixels, into a symbolic regression engine to recover the explicit force laws governing the collisions.
What it measures: It tests whether neural networks inherently learn factorized, classical physics equations in their latent spaces that can be symbolically extracted, reproducing the 2020 Cranmer graph neural network results but on raw video representation spaces.
Falsification: If the symbolic regression engine cannot find a mathematically parsimonious equation linking the latents to the next frame, it implies the video model uses highly distributed, non-classical heuristics to predict physics, rather than simulating classical mechanics.
Rank: 2

What will NOT work: 
Do not attempt to build a bigger Transformer and train it on a larger dataset of synthetically generated equations in the hopes of creating a zero-shot, end-to-end symbolic regression model that beats evolutionary search on high-dimensional data. This will not work because the combinatorial space of equations is infinite, and Transformers are fundamentally interpolators. As proven by the failures highlighted in the LLM-SRBench literature, when a purely autoregressive model encounters out-of-distribution constants or unfamiliar physical relationships, it hallucinates catastrophic structural errors [cite: 5, 7]. You cannot bypass the need for a discrete, hard-coded optimization loop by simply scaling attention heads.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3PsjWHB3luTCuOGR-TldGY4DG3jDiYwtil76dyT6ORxyPqrdwFSlHmBQiDa3sEdGSq2sTVRuJMqu8ECyowgoo4yMA0t8BDUXgMXg85PU-VqQE5IjYPg==)
2. [sourceforge.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqH1zFnyLsWKaUrXadbELpziP1TrvWkKjiVbK7KLAosydR44Z5_7TzuHd52Q6K4fEUNSWhBosLyI9mVHuTFCuBF5uJGDKTcamkRx_2-RVigIfnt97bNpo3U0PwwctQ5rBNW7o=)
3. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEk2UdGyi4smKpc2OZJLtLyU4SOshFVltXMOtM3rnEr5HKvBeJrulo0oa9Xur-SBx8aHOewCD-EbvfbBEDG_HynB-WNrw3-CeIxMghzT9y45T8YYGhYbQ0UWR-gAfEHbQ==)
4. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2g2-VZg7x_eeTOa8uoJPLHvbyhp3Mf4T42DDJOG4kBHw4H0QD36_DHFCm_sja5oYDBRhGzrCI2g1Jcf_fLivHDegmJbS3KVfNW6yKRErUY7zOV8M8k0xlj5dTAACYdrp9)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-NLFw5LJJBupKAgtcf-GpxAA2A-Z7ZdGqQX0eJsc4VgZcIOSvYDhY0Q_A2jqbODue0dynubRlz3GKftXfTVicQbTVkAWsRuJndwP8N_l4uLG1d_0HMcX02g==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPuzJOn5qboAboCVmoKVtTRc9VlrLUlzwyAGLLsY5xTZKCAX90frJXGerUF5GWrHLiy6UENWJAxXbqWIdwmhM2cKwICxcR10v2YsQHEOTxukcMYcP0cg==)
7. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEf_tdq_YHDjIojKKC7-3Phqrk2GmLb2ni039EaF8O--RXqfj4V2hGC7OgzaXVI9_gkX1llk46jZofZt1pohcliiCAX3tiBdG0SqHEVK_sGjEi4Pa4Z9-RXp4lhAD4=)
8. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEV9uQVHHUsCAw9Xn6iRXz0RtXTsHvgIMh2p6zTyxnHHHoY13TcSFLGvZXJc7JK71XRd0rYbhi0tOv1uDLppWeeJzlY5OQHL2kI54OVjrE64ALNoFalL2N8H9UKhGbsnA==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNgCqN2FsdGyBgazDDQ7MXu9vl6ZDIjP87UXs6UU9z7OXO5QcXlV6YvESYFuaPNS88skoJWSrXBXHxexJ_46hEniPVjAbYtNuv0MCW6bENUWejCyizYHSGFw==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIGleG-03M-GE5WoNLbG4ZfvANEVUHaRiDsEZ-xQ_TSmmxRJpAWuORMiiAMLh2KWRFCoukx2sbFn2gzTPtrNSxAQQ01R3-8_viVqrekotGSkz4dw3KUg==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyHzwueM7rHDIl4WHvjQuoIahRzOXCJXz7Wf4GXbqQy3AtPcwewyOftRpbEhCYLIPCvTGFiY1NrcAywZAj9mEHZIxTuWl_YmRHdhk5n11ddnkff-5yzW9vog==)
12. [ucl.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6pmohRx_TgoQOf48k4oPbrgU1PcRz-VtkRKASsei--SVY753UwAPzRPUrzgu0kaAWxiQ8TV22cnVd15S_L75M_gmp4okYXDw5VOmr48DtgdIQBBMJl9Rbqlzkj7H6h3QLjVLHcfotCcEc7bSwgu-eaQ==)
13. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaq24Z4_ZwwwvF0Y7b0u7xT3TxkEKUe6MdoHM4uO6tJNPVmOcQqX0VRwMVkhgs-DUdFwe6FsRIUI_7PAx-rFdDkvKDHGr-Dj_RtiGUsAyXyg4WCorsfS3mhPEopXLm4u11Nzud0OG1)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvjuyfBqlMxl2DlOO7lRFFuSZ1FIOA6j64302cSoG1mHqfDmDQUfuXJaauvKPaJWSGEaGf7Fu8rMhewFuO4Bj67yX46NS_rpOXzusJWLsHAHWikfnzJQ==)
15. [ucl.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwA5K5mjDEF34CTre6OVCmoNpulHCDnaqcFRpOSorcbzM7U9SrlvlViZsXjZc8aql_Gb2brvgqCVqx99VMRgsMhN1Xja482RKYzHQy8fqqJMiDEbKmf2NTdSBIHGYtaf4tiPzLLc5MYbi9CRnl-xUQzA==)
16. [wps.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuiKIRRX30PfXFLatQPUlsRKZn3oCif74-qWOos5NCZN3CAl71AhzEGTjNwvOwPRoBK95OKiEUvhgvO9XT8LthbZpExIlb3M2jQwp8_hRETZxMlYUFn80PaPTjFceD1BaIscw6T_FbhmEpF8wOkhwvz5On9I5tx8JP1o9JK8g4Y5ncQumEJnHRq1F_62m0FQWwW6f8WSAago3Ssfb55pHBiOklbiJz0fCoXBI7OA==)
17. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4Cz017du-FaoPJT2Y3p_iwyPNDCMdUiRzoyss3kIodneQWbjHDgvJySTSetCL0f_mxTOvaQ2AeMZ56kif5yiXXitZOn58PeglYoGq0ixi4qOlUNOP0ca6BOWOTXwHRQ==)
18. [cavalab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVg1rgv7UfWp85gBaEFv0kt1GXcDO_exZHd22zQ4jEYp0kfT3EGhl4qvvnK1ncEt4hjss2mGw1KSVet7dja6lhGGBDIQjSh9zb_hky8OnkLq07SbyxQ_RhcEyQLBpEI4_uAW8PcbVt1RoNm2ZLPUuLUfAyWb9xPpfgi3Hau8pslpOWwY-gCpv9nTRCKJD8ptLtiyztxNj8kXFYLoWjNQykBhxyRWJKBOgdHpG8T0ABdIO-tgQbAHJcYSlgE7W-Ow==)
19. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHt78TijMyd-n2zwxLWwiV_gw7sSsyu1FAKgU8Y1L5wxH_n1m4Wdmix51naOIe20W7C420PGj_YHaXSx_ou_YoH-5S5mU9Z4FsuVNxnYyEOycHu7Z-LU5D8D46Pg8=)
20. [royalsocietypublishing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqmAaKgX1BERl1GL1Vb30eGs9Qx8dpe1708vtPFdcZ4xnbqCBeSswkuflVPgZmE1RMV9Tc4oRFoHKsixU9P-e2e9sULLBYBL_HMCsUaedJmF-q9kEGc3jRlG6UJahvz9W7CQrt5uJeoIskKjyIbe0N2nGRkJM6UQyiAgX5Ifmt55I6TPSvU7svwr_TBWWWGym8URnqrtG0R2ODS_SLJ3kTpjOejVGz5gzpCijd)
21. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtVjjnowRO3cqGYQrC-rW0_V1V2oLMRQf4FSmXyN50EhzgqEq2F7BV-ulMi5rqLdSC6Oo8VvO_mM3PGg2j2DpSx5MTXtn8PQSbLwjGEGC_vYnC6vcK9cKNJ1QviYn1bCI1KR9pfAkDUxMm)
22. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2HWKDHA_Si5NGQiRiSNFp5zTBMBaXVAMQkRWJu-dOZTei3b7j8kJrPc_4BhQ9HzhkBeEw3mSrAplf735NxFLo4A1ANr8TjDEaAFecpm7_FK6bpvtTnvb-9DlzCc3SGAuBbO_V3HLd8WU7EWLNO6b8lCzcaEzLpH8yi82KtXIOXWZGYVP3ePgArHJc_i0Yya9dle072NaNA69P7YBB)
23. [cam.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEghSwUdP-O0FZeh3L77k-573txeEjhefrZmN0AlP8k0kKpm2pwrj6dRLO3-aqtGdYDcG-5pUJhV9Dm5ue3y1EM3mbXM9A8m24XpKxhKeZQDfV9_0qUyUjH0-wMgKpk)
24. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdHYrr-hzzcaRfJVdvnXp7c8k9hgy4k8t1WO_k6KezU8lyBDjvJXYq0pciYz90GcKQGr5O7Wp_9Q1ezB-77GQqeDSYsR_pfaBWhW1hbQPPCJyOg4cmQV9bCkG__reAZQvflbgRH3Xs9BHFag==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzedYkaGGTMBZ0pIlPVzDZ8a78HPHrnLaFm7oKJDPEwGHLWLw54SgzhLOR0cIZJ65ClrHj961aNPoDgfLkKsI4M9V3wZJdm93MeCoZwtqddS8SxX4uQR9YbA==)
26. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxy75A0YfpPD7vGoHTdT78QLdbB4JC-RdW37i33h17yJ2DVi2LTKGmgD_zaW-beauTx3HV3AHAJDEJtUoVTgcIfTY5JijoxQGFA_sFGuhrXI_pFabwMSEGIhpyrHokiHPjx--VKol1Dgvq6v_QSOukr2yF)
27. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIKb3sIDfTD3__MyxdC0C9QnxKVa1ySfxMxHhrKImTqnz5nEzt7-rlokpXJ3-tafwSHQEcQTI5PD7WoQBO98Ub7hrdJCFwtWBB0Zfw6D_34g==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHG3hMEWeh_P8nnNdFyqPemb1rA0ViZsK24J9moPrxLxnz_rT0fEfgyebOg11y0uFMWbgpYsoJUHZbJCV8e0SN2JL2WYLnN07YNeFXNCiG8r-wWdVMtZbxhag==)
29. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhw-To46G5l298kRaWbj9LxZTCgsaatRp6iQygi2V6P81vZl9bSfZhxUkfhbv0GWQQHAEj40KSW6N4lNNPqwZyaiXBEWynRYbHEJmAiEtvWn0h2HfINcpPqg==)
30. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHKxsngEwQoNUPq1PtuurfgG-EX8Kgu44Ru8DnEe6h8SajXlf87ye8RpN_gvsZM8BjmgPIGiwpMriNfYgvVCSGriCK5L7NSY-oOFi0mwXF3F1P5HvRXNI_0AB1V_Fc0WUORHsXmGTP-5iDBWhGVg==)
31. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtj1ZvpLnxu7zcCE98ldY91a-LyJGSuO0KoS1BTZjsNQU1o_vUPLTLDe-1HEHifho-Im7-HHUeLkF7R8xZFZSyvmH-99AJgnL9bnQr4KC1am2UvxE_3KsR)
32. [cavalab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwPv8bggWCYf96_pNzp5m0y-3xu6Q2cWl9nfp1TKKHI_-Q5pgGeCIAdT3yX5HFCpABEAEm5fQrRCh48b2ziSI6SvNMB4CCDJFDaBVf8hgvq_eo)
33. [cavalab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOl6FeKIAe-ElIW8WG8fOr6oBjMPow1uHYwI-B1JXf-dxtclIUsSy4G13q_QLXyE_PF9KSMz90yRZG3o6hVQekMikbBN_FYEymkjBrghU4m3EP7XRSx2eSfTVDqOI=)
34. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-cAEvl-5LsTlL08k1Le-5HI4Z36PewgdzWf5Ov202mQzkD2M2NiRKhQsBz5paxVoepbxTGuuCsD9Rt8d2ps9Bqxycz5NdoZzNZIPO6x4vZxsRG6um3A4PRYmGvru6eiCoqJVtmMAOjj7kaFbK6A==)
35. [opentrain.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPBhrl6bOszn0nE_jxciMmi0LWvXl0a-Q67I4ZUsTGP3LLKrikEqzJm0TQqusx4-UgZO04qayqWGy_VsE21sCUv1hDtrwNran33RJu_poyUQKbNt9j4F3yncyBlN0XowBFnj5-abi5vlT0vmNgMBuYplrodCcqgWxr1BhgDbgqy0OzirAsW-8Ic2p_7I_qCWTiPWgdfY86aA2vct0yaxnp72VJWe0bMqO3QWiVTH5PkC0QSANjyogrdIA=)
36. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyLRwJC4iOEp211Y7rLIJI54zsGlqBLN-bGgW5Yqn9kxkr0CwjbnCEZEaNP7QmKEbyk9_aphi__Q180JKyutiVsuoKxIOoFEBHizpziM_xAVFMYb0_-qGhxlzlQM1R)
37. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZezRW_Go390yj7dZzetUbQaf7KlTIBiRfOX0wZndZzc9idtDLVS2V-AYAbfUSbyyZe54OXSRFzUGFlmD7IEouYzPAjK2lIwjQibBaZ-2ryZoYLG407C0ZoKkw2buc3w==)
38. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKvZVtutWiErd4TjUwdGZV9jIlb76hZS-JpM2e3hzP88usyHZnP3kkqWprMmcM1qHUiirDFYNb6xrHQSlRKXAfHIvID221knARIDT7xaGNmYTGOgROnc-dpGAlT1weHR4gIJinH2xzSw==)
39. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGR_53FuD9HYyPZ_9HaU0x7U6qOTlsvA8Yh1ihYqpc82ZHvaHuYQFEuA461wXZS_nKIgTiw3wg_-rco694QRFRoBLEW-QEbjMADw-40zrfIRYU2WBa_sW8xqr116B0=)
40. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXrLdr0S1GQ6GfXrVo8dxsKdSa1hRF9hq31iChSFYJi0xrn9IAbxhAAOPdbJYxrqPSxWYTYdfVlrUj9B67m0EMfesMHGDNZ0_qzAyWV3UstW_O2nkTT-WGxBmoBN9NxNKGhAeX-W0jsw==)

