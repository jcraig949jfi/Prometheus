# Prompt 35: Counterexample-Guided Inductive Synthesis

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc4VktmYXJxbUlxYTNfUFVQMVozMnlBSRIXOFZLZmFycW1JcWEzX1BVUDFaMzJ5QUk
**Elapsed:** 425s

---

# FRONTIER PRACTITIONER DOSSIER: Counterexample-Guided Inductive Synthesis

Your understanding of Counterexample-Guided Inductive Synthesis is structurally precise for the classical formulation of the method, originating with Solar-Lezama's Sketch system and standardized by the SyGuS (Syntax-Guided Synthesis) community. However, for a practitioner entering the field in 2026, your description is outdated in two critical respects. 

First, the "sketch" (a program with holes) is rarely written manually by a programmer at the modern frontier. It is now typically generated dynamically by a fault-localization algorithm (such as MaxSAT) or synthesized from natural language by a Large Language Model. Second, the "verifier" is no longer strictly confined to a SAT or SMT solver checking a formal specification over all infinite inputs. Because constructing complete formal specifications is prohibitively expensive, the frontier has expanded the definition of a verifier. Modern verifiers often consist of bounded execution engines, learned neural models evaluating execution traces, or automated consistency checkers that cross-reference natural language docstrings with partial mathematical annotations. The essential monotonic accumulation of hardness remains, but the agents proposing and verifying have fundamentally shifted from pure symbolic logic to neurosymbolic ensembles.

The following dossier provides a comprehensive, executable roadmap for running frontier experiments in this discipline today.

## PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Counterexample-Guided Inductive Synthesis is an algorithmic framework that alternates between synthesizing a candidate solution over a finite set of examples and employing a verifier to either certify the candidate globally or return a new counterexample that exposes its inadequacy [cite: 1]. In 2026, the field has bifurcated. The classical SMT-based approach (SyGuS) has reached a high level of maturity but faces harsh scalability limits. Consequently, the field's frontier has shifted heavily toward neurosymbolic CEGIS, where Large Language Models act as the inductive synthesizer (generating candidates) and formal methods, execution engines, or auxiliary neural models act as the verification oracle [cite: 2, 3, 4].

What is SETTLED is the theoretical convergence and oracle complexity of classical CEGIS. For finite domains or constrained grammars, the loop is mathematically guaranteed to terminate either with a certified solution or a proof of unrealizability [cite: 1]. Furthermore, the integration of theory solvers directly into the CEGIS loop to handle non-trivial constants without blind enumeration is effectively solved [cite: 5].

What is CONTESTED is the epistemological soundness of the verifier in the era of generative AI. One side of the field argues that LLMs can act as components of the verifier by checking consistency between code, documentation, and annotations—a concept known as the "Clover paradigm" [cite: 4, 6]. The opposing side argues that neural verifiers inherently suffer from blind spots, high self-pass rates on incorrect code, and hallucinated proofs, insisting that only deterministic execution or SMT-based formal methods can act as a sound oracle [cite: 7]. 

What is OPEN is the pervasive problem of "specification overfitting." As the grammar of allowable programs becomes more expressive—or as the synthesizer is replaced by an unbounded LLM—the synthesizer frequently finds "spurious" programs that satisfy all accumulated counterexamples but fail the global specification [cite: 8, 9]. Overcoming this combinatorial explosion of spurious candidates without destroying the efficiency of the search remains the field's primary mathematical hurdle [cite: 10].

If you are looking for pure enumerative search, that subfield is largely dormant, having been absorbed into neurosymbolic program synthesis. What was lost in this merge is the absolute guarantee of completeness; LLM-driven synthesis sacrifices the exhaustive search of a grammar space in exchange for traversing massive, structurally complex program spaces using probabilistic human priors.

## PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Armando Solar-Lezama
Year: 2008
Title: Program Synthesis by Sketching
Venue: UC Berkeley (Ph.D. Dissertation)
Identifier: IDENTIFIER UNKNOWN
This is the genesis of the CEGIS loop as applied to partial programs. A practitioner must read the early chapters to understand how the inductive synthesis query and the verification query are encoded as interacting SAT problems.

