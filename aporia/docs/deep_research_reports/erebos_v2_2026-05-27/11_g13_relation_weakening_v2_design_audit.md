# Prompt 11: G13 Relation-Weakening — v2 design audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdVWVVXYXBiVE1MX2pfdU1Qc3RxcDBBYxIXVVlVV2FwYlRNTF9qX3VNUHN0cXAwQWM
**Elapsed:** 304s

---

# G13 Relation-Weakening: A Comprehensive Framework for Predicate Lattice Transformations, Semantic Relaxation, and Proof Mining

**Key Points:**
*   **Semantic Over Syntactic:** Recent advances indicate that syntactic regex-based predicate relaxation is fundamentally brittle; semantic weakening utilizing formal predicate lattices provides rigorous, mathematically sound transformations [cite: 1].
*   **Predicate Lattices:** State-of-the-art frameworks from 2024 to 2026, such as Open Cylindrical Algebraic Decomposition (Open CAD), Abstract Interpretation models, and Layered Modal Logics, formalize the "one step weaker" traversal on logical structures [cite: 2, 3, 4].
*   **Taxonomy of Weakening:** Not all predicates are amenable to relaxation. While quantitative bounds and universal quantifiers natively support gradual relaxation, highly rigid properties (e.g., parity, primality) demonstrate strong resistance to meaningful weakening.
*   **Integration with Proof Mining:** The Kohlenbach-school of proof mining perfectly mirrors the G13 objective by extracting quantitative bounds from non-constructive proofs through the systematic relaxation of logical operators [cite: 5].
*   **The Triviality Risk:** Weakening a claim frequently collapses its truth value to a degenerate or tautological state. Implementing stringent threshold criteria for "informative weakening" is necessary to preserve the utility of the generated hypotheses [cite: 1].

**Introduction to G13 Relation-Weakening**
Automated theorem discovery and claim generation heavily rely on structural mutations of existing knowledge. The G13 RELATION-WEAKENING plugin operates as a sister module to G03, shifting focus from arithmetic operators to *logical predicates*. By walking predicate-strength one step down a lattice (e.g., strict equality $\to$ inequality; universal $\to$ existential), G13 aims to discover novel, verifiable lemmas or relax overly constrained conjectures. 

**Relevance to Automated Reasoning**
The transition from v1 (syntactic mutation) to v2 (semantic mutation) represents a critical evolution. Semantic weakening ensures that the logical implications of the transformation are rigorously maintained within a specific formal framework, minimizing the production of nonsensical or mathematically invalid claims.

**Caveats on Semantic Relaxation**
While semantic weakening is highly powerful, it inherently risks the generation of degenerate truths. Evidence suggests that without proper bounding and domain constraints, weakened claims often survive evaluation simply because they have collapsed into triviality. The academic consensus leans toward employing structured verification pipelines to filter these degenerate cases, balancing exploratory freedom with mathematical rigor.

---

## 1. Predicate-Lattice Literature (2024-2026)

The conceptual core of the G13 plugin is the `_predicate_lattice`, a structure that maps the relative logical strength of various mathematical statements. Between 2024 and 2026, the mathematical logic and computer algebra communities published several frameworks that explicitly model this "one step weaker" notion across different domains. We survey three primary frameworks that seamlessly map onto G13's theoretical foundation.

### 1.1. Cylindrical Algebraic Decomposition (CAD) for Real-Closed Fields
Cylindrical Algebraic Decomposition (CAD) is a foundational algorithm in symbolic computation for studying real semi-algebraic sets, decomposing $n$-dimensional real space into connected, sign-invariant cells [cite: 3]. Historically, CAD has been utilized for real quantifier elimination. Recent implementations, specifically those documented in 2024 and 2025 by Lee, del Río, and Rahkooy in the `CylindricalAlgebraicDecomposition` package for Macaulay2, introduced the concept of **Open CAD** [cite: 3]. 

