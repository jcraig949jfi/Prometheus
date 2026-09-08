# Prompt 93: Automated Program Repair and Genetic Improvement

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdjNzJmYXVMV084amdfdU1QMTQ2TThRSRIXYzcyZmF1TFdPOGpnX3VNUDE0Nk04UUk
**Elapsed:** 457s

---

# FRONTIER PRACTITIONER DOSSIER: Automated Program Repair and Genetic Improvement

This report provides an exhaustive, in-depth evaluation of the Automated Program Repair and Genetic Improvement fields as they stand in 2026. The research synthesizes tacit methodological knowledge, foundational history, and the current frontier of machine learning integration. 

The field of automated program repair has undergone a tectonic shift over the last decade, transitioning from search-based evolutionary algorithms to heuristic-driven semantic repair, and currently to Large Language Model agentic systems. However, the foundational problem remains identical across all eras: the test suite is an imperfect proxy for program correctness. This report is written for a computational scientist entering the field, prioritizing reproducible methodologies, unvarnished critiques of legacy systems, and explicit identification of missing infrastructure.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Automated Program Repair in 2026 is fundamentally split between two paradigms that share an evaluation methodology but employ entirely different generation machinery. The original paradigm, which birthed the field, relies on search-based software engineering and genetic programming to mutate abstract syntax trees until a failing test passes [cite: 1, 2]. This paradigm has largely morphed into Genetic Improvement, which uses the same evolutionary machinery not to fix functional bugs, but to optimize non-functional properties like execution time, memory usage, or energy consumption while maintaining semantic equivalence [cite: 3, 4]. The second, currently dominant paradigm replaces evolutionary search with Large Language Models. In this paradigm, a system ingests the bug report, the failing tests, and the repository context, and generates a patch either through a static prompt pipeline or via an autonomous agent operating a terminal [cite: 5, 6]. 

What is SETTLED in this field is that traditional Search-Based Program Repair for functional bugs is a dead end for real-world development. The search space of possible syntactic edits is too large, and the fitness landscape defined by unit tests is too sparse and deceptive. We know definitively that early search-based systems like GenProg generated patches that were overwhelmingly plausible (they passed the test suite) but incorrect (they broke untested functionality or simply deleted the failing code) [cite: 7]. It is also settled that providing tests as the sole specification for program repair is mathematically guaranteed to cause overfitting. Finally, it is settled that Large Language Models possess superior priors for writing correct code compared to random mutation or human-mined templates, making LLMs the undisputed engine for functional patch generation today.

What is CONTESTED is the optimal architecture for deploying LLMs to fix bugs. A massive architectural war is currently live between Agentic and Agentless frameworks. On one side, researchers from Princeton and Stanford advocate for autonomous software agents (such as SWE-agent) that are given a terminal, a Docker container, and the ability to iteratively execute code, read test outputs, and navigate directories to build a mental model of the codebase [cite: 8, 9]. On the other side, researchers argue that complex agents are unnecessary, costly, and prone to infinite loops. They advocate for Agentless systems that use a rigid, hierarchical pipeline: static retrieval for fault localization, batched generation of diffs, and a final deterministic filtering step based on test execution [cite: 5, 6]. The Agentless camp recently demonstrated that a simple pipeline outperforms complex agents at a fraction of the compute cost [cite: 10].

What is OPEN is the problem of repository-level fault localization and correctness verification. When a bug spans multiple files or requires architectural understanding, both static pipelines and autonomous agents fail. Furthermore, the field has yet to solve the oracle problem: how to automatically verify that a plausible patch is actually correct without relying on held-out human tests.

In the last three years, the field was completely absorbed by the generative AI and Large Language Model community. The traditional software engineering venues (ICSE, FSE, ASE) are now saturated with LLM-based repair papers, and AI venues (NeurIPS, ICLR) host the leading benchmarks [cite: 8, 11]. What was lost in this merge was the rigor of formal semantics and the focus on deterministic, provable repair. The field has shifted from asking "Can we synthesize a patch that satisfies these constraints?" to "Can we prompt a model to guess the missing logic?" Genetic Improvement, however, remains a distinct subfield because optimizing non-functional properties requires continuous execution loops and profiling metrics that standard LLMs cannot natively predict without search-based wrappers.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Le Goues, C., Nguyen, T., Forrest, S., and Weimer, W.
2012
GenProg: A Generic Method for Automatic Software Repair
IEEE Transactions on Software Engineering
DOI 10.1109/TSE.2011.104
This is the existence proof for the entire field, demonstrating that genetic programming could automatically patch C programs [cite: 1, 2]. A practitioner must read this to understand the original generate-and-validate loop, the crossover and mutation operators, and the foundational mistake of conflating test suite success with true bug resolution.

