# The State of Library Learning and Abstraction Discovery in LLM-Guided Systems (2026)

**Key Points:**
*   **Research suggests** that while LLM-guided abstraction systems (such as LILO) empirically outperform pure enumeration-plus-compression frameworks (like DreamCoder) on specific benchmarks, the underlying mechanisms driving these performance gains are heavily contested. 
*   **The evidence heavily leans toward** the conclusion that many purported "library learning" systems in the 2024–2026 window (e.g., LEGO-Prover, TroVE, DynaSaur) suffer from severe methodological flaws, primarily the failure to normalize computational budgets and the misattribution of performance gains to abstraction reuse rather than simple ensembling (self-consistency) and iterative refinement (self-correction).
*   **It is highly probable** that true cross-task *direct reuse* of learned abstractions in many of these systems is functionally zero. Abstractions frequently fail "leave-one-out" ablation protocols, indicating they are cosmetic artifacts rather than load-bearing cognitive components.
*   **Emerging consensus** dictates that rigorous evaluation of abstraction discovery must involve minimally invasive ablations, strict inference-compute normalization, and direct measurement of verbatim cross-task tool invocation.

**The Evolution of Abstraction Discovery**
The paradigm of library learning—automatically discovering reusable, programmatic abstractions that compress downstream solutions—has transitioned from pure Bayesian top-down enumerative search to LLM-guided neurosymbolic frameworks. Systems like DreamCoder anchored the enumerative approach, while successors like LILO successfully integrated language models to propose, document, and deploy abstractions. However, as these systems scaled into domain-specific applications (e.g., mathematical theorem proving, visual shape modeling, robotics), the definition of a "successful" abstraction became dangerously conflated with raw task accuracy.

**The Ablation Crisis and Load-Bearing Metrics**
By 2026, the field has entered a methodological reckoning. Extensive audits of top-tier systems have revealed that the vast majority of learned abstractions act as single-use, localized heuristics rather than foundational, load-bearing lemmas. To verify that an abstraction is load-bearing, researchers now emphasize metrics such as *direct reuse frequency* and require rigorous *leave-one-out* ablation testing. Furthermore, evaluations must aggressively control for confounding variables, most notably the tendency of naive compression metrics to reward the baseline verbosity of LLMs (Pattern Base Rate Neglect) and the failure of abstractions to generalize beyond narrow problem families (Pattern Conductor Confound). 

***

## 1. Introduction and Problem Statement

The quest to build artificial systems capable of true conceptual abstraction remains one of the most vital frontiers in artificial intelligence. Borrowing from the programming languages (PL) literature, the algorithmic analogue to human concept formation is **library learning**: the automated construction, evolution, and application of libraries of reusable functions, lemmas, modules, or other computational artifacts [cite: 1]. A system engaged in library learning identifies recurring program patterns, extracts them, and adds them to a growing Domain-Specific Language (DSL), thereby theoretically compressing the search space and enabling solutions to increasingly complex downstream tasks [cite: 2]. 

The user's central inquiry operates on a fundamental doctrine: an abstraction or lemma merits algorithmic credit *only* if it is **load-bearing** within a proof-dependency or execution graph. A cosmetic abstraction—one that merely re-labels a sequence of operations without enabling novel generalizations or structurally reducing downstream computational complexity—represents a failure of the library learning process. 

As of 2026, the state of library learning is defined by a deep bifurcation between theoretical promise and empirical reality. On one hand, LLM-guided neurosymbolic frameworks have undeniably achieved state-of-the-art accuracy on complex benchmarks [cite: 3]. On the other hand, a wave of rigorous replication studies and audits has exposed severe methodological vulnerabilities in how these systems are evaluated, casting doubt on whether the "libraries" they learn are genuinely contributing to their success [cite: 4, 5]. 

This report provides a comprehensive, exhaustive review of the library learning landscape as of 2026. It directly addresses the flagged findings regarding the dominance of LLM-guided abstraction over pure enumeration, establishes the current standard for metrics and ablation protocols designed to isolate load-bearing abstractions, and systematically deconstructs the attack vectors that threaten the validity of current research—specifically the inflation of compression metrics and the illusion of cross-task reuse.

## 2. Flagged Findings: LLM-Guided Abstraction vs. Pure Enumeration

The baseline assumption presented in the query is that the **DreamCoder** line [cite: 6] and subsequent LLM-guided abstraction works serve as the anchors of the field, and that LLM-guided abstraction currently outperforms pure enumeration-plus-compression. A thorough verification against primary sources from 2024 through 2026 confirms that this claim is functionally accurate, though the nuances of *why* it outperforms enumeration are critical to understanding the current state of the art.

### 2.1 The Enumerative Anchor: DreamCoder
DreamCoder, introduced by Ellis et al. (2021), is universally acknowledged as the canonical precursor and state-of-the-art baseline for modern library learning [cite: 7, 8]. DreamCoder operates on a "wake-sleep" Bayesian learning cycle inspired by human cognitive structuring [cite: 2]. 
*   **Wake Phase:** A neural network guides a top-down, enumerative search to discover programs that solve a set of training tasks based on the current DSL.
*   **Sleep Phase (Abstraction/Refactoring):** The system analyzes the corpus of successful programs, identifies repeating subprograms (using symbolic compression techniques), and extracts them as reusable abstractions (Lambda calculus expressions). These abstractions are added back into the DSL, compressing the length of synthesized programs and decreasing required search depth for future tasks [cite: 2].

