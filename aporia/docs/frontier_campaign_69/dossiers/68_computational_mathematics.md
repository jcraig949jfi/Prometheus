# Prompt 68: Computational Mathematics

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdHR2FmYXEzbEhfYTBfUFVQZzZYaGlRTRIXR0dhZmFxM2xIX2EwX1BVUGc2WGhpUU0
**Elapsed:** 425s

---

# FRONTIER PRACTITIONER DOSSIER: COMPUTATIONAL MATHEMATICS OF ANOMALOUS STOCHASTIC PROCESSES

**Key Points**
* The baseline method described in your query perfectly characterises classical Brownian motion, but it is fundamentally outdated. The computational frontier exclusively studies **anomalous diffusion**, where increments are not independent and scaling laws are non-linear.
* Deep learning and convolutional neural networks have decisively dethroned classical analytical metrics, such as the Time-Averaged Mean Squared Displacement, for characterising short, noisy stochastic trajectories. 
* A major theoretical schism is emerging regarding the mathematical foundations of anomalous diffusion, pitting the standard Fractional Brownian Motion against the computationally superior Fractional Ito Motion.
* Trajectory segmentation—detecting exactly when a walker changes its physical state or environment—is the definitive benchmark task for computational mathematicians in this field today.

**Introduction**
You are entering a field that has undergone a profound methodological revolution in the last five years. Computational mathematics applied to stochastic processes has pivoted away from deriving asymptotic analytical bounds for idealised random walks. Instead, it has fully embraced data-driven inference on highly constrained, non-Markovian, and heterogeneous trajectories. This dossier will serve as your blueprint for navigating this frontier. It provides the explicit corrections to your initial theoretical anchor, curates the load-bearing literature, and catalogues the software and benchmarks you need to execute experiments today.

### ANCHOR CORRECTION: FROM CLASSICAL TO ANOMALOUS DIFFUSION

Your query anchors on the following premise: "Because each increment is independent with mean zero... the displacement after n steps is asymptotically normal... and the spread grows as the square root of the number of steps, which is the diffusive scaling law." 

**This description is outdated and misattributed for the current frontier.** 
You have flawlessly described classical, normal diffusion (Brownian motion). However, the frontier of computational mathematics and stochastic physics has abandoned this as the primary object of study. In real-world systems ranging from intracellular transport to financial market volatility, the assumption of independent increments and uniform step scales completely breaks down. 

The frontier studies **anomalous diffusion**. In anomalous diffusion, the spread (mean squared displacement) does not grow linearly with time, but rather scales proportionally to time raised to an anomalous exponent, alpha. If alpha is less than one, the walk is subdiffusive; if alpha is greater than one, it is superdiffusive. Furthermore, the mechanisms behind this are distinctly non-classical:
1. Increments are often **not independent**. In Fractional Brownian Motion, the increments have long-range temporal correlations. 
2. Step times are often **not uniform**. In Continuous Time Random Walks, the waiting time between steps is drawn from a heavy-tailed distribution, meaning a walker might pause for orders of magnitude longer than a standard step.

Your experiment must be updated. You are no longer measuring if an independent random walk stays within Gaussian bounds. You are measuring what class of anomalous correlation is driving the walk, and what the anomalous exponent is, given only a short, noisy, and potentially non-ergodic fossil of the trajectory.

***

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Computational mathematics in this subfield is now the science of decoding complex, non-Markovian stochastic trajectories using machine learning and advanced numerical simulation. It sits at the intersection of statistical physics, applied probability, and scientific machine learning. The primary objective is to take a short, noisy time-series of a random walker and infer the underlying generative stochastic differential equation, the anomalous scaling exponent, and the presence of dynamic state changes.

**What is SETTLED:** 
The debate over methodology for short trajectories is over. Machine learning—specifically convolutional and recurrent neural networks—vastly outperforms classical statistical estimators like the Time-Averaged Mean Squared Displacement when trajectories are short (under 200 steps) and contaminated with localization noise (cite: 41, 46). It is considered settled that attempting to classify anomalous diffusion models purely by calculating summary statistics is a dead end.

