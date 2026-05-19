# FALS-01: Training LLMs to recognize false math claims

**Pythia queue id:** 28
**Tier:** T1
**Priority:** 1
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdZeW9NYXBpaE5fempfdU1QX3RTYWtRbxIXWXlvTWFwaWhOX3pqX3VNUF90U2FrUW8
**Elapsed:** 318s
**Completed at:** 2026-05-19T09:21:38.985296+00:00

---

# Survey of 2025–2026 Research on Falsification-First Training for Mathematical Language Models

**Key Points:**
*   **The Paradigm Shift:** In 2025–2026, AI research transitioned from *verification-first* training (confirming true steps) to *falsification-first* training (hunting for counterexamples and targeted errors). Evidence suggests verification-first approaches cause models to suffer from "model collapse" in epistemic calibration, resulting in overconfidence and redundant confirmatory loops.
*   **The Verification Deficit:** While models like OpenAI's o3-mini can solve up to 48% of algorithmic problems from scratch, they successfully generate refuting counterexamples for less than 9% of subtly incorrect solutions. 
*   **The Illusion of Self-Correction:** Empirical studies reveal that 85% to 95% of large language model (LLM) self-verification steps are merely confirmatory rather than corrective. Models rarely detect actual errors during standard self-reflection.
*   **Falsification Yields Better Calibration:** Frameworks prioritizing epistemically-calibrated reasoning (**EpiCaR**) and Conflict-Aware Meta-Verification (**CAMV**) demonstrate Pareto-superiority. They jointly optimize accuracy and calibration, yielding near-human-level reasoning with up to a 3× reduction in inference compute by pruning useless confirmatory rechecks.

**The State of Mathematical LLMs**
The pursuit of mathematical reasoning in Large Language Models (LLMs) has reached an inflection point. Through 2024, the field relied heavily on process reward models and self-training regimens that reinforced successful reasoning paths. However, recent analyses in 2025 and 2026 demonstrate that this focus on "proving what is right" creates systemic blind spots in "recognizing what is wrong." 

**Why Falsification Matters**
Models optimized to produce correct solutions often fail catastrophically when tasked with challenging false premises, frequently attempting to prove invalid mathematical claims rather than refuting them. Falsification-first methodologies train models to actively search for failure modes, generate counterexamples, and establish localized claims of error. This mirrors the true scientific method and results in more robust, self-aware AI systems.

**About This Report**
This comprehensive report details the state of the art in training language models to identify false mathematical claims rather than simply verify true ones. It synthesizes primary literature from 2025 to 2026 (including major arXiv preprints and conference submissions), surveying novel datasets, falsification methodologies, evaluation benchmarks, and comparative architectures. Ultimately, it evaluates the strongest empirical evidence demonstrating that falsification-first training yields better-calibrated, more reliable mathematical reasoning than traditional verification-first approaches.

---

## 1. Introduction: The Crisis of Verification and the Falsification-First Paradigm

In the past decade, and particularly culminating in the milestones of 2024 and 2025, LLM-based reasoning systems have achieved remarkable success on final-answer mathematical tasks [cite: 1, 2]. Advancements propelled by reinforcement learning with verifiable rewards successfully pushed models to elite performance levels on standard datasets such as MATH and GSM8K. However, as the research community expanded to open-ended, research-level mathematics and rigorous formal proof verification in late 2025 and early 2026, a systemic flaw emerged in the underlying cognitive architecture of these models.

### 1.1 The Epistemic Calibration Problem
Current models exhibit a phenomenon best described as an "epistemic calibration cost." While iterative self-training methodologies—such as the widely used Self-Taught Reasoner (STaR)—are effective at boosting accuracy, they primarily reinforce successful reasoning paths [cite: 3, 4]. This repetitive reinforcement of the affirmative causes models to become overconfident, gradually losing their capacity to represent epistemic uncertainty [cite: 3, 4]. This failure mirrors model collapse in alignment protocols, where predictive distributions degenerate into low-variance point estimates [cite: 3].

The consequences of this miscalibration are profound. A 2026 study introducing the Knowledge and Belief Language Evaluation (**KaBLE**) dataset found that while modern LLMs achieve approximately 86% accuracy on factual scenarios, their performance drops precipitously (to as low as 54%) when faced with false scenarios [cite: 5, 6]. The models operate at scale using fast, associative, and persuasive generation (akin to human System 1 cognition) but lack the deep, reflective capacity required for falsification [cite: 4].

