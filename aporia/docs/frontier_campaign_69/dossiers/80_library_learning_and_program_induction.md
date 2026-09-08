# Prompt 80: Library Learning and Program Induction

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdiSEdmYXFPOUE0dmhfdU1QOGJqXzhBcxIXYkhHZmFxTzlBNHZoX3VNUDhial84QXM
**Elapsed:** 335s

---

FRONTIER PRACTITIONER DOSSIER
Field: Library Learning and Program Induction

WHO IS ASKING AND WHY
You are building an in-silico experimental research programme and require the tacit, operational knowledge of the library learning and program induction field as it stands in 2026. Your understanding of the core mechanism is entirely accurate: the field relies on a wake-sleep cycle where a neural policy guides search (wake) and an abstraction phase refactors solutions into new library primitives based on compression (sleep). You are also correct in your critical assessment: the field routinely conflates compression with expressivity. New primitives are judged on Minimum Description Length (MDL) and downstream solve rates, but the community does not systematically audit whether a promoted primitive strictly expands the mathematical closure of the library or merely provides a macro for an already reachable state. The leave-one-out closure depth test you described is a genuine, unaddressed gap in the frontier literature. This report provides the exact reading list, software ecosystem, benchmarks, and experimental recipes needed to build that missing audit and run frontier experiments today.


PART 1. THE FIELD IN 2026, AND ITS FRONTIER

The field of library learning and program induction sits at the intersection of neurosymbolic AI, programming languages, and cognitive science. It operates on the premise that intelligent systems should learn by writing symbolic programs and iteratively building domain-specific languages (DSLs) to compress their experiences. In the last three years, the field has undergone a violent restructuring due to the rise of Large Language Models. Traditionally, the "wake" phase relied on heavily trained neural recognition models proposing primitives for enumerative search. Today, LLMs handle the wake phase by directly proposing programs or acting as search heuristics, shifting the field's focus heavily toward the "sleep" phase: how to efficiently compress, refactor, and document the massive corpora of generated code into reusable abstractions. 

What is SETTLED is the computational mechanism of the sleep phase. The deductive, bottom-up enumerative search used by original systems like DreamCoder to find abstractions has been decisively replaced by top-down, corpus-guided search (via Stitch) and equality saturation over e-graphs (via Babble). It is settled that pure syntactic compression is insufficient; abstractions must account for semantic equivalences (like commutativity) to be optimal. 

What is CONTESTED is the nature of the abstractions themselves. One camp, rooted in classical programming languages, argues that abstractions must be purely symbolic, mathematically verifiable lambdas that optimize exact Minimum Description Length. The opposing camp (driving frameworks like LILO and ReGAL) argues that abstractions must be grounded in natural language to be useful for the LLMs that now dominate the wake phase. There is a live disagreement over whether a library primitive is valuable because it mathematically compresses the search space, or because it aligns with human linguistic priors (e.g., naming a concept "vowel" rather than a disjunction of 265 characters). 

What is OPEN is exactly the structural audit you identified. The field does not formally distinguish between "macros" (which shorten description length but do not expand the reach of the DSL within a bounded depth) and "generators" (which open up entirely new branches of the search space that were previously unreachable). Furthermore, evaluating out-of-distribution generalization remains an open problem. 

If the field is being absorbed, it is being absorbed into the broader discipline of Agentic LLM Workflows and Test-Time Compute. The classical Bayesian Program Learning identity is fading, replaced by "Language Models calling symbolic refactoring engines." What was lost in this merge is the rigorous, domain-general mathematical formulation of inductive logic; the field is becoming highly dependent on the pre-training distributions of commercial LLMs.


PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Ellis, K., Nye, M., Pu, Y., Sosa, F., Tenenbaum, J., Solar-Lezama, A.
Year: 2021
Title: DreamCoder: Bootstrapping inductive program synthesis with wake-sleep library learning
Venue: PLDI
Identifier: arXiv:2006.08381
This is the foundational text of the modern era, defining the wake-sleep architecture and the use of Minimum Description Length for library learning. A practitioner must know this because every subsequent system is either an extension of it or a reaction against its computational bottlenecks.