While elegant, DreamCoder's pure enumerative search faces severe limitations. Because it relies on searching through a vast space of symbolic strings, it often requires thousands of guesses to discover solutions to difficult tasks, rendering it highly compute-intensive and prone to combinatorial explosion as the DSL grows [cite: 8].

### 2.2 The Neurosymbolic Shift: LILO and LLM-Guided Synthesis
The breakthrough that validated the superiority of LLM-guided abstraction over pure enumeration was the introduction of **LILO** (Library Induction from Language Observations) by Grand et al. (ICLR 2024) [cite: 3, 8, 9]. LILO enriches the traditional PL library learning model with the vast commonsense and semantic priors embedded in LLMs.

LILO explicitly sought to outperform DreamCoder by replacing and augmenting the purely enumerative search with a dual-system synthesis module. Its architecture contains three core components:
1.  **LLM Synthesizer:** Uses an LLM to guide program synthesis, bypassing the exhaustive string-matching of traditional enumeration by leveraging the model's domain-general priors [cite: 3].
2.  **Symbolic Compression Module (Stitch):** Like DreamCoder, LILO relies on algorithmic advances in automated refactoring. It utilizes **Stitch**, a high-performance symbolic compression system written in Rust, to efficiently identify optimal $\lambda$-abstractions across large code corpora [cite: 3, 8].
3.  **Auto-Documentation (AutoDoc):** This is the critical innovation bridging neural and symbolic reasoning. When Stitch identifies a structurally optimal abstraction, an LLM is prompted with contextual usage examples to generate human-readable names and docstrings [cite: 3, 8]. 

**Verification of Performance:** Empirical evaluations verify the claim that LLM-guided abstraction (LILO) outperforms pure enumeration (DreamCoder). In direct head-to-head benchmarking on tasks such as string editing (regex), scene reasoning, and graphics composition (LOGO), LILO solved more complex tasks, achieved faster search times, and maintained comparable computational costs [cite: 3, 8]. For example, on regex tasks, LILO achieved a +33.14% improvement over DreamCoder [cite: 10]. 

Crucially, the success of LILO relies on the linguistic grounding provided by AutoDoc. Purely symbolic abstractions generated by Stitch are mathematically optimal for compression but are virtually incomprehensible to an LLM at inference time. By assigning natural language semantics to the discovered abstractions, LILO allows the LLM synthesizer to successfully invoke them in downstream tasks, proving that the abstractions are not merely cosmetic but actively deployed to solve novel problems [cite: 3].

### 2.3 Other LLM-Guided Advancements
Beyond LILO, other systems have cemented the dominance of LLMs in abstraction discovery:
*   **LambdaBeam** combined multi-level, execution-guided bottom-up synthesis with neural models, though it initially lacked library learning [cite: 2].
*   **RLAD (Reasoning abstractions via RL)** (ICLR 2026) introduced a two-agent training framework comprising an abstraction generator and an abstraction-conditioned solution generator, proving that conditioning a frontier model on explicitly generated reasoning abstractions improves Pass@1 and Pass@4 accuracy significantly more than simply scaling inference-time compute for raw solution generation [cite: 11].
*   **ShapeLib** (2026) demonstrated that LLMs can author programmatic libraries of 3D shape abstractions that generalize across shape distributions, outperforming prior alternative abstraction discovery works in usability and plausibility [cite: 12].

**Status:** The flagged finding is verified. LLM-guided abstraction, when coupled with symbolic compression engines (like Stitch) and semantic grounding (like AutoDoc), demonstrably outperforms pure enumeration-plus-compression frameworks.

***

## 3. The Ablation Crisis: The Illusion of Library Learning

While LILO proved that LLM-guided library learning *can* work, the application of this paradigm to broader domains (such as mathematics, logic, and planning) between 2024 and 2026 precipitated a severe methodological crisis. 

The core of the user's inquiry concerns **Status and Bounds**, specifically requiring that "a claimed improvement disappear when the abstraction is removed." A devastating series of papers published in late 2024 and early 2026 by Berlot-Attwell, Rudzicz, and Si fundamentally shattered the foundational claims of several prominent library learning systems by applying exactly this ablation protocol [cite: 4, 5, 13].

### 3.1 The Targets: LEGO-Prover and TroVE
Two highly cited systems that emerged in 2024 were **LEGO-Prover** and **TroVE** [cite: 14]. 
*   **LEGO-Prover** was designed for the autoformalization of theorems, converting natural language proofs into formal proofs verified by the Isabelle theorem prover. It claimed to achieve State-of-the-Art (SotA) performance by building a growing library of modular, reusable mathematical skills (lemmas) [cite: 5, 15]. It featured a "Prover" module that solved theorems using LLM proofs while retrieving suggested lemmas, and an "Evolver" module that refined and added new lemmas to the library [cite: 1].
*   **TroVE** generated Python code to solve math word problems, inducing Python helper functions as a reusable library [cite: 1, 15].
*   A third system, **DynaSaur**, achieved SotA on the GAIA agent benchmark through purported library learning [cite: 5, 15].

