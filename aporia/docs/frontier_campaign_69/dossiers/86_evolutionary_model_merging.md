# Prompt 86: Evolutionary Model Merging

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdFcnFmYXJ6cUFmWGpfdU1QLV9IZ3dRYxIXRXJxZmFyenFBZlhqX3VNUC1fSGd3UWM
**Elapsed:** 334s

---

# FRONTIER PRACTITIONER DOSSIER: Evolutionary Model Merging

Research in evolutionary model merging has rapidly shifted from manual, intuition-driven heuristics to automated, gradient-free optimization of parameter and data flow spaces. While the core premise remains robust, recent large-scale evaluations have overturned several early assumptions regarding task interference and the efficacy of advanced merging techniques on large language models. The field currently operates at the intersection of automated machine learning, singular vector decomposition, and generative hyperparameter search.

The evidence suggests that while basic model merging is a proven, computationally cheap alternative to multi-task fine-tuning, its more complex "interference-resolving" variants do not reliably generalize across heterogeneous modern LLMs. Furthermore, the sheer computational cost of evolutionary evaluation has pushed the frontier toward surrogate benchmarks and structural matrix operations over flat vector arithmetic. An entrant to this field in 2026 must navigate a landscape rich in empirical tools but rife with fragile assumptions and non-reproducible performance claims.

## PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Evolutionary model merging is the automated, gradient-free search for optimal combinations of weights and layer structures from multiple models that share a common pre-trained base. Your current understanding of the mechanism is fundamentally correct but slightly outdated in its unquestioned acceptance of advanced interference-resolution techniques. You correctly identify that Task Arithmetic creates task vectors by subtracting base weights from fine-tuned weights, and that early methods like TIES and DARE trim small components and resolve sign conflicts. You also correctly identify that the evolutionary version, pioneered by Sakana AI, uses population methods like Covariance Matrix Adaptation Evolution Strategy to search continuous merge coefficients in Parameter Space and discrete layer permutations in Data Flow Space.

However, a correction is necessary regarding the claim that later methods successfully "resolve interference" for modern large language models. This is currently the most contested issue in the field. 

What is SETTLED:
Linear Mode Connectivity holds for models fine-tuned from a shared base, meaning they exist in a connected loss basin and their weights can be combined arithmetically without destroying the underlying capabilities cite: 22. Evolutionary search over these combinations consistently finds non-intuitive, high-performing configurations that outperform simple averaging cite: 11, 13. Furthermore, merging is strictly cheaper than joint multi-task training, making it an essential tool for specialized capability integration.

What is CONTESTED:
The efficacy of interference-aware methods on large language models is highly contested. While TIES and DARE showed strong results on smaller models and classifiers, comprehensive systematic evaluations in late 2025 demonstrated that these subspace and interference-aware methods often result in significant performance drops when applied to heterogeneous LLM fine-tunes cite: 31. This 2025 evaluation argued that the oldest and simplest method, Task Arithmetic, is the only approach that reliably yields constructive interference on large LLMs. Additionally, the assumption that merging treats models as flat vectors is contested by researchers advocating for layer-level Task Singular Vectors, who argue that flat arithmetic destroys crucial structural matrix information cite: 30, 47. 

What is OPEN:
The evaluation bottleneck is the primary open problem. Evolutionary search requires evaluating hundreds of candidate models, which is computationally prohibitive at the 7B to 70B parameter scale. The frontier is currently focused on surrogate benchmarks that predict merged model performance without running full inference cite: 27, 49, and generative evolutionary merging that learns structured proposal distributions rather than relying on random Gaussian perturbations cite: 5. 

If the field has been absorbed, it is slowly being integrated into the broader Automated Machine Learning pipeline as a post-training optimization step, but it retains a distinct identity due to its strict gradient-free constraints and reliance on open-source model ecosystems.

## PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Ilharco, G., Ribeiro, M. T., Wortsman, M., Schmidt, L., Hajishirzi, H., and Farhadi, A.
2023
Editing models with task arithmetic
The Eleventh International Conference on Learning Representations
arXiv:2212.04089
This is the bedrock paper establishing that weight differences between pre-trained and fine-tuned models can be treated as task vectors and manipulated via simple arithmetic. A practitioner must know this because it defines the baseline mathematical operation that all subsequent parameter-space merging methods rely on.