Authors: Wong, C., Ellis, K., Tenenbaum, J., Andreas, J.
Year: 2021
Title: Leveraging Language to Learn Program Abstractions and Search Heuristics
Venue: ICML
Identifier: arXiv:2106.11053
This paper introduced LAPS, explicitly linking natural language annotations to the wake-sleep cycle. It is vital because it sets the theoretical precedent for using language to guide abstraction discovery, which later LLM-based models rely upon.

CURRENT FRONTIER SOURCES

Authors: Bowers, M., Olausson, T. X., Wong, L., Grand, G., Tenenbaum, J. B., Ellis, K., Solar-Lezama, A.
Year: 2023
Title: Top-Down Synthesis for Library Learning
Venue: POPL
Identifier: arXiv:2211.16605
This paper introduces Stitch, the current algorithmic standard for the sleep phase. It replaces DreamCoder's deductive search with a top-down corpus-guided search, achieving a 1000x speedup, making large-scale library learning computationally tractable.

Authors: Cao, D., Kunkel, R., Nandi, C., Willsey, M., Tatlock, Z., Polikarpova, N.
Year: 2023
Title: babble: Learning Better Abstractions with E-Graphs and Anti-unification
Venue: POPL
Identifier: arXiv:2212.04596
This paper proves that purely syntactic library learning is brittle and introduces Library Learning Modulo Theories (LLMT) using e-graphs. It is required reading for understanding how to compress libraries while respecting mathematical laws like commutativity.

Authors: Grand, G., Wong, L., Bowers, M., Olausson, T. X., Liu, M., Tenenbaum, J. B., Andreas, J.
Year: 2024
Title: LILO: Learning Interpretable Libraries by Compressing and Documenting Code
Venue: ICLR
Identifier: arXiv:2310.19791
LILO defines the 2024-2026 frontier by combining LLM-guided synthesis (wake) with Stitch (sleep) and an AutoDoc module that translates symbolic lambdas into natural language. It demonstrates that naming abstractions dramatically improves the LLM's ability to use them.

Authors: Stengel-Eskin, E., Prasad, A., Bansal, M.
Year: 2024
Title: ReGAL: Refactoring Programs to Discover Generalizable Abstractions
Venue: arXiv
Identifier: arXiv:2401.16467
ReGAL represents the purely LLM-driven approach to library learning, bypassing traditional symbolic compression to have language models iteratively write, verify, and prune helper functions. It is essential for understanding the gradient-free, execution-guided frontier.

Authors: Naik, A., Agrawal, D., Prakam, Mathur, Y., Kapadnis, M., An, Y., Marr, C., Rose, C., Mortensen, D.
Year: 2026
Title: PBEBench: A Multi-Step Programming by Examples Reasoning Benchmark inspired by Historical Linguistics
Venue: ACL
Identifier: arXiv:2505.23126
This is the most critical recent negative result. It introduces an uncontaminated benchmark for sequential inductive reasoning and proves that the best 2026 LLMs (including GPT-5 and open-source 120B models) still fail completely (under 5 percent solve rate) on deep compositional program induction without explicit library learning.

Authors: Zenkner, J., Sesterhenn, T., Bartelt, C.
Year: 2025
Title: To Guide or Not to Guide: Sparse Transductive Guidance in Program Synthesis
Venue: arXiv
Identifier: arXiv:2505.14744
This paper (TIIPS) explicitly discusses the limitations of purely transductive LLM reasoning and utilizes a "leave-one-out" evaluation protocol for execution verification. While not exactly the closure audit you seek, it highlights the methodological shift toward rigorous execution-based evaluation over static generation.


PART 3. SOFTWARE I CAN ACTUALLY RUN

Name: DreamCoder (Canonical Implementation)
URL: https://github.com/ellisk42/ec
Language: OCaml and Python 3.7
Licence: MIT
Year: 2023
Verdict: DORMANT
This is the reference implementation of the wake-sleep algorithm. Today, it can run the classic list processing, text editing, and LOGO graphics experiments. Gotchas: The codebase is notoriously monolithic and brittle. It relies heavily on an ancient version of Singularity (or Docker) to handle the complex IPC between the Python neural network front-end and the OCaml enumerative synthesizer. If you attempt to build it on a modern toolchain without the provided container images, it will fail. Most practitioners do not build on this repo; they extract its datasets and benchmark against its logs.

