# Quasi-symmetric functions + Schur positivity 2024-2026

**Pythia queue id:** 207
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdSMGNQYXQybEFaUFZfdU1QMHVqVGtBcxIXUjBjUGF0MmxBWlBWX3VNUDB1alRrQXM
**Elapsed:** 318s
**Completed at:** 2026-05-21T18:01:42.254619+00:00

---

# Quasi-Symmetric Functions and Schur Positivity: Advances and Breakthroughs (2024–2026)

**Key Points**
*   Research suggests that the intersection of quasi-symmetric functions and Schur positivity remains one of the most vibrant areas in algebraic combinatorics, providing profound insights into representation theory and graph theory.
*   It seems likely that recent unified frameworks, such as "crystal skeletons," successfully bridge classical methodologies like crystal graphs and dual equivalence graphs, offering powerful new tools for proving Schur positivity.
*   The evidence leans toward significant progress in long-standing conjectures, particularly regarding the Stanley-Stembridge conjecture on chromatic symmetric functions, with new signed elementary expansions and symmetry classifications published between 2024 and 2026.
*   Recent classifications in pattern avoidance, particularly concerning symmetric sets of permutations and matchings, have definitively resolved several modern conjectures, highlighting the deep connections between permutation patterns and symmetric functions.
*   Representation-theoretic interpretations, particularly utilizing 0-Hecke modules, have provided critical breakthroughs in understanding the Schur positivity of specialized families like genomic Schur functions and modified Macdonald polynomials.

**Contextual Overview**
The study of symmetric and quasi-symmetric functions serves as a foundational pillar in modern algebraic combinatorics. These functions are not just abstract algebraic objects; they encode profound structural information about mathematical symmetries, permutations, graph colorings, and representation theory. A central question in this field is "positivity": when a function is expanded in a specific mathematical basis (like the Schur basis), are all the resulting coefficients non-negative? When this occurs, the function is said to exhibit Schur positivity, a property that often signals a deeper, hidden algebraic or geometric structure.

**The Shift in Recent Years (2024-2026)**
Between 2024 and 2026, the mathematical community has witnessed a paradigm shift in how Schur positivity is approached. Traditionally, mathematicians relied on isolated combinatorial bijections or specific graph structures. Recently, the focus has shifted toward unifying theories and exhaustive classifications. Breakthroughs include the formalization of crystal skeletons, the exact classification of symmetric pattern-avoiding permutation sets, and novel representation-theoretic models for genomic and chromatic functions. These developments have resolved several standing conjectures while opening new, highly technical avenues for future research.

---

## 1. Introduction to Quasi-Symmetric Functions and Positivity Phenomena

The rich interplay between algebraic combinatorics and representation theory is heavily mediated by the rings of symmetric and quasi-symmetric functions. Positivity questions occupy a central place in this domain: given a naturally occurring symmetric, quasi-symmetric, or polynomial function, mathematicians seek to determine whether it expands with non-negative coefficients in a preferred basis, such as the monomial, elementary, or Schur basis [cite: 1].

### 1.1 The Ring of Symmetric Functions and the Schur Basis
A formal power series \( f \in \mathbb{Z}[x_1, x_2, \dots] \) of bounded degree is defined as a **symmetric function** if it is invariant under any permutation of its variables; that is, \( f(x_{\pi(1)}, x_{\pi(2)}, \dots) = f(x_1, x_2, \dots) \) for any permutation \( \pi \) [cite: 2, 3]. The space of symmetric functions, often denoted \( Sym \), possesses several standard bases, including the monomial (\( m_\lambda \)), elementary (\( e_\lambda \)), complete homogeneous (\( h_\lambda \)), and power-sum (\( p_\lambda \)) bases [cite: 4]. 

However, the most important basis for the vector space of symmetric homogeneous functions is the **Schur basis**, consisting of Schur functions \( s_\lambda \), indexed by integer partitions \( \lambda \) [cite: 2, 5]. Schur polynomials, named after Issai Schur, generalize elementary and complete homogeneous symmetric polynomials and form a linear basis for the space of all symmetric polynomials [cite: 6]. 

A symmetric function is called **Schur-positive** if all coefficients in its expansion into the Schur basis are non-negative integers [cite: 2, 5]. This property is highly sought after because it reflects a deep connection with representation theory: a symmetric function is Schur-positive if and only if its corresponding class function (via the Frobenius characteristic map) is a proper character of a finite-dimensional irreducible representation of the symmetric group \( S_n \) or the general linear group \( GL_n \) [cite: 1, 5]. For example, the skew Schur functions \( s_{\lambda/\mu} \) expand positively into ordinary Schur functions, with the coefficients being the celebrated Littlewood-Richardson coefficients [cite: 6].

### 1.2 Quasi-Symmetric Functions and Gessel's Fundamental Basis
The ring of **quasi-symmetric functions**, denoted \( QSym \), is a broader class of functions that generalizes symmetric functions. A formal power series \( g \) of bounded degree is quasi-symmetric if any two of its monomials \( x_{i_1}^{n_1} \dots x_{i_k}^{n_k} \) (where \( i_1 < \dots < i_k \)) and \( x_{j_1}^{n_1} \dots x_{j_k}^{n_k} \) (where \( j_1 < \dots < j_k \)) have the exact same coefficient in \( g \) [cite: 2]. Every symmetric function is quasi-symmetric, but the reverse is false [cite: 7].

A fundamental building block of \( QSym \) is Gessel's **fundamental quasi-symmetric function**, denoted \( F_{n, D} \), where \( D \subseteq [n-1] \). It is defined as the sum over all monomials \( x_{i_1} x_{i_2} \dots x_{i_n} \) such that \( i_1 \leq i_2 \leq \dots \leq i_n \), with the strict condition that \( i_j < i_{j+1} \) if \( j \in D \) [cite: 2, 5]. 

