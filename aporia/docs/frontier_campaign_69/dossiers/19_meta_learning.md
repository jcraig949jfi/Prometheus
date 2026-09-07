# Prompt 19: Meta-Learning

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdqS3FlYXFmWk1vYTFfUFVQbVpfcWdBVRIXaktxZWFxZlpNb2ExX1BVUG1aX3FnQVU
**Elapsed:** 335s

---

FRONTIER PRACTITIONER DOSSIER
Field: Meta-Learning

Key Points
Research suggests that gradient-based episodic meta-learning, once the dominant paradigm, has largely been absorbed into the study of in-context learning within large foundation models.
The foundational premise of Model-Agnostic Meta-Learning (rapid parameter adaptation) was heavily challenged by findings demonstrating that feature reuse dominates the process.
Simple pre-training and fine-tuning baselines frequently match or exceed the performance of complex meta-learning algorithms when evaluated under rigorous, cross-domain conditions.
The current frontier focuses on applying meta-learning objectives to condition large language and protein models for zero-shot or few-shot in-context learning without test-time parameter updates.

Orientation and Methodological Correction
Your description of the target method, Model-Agnostic Meta-Learning, is mechanically accurate. You correctly identified the two nested loops: an inner loop that takes a few gradient steps on a support set to yield task-specific parameters, and an outer loop that differentiates the loss of those parameters on a query set with respect to the original initialization [cite: 1, 2]. You also correctly identified that this requires computing second-order derivatives, or a first-order approximation, to update the shared initialization [cite: 1, 3]. 

However, your understanding of the underlying mechanism requires a crucial correction based on established tacit knowledge. The original premise was indeed that the initialization is primed for "rapid learning," meaning the inner loop gradient steps dynamically rewire the network for the new task. This has been definitively proven false [cite: 4, 5]. The network does not rapidly learn new representations; rather, the outer loop learns highly robust, universally applicable representations, and the inner loop merely aligns the final linear classification head to the new task [cite: 5, 6]. This phenomenon is known as "feature reuse." Understanding this shift is critical because it fundamentally alters where a practitioner should spend compute: optimizing the feature extractor's pre-training is far more important than micro-optimizing the inner-loop adaptation dynamics.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

In 2026, the field of meta-learning is fundamentally bifurcated. The classical paradigm of episodic, gradient-based meta-learning on small convolution networks (the era of Model-Agnostic Meta-Learning and Prototypical Networks) has been largely absorbed into the broader study of parameter-efficient fine-tuning and representation learning. The specific problem of few-shot image classification on narrow benchmarks is dormant. In its place, the frontier of meta-learning has merged with the study of in-context learning in foundation models, particularly transformer architectures across modalities like text, proteins, and functional magnetic resonance imaging. Today, meta-learning is primarily used as an outer-loop training objective to teach large sequence models how to dynamically adapt to new tasks via their context windows, entirely bypassing the need for explicit inner-loop gradient updates at inference time [cite: 7, 8, 9]. 

What is SETTLED is that the inner-loop gradient update is largely unnecessary for the feature extraction layers of a neural network [cite: 4, 6]. It is also settled that when the domain shift between training and test tasks is large, traditional episodic meta-learning performs worse than a simple baseline of supervised pre-training followed by linear fine-tuning [cite: 10]. Furthermore, it is settled that the meta-training phase and the task-adaptation phase are uncorrelated; optimizing them jointly is less effective than independently scaling the training classes and then applying standard fine-tuning [cite: 11, 12]. 

What is CONTESTED is whether gradient-based meta-learning has any remaining utility for adapting the weights of large-scale models. One side (largely practitioners scaling foundation models) argues that in-context learning completely supersedes gradient-based adaptation, viewing the prompt as a superior, non-destructive inner loop [cite: 7, 13]. The opposing side argues that in-context learning is fundamentally limited by context window constraints and memory scaling, and that meta-learned parameter-efficient fine-tuning (such as meta-learned Low-Rank Adaptation) is strictly necessary for tasks that require deep domain adaptation, such as complex protein fitness prediction or cross-subject brain decoding [cite: 8, 9].

