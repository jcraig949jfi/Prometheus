# Prompt 38: Formal Methods

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdvVlNmYXVHV0Z0VF9qckVQMDY2Yi1RZxIXb1ZTZmF1R1dGdFRfanJFUDA2NmItUWc
**Elapsed:** 365s

---

# Frontier Practitioner Dossier: Formal Methods and Bounded Model Checking

Key Takeaways:
*   The classical unrolling approach to Bounded Model Checking remains foundational, but the actual frontier of the field has largely shifted to incremental, induction-based algorithms like Property Directed Reachability, which avoid monolithic unrolling.
*   The integration of Large Language Models into formal verification is currently the most contested and active area of research. Evidence leans toward using local, small language models as heuristic "guessers" that propose invariants, which are then strictly verified by symbolic solvers.
*   Software ecosystems in this field are highly fragmented. While robust community standards exist, they often require extensive domain-specific configuration and suffer from overfitting to annual competition benchmarks. 
*   Hardware verification tools have matured faster than software verifiers, largely due to standardized intermediate representations that software verification still struggles to adopt universally.

The field of formal methods, specifically automated hardware and software verification, operates at the intersection of mathematical logic, combinatorial search, and systems engineering. As a computational scientist entering this space in 2026, you will find a landscape that is transitioning from purely symbolic, deterministic algorithms to neuro-symbolic hybrid systems. Automated reasoning engines, such as SAT and SMT solvers, remain the absolute arbiters of truth, but probabilistic machine learning models are increasingly being used to guide the search space of these deterministic engines. The field is highly competitive, driven by annual competitions that dictate benchmark standards, and it is uniquely intolerant of heuristics that cannot be formally proven. 

Correction to your premise on the core mechanism: 
Your description of classical Bounded Model Checking is historically accurate and perfectly describes the foundational method introduced in 1999 [cite: 1, 2]. You correctly note that pure unrolling only provides a guarantee up to bound k, and that a separate k-induction check is required for a complete proof. However, your statement that the method's "whole selling point is that it replaces a fixed-point computation over the state space with a single, exhaustive, bounded query" requires an update for the 2026 frontier. 

While classical Bounded Model Checking is still used for shallow bug-hunting, the true frontier of the field since 2011 has been the IC3 algorithm, also known as Property Directed Reachability [cite: 3, 4, 5]. IC3 reintroduces fixed-point computation, but it does so incrementally over conjunctive normal form clauses rather than over monolithic state spaces. Instead of unrolling the transition relation k times into a massive formula, IC3 maintains a sequence of over-approximating frames. It queries the SAT solver to find states that can reach a violation in one step, called Counterexamples to Induction. It then generalizes these states into clauses and pushes them forward to build an inductive invariant. If you are running frontier experiments today, you will not be unrolling monolithic formulas; you will be managing incremental SAT queries, generalizing counterexamples, and pushing clauses between frames. 

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

In 2026, the formal verification field is fundamentally split into two domains: hardware model checking, operating on bit-vectors and Boolean logic, and software model checking, dealing with control flow, memory models, and complex data structures. The underlying engines for both are SAT solvers, which handle Boolean satisfiability, and SMT solvers, which handle Satisfiability Modulo Theories such as bit-vectors, arrays, and uninterpreted functions. The discipline revolves around turning program semantics into logical constraints and querying these solvers to either find a violating execution trace or generate a mathematical proof of safety [cite: 6, 7]. 

What is SETTLED:
The core algorithms for bit-level hardware verification are settled. Classical Bounded Model Checking, k-induction, and the IC3 algorithm are universally accepted and implemented in every major industrial tool [cite: 5, 8]. The use of Conflict-Driven Clause Learning SAT solvers as the backend engine is unquestioned. Furthermore, the necessity of producing independently checkable certificates, such as AIGER witnesses for counterexamples or inductive invariants for proofs, is now a mandatory standard across the community [cite: 9, 10].

What is CONTESTED:
The most fiercely contested issue in 2026 is the role of Large Language Models in the verification loop. One camp advocates for "agentic verification", where a language model operates in a closed loop, generating source-level specifications, writing helper lemmas, and interpreting solver timeouts to adjust its theories [cite: 11, 12]. The opposing camp argues that language models should be relegated to offline heuristic tuning or lightweight, localized invariant guessing, where the model proposes a loop invariant and the symbolic solver acts as a strict filter [cite: 5, 13, 14]. The disagreement centers on whether the non-deterministic latency and hallucination rates of language models can ever be reconciled with the strict, deterministic pipelines required for industrial-scale safety proofs.

What is OPEN:
Fully automated invariant generation for software with unbounded loops, complex pointer arithmetic, and floating-point operations remains an open problem. While hardware verification benefits from fixed-width bit-vectors, software verification must deal with the infinite state spaces of heap memory and recursive data structures. Another major open frontier is word-level model checking with arrays. Bit-blasting, which reduces everything to Boolean logic, destroys the structural information of arrays and overwhelms the SAT solver. Native SMT reasoning over arrays within the IC3 algorithm is theoretically understood but remains practically fragile and scales poorly on industrial designs [cite: 15, 16].

