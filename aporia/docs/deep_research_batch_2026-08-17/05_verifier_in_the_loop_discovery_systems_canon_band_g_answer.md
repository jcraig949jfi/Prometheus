# Automated Discovery and the Formal Verification Selector: An Exhaustive Analysis of Generative Research Architectures

**Key Points**
*   **Generative Research Paradigms:** Current frontier AI systems achieve open-ended mathematical and algorithmic discovery by pairing Large Language Models (LLMs) as mutation engines with deterministic, non-model selectors (such as the Lean formal compiler or programmatic evaluators).
*   **Base Rate Neglect:** The reported successes of these systems often obscure the underlying denominator. For example, AlphaProof Nexus achieved a 2.5% success rate on open Erdős problems (9 out of 353) and an 8.9% success rate on OEIS conjectures (44 out of 492) [cite: 1].
*   **Gravitational Overfit:** Systems like FunSearch rely heavily on human-engineered "skeletons" (e.g., greedy algorithm templates). The AI primarily mutates hardcoded heuristics rather than generating fundamentally novel logical structures, tightly constraining the search space to the human's original intuition [cite: 2, 3].
*   **Novelty vs. Rediscovery:** AlphaEvolve's evaluation on 50 open mathematical problems resulted in a 75% rediscovery rate of known state-of-the-art solutions, yielding genuine improvements (novelty) in only 20% of cases [cite: 4, 5].
*   **Independent Replication:** Independent benchmarks, such as the OEIS Open project, suggest that complex evolutionary agent loops may not be strictly necessary. A generic Claude Opus 4.8 model utilizing a basic ReAct loop solved 30% of 492 OEIS conjectures, significantly outperforming the bespoke AlphaProof Nexus baseline (9%) at a comparable inference cost [cite: 6, 7].

**Executive Summary**
The integration of Large Language Models (LLMs) with formal verification systems and programmatic evaluators has initiated a new tier of AI capability: generative research. By utilizing the LLM to propose hypotheses, code, or formal proofs, and relying on a strict, deterministic environment to falsify incorrect propositions, these architectures circumvent the inherent hallucination risks of raw LLMs. This report systematically dissects the three primary systems in this class—FunSearch, AlphaEvolve, and AlphaProof Nexus. 

**Research Scope**
The focus is placed strictly on the underlying architecture (the mutation engine paired with a non-model selector), the human engineering required to set up the problems, and the exact base rates of success relative to the total number of problems attempted. 

**Analytical Framework**
We evaluate these architectures through two critical attack vectors: the separation of genuine novelty from the rediscovery of known results, and the identification of the denominator (the total number of attempts required to achieve a single success). This analysis is grounded in the recognition of two specific anti-patterns: `PATTERN_BASE_RATE_NEGLECT` and `PATTERN_PRIME_GRAVITATIONAL_OVERFIT`.

***

## 1. Introduction to Generative Research Architectures

The ambition to automate scientific and mathematical discovery has historically been hindered by the vast, unstructured nature of hypothesis spaces and the rigid demand for absolute logical correctness. Standard Large Language Models (LLMs) generate text based on statistical plausibility rather than formal rigor, leading to catastrophic logical failures when attempting to solve multi-step research problems [cite: 8]. To overcome this, recent frontier research has shifted toward a composite architectural paradigm: the generative research loop.

This architecture consists of two fundamental components:
1.  **The Mutation Engine (Generator):** An LLM or ensemble of LLMs tasked with proposing novel code, algorithms, or mathematical proof steps.
2.  **The Non-Model Selector (Evaluator/Falsifier):** A deterministic, external system—such as a programmatic scoring function, an execution sandbox, or a formal proof compiler (e.g., Lean)—that strictly evaluates the generator's output.

By tightly coupling an open-ended generative model with a strict falsification mechanism, these systems achieve a form of artificial evolutionary search. The LLM acts as the source of varied genetic material (code mutations), while the selector acts as the environmental pressure, ruthlessly pruning invalid or suboptimal code [cite: 9, 10, 11]. This report investigates three highly publicized systems that employ this architecture:
*   **FunSearch:** Developed by Google DeepMind (2023), optimizing programmatic heuristics for combinatorial problems [cite: 9].
*   **AlphaEvolve:** Developed by Google DeepMind (2025), a general-purpose evolutionary coding agent targeting algorithm design and optimization [cite: 4, 5].
*   **AlphaProof Nexus:** Developed by Google DeepMind and Aarhus University (2026), combining Gemini models with the Lean proof assistant to resolve open mathematical conjectures [cite: 10, 11].

We evaluate the verified claims, the base rates of success, the human setup constraints, and the independent replications associated with each system, directly addressing the attack vectors of base rate neglect and structural overfitting.

***

## 2. FunSearch: Programmatic Evolutionary Search

FunSearch (short for searching in the *function* space) was introduced by Romera-Paredes et al. (2023) as a method for discovering computer programs that solve mathematical and algorithmic problems [cite: 9]. Rather than searching directly for the mathematical object (e.g., a list of vectors), FunSearch searches for the *program* that constructs the object [cite: 12].

