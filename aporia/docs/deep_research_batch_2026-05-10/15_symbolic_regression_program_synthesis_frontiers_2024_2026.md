# Prompt 15: Symbolic-regression / program-synthesis frontiers 2024-2026

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdJVG9CYXIyM09LUE9fdU1QMVpETC1BWRIXSVRvQmFyMjNPS1BPX3VNUDFaREwtQVk
**Elapsed:** 273s

---

# Discrete Action Spaces and Substrate Vocabularies for Mathematical Reasoning: A 2026 Frontier Survey

**Key Findings**
*   **Symbolic Regression (SR) Grammars:** The state-of-the-art relies heavily on discrete, attribute-constrained grammars. Frameworks like PySR utilize context-free grammars with mathematical primitives, while newer neural approaches (DSO, SymbolicGPT) treat grammar generation as sequence modeling or autoregressive decision-making over discrete token spaces.
*   **Library Learning:** Systems like DreamCoder and LILO build hierarchical substrate vocabularies by compressing recurring patterns into abstractions via E-graph matching and branch-and-bound search (STITCH).
*   **LLMs as Semantic Mutators:** FunSearch and AlphaEvolve bypass strict formal grammars by using large language models as mutation operators over standard programming languages, achieving state-of-the-art heuristic discovery.
*   **Theorem Prover Registries:** Interactive Theorem Provers (ITPs) handle vast "primitive registries" (hundreds of thousands of lemmas) via embedding-based retrieval (ReProver), graph neural networks (ENIGMA), and online machine learning (Coq Tactician).
*   **Categorical Formalisms:** Advanced compositional rules are increasingly framed via applied category theory. Operads, PROPs, and multicategories explicitly model computational primitives, data flow, and resource calculus in string diagrammatic formalisms.
*   **MCTS over Typed Grammars:** Mathematical reasoning is now explicitly framed as Monte Carlo Tree Search over unbalanced hypergraphs of formal logic (HyperTree Proof Search, AlphaProof), treating the theorem-proving environment as a rigid discrete action space.

**The Substrate Vocabulary Problem**
Designing a discrete action space for an autonomous Learner requires defining a robust substrate vocabulary: a collection of primitives, compositional rules, and abstraction mechanisms. In computational mathematics and program synthesis, this challenge manifests as defining the "grammar" of searchable spaces. If the primitive set is too small, complex ideas require deeply nested, computationally intractable expressions. If the primitive set is too large, the search space combinatorics explode, defeating heuristic search algorithms.

**Evolution of Symbolic Search**
The frontier of symbolic reasoning has evolved from brute-force enumerative search and unconstrained genetic algorithms to tightly constrained, neuro-symbolic systems. By integrating deep reinforcement learning with rigid evaluation environments (like Python sandboxes or Interactive Theorem Provers), recent architectures explicitly factor mathematical reasoning into a generative phase (proposing actions/mutations) and a verifiable execution phase.

**Theorem Provers as Action Spaces**
Proof assistants (Lean 4, Isabelle, Coq) offer the ultimate typed grammars. They restrict the valid action space dynamically based on the current proof state. Modern systems navigate this by treating premise selection as an information retrieval problem over a dynamically growing library, transforming automated theorem proving into a sophisticated, context-aware sequence of discrete valid actions.

***

## 1. Symbolic Regression SOTA and Discrete Grammars

Symbolic regression (SR) represents the most direct analogue to finding a discrete mathematical action space, as its primary objective is identifying a closed-form, human-interpretable mathematical expression that maps input data to output data [cite: 1, 2]. Unlike conventional deep learning, which optimizes continuous weights within a fixed functional form, SR searches the combinatorial space of mathematical operations and their structural arrangements [cite: 2, 3]. 

### State-of-the-Art Frameworks (2020-2026)

**PySR**
PySR (Cranmer et al.) is a high-performance framework implementing multi-population genetic programming [cite: 4, 5]. Written in Julia with a Python interface, it evolves candidate models represented as expression trees. 
*   **Grammar / Action Space:** PySR utilizes a user-defined Context-Free Grammar (CFG) where the terminal nodes are input features and ephemeral random constants, and the internal nodes are mathematical operators (e.g., `+`, `-`, `*`, `/`, `sin`, `exp`) [cite: 3, 4]. 
*   **Constraints and Search:** The search space is navigated via evolutionary strategies (tournament selection, subtree mutation, and crossover) [cite: 3, 6]. PySR uniquely enforces "soft constraints" (penalizing physical impossibilities like finite slope violations) and "hard constraints" (pruning the search space). The constraint checking heavily leverages the SymPy computer algebra system, tracking structural complexity to maintain a Pareto front of accuracy versus parsimony [cite: 4].

**Deep Symbolic Optimization (DSO)**
Petersen et al. frame SR as a sequential decision-making process formulated via deep reinforcement learning [cite: 7, 8]. 
*   **Grammar / Action Space:** DSO employs an autoregressive Recurrent Neural Network (RNN) that emits tokens sequentially to build an expression tree in pre-order traversal [cite: 2, 8]. The grammar is strictly defined by a set of mathematical operators [cite: 9]. To ensure validity, DSO incorporates *in situ* structural constraints that mask invalid tokens during the RNN's sampling step, ensuring the generated tree complies with arity and domain restrictions [cite: 8, 10].
*   **Advancements:** Recent extensions like DisCo-DSO (Discrete-Continuous) allow the model to jointly emit discrete symbolic tokens and continuous floating-point values, bypassing the need for secondary constant-optimization algorithms like BFGS [cite: 8].

**SymbolicGPT and Transformer Models**
SymbolicGPT (Valipour et al.) treats SR entirely as a language modeling task [cite: 11, 12].
*   **Grammar / Action Space:** By interpreting symbolic mathematics as a formal language, SymbolicGPT uses a blank parse tree that is "decorated" with choices of operators and variables [cite: 11, 12]. The grammar enforces well-formed mathematical expressions as valid "sentences." 
*   **Mechanism:** The framework relies on an order-invariant PointNet-style embedding (T-net) to represent the dataset, which conditions a GPT-based transformer to decode the symbolic equation token-by-token [cite: 11].

**Recent 2024-2026 Work**
*   **LaSR (Large Language Model Symbolic Regression):** Integrates LLMs with traditional genetic algorithms (like PySR). The discrete grammar involves "abstract textual concepts" inferred by the LLM from high-performing hypotheses. The LLM acts as a semantic crossover/mutation engine zero-shot, bypassing strict random subtree swaps [cite: 6, 13].
*   **SR-LLM:** A framework integrating LLMs via Retrieval-Augmented Generation (RAG). The LLM breaks down physical domain knowledge into "symbolic primitives," which are then assembled into complex expressions using deep reinforcement learning [cite: 14].
*   **DVISR (Deep Variational Inference Symbolic Regression):** Transitions SR from finding a single best-fit equation to estimating a Bayesian posterior distribution over the grammar space via variational inference [cite: 15].
*   **Graph-based SR (IsalSR / GraphDSR):** Moving away from expression *trees*, recent models utilize Directed Acyclic Graphs (DAGs) to reuse shared subexpressions. To eliminate operand-order ambiguity in non-commutative operators (like division or subtraction), these grammars apply "unary decomposition" (e.g., $x - y$ becomes $Add(x, Neg(y))$) [cite: 2].
*   **SR4MDL:** Utilizes a Minimum Description Length (MDL) metric via a trained "MDLformer." Instead of relying purely on prediction error, which does not monotonically decrease as the symbolic form approaches the target, SR4MDL searches the grammar space by minimizing the description length of the symbolic string [cite: 16].

