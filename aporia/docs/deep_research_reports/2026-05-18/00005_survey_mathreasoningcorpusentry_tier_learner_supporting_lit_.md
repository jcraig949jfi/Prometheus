# Survey MathReasoningCorpusEntry Tier-Learner supporting lit (Mathlib + ProofNet + MATH + Step-DPO)

**Pythia queue id:** 5
**Tier:** 1
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chdpbk1MYXFpNEdhbUotc0FQX3JuZjZRbxIXaW5NTGFxaTRHYW1KLXNBUF9ybmY2UW8
**Elapsed:** 403s
**Completed at:** 2026-05-18T20:22:54.536866+00:00

---

# Survey: MathReasoningCorpusEntry and Tier-Learner Supporting Literature – Synthesizing Mathlib, ProofNet, MATH, and Step-DPO

### Leading Paragraph

*   Research suggests that the integration of rigorous formal mathematical libraries, such as Mathlib, with advanced machine learning benchmarks like ProofNet, effectively bridges the longstanding gap between informal mathematical reasoning and verifiable formal logic.
*   It seems likely that the deployment of massive, highly complex datasets—most notably the MATH dataset with its 12,500 competition-level problems—exposes the limitations of traditional language model scaling laws, thereby necessitating the development of more fine-grained, step-wise supervision methodologies.
*   Evidence leans toward Step-DPO (Step-wise Preference Optimization) providing a highly data-efficient and mathematically sound approach to overcoming the shortcomings of holistic Direct Preference Optimization (DPO), specifically in the realm of long-chain mathematical reasoning.
*   Tier-learner architectures—spanning multi-tiered educational frameworks, reinforcement learning transfer paradigms, and embodied pedagogical models—present a structured, curriculum-based approach to hierarchical skill acquisition that aligns seamlessly with the progressive complexity required for automated theorem proving.

The pursuit of artificial mathematical intelligence represents one of the most profound challenges in contemporary computer science and machine learning. To achieve human-level or superhuman mathematical reasoning, systems must not only generate plausible natural language arguments but also construct rigorous, formally verifiable proofs. This survey explores the critical supporting literature surrounding mathematical reasoning corpora (MathReasoningCorpusEntry) and tiered learning architectures (Tier-Learner). The report systematically examines the foundations of formal mathematics through Lean's Mathlib, the benchmarking of autoformalization via ProofNet, the evaluation of complex informal reasoning using the MATH dataset, and the optimization of step-by-step logic through Step-DPO. 

Furthermore, this report investigates the "Tier-Learner" paradigm, a multifaceted concept that permeates pedagogical theory, reinforcement learning, and automated educational systems. By synthesizing these diverse strands of research, we aim to provide a comprehensive understanding of how hierarchical learning structures can be applied to the staged acquisition of mathematical reasoning in large language models (LLMs). The subsequent sections delve into the architectural methodologies, empirical benchmarks, and theoretical frameworks that define the current state-of-the-art in this rapidly evolving domain.

---

## 1. Introduction: The Intersection of Formal Mathematics and Hierarchical Learning

The creation of an "automatic mathematician"—a computational system capable of autonomously posing conjectures, discovering novel mathematical truths, and rigorously proving theorems—has been a foundational aspiration of artificial intelligence since the mid-20th century [cite: 1]. Historically, the field has been bifurcated into two distinct methodological camps: symbolic logic systems that excel at rigorous verification but lack intuition, and neural generative models that excel at pattern recognition and intuition but struggle with logical consistency. 

Recent advancements have catalyzed a convergence of these two paradigms, driven primarily by the advent of Large Language Models (LLMs) and interactive theorem provers (ITPs). This convergence relies heavily on the curation of high-quality data corpora and the development of sophisticated optimization algorithms. At the core of this movement are several pivotal elements:
1.  **Mathlib**: The foundational, mathematically rigorous library of the Lean theorem prover, which provides the axiomatic grounding for automated reasoning [cite: 1, 2].
2.  **ProofNet**: A targeted benchmark designed to evaluate a model's capacity to translate informal, natural language mathematics into formal, machine-verifiable statements—a process known as autoformalization [cite: 3, 4].
3.  **MATH Dataset**: A large-scale corpus of competition-level mathematical problems that challenges models to perform deep, multi-step informal reasoning [cite: 5, 6].
4.  **Step-DPO**: A novel reinforcement learning alignment technique that optimizes the step-by-step reasoning process rather than relying on holistic, outcome-based evaluations [cite: 7, 8].

In parallel with these computational advancements, the concept of the "Tier-Learner" has emerged as a crucial theoretical framework. Drawing from educational pedagogy, cognitive science, and structured reinforcement learning, the Tier-Learner model posits that complex skills—such as mathematical theorem proving—are best acquired through a hierarchical, multi-tiered process of scaffolding and targeted intervention [cite: 9, 10]. By exploring the intersection of these computational benchmarks and tiered learning frameworks, this survey provides an exhaustive overview of the mechanisms necessary to cultivate robust mathematical reasoning in AI systems.

---

## 2. The Foundation of Formalization: Lean Theorem Prover and Mathlib

### 2.1 The Philosophy and Architecture of Lean

Formalization is the process of translating informal mathematics, logic, or scientific reasoning into a fully precise formal language that can be mechanically checked by a computer proof assistant [cite: 2]. In the context of modern mathematical AI, this involves writing exact definitions, stating theorems in symbolic form, and providing step-by-step proofs that the system verifies against fundamental axioms [cite: 2]. The Lean theorem prover, originally developed at Microsoft Research, has emerged as the premier interactive theorem prover (ITP) for this task, largely superseding older systems like Coq, Mizar, and Isabelle in the machine learning community [cite: 1, 3]. 

Lean 3 and its successor, Lean 4, provide a functional programming environment where mathematical proofs are treated as programs, and the correctness of a proof is verified through type checking (following the Curry-Howard correspondence). Lean 4, in particular, aims to provide an open-source platform for correct and maintainable code, allowing users to define theorems and prove them via tactics or temporarily bypass them using the `sorry` command [cite: 11].

### 2.2 Mathlib: The Digital Library of Mathematics

The utility of any ITP is intrinsically tied to the breadth and depth of its mathematical library. For Lean, this library is **Mathlib** [cite: 1, 12]. Mathlib is a massive, unified, and community-maintained repository of formalized mathematics. 

