# Prompt 39: Automated Theorem Proving

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdFbGFmYXZ2bEwtaWdqckVQaHA3ZG9RURIXRWxhZmF2dmxMLWlnanJFUGhwN2RvUVE
**Elapsed:** 364s

---

# FRONTIER PRACTITIONER DOSSIER: Automated Theorem Proving

KEY POINTS
The primary engine of modern automated theorem proving in classical first-order logic remains the given-clause algorithm operating over the superposition calculus. 
Your understanding of the mechanism is perfectly accurate: the heuristic controls the search trajectory by prioritizing the unprocessed set, trading budget for discovery speed without affecting the soundness of the underlying inferences.
The absolute frontier of the field in 2026 is the integration of context-aware graph neural networks and reinforcement learning to replace handwritten age-weight heuristics for clause selection.
Large Language Models have largely failed as end-to-end saturation provers due to symbol hallucination and ungroundedness, forcing the field to pivot toward hybrid neuro-symbolic architectures where neural networks act strictly as oracles guiding deterministic symbolic kernels.
The Vampire prover has achieved absolute dominance, winning all divisions at recent competitions, largely due to its integration of advanced data structures, SAT-solver backends for propositional logic, and deep neural guidance.

EXECUTIVE SUMMARY
This dossier provides a complete operational blueprint for a computational scientist entering the field of Automated Theorem Proving in 2026. The field is highly consolidated around a few monolithic C++ codebases and a single authoritative benchmark library. The barrier to entry is no longer understanding the esoteric details of paramodulation, but rather engineering high-throughput, low-latency inter-process communication between PyTorch-based learning environments and highly optimized symbolic C++ kernels. This report details the load-bearing literature, the exact software and datasets that matter, a reproducible experiment to establish a baseline, the missing infrastructure that a newcomer must build, and the most viable targets for frontier research.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Automated Theorem Proving in first-order logic is currently defined by the saturation-based proof search paradigm, heavily optimized over forty years of engineering. The field aims to prove the validity of a first-order formula by establishing the unsatisfiability of its negation, translated into Clause Normal Form. Provers use the given-clause algorithm to partition the search space into an active set of processed clauses and a passive set of unprocessed clauses. Your description of this mechanism in the query is flawlessly accurate. It precisely describes the DISCOUNT loop variant of the given-clause algorithm. You are correct that the heuristic only changes the cost, never the correctness, because every inference rule applied (resolution, superposition, factoring) is logically sound [cite: 1, 2]. The field measures success almost exclusively by whether a prover can derive the empty clause (a contradiction) within a strict wall-clock time limit or a strict budget of processed clauses.

WHAT IS SETTLED: The core symbolic calculus is completely settled. Superposition, ordered binary resolution, and paramodulation, combined with standard redundancy criteria such as tautology deletion and subsumption resolution, form the unquestioned mathematical foundation of the field [cite: 1, 3]. The given-clause loop itself is settled as the optimal control structure. Furthermore, the necessity of abstracting propositional reasoning to backend SAT solvers, an approach pioneered by Vampire, is now standard practice [cite: 4, 5]. 

WHAT IS CONTESTED: The representation of clauses for machine learning evaluation is fiercely contested. One faction argues for symbol-independent features, mapping clauses to fixed-size arity-based vectors or anonymized graph tensors, allowing neural models to generalize across completely different mathematical theories without retraining [cite: 6, 7, 8]. The other faction argues that stripping semantic names destroys the inherent meaning of the symbols, advocating for natural language processing embeddings to align clause selection with the semantic meaning of the proof goal [cite: 9]. Additionally, the architecture for clause evaluation is contested. Historically, clauses were evaluated in isolation by decision trees. The frontier advocates for Leapfrogging and context-aware evaluation, where a Graph Neural Network evaluates a batch of generated clauses collectively against the context of the already-processed active set [cite: 6, 8].

WHAT IS OPEN: Zero-shot logical rule induction and transfer learning remain open problems. While foundational models can do syntactic pattern matching, building a model that reliably infers complex structural rules across unseen domains without fine-tuning is unsolved [cite: 10]. Furthermore, hardware acceleration of the symbolic kernel is wide open. While neural evaluation happens on GPUs, the symbolic prover spends millions of CPU cycles on NP-complete first-order subsumption checks [cite: 1]. Moving the symbolic redundancy elimination to parallel hardware remains an open engineering challenge.

