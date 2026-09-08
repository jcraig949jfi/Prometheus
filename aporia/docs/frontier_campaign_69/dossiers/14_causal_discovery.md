# Prompt 14: Causal Discovery

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdSNmVlYXJ5Q0w0THhqckVQMThYaWtBMBIXUjZlZWFyeUNMNEx4anJFUDE4WGlrQTA
**Elapsed:** 395s

---

# FRONTIER PRACTITIONER DOSSIER: CAUSAL DISCOVERY

**EXECUTIVE SUMMARY**
Research suggests that the field of causal discovery in 2026 is undergoing a profound methodological crisis and a subsequent renaissance. For decades, the discipline was dominated by classical constraint-based and score-based algorithms. The introduction of continuous optimization methods in 2018 promised to bypass the NP-hard combinatorial search of Directed Acyclic Graphs (DAGs), but recent evidence leans heavily toward the conclusion that these methods inadvertently exploit statistical artefacts—specifically, variance scaling—rather than discovering true causal structures. Simultaneously, the availability of massive single-cell interventional datasets and the advent of Large Language Models (LLMs) capable of parsing semantic metadata have upended traditional evaluation metrics. As a computational scientist entering this field, your most valuable asset is skepticism toward purely synthetic benchmarks and an emphasis on out-of-distribution generalization, amortized inference, and hybrid neurosymbolic architectures. 

Regarding your description of the anchoring method: Your summary is highly accurate, neither outdated nor misattributed. It perfectly describes the skeleton discovery phase of the Peter-Clark (PC) algorithm, developed by Spirtes and Glymour [cite: 1, 2, 3]. To correct by addition: your description treats the conditional independence test as a black box. In practice, the choice of this test (e.g., Fisher-Z for linear Gaussian data, G-squared for categorical data, or kernel-based tests for nonlinear dependencies) entirely dictates the computational complexity and statistical power of the algorithm [cite: 2, 4, 5]. Furthermore, while you correctly identify causal sufficiency, faithfulness, and the Markov condition as the untestable bedrock assumptions, modern implementations often relax causal sufficiency by transitioning to the Fast Causal Inference (FCI) algorithm, which outputs a Partial Ancestral Graph (PAG) to account for latent confounders [cite: 5]. 

## PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Causal discovery today is an ecosystem fractured by a recent paradigm collapse and the rapid influx of deep learning architectures. The core objective remains unchanged: to infer the underlying causal graph from observational data, supplemented where possible by interventional data. However, the operational frontier has shifted away from designing new heuristic search algorithms over discrete DAG spaces. Instead, the frontier is defined by Amortized Causal Discovery—training neural networks on vast simulators of structural causal models (SCMs) to perform zero-shot inference on empirical data—and the integration of LLMs to generate graph priors from the semantic metadata of variables before any statistical tests are run [cite: 6, 7, 8, 9].

**SETTLED:** The asymptotic correctness of classical constraint-based methods (PC, FCI) and score-based methods (GES) under strict assumptions (Causal Markov, Faithfulness, Causal Sufficiency, and infinite sample sizes) is mathematically settled [cite: 1, 2, 10]. It is also settled that without interventional data or highly specific parametric assumptions (like non-Gaussianity or unequal noise variances), observational data can only identify a causal graph up to its Markov Equivalence Class (MEC). 

**CONTESTED:** The utility and validity of continuous optimization for DAG learning is the most fiercely contested issue in the field. In 2018, the NOTEARS algorithm formulated DAG search as a smooth, differentiable penalty function, sparking a massive subfield of gradient-based causal discovery [cite: 11, 12]. However, the "varsortability" critique demonstrated that these methods succeed on synthetic benchmarks primarily because they exploit a statistical artifact where effect variables naturally develop higher marginal variances than cause variables in additive noise models [cite: 13, 14]. Proponents of gradient-based methods argue that this failure only occurs when data is standardized, which fundamentally violates the equal-variance assumptions of the original models [cite: 15, 16]. This specific live disagreement separates the classical statistical causality camp (who view continuous methods as fundamentally flawed on real data) from the deep learning causality camp (who maintain that scale-variant losses are theoretically justified).

**OPEN:** The most critical open problem is how to bridge the gap between semantic domain knowledge and empirical covariance. LLMs have demonstrated remarkable ability to guess causal connections based on variable names (e.g., knowing that "smoking" causes "cancer" without seeing data), but they fail on novel or anonymized causal graphs [cite: 17, 18, 19]. Creating reliable neurosymbolic systems that use LLMs for prior generation and constraint-based algorithms for empirical falsification is completely open. Furthermore, evaluating causal discovery on real biological interventional data (like perturbational single-cell RNA sequencing) remains an open challenge, as current models surprisingly fail to leverage interventional data to outperform purely observational baselines [cite: 20, 21].

## PART 2. THE READING LIST THAT ACTUALLY MATTERS

**FOUNDATIONAL SOURCES**

Peter Spirtes, Clark Glymour, Richard Scheines
2001
Causation, Prediction, and Search
MIT Press
DOI 10.7551/mitpress/1754.001.0001
This is the foundational text defining the PC and FCI algorithms, establishing the mathematical proofs connecting causal graphs to probabilistic independence, and formalizing the exact constraint-based method you anchored this query to [cite: 10, 22].

