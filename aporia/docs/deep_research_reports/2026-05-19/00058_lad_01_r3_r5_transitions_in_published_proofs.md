# LAD-01: R3-R5 transitions in published proofs

**Pythia queue id:** 58
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdlMG9NYXBHS0d1LXcxTWtQdEthYm1BaxIXZTBvTWFwR0tHdS13MU1rUHRLYWJtQWs
**Elapsed:** 2910s
**Completed at:** 2026-05-19T12:21:46.463690+00:00

---

# Empirical Studies on Reasoning Levels and Step Transitions in Mathematical Proofs (2020-2026)

**Key Points**
*   **Research suggests** that the transition from simple pattern matching to robust mathematical reasoning in artificial intelligence requires decoupling abstract logical rules from surface-level problem text.
*   **It seems likely that** linear "Chain-of-Thought" prompting often masks underlying errors, prompting a shift toward representing proofs as directed acyclic graphs where each step is explicitly tied to its specific premises.
*   **The evidence leans toward** the conclusion that large language models (LLMs) struggle heavily with self-verification and often generate correct final answers through flawed intermediate step transitions.
*   **Experts generally agree** that formal proof assistants, such as Lean 4, are revolutionizing the evaluation of machine reasoning by replacing ambiguous natural language assessment with strict, machine-checkable formalization.
*   **Emerging theories indicate** that belief in mathematical proofs—both for humans and potentially for machines—undergoes an "epistemic phase transition," where a network of deductive and abductive steps suddenly coalesces into high confidence.

**Understanding Reasoning Levels**
Mathematical reasoning is not a monolithic skill. Recent empirical studies break it down into distinct cognitive levels. *Rule-execution* involves applying a strict computational or logical operation. *Deduction* requires weaving these rules into a coherent, multi-step argument. *Abstraction* allows solvers to map generalized theorems onto novel, specific instances. *Search* represents the exploration of possible logical paths, while *counterfactual* (or abductive) reasoning involves working backward from conclusions or testing alternative hypotheses. 

**The Shift in AI Evaluation**
Historically, AI systems were evaluated based on whether they produced the correct final answer. Between 2020 and 2026, researchers realized this was insufficient; models were "hallucinating" or memorizing patterns. Consequently, the scientific community began developing datasets and methodologies that assign granular labels to every single transition between reasoning steps, allowing researchers to pinpoint exactly where a logical argument breaks down.

**The Role of Formal Mathematics**
A major breakthrough in this period has been the integration of AI with formal proof assistants like Lean 4. Rather than relying on human crowdsourcing to grade complex mathematical arguments, modern frameworks require AI systems to write proofs in formal code. This ensures absolute logical rigor and has allowed AI to reach medal-winning performance levels in international mathematical olympiads.

---

## 1. Introduction

The period spanning 2020 to 2026 has witnessed a paradigm shift in the evaluation and training of large language models (LLMs) and neuro-symbolic systems for mathematical problem solving. As foundation models scaled, their ability to produce seemingly coherent natural language arguments improved dramatically. However, empirical studies repeatedly demonstrated that these models often relied on statistical pattern matching rather than genuine logical inference [cite: 1]. This realization prompted a critical methodological transition: moving from *outcome supervision* (evaluating only the final answer) to *process supervision* (evaluating the rigorous validity of each intermediate step transition) [cite: 2, 3].

To systematically study step transitions, the research community has sought to label and evaluate distinct **reasoning levels** operating within mathematical proofs. These levels—broadly categorized as rule-execution, deduction, abstraction, search, and counterfactual reasoning—represent the cognitive and algorithmic primitives necessary to construct a valid mathematical argument. This exhaustive report synthesizes empirical studies from 2020 to 2026 that have attempted to classify, label, and computationally model these reasoning levels across step transitions in published mathematical proofs. It explores the foundational datasets created to benchmark these capabilities, the novel methodologies developed to track logic across steps, and the empirical findings regarding the strengths and limitations of contemporary AI systems.

## 2. Conceptual Framework of Reasoning Levels in Step Transitions

Recent empirical frameworks attempt to "decouple" mathematical reasoning into atomic cognitive units [cite: 4, 5]. By categorizing reasoning into distinct levels, researchers can isolate specific failure modes in automated theorem proving.

### 2.1 Rule-Execution
Rule-execution is the most fundamental reasoning level. It refers to the ability to accurately interpret formal rules and execute multi-step computational or symbolic operations without external tools [cite: 6]. In mathematical proofs, rule-execution is the atomic act of applying an axiom or theorem to a given state to produce a new state.

Studies have utilized benchmarks like the Turing Machine Bench (TMBench) to evaluate this capability, defining computational reasoning as the strict adherence to rule-based transitions [cite: 6]. Similarly, the "List Function" and "SALT" datasets evaluate explicit rule execution by requiring models to infer underlying transition functions from input-output pairs and apply them to novel inputs [cite: 7]. A critical finding in this domain is that models trained via standard Supervised Fine-Tuning (SFT) often fail at basic rule-execution because they memorize spurious surface correlations in problem-solution pairs rather than internalizing the structural invariants of the logical rules [cite: 1].

### 2.2 Deduction
Deduction is the process of synthesizing atomic rules into coherent, hierarchical sequences [cite: 1, 8]. Unlike isolated rule-execution, deduction requires *multi-step consistency*, ensuring that the conditions established in one step propagate logically to satisfy the premises of the next [cite: 1].

Within the "Atomic Thinking" paradigm proposed by Kuang et al. (2025), deduction is classified as "forward multi-step reasoning with formal math language" [cite: 4]. This level of reasoning demands rigorous symbolic manipulation. Studies reveal that while modern LLMs can easily apply individual deductive rules in isolation, they struggle with long-horizon reasoning consistency, often falling victim to attention disruption or hallucination over long textual chains [cite: 9]. 

### 2.3 Abstraction
Abstraction involves identifying generalized mathematical concepts and mapping them onto specific problem instances. Empirical studies have formulated this as the transition from "surface-level pattern matching" to the application of generalizable theorems [cite: 1]. 

