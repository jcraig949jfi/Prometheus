# Isogeny graph structure for elliptic curves (volcanoes, Sutherland 2013) 2024-2026 extensions

**Pythia queue id:** 162
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChczelVQYXZ5bUJvZXlqTWNQN3EtRXdBaxIXM3pVUGF2eW1Cb2V5ak1jUDdxLUV3QWs
**Elapsed:** 257s
**Completed at:** 2026-05-21T16:46:25.400490+00:00

---

# Isogeny Graph Structure for Elliptic Curves: From Sutherland's Volcanoes (2013) to 2024–2026 Extensions

**Key Points:**
*   Research confirms that the structure of ordinary isogeny graphs over finite fields takes the explicit form of an $\ell$-isogeny volcano, a concept heavily formalized by Andrew Sutherland in 2013. 
*   Between 2024 and 2026, the theory of isogeny graphs was significantly extended, notably by adding $\Gamma_0(N)$, $\Gamma_1(N)$, and $\Gamma(N)$ level structures to ordinary volcanoes (Perrin and Voloch, 2025).
*   Recent breakthroughs (Galbraith, Gilchrist, and Robert, 2024-2025) have improved algorithms for climbing tall isogeny volcanoes, dropping worst-case complexities from $\tilde{O}(q^{1.5})$ to $\tilde{O}(q^{1/4})$ using Kani's lemma and sesquilinear pairings.
*   While ordinary curves form volcano structures, supersingular curves form optimal expander graphs. Recent work (Arpin, Scheidler, and Hedayat, 2025) has explored the "spine" of these supersingular graphs (vertices over $\mathbb{F}_p$), revealing wave-shaped structural patterns that challenge the standard heuristic of graph randomness in cryptographic security proofs.
*   The "Inverse Volcano Problem"—determining if any abstract volcano can be realized over a finite field—was rigorously answered in the affirmative by Bambury, Campagna, and Pazuki.

**Executive Summary:**
The mathematical landscape of elliptic curves over finite fields is intrinsically mapped by isogeny graphs. An isogeny is a non-constant algebraic morphism between two elliptic curves that preserves the identity element. When mapping out the network of these curves (vertices) and the $\ell$-isogenies connecting them (edges), highly structured geometric patterns emerge. For ordinary elliptic curves, this structure is universally recognized as the "isogeny volcano," a term popularized by Fouquet and Morain and rigorously computationally detailed by Andrew Sutherland in 2013. The volcano consists of a "crater" (the surface level), underlying "levels," and a "floor," dictated by the endomorphism rings of the curves.

As post-quantum cryptography—specifically isogeny-based cryptography—matured, the necessity to deeply understand and manipulate these graphs intensified. While supersingular graphs (which do not form volcanoes but rather Ramanujan expander graphs) are primarily used for cryptographic protocols, ordinary volcanoes remain critical for pairing-based cryptography, point counting (the SEA algorithm), and discrete logarithm reductions. The years 2024 to 2026 marked a renaissance in isogeny graph research. Mathematicians extended the classical volcano model by attaching level structures to the vertices, fundamentally altering the graph's crater dynamics. Concurrently, new algorithms leveraging higher-dimensional representations and sesquilinear pairings allowed for exponentially faster traversals of "tall" volcanoes. Meanwhile, deep structural analyses of supersingular graphs over $\mathbb{F}_p$ (the "spine") have begun to uncover non-random structural anomalies, carrying profound implications for the security assumptions of tomorrow's cryptographic standards.

This report comprehensively details the foundational framework of isogeny volcanoes as established by Sutherland and synthesizes the advanced theoretical and algorithmic extensions developed between 2024 and 2026. 

***

## 1. Introduction to Elliptic Curves and Isogenies

To comprehend the complex topology of isogeny graphs, one must first establish the fundamental properties of elliptic curves over finite fields. An elliptic curve \(E\) defined over a field \(k\) is a smooth, projective algebraic curve of genus one, equipped with a distinguished \(k\)-rational base point denoted as \(\mathcal{O}\) (the identity element) [cite: 1, 2]. The set of points on an elliptic curve forms an abelian group.

An **isogeny** \(\phi: E_1 \to E_2\) between two elliptic curves is a non-constant rational map (a morphism) that maps the identity of \(E_1\) to the identity of \(E_2\) [cite: 1, 2]. Because elliptic curves are group varieties, an isogeny is automatically a group homomorphism. The degree of an isogeny is its degree as a rational map; if the degree is a prime number \(\ell\), it is referred to as an \(\ell\)-isogeny [cite: 1, 3]. For every separable isogeny \(\phi: E_1 \to E_2\) of degree \(\ell\), there exists a unique "dual isogeny" \(\hat{\phi}: E_2 \to E_1\) of degree \(\ell\) such that the composition \(\phi \circ \hat{\phi} = \hat{\phi} \circ \phi = [\ell]\), where \([\ell]\) denotes the multiplication-by-\(\ell\) map on the respective curves [cite: 4, 5].

Elliptic curves over a finite field \(\mathbb{F}_q\) (where \(q = p^n\), for a prime \(p\)) are classified into two disjoint categories based on their endomorphism rings:
1.  **Ordinary Elliptic Curves:** The endomorphism ring \(\text{End}(E)\) is an order \(\mathcal{O}\) in an imaginary quadratic field \(K = \mathbb{Q}(\sqrt{-D})\) [cite: 3, 6]. Ordinary curves have a group of \(p\)-torsion points over the algebraic closure \(\overline{\mathbb{F}}_q\) that is isomorphic to \(\mathbb{Z}/p\mathbb{Z}\).
2.  **Supersingular Elliptic Curves:** The endomorphism ring \(\text{End}(E)\) is a maximal order in a quaternion algebra over \(\mathbb{Q}\) [cite: 7, 8]. These curves have no \(p\)-torsion points over \(\overline{\mathbb{F}}_q\).