### Discrete Grammars Analyzed
The overarching trend in SR is the shift from unconstrained Context-Free Grammars to highly constrained, context-aware action spaces. Unrestricted grammars yield combinatorial explosions. Consequently, systems now deploy **dimensionally-consistent attribute grammars**, which only generate mathematical expressions that satisfy physical unit constraints (e.g., not adding meters to seconds) [cite: 7]. By incorporating these constraints directly into the generative substrate (either via masking in DSO or attribute restrictions in PCFGs), the discrete action space is exponentially reduced, yielding higher accuracy with fewer evaluations.

***

## 2. Neural Program Synthesis and Library Learning

While symbolic regression searches over isolated mathematical expressions, program synthesis searches over fully-fledged programs involving loops, conditionals, and higher-order functions. The primary mechanism for managing the combinatorial explosion of the action space in program synthesis is **library learning**: the autonomous construction of a substrate vocabulary that expands as the agent learns.

### DreamCoder
Ellis et al. introduced DreamCoder, a system for inductive program synthesis that automatically derives a library of program components alongside a neural search policy [cite: 17, 18, 19].
*   **Mechanism:** DreamCoder utilizes a Bayesian "wake-sleep" algorithm. During the "wake" phase, it attempts to solve problems using its current primitive registry. During the "sleep" phase, it performs *abstraction* (growing the library) and *dreaming* (training the neural search policy on hallucinated tasks) [cite: 19, 20].
*   **Primitive Registry / Grammar:** The underlying grammar is a probabilistic typed lambda calculus. 
*   **Composition Rules (E-Graph Refactoring):** To build new primitives, DreamCoder applies a refactoring algorithm based on **E-graph matching** (equivalence graphs) [cite: 17, 18]. It identifies common sub-components across multiple synthesized programs, abstracts them, and adds them to the library as newly coined primitives. For example, it might discover that combining a `filter` primitive and a `maximum` primitive creates a highly useful `nth-largest` function, which then becomes a discrete action in its vocabulary [cite: 18].

### LILO (Library Induction from Language Observations)
LILO (Grand et al., 2023) is a neuro-symbolic framework extending the library learning paradigm by tightly integrating Large Language Models [cite: 21, 22, 23].
*   **Mechanism:** LILO iteratively synthesizes, compresses, and documents code. Unlike DreamCoder, which relies solely on a neural network trained from scratch to guide enumerative search, LILO uses pre-trained LLMs to guide the program synthesis [cite: 21, 23].
*   **STITCH Compressor:** A critical limitation of DreamCoder was the computational expense of evaluating lambda abstractions. LILO replaces DreamCoder’s internal abstraction engine with **STITCH** (Bowers et al.), a symbolic compression module. STITCH executes an optimized branch-and-bound search over large datasets of lambda calculus programs to find optimal abstractions 1000x faster than DreamCoder's original method [cite: 21, 23].
*   **Auto-Documentation (AutoDoc):** When STITCH identifies a structural pattern and registers a new primitive, that primitive is purely symbolic (e.g., `fn_001`). LILO uses an LLM to generate human-readable names and docstrings for these abstractions. This semantic grounding allows the LLM synthesizer to successfully utilize the new primitives in future synthesis tasks [cite: 21, 22, 23].

### Neuro-Symbolic Systems for Mathematics
The library-learning paradigm is being explicitly ported to symbolic mathematical reasoning:
*   **ConPoLe:** Poesia et al. utilize contrastive reinforcement learning to solve domains like equation simplification and Rubik's cubes. Crucially, they apply DreamCoder-style abstraction techniques to automatically learn mathematical "lemmas" from solutions. Rewriting mathematical trajectories with these learned lemmas strictly reduces the length of future proofs [cite: 24].
*   **DiffDock & Differentiable Programs:** Beyond functional primitives, neuro-symbolic research is extending library learning to continuous spaces (like molecular docking in DiffDock) and synthesizing functions composed of differentiable primitives [cite: 25].

***

## 3. LLM-as-Program-Synthesizer vs. Non-LLM Symbolic Regression

Between 2023 and 2026, the paradigm of treating language models as the primary generative engine for program synthesis has yielded unprecedented results. Systems like FunSearch, AlphaEvolve, and SOAR rely on treating the LLM not just as a code completion tool, but as a formal mutation operator over a discrete action space of source code strings.

### Key Systems

**FunSearch**
DeepMind’s FunSearch (Searching in the Function Space) combines a frozen LLM with an evolutionary automated evaluator [cite: 26, 27].
*   **Mechanism:** Instead of searching for the mathematical solution directly, FunSearch searches for a *program* that generates the solution. It uses the LLM as the crossover/mutation engine. Existing high-scoring programs are sampled from a pool and placed into a prompt; the LLM suggests improvements, and the evaluator executes the code to generate a scalar fitness score [cite: 26, 27].
*   **Results:** FunSearch discovered verified new lower bounds for the Cap Set problem in extremal combinatorics, marking one of the first times an LLM generated verifiable new knowledge in an open mathematical problem [cite: 26, 27, 28].

**AlphaEvolve**
AlphaEvolve operates as a generalized, closed-loop evolutionary coding agent [cite: 29, 30].
*   **Mechanism:** It isolates sections of a code skeleton marked as evolvable. A database maintains candidate programs. An LLM ensemble (powered by Gemini) acts as a "semantic mutator." Because the LLM understands data structures, algorithmic patterns, and optimization tradeoffs (having trained on billions of lines of code), its proposed mutations are highly targeted, bypassing the random bit-flipping of traditional genetic algorithms [cite: 30].
*   **Results:** AlphaEvolve improved the 56-year-old state-of-the-art for 4x4 matrix multiplication and optimized complex hardware RTL circuits and data center scheduling heuristics [cite: 30, 31].

**SOAR and Trial-and-Error Learning**
SOAR acts as a continuous learning module that refines LLM-generated programs based on execution feedback [cite: 32]. It teaches the LLM to refine its own search trace iteratively, serving as a drop-in upgrade for systems like FunSearch or AlphaEvolve [cite: 32].

### Comparison: LLM Synthesizers vs. Non-LLM Symbolic Regression

The framing of the "discrete action space" differs fundamentally between these two paradigms:

| Feature | Non-LLM Symbolic Regression (e.g., PySR) | LLM Program Synthesizers (e.g., AlphaEvolve) |
| :--- | :--- | :--- |
| **Action Space** | Explicit, user-defined grammar (e.g., $+, -, \sin, \exp$). The space is a rigid Abstract Syntax Tree (AST) of mathematical primitives [cite: 3, 4]. | Unbounded formal language semantics (e.g., Python, C++). The space is the entire syntactic landscape of Turing-complete code [cite: 30, 33]. |
| **Mutation / Transition** | Structural operations: random subtree swaps, node deletions, constant perturbations [cite: 4, 6]. | Semantic operations: logical refactoring, introducing complex numbers, altering data structures via language tokens [cite: 30, 31]. |
| **Priors** | Hard-coded dimensional analysis, SymPy algebraic simplifications, Pareto complexity penalties [cite: 4]. | Implicit knowledge embedded in LLM weights (e.g., naming conventions, algorithmic design patterns, optimization heuristics) [cite: 30, 33]. |
| **Evaluation Speed** | Extremely fast. Expressions are compiled to SIMD arrays or evaluated algebraically in milliseconds [cite: 34, 35]. | Slower. Requires complete sandbox execution of Turing-complete code (though often parallelized) [cite: 26]. |

