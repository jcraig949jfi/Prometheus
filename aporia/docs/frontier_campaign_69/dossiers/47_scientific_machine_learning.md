# Prompt 47: Scientific Machine Learning

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdmMXVmYXNMdEFibkQzOUlQc2ZEeHlBOBIXZjF1ZmFzTHRBYm5EMzlJUHNmRHh5QTg
**Elapsed:** 334s

---

# FRONTIER PRACTITIONER DOSSIER: SCIENTIFIC MACHINE LEARNING

Scientific Machine Learning in 2026 represents a critical convergence of classical numerical methods and deep learning, specifically aimed at solving forward and inverse problems governed by partial differential equations. The field has rapidly matured past the initial hype of merely replacing traditional solvers, now focusing heavily on areas where classical methods struggle: high-dimensional spaces, ill-posed inverse problems, and parameterized real-time surrogate modeling. The core debate has shifted from whether these methods work to exactly why they sometimes catastrophically fail, with recent breakthroughs completely reframing our understanding of training pathologies from theoretical loss landscape issues to fundamental limitations in hardware arithmetic precision.

As a computational scientist entering this field, you will find a landscape that is conceptually elegant but practically brittle. The foundational premise is sound, yet the tacit knowledge required to actually converge a model is vast. You must navigate a fragmented software ecosystem where canonical implementations are often abandoned, and community standards require deep understanding of both backpropagation mechanics and numerical analysis. The most profound realization you will make is that the disconnect between a near-zero optimization loss and a physically accurate solution is not an anomaly, but the defining challenge of the entire discipline. 

Before proceeding to the dossier, your summary of the method requires validation and two critical corrections. Your understanding of the mechanism is excellent, particularly your insight that the difference between the mean squared residual and the relative error is the entire subject. When the residual approaches zero but the error remains large, the field calls this a "failure mode", a pathology that has dominated recent literature [cite: 1, 2]. 

However, your description requires two corrections to reflect the 2026 frontier:
First, you noted that what varies is the network weights. This is true, but you omitted the field's greatest historical limitation: a standard Physics-Informed Neural Network is entirely transductive. It learns a single solution instance. If you change a boundary condition, an initial condition, or a physical parameter like the Reynolds number by even a fraction, you must re-initialize and retrain the network from scratch [cite: 3, 4]. This lack of generalization is why the frontier has heavily bifurcated into Operator Learning, where the network learns the mapping between infinite-dimensional function spaces rather than a single solution.
Second, you noted that the network is usually trained by Adam followed by a quasi-Newton refinement like L-BFGS. While historically accurate, we now know this standard pipeline is deeply flawed when executed in standard single-precision floating-point arithmetic. Recent findings prove that L-BFGS routinely triggers premature convergence conditions under standard precision, freezing the network in a spurious failure phase [cite: 2, 5].

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Scientific Machine Learning today is primarily occupied with embedding physical domain knowledge into deep learning architectures to ensure predictions are strictly governed by known laws of physics, thereby reducing the massive data requirements of black-box models. The field serves as the computational engine for modern digital twins, aerodynamic surrogate modeling, and in-silico material discovery. The initial excitement of standard physics-informed networks has settled into a rigorous engineering discipline focused on scaling these architectures to complex, multiscale, and highly nonlinear regimes where traditional finite element or finite volume methods become computationally intractable.

What is SETTLED is the fundamental viability of automatic differentiation as a replacement for spatial and temporal discretization. It is universally accepted that exact derivatives can be computed through the network graph, avoiding truncation errors inherent to classical meshing. It is also settled that these methods are uniquely superior for ill-posed inverse problems, such as inferring a hidden velocity field from a sparse set of temperature measurements, because the forward and inverse formulations are identical in code.

