# Prompt 92: Curriculum Learning and Task Ordering

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdjNzJmYW9QZ1BJdmhfdU1QOGJqXzhBcxIXYzcyZmFvUGdQSXZoX3VNUDhial84QXM
**Elapsed:** 395s

---

# FRONTIER PRACTITIONER DOSSIER
Field: Curriculum Learning and Task Ordering

WHO IS ASKING AND WHY

This report is formulated for a computational scientist with high engineering competency but limited domain-specific tacit knowledge, preparing to execute frontier experiments in curriculum learning and task ordering as of mid 2026. 

Key findings for this field currently indicate:
*   Curriculum learning is not a universally applicable accelerant; its effectiveness is highly conditional on the dataset's noise profile, the model scale, and the learning budget.
*   The frontier has shifted dramatically away from static easy-to-hard image classification tasks toward dynamic data mixing for large language model pretraining and prompt-level curricula for reinforcement learning post-training.
*   The historical assumption that "hard" examples should be prioritized (active learning) or "easy" examples should be prioritized (standard curriculum) has been superseded by methods targeting the "learnable but not yet learned" frontier, calculated via reducible holdout loss.
*   Methodological critiques remain severe, with multiple high-profile methods recently shown to fail at transferability or to perform no better than random shuffling when data is abundant and clean.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Curriculum learning in 2026 is fundamentally bifurcated. The original formulation asked whether ordering fixed training examples from easy to hard, measured by some heuristic or model-based difficulty proxy, accelerates convergence or improves generalization compared to random shuffling (cite: 32). In traditional domains such as supervised image classification, the field has largely matured into a niche regularization technique for noisy data. However, the paradigm has experienced a massive resurgence and transformation in the context of Large Language Models and Reinforcement Learning. The frontier now revolves around dynamic data mixing algorithms, such as DoReMi and Skill-It, which continuously adjust the sampling probabilities of data domains or "skills" based on real-time model loss, and Prompt Curriculum Learning, which sequences reasoning tasks during the reinforcement learning post-training of models. 

What is SETTLED: It is settled that for supervised learning on clean, abundant data with overparameterized models, standard fixed-schedule curriculum learning provides negligible benefits over uniform random shuffling, and can even degrade performance by inducing early overfitting to simple examples (cite: 2, 5, 45). However, it is equally settled that in the presence of severe label noise or highly constrained compute budgets, curriculum learning and its advanced variants reliably outperform random baselines by preventing the model from fitting irreducible noise. It is also theoretically settled that for certain classes of problems, such as learning k-parities, a curriculum of specific product distributions mathematically reduces the sample complexity compared to learning under a uniform distribution (cite: 60). 

What is CONTESTED: The primary live disagreement in 2026 centers on the transferability and scalability of data-mixing curricula for LLM pretraining. One side, championed by the original authors of DoReMi, argues that optimal domain weights (the curriculum mixture) can be discovered by training a small proxy model using distributionally robust optimization, and that these weights successfully transfer to much larger models (cite: 41). The opposing side, supported by recent empirical ablation studies, argues that domain weights are highly sensitive to the specific tokenizer, model architecture, and scale, demonstrating that proxy-derived weights often fail to outperform heuristic baselines when transferred to frontier-scale models (cite: 40). A secondary contestation exists around whether language models learn skills in a strictly compositional, interdependent order (the Implicit Curriculum Hypothesis) or if this behavior is merely an artifact of the data distribution (cite: 35). 

What is OPEN: The field lacks a computationally frictionless method for calculating real-time, per-instance difficulty at the scale of tens of billions of tokens. Current methods require either multiple training passes, expensive reference models, or proxy models that do not perfectly align with the target architecture. The frontier of research is focused on zero-overhead automated curriculum learning, transfer-aware dynamic curriculum sampling for multi-step reasoning tasks, and reinforcement learning pipelines that autonomously route prompts from easy to hard based on the policy's evolving capability without requiring costly rollouts. 

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Yoshua Bengio, Jerome Louradour, Ronan Collobert, Jason Weston
Year: 2009
Title: Curriculum Learning
Venue: International Conference on Machine Learning
Identifier: DOI 10.1145/1553374.1553380
This is the genesis paper that formalized the concept of curriculum learning in machine learning, proposing that training on examples in an easy-to-hard order acts as a continuation method to find better local minima. A practitioner must read this to understand the original hypotheses and the fundamental baseline against which all modern methods are compared (cite: 8).