### 2.1 Architecture Overview
The FunSearch architecture is built upon an island-based evolutionary algorithm. It requires an initial human-provided program (the "skeleton") and an evaluation function [cite: 3, 9]. 
*   **Mutation Engine:** A pretrained LLM (e.g., Codey or subsequent models) receives a prompt containing high-scoring programs from a database and is instructed to generate modified, improved variants [cite: 9].
*   **Selector:** An automated, problem-specific programmatic evaluator that executes the generated Python code and returns a scalar fitness score (e.g., the size of a constructed mathematical set or the efficiency of a bin-packing heuristic) [cite: 3, 13].

### 2.2 Verified Claims and Achievements
FunSearch has demonstrated human-competitive or super-human performance on several established combinatorial and optimization problems:
*   **The Cap Set Problem:** A central problem in extremal combinatorics asking for the largest possible set of vectors in an \(n\)-dimensional space over a finite field of three elements where no three vectors sum to zero [cite: 14, 15]. FunSearch discovered new, explicit constructions that improved the known lower bounds for finite dimensions (e.g., from 3.391 to 3.421 for \(n=2\), and 7 to 7.280 for \(n=3\)) and achieved the largest improvement in 20 years to the asymptotic lower bound [cite: 3, 12].
*   **Online Bin Packing:** FunSearch discovered new programmatic heuristics that improved upon widely used baseline algorithms (such as First-Fit and Best-Fit) for standard distributions of interest [cite: 12, 13].
*   **Scientific Computation:** In subsequent applications, FunSearch discovered analytic priority functions that reduced memory and runtime requirements by orders of magnitude for Integration-By-Parts (IBP) reduction in Feynman integral calculations, outperforming Laporta strategies [cite: 13].

### 2.3 Attack Vector: Base Rate and Denominator Neglect
When assessing FunSearch, the literature frequently highlights its peak achievements without contextualizing the volume of computational attempts required. The denominator—how many programs were generated and evaluated to yield a single SOTA improvement—is massive.
*   **Evolutionary Iterations:** FunSearch relies on evaluating thousands to millions of candidate programs. In a smaller-scale application involving LFADS regularization scheduling, a FunSearch configuration ran 50 generations with 10 candidates per generation, evaluating 500 total candidates, of which only 304 (60.8%) were syntactically valid and executable [cite: 16]. 
*   **Speed of Evaluator Constraint:** FunSearch's success is entirely dependent on the existence of a fast evaluator. As noted by analysts, "FunSearch works because the cap set problem has a fast evaluator" [cite: 17]. The system must churn through vast amounts of invalid or useless code, meaning the base rate of success per generated candidate is infinitesimally small.

### 2.4 Attack Vector: Human Engineering and Prime Gravitational Overfit
The most critical vulnerability in the FunSearch architecture is its reliance on human-engineered problem framing, manifesting as `PATTERN_PRIME_GRAVITATIONAL_OVERFIT`. 

The user must provide a "skeleton" solution—a basic framework with a specific component isolated for the LLM to evolve [cite: 15]. Critics have pointed out that the FunSearch team utilized "the simplest possible greedy algorithm, based on priorities which are computed at the start as a function of individual vectors" [cite: 3]. The LLM does not invent new algorithmic paradigms; it merely mutates the scoring function within the human's greedy loop.
*   **Hardcoded Variations:** Independent evaluations have observed that "the variations introduced by FunSearch consist of different hardcoded numbers, as opposed to inserting more structure, like loops or maths-functions, into the program" [cite: 2]. 
*   **Seeding Dependency:** If the system is seeded with a highly structured but inflexible construction, it stagnates quickly. Conversely, a trivial instance with a flexible structure (e.g., a simple `for` loop) improves progressively, demonstrating that the architecture is heavily constrained by the gravitational pull of the initial human seed [cite: 2].

FunSearch is not achieving open-ended discovery from scratch; it is performing hyper-parameter optimization and algebraic tuning within a human-designed greedy heuristic skeleton.

***

## 3. AlphaEvolve: General-Purpose Evolutionary Coding

Unveiled in May 2025 by Google DeepMind, AlphaEvolve scales the FunSearch concept into a general-purpose evolutionary coding agent [cite: 5]. It is designed to operate across a broad array of scientific and engineering tasks, automatically modifying code to optimize for multiple objectives [cite: 4, 5].

### 3.1 Architecture Overview
Similar to FunSearch, AlphaEvolve pairs Large Language Models (primarily the Gemini family) with evolutionary computation. 
*   **Mutation Engine:** LLMs act as evolutionary agents, producing variants of existing algorithms by mutating code based on prompt history and evaluation telemetry [cite: 5, 18].
*   **Selector:** An objective evaluation function that programmatically tests the code, preventing hallucinations and selecting the most effective variants for the next generation [cite: 4].