**What is CONTESTED:**
There is a massive live disagreement regarding the foundational mathematical model of anomalous diffusion. On one side is Fractional Brownian Motion, the historical standard, which relies on correlated increments. It is notoriously difficult to simulate, lacks a martingale property, and is analytically intractable for many stochastic calculus applications. On the other side are proponents of Fractional Ito Motion, a newer model that generates anomalous scaling via spatial volatility and logarithmic potentials rather than temporal memory (cite: 37, 77). The debate is whether Fractional Brownian Motion is a physical reality or merely an inconvenient mathematical artifact that should be replaced by Fractional Ito Motion.

**What is OPEN:**
The frontier is wide open for out-of-distribution generalisation and the characterisation of heterogeneous, multi-state random walks. When a walker dynamically changes its environment (e.g., entering a trap, dimerizing, or changing its diffusion coefficient), segmenting that trajectory accurately remains an unsolved problem under high noise conditions (cite: 11, 26). 

**What changed in the last three years:**
The field absorbed single-particle tracking analysis entirely into the domain of deep learning. The classical approach of fitting theoretical curves to empirical data has been swallowed by the Anomalous Diffusion (AnDi) challenge framework, where researchers simulate millions of paths and train over-parameterised networks to learn the inverse mapping directly. The nuance of analytical stochastic calculus was temporarily lost in this merge, replaced by brute-force simulation and pattern recognition.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

**FOUNDATIONAL SOURCES**

Metzler, R., Klafter, J.
2000
The random walk's guide to anomalous diffusion: a fractional dynamics approach
Physics Reports
DOI 10.1016/S0370-1573(00)00070-3
This is the definitive, load-bearing survey that established the mathematics of fractional dynamics and Continuous Time Random Walks (cite: 38). You must know this because it defines the theoretical bounds and generating fractional Fokker-Planck equations that every modern simulator approximates.

Burov, S., Jeon, J.-H., Metzler, R., Barkai, E.
2011
Single particle tracking in systems showing anomalous diffusion: the role of weak ergodicity breaking
Physical Chemistry Chemical Physics
DOI 10.1039/c0cp01879a
This paper exposes the fatal flaw in classical trajectory analysis. It proves that for non-ergodic anomalous processes, time-averaging a single trajectory does not converge to the ensemble average (cite: 56, 57). You must know this to understand why classical mean squared displacement fails.

Granik, N., Weiss, L. E., Nehme, E., Levin, M., Chein, M., Perlson, E., Roichman, Y., Shechtman, Y.
2019
Single-Particle Diffusion Characterization by Deep Learning
Biophysical Journal
DOI 10.1016/j.bpj.2019.06.015
This is the proof-of-concept paper that caused the field to pivot (cite: 41). It demonstrates that a neural network trained on simulated Fractional Brownian Motion and Continuous Time Random Walks can classify experimental trajectories using orders of magnitude less data than classical methods.

Munoz-Gil, G., et al.
2021
Objective comparison of methods to decode anomalous diffusion
Nature Communications
DOI 10.1038/s41467-021-26320-w
The results of the first Anomalous Diffusion Challenge. It is the foundational benchmark paper establishing that machine learning universally beats classical statistics for trajectory inference across all tested scenarios (cite: 46, 48).

**CURRENT SOURCES (2023 ONWARD)**

Eliazar, I., Kachman, T.
2022
Anomalous diffusion: Fractional Brownian motion vs. Fractional Ito motion
Journal of Physics A: Mathematical and Theoretical
DOI 10.1088/1751-8121/ac4cc7
This is the most critical theoretical challenge at the current frontier. The authors propose Fractional Ito Motion as a replacement for Fractional Brownian Motion, offering a model that is a martingale, easy to simulate, and analytically tractable (cite: 37, 77). 

Pacheco-Pozo, A., Krapf, D.
2024
Fractional Brownian motion with fluctuating diffusivities
Physical Review E
arXiv:2405.03836
This paper addresses a vital gap by extending Fractional Brownian Motion to environments where the generalized diffusion coefficient is itself a stochastic process. It is required reading for modeling complex, heterogeneous systems (cite: 36, 74).

