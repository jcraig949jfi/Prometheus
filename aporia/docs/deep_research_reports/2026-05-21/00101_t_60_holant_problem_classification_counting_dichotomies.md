# T#60 Holant problem classification (counting dichotomies)

**Pythia queue id:** 101
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdUaHNQYXNHckZiR1pfdU1QdkxtS2tRcxIXVGhzUGFzR3JGYkdaX3VNUHZMbUtrUXM
**Elapsed:** 433s
**Completed at:** 2026-05-21T14:56:00.271002+00:00

---

# T#60 Holant Problem Classification: Counting Dichotomies and Complexity Frameworks

**Key Points**
* **Research suggests** that the Holant framework provides a highly generalized and robust mathematical structure for classifying the computational complexity of counting problems on graphs, encompassing both counting Constraint Satisfaction Problems (#CSP) and graph homomorphisms.
* **It seems likely that** complete complexity dichotomies—classifications proving that a problem is either strictly computable in polynomial time or #P-hard—can be established for increasingly broad classes of Holant problems. Recent breakthroughs have extended these dichotomies to encompass complex-valued functions and odd-arity signatures.
* **The evidence leans toward** the counting of weighted Eulerian Orientations (#EO) playing a pivotal, foundational role in resolving the ultimate classifications of complex-valued Holant problems, revealing a highly nuanced \(\text{FP}^{\text{NP}}\) versus #P dichotomy rather than a simple P versus #P split.
* **Note on Terminology:** The specific alphanumeric query "T#60" alongside "Holant" and "dichotomy" surfaces a unique multidisciplinary intersection in academic literature. While "Holant dichotomies" strictly refers to theoretical computer science and complexity theory, the strings "T60", "Holland", and "dichotomy" concurrently appear in acoustic physics (reverberation times), mechanical engineering (SAF-Holland coupling systems), cognitive psychology, and statistical parameters. 

**Introduction to Counting Complexity**
The study of computational complexity traditionally revolves around decision problems, classifying them into classes such as P (solvable in polynomial time) and NP (verifiable in polynomial time). However, many real-world and theoretical applications require not just deciding if a solution exists, but counting the total number of valid solutions. This gives rise to the counting complexity class #P, introduced by Leslie Valiant. The Holant framework was explicitly developed to comprehensively study the complexity of these counting problems, offering a more refined perspective than traditional Constraint Satisfaction Problems (#CSP).

**The Dichotomy Meta-Conjecture**
According to Ladner's Theorem, if P \(\neq\) NP, there exists an infinite hierarchy of intermediate complexity classes that are neither in P nor NP-complete. However, a major pursuit in theoretical computer science is identifying restricted domains where Ladner's Theorem does not apply, resulting in a "dichotomy." A dichotomy theorem guarantees that every problem within a specific family falls strictly into one of two categories: entirely tractable (solvable in polynomial time) or maximally intractable (#P-hard). The Holant framework has been the primary vehicle for discovering these dichotomies in counting complexity over the last two decades.

**Recent Breakthroughs and Quantum Intersections**
Recent literature has seen a surge in completed dichotomy theorems for the Holant framework, specifically resolving complex-valued symmetric signatures, Eulerian orientations, and odd-arity signatures. Furthermore, the mathematical formalisms utilized in Holant problems—specifically tensor networks and basis transformations—have been shown to share deep, structural equivalencies with quantum information theory, where concepts of quantum entanglement have been successfully applied to simplify and prove new Holant dichotomies.

***

## Introduction to the Holant Framework

### The Origins of Counting Complexity
The formal study of computational complexity historically began with decision problems—determining whether a given computational instance possesses a specific property or solution. The Cook-Levin theorem established the class of NP-complete problems, identifying boolean satisfiability (SAT) as the quintessential problem for which any other NP problem can be polynomially reduced. However, the theoretical computer science community quickly realized that answering *whether* a solution exists is often insufficient; many disciplines, ranging from statistical physics to combinatorial optimization, require determining *how many* solutions exist. 

To formalize this, Leslie Valiant introduced the complexity class **#P** (pronounced "number-P" or "sharp-P") in 1979 [cite: 1]. A problem belongs to #P if it corresponds to the number of accepting paths of a nondeterministic Turing machine that runs in polynomial time. Valiant famously proved that computing the permanent of a matrix with 0-1 entries—which is equivalent to counting the number of perfect matchings in a bipartite graph—is #P-complete [cite: 2]. This was a profound discovery because the corresponding decision problem (whether a perfect matching exists) is computable in polynomial time via Edmonds' matching algorithm, demonstrating that counting can be vastly harder than deciding.

### The Rise of Constraint Satisfaction and Dichotomy Theorems
As the study of complexity progressed, researchers sought to map the boundaries of tractability. Ladner's theorem explicitly states that assuming P \(\neq\) NP (and analogously for counting, P \(\neq\) #P), there are infinitely many intermediate complexity classes [cite: 1]. Consequently, one cannot expect a simple bipartite classification of all computational problems. However, researchers hypothesized that for naturally restricted families of problems, such intermediate complexities might not exist. This hypothesis was validated for decision Constraint Satisfaction Problems (CSP) by Thomas Schaefer in 1978, who proved a dichotomy theorem stating that any boolean CSP is either in P or NP-complete [cite: 1]. 

In the realm of counting complexity, analogous dichotomies were pursued. Creignou and Hermann (1996) proved a dichotomy for unweighted counting boolean CSPs (#CSP), and Bulatov and Grohe (2005) established a dichotomy for #CSP over arbitrary finite domains [cite: 3, 4]. These theorems assert that any problem in the #CSP framework is either polynomial-time computable or #P-hard [cite: 1, 3]. 

### The Formulation of Holant Problems
While #CSP was highly successful in modeling a wide array of problems, it possessed inherent limitations. In #CSP, an instance is typically modeled as a set of variables mapped to a domain, governed by a set of constraint functions. Graphically, this can be represented as a bipartite graph where variables reside on one side (the left-hand side) and constraint functions reside on the other (the right-hand side) [cite: 5]. Crucially, in this bipartite representation, the nodes representing variables implicitly function as equality constraints: they ensure that every constraint function connected to a specific variable receives the identical value [cite: 3, 5].

The **Holant framework** was proposed by Jin-Yi Cai, Pinyan Lu, and Mingji Xia as a strictly more general and refined framework to study counting problems [cite: 5]. The Holant framework eliminates the implicit assumption that variables must broadcast equality. By making the role of the constraint functions entirely explicit, the Holant framework can encode natural combinatorial problems that #CSP cannot, such as counting perfect matchings (which requires an EXACT-ONE constraint rather than an EQUALITY constraint) [cite: 2, 6, 7]. 

The Holant problem is parameterized by a set of constraint functions, or **signatures**, denoted by \(\mathcal{F}\) [cite: 3, 8]. The framework is strongly influenced by the development of holographic algorithms and holographic reductions, originally inspired by Valiant's work [cite: 1, 2, 9]. In the Holant framework, instances are defined by a signature grid, and the goal is to compute a partition function, known as the Holant sum [cite: 5, 8].

## Mathematical Formalism of Holant Problems

### Signatures and Signature Grids
To precisely define a Holant problem, we must establish its algebraic and graph-theoretic properties. A Holant problem is defined over a signature grid \(\Omega = (G, \mathcal{F}, \pi)\) [cite: 3, 10]. 
1. **\(G = (V, E)\)** is a graph, which may be general or restricted to specific classes like planar or bipartite graphs [cite: 3, 10]. The edges \(E\) represent variables. The presence of self-loops and parallel edges is invariably permitted [cite: 10, 11].
2. **\(\mathcal{F}\)** is a set of signatures (constraint functions) [cite: 3, 10]. Each signature \(f \in \mathcal{F}\) of arity \(k\) is a mapping from \(\{0, 1\}^k \to \mathbb{C}\), representing a local constraint over the boolean domain [cite: 10, 11]. The codomain can be restricted to non-negative reals, algebraic reals, or expanded to arbitrary complex numbers [cite: 6].
3. **\(\pi\)** is an assignment function that maps each vertex \(v \in V\) to a signature \(f_v \in \mathcal{F}\) of appropriate arity matching the degree of \(v\) [cite: 6, 10].

A configuration (or assignment) \(\sigma\) is a mapping from the edge set \(E\) to the domain \(\{0, 1\}\). For a vertex \(v\), let \(\sigma|_{E(v)}\) denote the restriction of the assignment \(\sigma\) to the incident edges of \(v\). The **Holant sum** (or partition function) of the signature grid is defined as the sum over all possible assignments of the product of the evaluations of the vertex signatures:

\[ \text{Holant}(\Omega) = \sum_{\sigma: E \to \{0,1\}} \prod_{v \in V} f_v(\sigma|_{E(v)}) \] [cite: 6, 7, 8]

The computational problem, denoted as \(\text{Holant}(\mathcal{F})\), asks to compute \(\text{Holant}(\Omega)\) given an input signature grid \(\Omega\) [cite: 3, 8].

### Bipartite Holant Problems and Tensor Representations
A critical structural variant is the bipartite Holant problem, denoted as \(\text{Holant}(\mathcal{F} \mid \mathcal{G})\) [cite: 1, 3, 12]. In this formulation, the underlying graph \(H = (U, V, E)\) is bipartite. The vertices in \(U\) (the left-hand side, or LHS) are assigned signatures strictly from the set \(\mathcal{F}\), while the vertices in \(V\) (the right-hand side, or RHS) are assigned signatures strictly from the set \(\mathcal{G}\) [cite: 3, 12, 13].

This bipartite structure translates elegantly into tensor algebra. Signatures in \(\mathcal{F}\) are mathematically treated as row vectors, or **covariant tensors**, whereas signatures in \(\mathcal{G}\) are treated as column vectors, or **contravariant tensors** [cite: 1, 3, 5, 12]. This covariant and contravariant distinction is vital for applying basis transformations in holographic algorithms [cite: 3, 5, 12]. 

The #CSP framework can be rigorously defined as a specialized bipartite Holant problem where the LHS signature set \(\mathcal{F}\) consists entirely of EQUALITY signatures of varying arities, denoted as \(=_k\) [cite: 1, 5, 13]. Mathematically, \(\text{#CSP}(\mathcal{F}) \equiv_T \text{Holant}(\text{EQ} \cup \mathcal{F})\) [cite: 13].

### Symmetric vs. Asymmetric Signatures
A signature is **symmetric** if its output depends exclusively on the Hamming weight of its input—that is, the number of 1s in the edge assignment \(\sigma|_{E(v)}\)—rather than the specific permutation of the variables [cite: 6, 7]. A symmetric signature of arity \(k\) can be concisely represented by a vector \([x_0, x_1, \dots, x_k]\), where \(x_i\) is the value of the function when exactly \(i\) of its inputs are assigned the value 1 [cite: 8]. Symmetric functions already capture most of the mathematically interesting combinatorial problems and physical system models [cite: 7].

For example, counting independent sets can be formulated using the symmetric binary NAND signature \([cite: 6]\) [cite: 8]. Counting perfect matchings relies on the EXACT-ONE signature \([0, 1, 0, \dots, 0]\) [cite: 2, 6]. Conversely, **asymmetric signatures** do not possess this permutation invariance, increasing the complexity of classifying the problem space significantly [cite: 8, 14, 15].

## Holographic Algorithms and Reductions

The mathematical power of the Holant framework is inextricably linked to **holographic algorithms**, a concept introduced by Valiant to identify new polynomial-time solvable counting problems [cite: 6, 9, 16]. Holographic algorithms rely on the principles of quantum computation-inspired linear algebra to transform the computational basis of a counting problem, thereby revealing hidden tractability [cite: 6].

### Basis Transformations and Invariance
The core mechanism of a holographic reduction is a basis transformation applied to the edge variables of the signature grid [cite: 5]. Let \(T \in \text{GL}_2(\mathbb{C})\) be a non-singular \(2 \times 2\) matrix over the complex numbers [cite: 1, 5]. We can use \(T\) to transform the signatures in a bipartite Holant problem without altering the overall Holant sum.

Given a bipartite signature grid \(\Omega = (H, \mathcal{F} \mid \mathcal{G})\), we can apply the transformation matrix \(T\) to the edges. By the rules of tensor transformation, the contravariant tensors (column vectors in \(\mathcal{G}\)) are multiplied by \(T^{\otimes k}\), where \(k\) is the arity of the signature [cite: 1, 12]. Conversely, the covariant tensors (row vectors in \(\mathcal{F}\)) are multiplied by \((T^{-1})^{\otimes k}\) [cite: 1, 12]. 

If we construct a new signature grid \(\Omega'\) where the LHS signatures are replaced by \(\mathcal{F}' = \mathcal{F} (T^{-1})^{\otimes k}\) and the RHS signatures are replaced by \(\mathcal{G}' = T^{\otimes k} \mathcal{G}\), the fundamental theorem of holographic algorithms guarantees that the partition function remains perfectly invariant:
\[ \text{Holant}(\Omega) = \text{Holant}(\Omega') \] [cite: 5, 12].

This invariant property establishes a computational equivalence between the two problem spaces. Consequently, if one set of signatures is known to be tractable, any set of signatures that can be holographically transformed into it is also tractable [cite: 1]. We say that \(\mathcal{F}\) is \(\mathcal{C}\)-transformable if there exists a matrix \(T\) such that applying \(T\) maps the functions of \(\mathcal{F}\) into the known tractable class \(\mathcal{C}\) [cite: 1]. 

### Matchgates and Planar Graphs
Valiant's original holographic algorithms were heavily reliant on **matchgate tensors** and restricted to planar graphs [cite: 16, 17]. Matchgates are specialized graph gadgets where the partition function corresponds precisely to the counting of perfect matchings, which can be evaluated in polynomial time on planar graphs using the Fisher-Kasteleyn-Temperley (FKT) algorithm [cite: 16]. By applying a holographic reduction, complex, seemingly intractable non-matching problems on planar graphs can be transformed into a planar perfect matching problem, rendering them solvable in polynomial time [cite: 3, 17].

### Gadget Construction and Polynomial Interpolation
In addition to basis transformations, proving Holant dichotomies requires sophisticated techniques for building reductions between different function sets to prove #P-hardness [cite: 9].
*   **Gadget Construction:** A signature from \(\mathcal{F}\) at a vertex is treated as a basic realizable function [cite: 9]. By connecting multiple vertices together and marginalizing over the internal edges, researchers can synthesize new signatures, known as macroscopic signatures or F-gates [cite: 3, 8]. If \(\text{Holant}(\mathcal{F} \cup \{g\})\) is #P-hard, and \(g\) can be realized as an F-gate using only signatures from \(\mathcal{F}\), then \(\text{Holant}(\mathcal{F})\) must inherently be #P-hard [cite: 3].
*   **Polynomial Interpolation:** Initiated by Valiant and further developed by Vadhan, Dyer, and Greenhill, polynomial interpolation allows complexity theorists to simulate the presence of a specific signature by evaluating the Holant sum across multiple carefully constructed modified grids and interpolating the desired value algebraically [cite: 3, 5, 9]. Once unary functions can be interpolated, hardness results from restricted frameworks can be lifted to general frameworks [cite: 3].

## Classifications of Holant Problems: The Sub-Frameworks

Due to the immense mathematical difficulty of proving a single dichotomy theorem for every conceivable arbitrary set of signatures, researchers have structured their approach by classifying Holant problems across several dimensions: the availability of auxiliary functions, the structural properties of the signatures (symmetric vs. asymmetric), and the algebraic domain of the function outputs (non-negative real, real, or complex) [cite: 7, 9].

### The Holant* Framework
The **Holant\*** (Holant-star) framework represents the most computationally permissive setting. In \(\text{Holant}^*(\mathcal{F})\), it is assumed that the set of all possible unary signatures, denoted as \(\mathcal{U}\), is freely available for use at any vertex [cite: 3, 8, 12]. Mathematically, \(\text{Holant}^*(\mathcal{F}) = \text{Holant}(\mathcal{F} \cup \mathcal{U})\) [cite: 7, 8, 12].

The unrestricted availability of unary functions is a massive analytical advantage. Unary functions allow researchers to "break" edges in the gadget constructions, isolating variables, and synthesizing a vast array of macroscopic signatures [cite: 7]. This flexibility made \(\text{Holant}^*\) the logical starting point for Holant dichotomies. Cai, Lu, and Xia successfully established a complete dichotomy theorem for \(\text{Holant}^*(\mathcal{F})\) for arbitrary complex-valued symmetric constraint functions [cite: 3, 5, 8].

The dichotomy for \(\text{Holant}^*\) states that the problem is computable in polynomial time if and only if the signature set falls into one of a few highly specific tractable classes (such as degenerate signatures, arity \(\le 2\) signatures, or holographic transformations of Fibonacci gates); otherwise, it is robustly #P-hard [cite: 3, 5, 8]. This dichotomy also paved the way for resolving complex-valued boolean #CSP, as #CSP can be reduced from \(\text{Holant}^*\) [cite: 8].

### The Holant^c Framework
A more restrictive, yet practically compelling framework is **\(\text{Holant}^c\)**. In this framework, only two specific unary functions are assumed to be freely available: the constant zero function (IS-ZERO) \(\delta_0 = [cite: 6]\) and the constant one function (IS-ONE) \(\delta_1 = [cite: 6]\) [cite: 6, 7, 11, 12]. 

These are frequently referred to as "pinning functions" because they allow the algorithm designer to permanently fix a specific edge (variable) to a boolean constant of 0 or 1 [cite: 3, 6, 12]. This mimics the behavior found in many natural counting problems and standard #CSP instances where inputs can be hardcoded [cite: 3, 12]. 

Proving a dichotomy for \(\text{Holant}^c\) is significantly more challenging than for \(\text{Holant}^*\) due to the loss of arbitrary unary functions for gadget construction [cite: 3]. However, researchers systematically leveraged the \(\text{Holant}^*\) dichotomy as a "launching station." Through intensive polynomial interpolation, they demonstrated that under certain conditions, the availability of \(\delta_0\) and \(\delta_1\) is sufficient to interpolate all other unary functions, thereby reducing the \(\text{Holant}^c\) problem to a known \(\text{Holant}^*\) problem [cite: 3]. Complete dichotomies have been achieved for \(\text{Holant}^c\) with real-valued symmetric functions [cite: 3, 12], and subsequently expanded to complex-valued functions [cite: 7, 11, 18].

### The Holant+ Framework
Recently, an intermediate framework known as **\(\text{Holant}^+\)** was formalized, directly inspired by concepts from quantum computation and entanglement [cite: 6]. In \(\text{Holant}^+(\mathcal{F})\), four specific unary signatures are freely available: \(\Delta_0 = [cite: 6]\), \(\Delta_1 = [cite: 6]\), \(\Delta_+ = [cite: 6]\), and \(\Delta_- = [1, -1]\) [cite: 6, 11]. The inclusion of \([cite: 6]\) and \([1, -1]\) corresponds to quantum superposition states. The \(\text{Holant}^+\) dichotomy was fully resolved and utilized to elegantly streamline the final proofs of the full complex-valued \(\text{Holant}^c\) dichotomy [cite: 6].

### The General Holant Framework
The ultimate goal of this subfield is a comprehensive dichotomy for the **general Holant framework**—that is, \(\text{Holant}(\mathcal{F})\) without the assumption of *any* freely available auxiliary functions [cite: 7]. In this raw setting, the lack of freely available equality or unary functions makes algorithmic reductions incredibly difficult, often requiring massive, computationally assisted gadget discoveries [cite: 7]. 

Significant milestones have been achieved in this regard. A dichotomy for the general Holant framework was proven where all constraints are real-valued symmetric functions [cite: 7]. This real symmetric setting captures the vast majority of physically and combinatorially relevant models, such as perfect matchings, independent sets, and vertex covers [cite: 7]. Progress toward a unified complex-valued general Holant dichotomy has been steady, heavily relying on classifications of Eulerian orientations, which will be discussed in detail below [cite: 11, 13].

## Specific Tractable Families of Constraint Functions

Across the various Holant dichotomies, the criteria for tractability generally converge on a few specific families of mathematical signatures. If a signature set \(\mathcal{F}\) (or its holographic transformation) belongs entirely to one of these families, the partition function can be computed in polynomial time.

**Table 1: Primary Tractable Categories in Holant Dichotomies**
| Category | Mathematical Description | Mechanism of Tractability |
| :--- | :--- | :--- |
| **Arity \(\le 2\)** | Signatures taking at most two boolean inputs. | Reduces naturally to easily computable graph properties like matrix traces or simple path counting [cite: 4, 5, 7]. |
| **Degenerate (Product)** | Signatures that can be expressed as a tensor product of unary functions (e.g., \(\lambda[x,y]^{\otimes k}\)). | Variables act entirely independently; the Holant sum cleanly factorizes into a product of local independent sums [cite: 12]. |
| **Affine** | Signatures corresponding to the indicator functions of affine subspaces over \(\mathbb{F}_2\). | Can be evaluated rapidly using Gaussian elimination over the field of two elements [cite: 2, 4, 7]. |
| **Fibonacci Gates** | Signatures whose values satisfy a specific second-order linear recurrence relation. | Holographically transformable into matchgate tensors, solvable via FKT perfect matching algorithms [cite: 1, 12]. |
| **Vanishing** | Signatures whose properties result in exponential cancellations in tensor spaces. | Under specific parity conditions, the global sum perfectly cancels out to zero or a trivial value [cite: 3, 4]. |

### Fibonacci Gates and Holographic Algorithms
The most mathematically surprising tractable family discovered during the classification of Holant problems was the class of **Fibonacci gates** [cite: 5, 18]. A symmetric signature \(f = [f_0, f_1, \dots, f_k]\) is defined as a Fibonacci signature if there exists a constant \(c\) such that the recurrence relation \(f_i = c f_{i-1} + f_{i-2}\) holds for all valid \(i\) [cite: 1]. For instance, the parity function \([a, b, a, b, \dots]\) is a specialized Fibonacci function where \(c = 0\) [cite: 1].

In the complex domain, a generalized Fibonacci signature can be expressed algebraically as \(x_k = A \alpha^{k-1} + B \alpha^k\) [cite: 12]. If a parameter \(\alpha = \pm i\) (the imaginary unit), the signature satisfies \(x_{k+2} = \pm 2i x_{k+1} + x_k\) [cite: 12]. Cai, Lu, and Xia proved that if all node functions in an unweighted graph are Fibonacci functions with identical parameters, the partition function can be computed exactly in polynomial time [cite: 1, 12].

The underlying mechanism for this tractability is that Fibonacci gates can be holographically transformed into matchgate tensors [cite: 12, 18]. By employing a specific non-singular transformation matrix \(T\), the complex Fibonacci relationships map directly onto the FKT algorithm's requirements for counting planar perfect matchings [cite: 12]. If arbitrary edge weights are introduced, or if different functions utilize conflicting Fibonacci parameters, the problem typically collapses back into #P-hardness, though fully polynomial-time randomized approximation schemes (FPRAS) and deterministic FPTAS can sometimes be constructed for these weighted variants [cite: 1].

### Affine and Vanishing Signatures
Affine signatures represent constraints that can be defined by systems of linear equations over the boolean field \(\mathbb{Z}_2\) [cite: 7]. Because systems of linear equations can be solved efficiently using Gaussian elimination, Holant problems strictly composed of affine signatures avoid exponential blowup [cite: 19]. 

Vanishing signatures represent a more esoteric complex-valued phenomenon [cite: 4]. Because Holant sums allow for negative and complex weights, it is possible for massive ensembles of configurations to perfectly destructively interfere with one another [cite: 3]. Vanishing signatures are meticulously structured symmetric constraint functions that, when combined with specific binary functions, guarantee that the global Holant sum cancels itself out entirely. The complete characterization of all symmetric vanishing signatures was an essential breakthrough required to finalize the complex-valued \(\text{Holant}^*\) dichotomy [cite: 4].

## The Eulerian Orientation (#EO) Problem and Odd-Arity Dichotomies

As researchers pushed toward a fully generalized dichotomy for complex-valued Holant problems over the boolean domain without freely available auxiliary functions, they encountered a formidable mathematical roadblock: the **Eulerian Orientations** problem [cite: 13].

### Definition and Statistical Mechanics Connection
An Eulerian orientation of an undirected graph \(G\) is an assignment of a direction to each edge such that for every vertex, the number of incoming edges (in-degree) is exactly equal to the number of outgoing edges (out-degree) [cite: 13]. The problem of counting weighted Eulerian orientations is denoted as **#EO** [cite: 10, 13]. 

In the language of the Holant framework, #EO is defined by assigning an Eulerian orientation signature to each vertex and treating the edges as orientation variables [cite: 10, 13]. 

#EO holds immense significance beyond theoretical computer science; it is deeply entrenched in statistical physics [cite: 13]. The computation of #EO on bounded regular graphs is entirely equivalent to computing the partition function of **ice-type models** [cite: 13]. Specifically, when the underlying graph is a finite region of a 4-regular square lattice, computing #EO is identical to evaluating the partition function of the classical **six-vertex model**, a foundational construct in the study of thermodynamic phase transitions [cite: 10, 13]. Extending this to models where Eulerian constraints are softly broken yields the eight-vertex model [cite: 13].

### The FPNP versus #P Dichotomy
For nearly fifteen years, resolving the complexity classification of #EO was considered the most significant bottleneck to a comprehensive general Holant dichotomy [cite: 10, 13]. In 2024 and 2025, groundbreaking papers by Meng, Wang, Xia, and Zheng finally provided a complete complexity dichotomy for #EO [cite: 11, 13, 20].

Unlike previous Holant dichotomies that separated problems strictly into P (polynomial time) and #P-hard, the #EO dichotomy introduced a subtle shift in the tractability baseline, establishing an **\(\text{FP}^{\text{NP}}\) vs. #P dichotomy** [cite: 10, 11, 13]. 
*   **\(\text{FP}^{\text{NP}}\)** represents the class of function problems solvable by a deterministic polynomial-time Turing machine that has access to an oracle for an NP-complete problem [cite: 10, 11]. 
*   **#P-hard** remains the highest level of counting intractability.

The theorem dictates that for any signature set \(\mathcal{F}\) defining an #EO problem, the problem is either solvable in \(\text{FP}^{\text{NP}}\) or it is strictly #P-hard [cite: 13]. While \(\text{FP}^{\text{NP}}\) is computationally harder than standard P, it is theoretically well-separated from #P (assuming the polynomial hierarchy does not collapse at the second level), thus maintaining the spirit of a true dichotomy separating polynomial-hierarchy tractable problems from #P-hard counting [cite: 10, 11].

The analysis of #EO problems requires analyzing pure signatures, closure properties under gadget construction, and rebalancing signatures [cite: 20]. Signatures possessing the ARS property (Affine, Real, Symmetric) form a crucial subclass analyzed in this domain [cite: 13, 17].

### The Decomposition Lemma and Odd-Arity Signatures
The resolution of the #EO dichotomy immediately acted as a skeleton key for unlocking broader Holant dichotomies. A pivotal mathematical mechanism derived from this research is the **generalized Decomposition Lemma** for complex-valued Holant over the boolean domain [cite: 10, 11, 17, 21].

The Decomposition Lemma asserts a rigorous structural constraint on signatures: either a signature can be successfully decomposed and derived from its tensor product with other signatures (facilitating reductions), or the resulting Holant problem's complexity collapses to an \(\text{FP}^{\text{NP}}\) classification [cite: 10, 17, 21]. This lemma is hailed as a powerful universal method for building reductions in complex-valued Holant frameworks [cite: 10, 17, 21].

By leveraging the Decomposition Lemma and the #EO dichotomy, researchers achieved a monumental milestone in 2025: **A full complexity dichotomy for complex-valued general Holant on the boolean domain, provided the signature set contains at least one non-trivial signature of odd arity** (denoted as \(\text{Holant}^{\text{odd}}\)) [cite: 10, 11, 17, 21]. The theorem succinctly states: Let \(\mathcal{F}\) be a set of signatures containing a non-trivial signature of odd arity. Then \(\text{Holant}(\mathcal{F})\) is either in \(\text{FP}^{\text{NP}}\) or it is #P-hard [cite: 10, 11].

## Extensions of the Holant Framework

While boolean domains and exact counting encompass the core of Holant research, the framework's flexibility has driven expansion into several orthogonal mathematical territories.

### Higher Domain Sizes
The boolean domain restricts variables (edges) to \(\{0, 1\}\). Extending Holant to higher domains \(\kappa \ge 3\) increases the complexity of tensor spaces dramatically. Dichotomy theorems have been explored for domain size 3. Notably, Cai, Lu, and Xia established a dichotomy theorem for \(\text{Holant}^*\) with a single ternary symmetric function over a domain of size 3 [cite: 18, 22, 23]. This research proved the existence of unexpected tractable families on larger domains and initiated the use of holographic reductions in higher-dimensional tensor spaces, serving as the foundational algorithmic technique for subsequent non-boolean Holant classifications [cite: 18, 22]. Furthermore, non-negative ternary signatures on 3-regular bipartite graphs have also been classified, with tractability hinging on Affine-transformability or Product-transformability [cite: 14].

### Parameterized Holant Problems (p-Holant)
In the realm of fine-grained and parameterized complexity, Radu Curticapean introduced the parameterized Holant framework (\(\text{p-Holant}\)) in 2015 [cite: 2, 24]. This framework analyzes counting problems based on a structural parameter \(k\), seeking Fixed-Parameter Tractable (FPT) algorithms. \(\text{p-Holant}\) encompasses the counting of edge-colorful \(k\)-matchings, graph-factors, and bounded-weight subgraphs [cite: 2, 24].

Research into symmetric signatures in \(\text{p-Holant}\) revealed a striking **trichotomy**, fundamentally categorizing problems into three exhaustive tiers [cite: 2, 24]:
1.  **FPT-near-linear time:** Solvable in \(f(k) \cdot \tilde{\mathcal{O}}(|x|)\). All constant signatures fall into this category.
2.  **FPT-matrix-multiplication time:** Solvable in \(f(k) \cdot \mathcal{O}(n^\omega)\), where \(\omega\) is the matrix multiplication exponent. However, these cannot be solved in near-linear time unless the Triangle Conjecture fails.
3.  **#W[cite: 6]-complete:** Intractable in the parameterized sense. No significant algorithmic improvement over brute-force search is possible unless the Exponential Time Hypothesis (ETH) collapses [cite: 2, 24].

This classification illuminated a surprising gap in the complexity landscape: not only is every instance rigidly separated into FPT or #W[cite: 6]-complete, but every single FPT instance can be solved at worst in matrix-multiplication time [cite: 2].

**Table 2: The Parameterized Holant (p-Holant) Trichotomy** [cite: 2, 24]
| Classification Tier | Time Complexity | Hardness Assumption |
| :--- | :--- | :--- |
| Tier 1: Near-Linear | \(f(k) \cdot \tilde{\mathcal{O}}(|x|)\) | Unconditional Tractability |
| Tier 2: Matrix-Multiplication | \(f(k) \cdot \mathcal{O}(n^\omega)\) | Bounded by Triangle Conjecture |
| Tier 3: Parameterized Intractable | \(\Omega(n^{f(k)})\) | #W[cite: 6]-complete; ETH violation |

### Quantum Information Theory and Entanglement
The mathematics of holographic algorithms—relying on tensor products, basis transformations, and state spaces—is practically isomorphic to the mathematics of quantum mechanics. Miriam Backens demonstrated that quantum information theory, specifically the study of **quantum entanglement**, can be explicitly employed to explain existing Holant results and derive new dichotomies concisely [cite: 6]. 

By treating signatures as multi-qubit quantum states, the tractability of a constraint function becomes intrinsically linked to its degree of quantum entanglement. Highly entangled signature states resist decomposition, leading to #P-hardness, whereas unentangled (product) states correspond to tractable degenerate Holant instances. This quantum perspective directly inspired the formulation and resolution of the \(\text{Holant}^+\) dichotomy [cite: 6, 17].

***

## Methodological Disambiguation: Epistemological Occurrences of "T-60" and Dichotomies in Multidisciplinary Contexts

Because algorithmic search queries inherently function through string matching, the conjunction of "T#60", "Holant", and "dichotomy" surfaces a highly distinct cross-section of unrelated academic and industrial literature. To ensure complete epistemological rigor, this report systematically disambiguates these occurrences, contrasting their usage with the theoretical computer science framework detailed above. 

**Table 3: Multidisciplinary Disambiguation of Query Nomenclature**
| Field of Study | Terminology | Contextual Meaning |
| :--- | :--- | :--- |
| **Theoretical Computer Science** | Holant Dichotomies | Classifying graph counting problems as P or #P-hard. |
| **Acoustic Physics** | T60 | Reverberation time required for sound to decay by 60 dB. |
| **Mechanical Engineering** | SAF-Holland T-60 | Specific models of heavy-duty truck pintle hooks. |
| **Psychology / Neuroscience** | T > 60 | Statistical threshold on the Conners-3 evaluation scale. |
| **Philosophy / Game Theory** | T=60 Dichotomy | Temporal parameters in optimization and Zeno's Paradoxes. |

### 1. Acoustic Physics and Speech Dereverberation: The T60 Parameter
In acoustics, **T60** is a foundational parameter defining the reverberation time of a room—specifically, the time required for a sound pressure level to decay by exactly 60 decibels after the sound source has ceased emitting [cite: 25, 26].

Modern approaches to speech dereverberation heavily rely on estimating the acoustic environment's T60 value. Recent models utilize Deep Neural Networks (DNNs) that treat T60 estimation as a multi-task framework, simultaneously executing T60 classification and regression directly from reverberant audio signals [cite: 25, 26]. The DNN structures decompose Room Impulse Responses (RIRs) into direct-early components and late reverberations across varying simulated T60 times (e.g., \(T60 = 0.3s, 0.6s, 0.9s\)) [cite: 25, 26]. Furthermore, advanced dereverberation techniques employ the **Complex Ideal Ratio Mask (cIRM)**, processing both the magnitude and phase responses in the imaginary and real domains, yielding substantial improvements in Perceptual Evaluation of Speech Quality (PESQ) scores across different T60 environments [cite: 25, 26].

### 2. Mechanical Engineering and Commercial Transport: SAF-Holland T-60 Series
The string "Holland" paired with "T-60" overwhelmingly references **SAF-Holland**, a premier global manufacturer of commercial vehicle coupling systems. SAF-Holland produces a highly specific line of heavy-duty pintle hooks bearing the T-60 designation, engineered for medium to heavy-duty on/off-road towing [cite: 27, 28, 29, 30].

The two primary mechanical dichotomies in this series are rigid-mount versus swivel-mount hooks:
*   **PH-T-60-AOL-8 (Rigid Mount):** A forged steel alloy rigid hook designed for over-the-road towing. It boasts a maximum vertical load of 6,000 lbs and a Maximum Gross Trailer Weight (MGTW) of 30,000 lbs [cite: 28, 29].
*   **PH-T-60-AOS-L-8 (Swivel Mount):** A split-flange mounted, swivel-style hook designed to allow for maximum articulation on uneven off-road terrain. It has a lower maximum vertical load of 3,600 lbs and an MGTW of 18,000 lbs [cite: 27, 30, 31]. 
Both assemblies feature Black Armour corrosion protection and heat-treated latches, representing a functional, mechanical dichotomy of load distribution systems [cite: 28, 30]. Additionally, troubleshooting manuals for SAF-Holland fifth wheels frequently denote specialized lock pins like the KD-T-60-AHLH or cotter pins for XB-T-60 assemblies [cite: 32, 33].

### 3. Cognitive Psychology and Medical Threshold Dichotomies
In medical and psychological research, statistical thresholds naturally enforce diagnostic dichotomies. For example, in fMRI studies distinguishing children with Reading Disabilities (RD) combined with Attention-Deficit/Hyperactivity Disorder (ADHD), clinical inclusion relies on the Conners-3 parent-report scale. A strict clinical dichotomy is enforced where elevated ADHD symptoms are statistically categorized by a T-score threshold of **\(T > 60\)**, separating the RD+ADHD group from the RD-only control group (\(T < 60\)) [cite: 34]. Similarly, in neural network modeling of alexia (reading impairment) following stroke, reading accuracy metrics naturally yield statistical t-values across sample sizes, such as a significance of \(t(60) = 2.6\) for high-frequency consistent word accuracy [cite: 35].

### 4. Dynamical Systems, Paradoxes, and Temporal Optimization (T=60)
The variable \(T=60\) acting as a threshold appears frequently in the modeling of complex systems and paradoxes:
*   **Zeno's Dichotomy Paradox:** In philosophical mathematics, the Achilles and the Tortoise paradox is fundamentally linked to the "dichotomy paradox" of infinite spatial subdivision. Discussions surrounding this paradox often utilize theoretical bounding intervals, such as evaluating computer processing bounds at exactly \(t=60\) seconds, examining the asymptotic approach of \(t = 60 - 2^{-u}\) [cite: 36].
*   **Quantum Optimization (MaxCut):** In Adiabatic Quantum Computing (AQC) applied to the MaxCut graph problem, researchers identified that evaluating the eigenvalues of a normalized Laplacian matrix allows them to estimate total algorithm run-times. Specifically, empirical evidence showed that running AQC for \(T=50\) or **\(T=60\)** seconds achieves a uniformly high probability of success for specific problem instances [cite: 37].
*   **Vestibular Physiology:** Mathematical models reconciling the dichotomy between active and passive head rotations (and the brain's perception thereof) evaluate canal after-effects triggered precisely at \(t=60\) seconds following sustained constant-velocity rotations [cite: 38].
*   **Traffic Modeling (StarLogo):** In constructionist learning research utilizing the StarLogo simulation environment, students observing decentralized emergent behavior discovered that localized radar traps caused cascading traffic jams perfectly modeled at temporal ticks \(t=60\) and \(t=70\) [cite: 39].

***

## Conclusion

The pursuit of complexity dichotomies within the Holant framework represents one of the most elegant and mathematically rigorous endeavors in modern theoretical computer science. By abandoning the implicit equality constraints of traditional #CSP and adopting the language of covariant and contravariant tensors, the Holant problem provides a universal language for local constraint-based counting on graphs. 

Through the ingenious application of holographic reductions, polynomial interpolations, and quantum entanglement models, researchers have successfully mapped out the borders of tractability. They have proven that, modulo the collapse of established complexity hierarchies, counting problems parameterized by symmetric signatures—and increasingly, asymmetric and complex-valued signatures—adhere strictly to dichotomous boundaries, bypassing Ladner's intermediate wilderness. 

The recent breakthroughs surrounding the Eulerian Orientations (#EO) problem and odd-arity signatures have shifted the paradigm, revealing that the boundary between tractable and intractable counting is governed by the \(\text{FP}^{\text{NP}}\) class. As computational theory continues to evolve, the methodologies developed to solve Holant dichotomies will undoubtedly continue to influence quantum algorithm design, statistical mechanics, and our fundamental understanding of computational hardness.

**Sources:**
1. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNPlYYYYR2ZWB57y2_Zg3up7YZ7NJoFjBKk0JuMA3UkKdVCBLxwq3WCrRMuw0BcEw44VenhwJ10mKKjCh9g0aMxl-zKlOe__TqEUkpD1Gh2ROt6KNks3-3coVI7wrSSxvjihdkgg5vT1CfXdZDYikau0Y-G3hOnQkp5LSEvz_wvY4FtcHM3zjCzrLdqSIp96qcC_EZOSAuDDHzoTPTpgclhg==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxmERY1Y_ayz1pBi5xl-4bgt3ipjy6sBaA6LAedBIo5F_tCIh5D2ar6zZyEpOpuFukpnNiGiEH0oSB3aY11fxaFxrI6YCXisYUDwjS3C5Yg43TUk_W)
3. [wisc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJUMs_vOA1pQyI68mdlPd987Ao8x5RkVc7qiY8hy7UrsZCnxqn62XS93GuYDkOpnUy_syzeciRYwdQMezvB9OR49zvk01uVAHM6LTx1q60Lxc3s5bzpm67IM3eaOqCblmThrKIHA==)
4. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHToGNEkhf4v4Ggx2QtFSUK5kQFHRXJeoDwcaa-Pllsiptqixjsp_QK0wv5FDNMAubS4CLz9ch3O6n7Ky6VSa7rgMFuDzU0r6eS1gmMladZ7BxZNijFR2gAKt1STZ2e9ee2NA==)
5. [pinyanlu.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0ggrcDiAKMaPzYlytDO0L2cgTPhv_W2nHyL5665In5Jnw_73QJKaEuwbUDcWBagMqQaW6I1e-T3dVmp0QSYwW3YV2_TEfdHl9_jPJNxlAVu3_tZiCjIpFGA3YbXFyAIUb-Xq6ZMECLzaf_NQ0s5_mzb-mJEkAhaUY5tgcfztFZr49Yj_k95QqrMr8sw==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1lp_BAbJXfy9Xl7wo8F-Bpm6swdrVxyNrwlcqqk0eYLVIzapi6CkBVo7ksPsimpyNXxHz7HncjGKMb6N9QonnlqEcreK95UFgy1fSeTqCLG74DDVD)
7. [pinyanlu.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQwTD7m4AbbDfUMK4flkHK54feZ1XbGTnzDwwobygSpYF4tEhl1XBl0AGNy--lYLqF8IBflRG7LEieTIkJ7m17Nlg_BXLp-994vp1_HaehzIpXul7rfXGJkpGGJfdZdHpXwSPMKX5op9jMFvJYxZPK1VwF-YWL8a8Dv_eanb_6oechBpYcW6Kl8TO0oHOygM5sSw==)
8. [wisc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZ64ihRalE241WKhb7OxDnYhPMS9ZOWekqtbJHghtler5iKRaVccGigxJk6E6S_258RheyVcJPcFwf7WH44jzrXgl1tXPR33GLM14a3E1M6AuxYAePmgDicaq3_kqwe3bZY9w3-lQ9SM5hV1xtSCXzPzqzyvLVPgYQS_b8fQ==)
9. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzX7I8RqFHIoXO0TXYlZWchC-2k5Vu8aCQ1siSM7SYgzO-IBldOsUId3C_HdLHZw0Hi4WsK37X20Qns3z8CjURlHpiB-NfhvTVPj15aG76jFOpQ9YY8Lse_S_eFJRpiNZoNHehaduo4T4t)
10. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFH4CHHvWI-0dvs0dKU200x6p0tCyYC1wLcG243nR0URKLQHXX7Oc6H8XGa7YzGR_4DZ68hqRzPy4kNaihiaQYLyCOd3swJYosZCyJXpnn1PwZenlbjnFqLAzP30YP5puHxOtJz4g-6BuvS0kIYMiOwPRZU-Mmdy0eRsCBqp6hw8xFwFI5ClUu9Cajk18m6K7oz9crE15GaIndH4gQZ9HUd65DwXQ=)
11. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGp88oygE2nq7I9MiJl_vjb2nolY8GVmVgoHWStRko_0kMs3nn1VgFkJPhPP-ELGkY0bKY199qnQxQZEm2ToF71pfN462osApt1P_33lxO-BerdouBBPDz4-lG6Q5U4SXUgrjjSTFx_vbNHlGhVmWqEdhZyynrxlTf_biOnBEeZ2cCQL3gtmA6XqZ94ltmvIlpF6lXgJW9t_zJNB5WTLEI=)
12. [wisc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaMYO4ZJs8OKg-5gIntNHPC5h3yf3-LQYERLwFggmfiOQ7W_Uo0ccjkpZrhYDJ4gEdQhZHxzyYLNgQbihey4M4TpCalh6vPAThq_HggN80RW_8LTtLM0AfrA5qnLDY_XyMPPXkmCjx)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHkhDGl9cq0kNZPA5rzQhNxS338kzJGI3jbp-g702VQ6t_hAe2cXoTWb0K3Q_97mYPq-OeY034UMAm2AnvwqntTyVAn40-w6nx2HTIg6zDrZdlMLof)
14. [proquest.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECj1OvguJmWL3K0DFFwnj047mXBqTc5jl9E0Irlfuk2-0Z9QS1vxKQx2DIQ5iGxrZaMtSa95jGNvuAHFVlv5oUSZLidE6KtuqCw2oRFoFgjsJqB0hfn1eIT3tN7_zPdQCS0-NxoLTcz0zcCLNnr57ydLT2lxwfvpum929RXfBSiq5I11E5cEyU4eRFy9e58ECJ47wyC9VOOXhr9g==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9tHKZRRgbtxcqR1AfhKcrZU3zT6PVXLCH0au83kkTJ3l-1jq_FIh-XBruXDKc1-Lv-W_lDxY7P5C_DLLrXbia7XPWIxjxmiwUFFgRAMDu8CXAPnFS)
16. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAPHZPVflypwBYEO0woiah4QY0JKw1_MVbEyK-C2tyDG5_G0-DGYF2ztkgdgsPdqqw0MxGLQJDaofmB-Lgh7hGqEmy_2cpp5E-I0H80VyO-cBPPaG_ipCDBOzGG4K24EBt)
17. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYgJbx-k8DsY2Kbeb83ZlHx41dAmPZa1MK4yqXqyjFX4MJyYtC3P1jM5DiIeGRuE_3YHvoZmVKpB3bfnNpYiF8mii0JF2cNxeBSRn2IreQcgFco8yvySnh8aWrwF80xqqfTUC12x8UYges0yWDJyvBHkzVzeqBOgSAmHw=)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdO0pKLXnD36rqtJSTWFSoDBc-OMu5gmPsqfJ6N-VpalKCQk1xvcs10hrFKjJUhfrpr6VcIN2-_-GDhqQPTNGidsd-4QlyU_x4EzKHKFhYEBZ9F0e61GM9Iawzkki270gc_KQOztSJi0Ob9D-SKipSRXZCiTD4tsSu06xBrFQZoBWf4kJYpc9rP5-nv9cuc2xzBordUOAKSJjvE8VPn0yMI7L6ZLykMC13JwGYubX-GQ==)
19. [acm-stoc.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGY55hMGTeAEh6rrt3fOyQLuidbSAuhKww3ktqQxkVutcxsYb4_iInQbnBFy208laYFTt2BaFYFwjEQKw19IRO_KdskqVGds6YUk_j7vWffmcbptpM5SrBAn3lN)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhcJ52R3b-ZnD31YFIE_xXxBGEw1HcKelwgVv8b3BtXTIUxMajYx6oIGPEBR8gszHKNHa8Uu5BL4Eg2bF64M7_qEDkLoTVnJjh7B2DxaeEOu1g7nqe)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYV0Gn-bRSOOabCKN3-V_FvKx6yr_EiDZNAXyfTnrDu25eHikQwDDIlXVDvjg5dyaEV_BN2KJH_wNtJ70ug9QwuYquGczI0wAgu40kB3XnhcF-VFrT)
22. [researcher.life](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE73mNPwF1Z5H5pOse-pWcTwe5czhDJ-nQfy7wKywMKfr77GjkUfl8_O1HmEx8Kw6AQEYGS6g3UT1Uer2IzPKiE5lnHxUsRTqADYvBiIc0UXDih1Mh2phiYzVXRDhKluV4Tf0kbh8VPKVBwpN3iE3SgYLuhAhSk436vJCnjMnYFwqETYeb2tNgN9bEavnc1KZHoO791Az79UuR8vRITvGxV0CJRhcVmILa7HqnaZR2ScvI=)
23. [dblp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDXX2E2v90335N7ieiZ510z0uTx1Srs4lrBkGJR_H5ChHOcwbu--AlyCMEEfo1MV8865v6UtoOvENmcuzsmqmHnOy72E3aqOanEhYOUH2UPEU=)
24. [ethz.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbl95l8K5vKMohCW_TUDV3CObt2GMVvzmFQ7PY8AQ2d8Hl11boVEuOErQ6sFkfBlCNV91Bryih5BkzJ84_NKN0wwPZXh5XTZ7-o3pamHGFLhaPOIkb1dr-7naKW87_2KHel6SZ5Ls8txUrdb4wFm7Rmo2dJiAdoo85hMArupperUHQNnriy-XivOLIG-vW_qnGq_lweg==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGE0-2VV_9i0wy0rLujfJASMVjJIWLkaAFJv-jCGGjYWaf9rGDteKh4FbwFciI1v7bs7NHjHkW8czm1H1Q_2QIWNGlBAwZynrMc-Y3B-NlvvYk38psv)
26. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfXILzadtXWhxya46y66K5MyeC2poWSM5hjBx1wj-fEDW7raSi518v0KwfWeVHNZFd_AN7_3GPZum0fvLaRbENQ0FlJkplPUWDrexC7bHDrJHQIth0sw2rMHfSoZaF-P6DxgG8N8Q=)
27. [sadlerpowertrain.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5Qo83Mw-8DgnVNA1ocJdJFqfRCaEcNv2njYytoeoK_sRyxhp4K6S2Vhpd2tvGhNtmlyzCorzi9MsKDGAaNLYbnknfxiwDyp7kj2XMaT-_uVi5mc7mX4bquA625iQEva7fOXPR8yyv1Ws4rL-EHie2QYMPKX_6y1XwOOb0HpqQe7ByGDMb0b16PQc=)
28. [safholland.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhvk90BDI8U3c-27CjGYN7u253ol1nxCV7GarTlAbOGj9ff99GmyP95bNs4J6gEX_apJJ5Dbdt7kmxt6gweTTJwxQei-yicuPD4CYnXvGCx0LuS_avV55QILrItJMKfjOQPjQFJn0uNjkq_E1H-WCv)
29. [truckspring.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbD1j3f1YICJcplJrHGS-NoQFRw7IGMxd-SNPrYu9onmGHL6cQM2aSaBIh6A8LoVksbp440_LgmxiJQQep3mLMhRroW3l2-bo0vUVq3IMYzjnsqbAL8vmS8lFULxhhe4vV2niRkJ4vAkbYMSM98nrKcuF5ED32TmfcVJQVWKAX6HxBkSbNAR_i)
30. [safholland.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFl13fHLAUElb7J3Ysk25tYBFFn7RoI4OPH2vIMXa32XiiIHMoEvpxxCuLwTu3Rbw-sbmb5CW5nxfMLLunavhNdz68FTqsSnJVMpyrikgwVYiqovyY6i15gwdICX9RdNOpFJ0Xl3sWFu3YwoJXFK70PDB0=)
31. [anythingtruck.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF41VWuAEmnSkYFKmVd9Cl6iNxLP_2rD6Oz09mEyf60NVCcSevcBlvztLgK-QNhp-TA0dPVzlNLGt9qnfVnFhp3Ff5dz1TQqQIaTtuIGBbXWBByZWkerhMhmqPnFrY7LIkC7b6Ide1kQXpqXY9iLg==)
32. [ebay.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjGQlg3X5kMi2J8GTPuLo8UXl66w6z7JKlxQucFfjhFazqRTx3GcAQdcrLGZRSZ7eqRwsvEg01DHlUiB0m8yK2R0sUihRjiYQtZ44E55fVoHqbNXJQPVIcPtw=)
33. [safholland.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNe6qeHpEZV-T2LlJ-7O_cuXkrKXMDnCR-o1fpRaEZxdAmv8UFL3EpQHRq5jq0bqoJLYooHyA73EMZGPLzrbfuXz8uAWb_BPqqC8Xd9MkR11i3C8BTt82R7IwVgKlMFFS7514YmqGDcSnYZPl06Ax6cVlnYtUepPZl7ORgkLWuzwYkj8yFcBIOqLB6ykF5n-tYgBaDWqRjMXxxccLgMSsKPASCow-fsvOsbQ8Qq6MQJH-bRx8K1oslEv19dt444iSpGdFUIwjp1XQulhWN6V-hhg2kDuu10HedG60LCHG_RMJ-iA7QAFEAUQDwHYw_5OKFJqKQ)
34. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECx0K9y8z0tHNQ2B9eM_wh46jYG9vqGZf6XThArJdmO28NKbuJJZeQkAltZ3jVGUFR1rtHz5eqxW7bm0xxe0bWTdjOHambwhpRVLEPRf-EydFVhIIgorHlK9GtPkiq1hIVaNPvX3RD)
35. [biorxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvZ3w_40AH6XqEuMM9JrkpVXi7F65mjmdVrkFh2jEI72TEa5flWi773fc9wNj8XGVZXPCHht2AX7k5LYV9xmRlO1wTFpH8D8ObQwZuxky5HFnePJF3E2BSTtAv8x7OkvrXVWs4UYuuVN0EycT9JCFfW4Y_SNla)
36. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHi1Bo_lZeaLpfXSfGf9_fOARaa7AbjywvyY_oPZTRNh6YxVWHPaEMzqsneYdF7yU5JutGYivsXcTTLG33uxicod71C5ESD35OwOj8nn_XO_VriZnj4Siy1JI5GgWtfZthrkK_lX8D_gcIFqkFllIWb8933_voKhzXe3V-hsc3lj-A9E9OUR5QD)
37. [unimelb.edu.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEbztcKu1v8cPdqmMZ28tKnBO7dZgVV_SzQB_s4HDI1XGuIgR5d-499RJVgowJ8G9u_e2qZl45EDVtAYHVSteZzJpOxi1yKnm2y_cjuJDuhi_z4XxhjdX17JNVVS1RUKPoCP229l1BCUjO6HJxSgsWyH23lu_DWl7Zrz6-R-m7NCq4VyZTmPd8sgjHmizL3iwNPuQhyak0wHDiwj5waQ-KOhIOfuGSxGXhnmy20uRpPv23QbZZ4GuiNfb4)
38. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHW27Tp6Oe8PY2nv6bl1aSgAC7ws89sRjFcjj7gjpV1-ax214ziNGxRTYPeO7j0IqvWq51h_DYL0FcaJCR8-gGWxVSRHxwTw2f5GC1mkXc2rxjUcXhV3UwnVv_N-WNnstHiFQGyR1U=)
39. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLg9sbyawIrqrIBVRiJCMF5xDVzmaNuKRWpgu9FggzCjK7f0eHYp4oeKRmBjJoBpDENgGtWvZwWGNeaSKKUhP3IRfZPSM0o89VSL4zvtgOLqICI8jEwc4Puaxl1eZ1bhBvBhLZpH86T8PiLyE=)