### 3.2 Verified Claims and Achievements
AlphaEvolve has claimed substantial impact across both theoretical mathematics and applied industrial optimization:
*   **The Kissing Number Problem:** In pure mathematics, AlphaEvolve tackled the 11-dimensional kissing number problem (packing spheres into high-dimensional spaces without overlap). The system discovered a configuration with 593 tangent spheres, establishing a new record and breaking the previous lower bound of 592 [cite: 18, 19].
*   **Matrix Multiplication:** AlphaEvolve improved the state of the art on 14 matrix multiplication targets. Most notably, it discovered an algorithm to multiply two \(4 \times 4\) complex matrices using only 48 scalar multiplications, surpassing Strassen's 1969 algorithm (49 multiplications) [cite: 19, 20].
*   **Industrial Infrastructure:** AlphaEvolve optimized the AC Optimal Power Flow problem, increasing the ability of a Graph Neural Network to find feasible solutions from 14% to over 88% [cite: 21]. It refined Log-Structured Merge-tree compaction heuristics in Google Spanner, reducing write amplification by 20% [cite: 21]. Furthermore, it was utilized to optimize TPU circuit design and data center scheduling [cite: 5, 19].

### 3.3 Attack Vector: Base Rate and Novelty vs. Rediscovery
To separate genuine novelty from the rediscovery of known results, we must examine AlphaEvolve's performance across benchmark datasets. 
*   **The 50 Problem Benchmark:** Google evaluated AlphaEvolve across a curated selection of 50 open mathematical problems spanning analysis, combinatorics, number theory, and geometry [cite: 4, 19].
*   **Rediscovery vs. Novelty:** The results explicitly state that the model was able to *rediscover* state-of-the-art solutions 75% of the time, and discovered *improved* (novel) solutions only 20% of the time [cite: 4, 5, 20]. 
*   **The Denominator:** For every 5 problems attempted, the system generated a genuinely novel mathematical advance in 1 case, rediscovered existing knowledge in 3.75 cases, and presumably failed to match the state-of-the-art in the remainder [cite: 5]. 

This 20% novelty rate represents a monumental leap for AI, but applying `PATTERN_BASE_RATE_NEGLECT` principles reveals that the vast majority of the system's output on open problems consists of navigating toward already-known attractors in the solution space, rather than breaking entirely new ground.

### 3.4 Human Engineering Constraints
Like FunSearch, AlphaEvolve requires an initial algorithm and an evaluation function with metrics to optimize [cite: 4, 5]. Ablation studies revealed that omitting problem-specific context in prompts or disabling human-designed initial algorithms significantly degrades performance [cite: 19]. The system was sometimes seeded with human-designed ideas to further improve outcomes, heavily implying the presence of `PATTERN_PRIME_GRAVITATIONAL_OVERFIT`—the AI optimizes the structure it was handed rather than originating the framework itself [cite: 19].

***

## 4. AlphaProof Nexus: Neuro-Symbolic Theorem Proving

AlphaProof Nexus, published by Google DeepMind and Aarhus University in May 2026, represents the most rigorous application of the generative research paradigm to date [cite: 1, 10]. Instead of relying on programmatic heuristics, AlphaProof Nexus pairs frontier LLMs directly with **Lean**, a formal proof assistant whose compiler mechanically verifies every logical step [cite: 22].

### 4.1 Architecture Overview
The system processes input in the form of a "proof sketch"—a Lean file containing a target theorem where the proof body is replaced by the `sorry` tactic (a placeholder that bypasses verification) [cite: 11, 22]. The goal is to iteratively generate type-safe code that removes all `sorry` tactics, resulting in a machine-verified proof [cite: 11].

The framework features four increasingly complex agent variants:
*   **Agent A (Basic):** Independent sub-agents running Gemini 3.1 Pro. The LLM generates proof steps, the Lean compiler checks them, and compiler error messages are fed directly back into the LLM prompt for the next attempt [cite: 23, 24].
*   **Agent B:** Adds access to AlphaProof, a reinforcement-learning-based tool trained on olympiad-level math, allowing the LLM to delegate specific logical subgoals [cite: 22, 24].
*   **Agent C:** Introduces an evolutionary component. Sub-agents share a population of proof sketches, which are rated for plausibility and novelty by Gemini 3.0 Flash agents and ranked using an Elo system [cite: 24].
*   **Agent D (Full-Featured):** Combines all aforementioned capabilities. This agent was the primary engine used for the large-scale open problem sweeps [cite: 24].