Name: DreamCoder ARC Fork
URL: https://github.com/mxbi/dreamcoder-arc
Language: Python and OCaml
Licence: MIT
Year: 2024
Verdict: DORMANT
A community fork aimed at applying DreamCoder to the Abstraction and Reasoning Corpus. It includes necessary patches to make the codebase compile after years of dependency rot. If you must run a full DreamCoder pipeline today, start here rather than the canonical repo, but expect hard-coded paths and Singularity configuration headaches.

Name: Stitch
URL: https://github.com/mlb2251/stitch
Language: Rust
Licence: MIT
Year: 2023
Verdict: MAINTAINED
This is the most important piece of software in the field right now. It replaces the sleep phase of DreamCoder. Today, you can feed it a JSON corpus of Lisp-like ASTs, and it will run a top-down branch-and-bound search to return an optimal set of compressed lambda abstractions. Gotchas: It only understands a highly specific Lisp-like lambda calculus format. If your domain is Python or C, you must write a complete Lispification layer (as the Leroy 2026 paper attempted) before Stitch can process it. It is entirely decoupled from the "wake" phase, meaning you must build your own search/synthesis engine to feed it.

Name: Babble
URL: https://github.com/dcao/babble
Language: Rust (built on the egg library)
Licence: MIT
Year: 2023
Verdict: DORMANT
Babble performs library learning modulo theories using e-graphs. It can run experiments demonstrating that semantically equivalent but syntactically different programs can be compressed into a single abstraction. Limitations: You must manually provide the domain-specific equational theory (the rewrite rules). If your rules cause an infinite loop in the e-graph equality saturation, the tool will hang or exhaust memory.

Name: LILO
URL: https://github.com/gabegrand/lilo
Language: Python, Rust, OCaml
Licence: MIT
Year: 2024
Verdict: MAINTAINED
LILO wraps Stitch with LLM calls to perform neurosymbolic library learning. You can run its iterative synthesis and compression loops on the REGEX, CLEVR, and LOGO domains. Gotchas: It heavily wraps the original DreamCoder OCaml binaries for evaluation, inheriting their fragility. Furthermore, it was built around OpenAI's code-davinci-002 and early gpt-3.5 models. Replicating its exact results requires careful modification of its API calls to accommodate 2026 model endpoints, and its prompts are highly tuned to the old Codex behavior.


PART 4. DATA AND BENCHMARKS

Name: DreamCoder Compression Benchmark
URL: https://github.com/mlb2251/compression_benchmark
Size: 27 snapshots across 6 domains
Licence: MIT
Purpose: The authoritative benchmark for the "sleep" phase. It provides pre-extracted snapshots of the intermediate program sets sent to the compressor during successful DreamCoder runs. It is used to measure compression ratio and speed without needing to run the expensive neural search phase. There is no known contamination, but the dataset is saturated: tools like Stitch solve it optimally in seconds.

