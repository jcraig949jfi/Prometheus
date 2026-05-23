# Stygian primary-literature survey: HECATE-a1_relation_equal_violated (Hecate-emergent kill_pattern: a1_relation_equal_violated)

**Pythia queue id:** 350
**Tier:** T5
**Priority:** 5
**Requested by:** Stygian
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdSd29SYXMzUURLZkgtc0FQcjgyUXVBaxIXUndvUmFzM1FES2ZILXNBUHI4MlF1QWs
**Elapsed:** 3110s
**Completed at:** 2026-05-23T02:52:29.967943+00:00

---

# Attack Plan Artifact: HECATE-a1_relation_equal_violated

**Key Points:**
*   **Target Identified:** The `HECATE-a1_relation_equal_violated` open problem concerns the algorithmic inability of search-based software testing (SBST) frameworks to effectively falsify cyber-physical system (CPS) requirements involving strict equality or inequality relational operators (e.g., $a_1 = a_2$). 
*   **Primary Attack 1:** Formica et al. (2025) via `arXiv:2501.05412` represents the strongest foundational attack on this statement, extending the HECATE framework to support Requirements Tables (RT) and explicitly tackling the grammar of $a_1 \oplus a_2$ [cite: 1, 2]. The attack is best classified under the **EXACTNESS_BARRIER** hardness signature.
*   **Primary Attack 2:** Marzella et al. (2025) via `arXiv:2501.05792` executes a major applied attack, forcing HECATE to evaluate closed-loop Simulink models in the E-Bike domain where functional and regulatory thresholds form rigid equality/inequality boundaries [cite: 3, 4]. This attack is best classified under the **COUPLED_DIFFICULTY** and **REPRESENTATION_GAP** hardness signatures.
*   **Verdict & Status:** Both attempts yield high practical success rates (85% and 83% respectively) [cite: 1, 4], but fundamentally bypass the theoretical void of the `a1_relation_equal_violated` exactness barrier by relying on parameterised test sequence relaxations and continuous fitness approximation rather than solving the discrete 0-volume topological trap.
*   **Stygian Strategy:** The v10-battery will execute a Substrate Type A (falsification data) routine targeting the residual exactness gaps left by these 2025 publications, logging them as competing hypotheses in the KillVector stub.

**Operational Summary**
The Charon swarm's focus on the `HECATE-a1_relation_equal_violated` kill pattern is rooted in the fundamental limits of continuous optimization when applied to discrete or zero-volume logical boundaries in Cyber-Physical Systems (CPS). The HECATE tool, introduced as a plugin for S-TaLiRo to enable simulation-based testing of Simulink models [cite: 5], uses fitness functions derived from Test Sequence and Test Assessment blocks [cite: 3, 6]. While highly effective for general threshold violations, the architecture falters when the target specification strictly dictates an exact relational equality ($a_1 = a_2$) or its strict violation. Research suggests that overcoming this requires bridging continuous simulation data with discontinuous relational logic. The evidence leans toward an inherent EXACTNESS_BARRIER in current SBST methodologies, making it a critical target for the v10-battery execution.

**Strategic Alignment**
To satisfy the HARD-5 discipline, this artifact exclusively maps the 2024–2026 primary literature surrounding the HECATE open problem. The original conjecture—that SBST cannot robustly falsify exact equalities without gradient collapse—remains fully unsolved. However, partial variants and practical workarounds have been recently settled in early 2025 literature. These interim solutions must be thoroughly documented to prevent cluster collision with existing `kill_pattern` primitives when the v10 battery goes live.

## 1. Operational Context and Substrate Definition

