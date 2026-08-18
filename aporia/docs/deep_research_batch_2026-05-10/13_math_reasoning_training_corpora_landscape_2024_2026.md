# Prompt 13: Math-reasoning training corpora landscape 2024-2026

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdRRDRCYW9DRk44emVfdU1QOUk2VW1RaxIXUUQ0QmFvQ0ZOOHplX3VNUDlJNlVtUWs
**Elapsed:** 757s

---

# Project Prometheus: v1.0 Learner Model (Ergon Agent) Math-Reasoning Corpora Survey

**Key Points**
*   **Scale and Quality Divergence:** Modern mathematical pre-training relies heavily on web-scale extraction (e.g., OpenWebMath, MathPile), yet model reasoning capabilities are ultimately unlocked by high-quality, curated, and instruction-tuned datasets (e.g., MATH, GSM8K) with dense computational anchors.
*   **The Rise of Synthetic Augmentation:** Standard human-annotated datasets are being rapidly eclipsed by synthetically bootstrapped corpora. Techniques like Forward-Backward Reasoning (FOBAR), Program-of-Thought (PoT), and iterative tool-use trajectories have proven essential for scaling instruction data without massive human labor. 
*   **Formal Verification as a Supervision Paradigm:** The integration of formal theorem provers (Lean, Isabelle, Coq) as absolute correctness verifiers is redefining reward modeling. Step-level optimization (e.g., STEP-DPO) circumvents the limitations of holistic reward models by isolating logical fallacies at the exact point of failure.
*   **Untapped Domain-Specific Reservoirs:** While general arithmetic and undergraduate-level proofs are well-mined, vast structural databases in algebraic geometry (The Stacks Project), number theory (LMFDB), and topology (The Knot Atlas) remain highly underexplored for training LLMs in deep, structural mathematical intuition.

**Overview of the Math-Reasoning Data Ecosystem**
The pursuit of advanced mathematical reasoning in Large Language Models (LLMs) has transitioned from purely autoregressive next-token prediction on raw web data to highly structured, rigorously verified, and algorithmically augmented pipelines. For the Ergon agent under Project Prometheus, establishing a v1.0 training corpus requires an intricate balance between expansive pre-training data and dense, high-signal reasoning trajectories. The current landscape is categorized into foundational raw corpora, synthetically expanded instruction sets, and verifier-backed preference data. 

**Anchor-Density-First Design**
A central thesis of modern mathematical corpus design is "anchor density"—the relative frequency of rigorous mathematical structures (formal theorem statements, logical proofs, and systematic computations) compared to expository prose or boilerplate text. High anchor density ensures that the model learns the structural mechanics of mathematics rather than merely mimicking the linguistic patterns of mathematical discussions. The following report provides an exhaustive, seven-section survey of the mathematical data ecosystem, profiling major corpora, augmentation strategies, verifier integration, anchor densities, domain-specific databases, state-of-the-art training pipelines, and anti-anchor flags to inform the development of the Ergon agent.

## 1. Major Existing Math Corpora

The foundation of any mathematical reasoning model relies on the ingestion of diverse, high-quality corpora ranging from grade-school arithmetic to postgraduate-level formal proofs. The following table and detailed analysis profile the major existing math corpora regarding their scale, licensing, and anchor density.

| Corpus | Scale (Tokens / Problems) | License | Primary Anchor Density Profile |
| :--- | :--- | :--- | :--- |
| **MATH** | 12,500 problems [cite: 1] | MIT [cite: 2] | High computation, high informal proof |
| **GSM8K** | 8.5K problems [cite: 3] | MIT [cite: 4] | High computation, zero formal theorem |
| **MiniF2F** | 480 problems [cite: 5] | MIT [cite: 6] | High formal theorem, high formal proof |
| **ProofNet** | 371 examples [cite: 7] | MIT [cite: 8] | High formal/informal theorem and proof |
| **NaturalProofs** | 32K proofs, 14K definitions [cite: 9] | CC BY-SA 3.0 / MIT [cite: 9, 10] | High informal theorem, high informal proof |
| **MathPile** | 9.5 Billion tokens [cite: 11] | CC BY-NC-SA 4.0 [cite: 11] | Mixed: high expository, moderate proof |
| **OpenWebMath** | 14.7 Billion tokens [cite: 12] | ODC-By 1.0 [cite: 12] | Mixed: high computation, high expository |
| **ArXiv-Math** | ~28 Billion tokens [cite: 13] | Various / ArXiv [cite: 14] | High informal theorem, high informal proof |
| **Mathlib (Lean)** | >100,000 theorems [cite: 15] | Apache 2.0 [cite: 16] | 100% formal theorem, 100% formal proof |
| **Coq stdlib** | Core Library scale [cite: 17] | LGPL [cite: 18] | 100% formal theorem, 100% formal proof |
| **Isabelle AFP** | >12,000 theories, 65GB XML [cite: 19] | BSD-style / LGPL [cite: 18] | 100% formal theorem, 100% formal proof |
| **AlgebraicCombinatorics**| Domain-specific publications [cite: 20]| Academic / Open Access | High informal theorem, high informal proof |

### Informal Problem-Solving Datasets
**MATH**: The Mathematics Aptitude Test of Heuristics (MATH) dataset comprises 12,500 challenging competition mathematics problems (7,500 training and 5,000 test) spanning algebra, geometry, number theory, and probability [cite: 1]. It is distributed under the MIT license [cite: 2]. Anchor density is heavily skewed toward step-by-step computations and informal logical proofs utilizing LaTeX formatting, making it a critical benchmark for advanced mathematical reasoning [cite: 1].

**GSM8K**: Grade School Math 8K consists of 8,500 linguistically diverse, multi-step elementary math word problems [cite: 3]. Distributed under the MIT license, it focuses entirely on basic arithmetic operations (+, -, ×, ÷) requiring 2 to 8 steps to solve [cite: 3, 21]. The anchor density is strictly computational, completely lacking theorem statements or abstract proofs, but it serves as the foundational benchmark for evaluating chain-of-thought (CoT) reliability [cite: 3, 22].

### Formal and Translation Benchmarks
**MiniF2F**: A cross-system formal mathematics benchmark consisting of 480 exercises drawn from the AMC, AIME, and IMO competitions [cite: 2, 5]. It is translated across multiple formal systems including Lean, Isabelle, HOL Light, and Dafny [cite: 2, 6]. Licensed under MIT, its anchor density is overwhelmingly concentrated on formal theorem statements and verification-ready proofs [cite: 6].

