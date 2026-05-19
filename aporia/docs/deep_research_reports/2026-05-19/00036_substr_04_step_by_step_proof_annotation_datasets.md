# SUBSTR-04: Step-by-step proof annotation datasets

**Pythia queue id:** 36
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdPVGtNYXVPM09MNmFfdU1QMGUtNm9BWRIXT1RrTWF1TzNPTDZhX3VNUDBlLTZvQVk
**Elapsed:** 554s
**Completed at:** 2026-05-19T10:28:52.459324+00:00

---

# Exhaustive Analysis of Step-by-Step Annotated Theorem Proof Datasets and the Paradigms of Reasoning-Ladder Calibration in Artificial Intelligence

**Key Points:**
*   **Mathlib4 & LeanDojo:** Research suggests that extracting step-by-step tactic traces from Lean 4 repositories provides critical state-action pairs for neural theorem provers, with modern benchmarks containing over 122,000 theorems and 259,000 tactics.
*   **Isabelle's Archive of Formal Proofs (AFP):** The evidence indicates that the AFP comprises roughly 167,000 lemmas across millions of lines of code. Advanced methodologies like High Utility Itemset Mining (HUIM) are increasingly used to perform step-grading, identifying which proof steps are mathematically significant versus trivial. 
*   **MiniF2F Benchmark:** It seems highly probable that cross-system benchmarks are essential for fair evaluation. MiniF2F standardizes 488 Olympiad-level problems across systems like Lean, Metamath, and Isabelle, providing a unified metric for neural reasoning capabilities.
*   **ProofWiki & NaturalProofs:** The evidence leans toward the necessity of bridging informal and formal mathematics. Datasets like NaturalProofs synthesize over 46,000 unique mathematical references across 31 domains, aligning natural language proofs with structured references.
*   **Reasoning-Ladder Calibration (AI Math):** AI models appear to learn mathematical reasoning in a punctuated, ladder-like fashion (Easy → Medium → Hard → Extremely Hard). Supervised Fine-Tuning (SFT) easily bridges the gap to Medium problems but plateaus at Hard problems without novel frameworks like analogical reasoning ("MetaLadder").
*   **Reasoning-Ladder Calibration (Epistemic/Legal):** In human-AI alignment, reasoning ladders represent a spectrum of epistemic openness (from dogmatic "Zealots" to objective "Scientists"). Calibrating AI interactions requires adjusting the ratio of "compassionate rigor" to safely deconstruct cognitive biases and prevent AI hallucinations.

**Layman's Summary:**
Artificial Intelligence has made incredible strides in generating text, but solving complex mathematical proofs step-by-step remains one of its greatest challenges. To teach AI how to do math, researchers must feed it massive datasets of human-written proofs that have been carefully translated into computer code (formal mathematics). This report looks at the four most important datasets used for this purpose: Mathlib4 (for the Lean programming language), the Archive of Formal Proofs (for Isabelle), MiniF2F (a collection of high-school math competition problems), and ProofWiki (a Wikipedia-like database of math proofs). We will look at how big these datasets are and what specific areas of math they cover. Finally, we explore the concept of "reasoning-ladder calibration." This refers to two things: first, how AI models learn math in sudden "leaps" of difficulty (like climbing a ladder), and second, how we can calibrate AI to communicate with humans at different levels of stubbornness or open-mindedness, ensuring the AI relies on solid, step-by-step logic rather than making things up. 

***

## 1. Introduction to Formal Mathematics and Machine Learning

The intersection of artificial intelligence and interactive theorem proving (ITP) represents the frontier of automated reasoning. Unlike empirical sciences, mathematics allows for its results to be verified mechanically through formal logic [cite: 1]. Interactive theorem provers, such as Lean, Isabelle/HOL, Coq, and Metamath, require users to write proofs using specialized programming languages where every logical deduction is rigorously checked by a computational kernel. 

Historically, automating these proofs relied on symbolic search algorithms and heuristic-driven tactics. However, the advent of Large Language Models (LLMs) has introduced neural theorem proving, where models are trained to predict the next logical step (a "tactic") in a proof [cite: 2, 3]. The primary bottleneck in advancing neural theorem provers is the scarcity of high-quality, step-by-step annotated training data. Informal mathematics, as written in textbooks and on blackboards, skips tedious logical steps, relying on the reader's intuition. Formal mathematics, while rigorous, is often compiled in ways that obscure the intermediate states of the proof environment [cite: 4]. 

