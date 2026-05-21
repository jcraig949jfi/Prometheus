# Geometric structures on 3-manifolds (Thurston) algorithmic 2024-2026

**Pythia queue id:** 226
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdPMUlQYXFfMUthSFJqTWNQNTRPcS1BWRIXTzFJUGFxXzFLYUhSak1jUDU0T3EtQVk
**Elapsed:** 316s
**Completed at:** 2026-05-21T18:48:25.216124+00:00

---

# Algorithmic Developments in Geometric Structures on 3-Manifolds (2024-2026)

**Key Points:**
*   **Algorithmic Geometrization:** Thurston’s Geometrization Theorem continues to serve as the bedrock for modern computational topology. Between 2024 and 2026, research has shifted heavily toward creating practical, implemented algorithms for properties once deemed strictly theoretical, such as Heegaard genus, totally geodesic surfaces, and topological volume.
*   **Triangulations and Normal Surfaces:** The reliance on almost normal surfaces for Heegaard genus computation has been bypassed by novel local triangulation modifications, vastly improving computational efficiency on real-world datasets of hyperbolic 3-manifolds. Furthermore, the structural understanding of the Pachner graph has been refined, showing that 1-vertex triangulations are connected by unimodal sequences of bistellar flips.
*   **Hyperbolic Sub-structures and Dehn Surgery:** New algorithms have resolved major open questions in specific domains, including a practical Dehn parental test using Diophantine equations and the exhaustive search for "knot friends" (knots sharing identical 0-surgeries) to probe the smooth 4D Poincaré conjecture.
*   **Complexity and Treewidth:** The intersection of parameterized complexity and 3-manifold topology has grown, with proofs establishing that hyperbolic volume provides linear bounds on the treewidth and pathwidth of dual graphs of triangulations, enabling fixed-parameter tractable (FPT) algorithms.
*   **Topological Deep Learning:** The introduction of massive combinatorial datasets, such as the MANTRA assemblage in 2025, marks the beginning of benchmarking graph neural networks and simplicial complex models on exact topological invariants of 3-manifolds.

The study of 3-manifolds experienced a paradigm shift in the late 20th and early 21st centuries following William Thurston's Geometrization Conjecture and its subsequent proof by Grigori Perelman. The classification of 3-manifolds into eight canonical geometric structures essentially reduced the topological classification of these spaces to geometry. In recent years, and particularly within the 2024–2026 timeframe, the focus of the global topological community has sharply pivoted from theoretical classification toward *algorithmic* and *computational* realization. This transition is characterized by the development of sophisticated software (such as SnapPy and Regina), advances in parameterized complexity, and the translation of deep geometric theorems into computationally tractable algorithms.

This report comprehensively details the algorithmic advancements in 3-manifold geometry and topology from 2024 to 2026. We will explore breakthroughs in the algorithmic manipulation of triangulations (such as unimodal Pachner move sequences), practical algorithms for computing the Heegaard genus, the automated detection of totally geodesic surfaces in hyperbolic manifolds, minimal volume link complements, the computational search for exotic knot traces ("knot friends"), and the emerging intersection of 3-manifold triangulations with machine learning architectures. 

## Theoretical Foundations: Geometrization and Algorithmic Topology

To understand the algorithmic achievements of 2024–2026, it is imperative to review the foundational principles of algorithmic 3-manifold topology. A 3-manifold is a topological space that locally resembles three-dimensional Euclidean space [cite: 1]. William Thurston’s Geometrization Conjecture, formulated in 1982, postulated that every closed, orientable prime 3-manifold can be cut along embedded 2-tori (known as the JSJ decomposition) such that the interior of each resulting piece admits a unique, finite-volume geometric structure [cite: 2]. There are exactly eight such 3-dimensional model geometries: Spherical ($S^3$), Euclidean ($E^3$), Hyperbolic ($H^3$), $S^2 \times \mathbb{R}$, $H^2 \times \mathbb{R}$, $\widetilde{SL}(2,\mathbb{R})$, Nil, and Sol [cite: 2, 3]. 

The vast majority of 3-manifolds—and particularly knot complements—are hyperbolic [cite: 1, 2]. The geometric structure of a hyperbolic 3-manifold is uniquely determined by its topology, a consequence of Mostow's Rigidity Theorem, which implies that geometric quantities like hyperbolic volume are topological invariants [cite: 4]. Consequently, algorithms in this domain frequently leverage hyperbolic geometry to distinguish topological spaces. 

From a purely algorithmic standpoint, it is a semi-historical result (tracing back to Thurston and Riley, and later rigorously formalized by Kuperberg) that the geometrization theorem implies the existence of a deterministic algorithm for the homeomorphism problem for closed, oriented, triangulated 3-manifolds [cite: 5]. While deciding if two closed oriented 3-manifolds are homeomorphic is known to be elementary recursive, the practical implementation of such general algorithms remains notoriously difficult due to extreme computational complexity [cite: 6]. Thus, the goal of modern computational topology is to find practical algorithms, heuristics, and parameterized bounds for specific invariants and substructures [cite: 4, 7].

## Algorithmic Manipulation of Triangulations and the Pachner Graph

The fundamental data structure used to compute the topology of a 3-manifold is the triangulation—a decomposition of the manifold into a finite number of tetrahedra with specific face-gluing rules [cite: 8, 9]. For non-compact 3-manifolds with torus boundaries (such as knot complements), ideal triangulations—where the vertices are truncated or pushed to infinity (ideal vertices)—are heavily utilized [cite: 8]. 

A central theorem in computational 3-manifold topology, originally proven independently by Matveev and Piergallini, dictates that any two triangulations of the same 3-manifold are connected by a finite sequence of bistellar flips, also known as Pachner moves [cite: 4, 8]. In three dimensions, these moves modify a local complex of tetrahedra without altering the underlying topology.

### Unimodal Sequences of Pachner Moves
Despite the theoretical guarantee that two triangulations can be connected, the structure of the path in the "Pachner graph" (the graph where nodes are triangulations and edges are Pachner moves) has historically been poorly understood, posing challenges for algorithmic searches. 