**ProofNet**: Designed for the autoformalization and formal proving of undergraduate-level mathematics, ProofNet contains 371 examples drawn from pure mathematics textbooks (topology, real/complex analysis, abstract algebra) [cite: 7]. Each example is a triplet: a natural language theorem statement, a natural language proof, and a formal theorem statement in Lean 3 [cite: 7, 8]. The repository carries an MIT license [cite: 8], and its anchor density is strictly theorem/proof-oriented.

**NaturalProofs**: A large-scale, multi-domain dataset containing 32,000 theorem statements and proofs, alongside 14,000 definitions and 2,000 axioms/corollaries [cite: 9]. The data is sourced from ProofWiki, the Stacks Project, and published textbooks [cite: 9, 22]. It bridges the gap between raw text and formal logic, offering a high anchor density of informal proofs and theorems [cite: 9].

### Massive Pre-training Corpora
**MathPile**: A diverse, 9.5 billion token, high-quality math-centric corpus aggregated from textbooks, arXiv, Wikipedia, ProofWiki, and StackExchange [cite: 11, 13]. Adhering to a "less is more" philosophy, it underwent rigorous language identification, cleaning, and deduplication [cite: 11, 23]. Due to the inclusion of non-commercial textbooks, it is licensed under CC BY-NC-SA 4.0 [cite: 11]. The anchor density is highly mixed, balancing dense mathematical anchors with significant expository prose.

**OpenWebMath**: Comprising 14.7 billion tokens across 6.3 million documents, this dataset was extracted and filtered from over 200 billion HTML files on Common Crawl [cite: 12, 24]. Released under the ODC-By 1.0 license (subject to Common Crawl ToU) [cite: 12], it utilizes specialized pipelines to preserve LaTeX formatting and remove boilerplate HTML [cite: 25, 26]. The anchor density leans heavily toward computational discussions and expository text from forums like StackExchange and math blogs [cite: 24].

**ArXiv-Math**: Sourced from the mathematics subset of arXiv, this corpus is frequently integrated into larger datasets (e.g., Proof-Pile, which contains 10GB of arXiv math, or TxT360 which contains up to 28B tokens) [cite: 13, 14]. Due to the density of LaTeX special characters, token counts are exceptionally high [cite: 27]. The anchor density is overwhelmingly skewed toward advanced informal theorems and proofs.

### Formal Library Corpora
**Mathlib (Lean)**: The user-maintained library for the Lean theorem prover, containing over 100,000 formalized mathematical results (lemmas, propositions, theorems) [cite: 15, 28]. Distributed under the Apache 2.0 license [cite: 16, 18], Mathlib represents the gold standard for formal anchor density, consisting entirely of verifiable logic, tactics, and theorem statements [cite: 28].

**Isabelle AFP & Coq stdlib**: The Archive of Formal Proofs (AFP) for Isabelle contains over 12,000 theories and locales, exportable as 65GB of OMDoc/XML semantic data [cite: 19]. It is available under BSD-style and LGPL licenses [cite: 18]. The Coq standard library (now part of the Rocq/Coq split) provides foundational Gallina-based mathematical formalizations under the LGPL [cite: 17, 18]. Both offer 100% formal anchor density, making them critical for training neural theorem provers.

**AlgebraicCombinatorics**: While not a centralized monolithic dataset like Mathlib, corpora derived from specific subfields like algebraic combinatorics represent highly specialized academic text (e.g., enumerative combinatorics, graph theory) [cite: 20, 29]. The anchor density is dense with domain-specific theorems, but the lack of unified licensing and standardized formatting makes automated extraction challenging without dedicated autoformalization pipelines.

## 2. Synthesis-Augmented Corpora

The bottleneck of human-annotated data has necessitated the development of synthesis-augmented corpora. By leveraging frontier models to generate, rephrase, and execute reasoning trajectories, researchers have exponentially expanded the scale and diversity of mathematical training data.

### MetaMath
The MetaMath framework generated the MetaMathQA dataset (comprising 395K data points bootstrapped from GSM8K and MATH) [cite: 30, 31]. MetaMath utilizes several distinct augmentation strategies to enrich the training set:
*   **Answer Augmentation:** Generating multiple distinct reasoning paths for a single question using few-shot Chain-of-Thought (CoT) prompting combined with temperature sampling to ensure diversity [cite: 32].
*   **Question Bootstrapping (Rephrasing):** Increasing narrative diversity by utilizing LLMs to rewrite existing questions from multiple perspectives while preserving the underlying mathematical structure [cite: 30, 32].
*   **Forward-Backward Reasoning (FOBAR & SV):** MetaMath pioneered backward reasoning augmentations. In Self-Verification (SV), a question is rewritten into a declarative statement followed by a backward reasoning prompt. In FOBAR, the ground-truth answer is appended to the problem, and an unknown variable within the original question must be solved for [cite: 32]. This significantly improves the model's robustness against benchmark hacking and memorization.

### MAmmoTH
The MAmmoTH models are trained on the MathInstruct dataset, and its multimodal successor MAmmoTH-VL utilized 12 million multimodally enriched entries [cite: 32, 33, 34]. The core augmentation strategy relies on **Hybrid Instruction Tuning**:
*   **Chain-of-Thought (CoT) & Program-of-Thought (PoT):** MAmmoTH synthesizes both natural language CoT rationales and executable Python PoT rationales [cite: 33]. GPT-4 is used to generate missing PoT rationales for existing datasets (like AQuA and TheoremQA) [cite: 32]. This dual approach allows the model to dynamically choose between semantic reasoning and computational tool-use depending on the problem's nature [cite: 33].
*   **Self-Filtering:** Generated responses undergo rigorous quality filtering to remove hallucinated or irrelevant content before being integrated into the training corpus [cite: 34].

### ToRA
The Tool-Integrated Reasoning Agent (ToRA) relies on the ToRA-Corpus (initially 16K highly curated examples based on MATH and GSM8K) [cite: 35]. ToRA's primary augmentation strategy focuses on **Interleaved Tool-Use**:
*   **Interactive Trajectories:** GPT-4 is prompted to generate solutions that interleave natural language reasoning with Python code blocks and their execution outputs [cite: 36, 37].
*   **Output Space Shaping:** To encourage diverse reasoning and eliminate improper tool usage, multiple trajectories are sampled per question. Invalid trajectories are passed through a "teacher model" for correction. The final training set combines the original valid trajectories with the teacher-corrected trajectories, drastically expanding the model's exploration of plausible reasoning paths [cite: 32].