In essence, non-LLM Symbolic Regression frames the discrete action space from the *bottom up* (composing primitive arithmetic operators). LLM synthesizers approach the space from the *top down* (utilizing the latent structure of human-written code as an informal, massively parameterized action space).

***

## 4. Theorem-Proving Systems and Library Learning

In Interactive Theorem Provers (ITPs) like Lean 4, Isabelle, and Coq, the "primitive registry" problem takes the form of **Premise Selection**. These systems possess vast standard libraries (e.g., Lean’s Mathlib, containing hundreds of thousands of previously proven lemmas and theorems) [cite: 36, 37]. For an automated agent to reason in this discrete space, it must dynamically query this massive vocabulary to decide which "primitive" (lemma) to apply at any given step.

### Lean 4 and Mathport
Lean 4, driven heavily by its Mathlib library, is currently the center of automated formal mathematics [cite: 37, 38].
*   **The Primitive Zoo:** Mathlib contains upwards of 260,000 accessible premises [cite: 37]. 
*   **Machine Learning Premise Selection:** Native implementations inside Lean (such as the `suggest_premises` tactic) utilize fast, incremental random forests trained directly on Mathlib. The features used to define this discrete space include human-crafted n-grams, names, and bigrams of the logical state [cite: 38, 39].
*   **ReProver (Retrieval-Augmented Prover):** Developed via the LeanDojo framework by Yang et al., ReProver uses a ByT5 transformer to generate tactics [cite: 40, 41]. Crucially, it tackles the primitive registry problem by using a retrieval-augmented design: given a proof state, it retrieves relevant premises from Mathlib via dense embeddings, concatenates them into the LLM context, and generates the next tactic [cite: 41, 42].
*   **LeanHammer:** Translates Lean formulas into first-order logic to be solved by external automated theorem provers (ATPs) using neural premise selection [cite: 38].

### Isabelle and Sledgehammer
Isabelle’s Sledgehammer is the archetypal tool for integrating library learning with automated reasoning.
*   **Traditional Sledgehammer:** Relies on symbolic filters like MePo (iterative relevance filtering) and machine learning models like MaSh (Naive Bayes, k-NN) to select a subset of hundreds of premises. These are then shipped to external first-order ATPs (like E Prover or Vampire) [cite: 36, 43, 44].
*   **ENIGMA:** Incorporates property-invariant Graph Neural Networks (GNNs) to guide the external ATPs over the Isabelle problem space [cite: 45].
*   **Magnushammer:** Represents the modern, neuro-symbolic evolution of this pipeline [cite: 44, 46]. Instead of relying on external provers, Magnushammer uses a two-stage transformer pipeline (Select and Rerank) trained contrastively on Sledgehammer proofs. It feeds the selected premises *directly* into Isabelle's native tactics, proving that neural models can autonomously map proof states to massive discrete primitive registries without intermediary logical translation [cite: 44, 46].

### Coq and Tactician
Coq utilizes Tactician, an online machine learning plugin that assists users in tactical proof decisions [cite: 47, 48, 49].
*   **Registry Handling:** Tactician extracts features from the Abstract Syntax Trees (ASTs) of proof states (specifically, term walks of length one and two) [cite: 50]. 
*   **Online Learning:** Instead of training on a frozen dataset, Tactician’s models (k-Nearest Neighbors, Random Decision Forests, XGBoost) update *incrementally* every time the user performs a step in a proof [cite: 47, 50]. This makes the primitive registry highly contextual and localized to the specific branch of mathematics the user is currently working on.

***

## 5. DSL Design for Math Reasoning: Primitives and Architecture

Domain-Specific Languages (DSLs) for computational mathematics (Computer Algebra Systems) provide deeply engineered blueprints for organizing primitive zoos. Their design retrospectives reveal how to structure a discrete action space for logic.

### Mathematica (Wolfram Language)
Mathematica’s entire architecture relies on a single, monolithic design principle spearheaded by Stephen Wolfram: **Everything is an expression.**
*   **Primitive Organization:** The fundamental data structure is the immutable tree. The mathematical expression $x + y$ is represented as `Add(x, y)`, an ordered tree with the head `Add` [cite: 51, 52]. This means there is no fundamental data-type distinction between a mathematical formula, a dataset, or a user-interface element; all are symbolic expressions manipulated via pattern matching and rule-replacement algorithms [cite: 53, 54].
*   **Evolution:** Recently, Mathematica has integrated LLMs as "superfunctions" alongside classic primitives like `Integrate` or `Solve`, framing neural text generation as just another evaluable node in the symbolic tree [cite: 52]. 

### SymPy
SymPy is an open-source Python library for symbolic mathematics [cite: 51, 55].
*   **Architecture:** Like Mathematica, it relies on immutable expression trees to allow for expression interning and hashing (which enables aggressive caching). 
*   **Assumptions System:** A key feature of SymPy’s registry is the assumptions system. Symbols are not just blind variables; they are tagged with properties (e.g., `positive`, `real`, `integer`). SymPy’s rewriting engines will not apply simplifications unless the assumptions provably allow them (e.g., $\sqrt{x^2} = x$ is only applied if $x$ is tagged as non-negative) [cite: 51]. This organizes the primitive zoo by logically sandboxing valid operations based on data-type proofs.

### Magma
Magma is a highly specialized system for algebra, number theory, and geometry [cite: 56, 57, 58].
*   **Design Retrospective:** The foundational architecture of Magma (as outlined by Bosma, Cannon, et al.) is explicitly based on **universal algebra and category theory** [cite: 56, 57]. 
*   **Primitive Organization (The "Magma"):** Unlike Mathematica’s untyped expression trees, Magma enforces a natural *strong typing* mechanism. Every object generated in the system belongs to a unique algebraic structure called its "parent" (or magma) [cite: 57]. Structures are classified by "variety" (a class of structures sharing defining operators and axioms, such as the variety of all rings). Computations are strictly checked against the morphisms of these structures, providing mathematical rigor natively in the language runtime [cite: 56, 57]. 

***

## 6. Composition-Rule Formalisms (2020-2026)

To construct a formal "action space" for a Learner, the rules dictating how primitives compose must be rigorously defined. Recently, computer science has turned to Applied Category Theory to formalize these rules explicitly. Between 2020 and 2026, formalisms such as Operads, PROPs, and Multicategories have been utilized to structure programmatic primitive registries.

