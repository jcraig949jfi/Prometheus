# Prompt 94: In-Context Learning

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdjNzJmYXRmMU81eXdfUFVQMkx5WHVBSRIXYzcyZmF0ZjFPNXl3X1BVUDJMeVh1QUk
**Elapsed:** 396s

---

FRONTIER PRACTITIONER DOSSIER
Field: In-Context Learning

Research into In-Context Learning represents one of the most mechanically fascinating and theoretically contested frontiers in modern computational science. The evidence leans toward a complex, scale-dependent reality where language models dynamically transition between retrieving pre-trained priors and actively learning new task mappings within their forward pass. 

Regarding your anchor description, your summary is highly accurate up to roughly the end of 2023, but it requires two explicit corrections based on recent findings. First, the theoretical claim that transformers implement gradient descent is an expressivity proof, meaning they possess the capacity to do so. However, empirical models often do not behave like pure gradient descent in practice; gradient descent is fundamentally invariant to the order of training examples, whereas empirical in-context learning is notoriously order-sensitive. Second, the observation that random labels barely degrade performance was recently challenged by the 2026 discovery of "set-level fixation." When demonstrations carry homogeneous labels or completely varied nonsense tokens, models often bind their output exclusively to the demonstrated token inventory, collapsing accuracy on novel queries to near zero. This reveals that the model is performing constrained vocabulary retrieval rather than simply falling back on semantic priors. 

What follows is an exhaustive, strictly formatted practitioner dossier designed to bootstrap an in-silico experimental research programme in this field.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

In-Context Learning is the study of how autoregressive models adapt their predictive distributions based on prompt demonstrations at inference time, without any parameter updates. Operationally, the field seeks to explain how the concatenation of independent examples induces a transient, localized task adaptation that mimics traditional supervised fine-tuning. The field operates at the intersection of behavioral benchmarking, where input distributions are systematically perturbed, and mechanistic interpretability, where the internal activations of the model are traced and causally patched to locate the circuits responsible for this adaptation.

What is SETTLED: The effectiveness of in-context learning is heavily dependent on the format of the prompt and the distribution of the input text. Small language models, generally those under 10 billion parameters, operate almost entirely on a "task recognition" basis; they rely on semantic priors established during pre-training and largely ignore the specific input-label mappings provided in the context. Theoretically, it is settled that the transformer architecture is expressive enough to implement algorithms like gradient descent and ridge regression within its linear attention layers. 

What is CONTESTED: The exact mathematical mechanism utilized by trained models on natural language tasks remains heavily debated. While the "mesa-optimization" camp argues that the forward pass implicitly executes gradient descent over the in-context examples, critics point to the severe order-sensitivity of language models, a trait fundamentally incompatible with standard gradient descent. Furthermore, the exact role of the labels is contested. The initial consensus that ground-truth labels are unnecessary has fractured; researchers are divided on whether large models genuinely learn novel relationships from context or merely use the labels to restrict their output vocabulary to a localized subset.

What is OPEN: The mechanistic localization of in-context learning failures is the current frontier. In 2026, the field is actively investigating "contextual evidence shift", a phenomenon where mathematically correct demonstrations actively degrade performance because they alter the distribution of evidence the model uses for inference. Similarly, the exact layer-wise transition dynamics from task recognition to task learning as models scale from 7B to 70B parameters remains an open architectural mapping problem. In the last three years, the field has aggressively transitioned from treating models as black boxes that either learn or do not learn, to probing them as white boxes containing specific, dissociable circuits for format adoption, semantic override, and vocabulary retrieval.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Min, S., Lyu, X., Holtzman, A., Artetxe, M., Lewis, M., Hajishirzi, H., Zettlemoyer, L.
Year: 2022
Title: Rethinking the Role of Demonstrations: What Makes In-Context Learning Work?
Venue: EMNLP
Identifier: arXiv:2202.12837
This is the foundational paper demonstrating that replacing ground-truth labels with random labels barely degrades performance on many classification tasks. A practitioner must know this because it established the "task recognition" hypothesis, arguing that the label space, input distribution, and overall format are the true drivers of in-context learning (cite: 26, 28).

