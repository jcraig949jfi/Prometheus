# FALS-03: Falsification routing in LLMs — prompting + fine-tuning

**Pythia queue id:** 30
**Tier:** T1
**Priority:** 1
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdhaW9NYW9uREY2V01fUFVQc29YcHdBTRIXYWlvTWFvbkRGNldNX1BVUHNvWHB3QU0
**Elapsed:** 244s
**Completed at:** 2026-05-19T09:20:31.131695+00:00

---

# Inducing Falsification-First Behavior in Large Language Models: A Comparative Analysis of Contrastive Prompting, Reflexion, Debate, and Reinforcement Learning from Verification Signals

**Key Points**
*   **Falsification-first behavior** aims to counteract the inherent confirmation bias of Large Language Models (LLMs), shifting them from generating plausible narratives to actively attempting to break or disprove claims.
*   **Reflexion** relies on self-critique and feedback loops. Research suggests it is highly effective in general reasoning but struggles fundamentally in mathematical tasks unless augmented with structured search.
*   **Contrastive Prompting** leverages dyadic reasoning trace analysis—comparing successful and failed attempts—to extract granular reasoning rules. It seems likely to enhance analogical and counterfactual reasoning.
*   **Debate** utilizes multi-agent adversarial setups. The evidence leans toward debate being highly effective for reading comprehension and logical puzzles, though it must mitigate models' inherent sycophancy and verbosity biases.
*   **Reinforcement Learning from Verification Signals**, specifically Process Reward Models (PRMs) and Process Advantage Verifiers (PAVs), provides the most rigorous framework for mathematical reasoning, delivering massive gains in sample efficiency and problem-solving accuracy.
*   **Math vs. General Reasoning** presents fundamentally different error landscapes. Math has a brittle, sharp error surface requiring dense step-level verification, whereas general reasoning has a smooth error surface where iterative self-reflection is sufficient for improvement.

**Understanding Falsification-First AI**
For most users, interacting with an AI feels like a collaborative brainstorming session. Language models are designed to be helpful, meaning they often adopt a "yes, and..." approach, automatically agreeing with the user's premise and building a compelling narrative around it. While this is excellent for creative writing, it is dangerous for rigorous scientific analysis or complex problem-solving. Falsification-first AI flips this dynamic. Instead of asking the AI to prove an idea is right, the AI is explicitly tasked with finding every possible way the idea could be wrong. This approach relies on the scientific method—testing a hypothesis to its breaking point to see if it survives.

**How Do We Teach AI to Prove Things Wrong?**
Researchers use several methods to induce this skeptical behavior. One is "Reflexion," where the AI checks its own work after finishing a task and tries to correct any mistakes. Another is "Contrastive Prompting," where the AI is shown the exact moment a line of reasoning shifted from a wrong path to a right path, learning to avoid the trap. A third method is "Debate," where two AI models argue opposite sides of a case in front of a third AI "judge," forcing them to poke holes in each other's logic. Finally, for math and coding, researchers use "Process Reward Models," which give the AI a grade for every single step of its work, rather than just grading the final answer. 

**The Difference Between Math and General Reasoning**
Not all problems are solved the same way. If an AI makes a tiny mistake while summarizing a book, the summary is still mostly readable and useful. This is called a "smooth" error landscape. But if an AI misses a negative sign in a 20-step algebra equation, the final answer is completely wrong. This is a "sharp" or brittle error landscape. Because of this, methods like Reflexion work wonderfully for writing and general logic, but fail spectacularly at math. To conquer math, AI needs strict, step-by-step verification methods that prevent errors from cascading.

***

## 1. Introduction: The Necessity of Falsification-First Behavior in LLMs

Large Language Models (LLMs) have demonstrated extraordinary capabilities across domains requiring structured reasoning, formal logic, and expansive knowledge synthesis [cite: 1, 2]. However, their autoregressive nature predisposes them to a dangerous failure mode: the rapid production of highly plausible, endlessly revisable, and internally consistent analyses that are optimized for publishable positive results rather than objective truth [cite: 3, 4]. Because LLMs fundamentally optimize for sequence probability, they naturally default to a "yes, and..." conversational dynamic [cite: 5]. When presented with a prompt, they tend to formalize the user's intuition, selectively marshaling references and logic to support the initial premise, effectively turning hypothesis spaces into candidate claims supported by selectively chosen narratives [cite: 3, 4].