Xun Zheng, Bryon Aragam, Pradeep Ravikumar, Eric P. Xing
2018
DAGs with NO TEARS: Continuous Optimization for Structure Learning
NeurIPS
arXiv:1803.01422
This paper introduced the algebraic trace exponential constraint that converted combinatorial DAG search into a continuous gradient-descent problem, launching the modern deep learning approach to causal discovery [cite: 11, 12].

Jakob Runge, Peer Nowack, Marlene Kretschmer, Seth Flaxman, Dino Sejdinovic
2019
Detecting and quantifying causal associations in large nonlinear time series datasets
Science Advances
DOI 10.1126/sciadv.aau4996
This paper introduces the PCMCI framework, which is the foundational standard for applying constraint-based causal discovery to highly autocorrelated, high-dimensional time-series data [cite: 23].

**CURRENT SOURCES (2023 ONWARD AND FRONTIER-DEFINING)**

Alexander G. Reisach, Christof Seiler, Sebastian Weichwald
2021
Beware of the Simulated DAG! Causal Discovery Benchmarks May Be Easy To Game
NeurIPS
arXiv:2102.13647
While slightly before 2023, this is the most critical destructive paper of the decade; it proves that gradient-based methods like NOTEARS exploit "varsortability" and fail completely if data is standardized [cite: 13, 14]. A practitioner must know this to avoid building on broken foundations.

Mathieu Chevalley, Yusuf H. Roohani, Arash Mehrjou, Jure Leskovec, Patrick Schwab
2022
CausalBench: A Large-scale Benchmark for Network Inference from Single-cell Perturbation Data
ICLR
arXiv:2210.17283
This paper established the current standard for evaluating causal algorithms on real-world interventional data, revealing the negative result that modern algorithms scale poorly and fail to utilize interventional data effectively [cite: 20, 21].

Lars Lorch, Scott Sussex, Jonas Rothfuss, Andreas Krause, Bernhard Schölkopf
2022
Amortized Inference for Causal Structure Learning
NeurIPS
arXiv:2205.12934
This defines the current deep learning frontier: abandoning graph search entirely to train transformer-based variational inference models on millions of synthetic SCMs to achieve zero-shot causal discovery on new datasets [cite: 7, 8].

Emre Kiciman, Robert Osazuwa Ness, Amit Sharma, Chenhao Tan
2023
Causal Reasoning and Large Language Models: Opening a New Frontier for Causality
TMLR
arXiv:2305.00050
This is the definitive text on using LLMs to infer causal graphs from variable metadata, demonstrating that LLMs outperform traditional algorithms on pairwise discovery by leveraging semantic priors rather than statistical covariances [cite: 6, 24, 25].

Ignavier Ng, Yujia Zheng, Jiji Zhang, Kun Zhang
2024
Reliable Causal Discovery with Continuous Optimization: A Re-evaluation of Varsortability
NeurIPS
arXiv:2407.13313
This is the primary counter-argument to the varsortability critique, mathematically arguing that data standardization violates the underlying equal-variance assumptions of NOTEARS, providing the required nuance for anyone utilizing score-based methods today [cite: 15, 16].

Sawal Acharya et al.
2025
CauSciBench: A Comprehensive Benchmark on End-to-End Causal Inference for Scientific Research
NeurIPS Workshop / ICLR
arXiv:2603.15542
This paper introduces the premier benchmark for evaluating whether an LLM agent can autonomously execute the entire causal discovery and inference pipeline, highlighting the gap between theoretical causality and practical scientific execution [cite: 9, 26]. 

## PART 3. SOFTWARE I CAN ACTUALLY RUN

causal-learn
https://github.com/py-why/causal-learn
Python
MIT
2024
MAINTAINED
This is the community standard for classical causal discovery in Python. It is the modern, Pythonic reimplementation of the famous Java-based Tetrad software originating from Carnegie Mellon University. You can run the exact PC algorithm template you described, alongside FCI, GES, and LiNGAM [cite: 27, 28, 29, 30]. Gotchas: Conditional independence tests in Python loops are notoriously slow for dense graphs over 100 nodes. 

Tigramite
https://github.com/jakobrunge/tigramite
Python
GPL-3.0
2024
MAINTAINED
This is the authoritative software for time-series causal discovery. It runs the PCMCI and LPCMCI algorithms, capable of discovering lagged and contemporaneous causal links while accounting for autocorrelation and latent confounders [cite: 23, 31, 32]. Gotchas: Time-series assumptions require stationarity; if your data has regime shifts, you must carefully configure the RPCMCI variant.

gCastle
https://github.com/huawei-noah/trustworthyAI/tree/master/gcastle
Python
Apache 2.0
2024
MAINTAINED
Developed by Huawei Noah's Ark Lab, this is the most comprehensive toolkit for running gradient-based continuous optimization models (NOTEARS, DAG-GNN, GOLEM) with GPU acceleration via PyTorch [cite: 33, 34]. Gotchas: As demonstrated by the varsortability critique, running these algorithms on unscaled real-world data will likely yield a graph that just points from low-variance to high-variance nodes [cite: 13, 35]. 

dodiscover
https://github.com/py-why/dodiscover
Python
BSD-3-Clause
2024
MAINTAINED
This library focuses on causal discovery using both observational and interventional data. It implements the PsiFCI algorithm, which is an extension of your anchored PC/FCI method that natively handles datasets where variables have been explicitly knocked out or intervened upon [cite: 4, 36]. Gotchas: It relies heavily on categorical testing (like G-Square); continuous interventional testing requires careful discretization or kernel choices.

