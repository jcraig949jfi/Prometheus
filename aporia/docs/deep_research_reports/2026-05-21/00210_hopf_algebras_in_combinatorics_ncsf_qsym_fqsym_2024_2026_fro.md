# Hopf algebras in combinatorics (NCSF, QSym, FQSym) 2024-2026 frontier

**Pythia queue id:** 210
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChZRVWtQYXAyRU5ORG11Z2U2N2JfUkRnEhZRVWtQYXAyRU5ORG11Z2U2N2JfUkRn
**Elapsed:** 309s
**Completed at:** 2026-05-21T18:10:00.080783+00:00

---

# The Frontier of Combinatorial Hopf Algebras: NCSF, QSym, and FQSym (2024–2026)

### Key Points
*   **Fundamental Structures:** Combinatorial Hopf algebras provide a rigorous mathematical framework for decomposing and synthesizing complex combinatorial objects. Research suggests that these structures mirror the foundational principles of breaking down counting problems into more manageable subproblems.
*   **The Classical Triad:** The interplay between Symmetric Functions (Sym), Quasisymmetric Functions (QSym), and Noncommutative Symmetric Functions (NSym/NCSF) forms the bedrock of modern algebraic combinatorics. It seems likely that the Malvenuto-Reutenauer algebra of Free Quasisymmetric Functions (FQSym) serves as a universal terminal structure bridging these domains.
*   **Recent Superspace Extensions:** Between 2024 and 2026, researchers have pushed the boundaries of these algebras into "superspace," incorporating both commuting and anticommuting (fermionic) variables. The evidence leans toward superspace analogues like $sNCQSym$ and $sFQSym$ completing a long-sought hierarchy of super-algebras.
*   **New Combinatorial Bases:** Recent years have witnessed the construction of novel Hopf algebras built on partition diagrams (ParSym and ParQSym) and partially commutative colored variables ($QSym_A$ and $NSym_A$), significantly expanding the scope of non-commutative representation theory.
*   **Peak Algebras in Noncommuting Variables:** The classical descent-to-peak maps have recently been successfully generalized to noncommuting variables, uncovering deep connections between Schur Q-functions and generalized Dehn-Sommerville equations.

### Introduction to the Frontier
Combinatorial Hopf algebras are abstract mathematical structures that have proven remarkably effective at solving complex counting and structural problems. Simply put, an algebra allows us to multiply things together (synthesize), while a "coalgebra" allows us to pull things apart (decompose). A Hopf algebra seamlessly combines both operations, allowing mathematicians to mathematically model the ways in which discrete structures—like trees, networks, or permutations—can be broken down and reassembled. 

In recent decades, three specific Hopf algebras have dominated the landscape: the Noncommutative Symmetric Functions (NCSF or NSym), the Quasisymmetric Functions (QSym), and the Free Quasisymmetric Functions (FQSym). While classical symmetric functions have been studied for over a century, these modern non-commutative and quasi-symmetric variants allow mathematicians to track specific orderings and arrangements that classical symmetries would otherwise ignore. 

As we look at the research frontier from 2024 to 2026, the field has exploded with high-dimensional generalizations. Mathematicians are now applying these frameworks to "superspace" (which borrows concepts of fermion and boson particles from quantum physics), colored and partially commutative variables, and complex partition networks. The following report provides an exhaustive, rigorously detailed academic synthesis of these cutting-edge developments, exploring how the classical triad of NSym, QSym, and FQSym is being continuously deformed, expanded, and applied to solve newly emerging challenges in advanced algebraic combinatorics.

---

## 1. Foundations of Combinatorial Hopf Algebras

### 1.1 Algebraic and Coalgebraic Preliminaries
To contextualize the advanced 2024-2026 frontiers of NCSF, QSym, and FQSym, it is imperative to establish the rigorous algebraic foundation of Combinatorial Hopf Algebras (CHAs). Roughly speaking, a Hopf algebra is a vector space over a field $\mathbb{K}$ (or a commutative ring $R$) equipped with two fundamental operations: a multiplication that synthesizes complex structures, and a comultiplication that models the notion of breaking down a complex structure into simpler components [cite: 1]. This dual nature perfectly mirrors the combinatorial principle of decomposing a counting problem into smaller, more manageable subproblems [cite: 1, 2].

Formally, a bialgebra $\mathcal{H}$ over a field $\mathbb{K}$ is a vector space equipped with an associative multiplication $\mu: \mathcal{H} \otimes \mathcal{H} \to \mathcal{H}$, a unit map $\eta: \mathbb{K} \to \mathcal{H}$, a coassociative comultiplication $\Delta: \mathcal{H} \to \mathcal{H} \otimes \mathcal{H}$, and a counit $\epsilon: \mathcal{H} \to \mathbb{K}$ [cite: 1, 3]. These maps must satisfy strict compatibility conditions; specifically, the comultiplication $\Delta$ and the counit $\epsilon$ must be algebra homomorphisms, or equivalently, the multiplication $\mu$ and unit $\eta$ must be coalgebra homomorphisms [cite: 4]. 

A Hopf algebra is a bialgebra equipped with an additional $\mathbb{K}$-linear anti-endomorphism known as the antipode, denoted $S: \mathcal{H} \to \mathcal{H}$ [cite: 2, 3]. The antipode satisfies the fundamental property that $\mu \circ (S \otimes \text{id}) \circ \Delta = \eta \circ \epsilon = \mu \circ (\text{id} \otimes S) \circ \Delta$ [cite: 3]. In the context of graded, connected bialgebras—which dominate combinatorial applications—the antipode is guaranteed to exist and is uniquely determined [cite: 4, 5]. Takeuchi's formula provides an explicit way to compute the antipode in such incidence Hopf algebras [cite: 2]. 

### 1.2 Combinatorial Hopf Algebras (CHAs)
A Combinatorial Hopf Algebra is conventionally defined as a pair $(\mathcal{H}, \zeta)$, where $\mathcal{H}$ is a graded, connected Hopf algebra over a field, and $\zeta: \mathcal{H} \to \mathbb{K}$ is a character, meaning it is a linear and multiplicative functional [cite: 6, 7]. The character theory of Hopf algebras, heavily pioneered by Aguiar, Bergeron, and Sottile, provides a framework for understanding the terminal objects in categories of such algebras [cite: 2, 7]. 