Authors: M. Pawan Kumar, Benjamin Packer, Daphne Koller
Year: 2010
Title: Self-Paced Learning for Latent Variable Models
Venue: Advances in Neural Information Processing Systems
Identifier: IDENTIFIER UNKNOWN
This paper introduced Self-Paced Learning, shifting the curriculum design from a manual, predefined schedule to an automated, dynamic process where the model itself determines example difficulty based on its current loss. It is critical because it introduces the self-paced regularizer, forming the mathematical basis for modern automated task ordering (cite: 20).

Authors: Petru Soviany, Radu Tudor Ionescu, Paolo Rota, Nicu Sebe
Year: 2022
Title: Curriculum Learning: A Survey
Venue: International Journal of Computer Vision
Identifier: arXiv:2101.10382
This is the single best comprehensive survey of the field prior to the LLM explosion, categorizing approaches into data-level, model-level, and task-level curricula. It serves as the definitive reference for historical difficulty measures and pacing functions (cite: 33).

CURRENT SOURCES (2023 - 2026)

Authors: Soren Mindermann, Muhammed Razzak, Winnie Xu, Andreas Kirsch, Mrinank Sharma, Adrien Morisot, Aidan N. Gomez, Sebastian Farquhar, Jan Brauner, Yarin Gal
Year: 2022
Title: Prioritized training on points that are learnable, worth learning, and not yet learnt
Venue: International Conference on Machine Learning
Identifier: arXiv:2107.02565
This paper introduced Reducible Holdout Loss Selection. It is mandatory reading because it explicitly refutes the binary "easy versus hard" debate by proving mathematically and empirically that you should prioritize data with high reducible loss, thereby ignoring both trivial data and noisy, unlearnable data (cite: 66).

Authors: Sang Michael Xie, Hieu Pham, Xuanyi Dong, Nan Du, Hanxiao Liu, Yifeng Lu, Percy Liang, Quoc V. Le, Tengyu Ma, Adams Wei Yu
Year: 2023
Title: DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining
Venue: Advances in Neural Information Processing Systems
Identifier: arXiv:2305.10429
DoReMi represents the frontier of domain-level curriculum learning for LLMs, using Group Distributionally Robust Optimization on a proxy model to determine domain mixture weights. It is essential for understanding how the field moved from instance-level sorting to domain-level continuous mixing (cite: 41).

Authors: Mayee F. Chen, Nicholas Roberts, Kush Bhatia, Jue Wang, Ce Zhang, Frederic Sala, Christopher Re
Year: 2023
Title: Skill-it! A Data-Driven Skills Framework for Understanding and Training Language Models
Venue: Advances in Neural Information Processing Systems
Identifier: arXiv:2307.14430
This paper shifts the difficulty paradigm from static heuristics to a dependency graph of skills. By demonstrating that models learn more efficiently when prerequisite skills are sampled before advanced skills, it defines the current frontier of skill-based task ordering (cite: 35).

Authors: Elisabetta Cornacchia, Elchanan Mossel
Year: 2023
Title: A Mathematical Model for Curriculum Learning for Parities
Venue: International Conference on Machine Learning
Identifier: arXiv:2301.13833
One of the rare purely theoretical justifications for curriculum learning, proving that for learning k-parities, a curriculum of product distributions significantly reduces computational cost. A computational scientist must know this to understand the mathematical bounds of when a curriculum is provably beneficial (cite: 63).

Authors: Zikeng Zhou, et al. (THUMNLab)
Year: 2024
Title: CurBench: A Curriculum Learning Benchmark
Venue: International Conference on Machine Learning
Identifier: arXiv:2405.00000 (approximate, IDENTIFIER UNKNOWN)
This introduces the first unified benchmarking suite for curriculum learning across vision, text, and graph modalities. It is crucial because it standardizes the evaluation of 15 core curriculum methods, providing the baseline metrics a practitioner must beat (cite: 72).

