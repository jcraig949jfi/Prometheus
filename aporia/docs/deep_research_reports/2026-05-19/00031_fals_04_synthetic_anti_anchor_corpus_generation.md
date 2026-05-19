# FALS-04: Synthetic anti-anchor corpus generation

**Pythia queue id:** 31
**Tier:** T1
**Priority:** 1
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdaU3NNYXNyWEpJT2RfdU1QNDcyUnlBWRIXWlNzTWFzclhKSU9kX3VNUDQ3MlJ5QVk
**Elapsed:** 879s
**Completed at:** 2026-05-19T09:35:17.430704+00:00

---

# Methods for Generating False-But-Plausible Mathematical Claims for Training Data: A Comprehensive Analysis

### Key Points
*   **The Necessity of Negative Data:** Research suggests that training Large Language Models (LLMs) exclusively on correct mathematical proofs limits their ability to recognize subtle logical errors. High-quality, "false-but-plausible" negative examples appear essential for establishing robust decision boundaries in automated reasoning.
*   **Counterfactual Perturbation Shows High Scalability:** Methods that systematically alter the abstract syntax trees of math problems or drop hypotheses from formal proofs (e.g., in Lean 4) have demonstrated significant scalability, allowing researchers to generate hundreds of thousands of verifiable negative examples automatically.
*   **Hypothesis Softening Exposes Edge-Case Vulnerabilities:** By slightly relaxing the constraints of established theorems, developers can create plausible but false claims that successfully trick models, mimicking historical mathematical misconceptions. 
*   **Mimicry and Similarity Exploit Heuristic Reliance:** Techniques like citation-form mimicry (faking proof structures and references) and prove-by-similarity attacks (applying valid logic from one geometric shape to a slightly different one) reveal that LLMs often rely on pattern matching and stylistic "vibes" rather than rigorous deductive logic.
*   **The Failure of Naive Rejection Sampling:** Evidence leans toward the conclusion that simply using incorrect model outputs (rejection sampling) fails to provide sufficiently "hard" or instructive negative examples, as these outputs often contain trivial arithmetic or formatting errors rather than deep logical flaws.

### Introduction to the Paradigm Shift in AI Mathematical Reasoning
In recent years, the intersection of artificial intelligence and mathematics has witnessed a paradigm shift from simple pattern matching to complex, multi-step logical reasoning. While supervised fine-tuning (SFT) on vast datasets of correct proofs and step-by-step solutions has yielded impressive results, this approach is reaching a point of diminishing returns. Models trained exclusively on positive examples often struggle to identify subtle logical fallacies, hallucinate steps, and fail to generalize to out-of-distribution problems. To bridge this gap, the focus has shifted toward training paradigms that incorporate high-quality negative examples—specifically, false-but-plausible mathematical claims and reasoning traces. 

### The Challenge of Defining "Plausible" Falsehoods
A significant hurdle in this domain is generating negative examples that are genuinely instructive. A mathematical claim can be false in trivially obvious ways (e.g., $2 + 2 = 5$), which provides minimal training value for advanced models. Conversely, a claim can be false in a highly sophisticated manner, requiring deep domain expertise to debunk. The goal of generating false-but-plausible claims is to target the "uncanny valley" of mathematical reasoning: claims that perfectly mimic the syntax, vocabulary, and structural flow of a valid proof but contain a fatal, heavily disguised logical flaw. This report comprehensively explores four primary methodologies for generating such data—Counterfactual Perturbation, Hypothesis Softening, Citation-Form Mimicry, and Prove-by-Similarity Attacks—analyzing their implementation, scalability, and limitations.

---

## 1. The Epistemological and Computational Foundations of Negative Mathematical Data

Before delving into specific generation methodologies, it is crucial to understand why false-but-plausible mathematical claims are computationally necessary for training modern Large Language Models (LLMs) and neuro-symbolic AI systems.

### 1.1 The Limitations of Positive-Only Training
Historically, LLMs have been trained using Supervised Fine-Tuning (SFT) on datasets comprising human-written or synthetically generated correct mathematical solutions. While this enables the model to mimic the structure of a proof, it fails to teach the model the underlying boundaries of logical validity. In the context of formal theorem proving, natural language proving is inherently much easier to fake than formal proving; every reasoning step must be rigorously specified, and even minor syntax errors or logical leaps can lead to invalid proofs [cite: 1]. 

When LLMs are trained only on correct data, they develop a heuristic reliance on stylistic markers of correctness. They learn what a proof *looks* like rather than what makes a proof *true*. Consequently, when tasked with evaluating a novel claim or generating a long-horizon proof, they often hallucinate steps that sound mathematically plausible but are logically disconnected [cite: 2, 3].

### 1.2 The Rise of Process Reward Models (PRMs)
To address the shortcomings of SFT, researchers have increasingly turned to Reinforcement Learning (RL) guided by Reward Models. While Outcome Reward Models (ORMs) only evaluate the final answer, Process Reward Models (PRMs) evaluate the correctness of each intermediate reasoning step [cite: 4, 5].

