# Prompt 41: Inductive Logic Programming

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdFbGFmYW8yY01jUHFqckVQajlQVDJBURIXRWxhZmFvMmNNY1BxanJFUGo5UFQyQVE
**Elapsed:** 304s

---

Inductive Logic Programming is a subfield of artificial intelligence that focuses on learning human-readable, logical rules from data and background knowledge [cite: 1, 2]. The field revolves around systems that can look at examples of a concept, use pre-existing facts, and automatically write a logic program that accurately separates positive examples from negative ones. In recent years, this area has seen a clash of philosophies. On one side, traditionalists advocate for purely symbolic, discrete systems that guarantee exact reasoning and interpretability. On the other side, researchers favor neuro-symbolic approaches, attempting to merge the fuzzy pattern-matching capabilities of deep learning and large language models with the strict verification of logic programming [cite: 1, 3]. It seems likely that the future of the field lies somewhere in the middle—using neural networks to process messy, real-world data into structured facts, and using logic programming to formally verify and build rules from those facts [cite: 4]. 

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Inductive Logic Programming in 2026 is the primary mathematical formalism for learning interpretable, symbolic rules from data. It operates at the intersection of machine learning and automated theorem proving. The field has largely shifted away from early heuristic-based search toward exact, solver-backed combinatorial optimization. The organizing principle is no longer just "can we find a rule," but "can we provably find the optimal rule according to a cost function, and can we do it efficiently by learning from the failures of previous attempts" [cite: 5, 6]. 

Your description of Meta-Interpretive Learning is historically accurate for the 2014 to 2020 era, but it requires a crucial correction for the 2026 frontier. Meta-Interpretive Learning, driven by a Prolog meta-interpreter, iterative deepening, and metarules, was the standard. However, the current frontier has largely abandoned the pure top-down Prolog meta-interpreter search because it scales poorly and suffers from redundant computation. The state of the art is now Learning from Failures, a paradigm that separates generation, testing, and constraining into distinct phases. A modern system uses Answer Set Programming or a MaxSAT solver to generate a hypothesis based on constraints, tests that hypothesis in Prolog, and if it fails, extracts a logical explanation for the failure to mathematically constrain the solver from ever generating a similar hypothesis again [cite: 7, 8, 9]. Predicate invention is no longer just binding a fresh symbol during a meta-interpreter proof; it is formulated as an explicit Answer Set Programming problem where the solver is permitted to invent intermediate concepts if and only if it reduces the overall Minimum Description Length of the final program [cite: 9].

What is SETTLED: The theoretical necessity of constraint-backed search for exact symbolic induction. Heuristic top-down searches are considered legacy. The requirement for systems to support recursion and automated predicate invention is also settled; any modern system that cannot learn a recursive rule is considered obsolete [cite: 10, 11].

What is CONTESTED: The role of deep learning and Large Language Models. There is a live, often fierce disagreement between the pure symbolic camp (led by researchers like Andrew Cropper and Stephen Muggleton) and the neuro-symbolic integrationists. The symbolic purists argue that neural networks should be entirely separated from the reasoning engine, treating logic as a pristine, verifiable layer. The neuro-symbolic camp argues that continuous relaxation of logical operators is necessary to handle noisy, real-world visual and textual data [cite: 3, 7].

What is OPEN: Abductive reasoning over unstructured data. The field has not yet solved how to automatically generate the declarative bias (the strict templates and type constraints that guide the solver) without human intervention [cite: 12, 13].

In the last three years, ILP has been heavily absorbed into the broader field of Neuro-symbolic AI. Pure ILP venues have shrunk, while hybrid papers dominate mainstream machine learning conferences. What was lost in this merge is the focus on mathematical elegance and completeness guarantees, as many modern hybrid papers sacrifice exact logical entailment for differentiable approximations that scale better but hallucinate or fail on edge cases [cite: 3, 14].

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Stephen Muggleton, Luc De Raedt
1994
Inductive Logic Programming: Theory and methods
J. Log. Program.
DOI 10.1016/0743-1066(94)90035-3
This is the foundational text of the field, establishing the mathematical definitions of background knowledge, positive and negative examples, and inverse entailment [cite: 15, 16]. A practitioner must read this to understand the vocabulary and the theoretical boundaries of what can be induced.

Stephen Muggleton, Dianhuan Lin, Niels Pahlavi, Alireza Tamaddoni-Nezhad
2014
Meta-interpretive learning: application to grammatical inference
Machine Learning
DOI 10.1007/s10994-013-5358-3
This paper introduces the Meta-Interpretive Learning framework you anchored your query on, defining how abduction and metarules allow for recursive logic programs and predicate invention [cite: 17, 18].