Authors: Rajeev Alur, Rastislav Bodik, Garvit Juniwal, Milo M. K. Martin, Mukund Raghothaman, Sanjit A. Seshia, Rishabh Singh, Armando Solar-Lezama, Emina Torlak, Abhishek Udupa
Year: 2013
Title: Syntax-Guided Synthesis
Venue: FMCAD
Identifier: DOI 10.1109/FMCAD.2013.6679385
This paper formalized the SyGuS standard, defining the modern interface between synthesizers and verifiers. It is required reading to understand the benchmarks and parsing infrastructure the community relies on today.

Authors: Saswat Padhi, Todd Millstein, Aditya Nori, Rahul Sharma
Year: 2019
Title: Overfitting in Synthesis: Theory and Practice
Venue: CAV
Identifier: arXiv:1905.07457
This paper proves the No Free Lunch theorems for SyGuS, demonstrating that increasing the expressiveness of the synthesizer's grammar directly degrades performance due to overfitting on finite counterexamples [cite: 8, 9]. It is the most important theoretical critique of the CEGIS loop.

Authors: Emina Torlak, Rastislav Bodik
Year: 2013
Title: Growing Solver-Aided Languages with Rosette
Venue: Onward!
Identifier: DOI 10.1145/2509578.2509586
Defines the architecture of Rosette, the premier framework for building domain-specific CEGIS tools by lifting interpreter execution into SMT constraints [cite: 11, 12].

CURRENT SOURCES (2023-2026)

Authors: Pedro Orvalho, Mikolas Janota, Vasco Manquinho
Year: 2025
Title: Counterexample Guided Program Repair Using Zero-Shot Learning and MaxSAT-based Fault Localization
Venue: AAAI
Identifier: arXiv:2502.07786
Defines the modern neurosymbolic frontier. The authors use a formal MaxSAT solver to identify the minimal buggy lines in a program, replace them with holes to create a sketch, and use an LLM inside the CEGIS loop to synthesize the missing code against a test suite [cite: 2, 13]. 

Authors: Chuyue Sun, Ying Sheng, Oded Padon, Clark Barrett
Year: 2024
Title: Clover: Closed-Loop Verifiable Code Generation
Venue: SAIV
Identifier: arXiv:2310.17807
Introduces a paradigm shift where the verifier is an automated consistency checker integrating LLMs and formal tools (Dafny) to ensure code, docstrings, and formal annotations logically align [cite: 4]. It challenges the assumption that the specification must be written manually prior to synthesis.

Authors: Ansong Ni, Jianpeng Cheng, Wei Chen, Huaixiu Zheng, Rui Zhang, Xi Victoria Lin, Sida I. Wang
Year: 2023
Title: LEVER: Learning to Verify Language-to-Code Generation with Execution
Venue: ICML
Identifier: arXiv:2302.08468
Demonstrates replacing the traditional SMT verifier with a learned neural verifier that evaluates execution results (data types, value ranges) to accept or reject LLM-generated code [cite: 3, 14].

Authors: Alessandro Abate, Haniel Barbosa, Clark Barrett, Cristina David, Pascal Kesseli, Daniel Kroening, Elizabeth Polgreen, Andrew Reynolds, Cesare Tinelli
Year: 2023
Title: Synthesising Programs with Non-trivial Constants
Venue: Journal of Automated Reasoning
Identifier: DOI 10.1007/s10817-023-09664-4
Introduces CEGIS(T), an architecture that embeds a first-order theory solver inside the CEGIS loop to handle the synthesis of complex numerical constants without triggering combinatorial enumeration [cite: 5, 15].

## PART 3. SOFTWARE I CAN ACTUALLY RUN

cvc5
https://cvc5.github.io/
C++ (Rust bindings available)
BSD License
2026
MAINTAINED
This is the community standard for classical SyGuS and SMT verification. It is the successor to CVC4 and contains highly optimized, built-in SyGuS enumerators and theory solvers [cite: 16]. It is used to run formal verification experiments and baseline CEGIS loops. Gotcha: Compiling from source requires modern GCC/Clang; the Rust bindings (cvc5-rs) can be fragile regarding static linking paths, so most practitioners use the precompiled binaries or C++ API directly [cite: 17, 18]. 