Many combinatorial objects generate quasi-symmetric functions. For instance, given a set of combinatorial objects \( B \) equipped with a descent map \( \text{Des}: B \to \mathcal{P}([n-1]) \), one can define a quasi-symmetric generating function \( Q(B) = \sum_{b \in B} F_{n, \text{Des}(b)} \) [cite: 2, 8]. A major problem, originally addressed by Gessel and Reutenauer, is identifying sets \( B \) and statistics \( D \) for which \( Q_D(B) \) is symmetric, and furthermore, Schur-positive [cite: 5].

## 2. Methodologies for Proving Schur Positivity: A 2024-2026 Synthesis

Proving that a combinatorially defined function is Schur-positive is a notoriously difficult task. Over the decades, several distinct methodologies have been developed. In the period of 2024–2026, these classical methods have been refined, and unifying theories have emerged that bridge previously disparate techniques [cite: 9].

**Table 1: Primary Techniques for Proving Schur Positivity**

| Technique | Description | Recent Developments (2024-2026) |
| :--- | :--- | :--- |
| **Representation Theory** | Constructing a graded module whose Frobenius character equals the function [cite: 9, 10]. | Utilization of 0-Hecke modules for genomic Schur functions and modified Macdonald polynomials [cite: 11, 12]. |
| **RSK Correspondence** | Bijective proofs converting words to semi-standard tableaux [cite: 9, 10]. | Applied to unicellular LLT and non-symmetric Macdonald polynomials [cite: 9]. |
| **Crystal Graphs** | Defining a graph structure with local rules acting on underlying objects to yield Schur components [cite: 6, 9]. | Integrated into a broader framework via "Crystal Skeletons" [cite: 13, 14]. |
| **Dual Equivalence** | Defining a graph structure on Gessel expansions where connected components sum to Schur functions [cite: 6, 9]. | Proven to be a specialized instance of the newly axiomatized Crystal Skeletons [cite: 13, 15]. |
| **Slinky Rule / Sign-Reversing** | Converting fundamental expansions to signed Schur expansions and defining involutions to cancel negative terms [cite: 9]. | Applied to vertex-colored graphs and chromatic symmetric functions [cite: 16, 17]. |
| **Positive Permutation Classes** | Identifying subsets of \( S_n \) whose descent generating functions are Schur-positive [cite: 9]. | Complete classification of symmetric sets without monotone elements by Tuong Le [cite: 18, 19]. |

### 2.1 The Evolution of Dual Equivalence and Crystal Skeletons
Dual equivalence, originally introduced by Haiman and further formalized with a local characterization by Assaf and Roberts, is a graph-theoretic approach to Schur positivity [cite: 9, 15]. The core idea is to take a function expressed as a sum of fundamental quasi-symmetric functions and impose a specific graph structure (a dual equivalence graph) on the underlying combinatorial objects. If the graph satisfies a specific set of axioms, its connected components are guaranteed to sum to individual Schur functions [cite: 9].

Simultaneously, **crystal graphs** have been used to study the representation theory of Lie algebras [cite: 15, 20]. A crystal graph structure defines local rules (acting as raising and lowering operators) on combinatorial objects, linking them to an \( S_n \)-module (a representation) whose Frobenius image is the symmetric function [cite: 9].

A major theoretical breakthrough occurring between 2023 and 2025 is the formalization of **Crystal Skeletons**. Introduced initially by Maas-Gariépy in 2023 by contracting quasi-crystal components within a crystal graph, crystal skeletons model the expansion of Schur functions directly into Gessel's quasi-symmetric functions [cite: 13, 15]. 

In a pivotal 2025 paper, Brauner, Corteel, Daugherty, and Schilling provided a full combinatorial description and a new axiomatic approach to crystal skeletons, acting as an analog to the local Stembridge axioms used for standard crystals [cite: 14, 15]. Crucially, they proved a conjecture by Maas-Gariépy stating that crystal skeletons explicitly generalize dual equivalence graphs [cite: 13, 15, 20]. 
*   **The Framework:** The vertices of a dual equivalence graph \( DE(\lambda) \) are indexed by standard Young tableaux \( SYT(\lambda) \). The edges are defined by elementary dual equivalence relations \( D_i \) that operate on specific configurations of letters \( i-1, i, i+1 \) in a permutation [cite: 15].
*   **The Unification:** Brauner et al. demonstrated that by taking a crystal skeleton and restricting its edges to certain minimal length intervals (specifically Dyck pattern intervals of size 3), one perfectly recovers the dual equivalence graphs developed by Assaf and Roberts [cite: 15]. They provided three versions of axioms based on \( GL_n \)-branching, \( S_n \)-branching, and local Stembridge-like axioms [cite: 13]. This unifying concept provides a universal method for establishing the symmetry and Schur positivity of quasi-symmetric functions moving forward [cite: 21].

### 2.2 Edelman-Greene, Slinky Rule, and Sign-Reversing Involutions
When geometric or graph-theoretic models are insufficient, mathematicians turn to bijective algebraic manipulations. The **Edelman-Greene bijection** is famously used to demonstrate that Stanley symmetric functions are Schur-positive [cite: 9]. 

Another approach is the **slinky rule**, which converts an expansion in the Gessel fundamental quasi-symmetric basis into a signed Schur expansion. Because the result contains negative coefficients, researchers must invent a complex sign-reversing involution to cancel out the negative terms, leaving only the positive Schur components [cite: 9]. This approach, heavily reliant on defining precise involutions, has seen massive application in the study of chromatic symmetric functions in 2024 and 2025 (detailed in Section 4).

## 3. Pattern Avoidance and Symmetric Sets (2024-2026)

The intersection of pattern avoidance and quasi-symmetric functions has yielded some of the most exact and definitive results of the 2024-2026 period. 

