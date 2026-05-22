# Followup [FU-2026-05-22-003 <- row9]: While this bolsters confidence in the conjecture and reshapes the landscape of combinatorial group t

**Pythia queue id:** 288
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd3cXdQYXN2eUt2VzZfdU1QN3ZyRDBBOBIXd3F3UGFzdnlLdlc2X3VNUDd2ckQwQTg
**Elapsed:** 249s
**Completed at:** 2026-05-22T01:13:32.277739+00:00

---

# Status Update on the Andrews-Curtis Conjecture: AI Discovery, Low-Dimensional Topology, and Algebraic Bounding (2025–2026)

### Executive Summary
* **The central problem remains unsolved**: The general Andrews-Curtis (AC) conjecture, formulated in 1965, posits that every balanced presentation of the trivial group can be reduced to the standard trivial presentation using a sequence of elementary transformations (Nielsen moves and conjugations). Despite intensive research, the conjecture remains open [cite: 1].
* **General consensus leans toward falsehood**: The prevailing opinion among combinatorial group theorists and topologists is that the Andrews-Curtis conjecture is false [cite: 1, 2, 3]. However, finding a definitive, verifiable counterexample has proven notoriously difficult.
* **AI and Autoformalization breakthroughs**: Recent 2025–2026 efforts have successfully utilized Large Language Models (LLMs) combined with Reinforcement Learning (RL) and Lean formalization to eliminate hundreds of potential counterexamples, notably within the Miller-Schupp family [cite: 4, 5]. 
* **Topological and algebraic advances**: Theoretical bounds have been established for "thickenable" presentations [cite: 6], and structural isomorphisms for Andrews-Curtis groups of non-elementary torsion-free hyperbolic groups have been proven [cite: 7, 8]. A counterexample for the generalized AC conjecture concerning presentations of $\mathbb{Z} \times \mathbb{Z}$ has also been identified using novel winding invariants [cite: 9].

The Andrews-Curtis conjecture exists at the nexus of combinatorial group theory and low-dimensional topology. An answer to this question carries profound implications for our understanding of simple homotopy theory, 3-manifolds, and the smooth 4-dimensional Poincaré conjecture [cite: 9, 10]. While automated theorem proving has made significant strides in verifying known mathematical results, the AC conjecture has stubbornly resisted brute-force computational attacks. Modern AI approaches have recently highlighted the severe difficulty of bridging the gap between competition-level mathematics and open, research-level problems. At the same time, traditional topological methods continue to whittle away at the boundaries of the conjecture, categorizing specific families of presentations where the conjecture either holds with explicit bounds or fails in generalized forms. This brief synthesizes the current status, flagged findings, and attack vectors for the AC conjecture as of mid-2026.

---

## 1. Brief Summary

The Andrews-Curtis (AC) conjecture asks whether every balanced presentation of the trivial group can be transformed into the canonical trivial presentation solely through stable Nielsen transformations and conjugations [cite: 1]. Within the Prometheus context, the conjecture has been surfaced as a prime testing ground for AI-driven mathematical discovery [cite: 4, 5]; recent deployments of RL-guided LLMs formalized in Lean have successfully mapped and trivially reduced 753 specific Miller-Schupp presentations, eliminating them as potential counterexamples [cite: 4], but the general conjecture remains an open, unresolved problem spanning group theory and topology [cite: 11, 12].

---

## 2. Flagged Findings

The landscape of the Andrews-Curtis conjecture has shifted due to several key findings in 2025 and 2026, combining computational brute force, formal verification, and topological invariants. The current consensus—that the conjecture is false—remains intact [cite: 1, 3], but the boundaries of where counterexamples might hide have been significantly constrained. 

### AI-Driven Trivialization and the Research Gap
In late 2025 and early 2026, researchers demonstrated that state-of-the-art Large Language Models, which routinely achieve high performance on olympiad and undergraduate mathematics (such as the IMO or MiniF2F benchmarks), fail completely on research-level reasoning required for the AC conjecture [cite: 4, 5]. To overcome this, researchers built the AC Certifier (ACC), a deterministic autoformalizer in Lean that rigorously verifies AC trivialization paths [cite: 4, 5]. By synthesizing patterns from these Lean proofs into reusable theorem statements and incorporating them into Reinforcement Learning (RL) agents, the system successfully trivialized 753 presentations from the Miller-Schupp (MS) family [cite: 4, 5]. This represents a significant flagged finding: the MS presentations, long considered a rich vein of potential counterexamples, have been systematically eliminated at certain complexity horizons [cite: 4, 5]. 

