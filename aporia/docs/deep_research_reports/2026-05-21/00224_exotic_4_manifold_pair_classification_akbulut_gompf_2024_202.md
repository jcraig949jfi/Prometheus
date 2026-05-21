# Exotic 4-manifold pair classification (Akbulut, Gompf) 2024-2026 (Ren-Willis cross-link)

**Pythia queue id:** 224
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd2VkFQYW8yVUVibVo5TW9QenV5WjBRNBIXdlZBUGFvMlVFYm1aOU1vUHp1eVowUTQ
**Elapsed:** 377s
**Completed at:** 2026-05-21T18:43:03.356980+00:00

---

# Exotic 4-Manifold Pair Classification: The Akbulut-Gompf Legacy and the Ren-Willis Combinatorial Paradigm (2024-2026)

**Key Points:**
- Exotic 4-manifolds are spaces that are topologically identical (homeomorphic) but fundamentally distinct in their smooth calculus-based structures (non-diffeomorphic).
- The historical detection and classification of these structures were deeply rooted in physics-inspired gauge theory, relying heavily on Seiberg-Witten and Donaldson invariants.
- Recent mathematical breakthroughs between 2024 and 2026, most notably by Qiuyu Ren and Michael Willis, established the first "analysis-free" methods to detect exotic 4-manifolds utilizing a combinatorial tool known as the "skein lasagna module."
- These groundbreaking algebraic techniques successfully distinguished historical examples proposed by Selman Akbulut, such as the knot traces $X_{-1}(-5_2)$ and $X_{-1}(P(3,-3,-8))$, bypassing the need for partial differential equations entirely.
- Concurrently, researchers including Robert Gompf, R. Inanç Baykur, and Noriyuki Hamada have advanced the geographic classification of these manifolds, revealing new signature-zero exotic pairs, minimal symplectic spaces, and infinite-order smooth structures.

**Introduction for the General Reader:**
Understanding the universe's ultimate geometry often compels mathematicians to investigate four-dimensional spaces. Dimension four holds a unique and somewhat mysterious position in mathematics: it is the only dimension where two spaces can possess the exact same overarching continuous shape (they are "topologically" identical) yet possess incompatible smooth structures (they cannot be smoothly morphed into one another without encountering tears, creases, or singularities). These fascinating topological twins are known as exotic manifold pairs. Historically, proving that two spaces formed an exotic pair required incredibly complex tools borrowed directly from quantum physics and string theory, known as gauge theory. While incredibly powerful, these equations are notoriously difficult to solve and compute explicitly. 

Recently, however, the mathematical community has witnessed a massive paradigm shift. Between 2024 and 2026, researchers began leveraging more algebraic, rule-based methods—often involving the mathematical theory of knots and links—to tell these exotic spaces apart. This shift is highly exciting because it suggests that mathematicians might finally be able to understand the smooth fabric of four-dimensional space through purely combinatorial algorithms, opening up entirely new pathways in geometry. The work is ongoing, and while researchers are highly optimistic about these new tools, the full classification of these exotic spaces remains a deeply complex and actively debated frontier.

## 1. Introduction and Historical Context
The study of low-dimensional topology, specifically the topology of 4-manifolds, witnessed a monumental revolution in the 1980s. Michael Freedman achieved a sweeping classification of simply connected topological 4-manifolds, proving that their homeomorphism type is entirely determined by two pieces of algebraic data: their intersection form and the Kirby-Siebenmann invariant [cite: 1, 2]. Freedman’s breakthrough implied that if two simply connected, closed 4-manifolds have the same intersection form (and the same parity of the Kirby-Siebenmann invariant), they are homeomorphic [cite: 3, 4].

However, this topological rigidity sharply contrasted with the smooth category. Simon Donaldson’s pioneering work on the moduli spaces of anti-self-dual Yang-Mills equations revealed that the intersection form of a smooth, definite 4-manifold must be diagonalizable [cite: 1, 3]. This immediately implied the existence of topological 4-manifolds that admit no smooth structures whatsoever, such as the $E_8$ manifold [cite: 2, 5]. More profoundly, the synthesis of Freedman’s and Donaldson’s work led to the discovery of **exotic 4-manifolds**: pairs of manifolds that are homeomorphic but not diffeomorphic [cite: 1, 6]. Over the subsequent decades, the toolkit of gauge theory was refined, culminating in the Seiberg-Witten invariants, which became the standard apparatus for distinguishing smooth structures [cite: 4, 6].

## 2. The Dichotomy of Dimension Four
In dimensions $n \neq 4$, the relationship between topological and smooth manifolds is well-understood through the lens of surgery theory and the $s$-cobordism theorem [cite: 6, 7]. For dimensions $n \geq 5$, smooth structures on a given topological manifold are classified by algebraic topology (up to finite ambiguity), and in dimensions $n \leq 3$, topological and smooth categories are equivalent [cite: 8, 9]. Dimension four stands alone as an anomaly. The failure of the Whitney trick for embedding 2-dimensional disks in 4-manifolds destroys the classical proof of the $h$-cobordism theorem [cite: 5, 6]. 

The resulting topo-smooth dichotomy means that a single topological 4-manifold can harbor an infinite myriad of distinct smooth structures [cite: 10]. The quest to map the "geography" of these exotic structures has been a central driving force in the field. To navigate this geography, mathematicians have sought to construct manifolds with specific Betti numbers, signatures, and Euler characteristics, while simultaneously developing invariants capable of distinguishing them [cite: 4, 11].

### 2.1 Intersection Forms and Signatures
For a closed, oriented 4-manifold $M$, the intersection form is a symmetric bilinear pairing:
\[
Q_M: H_2(M; \mathbb{Z}) \times H_2(M; \mathbb{Z}) \to \mathbb{Z}
\]
defined by $Q_M(\alpha, \beta) = (\alpha \cup \beta)[M]$ [cite: 2, 5]. According to Poincaré duality, $Q_M$ is a unimodular matrix. The signature of the 4-manifold, denoted $\sigma(M)$, is defined as the signature of this intersection form—the number of positive eigenvalues minus the number of negative eigenvalues over the reals [cite: 2, 5]. Exotic 4-manifolds with signature zero have historically been notoriously resilient to gauge-theoretic detection, largely because standard Seiberg-Witten computations often vanish or degenerate in these topological regimes [cite: 12, 13].

