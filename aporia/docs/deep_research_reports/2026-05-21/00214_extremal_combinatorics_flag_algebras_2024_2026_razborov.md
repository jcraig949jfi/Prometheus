# Extremal combinatorics + flag algebras 2024-2026 (Razborov)

**Pythia queue id:** 214
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdlRXNQYXRIR0ZlREwtc0FQcjVHd2dBbxIXZUVzUGF0SEdGZURMLXNBUHI1R3dnQW8
**Elapsed:** 307s
**Completed at:** 2026-05-21T18:19:24.908974+00:00

---

# Extremal Combinatorics and Flag Algebras: Theoretical Breakthroughs and Computational Scale-Up (2024-2026)

**Key Points:**
*   **Flag algebras**, introduced by Alexander Razborov in 2007, have transitioned from a primarily theoretical calculus to a heavily computational framework, culminating in sophisticated automation tools like the `FlagAlgebraToolbox` in SageMath (2026).
*   Recent research (2024–2026) has successfully paradoxically applied flag algebras—originally designed for asymptotic bounds on infinite limit objects—to determine **exact bounds for finite combinatorial structures**, including small Ramsey numbers.
*   The fundamental theory of flag algebras is currently undergoing a structural evolution; researchers are formalizing it through **category theory** and **logical semantics**, making it accessible to computer scientists working in automated verification.
*   Alexander Razborov continues to actively shape the field, co-authoring significant papers in 2025 on **domination exponents** for pairs of graphs, challenging long-standing limits in graph density profiles.
*   Large-scale initiatives, such as the MATH+ Berlin **FlagScale** project, are actively overcoming prior computational bottlenecks, moving flag algebra computations from personal computers to high-performance computing (HPC) environments. 

**Introduction for the General Reader**
Extremal combinatorics is a branch of mathematics that asks questions about the absolute limits of discrete structures: for example, "What is the maximum number of edges a network can have without containing any triangles?" For decades, mathematicians solved these problems using localized, ad-hoc techniques. In 2007, Alexander Razborov introduced "flag algebras," a revolutionary framework that translated these varied graphical problems into continuous algebra. Instead of looking at finite graphs, flag algebras look at the "limits" of graphs as they grow infinitely large. By doing so, it allows mathematicians to use powerful computer optimization software—specifically semidefinite programming—to find the absolute bounds of these structures. 

**The Current Era of Research**
Between 2024 and 2026, the study of flag algebras has entered a highly industrialized phase. While early flag algebra proofs required mathematicians to meticulously hand-code complex constraints, new software pipelines automatically generate and solve these massive equations. Furthermore, mathematicians are finding surprising ways to use this tool, which was built for infinity, to solve problems about very small, finite networks (like calculating exact Ramsey numbers). Concurrently, theoretical limits are being tested through category theory, redefining how these mathematical objects map to one another.

**Addressing the Complexity**
It seems likely that the integration of flag algebras with machine learning and automated theorem provers (like Lean) will dictate the next decade of combinatorial research. However, the method has intrinsic limitations; certain classes of problems appear resistant to the "sum-of-squares" methodology that flag algebras rely on. A major focus of the 2025 academic workshops is understanding exactly where flag algebras fail, and how to rigorously translate computer-generated proofs back into human-readable mathematics. 

***

## 1. Introduction: The Evolution of Flag Algebras in Extremal Combinatorics

Extremal combinatorics focuses on determining the maximum or minimum sizes of discrete structures—such as graphs, hypergraphs, or permutations—that satisfy specific restrictive properties [cite: 1, 2]. Historically, this field was viewed by mathematicians in other disciplines as a collection of clever, but isolated, ad-hoc methods [cite: 3]. This perception shifted dramatically with the introduction of overarching theoretical frameworks, most notably the probabilistic method, the regularity lemma, and the theory of graph limits [cite: 3, 4]. 

Within this movement toward unification, Alexander A. Razborov introduced the theory of **flag algebras** in 2007 [cite: 5]. Inspired by John Adrian Bondy's work on the Caccetta-Häggkvist conjecture and Lovász and Szegedy's work on graph limits, Razborov constructed a universally quantified first-order formal calculus that describes the relations between densities of small patterns in limit combinatorial structures [cite: 6]. The flag algebra framework translates extremal combinatorial questions into continuous polynomial optimization problems [cite: 5]. These problems can then be relaxed into semidefinite programs (SDPs) and efficiently solved by computers using the sum-of-squares (SOS) method, providing rigorous, automated certificates for asymptotic bounds [cite: 5, 7].

Between 2024 and 2026, the field of flag algebras experienced a rapid expansion in both theoretical foundations and computational applications. The method, which had already led to breakthroughs on open problems posed by Erdős, Sós, Turán, Gromov, and Zarankiewicz, was systematically scaled up [cite: 8, 9]. The MATH+ FlagScale project [cite: 6], the release of SageMath's `FlagAlgebraToolbox` [cite: 10, 11], and major collaborative workshops at the American Institute of Mathematics (AIM) [cite: 3, 9] represent a concerted effort to push the boundaries of what is computationally and theoretically possible. Furthermore, foundational efforts to categorify flag algebras [cite: 12] and re-cast them in the language of formal logic [cite: 13, 14] have broadened the technique's accessibility to theoretical computer scientists and logic verification communities.

This report exhaustively details the state of extremal combinatorics utilizing flag algebras from 2024 to 2026, highlighting Alexander Razborov's ongoing contributions, the development of software frameworks, the mathematical categorification of the theory, and the surprising new applications of the method to finite exact bounds.

## 2. Theoretical Foundations and the Flag Algebra Calculus

