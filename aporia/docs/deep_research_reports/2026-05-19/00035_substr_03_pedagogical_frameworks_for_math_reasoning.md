# SUBSTR-03: Pedagogical frameworks for math reasoning

**Pythia queue id:** 35
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChZCRGdNYXJHekNzWFNqTWNQcmZqd01BEhZCRGdNYXJHekNzWFNqTWNQcmZqd01B
**Elapsed:** 307s
**Completed at:** 2026-05-19T10:19:36.115972+00:00

---

# The Polya-Lakatos-Tao Pedagogical Lineage as a Reasoning-Strategy Substrate: Modern Computational Instantiations and Substrate-Style Verification

**Key Points**
*   **The Pedagogical Lineage**: The mathematical reasoning paradigms established by George Pólya (heuristic decomposition), Imre Lakatos (dialectical refutation), and Terence Tao (tactical exploitation and formal synthesis) provide a foundational substrate for modern artificial intelligence reasoning.
*   **Modern LLM Heuristics**: Recent prompting architectures—such as Auto-CoT, Least-to-Most, Plan-and-Solve, and SELF-DISCOVER—function as automated instantiations of Pólya’s four-stage problem-solving methodology, transitioning models from passive generators to strategic planners. 
*   **Substrate-Style Verification**: The integration of Large Language Models (LLMs) with formal verification substrates like Lean (e.g., DeepMind's AlphaProof, Math Inc.'s Gauss AI) operationalizes the Lakatosian dialectic, where formal compilers provide the "counterexamples" that iteratively refine neuro-symbolic proofs.
*   **Human-Centric AI Proofs**: Systems like *HumanProof* demonstrate that mapping automated proofs back onto human pedagogical structures (via hierarchical task trees) is essential for mathematical comprehensibility, directly mirroring Tao’s translation between intuitive and formal mathematics.

**Introduction**
The challenge of teaching artificial intelligence to reason mathematically has fundamentally mirrored the historical challenge of teaching human students. For decades, mathematical pedagogy was dominated by rigid memorization, but a paradigm shift occurred through the works of George Pólya, Imre Lakatos, and Terence Tao. They conceptualized mathematics not as a static body of facts, but as a dynamic, heuristic, and dialectical process. Pólya emphasized structured problem decomposition; Lakatos highlighted the role of error, counterexamples, and iterative refinement; and Tao synthesized these into tactical play and collaborative formalization. Today, this pedagogical lineage serves as the theoretical substrate for state-of-the-art computational reasoning. By embedding these human-like cognitive strategies into LLMs—through advanced prompting heuristics and integration with rigorous formal theorem provers—researchers are successfully bridging the gap between informal mathematical intuition and machine-verified logical certainty.

***

## 1. The Polya-Lakatos-Tao Lineage: A Theoretical Substrate

The foundation of modern computational reasoning architectures can be traced back to the philosophical and pedagogical models of mathematical discovery. The lineage of Pólya, Lakatos, and Tao provides a structural ontology for how complex reasoning can be decomposed, tested, and formalized.

### 1.1 George Pólya: Heuristic Decomposition and Plausible Reasoning
George Pólya’s seminal 1945 text, *How to Solve It*, introduced a systematic approach to mathematical problem-solving that has become the canonical blueprint for algorithmic reasoning [cite: 1, 2]. Pólya argued that mathematical discovery relies on "plausible reasoning"—heuristics that do not guarantee a solution but structurally narrow the search space [cite: 3, 4]. His methodology is explicitly formulated into four sequential stages:
1.  **Understand the Problem**: Identifying the unknown, the data, and the condition.
2.  **Devise a Plan**: Finding the connection between the data and the unknown, often by recalling related problems, generalizing, or specializing.
3.  **Execute the Plan**: Carrying out the steps and checking each one for validity.
4.  **Review and Extend**: Examining the obtained solution, checking the result, and exploring its broader applicability.

In modern AI, these steps serve as the theoretical baseline for evaluating LLM reasoning failures [cite: 2]. When language models fail at mathematical reasoning, it is frequently due to an inability to devise an appropriate plan (Stage 2) or a failure in the rigorous execution of sub-steps (Stage 3) [cite: 2]. 

