# Prompt 50: Machine Discovery

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcwMXlmYXQ3M0F1LWFfdU1QNGEtY29RYxIXMDF5ZmF0NzNBdS1hX3VNUDRhLWNvUWM
**Elapsed:** 304s

---

# FRONTIER PRACTITIONER DOSSIER: MACHINE DISCOVERY

### EXECUTIVE SUMMARY

Machine discovery in mathematics has recently crossed a historical threshold, transitioning from rule-based heuristic search to neuro-symbolic generation and large language model-guided exploration. 

Research suggests that we have entered an era of "proof abundance," where the primary bottleneck is no longer generating valid mathematical constructions, but rather digesting, contextualizing, and verifying them. The foundational approaches of the 1970s, which relied on manually curated rules, have been definitively superseded by hybrid systems that pair the creative intuition of neural networks with the uncompromising rigor of formal symbolic engines. 

Key points for a practitioner entering this field in 2026:
* The original Automated Mathematician method you described is historically foundational but methodologically flawed; its success was largely an artifact of its programming language rather than its heuristic rules.
* The current state of the art relies on neuro-symbolic architectures, such as AlphaGeometry and FunSearch, which search for programs or auxiliary constructions rather than searching directly for solutions.
* Evaluation has shifted entirely to formal theorem-proving environments like Lean and domain-specific languages, utilizing strict benchmarks like miniF2F-v2 and IMO-AG-30.
* A major crisis of reproducibility and misalignment was recently exposed in standard benchmarks, making rigorous validation of evaluation datasets the highest priority for new entrants.
* The most valuable open problem is no longer proof generation, but proof digestion: the automated extraction of reusable mathematical insights from massive, machine-generated proof traces.

***

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Machine discovery in mathematics is the engineering of systems that can autonomously generate novel, verifiable, and interesting mathematical concepts, constructions, or proofs. In 2026, the field operates at the intersection of large language models, formal interactive theorem provers, and evolutionary program search. It has successfully graduated from toy domains to resolving open problems in extremal combinatorics and achieving gold-medalist performance in International Mathematical Olympiad geometry [cite: 1, 2]. The field is highly active, heavily funded, and is currently experiencing a foundational shift in its core philosophy, led by prominent mathematicians such as Terence Tao [cite: 3].

What is SETTLED: It is definitively settled that hybrid neuro-symbolic systems are strictly superior to pure neural or pure symbolic systems for mathematical discovery [cite: 2, 4]. Systems must separate the "proposing" phase, handled by neural models generating code or auxiliary constructions, from the "closing" or "verifying" phase, handled by formal symbolic engines or automated evaluators [cite: 5, 6]. It is also settled that pure autoregressive language models, operating without a formal verification loop, hallucinate too frequently to conduct reliable independent mathematical research [cite: 7].

What is CONTESTED: The nature of the training data required to reach the next frontier is fiercely debated. One side, championed by the creators of AlphaGeometry, argues that pure synthetic data generation via symbolic exploration is sufficient and completely sidesteps the need for human demonstrations [cite: 6]. The other side argues that to reach true research-level abstraction, models must be trained on formalizations of actual human mathematical literature, leading to intense efforts in "autoformalization" [cite: 8]. Additionally, there is active disagreement over whether automated conjecturing systems (which propose theorems without proofs) are still valuable, or if conjecturing must now be tightly coupled with automated proving to be useful [cite: 9].

What is OPEN: The most critical open frontier in 2026 is what Terence Tao defines as "proof digestion" [cite: 3, 10]. The field has accelerated generation and verification far ahead of the human capacity to understand the results. Mathematics has moved from an era of proof scarcity to an era of proof abundance [cite: 10, 11]. We can now generate massive, correct proofs and code-based constructions, but we do not have automated systems capable of simplifying these results, extracting reusable lemmas, or explaining the geometric or algebraic intuition behind them [cite: 3, 11]. 

Correction to your method anchor: Your description of Douglas Lenat's AM (Automated Mathematician) is highly accurate to Lenat's original published claims, but it lacks the field's tacit historical knowledge regarding its validity. You must know that AM is widely considered a flawed experiment. Critics, notably Ritchie and Hanna in 1984, demonstrated that AM's heuristic rules were intertwined with undocumented control flow logic and relied on vague, unexplained procedures rather than a clean algorithmic loop [cite: 12]. Furthermore, Lenat himself later conceded in "Why AM and Eurisko appear to work" that AM's success was largely an artifact of Lisp [cite: 12, 13, 14]. Because Lisp's syntax is so dense and closely mirrors fundamental mathematical logic, randomly mutating short Lisp programs naturally yields structures that human observers interpret as deep mathematics [cite: 13]. AM did not discover concepts through pure heuristic brilliance; it navigated a language space where it was statistically highly probable to bump into fundamental arithmetic [cite: 14, 15]. Consequently, modern practitioners do not build AM-style heuristic agenda loops.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL

