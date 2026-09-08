# Prompt 40: Proof Search

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdFbGFmYXBYTE1LVzVzT0lQMHVTTTJRZxIXRWxhZmFwWExNS1c1c09JUDB1U00yUWc
**Elapsed:** 334s

---

# FRONTIER PRACTITIONER DOSSIER: PROOF SEARCH IN 2026

The domain of neural theorem proving and proof search has advanced rapidly, transitioning from specialized curiosity to a frontier discipline integrating reinforcement learning, large language models, and formal verification. You asked for a concrete, skeptical, and practitioner-focused briefing on how to enter this field today, anchoring on the method of language models generating tactic proposals that are evaluated by a formal logical kernel.

Key points to understand immediately:
First, the field has coalesced almost entirely around Lean 4 as the formal kernel, absorbing mindshare from Metamath and Isabelle.
Second, the benchmark landscape is currently in crisis; the standard historical benchmark has been both saturated and exposed as methodologically flawed, requiring entrants to use revised versions or entirely new datasets.
Third, the frontier has moved past simple tactic generation into recursive subgoal decomposition, test-time reinforcement learning, and agentic code-interaction loops.

The method you described in your query remains the core engine, but the wrapper around it has evolved. Your understanding of the basic mechanism—a transformer sampling candidate steps, checked by a kernel, guided by a best-first search or Monte Carlo Tree Search—is correct. However, in 2026, state-of-the-art models no longer rely purely on step-by-step tactic generation. They employ "truncate-and-resume" strategies for whole-proof generation, synthesize informal chain-of-thought reasoning before emitting formal code, and use test-time variant generation to scale compute during inference. A model proposing an illegal step still wastes compute, but modern systems mitigate this by allowing the agent to read the kernel's error message and correct itself in a multi-turn loop.

Below is the detailed dossier, structured exactly as requested, providing the tacit knowledge required to build and measure frontier experiments.

## PART 1. THE FIELD IN 2026, AND ITS FRONTIER

In 2026, the field of neural theorem proving is fundamentally about aligning the intuitive, pattern-matching power of large language models with the unforgiving, exact logic of interactive theorem provers. The dominant paradigm involves generating synthetic training data by autoformalizing natural language mathematics, training models to emit formal proof tactics, and using tree search algorithms driven by the formal kernel's binary feedback (proof state valid or invalid) to discover solutions. This is no longer a purely academic exercise; it is heavily resourced by major AI labs aiming to bootstrap general reasoning capabilities that do not suffer from hallucination.

What is SETTLED:
Lean 4 is the undisputed standard environment. Over the last three years, the field has effectively absorbed the communities previously working in Metamath, HOL Light, and Isabelle. While those systems still exist, the overwhelming majority of machine learning infrastructure, open-source tooling, and benchmark development is now built exclusively for Lean 4. What was lost in this merge was the diversity of foundational logics, but what was gained is a unified, highly active engineering ecosystem. Furthermore, it is settled that pure supervised fine-tuning is insufficient. The frontier strictly requires reinforcement learning from formal feedback (correct/incorrect proof states) and massive test-time compute scaling via tree search or multi-turn agentic loops. 

What is CONTESTED:
The primary architectural disagreement is between the "Proof Search" paradigm and the "Agentic Coding" paradigm. On one side, teams like DeepMind (with AlphaProof) and DeepSeek (with DeepSeek-Prover-V2) advocate for highly specialized, AlphaZero-style tree search algorithms that generate millions of problem variants at test time and recursively decompose mathematical goals into subgoals. On the other side, teams like Mistral (with Leanstral) argue that theorem proving should be treated as a software engineering task. They deploy generalist Mixture-of-Experts models inside code-agent harnesses (like Mistral Vibe) that interact with the Lean language server exactly as a human developer would, reading files, compiling, and editing, rather than searching a restricted tactic tree.