Authors: Garg, S., Tsipras, D., Liang, P., Valiant, G.
Year: 2022
Title: What Can Transformers Learn In-Context? A Case Study of Simple Function Classes
Venue: NeurIPS
Identifier: arXiv:2208.01066
This paper isolates in-context learning from pre-training biases by training transformers from scratch on synthetic function classes like linear regression. It is crucial because it provides the mathematical baseline proving transformers can learn unseen functions in-context with performance matching the optimal least squares estimator (cite: 37, 71, 75).

Authors: von Oswald, J., Niklasson, E., Randazzo, E., Sacramento, J., Mordvintsev, A., Zhmoginov, A., Vladymyrov, M.
Year: 2023
Title: Transformers learn in-context by gradient descent
Venue: ICML
Identifier: arXiv:2212.07677
This paper formalized the "mesa-optimization" hypothesis by providing a weight construction showing that a single linear self-attention layer is mathematically equivalent to one step of gradient descent on a regression loss. It anchors the learning account of your query (cite: 12, 13, 76).

Authors: Wei, J., Wei, J., Tay, Y., Tran, D., Webson, A., Lu, Y., Chen, X., Liu, H., Huang, D.
Year: 2023
Title: Larger language models do in-context learning differently
Venue: arXiv
Identifier: arXiv:2303.03846
This paper overturned the absolute consensus of Min 2022 by showing that the ability to learn from flipped or semantically unrelated labels is an emergent property of scale. It is required reading because it defines the current understanding that small models recognize, while large models learn (cite: 31, 32, 63).

CURRENT FRONTIER SOURCES

Authors: Kossen, J., Gal, Y., Rainforth, T.
Year: 2024
Title: In-Context Learning Learns Label Relationships but Is Not Conventional Learning
Venue: ICLR
Identifier: arXiv:2307.12375
This work provides a highly rigorous probabilistic study of in-context learning dynamics as the number of examples increases. It establishes the modern middle ground: models do depend on in-context labels and can learn novel tasks, but they heavily preferentially weight information closer to the query and struggle to overcome pre-training priors (cite: 22, 54, 55).

Authors: Lin, X., et al.
Year: 2024
Title: Dual Operating Modes of In-Context Learning
Venue: arXiv
Identifier: arXiv:2402.18819
Introduces a probabilistic model explaining how in-context learning operates simultaneously as task learning and task retrieval. It is vital for its explanation of the "early ascent" phenomenon, where risk initially increases with a few examples due to incorrect skill retrieval before decreasing as task learning takes over (cite: 1).

Authors: Qiu, C., Peng, C., Yang, Y., Huang, K., Zhou, Y.
Year: 2026
Title: When Correct Demonstrations Hurt: Rethinking the Role of Exemplars in In-Context Learning
Venue: arXiv
Identifier: arXiv:2605.26350
This paper completely dismantles the assumption that exemplar correctness guarantees utility. By introducing task-preserving perturbations, the authors demonstrate that perfectly correct demonstrations can catastrophically degrade performance through "contextual evidence shift" (cite: 30, 47, 59).

Authors: Liu, M., Peng, C., et al.
Year: 2026
Title: In-Context Fixation: When Demonstrated Labels Override Semantics in Few-Shot Classification
Venue: arXiv
Identifier: arXiv:2605.08295
The most critical recent paper addressing your anchor method. It proves that providing homogeneous or varied nonsense labels triggers "set-level fixation", collapsing model accuracy to near zero on novel queries. The authors localized this fixation to a specific layer-7-centered circuit in 1B-scale models, proving that in-context learning acts as constrained vocabulary retrieval (cite: 2, 5, 83).