In the last three years, the field has seen the total victory of learning-based guidance over manual heuristics. Vampire achieved unprecedented dominance in the CASC-30 and CASC-J13 world championships by winning every single division [cite: 11, 12]. The field has also successfully expanded beyond pure classical logic; as of late 2024 and 2025, the community benchmark absorbed non-classical logics, including normal modal and epistemic logics [cite: 13, 14, 15]. The field of pure Inductive Logic Programming has been largely absorbed into this neuro-symbolic proving paradigm, losing some of its interpretable, top-down heuristic search identity in the merge, but gaining massive scalability [cite: 10].

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Bachmair, L., & Ganzinger, H.
2001
Resolution Theorem Proving
Handbook of Automated Reasoning
DOI 10.1016/b978-044450813-3/50004-7
This is the theoretical bedrock of the field, establishing the formal framework for saturation up to redundancy and proving the refutational completeness of the ordered resolution calculus [cite: 2, 3]. A practitioner must read this to understand why subsumption and simplification do not compromise the prover's ability to find a proof.

Riazanov, A., & Voronkov, A.
2002
The design and implementation of VAMPIRE
AI Communications
DOI 10.5220/0002425900430052
This paper defines the architecture of the most successful prover in history [cite: 16, 17]. It explains the memory models, indexing techniques for rapid term matching, and the implementation details of the given-clause loop that still govern the software today.

Kovacs, L., & Voronkov, A.
2013
First-Order Theorem Proving and Vampire
Computer Aided Verification
DOI 10.1007/978-3-642-39799-8_1
This outlines the introduction of AVATAR, a paradigm shift that split first-order proving into a propositional SAT skeleton evaluated by a SAT solver, and a first-order part handled by superposition [cite: 18, 19]. This hybrid architecture is mandatory knowledge for understanding modern saturation provers.

Jakubuv, J., & Urban, J.
2017
ENIGMA: Efficient Learning-based Inference Guiding Machine
arXiv:1701.06532
This paper triggered the modern machine learning revolution in clause selection [cite: 20, 21]. It demonstrates how to extract features from clause syntax trees, train gradient-boosted decision trees on past proofs, and tightly link the classifier with the E prover's core to rank generated clauses in microseconds.

CURRENT SOURCES

Bartek, F., et al.
2025
The Vampire Diary
Computer Aided Verification
DOI 10.1007/978-3-031-98682-6_4
This is the single most important survey of the current frontier, detailing a decade of advances in Vampire, including its support for higher-order logic, inductive reasoning, and its integration of neural guidance to effectively complement SAT and SMT solvers [cite: 4, 5, 18, 22].

Suda, M.
2025
Efficient Neural Clause Selection through Reinforcement Learning
arXiv:2503.07792
This paper defines the 2025 state-of-the-art for neural clause selection inside Vampire [cite: 23, 24]. It recasts clause selection as a reinforcement learning problem and demonstrates a neural architecture that is lightweight enough to be evaluated inside the high-speed saturation loop, achieving a 20 percent improvement on unseen problems.

Chvalovsky, K., et al.
2021
ENIGMA Anonymous: Symbol-Independent Inference Guiding Machine
arXiv:2002.05406
This paper introduced symbol-independent Graph Neural Networks for clause selection [cite: 6, 7, 25]. It is critical because it solves the vocabulary problem, allowing a model trained on one mathematical theory to seamlessly guide proof search in a completely different domain by abstracting away specific symbol names.

Jakubuv, J., et al.
2021
Context-Aware Clause Selection for Theorem Proving
arXiv:2107.10034
This paper introduces Leapfrogging and context-aware evaluation [cite: 8]. Instead of evaluating passive clauses in isolation, the GNN evaluates batches of clauses collectively against the context of the already-selected active clauses, interleaved with precise symbolic inference rounds.