### 3.1 The Foundations of Pattern Quasisymmetric Functions
Given a set of permutations (patterns) \( \Pi \), the avoidance class \( S_n(\Pi) \) denotes the set of permutations in the symmetric group \( S_n \) that avoid every element of \( \Pi \) [cite: 8, 22]. In 2020, Hamaker, Pawlowski, and Sagan introduced the concept of **pattern quasisymmetric functions** [cite: 23]. The object of study is the generating function \( Q_n(\Pi) = \sum_{\sigma \in S_n(\Pi)} F_{n, \text{Des}(\sigma)} \) [cite: 8].

A set of permutations \( \Pi \) is said to be *symmetrically avoided* if \( S_n(\Pi) \) yields a symmetric function for all \( n \). Furthermore, it is *Schur-positively avoided* if the resulting symmetric function is Schur-positive for all \( n \) [cite: 18, 19]. Hamaker et al. successfully characterized all subsets of \( S_3 \) that generate symmetric and Schur-positive functions, pointing out relationships with Knuth classes and arc permutations, and laid the groundwork for generalizations to higher symmetric groups [cite: 8].

### 3.2 Avichai Marmor's Bounding Theorems (2024-2025)
Building on the work of Bloom and Sagan, who showed that for \( k \geq 4 \), if \( \Pi \subseteq S_k \) is symmetrically avoided and \( |\Pi| \leq 2 \), then \( \Pi \) must be a subset of the monotone permutations \( \{12\dots k, k\dots 21\} \), Avichai Marmor made significant strides in 2024 and 2025 [cite: 19, 24].

Marmor proved a tight lower bound for pattern avoidance and symmetric functions. He demonstrated that for \( n \geq 5 \), any symmetric set \( S \subseteq S_n \) must have a size of at least \( n - 1 \), unless \( S \) is a subset of the monotone elements [cite: 18, 19]. To prove this, Marmor utilized a novel generalization of Bose's theorem in extremal combinatorics and leveraged the multilinear polynomial approach introduced by Alon, Babai, and Suzuki [cite: 24]. This resolved a standing lower bound conjecture but left open the classification of symmetric sets of larger sizes.

### 3.3 Tuong Le's Complete Classification (2026)
In January 2026, Tuong Le published a definitive resolution to the questions posed by Marmor's bounding theorems [cite: 18, 19]. Le provided a complete classification of the possible sizes of symmetric sets not containing the monotone elements \( 12\dots n \) and \( n\dots 21 \) for \( n \geq 52 \) [cite: 18, 19]. 

Le's work revealed a striking structural duality: a set \( S \) is symmetric if and only if its complement \( S_n \setminus (S \cup \{12\dots n, n\dots 21\}) \) is symmetric [cite: 19]. Furthermore, Le provided a complete classification of symmetric sets of size at most \( n - 1 \). By classifying these sets, Le achieved a monumental corollary: all symmetrically avoided sets of size at most \( n-1 \) are actually Schur-positively avoided, completely resolving Marmor's conjecture regarding the positivity of these sets [cite: 18, 19].

### 3.4 Pattern-Avoiding Peak Functions (Slattery-Holmes, 2025)
Expanding the scope beyond descent statistics, Matthew Slattery-Holmes (in joint work with Michael Albert and Dominic Searles) investigated **pattern-avoiding peak functions** in 2025 [cite: 23, 25]. Instead of using the descent set, this research focused on the *peak set* of a permutation, defining analogous quasi-symmetric functions expanded in terms of peak functions [cite: 22, 23].

Slattery-Holmes successfully identified precisely which subsets of \( S_3 \) result in a pattern-avoiding peak function that is symmetric [cite: 23]. Furthermore, while descent-based symmetric functions are usually evaluated for standard Schur positivity, peak-based symmetric functions are evaluated for positivity in the closely related **Schur P-functions** and **Schur Q-functions** [cite: 22, 23]. Slattery-Holmes provided explicit formulas for the positive expansion of these symmetric peak functions into Schur Q-functions. The research extensively utilized Robinson-Schensted-Knuth (RSK) insertion algorithms and analyzed Wilf-equivalence and peak-equivalence among permutation sets [cite: 22].

**Table 2: Breakthroughs in Pattern Avoidance and Symmetry (2024-2026)**

| Researcher(s) | Year | Key Contribution | Implication for Schur Positivity |
| :--- | :--- | :--- | :--- |
| **A. Marmor** | 2025 | Proved symmetric sets in \( S_n \) (\( n \ge 5 \)) lacking monotone patterns must have size \( \ge n-1 \) [cite: 18, 19]. | Established hard lower bounds for when a pattern class can yield a symmetric function [cite: 24]. |
| **M. Slattery-Holmes** | 2025 | Classified subsets of \( S_3 \) that yield symmetric pattern-avoiding peak functions [cite: 22, 23]. | Provided explicit positive formulas in terms of Schur Q-functions and Schur P-functions [cite: 22, 23]. |
| **T. Le** | 2026 | Completely classified symmetric sets of size at most \( n-1 \) for \( n \ge 52 \) [cite: 18, 19]. | Proved definitively that all such symmetrically avoided sets are strictly Schur-positively avoided [cite: 18, 19]. |

### 3.5 Matchings, Short Chords, and Schur Positivity
In addition to pattern avoidance in permutations, the study of perfect and partial matchings has seen rigorous algebraic classification. In 2024, Avichai Marmor published a seminal paper in *Algebraic Combinatorics* titled "Schur-positivity of short chords in matchings" [cite: 5, 8].

A matching \( m \) on a finite set of vertices is an unordered partition of the set into blocks of size 1 or 2. If a block consists of \( (i, i+1) \), it is termed a **short chord** [cite: 2]. Marmor analyzed the set of matchings on \( N \) vertices with exactly \( f \) singletons (unmatched vertices) and proved that this set is Schur-positive with respect to the short chord statistic [cite: 5].

