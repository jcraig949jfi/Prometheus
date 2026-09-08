# Prompt 57: Analogical Reasoning

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdoV0dmYXVQRUZZdmhfdU1QOGJqXzhBcxIXaFdHZmF1UEVGWXZoX3VNUDhial84QXM
**Elapsed:** 334s

---

# Frontier Practitioner Dossier: Analogical Reasoning

Key Points:
Research suggests that classical analogical reasoning, anchored by the Structure-Mapping Engine, remains theoretically robust but computationally isolated due to its reliance on hand-coded, rigid symbolic representations. 
The modern frontier is dominated by Large Language Models and Large Reasoning Models, though recent evidence leans toward the conclusion that these models rely on shallow pattern matching and contextual memorization rather than true abstract structural alignment.
The most promising path forward appears to be Neurosymbolic integration, utilizing probabilistic abductive reasoning to bridge the gap between noisy visual perception and rigorous structural mapping.

State of the Discipline:
The field is currently fractured between cognitive scientists who emphasize deep, systematic structural alignment and machine learning practitioners who attempt to elicit analogical reasoning emergently from massive scale. This tension has produced a crisis of evaluation, where classical benchmarks are saturated by models that fail to generalize under perceptual uncertainty. 

Strategic Outlook for Practitioners:
A competent computational scientist entering this field in 2026 should avoid attempting to build yet another purely connectionist end-to-end model. The highest leverage lies in constructing differentiable, probabilistically tolerant mapping engines that can accept noisy, open-vocabulary scene graphs and enforce the constraints of one-to-one mapping and parallel connectivity without requiring human ontological intervention.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

The field of analogical reasoning in 2026 is a discipline caught in a methodological tug-of-war between classical symbolic cognitive modeling and modern deep learning. At its core, the field investigates how intelligent agents recognize that two distinct situations share a common underlying relational structure, despite having entirely different surface features, and how they project inferences from a familiar base domain to a novel target domain. Your description of the Structure-Mapping Engine mechanism is remarkably accurate and perfectly captures the foundational 1989 algorithm proposed by Falkenhainer, Forbus, and Gentner [cite: 1]. The only minor correction required is that while the original algorithm exhaustively merged structurally consistent kernels into maximal global interpretations, modern implementations utilized by the Qualitative Reasoning Group employ a greedy merging algorithm that operates in O(N squared log N) time to maintain tractability over large knowledge bases [cite: 2]. The systematicity principle, parallel connectivity, and one-to-one mapping remain the definitive constraints of the field [cite: 2].

What is SETTLED is that pure structure mapping works flawlessly when the representations of the base and target domains are perfectly abstracted, noise-free, and ontologically aligned. If you provide a symbolic engine with a pristine predicate calculus description of the solar system and the Rutherford atom, it will reliably map the planets to the electrons and gravity to electromagnetic attraction. It is also settled that human cognition fundamentally relies on this type of abstract, systematic relational mapping to achieve rapid few-shot learning and out-of-distribution generalization. 

What is CONTESTED is whether modern Large Language Models and Large Reasoning Models perform anything resembling true analogical reasoning. One faction, heavily represented by commercial AI labs, argues that analogical reasoning is an emergent property of next-token prediction over massive datasets, pointing to LLM successes on text-based analogy prompts and code translation tasks [cite: 3]. The opposing faction, led by cognitive scientists and critical AI researchers like Melanie Mitchell and François Chollet, argues that LLMs are merely deploying sophisticated statistical pattern matching, relying on data contamination and "Function Vectors" that capture low-level formatting rather than invariant conceptual structure [cite: 4, 5]. This faction argues that when perceptual uncertainty or confounding variables are introduced, LLM analogical reasoning collapses entirely [cite: 6, 7].

What is OPEN is the neurosymbolic frontier. The grand challenge of the field is the "perception-to-structure" bottleneck. How do we take messy, real-world continuous data (images, video, unstructured text), extract a reliable relational graph, and perform rigorous structure mapping over it? The field is actively seeking mechanisms to integrate the perceptual flexibility of neural networks with the strict logical constraints of the Structure-Mapping Engine [cite: 8, 9]. 