The set of \(\mathbb{F}_q\)-isomorphism classes of elliptic curves can be identified via their \(j\)-invariants [cite: 4, 6]. For a fixed prime \(\ell \neq p\), the **\(\ell\)-isogeny graph** \(X_\ell(\mathbb{F}_q)\) is a directed graph where the vertices are the \(j\)-invariants of elliptic curves defined over \(\mathbb{F}_q\), and directed edges exist from \(j_1\) to \(j_2\) if there is an \(\ell\)-isogeny connecting the corresponding curves [cite: 4, 6]. Due to the existence of the dual isogeny, if there is an edge from \(j_1\) to \(j_2\), there is also an edge from \(j_2\) to \(j_1\). Therefore, barring exceptional curves with automorphisms (specifically \(j = 0\) and \(j = 1728\)), these graphs can be treated as undirected multi-graphs [cite: 5, 6].

The structure of these graphs varies wildly depending on whether the curves are ordinary or supersingular. Supersingular components form highly connected, optimal Ramanujan expander graphs [cite: 8, 9], which makes them ideal for cryptographic protocols because taking a random walk quickly approaches a uniform distribution. Conversely, the ordinary components form highly regular, stratified geometric structures known as **isogeny volcanoes** [cite: 3, 10].

## 2. The Foundational Framework: Sutherland (2013) and Isogeny Volcanoes

The term "volcano" was originally coined by Mireille Fouquet and François Morain in 2001, but the mathematical community widely attributes the modern, computationally explicit codification of isogeny volcanoes to Andrew V. Sutherland's seminal 2013 paper, *Isogeny Volcanoes* [cite: 11, 12]. His work consolidated the theory into a framework that yielded substantial performance gains for computational number theory, such as the Schoof-Elkies-Atkin (SEA) point counting algorithm and the evaluation of modular polynomials [cite: 11, 12].

### 2.1 Formal Definition of an \(\ell\)-Volcano

Let \(\ell\) be a prime. An abstract **\(\ell\)-volcano** \(V\) is a connected, undirected graph whose vertices are partitioned into one or more distinct levels (or depths) \(V_0, V_1, \dots, V_d\) [cite: 1, 11]. The integer \(d\) is known as the depth of the volcano. The structure is strictly defined by the following topological constraints:

1.  **The Crater (Surface):** The subgraph induced by the vertices on the top level \(V_0\) is a regular graph of degree at most 2. This level is referred to as the "surface" or "crater" of the volcano [cite: 6, 11]. If the crater contains more than two vertices, it forms a simple cycle.
2.  **The Lava Flows (Levels):** For any level \(i > 0\), every vertex \(v \in V_i\) is adjacent to exactly *one* vertex in the level directly above it, \(V_{i-1}\). Every edge not residing entirely on the surface \(V_0\) is formed in this vertical manner [cite: 1, 11].
3.  **The Floor and Regularity:** For every level \(i < d\), every vertex \(v \in V_i\) has exactly \(\ell + 1\) edges incident to it [cite: 1, 11]. Because one edge points upward to \(V_{i-1}\) (except on the crater), there are \(\ell\) edges pointing downward to \(V_{i+1}\) (or \(\ell+1\) downward edges if \(v \in V_0\) has no horizontal edges).
4.  **The Floor:** The lowest level \(V_d\) is called the floor. Vertices on the floor have degree 1 (or at most 2 if \(d=0\)), consisting entirely of the single edge connecting back up to \(V_{d-1}\) [cite: 3, 5].

### 2.2 Algebraic Geometry of Volcanoes: Endomorphism Rings

The visual topology of the \(\ell\)-volcano elegantly mirrors the underlying algebraic structures of the elliptic curves' endomorphism rings. For an ordinary elliptic curve \(E/\mathbb{F}_q\), the endomorphism ring \(\text{End}(E)\) is an order \(\mathcal{O}\) in an imaginary quadratic field \(K = \mathbb{Q}(\sqrt{-D})\) [cite: 5, 6]. The endomorphism ring must contain the order generated by the Frobenius endomorphism, \(\mathbb{Z}[\pi_E]\), and it must be contained within the maximal order \(\mathcal{O}_K\) of \(K\) [cite: 11]. Thus, \(\mathbb{Z}[\pi_E] \subseteq \mathcal{O} \subseteq \mathcal{O}_K\).

Sutherland demonstrated that the levels of the volcano correspond precisely to the conductors of these endomorphism rings [cite: 6, 11]. Specifically, if \(V\) is an ordinary connected component of the \(\ell\)-isogeny graph \(G_\ell(\mathbb{F}_q)\) that does not contain the exceptional \(j\)-invariants \(0\) or \(1728\):
*   All vertices in a specific level \(V_i\) correspond to elliptic curves with the exact same endomorphism ring \(\mathcal{O}_i\) [cite: 6, 11].
*   As one descends the volcano from \(V_i\) to \(V_{i+1}\), the endomorphism ring shrinks. Specifically, \(\mathcal{O}_{i+1}\) is a subring of \(\mathcal{O}_i\), and the index \([\mathcal{O}_i : \mathcal{O}_{i+1}] = \ell\) [cite: 6, 11].
*   The vertices on the crater \(V_0\) have endomorphism rings that are locally maximal at \(\ell\), meaning \(\ell\) does not divide the index \([\mathcal{O}_K : \mathcal{O}_0]\) [cite: 6, 11]. 
*   The vertices on the floor \(V_d\) correspond to curves whose endomorphism ring is exactly \(\mathbb{Z}[\pi_E]\) locally at \(\ell\), meaning their conductor cannot be divided further by \(\ell\) [cite: 3, 13].

### 2.3 The Complex Multiplication (CM) Action and Isogeny Directions

Because the endomorphism ring \(\mathcal{O}_i\) is identical across a level, the edges of the volcano can be categorized by how they affect the endomorphism ring:
*   **Horizontal Isogenies:** These are edges connecting two vertices within the same level \(V_i\). By definition, these can only exist on the crater \(V_0\) [cite: 6, 11]. The horizontal \(\ell\)-isogenies arise from the action of invertible \(\mathcal{O}_0\)-ideals of norm \(\ell\). The number of such isogenies (0, 1, or 2) depends on whether the prime \(\ell\) is inert, ramified, or split in the imaginary quadratic field \(K\) [cite: 6, 11]. If \(\ell\) splits, the ideal classes form an orbit, leading to the cyclic nature of the crater [cite: 6, 11].
*   **Descending Isogenies:** These edges go from \(V_i\) to \(V_{i+1}\). The target curve has a strictly smaller endomorphism ring (\(\mathcal{O}_{i+1} \subset \mathcal{O}_i\)) [cite: 6, 13]. 
*   **Ascending Isogenies:** These edges go from \(V_{i+1}\) to \(V_i\). The target curve has a strictly larger endomorphism ring. From any vertex not on the crater, there is exactly one ascending \(\ell\)-isogeny [cite: 6, 13].