Name: PBEBench (and PBEBench-Lite)
URL: IDENTIFIER UNKNOWN (Typically released on HuggingFace under the authors' CMU affiliations)
Size: ~1000 dynamically generated instances
Licence: UNCONFIRMED
Purpose: Evaluates multi-step sequential inductive reasoning and program synthesis. Used to measure the failure rates of LLMs on deep compositional tasks. Authoritative because it dynamically generates cascades of string rewrite rules, mathematically guaranteeing zero contamination in LLM pre-training data.

Name: ARC (Abstraction and Reasoning Corpus)
URL: https://github.com/fchollet/ARC
Size: 400 training tasks, 400 evaluation tasks
Licence: Apache 2.0
Purpose: The grand challenge of program induction. It measures the ability to induce core knowledge priors (geometry, topology) from few examples. Caveat: Highly susceptible to overfitting. Many tools solve 40 to 60 tasks by hardcoding primitives that perfectly map to those specific tasks, failing completely on the rest. Do not trust any paper that reports a small bump in ARC score without publishing the exact primitives learned.

Name: CLEVR (Scene Reasoning) and Logo (Graphics)
URL: Contained within the LILO and DreamCoder repositories.
Size: Varies by run (usually hundreds of tasks).
Licence: MIT
Purpose: Standard evaluation domains for measuring whether a system can learn concepts like "draw a polygon" or "filter by color". Caveat: These domains are fully saturated. The true underlying primitives are known, and modern systems easily rediscover them.


PART 5. THE REPRODUCTION RECIPE

The single most reproducible, informative, and structurally isolated experiment in this field is verifying the performance of top-down corpus-guided synthesis against deductive search (Claim 1 from the Stitch 2023 paper). It isolates the library learning component entirely, decoupling it from the noise of neural network training or LLM API drift.

The Recipe:
1. Software: Install Rust 1.63+. Clone Stitch from https://github.com/mlb2251/stitch (checkout commit 9a30d03 or the main branch).
2. Dataset: Clone the DreamCoder Compression Benchmark from https://github.com/mlb2251/compression_benchmark.
3. Parameters: Run Stitch over the benchmark JSONs with max arity set to 3, and the cost metric set to standard AST node count (compression ratio).
4. Execution: Use the provided bash scripts (e.g., make benchmark).
5. Compute Cost: Less than 1 CPU hour on a standard laptop. No GPU required.
6. Expected Result: Stitch will achieve compression ratios equal to or up to 1.5x better than DreamCoder's logs, and it will do so in milliseconds per task compared to DreamCoder's minutes. You are comparing against the baseline numbers published in Figure 11 of Bowers et al. (arXiv:2211.16605).

Three common ways people get this wrong:
1. Format Mismatch: Modifying the AST structures before passing them to Stitch. Stitch expects strict Lisp-like curried lambda calculus. Any deviation in parenthesis parsing silently ruins the pattern matching.
2. Timing Artifacts: Failing to isolate the Rust binary execution time from the Python wrapper startup time when measuring the microsecond-level benchmarks.
3. Timeout Configuration: Leaving the beam search timeout unbounded when testing novel, highly recursive domains, leading to out-of-memory errors rather than graceful early stopping.

What is missing: There is no standardized reproduction recipe for the wake-sleep cycle as a whole that runs reliably under 50 GPU hours. Training the neural recognition model in DreamCoder requires massive parallel CPU sampling (shattering) and GPU training, often failing silently due to RPC timeouts between OCaml and Python.


PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

1. The Leave-One-Out Expressivity Auditor
No tool currently audits library expressivity. To run your desired experiment, you must build a symbolic evaluator with the following interface:
Input: A base DSL, a corpus of learned primitives, and a target depth N.
Output: A rigorous delta of reachable states.
Mechanism: For each learned primitive P, temporarily remove P from the library. Enumerate the exact closure of the remaining library up to AST depth N. Enumerate the closure of the full library up to depth N. Subtract the former from the latter. Group the remaining programs into equivalence classes based on their execution trace on a standard test suite.
Hard part: Combinatorial explosion. Enumerating the closure of a DSL up to depth 5 or 6 produces billions of programs. You will have to build a deferred execution engine using e-graphs (leveraging the egg library in Rust) to compactly represent the closures and perform set subtraction over equivalence classes without materializing the raw ASTs. This is a massive engineering effort (3 to 6 months for a competent systems programmer).

2. Universal Imperative Lispifier
Stitch and DreamCoder require Lisp-like functional ASTs. If you want to run library learning on Python or C, you must write a bidirectional AST translator.
Interface: Input is imperative source code; Output is a curried functional graph with explicit state-passing.
Hard part: Mapping imperative loops and mutable variable scoping into pure lambda abstractions that Stitch can pattern-match, and then translating the compressed lambdas back into idiomatic Python. The Leroy 2026 paper attempted this, but groups continually rebuild private, brittle regex-based parsers because a robust off-the-shelf compiler frontend for library learning does not exist.

3. LLM-Agnostic Execution Verifier
Systems like ReGAL and LILO rely on LLMs outputting executable code and Python's eval() function. A serious entrant needs a sandboxed, deterministic execution environment that captures partial states, timeouts, and memory limits for LLM-generated code, returning structured feedback traces.


PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

Pure Transductive LLM Reasoning Fails on Deep Induction
The most significant recent negative result (evidenced by PBEBench in 2026) is that directly prompting an LLM to predict outputs based on few-shot examples (transduction) fails catastrophically on deep compositional tasks. Approaches that attempted to bypass explicit program synthesis entirely by relying on long chain-of-thought (LCoT) or test-time training crashed below a 5 percent solve rate when the underlying logic required a cascade of 20+ operations. Explicit library learning is mandatory for these domains.

Compression does not equal Abstraction (The Macro Trap)
A standing, largely unanswered critique of the DreamCoder lineage is that MDL-based compression often learns useless, highly specific macro-actions that overfit the training distribution. If the training set requires rotating a square by 90 degrees three times, the system will learn a primitive for "rotate 270 degrees" because it mathematically compresses the current solution corpus. However, this primitive fails to generalize to a test task requiring a 45-degree rotation. The system shortened the path to known targets but did not build a better general-purpose language. Your proposed leave-one-out expressivity test directly attacks this flaw.

Syntactic Pattern Matching Fails on Commutative Domains
Prior to Babble, attempts to scale Stitch-like syntactic pattern matching to mathematical domains (like algebra or physics equations) failed. Stitch could not recognize that (add A B) and (add B A) were the same pattern, leading to an explosion of redundant library primitives. The claim that syntactic library learning is domain-general was corrected; it strictly requires domain-specific equational theories (e-graphs) to succeed in mathematically rich spaces.

The "Wake-Sleep" Misnomer Critique
A methodological critique from the broader machine learning community is that calling this process "wake-sleep" is marketing. It is simply alternating optimization: generating data, then refactoring. Unlike biological sleep, which consolidates and prunes memories, computational sleep phases strictly accumulate primitives, leading to library bloating over thousands of iterations. The field has struggled to implement a reliable "forgetting" mechanism that prunes primitives which are no longer useful without accidentally destroying the dependencies of higher-order abstractions.


PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given your computational resources and the current state of the field, here is what you should build and measure, ranked by impact and feasibility.

1. The Expressivity vs. Compression Audit (The User's Anchor)
Feasibility: High. You have compute and can build the missing e-graph evaluator.
Experiment: Take the pre-computed libraries from the DreamCoder Compression Benchmark. Implement the leave-one-out closure depth test. For every promoted primitive, calculate its "Expressivity Delta" (the fraction of unique functional behaviors at depth N that disappear when the primitive is removed). Plot the Expressivity Delta against the Minimum Description Length (MDL) score that earned the primitive its promotion.
What it measures: The correlation between mathematical compression and true generative expansion.
Falsification: If the experiment shows that 90 percent of promoted primitives have an Expressivity Delta of zero (meaning they are purely syntactic sugar for already reachable states), it falsifies the core premise that MDL-based library learning organically discovers fundamental domain concepts. It would prove the systems are just building caching macros.

2. Pruning via Reachability
Feasibility: Medium. Requires success in Experiment 1.
Experiment: Modify Stitch to use your Expressivity Delta as a regularization term in its branch-and-bound search, penalizing candidate abstractions that compress the corpus but do not expand reachability. Run this modified Stitch in a full wake-sleep loop against a standard LLM-based solver on PBEBench.
What it measures: Whether filtering out "pure macros" prevents the combinatorial explosion of the library and increases the solve rate on out-of-distribution held-out tasks.
Falsification: If the pruned library solves fewer tasks or takes longer to search, it implies that caching macros are actually computationally necessary to overcome the limited search depth of the wake phase, validating the current MDL approach.

3. Hybrid LLM-Guided E-Graph Anti-Unification
Feasibility: Medium to Hard.
Experiment: Combine Babble's e-graph infrastructure with LILO's LLM AutoDoc. Use an LLM to propose domain-specific rewrite rules (equational theories) dynamically based on the task failures, then run equality saturation to compress the library.
What it measures: Whether LLMs are better suited to providing the "rules of the universe" (axioms) rather than searching for specific program solutions.
Falsification: If the LLM proposes unsound rewrite rules that collapse the e-graph into a single equivalence class, the approach fails.

What will NOT work:
Do not attempt to scale the traditional deductive neural-guided search (the original DreamCoder "wake" phase) by throwing GPU compute at it. The combinatorial branching factor of program trees scales super-exponentially. Training a larger neural recognition model to predict which primitive to use next yields rapidly diminishing returns. The frontier has explicitly abandoned scaling the neural recognition model in favor of using off-the-shelf LLMs to propose full program traces, focusing all algorithmic innovation on the symbolic compression (sleep) phase. Focus your compute on evaluating the structures the sleep phase produces.