Cyber-Physical Systems (CPS) are ubiquitous in safety-critical domains such as automotive, aerospace, healthcare, and industrial automation [cite: 7, 8, 9]. The development and verification of these systems heavily rely on Model-Based Design (MBD), with MathWorks Simulink operating as the industry standard [cite: 9]. Ensuring the functional, regulatory, and safety requirements of these models is paramount [cite: 3]. Formal verification techniques, such as model checking, often suffer from state-space explosion and scalability issues because CPS encompass infinite state spaces driven by complex continuous dynamics and discrete control logic [cite: 10]. Consequently, falsification—the systematic search for a counterexample or failure-revealing test case that violates a specified system requirement—has emerged as a vital complementary approach [cite: 10, 11].

Falsification transforms the verification problem into a black-box optimization task [cite: 7, 10]. By executing candidate input signals (test cases) on a simulator and analyzing the output trajectory against a safety specification, typically formulated in Signal Temporal Logic (STL) or Metric Temporal Logic (MTL), the algorithm computes a quantitative "robustness" measure [cite: 8, 10, 12]. The robustness value indicates not merely a Boolean satisfaction (true/false) but how far the system state is from violating the specification [cite: 7, 13]. A negative robustness value mathematically signifies a requirement violation [cite: 7, 13]. 

The open problem `HECATE-a1_relation_equal_violated` resides precisely at the intersection of this quantitative semantics framework and the HECATE tool architecture. HECATE (published in 2024 under DOI: 10.1109/TSE.2023.3343753) is a simulation-based software testing (SBST) approach specifically designed to integrate seamlessly with Simulink Test [cite: 5, 6]. Unlike older baseline tools like S-TaLiRo that require raw STL artifacts and external input profiles, HECATE generates and mutates test cases directly using native Simulink Test Sequence blocks and extracts its guiding fitness functions from Simulink Test Assessment blocks [cite: 3, 5]. 