To understand the advances of the 2024–2026 period, it is essential to establish the mathematical mechanics of Razborov's flag algebras [cite: 13, 14]. The easiest and most popular usage of the theory relies on homomorphisms from linear combinations of combinatorial structures to the real numbers [cite: 7]. 

### 2.1. Types, Flags, and Densities

The theory generalizes across universally quantified first-order theories, meaning it is applicable whenever a subset of a structure induces a substructure [cite: 12]. This includes simple graphs, directed graphs, hypergraphs, permutations, and recently, leaf-labeled rooted binary trees [cite: 5, 15].

*   **Types:** A type $\sigma$ is a fixed combinatorial structure whose vertices are labeled $1, 2, \dots, |\sigma|$. The simplest type is the size 1 type corresponding to a single vertex [cite: 15].
*   **Flags:** A $\sigma$-flag (or simply a flag) is a pair $F = (M, \theta)$, where $M$ is a combinatorial structure and $\theta: \sigma \to M$ is an embedding of the type $\sigma$ into $M$ [cite: 15]. 
*   **Flag Algebra ($\mathcal{A}^\sigma$):** Linear combinations of $\sigma$-flags form a vector space. A multiplication operation $F_1 \cdot F_2$ is defined based on the probability that choosing random overlapping subsets in a larger structure will yield $F_1$ and $F_2$ intersecting exactly at the labeled type $\sigma$. Factoring out an ideal of relations (which represent elements that intuitively evaluate to zero in the infinite limit) yields the flag algebra $\mathcal{A}^\sigma$ [cite: 7, 15].

### 2.2. Semantics and Limiting Objects

Problems in extremal combinatorics generally ask for the maximum or minimum possible density of a fixed finite pattern among all large structures satisfying certain constraints (such as forbidding a specific subgraph) [cite: 13, 14]. In flag algebras, limit sequences of combinatorial structures are represented by order-preserving algebra homomorphisms from the flag algebra to the real numbers: $\phi: \mathcal{A}^0 \to \mathbb{R}$ [cite: 12].

As an example, to prove Mantel's Theorem (which states that the maximum number of edges in a triangle-free graph on $n$ vertices is $\lfloor n^2/4 \rfloor$), one utilizes the syntax of flag algebras. Assertions are made about limiting graphs using density expressions [cite: 13, 14]. By establishing that the density of triangles is exactly related to edge density, Razborov used flag algebras as a purely theoretical framework to provide the exact algebraic relation [cite: 6].

### 2.3. The Downward Operator and Sum-of-Squares (SOS)

A core innovation in flag algebras is the ability to shift between different types. The **downward operator**, denoted $[\![ \cdot ]\!]$, transfers expressions from a labeled variant of the algebra (with a type) back to the unlabeled setting (the empty type) [cite: 13, 14]. 

Because any square of a flag element is non-negative (i.e., $f^2 \ge 0$), the downward operator guarantees that $[\![ f^2 ]\!] \ge 0$. The sum-of-squares (SOS) method leverages this: any linear combination of flags that can be expressed as a sum of squares via the downward operator represents a valid inequality [cite: 12]. Computationally, finding the optimal sum-of-squares expression to bound an objective function is relaxed into Semidefinite Programming (SDP) [cite: 6].

## 3. Alexander Razborov's Ongoing Contributions (2024–2026)

Alexander Razborov, currently affiliated with the University of Chicago and the Steklov Mathematical Institute, developed flag algebras in 2007 [cite: 16, 17]. Between 2024 and 2026, he remained highly active in expanding the theoretical limits of extremal combinatorics, exploring density profiles, propositional proof complexity, and quasirandomness [cite: 18, 19]. 

### 3.1. On Domination Exponents for Pairs of Graphs (2025)

Understanding graph density profiles—the region of all feasible density configurations for a set of subgraphs—is notoriously challenging [cite: 15, 17]. Even for pairs of graphs, complete characterizations are known only in very limited cases, such as the relationship between edges and cliques [cite: 17, 20]. 

In a pivotal August 2025 paper titled *"On Domination Exponents for Pairs of Graphs"* co-authored with Grigoriy Blekherman, Annie Raymond, and Fan Wei, Razborov explored a relaxation of the graph density profile problem by formalizing the concept of the **homomorphism density domination exponent** [cite: 17, 21].

**The Domination Exponent $C(H_1, H_2)$:**
Given two graphs $H_1$ and $H_2$, the domination exponent $C(H_1, H_2)$ is defined as the smallest real number $c \ge 0$ such that:
\[ t(H_1, T) \ge t(H_2, T)^c \]
for all target graphs $T$, where $t(H, T)$ represents the homomorphism density from $H$ to $T$ [cite: 17, 20]. The homomorphism density $t(H,T) = \frac{\text{hom}(H,T)}{v(T)^{v(H)}}$ represents the probability that a random mapping of vertices from $H$ to $T$ preserves adjacency [cite: 20].

**Key Findings of the 2025 Paper:**
1.  **Infinite Families of Constructions:** A major question in the field was which classes of target graphs $T$ are sufficient to realize the values of $C(H_1, H_2)$ [cite: 20]. Razborov and his co-authors proved that to realize domination exponents for all connected graphs $H_1, H_2$ (and specifically even when $H_1$ and $H_2$ are confined to be even cycles), infinitely many families of graphs are required [cite: 17, 20]. This directly resolved an open question (Question 6.4) from prior literature [cite: 20].
2.  **Pure Binomial Inequalities:** The paper advances the study of "pure binomial inequalities" in graph homomorphism numbers [cite: 4, 20]. The authors utilized tropicalization concepts from algebraic geometry, analyzing the cone of valid pure binomial inequalities for families of graphs including complete graphs, even cycles, stars, and remarkably, paths [cite: 4, 20].
3.  **Exact Values and Sharp Bounds:** The team derived exact values for $C(H_1, H_2)$ when $H_1$ is an even cycle and $H_2$ contains a Hamiltonian cycle, and they provided asymptotically sharp bounds when both $H_1$ and $H_2$ are odd cycles [cite: 17, 22]. 