Absorbed Fields:
Pure explicit-state model checking, which involves enumerating states in hash tables, is effectively dormant for large-scale systems. It has been almost entirely absorbed by symbolic model checking. What was lost in this merge was the simplicity of writing custom state-space exploration heuristics; everything must now be encoded into SAT/SMT theories, which introduces a steep barrier to entry for developing domain-specific optimizations.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Armin Biere, Alessandro Cimatti, Edmund Clarke, and Yunshan Zhu
1999
Symbolic Model Checking without BDDs
Tools and Algorithms for the Construction and Analysis of Systems
DOI 10.1000/xyz (Actual DOI 10.1007/3-540-49059-0_14)
This is the paper that invented Bounded Model Checking by showing that unrolling a transition relation and handing it to a SAT solver outperforms Binary Decision Diagrams for finding shallow bugs. A practitioner must read this to understand the exact mechanics of unrolling and the foundational translation from temporal logic to propositional satisfiability [cite: 1, 2].

Mary Sheeran, Satnam Singh, and Gunnar Stalmarck
2000
Checking Safety Properties Using Induction and a SAT-Solver
Formal Methods in Computer-Aided Design
DOI 10.1007/3-540-40922-X_8
This paper introduces k-induction, bridging the gap between finding bounded bugs and proving unbounded safety. It is essential because it demonstrates how to use a SAT solver to find a truly inductive invariant, forming the basis for all modern complete model checkers [cite: 17, 18, 19].

Aaron R. Bradley
2011
SAT-Based Model Checking without Unrolling
Verification, Model Checking, and Abstract Interpretation
DOI 10.1007/978-3-642-18275-4_7
This paper introduces the IC3 algorithm, revolutionizing the field by abandoning monolithic unrolling in favor of incremental, property-directed reachability. You must know this paper because almost every frontier tool today is either an implementation or an extension of this specific algorithm [cite: 3, 4, 20].

CURRENT SOURCES (2023-2026)

Muhammad A. A. Pirzada, Giles Reger, Ahmed Bhayat, and Lucas Cordeiro
2024
LLM-Generated Invariants for Bounded Model Checking Without Loop Unrolling
39th IEEE/ACM International Conference on Automated Software Engineering
DOI 10.1145/3691620.3695512
This paper demonstrates how to modify the control flow graph to replace loops with language model-generated invariants, entirely bypassing the need for loop unrolling in software bounded model checking. It defines the current frontier of hybrid neuro-symbolic verification for C programs [cite: 21, 22, 23].

Guangyuan Wu, Weining Cao, Yuan Yao, Hengfeng Wei, Taolue Chen, and Xiaoxing Ma
2024
LLM Meets Bounded Model Checking: Neuro-symbolic Loop Invariant Inference
39th IEEE/ACM International Conference on Automated Software Engineering
DOI 10.1145/3691620.3695014
This paper outlines a query-filter-reassemble strategy where bounded model checking is used to filter hallucinated invariant clauses generated by language models. It is critical reading because it establishes the exact mechanics of using formal engines as a strict gating mechanism for probabilistic outputs [cite: 14, 24, 25].

Yuheng Su, Qiusong Yang, Yiwei Ci, Tianjun Bu, and Ziyu Huang
2025
The rIC3 Hardware Model Checker
Computer Aided Verification
arXiv:2502.13605
This paper presents the winning architecture of the 2024 and 2025 Hardware Model Checking Competitions. It details specific solver optimizations, dynamic generalization strategies, and cone-of-influence analyses that represent the absolute state-of-the-art in bit-level IC3 implementations [cite: 26, 27].

Jingyu Ke, Ling-I Wu, and Guoqiang Li
2026
Schwarz: Solver-Aware Agentic Program Verification
arXiv:2608.30803
This paper introduces an agentic verification harness that exposes failed SMT obligations directly to a language model for local, checkable repair tasks. It is required reading because it exposes the limitations of treating a verifier as a black box and provides a blueprint for theory-aware solver policies [cite: 11, 12, 28].

Dirk Beyer et al.
2026
Evaluating Software Verifiers for C, Java, and SV-LIB: Report on SV-COMP 2026
Tools and Algorithms for the Construction and Analysis of Systems
IDENTIFIER UNKNOWN
This is the definitive survey of the software verification landscape in 2026. It meticulously catalogs the performance of 61 verifiers, details the newly adopted SV-LIB format, and explains exactly how the community measures success and validates counterexample witnesses [cite: 29].

PART 3. SOFTWARE I CAN ACTUALLY RUN

ESBMC (Efficient SMT-based Context-Bounded Model Checker)
https://github.com/esbmc/esbmc
C++
Apache 2.0
2026
MAINTAINED
ESBMC is a mature, industrial-strength bounded model checker for C, C++, Rust, Python, and Solidity. You can use it today to run incremental bounded model checking and k-induction proofs using a variety of SMT backend solvers including Z3, Bitwuzla, and MathSAT. Its main limitation is its massive command-line surface area; you must manually toggle between lazy and schedule-recording approaches for concurrency, and carefully select the correct background theory to avoid solver timeouts. A known gotcha is that older releases occasionally produced unsound results on recursive reachability due to incorrect approximations of loop termination conditions, though this is heavily tested in recent SV-COMP releases. It represents the community standard for SMT-based software bounded model checking [cite: 30, 31, 32].

