# Prompt 87: Symbolic Execution and Constraint-Based Test Generation

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdFcnFmYXZqbEFaM2lfdU1QajllTjBBYxIXRXJxZmF2amxBWjNpX3VNUGo5ZU4wQWM
**Elapsed:** 364s

---

# FRONTIER PRACTITIONER DOSSIER

## INTRODUCTION AND MECHANISM CORRECTION

The in-silico experimental research programme you are building requires moving past the theoretical descriptions of symbolic execution found in survey papers and dealing directly with the engineering realities of the 2026 frontier. Your baseline understanding of the mechanism is functionally sound, but it contains a critical misattribution regarding how modern systems operate and what they actually trade away. 

You stated that concolic execution flips one branch at a time, which trades completeness for reach. This misses the primary mechanical advantage of concolic execution. Concolic systems trade completeness for reach by concretising unmanageable constraints. When a symbolic execution engine encounters a highly nonlinear mathematical operation, a cryptographic hash, or an unresolved system call, a traditional Satisfiability Modulo Theories solver will hang indefinitely. Concolic execution bypasses this by dropping the symbolic formula for that specific variable and substituting the concrete value observed during the runtime trace. The engine loses the ability to reason about alternative paths through that specific complex function (sacrificing completeness) but successfully moves past the bottleneck to explore deep application logic (achieving reach). 

Furthermore, the operational model you described where the engine asks a constraint solver whether each side is satisfiable at every branch is the architecture of pure symbolic execution. This architecture is effectively dead for large-scale systems software. The frontier is defined by hybrid fuzzing architectures. In a modern setup, a high-speed Coverage-Guided Fuzzer drives the program via concrete inputs millions of times per second. The concolic execution engine lies dormant until the fuzzer gets permanently stuck on a narrow mathematical constraint, such as a magic-value check. The concolic engine is then invoked specifically to solve that localized constraint, passing the satisfying input back to the fuzzer. 

Path explosion and solver intractable states remain the two fundamental obstacles, but the frontier has shifted from trying to solve them mathematically to bypassing them via heuristic orchestration, compiler-level integration, and approximate solving. 

## PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Symbolic execution and constraint-based test generation in 2026 is a mature, highly integrated discipline that has largely been absorbed into the broader field of automated software testing and vulnerability discovery, functioning as the heavy-artillery component of hybrid fuzzing pipelines. Standalone pure symbolic execution is no longer considered a viable research path for whole-program analysis on real-world software. The merge into hybrid fuzzing cost the field its strict mathematical soundness; modern tools deliberately generate incomplete constraints and rely on fast downstream fuzzers to validate whether a generated input actually triggers the desired state. 

What is SETTLED is that Intermediate Representations are an unacceptable performance bottleneck for dynamic symbolic execution. For a decade, engines lifted binary code to intermediate languages like LLVM IR or VEX to simplify constraint generation. It is now settled that the emulation overhead of this lifting dwarfs the time spent in the solver. The field has moved entirely to either direct native-instruction symbolic emulation or ahead-of-time compiler instrumentation where symbolic tracking is baked directly into the binary at compile time. It is also settled that strict soundness is unnecessary; optimistic constraint solving, where complex constraints are simply dropped, yields better practical bug discovery.

What is CONTESTED is the role of Large Language Models in the symbolic execution pipeline, and the necessity of formal SMT solvers. One faction attempts to use LLMs as direct vulnerability discovery engines, prompting them to find bugs or act as solvers. The opposing faction, which currently holds the empirical high ground, argues that LLMs hallucinate constraints and fail at complex pointer arithmetic. This faction asserts that LLMs must only be used as orchestrators to write the highly complex environment harnesses and stubs required to initialize the symbolic engine, leaving the actual path verification to the mathematical solver. Simultaneously, the necessity of heavy solvers like Z3 is highly contested. A growing movement argues that approximate solvers using gradient-descent fuzzing techniques can satisfy path conditions significantly faster than formal SMT solvers, fundamentally challenging the field's reliance on theorem provers.

What is OPEN is fully autonomous environment modeling. The greatest barrier to entry in this field is not path explosion, but state initialization. If you want to symbolically execute a deep network protocol parser, you must first construct a valid memory state, mock the file descriptors, and simulate the network sockets. Doing this without human intervention remains an unsolved, open problem that gates the fully autonomous application of these tools.

## PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL

Cristian Cadar, Daniel Dunbar, and Dawson Engler
2008
KLEE: Unassisted and Automatic Generation of High-Coverage Tests for Complex Systems Programs
OSDI
DOI 10.5555/1855741.1855756
This paper defines modern symbolic execution and establishes the standard methodology for using LLVM bitcode [cite: 1, 2, 3]. You must read this because every subsequent tool in the field measures its baseline coverage against the GNU Coreutils experiment described here.