### 1.2 The Self-Verification Dilemma
A cornerstone of verification-first training has been test-time scaling through chain-of-thought and self-reflection. The assumption was that if a model checks its work, it will catch its mistakes. However, a massive empirical analysis published in February 2026, titled *Self-Verification Dilemma: Experience-Driven Suppression of Overused Checking in LLM Reasoning*, definitively dismantled this assumption [cite: 7, 8].

The researchers found that Large Reasoning Models (LRMs) generate long reasoning traces filled with "recheck" steps. Yet, an overwhelming **85% to 95% of these rechecks are merely confirmatory rather than corrective** [cite: 7]. The models engage in redundant re-computation, arithmetic checking, and constraint validation that overwhelmingly rubber-stamp prior intermediate results, rarely identifying errors or altering flawed reasoning outcomes [cite: 7]. This reveals a stark mismatch between how frequently verification is activated by the model and its actual utility in improving epistemic integrity. 

### 1.3 The Popperian Shift to Falsification
To resolve the vulnerabilities of verification-first paradigms, researchers in 2025 and 2026 began embracing a "falsification-first" standard, directly inspired by Karl Popper's philosophy of science [cite: 9, 10]. Under a Popperian framework, a theory or hypothesis is only scientific if it can, in principle, be refuted by empirical evidence [cite: 9]. The process of empirical risk minimization (ERM) and stochastic gradient descent (SGD) conceptually mirrors this: competing hypotheses are assessed and rejected if incompatible with the evidence [cite: 9]. 

In the context of language models, a falsification-first approach mandates that agents should not be utilized primarily to craft compelling, plausible narratives or derivations, but rather to actively search for the ways in which a claim can fail [cite: 11, 12]. In mathematical and algorithmic contexts, this translates to training models to seek **counterexamples**, identify **boundary condition failures**, and generate **verifiable witnesses of incorrectness** [cite: 13, 14]. 

---

## 2. Datasets and Evaluation Benchmarks (2025–2026)

The shift toward falsification necessitated the creation of entirely new datasets and benchmarking suites. Traditional benchmarks evaluated models based solely on final numerical answers, completely neglecting the rigorous reasoning and proof generation required to falsify an invalid claim [cite: 15, 16]. The years 2025 and 2026 saw the introduction of robust benchmarks designed specifically to test inverse capabilities: refutation, targeted mutation, and epistemic resilience.

### 2.1 The REFUTE Benchmark (August 2025 / February 2025)
Perhaps the most significant benchmark introduced for algorithmic and mathematical falsification is **REFUTE** [cite: 14, 17]. Existing benchmarks predominantly assess a model's ability to generate solutions. The creators of REFUTE argued for evaluating the *inverse* capability: creating counterexamples for subtly incorrect solutions [cite: 14, 17].

**Methodology of REFUTE:**
REFUTE operates as a dynamically updating benchmark utilizing recent problems and incorrect submissions from programming and algorithmic mathematics competitions [cite: 14, 17]. The benchmark tests whether an LLM can parse a subtly incorrect solution and generate a specific mathematical or programmatic counterexample \(\mathbf{x^*}\) that satisfies the problem's constraints but causes the flawed solution to fail [cite: 17]. Counterexamples in REFUTE can be evaluated automatically and deterministically using a ground-truth code execution environment [cite: 14, 17].

**Findings from REFUTE:**
The results from REFUTE highlighted massive deficiencies in frontier models:
*   **The Capability Gap:** The best reasoning agents, including OpenAI's o3-mini (high) with code execution feedback, could create valid counterexamples for **fewer than 9%** of the incorrect solutions [cite: 14, 17].
*   **The Verification Paradox:** This catastrophic failure in falsification occurred despite the fact that the same model's Elo ratings indicated an ability to solve up to 48% of the exact same problems from scratch [cite: 14, 17].
*   **Failure Modes:** The researchers identified that models lack effective structural abstraction. When debugging or falsifying, human experts typically critique high-level algorithmic logic first. LLMs, conversely, misallocate their attention to boilerplate subroutines or input/output templates [cite: 14]. Furthermore, LLMs demonstrated severe limitations in boundary condition analysis, failing to stress-test edge cases by systematically varying inputs to their extremal values within constraint boundaries [cite: 14].