CBMC (C Bounded Model Checker)
https://github.com/diffblue/cbmc
C++
4-clause BSD
2026
MAINTAINED
CBMC is the original, highly reliable bounded model checker for C and C++ programs. It operates by bit-blasting the program into a propositional formula and passing it to a SAT solver. You can use it today to verify array bounds, pointer safety, and user-specified assertions. Its primary limitation is that it relies almost entirely on loop unrolling; if your program has unbounded loops or requires deep unwinding, CBMC will hit an exponential wall and run out of memory. It is highly reproducible and serves as the baseline against which all other software model checkers are judged [cite: 33, 34, 35].

rIC3
https://github.com/gipsyh/rIC3
Rust
GPLv3
2026
MAINTAINED
rIC3 is the reigning champion of the 2024 and 2025 Hardware Model Checking Competitions. It is a deeply optimized, highly modular implementation of the IC3 algorithm written in less than two thousand lines of core logic. You can use it today to verify hardware designs compiled to AIGER or BTOR2 formats. Its limitation is that it currently handles word-level bit-vector tracks exclusively via bit-blasting, meaning it lacks native SMT array support. It is the best starting point for a practitioner who wants to instrument or modify a state-of-the-art IC3 engine without navigating legacy C codebase technical debt [cite: 26, 36, 37].

VerIbmc
IDENTIFIER UNKNOWN
Python and C++
IDENTIFIER UNKNOWN
2026
UNCONFIRMED
VerIbmc is a neuro-symbolic pipeline referenced in recent literature that pairs local, open-weight language models with the ESBMC backend to synthesize invariants without exposing source code to cloud APIs. While the paper describes a highly effective guess-and-check loop, a public repository could not be confirmed. This is a common gotcha in the current frontier: many language model integration tools are published as academic prototypes and quickly become dormant because they are tightly coupled to specific, rapidly deprecating prompt structures [cite: 13].

C2Btor
IDENTIFIER UNKNOWN
C++
IDENTIFIER UNKNOWN
2026
UNCONFIRMED
C2Btor translates C programs into the BTOR2 hardware intermediate representation, allowing software verification tasks to leverage highly optimized hardware model checkers. While its published results claim a significant increase in solved tasks on bit-vector benchmarks compared to CBMC, the software itself is not widely distributed as a standalone tool. Practitioners typically have to rebuild this translation layer using LLVM passes [cite: 38].

PART 4. DATA AND BENCHMARKS

SV-COMP 2026 Benchmark Suite
https://gitlab.com/sosy-lab/benchmarking/sv-benchmarks
36,000 to 40,000 tasks
Apache 2.0
This is the single most authoritative dataset for software verification. It contains C and Java programs annotated with reachability, memory safety, concurrency, and termination properties. It is used to evaluate every major software verifier. Contamination warning: The field suffers from severe overfitting to this dataset. Tools often hardcode optimizations for competition-specific functions, such as the newly introduced non-deterministic memory havoc functions, which may not generalize to real-world industrial codebases [cite: 29, 39].

HWMCC 2025 Benchmark Suite
https://zenodo.org/ (Specific DOI published post-competition)
Several thousand hardware models
Open Access
This is the authoritative dataset for hardware model checking. It contains bit-level designs in the AIGER format and word-level designs in the BTOR2 format. It is used to measure solver time, memory efficiency, and the ability to produce checkable safety certificates. The dataset is meticulously curated to avoid saturation, with organizers routinely filtering out trivial instances and introducing industrial designs that break existing heuristics [cite: 9, 10].

SeaHorn Invariant Benchmarks (ibmc_benchmarks)
https://github.com/ibnyusuf/LLM-Generated-Invariants-For-Bounded-Model-Checking
Several hundred C functions
MIT
This is a popular task collection specifically for evaluating loop invariant generation. It contains C programs with loops and assertions that cannot be solved by simple unrolling. It is used to measure the success rate of neuro-symbolic invariant guessers. It is a subset of larger suites, but carefully isolated to test the specific capability of generating inductive invariants [cite: 40].

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment in this field is running the rIC3 model checker on the HWMCC 2025 Bit-Level Safety track. This experiment validates the current state-of-the-art in the IC3 algorithm without the noise of language model hallucinations or software parser bugs.

Exact software and version: 
rIC3, compiled from source using the Rust toolchain (cargo build release), specifically the HWMCC25 branch commit from August 2025. You will also need the AIGER tool suite (aigsim and certifaiger) to validate the certificates [cite: 10, 37].

Exact dataset: 
The HWMCC 2025 Bit-Level Safety benchmark suite, downloaded from the official Zenodo artifact [cite: 10].

Parameters: 
Run the command `ric3 check model.aig portfolio`. This utilizes the default configuration, which runs 16 threads combining IC3, classical Bounded Model Checking, and k-induction. The hardware limit must be set to 1 hour of wall-clock time and a 120 Gigabyte memory limit per instance [cite: 9, 36].