These systems claimed massive performance increases and attributed them to the successful induction and reuse of abstractions. 

### 3.2 The Findings: Negligible Direct Reuse
Berlot-Attwell et al. subjected these systems to rigorous audits, tracking the exact lifecycle of the generated abstractions. They measured **direct reuse frequency**: the count of how many distinct downstream solutions invoked each tool verbatim [cite: 1]. 

Their findings were unequivocal: **Function and lemma reuse in LEGO-Prover and TroVE was extremely infrequent, bordering on non-existent** [cite: 13, 14].
*   In LEGO-Prover, when relevant lemmas were retrieved and provided to the Prover in its context window, the system frequently failed to utilize them. While it occasionally demonstrated "direct use" (using a lemma to solve the *single* specific problem it was generated for), it demonstrated virtually zero "direct *reuse*" across novel, downstream problems [cite: 15].
*   Most learned tools across these systems were entirely single-use, tailored narrowly to the idiosyncrasies of one specific problem [cite: 1].
*   DynaSaur similarly exhibited low direct reuse of its learned libraries despite claiming SotA performance [cite: 5].

If the abstractions were not being reused, how were these systems achieving higher benchmark scores?

### 3.3 The True Drivers: Self-Correction, Self-Consistency, and Compute Budgets
Through meticulous ablation studies, the researchers disabled the library sharing mechanisms—effectively preventing the systems from accessing the learned abstractions. According to the foundational doctrine of library learning, this ablation should have caused performance to plummet back to baseline levels.

Instead, **ablating the reuse mechanism had little to no effect on the overall accuracy of the systems** [cite: 1, 13]. The claimed improvements did *not* disappear when the abstractions were removed. 

Berlot-Attwell et al. identified three alternate mechanisms that were the true drivers of the observed performance gains:
1.  **Self-Correction (Iterative Refinement):** The library learning architectures inherently structured the search process more effectively. In LEGO-Prover, a failed attempt by the Prover would generate a specific request that the Evolver would later solve. This error-driven exploration allowed the model to bypass dead ends, acting as an implicit multi-turn reasoning chain rather than a library invocation [cite: 1].
2.  **Self-Consistency (Ensembling):** Systems like TroVE relied on majority voting or consensus mechanisms across multiple candidate solutions to select the best answer. The performance gains arose from the statistical power of ensembling, utterly independent of the library's content [cite: 1].
3.  **Compute Budget Effects (The Ultimate Confound):** The most damning finding was the lack of compute normalization. Library learning systems run multiple iterations, execute external tools, and sample heavily to generate, refine, and test abstractions. The baselines they were compared against (e.g., standard prompting or simple Draft-Sketch-Prove methods) were given significantly smaller inference budgets. When Berlot-Attwell matched the computational cost (e.g., measuring API costs in USD or total tokens generated), they found that the **simple baseline of prompting the model consistently matched or outperformed the complex library learning systems** [cite: 4, 5, 15]. 

**Status:** The current state of library learning evaluation is highly suspect. A significant portion of the literature from 2024 to 2025 failed to account for compute and behavior [cite: 4]. Any system that claims to discover load-bearing abstractions must now prove that its gains survive compute-budget normalization and are not merely artifacts of iterative sampling.

***

## 4. Defining and Measuring "Load-Bearing" Abstractions

The user's problem statement asks: *What metrics establish that a discovered abstraction is load-bearing rather than cosmetic?*

To separate genuine cognitive tools from cosmetic refactoring, the field has coalesced around a rigorous set of quantitative metrics and theoretical frameworks as of 2026. The shift has moved entirely away from simple "task accuracy" (which is easily confounded by the factors discussed in Section 3) toward direct mechanistic analysis of the proof-dependency graph [cite: 1].

### 4.1 Primary Metrics for Abstraction Validity

#### 4.1.1 Direct Reuse Frequency
The most fundamental metric for a load-bearing abstraction is **Direct Reuse Frequency**. This is defined as the absolute count of how many distinct solutions invoke a given tool, function, or lemma *verbatim* [cite: 1]. 
*   If a library $L$ consists of tools $\{f_1, f_2, ..., f_K\}$, a tool $f_i$ is only considered load-bearing if it appears in the final execution traces of $N > 1$ distinctly different downstream problems.
*   The absence of direct reuse—or the proliferation of single-use abstractions—is definitive proof that the library learning mechanism has failed to generalize [cite: 1, 15].