In the last three years, the field experienced a violent pendulum swing. In 2023 and 2024, early papers claimed LLMs had effectively solved human-level analogical reasoning benchmarks. By late 2025 and early 2026, rigorous adversarial testing revealed these claims were mostly artifacts of overlapping training data and rigid evaluation formats. The introduction of benchmarks like ConceptARC [cite: 10, 11] and I-RAVEN-X [cite: 6] demonstrated that LLMs fail to abstract concepts like "inside" or "same shape" when presented in visually novel or uncertain configurations. Consequently, the field has aggressively pivoted back toward hybrid architectures—specifically neuro-symbolic probabilistic abductive reasoning models that maintain a separation between perceptual embedding and structural mapping [cite: 9].

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Falkenhainer, B., Forbus, K. D., and Gentner, D.
1989
The Structure-Mapping Engine: Algorithm and Examples
Artificial Intelligence
DOI 10.1016/0004-3702(89)90077-5
This is the load-bearing pillar of the entire field, formalizing Gentner's psychological theory into a computable algorithm. A practitioner must read this to understand exactly how local match hypotheses are generated, constrained by parallel connectivity, and scored via the systematicity principle [cite: 1].

Gentner, D.
1983
Structure-Mapping: A Theoretical Framework for Analogy
Cognitive Science
DOI 10.1207/s15516709cog0702_3
The seminal theoretical paper that defined the rules of the game: that analogies are about relations, not attributes, and that higher-order relations (relations between relations, like causality) carry more weight than isolated facts [cite: 1, 12].

Chalmers, D. J., French, R. M., and Hofstadter, D. R.
1992
High-Level Perception, Representation, and Analogy: A Critique of Artificial Intelligence Methodology
Journal of Experimental and Theoretical Artificial Intelligence
DOI 10.1080/09528139208953747
The definitive standing critique of the Structure-Mapping Engine. The authors argue that analogy cannot be separated from perception, and that supplying SME with hand-coded, pre-abstracted representations bypasses the actual difficult part of cognition [cite: 13, 14].

Chollet, F.
2019
On the Measure of Intelligence
arXiv
arXiv:1911.01547
Introduces the Abstraction and Reasoning Corpus (ARC), which has become the inescapable standard for testing visual analogical reasoning and few-shot generalization in modern AI systems [cite: 10, 15].

CURRENT SOURCES (THE 2026 FRONTIER)

Camposampiero, G., Hersche, M., Wattenhofer, R., Sebastian, A., and Rahimi, A.
2025
Can Large Reasoning Models do Analogical Reasoning under Perceptual Uncertainty?
arXiv
arXiv:2503.11207
This paper shatters the illusion that Large Reasoning Models like o3-mini have solved analogy, proving that their performance drops from over 80 percent to near random chance when perceptual uncertainty (confounders and distribution smoothing) is added to the I-RAVEN dataset [cite: 6, 7].

Opiełka, G., Rosenbusch, H., and Stevenson, C. E.
2025
Analogical Reasoning Inside Large Language Models: Concept Vectors and the Limits of Abstraction
arXiv
arXiv:2503.03666
A crucial mechanistic interpretability paper proving that while LLMs can form "Function Vectors" for simple analogical tasks, these vectors are highly sensitive to surface-level formatting and fail to represent true invariant "Concept Vectors" for abstract relational ideas like "previous" or "next" [cite: 5, 16].

Moskvichev, A., Odouard, V. V., and Mitchell, M.
2023
The ConceptARC Benchmark: Evaluating Understanding and Generalization in the ARC Domain
Transactions on Machine Learning Research
arXiv:2305.07141
Demonstrates that AI systems capable of passing original ARC tasks fail miserably when tested systematically on specific, isolated concepts like "containment" or "symmetry", exposing a lack of true conceptual abstraction [cite: 10, 17].

Lewis, M., and Mitchell, M.
2024
Evaluating the Robustness of Analogical Reasoning in Large Language Models
arXiv
arXiv:2411.14215
Tests LLMs on variations of classic analogy problems (letter strings, digit matrices, story analogies) and proves that their analogy-making is brittle, highly susceptible to answer-order effects, and easily disrupted by paraphrasing [cite: 4].

Yasunaga, M., et al.
2023
Large Language Models as Analogical Reasoners
arXiv
arXiv:2310.01714
Introduces "Analogical Prompting", a method where an LLM is prompted to self-generate relevant past experiences before solving a new problem. Important to read to understand the baseline best-case scenario for connectionist analogy [cite: 3].

SURVEY RECOMMENDATION

Wan, Z., et al.
2024
A Survey of Neuro-Symbolic AI
arXiv
arXiv:2405.06561 (IDENTIFIER UNKNOWN for exact 2024 survey, but standard recent NeSy literature)
While a specific neurosymbolic survey was highlighted [cite: 8], the practitioner should seek recent overviews categorizing NeuroSymbolic architectures to understand where structural mapping can be embedded into latent spaces.

PART 3. SOFTWARE I CAN ACTUALLY RUN