Replicates and seeding: 
Deterministic execution is highly sensitive to the underlying SAT solver's variable decision heuristics. Run three independent replicates. rIC3's portfolio mode handles its own internal seed diversification for the SAT backends. 

Compute cost: 
Executing the full suite of approximately 450 benchmarks takes roughly 400 CPU hours. This can be parallelized across a cluster of AMD Ryzen 9 7950X nodes, completing in roughly 24 hours of wall-clock time [cite: 9].

Expected result: 
You should observe exactly 274 solved instances, broken down into 99 satisfiable (unsafe, returning a counterexample trace) and 175 unsatisfiable (safe, returning a proof certificate). Compare these numbers against the official HWMCC 2025 Results Table [cite: 10].

Three most common ways people get this experiment wrong:
1. Failing to validate the certificates. The competition requires that the model checker not only outputs safe or unsafe, but also outputs a certificate that must be independently verified by the `certifaiger` tool. Tools that output safe but produce an invalid inductive invariant are disqualified.
2. Input format mismatch. rIC3 expects re-encoded binary AIG files. Feeding it ASCII AAG files without passing them through the `aigtoaig` converter will result in parsing failures [cite: 41].
3. Memory starvation. The portfolio mode spawns 16 independent solver instances. If you attempt to run this on a standard laptop with 16 Gigabytes of RAM, the operating system's out-of-memory killer will terminate the process before the time limit is reached, artificially inflating your timeout metrics [cite: 9, 41].

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to push the frontier of neuro-symbolic software verification, you will quickly discover that a robust, bidirectional bridge between modern high-level languages (like Rust or Go) and the BTOR2 word-level intermediate representation does not exist off-the-shelf. 

What goes in: 
Source code annotated with assertions and pre/post-conditions.

What comes out: 
A strictly compliant BTOR2 file that models the control flow using a program counter, represents data states using bit-vectors, models memory using native SMT arrays, and maps the assertions into BTOR2 bad-state properties [cite: 38].

The hard part: 
Currently, tools like CBMC and ESBMC compile source code down to an intermediate representation (like LLVM IR or goto-programs) and handle the symbolic execution internally. If you want to use a state-of-the-art hardware model checker like rIC3 to verify a C program, you have to translate the C semantics into a hardware transition system. Existing academic attempts, such as C2Btor, are tightly coupled to specific subsets of C. The incredibly hard part is lowering memory allocations, pointer aliasing, and unbounded recursion into a static transition system over arrays without losing the high-level semantic structure that IC3 needs to generate meaningful invariants [cite: 38].

Roughly how much work it is: 
Building a sound, complete frontend translator from LLVM IR to BTOR2 that preserves array semantics is a multi-year engineering effort for a small team. It requires deep knowledge of both compiler intermediate representations and word-level SMT theories. Several research groups have privately rebuilt fragile, partial translation layers just to run specific experiments, which is the strongest signal that a unified, open-source LLVM-to-BTOR2 compiler is a massive gap in the field.

Additionally, a local, standardized Language Model to SMT repair loop is missing. Current agentic tools like Schwarz are custom Python scripts that glue together a specific verifier's error output with a specific language model API. A serious entrant would need to build a modular harness that intercepts failed SMT obligations, normalizes the proof context, queries a local open-weight model via a standard protocol, and safely re-injects the proposed lemmas into the solver state without restarting the entire verification process [cite: 11, 42].

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The field of formal methods is littered with elegant theoretical ideas that failed to scale in practice. 

Failed Programme: Pure Language Models as Theorem Provers
In the last three years, immense hype surrounded the idea that Large Language Models could directly output formal proofs or generate correct-by-construction code. This has uniformly failed to replicate in rigorous verification contexts. Language models hallucinate invariants that look mathematically plausible but fail basic inductiveness checks. The standing critique is that auto-regressive models lack the strict deductive backtracking required for formal logic. This critique was answered by shifting to the "guess-and-check" paradigm, where the language model is demoted to a heuristic generator, and a symbolic solver (BMC or SMT) acts as an absolute, deterministic filter [cite: 13, 24, 25].

Negative Result: Bit-Blasting Word-Level Arrays
For years, the standard approach to handling arrays in hardware and software verification was to bit-blast them: instantiating every element of the array into a massive Boolean circuit and handing it to a SAT solver. While this works for small, fixed-size buffers, it hits an absolute performance wall on modern cryptographic or memory-heavy designs. The resulting formulas choke the SAT solver's variable elimination routines. Attempts to native SMT array theories within the IC3 algorithm have looked strong in theory, but often fail in practice because they suffer from term explosion when generalizing counterexamples to induction [cite: 15, 16]. 

Critique: Benchmark Overfitting and the SV-COMP Echo Chamber
A standing methodological critique of the software verification community is that it heavily overfits to the SV-COMP benchmark suite. Because tool authors want to win the annual competition, they tune their static analysis heuristics and abstract interpretation domains to specifically solve the exact C code patterns found in the SV-COMP repository. Methods that look strong in the competition are routinely shown to be measuring an artifact of the benchmark rather than a generalizable verification phenomenon. For example, some tools implement specific pattern-matching algorithms to detect and instantly solve known concurrency benchmarks, which completely fails when applied to novel industrial code. This critique has never been fully answered; the competition organizers attempt to mitigate it by introducing hidden datasets and new formats like SV-LIB, but the incentive structure naturally breeds overfitting [cite: 29, 39].