Andrew Cropper, Rolf Morel
2021
Learning programs by learning from failures
Machine Learning
DOI 10.1007/s10994-020-05912-9
This paper marks the paradigm shift from Meta-Interpretive Learning to solver-backed constraint learning, introducing the Popper system [cite: 8, 19]. It is mandatory reading for understanding the mechanics of modern hypothesis generation and pruning.

Andrew Cropper, Sebastijan Dumancic
2022
Inductive logic programming at 30: a new introduction
Journal of Artificial Intelligence Research
DOI 10.1613/jair.1.13507
This is the single best modern survey of the field, bridging the gap between legacy Prolog implementations and modern Answer Set Programming paradigms [cite: 11, 13, 20]. 

CURRENT SOURCES (2023-2026)

Celine Hocquette, Andrew Cropper
2025
An Empirical Comparison of Cost Functions in Inductive Logic Programming
arXiv:2503.07554
This paper empirically demonstrates that simply minimizing the textual size of a hypothesis does not consistently reduce generalization error, upending a long-standing assumption in the field [cite: 5, 6]. It evaluates over 1000 tasks and dictates how practitioners should configure solver cost functions today.

Yi Chu, Shaowei Cai, Chuan Luo
2023
NuWLS: Improving Local Search for (Weighted) Partial MaxSAT by New Weighting Techniques
AAAI
DOI 10.1609/aaai.v37i4.25505
While nominally a SAT solver paper, this work is crucial because the NuWLS solver became the community standard backend for the Popper ILP system, enabling the scale required for modern frontier experiments [cite: 21, 22, 23].

Yifei Peng, Yaoli Liu, Enbo Xia, Yu Jin, Wang-Zhou Dai, Zhong Ren, Yao-Xiang Ding, Kun Zhou
2026
ILP-CoT: Abductive Visual Rule Induction by Bridging Inductive Logic Programming and Multimodal Large Language Models
arXiv:2509.21874
This paper defines the current frontier of hybrid integration, showing how to use Multimodal Large Language Models to propose structural rule drafts and facts from unstructured data, which an ILP system then mathematically verifies to eliminate hallucinations [cite: 4, 24].

Jingyuan Sha, et al.
2024
Neuro-symbolic Predicate Invention: Learning relational concepts from visual scenes
Neurosymbolic Artificial Intelligence
DOI 10.3233/nsai-240101
This work introduces NeSy-PI, solving a critical open problem: how to invent predicates directly from continuous 3D visual perception rather than relying on human-engineered discrete background knowledge [cite: 25, 26].

Lukas Helff, Wolfgang Stammer, Hikaru Shindo, Devendra Singh Dhami, Kristian Kersting
2024
V-LoL: A Diagnostic Dataset for Visual Logical Learning
MLR Press
arXiv:2306.07743
This introduces the authoritative modern benchmark that merges classical symbolic induction tasks with complex visual rendering, forcing systems to handle both perception and exact reasoning simultaneously [cite: 27, 28].

PART 3. SOFTWARE I CAN ACTUALLY RUN

Popper
https://github.com/logic-and-learning-lab/Popper
Python and Prolog
MIT License
2025
MAINTAINED
Popper is the community standard for modern ILP experiments, executing the Learning from Failures paradigm [cite: 29]. It can successfully induce recursive list transformations and graph algorithms from small datasets today. The primary gotcha is environmental: it strictly requires SWI-Prolog, the Clingo ASP solver, and for any non-trivial experiment, you must manually compile and link the NuWLS MaxSAT solver, otherwise the combine stage suffers a combinatorial explosion [cite: 29]. It also lacks support for floats and relies heavily on users hand-crafting a precise declarative bias file.

NuWLS MaxSAT Solver
https://maxsat-evaluations.github.io/2023/
C++
MIT License
2023
MAINTAINED
This is not an ILP system itself, but it is the required backend component for Popper to achieve state-of-the-art results [cite: 29, 30]. It executes the constraint satisfaction problem that Popper generates. The gotcha is that it must be built from source and added to your system path manually; if Popper falls back to its default RC2 solver, your experiments will time out on complex datasets.

Metagol
https://github.com/metagol/metagol
Prolog
MIT License
2021
DORMANT
This is the canonical reference implementation for Meta-Interpretive Learning [cite: 31, 32]. It can run grammar induction and simple family tree proofs. However, the originating authors explicitly note that it is no longer under development and has been superseded by Popper [cite: 31]. It is unsuited for modern experiments because its pure top-down search does not scale to large background knowledge databases.

Aleph
https://www.cs.ox.ac.uk/activities/machlearn/Aleph/
Prolog
Academic Free License
2020
DORMANT
Aleph is the most famous historical ILP system, implementing Mode-Directed Inverse Entailment [cite: 16, 33]. Practically every paper from 2000 to 2020 benchmarks against it. However, it is effectively dead software. It is a massive monolithic Prolog file originally built for the YAP Prolog compiler. While there are ports to SWI-Prolog, the software fails on modern continuous integration pipelines and struggles with deep recursion. Practitioners only run it today to generate baseline comparison tables [cite: 34].

