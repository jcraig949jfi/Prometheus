# Prompt 11: Equation Discovery

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdsNldlYXJua0lJVy1fdU1QenVmVDhRdxIXbDZXZWFybmtJSVctX3VNUHp1ZlQ4UXc
**Elapsed:** 304s

---

# FRONTIER PRACTITIONER DOSSIER: EQUATION DISCOVERY

Equation discovery, frequently synonymous with symbolic regression in modern contexts, is the scientific discipline of algorithmically extracting governing mathematical equations from measured empirical data. Your understanding of the core mechanism, Sequentially Thresholded Least Squares applied to a candidate library, is entirely correct and forms the bedrock of the Sparse Identification of Nonlinear Dynamics methodology [cite: 1, 2]. However, the field has evolved significantly past estimating derivatives numerically, as this fails catastrophically on noisy real-world data [cite: 3, 4]. 

Today, the frontier is defined by two major paradigm shifts. First, the adoption of weak formulations, which replace noisy numerical differentiation with integration against test functions, has practically solved the noise problem for classical systems [cite: 3, 5]. Second, the field is experiencing a profound collision with Large Language Models, sparking intense debate over whether these models are genuinely discovering equations or merely reciting textbook physics memorised during their training [cite: 6, 7]. If you intend to run real experiments today, you must navigate these exact tensions: avoiding the pitfalls of numerical differentiation, and evaluating your methods against benchmarks that strictly control for data contamination.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Equation discovery in 2026 sits at the intersection of data-driven dynamical systems and interpretable machine learning. The goal is no longer just to find an equation that fits a curve, but to find the exact parsimonious physical law that governs a system, enabling extrapolation and physical interpretation. The field has largely moved away from pure genetic programming heuristics in favour of either sparse regression over large feature libraries, or hybrid approaches that combine regularised evolution with gradient-based neural network optimisation. 

What is SETTLED is the fundamental architecture of the sparse regression approach for clean data. The method you described, Sparse Identification of Nonlinear Dynamics, alongside its core optimiser Sequentially Thresholded Least Squares, is accepted as the standard for identifying ordinary and partial differential equations when the data is high-fidelity [cite: 1, 2]. It is also settled that numerical differentiation of noisy data is a dead end. The community has universally adopted the "weak form" for noisy scenarios, where the governing equation is integrated against compactly supported test functions. This shifts the derivative via integration by parts onto the analytical test function, acting as a low-pass filter and allowing machine-precision recovery even when the signal-to-noise ratio is near one [cite: 3, 5].

What is CONTESTED is how to legitimately evaluate and benchmark the next generation of algorithms, specifically those incorporating Large Language Models. There is a fierce, live disagreement regarding whether LLMs can perform genuine scientific reasoning. One side, representing traditional symbolic regression researchers, argues that LLMs are merely pattern-matching and reciting famous equations from their training corpora. They point to the catastrophic collapse in LLM performance when standard physics problems are mathematically transformed into equivalent but unfamiliar representations [cite: 8, 9]. The opposing side argues that LLMs can be used as effective "priors" to guide evolutionary algorithms or propose equation skeletons, forming a neuro-symbolic agentic loop [cite: 10, 11]. Consequently, the benchmark ecosystem is heavily contested, with standard suites being heavily critiqued for encouraging overfitting and ignoring computational energy costs [cite: 12, 13].

What is OPEN is the seamless integration of equation discovery with latent state representation for highly complex, partially observed spatiotemporal systems. Identifying dynamics when you only have sparse sensor measurements, and the true governing variables are unknown, remains a frontier challenge. While methods like shallow recurrent decoders have been proposed to map sparse sensors to a latent space where sparse regression can operate, guaranteeing that this latent space maps to a physically meaningful coordinate system is unsolved [cite: 14]. Furthermore, traditional Koza-style Genetic Programming has been largely absorbed into modern tools that use distributed, regularised evolution, meaning pure genetic programming as a standalone field is essentially dormant in the context of physical equation discovery.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Brunton, S. L., Proctor, J. L., Kutz, J. N.
Year: 2016
Title: Discovering governing equations from data by sparse identification of nonlinear dynamical systems
Venue: Proceedings of the National Academy of Sciences
Identifier: DOI 10.1073/pnas.1517384113
This is the paper that formalised the exact method you described, demonstrating that dynamical systems can be recovered by casting the problem as sparse regression over a library of candidate functions [cite: 1, 2]. A practitioner must read this to understand the base mechanics, the library construction, and the Sequentially Thresholded Least Squares algorithm that remains the backbone of the field.