### 3.2. Biregularity and Sidorenko's Conjecture

Sidorenko's conjecture (1991) is a central topic in extremal graph theory. It posits that for every bipartite graph $F$ and every graph $G$, the homomorphism density $t_F(G)$ is at least $t_{K_2}(G)^{e(F)}$ [cite: 23, 24]. In the language of domination exponents, Sidorenko's conjecture asserts that for any bipartite graph $H$, $C(H, K_2) = e(H)$ [cite: 17, 20].

Razborov's work has been instrumental in framing approaches to this conjecture. His 2021 preprint, *"Biregularity in Sidorenko's Conjecture"*, co-authored with Leonardo Coregliano, introduced the concept of **induced-Sidorenko bigraphs** as building blocks to obtain Sidorenko bigraphs [cite: 24, 25]. This provided a generalization of the $N$-decompositions technique developed by Conlon and Lee [cite: 24]. Razborov and Coregliano's concepts formed the foundation for further generalizations throughout 2024 and 2025, heavily influencing subsequent research on hypergraph extensions of Sidorenko's conjecture [cite: 23, 24].

### 3.3. Propositional Proof Complexity

Beyond purely structural combinatorics, Razborov maintains a deep focus on theoretical computer science and complexity logic. His recent publications, including works on the space characterizations of complexity measures (2023) and his lectures on Propositional Proof Complexity at the 8th European Congress of Mathematics (published 2023), intersect conceptually with the logical frameworks that underpin automated theorem verification—a field that flag algebras are increasingly being integrated into [cite: 18, 19].

## 4. The Categorification and Logical Re-framing of Flag Algebras

Until 2024, flag algebras were primarily presented in purely combinatorial terms when applied to specific optimization problems, despite Razborov's original formulation being phrased in universally quantified first-order theories [cite: 12]. Because applications (such as studying Ramsey multiplicities or hypergraph Turán problems) often utilized custom, ad-hoc derivations of the algebra, the theory risked becoming mathematically fragmented [cite: 12].

### 4.1. Category Theoretic Foundations (2024)

At the Discrete Mathematics Days in Alcalá de Henares (July 2024), Aldo Kiem, Sebastian Pokutta, and Christoph Spiegel presented a landmark paper titled *"Categorification of Flag Algebras"* [cite: 12]. This work proposed a unified category theoretic foundation for flag algebras, capturing both the original first-order logic derivation and the pure combinatorial approaches [cite: 12].

**Archimedean Partially-Ordered Vector Spaces**
To formalize the framework, Kiem et al. defined flag algebras as Archimedean partially-ordered vector spaces [cite: 12]. An $\mathbb{R}$-vector space $V$ with a preordering $\le$ is considered Archimedean when, for every $v, w \in V$, the condition $v \le r w$ for every $r \in \mathbb{R}_{>0}$ implies $v \le 0$ [cite: 12]. 

**Presheaves and Colimits**
The categorification models theories as functors. The colimit $\mathcal{A}[F] = \text{colim}_\mathbb{R} F$, acting as a functor from the category of finite presheaves $\text{FinPsh}(\mathcal{A})$ to the category of Archimedean spaces $\text{Arch}$, perfectly reproduces Razborov's original flag algebra [cite: 12]. In particular, for every universally quantified first-order theory $T$, the flag algebra $\mathcal{A}[T]$ defined by Razborov was proven to be isomorphic to the Archimedean vector space $\mathcal{A}[F_T]$ derived from the presheaf $F_T$ [cite: 12]. 

**New Foundational Results**
This categorification was not merely an abstraction exercise; it yielded immediate structural mathematics results [cite: 12]. Kiem, Pokutta, and Spiegel achieved:
1.  A partial classification of linear and order-preserving maps between flag algebras [cite: 12].
2.  A formulation of higher-order vertex differential methods [cite: 12].
3.  A rigorous generalization of the downward and upward operators as induced maps between density categories [cite: 12].

### 4.2. A Logical Perspective for Computer Scientists (2026)

Following the mathematical categorification in 2024, an effort emerged to translate flag algebras into the vernacular of computer scientists working in programming languages, automated verification, and formal methods [cite: 13, 14]. A comprehensive survey published in January 2026 aimed to reframe flag algebra entirely in terms of syntax, semantics, and proof strategies [cite: 13, 14].

**Syntax:** 
Instead of relying purely on combinatorial sums, the logic community framed flag algebras using standard formal syntax logic [cite: 13, 14].
*   **Density Expressions $E$:** $E ::= H \mid r \cdot E \mid 0 \mid E + E \mid 1 \mid E \cdot E$ (where $H$ ranges over graphs and $r$ over real numbers).
*   **Assertions $A$:** $A ::= \text{false} \mid \text{true} \mid E \ge E \mid \neg A \mid A \vee A$ [cite: 14].

**Adjoint Pairs:**
In this framework, the transfer mechanism of the downward operator—used to move inequalities from a labeled variant back to the unlabeled setting—was explicitly mapped to the concept of an **adjoint pair of functions** [cite: 13, 14]. This concept is highly reminiscent of Galois connections and categorical adjunctions, which are standard paradigms in automated code verification [cite: 13]. By translating Razborov's calculus into this logic, the 2026 survey provides a direct bridge for the integration of flag algebras into proof assistants like Lean [cite: 13, 26].

## 5. The Computational Scale-Up: Software and HPC