Authors: Douglas B. Lenat, John Seely Brown
Year: 1984
Title: Why AM and EURISKO appear to work
Venue: Artificial Intelligence
Identifier: DOI 10.1016/0004-3702(84)90016-X
The authors concede that AM's success was heavily dependent on the syntactic density of Lisp rather than its heuristic rules. A practitioner must read this to understand why raw heuristic search over concepts eventually exhausts itself and why representation languages dictate discovery ceilings [cite: 14].

Authors: G. D. Ritchie, F. K. Hanna
Year: 1984
Title: AM: a case study in AI methodology
Venue: Artificial Intelligence
Identifier: DOI 10.1017/CBO9780511663116.024
The definitive methodological critique of early machine discovery, proving that building impressive-looking programs without clearly stated theoretical content is unproductive [cite: 16]. It establishes the rigorous standard of transparency required in the field today.

Authors: Simon Colton
Year: 2002
Title: Automated Theory Formation in Pure Mathematics
Venue: Springer Distinguished Dissertations
Identifier: DOI 10.1007/978-1-4471-0147-5
Details the HR system, the most significant successor to AM, which formalized the generation of mathematical conjectures using model finding and heuristic production rules [cite: 17]. It defines the baseline for automated conjecturing before the deep learning era.

CURRENT

Authors: Bernardino Romera-Paredes et al.
Year: 2023
Title: Mathematical discoveries from program search with large language models
Venue: Nature
Identifier: DOI 10.1038/s41586-023-06924-6
Introduces FunSearch, proving that LLMs can discover novel, verifiably correct constructions for open mathematical problems (the cap set problem) when their output is treated as executable code and filtered through a strict evaluator [cite: 1, 5]. This paper is the template for modern function-space search.

Authors: Trieu H. Trinh et al.
Year: 2024
Title: Solving olympiad geometry without human demonstrations
Venue: Nature
Identifier: DOI 10.1038/s41586-023-06747-5
Introduces AlphaGeometry, demonstrating that generating 100 million synthetic theorems via symbolic deduction can successfully pretrain a neural language model to supply auxiliary constructions for Olympiad-level geometry [cite: 2, 6]. It defines the modern neuro-symbolic split architecture.

Authors: Kunhao Zheng, Jesse Michael Han, Stanislas Polu
Year: 2021
Title: MiniF2F: a cross-system benchmark for formal Olympiad-level mathematics
Venue: ICLR
Identifier: arXiv:2109.00110
Introduces the original cross-system benchmark that unified the evaluation of neural theorem provers across Lean, Metamath, and Isabelle [cite: 18]. Essential reading for understanding how the community standardized performance metrics.

Authors: Roozbeh Ospanov et al.
Year: 2025
Title: miniF2F-Lean Revisited: Reviewing Limitations and Charting a Path Forward
Venue: NeurIPS
Identifier: arXiv:2511.03108
Exposes that over half of the original miniF2F benchmark had misaligned formal and informal statements, presenting the corrected miniF2F-v2 [cite: 19, 20]. A practitioner must read this to avoid training on contaminated or unprovable baseline data.

Authors: Terence Tao
Year: 2026
Title: Mathematics in the age of AI
Venue: Proceedings of the ICM 2026
Identifier: IDENTIFIER UNKNOWN
Summarizes the transition from proof scarcity to proof abundance, outlining the impedance mismatch between proof generation and proof digestion [cite: 3, 11]. This is the best available survey of the field's current philosophy and strategic direction.

PART 3. SOFTWARE I CAN ACTUALLY RUN

Name: AM (Automated Mathematician)
URL: https://github.com/white-flame/am
Implementation Language: Interlisp
Licence: Public Domain
Approximate Year of Most Recent Activity: 2023
Maturity Verdict: DORMANT
Experiment it can run: You can technically run Lenat's original 1977 code, recovered from the SAILDART archive, to trace its concept generation loop.
Known limitations or gotchas: It requires the Medley Interlisp emulator to run [cite: 21, 22]. It is completely detached from modern toolchains and is useful only for software archaeology. Do not attempt to build a modern research program on top of this codebase.

