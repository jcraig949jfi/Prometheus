# Prompt 16: Optimal Experimental Design

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcyNmllYXY2TE5fV08zOUlQZzYtU29RaxIXMjZpZWF2NkxOX1dPMzlJUGc2LVNvUWs
**Elapsed:** 395s

---

FRONTIER PRACTITIONER DOSSIER
Field: Optimal Experimental Design

This report synthesizes the tacit knowledge, foundational literature, living software, and current research frontier of Optimal Experimental Design (OED). It is structured to transition a competent computational scientist from theoretical awareness to active, frontier-level experimentation. 

Before proceeding to the structured report, a critical correction must be made regarding the mechanism described in your query. Your description is accurate for a specific, classical subset of the field: exact discrete D-optimal design for linear models with fixed candidate spaces [cite: 1, 2]. However, it requires three vital corrections for a practitioner operating at the frontier in 2026. 

First, for non-linear or implicit models, the Fisher Information Matrix depends on the unknown parameters themselves; you cannot simply evaluate basis functions independent of the true parameters. Because of this, the modern frontier has largely moved to Bayesian Optimal Experimental Design (BOED), which maximizes Expected Information Gain (EIG) over a prior distribution rather than relying on a static information matrix [cite: 1, 3]. Second, standard exchange algorithms like Fedorov or coordinate exchange are not entirely neutral or random; recent analyses have proven they exhibit severe run-order artifacts that systematically over-represent certain design sequences. Their raw output must be explicitly randomized before execution in a physical lab [cite: 4, 5]. Third, maximizing the determinant of the information matrix fundamentally assumes a well-specified model; if your model is misspecified, maximizing this classical determinant will frequently cluster your measurements in entirely irrelevant regions [cite: 6]. 

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Optimal Experimental Design is the mathematical formalization of how best to acquire data. It shifts the burden of experimental planning from human intuition to computational optimization, seeking the specific experimental conditions (measurement locations, times, or inputs) that will yield the maximum possible information about a model's underlying parameters. In 2026, the field is distinctly split into two eras: the classical design of experiments (using Fisher Information and alphabetic criteria like D-optimality) and the modern Bayesian formulation (optimizing expected utilities like Expected Information Gain using deep learning and generative models).

What is SETTLED: The classical formulation for linear and low-order polynomial models is considered a solved problem. The use of D-optimality (minimizing the volume of the confidence ellipsoid), A-optimality (minimizing the average variance), and E-optimality (minimizing the maximum variance) for linear models relies on mature coordinate-exchange and Fedorov algorithms [cite: 1, 2]. If your model is linear and your design space is a simple discrete grid, classical exchange algorithms are universally accepted as the correct approach.

What is CONTESTED: The estimation and optimization of Expected Information Gain (EIG) for complex, high-dimensional, or implicit models remains fiercely contested. Because EIG involves a double-intractable nested integration (an expectation over the data, which itself requires an expectation over the posterior), researchers are divided on the best approximation strategies. One faction advocates for amortized Variational Inference (vOED), training neural networks to approximate the posterior [cite: 7, 8]. Another faction pushes for Conditional Normalizing Flows, arguing that their exact likelihood evaluations provide superior gradient-based optimization without the bounds-gap inherent in variational methods [cite: 9]. Furthermore, in sequential experimental design, there is an active debate between using fixed, pre-trained policy networks via Deep Reinforcement Learning (RL) versus semi-amortized methods that dynamically fine-tune the policy during the experiment to prevent out-of-distribution failure [cite: 10, 11].

What is OPEN: Two major frontiers remain wide open in 2026. The first is robustness to model misspecification. Standard BOED collapses if the simulated generative model does not perfectly match the physical reality, leading to Generalised BOED (GBOED) frameworks that attempt to optimize designs using robust loss functions rather than strict likelihoods [cite: 6]. The second open frontier is task-driven or goal-oriented experimental design (e.g., ACTION-BED). This paradigm argues that maximizing abstract information (EIG) is frequently misaligned with the experimenter's actual downstream goals, and that designs should instead be optimized directly to minimize future decision loss [cite: 12].

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Meyer, R. K., & Nachtsheim, C. J.
Year: 1995
Title: The Coordinate-Exchange Algorithm for Constructing Exact Optimal Experimental Designs
Venue: Technometrics
Identifier: DOI 10.1080/00401706.1995.10485889
Why a practitioner must know it: This is the load-bearing paper for the exact method you anchored on. It defines the coordinate-exchange algorithm that replaced exhaustive candidate-set searches, allowing classical D-optimal designs to scale to higher dimensions [cite: 13, 14].