What is OPEN is the mathematical mechanism by which transformers implicitly execute meta-learning algorithms during forward passes, and how to construct unsupervised meta-learning environments that automatically generate task distributions robust enough to force a model into meta-learning without human-labeled episodes [cite: 7, 14]. The absorbing field is In-Context Learning and Foundation Model Alignment. What was lost in the merge was the elegant, model-agnostic formulation that allowed any arbitrary neural network architecture to become a few-shot learner; today's frontier is almost exclusively tailored to the transformer architecture and its specific attention mechanisms.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Finn, C., Abbeel, P., Levine, S.
2017
Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks
International Conference on Machine Learning
arXiv:1703.03400
This is the paper that defined the method you are anchoring to [cite: 1, 3]. It introduced the nested-loop optimization algorithm for learning a model initialization. A practitioner must know this because it established the standard mathematical notation, the episodic training structure, and the baseline metric against which the next five years of research were measured.

Snell, J., Swersky, K., Zemel, R.
2017
Prototypical Networks for Few-shot Learning
Advances in Neural Information Processing Systems
arXiv:1703.05175
This paper defined the primary alternative to gradient-based meta-learning: metric-based meta-learning. It computes a prototype vector for each class and classifies queries via Euclidean distance. It remains crucial because it is often much faster to train and far less brittle than gradient-based methods, serving as the default baseline in modern software libraries.

Raghu, A., Raghu, M., Bengio, S., Vinyals, O.
2019
Rapid Learning or Feature Reuse? Towards Understanding the Effectiveness of MAML
International Conference on Learning Representations
arXiv:1909.09157
This is the most critical load-bearing paper for understanding the tacit reality of the field [cite: 4, 5]. It proves through layer-freezing experiments that Model-Agnostic Meta-Learning works almost entirely by reusing high-quality features learned in the outer loop, leading to the Almost No Inner Loop algorithm.

Chen, W., Liu, Y., Kira, Z., Wang, Y., Huang, J.
2019
A Closer Look at Few-Shot Classification
International Conference on Learning Representations
arXiv:1904.04232
This paper devastated the complexity of the field by demonstrating that a simple pre-training baseline, when equipped with a deeper backbone network like a ResNet, eliminates the performance gap of complex meta-learning algorithms [cite: 10]. It introduced cross-domain evaluation, proving that meta-learning algorithms fail to generalize out of distribution.

Triantafillou, E., Zhu, T., Dumoulin, V., Lamblin, P., Evci, U., Xu, K., Goroshin, R., Gelada, C., Swersky, K., Manzagol, P., Larochelle, H.
2020
Meta-Dataset: A Dataset of Datasets for Learning to Learn from Few Examples
International Conference on Learning Representations
arXiv:1903.03096
This paper introduced the authoritative benchmark that the field currently uses to measure true generalization [cite: 15, 16]. It curates ten diverse datasets and enforces realistic class imbalances, ending the era of toy benchmarks.

CURRENT SOURCES (THE 2026 FRONTIER)

Luo, X., Wu, H., Zhang, J., Gao, L., Xu, J., Song, J.
2023
A Closer Look at Few-shot Classification Again
International Conference on Machine Learning
arXiv:2301.12246
This paper represents the modern consensus that the meta-training phase and the adaptation phase are completely disentangled [cite: 11, 12]. It establishes scaling laws for few-shot learning, showing that test error decreases as a power law with the number of training classes, not training samples per class [cite: 12, 17].

Beck, J., Surana, S., McAuliffe, M., Bent, O., Barrett, T., Luis, J., Duckworth, P.
2025
Metalic: Meta-Learning In-Context with Protein Language Models
International Conference on Learning Representations
arXiv:2410.08355
This paper exemplifies the modern frontier, applying meta-learning over a distribution of protein fitness prediction tasks to enable positive transfer via in-context learning [cite: 8]. It demonstrates how fine-tuning models originally trained for in-context meta-learning yields state-of-the-art results with vastly fewer parameters [cite: 8, 18].

Vettoruzzo, A., Braccaioli, L., Vanschoren, J., Nowaczyk, M.
2025
Unsupervised Meta-Learning via In-Context Learning
International Conference on Learning Representations
arXiv:2405.16124
This source outlines how to reframe unsupervised meta-learning as a sequence modeling problem [cite: 7]. It defines the mechanism for learning task context from support images to predict query images without relying on manually labeled task distributions, bypassing a major bottleneck in meta-dataset construction [cite: 7, 14].

Luo, A., Yu, M., Nan, M., Adeli, H., Prince, J., Pyles, J., Wehbe, L., Henderson, M., Tarr, M.
2026
Meta-learning In-Context Enables Training-Free Cross Subject Brain Decoding
Conference on Computer Vision and Pattern Recognition
arXiv:2604.08537
This represents the most aggressive application of the current paradigm, utilizing hierarchical in-context meta-learning to invert functional magnetic resonance imaging encoders [cite: 9, 19]. It proves that meta-learning can generalize across distinct human subjects without any fine-tuning, demonstrating the raw power of the method when anchored to foundation models [cite: 9].