Authors: Messenger, D. A., Bortz, D. M.
Year: 2021
Title: Weak SINDy: Galerkin-Based Data-Driven Model Selection
Venue: Multiscale Modeling and Simulation
Identifier: DOI 10.1137/20m1343166
This paper introduced the weak formulation of the sparse regression method, replacing pointwise derivative approximations with linear transformations and variance reduction techniques via integration [cite: 3, 15]. It is load-bearing because it defines the exact mathematical technique required to make equation discovery survive real-world measurement noise.

Authors: de Silva, B. M., Champion, K., Quade, M., Loiseau, J. C., Kutz, J. N., Brunton, S. L.
Year: 2020
Title: PySINDy: A Python package for the sparse identification of nonlinear dynamical systems from data
Venue: Journal of Open Source Software
Identifier: DOI 10.21105/joss.02104
This introduces the canonical software architecture for the field [cite: 16]. Understanding this paper is crucial for grasping how the community standardises libraries, optimisers, and differentiation methods into a scikit-learn compatible pipeline [cite: 17].

Authors: Cranmer, M.
Year: 2023
Title: Interpretable Machine Learning for Science with PySR and SymbolicRegression.jl
Venue: arXiv
Identifier: arXiv:2305.01582
This source defines the modern evolutionary alternative to sparse regression, introducing a highly optimised evolve-simplify-optimize loop tailored for discovering unknown scalar constants [cite: 18, 19]. It is required reading for understanding how genetic algorithms have been modernised, vectorised, and distributed for physics applications.

CURRENT FRONTIER SOURCES

Authors: Shojaee, P., Nguyen, N. H., Meidani, K., Farimani, A. B., Doan, K. D., Reddy, C. K.
Year: 2025
Title: LLM-SRBench: A New Benchmark for Scientific Equation Discovery with Large Language Models
Venue: arXiv
Identifier: arXiv:2504.10415
This paper exposes the memorisation crisis in current LLM-based equation discovery by synthetically transforming common physical models into unfamiliar mathematical representations [cite: 9, 20]. It is essential for a practitioner because it provides the exact methodology for testing if an algorithm is discovering an equation or just retrieving it.

Authors: Aldeia, G. S. I., Zhang, H., Bomarito, G., Cranmer, M., Fonseca, A., Burlacu, B., La Cava, W., de Franca, F. O.
Year: 2025
Title: Call for Action: towards the next generation of symbolic regression benchmark
Venue: Proceedings of the Genetic and Evolutionary Computation Conference Companion
Identifier: DOI 10.1145/3712255.3734309
This is the most critical recent critique of how the field measures success, updating the community standard benchmark while highlighting the failure of current methods to balance accuracy with model complexity and energy consumption [cite: 12, 21]. It tells you exactly what metrics the community will demand from your experiments going forward.

Authors: Kaptanoglu, A. A., de Silva, B. M., Fasel, U., Kaheman, K., Goldschmidt, A. J., Callaham, J., Delahunt, C. B., Nicolaou, Z. G., Champion, K., Loiseau, J. C., Kutz, J. N., Brunton, S. L.
Year: 2022
Title: PySINDy: A comprehensive Python package for robust sparse system identification
Venue: Journal of Open Source Software
Identifier: DOI 10.21105/joss.03994
This update maps out the frontier of the canonical software, covering implicit partial differential equations, trapping algorithms for global stability, and ensembling [cite: 22, 23]. It is the practical manual for what is computationally possible off-the-shelf today.

PART 3. SOFTWARE I CAN ACTUALLY RUN

PySINDy
URL: https://github.com/dynamicslab/pysindy
Language: Python
Licence: MIT
Year of most recent activity: 2025
Maturity: MAINTAINED
This is the community standard that most people actually use [cite: 24, 25]. It can run the exact experiment you described, supporting arbitrary polynomial and trigonometric libraries, and includes multiple optimisers like Sequentially Thresholded Least Squares and Mixed-Integer Optimisation [cite: 24, 25]. Known gotchas: The 2.0.0 and 2.1.0 releases introduced severe backwards incompatibilities, completely removing the legacy model pipeline object and changing how discrete systems are instantiated [cite: 25]. If you read a tutorial from 2021, the code will crash on the current release.

PySR
URL: https://github.com/MilesCranmer/PySR
Language: Python and Julia
Licence: Apache 2.0
Year of most recent activity: 2026
Maturity: MAINTAINED
This is the primary alternative to sparse regression, using regularised evolution [cite: 26, 27]. It is incredibly fast because the frontend is Python but the backend is a highly optimised Julia library that fuses user-defined operators into SIMD kernels at runtime [cite: 18, 19]. It can discover highly nonlinear equations that do not fit neatly into a pre-defined polynomial library. Known gotchas: Because it bridges Python and Julia, PyTorch C bindings frequently interfere with the Julia call interface, causing silent segmentation faults if you try to train a neural network and run PySR in the same uninterrupted memory space [cite: 28].