Authors: Chaloner, K., & Verdinelli, I.
Year: 1995
Title: Bayesian Experimental Design: A Review
Venue: Statistical Science
Identifier: DOI 10.1214/ss/1177010130
Why a practitioner must know it: The definitive theoretical bridge between classical Fisher-information-based design and modern Bayesian design. It formally defines Expected Information Gain (EIG) and establishes the theoretical limits that all modern neural-network estimators are attempting to approximate.

Authors: Foster, A., Jankowiak, M., Bingham, E., Horsfall, P., Teh, Y. W., Rainforth, T., & Goodman, N.
Year: 2019
Title: Variational Bayesian Optimal Experimental Design
Venue: Advances in Neural Information Processing Systems
Identifier: arXiv:1903.05480
Why a practitioner must know it: This paper triggered the modern deep-learning renaissance in OED. It introduced amortized variational inference to estimate EIG, proving that neural networks could bypass the computationally ruinous nested Monte Carlo approaches that previously stalled the field [cite: 7, 15].

Authors: Strouwen, A., & Goos, P.
Year: 2019
Title: A Note on the Output of a Coordinate-Exchange Algorithm for Optimal Experimental Design
Venue: Chemometrics and Intelligent Laboratory Systems
Identifier: DOI 10.1016/j.chemolab.2019.103819
Why a practitioner must know it: A critical negative result. It proves that the classical coordinate-exchange algorithm you described is not random and heavily biases the run order of the chosen measurements, requiring explicit post-hoc randomization to avoid experimental confounding [cite: 4, 5].

CURRENT SOURCES (THE FRONTIER)

Authors: Huan, X., Jagalur, J., & Marzouk, Y.
Year: 2024
Title: Optimal experimental design: Formulations and computations
Venue: Acta Numerica
Identifier: DOI 10.1017/S096249292400001X
Why a practitioner must know it: This is the single best survey of the field currently in existence. It maps the entire modern landscape, connecting classical discrete optimization to continuous Bayesian sequential policies, and is mandatory reading for a computational entrant [cite: 1, 16].

Authors: Orozco, R., Herrmann, F. J., & Chen, P.
Year: 2024
Title: Probabilistic Bayesian optimal experimental design using conditional normalizing flows
Venue: arXiv
Identifier: arXiv:2402.18337
Why a practitioner must know it: Defines the state-of-the-art for performing OED on extremely high-dimensional models (like medical imaging). It replaces variational approximations with conditional normalizing flows to jointly optimize the design and the posterior directly [cite: 9].

Authors: Wang, J., & Dowling, A. W.
Year: 2022
Title: Pyomo.DOE: An open-source package for model-based design of experiments in Python
Venue: AIChE Journal
Identifier: DOI 10.1002/aic.17754
Why a practitioner must know it: The most important paper for applying OED to large-scale, equation-oriented physics models (Partial Differential-Algebraic Equations). It demonstrates how to leverage stochastic programming abstractions to perform OED without relying on black-box sampling [cite: 17, 18].

Authors: Barlas, Y. Z., & Salako, K.
Year: 2025
Title: Performance Comparisons of Reinforcement Learning Algorithms for Sequential Experimental Design
Venue: AAAI Workshop on Generalization in Planning
Identifier: arXiv:2503.05905
Why a practitioner must know it: Represents the immediate frontier of using Deep Reinforcement Learning for sequential OED. It proves that standard RL agents often fail to generalize to out-of-distribution experiments and demonstrates that ensemble and dropout-based Q-learning algorithms are required for robust policies [cite: 10, 19].

Authors: Harikumar, H., Katt, S., Barlas, Y. Z., & Kaski, S.
Year: 2025
Title: Robust Experimental Design via Generalised Bayesian Inference
Venue: arXiv
Identifier: arXiv:2511.07671
Why a practitioner must know it: Introduces Generalised BOED (GBOED). It addresses the field's greatest vulnerability: catastrophic failure when the in-silico simulator does not perfectly match the physical environment. It replaces the standard likelihood with a robust loss function to prevent the clustering of designs in irrelevant regions [cite: 6].

PART 3. SOFTWARE I CAN ACTUALLY RUN