## 3. Early Exotic Constructions: Akbulut and Gompf
The proliferation of exotic smooth structures relies heavily on cut-and-paste topological operations. Two of the most foundational figures in this arena are Selman Akbulut and Robert Gompf. Their constructions of corks, plugs, and specific knot traces provided the earliest explicit examples of exotic phenomena [cite: 14, 15].

### 3.1 Akbulut's Knot Traces
In 1991, Selman Akbulut discovered a compact, contractible 4-manifold (a "cork") and utilized it to construct an exotic pair of 4-manifolds with boundary [cite: 1, 8]. A highly illuminating setting for Akbulut's work is the theory of **knot traces**. Given a knot $K \subset S^3$, its $n$-trace, denoted $X_n(K)$, is the 4-manifold obtained by attaching an $n$-framed 2-handle to the 4-ball $B^4$ along $K$ [cite: 16]. 
Akbulut identified an exotic pair utilizing the $(-1)$-traces of two specific knots: the twist knot $-5_2$ and the pretzel knot $P(3,-3,-8)$ [cite: 1, 17]. The manifolds $X_{-1}(-5_2)$ and $X_{-1}(P(3,-3,-8))$ were shown to be homeomorphic using Freedman's theorem, but their boundary 3-manifolds and smooth interiors harbor deep geometric disparities [cite: 1]. Distinguishing these traces natively, however, required sophisticated topological arguments intertwined with gauge theory or Floer homology [cite: 1].

### 3.2 Gompf's Infinite Order Corks and Nuclei
Robert Gompf significantly expanded the taxonomy of exotic 4-manifolds. Gompf introduced the concept of the "nucleus" of elliptic surfaces, identifying the minimal submanifolds responsible for generating exotic smooth structures [cite: 16, 18]. Furthermore, Gompf pioneered the study of infinite-order corks. A cork is a pair $(C, f)$, where $C$ is a contractible 4-manifold and $f: \partial C \to \partial C$ is an involution on its boundary that does not extend to a diffeomorphism of the interior [cite: 14, 15]. Cutting $C$ out of a 4-manifold $X$ and regluing it via $f$ produces an exotic copy $X'$.
In 2017, Gompf proved the existence of infinite-order corks, where the diffeomorphism $f^k$ does not extend to the interior for any integer $k$, allowing for the generation of infinitely many pairwise non-diffeomorphic 4-manifolds through repeated cork twists [cite: 14, 15]. Gompf’s techniques, such as the swallow-follow operation, provided powerful mechanisms for embedding these corks into closed simply connected 4-manifolds [cite: 14, 19].

## 4. Gauge Theory vs. Combinatorial Topology
For decades, the only known methods to rigorously prove that two 4-manifolds formed an exotic pair relied on global analytical invariants: Donaldson’s polynomials, Seiberg-Witten invariants, or Heegaard Floer homology [cite: 1, 3]. These tools are defined via solutions to non-linear partial differential equations on the manifold, requiring a generic Riemannian metric and intricate perturbation schemes [cite: 3, 20].

While gauge theory is incredibly successful, it comes with severe computational drawbacks. It is often non-algorithmic, and extracting explicit values for manifolds built from complex handlebody diagrams can be insurmountably difficult [cite: 19, 21]. The topological community long sought a completely different approach: a combinatorial, algebraic invariant that could be computed directly from a Kirby diagram without invoking functional analysis [cite: 20, 22]. This search led mathematicians to the intersection of knot theory and 4-manifold topology, specifically to categorified link invariants like Khovanov homology [cite: 20, 22].

## 5. Khovanov Homology and Link Cobordisms
Introduced by Mikhail Khovanov around 2000, Khovanov homology is a categorification of the Jones polynomial [cite: 20]. For an oriented link $L \subset S^3$, Khovanov constructed a bigraded chain complex of abelian groups $C_{i,j}(D)$, where $D$ is a planar diagram of $L$ [cite: 20, 23]. The Euler characteristic of this complex recovers the Jones polynomial:
\[
\sum_{i} (-1)^i q^j \text{rank}(H^{i,j}_{Kh}(L)) = (q + q^{-1}) J_L(q^2)
\]
Khovanov homology assigns algebraic data to the resolutions of crossing points in $D$ [cite: 20, 23].

A profound feature of Khovanov homology is its **functoriality**. If $\Sigma \subset S^3 \times [cite: 12]$ is a smooth, properly embedded orientable surface (a link cobordism) connecting link $L_0$ to $L_1$, it induces a well-defined map on Khovanov homology:
\[
Kh(\Sigma): Kh(L_0) \to Kh(L_1)
\]
This property, rigorously established by Jacobsson, Bar-Natan, and later extended to $\mathfrak{gl}_N$ by Morrison, Walker, and Wedrich, implies that Khovanov homology "sees" the smooth 4-dimensional topology of the surfaces bounding knots [cite: 24, 25].

### 5.1 The Lee Deformation and Rasmussen $s$-Invariant
Eun Soo Lee introduced a deformation of the Khovanov complex that disrupted the quantum grading but produced a homology theory that is starkly simple: its rank depends only on the number of components of the link [cite: 26, 27]. Jacob Rasmussen utilized this Lee homology to define the $s$-invariant, $s(K) \in \mathbb{Z}$, which provides a rigorous lower bound on the slice genus $g_4(K)$ of a knot in the 4-ball:
\[
|s(K)| \leq 2g_4(K)
\]
Rasmussen used this purely combinatorial invariant to give a new proof of the Milnor conjecture concerning the slice genus of torus knots, entirely bypassing gauge theory [cite: 20]. This planted the seed for utilizing link homology to probe absolute 4-manifold topology [cite: 19, 20].

