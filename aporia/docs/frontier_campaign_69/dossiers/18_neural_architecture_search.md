# Prompt 18: Neural Architecture Search

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcyNmllYXF6Z0g4RzdqckVQaXVIMHlBcxIXMjZpZWFxemdIOEc3anJFUGl1SDB5QXM
**Elapsed:** 425s

---

FRONTIER PRACTITIONER DOSSIER
Field: Neural Architecture Search

Key Points

Neural Architecture Search is undergoing a significant paradigm shift. The era of optimising small convolutional cells for image classification on standard hardware is effectively over. The current frontier involves Large Language Model guided search, hardware-architecture co-design for unconventional hardware, and automated discovery of foundation model routing or tokenisation strategies.

Random search with early stopping remains a formidable, load-bearing baseline. Many sophisticated algorithms published between 2017 and 2022 fail to reliably outperform random search when evaluated fairly across independent random seeds and matching computational budgets.

Tabular benchmarks such as the NAS-Bench series democratised reproducible search by replacing expensive network training with pre-computed table lookups. However, these benchmarks suffer from severe saturation and overfitting, as the field has collectively overtuned hyper-parameters to these specific, constrained spaces.

Weight-sharing one-shot methods, which train a single supernetwork to evaluate all architectures simultaneously, suffer from severe ranking correlation collapse. The performance of a subnetwork within the shared weights rarely correlates with its performance when trained in isolation from scratch.

Methodological Anchor and Current Context

The experimental mechanism you described remains the canonical method for evaluating search algorithms in this field. You correctly define the paradigm: pre-computing the exact validation and test accuracies of a constrained architecture space (like a cell graph) to create a tabular benchmark. By doing this, querying the objective function becomes a table lookup, allowing search algorithms such as random search or regularised evolution to be run thousands of times to rigorously measure their regret against a known global optimum.

Your description of regularised evolution is entirely accurate: it maintains a fixed-size population, samples a small tournament, mutates the winner, and replaces the oldest member of the population. This age-regularisation prevents early local optima from permanently dominating the population pool. Your understanding of what is judged (the best accuracy found within the budget) and measured (regret against the known optimum over many independent replicates) is spot on. 

What has changed is that while this methodology is the gold standard for measuring the search algorithms themselves, the search spaces they operate on (small cell graphs for CIFAR-10) are no longer at the frontier. The method is settled, but the objects of study have moved toward macro-architectures, hardware-aware constraints, and Large Language Model architectures.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Neural Architecture Search (NAS) in 2026 is a field that has largely absorbed the bitter lessons of empirical rigour and is currently transitioning into a sub-discipline of hardware-software co-design and foundation model engineering. Originally conceived as a way to automate the discovery of topologies that outperform human-designed convolutional networks, the field spent several years plagued by poor reproducibility, confounding hyper-parameters, and a failure to benchmark against simple baselines. The introduction of tabular benchmarks transformed the field into a rigorous mathematical study of discrete optimization, but the restricted spaces required to compute these tables meant the discovered architectures rarely generalised to frontier deep learning problems. Today, NAS has been partially absorbed into Automated Machine Learning (AutoML) and Systems AI. What was lost in this merge was the biological inspiration of evolving entirely novel, unbounded computational graphs from scratch.

What is SETTLED is the necessity of rigorous baselines and decoupled evaluation. It is now universally accepted that Random Search is a highly competitive baseline that must be included in any evaluation (cite: 76). It is also settled that the evaluation of the search phase must be statistically separated from the final model training pipeline, as advanced data augmentation and regularisation can mask a poor architecture. Tabular benchmarks are the settled standard for proving the mathematical superiority of a search algorithm.

What is CONTESTED is the validity of fast evaluation proxies. The field remains deeply divided over weight-sharing supernetworks. One side argues that weight-sharing is the only computationally tractable way to search macro-spaces without astronomical budgets. The opposing side, armed with standing empirical critiques (cite: 81), argues that weight-sharing induces co-adaptation, destroying the rank correlation between the proxy evaluation and the true stand-alone performance of the architecture. A newer, related disagreement surrounds Zero-Cost Proxies, which estimate network performance using initialisation statistics at initialization without training. While popular for speed, recent findings show they exhibit negative correlations with true accuracy when non-idealities or unconventional hardware constraints are introduced (cite: 26).