In 2025, Burton and He published a significant advancement concerning the structure of these simplification paths. They focused on 1-vertex triangulations (triangulations containing exactly one vertex), which are widely preferred in computational topology due to their minimal complexity [cite: 10, 11]. The basic Pachner moves that preserve the number of vertices are the 2-to-3 (2 $\to$ 3) move and its inverse the 3-to-2 (3 $\to$ 2) move. Other moves include the 4 $\to$ 4, the 0 $\to$ 2 (inflating a "pillow"), and the 2 $\to$ 0 (collapsing a "pillow") moves [cite: 10, 12].

Burton and He proved that any two 1-vertex triangulations of the same 3-manifold (each with at least two tetrahedra) are connected by a **unimodal sequence** of elementary moves [cite: 11, 13]. A sequence is defined as unimodal (or monotonic) if it cleanly breaks into two distinct phases:
1.  **Ascent:** A sequence of moves that monotonically increases the size (number of tetrahedra) of the triangulation.
2.  **Descent:** A sequence of moves that monotonically decreases the size [cite: 8, 11].

Crucially, the authors proved that the ascent can be achieved strictly using 2 $\to$ 3 moves, and the descent can be executed strictly using 2 $\to$ 0 moves [cite: 11, 13]. This structural theorem restricts the search space for algorithms that explore the Pachner graph to prove homeomorphism or find minimal triangulations, allowing heuristic algorithms to search via an "ascent-descent" paradigm rather than wandering aimlessly through local minima [cite: 11, 14].

### The Crushing Operation
Another powerful algorithmic tool on triangulations is the crushing operation introduced by Jaco and Rubinstein. Crushing systematically flattens certain normal surfaces (like spheres or disks) within a triangulation, always resulting in a triangulation of strictly smaller size [cite: 4]. While crushing may alter the topology of the manifold (e.g., by cutting it into prime components), it is a vital step in state-of-the-art algorithms for 3-sphere recognition, unknot recognition, and testing for essential surfaces [cite: 4]. The theoretical control of crushing in the 2024-2026 era remains integral to bounding the complexity of JSJ decompositions and processing large census databases [cite: 4, 15].

## Normal Surface Theory and Heegaard Genus Computation

Normal surface theory, pioneered by Haken, is the cornerstone of algorithmic 3-manifold topology. It translates topological problems (finding embedded surfaces like spheres, disks, or tori) into integer linear programming [cite: 6]. An embedded surface is "normal" with respect to a triangulation if it intersects each tetrahedron in a disjoint union of elementary disks (triangles and quadrilaterals) [cite: 16, 17]. By solving the associated matching equations, one can algorithmically determine properties like knot triviality or whether a manifold is Haken [cite: 16, 18].

### Breaking the Almost Normal Surface Barrier
The Heegaard genus is a fundamental invariant of a 3-manifold, representing the minimal genus of a surface that splits the manifold into two handlebodies. However, computing the Heegaard genus of a triangulated 3-manifold is proven to be NP-hard [cite: 7]. Until recently, algorithmic implementations for Heegaard genus relied heavily on "almost normal surfaces"—an extension of normal surface theory that permits one piece of the surface within a tetrahedron to be a non-standard octagon or a pair of normal disks connected by a tube [cite: 19]. Almost normal surfaces massively inflate the size of the solution space and complicate algorithmic implementation.

In a landmark paper presented at the 40th International Symposium on Computational Geometry (SoCG 2024), Burton and Thompson introduced a general method to completely circumvent almost normal surfaces [cite: 7, 19]. 

**The Algorithm (Burton & Thompson, 2024):**
Instead of extending the surface theory, Burton and Thompson proposed modifying the input triangulation itself. They demonstrated that by adding exactly four specific new tetrahedra to the triangulation, any crucial surface that would have been "almost normal" in the original triangulation is isotoped into a strictly "normal" surface in the newly modified triangulation [cite: 7, 19]. 

This localized modification carries an exceptionally low cost (adding only 4 tetrahedra) while migrating the entire problem back into the well-studied, highly optimized domain of standard normal surface theory [cite: 7]. 

**Experimental Results:**
Burton and Thompson implemented this algorithm and applied it to a dataset of 3,000 closed hyperbolic 3-manifolds. Despite the theoretical NP-hardness of the problem, their algorithm effectively and precisely computed the Heegaard genus for at least 2,705 of these manifolds [cite: 7, 19]. This implementation marks one of the first highly efficient, practical algorithms for Heegaard genus extraction operating at scale [cite: 19, 20].

## Totally Geodesic Surfaces in Hyperbolic 3-Manifolds

A surface embedded in a hyperbolic 3-manifold is termed **totally geodesic** if every geodesic arc with respect to the induced Riemannian metric on the surface is simultaneously a geodesic in the ambient 3-manifold [cite: 17, 21]. Totally geodesic surfaces impose rigid geometric and algebraic constraints; for instance, the fundamental group of the surface must inject into the fundamental group of the 3-manifold, and the image must be a Fuchsian subgroup [cite: 17, 22]. 

A major open question in this area has been the **Menasco-Reid Conjecture**, which posits that the complement of a hyperbolic knot in the 3-sphere does not contain any closed totally geodesic surfaces [cite: 7, 21]. 

At SoCG 2024, Basilio, Lee, and Malionek presented comprehensive algorithms for detecting totally geodesic surfaces and provided extensive experimental results [cite: 17, 18].