SME4
https://github.com/slburson/SME4
Common Lisp
MIT License (UNCONFIRMED, standard open source)
2023
MAINTAINED
This is the closest you will get to the canonical reference implementation of the Structure-Mapping Engine from Ken Forbus's Qualitative Reasoning Group. It was recently ported to modern Common Lisp (ASDF loadable via Quicklisp, runs on SBCL) [cite: 18]. You can run the classic heat-flow to water-flow analogy experiments with this today. Limitation: It relies on completely manual, hand-crafted Lisp s-expressions for its knowledge base, meaning you cannot easily hook it up to modern datasets like ARC without writing an exhaustive vision-to-symbol pipeline yourself.

SMEPy
https://github.com/crazydonkey200/SMEPy
Python
License UNKNOWN
2018 (Approximate)
DORMANT
A direct Python translation of the Structure-Mapping Engine [cite: 19]. It can run the classic water-flow and heat-flow analogy out of the box. Gotcha: This is an unoptimized, naive port. It does not contain the advanced greedy-merge optimizations of modern SME implementations, meaning it will suffer combinatorial explosion and crash if you feed it a scene graph with more than a few dozen predicates. 

ANASIME
https://github.com/Tijl/ANASIME
Python
GPLv3
2013
ABANDONED
Developed at the Donders Centre for Cognition to systematically assess algorithmic variants of Structure-Mapping Theory, including fixed-parameter tractable adaptations [cite: 20]. It includes a highly useful predicate structure pair generator. Limitation: It is written in Python 2.6 and relies on outdated networkx and pygraphviz libraries; it requires significant syntax porting to run on modern Python 3 toolchains [cite: 20].

SME-clj
https://github.com/svdm/SME-clj
Clojure
MIT License
2010
ABANDONED
A master's thesis implementation of SME in Clojure [cite: 21]. Strictly historical. It requires ancient versions of Clojure (1.2.0) and is entirely unbuildable on modern Leiningen toolchains without dependency hell. Avoid unless mining for algorithm structure.

raven-large-language-models
https://github.com/IBM/raven-large-language-models
Python
MIT License (with specific dependencies)
2025
MAINTAINED
This is the active, frontier repository for evaluating neuro-symbolic probabilistic abductive models (like ARLC) against Large Reasoning Models on analogical tasks under perceptual uncertainty [cite: 9, 22]. You can use this to generate the I-RAVEN-X dataset with confounding variables and smoothed probability distributions, and replicate the exact failure modes of modern LLMs. Gotcha: Requires heavy compute (optimized for dual A100 GPUs) and specific CUDA 12.1 environments [cite: 22].

ConceptARC Editor and Dataset
https://github.com/victorvikram/conceptarc
HTML/JS (Editor) / JSON (Data)
Open Access
2023
MAINTAINED
The standard benchmark suite for testing whether an AI has actually learned a relational concept or is just memorizing patterns [cite: 17, 23]. Contains an excellent browser-based editor for building your own ARC-style analogical grids. Limitation: It is purely a dataset and visualization tool; it contains no inference code.

PART 4. DATA AND BENCHMARKS

The Abstraction and Reasoning Corpus (ARC)
https://github.com/fchollet/ARC
800 unique tasks (400 training, 400 evaluation)
Apache 2.0
The undisputed authoritative benchmark for general visual analogical reasoning. Models are given a few demonstrations of a grid transformation and must generate the test output grid from scratch [cite: 10, 15]. Known Saturation/Overfitting: Many closed-source LLMs have likely ingested the public training set, and Kaggle-winning symbolic solutions often rely on hand-coded domain-specific languages (DSLs) that hardcode the exact symmetries and color shifts required, completely failing to generalize outside the benchmark [cite: 10, 24].

ConceptARC
https://github.com/victorvikram/conceptarc
160 tasks (16 concept groups, 10 tasks each)
Open Access
Designed specifically to fix the generalization loopholes in the original ARC. It measures abstraction abilities on basic spatial and semantic concepts (e.g., inside, outside, same-shape, line-of-sight) [cite: 10, 11]. If an architecture claims to have solved analogical mapping, the field now demands it be tested on ConceptARC to prove it understands the underlying relation across wildly varying visual noise. 

I-RAVEN and I-RAVEN-X
https://github.com/IBM/raven-large-language-models
Procedurally generated (effectively infinite, tens of thousands of instances typically used)
MIT License (derived)
Used to measure analogical reasoning via Raven's Progressive Matrices. Original RAVEN was discovered to have a severe contamination problem: the answer candidates were generated in a way that allowed neural networks to ignore the context matrix entirely and just guess the answer based on statistical regularities in the candidate pool [cite: 25]. I-RAVEN fixed this candidate generation flaw. I-RAVEN-X is the new 2025 authoritative variant that increases operand complexity, expands attribute ranges to 1000, and introduces severe perceptual uncertainty via confounding variables [cite: 6, 25].