PART 3. SOFTWARE I CAN ACTUALLY RUN

Name: lm-evaluation-harness
URL: https://github.com/EleutherAI/lm-evaluation-harness
Language: Python
Licence: MIT
Year: 2026
Verdict: MAINTAINED
This is the community standard evaluation harness used to run zero-shot and few-shot in-context learning experiments across over 200 standard academic benchmarks. Today, you can use it to replicate the exact label-randomization experiments across open-source models like Llama-3 and Pythia. Its main limitation is that it focuses purely on behavioral benchmarking (inputs and outputs) and does not natively support the extraction or patching of internal activations required for mechanistic interpretability research (cite: 16, 17, 18).

Name: MetaICL
URL: https://github.com/facebookresearch/MetaICL
Language: Python
Licence: MIT
Year: 2023
Verdict: DORMANT
This is the reference implementation from the authors of the foundational Min 2022 paper on rethinking demonstrations. It allows you to run experiments modifying ground-truth labels to random labels. However, it is largely dormant, and its canonical implementation relies on older transformer versions and data loading paradigms that may require careful environment pinning (Python 3.8, datasets 1.4.0) to build on modern toolchains. Practitioners today generally port the logic from this repository into customized scripts built on top of modern HuggingFace libraries (cite: 41, 42, 43).

Name: transformers-learn-in-context-by-gradient-descent
URL: https://github.com/transformerGD/transformers-learn-in-context-by-gradient-descent
Language: Python
Licence: Apache 2.0
Year: 2023
Verdict: DORMANT
This repository contains the notebooks and reference implementations for the Von Oswald 2023 paper demonstrating that transformers can perform gradient descent. You can use it to train linear self-attention layers on synthetic regression tasks to observe mesa-optimization. The gotcha is that it is highly specialized for synthetic continuous mathematical functions and does not easily scale to testing large, pre-trained natural language models without extensive modification (cite: 11, 51, 76).

Name: Task-Preserving-ICL
URL: https://github.com/Chenghao-Qiu/Task-Preserving-ICL
Language: Python
Licence: MIT
Year: 2026
Verdict: MAINTAINED
This is the reference implementation for the 2026 finding on contextual evidence shift. You can run experiments applying task-preserving perturbations across sentiment classification and logical reasoning tasks. It provides the most modern pipeline for testing the correctness-utility gap in frontier models, though you must supply your own API keys or local compute to host the larger evaluated models (cite: 30, 46, 47).

PART 4. DATA AND BENCHMARKS

Name: CROSSFIT and UNIFIEDQA
URL: HuggingFace Datasets (crossfit, unifiedqa)
Size: Hundreds of diverse NLP tasks, millions of instances.
Licence: Various (Open for research)
These task collections are treated as authoritative for broad generalization testing. They were heavily utilized in the foundational MetaICL work to demonstrate that models could perform in-context learning on unseen tasks. They are heavily saturated for modern models, and contamination is a known issue since many tasks inevitably leaked into the pre-training mixtures of models released after 2022 (cite: 43).

Name: Synthetic Linear and Boolean Function Generators
URL: Generated dynamically in-memory (no static download)
Size: Infinite
Licence: N/A
Used to measure the pure mathematical learning capabilities of transformers (testing the gradient descent and algorithm selection hypotheses). Because the data is generated via random isotropic Gaussians or Boolean logic gates at runtime, it guarantees zero pre-training contamination. It is the authoritative benchmark for mechanistic theories of learning, though critics note that solving these does not generalize perfectly to explaining natural language capabilities (cite: 37, 75).