### Exponential Bounds for Thickenable Presentations
A major theoretical breakthrough was announced by Marc Lackenby in May 2026 regarding "thickenable" group presentations [cite: 6]. A presentation is thickenable if its associated 2-complex embeds in a 3-manifold [cite: 6, 13]. For this specific class of presentations, it is known that the stable Andrews-Curtis conjecture holds [cite: 6]. Lackenby's finding provides an explicit, exponential-type upper bound on the number of stable AC moves required to reduce such presentations to the standard one [cite: 6]. This is flagged as a critical divergence from non-thickenable presentations, where no such bounds are known to exist and where the conjecture is widely suspected to fail [cite: 6].

### Isomorphisms in Hyperbolic Groups
In July 2025, Robert H. Gilman and Alexei G. Myasnikov published results investigating the full Andrews-Curtis group $FAC_k(G)$ and the natural epimorphism $\lambda: FAC_k(G) \to AC_k(G)$ [cite: 7, 8]. They proved that if a group $G$ is non-elementary, torsion-free, and hyperbolic, then $FAC_k(G)$ acts faithfully on every nontrivial orbit of $G^k$ [cite: 7, 14]. Consequently, under these strict geometric conditions, the epimorphism $\lambda$ is an exact isomorphism [cite: 7, 8, 15]. This finding is vital because it shifts the structural understanding of how AC transformations operate on normal generating sets in negatively curved spaces.

### Counterexamples in Generalized and Related Forms
While the classical AC conjecture remains open, related forms have seen counterexamples. A March 2025 paper in *Algebraic & Geometric Topology* introduced a new invariant, the "winding invariant," to distinguish equivalence classes of presentations [cite: 9]. The authors constructed two presentations of the free abelian group $\mathbb{Z} \times \mathbb{Z}$ that have simple homotopy equivalent standard complexes, yet are mathematically proven to not be $Q^{**}$-equivalent [cite: 9]. This resolves a localized version of the generalized Andrews-Curtis conjecture (which posits that simple homotopy equivalence implies Q**-equivalence) in the negative [cite: 9]. Furthermore, at a topology seminar at Oregon State University in May 2025, Nada Bagherifard detailed a 3-dimensional approach to the AC equivalence, asserting a partial connection to 3-manifold equivalence and demonstrating that "a version of the conjecture is not true" [cite: 10, 16].

### Where the Consensus Might Be Wrong
The consensus that the AC conjecture is false relies heavily on the sheer difficulty of finding reduction paths for presentations like the Akbulut-Kirby $AK(3)$ complex [cite: 14, 17]. However, the AC conjecture search space is notoriously pathological. It is entirely possible that the consensus is wrong, and the conjecture is true, but the reduction paths require an astronomically high number of operations that initially increase the relator lengths before collapsing them. As demonstrated by Lackenby [cite: 6], even where the conjecture is true (thickenable presentations), the bounds are exponential. If non-thickenable presentations admit superexponential or Ackermann-like bounds, the lack of empirical trivializations would be perfectly consistent with a true conjecture.

---

## 3. Problem Statement

To interrogate the precise mathematical object underlying the Andrews-Curtis conjecture, one must formalize the concepts of group presentations, balanced presentations, and elementary transformations [cite: 3, 14, 18].

### Group Presentations
Let $F_n$ be a free group of rank $n$ freely generated by a set of generators $X = \{x_1, x_2, \dots, x_n\}$ [cite: 18]. A group presentation $P$ is typically denoted as $P = \langle x_1, \dots, x_n \mid r_1, \dots, r_m \rangle$, where $R = \{r_1, \dots, r_m\}$ is a set of words (relators) in $F_n$ [cite: 8]. The group presented by $P$ is the quotient group $G = F_n / \langle\langle R \rangle\rangle$, where $\langle\langle R \rangle\rangle$ is the normal closure of $R$ in $F_n$ [cite: 3, 9].