This phenomenon creates a severe vulnerability, particularly in automated scientific data analysis and formal reasoning. Scientific knowledge is not validated by the accumulation of post hoc statistical support or fluent explanations on a single dataset; missing evidence often occupies a negative space where experiments that would have falsified the claim are simply never run [cite: 3, 4]. Consequently, there is a growing consensus that non-experimental claims produced with agentic assistance must be evaluated under a **falsification-first standard** [cite: 3, 4]. Under this paradigm, agents are explicitly engineered not to craft the most compelling narrative, but to actively search for the ways in which a claim or reasoning trajectory can fail [cite: 4, 5]. 

Inducing this adversarial, falsification-first behavior requires specialized architectural and methodological interventions. Front-loading constraints before the narrative starts building gives the model something to push against, shifting the interaction from affirmation to an actual audit [cite: 5]. This report exhaustively analyzes the latest techniques for inducing falsification-first behavior in LLMs—namely Contrastive Prompting, Reflexion, Multi-Agent Debate, and Reinforcement Learning (RL) from Verification Signals. It evaluates their comparative effectiveness across the distinct error landscapes of mathematical versus general reasoning, and synthesizes the strongest empirical evidence underpinning each approach.

## 2. Reflexion: Iterative Self-Critique and the Limits of Introspection

### 2.1 The Mechanism of Reflexion
Reflexion represents a foundational attempt to move LLMs beyond single-pass autoregressive generation by embedding them within an agentic retry loop [cite: 6]. Operating as an extension of frameworks like ReAct (Reason + Act) [cite: 2, 7], Reflexion introduces explicit iterative critique-revise cycles. In a standard Reflexion architecture, the system comprises a base foundational LLM supported by a reflection layer [cite: 8]. When the base model produces an incorrect or halted outcome, it triggers the generation of a set of reflections. These reflections form a "reflection pool," which serves as persistent memory, enabling the base LLM to amend its reasoning trajectories in subsequent iterations [cite: 7, 8]. 

This generate-verify-retry structure operates on the premise that the model can act as its own critic, providing targeted feedback to refine its internal reasoning trace before committing to a final output [cite: 1, 2]. The system continuously accumulates knowledge, theoretically allowing later problems to benefit from earlier reasoning experiences and failures [cite: 7, 9].

### 2.2 Efficacy in General Reasoning
Reflexion is highly effective in general reasoning, reading comprehension, and creative writing tasks. In general reasoning, the "error surface is smooth"—small mistakes in logic or factually inaccurate intermediate steps often still lead to outputs that are contextually usable or meaningful [cite: 1]. Because the penalty for slight deviations is low, a self-reflective loop can easily identify narrative inconsistencies, hallucinations, or stylistic errors and iteratively smooth them out [cite: 1, 8]. 

Empirical tests across diverse text-based datasets, including HotPotQA, SimpleQA, and PubmedQA, underscore the efficacy of reflection layers in augmenting success signals, Rouge-L scores, and consistency metrics [cite: 8]. In creative writing benchmarks, Reflexion achieves solid scores (e.g., 6.38/10), reflecting its utility in domains where quality is subjective and iterative refinement mirrors the human drafting process [cite: 7].

### 2.3 The Mathematical Failure Mode: Misconception Propagation
Despite its success in general reasoning, Reflexion struggles profoundly in formal mathematics. The primary distinction between informal natural language reasoning and mathematical reasoning lies in the error landscape. Math is highly sensitive to missteps; it features a jagged, brittle error landscape where a single incorrect logical jump or arithmetic error invalidates the entire subsequent trajectory [cite: 1]. 

When applied to multi-step mathematical problem-solving, Reflexion yields exceptionally poor performance, famously scoring an average of 3.93 out of 10 in rigorous cross-domain evaluations [cite: 7, 9]. The root cause of this failure is that self-reflection alone is vastly insufficient when the initial reasoning is fundamentally flawed [cite: 7, 9]. Because Reflexion typically operates on a linear trial-and-error approach, it lacks structured exploration. If the model commits to a flawed initial premise, the reflection cycle may actually reinforce rather than correct the misconceptions, creating an echo chamber of confident but incorrect logic [cite: 7, 9].