To train a robust PRM, one must supply it with both positive (correct) steps and negative (incorrect) steps. However, treating all incorrect responses as equally informative overlooks the crucial role of sample quality [cite: 6, 7]. Rejection sampling—a common technique where a model generates multiple answers and the incorrect ones are used as negative data—often yields trivial errors, such as basic arithmetic mistakes or formatting failures [cite: 6, 8]. 

To truly refine a model's deductive capabilities, the negative training data must consist of **Plausible Negative Samples (PNS)**: responses that exhibit expected formatting, structural coherence, and sophisticated reasoning, but ultimately rely on a false mathematical claim or a subtle logical error [cite: 6, 7]. 

---

## 2. Counterfactual Perturbation

**Counterfactual Perturbation** is a highly systematic methodology for generating false-but-plausible mathematical claims by making precise, localized changes to a known true statement, problem, or proof. The core philosophy is to preserve the macroscopic structure of the problem while altering a microscopic, critical element that invalidates the original conclusion.

### 2.1 Abstract Syntax Tree (AST) Modification in Math Word Problems
One of the most successful and scalable implementations of counterfactual perturbation targets Math Word Problems (MWPs). While language models excel at natural language comprehension, they often falter when the underlying numerical logic of a problem is adversarial manipulated [cite: 9, 10].

Researchers have developed pipelines to structurally generate adversarial examples by perturbing numeric values while preserving the problem's natural language coherence [cite: 9, 11]. The methodology operates as follows:
1.  **Code Conversion:** A known, solvable MWP is fed into an LLM to generate a corresponding Python script that models the solution [cite: 10, 11].
2.  **AST Construction:** The Python script is parsed into an Abstract Syntax Tree (AST). In this tree, leaf nodes typically represent the numeric variables of the problem, while non-leaf nodes represent mathematical operations (addition, multiplication, etc.), culminating in a root node representing the final answer [cite: 9, 10].
3.  **Constraint-Based Perturbation:** The variables in the leaf nodes are counterfactually perturbed (e.g., changing a value from 5 to 7). However, to ensure the resulting problem remains plausible and educationally valid, strict node-level constraints are applied. For instance, if a problem involves physical objects, a constraint ensures that perturbed variables do not result in negative object counts or fractional humans [cite: 10].
4.  **Recomputation:** The AST automatically recomputes the new ground-truth answer based on the perturbed variables [cite: 10].

**Why this works:** This method creates an adversarial environment where an LLM cannot rely on memorized answers from its training corpus. By simply changing the numeric values through AST perturbation, researchers have demonstrated significant degradation in the problem-solving ability of frontier LLMs, proving that the models often memorize surface-level associations rather than mastering the underlying algorithmic logic [cite: 9, 12].

### 2.2 Symbolic Mutation in Formal Theorem Provers (Lean 4)
While AST perturbation works well for arithmetic word problems, higher-level mathematical claims require a different approach. A groundbreaking method for generating plausible counterexamples involves **symbolic mutation** within interactive theorem provers like Lean 4 [cite: 13, 14].

Mathematical reasoning demands two complementary skills: constructing proofs for true statements and discovering counterexamples for false ones. However, training data for existential theorems and counterexamples is exceedingly scarce [cite: 13]. To synthesize this data, researchers employ a counterfactual perturbation technique called "hypothesis dropping":
1.  **Theorem Extraction:** A universally quantified, formally verified theorem is extracted from a library like Mathlib [cite: 13].
2.  **Hypothesis Discarding:** A critical hypothesis (premise) required for the theorem's validity is systematically discarded [cite: 13, 15]. For example, if a theorem states "For all continuous and differentiable functions $f(x)$...", the perturbation might drop the "differentiable" hypothesis, leaving "For all continuous functions $f(x)$...".
3.  **Counterexample Generation:** Because the necessary hypothesis is missing, the modified theorem is now a false claim. The LLM is then tasked with generating a formal counterexample in Lean 4 to prove that the mutated claim is false [cite: 14].

This method synthesizes hundreds of thousands of high-quality, formal negative examples. It provides a multi-reward expert iteration framework, rewarding the model for successfully disproving the mutated claim, thus heavily reinforcing its understanding of why specific hypotheses are logically necessary [cite: 13, 14].

### 2.3 Critical Token Fine-Tuning (CFT) via Counterfactual Verification
At the token level within LLMs, counterfactual perturbation is used to identify and isolate the exact point where a mathematical reasoning chain succeeds or fails. **Critical Token Fine-Tuning (CFT)** relies on perturbing tokens to assess their functional indispensability [cite: 16, 17].

In this framework, a token in a correct mathematical solution is counterfactually replaced with alternative candidates. The model then generates the rest of the continuation. If all top-$k$ perturbations result in an incorrect final answer, the original token is deemed a "critical token" [cite: 16, 18]. 