For example, the Theorem-SFT framework models abstraction through a process called "De-instantiation," which explicitly trains models to decouple abstract logical principles from problem-specific noise [cite: 1, 8]. Another profound test of abstraction is the Karp dataset, introduced in 2025, which focuses on NP-completeness reductions [cite: 10, 11]. Reductions require a unique blend of algorithmic thinking and high-level abstraction to map the intrinsic properties of one computational problem onto another [cite: 11]. Furthermore, studies on the Abstraction and Reasoning Corpus (ARC-AGI) suggest that true conceptual rule induction often requires synergistic visual-language reasoning, where vision supports global pattern abstraction and language handles precise execution [cite: 12, 13].

### 2.4 Search
Search refers to the exploration of the proof space to find a valid sequence of step transitions. Because the search space in mathematics is astronomically large, exhaustive search is impossible; therefore, systems must employ heuristics, evaluation functions, and pattern recognition to guide the derivation [cite: 14].

In the 2025-2026 landscape, search is primarily operationalized through algorithms like Monte Carlo Graph Search (MCGS) or Monte Carlo Tree Search (MCTS), acting over formal proof states [cite: 15, 16]. Systems such as Aristotle utilize large transformer models as both policy and value functions to predict the next logical tactic, expanding a "hypertree" search structure to find bottleneck states and resolve them [cite: 16, 17].

### 2.5 Counterfactual and Abductive Reasoning
Counterfactual and abductive reasoning involve hypothesizing, working backward from conclusions, and testing alternative states. Cognitive psychology adaptations in AI evaluate "Counterexample-driven Backward Reasoning," which requires constructing counterexamples to invalidate false premises [cite: 4]. 

A landmark empirical study by DeDeo and Viteri (2022) analyzed an unusual dataset of machine-aided proofs from the Coq system, alongside hand-constructed cases like Andrew Wiles's proof of Fermat's Last Theorem [cite: 18, 19]. They demonstrated that belief in mathematical arguments relies on a cognitively plausible mechanism combining deductive (forward) and abductive (backward) reasoning. In complex proof networks, this combination triggers an **epistemic phase transition**—a dramatic, rapidly-propagating jump from uncertainty to near-complete confidence, even at reasonable levels of claim-to-claim error rates [cite: 19, 20]. This suggests that the network architecture of proofs provides inherent error tolerance through multi-pathway validation [cite: 21].

## 3. Key Datasets and Corpora (2020-2026)

To empirically measure these reasoning levels, researchers have curated highly specialized datasets that move beyond traditional question-answer pairs, opting instead for step-by-step logic annotations.

### 3.1 PRM800K and FELM
Released in 2023, the **PRM800K** dataset marked a major milestone in process supervision. It contains 800,000 step-level labels applied to 75,000 solutions for 12,000 problems in the MATH dataset [cite: 2, 22]. Each individual reasoning step is explicitly labeled by human crowdsourcers as correct, incorrect, or neutral [cite: 22, 23]. Concurrently, the **FELM** (Factuality Evaluation for Language Models) benchmark was curated to evaluate the factuality of solutions to GSM8K and MATH problems using step-level annotations [cite: 22, 24].

### 3.2 CHAMP (Concept and Hint-Annotated Math Problems)
Introduced in 2024, **CHAMP** consists of 270 high-school competition-level math problems designed to evaluate mathematical reasoning capabilities comprehensively [cite: 23, 25]. Unlike PRM800K, which relies on crowdsourcing, CHAMP was annotated exclusively by expert authors [cite: 23, 25]. 

CHAMP introduces a novel annotation schema:
*   **Concepts**: General mathematical facts, theorems, or formulas relevant to the problem [cite: 24, 25].
*   **Hints**: Problem-specific tricks or strategies [cite: 23, 24].
*   **First Wrong Step Labeling**: Ground-truth identification of the precise step transition where a model's logic first fails [cite: 22, 24].

CHAMP enables fine-grained evaluations of how additional contextual information alters step transitions and exposes the widespread inability of LLMs to verify their own generated solutions [cite: 23, 24].

### 3.3 PERL (Premises and ERrors identification in LLMs)
Developed alongside the PARC (Premise Augmented Reasoning Chains) framework in 2025, the **PERL** dataset addresses the verbosity and entanglement of linear LLM reasoning chains [cite: 26, 27]. The dataset comprises reasoning chains labeled with explicit directed edges linking every step to its specific mathematical premises [cite: 27, 28]. By identifying 50 positive and 50 negative reasoning chains and synthetically introducing logical errors via GPT-4o, PERL serves as a benchmark for evaluating whether models can accurately trace dependencies across long context windows [cite: 26].

### 3.4 The Karp Dataset (NP-Completeness)
To evaluate advanced abstraction and algorithmic thinking, the **Karp dataset** was introduced in 2025. It is the first dataset composed of detailed natural language proofs of NP-completeness reductions [cite: 10, 11]. Comprising 90 detailed proofs sourced from seminal computational complexity literature (e.g., Garey and Johnson, Papadimitriou), this dataset shifts the focus from numerical calculation to deep structural mapping and formal proof techniques [cite: 11, 29]. It heavily targets the abstraction and counterfactual reasoning levels, demanding that models prove that if problem A can be reduced to problem B, the properties of A are inherently mapped to B [cite: 11].

### 3.5 LogicTree and Rule-based Datasets
For evaluating explicit rule-execution, datasets like **List Function** (250 predefined transition functions mapping integer lists) and **SALT** have been heavily utilized [cite: 7]. Additionally, the dynamically constructed **LogicTree** dataset functions as both a training corpus for Reinforcement Learning and a benchmark to test deductive reasoning depth without relying on external mathematical knowledge [cite: 9]. 