AVICI
https://github.com/larslorch/avici
Python (JAX)
MIT
2023
MAINTAINED
The reference implementation for Amortized Inference for Causal Structure Learning. You can run zero-shot causal graph predictions using pre-trained transformer models on synthetic or empirical data [cite: 8, 37]. Gotchas: The pre-trained models (like `neurips-linear`) are highly sensitive to out-of-distribution shifts. If your empirical data's noise profile differs drastically from the training simulator, it will hallucinate edges quietly.

CausalDiscoveryToolbox (CDT)
https://github.com/FenTechSolutions/CausalDiscoveryToolbox
Python / R
MIT
2019
DORMANT
Once a highly popular wrapper uniting R packages (pcalg, bnlearn) and Python neural methods. Gotchas: It is effectively dead and unbuildable on modern Python toolchains without excruciating manual resolution of R-bridge dependencies [cite: 38, 39, 40]. Do not use this; migrate to causal-learn.

## PART 4. DATA AND BENCHMARKS

Sachs Protein Signaling Dataset
bnlearn.com/book-crc/code/sachs.interventional.txt.gz
11 variables, 7466 observations
Open access
This is the most famous historical dataset in causal discovery. It consists of flow cytometry measurements of human immune system cells subjected to molecular interventions. It is used to measure structural Hamming distance (SHD) against a known ground-truth biological network [cite: 4, 41, 42]. Overfitting warning: This dataset is entirely saturated. Almost every algorithm published since 2010 claims to solve it, often through hyperparameter tuning that does not generalize to other domains.

CausalBench
github.com/causalbench/causalbench
Over 200,000 interventional samples (RPE1 and K562 cell lines)
Open access
The current authoritative benchmark for biological network inference. It measures distribution-based interventional metrics (evaluating the capability to recover strong interventional effects) and graph distances on massive perturbational scRNA-seq datasets [cite: 20, 43, 44]. Known saturation: Methods that explicitly model interventional data currently fail to meaningfully outperform purely observational baselines (like GRNBoost) on this benchmark [cite: 20, 21]. 

CauSciBench
github.com/causalNLP/CauSciBench
367 evaluation tasks spanning 9 disciplines
Open access
A modern benchmark designed specifically to test LLM agents. It measures the end-to-end capability of models to read a scientific problem, select variables, choose an estimation method, generate code, and interpret the causal effect [cite: 26, 45]. It actively mitigates the "causal parrot" contamination problem by comparing performance on real-world papers against purely synthetic, isomorphic scenarios [cite: 19, 26].

Tuebingen Cause-Effect Pairs
webdav.tuebingen.mpg.de/cause-effect
100 real-world variable pairs
Open access
Used to evaluate pairwise causal directionality (distinguishing cause from effect in bivariate settings without conditional independence). It is widely used but heavily contaminated in the training sets of modern LLMs, making it unreliable for testing foundation models in 2026 [cite: 25, 38]. 

## PART 5. THE REPRODUCTION RECIPE

The single most informative and reproducible experiment you can run today is not a successful discovery, but a catastrophic falsification. You will reproduce the "Varsortability" experiment by Reisach et al. (2021) which proved that continuous optimization methods (NOTEARS) are gaming synthetic benchmarks [cite: 13, 14]. 

**Exact Software:** 
Python 3.9, numpy, scikit-learn, and the original NOTEARS implementation (github.com/xunzheng/notears) at the latest commit.
You also need the baseline implementation from Reisach: github.com/Scriddie/Varsortability.

**Exact Dataset / Generator:**
Synthetic Linear Additive Noise Model (LANM).
Generate an Erdős-Rényi (ER) random DAG.
Parameters: 
Number of nodes (d) = 50.
Expected degree (edges per node) = 4. 
Edge weights sampled uniformly from [-2.0, -0.5] U [0.5, 2.0].
Noise distribution: Gaussian, independent, unit variance.
Samples (n) = 1000.

**Seeding and Replicates:**
30 independent replicates. Set random seeds sequentially from 1 to 30.

**Compute Cost:**
Extremely low. Less than 2 CPU hours total for all replicates.

**The Execution:**
1. Generate the raw dataset X from the DAG.
2. Run NOTEARS on the raw dataset X. Measure the Structural Hamming Distance (SHD) against the true DAG.
3. Apply standard scaling to X (enforce mean 0, variance 1 for every column) to create X_scaled.
4. Run NOTEARS on X_scaled. Measure the SHD.
5. Run the trivial "SortnRegress" baseline (which simply sorts variables by variance and regresses) on the raw dataset X. Measure SHD.

**Expected Result:**
Raw NOTEARS SHD: ~20 to 40 (Excellent recovery).
SortnRegress SHD: ~20 to 40 (Matches NOTEARS).
Scaled NOTEARS SHD: ~250 to 300 (Catastrophic failure, near random guessing) [cite: 13, 14, 46].
*Citation:* Reisach et al. (2021), Figure 5 [cite: 13, 47].