Open CAD restricts the decomposition to full-dimensional cells, designed specifically to solve existential problems involving *strict inequalities* [cite: 3]. In the context of G13, Open CAD provides a precise, geometric predicate lattice. 
*   **The "One Step Weaker" Mapping:** In CAD, a predicate enforcing strict equality (a lower-dimensional algebraic variety) can be weakened one step by relaxing it to a non-strict inequality, and further to a strict inequality. Geometrically, this corresponds to expanding a condition constrained to a $k$-dimensional boundary cell to the $(k+1)$-dimensional full-dimensional cell (Open CAD) adjacent to it. CAD algebraically codifies the step from $f(x) = 0 \to f(x) \le 0$ as a well-defined lattice operation on the sign-invariant regions [cite: 3].

### 1.2. Abstract Interpretation Lattices
Abstract interpretation provides a unified lattice model for the static analysis of program semantics and logical properties [cite: 4]. In abstract interpretation, logical predicates defining program states are mapped into a complete lattice $(L, \sqsubseteq, \sqcup, \sqcap, \bot, \top)$. A 2025 framework by Ranzato explicitly models "Best Correct Approximations" within these complete lattices, parameterized by an abstract domain $A$ [cite: 4]. Similarly, Baldan et al. (2025) formalize model checking as an instance of abstract interpretation where state partitioning abstractions evaluate property-preserving state relations [cite: 6].

*   **The "One Step Weaker" Mapping:** In this framework, predicate strength is directly analogous to lattice height. If a claim is evaluated against a predicate $P_1$, walking "one step weaker" implies applying an abstraction function (or upper bound operation $\sqcup$) to move to $P_2$ where $P_1 \sqsubseteq P_2$. For instance, moving from a specific set of integer solutions to an interval abstraction, or applying a widening operator, represents a mathematically proven "one step weaker" relaxation of the logical predicate bounding a variable [cite: 4, 6].

### 1.3. Stratified and Layered Modal Logic Strength Orderings
Modal logic has traditionally organized systems by strength (e.g., K $\subset$ T $\subset$ S4 $\subset$ S5). However, modern approaches in 2024 and 2025 have formalized this via *Layered Accessibility* and *Stratified Modal Logic*. A 2025 study on stratified modal frameworks abandons a uniform accessibility relation in favor of relations indexed by levels of ontological admissibility, denoted as $R_\alpha$ for $\alpha \in I$ [cite: 2]. Similarly, 2024 work by Glazier on "Contingentism" explores the logic of actuality, mapping iterated modalities into a strict hierarchy of logical strength [cite: 7].

*   **The "One Step Weaker" Mapping:** Under the layered accessibility framework, an operator $\Box_\alpha \phi$ signifies that $\phi$ holds under a very strict regime of structural constraints [cite: 2]. A "one step weaker" transformation in G13 directly corresponds to reducing the index $\alpha \to \beta$ (where $\beta < \alpha$), thus modifying the accessibility relation to permit more flexible transitions. Syntactically, this translates to weakening $\Box \phi \to \Diamond \phi$, or relaxing an absolute metaphysical necessity to a nomological necessity [cite: 2, 7].

---

## 2. Semantic vs. Syntactic Weakening

The current implementation of G13 relies on syntactic weakening—utilizing regular expressions to execute string replacements on claim text (e.g., replacing `<` with `<=`). While computationally inexpensive, this approach is fundamentally brittle. It fails to account for the mathematical context, often resulting in syntax errors, scope violations, or logically malformed propositions. Semantic weakening operates on the underlying formal representation of the claim, ensuring the relaxed predicate maintains well-formedness.

We propose three distinct methodologies for implementing semantic weakening, backed by 2024-2026 literature.

### 2.1. Model-Checking-Based Semantic Weakening
In combinatorial optimization and propositional proof systems, semantic weakening is heavily utilized to evaluate search problems. Recent literature on the complexity of Total Function Nondeterministic Polynomial (TFNP) and Total Function Polynomial Hierarchy (TFPH) problems highlights how search problems are verified via semantic weakening in Cook-Reckhow proof systems [cite: 8]. Furthermore, Danner (2026) formalizes semantic weakening rules within XOR-OR-AND normal forms for conflict-driven SAT solving [cite: 9]. 

**Methodology:**
1.  **State Space Formulation:** The logical claim is encoded as a Boolean satisfiability problem or a transition system for a bounded model checker (BMC).
2.  **Semantic Implication Testing:** Instead of altering text, the model checker identifies a target constraint clause $C$. It then queries the underlying engine for a clause $D$ such that $C \models D$ (i.e., $D$ is semantically implied by $C$, making $D$ strictly weaker) [cite: 8, 10].
3.  **Validation:** The BMC verifies that the state space permitted by $D$ is a strict superset of $C$, and importantly, does not encompass the entire universal set (preventing triviality).