### 4.2 Verified Claims and Achievements
AlphaProof Nexus targeted genuinely open, research-level mathematical problems rather than textbook or competition exercises [cite: 8, 10].
*   **Erdős Problems:** The system autonomously resolved 9 open mathematical problems from Paul Erdős's catalog. Notably, two of these problems had been open since 1970 (e.g., the Erdős–Sárközy problem on divisibility-restricted sets), and one since 1996 (Erdős #125 on base-3/base-4 sumsets, where the agent proved the lower density is zero) [cite: 1, 25].
*   **OEIS Conjectures:** The system proved 44 open conjectures from the Online Encyclopedia of Integer Sequences (OEIS) [cite: 24, 25].
*   **Algebraic Geometry:** Settled an approximately 15-year-old open question regarding the log-concavity of pure O-sequences in codimension 3 and type 2 [cite: 23, 25].
*   **Convex Optimization:** Discovered a novel parameter schedule for Anchored Gradient Descent-Ascent in min-max convex-concave optimization, simultaneously proving an exact \(O(1/t)\) convergence rate [cite: 8, 25].

The per-problem inference cost for these proofs was remarkably low, averaging a few hundred dollars per problem, transforming decades of unsolved math into a standard compute budget line item [cite: 1, 26].

### 4.3 Attack Vector: Base Rate and Denominator Neglect
While the absolute achievements of AlphaProof Nexus are historic, isolating the denominator reveals the true current capability bounds of the system (`PATTERN_BASE_RATE_NEGLECT`).

*   **Erdős Problems Base Rate:** The agent was run against 353 formalized open Erdős problems. By solving 9 of them, the base rate of success per problem attempted is exactly **2.5%** [cite: 1]. As analysts noted, "The overall success rate of 2.5% on Erdős problems... underscores both the system's capability and its limitations. The vast majority of open problems remain beyond the system's reach" [cite: 1].
*   **OEIS Conjectures Base Rate:** The system was run against 492 open OEIS conjectures. By proving 44 of them, the base rate of success per problem attempted is **8.9%** [cite: 1]. 

These low success rates highlight the difficulty of research-level mathematics; even armed with evolutionary algorithms and rigorous formal verifiers, the LLM fails to find a valid proof path in over 90% to 97% of its attempts. 

### 4.4 Human Engineering and Setup Cost
The transition from natural language mathematics to formal Lean code imposes a severe human engineering bottleneck [cite: 26]. 
*   **Formalization:** AlphaProof Nexus requires the mathematical problem to be expressed perfectly in Lean [cite: 11]. For the OEIS sweep, the 492 conjectures were "autoformalized" from natural language using Gemini [cite: 22, 23]. 
*   **Misformalization Guardrails:** Because LLMs frequently misinterpret mathematical nuances during translation, the researchers had to mandate that the agent first prove "test lemmas" (verifying that the Lean formalization matches the first few terms of the integer sequence) before attempting the actual target conjecture [cite: 22, 23, 27]. 
*   **Human Review:** Despite autonomous proof generation, humans must still review the initial formalization to ensure the AI did not solve a trivialized or mathematically distinct version of the intended problem [cite: 22].

***

## 5. Independent Verification and Replications

A critical component of this investigation is examining independent replications to verify whether the complex, multi-agent architectures presented by the original authors are strictly necessary, or if the underlying power stems simply from pairing an LLM with a formal compiler.

### 5.1 The "OEIS Open" Benchmark (August 2026)
In August 2026, Tom Adamczewski introduced "OEIS Open," an independent, open-source benchmark based on the exact 492 OEIS Lean conjectures formalized by the DeepMind team (Tsoukalas et al.) [cite: 6, 7]. 

Adamczewski developed a secure evaluation tool called `SafeVerify` and tested *generic* language models against the DeepMind baseline, utilizing a deliberately simple "ReAct-style tool loop" rather than a complex evolutionary agent ecosystem [cite: 6, 28].

**Key Independent Findings:**
1.  **Generic LMs Outperform AlphaProof Nexus:** Using the simple ReAct loop and a strict budget of $50 per attempt, **Claude Opus 4.8 resolved 30%** of the 492 conjectures (144-147 conjectures). GPT-5.5 resolved 26%, and Gemini 3.5 Flash resolved 22% [cite: 6, 7]. 
2.  **Baseline Comparison:** This 30% success rate vastly outperforms the AlphaProof Nexus baseline, which reported a 9% success rate (44 out of 492) at a similar $50-per-conjecture cost [cite: 6].
3.  **Architecture Implications:** The OEIS Open results strongly suggest that the highly engineered, evolutionary, Elo-rated multi-agent architecture of AlphaProof Nexus (Agent D) may be unnecessary for these problem classes. The raw reasoning power of frontier LMs (like Claude Opus 4.8), when simply grounded by iterative Lean compiler feedback (equivalent to the basic Agent A), is sufficient to eclipse bespoke architectures [cite: 6].

### 5.2 DeepMind's Internal Ablation Confirmation
Interestingly, DeepMind's own post-hoc analysis corroborated the findings of the independent OEIS Open replication. The researchers admitted a "surprising result": their simplest Agent (A)—which merely looped Gemini 3.1 Pro with Lean compiler errors and lacked any evolutionary or RL components—was also capable of proving *all nine* of the solved Erdős problems, albeit at a higher inference cost on the hardest problems [cite: 1, 24]. 