Just, R., Jalali, D., and Ernst, M. D.
2014
Defects4J: A Database of Existing Faults to Enable Controlled Testing Studies for Java Programs
International Symposium on Software Testing and Analysis
DOI 10.1145/2610384.2628055
This paper introduced the canonical benchmark for the first decade of APR research, containing real Java bugs with their triggering tests [cite: 12, 13]. You must read this to understand how software engineering benchmarks are constructed, how test execution harnesses are built, and how the field standardizes reproducibility.

Qi, Z., Long, F., Achour, S., and Rinard, M.
2015
An Analysis of Patch Plausibility and Correctness for Generate-and-Validate Patch Generation Systems
International Symposium on Software Testing and Analysis
DOI 10.1145/2771783.2771791
This is the most critical paper in the history of the field. It dismantled the claims of GenProg by proving that the vast majority of its patches were plausible but incorrect, often simply deleting the buggy functionality to bypass failing tests [cite: 7]. You must read this to engrain the distinction between plausible and correct, and to understand the danger of weak test proxies.

Petke, J., Haraldsson, S. O., Harman, M., Langdon, W. B., White, D. R., and Woodward, J. R.
2018
Genetic Improvement of Software: a Comprehensive Survey
IEEE Transactions on Evolutionary Computation
DOI 10.1109/TEVC.2017.2693219
This is the single best survey on Genetic Improvement, explicitly separating it from functional program repair [cite: 3, 4]. It is required reading to understand how metaheuristic search is applied to non-functional properties like execution time and energy, which remains a highly viable technique in 2026.

CURRENT SOURCES

Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., and Narasimhan, K.
2023
SWE-bench: Can Language Models Resolve Real-World GitHub Issues?
International Conference on Learning Representations
arXiv:2310.06770
This paper defines the modern frontier by introducing SWE-bench, the authoritative dataset of Python GitHub issues that evaluates whether LLMs can resolve complex, multi-file bugs [cite: 14, 15]. You must read this to understand the execution-based evaluation framework that replaced Defects4J and the baseline performance of raw LLMs.

Zhang, Y., Ruan, H., Fan, Z., and Roychoudhury, A.
2024
AutoCodeRover: Autonomous Program Improvement
arXiv preprint
arXiv:2404.05427
This paper represents the intersection of traditional software engineering techniques with LLM agents, utilizing abstract syntax tree searches and spectrum-based fault localization to guide the agent [cite: 16, 17]. It is essential for understanding how to provide structural code awareness to language models rather than treating the repository as raw text.

Xia, C. S., Deng, Y., Dunn, S., and Zhang, L.
2024
Agentless: Demystifying LLM-based Software Engineering Agents
arXiv preprint
arXiv:2407.01489
This is a load-bearing critique of the current autonomous agent hype, proving that a rigid, hierarchical prompt pipeline out-performs complex terminal-operating agents at a fraction of the cost [cite: 5, 6]. A practitioner must read this to avoid building unnecessary agentic loops and to understand the state-of-the-art baseline for SWE-bench.

Renzullo, J., and Reiter, P.
2024
Automated Program Repair: Emerging trends pose and expose problems for benchmarks
ACM Computing Surveys
arXiv:2405.05455
This is the best recent survey on the machine learning era of APR, specifically focusing on how the shift to neural models broke traditional evaluation paradigms [cite: 18, 19]. It details the systematic differences between APR benchmarks and standard ML datasets, and the urgent need for standardized correctness reporting.

Liu, S., Liu, F., Li, L., Tan, X., Zhu, Y., Lian, X., and Zhang, L.
2025
An Empirical Study on Failures in Automated Issue Solving
arXiv preprint
arXiv:2506.17208
This paper provides an empirical teardown of the SWE-bench leaderboards, revealing data leakage, weak tests, and the exact architectural choices that separate successful agents from failed ones [cite: 11, 20]. It is vital for understanding the silent saturation and contamination issues in modern LLM benchmarks.

PART 3. SOFTWARE I CAN ACTUALLY RUN

Agentless
https://github.com/OpenAutoCoder/Agentless
Python
MIT Licence
2025
MAINTAINED
This is the current community standard for running a static, non-agentic pipeline to solve GitHub issues using LLMs [cite: 21]. You can run it today on the SWE-bench datasets to replicate state-of-the-art repair metrics using the OpenAI or Anthropic APIs. The major limitation is that the pipeline is highly optimized for the SWE-bench directory structure and task format; adapting it to an arbitrary private repository requires rewriting the localization parsers.