### DeepSeek-Math
The DeepSeek-Math pipeline utilizes a synthesized instruction-tuning dataset of 776K examples covering English and Chinese [cite: 32]. 
*   **Knowledge Point (KP) Combinations:** DeepSeek utilizes generative models to extract implicit and explicit "Knowledge Points" from seed datasets. By combining these KPs, novel problems are synthesized across various difficulty levels [cite: 38].
*   **Multi-Paradigm Reasoning:** DeepSeek-Math data interleaves CoT, PoT, and tool-integrated reasoning formats. Furthermore, during Reinforcement Learning, it relies on generated responses scored via Process Supervision (rewarding each correct logical step) rather than merely outcome supervision [cite: 32]. 

**What Works?** 
The consensus across these synthesis strategies is that simple data replication is insufficient. **FOBAR (backward reasoning)** forces the model to understand bidirectional algebraic relationships. **PoT/Tool-use interleaving** offloads brittle arithmetic to deterministic external interpreters, reserving the LLM's capacity for semantic logic. Finally, **Output Space Shaping / Rejection Sampling**, where models learn from corrected failed trajectories, acts as a powerful regularizer against hallucination [cite: 32, 36].

## 3. Verifier-Paired Corpora

Standard Direct Preference Optimization (DPO) and Reinforcement Learning from Human Feedback (RLHF) often fail in mathematical reasoning because holistic "outcome-based" reward models struggle to assign credit to specific intermediate steps. Verifier-paired corpora address this by tightly coupling language generation with step-wise verification.

### STEP-DPO Preference Data
The **Math-Step-DPO-10K** dataset is a high-quality preference corpus containing 10,000 step-wise preference pairs [cite: 39, 40]. Standard DPO evaluates an entire answer holistically, meaning if a model makes a single arithmetic error in step 8 of a 10-step proof, the entire trajectory is penalized. This causes "advantage collapse" and fails to provide fine-grained supervision [cite: 41, 42].
*   **First-Error Isolation:** Step-DPO treats individual reasoning steps as the fundamental unit for preference optimization [cite: 39]. The dataset explicitly pairs a set of correct preceding steps with two candidate next steps: one correct and one incorrect [cite: 43]. By optimizing only the *first* erroneous step, the model learns pinpoint logical accuracy [cite: 44].
*   **In-Distribution Generation:** A critical finding from Step-DPO is that preference pairs generated by the *policy model itself* yield better results than data generated by GPT-4 or humans [cite: 39, 45]. Out-of-distribution GPT-4 data forces the model to mimic alien reasoning styles rather than correcting its own inherent biases. Step-DPO on Qwen2-72B-Instruct achieved 70.8% on MATH and 94.0% on GSM8K with only 10K pairs [cite: 39].

### Attached Formal Verifiers (TP-as-a-Judge)
Beyond LLM-based preference models, recent SOTA pipelines employ absolute formal verifiers. The **Theorem Prover as a Judge (TP-as-a-Judge)** framework integrates interactive theorem provers (like Lean 4) directly into the data synthesis loop [cite: 46, 47].
*   **Reinforcement Learning from Theorem Prover Feedback (RLTPF):** Instead of relying on human annotators or larger LLMs to grade math outputs, the generated proof sketches are autoformalized and sent to a theorem prover [cite: 46, 47]. If Lean compiles the proof, the trajectory receives a positive reward; if it fails, the precise error message (e.g., type mismatch, unsolved goal) is used as a negative reward or as a prompt for corrective reflection [cite: 46, 48].
*   Datasets generated this way (e.g., Kimina-Prover training sets) offer perfect step-level soundness. This eliminates the "Soundness Gap" observed in LLMs, where a model arrives at the correct final answer via mathematically invalid intermediate steps [cite: 5].

## 4. Anchor-Density Profiling

For the v1.0 anchor-density-first design of the Ergon agent, it is crucial to understand the structural composition of the pre-training data. We define four categories:
1.  **Theorem Statements:** Formal or informal declarative mathematical truths, definitions, and axioms.
2.  **Proofs:** Logical, step-by-step deductive chains (formal code or natural language).
3.  **Computations:** Arithmetic calculations, algebraic manipulations, and executable code algorithms.
4.  **Expository Prose:** Contextual framing, historical notes, navigational web text, and pedagogical fluff.

Based on dataset documentation, the following is an estimated fractional profiling for the top 5 corpora discussed:

| Corpus | Theorem Statements | Proofs | Computations | Expository Prose |
| :--- | :--- | :--- | :--- | :--- |
| **Mathlib (Lean)** | 30% | 70% | < 1% | < 1% |
| **ProofNet** | 30% | 70% | < 1% | < 1% |
| **MATH** | ~ 5% | ~ 15% | 60% | 20% |
| **MathPile** | 10% | 20% | 30% | 40% |
| **OpenWebMath** | < 5% | 10% | 45% | 40% |

*Note: Percentages are approximations derived from the structural intent and source distribution of each dataset [cite: 1, 8, 11, 12, 28].*

*   **Mathlib** and **ProofNet** represent the absolute zenith of pure anchor density, devoid of expository prose. Their tokens are exclusively dedicated to establishing propositions and proving them via logical tactics [cite: 8, 28].
*   **MATH** is highly computational. While it contains logical derivations, its core structure revolves around solving for a boxed answer via sequential algebraic or arithmetic steps, with expository text limited to problem setups [cite: 1].
*   **MathPile** and **OpenWebMath** are massive web-scale corpora. Despite rigorous filtering, a large fraction of their tokens consists of expository prose (e.g., textbook explanations, Wikipedia introductions, StackExchange conversational formatting). Computations and proofs make up the middle bulk, with pure theorem statements being relatively rare compared to the surrounding explanatory text [cite: 11, 12].

For Project Prometheus, if the goal is an *anchor-density-first* curriculum, data should ideally be upsampled from Mathlib and ProofNet for deep logical structure, transitioning to MATH for computation, and heavily filtering MathPile/OpenWebMath to strip out the 40% expository prose overhead.

## 5. Underexplored Corpora

While datasets like MATH and GSM8K dominate leaderboard evaluations, they primarily test grade-school to competitive high-school mathematics. Deep structural mathematics relies heavily on specialized domains. Vast, highly structured databases exist in number theory, algebraic geometry, and topology that remain severely under-mined by current LLM pipelines.

### Number-Theory: LMFDB
The **L-functions and Modular Forms Database (LMFDB)** is a massive, collaborative encyclopedia of modern number theory containing over 1 billion ($10^9$) concrete mathematical statements and data points [cite: 15, 49]. 
*   **Content:** It catalogs complex arithmetic and geometric invariants, including elliptic curves over $\mathbb{Q}$ and number fields, modular forms, Galois representations, L-functions, and their intricate interconnections (e.g., the Langlands program) [cite: 49, 50].
*   **AI Potential:** The database is highly structured, and researchers have already used machine learning on LMFDB data to predict the Q-gonality of modular curves and detect elliptic curve ranks via deep convolutional neural networks [cite: 50, 51]. Recent grants aim to bridge LMFDB with Lean 4's Mathlib, autoformalizing these 1 billion statements into verifiable theorems [cite: 15]. For the Ergon agent, parsing the LMFDB's raw structural tables into natural language/formal pairs would yield an unprecedented number-theory reasoning corpus.