### 2.2. Abstract-Interpretation-Based Weakening
As defined by Cousot's foundational theories and modernized in 2025/2026 literature [cite: 4, 11, 12], abstract interpretation utilizes a Galois connection $(\alpha, \gamma)$ between a concrete domain $C$ and an abstract domain $A$. 

**Methodology:**
1.  **Parsing to Abstract Syntax Tree (AST):** The predicate is parsed into an AST. Variables and relations are mapped to a concrete semantics domain $C$.
2.  **Galois Connection Relaxation:** The G13 plugin applies the abstraction function $\alpha$ to a sub-predicate, mapping it into a chosen abstract lattice $A$ (e.g., the lattice of intervals, or the lattice of polyhedra). 
3.  **Lattice Traversal:** The plugin computes the least upper bound (LUB) or applies a widening operator to move precisely one step up the abstract lattice [cite: 6, 11]. The resulting abstract element is concretized via $\gamma$ back into a logical formula. Because $\gamma(\alpha(x)) \supseteq x$, the new semantic predicate is guaranteed to be a sound weakening of the original.

### 2.3. Theorem-Proving-Tactic/SMT-Based Weakening
Modern SMT solvers (like Z3) and interactive theorem provers (Lean, Coq) employ sophisticated semantic representations. A 2026 framework for Dependent Effect Systems integrates categorical semantics with SMT solvers like Z3, highlighting how effects dependent on program values can be analyzed and semantically weakened via typing environments [cite: 13, 14]. Additionally, the "First Proof" benchmark (Abouzaid et al., 2026) defines semantic weakening explicitly in the context of Large Language Models and formal theorem proving: *"A statement that is plausible but strictly weaker than the theorem's conclusion, e.g., dropping a uniformity requirement or restricting the domain"* [cite: 1].

**Methodology:**
1.  **SMT Encoding:** The theorem statement is converted into SMT-LIB format.
2.  **Tactic Application:** G13 utilizes predefined SMT tactic combinators. For instance, a tactic can isolate a universally quantified variable $\forall x \in X, P(x)$. The tactic semantically injects a sub-domain restriction $\forall x \in Y \subset X, P(x)$ or relaxes the quantifier to an existential one $\exists x \in X, P(x)$.
3.  **Z3 Verification:** Z3 is queried to prove that `Original => Weakened` is `SAT`, and `Weakened => Original` is `UNSAT` (ensuring it is *strictly* weaker and not an equivalent formulation) [cite: 13].

---

## 3. The Weakening-Targets Problem

Not all predicates are structurally suited for relation-weakening. Applying G13 universally results in absurdities (e.g., trying to "weaken" the property of a number being prime). We propose a taxonomy dividing mathematical predicates into **Weakening-Natural** and **Weakening-Resistant** categories.

### 3.1. Taxonomy of Predicates

| Category | Sub-type | Original Predicate | Weakened Predicate | Rationale for Weakening |
| :--- | :--- | :--- | :--- | :--- |
| **Weakening-Natural** | **Quantitative Bounds** | $\sum_{i=1}^n x_i = k$ | $\sum_{i=1}^n x_i \le k$ | The transition from strict equality to bounding maintains meaningful constraint while expanding the solution space. |
| **Weakening-Natural** | **Quantifier Scope** | $\forall x \in \mathbb{R}, P(x)$ | $\forall x \in \mathbb{Z}, P(x)$ | Restricting the domain of a universal quantifier is a classic semantic weakening tactic heavily used in analysis [cite: 1]. |
| **Weakening-Natural** | **Topological/Analytic** | $f(x)$ is uniformly continuous | $f(x)$ is pointwise continuous | Drops a global uniformity requirement to a local one. Deeply rooted in real analysis theorems. |
| **Weakening-Natural** | **Set Theoretic** | $A = B$ | $A \subseteq B$ | Relaxes strict equivalence to inclusion, a fundamental operation in lattice theory. |
| **Weakening-Resistant** | **Binary Categorical** | $n$ is a prime number | $n$ is an odd number? (Ill-defined) | Primality has no adjacent structural weakening that preserves the combinatorial intent of the theorem. |
| **Weakening-Resistant** | **Rigid Symmetries** | String $S$ is a palindrome | ? | Palindromic structure is all-or-nothing. Removing the constraint on a single index destroys the fundamental property. |
| **Weakening-Resistant** | **Graph Isomorphism** | Graph $G \cong H$ | Graph $G$ is homomorphic to $H$ | While technically a weakening, homomorphism often collapses the target problem entirely, rendering it trivial in many graph theory contexts. |