Yadav, P., Tam, D., Choshen, L., Raffel, C., and Bansal, M.
2024
TIES-Merging: Resolving interference when merging models
Advances in Neural Information Processing Systems 36
arXiv:2306.01708
Introduces the concept of parameter interference and proposes resolving sign conflicts and dropping redundant parameters before merging. It is essential reading because its specific heuristic became the default starting point for most 2024-era model merging software, including MergeKit.

Yu, L., Yu, B., Yu, H., Huang, F., and Li, Y.
2024
Language models are super mario: Absorbing abilities from homologous models as a free lunch
Forty-first International Conference on Machine Learning
arXiv:2311.03099
Proposes DARE, a technique to randomly drop a large fraction of task-specific parameters and rescale the remainder, showing that LLMs have highly redundant delta parameters. You must know DARE because it is frequently paired with TIES in evolutionary search spaces to aggressively sparsify candidates.

Akiba, T., Shing, M., Tang, Y., Sun, Q., and Ha, D.
2024
Evolutionary Optimization of Model Merging Recipes
Nature Machine Intelligence
arXiv:2403.13187
This is the originating paper for the evolutionary approach, introducing simultaneous search in both Parameter Space and Data Flow Space. It is the exact anchor for your experimental programme, providing the blueprint for using the Covariance Matrix Adaptation Evolution Strategy to orchestrate model merging without gradients cite: 11, 14.

CURRENT FRONTIER SOURCES

Gargiulo, A. A., Crisostomi, D., Bucarelli, M. S., Scardapane, S., Silvestri, F., and Rodolà, E.
2025
Task Singular Vectors: Reducing Task Interference in Model Merging
Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition
arXiv:2412.00081
Critiques flat-vector Task Arithmetic by demonstrating that layer task matrices are low-rank and should be manipulated via Singular Value Decomposition. Introduces TSV-Merge to explicitly decorrelate singular vectors. You must read this because it represents the shift from naive vector arithmetic to structure-aware matrix operations cite: 30, 44.

He, Y., Zeng, S., Hu, Y., Yang, R., Zhang, T., and Zhao, H.
2025
MergeBench: A comprehensive evaluation suite designed to assess model merging at scale
Preprint
arXiv:2505.10833
The authoritative benchmarking paper that standardizes evaluation across 2B to 9B LLMs over five domains. It is critical because it empirically proves that merging performs better on larger base models and highlights the severe limitations of in-domain performance compared to true multi-task training cite: 58, 61.

Akizuki, S., et al.
2025
SMM-Bench: Surrogate Benchmarks for Model Merging Optimization
AutoML-N 25
arXiv:2509.02555
Addresses the compute bottleneck of evolutionary search by providing a surrogate benchmark that predicts merged model performance using regression. A serious computational scientist needs this to test new optimization algorithms locally without burning thousands of GPU hours on actual LLM inference cite: 27, 49.

Systematic Evaluation Authors (Anonymous/Preprint)
2025
Systematic Evaluation of Merging Methods on LLMs
Preprint
arXiv:2511.21437
A massive empirical takedown of recent merging literature, showing that interference-aware methods like TIES and subspace methods fail on heterogeneous LLMs, and only simple Task Arithmetic consistently achieves constructive interference. This is mandatory reading to prevent you from wasting time tuning broken heuristics cite: 31.

Wang, et al.
2026
Evolutionary Generative Merging
Preprint
arXiv:2605.29295
Introduces EvoGM, which replaces random evolutionary mutations with a learnable generative model to propose merge coefficients. This sits at the absolute frontier of 2026, shifting the field from random search to structured generative optimization cite: 5.

## PART 3. SOFTWARE I CAN ACTUALLY RUN

MergeKit
https://github.com/arcee-ai/mergekit
Python
MIT
2026
MAINTAINED
This is the absolute community standard that everyone actually uses. It implements Task Arithmetic, TIES, DARE, and Frankenstein layer-stacking for almost all modern LLM architectures. It includes a specific script called mergekit-evolve which implements the Sakana AI evolutionary search over parameter spaces using Covariance Matrix Adaptation Evolution Strategy and the EleutherAI evaluation harness cite: 16, 39.
Gotchas: It writes intermediate models to disk during evolutionary search, which will silently destroy your storage I/O and fill your hard drive if you do not aggressively manage the cache. Furthermore, its memory requirements can spike unpredictably depending on the lazy loading of tensors across multiple source models.

SakanaAI Evolutionary Model Merge
https://github.com/SakanaAI/evolutionary-model-merge
Python
Apache 2.0
2024
DORMANT
This is the reference implementation from the originating authors of the evolutionary approach. It specifically contains the recipes used to create their famous Japanese Math LLM, operating on Mistral-7B. It allows exact reproduction of their Data Flow Space and Parameter Space searches cite: 6.
Gotchas: The repository has seen little update since the original paper publication. It relies heavily on a specific older version of fasttext for language identification and expects specific prompt formats that may require manual patching for newer LLMs. It is better treated as reference code than a production library.