The theoretical power of flag algebras is fundamentally tied to computational execution. The size of the Semidefinite Programming (SDP) relaxations scales exponentially with the size of the studied sub-structures [cite: 6]. Prior to 2022, existing applications were largely limited to the context of personal computing, severely restricting the depth of the bounds that could be calculated [cite: 6].

### 5.1. The FlagScale Project (MATH+ Berlin)

Recognizing this computational bottleneck, the Berlin Mathematics Research Center (MATH+) funded the **FlagScale** project (Project ID EF1-21) from October 2022 to September 2025 [cite: 6]. Spearheaded by Principal Investigators Christoph Spiegel and Sebastian Pokutta, alongside researchers Aldo Kiem and Olivia Röhrig at the Zuse Institute Berlin (ZIB), the project sought to scale up flag algebras in combinatorics [cite: 6]. 

**Goals and Impact:**
The core objective was to improve the underlying computational aspects to scale up the flag algebra calculus for existing problems and to open up new areas of application for the SDP-based approach [cite: 6]. Because the density computations and the size of the SDP scale rapidly, FlagScale actively developed software frameworks enabling researchers to leverage high-performance computing (HPC) and robust integer programming methods [cite: 1, 6]. 

The ZIB group, heavily engaged with Artificial Intelligence and computational mathematics, also investigated how common search heuristics and Machine Learning could overcome traditional computational limits (such as exponential growth in search spaces) when applied to extremal structures [cite: 1, 2]. This interdisciplinary focus generated tools that married reinforcement learning, formal verification, and SDP matrix generation [cite: 2, 27].

### 5.2. FlagAlgebraToolbox in SageMath (2026)

A direct result of the drive toward better computational tools was the release of the `FlagAlgebraToolbox` in January 2026 [cite: 10, 11]. Authored as an extension of the open-source mathematics software SageMath, the toolbox automates flag algebra calculations and numerical optimizations [cite: 11, 28].

**Toolbox Architecture:**
In practice, carrying out a flag algebra computation manually involves an immense number of small steps: generating a list of combinatorial objects and flags, calculating the chain rule, establishing multiplication relations and projections between flags, and finally finding optimal sum-of-squares expressions [cite: 11]. Existing implementations prior to 2026 (such as 'Flagmatic' introduced in 2012 by Falgas-Ravry and Vaughan) were highly tailored to standard theories like basic graphs or 3-graphs and lacked extensibility [cite: 5, 11].

`FlagAlgebraToolbox` abstracted these processes. It provides high-level methods for constructing diverse combinatorial theories, including graphs, digraphs, hypergraphs, and hypercubes [cite: 11, 28]. 

**Key Features:**
*   **Automatic Coercion:** Flags are automatically coerced into a `FlagAlgebraElement` to perform arithmetic. The suitable algebra is dynamically found [cite: 28, 29]. For example, the sum of an edge and a triangle results in a linear combination of flags within a suitable `FlagAlgebra` parent object [cite: 11, 29].
*   **Projections:** Projecting a flag with a large type to a smaller one is handled seamlessly by the `project()` function [cite: 11, 29]. 
*   **Exact Rounding:** While SDP solvers (like CSDP, integrated natively) output numerical floating-point bounds, `FlagAlgebraToolbox` includes an automatic rounding method (using the parameter `exact=True`) to convert numerical optimizations into rigorous, exact mathematical proofs [cite: 10, 28]. 
*   **Custom Theories:** Users can encode custom bounds easily; for example, the `ThreeGraphTheory` encodes rules for 3-graphs to maximize induced densities [cite: 11, 28].

### 5.3. Fully Computer-Assisted Proofs and Heuristics

The synergy of flag algebra density bounds with computational search heuristics created a new paradigm of "Fully Computer-Assisted Proofs in Extremal Combinatorics," detailed in a pivotal paper by Olaf Parczyk, Sebastian Pokutta, Christoph Spiegel, and Tibor Szabó [cite: 26, 30]. 

The obvious downside of computational search heuristics (like simulated annealing or genetic algorithms) is the lack of a guarantee of global optimality [cite: 30]. However, the researchers demonstrated that this flaw can be fully eliminated by combining the search heuristics with the absolute lower bounds and stability results generated by Flag Algebras [cite: 30]. If a heuristic finds a constructive network that exactly matches the theoretical limit proven by the Flag Algebra SDP, the problem is definitively solved [cite: 30]. Using this combined system, the team settled the minimum number of independent sets of size four in graphs with clique numbers strictly less than five, and made the first major improvement in the upper bound of the Ramsey multiplicity of $K_4$ in 25 years [cite: 30, 31].

## 6. Breakthrough Applications in Extremal Combinatorics (2024–2026)

With the theoretical and computational frameworks significantly strengthened, the period of 2024-2026 saw rapid closures of long-standing open problems across various subfields of combinatorics. 

### 6.1. Finding Exact Ramsey Numbers

Ramsey numbers $R(t_1, t_2)$ determine the minimum number of vertices $n$ such that any 2-edge-coloring of the complete graph $K_n$ contains either a monochromatic clique of size $t_1$ in the first color or a monochromatic clique of size $t_2$ in the second color [cite: 7]. Finding exact Ramsey numbers is notoriously difficult and typically restricted to extremely small graphs; famously, $R(5,5)$ remains unknown, though Angeltveit and McKay established the best upper bound of $R(5,5) \le 46$ in 2024 [cite: 7].

**The Paradox of Applying Flag Algebras to Small Graphs:**
Because the flag algebra method was designed by Razborov to find asymptotic results for *very large* (infinite limit) graphs, the prevailing intuition was that the method would be highly unsuitable for finding exact, small Ramsey numbers [cite: 7]. However, a 2026 paper successfully developed a technique to do precisely this, leveraging SDP certificates that are sums of squares [cite: 7].