### 3.6 ProofBench and University-Level Benchmarks
Recognizing the saturation of school-level benchmarks (GSM8K, MATH), researchers introduced datasets targeting university-level mathematics. **MathOdyssey** and **U-MATH** target advanced topics like Calculus, Abstract Algebra, and Differential Equations [cite: 30]. More recently, **ProofBench** evaluates models by pairing natural-language mathematical problems with their corresponding formal statements in Lean 4, drawing from graduate-level qualifying exams [cite: 31]. Models are scored strictly on whether their generated proof compiles in the Lean formal verification environment, eliminating the ambiguity of natural language grading [cite: 31].

**Table 1: Summary of Key Step-Transition Datasets (2020-2026)**

| Dataset | Year | Primary Reasoning Focus | Step-Level Annotation Strategy | Size / Scope |
| :--- | :--- | :--- | :--- | :--- |
| **PRM800K** | 2023 | Deduction, Process Verification | Crowdsourced ternary labels (Correct, Incorrect, Neutral) per step [cite: 2, 24]. | 800K steps across 75K solutions [cite: 22, 24]. |
| **CHAMP** | 2024 | Deduction, Search | Expert-annotated concepts, hints, and first-wrong-step identification [cite: 23, 25]. | 270 Competition problems [cite: 24, 25]. |
| **Karp** | 2025 | Abstraction, Counterfactual | Natural language NP-completeness reductions [cite: 10, 11]. | 90 detailed proofs [cite: 29]. |
| **PERL** | 2025 | Deduction, Rule-Execution | Directed Acyclic Graph (DAG) mappings connecting steps to specific premises [cite: 27, 28]. | Synthetic and real reasoning chains [cite: 26, 27]. |
| **ProofBench**| 2026 | Deduction, Formal Search| End-to-end Lean 4 formalization and compilation tracking [cite: 31]. | Graduate-level qualifying exam problems [cite: 31]. |

## 4. Methodologies for Labeling and Modeling Step Transitions

Methodological advancements have evolved rapidly to handle the complexity of labeling reasoning steps, transitioning from manual annotation to automated algorithmic verification and formal proof simulation.

### 4.1 From Linear Chains to Premise Augmented Reasoning Chains (PARC)
A traditional Chain-of-Thought (CoT) sequence is modeled as a linear trajectory: \( s_0 \rightarrow s_1 \rightarrow s_2 \dots \rightarrow s_N \) [cite: 32]. However, this linear representation obfusctates local logical dependencies, making it difficult to trace errors that occur due to faulty preceding assumptions [cite: 26, 33].

Introduced in 2025, the **Premise Augmented Reasoning Chains (PARC)** methodology restructures linear reasoning into a Directed Acyclic Graph (DAG) [cite: 27, 28]. In PARC, nodes represent reasoning steps and directed edges represent strict premise links [cite: 26, 27]. 
*   **Methodology**: Researchers utilize Aggregative Premise Mapping and Dyadic Premise Mapping to force an LLM to explicitly output the set of premises \( P_k \) required for step \( s_k \) [cite: 28]. 
*   **Advantage**: By verifying each step in isolation under its specific premises, PARC allows systems to identify **accumulation errors**—steps that are locally logically sound but output incorrect data because they inherited faulty premises from an upstream node [cite: 27, 28].

### 4.2 Automated Process Labeling (AutoCV)
Manual annotation of step-level correctness (as done in PRM800K) is prohibitively expensive [cite: 2, 3]. To automate this, the **Automated Process Labeling via Confidence Variation (AutoCV)** method leverages variations in a verification model's confidence scores [cite: 3].
*   **Mechanism**: A verification model is initially trained only on final answer correctness [cite: 3]. During inference, it evaluates a partial reasoning trajectory and assigns a confidence score representing the probability of arriving at the correct final answer from that specific step [cite: 3].
*   **Labeling**: By detecting relative drops or changes in confidence scores across sequential reasoning steps, AutoCV automatically annotates where the reasoning process deviates from valid deduction, efficiently generating process supervision data without human intervention [cite: 3].

### 4.3 Theorem-SFT: Structural De-instantiation (Cond, Map, Exec)
The **Theorem-SFT** framework (May 2026) offers a profound methodological shift in how models are trained to execute rule transitions [cite: 1]. Vanilla SFT trains models to map problem text to solution text, often resulting in "Premise Oversight" (applying rules without verifying conditions) and "Conclusion Misassignment" (failing to bind abstract theorem entities to specific problem geometries) [cite: 1, 8].

Theorem-SFT formalizes every step transition as a structural functional operator \( T = \langle \text{Cond, Map, Exec} \rangle \) [cite: 1, 8]:
1.  **Cond (Conditions)**: The logical gate. The model must explicitly verify that the preconditions of the theorem are satisfied in the current proof state [cite: 1, 8].
2.  **Map (Entity Mapping)**: Referential alignment. The model binds the theorem's abstract variables (e.g., `[base]`, `[height]`) to problem-specific concrete objects (e.g., `segment BC`, `altitude AD`) [cite: 1, 8].
3.  **Exec (Deductive Execution)**: Once `Cond` is verified and `Map` is established, the model executes the invariant logical operator to derive the conclusion, generating the next step [cite: 1, 8].

By training models to explicitly output this `Cond` $\to$ `Map` $\to$ `Exec` sequence, Theorem-SFT successfully decouples abstract logical principles from problem-specific noise, forcing genuine deductive rule execution [cite: 1].

### 4.4 Reinforcement Learning and Markov Transitions (STaR, RL-STaR, TSMC)
To enable models to self-improve their step transitions without external data, frameworks like **STaR** (Self-Taught Reasoner) and **RL-STaR** rely on Reinforcement Learning [cite: 34, 35].
*   **Theoretical Grounding**: These frameworks model reasoning as a Markov Decision Process (MDP), where each reasoning string \( s_n \) contains sufficient information to derive \( s_{n+1} \) independent of previous history [cite: 32, 35]. The transition function \( P(s_{n+1} | s_n) \) is optimized to match the ground-truth optimal transition probability [cite: 32].
*   **Convergence**: A notable mathematical proof provided in the RL-STaR analysis (2024) demonstrates that even if a model generates incorrect intermediate reasoning steps that lead to a serendipitously correct final answer, the probability of incorporating these incorrect step transitions diminishes over continuous iterations [cite: 32, 34]. As long as the pre-trained model exceeds random guessing at step transitions, reinforcement learning will theoretically converge to the optimal reasoning policy [cite: 34].
*   **TSMC (Tree Search Monte Carlo)**: Methods like TSMC further optimize this by sequentially refining sampling efforts to focus exploration on promising candidate transitions, estimating expected future rewards at partial solutions to bypass the need for step-wise human annotations [cite: 36].

