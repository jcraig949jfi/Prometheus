# LAD-05: Open-ended conjecture-formation systems compared

**Pythia queue id:** 62
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdlbGtNYXFTUktPLXcxTWtQdEthYm1BaxIXZWxrTWFxU1JLTy13MU1rUHRLYWJtQWs
**Elapsed:** 441s
**Completed at:** 2026-05-19T12:44:36.233613+00:00

---

# Automated Conjecture Formation and Algorithm Discovery (2024-2026): A Comparative Analysis of IRIS, AlphaEvolve, OpenEvolve, and AlphaGeometry

*   **Key Points:**
    *   Between 2024 and 2026, artificial intelligence systems for automated conjecture and mathematical discovery transitioned from purely symbolic engines to hybrid neuro-symbolic and evolutionary frameworks. 
    *   DeepMind's **AlphaGeometry** demonstrated that combining a neural language model with a symbolic deduction engine, trained on vast synthetic datasets, can solve Olympiad-level geometric proofs at a gold-medalist tier.
    *   **AlphaEvolve** (Google DeepMind) and its open-source counterpart **OpenEvolve** reconceptualized algorithm discovery as a code-evolution problem, utilizing Large Language Models (LLMs) as "semantic mutators" within a continuous evaluation loop to break decades-old mathematical stagnation.
    *   The **Inequality Ranking and Inference System (IRIS)** introduced a rigorous geometric and heuristic scoring methodology to numerically evaluate the structural significance of generated conjectures, mitigating the overwhelming noise typically produced by automated conjecturing systems.
    *   While these systems exhibit superhuman capabilities in verifiable search spaces, evidence suggests they still fundamentally lack the abstract, qualitative human intuition required to independently define what constitutes an "elegant" or "interesting" mathematical problem.

**The State of Automated Reasoning**
Recent advancements indicate a paradigm shift in how artificial intelligence approaches rigorous mathematics. Early AI systems struggled with complex geometry and theoretical computer science due to acute shortages of human-annotated training data and the innate brittleness of rule-based logic. It appears likely that the integration of Large Language Models (LLMs)—which excel at identifying patterns and proposing intuitive leaps—with deterministic automated evaluators or symbolic engines has successfully bypassed previous bottlenecks. 

**Evolutionary Code Generation vs. Symbolic Proofs**
The landscape is currently bifurcated into two dominant methodologies. On one side, neuro-symbolic systems like AlphaGeometry synthesize enormous amounts of data to master rigid mathematical domains, prioritizing formal proofs. On the other side, systems like AlphaEvolve and OpenEvolve treat the problem space dynamically, iteratively mutating code to optimize scalar rewards, thereby discovering novel algorithms. Research suggests that while both approaches are highly effective within their respective bounds, they remain constrained by the necessity of automated, machine-verifiable evaluation loops.

**The Valuation of Conjectures**
A central challenge in automated mathematical discovery is not merely generating valid statements, but identifying the statements that actually matter to human mathematical theory. Frameworks like IRIS have been developed specifically to address this, assigning numerical values to conjectures based on geometry, sharpness, and novelty. The evidence leans toward a future where generative AI acts as a relentless proposer of ideas, while sophisticated ranking algorithms and human-in-the-loop oversight curate these outputs into cohesive scientific knowledge.

## Introduction to Automated Conjecture Formation

The quest to automate mathematical discovery is foundational to the field of artificial intelligence, tracing its roots back to early theorem provers and heuristic-based conjecturing programs like Graffiti [cite: 1, 2]. However, the period spanning 2024 to 2026 has witnessed an unprecedented acceleration in the capabilities of automated systems. This surge is largely attributable to the maturation of Large Language Models (LLMs) and their integration into complex scaffolding systems that ground their statistical creativity in rigorous, deterministic environments [cite: 3, 4]. 

In isolation, standard LLMs like GPT-4 frequently hallucinate, making syntactic and semantic errors when attempting formal mathematical logic, often yielding a success rate of 0% on complex Olympiad-level tasks [cite: 5]. To circumvent this limitation, contemporary systems have adopted specialized architectures. This comprehensive academic report provides a comparative analysis of four state-of-the-art systems developed or prominent between 2024 and 2026: **AlphaGeometry** (and its successor AlphaGeometry 2), **AlphaEvolve**, **OpenEvolve**, and **IRIS** (Inequality Ranking and Inference System). The comparative analysis evaluates these platforms strictly across four primary axes: methodology, output quality, evaluation framework, and claimed novelties.

## AlphaGeometry: Neuro-Symbolic Theorem Proving

Announced in January 2024 by Google DeepMind and published in the journal *Nature*, AlphaGeometry represents a watershed moment in automated geometry theorem proving [cite: 3, 6]. Designed specifically to tackle Euclidean plane geometry problems from the International Mathematical Olympiad (IMO), the system successfully bridges the gap between neural intuition and symbolic rigor.

### Methodology
AlphaGeometry employs a fundamentally **neuro-symbolic architecture**, explicitly modeled on the cognitive psychology framework of "thinking, fast and slow" [cite: 3, 7]. The architecture is composed of two distinct but deeply integrated subsystems:
1.  **A Neural Language Model (The "Fast" System):** This component is responsible for providing quick, intuitive ideas. When a problem reaches a deadlock, the LLM predicts and proposes potentially useful auxiliary geometric constructs (such as adding a new point, line, or circle) that could open up new pathways for deduction [cite: 3, 6].
2.  **A Symbolic Deduction Engine (The "Slow" System):** Comprising Deductive Database (DD) and Algebraic Reasoning (AR) engines, this rule-bound component performs rigorous logical reasoning and algebraic computations using classical geometry rules (e.g., angles, similar triangles) [cite: 3, 6]. 