By treating these counterfactual failure paths as negative examples, the model learns the precise boundaries of logical necessity. Standard SFT uniformly updates all parameters, treating all tokens as equally important, which dilutes the learning signal. CFT focuses gradient signals exclusively on these decisive reasoning steps, enhancing both generation accuracy and output diversity while preventing overfitting to non-critical stylistic tokens [cite: 16, 17, 19].

---

## 3. Hypothesis Softening

**Hypothesis softening** is a technique deeply rooted in the history of human mathematical discovery, and it serves as a highly effective method for generating false-but-plausible claims for AI training. In essence, it involves taking a robust mathematical theorem and slightly relaxing (softening) the preconditions or boundary conditions, resulting in a statement that "feels" intuitively true but is technically false.

### 3.1 Historical and Epistemological Context
Throughout the history of mathematics, brilliant human minds have fallen victim to hypothesis softening. Mathematicians frequently held false, intuitively reasonable ideas that were backed by what they believed to be rigorous proofs, only to be debunked by pathological counterexamples later [cite: 20].

A classic example is the assumption regarding continuous functions. In 1821, Cauchy proposed a proof that a convergent infinite series of continuous functions is necessarily continuous [cite: 20, 21]. Intuitively, this hypothesis softening—assuming convergence alone is sufficient without requiring *uniform* convergence—seemed perfectly plausible. It was only years later that Abel pointed out Fourier series that served as counterexamples, and the concept of uniform convergence was formalized to fix the softened hypothesis [cite: 20].

Similarly, the Weierstrass function shocked the mathematical community in 1872. Prior to this, it was widely believed (a softened hypothesis) that every continuous function is differentiable except perhaps at a set of isolated points. Weierstrass produced a pathological real-valued function that is continuous everywhere but differentiable nowhere, proving the softened assumption completely false [cite: 22].

### 3.2 Applying Hypothesis Softening to AI Training
To train an AI, generating claims based on softened hypotheses is an excellent way to test the depth of the model's rigorous understanding versus its reliance on intuition. 

**Methodology:**
1.  **Identify a strict theorem:** e.g., "If a sequence of continuous functions converges uniformly to a limit function $f$, then $f$ is continuous."
2.  **Soften the condition:** Remove the word "uniformly."
3.  **Present the claim:** "If a sequence of continuous functions converges to a limit function $f$, then $f$ is continuous."
4.  **Task:** Ask the LLM to prove or disprove the statement.

When presented with such claims, baseline LLMs often hallucinate a proof confirming the false statement, mimicking Cauchy's historical error, because the statement aligns closely with the statistical distribution of mathematical texts in their training data [cite: 20]. 

In pedagogical settings, asking students to evaluate a random mix of true statements and softened false statements forces them to read proofs critically, as they can no longer assume the textbook is only asking them to prove truths [cite: 23]. Similarly, integrating softened hypotheses into LLM training datasets forces the model to engage its internal verification mechanisms rather than relying on surface-level semantic familiarity.

---

## 4. Citation-Form Mimicry and Hallucination Injection

**Citation-form mimicry** targets the linguistic and structural presentation of mathematical writing. It exploits the fact that LLMs are exceptionally good at replicating the "vibe" or style of a specific domain. By wrapping a false claim in the dense, authoritative syntax of a formal mathematical proof, including fake citations or misapplied lemmas, the claim becomes highly plausible to both human laypersons and uncalibrated AI evaluators.

### 4.1 The Threat of Mimicry
An LLM might state: *"By applying the Cayley-Hamilton theorem to the boundary conditions of the manifold, it trivially follows that..."* 
If the Cayley-Hamilton theorem (which relates a square matrix to its characteristic polynomial) has absolutely no relevance to the topological manifold being discussed, the logic is entirely broken [cite: 24]. However, the citation-form mimicry provides a veneer of absolute authority. Because LLMs are trained to be helpful and confident, they frequently generate proofs for false assertions (like $1=2$ or $1 > e$) using sophisticated-sounding limit operations or infinite series manipulations that contain a single, deeply buried divide-by-zero or scope error [cite: 24, 25].

### 4.2 Taxonomy of Hallucinations in Mathematical Reasoning
To systematically train models to detect this mimicry, researchers must first categorize it. The **Fine-Grained Process Reward Model (FG-PRM)** framework introduces a comprehensive taxonomy of common hallucinations in LLM mathematical reasoning [cite: 3, 26]. This taxonomy is essential for generating targeted synthetic negative examples:

| Hallucination Type | Description | Example Mechanism |
| :--- | :--- | :--- |
| **Fabrication** | Creating non-existent facts, rules, or theorems out of thin air. | Citing a fabricated "Euler's Second Lemma of Invariants" to justify a step. |
| **Factual Inconsistency** | Stating a mathematical fact that contradicts established ground truths. | Stating the derivative of $\sin(x)$ is $-\cos(x)$ in a calculus proof. |
| **Context Inconsistency** | Contradicting information established earlier in the same reasoning chain. | Defining $x = 5$ in Step 1, but substituting $x = -5$ in Step 4. |
| **Instruction Inconsistency** | Failing to adhere to the constraints explicitly requested by the user prompt. | Solving for $y$ when the prompt explicitly asked to solve for $x$. |
| **Logical Inconsistency** | Reaching a conclusion that does not follow from the preceding steps. | "Since $x > 0$ and $y > 0$, therefore $x - y > 0$." |
| **Logical Error** | Misapplying a valid mathematical rule or formula. | Expanding $(a+b)^2$ as $a^2 + b^2$ without the $2ab$ term. |