Marmor provided two distinct proofs for this theorem:
1.  **Combinatorial Criterion:** Utilizing a new criterion for Schur-positivity that relies on a sparse statistic and statistic-preserving bijections to Standard Young Tableaux (SYT) [cite: 5].
2.  **Bijective Proof:** Establishing a variant of Knuth equivalence specifically tailored for matchings [cite: 5]. 

Just as Gessel proved that permutation sets closed under Knuth equivalence are Schur-positive, Marmor demonstrated that two matchings are Knuth equivalent if and only if their "cores" are identical. Consequently, every equivalence class of matchings corresponds directly to a Schur function (specifically \( s_{N-k, k} \)) [cite: 5]. Marmor derived the exact coefficients of the Schur expansion, interpreting them in terms of Bessel polynomials, and further characterized all matchings \( m \) such that the set of matchings avoiding \( m \) remains Schur-positive [cite: 5].

## 4. Chromatic Quasisymmetric Functions (CQFs) and e-Positivity

One of the most intensely researched areas in the 2024-2026 timeframe is the study of **chromatic symmetric functions** and their quasi-symmetric refinements. 

### 4.1 Historical Context: Stanley-Stembridge and Shareshian-Wachs
In 1995, Richard Stanley introduced the chromatic symmetric function \( X_G(x) \) of a graph \( G \), which generalizes the classical chromatic polynomial. The central unsolved mystery of this object is the **Stanley-Stembridge conjecture** (1993), which posits that if \( G \) is the incomparability graph of a \( (3+1) \)-free poset (such as a unit interval graph), then \( X_G(x) \) is **e-positive**—meaning it expands with non-negative integer coefficients in the elementary symmetric function basis (\( e_\lambda \)) [cite: 3, 26]. Because \( e \)-positivity mathematically implies Schur positivity, proving the Stanley-Stembridge conjecture would inherently prove the Schur positivity of these graphs [cite: 3, 27].

In 2016, Shareshian and Wachs refined this by introducing the **chromatic quasisymmetric function (CQF)**, denoted \( X_G(x; q) \), for labeled graphs. The CQF introduces a parameter \( q \) that tracks the number of *ascents* in a proper coloring. An ascent occurs on a directed edge \( (u, v) \) if the color of \( u \) is strictly less than the color of \( v \) (\( \kappa(u) < \kappa(v) \)) [cite: 27, 28]. By definition, \( X_G(x; q) \) is generally a quasi-symmetric function. However, Shareshian and Wachs proved that when \( G \) is the incomparability graph of a natural unit interval order, \( X_G(x; q) \) miraculously becomes a symmetric function, and they conjectured that it is \( e \)-positive [cite: 28].

### 4.2 When is a Chromatic Quasisymmetric Function Symmetric?
A highly active sub-problem addressed in 2024 and 2025 is identifying the exact conditions under which a CQF, \( X_G(x; q) \), transitions from being merely quasi-symmetric to fully symmetric. This was systematically addressed by Gillespie, Pappe, and others [cite: 7, 29].

**Key 2024/2025 Discoveries on CQF Symmetry:**
1.  **The Product Theorem:** Gillespie et al. proved a remarkable foundational fact: if the product of two quasi-symmetric functions \( f \cdot g \) (in countably infinitely many variables) is symmetric, then both \( f \) and \( g \) must individually be symmetric [cite: 3]. This allowed researchers to reduce the symmetry problem of CQFs entirely to connected graphs, as a graph's CQF is symmetric if and only if the CQF of each connected component is symmetric [cite: 3, 27].
2.  **Multiple Sources/Sinks:** Any labeled, connected, directed acyclic graph that possesses more than one source or more than one sink inherently has a non-symmetric CQF [cite: 3, 27, 29].
3.  **Directed Trees:** Resolving an open question posed by Aliniaeifard et al., it was established that for a directed tree \( T \), the CQF \( X_T(x; q) \) is symmetric if and only if \( T \) is a simple directed path (with the natural labeling \( 1, 2, \dots, n \)) [cite: 3, 7]. All other trees yield non-symmetric CQFs [cite: 27, 29].
4.  **Mixed Mountain Graphs:** Researchers identified a novel family of graphs termed "mixed mountain graphs"—constructed by stringing together sequences of \( k \)-mountains (complete cliques) and bottomless \( k+1 \)-mountains (cliques missing one edge) sharing single vertices, connected end-to-end. It was proved that every mixed mountain graph generates a strictly symmetric CQF [cite: 3, 29].

### 4.3 Foster Tom’s Signed e-Expansion (2024-2025)
To attack the Stanley-Stembridge conjecture directly, mathematicians attempt to find explicit combinatorial formulas for the \( e \)-expansion of the CQF. In 2024 and 2025, Foster Tom published a breakthrough approach utilizing **signed elementary symmetric function expansions** [cite: 16, 17].

Because direct positive formulas remain elusive for all unit interval graphs, Tom provided a signed formula in terms of objects called **forest triples** [cite: 17]. A forest triple relies on identifying decreasing subtrees within the natural unit interval graph [cite: 17]. While the initial expansion contains negative coefficients (preventing immediate proof of \( e \)-positivity), Tom introduced sophisticated **sign-reversing involutions** on these forest triples [cite: 16].