The operational loop dictates that the symbolic engine attempts to deduce all possible statements from the problem's premises. If a proof is not found and new statements are exhausted, the LLM is queried to generate a single new auxiliary construct. The symbolic engine then resumes deduction using the expanded premise space. This cycle continues until a solution is achieved or computing limits are reached [cite: 7, 8].

Crucially, AlphaGeometry bypasses the lack of human-annotated geometric proof data through massive synthetic data generation. DeepMind generated one billion random diagrams of geometric objects and utilized a traceback algorithm to extract minimal proofs and premises [cite: 5, 9]. This massive dataset was subsequently filtered down to 100 million unique, high-quality theorem-proof examples, which were used to pre-train and fine-tune the LLM completely independent of human demonstrations [cite: 3, 5].

In February 2025, DeepMind released **AlphaGeometry 2**, which utilized a fine-tuned version of the Gemini model. This iteration expanded the representation language to accommodate problems involving moving objects and linear equations of ratios, distances, and angles, allowing the system to cover 88% of IMO geometry questions from 2000 to 2024 [cite: 6, 9].

### Output Quality
The output quality of AlphaGeometry has been widely praised by domain experts, including former IMO gold medalists, for being "verifiable and clean" [cite: 3, 10]. Unlike previous AI approaches to formal mathematical proofs (which were often "hit-or-miss" or generated highly convoluted, unreadable outputs), AlphaGeometry produces solutions with machine-verifiable structure that simultaneously read like classical, human-authored geometry proofs [cite: 3, 8]. 

Quantitatively, AlphaGeometry achieved exceptional results. On the IMO-AG-30 benchmark—a set of 30 Olympiad-level classical geometry problems compiled from competitions between 2000 and 2022—AlphaGeometry solved 25 problems within the standard Olympiad time limits [cite: 3, 10]. This massively outperformed the prior state-of-the-art algebraic baseline known as Wu's method, which only solved 10 problems [cite: 6, 11]. AlphaGeometry's score of 25 approaches the average performance of human gold medalists, who historically solve an average of 25.9 out of 30 comparable problems [cite: 7, 10]. 

### Evaluation Framework
AlphaGeometry's primary evaluation framework is grounded in the **IMO-AG-30 benchmark**, a rigorously specialized environment for classical geometry designed to test the system against the world's most difficult high-school mathematical challenges [cite: 11]. The evaluation is deterministic; because the output is formal logic, its correctness is independently verified by the symbolic engine [cite: 3]. Furthermore, qualitative evaluations were conducted by human mathematical experts to assess readability and structural elegance [cite: 5, 10].

### Claimed Novelties
1.  **Massive Synthetic Data Generation:** The automated synthesis of 100 million unique geometric proofs successfully sidestepped the historical data bottleneck in AI mathematical reasoning [cite: 3, 5].
2.  **Symbiotic Neuro-Symbolic Loop:** The elegant division of labor between the LLM (for intuitive, auxiliary constructions) and the symbolic engine (for exhaustive deduction) [cite: 7, 8].
3.  **Human-Readable Proofs:** Producing logic that not only satisfies a computer verifier but is indistinguishable from top-tier human mathematical reasoning [cite: 10].

## AlphaEvolve: LLM-Driven Evolutionary Discovery

Unveiled by Google DeepMind in May 2025, **AlphaEvolve** shifts the paradigm from neuro-symbolic proving to open-ended algorithmic discovery. Described as an evolutionary coding agent, AlphaEvolve is designed for general-purpose scientific and algorithmic discovery, capable of modifying and optimizing entire codebases rather than simply completing code snippets [cite: 4, 12, 13].

### Methodology
AlphaEvolve treats the discovery of mathematical conjectures and algorithms as a code-evolution problem. It utilizes an ensemble of large language models (specifically Gemini 2.0 Flash for breadth/speed, and Gemini 2.5 Pro for deep, semantic soundness) acting as "semantic mutators" within an automated evolutionary loop [cite: 4, 14, 15].

The pipeline operates as follows:
1.  **Problem Specification:** A human researcher provides an initial, often highly unoptimized code skeleton with marked evolvable sections, alongside a deterministic, automated evaluator function that can take a program's output and return a scalar fitness score [cite: 13, 14].
2.  **Prompt Sampling:** The system assembles context-rich prompts by selecting "parent" programs from a database, along with their evaluation scores and historical execution artifacts [cite: 15].
3.  **LLM Generation:** The Gemini ensemble generates variations, mutations, or complete rewrites of the algorithm [cite: 4, 16].
4.  **Evaluation & Storage:** The generated code is executed. If it compiles and runs, the automated evaluator scores it. Successful programs are stored in the evolutionary database, becoming parents for the next generation [cite: 4, 15].

Unlike systems that merely predict text, AlphaEvolve interacts with an environment (a compiler and a scoring function) mirroring the scientific method of hypothesis proposal, testing, and refinement [cite: 12]. 

### Output Quality
AlphaEvolve has generated output of astonishing quality, resolving problems that had stagnated for decades. The system was tested across a diverse array of domains:
*   **Matrix Multiplication:** AlphaEvolve developed a search algorithm that discovered a procedure to multiply two 4x4 complex-valued matrices using only 48 scalar multiplications—representing the first improvement over Strassen's algorithm in this setting in 56 years [cite: 16, 17].
*   **Mathematical Conjectures:** Tested against a suite of over 50 open mathematical problems, AlphaEvolve matched the best-known human constructions 75% of the time, and surpassed the state-of-the-art to discover provably better constructions in 20% of the cases [cite: 13, 18]. It yielded new insights into the kissing number problem and the Kakeya conjecture by optimizing discrete gaussian random variables to improve sum-difference exponents [cite: 16, 19].
*   **Systems Engineering:** In practical applications, the generated code optimized digital circuits, discovered better data center scheduling heuristics (recovering 0.7% of stranded resources), and achieved up to a 32.5% speedup in the FlashAttention kernel used for training AI models [cite: 4, 13].