## 6. The Skein Lasagna Module: Formalism and Properties
To extend the functoriality of Khovanov homology from $S^3 \times [cite: 12]$ to arbitrary 4-manifolds, Scott Morrison, Kevin Walker, and Paul Wedrich introduced the **skein lasagna module** [cite: 21]. This module represents the degree-zero part of the topologically-inspired "blob complex" [cite: 21, 28].

### 6.1 Definition of Lasagna Fillings
Let $X$ be an oriented, compact smooth 4-manifold with a framed oriented link $L \subset \partial X$. A *lasagna filling* of $(X, L)$ consists of a finite collection of disjoint, standardly embedded 4-balls $B_i \subset \text{int}(X)$, alongside a properly embedded, framed, oriented surface $\Sigma \subset X \setminus \bigcup \text{int}(B_i)$ [cite: 20, 24]. The boundary of $\Sigma$ matches $L$ on $\partial X$ and forms auxiliary links $L_i \subset \partial B_i$. 

Each auxiliary link $L_i$ is "decorated" with an element $v_i$ chosen from the Khovanov-Rozansky homology of $L_i$ in $S^3$. The skein lasagna module, denoted $S(X, L)$ (or $S_0^{\mathfrak{gl}_2}(X; L)$), is defined as the $\mathbb{R}$-module generated by all possible lasagna fillings, modulo a set of local skein relations and ambient isotopies [cite: 21, 24].

### 6.2 Skein Relations and Evaluation
The relations governing the lasagna module stipulate that linear combinations of fillings are multilinear in the decorations $v_i$ [cite: 21]. If a segment of the surface $\Sigma$ lies inside a standard $S^3 \times [cite: 12]$ neighborhood, replacing that segment with a different cobordism $\Sigma'$ that induces the same map on Khovanov homology yields an equivalent element in $S(X, L)$ [cite: 21, 25]. The lasagna module assigns a vast, often infinite-dimensional vector space to a 4-manifold, acting as a universal target for Khovanov-style evaluations of surfaces [cite: 28, 29]. 

Computing $S(X, L)$ directly from its definition is generally intractable except for $B^4$ (where it recovers the standard Khovanov homology of $L$) and $S^4$ [cite: 21]. However, significant computational machinery was developed by Manolescu and Neithalath to compute these modules for 4-dimensional 2-handlebodies using cabled Khovanov homology [cite: 28, 29].

## 7. The Ren-Willis Breakthrough (2024-2026)
The theoretical promise of the skein lasagna module was fully realized in a series of groundbreaking papers published between 2024 and 2026 by Qiuyu Ren and Michael Willis [cite: 1, 17]. They provided the **first analysis-free proof of the existence of exotic compact orientable 4-manifolds**, dismantling the absolute monopoly that gauge theory held over 4-manifold classification [cite: 1, 30].

### 7.1 Distinguishing the Akbulut Traces
Ren and Willis turned their attention to the classic exotic pair discovered by Akbulut: the knot traces $X_1 = X_{-1}(-5_2)$ and $X_2 = X_{-1}(P(3,-3,-8))$ [cite: 1, 17]. The authors evaluated the Khovanov-Rozansky $\mathfrak{gl}_2$ skein lasagna modules for these manifolds [cite: 26, 31]. 

The critical insight lay in analyzing the knots themselves. The pretzel knot $P(3,-3,-8)$ is a slice knot. By the standard slice-ribbon folklore (and the trace embedding lemma), because the knot is slice, its trace $X_2$ admits specific topological simplifications, and its skein lasagna module evaluation reflects this triviality [cite: 1, 30]. Conversely, the twist knot $-5_2$ is a positive knot with a non-zero Rasmussen invariant, specifically $s(-5_2) = 2$ [cite: 1, 32].

Ren and Willis proved that the skein lasagna modules over the rationals, $S_0^{\mathfrak{gl}_2}(X_1)$ and $S_0^{\mathfrak{gl}_2}(X_2)$, are non-isomorphic [cite: 1]. Because the skein lasagna module is a diffeomorphism invariant, this completely algebraic computation proves that $X_1$ and $X_2$ are not diffeomorphic, firmly establishing them as an exotic pair without ever writing down a partial differential equation [cite: 31, 33].

### 7.2 Generalizing to Infinite Families
The methodology established by Ren and Willis did not stop at a single pair. Because the Khovanov skein lasagna module respects connected sums (specifically, the module of a connected sum is the tensor product of the constituent modules [cite: 26, 29]), the exotica remains intact under boundary connected sums with other manifolds possessing non-vanishing skein lasagna modules. Ren and Willis leveraged this to construct infinite families of exotic knot traces and 4-manifolds whose detection explicitly requires the Rasmussen $s$-invariant in the hypothesis, suggesting these families might not be directly recoverable by standard Floer-theoretic methods [cite: 1, 26].

## 8. Lasagna $s$-Invariants and Genus Functions
To formalize the topological obstruction presented by the Lee deformation of the lasagna module, Ren and Willis defined a "lasagna version" of Rasmussen’s $s$-invariant [cite: 31, 33]. 

### 8.1 Defining the Lasagna $s$-Invariant
The lasagna $s$-invariant of a 4-manifold $X$ at a homology class $\alpha \in H_2(X)$ is denoted $s(X; \alpha)$ and takes values in $\mathbb{Z} \cup \{-\infty\}$ [cite: 1, 30]. It is extracted from the filtered structure of the Lee skein lasagna module $S_0^{\text{Lee}}(X; L)$ by looking at the maximal filtration level supporting the generator associated with the homology class [cite: 26, 32]. 

### 8.2 Bounding the Genus Function
The power of $s(X; \alpha)$ lies in its relationship to the smooth genus function. The genus function $g(X, \alpha)$ of a 4-manifold is the minimum genus of any smoothly embedded surface representing the homology class $\alpha$ [cite: 1, 10]. Ren and Willis proved a foundational adjunction-type inequality:
\[
g(X; \alpha) \geq s(X; \alpha) + \frac{\alpha^2}{2}
\]
where $\alpha^2$ is the self-intersection number of the class [cite: 1]. This inequality provides a sharp, algorithmically derivable lower bound on the shake genus and slice obstructions of knots within arbitrary 4-manifolds [cite: 1]. The fact that $s(X_1; \alpha) \neq s(X_2; \alpha)$ for the Akbulut pair directly proves that their interiors are not diffeomorphic [cite: 1].