### The Detection Algorithms
The algorithm proposed by Basilio, Lee, and Malionek operates in several stages, leveraging both the topological framework of Regina and the hyperbolic geometry engine of SnapPy [cite: 18, 23]:
1.  **Volume and Euler Characteristic Bounds:** The algorithm first filters candidate 3-manifolds using Miyamoto's theorem, which provides a strict lower bound on the volume of any 3-manifold that can contain a totally geodesic surface. Concurrently, if such a surface exists, Miyamoto's theorem provides a strict upper bound on its Euler characteristic [cite: 17].
2.  **Normal Surface Enumeration:** The algorithm utilizes Regina to enumerate all admissible normal surfaces (given as vectors of normal coordinates) up to the bounding Euler characteristic [cite: 17].
3.  **Linear Algebraic Verification:** Because determining whether a surface is totally geodesic can be reduced to checking precise linear algebraic conditions on the holonomy representation of the surface's fundamental group, the algorithm explicitly computes the group embedding $\pi_1(S) \hookrightarrow \pi_1(M)$. It then evaluates the holonomy lift $\rho$ to check for the defining characteristics of a totally geodesic immersion [cite: 23].

### Computational Discoveries
The researchers applied their algorithm to an immense census of over 150,000 triangulated 3-manifolds [cite: 18, 21]. 
*   **Discovery of New Examples:** The algorithm successfully identified nine 3-manifolds containing verified totally geodesic surfaces [cite: 18, 21].
*   **Menasco-Reid Conjecture Verification:** The algorithm was applied to the complements of hyperbolic knots. The authors computationally verified the Menasco-Reid Conjecture for all knots up to 12 crossings, proving that none of these knot complements contain a totally geodesic surface [cite: 18, 21].

## Minimal Volume Link Complements and Dehn Filling Algorithms

In hyperbolic 3-manifold theory, volume strictly decreases under Dehn filling—the topological operation of gluing solid tori into the boundary components (cusps) of a manifold [cite: 24]. A significant line of algorithmic research involves understanding which manifolds can be obtained as Dehn fillings of others, and determining the "topological volume" of a closed 3-manifold, defined as the minimal hyperbolic volume among all hyperbolic link complements within that manifold [cite: 25].

### The Dehn Parental Test
In a 2025 preprint, Schmalian introduced an exact algorithm to compute the minimal volume hyperbolic links inside an arbitrary 3-manifold $M$ [cite: 24, 26]. A critical subroutine of this process is the **Dehn parental test**: an algorithm that takes two 3-manifolds $N$ (with toroidal boundary) and $M$, and definitively decides whether $M$ can be obtained by Dehn filling $N$ [cite: 24, 26].

**Mechanism of the Algorithm:**
The algorithm relies heavily on Jørgensen-Thurston theory, which states that for any volume bound $V$, there exists a finite list of "parent" hyperbolic manifolds such that every hyperbolic manifold with volume $\le V$ is obtained by strongly non-exceptional Dehn filling of one of these parents [cite: 24]. Schmalian proved that the set of boundary slopes that yield a Dehn filling from $N$ to $M$ is governed by a special class of quadratic Diophantine inequalities [cite: 24, 26]. Because the solvability of this specific class of Diophantine equations is decidable, the entire Dehn parental test becomes algorithmic [cite: 24, 26].

Using this subroutine, Schmalian's algorithm can output a finite set containing all minimal-volume $k$-component hyperbolic link complements in $M$ up to homeomorphism, computing the topological volume $\text{vol}_t(M)$ to arbitrary precision [cite: 24].

### Topological Volume Classifications
Parallel work by Kegel et al. (2024) explored this topological volume invariant $\text{vol}_t(M)$ across various closed non-hyperbolic manifolds. They established asymptotically tight upper and lower bounds and fully classified all non-hyperbolic closed 3-manifolds with a topological volume $\le 3.07$ [cite: 25]. A striking topological insight from this work is that for almost all lens spaces (with finitely many exceptions), the volume minimizer is obtained by Dehn filling one of the cusps of the complement of the Whitehead link or its sister manifold [cite: 25].

## The Search for Exotic Knot Traces and "Knot Friends"

A major driving force in low-dimensional topology is the Smooth 4-Dimensional Poincaré Conjecture. A known potential avenue for constructing a counterexample to this conjecture involves finding two knots with the same 0-framed Dehn surgery trace (the 4-manifold obtained by attaching a 0-framed 2-handle to the 4-ball along the knot) but with different smooth slice statuses [cite: 27, 28]. 

Two distinct knots $K$ and $K'$ are defined as **friends** if their complements, when filled along the 0-slope (0-surgery), produce diffeomorphic closed 3-manifolds [cite: 27, 29]. The task of finding knot friends has thus become highly sought after. In 2026, Kegel and Spreer published a practical algorithm combining SnapPy and Regina to systematically search for friends of a given knot [cite: 27, 28].

### Algorithmic Pipeline for Knot Friends
While theoretically, one could simply enumerate all knots by crossing number, compute their 0-surgeries, and check for homeomorphism, the super-exponential growth of knots relative to crossing number makes this approach intractable [cite: 27, 28]. Kegel and Spreer's algorithm (Algorithm 1: Friend search) takes a much more direct, geometric approach:

1.  **Ideal Triangulation:** Given a knot diagram $K$, the algorithm uses SnapPy (via the Weeks algorithm) to construct an ideal triangulation of the knot complement, guaranteeing the number of tetrahedra is at most four times the crossing number [cite: 27, 28].
2.  **0-Surgery and 1-Vertex Triangulation:** A 0-surgery is performed on the ideal triangulation, and the resulting closed manifold $K(0)$ is passed to Regina to compute a 1-vertex triangulation [cite: 27, 28].
3.  **Loop Edge Drilling:** In a 1-vertex triangulation of a closed 3-manifold, every edge is a loop, and thus represents an embedding of a circle (a knot) inside $K(0)$. The algorithm systematically drills out every edge $e$ from the triangulation [cite: 28].
4.  **Knot Complement Verification:** For each drilled manifold $E = K(0) \setminus e$, the algorithm checks if $E$ is diffeomorphic to a knot complement in the 3-sphere $S^3$. It first checks if the first homology $H_1(E)$ is isomorphic to $\mathbb{Z}$. If so, it utilizes the Gordon-Luecke theorem and the 6-theorem to rigorously verify if it is a knot complement [cite: 28].
5.  **Diagram Recovery:** If $E$ is confirmed to be a knot complement, the algorithm changes the basis on the cusp so that the 1/0 slope corresponds to the meridian, and uses SnapPy to recover a planar diagram for the new knot $K'$ [cite: 28, 29]. 