What is CONTESTED is the root cause of training failures on stiff or high-frequency equations. For years, the prevailing consensus was the "Loss-Barrier Hypothesis", which posited that steep, rugged loss landscapes prevented optimizers from finding the true solution basin. This was countered by the concept of "spectral bias", arguing that neural networks inherently prioritize low-frequency components [cite: 1, 6]. In the last year, a fierce disagreement has erupted due to evidence suggesting the real culprit is simply insufficient arithmetic precision. Researchers advocating for the "precision-induced stall" theory demonstrated that simply upgrading the exact same vanilla architectures from 32-bit to 64-bit precision completely eliminates supposedly fundamental failure modes by preventing the L-BFGS optimizer from satisfying premature convergence checks [cite: 2, 5]. The opposing side argues that relying on 64-bit precision is a brute-force hardware patch that ignores the underlying architectural inability to isolate high-frequency features.

What is OPEN is the scalability of these methods to high-dimensional problems. Because these networks rely on evaluating the equation residual at sampled collocation points, moving to high-dimensional spaces causes the required number of points, and thus the numerical integration error and gradient variance, to explode [cite: 7]. The field is actively searching for representations that bypass Monte Carlo spatial sampling entirely.

In the last three years, the field has undergone a massive consolidation. The era of writing bespoke PyTorch training loops for every new equation has largely ended. The field is being absorbed into a standardized, industrial-scale pipeline approach, primarily driven by NVIDIA's ecosystem. What was lost in this merge is the lightweight, hacker-friendly nature of the early frameworks; modern workflows often require navigating heavy, enterprise-grade abstractions designed for multi-node GPU clusters.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL

Raissi, M., Perdikaris, P., and Karniadakis, G. E.
2019
Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations
Journal of Computational Physics
DOI 10.1016/j.jcp.2018.10.045
This is the load-bearing text that formalized the field, demonstrating how to compute exact derivatives using automatic differentiation to penalize equation residuals [cite: 8, 9]. A practitioner must know it because every subsequent paper assumes you understand the notation and the baseline continuous-time and discrete-time models introduced here.

Lu, L., Meng, X., Mao, Z., and Karniadakis, G. E.
2021
DeepXDE: A deep learning library for solving differential equations
SIAM Review
arXiv:1907.04502
This paper introduces the architecture behind the most widely used open-source library in the field [cite: 10]. You must read it to understand how constructive solid geometry and boundary condition abstractions are practically implemented in software.

Wang, S., Teng, Y., and Perdikaris, P.
2021
Understanding and mitigating gradient flow pathologies in physics-informed neural networks
SIAM Journal on Scientific Computing
arXiv:2001.04536
This source identified that the boundary condition losses and the interior residual losses often have wildly different gradient magnitudes, causing the network to ignore the physics. It introduced adaptive loss weighting, which remains a mandatory concept for writing custom training loops.

CURRENT

Nasir, K., Menon, R., and Iyer, S.
2025
Neural Networks Meet Physics: A Survey of Physics-Informed Approaches to Modeling and Simulation
TechRxiv
DOI 10.36227/techrxiv.174612233.30190684
This is the single best recent survey, providing a critical overview of modern network architectures, optimization challenges, and operator learning [cite: 4]. It maps exactly where the boundary between research and production sits today.

Xu, C., Liu, D., Nassereldine, A., and Xiong, J.
2025
FP64 is All You Need: Rethinking Failure Modes in Physics-Informed Neural Networks
Advances in Neural Information Processing Systems
arXiv:2505.10949
This paper single-handedly upended years of literature by proving that many recognized failure modes are actually precision-induced stalls rather than inescapable local minima [cite: 2, 5]. You must know this result to avoid wasting weeks tuning architectures when you only needed to cast your tensors to 64-bit floats.

Kaminsky, N., Freedman, D., and Radinsky, K.
2026
Overcoming PINNs Failure Modes In High Dimension With Low-Rank Fourier Sum
International Conference on Machine Learning
IDENTIFIER UNKNOWN
This spotlight paper defines the absolute frontier for high-dimensional problems by replacing sampling-based collocation with exact, closed-form integration using separable Fourier expansions [cite: 7, 11]. It is essential reading for understanding how the field is moving away from brute-force point sampling.