Authors: Shubham Parashar, et al.
Year: 2025
Title: Curriculum Reinforcement Learning from Easy to Hard Tasks Improves LLM Reasoning
Venue: arXiv
Identifier: arXiv:2506.06632
Defining the 2025-2026 frontier in post-training, this paper introduces the E2H Reasoner. It demonstrates that while vanilla RL struggles on inherently difficult reasoning tasks, a curriculum scheduling tasks from easy to hard establishes convergence guarantees and requires fewer total samples (cite: 46).

Authors: Zhaolin Gao, Joongwon Kim, Wen Sun, Thorsten Joachims, Sid Wang, Richard Yuanzhe Pang, Liang Tan
Year: 2025
Title: Prompt Curriculum Learning for Efficient LLM Post-Training
Venue: arXiv
Identifier: arXiv:2510.01135
This paper introduces a lightweight RL algorithm that selects intermediate-difficulty prompts using a concurrently updated value model. It highlights the current frontier of avoiding costly rollouts while dynamically sizing prompt difficulty during model alignment (cite: 49).

PART 3. SOFTWARE I CAN ACTUALLY RUN

Name: CurBench
URL: https://github.com/THUMNLab/CurBench
Language: Python, PyTorch
Licence: MIT
Activity: 2024
Verdict: MAINTAINED
CurBench is the community standard evaluation harness for comparing curriculum learning algorithms. Today, you can run comparative experiments across 15 different curriculum learning methods on datasets like CIFAR-10, CIFAR-100, Tiny-ImageNet, and GLUE text classification tasks, testing under standard, noisy, and imbalanced settings. Its main limitation is that it focuses on relatively small-scale supervised learning tasks and does not natively support distributed LLM pretraining or reinforcement learning workflows. It is the best starting point for a newcomer to reproduce legacy baselines (cite: 71).

Name: RHO-Loss
URL: https://github.com/OATML/RHO-Loss
Language: Python, PyTorch (Lightning)
Licence: MIT
Activity: 2022
Verdict: DORMANT
This is the reference implementation for Reducible Holdout Loss Selection. You can use it today to run data selection experiments on vision datasets and small BERT models. It successfully implements the holdout loss calculation using a smaller irreducible loss model. The primary gotcha is that it is tightly coupled to older versions of PyTorch Lightning and Hydra. While the conceptual framework is highly robust, the codebase requires modernization to run on 2026 LLM architectures, as it is not built for multi-node streaming datasets (cite: 67).

Name: Skill-It
URL: https://github.com/HazyResearch/skill-it
Language: Python, PyTorch
Licence: Apache 2.0
Activity: 2023
Verdict: DORMANT
This codebase allows you to construct a skills dependency graph and run the online data selection algorithm to dynamically sample training data based on prerequisite skills. You can run continual pre-training and fine-tuning experiments on datasets like Natural Instructions or RedPajama. The main limitation is that it requires your dataset to be explicitly partitioned into defined "skills" beforehand; if your data lacks metadata to define these skill slices, the algorithm cannot generate the dependency graph. It is highly educational but requires significant adaptation for unstructured web data (cite: 56).

Name: Procgen Curriculum Suite
URL: https://github.com/montrealrobotics/procgen-curriculum
Language: Python, C++
Licence: MIT
Activity: 2026
Verdict: MAINTAINED
This is a modern benchmark suite specifically designed for curriculum reinforcement learning. It extends the standard Procgen environments by assigning structured task spaces of varying dimensionality, allowing you to test automated curriculum algorithms against hand-specified, difficulty-ordered POMDPs. The gotcha is that it requires specific C++ and Qt5 compilation toolchains which can be difficult to configure outside of isolated Conda environments, but it remains the most authoritative testbed for RL curricula today (cite: 13).