SWE-agent (and mini-swe-agent)
https://github.com/princeton-nlp/SWE-agent
Python
MIT Licence
2025
MAINTAINED
This is the canonical reference implementation of an autonomous software engineering agent that uses a custom agent-computer interface to navigate repositories and edit files [cite: 8, 9]. You can use this to execute experiments where an LLM is given terminal access to a sandboxed environment. The original SWE-agent is effectively superseded by mini-swe-agent, which condenses the logic into a much smaller, more hackable codebase. The primary gotcha is the massive overhead of its backend sandbox, SWE-ReX, which requires building heavy Docker containers for every single repository evaluation.

AutoCodeRover
https://github.com/AutoCodeRoverSG/auto-code-rover
Python
MIT Licence
2024
MAINTAINED
This tool executes an autonomous software engineer that searches codebases via Abstract Syntax Tree APIs rather than raw grep commands, and optionally utilizes spectrum-based fault localization if a test suite is provided [cite: 16, 22]. You can run it locally on live GitHub issues or SWE-bench tasks. Its limitation is its reliance on the exact parsing output of tree-sitter, which can fail silently on severely malformed code, and its fault localization features are useless on repositories that lack a comprehensive pre-existing test suite.

Magpie
https://github.com/bloa/magpie
Python and C++
MIT Licence
2024
MAINTAINED
This is the modern community standard for Genetic Improvement, superseding the older PyGGI framework [cite: 23, 24]. It can be used today to run local search or genetic programming over C, C++, or Java source code to optimize non-functional properties like execution time. It uses srcML to manipulate the code as XML trees. The gotcha is that setting up the fitness function requires writing a highly deterministic external evaluation script, and the target software must be compilable within a fraction of a second to allow for thousands of generational loops. 

Gin (Genetic Improvement in No Time)
https://github.com/gintool/gin
Java
MIT Licence
2023
DORMANT
This is a microframework for the genetic improvement of Java code, capable of handling Gradle and Maven build tools and applying statement-level edits to optimize runtime [cite: 25, 26]. You can run it to replicate Java-specific genetic improvement case studies. While technically functional, it has not seen significant updates in recent years and requires Java 17 and specific Gradle versions, making it brittle to deploy on modern 2026 codebases without manual dependency downgrades.

GenProg
IDENTIFIER UNKNOWN
OCaml and C
IDENTIFIER UNKNOWN
2012
ABANDONED
This is the famous, foundational tool from 2012 that birthed the field [cite: 1, 2, 27]. Do not attempt to run it. The canonical implementation relies on obsolete OCaml toolchains and custom C parsers that fail on any modern C dialect. Published results from the early 2010s cannot be reproduced easily today due to compiler drift. Researchers testing genetic programming baselines today use Magpie instead.

PyGGI
https://github.com/coinse/pyggi
Python
MIT Licence
2019
ABANDONED
An early Python framework for genetic improvement [cite: 28, 29]. It is effectively dead and explicitly superseded by Magpie, which was developed by the same lineage of researchers. Do not use it.

PART 4. DATA AND BENCHMARKS

SWE-bench
https://huggingface.co/datasets/SWE-bench/SWE-bench
2294 Issue-Pull Request pairs
MIT Licence
This is the authoritative benchmark for evaluating LLM-based software engineering agents in 2026 [cite: 15, 30]. It measures the correct fix rate for real-world Python GitHub issues, validated by executing held-out PASS_TO_PASS and FAIL_TO_PASS unit tests. It suffers from known saturation and contamination issues, as many of these public GitHub repositories were included in the pre-training data of frontier LLMs. It also contains tasks with unresolvable descriptions and broken test environments [cite: 10, 31].

SWE-bench Lite
https://huggingface.co/datasets/princeton-nlp/SWE-bench_Lite
300 Issue-Pull Request pairs
MIT Licence
A curated subset of SWE-bench stripped of issues with overly complex, multi-repository edits or vague descriptions [cite: 11, 20]. This is currently the most popular dataset for rapid evaluation of agent architectures because running the full SWE-bench requires prohibitive compute costs. However, it suffers from severe "answer leakage," where hints or direct solutions are present in the issue descriptions [cite: 31]. 

SWE-bench Verified
https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified
500 Issue-Pull Request pairs
MIT Licence
A human-annotated subset built by OpenAI to explicitly remove tasks from the original SWE-bench that were impossible to solve, had broken unit tests, or had misaligned ground-truth patches [cite: 10, 32]. If you are building a new system in 2026, this is the exact and only dataset you should treat as the authoritative measure of correct patch generation capability. 