SURVEY
Vettoruzzo, A., Bouguelia, M., Vanschoren, J., Rognvaldsson, T., Santosh, K.
2024
Advances and challenges in meta-learning: A technical review
IEEE Transactions on Pattern Analysis and Machine Intelligence
DOI 10.1109/TPAMI.2023.3323051
This is the single most comprehensive and up-to-date survey of the field, clearly delineating the transition from classical gradient-based approaches to current in-context and unsupervised paradigms [cite: 14]. 

PART 3. SOFTWARE I CAN ACTUALLY RUN

learn2learn
https://github.com/learnables/learn2learn
Python (PyTorch)
MIT License
Most recent activity: 2025
MAINTAINED
This is the community standard for running classical episodic meta-learning experiments [cite: 20, 21]. It uses state-preserving wrappers rather than monkey-patching, which allows it to maintain the stateful look and feel of standard PyTorch [cite: 20]. You can use it today to run the Almost No Inner Loop algorithm on standard vision datasets [cite: 22]. The primary limitation is that it was designed in the era of small Convolutional Neural Networks; attempting to pass a large language model through its task generator and differentiable optimizer will likely result in out-of-memory errors because it is not deeply integrated with PyTorch's Fully Sharded Data Parallelism.

higher
https://github.com/facebookresearch/higher
Python (PyTorch)
MIT License
Most recent activity: 2023
DORMANT
Originating from Facebook Research, this library provided differentiable versions of optimizers by monkey-patching PyTorch modules to make them stateless [cite: 23, 24]. It was once the canonical way to backpropagate through an unbounded number of optimization steps [cite: 23]. However, because it overrides fundamental PyTorch mechanics, it heavily conflicts with modern PyTorch features like torch.compile and standard state dictionary extraction [cite: 25]. While famous, it is brittle on modern toolchains and most practitioners avoid it for new projects, opting instead to write custom inner-loop unrolling using PyTorch's native functional APIs.

torchmeta
https://github.com/tristandeleu/pytorch-meta
Python (PyTorch)
MIT License
Most recent activity: 2023
DORMANT
Torchmeta was designed to be the OpenAI Gym of meta-learning, standardizing the data loading pipelines for few-shot learning benchmarks [cite: 26, 27]. It was universally used to guarantee reproducibility across dataset splits. Unfortunately, it is now effectively dead. It relies on deprecated torchvision APIs and requires significant patching to build in a 2026 environment. Modern practitioners usually bypass it and write custom data loaders using the HuggingFace Datasets library.

meta-dataset
https://github.com/google-research/meta-dataset
Python (TensorFlow / JAX)
Apache 2.0 License
Most recent activity: 2026
MAINTAINED
This is the official evaluation harness for the field's most authoritative benchmark [cite: 28]. It is notoriously difficult to install because it relies on a complex pipeline of TensorFlow Datasets, even if your underlying model is in PyTorch or JAX. The gotcha is that the data generation pipeline is heavily CPU-bound; if you do not provision a machine with massive CPU core counts and high memory bandwidth, the dataloader will silently become the bottleneck, leaving your GPUs completely starved. 

PART 4. DATA AND BENCHMARKS

Meta-Dataset
Access: https://github.com/google-research/meta-dataset
Size: ~150 GB (uncompressed)
License: Mixed (aggregates multiple datasets with varying non-commercial restrictions)
This is the authoritative benchmark suite [cite: 15, 16]. It consists of ten distinct image datasets including ImageNet, Omniglot, Aircraft, CUB-200, and Describable Textures. It measures cross-domain few-shot classification and tests a model's robustness to realistic class imbalance and varying shot counts [cite: 16, 29]. Unlike older benchmarks, achieving high accuracy on this requires leveraging diverse training sources without catastrophic interference.

ProteinGym
Access: https://proteingym.org
Size: ~50 GB
License: MIT
This is the emerging authoritative benchmark for the application of meta-learning in the biological domain [cite: 8]. It contains over two million experimental measurements of protein fitness across hundreds of distinct protein families. It is used to measure how well a meta-learned model can predict the functional consequences of mutations in previously unseen proteins [cite: 8].