In combinatorics, it is proven that the algebra of quasisymmetric functions, QSym, serves as the terminal object in the category of combinatorial Hopf algebras equipped with a single character [cite: 1, 8]. Because QSym is the terminal object, any combinatorial Hopf algebra $\mathcal{H}$ possesses a unique canonical Hopf morphism to QSym [cite: 6, 8]. This universality theorem explains the ubiquity of quasisymmetric functions as generating functions across vast arrays of combinatorial species, posets, and trees [cite: 2, 6].

## 2. The Classical Triad: Sym, QSym, and NSym

The landscape of algebraic combinatorics is anchored by the classical ring of symmetric functions (Sym), its generalization to Quasisymmetric Functions (QSym), and the dual Hopf algebra of Noncommutative Symmetric Functions (NSym or NCSF). 

### 2.1 Symmetric Functions (Sym)
The algebra of symmetric functions, Sym, is a graded subalgebra of the ring of formal power series $\mathbb{K}[[x_1, x_2, \dots]]$ characterized by invariance under any permutation of the variables [cite: 9, 10]. Sym is freely generated as a commutative algebra by the elementary symmetric functions $e_n$, the complete homogeneous symmetric functions $h_n$, or the power sum symmetric functions $p_n$ [cite: 2, 7]. It boasts an orthonormal basis given by the Schur functions $s_\lambda$, which are fundamental in the representation theory of the symmetric group and the general linear group [cite: 4, 9]. As a Hopf algebra, Sym is remarkable because it is both commutative, cocommutative, and self-dual [cite: 2, 4].

### 2.2 Quasisymmetric Functions (QSym)
Quasisymmetric functions, introduced by Gessel in 1984, generalize symmetric functions by requiring a weaker condition: a formal power series $f \in \mathbb{K}[[x_1, x_2, \dots]]$ of bounded degree is quasisymmetric if the coefficient of any monomial $x_{i_1}^{\alpha_1} x_{i_2}^{\alpha_2} \cdots x_{i_k}^{\alpha_k}$ depends only on the composition $\alpha = (\alpha_1, \alpha_2, \dots, \alpha_k)$ of exponents, provided that the indices are strictly increasing ($i_1 < i_2 < \dots < i_k$) [cite: 8, 11]. 

QSym contains Sym as a sub-Hopf algebra, because every symmetric function is trivially a quasisymmetric function [cite: 8, 9]. A natural basis for the graded components of QSym is the monomial basis $M_\alpha$, indexed by compositions [cite: 9]. The multiplication of monomial quasisymmetric functions is governed by the "quasishuffle" (or overlapping shuffle) product, which sums over ways to interleave and occasionally merge the parts of compositions [cite: 3, 12]. As a Hopf algebra, QSym is equipped with a deconcatenation coproduct:
\[ \Delta(M_\alpha) = \sum_{\alpha = \alpha' \cdot \alpha''} M_{\alpha'} \otimes M_{\alpha''} \]
where the sum ranges over all ways to split the composition $\alpha$ into a concatenation of two compositions $\alpha'$ and $\alpha''$ [cite: 3, 4].

QSym has immense applications in enumerative combinatorics, particularly in the study of P-partitions, reduced decompositions in finite Coxeter groups via Stanley symmetric functions, Schubert polynomials, and Macdonald polynomials [cite: 8, 12]. 

### 2.3 Noncommutative Symmetric Functions (NSym / NCSF)
The graded Hopf algebra dual of QSym is the algebra of Noncommutative Symmetric Functions, universally denoted as NSym or NCSF [cite: 7, 13]. NSym was introduced in 1995 by Gelfand, Krob, Lascoux, Leclerc, Retakh, and Thibon [cite: 3, 14]. It is defined as the free associative algebra generated by noncommuting symbols $\{H_1, H_2, \dots\}$, equipped with no relations [cite: 3, 13]. 

For any composition $\alpha = (\alpha_1, \dots, \alpha_k)$, the complete homogeneous noncommutative symmetric function is defined by simple concatenation:
\[ H_\alpha = H_{\alpha_1} H_{\alpha_2} \cdots H_{\alpha_k} \]
The set $\{H_\alpha\}$ indexed by all compositions forms a basis for NSym [cite: 3, 13]. Because NSym is the graded dual of QSym, there exists a canonical non-degenerate Hopf pairing $\langle \cdot, \cdot \rangle: \text{NSym} \otimes \text{QSym} \to \mathbb{K}$ defined by $\langle H_\alpha, M_\beta \rangle = \delta_{\alpha, \beta}$ [cite: 3, 12].

The comultiplication in NSym is determined by duality from the multiplication in QSym, resulting in:
\[ \Delta(H_n) = \sum_{i+j=n} H_i \otimes H_j \]
extended multiplicatively to all of NSym [cite: 7]. Consequently, NSym is a non-commutative, cocommutative Hopf algebra [cite: 15]. The projection from NSym to Sym, mapping the non-commuting generator $H_n$ to the commuting complete homogeneous symmetric function $h_n$, acts as a graded Hopf morphism [cite: 7, 16]. 

## 3. Free Quasisymmetric Functions (FQSym) and the Malvenuto-Reutenauer Algebra

The apex of the classical combinatorial Hopf algebraic hierarchy is the Malvenuto-Reutenauer Hopf algebra of permutations, also known as the algebra of Free Quasisymmetric Functions (FQSym) [cite: 8, 17]. FQSym serves as a terminal object governing product and coproduct rules through permutations and the weak Bruhat order [cite: 17, 18]. 

### 3.1 Structure of FQSym
FQSym is constructed on the linear span of all permutations across all symmetric groups $\mathfrak{S}_n$ [cite: 18, 19]. A standard basis for FQSym, often denoted $F_\sigma$ or $G_\sigma$ (for $\sigma \in \mathfrak{S}_n$), admits multiplication and comultiplication rules directly linked to permutation operations [cite: 10, 20]. 