Rosette
https://emina.github.io/rosette/
Racket
MIT License (unconfirmed)
2026
MAINTAINED
Emina Torlak's solver-aided host language is the standard tool for rapidly prototyping a new CEGIS domain [cite: 12]. You write an interpreter for your domain in Racket, and Rosette automatically compiles it to SMT constraints for the Z3 backend. Gotcha: It operates purely on bounded symbolic execution. If your experiment requires large symbolic arrays or unbounded loops, the symbolic heap will explode, and compilation to SMT will silently stall [cite: 19].

LLM-CEGIS-Repair
https://github.com/pmorvalho/LLM-CEGIS-Repair
Python
Licence unconfirmed
2025
MAINTAINED
The reference implementation for neurosymbolic CEGIS using MaxSAT for fault localization and LLMs for synthesis. It orchestrates the loop between the LLM API and the test suite execution [cite: 20, 21]. Gotcha: It is tightly coupled to its specific dataset of introductory C assignments (C-Pack-IPAs). Running it on arbitrary programs requires rewriting the fault-localization abstraction layers.

Sketch
https://github.com/asolarlez/sketch-backend
C++ and Java
MIT License (unconfirmed)
2020
DORMANT
The original and famous system that defined the CEGIS methodology. While conceptually foundational, it is practically dead for new research. The frontend and backend are split across repositories, it requires legacy toolchains (e.g., GCC 4.3 workarounds are literally in the README), and it fails to build reliably on modern Linux distributions [cite: 22]. Do not attempt to build this; use Rosette or cvc5 instead.

LEVER
https://github.com/niansong1996/lever
Python
Licence unconfirmed
2023
DORMANT
The reference implementation for execution-based neural verification of code generation. Gotcha: Dependent on deprecated OpenAI Codex APIs (code-davinci-002) which are no longer accessible [cite: 23, 24]. The published results cannot be strictly reproduced today without substituting a modern open-weights model like CodeLlama and retraining the verifier.

## PART 4. DATA AND BENCHMARKS

SyGuS-Comp Benchmarks
https://github.com/SyGuS-Org/benchmarks
Thousands of SMT-LIB files
Public domain / MIT (unconfirmed)
The authoritative baseline for formal syntax-guided synthesis [cite: 25]. It contains tracks for Linear Integer Arithmetic, Bit-Vectors, and Strings. What it measures: The speed and correctness of classical CEGIS solvers. Known problem: Severe specification overfitting. Because the grammars are highly constrained to make the problems tractable, solvers often "game" the benchmark by enumerating edge-case syntax rather than learning generalizable synthesis logic [cite: 8]. 