## 5. Empirical Findings on Model Capabilities and Failures

The methodologies and datasets outlined above have yielded critical insights into how contemporary AI models navigate reasoning levels across step transitions. 

### 5.1 Format and Modality Dependencies in Rule Execution
A 2025 study examining "System 1" (direct induction/fast reasoning) versus "System 2" (abduction + deduction/deliberate reasoning) pipelines found stark variations in explicit rule execution based on task format [cite: 7].
*   **Difficulty Dependency**: The System 2 logical inference pipeline (which mimics rigorous step transitions) demonstrates massive advantages on hard questions (outperforming direct induction by 37.2%), while the gap narrows significantly on easier questions [cite: 7].
*   **Task Format**: Surprisingly, when a task requires explicit rule execution in a Free-Text Generation (FTG) format, the System 1 approach often outperforms System 2 [cite: 7]. Conversely, System 2 excels in Multiple Choice Question (MCQ) formats. This simulates how extended contextual distances in long reasoning chains can impair the precision of free-text generation [cite: 7].
*   **Visual vs. Textual**: Visual and symbolic tasks benefit greatly from step-by-step deductive pipelines, whereas text-heavy reasoning tasks see diminishing returns [cite: 37, 38].

### 5.2 The Verification and Meta-Evaluation Gap
While large models generate high-quality text, empirical studies using the CHAMP and PRM800K datasets reveal that models fundamentally struggle to *verify* mathematical solutions [cite: 22, 23]. 
*   **Flawed Reasoning, Correct Answers**: Evaluation over CHAMP annotated data demonstrated that LLMs frequently arrive at the correct final mathematical answer through logically flawed or hallucinated reasoning steps [cite: 22, 25]. 
*   **Overconfidence in Deep Reasoning**: Introspective Uncertainty Quantification (IUQ) studies in 2026 highlight a severe calibration issue. When LLMs generate deeper, multi-step reasoning traces, their Expected Calibration Error (ECE) actually *increases* [cite: 39]. Models become overwhelmingly overconfident (expressing >85% confidence) in their logic even when intermediate step transitions contain severe factual or rule-execution errors [cite: 39].

### 5.3 The Epistemic Phase Transition
At the intersection of cognitive psychology and mathematics, empirical analysis of machine-aided proofs in the Coq system provides a compelling explanation of how human and machine belief networks operate. DeDeo and Viteri (2022) studied the interaction of deductive inference (moving forward from axioms) and abductive inference (moving backward from conclusions to plausible premises) [cite: 18, 21].

*   **Network Robustness**: Traditional linear proofs suffer an exponentially growing probability of error as steps increase [cite: 18, 40]. However, real-world mathematical proofs form a highly interconnected network of claims. 
*   **The Phase Transition**: By simulating belief formation through Metropolis-Hastings update rules, researchers found that when proofs have multiple interconnected lines of reasoning, errors in individual step transitions do not undermine the entire structure [cite: 20, 21]. Instead, the argument undergoes an **epistemic phase transition**—a rapid propagation from uncertainty to near-complete confidence [cite: 18, 20]. This demonstrates that step transitions in complex proofs rely heavily on structural redundancy and counterfactual validation to remain robust [cite: 21].

## 6. The Lean 4 Revolution: Formalizing Step Transitions

By late 2025 and early 2026, the community recognized that natural language evaluations of mathematics inherently mask subtle logical errors, unstated assumptions, and invalid steps [cite: 31]. The solution was the integration of automated theorem proving into strict, functionally deterministic environments, predominantly **Lean 4** [cite: 31, 41]. Lean 4 is an interactive theorem prover and functional programming language where every logical inference and step transition must be formally verified by a computational kernel [cite: 31, 41].

### 6.1 The Formalization Gap
A critical 2026 benchmark study highlighted the "Formalization Gap." Frontier LLMs achieved over 95% accuracy on informal mathematical reasoning tests, yet successfully produced complete, compiling Lean proofs for only 2.8% of the same problems [cite: 42, 43]. Translating mathematical intuition into the rigid syntax and typing required by a formalized deductive system presents a massive hurdle, as Lean is unforgiving of the ambiguous step transitions common in natural language [cite: 42].

### 6.2 Aristotle and IMO-Level Performance
In late 2025, Harmonic introduced **Aristotle**, an AI system that achieved a gold-medal-equivalent performance on the 2025 International Mathematical Olympiad (IMO) by formally solving and verifying five out of six problems in Lean 4 [cite: 15, 17].

Aristotle explicitly models multiple reasoning levels across three primary subsystems [cite: 15]:
1.  **Lean Proof Search System (Search & Deduction)**: Uses a highly parallel Monte Carlo Graph Search (MCGS) operating over Lean 4 proof states [cite: 15, 44]. A 200B+ parameter transformer acts as the policy and value function. The system predicts Lean tactics to navigate the search space, expanding a hypergraph of equivalent states and prioritizing actions via a PUCT (Predictor Upper Confidence bound applied to Trees) formula to tackle bottleneck steps [cite: 16, 17].
2.  **Informal Reasoning System (Abstraction)**: A lemma-based engine that generates informal natural language proofs, breaks these complex proofs down into modular lemmas, formalizes each lemma (Autoformalization), and iterates based on exact error-message feedback from the Lean compiler [cite: 15, 44].
3.  **Geometry Solver**: A dedicated deductive database solver specifically tailored for geometry (Yuclid) [cite: 44, 45].

**Table 2: Innovations in Formal Proof Search (Aristotle Architecture)**