What is OPEN:
The translation boundary between informal mathematics and formal code remains fully open and highly brittle. Autoformalization—having a model read an English math problem and write the exact Lean theorem statement—fails frequently. Furthermore, Olympiad-level geometry remains largely unsolved by pure language-model proof search; it currently requires dedicated symbolic geometry engines (like AlphaGeometry 2) because synthetic geometry does not map easily to the algebraic tactic states used in Lean. 

## PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL

Authors: Stanislas Polu, Ilya Sutskever
Year: 2020
Title: Generative Language Modeling for Automated Theorem Proving
Venue: arXiv
Identifier: arXiv:2009.03393
This is the GPT-f paper that proved language models could generate formal tactics well enough to close proofs in Metamath. A practitioner must know it because it defined the standard proof-step generation paradigm and the baseline metric of pass-rate under a fixed expansion budget (cite: 35, 36, 37).

Authors: Guillaume Lample, Marie-Anne Lachaux, Thibaut Lavril, Xavier Martinet, Amaury Hayat, Gabriel Ebner, Aurélien Rodriguez, Timothée Lacroix
Year: 2022
Title: HyperTree Proof Search for Neural Theorem Proving
Venue: NeurIPS
Identifier: arXiv:2205.11491
Introduced HyperTree Proof Search, adapting Monte Carlo Tree Search for unbalanced hypergraphs in theorem proving. Essential reading for understanding how search policies and value critics are applied to proof states (cite: 21, 22, 23).

Authors: Albert Q. Jiang, Wenda Li, Szymon Tworkowski, Konrad Czechowski, Tomasz Odrzygóźdź, Piotr Miłos, Yuhuai Wu, Mateja Jamnik
Year: 2022
Title: Thor: Wielding Hammers to Integrate Language Models and Automated Theorem Provers
Venue: NeurIPS
Identifier: arXiv:2205.10893
Demonstrated that language models are terrible at premise selection but great at high-level reasoning, solving this by integrating external symbolic "hammers" to close low-level goals. Crucial for understanding why you should not force a transformer to do retrieval purely from memory (cite: 25, 26, 28).

Authors: Kunhao Zheng, Jesse Michael Han, Stanislas Polu
Year: 2021
Title: MiniF2F: a cross-system benchmark for formal Olympiad-level mathematics
Venue: ICLR
Identifier: arXiv:2109.0110
The original definition of the most famous benchmark in the field. You must read it to understand the historical evaluation standard, even though the dataset itself is now considered deeply flawed (cite: 43, 67).

CURRENT

Authors: Huajian Xin, Junxiao Song, Zhihong Shao, Bo Liu, Xuan Lu, Wenjun Gao, Qihao Zhu, Dejian Yang, Zhibin Gou, Fuli Luo, Chong Ruan
Year: 2024
Title: DeepSeek-Prover-V1.5: Harnessing Proof Assistant Feedback for Reinforcement Learning and Monte-Carlo Tree Search
Venue: arXiv
Identifier: arXiv:2408.08152
Introduced the "truncate-and-resume" method, which bridges whole-proof generation and step-by-step search, allowing models to correct failed proof attempts dynamically (cite: 47, 48, 49). 

Authors: Zhihong Shao, Junxiao Song, Huajian Xin, Haocheng Wang, Wanjia Zhao, Liyue Zhang, Zhe Fu, Qihao Zhu, Dejian Yang, Z.F. Wu, Zhibin Gou, Shirong Ma, Hongxuan Tang, Yuxuan Liu, Wenjun Gao, Daya Guo, Chong Ruan
Year: 2025
Title: DeepSeek-Prover-V2: Advancing Formal Mathematical Reasoning via Reinforcement Learning for Subgoal Decomposition
Venue: arXiv
Identifier: arXiv:2504.21801
Defines the current open-source state of the art in neural theorem proving. Details how to use a massive reasoning model to generate chain-of-thought subgoal decompositions to create cold-start data for a smaller proof-search model (cite: 50, 51, 74).