MiniImageNet
Access: Various direct academic downloads; originally curated by Vinyals et al.
Size: ~2.5 GB (60,000 images, 84x84 resolution)
License: Custom (derived from ImageNet)
This is a popular but fully saturated legacy benchmark [cite: 30]. It is used to measure 5-way 1-shot and 5-way 5-shot classification [cite: 6, 22]. It is widely considered solved by simple pre-training baselines. Any paper in 2026 that solely reports state-of-the-art on MiniImageNet without cross-domain evaluation is likely overfitting to the benchmark or exploiting data contamination. 

Omniglot
Access: https://github.com/brendenlake/omniglot
Size: ~10 MB
License: MIT
A collection of 1623 handwritten characters from 50 different alphabets [cite: 30]. Historically the "MNIST of meta-learning." It is utterly saturated. It should only be used as a rapid continuous integration test to verify that your gradient loops are functioning, not as a source of experimental findings.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to anchor yourself in this field is the reproduction of the Almost No Inner Loop algorithm on the MiniImageNet dataset, as defined by Raghu et al. [cite: 4, 22]. This experiment is informative because it empirically proves the "feature reuse" phenomenon and provides a highly stable baseline [cite: 5].

Exact Software: Python 3.10, PyTorch 2.2, learn2learn 0.2.0 [cite: 21].
Dataset: MiniImageNet, utilizing the standard 64 training, 12 validation, and 24 test class splits [cite: 6].
Parameters: 
- Task setup: 5-way, 1-shot (5 classes per task, 1 support image per class) [cite: 6].
- Inner loop learning rate: 0.1 [cite: 6].
- Inner loop steps: 5 [cite: 6].
- Outer loop optimizer: Adam.
- Outer loop learning rate: 0.001.
- Meta-batch size: 16 tasks per outer update [cite: 6].
- Base model: 4-layer Convolutional Neural Network (32 hidden channels per layer).
- Mechanism: Freeze the four convolutional layers during the inner loop. Only apply the inner loop gradient steps to the final linear classification head [cite: 5, 22].
Replicates: 3 independent seeds (e.g., 42, 43, 44) [cite: 5].
Approximate Compute: 4 to 6 GPU hours on a single standard workstation GPU (e.g., RTX 4090 or A100).
Expected Result: 46.9 percent accuracy with a 95 percent confidence interval of plus or minus 0.2 percent on the test set query images [cite: 22]. Citation for this number is Raghu et al., 2019, "Rapid Learning or Feature Reuse?" [cite: 22].

The three most common ways people get this experiment wrong:
1. Batch Normalization Leakage. Practitioners accidentally use transductive batch normalization, where the statistics of the query set are aggregated and used during the forward pass [cite: 31]. This allows the model to cheat by implicitly passing information between query samples. You must strictly track running statistics independently or use instance normalization.
2. Graph Detachment. In PyTorch, if you do not pass create_graph=True to the inner loop gradient computation, the computational graph is destroyed after the inner loop step. The outer loop will then silently fail to backpropagate through the optimization trajectory, resulting in a model that does not actually meta-learn.
3. Memory Leaks. Storing the unrolled computational graphs across a large meta-batch size quickly exceeds VRAM limits. Practitioners often fail to properly clear intermediate graph buffers, crashing the experiment at epoch two.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you are entering the field to do frontier work, you must build a distributed, parameter-efficient meta-learning harness for large foundation models. There is no off-the-shelf tool that correctly applies episodic gradient-based meta-learning to a 10-billion parameter transformer model using PyTorch Fully Sharded Data Parallelism. 

What goes in: A HuggingFace transformer model, a task generator yielding support and query sequence prompts, and a configuration for Low-Rank Adaptation matrices.
What comes out: A meta-learned set of Low-Rank Adaptation weights that serve as the universal initialization for new tasks.
The hard part: PyTorch's native tools for differentiating through optimization steps (like torch.func or the dormant higher library) are fundamentally incompatible with the complex, multi-GPU gradient sharding mechanics of Fully Sharded Data Parallelism. When you take an inner-loop step on a distributed model, tracking the higher-order gradients across device boundaries requires deep, low-level overriding of the communication hooks. 
Work estimate: This is a severe engineering challenge requiring two to three months of dedicated work by an expert systems programmer. 
Private rebuilds: Several industrial labs studying Meta-Learning for Large Language Models have rebuilt this exact component privately. They typically implement it by manually unrolling the inner loop for a fixed number of steps using implicit gradient formulations (like the Neumann series approximation) to avoid holding the entire distributed graph in memory, bypassing PyTorch's automatic differentiation engine for the outer loop entirely.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The history of meta-learning over the past six years is dominated by the dismantling of its own foundational assumptions. This section is extensive because the tacit knowledge of what failed defines the current research boundary.