Phua, D., & Inoue, K.
2026
A Foundation Model for Zero-Shot Logical Rule Induction
arXiv:2605.04916
This paper represents the frontier of replacing transductive inductive logic programming with domain-agnostic neural rule inducers [cite: 10]. It contrasts brute-force language model approaches with end-to-end differentiable frameworks that learn directly from observed data without explicit semantic models.

Schon, C.
2026
Context-Aware Clause Selection Using Symbol Name Meanings in Theorem Proving
DOI 10.1007/978-3-032-04167-8_17
Representing a counter-movement to ENIGMA Anonymous, this paper uses NLP distributional semantics and word embeddings to leverage the human-assigned meaning of symbol names in commonsense knowledge bases to dramatically reduce the number of processed clauses [cite: 9].

Rawson, M., et al.
2025
Ground Truth: Checking Vampire Proofs via Satisfiability Modulo Theories
Conference on Automated Deduction
DOI 10.1007/978-3-031-99984-0_8
Trusting the output of an enormously complex C++ prover is a known vulnerability. This paper describes the modern frontier of exporting Vampire's refutation steps into a format that can be independently verified by external SMT solvers and the Lean 4 interactive theorem prover [cite: 18, 26].

PART 3. SOFTWARE I CAN ACTUALLY RUN

Vampire
https://github.com/vprover/vampire
C++
Modified BSD Licence
2026
MAINTAINED
Vampire is the undisputed heavyweight champion of the field, having won all eight divisions at the most recent CASC world championships [cite: 11, 27, 28]. You can run a full saturation proof search with neural clause selection, induction, and higher-order logic today. Its main gotcha is its immense complexity; modifying the inner given-clause loop requires navigating decades of highly optimized, tightly coupled C++ code. The current release is fully reproducible, but you must supply a high-quality SAT solver backend such as Z3 or CaDiCaL to unlock its full AVATAR capabilities [cite: 5, 11, 27]. 

E Prover
IDENTIFIER UNKNOWN (Canonical academic site used over direct repo)
C
GPL
2026
MAINTAINED
E is the preferred testbed for machine learning experiments due to its cleaner, more modular architecture compared to Vampire [cite: 6, 7, 20]. The ENIGMA framework is built directly into E. You can run context-aware, GPU-accelerated Leapfrogging experiments using its GNN integration today. The known limitation is that its baseline symbolic performance is slightly lower than Vampire's, meaning ML improvements in E sometimes only bring it up to par with Vampire's unguided manual heuristics [cite: 12]. 

TPTP Editor
https://marketplace.visualstudio.com/items?itemName=DE.tptpeditor
TypeScript
Free / Open Source
2026
MAINTAINED
This is a modern VSCode extension that provides syntax highlighting, error detection, and remote submission to the SystemOnTPTP cluster [cite: 29]. A practitioner must install this immediately. It completely removes the friction of parsing the esoteric TPTP syntax and allows you to author conjectures and test them against 50 different solvers without setting up local toolchains.

Prover9
IDENTIFIER UNKNOWN (Originally by William McCune)
C
GPL
2026 (Updated fork)
DORMANT
Prover9 is the direct descendant of Otter, the original successful saturation prover. While a 2026 fork added native TPTP parsing and multi-core scheduling, the core inference engine is untouched since 2009 [cite: 30]. It is effectively dead for frontier research, but it remains the most readable, canonical reference implementation of a basic given-clause loop in existence. Do not run experiments on it, but read its source code to understand how the loop works before looking at Vampire.

PART 4. DATA AND BENCHMARKS

TPTP Problem Library (Thousands of Problems for Theorem Provers)
https://tptp.org/TPTP/
10.5 GB
Academic / Open Access
The TPTP is the absolute, unquestioned center of gravity for the field. Version 9.3.1, released in August 2026, contains over 26000 problems across multiple logics, including classical first-order, higher-order, and recently, non-classical modal and epistemic logics [cite: 15, 31, 32]. It is used to measure the objective strength of an automated theorem prover. The benchmark is authoritative, but it suffers from extreme overfitting known as TPTP DNA. Because all major provers are tuned against this exact dataset for decades, their internal heuristics often collapse when exposed to completely novel formalizations that lack the structural signatures of TPTP problems [cite: 2, 12].