*   **Scale and Scope**: Mathlib currently encompasses approximately 2.2 million lines of code [cite: 12]. It constitutes the largest unified library of formalized mathematics in existence, covering extensive swaths of the undergraduate curriculum and selected advanced topics at the graduate level [cite: 12].
*   **Design Philosophy**: Mathlib emphasizes the most abstract and general formulations of mathematical results [cite: 1, 3]. Rather than containing highly specific, concrete problem instances, it builds a dense, interconnected web of general theorems and algebraic structures.
*   **Challenges in Expansion**: Despite its massive size, extending Mathlib's coverage to encapsulate a substantial fraction of the historical and ongoing mathematical literature would require growth by several orders of magnitude [cite: 12]. Furthermore, recent analyses indicate that after an initial period of exponential acceleration, the manual expansion of Mathlib by human contributors has stabilized to an approximately linear rate [cite: 12]. This bottleneck underscores the urgent necessity for **autoformalization** technologies.

### 2.3 The Autoformalization Imperative

Autoformalization is the task of automatically translating natural language mathematics (such as textbook prose, handwritten notes, or LaTeX source files) into formal mathematical statements and proofs within an ITP [cite: 1, 2]. The primary goal is to build a bridge between informal mathematical reasoning and formal, machine-verifiable logic [cite: 1]. 

The benefits of successful autoformalization are manifold:
1.  It renders proofs more trustworthy by eliminating human verification errors [cite: 2].
2.  It makes advanced mathematical literature semantically searchable and reusable [cite: 2].
3.  It extracts dense training signals from vast corpora of informal mathematical text, grounding language model reasoning in formal logic [cite: 1].

However, autoformalization faces severe challenges. Because the volume of parallel data (documents containing both natural language and its exact formal Lean translation) is negligible, autoformalization is essentially an unsupervised machine translation problem [cite: 1].

---

## 3. Bridging Informal and Formal Mathematics: The ProofNet Benchmark

To systematically evaluate the capability of language models to perform autoformalization and theorem proving, Azerbayev et al. (2023) introduced the **ProofNet** benchmark [cite: 1, 13]. 

### 3.1 Dataset Composition and Structure

ProofNet is designed to test the autoformalization of undergraduate-level mathematics. Unlike Mathlib, which focuses on abstract foundational theory, ProofNet tests the ability of models to apply those abstract results to concrete, specific problems [cite: 1, 3]. 

The benchmark consists of exactly **371 examples** [cite: 4, 14, 15]. Each example in the dataset is a triplet comprising:
1.  A formal theorem statement expressed in Lean 3.
2.  A natural language theorem statement.
3.  A natural language proof [cite: 13, 14, 16].

The mathematical domains covered by ProofNet are drawn from popular undergraduate pure mathematics textbooks and include:
*   Real and Complex Analysis
*   Linear Algebra
*   Abstract Algebra
*   Topology [cite: 3, 4, 14].

By focusing on the undergraduate level, ProofNet sets a much higher bar than previous benchmarks that relied primarily on high-school competition mathematics. The problems are selected to ensure broad coverage of the undergraduate curriculum, ranging from straightforward definitional applications to problems requiring deep, ingenious creativity [cite: 3].

### 3.2 Supported Evaluation Tasks

ProofNet supports multiple axes of evaluation for mathematical AI systems:
*   **Autoformalization of Statements**: Given an informal natural language statement, produce the formal Lean 3 statement [cite: 1].
*   **Informalization of Statements**: Given a formal Lean 3 statement, translate it back into readable natural language [cite: 1, 14].
*   **Formal Theorem Proving**: Given a formal statement, generate the formal Lean proof [cite: 1].
*   **Informal Theorem Proving**: Given an informal statement, generate the informal natural language proof [cite: 1].

### 3.3 Baseline Methodologies and Innovations

The authors of ProofNet established initial baselines using models such as Codex (Code-davinci-002) and GPT-J through in-context learning [cite: 1, 3]. Because standard LLMs lack exposure to Lean's specific syntax, the authors trained a custom model named **ProofGPT** (available in 1.3 billion and 6.7 billion parameter scales), which was fine-tuned on the "proof-pile"—an 8-billion token dataset of mathematical text [cite: 1, 14]. 

To improve beyond standard few-shot prompting, the ProofNet framework introduced two novel methodologies:
1.  **Prompt Retrieval**: This method uses nearest-neighbor search against a dense embedding database to dynamically construct prompts. It retrieves the specific Mathlib declarations that are most semantically relevant to the natural language theorem being formalized [cite: 1, 14].
2.  **Distilled Backtranslation**: A technique borrowed from unsupervised machine translation. It involves extracting Mathlib declarations, informalizing them using an LLM (like the OpenAI API) to create synthetic parallel data, and then fine-tuning a model to translate back from informal to formal [cite: 13, 14].

### 3.4 Evaluation Metrics

Models evaluated on ProofNet are judged based on several rigorous metrics:
*   **Compile Rate**: The percentage of generated Lean statements that successfully compile without syntax errors [cite: 14].
*   **Typecheck Rate**: The percentage of compiled statements that successfully typecheck against the Lean kernel [cite: 14].
*   **BLEU Score**: A measure of syntactic overlap between the generated text and the reference text [cite: 14].
*   **Accuracy**: A holistic measure of whether the formalization perfectly captures the semantic intent of the informal theorem [cite: 14].

*Table 1: Comparison of Mathematical Libraries and Benchmarks*

| Benchmark / Library | Focus Area | Format | Size | Primary Function |
| :--- | :--- | :--- | :--- | :--- |
| **Mathlib** | Abstract / General Math | Lean Formal Code | ~2.2M Lines [cite: 12] | Foundational Axioms and Theorems |
| **ProofNet** | Undergraduate Math | Triplet (Lean, NL State, NL Proof) | 371 Examples [cite: 4] | Autoformalization Evaluation |
| **FormalQualBench** | Graduate-level Math | Lean 4 | 23 Theorems [cite: 17] | Specification-based Evaluation |
| **MATH** | Competition Math | NL / LaTeX | 12,500 Examples [cite: 5] | Informal Multi-step Reasoning |

---

## 4. Evaluating Complex Reasoning: The MATH Dataset

While ProofNet focuses on formalization, the ability of an AI to conduct complex, multi-step reasoning natively in natural language is equally critical. This capability is benchmarked heavily by the **MATH Dataset**.

### 4.1 Dataset Origins and Construction

Introduced by Dan Hendrycks et al. in 2021, the MATH dataset was explicitly designed to measure mathematical problem-solving capabilities and to find the limits of Transformer-based language models [cite: 6, 18, 19]. 

The dataset contains exactly **12,500 challenging competition mathematics problems** [cite: 6, 20]. These problems are sourced primarily from elite American high school mathematics competitions, such as the AMC 10, AMC 12, and AIME (American Invitational Mathematics Examination) [cite: 5, 21]. 