*Table 1: Taxonomy of Mathematical Hallucinations adapted from the FG-PRM framework [cite: 3, 26].*

### 4.3 Automated Hallucination Injection
Manually writing proofs that feature citation-form mimicry and targeted logical errors is labor-intensive. To scale this, researchers have developed **automated hallucination injection frameworks** [cite: 27, 28].

In this process, researchers start with a dataset of mathematically correct problems and their golden Chain-of-Thought (CoT) solutions. They then utilize a powerful LLM (e.g., Llama3-70B or GPT-4) guided by specific prompts to deliberately inject one of the six hallucination types into a specific step of the golden proof [cite: 26, 27]. 

For example, the injection LLM might be prompted to take a valid proof and swap out a legitimate theorem citation for a fabricated one, adjusting the surrounding text to ensure smooth syntactic flow. The resulting hallucinatory reasoning steps serve as high-quality, fine-grained negative examples. These are used to train task-specific PRMs—each specialized in detecting a distinct type of hallucination [cite: 3, 26, 27]. By showing the model exactly what citation-form mimicry looks like across thousands of examples, the AI learns to verify the semantic payload of a citation rather than just accepting its authoritative tone.

---

## 5. Prove-by-Similarity Attacks

A **Prove-by-Similarity Attack** exploits the heuristic tendency of both humans and AI models to assume that if two mathematical structures look similar, they must share the same properties and follow the same proof logic. This is a form of spatial, geometric, or algebraic hallucination.

### 5.1 The Danger of Analogical Reasoning
Analogical reasoning is a powerful tool in mathematical discovery, but it is not a substitute for rigorous proof. In a prove-by-similarity attack, a false claim is constructed by taking a known, verified proof for Object A, and applying it verbatim to Object B, which is visually or conceptually similar but mathematically distinct.

### 5.2 Geometric Case Studies: The Semiellipsoid vs. The Hemisphere
A prime example of this vulnerability is found in multivariable calculus and geometry, specifically regarding the calculation of centroids. 

Consider the centroid of a solid hemisphere. Standard calculus textbooks easily prove that the centroid of a uniform solid hemisphere of radius $R$ lies on its axis of symmetry at a distance of $\frac{3}{8}R$ from the base [cite: 29]. 

Now, consider a semiellipsoid, defined by the region $\frac{x^2}{a^2} + \frac{y^2}{b^2} + \frac{z^2}{c^2} \leq 1$ where $z \geq 0$. A prove-by-similarity attack asserts the following false-but-plausible claim: *"Because a semiellipsoid is just a stretched hemisphere, its centroid must also be calculated using the identical integral bounds, resulting in a drastically different relative position."* Alternatively, an LLM might wrongly assert that the centroid moves non-linearly with the stretching of the axes.

In reality, a correct "proof by similarity" (via affine transformation/scaling) shows that because the hemisphere is scaled consistently along the axes, the relative fractional position of the centroid along the $z$-axis remains strictly at three-eighths from the base ($\frac{3}{8}c$), avoiding the need to re-evaluate the complex integrals entirely [cite: 29]. 

However, when generating adversarial training data, researchers can intentionally inject the *false* similarity argument. By creating a proof that perfectly mirrors the integration steps of a hemisphere but maliciously applies them to the semiellipsoid's differing geometric boundaries, the LLM generates a highly plausible, mathematically dense, but ultimately false conclusion.

### 5.3 Algebraic and Topological Similarity
This attack vector scales beyond geometry into algebra and topology. For instance, an LLM might be presented with a proof regarding infinite series in the real numbers ($\mathbb{R}$) and asked to apply the same logic to the p-adic numbers ($\mathbb{Q}_p$). Because the algebraic notation looks virtually identical, the model will often execute a prove-by-similarity hallucination, blithely using Euclidean absolute value properties in a non-Archimedean space where they strictly fail to apply. 

Injecting these cross-domain similarity failures into the training data forces the LLM to verify the fundamental axioms of the specific space it is operating in, rather than blindly carrying over heuristic templates.

---

## 6. Evaluation: What Scales?

The transition from academic theory to industrial LLM training requires methodologies that can scale to produce millions of tokens of synthetic data cheaply and efficiently. 

### 6.1 Automated Symbolic Mutation Scales Exceptionally Well
The Lean 4 "hypothesis dropping" methodology [cite: 13] scales exceptionally well. Because interactive theorem provers are grounded in strictly formalized logic, extracting theorems and algorithmically deleting premises requires no human intervention. Furthermore, the verification of the resulting LLM-generated counterexamples is entirely automated by the Lean 4 compiler. 