pyro.contrib.oed
URL: https://docs.pyro.ai/en/stable/contrib.oed.html
Language: Python
Licence: MIT
Activity Year: 2022
Maturity: MAINTAINED
This is the reference implementation for variational BOED by the original authors of the 2019 NeurIPS paper. It can run expected information gain estimation using Nested Monte Carlo, Laplace approximations, and Variational Neural Networks. The known limitation is that the OED module itself sees infrequent updates compared to the core Pyro library, and handling implicit random effects requires complex custom tracing [cite: 20, 21].

Pyomo.DoE
URL: https://pyomo.readthedocs.io/en/stable/contributed_packages/doe/doe.html
Language: Python
Licence: BSD
Activity Year: 2024
Maturity: MAINTAINED
The community standard for equation-oriented, physics-based experimental design. Unlike probabilistic frameworks, it relies on exact algebraic gradients via the Pyomo ecosystem to optimize Fisher Information Matrices for continuous dynamic models (PDEs and DAEs). Its limitation is that your model must be explicitly written in Pyomo's equation-oriented syntax; it cannot optimize black-box simulators [cite: 18, 22].

PyOED
URL: https://gitlab.com/ahmedattia/pyoed
Language: Python
Licence: BSD 3-Clause
Activity Year: 2024
Maturity: MAINTAINED
An extensible suite specifically designed to bridge data assimilation, inverse problems, and optimal sensor placement. It excels at spatial design problems (e.g., where to place weather sensors). Its main gotcha is that it is heavily tailored toward linear and weakly non-linear inverse problems rather than deep learning-based generative models [cite: 23, 24].

RL-BOED
URL: https://github.com/yasirbarlas/RL-BOED
Language: Python
Licence: MIT
Activity Year: 2024
Maturity: MAINTAINED
A modern evaluation harness and implementation for training Deep Reinforcement Learning agents to perform sequential experimental design. It can run the canonical Source Location Finding experiment using state-of-the-art algorithms like Soft Actor-Critic (SAC) and REDQ. The limitation is that it relies on older dependencies for specific RL environments, requiring strict environment management to avoid dependency conflicts [cite: 25].

GeneDisco
URL: https://github.com/genedisco/genedisco
Language: Python
Licence: Apache 2.0
Activity Year: 2022
Maturity: DORMANT
A domain-specific benchmark suite for evaluating active learning and experimental design in drug discovery (specifically CRISPR interventions). While the core software is mostly dormant, it remains an authoritative benchmark. The limitation is its narrow domain focus; it is highly optimized for discrete genetic intervention spaces and does not generalize easily to continuous physics models [cite: 26, 27].

PART 4. DATA AND BENCHMARKS

In modern OED, static datasets are rare. Because the algorithm must evaluate the hypothetical outcome of any proposed design, the field relies almost entirely on generative simulators. However, a few authoritative benchmark suites exist.

Source Location Finding (Generative Benchmark)
URL: Generative environment (implemented in pyro.contrib.oed and RL-BOED).
Size: N/A (Procedural).
Licence: MIT.
This is the standard synthetic benchmark the field treats as authoritative for evaluating EIG estimators and sequential policies. The task is to place sensors in a 2D continuous space to locate a hidden signal source that decays via the inverse-square law. It is used to measure the computational efficiency and sample complexity of an OED algorithm. Known saturation: The basic 2D version is largely solved by modern variational methods; frontier papers now use highly constrained or high-dimensional variants to demonstrate performance gaps [cite: 12, 25, 28].

fastMRI
URL: https://fastmri.org
Size: Over 1,500 clinical MRI exams (hundreds of gigabytes).
Licence: Requires data use agreement (academic use only).
An authoritative empirical benchmark for high-dimensional OED. The task is to select an optimal subsampling mask (the experimental design) for k-space frequencies to reconstruct an MRI image. It is used to measure how well an OED algorithm can optimize binary designs in dimensions exceeding 320 by 320. A known limitation is that the ground-truth reference is typically a fully-sampled multi-channel reconstruction, meaning the benchmark optimizes for a specific reconstruction algorithm's definition of quality rather than ultimate diagnostic utility [cite: 29, 30].

GeneDisco Benchmark Suite
URL: https://github.com/genedisco/genedisco
Size: Contains multiple curated public datasets (Achilles, STRING, CCLE).
Licence: Apache 2.0.
Used to measure batch active learning policies for identifying causal gene-to-phenotype relationships. It is the authoritative benchmark for discrete, combinatorial OED in biology. Known limitation: The biological response models are inherently noisy and rely on surrogate predictive models, meaning algorithms that aggressively exploit the surrogate often overfit and perform poorly in actual wet-lab validations [cite: 26, 31].

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to understand the modern frontier is the Source Location Finding task using Variational BOED, originally published by Foster et al. (2019). Reproducing this will teach you the mechanics of amortized inference, EIG lower bounds, and continuous design optimization.