Each problem in the dataset is annotated with:
*   **Step-by-Step LaTeX Solutions**: A rigorously formatted scratch space documenting all intermediate derivation steps [cite: 5, 6].
*   **Final Answer Format**: The final numeric or symbolic answer is isolated inside a LaTeX `\boxed{...}` tag for easy programmatic extraction [cite: 5].
*   **Difficulty Rating**: An integer scale from 1 (easiest) to 5 (hardest), standardized by the Art of Problem Solving (AoPS) [cite: 5, 21].
*   **Subject Categorization**: Problems are divided into 7 distinct subjects: Prealgebra, Algebra, Number Theory, Counting and Probability, Geometry, Intermediate Algebra, and Precalculus [cite: 5, 21].

### 4.2 Impact on Large Language Models

Upon its release, the MATH dataset revealed severe limitations in the reasoning capabilities of contemporary AI. While a three-time IMO (International Mathematical Olympiad) gold medalist achieved an accuracy of 90% on the benchmark, massive language models like GPT-3 scored approximately 5% [cite: 6]. This stark contrast highlighted that simple pattern matching and standard scaling laws were insufficient for deep logical derivation.

Over the subsequent years, performance on MATH became the gold standard for evaluating reasoning models (e.g., Google's Minerva, OpenAI's GPT-4, and DeepSeekMath). By June 2022, state-of-the-art performance had climbed to 50.3%, significantly outpacing forecasters' predictions [cite: 22]. 

### 4.3 Perturbation Studies: True Reasoning vs. Memorization

As models achieved higher scores on MATH, researchers began questioning whether the models were exhibiting true reasoning or simply memorizing training data patterns. To investigate this, recent studies have developed perturbed variants of the dataset, such as **MATH-P-Simple** and **MATH-P-Hard** [cite: 21].

*   **Simple Perturbations**: Slight modifications to the problem that preserve the underlying reasoning patterns and solution steps [cite: 21].
*   **Hard Perturbations**: Fundamental changes to the nature of the problem such that the original solution steps no longer apply [cite: 21].

When tested on 279 perturbed level-5 (hardest) problems from the MATH dataset, state-of-the-art reasoning models like `o1-mini` and `gemini-2.0-flash-thinking` suffered significant performance drops ranging from 10% to 25% on MATH-P-Hard [cite: 21]. This phenomenon highlights a novel form of memorization where models blindly apply learned problem-solving skills without assessing their applicability to modified contexts [cite: 21].

### 4.4 Example from the MATH Dataset

To illustrate the complexity, consider a typical problem format from the dataset involving piecewise functions and continuity:

```latex
Problem: Let \[f(x) = \left\{ \begin{array}{cl} ax+3, &\text{ if }x>2, \\ x-5 &\text{ if } -2 \le x \le 2, \\ 2x-b &\text{ if } x <-2. \end{array} \right. \]
Find $a+b$ if the piecewise function is continuous.

Solution: For the piecewise function to be continuous, the cases must "meet" at $2$ and $-2$. 
For example, $ax+3$ and $x-5$ must be equal when $x=2$. 
This implies $a(2)+3=2-5$, which we solve to get $2a=-6 \Rightarrow a=-3$. 
Similarly, $x-5$ and $2x-b$ must be equal when $x=-2$. 
This yields $-2-5 = 2(-2)-b \Rightarrow -7 = -4-b \Rightarrow b=3$.
Finally, $a+b = -3+3 = \boxed{0}$.
```
[cite: 20]

---

## 5. Optimizing Reasoning Processes: Step-DPO and Process Supervision

As established by the MATH dataset, long-chain reasoning requires a precise sequence of logical steps. Standard post-training alignment techniques, such as Reinforcement Learning from Human Feedback (RLHF) and Direct Preference Optimization (DPO), have shown remarkable success in general dialogue alignment but struggle significantly with mathematical reasoning [cite: 7, 23].

### 5.1 The Limitation of Standard DPO

Traditional DPO optimizes models based on holistic, solution-wise preference data. Given a prompt \( x \), a preferred answer \( y_w \), and a rejected answer \( y_l \), standard DPO adjusts the policy model \( \pi_\theta \) using the objective:

\[ \mathcal{L}_{DPO} = - \log \sigma \left( \beta \log \frac{\pi_\theta(y_w | x)}{\pi_{ref}(y_w | x)} - \beta \log \frac{\pi_\theta(y_l | x)}{\pi_{ref}(y_l | x)} \right) \]

However, mathematical solutions are highly sequential. A rejected answer \( y_l \) may contain 10 correct reasoning steps before making a fatal arithmetic error on step 11. Because standard DPO evaluates the answer holistically, it penalizes the *entire* sequence, inadvertently suppressing the model's likelihood of generating the perfectly valid first 10 steps [cite: 8, 23]. This lack of fine-grained process supervision introduces significant noise and limits reasoning improvements [cite: 8, 24].

### 5.2 The Step-DPO Methodology

To address this, Lai et al. (2024) introduced **Step-DPO** (Step-wise Preference Optimization) [cite: 7, 24]. Step-DPO treats individual reasoning steps as the fundamental units for preference optimization rather than evaluating the entire answer [cite: 7, 8]. 

The Step-DPO formulation operates as follows:
1.  Given a prompt \( x \) and a sequence of initial correct reasoning steps \( s_1, s_2, ..., s_{k-1} \).
2.  The algorithm identifies the exact point of divergence where an error occurs.
3.  It maximizes the probability of the correct next reasoning step \( s_{win} \) and minimizes the probability of the specific incorrect step \( s_{lose} \) [cite: 23, 25].

By isolating the error, Step-DPO provides highly targeted supervision. The authors developed a data construction pipeline that yielded a high-quality dataset containing **10K step-wise preference pairs** (the `Math-Step-DPO-10K` dataset) [cite: 7, 26, 27].

### 5.3 Data Efficiency and In-Distribution Preference

A critical observation from the Step-DPO research is that preference optimization is highly sensitive to the source of the data. The authors found that self-generated data (data generated by the policy model itself) is significantly more effective for Step-DPO than data generated by external or superior models like GPT-4 or humans [cite: 7, 8, 24]. This is due to the "in-distribution" nature of self-generated data; it directly targets the specific probabilistic weaknesses of the model being trained, avoiding out-of-distribution hallucinations [cite: 7, 24].

### 5.4 Empirical Breakthroughs