Sutherland's extensive work mapped these structures to compute modular polynomials \(\Phi_\ell(X, Y)\) rapidly. By utilizing a Chinese Remainder Theorem (CRT) approach, one can compute \(\Phi_\ell \pmod p\) by navigating \(\ell\)-volcanoes intersecting \(\text{Ell}_{\mathcal{O}}(\mathbb{F}_p)\) to find neighbors, vastly outperforming earlier classical algorithms and making the computation quasi-linear in the size of the polynomial [cite: 11].

## 3. The Evolution of Volcano Theory: The Inverse Volcano Problem

Between Sutherland's 2013 formalization and the recent 2024-2026 breakthroughs, an essential intermediate step was solidifying the existential bounds of these graphs. While it was known that ordinary isogeny graphs took the shape of volcanoes, mathematicians wondered about the reverse: *Given any abstract graph obeying the combinatorial rules of an \(\ell\)-volcano, does there exist a finite field \(\mathbb{F}_p\) and a prime \(\ell\) such that this abstract graph is a connected component of the actual \(\ell\)-isogeny graph over \(\mathbb{F}_p\)?*

This is known as the **Inverse Volcano Problem** [cite: 14, 15]. 

In 2022-2024, Henry Bambury, Francesco Campagna, and Fabien Pazuki provided an affirmative answer to this problem [cite: 15, 16, 17]. They proved that for an abstract \(\ell\)-volcano \(V\) of depth \(d > 0\), there exist infinitely many primes \(p \in \mathbb{Z}\) such that \(V\) perfectly models a connected component of the \(\ell\)-isogeny graph over \(\mathbb{F}_p\) [cite: 17]. For flat volcanoes (depth \(d=0\), where the volcano is just a crater), the structure does not depend on the choice of \(\ell\); hence there are infinitely many pairs of primes \((p, \ell)\) such that the abstract crater realizes as a component in the graph [cite: 10, 17]. Solving the inverse problem required navigating complex Diophantine equations (Nagell, Mahler, Pell) and analyzing the splitting behavior of primes in families of imaginary quadratic fields [cite: 17]. This theoretical underpinning proved that the structural bounds defined by Sutherland were tight and universally applicable across the universe of finite fields.

## 4. 2024–2026 Extensions I: Ordinary Isogeny Graphs with Level Structure

The classical isogeny graphs considered vertices as merely \(\mathbb{F}_q\)-isomorphism classes of elliptic curves. However, the maturation of isogeny-based cryptography demanded more sophisticated graph representations. Between 2024 and 2025, Derek Perrin and José Felipe Voloch published rigorous studies examining \(\ell\)-isogeny graphs of ordinary elliptic curves enhanced with an added **level structure** [cite: 4, 18, 19]. 

### 4.1 Incorporating $\Gamma_0(N)$, $\Gamma_1(N)$, and $\Gamma(N)$ Structures

Given an integer \(N\) coprime to both \(p\) and \(\ell\), Perrin and Voloch investigated the topological changes to isogeny volcanoes when vertices are redefined as tuples \((E, \gamma)\), where \(E\) is an elliptic curve and \(\gamma\) is a specified level \(N\) structure on \(E\) [cite: 4, 18]. In this enhanced graph, an edge exists between \((E, \gamma)\) and \((E', \gamma')\) if and only if there is an isogeny \(\phi: E \to E'\) satisfying the added condition that \(\phi(\gamma) = \gamma'\) [cite: 4, 18].

Three distinct types of level structures were rigorously analyzed:
1.  **\(\Gamma_0(N)\)-level structure:** The addition of a cyclic subgroup of order \(N\).
2.  **\(\Gamma_1(N)\)-level structure:** The addition of a specific point of order \(N\).
3.  **\(\Gamma(N)\)-level structure:** The addition of a full basis for the \(N\)-torsion subgroup \(E[N]\) [cite: 4, 14, 18].