A presentation is **balanced** if the number of generators equals the number of relators, i.e., $n = m$ [cite: 1, 18]. The standard or trivial presentation of the trivial group is $\langle x_1, \dots, x_n \mid x_1, \dots, x_n \rangle$ [cite: 3].

### Andrews-Curtis Transformations
Let $U = (u_1, \dots, u_n)$ be an $n$-tuple of elements in $F_n$. The elementary Andrews-Curtis (AC) transformations on $U$ are defined as follows:
1. **Nielsen Transformations on Relators**:
   - $u_i \mapsto u_i u_j$ or $u_i \mapsto u_j u_i$ for $i \neq j$ (multiplication by another relator) [cite: 3, 8].
   - $u_i \mapsto u_i^{-1}$ (inversion of a relator) [cite: 3, 8].
2. **Conjugation**:
   - $u_i \mapsto w u_i w^{-1}$ for any $w \in F_n$ (conjugation of a relator by an arbitrary word in the free group) [cite: 3, 8, 18].

These operations are referred to as Q-transformations [cite: 9]. Two presentations (or equivalently, two $n$-tuples of relators) are said to be AC-equivalent (or Q-equivalent) if one can be transformed into the other via a finite sequence of these elementary AC-transformations [cite: 3, 9].

Sometimes, the definitions are extended to stable operations:
3. **Automorphisms**: $u_i \mapsto \phi(u_i)$ where $\phi \in \text{Aut}(F_n)$ [cite: 9].
4. **Stabilization**: Adding a new generator $x_{n+1}$ and a new relator $r_{n+1} = x_{n+1}$, or the inverse operation (destabilization) [cite: 9].
Operations including 1–3 are called $Q^*$-transformations, and operations 1–4 are called $Q^{**}$-transformations [cite: 9].

### The Core Conjecture
**The Andrews-Curtis Conjecture**: If a balanced presentation $P = \langle x_1, \dots, x_n \mid r_1, \dots, r_n \rangle$ presents the trivial group, then $(r_1, \dots, r_n)$ is AC-equivalent to the trivial basis $(x_1, \dots, x_n)$ [cite: 1, 8]. Equivalently, $P$ can be transformed into the trivial presentation via Q-transformations [cite: 1, 5].

### The Andrews-Curtis Group ($AC_k(G)$) and Full AC Group ($FAC_k(G)$)
In the generalized algebraic study of these transformations, for any group $G$ and integer $k \ge 2$, the AC transformations generate a permutation group. 
Let $G^k$ be the set of all $k$-tuples of elements in $G$. Let $N_k(G) \subset G^k$ be the subset of all $k$-tuples that generate $G$ as a normal subgroup [cite: 7, 8, 15].
The AC transformations act as a permutation group on $N_k(G)$; this group is termed the **Andrews-Curtis group**, denoted $AC_k(G)$ [cite: 7, 8, 15].
Because $N_k(G)$ can possess an exceedingly complex structure, Gilman and Myasnikov interrogate the **full Andrews-Curtis group**, $FAC_k(G)$, which is generated by the AC transformations acting on the much simpler, unconstrained set $G^k$ [cite: 7, 8, 15].

The precise object interrogated in their 2025 work is the natural epimorphism:
$$ \lambda : FAC_k(G) \to AC_k(G) $$
The open mathematical question extending from this is under what conditions $\lambda$ is an isomorphism, which they successfully resolved for non-elementary torsion-free hyperbolic groups [cite: 7, 8].

---

## 4. Status & Bounds

As of 2026, the general Andrews-Curtis conjecture remains open [cite: 11, 12]. There is no known counterexample, but there are numerous "potential counterexamples"—presentations that are known to present the trivial group but for which no AC-trivialization sequence has yet been discovered [cite: 1, 3].