### Operads and PROPs
An operad describes operations with $n$ inputs and one output, alongside strict axioms for how these operations plug into each other (composition) [cite: 59, 60]. PROPs (Products and Permutations) extend this to operations with $m$ inputs and $n$ outputs.
*   **String Diagrams:** In recent computational theory, PROPs are represented visually and algebraically as string diagrams. Bonchi et al. introduced the "resource calculus," utilizing string diagrams to model concurrent systems [cite: 61, 62]. By mapping computational primitives to string diagrams, systems enforce data flow, ordering constraints, and resource allocation natively in the geometry of the syntax [cite: 61, 63]. 
*   **Freecat and Probabilistic Generative Models:** Category theory is being used as a generative prior for machine learning. The "Freecat" framework establishes probabilistic generative models of morphisms within a free monoidal category. By parameterizing generating objects and wiring diagrams, this system provides a highly structured composition rule formalism that rivals traditional CFGs for learning programming structures [cite: 59].
*   **CoREACT and Lambda Calculus:** The CoREACT project (2023-2027) explicitly uses operads for Coq-based rewriting and program synthesis [cite: 64]. Furthermore, research into the combinatorics of typed lambda calculus heavily relies on "colored operads" to enumerate valid programmatic expressions (program synthesis by typing constraints) [cite: 65].

### Multicategories
Multicategories are closely related to operads but are heavily utilized in modeling typed functional programming languages, specifically those with first-class control primitives or linear type theory [cite: 66, 67].
*   **Application to Synthesis:** These structures provide the mathematical backbone for tracking resourceful types (e.g., graded or linear types) during program synthesis. By structuring the synthesizer’s action space as a multicategory, the search space is aggressively pruned of ill-resourced or logically invalid programs before they are even evaluated [cite: 60].

***

## 7. The Discrete Action Space: MCTS over Typed Grammars

The ultimate frontier of discrete action spaces for mathematical reasoning involves treating formal mathematics (via systems like Lean 4) as a turn-based game, navigable via Monte Carlo Tree Search (MCTS). This explicitly frames math reasoning as "MCTS-over-typed-grammars." 

### HyperTree Proof Search (HTPS)
Introduced by Lample et al. (2022) for Neural Theorem Proving, HTPS brings the AlphaZero paradigm to mathematics [cite: 68, 69, 70].
*   **The Action Space:** Unlike chess, where a move leads to one new state, applying a mathematical tactic can split a goal into multiple independent subgoals (e.g., proving a base case and an inductive step). The state space is therefore an **unbalanced hypergraph** [cite: 68, 71]. 
*   **Mechanism:** HTPS runs a Select-Expand-Backpropagate loop. A policy network selects a leaf node (an unproven subgoal) and proposes tactics (discrete actions from the formal grammar). A critic network evaluates the probability of proving the newly generated subgoals. The values are backpropagated up the hypergraph to update the visit counts and action values [cite: 68, 71, 72].
*   **Results:** HTPS achieved state-of-the-art results on Metamath (proving 65.4% of held-out theorems) and heavily influenced all subsequent systems [cite: 69, 71].

### AlphaProof
Google DeepMind’s AlphaProof (2024), which achieved a silver-medal standard at the International Mathematical Olympiad (IMO), is the direct realization of MCTS over Lean's formal grammar [cite: 73, 74, 75, 76].
*   **The Action Space:** AlphaProof operates entirely within the Lean 4 proof assistant. The "grammar" is Lean's tactic language [cite: 75, 76]. Lean provides the perfect MCTS environment because proof verification is deterministic and automatic, yielding clear scalar rewards [cite: 74, 75].
*   **Test-Time RL (TTRL):** AlphaProof overcomes the "finitude of data" in mathematics by generating millions of related problem variants at inference time, allowing the agent to adapt its policy network specifically to the problem at hand during the MCTS rollout [cite: 76, 77].
*   **Retrieval Augmentation:** AlphaProof relies heavily on a retrieval-augmented registry to supply the MCTS with valid premises from Lean's vast library, merging the library-learning/premise-selection paradigm with hypergraph search [cite: 74].

### Best-First Search and LLM Heuristics
While MCTS is powerful, other systems argue for slightly different traversal mechanisms over these typed grammars:
*   **UlamAI Prover:** Explicitly characterizes its architecture as "search, not hope." It utilizes a best-first search with beam capping over Lean proof states. At each node, an LLM proposes 8–16 candidate tactics. Successful compilations expand the search tree. Crucially, UlamAI introduces a *repair loop*, where Lean compilation errors are fed back into the LLM to generate targeted fixes [cite: 78].
*   **BFS-Prover / StepProver:** Models like ByteDance's BFS-Prover and InternLM2.5-StepProver argue that simpler Best-First Search, augmented with a strong "critic" model to capture preference information during tactic generation, can outperform heavy MCTS implementations by relying on expert iteration and deeper search depth [cite: 77, 79].

### Conclusion of the Frontier
Project Prometheus's goal of building a substrate vocabulary for a future Learner aligns precisely with the 2026 convergence of formal theorem proving, language modeling, and reinforcement learning. The discrete action space is no longer a blindly enumerated grammar of arithmetic operators; it is a continuously expanding library of abstracted programmatic constructs (LILO, DreamCoder), tightly governed by the categorical and type-theoretic rules of Interactive Theorem Provers (Lean, Coq), and navigated autonomously by deep heuristic search algorithms (AlphaProof, HTPS) capable of self-correction and continuous semantic mutation.