WSINDy_PDE
URL: https://github.com/MathBioCU/WSINDy_PDE
Language: MATLAB
Licence: UNCONFIRMED
Year of most recent activity: 2020
Maturity: DORMANT
This is the reference implementation from the originating authors of the weak form SINDy algorithm for partial differential equations [cite: 29, 30]. It is capable of achieving machine-precision recovery on highly noisy spatiotemporal grids [cite: 31, 32]. Known gotchas: It is entirely bound to proprietary MATLAB toolchains and has not been updated in years, making it practically unbuildable in modern open-source scientific pipelines [cite: 29, 33]. Most practitioners instead use the WeakPDE library implementation that was ported into PySINDy [cite: 34].

sindyr
URL: https://github.com/racdale/sindyr
Language: R
Licence: GPL-2.0 or GPL-3.0
Year of most recent activity: 2026
Maturity: MAINTAINED
This is an R implementation of the sparse identification algorithm, heavily tailored for cognitive science and biological applications [cite: 35, 36]. It is useful if you need to run sliding-window analyses on time series data to detect phase transitions or concept drift [cite: 35, 37]. Known gotchas: It lacks the high-performance PDE solvers, weak formulations, and advanced optimisers found in the Python ecosystem.

SRBench
URL: https://github.com/cavalab/srbench
Language: Python and C++
Licence: MIT
Year of most recent activity: 2025
Maturity: MAINTAINED
This is not an equation discovery tool itself, but the authoritative evaluation harness for the entire field [cite: 38, 39]. It provides a unified Docker-based execution environment to run your algorithm against 25 existing symbolic regression methods [cite: 38, 40]. Known gotchas: Setting it up requires configuring a complex Docker Compose pipeline, and running the full benchmark suite takes days of compute time [cite: 39].

PART 4. DATA AND BENCHMARKS

SRBench Datasets (PMLB)
URL: https://github.com/EpistasisLab/pmlb
Size: 252 datasets
Licence: MIT
This is the authoritative benchmark suite for traditional symbolic regression [cite: 39, 40]. It contains a mixture of black-box real-world data and ground-truth synthetic data from physics simulators. It is used to measure a method's Pareto frontier of symbolic accuracy against model complexity [cite: 21, 41]. Known contamination: Because these datasets have been used for years, many older algorithms have implicitly overfit their hyperparameter defaults to these specific data distributions. 

Feynman Physics Equations
URL: Access via SRBench or AI Feynman repositories
Size: 100 equations
Licence: MIT
This dataset is derived from the Feynman Lectures on Physics [cite: 8, 20]. It is popular but severely contaminated. It is now widely recognised that evaluating Large Language Models on this dataset measures recitation rather than discovery, as the models simply recognise the variable names and output the memorised formula [cite: 6, 7]. A model achieving high accuracy here without rigorous ablation is likely overfitting to the benchmark.

LLM-SRBench
URL: https://huggingface.co/datasets/nnheui/llm-srbench
Size: 239 problems
Licence: MIT (Requires contact information agreement for access)
This is the new authoritative benchmark specifically designed to defeat LLM memorisation [cite: 8, 42, 43]. It is split into two parts: LSR-Transform, which takes standard physics equations and symbolically alters the input-output mappings into strange mathematical forms; and LSR-Synth, which generates entirely novel discovery-driven problems [cite: 7, 8]. It is used to measure genuine data-driven reasoning. Known saturation: The benchmark is deliberately extremely hard; current state-of-the-art frontier models peak at roughly 31 percent symbolic accuracy [cite: 8, 11].

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to anchor yourself in this field is recovering the chaotic Kuramoto-Sivashinsky partial differential equation from highly noisy data using the weak formulation. This proves that you can handle spatiotemporal data, bypass numerical differentiation failures, and achieve sparse model recovery.