### Evaluation Framework
AlphaEvolve relies entirely on an **automated execution and scalar scoring framework**. It cannot operate on problems that require abstract, qualitative human judgment (e.g., "Is this proof elegant?") [cite: 14, 18]. Instead, it solves problems framed as optimization tasks, running the LLM-generated code in sandboxed environments, capturing the standard output/errors, and utilizing predefined metrics to establish a fitness score [cite: 13, 14]. This creates a dense, automatic feedback loop that prevents the system from suffering from LLM hallucinations [cite: 13, 18].

### Claimed Novelties
1.  **LLMs as Mutation Engines:** Treating high-level code as the "DNA" of an evolutionary algorithm, with state-of-the-art LLMs intelligently mutating the code [cite: 13, 14].
2.  **Broad Domain Agnosticism:** Unlike previous narrow AI (like AlphaFold or AlphaTensor), AlphaEvolve is a general-purpose agent applicable to any domain where an automated evaluator can be written [cite: 13].
3.  **Closed-Loop Autonomous Research:** The ability to recover from errors and use execution traces (like compiler errors) as context to fix its own bugs in subsequent generations [cite: 16, 20].

## OpenEvolve: Democratizing Quality-Diversity Evolution

Following DeepMind's publication of AlphaEvolve, the open-source community rapidly developed **OpenEvolve**, introduced in May 2025. It replicates the core methodology of AlphaEvolve but integrates several advanced techniques from evolutionary computation to enhance diversity and prevent premature convergence [cite: 13, 21, 22, 23].

### Methodology
OpenEvolve retains the LLM-driven mutation loop but fundamentally upgrades the "Program Database" component by implementing a **Multi-Dimensional Archive of Phenotypic Elites (MAP-Elites)** combined with an **Island-Based Architecture** [cite: 23, 24].

1.  **MAP-Elites (Quality-Diversity):** Rather than just keeping the single "best" program, OpenEvolve discretizes user-defined features (e.g., code complexity, algorithmic structure, diversity metrics) to create a multi-dimensional grid. Each cell in the grid retains the best program for that specific combination of traits. This ensures a diverse population of solutions and heavily mitigates the risk of the system becoming trapped in local minima [cite: 23, 24, 25].
2.  **Island Model with Migration:** OpenEvolve runs multiple isolated populations (islands) in parallel across a distributed system. Periodically, top-performing programs migrate between adjacent islands in a ring topology. This controlled gene flow preserves genetic diversity while maximizing parallel compute [cite: 23, 26, 27].
3.  **LLM Ensemble and Artifact Side-Channel:** OpenEvolve is model-agnostic, interacting with any OpenAI-compatible API. It often ensembles models (e.g., Gemini Flash + Gemini Pro) and utilizes an "artifact side-channel" that explicitly feeds execution tracebacks and standard error outputs back into the prompts to guide the LLM out of syntactic failure states [cite: 22, 24, 26].

### Output Quality
OpenEvolve's output quality heavily mirrors that of AlphaEvolve, successfully replicating several of DeepMind's proprietary results. For example:
*   **Circle Packing:** Starting with a crude concentric ring script, OpenEvolve iteratively transformed the code across hundreds of generations. It transitioned from geometric patterns to grid-based arrangements, ultimately writing code that utilized SciPy's Sequential Least Squares Programming (SLSQP) solvers. It achieved a sum of radii of 2.634, which is 99.97% of DeepMind's reported optimal result [cite: 22, 28].
*   **Function Minimization:** Given a basic random search algorithm, OpenEvolve autonomously discovered and implemented a complete simulated annealing algorithm—deriving concepts like temperature cooling schedules and adaptive step sizes without explicit programming instructions [cite: 21, 22, 29].

### Evaluation Framework
OpenEvolve utilizes a **Multi-Stage Cascade Evaluation** pipeline. Users define multiple stages of evaluation (`evaluate_stage1`, `evaluate_stage2`, etc.) with escalating thresholds. This filters out weak or broken candidates rapidly, reserving expensive compute and longer timeouts for highly promising programs [cite: 24, 26]. The framework also natively supports Multi-Objective Pareto optimization, allowing developers to balance complex trade-offs automatically [cite: 26].

### Claimed Novelties
1.  **MAP-Elites Integration:** The first successful integration of quality-diversity evolutionary algorithms with LLM-based code mutation, ensuring the system values "inspiration" as much as sheer "performance" [cite: 23, 27].
2.  **Island-Based Parallelism:** Allowing for highly scalable, cross-machine, deterministic evolution runs [cite: 26, 27].
3.  **Open-Source Agnosticism:** Complete configuration flexibility allowing multi-language support (Python, Rust, R, Metal shaders) and any LLM backend [cite: 13, 26].

## IRIS: Inequality Ranking and Inference System

While AlphaEvolve and OpenEvolve generate code to hunt for optimal values, mathematics is deeply concerned with the formulation of formal theorems and bounds. The **Inequality Ranking and Inference System (IRIS)**, introduced at the ICML 2025 Workshop on AI for Math by researchers from Duke University and affiliated institutions, addresses the critical issue of *evaluating* and *ranking* mathematical conjectures [cite: 30, 31]. *(Note: In the context of 2024-2026 AI literature, the acronym IRIS is also occasionally used for the "Interactive Research Ideation System" [cite: 32], an MCTS-based literature synthesis tool; however, for automated conjecture formation, the Inequality Ranking framework is the primary focus of this analysis).*