PyILP
https://github.com/danyvarghese/PyILP
Python
MIT License
2023
MAINTAINED
This is a modern Python wrapper designed to orchestrate Aleph and Metagol [cite: 34, 35]. It is useful for educational purposes or quick baseline generation because it handles the archaic Prolog file formatting for you. The limitation is that it inherits the search bottlenecks of the underlying legacy solvers and is not built for high-performance computing clusters.

ILP-CoT
https://github.com/future-item/ILP-CoT
Python
MIT License
2025
MAINTAINED
This is the reference implementation for the frontier integration of Large Language Models and ILP [cite: 3, 24]. It runs a failure-reflection loop where an LLM proposes facts from images, and a Prolog backend verifies them. The gotcha is that it requires API access to external LLMs and its performance is entirely bottlenecked by the latency and context window of the proprietary model you plug it into.

PART 4. DATA AND BENCHMARKS

ILP Experiments Framework
https://github.com/logic-and-learning-lab/ilp-experiments
Size: Hundreds of tasks across 5 domains
MIT License
Used to measure system search time, hypothesis size, and predictive accuracy on program synthesis, games, and list transformations [cite: 36]. This is the authoritative, modern test harness for the field. It handles running systems in parallel and standardizes output to JSON. If a system cannot solve the String Transformations or List Functions tasks in this repository, it is not at the frontier.

V-LoL (Visual Logical Learning)
https://sites.google.com/view/v-lol
Size: 10000 plus generated visual scenes
CC BY 4.0 License
Used to measure a system's ability to combine visual perception with strict logical induction [cite: 27, 37]. It translates classical symbolic benchmarks (like the Michalski train problem) into 3D rendered images. This benchmark is actively treated as authoritative for neuro-symbolic papers. Known gotcha: End-to-end neural networks tend to overfit on the visual textures rather than learning the underlying relational logic, solving the benchmark in a way that does not generalize to out-of-distribution visual angles [cite: 28].

Mutagenesis Dataset
Identifier: DOI 10.1007/BF00993277 (Legacy)
Size: 230 molecules
Open Access
Used to measure binary classification accuracy on structured chemical graphs [cite: 38, 39]. This is the most famous dataset in the field. However, it suffers from severe saturation and contamination. Almost all modern ILP systems can achieve near-perfect accuracy on it, often by learning degenerate rules that exploit artefacts in how the 230 molecules were historically sampled. You should run it only to prove your system is functional, never to claim state-of-the-art performance.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to anchor yourself in the 2026 frontier is running Popper on the List Transformation synthesis tasks. This proves your environment has the constraint solver correctly bound to the logical tester, and it demonstrates both recursion and predicate invention.

Software and Versions:
Popper version 5.0.1
SWI-Prolog version 8.4 or higher
Clingo version 5.5
NuWLS-c-2023 MaxSAT solver (compiled and added to system path)

Dataset:
The logic-and-learning-lab/ilp-experiments suite. Specifically, the synthesis-finddupl task (finding duplicate elements in a list) [cite: 29, 36].

Parameters to set in the bias.pl file:
max_vars(6).
max_body(4).
enable_recursion.
type(head,(list,element)).
type(tail,(list,list)).
type(element,(list,element)).
direction(head,(in,out)).
direction(tail,(in,out)).

Compute Cost:
Negligible. Less than 0.1 CPU hours. This is a combinatorial search problem that either solves in seconds or explores a non-terminating branch and times out. No GPU is required.

Expected Result:
The system should output the exact minimal recursive logic program:
f(A,B):- tail(A,C),head(A,B),element(C,B).
f(A,B):- tail(A,C),f(C,B).
The expected search time using NuWLS is under 10 seconds. This matches the published results from the original Cropper and Morel 2021 Machine Learning paper [cite: 8, 29].

Three most common ways people get this experiment wrong:
1. Omitting the type and direction annotations in the bias file. Without these constraints, the hypothesis space explodes, and the Prolog interpreter will throw instantiation errors when trying to evaluate unground variables on arithmetic or list predicates [cite: 29].
2. Failing to link the NuWLS MaxSAT solver. If Popper falls back to its default internal RC2 solver, it will still function, but the combine stage will consume exponentially more memory and time, eventually timing out on recursive tasks [cite: 29, 40].
3. Leaving enable_recursion active when running non-recursive tasks. Recursion dramatically alters the topology of the search space. If a practitioner blindly copies a bias file from a recursive experiment to a simple relational dataset, the solver will waste all its time exploring infinite loops.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