This finding isolates the true engine of discovery: **"the power of compiler feedback in grounding LLM reasoning"** [cite: 24, 29]. The complex non-model selectors (evolutionary islands, Elo raters, PBT) provide compute-efficiency optimizations, but the foundational capability rests almost entirely on the deterministic falsification provided by the formal verifier [cite: 29].

### 5.3 Open-Source Implementations of AlphaEvolve
Following AlphaEvolve's publication, the open-source community rapidly replicated its architecture. The most prominent replication is **OpenEvolve**, developed by Asankhaya Sharma [cite: 4, 5]. OpenEvolve successfully implements the distributed evolutionary algorithms and multi-language support described in the original paper, proving that the generative research paradigm is easily reproducible without proprietary Google infrastructure [cite: 4].

***

## 6. Synthesis of Attack Vectors and Anti-Patterns

By synthesizing the empirical data from FunSearch, AlphaEvolve, and AlphaProof Nexus, we can rigorously address the specific attack vectors outlined in the problem statement.

### 6.1 PATTERN_BASE_RATE_NEGLECT (The Denominator Problem)
The public perception of AI mathematical breakthroughs is heavily skewed by the selective reporting of successes. The denominator is the true finding of this analysis:
*   **AlphaProof Nexus (Erdős):** Base rate = **2.5%** (9 successes / 353 attempts) [cite: 1].
*   **AlphaProof Nexus (OEIS):** Base rate = **8.9%** (44 successes / 492 attempts) [cite: 1].
*   **Claude Opus 4.8 (OEIS Open):** Base rate = **30%** (147 successes / 492 attempts) [cite: 6, 28].
*   **AlphaEvolve Novelty Rate:** Base rate = **20%** (Improved bounds on 10 out of 50 attempted open math problems) [cite: 4, 5].

When an AI system is deployed as a generative research agent, it functions more as a high-throughput computational sieve than an autonomous mathematician. The low base rates indicate that while the LLM + Verifier architecture is capable of exploring the combinatorial space of proofs, it relies on brute-force iteration (constrained by compute budgets like $50 to a "few hundred dollars" per problem) to stumble upon valid logical paths [cite: 6, 26, 28]. 

### 6.2 PATTERN_PRIME_GRAVITATIONAL_OVERFIT
The extent to which these systems discover novel structures versus optimizing structures they were seeded with is a critical vulnerability in their epistemological claims.
*   In **FunSearch**, the requirement for a human-provided "skeleton" algorithm ensures that the AI cannot escape the gravitational pull of the human's original intuition. The LLM modifies priority functions and hardcoded numbers within a greedy loop, but it does not spontaneously invent entirely new algorithmic architectures like divide-and-conquer or dynamic programming if seeded with a greedy template [cite: 2, 3, 9].
*   In **AlphaEvolve**, ablation studies confirmed that performance collapses when problem-specific context and human-designed initial algorithms are removed [cite: 19]. 
*   In **AlphaProof Nexus**, the LLM is constrained by the Lean Mathlib library and the specific natural-language-to-Lean translations engineered by humans [cite: 27, 30]. The agent is searching for a path between two firmly human-defined points (the axioms and the target `sorry` goal).

### 6.3 Distinguishing Novelty from Rediscovery
Determining whether an AI generated a genuinely new mathematical insight requires rigorous historical awareness [cite: 30]. 
*   AlphaEvolve explicitly separated these metrics: on 50 open problems, 75% of its outputs were mere rediscoveries of state-of-the-art solutions generated by humans decades prior [cite: 4, 5]. Only 20% represented genuine mathematical progress (such as the new 593-sphere lower bound in 11-dimensional space) [cite: 18, 19].
*   AlphaProof Nexus circumvented the rediscovery problem by exclusively targeting open problems (Erdős and OEIS) that were historically unsolved [cite: 24, 26]. Therefore, the 9 Erdős proofs and 44 OEIS proofs are, by definition, mathematically novel, though their strategic importance to the broader field of mathematics varies [cite: 31].

***

## 7. Conclusion

The current frontier of generative research is defined by the marriage of Large Language Models to deterministic, non-model selectors—primarily programmatic evaluators (FunSearch, AlphaEvolve) and formal proof compilers (AlphaProof Nexus). 

**Verified Claims:** These architectures have unequivocally generated novel scientific knowledge, improving combinatorial bounds, optimizing industrial algorithms, and formally proving decades-old open mathematical conjectures [cite: 12, 21, 26].

**The Denominator Reality:** The success of these systems is heavily obscured by base rate neglect. In rigorous, large-scale deployments, the success rate per attempted problem ranges from 2.5% to 30%, depending on the difficulty of the problem set and the specific model utilized [cite: 1, 6]. The systems rely on high-throughput generation and relentless falsification to filter out the vast majority of invalid ideas.

**Human Engineering Costs:** None of these systems operate in a vacuum. They suffer from structural overfitting, requiring intense human labor to frame the problem, define the evaluation metrics, formalize the code in specialized languages like Lean, and provide the initial algorithmic skeletons [cite: 3, 11]. 