Munoz-Gil, G., et al.
2024
Quantitative evaluation of methods to analyze motion changes in single-particle experiments
Nature Communications
arXiv:2311.18100
The manifesto for the second AnDi challenge. It shifts the frontier from homogeneous trajectories to phenomenological models involving state changes, traps, and dimerization (cite: 11, 69).

Asghar, S.
2025
U-Net 3+ for Anomalous Diffusion analysis enhanced with Mixture Estimates
arXiv:2502.19253
Details the architecture of U-AnD-ME, the top-performing model in the 2024 AnDi Challenge. It demonstrates how full-scale skip connections in convolutional networks resolve the timestep-level segmentation problem for random walks (cite: 67).

Hatzakis, N. S., et al.
2024
Deep learning assisted single particle tracking for automated correlation between diffusion and function
Nature Communications
DOI 10.21203/rs.3.rs-3716053/v1
A highly advanced application paper showing the endpoint of this field: using deep learning not just to extract mathematical exponents, but to map the segmented diffusion states directly to biological functions in 3D (cite: 42).

PART 3. SOFTWARE I CAN ACTUALLY RUN

DifferentialEquations.jl
https://github.com/SciML/DifferentialEquations.jl
Julia
MIT License
2026
MAINTAINED
This is the community standard for numerically solving standard and stochastic differential equations. It is extraordinarily fast and supports GPU acceleration and automatic differentiation (cite: 31, 32). However, its native support for the highly correlated noise required for Fractional Brownian Motion is limited; you often have to bridge your own fractional noise generators into their SDE solvers. 

andi-datasets
https://github.com/AnDiChallenge/andi_datasets
Python
MIT License
2024
MAINTAINED
The authoritative reference implementation for generating anomalous diffusion trajectories. It natively outputs Fractional Brownian Motion, Continuous Time Random Walks, Levy Walks, and phenomenological models like transient confinement and dimerization (cite: 12, 29). Its limitation is that it is strictly a data generator and evaluation harness, offering no native inference or deep learning models itself.

U-AnD-ME
https://github.com/SolomonAsghar/U-AnD-ME
Python
IDENTIFIER UNKNOWN
2024
MAINTAINED
The state-of-the-art inference engine built on a U-Net 3+ architecture, which won the 2024 AnDi Challenge. It processes trajectories and outputs timestep-by-timestep predictions of changepoints, diffusion types, and anomalous exponents (cite: 14, 66). Gotchas: The repository lacks an explicit open-source license, meaning commercial use is risky, and retraining the Gaussian mixture models requires significant domain expertise.

BI-ADD
https://github.com/JunwooParkSaribu/BI_ADD
Python
GPL-3.0 License
2024
MAINTAINED
The Bottom-up Iterative Anomalous Diffusion Detector. This is a highly robust reimplementation of changepoint detection that combines supervised and unsupervised learning (cite: 11, 61). It performs exceptionally well on single molecular trajectories. Its main limitation is its rigid dependency structure, requiring specific older versions of TensorFlow (2.14 or 2.17).

randi
https://github.com/argunaykut/randi
Python
IDENTIFIER UNKNOWN
2021
DORMANT
A famous early deep learning framework from the first AnDi challenge using recurrent neural networks (LSTMs) (cite: 13). It is effectively dead and superseded by convolutional approaches. You cannot easily reproduce its published results on modern toolchains without heavily downgrading your CUDA and TensorFlow environments. 

PART 4. DATA AND BENCHMARKS

AnDi 2 Benchmark Dataset
https://doi.org/10.5281/zenodo.14281479
Approximate size: Hundreds of directories containing 151 files each (massive scale)
CC BY 4.0
This is the authoritative benchmark of the field in 2026. It is used to measure a model's ability to detect changepoints, classify states, and infer parameters on multistate anomalous diffusion trajectories, trapping, and dimerization (cite: 69, 70). Contamination warning: Because the generation code is public, it is very easy to inadvertently train on the test set parameters. Ensure strict separation of the Zenodo dataset from your training generators.

Anomalous Diffusion Challenge dataset (AnDi 1)
https://zenodo.org/records/3707702
Approximate size: Variable (generator script)
CC BY 4.0
The legacy benchmark for basic anomalous diffusion classification (cite: 15). The field treats this as solved. It measures basic inference on homogeneous trajectories. Do not use this as your primary benchmark today, as modern architectures heavily overfit it.