The Fall of Rapid Learning
The original premise of Model-Agnostic Meta-Learning was that the outer loop discovered an optimal dynamic initialization in the loss landscape. It was hypothesized that this initialization was highly sensitive, such that a few gradient steps would cause massive, rapid shifts in the network's internal representations, customizing the feature extractors for the new task [cite: 5, 6]. This program failed entirely. Extensive representational similarity analysis and layer-freezing experiments proved that the internal representations do not change meaningfully during the inner loop [cite: 5]. The inner loop merely aligns a linear classifier to pre-existing, universally robust features learned by the outer loop [cite: 5, 6]. This realization led directly to the Almost No Inner Loop algorithm, proving that computing second-order derivatives through the network body was a massive waste of compute [cite: 4, 22].

The Baseline Critique and the Failure of Complexity
For years, the field was flooded with increasingly complex algorithms: task-dependent metric scaling, memory-augmented neural networks, and hyper-network parameter generators. In 2019, a standing methodological critique emerged: the entire field was measuring an artifact of using shallow neural networks. When researchers replaced the standard 4-layer convolution network with a ResNet-18, a simple supervised baseline—pre-training on all available base classes via standard cross-entropy and then freezing the network to train a logistic regression classifier on the new task—matched or explicitly outperformed almost all published meta-learning algorithms [cite: 10]. Furthermore, when tested on cross-domain tasks (e.g., training on ImageNet and testing on medical images), meta-learning models failed catastrophically compared to the standard fine-tuning baseline [cite: 10, 32]. 

The Disentanglement of Training and Adaptation
A later critique systematically dismantled the need for episodic training itself. It was long held that you must construct artificial "tasks" (episodes) during training to simulate the testing environment [cite: 3]. However, massive empirical studies in 2023 demonstrated that the meta-training phase and the adaptation phase are completely uncorrelated [cite: 11, 17]. Algorithm design can and should be done individually for each phase [cite: 11]. Episodic meta-training often enforces an artificial bottleneck that harms the model's ability to learn general global features. A standard supervised model trained on a wide distribution of classes (or a self-supervised model) produces a feature space that is strictly superior to episodically meta-trained spaces [cite: 12, 17].

The Benchmark Saturation Problem
Many methods that looked strong were later shown to be measuring the benchmark rather than the phenomenon. MiniImageNet is heavily saturated, meaning performance differences between algorithms reflect random seed variations and hyperparameter tuning rather than algorithmic superiority. Models began to overfit to the specific geometry of the 5-way 5-shot arrangement. When the community shifted to Meta-Dataset to answer this critique, it became apparent that algorithms highly tuned for MiniImageNet could not handle class imbalance or varying shot counts [cite: 16, 29].

In summary, the standing, largely unanswered critique of gradient-based meta-learning for representation learning is that it is computationally exorbitant and mathematically elegant, but empirically inferior to simply scaling up self-supervised pre-training on diverse data and using linear probing at test time.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the computational landscape and the hard lessons of the past decade, a well-resourced newcomer should entirely abandon episodic gradient-based meta-learning for small vision models. Instead, focus on the intersection of meta-learning formalisms and massive sequence models.

Aim 1: Unsupervised Meta-Learning via In-Context Sequence Modeling (Highest Priority)
What to do: Design an experiment that reframes unsupervised meta-learning as a flow generation or sequence modeling problem for foundation models. specifically, construct a training environment where a transformer is fed a non-causal sequence of unlabeled support data and forced to predict the representations of query data, explicitly training its attention heads to execute functional inversion in-context [cite: 7, 14].
Feasibility: Feasible now due to advancements in context window scaling and FlashAttention optimizations.
Measurement: Evaluate zero-shot transfer accuracy on out-of-distribution downstream tasks without any parameter updates [cite: 7, 8].
Falsification: The idea is falsified if standard self-supervised contrastive learning (like DINO) produces embeddings that yield higher accuracy under a simple k-nearest neighbors classifier than the outputs generated by the in-context meta-learned sequence model.