To overcome this, researchers have developed vast, meticulously annotated datasets and benchmarks. This report exhaustively analyzes the existing landscape of theorem proof datasets—specifically Mathlib4 tactic traces, AFP step-grading, MiniF2F, and ProofWiki structured proofs. Furthermore, it explores the dual paradigms of "reasoning-ladder calibration," detailing both the mathematical scaling laws of AI reasoning and the epistemic frameworks required for rigorous human-AI interaction.

## 2. Mathlib4 Tactic Traces and the Lean Ecosystem

The Lean theorem prover, particularly in its transition from Lean 3 to Lean 4, has become a dominant force in formalized mathematics. Its standard library, Mathlib, is a massive, community-driven repository of formal mathematical knowledge. 

### 2.1 The LeanDojo Framework and Tactic Extraction
Raw Lean code is highly condensed. A single line of code might trigger a complex tactic that transforms the entire logical state of a theorem, but this intermediate transformation is invisible in the raw text [cite: 4]. To train neural models, researchers need the exact "proof state" before and after a tactic is applied, as well as the specific mathematical premises invoked.

To solve this, the **LeanDojo** framework was developed as an open-source toolkit that bridges the gap between machine learning environments (like Python) and Lean [cite: 4]. LeanDojo automatically clones Lean repositories and traces them using Lean instrumentation [cite: 4]. This tracing process extracts rich, structured data that is not visible in the source code, including:
*   **Abstract Syntax Trees (ASTs):** The structural representation of the Lean code.
*   **Proof States:** The local context, hypotheses, and the specific goal that needs to be proven at any given step [cite: 4].
*   **Tactics:** The human-written commands (e.g., `simp`, `rw`) that transition the proof from one state to the next.
*   **Premise Information:** Fine-grained annotations detailing exactly which prior theorems or definitions (premises) are utilized to execute a tactic [cite: 4]. 

LeanDojo operates with lifelong dataset management, storing theorem information in dynamic databases that sort repositories by difficulty and append new data without requiring full retracing [cite: 4]. 

### 2.2 Dataset Statistics and Augmentation
The scale of the Mathlib4 tactic trace datasets is immense. The **LeanDojo Benchmark 4** contains **122,517 theorems/proofs**, **259,580 tactics**, and **167,779 premises** extracted directly from Mathlib4 [cite: 4]. 

This data is crucial for models like **ReProver** (Retrieval-Augmented Prover), which uses an encoder-decoder Transformer. Given a proof state, ReProver retrieves relevant premises from Mathlib, concatenates them with the state, and generates the next tactic [cite: 4]. AlphaProof, an advanced AI system, similarly utilized approximately 300,000 state-tactic pairs extracted from Mathlib4 for supervised fine-tuning, allowing it to internalize Lean syntax and imitate expert tactics [cite: 5]. 

Furthermore, data augmentation techniques have been introduced to enrich this data. The `Lean4trace` tool accesses the Lean elaborator's state to create canonical datasets [cite: 1]. From here, researchers apply two primary augmentation strategies:
1.  **Automatic Tactics Augmentation:** Testing existing automated tactics at each proof state and recording successful ones, which provides a +1.7% improvement in pass rates [cite: 1].
2.  **Tactics Decomposition:** Breaking down composite tactics (like `rw` or `simp`, which apply lists of rules) into multiple, simpler, step-by-step tactic applications. This provides a +2.0% improvement on hold-out subsets of Mathlib [cite: 1].

Additionally, to bridge the gap between human intent and formal code, researchers have recently released a massive code search dataset for Lean consisting of over **1.4 million query-code pairs**, including 337,647 proof states and 244,521 informalized statements [cite: 6].

## 3. The Archive of Formal Proofs (Isabelle) and Step-Grading

Isabelle/HOL is a highly mature interactive theorem prover based on Higher-Order Logic. It features the structured proof language Isar, which allows proofs to be written in a human-readable format. The central repository for Isabelle is the **Archive of Formal Proofs (AFP)**.

### 3.1 Scale and Complex Network Characteristics
Organized much like a scientific journal, the AFP accepts peer-reviewed submissions and encompasses a vast array of computer science and mathematical domains [cite: 7]. It has been online since 2004 and represents one of the largest collections of formalized mathematical knowledge [cite: 8]. 