By iterating this process, Kegel and Spreer generated over 500,000 pairs of 0-friends [cite: 29]. These extensive datasets are currently being mined for discrepancies in smooth sliceness (using invariants like the Rasmussen $s$-invariant) to search for exotic smooth structures on $\mathbb{R}^4$ [cite: 29, 30].

## Parameterized Complexity, Treewidth, and Hyperbolic Volume

While exact algorithms for 3-manifold invariants often run in exponential time, the field of parameterized complexity seeks to solve these problems efficiently when certain structural parameters of the input are small. A primary parameter studied is the **treewidth** (or pathwidth) of the dual graph of a 3-manifold's triangulation. If a dual graph has bounded treewidth, the triangulation is somewhat "tree-like," allowing many NP-hard topological problems (such as computing Turaev-Viro invariants or finding minimal surfaces) to be solved in fixed-parameter tractable (FPT) time [cite: 31, 32].

A fundamental question was whether the geometric properties of a 3-manifold could bound its combinatorial treewidth. Maria and Purcell established a groundbreaking result: the hyperbolic volume of a closed 3-manifold provides a linear upper bound on the treewidth of its dual graph. Specifically, there exists a universal constant $C > 0$ such that for any closed hyperbolic 3-manifold $M$, there exists a triangulation where the treewidth $\text{tw}(M)$ is bounded by $C \cdot \text{vol}(M)$ [cite: 4, 31, 32].

Recent follow-up work by Huszar, Maria, Purcell, and Spreer extended these bounds. They proved that hyperbolic volume also provides a linear upper bound on the **pathwidth** of the dual graph of some triangulation [cite: 15, 33]. This proof required a deep synthesis of topological tools, including generalized Heegaard splittings, amalgamations, the thick-thin decomposition of hyperbolic 3-manifolds, and the JSJ decomposition [cite: 15, 33]. These bounds formally bridge differential geometry and algorithmic graph theory, confirming that low-volume hyperbolic 3-manifolds can always be triangulated in a way that allows highly efficient FPT algorithms to process them.

## Pseudo-Anosov Flows and Veering Triangulations

Moving beyond static topology, 3-manifolds serve as the phase spaces for dynamical systems. A pseudo-Anosov flow is a dynamical flow on a closed 3-manifold that is Anosov (exhibiting stable and unstable foliations) everywhere except along a finite set of singular periodic orbits [cite: 34, 35]. These flows are intimately tied to the topology of the manifold, specifically fibered hyperbolic 3-manifolds where the fundamental group acts on a universal circle at infinity [cite: 35, 36].

Agol and Guéritaud proved a seminal theorem establishing that every transitive pseudo-Anosov flow on a closed oriented 3-manifold can be combinatorially encoded by a specific, rigid structure known as a **veering triangulation** [cite: 37, 38]. Veering triangulations lack perfect fits and admit positive angle structures, directly linking the dynamical trajectories of the flow to the discrete combinatorics of the tetrahedra [cite: 38].

However, the encoding of a pseudo-Anosov flow into a veering triangulation is not unique; drilling out different collections of periodic orbits from the same flow yields distinct veering triangulations [cite: 37]. In 2026, Parlak and Segerman presented an algorithm that completely bridges this gap. Given one veering triangulation as input, their algorithm systematically constructs all other veering triangulations that encode the identical pseudo-Anosov flow [cite: 37]. This algorithm facilitates the classification of Reeb flows for pseudo-Anosov contact structures and allows dynamicists to transition between combinatorial models without losing the underlying dynamical invariants [cite: 34, 37].

## Quantum Invariants and Link Floer Homology

The algorithmic computation of quantum invariants for 3-manifolds has advanced sharply. Quantum invariants, such as the Witten-Reshetikhin-Turaev (WRT) invariant and the Turaev-Viro state sum, embed deep topological data but are classically #P-hard to compute [cite: 39]. 

Recent works have established new algorithms leveraging the structural properties of 3-manifolds:
*   **Torus Bundles:** For WRT invariants of torus bundles, algorithms now exploit the non-commutative torus structure. By embedding the skein algebra of the closed torus into its symmetric subalgebra at roots of unity, researchers achieved a fixed $N^2$-dimensional representation supporting polynomial-time classical computation with $O(N^2)$ space [cite: 4].
*   **Tambara-Yamagami Invariants:** Delaney, Maria, and Samperton (2024/2025) formulated an algorithm for computing the Tambara-Yamagami quantum invariants of 3-manifolds, explicitly parameterized by the first Betti number of the manifold, utilizing the Turaev-Viro-Barrett-Westbury state sum framework on spherical fusion categories [cite: 39, 40].
*   **Complexity Reduction:** Ennes and Maria (2025) proved that for any 3-manifold quantum invariant in the Reshetikhin-Turaev model, there exists a deterministic polynomial-time algorithm that takes an arbitrary closed 3-manifold $M$ and outputs a new closed 3-manifold $M'$ with the *exact same quantum invariant*, but strictly guaranteeing that $M'$ is hyperbolic, contains no low-genus incompressible surfaces, and is presented by a strongly irreducible Heegaard diagram [cite: 5, 39]. This reduction severely constrains the topology of hard instances for quantum computation.
*   **Link Floer Homology:** Algorithms have also been established to compute the Link Floer homology of algebraic links directly from their Alexander polynomials. This homology, a filtered version of Heegaard Floer homology, was specifically algorithmicized for torus links $T(n, mn)$, allowing computations of limits that define colored link Floer homology [cite: 36].

## Machine Learning and Topological Deep Learning: The MANTRA Dataset