### 2.2 MAMUT: Math Mutator (February 2025)
To train models in the art of identifying false mathematical claims, researchers require vast quantities of high-quality, specialized data containing both valid and invalid variations of formulas. In February 2025, researchers introduced **MAMUT (Math Mutator)**, a novel framework designed to generate equivalent and falsified versions of mathematical formulas in LaTeX notation [cite: 18, 19].

**MAMUT Algorithms:**
MAMUT leverages symbolic representations to create datasets via two core algorithmic pathways:
1.  **EquVG (Equivalent Version Generation):** Creates mathematically valid variants through symbolic transformations such as commutativity, associativity, variable substitution, and LaTeX formatting variations [cite: 20].
2.  **FalseVG (Falsified Version Generation):** Intentionally injects mathematically invalid, yet structurally plausible, variations of formulas [cite: 20, 21]. 

By minimizing shallow lexical overlap (e.g., ensuring query formulas and document formulas do not share the exact same variable names), MAMUT forces the LLM to focus on underlying semantic equivalence and logical truth rather than relying on superficial pattern matching [cite: 20]. Models trained on the four massive datasets generated by MAMUT exhibited state-of-the-art (SoTA) performance on mathematical retrieval and verification tasks [cite: 20].

### 2.3 RealMath and Hard2Verify
While competition mathematics (like the IMO and USAMO) have been standard yardsticks, models have historically learned to game them through dataset contamination [cite: 22]. 
*   **RealMath (October 2025):** Derived directly from research papers (arXiv) and forums (Math StackExchange), RealMath evaluates models on authentic research mathematics [cite: 2]. It specifically tracks failure modes such as incorrect arguments, missing critical insights, and logical inconsistencies [cite: 2].
*   **Hard2Verify:** An open-ended frontier math benchmark demanding step-level verification [cite: 1]. It acknowledges that in modern LLM reasoning, catching step-level mistakes is a mandatory prerequisite for open-ended proof generation [cite: 1].

### 2.4 KaBLE: Knowledge and Belief Language Evaluation
To quantify epistemic drift, the **KaBLE** dataset (13,000 questions across 13 tasks) was developed to test epistemological reasoning [cite: 5, 23]. It uniquely evaluates models on their ability to distinguish between factual and false statements across ten domains [cite: 6, 23]. 
The dataset revealed that LMs lack a robust understanding of the factive nature of knowledge (the principle that knowledge inherently requires truth), relying heavily on linguistic cues for fact-checking rather than executing deep, causal falsification [cite: 6]. 

---

## 3. Methodologies and Comparative Architectures

To address the profound deficits highlighted by REFUTE and KaBLE, the 2025–2026 period yielded novel architectural interventions and training objectives. These methodologies pivot away from reinforcing successful long-horizon generation and instead formalize reasoning as a process of adversarial critique, conflict identification, and epistemic calibration.

### 3.1 Epistemically-Calibrated Reasoning (EpiCaR)
Published in January 2026, **EpiCaR** directly targets the calibration cost associated with iterative self-training [cite: 3, 24]. In standard reinforcement regimens, models learn *how* to reason, but fail to learn *when* their reasoning should be trusted [cite: 3].

**The EpiCaR Architecture:**
EpiCaR reframes mathematical training as an epistemic learning problem [cite: 3]. It integrates explicit self-evaluation signals into an iterative supervised fine-tuning framework [cite: 4, 24]. 
The framework operates on an iterative dual-loop process:
1.  **Generation Phase:** The model produces multiple reasoning paths for a given input query [cite: 24].
2.  **Mixing Phase:** Outputs are synthesized and evaluated.
3.  **Dual-Objective Optimization:** The system jointly optimizes problem-solving accuracy alongside self-evaluation metrics [cite: 24]. 

By explicitly externalizing uncertainty (a concept referred to as epistemic verbalization), EpiCaR allows the model to map the limits of its own knowledge [cite: 4]. When applied to the Llama-3 and Qwen-3 model families (specifically at the 3B+ parameter scale), EpiCaR generalized effectively to out-of-distribution mathematical reasoning (GSM8K) and code generation (MBPP) [cite: 3, 24].