Nick Stephens, John Grosen, Christopher Salls, Andrew Dutcher, Ruoyu Wang, Jacopo Corbetta, Yan Shoshitaishvili, Christopher Kruegel, and Giovanni Vigna
2016
Driller: Augmenting Fuzzing Through Selective Symbolic Execution
NDSS
DOI 10.14722/ndss.2016.23368
This paper formalized hybrid fuzzing by combining AFL with a concolic engine to bypass magic-value checks [cite: 4, 5, 6]. It is required reading to understand the architectural shift from standalone symbolic execution to fuzzer assistance.

Insu Yun, Sangho Lee, Meng Xu, Yeongjin Jang, and Taesoo Kim
2018
QSYM: A Practical Concolic Execution Engine Tailored for Hybrid Fuzzing
USENIX Security
https://www.usenix.org/conference/usenixsecurity18/presentation/yun
This paper proved that dropping intermediate representations and strict soundness in favour of fast native instruction emulation makes concolic execution scalable [cite: 7, 8]. It changed the engineering standard for how solvers interact with the host environment.

Sebastian Poeplau and Aurelien Francillon
2020
SymCC: Efficient Compiler-based Symbolic Execution
USENIX Security
https://www.usenix.org/conference/usenixsecurity20/presentation/poeplau
This paper shifted the paradigm from interpreting binaries to compiling symbolic tracking directly into the target program, achieving massive speedups over KLEE and QSYM [cite: 9]. It defines the modern performance baseline.

Ahmad Hazimeh, Adrian Herrera, and Mathias Payer
2020
Magma: A Ground-Truth Fuzzing Benchmark
ACM SIGSAC
arXiv:2009.01120
This paper established the definitive ground-truth benchmark by inserting real forward-ported bugs into complex software [cite: 10, 11]. You must know this because it mathematically dismantled the flawed metric of unique crash counts that plagued the field for a decade.

CURRENT

Joshua Bailey and Charles Nicholas
2025
Symbolic Execution in Practice: A Survey of Applications in Vulnerability, Malware, Firmware, and Protocol Analysis
arXiv
arXiv:2508.06643
This is the single best modern survey available, categorizing current heuristic guidance and scope reduction techniques for mitigating path explosion [cite: 12, 13]. 

Zijian Wu, Xianhao Zhang, Meng Li, Yang Liu, Chunmiao Li, et al.
2026
Static Analysis Informed and LLM-Orchestrated Symbolic Execution
arXiv
arXiv:2604.06506
This paper defines the absolute frontier of 2026 by using static analysis to find targets and LLMs to autonomously write the symbolic execution harnesses [cite: 14, 15]. It addresses the massive human-setup bottleneck that prevents symbolic execution from scaling across large codebases.

Gregory Duck, et al.
2025
AutoBug: Large Language Model Powered Symbolic Execution
OOPSLA
arXiv:2505.13452
This paper demonstrates enhancing LLM inference via a path-based decomposition of program analysis tasks without translating into less-expressive formal languages [cite: 16]. It is critical for understanding the neuro-symbolic overlap.

Domenico Borzacchiello, Emilio Coppa, and Camil Demetrescu
2021
Fuzzy-SAT: Approximate Constraint Solving for Concolic Execution
ICSE
arXiv:2102.06580
This paper introduces an approximate solver that uses gradient-descent fuzzing techniques to solve concolic queries, proving that traditional SMT solvers like Z3 are not strictly necessary for all path conditions [cite: 17, 18].

## PART 3. SOFTWARE I CAN ACTUALLY RUN

KLEE
https://github.com/klee/klee
C++
UIUC License
2024
MAINTAINED
KLEE runs dynamic symbolic execution directly on LLVM bitcode and is perfectly suited for replicating foundational coverage experiments [cite: 19, 20]. Its known limitation is that it is heavily tied to specific older LLVM versions and struggles with complex external environment states without extensive manual stubbing. 

SymCC
https://github.com/eurecom-s3/symcc
C++
GPLv3
2024
MAINTAINED
SymCC acts as a compiler wrapper that embeds concolic execution directly into the binary during compilation, resulting in orders of magnitude faster execution than interpreted engines [cite: 21]. Its primary limitation is that it requires full source code access, and the symbolic handling of unsupported libc functions requires manually writing C++ wrappers [cite: 21].

SymQEMU
https://github.com/eurecom-s3/symqemu
C++
GPL
2024
MAINTAINED
This brings SymCC's compilation-based speed to binary-only targets by modifying QEMU's TCG translation layer [cite: 22]. The known limitation is that it ignores the effects of most complex QEMU helpers, meaning complicated x86 floating-point or vector instructions might silently drop symbolic state during execution [cite: 22, 23].