What is OPEN is Large Language Model guided NAS and unconventional hardware co-design. The frontier involves using LLMs not just as code generators, but as evolutionary operators (mutation and crossover) that can reason about macro-architecture text encodings (cite: 31). Furthermore, the application of NAS to optical computing, analog circuits, and other unconventional hardware platforms is a wide-open frontier, as these platforms introduce physical non-idealities that break traditional NAS assumptions (cite: 66).

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Real, E., Aggarwal, A., Huang, Y., and Le, Q. V.
2019
Regularized Evolution for Image Classifier Architecture Search
AAAI Conference on Artificial Intelligence
arXiv:1802.01548
This paper introduces the regularised evolution algorithm (AmoebaNet) and establishes the exact tournament selection with age-based death mechanism you anchored on. It is essential for understanding how simple evolutionary rules can match or beat complex Reinforcement Learning controllers.

Li, L. and Talwalkar, A.
2019
Random Search and Reproducibility for Neural Architecture Search
Uncertainty in Artificial Intelligence
arXiv:1902.07638
This is the single most load-bearing methodological critique in the field. It demonstrates that random search with early stopping is a formidable baseline, and exposes how many published NAS results relied on hyper-parameter tuning rather than architectural superiority.

Sciuto, C., Yu, K., Jaggi, M., Musat, C., and Salzmann, M.
2019
Evaluating the Search Phase of Neural Architecture Search
International Conference on Learning Representations
arXiv:1902.08142
This paper empirically dismantles the weight-sharing assumption. It proves that the ranking of architectures evaluated via a shared supernetwork does not correlate with their true ranking when trained from scratch, fundamentally challenging DARTS and ENAS.

Ying, C., Klein, A., Christiansen, E., Real, E., Murphy, K., and Hutter, F.
2019
NAS-Bench-101: Towards Reproducible Neural Architecture Search
International Conference on Machine Learning
arXiv:1902.09635
The introduction of the first tabular benchmark. The authors exhaustively trained and evaluated 423,624 unique convolutional architectures. This paper defines the exact in-silico experimental protocol you wish to run.

Dong, X. and Yang, Y.
2020
NAS-Bench-201: Extending the Scope of Reproducible Neural Architecture Search
International Conference on Learning Representations
arXiv:2001.00326
A critical evolution of the tabular benchmark. While smaller (15,625 architectures), it provides results across multiple datasets and standardises the node/edge operation space, making it the default testbed for modern search algorithms.

CURRENT SOURCES

White, C., Safari, M., Sukthanker, R., Ru, B., Elsken, T., Zela, A., Dey, D., and Hutter, F.
2023
Neural Architecture Search: Insights from 1000 Papers
arXiv
arXiv:2301.08727
This is the one best survey in the field. It provides a comprehensive taxonomy of search spaces, algorithms, speedup techniques, and benchmarks, capturing the transition of the field up to the era of LLMs.

Ji, Z., Zhu, G., Yuan, C., and Huang, Y.
2025
RZ-NAS: Enhancing LLM-guided Neural Architecture Search via Reflective Zero-Cost Strategy
International Conference on Machine Learning
arXiv:2509.26037
This defines the current software frontier. It demonstrates how to integrate Large Language Models as reflective mutation operators combined with training-free metrics to navigate massive search spaces without full network training.

King, T. and Leleu, T.
2026
LLM-Guided Neural Architecture Search for Robust Co-Design of Physical Neural Networks
arXiv
arXiv:2606.10294
This paper represents the hardware frontier, introducing Unconventional Hardware Neural Architecture Search (UH-NAS). It shows that traditional NAS zero-cost proxies fail under hardware noise and uses LLMs to co-optimize task accuracy against physical energy costs and analog non-idealities.

