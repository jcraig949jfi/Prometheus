# Ramsey-theoretic bounds + recent SAT-driven progress 2024-2026

**Pythia queue id:** 215
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdlVXNQYXZtUEJQWFBqTWNQa2NHaS1BaxIXZVVzUGF2bVBCUFhQak1jUGtjR2ktQWs
**Elapsed:** 325s
**Completed at:** 2026-05-21T18:19:43.576274+00:00

---

# Ramsey-Theoretic Bounds and Recent SAT-Driven Progress (2024-2026)

### Leading Paragraph

*   **Transformative Computational Impact**: Recent years (2024–2026) have witnessed a paradigm shift in Ramsey theory, driven heavily by advanced Boolean satisfiability (SAT) solvers coupled with Computer Algebra Systems (CAS) and artificial intelligence.
*   **Major Classical Bounds**: Breakthroughs include the first formally certified proofs of the exact values of $R(3,8) = 28$ and $R(3,9) = 36$, as well as a significant reduction in the upper bound of the elusive $R(5,5)$ from 48 to 46. 
*   **Algorithmic Innovations**: Modern approaches leverage "SAT+CAS" methodologies, Cube-and-Conquer paradigms, and linear programming to bypass the exponential combinatorial explosion that traditionally halted computer searches.
*   **Structural and Variant Graph Progress**: Significant discoveries have been made in off-diagonal variants, multicolor numbers, ordered and cyclic Ramsey numbers, and doubly saturated Ramsey-good graphs, often utilizing newly developed AI frameworks and auto-formalization tools like Lean.
*   **Uncertainty and Open Questions**: While bounds are continually tightening, the exact value of $R(5,5)$ remains heavily debated (likely between 43 and 46), and the scalability of current SAT solvers to $R(6,6)$ or $R(3,10)$ remains a formidable computational challenge.

Ramsey theory, colloquially known as the mathematics of absolute order emerging from chaos, centers on the principle that sufficiently large structures inevitably contain highly organized substructures. The foundational problem asks for the minimum number of nodes in a graph—the Ramsey number—guaranteeing a specific monochromatic geometric shape when its edges are colored. Historically, proving these bounds relied entirely on human mathematical ingenuity, probabilistic bounds, and ad-hoc computer searches. However, the period between 2024 and 2026 has marked a computational renaissance. Through the synergy of high-performance SAT solvers, computer algebra, flag algebras, and emerging Large Language Models (LLMs), mathematicians have broken through decades-old computational walls. This report provides an exhaustive, highly detailed academic synthesis of the theoretical bounds and SAT-driven progress in Ramsey theory over the 2024–2026 period. 

---

## 1. Introduction to Ramsey Theory and Computational Complexity

### 1.1 The Foundations of Ramsey Theory
Initiated by Frank P. Ramsey's 1930 publication *On a Problem of Formal Logic*, Ramsey theory is a foundational branch of combinatorics that studies the conditions under which order must appear [cite: 1, 2]. In its most classical graph-theoretic form, the Ramsey number $R(s, t)$ is defined as the minimum integer $n$ such that every two-coloring (conventionally red and blue) of the edges of a complete graph $K_n$ on $n$ vertices necessarily contains either a red clique of size $s$ or a blue independent set (which equates to a blue clique in the complement graph) of size $t$ [cite: 3, 4].

This problem is frequently illustrated using the "party problem," which asks for the minimum number of guests required to ensure that at least $m$ people mutually know each other, or $n$ people mutually do not know each other [cite: 5, 6]. Due to the symmetry of the complete graph, $R(s, t) = R(t, s)$ [cite: 6]. 

### 1.2 Theoretical Bounds and the Combinatorial Explosion
The existence of Ramsey numbers for all finite $s$ and $n$ is guaranteed by Ramsey's theorem, but determining their exact values is notoriously difficult [cite: 6]. Theoretical bounds were heavily pioneered by Paul Erdős and George Szekeres. Erdős utilized the probabilistic method to establish the first exponential lower bounds for diagonal Ramsey numbers, proving that $2^{k/2} < R(k, k) < 4^{k-1}$ [cite: 3, 6]. A recent theoretical breakthrough by Campos, Griffiths, Morris, and Sahasrabudhe improved the upper bound of the complete graph to $R(k, k) \le (4 - \epsilon)^k$, which was subsequently optimized by Gupta, Ndiaye, Norin, and Wei [cite: 7, 8]. 

Despite these theoretical bounds, computing exact small Ramsey numbers is hampered by severe computational complexity. A complete graph on $n$ vertices possesses $\frac{n(n - 1)}{2} \in O(n^2)$ edges [cite: 3, 9]. Because each edge can be colored in one of two colors, the total search space of possible edge-colorings is $2^{n(n-1)/2}$ [cite: 3]. For a modest graph of 28 vertices, this results in a search space exceeding $6 \times 10^{113}$ possible colorings, vastly outnumbering the estimated atoms in the observable universe [cite: 3, 9]. This unfathomable complexity famously prompted Paul Erdős to remark that if an alien force demanded the exact value of $R(5, 5)$, humanity might successfully compute it by marshaling all its resources, but if the aliens demanded $R(6, 6)$, our only choice would be a preemptive strike [cite: 6, 9].