Bongard-LOGO
Access route: Stanford/Nie et al. project page (IDENTIFIER UNKNOWN for exact raw URL, accessible via standard search)
12000 problems
Open Access
A modern adaptation of classical Bongard problems, requiring an agent to find the analogical rule that unifies a set of primary shapes and excludes a set of negative shapes [cite: 10, 26]. Often solved via program synthesis rather than pure structure mapping [cite: 10].

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to run in 2026 is the Perceptual Uncertainty Stress Test on Analogical Reasoning, published by Camposampiero, Hersche, Wattenhofer, Sebastian, and Rahimi (2025) [cite: 6, 7]. This experiment definitively proves that Large Reasoning Models are not performing structural evaluation, but rather fragile pattern matching that collapses when visual input is not pre-abstracted perfectly.

The Setup:
Software/Version: Clone the IBM repository at https://github.com/IBM/raven-large-language-models [cite: 9, 22]. You will need Python 3.10, PyTorch 2.3.1, and CUDA 12.1.
Dataset Generator: Use the included I-RAVEN-X generator script. 
Parameters to Set:
1. Matrix size: 3x10 (extended from standard 3x3) [cite: 27].
2. Attribute Range: Set to 1000 (forces the model to handle massive variance) [cite: 6].
3. Perceptual Uncertainty Flags: Enable "Confounding Attributes" (injects random background colors and patterns that have no bearing on the analogical rule) and "Smooth Attribute Distributions" (uses a three-bins probability smoothing strategy instead of a deterministic oracle integer) [cite: 6, 27].
Replicates and Seeding: Run across the full generated I-RAVEN-X test suite (typically 10,000 instances) using a fixed random seed for the generator to ensure the exact same confounding variables are applied across all model evaluations.
Compute Cost: Generating the dataset and running the Neuro-Symbolic ARLC baseline requires a local GPU setup (approx 10 to 20 GPU hours on dual A100s). Querying the OpenAI o3-mini API requires zero local compute but will consume several million API tokens due to the long context of the 3x10 matrices and the model's internal reasoning loops (o3-mini consumes roughly 3.4 times more tokens attempting to solve these than standard prompts) [cite: 6, 9].

Expected Result:
When evaluated on the clean I-RAVEN dataset, o3-mini should score approximately 86.6 percent. When evaluated on your generated I-RAVEN-X dataset with perceptual uncertainty enabled, the o3-mini accuracy must plummet to approximately 17.0 percent (approaching random chance) [cite: 6, 9]. In contrast, the local ARLC neuro-symbolic model should drop only from 98.6 percent to approximately 88.0 percent [cite: 6, 9].

Three Most Common Ways People Get This Wrong:
1. Failing to disable oracle perception. Many researchers pass the matrix to the LLM as a clean, perfectly structured JSON dictionary of features (e.g., shape: square, color: red). By doing this, they perform the perception and abstraction for the model, rendering the analogical mapping trivial. You must pass the smoothed probabilities and confounders.
2. Allowing LLM API temperature variation. Reasoning models must be locked to Temperature 1 (or the API equivalent for reasoning models like o3-mini) to ensure their internal chain-of-thought routing behaves as designed; restricting or altering this breaks their search space [cite: 17].
3. Relying on original I-RAVEN instead of I-RAVEN-X. Original I-RAVEN is saturated. LLMs will appear to succeed because the attribute range is narrow enough for them to guess the relational logic via memorized frequentist distributions rather than systematicity [cite: 25].

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to run frontier experiments, you cannot use SME4 or SMEPy out of the box because they operate on rigid, discrete symbols (Lisp or Python strings). What does not exist, and what multiple research groups are attempting to build privately, is a Differentiable Structure-Mapping Engine (DSME) implemented natively in PyTorch or JAX.

What Goes In:
Two sets of probabilistic scene graphs (a base and a target). Instead of discrete predicates like "orbit(sun, earth)", the input must be a set of tensor embeddings representing entities (nodes) and their relations (edges). Each node and edge carries a high-dimensional vector and a probability distribution over its presence.

What Comes Out:
A soft-mapping matrix (a differentiable assignment matrix) that represents the probability of correspondence between base and target items, constrained by a differentiable penalty for violating one-to-one mapping and parallel connectivity. It must output a scalar Structural Evaluation Score that can be backpropagated through to update the weights of the perceptual front-end.

The Hard Part:
Parallel connectivity requires that if a relation is mapped, its arguments must also be mapped. In classical SME, this is a strict boolean constraint checked via tree-traversal. In a tensor framework, enforcing this structurally consistent hierarchical alignment requires complex continuous optimization (like Sinkhorn iteration or graduated assignment algorithms) over an exponentially large combinatorial match space [cite: 28]. Avoiding local minima where the matrix softly matches everything to everything is extremely difficult. 