Authors: Thomas Hubert, et al. (DeepMind)
Year: 2025
Title: Olympiad-level formal mathematical reasoning with reinforcement learning
Venue: Nature
Identifier: DOI 10.1038/s41586-025-09833-y
The AlphaProof paper. This is mandatory reading for its description of test-time reinforcement learning and variant generation, which allowed an AI to reach Silver Medal performance at the IMO by scaling compute over days rather than minutes (cite: 14, 68, 71, 72).

Authors: Roozbeh Yousefzadeh, Azim Ospanov, Farzan Farnia
Year: 2025
Title: miniF2F-Lean Revisited: Reviewing Limitations and Charting a Path Forward
Venue: NeurIPS
Identifier: arXiv:2511.03108
A devastating critique of the miniF2F benchmark, revealing that over half the problems had critical errors or simplified formalizations, dropping state-of-the-art end-to-end accuracy from claimed highs of 97 percent down to 36 percent. Essential for benchmark hygiene (cite: 55, 57, 59).

Authors: Mistral AI
Year: 2026
Title: Leanstral: An Open-Source Code Agent for Lean 4
Venue: arXiv
Identifier: arXiv:2608.leanstral
Defines the agentic, rather than search-based, approach to theorem proving. Details a 119B Mixture-of-Experts model that treats Lean 4 as a standard coding environment rather than a specialized reinforcement learning gym (cite: 78, 79, 81).

## PART 3. SOFTWARE I CAN ACTUALLY RUN

LeanDojo (and LeanCopilot)
URL: https://github.com/lean-dojo/leandojo
Implementation Language: Python, C++ (Lean 4 bindings)
Licence: MIT
Most Recent Activity: 2026 (v2 active)
Maturity: MAINTAINED
This is the foundational infrastructure for interacting with Lean programmatically. LeanDojo extracts abstract syntax trees, proof states, and premises from Lean repositories, and LeanCopilot allows you to run models natively inside Lean as tactics. You can use this today to trace a math library and train a custom premise retriever. The known limitation is that managing Lean toolchains and exact mathlib version dependencies is notoriously fragile; if your environment drifts from the exact commit LeanDojo expects, the extraction fails silently or crashes. 

DeepSeek-Prover-V2
URL: https://github.com/deepseek-ai/DeepSeek-Prover-V2
Implementation Language: Python (Transformers / vLLM)
Licence: MIT (Code), DeepSeek Model License
Most Recent Activity: 2025
Maturity: MAINTAINED
This contains the reference implementations and model weights for the 7B and 671B parameters models that currently dominate open-source leaderboards. You can run the 7B model locally to execute proof searches on novel Lean 4 statements. The main gotcha is that the reported 88.9 percent pass rate requires a pass at 8192 configuration—meaning 8,192 independent inference rollouts—which requires a massive multi-GPU cluster. To run it on a single workstation, you are restricted to lower budgets (e.g., pass at 32), which drops performance to around 76 percent (cite: 51, 77, 85).

Leanstral 1.5
URL: https://huggingface.co/mistralai/Leanstral-2603
Implementation Language: Python (Mistral Vibe harness)
Licence: Apache 2.0
Most Recent Activity: 2026
Maturity: MAINTAINED
An open-weight Mixture-of-Experts agent specifically for Lean 4. Unlike DeepSeek, this acts as a code agent. You can run it today to take an open Lean 4 file, read the compiler errors, and attempt to fix the proof interactively. The limitation is that it requires 200k tokens of context to operate effectively, demanding high-VRAM hardware (though only 6B parameters are active at once) (cite: 78, 79, 80).

miniF2F_v2
URL: https://github.com/roozbeh-yz/miniF2F_v2
Implementation Language: Lean 4
Licence: Apache 2.0
Most Recent Activity: 2025
Maturity: MAINTAINED
This is the corrected evaluation harness for the field. You can run your model against this today to get an honest assessment of its Olympiad-level capabilities. It splits into two subsets: v2c (competition level, exactly matching informal math) and v2s (simplified). Be explicitly aware that any software still reporting against the original openai/miniF2F repository is generating inflated results due to broken formalizations in the original dataset (cite: 56, 63, 64).