### 1.2 Imre Lakatos: Dialectical Refutation and Concept Formation
While Pólya focused on the heuristics of the individual solver, Imre Lakatos, in his 1976 work *Proofs and Refutations*, reframed mathematical reasoning as a social, dialectical process driven by error and counterexample [cite: 5, 6]. Lakatos modeled mathematical discovery as a dialogue where an initial, often flawed conjecture is proposed, followed by a proof attempt, which is subsequently dismantled by "counterexamples" [cite: 6, 7]. 

Lakatos introduced highly specific mechanisms of reasoning adjustment, including:
*   **Monster-barring**: Refining a definition to exclude pathological counterexamples [cite: 7, 8].
*   **Exception-barring**: Modifying the conjecture's domain of applicability to protect the core theorem [cite: 7, 8].
*   **The Method of Proofs and Refutations**: Using counterexamples to locate the specific hidden assumptions in a proof step, thereby simultaneously improving the proof and the theorem [cite: 7].

Lakatos argued that proofs are not merely tools for establishing unquestionable truth, but rather instruments for deeper conceptual analysis [cite: 4, 5]. This "generate-and-critique" loop forms the pedagogical basis for modern agentic self-reflection and verification pipelines.

### 1.3 Terence Tao: Tactical Exploitation and Formal Translation
Terence Tao’s contributions to mathematical pedagogy and practice represent the modern synthesis of Pólya’s heuristic planning and Lakatos’s rigorous refinement, extending them into the era of mass collaboration and formal verification. In his book *Solving Mathematical Problems*, Tao expands upon Pólya’s framework by emphasizing specific tactical approaches: simplifying, exploiting data, and reaching tactical goals before attempting a global solution [cite: 3, 9]. Furthermore, Tao frames abstract concepts, such as epsilon-delta $\forall \epsilon > 0, \exists \delta > 0$ proofs, in game-theoretic terms—a mental model of adversarial reasoning that maps directly to min-max algorithms and reinforcement learning [cite: 10].

Crucially, Tao has been at the forefront of the modern shift toward computer-verified mathematics (e.g., Lean) and collaborative problem-solving (e.g., the Polymath projects) [cite: 11, 12]. His formalization of the Polynomial Freiman-Ruzsa (PFR) conjecture [cite: 13] and the Prime Number Theorem [cite: 14] in Lean exemplifies the transition from informal plausible reasoning to machine-checked formal substrates, laying the groundwork for neuro-symbolic AI systems.

***

## 2. Modern (2020–2026) Computational Instantiations

Between 2020 and 2026, the theoretical paradigms of Pólya, Lakatos, and Tao were explicitly instantiated in various computational architectures, ranging from specialized agentic workflows to massive reinforcement learning models.