Defects4J
https://github.com/rjust/defects4j
835 real bugs from 17 Java projects
MIT Licence
This was the historical gold standard for evaluating traditional search-based and early deep learning APR systems [cite: 33, 34]. It provides a high-level interface to access faulty and fixed program versions and their corresponding test suites. While technically sound and highly reproducible, it is largely considered saturated by the field in 2026. Any LLM evaluated on Defects4J is almost certainly overfitting to its pre-training data, as these specific bugs have been parsed and published thousands of times over the last decade. It should be used strictly for baseline testing of non-LLM metaheuristic algorithms.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment in the modern field is the evaluation of Agentless on the SWE-bench Lite dataset. This experiment definitively measures the capability of a static, hierarchical prompt pipeline against complex autonomous agents. 

Software and Version: Agentless v1.5.0
Dataset: SWE-bench Lite (300 tasks)
LLM Endpoint: GPT-4o or Claude 3.5 Sonnet
Compute Cost: Approximately 24 to 36 CPU hours for the Docker-based test execution phase, and roughly 100 to 200 USD in API token costs [cite: 10, 21].

Parameters and Regimes:
The experiment does not require complex seeding because the pipeline relies on the temperature settings of the LLM. The temperature should be set to 0.0 for the greedy localization phase. During the repair phase, generate multi-sampled patches by setting the temperature to 0.8 and sampling exactly n=10 candidate patches per identified edit location. 
The pipeline operates in three distinct phases:
1. Localization: The LLM is given the repository structure and issue description to select target files, then target classes/functions, and finally specific line numbers.
2. Repair: The LLM generates diff-formatted patches for the targeted lines.
3. Validation: The system automatically generates a reproduction test, applies the candidate patches, and runs the pre-existing repository regression tests. The highest-ranked patch that passes the syntax check and regression tests is selected as the final submission.

Expected Result:
You should achieve a Pass@1 resolution rate of approximately 27.33 percent to 32.00 percent, meaning 82 to 96 issues are correctly resolved and pass all held-out evaluation tests [cite: 5, 10]. This number should be compared against the baseline reported in Xia et al., arXiv:2407.01489 [cite: 6].

Three common ways this experiment goes wrong:
1. Docker Environment Failures: The SWE-bench evaluation harness requires building obsolete Python environments from legacy requirements.txt files. These builds frequently fail on modern Linux kernels or due to deprecated apt repositories, causing the validation phase to falsely report a patch as failing. Practitioners must heavily cache the Docker images provided by the SWE-bench maintainers rather than building from scratch.
2. Plausible vs. Correct Misreporting: Practitioners often fail to execute the PASS_TO_PASS tests (the regression tests that verify existing functionality). If you only run the FAIL_TO_PASS tests (the tests that verify the bug is fixed), your pass rate will artificially inflate due to patches that simply delete the feature to suppress the error.
3. API Context Window Truncation: During the localization phase, injecting massive files into the prompt will result in silent context truncation or attention degradation. If the file chunking parameter is set improperly, the LLM will fail to locate the bug, collapsing the rest of the pipeline. 

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

A Language-Agnostic, LSP-Driven Abstract Syntax Tree Mutator
Currently, Genetic Improvement frameworks like Magpie rely on tools like srcML or JavaParser to convert source code into manipulable trees [cite: 23, 25]. These parsers are brittle, language-specific, and frequently fail on modern syntax features. A serious entrant needs to build a generic mutation engine that interfaces directly with the Language Server Protocol (LSP). This tool would take a standardized LSP semantic token tree, apply cross-over or mutation operators, and output syntactically valid code. The hard part is mapping arbitrary edits back to a compilable string without breaking formatting or scope boundaries. Several research groups have hacked together bespoke Python-to-AST mutators privately, signaling a massive gap for a standardized, multi-language tool.

A Headless, Lightweight Execution Sandbox for LLMs
The current standard for evaluating LLM patches (SWE-bench) requires spinning up a heavy Docker container, installing dependencies, and running a massive integration test suite just to verify a five-line diff. This process takes minutes per patch, making iterative, agentic feedback loops unacceptably slow. What must be built is a lightweight, snapshot-based micro-VM (similar to Firecracker) tailored specifically for Python and Java code execution, which can instantiate an environment, inject a patch, run a single test, and return the stdout/stderr in under 100 milliseconds. Building this requires deep systems engineering knowledge to manage memory snapshots and filesystem state.