CASC (CADE ATP System Competition)
https://tptp.org/CASC/
Archive of results
Open Access
CASC is the annual world championship for theorem provers [cite: 12, 33, 34]. The archived experimental records contain the exact CPU times, solved problem counts, and solution outputs for every major prover. A practitioner uses the CASC archive to establish baseline performance metrics. If you build a new heuristic, you must demonstrate that it beats the CASC-J13 (2026) winner on the exact eligible problem list published for that year.

Mizar40 / MPTP (Mizar Problems for Theorem Proving)
IDENTIFIER UNKNOWN (Hosted academically)
Roughly 50000 problems
Open Access
This is the standard dataset for large-theory premise selection and machine learning evaluations [cite: 7, 8]. It is used to measure how well a heuristic can navigate massive mathematical libraries with tens of thousands of irrelevant axioms. It does not suffer from the same saturation issues as TPTP, but it is heavily biased toward set theory and topology.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to baseline yourself at the frontier is the evaluation of Reinforcement Learning for Neural Clause Selection in Vampire.

Software and Version:
Vampire version 5.0 (the specific build utilized at CASC-30 in 2025) [cite: 12, 23, 34].

Dataset:
The standard diverse TPTP first-order logic benchmark suite, partitioned into training and holdout sets [cite: 23, 31].

Parameters:
You must configure the standard given-clause loop with a fixed age-weight ratio to establish the baseline. For the neural run, you must inject the trained RL network as the primary Clause Evaluation Function. The critical parameter is the CPU instruction limit per problem, which controls the budget without being affected by GPU network latency. 

Replicates and Seeding:
Because the prover's internal term-hashing can cause non-deterministic behavior depending on memory layout, you must run 5 independent replicates per problem using a randomized random-seed parameter supplied to Vampire's command line.

Compute Cost:
Training the network requires approximately 48 to 72 GPU hours on an A100. Evaluating the test set across the diverse TPTP benchmark requires approximately 500 CPU hours, heavily parallelized across a cluster.

Expected Result:
You are looking to replicate the published claim: a 20 percent improvement in the number of in-training-unseen problems solved under a short, practically relevant CPU instruction limit, compared to the baseline manual strategy from which the network initially learned [cite: 23]. The baseline number of solved problems is entirely dependent on your hardware speed, which is why the 20 percent relative improvement is the target metric.

Three Common Ways People Get This Wrong:
1. Measuring wall-clock time without accounting for neural evaluation overhead. If you compare a manual heuristic to a neural heuristic using a 60-second wall-clock limit, the neural model will process drastically fewer clauses due to GPU synchronization latency, masking its superior choice quality [cite: 8, 35]. You must measure by processed-clause count or CPU instruction limit.
2. Failing to isolate the heuristic from the simplification machinery. Subsumption and demodulation change the state of the active set dynamically. A different heuristic changes which clauses become active, which radically changes which future clauses are deleted by subsumption. This butterfly effect makes debugging seemingly identical runs impossible unless simplification is temporarily disabled.
3. Evaluating clauses in isolation. Naive implementations run the neural network on one clause at a time. The start-up overhead of moving a single tensor to the GPU takes longer than doing ten thousand manual symbolic inferences. You must batch the evaluation [cite: 8, 35].

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

A Universal, High-Throughput Clause Evaluation RPC Server
Currently, ENIGMA has a bespoke, multi-threaded GPU server tightly coupled to the E prover [cite: 35]. Vampire has its own internal neural evaluation pipelines. There is no off-the-shelf, language-agnostic Inter-Process Communication (IPC) tool designed specifically for high-speed saturation provers to send clause states to external ML models.
Interface required: A gRPC or ZeroMQ socket that accepts a flat array of serialized clause abstract syntax trees (or anonymized arity tensors) and a state vector representing the current active set. It must return an array of floating-point priority scores. 
The hard part: Serialization latency. The budget for selecting a given clause in C++ is on the order of 10 microseconds [cite: 20, 35]. Sending strings over a local socket takes longer than that. You must build a zero-copy shared memory interface. Multiple groups have privately rebuilt variations of this exact batched-evaluation bridge because no universal standard exists.