**Sources:**
1. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYYr2HfxeKDhjDH1h1xkh-STPhiKkX-USoxfN3kkI0Q_fb2i9yNE8ePxbEJbMYF_q8nmqCQzYljeI1GtLG6E2RHE6BhxMVmhGkpowPBrQx54RDlhLl4B_R20E_NpG2qI4pLosH8bZ0aUjim-cZ)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxrcflls64eDZjPGDsB0-_BhQm6QxgAAOBVKKeigj_C-WF1XVVrFNtxrWUX5sQ-L4TslXCCw8CEo_2eYc0x_rFObf-QX8uB9xIqAMieI0IPzIjRY2-oKvZ6A==)
3. [ml4science.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGX63j6RVTVhZdbX7nVmzGipAGKJeol-SB3qEYEiy7sASoyAKtrhdrEvJqcEI9OwI1x63GQF7CaLi3yBTgriufrMe0EBxHZtamzJzue7q2ut37q-xWmyCYmr4HE5G0yPgN0d43YwGxC2avjVDyBgfn09PFwaLx5)
4. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcPfEJxqXAGUJ5Y4jcKmvVnlJkO1fZ9oL-CvG9cy2pkzvauVUNF_IyyUVbV-nAdzZJwfcfTyBDN5Ry1g_McpF3aiHcVnmO-CDCNJO0T4nq1EiXRHHWQj3Z4HjVTiEf)
5. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFz6v95Ae3f36jE45Gneknv8sKjrT0rwi4R2c1gNTN-hlRDzaaUgZOy0ULakRsTe0I35lBR-mBrRXe0-0AM8Rpnk6P5J--vSu2IimRL-8p4oq0lSInkPhe3vw9ekQ==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHKF0uB_hm4uR4PVcUZHY352CD_CU9Rh-aREhDziwD_5qP2-cIXX-bZafts68tV5xIfY2ISXWoD3j5QedZK4HCMlZG0slk6FbTVOvzg4J9NhGZ-SJ-TGrEuA==)
7. [ijs.si](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGutHt-5VLtnsB-oXOmO0UhfLwtJUyZkWzmRyGxQbKfmaD5mLUkIESal-S4OZAWMaUwY-WmB2ABgSkvhjW-QaK2b0_kpiXk8aROpslRwFTJo3INz0VEMDpkRt1U4P1p5YYVm-s8wT4nYEegMRMEgHdJwJNQUqwFJIvQ5w==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUfwGjepN7bdNsS4p-RCjJ4MYGXsV-wNXtbUCbfiNCJ5ZLStt4an6hwnLfWtZWQmqnMPoLNlwQz12PUKZjh89nFjp0OuGvxdv3xglWIL7d7gcmOgsBTzcIYA==)
9. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-2jvZf7iQZwJcIjGcAV6FAR20ymPedtOgUduHA38qR0yqDYR4d93uqaiE5iPkx3UHYyo7BGypVpsl3Sgz2HrrkM7u3HRehHZwjOU10BP-pVTsdL4D5zCwN7kM6ErnMyE=)
10. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFP5dbZXvHWXq3fztminVuZFDhe32LQbPxsurur122A7qdtwIPyrLZcamdk3SeLF3MLFU4GhuBG9hpUeaAlQynMGTC2dManHI32U8k6zOGuFIQZJjwonhyOiOw2kOD70W75IQWg9vyXsZ4o24FJx6PMpionaEvddyyvFdnnt__hDn7bbNoT8OzpEhw0cBCPqVobcJ3VmVwHwksbP5pHz_-C1X5G5Imi)
11. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9w1F_1E8zxTtcTN5MwGU5uj0GH1q6lG7aD2YyjTUhrvWYd2VsUki5C2B-hjrEwax9j1kfXSd0yd6kBSMvWqpOr85_7pPc6EmiWfNRx-jl_bNF4n95Tgi57gGuj28zjz6o-YNmT3O_Vp7q36Jc)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgbsZkkGu7lN7FXWCBG3hOVZXtHquwSY-S_6-rouPWewDn53rKlQFkrzfEW9KCaRDrhDy8KcGMd1Emid2oBZp2AzBpQycUNGFwmkKEXUZ5Z3NHVbQkUiN9ra6vVX_rh51Fuvexx_ZtY5NBUX2Y8EJO8nVIVpHgKW74AR-1yqUBStTTqx9utaQVu_xeXIb_qZvIrJyIty7PocqLztsKcG-W-go15r-obLo2kpI=)
13. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmoixbcCHbtC7KZfO-1AANSrgfzyoVPpyt9nn_Or7xKgx3SL4RVIIz2g3pcf1LUwB-NFcY3w0ywnBqMUZ99sBA0yHpuG0WJ9TMe8zOnbOrjhq4-PJmcEIk8Ipp3SVzp3_hogOvB_Tq_u7vlBvPPfFHP-91V-y4JxFsbw4JeNBtGeHZmNDIhoTQ_ZbuWtzSqFqpqoAowfpO4KZjDT7xfpbzdIVB_1p2okUL8DRphEWpK0VQ-IsE)
14. [pnas.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXwfUS93PlI9re2rLaGzCLFMYmqeiZpwB7AcXWOo75H5J9TreIF3FCDvXnHIdOi9JlHoJQmZtC9TFnA8drdNyQzvfR5MPAiPLka2g6XzA-HmQOWaODPnPKZN5ge1oQXnJv3un44uo=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJ5gCBdZmRvQtd9VVhV8qo041cKCpeQkZdGD-q_uXhDN0eKjfsnzYyJWKAZ2JOuH42gCRy1rEaTWR6ryD7InEobda4TiLA0MZ7N9vyjJJS_oywu7PjGSr3eA==)
16. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTPjsFevDy5ShZKvgnmvay3j7jo99qUrlloPLbuZggx31plHPPmba4HZWQNF0yM9UZySiS_slXHEnMtMWjW8a2LSNe7E4qvjY_reozdZfIe1-m8nHNFHU1iAaPTK2pn08=)
17. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHScgsWL8ETbDyLaR9-oSlDBW5bW67rlwwYNvOGqqaFIyvLmg1txSlYmhgtasGz0in82-WijVdnQCEOpKE7x3cVAWvF4gs-9WDBnInunm5dtjCUTAutOItC1Ls_8sjbUOCVBjS-1FFxVLXi80oEc7o3aQ==)
18. [neurosymbolic.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFX6nRor0vOyeCYQe_2vdCbXfJ5M4HfHOyL7fp9LWcwNuZpyn92nYTNb7EgdkS468Cda_K9Rm6PyKQy8e23nNlf7sbJDr8DTIE5GDMTaFon4mbenl5Mkl_0IAJ-8Q_xZ2znI4o4gMqh3guPO1msuA==)
19. [cornell.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYZkCbCdGI3z2feZB2_3fxdVD0VtdQP6K8oS43xdryzhzT8ZNfCbb4KEIHysDV4JEsu_O5J8OXiz5GVn8w5NEmw7eXTjLAQsz6AgdtV6_Vcmw9cjaoXsTIsoBix8Y1gFm50cykMqWNx2R5xy23BTWoz8z5aemoo_7I3kR_g2Pg95c=)
20. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQIpvitV_UY-cz_StRgyQG8tIGV37Z4NcOEm9k9z04_LhN-GqhdvgTduys2pTdrzS2fi5r22kox-cXPSy0GZ5XF_9mB7A7L-j-qPnFPlzoyHMrOwsUNSCOpLEfWUUUFuag)
21. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQG72oLvjmQxRiszdRbMBGk-OlIsSvhYSgDpAsAO-uLwd6eTdk8aG2CJ5sI_F04ZwBIUaRqC3cBnpbD8Fu45N70UDRrWaDguHO0T8vdnhhmmwYffy2bQpZmoJ6OIaZYb8=)
22. [marktechpost.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExlkBOntybY5hUD0760M6MiqD1JJnNJ3Z2wVxDwllCYpovYiln4Sy2ZgCIQk5pd5r05NwSUGcRnS9iT7ETj4V4e5Z022xnTZ1QFoD4WEGsm-5qZCyaO2ZEicDWNPcT91IZRqL2C0L8YwtX_rhGJN0xPdAgkPJEDl1yKCpcthtfU19ooR24vF7Ju0NqehBqTuarwql8qPr1csBJtprf1zKWeNbwBiazkAYf7t0Ohkb0yAcBBhzYxKC67LeZbSsj8cxmoXl-l7aJFTPlCrK3qi9ZRm1Wdg==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETRT4swqHlh9suDtJQLDp6iYh8VbezBaAo95R0E5-ic-xSHyJU8uz11UAK5I6Xs27Pj1V-VMQoOeVPJf19JxemZtSHQV38TdAHhYzhkr8gK65h6Lyjg6tpmw==)
24. [neurosymbolic.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUdagZRVAR10glU8kCLFY3xj_jLTDE5goNq79HNHLfLSaFydqgaZ7KxxTPciptuwHH3PGi2JP8Aq9KlcOJj9W7_w6tCOg40NoLYaNQ99lrA3yUTbKXqW6S0W2YjGdR0VBjmA==)
25. [neurosymbolic.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0xRe55ZgmRr2Z6J4wfNDFXs7uIKPs9clWzNVXzSluz3niHqU3gRAxJBvJuqIwQPUcpBNKc2sdU4_Ud0pfWz9cZ3b59ecvmyei0qsxym-w38m6V6SXjdSK8OcoiMmJr5EI)
26. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJYzirgW79VNSgq82To9tdmL2KSkdiZkgn-W3LXvkyXoaHk1IeY1VjNdedmE00uxftODzPRSyIUCvVCGKc6RtqzJcCmDMBXubpASS6tKJfaAPLVjkr-uQ6-Nbldvk=)
27. [googleapis.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-LxgDwMhB33DsHfrGBIwrbws3yqMOYyC7MIb2WaqSm_nuIhY8Lmz6qq89nDIg0OKOQtGTFCj3bLxKI99H9c5wP1vSVlq0R2G2AaZ6DG7eCuZ2542rv80tUhzqR0b1GvQ2zyc-JYpsEalhcL0fxDDkia0HDwToZnC1VnUsVjCWgLZcTF4EoSlRpzVxoXgVVRNhaM36VmTBRxphBQQWImVkxt_K_lTwyBztAxA6T_Kz9sVpLj9Y7SxifScRMXrEcwMba-LyJh5VEerJmrHXzxORf2CjOgusksx5d3F-G_Cyoa86JwSjUsDjAKw6goxiRxYg1ey7LZRK80TE6iWSJu-okPM1A1BqtPQQLxugyR4kMJw_qgMCHS4D)
28. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQES80IOsIUXtLGcVGuk7RF-aHY3rgXA7mZt_smULob3aj1f9KAf_9dhgz2rKKDA9bP7ojNYTkCnkGxMmYEAjUWAWQtq_ysZzAsvblTZtcRBu-38vmAZxGzDui4d5TG9vq_AMu7Z1hM-1ZDKejfG9-x9fGYxL8vowA==)
29. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJIKxEqHclbwkgVmoTHXvQqv62Lg7MKn6k8_Zet-2MRh_UQ-N30GMYqrxPC0xGYHFBqUB8kcSQ7vGaQdyJ47jnd_Ve_ejfv3RdEeDBaOKLc1G0duD81HxQ7PiS3HPfx9O4mPa0VzjYIA==)
30. [rewire.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhurwDwt50j-FfPBaXe6fkcCjuq05u_ZrBlxIAw3IkxSO16-0PabWGYnNLcM5lLQZQnCaPeJMFEqZ_UQWeWa_jh7dS-heSdKVS3-XEP_zDd0hop_dyaHroCpI8p7qGYf17-eg6Fd_niJ16RKMrPMRPsJT0I1_krIVR0JwTprrWsqyEY-PhBA==)
31. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbMtoC19T6FXNRNZGkD6f9YFG2amnp_rPv7SBFFZ-Ucta8UoyTBwQKpCKtvweVBeKaWcXoYaufQOqUnQkj5b9bOnaSVJUViRYPMlRVhjRLg-S-fl3T3au2XOSGr3viSBy0rb-Tn0iACr822fwxM6bFpj5opiZwcZVxVgXwVAhC2gTuNFU1w2zWkWH-ehFgax2dMCuZtXp2CqgGs7hbXifPlP_8qh27v1g19UoZ88FniU48NJpYnuGXEj7NKCQ75E8ZWTaxlrc=)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGiONUHypIJzGxkRzPvLSaX9zrrW9hw5BYxYuHjh1EIGJs-lMKtc6QgsKGzM7yuBdFZl-mlYoq7OsZ327DX0dlZ5XZPpC3iwZ6MMp7tat5AuhVodZK0BU_zBA==)
33. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWLx-D8la9c4DbnN3TeD8ba2kY0mMI8RwYBRpbrs7bbGy6uSaiM5AxqpGtJqLXxr2uuAXWG9yZt46AevduaSG3DHxL27oN5GgmGlwjNC54PQwydvwvBCfxCXuVv2FkNV6N7pY79TN7xBb80eBSs_Q8Ezj6SM3oGUk-rmuG1VvQd457AZ87jNPfql9V3XgyvQTOsqaoy_YZhRYPQmsbjKOwFqPX6SMdYJzB2w==)
34. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSbX-R3V8j4FH1k0XAuSRPr1CKo22cuuz13qV6Dil-XeErIVf6S0D86zCPeY25Mci6LY3Plw1tlZ6eDVWXEmhtukZpXAU6Cj_IRkTeuC0TmI2W1-CA3W-SlXWaSItVvFTqid5P6K8ZLOMW-hMpvR1C9T_LqUVu8NvMOhjCNcMBMogXtQ==)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7kE30p7sSH2R_gG0aXBh-1rkKH7_U2BWFbYBtrjdkkZQwEMJq_VwOsz2t_WsTQOc8Bq-Mq-gAqucINHKd8W0Eg-jENAoX_q5SLc85Q-LTw-fapynSrg==)
36. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaENVQaNGpii7Hvgml71q4khvY10A3mHc6atYie5b2MQCU3vGoAZB_VHmXFl_qX8m1rJuQbcSMBi3msBLnU8LQuXdUfx8nB0a9q_ufswCWm7QzMVMpZlom8XaHazgSfgXh0CYQgd4FxjmbSS8gKdhO)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsCuHkM7gGQ8C9NgXthGWXyKC1WXVJmUpitNnbHCu94R0EPUV0FUnkjefgEDNwfFKCo2cCfcMSnuZhzsK0in9Oblrj-7lzEQ5CxOM3H-p2pNCAxMRBgBrKYg==)
38. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdNetIi0UDP2RCSt46zBgQOKkOgp_zTA24OdS1FDE3lSFKcHU2eiWg8mC0bdFcVOtbLyDQaNKaLyk28UOGzBBJqdpXlcFVCS4h_gDFeb0KXQ7ABXBTK2e3fnRcew9REWX1inopttEYDIWGeTWMOA==)
39. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlPyrnhDyRLi23tin40RlVSADLAAWf3A6TEBDQULTFVJkivT8luuY436DGx8nGOBCSE-LuaOt87grHQ00bgr4SPDX5h96X8PBxZjHuGljsO0jO3sQTxA==)
40. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1bet1Gbg5cJexOycEvIpkcae2wH1Yw4UBIjJKKPPiPkttDknpWiJbC-MteUSWI205-ceWHIjZh2doOP2XmeRIKpk5CoindCdhlxHa41Kq-eOnitZ9GE0zKJQX)
41. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGltyIQyeb8PdlO1I1Ye_z-dNlC0j-OysDAmncc8m4-h5uFtLTtK2LY9L4BgOJy1O-N6HCKA7CBb4b6PFQhRSyxoB6YuUmA8wdKGKQg3ZdCnux0H6a2BScERlRZ_p8NquQHKQ==)
42. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6fKd4npHHWz8KE61WAXcyYaYU9H3HQxPHixh0AoAyWDrNtKRw1_pElzgGdOi9qWonzQ7sDLgqmGG7p4_4XF1ngX8HE178jomvjVW5IuV4WgGbWNz0EiifewLRuF_xvQgB)
43. [cmu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOU8g43cNhxJwXR6fNAmjg_N-2v6OimW1dwONJVo-H64vJHktrB0rqnvFKHViUvZFepq7l81saPwksjNuXPuzvoE16Y6yWUvu06rlI9g5qm57fw8YLf2aXfbPWW53LeUoe7DrThyODNflO6_Z-QgoWcnTi)
44. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWGFi2YuCqaMbfkxtBgWe_uFVG0fi0yfPc_3-gXosFGwaQeDdbgvwjlh7X48VaUDnDtLkqbpU38h3aWqlKS14i3ph0OQ3w4mnBAfXtyoGFWUrnH5wdVQSvFg==)
45. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHllIFt6iirl0JIamcqi7Zwx0x_QGrf8uF-ll2DUCqEdQr6Yxb-EZDbJ67qnLjOLAF5W8127AbmHbKGAx34Xg00gtKwsCrWptI4gb6q6Kjojpp9hyioE_dhJ8RnDnXilbbDj8xZFCi4fgFCRvME-dYyNtc5__rIZCMhBiTFlGkNMJTpkN9DJ_QW0uZdyJl0U0iH4YJLNjfC9nKBZBMbrpcw)
46. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3SiRjXVDaNf8AXw08NY68Kj_3tF4JKFhERTYYkkpgV7aAZVTeONdHbOg8cwOE4NDz_ws64DWaVXoUlfMKiKuA_d3UtItKtn5hyafCmj-aCaDdyOcrC9uHiAdUwobXLQXS_hGfmQra6ivTwq5W4qbyltw=)
47. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGe_P9sqcbBpast_VzTQsAo6wN3f_mhIO9JjfnQ-G8d5c05R4uMQ9MQAlep6WiAVdXRikbD6H3oAStB50cqACM5x2jhC4FSDlZqgBtcipDbIET7PciO3mmWNXk7XG9ata9cnsrNkTs-P0UZyk5kv8hk5siio9tgHampHCv8CvSfiA9XgDINvDfgai84XZcsCfewQ37sbJ2rR60sgswM6GQR)
48. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYeOoACx5PlGtr3YGDy_3_soGpj62yrI4WKsup60NniXmD-mgN6Zjag5nC3WVgFgM_lfQ9JSVf6B_G2QxRrnO9wgF8RmdKC3wdTKEKxdR55-9rTOMgvw==)
49. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-dA_cLi5RWmBOufvKIqkFJqlm3T3-qLTHrLisCm4gJ8_CT5gMhxA042vxGmji3OkpJlTOCBcU0h_HuOUXMWLW-rtcAfb-RO1DI-WhZTrfsNnNPefPQA==)
50. [aitp-conference.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcAnE9i3eG0LBemNWe_FAiVPtQU1iqv56ZEmZ0__nraYF0xC8C5GPgdy3ifWDdUEtUAT8omVBK7ZjMxEIExNv554hkyNZgZ63Io5hWQGknIDWquROhOIOVpD9_U3XXrj_vnAXBKoeV5y0P)
51. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWezUkMrmnSM_wpQw0u5dsWefSC0y8WbUTnbns8wadMxbnEzWyGKLFJD8BgqwTO7cAYG933rQWAbHs79Kl0HT_U5g0pBR0GFrwG3-VtoJzGQxXq86UBujFXLB9Jjvg-zqMLVkksBfXBsCgXdVv0vQnr0Az1gJFrowqljg=)
52. [stephenwolfram.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZ7_t03a0wgG2wzbbaRpEtk-l2HI2QfcVjDiD7pR_QD7DrH7Xw1Nliw4bt8IHYcIC6BIQAgknkMvTMjLgwxn632GtWHvD8N__--U6re71XVJZPio8mePD6u8_Ep6MC3ojS2iaMYDb0DEky-AjYY0Vi-xSphOIb066O1NBUWTqo9WWjpJ7fBwTJMN6nNsDe4nfpVdI9r4Ijnjyn3DM7xQRdLjJVy-woOb0S9AkoALAtdg==)
53. [dokumen.pub](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYRQCjABRfa63TtyYIVk4D_3rUz25R-0tuvGEqWd6dW_3j8TFTudTi03brcwbg7sHc0JBJQcpEczV9MMn1mlThI8X68eB0csmkgSsp8H8D1YUOzmchHWbkiEfrTV9B7jyTT03-Zfln_K2d8yoO5kxP05rmxkpoLB7J2wnzXmXiXrsixHm0rKF87QWZzV7BGWNxBi9eYlo0-JvZaxKmhgEaudq2SY7zRBBs_4IyUEVC2mDGdWO5bJsl3LEHjHOkr_c3BhY=)
54. [vdoc.pub](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfr80w7oTh_Uvx96-CeDDtIfBbW69PoP3lvM6aYIQ7d9TBFNXFZbqA_YNFfPYyM69zZqgJRdLK8owRYA9rCU2-E5f90uMuJaJA4S0kkFWXOq2HEcUM1L4cS2P-vea6amLD3z_XM-U3uKb9eZoRYAdsmsaMONxSd_gvj5NlNd4-DHC6Rg==)
55. [tudelft.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFt0lVmAnPfeT_m2efBiPNcOlfzYbUkeZ-8reWIkqmLtfNfxLxErXR1d8OCCBlN8WB8NF6e34PVe4xHqdafWMxiZBYvnbl96SYD4wAUqAOg7oGWbSYpS3NgoTZqXvKORcEixj_L9pwUaEo6c9mba2psS6xst5pzNRkJss8dnr80YlDT)
56. [uzh.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmYESkdMMcvvUUUum9Yofjq1IUwVPWvMSNSV1_24LuDPwJ9OZUIeypibZ6PrXrHzrEUYbC_y7hrHJ7wPXTqCM2eRc7j2hNXzty3eNzJxoDD_tBqhnqWVaUkMteAROozTPThlBHY3il3jUce-6jgn4=)
57. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGiBbbNEd5UQ3B4xai0mBieGgvN9Vjt4YT5nY6gEoh6qQ3qXo9H4PyMTsh0S2yrRcuXqV3QHiF2H8loRHoQ2mxxVAk3HFop1g60LGX92ejhh_GWlp1OXmZd2ltCR34idC47CmAiYXDsMsfq-EzCfRb19OGLcyjgMf3mDIJyuwE-wOztfd0P1BX_aTrTTQnUy37EtAFomHGPYsek8lFSeMp6Ff2yhkwfvFvuBuA=)
58. [neiger.science](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGM0wy6VALTcGatx6Xi7LMrgX4QZOC_rW_n4PP6VcY-cqHgRR-r_H08i1dk5LKkRxg7uhCavC_0GY9y6XFq3JMugIOdvjT2MS0GJurFNASxzNLBJNCsqzjAmf-dNr6e)
59. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGH5iGhR-6PJQbz8v7AUusoxJCDu3pj0uVpU-yD_2Mb1zepfLivEZAELi409whjUBP3naVhbm2HixgY9mn9g8cUvkHcvS5bnVbTXfOfB7ApA6Qz0S5waBPdLHNVTStRQiFsEVUMOGanYgsd1uWd)
60. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKo2df7elZyM6ILb92MO26Wq8HeS8-Jz34irqtqeCBnplcKe4rrn0AIL53mBY36q9yvB6on2VbwvencDrSJaRQUqjRyk_1Fr-IP1mx_6uwIXmnGr5JIR_DcRMM_LV1SwokqerGZ7D2m312vh9m9hX615cKdEAfDalv7Dl6GDgy7VFj4kxd_DYw9oNTAtRdnEspuQnNHaf8QiSF96lany6PGvRTUOMRAfqEV4g7cP3TEyPhIdXoesw=)
61. [soton.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmluMnIcIW0thEZzffYBte2wXLydU6hxxo0WPsFcRdlG3vQJWGG7-Adj8k9w9KCXCSgg9NRIxZKmKKnqkMpgMbc0XO4MNCfQx4otsjWF_He_wjzybrEyMKTEVDPACTHLv9ErYbL8TwF0JUnDN8NnxQ)
62. [rwth-aachen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOTcS_iEr5oiUYykiOtUZQp_cvMJ80Hawq0dQCEmLtM7AqjvyWec6jNK2NOE65U_S-ilirvncGiCnHgMhDE5Ung83OYu611PvKW2yKl7KQZu9bM68lJh6zPepjdg5YnCImw7w3CIiKgo3q7DGIpex6oazmuDLFyYhSYPOosGeL_wfC8FZhXryuCzvVW9Z1QBTrub5ViKGFL4qO)
63. [piedeleu.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSFlW7tn4ltgALbQROvqpceDxvZ9q0kFTEq5EuX01JxPoTjtilx1i7UKu0HHQ3UxFgbDjfalEzYnTfrVkjdJkWdSiPrR-fU4sFV8caTb4wmORUQMp9sxNDMMoYI-pJSVuang7MLSEDbQ==)
64. [inria.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEm5K73lhEcQHTY6MHZu6i8dCQwlPdBz_wNzXjOUmInHE7D813jkTfft_POE7tS8M2pI0iNgVQDPz07KxagumgajjGV4i6TcDgiU6glZXEgsZMDlMeQ5EcnsMuM5C0DbZDXxZc0_a0CuvqN4NCM6wrLiHhQkTB3nFV3F7Y9Z6kFkg==)
65. [polytechnique.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwE8C2KChw-I2CnhsukyxD8zypSaaE0MUu6z9gZe-kLGmjZt6TaW1nQ78tb_XHvdio3U009wKrlulcLwb-zDQGfrE5UBBVX-PKh5JK0sfQa2xb7NOtAynKV2HEgqGwLgOv6DTXy6CH0BhxeXyL-tsSODtklQqEvnYqwb3xbR6uKQ==)
66. [kyoto-u.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHY3zmuZKX_DvER5rn77h0Ar8kkreed7ct9HC3cX6e6Tg2atGEfREmeR82-rmb3nGa4_VmrWUy2KD7GsT7T9Gr7ypVr3JA7j_JRyZmd439iur0m8WgWO9-mhi8T4mrUKx2v51qcyzDYoywviewI_Q==)
67. [mta.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtpstrOX8F8-6xtq9Ob3NtCRzfzbnCZikizttIHGCR6VJg4-GoXmYb5UpD6BGmSwfY_FYGg-SI__dm_8jCWn5BIHr2mQuV0L-OuN7Zojk1As0bROxHnzfsY7dSNl2jz9khY-E=)
68. [gebner.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcgtoUWwoYGVB44IrytsOj1LZ7vcqQJSc3pb5QflUfVq2aidRdfdBn8r7-4QUDYMNUa4L5aWv8nn_yXer8FFOD_-NeFp2luhlns9sUHzQdAOXerJToQT59hqLpODFCCaoW)
69. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAn6mD4fnOSp50hK6C59elom3aYubMTdizw7gfJ3S9uGYItOT2eOPbZQehwwzCYrxKn7MJP_CVFf2uqgaNCAEFOO63K3FqCEECTpjz9u_3T0kW-SKAMWS7pl5oMDAVknGQ)
70. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGx1z4x2o9Z3PL4c0oeNF_qj_eNO5eXrgKORTYzRi0JefGLirYjqpm6MxcoKCi1XQRNjmOuphrzwFxnLW1gm9UvBda0TrmpEKep5KPBz48IjK-quW_wWasxKO_wQE-fBbO7J7II0y6KWsdp30ebkiKq3JIolS0ZMRVDH5-djJ-P8oqL-1t8XqN_Arscxb6-RvZ_4Y92f7Q8E9zsx9r0_dEYbTi4LySwUzcqtIoMu2qkfjrY7JQSN8BFro9ynVbIkr8uejx3noA=)
71. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5iOHIPL8-ovoXRLgE3IJlbQuEVmpWP__FpmpmML2PYYfRfzAmesH88Cv19noQwZChKZUoXKgi93iVLeBuZL3xS6sKyZm1NnXLUQz1fOAN4uPjCahNOg==)
72. [aitp-conference.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEd4pBDLFISoJjvIF1RwfNbMvf-PfJvXaR_YIJdxTJp2U4U5SdfR07XgZbTaSoWecGbZ-3phrbThokxLG9013a_-7R0u9cCapeGZz-1LFURuJieHUh_qTKBDrwi-FgW3nsUM5kO)
73. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSqd5C8AA6UNnXF5o-tttvp-B6ExF1jB0BmPO4mIqikUb38rYpt8lc2lFn8I-c6awMwr6heZM2895j6Kxd5r5sBMTmECf6E7PeALdgSvCutiUsX8FordcuOPfeFWKPbxkrJ6VlVNwVRgk41Q==)
74. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFl4zj0u_LFPYEWoLCDnAfwEZwDGlRSMrQVjJW4f-yVLdzN_0eTjHIASmNTxGBLe_ZnzlkILkCq5tmKbyDbi_nji9YVHcO9imUAslPiSdNsE8mS7uZcdEuVg-9ev20rpjlX_miQ)
75. [julian.ac](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6BD8YfPMG4DXCkcZwTjvp8H6CHRuHp9MXfrbNdbUAMPd5sHPlt7EXSiSZM8R1Qrg2CpAo0guqS3XF14CY2WQ5oTMCyKrXlNour5Mgnq0Ti6n7Ss9VDiRTha5kO_HNKYxD4kgj-8mV_yS27JgS)
76. [tomzahavy.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELtLQSHBnqQhVM6cQB7dtPsrkd7f0HJVbxUJvBL0lqiFALND2wjRRuhb__VW1IS6gpDoRRO5O5MclEE-dFsN5B7EBr0GUo34bYFLPqSDyIMW4y6VTvycJXi1HdpNXrX-63b6XD0KjonmogfbGSRbRvWZ-SJj-USg0_PSZ5Q_lKvJw6IQ2-1s2HlL1Gl_ezmQ==)
77. [virginia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhRxz4-imN2AxntLRwQSFvaA5kLKe_nPuhCOC59soeORkQNBQOtzbcyGXbTntA5O2EY_czW49uWXR80VMHZxAQrSHRjAz4xkQnD77rM2_08QISmH-vnF1TbII5iml5jOhbmLt8732Sj0yYx5079gLnvgKZqufMFCDC7-7WNQ2NQgPYXHZ26CiiCoGkh-UkXMT_tmYG1iN6ioeBfDTLBP0EUivOLfB7W1ZGkLTy_iYWoJoxwq26_Km9L97wIUua45BMBBp0y7Cl)
78. [ulam.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1Y8RzI4TSe6AqRap9L1gmkIwGGxLrmu2LMStPUmoP9rYxHYcly0PL_KPeLhn66InmvuZyQ0p2z6AZfH7xWo7Qynmvd52zQOSyjRwPztcbu9HfCQLcz_Q=)
79. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNvQiRv2ZgalCOYvJvp_xGeoRh_0ARXv4eojMf-ZN5pGAa1OgvyhJe29DcKn2SpsSPfPlBj6z_58j66-tgVhreZI0sgAAi_IiSj9NnqYBjcDottvu8B12UOw==)