## 2. The SAT-Driven Methodological Revolution

### 2.1 Boolean Satisfiability (SAT) Solvers in Combinatorics
To breach the combinatorial wall, mathematicians have increasingly turned to Boolean satisfiability (SAT) solvers. A SAT solver is a computer program that takes a Boolean formula, typically expressed in Conjunctive Normal Form (CNF), and determines if there exists a true/false assignment to its variables that makes the entire formula evaluate to True [cite: 1, 9]. If such an assignment exists, the formula is satisfiable (SAT); if not, it is unsatisfiable (UNSAT) [cite: 1, 10]. 

Modern SAT solvers utilize the Conflict-Driven Clause Learning (CDCL) architecture [cite: 1, 11]. CDCL solvers iteratively assign values to variables, propagate logical consequences (unit propagation), and, upon encountering a logical contradiction, analyze the conflict graph to "learn" a new clause. This learned clause prevents the solver from ever exploring that specific flawed region of the search space again, effectively pruning the exponential decision tree [cite: 1, 9]. Over the 2024–2026 period, solvers such as Kissat, CaDiCaL, and AlphaMapleSAT have been highly utilized in Ramsey computations [cite: 3, 12, 13].

### 2.2 SAT Encodings for Ramsey Problems
Transforming a Ramsey problem into a SAT instance involves mapping graph properties to Boolean logic. For each edge $e_{i,j}$ between vertices $i$ and $j$, and each color $c$, a Boolean variable $x_{i,j,c}$ is introduced [cite: 14]. The CNF formula must enforce the following topological constraints:
1.  **Exact Coloring**: Every edge must receive exactly one color. This requires an "at least one color" clause ($\bigvee_c x_{i,j,c}$) and an "at most one color" clause ($\neg x_{i,j,c_1} \lor \neg x_{i,j,c_2}$) [cite: 14].
2.  **Forbidden Subgraphs**: To find a graph that *avoids* a monochromatic clique of size $s$ in color $c$, a clause is added for every potential $s$-clique in the $n$-vertex graph. The clause states that not all edges in this specific subset can be color $c$ (e.g., $\neg e_1 \lor \neg e_2 \lor \dots \lor \neg e_{\binom{s}{2}}$) [cite: 9, 14].

If the SAT solver finds the formula satisfiable, it outputs an $R(s, t)$-good graph, thereby proving that $R(s, t) > n$ [cite: 14, 15]. If the formula is unsatisfiable, it certifies that no such graph exists, contributing to an upper bound proof [cite: 16].

### 2.3 The SAT+CAS Paradigm and Symmetry Breaking
A severe limitation of naive SAT encodings for graph theory is graph isomorphism. Because the vertices of a graph can be permuted without altering the topological structure, a SAT solver might waste vast amounts of time ruling out millions of isomorphic copies of the exact same invalid graph [cite: 3, 17]. To overcome this, recent state-of-the-art approaches employ the SAT+CAS (Computer Algebra System) paradigm [cite: 3, 18]. 

In SAT+CAS, the SAT solver is dynamically coupled with a CAS that understands deep mathematical symmetries [cite: 3]. When the SAT solver finds a partial assignment (a subgraph), the CAS evaluates it. If the subgraph is noncanonical (isomorphic to a previously explored state), the CAS generates a symmetry-breaking clause that guides the SAT solver away from this subgraph and all of its symmetric extensions [cite: 3]. This technique, known as "orderly generation," dramatically prunes the search space [cite: 3]. Specific ablation studies showed that the SAT+CAS paradigm solved the $R(3,6)=18$ problem 7 times faster than a SAT-only solver [cite: 3]. 

### 2.4 Cube-and-Conquer and Formal Verification (DRAT)
For massive proofs, researchers utilize the Cube-and-Conquer method. This hybrid technique uses a look-ahead solver to partition the massive Boolean formula into thousands of smaller, independent subproblems ("cubes"), which are then solved in parallel by CDCL solvers [cite: 9, 11]. 

However, computer-assisted proofs are prone to software bugs. To ensure mathematical rigor, SAT solvers are required to emit proof certificates, typically in the DRAT (Deletion Resolution Asymmetric Tautology) format [cite: 11, 19]. These certificates record every learned clause. Independent, formally verified proof checkers (sometimes implemented in theorem provers like Lean or Coq) read these certificates to validate the unsatisfiability of the formula [cite: 11, 19]. These DRAT proofs can be astonishingly massive, scaling into the terabytes for Ramsey problems [cite: 9, 11].

## 3. Breakthroughs in Classical Diagonal and Off-Diagonal Ramsey Numbers

### 3.1 The Certification of $R(3, 8) = 28$ and $R(3, 9) = 36$
Prior to 2024, the exact values of $R(3, 8)$ and $R(3, 9)$ were believed to be 28 and 36, respectively, based on a 1992 computational paper by McKay and Min [cite: 3, 18]. However, this 1992 result was an unverified computer search that relied heavily on recursive graph enumeration and removing non-canonical graphs, meaning it could not emit a formal mathematical proof certificate [cite: 1, 3, 18]. 