SMM-Bench
https://github.com/shiralab/SMM-Bench
Python
MIT
2025
MAINTAINED
The reference implementation for the Surrogate Model Merging Benchmark. It allows you to simulate evolutionary optimization trajectories for both Parameter Space and Data Flow Space merging using pre-computed LightGBM regression models trained on tens of thousands of actual LLM evaluations cite: 26, 49.
Gotchas: Because it is a surrogate, optimizing perfectly against this software will eventually hit the limits of the regression model's accuracy. It simulates the optimization process flawlessly but cannot discover emergent capabilities outside its training distribution.

Task Singular Vectors (TSV)
https://github.com/AntoAndGar/task_singular_vectors
Python
MIT
2025
MAINTAINED
The canonical implementation for singular value decomposition-based model merging. It compresses task vectors to 10 percent of their size while explicitly computing and reducing interference between singular vectors across tasks cite: 30, 44.
Gotchas: Applying full Singular Value Decomposition to every layer of a 70B parameter model is massively memory and compute-intensive. You will likely need to write custom chunking or offloading logic if your compute cluster is not heavily provisioned with high-VRAM GPUs.

## PART 4. DATA AND BENCHMARKS

MergeBench
https://yifei-he.github.io/mergebench/
Size: Varies by task subset (covers 5 key domains)
Licence: MIT / Open Access
The authoritative benchmark suite of 2025 for assessing model merging at scale. It standardizes fine-tuning and evaluation protocols across instruction following, mathematics, multilingual understanding, coding, and safety. You should use this to measure multi-task performance, forgetting, and runtime efficiency cite: 58, 61.
Contamination Note: Because it relies heavily on standard public subsets, standard LLM contamination protocols apply.

SMM-Bench-PS and SMM-Bench-DFS Datasets
https://github.com/shiralab/SMM-Bench
Size: 40,913 data points of hyperparameter-to-performance pairs.
Licence: MIT
A precomputed dataset mapping merge coefficients to actual LLM evaluation scores. It uses Japanese mathematics as the anchor task. Used strictly to train surrogate evaluators or to test optimization algorithms (like Covariance Matrix Adaptation Evolution Strategy vs Differential Evolution) without running actual LLMs cite: 27, 49.

MGSM (Multilingual Grade School Math) - Japanese Test Set
https://huggingface.co/datasets/juletxara/mgsm
Size: 250 test examples (subset of GSM8K)
Licence: MIT
This is the specific dataset used by Sakana AI as the fitness function for evolving their Japanese Math LLM. It tests whether a model can perform arithmetic reasoning in a non-English language cite: 35.
Saturation Note: With only 250 examples, an evolutionary search can rapidly overfit to this specific validation set. If you use it for the fitness function, you must evaluate the final merged model on a completely held-out set to prove generalization.

Open LLM Leaderboard
https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard
Size: Continuous aggregator
Licence: Open
Merely popular, not authoritative for rigorous science. While early model merging research heavily targeted this leaderboard, it is widely considered saturated and contaminated by the community. Do not use this as your primary scientific metric; use it only to contextualize your model against the public ecosystem cite: 35, 37.

## PART 5. THE REPRODUCTION RECIPE

The most informative and reproducible experiment is the Parameter Space evolutionary merge of a Japanese Math LLM as defined by Sakana AI, because it perfectly isolates the evolutionary coefficient search over a shared base.

Software and Version:
Clone the SakanaAI/evolutionary-model-merge repository at its March 2024 release state. Install Python 3.10.12 and CUDA 12.3. Alternatively, you can use MergeKit (version 0.4.x) utilizing the mergekit-evolve script cite: 6, 39.

Base Model:
Mistral-7B-v0.1

Source Models:
1. shisa-gamma-7b-v1 (Japanese fine-tune)
2. WizardMath-7B-V1.1 (Math fine-tune)
3. Abel-7B-002 (Math fine-tune)

Dataset:
MGSM Japanese test set (mgsm-ja), consisting of exactly 250 problems.
You must download the fasttext lid.176.ftz model for language detection evaluation as required by the Sakana repository cite: 6.