### Algebraic-Geometry: The Stacks Project
**The Stacks Project** is a monumental, open-source collaborative textbook and reference work covering algebraic geometry and commutative algebra [cite: 22, 52]. 
*   **Content:** It operates on a unique "Tag" system, where every definition, lemma, proposition, and proof is uniquely identified, allowing for a deeply interconnected graph of mathematical dependencies [cite: 52, 53]. 
*   **AI Potential:** Datasets like *AlgGeoTest* and *Proof2Hybrid* have recently begun utilizing The Stacks Project to generate proof-centric multiple-choice benchmarks [cite: 52, 54]. Because the text is strictly pedagogical yet mathematically rigorous, it provides the perfect substrate for training LLMs in high-level abstraction, category theory, and scheme theory without the noise of raw web data [cite: 53, 54].

### Knot-Theory: The Knot Atlas
**The Knot Atlas** is an online wiki and database storing authoritative information on mathematical knots, links, and their invariants [cite: 55, 56].
*   **Content:** It utilizes RDF (Resource Description Framework) data dumps to store complex topological invariants such as the Jones polynomial, Alexander polynomial, Khovanov homology, and hyperbolic volume for hundreds of thousands of knots [cite: 56, 57, 58]. 
*   **AI Potential:** Prior neural network research has utilized The Knot Atlas to predict the hyperbolic volume of a knot directly from its Jones polynomial with 97.6% accuracy, probing deep, undiscovered topological connections [cite: 57]. Injecting this RDF data into an LLM training corpus would establish dense, graph-based anchors for topological and geometric reasoning.

## 6. Recent SOTA Training Pipelines

The current frontier of mathematical LLMs is dominated by DeepSeek, Qwen, and Gemma architectures. Their training pipelines have converged on a trifecta of scale, synthetic instruction tuning, and advanced reinforcement learning.

### DeepSeek-Math
**Corpora:** Pre-trained on a bespoke 120 billion token mathematical corpus extracted from Common Crawl. A fastText classifier was used to aggressively filter out non-mathematical HTML, preserving LaTeX and code snippets [cite: 32]. 
**Augmentations:** DeepSeek-Math-Instruct is fine-tuned on a 776K example dataset covering CoT, PoT, and tool-integrated reasoning formats across English and Chinese [cite: 32]. 
**Evaluation & RL:** DeepSeek's breakthrough relies on **Group Relative Policy Optimization (GRPO)**. Unlike standard PPO which requires a separate, memory-intensive value model, GRPO computes the baseline from the average reward of a group of multiple outputs generated for the same prompt [cite: 32]. By combining Outcome Supervision (final answer correctness) with Process Supervision (step-by-step logic), the model achieves competitive results on MATH and GSM8K using a fraction of the parameter count of legacy models [cite: 32].

### Qwen2.5-Math
**Corpora:** The Qwen2.5-Math pre-training corpus (Qwen Math Corpus v2) exceeds 1 Trillion tokens [cite: 59, 60]. This massive scale was achieved by utilizing the prior generation model (Qwen2-Math-Instruct) to synthesize vast amounts of high-quality mathematical Q&A pairs, aggressively expanding the pre-training data beyond what web crawling could provide [cite: 59, 61].
**Augmentations:** It heavily relies on an iterative self-improvement pipeline. During supervised fine-tuning (SFT), a Reward Model (RM) evaluates massive sample batches from the base model, utilizing rejection sampling to keep only the highest-scoring CoT and Tool-Integrated Reasoning (TIR) trajectories [cite: 61, 62].
**Evaluation & RL:** Similar to DeepSeek, Qwen2.5-Math implements GRPO. The reinforcement learning phase optimizes the policy objective using normalized advantages and KL penalties, enabling the model to tackle extremely long-chain reasoning tasks and Olympiad-level problems [cite: 59].

### Gemma-Math (MathGemma & Distillations)
**Corpora:** MathGemma models (and community variants like `qwen-to-gemma-math`) utilize high-quality reference corpora such as MathPile and GSM8K train splits [cite: 63, 64]. 
**Augmentations:** The pipeline relies heavily on **Knowledge Distillation / Behavioral Cloning**. For example, open-source efforts prompt larger teacher models (like Qwen3-plus) at temperature 0 to generate deterministic, step-by-step CoT traces. These traces are rigorously filtered for length, answer presence, and lack of repetition, then injected into the smaller Gemma model via LoRA [cite: 64].
**Evaluation & RL:** Beyond distillation, Google's internal pipelines for math (e.g., AlphaProof) integrate Reinforcement Learning over formal environments (Lean 4), while recent algorithmic advances apply Direct Q-learning Optimization (DQO) to allow Gemma models to learn from offline, negative, or unbalanced trajectories without the strict holistic holistic boundaries of DPO [cite: 65, 66].

## 7. Anti-Anchor Flags

If "anchor density" measures the presence of rigorous mathematical structure, **Anti-Anchor Flags** are the heuristic signals used to detect and filter out tokens that degrade mathematical coherence. In the context of building a v1.0 training corpus, recognizing and purging anti-anchor data is as critical as sourcing the anchors themselves.

1.  **Semantic Mismatches and Implicit Gaps:** In autoformalization pipelines, LLMs frequently omit implicit assumptions present in natural language (e.g., failing to specify that a space is Euclidean when assuming the $\ell^2$ norm, defaulting to $\ell^\infty$ in Mathlib) [cite: 67]. Datasets exhibiting high rates of compilation failure due to unresolved dependencies or missing variable declarations carry a high anti-anchor flag and must be discarded or sent for teacher-correction [cite: 48, 67].
2.  **Unreasonable Math Problems (UMP):** Recent benchmarking (e.g., the UMP benchmark) has revealed that LLMs struggle to detect mathematically flawed questions (e.g., scenarios with undefined variables, illogical physical states, or contradictory premises) [cite: 68]. Anti-anchor flags must be deployed during synthetic data generation to detect when a model generates a hallucinated or contradictory problem statement [cite: 68].
3.  **The Soundness Gap (Guessing):** On datasets like IneqMath or miniF2F, models often hallucinate an informal proof but guess the correct final numerical answer [cite: 5]. If a pipeline uses purely "Outcome Supervision" (checking only the final boxed answer), it risks ingesting massive amounts of anti-anchor data—where the logic is fundamentally broken, but the answer is coincidentally correct [cite: 5].
4.  **Formatting and Boilerplate Overhead:** Web datasets (like Common Crawl) are plagued with anti-anchors such as navigational menus, generic Wikipedia disclaimers, and broken MathJax/LaTeX rendering. SOTA pipelines (like Nemotron-CC-Math) utilize tools like Lynx and localized LLM-based standardization to strip this HTML boilerplate, ensuring that `\frac{a}{b}` is not degraded into disjointed plain text [cite: 69, 70]. 
5.  **Verbose Deflection:** When confronted with complex or unreasonable inputs, reasoning models (such as DeepSeek-R1) sometimes exhibit a specific anti-anchor behavior: generating overly verbose, repetitive, and meaningless "thinking" blocks that fail to converge on a logical deduction [cite: 68]. Filtering algorithms must flag trajectories with repetitive n-gram loops or excessive token lengths without mathematical progression [cite: 64, 68].