Name: Eurisko
URL: https://github.com/white-flame/eurisko
Implementation Language: Interlisp
Licence: Public Domain
Approximate Year of Most Recent Activity: 2024
Maturity Verdict: DORMANT
Experiment it can run: Lenat's successor to AM, capable of modifying its own heuristics. User "seveno4" successfully ran it in Medley Interlisp with minimal changes [cite: 22, 23].
Known limitations or gotchas: Suffers from the exact same obsolescence as AM. Famous, historically legendary, but effectively dead for modern research purposes.

Name: FunSearch
URL: https://github.com/google-deepmind/funsearch
Implementation Language: Python
Licence: Apache License 2.0
Approximate Year of Most Recent Activity: 2024
Maturity Verdict: MAINTAINED
Experiment it can run: Replicates the evolutionary search for new mathematical constructions (such as cap sets and bin packing heuristics) using an LLM to mutate Python programs [cite: 5].
Known limitations or gotchas: The open-source repository contains only the single-threaded implementation of the pipeline [cite: 5]. It explicitly does not include the language models, the execution sandbox, or the distributed infrastructure used in the original Nature paper experiments. You must bring your own LLM API and containerized execution environment.

Name: AlphaGeometry
URL: https://github.com/google-deepmind/alphageometry
Implementation Language: Python and C++
Licence: Apache License 2.0
Approximate Year of Most Recent Activity: 2024
Maturity Verdict: MAINTAINED
Experiment it can run: Solves Olympiad-level geometry problems by combining a neural language model (for auxiliary constructions) with a symbolic deduction engine (Deductive Database and Algebraic Rules) [cite: 24].
Known limitations or gotchas: Requires significant compute to run the neural model optimally. However, the repository contains the pure symbolic engine (DD and AR) which can be run on a CPU and is highly performant on its own.

Name: FERMAT
URL: https://github.com/trishullab/Fermat
Implementation Language: Python
Licence: UNCONFIRMED
Approximate Year of Most Recent Activity: 2025
Maturity Verdict: MAINTAINED
Experiment it can run: Provides a reinforcement learning framework for automated theory formation, updating the concepts of HR into a modern Markov Decision Process utilizing a formal domain specific language [cite: 25].
Known limitations or gotchas: Currently restricted to explicit symbolic steps and specific mathematical knowledge graph representations; lacks the broad adaptability of natural language systems.

Name: miniF2F-v2
URL: https://github.com/roozbeh-yz/miniF2F_v2
Implementation Language: Lean 4
Licence: Apache License 2.0
Approximate Year of Most Recent Activity: 2025
Maturity Verdict: MAINTAINED
Experiment it can run: Evaluates the end-to-end performance of an automated theorem prover on Olympiad-level mathematics, ensuring exact alignment between informal natural language statements and formal Lean code [cite: 26].
Known limitations or gotchas: Ensure you are using v2. The original v1 repository (openai/miniF2F) contains over 50 percent misaligned problems and unprovable statements [cite: 20].

PART 4. DATA AND BENCHMARKS

Name: miniF2F-v2 (Includes v2c and v2s variants)
Access Route: https://github.com/roozbeh-yz/miniF2F_v2 or https://huggingface.co/datasets/roozbeh-yz/miniF2F_v2
Approximate Size: 488 problem statements (test and validation splits)
Licence or Access Restriction: Apache License 2.0
What it is used to measure: The standard for measuring end-to-end theorem proving accuracy from natural language to formal Lean code [cite: 26].
Contamination or Overfitting Notes: The original version (miniF2F-v1) is famously contaminated. It contained sixteen entirely unprovable statements and massive discrepancies where the formal code simplified the informal prompt [cite: 8]. This caused severe measurement artifacts where models appeared to fail at reasoning but were actually failing at translation. Always use v2c (competition level, exact match) or v2s (simplified level, prompt includes solution constraints).