Despite using only 10,000 preference pairs and requiring fewer than 500 training steps, Step-DPO yielded extraordinary performance gains. 
*   When applied to `Qwen2-72B-Instruct`, Step-DPO achieved an accuracy of **70.8% on the MATH test set** and **94.0% on GSM8K** [cite: 7, 24].
*   This performance surpassed a series of highly resourced closed-source models, including GPT-4-1106, Claude-3-Opus, and Gemini-1.5-Pro [cite: 24, 26].
*   For smaller models, such as `Qwen2-7B-Instruct`, performance on MATH increased from 53.0% to 58.6% [cite: 26].

### 5.5 Evolutions of Step-DPO: SCDPO and Full-Step-DPO

The success of Step-DPO has rapidly spawned derivative frameworks that seek to refine process supervision further.

*   **Step-Controlled DPO (SCDPO)**: Proposed as an automated method for generating negative samples that begin making errors at specifically controlled steps. By taking the prefix of a correct solution and generating new steps with high temperatures to induce errors, SCDPO applies training loss only to tokens after the correct prefix, improving model alignment and avoiding reasoning pitfalls [cite: 28].
*   **Full-Step-DPO**: While Step-DPO successfully identifies the *first* erroneous step, it fundamentally ignores all subsequent or alternative steps in the reasoning chain [cite: 23, 29]. Full-Step-DPO leverages step-wise rewards from the *entire* reasoning chain. It trains a self-supervised Process Reward Model (PRM) to automatically score every single step without relying on external GPT-4 annotations [cite: 23, 29, 30]. A novel step-wise DPO loss dynamically updates gradients based on these continuous step-wise rewards, demonstrating superior stability and resilience on out-of-domain mathematical reasoning benchmarks [cite: 23, 29].

---

## 6. Tier-Learner Pedagogies and Frameworks in AI and Education

The mathematical benchmarks and optimization strategies discussed above all share an underlying philosophy: the acquisition of complex reasoning is not a singular leap but a structured, staged progression. This mirrors the concept of the **"Tier-Learner"**, a paradigm widely utilized across educational psychology, instructional design, linguistic modeling, and reinforcement learning.

### 6.1 Multi-Tiered Systems of Support (MTSS) in Education

In traditional pedagogy, tracking and tiered instructional supports are used to manage wildly different learner abilities within a curriculum. A standard framework is the Response to Intervention (RTI) model, which categorizes learners based on their need for support [cite: 31]:
*   **Tier 1 (Core Instruction)**: Standard grade-level instruction provided to all students [cite: 31].
*   **Tier 2 (Targeted Intervention)**: Supplemental instruction for students who fall below benchmark expectations [cite: 32].
*   **Tier 3 (Intensive Intervention)**: Highly specialized, intensive support for learners who severely struggle with foundational concepts [cite: 9, 32]. 

For example, a "Tier 3 math class" might take the place of standard mathematics for students who fail basic arithmetic operations or lack fundamental reasoning skills, requiring a slower pace and highly granular instruction [cite: 9]. In assessment frameworks like the OCR GCSE Mathematics, expectations are mapped across columns where a Higher tier learner's capability is cumulative, building upon the foundational competencies of a Foundation tier learner [cite: 33].

### 6.2 The EMPOWER Framework and Immersive Tiered Learning

The tier-learner concept has been modernized through AI and Extended Reality (XR). The **EMPOWER framework** (Embodied, Motivational, Pedagogical, XR-enhanced) guides the development of Embodied Pedagogical Agents (EPAs) [cite: 34, 35]. 

Within EMPOWER, a multi-agent AI simulator models learner behaviors using a tiered pedagogical alignment:
*   **Tier 1 Tasks**: Basic prompts for recall, comprehension, and reflection [cite: 34, 35].
*   **Tier 2 and Tier 3 Tasks**: Advanced, cognitively demanding activities such as physical simulation, synthesis, and complex spatial reasoning [cite: 34, 35].

The system uses algorithms like Bayesian Knowledge Tracing (BKT) and Q-Learning to adaptively unlock higher-tier tasks only when the learner demonstrates sufficient mastery of the lower tiers [cite: 34]. Prematurely attempting Tier 3 tasks without completing simpler tasks results in reduced credit, actively guiding the learner toward a structured path [cite: 34].

### 6.3 Three-Tier Learner Profiles in Medical AI Education

In professional and academic environments, tier-learner profiling is utilized to structure curriculum development. In the context of integrating AI into medical education, scholars advocate for a tiered competency model that categorizes learners based on their interaction with AI technologies:
1.  **Consumer (Core Tier)**: Focuses on basic AI literacy, utilizing AI tools responsibly, and understanding broad implications [cite: 36, 37].
2.  **Translator**: Acts as an intermediary, understanding both clinical needs and technical AI capabilities to facilitate integration [cite: 36].
3.  **Developer (Advanced Tier)**: Engages in deep interdisciplinary collaboration, algorithm design, and system architecture [cite: 36, 38].

This multi-tiered approach allows for differentiated learning pathways, ensuring that individuals receive training commensurate with their professional trajectory and cognitive readiness [cite: 36, 38].

### 6.4 Phonology and the Restrictive Tier Learner

The "tier" concept also extends to theoretical linguistics and natural language processing. In modeling phonological long-distance dependencies (where sounds interact across intervening segments), researchers utilize **Tier-based Strictly Local (TSL)** models. 

The **Restrictive Tier Learner (RTL)** is an algorithmic model that automatically induces only the specific phonological tiers necessary to capture these long-distance dependencies [cite: 39]. Rather than providing an innate Universal Grammar tier a priori, the RTL analyzes typological data (e.g., trigram constraints) to discover the "canonical tier"—the unique largest subset of the alphabet necessary to explain the dependency [cite: 39, 40, 41]. This model demonstrates that tiered representations can be computationally derived from raw data through an algorithmic learning process [cite: 41].

### 6.5 Tiered Reinforcement Learning

In the domain of artificial intelligence, **Tiered Reinforcement Learning** represents a parallel transfer learning framework. The goal is to transfer knowledge from a low-tier (source) task to a high-tier (target) task, reducing the exploration risk and computational burden of the latter [cite: 10]. 

Unlike traditional transfer learning, Tiered RL does not assume that the low-tier and high-tier tasks share identical dynamics or reward functions. Instead, it relies on a condition known as "Optimal Value Dominance" to ensure robust knowledge transfer [cite: 10]. By maintaining near-optimal regret in the low-tier task, the system can systematically assemble information from multiple low-tier sources to provably benefit the exploration of much larger, high-tier state-action spaces [cite: 10].

*Table 2: Manifestations of the Tier-Learner Paradigm*