## 9. Variations: Cornered Skein Lasagna and 1-Dimensional Inputs
The Ren-Willis breakthrough triggered a cascade of developments in categorical 4-manifold topology throughout 2024 and 2025. 

### 9.1 Cornered Skein Lasagna Theory
Sarah Blackwell, Vyacheslav Krushkal, and Yangxiao Luo extended the skein lasagna module framework to 4-manifolds with corners [cite: 21]. Trisections of 4-manifolds, introduced by Gay and Kirby, decompose any closed 4-manifold into three 4-dimensional 1-handlebodies $\natural_k(S^1 \times B^3)$ meeting along a central surface [cite: 21, 34]. Blackwell, Krushkal, and Luo developed a bicategorical framework that computes the skein lasagna module $S(X)$ of a trisected closed 4-manifold by gluing the categories associated with these cornered 3- and 4-manifolds [cite: 21]. This structural decomposition is crucial because it localizes the computation of a global 4-manifold invariant into manageable 1-handlebody chunks [cite: 21, 34].

### 9.2 Skein Lasagna Modules with 1-Dimensional Inputs
Simultaneously, a collaboration between Qiuyu Ren, Ian Sullivan, Paul Wedrich, Michael Willis, and Melissa Zhang produced a variant of the Khovanov skein lasagna module tailored for 1-dimensional inputs [cite: 24, 35]. This theory takes as its base the Khovanov homology for links in connected sums of $S^1 \times S^2$, originally defined by Rozansky and Willis [cite: 20, 24]. 

The authors successfully proved the functoriality of the Rozansky-Willis homology for cobordisms in "4-dimensional relative 1-handlebody complements" [cite: 24, 35]. By bypassing complex structural obstructions through an isomorphism established by Sullivan and Zhang relating Rozansky-Willis homology to the classical lasagna module on $\partial(D^2 \times S^2)$, they established a highly robust computational invariant [cite: 21, 24]. 

A remarkable application of this 1-dimensional input theory was the analysis of **Gluck twists**. A Gluck twist involves excising a neighborhood of an embedded 2-sphere $S^2 \times D^2$ and regluing it via a non-trivial diffeomorphism [cite: 24, 35]. The team proved that Gluck twists induce canonical isomorphisms on Khovanov skein lasagna modules over the rationals [cite: 24, 35]. Consequently, Khovanov skein lasagna modules *cannot* detect exotic structures arising purely from Gluck twists, mapping a strict theoretical boundary on the sensitivity of these combinatorial invariants [cite: 24, 35].

## 10. Skein Lasagna-Free Proofs of Exotic Manifolds
Following the Ren-Willis paradigm, mathematicians quickly sought to distil the logic into even simpler, "lasagna-free" arguments. Research by Hayden, Sundberg, and others showed that Khovanov homology could distinguish exotic surfaces embedded directly in the 4-ball [cite: 22, 36]. 

By pushing these techniques, authors provided lasagna-free proofs distinguishing exotic compact, orientable 4-manifolds [cite: 36, 37]. The core of these proofs leverages the fact that the Khovanov map for link cobordisms $\Sigma \subset [cite: 12] \times \mathbb{R}^3$ depends strictly (up to an overall sign) on the isotopy class of the surface relative to its boundary [cite: 36, 37]. By tracking specific classes, such as Plamenevskaya's invariant, through the cobordism maps of exotic disks, researchers demonstrated the existence of exotic Mazur manifolds—compact, contractible 4-manifolds consisting of a single 1-handle and 2-handle [cite: 22, 25]. These parallel developments confirmed that the combinatorial detection of 4-manifolds is a deep, intrinsic property of categorified link invariants, not merely an artifact of the lasagna construction [cite: 36, 37].

## 11. Advancing the Geography: Signature-Zero Exotic 4-Manifolds
While algebraic topology advanced on the algorithmic front, the geometric topology community achieved parallel breakthroughs in classical 4-manifold classification. In 2024, R. Inanç Baykur and Noriyuki Hamada addressed a long-standing void in the geographic mapping of exotic spaces: the construction of small topology, signature-zero 4-manifolds [cite: 4, 12].

### 11.1 The Scarcity of Signature-Zero Exotica
Despite decades of effort following Donaldson and Seiberg-Witten, constructing exotic smooth structures on closed simply connected 4-manifolds with signature zero ($\sigma = 0$) and minimal Euler characteristic remained incredibly difficult [cite: 13, 38]. Because $\sigma = b_2^+ - b_2^-$ must equal zero, these manifolds lie precisely on the "equator" of the geography chart. Gauge-theoretic invariants often behave trivially or exhibit destructive wall-crossing phenomena in this domain unless the manifold is sufficiently large [cite: 4, 13].

### 11.2 The Baykur-Hamada Constructions
Baykur and Hamada produced infinitely many pairwise non-diffeomorphic, irreducible smooth 4-manifolds homeomorphic to:
- $\#_{2m+1}(\mathbb{CP}^2 \# \overline{\mathbb{CP}}^2)$ for each $m \geq 4$
- $\#_{2n+1}(S^2 \times S^2)$ for each $n \geq 5$ [cite: 12, 13].

These manifolds represent the smallest known exotic closed simply connected 4-manifolds with signature zero [cite: 11, 13]. Even more remarkably, each of these homeomorphism classes contains **minimal symplectic 4-manifolds** [cite: 11, 38]. An exotic manifold is irreducible if it cannot be decomposed into a connected sum of smaller manifolds [cite: 4, 39]. The existence of these minimal symplectic configurations conclusively demonstrates that complex geometric structures can exist on topographically restricted topological spaces [cite: 12, 40].