### Last Known Status of Potential Counterexamples
1. **Length 12 and Below**: It has been computationally verified (using genetic algorithms and breadth-first search) that all known balanced presentations of the trivial group where the total length of the relators is $\le 12$ satisfy the conjecture [cite: 19].
2. **The Example $\langle x, y \mid xyx = yxy, x^2 = y^3 \rangle$**: Once thought to be a prime potential counterexample, this presentation was successfully trivialized computationally [cite: 19].
3. **Akbulut-Kirby Examples ($AK(n)$)**: These presentations arise from the study of 4-manifolds [cite: 8]. The $AK(2)$ presentation was previously proven to be AC-trivializable [cite: 14]. However, despite extensive computational efforts utilizing strong equivalence relations and automorphism-moves, $AK(n)$ for $n > 2$ remains unsolved [cite: 14, 17]. Specifically, $AK(3)$ is currently recognized as the shortest (in terms of total relator length) potential counterexample to the conjecture [cite: 14, 17].
4. **Miller-Schupp (MS) Family**: The 2025/2026 work by Zhang et al. utilizing RL and the Lean autoformalizer ACC managed to solve 753 presentations belonging to the Miller-Schupp family, definitively eliminating them as potential counterexamples [cite: 4, 5].

### Current Best Bounds and Conditional Qualifiers
When considering the length and complexity of trivialization paths, the AC search space is characterized by massive combinatorial explosions. 
- **Non-Thickenable Presentations**: There are no known upper bounds on the number of moves required to trivialize an arbitrary balanced presentation of the trivial group [cite: 6]. Paths to trivialization frequently require intermediate states where the total length of the relators is exponentially larger than the initial state [cite: 3, 14].
- **Thickenable Presentations**: A significant conditional qualifier exists for "thickenable" group presentations (presentations where the associated 2-complex can be embedded into a 3-manifold) [cite: 6, 13]. Marc Lackenby (2026) has shown that for this restricted class, the stable Andrews-Curtis conjecture holds, and critically, there is an **explicit exponential-type upper bound** on the number of stable AC moves required [cite: 6]. This bounds the depth of the search tree required to computationally verify such presentations, standing in sharp contrast to the unbounded nature of non-thickenable spaces [cite: 6].
- **Hyperbolic Group Orbits**: For non-elementary torsion-free hyperbolic groups, the action of $FAC_k(G)$ is strictly faithful on every nontrivial orbit of $G^k$, bounding the behavioral complexity of the permutation group by structurally linking it directly to $AC_k(G)$ [cite: 7, 8, 15].

---

## 5. Literature (Primary Sources)

The following represent the primary source literature tracking the evolution and most recent advancements regarding the Andrews-Curtis conjecture in 2025 and 2026, alongside foundational algorithmic papers.

* **[cite: 4, 5, 20]** Zhang, C., Zhou, A., George, R. J., Gukov, S., & Anandkumar, A. (2025). *AI-Driven Mathematical Discovery for the Andrews–Curtis Conjecture*. MATH-AI: The 5th Workshop on Mathematical Reasoning and AI at NeurIPS 2025. [OpenReview ID: lt3Lpa4d2d].
* **[cite: 7, 8, 14, 15]** Gilman, R. H., & Myasnikov, A. G. (July 4, 2025). *Andrews-Curtis groups*. Journal of Groups, Complexity, Cryptology, Volume 16, Issue 1 (Special issue in memory of Ben Fine), 7:1–7:7. [arXiv:2506.23031 [math.GR]]. DOI: 10.46298/jgcc.2025.15972.
* **[cite: 6, 13]** Lackenby, M. (May 18, 2026). *The stable Andrews-Curtis conjecture for thickenable group presentations*. Oxford Topology Seminar, Mathematical Institute, University of Oxford.
* **[cite: 9]** (March 5, 2025). *Algebraic & Geometric Topology*, Volume 25, Number 1. Contains findings on the winding invariant distinguishing $Q^{**}$-equivalence in $\mathbb{Z} \times \mathbb{Z}$ [cf. Evans, winding invariants].
* **[cite: 10, 16]** Bagherifard, N. (May 12, 2025). *A 3-dimensional approach to the Andrews-Curtis Conjecture*. Geometry and Topology Seminar, Department of Mathematics, Oregon State University.
* **[cite: 18]** Google DeepMind. (February 3, 2026). *Formal-conjectures Issue #2144: Andrews-Curtis conjecture*. GitHub.
* **[cite: 2, 3]** Gilman, R. H., Miasnikov, A., & Shpilrain, V. *Breadth-First Search and the Andrews-Curtis Conjecture*.
* **[cite: 17]** (September 1, 2016). *Conjugacy search problem and the Andrews-Curtis conjecture*. [arXiv:1609.00325].
* **[cite: 19]** Miasnikov, A. D. (April 21, 2003). *Genetic algorithms and the Andrews-Curtis conjecture*. International Journal of Algebra and Computation, Vol. 9 No. 6 (1999) 671-686. [arXiv:math/0304306 [math.GR]].
* **[cite: 12]** Roman'kov, V. (May 19, 2023). *On the Andrews-Curtis groups: non-finite presentability*. [arXiv:2305.11838].