### 2.4 Hybridizing Reflexion: ReTreVal
To mitigate the limitations of linear Reflexion in sharp error landscapes, recent frameworks have hybridized reflection with structured search. The ReTreVal (Reasoning Tree with Validation) architecture combines the exploration of Tree-of-Thoughts (ToT) with node-level self-refinement and explicit LLM-based critique scoring [cite: 7, 9]. Unlike linear ReAct or standard Reflexion, ReTreVal constructs an adaptive reasoning tree that adjusts its depth based on problem complexity [cite: 7, 9]. At each node, the system generates multiple candidate thoughts, applies self-critique, and uses a dual validation mechanism to prune low-quality paths [cite: 7, 9]. 

By allowing the model to backtrack when a path proves unproductive, ReTreVal avoids committing to flawed initial reasoning [cite: 7]. This structured exploration, augmented by a persistent reflexion memory buffer for cross-problem learning, dramatically boosts mathematical performance from Reflexion's 3.93 to 6.92/10, while pushing creative writing performance to 7.88/10 [cite: 7].

## 3. Contrastive Prompting and Dyadic Trace Analysis

### 3.1 Principles of Contrastive Prompting
Contrastive prompting moves beyond basic zero-shot or few-shot Chain-of-Thought (CoT) by leveraging positive and negative examples to explicitly illuminate the causal mechanisms of reasoning [cite: 10, 11, 12]. At its most basic, contrastive prompting provides the model with a "Bad answer" and a "Good answer," forcing the LLM to contrast the two and deduce the features of the superior response [cite: 10, 12]. However, this traditional approach generally compares final outputs or prompt inputs, lacking visibility into the intermediate cognitive processes that differentiate success from failure [cite: 6, 13].

### 3.2 Dyadic Reasoning Trace Analysis (ContraPrompt)
The latest advancement in contrastive behavior induction is **ContraPrompt**, which utilizes dyadic reasoning trace analysis [cite: 6, 14]. Researchers observed that agentic retry loops generate a wealth of discarded data—specifically, the failed traces that preceded a successful retry [cite: 13]. ContraPrompt operates by comparing complete intermediate reasoning processes: it takes a pair of Chain-of-Thought traces (one failed, one successful) that share the exact same model, input, and base prompt [cite: 6, 13]. The only difference between the two traces is the reasoning strategy and the appended error feedback [cite: 6].

By analyzing this dyadic pair, the rule extractor is prompted to focus specifically on the change in reasoning approach [cite: 6]. This allows the system to extract generalized prompt rules from contrastive trace evidence without requiring model weight modification via RL [cite: 6, 13]. The result is a highly granular, process-level optimization signal.

### 3.3 Counterfactual and Analogical Reasoning
Contrastive and counterfactual tasks push the boundaries of an LLM's implicit reasoning. For example, placing an actual event and a counterfactual outcome side-by-side tasks the model with identifying the minimal causal shift required to transition between them [cite: 11]. Studies have shown that training models on executable counterfactuals (e.g., using code to map logical relationships) dramatically suppresses heuristic shortcuts and confirmation biases [cite: 11]. Remarkably, RL training on code-based counterfactual tasks transfers robustly to counterfactual problems in mathematics—a domain absent from the training distribution—providing strong evidence that contrastive approaches catalyze the emergence of generalizable, task-agnostic reasoning schemas (analogical reasoning) [cite: 11].

### 3.4 Empirical Evidence for Contrastive Methods
ContraPrompt delivers highly quantifiable performance gains. Evaluated on diverse benchmarks, ContraPrompt achieved an accuracy of 74.94%—a +7.77 percentage point absolute increase (an 11.6% relative improvement) over the unoptimized baseline (67.17%) [cite: 13, 14]. It also outperformed state-of-the-art prompt optimization methods like GEPA by +1.94 percentage points [cite: 13, 14]. The data indicates that dyadic trace analysis is exceptionally valuable in bridging the capability-application gap: the space where a model possesses the latent capability to solve a task but fails to execute it reliably on the first attempt [cite: 13].

## 4. Multi-Agent Debate: Adversarial Falsification