By meticulously profiling corpora for high anchor density, leveraging step-wise verifier feedback, integrating deep structural databases like LMFDB, and aggressively filtering anti-anchor flags, Project Prometheus can establish a profoundly robust v1.0 mathematical reasoning corpus for the Ergon agent.

**Sources:**
1. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6o1kEEfZVPXkn74kqkt4bFF5KBlPE5JM-L5mXYpN9Wwjk_JmdgtX0Rw4_jiTb8cDAtp83Hzs5LLHZtFscOjRrccBo29Vj2tWkEl6glrd3V5mRiE7ok6eRAAVPnOH3cBiyYZ2EkeXG0p8w2L_ar0hbOpsrrtbmbtM8s0iGd_2kgAppf8x1XPRNjpw-WLLJi69FRQYYhoFboEkgoW7PcZOJMPPbLCJ3QDQ_-bZUELdvCrxwjJvSL75_UEOPirN_1uL3JjPfMr2U)
2. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxrf2I-oH-Yrxye63s79VRzczbthe6zXW699VrrEeAXE2o9LCAD_zcLaZEmJWXabIUr6VbfmFb6zq7Fwx2bsM-RCr33qwmIfkeOyaJ09asKk95V4XGs9A_gI7hyWfx2bHiFgU=)
3. [kaggle.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGv1mjUeKUZpOzqjIXbVFviUD3glb5zkXm5Ru8Xtot-ChbnzHj3MDEfkuHISV3MsVI9RyrvXmELC9P6Q86dLBYnzG9TriCB7h83IEpy11z88z3GtQh9C9YMgh4KwVhTklVYdisSP-CfpPDh0yfJ1tFLaje4eNihJXTXagLLCuTWcGn2rY5YAxXj7sA8Gw==)
4. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEn-OQegGtKzwi_Uu81VZrfYZIFT1itHEU6KQtx4rxd4ouwbZBU0PBOk26nF1KgyR3l02njcl9Xm3j1iEHfpewcIqjNQNLX-IiYHvyVi2ivSLvAGk1F1382jmeu4So8EgQUDQ==)
5. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKeoKp0JywVCe1iPANXD0s7WH32YtjKUhe5tCvJgC93kmngWzl5RaLrB1Tvb0fAN-etj5r-eXqDu_ot5LMs516E0XvH2WdTpVhP3jYu4wnbz7r1-ew1LKaWvzIqq-b89pa0LIuAUo4kjbV32hiEbarz7GbkOk=)
6. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEgEn3bljUui23r63Wlti10p4G0mbgXbrXZBIfWQT4qUN0V6ScD0aLNtel2A3kSm4yWt33HSZQrzpkftY_rwjjCrtlWF_24ivEkzIbU-LJZZn7fHjazRiY77PW)
7. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSaAsZU7Cwr7laGxfDkJept2c2KQIzKWDaA4qMHLE5pd4hLu5ToQdkJ70n5ilq6pdiQaPsemlizKdt0pTFmLmawmYJ7H5KDQMGTu0qhP29rC2HJ3FUBGdl40cU_F3_gAKICQ4Kg-k3JgSPRYudWXM=)
8. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHC3vUE24JIB4A1pb1_sV8zcR4c81lFPEh_b9J06r8P-qPdkdQ_XrxkXtAnD28sV68ggRtgzb4NhN9BY4Rh8pZmXK62Ms_D2KjGJAzGBB5lefde8ZRArmZlDWcBeN-t1zk=)
9. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZRwvPkZRZvCoIkOx_ud289e37F46-9TlTVuBBzTSrSsvjwVgSWap378j5TSlSO96OIgf5EcKTu21iNfM3wjr50gsNtg7IezWSEcsX0vUYRjzx9HTbL8WiqUWOYVZHv_KLAmFvGjufiqRHUcTjWuRpIBfJ6_mAJOq3XXUAiR7_IwqirphUC_2zx9reYPmbJWn-Q-5Yk9GLi4d8CUZb7KL2_YFT0MgfPBYwoA==)
10. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFN3dbytpeY8kcL3bKctlAxOfIma6lmv78dlJnfP3MvMXassReaaA6_SK8pT9QqEwNlk82EciyGVrO5hlLYCdSHU3_1P_UHxDA7Mh_DNAsA0Jhw4ZO8IzwQ0XwfApb9bdevvI1MTgZ2UFNETvoBTMQ)
11. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnb57uowQJSmd2KXx4cRxakpQ3zOh5ibry0W-mkJ6qThJ_KQnb_psne_1WtLrMthvItGvOx8wX0zOrkHaTLJk9JLqikDHnaTEsf0hns96B6kvvd3xPc4Sok0Ghxt_w)
12. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrZ2_mGTKEdLa4SwImGCFrKD1Z8-WXRaLOBd2vo9Oqyj1QdswTxMoE5rQaZDpaSnn4xgHHLZC-KJdKnO0KppVfbzuvXspJYXNPbQcTEM91hxRb9H552B3A-5w=)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFraSNCd6dYL4UKkjy--qJV2Z2LcOiu7KyDalFAqIwVcTO5_GRbXZAzyDgbcai0PuyfDQkd6x0vZV-ElCJFQjrJNtjmugsftrqxrC3vrd4qj5lKyrJKOfWwaJLX-1uUpMG5nYRXqyi6nHbqRLllGkAPZMGkpH4nl6GVYQMz8jFKTGbpHzfDuohtpZ90ZwpRWM_VXWDHk6WQI64i8Tu6wCNy9Hj2)
14. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvpSPeyO2bOD9U940WJagnJPjm54sJljCz1cXz9ORciW4ZDc-v8i-FQi5eH_Jo2_d97xEbF_LG0kc7TH7YMJkBd-G-SV3cgnTFsSHPsCJn2pz8g5AKCqP0kZ720m4rkLNugDuUDNhwZGcacprdNiD7_A==)
15. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3tKAb6I2n-3bUKrdXAn4bKF2VW2EpZjuULLNqopfQTuh0CHtv2g9UwWc0Bebj2cjEnHsBVuJSW1-2bbVA6F-rAIm-0fjcpg_ykBrARKO2yxMH1F-XbMWpgun8w6NnQM-lWbMifnlAfc8yZLcsbP25V_FJfEu5FnHbWEpAEpv4_rF3cQ01JlkpeQ==)
16. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4rt6A7NtO4s2olkmowbKsoY4cmTpHFPi28LXVMOZrHw9uCSZ1rbBDV4HM3OLGQwA9ZUWz40p5gn04O49yhZvQygkVZWtYLi7mzHajPU-gbWCclg1-U_2tsnoX4D-t)
17. [rocq-prover.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF77EGnR5dzfbhosoa92uJSkWMoS11q-fCebzWQsJ5Yhn3dwakk6_M5Q827Nl3HAmkfaMFfDcXonlcqwGFXNciCBGBfJptFNCI4EGhcnL7O4ePR5XpV1WcfGPTX0b1DRmOtg_FRabcmnd8sAQ==)
18. [cam.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwM0gjh0yaMy79QuLSO8Dw0q6-v9ewG-hrGkWuRvkFus7QHGfkCg_FMX19-8yURkPTYs_4K5IjCY222dwpXfZic3rq7y824q_Fk2j-7dC_489gJy3CdQ_6N5WOEPH1P2hXqvFztfGoBG6yx448puEI7G0e8-uhzEu4OZBzRNJ4_y3aoiBwS5A17cDxQHHQLA==)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUrhcnUtBU2zofJUKcGSPv4o7UUR1SHIQj45CIgn_a4TydQiO5bzDc7ZNSGyk-aiW1rZDAmV9fwCuPuQr6uZBat8wkXffhOKFSgIft-W34_CD1dNhSuOhG8ySyFg6XIbSaOvDpLDbnNU8FgtspyOK4xGhpRzdwtesMfYmtWUk6lvdxv2AhfIuZGBfSMZMYM_5a0fDl41-R91Cj49euq5iOiWseNLrIPoNYEXQVLZcK)
20. [crmath.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvYxctVBBvYLtQT4URL4gH7MdH9h-WHS90t6f_XY5FAYfSo6E0fPbh6FaqHWwE1eyq5r2npy4w6jZP_WoiNKN8vbhkh5GIUfZx74htL0wRRnB3Rq2_ieoXY2xX2Vp_IdzacJpTThr0McPyNfs=)
21. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8vlQwgxngsnTJhIC-1z6QVf97wkNND4RtKJfWXWmMPJc7URqAl02WnTbqs8hLdSi0bgymwpKZLVQozQSEIrAUTFDDsonKld8fa4jY66x1FGnW4VpJjCbC1Uc-V_dZXxBE)
22. [abaka.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMYic6Jib6MCXGqMuhIN_bukLY5agfXtYp8uoIYfAeLrnEMB9GLbddtDfDlZEAeEQWiC6XmudWixYQ-G_I1DcZKhdPkBy8LvtN7ZF7sPLCLF6mHAh5jbkHtmIfJsPUwnQ7Kq7v)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIM-hz5N1JKSek2-1UXuIxW3QqqBWfXy5O8IyHkZEzHfc8oQcbcM33ddgYJGtRg-kfq2n7uRnht6SLGyXUJ_hx_UFigPJYRYoX75Ueh9AQx9ivn9_r4PTUgQ==)
24. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpJlcPsjcD62IjXzUkHxhXGDAfM5fcpTN3SArqIkgCH1s7VznX1kbOrucSPJf59vyvFXUiNlbZDChJ0AI8sc92a9QelB53qLoFAfLS5cyG6IRpDl-OviYjwVRDZH8tGIG9Twu7esOCSnbhmDDxNmeg7VfRD8xs0WeRRBExbYqmTj1EPwhAqLRXxcUUUYho2_68H5m_7FH_V7DJRi6zsnFZlg==)
25. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYZpGnxaZZI14gBk3vtk_bSKlEVJxVoOMyKF8qkgApsnvG17LrlLYsEK4CDuO7mfBE14ewWahLkmFLd5aA4c6Z95NjIhVCkpsZwhnAifkp7SYRKlQzl5n8C6pYAyqczsU=)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGN3sns2lyMPSq82PV35U161fCF63JkYj66F1O05oH7hUbYz7MtKdcmjTE-PaxPhWGaQVV_6fOQUUO2KwtHP9DzCJnimkSkA56L_Pqu3o0DEnxcrGDYUA==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGB62U1GguWv5QP70LQbruGBZv19NwIpnj3pAIxS6wiBt_35IlxAZAmTxuOpxNZ4ehw2GeCAVMf7KBm2gwJ4wAutsFTMXOpNg0slP4yZ2o-ioY7Rna_Ldts3A==)
28. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgL4_Trsc3DdKjx_RPJww6dYLeylITk8X7e3RSrHJkKmBKKz-9SHSRxtOwLn8kzI_AKkx1PplcIpNndTerGAt9dNSGVcyFYq854MrlU6ff4DGAFdDAknEo9q7Fe8dOaNdKSMX_wVs=)
29. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvi8hczpXxSxCwfuSRUJlL0p1Dml01h2-4YK9QRqfBtV_TJqWzqHfzkJ_st6H0uTZrJFsqci4Y4We8S5WSooxVQDXRg8roMMIEKl-UsJc4FdqknaZ3d8Nd8j3tjGWZwdt0Pd85TjpUN6OqOpyFTqGSnOLGfYYZfRKoFKd1ADGs8UMMdMvhNbDcWdvR)
30. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0bSvbAZSKNZihYHdi3MIOnUEKsvt8TAd5Jrn_2gx7HZS5DqURMEywjXDttuKaqrkh7wyIKR66rbVtjoEOe0U4kAQH0JHfSZzRG8dRDiqv7dpLgsHofNaUZhqOcNbA4xzzIWBxpvkqMLKH)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE33_R-c_Bi3-4F8fvN7RyoE9s6PoLLiEKgtwYP4rBEGFFKY4fjedRyD_tHFrPqKGHoYyaLnlagZylsG2x0HKyVFUndo5mAB8c39Gxbb4bVqQa8MLpazg==)
32. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHt6ay2EGYMZM6EsLuwasV7urFuzalqvT78Qsra-eimDxpaBJbTcA8kjOVf3PvvyaJfN87zFN6M63erH6Q-mT27_0Tb5gCGWB-IsWS_fUqmJjTj3H4wO7nxE0Ag6is3LaaOT6ZbrUhkYduxlxeJsKNOSr0Wd4b0NiYyY-yIlSG9PNCAQkzzOAG)
33. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmX9d7-ky_bF1KmIEoe6R-OlLEKLEeabl4ShaM9q8RLQ2RFEd48TVMyHJgNVaKbT7Edm_-YH_jolGfNaEnw3jF577Zj5CYZYZqxG75nteZpt62JAtIw2MrtEFh5qkQyaw=)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_l76n1rvJDcpvgr1M1vejbRehtIlZ2MzCZWPIdl4SLglts9U3vvmHW7IVH0P1uG6qHHbNV67DZw3lUsm0T6duXqc4XiXp55dSjKqShdp47a-sQc34loZoaA==)
35. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3ffjJF4NubOsD9Z6kTush7cniE_hP_2Sw1_ADNaL-7L7BEQbs9WjnyexMp-F0Gs8NKn26xUlQWDXyMtzIcGDX9VLrsQCIQ5FJmuuIFm9HtWXcb2gHgjg=)
36. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnTo8ljkf3-gwHSThUti1Hb5hezn7wXLIcmeB5b8h3c0MEbv9pn3zVtitn2lx2S7BI4-0npm4k5ac2biO1tLLvYMNl5jkFnTDlAb6OtYDU5yr-850mqjm-DjoDnuIvB_A=)
37. [ijcai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFF0HVwy1JChtCJyokQf7wKXA_0RkQPlLd0--85lbJ5SrtreEqVEiPs009mQrKOhsdRrdfAyayRx31-LlQ4_oPfXT3-LnMAHKbDNsqJ4C2ntVyBAXaLxh7e_1Wb_wnxzlWHj1PS2A==)
38. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5VTejCMKmDzVAVcJavvUnUobKsmwFQwAfwAoDuRjwKchsNvmh9bRFrJsediC5AZ-utoETw3Aj5muf6qc-LY0xqY5bqVJM-M0Jud48j6-cWi--af6oLpwr6g==)
39. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErhJ9vpubXcoD0WBvbOt1-1Is98jvUERLwZU3WMl7qJMV7wXx9jOW-r46vzKCFhfm92A_EcVgyfLOXwlvdu0bdrkyV0ecwAuWHFHNuGyTGVJ45fpdf_XhJNnHb9YJ6O8Sl9BbibI5xqEdZxBqwCWN-dPjPIlLmXX4wtZOYT-Af6mdtEw8jR5uaER_C6e-55_kVbR2K6cBUDWKqaEhL5p9ent3ZBMDCGNf-KveQos8ZccEjCJJVvdwApbAWxGUute6WnG0=)
40. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUNkjKxuAD3HSyzL8Dg9JeAkls9SB9Z_-pJfOF6q0-zW36fQpjBCVSvygDuUu-DHxB90habF-uU1dERfwEBhEilE6MNw4v1RkPFE-HJKx6lNBsTE2cZ-mXHKsLoaG4SUo=)
41. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDbpv6Wt07uAidqlVnbiFFiomTVYY8w03cxegzeoxcbUeOek_UP1ILx8Fc1-jyuGAcVnWzoABI7SraLk97HX7ehb_Q10PLcff0uq59Z9oR0LAnQjFJZRm0nIUIpMJzaXQ=)
42. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTgM7zE1tzqXAZR33ReEPbASVrNMjxBmR5lZmQw8478Cd3XgnM4KabNHoWeD1Tw6Xn6vwIAO1joRzTq2I2m1Y4DlwKnxKijtBbhmsNh-i5tTlUN5_5dBhICBzFWLpZ-Pftb2uXr9gIxaPioDy8YjTrb681vhgar9cGw5XbM48uuJw7AxhcSSAGEAMznVRxyK0P0LUCYUTp_gZekBfBUmFQDYY4Xr9YnOtLFJ9uLhwVBMdBMjs=)
43. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYlyPI7I1PWALFm6f2Ihy3vw2TxfctiwMKKTr0Eq_sylWmv5h-6kFiiUW9T6F-pEaHWUN1CH64YNhfeMvn6V4vJUvS9iIkuRxzTP7GH1nkPfbCBSEIkA==)
44. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGg0JD7rgIdYyqj95YUcSVvWfHTRE_Y-k5kwfQt-ZKxp5JgnCP7P77HixXfiurTDjZ1QbuCDHOOkrJ-4vandJzohXkZcQm7Wbw_saeVktaHPK1y0QjypePwYg==)
45. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5SG4hFKJAfJzfafDyZLFXvpcZSqwPhbct3VhmlZaG6OnCv-RqWJpXRXw4oCJan95nwouz_J03uZ409ugjMcWxZvG634NQKN4EXXl02zmWUI4IEIaeTVALrmobEozs)
46. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyfRv5SFmg6JMDfQHGxX4XS4xcUoukqnCCN0U6mvfpobt-uuOXW1paGQWgSof94KWFaGQSkU23EGEv96JISrYJusN6wYn3Lsqrs0pwk3kcLKPa51dkm3ERAFGSAX4gdbaj9ROTAg==)
47. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGC4PqYzhpKvFrltbTM5vb1ay0hPXos5FcYK9RqOktyJtYBMCpSa1Yo_qE1-HT5ripIQV9DeMxhSH6XlbpqqwuTf3o4OCMlzKhtQV1_Izx-TmEZTqYRY8yIP7ynPVvcSbltPwXmtlA1pDlxEmOMUbPL0m5Q)
48. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3s7FscNuBPLYfhdMCovz5SZdL3PJpRysgh4DBDSZY9XO_18pSBa4Yk_55Xac8FcgTXTCHD_Tr2GAQyYh2Fe3XMv4O__APs6NSHRvrl9F0iTkYONDLDPrYXg==)
49. [lmfdb.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKglaMDnDNY6jHRvOC6w9xJ7ig4BEcZnTCKCdv_8pFUZDknKf5bcfU0UFKCjcNp8Hl3LF7IA3i24n7OCXGFAAeaFznto9ICS2RUHSs7F54FQyfuVtQjg==)
50. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAN-yMZtKXjB6PoBjd9ejpUlAPh4NTtwuuohozQ4Z2aWwOL81FZG755wXwWYoZtZWNttjSVXwhGXpPJtK-Kc_5q6oC4hJzO0lZtPT80rcTf6-KiTJHif2cF3WY3gP9)
51. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLxRc8rmACWDEc5Mq9uqPfZOEQKN2zE30sd70O0NsLpt3Z-LNhxmDKan6h5PwFPt-130cjGU-Bh5d9GICF30kK3UAt9jg78HoaAtdoxMBV-wYMdoyoIQ==)
52. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2P2VDpx1xClIqjaqZwWOIe8PQCun4ujZw9jQJUv-K1qNxJpK89xRS8C8tAvymhXBYP2f-KVRuI2i4T4aWboo_ZHtQFPc2_kR0R_hTcdwLmyNrDaRH7P7ozA==)
53. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsld4JtllDEHHdqQaMAqsLA0WFFfVXuWDJpdy8OVbmcZAjHZeyr67mL-OUKJgMafUEI6x8x5NGrbLf58h3_7fXEgVBPrNh7I7Jd8Q3N_6-WyfrfA==)
54. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCtndZ_EEf9N6d6LKKgoC4DU2-fIDHlf8qgLyEk3ba21kXrwhvfy491BBYLPTztjqkcST0oVD3tJd7XUVUzIvCPMPt6UZqwdMU66Ng7DUiTWG0Fi2WVF4X4z0wO6rg3ak=)
55. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhH1JCfXXoaf081uC--rn7HCN8YSAucSZ1wVQR4kUVJNRl4eODKijYXuBLiYmZP-eXqJVPogswSysDkED0MJRr7n5pvRY-YuqacHNeOr26qqY17Kywk7GREq2XpQFKFn8=)
56. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERZliG8TgZEPQKr4Y5SkJUajzhXofh3ymkGoLqzt29DR9ILGXxm5ydIDOHLu7FGCW3ZtczJnbK1iPply8fZ0NF90_e_xMxLvdwBvuHIFFhA6FSfrjExds2HXRhSBWqqjJXMIaM94xmx7dBhBOXxYyfHU2VUOHx7Yd5)
57. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-g580c75l5O1YCAsz4ScPJ7FgeQMRUlHI6lGI0RPGxPNZ9H0IXjfITIJ-TyUIVW1BqtY-kQV4Z6i5r0k0vDrJD8GR8NG75IAO1sgknV184ql-8DSKYw==)
58. [scipost.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2W6KLM7j_RmGtlvkg70Kq2YtqixRmG2LXjjRcp_BP9Bl0ypyyhqn_lp6L8zCSfO37eE91vGAxUEjTVDSKpjTzA0LMEH41C3NSEvJG7iY6ABfFLYa8oaFte-fbB2sTMzvdrA==)
59. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEThfDd8qRu9tn8f9DHIRxBmueA_ec0SD-0hmpPcy3aoMO7Sgc5BVDYRTC6_A5BtZLHiO8AC1RCbjelIEQ8KL8jY51WzrV8hV_FtUKgbdsPLcT33gVxnKreiR6wkZAbVtsdy8qRQfcV-_9wO350jQ==)
60. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyuEF4LO1l4ArdmYbekr0SMkLjakYVzKuiwy6xnOhXhIWwTzzU28X0VzvrJRbFuWViYsgt7CKs0QgQ4y2tYAY9dskEmW9k6sfKdf8sm0UBTnyWbFK22ZFbbG5UXgwRVv_r)
61. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwwgBFglr8kMo9WomWMXt0uhnP0jw2srL8wOuz_qeAWZQXsm0sK-CtvJWBgH_ZjyFLeUeKWTs0v4VMy4S_ZlX7SDM1Bqzp-NwUJntYgTmew6rFWqko9lcktg==)
62. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_IcFaAfSaLh3OaBS9F8xsE0j5eziQ3mr2r3SfnVCv3UgPIBjqy1sf3jT400NVjjEBORj6QPNDf2HmwqM6yzNfqDnylZXSPUZLc44WM-oaeXBWVW43qYXUxgwLFqaXY9-r_c3aBr0xoMKLYg==)
63. [vips.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEU4xxs6NgjH54i71B8cccuykN1CVTi8t3sEoEapMT6ALmlqLbPqukpLie8cakThqmZ1fWFAy-ysSilxYYQ0s84llove5bkFKu1xTQcWQcO-6BSbbiZmPPPnObLM0cFVTaYPbmTW6GPtFJ2UfRNmgrTD-hm)
64. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHybZzzPSqBqCogFiHkL0BnJnbLfGTkGUdVF0IEF-XeE2TXOw7grTJHou6XD-GRNVlMg2dsV7xcyx3cfSiIDn-8eIGD6SyU5W_ILh4C9pf1wtcSPqxlyjpfdayJy2UZv3IwDRJvBPB-O8w=)
65. [vips.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiPrxx5Ui1zrK83t8jAJ3pfhxMHH-myd7ljW306ZPGta0ZwEjbrCs4yM_L5lv2l09rHvPogdwvP6UfiRszY-0-dMDa0QpGDhqx87O_VHRm5CgS4Rz3VnXU7fZL3qUXgSp9Dg==)
66. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHftQOqyuT3twzhmuBXgtPUi2eE6kMe9VO0wbufyE-wjnyalsiF76c2tCVAuFZ3IkgFf5beeo20PQI8s3S5wjuLnQNsuY2EoVpRUi7XHDENxvWRH56mPvFfNg==)
67. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2i85DEd2s3doBdbrcoSOuelmIOS_CH94qaH84ODJPrGGdn8jaLneyJRTu7xGhuYPdWPNEi1eSLE3ByHr6KYTytUf6Sw7Qdwua8b3lY1x-RssFA5alKdPXxVlk--SRHPI=)
68. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUGwxpjvsj77MsNb-goQqtKshTfuq8tUkaisIB0nlFQnUtO0z9gkQrXOMb_AJHuFKk_jQbBYK1gIbzmSRf9E6S-07ZewFLZ7bheflS77ctloCsJr0wY-ECQ4tbdt-CSpUg0vwG9gM_vlO5j8qblqS_qrM=)
69. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXL7dvVoUs9kZ_hhmpsACfZ1l_W1sBSN5UhI9VIApJkysOlhHEk1DJa8MXkFicfPdpaNQ6ZINaYHPcxrayyClBLujtN-of451n6JyAtQ0dgjGTRNhy12abRg==)
70. [nvidia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJEcb0RxfHjy_gMEwh1tUEfy2YAa_HiAv-yp1_o5Xsig0JleJa7c8YryL-4uVHiJGVCs5HMfUaRZqVRsIfdH2rGFE1HxLnzrK3CWhr2ZcdDHF38X390ytQJfUkTT-PuLLMA36s1-X6NeBK313WpF7o1B2W8vjhrbDk_jXDcA==)