Chaudhry, F.
2025
Scaling Laws and Pathologies of Single-Layer PINNs: Network Width and PDE Nonlinearity
Advances in Neural Information Processing Systems
IDENTIFIER UNKNOWN
Inspired by scaling laws in language models, this paper provides quantitative evidence that optimization, not approximation capacity, is the bottleneck for complex physics, and establishes empirical scaling laws [cite: 6]. It is vital for estimating compute requirements before running experiments.

Takamoto, M. et al.
2022
PDEBench: An Extensive Benchmark for Scientific Machine Learning
Advances in Neural Information Processing Systems
arXiv:2210.07182
This establishes the authoritative datasets and metrics used to judge modern models, moving the field past trivial toy problems into realistic, multi-scale physical scenarios [cite: 12]. 

PART 3. SOFTWARE I CAN ACTUALLY RUN

DeepXDE
https://github.com/lululxvi/deepxde
Python
Open Source
2026
MAINTAINED
DeepXDE is the community standard for rapid prototyping, originating from the foundational Karniadakis group [cite: 13]. Today, it can easily run forward and inverse solves on complex constructive solid geometries using PyTorch, JAX, or TensorFlow backends. Its known limitation is that it abstracts away the training loop so heavily that implementing highly custom, non-standard gradient penalties or multi-GPU scaling requires fighting the framework.

NVIDIA PhysicsNeMo
https://github.com/nvidia/physicsnemo
Python
Apache 2.0
2026
MAINTAINED
Formerly known as NVIDIA Modulus, this is the enterprise standard for scaling experiments to multi-node clusters [cite: 14, 15]. It can run industrial-scale surrogate modeling using Fourier Neural Operators and Graph Neural Networks on multi-million node meshes. The gotcha is a remarkably steep learning curve, heavy reliance on the NVIDIA software ecosystem, and frequent breaking changes between major versions. If you are building a production pipeline, use this; if you are testing a math hypothesis, it is overkill.

NeuralPDE.jl
https://github.com/SciML/NeuralPDE.jl
Julia
MIT
2026
MAINTAINED
This is a solver package within the massive Julia SciML ecosystem that translates differential equations into neural network optimization problems automatically [cite: 16, 17]. It can run extremely general stochastic and fractional differential equations seamlessly. The obvious limitation is that you must write Julia, isolating you from the broader PyTorch machine learning ecosystem.

Replication-PINNs
https://github.com/oscar-rincon/Replication-PINNs
Python
Unspecified
2021
DORMANT
This was a famous PyTorch reimplementation of the foundational 2019 TensorFlow 1.x code [cite: 18]. While theoretically useful as an educational tool, it is effectively dead. Modern toolchains have evolved, and the published results here often fail to reproduce on newer hardware due to subtle changes in PyTorch's default automatic differentiation graphs and precision handling. Do not use this for new experiments.

PART 4. DATA AND BENCHMARKS

PDEBench
https://github.com/pdebench/PDEBench
Data repository accessed via DaRUS or HuggingFace
Approximately 1 Terabyte
MIT and BSD 3-Clause
This is the authoritative benchmark suite the field uses to measure true progress, containing forward and inverse problems for 1D, 2D, and 3D equations including compressible Navier-Stokes and shallow water equations [cite: 19, 20]. It measures continuous error metrics against high-fidelity classical numerical simulations. 

A critical known overfitting problem with PDE benchmarks in general is that models can achieve a near-zero loss on the training collocation points but fail entirely between the points, learning a highly oscillatory artifact rather than the smooth physical solution [cite: 1, 2]. Therefore, evaluating against the dense, precomputed reference tables provided by PDEBench is mandatory; evaluating the model against its own loss function is considered poor methodology.

DrivAerML Dataset
Access route handled via PhysicsNeMo DataPipes
Approximate size varies by resolution, generally tens of Gigabytes
Proprietary or Registration Required depending on host
Used to measure the performance of machine learning based surrogate modeling on realistic external automotive aerodynamics [cite: 21, 22]. It is heavily used by the industrial sector to test Graph Neural Networks and point-cloud based models.