**Methodology for Finite Bounds:**
To bound $R(G_1, \dots, G_k)$, the researchers assumed some $n < R(G_1, \dots, G_k)$ and started with a $\{G_1, \dots, G_k\}$-free $k$-edge-coloring $H$ of a complete graph $K_n$ [cite: 7]. They then replaced every vertex with a large independent set of size $N$ (an iterated blow-up graph) [cite: 7]. Combinations of flag algebra inequalities evaluated on this massive blow-up produced desired bounds that cascaded down to restrict the properties of the original small graph $H$ [cite: 7]. 

**The Clebsch Graph and $R(K_4^-, K_4^-, K_4^-)$:**
Using this technique, the SDP flag algebra computation gave a list of graphs on 8 vertices that were highly unlikely to appear in a Ramsey graph on 16 vertices [cite: 7]. Assuming the 8-vertex subgraphs were forbidden provided a massive restriction on possible graphs on 9 or more vertices, allowing the computers to exhaustively enumerate all such remaining graphs up to 16 vertices [cite: 7]. This led to the discovery of exactly one valid Ramsey graph on 16 vertices: the Clebsch graph [cite: 7]. Consequently, they proved that the 3-color Ramsey number for $K_4$ minus an edge is exactly 28:
\[ R(K_4^-, K_4^-, K_4^-) = 28 \]
Previously, the best-known upper bound was 30 (Piwakowski) [cite: 7]. This achievement marks a historical milestone in leveraging infinite-limit frameworks to solve finite discrete matrices [cite: 7].

### 6.2. Inducibility of Graphs and Rooted Binary Trees

The "inducibility" of a graph, introduced by Pippenger and Golumbic in 1975, asks for the maximum frequency with which a fixed graph on $k$ vertices can appear as an induced subgraph in an infinitely large graph [cite: 5]. 

**$(\kappa, \ell)$-edge-inducibility:**
In July 2025, Levente Bodnár and colleagues published exact results for the $(\kappa, \ell)$-edge-inducibility problem, which asks for the maximum number of $\kappa$-subsets inducing exactly $\ell$ edges that a graph of order $n$ can contain [cite: 32]. Using flag algebras and a stability approach, the team resolved this problem for all sufficiently large $n$ in eleven new non-trivial cases where $\kappa \le 7$ [cite: 32]. They also computed the $F$-inducibility constant for three new graphs on 5 vertices: the 3-edge star plus an isolated vertex, the 4-cycle plus an isolated vertex, and the 4-cycle with a pendant edge [cite: 32]. 

Furthermore, Bodnár's work developed general methods for establishing "stability-type" results directly from flag algebra computations [cite: 33]. They defined a problem as *perfectly B-stable* for a graph $B$ if every admissible graph $G$ of order $n \ge C$ can be made into a blow-up of $B$ by changing only a limited number of adjacencies [cite: 33]. One of their sufficient conditions for perfect stability was stated in such a way that it allowed for automatic verification by a computer [cite: 33].

**Leaf-Labeled Rooted Binary Trees:**
Beyond graphs, flag algebras were applied for the first time to leaf-labeled rooted binary trees (objects widely studied in phylogenetics) in 2024 [cite: 5]. While Czabarka, Székely, and Wagner had previously studied limit sets of $k$-profiles for these trees, researchers in 2024 built a specific flag algebra of rooted binary trees [cite: 5]. This framework allowed them to formulate extremal problems as polynomial optimizations [cite: 5]. By doing so, they recovered all existing bounds on the inducibilities of trees with up to 10 leaves, computed hundreds of completely new sharp bounds, and computed the first outer approximations of profiles of trees (encoding the possible simultaneous densities of multiple small trees in an infinite tree) [cite: 34]. 

### 6.3. Turán Problems in Hypergraphs

Flag algebras maintain their critical role in determining Turán densities, especially for hypergraphs [cite: 8]. The Turán $H$-density for 3-graphs, generalizing the notion of inducibility, was investigated via Razborov's semi-definite method, resulting in new proofs that, for example, the density $\pi_{K_4^-}(K_4) = 16/27$, confirming that Turán's construction is optimal for this configuration [cite: 33].

## 7. The Mathematical Community: Workshops and Future Directives

The rapid acceleration of flag algebra research has necessitated significant community organization to aggregate findings and chart future courses.

### 7.1. The 2025 AIM Workshop

From October 13 to October 17, 2025, the American Institute of Mathematics (AIM) in Pasadena, California, hosted a seminal workshop titled **"Flag algebras and extremal combinatorics"** [cite: 8, 9]. The workshop was organized by József Balogh (UIUC), Dingding Dong (Harvard), Bernard Lidický (Iowa State), and Annie Raymond (UMass Amherst) [cite: 3, 9]. Sponsored by AIM and the NSF, the event attracted experts in both the computational aspects of flag algebras and researchers exploring the theoretical limitations of sum-of-squares methods [cite: 3, 9].

**Key Topics of the Workshop:**
1.  **Applications in Combinatorics:** Participants shared cutting-edge applications to hypergraph Turán problems, rainbow Turán problems, and Sidorenko's conjecture [cite: 8, 9].
2.  **Strengths and Limitations:** A major scientific objective was to better understand the theoretical boundaries of flag algebras. This included utilizing tools from algebraic geometry (such as tropicalization) to prove inequalities that generate *all* valid inequalities of a certain form, and conversely, identifying classes of extremal problems that fundamentally *cannot* be solved with the sum-of-squares method [cite: 3, 8].
3.  **Proofs Without Computers:** As the reliance on high-performance computing and numeric SDP solvers grows, there is a push to translate SDP certificates back into human-readable proofs. The workshop dedicated specific sessions to obtaining proofs by flag algebras that do not explicitly require computer assistance to be verified [cite: 8, 9]. 