PART 3. SOFTWARE I CAN ACTUALLY RUN

NASLib
https://github.com/automl/NASLib
Python
Apache License 2.0
2026
MAINTAINED
This is the community standard framework for running NAS experiments. It provides unified, high-level abstractions for defining search spaces, optimisers, and evaluation pipelines. You can use it today to run regularised evolution or random search against NAS-Bench-101 and NAS-Bench-201 with only a few lines of code (cite: 59). A known limitation is that because it acts as a wrapper over many diverse benchmarks, debugging specific search space translation errors can be opaque.

Archai
https://github.com/microsoft/archai
Python
MIT License
2023
DORMANT
Developed by Microsoft Research, Archai was built to make NAS reproducible by standardising the training loops and hyper-parameter configurations (cite: 71). It is excellent for running Differentiable Architecture Search (DARTS) and Pareto-frontier searches. However, active development has slowed, and deploying it on the newest PyTorch 2.x releases may require dependency wrangling.

NASBench-PyTorch
https://github.com/romulus0914/NASBench-PyTorch
Python
Apache License 2.0
2021
DORMANT
The original NAS-Bench-101 API was written in TensorFlow 1.x and is notoriously difficult to build on modern toolchains. This repository is a PyTorch reimplementation that allows you to query the dataset and train specific graph hashes (cite: 89). Its limitation is that it does not generate the full search space from scratch, but rather acts as a bridge to train specific architectures found in the benchmark using PyTorch.

NAS-Bench-201 API
https://github.com/D-X-Y/NAS-Bench-201
Python
MIT License
2020
ABANDONED
This is the original API for NAS-Bench-201. It is explicitly marked abandoned by the author in favour of NATS-Bench (cite: 85). Practitioners should not use this repository directly, but instead download the underlying benchmark file and interface with it through NASLib or NATS-Bench, as the legacy code relies on outdated PyTorch paradigms.

LM-Searcher
https://github.com/Ashone3/LM-Searcher
Python
License Unknown (UNCONFIRMED)
2025
MAINTAINED
A modern tool for cross-domain NAS using Large Language Models (cite: 31). It allows you to run zero-shot inference for architecture optimization using numerical string representations. It is currently alive and actively tied to modern local LLM serving frameworks like vLLM, though it requires substantial local GPU memory to run the LLM inference step.

PART 4. DATA AND BENCHMARKS

NAS-Bench-101
Access route: https://github.com/google-research/nasbench
Size: 423,624 architectures (over 5 million trained models), approx 2GB to 3GB tabular data
Licence: Apache License 2.0
This is the authoritative foundational benchmark. It maps convolutional cell graphs (up to 9 nodes, 7 edges) to their validation and test accuracies on CIFAR-10 at multiple epoch budgets (cite: 91). Known saturation problem: the variance of the top 1 percent of architectures is so tight that differences are mostly statistical noise.

NAS-Bench-201 (now NATS-Bench)
Access route: Google Drive link maintained via NATS-Bench repository
Size: 15,625 architectures, 2.2GB tabular data
Licence: MIT License
Used to measure search algorithms across multiple datasets (CIFAR-10, CIFAR-100, ImageNet16-120). It defines a denser, more unified search space than 101. Known contamination issue: because it is so heavily used, many modern NAS algorithms have their hyper-parameters implicitly overtuned to perform well specifically on the structural quirks of these 15,625 cells (cite: 88).

NAS-Bench-360
Access route: https://arxiv.org/abs/2110.05668 (Data hosted externally)
Size: 10 diverse tasks, tabular records for 15,625 architectures on two tasks
Licence: UNCONFIRMED
Used to measure the generalisation of NAS algorithms to non-vision tasks (e.g., audio, genomics) (cite: 94). It directly addresses the overfitting problem of NAS-Bench-201 by forcing search algorithms to operate on modalities far outside their original design parameters.

PART 5. THE REPRODUCTION RECIPE