angr
https://github.com/angr/angr
Python
BSD 2-Clause
2024
MAINTAINED
angr provides a comprehensive binary analysis toolkit capable of dynamic symbolic execution across multiple architectures [cite: 24, 25]. The major limitation is the extreme Python execution overhead, which makes it prohibitively slow for deep hybrid fuzzing compared to compiled counterparts like SymCC.

S2E
https://github.com/S2E/s2e
C++
MIT License
2024
MAINTAINED
S2E is a full-system symbolic execution platform based on QEMU that can selectively symbolize hardware, OS kernels, and drivers [cite: 26, 27]. The critical limitation is severe path explosion; if the symbolic boundaries between the kernel and the target application are not perfectly defined by the user, the analysis will stall immediately.

QSYM
https://github.com/sslab-gatech/qsym
C++
Apache 2.0
2023
DORMANT
This is the reference implementation of the first native-instruction hybrid concolic executor [cite: 28]. You should not build upon this today; it is tightly coupled to an obsolete Intel PIN instrumentation version and relies on an outdated Linux kernel version, requiring a pre-built Vagrant virtual machine just to compile [cite: 28, 29]. Its methodology survives, but the software has been superseded by SymCC.

Driller
https://github.com/shellphish/driller
Python and C
BSD 2-Clause
2016
ABANDONED
Driller is the famous originating tool for hybrid fuzzing [cite: 4, 5]. It is effectively dead and unbuildable on modern toolchains. The published results cannot be reproduced with the current release. Practitioners now execute hybrid fuzzing using AFL++ coupled with SymCC or SymQEMU instead.

## PART 4. DATA AND BENCHMARKS

Magma
https://hexhive.epfl.ch/magma/
Approximately 2 MLOC across seven targets
Open Access
Magma is the authoritative ground-truth benchmark for evaluating fuzzers and symbolic execution engines [cite: 10, 30]. It is used to measure true bug discovery by utilizing real forward-ported vulnerabilities inserted into targets like libpng and libtiff, accompanied by lightweight oracles [cite: 11]. It strictly measures bugs reached, triggered, and detected, successfully solving the crash deduplication inflation problem that plagued earlier datasets [cite: 10, 30].

LAVA-M
https://moyix.blogspot.com/2016/06/lava-large-scale-automated.html
Four GNU Coreutils programs
Open Access
LAVA-M is a historically popular but heavily contaminated benchmark suite [cite: 10]. It is used to measure the ability to bypass magic-value checks. The known saturation and contamination problem is that LAVA injected highly artificial, synthetic bugs that do not represent the complex memory states of real vulnerabilities [cite: 10, 31]. Tools that overfit to solve LAVA-M frequently fail to generalize to real-world memory corruption.

OSS-Fuzz and FuzzBench
https://github.com/google/fuzzbench
Dozens of open-source projects
Apache 2.0
FuzzBench is the authoritative evaluation harness provided by Google. It is used to measure code coverage and crash discovery over standardized compute budgets. The known limitation is its reliance on coverage profiles, which have been proven to correlate poorly with the actual discovery of distinct, unique ground-truth bugs [cite: 10].

Cyber Grand Challenge Binaries
https://github.com/trailofbits/cb-multios
Hundreds of synthetic binaries
Open Access
These are popular historical task collections from the 2016 DARPA challenge [cite: 10]. They are known to be completely saturated; modern tools easily solve them. Because they were designed for an archaic operating system and lack standard POSIX environment interactions, solving them does not generalize to modern Linux binaries [cite: 10].

## PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment in this field is the foundational evaluation of KLEE on GNU Coreutils. Reproducing this gives you the exact baseline understanding of path exploration, symbolic environment modeling, and coverage measurement.

Exact software and version: KLEE version 2.2, LLVM 9.0, uClibc, and GNU Coreutils version 6.11 [cite: 20, 32].
Exact dataset: The unpatched GNU Coreutils 6.11 source code. 

Every parameter that has to be set: 
To build the target, compile with gcov support, then separately build the LLVM bitcode version using wllvm [cite: 32]. 
To execute the experiment on a utility like echo, use the exact parameters:
klee --optimize --libc=uclibc --posix-runtime --max-time 3600 ./echo.bc --sym-args 0 2 4 --sym-files 1 8 --sym-stdin 8 --sym-stdout [cite: 33, 34]. 
These arguments limit the symbolic execution to a 3600 second budget, symbolize up to two command-line arguments of up to four bytes each, symbolize one file of up to eight bytes, and symbolize the standard streams.

Replicates and seeding: Run 5 independent replicates per search heuristic. The original experiment utilized a round-robin scheduling of RandomPath and DepthFirstSearch [cite: 35].

Approximate compute cost: Roughly 1 to 2 CPU hours per utility. Executing the entire suite of 89 utilities requires approximately 150 to 200 CPU hours. 