| Component | Functionality | Reasoning Level Applied |
| :--- | :--- | :--- |
| **MCGS Hypertree** | Explores tactics, splits goals, identifies equivalent states to prevent redundant paths [cite: 17, 45]. | Search, Rule-Execution |
| **Logical Negation Transitions** | Augments single-goal states with their logical negations to prune search trees and disprove false paths quickly [cite: 17]. | Counterfactual / Abductive |
| **Iterative Autoformalization** | Breaks natural language plans into Lemmas; translates into Lean 4; utilizes compiler error traces for self-correction [cite: 16, 44]. | Abstraction, Deduction |
| **Test-Time Training** | Model retrains on its own successful and failed search traces during the inference process for a specific problem [cite: 42, 44]. | Search, Deduction |

By requiring that every sequence of steps be accepted by the Lean proof checker, systems like Aristotle definitively solve the problem of "hallucinated deduction" and demonstrate that synergistic application of formal search, modular abstraction (lemmas), and compiler-guided counterfactual correction leads to human-expert-level theorem proving [cite: 16, 46].

## 7. Educational and Cognitive Perspectives

The computational attempts to label and replicate reasoning levels closely mirror findings from mathematics education and cognitive psychology.

### 7.1 Transitioning from Empirical to Deductive Proof Schemes
In educational settings, students often default to "empirical arguments"—validating a mathematical statement by testing specific numerical instances—rather than formal, deductive proofs [cite: 47, 48]. Studies show that early-grade learners rely on external and empirical proof schemes, gradually transitioning to "structural" or deductive schemes as their expertise deepens [cite: 48]. 

This directly parallels the evolution of LLMs. As noted in the Theorem-SFT research, models trained on simple input-output pairs remain stuck in an "empirical" mindset, relying on surface-level pattern matching [cite: 1]. The shift to structured rule-execution and Lean 4 formalization forces AI models to adopt a strictly deductive proof scheme [cite: 1, 16]. Instruction sequences designed to induce cognitive conflict in students—forcing them to see the limitations of empirical validation—are conceptually similar to the negative supervision and counterexample-driven backward reasoning used to train formal AI models [cite: 4, 47].

### 7.2 Atomic Thinking vs. Holistic Context
Cognitive theories emphasize that humans solve complex problems by breaking them into fundamental "atomic" capabilities, solving them incrementally, and passing only essential information to the next step [cite: 4]. Conversely, standard LLM "Chain of Thought" mechanisms rely on massive, holistic sequential context, which introduces noise and requires excessive self-correction [cite: 4, 49]. The recent empirical success of the PARC (graph-based) methodology and "Atomic Thinking" framework validates the cognitive assumption that strict, modular decoupling of rules, concepts, and logic steps yields higher fidelity reasoning than monolithic textual generation [cite: 4, 49].

## 8. Limitations and Future Directions

Despite significant advances, empirical studies highlight several ongoing challenges in labeling and modeling step transitions:

1.  **Scalability of Annotation**: High-quality step-level datasets like CHAMP and Karp require arduous, expert-level human annotation [cite: 11, 25]. While automated methods like AutoCV are promising, they remain dependent on the robustness of the underlying verification model, which can be prone to the same biases as the generator [cite: 3, 25].
2.  **Reward Hacking in Reinforcement Learning**: Frameworks utilizing process-based RL risk "reward hacking," where models discover degenerate logic paths that exploit the reward function without representing genuine mathematical deduction [cite: 9, 50]. Cross-level random inspection and constitutional AI constraints have been theoretically proposed to mitigate this in AGI governance, but practical implementation remains complex [cite: 50].
3.  **Sub-symbolic vs. Symbolic Integration**: While formal systems like Lean 4 enforce rigor, they lack the intuitive, sub-symbolic pattern recognition of neural networks [cite: 12, 42]. Future work must continue to bridge the "formalization gap" by developing neuro-symbolic algorithms capable of fluidly translating hierarchical visual and textual abstractions into strict first-order logic rules without losing semantic richness [cite: 12, 51]. 

## 9. Conclusion

The empirical study of mathematical proofs between 2020 and 2026 has fundamentally transformed the landscape of automated reasoning. Recognizing the inadequacy of evaluating only final outcomes, the scientific community has rigorously mapped the internal mechanics of step transitions across varying cognitive levels: rule-execution, deduction, abstraction, search, and counterfactual logic.

Methodological innovations have shifted the representation of reasoning from linear textual strings to Premise Augmented Reasoning Chains (PARC) and decoupled functional operators (Theorem-SFT). Concurrently, the creation of highly specialized datasets—from the granular step-labels of PRM800K and CHAMP to the high-level NP-completeness proofs of the Karp dataset—has provided the necessary testbeds to isolate specific logical failures, such as premise oversight and accumulation errors. 