By pairing positive and negative terms and canceling them out, Tom successfully proved exact, non-negative combinatorial formulas for several distinct families of graphs:
*   **K-chains:** Graphs formed by joining complete cliques at single vertices. Tom's formula immediately implied strict \( e \)-positivity and \( e \)-unimodality for all K-chains, providing a new proof of a result initially explored by Gebhard and Sagan [cite: 16, 17].
*   **Melting K-chains:** Graphs obtained from K-chains by removing any number of edges from any of the cut vertices. Prior to Tom's 2024 work, melting K-chains were not known to be \( e \)-positive [cite: 17]. Tom's sign-reversing involution generalized perfectly to this family, establishing their \( e \)-positivity for the first time [cite: 17].
Tom also generalized these forest triple formulas directly to the quasi-symmetric refinement of Shareshian and Wachs, providing a unified algebraic tool for future proofs [cite: 16, 17].

### 4.4 Non-commutative Functions and Flip Operators
Another advanced methodology applied to CQFs involves non-commutative symmetric functions and **flip operators**. Hwang (2022/2023) introduced a flip operator on proper colorings of graphs [cite: 26]. This operation establishes an equivalence relation on colorings such that all colorings in an equivalence class maintain the same ascent statistic [cite: 28]. 

It was shown that the connected components of colorings under these local flips are independently Schur-positive, refining the Shareshian-Wachs model [cite: 26]. This noncommutative approach provides expansions of the CQF in terms of several bases, unifying positivity results and offering partial resolutions toward the overarching \( e \)-positivity conjecture [cite: 28].

Furthermore, research into **alpha-chromatic symmetric functions** in 2025 by Haglund, Oh, and others has generalized these concepts, showing explicit monomial expansions in terms of \( \alpha \)-binomial bases and revealing deep connections between CQFs and rook theory, specifically providing new solutions to Garsia and Remmel's problems on \( q \)-hit numbers for Ferrers boards [cite: 4].

## 5. Genomic Schur Functions and 0-Hecke Modules (2026)

While classical Schur functions are deeply tied to the representation theory of the symmetric group, generalized symmetric functions often require more complex algebraic structures, such as Hecke algebras, to find representation-theoretic interpretations. A prime example from 2026 involves **genomic Schur functions**.

### 5.1 Background on Genomic Schur Functions
Genomic Schur functions, denoted \( U_\lambda \), were introduced by Oliver Pechenik and Alexander Yong in the context of the \( K \)-theory of Grassmannians [cite: 11, 30, 31]. They serve as generating functions for "genomic tableaux," which were utilized to prove the first positive combinatorial rule for Littlewood-Richardson coefficients in torus-equivariant \( K \)-theory [cite: 31]. 

Pechenik proved that while \( U_\lambda \) forms a basis for the ring of symmetric functions, it is generally **not Schur-positive** [cite: 30, 31]. It is, however, always positive when expanded in the fundamental quasi-symmetric basis (it is fundamental-positive) [cite: 31]. Interestingly, Pechenik noted a special case: if the partition \( \lambda \) has exactly two parts (a two-row shape), the genomic Schur function *is* Schur-positive [cite: 11, 30].

### 5.2 Representation-Theoretic Proof by Kim and Yoo (2026)
Following Pechenik's combinatorial observations, Young-Hun Kim and Semin Yoo hypothesized that this specific two-row Schur positivity was not a mere numerical coincidence but indicated a deeper algebraic structure. They conjectured that this expansion admitted a representation-theoretic interpretation in terms of **0-Hecke modules** [cite: 12, 30, 31].

The Grothendieck group of the category of finite-dimensional \( H_n(0) \)-modules corresponds directly to the ring of quasi-symmetric functions, making the 0-Hecke algebra the natural setting to study fundamental-positive functions [cite: 30, 32]. 

In April 2026, Kim published a breakthrough paper titled "A representation-theoretic interpretation of the Schur expansion of two-row genomic Schur functions" [cite: 12, 31]. For each partition \( \lambda \) and integer \( 1 \leq m \leq n \), Kim constructed an explicit \( H_m(0) \)-module, denoted \( \mathbf{G}_{\lambda; m} \) [cite: 11, 32]. 
*   **The Construction:** Kim defined a highly specific action of the 0-Hecke algebra \( H_m(0) \) on sets of *increasing gapless tableaux* [cite: 11, 32]. 
*   **The Result:** He proved that the image of this module under the quasi-symmetric characteristic map is precisely the \( m \)-th degree homogeneous component of the genomic Schur function \( U_\lambda \) [cite: 11]. By proving the conjecture of Kim and Yoo, this work established a definitive representation-theoretic origin for the Schur expansion of two-row genomic Schur functions [cite: 12, 30].

## 6. Flip Operators and Macdonald Polynomials

Beyond chromatic functions, the concept of **flip operators** has seen profound application in the study of Macdonald polynomials, which are two-parameter (\( q, t \)) generalizations of Schur polynomials [cite: 33, 34].

### 6.1 Modified Macdonald Polynomials and Mahonian Statistics
The modified Macdonald polynomial, \( \tilde{H}_\lambda(X; q, t) \), introduced by Garsia and Haiman, is fundamentally tied to the representation theory of diagonal coinvariants and is known to be Schur-positive (and thus monomial-positive) [cite: 34, 35]. Understanding the explicit combinatorial formulas for these polynomials relies heavily on statistics like inversions (inv), queue inversions (quinv), and the major index (maj) on fillings of Young diagrams [cite: 33, 34].

### 6.2 Queue Inversion Flip Operators
In recent years, Ayyer, Mandelshtam, and Martin introduced the **queue inversion flip operator**, inspired by earlier inversion flip operators by Loehr and Niese [cite: 33, 35, 36]. This operator, denoted \( \rho_i \), acts on pairs of adjacent columns of equal height within a super filling of a Young diagram [cite: 35, 36]. 