PART 5. THE REPRODUCTION RECIPE

The most informative experiment to execute in 2026 is the demonstration of precision-induced stalls, proving that optimizing in 64-bit precision fundamentally changes the network's ability to solve previously "unsolvable" failure modes on the 1D convection equation.

Software and Version: DeepXDE version 1.11 or higher, configured to use the PyTorch backend. Alternatively, the specific script from the 2025 FP64 paper authors at https://github.com/miniHuiHui/PINN_FP64.
Dataset: No external dataset is required. The analytical solution for the 1D convection equation is generated dynamically.
Parameters:
Equation: Partial derivative of u with respect to t plus beta times the partial derivative of u with respect to x equals zero. Set beta to 40.
Domain: x from 0 to 2 pi, t from 0 to 1.
Collocation points: 2000 points sampled via Latin Hypercube Sampling.
Network: 4 hidden layers, 50 neurons per layer, hyperbolic tangent activation.
Precision: You must set the global backend float type to float64.
Optimizer: Adam for 10000 iterations at a learning rate of 0.001, immediately followed by L-BFGS with a strict tolerance of 1 times 10 to the negative 16.
Replicates and Seeding: 5 independent replicates using random seeds 1, 2, 3, 4, 5.
Compute Cost: Less than 1 GPU hour on a standard consumer NVIDIA card.
Expected Result: The mean squared residual will drop below 1 times 10 to the negative 8. The relative L2 error against the exact solution will be roughly 0.005 or lower. This is compared against the published failure in FP32, where the relative error stalls near 1.0, effectively a 100 percent error [cite: 1, 2, 5].

Three common ways people get this experiment wrong:
One. Failing to force the entire computational graph into 64-bit precision. If the automatic differentiation engine subtly falls back to 32-bit floats for specific operations, the L-BFGS line search will fail prematurely.
Two. Using completely uniform grid sampling for collocation points. Without stochasticity like Latin Hypercube Sampling, the network will alias the high-frequency components of the convective wave.
Three. Omitting the Adam pre-training phase. L-BFGS is incredibly sensitive to initialization; feeding it a completely untrained random network often causes it to step into an irrecoverable local maximum.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

A generalized, automated precision-switching memory orchestrator for PyTorch that works natively within physics-informed training loops. 
What goes in: A standard FP32 computational graph and a memory budget. 
What comes out: A training sequence that automatically promotes specific tensors and automatic differentiation operations to FP64 only when the optimizer detects a gradient norm plateau, aggressively offloading or checkpointing memory to fit within standard 24 Gigabyte consumer GPU limits.
The hard part: PyTorch's automatic differentiation graph natively resists dynamic precision casting mid-optimization without breaking the optimizer state or causing massive memory spikes. Because FP64 halves the available memory and severely throttles tensor cores on non-datacenter GPUs, training entirely in FP64 is economically punitive. 
Roughly how much work it is: Three to six months of deep systems-level PyTorch engineering. Several industrial labs have rebuilt proprietary versions of this to manage mixed-precision training, which is the strongest signal that an open-source, plug-and-play precision orchestrator is a massive gap in the ecosystem.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The most significant standing critique of the field is that physics-informed neural networks routinely fail to learn the correct solution for seemingly simple problems exhibiting high-frequency components, stiffness, or strong advection. When applied to problems like the Korteweg-de Vries equation or strong convection, early methods looked entirely successful because the loss function dropped to zero. However, when plotted against the true solution, the network was shown to be predicting a trivial zero-state or measuring an artifact of the collocation grid [cite: 1]. 

This led to a massive, multi-year research programme attempting to fix the "rugged loss landscape" of PINNs. Hundreds of papers were published proposing complex architectural changes, custom loss reweighting schemes, and exotic activation functions to navigate these local minima. 