Stochastic Simulation Dataset of IoT Malware Spread
https://investigacion.ubu.es/documentos/691dfb251915b61ef18a0488
Approximate size: Unknown
IDENTIFIER UNKNOWN
Merely a popular, domain-specific dataset (cite: 16). Included to warn you that "stochastic simulation datasets" often refer to epidemiological or network models, which use entirely different mathematical scaffolding (SIR models) than the spatial continuous random walks you are studying. Ignore these.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to establish yourself in this field is replicating the Single-Trajectory Task of the 2024 AnDi Challenge using the winning U-AnD-ME architecture.

The Exact Specification:
Software: Python 3.10, TensorFlow 2.14, andi-datasets version 2, and the U-AnD-ME repository. 
Dataset Generator: andi-datasets Python package.
Parameters: 
- Dimensions: 2D trajectories.
- Trajectory Length: 224 steps.
- Models included: Single-state, multi-state, transient confinement, dimerization, and quenched traps.
- Anomalous exponent (alpha) range: Drawn uniformly between 0.1 and 1.9.
- Localization error: Gaussian noise added, scaled dynamically to the generalized diffusion coefficient.
Independent Replicates: Train the U-Net 3+ encoder-decoder on 50,000 dynamically generated trajectories per epoch. 
Seeding Regime: Numpy and TensorFlow seeds locked to 42. Training data generated dynamically on the fly to prevent overfitting.
Compute Cost: Approximately 24 to 36 GPU hours on a single NVIDIA A100 or H100 to reach validation stagnation (cite: 66).
Expected Result: When evaluated against the Zenodo AnDi 2 Benchmark test set, the model must achieve a Mean Absolute Error for the anomalous exponent (alpha) of less than 0.15, and a changepoint detection F1 score exceeding 0.85. 
Citation for comparison: Asghar, 2025, arXiv:2502.19253 (cite: 67).

Three most common ways people get this experiment wrong:
1. Ignoring experimental localization noise. If you train the neural network on mathematically perfect random walks, the model will learn high-frequency features that do not exist in reality. When exposed to the benchmark test set (which includes simulated optical blur), the network's accuracy will collapse (cite: 55).
2. Padding trajectories improperly. Neural networks require fixed input sizes (e.g., 224 steps). Experimental trajectories vary wildly. If you zero-pad the end of an anomalous random walk, the network interprets the padding as a "quenched trap" (zero motion) and falsely segments the trajectory.
3. Calculating ground-truth Time-Averaged Mean Squared Displacement on non-ergodic Continuous Time Random Walks to verify the generator. Because CTRW breaks weak ergodicity, the time average will heavily deviate from the theoretical ensemble exponent, tricking entrants into thinking the data generator is broken (cite: 56).

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

A massive technical gap exists for a fully differentiable, hardware-accelerated stochastic simulator for Fractional Ito Motion and Fractional Brownian Motion with fluctuating diffusivities. 

What goes in: An array of time steps, a continuous spatial field representing the logarithmic potential or volatility landscape, the anomalous exponent alpha, and a random seed.
What comes out: A batch of tens of thousands of simulated 2D random walks, alongside the analytical gradients of the trajectory endpoints with respect to the input parameters.
The hard part: Fractional Brownian Motion is fundamentally non-Markovian; every increment depends on the entire history of the walk. Simulating this requires operations like the Davies-Harte method or the Cholesky decomposition of a massive covariance matrix. These operations scale horribly with trajectory length and are exceptionally hostile to the automatic differentiation engines in JAX or PyTorch.
Amount of work: High. This is a 6-to-12-month scientific engineering project. 
The signal: Multiple research groups currently wrap non-differentiable NumPy CPU generators inside custom PyTorch autograd functions, using crude finite-difference approximations or surrogate models to pass gradients backward. A native, differentiable, GPU-accelerated engine for fractional stochastic differential equations would fundamentally shift the field, allowing end-to-end training of inference models directly against the physics simulator.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The most spectacular negative result in this field is the failure of the Time-Averaged Mean Squared Displacement (TAMSD) when applied to single trajectories of non-ergodic processes. 
For decades, researchers assumed that observing a single random walker for a very long time was statistically equivalent to observing many random walkers for a short time (the ergodic hypothesis). Barkai, Metzler, and others launched a standing critique proving that for processes like Continuous Time Random Walks, which feature heavy-tailed pausing times, weak ergodicity breaking occurs (cite: 56, 57). A single walker might get stuck in a trap for the entirety of the observation window. Therefore, the TAMSD remains a random variable and does not converge to the ensemble average. Thousands of biological papers published before 2015 that fit straight lines to log-log TAMSD plots to extract anomalous exponents are now known to be reporting statistical artefacts (cite: 53, 58). 

