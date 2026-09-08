# Prompt 36: Program Synthesis

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdvVlNmYW9fNkZhemlfdU1QbU9lcjhBbxIXb1ZTZmFvXzZGYXppX3VNUG1PZXI4QW8
**Elapsed:** 365s

---

FRONTIER PRACTITIONER DOSSIER
Field: Program Synthesis

To build a rigorous in-silico experimental research programme in Program Synthesis in 2026, you must navigate a field undergoing a violent paradigm shift. You are entering at the exact moment when classical, mathematically guaranteed symbolic methods are colliding with probabilistic, deep-learning-based language models. If you want to run frontier experiments today, you will read the foundational papers that defined the syntax-guided synthesis and CEGIS frameworks, install robust symbolic solvers like cvc5 and Rosette, download the authoritative SyGuS-COMP benchmark suites, reproduce hybrid neurosymbolic search algorithms, and ultimately build the missing infrastructure: tightly coupled, low-latency interfaces between local language model token-generation logits and symbolic SMT solver contexts. At the end of this pipeline, you will measure the absolute boolean correctness of generated programs against logical specifications, strictly separated from the continuous computational costs of wall-clock time and solver iterations. 

Your understanding of the Counterexample-Guided Inductive Synthesis loop is fundamentally accurate but requires one critical update for 2026 practice. You correctly described the adversarial loop between the synthesizer proposing hole values and the verifier hunting for counterexamples. However, standard CEGIS struggles catastrophically with non-trivial constants. A single counterexample often only eliminates one specific candidate program, forcing the synthesizer to naively enumerate all possible integer or floating-point values one by one. The modern correction to your mechanism is CEGIS(T), where T is a first-order theory. In contemporary solvers, the verification phase does not merely return a single counterexample; it communicates with a theory solver using techniques like Fourier-Motzkin variable elimination to prune entire continuous regions of the search space simultaneously (cite: 39, cite: 41). If you build a naive CEGIS loop today, it will hang indefinitely on simple arithmetic bounds. 

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Program synthesis in 2026 is almost entirely defined by Neurosymbolic Programming. The classical era of program synthesis, which relied purely on enumerative search, deductive synthesis, and SMT solving, hit a hard combinatorial wall. Without hand-crafted, highly specific domain-specific languages to constrain the search space, classical solvers could not scale beyond small scripts. Conversely, the deep learning boom produced Large Language Models that can generate vast amounts of code but offer zero formal guarantees of correctness, frequently hallucinating APIs and failing on edge cases. The frontier of this field is the active fusion of these two paradigms: using neural models to guide, bias, or drastically reduce the search space, while retaining the SMT solver and the CEGIS loop as an absolute verification oracle to guarantee the boolean correctness of the final program (cite: 8, cite: 68).

What is SETTLED is the core verification architecture. The CEGIS loop, originally popularized by Armando Solar-Lezama's work on Sketch, remains the gold standard for proving that a synthesized candidate matches a specification over all possible inputs (cite: 2, cite: 40). It is also settled that pure LLM generation without a symbolic verifier is insufficient for formal synthesis tasks. 

What is CONTESTED is the exact architecture of the neurosymbolic integration, specifically the division of labor between the neural network and the symbolic solver. On one side are researchers building systems where the LLM is the primary generator, occasionally asking the SMT solver for feedback or counterexamples to refine its next text prompt (e.g., Proof of Thought frameworks). On the other side are traditional formal methods researchers who use the LLM merely as a statistical heuristic to assign weights to a Probabilistic Context-Free Grammar, passing that weighted grammar to a classical enumerative solver like cvc5 to do the actual heavy lifting (cite: 15, cite: 87). 

What is OPEN is the problem of zero-shot library learning and open-domain generalization. Systems that learn reusable abstractions, like DreamCoder and LILO, still require a human to manually engineer a domain-specific set of base primitives to bootstrap the system (cite: 23, cite: 91). A system that works across arbitrary, unseen domains without significant upfront engineering of the grammar or primitives simply does not exist yet.