Automated Declarative Bias Generator
What goes in: Raw relational datasets and an optional unstructured text description of the domain.
What comes out: A perfectly formatted bias.pl file containing mode declarations, type signatures, and metarules.
The hard part: Currently, configuring the hypothesis space constraints is a dark art requiring deep tacit knowledge of how the specific ILP system's solver operates [cite: 12]. A practitioner must manually define what predicates can appear in the head versus the body. If you specify this incorrectly, the system either learns nothing or takes infinite time. You would need to build a pipeline that uses an LLM or static analysis over the background knowledge to automatically infer and generate these constraints. This is roughly three to four months of engineering work for a competent developer. Several groups (including the authors of ILP-CoT and PyILP) have attempted to build private wrappers to automate this, which signals a massive gap in the public tooling [cite: 12, 24].

Native GPU-Accelerated SAT/MaxSAT integration
What goes in: A continuous stream of hypothesis constraints from the Prolog tester.
What comes out: The next optimal hypothesis to test, computed directly on GPU hardware.
The hard part: Current state-of-the-art systems like Popper rely on shelling out to external CPU-bound solvers like Clingo or NuWLS. The overhead of translating Prolog failure states into pseudo-boolean constraints, writing them to a file, invoking a binary, and parsing the stdout is immense. You would need to build an in-memory, GPU-native constraint solver tightly coupled with the Prolog engine via Foreign Language Interfaces. This is highly non-trivial systems programming (C++/CUDA to Prolog), representing six to nine months of work.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

Scaling pure symbolic ILP to big data failed.
For decades, researchers attempted to make ILP systems scale to millions of background facts (e.g., full genome databases or large knowledge graphs). It systematically did not work. The search space in ILP grows factorially with the number of predicates and clauses. Claims that purely symbolic systems could replace standard machine learning on large tabular datasets failed to replicate in industrial settings. The field quietly accepted that ILP is a small-data regime technique; its power is generalizing from 5 to 50 examples, not 5 million.

Pure Differentiable Logic Networks lost interpretability.
Around 2019 to 2022, there was a major push to create fully differentiable ILP systems (e.g., dNL-ILP, ∂ILP). The method looked incredibly strong on paper, using gradient descent to softly select predicates and weights, supposedly merging deep learning with logic [cite: 41, 42]. However, the standing critique is that by making logic fuzzy, you destroy the very reason for using ILP: exact, verifiable, and minimal symbolic representation [cite: 3]. The models were shown to be learning statistical approximations of the benchmarks rather than true logic, and they failed to generalize outside the exact length of the training sequences. This research direction has largely been sidelined in favor of keeping the neural and symbolic layers strictly separated.

Overfitting on the Mutagenesis and Bongard Benchmarks.
A standing critique of the field is that for years, papers claimed state-of-the-art results by improving accuracy on toy datasets like Mutagenesis or artificially generated Bongard problems [cite: 39, 43]. Later analysis showed that systems were simply memorizing statistical artefacts in how the datasets were sampled (e.g., picking up on irrelevant bond structures that coincidentally correlated with toxicity in that specific 230-molecule set). When challenged with truly unseen domain data, the induced rules were scientifically meaningless. The critique was answered by shifting the field's focus to program synthesis (string and list transformations) where the rule either mathematically solves the algorithm for all infinite cases or it does not [cite: 10, 11].

LLM Hallucinations on Long Predicate Chains.
Recent attempts to simply prompt Large Language Models to act as ILP solvers failed. A standing critique, formalized by de Souza et al. in 2024, is that while autoregressive LLMs can approximate short logical theories, they entirely lack explicit symbolic grounding [cite: 44]. As the complexity and dependency structure of the rules increase, LLMs inevitably hallucinate invalid logic and violate negative example constraints. This critique remains unanswered by the pure Deep Learning community, reinforcing the necessity of external formal inference engines like Popper to act as verifiers.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Experiment 1: LLM-Guided Declarative Bias Generation for Popper
Feasibility: High. It is now feasible because LLM API costs are trivial and their ability to parse Prolog syntax is highly refined.
Method: Build an orchestration layer that feeds an LLM the raw natural language description of a scientific domain and a few data samples. Task the LLM with generating the rigorous bias.pl file (type and mode declarations). Then, run Popper using this generated bias against the background knowledge.
Measurement: Compare the search time, hypothesis size, and generalization error of Popper running with the LLM-generated bias versus the human-expert-generated bias on the ILP-experiments datasets.
Falsification: If the LLM consistently generates overly permissive bounds that cause Popper's MaxSAT solver to time out, the idea that LLMs can replace human tacit knowledge in search-space constraint is falsified.