In 2025 and 2026, researchers heavily modified these operators to quantify exact changes in specific Mahonian statistics. For instance, the operator was altered to allow execution beginning at any row (not just the topmost row) and to include strict non-equality conditions on terminating rows [cite: 33, 35]. By applying sequences of these queue-inversion flip operators, mathematicians constructed new involutions that preserve the major index statistic while predictably altering the inversion and quadruple coinversion statistics [cite: 34, 36]. This has allowed for the derivation of highly compact "multiline queue" factorization formulas for specialized Macdonald polynomials and the introduction of new "quasi-symmetric Macdonald polynomials" that refine classical symmetric versions and specialize gracefully into the quasi-symmetric Schur polynomials defined by Haglund, Luoto, Mason, and van Willigenburg [cite: 36, 37].

## 7. The ab-Index and Intersection Posets (2024)

An intriguing tangential development from 2024 linking quasi-symmetric functions to number theory is the study of the **Poincaré-extended ab-index** [cite: 38]. 

Motivated by conjectures regarding Igusa local zeta functions for intersection posets of hyperplane arrangements, mathematicians studied multivariate rational functions arising from p-adic integrals [cite: 38]. By defining the extended ab-index (and a generalized "pullback ab-index"), researchers recovered and unified prior results by Billera-Ehrenborg-Readdy and others on the combinatorics of P-partitions [cite: 38].

Crucially, the algebraic connections forged in this work allowed the results to be directly translated into the language of quasi-symmetric functions. In the specific case where the resulting functions are symmetric, researchers posed new conjectures regarding their Schur positivity—conjectures that were rapidly strengthened and proved using advanced algebraic techniques (e.g., by Ricky Liu in appended work), further demonstrating the omnipresence of Schur positivity across diverse mathematical domains [cite: 38].

## 8. Conclusion and Future Directions

The period spanning 2024 to 2026 has been marked by a transition from isolated combinatorial proofs to sweeping, unified classifications in the study of quasi-symmetric functions and Schur positivity. 

1.  **Unification of Tools:** The development of crystal skeletons has successfully bridged the gap between dual equivalence graphs and crystal graphs, offering a unified, axiomatized framework for breaking down fundamental quasi-symmetric expansions into Schur-positive components [cite: 13, 15].
2.  **Absolute Classifications:** The work in pattern avoidance by Marmor, Slattery-Holmes, and Tuong Le has provided exact, definitive classifications of symmetric sets, proving that subsets lacking monotone patterns can only be symmetric (and Schur-positive) under extremely specific, now fully quantified, constraints [cite: 18, 19, 23]. 
3.  **Tackling the Stanley-Stembridge Conjecture:** While the ultimate proof of the Stanley-Stembridge conjecture for all unit interval graphs remains slightly out of reach, the introduction of signed elementary expansions and sign-reversing involutions on forest triples by Foster Tom has proven \( e \)-positivity for wide swaths of graph families, including melting K-chains [cite: 17]. Furthermore, the exact classification of which directed graphs yield symmetric chromatic quasisymmetric functions has massively narrowed the scope of the problem [cite: 3].
4.  **Representation Theory's Continued Relevance:** The resolution of the genomic Schur function positivity via 0-Hecke modules highlights that whenever a symmetric function exhibits Schur positivity, there almost certainly exists a beautiful, hidden graded module waiting to be constructed [cite: 12, 30].

As research moves forward, the algebraic tools forged between 2024 and 2026—be they flip operators, crystal skeleton axioms, or noncommutative symmetric functions—will undoubtedly serve as the primary weapons used to dismantle the remaining mysteries of Schur positivity.