---

## 6. Attack Vectors

The effort to crack the Andrews-Curtis conjecture is distributed across classical algorithmic searches, topological invariant analysis, and cutting-edge artificial intelligence methodologies. 

### Exhausted Approaches
1. **Basic Breadth-First Search (BFS)**: Early computational attacks relied on BFS of the tree of equivalent presentations [cite: 2]. While BFS was able to outperform genetic algorithms in specific regimes (extracting provably shortest proofs for length 13 cases with two generators), it rapidly exhausts available memory and computational time [cite: 2]. The search space grows exponentially, and BFS cannot penetrate deep enough to find the massive temporary length expansions required for complex trivializations [cite: 2, 3, 14].
2. **Genetic Algorithms**: Non-deterministic approaches like genetic algorithms were deployed in the early 2000s to test the conjecture [cite: 19]. These algorithms were successful in proving the conjecture for all balanced presentations of the trivial group with a total relator length of at most 12, including the infamous $\langle x, y \mid xyx = yxy, x^2 = y^3 \rangle$ [cite: 19]. However, genetic algorithms suffer from local minima—they struggle when the fitness landscape requires a long sequence of operations that temporarily degrade the fitness (increase relator length) [cite: 3, 19].

### Live Techniques

#### 1. AI-Driven Reinforcement Learning and Autoformalization
In analyzing the performance of LLMs on the AC conjecture, we observe a classic `PATTERN_BASE_RATE_NEGLECT`: the assumption that models demonstrating high proficiency on competition-level benchmarks (e.g., IMO, MiniF2F, PutnamBench) will seamlessly transition to open mathematical research [cite: 4, 5]. The base rate of success in unguided, research-level combinatorial group theory is exceedingly low because these spaces lack dense human-provided intermediate lemmas. LLM theorem provers fail on research-level AC reasoning out-of-the-box [cite: 4, 5].

To correct for this, Zhang et al. (2025) developed a live pipeline:
* **Lean Formalization**: The AC conjecture was formalized in the Lean proof assistant [cite: 4, 5]. A deterministic autoformalizer, the AC Certifier (ACC), was built to rigorously verify AC trivialization paths and produce the corresponding Lean proofs [cite: 4, 5]. DeepMind's formal conjectures tracker (Feb 2026) notes that prerequisites for full AC formalization include basic group theory, conjugation operations, and defining Nielsen transformations on relators (which are distinct from standard Nielsen moves on generators in Mathlib) [cite: 18].
* **Theorem Discovery and RL Integration**: LLMs are leveraged not as end-to-end provers, but for *theorem discovery*—synthesizing patterns from ACC-generated proofs into reusable theorem statements [cite: 4, 5]. These intermediate theorems are then injected into a Reinforcement Learning (RL) agent. 
* **Horizon Scaling**: The RL agents are trained to find AC trivialization paths. Furthermore, when deploying reinforcement learning agents to navigate the AC equivalence graph, researchers encountered limitations akin to a `PATTERN_VRAM_TRUNCATION_ARTIFACT`. Specifically, the search space for AC trivializations often requires temporarily expanding the word length of the relators before a reduction can occur. When RL agents are constrained by truncated horizon lengths (sparse rewards), they fail. Zhang et al. demonstrated that theorem incorporation allows agents to succeed at much longer horizons. For instance, scaling the horizon length to 1024 and 8192 yielded substantially higher solved counts (282 solves compared to just 21 without theorem incorporation at length 8192) [cite: 5]. This technique definitively solved 753 Miller-Schupp presentations [cite: 4, 5].