### 3.2 Conflict-Aware Meta-Verification (CAMV) and Co-Sight
Another major architectural leap is the **Co-Sight** framework, featuring **Conflict-Aware Meta-Verification (CAMV)** and **Trustworthy Reasoning with Structured Facts (TRSF)**, introduced in October 2025 [cite: 25, 26].

**The Failure of Full-Chain Verification:**
Long-horizon reasoning typically fails because evaluating massive, continuous chains of thought is computationally exorbitant and prone to attention degradation. 

**The CAMV Solution:**
CAMV reformulates verification not as a holistic review, but as **conflict identification and targeted falsification** [cite: 25, 27]. 
1.  **Disagreement Hotspots:** CAMV monitors multiple expert agents (or sampled reasoning paths). Instead of verifying everything, it allocates computation *only* to the specific steps where reasoning paths diverge or conflict [cite: 25, 26].
2.  **Constraint-Based Pruning & Consensus Anchoring:** Once a conflict is identified, the system attempts to falsify the diverging claims. This bounds the verification cost to the number of inconsistencies rather than the full trajectory length [cite: 26, 27].
3.  **TRSF Module:** TRSF acts as a structured facts module, continuously organizing and validating evidence through a three-tier context compression (tool, notes, and facts levels). This ensures that attempts at falsification are grounded in verified, traceable information [cite: 25, 26].

Together, TRSF and CAMV create a closed verification loop: TRSF supplies auditable facts, and CAMV selectively falsifies or reinforces them, achieving 84.4% on GAIA and resolving test-time inverse scaling [cite: 26, 28].

### 3.3 Critique-Resilient Benchmarking
In February 2026, researchers recognized that as AI surpasses human ability to easily spot subtle mathematical errors (the "post-comprehension regime"), evaluation must become automated and adversarial [cite: 13, 29]. 

**Bounded Verification of Localized Claims:**
The researchers established a falsification-first definition of correctness: an answer is deemed "critique-resilient" (correct) *only* if no adversary can convincingly prove otherwise within a bounded budget [cite: 29, 30]. 
This approach leverages an asymmetry inherent in mathematics: while verifying an entire 50-page mathematical proof may be computationally infeasible, checking a specific, localized alleged error (a falsification witness) remains highly tractable [cite: 13, 30]. An automated LLM-to-LLM process is established where "critic" models actively attempt to produce local, verifiable claims of error against a generator model. Humans are relegated to the role of bounded adjudicators who only evaluate the short, checkable certificates of failure [cite: 13, 29].

### 3.4 Multi-Agent Debate (MAD): Skeptic vs. Supporter
Agentic approaches have also formalized falsification-first training via role-playing. In multimodal reasoning and fact-checking evaluations (such as those using MCTS and MAD), architectures explicitly instantiate two agents with complementary roles:
*  **Agent A (Skeptic):** Operates on a *falsification-first* mandate, actively searching for discrepancies, contradictions, and logical misalignments [cite: 31, 32].
*  **Agent B (Supporter):** Operates on a *verification-first* mandate, aggregating supporting evidence [cite: 31, 32].
These round-based debate processes demonstrated that injecting dedicated falsification logic significantly outperforms standard generative pipelines by mitigating the non-causal authenticity assumptions that standard models make [cite: 31, 32].

---

## 4. The Superiority of Falsification-First over Verification-First

The core of the user's query asks for the strongest evidence that falsification-first training produces better-calibrated reasoning than verification-first approaches. By synthesizing the primary papers from 2025 and 2026, a compelling evidentiary consensus emerges. Verification-first creates computational waste and epistemic blindness; falsification-first creates efficiency and epistemic resilience.

### 4.1 Evidence 1: Eradicating the "Self-Verification Dilemma" 
The strongest behavioral evidence against verification-first training is the empirical reality of how LLMs utilize it. The February 2026 study *Self-Verification Dilemma* proved that standard verification (asking a model to "double-check" its work) results in 85% to 95% of rechecks being merely confirmatory [cite: 7]. 
Models suffer from "overthinking," burning token budgets to essentially output "Yes, my previous step looks correct" without rigorously testing the logic [cite: 7]. 

By applying a falsification-first intervention via **Experience-Driven Suppression (EDS)**—which detects when a model is entering a useless confirmatory loop and suppresses it based on a historical experience pool—researchers achieved a **20.3% reduction in token usage** [cite: 7, 8]. Crucially, removing these verification-first loops maintained accuracy and, in several datasets, actually *yielded accuracy improvements* [cite: 7, 8]. This proves that verification-first behaviors are not just inefficient; they introduce noise that degrades overall reasoning calibration.