Name: DoReMi (Reference Implementation)
URL: IDENTIFIER UNKNOWN
Language: Python
Licence: Apache 2.0
Activity: 2023
Verdict: ABANDONED
The original reference scripts used for the DoReMi paper were integrated into private Google/DeepMind frameworks. While various community reimplementations exist in open-source LLM training libraries, a standalone, authoritative DoReMi repository is effectively unavailable for direct push-button reproduction. Furthermore, published results regarding the transferability of DoReMi domain weights have failed to reproduce reliably when changing model architectures, meaning practitioners today usually have to rebuild the Group DRO proxy pipeline from scratch within their own training harness (cite: 40).

PART 4. DATA AND BENCHMARKS

Name: CurBench Dataset Collection
URL: https://github.com/THUMNLab/CurBench
Size: Varies (CIFAR, Tiny-ImageNet, GLUE, Graph datasets)
Licence: Various open-source
Used to measure: The baseline efficacy of curriculum learning algorithms under controlled conditions. The most critical aspect of this collection is the "Noise-0.4" setting, where 40 percent of labels are randomly corrupted. This is treated as an authoritative benchmark for evaluating whether a curriculum method successfully prevents a model from memorizing irreducible noise (cite: 70).

Name: Clothing-1M
URL: IDENTIFIER UNKNOWN
Size: 1 million images
Licence: Non-commercial research use
Used to measure: Performance on real-world, web-scraped noisy data. Unlike synthetic noise injected into CIFAR, Clothing-1M contains actual mislabeled data from the internet. It is heavily utilized by RHO-Loss and other data selection methods to prove that prioritizing learnable examples speeds up convergence and improves final accuracy by avoiding human-like label errors. Saturation is not yet a severe issue, but the dataset is limited to the vision domain (cite: 65).

Name: The Pile
URL: IDENTIFIER UNKNOWN
Size: 825 GB
Licence: MIT (with varied sub-licenses)
Used to measure: Domain reweighting and language model pretraining curricula. DoReMi and other data mixing algorithms use The Pile because it is strictly partitioned into 22 distinct domains (e.g., Wikipedia, ArXiv, GitHub). Contamination is a known issue, as many downstream benchmark tasks have leaked into The Pile's web-scraped components. However, it remains popular for measuring how dynamically shifting mixture proportions during training affects domain-specific perplexity (cite: 53).

Name: Natural Instructions (Super-NaturalInstructions)
URL: IDENTIFIER UNKNOWN
Size: 1600 plus NLP tasks
Licence: Apache 2.0
Used to measure: Skill acquisition and instruction tuning. In the Skill-It framework, task categories within this dataset are treated as distinct skills. It is used to measure cross-task generalization and whether learning a prerequisite task accelerates the learning of an advanced task. Overfitting is a known hazard if the curriculum scheduler collapses to a small subset of easy tasks (cite: 36).

Name: DeepScaleR and MATH Benchmarks
URL: IDENTIFIER UNKNOWN
Size: Tens of thousands of mathematical reasoning problems
Licence: MIT
Used to measure: The reasoning capabilities of LLMs post-trained via Reinforcement Learning. These are currently the authoritative benchmarks for Prompt Curriculum Learning and Easy-to-Hard Reasoner experiments. They measure whether a model can solve complex, multi-step proofs. A known limitation is that models can sometimes learn to game the specific formatting of the MATH benchmark without acquiring generalized mathematical reasoning (cite: 49).

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to run as a newcomer is the RHO-Loss evaluation on CIFAR-10 with synthetic label noise. This experiment cleanly isolates the fundamental mechanism of modern data selection: it proves that standard easy-to-hard curricula fail, active learning (hard mining) fails, and only selecting the "learnable but not yet learned" points succeeds.