In a landmark achievement published between 2024 and 2025, researchers Conor Duggan, Zhengyu Li, Curtis Bright, and Vijay Ganesh provided the first certifiable proofs of these bounds [cite: 3, 18]. Using the SAT+CAS framework incorporated into a software tool named MathCheck, they seamlessly integrated a SAT solver with orderly generation algorithms to block noncanonical graphs [cite: 3, 5]. 

For the $R(3,8)$ problem, the team chose the AlphaMapleSAT solver, which uses a Monte Carlo Tree Search to rank splitting variables optimally [cite: 3]. To prove that $R(3,8) = 28$, they verified the non-existence of a $(3,8)$-graph on 28 vertices [cite: 3]. For the much larger $R(3,9)$ problem, they relied on a 1968 theoretical reduction by Graver and Yackel, which showed that the existence of a $(3,9)$-graph on 36 vertices implied the existence of a specific $(3,8)$-graph on 27 vertices with exactly 80 edges [cite: 3, 9]. Using the Cube-and-Conquer paradigm, the SAT+CAS system generated 13,700 cubes to partition the $(3,8;27;80)$ search space [cite: 9]. The computation required 245 days of sequential CPU time (reduced to 2 days of real time via parallelization) and generated a massive 1.1-terabyte proof file [cite: 9]. 

### 3.2 The Squeeze on $R(5, 5)$: Lowering the Bound to 46
The diagonal Ramsey number $R(5, 5)$ is perhaps the most famous open problem in the field. It represents the minimum number of guests needed to guarantee a clique of 5 mutual acquaintances or 5 mutual strangers. In 1989, Geoffrey Exoo established the lower bound of 43 ($R(5, 5) \ge 43$) by discovering a valid 2-coloring of $K_{42}$ using simulated annealing [cite: 6, 20]. For decades, the upper bound remained stubborn. In 1997, McKay and Radziszowski established $R(5,5) \le 49$, which they later improved to 48 in 2017 [cite: 6, 21, 22].

In September 2024, Vigleik Angeltveit and Brendan D. McKay published a breakthrough result proving that $R(5, 5) \le 46$ [cite: 4, 21, 23]. The sheer size of $\mathcal{R}(4, 5, n)$—the set of graphs without a 4-clique or 5-independent set—prevented a brute-force approach. For instance, the number of graphs in $\mathcal{R}(4, 5, 23)$ is estimated to be around $10^{11}$ [cite: 4]. To bypass this, Angeltveit and McKay formulated the search as a massive linear programming problem combined with "pointed graphs" and gluing operations [cite: 4, 23, 24]. 

For a hypothetical counterexample graph $F \in \mathcal{R}(5, 5, 46)$ to exist, every vertex within $F$ must have a precisely constrained degree, mathematically proven to fall exclusively in the set $\{21, 22, 23, 24\}$ [cite: 4, 21]. Rather than searching the entire graph, the method considers two adjacent vertices, $a$ and $b$. By examining the intersections of their neighborhoods and non-neighborhoods, the researchers decomposed the hypothetical 46-vertex graph into manageable subgraph structures, applying linear programming to dramatically cull the list of feasible neighborhood degree sequences [cite: 4, 21]. The resulting computational pipeline required roughly 30 CPU years for the initial search and 50 CPU years for independent verification, definitively proving that no 46-vertex graph can avoid a 5-clique and a 5-independent set [cite: 24]. 

### 3.3 Strategies to Further Constrain $R(5,5)$
Efforts to close the gap between 43 and 46 continue into 2025. Thibault Gauthier presented a specialized framework at AITP 2025 designed to systematically lower the upper bound of $R(5,5)$ down to 43 by framing the search as a series of SAT-solvable "gluing problems" [cite: 12]. 

Assuming the existence of a hypothetical graph $K_{43}$ in $\mathcal{R}(5,5,43)$, one can isolate a "splitting vertex" of blue-degree $d$. The graph is thus decomposed into two disjoint sets: its blue neighbors, which must form an $R(4,5,d)$-graph, and its red neighbors, which must form an $R(5,4,42-d)$-graph [cite: 12]. Since $R(4,5) = 25$, it is deduced that the degree $d$ and $42-d$ must both be strictly less than 25, leaving only two feasible cases for the splitting vertex: $d = 18$ and $d = 20$ [cite: 12]. 

The total number of required gluing problems (testing all combinations of valid subgraphs) is astronomically high—estimated at $1.73 \times 10^{24}$ for $d = 18$ [cite: 12]. Gauthier's methodology involves aggressive generalization techniques, proving that many gluing configurations can be handled in a single SAT instance [cite: 12]. Even with this abstraction, the estimated computational cost to fully resolve $R(5,5)$ via this exact pipeline is approximately 42 trillion CPU-hours [cite: 12].

## 4. Advances in Multicolor and Graph-Specific Ramsey Bounds

While classical Ramsey theory uses two colors on complete graphs, the theory extends naturally to multiple colors and arbitrary subgraphs. Recent SAT-driven methodologies have established numerous bounds in this domain. 