Automated Correctness Oracles via Test Synthesis
The field relies on human-written held-out tests to judge if a patch is CORRECT rather than just PLAUSIBLE. What does not exist off-the-shelf is a reliable system that automatically synthesizes high-coverage, specification-aligned test cases that can act as an independent correctness oracle. You would need to build a pipeline that feeds the original bug report and repository constraints to an LLM, generates an extensive suite of edge-case tests (xTestCluster approach), executes them against the candidate patch, and filters out patches that overfit [cite: 35]. The hard part is preventing the LLM from hallucinating tests that assert incorrect behavior, thereby rejecting valid patches.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The Collapse of Search-Based Functional Repair
The most famous failed programme in this field is the attempt to use unguided evolutionary algorithms (Genetic Programming) to fix functional software bugs. Early systems like GenProg, RSRepair, and AE claimed to fix hundreds of bugs automatically. However, independent replication and semantic analysis by Qi et al. in 2015 demonstrated that the vast majority of these patches were mathematically equivalent to a single operation: deleting the buggy code [cite: 7, 36]. Because the test suites were incomplete, deleting the functionality caused the failing test to pass without triggering any regression tests. The authors introduced "Kali," a dummy system that only deleted code, and proved it outperformed years of complex genetic programming research. This resulted in the abandonment of purely search-based functional repair in favor of semantic, template-based, and eventually LLM-based repair. 

The Weak Proxy Critique
The standing methodological critique of the entire APR field is the "Weak Proxy" problem. A test suite is a weak proxy for the true specification of a program. If an automated system uses the test suite as its fitness function, it will invariably find a solution that satisfies the tests but violates the unwritten intent of the software (overfitting) [cite: 7]. This critique was partially answered by the community adopting the strict separation of PLAUSIBLE (passes provided tests) and CORRECT (passes held-out evaluation tests or human review). However, the critique has never been truly solved for deployed systems, because in a real-world scenario, the developer does not possess a secret held-out test suite. If the provided tests are weak, the AI will overfit.

The Illusion of Agentic Superiority
A more recent failed claim is the assumption that providing Large Language Models with autonomous feedback loops, terminal execution, and bash access strictly improves their ability to fix bugs. Frameworks built on this premise look impressive but frequently fail to replicate their superiority under controlled conditions. The Agentless paper demonstrated that these complex agents get trapped in infinite bash loops, hallucinate file paths, and waste context windows on command-line errors, ultimately performing worse than a deterministic system that simply provides the LLM with the right files and asks for a diff [cite: 5, 6]. The critique that agents are measuring the efficacy of the prompt engineering rather than the reasoning capability of the model remains largely unanswered.

Data Contamination and Answer Leakage
A standing critique of modern LLM benchmarks like SWE-bench is data contamination. The bugs and pull requests in SWE-bench are drawn from public open-source Python repositories (like Django, SymPy, scikit-learn). The frontier models being evaluated on this benchmark (GPT-4, Claude) were trained on these exact repositories. Claims that LLMs can reason about novel software bugs are continuously undermined by the realization that the models have memorized the ground-truth pull requests. Furthermore, researchers in 2025 discovered that a massive percentage of SWE-bench Lite issues contain "answer leakage," where the issue reporter literally pastes the required fix into the issue description, meaning the agent only has to copy and paste to succeed [cite: 31]. 

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

If I were a well-resourced newcomer in 2026, I would abandon the crowded space of writing better prompts for SWE-bench and focus entirely on the verification and non-functional optimization frontiers.

Rank 1: LLM-Driven xTestCluster for Autonomous Patch Verification
Experiment: Given a candidate patch generated by an LLM, use a separate LLM to generate 100 highly adversarial, edge-case unit tests targeting the modified AST nodes. Execute these tests against both the original code and the patched code to cluster behavioral differences, automatically rejecting patches that fail on expected invariants. 
Why it is feasible now: LLMs are now cheap and fast enough to generate hundreds of compilable unit tests in seconds, and AST-parsing tools allow for precise targeting of modified lines.
What it would measure: The percentage of plausible but incorrect patches that can be autonomously filtered out without requiring a human developer's held-out test suite.
Falsification: The idea is falsified if the LLM-generated tests consistently reject the actual ground-truth human patches (false positives), proving the generated tests are too noisy to act as an oracle.

Rank 2: Multi-Objective Genetic Improvement of GPU Kernels via LLM Mutation
Experiment: Use the Magpie framework to optimize the execution time and power consumption of custom CUDA/C++ kernels. Instead of using random deletion or crossover operators, replace the mutation engine with an LLM instructed to "apply loop unrolling, memory coalescing, or bitwise optimizations." Use a high-speed profiler as the fitness function.
Why it is feasible now: LLMs possess strong priors for low-level performance optimization but cannot run execution loops. Genetic Improvement frameworks possess the execution loops but lack semantic awareness. Combining them is highly viable.
What it would measure: The percentage reduction in execution time or energy consumption compared to maximum compiler optimization flags (-O3).
Falsification: The idea is falsified if the LLM-mutated variants fail to out-perform standard random mutation over a long generational timescale, indicating that the LLM's priors are useless in the highly non-linear fitness landscape of hardware execution.