This programme largely failed. In 2025, it was conclusively demonstrated that the loss landscape for these problems is actually relatively smooth. The failure was an artifact of the optimization software. Standard optimizers like L-BFGS rely on gradient norms to determine convergence. In 32-bit floating point precision, numerical noise swamps the gradient signal before the network reaches the true minimum, causing the optimizer to declare convergence and freeze the network in a spurious failure phase [cite: 2]. The standing critique regarding optimization failure was answered simply by switching to 64-bit precision, which exposed that the architectures were fine all along [cite: 2, 5].

Another standing critique is "spectral bias". Neural networks inherently learn low-frequency functions faster than high-frequency ones. This was proven to be a severe bottleneck for turbulent fluid dynamics. This critique was partially answered by utilizing Fourier feature mappings, which force the input coordinates into a higher-dimensional periodic space before entering the network.

A critique that has never been fully answered is the curse of dimensionality regarding collocation points. For a 1D problem, 1000 points might densely cover the domain. For a 4D space-time problem, 1000 points leaves the domain virtually empty. Because the residual is only penalized exactly at the collocation points, the network is free to wildly violate the physics in the void between points. While adaptive sampling techniques have been tried, they are computationally expensive and often fail to scale past 3 spatial dimensions. 

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the current state of the frontier, a well-resourced newcomer should aim at the following specific experiments, ranked by impact.

Rank 1: Implement Low-Rank Fourier Sums for high-Reynolds number fluid flow.
What makes it feasible now: The mathematical framework for evaluating closed-form physics objectives without spatial sampling was just published for high-dimensional spaces [cite: 7, 11].
What it would measure: Whether exact, analytic loss evaluation can prevent the network from overfitting to collocation artifacts in highly chaotic regimes like 3D Navier-Stokes. 
Falsification: If the low-rank assumption fails to capture the intricate, non-separable vortex structures of turbulence, the relative error will stagnate despite the closed-form integration, falsifying the idea that sampling noise is the sole barrier to turbulent simulation.

Rank 2: Establish empirical scaling laws for mixed-precision Operator Learning.
What makes it feasible now: The availability of massive benchmark datasets like PDEBench [cite: 12] and the recent realization that optimization, not capacity, limits scaling [cite: 6].
What it would measure: The exact power-law relationship between network width, PDE nonlinearity, and optimal compute budget when transitioning from FP32 to FP64 mid-training.
Falsification: If the error does not reliably decrease with a predictable power law as network width and compute scale up, the hypothesis that SciML models behave like large language models regarding scaling is falsified.

Rank 3: Train an auto-regressive foundational physics model solely on residuals, entirely devoid of simulation data.
What makes it feasible now: Massive distributed frameworks like PhysicsNeMo [cite: 14] can handle multi-node execution.
What it would measure: Whether an operator network can learn generalized physics solely through self-supervised physical penalty, rather than by mimicking classical solvers.
Falsification: If the model cannot generalize to unseen boundary conditions better than a randomly initialized network, the concept of unsupervised foundation models for physics is fatally flawed.