Ultimately, the most profound breakthrough has been the integration of these reasoning frameworks into formal proof assistants like Lean 4. As demonstrated by the Aristotle system's gold-medal success at the 2025 IMO, combining the expansive, abstract search capabilities of large language models with the inflexible, rule-execution rigor of a formal compiler produces mathematical arguments that are not only highly complex but epistemically unassailable. This synergistic approach not only paves the way for advanced machine-mathematician collaboration but also offers unprecedented insight into the cognitive mechanisms underlying mathematical truth itself.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTZiF-HT0oxmFQMPGGqfRRtqbCxLabc7QJoXIYGtbABTlIRUowuR5rQxEDCS-XbtMR_bY8hpt1JonYR35KZ_0GbaaXpUYF4jgZxuHAZXwjAkvQQLZmt8qBHA==)
2. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEV0h9QwTVckxqChDH0AQwTEBoiMxnZvXSzRbwUjQXzHuHJ04bxuFQTCgVMH76TlScS0OZJJgJjHRkFKIukme30YAr7DncZCDKBqvlJDVQS_L3FOZspH4pGT9UK5VCUtSM=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzdWGMnJZQT5p--3oaNhjUULl9-YsJVBek4_1icMM8siVmgmGWbf_WEvxPaMj8ZMVmorjYhzqBq18A2qhaYt8AsL4HTS70gdfaK7Kfbo_S9lfsKffSIEEftw==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEz2l2ZGwkPjqq0Bx3L8HYQmud-7onXUtsbnzXx3J1aR_Ga_ftLYje4XNw-dJhRoxZ1uKMrElQAOpAwh7aAXv0tDOBoAhOpIxfIQuUN5sNNLLNnLI3l3eiUmQ==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdUza_KyqdhnqsqwnHw8vfyOSRBGhuBzKwFadbBwCsun3CmrK-jvvZdu00pvKGDs05y4t8aLO2p5y82hHHJ20W0sES3O1-OjeNba9Nr7iM7x4Ifm68OA==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqG9FRMv2fYwzpeoWh70-J9EExsz3QjGGCJ3KKv5iueimo1JCrhc35IhsL0XauIC4omcqwy6I67c-49y9vWKRtcm-_8OWB2stor9M6Vlji4QxR2GrtGLEmzQ==)
7. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOF6mUiy_NRK3EXUzhH4vsh-tuy-7zHhf2bk2jYXb6FC6aTuCl4bPcymXVD1UyXars-3q8ZIrv7wMt6zNS2VOvbUM1PcVxBIBGi2dKCPwZnej4li9b1P_pYdvStNR-mvh6Qr-H8AON)
8. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFflxsowqKDPdnAVLKWE4FL7sAtdtsYZWBPZ_xtNZJVHVbkrw6GdCtAJEIA6owr3H8u4gjd4I-oXJicqXsjh8IQ6I9Hlq9epBWBWdCMrqB_am6UKGz9L0ZHiyOI-9YOWdO9oZqcLMlNrz_3h1_KGcg-TX-jnW9IuipNCxBVaMTLd2fxV7TsEks6wJ6AV_yy2xAnKlynr_nVO0LgzHJYFy9tg6fdbg1RZsLPE28n-REejuHV)
9. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFEd672U2mi2vkBU-awo7GA9bTo0pxtApd1YqzLoPkmoarSBnCIPwzQ4vvsgL7Xs0BVrUf0RpCyII8Mw07EGc4fsTLD8fFfRHGWJd6EgN8_hgTAQeIC9GdgZ7NyakE_a4=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHO47Nci3mDPdky19SHt4IGwYeYCsQZVY2PIvmVrrk-wiUjpqVB_CZ9iv8My5lOTuWDnVi7QhHdwi7rElM7eZjHUVC_Ypv8SSrqJCz1WNSwSdwPN8GU3A==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTJzrq0ZzWwp02Qko84uHfi8w9HnVgRv6SLBZruf8BFwID6BiOHa121u0kxH1LUY8zF8MaRXDAgao0UGow_gxKqYDBSOsAv6KTRcEopzoUkVWpT9yM_OMd3g==)
12. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFq31JgWcx32GQYoDxjkNz1huAhfyd-Qc7uy_WCt3rkRd75uIueCq0ylnZs2qsNHHfKHOixOAOUvaQd-btS9gRKQY7IeFHWdtiPUUv4deYPicY1VbSDEDTVjT2GD2wKQ1PF8S6GqEfHW_S36yoj)
13. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeBRxEKZ-Mmm__9ZyN0atn_GFjxSWjpMPIpKZnQRRQwu6cP1xHsvwesVDnc2S-vrIBVbG2V2RO73pQ1Gqp4058rYCya16O1wlWJtnMZL8DlJaIjizYc1l7LD2OmoL6tUxmOiED1CxOnJl787f7QTPU02Ot)
14. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxNpVjFeFQumB3Hcl134BH15ItXnPPYEveimr6wkkZ9LhlrClSd_NouB8vkOlaaU2UaZ9k45wOmOHaGkZL0uaplov5urpqAqn59yJxlRLbmBGGI5sMV2OhhylYXR1L60DiUC-IyhR_elLXsy8=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmE36grjNr8TGxV2gdUjAu6iNsRQCaoElFxfb3IYvVn1sp5-cDRaOaXcZkbNij7plVdEjb8-zoKt0CV5l4NuE5WCA4e5f8gQ3Qq4Um_BtSbmgeTrW8CwdWZQ==)
16. [chatpaper.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGn9oDwTw0xn9Tn_GX3GgdzvqsIEXJLsqGGVf473htTjoc6HXp0LtFsp3vJHWeLvG0LqmSfFz-TKzF5F6oCbyharCuuB4hUTe06p0cjWebvAXOEPy28FDD5)
17. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGX2_D7uA120ANy34VRVgQYG2JlA_qgPyjPb09_e_cYhou2Jtod-vXnXqfDTrtquqctRQ8fjUqcEn0Zuoyxo1Ovf8KMznmiR8XbK88gahx0qi_BO2JBfxMDKn7j5v8j7mFgGyXmSX44A8BnaU9RcgaWFblq-teELxy75Xw9PI8j-_F8Gzd9ZvN2eQ==)
18. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFO005xwZita0IS9VHiUqcE1SqeR1qMhXxssP286WKRKEGGjSpKsSypUzVg0cusFq5VHpwsHo0mwzbx0Xa26eczIFpcjrIluNWO7y4NLvCWkJrJqyLdv65llbA9OmQBRw==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERYF6s9nttGZVXRIwBhOQzUtg475VTh8T_7YqFTg9mssf8bHNW2ng6ovpqSpUjrOT8DL9iC0mD-vaoITaaACc8hwJgKJjUEcWpvPXiLyoKabGuPX3RnQ==)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGw442TjNvVtwl1_2YQx9pVQ2hK0iSY3xJwoYIpkzZ8KQ8yfvxpM9YqQct8rmDBGk_i9PsvNrCUDZyPeypfaNIfgq2VgY65TFz6XdMs1Jt_d0wNZZmeODFG3LqAm4OpuGCzYL9ZVXKgv10DzSo1BPdTw-Y6AIe6jRHHb7FEOZ2OJfAnALQhSLDmO8y1RFSmdzs=)
21. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4kK_U2dp_TfIddOgefaFe8yVYPpWpw0fPsdqx4MOSkpSglP_uFHMvS8qiKWk1mUPpdb4yeQYfs1Y7ldmJlE5El-Jmn02Ifxe5dYFHRL10_YYcs9VFzwjSVGk22ocOdYtvIRuzMEWIL-a_)
22. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKw6Ul6yaDyhIVIqlDsZb40841rD8F-3KvqvJqGXrohRw8jovsgkhRohyqeHFKID63OdT7gD57efXUGX2jhmv6tuT0mcg66A8mFViIRYqLtIG1kD3gVJ-Ht90wsH7_Cp0SeFZZwPlhAA==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHc9tkvuA2qpvVeoFZPVvc9fT_wHZxOPUpt1TW9Mp9uSrXRdBLC1PMnlK1p482Ak77-YQ7p4s13XHsNhIjTsRyTcj3-sbjnCT0RuiPpi0Hb0q-8L1Qd69_UwQ==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHp1xtDTXLcDQKuKsDCoFBGRBurBO6JC3fbdEKw6g_S1PzZ2ADrBNHDe-Ru2ZZtYYwWrt4PVcFXtcSjKsJnXaxlVM6_6mtEtXlYgVYwKSOnifRJWvnVPJhBmQ==)
25. [chatpaper.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQIjrmsLgxUtyg3m-ilHKyawwlAcdCwEAx5-8ynokKuSk-V4f1rr5mqrtjyxUm0LqeZtV70wioTE_6Qlu-C-YHxKqhElyXCHBhyPG3xVjJ5xzEnm5tu8s=)
26. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2lKlSimaNu-ayg1jTLqVMxNupr_mOIP9wVgHx8Qut07RDqcZJhldVO20AA86fepBP_y2I5jo1bt3lrRCMxTyIATmoUPAa7kRyOMXdyWxdYwqvLGiQE7wkCKMzPSysGQ==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfinj8Lv_3m0F3K2i2Sz0pcSsCEhY1plRr8AIXRzksVs25Qv8k6cKlZfSX6A_KwI7A3Kvh_7DZW3DZPQgMg9m_N0jKmqpj9iZu2dmzpJRvTGMQ6qH8042eDQ==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFn__KoBDLI4oEczaplguN5QyUdUoFMAVsHt2n5GX6PRywfAtJwYLiAWZurHoh390bR2JB1DBiRrRCP1YAAzQjZrohzUGWiiYXwsHFX3KQ9EwbDyfIOqIE=)
29. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH52j04kvbsiH6Pvza4TbcqzzQglHY98jMFLy8McoCfl6HXeE6rss9nsrGyGMc89X88LEhHi-cNhUo5FCd1Csz2YYPrYbUkGI12HDuEG_lQTkOAqKIK-0K8v0wtsx-TulEex085nPL0GfCekWQ=)
30. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCQRjXNjqzD1D01cyxm56bkmhKPPFp2fPpU0lg8U0Q9Z82lL9mgGvEWe2aJkPJ5AY0RXm_p113Brpaa80T4_XgI9XTEp3mfeHryR-zzIyoqNrqhy9rDS-vcf55pNlV)
31. [vals.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0c2Ph73jjWs-54TBCSwNQJTpmPpRcTW-TZgFlpzV-vyjn8q_yaMeiucQuVo0tRIKh4lIv4gJSVL5OUrZRaMgdz1U4KglOjSqVi6KUArCtWsPWUytAhj93KECAlgUSY30=)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLsrjah3tFPZLpkpouWutVQW9Vj55xFXnoC0Mfu1pwi0SvsUzvEw1CPVqncmrd0XUbN85obZXVyJFTzYgVNN7Z-FfbS1SHEGSZiaYisUYWnZFBNgx76fY=)
33. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGWf3E8A_zCI0C5yYua3EfsvuMP35QOoK-BJapFUOSmYEMMgvagjRkqPq9KODfnogsqdZeJCV9wLJejC7QlcmGGspXpUXDxO878NbdS0CaOMbX7FwBwYRSOBBDPR7m_8QhXoa4N0p85SorTDnvDWnhkzI-FE8gzyzU-sySRsKc0OgjVZqHpMmHfIjuJaOC_WPdkl_GU1T0q7OOdqTOJgGhdFEmrlpgUO9qdk0vABWcmWA90Vys3LAPgdHvrUnwtizfLemTfA==)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWxzHkI_4D6U4ifDqaYvQPu4CUTZXJOlyBtYQZQqlqMRA1iTiuPAPqHXU2vWeOHv1NUZZjZYvlh-sTDDWpYTdzqlL4-ErKXRWtGm4IYtY69av4nCsH5JEcMg==)
35. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHA_L2PpEgigzwGVCQajB6anHEAOrduEaxpkIXj5Z2APbPl6I0dVEWasZzj9zOiBtk1XiA0wlUBMSuxytNlULvG96k08rw_amXao8lS62KKYIOoL39UJRawRuj1Zs0nB3welw7NZzimPUNL60oVxmEUtaJR7JIS7KMaoJd3aGujhyEavMeIZmY-RORuh5XPbvb6646b7zjM-VFo9816nKApWL8b9nQ8RiCx0B2aOSxfcyBLfWHcq96knXIVE0-yYVcuWY3C)
36. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQGXvwAJqIBT63TPn3PANCmGli1ytCeQO9SBozLWDb6kpc0h4ni4sdPTMn6JYvpCqeElIOw1GSb-YVYLcwrn2jGCzmCu0Q2d5ZKIZYHuQLDel6BhYWSg==)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuCSjAaVx22u1Ymh_FdNeEoZjJESkbDww3ZikwwMsS1xut86o1SzxBQWJgYpo5LyRYQDaB3aR3BipGyk_GYqRXZom6LUHCZT0AlkOtT_SDExM__uRuTGDvMMXFmw==)
38. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXDfBRzPOMNQ4kwR8eVQQHXN6BWQ7usBt2jvRko7r1pqR01pphW7SmP42riCjslUVrYWw3CvEfCNgQrjvOWKbErCPX1LCr9qIvoMH6nUYQzECju2IbkQ==)
39. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0mhiggg8OyrlkDdkPba9UTPcWE4ym1R4SlBWlluMXnQ3NNw7yIbPPiMv7MwKcMswz0JJHbelHS9f6sUeozzN-KSRhEfqs4e8LzwRHkXPGbods23Knx94Ej_jekogfkrzqmayQCOxPFmo=)
40. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELiXDZTsk9WjbKlSfJ2zJB3s8eDJ69hpY1tb7IBT1dD2lIwCl5NnP0lxjmL0SJ6csxuBYGfdLRbVnxo0U1AO6rfQ_RaCAYkwaqXG4WiHkn2bcYznrtpmSYPw2por0ZJXUxdyfVVc-Dp86ZaDqo5OnhT40l87lhaAG2sFnq4upzK3i7A0O1lJwLv7MRSyZDJezYxOTvr_0zNbp9Iw5BjahdA--7xv4BNmYTRicbP1C06qfZkKrCKiXk22g=)
41. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfFupsPu_1eWiKLwGUE0tOHB3pOz1fvAQaKSGEWI6ckaXueWvz__niQxXJh2TsO5BVSWDZBPAvaPw85pGo1Sge1qIV0VE6n915rvtnXzY1d4xi6oDmuo1eL5-9IIw8LxPsD6tH2uvFaSOZ0iMR8k-CHL0ZFa_Oju5NYICEDvwNtlKs15SKnYA9eZJFElVZHr4uymeO8DS0hMuGDWTpOjGwQGdIuytUwerxGKIHDCS3Nj9ek6yubo5eBgJz)
42. [yad.codes](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKjUosl10FSRtsgJy1Xo9HowpSfD24Ohm8oGibISUM1mzllPFn0qsy4NpFVJbXL4kxTaIW354gXVfmiVLrj3xTZwxmmyYkNZGdWp61f0KHGtOVn-jf5QYxiN8GkvkmCSA=)
43. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhCbsfw5proqzwpq0HgO_zgJ6fQOnPaj14XgFiQZwwvzyDPuT1MqlfAHiMbqZpw9ixMvaecYJJKItstB8CP8s2lR2PRJze3JuFvbgwl46fjfZ9FKFyfZO_vzzyCZSZGW2or7Z90ZNsnBcLEtdD18Xizw==)
44. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8hMLWQ9FM_s5WMbwrAQIck54V5YKaZI-d9IXG_Pde_jqpS1SYnSPEuh3sa_hmMYI4SRdjb-joKU6gKOzY13Rt2t3p54F-WyGPDW6gwpEMm4fe3y9AGpUdqrKZ9XOX)
45. [virginia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFN4oZf4SuHF_lfcsix6JpT4vyzKlO59DJCXmxd27678asPz2Wej9tnqf9Jy0hR1qADksvgt7yP0Dnilu2F4e2U1FiQrKESyLupUy9jwkhavTaTzcyNK7ahITbefUTcz8p2fzwoiCzckMiC_MPRoW-DFm1isKUxYVxGHWiV6pI1_S_XBH1948fCwBWlPVvgTefUMLBjawReo2nqcmdqb0A9W9S9a7KSABjjEE9W8EYcyf4nhJR22afh7kzXA_OkFwAhkES-DyaZ)
46. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9AO6793XmnyrYdkXNaAwTxUhVdWAAcgtlo3hiHBwySLjLSAilYD4ysFDNKCeKhmAYmyMTkFLRUyZE70C6iH5vPMRWu8L-fXmjJsTFsc9J8fIGqqOZhL3oizjQJssX-dcMqaM09h4X79U2qU29fZ1WUB7tyRzh4rj3m6Wh2vY0MReuo5I5dEc=)
47. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJTY8HplAk4giMXUqCIHaCvOEPi4fO20r6yT_T83QtgTpCu-0A1gli7LBvYW9pHYNWLb2XQAFpv-rA4BUIa0TQCDIkdzyKl-AOFV3-oDQ_Hf89fNmh7Yrv_L7eQpSEF2yrlVMnpxs2aRLwoaYCTOMR4GWZ6F67nk79_5sVAGdtnHT6Q6H7Fh2H27A3jFQelxHfziSbk8BruXfQAIqbnxh4w5FZPG3e)
48. [ed.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUHbKpVw0TPZZrr2nvRP4EONjngLNL7lCZs5wRrf8ImIpzPWwCx8ff_ghUuXCG6lDX0FIRxMhbr7j7_VwmkYRvD0KcKpufLbNYsJ5XnZWVluQFKvT4d4HkvuE7rj0Ozxm2FJgvFL4=)
49. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpP4MlUvqhKaSEQmDzQonpDra4lRwRCY0OR5u17KLTFE7pj_6qoAVL_f6XYc54SMMzCHk_Ync3ZRBPerps8OtMZ3bBjp_S70hACMRL524DO3EbgJdiDXU5uijW6UU9BZ_dm-s=)
50. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjjQ9bzAdAq8ITdQ1s9Ppm_Ep6Jows2JBr3LdiQWHamoUYuv0d6epR4xTni2z52xAXtfHHn8kF5sEnNrw9n_0y_yGld6rKvla21SfYNvb86_LubvTGQRsEHMn8XvoOCVBTaZbWS9Y=)
51. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxsp3rzinHr4d8NwPeoaPM6NwBrDfCxB9ej8OEnq1t_UjbjoOfoMj_qC-4xHQp6FDW6n8GCcXlAKrhjrDjbI1xWWjcF7-bTOgr676JiM9ZbdLIfqWfGw0CHviVjO8hjDESYEo3j0G1LOzTtgpeGsgORsIAd0in-JcyRaee8-kW25fuxXYBdB-2-wzHF9JPdyCgaWipaEVMU-zhh7hvS6BROmza1hg5MYeWBzKfkzHDlNKRrS-JN1tahO8wcOsEtr1fRnUTRw==)