A second standing critique targets Fractional Brownian Motion itself. While it perfectly matches the anomalous diffusion scaling law, Iddo Eliazar and Tal Kachman demonstrated that it is a mathematical nightmare (cite: 37). Because it is not a semimartingale, standard Ito calculus does not apply, making it impossible to model financial or physical systems that require stochastic integration. They argue that much of the field is forcing a physically unrealistic mathematical model onto data simply because it fits a single scaling law, ignoring Fractional Ito Motion, which achieves the same scaling while preserving Markovian and martingale properties. This critique has only been partially answered, mostly by physicists arguing that biological environments genuinely exhibit the long-range memory that Fractional Brownian Motion models. 

Finally, the machine learning programme has suffered severe replication failures regarding Out-Of-Distribution (OOD) generalisation. Deep learning classifiers trained to distinguish between Fractional Brownian Motion and Continuous Time Random Walks achieve 95% accuracy on simulated data. However, when applied to real biological tracking data where the noise profile is slightly different, the models confidently hallucinate incorrect physics (cite: 25). The neural networks are often shown to be memorising the specific noise signatures of the data generator rather than learning the underlying anomalous diffusion phenomenon.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Rank 1: Empirical Falsification of Fractional Brownian Motion via Fractional Ito Motion.
Design an experiment to train a neural network exclusively on the non-Gaussian dissipation patterns generated by Fractional Ito Motion, and test it against massive open-source datasets of single-molecule tracking. 
Feasibility: High. The theoretical framework for Fractional Ito Motion was solidified in 2022 (cite: 37), but no one has yet built the deep learning inference tools to detect it in the wild.
Measurement: It would measure the shape of the volatility landscape and the martingale property of experimental trajectories.
Falsification: The idea is falsified if the experimental trajectories consistently converge to the purely Gaussian dissipation patterns predicted by Fractional Brownian Motion, proving the environment is homogeneous and memory-driven rather than volatile.

Rank 2: Zero-Shot Generalisation via Contrastive Representation Learning.
Rather than training a supervised model like U-AnD-ME to classify known theoretical models, build a foundation model that uses contrastive learning on unlabelled experimental trajectories.
Feasibility: High. We have enough compute and raw single-particle videos to train massive self-supervised models.
Measurement: It would measure the latent embedding distance between different experimental conditions, mapping the true manifold of anomalous diffusion without forcing the data into human-defined theoretical boxes.
Falsification: The concept is falsified if the latent space collapses and fails to separate mathematically distinct processes, such as dimerization versus transient confinement.

Rank 3: End-to-End Differentiable Volatility Inference.
Solve the gap identified in Part 6 by building a differentiable Fractional Ito Motion simulator in JAX. Use gradient descent to optimize the spatial volatility field directly against an experimental trajectory.
Feasibility: Moderate to Hard. The automatic differentiation of stochastic processes is mathematically perilous. 
Measurement: It would measure the continuous physical potential and spatial diffusivity of a biological cell at nanometer resolution.
Falsification: Falsified if the loss landscape is too chaotic or flat for first-order gradient optimisers to converge on a unique volatility field.

What will NOT work:
Attempting to derive new, purely analytical corrections for the Mean Squared Displacement on short trajectories. The statistical noise floor of trajectories under 100 steps is absolute. Researchers spent a decade trying to add bias-correction terms to classical estimators (cite: 52, 54). Deep learning has definitively proven that the temporal sequence contains non-linear features that summary statistics permanently destroy. Any programme aiming to improve analytical estimators rather than upgrading machine learning architectures is destined to fail.