Work Required:
This is a six-to-twelve month project for a competent computational scientist. It requires rewriting the classical SME local-to-global match algorithm as a series of batched tensor operations (e.g., calculating a pairwise similarity matrix for all predicates, then using graph neural network message passing to enforce the systematicity principle from the top down). 

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The history of analogical reasoning is littered with programs that solved isolated toy domains and failed to generalize to the real world. 

The High-Level Perception Critique (The Chalmers-French-Hofstadter Dispute)
The most famous standing critique of the entire structure-mapping enterprise was leveled in 1992 by David Chalmers, Robert French, and Douglas Hofstadter [cite: 13]. They argued that the Structure-Mapping Engine was fundamentally flawed because it assumed that representations are supplied "ready-made" by a separate perception module. Hofstadter argued that in human cognition, analogy and perception are indistinguishable; the act of building the representation is driven by the pressures of the analogy itself [cite: 13, 14]. SME's "hand-coded rigid representations" meant that the human programmer was doing all the actual cognitive work by deciding which predicates to type into the Lisp engine [cite: 14]. 
Was it answered? Ken Forbus and Dedre Gentner responded extensively, arguing that modularity in AI is a necessary engineering abstraction and that SME's speed and systematicity allowed it to scale to thousands of domains, whereas Hofstadter's own architecture (Copycat) was permanently trapped in a micro-domain of letter strings [cite: 29]. However, the critique was never truly defeated; the modern failure of AI on visual analogy tasks like ARC is a direct consequence of our inability to seamlessly fuse low-level perception with high-level relational representation.

The Illusion of LLM Zero-Shot Analogy
Between 2022 and 2024, a massive research program emerged claiming that Large Language Models had developed emergent analogical reasoning capabilities. Papers claimed that models like GPT-4 could match human performance on digit matrices and story analogies [cite: 30, 31]. 
This claim is currently failing to replicate under strict conditions. Lewis and Mitchell (2024) demonstrated that when classical analogy problems are slightly varied in ways that maintain the exact same abstract structure but shift the surface features away from the LLM's pre-training distribution, human performance remains stable while LLM performance drops sharply [cite: 4]. Furthermore, LLMs are highly susceptible to answer-order effects and paraphrasing in story analogies, proving they are relying on surface statistical cues [cite: 4].

The Function Vector Artefact
In 2024 and 2025, researchers attempted to find the mechanistic representations of analogy inside LLMs. Todd et al. discovered "Function Vectors"—compact representations in the attention heads that seemingly encoded rules like "antonym" or "capital of". However, Opiełka, Rosenbusch, and Stevenson (2025) proved this was largely a mirage [cite: 5, 16]. These Function Vectors are not invariant; they change completely if you alter the input format from open-ended to multiple-choice. They capture the low-level format of the task, not the pure abstract concept [cite: 16]. When forced to process truly abstract structural concepts like "previous" or "next" in novel domains, LLMs lack any invariant linear representation, explaining why their analogical reasoning fails to generalize [cite: 16].

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the tacit knowledge of the field, building another text-based prompt harness for an LLM is a dead end. Attempting to scale up LLMs to solve visual analogies by feeding them more tokens will NOT work; Camposampiero et al. proved that increasing reasoning tokens by 3.4 times did not prevent o3-mini from crashing to 17 percent accuracy under perceptual uncertainty [cite: 6]. The model lacks the architectural prior for systematicity.

A well-resourced newcomer should focus exclusively on bridging the perception-to-structure gap through Neurosymbolic integration. 

Experiment 1: The Differentiable Systematicity Prior (Rank 1)
Build a neural architecture where the final layers are explicitly constrained by the mathematics of the Structure-Mapping Engine. 
Feasibility: Modern frameworks like PyTorch now support complex differentiable optimization layers (e.g., CVXPY layers or Sinkhorn-Knopp). 
Measurement: Train this model on the ARC dataset. Measure its sample efficiency. 
Falsification: If the model requires just as many training examples to reach 80 percent accuracy as a standard Transformer, then the SME systematicity constraint provides no useful inductive bias for gradient descent, falsifying the utility of hard-coding classical structure mapping into deep learning.

