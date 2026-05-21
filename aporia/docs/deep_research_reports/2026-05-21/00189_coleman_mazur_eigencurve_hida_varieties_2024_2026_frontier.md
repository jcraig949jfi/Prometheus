# Coleman-Mazur eigencurve + Hida varieties 2024-2026 frontier

**Pythia queue id:** 189
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc0RDhQYW9yZk5lYVNfdU1QNGRPTHFBYxIXNEQ4UGFvcmZOZWFTX3VNUDRkT0xxQWM
**Elapsed:** 248s
**Completed at:** 2026-05-21T17:28:57.864541+00:00

---

# The 2024-2026 Frontier of the Coleman-Mazur Eigencurve and Hida Varieties: Advances in $p$-adic Langlands and Geometric Automorphic Forms

**Key Points:**
*   **Geometric properties of the eigencurve:** Research suggests that the local geometry of the $p$-adic eigencurve at $p$-irregular classical weight one cusp forms is highly complex, with recent 2025 breakthroughs mapping these intersections using $p$-adic transcendence theory and Gross-Stark regulators.
*   **Perfectoid spaces and higher dimensions:** The evidence leans toward perfectoid geometry providing the most natural framework for generalizing overconvergent modular forms, as seen in recent constructions of Hilbert modular forms via infinite-level Shimura varieties and the Hodge-Tate period map.
*   **$p$-adic Langlands functoriality:** It seems likely that the interpolation of functorial transfers, such as the symmetric square lift from $U(2)$ to $U(3)$, will become a standard tool in constructing new intersection points on higher-rank eigenvarieties.
*   **Weight map ramification:** The depth of congruences between eigenforms of equal weight appears deeply linked to the variation of $p$-adic adjoint $L$-functions and the ramification of weight maps over the eigenvariety.

The study of $p$-adic families of automorphic forms represents a cornerstone of modern number theory, linking the algebraic geometry of modular curves to the profound arithmetic of Galois representations and $L$-functions. Initially pioneered in the 1980s, the theory demonstrated that modular forms could be continuously deformed $p$-adically. Over the past few decades, this concept has evolved into the study of vast geometric spaces called eigenvarieties. These spaces organize infinite families of automorphic forms and serve as the testing ground for some of the most ambitious conjectures in mathematics, including the Birch and Swinnerton-Dyer conjecture and the geometric Langlands program. 

As we approach the 2024–2026 research frontier, the field is undergoing a paradigm shift. Mathematicians are moving beyond the classical, well-behaved regions of these geometric spaces to explore their most irregular and complex points. Simultaneously, new mathematical machinery—such as perfectoid spaces and derived algebra—is being deployed to extend these theories from classical modular forms to higher-dimensional unitary and symplectic groups. This report provides an exhaustive academic synthesis of these cutting-edge developments, detailing the structural properties of Hida varieties, the local geometry of the Coleman-Mazur eigencurve, and the ongoing integration of perfectoid geometry into the $p$-adic Langlands program.

## Theoretical Foundations: Hida Families and the Coleman-Mazur Eigencurve

To contextualize the frontier of 2024–2026, it is essential to rigorously define the foundational objects of the field: **Hida families** and the **Coleman-Mazur eigencurve**. 

### Ordinary Forms and Hida Theory

The theory of $p$-adic deformations of automorphic forms was initiated by Haruzo Hida in the 1980s, following his discovery of systematic congruences between the Fourier coefficients of modular forms [cite: 1]. Hida's foundational insight was that classical eigencuspforms that are **ordinary** at a prime $p$ (meaning the $p$-adic valuation of their $a_p$ Fourier coefficient is zero) can be interpolated into $p$-adic analytic families [cite: 2]. 

By taking the inverse limit of the ordinary parts of the cohomology of modular curves at $p$-power levels, Hida constructed the big ordinary Hecke algebra. A trivial case of Hida's theory provides a $p$-adic family, depending on continuous parameters, of abelian characters of the absolute Galois group [cite: 3]. More profoundly, Hida proved that the ordinary Hecke algebra is finite and flat over the Iwasawa algebra $\Lambda := \mathbb{Z}_p[[1 + p\mathbb{Z}_p]] \cong \mathbb{Z}_p[[X]]$ [cite: 4, 5]. This ring-theoretic result has a profound geometric consequence: the spectrum of the ordinary Hecke algebra yields a finite cover of the $p$-adic weight space, providing a rigid analytic space that parameterizes systems of Hecke eigenvalues for ordinary modular forms [cite: 5]. 