Parameters:
Merge Method: DARE-TIES (Parameter Space).
Layer Granularity: 1 (meaning coefficients are optimized per layer, per model).
Evolutionary Algorithm: CMA-ES.
Population Size: Defaults to standard CMA-ES heuristics based on dimensionality, typically configured around 16 to 32 for local cluster experiments.
Generations: 100 to 200.
Objective Metric: Exact match accuracy on mgsm-ja.

Replicates and Seeding:
Run 3 independent evolutionary replicates with fixed random seeds for the CMA-ES initialization.

Compute Cost:
Depending on your hardware, running inference on 250 MGSM examples for 32 population members across 150 generations requires approximately 1.2 million forward passes of a 7B model. Expect this to take 200 to 300 GPU hours on A100 or H100 hardware if unoptimized, though caching and surrogate approaches can reduce this.

Expected Result:
The evolved model should achieve a state-of-the-art score on the mgsm-ja test set, surpassing the individual capabilities of shisa-gamma (good at Japanese, poor at math) and WizardMath (good at math, poor at Japanese), achieving an accuracy near or above 50 to 55 percent, as published in the original Sakana AI Nature Machine Intelligence paper cite: 14, 38.

The Three Most Common Ways People Get This Wrong:
1. Tokenizer Discrepancies: Attempting to merge models that, despite sharing a base, have had their tokenizer vocabularies extended differently by their fine-tuners. If the embedding matrices are mismatched, the arithmetic produces garbage. You must transplant or align tokenizers first (often using tools like mergekit-tokensurgeon) cite: 20.
2. I/O Bottlenecking: Running standard evolutionary merge scripts writes every generated candidate checkpoint to disk before passing it to the evaluation harness. This will throttle your experiment to a halt and destroy SSDs.
3. Validation Overfitting: Using the exact same 250 MGSM questions as both the CMA-ES fitness function and the final evaluation metric. The resulting capability is often an averaging artifact overfit to the prompt style rather than true bilingual arithmetic reasoning.

## PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you intend to run frontier evolutionary merging experiments natively, you will quickly find that no off-the-shelf tool provides an Ephemeral In-Memory Evaluation Engine for CMA-ES.

The Gap:
Currently, frameworks like MergeKit decouple the merge step from the evaluation step. The orchestrator generates a configuration, the framework physically writes a 15GB safetensors checkpoint to disk, the evaluation harness loads it into VRAM, runs the dataset, unloads it, and deletes the file cite: 39. This latency makes large-population evolutionary search computationally excruciating.

The Interface to Build:
You must write a PyTorch-native evaluator that keeps the base model weights permanently pinned in GPU memory.
What goes in: A population vector of continuous merge coefficients (e.g., from an optimizer like Optuna or CMA-ES).
What happens inside: The engine performs the DARE-TIES or TSV-Merge arithmetic on the fly, applying the resulting task vector as a rank-1 or transient update to the base model weights directly in VRAM. It then immediately runs batched inference over the validation set.
What comes out: A vector of fitness scores.
The Hard Part: Managing VRAM fragmentation and handling Data Flow Space (layer shuffling) dynamically. For DFS, you must write a custom dynamic routing wrapper around the Transformer blocks that changes the execution graph per forward pass without recompiling the model.
Work Estimate: This is roughly two to four weeks of deep systems-level PyTorch engineering for a competent computational scientist.

The Signal:
Several private labs have quietly rebuilt this exact pipeline because the standard HF-Transformers approach is too rigid for population-based dynamic architecture routing. The existence of SMM-Bench cite: 26 (a surrogate benchmark) is direct proof that the community is desperate to avoid the I/O and compute overhead of the standard evaluation loop.

## PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The literature around model merging is plagued by early optimism based on small models that failed to replicate at scale. This section highlights the critical methodological flaws and retracted assumptions in the field.

The Failure of Subspace Methods on Large Models
In 2023 and 2024, the field accepted that naive Task Arithmetic caused parameter interference, which was solved by techniques like TIES (resolving sign conflicts) and DARE (sparsification) cite: 22, 48, 26. However, a massive late 2025 systematic evaluation tested these exact methods across multiple modern LLMs (Llama-3, Gemma) and 16 standardized benchmarks cite: 31. The results were devastating: interference-aware and subspace merging methods frequently resulted in significant performance drops compared to the base models. The study concluded that only the oldest and simplest method, Task Arithmetic, reliably yields performance gains on LLMs. The claim that TIES and DARE universally solve interference failed to replicate under heterogeneous LLM fine-tuning conditions.