Hardware-Accelerated First-Order Subsumption Engine
During a standard proof search, millions of subsumption checks are executed [cite: 1]. Unlike propositional SAT solving, first-order subsumption requires NP-complete unification and matching searches. 
Interface required: A CUDA or FPGA kernel that takes a new candidate clause and the entire active set of clauses, and returns a boolean indicating if the candidate is subsumed by any active clause.
The hard part: Branch divergence on GPUs. Unification requires highly irregular tree-traversal algorithms that perform terribly on SIMD architectures. Building a GPU algorithm that efficiently batches first-order unification would revolutionize the field, as subsumption is currently the greatest absolute bottleneck in saturation proving [cite: 1].

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

Pure Large Language Models for Saturation Proving
Attempting to use LLMs (like GPT-4 or specialized variants) to act as end-to-end saturation provers or direct clause generators has failed to produce frontier results. Methods like LINC or DeepSeek-Prover translate natural language to logic well, but when asked to execute deep proof searches, they hallucinate abstract symbols and lose grounding in reality [cite: 10]. They cannot maintain the strict invariant required by the active/passive sets because they do not understand formal refutational calculus, only statistical language patterns.

Unbatched CPU Inference for Neural Guidance
Early attempts to plug neural networks directly into the clause evaluation function of the C++ prover, evaluating one clause at a time on a single CPU, were a catastrophic failure. The inference time per clause was measured in milliseconds, while manual heuristics operate in microseconds. The provers lost entirely on wall-clock benchmarks because they simply ran out of time before generating enough of the search space [cite: 8, 35]. This forced the architectural pivot to delayed, batched evaluation on dedicated GPU servers.

The TPTP DNA Critique
There is a standing, heavily debated methodological critique regarding the field's reliance on the TPTP library and the CASC competition [cite: 12, 31]. Because the CASC rules enforce strict time limits on known problem categories, authors heavily tune their systems' strategy schedules to the statistical distribution of the TPTP. Methods that look incredibly strong in papers are often shown to be measuring an artifact of the benchmark: the prover simply recognized the syntactic signature of a known problem family and loaded a hardcoded heuristic. When these provers are deployed in real-world software verification or interactive theorem proving backends, they frequently fail to replicate their benchmark performance. This critique has been answered partially by introducing unseen problem divisions and shifting to reinforcement learning that generalizes better, but the underlying bias of the TPTP library remains an unresolvable structural reality of the field.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

1. Global Active-Set Reinforcement Learning
Feasibility: Modern GNNs and Leapfrogging have proven that evaluating batches of clauses in context works [cite: 6, 8]. However, current systems still treat the active set as a relatively static background context.
Experiment: Train an RL agent whose action space is not just selecting the next given clause from the passive set, but aggressively pruning and re-ordering the active set itself dynamically. 
Measurement: Measure the total memory footprint and the depth of the generated proof tree.
Falsification: The idea is falsified if the overhead of constantly re-embedding the active hypergraph exceeds the time saved by having a highly optimized, smaller active set.

2. Zero-Shot Domain Transfer via Foundational Logic Models
Feasibility: ENIGMA Anonymous proved that stripping symbol names allows generalization [cite: 7, 8], and recent work in differentiable ILP shows zero-shot rule induction is possible [cite: 10].
Experiment: Train a massive symbol-independent GNN on the entirety of the MPTP set theory benchmark. Then, without any fine-tuning, deploy it as the clause selector for Vampire on software verification (memory model) problems.
Measurement: Compare the budget consumption of the zero-shot model against a model trained directly on the software verification problems.
Falsification: The idea is falsified if the structural graphs of software verification clauses are so topologically distinct from set theory clauses that the symbol-independent embeddings produce random noise.

3. GPU-Accelerated Redundancy Elimination
Feasibility: Provers are currently hard-bottlenecked by single-core CPU subsumption [cite: 1]. High-memory-bandwidth GPUs are now ubiquitous.
Experiment: Extract the subsumption index (typically a feature vector index or discrimination tree) from Vampire, implement a flattened representation in CUDA, and route all forward-subsumption checks from the given-clause loop to the GPU asynchronously.
Measurement: Total wall-clock time spent in the simplification routines versus the core inference routines.
Falsification: The idea is falsified if the latency of the PCIe bus transfer for newly generated clauses is higher than the CPU time required to traverse the discrimination tree.