Hida's theory naturally maps to the portion of the eigenvariety exhibiting the most robust analytic behavior [cite: 3]. However, the restriction to ordinary forms—where the $U_p$ operator is invertible and acts with unit eigenvalues—omits a vast portion of the automorphic spectrum.

### Overconvergent Modular Forms and the Finite Slope Regime

The limitation of the ordinary condition was overcome approximately a decade later by Robert Coleman, acting on a suggestion by Barry Mazur [cite: 3]. Coleman expanded the interpolation to eigencuspforms of **finite slope**, where the $p$-adic valuation of the $a_p$ eigenvalue is bounded, but strictly greater than zero ($a_p \neq 0$) [cite: 2]. 

Coleman's theory relies on the geometry of modular curves and the concept of **overconvergent modular forms**. By considering the rigid analytic generic fiber of the modular curve, one can define regions of overconvergence beyond the ordinary locus. An overconvergent modular form is a section of an automorphic line bundle $\omega^{\otimes k}$ over a strict neighborhood of the ordinary locus in the $p$-adic modular curve [cite: 5]. The key mechanism allowing for interpolation is the compactness of the Hecke operator $U_p$ on these $p$-adic Banach spaces of overconvergent forms [cite: 6, 7].

Because $U_p$ is completely continuous, its spectral theory mirrors that of compact operators on Hilbert spaces, admitting a well-defined characteristic power series known as the Fredholm determinant [cite: 5]. Coleman's classicality theorem guarantees that any overconvergent modular $U_p$-eigenform of weight $k \geq 2$ and slope less than $k-1$ is, in fact, classical [cite: 5, 8]. 

### The Construction of the Coleman-Mazur Eigencurve

Building upon these Banach spaces and the spectral theory of $U_p$, Coleman and Mazur constructed the first global geometric parameter space for these finite-slope families: the **Coleman-Mazur eigencurve** [cite: 7, 9]. 

The eigencurve $\mathcal{C}$ is a rigid analytic curve equipped with a locally finite weight map to the $p$-adic weight space $\mathcal{W}$ [cite: 5]. The $\mathbb{C}_p$-points of this curve classify normalized overconvergent eigenforms that are not in the kernel of the $U_p$ operator [cite: 5]. Over this eigencurve, one can attach $p$-adic Galois representations and $p$-adic $L$-functions, effectively creating families of these arithmetic invariants that vary continuously with the weight [cite: 5]. 

Following this pioneering work, Buzzard introduced the "eigenvariety machine," an axiomatic construction that allowed the field to generalize the eigencurve to higher-dimensional reductive groups, leading to the broader study of **eigenvarieties** [cite: 9]. The generic fiber of the big ordinary Hecke algebra constructed by Hida corresponds precisely to the locus on the Coleman-Mazur eigencurve where the valuation of the $U_p$-eigenvalue is zero [cite: 10]. Consequently, any Hida family passing through an ordinary classical eigencuspform is natively a Coleman family, though the reverse is not necessarily true [cite: 2].

## The Local Geometry of the Eigencurve at Weight One Points (2024-2025 Frontier)

While the global structure of the eigencurve is well-understood, its local geometry at specific classical points remains a focal point of 2024-2026 research. For classical points of regular weight and small slope, the weight map is étale, and the eigencurve is smooth [cite: 8]. However, the geometry becomes intensely pathological at points corresponding to classical weight one modular forms.

### $p$-Irregular Points and the Failure of $R=T$

The study of the geometry of the eigencurve at classical weight one forms has seen immense progress in a definitive February 2025 paper by Betina, Maksoud, and Pozzi [cite: 1, 11]. Weight one forms are critically important because their associated Galois representations have finite image (Artin representations). 

A classical weight one eigenform $f$ is unramified at $p$, meaning the Hecke polynomial $X^2 - a_p X + \chi(p)$ has two roots, $\alpha$ and $\beta$. If these roots are distinct and the ratio is not $1$, the form is $p$-regular. If $\alpha = \beta$, the form is termed **$p$-irregular** [cite: 11, 12]. The local geometry of the eigencurve $\mathcal{C}$ at $p$-irregular classical weight one cusp forms presents severe difficulties because the traditional commutative algebra arguments—specifically the $R=T$ theorems identifying the universal deformation ring $R$ with the local Hecke algebra $T$—fail in these edge cases [cite: 11, 12].