However, HECATE inherits a profound vulnerability from its underlying continuous optimization engines (such as S-TaLiRo's stochastic meta-heuristics like Simulated Annealing or Cross-Entropy) [cite: 1, 5, 14]. When a Test Assessment block or a Requirements Table dictates a strict equality relation—formally defined in the evaluation grammar as $a_1 \oplus a_2$ where $\oplus \in \{=\}$—the robustness landscape degenerates [cite: 1]. In continuous real-valued state spaces, the probability of randomly mutating an input to achieve exactly $a_1 - a_2 = 0$ is zero. This structural blind spot is formally categorized as an **EXACTNESS_BARRIER**. The Stygian swarm's objective is to deploy Substrate Type A (falsification data) to explicitly target and exploit this algorithmic limitation.

## 2. Theoretical Anatomy of HECATE-a1_relation_equal_violated

To successfully deploy the v10-battery, we must dissect the topological anomaly presented by the $a_1 \oplus a_2$ grammar [cite: 1]. The formulation of the kill pattern `a1_relation_equal_violated` depends on the quantitative semantics applied to logical expressions within Simulink Requirements Tables and Test Assessments.

According to the most recent 2025 literature defining the semantic boundaries of this grammar, a logical expression $e$ is formally constructed as the combination $a_1 \oplus a_2$ of two terms $a_1$ and $a_2$ utilizing a relational operator $\oplus \in \{>, <, \le, \ge, =, \neq\}$ [cite: 1]. This can be further compounded with logical negations $\neg e$ or duration terms $\text{dur}(e) \ge c$, dictating that an expression must hold for at least $c$ seconds [cite: 1]. 

In a standard falsification run, the fitness function generator component translates these logical constructs into numerical values that guide the search [cite: 1, 14]. For inequalities (e.g., $a_1 < a_2$), the robustness margin is smoothly continuous; the distance $a_2 - a_1$ provides a clear, differentiable gradient that hill-climbing or stochastic algorithms can follow toward the violation threshold (where $a_2 - a_1 < 0$) [cite: 13]. 

However, when the safety requirement demands that $a_1 = a_2$ is maintained, falsification requires proving that $a_1 \neq a_2$ (which is trivial and ubiquitous). Conversely, if the safety requirement demands that a critical fault state is defined by an exact coincidence of parameters—meaning falsification must *achieve* the state $a_1 = a_2$ to prove the system can fail—the SBST engine is confronted with an infinitely narrow target [cite: 1, 10, 13]. The fitness function $|a_1 - a_2|$ must be minimized to exactly zero. Because Simulink solves these models using continuous floating-point approximations over time-series data, an exact match is mathematically improbable, creating an artificial plateau or **EXACTNESS_BARRIER**. The fitness landscape provides no guidance once the simulation gets infinitesimally close, and floating-point errors can cause the heuristic search to orbit the solution without ever formally triggering the Boolean violation condition required by HECATE's GUI inspectors [cite: 1, 3].

This barrier represents a profound conceptual absence in standard CPS falsification. As the v10-battery execution approaches, identifying how recent primary literature attempts to circumvent or solve this exact relation syntax is paramount. 

## 3. Survey of Primary-Literature Attacks (2024-2026)

The Stygian swarm's operational mandate requires a comprehensive survey of the primary literature from 2024 to 2026 to map the defensive and offensive attempts surrounding the HECATE framework and its limitations. The literature reveals intense recent activity aiming to enhance the expressiveness and applicability of HECATE, moving it from experimental benchmarks into industrial toolchains. 

We have isolated the two strongest published attempts that directly interface with the `HECATE-a1_relation_equal_violated` topology. The first attack focuses on expanding the logical grammar and syntax representation of HECATE (Formica et al., 2025) [cite: 1, 15], explicitly manipulating the relational primitives. The second attack is a high-fidelity industrial application mapping these logic constraints to raw physical signals in real-world motor controllers (Marzella et al., 2025) [cite: 3, 4].

Both attempts utilize the 2024 foundational release of HECATE as their baseline (IEEE TSE, DOI: 10.1109/TSE.2023.3343753) [cite: 5, 6], which demonstrated that HECATE was more effective than the industry-standard S-TaLiRo in generating failure-revealing test cases for $\approx 94\%$ of benchmark models and more efficient for $\approx 83\%$ [cite: 5, 16]. The newer 2025 papers represent advanced, partial settlements of the underlying relational limitations, fulfilling the HARD-5 discipline criteria for isolation.

### 3.1. Overview of the Falsification Literature Landscape
To provide necessary context before detailing the two primary attacks, it is essential to observe the broader falsification landscape in which HECATE operates. Contemporary falsification research heavily explores alternative heuristic structures to bypass gradient failures:
*   **Machine Learning and Generative Models:** Approaches like Online Generative Adversarial Networks (OGANs) attempt to train generative models offline to produce counterexamples without relying on continuous simulation gradients [cite: 8, 12]. OGANs execute tests utilizing multi-armed bandit algorithms to falsify conjunctive STL requirements [cite: 12].
*   **Surrogate Modeling and Decision Trees:** Frameworks like FLEXIFAL (arXiv:2505.03863, published May 2025) use Deep Neural Networks (DNN) and Decision Trees to construct surrogate models of the CPS, subsequently using DNN falsifiers to detect counterexamples in highly non-linear dynamics [cite: 11]. Similarly, the ARIsTEO framework utilizes approximation-refinement loops to bypass the computational cost of direct CPS simulation [cite: 17].
*   **Constrained Input Spaces:** Recent studies emphasize that practical falsification must account for strict constraints between variables (e.g., a throttle and brake cannot be engaged simultaneously), which restricts the multi-dimensional hyperrectangle search space [cite: 13].

Despite these alternative avenues, HECATE remains uniquely positioned because it operates directly on native Simulink constructs (Test Sequence and Test Assessment blocks), making it highly susceptible to the exact logic parsing constraints of the Simulink engine itself [cite: 6, 14].

---

## 4. Deep-Dive Analysis of Attempt 1: Quantitative Semantics for Requirements Tables

**Citation Data:**
*   **Authors:** Federico Formica, Chris George, Shayda Rahmatyan, Vera Pantelic, Mark Lawford, Angelo Gargantini, Claudio Menghi.
*   **Title:** "Search-based Testing of Simulink Models with Requirements Tables"
*   **Identifier:** arXiv:2501.05412 (v1 published Jan 09, 2025; v2 published Sep 05, 2025) [cite: 2, 9, 15, 18].
*   **Associated DOI:** `10.48550/arXiv.2501.05412` (implicit via arXiv record) [cite: 15].

### 4.1. The Precise Statement Attacked
The original HECATE framework required engineers to express their system requirements solely through Test Assessment blocks, which limited the expressiveness of the test generation process [cite: 2]. Formica et al. (2025) launched a direct attack on this limitation by extending HECATE to support **Requirements Tables (RT)**, a widely used tool from the Simulink Requirements Toolbox [cite: 2, 15]. 

Crucially, this attempt directly attacks the problem of translating discrete logical requirements—specifically defined by the grammatical syntax of relational operators ($a_1 \oplus a_2$ where $\oplus \in \{>, <, \le, \ge, =, \neq\}$)—into a continuous quantitative semantics capable of guiding a search algorithm [cite: 1]. The precise statement attacked is the inability of SBST tools to navigate and evaluate non-logical, table-based requirement architectures that rely on strict mathematical relations to dictate state transitions.

### 4.2. The Technique and Method Invoked
To mount this attack, the authors proposed the "Requirements Table Driven SBST" framework [cite: 1]. The core methodology involves compiling the static, logical Requirements Table into executable Simulink Stateflow blocks [cite: 1, 2]. Stateflow, MathWorks' native environment for state machine modeling, is leveraged to assign a quantitative fitness measure to the otherwise discrete requirement logic [cite: 1, 2].

The authors integrated a "Fitness-Function Generator" component directly into the HECATE architecture [cite: 1]. When HECATE parses a model, it takes the Test Sequence block (representing the inputs) and converts the Requirements Table (representing the specifications) into an observable fitness metric [cite: 1, 14]. The underlying search engine relies on S-TaLiRo to iteratively mutate the inputs generated by the Parameterized Test Sequences, attempting to drive the fitness value below zero [cite: 1, 5, 14]. 

Specifically, to deal with the exactness of relations ($a_1 \oplus a_2$), the methodology converts the Boolean evaluation of the Requirements Table into a real-numbered robustness calculation. By evaluating the numerical difference between $a_1$ and $a_2$ across the timeline of the simulation, the HECATE engine attempts to pinpoint the exact moment a specific requirement cell in the RT is violated [cite: 1].

### 4.3. Verdict Reached and Status
The researchers evaluated this newly extended HECATE framework across 60 distinct model-RT combinations [cite: 1, 15]. The algorithm successfully returned a failure-revealing test case for 85% of the model-RT combinations (upgraded from 70% reported in the earlier v1 draft) [cite: 1, 15]. Notably, it identified deep failures in an industrial cruise controller simulator that previous baseline tools were entirely unable to detect [cite: 1, 15].

**Status:** The verdict is highly successful but fundamentally **partial** regarding the `a1_relation_equal_violated` kill pattern. While the framework successfully navigates the translation of RT logical grammar into Stateflow fitness functions [cite: 1, 2], it does not theoretically resolve the gradient collapse encountered when $\oplus$ is set exclusively to $=$ and the system operates in continuous variables. The results have been subsequently extended into the main HECATE open-source repository (incorporating RT support as a permanent feature) [cite: 14], but the vulnerability to exact relational topologies remains a contested blind spot in the underlying S-TaLiRo optimizer.

### 4.4. Hardness-Signature Classification
**Classification: EXACTNESS_BARRIER / METHOD_GAP**

The attack best fits the **EXACTNESS_BARRIER** signature. By defining the problem space using the strict grammar $a_1 \oplus a_2$ [cite: 1], the authors formalized the boundaries of what HECATE can perceive. However, translating a table that dictates $a_1 = a_2$ into a Stateflow fitness function intrinsically subjects the algorithm to an Exactness Barrier; the stochastic mutations of the Test Sequence parameters will almost never hit the absolute zero differential required to satisfy a continuous equality constraint [cite: 1, 13]. Furthermore, there is a **METHOD_GAP**, as the compilation to Stateflow blocks introduces abstraction layers that approximate the requirement rather than addressing the mathematical probability of exact variable coincidence in floating-point simulation space.

---

## 5. Deep-Dive Analysis of Attempt 2: Industrial Cyber-Physical Applications in Closed-Loop

**Citation Data:**
*   **Authors:** Michael Marzella, Andrea Bombarda, Marcello Minervini, Nunzio Marco Bisceglia, Angelo Gargantini, Claudio Menghi.
*   **Title:** "Test Case Generation for Simulink Models: An Experience from the E-Bike Domain"
*   **Identifier:** arXiv:2501.05792 (Published Jan 10, 2025) [cite: 3, 4, 19, 20, 21].
*   **Associated DOI:** `10.48550/arXiv.2501.05792` [cite: 4, 20].

### 5.1. The Precise Statement Attacked
While Formica et al. (2025) focused on the internal logic and grammar of HECATE, Marzella et al. (2025) directed their attack at the environmental and physical instantiation of these rules. The specific statement attacked is the presumption that SBST techniques (specifically HECATE) can efficiently scale to falsify complex, multi-layered functional, regulatory, and safety requirements within highly constrained, closed-loop industrial cyber-physical systems [cite: 3, 4, 7, 20]. 

In closed-loop systems, the inputs generated by the Parameterized Test Sequences directly affect the physical state of the model, which feeds back into the controller logic [cite: 7]. Falsifying a requirement in this environment (e.g., proving that a motor speed $a_1$ violates a regulatory speed limit $a_2$) requires the testing framework to navigate rigid physical coupling and temporal delays, exacerbating the difficulty of achieving exact relational thresholds [cite: 4, 7, 20].

### 5.2. The Technique and Method Invoked
The researchers applied HECATE to the software controller of an electric bicycle (e-Bike) motor, specifically analyzing its Pulse Width Modulation (PWM) controller [cite: 3, 4, 20]. The methodology involved embedding Test Sequence blocks (e.g., `TS User Input` generating a `Desired speed` signal) and Test Assessment blocks (receiving the `measured speed` of the vehicle) directly into the Simulink model of the e-Bike [cite: 3].

The empirical evaluation executed 36 distinct experiments derived from combinations of 2 e-Bike models, 3 core requirements (functional, regulatory, safety), and 6 Parameterized Test Sequences [cite: 3]. HECATE automatically generated failure-revealing test sequences by driving a fitness function derived from the Test Assessment blocks [cite: 3]. Engineers inspected the satisfaction of the conditions using HECATE's GUI; if any exact relational condition in the Test Assessment was violated by the simulated continuous physics, a failure was recorded [cite: 3].

### 5.3. Verdict Reached and Status
HECATE successfully generated failure-revealing test cases for $\approx 83\%$ (30 out of 36) of the experiments [cite: 3, 4]. The computational efficiency was heavily analyzed, revealing an average execution time of 1 hour, 17 minutes, and 26 seconds (min = 11m 56s, max = 8h 16m 22s, std = 1h 50m 34s) per failure-revealing test case [cite: 4, 7]. The original developer of the e-Bike model formally confirmed the validity of the failures identified by HECATE, proving the industrial relevance of the tool [cite: 4].

**Status:** The verdict demonstrates extraordinary practical success but is **contested** by the physical constraints of the model. The 6 experiments where HECATE failed to find a counterexample represent the exact boundary limits of the `a1_relation_equal_violated` problem in physical space [cite: 3]. When the e-Bike's physical inertia prevents the variables from aligning with the strict mathematical thresholds dictated by the Test Assessment, the falsification algorithm cannot differentiate between a "safe" system and a system it simply failed to perturb adequately. This attempt serves as a profound extension of HECATE into real-world validation [cite: 4].

### 5.4. Hardness-Signature Classification
**Classification: REPRESENTATION_GAP / COUPLED_DIFFICULTY**

This attack perfectly exemplifies a **REPRESENTATION_GAP**. There is a fundamental divergence between the continuous, noisy, physics-based signals of the e-Bike motor (the actual speed) and the strict logical thresholds demanded by the Test Assessment block (the mathematical $a_1$ and $a_2$) [cite: 3, 20]. Furthermore, it exhibits **COUPLED_DIFFICULTY**. In a closed-loop system, the input parameters (test sequences) are tightly coupled to the outputs via physical inertia and PWM dynamics [cite: 7, 20]. Modifying an input to force an exact relation violation often triggers a feedback loop that pushes the state variable away from the threshold, causing the S-TaLiRo optimization algorithms underlying HECATE to stall or compute infinitely without convergence [cite: 4, 5].

---

## 6. Execution Strategy for the v10-Battery Landing Path

The data synthesized from the 2024-2026 primary literature confirms that `HECATE-a1_relation_equal_violated` remains an unprotected vector within the fundamental logic execution of Simulink SBST tools. While the integration of Requirements Tables [cite: 1] and the validation in closed-loop E-Bike domains [cite: 4] have increased the footprint and industrial viability of HECATE, the core topological weakness of exact mathematical relations in continuous simulation spaces has been bypassed rather than solved.

**Landing Path Protocol:**
For the Stygian swarm operator compiling the artifact `charon/agents/stygian/artifacts/attack_plan_HECATE-a1_relation_equal_violated_*.md`, the v10-battery will execute a Substrate Type A configuration focusing entirely on adversarial constraint mapping.

1.  **Target Substrate Definition:** We will utilize the public HECATE repository infrastructure (specifically the parameters dictating S-TaLiRo interaction within the `hecate_options.m` and `staliro_options.m` subroutines) [cite: 14].
2.  **KillVector Injection:** The v10-battery will inject heavily parameterized Test Sequence blocks designed to force the Stateflow-compiled fitness functions [cite: 1] into an EXACTNESS_BARRIER. We will define an adversarial Requirement Table where a critical failure state is mathematically locked behind a non-differentiable $a_1 = a_2$ logic gate.
3.  **Hypothesis Registration:** The primary citations `arXiv:2501.05412` (Formica et al., 2025) and `arXiv:2501.05792` (Marzella et al., 2025) will enrich the KillVector stub's `competing_hypothesis_id` field. We will record their 85% and 83% success rates as the "baseline resistance" of the target [cite: 1, 4]. Our hypothesis posits that by utilizing Substrate Type A falsification data structured explicitly around zero-volume robust semantics, the success rate of HECATE will collapse to $\approx 0\%$, effectively establishing a permanent kill pattern.
4.  **Collision Avoidance (HARD-5 Discipline):** To prevent collision with existing kill patterns (e.g., standard ML adversarial models or simple boundary testing), the attack must strictly isolate the $a_1 = a_2$ exactness barrier, abstaining from invoking broader closed-loop coupling difficulties [cite: 3] or general surrogate model (e.g., OGAN, FlexiFal) approximation flaws [cite: 11, 12].

By strictly defining the grammar limits attacked by Formica et al. [cite: 1] and the physical boundaries documented by Marzella et al. [cite: 4], the Charon swarm will effectively map and dissect the remaining vulnerabilities of the HECATE architecture. Ensure this artifact is fully compiled into the Stygian operational log prior to v10-battery initialization.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEo4lhcMTwk-4gR9dOCvlcMSg8Kw5ejIZ4wMAt-_BSL9hRqA1mMLeFO7BXmnHVmk63_vJAikOG33V9B-Jg7zKrR87MVvetZVLms29sCdQC8-EJGPmRC)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPJkJeCt4fStCdv_TGtgBq3ScG2CZY7BxvhEd18x-SyEL1YA3dCnHS0m8AxF21wcYK7NgEz4LPEMi3Tmmq7q40bvbVbgTpKLL2uYFzStowh2gCkLLn_1BY)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsCHD6uIZgv3P9wRcO3D3Sgm6rrsjJpu1EZOz_OVAcR7mE04otKmPYh73YiMin2p4YG-vTPicI0Z5yiMR9JMKBfUoembtbXlOIvXxT8NeQ4pFilO53KvL9)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdjhEFXQ9tpr0eLWOapk1uhDNfZ4pbLI0E3Y0AFzs0lHvUImV2LXhrnFfaOLqb4CXgAJGIWHNXoQwM0lwqu3w4wdoBkga_hzcK4PHqJdW0XMXqNHjC)
5. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_eZVfxGWFNbcbogjPGqJtL3J36o8SO51CTwiFTW4VtvtKEEG4aFX0TSh93cAvqWmBl4Ei97K41IutenKeU2EEi4PsOZwh5PW8hRVlHkTdSZPr2Awg1O_kaIRMXgR6ru8MHUt6Irb8mEKCQogXPh0AIsimCsMo6mkTzA==)
6. [mathworks.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRMHW3VN0w7ojptAI95jrIuFd7scHXcnlE9IQeL5Ssnw64aB9Pe4bsM5rAOkntYODYcxSG2kkzzwjG8nb2rLZ-JEFruQ-1oV9qCivcY08Fvpe82jElSiHGUHaoddbAjgWGj5dwGY7NXgi_sTbiRJXGAZ-TH34VQw==)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYaK0GalIMUhEfCs5wNGeIGJZopzqXppD066FKIHjPUOgcTQHDqNaPke0sl_xZZbdsnuqESVKKg6YfKcxMSMqpBjV8rsAwCRAtT0HKgcofDUIWWKTI95YUMHLzhqMhwn0o_6ep0q0C5Fb5YP7mOmCVUu-y_goVDTYdYcMBhDcoI-UgdDLjDFmUPlPv3SLVBJAyJdJkEvlGsU2KHKNML37mhe778tFil0aw_rvX7-Cg5qg=)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXIeY8wuEA4_SPlbAxeaYZ_CJEmYCv5UEvUSXQchLXkAjybNFjc-c2ZVqyh48vaDM1aDVpSVAfW-SAtKTnZn8qFGPsbiXhvsgDED0deB-IzY7IgP-7RMpeHceM4bjp5aCT018Dwwepm02GbUAW_nrCNotktD3AeFAkJwfGBjL8nhgCFLYdSUWpo16tHg5kZTFAmLDwsbK5a8pTPw011-2aDj4c8A==)
9. [uantwerpen.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfvh-LcJmQYKHM402Ey0T2Xj8lYv8ckAwqqFIfzY2xQAmlObevQOWno1twwv8zW51bAf4YajZZQ7MQat8I3MHjfZiTJeuEo-2Q8-8Xdxeq6lfUbtWhaBgq5-IewZsJsJEYmQ1TaenTwG7Eqszruo4woSrQL3EGLw==)
10. [mountainscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEGlrE2VLBfb2PLAjCLyUQgXpLOiNR2kyd7sbLYTWyCcpJ4BelUI2AatKhIV3-twsg8iCZXDn64A89PxN-fygB3lsqv2tzZa7Km_tbRS2uYfnfiYKGuUD1kLyPEl18EvnOO8Xg-jselt6tdPIddtgemx4Jz2R3R1qoE2-EkozsEfyef8lkAAklvg==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4yROtwpZUyDWypWV3kKvV5OugpRp_pFMZp31ZfD7V6uyVD2Gk3W3EX-5n9_toItu6Wgct6FReOj6N5lKPHjtu3AIbzYbnf6Dd-QGsjnNA3spRI1xS)
12. [mdu.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtw6louou99lfGCZjSYv77BuSgtfn8PvhKv6UVlMKkEUnbITlswm6Jakw6GBZD5FPZmOzyzTZJ_znSbul-_E15zl1BCCWxL1jwErUgvS9ip2L_XT5g_XpbsAdCwiJxDceK8e8DLFaJdWwXr67QrQesbT34xWzzwn4W-RKj35j8wBVT66POOS0WT_kixr9hqGnK5i8bY8QI3-MJi-DBT5EzfcwT4JUaX0thnzuitthSs8u5B9rJaQME_dK2oM5vxJPKlHteRcozJmE-R3p-WOi6oy6sZofD40TBP7LicTQrL_1YFw3Gxr6fd6-TW5NNDpwNe2Jm9-Ax25y-dCEXbRUmh0paxbI=)
13. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQc-KksARwK3dVjiKZXySlQPm_1gOzGJoWQR2jIYKImcS2TLMt3vF64xKMvsnKcBMvNIo6-Htvaih00d7QiE-HDoHaErXbD3EOBMk1kD3X-L31AgTRWV97h3DVjDjVoh-Yt9iTlyMdgC3IQp56)
14. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIMK-f2W3HZizU_J-QVqUg6-sESCSv1CTi8IBCTuM6zvpCrv5ProKY58P5ozCzJkmi0WLouUDhOPAB6EwHWz4dRMcx9hafpEPS9qD-RJqDWVEK-f1RnFvDTSA=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkX71iR1SUIAaPf-ivsgFVay_004E4SJ_gSSEQ1G7lTJ_UGZWk27PEwHE_qfUsnwhSfnUzL0LT2786QQVoBY1zXYawavIElur6fCfQuupPy6gYg8Vc)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCLtx3FC3KsQ3YbtvSmzqiQuo6OgoFOioB1N-uZFKrY_zqOBdziCr1ae9q6ud3ul4kdNd2l7Gb0DT3f72zaJqOsBqNOhM4aco-8XNW09gUdKigkczR)
17. [uni.lu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhydC93hU3IK6mTSMdj0cAj6RQ3che9PtzrR6GPum3NnStpfmYjTSLvKqsQRE-JilrC-_jpdLXPJ7hA3XFl6Hh5K2hivG9VWlIve-eSbZFx0kFEfsOqB4fVaJKMrMoK6Jp6cuaff0qZZtsTw==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1j8lP5F50FtDgonkGJb3Tn8_N4T9Xg1LxW0EfrfOJ-4MUB6Yv801COtfArzr1UWlz9Tj7VM7jcQO-TGk9gKxsheMbWGu0dPYJN8kKAn2Qvgp1fSB8BGzR)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfLQlfUu1KK8BjPW_7PPsS4DYyTsU36VH-rsSXlbuWCfpTuXo3cgl3gbsAqnBCk_IsODx1nB02sddBIoklrJBQ_jFoCCWCDvh7IpBgQwN4cFkCOcQt32CoemD4UuJqdb6-NgxiR-cnr7E=)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvzFb1UlZOGcLeOewmFt84sU0JFA_Z3sDIjs3kCZFCAAtc6C6wMmmKIMPcCEr9Q-5I76RjV2t5cHZvaF2WI2xEH2X11KxVF07W4H751IlIGunQmwKHSiZQMaDxswbqfGe47mS_KIq8Cil2lhv7UFnqahYHgS6e9_qUZzsFXR8VdfNbA_hqoAPPViHDo3UB8tRmRLRFLAA0k3rWV_sMZ-WCipO7ZjZUiimUYjA2sOgqU7aPvNEaTw==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFazHPH_fNsjjx-nuiIHXEQZbzwOfBUwBiTU6Bkh6M-ei3ASNGJb1DFDgbA4jkfQ-16JHDwGWjJsjKljeDm5m2hieZKneTVYWCDlOsb6v8ZUAIEHJISdon9hS80kE-Y_A4no1U9s7y3qBFTZCmh7g==)