Expected result: KLEE will automatically generate ktest files that, when replayed against the gcov-instrumented native binary, achieve greater than 80 percent line coverage on the coreutils suite, reproducing the published numbers from Cadar, Dunbar, and Engler, 2008 (DOI 10.5555/1855741.1855756) [cite: 3, 36].

The three most common ways people get this experiment wrong:
1. Misplacing the time budget flag. If --max-time is placed after the target bitcode file (e.g., ./echo.bc --max-time 3600), the KLEE command line processor ignores it, and the POSIX runtime passes the flag directly into the target program [cite: 34]. The engine will hang indefinitely instead of terminating.
2. Mismatching the compiler infrastructure. KLEE strictly requires matching the exact LLVM version used to compile the target to bitcode. Building KLEE with LLVM 11 but compiling coreutils with LLVM 9 will result in silent structural failures during execution.
3. Measuring coverage incorrectly. Practitioners frequently read KLEE's internal klee-stats metric, which measures all linked bitcode including the massive uClibc standard library. This results in an artificially low coverage number. You must use the klee-replay tool to drive the generated .ktest files into a natively compiled gcov binary to isolate and measure the true application coverage [cite: 33].

## PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

Component: Autonomous State Initialization and Harness Synthesizer.
What goes in: A pointer to a C/C++ repository, the target function signature, and the associated struct definitions.
What comes out: A compiled C++ test harness that automatically allocates memory for the complex nested structs required by the target function, mocks the global file descriptors or sockets, and inserts the engine-specific API calls (such as klee_make_symbolic) before invoking the target.
The hard part: Program slicing and invariant inference. If you want to symbolically execute a deeply nested network parsing function, simply passing symbolic bytes to it will result in immediate null pointer dereferences because the application context was never initialized. Reconstructing the prerequisites requires tracing the static dataflow backwards to understand exactly what global state must be mocked to bypass initialization checks.
How much work it is: Building a robust, universal static-analysis-to-harness pipeline is roughly 6 to 12 months of intensive engineering for a competent systems programmer. 

This represents the most critical real gap in the field. Every major research group privately writes custom Python scripts, AST parsers, or LLM wrappers to generate these harnesses for their specific evaluation targets [cite: 14, 15]. There is no off-the-shelf, universal harness generator integrated into tools like SymCC or angr. SAILOR approaches this using LLMs, but a deterministic, deterministic graph-based state initializer does not exist.

## PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

FAILED PROGRAMME: Pure Concolic Execution for Full Program Analysis.
Early ambitions that systems like SAGE or Driller could scale linearly to verify whole programs were destroyed by the physical reality of path explosion. Path conditions multiply exponentially inside unrolled loops and deep call graphs. Pure concolic systems invariably suffer state exhaustion in shallow parsing logic. The field attempted to build better search heuristics, but this ultimately failed. The survival of the technique required the pivot to hybrid fuzzing, relying on cheap, native concrete execution to rapidly traverse the shallow code and strictly reserving the solver for isolated constraints.

CORRECTED RESULTS: Crash Count Inflation.
For nearly a decade, papers claimed superiority by reporting the total number of unique crashes found during a campaign. A standing critique, which was eventually proven mathematically by the authors of Magma and FuzzBench, demonstrated that standard deduplication metrics (like stack trace hashing or coverage profiles) are fundamentally flawed [cite: 10, 37]. A single root-cause vulnerability can easily produce hundreds of unique crash hashes. Consequently, tools were optimizing for benchmark artefacts—discovering 300 different paths to trigger the exact same bug—rather than finding distinct vulnerabilities. Modern evaluations completely reject raw crash counts in favour of ground-truth bug injection tracking.

STANDING CRITIQUES:
1. The Intermediate Representation Bottleneck.
A standing critique of dynamic symbolic execution was that translating binary instructions into intermediate representations (like VEX or LLVM IR) before generating constraints accounted for up to 90 percent of total execution time, crippling throughput [cite: 7, 8, 38]. This critique was conclusively answered by QSYM, which extracted constraints directly from native instructions, and later by SymCC, which moved the overhead to compile time [cite: 8, 9]. 

2. The LAVA-M Artefact.
Between 2017 and 2020, symbolic execution tools routinely claimed state-of-the-art status by rapidly solving the LAVA-M benchmark. Critics pointed out that LAVA-M bugs are synthetic magic-value checks (e.g., checking if a 4-byte integer perfectly matches 0xdeadbeef) [cite: 10]. These artificial constructs look nothing like real spatial or temporal memory safety vulnerabilities. The critique asserted that LAVA-M was merely measuring the capability of the SMT solver to perform dictionary lookups, not the engine's bug-finding capability. This critique was never answered by the original benchmark authors, and the field has since deprecated LAVA-M.