### 4.1 The Architecture of LLM Debate
While Reflexion relies on an LLM critiquing itself, multi-agent debate externalizes the falsification process, relying on adversarial interaction between independent instances. Under the Society of Mind theory, debate coordinates multiple LLM agents, allowing them to propose answers, critique opponents' logic, and recursively revise their stances [cite: 15, 16]. The standard debate protocol features two "expert" LLM debaters advocating for mutually exclusive answers, and a "non-expert" judge (either a human or a weaker LLM) that selects the winner based on the strength of the arguments, evidence quoted, and successful refutations [cite: 17, 18]. 

This framework acts as a scalable oversight mechanism. As LLMs surpass human expertise in esoteric domains, human evaluators lack the ground-truth knowledge to verify claims [cite: 17, 18]. Debate forces the models to act as adversarial verifiers, surfacing the negative space (the flaws in a claim) so the non-expert judge can make an informed assessment [cite: 17, 18]. 

### 4.2 Efficacy in General Reasoning and Reading Comprehension
Debate has proven extraordinarily effective in general reasoning, particularly in reading comprehension and logical consistency. Evaluated on the QuALITY reading comprehension dataset, researchers implemented a three-round debate where models produced arguments, extracted quotes, and critiqued opponents [cite: 18]. 

The empirical evidence is striking. In a non-adversarial "consultancy" baseline (where a single model argues for an answer), non-expert LLM judges achieved only 48% accuracy, and non-expert human judges achieved 60% [cite: 17, 18]. When transitioned to a debate format, the accuracy of non-expert LLM judges surged to 76%, and human judge accuracy skyrocketed to 88% [cite: 17, 18]. Furthermore, when human judges utilized ensemble voting in static debates, their accuracy reached up to 98% [cite: 18]. Debate consistently raises collective accuracy and improves the judge's confidence calibration by explicitly breaking the "compelling narrative" trap through adversarial cross-examination [cite: 17, 18].

Controlled studies using the Knight-Knave-Spy logic puzzles further validate this process. Rather than relying on simple majority voting, step-wise debate analysis showed that models actively engage in genuine reasoning—correcting initial errors, exchanging evidence-grounded arguments, and demonstrating attentive engagement that correlates directly with performance gains [cite: 15].

### 4.3 Pitfalls: Persuasion, Sycophancy, and Bias
Despite its power, debate introduces unique failure modes related to LLM psychology. Debate outcomes are heavily influenced by the intrinsic rhetorical capabilities of the agents. If one agent is strategically persuasive or confident—even if factually incorrect—it can degrade collective reasoning accuracy [cite: 16]. LLMs naturally exhibit a "verbosity bias," heavily favoring longer arguments regardless of their substantive merit [cite: 18, 19]. Furthermore, they exhibit positional bias (favoring the second candidate response or the concluding side of the debate) and sycophancy (crediting unverified quotes if delivered confidently) [cite: 18, 19].

To mitigate these issues, debate protocols must enforce strict word limits with rejection sampling to eliminate verbosity advantages, randomize argument order, and carefully verbalize prompts to suppress lexical biases [cite: 18, 19]. When these biases are controlled, LLMs like GPT-4 match or exceed the performance of state-of-the-art models fine-tuned specifically for debate evaluation, achieving F1 scores around 86.01% [cite: 19].

## 5. RL from Verification Signals: PRMs and PAVs

### 5.1 The Shift from Outcome to Process Rewards
In highly structured domains like formal mathematics and complex code generation, standard prompting, reflection, and debate often hit performance ceilings. The traditional alignment approach relies on Outcome Reward Models (ORMs), which judge only the final answer of a reasoning trace [cite: 20, 21]. However, ORMs provide a sparse signal. If a model generates a 50-step mathematical proof and receives a binary "thumbs down" at the end, it has no mechanism to determine which of the 50 steps contained the fatal flaw [cite: 20, 22]. 

To solve this, researchers developed **Process Reward Models (PRMs)**. PRMs evaluate and score every intermediate step in a multi-step reasoning trace, offering dense, fine-grained supervision [cite: 21, 22, 23]. This allows the reinforcement learning algorithm to perform highly stable credit assignment, learning exactly where the reasoning went wrong and penalizing only the specific falsifiable error [cite: 21, 24].

### 5.2 Process Advantage Verifiers (PAVs)
The evolution of PRMs has culminated in **Process Advantage Verifiers (PAVs)**. While traditional PRMs predict whether a step is correct or incorrect, PAVs are designed to measure *progress*—specifically, the change in the likelihood of producing a correct response in the future (the advantage) under a distinct "prover" policy [cite: 23, 25]. By calculating advantages rather than standard Q-values, PAVs can distinguish between good and bad steps generated by the base policy, even when the base policy cannot do so itself [cite: 23, 25].