If this field appears dormant from the outside, it is because much of the mainstream attention has been absorbed by the broader Agentic AI and LLM Code Generation fields. What was lost in that merge was the rigorous demand for formal correctness. The true program synthesis frontier is maintained by a smaller cohort of practitioners who refuse to abandon the mathematical guarantees of SMT-based verification.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Armando Solar-Lezama, Liviu Tancau, Rastislav Bodik, Sanjit A. Seshia, Vijay A. Saraswat
Year: 2006
Title: Combinatorial Sketching for Finite Programs
Venue: ASPLOS
Identifier: DOI 10.1145/1168857.1168907
This is the genesis of the sketching method and the formalization of the CEGIS algorithm you described (cite: 28, cite: 29). A practitioner must know this because it defines how to compile a partial program and a reference specification into a boolean satisfiability problem.

Authors: Rajeev Alur, Rastislav Bodik, Garvit Juniwal, Milo M. K. Martin, Mukund Raghothaman, Sanjit A. Seshia, Rishabh Singh, Armando Solar-Lezama, Emina Torlak, Abhishek Udupa
Year: 2013
Title: Syntax-Guided Synthesis
Venue: FMCAD
Identifier: DOI 10.1109/FMCAD.2013.6679385
This paper formalized SyGuS, shifting the field by proving that supplementing a logical specification with a syntactic template makes synthesis tractable (cite: 43, cite: 47). It is mandatory reading because it defines the input format and theory constraints used by all modern solvers today.

Authors: Emina Torlak, Rastislav Bodik
Year: 2013
Title: Growing Solver-Aided Languages with Rosette
Venue: Onward!
Identifier: DOI 10.1145/2509578.2509586
This paper introduces the concept of a symbolic virtual machine that lifts concrete language interpreters into symbolic ones automatically (cite: 50, cite: 51). It is essential for understanding how to build new synthesis tools without writing custom SMT encodings from scratch.

Authors: Kevin Ellis, Catherine Wong, Maxwell Nye, Mathias Sable-Meyer, Luc Cary, Lucas Morales, Luke Hewitt, Armando Solar-Lezama, Joshua B. Tenenbaum
Year: 2021
Title: DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep Library Learning
Venue: PLDI
Identifier: arXiv:2006.08381
DreamCoder proved that a synthesis system can improve its own search space over time by learning hierarchical libraries of reusable code concepts (cite: 33, cite: 36). You must read this to understand Version Space Algebras and the limits of purely symbolic compression.

Authors: Swarat Chaudhuri, Kevin Ellis, Oleksandr Polozov, Rishabh Singh, Armando Solar-Lezama, Yisong Yue
Year: 2021
Title: Neurosymbolic Programming
Venue: Foundations and Trends in Programming Languages
Identifier: DOI 10.1561/2500000049
This is the single best survey in the field. It provides the standard vocabulary for the three axes of synthesis: intent, search space, and search algorithm, bridging deep learning and formal methods (cite: 68, cite: 70).

CURRENT SOURCES

Authors: Gabriel Grand, Lionel Wong, Matthew Bowers, Theo X. Olausson, Muxin Liu, Joshua B. Tenenbaum, Jacob Andreas
Year: 2024
Title: LILO: Learning Interpretable Libraries by Compressing and Documenting Code
Venue: ICLR
Identifier: arXiv:2310.19791
LILO replaces DreamCoder's expensive enumerative compression with a combination of branch-and-bound search and LLM-guided documentation (cite: 91, cite: 94). It is critical for showing how auto-documentation allows an LLM to effectively use symbolically compressed mathematical abstractions.

Authors: Yixuan Li, Julian Parsert, Elizabeth Polgreen
Year: 2024
Title: Guiding Enumerative Program Synthesis with Large Language Models
Venue: CAV
Identifier: arXiv:2403.03997
This paper demonstrates that pure LLMs fail at strict formal synthesis, and proposes integrating an LLM to dynamically update the weights of a Probabilistic Context-Free Grammar guiding an enumerative solver (cite: 87, cite: 89). This is the exact blueprint for modern competitive solver design.