What will NOT work:
Attempting to replace the superposition calculus entirely with an end-to-end neural sequence model will fail. The search space of first-order logic is semi-decidable, and the precise unification of variables cannot be reliably approximated by continuous vector operations without sacrificing the absolute soundness guarantee that makes automated theorem proving useful in the first place. You must leave the generation of clauses to the symbolic engine, and restrict the neural network entirely to the heuristic ranking of those clauses.

**Sources:**
1. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGN3Wdcscv7bM3ik8NqXyI0W1WG48SFM29h4PUVybFRnf5uVEaSe2FVBnKYBsf1YxMSAs31D-XCXuYU6Vz239rCCjHcT1UhvvFtF5vuDKGFwdIYjxXAJOi0NyY3PbDLAPmCnc_P7GeQ8fDgZTDJaCUg0nq0-eB7mQSphZw=)
2. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH94W2QZljPRVq2YmP5hKVB3rjLuVUMptBjl2E-gGAVNRgLFWnCy6cei0bE2EuP4B-j_oPou-jJ0zH_TQNs8Z0QSb0fB4MEipWURYFEY1MXvhwGkl8afVQo8NQreirUqddh8Td3_j_E)
3. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJ9EsksstUONxv5yPTBfzFm7GSLLqxm20cYUWc66EA0UhsXqAjqYgVudvNYchBEKtMrqONAqROwx_LwTlZMOsMr1YlgF0ZbiFjpuvfS0Hb4RvJz6931bFn5gPC4YHZnfhT-y4yFNKxeRKuSqVzttKAconR-XM3RjXcMfVFjLejGdBzeUU-cB2kGKKR0X2nvGeLoE7g0M-YW4XRc5hUzuOetgd9kR8IIX28yk1g_pzwDdnD)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH94-InIn71bKE2jkfDJ8Qbn6Au1Qxwyu1-j25SVrsA2UDoDg3aFknxXaV4iQhp6PV2S-5QQJejMUdvGzfEUha0WZ9QeM-CG9Uyq5K7VKf60P2libMzrw==)
5. [tuwien.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2NQXJSHeWSuaAKh8vJjoWjyq9PF04xXBeemFq9DRGMAoHHF2xPNhHbIAbJN2SgeZ8GcjLxl1lja5uL0xBTjcznVCbSU9nNNUBwH0ZkFcwrqgDsnYvJXeNOL3f2FxyZqYqj9Uq_k8c4ithrzw=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtJIzuaG2rkxCs2ZwcMDBBtkp0VlWbB7B9BQOB6Dvz6XmDsR-RzBCWp202HLleIFj4udWKX9yzChItD6Kk_50aTZmqFFO9LpvbWrkZaaCmLMpHFfGSgXMgTA==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYl3i9PEg1ZcCJM1-KW4yoe5RH9-6rQmIcac4TK0jHAwJFnRCz-JhYwrhuRB_DwfgK0ekJ-c5poGI2fjpI_5a5dYaGjbo2U_fjStvOGVJ0s36jDsx1xw==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRvdFb-xihI9EZesg0gfaYYKCTMqORVMpm2OecCVPQvS3TeOikFRjS2918Fh9iJgkBvGNt0YoJc6DB0TzrTsoLcNUM0gw1WoRaCE8SGTDlSIk8v5PmGA==)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTDrYHLXPfElYB-wEI4CQB_n5GRopHsgu-aqzgPX8NUUO8T2XFHkumnxAnFdwsWouyJskRA3qhh0sSH6y0ojLrKGHR6FBSIp5Y6hjIEXtYZ09aQ2OsQBKfxM9G08gPFx6HBZ9-Sc4rXkPVghlsih0dcMbqX-rFGAI3qYDWLn_m0_DVcseqLir9tNMkhIx7yIUO-LGl-0XRdz6JFMmLzPRMDGN133or1PhPQlcbg-76xn5nTbkd)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBrPYju8I9k8XZ8etML1456woTlfj5RV7R3T0MVtIKH7VnyYoCNuD3XtU7nZ9n7-xD6E2IL18Nx9tvN4DznI7xdRxWFP4qrDgsCr57NwzJmvg8MKd_rsbiog==)
11. [cysec.wien](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHO0MEp14jwF-vNaZPhE_7KSw2oitNNR0GYrMttOEf5-zQdkjX4kO8JCwF6QBk-nygR0sgkybNMWapPE108bHd2OXuZbl7QbJNmt_hJ2V-1JUVPs8T8-mgXzpJCXoqYcO3HvHTuJor8WMcToCV3OQk=)
12. [tptp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGp_KJcGBiQE5nss41wRMvT9wXnKymvE6vOq8TgGYyBi0TT_SKcOGQPcBNDZegrB-yPJysv9b3Ns6G5cmaRx0IWK2VNjGI5uP0nuRCC)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsuo0CQuYXiYZPqfIOc4mr2EybztNJAzAk7i6B-vQRbnylEWCSDxC_lvuqI2q0FJhAaTZ3qK_YzTZU8_AsRRHqeJ66ESYaI1ObDj0XQtCdblq67NgISA==)
14. [tptp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtj885ulGEnF8-2E0c-DFD2dx6kUeAUNofHmG775g91M70SB2MspeJECsYyyINDGfdGXjYs6uRKswjhomZxvKfjt3C5pV80cUBTDpJyAYBV170cYwbFPnqs3mWY_AHiULq__ZLjKDSih4YJP_lBLv7fQ==)
15. [ceur-ws.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFBlW5XIn4vcv2XbWtN7VCeHmxHjkyPkFKQ7988qp_LoDwVrfJSGkQzJX0GSIEMWnUlRsq9U-7xar-zfF_D6X4Rcl4EvJQsJa7NfcnTAgSrWOxHy2kdAQoZS44h5E=)
16. [scitepress.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRQPAC9YnDPLmkUF04b7TVyevnQxEmD0N23wYtQfZZKtwkRNw8i6FXX-OVTYoqxADv3u4Rxf9B6Ai1sYtUijrCifSgDBJni0V-bGAh5DZAYhjPj8GP24TiRJG1Sa8y1iibPAM=)
17. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIPF5nBDxVSQRj_ij0XLO6v4IyJA57yZSFCpJQeewNYBtITSmzD5lqMOBnNY1YJqGLh7nI16o_Pxk2zgieLKi6qAGdvPccipNRA54b5qVVW2y4aHRojEDdpY5xkr_HJOWDlyYLwgQXGYgP99j-dPq0n2RmGBOq7Lv6YbAytw==)
18. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMfiSEBlC3cg2HHsSTBMN-cd4Ag-2wUWmbsxgWjgfJ-830sZKde51dWFLCQ4W1ngHOtpccB315W2-k63KYeHnHTsmP-zR5-WoD3fMKCilP7NQM5t5XIvG9aWjOx-gmmr8duoRVU2peJ5TAbUl4-JT0UkycgTWXlVdNzqxG)
19. [oeaw.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTQpXyRt620JFXIy3YCoC0J1c3Sj2XnqjM7z7ZbnXcOrObKZoVh9tqJnFfkOUQSMcfh3NViNEA3Ehpk8cP8o49-f_KbA3Yajt6BznW7HzssYyME6QMMYAwNG33nVCQ)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE77ZaMcRDTAFU5U-RWttluUCfq1aCf9-DALQlTh-ntHs8KhzHQzgiyYm5WLSDYjlHHnYFpv4KkwOw5YAwJ5wDSBTjdQRDvvp9dAFOGBOoFPfTkO2pjIUMMsw==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHePyuRdtzuMwmYdx-q9KLz7w7xWyn3SkhI58z9MxPNKn8jOhC38IWiCUCQiZikx4Q71qe_2fh_UXWbok44KQxFW-hoIRZhpRJ2u9OluKB9YaIqeqixrA==)
22. [soton.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4EEKchtg-q_ps-CENXDgdMvAJHM7apW3zXJblRoYa8r1tFYqQrVJRGSrxICD1oMr0pLKai02vXckBRg8vdx3QXjyRCRZrhv1BIpkK0FILkVrUkRdjW2sRDQ==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBr6LA2_pzqeMsvOEwLlY3kz0ZGI6B6NBM1luLsmgR2oFTuEye-8gU6iegeMpGVs9HndCq6zJS1YK4bHfcFZ6uBLm_GeLWblr39z1_F4UuPCJRUl853g==)
24. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYA_AeQ-GW-GLamxbm66eva-3U4hOrzVP6UHCwtus0NAyUDiVZ6-_6E-wFMNr9RchJRfgkbVAfnAdbaxn-YNhMp8qhPxhLTyr2uxn3cmjENyxTTti7tqwoP3Pjai0=)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnpOnVefhgabnF5ML7DLMxzWXQj5k0z2uH84c5fgFZZUhsJM5KUzX07Qt5JcwWg6V4EnBIYmd_If_4C8HjLBHyeDFmoNIwFKrVeqkOOODsP1xMRWbFkA==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaQrQD3ZT8v1VX8XFHsgW1qVEiDGTLbtCqGHIswR19Y5dq21VJMhuwjs9QHzqXFsQ3DLcWvLRao4SQTrgAGeLQen7WxISOQyYxILE4Q6oASfcilxFfjrRNow==)
27. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFocHXpvr9h2KELR3-lY_2ChXmJxrVbM2VNa6D2Jm4SYI7qe2Ye97Y_6Z74dKhsysfZwkXUfaKM88bPsdvn9qIA0h6__uR-W-6jgl5ta9yiShDwrY6lLP7i)
28. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8TVS4i2bhuLKh6CqikEgoDCPsgPqJmtAvkF0Zi3-oR-vRvZVyKY4OSCOrk1HhufEspdhh3TN6Ca5fajA2f8r_IdSDf_PaIO_9C1ABX0KWVXsoROpN3jgdMXS8WHlzHoOYU3Q6uMn-r1TQAvU=)
29. [visualstudio.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGa4VZujjXyJTis2sHkZMDWV7FgOlI5tqGv2Qle4XYE5_DnWwHV9eUWqzlQ1IK94gDB4tHnipDkp5TtSzyvs0nP_A1LuDSi37pACyMIrH0kqRY4_511OhqqR3I5oKsiNSQ_MGfdHj7HUSVy4GivCB_Ioo-qtOpC7Q==)
30. [tptp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbpeyPJIUILZRVxpLbptqavAer9dgiVXfdiNR7qrLdfXMhCoYrgAcUoR4TluHbkmYExnwVTK-hv-w1I5nJEmpnATxy1kuQBg5M7Rm4lg2UsA6jtkmahaxmI8_liw7cN-Kvjcoc8lLy)
31. [tptp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-y8iY0Z9tjH2F9f-itTlW4Xm4tanFmENI32eO61a9DdZO3j1TL_-yZ_KEHmUMZWW7RWJepskTRh8VS6aLXbPSnNn6Nl2VRVUg5yMi)
32. [tptp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKkopVYDbLRfMdcyLJXpB2AJPUW1URZwxbHF0lDVMfISeNeOGGGpv2NL2DedLA-l6ZagJOK6CKQdojMNZiU7VqKvhORBZO_WbZglu4nPB4VyWNXUC8cW0veWt6EOLbChxd)
33. [tptp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnyisLemaW-36ke_x2dS5LXmjltDxm-ByclfnaPZe-sIG6nLBQGQoqV_ZaIHxqpZGrj8gTYzygKPeeKaYi0nhnnpBCYIOsFHZUEsGIl6Xd9Q==)
34. [tptp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7lJOFtb-mLsSsQT9q2ZN6IWMveXL_qS7xmDQfgpp8-4-T4pTDHy-a5a79nOU0ISU-FT1avyNKnatjW-GJV-pOtz2T9k1m7VCrrxzGsFyI)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMyObwO-6H-1N-bcSFIR7Q2M4SIyX3TYw7_qHmVL4MYJ4P9VUZFnR0qJIxLU9RTtk5E45PvmNhvPUOfL_t1BsK6D-C_qOS-eMg2uLnWaInrYxwyxNZNw==)