Rank 3: Repository-Level Fault Localization via Sandboxed Execution Traces
Experiment: Instead of feeding an LLM a static text dump of repository directories to find a bug, build a lightweight trace-collector. Run the failing test, capture the stack trace and variable states at every step, and feed the dynamic execution trace to the LLM to localize the bug.
Why it is feasible now: Context windows (up to 2 million tokens) can now comfortably ingest massive execution traces that previously had to be heuristically summarized.
What it would measure: The absolute precision and recall of identifying the exact faulty file and line number compared to static retrieval methods like BM25 or raw directory browsing.
Falsification: The idea is falsified if the dynamic trace fails to improve localization accuracy over static grep/AST parsing, suggesting that execution state does not provide actionable signal to current transformer architectures.

What will NOT work, and why:
Attempting to build a new autonomous software agent that operates a Linux terminal to fix bugs will not work. The community has exhausted this direction (SWE-agent, AutoCodeRover, OpenHands, etc.). The bottleneck is no longer the agent's ability to type bash commands; the bottleneck is the underlying model's inability to reason across massive, disjointed code architectures without losing context. Adding more complex multi-agent architectures (e.g., "Manager Agent", "Coder Agent", "Reviewer Agent") simply multiplies the hallucination rate and API costs without solving the fundamental reasoning ceiling. Furthermore, attempting to evaluate new repair tools on the original Defects4J dataset will not work, because reviewers will immediately and correctly reject the results due to irreversible pre-training data contamination.