### Methodology
IRIS approaches conjecture formation as a problem of **Theory Selection over Invariant Tables**. Instead of generating chaotic arrays of random formulas, IRIS focuses on linear inequalities over numerical invariants (e.g., graph structures, knot features, or convex geometry metrics) [cite: 31, 33]. The methodology builds upon and re-engineers the legacy pipeline of Graffiti/TxGraffiti, elevating it for modern machine learning environments [cite: 1, 30].

The IRIS pipeline operates through the following steps:
1.  **Conjecture Generation:** Candidate inequalities are proposed over a dataset of objects (rows) and their invariants/predicates (columns) [cite: 33].
2.  **Geometric and Heuristic Scoring:** IRIS interprets these inequalities as hyperplanes in a high-dimensional data cloud. It calculates a numerical score based on multiple dimensions of mathematical significance [cite: 31].
3.  **Automated Counterexample Discovery:** Instead of relying purely on static data, IRIS features an automated counterexample engine. It uses Graph Neural Network (GNN) embeddings and Proximal Policy Optimization (PPO) reinforcement learning to aggressively attack the generated conjectures, successfully refuting up to 95% of weak or false proposals [cite: 30].

### Output Quality
The output of IRIS is not a single proof or algorithm, but a **compact, highly prioritized library of surviving mathematical conjectures** [cite: 1, 33]. These conjectures are formatted as human-readable statements (e.g., \( H \implies \Phi \)) accompanied by structured numerical valuations [cite: 33]. 

By defining the "touch set" of a conjecture—the specific data points that lie exactly on or infinitesimally close to the boundary defined by the inequality (\( |a^\top x - b| < \varepsilon \))—IRIS is able to identify mathematically "sharp" bounds [cite: 31]. A notable qualitative success of IRIS involved uncovering an unexpected correlation between algebraic invariants (knot signatures, \(\sigma(K)\)) and geometric quantities (natural slope), yielding conjectures of the form \( |2\sigma(K) - \text{slope}(K)| < c_1 \cdot \text{vol}(K) + c_2 \) which were subsequently proven by human mathematicians [cite: 31].

### Evaluation Framework
The evaluation framework of IRIS is intrinsic to its purpose: it is itself an evaluation system. It judges conjectures based on:
*   **Sharpness:** How closely the inequality bounds the actual objects (the size of the touch set) [cite: 31].
*   **Diversity & Novelty:** Whether the conjecture explores new dimensional spaces compared to already accepted theorems in the library [cite: 31].
*   **Difficulty:** The robustness of the conjecture against the PPO-based counterexample generator [cite: 30].

### Claimed Novelties
1.  **Numerical Valuation of Conjectures:** Shifting the paradigm from binary (true/false) to continuous valuation, acknowledging that even refuted conjectures provide vital geometric boundaries and insights [cite: 31, 33].
2.  **GNN + PPO Counterexample Generation:** Integrating deep reinforcement learning with graph neural networks to actively play the role of the "skeptic," iteratively stressing the conjecture library [cite: 30].
3.  **Geometric Formulation of Theory Selection:** Utilizing convex geometry concepts (like exposed faces of data clouds) to formalize what makes an inequality "interesting" [cite: 31].

---

## Comprehensive Comparative Analysis

To understand the trajectory of automated mathematical discovery, we must synthesize how these four systems intersect, diverge, and complement one another across the predefined criteria.

### 1. Methodology: The Architecture of Discovery

The methodological philosophies of these systems highlight three distinct approaches to AI in mathematics: **Neuro-Symbolic Search** (AlphaGeometry), **Evolutionary Meta-Programming** (AlphaEvolve, OpenEvolve), and **Geometric Theory Selection** (IRIS).

| Feature | AlphaGeometry (1 & 2) | AlphaEvolve | OpenEvolve | IRIS |
| :--- | :--- | :--- | :--- | :--- |
| **Core Paradigm** | Neuro-Symbolic | Evolutionary LLM Agent | Evolutionary Quality-Diversity | Geometric/Heuristic Ranking |
| **Primary Engine** | LLM + Deductive Engine | LLM + Code Evaluator | LLM + MAP-Elites Grid | GNN + PPO + Invariant Tables |
| **Data Reliance** | 100M Synthetic Proofs | Zero-shot / Code history | Zero-shot / MAP-Elites history | Pre-computed Invariants |
| **Generative Action** | Proposing auxiliary constructs | Mutating full source code | Mutating full source code | Generating linear inequalities |

**AlphaGeometry** operates strictly within formal deductive logic. The LLM is heavily constrained; it cannot hallucinate a false proof step because every assertion must traverse the symbolic DD+AR engine [cite: 3, 8]. Its intelligence is derived from the sheer volume of synthetic data (100 million examples) injected during pre-training, giving it a profound "intuition" for classical geometry [cite: 3, 5].

Conversely, **AlphaEvolve and OpenEvolve** utilize LLMs in an unconstrained, highly stochastic manner. The LLMs write raw text (code). They are not trained on billions of synthetic proofs; rather, their power comes from the **evolutionary loop** [cite: 12, 21]. If AlphaGeometry is analogous to human logical deduction, the Evolve systems are analogous to natural selection. **OpenEvolve** drastically improves upon AlphaEvolve's methodology by implementing **MAP-Elites** [cite: 25]. Where AlphaEvolve might aggressively optimize toward a single local minimum, OpenEvolve's grid architecture forces the LLM to retain programs that are sub-optimal but structurally diverse, ultimately leading to more profound algorithmic breakthroughs (like discovering simulated annealing from random search) [cite: 23].