The multiplication in FQSym relies on the shifted shuffle product [cite: 19]. Given a permutation $\sigma \in \mathfrak{S}_m$ and $\tau \in \mathfrak{S}_n$, their product is the sum of all permutations in $\mathfrak{S}_{m+n}$ obtained by shuffling the letters of $\sigma$ with the letters of $\tau$ shifted by $m$ [cite: 10, 19]. 
The coproduct in FQSym uses the deconcatenation of the values of the permutation, splitting a permutation into a prefix and suffix, and standardizing both pieces [cite: 19]. 

FQSym is uniquely fascinating because it is self-dual, non-commutative, and non-cocommutative [cite: 10, 18]. FQSym contains NSym as a Hopf subalgebra and projects onto QSym as a quotient, placing it in a central position within a commutative diagram of Hopf algebras [cite: 8, 18]. Furthermore, FQSym acts as a generalized Frobenius characteristic for certain categories of modules over the 0-Hecke algebra, providing profound connections to non-commutative representation theory [cite: 21, 22].

## 4. The 2024-2026 Frontier: Colored and Partially Commutative Variables

A major vector of research stretching through 2024 has been the generalization of QSym and NSym using partially commutative and colored variables, primarily spearheaded by mathematicians like Spencer Daugherty [cite: 13, 23].

### 4.1 The Algebras $QSym_A$ and $NSym_A$
In 2024, the quasisymmetric functions were successfully generalized for a finite alphabet of colors, denoted $A$, resulting in the colored quasisymmetric functions $QSym_A$ [cite: 13]. These generalizations were constructed using *partially commutative colored variables* [cite: 24, 25]. 

For a color $a \in A$, researchers define the set of infinite colored variables $x_a = \{x_{a,1}, x_{a,2}, \dots\}$ and let $x_A = \bigcup_{a \in A} x_a$ [cite: 13, 24]. A critical innovation here is the partial commutativity: variables only commute if their second indices (the integer subscripts) are different. Specifically, $x_{a,i} x_{b,j} = x_{b,j} x_{a,i}$ if $i \neq j$, but if $i=j$, the variables do not commute [cite: 24].

The dual algebra to $QSym_A$ is the colored noncommutative symmetric functions, $NSym_A$ [cite: 13]. $NSym_A$ generalizes NSym through a deep relationship with the Hopf algebra of colored rooted trees [cite: 13, 24]. The natural basis for $NSym_A$ is identified with the set of "sentences" over the alphabet $A$. A "word" over $A$ is a finite sequence of colors, and a "sentence" is a finite sequence of non-empty words [cite: 3, 23]. The Hopf algebra of sentences is equipped with multiplication defined by the concatenation of sentences, while comultiplication relies on sophisticated subset deconcatenations [cite: 3, 23].

### 4.2 Generalized Commutative Images: $Sym_A$ and $PSym_A$
Within this frontier framework, researchers defined an algebra $Sym_A$ that sits inside $QSym_A$ as a Hopf subalgebra [cite: 13, 14]. When the alphabet $A$ has a size of exactly one, $Sym_A$ collapses into an algebra perfectly isomorphic to the classical symmetric functions Sym [cite: 14, 25]. 

Correspondingly, the graded dual of $Sym_A$ is defined as $PSym_A$, which represents the commutative image of $NSym_A$ [cite: 13, 14]. This suite of algebras ($QSym_A$, $NSym_A$, $Sym_A$, $PSym_A$, alongside their classical counterparts) can be placed in a beautiful commutative diagram connected by canonical Hopf morphisms [cite: 13]. The expansion of multiplication, comultiplication, and the antipode across these colored spaces has been explicitly documented, including the creation of dual bases that generalize the classical Schur functions to these colored, partially commutative regimes [cite: 13].

### 4.3 Colored Dual Immaculate Functions
One of the major triumphs in this colored variable theory (published in 2023-2024) is the generalization of the immaculate and dual immaculate bases [cite: 3, 26]. The *colored dual immaculate functions* are defined combinatorially via specialized tableaux [cite: 3, 26]. The immaculate bases are highly significant in NSym for their connections to representation theory, and extending them to $NSym_A$ involved using creation operators to study expansions, establishing right Pieri rules, and developing methods for expanding colored immaculate functions into colored ribbon bases [cite: 3, 26].

## 5. The 2024-2026 Frontier: Superspace Generalizations

Perhaps the most dramatic paradigm shift in the combinatorial Hopf algebra landscape reaching maturity in 2026 is the complete mapping of the "superspace hierarchy" [cite: 17, 27]. Superspace algebraic combinatorics extends classical theory by operating over two sets of variables: standard commuting variables (bosonic) and anticommuting variables (fermionic) [cite: 17].

### 5.1 Symmetric and Quasisymmetric Functions in Superspace
The algebra of symmetric functions in superspace, denoted $sSym$, was developed as a subalgebra of invariants within $\mathbb{Q}^\theta[[x]]$, where $x = (x_1, x_2, \dots)$ are commuting variables and $\theta = (\theta_1, \theta_2, \dots)$ are anticommuting (Grassmannian) variables satisfying $\theta_i \theta_j = -\theta_j \theta_i$ and $\theta_i^2 = 0$ [cite: 17, 27]. $sSym$ arises naturally in physics, particularly in theories involving supersymmetry, and possesses a Hopf superalgebra structure [cite: 12, 17]. 

Similarly, the Quasisymmetric Functions in Superspace ($sQSym$) and the Noncommutative Symmetric Functions in Superspace ($sNSym$) were previously established as a pair of dually paired Hopf superalgebras [cite: 12, 27]. The structures are $\mathbb{Z}_2$-graded by their fermionic degree [cite: 12]. The bases of $sQSym$ and $sNSym$ are no longer indexed merely by integer compositions, but by *dotted compositions*, which account for the fermionic signs and parities [cite: 12, 17]. The product of monomials in $sQSym$ is described via overlapping super-shuffles, while the coproduct is a signed deconcatenation [cite: 12].