Experiment 2: LLM Activation Patching with Classical SME (Rank 2)
Extract the internal activations of an open-weights LLM (like LLaMA-3) during a story analogy task. Use Representational Similarity Analysis (RSA) to isolate the "Concept Vectors" [cite: 5, 16]. Instead of letting the LLM generate the final text, project these isolated Concept Vectors into a discrete predicate vocabulary, and feed those predicates into the classical SME4 engine to compute the mapping.
Feasibility: Mechanistic interpretability tooling (like TransformerLens) makes isolating and extracting attention-head activations trivial today. SME4 is available to handle the symbolic mapping [cite: 18]. 
Measurement: Measure accuracy on the Webb et al. story analogy benchmark, comparing the hybrid model against the base LLM.
Falsification: If the SME4 structural evaluation score completely fails to distinguish between analogous and non-analogous stories when fed LLM-derived predicates, it proves that the LLM's internal Concept Vectors are too entangled or ungrounded to serve as reliable nodes in a relational graph.

Experiment 3: Abductive Scene Graph Mapping on ConceptARC (Rank 3)
Replicate the ARLC neuro-symbolic probabilistic abductive model [cite: 9], but instead of applying it to Raven's matrices, apply it to the ConceptARC dataset. Use a vision-language model to generate a vast, noisy probabilistic scene graph of the ConceptARC grid. Use an abductive reasoning engine to prune the graph down to the subgraph that maximizes Gentner's parallel connectivity.
Feasibility: Vision-language models are now fast and cheap enough to generate massive zero-shot scene graphs, and abductive solvers (like ASP or the ARLC codebase) are available [cite: 22, 32].
Measurement: Generalization accuracy on ConceptARC across the 16 distinct concept groups.
Falsification: If the abductive mapping engine fails to generalize across the concept groups better than current multi-modal LLMs (like GPT-4 Vision), it suggests that visual analogical reasoning requires a continuous, dynamic re-representation of the image (as Hofstadter argued), rather than the pruning of a static, pre-generated probabilistic graph.