### 4.1 Multicolor Classical and Cycle Ramsey Numbers
Multicolor Ramsey numbers $R(G_1, G_2, \dots, G_c)$ define the smallest $n$ where a $c$-coloring of $K_n$ contains a monochromatic $G_i$ in color $i$ [cite: 6, 16]. SAT solvers are uniquely positioned to find lower bounds by searching for highly structured, symmetric colorings (like block Cayley colorings) that satisfy the avoidance criteria [cite: 16]. 
Recent notable 2024–2025 bounds derived from Kissat and CaDiCaL solvers include:
*   $R(K_4, K_4 - e, K_4 - e) \ge 35$ [cite: 16].
*   $R(K_3, K_4, C_4, C_4) \ge 49$ (a 4-color graph problem involving triangles, 4-cliques, and 4-cycles) [cite: 16].

For graphs involving purely cycles, Sun, Yang, Wang, Li, and Xu, as well as Tse, have pushed bounds forward [cite: 16]. Theoretical frameworks combining SAT with semidefinite programming (SDP) and flag algebras recently proved upper bounds such as $R(C_3, C_6, C_6) \le 18$ and $R(C_5, C_6, C_6) \le 17$ [cite: 16]. 

### 4.2 Wheels and Fans Versus Complete Graphs
The Ramsey number for wheels $W_n$ (a cycle of $n-1$ vertices connected to a central hub) and complete graphs is an active area of combinatorial geometry. In 2026, researchers utilized the blow-up technique coupled with SAT and tabu search heuristics to vastly improve bounds [cite: 25]. 
Specifically, previous bounds found via simulated annealing ($R(W_5, K_6) \ge 33$) and block-circulant checking ($R(W_6, K_6) \ge 34$) were entirely superseded. The new SAT-driven blow-up methods definitively established:
*   $R(W_5, K_6) \ge 35$ [cite: 25].
*   $R(W_6, K_6) \ge 35$ [cite: 25].
*   $R(W_5, W_7) \ge 15$ [cite: 25].

### 4.3 Geometric and Lattice Ramsey Numbers
Geometric extensions apply Ramsey theory to lattices and coordinate planes. One prominent problem investigates $R_c(L)$, defined as the least $n$ such that for all $c$-colorings of an $n \times n$ lattice grid, there exists a monochromatic right isosceles triangle forming an 'L' shape [cite: 26]. In late 2023, researchers successfully parallelized two probabilistic SAT solvers to constrain this bound. By formulating the grid coloring as a Boolean satisfiability formula, they discovered a 3-coloring of a $20 \times 20$ grid containing no monochromatic 'L', proving $R_3(L) \ge 21$. Theoretical proofs constrain the upper bound to $R_3(L) \le 2593$ [cite: 26].

## 5. Structural Generalizations: Ordered, Cyclic, and Directed Ramsey Numbers

The Ramsey framework becomes radically more complex when structural constraints are placed upon the vertices, such as strict orderings or directional edges. 

### 5.1 Ordered and Cyclic Ramsey Numbers
Standard Ramsey theory allows the monochromatic subgraph to appear on any arbitrary subset of vertices. In the ordered Ramsey number $R_{ord}(H_1, \dots, H_k)$, the vertices of the complete graph $\{0, 1, \dots, n-1\}$ possess a strict total order. The monochromatic subgraph $H_j$ must not only be found but its vertices must appear in the exact same mathematical sequence as they do in the definition of $H_j$ [cite: 13, 27, 28].

In April 2026, researchers Bašić, Damnjanović, Stevanović, and Stošić presented a comprehensive framework mapping ordered and cyclic Ramsey numbers into CNF clauses specifically tailored for the Kissat solver (winner of the SAT Competition 2024) [cite: 13, 27]. They successfully computed the exact two-color ordered Ramsey numbers for diverse classes including monotone paths, alternating paths, nested matchings, and stars [cite: 13, 27]. For example, they derived precise bounds for quasi-monotone paths $R_{ord}(P_{5, a}^{qmon}, P_{5, b}^{qmon})$ for all sub-variants [cite: 13]. 

Alongside ordered graphs, this team formalized the **Cyclic Ramsey Number** $R_{cyc}(H_1, \dots, H_k)$. Here, the total ordering is relaxed into a cyclic ordering (vertices arranged on a circle) [cite: 13, 27]. The SAT formulation encodes tuples of vertices that increase up to a cyclic permutation [cite: 27]. 

Interestingly, these researchers also deployed a reinforcement learning (RL) framework (Reinforcement Learning for Graph Theory - RLGT) to establish lower bounds [cite: 13, 27]. While the SAT approach natively outperformed the RL agent in exact correctness, the RL model demonstrated powerful heuristic capabilities for zeroing in on high-probability avoidance graphs, indicating a hybrid future for graph-theoretic bound discovery [cite: 13].

### 5.2 Directed Ramsey Numbers (Tournaments)
Directed Ramsey numbers $R(k)$ apply to tournaments—directed graphs where every pair of vertices is connected by exactly one directed edge. A tournament is *transitive* if edges $uv$ and $vw$ guarantee the existence of $uw$. The directed Ramsey number $R(k)$ is the minimum number of vertices ensuring a transitive subtournament of size $k$ [cite: 1, 5].

Classical bounds are known up to $R(6) = 28$. The value of $R(7)$ has been a subject of intense computational pursuit [cite: 6]. Neiman, Mackey, and Heule (2022) leveraged SAT solving techniques—specifically self-subsuming resolution and constraint encodings—to narrow the bounds of $R(7)$ strictly between 34 and 47 [cite: 1, 5, 29]. The lower bound of 34 was established by using SAT to prove that no 33-vertex transitive-free tournament exists [cite: 5]. Their computation required 128 CPU years across 456 parallel threads [cite: 5]. 