Software and Version:
Python 3.6.8 to 3.9 (legacy compatibility required for specific sub-dependencies).
PyTorch 1.1.0 (or carefully updated to modern PyTorch with minor syntax adjustments).
Pyro 1.7.0 (via the pyro.contrib.oed module).
Target repository: https://github.com/ae-foster/pyro/tree/vboed-reproduce

Dataset:
Procedurally generated 2D Source Location Finding simulator (included in the repository).

Parameters to set:
Design space: Continuous 2D grid boundaries.
Prior: Normal distribution for the source location with mean zero and standard deviation 1.0.
Likelihood noise: Normal distribution with standard deviation scaled by distance.
EIG Estimator: Nested Monte Carlo (NMC) as the baseline, followed by the Variational (vOED) estimator.
Outer loop samples (N): 2500.
Inner loop samples (M): 50.
Optimizer: Adam.
Learning rate: 0.001.

Seeding and Replicates:
Execute 10 independent replicates with fixed random seeds from 1 to 10 for both PyTorch and NumPy.

Compute Cost:
Extremely light. Approximately 1 to 2 CPU hours total, or minutes on a standard GPU.

Expected Result:
The algorithm should output a symmetric circular or semi-circular array of optimal sensor locations around the prior mean. The computed Expected Information Gain using the variational bound should closely match the Nested Monte Carlo baseline but require an order of magnitude less compute time. Compare your EIG values against Figure 2 in the original paper (arXiv:1903.05480), which demonstrates the variational estimator maintaining low variance compared to NMC as the design dimensions increase [cite: 7, 15].

Three most common ways people get this experiment wrong:
1. Conflating the inner (M) and outer (N) Monte Carlo sample sizes. If M is set too low relative to N, the Expected Information Gain is systematically over-estimated due to a positive bias in the nested estimator [cite: 15, 32].
2. Failing to reset or properly initialize the neural network's variational parameters for each fundamentally new candidate design, causing the optimizer to get stuck in local optima from previous design evaluations.
3. Using the variational objective (which relies on the Evidence Lower Bound) as a strict upper bound. It is a lower bound on EIG, and improper tuning of the learning rate will result in falsely low design scores, leading to sub-optimal sensor placement.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you intend to run real experiments on novel physical systems, the most significant missing component is a universal, differentiable bridge between black-box scientific simulators (typically written in C++, Fortran, or proprietary software) and modern auto-differentiation OED frameworks (PyTorch, JAX).

Interface required:
What goes in: A continuous or discrete design vector proposed by the OED framework.
What comes out: The simulated physical observation, and crucially, the exact gradient of that observation with respect to the design vector.
The hard part: Modern variational BOED and Normalizing Flows require taking derivatives through the simulation to update the design policies efficiently. If your simulator is a black-box finite element solver, it is non-differentiable.
Work required: High. Several research groups have privately rebuilt their entire physical simulators natively in PyTorch or JAX solely to enable OED [cite: 9]. Building a robust surrogate model or integrating an adjoint solver to pass gradients from a black-box simulator back to the OED policy network is a major, customized software engineering effort.

A secondary missing component is a plug-and-play Task-Loss Integrator. Current frameworks output the design that maximizes Expected Information Gain. If your goal is downstream decision making (e.g., placing sensors not just to learn a parameter, but to specifically prevent a catastrophic system failure), no off-the-shelf tool allows you to swap EIG for Expected Future Loss (EFL). You will have to write the custom objective function and the corresponding bi-level optimization loop yourself [cite: 12].

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

Nested Monte Carlo Dimensional Collapse
Early attempts to perform BOED on complex models relied on Nested Monte Carlo (NMC) to evaluate Expected Information Gain. This approach failed catastrophically as dimensions increased. Because NMC evaluates a posterior expectation inside a marginal expectation, the computational cost scales to the power of three, causing "belief explosion" where the agent cannot explore enough of the belief space. Scaling this method purely with brute-force compute was abandoned in favor of amortized variational inference and neural density estimators [cite: 15, 33].

Coordinate-Exchange Run-Order Artifacts
For decades, classical OED relied on coordinate-exchange algorithms to build optimal discrete designs, assuming the output was independent of the algorithm's internal mechanics. Strouwen and Goos (2019) demonstrated that this was false. The row-by-row sequential optimization structurally biases the algorithm to select extreme factor levels for the earliest measurements. Designs that looked optimal on paper were harboring severe temporal and run-order artifacts. The standing correction is that the output of any coordinate-exchange algorithm must be explicitly randomized before execution [cite: 4, 5].