| Field | Tiered Architecture | Primary Mechanism | Citation |
| :--- | :--- | :--- | :--- |
| **Education (MTSS/RTI)** | Tiers 1 (Core), 2 (Targeted), 3 (Intensive) | Differentiated instructional intervention based on cognitive deficit. | [cite: 31, 32] |
| **XR Pedagogy (EMPOWER)** | Tier 1 (Basic/Recall), Tier 2/3 (Synthesis/Spatial) | Q-Learning and BKT unlock higher tiers upon mastery. | [cite: 34] |
| **Medical AI Training** | Consumer, Translator, Developer | Differentiated learning pathways based on technological engagement. | [cite: 36, 37] |
| **Phonological NLP** | Restrictive Tier Learner | Induces canonical tiers from trigrams for long-distance linguistic rules. | [cite: 39, 41] |
| **Machine Learning (RL)** | Low-tier (source) to High-tier (target) | Knowledge transfer via "Optimal Value Dominance". | [cite: 10] |

---

## 7. Synthesizing Tier-Learner Architectures with Mathematical Reasoning Corpora

The diverse threads of Mathlib formalization, ProofNet benchmarking, MATH problem solving, Step-DPO process supervision, and Tier-Learner pedagogy coalesce into a unified roadmap for training artificial general intelligence (AGI) in mathematics.

### 7.1 Curriculum Learning as an Educational Tier System for LLMs

To train an LLM to reach the level of an automated mathematician, researchers implicitly employ a Tier-Learner architecture via Curriculum Learning.
*   **Tier 1 (Foundation)**: The model is pre-trained on vast, unstructured corpora like the AMPS dataset and the "proof-pile", acquiring basic syntactic competence and algebraic symbol manipulation [cite: 1, 18].
*   **Tier 2 (Informal Complex Reasoning)**: The model is fine-tuned on the MATH dataset. Here, it learns multi-step, logical deductions in natural language. If the model acts as a "Tier 3 struggling learner," making frequent logical errors, researchers apply targeted, intensive interventions like **Step-DPO**. Instead of failing the model holistically, Step-DPO provides highly granular, step-by-step corrective feedback, directly mirroring targeted pedagogical intervention [cite: 7, 8, 9].
*   **Tier 3 (Formal Verification and Autoformalization)**: Having mastered informal logic, the model advances to the highest cognitive tier: interacting with Lean and Mathlib. The ProofNet benchmark acts as the assessment module for this tier, requiring the model to synthesize informal intuition into rigorous, machine-verifiable code [cite: 1, 13, 34].

### 7.2 Agentic Reinforcement Learning and Tiered Transfer

Recent surveys outline the landscape of "Agentic Reinforcement Learning" for LLMs, conceptualizing models not merely as static sequence generators but as interactive agents navigating dynamic environments (like Lean) [cite: 42, 43]. 

This transition involves formalizing Agentic RL through Markov Decision Processes (MDPs) and Partially Observable Markov Decision Processes (POMDPs) [cite: 42]. Within this framework, Tiered Reinforcement Learning can be utilized. A model might solve simpler, high-school level formalizations (low-tier tasks) and transfer the learned policies and lemma extraction strategies to graduate-level mathematics, such as the FormalQualBench tasks (high-tier tasks) [cite: 10, 17].

### 7.3 The Process Reward Model (PRM) as an Automated Tutor

In the Full-Step-DPO and SCDPO frameworks, the Process Reward Model (PRM) essentially functions as an automated, highly attentive tutor [cite: 23, 28, 29]. Much like a human educator monitoring a Tier 2 math student's scratchpad, the PRM evaluates every line of the LaTeX derivation. It assigns dynamic, continuous rewards to each step, actively preventing the "memorization" of faulty logical leaps (a vulnerability exposed by the MATH-P-Hard perturbations) [cite: 21, 23]. This continuous, step-wise gradient update enables the policy model to develop genuine resilience and robust reasoning capabilities.

---

## 8. State-of-the-Art and Future Directions in Autoformalization and Mathematical AI

The field of mathematical reasoning AI is advancing at a breakneck pace, driven by the synthesis of the corpora and techniques outlined in this survey. Several cutting-edge developments dictate the future trajectory of the field:

### 8.1 Advanced Agentic Provers and Formalization Pipelines

While ProofNet established a baseline with 371 Lean 3 statements, newer pipelines are drastically expanding the scale of formal data. 
*   **Lean Workbook**: An iterative active learning pipeline that successfully translated over 57,000 synthetic math problems into Lean 4 formal statements, validated via Lean compilation and Natural Language Inference (NLI) [cite: 11].
*   **FormalQualBench**: A benchmark of 23 classical graduate-level theorems designed to enforce "Specification-Based Evaluation." Here, models are given only the verified Lean statement and must independently construct all necessary definitions, lemmas, and proof strategies using Mathlib [cite: 17]. This prevents models from bypassing the Lean kernel using unsound exploits [cite: 17].
*   **Breakthrough Systems**: Models such as DeepMind's AlphaProof, ByteDance's Seed-Prover, and Harmonic's Aristotle have demonstrated unprecedented capabilities. For instance, Seed-Prover achieved a gold-medal equivalent on the 2025 IMO problems using Monte Carlo Graph Search (MCGS) over Lean 4 proof states and step-wise lemma generation [cite: 44]. Furthermore, AI systems successfully formalized the strong Prime Number Theorem in Lean in just three weeks—a task that previously stalled human experts for 18 months [cite: 44].

### 8.2 Synthetic Data Generation and Look-Ahead Guidance

The reliance on human-curated datasets like MATH is yielding to synthetic prompt generation. Systems like **PromptCoT 2.0** generate highly diverse, complex synthetic mathematics prompts, completely untethered from human annotation bottlenecks [cite: 45]. When these synthetic prompts are combined with self-play and supervised fine-tuning, models exhibit dramatic improvements across multiple benchmarks [cite: 45].

Simultaneously, techniques like **Local Look-Ahead Guidance via Verifier-in-the-Loop** combine the philosophy of Step-DPO with real-time ITP feedback. Rather than waiting for a full proof to fail, the Lean verifier evaluates intermediate logical steps incrementally. This step-by-step local verification produces a global improvement in the model's formal reasoning accuracy and exploration efficiency [cite: 46]. 

### 8.3 Retrieval-Augmented Formalization

As Mathlib grows linearly but AI models scale exponentially, bridging the gap requires retrieval mechanisms. Tools like **DRIFT** (and the prompt retrieval baselines established in ProofNet) utilize dense embeddings to scan Mathlib for relevant premises [cite: 1, 47]. These models don't just retrieve axioms; they retrieve illustrative theorems to aid the LLM in understanding how to apply abstract Mathlib declarations to concrete problems [cite: 47].