#### 2. Topological Invariants and Algebraic Epimorphisms
* **Winding Invariants**: To differentiate presentations that have simple homotopy equivalent standard complexes, topologists have developed new algebraic invariants over group rings. The "winding invariant" evaluated in $GL_2(\mathbb{Z}[F_n])/GE_2(\mathbb{Z}[F_n])$ has been actively used in 2025 to prove that certain presentations of $\mathbb{Z} \times \mathbb{Z}$ are not $Q^{**}$-equivalent, directly attacking the generalized AC conjecture [cite: 9]. 
* **Geometric Group Theory**: The approach of Gilman and Myasnikov (2025) attacks the structure of the AC transformations holistically. Instead of looking at individual paths, they analyze the full permutation group $FAC_k(G)$ [cite: 7, 8, 14]. By applying techniques from the theory of hyperbolic groups and equations over groups, they proved that $\lambda : FAC_k(G) \to AC_k(G)$ is an isomorphism for non-elementary torsion-free hyperbolic groups, effectively demonstrating that the ambient geometry of the group dictates the structural fidelity of the Andrews-Curtis operations [cite: 7, 8, 15].

#### 3. 3-Dimensional and 4-Dimensional Mapping
Topological approaches involve translating the algebraic problem into the language of manifolds [cite: 9, 10]. 
* **3-Manifold Equivalence**: Bagherifard (2025) maps AC equivalence to a notion of equivalence on certain families of 3-manifolds, using this geometry to demonstrate localized failures of the conjecture [cite: 10, 16].
* **Thickenability**: Lackenby's (2026) approach utilizes the concept of "thickening" a 2-complex into a 3-manifold [cite: 6, 13]. If the presentation is thickenable, standard 3-manifold techniques (likely involving hierarchies or normal surface theory) can be brought to bear, bounding the complexity of the topological deformations (and hence the algebraic AC moves) to explicit exponential limits [cite: 6]. 

---

## 7. Cross-References

The Andrews-Curtis conjecture is a foundational linchpin, closely coupled with several major open problems and candidate primitives across algebra and topology.

### Related Open Problems
1. **The Zeeman Conjecture on Collapsibility**: Proposed by E.C. Zeeman, this conjecture states that if $K$ is a finite contractible 2-dimensional CW-complex, then the Cartesian product $K \times I$ (where $I$ is the unit interval) is collapsible [cite: 1]. It is mathematically proven that the Zeeman conjecture implies the Andrews-Curtis conjecture [cite: 1]. Thus, if the AC conjecture is false, the Zeeman conjecture must also be false.
2. **The Smooth 4-Dimensional Poincaré Conjecture**: The AC conjecture is deeply entangled with the classification of 4-manifolds. It is widely noted that the AC conjecture and the smooth 4-dimensional Poincaré conjecture are connected, and there is a contingent of mathematicians who suspect both conjectures may be incorrect [cite: 10, 16]. Constructing a counterexample to the AC conjecture via 2-complexes could provide the necessary skeletal structure to construct exotic smooth 4-spheres.
3. **The Generalized Andrews-Curtis Conjecture**: This states that any two presentations $P$ and $Q$ with simple homotopy equivalent standard complexes $K_P$ and $K_Q$ are $Q^{**}$-equivalent [cite: 9]. As of 2025, this has been shown to be false for $\mathbb{Z} \times \mathbb{Z}$ via winding invariants [cite: 9].

### Anti-Anchors and Potential Counterexamples
1. **The Akbulut-Kirby Examples $AK(n)$**: These presentations are derived from 4-manifold theory and are standard anti-anchors in the search for counterexamples. The presentation $AK(n)$ is a balanced presentation of the trivial group with relators $(x^n y^{-(n-1)}, x y x y^{-1} x^{-1} y^{-1})$ [cite: 8]. While $AK(2)$ was proven AC-trivializable [cite: 14], $AK(3)$ remains the shortest, most famous unresolved potential counterexample [cite: 14, 17].
2. **The Miller-Schupp (MS) Presentations**: A family of presentations long suspected to harbor counterexamples. Thanks to AI-driven RL in 2025/2026, 753 of these have been trivialized, shrinking the pool of viable anti-anchors in this family [cite: 4, 5]. 
3. **Finite Presentability of AC Groups**: A related question is whether the groups $AC(F_r)$ are finitely presented. Roman'kov (2023) defined a class of generalized AC groups $A_{r,s}$ and proved that $A_{2,s}$ is non-finitely presented, implying that the standard Andrews-Curtis group $AC(F_2)$ is non-finitely presented [cite: 12]. This reveals the underlying wildness of the transformation space.