By appending these structures to the equivalence relations defining the vertices, the graph expands significantly. Up to an equivalence relation, a vertex in the enhanced graph \(G_\ell\) is defined from the base volcano set \(V\) as \(V' = \{(E_i, \gamma_i) \mid \forall E_i \in V \text{ and } \gamma_i \text{ is a level structure}\} / \sim\) [cite: 4].

### 4.2 Crater Structure and Generalized Ideal Class Groups

Perrin and Voloch's fundamental result demonstrated how the craters of these enhanced volcanoes mutate based on the choice of parameters. Rather than the classical action of the ideal class group \(\text{Cl}(K)\) on the crater, the addition of a level structure subjects the crater to the action of **generalized ideal class groups** (also known as ray class groups) of the order \(\mathcal{O}\) [cite: 4, 18]. 

If \(G_\ell\) is a connected component, its new crater \(C_\ell(N)\) expands because the level structure breaks the standard \(\mathbb{F}_q\)-isomorphism symmetries. The authors utilized class field theory to calculate the precise size and shape of these new craters. For instance, the size of a crater \(C_{\ell,0}(N)\) (corresponding to a \(\Gamma_0(N)\) structure) depends strictly on the order of the subgroup \(\langle \mathfrak{l} \rangle\) viewed as a subgroup of a generalized class group [cite: 18, 20]. 

The stabilizer of these level structures plays a critical role. Perrin and Voloch proved that the stabilizer of a level structure corresponds to specific congruence conditions modulo \(N\mathcal{O}\) [cite: 20]. For example, the stabilizer of a point \(P\) (a \(\Gamma_1(N)\) structure) is \(\text{Stab}(P) = \{\alpha \in (\mathcal{O}/N\mathcal{O})^\times \mid \alpha \equiv \pm 1 \pmod{\mathfrak{a}^{-1}N\mathcal{O}}\}\) [cite: 20]. Depending on the prime \(\ell\) and the conductor of \(\mathcal{O}\), a base volcano with \(n\) vertices expands into multiple disconnected components or a vastly enlarged single component containing \(3n\) or \(6n\) vertices, depending on the stabilizer intersection [cite: 20].

This extension explicitly serves modern cryptosystems (such as CSIDH with level structure) [cite: 4], where tracking torsion point mappings through isogeny walks represents the core cryptographic operation.

## 5. 2024–2026 Extensions II: Algorithmic Advances in Navigating Tall Volcanoes

A central problem in elliptic curve cryptography is the Computational Isogeny Problem: *Given two elliptic curves \(E_0, E_1\) defined over \(\mathbb{F}_q\) with the exact same number of rational points, find an isogeny \(\phi: E_0 \to E_1\).* According to Tate's isogeny theorem, curves with the same number of points over \(\mathbb{F}_q\) are necessarily isogenous [cite: 1, 21].

### 5.1 The Conductor Gap and Galbraith's 1999 Bound

Historically, determining an isogeny was primarily bottlenecked by the "conductor gap." If the endomorphism rings of the two curves reside at vastly different levels of the isogeny volcano (i.e., one is at the crater and one is deep on the floor), finding the isogeny requires traversing the vertical distance [cite: 13]. Steven Galbraith, in 1999, published an algorithm that could navigate this vertical distance with a worst-case complexity of \(\tilde{O}(q^{1.5})\) field operations [cite: 13, 21]. This worst case occurred when the conductor was divisible by a massive prime \(N \approx \sqrt{q}\), creating what is termed a "tall volcano" [cite: 13].

### 5.2 The 2024-2025 Breakthrough: $\tilde{O}(q^{1/4})$ Complexity

In an exceptional series of papers spanning 2024 to 2025, Steven D. Galbraith, Valerie Gilchrist, and Damien Robert systematically dismantled the 1999 bound [cite: 13, 21, 22, 23]. They focused specifically on "tall volcanoes"—graphs where the crater is very small (constant or polynomial size) and the depth is vast. Such isogeny classes represent a real-world scenario critical to pairing-based cryptography, utilizing pairing-friendly ordinary elliptic curves [cite: 13].

The team introduced a method to compute a representation of an isogeny of large degree \(N\) using a meet-in-the-middle algorithm [cite: 13]. They achieved a drastic improvement: algorithms operating rigorously in **\(\tilde{O}(q^{1/4})\) field operations** [cite: 13, 21]. Equivalently, they can compute the representation in \(\tilde{O}(N^{1/2})\), where \(N\) is the degree of the isogeny [cite: 13]. 

The primary mathematical tools enabling this leap were:
1.  **Kani's Lemma:** The researchers applied Kani's construction, which allows for an efficient representation of an isogeny of large prime degree [cite: 13, 21]. By using dimension 8 isogenies on abelian varieties \(E^4\) (building off Castryck-Decru-Maino-Martindale techniques), they evaluated unknown vertical isogenies via matrix products [cite: 24]. 
2.  **Sesquilinear Pairings:** Originally, Galbraith's 2024 work required a heuristic assumption regarding the distribution of Elkies primes to navigate the gap [cite: 13]. However, in subsequent 2024 and 2025 papers, the team implemented newly discovered sesquilinear pairings (building on work by Katherine Stange and others) [cite: 21]. These self-pairings eliminated the need to restrict to Frobenius eigenspaces and Elkies primes entirely [cite: 13, 21]. Consequently, they established a rigorous, heuristic-free algorithm to calculate ascending isogenies [cite: 21, 25].

If one curve in an isogeny class exhibits a vulnerability allowing its Elliptic Curve Discrete Logarithm Problem (ECDLP) to be solved in \(\tilde{O}(q^{1/4})\), this new algorithm proves that the ECDLP on *any other curve* in the same isogeny class can be solved equally fast, firmly closing the equivalence gap for ordinary curves [cite: 13].

## 6. 2024–2026 Extensions III: The Spine of Supersingular $\ell$-Isogeny Graphs

While ordinary curves map to volcanoes, supersingular elliptic curves exhibit vastly different behavior. Over a finite field \(\mathbb{F}_p\), the supersingular \(\ell\)-isogeny graph \(G_\ell(\mathbb{F}_{p^2})\) is highly interconnected [cite: 26]. By the Deuring correspondence, supersingular \(j\)-invariants associate with maximal orders in a quaternion algebra ramified at \(p\) and \(\infty\) [cite: 2, 7]. The resulting graphs are famously \(( \ell + 1 )\)-regular Ramanujan graphs (when \(p \equiv 1 \pmod{12}\)), meaning they are optimal expander graphs [cite: 8, 27]. This rapid expansion implies that short random walks quickly achieve uniform mixing, forming the security bedrock for cryptographic schemes like SQISign and Charles-Goren-Lauter hash functions [cite: 22, 26].

However, the assumption that these graphs behave entirely "randomly" without exploitable substructures was heavily scrutinized in 2025.

### 6.1 Uncovering The Spine

In a highly impactful 2025 paper titled *The Spine of a Supersingular \(\ell\)-Isogeny graph*, mathematicians Taha Hedayat, Sarah Arpin, and Renate Scheidler investigated the internal substructures of these graphs, focusing specifically on the **"spine"** [cite: 8, 9, 28, 29, 30]. 

Every supersingular elliptic curve over \(\overline{\mathbb{F}}_p\) has a representative defined over \(\mathbb{F}_{p^2}\), meaning its \(j\)-invariant lives in \(\mathbb{F}_{p^2}\) [cite: 8, 9]. The "spine" is defined as the subgraph induced strictly by the \(\mathbb{F}_p\)-vertices (the subset of curves whose \(j\)-invariants reside entirely in the base field \(\mathbb{F}_p\)) [cite: 28, 29].

### 6.2 Structural Deviations and Cryptographic Implications

Hedayat, Arpin, and Scheidler uncovered exact behavioral patterns governed by congruence conditions on the prime \(p\):
*   When mapping the structure of \(G_\ell(\mathbb{F}_p)\) onto \(G_\ell(\mathbb{F}_{p^2})\), the spine exhibits operations classified as "Stacking," "Folding," or "Attachment" [cite: 30]. Stacking is the default geometric interaction, but Folding occurs in specific scenarios (e.g., the components of \(G_2(\mathbb{F}_p)\) containing \(j=1728\) fold when \(\ell > 2\)) [cite: 30].
*   If \(p \equiv 1 \pmod 4\), there are \(h(-p)\) \(\mathbb{F}_p\)-isomorphism classes of supersingular elliptic curves, all sitting on a single geometric level [cite: 26].
*   If \(p \equiv 7 \pmod 8\) and \(\ell=2\), there are \(h(-p)\) vertices on a "surface" and \(h(-p)\) vertices on a "floor", connected 1-to-1 via 2-isogenies [cite: 26].
*   If \(p \equiv 3 \pmod 8\), there are \(h(-p)\) vertices on the surface and \(3h(-p)\) vertices on the floor, fundamentally altering the routing of 2-isogenies. For every isogeny on the surface, there are three descending 2-isogenies to the floor, and zero horizontal isogenies [cite: 26].

Crucially, the authors analyzed the "center" of the full \(\ell\)-isogeny graph. By plotting the number of vertices in the center of the graph, they discovered a distinctive **wave-shaped pattern** [cite: 28, 29]. While these plots ultimately support the theoretical assertion that centers of supersingular \(\ell\)-isogeny graphs mimic the behavior of random \(\ell+1\)-regular graphs [cite: 28, 29], understanding these strict congruence-based topological biases (like the lack of horizontal isogenies when \(p \equiv 3 \pmod 8\)) is paramount. Identifying "hidden structures" or subgraphs with anomalous mixing times acts as a potential attack vector for adversaries attempting to bypass the hardness of the Supersingular \(\ell\)-Isogeny Path Finding Problem [cite: 9, 30].

## 7. 2024–2026 Extensions IV: Higher Dimensions, Pairings, and Global Distributions

The scope of isogeny graphs expanded beyond classical 1-dimensional representations over this period, merging into higher dimensions and global distributions.

### 7.1 Higher Dimensional Isogeny Representations
In 2024, Damien Robert published extensive surveys and new algorithms regarding the "higher dimensional" (HD) representation of isogenies [cite: 21, 24]. Robert noted that finding isogenies between a random ordinary curve \(E\) and another curve \(E'\) requires building known endomorphisms [cite: 24]. To combat the lack of known endomorphisms on a random curve \(E\) (apart from integer multiplication), mathematicians employed Zarhin's trick [cite: 24]. 

By projecting the curves into dimensions 2, 4, or 8 (e.g., \(E^4\)), one can build endomorphisms respecting the principal polarization via integer matrices [cite: 24]. This allows the Castryck-Decru-Maino-Martindale attack framework (originally utilized to break the SIDH protocol) to be generalized [cite: 24]. The HD representation confirms that if an isogeny \(\phi\) can be evaluated on a sufficient number of "nice" points in higher dimensions, it can be efficiently evaluated everywhere, heavily expediting the climbing algorithms for volcanoes [cite: 24].

### 7.2 Global Distributions of Endomorphism Rings
In 2026, research shifted toward a global framework for studying endomorphism rings inside ordinary isogeny classes. Traditionally, the local viewpoint studied how the endomorphism ring remained constant along each level of an \(\ell\)-isogeny volcano [cite: 31]. However, an emerging 2026 paper introduced *weighted exact and cumulative distributions* of endomorphism rings [cite: 31]. 

By analyzing the global variations of the prime via ring class fields and Chebotarev densities, mathematicians derived canonical laws for the \(\ell\)-adic valuation of conductors [cite: 31]. This new framework recovers the vertical stratification of \(\ell\)-volcanoes not just locally, but "in an averaged sense" across all components globally [cite: 31]. The condition of an elliptic curve having CM by an order \(\mathcal{O}_D\) over \(\mathbb{F}_p\) is now definitively tied to the splitting conditions in the associated ring class field \(L_D\) via the Artin reciprocity map [cite: 31].

### 7.3 Higher Rank Drinfeld Modules
The topological theories defining volcanoes are not strictly limited to elliptic curves. In recent years, extending these structures to genus-2 curves, Jacobians, and Drinfeld modules has seen intense activity. Perlas Caranay (2018) and Chien-Hua Chen (2025) successfully translated volcano theory to compute the "Isogeny Volcanoes of Rank Two Drinfeld Modules," expanding the framework of self-isogenous modular polynomials to characteristic \(p\) function fields [cite: 32]. 

## 8. Cryptographic Implications and Post-Quantum Protocols (2024-2026)

The fundamental motive behind the rapid expansion of isogeny graph theory is the impending transition to post-quantum cryptography. The hardness of the Computational Isogeny Problem (both ordinary and supersingular) offers robust resistance to Shor's algorithm, which easily breaks traditional RSA and ECC [cite: 4, 13].

### 8.1 Path-Finding and Endomorphism Ring Computation
A core cryptographic problem is finding a path in the isogeny graph. In 2026, Kirsten Eisenträger and Gabrielle Scullard formalized a deterministic algorithm to compute the full endomorphism ring of a supersingular elliptic curve from a subring [cite: 7]. Building on Kohel's 1996 thesis (which ran in \(O(p^{1+\epsilon})\)) and subsequent subexponential algorithms, Eisenträger and Scullard's 2026 algorithm runs in time polynomial in \(\log p\), the logarithms of the degrees of the generators, and the largest prime in the factorization of the discriminant [cite: 7]. The algorithm achieves this by computing non-commuting endomorphisms and executing path-finding directly on the Bruhat-Tits tree [cite: 7]. This is highly relevant to breaking or securing protocols like SQISign, where knowledge of the endomorphism ring implies knowledge of an isogeny path to a base curve [cite: 7, 33].

### 8.2 Enhancing and Analyzing Current Schemes
The advances in isogeny volcanoes directly impact modern schemes:
*   **CSIDH and SCALLOP:** The works on navigating tall ordinary volcanoes via sesquilinear pairings (Galbraith, Gilchrist, Robert) were used to analyze the security of the PEARL-SCALLOP group action. Their $\tilde{O}(q^{1/4})$ attacks forced adjustments in very particular parameter choices, although the core SCALLOP parameters remain unaffected [cite: 22].
*   **SQISign:** Advancements by Nakagawa and Onuki (2024) optimized SQISign implementations by analyzing 3-isogeny walks [cite: 34]. Moving from 2-isogenies to 3-isogenies replaces the computational requirement of calculating square roots in \(\mathbb{F}_{p^2}\) with cube roots, leading to highly efficient C-code implementations for length-\(m\) 3-isogeny chains [cite: 34].
*   **Level Structures:** The addition of \(\Gamma_0(N)\) level structures to supersingular and ordinary graphs by Perrin, Voloch, and Arpin [cite: 18, 19, 27] acts as the theoretical bedrock for "CSIDH with level structure," where adversaries must track not just the curves, but the torsion subgroups traversing the isogenies [cite: 4, 27].

## 9. Future Directions and Open Problems

Despite the exponential growth in theoretical frameworks and algorithmic optimizations from 2024 to 2026, several open problems persist in the study of isogeny graphs:

1.  **Inverse Volcano Problem Exceptions:** While the inverse volcano problem has been solved for \(\mathbb{F}_p\), Bambury et al. noted exceptions when scaling to \(\mathbb{F}_{p^2}\). There exist abstract 2-volcanoes that cannot be realized as connected components of ordinary isogeny graphs over \(\mathbb{F}_{p^2}\) for any prime \(p \neq 2\) [cite: 17]. Classifying the full set of these exceptions and determining if they are finite or structurally identifiable remains an open challenge.
2.  **Higher Genus Volcanoes:** As cryptographic interest slowly bridges toward genus 2 and 3 curves (principally polarized abelian varieties and Jacobians), formalizing the exact topological equivalent of the \(\ell\)-volcano for higher genus hyperelliptic gluing isogenies is an area of intense active research [cite: 2, 35, 36]. The Jacobian of a genus \(g\) curve is an abelian variety of dimension \(g\), and while isogenies map similarly, the resulting graphs are vastly more complex and structurally daunting.
3.  **Exploiting the Spine:** The discovery of wave-patterns and non-random topological traits within the spine of supersingular graphs (Arpin, Scheidler, Hedayat) opens the door to potential new heuristics for the Supersingular Isogeny Path Finding Problem [cite: 9]. If adversaries can mathematically detect whether a given curve resides close to the spine or the "floor" of a structurally biased subgraph, it could prune the quantum search space for isogeny paths.

## 10. Conclusion

Andrew Sutherland’s 2013 formalization of the isogeny volcano provided the computational and geometric foundation required to understand the ordinary isogeny landscape. The years 2024 through 2026 saw an unprecedented evolution of this framework. Through the incorporation of \(\Gamma_0(N)\), \(\Gamma_1(N)\), and \(\Gamma(N)\) level structures, researchers mapped how the craters of volcanoes physically morph and expand under generalized class group actions. Algorithmic traversals of these graphs achieved a quantum leap; algorithms to climb tall pairing-friendly volcanoes shed outdated heuristics and dropped worst-case runtime complexity to \(\tilde{O}(q^{1/4})\) through the ingenious use of Kani's lemma and sesquilinear self-pairings in higher dimensions. 

Simultaneously, the investigation into supersingular expander graphs mapped the elusive "spine" over base fields, revealing underlying congruential biases that cryptographers must now account for to ensure long-term security. From solving the inverse volcano problem to generating deterministic polynomial-time algorithms for computing endomorphism rings via Bruhat-Tits trees, the study of isogeny graphs stands at the apex of modern arithmetic geometry and post-quantum cryptography.

**Sources:**
1. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaWBUit_CX6U0eEh3gwHJ2XjrYC685fUzHUY5w1vz4F6mTjFi-Qs0DwJwyzu48giCF_aB3U6biAoAXtzJ7nRQg386DCLtgsm9OsOHGa__NZSUpZbZl6Td0aEvmHQsdj5sn-so2RMM=)
2. [loria.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGm7XOvWiTrqxd_DRxvjzqj9NpLEBNXZKhM0mRNSMj5del1UJhwBERgLBPLKeRUooOf-g2kODeI3zIhIClaYlPSsDiWXUp4nHg-akEG870e7aS2iarl-oKzqzjFc5aLmwXSputnvCryODQALp0utj4=)
3. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_re07HnR10Sl-3vNV2yxcom0Vs8SeUL0J9X-e6b6p11zW5dHQ82bWSl6nuhXBLwv9FMxgioQVMO6qWQh-4tlnM-jpnSNshLJ2ai2kAVwgxpF3K34nn9gN0FcUqIMYccM93dBLqjO7QEKTLM6WgjWw8Q==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFS54MFJve_LUZYmdLgR1SyIJC78LRBtm7KZ7Zp8Wt7w-wTOKF0Sfy7uKGfzMA7PRIXQsCk0zrDQ7ybBRkVa_L4Z47rgY5ecsC2kvdyOl4aiGrU68-aWw==)
5. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5aMBT-aipgNCs7dIADsq2xF8lGCyMW493u6Ft728QkGgSPOBpUHVfzzpgA29airujf6wX2BSVIdurwCqS7NeVZj7m4L57VjXOfkUWRZ9wwIiXYQCvy98dhw9Fy9md3Yro1Ob1ddvLa3WIUAMedSHXTz97UIBo53oZlAiMtYTdoa6dL1_SP5aeWF4=)
6. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_ACISdrSQYfocisFJy259aORnNrXbx7UT04B2rLH8b7KZb_VCoBAw2qegCqCinfX7wAmREpnsYwEesDdupVJvuEVusWvXsD_sP-97nPl7tqmwTvfoOMTva9-18zUuq6X38I52OnCZ-7aXnwy1AR4w9bpO1VGrX7zRL7pd1mKG1tKGJUd52MKRWw_x4Aw=)
7. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxAEMwLgPXMjO0FMXsChxe1rtpofZi5OfwdtJWU5J0jzy6u7qsQJiwBQ3FcnbvOdqHa_DILE-spC-NC2dYkv1MvnprtRjyrrssupmRrfQxQytCUBfX5VZaaSzTu4ZDPr6_LFGjTApKgN-MqdduEsHCBArtEAtb)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQtttILmMEHM0x0njCFSYxOxFpsRMAP2-pJv8709L1_YpmwzsEqCWMlMLHRJmGOy5pxvLlmtX9YHV6EIiJFPKGgAdVrPhXQGwjHE7b7NKnzRNT6XQevg==)
9. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG27U6e8vg0YPoXfkcF-wSlzas_A4PTKH77j6hrWxiQ4NXu_txokxoIeHtj-NoQDHg3l3LVpjZ-PHt4JuizYOaqv0L7biqta4hqjjnLbWK6J421L9fZTZKG6ZD5bT1MqdHI)
10. [unimelb.edu.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDFd4ojEQVYQjRU0beXEWwQ83suvdlM4s5gOSSibygpgwe-fhLT9Elh6U-OUOujqY6hyXgEhe7yU1P9f04zCYlwGAuxDILEXLMqfiX-5bQMOmHvhm0azCjTNA_nrUpFzyvKUawSEiZJugzYvQiZr0npdTeKjn3e8Z_yNUxH-ZRwOuO2a_Xl9SA4vC4YaNTVkexQGvO5KFwPaeXVV1yeTNgGdaeAX5MYHtncmZ20qzcXeJs2GYV)
11. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLjvDN_2TODlC4Iu1vuuQMpoXVSu4xak-51ihNjpvV-tahiuoTqTkIJxym5QhpksasNYHOWcNUYexBmvAEKdKHpDuoxlA3IOJWERS27izWFEu_6a1aHYmja7mR0Q==)
12. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSt5dJOIWmsgt79sfQICNX_x63NK44_Qu7LXZfP35V60oHnjRFnDSN93hjdoMSNmelSnQlxSQB4bB5PhnVnllJVxut0pusu9aUCErafLupBJsgkd_-sSfvrOPdlw==)
13. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHt9fn-eW5LNKgVJwnIx6lquETs6uWskcaByqAuyIiQ7-DQ_xa3m5bgMMwv27FWHjDi0wqsZqQG5KWks9Y-wQ-KOBJlnVBAm6cUCLUUabLhXKhE1TlE_TejSpHeyzioEEg=)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrl7JMakNscouXuYUPcPOiAdFqiTM7YSdxZETXeT94RCA9hzvBc0_dxQDNW9jyZ6aK34aoUBlMUj7hy29ad4LM-XQCaNd0J4K7L-0wIy2oC4KFL19kH7e5R9hIIuPgcd_7ZOOwGndzkQobhm97Pr3wVRKpq0rruyRZGn0zv9Lnp7eYX-CrOW9kIyOEUjfaQ_ArUfr5xLbD75vV5NcTj1bUQkW1fxJhnJV4aIA=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0gV0HVP9iXytHYQC471oNuxF0s9IwsC4WtCJRWpCeNo2Qexy3rqOKzo6w5oB8g8oCjCoYJENWB5E4SMT8ENhxhicHztTVGtmdFbQqM2n_Oi_Gw9nwsQ==)
16. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSuSJycqbLZ02JyItWKWa57uBGRd7PLz8gwUlJWypgW7SdcgxXk9wuJwVi9HTFO_GNiWIeXCj76re9aXqH7rO4gPEL9tpCDfc6vGLByXFQ1e3WoYyG6wqVOiFUKZD_4C2He19Ds0s0IOxk-TpllseVN7tyBDzoarpfaKno-fQHZgLGdGyMleUEnvt05WTrSdRP-m4YVp7Knyna5jcFPXIwTBstmGtNC6A9YzuQ65eJ5Oy8OOkb1mm4xPDkLXwzE9B4XGgNkEr2wdttYQJn2ey1dKDl)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG95QGd7WlMKh24gAzMQ19A5IORxWppS_AY1kqQQKGwrKX11HUkAsVpdw0OkATuNH8iCNrzIojw444ixn_J5svpDL2_81rghY89gvnWXOVP1rQTWpi6Jw==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwAC3Chy5jIxx81w6X7iVOoyyIFYTf-1WbvePE16Pc6HI0g611tvhJN9IFuosjjt24ibFGjgZUhW97HKVpHI2nyH8CnBmaKlyb9l363p_x0FEfJpkBRI8QDQ==)
19. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcqt9mxpZAyt10FKIJrMVVQUfXYhiwXaN6FwilFxHxMA5ZY7xCfECOnfng7qMW_kw9iNTD0ixKbvaM5XnKlcgp_jUE3qjvkOLeoySfCCWws15oDW1HqmJdl0BQre9IoeynZtRegsN14R69Dbm7e2yD_SU=)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGY_yBpxuGopYoTVqwaDtzEiJZOPsKai031kGkSAytQUfEQVPkwwG4ECf4A9RZ-Yd1j7KTDPPIQH9Q75mM4CmADWeFHdBcC5ZqOFiJR65um9N0mT7r-vefj-qQBX9-FpEXsns_dbuKB_1dgQL3U0h9H4VHxvjEZP9EIXQG8W9fW344GXCoOos04_QCxwWnymSyiMZzyPA==)
21. [u-bordeaux.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERo1XmCGIb3MfRfGmDjKMe9zX7oRJCghSXkP5trxkYSigUHz9e0OC-NAZWfM0tPS0KO7d-R2dMvOpESyCFjuW52flNs8-vKk6nxTPRWAdc0g4YPmt_Bojxg88Q8TUT4dNEcwg1KoshGjzCoCDV-zfoqBu708cwyUQJoHzj1H9NwZtu5Ykl_CpmQAaY4xvJ41wTYgE=)
22. [mathstodon.xyz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUQHhfWa54IchEtJiweiPuvJkzEayZB0K5FjDrBplSjIDS3YsLIDrcXAfgUxUlxm_fHqs57tRouvTdC5fBkQrn_iQB-PCQrI1rkij0WJsTKZxR7o8PWjw=)
23. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-Te2ptlkM09FEa0XSawqUcONvHPrD4WxgZLba7Tq-vLKV6E-D04q2PhCcLqJrXLRyeJBXc5cOGyMU53gbWp7Dq2fZO6GesQbIOJIka4XucxHkyYPHRR35thN__OeffixT82HN4FU2y0sSsIFSpehXNnUZazcaStzgMTfjStF2U1nMqIXMs0Zp5M6s3qoJEm9gxvDqTd_FH6onlI5sXVxUGMqsfoTFaTCEWrdMofKRys2G9Sky7rD7gqYoUTOSMrlrtgNjXO6m)
24. [u-bordeaux.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGw-_EM6siiFFC2lDH038MWJuqkBMZ3vC557TMlFD-GlFs50U2K3S9FwLWn-v_Xb-xMzX7XdQyEVh_xJX3_rzYcYk61o9jggIpFdkE2ANbFe7sKfnsrXIoW9SxNzJA_Nzzd_WqwmZ_8YjzHNWywVsgm8Xa9JqZrcvbfjJOPAjJv_6eeC4A9Wj6epYQgJNw8PQ==)
25. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFh9jA5KdJTZOCW447MmXTQ96UfnTLymfeHVwCaeknj5bX6qWHpaZZUGd2qYe7rKykin9WbeMOyZPf011IES_i4W40cJmJ8blT1YyP8IpcoBaYXIBTtJMAJgKOEnwrv12apYwWqJVh8Btnd4TCVu8j1-rCTVqHjBQjEteq1QW2o3AuvRnPCFZbR9qWyrrsuSEPJDq00CIHIaMgPiQQlD560xaRzIYcSwRg1)
26. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHL13TbZL4Ge_Dg4BAJbP_QKJIjXlWbCiU0HiLywcHTCTEEqE28_O6NZdNTn5f9b7d-4PY1G2sPfYAaLCpn-TJh13T3jW4vsbfl4b5yUxDxUsIgCXtg5p0YzzlqtV7tSiWoyR0dGkT13AGAil6Mc_UKaBmWTCdsCVAqVzDyKznYjFy8MJj8nGQZWn8U)
27. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElqlSAcy0RbhXxoJzMisbzFj2r0OVBsSS18tTTU0ODNFHaYFBh9G3QQ3LnFXj0edFF1t_oMt85ZzeFJ8oMIf-J5QIwKCTPJdYc3cOGBkOn_53t17E0yfp0WStN2lnT5WtOFg0ENsCBJgonT30pmuVa8407LheQ7JYhoYzunvbTNia_Ijw6WfGnVOt_w0PoImVjvJK5_wKPSHvClJ4xwheEYDlaVsW9NMbqChWRSYtZfyCrkUCWaO63eBUUgQ==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuvO-IXY-7ZF91xZ9kpAR0uZ_M7uRETkHXoo4PiUYAVj9kzXuKvAQEBJ-aasvcFsoIhSKsGHdDdje45YZkl5MmTVeKdRYnNhe6citgaapsjjjtTTkWTA==)
29. [lucant.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZ6pQeW1aGJi4AhcQH-Epqic811q3J_xrEXWRfvgvysM4doyLfIrolS1uJIOP_A3nzKlY7LwZ-nugizSJN1BtGdwcLFiATKh71g3F5teYqmWLOa7hZicYhyyBAP2K8JpdrVBg85L5hD1c=)
30. [gaati.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHt78vDeWiqKqe5Nx8YCSkPGhY77kDJMjY5PbpI978giFZnqVcBavBhhD1J5wZ5Fq-ilAk4HxClj-TzFWIgJyhnESmvjWapEddDU65AicCyDr_t-jp0A42mrmgewwLcjUHPsw==)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpR6wDLzLwb0G_PUAyo5InePhfl42echZk0DCkNniDWK5IyfKwstUQ-50dYlXTpx048cU7GgoN8UH9xLtjNsPSm5vBa0Wy4akJvU8Dja7SfpV5KrKRfQ==)
32. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXf2046QZRLYsx7sKtDdT-IWji4cQ-h6zZP2vZlNq9q-Wq_zIz9-uxp94nQhAqOEsqt3LVE59YpQyViIFcAjMFIq2KkaikYKEHNXh2hFs4TY23bU_0VHyTqTuvEaUwdQEy1bNGxgq1tE87Yi_RPPQUqD--DSNL_GFbbwZeNP0xKAm6YqguC2kbGbsRrc23O8AhWE8bFx6Ffv-qEDZMl2OKc4E-R4sGO6E7uRg5xmI7BndgiGlwPRNNZ58uDw==)
33. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFubnX3FOBQftVX3FttkSQ22_ETkbIWItat7Xr_62Ott_FU4z4snLYtJiDYZmhPHCZXzFCZvstLQDfjR1fsFVbFT_XGotXuSPj72DSH5XSOSq8=)
34. [askcryp.to](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3mwt5uz-S8qCwI8LBHLKvpsBFMXR6KFz4yxb9XwekR0GZ4_AefhtpaQU2F-zZFO2i9KDu1hlvqyc8gWfLKoAY3Hoee7IoujNEg1vyz3wBLRMzLJqznHBNNZSuGEOyib4fUBfIC6lTvId-iNwDctWPN64sIIrL07M0fW_TuFTEJudIrzecE-XBy7N9Znn1ZSxoI3UJmbXYHYTW9s-I58krOMIiARk=)
35. [isogeni.es](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDqluJPUJgtP9P7G-zk8S02tF7maKgNpB3Ok-P38L_bMOgW6D4BcjOF6WqD5gJ1H9-si3m26cQUM65DlS2oMNqhuP0eGUqCIJR)
36. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDOpQ7JLRM92vBr2PDQMXFzaEcGrJSIphOhJZ4HQOCW-SsoL8j2PYMCds5LJJqlrDpMX-pbmiO7qSke8qVilQUVqjIiWUvLQ3NqgmQOC2d5hv-woyNieN3v5Z8McSCalF0wfMB06rhYGPryraEcZc5Lvqke2vasSyC8hOAXkRL5sq_Lb_kQFpUlhCBOzjaw7D-NgO4bzOOBULZPFtbF_Y41o6jmY7FH1rrNgO8E6ZgjB5dHFvOLBYgsKDXrDvzvGK4cOD2j3Y1Eg4vhkfGVQyTl1jWN4LNzenzd8sFAOvy_Pdqttc7AkJ6lvBpFA==)