Software and Version: PySINDy version 2.1.0 [cite: 25].
Dataset Generator: Generate a numerical simulation of the 1D Kuramoto-Sivashinsky equation using a standard spectral solver (e.g., SciPy's solve_ivp with Fourier derivatives). Generate a spatial grid of 256 points and a time grid of 200 points. Add 10 percent Gaussian noise to the resulting state matrix.
Parameters:
1. Feature Library: Instantiate `pysindy.WeakPDELibrary`. Set `library_functions` to include polynomial terms up to order 3. Set `derivative_order` to 4 (since the Kuramoto-Sivashinsky equation contains a fourth spatial derivative).
2. Spatiotemporal Grid: Pass your spatial and temporal arrays to the library construction.
3. Integration Domain: Set `K` (the number of integration subdomains) to 1000.
4. Optimiser: Use `pysindy.SR3` (Sparse Relaxed Regularized Regression) with a sparsity threshold of 0.1 and `max_iter` of 100.
Replicates and Seeding: Run 10 independent replicates using standard NumPy random seeds (e.g., 0 to 9) to govern the noise generation.
Compute Cost: Less than 1 CPU hour on a standard workstation.
Expected Result: The algorithm will return a sparse coefficient vector where only the terms `u_xx`, `u_xxxx`, and `u u_x` survive, with coefficients close to their true physical values (-1, -1, and -1, respectively). 

Three common ways people get this experiment wrong:
1. Attempting to use standard finite-difference derivatives instead of the WeakPDELibrary on the noisy data. The high-frequency noise will be amplified by the fourth derivative, causing the least-squares matrix to become ill-conditioned and resulting in total garbage coefficients [cite: 3, 4].
2. Forgetting to omit the linear target term from the candidate library when dealing with implicit or complex PDEs, causing the optimiser to trivially fit the identity function [cite: 34].
3. Failing to normalise the columns of the library matrix before applying the sparsity threshold. Higher-order derivatives will have vastly different numeric scales than low-order polynomials, causing the thresholding step to unfairly penalise and drop valid terms just because they have small absolute numeric weights.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

There is a glaring gap in the software ecosystem for a native, GPU-accelerated, auto-tuning weak form equation discovery tool for high-dimensional partial differential equations.

What goes in: An N-dimensional tensor of noisy measurements, a tensor of spatial coordinates, a time vector, and a library specification.
What comes out: The sparse coefficient vector and the optimal integration radii for the test functions.
The hard part: The weak formulation requires integrating the data against compactly supported test functions over thousands of subdomains. In 1D or 2D, this is fast. In 3D or 4D, the number of required convolutions explodes. The state-of-the-art method uses the Fast Fourier Transform to exploit the separability of the test functions, achieving logarithmic scaling [cite: 5, 31]. However, the canonical implementation of this FFT-based weak form (WSINDy_PDE) was written in proprietary MATLAB and abandoned by the authors [cite: 29, 33]. 
How much work it is: Porting the MATLAB FFT weak-form logic into a modern framework like JAX or PyTorch, handling arbitrary boundary conditions, and writing a differentiable pipeline to auto-tune the test function hyperparameters would take a competent computational scientist two to three months of dedicated engineering.

This is a real gap. PySINDy provides a basic `WeakPDELibrary`, but it lacks the advanced, mathematically rigorous a priori test function selection and FFT acceleration defined in the original Messenger and Bortz papers [cite: 5, 31]. Several research groups have privately written their own hacky Python scripts to bypass PySINDy's limitations for specific 3D fluids problems, signalling that an off-the-shelf, high-performance solution is desperately needed.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

Pointwise Derivative Estimation on Real Data
The original methodology of estimating time and space derivatives using finite differences or total variation regularised derivatives completely failed to scale to real-world applications. It was proven that even minor measurement noise (above 1 to 2 percent) would be catastrophically amplified by numerical differentiation, completely obfuscating the underlying dynamics [cite: 3, 4]. This failure forced the entire field to abandon pointwise derivatives and pivot to integral/Galerkin formulations (Weak SINDy) [cite: 3, 5].

Large Language Models as Zero-Shot Equation Discoverers
Initial programmes attempting to feed raw data arrays into Large Language Models and prompt them to return governing equations appeared highly successful on standard benchmarks. However, this was later proven to be a severe methodological artefact. The LLMs were not reasoning about the data; they were pattern-matching the prompt descriptions and variable shapes to recite textbook equations (like the Feynman equations) they had ingested during pre-training [cite: 6]. When researchers applied symbolic transformations to these datasets (switching roles of inputs and outputs, or mapping to obscure mathematical forms), the accuracy of state-of-the-art frontier models like GPT-4o collapsed to below 35 percent, and non-reasoning models collapsed to below 10 percent [cite: 8, 10]. The claim that standard LLMs can perform zero-shot mathematical discovery has failed to replicate under rigorous conditions.

The SRBench Methodological Critique
A standing critique of the entire symbolic regression field, formalised heavily by Aldeia et al. in 2025, is that the community optimises for the wrong metrics [cite: 12, 13]. Traditional benchmarks reward algorithms that find the smallest possible equation that fits a toy dataset, leading to severe overfitting to Occam's Razor. Furthermore, the field historically ignored computational cost. The critique points out that some evolutionary algorithms burn hundreds of kilowatt-hours to find a solution that a sparse regression algorithm finds in seconds, yet they are ranked equally on accuracy tables [cite: 12, 13]. This critique is currently unanswered in the structural design of most algorithms, though SRBench has begun enforcing runtime tracking to expose these inefficiencies [cite: 21].

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

1. The Agentic Discovery Loop (Highest Priority)
What has not been done is building an autonomous loop where an advanced reasoning LLM acts strictly as a domain-expert prior generator, and a deterministic tool like PySINDy or PySR acts as the experimental execution engine. You would build a system where the LLM reads a scientific context, proposes specific bespoke feature libraries or constraints, commands the execution of the sparse regression, evaluates the residual errors, and iteratively refines the library based on the data feedback [cite: 10]. This is feasible now because of structured outputs and tool-calling interfaces in frontier LLMs. It measures the ability of neuro-symbolic systems to discover genuinely novel physics rather than memorising them. This idea would be falsified if the agent loop fails to out-perform a simple brute-force library expansion on the LLM-SRBench LSR-Synth dataset.

2. End-to-End Latent Weak SINDy
Real-world systems rarely provide measurements of the exact governing state variables; you usually have proxy sensors (e.g., pixel intensities instead of fluid momentum). You should build an architecture that simultaneously trains a shallow autoencoder to map sensor data to a latent space, while enforcing a Weak SINDy loss function on that latent space to ensure it is governed by a sparse set of equations [cite: 14]. While basic versions of this (SINDy-SHRED) exist, they rely on clean numerical derivatives [cite: 14]. Fusing the Weak Form (integration) with a recurrent decoder architecture is feasible now due to advancements in JAX/PyTorch autodiff over integral operators. It would measure the true intrinsic dimensionality of chaotic video data.

What will NOT work:
Attempting to train a massive, end-to-end transformer model from scratch to map raw time-series data directly to LaTeX equations. This will fail. The combinatorial explosion of mathematical grammar combined with the chaotic nature of physical trajectories means the network will simply memorise the training distribution. As demonstrated by the catastrophic failures documented in the LLM-SRBench evaluations, pure sequence-to-sequence models completely lack the inductive biases required to generalise physical laws out-of-distribution [cite: 8, 11]. Without an explicit structural constraint like a sparse regression layer or a symbolic evolution engine, the model will hallucinate physically impossible terms.

**Sources:**
1. [pnas.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRO_5UZh1IXgiOv1BFkRRzYTj6xMjBcOA2k-QoRCSbG6KwyCsNSACfD3N7-8C7J5lsTk3Wwk_cTYFPc3rjzCSZEryYVAcZ-xKJ1zAl1mOkvIWmhruAvLmyscOAmUhBBSSWDN3N5Q==)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJWHcA8U_3T8C54qhUcftN3uv35Ag0rKJTeSLEOGPWCYODE5XMzIuee3-QnoWDxLhK1-cbzh-ptA0a1KMv78aQvxzysQMQKxme-D6QKTT0kzxZ7L9tcKyuR5B3lHyo6OApRFrrxnAIqiaMvWB5MRWhG1ZM3gHnjHaweBZwyfQBYBSgGFZZWz1EIunFITneUNxeROiQ6IuKfXg=)
3. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHD4cyZDTXhTrZmA8h_delx92LZh1kirMEah3gNqJMdHAa8d2n6i3xTkMMtsurNlrIs3QyUDGd1hObZ1wMJNlsy4b919f0guBnrc-FfgUGAy3DDmVMqTc5LMwP85-CB)
4. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpsjWE0efT-9OCxUCWxXvumG5Cp1PgooI0tmvliu_-UPo-9kznWmbsse4p_MydP9kCYoEvSJV5pjcicxOhKuZrgid2g0qQZxMsYtj2qNIOmedI_mseD9cbMfGhN1LWnw8i29KQjjRtmeamsVIr4QlPlKppSd7zocpO)
5. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFNSLTvq8gluYuhg-yrtIQUHMJHLkJV1dxBv65I9wwCzwFzKrOMH3BaqAi9dfUTb8neC3VkjFWZoxd4yNeKyN0HLpTvtZu-5Z-UsjOlQfUyT_jCOZAXqabhY1T0xm6E4U_1HETfOI=)
6. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_9QEvfkFUWQlz57L8CNN0BMPkXulL_C17FmdtzmZrExWoW0Oxau-d_-niR8Cmx8Zy0hGPHXI7sDpuxZPOcRoVh6qWaWyoeFcxL_W1zW17f9JP_ja64hOW5ndTKQ==)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKZqWHgQxF0yiFfJuI4AvAJ-rtaZ7U7DZT3lX29WTL9_r1-4oJaMsVY3MN-KtWeKXNy2_7i9QM4OfP4cVAUUAxu6dg1-onUmOlERAuc9ZA5x2osh0EcDkkMh_Cbdl5DPb-BaW0i2yDYZTWi_w1xH6BoNVZpAMf2sknmnWWjjBYuzdMER95PK2xHvDBqVw493ZfEBDxi1Fvjb1yKO-GTC6gYEi2DyLDznJK7d9HtKprm5e5h9tqWVxptsT2UQwYSrbw)
8. [creddy.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFB1PuNmHqigKKXbl_HFVbp0iTzBUefa5yj7FSEc1SZF6i84WprkJUQf75qk69SrFjOXFDUQDzHQMXO5G4MgnN_46jxa881m0VmxOf9ULXJQP7HAaz7QroZVA==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0zbWPR3jwEcKDDeaP9LPpMJfFJerxesLB_ZDsG-MPeLm-S6hrAA3iyBejZTsv-bYj9pY_SmQX5v8dGxeNlVsVrkhMjHbOn7Ap2vFnJB-mtOQVyq2m)
10. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5dOFDYPrgWMWl7-q0RVrdEEiC6-qtKMd8P9mVJqhdk3pS0bldTj6PXCzDjKN8pJ7EjbppsTHBtNVOB97tmXc4ysPPrztBpldNLTTKX6l2YdOKp7T1y5s3XqJfew==)
11. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzKxEdAwVv_WxANzEpe5ljS0zxvj9DtzB_pADqzV0UWlPIYzfthqz4T2uj2yW8ahcKSDoFCchvYnwyUdeC-15KlHOxU0kwfuC8_zcOjcdPcocXRI_a9iaIHbjKQAgA)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMbzgP6eXm4ev6FygeBNTIvpZuAmwXrHPbKCLsnovYnZjAyJdjsETy7VcLPiL7A_6JefD_LiVL38wsioShFeoVxBuh_5xNZagXWbjOP_zwx0Rvo5f-)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEq5DWkdvCnaEJQXnq9JySIziBD-VwgwW87Xyi3hgvTKgkOBt1GQGYYbJRmCPkb_mQTRXDCUU5n5ODL6UhyaNVPkltpQtM-mOqDAjqwwq6DRCswAPV4VEtDX6eOY19CtNJW8v6j_zBIVXuFIO0mhw63rH1xrb0C8RcuGhzd6eTx5x1_Y7cgH1iFdCAsWxdAoidXFada-szar6SKyhYXgCdP15ZnTyilTI-S_VB4qH0z00RzDTY=)
14. [pnas.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEU2GHWedaWQwKiJEHt2NkvGYWwKhgi_wv-imFEBkh-RNsdt9APkZ3O9OvFUocrnVWFvON2wZcWO_k2-EAa_JP-stl194wSbA1n1p5WJYwYgBKZrzOOCIOCbmUZf8jtpceIm7tnQw==)
15. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRQBSOsaZ3Ys0dwiTZ0dVcWKb8HvjrsUzdJ_h4RetJC67zzvHczqnaEpvjsS4ya7ay4rGlSOKT63PT0mVjzA4HqEYZ45RG983iLSN6FSNjS5c87rmW9FomI-i0axnwc7W8Du-jZXGPpPuqEEDdZbSNscdauxR-2NVtnPYPxDKobZU-IQdDWqhh6RRM5-UklXsLGhdmvsGp1_bc0a2TjvKW7PxDayrAf39FQSAdI8IGVrJ_ZPcsqgXI_XpkKG-w3VeXDBs=)
16. [theoj.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0RH431QkFn23khrKO-Rf36g9isMWrLDPEzE2r2TJSIYR_XAtV2e-KWbbnhbWu1sNGFbfOTzwd_LqDq9FSHhN12KH-IG8_LBXd7jU-Esd8ByUbjDI4UE4-MaP0A4djsTMEqaXRQ-4=)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXk9G1PpM8aHqJgoEl_dcbI5eXMJS75edtqMPW9mBC3vQpu1faiNPBCDKrmAVnJ6r05v4-42BXleGkjeKGtSS2BRTthrnSXPgK6idxg3F8iD_HBn8942Z_LQF-6J_Qnw8vzge8_w_Vqrs5Rwi3l65qSf0ZpPPfZxp0yYZjn8AqELznV5GlZDCbZgpPWrqwdGQcnpX5R_XAnmp1n_FCWDt06Dnzn_vk8EBzZxGpOzm6HTv7-DM4g4C7kyXrgAHCnmkRl_xUP2yb0A==)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtHBUUudWypyCXsj2nEGvcuotKaBP2C4mpmMjOib5Nd1kRvpd1yIgRDe9Adaf_dfDM9UmSR_E8baKzg7L62Q1NOH26C-FM8-VHfME3z9AHS7gSg0hdn5qWX7tbr8w9xCGULHaUnHTwnw1UbZNI5QNQ5hqW_tJDS0I-28p7MjBBlGSx3UTJWX2LPU7978bOkdzmbVBsI7j2TCVQVF17xNvLgSCDSKPMWIj350YwDg4Kr5yXazlyQA==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGX3ebHqm3mkfTIWrbNFFWBKL7y3MqRIkxh44-082L6Zad0c9Auo7vPqFciryp4Y4ilmbbH6eJptO3zQXFv6mlhPQnoO_ii_vNM_hhL3AnY1G4OGq__)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8M4hQD41Vy-BgbvctNd9BniYkk_jBA_uFxG10K1lbkohcY4xWlb31frmshzFNnc7ZNJGWiO9pGV_rhQNITpvOWnYfRMv4ZpQVHK5zwcO6YzTUUmnpjG0v)
21. [cavalab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGT77T8-8bc-RsKuoI8WSh8A8tcA-EhHszRcUsHm-QCZ6YDxd5PVmXeLAXe2qnGjw6YvI69twlPyAutir18wZqdXNFyhICwV_8tfggj3Vg9e3hkx9Ia_SjFgDoxPqc-m9IUvAwKDF6XsXFrZdrFAzlhpbtDqNWbOI4sefkBWuz5DfroSc6cnr97hmdQgwfuHldmg_Ryw4CwItCIFm8vSWXNDXznH_hAVjj8FVcCXJ5tIbbMUT2qPdO16lMvJc_nHz_Brd6JBl-Y)
22. [theoj.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1zdkAj4WMCenW-i4hpKGWw7U0jh0_fPH2xmkp_1TNnan3ipoyQJ06RPqEkJH4r7a0UgwMVS0lmhLul_Inh4YV7WW38mAV1HP8AyVMy0ki8352FDNzFHnF9t9iGOVXF8xzT6b9VsM=)
23. [isma-isaac.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlqIlTyS_Xgm4C3licdFyLca1iUIdql1q2iuwD7FtaBnz8nmZaSyHzN287WbR4G9Sf-oW9FhVWR3zkWJQB0f4DrEsetJuT7zKjRmB2XN1MheujzwsInTcB3SVZCkB7pxPuhpyhv4_8g9qNwGjfPdhakphcImUIWtJF_YlhY6D_6Rownnu2IGRSshMzE7Niz1g=)
24. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3HWILg3FUPr_4Zp5mqb1H-o40NEfOU7rK1XV5S6Jh_Y0AimwTz5M7XTP-85IXrB-c-_Qr4vOuvL_lx69LLT9lRN06eA5sLLkG034WB1P5MKWodiBBtjMt2Hce)
25. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxWqvxX7u32eF_-OAvIil8Dpqv657BRmT3TQdmMgzBaz6LwKcFwhC3phpna4djiFUrHfjdYijSnTGNQoMEtLnlTYWRx2y8k_CBb3YgRwOdfMz6O87wwHhBOvWg6bXLyQm_afdR)
26. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHljBBjfJhpB1ZrOtU-ckl2UygFY9SO3YbileFhPfgZyTeAvQ-b106y_MaDFj-4g_eTGvFmfuDiKHITUDhVY6j0qv3mEDXpqNOpCM_VkPkMdER21A_XBGjh0kf-CiXGjeQpzgh8MzsTcw=)
27. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8rlmbMvztrwXajSkFKJG7AYuO3k7azRgMfvoN4DIQCknRU2WOSYacwTzy37pbImgfTn460MuT5F5JPlMr48C4S3IacQ_k3nf4rfx3AvuUhXAEVfepoigx2TjlxzU2eqI4EKuwa-9kI9KKuuNicwFCvWvzDgRkTf-1nKznUc4A1HuiDNlTpgxT62K8ukzs5xxaM25jwcjGtOsFkvxv)
28. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqeHCfUXYN4AWYKvvhGod-tQklAtcK1LQsAF3DGzlGMp1JCRgn1Unt8oJsTVzkIEt6AZka2RqOIdTr1snufnJsCfVxETzJrw7g_CCjwE7zNsdfRblUPOW-w9T9ONOGc8gzTrfOkAZEtYXpNeFK5qHNz--4wvkaxtljDGjsMgI=)
29. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXozFvziAR_bYyOOkgzS_LHdslIpVTeV3Ulv5WxeZj4ZAaz3_O9rnBIBh7ayGxItdTO4d37vvYjxnfD47Gdth0X2lk-vxTMVZdRDAxVYxiaeuLCAeEZ-LmfBw9Sg==)
30. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtFWZPL0YAmX9JJsNv17DSagdOh4v-nBDfGClC7iox1orT3r6zv92wG_hqRPYublB3a7yAcC20uZEBB0XQmD38gXWEh0dRAd3EO34EdY1Ym3gz9Wp2SXzo-VGb5Fg03d3v5Gl564gZ)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGs8vTC6OV68ozypiATdw-nYJCYBDsw4Cl_4oXZG7p0Q72zFvqSvwhzm1z-ePNrUQF_2NCdZKReYr1aghxpoj6Yvgt3hA3QRq5lU5T4j6lPRiYtkibg)
32. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsQkWKVbQoVRWWElXSHrSlReZJiD64TI5L5HqZvE18b2ebXodqlX7MAYCnks5pwy7ppbpUhpC_qNlhr06LQaYEpFitL7TjpfUTZldoaOVdSXlSRn2qsekBJWQPKOpc)
33. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQED6sMbj7OYm_YEPg3uIwgCfrIHu-yiZhOKbka79K0RZtI1yYEbhq6FZYfmjQTmwfrfKKVR3rI8JCpdcvGWUKq51MHoMJA58oc2k5q80y7Cn5E=)
34. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCwzc8muo8W9XIF3SXsgtgKcJzhR4TJzsiGRBnd-GyvmLU6EMjw-uwfUdQoQ5hj0BEQPWKvgTn0B2YBohEFka5duqPmSCmVtugCLUfhBQ358uXRRvk4GtzRGp3tCe-WUkCPSzxVkGF43yOVYBl252W0MCDmo5xfWaktuKLYOiJoXXmhDFvn5VqxQ==)
35. [r-universe.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEsvarYQG9pBNq4eWrby7qMkcb16P6ldxuqKyw7fpvfq9f7Q98dJn4NpTCr854fyahg1p-u3LLBF_fjmZIdXoqcGBmS6qTx1ccJGJvcvD-M9ixQbpec32dJegcQiGcdd-61viavb4Pqmfz)
36. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlNDgXBOmvHy0aYNxSJw7NWMaJDyYm0RzUkn0H_03s1qEZvJ-t-I2pkqG0M2ZhqNlr3Q4TkvPrcvkjQWCM26bS0tbVZ3aGFasD8kBK1Lr2f9eLF97OuQ==)
37. [co-mind.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvucjPQDBUChVssZVUF_h7dz1ZLyddzwaHKpKtt8fo7F1hQaq6dTXJtxPv6_7w0oHKY7y3j0o0LdnMfPMWt_TWqH-F6XxpXY7L_Ze_quoDEUxlSaUqx3dONH85AJIZ87P_PhPzcT5jGBwdINStAMj8CsP_nQYDADS_JMGcrA==)
38. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVLmiSKqh4Wt58f_vnTRc9OqSlaFleqWVHD6W3faChTujc3VBzF_x-ykv3U3cozx8iwSNm9icrclQhHiRr4Vx7PbhOB9xAI_KaCpXNDpPlDSgOmNQKLPM=)
39. [cavalab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfFb3TO3Pw5ExuEOU7IuRanAW5z2Q2GID1VJnKvGwlrPdTg2rEQtDCjce3QqbL8E8Dpp0o4hrf_HIpFDhb9QdnF49ZkH4VBTwG6TSVZtH0rQnyvrA9McFGkbyydQ==)
40. [cavalab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7CtdnCSt6DezdJTtugEu_IkPFMsU3rNQguJKRHCaN8N5VUWm8GnVGFdZqcTsAsz2z_fINFEO8e3yVnxivzaBlcsD4suEd-IXfiVr2X8BN3AY=)
41. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXEv9gEhBQqk6_egMIpNKvqplzQNUGH3TJfMZCIs3jM-n-kxBNixnvai87fkklVHQpCuzVK_oHt7l-8Whyo4Wg9rQtTgdT4CpPUyhXCbiBOzpYQGd1HWVWXVRl6RNW)
42. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERLEGHpDE2_3M3qsILsJOGk2v13a03eocD2O92sL00d5HpGkgoPO6EBCP_dEI5rARZxkbtB_gFFv3HRByb1XCF-rGFxYuCW0u8nUdkEQyLu5bFGdOBDGyQJNpBn6mHIOrw-jlceRiY)
43. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjwEwju_7Yko_wx9S2gGM0F3tc4qoGd-JRRbLfS_Aj6FtQVm5NTxpQerFbwTJFUI_sk22PMbamRct3XwbYUw7_eDyLFHpww2pfQnXFcoW5Cjje1qrvFRPGaj4mLmmg3P4RGfHqDA7FMqzqi3xJ)