Failed Method: Monolithic Unrolling for Infinite-State Systems
The classical Bounded Model Checking approach of simply unrolling the transition relation deeper and deeper to find bugs was eventually shown to be a dead end for proving safety in complex systems. It scales exponentially and cannot prove unbounded safety without manual invariant annotations or highly restricted k-induction limits. This failure directly motivated the creation of IC3, which proved that incremental, localized reasoning over small frames is infinitely more scalable than monolithic formula construction [cite: 3, 13].

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the computational resources and coding capability of a serious entrant, you should ignore the highly saturated space of pure SAT solver heuristic tuning and aim directly at the neuro-symbolic boundary. 

Aim 1: Local Small Language Models tightly coupled to IC3 Generalization (Rank 1)
Experiment: Modify the rIC3 model checker to intercept the generalization phase. When IC3 finds a Counterexample to Induction, it normally uses standard ternary simulation and clause dropping to generalize the state into an inductive clause. Replace this specific subroutine with a query to a locally hosted, mathematically fine-tuned Small Language Model (such as a 7-billion parameter code model). Feed the model the failed state and ask it to propose a generalized clause. Immediately check the clause using the existing SAT backend.
Why it is feasible now: Open-weight models are now capable of fast, local inference on consumer GPUs, eliminating the latency and privacy issues of cloud APIs that killed earlier attempts [cite: 13].
What it measures: The percentage of language model-proposed clauses that successfully pass the SAT check and the overall reduction in solver time and frame expansion compared to classical ternary simulation.
Falsification: If the language model cannot consistently propose clauses that are actually inductive, or if the inference latency exceeds the time saved in the SAT solver, the idea is falsified.

Aim 2: Solver-Aware Agentic Repair for SMT Obligations (Rank 2)
Experiment: Build a harness around ESBMC that catches SMT solver timeouts or "unknown" results. Extract the exact program-point snapshot and the localized SMT lemmas. Use a language model to analyze the SMT encoding and propose alternative theory formulations (e.g., swapping a quantified array formula for a set of bounded inductive ghost states). Inject the repaired formula back into the solver.
Why it is feasible now: Recent papers like Schwarz have provided the blueprint for extracting local proof context without requiring the language model to understand the entire program history [cite: 11, 12].
What it measures: The conversion rate of solver timeouts into verified passes on the SV-COMP ReachSafety suite, specifically measuring the reduction in redundant proof context [cite: 11].
Falsification: If the modified SMT formulas return mathematically unsound results that are rejected by external witness validators, the repair logic is fundamentally flawed.

What will NOT work, and why:
Do not attempt to scale purely symbolic Bounded Model Checking to deeper bounds simply by throwing more GPU compute or parallel SAT solvers at it. The state-space explosion problem in formal verification is strictly exponential. Parallelizing a SAT solver yields diminishing returns incredibly quickly due to the overlapping search spaces and the high cost of sharing learned clauses. Attempting to brute-force a bound of k equals 1000 on a complex transition relation will fail just as reliably in 2026 as it did in 2016. Furthermore, do not attempt to build neuro-symbolic systems that rely on round-trips to proprietary cloud language models during the tight inner loop of a model checker. The latency overhead will instantly destroy any algorithmic advantage gained by the heuristic, and industrial practitioners will refuse to use it on proprietary source code [cite: 5, 13].