3. The SMT Solver Bottleneck.
Z3 and other formal theorem provers struggle immensely with nonlinear arithmetic, complex pointer arithmetic, and string operations. When queries become complex, the solver hangs. While approximation via concrete values is the standard workaround, the reliance on heavy theorem provers remains a standing critique. This is currently being answered by the development of approximate solvers like Fuzzy-SAT, but the debate over dropping mathematical soundness entirely remains highly contested [cite: 17, 39].

## PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

If you are a well-resourced newcomer with compute and engineering capability, you should aim entirely at the neuro-symbolic intersection and compiler-level integration. 

RANK 1: End-to-End LLM-Orchestrated Harness Generation for Hybrid Fuzzing.
Experiment: Construct a pipeline that uses static analysis (such as CodeQL) to extract target function signatures and dependency graphs, feeds these graphs into a modern reasoning LLM to synthesize isolated C++ execution harnesses, compiles them with SymCC, and executes them with AFL++. 
Feasibility: Feasible now due to the massive context windows and advanced code reasoning capabilities of 2025/2026 LLMs, which could not be done reliably prior to this year [cite: 14, 15]. 
What it measures: The reduction in human-hours required to achieve 80 percent coverage on complex, stateful targets like database daemons or network parsers compared to manual harness writing. 
Falsification: If the LLM consistently hallucinates impossible memory invariants that cause the harness to crash before reaching the target logic, the approach is falsified.

RANK 2: Neuro-Symbolic / Approximate Constraint Solving in the Compiler.
Experiment: Write a custom LLVM pass for SymCC that replaces the calls to the Z3 SMT backend with a lightweight, gradient-descent approximate solver (similar to Fuzzy-SAT) compiled directly into the binary's runtime [cite: 9, 18]. 
Feasibility: Feasible now because the architecture of SymCC allows for swappable runtimes, and approximate solving algorithms are mature enough to port into C++ headers. 
What it measures: Total path throughput and execution speedup over standard SymCC-Z3 implementations. 
Falsification: If the approximate solver fails on deeply nested cryptographic invariants, forcing a fallback to a formal solver, the overhead will negate the speedup, falsifying the utility of the inline integration.

RANK 3: Concolic Execution for Firmware Peripherals via LLM Hardware Modeling.
Experiment: Target S2E at a bare-metal firmware binary and use an LLM to automatically generate symbolic Memory-Mapped I/O (MMIO) responses based on hardware datasheets, preventing the engine from crashing during peripheral polling loops.
Feasibility: Feasible now because LLMs can accurately parse hardware specification PDFs to map out register states [cite: 40]. 
What it measures: Code coverage deep within firmware interrupt handlers that previously required physical hardware-in-the-loop testing.
Falsification: If the generated MMIO models lack the necessary temporal timing constraints required by the firmware's real-time operating system, the firmware will panic, failing the experiment.

WHAT WILL NOT WORK:
Using Large Language Models as direct replacements for the symbolic execution engine. Do not attempt to prompt an LLM with source code and ask it to compute the path constraints or generate the test cases directly. This will fail because LLMs are statistical models that hallucinate constraints, lose track of complex pointer arithmetic, and cannot provide mathematical guarantees of satisfiability [cite: 14, 16]. They lack the deterministic state tracking required for memory safety validation. LLMs must remain orchestrators, writing the code that sets up the deterministic engines, rather than acting as the execution engines themselves.