Aim 2: Meta-Learning Low-Rank Adaptations for Cross-Modal Functional Inversion
What to do: Run experiments that meta-learn the initialization of Low-Rank Adaptation matrices for cross-subject decoding, such as translating functional magnetic resonance imaging signals into semantic space across different human subjects [cite: 9, 19]. The outer loop optimizes the low-rank initialization across many subjects; the inner loop takes two gradient steps on a brief calibration session for a new subject.
Feasibility: Feasible now because we have access to massive neuroimaging datasets like the Natural Scenes Dataset [cite: 19], and Low-Rank Adaptation drastically reduces the memory overhead of the inner-loop unrolling.
Measurement: Cross-subject decoding accuracy, measured by the structural similarity index and semantic clip distance of reconstructed stimuli [cite: 9].
Falsification: The idea is falsified if training a single massive transformer on all subjects jointly (without any subject-specific inner loop adaptation) achieves equal or superior decoding accuracy.

Aim 3: Generative Flow Matching for Task-Specific Weight Generation
What to do: Rebuild the mechanism of meta-learning entirely by discarding the inner loop gradient descent. Instead, train a continuous normalizing flow model (Flow Matching) that takes a support set as a conditioning context and directly generates the optimal neural network parameters (weights) for a classification head [cite: 33].
Feasibility: Feasible now due to the stabilization of flow matching algorithms and their recent successful application to latent spaces. 
Measurement: Mean squared error of the generated weights versus the ideal weights found via traditional convergence, and the downstream few-shot accuracy on unseen domains.
Falsification: The idea is falsified if the generative model collapses to predicting the mean weight distribution, failing to capture high-frequency task-specific decision boundaries, resulting in performance worse than a statically initialized random head.