### 5.2 The 2026 Breakthrough: $sNCQSym$ and $sFQSym$
Despite the existence of $sSym$, $sQSym$, and $sNSym$, the superspace analogues of the noncommutative quasisymmetric functions and the Malvenuto-Reutenauer algebra (FQSym) remained an unsolved frontier until a definitive set of papers in 2026 [cite: 17, 27]. 

Researchers formally introduced the algebra of Quasisymmetric Functions in Noncommuting Variables in Superspace, $sNCQSym$, and constructed the Hopf superalgebra of Free Quasisymmetric Functions in Superspace, $sFQSym$ [cite: 17, 27]. 
To construct $sNCQSym$, researchers generalized the notion of packed words to accommodate superspace parities, characterizing quasisymmetry via a "superspace standardization" algorithm [cite: 17]. The elements of $sNCQSym$ are naturally indexed by *set supercompositions*, which generalize the classical set compositions [cite: 17, 27]. $sNCQSym$ acts as an invariant algebra under a noncommuting analogue of the quasisymmetrizing action of the infinite symmetric group $\mathfrak{S}_\infty$ in superspace [cite: 17, 27].

By isolating a distinguished class of minimal elements within the partial order of set supercompositions, termed *superpermutations*, researchers successfully generated the superspace analogue of the Malvenuto-Reutenauer algebra, $sFQSym$ [cite: 17, 27]. 
The $sFQSym$ sub-Hopf superalgebra possesses a monomial basis formed via Möbius inversion on the *super left weak order* [cite: 17, 27]. The product and coproduct rules for these bases explicitly rely on super-shuffles and global super-descents [cite: 17]. Ultimately, an abelianization morphism $\pi: sNCQSym \to sQSym$ was constructed, demonstrating that the noncommutative structures strictly project onto the commuting ones, successfully mapping the fundamental basis of $sFQSym$ onto the fundamental basis of $sQSym$ [cite: 27].

## 6. The 2024-2026 Frontier: Partition Diagrams and ParSym

Simultaneous to the advances in colored variables and superspace, 2024 and 2025 witnessed the creation of completely novel Combinatorial Hopf Algebras built upon the combinatorial topology of partition diagrams. 

### 6.1 The Hopf Algebra of Partition Diagrams: ParSym
In 2024-2025, John M. Campbell successfully endowed the combinatorial objects that index the bases of partition algebras with a full Combinatorial Hopf Algebra structure, naming it ParSym [cite: 15, 16]. 

Partition algebras, which play fundamental roles in statistical mechanics and Schur-Weyl duality, possess bases indexed by partition diagrams—essentially bipartite graphs depicting connections between two rows of vertices [cite: 15]. Prior to 2024, partition algebras had not been equipped with Hopf algebra or bialgebra structures [cite: 15]. 

Campbell introduced ParSym by heavily mimicking the structural lifting of NSym [cite: 15, 28]. Recall that in NSym, the product of the complete homogeneous basis elements is given by the concatenation of compositions: $H_\alpha H_\beta = H_{\alpha \cdot \beta}$ [cite: 15, 16]. Campbell lifted this rule to partition diagrams by setting:
\[ H_\pi H_\rho = H_{\pi \otimes \rho} \]
where $\pi \otimes \rho$ is the horizontal concatenation of the partition diagrams $\pi$ and $\rho$ [cite: 15, 16]. This natural weighting generates a free, graded algebra ParSym. 

To endow ParSym with a coalgebra structure, Campbell utilized an analogue of "near-concatenations" for partition diagrams, formulating a coproduct that satisfies the critical coassociativity axioms [cite: 15, 16]. Unlike the previously known Hopf algebra of set partitions (NCSym), ParSym projects directly onto NSym via a natural "forgetful" morphism, analogous to how NSym projects onto Sym [cite: 16]. To establish the antipode for ParSym, Campbell introduced an analogue of the elementary generators ($E$-generators) of NSym and utilized a sign-reversing involution [cite: 15, 16]. A spectacular feature of ParSym is that the standard diagram subalgebras of partition algebras (such as the Brauer algebra, Temperley-Lieb algebra, or algebras of perfect matchings and planar diagrams) naturally form Hopf subalgebras of ParSym simply by restricting the indexing sets [cite: 16].

### 6.2 The Graded Dual: ParQSym
Following the introduction of ParSym, researchers Lingxiao Hao and Shenglin Zhu (published in late 2025/2026) successfully constructed its graded dual, denoted ParQSym [cite: 11, 29]. 

Mirroring the transition from NSym to QSym, the CHA structure of ParQSym was described in an explicitly combinatorial way [cite: 11, 29]. ParQSym functions as the quasisymmetric counterpart to partition diagrams. The research explicitly defined subcoalgebras, Hopf subalgebras, gradings, and filtrations of both ParSym and ParQSym, proposing bases that act as direct analogues to the distinguished complete, elementary, and ribbon bases of NSym, and the monomial and fundamental bases of QSym [cite: 11, 29].

## 7. The 2024-2026 Frontier: Peak Algebras in Noncommuting Variables

Another major theoretical expansion from 2025 to 2026 lies in the non-commutative lifting of "Peak Algebras," led by Farid Aliniaeifard and Shu Xiao Li [cite: 30, 31]. 

### 7.1 The Classical Peak Algebra
In permutations, a "descent" occurs when a sequence decreases (e.g., $\sigma_i > \sigma_{i+1}$). A "peak" occurs when a value is strictly greater than both its predecessor and successor ($\sigma_{i-1} < \sigma_i > \sigma_{i+1}$) [cite: 32]. In 1997, John Stembridge introduced the theory of enriched $(P, \gamma)$-partitions to study peaks, proving that the generating functions of these enriched partitions generate a sub-algebra of QSym called the Peak Algebra ($\Pi$) [cite: 31, 32]. 