## 12. Symplectic Geometry, Lefschetz Fibrations, and Gompf-Thurston Forms
The methodology employed by Baykur and Hamada relies on the sophisticated manipulation of Lefschetz fibrations [cite: 12]. A Lefschetz fibration is a smooth map from a 4-manifold to a 2-dimensional surface, behaving like a fiber bundle except at a finite set of isolated critical points where the fiber degenerates [cite: 11, 41].

### 12.1 Small Lefschetz Fibrations via Mapping Class Groups
Baykur and Hamada explicitly constructed "small" Lefschetz fibrations over the genus-2 surface [cite: 12, 38]. By representing the monodromy of these fibrations as products of positive right-handed Dehn twists and commutators in the mapping class group of the surface, they systematically controlled the fundamental group and homology of the total space [cite: 12, 42]. They generated both spin and non-spin monodromies by carefully embedding specific curve configurations (like the lantern relation and the four-holed torus relation) into their factorizations [cite: 12, 38].

### 12.2 The Gompf-Thurston Symplectic Construction
To endow these spaces with symplectic geometry, they applied the **Gompf-Thurston construction**. This theorem guarantees that any Lefschetz fibration with a non-torsion fiber class admits a symplectic structure $\omega$ for which the regular fibers and specific sections are symplectic submanifolds [cite: 38, 39]. By applying equivariant Luttinger surgeries (a specific type of Dehn surgery along Lagrangian tori that preserves the symplectic structure but drastically alters the fundamental group), Baykur and Hamada systematically killed the fundamental group of their fibrations while preserving the signature and the minimal symplectic nature of the space [cite: 4, 12]. This surgical precision yielded the exotic $\#_{2n+1}(S^2 \times S^2)$ families [cite: 13, 38].

## 13. Computational Topology: Triangulations of Exotic 4-Manifolds
The surge in algebraic invariants (like the lasagna module) and surgical procedures (Lefschetz fibrations) in 2024 was heavily complemented by the algorithmic mapping of these manifolds by computer scientists. Rhuaidi Antonio Burke introduced a suite of software tools fundamentally bridging computational geometry with smooth 4-manifold topology [cite: 8, 9].

### 13.1 PL Equivalency and Heuristic Simplification
In dimension four, the smooth and piecewise-linear (PL) categories are equivalent [cite: 9]. This means every smooth exotic 4-manifold can be exactly represented by a finite simplicial complex (a triangulation). Burke developed an algorithm that directly translates 4-dimensional Kirby diagrams (link configurations in $S^3$) into explicit 4-manifold triangulations [cite: 8, 9]. 

Given that naïve triangulations of 4-manifolds are astronomically large, Burke deployed a new set of heuristic simplification algorithms utilizing stellar structures and bistellar flips to reduce the triangulations to minimal sizes [cite: 9]. 

### 13.2 Smallest Known Triangulations
Using these tools, Burke computationally generated and analyzed the smallest known triangulations of exotic pairs, corks, and plugs [cite: 8, 9]. He also documented the smallest known triangulation of the K3 surface—a foundational building block in simply connected 4-manifold theory [cite: 9]. The availability of these minimal triangulations allowed researchers to observe structural features previously hidden within the continuous realm, establishing lower bounds on the complexity of 4-manifolds dictated by their topological decomposition into specific "building blocks" like snapped balls and coned solid tori [cite: 9]. The existence of structural subcomplexes identical to Akbulut and Gompf corks within these triangulations acts as a combinatorial obstruction to further simplification, perfectly mirroring the smooth obstructions observed in calculus [cite: 9].

## 14. Exotic 2-Handlebodies with Non-Trivial Second Homology
Rounding out the major developments of 2024-2026 is Kouichi Yasui's expansive theorem on exotic handlebodies [cite: 10, 43]. While Akbulut and Gompf previously proved that certain handlebodies admit multiple smooth structures, Yasui provided a massive generalization for spaces with boundary.

Yasui proved that **any** 4-dimensional 2-handlebody with a non-trivial second homology group can be modified to admit an arbitrary number of exotic smooth structures [cite: 10, 43]. Furthermore, Yasui demonstrated that these manifolds possess pairwise algebraically inequivalent genus functions, creating infinite matrices of exotic submanifolds [cite: 10].

This result strongly implies that "exotica" is not a rare localized phenomenon but a pervasive, fractal-like property of almost all 4-manifolds with sufficient homological depth [cite: 10, 43]. Yasui also proved that every 4-manifold can harbor infinitely many pairwise exotically knotted and exotically embedded codimension-0 submanifolds, meaning the internal topology of these spaces is infinitely entangled [cite: 10]. Yasui specifically linked these findings to invariants of "genus function type," explicitly naming the Ren-Willis lasagna $s$-invariant as a prime mechanism capable of detecting and cataloging these infinite families [cite: 10].

## 15. The Smooth Poincaré Conjecture and Future Trajectories
The ultimate horizon for 4-manifold topology remains the Smooth 4-Dimensional Poincaré Conjecture (S4PC), which posits that the standard 4-sphere $S^4$ is the only smooth manifold homeomorphic to the 4-sphere [cite: 20]. No exotic $S^4$'s are currently known.

The historical strategy, pioneered by Freedman, Gompf, Morrison, and Walker, involved searching for a knot $K$ that is slice in a contractible 4-manifold $W$ (where $\partial W = S^3$) but possesses a non-zero Rasmussen $s$-invariant [cite: 19, 20]. If such a knot exists, $K$ cannot be slice in the standard $B^4$. Consequently, $W$ cannot be diffeomorphic to $B^4$, rendering $W$ an exotic 4-ball. Gluing two such exotic balls together (or capping with a standard ball) yields an exotic $S^4$ [cite: 19, 20].