If the LLM provides a Lean-verifiable proof that the mutated theorem is false, the system automatically registers this as a high-quality, verified negative example. This zero-human-in-the-loop pipeline has allowed researchers to rapidly synthesize datasets containing upwards of 575,000 formal counterexample problems [cite: 13, 14].

### 6.2 AST-Based Perturbation is Highly Scalable
For natural language math word problems, Abstract Syntax Tree modification [cite: 9] scales effectively. Once the initial computational overhead of translating the MWP corpus into Python ASTs is completed, iterating through the nodes to generate permutations (e.g., swapping addition for multiplication, perturbing numerical leaves) operates at native computing speeds. The only bottleneck is the reliance on a secondary LLM to ensure the new natural language text accurately reflects the perturbed AST, though this is vastly cheaper than human annotation [cite: 10, 11].

### 6.3 LLM-Driven Synthetic Hallucination Generation
Using strong frontier models (like GPT-4 or Llama-3-70B) to inject targeted hallucinations (fabrications, context inconsistencies) into known correct proofs [cite: 26, 27] scales reasonably well. While it incurs API inference costs, the generation of datasets like "Fine-grained Hallucinations" (FG-H) allows researchers to expand a few thousand seed problems into tens of thousands of varied, balanced synthetic negative reasoning steps [cite: 3, 27].

---

## 7. Evaluation: What Fails?

While several methodologies succeed, the pursuit of high-quality negative data has also highlighted several significant failure modes.

### 7.1 Naive Rejection Sampling Fails to Provide "Hard" Negatives
Historically, the most common method for gathering negative data was rejection sampling: ask an LLM to solve a problem 100 times, keep the correct answers as positive data, and use the incorrect answers as negative data [cite: 6, 8]. 

Research overwhelmingly shows this approach is sub-optimal. Rejection sampling treats all incorrect responses as equally informative, ignoring the quality of the sample [cite: 6, 7]. Models often fail due to trivial arithmetic typos rather than deep logical flaws. Training a PRM on these trivial errors does not teach the model how to spot citation-form mimicry or subtle hypothesis softening; it merely teaches the model to become a glorified calculator [cite: 6, 7]. On complex tasks, alternative negative sample methods like simple rejection sampling drastically underperform compared to targeted, plausible negative synthesis [cite: 6].

### 7.2 LLM-as-a-Judge Struggles Without Formal Verification
Relying solely on one LLM to judge the "plausibility" or "falseness" of another LLM's proof frequently fails. LLMs suffer from sycophancy; if pushed on a correct argument, they may "discover" an error that isn't there just to agree with the user, or conversely, they may greenlight a completely fabricated proof because it looks aesthetically rigorous [cite: 2, 30].

Therefore, generating false-but-plausible claims using *only* LLM generation without a grounding mechanism (like a formal prover, Python execution, or strict rule-based AST constraints) often results in noisy data where the "ground truth" is highly debatable.

### 7.3 Uniform SFT Penalty Fails
Standard Supervised Fine-Tuning (SFT) uniformly penalizes all tokens when a model makes a mistake. This fails because, in a 500-token proof, 499 tokens might be perfectly valid, logical deductions, with only a single "critical token" causing the failure [cite: 17, 18]. Penalizing the entire output destroys the model's ability to generate diverse, structurally sound text. This is why Critical Token Fine-Tuning (CFT) has emerged to replace uniform penalty, isolating the exact token of failure via counterfactual perturbation [cite: 17, 19].

---

## 8. Integration into Advanced Training Frameworks

The ultimate goal of generating these false-but-plausible claims is to integrate them into reinforcement learning pipelines to create state-of-the-art reasoning models.

### 8.1 Plausible Negative Samples (PNS) in Preference Optimization
The **Plausible Negative Samples (PNS)** framework directly addresses the need for high-quality negatives. PNS synthesizes negative samples that exhibit expected formatting and structural coherence but yield incorrect answers. By training a dedicated model via reverse reinforcement learning, guided by a composite reward (combining format compliance, accuracy inversion, and CoT evaluation), PNS generates responses that are nearly indistinguishable from correct solutions [cite: 6, 7]. When these PNS are used in Direct Preference Optimization (DPO), models show significant improvements (e.g., an average 2.03% boost over standard RL-trained models on math benchmarks) [cite: 6, 7].

### 8.2 Reinforcement Distillation (REDI)
The **REDI** framework demonstrates that incorrect (negative) reasoning examples are highly valuable for knowledge distillation. Instead of discarding rejection-sampled errors, REDI employs a two-stage process. Stage 1 uses positive traces for SFT. Stage 2 refines the model using both the positive traces and the generated negative traces through a novel, reference-free loss objective. Using this method, relatively small models (like Qwen-REDI-1.5B) trained on just 131k positive and negative examples can match or surpass the math reasoning capabilities of models trained on 800k proprietary data points [cite: 8].