The most informative and reproducible experiment is comparing Regularized Evolution against Random Search on the NAS-Bench-101 tabular dataset, proving that evolution finds better architectures in the extreme low-budget regime, but random search is highly competitive globally.

Exact Software and Version:
Use Python 3.10 and install NASLib (automl/NASLib) at the current Develop branch (cite: 57). You will also need the downloaded NAS-Bench-101 tfrecord file, which NASLib can parse.

Exact Dataset:
NAS-Bench-101 (CIFAR-10 pre-computed tables).

Parameters to Set:
For Regularized Evolution:
Population size: 100
Tournament size: 10 (sampled uniformly from the population) (cite: 48)
Mutation regime: Uniformly pick one valid transformation (either flip a structural edge or change a node's operation among 3x3 conv, 1x1 conv, 3x3 max-pool).
For Random Search:
Sample architectures uniformly from the search space without replacement.
Budget: 
Restrict both algorithms to a strict budget of exactly 1,000 architecture queries.

Seeding Regime:
You must run exactly 500 independent replicates of both algorithms. Seed them sequentially from 1 to 500.

Approximate Compute Cost:
Because evaluating an architecture is simply reading a pre-computed JSON/dictionary value, the total compute cost for 500 replicates of 1,000 queries will take less than 1 CPU hour on a standard modern workstation. No GPUs are required.

Expected Result:
According to the original NAS-Bench-101 findings (Ying et al., 2019), both algorithms will rapidly climb the accuracy distribution. At a budget of 1,000 queries, Regularized Evolution will achieve a slightly higher mean validation accuracy and lower regret against the global optimum than Random Search, but the margins will be narrow. You should see test accuracies around 94.0 to 94.2 percent. 

Three Most Common Ways People Get This Wrong:
1. Confounding the query budget. Practitioners often allow evolutionary algorithms to query the table to evaluate the initial population for "free", or fail to count invalid mutated graphs against the total budget, giving evolution an unfair advantage over random search.
2. Inadequate replicates. The variance in NAS-Bench-101 is high. Running 5 or 10 random seeds will result in heavily skewed, statistically insignificant comparisons. Less than 100 replicates is invalid.
3. Reporting validation instead of test accuracy. The search algorithm must optimise over the validation accuracy, but the final reported metric for the run must be the test accuracy of the chosen architecture, retrieved only at the very end of the search.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to run frontier experiments in hardware-aware or LLM-guided NAS, you will discover a severe lack of modular bridging tools. You will have to build a Hardware-Agnostic Energy and Noise Simulator Interface.

What goes in: An arbitrary neural network architecture graph (e.g., an ONNX file or PyTorch module) and a hardware specification profile (e.g., analog optical mesh noise parameters, mixed-precision constraints).
What comes out: A zero-cost or few-shot estimation of both the inference energy cost and the expected accuracy degradation due to physical non-idealities.
What the hard part is: Traditional NAS evaluates clean floating-point graphs. To evaluate unconventional hardware, you must dynamically inject realistic noise distributions (like phase errors in optical computing) into the forward pass without requiring a full backpropagation training loop for every candidate.
How much work it is: Building a robust, vectorized noise-injection simulator that wraps PyTorch operations takes roughly three to six months of dedicated engineering by a competent computational scientist.

You will also have to build a Text-to-Architecture Graph Compiler. Existing LLM-to-NAS tools (like RZ-NAS or ONNX-Net) often rely on fragile string-parsing to convert an LLM's text output into a valid Directed Acyclic Graph (cite: 98). Several groups have rebuilt private regex-based parsers to translate LLM JSON responses into valid PyTorch computational graphs. You will need a robust compiler that takes raw token output, strictly verifies topological constraints, prunes invalid disconnected nodes, and returns a runnable metric or a rejection penalty to the LLM.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The most profound negative result in NAS is the collapse of the Weight Sharing Trap. Between 2018 and 2021, Differentiable Architecture Search (DARTS) and Efficient Neural Architecture Search (ENAS) dominated the field. These methods combine all candidate architectures into a single continuous supernetwork and train it via gradient descent. The critique, successfully argued by Sciuto et al. (cite: 81) and later corroborated by many others, is that the weight-sharing mechanism introduces catastrophic co-adaptation. The weights assigned to a specific convolution operator in the supernetwork are heavily influenced by the routing of the rest of the graph. Consequently, the correlation between an architecture's performance inside the supernetwork and its true performance when trained from scratch frequently drops to near zero. Methods that looked incredibly strong were shown to be measuring an artefact of the supernetwork's optimization dynamics, rather than discovering a genuinely superior architecture. While some methods attempted to patch this with uniform sampling during training, the critique stands largely unanswered for highly complex macro-spaces.

A second failed programme is the over-reliance on Zero-Cost Proxies under noise. Zero-cost proxies evaluate the Jacobians or activation overlap of an untrained network at initialization to predict its final trained accuracy. They were heralded as the solution to NAS's compute problem. However, recent findings in 2026, such as those from the UH-NAS framework, demonstrated that these proxies exhibit negative correlations with validation accuracy when deployed on unconventional hardware with physical non-idealities (cite: 26). The proxy measures theoretical expressivity, ignoring whether the architecture is robust to analog noise.

A standing methodological critique of the field is that NAS on CIFAR-10 and ImageNet cell-spaces is a solved and saturated problem. The differences between the architectures found by advanced Reinforcement Learning and Random Search are often statistically indistinguishable when trained with identical, modern data augmentation (Mixup, CutMix). The critique is that the field spent years overfitting to the benchmark rather than discovering new phenomena. This was answered by the creation of NAS-Bench-360 and the pivot to new modalities, but the historical literature remains heavily polluted by claims that failed to replicate under controlled hyper-parameter regimes.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the computational resources and coding capability you possess, you should entirely avoid cell-based image classification NAS. 

Rank 1: Co-Design of Tabular Foundation Models
Experiment: Apply LLM-guided NAS (using a framework like RZ-NAS) combined with evolutionary algorithms to discover architectures specifically designed for tabular data prediction, rather than vision or language.
Why it is feasible now: The recent emergence of tabular foundation models (like TabPFN) and text-based ONNX surrogate models allows for rapid evaluation.
What it would measure: Whether progressive filter-and-refine NAS can discover topological motifs (e.g., specific attention-routing or MLP structures) that consistently outperform gradient-boosted trees (XGBoost) across diverse tabular datasets.
Falsification: If the best architecture found by the LLM-guided NAS, when evaluated on held-out tabular datasets, cannot beat a well-tuned XGBoost baseline or random sampling from a constrained MLP space, the hypothesis that deep architectural complexity benefits tabular data is falsified.

Rank 2: Agentic Transfer Across Hardware Domains
Experiment: Replicate an LLM-guided evolutionary search across two wildly different hardware simulators (e.g., a standard GPU energy model and an analog optical mesh model).
Why it is feasible now: Tools like LM-Searcher and the conceptual framework of UH-NAS have proven that LLMs can digest hardware constraints via text prompts.
What it would measure: The capability of an LLM agent to maintain an archive of architectures and successfully transfer design intuition (motifs) from a high-precision digital environment to a noisy analog environment without retraining.
Falsification: If the LLM agent's proposed architectures achieve lower accuracy or worse Pareto energy fronts on the analog hardware than a naive random search conducted directly on that hardware, the idea of cross-domain agentic transfer is falsified.

What will NOT work:
Attempting to invent a new search algorithm (e.g., a novel gradient-based relaxation or a new swarm optimization variant) and benchmarking it on NAS-Bench-101 or NAS-Bench-201. This will not work because the search spaces are fundamentally saturated and the community no longer considers marginal improvements on these benchmarks as evidence of a method's superiority. The variation you measure will be pure statistical noise, and you will fall into the trap of tuning your hyper-parameters to beat the baseline artificially. The frontier has moved to new data modalities and hardware constraints; applying new math to the old benchmarks is a dead end.