### Candidate Primitives
* **Standard 2-Complexes**: The translation of algebraic words into 2-dimensional CW-complexes ($K_P$) remains the core primitive for analyzing AC equivalence through simple homotopy [cite: 9].
* **Equations over Hyperbolic Groups**: Used as a primitive by Gilman and Myasnikov to control the behavior of the full AC group $FAC_k(G)$ [cite: 8, 21].
* **Lean Formalization (ACC)**: The AC Certifier (ACC) code base, which defines Nielsen transformations on relators and synthesizes automated theorem bounds into Lean, represents a new digital primitive for future computational attacks on group theoretic conjectures [cite: 4, 5, 18].

**Sources:**
1. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVUPpBhNLRGXanFC7hIr-eKf4BXv8MzmJ7KwvsT1n2-mhknY-esDc3vHyLal0-Ic33O54nGoYDiZ_5iOdXLYPRnPQgG67x1o-k442y6lmXXEM8BcF-1fNsFTGHyvw-6NEAf9MJgWr0YOHDNfeCVifBog1M6FI=)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvxxaV_n7rn9YBNs48H4jz1BYhCfprPrId8IKiEDVnCo26Ap0b8w0Xb-1zsZeAQSLO4qOuLJYRQpTl649DZs5W9_kDxnSPHNE6piryHfLX6l0iO2Q4EBMRe37uX160VjTdSuPDvg0mo4dcSoeDP1s0v3dpV_iHgYEyX4AsriJLUxH4RYJEI5gUWYBdaoL36bKciAs0tTto0y6VpQ3XIw==)
3. [stevens.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhC0IEaDN0Qcu_B94ayMcdQcFzKevANWzYKOOF_tjmAJRjE11DMf8-SdjF2ktda4p1psp9uJEQgGaGTvdnVR-9Krsd_dzP5LjIjDgLHrrUPDusya00V5FKtCez0kjdwJb0yY7_DoJ-NexPf7HIzN_HJMTAAaRwgzPkpHa0S88yANVfgAw=)
4. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHY3NMO6ZywxlJ5qB0FAfXPVn5s7qhGcPq-WOCicPSPOwv4HP4LO2ilHGQfvagZ7ePHpW0EfnU5_p7rcKweYPBvAsWzhuG2rlbFN6_5OZiPVI1h6nNGCohG6DFppA==)
5. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0l26nhu2DuwtdWtatW8kL7eiimBfJNzaQ44-nzVcNPf_d-lZug3NtV6cee0gjnEiUr69DaBwlO60h97G45xsyXEVm1UVvmgV9HYVTg3BHtew69jw_M2Nt-WJYBc2Q)
6. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5BbKn_4fQIivyj-zBkLL0xRXTfI9OePeNb1pNCNbvsWTjO6nKABOqY59kchLe58WyFOht6OPJG5vIGOS8Lf-bzvoUXxJ11FUamGDQ_XgdN2OvY6HkQPNpVbn-)
7. [episciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZz0bAIHGd-OGFwQdOb8JgT0572MKcCkGFwDYgVQoUmFc_sonKZD4-Cg3ULLwiRY90w9JzQDME8YvpJZ4EJTZPLVzvoN2PmEUuVpTWwT-QqLKtWnJz5_M=)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF91hEXayjNM4MiZlTKKcvWSa6Uk50i7KaG4Ly1EPsk7wKBczkJeRgZ7EiT6ZoOWaEikjbkgRtrUVm0IliL1PIP82YSexzT4cctD9-BstghLT8X5j5G2g==)
9. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHReGPIHBbbiOnSVjcWPoKc-gUnjalTGSH1cneZl_-AaGwAERAEH1Zo34BryHin2nu14fA4zCOxvXJ1xEbiPPLmOOZM2UOwix3nRegKsrSDAd0md1dLUkDBo7NCOEbAwAx8630sMAWUNQ==)
10. [oregonstate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhJf1DqSdRmBG_Rc6VFoSOwMfoyS2-TxN2Fi0xYNlBmBB-GHBagsJW6htcbYev3rZRppQtdAlN7gdAGI2HzPSsdDBddP5B3sY13RTMVlYqKkS8wMnpvkhP7sGgqDe9S4jBeJk8m-XkUYNvkYfxd05Smpz6YTt9hFgOcsLRxGOZZbg3n--ixVkk4HgTbkVTScaR-u3dIMUnE_108T9iEzon02mdhmXPShQASHtFCL_wCy16p84=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2gTfavQhjgww16Ke2ASUl_FumeAw6ijhgEhgvw62lACq6T9wxL_OMm0Wi1-Dmb8cUMQx-jDJuoiVeg5-F7KAAC2QNxOct45z1G5v6G7QCb24-X7xyvkvM)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-jePG6treY3v0rrHr_CREhkUPl75fFiguwse1qxPVncRqFKodVf4wpa0IZi7Li9yQsL24fYunIRJQM_tqAEpwoTIFn6Ib-W6NBR3tiPWouzOtdZmAKg==)
13. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyrH4p3SIf9QDjjLACmxDWztEmpcYQOE1ZqKsjREUhM7kn6sPe9UgB-bAbaQjuggs04Znzhqn1EJ9g9HK2HjeZAwJBVGcjwEd7d4ESzFZ_tBvKwu59AvO8eKXG3M_HSQKg7w==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFm9kmH1gcCcyF3sC09lJOSPuikkLFY4szT6d20Powmqc70IgGJ0VFtkBFZVbKINo2AF6Fs8ujHbQGpHuonKExUPP1ql5yJm4VC24VW1ylm2hRyQcYKJYfqHw==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEESMz3of7zPjlscDd1JfUvDz9nKO0Dd-vdN5JJXe08AGu625kWZYOpe6zbHmQC9tGubhWzReaMPjx6GcECtRt6kH-NowLml_Aa0ZdufsGoV22FYZ7Mfg==)
16. [gatech.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFh0bk1kiFA14CMQTLKKR2lW-Ptmp1sQ7s_UwXNcCr2mGaECbzrdrdzaaQQxj6ofkUlERfe34ZW5k7OduQcxZNHY3qG6BlhHLG1yrssnPVlACVbRi_ZxTr7T3jgHPO9HngVqRRc2Vri9EKfyx_1U-4S02LVhA==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdNyOO9Rptn35b5dq4s4ai5oJAbZMXY2cthFeHOwzoU4u0wzGgGZSRcuKC1LKt2JuQYJMuLpaOjWaK2aHq7YhpNP6nsZMi7FOrE97HQRtbDtJdhlbnrw==)
18. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0RjaIA7ZU1yiM8M-NjP6F9WiPwKNHsigC7rl-LeZQXXHQtWlKd-JBE0qsji_u_AXiksv6SPeudtODJBnSich_oRVluU7TwDItSWa7JHykHbQt0FzFwMEgBon1QdFo1muYzP7F9mrsaUJUBp2m6gJbsFDsPxti2g==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-6gdz09tFXTNJexB8Ek-LgJ-dfwZbBGmE84CC8EGo6ziNJdrlCRO-7dI3Vr9z27kXiF6li6Mm-1obxLd-Tmt2ow0WvjaH1dFTtfyaPSZHBqAsGzMXmF9E)
20. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFP2KSwWHxapunTB4HTQZ3lwnVPqCXCTnoJtjIcjXCZV_UtCcSGRmMHX5jnmyy_h0kMIa5fQCFxgTFCe8AKx9pofxoI6RLyBEC9TfRJH_oc-eJb1ErsSq3yDsW4-9LLdrwXA-tVusgtqqHF0GQSHFCTUWBSh8VH0RsjwfXeSMjuWT1guG845BwDN-0HRhBXIHtNwUmpkRmdDBNNiZlfLq3Lycy7HGcXBaSbDgp8kYsWRhZO1FbmgXdtoBdoMjkf)
21. [episciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFATRMn0lKthGh6AeFoJA7rNdLb0F-cnKfcH7zy-nMBxTgzc_3U19JkDu5IP-U23ReVudJH3nlTCfv-m-EeGBzUkYwnZ_t5wmw1AaXt5UdWBU0JMaa3lO0AStbP)