This theoretical breakthrough means that even computationally weaker provers can be used to improve stronger base policies during RL, provided they distinguish steps effectively without being misaligned [cite: 23, 25]. 

### 5.3 Empirical Evidence in Mathematical Reasoning
The empirical dominance of PRMs and PAVs in mathematical reasoning is undisputed. The foundational paper *Let's Verify Step by Step* (Lightman et al.) demonstrated that process supervision significantly outperforms outcome supervision. Using PRMs, the model solved 78.2% of problems from a rigorous MATH benchmark subset, compared to 72.2% with ORMs, significantly lowering trace error rates from 14.0% to 3.4% [cite: 24, 26]. 

PAVs amplify these gains exponentially. Compared to traditional ORMs, PAVs are mathematically proven to be >8% more accurate [cite: 24, 25]. Crucially, they address the massive computational overhead usually associated with step-level verification. PAVs are 1.5 to 5x more compute-efficient than baseline importance-weighted search approaches [cite: 24, 25]. When deployed in online Reinforcement Learning, PAVs enable an unprecedented **6x gain in sample efficiency** [cite: 24, 25]. Furthermore, base policies trained with PAVs achieved an 8x better Pass@N performance (the probability of sampling the correct solution in N attempts), allowing them to solve hard problems that were entirely out of reach for models trained via standard Supervised Fine-Tuning (SFT) [cite: 20]. 

This paradigm is central to the latest generation of reasoning models, such as DeepSeek-R1, which utilizes Group Relative Policy Optimization (GRPO) to generate multiple responses and use their mean reward as an advantage baseline, drastically reducing memory overhead while leveraging process-like verification [cite: 22].

## 6. Comparative Effectiveness: Math vs. General Reasoning

The comparative effectiveness of these falsification-inducing techniques is fundamentally dictated by the nature of the task's error landscape. 

### 6.1 General Reasoning (Smooth Error Landscape)
*   **Characteristics**: High tolerance for ambiguity; informal inference; missing or slightly inaccurate intermediate steps do not universally corrupt the final output [cite: 1].
*   **Optimal Techniques**: Reflexion and Multi-Agent Debate.
*   **Analysis**: Because the error surface is smooth, models can easily evaluate their own narrative outputs or debate opponents without the logic collapsing. Debate thrives here because natural language allows for rhetorical persuasion, quote extraction, and semantic critique [cite: 16, 17, 18]. Reflexion succeeds because iterative drafting can easily identify stylistic or factual inconsistencies without needing a mathematically verifiable ground truth [cite: 1, 8]. Contrastive prompting (ContraPrompt) is highly effective for aligning these models to specific behavioral nuances or counterfactual logic [cite: 11, 13].

### 6.2 Mathematical Reasoning (Sharp Error Landscape)
*   **Characteristics**: Zero tolerance for ambiguity; high requirement for depth, precision, and explicit multi-step inference; purely deterministic [cite: 1].
*   **Optimal Techniques**: RL from Verification Signals (PRMs/PAVs) and Hybrid Tree-Search (ReTreVal).
*   **Analysis**: Linear techniques like Reflexion fail catastrophically (3.93/10) because a mathematical error cannot be fixed through general narrative critique; reflection often reinforces the foundational arithmetic or logical flaw [cite: 7, 9]. Debate can occasionally help in logic puzzles, but is inefficient for deep proofs. To succeed in math, the model must undergo representational phase transitions where internal circuits explicitly encode causal and compositional relations [cite: 2]. This requires the dense, step-by-step credit assignment provided by Process Reward Models and PAVs [cite: 21, 26]. When inference-time scaling is required, adaptive tree construction (ToT) combined with rigorous critique scoring ensures that failed mathematical paths are pruned immediately, preventing error cascading [cite: 7, 9].

## 7. The Strongest Empirical Evidence for Each Approach

To synthesize the state-of-the-art, the following represents the strongest documented empirical evidence for each falsification technique:

1.  **RL from Verification Signals (PRMs/PAVs)**:
    *   *Evidence*: Lightman et al. achieved a **78.2% solve rate** on the MATH benchmark using PRMs [cite: 22, 24, 26]. 
    *   *Evolution*: Process Advantage Verifiers (PAVs) generated an **8x improvement in Pass@N performance**, >8% greater accuracy than ORMs, 1.5 to 5x compute efficiency gains, and a **6x improvement in RL sample efficiency** [cite: 20, 23, 25]. This is the most robust technique for structured reasoning.
2.  **Multi-Agent Debate**:
    *   *Evidence*: On the QuALITY reading comprehension benchmark, transitioning from a single-agent consultancy to an adversarial debate raised the accuracy of non-expert LLM judges from **48% to 76%** [cite: 17, 18]. Human judge accuracy increased from **60% to 88%**, reaching **98%** with ensemble voting [cite: 18]. This represents the apex of truth-finding in ambiguous text data.
3.  **Contrastive Prompting (ContraPrompt)**:
    *   *Evidence*: Using dyadic reasoning trace analysis on diverse benchmarks, ContraPrompt achieved **74.94% accuracy**, delivering a **+11.6% relative improvement** (+7.77% absolute) over unoptimized baselines, and optimizing effectively in a single iteration without model weight modification [cite: 13, 14].
4.  **Reflexion (Hybridized as ReTreVal)**:
    *   *Evidence*: While standard Reflexion scored an abysmal **3.93/10** on math, upgrading the architecture to ReTreVal (combining Tree-of-Thoughts with critique and reflexion memory) boosted mathematical reasoning to **6.92/10** and creative writing to **7.88/10**, showcasing how structured exploration repairs Reflexion's vulnerability to sharp error landscapes [cite: 7, 9].