Authors: Muhammad A. A. Pirzada, Julian Parsert, Weiqi Wang, Lucas C. Cordeiro
Year: 2026
Title: VerIbmc: LLM-based Generation of Weakest Preconditions and Precise Array Invariants
Venue: arXiv
Identifier: arXiv:2606.16886
This represents the absolute cutting edge of privacy-preserving, local neurosymbolic synthesis using open-weight models (7B to 120B parameters) to synthesize loop invariants without expensive cloud APIs (cite: 72, cite: 73).

Authors: Gabriel Grand, Valerio Pepe, Jacob Andreas, Joshua B. Tenenbaum
Year: 2024
Title: Loose LIPS Sink Ships: Asking Questions in Battleship with Language-Informed Program Sampling
Venue: CogSci
Identifier: arXiv:2402.19471
This paper details how to formulate a Monte Carlo search that samples candidate questions from an LLM prior and computes Expected Information Gain via symbolic execution (cite: 81, cite: 82). It exposes the grounding failures of pure LLMs and how symbolic world models fix them.

PART 3. SOFTWARE I CAN ACTUALLY RUN

cvc5
URL: https://github.com/cvc5/cvc5
Language: C++
Licence: BSD 3-Clause
Year: 2025
Status: MAINTAINED
This is the community standard SMT solver and the engine behind most modern SyGuS experiments. It natively supports syntax-guided synthesis, strings, bit-vectors, and finite fields (cite: 58, cite: 60). You can run authoritative enumerative synthesis experiments directly via its command line using SyGuS-IF format files. Its known limitation is that while it is incredibly fast for pure logic, integrating it deeply into Python-based machine learning loops requires traversing heavy API bindings, which bottlenecks neurosymbolic research.

Rosette
URL: https://github.com/emina/rosette
Language: Racket
Licence: MIT
Year: 2023
Status: MAINTAINED
Rosette is the preeminent tool for building new solver-aided languages (cite: 6, cite: 7). You write an interpreter for your domain in Racket, and Rosette automatically compiles your interpreter and your sketch into SMT constraints. You can run custom DSL synthesis experiments today. The primary gotcha is that debugging solver bottlenecks in Rosette is notoriously difficult because the symbolic evaluation unrolls the interpreter in ways that obscure the origin of the constraints.

DreamCoder
URL: https://github.com/ellisk42/ec
Language: OCaml and Python
Licence: MIT
Year: 2021
Status: DORMANT
DreamCoder is famous, historically vital, and highly fragile to run. You can theoretically run the List and Text domain bootstrapping experiments. However, it requires a highly specific two-stage Singularity container build to manage conflicting Python and OCaml dependencies (cite: 54, cite: 55). The known limitation is severe memory leaking during the OCaml enumerative Wake phase; researchers frequently have to write external bash scripts to kill and restart the process during long training runs. 

Sketch
URL: https://github.com/asolarlez/sketch-backend
Language: C++ and Java
Licence: MIT / GPL
Year: 2020
Status: DORMANT
This is the canonical implementation of the mechanism you described (cite: 4, cite: 5). It is effectively dead for new research. The build system is broken on modern toolchains; attempting to compile it often requires downgrading to gcc 4.3 or 4.5 or relying on pre-compiled jars that obscure the backend (cite: 5, cite: 64). Do not attempt to use this for new experiments; practitioners today use cvc5 or Rosette to achieve the exact same sketching mechanism.

PART 4. DATA AND BENCHMARKS

SyGuS-COMP Benchmark Suite
URL: https://sygus.org/
Size: Thousands of formal synthesis tasks.
Licence: Open access (various open source licences per file).
This is the authoritative benchmark for the field (cite: 18, cite: 21). It is divided into tracks: Linear Integer Arithmetic, Bit Vectors, Strings, and Invariants. It is used to measure pure formal synthesis capability. There is no known data contamination with LLMs because the problems are represented in highly specific SyGuS-IF Lisp-like syntax that varies from standard code corpora, though recent LLMs have seen some of it. It measures absolute boolean correctness.

DreamCoder Domains (List, Text, LOGO)
URL: Provided within the ellisk42/ec repository.
Size: Hundreds of tasks per domain.
Licence: MIT.
These are popular collections of small inductive programming tasks used to measure library learning and hierarchical abstraction. They are heavily saturated; solving the List domain is now considered a baseline sanity check rather than a frontier result. They measure the ability of a system to compress solutions into a learned DSL.