### 8.3 Fine-Grained Process Reward Models (FG-PRM)
By utilizing the automated hallucination generation (inserting fabricated citations and softened hypotheses into correct proofs), researchers have successfully trained the **FG-PRM**. Unlike an Outcome Reward Model that just grades the final answer, the FG-PRM evaluates the reasoning trajectory step-by-step [cite: 3, 5]. Because it was trained on synthetic false-but-plausible claims categorized into the six-part taxonomy, the FG-PRM can pinpoint exactly *where* and *how* an LLM's generated proof deviates from logical reality, providing a dense, stepwise credit assignment that drastically improves RL training [cite: 3, 5, 31].

---

## 9. Conclusion

The frontier of artificial intelligence in mathematics has moved beyond simply teaching models to produce the right answer; the current imperative is teaching them to recognize the myriad, sophisticated ways a logical argument can fail. 

Methods for generating false-but-plausible mathematical claims are central to this evolution. **Counterfactual perturbation** (via AST manipulation and Lean 4 symbolic mutation) and **Critical Token Fine-Tuning** provide highly scalable, automated pathways to generate robust adversarial data [cite: 9, 13, 17]. **Hypothesis softening** and **prove-by-similarity attacks** expose deep epistemological vulnerabilities, mimicking the historical pitfalls of human mathematicians [cite: 20, 29]. Meanwhile, **citation-form mimicry** testing (via hallucination injection and FG-PRM) forces models to prioritize rigorous step-by-step verification over aesthetic linguistic patterns [cite: 3, 26].

While naive approaches like standard rejection sampling fail to provide the rigorous "hard negatives" required [cite: 6, 8], the integration of synthetic, plausible falsehoods into advanced reinforcement learning pipelines (such as REDI, PNS, and FG-PRM) represents a highly effective, scalable path forward [cite: 3, 6, 8]. By mastering the architecture of false proofs, AI systems are paradoxically moving much closer to mastering incontrovertible mathematical truth.