Experiment 2: End-to-End Visual Predicate Invention on V-LoL using ILP-CoT
Feasibility: Medium. Feasible now because the V-LoL benchmark provides a controlled but visually noisy environment, and the ILP-CoT architecture provides the scaffolding.
Method: Replicate the V-LoL Michalski train problem using a raw Vision-Language Model to extract the logical facts (e.g., "car_has_roof(car1)"). When the ILP solver fails to find a rule, trigger a failure-reflection loop where the VLM is queried to invent a new relational concept (e.g., "is_carrying_load") from the image pixels, which is then fed back to the solver [cite: 24, 27].
Measurement: The percentage of visually invented predicates that are actively utilized in the final minimal hypothesis, and the classification accuracy on out-of-distribution visual angles.
Falsification: If the system defaults to memorizing pixel patterns and the logical rule accuracy drops below a standard ResNet baseline, the integration of visual perception into logical predicate invention is fundamentally mismatched at current VLM resolution levels.

Experiment 3: Cost-Function Ablation on Continuous Scientific Data
Feasibility: High. Feasible now because the MaxSAT integration allows optimal hypothesis learning across varied cost functions, as demonstrated by Hocquette and Cropper in 2025 [cite: 5].
Method: Gather a modern, noisy dataset (e.g., from a materials science database regarding alloy properties). Discretize the continuous variables into logical thresholds. Run Popper over the data while varying the MaxSAT cost function from "minimize textual size" to "minimize training error" to "minimize description length."
Measurement: The variance in out-of-sample predictive accuracy across the different cost functions.
Falsification: If "minimize textual size" produces identical generalisation error to "minimize description length" on real, noisy scientific data, then the complex penalty functions introduced in 2025 are practically unnecessary outside of synthetic benchmarks.