Stembridge defined the descent-to-peak map $\Theta_{QSym}: QSym \to \Pi$, mapping standard generating functions to enriched generating functions, and showed that the dimension of the homogenous degree-$n$ components of $\Pi$ is governed by the number of odd compositions [cite: 31]. Furthermore, the restriction of the map $\Theta_{QSym}$ to the symmetric functions Sym perfectly yields the Hopf algebra of Schur Q-functions, a foundational structure in the projective representations of symmetric and alternating groups [cite: 4, 33].

### 7.2 Extension to Noncommuting Variables ($NC\Pi$)
In 2025 and 2026, Aliniaeifard and Li introduced the noncommutative analogues of Stembridge's architecture [cite: 30]. They defined the *Labelled Descent-to-Peak Map*, denoted $\Theta_{NCQSym}$, acting upon the Hopf algebra of quasisymmetric functions in noncommuting variables (NCQSym) [cite: 30]. 

The image of this map defines the *Peak Algebra in Noncommuting Variables*, denoted $NC\Pi$ [cite: 30]. The researchers rigorously demonstrated that $NC\Pi$ forms a highly structured Hopf algebra, providing closed formulas for its product and coproduct utilizing generalized chromatic functions [cite: 31]. 

Crucially, the dimension of the homogenous functions of degree $n$ within $NC\Pi$ equals the number of *odd set compositions* (where all subsets in the composition have an odd size), connecting the structure directly to OEIS integer sequence A006154 [cite: 31, 33]. 

### 7.3 Schur Q-Functions in Noncommuting Variables
Within this generalized space, Aliniaeifard and Li defined the Hopf algebra of Schur Q-functions in noncommuting variables [cite: 30]. They showed that restricting the descent-to-peak map $\Theta_{NCQSym}$ to the non-commutative symmetric functions (NCSym) perfectly outputs these noncommuting Schur Q-functions [cite: 33]. 

These functions maintain combinatorial properties strikingly analogous to classical Schur Q-functions, indexed by odd set partitions. Furthermore, the expansion of enriched monomial bases of $NC\Pi$ into the monomial basis of NCQSym was proven to satisfy the generalized Dehn-Sommerville equations of Bayer and Billera [cite: 30, 31]. As a structural finale, the researchers proved that the noncommuting peak algebra $NC\Pi$ behaves as a left co-ideal of NCQSym under the internal coproduct, directly extending Schocker's prior results for the commutative peak algebra [cite: 31, 33].

## 8. The 2024-2026 Frontier: Permuted Noncommutative Symmetric Functions (PNSym)

From 2024 into 2026, Darij Grinberg introduced a spectacular new combinatorial Hopf algebra dubbed PNSym ("Permuted Noncommutative Symmetric Functions") [cite: 5, 34].

### 8.1 The Solomon Mackey Formula and Endomorphisms
The creation of PNSym stems from solving a generalization of the Solomon Mackey formula for graded bialgebras [cite: 5]. For any graded connected bialgebra $H$, operations defined by projecting iterated tensor products onto their multigraded components (and then multiplying them back) form natural Adams operators [cite: 34, 35]. Specifically, Grinberg studied maps $p_{\alpha, \sigma}: H \to H$, which project $H^{\otimes k}$ onto a specific degree distribution indexed by a composition $\alpha$, permute the tensor factors according to a permutation $\sigma$, and then multiply them back [cite: 35].

When the algebra $H$ is strictly cocommutative, the composition of such operators reduces simply to the rules governed by the standard Noncommutative Symmetric Functions (NSym) [cite: 5, 34]. However, when $H$ is a *general* connected graded bialgebra (lacking cocommutativity), the standard NSym formulation fails to encapsulate the convolution and composition of these generalized operators [cite: 34].

### 8.2 The Construction of PNSym
To govern these operators for an arbitrary connected graded bialgebra, Grinberg constructed PNSym [cite: 5, 34]. The underlying basis elements of PNSym are indexed by "mopiscotions" (a portmanteau related to compositions and permutations) and "weak mopiscotions" $F_{\alpha, \sigma}$, where $\alpha$ is a weak composition and $\sigma$ is a permutation [cite: 5, 34]. 

PNSym is uniquely equipped with three interactive operations:
1.  An **"internal product"** ($\ast$), which governs the composition $p_{\alpha, \sigma} \circ p_{\beta, \tau}$ of operators [cite: 34].
2.  An **"external product"** ($\cdot$), which corresponds to the convolution $p_{\alpha, \sigma} \star p_{\beta, \tau}$ of operators on the bialgebra $H$ [cite: 34, 35].
3.  A **coproduct** ($\Delta$), which corresponds to the action of operators on the tensor product of two bialgebras [cite: 34].