### 3.2. Structural Indicators of Resistance
Weakening-resistant predicates generally possess one or more of the following characteristics:
1.  **Indivisible Spectra:** They operate in discrete spaces where intermediate states do not exist (e.g., parity).
2.  **Global Rigidity:** The property requires the synchronized participation of all elements (e.g., perfect matchings in bipartite graphs).
3.  **Non-Archimedean Nature:** They do not admit a metric of "closeness" or "degree" (unlike arithmetic bounds which exist on a continuum).

---

## 4. v2 LOADER DESIGN

To transition G13 from a syntactic regex toy to a robust semantic analysis tool, we specify the architecture for **G13 v2**. This loader integrates formal SMT solvers, specialized mathematical contexts, and advanced kill patterns.

### 4.1. Semantic Weakening via SMT Solver (Z3)
The v2 loader requires a bidirectional translation layer between natural mathematical language (or intermediate representations like Lean/Isabelle) and SMT-LIB syntax.

**Workflow:**
1.  **Input Parsing:** The claim is ingested and parsed into an abstract syntactic and semantic representation.
2.  **Target Identification:** The loader traverses the AST to locate nodes categorized as "Weakening-Natural" (e.g., `<, =, \forall, \subset`).
3.  **Mutation via Z3:** For a identified node $N$, the loader proposes a mutation $N'$. It queries Z3 with the assertion:
    ```smt
    (assert (and (=> N N') (not (=> N' N))))
    (check-sat)
    ```
    If Z3 returns `sat`, the transformation is mathematically confirmed as a *strict semantic weakening* [cite: 13, 14].
4.  **Reconstruction:** The SMT-validated weakened predicate is translated back into the host language.

### 4.2. Mahler-Context Loader (Lehmer's Bound -> Mossinghoff)
To demonstrate G13 v2 in a highly non-trivial domain, we specify a loader for the **Mahler Measure** context, specifically targeting Lehmer's conjecture.

**Context:**
Lehmer's conjecture posits that there exists a universal constant $\mu > 1$ such that for any non-cyclotomic polynomial $P(x) \in \mathbb{Z}[x]$, the Mahler measure satisfies $M(P) \ge \mu$. The lowest known value is Lehmer's bound, $M(P) \approx 1.17628$, achieved by a degree-10 polynomial. Michael Mossinghoff maintains extensive lists of polynomials with very small Mahler measures.

**G13 v2 Operation:**
1.  *Initial Claim:* "For all non-cyclotomic $P(x)$, $M(P) \ge 1.17628$."
2.  *Weakening Application:* G13 semantically relaxes the universal quantifier to a bounded degree subset, or relaxes the strict absolute bound to an asymptotic one.
    *   *Weakened Claim 1:* "For all non-cyclotomic $P(x)$ with $\text{deg}(P) \le 100$, $M(P) \ge 1.17628$."
    *   *Weakened Claim 2:* "There exists $\epsilon > 0$ such that for all $P(x)$, $M(P) \ge 1 + \epsilon$."
3.  *Re-Testing on Mossinghoff Data:* The loader automatically queries the weakened claims against Mossinghoff's database of polynomials. If a polynomial with degree $> 100$ is found with a lower measure, the original claim might fall, but *Weakened Claim 1* survives.

### 4.3. New Kill Patterns
To manage the influx of uninformative mutations, v2 introduces two new `kill_patterns`:

1.  `predicate_unrelaxable`: Triggered during the SMT phase. If Z3 determines that all proposed weakenings of a node either yield an equivalent formula (bidirectional implication) or an unsatisfiable branch, the predicate is flagged as structurally rigid and the mutation is aborted.
2.  `weakened_form_trivial_on_target`: Triggered during the evaluation phase. If the weakened predicate resolves to `True` for *every* element in the test domain (e.g., relaxing $x < 5 \to x < \infty$), it is mathematically degenerate. The loader calculates the variance of the truth values across the test suite; zero variance on a previously restrictive predicate kills the claim.

---

## 5. Interaction with Proof Mining

Proof mining, pioneered by Georg Kreisel and brought to maturity in the 1990s by the school of Ulrich Kohlenbach, is a subfield of mathematical logic. It focuses on the extraction of computational content—specifically quantitative bounds—from prima facie non-constructive mathematical proofs [cite: 15, 16, 17]. Proof mining extensively utilizes techniques such as functional interpretations (e.g., Gödel’s Dialectica interpretation) and majorizability.

Recent advancements in 2024 and 2025 by researchers such as Neri and Pischke have extended Kohlenbach's framework into probability theory and functional analysis, extracting quantitative strong laws of large numbers and metastable convergence bounds [cite: 5, 17, 18].

### 5.1. The Direct Interaction Pipeline
G13's weakening ladder echoes the very foundations of proof mining. Proof mining often operates by relaxing a strict universal quantifier (e.g., the standard Cauchy definition of convergence, which is $\forall \epsilon > 0, \exists N, \forall m,n \ge N$) into a bounded, quantitative form (e.g., Tao's metastable convergence: $\forall \epsilon > 0, \forall f, \exists N, \forall m,n \in [N, f(N)]$). 

We propose a direct, automated interaction between G13 and Proof Mining tactics:

1.  **Identification of Ineffective Claims:** G13 analyzes a qualitative theorem (e.g., "Sequence $x_n$ converges to $x^*$"). This is a highly restrictive, often non-computable predicate due to alternating $\forall \exists \forall$ quantifiers.
2.  **Logical Relaxation (G13):** G13 semantically weakens the predicate. It drops the unbounded universal quantifier requirement, transforming $\forall m \ge N$ to a bounded interval $\forall m \in [N, \Phi(N)]$, generating a weakened, *finitary* claim [cite: 5].
3.  **Routing to Proof-Mining Tactics:** The weakened claim is routed through a functional interpretation module (similar to Lean's `Dialectica` tactics). Because G13 has pre-relaxed the predicate into a computationally tame structure, the proof-mining module can successfully extract the witness bounding function $\Phi$.
4.  **Output Generation:** The system outputs a quantitative version of the theorem, providing explicit rates of convergence or metastability [cite: 16, 17]. G13 acts as the *heuristic surface* that prepares logical structures for the *rigorous depth* of Kohlenbach proof mining.

---

## 6. Contrarian: Weakening is Usually Useless

To rigorously evaluate the G13 plugin, we must steelman the contrarian perspective: **Semantic and syntactic weakening of relational structures is usually useless because the resulting claims rarely achieve substrate-grade importance, frequently collapsing into degenerate truth values.**

### 6.1. The Argument for Degeneracy
When a mathematician formulates a theorem, the predicates are finely tuned to exist precisely at the boundary of truth and falsehood, capturing deep structural invariants. If we arbitrarily take a predicate like $f(x) < g(x)$ and weaken it via G13 to $f(x) \le g(x)$, what have we achieved? 
If the original claim was true, the weakened claim is trivially true. If the original claim was false because $f(x)$ occasionally equals $g(x)$, the weakened claim might become true, but it loses its analytic bite. More egregiously, weakening a universal quantifier ($\forall x, P(x)$) to an existential one ($\exists x, P(x)$) over an infinite domain like the real numbers is practically guaranteed to return `True` for any non-contradictory predicate $P$. 

As noted in discussions regarding the "First Proof" benchmark and mathematical olympiad evaluations by Abouzaid et al. (2026), AI models frequently exploit semantically weakened statements because they are overwhelmingly plausible but mathematically uninteresting [cite: 1]. A weakened claim usually has degenerate truth values—it is a trivial superset of the original. The survival of a weakened claim is not evidence of a novel discovery; it is merely an artifact of reducing constraints until the statement becomes a tautology. 

### 6.2. Threshold Criteria for "Informative Weakening"
To counter this degeneracy, G13 v2 must implement strict threshold criteria. A weakening is only deemed "informative" if it satisfies the following constraints:

1.  **Non-Triviality Measure (Model Elimination):** Let $M$ be the set of all possible models/instances in the domain. Let $S_{orig}$ be the subset satisfying the original predicate, and $S_{weak}$ be the subset satisfying the weakened predicate. An informative weakening requires that $S_{weak} \subset M$ strictly. If $S_{weak} = M$ (the predicate admits all models), the weakening is degenerate and must be killed via the `weakened_form_trivial_on_target` pattern.
2.  **Boundary Proximity (Information Theoretic):** The information loss between the original and weakened claim must be bounded. This can be quantified by the probability of the claim being true over a randomized test suite. If the original claim has a 10% pass rate, a weakening that jumps to a 99.9% pass rate is likely useless. An informative weakening should target a modest survival rate increase (e.g., 10% $\to$ 25%), indicating it has relaxed a specific constraint without abandoning the core structural geometry of the problem.
3.  **Proof-Theoretic Tameness:** As derived from Kohlenbach's framework, a useful weakening must transition a claim from a non-computable class to a computable one, or from a high-complexity class to a lower one (e.g., $\Pi_3^0 \to \Pi_2^0$) [cite: 5, 15]. If the weakening does not change the arithmetic hierarchy of the statement, its utility as a logical bridge is minimal.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPDBUgW3nzcW1GUkXE8ZUMgONsKP_rUKjOnJNGy-RY5BBf4o6X7jixQAHDm4jWnIYVqewOUk3G8bDTV_1IRljlH-Kic7XGZ-gmmBqeFJCGCbBPX947PRjp0w==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDPFR5ukciMedyVHi8iVkpeS5ygsOZhdjnopSXBFJUL6Ti1PyyHtizNTYvKY00ovcm_a_xigSL6SBxQkU3r0qh19xcVQIqYof4C0lq9FbO3Tztu1eUa_c=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkehmPGn2hJ_GwFvZVKjkyMKJk-ZPQ0O-UJTcg-fREKPiYbFnweEzRf6OT_C30hHtLgVifk_Dp_AHKD8-pOOWQnBummo0jgC0gA8wtliNK5apnzDKGbjG3iQ==)
4. [unipd.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAlpEqjFBjgVJuFpqRfCWqC30h3P6B6dn-CVkAmr_LrVTDTJ4Jc87tPUvSCYKDzCVg0d47YfsznGCs7inleDk--VfHUfBpCTqF4cZFSbnhPXq4jfivXc6n3-P1IpclJMI24nqdZiK_dkwzjrU=)
5. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIG9d7pW8Z3o6ZoNg81PlkQ5RZJXGptaLwpuo1pyDnrOWAfheVqI1ZKKun12PW8ZX5huRH2XBAW5XaYmVwYJ-MnVOqC54ey8L2Rrh2bdB2VK1uhhtL6mVzsaUkzp-BLjoqcSnG17J4_g-JevGWDXEQ1kaHfaCM_27my1yGZLyUIsvInakSeIiwLBSMSY70a077QML2jEDBJ--RcE7-jrMcdaNmdXBvC3rO4ILwWKEFBT-JKt6rCjfYM34Aatxptpn6xrQdfeg=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFM0tth-lwDweRyo0iDBA8jRURweePwyEsys1-GpGgziq5evhof77C3z8U1FNXutBlOkmtQI7Fbd5tRqkwQFB-oQi38K_1eyvtjEK0p5Z4XesHaedd8tQ==)
7. [umich.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6ORpZWZtoEu8zT4G5sZmaqnhSXaRT2NiwgWuEL2dZcpSy1Xfo0bwXbUMDPGWTxsqw0nbel8aV9lL0P_F_16Uv3ueBslFse01obLnciN0r88fSafgnNZgMJJqh7p-qAZiCmGETeUbg6wNqytdCrFN9ew==)
8. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE10DIZaXF1MdYV3inxKGj4ytBdnIkxh7w-m6bUOxgCZPGK4YWx5bJnCT0ApAlM7e57FFfY3gYMuuvWFAbKnoZW8iW8m747C5hKL439jEWgE_8M__2VGvnjIXjZo3QfN6ZoxfHyVVdj)
9. [kobv.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzJtOWRp-HeIKnUfKLHIMMNxaTFS_dT26w0FnGbivdiEBzyrdLBQp-l2df_cHLZbWkxcgDHQ0x1oc_JkIB2QENG5oHZ_bSEbTIJf1_ZPSZXqLQ7VkNMSfNHifiHiIo9-3OyaxwKHxUqCPJMEjYapnVDqoiIBa3JnzKhIcEWLh8gIRwy_wCMOhgkddmYWgqXxma6WaoYpA708U0ZlQ=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDFaWU8Y610C1oG0PnPqDcDJWX8cgxPGK3rz7VmlMJUtquz1WmDlvWxuBncFdeFFqQ3JDgf2Bx5dWruJ3JGyLLZRp0Gr-ZcE6QIX6AL1oIqIKQ1IUHLA==)
11. [normalesup.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGy6CDjtOQKfxSvd5rNQso2Wy6BU_B8XS0WJAaHzC4iLmCc-y4g6zXOAnew5ahZIZGwbUFsShDXVNeDozJccg5AF_2LG0yv7O8zmYtWAkFK_R5KSIpIU7visgLZfyUgUz_MYyHN78OFbeEXiDOa_7zTyYN3UUwzlXRDkpdJ3Zv8nXAJj61oCeYijrN21RmeFiH95SZFmbuTyZBpQnfS)
12. [frontiersin.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErF905czHhSGZmGqfIjDVNrI9ZUaJdqCsrI855V7lgv-xOs8FZKXszk_wHzTTvVl-c_1_krzAqJ2tsK0eLNc-zzlqAW8hYuTGR_JXYeYpseh7xgtqvKDsdf21E6UbAA-3J6sOjF1tcpzZbs3UacNcUiwKo86AM4DoocqE36ifbphh3eaitRB6WCffyuPtuu8OIIh13)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVxiEcoKThGMfBLx_ficeMyV3yeQb8YjBB02v7wKSy7uNzGPceuTESfmtFzEZuYRboX87tRWTlVgV3LsBw_kg3CykWbsZ_SVDVo6V-MTQ58ocUeikOnQ==)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgbQDoFiHBrjfWdDXCB-ORvPIUYHYeTkTDIOQ4T7mRbny9mt9WsC5mu3j2hAwoOItMUCXWvHBUxUbIi9wy4ylFAIXG_kJYtTK_eUVsHcbEwZaADvb3MfD--R6YXvogow12te2GFmUxKwNxJxY-wppE8mKftDvuvR-Rclj5-g_oOg7wYAznX3s9Na20H9iVk1JLIjmBS17I3sPIkuUf6Uf2hIry1w==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJDmO-QkDO59UaI9X7sUYC_VktudrU9aVfo82KwIcenN_PdMj8-6ZwOykhk0oVBjvzyhCKg6fxpYiybPGpkM9SOdC3TS38NzxOsjx1RTzguDZBMW6DrLBtjg==)
16. [ilds.ro](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHL7ePE96n6JlRjNSlwL35MvbrZXGszhPE4M8-RLnyvdoJFkyGYpHPdpwXhZN-BAvmTAzX_wJVpfcfndEGwn8kFdcJMFdYCpBSPHmmpwvfXTl1Uk5bX12hhoC_mNt6ubWfVbEIrp5PboA==)
17. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGydCEn2Gp26U7cGznJyW2jv807NMAODXZnlwiTdX3kayro5S5y3IA9Y55XUTZqm8RSqypxHd1BpgQiv4nrIL3_mPUjImg9-ox3y99sQ5kVDVQbuNIti3oiWuHBibwgMxsc-sbIdJ3nhiw=)
18. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF42FoqrS4i7aVfceA7ExC8kK38lemlemJHZFiAHEI4fDlKdB-QYWG5dhz8WOhXyMzp_fyUPl7ul2exMq_yDW32ZOWuni771ZWhWNuEySdeHMNl6Pf8l5PwrLXi54qfcoZiO0VmH7AzUYLK_itcx3Rfhp0d7Ka8ydW1_oilSniy7pufplH3CkBsUq0_SUrD)