The Misspecification Collapse
The most damaging ongoing critique of modern BOED is its fragility to model misspecification. BOED algorithms are aggressively greedy; they will place sensors exactly where the assumed mathematical model dictates the variance is highest. If the real-world physics deviate even slightly from the in-silico simulator, the algorithm will confidently place sensors in useless locations. This critique is currently being addressed by the emerging field of Generalised BOED (GBOED), which abandons strict likelihoods for robust, heavily regularized loss functions, though it remains a work in progress [cite: 6, 34].

The ACTION-BED Critique (EIG Misalignment)
A standing methodological critique of the entire field is that maximizing Expected Information Gain is a proxy goal. A 2026 critique points out that reducing parameter uncertainty does not inherently improve downstream decisions if the reduced uncertainty occurs along parameters irrelevant to the actual physical intervention. EIG encourages uniform uncertainty reduction, which is sample-inefficient. This critique remains partially unanswered in standard software, requiring practitioners to build custom decision-focused frameworks [cite: 12, 35, 36].

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given your compute resources and coding ability, a well-resourced newcomer should bypass classical linear OED entirely and aim directly at the intersection of generative deep learning and task-driven experimental design.

Rank 1: Task-Aligned Sequential Experimental Design (ACTION-BED)
What it is: Build a framework that optimizes experimental design not for information gain (EIG), but for a specific downstream operational loss (e.g., minimizing the control error in a robotics task or the classification error in medical screening).
Feasibility now: Compute scaling and differentiable simulators make it possible to perform end-to-end gradient-based optimization through both the design phase and the subsequent decision phase.
What it measures: The difference in Expected Future Loss (EFL) between an EIG-optimized design and a task-optimized design.
Falsification: The idea is falsified if the task-aligned design performs no better on the downstream operational metric than a design chosen by standard EIG maximization [cite: 12, 35].

Rank 2: Robust OED via Generalised Bayesian Inference (GBOED)
What it is: Run an experiment where the physical reality is intentionally perturbed away from the in-silico simulator, and use generalized loss functions (instead of strict likelihoods) to prevent the policy from placing measurements in irrelevant regions.
Feasibility now: The recent formulation of Gibbs Expected Information Gain provides the mathematical framework to apply these robust losses to OED without breaking the Bayesian update mechanism.
What it measures: The out-of-distribution performance and regret of the experimental design when evaluated on the misspecified physical system.
Falsification: The idea is falsified if classical BOED recovers from the misspecification just as well as GBOED when given a weakly informative prior [cite: 6, 34].

Rank 3: Score-Based Diffusion for OED Sampling
What it is: Leverage diffusion models to sample from the "pooled posterior" during the design optimization loop, framing the selection of the experimental design as a bi-level sampling-as-optimization problem.
Feasibility now: The maturity of conditional diffusion models in 2026 allows for stable, score-based sampling in spaces where traditional MCMC fails.
What it measures: The sample efficiency and computational time required to converge on an optimal design in a high-dimensional image-based task (like the fastMRI benchmark).
Falsification: The idea is falsified if the diffusion sampler collapses into local optima more frequently than standard variational inference [cite: 28, 37].

What will NOT work:
Attempting to scale Nested Monte Carlo EIG estimation by simply applying more GPU compute or throwing standard Deep Reinforcement Learning algorithms (like vanilla PPO) at the problem. The state space of sequential beliefs in OED grows exponentially ("belief explosion"). Standard RL agents fail to generalize across this space because they memorize specific trajectories rather than learning robust information-seeking policies. You must use algorithms specifically augmented with dropout or ensemble Q-functions to prevent policy collapse [cite: 10, 33].