Name: Semantically-Unrelated Label ICL (SUL-ICL) Tasks
URL: Constructed programmatically from base datasets like SST-2
Size: Varies based on base dataset
Licence: MIT / Open
Used to measure a model's ability to override semantic priors. By replacing standard labels like positive and negative with arbitrary tokens like foo and bar, researchers isolate task learning from task recognition. This is a popular diagnostic tool, but models are known to occasionally solve it by leaning on formatting heuristics rather than true mapping comprehension (cite: 31, 32).

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to distinguish task learning from task recognition is the "Flipped Label" scaling experiment from Wei et al. 2023 (cite: 31, 32). This experiment cleanly isolates the point at which a model stops relying on pre-trained semantic priors and begins actively utilizing the input-label mappings provided in the context window.

Exact Software and Version: lm-evaluation-harness (v0.4.0 or newer).
Exact Dataset: SST-2 (Sentiment classification) loaded via the HuggingFace datasets library.
Parameters to Set: 
The target models: Pythia-1B (representing small scale) and Llama-3-70B-Instruct (representing frontier scale).
The few-shot counts (k): 0, 4, 8, 16, 32.
The label mapping: Override the default prompt template to deterministically flip the targets. Map the ground-truth positive class to the string "Negative" and the ground-truth negative class to the string "Positive".
Seeding Regime: 5 independent replicates using fixed random seeds (e.g., 42, 43, 44, 45, 46) to sample the in-context demonstrations, reporting the mean and variance.
Compute Cost: Approximately 15 to 20 GPU hours on a node with 4x A100 80GB GPUs to run the full sweep across both models and all seeds.

Expected Result:
For Pythia-1B, as the number of in-context examples (k) increases from 0 to 32, the accuracy on the flipped-label task should remain deeply impaired, hovering near 0 to 10 percent (or behaving randomly), because the small model relies on its semantic prior and ignores the contradictory in-context mapping. For Llama-3-70B, the accuracy should initially drop at low k, but as k reaches 16 and 32, the accuracy should steeply climb toward 80 to 90 percent, proving the large model has the capacity to override its prior and learn the new mapping purely from context. You are comparing against the theoretical curves established in Wei et al. (2023), specifically Figure 2 (cite: 31).

Common ways people get this wrong:
1. Using instruction-tuned models for the small baseline instead of base pre-trained models. Instruction tuning artificially inflates a model's adherence to its prior knowledge, skewing the comparison.
2. Failing to strictly control the prompt formatting. If the separator between the input and the flipped label changes from a newline to a space, models can fail to recognize the format, artificially suppressing the learning effect.
3. Evaluating on a dataset where the classes are heavily imbalanced, allowing the model to achieve high accuracy by simply collapsing to a majority class prediction regardless of the demonstrations.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you intend to run frontier experiments bridging behavioral observation and mechanistic interpretability, you will have to build a "Long-Context Distributed Activation Caching and Patching Harness." 

What goes in: A large language model distributed across multiple GPUs (e.g., a 70B parameter model utilizing tensor parallelism), a batch of 32-shot prompts, and a patching configuration specifying which attention heads or MLP layers to intervene on (e.g., swapping the activations of a specific token from a clean run to a corrupted run).
What comes out: The modified logits of the final query prediction, and a causal mediation score indicating how much of the performance gap was recovered by patching that specific circuit.
The hard part: Existing mechanistic interpretability libraries like TransformerLens are incredibly powerful but are generally memory-bound to single GPUs and optimized for small models (under 10B parameters) and short contexts. To run per-item paired activation patching on a 70B model with a 32-shot prompt, the intermediate activations will rapidly exceed VRAM limits.
The work required: You will need to write custom PyTorch forward hooks integrated directly into a distributed inference backend like vLLM or Megatron-LM to selectively cache and swap only the required activations at runtime, clearing computational graphs dynamically to prevent out-of-memory errors. Several top-tier alignment and interpretability groups have quietly built these distributed patching frameworks internally, as evidenced by recent publications executing circuit discovery on models up to 70B parameters, but no robust, off-the-shelf, open-source tool currently provides this specific interface for massive models.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The most prominent negative result in this field involves the original, highly influential claim by Min et al. (2022) that ground-truth labels barely matter for in-context learning. While the empirical observations in that paper were entirely correct for the models tested at the time, the theoretical conclusion failed to replicate as a generalized law. As shown by Wei et al. (2023) and Kossen et al. (2024), the inability to learn from labels was an artifact of using smaller, under-parameterized models. When scaled appropriately, language models absolutely do learn input-label mappings and suffer severe degradation if those mappings are randomized (cite: 26, 31, 54).