What will NOT work: 
Attempting to solve three-dimensional turbulence by simply increasing the depth of a standard fully-connected PINN and running it for a month on a GPU. This will not work because the spectral bias of the architecture will prevent it from capturing the Kolmogorov microscales, and the uniform collocation sampling will ensure that the gradient variance remains too high for the optimizer to make meaningful progress [cite: 6]. Adding compute to a fundamentally misaligned architecture will only yield a very expensive, smoothly wrong answer.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzYtXSQNKeGS2NnrizZ5Csnar53g2-3Z29QIPT8j4aEE8_dchsJjHg5DHXvpmjNVaHZWsURmJQs0_03php1vi-haruJ4hahTX_sZE0bniSwIXoDgfSqQ==)
2. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXAYHjpe9r8E4zMZnBmz2biHUuA3ZiXSZbL5805NTic9ioSwn4YoPf6WokUgQ0btIJPnPLCaVO1Am5jdDJkLSrnJTOTRD6nDkAXjlejkOV-1mfrH4JezIttxd6wumSJEeukVU=)
3. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEw8nF-hnBciwqi79vqqaRwQ4vJxwDOKli8RCQH10oW1jiHaXe9KSIfWRMlVvrduG7_aLVIfIxpy5CAd4itDbCjWIZWAga4UzZ0L954mSAj51qVz0qM-nbEWo0Sg==)
4. [techrxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUGbbUn0pTxuje-dRtl1Bf03YPDWLQd0k2dBixzDSEdjFSLu4qJ-CBHmxFlfMCC8z4WUZK1mNsx3ToP9K0Fh0kx0y6byiNTmX2N03k1xhyHoMvXezECsEhAIggFc173fz3XOvm0t3nX_i98Ku0envW_wpAX7F_BA==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVZ8Z_sdV47IkqHZfj0gOXCPsI4y3GH-B7lUl-69LgrdulhbGQXnqez64jOysrE5t_7t-FNE1xL-U4nmlw-eJEA2axb3wr0O1gbn87QXUKHTfSujM5ANAlEQ==)
6. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQ4RMsX9HIKXhDlFz8mOvsi5SKqDgXtFX24ZUkMAHG56XojS4_IiHNUCjwxeGgrl5seilXvXckVm_CET8PhGIpR_0_M1Wf8v33cLjzwbP9_kn4y_0pL4qeG_M5P5-1OGWBfonmo1YRRx9ciO6eCCq2XSUQvD2_mpTrA0mw3nxsCg==)
7. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeLVrDVqCyhRIjoyLFabG50HYFBfnDafqEVxy9lCe5QEESS3b4qkUTUkJmheLVD_WouCN7BCttjPd9J7duOPcsOnmlvtqLMCJkeVQ7aVAL0B0_Kf1irxBgieNjpg9yYYt8H3FOt7austee4QvFReVCgajjWMHKaz89ny73y71gDsEZRkHGofCNDzMDOFz4hpnArpof0MpcPyYX01A_kRQBMBl8kVIMrAyMDNHAR0rgX0gcaBB6vpDS)
8. [iastate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFW7lixR6DsnQ7yDOhYttVZFlwfRwZzf-XZQQ9HTZDxoLNvZHLb9i1xKI2_cVmR-MExUdEEjci0YfyqwGgZrpRzLFnvzNeSKF52zy67c4o7MZCiN5smBiGYJrf5xycbZwCCZ270vMgaR9V5uAEm9bgeSZNX8f_hjazHu15dmN5DwF_MeA==)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEpG0O-C5KMZKKF4l6oDQoz5Pe3nhEejwGIEVVRlS1E-E-YPzdNgtTrO-TTNR9cslqEXvEob1h-lr58IMntverd5n1gFtnl2_w_GSnHMVXZdvGXHRe2u4KPk7uXj4UsGjvKp6Ts_h6tjeH7GWM9tk6DpsSrSAnWFTr-Lw6n2nxaVqbypcfD6OdManJt8jBH6sILMIrh1eZ0V3TKyBccQi697DBpkkcNgb7_WFdifB75IV3TrqQrySTF95nLhx5g9y65LM9eV8RjDKc372XQ21_93910kTjKTw8nbzCCoYeIOq3k1hxJx85SNAbAzoye6POSttYtWGP1vS6NIdSivzp)
10. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8mugwPcGmAsy9sfHTPEtfQfU77rFMjO4JFfeVKQt7MbjSFMjlmY8qbk149tcjptHgrNs8rYrURDlGrT0buxJNjrH2IJAAkGntsE7niLyFmxV9c0AK867afR-lDLIUjfGQoGM5CSzgyZFfsWA3uNPlOYhifO4gBBNLMTFrTi02)
11. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPjeof5MqPesZsCFNOLc2JcRxzQ-rR3cIQ3nFEZS7bVOzA1wbN1Z1f9cudaw3eRz2hfh2criu1M5_u4klbaWdo15_9uARXgY1UMbuFLZF9mtjlBS5Ea7tiO_buQr57rg==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0di6wpN2ER86iKFUH0ncMHloEfFpWZNFjkDbssH5ca9aDE3UewRFFxEhLb7Y7FMSBl7WMdPiYt09zabH6mQgZZVxKz_STIIt4u7NdVlJw3RtLqx3LgH_t2w==)
13. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzbaG8qV9ZEXSag23GLwAzNTGqCB8EVfZOcSTGryz6D1daySHMVkU0eyLtI9DQrqkfmavB40OTVkjTQNTCtv0H-2xuWSir7L8pMI2RbBYca01Mjk3Jd2gQHQ==)
14. [nvidia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEe5Bdh1z8zcVYrtGAnDiS4MTU3fK-DcY8_d8WtdSzNqw10TBCX81IjYHnv4YAPyu2T1qXvvbfTlflKkmoZy-LUqgKQTrNMPQnJtlhZX2HyFAYAnee6blvK1TBrzsbL)
15. [softwareone.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcQS9SC4JaHmRr4W66WTqMWE-w7Yo2xlXBo4xyoZQXjGjdyPuWZRSi6BAX-fA5we4AepJKmLHaDRQwMMkDi_-_p_b-fw8A4IfSSxMX2BHZH9CLQPf-BRGYqx9gNUNEQhILInpOG_xzjw8Khqhp6B8bnmPh83B0IF-0JTS1rym6)
16. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpHBxfQ4T5sxPugJlR-0a15vZZpgXEVftWq-72vZd5tdBR1ZciHNpoU52CWHBB503HJPPM8zggWlPlD5kjXMkYeLlvYL3lPD1l4PRNicxfrVC9L_u74KCVgGYL)
17. [sciml.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyqvn8HMlEtPwyOu2Uh-wGLU6zxparZ6kOvUZXlswnY1044VwLy4F3mHdKBDNKLhHuSePvuWDSFaWMSpGkwMmHqKdnKORei52Z5bukPlkTYd6nLKAFJ5awSi4=)
18. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZY6I8h6e_rQBcZi4WKTL3OM-gUOCpT9DD3YTqiXCdUF0yCiVStzKfHXqr3z6z5qzVjXQJRS_IFgTsLeJsX9g6W_mtgcpyoYFhVMn1awiao6x_ImsYSgt9VZ-NjQcHCq5-U9pWxzbH)
19. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhYChkE3_err0D54AUOTfYHnYYVF2UKrJWr5eUgC8Ghjd4QZ6LKte7wEvzkOmMcV6Xi6gcvOgToZYsVgyJI85nKo_-hjApWhLmn5eQCqr_0uVTn9zoaYzQozk=)
20. [uni-stuttgart.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEl6TtO5wEY-j2vxL6XE4gilgjPY5fNVuah58qwFe9RZKoZmp1ZEVFpA0DNFLNNBzLgOjWWoi7O606Zce_PIK-9n36gGDu3MHdf87al9O1ZVbRoh8MqHopEQcO3nhSb6fdMwUV2_8QVk3DxE8cCN7TNo9ycTQlomSGJaYRB97xqx9tHpQGMzw0=)
21. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkoaZZgBpoxQFrbFhKq7QDqjEfWTh6mBbf8r-u19Moo4fwyPNedgUeJA5m8aR6xYnMLALieqkLapna5Lq4AjxNhayNIjsE5AgEGCWWV5pB7IJSOKAIJb27iAlw8Z3ACqSx03Iyos7KHiB6VWmeau7qRR6oq1C4qnaoF3r21FO5)
22. [nvidia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtoB7bsoRYqZQQQURFdREJOHGBexuEGl0cwePxSLjupmRb9G0GTfcWvH0We3Q6EFa8WwnpRzp_iOgy190YJwXYeUW5FXudKy2z6Yw2gExNxzOnaxyyQisE9HSCzXY5rzPWWubJGN1rxwlNJXAwBwY4CZKPPtgFFrmyrDEjNIaTcHxhYR-fbQ1k7gbRXFR8Qq9LtO377E4jRkI=)