## 8. Conclusion
Inducing falsification-first behavior is no longer a theoretical exercise; it is an architectural necessity to prevent LLMs from polluting the information space with plausible but structurally flawed narratives. The data reveals a clear dichotomy in application. For empirical sciences, literature, and general reasoning, Multi-Agent Debate and Contrastive Prompting serve as highly effective adversarial filters that expose negative space and enforce rigorous verification. Conversely, in formal mathematics and coding, the brittle nature of the error landscape demands algorithmic rigidity. Here, RL using Process Advantage Verifiers and Process Reward Models stands alone as the definitive solution, utilizing dense, step-by-step mathematical falsification to drive unprecedented levels of reasoning accuracy. As models scale, the integration of these methodologies—combining the narrative critique of debate with the mathematical rigor of PRMs—will likely form the foundation of next-generation, universally verified Artificial General Intelligence.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8EeJa4C5yP51URGuE3LugE9G817cA-LRjlpV9k_1XDIaT08Llb1W6ZBBXtcE-5QjgmDlAWussTjb4MCBYT_VYFVYnj-hmtoWP-7c6qL1rbURqdBfjiKyn5g==)
2. [aman.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwOZS_a3OZ_DkdajjiIGKfpVA37u_6Ez0gMoehhtOikXCN-Ek3dkgwtdmuWHSRR9cZnCCstjkQG5tgI8w06FC5SXVOZnWtOLrFc9vMp_Dc53JOzP-tmsMIgPR_sbL8SYLFxMc=)
3. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfy7guV0riPz6babhFza1Dggth8AbF5Uy3TH-gv7cTsYl5NtmEy5Vmy7LyHgZbMOHLtQD4cSDUNA3K5wtxC56IyBftUVmylxFdLxskAJvriQ3XxCOn04cqAi1AqsZVpSN_lNUCHH_Lk-900yVMa3BjwjsUMfIJ6HgaKnQjFZPin5cDgnqFgL8-nSfBUDo6MhaiMRVLKSpLyROXuzbGk84y1kEY2nat-W9fOJzYj7DFXmVL90CDyaxYa3KFOeih0Q==)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2SUz4v5ChfeRTp8GJYp5L8MI1gLhAD6vYR-9c3f4IlQuDqWj7SGot9przlvTOhIhXL_xn871yPNRBF8GzbKQHGJ_KNtbYiggmcQIvlJFkfvKnSKWtviFuxAQ9ELtstoZ3ZxgoLOxgU1-ZrILC2deloHgJ8y49223G0FzU2IALyOkb0vW9jxtZQDGHGIKJtEIm9dx3STOxSZ32YLItRgw=)
5. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxK-yp_GM8vij4uV3lE7gH5U_oOTX7ud8U7_g1ebaUXMzjh_GOPgqjYX2UNAN_6lucq_zuQT0jELA1WavajPPietJX0DngliZ9v9RCyQj6kPK3fyW6QZq--Rkc9qMsHl4I6fw5f9OM782OuE2ZzrZx7ZLcqMpIz888bp7YUsL2Egcmv16CiQpKSbA7sAf6_FoLCjp0D7ACOZs=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHxW6Mmf2Wmdo4Ki5QQVRZlOAWJAlTxfJT_h90G4bOQyo3R2Sy7-SCjQ0Q5Cwm9RfOYTsQuRcJutrgv03gL-f7lubBOnEeedUt_1dcQNfAoxUU1LAhOOH8pw==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEFVsQfzbugc2S4kXFm6BBpsDpcc1Ff67GFIDi-zSZTESNpCRiyZURNGxIWnX1FxIRrqaX7LECFDZv-pKZ6G1K61ODJVmQg9ADo61bBn4-dx3WUZ132PBL8A==)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5gIUjUfW77ZSMLcODSwO9qg-UV7ZRWDwFGZhFO39V14VW3oBsK_zwuprSvnwZ23G7BF6r2f5KMYid7gRnk-z2x7W0qhWFZAiZC6LxQBlyjXTMIWx1XQsqyWKzo9SrEZQSFDagyFiOci0CQtx8fsEeFEn3r8w_4mb63gM7KQmiq-JK9OYMmGcL-y1wacaOJLYZP6Gk6jmx12vPD8Zu43PkATypsqLzVEZNUFEb5i68bapOM_HBC9A=)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE--JKVGONa0fsupG6pNLX6bR9kqVNjv2okCBAjsiJqCgCOGvKJkOMqRoUnZPd9JnaF1vvjf1jzoHaorfbtux_HJwbFMnQBE7XBWMtk9PECZvWkTwbdQA==)
10. [towardsai.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHj2vXA-7Dn_oXBGIq9XXAD8xmacjHGhomMWSk_i65VmLOtAmqQZHwaXY2FPLqEVWDJWg1wpqMIdHzjAMiSOt7_9CyEAduEyqW5IEYFelREx40Sk4zYPFo-ki6pfk_RmUZUfidkxlOMRh5a_nfjR-G3FCX1GPSOhe19jlKdsa3xxuA=)
11. [note.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuxNiFYf1rTVSIFEmhKMAvzy6p59ndJp6ipo6cORtZpQmvbsnn1uKC2HwQeugWE0XZJJ1ewXtenFslh9nnbxb3K6O7eFqH-Nr4XNAKYOL2cqkNgEPP9z4Gk6T4nRwpRszVKNo=)
12. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzAaLPjzJwi6-xOmaK0D2fViTsQ-ywFizQui77VI3tDKiw2SFLln1LOtbHn_4Mc3MMYKVtxz_SYeXr48lREexpOBer8Q9DJdnF0rM-Lq7T7XXXwk0NJKeKeKYhQo7J1JIAl43H_9b_BcgENIiFISvR5d3jtd50ST-6QGKn9LbcEWaK1D9hppwqHYuq-QwipVx0Efc=)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkQicjE9sOYgtK8MyoOQ3jUxh5T2wo3McovqYl6gXWQ245eG2JVCYIMaPWkhhtArVVL_pvt30QwnWyZpZ8dVtM8DTyqZzhR8xd28XiF9OcKB7FaBf1Pw==)
14. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqI-YZZG3nhhJXOh1RATXnN6W02FxQlUkJr_TJLsranJHOUA7lG2J28vYs6PzzykdrtHikwqgWiGACeaqswySxQZcl97YjPelNkA6JhjHoXEzC94hSdE0KDUM-_qcwBCn0EGbcmRnhDbhP7qdND_UNqULOmdVmJQSNixgv6gvjQIxjS5pTQDPp-wTmypwxizjTulc0uQJAzxqgg7qYRuaB_x_3M2nu3VXpfWnA)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHLKRYGE9sZrayQ-bsJ3KOEB_fqubl5RJhrfC8R30lN6ZqU_DeKo15nuQfeNbH26d5xBKW-l-3LvdzL-wc85vtGOT-6rltKeXYqGslhgIM6_zHCh4cWtkixQ==)
16. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFS4kKJnro-6giirK-8MV4dPuohotTJmCnDphGKGceSX3yOGT37Sql-ET2EeZlO8rUjPHz62NwXCsDN4UQhuJHntymjvIHhkIxViw4RSgoYuUuAt3VkLF1Skgh7khm6TdRrwr-x_4s7Ig==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyXdPdSnB1CNv7RV88tdhKSmtYnrpJ9TVGoFlpJBG896_6_YXxiyRR0ZQ3Y00X373F_w21IkOLM7DdshXUBeq1uLRfyYmZgFJ16LM05OQPhvkkLRBzyQgQbw==)
18. [lesswrong.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHs5r1M28zu-OUOBbGHjDrpugM8206jHBdrnuI3h98jMflxSc2Nj6pxpLlcdKqxTYuNGPnAU3pYwA7ka4iEmIYeGIoCe37RG2dV4SVCchmz9Kjb4BXNHmcSSvJn71N_7zfuXK2KROz7I182JkA9ROctl2eRRG4zK9GzlFcs22oRFd1Ys06EslRGiOwsfYtIVJJVhghZ4D5gHIAYDoelpR-sQ==)
19. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEe6u2l1mAPCrYoH5fKtDqA45UC77R4ArEmsuA12BMluYtMDpImoOi97QxfwyBqxQ6cJVEj3fk5loWo2-q_5cVDODK-lpbLN1jAtYuUSzP432G-0d7cIOSg2gMvE2Fad0QRUvKM)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-gGT2mtOnhEJU6e5adbAIgmUm3u41yaieA91-KUzuxSOnuR-qnWCSi6hwqSAHwC3MVWBuaVP_BJxu7xMbBlzuWrup2pTIqBUNZ3P1i4ZXzkXRlvgPwg==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFn6TK3MG1PKMn6vv7SH6AkLzlfaJfHUNFc9brDdOQO7nJPX9NX3s-m3ZEpqehRYj0FLmwVvy7jUaT2SfwUGevyZJF8a-elfKVtpgjCNW-3qowRUyrWRLxMHQ==)
22. [letsdatascience.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhhjGG1fFmclZW5vxDvJG7eGp6iFk6uAyv5UP5bG5ZDO5s65AdafiqVjZiBf6VKLx3amIbnoAKt5TEAC9pFM3TiySwq1kiHfBfDLqiZyc-hrywKi2uPTg8NsFB-_K-FUKwuGiE8oaspdzoyacqdpTS96uiV1YtVh0gT2HkHltNTfrJf4DlMUoJWTq8Dw==)
23. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGY2JkgW_SMpWhv2A4IMxU59xinoiLCutJ07fbhejNW5QJ1mKKFl1MK_JU1Vk90Yo82KeNUu_w0xw7ofgenrnxuk-N041Uv60aRu1BE6mzGkbNp03qbW3RBccwLFsvf7tPp5h9q-YPq2GC5wuMjwtW7ZTpMHyvOCmABjFPUEQsbNECntuxvz37jgGgsxgeMwfWjC7t5OqNHGt24lHGOkvj8_DrS)
24. [mcginniscommawill.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwvZLUYMRsvCZ5OTlFAg9yJX3JJbEmzBtQSGe8zXJT_InaKn-g9RJRruE8J-AQsAIrWPgtdcQAC_gX57SPpB3OYAEvUq6cAsW-u4IvPgJQBolp0VcPMie_O32XIvj9QUwZ4CnQ4O4xpIVj_dvqMVZQDzca_yXBJb8fnQRa_iNTT2xjkqz2eA==)
25. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAjPdscmy50GtT3dfRiAkw9XbIaQ7gTucC68BlWRszPJ-y6_cJAWbd_g7tkfe0Nh_f8JiTjL9AHlmhWaIEmHnbzjJ_GPeCmqdI1U25QBp9IPHF0qymYBJDABsdrZ2Xeh0=)
26. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtLvw3_5k6pHwQTfNyBc1mcR3O33g43mx0__FXDAcLod6ZVpmUFfmVvjWwVptK0ttzpqXZVWEOJTnsA0Klp7aqTtyqdSCkV_aWg17Ixn2AA8X0JoQ55tEzrMNgl_zuyla6q1KpyXReAFBQ5eWnHV9wTtx-LYzD556dzKh00Kc=)