**Sources:**
1. [azregents.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaFI2JzCyiuI2V6PSRZu6jOqUQkxydwNfCT_YUZMnl0qcV_NWaVmJAWcUZfYjRU_YhfCjLntQWROj6pM1AbLQTypF7TSEt6zE_RsoAasXyrASwIOYtYEc4oAvnGrUHkBPc3lZcNl8VzMvvBmVSpMTPHS_jCbGKLUgjGUlFsdVtSjHphU7-Cluk-Ktec75pXYB9ugED6C9eyiVO)
2. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEU3srbJKEXjwJPzpJliYs3uNb7UWxJJnc9lhHXK1GHrNRq3c4QPEjVr_7I4rin9UkjJWVAM9PQaa30NA7X8jZtNPTf1Q_9JlKMIVybTxCm1rtRY2nzzuKmaIcz9R5RKZgYOO6M9WHAtOZYnhZijJWiAE6griLa6X4h5w==)
3. [upenn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdk8ylcD1M2pA9yjemOGVUZA92GqF-zs3I4HflPpLtSYE9B4ZBBATdX1ZoVUHeRCkGaQBQWvWZy6Vq4truU5H-q-QiI6ikqQVB95L3vRNuZvuuoaxKACahoIzL7gOPF1YHF6rf--cj1Ohg2wtdWQ==)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLGJ3rjisnNpzqrBX7j1q4ddc_ezaBLwCs158Osk3tVIoHF7giGyPhpTJLIx05OSf7L_Bh3NMinmNc8VFvwTVJnrh1OP4pUeBH3spW8E_7cKbsYsYf4MkUJ4w0cYJF_VCokMISTQyxQYtD-MtOo4Gh7qmj31a0v1Dl1Zh2JAq6e4kLCG62Nap5UMb-Rw_5lxivNeFFyZxOjZYTCcg25Q==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGDFwI_7iBQ7xOzG1DVcHk8G7BVhLlx6PtOsLIssHWYVv54ZupdeSAxeUnyx6BgNOF00ycTCzEM0UlNethB2YWWxIWq95gfq3K5GKGUyOmmNJD1bSHg6nS)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwnLuauNmavP_aeB3SGv7G-1LSbvFpwpXJ4ji7XN_hwRLREPCgZQkHgSYrEIqOGukXjtzb5KT_ud6q0l6LPfZP1gxRd8qUdonEUo8J--QHX6MNgDQs)
7. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEua5SYOiFYPV7bbp-Xbblf0NJV_-9vTAor-lbM9T0vql9zQbUFzQSH-Yt-Uy1lvccF_KZ8r8KBGELkYxFWcWBO0RihHlfduXhjFN-8kf4F88JG9TsFAaUIPUjcMjHXOpEt6iR3aLVu8M1T)
8. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVoj47b7X9UiWKL36uGoe9Zlx-g1btLi3WmDgCaQW6ZeBiBteci2tx_EUzuI4wVb5m6KziMXHhNZyshheQRzKoWUnDKbVsNAqhgPliu7Ehxa8=)
9. [swe-agent.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFl1ZfPyLWQyYktUhy0BKDptUXxW-RITrbReQRvfeNrU_yx5KHhiy1xHMze4pxh-xLFTYyIzmhvIJjgodRuauvPm1iMhow4Zr-zgfUKznTSllJ)
10. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXjN50_JUGoJ_rl4AW1oetjvTt-C4UW0nve66H5MNhSU-qW2moM-ojxQLtlPkyrMmc8m1_FzevA5Jkl54s7tBVewt6hBDPPYnWuejcms46DuR2se9qG1xHE36UsA==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGo9HAxMWUi8u0PJsjr0tIOrwhGvG6pfWavoe_H_uAnfOIVQ_M_fIwo41OK3GltCt4xmZxwVyNJ6pCltgPuQcZkaHiRBVsFFKhJrlTHyd7o1vXwr9YlmXCm)
12. [washington.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh2lpki8s4RWDKeQ13WINb5wHAHnk7dYVCqHI4EHsO0lmGFsAwPfiKRtlCmqgAqqZ_fokCuHPP48xjTpfvHbcL8qUPpN15sG2XmkwW7VIJaXGVLD_APHpswpGZwc163VAPQsFQGx5hRvNEC40mdgHHuH8I9jMKVlv9GPHK5RLbvlLXZG9oSQ==)
13. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHevKpuXYDDPZeh_Sb5PTZ25sX2v2zbPaKw4nNyJCpeZGwHlW6yEXSdjKk10vwBlc2LLNLubJFSIGc91d3HK2E895A35NxJcrPZaVNWNBO-LyKVVSxaW-wPd1Xwks8ZGmDVKb9-J2fDsUSP3oVx3ngMNMpSLvgD2ShruLrzLv0QvTn9yIdLTjSHLjZOzi6GhcSA7yyE7yxjWbh1QSKroHHKaDbW__jjJWK43iQztzx5sYPzmyATsncO6bz46Mcbv5r2fnDt-w==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfioqszjl8YtnjCRk_Rv9uXK1NO2ypN8dNa7-HsNnRguvQNz6395mSiiU2O_LGR-0myKsjMJFi4C66vRqY-raru8nlpGzBeIy59KC6j7IpWsN-YjZq)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH590_V8UK5TMjK71RtEmeHmlcBWoBrsoktoKjJ_rb5-NXpcPsb-g1MMMv7mhdalatsP0-QSb759mrwQTzMTSUp8OyhZdSOeY0oCUCaUCgIrW6pDjDJ4A==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDrur2dxQmsGF0mECpczSewUEtZxEAlcDilWwRTak76FSSFDC8a0Y6fgPvpZZ6qPqmiRcTG88qRwYRquje-FlOpId8sX_hXQbK1OZmVOzSgpN_yMEP)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtn14hKVIKRGQClN6bjUZ-Y2Zq7XD9zoa9XivvzQpaV_hZleCNX3NA-czmPPPPGxRk89atH0hXQMSEIwxkSjwsX9T4KPmjbWNzVE9sHHycgwklAR9ZhXLh)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUVMBdYuVdS9iCGsamsxnk6pWCeQgiSX50Ce2olXHfAOhaxj1Fxc32ScLLXWVqEwiLiZD_FDETKroSPBgmTzs6OxWrrmThj-_r7tA_MRtWYArZ4pfD32xj)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQh0l0exGAlfdn3dYN7nSnXhAqu3Zzh_pLzov5psu1Xry8lCmwBty2WnsYeuO-c_KQBZc3APVV_-H4m66kFyhFceQMMVZjWJuWsCXsWGf3Qlmvj8Ns)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9CNGSN8raRLQz7hGlV9pvJNfWqIIUbSN_w5BujHRQ-XXdLdrd5k0HZkmRQKjcSxAQ0EAYW3rs9IjxQ4hF_5CchbcPhwtr6Qa__rlNaOLtW0LhjjQkXfJH)
21. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnYXfKGlXYXXA5E6nxBNETXQcaLAxYlt3Qi86xbvEKoKb5hvJI123mr8HZgljqOrt-wLPU0wpbhi914wNhQkkXIqJ9ZchlcvypxJK5kD-Fb7Ps47A10YI5v3NtjeYnMg==)
22. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTJW3DPOTbVLIyai7HP9ZibJrUgEnJG6eFl2Ae6ZYuULe_A-O0dB6eVIdBSVai9ei_Ib1rmuDMoBv2mcraEtqhwACWNrtwM0WDRQ0ti_o25VbhdRbZmFh0_8GpqEb998VoTXRFr_py)
23. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7sN_mOhgZ20-EeZQCNXo9_2T5CAUlDs6ymYnh3VrBpl3G3yYPY1Y55bd5-KSSl2cdaeSBDrhJhXRoI19aHEa3XZm6LjjxNT_wL6MdatueK9GyYg==)
24. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1qaOPU1CycS04w6QWM1oCo1YckRmw10vWmIYMJaSdOJwZQuj-wjISHccaaSDgUPwFsEuqi-6FOApfIXtzO1AUxs4PK3dlXXVTuJ-ShLtr0XeYHA8eXkpVKdMYLTbQUVfqCJyjaK4=)
25. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcyF2SzINp9YyHCcZgL299kaEUNyp_6MKK5N47SQkAMJs1U5i3ytJSHn8qBTEhdrWhkRplPe-pbDEoPKi13zHyGrOVLjWe0ws1al5GJA_JMrGl3Q==)
26. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqF1IcfxE_a9Fbgmu2MpOn70uun-XiGel_mFzeRwXviwpW9yImBzu2UFkG1fNZAxFBenWdo2WrnrSgzXNLggTO-5vPUWGZwQPZraGvsTlllg7Bzul4CJpwKBd-DQ==)
27. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCjxv2jR4piUDeizK9wyrrDh5u9x_n6VWnyEPQoYsVEqmzCtAAstk4Erzwiept903hW0pW8FA6BPCtYj_A17pxM2zD6h3-J5-Hl74b88Mc38RXG3EdSbmUmgBFfy0wlQMbjilmKHNtgXQ=)
28. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGoBGhfjrwywzRS-ZYm-B1yM_t7k-UWirx1Az6anbxCVqoxJHhoc2Rhhl4SZxsCM5aalvBqMxMJHdUlwQFFYY4u13cZbiuH-iMnWb5KcvJRCT43waQ=)
29. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2vjyuTvnke97gyR75wvg7s5ftry8W633e5K5sXyXO7LiryZnh6VxEzSbk5dGEdvtXC3cjHCmbXzOzWZ_eL0xuLFMLOL5Aa3H5X_OnqyCIi8CmYUs=)
30. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcIouxDXKkSmJCsu9JADIn0zY5LYLrm_B2xy805hoqFQAOPUoLARdYhXDN7ZSz4uuDkuoItWu8DTu3HL9mZB71RwgK-Mb56OetvbMuBPiMqB50jZFXZGnA0edKdJgwIZYg2MOcwcZVmg==)
31. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnlMvmSkp6WQaxuGjOLN-RVJIhuXnUAjXqHNho_1GG0QTRqZ8rBWZcQoVwgdadJdqlpaijA19HELeD4ugwoFY_7RdHvdg7IeYqqtzQkVcDG4CJkBU6rh9vVZla_yI=)
32. [openai.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGA5jHbzvS9RjOL7WrX2hK52aQVE_BobNtCQ2BikU1vILcdGI3Kgocgp3R03WfHLHGa0yVckZaSQa5gsjHKKPtG5joOljmcK9lmjM4q9mH_-mKDiFoeWyg4tPjQd4FY2f3YMxOc-dSsqdeO1iX6)
33. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPl_wIuiNGuVvaC7x1gZTY5CdM64hCVG0Nw-ClHdf0Koz6gvwmuvhoSXdU5hgzrKbZtAJAvb51kvey4Wi85fUNcUVrpSaL83eEFhICm3LoU3dxoUrE6Jw=)
34. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEphNc6cAKH0letJYHyjDCVtVE2wv2ljZy69RaENr6Alj75hQfrLQWLGle6Z1pP9mJjL1tPgkFmqQ2OlaSuRHATgdkmGY2Xa2fYAWWxhUqCcOuE8ShxZXjGRIijJA==)
35. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_Dpv4h01M-iEiM2-waQzGWGaezz9nSgt8uO124oXjVUH9InWH1Wf7ISv5k3Ax7Gvjhwn35iIbbsgd4aNjAc0b3p1D6B6HORhNvllrPYBvUfiqKSfN7sPpl851136DPw1jxXqHWdpB)
36. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJn5mi5f648II-IutiTavkSOl_VqKSp8fAZuPammJmBJ1EFuTZ8zkKpZw6U5frn3eWIwCejjCJY7XZ322E9PkGGoJVrFj3hWoN3dhfZOnocyjjHTZ9hbvg-ihUW0PfNc44PWr6j8EgbQGO0U5cfm0=)