#### 4.1.2 Soft Reuse (Alignment Scores)
Because LLMs often modify or adapt code in-context rather than calling a function strictly by its signature, researchers measure **Soft Reuse**. This involves calculating subsequence alignment scores or utilizing AST (Abstract Syntax Tree) matching to determine if the *logic* of a learned lemma was partially incorporated or slightly modified across solutions [cite: 1, 15].
*   Even under generous soft reuse thresholds (e.g., matching lemma names, whitespace variations, or partial logic sub-graphs), systems like LEGO-Prover failed to demonstrate significant cross-task survival [cite: 1, 5, 15]. Therefore, to be load-bearing, an abstraction must display high soft-reuse durability across a problem corpus.

#### 4.1.3 Search Depth and Program Length Reduction (Compression)
In a valid library learning system, the introduction of an abstraction should provably compress downstream solutions. This is quantified by:
*   **Average Program Length Reduction:** For example, the SMPMA (Self-Modifying Program Synthesis) framework demonstrated compression by reducing the average program length to 4.2 operations when solving ARC-AGI subset tasks [cite: 16].
*   **Search Tree Pruning:** A load-bearing abstraction encapsulates multi-step reasoning into a single primitive. This drastically reduces the branching factor and search depth required for enumerative or LLM-guided synthesis algorithms to find a solution [cite: 2]. If the abstraction does not statistically decrease the time-to-solution or the required node expansions in the search tree, it is cosmetic.

### 4.2 The Theoretical Framework: Retention as Cache Eviction
To fully understand what makes an abstraction load-bearing, we must look to theoretical models of procedural memory and skill retention. In 2026, June Kim's seminal work, *Generalize or Specialize? Retaining Reusable Skills for World-Model Agents*, formalized the concept of abstraction discovery as a problem of **cache eviction** [cite: 17].

According to Kim, an agent fluently generating skills (which LLMs excel at) will quickly accrete an infinitely growing library. Unbounded accumulation is self-defeating due to the carrying cost $\kappa(c)$ of storing, matching, and maintaining abstractions [cite: 17]. A load-bearing abstraction must justify its carrying cost via one of two competing selection pressures:

1.  **Compression (Minimum Description Length - MDL):** This is the **Generalization** pressure. An abstraction is retained only if the library $L$ plus the re-expressed corpus encodes in fewer bits than the raw corpus [cite: 17]. Compression explicitly targets the most frequently recurring patterns. If a tool is broadly reusable across many standard situations, it is load-bearing via compression.
2.  **Planning Utility (Minton's Macro Utility):** This is the **Specialization** pressure. Certain abstractions are mathematically rare (invisible to frequency) but possess immense payoff value because they crack a particularly hard, domain-specific bottleneck [cite: 17]. 

Kim points out that current LLM agents rely almost entirely on compression-based retention (e.g., Stitch). However, in long-horizon, complex environments, compression and utility diverge. An abstraction might not compress the overall dataset significantly, but if its removal causes the agent to fail entirely on a specific, high-value family of tasks, it is load-bearing via utility [cite: 17]. Future systems must track payoff value (reward and reconstruction cost) alongside recurrence (frequency and recency) [cite: 17, 18].

***

## 5. Standard and Missing Ablation Protocols

The core of the user's inquiry rests on the doctrine that a claimed improvement must disappear when the abstraction is removed. The catastrophic failures of systems evaluated between 2024 and 2025 occurred precisely because standard ablation protocols were missing or poorly designed. 

As of 2026, the empirical community has established a rigorous, non-negotiable set of standard ablation protocols.

### 5.1 The "Leave-One-Out" (Disable Library Sharing) Test
The definitive test for a load-bearing abstraction is the minimally invasive ablation of library sharing, often referred to as a "leave-one-out" or "library-masking" test [cite: 1].
*   **Protocol:** The system is evaluated on a holdout test set with access to the fully learned library $L$. Then, the system is evaluated on the identical test set with the library mechanism completely disabled (or specific abstractions masked out).
*   **Requirement for Validity:** The accuracy of the system must suffer a statistically significant drop. Furthermore, this drop must occur specifically on the tasks that previously directly invoked the ablated abstraction.
*   **Historical Failure:** When Berlot-Attwell applied this test to LEGO-Prover and TroVE, disabling the library did *not* induce marked drops in accuracy [cite: 1]. This undermined the entire premise of those systems.

### 5.2 Compute-Normalized Baseline Comparison
As discussed in Section 3, comparing a multi-iteration library learning system against a zero-shot or single-pass LLM baseline is scientifically invalid [cite: 4, 5]. 
*   **Protocol:** The baseline system must be allocated the exact same computational budget as the full library learning system. Budget can be measured in total tokens generated, API cost (e.g., USD cost for GPT-4 calls), or GPU-hours [cite: 1].
*   **Example Implementation:** In testing Draft-Sketch-Prove against LEGO-Prover, researchers extended the number of baseline iterations to approximately match the compute cost of LEGO-Prover. Under these normalized conditions, the baseline remained within one standard deviation of, or outperformed, the library system [cite: 5, 15].

### 5.3 Mechanism Isolation via Decoupling
To ensure that an abstraction is providing the value—and not a secondary mechanism—individual system components must be toggled independently.
*   **Protocol:** Isolate the generation, selection, and application phases. For instance, in the SMPMA (Self-Modifying Program Synthesis) framework, the authors isolated mechanism contributions by specifically toggling macro templates, operation prioritization, and scoring modes independently on an ARC-AGI subset [cite: 16]. 
*   In the robotics framework **LiLo-VLA** (a modular framework for long-horizon tasks), researchers performed an ablation by removing the "Reaching Module" to prove that decoupling transport from interaction was fundamentally necessary, resulting in a 0% success rate without it, thus proving the module was load-bearing [cite: 19].

### 5.4 LILO's Ablation Example
Even successful systems like LILO must demonstrate this. In the original LILO paper, researchers ran an ablation `[Lilo (✂ Search)]` to isolate the effects of the enumerative search versus the LLM-guided AutoDoc library [cite: 3]. They found that the abstraction search was heavily load-bearing on domain-specific structures (like graphics drawing commands) that were impossible to infer from language alone [cite: 3].

***

## 6. Attack Vectors and Systemic Confounds

The user requested specific analysis of "Attack Vectors"—ways in which library learning systems can fake success or game the evaluation metrics. Two specific cross-references were provided: `PATTERN_BASE_RATE_NEGLECT` and `PATTERN_CONDUCTOR_CONFOUND`.

### 6.1 PATTERN_BASE_RATE_NEGLECT: The Verbosity Trap
**Definition:** Random or highly verbose abstractions can compress a dataset significantly if the baseline generation is extremely poor or redundant. What is the floor of compression?

When an LLM is asked to solve a problem without a library, it frequently relies on highly verbose, repetitive, and unoptimized code (e.g., repeating a standard boilerplate loop ten times instead of writing a clean helper function). 
*   **The Attack Vector:** If a system uses a symbolic compressor like Stitch on this verbose LLM output, Stitch will easily identify massive, multi-line blocks of code that repeat across the corpus. The system will claim it has discovered a "deep, highly compressible abstraction" [cite: 8].
*   **The Reality:** The system has not discovered a fundamental algorithmic primitive or a "load-bearing lemma." It has merely compressed the LLM's inherently bloated syntax. The compression metrics (e.g., bits saved or lines reduced) will look spectacular, rewarding the verbosity of the baseline rather than the conceptual economy of the library.
*   **Mitigation:** To combat Pattern Base Rate Neglect, the "floor" of compression must be established by measuring the compression rate of the corpus against a heavily optimized, human-written baseline, or by rigorously checking if the extracted abstractions align with human-interpretable concepts (as AutoDoc attempts to enforce) [cite: 20]. Furthermore, the system must prove that the abstraction is actually *reused* to solve *new* problems, not just retroactively compressing old ones.

### 6.2 PATTERN_CONDUCTOR_CONFOUND: Domain Overfitting
**Definition:** Abstractions that pay only within one highly specific problem family, failing to generalize to the broader domain.

Library learning is inherently data-driven. The abstractions a system discovers are fundamentally bound to the statistical distribution of the training corpus [cite: 2, 16]. 
*   **The Attack Vector:** A system is trained on a synthetic dataset where tasks cluster tightly around minor parameter variations (e.g., a list-processing domain where the only difference between tasks is `add-1`, `add-2`, `add-k`) [cite: 2]. The system learns an abstraction `add-x`. The researchers claim the system has achieved massive abstraction discovery.
*   **The Reality:** The abstraction is functionally a cosmetic wrapper around a single, hyper-specific task family. It possesses zero load-bearing capability outside of this specific distribution. When tested on a genuinely novel task (domain transfer), the library provides zero utility [cite: 2]. 
*   **Mitigation:** Validating library learning requires evaluating the system on out-of-distribution (OOD) test sets. The abstractions must prove their utility by acting as composable primitives for tasks that structurally diverge from the training set. If the library only pays off within one problem family, it is suffering from the Pattern Conductor Confound.

***

## 7. Domain-Specific Implementations (2024–2026)

To provide a comprehensive overview of the literature and state of the art, we must examine how these principles are applied across various distinct domains.

### 7.1 Mathematical Reasoning and Theorem Proving
Mathematical reasoning has been the primary battleground for library learning, driven by the desire to automate formal verification in languages like Isabelle/HOL.
*   **LEGO-Prover (Wang et al., 2024):** Attempted to autoformalize theorems by converting natural language proofs into formal Isabelle theorems, storing successful lemmas [cite: 5]. As discussed extensively, it failed the ablation and direct-reuse tests [cite: 1, 15].
*   **TroVE (Wang et al., 2024):** Induced Python helper functions for math word problems. Found to rely entirely on self-consistency (majority voting) rather than tool reuse [cite: 1, 15].
*   **RLAD (Li et al., 2026):** Addressed previous flaws by jointly training an abstraction generator via Reinforcement Learning, decoupling the learning signals of abstraction proposal and solution generation. Showed genuine test-time improvements over frontier models (like o4-mini) by conditioning solutions on abstract structures [cite: 11].

### 7.2 Program Synthesis and Code Generation
The origin point of library learning, focusing on domain-specific languages (DSLs) and lambda calculus.
*   **LILO (Grand et al., 2024):** Combines LLM generation, Stitch compression, and AutoDoc. Remains the gold standard for neurosymbolic program synthesis, successfully solving regex, scene reasoning, and graphics tasks with verifiable ablation studies [cite: 3, 9].
*   **SMPMA (Self-Modifying Program Synthesis, 2026):** Operates on the ARC-AGI benchmark. Mines reusable abstractions (fixed sequences and parameterized templates) from successful programs. Demonstrated non-trivial generalization, achieving 2.5% strict accuracy on ARC-AGI through 47 learned abstractions, supported by rigorous isolation of mechanism contributions [cite: 16].

### 7.3 High-Performance Computing (HPC) Optimization
A novel application of LLM abstractions involves low-level hardware optimization.
*   **Effect of Abstractions on LLM-Guided HPC Optimizations (Klepl et al., 2026):** Investigated whether traditional verifiable abstractions (like polyhedral models used in Halide or Exo) improve LLM-guided parallel code optimization [cite: 21, 22]. Found that LLMs, given specific high-level optimization goals, can generate C code that outperforms traditional abstraction-based computation pipelines. This suggests that LLMs can internalize high-level semantics to perform optimizations that go beyond strictly verifiable, rule-based automated transformations [cite: 21].

### 7.4 Robotics and Physical World Modeling
Abstraction in continuous, physical environments requires decoupling temporal and spatial skills.
*   **LiLo-VLA (2026):** A Vision-Language-Action framework for long-horizon robotics tasks. It introduces zero-shot compositional generalization by isolating atomic skills. Extensive ablation studies (e.g., removing the Reaching Module) proved that standard end-to-end architectures cannot implicitly learn long-horizon dynamics from atomic demonstrations. LiLo-VLA achieved an 85% real-world success rate by treating physical skills as reusable abstractions [cite: 19].

### 7.5 Visual Shape Modeling and 3D Abstractions
*   **ShapeLib (2026):** Uses the priors of LLMs to design libraries of programmatic 3D shape abstractions. Given text descriptions and a seed set of shapes, ShapeLib guides an LLM to propose and validate geometric functions. Crucially, it trains recognition networks to map new shapes to programs using these newly discovered abstractions, proving cross-task generalization and usability beyond the training set [cite: 12].

### 7.6 Linguistic and Orthographic Modeling
*   **Grapheme-to-Sound Joint Compression (Jiang et al., 2025/2026):** Applied library learning to uncover the compositional structure of Chinese characters. By jointly compressing written and sound forms, the model discovered over 1,900 sound-related abstractions that functionally mirror the phonetic and semantic radicals in Chinese orthography. This represents a rare, highly interpretable application of library learning to natural linguistics [cite: 23].

***

## 8. Theoretical Perspectives: The Semiotic Gap

Underlying the empirical debates over ablation protocols and reuse metrics is a deeper theoretical debate about the nature of LLMs and their capacity for true abstraction. 

### 8.1 Pattern Matching vs. Conceptual Abstraction
A core skepticism in the 2026 literature revolves around the semiotic distinction between *signs* and *symbols*. 
*   **Pattern Matching:** LLMs excel at recognizing regularities in observable data (signs). They predict what is most probable based on statistical correlations [cite: 24]. When an LLM generates a block of code, it is often assembling a highly probable sequence of tokens based on its training data.
*   **Abstraction:** True abstraction requires extracting a general, underlying principle (a symbol) that applies universally, even to instances never encountered before [cite: 24]. 

Critics argue that LLMs do not raise the level of abstraction; they merely obscure complexity. They lack a consistent, internal theory to guide the development of reliable, stable, and compact abstractions that compose well across systems [cite: 25, 26]. This is why purely LLM-generated libraries often fail the load-bearing tests: the model is generating statistically plausible but conceptually hollow refactorings. 

### 8.2 Neuro-Symbolic Integration (Type 6 Taxonomy)
To bridge this gap, the field is moving toward rigorous Neuro-Symbolic (NeSy) integration. Using Henry Kautz's taxonomy, the ultimate goal is **Type 6** integration: a neural system that can invoke and execute genuine symbolic reasoning internally as an emergent property [cite: 10]. 

Current systems like LILO represent a stepping stone. By offloading the raw symbolic compression to a deterministic engine (Stitch) and using the LLM merely to guide the search and document the results (AutoDoc), the system binds neural pattern matching to mathematically guaranteed symbolic abstractions [cite: 8, 10]. The LLM acts as the intuitive apprentice proposing the architecture, while the symbolic compressor acts as the master builder ensuring the beam is actually load-bearing [cite: 10].

***

## 9. Conclusion

As of 2026, the state of library learning and abstraction discovery is marked by a profound paradigm shift. The initial wave of optimism surrounding LLM-guided library systems has met a wall of rigorous, empirical skepticism. 

**Summary of Findings:**
1.  **LLMs vs. Enumeration:** LLM-guided frameworks (like LILO) undeniably outperform pure enumerative methods (like DreamCoder) by leveraging natural language priors to vastly reduce search spaces and document symbolic compressions.
2.  **The Ablation Imperative:** The field is recovering from a methodological crisis wherein highly publicized systems (LEGO-Prover, TroVE) failed to prove that their learned abstractions were load-bearing. Direct reuse in these systems was virtually zero. Performance gains were illusory, driven by self-consistency, iterative refinement, and heavily unbalanced compute budgets.
3.  **Metrics:** To establish an abstraction as load-bearing, researchers must track verbatim *direct reuse frequency* and verify that the abstraction reduces downstream search depth.
4.  **Protocols:** The gold standard for validation requires minimally invasive *leave-one-out* ablation tests (disabling library sharing) and strict compute-budget normalization against baseline prompt models. 
5.  **Attack Vectors:** Evaluators must vigilantly guard against *Pattern Base Rate Neglect* (compressing verbose baseline LLM output and mistaking it for deep abstraction) and the *Pattern Conductor Confound* (overfitting a library to a single, narrow problem distribution).

True abstraction—the discovery of reusable, load-bearing cognitive primitives—remains the hallmark of intelligence. The algorithmic pursuit of this goal via library learning requires strict discipline, ensuring that our models are actually building foundations, rather than merely painting the walls.

**Sources:**
1. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMzdIgWJPZZ58EcPrlVLQ4QwgLJxgYS9Wksd76Er-YOzyeaRYCkca18GNGTfOWAAbvTXfyAjjkN-ZfiHovLkteupbJHx-TAusW_ivxNMXCN8WsQt-ekwyIDUJpvWMXd3t-gFRsRtFlwn-xW0bikBDX_TPq)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3s8dFQ3F94itR18y8fij4xvSuWHsvLJGnwiOMjz1Wh-u7KgQFc656H2OV1ClO-Q693v1-OzwsSWLRPpzy7sjxw3B2GeIH1zP0kY9hlajKEwxhAoCJZg==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYyqsQn6G9Oiq3-faYJ5hsQ8OC4FWqKHEzeB7rDXJqt_6-DSFZCPb4009wFI4hscsqMognhZriOacdw9fKfhg7Cu6Pj7rK3mnz1aIXc22n6-3sGf8Wrkq7)
4. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLn5B9BVAd_rhYxJSoo9i45Lag7IVUdEPArjVh0arVLDEfjcowttxRMUY25I9NwcKLQP-Vo8-7xizQSg5CG4i3-_S71zbqCIACxAwmQFCVQP6prT8QoCcCcD8PKTyJ387q)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9eP317_GUxg9ItQ-sntSqVwB-7gX1OQ6LmLk4HcgQw0KD00xlgrI9lJmbNuHaKl3-kwcdX9IK3VyFmW5dIoBAMkNfk4yhWgLkdljMGn7zJAY7jCf32pyo)
6. [neurosymbolic.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFAxfU5f3eAppexoogSm3HoweW2f9UsAk4V5HCtl9y-f1HURhYys6MMx2KGwNS0oC-4azZ2gN5HHEDeXTdDpprDBUvCvCUnmKsdaU-t3i_Z9NjxiwDoXT1hR11ewf36C8=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCzChUGnWpdi_x6umSpy1WVM4TId79LlcaFXjhPNScrna3Kq9lRlsUTcXv3Kj1kPcBi1n0qwQpKAV6gxjK-iWwBs3MSz3xryhBJAYaYJ0jef_wq2AkcsBi)
8. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHl-7HhsDfFqMSNCcDk15lmMSkII90XxCvstaIIg7QP7ub754iybk8qQG_n_HQ0iYICs3Q04rXVQ57UDBPwur45KU64IT1lNK1hgOTs-9SML-GEctPKEfY3P7-9GI-y0wGcLUXKfUk1Idp9Zu2qJBiOU84JC5AiGSiOiahiormYtG58o1wt)
9. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJqx9U7OQ7nlfW_kWffjIAkt5e8HMxsk9V4oQWBU4dTNnDf17dY8OCmTN45aij8LgsaOV4I3yrhxVi-KRpwqgMM9RFrttq8Av2fFFcgnBYc4fRTlThTQ==)
10. [gopubby.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXCzrQHnjO6_7bbujkL0_bdytBCHxDPRok1E1LUQ9MD4-CBxqDMkSaT6dkqw1gk__J5-TCkHy6hfDc4ZmtVnAmwAXFNyfdLPxvNuf26PbsrZPuRzz4vjA0laXtdPl4JYHiQLqwxWKDSRdrb2KzXdeU9Rvy6Rh2U4VEEwSX2kAKkPxNnDAJs6Sf)
11. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhN_QcDdNifws4y9r-rromn25hwkZ7vDOLXCq-1ENEbeL6fYK1aW_iyuI0q8eQYh0TyvMV4hqB90l033CV6oqcAQN6NlqhhEdfxPEO0P0uOBXsK73-hpeiMoIy0XiTSw==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2UYnKzMuLQdVrPFS9z1nG9WnHSx7DK3ZIkA9mMHgBhRJxj5gOZKHcfb1FpW3HICl55rHvodWD9VcUlIOH3Wjb-gZvh3VIVRE31vF_WhrzL0oWVD-dHnn1)
13. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErGVxVtXIM3iPqGIfqju3tWacYTvCVIZzpWuEwvJ6cN_aBcbKAr7F8Bi1d0PcFeI_mV7mpFVRmv1Yqst5_wPI9WuB3FLZ3af1Lutcs4c7IPh6jjCFVy7bq4n34fIAvdfmXOZwIIFj7j_c142sd1majkg==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUaENuDwmpbpdGkAJ5lPFLLG07sYpinUdX9XwZKXAgKgQljODUo_dDYzrJ1gAlpDiX0Nr-CO-aBDQzlrQLcbM-rwtoKo5BLIrRQHpJJgAq2XhL_zJnyodG)
15. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGi2a922Q2SS4AQxD0mCVF7uHbvxxt6V1hhLxN6qLXSybFRDIfxgt96f0TSeQs7X4d9nTofWVB-XxPpjCM0vjJBVdi8MSSOpx7nMMQr-_5xPD2fnPhAoSbkOaVJjzyCi5vwuQL5)
16. [techrxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBL6OAiDCpokdhxtaee5r8eOWtrX3yqPXiqtURwSpRKvDV6umT8nRN0-QKm5aKtCfR8zd1krBevB1KVSt7gOSD5ywMgla7keCx0SGt4kc5Cot--HR6L76nRTxzFKv8lEZUREJ5UWgEvNOucdc6LdsjADyOFrsz)
17. [june.kim](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFz41xEaCjMTMq6ChTgDZVd2360nnZgT8-h0SU0Ot1kbXWX6Xr_-e0SQjgkE6BzS9dacGD0KIEGN5lBm5MrBvSaG1lAhALSQQOrE0a6Rm-EZGd2IxiQeh3h0XFq_4X6)
18. [june.kim](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELpZcq7EF79nBo1r8EuOcmcGDrVw69LmGF9_XSh1jbC-dZw3eRlr523lHFR8bScHH95H-qb70Nuouj5FtPi-Y-bdDqnS_5e7ClWFM7xDhB)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkajJXruV09O3Z3eFa5rd91G2aQlwLMHYYgSnXq5eYZZZ7Yr-efj0ojaOj34zrD3qIWwvA4t68pdgB5va1mBhm3Lbjhc3TTEChYZmdf-HOtcKxfFKDcCIv)
20. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwQVQOvlPh9EsC6ezjf7tSel-WurhsTLcJp52FxXuJWXUJJrQDkivnLmgRs8DrJRwYXYrt31zgMEthbzl5XHdMWCGBtbY4b8N3eka2RBRwiK2No4jAN9kI0Z9_s99n2U2qkPZQBBr6qSh731XZwloBv1dOVhgoLbw5Vyw1njmtJjXjw8TivKkw9r0rE3Oyq7JE1Ec=)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGdVw787KDbXDCx0CTJFAFR1yt2EBRRfw8yJ15fpJ-lfMgTjDbHBEA9P0Hi4JJbsnSm_Ol8j9IQC-cbYepkQ5JdODoXjeK3kG62uToi7xCahRdDJbDsier)
22. [takara.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbI4T6xWHvZ-GD2z2qDj_FDrE9Q3kSaLyr3NGgJqx2d-M91tLaKzBXmCemOIVVuuYyN0P2hGrGLMW43jk0r_fVHthCC76IEHZl1K7nSv2KAbNuBOZHtxqq)
23. [jiang.gy](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_i0pg-jynWtdDuaLzUeHsRsKkebMlTCJHt4rsqS7Kt2-9FlzomuCGeaVO_H5Xltd6zN99-9Wsi3aTKjlYjVq5dlNsbmZSnO9KP0EE718AZY0T_B4mDTaK19kiVY9y3ifnREV2qsQ=)
24. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAllghn1Z-K0pCaZ5ifA7xe0ep5cMBEuAz6OMtBo4Wq_7cmfJpCAVupl9cVByJU-WqyoXC5Y9U9D_FcaNfCTOyfsy57FSenqvi3gtKt59RBAM5ABoaA3YJCKuqjL00vcO-qoTkHibv-VxIvt5-uOuMV-qm_qMKGJ2F4NMyxdeRxb-TlnraNSp3W9M-Mn-JBHPO1C_0NnK8zhd0nizG)
25. [codeistruth.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPTh26Jtqe76fRovEWYphIAJoUtodR9aB5ul0ocRA4-xupZgIJk5ZRjWOq2IEL0zaUQldZYLdANa_Qw9CuQjYy0vNtZMXrTHZ9y6WhQZOWU644GewfEMNkT4LFFEOtnLyU)
26. [martinfowler.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEepk2Bl9AOfXwGau-oRDbemXlsHrB0RrijrOIMofyU2Y0dleciTI1FugNXRjgsLP4yuc0EniWMWMS7j-6bm8D86B321hnZFGwrjjRkdQIZpkpjAP0Uhk-TQZk172OS5DYQkUD9jXuYJR4jKVa4XDZaRKG-)