The "Transformers as Gradient Descent Optimizers" programme has faced heavy, standing methodological critiques. While the theoretical expressivity proofs by Von Oswald and Garg are mathematically sound, critics (e.g., Shen et al., 2023; GeTu peer reviews) have demonstrated that the implicit dynamics of empirical models diverge sharply from standard gradient descent. The primary standing critique is order-sensitivity. Gradient descent computes an update based on a batch of examples, a mathematically commutative operation that is completely invariant to the order of the data. In contrast, in-context learning is highly sensitive to the order of demonstrations; shuffling the examples can swing accuracy by over 30 percent (cite: 78). This critique has never been fully resolved by the mesa-optimization camp, leaving it highly contested whether empirical natural language models actually utilize the elegant gradient descent constructions found in isolated mathematical settings.

Another widely held intuition that recently failed is the assumption that providing correct, task-relevant demonstrations always improves or at least maintains performance. The programme of purely scaling up correct demonstrations hit a wall. Qiu et al. (2026) demonstrated that applying task-preserving perturbations to the inputs of correct exemplars can catastrophically degrade accuracy. This falsified the idea that models simply read the task mapping from correct examples, showing instead that models are highly sensitive to "contextual evidence shift," where the mere presence of out-of-distribution textual features in the context overrides the mathematical correctness of the mapping (cite: 47, 59).

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Experiment 1: Cross-Architectural Circuit Discovery for Set-Level Fixation (Rank 1)
Now that Liu et al. (2026) have identified that transformers suffer from set-level fixation (acting as constrained vocabulary retrievers driven by a layer-7-centered circuit in Pythia-1B) (cite: 83), a well-resourced entrant should execute a causal scrubbing experiment across fundamentally different architectures like State Space Models (Mamba) or Recurrent Neural Networks (RWKV). You would apply varied nonsense labels in a few-shot prompt and measure if these non-attention architectures also collapse into set-level fixation. This is feasible now because competitive open-source SSMs exist. It would measure whether vocabulary fixation is an artifact of softmax attention heads copying tokens, or a universal dynamic of autoregressive pre-training. If SSMs do not exhibit fixation and smoothly ignore the nonsense labels, it would falsify the idea that in-context learning universally degrades into vocabulary retrieval.

Experiment 2: Mechanistic Disentanglement of Contextual Evidence Shift (Rank 2)
Building on Qiu et al. (2026) (cite: 59), you should perform targeted activation patching to locate the exact layers where "contextual evidence shift" overrides exemplar correctness. You would run a clean prompt with standard correct exemplars and a corrupted prompt with task-preserving perturbed exemplars. By patching activations from the clean run into the corrupted run, you would isolate the specific semantic processing heads that misinterpret the perturbation. This is feasible now due to advancements in automated circuit discovery. It would measure exactly where the model's robustness fails. If patching the early representation layers fully recovers performance, it falsifies the idea that the model is failing at the later logic/mapping stages.

Experiment 3: Dynamic Order-Invariant Prompt Engineering via Reinforcement Learning (Rank 3)
What will NOT work: Attempting to solve the order-sensitivity problem of in-context learning by manually crafting prompt templates or separating examples with complex delimiter strings. This has been tried exhaustively since 2021 and routinely fails because order-sensitivity is an ingrained artifact of absolute and relative positional embeddings. Unless you are modifying the attention mechanism itself to be explicitly permutation invariant over the demonstration tokens, prompt-level hacks will just overfit to the evaluation baseline and fail to generalize.