CloverBench
Access via Clover repository (https://github.com/ChuyueSun/Clover)
60 annotated Dafny textbook programs
Licence unconfirmed
A custom dataset designed specifically to measure the consistency checking paradigm of LLM generation [cite: 4]. What it measures: The ability of an LLM and formal verifier to ensure code, docstrings, and formal annotations match. Known problem: Saturation and scale. It is a hand-crafted dataset of only 60 programs at a textbook difficulty level, making it highly susceptible to prompt-engineering overfitting and training-data contamination in frontier LLMs.

C-Pack-IPAs
Access via MENTOR submodule (https://github.com/pmorvalho/MENTOR)
1431 incorrect student C programs
Licence unconfirmed
The authoritative dataset for educational automated program repair [cite: 13, 21]. What it measures: The capability of a CEGIS loop to localize faults and synthesize minimal, semantic patches that pass a test suite. Free from standard open-source contamination because it comprises real student coursework.

TCGBench
Access route via SAGA framework (arXiv:2502.11894 unconfirmed exact URL)
Size unconfirmed
Licence unconfirmed
A newly formalized foundational dataset for evaluating Test Case Generation and the quality of verification suites, specifically highlighting the blind spots in LLM-based verifiers [cite: 7].

## PART 5. THE REPRODUCTION RECIPE

The most reproducible, informative, and structurally modern experiment in this field is the AAAI 2025 Neurosymbolic CEGIS pipeline for automated program repair [cite: 2, 13]. This experiment proves that replacing the enumerative synthesizer with an LLM, while keeping the structural rigidity of a MaxSAT-generated sketch, fundamentally outperforms both pure LLM generation and pure formal methods.

Exact Software and Version:
LLM-CEGIS-Repair repository (https://github.com/pmorvalho/LLM-CEGIS-Repair), master branch as of early 2025 [cite: 20].
CFaults (MaxSAT fault localization submodule) [cite: 21].

Exact Dataset:
C-Pack-IPAs (1431 incorrect introductory C programs), included as a submodule [cite: 21].

Parameters to Set:
Fault Localization: MaxSAT.
Sketch format: Bug-free program sketch with "@HOLE@" tokens replacing the minimal buggy lines identified by MaxSAT [cite: 26].
Model: Llama-3 (or GPT-4 for API equivalence).
Prompt Configuration: Zero-shot, featuring the FL-based sketch, IPA description, and the failing I/O test suite [cite: 26].
Iteration Budget: Maximum 5 CEGIS loop iterations per program.

Replicates and Seeding:
3 independent replicates. Set sampling temperature to 0.0 (greedy decoding) for deterministic baseline, or 0.7 with fixed random seeds for the generator to allow search diversity across CEGIS iterations.

Approximate Compute Cost:
15 to 25 GPU hours on an A100 or H100 for local LLM inference (Llama-3 8B or 70B), plus standard CPU overhead for the MaxSAT solver and C test suite execution.

Expected Result:
The counterexample-guided approach utilizing MaxSAT sketches will successfully repair a significantly higher percentage of programs compared to baseline APR tools (CLARA, VERIfiX) and zero-shot LLM baselines without sketches. The baseline formal tools will time out at 90 seconds on programs like "find maximum of three numbers", while the CEGIS pipeline will produce a semantically correct, minimal patch in a single interaction [cite: 26].

Three Most Common Ways People Get This Wrong:
1. Over-generation: Practitioners fail to enforce the strict boundaries of the "@HOLE@" sketch, allowing the LLM to rewrite the entire control flow graph of the program. This destroys the monotonic narrowing of the CEGIS loop and turns it into a blind guess-and-check system.
2. Contaminated Evaluation: Judging the synthesized program via string-matching (BLEU/CodeBLEU) against a reference solution rather than compiling and executing it against the test suite to verify semantic equivalence.
3. Timing Artifacts: Failing to isolate the computational cost of the MaxSAT fault localization from the LLM inference time when comparing efficiency against classical symbolic solvers.

## PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you are building an in-silico programme, you will quickly discover that a generalized "Neurosymbolic CEGIS Harness" does not exist. 

Currently, researchers who want to run classical CEGIS write strict SMT constraints in cvc5 or Racket. Researchers who want to run LLM-based CEGIS write fragile, ad-hoc Python scripts chaining API calls to execution environments. There is no off-the-shelf, language-agnostic middleware that formally manages the state of the inductive loop between an LLM generator and a deterministic verifier.

You will have to build a harness with the following specific interface:
Input: A target function signature, a natural language specification, a grammar of allowable operations (optional), and an initial set of concrete I/O examples.
State Management: A monotonic accumulation database of counterexamples.
Output: A formally verified Abstract Syntax Tree (AST) or a proof of resource exhaustion.

The Hard Part:
Bidirectional Translation. When the execution verifier or SMT solver fails a candidate, it returns a raw counterexample (e.g., a specific matrix input or a memory state). You must build a translation layer that converts this mathematical failure state into a narrowed natural language prompt or a precisely annotated sketch for the LLM. Conversely, you must parse the LLM's raw string output back into a strict AST to pass to the verifier.

Effort Estimate:
Roughly 300 to 500 hours for a competent computational scientist. The fact that the Clover team, the LEVER team, and the LLM-CEGIS-Repair team all independently rebuilt private, tightly-coupled versions of this exact execution-and-prompting loop is the strongest possible signal of a systemic tooling gap.

## PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

Combinatorial Explosion:
The foundational failure of classical CEGIS is its susceptibility to combinatorial explosion. Whenever a problem requires synthesizing a program outside of a narrowly constrained domain, enumerative and symbolic search algorithms are overwhelmed. Attempting to synthesize arbitrary higher-order functions or programs requiring complex auxiliary helper functions reliably causes state-of-the-art SMT solvers to time out. The search space degenerates into a naive, unguided enumeration [cite: 10, 27].

Specification Overfitting (The NFL Theorem of SyGuS):
Padhi et al. introduced the most vital standing critique of the field: CEGIS inherently overfits [cite: 8, 9]. The core mechanism of CEGIS relies on testing candidates against a finite set of counterexamples. Padhi proved mathematically that as the expressiveness of the synthesizer's grammar increases, the number of "spurious" programs—programs that perfectly satisfy the accumulated examples but fail the global specification—explodes. The synthesizer wastes its iteration budget returning these overfitted artifacts. This critique was partially answered by proposing parallel learners with varying grammar expressiveness (PLearn) and hybrid enumeration, but it remains a fundamental limit on unbounded synthesis [cite: 9].

LLM Self-Verification Failures:
A recent failed programme is the assumption that LLMs can act as their own standalone verifiers. Early research posited that having an LLM generate a program, and then asking the same or a larger LLM to "verify" the correctness of the code against the prompt, would yield a valid CEGIS loop. This does not work. Studies on Test Case Generation (TCG) demonstrate that direct generation of tests and verification verdicts by LLMs yields high self-pass rates but terrible actual detection rates, masking severe model blind spots [cite: 7]. Without grounding the verification phase in deterministic execution, an SMT solver, or a formal framework like Dafny (as in Clover), LLM-to-LLM CEGIS degenerates into an unmeasured hallucination loop.

## PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

To run frontier experiments with high impact, a well-resourced newcomer should execute the following specific experiments, ranked by feasibility and theoretical value:

Rank 1. LLM Priors for Anti-Overfitting in Formal SyGuS
Experiment: Modify an open-source SyGuS solver (like cvc5) so that the enumerative synthesis phase is guided by a probability distribution generated by a coding LLM, rather than a lexicographical or structural grammar search. 
Feasibility: High. You have compute to run the LLM inference to score the grammar branches, and the cvc5 architecture is well-documented.
What it measures: It directly tests a solution to the "Specification Overfitting" theorem. By using the LLM's learned distribution of human-written code as an inductive bias, the solver should bypass the spurious, overfitted programs that plague expressive grammars.
Falsification: If the LLM prior is too misaligned with the strict logical constraints of the SyGuS problem, it will heavily penalize the sparse, correct mathematical solutions, causing the timeout rate to increase relative to baseline enumeration.

Rank 2. CEGIS for Verifier-Level Invariants
Experiment: Run the CEGIS loop to synthesize formal loop invariants and pre/post-conditions (e.g., in Dafny or Liquid Haskell), rather than synthesizing the executable code itself. Once the invariants are synthesized and verified by the SMT solver, pass them to an LLM to generate the final code.
Feasibility: Moderate. Requires building the translation layer between SMT counterexamples and invariant sketches.
What it measures: Isolates the hardest bottleneck in formal software generation. LLMs are currently excellent at writing code but terrible at deducing strict inductive invariants. This experiment tests if CEGIS is more efficiently deployed at the specification level rather than the implementation level.
Falsification: The experiment fails if the counterexamples generated by the verifier are too low-level (e.g., raw memory states) to be effectively mapped back into an inductive query for the invariant sketch.

What will NOT work:
Unbounded LLM-driven CEGIS without localized sketches. Do not attempt to run an experiment where an LLM is fed a failing test case and asked to "fix the whole program," looping until it passes. This has been tried extensively and results in destructive, invasive rewrites that break previously functioning logic [cite: 2, 13]. The LLM quickly gets trapped in a cycle of alternating regressions. Any successful CEGIS loop in 2026 requires the verifier to formally narrow the search space (e.g., via MaxSAT fault localization) so that the synthesizer is forced to solve a strictly bounded hole.

**Sources:**
1. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3ZhCErbk7u7_1eyAA4rryZbRcWsPX0CbnrOzqcanisttelSJgWjNZ6AfapPKH_gGIuKG1ldm3WMY5rNl5QWYs148df5f85Yp-rudK1LZdPH392ugaq4XPG3U-xZCAXvYjatpSGWPsudw9vyab6RUnEdbALvqwp3tPJafcqfUHLS0jSElAITnnzA==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7BxIi49Xvzmkwv24c0jvv143eYbcRR9vCKEJWz1Vn7kXcEc1LiwOgbPBpj5NmQ4f0vg6v5SB19UP2AA9mYGgof-BuV2xanFs6KkmFsIil87FWamiYvQKSzA==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5BxN-gTgJwlZfHXptGjB8RZADGseKIBvu_inlMsMx_O7vhBp9e2yB-030syXT4_dRjhepMsiYGTUqWErbhjJf790CSp6DrMBz8hWkGzI34xrh3etLrw==)
4. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3sU_svteFAb_yIqXdHb_NGMERLGdZ8xjPuZewNTOK81E-mUYCtn-l_ZkMYxjFlYI8eVziRKNopO13LGinHUqAHTkeMwytEoAYmQ-9ADGEhyNqq_AcK9_W2mAYD00=)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_pOeLasxuLkFQ3YSI678gTS8b7A4xz1-cm4XdTRXWWQqNqK2vS6kjWIfQyLTTJ87GEbJ8rN08SXpt-VQ92ppWnDb5kigxO3ePJuQ9w3qiH8X-SAbORRDoSXQ2ANLbOXdKfSKBkyoj72CwzZu_zxQ_z6d4A0mcli4Io-1FfWau246dDqcv9CT_ldf8tPRU-FVz9o3MqRihlMw=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGY8xJTAXn1pVYkO71Xrcg5vkQ80Rt7aHxziUcMkowZzEvoFY2M7-lVkdjI9Laek1unu8bLdY5Urytc452hJz-jhFQTm0Fn4LJhhloyOlPVGIMHTudMLQ==)
7. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvj8PbOknbEEValMd9D3mkaf7v-fgcAUX1yg1g-h3t6aFrTiNDFEBuy6aMgLcRKn-_LH0Cy229s5VyYz66edctcQSEPmqQhWup9L0_oeco2EUZ7Fjy33_OggyvjRn_2FsdXPE=)
8. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJDRlVU9jim7uogk7AsHbaf5ie3l-bdqqFK8HzyTtMuMIVDCStkdswrAejNNYd54g8StUmoGYjrXayfzJrLVbVdBNGRGsH6Ipr5ChZOkjJ1aMYIrmgazsupT7HdOD7SbM=)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpXvrdyD7gNV_nVuMcqnGb49iRrch4dqfYRI0vww3yd6yCwXVuTBBTtAt3N2NwGjMVVEPDbVcBy-B5311sZtUbY4hkegxdYDRasGvKx-Ic-93LyzWVOA==)
10. [ceur-ws.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCndbJ2dmhPuaCMqkAYh2F-f4uNoUYTcaTcOVUzlJ5_KXIe_Keq6O7LdUvo1K9833dPjuQniRp37ht4GGpSsh2YMffTqRsHrGNIrccONUJSPlX8lW9FDBB6KYqj3Ub8bfJKw==)
11. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCZlBcsbbgkrR4jk4dPZ-ko9EH_CtyPu-sdVTrvsZGzjbb8FYLl_xmuUeqhCqXzGVhmeHt9qFE5aHLMRWQhmpzlwNrdYW5zMRgJKaVrm0=)
12. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyzGBR0JeGXqSoKutLV_UessMaE7SoL0ZaSvdsPH8TM3eiGozdwu-OStd5bXtQ6q8FULiAvt5eR2ls2w3we9wQtL1U8fqEpNx8khYy8WBT7wYvbW4zPg==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVnMdFG2qAGpcgU2Nj8eBI0gToe41sU9yvTpeydlVxN6TmYaUQ6WZw7q_xm7epZhoXJBLf5m9ZkjXKdPdHdhSZse3wvk8Vk4vijSFqRQsCDKxDjkPnfg==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5PCowIifk7DH0emc-vNYefWmU2vE36fi1hjm2RliTxPIGa2Zx0UY-tkGycxCfNPtc3YpAmn8GerH_l_8Ou7rz2w-Cyd86X6eNYuL64letBwrLKI-Vgg==)
15. [ed.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmfhpGckgWfkRsBBD_4j_ZtmIouWyuz6v3973BLe-sKQvzntgEJSgknzOR1iSBqeYam6hIhs2qaYxM4wQrrWKMcXlqJfsZ81Tf2ADhwzGQWpa2kZqR27_ttpcaYCJLSHmDAkNONodoGS6JHy-QjoxP8C04r2pwS6yyG1zAPhQQhrpe2XsxCxH12puHPs0H9g==)
16. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBflDjSQoX5WihzcvS8Mq59MujA-IVqG35tR7we4mYW0LVo1WZFTOBGDWwvmZfmwgfBMLSqqKADWaDRIPaO6jtbKs-EKIg4ti0wAg-kQ==)
17. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHERHQ2aOdcU8vzGxqSom55ksdZlwLr9QiqLOQCoFd7BG35m8J_Chd4kntYrHeWVWfgAQ9Ckbrc0uVZfM0d1PRY7U3yyaszksQMCaODxMxuBiz1qmS5)
18. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOsd89B7t3JJYbKZ7SiTzAZKXLSThN8h5-I1DWkhrh4T317DGc01ZM7v9sT8QFWwsRiqbsCa1ZKyEjqZrmrnLhfGzrRgOuJgEArfjuf5zRkTIkvRRHicu8wPYjSw==)
19. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFz2s_Mn3chrijjclJEe7VORvotmd2fa9CeMnofSwg3VIBqymjpRuyVhFuHja0uedGP2fmcyA5dAwzqh8u_VpXnycCdBFflOzs2MIRtqNQ9pebraX2ISVU2NAy6pNnrKg==)
20. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6QJt99yxl-QOX3mGWF_aqg52MuKQF9wmwxVTRR4hajXmZ2aWNrZlkhxnebqzya3FMs8JV2NXae1-4A46oamf73q2mGSmnvTxZpHFCK3JdQEFh-IhDCGAbondrQ1HYVxvG_t0=)
21. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOXShn-I7a4J17EX6Nnse1VA2gzmo6Tc2WIiJO6G_TpH4wtnoON-O2C6aQaNIZucKtxgRNIEXR4QS3BI0lqB0P2-z8CXFepZkrsdP44NHHTwVD1vIVEAVzZQ==)
22. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEebEiIa4zlZm0nucFKyfRE6m4t1fOjGjBPhFYHxy8l3xcum2JPQqsY-qovYuJISOxUflWo_x2mdcBnCxm5UxZFqjsImUtj-9hcVtfasOR7yotqKv9z3NPWA1ESukLKSVwu)
23. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_W_ibW7_-zT5tj9fLPh6u-ZxPtF3AIGTx_kBYiDkqEqCZo0ngABUkTmRPD2Gi7f_W3rnDItKMQf95Dg7XJeA5-3FtmggTTBCEYQhmcuWXnPl6vY4O68Z_LhrzyVpbYeQQDla3DT0RMQ==)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMO5DNdI7dDHligh5B7utbe9mNiMc2dLHpIQT8yLI8BtUlumt0o2hDdIujhCpNs8ud8KSEAcs8GjOPx3fNqL-fHLuR76UnXxtM0nqioQkgjWIOi3vu3-fUos55LDbq-tVcWAPRuFcllauiHwaCGs9kYyhmZRfRASkmdlouI0krjGvVCKdVJDigAWSZK3sU8Im-iDHoPUjEdu6IRd-xp--BfHCM--xzddJJmPe_)
25. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKYqcQ7EZTyVUTa19icLtuPjX36CWZ99iI2Ul2p2PtLOvVn0kB8MWODowiupbdKtUP6ri2yG0H3uhTeXiMuLmtHgO3AnJ2jJ1I36bTmPeL7hMODz8AyFwka6QSXcE=)
26. [utl.pt](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFx4C1EVGYT5fG_XROcAVxwhC-x2lvVdzKNeksQNVG35aH9QWcbli9s6j0fodILf7obT2cMNEu4Hw-4pwnS5mZuKDOa5mOzq1xYPH1IV2uyKoCZNCWmwk85kJz6jo0kM9KGn7qzgaMFheRoGRaruvSbMHKrmRvcMzuDxYg_3LiVyg==)
27. [upenn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwT3z70oY8jJ1DdqxuuHjqHnwCqm_VRiGEkjE3_AKxMZty5MBuN-GnKmIl5UCNflWGT7XZoown1A7fEFy0vYGdakruCq7pO2xdGPJGKprR0r9VqiQndWANIUwxi499NeOlr6TZxcMUCIM=)