Betina, Maksoud, and Pozzi provided a complete description of the local geometry of the $p$-adic eigencurve at these $p$-irregular points where the usual $R=T$ methods fall short [cite: 11, 12]. Their methodology required the definition of a "non-CM" deformation ring to parameterize deformations that explicitly do not arise from Complex Multiplication (CM) families [cite: 11, 12]. 

### Gorensteinness and $p$-adic Étale Cohomology

A profound consequence of the complex geometry at $p$-irregular points relates to the algebraic structure of the local rings and cohomology groups. In standard Taylor-Wiles patching arguments, a crucial requirement is that the local ring of the eigenvariety is Gorenstein, and that the associated Hecke modules arising from the étale cohomology of Shimura varieties are free [cite: 11]. 

The 2025 work examines the explicit failure of both properties. As a major application of their geometric description, Betina, Maksoud, and Pozzi demonstrated that the ordinary $p$-adic étale cohomology group attached to the tower of elliptic modular curves $X_1(Np^r)$ is **not free** over the Hecke algebra when localized at a $p$-irregular weight one point [cite: 11, 12, 13]. This represents a significant deviation from classical Hida theory (where Ohta's control theorems usually guarantee freeness) and poses new challenges for Euler system constructions [cite: 4, 11].

### Gross-Stark Regulators and Transcendence Theory

The exact shape and intersection multiplicities of the irreducible components of the eigencurve at these $p$-irregular points are heavily governed by $p$-adic $L$-values and regulators. The 2025 results are proven under the assumption that certain **Gross-Stark regulators** do not vanish [cite: 14]. 

This non-vanishing is consistent with broad conjectures in $p$-adic transcendental number theory, specifically related to the linear independence of $p$-adic logarithms of algebraic numbers [cite: 11]. By proving a generalization of Waldschmidt's bound for Leopoldt's defect, researchers have bounded Gross's defect and computed the "mysterious" cross-ratios of the $p$-ordinary filtrations of the Hida families containing the irregular form $f$ [cite: 14, 15]. Their structural theorem settles a conjecture of Darmon-Lauder-Rotger regarding the dimension of the generalized eigenspace, which is a critical technical prerequisite for formulating the Elliptic Stark Conjecture in the uncharted rank 2 setting [cite: 12].

## Perfectoid Shimura Varieties and Overconvergent Hilbert Modular Forms

To extend the theory of Coleman families beyond the classical modular group $GL(2)/\mathbb{Q}$ to general totally real fields (Hilbert modular forms), the field has increasingly adopted the machinery of **perfectoid spaces** [cite: 2, 9]. Perfectoid spaces, introduced by Peter Scholze, are a class of adic spaces built from perfectoid rings that allow for the translation of problems between characteristic $0$ and characteristic $p$ [cite: 9].

### The Infinite Level and the Hodge-Tate Period Map

In a series of recent papers (2023-2025), Birkbeck, Heuer, and Williams established a sweeping new construction of $p$-adic overconvergent Hilbert modular forms using Scholze's perfectoid Shimura varieties at infinite level [cite: 16, 17, 18]. 

Historically, overconvergent Hilbert modular forms were constructed using coherent cohomology and rigid analytic geometry by Andreatta, Iovita, and Pilloni [cite: 19]. The new perfectoid approach provides an analytic definition that closely resembles the classical definition of complex Hilbert modular forms as holomorphic functions satisfying transformation properties under congruence subgroups [cite: 16, 18]. 

For a totally real field $F$, one considers the Hilbert moduli space at infinite $p$-level, denoted $X_{\Gamma}(p^\infty)$, which is a perfectoid space [cite: 18]. This infinite-level space admits a **Hodge-Tate period map**, $\pi_{HT}$, mapping to the flag variety. The pullback of the automorphic line bundle $\omega$ along this projection can be canonically trivialized over open subspaces [cite: 18]. 

By restricting to an $\epsilon$-overconvergent anticanonical locus and taking sections, one obtains a highly natural definition of overconvergent Hilbert modular forms [cite: 18]. The authors successfully constructed sheaves of geometric Hilbert modular forms, as well as subsheaves of integral modular forms, and proved that their definitions vary continuously in $p$-adic weight families [cite: 16, 17]. Crucially, they demonstrated that the resulting spaces are isomorphic as Hecke modules to the earlier constructions by Andreatta, Iovita, and Pilloni, thereby unifying the perfectoid perspective with classical rigid analytic eigenvariety machine outputs [cite: 16].

## Ramification of Weight Maps and Adjoint $L$-Values

As eigenvarieties for Hilbert modular forms became better understood, the relationship between the geometry of the eigenvariety over its weight space and the arithmetic of $L$-functions emerged as a prominent 2024-2025 research vector. 

### The Bergdall-Hansen Middle-Degree Eigenvariety

Bergdall and Hansen constructed a middle-degree eigenvariety for Hilbert modular forms over a totally real field $F$. A July 2024 paper explicitly studied the **ramification locus** of this eigenvariety in relation to the $p$-adic properties of adjoint $L$-values [cite: 20, 21]. 

When a Hida family is finite and flat over the weight space, its local geometry near a classical form is typically isomorphic to the weight space. However, when the multiplicity of the weight fiber above a specific integer weight $k$ is greater than one, the weight parameter ramifies [cite: 20, 21]. The depth of the congruence between two $p$-ordinary cusp forms $f$ and $g$ lying on a common component in the same weight fiber corresponds geometrically to the proximity to this ramification point [cite: 21].

### Twisted Poincaré Pairings

To formalize this connection, the researchers introduced an analytic **twisted Poincaré pairing** over affinoid weights. This $p$-adic pairing interpolates the classical twisted Poincaré pairing for Hilbert modular forms [cite: 21, 22]. 

The classical pairing was already known to be related to the algebraic part of the adjoint $L$-value, $L^{alg}(1, f, Ad^0)$, through works by Ghate and Dimitrov [cite: 20, 21]. The 2024 strategy leverages the theory of $L$-ideals (previously used by Bellaïche and Kim for $F=\mathbb{Q}$) to connect the analytic pairings to the ramification of the weight map [cite: 20, 22]. This firmly establishes that the variation of the $p$-adic adjoint $L$-function over the Hilbert modular eigenvariety directly governs its geometric singularities and ramification behavior [cite: 20].

## Functoriality, Unitary Groups, and Rankin-Selberg Products

A major focus of the 2024–2026 frontier is the realization of Langlands functoriality within the $p$-adic realm. The eigenvariety provides a geometric mechanism to interpolate functorial transfers that are classically established only at discrete weights.

### Symmetric Square Functoriality and Level Raising on $U(3)$

An April 2025 paper explicitly investigates $p$-adic automorphic forms on definite unitary groups $U(3)/\mathbb{Q}$ [cite: 23]. While classical Langlands functoriality for symmetric squares from $GL(2)$ to $GL(3)$ is well established, establishing this map between eigenvarieties is significantly more complex.

The authors utilized $p$-adic Langlands functoriality to interpolate the symmetric square map from the eigenvariety of $U(2)$ to the eigenvariety of $U(3)$ [cite: 23]. Using David Hansen's method for $p$-adic symmetric square functoriality, the researchers generated non-classical points on the $U(3)$ eigenvariety [cite: 23]. 

Specifically, they proved exact level-raising results: if there is a non-very-Eisenstein point $\phi$ on the "old" component (parameterizing forms old at an inert prime $l$) satisfying the specific Hecke eigenvalue relation $T_l(\phi) = l(l^3 + 1)$, then this point must also lie in the "new" component [cite: 23]. This yields explicit intersection points between the old and new components of the $U(3)$ eigenvariety, serving as a $p$-adic analogue to classical level-raising results [cite: 23].

### Ordinary Distributions and Bessel Periods

In December 2024, researchers introduced a novel notion of **ordinary distributions** for unitary groups and their Rankin-Selberg products, providing a foundation to redefine ordinary eigenvarieties [cite: 24]. 

For both definite and indefinite unitary cases (parallel to root numbers $1$ and $-1$), the authors constructed the **Bessel period** on the Rankin-Selberg eigenvariety. They realized this period simultaneously as an ordinary distribution and as an element in the Selmer group of ordinary distributions [cite: 24]. 

This allowed the proposal of an Iwasawa-type Main Conjecture over the eigenvariety. The conjecture relates the vanishing divisor of the $p$-adic Bessel period to the characteristic divisor of the Selmer group of the associated Rankin-Selberg Galois module [cite: 24]. The authors successfully proved one side of this divisibility (upper bounding the Selmer group) under certain conditions, upgrading previous Iwasawa theory results to the full geometric level of the ordinary eigenvariety [cite: 24].

### Higher-Rank Shalika Families

Parallel progress is being made for general linear groups. Preprints in 2024 and 2025 by Barreras Salazar, Dimitrov, Graham, and Williams investigate the $GL(2n)$ eigenvariety [cite: 25]. They study **Shalika families**—families of automorphic representations characterized by the non-vanishing of Shalika periods—and their branching laws. The development of finite-slope Shalika families and the construction of $p$-adic $L$-functions for $GL(2n)$ over these families represents a significant expansion of the eigenvariety machine into higher-rank functional analytic settings [cite: 25].

## Infinite Slope and the Boundary of Weight Space

While Coleman and Hida families effectively parameterize finite slope eigenforms (where $U_p \neq 0$), a deeply challenging frontier is the study of **infinite slope** forms, where the eigenform lies in the kernel of the $U_p$ operator. 

### Limits and $p$-Supercuspidal Representations

The question of whether one can construct $p$-adic families of infinite slope was historically open. Diao and Liu answered a foundational question of Coleman and Mazur by proving that the eigencurve is "complete" (satisfying the valuative criterion for properness), meaning no eigensystems of infinite slope appear as a straightforward limit of finite slope eigensystems along the eigencurve itself [cite: 10].

However, one can construct sequences of finite slope eigenforms that converge to an infinite slope form by moving in a "transversal" direction [cite: 10]. Research delineates two types of infinite slope families:
1.  Twists of finite slope Hida or Coleman families by a Dirichlet character of $p$-power conductor [cite: 10].
2.  **$p$-supercuspidal** representations (or non-ordinary families with complex multiplication), which cannot be written as twists of finite slope forms [cite: 10]. 

### The Spectral Halo Conjecture and Ghost Series

To understand the slopes at the boundary of weight space, researchers rely on Coleman's **Spectral Halo Conjecture**. The conjecture posits that upon deleting a closed subdisc of weight space, the Coleman-Mazur eigencurve decomposes into an infinite disjoint union of finite flat covers over the remaining outer annuli [cite: 26]. 

These families over outer annuli are interpreted as $p$-adic families passing through overconvergent eigenforms in characteristic $p$ [cite: 26]. The exact values of the slopes in these extreme regions can be computed using "Buzzard's algorithm." Furthermore, the constant valuations observed in these halo-like regions are beautifully captured by the **ghost series**, a combinatorial power series whose Newton polygon models the $p$-adic Newton polygon of the characteristic power series of $U_p$ at the boundary [cite: 26].

## Overconvergent Cohomology and the Derived Langlands Program

The final major frontier of 2024–2026 involves viewing eigenvarieties through the lens of topological and derived algebra. 

### Definite Quaternion Algebras and Derived Hecke Algebras

For groups that are compact at infinity, such as definite quaternion algebras over $\mathbb{Q}$, the construction of eigenvarieties simplifies because automorphic forms can be viewed as functions on finite sets (or locally symmetric spaces of dimension zero) [cite: 6, 7]. Overconvergent automorphic forms in this setting are defined using locally analytic representations of the Iwahori subgroup [cite: 6].

In the broader context of the **geometric and derived Langlands programs**, classical Hecke algebras are being replaced by **derived Hecke algebras** [cite: 27]. Derived commutative algebra, which features prominently in the work of Bhatt, Morrow, and Scholze on integral $p$-adic Hodge theory, allows mathematicians to replace standard endomorphism rings with Ext-groups [cite: 27]. This derived approach is essential for understanding the moduli stack of local systems and provides a topological approximation of commutative rings, paving the way for a categorical $p$-adic Langlands correspondence [cite: 9, 27].

### Endoscopic L-Packets and Non-Gorenstein Points

The cohomological perspective also sheds light on the internal geometry of the eigenvariety. Recent generalizations of Bergdall and Hansen's work examine cuspidal cohomological automorphic representations of $GL(2)$ and the local geometry of the $SL(2)$ eigenvariety [cite: 8]. 

Researchers demonstrated that non-automorphic members of **endoscopic L-packets** of regular weight contribute eigenvectors to overconvergent cohomology at critically refined endoscopic points on the eigenvariety [cite: 8]. By proving that the $SL(2)$ eigenvariety is locally a quotient of the $GL(2)$ eigenvariety, they precisely quantified this contribution. A striking corollary of this geometric analysis is the proof that the $SL(2)$ eigenvariety often fails to be Gorenstein at these critically refined points, further emphasizing that non-Gorenstein singularities are a fundamental feature of the boundaries and functorial intersections of eigenvarieties [cite: 8].

---

## Data Summary: Key 2024-2025 Publications and Contributions

| Authors | Date/Source | Primary Subject | Key Geometric/Arithmetic Contribution |
| :--- | :--- | :--- | :--- |
| **Betina, Maksoud, Pozzi** | Feb 2025 [cite: 11] | Coleman-Mazur Eigencurve | Described local geometry at $p$-irregular weight one forms; proved failure of $R=T$ and non-freeness of $p$-adic étale cohomology of modular curves. |
| **Birkbeck, Heuer, Williams** | 2023-2025 [cite: 16, 18] | Hilbert Modular Forms | Constructed overconvergent forms via perfectoid Shimura varieties at infinite level using the Hodge-Tate period map. |
| **Bergdall, Hansen** | Jul 2024 [cite: 20, 21] | Hilbert Eigenvarieties | Linked the ramification of weight maps to $p$-adic adjoint $L$-values via analytic twisted Poincaré pairings. |
| **Anonymous/Preprint** | Dec 2024 [cite: 24] | Unitary Groups | Constructed Bessel periods as ordinary distributions; proved one side of the Iwasawa Main Conjecture for Rankin-Selberg products on eigenvarieties. |
| **Anonymous/Preprint** | Apr 2025 [cite: 23] | Unitary Groups ($U(3)$) | Proved exact level-raising results and interpolated symmetric square functoriality from $U(2)$ to construct new intersection points on the $U(3)$ eigenvariety. |
| **Loeffler, Rockwood, Zerbes** | Jun 2025 [cite: 4] | Hilbert Modular Varieties | Established exact control theorems for the ordinary part of middle-degree étale cohomology in the sense of Hida theory. |
| **Newton** | Nov 2024 [cite: 6, 7] | Overconvergent Cohomology | Synthesized the construction of eigenvarieties via definite quaternion algebras and locally analytic representations for the Heidelberg Spring School. |
| **Barreras Salazar et al.** | 2024-2025 [cite: 25] | $GL(2n)$ Eigenvarieties | Explored branching laws and $p$-adic $L$-functions for finite-slope Shalika families. |

---

## Conclusion

The 2024–2026 frontier of Hida varieties and the Coleman-Mazur eigencurve represents a period of explosive synthesis in arithmetic geometry. The field is moving decisively past the smooth, étale, and ordinary regions that defined the late 20th century. By interrogating $p$-irregular points, endoscopic boundaries, and infinite slope regimes, mathematicians are uncovering deep pathologies—such as the failure of Gorensteinness and the breakdown of classical $R=T$ theorems—that are intimately linked to $p$-adic transcendence theory and Gross-Stark regulators.

Simultaneously, the foundational language of the field is being rewritten. Perfectoid geometry and derived Hecke algebras are replacing classical rigid analytic parameter spaces, allowing for the natural construction of overconvergent forms for general totally real fields and higher-rank unitary groups. As $p$-adic Langlands functoriality becomes operationalized, eigenvarieties are no longer seen as isolated geometric objects, but as an interconnected web of spaces bridging $GL(2)$, $SL(2)$, $U(2)$, $U(3)$, and beyond. This profound geometric unity promises to be the bedrock for the next generation of proofs surrounding the Birch and Swinnerton-Dyer conjecture and the categorical Langlands program.

**Sources:**
1. [ku.dk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6egGNldrLh2A9iTVyGaD22HuRiWhBDL9pTw7U7989KrkcbBKVOz6YljkP6-r8WxiIH8qPPc8CzOJnfkmxX6Gz6xUk5sfIA21ESGBL-BlOsNhraE8zOPd4ncfLKcDgGnr8ndAwi_IHgkCobEdxjLRg)
2. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBbRcLuK_rCWDxq3OYjcE1guHHmVOpDhvqB9HOFD5iDUjIc-6zahaNiCSXZGNfT9NiaVt7cIebz5bbpofIoU1X-W6GnJdOcAwlGDGCKXTukob09fix4ILk4ZTNabiBeR_5Rh3fFty1JSBxvw_fxJ7EGp6X7c5MfuzBJhmeS5bEawrGVqOmsDDjf3b9E9cTDUcVgIpQ2nkHYA==)
3. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEbQ8iQlhtLQt-59yDKsuYmdmI7ze4Go0nSpPK8aPmosPodvYJruOwQNYIqjYJmwmGu2TaR6Q-xLZP5aQfj8DADIevBRdkwvtGgU7uMDHvoQMZfkE4bXMTUFXURjwhU7K672hrf7wK53UH8A19toekSa4ARHr5CsHuQdG4-BdF7nQNePFWcX0=)
4. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfQqPqlUlyAeZHkIQrOjxn6uES-Kf-OK5sQYi_wmYOG2PkJcemOvhyqwNDa0Btth2OU-Ago1VUtItdhTAn1OcBkvD9MFM0szvs93slg6DS7IiM6xqg68XLvrGoGFpVPW3LQa5Zb1nrrSJeEr7mmFxuAJSr1N3n3pBfqigKj5tiQj8YhfILViPWiQ6Q8VTV3t89dmHw6KWv0X6hvV2tlxHeQo7hoSd7ViAxic-C5AWgEE4miF4Cj1V1Hh1gW-aQF838if2UAkiz15__0vNmHOOzvSjvvKE=)
5. [uni-due.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGs-zGJzwBdJLHNTItoehuwJuVfTZHf4M-PS4W5PhlzogYy1N1PUK78lWZ51LEGdWqGBX31ZRHI1P8TFViX1vtzQ3JXsfXv5RPMfrWVF6qXpSh7Xlm9rjDeAGC9y2vNl8p3NwnTlJuEYo52BNYRt_XcRGKtG0vkheb52_Rv95BKoqRZbByxbqqxo7zFHa3RdZUvqrHbCcyfxDPORRtVkD3_)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5IlhjI6Vuc8gpKaUpwsZ6nc_ZXq4hKmBf5JJRlOAwz1fccN0imJObaOHZUyrn2renybzVoxtXUgPdNgB2jcxzicchbwCOUOpdCjoEGIghZWdxA141JZWb-w==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmwAr_zzEOiDNKqpMq7grAby8fcvyIgJ6E2b0_ZJryWlolGMt4XYnhvhmaS3-V25n0j9FzrtVlrvjc6IZ9rXbm0us7XFWE0PhFjprIPCAKpMNzohDOfA==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDXbd6o7cfUDJVHyr9dnxJ7_RHj8KSmOxq8DYHv4QlsJssiHbIR-hHd5AjOIbc-V_5Z4CRtYQVIKICtsRrHR7hjB3BnJXOdjObBSAn6IaqiY-hSrAzuQ==)
9. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9rxyXqixS91LuPWcqj2jYnFLAU3DnAdoyrLKFlCNbu_TzxQm45Anjdn_yeFgpvA9vA1pG7Awlh-_gvkyPoU5A1IEJPP12CwloEnAV7xFqik-bYdTw9LGiW7fsJUf3NXFD3_kNIKWKzQ==)
10. [uni.lu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiWGTe1ZSvUmEKv82yEliZMnjtr6jcAP5YtohNwPVQ-4w5Bv_DloDAnPw9dN3sUY33m3wVemkM2xJsZ-NXxhzU4-5UFV9ropLE0OghiGn85PlbPfvEJeI_OVCcxTiVAd3jzhOMpXX0mp4jdYjUqJ5o1ZwsLRThVBC-Kg==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNWbbRKwVhO2EjG4xhhT4nVlBAtqRM8q9YHbSBabiZfAl3YQ0ppx0jiJ8A0SZ4lvGZsnCVtuY1bgpPE_I2k1vDmH3nQOz09NNWhMKRUjBRn5HN7jlgqw==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE59ujI_vx_h_QX-Lf5suU78CFCS6OfQX8vmfwCYYJEqPUfYHrLFXucyeitcE3kPPkVwkAEKIx8WAdECa8sRGUedFOUzH95Mrk9_Hsb60kWpDjBeJRPRdlhbw==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtqZsATP-JLACcOTyss8jXwnsUOiCDXaFhT3bXa_2x85A1sn_ntNxXLiR-lPYk6A24Hu0LR01UZSfVi0bCuJL2b4Cy7ntUU-wE5E4w3IIQWstRxD9PLg==)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaS9FTjkDIMaF0pjIpH_eynJvN0NllmXaJkaEQIUqFQnNtxCJycLTn60zRtq8OTCfrCqmwQSNEiB7XUpNgmZJBrW4myj4YNbJSoNVkne2saGDum0PRoKxrWh2yfkylQvKSWQqJorKtHx7gHh5VSE7qFTVb1XhlAsle--55Zmt8dtVb)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8Qde6Vb6G-IDFvlq9HLEvphjg5hLDKyl91jHbmxBDJCfMEs3dcwNef_PmhV-1o2Cgmlt14LAkOj9s0CIUf2LMkxzhWgwjTSnh4YzZs71WlObHlfxcmlGwxI7skdSQkx_lgoUPtFexg-y-BgNf9U7g_hxM728tUyZP9YPdAB09S_-VwgCb_1qK)
16. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMFDDWdni_9Zd8mA44jbRCuhS1_SfdYnDU68SKFY2KkflJkK51PwTBtUtzp7I30JIyIzjJ3u7vL-wiDmigpgxfjK1qcIRcFfx2wyuk_i4gtjIaM6JCZKNWdqRwCYGzNfKNw-UHb4kjLw84L-fd6OZe)
17. [uea.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2BdEquZSy3N4YiRBe0wH5_UXNQK6HyLqPGYypkZnRFVkKVexEXE1YzD1DUrAX0oSzEeXXzr7ZTW20ff6nnm8jv3sEod-ML4huDOG2lhGGTST_PFPscNy_ri2puVqarwm7IXwrkm6Cs1tRqRdFNchjWtbb341a-Tm9qvxqltpAsPD66LgczhDL3HmevEJh7pbIwud1Iki9W0o5TgiLuqi_Ds49LuQ0HnllaSfL)
18. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElVOwbEVrv1wmc9JY0l81APWQFsqOh4BRShlGZI2F5SkYei-XexmCxTTMzR2lO2PP4m1jmbguY9j_dqMEImZeYEsr_sh0bN6-u0FwAoaRFGfZ2-DXgBkgtvVz26rGHB5KoCe7OdHg=)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7onWyONEaOxVUgHDzG0n1r06yWk9sj9psjzF1uHtNjmSHpkwIyf5OOoloTzH-CS1d1qi2madK6e51sySZ4piJa2Tx5kSSYsOCETCfkCcFyyk20z_0XohWHStSfA4osHeGxylreFHLw0qNF4RFFAOkk-RC3uG5ONaheKtsgJ10CaijIjod)
20. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3B-ELMpKO8PosYz1-_Ua73uTjE-KPfksl4G21ahCUNM9AuyWB7V3cHcdfQLHC_E8hUM8MhDdyNojj566qMXa5RzHa_xAkcxP4InZKzAWE-8l6EIUVk3ZACAR8e2jq08bdMn9QBD4TdpdqO-SKCRF7I809uVVmse4a_fTFxIOYXR5u)
21. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMxMuwkQzcyBpT3wMKQUAl9RawR2rqBe8frW5_8wsJALFw9yMRxZf9aipKuT7tAx3qgz0e9XZtMAXnaNmZaPNZF7FqRGc0KOe3sUnq8F8satyzVForVhA1KQbR_LLrTepz_epv53AILGB7Fs2b03nBu7P3MK10G2qwqihdnRDxdanr)
22. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWG86PtQSpnfD_MMftXMXMg0dvGY8ELcQrGIyeyjgUz9rXpvJ9ekrT5c0C1PQK6xEySWB-H1RG0GvTzGCCv6SAhGbJau9n4Ot_xWyLiiMAr7gIxxug4sYFaEJAdLc5gwV-dN0yUDg=)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF48OcZ1uMXAiiiuqogRUEyxQMYrHsN089wyHz9qz6d_R1lwePzdIEJZw7Y0YzvC69Si0U6ocqscj4AOguR_UDOLMmVJnf4Fh2v-RB3MxeWPWzCadT6Pg==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzcLQxGnYSoeTli5PalpbpU0-W2dP5v_jRFGD8I3N8-U_vltZqZGYYJZuLPIpoxm8IjSYg93u62qxhzKN0uVvBR_J0C81o4IrfMGS0CbtMy4bUPIwxxw==)
25. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEX7PguizAEj7mMaTb_JsTUCubmSih7qm9GA8IfHG4rInh1fGt3f21DUs-NL7jcwB2AVpnHuZ_vjJSzQCzy9fCN1uQDhiHPYCIM_G1CCV56pXUJXz4gBRKJ_iosTXSDNu1gFoyMI4pjDOOR5uoR)
26. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHau8L3hfiIYgvXCeiseuJ7WEVt0-SrMJRmDiXY_bHxXiKl-pf104FBXcMHnvSNQgP5keALEGDDN_i_qR94Z7_dPf9pgxNs-y0azVbSzOFKdUnzdQzE0e_lnDGgseZLBJ-R06FybR5ena_jD-UFRW0=)
27. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyENj0wbwRtgibJh5HuFzzu_nrpOfVd-Z_5iBlQVA5q03m8FiiZPT2ioBkEkthsSaGnJvfdIOL420A45ZYTc3VksLz0y_u5HX6Axqar0_ebSa8sBnPE906i-iRbbopRSY-2l3xPdg=)