---

## 9. Conclusion

The pursuit of artificial mathematical reasoning mandates a complex interplay between expansive informal datasets, rigorous formal verification environments, advanced step-wise optimization algorithms, and hierarchical learning methodologies. 

As demonstrated by the **MATH dataset**, multi-step informal reasoning requires models to move beyond statistical pattern matching into the realm of structured logic. Traditional alignment techniques like DPO fall short in this domain, necessitating targeted, granular interventions like **Step-DPO** and Process Reward Models to accurately assign credit and penalize localized logical fallacies. 

When informal reasoning is mastered, the ultimate frontier remains formal verification. **Mathlib** provides the axiomatic grounding, while benchmarks like **ProofNet** and FormalQualBench test a model's ability to seamlessly translate human intuition into machine-verifiable code. 

The connective tissue binding these distinct technical achievements is the **Tier-Learner** paradigm. Whether viewed through the lens of educational scaffolding, tiered reinforcement learning, or hierarchical curriculum design, the premise remains identical: complex mathematical intelligence cannot be forged holistically. It must be constructed step-by-step, tier-by-tier, ensuring that foundational axioms and basic derivations are deeply mastered before ascending to the abstract, formal heights of autonomous theorem proving. The continued integration of these corpora and optimization techniques heralds a near future where AI mathematicians operate not merely as calculators, but as verifiable, creative contributors to the corpus of human knowledge.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGO1QioMfBpRBHJBq7AdWnYxbL66nUKtaJ467uz7DJsbHwStkoUKl_fJNfKOgbuO39CpNCJyoj4oPe4-jLFF9jLNtqQNlx67luuNHJQ5iko-qGCp9rJ)
2. [utk.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyLUP8hvE7xmxG2v950u9LI0Q1cbGuDn9t_UX4GHJAjCuO1iqKrHLER-j2SrYRkpYobmFBfRaWxpQd12DRytEbikcrKTGgIM7vcGmiNsJ6Qdd0j8_muTSDzWuPe-gq)
3. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNqWJl4ClcbiUY6uO9KIwjouhz3tg4FpkgA-KLvxcmKNu0OTScIkga6wf5kV2gfVZyFyCm95Sge-U8HFqXrC-HvoUDHjjCLJI4RWG293ypqgNjrUWkSsmT26LKiKZq2w==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHG8t1Ki0bvdW4Vq8o1fYmvy9BgWI68Fq099pNDxxbXD21Xf46nFqa6xhWRHbHIsH9eX1QOM1y3uDqRzWhzNonaM7qvYDvxwBty-9dn6GXppuR_NBlT)
5. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjUm8kHdwH0TKl5LGqsiimelDYEmMW-7MKABldGLNExdZTqd4H-b0CIER3LzbqKBZu76SWh-GJuRHcON1_DyObayPQfXvyb0TtWonQ8NTW1j1IsNHYadci_K4rDaoxDDj0bIR5PQ==)
6. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMpqUGn--dju4VS2Calr4M24BoJ5R9bzXz2-PW5xXbqIgW-1zxB9h7frkmFLc3HoLGmJuJIUY6YXtxvB6byITi0cF1-ztgM2zaixDWMrTjSl1qVqNCnNdtSAJXq7d38Ew=)
7. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-patjixh2I7-MORjQpRlmatpAIX_NWBQoxhxnlJT8BvoPn8OwpDOPeEEb5FeFtHzRw_HbJAbLpgwAj-inHH-rheyMgRBksHPJRddjtCqtl6k4-impfanzhttZy1blQEwP4bUd8sENweKtPRu0jiwGcn2_bfBiBIa7B_F42czV09x2wbbNRYlbhlZl1ZYdwVEKEZ4WkJrxUOrV2jZGCyMBvyI3QNkPsJqh4x1USL3PEohk1IokXfigcPPvjTVQTJv6mg==)
8. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGt4evZj4iWVo2IRlDJK1KEl-oOfA8ZuVAcHnqpTb5kKpiIA30KeTDpgHcgTA7kZAvKvBkEvcVNfp0k1b6g7vqLtgUurvy6ooait1WOucNGazDhBOFzNQyEVkgiLGc=)
9. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhZoVpTkqkfugi4om4zbvHxJ9XHzbjFDXpojYQ-teIjUMYTxt14-lD8uAMHzZgU_soEjy0zUJzKK-EDT97qGE-CyuPlho7R_ujwSOJ0ngpKBa4D1Myldf9y577Yp2Amf0CMpZd3PW7Z1F8CEA-XnaHPFoXXK9ScOhRxa3m7TOc2mTsL6YleuT2HHaNgJr0sKRAMos4uCMXKLjD6g==)
10. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKxEuwx-h8dOxGAxFB7lEx_kYgQ1RtcRsNwDjTXTGTtzFaNyJmluNLiYeo8H727qCFB6oI4dkl1hanEEhr9086bTmjwcFVixGt7i7y8oFcVjvg53GZ4k0cOAqKZJumNA==)
11. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5kgQ4Swy9_RG0L7z0_GLdeWy5VQLT9YeppxTWuGzztcQuehwxeanG63WOm52h9-zFjx6amcXtV2lTIsh4FX-k1lXWRrTEoPju0NU8GBOxtFTvabjBnpADraioOIsSjZsG)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFw07tsHm7Eo7cnydrTDq_jSn2cDrwcD8cndS34e9JLd2Yabxg3TB4AtHPV6JBKnmnwJI-pssWzVvhChHOn7vf5f9qLzOqrUCvwkDWfx8_IFR1jWgz_SHAa)
13. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfa9mORML72AY-FQ5cou1UDu8VypX2ld3MsItMpCvhkjT9xtREYkWICiI2aNczoMteo_4hJE1tDk2gcUESAxpV-ULRmYU7i9tGyK6_6IPLDn42hKv0g7PNVcWhyyuxkzeV0g==)
14. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGq8BIfZCDUU0XxLqdrbGc7VTVCntpK6hnwICOJ9iealPAqn9LRr0XIAiy8FPdizCR5aY73-hmeQEhEVg0LzwIBqcEzh3fzs5TS8eN4azVsVpWnc1hXv432IXij75vM3A==)
15. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdz9TYNsfeLlkeVl2xNs5lng7JKOwcR8ojzvk4OUH2tSeIZ_6NfmrLAMF_fU7jCuoPx0ZVRwcx7c9I-qRPfSjclnaO6DANVvETr_ecxqu2FY5oyO1GrsxAfoonvCA=)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJsGg56GFyYLBV8gtw9uwRUy96HU5VCJnECE25t2YuV6wNcUXwgiMPiPYEO8bfwInwo37vrBrbRCk1hqdoeMHQr3hfSoa_DxvTCkSrMhR44Ew4SZJ8mS3T4TPvQtvEjFov_DwYLn2rTe4Cx0WlKswfhNb0_dtoRj669xC1LmJ2w_rZT72DQZIieRt4745v1aYQME2dAjL89lAyVHthgcBDAB80PKSmzLGeqYfFTenzzuXr8WAqPw==)
17. [math.inc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEemUUEVMyc8t6k1fisww4APwh8E5cnLeewgnKd9JKuVx0mjHIN7xuHKZpphmSDzrhTTZWjrR1W5eYibF04UBwWYbQ-uCR9cqeJjItwfLyFbs6wEtsJvswS7g==)
18. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGE_ZhRozSxFExzbksdj0ypFG0LE7qP_BpwKp8mvKvRYdOpFzBr_KdIppN-2-KPd8f5iDOiCu5GpOB9n3YfkBx4mi6qHyKB3GtqNVGD5MfjsTN0JnmCHw==)
19. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEacQujS-TtJxdNH6ixCfkAuB7loZLyDXX0HNCyTGpdy33iKYd753r8YsWCb86pht-N5eXfu-1lPvyh5MTLgT6dvU1BmLaULkoJ9MtGj4RS0Kno7hhh-P7y0Z_7uT9Fx5_7d_-5kqRKFCRWzv-_v6SDxjx1ZqmdmRuoakUSkIXD8S0bTJevg_PZblVkYUR27SiMnLWcZg7SLeo=)
20. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSEzrhQIHsbWau3nEN379TQ07-m_247n9leTkavmG3KQ4XKgWKOcf4re0AMoYOtPnlWAEMh-cOs8Fp0surgkgcDzXA6wEXwE625bb59ZoftiHCHdW8CXZfkZhXkr5Y2FnPx7HV0ofm_o3_pBW7fw==)
21. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5-PQcIhyhlBH-FcLBWRkCMr4lx3oOyMPtaS9FucS85lD6H5I177OQgF2snvHakTdn0imR6ZEekABWj6kzSd7Zu5nyxNyZz0qFtQQ32VBkbtPGLWVjfDYblHWs-sWL)
22. [ghost.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpenXq1ouRQ4_YcHscutMxgVBayKddEaYAaWPli6ChOnbdAI_LCOpTkn5sDbu7bmZaAXp0VF4BURJd_iIBziKu7BTiHkdjzGiwnrZZLN8RJh8SshTSU6MPXGyXAAsqx6B8u6CVYAKh8UFkMhOmSQ6VvQBVS6rmYA==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0vX6lLMC_J7V2XOpQy6Z3sN86N_g207joS9R61GJSNc65evpx5lLWYw323Du2iWxw_Mfcl8X_LvmJbeLsxmk1jvRknW8Oa0eDF1oig1RXAEOu3BlvmxrN)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwQNz00-ol0gyrTYlUT4xc4kFxWh-sYBYGzVvu2kTCa2OENC0trhE_eXOEjaFWAPDpCbJxKTari_bx7ryzwfSD2sYdr1UxGds79hMUk6Zllxz6Z4lB)
25. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-eDIR4fiHUAcm8t8J9JtBzcYjbcVhg0dXszr-kixob7YQAe43GFlp8JeZ5NQ975YrL9xStcmOhBhoXF98yWIacH3yO0r-jysS71ukMVw-F5QTPJawRYzIBD_s7jygifQrqcDYJxAg5GDxIQ-9QjBxYGBqSWdDS98wQGQGnlV2kdjsYCgAOgsvfTsO)
26. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuJgQ3TCs0LyX0vCdSsSSUN3tAxtjo1v87UrNV_SID58BIQmtOyfRJH6nHu17_FJ2o5aZbt7u7EnjhRognIYPOBHuvnNJgA3hXJpxY0W0rwQrPRIw4JSdX-zdHO30_UA==)
27. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9WI3TWo8ayFYD_FOVyekHSReUYphuCyyWNtiov5F4rZg0m70hi7PnONwWF2402nT_XGvY_rGMuKy5DkvU1hYG1C0pH1UJsWuf_rBUKjNTwBKWKAZJBB8Uwc0o3pn6Q223JUahkSWGY86r3Gx-)
28. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFulAxV5MO5nzDJk3Js6dIXxg_-zR2z3uPhUArrh-m-pcyLdUnUH1tfWOpm5k5GQLhSye93oeVtsBY8Knlc-2_Vy5mDnLVhB6LHt7zKQcRjg0VZZWFqa9lqyqid7lbkEA==)
29. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-eCiId70eBCpFIlKONh9Si8g86-jJiG1AEAXD8wfIDlPhUM3B_Sse1ka4F9xzWrI-CXYE7y9n5Bw7f_EV-gIZCDQRyvGKLBkTqOKqvtjZNVkuXpJuCsEs-5rAzYM3tEtBi3eXDhKVUw==)
30. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWHpXC7f-xlqtIzydOxgn4qylbYcsy7HmGS4GAq_JSFqO_f4DYqDhe2TJrtAOStQ-PfU2bBeqtVPlwlO1OJYES3NWjP-tZnAZb4kqc-7nzKpTGD3RmU85ta_wWb2Nrr7RbvnmNctozylROFz-vJH3cqlXC-UG_-Shtu_3uVjI_YGgbcSDwHTxytCifSZ7XT-eWzouLLD1TvpYN0QqTiCyLPL-P3_zhJxUqjie019tR2E9oCdUJdBYogJQ_ztFwnZ0rFOg=)
31. [finalsite.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1C3UwW3vQXFsw7VtjO0gGO_s9-jpTKYvr43BVsB6SweOKPJCIVXTY-PtQhwQ0HXH3ksv5hHt8sf_JOOC4uWVrmW86BEjflDoDcPpKSfkW5kD2jbmni05Yl5IKk-7DCpz7uOibwDrDVzplKfPQvKP59X4ExT0jwCmVhRrzLIqKRwRsTRtR8-QTxSmnaeECi58Gw-MNtsBH_oz92w_PmSvx4wdQfJkiUUDqTvR2Y6iBfZo=)
32. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbqeSEMKmQGBz4rdRkcfq_72aDdotK2XCnB7FKtuxfRfTkEzXkHXGYfJJxiIA32Mfd_FCkSITi6FkaLs9nnVNfHUQ4eD_6bmcWmXCIIv3Y7KbsfG0-IYsG8qGV10HKp0uCot4Q8-UTw_rCSsVN2g==)
33. [ocr.org.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIcA_pmHbUk9Ri6DDSkyKJAa7ocYASzZmasvAdLS6ZCPK5gMqvdGqRrVXBpT7rtPh0xTZA4a5BVixv6sPBW-eYEk0MA_xKXBEfY2KjuNWzB3aBRI6f0lQBB5XS_JMNRI4uT4CjJmy0_OLtnxKvtyTkgRN0PiAXiOeD5kXA)
34. [techrxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXQK-FQZ1JxfypW84uIEKT6aoa4USEMqAu1dgf8xmKGjvY9-Swnu3AucKifub_qMRI4KH-D-IPLsYJqqYyUaY6_9jGOTpaanCQXMPbTAPmFhc4iPdrwgQlBcT0393pVL1yKs03PPOFyKz-tnxC9aLJHxmsl2Yc)
35. [techrxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkFxa5s9it-4tc7tmkWRDbnBxkSsDXiUSss2nW3CkUV6x_0XiuegniNdwWHsswIVUcF_Ddc8hjhgtEQ2Accpy6ujub6LzsUsFsnIVA7bfTeHtsFmg_77KMQOrotpr4ezVtTQpHMA2HJhtvtllT1dMWeR8ci1kvJfvRYAy9d0WxaMXuQrffcbPEvQ==)
36. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsl03QJWqYw-0M_976jMuj8OxYZrrPpfqkmkyzhuCqx1W_6B9iMfjLZtLSurgX71nri2VPK8CJU21CB1NT464elsqsduUkHjPqNlwR5sob4IczDJlFMzBb37xI9kgZkK5cQBoz5lFV)
37. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBaLFnGyEpmJbD8s2INOaoC6uEDGZtr5cKTPguPROHrll36lubiAX8ksT6v3D-buIlc1vfMORvZELaI0x1_ELcXKdBakgLC9KVGgT1Pp66FMYYH03I9W_ATq5tzxgjj65wF99blakUUudK9hXWlqooCp1IV5iv7xq1WYJuM-k8iusi6MiC60PTOnSVAhIKZHBQv981YfvZmszvdMNuXNrrveCj2npJsSUH5sQ75tdV)
38. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNHt47BtDSFXsCGnCM7_7FxEPnQ2t-jlTutXe7hbC449x8_PDENwz3YkKilgiQNYhAiZTeD6LxE4C-rH7gxgqF3W2b3tbs08auecOeEtyjLC8hmMbYsRCffWN8yxfW0--DJan7aEs=)
39. [umass.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7BHV0AW-lyWrRZ_-ggOfEDACZWnZbASO_LjWODpXY_K8Z0OGdCw56AWp0WRxGsKgnTeDKjJl4feXvHO4xV4vnuBhQnWcyEShqaHdv70C6srRuqiXd6RREt5ECh-4fce8D3HSkGdGt1WCnfb6AJnHdv5bWdyBAE8wfv7rGVnk=)
40. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtZVgRDrbhj48dEooAXoofLutRTaFgpyn0Dqr1gIIBcyWa8a-RkIft0tU1Nb6CsG3NdX0nO7u55TbQ2XcscpJvBJSQT2hlnl5QUwvz-wbfBmJrY4jhR9FrDmuVfZ9g)
41. [umass.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERf1uz_VGBfRCUK5TFHkgnxqehVyCs2ZBsHEx-K-2NL5Xy7NPzWfTzihRu1jF0Hixpe186DMVuxubyAsLoDTW2D6EoF66HJYlZrKC7FpywYpS4f4vdT0dciPes4mUa05VP1FqzMsNVXfBqghVA5zJ040KvyF1ioO2Cuyuwv-NnGYVBui8IYnQ=)
42. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGiHSNLrdcBrtSusZYjVAoymjhwCDrJRR5M5FI-d65TSpUFY5q6fbNXWQ0SDmtYbkVnVYukJQ6prOrEmUgPsxE2L1kzFWP7a89DH81NKhGEhjvZ_rGiUKyw)
43. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGw8XaPoAgiESDWCoHk2lZyyhwVnAVmRjtCAsCvPhvTJkBbYlMbTxipmu3xi2NdCiP79tIPBllgVvcf6OAaqO0bSC-syDd18MDQEv7-pfkynY7bz1wsk9O1PH8m6fJmxs-BmZ5W_Ylx4zUVPuwe2htxMdzTDh-f8e-unSGniX1v73KBK9M-se8UiZ5uyvXB4OejnPgyx7tU-xJk5Ty0QNeiypvciyAsK58fa3TPg1yUpSozM4zOvGTG7850G0TixBLanw==)
44. [virginia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMxYBo-rNY_stur6kOh0IaicU98jIwpPoRcKUJUizJF5-eI4k6tFOfFiaMjWE0xGX1OkPBIUSJKt8sutlPRAyRy0kKEnkeJko6yhaH-aMmKN1SZHXQnVofEQTddqxApTqab8zWsHKxNWUE2AaGdOuxCsT3QIMl5FNN9Fc1nGqqDvmBG-2MzyIPj4k-17HGdjaAL4WjyAB6Dd8sKASOeXsT-dP8xf-06p7ommm7hfewJbGkOknuWjKrAtulHzPPZ82u8GYPZCg=)
45. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUjChERSjh7xu8cfilDtKg9y5T0zwExI7AavIwofQXE8lxgeGBpLY4j2gnZULoAQayPW_oOKNVm7jiQm77s8f_wc6_kbKgHGHTk-50KdqFOW749nzV)
46. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWt1kQ8jNL2YDi2Zh3-EBSnSMbEFTca3Rso5kyJoD07rpEl7dy6MZKMy2IuVTVJ0IK1IwnNrBTjoaP-cXc18n1cAQDloMCDa-1DMEilrFZ4iuZ2-iSyOGvTjP1jA1Hn_TNwTlwkuIhFA8sVClKuf0R2-deyW8-m8gthqudDSedV4FPMrZExtPlJS3cMrficVWFttj424951OxwR_9WkdvGl6LLYh6G2cS2c_fjv5w78DwGlZYYD4yJPQ==)
47. [arxivdaily.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTojL834SJRx9-JTjB-K6OaClYW1n2344oh_e2_hIaSTXaPTdElNOHgxHXWJUnl4ephYGfXN9T-gVn8ImPcV2rISyg46BtVgkZz3zQqQABG8gH0dw0YuEpWsgMIQ==)