ProofNet
URL: https://github.com/zhangir-azerbayev/ProofNet
Implementation Language: Lean 3 / Lean 4 (ports)
Licence: MIT
Most Recent Activity: 2023 (Original), 2025 (Ports)
Maturity: DORMANT (Original) / MAINTAINED (Ports)
The benchmark for undergraduate mathematics. The original Lean 3 implementation is effectively dead because the Lean 3 compiler is unbuildable on many modern toolchains. You must use the Lean 4 port maintained inside the DeepSeek-Prover repository to run experiments today (cite: 32, 34).

## PART 4. DATA AND BENCHMARKS

miniF2F-v2 (v2s and v2c)
URL: https://huggingface.co/datasets/roozbeh-yz/miniF2F_v2
Size: 488 problems (split into valid and test)
Licence: Apache 2.0
Measures: Automated theorem proving and autoformalization accuracy on high-school and Olympiad problems (AMC, AIME, IMO). 
Status: This is the authoritative benchmark. However, it suffers from massive contamination risk. Because AMC and IMO problems are heavily discussed across the internet, large language models have almost certainly ingested the informal solutions during pre-training. Furthermore, Leanstral claims to have 100 percent saturated the validation and test sets of this benchmark in 2026, meaning it is no longer useful for differentiating frontier models, though it remains a necessary sanity check for newcomers (cite: 40, 56, 63).

PutnamBench
URL: Included via DeepSeek-Prover repositories
Size: 672 problems
Licence: MIT
Measures: Proof search capabilities on extreme-difficulty undergraduate competition mathematics (the Putnam competition).
Status: Highly authoritative and far from saturated. Current frontier models (DeepSeek 671B) solve roughly 49 out of 658 problems. Code agents (Leanstral) claim higher numbers using massive token budgets, but it is the current standard for proving genuine reasoning rather than memorization (cite: 50, 51, 79).

DeepSeek-ProverBench
URL: https://huggingface.co/datasets/deepseek-ai/DeepSeek-ProverBench
Size: 325 formalized problems
Licence: MIT
Measures: Generalization across undergraduate mathematics (calculus, linear algebra, topology) and includes 15 highly restricted problems from recent 2024 and 2025 AIME competitions.
Status: Designed specifically to mitigate the contamination issues of older datasets by using freshly minted contest problems (cite: 53, 77, 85).

FIMO (Formalized International Mathematical Olympiad)
URL: Access via AlphaXiv/GitHub references
Size: 148 problems
Licence: MIT
Measures: IMO Shortlist problems focusing heavily on creative algebra and number theory.
Status: The ultimate barrier. The hardest benchmark in existence. GPT-4 solves 0 percent. DeepSeek models solve roughly 3.4 percent. Use this only to measure Olympiad-level frontier capabilities (cite: 6, 66).

## PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment for a newcomer is evaluating DeepSeek-Prover-V2-7B on the miniF2F-v2s test set using a constrained Monte Carlo tree search / best-first search.