As algorithms in classical computational topology mature, there is an escalating effort to interface 3-manifold theory with artificial intelligence and machine learning. Historically, graph neural networks (GNNs) have operated strictly on 1-dimensional graph structures (nodes and edges). However, triangulations of 3-manifolds encode higher-order topological information (faces, tetrahedra) that cannot be deduced purely from their 1-skeleton (the underlying graph). For example, the complete graph with 7 vertices triangulates both the connected sum of tori and the connected sum of projective planes, which are topologically distinct [cite: 41].

To address the limitations of standard GNNs and catalyze the field of Topological Deep Learning (TDL), a consortium of researchers released the **MANTRA (Manifold Triangulations Assemblage)** dataset at the International Conference on Learning Representations (ICLR) in 2025 [cite: 41, 42, 43]. 

**Dataset Composition:**
MANTRA is the first large-scale, intrinsically higher-order dataset strictly built from combinatorial topology. It comprises over 43,000 triangulations of 2-dimensional surfaces and over 250,000 triangulations of 3-dimensional manifolds (up to 10 vertices), originally curated by Frank H. Lutz [cite: 41, 44].

**Benchmarking Tasks:**
The dataset provides pre-computed topological labels that act as the ground truth for classification tasks. These include:
*   Betti numbers (computed over $\mathbb{Z}$)
*   Torsion subgroups (e.g., $\mathbb{Z}_2$)
*   Orientability
*   Exact homeomorphism type (e.g., $S^2 \times S^1$, $S^3$, Klein bottle) [cite: 41].

**Experimental Findings:**
The researchers benchmarked various neural networks, including standard Graph Convolutional Networks (GCN), Graph Attention Networks (GAT), Graph Transformers, and Multilayer Perceptrons, against explicitly Simplicial Complex-based models. 
The results definitively showed that standard graph-based models fundamentally struggle to learn topological properties because they lack access to the higher-order interactions of the simplices [cite: 41, 42]. While simplicial complex-based models outperformed the GNNs in capturing basic topological invariants, they still struggled with complex global properties like the orientability of manifolds, signaling that simply passing simplex data to a network is insufficient [cite: 41, 42]. MANTRA has therefore established a rigorous mathematical benchmark forcing AI researchers to design architectures that truly understand cellular homology and discrete geometric structures [cite: 42, 43].

## Software Evolution: SnapPy and Regina

The rapid pace of algorithmic discovery in 2024–2026 was largely sustained by the continuous evolution of two primary software packages: Regina (focused on combinatorial normal surface theory and Pachner graphs) and SnapPy (focused on hyperbolic geometry).

### SnapPy Developments (Versions 3.2 to 3.3.2)
SnapPy, originally derived from Jeff Weeks' SnapPea kernel, underwent major updates in this window, integrating tightly with SageMath and Python 3 [cite: 45, 46].
Key algorithmic additions in versions 3.2 (2025) through 3.3.2 (March 2026) include:
*   **Alternative Length Spectrum Algorithm:** A new, highly robust, verified implementation of the length spectrum algorithm to compute short geodesics within a hyperbolic manifold [cite: 45, 47].
*   **Ribbon Concordance and Slice Obstructions:** Extensive modules were added to search for ribbon disks and ribbon concordances (`ribbon_concordant_links`, `add_band`). Slice obstructions, including the Fox-Milnor test, were programmatically implemented [cite: 45].
*   **Orientable Cusped Census Expansion:** The built-in census of orientable cusped hyperbolic 3-manifolds was expanded to include manifolds with up to 10 ideal tetrahedra, adding over 150,000 new manifolds to the database for testing conjectures (as used by Basilio, Lee, and Malionek) [cite: 45].
*   **Maximal Cusp Area:** A faster and more robust algorithm was deployed to compute the maximal cusp area matrix (`cusp_area_matrix`), crucial for studying topological volume and Dehn fillings [cite: 45].
*   **Isometry Signatures:** The `isometry_signature` command was extended to function robustly on closed 3-manifolds, not just cusped ones [cite: 47].

These software improvements ensure that the theoretical algorithms designed by topologists—whether checking Diophantine inequalities for Dehn surgery or verifying Menasco-Reid via linear algebra on holonomy representations—can be executed at scale in deterministic timeframes.

## Conclusion

The period from 2024 to 2026 represents a golden era of maturation for algorithmic 3-manifold topology. The realization of Thurston's Geometrization Theorem has transitioned from a structural endpoint into a computational beginning. Breakthroughs such as the circumvention of almost normal surfaces for Heegaard genus computation, the strict topological volume bounds governing treewidth and parameterized complexity, the automation of totally geodesic surface detection, and the exhaustive algorithm-driven search for exotic knot traces demonstrate a field operating at peak computational efficiency. 

Furthermore, the introduction of massive datasets like MANTRA bridges the gap between pure mathematics and artificial intelligence, challenging the next generation of machine learning models to grasp the rigid, elegant geometry of 3-manifolds. As software like SnapPy and Regina continue to evolve, the boundary of what is computationally decidable in geometric topology will only continue to expand, transforming abstract geometries into verifiable, manipulable data.