**Sources:**
1. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHntFWd8UzO9Sjh07MO0QO--SnFs_XW5yDaxPLdHncVFHSKSLcTS7v_SvbQeHPdbojsYq5fAxN5Fqzmgjq1neEH3Wp-rDdqQhwKWSOt7BQnpagu78LCFzgBFEr28ghvl4Q=)
2. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFL4JuqJvcHrlAyTmtbXkhTw0owNTphiVYNRosXt2n6ZzV_0WBSTnMrSPd-iGumnlerE7Y5_OUY3WkWLadsM0SxsG0-aeSih0oSsowjRw_DbV6xiLj16y5Ld_lwhXi2pDYqsuwrKXj5c-ZmHfYuchMG-nc9zNQJlYuuEaXUoXOE9yJ1VHGYVsFqlnPYDK4AWOam-ZrNv2HuOGqqoAAyJRmEATqBZO517TauT5YQzZel)
3. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYjB-PqHPiI687k8a1492dDNdsfsLTy7gkb5LaZ0jSqTLJiLjDWUG52vOulW6JG8fjoGzvgnULZfzxsabjL-ZEnKnD-bAM0ORHYxOGaxPJC8KFcv5-xR-ZhUEZMXcRyBU=)
4. [rosanneliu.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgbwwV9RilPklxfBzoUu_MCHr2BVQ24fvCQWYUe4qwsykhW7dNbxUxl0J7ybMmQDexadkuC4ivMqE2rKqYn2dZv-5_3bIIblSvRdxF0Wzp95fuxsxCSDjBXus4B6o=)
5. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHVB4vmWToHabokBPNZe3PblLEhQPCNSiXoKL4jyjks3aCTJ1zeNMFYtBqW-BWI_o5IZWtpnGtxHUF8GUdHNORt2c6ZQBudokbeZUHP6BxPMNiPnmLezo_0512CPiTYDTH0A24W7j0Ry6jjglB70NO1zL8mq40BkXH_gGWeDsbdwt1xQ==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfJokch0ftW1xmkwU9ZLioq0o2rLcT7dZACpHGZbpe8li2WgXu94bdgrNG-FfCJioipHWLDb3uoLFsEKiPnKFWxUwWdAhX9rqAU6_SCGQb6FqM79wSAfoYIQ==)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFz4XzIBv9jyWABLim7Z2v8o0vpRmYGLsAdQ36sPQatC2cQcXFGJL1c9ZyPGPl3YAKdugdLGhlFOoNY1QgbuZxWIfdBQTSSUxUuk1M2igQ4uoo-d5To0y7ZxvN6RBmxE7hizQavmdQ_KN-efdPh3MUya5qdM2Z6FFP57jtnQZuGtTh_Ii3A86PK2crdUTpiR6w86OlsD8fn-IMvgVxKGxpZ3HuicayFnazNjlr3sAuJt0zbSuaMkI=)
8. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-tn4JBiau0_LYDvlZ1j2IcifhQakMTYkinFKAxKhEqY9IfiYWLJBECatbjhUAN2_vtHdfmWqRAXmz0_pdtuIqyp_B4e9jIAiU9L5Ua1nri2GjxzBbjRjaPNxdIfFK)
9. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfLeAvZepWQPf0pkqVE0qDXIIQZQd-Be4cLOyFRbO-z2ecVybzaQ4Ox5jKpVeGzsxN0THLqpeHxG8rt96iwIkXtyQ-uI_O-WYimdBLjKUOBNGPsZryGTY3faM82e1PZTIA8pYYS0p6Aqc4)
10. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEm9puSGS-eyeXt-9IVQOebNCsl0UtqusOc4tcO32apc995YPp-r0ZA916mPRlFFflpmQxpWJxF72wP5HlvTrQPndfHoY3lutwmfCIt-bnp_mXBhmHDsUDghFpjMAeNHc4vNcXA-Z6nNE6d8nvv9SM1lF85Wp7e5I_5xhsS7BsdfEC5Be0=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQET2zz-_wSow5cAtnk4b1DwMEsq1dkMKT89l7GdiE2vkoAzgr9XFu8F92_rZ534m_jtIZbMJt5WIL545TM8OJTZL9BilTsehbg-N2b2nfP9wlm-D5N58SYGWw==)
12. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvdapWVSeRXHMUOOzBBH_Eeo_p4RkTr--jKWGlFO4jnzpgf5kbuvv43u115DG1-9HcIlv4Dr_foGQt-sI-NiQ_qQ50ArmIX2EQdCyE8FhE7U-RxE4Z-XtHJAoAPgLunobppNn8V3Bq)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4W8RTRntQ0YzjA20ifruSRu6BujqF96ONyJKa_nV1SPiVZs9qsMQhGWkZFf2-rC43h34L52Ad54hOAPggM6Gq2B_bfeMfr6Ziuk140WVK7VqYat_cObS4Ow==)
14. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLRZ-YBTElEkEqPNGbx1eOhouk7DStgbCalWgIVdPdPDoQVBOCpZf8aDrkF7Q1bW3vpHNTupaAErwWwfokVkv-HITT1FcAJycgykRVdMVSKMp0sWLw6fldE238b9JTcSA=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSPdGEt0Jid19dggRwbJtKUC9xHndX11VQIQFlGcNEs7P5lwIrWem5cQfqhoVA8qa_JSglhbwhq_3kmKCb5D2GW2FGskRGZrlLKWRhv6b0rs2wllS2xg==)
16. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkSjgo4vSoXvtOFApVEhEXLwpXdxI3f12tc997H-5giiny20iySjqnnu_M7kvcRLqI7c5_Me6OWcoeBCq0U8Qpjk35fj4z6hQ2Safqs5dGzqyiLTfTZ4poanKI9Nx7wE8du3BgZhGPkqgyu-sU-761oh5E5QFXqaw=)
17. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG01YEBTaw9TRt3SC4JCV4BBelJrM5KZzIevOAWyvhP1xFUmu5xxSkqpx1pR1mfxJ9ubhbzKJiWO-md6nPSvLCOhLO1MWUOGXKMRoJNiVWkWpNxhvCt0IAKUV4NkJQj)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8baUaTdVXTMGCMTbUQrJKSkSiz0wOaKw4t3Iw5EHqJOqJlEaj8mzHR61EE4fSaGy8nK2uWc7HmYfuSKrd_Q6vK4rQkhH6F0O_pUknLKWdNX76XzrNSQ==)
19. [techrxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExlDSzK4o9qviiE_SlcivQuNQ2quIoz4Yt6pdo5Orsstb1WB9aqe1Ihf2lY3eXKJPfCpn7dOYQxdHMCikgrbOgdVCipBFJ4twnUaAU12QpVXRw-Ve0yAk07xtrMQ7CBAPwEiuJuo1R8eI4LCd7DtPiYgnv4QyfTwCEdGE=)
20. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQER1yXecBLz7JdWbP9_GzwJP-ig0KykImc0cUUMmURgQ9o-UVduTZ3udb7bb52d57qqRXRkPG-2wh3iTfek02-ivMqC88ljgEGXul3VFpEJaDBp3TmzAwiZNZQC7JGiPqXprJvuNrwjwIxSqTW7Y6Tlwd0sESzLOQrVurh1F0YTrFdhICMIcza1nulB_ooZNKyiCAyQxMan6hxatSb53yv9px4vhJA=)
21. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFg0nUzlIo_esYP2qeTbjoHj8AUZKSEUVs7NXZAQrndYQvavVuq1kOWbcoN21v8UP3epcw77Nqv6trRfO04TJZSiCornNlHoe45BYfqg5E049uU-wReBLg6Hsw56vQQAcR35gUn64dqaXUoYs85icyUy3DuDCWC7_PZ9XcB69bCr5gh-iT8P521FLyYEkIU)
22. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhlI8tECJw1VzhJbMpOj-LcUA4cPPHeRb22RbShOIhEUxcSQRlqKrUhnczgbFoD_38OewEDQ3GyzYya4121lUM3Wn5mWWKG7QiLLfk0sF7dcFwQwhIWe3IMuVBMP-CKU3ik1rV3XXxTwgs3UyvPjgcnAxh4pj4zVFsFJpsbdXyYicnxZorLLE8VTWJv5cNMo87sc2gV7U=)
23. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcydTACDDr1YXuBEw8FQlcRHpq4yaIvIMN2z6PhOFuBEeO1zld-NUwBrH4169t9dZyetVGDmAtc3m5Itr19M617AMHt-KfIsOl7hTFcEagf5LoZFrMVZLIZGNW5ZtS9KPYDM3Mbjkbn6jYQY5f6ox8EBcOKNzDNjKJRV7bSyOhVmJnvi1OtDqaKvwG4ujQuaSS)
24. [quora.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGlQrRs3LL0n0B9ZrDLD7jTGaAgC1uCQcsen5nXgrem8c5-1agOw9X1-ZfTMeyDJr-G6UknN2u2ErI0YX_9PFTjHvh8TGr-U5tFmKeBcbPMefwlMdGlyxXSv6OLB4a4c-PZIfJZkPoYWHTRDbCLK89q2joYr-rfMCxbaPQzS3mIJwd1kreO8yeVJsbbchkCAlOxsYl1oXTJ0oSrzXUtVLSEApyifl0LYelQ6D3m1yKPYekJjoYFfuoZ)
25. [ucsb.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHv4ybhk6Nfp3LiLl9fhTd9GUPPmxnbvH5PlbivExNc8b4FEwgWmHv11dKrKPkO2BObu0qHXctnauTq-KpZ41JnsZGTjvuHHyadOoRQP44XMdmqLFX9ayeHF65W-0XbL63t8LYTxufjed_QZnYZ7LG6EdYj8W_GC7T8HKIlgkOx)
26. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCSyZIcq8bfHYh14yFJqaJ_EQM7XwoPFom0OHpRjnIOKgRqCXBa4shpnJd9VZbybEW7MmGOsLj1oa3PqpKPv2FE9H__wNwzDmV2S0zc2IkgwvBX0dYira8fXsrjTlOmzl4XFnKqjxAi-_D7PrJYKN2KIHNyV0yM_C_tFdNPSmB9C1s4zEI9s8r4pdqVNtmygA_nwtb4yX9vqqQddqoogTRIOtrcdBaVkyRY_ydVvOtjjLdVChTjIdxb75olXzKjHQ=)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUDRHUGp_jFE3lPzCAXglGyDzsJwF5WGbsxCGUtz5RX5VBJ879gttcm5GHUR0k10lFr-TyLiDP43B0peoHbvD6XbMwtspy9SAuQfeONoYQKM7OzitQbVxWFA==)
28. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHN6UkkDzB-02eTLJFb6Oc7Rllvy_Gbw-tUpAbDEQBd7bcaifIPcwWLiv_dywvk04VeWu7hdkFD9CDGcCuZZfCCZ22dk3Zh0ZymbM41ajSZfWseM2ACnjrkislIz66vap7DDaF9rZa3yFan)
29. [vaia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4K9XTcV87OtBCfoKjq3olLrdk_AR2qbL3-0zrzp3r8U8ENx_dZ1S7hoJfj8bbrl7NSiGJa5hY3YMmsuhH8WoK3Lt8D8OhdiwGxQ0itXcQO_4mUfg_GLaG8bbYfvuVJ8KGw04x76jNc28HXdBhfKEWyoKezIn6rdpskObML5KkVTFq25PmIvyNJHcKidqINnMzLf9Q-aeEOyB-QgtyBnwMKNmORiLaKwynW2EQQnn51FVZLNcATUrqwNW2kTdWNv_rCO6kkDX0yvjGfCBWEpkgLLKGYAnS6kldx224dQ==)
30. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiZ97A_7OC39tYvV076J9MJnEb3VJp3rP-1HiBSQfeeuwhGJMhpIq9h-aeFlpoLQW1Iqtt5HoT6-aWGmiCFIl6CHMSOuFT95RUOtmO6S1X3W7ShY_rMNq0lLQim24zqncPn3qmGQ6npN6tvxCiw-OOEnI=)
31. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESD3ZgZuYea6IASpF12QHK83wvleAI2mwZDj1HHfdKtkUrwDuZoNChWsjX19Fmca-Ix8cXNgcITTuSIRrh2_5bellsv0bNbwVnZHncumLK8sFvG5w6dg0OdaRisN7OQKtD7kRItltWEHhsN94gJwGasw9w-wCsm1dziT_mBqyTh4hKcQbrnZHPclBc0ZVT-sYgBCNi9FG4rq6-8V2pQf8VeatLD1jkmuP1i26jIOGp6854WIJOlvJm-TWXqs-ioFg=)