### 4.2 Evidence 2: EpiCaR's Pareto-Superiority and Compute Reduction
Further evidence is found in the January 2026 paper introducing **EpiCaR** [cite: 3, 24]. The authors directly compared EpiCaR (a falsification/epistemic-aware objective) against STaR (a verification/reinforcement-based objective).

**Results:**
*   **Accuracy and Calibration:** EpiCaR achieved Pareto-superiority over standard baselines in *both* problem-solving accuracy and calibration on Llama-3 and Qwen-3 models [cite: 3, 24]. 
*   **Compute Efficiency:** Because EpiCaR models learn *when* to trust their reasoning (epistemic uncertainty) rather than blindly verifying, they require vastly fewer test-time scaling rollouts. EpiCaR achieved a **3× reduction in inference compute**, matching the performance of STaR at \(K=30\) samples using only \(K=10\) samples [cite: 3, 24]. This indicates that falsification-first training instills a highly calibrated internal sense of when a proof is logically sound, negating the need for brute-force verification scaling.

### 4.3 Evidence 3: Overcoming the "Wrong Direction" Failure Mode
In May 2025, an evaluation of state-of-the-art models (including GPT o3-mini, Claude-3.7-Sonnet, and DeepSeek R1) on creative mathematical problem solving highlighted a severe algorithmic handicap termed the "Wrong Direction" bias [cite: 33]. 

When mathematical problems explicitly requested the construction of a counterexample (a falsification task), models frequently misinterpreted the prompt due to their verification-first training priors. Instead of refuting the false claim, the models would stubbornly attempt to construct a direct proof for the invalid proposition [cite: 33]. 
Conversely, CAMV (Conflict-Aware Meta-Verification), which inherently operates on targeted falsification, overcomes this by bounding the reasoning task to *identifying the disagreement* [cite: 25]. CAMV achieved 84.4% on the GAIA benchmark and 35.5% on Humanity's Last Exam by specifically transforming reasoning from a detriment into a gain, effectively neutralizing inverse scaling laws observed in traditional verification [cite: 25, 26, 28]. 

### 4.4 Evidence 4: The Sub-9% REFUTE Falsification Rate
Finally, the REFUTE benchmark serves as the ultimate indictment of verification-first paradigms. A model trained heavily on verifiable rewards (o3-mini) can construct a valid mathematical solution 48% of the time, yet can only generate a counterexample to an invalid solution less than 9% of the time [cite: 14, 17]. 

This stark numerical delta mathematically proves that verification-first training does not generalize to generalized logical rigor. Verifying a true statement requires stringing together known algorithmic templates (which LLMs excel at via pattern matching); falsifying a claim requires systemic reasoning over input domains, boundary condition stress-testing, and structural abstraction—skills that are only developed through rigorous falsification-first training datasets like MAMUT and objectives like EpiCaR [cite: 14, 20].

---

## 5. Summary and Future Directions

The scholarly landscape of 2025–2026 marks a decisive turning point in the training of mathematical language models. The realization that verification-first training pipelines (which dominated the 2022–2024 era) lead to epistemic miscalibration, unyielding confirmation bias, and massive inefficiencies during inference has sparked a rapid pivot to falsification-first architectures.

1.  **Datasets:** Tools like **MAMUT** are automating the generation of negative mathematical space, providing the necessary LaTeX permutations to train models on what *looks* correct but is fundamentally flawed [cite: 18, 20]. Benchmarks like **REFUTE** and **KaBLE** act as the ultimate arbiters of this new paradigm, shifting the metric of success from "can it solve this?" to "can it break this?" [cite: 5, 14].
2.  **Architectures:** Methodologies like **EpiCaR** and **CAMV** explicitly encode epistemic uncertainty and conflict-targeting into the optimization loop [cite: 24, 25]. They prove that searching for points of failure is computationally cheaper and mathematically sounder than verifying entire chains of thought.
3.  **The Evidence:** The empirical data is incontrovertible. Falsification-first methods reduce inference compute (up to 3× in EpiCaR) [cite: 3], slash useless token generation (by 20.3% via Experience-Driven Suppression) [cite: 8], and achieve Pareto-superiority in both accuracy and calibration [cite: 24]. 