The graded structure of PNSym ensures that $F_{\alpha, \sigma}$ is homogeneous of degree $|\alpha|$. PNSym stands out in the 2024-2026 frontier as a profound universal algebra that lifts classical representation-theoretic identities (like Patras's 1994 formulas) to the absolute widest class of general graded connected Hopf algebras, proving invaluable for algorithmic checks of algebraic identities [cite: 5, 35].

## 9. Operads and Quasi-symmetrizing Actions (2025)

The frontier of Hopf algebraic combinatorics is deeply intertwined with operad theory and infinite symmetric group actions. 

### 9.1 Operads of Packed Words
In early 2025, Samuele Giraudo and Yannic Vargas advanced the theory of operads in relation to these Hopf algebras [cite: 20]. An operad is an algebraic structure that models operations with multiple inputs and one output, capturing compositional symmetries. The standard associative operad ($As$) is defined on the linear span of permutations, and its structure heavily underpins symmetric operad axioms [cite: 20]. 

Giraudo and Vargas built two novel analogues of the $As$ operad utilizing the linear span of *packed words* [cite: 20]. By interpreting a packed word as a surjective map between finite sets, they constructed one operad graded by the cardinality of the domain, and a second graded by the cardinality of the codomain [cite: 20]. 

This construction forms a hierarchy directly mirroring the classical hierarchy of combinatorial Hopf algebras. Just as the Malvenuto-Reutenauer Hopf algebra (FQSym) operates on permutations, the Loday-Ronco algebra on binary trees, and NSym on compositions, this new operadic hierarchy maps packed words onto a generalized Malvenuto-Reutenauer space, Schröder trees, and ternary words [cite: 20]. Furthermore, the researchers derived an analogue of the classical Dynkin idempotents for these operads of packed words [cite: 20].

### 9.2 Free and Parking Quasi-symmetrizing Actions
Simultaneously in 2025, Adrien Segovia mapped deep representation-theoretic actions generating FQSym and its parking-function variants [cite: 10]. Historically, the elements of the classical symmetric functions (Sym) are trivially defined as invariants under the action of the symmetric group permuting variables. In 2000, Florent Hivert proved that QSym and word quasi-symmetric functions (WQSym) could likewise be realized as invariants under a specialized "quasi-symmetrizing action" [cite: 10]. 

Segovia defined two actions of the infinite symmetric group on the set of words of positive integers: the *free quasi-symmetrizing action* and the *parking quasi-symmetrizing action* [cite: 10]. The invariants of these highly non-trivial actions cleanly recover the dual Hopf algebras $FQSym^*$ and $PQSym^*$ (where $PQSym$ is the Novelli-Thibon algebra of parking quasi-symmetric functions) [cite: 10, 36]. 

Segovia pushed this action further by introducing a tuning parameter $r \in (\mathbb{N} \setminus \{0\}) \cup \{\infty\}$. He proved that the space of invariants under these $r$-actions generates an infinite chain of strictly nested, graded Hopf subalgebras inside $PQSym^*$ [cite: 10]. The extreme case ($r = \infty$) yields enumerative results intricately mapping to trees with maximal decreasing subtrees of prescribed sizes [cite: 10]. 

## 10. Computational Frontiers: SageMath Implementation
As the combinatorial complexity of FQSym, NSym, and QSym has reached hyperspace (superspace, partition diagrams, colored variables), the algorithmic implementations inside computer algebra systems have become mission-critical. Throughout 2024-2025, the open-source mathematics software SageMath drastically expanded its `sagemath-combinat` framework to compute natively with these abstract structures [cite: 37, 38].

The modern implementation relies on the category framework to model abstract combinatorial Hopf algebras with "polynomial realizations" [cite: 36, 38]. Because a single combinatorial Hopf algebra can be instantiated in different bases (e.g., FQSym has fundamental $F_\sigma$, dual $G_\sigma$, and monomial basis elements), the software treats the abstract algebra as a singular object, defining products, coproducts, and morphisms *only* on the basis elements and dynamically extending them by linearity [cite: 38]. The use of standardizations, packings, and "alphabet doubling" algorithms internally maps abstract word quasi-shuffles into explicit computational tensor products, allowing experimental mathematicians to automatically generate and verify massive structural identities in FQSym, WQSym, PQSym, and NSym [cite: 36, 38].

## 11. Conclusion
The span of years from 2024 to 2026 marks a golden age in the study of Combinatorial Hopf Algebras. What began as a triad of classical architectures—the symmetric (Sym), quasisymmetric (QSym), and noncommutative symmetric functions (NSym/NCSF), crowned by the free permutations of the Malvenuto-Reutenauer algebra (FQSym)—has been spectacularly fractured and rebuilt in higher dimensions. 

The introduction of partially commutative colored variables ($QSym_A$, $NSym_A$) fundamentally broadens the algebraic scope to accommodate semi-commuting systems. The realization of the superspace Malvenuto-Reutenauer algebra ($sFQSym$) definitively unifies commuting and anticommuting bosonic-fermionic geometries under one combinatorial roof. The projection of Hopf structures onto partition diagrams (ParSym) resolves a longstanding void in the structure of partition algebras, while the descent-to-peak noncommutative maps ($NC\Pi$) weave peak statistics into generalized Dehn-Sommerville geometry. And with Grinberg's monumental universal operator algebra (PNSym), the functional mapping of generalized bialgebras is now algorithmically categorized. 

As we advance past 2026, the boundaries between representation theory, algebraic geometry, statistical physics, and pure operad combinatorics have been permanently blurred by the infinite adaptivity of the Hopf algebraic framework.

**Sources:**
1. [tugraz.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGazPBz61qgB2f7nGMQJaPWV_U1n_dYnH4MFxJT6w7I-gH8a1NjKQr2Tvug9TMXSedonZ7htAOEU1oZoCboKWGdAnFDncKl5ooY7w7ziffXw-ATnHhcPHsMYCyqCr1vsDW8ifPzLsizdZUnFmWgd0U_3zLeSU3sX9zS)
2. [diva-portal.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYMYfhs0mjBXCmXq0nCQ1rcD3NPuXbaM33cNAGfVM8aPe609a2Qn8vQS-C10b0OIl0X76xrZBDw_C4emwAh5k4IlnUAm-N01mR96plHjM0VDs1Dtvcoa_ypF_e4M-PGyqYD1vjwxSBvIP26F_qQah55FQWzEczE_E=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLc-c6A0rG3pcZwhv6U4xYvm9JI6gCKeXeRYhUI7ibyAca__eWhhUWL2Pxv30KqBSbuwmfrZwvWK3OEyl4jVn_zgz4xLQjejp9Sq0j0zlLTnxNDMw1PA==)
4. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEn9QIC-fOzpfE7i__lRoc4Dq3hWUHRdUFXtTGfTNASV7Kr0zvidanjRnHYMjv4R0pRLpQlP1cciNnl2rP7DfmLmkmMpAvosuJfWUNfuMHad1rLFSBWLNhdshDHyp4QKEf_5fuUdfOiTWH1GJjGzTb-)
5. [lmu.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvzxQZq7WK6SqRKAsVi_HRrwc95tvWZIx7cTcY_7KL1Ak7YPwV3pMKAh90i7Kgv-mPvkHhhpT_NkffGMl5j-nDA-t498YK8NggtX-HMA_0xy0_0_7XqKXPoEX3CcSz1U7FP3h5JJkfZzgNLpVUtPVSLoHt)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBOM3fSHgPzOOMoSiXEXBtzdDtXmkt8RxBXnXUvztXWo8k7cuwvtl9y-hpnsgEEnKzGaz5sBO7j5u3Uq-y_Uzx_DXK_I2yfXq0RvgtJz_q-L6dWzU1oXbyrdZ0u6LpCzQTFbg1AL8KV5C8URMslry3mX7myWnySC5878AHTUw89U-WYeERn11nogGdtmz4b6gcQt1FRiKS1wBBIPqVkqB44PY5DlJSw6dAK1piTCqW1A==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLjLXVxfRtxHyBaIdsuvBriy3cKYbvZWWo5F-2J5Trnl58uoMRgQGFtV9AyvWvEECOSFekawKioYX7If9REijah8hyB7RD6l6v8a0TIEelWL3ILwhp4X5wSg==)
8. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOcxmbDUnZHSUjn3ZKuN0ZZPQ1EW8DKdWR2If5dc9malvyyQc2fMAXCMbj-GPR5Cz-kQE3QgXBJskjeCWuXoPs9Cd5SmHANGat_B2W7MaQRS0OjzrHRh1xaHhSTCSineUUzR45cl79GjgS2g==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBuNHMFnYtlX6QGrxDb4xSFnipc-rJD1ozcG8rzPMPJ6d-bNoJGKczDjnMp7SOZ4UEmCCZ2nwFC8cFsnQtkOSl4NEBeqdkaLuVtWs7DohEJttk2IjTugxN_g==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5HAn5dbP0nbY6QWZbn31locn9uZMDJoxH6NB4ms9GDDfPNDIUXGnpmzNM-Zwe4bjWRpLq6CeC0jbTDZq6omcfTXoGETqXk4Dpw2KtYuyNkk3tm6LCLw==)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEj7yt2B0ap3nmQkq4MxWD883lwOiEJJZFKKiHXR75rVt6koStc2HwU4BHxiKw-dYTmk3QkCrDwzQuS1NrqqF5hfTPvRYzKCsxNeg8vFW_PvbH2uECtBFdOihGlxEt1WA_RuqaqfshEqSx5zIW2mcRN-tvMS91-0rIPUXvuX5K4v8oYmmLIGrsDZbVDvyZyNlQbbKXuwoMnjhTuS-Ca7y_E6b5OPN6JM8dQUCjJsFQ=)
12. [combinatorics.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNThSbm8ludXCd4GvKfRPws17RV04MUXZcohtXb_xRXxXHg4WwZ4Ai_zoBBNrelifC6piiRl3q3J4WuNdS6uGz7YqwUV7HN42lPTpxN2IlqbgJ1hMeJfktqgdCosDcJCUV4WeSISs7xcw6JVwXdlnBfWjaIP-cimkv6eWlX84grN2QtWoB)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGC_QgVLImEvyurvUiZ46EvXu_1ccUaC99ASgZ7CqWhKg-nYhZ338PetjZV0i2XoJSiECs3qPbumKieMTvRsESRypTz9MO9slig97lMRZu4Z93mdP9Hg==)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHlDNLBeykduSlXQVA3eAV_kxgSdHQlK-6mn_M5ZixkvvB0c7eCFRwVjkcMgrlr1qYRgD7_q9fjHEGoe0WF_ifG8cTQ6YmSSjSIQb-cWcIQ2H3kmAEdZ7ZpjhlkSzpVs1EJ5hUgT_wuW7-3TN3k5pG-8lpr7LRQyL6OP_M-QewEdfF9T9o_GMI-w==)
15. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_7oF5E9D8H_dG3masqHsLL4PPgkonsEqZO359YGFAZSuqBgXKFJww1JSPvmq9OHNWRbKdQgCg1wK9k91Wi_lOygbjlhrl7pVBPVwJmFcDV930PzD3RXgnbNIWH_mQJYUK0nhB0hlOwsIjI7QtmAQYU_CnZh1LBA==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGlZbVksQN-qOokPbJMmE8MUJ1Qpl6txCwsznpakGcr7LN6w2rc7u3oBtw6UWsHUQ_Fbxwjpe9hMdzwtOT5GFGNRzHK-8rT5EU60q_DQRyuF_CkyIJELQ==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEahfN_hlVPVCqqOoiRVjfuNx5ykLHZyS_SNJ3MGGjkqjDaU6PdRd7zv9RVbyDjUJrgKFHqNscYhXVQHxeEAZGs5Yc0mL6DLdDo27mju6nBJR56TgIPUe-Q5Q==)
18. [umass.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRiuVSZG0Fc_YC7hmQFJ5JRRzDYO71gwzl1IAP3ZkEnGMLIqHpE4rfxPcx_NwT7SpHIrnYsc8B20HryHcHZvGwytF4P1-9T84KGXWbUXNHjwzFkn76c7v-2pcmnQ_ZX4j2CkW0sojp9lQzoW9hHvG6Kav7twqjExXZsjJIMZ3TgWHCoZ4ANwNtbf7NMxU=)
19. [aimspress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE45EWkc2yJLtsCw3VqQtx9k87B-Mi9YM10FOS3iE-AO9JQt0cIyri6KY8QjVgr4IdUgXZQfS6Z92Ien4gX6y5MfOYuUVOp7fFHQMfsncsLm4ET1vO-xggRXvZHkBVU1Drew6a-oYHF6OdUG3IaU0VhZqo0u_Eh_bfuc1ZNLl0=)
20. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUtebHt7QkRsyRn5vBojLzD-RygjAY4imPHcJBYoNWBeXs7ivhB63Qt-t5Z-zXit4MIBwD1Y1jrDdS3xU3nIRLbZJbq01csSKOGOVZgKzNe9J-9BdD3eB0N_qkmLXNajabbLUgN6y7u5XTI7jSw0Sc)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHl6EjAw6TyvLme6d7-BBoJWD_rhHipWpBf8N-lhGyuxOd0yKLj0XnEeTaPn1e30G-w2ed2man8MMBAs8Js7worelkYrmfIZqsamIpxuf51xbChXjbLdniLPvj6MDsOWrsR1-8sgRUXETxoFa_7mW8xD3tQB91FS7C6X9nVcn_I1T8Cq-guDZk-H20K2uGF7O0osuMC6gPaGc8Lv4M6W1nOb5g4n0xBgo6smydrBsLsIKfLV-TESKqDCPaxyFg5noIl)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECbV8IrpopXHvDTNzZdt9GDupjiLRJB3_X5bpkXNIUYV9nWtwwlJ5dyo52wHwFIDGJ1soQtdTchwsu_Px1o3y8F4MKfLqsPM1OoVCm22SCtPfX9olrVg==)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1UFNgz-N8iKcfVyijbpVglP9E-A5lzVgXi8GjbMUWECDl-4JNbBYjS8jxIpdS2LN4_ZzNwMCyUPbqvZRgy_OUJT4ycJKwa3h_czl64LUretVQJIhrXthFhRivq7-Hx8onB4GJZtw6pOGgSjvK8H9zJFKQt9-WgmWvHZmcUmpBfQDigrivxNwc4RSr9EJ9vTrd555p4U8huWMuapoa)
24. [combinatorics.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8gpX4ZPeOBFueEvmsOOEh_VVnLJgiJUF3SnnOcU3xzzCg6Gb1qHiRhyDmtknxMesXNlUPlCSPQzPLuWpg6xEMsNDmaWerY3_N_JlYfi7T2RA7_gOVLr1CJZtGstxNtzXRQstisATIRu8r6DUccUx2MLs3LVK3PgZ-DqTLsdWvWyZ2Xj8=)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExqJ6iNimc1GFsLk81EHZ8FkqWbfOrnb3IJ_cbn_NtaDdAdJlvk32_lJyB73uB5Lvn7tlT3_kXqFeTsUwFApvjBMQy4j2rZNheU8HXRJV6781sYInt7g==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQzV0xnxzJ25-TjCthWvyI3N1hM4tjSKwC6hol_eGgzHWTFbKBIERIZjnCP1ZJ4zzLzFgCkSWGWBlNRX7vxChXfxtgpbzt8KyGFcPqr-uZlk7OhmJcpA==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEm2Ya9AQ9Yousy7Sn2MEOVxNJ0JVoT_2gxej1t4pNeRKMljmpGb8Ywt_KR-OdmnJ_xADXi1IxsmkbSkvqz4ObDLfA2oDKUDEtVQ_Cg44VqInoN_xiNFQ==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRim-QMQBBX-92mP_ijT8VsIX3t5IqC18dt1hBrH4RndVWESyI5KoJ1U7k3rEllsywG0uG6_D26ETZBHJC_u7Pc6ivx1221hHXv3l1Jkti60QOcT5_xQ==)
29. [worldscientific.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFD2YxlDWp9xEy4TgZb2gOZUkWYTdiOMiMWqfwV3PhMVipIh0tBZ_LYs6WErQm9AX7qaW8kBx0VADjTd7_v2e-d5naonN1h78zAo6R0xv41Cd1A_R2ptPG8GUmOfol1HNafRc4H7cNQpFjMEkgkjmreeARH8-PXEw==)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH22JUYATbVg0neYCsTbEsZx29f-NpdAvqjUJcMNGPHO7BhyVV9nLoEeFOHnXnm7x46zCf61Ytd3ANHOEKYUzbAlonkqV8iULyicj-Qeu7pkcwgDGIuIw==)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJbkbl5NLbyzho5dbpoSwq9s5eg5r9gRvD2oZx6v8whWVJcHqg_sFZruhhhY9rQUoPLF3bmGlT0HhgtnjGUSE99FIanilMU8tT3GG-TgOKm2YrfuAp7Q==)
32. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJlaugbohEDSU6TXSPsAAJgUbDxuUhdJPWG0_kPcoO2ZpQ5C-Tanlitg-dd0qxP4L17c2GUM_XcShorGSYjVEjSGN7atCtMF3NxUZZcRUNpxBtv47miy7FN1hdSBLxVfGuHnxbEH31fH85l8ozjirpE5q4nhbTkTFmYWTriQTeqK5WPNSDD8bawD2o6395UXc=)
33. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbe5WQU1iJPmTeXz-zvEDxsWSrXGJm4OWJyBW4tOrRoSx2SHh13_7loYVY7SwaEgHDya2Y66ak1t2n3BITtb2BJGmtxhV-Xi837fvP5L3WI3Cxnapaa10z-x3fezIOEN9_QtVp_iPKmjTrCXhNj9BInA==)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5WR-E6LdPz9SupMrDqRkYrLr4rgTB7yJgpVp0pQfUFK9lihnL-b9SYwYB2WoL_VQbjk0nXhk9FgeeOlVcIiTu4_d-bKRAGXd_rS3Kkfak-ZnQTawHFA==)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKhH29TSSgiKGnx1Bg1_aCb7-8v-hHV03MsnGztXrQxmFjvkSky8GYkzT_E28rqpZ1d5Q5ThoK7ov4jq8Yfewqvi45UmY9mOncFbZVc1Zpnsj7OK7B6Q==)
36. [episciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEacegyOJN8_7LBwCsHPU9vhezA91Yeej-hhdCAqrCCraO8HaJoAmX1a3CivC_WLb1Q3Ri_9AdHH7gwsiC0fktiwGPZy7xmsiDyGbRiCRR2BuzAUwENOOt98yRXiQ==)
37. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG46EMU5d-C9tUbTBdGGy8t3fH9xT2d807mmncgvy5yQaUfLIHO6TYSPed3NIdrwiRJ997ftRkM8ywB5EkIfF3Wk_qtL9f4tPv9GlqdcD7OHDc4Xia4ENx1Mu3pE4ZrJfCkgi0=)
38. [univ-mlv.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdyZ_H0zjscLo08_LxpetgtWoFFR425mwaAzz-SgoIe3Gk_rwRJoC55YZfVB4q9MG8iCaZDnTjrX_ADuVmTGIVxbVRwzIVOJ2tSCzt1EgsPt2jDNN4nbholUX_NfZeO9rTBtDtvq1CdKgGnEDF)