**IRIS** stands apart. While the other three systems seek to *solve* existing problems, IRIS seeks to *discover the problems themselves* [cite: 31, 33]. By treating conjectures as hyperplanes in a dataset of invariant vectors, IRIS applies geometry to evaluate mathematical text. Furthermore, the inclusion of a PPO reinforcement learning agent specifically trained to break conjectures represents an adversarial methodology not present in the generative loops of the DeepMind systems [cite: 30].

### 2. Output Quality: Verifiability, Creativity, and Impact

The metrics for "quality" differ vastly depending on the system's objective.

*   **AlphaGeometry:** The output is **formal, human-readable proofs**. This is a monumental achievement because historical systems (like Wu's algebraic method) produced proofs that were mathematically valid but incomprehensible to human mathematicians [cite: 10, 11]. AlphaGeometry outputs classical geometry rules—angles, similar triangles—mimicking a human student [cite: 3]. The quality is unequivocally world-class, matching IMO gold-medalist averages (25/30) [cite: 3, 10]. 
*   **AlphaEvolve / OpenEvolve:** The output is **executable code (Algorithms/Heuristics)**. The quality here is measured by optimization metrics against historical benchmarks. AlphaEvolve's discovery of a 48-multiplication algorithm for 4x4 complex matrices broke a 56-year stagnation [cite: 17]. OpenEvolve's generation of advanced optimization scripts (e.g., reaching 99.97% of the state-of-the-art in circle packing) proves that the evolutionary LLM approach yields superhuman heuristics [cite: 22]. However, the code output is strictly functional; as noted by mathematicians evaluating AlphaEvolve, the system cannot output "elegant" conceptual proofs or unify disparate fields [cite: 14].
*   **IRIS:** The output is a **ranked library of linear inequalities**. The quality is measured by the *sharpness* of the bounds and the survival rate against adversarial counterexamples. The system successfully curates human-readable statements that highlight genuine mathematical structure while filtering out illusory statistical patterns [cite: 31, 33]. The fact that its conjectures have led directly to human-proven theorems in knot theory demonstrates exceptional theoretical quality [cite: 31].

### 3. Evaluation Frameworks: The Anchors of Truth

Because LLMs inherently hallucinate, all successful automated conjecturing systems rely heavily on robust, deterministic evaluation frameworks to ground their outputs in reality.

| System | Evaluation Mechanism | Verification Type | Limitations |
| :--- | :--- | :--- | :--- |
| **AlphaGeometry** | Symbolic Engine (DD+AR) | Logical Deduction | Confined strictly to formalized Euclidean geometry; requires massive synthetic data. |
| **AlphaEvolve** | Sandboxed Code Execution | Scalar Fitness Score | Cannot evaluate abstract math concepts; limited by computational intractability of tests. |
| **OpenEvolve** | Multi-Stage Cascade Evaluation | Scalar Score + Trait Maps | High compute cost for maintaining parallel islands and MAP-Elites grids. |
| **IRIS** | Geometric Touch Sets & PPO Agent | Statistical & Adversarial | Limited to linear inequalities over pre-defined numerical invariant columns. |

**AlphaGeometry's** evaluation is self-contained. The symbolic engine verifies every step logically. If the engine cannot derive the conclusion, the step is rejected [cite: 3, 8]. The ultimate benchmark, IMO-AG-30, provided a static, highly prestigious yardstick for its success [cite: 3, 11].

**The Evolve Systems (Alpha/Open)** require the human user to write an automated `evaluate()` function [cite: 14, 24]. This is both their greatest strength and their fundamental limitation. As highlighted in literature analyzing AlphaEvolve, conjecture generation often requires intuition about mathematical significance that is not easily mechanizable into a scalar score [cite: 14]. If a problem cannot be reduced to a programmatic unit test that executes quickly, the evolutionary loop breaks down. OpenEvolve mitigates some evaluation bottlenecks by implementing "cascade evaluation," stopping the execution of weak programs early to save compute time [cite: 24, 26].

**IRIS** utilizes the most philosophically distinct evaluation framework. It posits that a conjecture's value does not depend solely on its ultimate truth [cite: 33]. A refuted conjecture in IRIS is not a "failure" (as a compilation error would be in AlphaEvolve); rather, refutations help locate the boundary of genuine structure [cite: 33]. By analyzing the "touch set" (the data points that make an inequality sharp), IRIS numerically grades conjectures based on how tightly they constrain known objects [cite: 31].

### 4. Claimed Novelties: Breaking Through Stagnation

Each system claims specific novelties that push the boundaries of AI-assisted scientific discovery.

**AlphaGeometry** claims the elimination of the human-data bottleneck [cite: 3]. Prior AI struggled with math because there is no internet-scale dataset of formalized proofs. DeepMind's generation of 100 million synthetic diagrams fundamentally solved this, allowing an LLM to learn the "language" of geometry natively [cite: 3, 9]. 

**AlphaEvolve** claims the realization of the autonomous "AI Scientist" loop [cite: 12]. It treats LLMs not as conversational agents, but as genetic mutation operators applied to high-level semantic structures (source code) [cite: 13, 14]. The discovery of entirely novel algorithmic optimizations (e.g., matrix multiplication, Kakeya conjecture improvements) without explicit human demonstrations of those algorithms represents a paradigm shift in programmatic search spaces [cite: 17, 20].

**OpenEvolve** introduces Quality-Diversity to LLM coding agents [cite: 23, 24]. By claiming the first successful integration of MAP-Elites with LLMs, OpenEvolve solved the problem of premature convergence in AI optimization. It proves that to find the best algorithmic solution, an AI must be incentivized to maintain diverse, weird, and sub-optimal solutions along the way [cite: 23, 25]. Additionally, its open-source, model-agnostic nature democratized access to DeepMind-tier evolutionary systems [cite: 21, 29].

**IRIS** claims the mechanization of mathematical taste. By assigning numerical values to the nebulous concept of a conjecture's "significance" through geometric touch sets and diversity metrics, IRIS provides a scalable framework to manage the exponential explosion of machine-generated hypotheses [cite: 31]. Its application of PPO to autonomously hunt for counterexamples creates an adversarial self-improving loop specifically tailored for theoretical mathematics [cite: 30].

## Limitations and Future Directions

Despite these profound achievements, a critical consensus emerges from the evaluation of these systems: **Artificial Intelligence cannot yet define mathematical significance on its own.**

AlphaEvolve and OpenEvolve are blind optimizers; they can minimize a function brilliantly, but they cannot answer the question, *"What is an interesting conjecture about this dataset?"* [cite: 14]. They require humans to write the code skeletons and define the exact scalar parameters of success [cite: 14, 28]. As noted by researchers, when OpenEvolve was tasked with a circle-packing problem, the LLM ultimately chose to act as a thin wrapper around a classical SciPy NLP solver—demonstrating that the AI is often best utilized as a meta-orchestrator of classical tools rather than a pure discovery engine [cite: 28]. 

AlphaGeometry remains strictly confined to its domain. The Deductive Database relies on domain-specific, hardcoded classical geometry rules [cite: 6]. Its applicability to broader mathematics (like topology or number theory) is highly constrained by the necessity of generating customized synthetic data engines for every new field [cite: 6].

IRIS addresses the problem of significance by mapping it to geometry, but it is currently constrained to linear inequalities and relies heavily on the pre-computation of invariant tables [cite: 31, 33]. 

Moving forward into 2026 and beyond, the trajectory of automated conjecture formation points toward the synthesis of these systems. We can anticipate architectures that utilize the **Quality-Diversity evolutionary loops of OpenEvolve** to generate novel mathematical invariants, pass those invariants to **IRIS-style heuristic rankers** to formulate significant conjectures, and finally hand those conjectures to **neuro-symbolic provers like AlphaGeometry** for formal verification. The era of AI acting as a passive tool for mathematics has definitively ended; it has now entered the role of an active, highly capable algorithmic collaborator.

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPB81Cund3bTjlJkiMHVIIP1GWchwzloPukg-1DndeO2QU0MF3TGudr2eDNTXkDl2tFggp9mX0m_ewL049BSs2SdN_fM7nEc_HEMPDG5g6q4xWUr3SeQeS4qE-_MQ2FctGI7C1q-Z19sETfOgt3t2LpfNEW5VmwQ4ucgXV_36bkGDI9Bvv-37jI18zoINmVRiuG0nGUIYCaH-JeLP3cm25LASiI5tKDtZ0HGCTTXf9CQ==)
2. [jair.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgCePULDraO0gv67jgBsYMA1JCDl-i-Cj9ex-_TSoBRbSy306CZpkWVxNilERPQ7zbWE214gQgisISBddMbdipXD3DrTqNh3P1wFTaCAZIkDqPK7_Xv8CcHAmZO67f-6op5mHtmzi1jvdIhw1HUIp_-hagGxmrnsKW6FMT)
3. [deepmind.google](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrQRfUE0xc2DD6oKT6o_UDKQeySQg3Q3iK5VOXMddSKJlKpxLxYnm0haCfJiHQjSIrVms1LmADG5nzEWYwh_yZrYfARbMb5d9M1bI_AmUkyhiHX3DtaVpKv_VzTSJ--z06kiCZRCyp0T6RlPufk8mfhEq1oQBn2PIgH2msjZDhGYzn54Z9X1Uu4Sw=)
4. [deepmind.google](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmATqAESVkwGuhp4Mayl-jLvg7uEAsAsF1kvqWCo67lWXbQLcRwrfHV_Ie9p6GA3H9y4PSujFoMDVAKftbdI2EpzIHm7X5xP6IBCSOS7mjVnU217sWnKFUz2AckqWvI_vk0a9xJy6TqExKAc52q0zk8rxDJR54wmu9lIovHcQqw-kGA5--i3Ojq8H3uRGOyMJTL3QznK7f0SeKQx54CQ0=)
5. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBvQup_aZ_uQKeK0zB6uIiYNhYmChWEraJ65av04LYfUn2ODDd4awWOOC2Q90shKjuO_0wIN56Zkx8PF0NN-bHqAZT7eFabZ-eVTZLr8adr5JckzEJ_HgJtMrZXa0qbDlPEGUwDT5Le1IZwD8Jxy7bMc8_pEi04UfFqDqpVA0p_3Aeu36Fkt8J6YGTBeswCVcEa4k=)
6. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUjK78p52nG8G1WhhqjQfarNoJe94hMHZEH7JzMkuOMSYXN7Qeiq15C3psSpM7GJM-oT_hVagIib8DwTUnmQLf3QjuyQ_2_IgYStEIImTtjWpBTkS_y_7uckzFUT4CDPn3)
7. [cioinfluence.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGb7dr0WyferEwxJ0C9tj_mMffNppyaMk1stcH5bW4F9P75UzFiVRN5DkHWb_btpw7mgFmjNvhDEENI6dz9FJukhzrbThbTq8FBOfygbhZALElxSNWVlhhLjkOBHLeSkoAp6WToKYq3B5MuVgGwEIxWwpdp1pi2Zoq92zBPQKHhFgg3fv0geZH664_gREBQ957gbg60XtA=)
8. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH93WuUWzn__GtT3VF-v5pjA1e1WZjyRVC2GVAS5YFLR6u0sufLCINJ3F939de8Pzi7gbJeW-dQIcZ_nvGi6x39W8JGbbRafv8rjZl4jmX6chmMDll4EKE6XnMNV_KNHyaVomLlH5Epp7K3Ke4aWTVoSkV8Y_sYhquswKOLx8d00T6bOBSf-OBwQgwZcDM0On7pSQQCLCyx448nTeUKaJdoXh5FXXEB2GA=)
9. [imsa.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2kKxTQiakCNLucrHcdWfWLnPZQ9G-8gDgegBtcS9d069akSdT_-AqMgwySUaViSY5rYgbiZK7Bb3TY6L8VSjhjZIAYTA8uA-i949poCw7M4Z--OaDdTOspvICo2iWId4hv4AjBAjZO7XE4DfeeqQsLAdnOVL3XZ3uNLn9VfYjckO5Pr67IM9jzSehiCCIZ0M=)
10. [understandingai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGETyPP1OZAhFnU3aY505J4AlqxMvUKBu_QVTIEhX0x9rJ0QfYEb2U0C25jBnAo295m1FDQSfqOWhyzi3qMXi4u0kVBnPdpQV3MhVIpCHFkP83PBR1qMHjcIuPGXb5OSIVnbFk28_2iMwPAl95V8c6KwfxbwNpZ6YAPr1g4DCaP7A==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3PPo2tpAaPnQigLkIae5VoLSvbHFreQhejjy24zShzaLeJOvZZyGHPT0nFwvBWxl0B-UDN9Eyort0tifuoTK23eQBtPDE_8DEUbVxQCCE77MwQOK-XvKPzg==)
12. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwKDWCX8GB6sbABSd-j8qc3joLrMAtYB5mxeG4G4LCz0uereBquczYvsjJBkWxj_BQFP2rT9-exxFloiZ-EdM5cIpLcSU3b9rdcs9BaFeB6gUpTOFiD4bDjXZAc-tsBm8oiptQbWlAUSpuXbX3kmrVSDFi20v93n6DgOiMEbAjgYKJ7e3DSZA=)
13. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3NHfpjibWz9NegR_29WjHOMSGY3GNrv0ukcRvecX27Pu0rK-uft0NyXbhau6_XIaiAayk5rlYIO8o7RdM33X5sXOO4Ullhg8aEWHkGv8_fRvLj50ewSuKfihskts_Pg==)
14. [rewire.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJW3EnuxrKMVCTaMcNA_s88-QIYjCG-kyZbqjOJiF4bYp0F8Hh4uvnY-bXkTkddpOsol-AYN7qcxxIzXykxg_oL1ltEtGc0a5OmzHdZSK-hvGw4DW56goJCHIB3mYn9fdcSxlmREmxcxkCLuKZnqN-V9QS7qllX8uvN81zJF-zkWz4VkGMZg==)
15. [composio.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVA-V0PzhwNWLg7mUTdCKYgCSvBWN8z8IJ5ZNRu9gTGU01BFMGjRt1W3DiXwceuk0G_JCQL2TMgo6_GIGugr5xOgXol97fieybg4uHIzEw3lp2XTJ5OxpuFzmjX06usQJLWSZaWo1oFhRSJp1m3lxyZN9IvbdkM-fTq2pjj8J7)
16. [deeplearning.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1-hJHBlJjSJFPh2SWF7Y8zsCdOOUVi2_qYJd4ySp1fVyihvtnQSo0LCxOZ6sda-4srUOcfPMLPYTTprYEkm7shlI7ps80fTaQzMqE3LQBbQOcHtAmafqwbuBrk7w760UpalF_hBedFhlwPzprqBGEgskkDnXrb7tbwMdG4Wzb-B0kSkCkEb6UnDBWTB38R2s2GtKN6xa14vfdxjGuIF-AG4XEKo5GXre2_uuyw4-1NbWrMkOHlmmZORUzdN8DEI54HPFrkq93T5MFqxUp2FpIAVmZRggDZsJZmzBsIcUH2jETw7912tFv-Bc2nZ-8Xh7yd0Shb1cltxa51Y4V4iSB00yJrebJSp7l_lzO2aRl7VJgRf-Ln8S_qhXPEWhKXovl-PXgSOJnItCTnYrRGrvSGhpUqOHi2aUU3IRJo--_HTW38UyY5g13n3j-mL8Hcl0qCAY_eT12-RA=)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrljVfop1lchT5WPdFGA0LkvXZD8gXDvQAX6M60i8Qu88khrfTOMYtfnJV1uEYgE_RFyEhDd_sm74JkfD-uPdzVtMo7WN48UeOgN2hf0DCvNJ3cnQK7g==)
18. [googleapis.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDHKiVHo9pZprnvjngv6unV3PoDx3wunEJ0YgkYwELcIK_UEvkZpj7o2gTq3708HXFZRkeZl6ZWS2xCKEBRYdzY9RbW2cpqALErw51YY9-0OzVoBxO5ROszNOQH3OZwAqsL_BIflqAtpI_l-RX0W_pwWds0t-nRDvTKUyRsuoYJMoG78TUthMND-5O-KT3POPgRS4emcPyLGX3jsza8e0AGjePiPDMxJKjVv28304IlR0diekTvP0PoyWSSk1x0Z9GSyWyU02CY67jIQzNHhGJ7vw=)
19. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5W0OodfgiGAj18-4-I0AVXv45ObRdgPOLT3nbM_xq4eYuEAUuc1VdBtJ1RP4VtN8gMbxpjMckuDfW-6GPokNjProcCLSYPFhtW1iFIB-sSwk9-Tqpg6YoGJjXSSOZU43cNrwNOA==)
20. [decrypt.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9X1cIZsM1XjtnBcfEKujdGq0p6CryHZsO_R5JAMDLlwlZzNnywNHd2tamTTKEbAQqCRtlRNF2tma7DjRsKay8_SF9h7qKedKru-qpqh-aS59pB_4iSmWbGWCV2zosOcZDaa0R4dLZYe83nMSLtOGyHis_7F7x8de55auvaRfHk4LZWvctTL7qUWlVVgWr8A==)
21. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETKcWWZKCE0qtlW1YBGjZuLHr7PuuftVDVW-ElNmPyzpPbzUoXaT5yHE98K3_7imaCum4LIgoX-CmCV4UWfNgC9Dz0SL2k99PofOyYZEwRnE8ETJbI-YJKK7oFUkO5MuS6XU8Mjw==)
22. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJH9GThIOv5TS9_MeGc1sULZbbdCrekqNKtbyTBK_XgRwKPdMJUhaBeIs1WXDOka3wNg5CMf2EEFqNyjfKKBELQ0SVG7MygBEnAwbI7Wsnq46Vnp327x06t4ClTy0STpwmDDvlJSf7S_p9Bf6PxCnGx7mVJunjt1Zjw3hTRxDfrV1oFYBW1P9ck5AxSdEiEy3OPioh4Zs1GisCKw==)
23. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJ4AwItBTqAXoNIwjZJYH4mA3lkgggKHYG__M0fWYucphsKPPQdSWX082a2VnOZTXu9YZa3Us97dmQBXyjVhRNNoHMN7j7_PKyPnHit_wOHYUTj_u4oux44uNSHWL7F6vYIqea9dz3alr1jT-m_1ql8WPS0aT4BZ0s29KRNiZV37kT8-BSBBMzYGAp5700W5uhOs3RfdMWhA==)
24. [algorithmicsuperintelligence.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF10Ev_Nd0CONUlLVAIUuU3sOmYeyV8q2xbtAHjh0xOExGcSoVAgmTvFH03LRcccRa9YGnrPBYAO-Wh43ThwKkcntkb32ZpoS79oKSaPTn2DEHyyVT34fSXYaL5-q-69oJOb1M1Yqd65qtpatAfMFjnaWz7MCRIzg==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOzV50W2nBb7Pr3lvRg9QwvryynDajOupxv4oDz46pE5g4jHG83ZmEepFvPLPu7B7Hd0x-SgkxWQnLQbhmhoPmd3Up0dAZhwUkNJ8bQkETFCYJ10kSzsnSoQ==)
26. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1qWiFBQ0-6u3X0ajR12g5BpzdbXyym6Np0TwLdEZGPdl09wv3Z2kjbh1ewKdNnPVouOdmaN08yS536UvrSdIr-02o3kN1qfgHaxRbpfYxV203Ocw5yrQ_d2Naei5VAf4gZqDynOLaN_VZYjooUZ1x)
27. [pypi.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqmLDFadpluotGy6NhZ1yfWkLbnn7Gc3VHJZClUFdh40p8OuC3LeFaQKXapDr6pMZ7E_S3AzhrC-QzUHxoPGaI36023yUQijc41dpssSnH-3g8UNugztDQcXgqlQDGW1s=)
28. [pokutta.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyzWUNLyJ2hDJgQCa68mOIwxvPKRSmRnUu_9x0Bmqn-GbSejgHbzjsZ3WySjntAOVYi_TqXu63FLbd2zjiqaR9ArZOGanJeC_v1QYa7tP0rA3UkR9eXaDs0_5IaPv500msmvtMs2JDa2dwRQF7uG-vGoAJ7A==)
29. [ycombinator.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHR3SG30IlHxD_7ZQnHvZnvYUiSXh7Gh1d4prWdJ7wMLC-HFnVgCKoi-JLl6r5mGUOKao42zNvaYnOxAvFDVL0wafar5U-I12sOAi2guxjqGKwemfRPEVjd5ShYv5E9NwoL5cQ=)
30. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6nsMTq2NB8KHIHhBQvH8xH_OqX21yHpWDlBIitB0i20gELts1J_ER11sx_NAzL7FmGUmne7BnGqGf6E116K2KmrZTYEHKFD4KtfBkRXK0y8G4vkFNq9tjyNM6)
31. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHs_YKIQct6TwCymbccW8sUePaLyIzt4penZPJeODujCFIDNf5hf4yfLDFUWJd_Wq885uiLR5h_poIyJyJfyPAHWENPvEe9B1xkiWhdNtZxN4-t3soSJt_lMwdlFrNx)
32. [takara.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFz-RmKpP9ffjsxvp_Fl3f1CylmaQy69SINGJpyM7_ypS569OS3isiMCknHUWKcJqaeRojaxDroPe7YEJTRYgLyy0KpWEz0vRDE1i4tgRZOZCTzgXVJDkK5Yw==)
33. [researchsquare.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7Nz-83L3vivnRbymS2NjKP_kbuMcRjgZTIbQB2r37YbpORJQogNWbHde2DL6D0tTgEQILGBBUJ5SKpBuVbdMFRW4Ax_ioCMyHZX1oCK6dN_vnm408nyJNLreSD5m7EPu99HfMryVd33hPeras9PoSh7-xuZVOrsA6qE4ia8frNKS69_lSn5wPazPUDCm2v26ZcRbNtLH0anPpyTMB8zo=)