**Sources:**
1. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5NxAA_g4J5yp91gOTYaSlZk2CfYB3WePD2i4F0XGmw2Gg5r-VPOHICGqmBQuET5u3AGJEYFc3h1QDWmZAEAvB8dNmSQ8pslc_hUSBgiaAjMyVrcJuZZTUbx6R8dLfSLUz2sNpLf7eYNdS72TBrE5Eak_XhKFpVojLNRh7tEH-59DG7Ry7Q8aVPzWOKeyr1w77JpElS6MtLklOBfyUs9iVS4WjRx4S06oW10DcROnADEj21mRklDuP0g6SmssHKry7PAYHOg98)
2. [northwestern.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQES53hLBiKyXkmrnELPLeHY18Z1cXJ_LiGvEaoshV7rTmViPbNL1tiqGNUgXIZIzzpAz3k2cThiWdFoF4Hy50sPEJbc6xt9M3ZivDkE4TJRL4NA_6oMnvOgiCNZtbIOU4XES7nhgOz352xJXN_OQwjZkIlAah3NGc8OaH4gJanlKJuiTsR13VOC07-bSrLh9Z6USUw=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcui9XSlInZQ5SNmSzm0oUd--KTYI7JCDXyJu9IO7Jw_dbHFXkOp8hmU5ywr467tKwFaOU2AinymGzGy-SXH4QUjj3PcMU_QCKBc3z2GALC8_Xw1VMOg==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTmkyoeN68EbdlhOy78gcKQZ5jwiIJnvLNBzOLMVd4nMTpq1T5BypsAdq2wqlSRm044q88Q9ERF2h4620Dsv_AHAWI1_tAaCjqB5I8zH4vkELBVEYD5A==)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYCtDcc9J3tY5Aj3RiAt0fakjYTEsjuKTBDawOmuPrirLOSLGCs-QGNFy29heVp9R865P_vzmTfDJniOANWAKoAE0o4y3_artRa0Cp6NzAGfC7iZpPJ_qPoL7AaJYjHpWaXpI0XkEw2O7gEtNMWd1QhbtRWI8zwdfzSDhBjQRFTBWvxroB8Zze2Iu2tEGckL-CV7a3rgsIl8M8XEhfCV5lOSkcVpbuGPBlfWiQx7hT4160t230M4ImzqR6kuk7PPJszeDAWm5Z2gI=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIR9H5CcFMRAf7DbaPh3kyMSyTyGoCRHC9YatA25LQeD5zwXOPRrBDjevUjNsF107HX7PQDYfolrVMW13OmHlun0EX_S4GPyJvw64tCPy9wut2GR0sse8n5A==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0VCWVcVg8vxF25MSGC06EiqhMDLDj3ttvGs-_igikz4_-5NX4mVWS2Bq2uhtvzySyOjrYQ7dnhvpi3BEeR6ysrLCHmq_iOM_piOsIYz-zbGV95-qXzw==)
8. [githubusercontent.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0ouUKLdCSb5LArGkA5YkgeVb1nwNVMVAFunR1oQxWV4LnMp6F3Nj9sLWSx3IZqs7PWHkDJUGG_5MmKb7uV_f0EBFWtiO7RnZEifquM0YKbGzX5Z5dve0fFJFeL03s7173cm_psun6KsjOMhDIBr6R2ds6iWYzC9zrSP59gmrF6QvTi-hf)
9. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFj8mJkprnLFzlMwhFL5paddmyL-AzRO08c21Imcnf3Mmb781JsPYaE_id6X2uGsZML3afUj1D_qY-UbB5jSqZ89cchoTbqtzqVI_7kYAFboaTxz9SDYnJaHIDsWpiid87F88y0rHoy6v4_TCvtHQ==)
10. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-2h46VYsuTtIktPguQPXbB21J_wqEgx8CRbwqYL2PPNhU7WOnR-Xa05MNHcmlhsTY2SvzztWYK8sdI_SQw9MrX6gCxTlbffeg4HaFbnwdp63bjZT_zSTzkK28x7d6aXE=)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfCfiW_giX2wny7nKDHkXVjtVWjmxuABxLAVA9r--VIFIGbAz7AmPyjYSbXl1GNDjZJa-Hue2_UbI_Naao8EpZc7v_9_wltOo2cqpZ61QAytiP5kLV9gojdpgLA2YVklPf7TCV92q8TdkhtH4ReC73Fz9I3gPRgaLJhwy0x8oItSGec-M2RIQf25LzE0r_bTfkVxyCVUaO5J9HH5yul4J7vBjpevrCkK9-UBerVTD50fDBYbzLh6XQHXsvXZjcn9Y=)
12. [cognitivesciencesociety.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEL0tXYUyO0sXaH9yNvpkjHF5NnTUCRcDJGeJWAEMb-N5_m1GSmFCarJsZXHYg3XWj03Uejvh5SZRA-EaAegu2OFHEqvyQiusap6VBRkUGm_n1yuVsHmrkK4CiMfeupIBRz8rdiJ5P8BqNf)
13. [consc.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFIAdfyyLCiuWurFYqoWZSPEnQ-m3vCNLP8sT6Y6QGG4O8vka7b9AYYXtt7ML60DQPMumgYO_do6n2Wn8xx0DQbjbdN_T2hYKfVtty2IQOdFfR6rABh2t9vftZbB4=)
14. [jfsowa.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExyDImmZGNapiEnX_R2IsPoiPSNhEh5yZoj2AewfUwxYr51XuV5kix60Uen8kjTbgU52nGJpO3y5VA5qJPYCOcQDUaRFzo6gc9_j843TTAt62Glx11kAG0bdX1)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3c5k3iZyd_3EtqnnP_2PGgq_SfhcjTSJ0LfdzsEacjKXGRknAP-y3YOT69RU2Hz8RZNcGeamQnnwIdHYGkt53pMWhwo7n5NUwN3pWV1ZBt5B6l3dx_zlHZg==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH75cy9vB3dug-u03MqTjIcYa0OKAx3Ph-BBoj2wrjTFtiSH1ipvAksyKMnDmnABQjxKak6ABWFvqvDyFcTyT3LtkSSb1jDzWlg_up8k5qPDCCfMjYPOjAYJw==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhjuvFQlsM2-1O18WQkQWd6gbBKbyvhAG7cAjcW1m5iovZl3rI7ZBueLGOtXekSXMAxfe8LjNue6CBDBzdGiQgevFcKncauHBleG32YVLOEcWk6lTjNguQhg==)
18. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG26sTqGywph9Lb1E9udIgoJYxNcuXolMuvZ5yF4Y-cUdHrBRJmij4dDtKCOeT01erWWXTQkj_nV_3aUp-fZX7aXrYzxsSnPJbrWQxuRktjn2pVdcj_Yw==)
19. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYM8xzts9f-koROU0tnGHikWLH7Z--qUMgEscfZ1H-urLT81M5IpX2wXaa_633oH5P7GDDcoj3NxbG00oqbEHbBGMLygGBUwTSibNCN6hg8uR3jsrq1T-hf8Aq2k8=)
20. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjBcJZ_VwSWeX8J_xYyt1hCY9VHSUHCIBBgF4FWmHHi6Jgzg8Ht9cj4jHOC_YpGdG_nB8WxOWfuLZTONJfpALb-jTAy_WmA_yb979LkYkzP-Rzx8T_)
21. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFazIuBo2hZHmyPMPm2_HyHyDGBzmBFn4h5sYrCWljs0A4Z_TVlMRLUcP0vbBD7gVGUE1aabMzkSzSmsdhI0xUgM_N0kdKH0e3836KHd1AWGzLK2xwj)
22. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGseKm9ETQRGPVSLezHQVcz4PzS0ekvkm3MTyhxtymuTR_DFpsDZH83xkRkmbv9Fnqu584JwaLOUETbjAC40Ms350vN49ezO1FRmo955yzg8Pg60pStchbOO0bDW9ZHycCaTHZmWlAxBQ==)
23. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnci8TNmjyxrYsC3du_9v3oyCPjhO_fvz0-5BtRj6HqhYMBOPVu0CE6G-XjBvCry4J75qyugMiyFvx6l2cDUcZ3SK5Q3lrzK3kbzb_d6b969ZJ0b5MEo360d05KwqpYyM=)
24. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQ89Cw3WP5SEqjmkH5uCspfyKK9yeaRmQjIhP11v7REhWIzZntpLcda4dc-AvskIIvJs3QfMbo5L0E_4hJPAFBK30jf7S-4TA7ltTAmGH7BT75NNCbvOBk2-vGm83WXyuiWcxQzWCGNzRD2Za40jVKLWwUNwEZKRAHogYT4g==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuzc_0dSplLKD4ZOTBiqR5gPH3dSJgRhzQLmbBYFmAbb6SZYSUUV9ZfcuviaLt3b5rgNsFQrsbhyhzz39f9kCfpZCS8xbJ58_BnrhnuGDmJiFOxGp68r-89w==)
26. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBfFYPYVlHpvUsW5bDi_P_EE6PrMpBSHygYjfgluu4HBv93Wv-HHvUoTBtqvzMK7WvGrpESTQYuZrR-ewFjbe44-1MMIxHPLnD3d5leUniqy-Ri5XL84ZExf9rGOcncUf6k1Bgxch0IQ==)
27. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgOgqSSjC9V2xoSXKc9VkxAPXvdlftVnMvxnhakqOVn9FUaUp_AD5UbPDgd1f5SOtvBUlbrcmHzkUi0BwkUryxKDaIoviLSWxA_RmTja-cGlnLH2O8Qf9xLeGh0mpvUMbOGs64sYjW4mOUamNUD_dLDF2hNleppQQLFwb7coQsgqjWUzLjy0OsFDsbqBix7f-1PCSqQJH_NXJERIeiEKSbzCL5yvWI3g20VDs=)
28. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhprS838Km7M4p3ttf_z07vy6BDOyALcz9tXQknV7dajjok-3ZCg1u1IomiZkDNDzJR483RDwqXA6EO25leFn3wvzWv9t9CVOILFYUqdcQbT4qN2ByD0TSwWD6NGR3-_bl5ABjFIgG5w==)
29. [northwestern.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHe5ZaNC4XkWAgMiPqfSuFSQP6we0KrWemhMuBpOoeGttxI9ob6TVtOW-vRFWB4-7XWGyu2pSsSAocc01DMrHd7088QutfEuOAjcg8zPBEb8wEHN5gm3B-7vyj8JYFug7MQKExbLOtHHpoh6yk4EsdqrqM09DCA3LbsGPMD3PpQ0XdXESPpW_Zi1DINoCGCVg==)
30. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEhldleRB0ut-qmVQGgG-iCYxUsHEyCCtqtTtko4lFCf73SBY316OfcZrAnaH8_q2mKHbBbCUvAesq7VD9-vFkUh_WDCkVdt94D_UJZE9sAxJ73O2WCrUVEOpJFl49bV1W3ARq9OS7jHvqLEBbA520JRGFDas2yrBgCTFuEJAS0dV_xStxnvlyMHPbTs7gj1t7Pj20OMU2OTbkbD8Aam3EfsPgEjkCip_4yx0EZSCTyWUthI-xrm70s9NsSaDdIbNxq6Mj-ytIpL3yOIgdBCuZ9WJgnireYT_oLpGinvPyhFUQLUWuo7_ecNAeHViyiDhtbuP1XwzoYcv8CQSSZ0XI7oLQk6r85UMb)
31. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4SWHxcdBaSoaMLRZuBCaD-McTXXjIVJMFqcrTAx5H-H0CTc4kUnzSGfZ5IOLBQGdseaaailoOXjJgMB4BzNYCr9xd56RPJerg3d2Xi9M-ZxK1yCXK0LmvuLJC6dwcLxttEtNRTe350bNy6Yv0zsHnvuM=)
32. [tudelft.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTgSKzKCk9cYAlvRnkGsBbh3bH3KLFniGyjjUHfYY-p07WXUB8YIPcAU2qiEzEDQVXQyTmJn3PsidEMnetWgg9yEy19K9aGh39GdMCOXgSLfj00WLArf8DNNFbyMTJJOhKJRTQyNTEYhXc5X69w1gfB_dAHMifqOIJIy6XisP-rw8iNIpKvoIxwMdFTA==)