Exact Software and Version:
- Model: deepseek-ai/DeepSeek-Prover-V2-7B (HuggingFace)
- Inference Engine: vLLM or llama.cpp (with DeepSeek's specific prompt template)
- Environment: Lean 4 (version must strictly match the mathlib4 commit specified in the DeepSeek-Prover-V2 requirements).
- Benchmark: roozbeh-yz/miniF2F_v2 (specifically the v2s test split)

Parameters to Set:
- Sampling Temperature: 0.7
- Expansion Budget (Pass at K): 128 independent rollouts per problem (Pass at 128).
- Max New Tokens per rollout: 8192 tokens.
- Context window: 32,000 tokens (essential for the truncate-and-resume strategy).

Replicates and Seeding:
Because this is a pass-at-K metric, you run 128 attempts per problem with varying random seeds. If the Lean 4 kernel accepts the proof in any of the 128 attempts, the problem is marked solved.

Compute Cost:
Running pass at 128 for the 244 problems in the miniF2F-v2s test set using a 7B parameter model requires approximately 48 to 72 GPU hours on a single NVIDIA A100 or H100 80GB, depending on batching efficiency and KV-cache offloading.

Expected Result:
You should observe an accuracy of approximately 73.4 percent to 76 percent on the miniF2F-v2s test set. 
Citation for this number: (cite: 56, 63, 85).

Three Most Common Ways People Get This Wrong:
First, using the original miniF2F (v1) dataset instead of v2s. If you use v1, you will accidentally measure the model's ability to solve excessively simplified or broken statements, completely invalidating the reproduction (cite: 55, 64).
Second, failing to align the exact Lean toolchain version. Lean 4 updates frequently break backward compatibility. If your mathlib version is off by even one month from the model's training cutoff, the tactics generated by the model will result in silent type-checker failures, tanking your success rate to near zero.
Third, restricting the context window. The 7B model relies heavily on its 32K context window to read error messages from the kernel and apply truncate-and-resume logic. Capping the context to 8K to save VRAM breaks the multi-turn refinement process.

## PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to operate at the absolute frontier (AlphaProof level), you will have to build a Test-Time Variant Generator and RL Environment. 

Currently, off-the-shelf tools (like LeanDojo) allow you to pass a state, get a tactic, and step the kernel. What they do not provide is the automated curriculum generation that DeepMind used to reach Silver Medal performance. 

Interface Requirements:
What goes in: A single formal theorem statement in Lean 4 that the model is struggling to prove.
What comes out: A set of 10,000 to 100,000 logically related, slightly easier formal theorem variants (e.g., relaxing constraints, substituting constants for variables, proving lemmas of the main theorem).
The Hard Part: You must write an agent that uses an LLM to rewrite Lean 4 statements, but also automatically verifies that the new statements are actually mathematically valid and non-trivial before adding them to the search space. DeepMind solved this privately using a combination of formalizer networks and AlphaZero-style and-or trees (cite: 71, 72). 
Workload: This is a massive systems engineering effort. It requires building a distributed Lean 4 compilation cluster that can handle millions of sandbox evaluations per hour without memory leaks. 

Several groups (DeepMind, DeepSeek, ByteDance) have rebuilt this test-time variant generation infrastructure privately to push past benchmark walls. Because the math search space is too sparse for simple MCTS to find a reward signal on IMO problems, generating stepping-stone variants at runtime is the only proven way to close the gap. No open-source library currently manages this seamlessly.

## PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The history of this field is littered with methods that looked revolutionary but were ultimately measuring artifacts. 

The Collapse of miniF2F v1:
For three years, the entire field optimized against the miniF2F benchmark. Papers routinely claimed high autoformalization and proving accuracies (up to 97 percent for translation). In late 2025, Ospanov and Yousefzadeh audited the benchmark and found that over half the formal statements did not match the informal English problems. In many cases, the formal statements were mathematically unprovable, or they were stripped of difficulty (e.g., giving the model the answer to a multiple choice question in the theorem statement). When evaluated end-to-end on a corrected pipeline (miniF2F-v2), the accuracy of state-of-the-art systems plummeted to 36 percent. The prior three years of literature on miniF2F v1 was largely measuring overfitting to broken formalizations (cite: 44, 55, 59, 64).

Pure Language Model Premise Selection:
Early attempts to have LLMs predict the required lemmas and premises from a library of hundreds of thousands of theorems directly from memory failed. The context window is too small, and LLM hallucinations in exact variable naming cause the Lean kernel to instantly reject the step. This was explicitly addressed by the "Thor" project, which showed that symbolic "Hammers" (automated theorem provers running in the background) must be integrated to handle premise selection, leaving the LLM to handle high-level logic. Any programme relying purely on an LLM to recall obscure mathlib premises will fail (cite: 25, 26, 28).

Single-Pass Whole Proof Generation:
Having a model look at a theorem and spit out a 50-line proof block in one shot does not work for frontier mathematics. It works for trivial high-school algebra, but fails entirely on undergraduate math. The error compounds at each line, and without intermediate feedback from the kernel, a single syntax error invalidates the remaining computation. This approach was largely abandoned in favor of truncate-and-resume (where the kernel chops off the proof at the first error and asks the model to continue) or interactive step-by-step search (cite: 47, 48).

The Contamination Critique:
A standing methodological critique of the field is data contamination. Open mathematical models are trained on the Pile, ArXiv, and GitHub. This means they have seen the informal natural language proofs for nearly every contest math problem in existence. When they successfully write a Lean proof for an IMO problem, skeptics argue they are not reasoning; they are simply translating a memorized English proof into Lean. This critique has only been partially answered by evaluating models on freshly minted AIME 2025 problems (where DeepSeek still managed to solve some). However, the critique stands unanswered for historical benchmarks like miniF2F, which are now considered completely saturated by contamination (cite: 40, 51).

## PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the saturation of standard benchmarks and the dominance of massive industrial labs in raw pre-training compute, a well-resourced newcomer should not attempt to train a better base model. Instead, you should exploit the fact that search algorithms and test-time compute scaling are still highly unoptimized and mostly proprietary.

Rank 1. Build an Open Test-Time Variant Generation Engine
Experiment: Implement a distributed tree search that, when stuck on a Lean 4 goal, uses an LLM to mutate the goal into 100 simpler sub-theorems, proves those, and uses the resulting value network updates to bootstrap a solution to the main goal (replicating AlphaProof's core loop). 
Feasibility: Feasible now because 7B open-source models (like DeepSeek-Prover-V2-7B) are finally smart enough to serve as the mutator and the prover simultaneously, and hardware for massive parallel inference (vLLM) is mature.
Measurement: Pass rate on PutnamBench or FIMO at pass at 128 compared to standard MCTS. 
Falsification: If the mutated sub-theorems take longer to verify than they save in search depth, the idea is falsified.

Rank 2. Interleave Symbolic Solvers deeply into the Tactic State
Experiment: Rebuild the "Thor" methodology for Lean 4 using modern LLMs. Instead of the LLM guessing algebraic simplifications, train the LLM to write SMT-solver queries (like Z3 or CVC5) in the middle of a Lean proof, parse the SMT output, and convert it back to Lean tactics.
Feasibility: Feasible because code-agents (like Leanstral) can now execute bash commands and Python scripts mid-proof, breaking out of the strict tactic environment.
Measurement: Reduction in token expenditure per closed proof on DeepSeek-ProverBench. 
Falsification: If the overhead of translating Lean state to SMT and back loses information, preventing the kernel from verifying the step.

Rank 3. Automated Curriculum Autoformalization
Experiment: Build an agent that crawls unformalized PDF math textbooks, extracts the theorems in dependency order, autoformalizes them into Lean 4, and trains a prover on them sequentially.
Feasibility: Feasible because multimodal foundation models can now accurately parse complex LaTeX from PDFs, which was impossible three years ago.
Measurement: Number of novel, mathematically sound theorems successfully committed to a clean Lean repository without human intervention.
Falsification: If the autoformalizer hallucinates definitions that mathematically compile but mean nothing (a common failure mode), the curriculum will collapse into nonsense logic.

What will NOT work:
Do not try to build a new static benchmark of historical math Olympiad problems. The data contamination issues are insurmountable; any model trained on the internet will have seen the answers. Furthermore, do not attempt to train a dense transformer to solve proofs in a single forward pass without a search wrapper. The search space of formal mathematics is too brittle, and the exactitude required by the Lean kernel absolutely mandates multi-turn interaction and search.