**Sources:**
1. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjpm22ZF3h2ewl6feRs6nZGuTYMJd4looDJmETaMDEWtRRdG_N6WswjCW2cbbrPyDI-HDTY1PsRXqirIoLs7aheZLw4tiDgmDsel6_AESEsc7PphyaYxKWg71bpSQnZo8IrqOdB__RvjiS26wDzq5MmT9HRA-lPWjLrqrY)
2. [abhikrc.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFv9V4UxIfGxnodeL3fajbBo87xyqflRpPHsQwVTYPEIuOuMVYKD-AC7_4MSggOJS_CvWbEYF1vbFG6R_cEMh3rXikB3kb3uxqcS6247-_5NHzRfYE2yZNMkhQXeAbG6HRX)
3. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFp84NiPkMFdXJUwTVDWkZJngszelF-UdU8ZzflvzQ-xvciuJgOlHkkwYwoK42cykGrCBugTXvRLKV1GKx4ZqpxOtkT6Wt8eHmE0eZIa_GsfFfNZX4GwlpX_14I3Rj5uKVTEetV1z4oqJ0InK_qKoiV8W2ybWcZ1c_pgxgcaJLCWSs3QQTAedK1a8oh)
4. [ndss-symposium.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJwRBHKaO3SAI-twSh2jFofioJq9JUVPo3txGvnBJ0r0fbc_oPoEVZjEf21K1VnCv0hy9SLbiltYpb45LnWZvixsTvYAoBa5Nqj6VOhFi4SXexxeiSpXfsBVD2Scchqy52d85dYRUJkpOOudKTbDKjwoq_GiKejfP8JpFowzDc3vnRvTd64ewH9X5M6MENeiFzGMCYJIZFTMtJnxGkLQxwi87eCdy2tpTkMTPlb2gHDFC8fA==)
5. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfa59Bd8f0EZHqIMIdblj59O3lBPoMmg_jdy5GoiI67R5trrb5W2QW7hbiJGNSX3k7t69DwBXBud2gfqIpfnb3LDQVkwMB4RfJF_x3X9JoHrEApS42PytmtVD5p1UID4Qa7HoxKN0hZABb_Sq54qHZddAOqwLn_pgFIVz96mP0O-vRei8ech33C4HVE8CHFsIIf1Sx2A_3Jd-FBi3X9ZxdNuDFusBjRc9cSPuCclCIKND4jkKJp-d5hQ_9SucUaohLn9GRrA==)
6. [elsevierpure.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRRG5TAGSKec5k25EUJxSaXwE8XZkyHDAXh2TjU7v4Jtlf_soVBnSinGUe-0igpZ2NEt-DQQxd-2OI-tx5a347nSF8fpfhY5mvnxnObxLUJ-zlfGLI7K3avHfmlwNxfQanRU6AenmTv073ftwT4B82jzcKKG5bnTSNr5hF0rXjJ2IQKnvyviZiQAluRLy_Zcc2YdbeZMQgk9wThX-Tceo3ghde)
7. [ucr.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmMinH8CfSz3uqfsz4knVftqqWOB8QVWZ6XdvvRohIrVyOp7KlaTP_vjw9TC4cSx3npGiewv2Icjxl6sy7KXxYEbSQ6W-Xm-5zI6une9MtgjTbJs6596ruFUgftp46u4sr2XgQTgTNUIYFCgm5oDkhclkHdhpaI7110rkTyQ==)
8. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFoyQbXDJcdDTTDwExS2Xxrzv8kGsm6vapKS0r6LmyOqZCJiaoBjVKNN7rXRSOGOJZUksE-KpXLIuoSpNb6IlIN7S4fy0hUtJaR03fojvCDFZ1CSn8WtfyOKI_ripxoKQq3L32k0QhSH-SCany9GCMmIL0PdZiqw==)
9. [eurecom.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGJhUAS2Z0AvT5UzrSuLi8nb0KhOczl4jJ0wgWmc_sTHQ9a5K8UoOI4n66sI4mz-qQHgDiW2Siqa5B4ZcGMr8kAjUuakJib2tZEEjLKdbk9wW4RagesMHhXIopdvzFdKWOsdJGs7LJIJz71zPRYdWTGwyh)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUnM54WAklZmIOJnAESK8PxDr8uV0ziNRp5BCuYD7mnxejZwk_tabFFm1T9DuGRDSFohbaYHsTS6fn_yEGoBb5eTXgUC8BgxaU0guIdZAN9XSSGdVLTg==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpfmoIW8TmPDjj8v7SZFnc-Qgx7bSd68YZ0n_IEJX8_KlRwMxIuDldghgnJg3TBpZtATGUm7Oz70_qGBO4LnxGP0xahAYlkwydCzT8EYfYYHKCeRjgOAugnA==)
12. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFF7ox4lHmOWThTdg3v5jVUV9PgnuX3yF9p5oWCkOt-WbOBVjqwXnh3WpsETdzyfA7qwhSlk0_aUYe4AcrG64VWB9GbFT1nrnuA_j-IYBHeW1iEOK1VnKXEW9l3pLv1Gxf8raYpfVVN6Iz_31JzXEGyxdIdyIsgB34tNx7CQ2ofo_SFr4w5fLSNMDgsR05OMDTWebeVV3P4xhSA65FJ2Dqbf1dh3evvKbXBWJ98JDOZVWi7UqbhzKqRCASjIQJ5cSEEnNlK4DZsTjcn)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3t6O-Ne3Srp3MsshR5W99vtX-fwYgHoFzEBlFaDQv_NqWAFiVGJIXvrkOTarIDehqnz7l2xsxlSzas0g72xe6I3NiRS82HT_AMGoMJwqRQOSlpIIUrw==)
14. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDNO7-Runwm-fMtiwYIlDyyaPmwYhbN6x9bc8JTz8BuPkyJP_LGTPaecbh3v3cf8Xlf-dxcOTCXuRfgarQUP8o8jfDneV8KGvewftZQpqKw3Qg6mn71H-afAAsVhg=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2OOAMDUh6lYmE7Mlowytg2uh-luZVzl1ePHWl722IhecU93Nc2Uj0dz249_uJ-0nK_UgdrmtxAmqS7wECqK33XTAu3R5RFjfLbyzFV2N-_DTV37nSYQ==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpjLb34l_mfJZpgGnSLvDYYS-84h3UxZiFaMM1MB7Es1_sBWh2p5rmKwavTGkGNSOsnOCHT4VuM1srO_voz3oNn7GnfKaI58yxU8u6ZbpoRrLXAfrnqg==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsBT1powWvGnkJyDWx3H-4ewGEPB5V2XSGwIIrn29nghiuArKK7UXSgpxk9cN7gZPyd8BCQ-r0IHr6eYUqX7VKJVKASUucQscvh0vmToV4V84B4E16NA==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9ouWxQCXaEDe1aJl-zJrGNgRV0s6zDPpftfg1GcrakFT5Achht4uVPujeZEVp-c-FbUT6_LB1OAN81WoqRB-Qo40iWh_DUipZgQokzXoB2UmT8k8HSwP0uQ==)
19. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOwcnpUnyBXknvRZTVnvnGtehp9gUfq29QucRVrFkWnSA_YzEYCVcbNTD71i-dvCalExK3I5e5Nrq91x8WoCFOwYNvLC4qRccThc2N9HOzlfSE)
20. [klee-se.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHd8WpbaGPQ37zKRsnV_1RzF-SCsbQDjE3nYbaO-IgYfeJegJ2s7wF8F0lwSte5XVbeEIUW_uqoZQvNGKfFkxWCwKuuvl9ExPor79WkiXjJRPuKDvXl3hve1tU7pA==)
21. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHN6eYassum4XI40w0WkW471vG5lO6ql5b8L4VZjUXCwb2l3-1REXgzHCieRHylFvAXcsv0Qzwt-pIxcTJFX-WvPc6vp_xWtjP9hv6iazaM0qbxpzc6MQyQHQ==)
22. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwLnKYnUyoV4zGzmfemRG2JRo_4f0hm69hjfBpbvyHNGEYIy6xn8wYuz8UAJkCADm4yo8UhleRdWuQH1aRym_LTQI6hzc_8OMgbQOeoiGEcqAz3X0nU_pY0T85)
23. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiOo6vUAhYYPrPxIh8ntxj_OgXxS4aA1tG8O3ZyJnSzsFWaJlFHBeY4TYFRTesBlwmJPKo1jljwU1tKFQBMHQVRgJ5pY_S3vlq-MqEJauC0HO7AZq-B8g5FB4M0idkWGDi09B1qw==)
24. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwGA1JLkAUHueptpwj_1rScG3rfoCMf_MENlCVJ_sNVrTqHL_TFnvUAyMy1Qo25BXLMGxcWdN5_ilEjjbZZGAZdFfV6s4amhQBwnYczZ1p1N87)
25. [angr.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-s33vBvAcwHW_a7YnxU9ZyMUWoFZhmu9snnBCfAAmRx30cUu5CAQPWSi8aSdgFT5hzMqHkuOdD9gqY3YerNbwqDYQADZL)
26. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMfqNdlHcW2XsggQbvriwKdrpXdVlxN3X7jvUPa9JA_4eCCyVcoyGfcitCK17CeDhmnceDJYVTWTygsUo4YmGFCVfiJzj4KLuXHVv14WAYfA==)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_os2qgmJbv8BEqHD4QLrWtk85MiT4puS5NMigQ0R3qYAmnmNISz7XCuP4xRRBWQ8r-ORllOMJGcZl3kAE9uuok6RcejlDWTEN9OipEB6OgEv6e6ZZh8FtQRAiVoq-MUP4v6f6OLuZr_wWKE13kC3mYachRW_kf5KUHQxYDWukjmvUSgACIT3gaJNkC1WQRH5DQO8Y5_aqIayGkM-DNWClesP4toZe5lRpvdg=)
28. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQG1k06AJG_FXEFKuKbQlk1IROuODHwSq2eYk4E_8Y2dZjegzdqf6L6iCIXzYIGXJXPNPQhI-0dNWFthPi4xAmSsn8O9asoy0XTIphGrbPPMIH0AmTuDTfP5A=)
29. [gts3.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH52YzOrFI14FXGhT-i_0zx8_VJhiDkeYeD5oveu6i6bss2IJAh7zfvfSznTynqO870uAlu1WpUfcFUy8I3EGSUj9OInS0Ag2tVmuXINBMj70E1LRiJKCyfDraGypBZC7K4mS1NBDTdOOy-BamyBaIOJQ==)
30. [epfl.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGv5A0FhGeGE3wZZ6dr2EZ4gtDM5eL5vwnDB3a4x1_eawiW8rJyVKOeQY2MhqzJlyBF-cPohyrRefiWy0N4pyut-5awnBa42JpaBZW1FhgDK556kI7Tn0iHcGgEwBVAKPm7bjk5iw==)
31. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-hn9es6MqSdCistXJJJMIJZVCyGlN0lGZsNm8an6MgPkfi8JDgvPum0EWUbcoPCA6HklnRBsFaGj8afG2caLFjz8Q8372R-znPKC7tBzlHrJjrfZIYUJd3PCfV0Q0Tuw7ZNCQWjmoNniRDsNse_r_k19vMwRz85wZXg2nbcHyfnTruZpelWrD3Ske8uhs2w==)
32. [klee-se.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHF3_OiTO7S5DcBUy4M248DNkpyQeNVk_QhvVYTx5ZjtZs4NdUw7dL7mMjmcUQD-cHCvAI3AmjWGzahnEns8hoWXm5VCDUVE64EpRomT6e0kCywFHVsNrmeUZLNQoN4Y-2ofiYFA==)
33. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUeLU-nVDYc77fP0csS31VNYOBiaru3zTgY2C3hQsFF3GkPidOg2zGjEyrRhwrPAorjGY9ySYb_K4yRxec1Cz8pTPxd9h_3JBxYdISmwWjzH_zbiTfzEtgLpBIL0vb4JQEKNT2qVFQQNzN3tNCii9M3MqgLeZxHEDLvl5cOEyb62S8nFRtmDLQi_YwSJatE11zPUKSuZKbbBz5mfqxAXWPiEuR6KruW95DKGFxo8C3jnkaK87BoYYYpZlSzFr35CFRmXBDWwmb)
34. [stackoverflow.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHujrl3mGcDMA67DuncwLqJfkeZ-GEbXNYnpq12RZmBS-lO0-8qzmbTRYMBoBtlQWjY-EUv7noztDEwR7p0tpUeZBmfhjT-FNiW92YrZxthOQdVl6XQYalesu-_lbzfzmEkvdxqerei-1JGk6UNfGa4yxpShnw_zUKyoWoIg4LAI6njBHKMl0RS)
35. [ic.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGz-lkuUrcTeVJiPVCx9WRhT8Q1Y3ct6paXJcuHk-ezsEk1PdJqxCCOlzeVG_euyqv091DRVX7aIjV8_TCls00JIe-pPiFJWSMsbm3iO5RAbjsvSmhcDMWBOYayWSfDJSprAQ4RqNWPsW9R0e0=)
36. [dartmouth.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSW8QB4qidTst7OJnT6BFOF6NBNYdNVo3L5-4wveGPXs77iYRy02lNR7Im1MzBtWNhJlZT0GesNtMix3RXxCfy-ZyXHCRBILIC6SCW--FCEvhu7RcYo4SnpaGdeIn6bGvKhEE7IqUxz0F5JfnQZeAuyZRxrpozyaPCHQ2RauaGoD-SvHVYw1eHs6S__QYp9YUT)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJDsp2N_37PiYz23apFvXl6ei_GnnhMzIFtw_14B-nZErA87t6HydwwJaGrY2HqYGccuaLHcbijZ1yLNrvFe9UvBki4Tln4L2Fri8fr_oFypb9CBI6pQ==)
38. [acolyer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHV4xpFxt46DXPRl4bASGlsPZC3qflropowjcAfjhoH81rqHHPyP8PmUn3hNlJSNx-Sop4qtE9HmR-c6pSdfd3REf0gQSrXBTzunXyDQOFbM0nurr22jHpTX1-fKiEls_kOvyy__qeDk4MkkueC9tvrQDvxyGnSG9W66wJDAAvg22MLBooV7Ob7M6mIzpFqxGfA0yo3-cyU-1-nC8FyT_Tn0g==)
39. [urfpublishers.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEitghJvBbsM6KZRoILMmLeMj1-vmbjmcdbdWcYxqGijOBhiQiugJkQ6uXAiJGfOqdtUUX0mPDKOmptHaAdoItwcZJkLgzpH00nXqEXrV2BNmIJFcnkBTJxT6bS5hFvPqQhJ6sJv3knbVxEIRVGBE0n3q_pB-pXGHzOiPUPg9v3JLUF6kXzrxP8KSXoXBYAyDAgHgeeIS7qXTYgPzhmKK1ndGw17HZcL04httD458dGhwI=)
40. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHBHikSK8jCyAt_Ti695KOt_BLnrl3gre77cltMipMXrKnRODM_bViXovR1a_nn2Pxpz_BBZp_S160aTSSM_TtjAAZxHj-Wjbk0j81ciWwLX0bwoQp45bAADDCc_Xxmg==)