**Architectural Necessity:** Independent replications, most notably the OEIS Open benchmark, demonstrate that the complex evolutionary and RL-based agent architectures popularized by DeepMind may be superfluous. A generic, state-of-the-art LLM equipped with a simple ReAct loop and grounded by a formal compiler can vastly outperform highly engineered legacy systems [cite: 6, 28]. The true breakthrough is not the multi-agent evolution, but the uncompromising, deterministic feedback of the formal verification selector.

**Sources:**
1. [mlq.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvYzH_n0JOEYl4eMN9elnOnfAFqvwfM525LH-WJ-AZRrPXLcD7GjZ-Ftxod9FWWs5SHJv_rjuDohKlMD606bIMA5qGQcUNortXJA6vza_UF0xIGwn3UpOp4f9S5KfZSBbPma-Um2zRiZWnUFZvxNsOSeRt180gU4A-FEVGLnVKhfm4ZL3If7hSL9a9z3Io3Cn5rp1HTtaN73W1dlUw2-iZbl2hjpKMQiCWTLtN)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVlWikqa2aeCo1a0WXWQJVvEojEw-zdt8Q8Hu7USre1uorI1djHXPpJ-wFoDKawcMmGnzE2LevVnuLtKBGcIoOXXYgHdZnuyiS8l4vhNHtIBJEQyum)
3. [nyu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-O6CGyG-H-4NHF_u84cuiFHAKmrTPQMMgsy3hvjxVX0evUU7M5M9XLgGRa0p-LNLRb5hVNBlxGg4B11Tb2rM6tjkIUdGdZXYaUCh4UQO65p2v7eqwkL9eO43oduKQ5ih0UvX4)
4. [handwiki.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvIWhDqQ2otnNSTOu6AY68JtsgR_6-UeEd6V_5w9uys9PxXBiqtlKE7LM8-eWuUazAXtQwSN7-zSzYTwCcYoNv2h0QBOjn1xpyn97HhwDADP7OuvsK-FHPU_M=)
5. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEjL2Jj2qmIZkzMXMy8wxr5tXO6zpASKstuupTNB9eZDZZv2jn6iVPgcFv7TmPqWHQeOW0mHnNLLTFjJS0gpd9QAJgELTUIpAv4erNLRsT4wlIK3-McOw8OlXWC8m4)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaaYvZRHAP62u8NAbms749k2qes21Ke3SUJLvnnHUy_hEYpGkjxMFBs0Be2ZauLeECl6DMLKu1zxuz65qH8Jm37yCcjGrkM0GI8OM6y31uzTirTQZMiYmT)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgv-SY--L9h6LXVR4JHWstLfA3WZb0W-xm9YAdCmrm5jcjltCNCx0LWl03Hp7Qjc6sciYLg284taF1V_S0AGYtIUTCorz20beuG-eTBM15wbLifaxvto986HWMrec1hyV619PD6-flDJBgxcyVe6Eea4UHlyBQVmLdd28LnbZQp9tov3pKPPaMBOtR9EDJ2W0DoeqLCaHtcom_yUADmczjnJOK2v23oswbb53A5frjAs35901ctbGM9PyL)
8. [dev.to](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_XdHy29tPhoJbKHycn9h3Y7LtWSsyWzdSj7TMc3t41_WRDQV2b7OhoHVOu0o1E5Nxjp4AXbKRNCp_iUSGE5V8hW6iAG_pQ8mIYMkuIzogBcZXr5EM3ebv8sKDxx7yfJzYPr8HD7gXPsBKWiMm2QoiO0PgpiRM_mA7ywHvDWAwKoewr6zQlt4CxRqVEmshOgLASpnMLgY88uLOuk-6ycDXt_3gEVR-vo39)
9. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEeM0qCF6l5Yf_N9KHN3YaMx2etfRoGTFCg4GNy198R3pajhJCGxHxReR4mLgt-sj8OYXwFUhtLqfpjIBX2zUzAkzdXK0iiu5Uc-IcMKuDQWPdWv5x6V7QFXBlk3w==)
10. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHx0midE8k7koHRGWOXta3QIAa530a-OMMmE5Hyy1FPh86LVJX_MV3DIC6MZWETPyt69BlirleEc77GzDyMC29M2Hs6s7_DYoKvZuhfKyoeLxNrFb6-xAb0EAMZdFeUlJXulMg=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8wROx2lrz5Ut7o_hPlcXSdYOyEPK0C5dLU5r8OH44jmrQ7EsE_qoReTQafXgFmtAfeINdyWD1dISke--ecHelHu2Dfes2IlKAf1R_KW7H1W2pO5bEZSlV)
12. [googleapis.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0DGJC8zyTywCQfKfMuM3WsVKlsPguAGk_2T5HnTq5p6AGfjmgwOVApF2qXFHE9xtokVYQPwtb2MISZJLRqH0zpZdthYMbl0ksYQW-Wlv9TsaZlzqemx3ABw4BbEf2cb7CPAvUZUqUCdAfaZEn70yIqNvfYrWU5pFWT3jL23CpO4t8iA8PsrHtNA5FqE7Rdz881-MN_LATYZS6sHkn6Z2gXpA-TbMlzWNAzOcptqLa-QfI5BiwC9SiZY1cDpMmE7y3P-GVohs3o7s1JRluHHP-LqrKrCdL8-BImstoELzAEcocTqapIL0AzIlGNTJ2fc_CPiXS0dsncKx7K-nitf3W2BAKYkfYIkZ4TM4ISL1_4-BJnQQXcbI=)
13. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfE3kKLb1wfxuJ4I9ZhACjGy_zGhANKeyIang_QGuNWzfIdIONXvvA_0xR8qnHnk9mwe3awrnFqKFF88dj9IOBzbJsw2U7FaJ9Vm7fejj5VnuVI9VuVYnLBcV0GsD1fS-_QKsz12pfPpQJXh8=)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3N94rzIK2uD6syAN2czSVQeuGw9P4_PgjOxX9pbzdhMp1KDJ2Acd-pvvuKi9U9SLIA0INc1xlJiZUytLZ0i1A8zxEejMkIOS3hIrBNOoDgDjnQbHrArjqj3pt9VgE3QJpBIYFz0-o8i-LSueC_LfRLDWgg4-SbyubYKdnrvQN-Ye-LE9nknEWU6xcH47hSmGWE_eEopjZt2KSftd9fEL_vDsNAVuMX72TCf49SxDiiNYZHA==)
15. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPFqSElU2V_ZZKz_amEGWY0mFkp60lQS_p__Ve0D1VhwGcEf5IrPbFc_fW7d94ogQX4QWUf6RGMUUsVshc-IY_bTrWq0jTXotCvMxNzsHSEALmUiEFOfX8F912_7_J2VGYPIoo-auorW3okOiBCk29bbZKs8wZcc0vaXesF3rkR72Js3C8wukBOlfK9El9qZBKF2tB4Cw1yg8XuqOFls7oOIdJccdgTCufJSaHVBDDuk0We7gp4E4c)
16. [biorxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhwuFpdu4oIg-M5KyJf6J0CyU__raAUzdmC6gEtWYLPIg2y9lr42ZSxlT5Z5epNNsIr9LrSPIxZOUSloRdBO4OM_7HV6D2_-gUxlinNTph5lYhdTIU37T-22u06PbO6u2nS31_L1TH_q3xOrOW4yNmLcNCMFUhEr6fB5w=)
17. [towardsai.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFG1SMPb7pvNL9nUGFL0ZHKAWEyTp9-hdY6tAIr5CDS9x-aJiek_nerzPXhIuvm4MnyqNPwq43duSEMBxj__kbDXBDMIGVzAw00rfPPaIJThkdGhFZ7WPrIyt1uq1qH-jEmPpq3P_mo6u9LC47iBe52th-2vYdAXM6U2xSH_6awYg==)
18. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdYCMAPZJGe-XMfW3T2mYMfhjiaGLsKyyF9HADmsSTm99_GwnIPcuL8AAL2xsgZqEKbhZzHmCK_tVrc06JCOsBurDebq6ZEjKdM_tXgT3kmek-GyMx7Hi1RJjGsusFqfXum_EV5QBpejs98jF4XsdLJRPc_-qye9poRcFoO22QPWP4f4b-sZNHjTIjsQzSGNJYbY2AwkK1krhnwo4_hb2pX18rKeTITPTc2skYDy4=)
19. [andlukyane.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxM6WPKUm5U7TnpdmzLFl0INSJtpPyUK6YrPoAr-4n7tD9xC5rNWSnxZvihPQHHMdxvE-FRq9Md2hV-2Zze-jLFTNaKbNx6AoJhAC8U5-qZlHBY0m56zaDdsCL9MeoslnJg7cWXVy7ttI=)
20. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0ogkeuUwtzE7Fp03sxzypV0eqQBmgZNNV3uyLqBpp-47p9sIqv4F2JovERAm9ZwjxpqpDOscyQINiylFVa4xTFfHcgJC84yDbJX0mh1ipcSy6C5VkwQYkltvAhwAErKJDtKTae109bFpadQrl5FGFmoDAK5iU_hr-3_z5hshvMDdE9yG-7v7qPXVEHpYF8eEvIriXjvwzfMFAzgir)
21. [deepmind.google](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETjTHtwXRPTY6KMsRMHfuQSUJ58u0cP_vcKqL1TaQueZVwgIM2kQUswDpT9G8j3EKDsW4Xtm1khSOOnoVyyerK5dgPhbVZOUDjCwKNxDtjLzVtm0szdYLQ--al8jQQFsm0uRhMZg==)
22. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-ZHH7JcfwEr0bwoHeFhmNv9f90NAfq8u_ir4MdgA6-qvgJMWaeEEqgvCzxbiTyDSKADa0ehTNGQot2g3ge5m2qqL9CJMedBltnR2ceZkRV07GYYgqfGMxlvHb7XrRmPOBASf27Kj5LZ1ualsvP2QBM8n0TP1jC-wFNy-bl4CirsebzLk6CjzDxqVvD5S1pK9cY367Xik7w6Q_qOS93HKXLCOMf3EMIMLwxRam0Pz3znuKDweMtlathY0UlYheOg==)
23. [36kr.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwSylTvzSK92MiA_PcmnIXWlXrG6pENgKJUGqn50foX0cFSV_iclsAtDIMmJvxllwYyos5DXzsfE4J4ntYViIQDpDoYG7HwTntnKozJKRdC8EaMs6ohmVUD3mE1_9C)
24. [the-decoder.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjQRnC8SZ0JNmHPqjPhksu_FR8RY1tguDYfeMY6NnYdxTSjL2IbP8k4AfZFOlDPv5duvzsZgdypYxMO-k8Zg5MGwmkuqeeyb5PmsLeXPNRX29rOoZU-fuGwQlt81TNh38yHJEuZPYNKCwS6mhoeI4k1HKq-ASXBUaT8Qak7Xag7oxC_fRK3ZDMG3p1kFtMhJq9EktuC0xJgbq_WAHEeGlU_7FZFjvWTvLpCA==)
25. [facebook.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNr_UYMGlBVTOUBtyi0YovWUy_5M5i5lDtXjdtqD0lT73FUPT74RF2jKoO8qKddR-kUfuE2X5d_Mt0mgphSYkY3QP1yfLcLe_j9qV7RmU9LC2iODOVPCPBK1cF1mCgjafG7DqEkVvIVyzcHhvssmcub8yPRid9crVcHAf2cdez_dGOkTqqbrqeialjOuC61AEPPg329fj4sE9YGs1vfPjwwpg6KIoN5cJ_kv6rq8nW_kVXtKZCluwyWe3rwinTZqg=)
26. [aiweekly.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1isez8P5D8-zcAeDZnBoqMEwhYOvAcwuU4C_VLexOVTchUABmXrf03-5jv74gdoahLZ5hasqYKxjJVNog8QZJOOXvaApz-YvVUV2zKAYc5joLi7aqF5ACmuqQTLLoHm__Mw2ek9kzUz0lIZ2Kk6swLQas7PWqg-p3QdxtZNtW4g==)
27. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGH0aZh0EC9wAw2yPgdfaDphVPI6ajsRe5znbAzg87GqZSJDGq_S1ayBsiL7PFEzfCWobMW7mFfww2pOJB5oUwWnsO8_etuZWzVYfpZaNlujKmwzJUwz8OWx60YOMUba_9ZwVfzBMqKRxoxoeLZaoOakZnlbpEvQEfZNSlC3yRUK-Aj0WZ8KpOC8rMJNbQONc4lag==)
28. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDRH34lVtmX94d3YjUU2xntLPh7qcuy-50BVt9rh_zDmB1sshS4556_4zR9lAr6oP5fALetu6SughRTKw5aU8b94hipVVFy9PzRph_RbsgBU-zw-x23WvlFh_Ex5QFiT5EIGHkwUPE3M2qhrhnfa0Ai9uc9VX4I5RzeVedGZ9bUhSI02opvnclhdb8bVeWkbqtrM9qK9p7_HGw53U4WUAm)
29. [ascii.co.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuN1FrUPY-Cxki1flsU3Qb2PxbvRZUliZQ7hUT_RDnT3v7GX5nn36Xh-ltRJtzPU5HAYaIHY6FDHcIK0pVWmeMznOZliDacM-FXj5qMLtx1yF0SWDqF2zTeBCa8KQm095P8hu1PoGUmM0MdERZjE1mAVv_QCilWD9RJG24M5ahFFrSerlc2vu3TK3-fXQGud4PI_0GAtxuSdZB1ttg7gt-bG5v0kOLrkcii-O-a9xeUdJY)
30. [yutori.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHS7_O_beV4qX_sbnRj1dyRShRDBDsZ7k8jTps7VgZ7Cgyvax2wygx2yYWDa6NqhgGnXtTiOR-sW1nQLXM-75y6nxS215SINrn1r_k9JLkBBS3wWSeKt0M9EExaNHzyXsRAx2aCLcnY5HyKWCD3jKpRbTOr)
31. [startupfortune.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXhjGaIRhf09Zfvih1ozLlXGb00YqGKc6jU648ifcV1ylWtjY5qAYbZ2KQyBa9wnWlaGK2vU-P9gDb2TLIrronkD6D8_TrFvXGNLsx4bYUh6Sl8g6f1uwHE8veZfHUbfwnaAjFmYj3WqWbDIv3kYm6VaXv4mV6eQFoJj0ZcGEiWg==)