Abstraction and Reasoning Corpus (ARC)
URL: https://github.com/fchollet/ARC
Size: 400 training, 400 evaluation tasks.
Licence: Apache 2.0.
ARC is massively popular but problematic. It was designed to measure fluid intelligence via grid transformations. Many program synthesis papers attempt to use it, but ARC is known to elicit highly brittle, overfitted DSLs. If a synthesis paper claims to solve ARC, it usually means the authors hand-engineered a massive library of grid-transformation primitives that do not generalize beyond the specific benchmark (cite: 54).

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment in the 2026 frontier is the execution of a Probabilistic Context-Free Grammar guided enumerative synthesizer on the SyGuS benchmarks, as detailed by Li, Parsert, and Polgreen in 2024 (cite: 87, cite: 89). This experiment separates the LLM from the solver, proving the efficacy of neurosymbolic guidance.

Exact Software: cvc5 version 1.1.0. A local Python script interfacing with an open-weight LLM (e.g., Llama-3 8B or DeepSeek-Coder).
Exact Dataset: The SyGuS-COMP 2019 Linear Integer Arithmetic (LIA) and String tracks.
Parameters:
- Solver timeout: 100 seconds per task.
- LLM prompt temperature: 0.2.
- Enumerator grammar depth limit: 6.
- Number of complete synthesis attempts per benchmark before updating the pCFG: 6.
Replicates and Seeding: 5 independent runs with fixed random seeds for the LLM sampling.
Compute Cost: Approximately 10 to 20 GPU hours on a single A100 or RTX 4090 for the LLM generation, plus 50 CPU hours for the cvc5 enumerative search.
Expected Result: The LLM-guided cvc5 should solve approximately 20 to 30 more problems on the unseen test set than cvc5 running in default blind enumeration mode within the 100-second timeout.
Citation: Li, Parsert, Polgreen (2024), "Guiding Enumerative Program Synthesis with Large Language Models" (arXiv:2403.03997).

The three most common ways people get this experiment wrong:
1. Conflating verification time with generation time. The wall clock time must pause when the LLM is queried if you are measuring solver efficiency, but must run continuously if you are measuring end-to-end system viability.
2. Prompting the LLM to output SyGuS-IF directly. LLMs are poor at this. You must prompt the LLM in Python or standard Lisp, and write a deterministic post-processor to translate the LLM's AST into the precise SyGuS-IF required by cvc5, or the solver will simply reject the syntax.
3. Failing to extract partial grammars. When the LLM fails to synthesize the full program, practitioners often throw away the text. The correct method is to parse the failed program, extract the sub-trees, and increase the statistical weight of those specific syntax rules in the cvc5 pCFG before restarting the enumerator.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

The most glaring missing component in the field—which several groups are currently trying to rebuild privately—is a low-latency, tightly coupled memory interface between an LLM's KV-cache and an SMT solver's context state. 

Currently, neurosymbolic synthesis operates via string passing. An LLM generates a complete program string; the string is parsed into an AST; the AST is translated to SMT-LIB; cvc5 evaluates it, finds a counterexample, and returns a text string explaining the failure; the LLM takes the text string and generates from scratch. This takes seconds per iteration.

What a serious entrant has to write themselves is a Grammar-Aligned Decoding (GAD) bridge (cite: 88). 
Interface Input: The current partially generated sequence of tokens, the current SAT context from the solver, and the active Context-Free Grammar.
Interface Output: A masked logits tensor for the next token.
The Hard Part: You must write a C++ or Rust orchestrator that pauses the LLM generation at every logical branch, queries the SMT solver to check if the current partial AST is already unsatisfiable (e.g., passing a string into an integer parameter), and zeroes out the logits of any token that violates the symbolic constraints before the LLM samples the next token. 
Workload: This is a heavy systems-engineering task requiring deep knowledge of PyTorch/vLLM internals and the C++ API of cvc5. It is approximately 4 to 6 months of work for a competent computational scientist.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