### 2.1 The Lakatosian Instantiations: HRL and MathChat
Early attempts to computationalize Lakatosian reasoning resulted in systems like **HRL** (an extension of Colton's HR system), developed by Alison Pease [cite: 7, 8]. HRL simulates a Lakatosian classroom environment using an agent architecture. Individual agents possess different databases of examples and evaluation heuristics [cite: 11]. When an agent proposes a conjecture, a central choreography agent uses Lakatosian methods (monster-barring, exception-barring) to analyze counterexamples and refine faulty conjectures [cite: 7, 11]. This system demonstrated that definition refinement—shifting from extensional definitions (a list of known primes) to intensional definitions (logical formulas)—could be automated [cite: 7].

More recently, LLM-based instantiations like **MathChat** leverage conversational frameworks to mirror the dialogue of discovery [cite: 15]. Using a user proxy agent to communicate with an LLM, MathChat executes Python code incrementally, reflecting the step-by-step progress of the model and allowing the LLM to adjust its reasoning based on the computational "feedback" [cite: 15].

### 2.2 The AI Co-Mathematician Framework
Developed by Google DeepMind (circa 2024-2026), the **AI co-mathematician** explicitly models the asynchronous, exploratory nature of human mathematical workflows [cite: 16, 17]. Powered by Gemini language models, this system is not a simple chatbot but a stateful workspace where a central coordinator agent delegates subtasks across parallel workstreams [cite: 16]. It assists human mathematicians (such as Marc Lackenby, who used it to solve an open question from the Kourovka Notebook) by tracking failed hypotheses, uncovering literature, and managing uncertainty [cite: 16, 17]. By surfacing the AI's underlying process via inline text and margin notes, it reconstructs the mental models required for human mathematical collaboration [cite: 17].

### 2.3 Formal Verification Instantiations: AlphaProof, DeepSeek-Prover, and Gauss AI
The most profound instantiations are those that marry LLM generation with Interactive Theorem Provers (ITPs) like Lean:
*   **AlphaProof (DeepMind)**: Achieving silver-medal equivalent performance at the 2024 International Mathematical Olympiad (IMO), AlphaProof represents a monumental leap in automated reasoning [cite: 14, 18]. It couples a fine-tuned Gemini language model—acting as an auto-formalizer to translate natural language problems into Lean 4—with the AlphaZero reinforcement learning (RL) algorithm [cite: 14, 19]. It uses "test-time RL" to generate and learn from millions of problem variants during inference [cite: 14, 18].
*   **Gauss AI (Math Inc.)**: Designed specifically to assist expert mathematicians, Gauss AI was instrumental in completing the formalization of the strong Prime Number Theorem in Lean in January 2024—a project led by Terence Tao and Alex Kontorovich that had stalled under human-only effort [cite: 14].
*   **DeepSeek-Prover-V2**: Released in 2025, this open-source model leverages Group Relative Policy Optimization (GRPO) reinforcement learning with Lean compiler feedback to advance formal subgoal decomposition [cite: 14, 16].

### 2.4 HumanProof: Bridging the Cognitive Gap
A persistent issue with theorem provers is their lack of human comprehensibility. Ed Ayers' **HumanProof**, an extension for Lean 3, aims to generate formalized proofs that mimic human pedagogical reasoning [cite: 20, 21]. Using a subtasks automation planning subsystem, HumanProof breaks equality problems into a hierarchy of tasks rather than resorting to brute-force normalizations [cite: 20]. Its *ProofWidgets* feature provides a visual, hierarchical representation of the goal state [cite: 20]. In user studies, mathematicians strongly preferred the HumanProof format because it provided "intuition and signposting"—critical pedagogical elements advocated by Tao and Pólya [cite: 21].

***

## 3. Comparing Pólya Patterns to Recent LLM Heuristic Libraries

The explosion of Large Language Model capabilities has driven the rapid development of prompt engineering strategies. These strategies, often termed "heuristic libraries," fundamentally seek to operationalize Pólya’s four stages of problem-solving. However, they vary significantly in their architecture, efficiency, and alignment with task-intrinsic structures.

### 3.1 Chain-of-Thought (CoT) and Auto-CoT
**Chain-of-Thought (CoT)** prompting revolutionized LLM reasoning by forcing the model to articulate intermediate steps before producing a final answer, effectively mapping to Pólya's Stage 3 (Execute the Plan) [cite: 15, 22]. **Auto-CoT** automates the construction of these prompts through clustering [cite: 22]. However, CoT suffers from uniform application: applying the same "think step by step" heuristic to simple tasks often induces "overthinking," leading to excessively long traces that accumulate errors and degrade accuracy [cite: 22, 23]. Research indicates a clear anti-correlation between reasoning length and accuracy on certain tasks, suggesting that rigid CoT lacks the pedagogical flexibility of human reasoning [cite: 23]. 

### 3.2 Least-to-Most and Decomposed Prompting
**Least-to-Most Prompting** and **Decomposed Prompting** act as direct computational analogs to Pólya’s Stage 2 (Devise a Plan: Decomposition) [cite: 2, 23]. They prompt the LLM to break down a complex problem into a sequence of simpler, sequential subproblems [cite: 2, 23]. This approach explicitly mitigates the complexity limits of transformers by ensuring that the resolution of one subproblem feeds directly into the context window of the next [cite: 2]. Least-to-Most has proven substantially more effective than standard CoT on tasks involving symbolic manipulation and compositional generalization because it inherently structures the reasoning space [cite: 24].

### 3.3 Plan-and-Solve Prompting
**Plan-and-Solve (PS)** prompting bridges Stage 2 and Stage 3 of Pólya's methodology. Rather than utilizing a generic "think step by step" command, PS explicitly instructs the LLM to first generate an actionable plan (monitor-generate paradigm) and then execute it sequentially [cite: 23, 24]. While PS achieved significant benchmarks (e.g., 76.7% accuracy on certain arithmetic tasks), it remains an isolated paradigm [cite: 23]. It excels at strategic planning but lacks an intrinsic mechanism to verify whether the selected strategy succeeds, meaning strategies can fail without feedback [cite: 23].

### 3.4 SELF-DISCOVER: Meta-Reasoning and Strategy Selection
The most advanced 2024 paradigm is **SELF-DISCOVER**, a framework developed by Google DeepMind and USC [cite: 25]. SELF-DISCOVER recognizes that the application of a single, uniform prior (like CoT or Least-to-Most) is suboptimal [cite: 24]. Instead, it uses meta-reasoning to allow the LLM to dynamically self-compose a task-intrinsic reasoning structure [cite: 24, 26]. 

The architecture strictly mirrors high-level human metacognition via three phases:
1.  **SELECT**: The model chooses relevant reasoning modules (e.g., "use critical thinking," "break down into sub-problems") from a predefined set based on the task’s requirements [cite: 27, 28].
2.  **ADAPT**: The selected generic modules are rephrased to fit the specific context of the task (e.g., adapting "break into sub-problems" into "calculate each arithmetic operation in order") [cite: 27, 28].
3.  **IMPLEMENT**: The adapted heuristics are formatted into an actionable, key-value JSON structure [cite: 26, 27]. 

In the second stage of SELF-DISCOVER, the LLM simply follows this generated JSON structure to solve instances of the problem [cite: 25, 27]. This decoupling of *strategy discovery* (Pólya Stage 2) from *task execution* (Pólya Stage 3) yields up to 32% performance improvements over CoT and Plan-and-Solve, while requiring 10 to 40 times less inference compute than ensemble methods like self-consistency [cite: 23, 24, 25].

### Table 1: LLM Heuristics mapped to the Pólya Problem-Solving Framework

| LLM Heuristic Strategy | Primary Mechanism | Alignment with Pólya's Framework | Limitations |
| :--- | :--- | :--- | :--- |
| **Zero-Shot / Auto-CoT** | Uniform step-by-step unrolling of thought traces. | **Stage 3** (Execute): Emphasizes calculation but lacks overarching planning. | Prone to overthinking; uniform application fails on diverse topologies [cite: 22, 23]. |
| **Least-to-Most** | Sequential reduction of complex prompts into easier sub-queries. | **Stage 2** (Devise Plan): Specialization and decomposition. | Assumes subproblems are linearly independent [cite: 2]. |
| **Plan-and-Solve** | Generates a strategic outline prior to execution. | **Stages 2 & 3**: Combines explicit planning with step-by-step execution. | Operates blindly; lacks feedback to verify if the plan is succeeding [cite: 23]. |
| **SELF-DISCOVER** | Meta-prompts (Select, Adapt, Implement) to self-compose task-specific JSON reasoning structures. | **Stages 1 & 2** (Understand & Plan): Identifies task-intrinsic structures before execution. | High initial meta-reasoning overhead; relies on quality of foundational heuristic seeds [cite: 25, 26]. |

***

## 4. Transferring Patterns to Substrate-Style Verification

While LLM heuristic libraries vastly improve the generation of plausible mathematical text, they inherently lack mathematical rigor. The integration of LLMs with formal verification environments—often called *Interactive Theorem Provers (ITPs)* or *Substrates* like Lean, Coq, or Isabelle—represents the frontier of modern AI mathematics [cite: 13, 14]. Transferring the pedagogical patterns of Pólya, Lakatos, and Tao into these rigorous environments requires novel architectural paradigms.

### 4.1 Pólya Patterns in Substrate Tactics: HumanProof and Hierarchical Trees
In formal substrates like Lean, a proof is essentially a program constructed using "tactics"—commands that manipulate the goal state [cite: 20]. However, raw Lean code often resembles assembly language, devoid of human semantic meaning [cite: 19, 20]. For example, DeepMind’s AlphaProof often produces valid but highly unorthodox ("alien") proofs that bewilder human mathematicians [cite: 19].

To align formal substrates with Pólya’s structured pedagogy, systems like **HumanProof** introduce *subtasks automation planning* [cite: 20]. Rather than relying on brute-force algebraic normalization, HumanProof transfers Pólya’s "decomposition" heuristic into the formal environment by generating a visual, hierarchical stack of sub-goals [cite: 20, 21]. By forcing the theorem prover to sequentially rewrite terms via this hierarchy, the output mirrors how a human mathematician would devise and execute a plan, establishing the critical "signposting and intuition" required for pedagogical comprehension [cite: 21]. 

### 4.2 Lakatosian Patterns in Compiler Feedback Loops
Lakatos’s *Proofs and Refutations* is defined by the dialectic between conjecture and counterexample [cite: 6]. In modern LLM-ITP systems, the Lean compiler acts as the ultimate, unforgiving Lakatosian interlocutor. 

Current "Generate-Verify" LLM approaches (like Self-Refine) often fail because they refine outputs blindly without grounded task assessment [cite: 23]. However, when an LLM is connected to Lean, the compiler provides immediate, deterministic feedback on failed tactics or type errors [cite: 14, 18]. 
*   **The Method of Proofs and Refutations**: When an LLM generates a proof step that fails verification, systems like **DeepSeek-Prover-V2** and **AlphaProof** use this error as a localized refutation [cite: 14]. The model is forced to analyze the specific assumption that caused the compilation failure, mirroring Lakatos’s method of using counterexamples to pinpoint hidden assumptions [cite: 7, 14].
*   **Test-Time Reinforcement Learning**: AlphaProof utilizes test-time RL to explore millions of variants of a problem [cite: 18]. When a generated formal proof hits a dead end (a refutation), the AlphaZero algorithm updates the value network, fundamentally learning from the refutation to guide future heuristic searches toward successful paths [cite: 19]. 

### 4.3 Tao Patterns: The Bridge from Informal to Formal
Terence Tao’s modern pedagogical philosophy emphasizes that the gap between informal intuition ("what you think") and formal rigor ("what you write") must be actively managed [cite: 4, 10]. This is precisely the role of the **auto-formalization** agent in systems like AlphaProof and Gauss AI.

In AlphaProof, a fine-tuned Gemini model acts as a translator, mapping the informal, natural language statement of an IMO problem into the strict formal syntax of Lean 4 [cite: 14, 18]. This process is highly non-trivial; for example, during the IMO 2024, AlphaProof struggled with geometry due to gaps in Lean’s Mathlib4, necessitating the use of the specialized AlphaGeometry 2 system [cite: 18]. 

By successfully auto-formalizing problems, these systems instantiate Tao’s goal of leveraging computational power to handle the "tedious" rigor (the substrate), freeing the human (or the high-level LLM planner) to focus on the high-level, tactical insight [cite: 12]. As Tao himself noted, the capacity of Lean to scale automated reasoning has fundamentally altered the landscape of problem-solving, making it an indispensable tool for ensuring soundness in verified AI systems [cite: 12].

### Table 2: Pedagogical Lineage Transferred to Substrate Verification

| Pedagogical Origin | Theoretical Concept | Computational Instantiation | Substrate Implementation Mechanism |
| :--- | :--- | :--- | :--- |
| **George Pólya** | Plausible Reasoning & Hierarchical Planning | **HumanProof** (Ayers, 2021) | Subtask automation planning; visual hierarchical task trees driving Lean tactics [cite: 20]. |
| **Imre Lakatos** | Proofs & Refutations (Dialectic Error Correction) | **DeepSeek-Prover-V2** / **HRL System** | GRPO with Lean compiler feedback acting as the deterministic Lakatosian refutation [cite: 7, 14]. |
| **Terence Tao** | Auto-Formalization & Collaborative Verification | **AlphaProof** / **Gauss AI** | Gemini-driven translation of natural language geometry/algebra to formal Lean expressions [cite: 14, 18]. |

***

## 5. Synthesis and Future Directions

The synthesis of the Polya-Lakatos-Tao lineage into computational reasoning strategies demonstrates a clear evolutionary path for Artificial Intelligence. Early LLMs acted as zero-shot pattern matchers, lacking structural reasoning. The introduction of heuristic libraries (CoT, Least-to-Most, Plan-and-Solve) marked a transition toward **Pólya-style cognitive architectures**, enabling models to independently outline and navigate search spaces [cite: 2]. The subsequent development of frameworks like SELF-DISCOVER (Select, Adapt, Implement) proved that models could perform meta-reasoning, stepping outside the problem to select the optimal heuristic [cite: 25, 26].

However, the inherent hallucination risks of purely linguistic models have mandated a turn toward **Lakatosian dialectics** through substrate-style verification [cite: 13, 18]. The 2024–2026 breakthroughs achieved by DeepMind (AlphaProof) and Math Inc. (Gauss AI) prove that integrating heuristic generators with interactive theorem provers (Lean 4) yields superhuman performance on benchmark logic tasks [cite: 14, 18]. 

The critical frontier remaining is **human-AI comprehensibility**, a concern heavily championed by Tao. While reinforcement learning agents like AlphaProof can generate logically sound Lean code, the resulting proofs frequently feature "alien" paths unreadable to mathematicians [cite: 19]. Ensuring that AI systems utilize frameworks like HumanProof to output structurally intuitive, signposted logic will be essential for the next generation of "AI Co-mathematicians" [cite: 16, 21]. As AI moves from a tool of verification to a true collaborative partner in mathematical discovery, maintaining the pedagogical roots of Pólya’s clarity, Lakatos’s rigorous debate, and Tao’s tactical elegance will be paramount.

**Sources:**
1. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEz612dz_e957t4VzB1-DzfdnrhE4VR5OZbrCaxjnrU8UJ4KteGI__5tjjY_j7HdNPz7gfUoFqivTmh6kS1rYIyJ1msA0wIy-GUymGBy_QxvnRlkHgS_Op4kXvp5gWGN-1_cWTxcPSmojlg9eyVzXSqa1AfXqTO4HZMmagMv8lY3ZJcNOhxP5ZXP5k-qbTctSw4Tccs1w==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGu-wfngYdARdFDbIhwD4ipHNT6pQNXcxrc4Iq2le9Xw5SNSwejslUFDQEkAXcbbaFbrMIQS-n7CFfAdr2odSjhroIbzMc0jnLslL75EUbCce98Lcog-2fQ)
3. [birmingham.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_QZpZKtIlV8G83ootDyBXEdLzLQVx0w8pGI3HgobFvqcHvc8eI9qnL6eFzVh9inDEzYp4JQ9dweEACyfr-jU1VR8M6TlfIVl4mspql-v-9VIP8Ous5V4ZUQNXuWtMrdruPNvZq3e_QSOikS5CjigLYU-H2N0bMoKXO_a0rdbxvmRfa6OwBz-bHGl95EIUgwjzT5gALWcpUyrQ0EE9KkiuW0TrV8qXwkK-MJI=)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHq20s5JsLnMmbbsTQa_EgSkp3IJnjoS7tIBCUdxNu7HaF0W5MnUX9K9NnmcO1VCMlXucNKWNZ8JrGt9sLdhKYZdjA4TYENe9SwNYt-Ci7h4KHR1zKrj5Tt)
5. [patrickstevens.co.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqMVY7_F_PBxjyCeLNeeux8MEF_NIDl7umBEJewmnLlXXeN4LeKPwNmuigUM3Gh_jSS1a1yAWlFvmZrjJxcGgm4jLj1Tp4qWC47PzIQRtObWJgZRMTj-ZlyfauqcKLh5Jw9bQ=)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH10dBTt5I7tQjaGKJ5BZsbYMMoGHpqbY-4T_FOskcfaJOnsZZOPyzm1yifk1AZTNHM9uF_bv2JOLGxwgiF1fKPvs7dD14iOrqmnSXusjPVCfmyrWJdbQLC3dm-UWBx4yV1oEf2mxIuAVDUUQbWTLzFmeR8f3MYvmddJniyIVqDxE-K51Vo-c9Vuth790zyFo-gzrsxA7Idytxer_8=)
7. [ed.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHw2vjUHDJIdyINMWw34rQNGbnsd586abh1Df49Ygo43DV0j7A5rDn4mlSA31rJ67C369Eik9yMNI8yFIvq9jJ2xwTZ6MyXIxk-Op-LBN40N76vGRYkCQJl6JsT6zDWNHQu6SPCqBKb3XNOaICGlByJeys=)
8. [dundee.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIo_VeTcwPvzsGA6Rx221naOcmxg7uALSJQNgzbpsHsUhQU4j756Z6FGEQwCy307uOtn5ERRQX56kxDygPgXH-B3wHxYrgTC1eMpvKI_2nIAUaNxQgXtvY7bLuhg1bDhIGFfP_N3fYcZfZpqD--LiPDenVxw3nyP_bJvdvvtpfAwSj_TAStpSgIJB2kckHlugI)
9. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxV1xygiiLrewvL0bAujMjL5L67rKIqilFt2jFx1zLf1HGWlxInRe6p-8T36G6UsrcguOISfslpsvO3VsGwEBb3YGZTP29xz3TJb6-6giSSiU5jgea3iqxpaKQLfHG19BTNV1soQDUJ1nfuaIO40QqPkDL)
10. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLLN9mspUWL0MywtOTuUeZqza0bJFZGSrogxzKTnJzODFqIBiIv9yvgEz4OSntfW4hu-fK7e2xJzsLKEGhWjciDCtR4IDBd9C10aP6QX-HlwlAwlRmOnc3EXTnfV6X-lLYa_2C81lchQLXksy8gxYL9nIHkSEQUEVa7aN0Lte6WRcLDtfkZLlJaOonmF8HZ5kBG6Zsun4=)
11. [ceur-ws.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHguvoIRPVf44hZ_mBNNF-LfDSCWvLmcIK_upL8Qh2oJpIxLOvnJuMAhENlEvl3SlDKvcy3HGyvlFETVmgYTi3QbEfDPpAae1crkvajb5d6GxJDDy3vaca4KXNuSg==)
12. [lean-lang.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9sMxhEeyhyEBA_vrpTdPoMQpyBNrMCzh9M3pZ67MJW074avjSAvsN-aPsdgM_uAQn5AdEJ9mrX__URtFA9cHgt-qhq4zUSFmquy0=)
13. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxXHGb2DDhIV2oeAslSC_DE9WQ17-XbVcdilnTnbv-IGLR-TaRaKXq4uMSyBOLFU_I0dfJukuy2DZFPrA8KGXDe-MzDQFeYuKmTwstsCo0FstlzLyke7tafSlf5eIS2ggSuo5WIWndCNY=)
14. [virginia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFc0DN6Qx57Q0BlTalM6w6UNRIK5sZL7i-a20IgwcZNzOUg9-xiMdoQbtqLOB-fOWdxKsbJPWafFfnwwYyqttRU-MLL5S-yrQzJH0PCVicym2qGTsLR_SotEKtLOoH47dpypOhJisRmya_-tTKVeje7zuWuBU9jlaVd_N2eZ49BD7ModCEQfo99XH2o6Jd4VMR-jA5L314UU8Ct3vDf_ogK9MbrwBM3DGBLMKUhvrAn6hqxlW4WRRBc-7741lPj-0m27SOxxM4=)
15. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKTFqGBgn2sVohMRPzJTALIrfpKZzCCwnbvBDksvzD37A0q6AxsgmPATxQAMeagAQ2QCPH1MmTuogcQGknlyF4Bd8965FemVfDt-g_dW1RUrSJy2bbiSdWl1ANqTdtA_Ztcd2UElA7VC8gRj8wlUUMmAE-buf6GFXEkILV)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJUE2-TjnHvAntIEHEKLKtvDKfqVNN5rbxp9w5aX28ga1XXlBE8S7_EBd79nh78LBAulfN5pK-C0FvVRN9sWnSlNlHvKXKJYKtQglQ-2ykZCaaEm2IZtLy)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnrnGjTDEHgF6ZDyW9Y77_Utwyrurniw7Zd0_p78weHHjDUucDeSGYnr_ZhXKROp2ukRlpR2Vm0NsOBrgd9eGl-gP7ZGRBk3FWwBJew2UeMCxySxXJ)
18. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrheWJ7J3k5RFLXfnga37IngKSGNIrgSKLBlhz5tLmp8w-nwkqcJs6jdfV6-SEV1xNN1gi84lREGh_1tiAcJkgyGxbGYqhnZeJTaCOQbDd_I7RTjy8A_stqBZfjpwopAhDQpnu7dkG)
19. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHO_DY0wfyGHhbeWpztDidiLZVVfk0fZNLTpJegNKcGS-960MDjx845kBHL8eIw7GfeHTDPQ5GYgYR_EEde7WAhiObnLJ2X7e7z2lfpCP2Tpg2RRGHScJzKeSJbhXsc-BVTTUkWIx31BUAywl0o1w4yzk4c7FVqywfYxNBqzWQdnUJOZPRNHd746YoBPz-1A==)
20. [cam.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaiG8HhdMGWcjGa8x4A4UT4VCxKaCHlP5r7OBAggygb7QNvO7iM-pLoqU-34OCSB6SGW2mCzK55NvlLfmig5z_wRBkMr4xnXieS8dEX4YDpOhZ7ZYzKOFF937C_WPULLKchdFAzgcdJmjVoufS-OsB-CKrLEzq_MbIu-uWLncZsA==)
21. [cam.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZaVDgmayod1UPZOPvK9g5Ny-DgMC_WPN-RVEKO31GkgPQe6HelnAzFYGGOBepFTHTsqKH3Vfk1RTfKRVM2bD_6r06jrDJhLUp_CtxPceE7ydaCOy-y0n3L04MvRCuQOl8tFyeuTglvPem6PpSRiY4DpgaCH7P73RvDp7TjfF4hM9nFX4rzrbeFya9MY_qrQxUruM=)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHt5D0VlxU87dRJMmI6tQ_Q-y9YKwGtUSVPH4s1Pb0tCzSJrdv4UBxyrX9AXbHlOm09JaZd2rl8QZ1u_goJyNMBYHX6tVEo8JHeW9ilDudX0KOnlAAi)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOt5WE8ox2miQeShM2C8PyjrVo_wcOu1w_BzjLY7bpdoNDoifPgxyhFkqmDUHPJqsTx_zSgT7dJUS_xSrmjkQzV6yG51YlWfkauig-TBPgFE-k-oRBIHc08k9zlCHllHvZ6igArRzczD5th7MGQ_6xdbk4jtMO3BdHNzWhgbt2qiDIPlZc8MOlY8RTzlT_aB_UcuBih5Sg0_mtoU3hrP6QUvdL68E7XO-HxXZyPg==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNgLNSPFuKX821ni72Tli0UPyC9BPPxEbrsONo2r2t1Xx3-GplGByjvK-GraHxTOolqRdS1zzHLQWwZzef8AukJWp9Z6Wn6ZZDacwWY_VY1I1-a3dtUe8t)
25. [the-decoder.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYQXdl3HrEr8evSb9hlZxsO8Y9ojAeWmDl6XbWJpVALWh99AYBlHSCru6ox29Ko-eQUijbQ6VSXGGXeB9iuABwJ0vTOdUClYkHmA5mZujNY_GJqooCqWVOBvKtSFTUbdoguybfiIkwhJy5jwdj0S6VSe50wmOQZWVUoxrRab-07M4jsEQIh8qMv4mtvl_x-0g8bFjVbFRzRoh3760PHw==)
26. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtu9ynAmXcHpXl394IeYzO3nvgGYTTRK8rx8A8EWmdSBq7OzW82dL1RU7RQgI0tbquHp9ISvzkoPzyn7730tKBhkQP_MCjD9q3y_Jt7pUIVFtFQbR4NaX1_S7gSKTWeB8t)
27. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTbvDi1XEaklw5yb9OYqixvXBQKk9lkfBQeCh50ltt7jA8QJY4rQ5PxyGyrMFElFi96XXnZv0RVsp_7g61VozSDvDR0XtM9q-n2-e6IdpblGEK11eIS7uVZnePE5qDB_CdBtTGN0cS_5weuS9bHcEEXRtZkCTxjQHJXu9b)
28. [ajithp.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEefQ56eNlNSvGHrzvAFbBDkJPhN8Z_EnH_8ImvSqVX7se8ej1_eXCN0mRyM2Gg49jdFpZ62LIGgG8hmlFh9-6wJmi8Rk-YngAq9eldzwM_zeRtcLprUiNsPjRwD4HGe1UT_K6TvgU-9W-Qkw3F-MaZ3nkS9O_c6Q==)