As the field approaches the "post-comprehension regime"—where frontier models output mathematical derivations too complex for human peer-reviewers to verify holistically—the reliance on localized, falsifiable witnesses of incorrectness (Critique-Resilient Benchmarking) will become the only viable path forward for artificial mathematical reasoning [cite: 29, 30]. By teaching machines to act as rigorous, Popperian skeptics rather than agreeable supporters, the AI community is taking a foundational step toward true mathematical intelligence.

**Sources:**
1. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKDcUAEOwdlLXhJzDJVQlmhlJlg-3nV0icI7Z_BKTeTDqEM0hHDQ1utW4zwRQCacU4LYCRCgQHCQcpyfObCo-fff5XAmPcD5zVdMlCA3qnzIEgJl_kCe3I-yGkbG5o8wAQA9kfYkQ1UfVHkCSiErSYd9ypKi60vqg=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEm8CSn6iu7w2nPH_ZlviDTfhuIZg5dmqrkz8nRx6-g2xp-CReUZay1Xg9Ob9kbRl3ywlFGl32A7oNC35n54HqH1vgiu_dFeQVe2Zh3BweOo9zA4DIqkubeTg==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_yy7bE83dxGR9eciV0oBgbIhRz62ol2k75K9PHqbbIg4iD6FN19qy286_sSQ9yJSKBWR9jMUVWZzvAHpqZENWe7o_6NzNhqC0TS_RNFSQtagZ4WkmMw==)
4. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzjCx8Kw37J1zdgUwSQKJ13mQJUGEagwDr0cxIR03fP9sART5Z8fJqkVLiNm7jgjD8BzaJACJwjACUvobYFcnjNW3oRsxri5nivOazJ1Md7hZ9wU_BoiZTx6EpxwE1Mn3UAiKlTgH4Al0Fsg==)
5. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEhCfvNrFiOe7GaSdCxB12Aumqv-eukEF1vJzEwB2-l_NZhK8ZGqdU1LEtrUyFeox7sKuz6uor62sGWFGMmFeZ4Z-3QZ9WfuyyrwUOcTmkRo1nB5GzuFvhZf6ugSMsCRLwa1u1yy8l2tm2pvSTr2AFCyn42ocxq0Ve9w==)
6. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPgkiovSYsl6sDlEgnKwqxI1crcOA1RtDbiwbN7WdF1Kkq4Rm0odcDiXCcRQw5Z5Y2tNRUA_bY-ARlIr1zXgUxs2fCJtxxSHMwPCoSQOJLaRjUG-OcSYyHWXZOORvRPMhN-cn0CYmWpHWT)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuUY17SDNpzT8AgvQdart7ZiXbOdzoLTdqCcW8j18eJ4Qnccivs5UbXB-oy8rISgee4Z_cGDymhyZAOdc-bTM8xdXsz7OvhMHMOMeydLAOA4UTGsIzSRYAjQ==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRnF5LiocT6SjcNtyvX3hKNEG4mxPeDzQU6yjwkY_P3bXi52MlxBJuJqnbVQ3ZgvxVS0SflrofMyzHQXn-3NryYAenmeQlxnfj8P57AOQnRiOf0ZooCQ==)
9. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmMtP-JPsH3DcOTj-kaL2gO2ovLT5YC_OtdDnLAjzeC0V9fllRux2ScFXT5MBHsLbSyBjuoJKyxw5loYTlFAKmcDpuELg4AGcEaJByd4cBawWeR-VpFycyFmysIeGNMWxL6-1h6D69w6sS)
10. [effectivealtruism.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaZXCdvICySZyrUAt7f8JiXNGO1QEHf1tV44nyIkzYS6cmx6KaXshYny4RpnApmZJ1Tf9-V-hvWsicNaPDBaJK9Z5buwcADBRnzbqvZdrQIAaVyf8LlTTqNfe6fx2WYyu7E6FO_MDEvSVNcgjoT2lGafXDpcJorxs1ZLReLeNhvMxwpGUWXSdS7gIqn82xuP87R1AqouSEoHUUB1BpIa9ewfks_iIBgzM=)
11. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8sgYOHhIr4V2mxHEx1a1EdARiS6PtJMAZJjyEzCD1_yf4dZ9kZQ22SZirPqO8QLl5v8IBJGt9FRzN_0bdPjJCbL4wYnqTm6H2hs0CHMJs0uSe1XoYcIRkAJ3K6KK1r63bmBgd2Z6RuunBn9ZYE_7mMikdzyz6AV_3ModO_QzBSzn0jdvGX5EExAnJdFelgP_eaFhuM5TuohtFJm-brL6V8Z6LE4Dd88Z_iHOYx0lbLijYhCnlNLw2KEgzAya3zg==)
12. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPbkHY7_YLwQs02g2LUV8JpP8zwKEwKzFjlanu57-Pdjt9SK2hZMInBOFBYHbe9bxlnlFwMgt6H7N6GFZ0cIe6alGGTEJ2lM0N4yCFzb53FgjQF6LbMYwv4X6qfYh8UD3MFiSHzuzyX5xtorjt6A==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeNR8nxqHA7WJyTni8ViFqDETyjMUXESKQcIH_MsrHX5Y5jXoFujPNB-7gIyM9RjE9ZljbIvdp9vztWKxJq_h_aEAxJrzPJkj0iHgP46RB1-XtfAw_P6kahg==)
14. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpFCZtXtqdjdS-3qtZlPsZSyj037A2Xh4A4x6yUB7RCfzM_hCLQK5r5IAILoL8Rgh33BjvIko_6pzjkOtN1fcJcr0N1OMzYy9Jc4T2H5Xzzwxnq9bdME1L2w8rFC6O-K0=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWgIkQ1N9UVC0gJFAICSVA0bGDJ07foJQGmp7RTwfywfY8qzmOTRhAmP42hADGYr4GlFztg309wP1pSR-p1Xi1SkOg5uk-Q7OPrBHKc7jysBoeoXdP2Q==)
16. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmNhn9rxzkI7APIJ_fyJ68gVVxKJr_aSCr6-9K4CdkfFTGtdAD5CvMjZ9SiZ9T7mzTtHSVE5tgY8I7C-be5z432BLUTt_LHXnYsJl054xdQPzO8rQp7cGZ)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFigo3NnFrjWRZgcEAsACch6mcdPXgcwvFH7Qs9ZAeRFspPRANq24gENXLu8E-p2NB2nyvYzMi2PfYJBB3z2CjjJPbMCGWUIQM7JD6xUlvaqthVx-_FR4g8OQVLxlhjSuz_mERGTQg5f43c6oVp80ZtTunfB4kDPHofKbIB9CTtuQnLhyQi11doRLaCzktFNe9Av_Fl7BMmKtj4zOORXNbj7DUY7-KRLvDVQ8XjPUcAvZqQRHCNUBIit0BCD8GkV09-V7s=)
18. [opentrain.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERTx3ZdI6bf0InWqiVMWKvRF7uDBsL3t80VbqwnKcJ-oYVYfWuqXqV143IS1rBwsjB-siyR0KWkttCtQrIi_VleCYqcOrsTm1F_WA3PpWo69VQxCogWiBru76mp0qI0DRh5fi8UB_k0yeWMG9mJuoMUiMlkb8EVtGaKvcYRhS-n4m2_wzTmHvl5wRvvDAo5V1s91csDwqPKQOfXr-broSU_ky_p-j0n4agy5e5QZGSvG2TdWe8xOTNMUQ=)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4HRiUsOn_UeeP6WlfBv6Bw58R2hw4wS06UEde9ZmeZ5iKNvflzmLogljKQHTtuIyc7U6Gs5mdV8DIfNSpKVUygvLSlEo10HUMVKINqCYqiVIGxhcAeQ==)
20. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNkZbZLw4adw9pkjtz5wn8enDWaUV380Wrsw_5dSNo6fy3W2jwbOcI17JgWeBfDZfF2oMUx4voaoF-4b17D27U3XVwS4LKhha6aK2AItGkVkn980L0sg645doE0YXfvtet7uNp8DI9kjUfeWSg3x6JqKoNYFkgeubyy_e4yRIh_Gfc82bBigQqdm7ZgT5SXG-zkakGqNNtvDMFqktlyKQzP2PcVCMqwMhvoI-8cWbV1JV17ZKUdQB--_Vcuu_G3AY=)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFicHgjyPSALa7WWSuxW3yAnABOIaHWLhfGFEZJ-PT-B683_ntJQsyOAx9WAZwZsyc3Ko4S2-G5G2g_NpMsIqd3MMvxLbHmNfmO72GwSbRrtaOoRrNuEB65pA==)
22. [apolo.us](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTQgd2UDYqpkyclspTKHB8JXl0npDkZcCdUycShe9cHceGWpKgUIt3OKIXSWlReJCgF7BYRGxFQQK5H-af9bITUgZyHMxxzpI2WPEIrYJzBwQdcCC_BmjRo_chAjXdW6nIOUt8hZN6_b7oQyu13svojRLVuyZ_uLvXh6ml9gsHOls4OftKLz058FchCjLsvVnG92lKURVn8hy2cvxg1Ligr_aKoQH5ag==)
23. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH95MAtR1LpG-4Iokx1k5Asv_Sj-seIQVZ1uCKla2myVnQIeIeTL9tZQWNNdtJB0q3dp7qR16DW-ITC32VvEhJQ80XogXKGyxlEPlC-ayv3KSDQtu0_JCGKe6X0hXUQ02YUJzjrHznmgCeiJA==)
24. [hyper.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyUnAHNKIcmvHwzy9gOCUtnFBe9JIE3pqur8cDaLkDPBqvbKi5sht28467PdCQ3nk9MFtvp-CAQ3BgG8IWFjKXn2XaXHpaT9GUdAg1ze5WjBVBfcCUtSuqvXKu0eYR1e8=)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9tCwPROe1z6y12bTbku_SUWn6jhR7TejJe-m1bHyagq6KWZQlHRA8Fo0XZv51NM1UCPwX-U8SYvgNsqKMSE-zOWwdKHzrZysYsFESsrBmrkmxQUgABQ==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLfZoSmspEMq7d1XA_3P8RMtfEPUWYyPSB2nhGb4KgjLl7ZjMr1DvWePjUAXXPjGofG2Zneq-68pt8fx1fRyd41DC_tzboak7YsvmxBnv22g623RxLjzx3HQ==)
27. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2FtindqcvFOnl_yQL3V0y-r0NQinvi4XK2FNzUqXSxXWo1YNoUs5q9scQouORow7l8NTrbfplRsF2ozLiRxX02iEb5FChZtFRVnBxtGlTMejkhLzJu6UeL2uWSRcyQSH-OY5qE410QLEPv9Uy13xx-CV87DmYbG2w)
28. [arxivdaily.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFphwOGFNbKFTnIaCGKuCm9xOQpIYP4C_ZAaA_kQOdGCwUBDF-5n_32LuGABqOJ_phojXUtLRhIwMLEmBEYIx8X3SHXi24_F6P1DZ7UQoaLOD7TK54Y2Yb-4Oi3a2k=)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYcCgdeigRwEyQ0PVFyLA_yWthldej6W1lrVV16U9AxXyp3pJnAsmUYiGWuZF5o1j9vWKgNshZA_eEEDDUv9mcawzYpwMrkLHhyhkE3k5BbIixXLmklA==)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSdmICu3jzMwIsn2wf9waHpLbMoLU9sB5kHABgLFRwk5ByDXOU4eRNDKWFwlxU4n1q5AJqAIo5oeq3vHkkgsuXwDJM8clW24IKxwCNoWJE1gJ__-7gRw==)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSv8cNcAJYa7Ev0acLWSKRqVgMNdQp0Cr4DAZsvlJsPmm5_vGsUnGvi-Nqs_HiZ8_Ep9IDazUH-sPXENXDqZJNxnoOEbiWiKS3J7uInSz0BIKRHwTXkm_ORQ==)
32. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRYUPM9DXPc4IKtj5c1cG2_I1JaKg-YiKNtbURI1oUOzN95Y3Pf5iiyM3e6bjRoAHSd4oSSdJKf6WSg3FWHy7tEvAlo79Wn7q4qHdb2BHPqVVTiaUmWO0J6km0qTOKmoQRyDrKLjOg2OI0_B-rW4xVgm_-)
33. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLWn5PhlVa5cAdaAruWcbGktqKiRLZ-G-EQMT15wn5wYFizlY-7pyuEHB5QvkyjWJOucarvmvnfpvivbXgPZ-rzCBtuiLuCY6OkZiQ1sNCihkNFF2rDQ==)