### 5.3 Canonical and Unordered Canonical Ramsey Numbers
Canonical Ramsey numbers deal with colorings utilizing an *arbitrary* (potentially infinite) number of colors. The Erdős-Rado Canonical Ramsey Theorem states that for any integer $p$, there exists an integer $ER(p)$ where any edge-coloring of $K_n$ contains a "canonically colored" copy of $K_p$ [cite: 7, 8]. 

A 2025 variant explored by researchers is the Unordered Canonical Ramsey Number $CR(s,t)$ [cite: 7, 8]. This requires the graph to contain either an *orderable* copy of $K_s$ or a *rainbow* copy of $K_t$ (where every edge is a uniquely different color) [cite: 7]. Using integer linear programs and SAT solvers, mathematicians attempted to extract feasibility certificates. While SAT struggled to scale effectively on the unordered properties, exact values for small instances were found, such as $CR(6,3) = 26$ and $CR(3,5) = 13$ [cite: 8]. 

## 6. Doubly Saturated Ramsey-Good Graphs and AI-Assisted Discovery

A pivotal 2026 study by Przybocki, Subercaseaux, Mackey, and Heule introduced a profound structural exploration of the Ramsey space by defining **Doubly Saturated Ramsey-Good Graphs** [cite: 15, 30]. 

### 6.1 Definition and Computational Findings
A graph is considered $R(s, t)$-good if it avoids an $s$-clique and a $t$-independent set [cite: 15]. A graph is *doubly saturated* if it is $R(s, t)$-good, but the fundamental act of either adding *or* removing any single edge destroys its "goodness" (i.e., adding an edge creates an $s$-clique; removing an edge creates a $t$-independent set) [cite: 15, 31]. 

Using an optimized SAT encoding requiring only $O(n^4)$ clauses to enforce the double saturation constraint alongside symmetry-breaking, the team charted this unknown space [cite: 15]. Their experimental results yielded profound structural insights:
*   There is a unique doubly saturated $R(3,3)$-good graph: the 5-cycle ($C_5$) [cite: 15].
*   There are exactly zero doubly saturated $R(3,4)$- or $R(3,6)$-good graphs [cite: 15].
*   The smallest doubly saturated $R(3,7)$-good graph contains 20 vertices, and the smallest $R(4,5)$-good graph contains 19 vertices [cite: 15]. 
*   The 13-vertex Paley graph (a circulant graph with distances $\{1, 3, 4\}$) is exactly one of the six valid doubly saturated $R(4,4)$-good graphs [cite: 15].

### 6.2 Infinite Families and LLM Formalization (Lean)
The most remarkable outcome of this 2026 research was the discovery of infinite families of such graphs. The SAT data outputs were fed into a Large Language Model (LLM). The LLM analyzed the edge-distance geometries of the discrete SAT outputs and successfully identified the generative circulant rules governing them [cite: 15, 31]. 

The resulting theorem proved that for all $t \ge 4$, there exists a doubly saturated $R(4, t)$-good graph precisely on $6t - 11$ vertices [cite: 15]. The proof specifies that by letting $m = t - 2$, a circulant graph on $n = 6m + 1$ vertices with specific chord distances successfully saturates both conditions simultaneously [cite: 15]. 
Crucially, to validate the human-AI hybrid discovery, the researchers used the LLM to auto-formalize the mathematical proof into the **Lean** theorem prover, guaranteeing absolute mathematical truth devoid of human or AI hallucination errors [cite: 11, 15, 31]. 

## 7. Theoretical Synergies: Flag Algebras and Semidefinite Programming

While SAT solvers dominate the search for explicit constructions (lower bounds), upper bounds are often handled by **Flag Algebras**, a method introduced by Alexander Razborov [cite: 8, 32]. 

Flag algebras operate by translating combinatorial subgraph densities into continuous variables, applying the Cauchy-Schwarz inequality, and solving the resulting constraints via Semidefinite Programming (SDP) [cite: 32, 33]. It essentially converts a discrete combinatorial problem into a continuous geometric optimization problem.

In 2024 and 2025, flag algebra computations resulted in tightly bound, strictly computer-assisted proofs for off-diagonal and graph-specific upper bounds [cite: 32, 33]:
*   **Symmetric Ramsey Multiplicity:** The flag algebra method improved upper bounds on the Ramsey multiplicity of $K_4$ and $K_5$ [cite: 33]. For fractional subgraph counting, variables like $c_{3,5} = 24011 \cdot 3^{-12}$ were precisely constrained using SDP [cite: 33].
*   **Graph Ramsey Numbers:** Flag algebras provided rigorous upper bounds for graphs without total symmetry. Recent breakthroughs include proving $R(K_8, C_5) = 29$, characterized by a balanced complete 7-partite graph on 28 vertices [cite: 32]. Furthermore, $R(K_9, C_6) = 41$ (bounded by an 8-partite graph on 40 vertices), and the Ramsey number of a 3-dimensional cube $R(Q_3, Q_3) \le 14$, closely squeezing the known lower bound of 12 [cite: 32].

## 8. Emerging AI Paradigms: The "Coprime Ramsey Number"