The scale of the AFP is staggering. It contains nearly **3 million lines of code** and over **167,000 proven lemmas** distributed across roughly 600 different entries [cite: 9]. To manage and understand this data, researchers treat the AFP as a complex network. By constructing a General Dependency Network (or dependency graph) of the theorems, researchers have found that the AFP exhibits a scale-free topology [cite: 9]. The in-degree distribution of the nodes (representing how often a theorem is cited as a premise by other theorems) follows a power law (specifically for \(k_{in} > 2\)) [cite: 9]. This topological characteristic is vital for automated reasoning, as it identifies the foundational "hub" theorems most critical to logical deduction.

### 3.2 Step-Grading through High Utility Itemset Mining (HUIM)
A major challenge in analyzing human-written Isabelle proofs is that not all proof steps hold equal mathematical significance. Standard frequent pattern mining can identify the most commonly used tactics, but frequently used tactics (like trivial simplifications) are often not the most mathematically insightful [cite: 10]. 

To achieve accurate **step-grading**—evaluating the importance of individual steps within a proof sequence—researchers have introduced **High Utility Itemset Mining (HUIM)** [cite: 10]. Under this framework, proofs are abstracted into a computer-processable corpus where each line represents a sequence. Proof commands are assigned "utilities" (weights) that represent their importance [cite: 10]. By discovering high-utility patterns rather than just frequent patterns, the system accurately grades and isolates the steps that carry the core mathematical intuition of the proof, differentiating them from boilerplate logical bookkeeping. 

### 3.3 Draft, Sketch, and Prove (DSP)
Further bridging the informal-to-formal gap in Isabelle, the Draft, Sketch, and Prove (DSP) methodology utilizes Language Models to generate an informal proof (the draft), which is then translated into a formal proof sketch [cite: 3]. This sketch contains step-by-step formal propositions with "gaps." An automated prover (like Sledgehammer) is then used to grade and verify these individual steps, filling in the gaps. This method increased the performance of Isabelle's heuristics on mathematical competition problems from 20.9% to 39.3% [cite: 3].

## 4. MiniF2F Annotations for Cross-System Evaluation

While Mathlib and the AFP offer deep, domain-specific libraries, evaluating the generalized mathematical reasoning of neural models requires standardized benchmark datasets. The most prominent of these is **miniF2F** (Formal-to-Formal).

### 4.1 Benchmark Architecture and Olympiad Focus
Introduced as a stepping stone toward the IMO Grand Challenge, miniF2F is a cross-system benchmark consisting of **488 manually curated mathematics problems** [cite: 2, 11]. These problems are drawn from highly challenging human competitions, including the AMC (American Mathematics Competitions), AIME (American Invitational Mathematics Examination), and the International Mathematical Olympiad (IMO), alongside high school and undergraduate materials [cite: 2, 12, 13]. 

The benchmark spans a wide variety of domains, including algebra, number theory, inequalities, combinatorics, geometry, and calculus [cite: 2]. Crucially, the dataset is evenly split into 244 test statements and 244 validation statements [cite: 2].

### 4.2 Cross-Platform Standardization and Step Annotation
The defining feature of miniF2F is its cross-platform alignment. The exact same mathematical content is formalized in identical statement formats across **Lean, Metamath, Isabelle/HOL, and HOL Light** [cite: 2]. All formalizations are mechanically checked by their respective kernels. This enables rigorous, apples-to-apples comparisons of Automated Theorem Provers (ATP) across entirely different software ecosystems [cite: 2]. 

Problems in the dataset are annotated heavily to ensure clean tracking. For example, problems derived from the MATH dataset are prefixed (e.g., `mathd-algebra-125`), while others use Metamath-style naming conventions [cite: 14]. MiniF2F is utilized extensively for step-annotated evaluation of neural theorem provers, such as GPT-f, which achieved a 29.6% pass rate on the Lean portion of the dataset after pre-training with the PACT (Proof Artifact Co-Training) methodology [cite: 15]. The benchmark relies on expert iteration, curriculum learning, and adaptive evaluation to continuously push the limits of automated reasoning [cite: 2]. 

## 5. ProofWiki and Structured Informal-Formal Proofs (NaturalProofs)

While formal theorem provers require rigid syntax, mathematicians communicate in a mixture of natural language and LaTeX. The **NaturalProofs** dataset was created to model mathematical reasoning in this native, human-readable format, structuring informal proofs with semantic reference labels [cite: 16, 17, 18]. 