Exact software and version: RHO-Loss reference implementation (commit hash unknown, circa 2022 release), Python 3.8, PyTorch 1.9.0, PyTorch Lightning.
Exact dataset: CIFAR-10, modified to include exactly 10 percent uniform symmetric label noise (labels randomly reassigned to one of the 10 classes with 0.1 probability).
Parameters to set:
*   Irreducible Loss (IL) Model: A small CNN with 256 hidden units.
*   Target Model: ResNet-18.
*   Batch size: 128.
*   Selection fraction: Top-k points selected from a larger randomly pre-sampled batch.
*   Holdout set size: 10,000 clean, accurately labeled images (this is critical; the holdout set must not contain noise).
Number of replicates: 3 independent replicates with fixed random seeds for weight initialization and noise generation.
Compute cost: Approximately 2 to 4 single-GPU (e.g., RTX 3090 or A100) hours.
Expected result: RHO-Loss should achieve a higher final test accuracy than uniform shuffling, and reach the baseline's maximum accuracy in significantly fewer steps. The specific published comparison shows RHO-Loss avoiding the memorization of the 10 percent noisy labels, leading to a generalization gap improvement of several percentage points over loss-based hard mining. Citation: Mindermann et al., 2022 (arXiv:2107.02565) (cite: 65).

Three most common ways this experiment is gotten wrong:
1. Contaminating the holdout set. The reducible holdout loss calculation relies on the holdout set being pristine. If the 10 percent label noise is accidentally applied to the holdout set as well as the training set, the algorithm will prioritize noise, and performance will collapse.
2. Using an irreducible loss model that is too capable. If the IL model perfectly overfits the noisy training data, it fails to provide a stable baseline of "what is inherently noisy," causing the reducible loss calculation to become meaningless.
3. Failing to re-evaluate the target loss continuously. The curriculum must be dynamic; a point that is "not yet learned" in epoch 1 becomes "already learned" in epoch 5. If the selection scores are cached and not updated, the model wastes compute on redundant points.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

To execute frontier experiments in 2026, a serious entrant must build a Distributed, Streaming Reducible Loss Scheduler for Transformer Pretraining. 

Off-the-shelf tools like CurBench and RHO-Loss operate on small, epoch-based datasets where it is feasible to run an evaluation pass over a subset of data to calculate scores before updating the model. For modern LLM pretraining, data is streamed once from cloud storage across thousands of GPUs, making multi-pass scoring impossible. 

Interface Requirements:
*   What goes in: A continuous stream of tokenized text batches, and periodic loss metrics from a concurrently training small proxy model (the Irreducible Loss model).
*   What comes out: A dynamically routed subset of batches to the main model, where the probability of a batch being yielded is proportional to its moving-average reducible loss.
*   The hard part: You cannot evaluate the target model's loss on a batch without doing a forward pass, which consumes compute. Therefore, the scheduler must use an asynchronous, highly optimized forward-only pass on a separate dedicated GPU node to calculate the target loss and proxy loss just-in-time, discarding batches that fall below the curriculum threshold before they hit the main training cluster.
*   Work estimate: 2 to 4 months of senior systems engineering, highly dependent on deep integration with frameworks like Megatron-LM or HuggingFace Accelerate. 

This exact component has been rebuilt privately by several frontier AI labs (as evidenced by papers describing bespoke dynamic data mixing pipelines) but does not exist in the open-source ecosystem as a reliable, plug-and-play middleware.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The field of curriculum learning is heavily burdened by negative results, replication failures, and standing critiques that heavily temper early enthusiasm.

Critique 1: The "Random Shuffling is All You Need" Baseline
The most standing methodological critique of the field is that curriculum learning often amounts to a highly complex way of achieving the same results as random shuffling. Simulation studies and large-scale empirical evaluations repeatedly show that for clean datasets and overparameterized models, curriculum learning is indistinguishable from random ordering. In 2026, Zhang et al. demonstrated that no fixed scheduling strategy consistently performs best across different reasoning tasks in LLMs, suggesting the effectiveness is fundamentally task-dependent rather than a universal property of learning (cite: 5). If a paper reports a curriculum learning improvement without stringently tuning the learning rate and batch size of the random-shuffle control, the critique stands that they are merely measuring an unoptimized baseline.

Critique 2: The Failure of Active Learning (Hard Negative Mining) in Noisy Environments
For years, the optimization literature argued that training should prioritize "hard" examples (those with the highest loss) to accelerate convergence. This programme failed in real-world environments because high loss is inextricably confounded with irreducible noise, mislabeling, and ambiguous edge cases. Prioritizing these points forces the model to overfit to garbage data, destroying generalization. This critique was definitively answered by the Reducible Holdout Loss framework, which mathematically separated "hard because it is unlearnable" from "hard because it is not yet learned" (cite: 66).