**Sources:**
1. [cantorsparadise.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOaT7MmFxJArS-jlGl-uano43vb4KsVyFoeg3Cny0DouhA0j4UrfH_UmFgrNJzj66bNxHwVD4s1Uf1kMvoXRh8-pDgFiQPGJ9N3X4xoWL0FFg6ZeYaZTxagrLocuPLF1-vDCjo4DyilcuU7N-x52BRzzvfewQwk50Cdb3MgzjnA1bGfQwifpe1FVN7ip2_z6bFZ8FIVnUbGbNVAoFFVtZcBIJUIyreMPgzF6r7)
2. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRjkbbFdMqF5eoquQAdn386bKMi_rlftUe4Q9ipqrZ8ebOm_l3tyNWayZ2FrUFuO80QgUMaQ41iO2ucUL8baeQqralz1u1P2nbOFaWtR0acBy-Uk8Gs4w4bmgz6CIEJkjEwmvFZONm8Kz4eCcy)
3. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhCijG-W6niY7qPSZ7Vez2uocRtWECR-q2DKIPae8lqAiS4OlSyDbqoBSanOLVOh2iUrLxcotbeNRXFd2C5Bjd48WlE5kWUn6yu4el3-XZ8NMN_9UmwWVt_kM=)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGAhvl-vBUKz2DyGTJIpRyV7Va8UlThvN3OfP83rynq9SefrExWP87kpA2Lcu1_Q9HUVr94CG3HPSAEEWjU6NRBMt6qUumnHjemhh3teYaIrp_qaOZdPPp_H8FOdrUlbx8f5G4VpTNDylCH7HmLkLnS_c9TrwnXtMpheK_vUM8DsH-nJzSXNXFkqkF5aLqzrCd0WAOaLw_YsHn6S1mK3oqM1QWX0mo1J8tkz2ezNXkb3Fb-Jsn)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFR0tusWPlmU1A9QlUb9J0pzsxQ5Pbyzd4xPdwRzaZjjm61Ti2oxXEE-jx4Z9r9K_qVEpXTkp-Ablfzj0KrAAScje6nuFA8GLe1ZE5TtlsWziE76PVbM5o9GhD0LfxIjUm61jO_DaepKlkyufdUGBQX0f75NEMi5DHSTm95PGjfIfsHoU7PS4RJaPG5gwYR5BF1uhcJI9qDTT1R_38caG4-hZy4O78=)
6. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERr6LJT-tpkLc0jZjtnkcoNizZDP7xTOlFjTQdOMMDN7ng1fPOeTE4lZFKTmIQAVG96IO0UN_6v_i767tu4LDNziT5qhvwiVpIaCb-T9aMFZaJnartBsodvqjORlX49QursQBH73KkXk5w)
7. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-QnS3yXMwK9cJqpANCAa9KqzkSEEoKD2AfgyWI2_LYEyUyTuE5Gvk5gzlVtGOzZq3LMgjgphx5Z1Osznbn96uFZ-JGAWCCXipJ_-FxCY1kvrcK4yfnJeDnAwKSz0FZG_zQYwVOeAsiafhryo0UgndFg==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7128lUrI0tdnTNjHTD0XH81idDu_i3YmI-xNFlPc7DutqWE9ZFRvV56iE3-QSdc3VfYT8-tbKJQk3ke5P3bYwSio4uexDKhCSkNm9YcFd8jwKAamHq5F-Tw==)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmKZ1nRUbFeRfnkpf0uzvQWUjNct4Fs0cWxneHKMJsprPBxXqg4cqXgrwXxYFK5DfRqGjDt0Oq9WWhAjetxcuxwRGoy_cXljPGbq1tRy6mH5HrXGZ9Sg1O0iMLPFW2gCu1W4r6QpQBp1TzzcAi2yxdek09hX1sThIMdz2oKkMKDxLyc9ZGzLtPU8EjbLIS03FDG21qNhW_zXVjlWWI0A==)
10. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWZJ5pXQCZnWHdIDVrUklvdKI4VmVdb-MdY86o-98fx0-kjA-i7xod_9x9ijYUP3jUrUVKjOPC-JC1mTf4hf-yS-j_4s2nBM83Jiiu0IurRu6KQvdYInAnDjp9PpMRz4LZLoy0wpHzqg==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpBTcVhAPfRHDSBW4BmxcnoN19PpkF1JSlUOonhpISH5TmMAz2T1pF9slzsxdN4avD3_07EXLSWOVmM35qpWRcwS02fctbvIhXNJMyLMypuGcMdi9DIJ2HMg==)
12. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvQkh-y6HWEROSbLgaN0chEeV7cNY5_bZC_wKsHgNV3rEaC-gboiry1NSU_WqX1jz53SdBmjRrTwgxvrMy28_1PvBZPNznTlUsr_kuT5gUMfc-B7VV0SRscEuy5OH-kwRxefG8ITK2MP-hrccJgG78gqWB3FXXUD09SzxZ6ByBkelMJTj36mv2LljtyG7xK4407-_6qmgroOICZUAOctLgT6tq)
13. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPrKmj2olZ-dtkDQfBaKLGMyhoxDY9nArB2-sRwlA9JBwgGD0OlpIJ6jOPsEEx6eeFTJ4FTaiwmL_AjhAj0ax0rNiYNRmop2ZWTtuId82hJqqljXlBDWt8tmM2BFdrR_poBebZhRsMbabVZgv1TFw3HtzT5I1eABfepioK-ubJ-1QIq6VW6ZoioxfXdvy1OB07YZQr7fDQav0OwvMq627lILUZ2S3mxwmnHl8bg2-aRZGbUYKkHAHbbz8=)
14. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDOxmd56Y6iYY2rYa7KQMrzePpa5NMQCl7NeVlV0PpiPKxCzmGh4K7YCuTmQzomMnzwkj_nZi40V-kNmrtLHn7sKPPXx2Zwy4-nzCM7guLZsV9l-IsYhjWQmcc8CbDBQ7uVJs=)
15. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWLPTB7IbHo-_UJFb9vtu74WRUv5BhM0mO_lwkUWagV9aDOmhhIRQs0ZAO7TVh-bCi9vNupReKf6fI1iodnn0gMmbJffKwci7ZAC_50GUXyubN7fxc_NGnYNGP_OA9ESN6_AVdu1D0AnO5t2gf-RT5h87R6DOgoswI5SNqTg==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAvPwCnQfiFBR0i3dF9EOio19UUp_UmgbFcFB9lugP-wyBOs4zhwcj6X-bgItlODS_yTMmuvT3M0cLGaat-o13HbL09zPJW8SCoBh7ozQgVdWjtcVuyarc)
17. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7aktjxEz37OfpC3hOIZCiz1n5UxckooZ5232q3Jv5fCP74KG2T4UeNtL1rbqD905xeJu4XSC2iZIHNkpKgMTz2WmTnJPaLzMx-XHZJlkAm6m8A7OtnGhfPIZe_87YTG1ILOIVlI-MhTpVGXbvLRjEhKpeefoeu4qNAMh9VWrhKJlzcQ4Nii_n4QjSZdp-yqc-G7AUN_A4NRDd5kaTjKpR06ED)
18. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdPx5PI6LfkRjYMe-fKmsTlLkNB7SJuDpRIWc7S0CMRd9NZpZNS1mB8wEgddP4T0rkftvzA82tMiBRqeEpg7qgHovsJ4GXxk8067pwKX3o7_G5-OTSKDbdJyv3PksDks-m_1tJphzsLhonP9s0pl2L3ngbnQz1FsRVESwFOg==)
19. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTnix0UD7xh3rKYtjID-0O_ec6iBrXbzBz8zfFhA5yo9yPVNgvBwu3e6fWNGwv4-J4y2HYMmp3FkRoGNcIvKLTkmisQOfRE4LPMvROG-lG_XPpJ_vi9aEbBMiIWcOuLTyqD82FmRMIVdYOGbvKoIZYV5vW_ssJviXCVvEcdA==)
20. [finn-thompson.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBu5JtQFd5aCSyIApLAVtqVD1BqiH-UhBf3uzCi7c0sOZv59-QZBwrh5rwhVEVHA5-4MT5-1eojKVHVOSBRifIi1IritQBQFrZUVMCDHXGkW-r-Z-iXqXvp4QPrA==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBQLiK0F1zldDa7kZ_zOfXuFBcqIPvfRMmi2GC1HyDiF8cx_uZ441x3YoYkdbD-MXO-mbEjfdHvUXM9Xy9i4KNtRxKMMpzXpGQUml8qruRcUoGGoXQRw==)
22. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGh6jYFjLGuxPJ6AKpNil0aEcZ0MTzqczMp5mbodl2ww_5V8m6AHbgIfGCgHt0a7Ja5sjveIl--itRoiuF-8S3OBVvySFlJXIQ2g-AUSKxbI2AB_XXYLAY8elIfhnwZGepxrkLYVTSz9iWlWIFw_ExxOmfyOzwAuTZlnJpCly1bf1Etv6VL5DfDDISdtVjbf3k=)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEw4tnfztPqb8wCd7rlbRKYwC0naNckBnEnQxYyXv44OwcWXYcXtGCNR78bL89R0VWGnffCSVVYaallOB67phrBB0dQMtrmXlvMmeOcKa0K2PhDBod1bJLfWQ==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoaIW-Z-K3uyShQUK4OuZl5zce9oTsX2_iPkSK-JTfFdPJPxEMoDFGLZmBM9pNWnFA7a9kOkkKDfsYQ1Uu_I-TQmuTQlKMO4wf3NM_V3xZ3xSAgH3grg==)
25. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKlZicZUsrfAcNB0bM0vTWeTtcza1bNh_vhFMNHV0ZA4KWh5JUs7p_jK_V2xl7uTBdnNI0fcUA4_1NepxB_gixu6V9dOBZ93CwBXwm8XvQEpVdH26Wkvl_nDPt_stEWH5Ijn6hx6RFRlaYMzaGww99rWrXT5sR_jYiqOTBFFES_IzS)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKjRSag9Jz-Da2T0Z00ikA-z2etTUlChAzpw7N8T8A5954O0NJeEoHyfubJCGBtfi37vKAkX6LGNb0VrSOA9gO5oMtsEqPDyWzkMzHYXGSusYI-f9s3A==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJmWa4C4sHS3QeUfqCaAmf8Sd6Enkbcq__cJCeHxrToW7jU6PcJPPoXB91WVet9fUE1hBHlhWHAYkWgquALTdoklPhoVkgTPfn79tp7b4HxSHcXT4CYiu_aQ==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBt_ycTy77eiGg098Fd5CjqyAV3Q_zXeOs6PpwTqZ7l9bT0G6adkd8r43NMD30BbmyxK8bwrGHLBwvn3BWU54pmkPQGr28GdwgJGFwn7XwcgyQq5Frng==)
29. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGijpNMQKC9SPJvmzj8qmrMwzp2AFMB9P4YtCfmWujWzltPnP_tfcS6Ad9qVKz3FN6FM4xopmNj9LOKjcaHiCX9cj03AtxVWU3XvoMAJpLQEW2oVOi_9qI8Nxcc4gTFnKp34q8DlepyiZJi_bjljjgO--qm2nMCnMPlfBskXodnULfxCVbDPEOEC9uWHaPMumpqnhjzBJM6IOg3umQYpg0epsuL4ozxXoWC0u6FvQvJrOqCQ0LMmIEPxqVj69yT_Q==)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1Ujxs-1S4zvvksDC56yLAJaIC9CZzCSg2mIDn6H_OPi4P9K4rvB9ddOro10viBK40tgY-X2Cy2kJbecj_MbwuODGMcwVLU5YYdf6PTPIJCy4JvpS7laPGWYQyZmtZJbJveKLlcL-3Z21QOHyUTda_RdA_L7aBBUb89byVRxhEZGo0QsXzY8YS)
31. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlKK56e_wowaTHWKFXcXgCfdjKbTIMoAAYh2ou-ZbUNYlS-0U1SR4INj6qIjrL7VhmrMuEA3nMkKrmwANj72YoTRNtcTSQRJEB1BadDTKaNHd5EYLg0QCQqWI0FD8HlUTnyLdcAHwDXah-HUr18nk3Na5ITxxOcxZPJHkTgxvWTPPtid59jqpSbYQwLaJ_dS9RKYgVNJ2dLXS-TQkvyUlb0FFD)
32. [ista.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGlNH4fAZtlaG0NcXbRQUJ2vRvVZ0bX0-14jdrC8kpKbJFo7vthFpE5F_GIfI_oNjFcuvI6bntAJ0ReCQUreZcz3vzsAiOXs5aEEcCzOzQGYiZyXVryZSffOvKX-Vsh7gfuxh3ftvWrDMz5xZFxddMAjrYo0ODM3Q662YonuMd3yUgV-INrjAw=)
33. [tcu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHw2WWP51UL4RQRAS6OO-4n9YtsOqOPmYv0v4Q5B1KOqNcQJfONndT7bo4z0liSKDoYo4WOY0xwnHITU-Au8km0qNXH61fG1thUjQWVCvBYQBjsIhPMeQmpefsbCVG06k50o-AG46VPaD6mq1B2)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZ421wSjpYsd_JH7qmWgQiyEhZ1SlPKMxiSGSoDJVl1FGlyE1NEAse71Vr1wfKxt2st3jt3KQNGmNuuDLabS056yjmNkqdggTG2sKQDpKZz5tJY2XmDvt3Kw==)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQ5C7Plj3yt7v9xaw3fBCjPo1yXjMMrljDHZPAvOfHftx_x-LHoK_OM1COT4hjNjZ0UQrEgqypZKoHWEGPm0Clld1SsWQt_8fQPEnAkfwHxoV5C1a605kJPw==)
36. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4zjp06qI65vc-nciAGGB-GFcu_kHuS9FAFXoMf4x3f5NcGL-r7ncJo3gU-6h-fyIQ2tJ0Hh8uTfnof9MhLBLfy8u3Lcr6qFJhLXAystkbxnzmP28EGhaIxfQS_BXK4V9HUXo=)
37. [mathinstitutes.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLhjNsPavHl5EKbv9834qN8i_dfqSNUnXBCdLGL60xpaCUxCsXobG_EvE5xJ-HKa3CG1eBOcKcl5zQyf8xkZfN0mlpCvwjKqwNQOtd7mTxwvf5fF5p_gaPnhPv2yNh4uHS)
38. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsFyEZLHnqsxJCTjjcEr9eoGO_t9AveCQAgAGI-5Wu2djFROoeGdmBcj8MQjYpa_XEykFz37nkkFEA36wQG5Ny1V9XGUDLNAoCyAo3trNmOg5IZLEq60bhGFX0VxdwI9DNzBzCxVYBfQr2shkIfcrIV7cLMC5r01IsurAd_jo8Iq_yNKJM260MqlrAmYug0LXo5lT6b_bJ3TBpQx8Xq8cVyc_ZBM7-)
39. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPlKQ84jfzUAPgmhAdx1nuVbfoRcaFmxNO_oiN8BqWK4OmjGmzoa_tdx5BSvIqHZfk4711tMhbL2rXOVaqAtXLd1BIEqBmsihfFU3ad3MmUTcR8euTBhFyQgCydx_DBOcz97wkAVThbfshh8MnmLe4TeCqxz4CVO6A7R-4)
40. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpobqPo1YQjEn6cxXLWS-syCUA5Tik8O0ZsYnYdBQrMkZmVAIEn6gcWNayo1arsaOsLV-rGpAJdJqwU6CVRy5UWDPkhls645_qdCZqs9yOaZ1Q-iE8zrs0BOUt6g2GYxZ6faJF9BKHSY7-1Wz_g32R5w==)
41. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkdCDRpn3_vBesdio_Xj0YUkg6dI74t_fuLtJEjQvrFwHS3VV4bg5Wh-Sq2Bg5I3jPEd0YQYpZxjGZwb7gpoFleSL9zh5MJ7P6wISePiOw9eGmo_KX2f7a5HvYnm4WEZgolvnAunMOj0M_l54IPVOQM0RqgPK2QKsgjb_f5J1Es-UTPzcU8QZ6Lzdnf6uzvLx_lTkv_I2HzgYix4apIhJSnyoY)
42. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPf20NnvYP7crO5SYhWcIpn5EghOhg9k8Wsx6_lLfFOqHVSEKilcsHps1zQo1RfX6IxnMUHQzS6oHvWYiguXs1VdiDOMM3NWo2GexRB0PDbpJIzolZw-3RJcSLX25Q7U9t_dD-3G9_G9v3LRJej2Yypmco_Sof0_ckF9x94TLWe_knPmdHR4DQsZ3v4-e7R9DG2UWW2fD93qdrHkW38dZmq6pzvi072A==)
43. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-DzDtPElIudbKJ8lRgkSSTfHfmuEoTtfz8zFsCJWqzpg-5KIwx04GORcG-ySN3mbbnH1tcg5zx2qkH_T-OVn1hUPxeg53gWXS7aQu7FGOsl6h_2XatraOZA==)
44. [pypi.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJolJIj0HVJQzat-NRTeU_6x6Gu63GKumumRLFKWW7vpT-A_2B3HWv3jjPzAIzqkOzEi-fIW2x5shGFfM8NP4NSMP1xVgUazH-ZhBC0Qhi2xJYUuROnukfoqKnWSGew8zTwrB15A==)
45. [computop.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE74trm7dCv__DHl4QoMVEKbBdkQtuHIDXa16Yy_S6e-q1FETCJmVkA7x2Qtu87Ja2sISNDitFOKUA0SoME0WePETWSzWCiV2tu3no1NJK6g20G)
46. [softpedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtFXkrcPZB9h8w0y8LBYATkGObaffxOsjpTjMwBncksvEAE_eg2cA10WPN1EOw_c4PvCK6YGLBMPujbLtE2tJo6JDYFv6v-Mk3kvq2eVI2sMgAZQ-vP0VU7Dr8wnwUtHjlOI6Y4D8AK4Q2VGs85w3nV_Ji)
47. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2hFekh4weHFVwtuQmq7GrEpjx7k6MLdVXWbmLu1aN-rhM0YR2k0OCN03CI1fBr4OPBeKYYgY4CZuN2f_90J9bitDc25SZML3H9ZEcF0Jmp-ayn6VNMU5ZPHDxY2rFSGaarn5jfA==)