**Sources:**
1. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_ksjN6fWqtxWZJxUJTeCGIoG5ooZIkbkP5ygxiQXJkh3_dLtvWjByQnuQ40L4BpbdFmeTAq4AckZF0j5hn0gNaZUTtqKkG2_0Qsl8ckHXx_qJmNIy0mMG6be4mlUPbr91aqBtqEIX-FWE4QSKaMUFgm-nUUryKwjphnvLwoyYOUe3lrdXBjbAEMTe06g_Uigtrxw5-idKgKGKRi3rWoQlEA5T4ilg8ux5ec4ktc3lKjZ3-MrY1KlrXo6ksxMLkAem8PRjvGLxPPU2w9FpknQ=)
2. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCCrBGS6havvMo4Fkg3XMt-hytET1WMN6Z7namhCq28YShKGprRimtSHB-ZkPqKL8XrtxWAUGxdiiLvvLvTOEsC5Sxwc-s9zckw4mNEAuEOpEYZefrIKWNlSk7U58TDcakSr7i9bhe9K70m1yryK2nL3odHJuX_x7x0DUF8w==)
3. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEi_eIYmzUgq8zX1bwRC_slhuLEEKmCpvbe_VFA_WvgjWD7GMhu63idjJbGZExpgBhJYlM6S3pcv2MzR_Ne25q9P_zMn10PZOWhOguvhCHyG3en0C0Z_BoO89cTUXidcTA5mTk4aONu1Koj47AQs0BfglAafvlCTMECvZGm1TzyFg==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmpHDeawEQ6SqOLxsLj7-9RlqSE51H_j4uFB4YnykgIDiszyMgn2czNkEk61PyNGc4YbtDCiCn8siUJ3KWpxbpftvqWRlVUUyouuWV1ABUa3sx1ueuOoM=)
5. [kuleuven.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVzTafs-cjnQ53-MaBnHZDfdNUQpYGequmAmVRVHo-PAn06t9BieVA7lEgKcWNdBc5tLFGTmggCNmj7FbYPe44JDd8yB5CyP4WHtnAEsUrr0Z2IqrNHhb4Wb3YvaLQLBA=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6Nrlcv79yZsLQbxfTxfJRzb518JIH8PKpafrC6aDbBtPmHwUm7aV32aCWQePix2R-DQnq_BMHXY7KobeOK3yaf4k1eURn1FLTb4cqYAQH5L9qXDgXDAIhmg==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIvznIPQD5Z8-CmzFpLqPvHEq5ASYLLx4ie7MdBrcd1F2G-BwOoKuK8oEofTaVO1S3wiqdsuQkIupR803pFG3B7csl5dP5sXhNK6dCegtRrT7meuEIkA==)
8. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErX1RarjaPAsjH5tW98bvUKwuNzFWxj-yQ6fRNmh0kJlg_dF72Cevf0RLgqg_s1T1FNQRb8XHxaq41plb2klHQkjsDzgQGqFOGpWZFS9xb5AxVy4KB_ZNU2BEPLKPppgE=)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmiq3D2fzDK9OLS8tEdbSPbz9xNrIQUXO5DlDNkRkVB6_gwJpBykzxg00L7iRTSLusG4ivhK6xZAXU8YnKemrTZSR5PGwa73OvLfTyBokzvbB_A-u2gxEpFQ==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH63M5-To6OkbvzqS5-Mggmpja5UJAzJMmtT-n3JIeNFSOCGYvbkojmD-vfEaQheGcbMf157q4sZ7pqVhvTmVCY6hQnh4eKfBji8XWUZ1XxyiuyG-ZB44B7PQ==)
11. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFE8ihOxYC3JhSoOJlirWc8lP2OKbocrc-Zyu6CXaiGyD_T4Khf5iIDSMDpdWQMWE6Gzu1cGKq2wq-0z209E6WnOrTtHEMmwQjvr_bmXMRb_u2kH0UC9Y1abiai7h2-Hw==)
12. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERH9mGeTCUElubzAdYyO6HJMCyJfrzC-Dcrlihka6vpa_PuLhBXc1nyWE-HkXXmiZSTGsY0hQdoMRSHzrzNUVcgkcFsJb0TXqKGzUUyDXgetynpgmHQhvDAAsVCNg=)
13. [umn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtoeKPIpE-bRAwChnCz4OLMdxCS_Xd_A7NiZa911O3iRtmm3PF4CShhDayO_voKbeY21OqLylxtJru8cmhAyPOsOrHOB20zj86TqsykBRkQY9q_OCjL7J5ys0Yf42ucTdte4UVSHiMANYlmdjPsJgSoNmNNNUl-Pqyd5ulyCBbcA86-WH5Mv_GvYu8CJh6jSHlzuRisakPij_zA8zoy1w4)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFejiWuvObRsz9QUDNQKjrb4DbkO_W6KSGogPy2HRPvowxPpICjC1omEIUvB9YHdZbjJS9sHJYnSLFfnHQHxRh_jXgFMTXvO6kyU0cf6MF0N1ISnDxq08LVUHmshz-qGkm36AXgKEtWUH34QavvJqVKfIaWc5GmHG9RIQ6OOZ-X7Hd_PVP163zc-YXZChUN93MRqPu8CTc1pscCPPnFcFtrNTaL0tHyT5kH4GN6pXPGvBtxFrh-ZNSujKzg0hq_CA==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGo13aSAThjY6mEiaHhJNSBFAJk7PQbFW1sPUhYmMRF3pw9GxEgPAH3AiNY9mNr2RQaw2Kdwk5EFYdFetf0Cy3fOsA0QfenYwJlFU96b1X0AMF5jdxO476A1Q==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkPHpvVVm_1z5NDplK4j1sXPqUZzKutrqVu8781WfQIfXhrIRT0XrPxp4cmaPq-vPNSnp7CyLPt7irtQ0e3kZ4L1CYp_Izd0MSE1mEuUVDsoPQE7WMj2Ftmg==)
17. [osti.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0IVpsJt431ACq_KB7tW8K6YXN_5c32BZaCx9c_H28fVnopjBdwQo2jpglnW5DsSJ9vgGsfzm9V9Vxx5qn4A_35ikSkTP4_2Nhekz8yc1s3COdnPQv3Hzcmb9eKenxow==)
18. [readthedocs.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFoCnrQiAsVR8ZcPJNJoNIhD43rGT7QCiicPhrGAszVa0qp-qTKD4-P_NGDCyZhvqUO3o2m9GMmw0kB-ckr2h9s9OsAIBp0xEyeazIBcxSR6B3v54fL6vTrjXl2f8UWmj5GY0tqybOsy76B-XtGHochkjiDU_AGksT3mulf9A==)
19. [catalyzex.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjdqJCGPQ_DmjlfwLYNv-xnjNsW049tADDMD9nXtTTXYinDUcpcRc2PA-b9RttAmCa4q7lzJVgiLwwY5Uo0teBNsj8TlYVWl8TcNY9VzRHkNTz-9_Y5tnay1YrvyVZlJ8H6QVzILI=)
20. [pyro.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUiWOswOHjYR99gMC7-QAw6wfDd0z1HEcuzhaDk7ydTOZCdDr0vMltTbuLIMpeH1I5_SJH2qXWszC8lSCEokTJVBE0ffsGemHZBivCfkYZiA6jffw0y4i0f-Rce84JGDZu2u_N)
21. [pyro.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEp-kDxz7pbzGlE03jGwfCgZdEvnSZGFvKqXgVkCOZzfHi93iGAB9JkXKwi4bs6BSs6nPQKgahfO3C1xZO2iHXyxWp15Xe1FBTmrcNmwhTcgT7gejMTWrcoenanPR6RqpmF2hB-X77KY_r1Ldxr9Xz88dp4oj4pm8JM8_loxjBjhdTk47LXZxpewQJW1_ZbTIaKznipZRmjH3uwSykk92yV5O7vUY3t4QOOVQ1gGWt0QTzPycCmQCaO)
22. [readthedocs.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJnkF2GVMgIVQGu_vjUB3eedM8PNWlt9NZ5hVuQ_5lJvrTQJ8MI1mtv6gohmlhEX-JxTJykifea3bkxutZVxVc9RDiKzfaZ7sqaCuniDDrRWCyv3m2qI4LKs2tfUs586HAV8ONJ1GwlX6SXV4p6ZqRrST-097k6JDtTmNQbB8=)
23. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6Ckqjo_QtXTpu76UOFYJ_SWN-JVclj-cMlHVgwQ597hqKAX0Fgcgo_3jJZMKOy_61fS3jyc5pdjSinpvrOVEJmEEPRG79ET-4TKqvtpMOa1Z6Zc8glr2aMiCgCfsYmi122WbQLyT8)
24. [anl.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_3Ed-WXblYkiDVjb7d6yIdcGXlnEtl7-5FTRsjBx0t6cPXX3K3UO9mru0xolX-9SPYQ03Lhh8bEFQ2qe3pAd5ivzk_e2FErwqBPUjnpf4uqZjGt4rlNMcp7hGTQCFfTKvKpUd2wYh)
25. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcr4XIw5rGk8p3MVMcPLsYDgEMV2VT8NHOyELDaymO2NwhQYt8CDVnFtB6kb5Yc_WJf65uZvh-2J56wOgAJeSkIynxV53eswBko21xdqhdHGCbWh7Rm09mBgFzfQ==)
26. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBYVPGaKmqJCvDkbMjSx99-yFlFKAgnb2kSq1_IJb-s7xmuds91f5zWlVEeF5oxMkzdDB9pWl296-2Sl9dhZ2VzflEruMx-bsKJ4NH1_M7Zc_EGTruG4RqO1EeLA==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4IytaVnxJWZhp3m055F56RgAPNTKBfHmhxmWVp-S0e0GIoHRR-JhiptxMZdbq5SVGsT2qIKWurMQmJk_w6GfOcFtxFgdbMtfjk10xncyGM86Kd6Gi1O8P-A==)
28. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHny3uwhqYkNTgVR3pbe3rbq56qITsOy2Oz8O0smwcn8K1B_pqgIGZBMsQjqMZU6543XPOC7Hi0l8hd_Blc2OT7ECEFiUvlNZSA117NkXHJMs4NowQZKVOktQh_yJEVxMS66_vWXrnQI-WuK3aw1OVA-gcoOAFY0UNtIQXYlyF_xhiIOFw7ikJXfQ8pRBPnb7lWfGPPrxO5EekjW99h_IIGWqoy)
29. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHb2etl4Zq5CHg0muauXa-VKFDazRtpmsJFHrJwOJLr6MedaukDBeaUgYI7iYCHh6m4njRTss28ac3zXqDqnkTQhc47lPp-jCHnuMnjd9BU1WrXvCrvJcjxIaQCSK619g1KWuiz2w8P)
30. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGM5cPUTlwVM98pxrwEQmgFEb5GjrInntgEGFqAjF3LEAtNG65nDhR0s5SyPsjMceMXNTR8LpWI_EYJ8n_0ykTPIerdnmmLBJ8--uB7WT7tqiNlvp6rWgUwMWC1MWtB2tpbh4nBpUyYlXgTF4suNfz7nQdC_yhJ2JCsrx_vSqg4djf_r7tyZEGsJeCTFbf3ve3k0KRy1mzt8UYMA3Bk1ouZT1hGg_bjNZ7HmT_116kuoLkc4UNj8Jogz8s1bNJjAmknGBqH)
31. [schwabpatrick.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5cHZt92xm3aDdoOOHeuipYAqg9RiHQqHAElyO9c8BBRu6REnfP2U3r6UcM720dBFyWtJfZKqRCoyv4h1XGG2SvtZusA3TZuebksAqx4ErqQkIKQdqlIBhY5JZLPPHKgGQTUMaa0pyGTJ0GkjXp-OeK6vEmDaDCUGvj1bg)
32. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFh4BQxj_CODEbfzDG3ZCvCo64sD44ad9AOjiGpyabwp7C5ToOJlE73b0QSp3j7eKjahgGPleUoVyz9Ui9W3A0Vx208yIuxje59g8IYnH5woS4o_vlEI298xAQq97wz-qDmhht4Nk4KLSDcLJnL)
33. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcvH4XMoF9KCpx1Xl5b1sJSHG1s-etMV1VCj39XvAfpVecFVeLvvlwJ65skq-JQyv47bvGxJy6RdrUfXi-XnmE8DTL5V55Zugh6eJTAxoOfHDA-e8e-H6oC5eywQyzAa9GnXcy2NYJTLfrbVXh6kx0xSxRgp_NBVJ5GOzgKNRgvxsSpR3unD_qAN9JxCTt7i-wMGmBqSCnadoDUmLjcS9JprRbrp3s)
34. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqDtSC_uEx2kZ6W3GydKV7iaOURCr5yo0_j-pxmk3XF6VcEHd4aSWTyAbmXogbZziVu4LxKMSWFWx3FE-nfDuWSszDL973BhcbsQCn1bG_cJpCQ0bFntRU_ms=)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECtztfd34PTdqOcQ6gexgpzF89ht663OfnO1jrgV_bAF5wLeKSlCpfN2jn1pZqO9tnM9hWJpRHoa7EY7mgoA7muQAV65tFiAjgOL_AO6SpBfKSWaEZDupQoA==)
36. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExT37Y4Shonllch89mgqqvFEeZ9pXk5bG5ySSvarCbzKwUPzuiAr1icXUppFXtU95xnH7lrNcvqKbI5_jDn68FC1f4j7lvgh_d8TnVIds1rNPme7o2CX5YrzgZeLMnwglh3ABh8eZ5XA==)
37. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSwyJo0pXT93pfU8iKOLsjRU9ef-DTe8I11_e8lC0iWRgtsgyTnYb5DTGFj2AEII_yMgoAFi-uPMG6KyM6Lef0pHXDwU6Lm--54gUmYsky84Vw2VRqMRg7uGitluHbaoQ=)