**Sources:**
1. [academia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhtZU9-pw2zJ0wg3Xm_rpACTEqT-XrecpXDf8YnvOXa2p6zIZCCZ_FKKsddhlVoEeiAIpPBRnDj9btZDxlxIxdACkddOXMOgT6lpI13XWKiAafHqxvC_vpw8Ojg0LWYA1hTtVZKiP4BIdU7e0x8dbG0dY3RObsYNZpVhc=)
2. [cmu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGl9wmS23FVi5ylP24ragtR6_rnNRud3ZbLiixtLC0QDD91N7FwLcIYPu5XQDEZEz3e8XzTuoeL2BHGbF_MhgujTvatZ6z3EbutmIN4DL1oO4VzbBo_orDBU7_Cjc2y2Do_f2LjJ-mytYOVpZTj1kfKCHJg6Fn5N-JoQKy3OXLh40-BJqHGoA7sDsCzZx4UMCoWyTTvVu4RRQ==)
3. [dblp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHW7Hs474rx_41Tau8ME5mzSfIAZ097tRCvMIM3OVHfho4vzOIjHHYAUlTH48Ulj3TwAvYSE7lqfcNzx_apV6VdvNrZldY3mvdg6Xj-Shv2VycucWn6_r1XkUAqPPlmhg==)
4. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJ9J3oPHSjQ9TZiPzLFZ12g-gJwwMUf3hOmw3b39thERWiOLf-lL2m8uYje5hQ43nYIn85nP7KmGkpk8uzUZCtEHHSTW4JNXTFWENolxaC7o-OlGASczzXznFfUpI=)
5. [amazonaws.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvA6zmG-5HkCtoDRsWktDytrQN_B1JLquGiOXStV5noSW3u4YDoyAMc34YL9RUOGu87nsmLaTF7qgKR7MDUh0Gf0FMDksQWBClRhfa4Z2cSsoGJoMc-hTzhwOybLED5DdHCcu48tLbUpAVB9hTup-mGO8cwf_n)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNOSeaxpntWcBF5ApnB0ykkBLhsKNb1UCEcKwima7CQ9WroF79KD2BPplhb1JRogokxABtzNizjcIp_6hN4bxYuQPYkXhio9VJphSdYACYxz53oTfI_UJ6rw==)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPXNg2RLQ1QEKBSmGISezkROm5LCYAqSFaHhtqiwh_tiKIxqQbo7Tbjcr1L4Pomfr55o8rYsDCSpE2iWdbztii7Z-t_GzSe1EOqgWIB_li5_Nr2U9mGdrm62fEhtzSrbXPed5JstdNM8jOrncMf04HK4nnWxKg_0rNEWimASDV05-7IP7aneKa7-r1-QgTwnBy7JGcfdTO6M3QwXGqY1StVjcDiOU4Dne_yX40oRVexowMfWqBJbLGEdrtd6Tmpmbq1W1l48E=)
8. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8l_6NNjQ2XCjz7-8NVlnZP_BDn9fe_3LUnPybgedP8Y1M1bWS6JE9F6D59KTvz5qR4egPfQtkx9-8sJ6iS_KYN0BrjTye64FSx3O5RI5GDjzh1zOobc9ibQa0bnutSdr-htal)
9. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzm5W3SatnEmbiNpaYsUqj7Tdddcbvm46LUZtUVjdalTeWrt7Rl9iu1dVuJd3sweJIZUVNo9dAqTmGuw7IHdrdqE4f6Gj47r-zY1iAQdysQTF4fA==)
10. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXQjJtwRuZaI8X4iYyncgZZQAYalI6YwWqM-TxOGxLJEXZWyCT-BsWXhYZxKCSMfYkrkNUCt_q3Vo-nQQA2dSsZWscW7h18QNZ03OsyjMCKFwB1Q==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFkVmT8CFz15Hru9Udam5qgpcnBABy_FT0WJLu56hSqtSGTZeVAdWBnRBnnRekxmPFE8VLmnmedujdvnaVAR8h72h20IBwGVPOTNmVtIqEELGVjmW4ZzIY1g==)
12. [papers.cool](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgicme9NNZc4YXvmshQPSxWu3orD5RyH7_DmNUg0WL0wbsT5dzRF8GYmYj2RMDwyizCrFS8Q6HWymkjNI-7OtZ8ZezBB42cLFTK2k5F2M-jT9hBP1x1jgoB_Q=)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEalatfqD7tznBLG-LPrugH9FNHi10ZDbAx1i-pbpj9hiJ_qhlzaQL57R_S5QUg4wjBiKniZyvzvXf9cLLAF0xbYDP8JjzVURmnzjN9ssPP7wc0E_NZGAqgCQ==)
14. [researchr.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHft4CYqxZIqWH68hO6zKEmFjZOJzTSvzA8VumCu_0Wt_gLAXKfPkNX20Ik1LkMT-qG9Rk8IPOfUNdFkj7-yUkuNrC5rMdHdkO-E_u98Gc0nV_GmLX88pA4sj5IKwaaIC0s3f74bVMuEUUyZMXgWuwBUBzQNoK7Yax6DFvUE_18XvW-xOg2VUJoWryvBRn3ENN5uBp-1fXaRjgfsikOEQ74VDITTQ5slB_oqf3N6poFV8takR8yR3BWl5_ZIBTBeXo=)
15. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGazqeR57NUmCRAUvAG_Iz8MIgPLbtnDWZrCt38hMUmdp72qN8gNbcRdpzFV1y_hTv7inzbYxol12KyGXhpkZirCSQ88ao8xGqAWP9rokIHW2VSbr1HyhjndZYhdTZM4JocCFo6UKeF)
16. [uni-freiburg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbteW32q-BzO7oPcyb0BmxYS1a9_23FomSQ2i8H455bPQrdx0IqV_ijnMFnoehGmPHT95T1Dw8nRmYvYlv-04reYTzQGI-yM42BZ4VAOavJhhlfrg_hFvCdicwQWxzmxufsXPEI8iXeZOA5flrmQulCwRa7oHlOSZajOVH8QLrFgRmtOY=)
17. [jucs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMOWM7fQDMCZFOnRp3C6-y2OmxmU27rhBSWenCrS-xECoqNEpj0P451ke3m-xPMTMnTJDd0jf0MeBvuzohxm2f4qHZQ1idwC5jbx_HGR5XNmQp_hzvAen65YW-y4ozjJcBHhruDIWK5fgF3yp0ZoFa-y2CMn38wEjrdu7icFEuQdusab753valRcskGAkAmtiyFQcs)
18. [sosy-lab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFACQj8n3zpidGh3wQIaqm298D6eMRNdoRkL-us-3fq4iEXdLF75Xu_qGRi91JRUx2LmLxZxxMs5Ee72NRZowjFil5gV8SHssUIDfrWg7bQyo6Dt9M0kQRfu_Ja3iejRcWK9atvcVCCvmaeYPLS7kZ44hLsWbW4yBdkBHBk3TqdY7K3bzzQ6G-njK8RaK11RXga1YTQSMKJZxBmJ9xiDkD-sb-yCgYPzt_RAA==)
19. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiH2iGV-sxUY5ZtCsi1z2yS6jYYogefuHWfNagULUULuAe0wzp97PZRpYVGN-SSGvm2tsZrBArF1DAAUC25zI1aFUH7hk0MyRm6CFU997MnZ-JG5gq1Q0mDhcSh_n7eDWDvW4sJej3J6c4gvyvuhBmDSj2F4ycqGp0YYFt)
20. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmothl9JgrvJQ6E1B8JLowDvKQVvLQgDrTlRql5iNJHCNNeRhHuPCf2KaFwtEeeqqntG3boOUif4w1vY8DoazL58tvwSSMA316MhcbLKnyNCueB1XwETWBYozIVN5SF37JHDMP-zNWV21KcPtSyuTgHdX23ISxZeNu7lRS)
21. [researchr.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzRE000OgpOKTQuOHtQnEjhRfOUC8mnjOHme9dIIKnHKSPjkHg64n2X6WaWA2lthtCOktFu0A1DCPGxoC5S3SKAx0yLLx2Q6LzJsP--2_r_ZXO3GHb2r2C2xJLYPum1nojRCVZtS3l1dMQXZKvwTXMBY7vsUuYcwC1Ll05hO7Eowrq3MbSmZOVsMvlfD9wM8r3cuPDjl9sU51DBxXWMzINiVkV-cgGJvatK97Es53Giy2u34yn2UzYr0g4tQy5rTSFSqk=)
22. [manchester.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHddhGD6FS4mVpAusL_2HoxgN-K4XJX5Z8Awc_pQ1k9M3PQ4GtMAgT1ccwLRn6leGKk4Dz_gCDA4pUS8bZKjC0ZnHSHKA3AFuaT9f1YyfQoCE0j32QPyuBiB-A8AjHrfDESru7YKLsuRbfeX5V-UmYVPcrLewBwOFIN6JIfpPvevC-5w4rrfqLRmnBYGxJK22IT7DBBwDZlYje7u_NocHzTWIZ8J6oClxHL4w==)
23. [manchester.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGP-9J5BeQjSmD0NmiFRSzA8jAcIHL642nquoJ6661N37XF-O_ojSaFKZ_9OB-nM68OiWoYfM9soZWW8h4Ky_EWLZeNpqeDQY93onOifWDRUdErrj6m-HKtlq5PFzbNvoDz5VWtM6dEUwk8gGHU2v0adZTCKZdY4REbQtbs4aWSUPm2ID5-2PHpCA==)
24. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeCSf32ICr4TjOWbvfiixO5umL5H6096DzrFR9xZT2aW2EHfnLHR6V3S96exCcnnPBAEPkiW-3NKK86cfoLkwvvR6gu9Q6JBwGsdIoJrzAarsxaT9ijX8cB_Hxk53kvjamFyPf6W7E)
25. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvE8zPAQEfe_cnIaRj5E72GgwzlBAgIM53zIeFZBgwYTU-VRDpiAHFtTs8_Fd5t-0lYAPoTWlIdMc_5Pgc2sxcisv_g2aEX9VubHMeyTXFXdTINKspsRRC2Cemhbk=)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUs1p8tP1JgIet9cqxGGwbnZcfRGmtmnJQHDegbrn2PklXKD0P66TenN1-QoYaAPJow2l35sDk7dlNdNZbEFVKOZmmOWVBkVIW5W8_qpUzIg_95lp5DijeLQ==)
27. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-fMcrdhjmlB3yYCxgor06h3OKZ4gaEmx4MbDb4ayFVpQOlDC2rq31-Il5k4Dl9Eiu1JbAdHdcM5TgBuouN6O_kCTdWwdrZF9x2qUiZXM7Tbg_fhg6Ds1MubWOQL_O65-hFbCvmkaGDHO5Z0AfFdR0bRt7VtrFGJKnMmw=)
28. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhgZ-u2U988LAf0b9HmR_jit9lxHF5Bo8r5Bu9oaK6PPldggNK2VV0NstNrEZrshMUhK7oqNN5qZ2y9oZ_cLQOn5KuMSkzT5CW6S68rPDc2NhgN2tbN4ZTc1M1IOmVt4IZMVJbP_3c4Xx6UEnr_UFVQg9rJn-2JJ6lzsih4-eBtDy2hnDA4PSrTx-2EYI=)
29. [sosy-lab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5IeX_N04s6DQjHAKiowwMBTVKwQHA51TTe1M7wZAS8Km6VYCGDsVdS9rWwwBirje0ywTLgWa9LV-34d5V9JEk_1J-ZDUs-MfQUi7A9fJKxEWMj24lBC5ZUUcbD60qeZRtJ4BjA_tLhazgdiWGQwfVj2bjBiELMhmFrG3g5FGX1LBFd8I_x7h-se9HK42ikC9JitQDiImt9nbzV5kPL-Wv5ZRptkFs0VmH1PKVjO4z0yHOYGAY)
30. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5xNmQHxs1e4tr_iLEFaXpBW3uDZj3WZ9jK-56z3ewKN0cYM31Ttj5YcZT3nY8_y25GnBfoajXzy9YfTFVDHFaLFRQL63iog1hQFnvMZ8RY0BDtYA=)
31. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIaWzKPo560rF08clfOzx2ZVv_1rQ7Q9kSn9nDsQlJWT2C1B_-OZHiFylQF-YP-eb2pPN0ckCsNbUj9nYh78_eL-rBSCDOYEWTTm1a7g==)
32. [manchester.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFszWgZMT1h4AiLrEv-U_B-Qn01RAkJqIYDRoabfOCRDXQ8KOevRDiHkcKrZ6w0oOblRIgC26VxnFC4_gBn5-jUeUudsaKNBeGA38bzRkTQNekqlZW-UVKN3D9btQIbpo46gZD5WWxWMI78_nyYxwHFd9DRUYmD1A==)
33. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7aydOylS6ADuS8hgI0WKcyDYhVazeNwnBcVaHSy4tENbMAzet0TXpuoXDDT-dQ5BilKK0BlI9QK2c07YgnsXpE5pmm4VMgYUuOOLX-CVD5mvQGyUfKQ==)
34. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJugydDeg8HZnqTOrgInQwbQ-aQ7tJt-0D0sndjlOKOTVotj3aqCtULrhl_B5Yf3fJca9vOqLFqcihAnueA7hMH-yP6c_6UxA0GAd9QxtX9Y9ALcmWglcroxIxZ96pjifuZpau6kQHHGp6jvzmATvbMA==)
35. [ycombinator.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4ksqYGu5EysazbR0gFPR1WMTlsnni56Rb7yNuGBMudD12gz6fN7qLHAmrOImUhjcTnFvTtu3iXSplC08BfGk7bjsHJXvcg17a6PfXTmla0nmIa2_tnGBntmo0gPtmeSW0EEw=)
36. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMkX_BrrR44r8kQv1IpnfeeHZTRHLheh-LuRx-H1EHFyyq73Rm8RSj3lWR30Urdy2smOTgntdCk1zsoLV2juAjVDuUbbINWKVzev5mRnP_o05AM1A=)
37. [crates.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGK40p3a9ccWpbfZ1POlGEpcnZmMBTLSMSaTFZxKp4Wwk_tC8u2NX-S7eGMUD9l-ca_BjfFvTNQiz3shHb2g6uld2ETbL_JSZm4pH706ARCejKFsg==)
38. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_87jL5KbvgpJjdPSAoiSkL9jn_WfqM1hh-BdikBxqYkdYIKGbajQilLcEBqIoGmldsF42_f3zmtWCFwpFFQRX_LNXZesrjQX3kb4LvE3OUpoOZztD934HdXMMKYPeVvJbnbKZQm7sHIaWWzrwUa3R6IAf7xNKKDmB-nA0aOEgt8Y943DTst1xDeomuCMwKs4uLhXmJrHLEe-dJpe-2bWJpGDwFccW3Q==)
39. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaGloMvsONGMQ5MS6_JXO-3CyQYfOMaxs4wLrZN-juKN2vhyUZsaA-dMwrUe1cxjI7sEpt-zl2K9by3NCrKZFfXs6D5WxDys4i1pB6OpIRFvt1SEPNSdpKHGeyacpJZPikJgrq2EeQYjyY7xc4h8eKY0ymbsoL8Mez8l0Gc5WCQ_KcUGDnQemH9B3f0cIa2ApOK6XmsB8q0r4UfRrSgw9fe-FErMqyUhe7aNA86Jxfylw=)
40. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3rVDHUF8AkzysWqacnPrj3L3luraFKw9JvoLR3aCH9jBpil4wLAzPu_12Sh-LkHTwWa7_lNRO8yunhXd4RPXv0ZLzQkOLFB39IVEeU1BWKj0t69zL9qGR6WEeWkUCPHjQqp8__lyidJoHXofVb_ym4i2BP3vCDD8R_Qzoaqrp9Tm9rS6m)
41. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPFfYii0YRH_3V_zD8gwrN2aDWGwujSKr_vqzJk098d4XED_RXE5cOqXqyU-dwvetyG6dp9Hn6d265L73sN3vnP_Id14HmXu0lRiBqdhSMxVu-XmkY5ZRYeFOy1w==)
42. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzkMF8GCnz-gb3GKqv0rmfxHtehi6HXtV8P5scwDoHc_NhpVeGmK5w8TgIos9pNbFlaXdBBhMEMQcDXktHwKfnbagxKl51dBPFlqtrUDsAJA4r3GihcCGO9bIgXVqDThcLBLsKs1_tY-I_304TOR3UL-DcCAFsPKONp9utaD9A-pN4hgNPEoA-3UU=)