The advent of the skein lasagna module and the combinatorial detection methods by Ren and Willis breathe immense new life into this program [cite: 20]. Because the lasagna module bypasses the computational dead-ends of gauge theory, algorithmic searches (augmented by software like Burke's and the categorified TQFT frameworks of Blackwell-Krushkal-Luo and Goertz-Wedrich [cite: 27]) are actively scanning for boundary knots that force lasagna $s$-invariants into contradictions [cite: 19, 20]. While an exotic $S^4$ has not yet been found, the tools to find it—if it exists—are now fundamentally algebraic and computationally accessible.

## 16. Conclusion
The span from 2024 to 2026 will be recorded as a golden era in low-dimensional topology. The historical legacies of Selman Akbulut and Robert Gompf—who first mapped the bewildering geography of corks, plugs, and exotic knot traces—have been completely vindicated by an entirely new branch of mathematics. The Ren-Willis cross-link, merging Khovanov homology, the Lee deformation, and the Morrison-Walker-Wedrich skein lasagna module, provided the first analysis-free, purely combinatorial proof of exotic 4-manifolds [cite: 1, 17]. 

Simultaneously, the geometric bounds of these spaces were shattered by Baykur and Hamada’s discovery of minimal symplectic signature-zero exotica [cite: 4, 12], while Yasui highlighted the infinite density of exotic submanifolds in 2-handlebodies [cite: 10, 43]. Supported by algorithmic triangulations and advanced TQFT gluing theories, mathematicians are no longer solely reliant on the partial differential equations of gauge theory. They now possess a robust, combinatorial, and algebraic lens through which to view the smooth fabric of four-dimensional space, paving the way for the ultimate classification of 4-manifolds and the resolution of the Smooth Poincaré Conjecture.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHD70ma5y2mGN_PhU_9tvtjKv3KswDaAEErdTZCjn0PDoPyVRQK_drBbKFOBGVI1hvJvneHJJJDFzVEdSIPRaQ8Y7OBTBTFbQf84iAMTQJVfpcPsxVb6w==)
2. [ed.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvI6KnO2tapyxgpRo4he-dwZPln4EGG4SIj1kPBZWAU0ffqau-z2ZYtA0tFRpEAgDcozRG2UIsAbiXh26SQTWuTX4YSyaX_b4KOLqnGqNZ_yw3jUWTMR5tPmAIoGsVZ7RGOsPRdzN4HeGNiYRY3AZY3P4q8F0=)
3. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFw244hmAOOSOvIHZKYM5T-Ns5PBDF79TBGSb1xkzI4dQ3lVytqrLxm48hSn-sgLMkWJEPYa8gcYWg5v6wzrKsaXfYtzXQztcXLf60eYvPlVl8czXSs9jEuCnWZNpddxg==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQET6vsCre6YlXBb16XP34kHAZHi6ru9AGo47I1-59AcAHatz8UgwJZvo1RuzIUKmcMdVKE0bskCxcTHaTF3y6B6w43I9OegVWJdZE9CtatPb1rdwn_ZqQ==)
5. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjOiXfV0R2EuVaPqGBVKpIU8j9JcCtaWP-osjJzLxBS0Tmo11JolSUcbHIYk3Vq4kwQcRXITGe7RqzizIYvNINP8m8cRU193Jn8zHp8aA8iraMfzOXRDi__C5hw7Y13MsOw3ob_FU6GkLQm8ZmUDec)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHOqSnzz4Ez0ygvLQ2MsLCJRQRpaK8oKWu96MrgmHl_0-JRjEmWBi0Gc3j3COjtfrDMBE8TCPMvmdgZD9kUBlpiF4x1unbtY4AGuxGsYB3x2qkIpFWTE6NTbUsOMEPGjZmgLbb7zV5ZQ0G8yXB7iDpRWKuCubrMvRdlwUoCoLhM-JtfsmBSHwlT2gCbp2bdlThzzExGmHFA_8rxzrNK_QNBkorFgvHNA1k5LBzLwBWLNCIpgfsjKkdHF32sgoYpZRqwysYrNLfQeZAI8Ps6YKyyz8VV0-OMzeuvqwNn4gBc1VzgNigaVDeK069fRtVYXnJ8zyF5z7f0osWfqKDQqCdhEI=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2eNfYAchstBoMLtGgfnJ64yLnUuF0lmF-JFUbcAcVShE_pB4IficCFDTFJ2b4Q3JNTCComS9IHenHHD9Wa4jSEObj-l53YRsyl6iaSbVA3VNkNKro8QQb1A==)
8. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGo3pM3FaAnCk2kPdx3sxGD-omL409YrU6JRWyAsp1WGd1wYppe-MkDF9jpoXvNLCu48EA_yJ9lpfnf2HesVD1oIg7tzcHoPy3JBUcYHTSy21BcHRfrX_lXJoPsYiyXG03oexjVKjySHpmyDbvQA-6hoHJ2-8RDRi2sYS2LsQ==)
9. [uq.edu.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHX5Cbpiv5P0gs5vqwSeKeAIx90-DDYHVLPcvZFFPgow-ZGuSEKsbCri5r5_RTr9oi5VXxRDBh5tOMq0dWBDimviuBCOF8ezRI_JxI7gnnbFAQzizMaogqwHtUJphInkBWb8PC7xuoJEnN4NP9OgxfjHJuaXihtCIIhhIac2cM=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJtVxsDs0QkURBlqwGPVvWwuIclmwY5K7LfvcwMyxSYc3mfnHJdBySQeTCXhXJ_lCe-i94V9yft3yewaxxvIU3T12JL_qgRRcg2U-64iPAp0xgF5vnp93rqA==)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOcKe0i6d6RqduiPt2pElQnjimJw7b5YLQz-_DNxKCnJHpXwu7xvyYA76dESo9nPrMqTPd-d-63aSlHQDjJR4MfLvzO1_N_zpq1sbp_Sab2O3y9lRgPvJ_SjlU-f6jImpeC-No3-WuLBwEF72Md_PuMjV3k5Lfj8zOh9xF-n0iAIaoWlM9hvRLESFLu881FA==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWMqlORxkaNSDjT8jcMEYy8oLHxcq2bQJLZYve8WvHWXzcqGi1VjrKzWI_1EwguGbd_SelBhjz0bha-D8S9fRTPB5SDgKayYzSJS8vpD7tnkKW6lTaKw==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxq2BEepNOs_jQDS4V3qCk3a8rhZFtGoasc4yD4-iePJI3FUIuldLgqFPbL-nUmWzlUH5QvIvvnpbie35uXr0LgZjxcvk88CyahBzBrCu0to_wQ2uPzA==)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzFuzeq8ASrSMKizaMuU2_NTKKwsscrtVLHSjTAEzvg-R9iDBJI8wBbhK2DcF2zZCtq4gRcXbV-dGc9NK9NJwHf05xDM8quzzMNKQRS_K-Nydw80AEEk09r3vvThhlqThytH8BhA0moPFLCGThzkyJg_GXIqu54LSJ-R782X5Rb7y9g1v4MuSXAentM-fjEnbCdU6rwbzfLdw=)
15. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSn13NnQhhur7GLxtG4eoYb0Hm_yLCf7R5Nc583iIMsCLKNcnLlV8hbvuzMneos23kSb7mj4kB6Tg3GB2O6dhO7FMqgAFVKj017hpw4PCwIT0loT_DaMIonwI74JHC2EPqfD3lWt52AlQJPXnIaAOtYyTFF1c2yr2d-Z4MYbdgn559TLmV3-Bzd9LA_alkVw==)
16. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbznlscTihb43hqF7eBtsZ7cMAIGnXl2MEEXsF07WTV_V5GQKpBY5MXkvsM0bheXtr4jeNbTna-WI9vuegHjF-EBds276cmAF1KgpULTwIvciVqvoAmOBPTVS4lo3j_2sZBFU30g79PMrRz2x5pV5oTSI6RxLVPZFfJ3tVEk82wyCPbJrBv2FqGsDbNQ==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcULJF0LtvDnX_A-Lm7gloL6Z6Mbr8Dy5V2xd53X4GSheacRlAMM1aDAcFcV5y7f7Lw53KSdAPeo3yGaCIkm0uXMn-am4HATOaz9C073WnxojLGMSDxQ==)
18. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPCgQ8L838hkRlq7eu4Xtn_JPN34PeEhwj02pDr4gSYtDFD2rLimoQWNePnqsDAN6WM5858Y2SNL4nBPVw0jzp44yzLEnw53WJkWKO7RzCgSwnpYGE_CR7JlVbXuVwDMspfLhuhDQBYmhzoHI=)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF04PTcVNG5FCOzyKh9JVaNyqv-AFiO6TVZKFXjgaJw7kV64s5PMuXyBYkNUcV2bElpUnPF0cKR7kmv_Rpy3ssJfBJnT6EKehfuCThYKnrbZqyemJ6dsp6fYJl4aGwKApb7eCQN8k0M7hUvPOipDAKY4nIviK0cbqNzvaa2pw40xND8Cby2BTo9w_Ayjw8uWMU3_kabp4Q2ePYq_bTLk9D_oKX1O_AN-zp2GHV1AkWnoRvRNg==)
20. [viasm.edu.vn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbvuoqNaVaA3Q-fvYDbOMRlBPdmfcBqf9o0w6VXKVDpXIeMOdl2lJAwMOBMbP_FnWlE5OEpYiU9QFP5TZMWR0a22dmULt60nwL-8hTsB_JSpJvzIOIPa6IuzYOfVeDzJ89HzU6gagKip3BsObr56JzwsYiJGq7p-GzLACB15jO8FbnWgjliO4bgO8wOEmSxZx4BBdgHnoNHs1Bb5Q=)
21. [theopenscholar.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVkh7r7zkJz-LRQrwpEiyM01ccNIjiwsQCelJRYIr1_F_hxjuZ5pfmXnhsMclOqyuhas6kp0saIJOSUg-3hX_UYKWEgRNFAM6TdRgPXb9xM_mPcqtieFqpG-awC4GpK3BQeTw4tmhwTKRDRTqhs-6EzljiuSa7_8TstdZ5cK-WdlzDYc4qQd-S)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjok7hkqN8Ty476tXlK5oOpH-OOWYOTsvp1IlLkAysoXTP5DZHoD9dWSabFQb8FVsA_dl2zLtsfdWjPJewgKOi-UM_-Oi2NKhPF7MJiQ-XbHAcxtnMmNuMVXiMVHQG4Btg_I1MXQF97q95XUIjzDK6sMSmifJIql_ipHcORsy7w1d3aDFuZHqtVJ043itSPEeJnDa2ltTS0Hn1Q2s=)
23. [melissa-zhang.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnRSGrvCecj2h4LdH4S19rxVlDn9BznObfcou4DLEcW2FzumikmsXj4AhRmI6W5TXFYj4THD_96gSUhYIwKV5ekXQQ6XuIBiFfecnszlJyyW2HETp6ZIUL1rXvwj0IaNfNkRSSZuf6Vg==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEH-owB6geCsgNITYDYqipOMKlHBXrHRh0rg7LqzhpUyWLelnIXla-0Oz9QN_X77AKjeW-lg1ZzepdbTIPeRd6_8KBVX4MowCSBWoVW6p-O5SQV0DZSwA==)
25. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEU2-1DDkeMW0yBCzGyoKuv3FYwpq0IjmWqpmNExPl1T9Ja1fEMagbp4xDCCiWNr_tNkdTga7tVOkHnuiL621QfS4fW_WiasFDCRbQonasJu7lKKpZbV7Q39KgmoRnlTMh8ZwRqqdpJO7uslKqS464MIquZCeasJE6zL2Bi9BTMArc)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVpMfFS8z1HTgAhdnbWqor2wqoY6c96hgNFeovPnTI_1hdIhYmqaO9VSqZ9zirHOW4ClGO2vo992SE69QaHF1l1d0EscAV0cY0sdFOSES05dMWO2wcDHA5CQ==)
27. [uni-hamburg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKTZE8saeagKRBi6jSyVLA-65wfgrJ5MnPkw6ambxvD-xKoFJtLYKtOufBKZmb92D5uHmAgx35hfErU8alg72Xc0CfakynqRdeS95CBTnk8pCgO51E3xSdJHSUw66I_LSPm_AtGEuoGR985TZGP0U4agsl5-E6vyVYf4sS)
28. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZYPcb8SDicIV3_QYJvV5sI1OWdfwVL676sC3acldwQ7SX1eKHYXTFNl7kb06i0G2Gt7mG-vhZAi6jIVWMiKw5KeizBZ-KmIpOj4X8BxoMGwvipH-OKqKtgDLptW1ehQI=)
29. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWnfwz6Ue-jVS7xUUsbTYzb7d2IAGVC2TlmRZl9ojZ9jlbqzatEEkeKhJtDumJv9--uvzRQCmoLFmd12y5HsTPSTaDIjhauhyt0XE_HxQNgD2hrgrQQKarFsOjXXDkLL_ZR1JnqZ7UJHBmJnFqLN9t2uNlK0BCS4-6Xbd063lDNhIBQl8BeuAcbL47i0-_DsKRkDbf9y6JmZTRx6gtE77gGNaJ-cGMFtiO6RcB89GALCaC63oSU8KQ_39ISYZNz6ialRo=)
30. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzOUyL_x__Yut6W9qMxtx-hQd2DGBQ9EnjkucMiU6vWmWvZm961P-y3d4cc051QCxjaeoWwkcqaYkLvgNGLJPaOzbTAiQndDPBaE-DWorm8QmG5eB5HcyRFI1kDtiP0SRfO3DV03h4oopI6sVGWzjIvQ==)
31. [osu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQJMWM3SH489zeH3Fohy8guBYjGRErp_fCGlFyQrGJJKePlwYJ4dNFAsR0RzIYKDcQbxWC6CQkRJ18NLLWCNTvCCjiyYK6wIo5VeRMistrSeLCq79OYQAkMw6yUUAxMUojMOrJpbAsN5NeBGQ=)
32. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfvjtaYMyLaWZDL6ggZJfgKfRpFkPv1rhTgFjBEAUIlZ58ns-yAY9PRWCM5ZeNE1Zocc3Jp_2FOvd0DKH8qwBcY25MZ4582LjrVzYUSDs-bud-PFbJs6Ix4ZUJbK-etNTpsf1NsLvAYWj4fTdnFgXjsjpW)
33. [ams.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAJDSmrFkE9-4yeoDJPd6Jc-BfDGP1lLEA21Vqgxz7iApPo_DZ11Rx8Hh0MXRVUJwlyO2kfWLGocth5Hpwo10x-H995mwUL8kqubVeSHzWnoY2puGylm9eIgIsSZ0MPgR0g_ANRqUvZtns6bEC-TUcXizSx7b3wc0=)
34. [vt.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOeT7mFrqyLWIh5tBuPczYQzpO8_Awqh1Z7deyiRYIZeC49pIHRGW8cDI-U6sI0s6hPPaoFSw5jnxSoGO7j7nuQkOcgYzJSjaEhv17TpcAgcPc4kN_DOJsiSDr)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFz7gdzmBqXG7qBqIynaxxucVEumS2D2L9-aUsxoNXimrTi6O9ItGumlqam-rqKEiBkfhwBT3CpAJsGFIoTt3yAdgTh8sNxcJFAWbogIaYEkZKBZT8LLQ==)
36. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHz9ePpJwrWq4rPb22JngCNDDrr7qkvWHAiYppQNiKVyhMFJkjYU4uk37C5ZSxpFODFy-XM87jZcngptRGZn88gW6otk4MEwRuAPjHVncY5AsF6eQgX4g==)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFly1nwxkYRPATOtXEBgRK5lVlXnNRa5XoVdtUgfW6S23H3tgQu9G_y6vNcbYQVU-oO-kV0Rp7T97ulPD2ubL73XA00WInFQZ3RpSOw83LtnJ35aGbqgRVMlQ==)
38. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0da0SnT9dJjJYy8PYWEeSKp82WOTdyqVJ7qgiBM9d9PVzRvfj2_yiTUPu0jLOowUfrAJAZHMdJwHqlK6LjhPd6TQN8H4tYXNJRwfS8kMdaph9XJygi1oCkA==)
39. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_wPAcvYP9Jkky5veHrTNpM9hDKHru1P7qLRYUlmXRo9KvRT7qKde44XFIizqM555iUqjJ7kOHuD_3PvwllKl94NH8Vd2Aez5MWvDYDZ8VSOFjRH5WsDe4cQ==)
40. [metu.edu.tr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1QMzPKOQvEvoBQ9od7bYifAV8EkV2ba1VsWCaOgjkZYFzyvlDcRQZBYj4ofv08T0pW1c52u2NaT7Bwl6HHbR59l4w16GBqIOPafC71JDcRVcfZSqfqgTlz2EzGpBXyCdb)
41. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQ6oaBW941ZVzFVQrB7xopLhddwj6Pw_F6tnyXbV8653FT-7ezMf325-5PPkQ1J1hqKhavybL449U4MjsAdIGO9K4tHpOsZpIVPtpCOYBsT2RXg-19oC5J8KJ_CdBHqIInqrCFTkI8Sa3XKKieWRA=)
42. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnBTM-0CI59SPKluFDHPHDF91J0AVW_pdTt7mxvhVB3XOrNWv9WT0aL9MJIXk5mjAhtyvSNTQFXEya9WGdQJ3kUhB35HevTbH_788wlSsgeFbcGtSQk0j53v-6Hwyx8failGitE0Ci3Kxdy__zrUVjSZknSQtddKyLZ6d9m8OO7umzlQ==)
43. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlhTBwmqsnq2ifgglO3uEyZtifbH_TdaE--kuscuz0miy9j5uRG74GYkVfvcizPPV9t5E2wLjUoP6xXU8x3PM4dqNu0NCs0U2h_mZJGUrLhbvQ2_Pp9w==)