The workshop followed the traditional AIM schedule, featuring theoretical lectures in the mornings to familiarize participants with background material, and collaborative, parallel problem-solving sessions in the afternoons [cite: 9]. The insights generated during this week in October 2025 are expected to heavily influence the future activity of the field [cite: 9].

### 7.2. Integration with Automated Proof Verification

As seen in the ZIB FlagScale group's objectives and the 2026 logical semantics reframing of flag algebras, the future of the field points toward total formal verification [cite: 2, 13]. The "LEAN on Me: Transforming Mathematics through Formal Verification, Improved Tactics, and Machine Learning" project (MATH+ AA5-9) highlights the intersection of extremal combinatorics and automated theorem provers [cite: 2, 26]. By formalizing flag algebra results in languages like Lean, researchers ensure absolute proof correctness of computer-generated bounds [cite: 2]. This removes the traditional skepticism surrounding "computer-assisted proofs" that has persisted since the proof of the Four Color Theorem [cite: 2].

## 8. Limitations and Open Problems

Despite the monumental successes of 2024–2026, the flag algebra method is not a panacea for all combinatorial limits. 

**Decidability of Pure Binomial Inequalities**
As highlighted in Razborov's 2025 paper on domination exponents, it remains remarkably unknown whether the set of all pure binomial inequalities (inequalities of the form $t(H_1,T)^{c_1} \dots t(H_k, T)^{c_k} \ge 1$) is decidable or not [cite: 20]. While tropicalization captures all valid pure binomial inequalities on specific domains, proving general decidability remains a profound open question in theoretical computer science and algebraic geometry [cite: 20].

**Limitations of Sum of Squares (SOS)**
The fundamental mechanism of flag algebras relies on SOS relaxations [cite: 6]. However, not all non-negative polynomials can be represented as sums of squares. Therefore, there exist theoretically valid density inequalities that the standard flag algebra SDP pipeline will never be able to certify [cite: 3, 21]. Researchers are actively exploring higher-order Delsarte Dual LPs and other algebraic geometries to bypass the SOS bottleneck [cite: 21, 25].

**Complex Constructions and Joint Distributions**
Current computational tools, including the 2026 `FlagAlgebraToolbox`, still face limitations regarding complex iterative constructions. For example, the blow-up construction functions currently struggle to support deeply recursive constructions [cite: 29]. Additionally, quasi-random relations within these computational models are typically treated as independent; a potential extension for future software iterations would be to allow any joint probability distribution between different relations, greatly expanding the expressiveness of the SDP relaxations [cite: 29].

## 9. Conclusion

The period of 2024 to 2026 represents a golden era for the study of Extremal Combinatorics via Flag Algebras. What began in 2007 as Alexander Razborov's elegant theoretical bridge between finite discrete mathematics and infinite continuous limits has matured into a highly industrialized, computationally backed scientific discipline.

Razborov himself continues to break new ground, utilizing concepts like domination exponents and tropicalization to push the boundaries of graph density profiles and Sidorenko's conjecture [cite: 17, 20]. Simultaneously, the broader mathematical community has formalized the theory via categorification and logic syntax, cementing its structural permanence [cite: 12, 14].

Crucially, the computing bottlenecks that previously restricted the method have been dismantled by high-performance toolboxes (`FlagAlgebraToolbox`) and funded scaling initiatives (FlagScale) [cite: 6, 10]. This unprecedented computational power has yielded seemingly paradoxical triumphs, such as utilizing a framework designed for infinity to uncover exact Ramsey numbers like $R(K_4^-, K_4^-, K_4^-) = 28$ [cite: 7]. As flag algebras become increasingly integrated with machine learning heuristics and automated proof verification platforms, they stand poised to illuminate the furthest, most complex frontiers of discrete mathematics.

***
### Data Tables

**Table 1: Key Software and Institutional Developments in Flag Algebras (2024–2026)**

| Initiative / Software | Year | Primary Contributors / PIs | Focus Area | Source |
| :--- | :--- | :--- | :--- | :--- |
| **Categorification of Flag Algebras** | 2024 | A. Kiem, S. Pokutta, C. Spiegel | Category theory, Archimedean spaces, formal math. | [cite: 12] |
| **FlagScale (MATH+ EF1-21)** | 2022-2025 | C. Spiegel, S. Pokutta, A. Kiem, O. Röhrig | Scaling SDPs, HPC integration, theoretical extensions. | [cite: 6] |
| **AIM Workshop Pasadena** | Oct 2025 | J. Balogh, D. Dong, B. Lidický, A. Raymond | Limits of SOS, Sidorenko's conjecture, human proofs. | [cite: 8, 9] |
| **FlagAlgebraToolbox (SageMath)** | 2026 | Various (ZIB Lab contributors) | Automated exact rounding, custom hypergraph theories. | [cite: 10, 11] |

**Table 2: Notable Extremal Bounds Achieved via Flag Algebras (Recent)**

| Problem / Structure | Result | Significance | Source |
| :--- | :--- | :--- | :--- |
| **3-color Ramsey $R(K_4^-, K_4^-, K_4^-)$** | 28 | Exact value determined via flag algebra asymptotic constraint downscaling; Clebsch graph identified. | [cite: 7] |
| **Ramsey $R(5,5)$** | $\le 46$ | Best upper bound (Angeltveit and McKay 2024). | [cite: 7] |
| **$(\kappa,\ell)$-edge-inducibility** | Solved for $\kappa \le 7$ | 11 new non-trivial cases resolved via stability flag methods. | [cite: 32] |
| **Turán Density $\pi_{K_4^-}(K_4)$** | 16/27 | Proves optimality of Turán's 3-graph construction for this configuration. | [cite: 33] |