Name: IMO-AG-30
Access Route: Provided within the AlphaGeometry repository (https://github.com/google-deepmind/alphageometry)
Approximate Size: 30 Euclidean geometry problems
Licence or Access Restriction: Apache License 2.0
What it is used to measure: The absolute frontier of automated geometric reasoning [cite: 27]. Compares solver performance directly against human International Mathematical Olympiad medalists [cite: 28].
Contamination or Overfitting Notes: Treated as highly authoritative. No training or tuning on these specific items is permitted. It is known to be saturated by the absolute best methods (AlphaGeometry and combined symbolic methods reach 25 to 27 out of 30) [cite: 28], but remains a harsh filter for standard models which often score 0.

Name: FIMO (Formalized IMO Shortlist)
Access Route: IDENTIFIER UNKNOWN
Approximate Size: 148 problems
Licence or Access Restriction: UNCONFIRMED
What it is used to measure: Advanced algebra and number theory capabilities [cite: 29].
Contamination or Overfitting Notes: Extremely difficult. DeepSeek-Prover solved only roughly 3.4 percent, while GPT-4 solved zero [cite: 29]. This benchmark is strictly for models that have saturated miniF2F.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment in this field today is not a neural network training run; it is the replication of the pure symbolic baseline on the IMO-AG-30 benchmark. Proving that decades-old algebraic and synthetic methods can rival modern neural networks establishes the exact baseline a newcomer must understand before spending GPU hours on language models [cite: 24, 28].

Exact Software and Version: 
You need the AlphaGeometry codebase (for the DD and AR engines) and JGEX (Java Geometry Expert) for Wu's method, as benchmarked by the 2024 studies reviewing AlphaGeometry's baselines [cite: 28]. 

Exact Dataset: 
IMO-AG-30 (the 30 classical geometry problems formalized in the AlphaGeometry domain specific language) [cite: 24].

Parameters to Set:
Time limit: Exactly 5 minutes of compute time per problem [cite: 27, 28].
Execution environment: Single-threaded CPU-only execution [cite: 28].
Hardware: Standard modern laptop CPU.

Compute Cost: 
Less than 3 CPU hours total (30 problems at a maximum of 5 minutes each). No GPUs required.

Expected Result:
When combining Deductive Databases, Angle/Ratio chasing, and Wu's Method, the symbolic engine will successfully solve 21 out of 30 problems [cite: 28, 30]. This number comes directly from the 2024 re-evaluations of AlphaGeometry's baselines, demonstrating that this classic method solves just 4 fewer problems than the full 100M-parameter AlphaGeometry model, effectively rivaling an IMO Silver Medalist purely through symbolic computation [cite: 28].

Three Most Common Ways People Get This Wrong:
1. Misunderstanding the domain specific language translation: The hardest part is ensuring the problem is correctly translated into the specific algebraic equations required by Wu's method. If the translation is wrong, the solver fails instantly.
2. Ignoring non-degeneracy conditions: Wu's method automatically generates conditions (like points not being collinear). Failing to handle or map these back to the synthetic proof state causes the engine to stall or reject valid configurations.
3. Using the wrong timeout limits: Neural models are often given 90 minutes or run on vast parallel beams. The symbolic baseline derives its legitimacy from the strict 5-minute, single-thread constraint. Granting it more time does not yield more results, as algebraic explosion occurs rapidly if a proof path is not found early.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to build a truly autonomous research agent, you will hit two massive tooling gaps that multiple labs are currently trying to build privately.

1. The Digestion and Extraction Engine
What goes in: A massive, machine-generated formal proof trace (such as the output from AlphaGeometry or a brute-force Lean verification).
What comes out: A minimal set of human-readable, reusable lemmas, scored by mathematical "interestingness," accompanied by a natural language exposition of the intuition.
The hard part: AI can generate 1000-step formal proofs, but humans cannot read them. The system must learn to compress a proof tree into intermediate conceptual milestones. This is the exact "impedance mismatch" Tao identified [cite: 3].
Work required: High. It requires building a reinforcement learning environment where the reward signal is based on the generalizability and brevity of extracted sub-theorems across multiple distinct proof branches.

2. A Bidirectional Semantic Autoformalizer
What goes in: A raw LaTeX PDF of a newly published mathematics paper.
What comes out: A fully formalized Lean 4 project containing the definitions, theorem statements, and proof outlines, with zero semantic loss.
The hard part: Translating high-school competition math (like miniF2F) is largely solved, but translating research-level mathematics fails because models hallucinate definitions or map concepts to the wrong foundational libraries [cite: 9]. 
Work required: Extreme. Several groups are trying to build this using retrieval-augmented generation over Lean's Mathlib, combined with cyclic back-translation to verify fidelity [cite: 26, 31]. You would have to build a system that iteratively compiles Lean code, reads the error trace, and adjusts the formalization until the types align perfectly with the informal text.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The history of machine discovery is defined by systems that looked intelligent but were secretly riding on artifacts of their environment or evaluation metrics.

The Artifact of Representation (The Critique of AM)
Douglas Lenat's Automated Mathematician is the most famous corrected result in the field. Lenat originally claimed AM discovered concepts using heuristic rules [cite: 12]. Later, Ritchie and Hanna published a standing critique that the system's control flow was deeply conflated with its heuristics, making it impossible to determine why it made decisions [cite: 16]. Lenat eventually admitted that the success was heavily dependent on Lisp [cite: 14]. Because Lisp uses nested lists (trees) that perfectly map to foundational logic, randomly mutating Lisp code has a high probability of generating valid math. The system did not possess deep heuristic intelligence; it was exploring a remarkably dense, forgiving conceptual space [cite: 14, 15]. When Lenat tried to adapt the system to other domains (Eurisko), it quickly ran out of steam and required constant manual curation to prevent it from generating useless meta-rules [cite: 14].

The miniF2F-v1 Contamination
For several years, researchers trained LLMs to autoformalize and prove theorems using the miniF2F benchmark. Papers reported a bizarre ceiling where accuracy would halt around 35 to 40 percent for end-to-end pipelines [cite: 19]. It was recently exposed that the benchmark itself was severely flawed. Over 50 percent of the formal statements were misaligned with the informal prompts. Sixteen problems were strictly unprovable due to missing hypotheses in the formal translation [cite: 8]. Methods that looked like they were failing at logic were actually measuring the benchmark's translation errors. This was corrected in late 2025 with miniF2F-v2, which saw baseline accuracies immediately jump to 70 percent [cite: 19, 20].

Autoregressive Hallucinations in Pure Math
Trying to use raw, standalone Large Language Models (like GPT-4) to discover new mathematics or generate full proofs without a formal verification loop is a failed programme. DeepMind explicitly noted that on the IMO-AG-30 benchmark, a standalone LLM scores exactly 0 percent, hallucinating syntax and semantic relationships constantly [cite: 32]. The critique stands that LLMs do not "reason"; they recognize patterns. This critique is answered by neuro-symbolic wrappers (like FunSearch and AlphaGeometry), which use the LLM solely as a creative generator (proposer) and rely entirely on a rigid evaluator (Python execution or Deductive Databases) to filter out the massive volume of incorrect ideas [cite: 5, 33].

Terence Tao's Proof Indigestion Critique
The standing methodological critique of the field today is that generating proofs without exposition is scientifically useless. Tao argues that simply verifying a trillion-step combinatorial proof does not advance mathematics if no human understands the underlying mechanism [cite: 34]. If an AI generates a correct proof but cannot give an expert-level explanation of the intermediate lemmas, Tao argues the result should not be published or accepted by the community [cite: 34]. This critique remains unanswered by the current generation of tools.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the computational leverage available today and the identified gaps in the field, a well-resourced newcomer should bypass Olympiad proof generation and aim directly at proof digestion and autonomous formalization.

Rank 1: The Lemma Extraction Experiment
Feasibility: High. AlphaGeometry and Lean 4 provide massive, completely accurate proof traces that are currently discarded once the "QED" is reached.
The Experiment: Train an offline reinforcement learning model to compress long, machine-generated formal proofs into the shortest possible sequence of intermediate lemmas that a secondary, smaller prover can easily bridge. 
What it measures: The compressibility and modularity of AI-generated proofs. 
Falsification: The idea is falsified if the extracted lemmas are highly specific to the individual proof and fail to increase the success rate of the prover when added to a global tactic library for unseen problems.

Rank 2: Interactive Back-Translation for Autoformalization
Feasibility: Moderate, requires heavy engineering of the Lean 4 compiler feedback loop.
The Experiment: Feed a pipeline informal math statements from the arXiv. Have an LLM generate a Lean formalization. Compile the Lean code. If it fails, feed the specific type-mismatch error back to the LLM to correct the formalization. Once it compiles, use a secondary LLM to translate the Lean code back into natural language.
What it measures: The semantic drift between the original informal statement and the back-translated statement, measured by human expert grading.
Falsification: The idea is falsified if compiler-error feedback causes the LLM to continuously simplify the theorem until it compiles trivially, destroying the original mathematical meaning (a known failure mode in early miniF2F iterations).

Rank 3: Modernizing Automated Conjecturing (The New HR)
Feasibility: Moderate. 
The Experiment: Rebuild Simon Colton's HR system, but replace the rigid production rules with an LLM prompted to generate new algebraic invariants. Use QuickSpec or a similar model-finding tool to aggressively filter out false conjectures by generating counter-examples.
What it measures: The yield of true, novel conjectures that survive counter-example filtering but cannot be trivially proven by existing SMT solvers.
Falsification: The idea is falsified if the system overwhelmingly generates tautologies or mathematically trivial bounds (the exact problem that plagued the historical Graffiti and HR systems).

What will NOT work:
Training a larger, purely autoregressive language model on more raw mathematical text in hopes that it will naturally learn to prove novel research theorems without a formal environment. This will fail because the supply of high-quality, step-by-step informal proofs in the training data is saturated, and the complexity of research mathematics requires infinite-branching exploration that pure text generation cannot sustain without a rigid, external state-tracking engine to catch inevitable logical drifts.

**Sources:**
1. [deepmind.google](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8jZOPC4VJHKhv6gN08KR9FHJr2MFSTcvP2SldX4Z137fHDg34iaV8vl0b7QfEnmTmkdW7ykJmdDF_eogqFgZIRpzTX7ut8kpNyFl-0OTvrufNK7fVct8YubWSqVMxymYyOs9hthTtQdcvy-f6a7niNX2QhKba4miOgXGL-fZ_JHFHOrQ4rhnq1-Jmg_KcA2iOLzwW9CMDEMvyiIrm1nCFf8686OfK8zET)
2. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAE-sG5BwECvOWXUS4LJRTJwo9ml05wkliCy06rXBmq1kXx3Bqy5mBiSRqoVu8ibZucjKinZqASwfaMxL-nr-lMtAeJmFtxwYr1H3-n8tAxNuSzEUJF_MHjEIbSXXG)
3. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF93BgviXEyrhsxXrIVuP0H7oJ8nMQjS1AH8vV0f11L2aGflHzfJQ224eMTbIhKt912CcK1bq9tRV5kmoLqZ5ws8aa66FaHP2ks5KtZ29yfnydaZyCRUkk6xjqtJzqXO99Ik0r5)
4. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFB1SsriedSvmVrlQikyTml74ALxNX9lZn5QlTbFdZ2zKqzI6ieGR8VcPOWrm7UL8Tu6kovn6Y329LKFKl_Hqc0Y6s0iM4OKlpwqt2ZI83zaoeUO57cc8l5BYRoEPJ7tu0iKoCJgzbCAXwTpdhHy41xWn9t5ZoYiuLrk_OSagfxKNhknAQWaXSucZ0-xDN8pi4vr2o=)
5. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1bNMKFj7GZmjbedrHaRNQv_4WZWDDCuyLdBvU9Vgq9R-bmhiYOo8DfklvpVapXfJwOcAumuuirkCCwcEBWThBlww4xb5qbkMYpERIDUPRJWY3VD9mNgdT_urpj-0=)
6. [qobilidop.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE688QnnqAX_fo2HAzhh1NafT3IQnwKXehJKgiYjWhpnjtEB7nng8sx3wAveFrmkMPHsRTmBrfs_zvhctvdF0CdAaQfLwOsa0LcVZN7r2KfqmH5XjAZxIOIn8Tufzm9eUPyhYKK2QDpQhFNlKI=)
7. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLu6Bu346Zp3q1EQcRcRq6bysPHcct_q8pGn9AJ3b8Z2iaBts3sZB5IhlOjzLxcmRayGjtZBMwEn5zwFQDbSi-OKAJSvCCWJxgqlK5irF5mDpiYn5PXprKLqnjZkulzQ==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyXKnYCC4PHdOjX13IH_hNSvBGng__Is-OXr5_aCo35VnGNFewq5vwa2K-zOsnHe4hv7tGJFNDL4gKSSoKWQP82WCwf78ue2LprJeoBO7k2fKPi8pzCOiBxg==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeApAwf2EJlcISjV38tDM-1zqnP0cz59nqhbbss4uu0MR4I7TusWfGY8kdmGlVXCjh_U5YaKd7DmWnMrqUoD89OmrV2T4CKo4yV8MmZyjqx5fEOIOHd2qkGg==)
10. [mathstodon.xyz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhl9bqKFWl1qQyPvivDl39BDr0c8-JaHsz6GtDo0v5UOIL4mhwN52iR7Y0Mm0rMAnCdx7hLLzQfxdCdQPKIM0SFqgT1vxSgcg2vyz6_2uOxvggYyVZ2a6erMGWTm_R7ytISbDo)
11. [4m4.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFW2gn-i6VvFS_yMvAycPckzX6wqn5wIaPM5TNEUXjOcQWtID3mwCRd2ctwm5i0iQ3UB_KtDgz3kcxDu8jK_o8bCdQmuVhPjKlwNzo55sn-lmuaYjX5u0UFFmpQgs_UaYbrFfc4LAaJDThm-9Uil0--m3-6skEYCiEyehps8mq)
12. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSIrrZ5IaMpXwQ9p83jKR5v8utWU_nea77HuwscN9ulOeqbQgH5zqMUrTq_6n7UG1QWQ_W9OEul4RGUGd2sHxS7D6eArb4KqiZXP4pzrYFMXVDIZwElfkyDKIJhcWaRXTJpFAcqzIpjEORpQ==)
13. [academickids.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUJ0I5GwZWHHG_Fsk0zxa3Pyk76ybGGB_GGePL-z4srdVFPbdfgVGb1KHNfa2x7dr71zyseTfP2d5SbcOuERKm7MEI-2UpAJbf4IAcbEJTFWxGRocR9aFfSRdTXVuNqzx0biYxNvYcKgmIY9Mtu9Cbd1NHDe4tj3CFPO7TbA==)
14. [yuxi.ml](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFb5p78CwYdbywwh2IuaPv0PgG5819exQLWR4de_L5IbIUeKjTTGd0cUJw-bUjIlDE9Thi_cIbbXI8QGkvfM2SSeVUYWw-uZKbDMAY-SNzPG8CmC2K_3fg=)
15. [oregonstate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLFpgLmoMhXSC35lRKAyWOekoKGkUGlLdMTWVxxAV8tAmMfnpAyy42PP3zrHOMrAtXiqP37KjnMtSRb7WZBJQnv9WCqRGHHAmssvByZ8P2KpxsCRMmpDhNnBGLfbYEe9GJ9Z6Qnh0JnQPEGKs=)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETl0sKDVOzzWzPw3bgJy57rXnL5cb61UzGrH1CSsFbrAnmNaAUge7kYFWriJfrWYaanTLViOiZLXFgVBVEY_ZfsTZ1eo96HDt-Kdri3CSflO7caVrwKFHL_lCLtXstzdI9DBghQjjA30Ui1cYKmW-unyuByBoQU3ZN59VEs9evYV9rSet21r2EnGrbIEcosObRZmkp7gYy1Bsn0spc7AGvmrLvF5fdRorC96vxf3WrMjDkdj5RCYH6oIYhsONhJdb83ItFKOznIWvsSQB6--aMJgmw29NpGBqvXHenFb5Z70lSFQ0L47Qsk1IHybb8z7E1MWTrcPJ9hShmGekuIhD8LTAe0Jjv99uUWao1qH6UUOQR)
17. [chalmers.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERUC6KcgqJXDmO6UXTrh9sfMZWqq9Y9xdHEopdo6QSMd9DdorH1yUlbyw3bBl31zCw9_c7b5M5TMVk7kST0RRF0ErD6kRIXQVxlCAmP29Q2YlIuH2bAFoRIR44yZGGnpWc68k9pj4yC2s8nqSqBLoJev3s5O-JLn0wJQoTw8IcBb9iDhvieT0=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0Mt8otwDOw6f8wc_Cn7u452EPLL528qWOCoAME-TIFyuvHWzaNvkgusZr1DAKWORsgxHLPlVo9i4SWUaWbdH2e_XTih3UWFqGTa9FV07c7o6XojegpQ==)
19. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9dH8uFOD-MwonmTM5dLo3jtmvlAyd_6Bmem_SyoJxndk6k6TIBkXPNrZbXYduT0bKT2jNBuhnCn_d3LiF5xFGKUbsXnPyFaxlgEMouZZFC21sqJjWw-MMs2CJxi7b)
20. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWyuqNWscvIlvoXieO6SjQlX4dXZ6AjijfXA8Ojtk3jQGmx3o-R4zVLzukvW6x0KKGbEj7pp-ycMk-qidF-_sscZbh9JWRJd1tjqenLJdP1hZBp6aDWn7YcC7jhjcIR2UyhrwJRRXEX8ueUbcHN3NnhuIjPZKUzwWfUWFtR8yqn6dW2Nj1GTRVkae7MDeBQhM=)
21. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5jR1tZg-Oh8FsNwW9LSoew8H5r5KgLpwqStri-cyDYpKB1rUGzkEeULL-5oT8rlseZYrwcyFF_zyvv8HtfUHeu6PnLoSK-oDw9dr-lgapVg8qCqLpAWYW)
22. [white-flame.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiynA3KO7zif3OI6pivtzQWEeoMjR3CvqLDES0QBnC0jv-8ooPCQm0Amc6kyhxHCeid7YNME5BrOKNG3i2HLMrno8iyQSXHnBihfHcMzDoqIv2IM6O7Sd10BiH0pw=)
23. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGt5ZzOxPaIi_5pFvR8x-Y5HQTpu8XpZ03oaTpLRudUvtrO8XHeyafku8j6J8TSvqcIFB3B8vlCMKHnRmoyiryhuW9ulpycnVF7g4-0zkrGV7qPEWcHg7JdHpOHQGvAHwqkMVZ7yEVKGg6tc9YkiCshunpeQ75gqm8RVQZXam5n0Zc5qjVdI8lR29GNyrjmv461SVQIjVVLjw==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEP0TUZvfnK4rDOThLJOPeApTLokbwRX7Jlyg8xFDH50kQXw6TKrBqmmMgxOORFqwegCrIlErGPp3FEEba1EKvmu9YLVRibOQiumZ0WLGXAplLFfz_5qPvc-w==)
25. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETAYrH9H32a2HJ95Xh2hcpSeSzIsbWPIMer8QTaCbZylzIbiRwaalQqAbcBby0Q0LV-SoIEp-7WJx57nHL1azVqdLFGSX0_13XOgpCYYlcppMOGMiHVxnnOfkd_n1cO2ZJ73Y=)
26. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9Cej1SOv97D8FAd4Dw0hCLd0_Lvwe-y6LCvL4x0N_qu_pbBWVkImD9a-Vs1vANXQvDOaeQvFT0JE06muk3wBUray2ROoRXqmA_LNjfnND5Fj8jK75EaFswwFEL4IM)
27. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnLYiSG68ODs9iFb7pgB4-D_MiO_U2XHgo1Tm0SFvfdHLi5hBjl7jcJX6ugM39LEQDNAP8UZAu5RgZ5VaF_NvSyt7JGmXnomMKDfMz18LZd2z7lyCWiBNN9fIHIsHvkjN2x7bCLn-CrFsF0w==)
28. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlF0Tj2ZEuWD_l90DVzabcOvJMoCNavtuUqp9sneLQdGKAmXo6XS-upkGRfJbhwEUF8fK_LaxU5rvTekmuTBJqyPHLiFoU6tlsTDUz27_5m9VtDedn4FxJQHddUdt8)
29. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6F2h_4PPyVsSll8DX4hPuG2D0X918S4tzvHD2dS8xwVcCYxauSZ5_FsaG4Nnmf4DwkuNN9D11Asnw11IrwNTCIYF_vDNiOPNL5as5rLbLLvch8xVGegGSkuL1-3316D3pG2HJGANlro0vEK77FyFT8CeI8U4=)
30. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAZcfDTvh9ha7EnVWBX-dR12QsbKtMSpGhdfH0SaPDVorkghL9KeaUfRy89vcrXUG589zlndiqGaToJZvFcG5A8Mm5qHUnNyy6Uq4qoZoe6XYZSB7X1ad7DWfF)
31. [aitp-conference.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvrM3ic61S1Oo6jVJKPD6RygnqUAA6EsCu_Qj3wZMFaCyfWb6BEcgvNJDtaOQ0NCxfsv78TFu02FV4UlPx5jwQnr2KjSew-gEC8VFLv0OVUL1hfHS9jB3yoOECswmuXQHhxiXoyUzXMuFjV9g=)
32. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETCjBuRb3gezUJJAO96-TKZ3JnFf3gmOXCNaEbLAGcHZZUzEYag5ur2Q-Gb2KfJ8SYjwVN_AT6pKFYwVs2eQQwRubAMM-rzMcJJMQEE3F-klhSZYPSaCGjm7C96NtCiBvdl5OlC5iHQlr9O4lZN7U2hEx7CsclSFUz-pwDBw201So37sqEjMlmuf6MNYq9oypFyyk=)
33. [deepmind.google](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdltOXzsFKgO3hIFPf0K9VTRpGh2VPVZLJLH5a3VTYiImWk3ejDd60bB1rDSWqWyvv-1e_S_BTH8yPfV3i5UetOQhRh--5NfqF8NlmMpYazaz13v8woINB7l4Pp6n6ZwJ7ATY3AI1FNkTJ9GDwsoBsiLs8adxMfztAnIMGogzYlCCv-L_MCPfzt3E=)
34. [mindoxai.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGG1oSynwWxCUhgG11GAlEKMOeYTY5seSlb8nuxalfmZqurZ6Pvl3qYE7Lk1o3ERuyMnZUNdnhgcdC9blHGd4qWoTw0x3CR8ATh84zWJbA-OUXh1piIBKsdU8P-4VPydlE28bPaQrs-W8Yd-Yh5FYrGBSe20yqEq6UUAq1QLM4WuwfZ_lUHAaYWy-w=)