### 5.1 Dataset Composition and Domains
NaturalProofs aggregates structured, step-by-step proofs from several key sources [cite: 16, 17]:
1.  **ProofWiki:** An online compendium of mathematical proofs written by a community of contributors.
2.  **Stacks Project:** A vast, collaborative repository focusing specifically on algebraic geometry.
3.  **Trench Textbook:** Real Analysis.
4.  **Stein Textbook:** Number Theory.

The dataset spans **31 top-level domains** (such as Set Theory and Analysis) and includes deep-coverage data for specialized subjects [cite: 16, 17]. In total, the dataset contains approximately **25,000 examples** and a reference set of **46,000 unique references** [cite: 16, 18]. 

### 5.2 Reference Graphs and Sequential Annotations
In NaturalProofs, a mathematical proof is treated as an ordered collection of statements containing logical references to prior theorems, definitions, or axioms [cite: 17]. The primary machine learning tasks defined by this dataset are mathematical reference retrieval (identifying which theorems are used in a proof) and mathematical reference generation (generating the exact sequence of references required to prove a theorem) [cite: 16, 17]. 

By treating all statements and reference links as a massive **reference graph** (which inherently contains cycles, such as Pythagoras's Theorem referring to the Sum of Squares of Sine and Cosine) [cite: 17], NaturalProofs allows models to learn the step-by-step logical dependencies of human mathematics. Node2vec and other graph-learning algorithms have been applied to this multi-graph to simulate the search heuristics humans use when writing structured proofs [cite: 19]. 

## 6. Coverage Statistics Synthesized by Domain

To provide a comprehensive overview of the existing datasets, the following table synthesizes the quantitative coverage and domain scope of the datasets discussed.

| Dataset / Library | Associated Prover | Number of Theorems / Problems | Number of Tactics / References | Primary Domains Covered | Key Features |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mathlib4 (LeanDojo 4)** | Lean 4 | 122,517 theorems/proofs [cite: 4] | 259,580 tactics; 167,779 premises [cite: 4] | Broad-coverage abstract mathematics, topology, algebra. | Tactic tracing, ASTs, premise retrieval, elaborator state tracking [cite: 4]. |
| **Archive of Formal Proofs** | Isabelle/HOL | ~167,000 lemmas; ~600 entries [cite: 9] | ~3 million lines of code [cite: 9] | Computer science, logic, software verification, general math. | Scale-free dependency graphs, High Utility Itemset Mining step-grading [cite: 9, 10]. |
| **MiniF2F** | Lean, Metamath, Isabelle, HOL Light | 488 Olympiad-style problems [cite: 2, 13] | N/A (Focuses on end-to-end verification) | Algebra, number theory, inequalities, combinatorics, geometry [cite: 2]. | 244 test / 244 validation split; apples-to-apples cross-system benchmark [cite: 2]. |
| **NaturalProofs (ProofWiki/Stacks)** | N/A (Natural Language + LaTeX) | ~25,000 examples [cite: 18] | 46,000 unique references [cite: 16, 18] | 31 domains (ProofWiki), Algebraic Geometry (Stacks), Analysis, Number Theory [cite: 16, 17]. | Reference graphs, pairwise and sequence generation, zero-shot evaluation [cite: 16, 17, 18]. |

*(Note: Data reflects approximations based on available benchmark versions and source code repository states.)*

## 7. What is Needed for Reasoning-Ladder Calibration?

The term **"reasoning-ladder calibration"** appears in two distinct, yet conceptually overlapping contexts within artificial intelligence literature. The first refers to the **mathematical reasoning capabilities of LLMs** (climbing tiers of problem difficulty). The second refers to **epistemic and structural alignment** (calibrating an AI's conversational rigor based on user dogmatism, or cross-examining its legal/factual logic). Both paradigms are essential for developing robust, reliable AI systems. 

### 7.1 Calibration of AI Mathematical Capabilities (The AIME24 Ladder)
Recent studies into LLM-based mathematical reasoning, particularly utilizing the AIME 2024 dataset, have revealed that AI models do not learn math gradually. Instead, they exhibit "punctuated equilibrium," learning in sudden, transformative leaps [cite: 20]. Researchers have classified mathematical problem difficulty into a four-rung reasoning ladder [cite: 21, 22]:
1.  **Easy-Level:** Problems solvable by base models more than 50% of the time without special training [cite: 21, 22].
2.  **Medium-Level:** Problems that require specific step-by-step logic [cite: 22].
3.  **Hard-Level:** Complex multi-step problems where model accuracy plateaus [cite: 21, 22]. 
4.  **Extremely Hard (Exh-Level):** Highly unconventional problems where models fail uniformly (near 0% accuracy) [cite: 21, 22]. 

#### 7.1.1 Overcoming the Plateaus: SFT and MetaLadder
To calibrate an AI to climb from the **Easy** to the **Medium** rung, research shows that large-scale pre-training is less important than high-quality Supervised Fine-Tuning (SFT). Providing a base model with just 500 to 1,000 instances of highly detailed, step-by-step mathematical reasoning trajectories (the "R1 reasoning style") allows the model to leap to over 90% accuracy on Medium problems [cite: 21, 22]. 

However, calibrating the model to climb to the **Hard** rung requires more than just scaling up data. At the Hard level, accuracy plateaus at around 65% because models suffer from instability in exploring reasoning chains [cite: 21]. They become rigidly attached to common strategies (e.g., immediately applying inclusion-exclusion principles for combinatorics), failing when these common solutions are infeasible [cite: 21]. 

To break through this cognitive limit and calibrate the model for advanced reasoning, standard Chain-of-Thought (CoT) prompting is insufficient. Researchers advocate for the **MetaLadder** framework, which internalizes analogical reasoning [cite: 23]. MetaLadder replaces the linear "Problem → Chain of Thought → Answer" structure with a context-aware reasoning ladder [cite: 23]. The calibration requires a specific data augmentation format known as **QSQ/C/QC**:
*   **Original Problem**
*   **Problem Type and Solution Strategy**
*   **Analogous Problem and its Solution** (retrieving a similar meta-problem)
*   **Original Problem and its Solution** [cite: 23, 24]

By explicitly forcing the model to reflect on a structurally similar problem before tackling the target problem, MetaLadder bridges the gap, teaching the AI the human-like cognitive process of analogical abstraction [cite: 23, 24]. 

### 7.2 Epistemic and Structural Calibration (Human-AI Interaction)
The second manifestation of reasoning-ladder calibration occurs in how AI systems manage human interaction and verify their own factual outputs. This requires adjusting the AI's logical rigor based on the nature of the conversation or the legal strictness of the domain.

#### 7.2.1 Calibrating for Epistemic Openness (The Stupidity Cure)
In human-AI dialogue (particularly for debates and belief examination), the AI must calibrate its responses to the user's "epistemic openness." A protocol known as "The Stupidity Cure" leverages a psychological reasoning ladder (adapted from Tim Urban) to detect and manage human *reification* (treating mental constructs as absolute reality) [cite: 25]. 

To calibrate properly, the AI must diagnose which rung of the ladder the user currently occupies regarding a specific belief [cite: 25]:
1.  **Zealot:** The belief is fused with identity; evidence cannot shift it [cite: 25].
2.  **Sports Fan:** Belief is tied to tribal loyalty, though slight criticism of their own side is tolerated [cite: 25].
3.  **Lawyer:** Evidence is used selectively and adversarially just to win the argument [cite: 25]. 
4.  **Scientist:** Belief is treated as a provisional model shifted freely by collaborative truth-seeking [cite: 25]. 

**What is needed for this calibration?** 
*   **Detection:** The AI must first query, "What evidence would change my mind?" to establish the baseline [cite: 25].
*   **Balancing Compassionate Rigor:** The prompt parameters must dynamically adjust the intensity of the AI's questioning [cite: 25]. A Zealot requires 80% compassion and 20% rigor to plant gentle seeds of doubt without triggering defensive shutdown. A Lawyer requires 70% rigor and 30% compassion, utilizing sharp questions that explicitly call out selective evidence [cite: 25]. 
*   **Incremental Goals:** The AI is calibrated to guide the user to the *next rung up*, rather than forcing an immediate jump to pure objectivity [cite: 25].

#### 7.2.2 Structural Verification (Cross-Examining the LLM)
In domains requiring absolute factual accuracy, such as law and applied mathematics, reasoning-ladder calibration requires forcing the AI to step out of seamless prose and explicitly construct its logical dependencies. LLM hallucinations are often brittle and can be dismantled through adversarial pressure [cite: 26, 27]. 

To calibrate an AI against hallucinations, operators must implement a "cross-examination" pipeline [cite: 26, 27]. This requires prompting the AI to:
1.  **Identify each reasoning step explicitly.**
2.  **List assumptions regarding facts or rules.**
3.  **Cite authorities for every step.**
4.  **Rate confidence in each part of the analysis** [cite: 26, 27]. 

When the model is forced to re-evaluate its own text across these discrete rungs, the "reasoning chain buckles" if a hallucination is present [cite: 26, 27]. Advanced implementations of this concept include the **Conflict-Aware Trust-Score (CATS)** pipeline, which evaluates groundedness, refusal accuracy, and factual correctness using an LLM-as-a-Judge, significantly raising Answer Correctness in models like Qwen from 0.069 to 0.883 [cite: 28]. 

## 8. Conclusion

The pursuit of artificial intelligence capable of robust, generalized mathematical reasoning relies entirely on the structural integrity of the datasets used to train it. The transition from informal human mathematics to machine-verifiable formal logic is mapped out by diverse repositories. **Mathlib4** provides a staggering volume of tactic traces and proof states for Lean, while the **Archive of Formal Proofs (AFP)** offers deep, step-graded theorem structures for Isabelle. **MiniF2F** acts as the crucial, cross-system arbiter of neural theorem proving capability on competitive problems, and **NaturalProofs** provides the bridge between natural language prose and formal reference graphs. 

Ultimately, these step-by-step annotated datasets are the raw materials required for **reasoning-ladder calibration**. Whether it is pushing an AI model past the 65% accuracy plateau on Hard-level math problems using analogical MetaLadders, or calibrating an AI agent to adjust its "compassionate rigor" when debating human users, explicit, structured, step-by-step logical reasoning is the foundational requirement. Through continuous dataset generation and algorithmic refinement, the field moves steadily toward systems capable of handling the "Extremely Hard" tiers of mathematical discovery.

**Sources:**
1. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7TpaWVO6mZG5yHIB3_wZX4Wlu_fiNKraZwI0ZtzSJTCtzmCmOC4YrgQzLF8L9CYORUMQMHkSagXCmsSgbleyMxUCjLxwTa8OamK3qA2c2NGly8xzYwyBCLG6yEalc)
2. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYZp91Dk3_Qeg3oaWEocLJfDS0pYdd2TjbFsa9vNQhCocQX-q5dkicCJTCakQDdthCXWLg4oC1ftxh6OUD-h8kYKqhokxl5QELxMi2WysKqGDGRtk45LdKQ5R7qSplR7A73ApZuFuRtdoEv6DQylsK02zjSNVFAewKNezqnre1pawbNTEFwb4mxSohp8aNW1I=)
3. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNPn8Beb6ifMpyAQnkRNfuDdutq8BD6g86RucNoLhAQ75XSjN2Hw2iEtkO0RxlxKSVoAsol6pnqTIr3YKJJcpyB913krbkYC_rY9upUE4w8wYy3QMDVWyey1C9ccfAUlWF)
4. [leandojo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtE3zbqEtoGDPcmr4XEbl4Iy0mflgjAL443sUNZW4iHOAux-y1PcRnh7XCWRnyersHHx2xGwWbr425IAA7BnX03Dtkef-FuBVqNxWkdvElLaLMSr1Rz3SN)
5. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGn5fIc5FGZuXoYdAtwX2Y-wePyhM_ZgmrPO3UNOA_-ytist__JkyHSXgx_BGKANAnwjPaJDNhoAMmc3pFoeFZ5eKkfFVWbUbOsRyt3mBLhdqinlSH44TgpGMbP3XRziPcfEMnW3lPrA==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVAC7__PW0NZMUx9emL67262x9-9rkKOYY3ibjy_KjC1xzEBBSM8Q-7FwzLkvN_gKX-_v1HsQa8PqF06vdGC5VYmA9zHhKd-utwXWNnWY5zCAYCG-LKgtZ6w==)
7. [isa-afp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFViZR-UUOdtWULxbEquE0eo5JjDoRZwH9Gu688nmcXp9l8deeiJWcd15gIoj1v6YjTT87fAnN1YcmnBxZhBYt1SBdTym0LAuLLOAVELus=)
8. [ed.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcc4GZxzxhRKShqCJD4V4-xS2r8hg650tLvgkp3vTPGqD1NAKi2Qn5reKpQ1Ue5uhqoE8KIpgAFFYWEJ45CEESO6otIzd4sGyiBkOOvuQaYKcQmfXGXMW48ySF47UOiYYby6hZs3OXztF4AVaxA37coRT4Nw==)
9. [ceur-ws.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgEePqOpkbT8Z9ImK8UM9YJnWll0PPytO8Djt5dgX6VXsqk7doNQLL4Sop_MQWJfk-HCo5Db-wGuB_pDhr__bBEOnk-2ZSyZxlQbtH9t2m97pg5JFQCK7kmxE=)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcoKt9-KJFGMEUQbrP0pXgfRwHmLJXTZbiMlBHUFsViXZqNlPxBnabzLpGJfGE5Nea3T_shHQ6SY_B9fO3i-fHpWs05P6xe6Xb1tcgmmV85PZQpgnWfnxwsFI9jOYArV9qcny1lScuXr4ZyUkXS1QQw2GRxK5MnAh93UlSjNh7tqaG8jymcNORN2DGWlUEPrgvFTdVL0611Bks6FRDjOBz8GdIc46_8RpdTPvOPcJauuRY4hh-x1h41bSYMHPCE-LiGM9F)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGm7_tIhLygKCplBLuaKyis8jl3YA_cE6a4_mwCWjMGzVNisrdD6iIaXoTw_OZh7DwL_aUDm9K3PuNbdUUKwijrFDz__lF7DJ9w671sJydv8aSAwOtijbVfmzL_pfOpyHAQW9PBc1ufZ0DdButr0F8s6j8obWduB6dinqNbDxLDTrGqviqlfyWdT2AMHMbU_laqA8__gS6CR9G6LuYVcpph9bbb2ufM4qDsAGV_XJ-B)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlGG_3n8ri7i8C8K5FSiGqj-zxYWU3uDcqbiy5OJ-AsFthS7UB1rNg6Z4Sf1fqBC96-5J3jXIf10P9NbgmlWsBVDniLHEMJWtSE6K2Va0Hh5GmKVg-1A==)
13. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGp1lP-V4TcfxciCw0haQCYOpT-8IAxGrRr5sVzR8ceMIOjytNqI86_OPI-WDi2BEDtPgFstz-GRre2BVvicfgh2ALHq1ebF4VjxoMb34FIQwurKbmpsAx5cZ7lDi6_uvW143IIAeoOFgNixy-blO-BgFWjPSXgam60DQBqhMByn7SlBxrN8kqvfC7aCpr3Zu_8CcMWUd7LLXo4QgTvxtBSufK-GFK8Gs4KjimDwnNqMQuiPS8mRE8i9Wbvjqhr)
14. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjPuoBj4htzjGQlwiZnbwI6WGCgYBdDOpluIg3_E_thTkn2sKpm6vUASwNcffVknkBNtrWwIS0kkHozgH378Z7KzFIzyADtJjuOKFYy63bN5cTW0QgGqewmNM8s4TuknbW)
15. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2C8KmfnzXKCQsfZzeMHf_5Iojn8UHHzWgaE6pSJp3-Kld_UYLtlfFGIEG6BhBxvddVQFH8pm4WUINuGK4lb3NgnzBNzDukugYTIiCJBhp3lf93W27oWRD8YFfcD64TDOdvCy-MR0Ev3Lj73CjEqcYlDzvMH0xZCQNx_D7eM9GkG0-c7jXMc_VgNLZdm-d3mgIZetmgyJj_BGwFYLTs6RX4E_M-j9ECIz5Gg==)
16. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbPSMJqWv_2dG2I1ZdKtO8eEqSSZe8SUPg2eOa8uJBtNB-4eSbrcuKjzAmCmKbqbDkimmbvk5roAQkW7I8RSTdVOhPomxlNxz6uV9lHM1V0BmIhtN2QRVHtJQlo9yHhg==)
17. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-qdM5WFddljD037BYbEktafAehihOOm9c31YRE8kd21w39tPyQtqXtoyBebfL5xrhUYAvN7yYvDs7MJ8QZwxMnneoxKccVuK4cSeqYHT9Hw7f9q11hUA6NHKActFys4EQ8hrPDoZ6SCtQnMF2ed1o3Y1je4gSksiSsvTaCD8cBD0swFJZtvWzm88YE2MkmCuEjMXGqwX_u5GKb4S24U0vBRrrMnDLit-g0Q==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGcW4CntNIwBAQ9acaSBYuFNRZ7kg0n3LBgA3G5zPD5aSgr3KQa1j_D4-1sd1bNNQBbt9DLIisUMAT8oxri6VIpJGxo5j5qjRXpnncImFM3drKbAml4A==)
19. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrhd0rhKDxYrZtMY9idrteBD0MK-fWvlHDJRMbyAFoHaI0yLRUtcGF2mYSKEr8kLlWxbv37KalIgqX60RFuNMRCIHUz-rLrOzBnhrxaSnXY535csrbzwqJJgiaqAbneexniODQRylZ5K2MEJUXJ7dM_PJHGPCQY8wKaPDaS5_Yk_LBYXf8DO2wsQ5Slbu209CeU2EynGz90QqXJ3qNF6oxw9UaoFVMpg0sta5weHvRPnL8DQ==)
20. [promptengineering.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_pzwy-H-ksH5b1t85SObzAp5Oqy5ipUI6jc9NSMBChO3muwyzcBVvgnlPUl5DqAuL8k-l5IqGvKsdkotjTtsOVHly8y8FyUsiPX_OnsVChqy80mZXjfheWOjDM1Tokw4fJXA2jyprPesA63rvbmNRIEBO9GeOPTPbrl9pl9IjAy5XnPAIeDC_wOChhRgM1-0d8m93KQlhIudjgYiwkInaL4HXa5oraylT)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHA33HJAtMElR4xKBl7_lReWrNeUz-DV2QksXpEJ5wRSipZzbo0N-NWEmmL3npQsWGcsSQpNHOmxYSsz1V0uxZWVV_02ItV6NJ943G5iWoNYzRGRXrmXPysig==)
22. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5uN9amZyJ_CVgoIqRZCpq3-unlir1QXhRxvX76S3FNQYapwS0nB7jycJFuUHGsKG4h80o7_lC65H7MXwTQfz2agxpu-LezPM0IZ-XZR755EzSpAaKlOVoIU3WWJycupc8vrcs1jOZ1THFYsnDvPDzKSkDNr163wZzkVjej4aOIotC72sfxfkIi4NNERBMP1NpUUbRJ2Eiv5nzFIpDhmGrAcL4XZwqCfykhnHqYMWbhT5-9hoIQnplsaB3LA==)
23. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7-HfKEIlL6yK2YVynKPXENLpOKpScsIXSwFcKP-YCAQEvLpaUTJWuCBzLJr8LxdRi5Fb_EhAVexnnbYG_gkSPjUuzKU_ceaXrpQfEDdD7WbYWfRkIJb1oESKcIOduyY2cr3REtrdQVRIJ)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGJzp37ndu5n9bHUPTM34DagR6aE86JK2tDyZr1qeyXaNRPNJZc0oeteHV4fNQ5afT6Asr8-qBXZ9fvpWzZV96aHfu8Iv1JyYpv5YIaYfifklVt9g_BQ==)
25. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFi4QWbXKRBfgSi2pPU_D7k-ZH0MG8aeQh0ip6hmLvqUGUViJhLd9EfVgzWJL28HObP1IoVOV-AYWAR6jvxEtDLXnt0o90JVDjwGS7FBmb0GDlAn31Rbe0dNuZlZJoG9HK-u8hqm7naxlsl82tzTrwVEc7FvhbG7yVy9kqTH2IAvtCNEtv_0B2uipc5PO19J5iya6JIzmlJchAq39Xebwo=)
26. [edrm.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwiSvkqMPpUk7ko0CzioHrqtEbBhpTBj6LQnCs6ul6w-G8xPfZbfzCswTwAXfZyXGR_EZbi0ZL0hNdTXg8FnqSGO120Vzc8sMpE2KzTRYwiEx6-AqbnstrlfdIGEEgSQZNNMc3kpUzz6qaT69RT2udXSH4PvquaRT_NqxdlXd-gdEbgm4pU2cbSg==)
27. [e-discoveryteam.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHftkgW4iI66SOcnbcfibvRJAQAJz6QBwoyXBpe78Ut9hSP6stGr7E3JXOLDSSr--4zYWOk2h1AoWdcVreBkaPryGplFVbzYZQl5IWw7dyq0vG02Y9thryHxqcSU5p_CwbYhsV_w2299DIupE6tWucpzgdZuqDUUyLSoA8-ME-hGFh3mf509Wv6RYUtSYheDzrbI6MSh2Fw)
28. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLus0spv84iadBgwEShhHUVovgD61teED_8qsN55tu9u4O7qgjXM9rQ30QBX8e1jYRRcSGvYi_CsbcnGrUH4UonkRCjr3o9gvb1dOZyEkm1fCLuXnOZ5wVUUOwSyfeURfNNDQHasaz3KNZ2979tkiwLXwmYVPYoXJEvBRz1w==)