Critique 3: The Transferability Crisis in Data Mixing
The DoReMi algorithm proposed that domain weights optimized on a 280-million parameter proxy model could be transferred directly to an 8-billion parameter model, yielding massive speedups. However, subsequent independent researchers have documented severe limitations. Recent studies demonstrated that DoReMi's sampling weights do not transfer well across different model architectures or tokenizers. Using the exact published DoReMi domain weights on newer models has resulted in test perplexities worse than default heuristic weights. This standing critique indicates that proxy-based curriculum generation is highly brittle and often requires retraining the proxy for every new architectural iteration (cite: 40).

Critique 4: Implicit Curricula and Memorization
A long-standing critique in natural language processing is whether curricula actually teach "skills" or simply alter the unigram frequency distribution of the training data. Some methods that appeared strong were later shown to be measuring an artifact of the benchmark. For instance, when curriculum learning improves results on reading comprehension, critiques often show the curriculum simply biased the model toward specific lexical overlap patterns present in the test set, rather than inducing true compositional skill acquisition.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the current landscape, a well-resourced newcomer should bypass traditional supervised image curricula entirely and focus on dynamic data selection for LLM reasoning and post-training.

Rank 1: Dynamic Prompt Curriculum for Reinforcement Learning
Experiment: Implement a continuously updating value model that estimates the probability of the target policy successfully answering a reasoning prompt. Route prompts to the policy that have a success probability between 0.3 and 0.7 (intermediate difficulty). Compare this against a uniform random prompt baseline and an active-learning (hardest prompt) baseline on the MATH and DeepScaleR benchmarks.
Feasibility: Feasible now because of the maturation of open-source RLHF/PPO frameworks and the findings of Prompt Curriculum Learning (cite: 49). 
Measurement: Compute hours to reach a 50 percent pass-at-1 rate on the evaluation set. 
Falsification: The idea is falsified if the intermediate-difficulty curriculum requires more token generations to reach the target metric than random sampling.

Rank 2: Zero-Overhead Reducible Loss Pretraining via Proxy Delta
Experiment: Instead of running a forward pass on the main 70B model to calculate reducible loss, use the loss delta between two small proxy models (e.g., a 1B model trained for 10,000 steps and a 1B model trained for 50,000 steps) to estimate which data domains contain the highest density of learnable information. Dynamically adjust the data mixture of the 70B model based on this delta.
Feasibility: Feasible now due to abundant compute to run continuous small-scale proxy trainings in parallel with the main run.
Measurement: Held-out perplexity across diverse domains (The Pile) at fixed FLOP intervals.
Falsification: Falsified if the 70B model's perplexity does not improve faster than a model trained on a static, heuristically defined data mixture.

Rank 3: Skill Dependency Graphing for Synthetic Data Generation
Experiment: Use an LLM to generate synthetic reasoning traces. Partition these traces by the specific logical rules required to solve them. Train a small target model on the synthetic data, strictly enforcing the prerequisite order dictated by the Skill-It framework (cite: 37).
Feasibility: Feasible now due to the low cost of generating massive synthetic reasoning datasets via models like GPT-4 or DeepSeek.
Measurement: Final zero-shot accuracy on out-of-domain reasoning tasks.
Falsification: Falsified if reversing the curriculum (training on complex synthetic traces first, simple ones last) yields identical final accuracy, indicating the model learns purely from exposure rather than compositional sequence.

What will NOT work:
Attempting to map DoReMi domain weights generated from an old proxy model (like a BERT or early LLaMA variant) directly onto a 2026 frontier architecture. The empirical evidence strongly suggests this will fail because data difficulty and domain relevance are intrinsically tied to the specific inductive biases, tokenizer vocabulary, and scale of the target model (cite: 40). The curriculum is relative to the student; an absolute curriculum derived from a different student will simply behave as suboptimal random noise.