**Sources:**
1. [zib.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEXC17sSPPq9-Pz7Iyl53Tz0TPl-Q3hj_yBZ0rgB2kTkuTTSyewuc-WnevJRuSIWn9QEf71HocLdyboJ2DG_UsjNoRuB1MYtzK2mdBGp9EzTy9u1EtNNsXixfThM7PIA==)
2. [zib.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXJHHdaupvoVqy9vmaHuMMx--ycZKXlgIQR7Np0tpWBN1I_nTFn2ekyHVIlmDV9Rau2XrHVC2Vq2UbsqjgNu8imhm7VSN-4wBdHWCRVjMkr9MgjezyX-HTmGhWciUzlFVAqGmc)
3. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpkIRgY1PA7_6EVaq6lFpWzE8OLIul5DURJLkJF0LyXx4VxiUKOILPwxQci5y0EP6ciniCb2f7Pi7gphPtZk-6K7qhKNeCBIB4ehtGFAnsyyHHuhSYwFhYvKtIxD0RSUYF7sw18cmotTmv)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHm20OPgvjLneZVZs6p4WHW2KxX6OXCeC0cNHlLBwIV0fU3Q2QZ3PhPzt6qRdDQ1fYfdYzVQcLPRaLc-ZZsbKoND--TDTGs_QhaFv_mNpsIMUGBBMFqM9i6iB1ghaYDlqWQuwgUcAIL7ZDzvWZw5Ja8vS2YHGHNBTMRRn21udAt2Kzterog7vJtbkP6JEC6rZrFLeyj)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEst4v8qMnye-x8CVZZ6kkzWb4lqeaC821LB8gzLpmMsTU7bEYbOLUHuJMdTf2KXy7VF-mCDGxT3FNus0reXlGao6RMORM486XvwvnO04-wh590Sbsa-g==)
6. [zib.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYSEmAXMMh-fgI7Ym-ZwFAKKntK1fIz6ezjlhgRnd5TIOfC-rHEPx3JoNN7GTwTUID2KP3s-ff7-zveWSoOIgA3IMX5XgSk1e4smcjJo2E0LJ1R5yjkeEl7y_mIhlqLg==)
7. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHc6KqTBYRHswD2g2eP5eOyquGSCOUzCwwZxhj1U8Anb6-tyULQWEaeGYj4zFdSLgC91aNK28wgfjwI1rlqDqgzTv_bOyMs1gPoEGIlEuYkYXKMY0ys710O2MwSn1LNn3qbZ0Q=)
8. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfHDJ4rmySCJsbbQ-zrUpFZT0OJ1LHadL6KmhrV_NP9YVBhMao0uVAMK-eyvzSz8RLKIWynI-O3JG291H1ivyUkeWr-dI3pprUgN9aa9hwGvdrRNfRlePKsGFTBtjoSjaWuM_yTJ8q7w==)
9. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQPvjQpcyimzWqzbO2wnPg-UsYNQKJQ6HDFbvfkpMhpLriHqnJekSNlniC0Qs7P8FwOUkrTU_72SFOWBrFkrp9iKrnbVhDnBrMMy2vXWafEM_dSUtARkM4baB7qWLHSTj7F07aju0ojgE=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlhEM4mIBB13U2vOKqvPBlX8gdwuli_Z71kR65APyHFqS415JqItrL5IlipDSZ6-ShhdnymVy0actg1QZKM7Dh4wvfVwDFMwzbDsKwICyeF4unkpkmNQ==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6Nk37wEE301EQWCUPqs-qi3qfuzYcSW1Vc6_6fzQvTbdIO6NCCMcOH5KAUy2OKLmZf3jL2OErwCednKXL58GBfd1TsJYFfkFgu8BK5GQZSkpQTXEy_w==)
12. [uah.es](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAH0CZGAPacknlotnYKKuNAt6AcnRj6mmDFNsjvIUxoCeKW7uR0PHrDYjVQXB6_o29oMrgwYEyI0dfoWPfvBzJrjjlk5ABG023wc0w3LFczTp36u7qU-7Omy5fGWQK6vyCOp8iOWx9j7Evay4h)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJ0IeCCafMOKhQjEKv3nz8XYzX1Hlm_7DDQvfWTZwfvhQ208M1N0yUw_7EdPU3odsi8JPN8XqboKVtjRblP07XLkHTj3SgI5BDFBIQQv_c1DN6BQ-K6XHT1Q==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpHA71E0Fy9BvOQBlEQ46NOx--SNqkh0GHBlURVX-vljbzzYCVMQNxBOwEy_xec_IzCg1UlsYK5zIXysGEYnBJtmL6_DIniIbKBzJHja0n3kz7GoVJbQ==)
15. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtR08Rf11pB5EPocZ9pzcry_D6n6duARFgAKawkPHvVl1pGgo_NtxE5p3Qv9nYkytFSmVoOrIj9OvBLWgNtRE-YZdfRCCO3W0RCI203oUDvgCCHqjVhYhtMDfFTdS0HE8=)
16. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFI3jgWHeRdBYO_cSbiV0vepdorFpf37aLJjIo4bwkQY_DORABgCUiSYtRhItyatl1RRvUGRycggp6gAoayXT2dGS_-ImRlO8YjYqaNq8lYmYUoGAH9xdZ0beQ6UD6UVNfGkdemjW1g98GmUw9aICSqk1U=)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFoD7psJQTeWQ4pmqDQpu8d0eKe3ikB_AJIupZGQfBTFeqcxvNVy3bDn4tZMkdxsDIiISEkVO9KOOO3WCKr2TqnGfdwlu7xttPye5NzR3xxYWOqdzD26YnI_g==)
18. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_uG4Hep5_gbjGvS4JGW24BP3Ts6f_RPbL0QnAJBJuCfognPYBonRFp78dKH3UbOwkXGxesPiAF2bvDw48a1MuFxsot8twOa4PAme8jpUzEBlO73WOQRlk1YK_rnBDzqgJMTVrI1qTscdzhA==)
19. [mathnet.ru](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDXcP1iQtiepe5RFsbsdeD8hKFn3ztFpS0slx4QsSuwzgp2nFe65xiOPO92XFiKq9gEWFA7Rlf4ETDXNTTBnFQXxF_mz5D9zV-yOosGMWh0oTxl6teizNM-aAz)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJoAKvnfRZLp2tB6qR4Y-ES2KldwIVJD6aqhmvYqxQJPFf26vljgLyTfUfLBXP0BxKeXdBk94OouVi52FvZyOmSQ_m9QYa_vpEbryF2pHuCdVmljI5Gw==)
21. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFf4ht_b9_hWn_OJm-mwMqIqP2O1p0bxADFzajtb0a_qd58z6y3FYUwtaxUNkHUsyjvVTaJhpnkOPaA4ae6qrc3ZkicrRwBNs5JimE910BlTG4TxjmLyHS_hXqx)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHArmvQPeVluJHLShwuu1C8QWXGz6xvb4SeW1GZzvMvw7vM65LBkO5L0Pfo9YTNH-BL4VVnZNpTQmkR2lwnwM5sss2YOhpDIZiAWkQMyl19f74_YJ_TWQ==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPhBVWN7fkYJR2hyfJNwkNuK7upNhyI4jXRTCjf5zjLbfUf9ClcSl-dBqi33tfP2Sl97LjtEPUFA7BtSFvWFcN9pnydW5x2r2XNy9nAQVx-9wpwPdabtVveA==)
24. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuZOa4B_muzohA4CJrL_LK2cEfBMCiP4ZVodFaBl_NW301h2n71QnEZH0LmV-B5hqGAQDb5WSAdxoSpPc_0CHKu3vqq5zLA7FVKswaV-7pzS0xe6rotdc8Y4Y5YBjwWfGYMDPhOIuk)
25. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5vCsiKUQCTz02HQrgXanKGldAtXiLaVMeXEBZSO7-6Va2Kwn_ovHSSW8HCoFAizMuVGMGoO-nrlxQH_vIpz-HngebdNvqAfOPJ3bGTaluLyPXVsuQs-DL0iCT8f1w7hxhW699MOWKAh5C9_ziDA==)
26. [christophspiegel.berlin](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrG3SnPX7-jhmjdruBVR0724Cnac9Aa9ScCg8ZSCtt1ECFCw_OatHBQkGji5Yy7190FQGQh-bxcrfU0QXNgtVCvQGb0DYWCqS_K8uQPi1Z3eZzEWwPBQ==)
27. [zib.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8GnhHUvLZIGlpboCh8cVgKhkYHwiT_ilkx0clQHIjvtuTwvpgUpT29GixLp9ykAcxAwcfnKSwH6WyIamjwCpWx-xck2Lw4kNNCmCXwlGzr8Db)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnUjhvoODn4RB5n6_eW4wnw8Sm3PhMYY05IkkJy1xplU4KVq5II45q9uBmJnYNrfsogrlpHoqyHd_O7nbNWG6UWhzOxwGVRTNNTN4_ZcL830NnVi4sdyieJA==)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGirNOZB65VfpPz7wjyalq-1YOh3TC5s9vWzcbHRc50Fds_z-DgzP18_p4w-vntuLp9PZOzZ_ygLncsTbKN5JGtztWaM8W3Zd2tXdkQTJrV9Eo0fWHiz0M2sQ==)
30. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnQWlcL6gnL6o9LRmqgJL5sxu2ayuS30R8uJS7DxaORV7mXnyVzHD9nRdYUVeAhbm0-mH5iLbIcTezTL6A8N1uKn1mOzqKMqjsSl8hETbj7mu1fI5S4SeRs_oW7m7w-wpPPzHK9OA3kVax-5E=)
31. [zib.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPX5nfJxH6fySSiP_FKQWqPxYvNmufcjJP6Sx5Tr75B4kNlZKA_IJh7w5SzqAtYpP494yGSMr5X76NRAAlcE8Y_clzbqAjuLPWxPCjNVvmS7bQtX7K)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQN_4FQTpNqTbQtB306LbxICnkL0L_L5K7cSzlYARVBTzliKTCKRozHBEkcKbS10WhLVaDd3zFiEYbJ-EpsyItFV9KNimcoBNXXxP53esevXHNMsuxfg==)
33. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyrBuDwLxOeZLehv_czJTABOSwHEWJJcInKJuimjDNyZiALnl_ePO_xKM1MFxvSttSgRoq6wsjcEBWMhE9v6RQiCOItGb-EFiXqdYPr_dyM3Xj8luv79-DjdakwW1_YDTeEGiRCYr9ha7Khy_ZjQ3P3-IHtRkO2pOVpiTnc7yHcMZG0YLvfDfdhpvhgq3l8jRPeevRmrdw9n6EgB1v4DA3gA==)
34. [danielbrosch.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHScix-wTqu1p40S91hHtu2_tVD4H8MVbvnjlbXg6jIlcC8evTw7LviOc44HAMJcT2jkateF1SE700efHkbw7Gv32oaMLNEWuXV1kxixZjfRSnplWTqwIC0LcwXiPWrMeI17bRx1w==)