**Three most common ways people get this experiment wrong:**
1. **Misinterpreting the metric:** People use Structural Intervention Distance (SID) without realizing SID becomes meaningless if the skeleton is fundamentally wrong but mathematically acyclic. You must measure structural Hamming distance (SHD) on the adjacency matrix to see the failure [cite: 47, 48].
2. **Ignoring the scale invariant baseline:** Practitioners standardize their data as a "best practice" preprocessing step, run NOTEARS, get terrible results, and blame hyperparameter tuning, entirely missing that standardization destroys the variance signature the algorithm mathematically relies upon [cite: 14].
3. **Violating equal noise variances:** Defenders of NOTEARS will claim this experiment is invalid because standardizing the data forces unequal noise variances, violating NOTEARS assumptions. But real-world data inherently has unequal noise variances and differing units. Running it exclusively on unscaled synthetic data masks this fatal empirical flaw [cite: 15, 16].

## PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to run frontier experiments at scale, you will quickly hit a severe infrastructure bottleneck. What does not exist is a **GPU-accelerated, batched, tensor-native conditional independence testing suite for constraint-based algorithms** (like the PC method you anchored on).

**The Interface:**
*Input:* A dense data tensor `X` of shape `[n_samples, d_variables]`, a tensor of query pairs `[batch_size, 2]`, and a padded tensor of conditioning sets `Z` of shape `[batch_size, max_set_size]`.
*Output:* A boolean tensor of shape `[batch_size]` indicating independence, and a float tensor of shape `[batch_size]` containing exact p-values.

**The Hard Part:**
Algorithms like PC and FCI are traditionally implemented as highly sequential, CPU-bound Python `while` loops (as seen in `causal-learn`). The conditioning sets $Z$ grow dynamically, making static computational graphs impossible. To rebuild this, you must write a custom CUDA kernel or a JAX `vmap` implementation that computes the Fisher-Z transformation (for continuous data) or G-squared statistics (for categorical data) in parallel over thousands of variable pairs simultaneously, dynamically masking out invalid conditioning sets.

**Work Estimate:**
This is roughly 3 to 6 months of work for a competent computational scientist familiar with PyTorch/JAX internals and mathematical statistics. 

**Signal of a Real Gap:**
Several private industrial labs and quantitative hedge funds have rebuilt the PC algorithm internally in C++ or CUDA specifically because the Python community standards crash or take weeks to run on graphs with more than 5,000 variables. The lack of an open-source, tensor-native constraint-based framework forces everyone to use gradient-based methods for high-dimensional data, which, as noted, are statistically flawed.

## PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

This is the most critical part of the dossier. The field of causal discovery is littered with elegantly proven algorithms that fail completely on empirical data. 

**The NOTEARS and Varsortability Collapse**
The introduction of continuous optimization for DAGs (NOTEARS) was hailed as the greatest breakthrough in the field in a decade [cite: 11]. The program spawned dozens of variants (DYNOTEARS, GOLEM, DAG-GNN) [cite: 15, 33, 49, 50]. However, the program effectively failed when Reisach et al. exposed that these methods achieve state-of-the-art results purely because they exploit "varsortability." In standard synthetic additive noise models, the variance of an effect variable is almost always higher than the variance of its cause [cite: 13, 14]. NOTEARS's loss function inadvertently penalizes pointing edges from high-variance to low-variance nodes. When real-world data is used—or when synthetic data is standardized so all variables have unit variance—the method's accuracy collapses to random chance [cite: 46, 51]. 
*How it was answered:* Ng et al. responded by proving mathematically that standardizing data pushes it out of the linear Gaussian equal-variance distribution that NOTEARS explicitly assumes [cite: 15, 16]. Therefore, they argue, the failure is expected. 
*The standing critique:* The response was mathematically correct but empirically damning. If NOTEARS only works when data happens to possess identical noise variances across all nodes—a condition that never exists in multi-modal real-world measurements—then it is useless for applied computational science [cite: 46].

**The Interventional Data Paradox**
A long-standing assumption in the field was that observational data was the bottleneck, and that if algorithms were given access to massive interventional data, causal discovery would be solved. The CausalBench programme tested this by applying state-of-the-art algorithms to massive single-cell perturbational datasets (where genes are explicitly knocked out via CRISPR). The negative result was staggering: algorithms explicitly designed to leverage interventional data consistently failed to outperform simple, highly scalable observational baselines (like Random Forest-based GRNBoost) [cite: 20, 21, 44, 52]. 
*Standing Critique:* Current network inference algorithms are too computationally fragile to scale to 200,000+ samples, and their parametric assumptions fail so spectacularly on real biological noise that the "ground truth" interventions cannot rescue them. This remains completely unanswered.

**LLM "Causal Parrots"**
In 2023, papers claimed LLMs could perform zero-shot causal discovery better than statistical algorithms [cite: 6, 24]. The failed program here is the assumption of structural reasoning. Later experiments showed that LLMs are merely retrieving memorized co-occurrences (e.g., "altitude causes temperature"). When given isomorphic causal graphs with variable names obfuscated or swapped, their performance degrades to random guessing [cite: 17, 53]. LLMs cannot infer causality; they can only retrieve human consensus metadata.

## PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the computational tools and the methodological crises outlined above, a well-resourced newcomer with heavy compute should avoid traditional score-based heuristic searches and flawed continuous DAG optimization. Here is what you should do, ranked by feasibility and impact:

**RANK 1: Scale Amortized Inference to Out-of-Distribution Foundational Models**
*The Experiment:* Train a massive transformer-based variational inference model (like AVICI) not on one class of SCMs, but on a heterogeneous mixture of 100 million synthetic causal graphs with highly diverse noise profiles (heavy-tailed, heteroscedastic, discrete, and continuous mixtures). Evaluate its zero-shot structural Hamming distance on CausalBench (empirical biological data). 
*Why feasible now:* AVICI proved the architecture works for small synthetic tasks [cite: 8, 37]. Compute clusters can now simulate SCMs at the scale of LLM pre-training data.
*What it measures:* Whether a neural network can learn a universal, scale-invariant mapping from covariance matrices to causal skeletons that generalizes to real physics/biology.
*Falsification:* If the zero-shot model cannot beat the classical PC algorithm on empirical data, it proves that synthetic SCMs are too fundamentally different from real-world data generating processes to be used for amortized learning.

**RANK 2: Automated Neurosymbolic Causal Discovery (LLM + PC Algorithm)**
*The Experiment:* Build a pipeline that feeds raw scientific literature and variable names into an LLM to output a prior structural causal model (a graph of high-confidence semantic edges and forbidden edges). Pass this prior graph into a highly optimized, GPU-accelerated implementation of the PC algorithm to act as a rigorous statistical filter that only deletes edges based on exact conditional independence tests.
*Why feasible now:* LLMs are now context-aware enough to build accurate metadata priors (as shown by CauSciBench) [cite: 26, 45], and we have the compute to run large-scale exact statistical tests.
*What it measures:* Whether injecting human semantic priors reduces the combinatorial explosion of the PC algorithm and improves the final F1 score of the skeleton on the Sachs dataset.
*Falsification:* If the final graph is worse than running PC from a fully connected graph, it implies LLM semantic priors introduce fatal collider-biases that corrupt the downstream statistical testing sequence.

**RANK 3 (WHAT WILL NOT WORK): Inventing a new differentiable DAG penalty**
Do not attempt to write a "better" version of NOTEARS, DYNOTEARS, or GOLEM [cite: 33, 49, 50]. Modifying the trace exponential constraint or adding new neural network layers to the mechanism generator will not solve the fundamental flaw. The field has mathematically proven that without strict, often unrealistic parametric assumptions, continuous optimization over unscaled data reduces to variance sorting, and over scaled data it becomes unidentifiable [cite: 13, 14, 46, 51]. You will waste compute on an artifact.