What did not work: Pure End-to-End Neural Synthesis for formal guarantees. Initial excitement around models like Codex and early GPT-4 suggested that LLMs could simply learn to write correct code in one shot. This failed to replicate in formal domains. LLMs predict likely code, not verified code. When tested on strict logical specifications, pure LLMs hallucinate variables, invent non-existent APIs, and fail silently on out-of-distribution edge cases (cite: 23, cite: 24). 

Failed programmes: The attempt to use classical synthesis (like pure Sketch) without domain knowledge. In the 2010s, the hope was that hardware scaling would allow exhaustive search to eventually synthesize large programs from scratch. This was proven false; combinatorial explosion halts unguided enumerative search completely at AST depths of 5 or 6 (cite: 17, cite: 89).

Standing Critiques:
1. The "Overfitted DSL" Critique: Critics point out that systems like DreamCoder perform well only because the human researchers spent months hand-crafting the base primitives to exactly match the evaluation domain. If the human does the hard abstraction work implicitly, the synthesizer is just doing simple combinatorial assembly. This critique has been partially answered by systems like LILO, which attempt to extract libraries automatically, but it remains a standing issue because LILO still requires initial human primitives.
2. The "Benchmark Memorization" Critique: Since LLMs are trained on GitHub and arXiv, they have likely memorized the standard SyGuS and ARC benchmarks. When an LLM solves a synthesis task today, we do not know if it is generalizing or reciting. This critique has never been fully answered; the field relies on generating entirely synthetic, zero-day constraints to test true reasoning, but standardizing these dynamic benchmarks is incredibly difficult.
3. The "Constant Enumeration" Critique in CEGIS: As noted in the introduction, standard CEGIS fails when synthesizing programs that require specific "magic numbers" or non-trivial constants (cite: 39). The verification oracle provides a concrete counterexample, which eliminates only one specific wrong constant, causing the loop to run indefinitely. This critique was answered by the development of CEGIS(T), but implementing theory-specific solvers for every domain remains a massive engineering bottleneck.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the compute, the coding capability, and the landscape, a well-resourced newcomer should aim exclusively at tight logic-logit integration and local, privacy-preserving synthesis. Rank of specific experiments:

1. The Interleaved Node-Expansion Experiment
Feasible now because: Open-weight models (Llama-3, DeepSeek) can be run locally and their inference engines modified at the CUDA/C++ level, which was impossible when the field relied on closed OpenAI APIs.
What it would measure: Synthesis time and solver iterations when the LLM is queried not for a whole program, but for a single AST node expansion within the cvc5 enumerative search tree.
Falsification: If this tightly coupled system uses more wall clock time than the standard prompt-parse-verify string-passing loop due to IPC overhead, the idea of inline symbolic decoding is falsified.

2. Zero-Shot DSL Extraction from Raw Codebases
Feasible now because: LLMs possess enough semantic understanding to cluster large codebases without executing them.
What it would measure: The solved boolean percentage on SyGuS benchmarks using a DSL that was entirely generated by an LLM reading unstructured Python repositories, compared to a DSL hand-crafted by humans.
Falsification: If the LLM-generated DSL fails to compress the search space enough to solve any benchmark within the iteration cap, the idea that LLMs can automatically bootstrap synthesis languages is falsified.

3. Privacy-Preserving CEGIS on Single Nodes
Feasible now because: High-memory single machines can host 70B parameter models alongside heavy symbolic verification tools (cite: 72).
What it would measure: The iteration cap and wall clock time required to synthesize exact array invariants for C code using only local compute.
Falsification: If a local 70B model combined with ESBMC or cvc5 cannot match the boolean solved rate of a closed API (like GPT-4), then local neurosymbolic synthesis remains commercially unviable.

What will NOT work:
Attempting to fine-tune an LLM purely on SyGuS problems to make it a "better synthesizer." This is a trap many newcomers fall into. You cannot solve the combinatorial explosion of formal logic by simply adjusting neural weights. The model will overfit the training syntax, and because neural networks lack explicit backtracking mechanisms, it will still confidently output structurally invalid code on novel test specifications. Do not build better models; build better interfaces between existing models and symbolic solvers.