The Flat Vector Critique
A standing methodological critique of the entire field, led by researchers like Gargiulo et al. (2025), is that treating neural networks as high-dimensional flat vectors fundamentally ignores structural matrix information. By flattening weights, traditional methods use coarse-grained metrics like cosine similarity to assess interference. When Gargiulo applied Singular Value Decomposition to layer matrices (TSV-Merge), they found that tasks interfere along specific singular vectors cite: 30, 44. Traditional methods were effectively destroying orthogonal capabilities by averaging them. This critique has been answered by the adoption of SVD-based merging, though its compute cost remains prohibitive for massive models.

The Over-Saturation Phenomenon
It was heavily hypothesized that merging more models strictly improves performance, akin to a "Model Soup." The Model Stock paper (2024) demonstrated that this is empirically false. As the number of merged models increases, performance gains saturate quickly and often decline. The authors proved that you only need a very small number of strategically selected fine-tuned models anchored to a pre-trained base to approximate the center of the loss basin cite: 21, 24. Programmes attempting to merge hundreds of models simultaneously have largely failed.

The Averaging Artefact Critique
A standing critique from rigorous evaluators (e.g., MergeBench) is that "constructive interference" is often just an averaging artefact. Averaging models often serves as a powerful regularizer, pushing weights back toward the robust pre-trained base, which artificially inflates scores on generalized benchmarks. When tested on strict, narrow in-domain tasks, merged models almost always underperform true multi-task training cite: 58. The gain is often just the erasure of fine-tuning degradation (forgetting) rather than the true synthesis of new capabilities. This critique remains largely unanswered by the pro-merging camp.

## PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the failures of massive flat-vector scaling and the compute bottlenecks of evolutionary search, a well-resourced entrant with coding capabilities should aim at the following specific experiments.

1. In-Memory Singular Vector Evolutionary Search (Highest Priority)
What it is: Combine the TSV-Merge (Task Singular Vectors) methodology with CMA-ES. Instead of evolving flat continuous scalars for entire layers, evolve the selection and decorrelation coefficients of the top 3 percent of singular vectors per layer.
Why it is feasible now: The mathematical groundwork for TSV was laid in early 2025 cite: 30, but it has not been orchestrated via evolutionary search because of compute constraints. If you build the ephemeral in-memory evaluation engine detailed in Part 6, you can execute this.
What it would measure: Whether targeting specific structural subspaces for mutation prevents the capability degradation seen in standard parameter-space merging.
Falsification: If the evolved TSV model fails to beat a simple Task Arithmetic baseline on a held-out multi-task suite, it proves that structural interference resolution is an artefact of small-scale testing and does not survive evolutionary pressure.

2. Temporal Evolutionary Merging (TIME-Evolve)
What it is: Run an evolutionary model merge sequentially rather than simultaneously. Integrate new expert models one by one into an expanding base, evolving the initialization and deployment strategy at each step.
Why it is feasible now: The design space for temporal merging was formalized in late 2025 / early 2026 cite: 25, showing that initialization strategies dominate single-step weight merging.
What it would measure: Whether an evolutionary algorithm can maintain a model's stability over time without suffering from catastrophic forgetting, simulating a continuous learning pipeline.
Falsification: If the final model's performance on the first incorporated task drops below 80 percent of its original capability after 10 sequential merges, temporal evolutionary merging is falsified as a viable continual learning strategy.

3. Generative Surrogate-Assisted Optimization
What it is: Implement EvoGM cite: 5 (Evolutionary Generative Merging), but tightly couple it with the SMM-Bench surrogate models cite: 49. Train a lightweight generative model to propose Data Flow Space layer routings based entirely on surrogate regression scores, only validating the absolute best candidates through actual LLM inference.
Why it is feasible now: The datasets (40,000 hyperparameter pairs) and surrogate baselines were published in late 2025.
What it would measure: The degree to which a generative model can out-predict random Gaussian mutation in a highly non-convex search space.
Falsification: If the generative pipeline requires more actual LLM evaluation steps to reach a target accuracy threshold than standard CMA-ES, the generative overhead is fundamentally not worth the engineering cost.

What will NOT work:
Do not attempt to scale standard DARE-TIES parameter space evolutionary merging to large configurations (e.g., trying to merge 20 different Llama-3-70B experts using CMA-ES). It will fail. The loss landscape for that many experts is entirely saturated cite: 4, 21, the computational cost will exceed your budget before the algorithm converges, and current evidence strongly indicates that interference-aware methods degrade at that scale anyway cite: 31. The frontier is found in structural precision (matrices over vectors) and search efficiency, not brute-force scale.