The interplay between AI agents and SAT solvers reached a new milestone in early 2026 with the autonomous computational exploration of "Coprime Ramsey Numbers" ($R_{cop}$) [cite: 34]. In this variant, a graph is formed by taking integers $1$ through $n$ and connecting every coprime pair with an edge, followed by a standard two-coloring [cite: 34]. 

In a publicized mathematical exploration, an AI agent (Claude Code) orchestrated a continuous loop of SAT solver querying (using Glucose4 via PySAT) and heuristic analysis. The AI discovered that classical heuristic random sampling failed drastically, estimating $R_{cop}(4) = 20$ due to the extreme rarity of avoiding configurations [cite: 34]. Correcting course by deploying exact SAT formulations, the agent established that the SAT solver instantly found avoiding colorings for all $n \le 58$. However, at $n = 59$ (a prime number), the formula became unsatisfiable, definitively proving $R_{cop}(4) = 59$ [cite: 34]. 

The agent extended this logic to the 3-color version $R_{cop}(3;3) = 53$, noting a statistically significant pattern where the fundamental clique variants all terminated on prime numbers (2, 11, 53, 59) [cite: 34]. This case study highlights a critical evolution in 2026: SAT solvers are no longer just static tools operated by mathematicians, but are now being actively compiled, targeted, and debugged by autonomous AI agents traversing theoretical graph topologies.

## 9. Conclusion and Future Directions

The progress in Ramsey-theoretic bounds between 2024 and 2026 exemplifies the apex of modern computational mathematics. The static boundaries of the 20th century, which relied on human intuition and primitive graph enumeration, have been thoroughly dismantled by the SAT+CAS paradigm, linear programming, and Flag Algebras. 

1.  **The Supremacy of SAT Certifiability:** The resolutions of $R(3,8) = 28$ and $R(3,9) = 36$ via massive, terabyte-scale DRAT proofs [cite: 3, 9] demonstrate that trust in computational math is shifting from algorithm verification to raw cryptographic proof checking.
2.  **The Siege on $R(5,5)$:** The upper bound reduction to 46 by Angeltveit and McKay [cite: 4, 21, 23] represents a masterful blend of linear programming and combinatorial constraints. However, crossing the chasm to the conjectured true value of 43 will likely require traversing Gauthier's 42-trillion-CPU-hour gluing matrix [cite: 12], potentially necessitating next-generation supercomputing or quantum assistance. 
3.  **The Structural Renaissance:** By venturing into doubly saturated Ramsey-good graphs [cite: 15], ordered matchings [cite: 27, 35], and sharp thresholds for books $B_n(k)$ [cite: 2], mathematicians are utilizing tools like Kissat and Lean to uncover continuous infinite families rather than just finite point-bounds. 