What will NOT work:
Attempting to discover a new, more efficient optimizer for the inner loop of a Model-Agnostic Meta-Learning setup applied to computer vision tasks. This will fail because the premise relies on rapid learning, which does not exist [cite: 4, 6]. Any mathematical improvement to the inner loop dynamics will be washed out by the dominant effect of feature reuse [cite: 5, 6]. Furthermore, due to the disentanglement of training and adaptation [cite: 11, 12], the field's reviewers will immediately reject the work if it does not explicitly prove that the new inner loop outperforms a frozen self-supervised feature extractor with a logistic regression head. Do not waste compute on this dead end.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHS-XrzwLA3ML579WQ4CgrXBbHkkjCALfzltbH7obf879GCysoqLtHdigy7QIvFQxm3iuiWGx_HvEVoYfV52SHe-ph6S3jA9HBAl38aAqtUWDZfexVrg==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZdSmi3jxrcLSEvK4uTfaWXxILT4wD6OTgaFI5ZiHkve8DH2iv-dxu4zx5NCJQ5ZNNO1dwH5TtdS1zPo8hNVmCTUD96gGDMepJyTxMkImMCyzjT_JCtYRo58S2wW8KdRcIkAHav-feJqGRLfaUgULGLmtJ7QXImjOzOGgcpduW1nPJ5bgutcm_)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTUwRXC7e1ZCaoY8vGp4Ut2kNPVIIivyFGBwlHxheMraxlSD3A0eLTFiltxItbEMpPCE30WLSF4kziCJAC0BAiddWi11EQppHooGCEpejvQ3eTh8BVpAVMJA==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1QRgl8G0xFkgeADeXTnszA715-k0dO1eXku0dx5Uuqr5QdwZrQVFQET2zB0DdVmmjNWnNwXWIs8Ok91PlI8GFRQXV0Z3U7PFBn2I0g8u4oQ8fhASvjQ==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzy24Wf-vp5bgtHA23Uxp9lgfa6iE8cKQaBIlWCcZ8juiABzXkJwgnSqAeok3TNes0Izxrl6zcYTte_gNu3ZiXO7-WM9aDVSo8khryKVL1qfzxITbDi2ZpLg==)
6. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUzUaY6od7udnu-pxj-ahTLnHZjpVAqV7tSLJO96jwhCVgwvaF1SaJg6GXi3BHodLCD4X5uuNez3GXWawBUfLRrWAgDvulcLFF35Mv3TtsIAvnM9rQCZ2F3Co01ZXQuq515kVaWXIPj1uetrrUJ1dxol7F6IEz)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuJmF3fEmwgnp8pvHfcNlc05wJwMaUvpMA8asoRUZetAmQV2bnAZfAjSYvPn6pJbbURHl-FrfH9PmhiCmhf1oLRuxxO8qFO_XldqAtt35uytvLAomevQ==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYDHPWQpbSTqweQ_gUKyD5WN3GljMn_1f7HcJ_Me8QdI-tEHrj__lSfU8WH9dzt9Rus5v_j-1By_Dgw8-twfvzDt2d5nT27-Kxhhu3CyNKxdWVy-Pjyw==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1wmipZTudp4xjKMU_OW7wpWLSvZBOrerigW5x6Pkm_9Sz5F5JiyvXwbCQHZcVTenOM0pa_n4CxDxdBcSq1cJ__yzUqRC9vWaZ1h6yVjxMc5SFcLy2Cg==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFV7YCqOA_vQTNbSaHt_p0HF369TQO5Gq0ny8Rqj4himT1mOfzQxhacWPZCKI7PIX9wuH_-hLOZB706kvkT-ZW5Nj32O2cTEPYgc9-f4fhT7uheJKbyeg==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPBXjZPNUA1pTpCtszXTDD_MwSUEf66WIz9XtbMuZpIbvpnVJvfijZYXiwV25XqIpBBu8IOLQbm9365-PwJrCy_OTeah8gksJ3m-RV2ZlzsDrLcJp3Vw==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfFqrButLvZjV71Kpctg-77E_DBQ7tOwbhqA3Kdkfh9XUMoNK_lIts1DzayTVDtlBSExpg8zcq7rk1SZJ9ynpZikRoBSwP5dlCHw2DeP1Mn9FJ8tPWFEpO3A==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrO7O4y3zYnqZ1JTu5igsHMyb7hhAzXySOFNz5bbxc6EeHwVUVlOnz1A75bJfudhOs-rjNmGUfglEfewBtvfV3fq89_0FYRbtvzptPG8m9HQxUj40wNA==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwQP_nS21n12yiwdw59-yGpcHIKi2OyIt3QaZqzPbXigXTH0vzWbjelglcjx5kSxW5piKq4XnGYUkuh69MV7gyUZbb9TqlJllDy8OJbrKPTPhQVNN13_keaw==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAtJWJGwIldkUXqr0fnPVnU8CLohcnVhKh34Y-uJeg9S-bjvHolKIuPVAfLcMASMxhhUin_0ojsnhkxyOQYS7RJFACFoogbAb4N56y9Tk0tvggsbeVvw==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-Z-nPjhMlcZEy760PcQ5751YWDWr2LZ9SYac-oM4ujUkdtXMeKoCfyL8MIMqwDfeaAOIgO36hZp4HAx8ri02cljQUnHJU_iUCHu6pdtZW1JlMPHyXdhVtUnto2tZ0sSuHYA==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCYreLYwcIMTMHUaLtCzywWQ7f10BtUqkspKze0wpzPy1GCEGzMufmEdJ-Ao3OGYqO_rndudfJ179QYkQCrnySsrQNpegV10D_FLOgnle9o8C2XwQ1Ow==)
18. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAmubT5DI3nb9GA60naisC6qToKQB2ygXjYz0fHpCGvhnjk4MoGgRpXgl7veQo1S9DkQFkcrWR8aYvRkCyz6ZS8FTWsPTaLvyiXVwquscI60ja6OSd148qaxe-ohQ=)
19. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHl_bvu10XWoBESksMFHC-bE53Mvc7jMdPZuFGmRlBDwC3J7VLgVdiyuuzyl2RQZHE9jL2FLEOZiZZRiYRXxQ0wJ3JLw3URt84WJHN-7r3GhWxkP-y2YISyQDE1a3A=)
20. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHxo6jHXfByXbb_dsc2xC_WyZ9pfPRDTDrwuM0mTIrG7oa7tBYKHvLRZWIO8LiiWVHpxM83lXNwLTYtDTDQrcbtc7Q5YAWjBHKWOfzwGKDTUcR_15llV2E1R1sNO-Xqg==)
21. [articsledge.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHra5cEmwTOsEcqjBo5IF23ybBocqjNHtIrvw87lR0aesoI8kfNLlhdisISpxwGV2-S5zf4c2kAtSJ9Tn8rvKpXhgHj1jDq8ox_cMINkqdbhbC5wTknqGo_ktntJcHaCvk7VOHV)
22. [learn2learn.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQPuAukrRpPa9VGGx0Q2OEMrpQWqe3izRD1Dra1fkIvA7zlsDHy2pAxj4iNETtI8L6YEzfAmnkjtOUCLwCJc9fOfAATWeXYGLw3qag7_ZYi-W1a9xgCsZ4NvIk5wf0Xx84yZePBamx36uL9n2bPhZ2zigh7Q==)
23. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHd24SdPWEqkQHOFaMBbNqsePHadBGmSHj_69EHWHP7MRj3dDDWBBOqMWorFtAEdmFkNqiUIFF2psHeGDKd6shxRN4nWYVEFQ4a1_3zvgZISw_t4NIYzenlvCYqTvcsRII=)
24. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETAKycLfSlkPYUlSXHGCaWyYq-NOVJ5l3_BVsa5u68tJtJrsULGRxGdrE2-NhRcSvIqFmFqCwUJPyz8NfKxxcJTbsRFAkSQZzk89wgan8XC0ysj4i4rS-NUt-yU5IIIQS0ABTWUCHVVtJNp1R2q2CaeRMvqCjrRpIUYHujXsPre0Rcb0v6)
25. [pytorch.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGW1zpogMp4tfGaUEBMBvk_CWItCeLfI5-fvevxt80bP7IY1rtJjp65fAPRkl8Hmi6l3BZVUSqGQ-NBSnycez22pAVBWKPM3qgSxt79yDvJrV0mxX4rabiae6aqO_rG9h_WH10src3hq9c29U50NoA4NTENSZsHypc4uPFo-vFpDC5jd6Wt5J2AEs9PjKXtnb_W)
26. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDKJhTjpzyPo6u0ARLnlodsOI-YeFESNItRCjFOWIj0EeNOvgoLhrNRzcR5Q5ZH4i70IaByx0R78i1rSVl3JIVOGBhUEBNKq8bkrHEP2XmLFNJeAyuehrjbmVR4djRQh8Lhg==)
27. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMgLfnlsstwVU-JTGZg6VyCelWblRYNB0090qd_57i0nO67FkYydURTcX4CDHc-IQsDv28UTa7hwMMBCC0fic8yz2ll4b8da8tLCUvvv8BFPfY9B69LRw7Pr0U8iVxHGAPLA9cY8LbL6Ay_-Wfqw7Ra7Q8iec0NImc34w5ZvK5bNnEuDkJ8c14pFk0)
28. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtECfFDdgKkjXt549Xq-e_FFEu1nUSoR2bvdNdxa_NZaLqcAbclyhAf3YRq2ru5mfJ4B-sXwb2DF_YcH1MTBZuwtAMX8MRzNRvHjMWryUINtq5K5hfxZhBo_4JOjEtw2SgqewSyA==)
29. [syncedreview.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5RbZgG73NeVadk5MXPv1JFYbOKXb9Zmbh4r6EuZ-BQFmJPzJgrvtXXLpVM8srmeFuXB2iW1gUiPw2RqfOdqtOQp6sVABhEWvxW70Tf1tzYJD62Q9Xk2IlbRmAHkHmjic2jFgc_81gpELC3NNjChv8pQR8v5ZAsFKEcY5n6dASMuI7cCVGZiRv8OqcDA8PqqmFsoXvDfgCaLM=)
30. [techairesearch.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQ3xPL5ONxzWNvi02--yrXRZLKXSCwgEw8cO05EYMMApOp5j_b3x1EA32cLYgtiMsSB3WI2oqHf6rSRGh8Ja4Bj0V5rsqgOaqs1uahXNjUmLBz82ywzH71oYUyWp0zasK8t5VovN7raxZMpNaX3zIVneItCLbKfieG9TrK5Dc=)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHj0_QdWfxY-rSS62lvqn_tbgs59ExtQKy2_ZdYIjV6gZSrTAjENlsiihsl8n4AwoMsQfhAr0_kCHgDuNc17WnrRq4e9AFvhCDcxgsyxEDoD92oiArl7uEuJQ==)
32. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHedaKW1_ZxEfgbOa5M_2TrZBiPVRRZfx7ADIVXknxne1w1sAJUNROudltF7yIUSlMGc1rLpdmKRkRsD3_g8cqf1PVvCAal5IQrOKHWg_EV2JApxFc1HUaQJp0lVEWHBBP7FmVyeIpB)
33. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGROV1GGwio_ghgtdGS1i1_BjnkPSSjRTy0sNTd0GXzqVDswLqe_kaPNfLOXz1mz8fnmdMBDylkqwL0308QgNwSRMw_nfRSxhC6s4KUG1h_b-OosLg-3UNbHyaLT7I=)