What will NOT work and why:
Attempting to build a "Neural ILP Solver" by fine-tuning an open-weight Transformer (like Llama or Mistral) directly on the ILP-experiments JSON traces to output the final logic program in one shot. It will not work because induction requires strict adherence to negative examples. An autoregressive token generator has no mathematical mechanism to backtrack when a generated clause subtly entails a negative example late in the generation process. It will look like it works on the training set, but it will fail catastrophically on out-of-distribution validation sets because it is performing statistical mimicry, not inverse entailment.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUQTP3KEi8k-y0DZL4ATRhjmM9ZRjM_cOLwijPsKz6hGiDrQboxIPkYSUQMMg90g_NrlWXElnn4nlgpRV-t-kMTtme6bmAkzv64zZCnnGpBCjkTRO4LKVEtA==)
2. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEg5Rm4c1_bIXtNXu5BzAxjIRteVvuWClWlNmi3R2bwCsAPZ36xHY-H93Vd5GSo4-ErstCabq5-E6P9CYbI-sJZ6UlKItWvOrSlYgNdNcCo33UUL1aOmrkBm0kKm8ryZBvkxbKqKWdK2hT1W-SXOZ8=)
3. [sciprofiles.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGswE2jab6xbAYDFz5we6vTN03vTLVGgxX2dLBHtNe0R4kjiGapoybujMNLS_6wceHEDWUM1VAsGLuDcBHzbJh3VnCfyhb0xaPPO7BT9S1rsq3f8vsE4x5YbCkOl6psb0ypw4QxWuGsogSDntYwyMlGtTgK9kinH5XAO8J0XHZMqCTGqy_tipMqkGu634b5H20oiWqTNTVrYIw=)
4. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdQRnelzPsODkiT2IZMHRmpbXAiOxUFCNm0qHbbVkFeoUrfGL4SVsj_Vm4FSHEmY8kn16g1nDRhFmnauxf1LRICyASzMNwu_H3BmGzAtizHUe7cqvlaoIbPsDt5wuqZctzd6WdzRXKg_dNu6QKjtudk8s=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGviWuf-EFPkI-RU1kMaDFSzFKZHpYfcJyuVdb34ZG1AOBVZj-s-V_OI_CnToAnqufdyjdc6njvm8ixLJnUi1XkScT0VOQksQpWE2wnY5XJyUippya7wXhxCg==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLEf5ANZQVCovX3Ofmc1KNpcqNagnf28xu-TU3rBzS1TsGiHCHrFdRiTjY5SXXYEzfYTcaQ02A10rLgpVnFy7m3eAm_lUgsES55vLhRBssaT2J10zSFw==)
7. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHj_LHxEADG8qh-ubjJv1RWX4LXyAylIjMHnU1XuyLDZI2jg8Eux_qAH8UiWuuSPP21UeLm6cIFw5Azmgmslbbhk7kEsSoHA0Es1GRVxiu2fetGi2vLjvkovaYY7Foxm9_rQUQJuoCoIkn3Qc9ZUfbdwO_UqQqhAm9ibehuJui7e_Iew7kRJdNu2Hnek5YuqK9oRrdZywUaW0GrJgVFizGOveuGL-6mfjTXL0fU2oZDoSBE5IbMYo5O4NE24ZqqsowEah4eFW5vYG9nUuziCfQW1AssNH490MKX2IUFsiuzxecF8kFQLRYro287fqPMuxSwHbwEJMvoNNUfozDLF5e150i8jB9NT1E3nHtf3YI=)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERfKUsdHxV-va8yxAfLKXFSYYzb4iOHav9B6HUIfYkvPGx1FAu3CXp2r3ujKgTDhFpWxaJdpdojYEJGLAXMpis4vXzawmAq-DMjE1kV3eYxvO5bVt8pA==)
9. [catalyzex.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErHO6DqwMGl0G_N7_EjNVvhJwi8I5nZeQcaf5McbIIOZar70PBsLRw9PEYRFRcINYNc7G8z68Z9WnIE4wVebCIJazz4aZ4yN8IlXbqCwhJugTNzoatv4bTyL-U3wgZfDo1YXA=)
10. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMYvaqZ03_yo1sr_zzEYRBZTF8LtkrpWFWzJGqzVtpMUvoVWa0ogTpMHM0aiV6mREyaGU-ZygbXNphhNW74jpDxTTuf6KWy7-FmsqdV9SDLnVaKPQd)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3pnnaCfxZTJ7O1UUk7KKFVgQU2qgM7gLmmpL5dwkIFbYw-N4TNzlWB866y36xbTKNCdWzpTBr7WZmiZV3Kgyv8pxbEPjrOAeqgFE8Dz29VNSE7v9wPIs1HXdAhgj7H_lqDuqZF4DX_si9VbweUgygH0muVKKNC7hwC02X5orZwkteYwh_t3oCKhKzinf7EDMhsUUOWpB6IJ4-KBsAyRJX4g==)
12. [surrey.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeqyHHPC7yvYBDhXrJ-TWOJI3Y3m8r0BCsflYQ-TLqsdEzNVGvyZWnD-BKym1P0AvR8Gn6grfPP9qmQZxlTOWDD2UJ6eti9GKVW0Lb_oxffMFq_6VQEVqwlD9LDtog5UHdVFgCPq5pG7jCevG8fz0VXIcy6ZiPT0QS5Sx8EfkHvw4S7Q9XiabyegAUsJqElWFgbGg_UKy4galIeiIe-JtbDvsgokEQHy9D6rZlphC__g==)
13. [jair.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrOzrMRDNN-W4wEdIWc2WlNWmdNlxM9bcU4fqJbf0tyi5IjsARCG_fYMQ5MoN6tptafb0Mo8QBHaMxxomUkFvTw7Ox62p7eEU3EI3c9Ds_MZv9crunkbOle6FQmPDHvtgGGCSmbt4fHwbUz4Em9tM6Gek=)
14. [ntu.edu.sg](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhxeXCsbI6Wf-lwAfDi51UvNjH0nQCwrZ3Hft2315lJAKMfvcaiE4_8dlWgg6geAEvE1zlIfILH9AD-OSKeWBoyX7fjihaINddMrjrtrGE24vqM1zn514xWAA4YZ6GvhtRDqLJD_mNdwJigAzASgQgix0BSGP9KI8nf76lLykw5FNDUovt)
15. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUajKlGqVI329FLciiks5ErqMg_TO96Bnlwp_yEhGKS_KPusFMCEaw1q2DixVFsDfaI7n8N0CPC1T9NkF8SY-vfAOvcT9W3UBOvkm6oXxaMugUO0ywilybOkt8aZU=)
16. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFElRMrp-DRiqjpfuGvr4rEu-8UUX34QKaTPDPPOpASEWA87-uuV2zb3w5qKOK4m9zCsZI3UkuQVgeec7oUCT9y32gRleK1OMNkEqWL1qAof6ophuVuCIdc0jTqV-7W45_jE5Fq7NfAbI70Iz1QgxZH1pR5udQTFrt-8g==)
17. [surrey.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-gw1DQ-Fvu7Kr0dw7BlonwSrK1zlmiuwnih5rs0qb1vQTxmeG1h_JxcRLl2ZBnCdfMyuQqZ07OlTjYSKR2tk0krpEd_WU4NVuW6KHmvr-aqh0IfSt_zMn6lcQvYGoKvxU7dC5DS8x87ofNiOPxseuKwSI6BMAbh_pGsgQ1N6yucd5BfCO9RNw7jPDssFY7vWBpqSSpvzcidJBgS-gDS0Dsr9891GYJdWPDov6Qtam0WEapcTHKQT3BcWXkr5XaysO7Me4tWY=)
18. [dblp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrN9K3RdEMpWgomCWKZc53L9Ju4OQhuLLQ9ms4BT1ZNDqLCHavo52L7olFkHwrz0cFKEIu3eD9n-ZKwk4O3xn1tjuRw0KJT4YY7vDD0cQqW2g93LxjZBTgBGudy0nbES9GbVpMOg==)
19. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqbNMhQFqaHPlCBxfRcEYup_vYUUkcxwXYsMJDuvtVhPq5Zyk7YBJ9UeF_fbfIeTbhq8wbZYdhiiZXrRBrtF4ZFZVvd7iCXgXntYTfbx7A-x_io46rsAtE3uXqNmEfjzinIMqZX_6VsIG5noT7iYF4Nl8=)
20. [jair.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXA0-jEOHGVfAwA-WrAPH-kki0AucQ2NaI7yle7NYBJd2zrtz3caOHbmqdMH0Chhug2yYQ4zS7dhMuPk3LiyrZUwSOQnUnhlbhXvKW53yWFpcg9zXyPhHb-tc_X8FfzVAHDGoho-p0Og==)
21. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGe-pvwjcfR2EKrLsDoJOhWwFVQKe-6GAHy_7vl7JRjiwmw7dDG7zYSgohLClltZjgXXkH6jD7ngaj4pEC2x1wtrpbDYQb4oyzYUCY_zVZhdQWjhTMs0j5OAOXDQuFf2sFYHqn8rVXOsF8C-ZQ=)
22. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHu8mESFoqZB28uiLqbDNjN16Ie7Dp597O6-SZjVJDbO8Ip7uJXAOhyARB42HfWZOVuj7AZj487EycU-DghoKWkiJUuJiiaFxcDpeHU7P0b83MJvSLOI3G6Bt9xgA74EOy_sXDoAG3yC4v7PdGGaqDaOdk=)
23. [ios.ac.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8Y_yX_lwo_OURxp1MS9QkaggsZ9ozBcLyMAXXIPloL3t7KDY_epzJi1IaPE1moX6tF0nIBJi6imBJ-zVCxUarsorlfKwvFgqmAaMPzuF9ryzOG-nL7ek92Zg_WyIQStCf5alssa6YVFjbDGx4o9GzPB18taCkZnPikG45yyW59825XrGQeypsOGEX39hgR0FFEE3YXb6a-rNqnRsYEvyt0KwBfrp5UPcTPPjl)
24. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtBxpK8QT3H13Pmr85BNpcAC0nFD1Q4fwNMnhO7UvAEmkFjUSDwbA7J1KcjtFVJJczRemwFSaeo0AqsnkDuZ337Yq-t0aIU5h8RAOl-jFstcOSSlmyWTeNYfAWsg==)
25. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwQGD4wI12DZxfDdTLvUR2GecQXSc1ED79-b2LbTrfjCf3jhFY6kExqifXuPGxJm2yAwVdCQE9LM_mBOc_P9EJz7C-ElKnzZcIwDfswz_RKZSw675Em6QRSRXy_YUd4RCf_m3093rtOuye6PnB4S0sJX7InUz_wbBn9YPWDaQnuFrPzFbMfOK6FH3_tvsJPkLg8NZ79nhF7y35AZBA4eEJ80hsUtKfhnnRGdBP_47tfjYgtZmmO12YGTleKg==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG75xFr4glqA3VGEidEOQ1hUtXMvhG1LHecnYaViu9R9-NOqfKusnQ7FUJXZIiX5WCyvkwwkj5Pkc3Zh7hhCkRpeRoL0D8mD_uojCFlk8JEKI2-HbPX0A==)
27. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHq5WvvBZZiBDBXCeSG7osvXDbtl1OfGZIk-wGIZL7Y5w3GudbZCBojshYWlJQ4G5NdS1z9hZoE49UOR0QNd0Q3IcZ3_s48YqlcMOgK2eJxRsq7zczevwoURBbH6DXBuFid)
28. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTyPuNsNp_IGHYXXIsWy4kltLX7Y7et43EFT3q4nNVBMU8oLRsBdGUcUl4Pdbuo0dfUxxX0w_eF7CRXUY-wD-LXWSGtRMIPTk67NijrutpKqjuYIruR16PuDkfj-wn)
29. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvMKELUDJo_hbSmam7AW7Zx4wExoaHsDqWqw6-wlFxouWQZkArW_flN7oo_zo8CnFXRATVoCuBwzwxwQzEf2sVH5sob5GsOyLRyTehjl17m3ih3AI0cAaMImAIKfovWlcjztNhCTY=)
30. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzzxP9kI99SNQgXQRkG3fbn8_C-FSeVCW9wk3331g27mvILNCcldJTGeDynrUSCD4iMDzvrzpNa_OrGjKKNznrclO5DpLoZ6pkAdzGoSLX5VM8aT4YrIjCOQv23u813Io8uEojg6V3iLsU072C5UaxmA==)
31. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3YBiJXHGC2sXqNFssc4F1v6q5BjGuizlQ3yqR8noXmuNbPrx06y8b2bwFv63_ckAV1denqZJMWSr9m2fC5Bw5e0585Fe5E08jUlVJpEgktdH8GtAX19La)
32. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGW-cIVBH9iR8Xa4btq2dCvZ0xfEIpiNA_3Tlp4PM3Z4QLtODMnaErWv7PUiWroaHRK-pxhzvGLbf1neYAAkirmCiCgU4T3oXY9SQcNwn5nYxdUoHgp7T2X8wP7ofdgmp_TN43S-GGoyCDx-PPd7q30BT_19MItkGmaWpvzGa1Aklcgs-v0h9Omn1Q-BMu_S834Qu8=)
33. [up.pt](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHy_4QCqRdVWB9rjWDzYCCHeOzjKGE-NKaOpdyygmJNUPBPzZKxYwQrP6kDvp-Pq6kck41l4XPk1L8elblqmLBZ3j7lASxTqI0XfiVE9xr5ihHUk2jJAJ85jlRliWseyOKG0tgfTyBVURLddGa-Bymbc2DZTdLHBzQ3kgfZSSBYHhIO)
34. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXoUp4EqKvjgImWTffDMqOFxQTbhAjLB9PzGRnh-LY-e5c2ekVl-PDT-3I7WR5w6ZIL51OkqSqUABRT1_-etFkEVH7JxaRUY6Zsywj9x0DJoYnAZdbo1PDkZuQ)
35. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTJHM86skIW-0AObAdUNcmjUq7fuLbRPwjliIBgdG_qCuwqpDCegphrf2wHFWq7u1a-qX2YMHJpiljGCi_p84ZymhZk4sHOPVewzndUg6TxPE41nAgl0RkuDM4qH7n)
36. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFi5ngP7RwoGb2h2LOYAJxyPg2AlXJOxJ8dfilvt4t7ozAMfnPCAAwkkbQ8tPfPFkj3Bf9WKc-4_aLWWONIM41q_yt_thtf032VLX9OtsJJgz2d29wDEymGIB40ad_wdz4s03nfSVSuKw7fKgC4qIk=)
37. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-N1HwHBlOyaWLvivuV3e44E6TAORqa3dr7HfQ0V2U8ilf9Z4Pxrn2r5f9Qif8mBffLP2wQX_mywoFSThKC79mN4_CTM5gbZWyoZhMK_rn2niSWWOgI9rshw==)
38. [jair.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwM8W_e7XCgLxrSWhJkjSEl058esoCTuUe3bt0b5CVPm0n34esezYp3Ht4zCAZqFdMoK-Dpeu_5ehMkj7gUFT1DictjvuP7OIlQkAKeoTNIJQHHKOt_opHr19bBvs4TlNpOP-zhJXItEINMef-GWVlc-s0zLjswEX_I6EB)
39. [dtic.mil](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDOd1mmiu35Ioqc4qg3vMUyXkJUZNA24daOBRq3kR1px6nSZq6tVLR9psRIAvIof7OkEG59SOscyGs2_E_19_Nw1QCH91sznSKqEPnU--fwB0ZVUHbQ-HEzC_FaDbL3AZkHAI1)
40. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8Nuc9LBTswbbNnqGeo_cu286avH5BGDNPlxpHpgCD3Z4VAnXMTtzPAV9XgEAKnqFwLajqtLGjieHeLsSpfJgHPBsSU_4GaLscVao5dh5mQK91FGoJua9gzQdVj5FaGOBG6dpbY89d0A_tgvuNRp8=)
41. [gatech.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFoGhcXhLU6JOI0UYLhoCI0lFP1bwKZGJzJw7Y9MnPwe2SR3kNioR_Jnl2DaqqjlfXV40WppxRt6_Q0PK3QsMfvxYgIkoOnvVCmcIUdujVIVmO30B5jSd-zpUnAnY7KVmE=)
42. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBXhwyu__dcx8d8PxENlvPhmxaKKu0oWooTZ5g-jjnZTTC0bNjpoYDfEc6Rx-FnHTLP8SAGPgsG6YxG3--1EjDrNYmQ41Jm4mD5zjWWg_1rR8QVaEO8w==)
43. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmYSJGW1IAkycn0BhaDbO6guUR2UP4_0alX0BvXk2qFtfUn9Eg1mITPT-XwxaM4vRM-NYhz8r0774UZrHEQfDtAZZg4tUZ84ZY2NCoz6C7QZh8VI8YFuUTdEx-Klp_yO-C_SMA)
44. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFmQC-1gqGc_ifntqVNOf-Yn5_h5HJb7aeAtxRVM7Q9AT3yTvMmA2wjdGUYlHG5NVPf6tvbVCzoFptf82kzUry4nJibfuJ2zc3a_B-orz8hrLKswNYpOvmKB6l9ZL-_E86l1S4DhKwR7fWxu1zCFrVLNI=)