Ultimately, Paul Erdős's hypothetical alien invaders might not require a preemptive strike if they ask for $R(6,6)$ a few decades from now. If the computational trajectory established in 2024–2026 holds—where AI heuristic steering, SAT-driven pruning, and CAS symmetry-breaking merge into unified autonomous frameworks—the computation of deep Ramsey limits will shift from mathematical impossibility to a question of sheer machine endurance.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETsE5VdeHwoNDXBZCPMqYhlaocgc2zjSoHhAFgLIDyGi14KZ35diqnw5xMmi8w2Lte4ynX0GktqdSFLGEsVllSayx_kBubjhv52e7rk1El8KVDXYvBPkk6)
2. [intlpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEo5Icgjd08rPJfDEpecN2IyTzyRXoGAujDYdMlbHFoJvA_UpL76BJ4Nf5o6hVSt3JMaFUj1CKB0fykuDMMp4h7D2D-EtZ97pGW_R7bP6KWLPLbRoE5ZFQcmxcwDbx3l0rRqByfvaU=)
3. [curtisbright.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsC_p0hpycDecVf2b5hP6t4NKXUk4kNwEMDGQYgDMAie9snuTz7BUZR5mhtErBZNbqGfVPc9PjrkacKDQi1hIqFT-aeeLbsYG9lFE5til0VzjllCLCzKbjKdP-l64JnKpnCe-XDoDFQ7XwnB4SQY3tqGy6zetK)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQ6YJFbK3D58NxKcWdmq71jhG85zD1poM6wStrPM0OP9xGKFT-H-ytO0KRXzgUWqGCB7VEgxz1cODdruCTxLe7XWsQ7Rzcwc32ZmQeW2Yl1KMcW8Il)
5. [ijcai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIufwYkmQ111T-36K8ZjZaJxgAHk1knktc3j3VvVCfyl6Zqxosabf8hVqgAqEojo9tC05dt-1tBRTLV8XDCFiwfAPxhkIDpPKZsGNLxccfK0SJUmoVE8E1IKTYtbuhb9HbWdNA)
6. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3ofYd0cCpXiE-X_FViml_ok6PTjDfkNH-7taXymiqC8y8IfCPRXrUeyA1SzsjduVqaPTbFaLhJzy2LKtWD5oPhacmm_RLdIF-HxasvQN1f6pHZ4zcUG63aiPRfpqolwwNazpL1Q==)
7. [iastate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGddBmvm7607j4a9d1YNhpO8jsUsTdaREYSUyLOMukDbDMtwEtiSYorjgJ88XZfSlW--JhObKlhoZyEYinLgg_MSWms2LegMCGAzNym08nqQDLXaEPWCnu3I8St29TonCQ1j7iaT80jBEeYREwjnyF0SiT-Rbt0UEHOffBPZFVJpcWo0a4YUR6H)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDBd0B4xL5t_C4yBQYRPz-6dVaHiY8W81M8a2TluArKlha9ktl1p0rYYugieW2uuB4Ub3g6p6q7_TSFov_NrrLjbm97XzqrpAUUD_XAk3as1GOxDDOZ84yYFjBxuDaNzRqy4-N2VYCn8ZgXqbPPoaOT3gGsB9mqUcuVOpANV3QJvHOsaCun3dW6Q31xgFY_J759AH2FJxzanvugFrkACs_kEomhL2Y40Y7bkCGTw==)
9. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfsL4F9LQiYlUasBaVAIOdpJyCWOnPqL1TGPncjMXR5wgY9iV1XDpiLdvZpOpntTbK48QX-Mjx4FzvEtufXLSck6SRvMzBgOPToWaeDKf4R7VO9lzphGUVX5qGjG-KuWN0694V96hNYs-DI5pa5BOW8CmNayFPW4gXNkfO2BLsYnxs9Ofj7k577AkQNcoiMqk=)
10. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVeWRkbdlNWYm5k5Plz8XstZ23vlir7T0TdERfZok5No6BQtQVMJKWEU69nWeTWR3RLrRjx8i32gWd4lPZdVPmmLEvsgPjfj3AgWZeRb1avSKERflnLtZNRDv0UCQ=)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgoUY69AbXyWK-d5RPjYIOpnFwDWkzVK580CFLeNyY_clyQGDKu_1SwOq9L-0RkqfzIpCg84JQBn-IebEH3wQYO9d4ZQw3wIpxz0HOWdah_NFFEhpJU-Gp_qvgJVJzgdijbe0IEHKhw3jVI5f8SsXhxqUpp6F6_KKJ5asSq4K3gPtnqBVcQzo7g41serDEvV5WXhmRsRWJ9emS2mMf5f5uSk5YsWFWwOMhHHUUF23ryO-TzA7mTzlzEcja4KBbdtQ=)
12. [aitp-conference.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqrsATks0smrzDoZD3kdebBt6tTXA_mUj0tf3TV3GYWGL5JE8dVWMIn5hXLWmzikzKqKin_smb7FW7GLQ44jpHGGTT1ZjC8s0-PYP0ptGQf55c2FuylWfygkR-wGQLgftxs5vMzzcY9-BVjSm1bK5NmP3o)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEa5YE5qMC6nWRCqNQAPu9O3r6EznyUeGRF3Sqm4kWuiRfrxZaNPFpcInRcPjkcSLSUdkHuTPjXTJEjuHv7b-YocVproBCwjOToPUPhU0_yWx1jFUTxlyJD)
14. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZj6QMv18tocR3Dy974lnzVdSQIJR0buXvBiKUKUPjjsUR5b3TDS2_YKYVl7qcz9qMuq0HPuO-RKZR1NmxzVS26Xm4I6JT1rv2BEkmMDLzCQ6xob3TbNzzeSpbPsCzUB9cAXFKihUbr_LtjfJu9KCDwSRzYFDBF2PB_GhwDkSsTMsSJkOWudJIRpVmTqf7)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyns_xPOTldiFncT2t2ZngkH9un0BE1U7tkyagnMj1pLfJwfnLByymT1yCLwlJXwwgRSbh0KX57VHUDnU54C0vbjjlcywcBvfjpSP3lLV6VKceqkuh)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEp_6gvZVZawPhwBB8XzO2v6Vy6riz49lq2-J1Qsq0-XS_cAjlK8Fx7pzAiGn_eikbZE0CIwe_N_m7zyklerhDD5sarDilqNHfwThm1Fyt_0Q8kWcdNHHSi)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOV9KdZ4kHxVATz3t5cMh5lQePxtvZZJ8vBgI8ADcdQo-6e-yWmBqbt7G4zcPN2c6_jIWe1AR9p2go2qIGgfcZyTfQlwp1jles0ov0cjHVpApqXXG1lm2HcQ641Y7R2I9LA0L_TQAAvftO8nH_mnyLAoRs9akZBZfIGi5F1mKvPQwKqjw3XVcEt_RkS3ZdRLZBkbMxjQC3Z2q6wqRh4g==)
18. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtahTyMSmVUpbEb-29shkZp2ELV7IIkkAQmqSpIwx0MHegeHyhE9NkjBe85zLeA6Maagu7AKCy2YsKSf1qxp3oUmIzQ0hBPVk2o3nX_eTsYxYTiNSQGeItLoMcecqjGSj-ggGIlSie0qqaxg==)
19. [cmu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5f2_GFyeMvLxhk96JxM8GS37qlD8k24zfsF_O3wj9b5MX3xmm8VhdRBFa55ZZSoJr8OxXxkiLtOqO4804lfiTRC3NwdaXaKaF0kzN_ch9wiK7gJjD_4DULvXRjz0ZFV9L7WPulWGsSS0xF2k=)
20. [wolfram.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZJj-pVlupIRJTmuiv9Tv2QzQxv1_4YwLj6vP-yq0j1F0QOViUe7gJNdHqSTgpUae1w0ZxOLjIe9IiSjirz_EyPF41MC-2Y5MWvsInyNYrKrgkvFvtExAWEuApi1xRHmUnzANx)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzw7UJeSarY71OEy-sNofP9Ki7LmPDlc4rClk0GCwebHRDZ8By2OPvszD_eWElpTLuHydH_IW1dkoOd8Sg-0fxfylwKgjkmuKbHY02MsNA7Jj9VJvygiJa)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8PMDfp7Qq789n63URlQ2ZQLISv48Nt9_8vi7pcpGBXvIiiLwJfB6gVQHUUZipyO-F-1sOR4ib5fmY3-ln-4cGfHra48HUUHkJuiZdhBXLKXBBxIefRV1zJaueuYPIzQ_Eb6DDzYM2cmjkWOjODLIAmmEcFv40rbXx)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGa8_c4n_c19ioQFOl5Dsu_Mb1hLkpMcxll5AYLz9iWjeY8AkfIlvkO8T4XmojcxbriaOfS1DGR6lBmr4QsCeuqnc6AL8rn9TznyKVuocSEDHy38VEI)
24. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgUUsdVJxRp-GNTL8WCrBJV5OWanAsLREx_AYp-3Ps6Q9ymcaX2BvTmGhUyBmi8UlxqbORF8XDbWKqtjsJ5WLF0d_ffPn7NEXXCXNEM8CSL62r1aypRMdY_K0CBuSVQkC2AJsyPp8oC50IjOk7g3Pzcho=)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKlS4fc2perlOoKUncTdfyusHiMjM08lYkYGirSyRAefX_VEo2CDcqVaMXEi3-ifb1Ug2WvDAAgoanTAbdl0mKhDYkOZjt50C_oBonfX178VJ6_YTBD0XK)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPMKwQW8Olu5BJAD9o7h4I9sdEN0rhfguB7lqCB6ToBPBPTFrWn4XIMueDhSc8uduMzA6ZBoZPoAQJoBab6lqblEKs7JZtHX1bsoXwsCPl9S9V3H4C)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUH-V3a8JTwXJjr5-GltAeEKILm1HZTHkSj_XpY9LYI1m-TNu2WE8ewFFQo8YOb_dAVIAJThbdsAsKj0cVV1lmEJZyQ06NJnV8k5euobHbyyCzG7Ql)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjuD14SuXNkyOaFdQLG4K6ABpht8SXi3jFq5df5XA5nbcZgd5z55Tfsv3YswJn42BnsXHK0G2lFwvkUEZjsWSDjAIH8x-_VVv8uFg5d_pCY_KxvqC4)
29. [dblp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeRm55QjJMCLG7MjEtz2-M8xOGo-0jLs-o2AlQ3nVDLXZRLBDHMehHyB_ZxbwtV3oGQ5GQ4gPt7_mmldUYbbMoAVny-icYWjsUCxTy0Zn8jaoQfMs2nN0=)
30. [cmu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQKFCZC0l2bp2T9Ci-0JjSZlpVfokddFOePaAOy-1PiOExCxfI1FO8pNaUXv79B1RoxtO_JiqgoPIOPnsJJ5xalZ95FsTL3UDzHrSrKcBAbTGqbJw=)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1n3RbhFmC_cNiLPUzU9ZgksxdRJWCyjoZ_CmhgzUBt2PtprCf5F10MRMRy3-gC38t6hkcbgi5_IKg50hUhF9qA2J4l7Wu5unyosLWTT_GG_nI5-6q)
32. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6Yg40kPXZrXfkmCB8GS7tpHgyoIywPY7bf6bds0oH9mXS8IADoUbuvj8fxtbcthUHPucuX3ynecmYQxyxHy-XPMygWSewKC4uGViypH1Gwg8sWxZLjlOvnNSfhZ6stwDycQ==)
33. [fu-berlin.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1r4b1NlIWg7mD7lKWF88HnAnl6mVAOV2LcsQCYRHiOxI4Hd8dnaWLfyIV96clzEsd0Jp-G1zbGccc3y90hNr8vBabckA31cohJn_-Ypfm96r1uBMRYgnXut6xemZxltN4kT7PgbAfyCDWfASnw5WdO5IB)
34. [metafunctor.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSQXOiursL2lSjqczj9sJx1fgz-KPbA-nUAuWerZYtKgnQAh3dlTfNqrJhpK1R_R9y0sUYOShWV28MqvweaMI6Bd7cdMRwlVcl1UrcH8zFnz2Q866BagucoiVrNdAC9GqZj6fwEbXW0UYvYOkN4omtOZDGDeiAXHc=)
35. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNAJbf67B3xnqJPxq0Lcnj91_wuDE0jnsg4JI0NgwYl8pStILTDkKQmQhUP3oa3PhKeekJLbCCPWr3yHG7jnXG3rlAYMl2Ru4FuXsaGtAFTPOS-WBcm6egZKs14p5EzfROu-9Bhqlb3BKNpgyk-ADcyB7zK4VYIt1lyMY7tm9kQWGhTLpy-WduS4PW7hh5POU_iW4=)