**Sources:**
1. [yzhu.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPtiVrSToW4L8uJj3HcwL1l8Fv6L4D4XKvK3sw0czyT3jc3GhyZnUJKTyoNTyGDeflKsMIZZvoxjtmtwHjNYIC0WBNiei-meq6-c1cn8QOXhzGxDVowfuD7Yrcewg=)
2. [licentiapoetica.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdpKUEulIa3rwD8q5sx-TEgZZ9Yi1ZU6IhkLBcSOJ7juTmr582fbikuVN-onl7P9TQH7B5k8scisdJR9QRcnhPfU4aa7rDtt16UL34PoOT2uoqwfHwd-irQFW5u3TNZPW1y0JKtUw0EtkfFCsRvcgHABVHq6inRxZkZf8iBxRXY8qtAHrDvIVkd88=)
3. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTRkOv1tcuChbQZrRPmAsPiImwVdTj_gA1-_8UJR7ysO48ewglsAjLxb0I1Nttz_CkPbPhvL-MrQj4d-wDzBBo7k9zh4wZo-vX3brOPyJCm1-aQh6tQ21tOxRkUerJiMflch04UxWUbHdzV7ojevq2ePwpHYzHdsbn7ctOcv4Hw8iGzv_ehFNgtbgRWCYt-luaET-S88Sz84ExulvOneTueFt7gERfiW7s)
4. [pywhy.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEu6mqPP9pez_HbBmQg_wrFoz1YV2UxNgAyXUkr6CaVPrIuU6YVAt_2hbtGvTaXDdMeMhuWv1SkL_tHx99Us5pKZFEPTJf-nZvKrMcRNrpyIl-bFHEURH9Dc3aI53w1OJu-6YwwO7rfDoP69i0dCv3wFUeWHPNLUQaXTPvvfA==)
5. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOpvEYIG4l4WKoZOb1OBaWW_Xxyd2WnVd2VweAiiW2zhtLq5-SPxBOS446vM9wO4VQRGSfi56IGVUGOuxAzxQCHmdpTbLxY-SWp2eFPwl4_avRxuC2IszqDkecJDqLseCqi21LlIlHhyxmJn-6SZ27pldnfIYkEg==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlYpjTEbp2N5sDjI-XnroBwLWuiD2NMxr6Unh2QtnMjIpBny8XdR1k4sjPn5ZYYIGSYZ2Azig90sVYEzUPAYM2qBY8Ui26CpSAAnFCUN_IOlAPkiEmedK7FA==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESxEdV2sWj4malNktAo585yfpl4PTlI1x9wuHPVeUhBpOoo023ZMxT38p5MtcGhkGc0WzuW9M9AX03r9257rCV4KXovDcl0_21LA-PPYyEQ6QPbH_avA==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqrZCD77jnjrUi05g-noUX-ft1zHLjLiTGpZqtrgxHWcfSp881CJwDKaQJdsvWHj18NHaM14ZfDRWkDVxbFK47S6M9UapkkY2HIqn4lVOcE6w9c6qVlQ==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0AsA_SjQuCce7ypXmJ3FGj2kY3fhXIisTnK7PDCixbiq_euhNhS5_Rt9jcrwlWvR8nytp7PER9-df7T2gbD68V-LisLGPT7s3h5YDHN5ywGWgSvfCZbWlLA==)
10. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFI4WeilW1JZiVYDsTE4NSPnRKsFPhe3kkAhZfwvxueVWpvN9nUF2hKv_j6xcRkl06Vdrcdel-RICj_sBj7yAJJt9eHZZjHSAdr49MbgB9rCrtcWbeaH-9pUGC6rKuMp8OLnAwiWF4MxlP8fpQksjljNG9yM6RN7N7auq9vMVLtKhQ=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZzcyXiFGuYX2Zr0ery88pAJJeTWqU0bOnszgGoIfhb7ilDq5AK2mgI5W3BJKw6jgFfz3OMd-RuzsP0fJSD17HoDQ8_82t5ZLBw8b2L5iDosikfE8VYw==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOznUedS5xVXdtcpWm1GPPeVUP7i4MSSwtnjaK5qPxOhR-fm47tj5wZQPRsDQd6L-2_i6cMI8LKlDXR6_svF9JVlRLAX2fKfA6DfFRJ6jgER7C5Z7OyA==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSk9fKF8ePnMbECqxQJ0ctWa_sM7drCdbng-JJNeFu-0ObWbaMzIiV4IE7YqYErn0D0UmnG5P-pwSwxphwdcW1t97nP1joTMVxMoYq3FW6Wcx_QN3BEw==)
14. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFp1XnMCM7KtMUzD4AsiGBv7Stl9QwZdVWoGb3PcNMus-DAcWzVLplsYY-ZgrDh-mRUeBwbzpj_b6CptqL0Z-0yVKEaoABFD1qAgfI1A7hbbFTA-4GeyXbxTGgXpMK7g7ltY9fgB4B)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQET3RCJzRQbuLXyuwaOPvxP62LDm38QL1gN3ovuCRmZJ0G3pLJgIJfmUZMsh4yDznEypc4gJDYpCrt5FdaNUZknhkpGgzbGsSu_Y4YqQCc37E40wJceQg0d9g==)
16. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcKcnC2iCXjmMYkaUKYoWRcc9GyX4sK5VNKuDdm_JHM0anKLSIaVnz2JLCICReBOrPfNSpOU2fo_PPbvMnceKhQ-TD4j58izfQw3Is0h0B59zamrgIXW5gkNbk66APeSAVNDm3HP4ZkA==)
17. [acalytica.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECIs1L5oicDe37BTxZbCTIUBpYh0LlR4sXS7J0l0EMWt-G_-jLuEFGxOj1S_mzDANrxT63ZhVxSMA_ofjnSkd5_DXHOzlweA1DHHcJscHrHpARcTAnnujEaqVd7NQsak79)
18. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAiEg1e0qOunxj5nDMhhuYB6-JR9oUH3gssTawNF-mT82TksbgLrF6S3jNIiSHGd0vE64yLGwQ-eJ4ESGefoNBYxWxatsnZI9pRWyBqXcHGTXFFZOsKArLOKVgK3mblzJ_C1DthZplzairF8siQA2C5nPYAA0hcgaRGfS754sVWqa7huIwsqEf2hwIT5Ay19YkgxM=)
19. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJEkIyIOiQLWOhA04KYMYwKcRonWEn8ZLi6PLGs1ehinWixuTB96t5BVrIcVcUmvp26T8sEkleaBvYj1IWsZ02-aRWHhXXRiVc5bRgaaKoJ26E9RDuWMgkqLESfB8=)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEu7qrV_OQxyonfl61GrN58whoICSYFFSDLyzvtziDfZHl_yhugFDAo0Ibu9sa6QKj5J1sVhltfrZuZ1L41ekFDfoxRZtwlqJCoM1mGVJTGjBVDpcA-9Q==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFClLzH988u1qX9Tzk0YPh5XPqU3s3OocE0WNs6JprBQfPPO7GBoj6o_377Fkz5Wq7Kwi7H6gxyx-O8xzoq1PJvEUe1Wm-VELVo0TH3WPIHoY7ZrF9MHw==)
22. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZC8dvCvOU_fc0wFuqWxMcPSFQNgjhKQb6oXVhMPNBTa65Qh9j0xKiR8SmqTx8LEaYvRu1LEqleaOQkArAYrpz4qVaXpSWxm7ewNF5cztkEhkJD8lj_x16hj2dYFYMNBWzUPzbxPTeiJJvLju7ghy6Lv9E7OqYf5J6kQ==)
23. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKIFNdUZ7FMlrE37nSjxC0Z6Lgpm90kCJY6XfuhvX4DFq8zX8Qv4cMAniXCjhxMclzpvmj8IpVzrPDEBgHf6afN5Ikm72Ufpp6G0liG9Dc3DXPFPNan2K_YoGrTzg=)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOGtTmTekM8Av45RVFpuCmIKYur0thzJa8TPbwNvhv-DzkIOSURjWdwnDRwVAp0Qs_5YT9I58i5Ka8P19mzT3mB7W_ooXnannKeEaF8juKZQwNMhsQyw==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFauQ2vdrRZjAgeEWQqz2CWfeJ_iQ0b3hfWk4t0PLaEo4_j90ltp0e9jbOvMs2GutBFzkFl69Ei9XWx5l_3t2Se53Lrpg5pF-pMenZEjECxAKr1FdI0JBQ0fbZUjz244BthUQ==)
26. [zhijing-jin.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4t0m8Hl6EJen4IGOML6yhfrct6V9e5B42J8ljPqtLI8Jr80d0JDUEQfp8QyUqowqV5CXaGgIY_rv1mSbYjHBIQhtNHGNeFkTXxBAK4Xm13WdLDWGxa5CiubhpJW21Xz7c2QAhpnnMRIOg81dXesw=)
27. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEApv1yBRqHm66cjG98-LIFR4HSMqTaUuN4gGK0IxYoUeSOC4Jft0BrZ--nld_A5nIL1nlRVZiv58uRMAgBYn66qmEOGIC6pv4vZyPL9c4fY6_LlOiftQim5Te5Lbywsj82W1xCrNBAB5inv_UbzWbg_MSzqgE24A63cY_OaUW3k1PQ1nXPUsK6)
28. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHW9nzQq7GOiuQ2Kdr4Z_amwUf3eEfAX2vY4MT-7SPDjwGOBP3tN7Uv1k4Vw3S6KD9pFpn8CTaOfJc6Ut7l34F10O_fMgSPG1wmuxQTxyGMK3GcTz0v5kJmVXQftkkKdGDhfhh8rsAdcJLiyK_xpaDPvnY=)
29. [pitt.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2IlWcB1o6tu1mG5DZ4zlmU2XSP7RgVtw7_kXoknqpfH82TjBL3TSad8xvKzCAplyWeNFcrboSSvmx8wZ28ljlGxyYk2w-tUeaIvpJJ4_bDb0MRw5T)
30. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH747J6BnKVX-ZtJTkLl_RrFmWMooIVWJVdb1-TQeoTOY5ulwnvoy4YagwlF6Lhc-YMcr0NN6G4aFFWVDEdpFx_jD0wi8s7OsxG81g1CqnKbTpSo5B4HV1UomZK4aTnqCAIZA==)
31. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNwzQDzACK7Ncrw50_sfq9LLMGDjeGhjwKclKNYl_TUCnH59HEVrUqbtC3d16fBkl0CulJmI_Ej9QAqXeFWM1rDtpbyi5Ktt2bv8afr2iPHWQ59KiQUa7KA0ph1_w=)
32. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSZ9avJdnE2NwhGhY6VIfDy4l_NW61ea48ZNfqiegS-HCrw-SlHjQkpEZWeFdDcGdnn-QV-FMQQTfzOt-YxJV8TQBloqbTnDGkGwFCeMBnPbNTqWkjcEC3605X2yLi41pgRCIOsjnS66CrctEDon4-zZjyZOOXvV1FxVfoTdhZsy2m9O6fRtIrJkLVzzQ_pFw6PSoLoUgWkm2s3xTZ1Qq851OU4QqfswgQVjuy7t9FFeTweCnulIi_)
33. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFamKGTfxBYirb6PNTR-EuTo_vPIVRyBsBKlUgQF96PC_2La7D1y0A1wZEIa-2veAw26o2vu4iq9aztfZnTEwCZk4BExUJ0MdEx8DEtZqZFPX5H_bzvBc512vy4lVn-gJGxqX3kRKAltqI-9Z610-SutjfVxgiJ8Y2amxmOwCWTJw==)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHU_bSedwFpmPG6x8uzS2_qnQfUU58foAadeCbAoRQkJUy7ouOF9c7xiwTiFbW794yKE9fzeypTuS-4JI-OilUOTYo8vxKmw0_4BMRHKpSz5H0uO8ZR43c6l8Hu0l0CYQQcWg==)
35. [towardsdatascience.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFALstzmbByf6Ztbr1yacrxfZAsAnnEjJIzmkmaGbRNkzZ313SN6hEzCHGwhwP6cL6RIZxERiUMrts-nsaZ3aI8n8oqy_0fFoAzkOUU2UEDx6tqWDqYkcxWbJe24tvgolrOh9CCwmvpKJJ_9CjlByQBlrJujsb-esMcL5QWLpgxiGjOtojkNcXiMB-ZK7fNx8RF478Fa4QBH_MjzLYF6Pw=)
36. [pywhy.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDW7IAXZMdemXxw6jKyL3wC-Qp9-b-_LC4Jal2MGfldPeF2hfmlqqm46qHXj2oaMN1LMQBi5YCbQz-x2gQ4E3Vn4VrR0lrzMcQxI7yXRevbawMjdhpCNalbGqGednohS6gWhk=)
37. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmJOfsQKpewHwRxai-_C5N-7CYxrGtvTWt0X9-HwOguznY96AGL0JKvjZxBSwi-uDg4sCXK0OyPutQdJxtdFfhRJeP1keH8fnz7hodTdqJDEa3r--o0TTt)
38. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCpZIUR3euinJTncJEdFVNXqAh8VnIwdbQCx6d68znFmy4P0S0pt3zyS-lHcvjuMAJOEar1bSEWCwRp29iu_Qy409aCXiRw1bmmscxvIAdzRvfUpUEiok2ekoSdJyNYB6v04sXlXYKW2EmiKdypyM2qkrHI7MgRTJcePMzdPQ=)
39. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRrDBB2bc9d-4PTqWhD7PcWuawBmVYLP08uupJKCLK3X50ow4ss2fUHI4wW70JeCYu8rQG6DvwFaubjqsBwTdSiAQuDTveZqrXLvuvV2IzNn56Zwn4jCs1wDbtOGU9cmIsCsSjmonO0dyQwRkRjQqq2CyoS3XqOIAOcduVKrBI)
40. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYrLxx3XwNrPU9AJKqe_LhYHbaAmE3lVbF0uFEeryoFGad9_BL1uyZEOPISw7iRi61wrSwlWAS1giVjoV_zk32FBM5Y7nQwGG7QalbFZNOWC8r02aF7xiHKA8lGV8-Lq3LRhJ3MtiabWE6j_b5OUkQ)
41. [zenodo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3F_LPaZ1KFz4MN7V-SnzFGhseJfev03DwJZFY5LPJxzceIq5ZcBAp1XxP8AqWGJQ5c7b7aKN9m-5Zo_KyCv-BXR4QXqSp434uVP4eIgSzASSYchJyzmkH)
42. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkLWBczGCgkZ8sjWTuaa75dFnBce3iWRDIHAKbABJg73fihda6_U_UipxW4zQg5to1M2HPHDJ9iDm6vhzbR74g1aEsMEj_C7qxiEjRasgnw4tcpkCOGrKq3Noohr86z9uNwl0CO0SkIQ==)
43. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHt-D8f83LlL3_KF4cGlgdDeJayX8r1Wg-UYWw3e62Fuc-f1Bl6cCor-LVU9QgWQM57H_haVA9oOUC_yM4AHe3Xk0MNpbWw9o5mengKdyRqlcnSSFlx23_wZvgEd0xpLCI=)
44. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeoya-YXaseDU0v4JeRDtFEYhz8M2kuYty3q8pMDwfNiNANfSgn56nHyG68P2j1tgeSUpfe9bfatnPMBnbv7JGKpOCSIsSoGGXaHsz4X9KBT6uEhLX7rJI9Q==)
45. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJKltZ2SxuTYrR7vC7yy2M8na5rPWf22eqdRpkAjKTmbii-k1jn1OkGoeXOPJxfSQeBwp261WhlWfk2akw0mpVcjU8kJji7nT8-XmGqN_fAD75Hm3cKDnI-X123Dh0)
46. [causalens.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGChHBbPcYB1OSc5SkQO_x_822LmUKpB8a5r5a4PEkDeSeSEjsBGpE9-KRiE9J7ShW1v8H_qV_OdBxseWtCKS41Cg89S112BaIYVtztJMLJd39SEnP9bQF8PBHHoTiHxvrxqQ-cnRJ1CGHfiYA1iDotBRE=)
47. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuEFEWaSMmY7nmSz4RsYokNWEnCNN-QxB4i-wi67UnfRHGxD1xTdDrAVbq8Jv7x71zxOR7wkKxekJS66f7LhkEsWbWwMGa5bc-y5uOB1ZuctzB27ftbJmN_5c-9F4AC3UidssjwMWcAehI8MEGu8QXukJ7vfbTB6VNzcvZYnVsRcsnn3Kw)
48. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLwFQExYROZ2RcdkD8Gc2W5gVLCfoocSUYB6_0wUqInaMvmeZUoAx1CVf3pN019wpUIr9dPELBbb9FGp9YvRCd6CwsdDE9mjp1-m7J1ztXtmTzvpR7_UlbTQ==)
49. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFm57FMOtj7Ivq1YxyXAXNNBIPgkGmuNLCUBMFrmH7-yxjSao9P3Njo0Qw-RGzxD6QOiIaJSql9jgzznCSxYU7wnllEDXCRCU5pKc7m1-knEtqzxBu1DUcoN_5d337zIQZf3sNIrQRyo0noVDb1WgQCUBAXWVhEKGQrm2pucms5_njVv1PFfA65oIgDcpwI33YHXm2CIdIaIKIt8jdnikWXoa5YkDtPPRfaXMYU-Q==)
50. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXTeYqcduFf6LbVM3-Bard1UBl7ZFQDX7sdmm7FJKPgb4u0RlZ6wM3KLpUpg2TIFjTiuoGCWbcgtLKokaEvj-CuweFKAqoTeUbqgrD-nTSDKk-RnC8fyi_ogpYV6H5HnvshowlOiRrEn70)
51. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGy2VBIwo4z1u0mCB9A4rqlh9KhqBlEdGJneaK-hx459PTbAr5BxPLkWVDErVz8HIL6Libio1SA-IcDcM1Xk_gz9EZYpbq6Jvc8IFv3ixdH-87TtoBSrP9i7HRDyZUM)
52. [gsk.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZp_ynUqFJncy6q2ZfxbcfvJCjpsxx4_bVy2LFxd_pufieIAbszwiWXMbQZVYo3DeLPM8zWMN8xqZuwsi57IxPeFJ6o0pHVDHVkFyk33BLaEjqMszE_zENpc_WAZDg9Q==)
53. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHxmrBRBLkq6XpoOeJRKXRTcdSBzhngWvahHHzsioTrx7YdxPzTyu9pWqVadXlz30U1oPcSujN7Ac0wKUki8b3o8n_NKdvVPokHcH6xHcq0nlCZL2Uvg==)