**Sources:**
1. [ijsret.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdrfg5YeXTR824wwNowh__woFu4C1wyGl4bFVHoD0hX2p8pT7y6UVFHWiXDDzONYS1hoZX8mtuXxI7SDqJ6YvC_sLyz9XIHFErhGic3axRXjvqlpihL7d1-_8Tgp_QHqsTS1EVFbMMQDvpDxtLd5TEMMQ_1Y8=)
2. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHglguLRxjYpJPXPhOiUfxSNbHDhqM_Ie0SZsgaMf9DddyIMW8gQFno4BXX4A3P3lzNjuxeAT6RLVF8dFfp9AdF8ReFXYimf8LtNDgpegd2qzYeBfL_FPtANm_Xd8oYB5sOLPxaXyQ7Yr9FqyX906UqH9hsv-Y=)
3. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpzxwZNIecaoCs16_KPEuOFPZEhIXpb1Y8sJyjNbuIYCmzeXZbla5NFPhEJGzzl9jMd-FapmNIFQR1zcYWXkvK_wCZDlcPWnTycF2Xf-vWje65_0gcjzuTNg0t9Xif6cCGJaHPvPa7C5GV_-L65pYRHQ==)
4. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCNtsL0ejQzUrKFNswH7LF7FP090saPV_SXVyWN4eSt-Z4lBx8HOhxSKVhSc_MId53LEA-zStgQNltwMKFJxw_sSABKVnOSL_zXuxiI9ZBdqqKjw3dQBeFcEVakvOe1RUBTrXXuaoNAv6YqJ_71UcLYQ==)
5. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExRg1ZNZV5Awo4RDG6Yeb2z0Y5xTT_MOSADFEDd_c66RnAUE0WO1vMWbKnfoSBou939lzCPvLloZAlYvaf4NwG_aar39iRHR0If7QLn1hojYoUuvphZyC3TqD5eYyERVs2nHtgNJ67oGqwmTHVPhre)
6. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFphGe392_g767UN8M1wrV-crI38i2Qm3uhqsnwONU_-q7AxNh1W5uFy1CcDAsPwDYb-On3uwlttQGjp8HxNXzqmnO1xvs1IV3qNrqQn8gEUVfS2zDc7quiWIJFidCBYnYb9x4E)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFF7ZXlQMeAItILRr8aFWvek-MYpcL949EcSRn8rQariVqpCVlW4oLfbN8k-pNMXeK2qn1B2bZHIF8Ix4MbToPMv4yI3vvdzSVIzrjt-GZTpZjXnsgg6wbM2RO-X-U3bbboGndFuxSv3s4RSuTKVCu2mhQxvaIPkOqX0B1mqy0NhQRN6Q0mq0WS0e0QDsL0lxkaWcbnY4xao8C1CKn)
8. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGU_7-ZHcXaYdyUCXZZHBCvHL_o9qwbfg2XbWruLPQ5KNKgpvj6KSzDOtholDl0MRJtOa5ApT8Ulfq89KKKH7U7pI7RweXW3vNfExT41U9-VmL4wD23JCJnq3hS6Rg6y40gi0aJuS0W7SnB_zwrwBN3)
9. [symmetricfunctions.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxWHgCaThIp_7oy7Ou7hPHkiPavpehOSRebdbdbzc3TqFELJtti2b5q1XEMF0NaE8DUKqbBNYO9z3LbQjTkPtpufBcs6-Bx2KyR0bXLrEcJJ6ukLEliqOetPeFGoQhoqnolxo3wD1_dBhA5-M=)
10. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgEXf7fMwqWM7AU5FnK9jFpYu84_ffxC-BMTV-qNjTJ-uixm74nJYpw7vxHlI0_y8OMPd_jMMQv_ur8C9tgDL9dDQmeTpY2Cm36nLq0zQX_lmleg877i4ZMY9NSiMOuPPh0J2nBiIpZs4dhcdOHMS6nzEY9kvENazatWGyJJsDQNnQ-2NinYHhbUKrcsuoQ1kpHWc=)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZky0h5IKspH3GNyV_nRWg2YYzZI1EXoOzqkT7wXcpDdA5fdrwBbBCRfj0UX3MrIb57j884x6jglKwuXjRxqTQ5e6Nae5newgaxwNAz_ytKiGdzDmtMXJWdTjv6nXxVllfJo0HLZ4U90VxtTiJFDrtg92AoXbqrk2Y3pHsFjkAGZfL3qU=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHahi5dxVsCPa3O1HXYFoC0vtppgExjSn_O-ejC6xD0dDN3GX2TsSfquR8ea2FNvyOb9GOG3yCMk2SkCVh8OTOJPZGJUxUDpBhW5HpKQSqHzW5rYYlNpQ==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJKW1x98jYRCH-9ibVWyEK8cEdLUhW704XDU6MYAPILaaUHVFvvzyrwHvQVhVfiaNT8jHkPaNmNTlDGwgkKogaP-qcVo3mUCFax1RxlCKCN8hvVNPPaw==)
14. [awm-math.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESFzDpvfaxt_Cs9PfdSiqPg8mzdb303UIvS--uXRMVw36sMfUg0HvEQj5l6XJp6DQ5kBjC_yvYAufXQU5AM7zpRwkzaF6Sq48t35sLtGU3G2WwpfHUwYWsL-8lIFyk0Ki_MAH1L5X35T4fqAdNDs2ihIhF1jxRTQ==)
15. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxudnRwj46O-rpyAX65T9FIYbzCGs12ZxK6AI6nv0krNUcNwOFYQeKcV8NtZ7ZLOiNh_guMFuIAjh-LdbnAup_GTYnC695JG5dj7sCEvwcQUCCQeX9BLX7nKlWxsfA0JbY7lH6s2izvjrOnx3heT63jg==)
16. [escholarship.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqDH_5_m-TOhYJwIUwwIlUrwM7P0w4RjAnmUSvgHRyPA1sBYls1sUoCc5hRflEcE3N47Cfn599NsKos9z1N-wXo7MxV0IxSSc08iD9R8hPPMSN57fxMWhASMUWVeDqvg==)
17. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNItOz14SWFHE_iPz5fgRejQK6QErRjCYMbhc4VlyDf7qEvCvrPTfGEumb-WgDE7xDHxvMG16PAQtNvjug2RTw1iONg8MY4uHhC61M0gWj-A6RwLD7PY_m75owWBUoHm62viLw51VPgLKtF_G74tQo)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOBPbo7CYykakGZoAbKwPyV-Ig28MkkIJ3vEJJaZ-n6VFeyImM_Ccqa6zPDDTwgsseja1IN1zbuMPAf37OWEiQEaWGileRqNdBdPEu-mY9StQCWfIMLA==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG65SV4GEmP6n3mtFhP8ehoBX3tWl0qjw5WncX33QfEwV0pKOvHnTO4s4Ik46-Bq499m-tH4ZNy_Ggokw5smXmhqmSdBW601WVDGnirLmd1UnzAlfnuMQ==)
20. [upenn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEToCp4IJTlUkvC3mQ-IvvRcjlUByUUHzGkvFrg2SYvKd1wm4e3sbxbHKkc6wt8uG4mWNABf2eNQPcy1lGm4qxyxYOjOebTfgZGNgLktKhqdBqBJK3ohjYYdXrD0KNfhjbP6-zkCl5FNTjI2kzZgp3R9N3qrX88OPKBZhKygpcQ2La3)
21. [usc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_RSU3xQ-me0hrLPDha7PszuFDpE72KU--Oa0TvXNJgpt0o0dCe9pcw6x7R40A6thIUsXbrrARTqovNmED0dyzoxm7t_JTRrTOvXZLci69HG0uiUUGiwrzUcFBwsaoN2Aw)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFusOiLpINlipqX9DUnXT3ynPt1dFf51B6Vx4ifk3aK-eFiwncoMEgBmt499XxKhK7I-IiGk_g2Sxr0RCfA9H71QmEIVUN8qFLCdMvmtKHdxzzeTulReA==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4UsO_T7bnTp9fPxRuQxk6eXBIDeXjmuv5rQByZogr30fQXKHAPUzQNc1dt3XICApuhYEUA0939yu-9GEb9TXKVAq9NMJ-DHhdpmDzNSLxF6NQlcR1RQ==)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAO1c4R8Wt9uPwP5M8gw_09f8ymdnFOezahIQI2BgzlqLGooxHy1fJ-xzAV1iP7aiMoCkveFeDW5kUjhS_Tjbmo7QsDQUNSjOytqmGjqaXV7bfPEqCRUajlNMJeyuTh1gmuQlf3c06ng72SkVrBuh0kTd3In0neEBDWjI9YI4m8G9IZTXb)
25. [st-andrews.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbijUl7PauafEosj0VBMAznu2_mGP2CxXFpEcvJ3U2hc6z_k6iUIddHCWF90sIF8hf6zpSz0_Pb7IbfrbvdxqWtaDWzlfd3QY4j_PPVjAs182dltssllhT9f_cvuglzeE3_mQ6Aj_nPYPXxHm-NoTpK8k3U7mO7BN02h221O6u)
26. [symmetricfunctions.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWugn4jusglxyU3Ohnf4MHQGpgeMWUGCORZUkHj_taoYajF91M7CDkSthxjtKzEdJ2vrGoHYePh7e7jD3jnsh9jdqCtsmDSqyN1EmwykuhGn83YYXQMmRNVE2RQyaHI79zadKBB76MmiBDfeNVB4lA_TOB5g==)
27. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8p_Fk3lkAqJsA2ccuzWw5L2catpRt-k4rVEe80fAaAVFXvPMqNR8uv1O6Ylh3O8yJ-6rw-ZTiRvZk7nlj1mU_0AxPHXmSla-mZIDm9F80A3rP8VWyswSJYW3JdzyuNu_xJkxFEtjUqJKaJgbv1UzK)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZSTnU0wdvM25MslKyjtg5FpY3h9QkWK8abAo_jZUwwcyEmNn8GdBTk__Py_qh3GFZd9a4vFkB5Zmy9xXwV744AEvUGUVpACRI_6M7YYfkX-XRCPNV9Q==)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrLtzXejx5k1ut03bik867_n_AARhoGVkDpzEQaPHEF_iGvvAZUFO7KsBr_BEvyNsRA6WCsKdEWr7b9ECkQSp5UBC3hBIGEZG1wZqc0MjeLeA-3oVj6A==)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGvuvnGuj41y3cI2-JOQ-9UehJQ5jkFf8PPDge4_uZmKeiULolomNLuB_I4jSO2NO4Q8l0HUu4c16w1NvPZVso3zLt9YVf7ikkf38Rx_R8pHKQahRQHQ==)
31. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4u8eObCaPk5Nmbo5-B_a2lKNtt_rooUleypJmKlKYloawHZTQTD5aty0wAkReh3dS5WCcVOjL35gUsXpAsGoS66URK-It3ZgHC_yBQXaBs3M76-WFKzP1-_p5Cx918ZI1U9bsPDQPl0g4H6QnZGAiu-AXrWKtGnq7MpovPBLSXJLEjobCymjBG9TkFyOoJlUwbp2Ma2H3sy2IjoIXbpZRAmJhT0cA5aKWtgN3Cph_6Wt14-57X0abx7XV0RI3agrAl76bmUnNMCz60XJN)
32. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6n0dWOTG-TWsNVOLkNCFsMQo46riUuXWKfG9idAiJROV5b9zSOA5TQzbazQY5auya3PFxUgJNM9CIREN6yccOc22VJD6ZmKM5LnlDl4k0HVnhFEuYNHvxpgoDt_ArCve4zYI=)
33. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcdbhsOw8AWrl1W20vBDtWdcGheljeF_lVmKHeNarMiKSFKtfQLIhIaxhFR07Lr4_Kiw0uCnzhRlUDFjH0Fc48C-M0Gj3X9o2VaeNxw_taEKOFkhbNN-7oJ76jj6SMY7wH4NDk9y1kHy_CUH878x4BKQ==)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEx4gULdI7eqYPWWOnpm27QiZdwQcN1O_gw-R-hsfVZxjSfskB9UP9a6nSwUbz-_DVE1Km9IrUM8Vzk1o9oSXZWNdv6NFzfp7dZIgWAuPDUhAfb7FVHw==)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFJhinFUT4twZqO4TBW0-7TbzLLTdcvaqBcxgOLB3xskboWPD681udL6r9kvpcJPflXBFxdjLQ41s6fy1a5rEJcXqfNABhtJadjgZEjb1Z4GbaFA3AMg==)
36. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAcq9DTPO2deUg3cKeJAXUnzl2E-Y4ctIBxo_Yn6rX7tvApS3-FVOrt-6bdPeSbhQ2EOK5Kb2Ji4RdsRYAeb2T9B7ren_ZJ1IF2rIZtaBWjSGyJqHpBPZPOsLQg_-QkRiuNlCWlWQ8BbADtAH_2_K3CmicvzpDkjx5Z9UNviA0vhC6AWG4yV3mmDRWlNEFxOM4uwObfV2FZISTVrkVjMvuA-4ebBBWrEfUaKYnUdQpiIbQTxSCBn4Q0EmICw==)
37. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvSUkp9YPTJC3uYrjWdPu9j_Oyhg2OKoUCH-LkVaTX6E89R1pb0uIMyv7o7uOtta12WGYLhkP39-t4EpZ43MuWs9WYILp5aoLyGndsX27WYzL9Ju01PIohu4z1m1aKEZi733iQF0nDsEeFkklJFIkVUO1-ulby4ny7LKaLtul8xweOqVpuqzgpukQs)
38. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1aMelqHRhXS3xhRZvRbHFMdcI7CQvBqEttuYg-E7yucE0xI2I0cFabO7CBr_ygLBWOfaAP8ae67YRG8rEhunf-dO1y_iQtqKzAdvnIt5SNVLdjQ8B1w==)

