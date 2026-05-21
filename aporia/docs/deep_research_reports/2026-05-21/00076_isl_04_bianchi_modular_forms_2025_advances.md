# ISL-04: Bianchi modular forms 2025 advances

**Pythia queue id:** 76
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdMLTRPYXRYQ0JhNk5fUFVQay1ia2dRVRIXTC00T2F0WENCYTZOX1BVUGstYmtnUVU
**Elapsed:** 253s
**Completed at:** 2026-05-21T11:40:28.801365+00:00

---

# Advances in Bianchi Modular Forms (2024–2026): Modularity Lifting, Computations, and Paramodularity

*   **Significant Breakthroughs in Modularity Lifting:** Recent years have seen the resolution of long-standing conjectures in the Langlands program over imaginary quadratic fields. Groundbreaking work has established the modularity of elliptic curves over infinitely many imaginary quadratic fields and successfully proved the Ramanujan and Sato-Tate conjectures for Bianchi modular forms of weight at least 2.
*   **Computational Frontiers Expanded:** The computation of Bianchi modular forms—historically restricted to Euclidean imaginary quadratic fields or those with class numbers up to 3—has now been extended to fields with arbitrary class groups. Implementations in C++ and Magma have significantly expanded the L-functions and Modular Forms Database (LMFDB), providing explicit Hecke eigensystems and dimensions for deeper levels.
*   **Paramodular Connections:** The theta lift connecting Bianchi modular forms to Siegel modular forms of genus 2 continues to be a crucial tool for investigating the Brumer-Kramer Paramodular Conjecture. Recent advances also explore the explicit Eichler-Shimura-Harder isomorphism, establishing rationality theorems for Bianchi period polynomials. 
*   **Methodological Innovations:** Modern proofs circumvent the historical lack of algebraic geometry associated with locally symmetric spaces over complex places by employing $p$-adic local-global compatibility, derived Hecke algebras, and potential automorphy of symmetric powers of Galois representations.

### What are Bianchi Modular Forms?
To understand the recent leaps in number theory, one must look at the generalization of classical modular forms. Classical modular forms are highly symmetric complex functions defined on the upper half-plane, transforming under groups like $SL_2(\mathbb{Z})$. Bianchi modular forms generalize this concept from the rational numbers to imaginary quadratic fields—number systems constructed by adjoining the square root of a negative integer to the rational numbers (e.g., $\mathbb{Q}(\sqrt{-17})$). Instead of the two-dimensional hyperbolic plane, Bianchi modular forms are defined on the three-dimensional hyperbolic space, transforming under Bianchi groups like $SL_2(\mathcal{O}_K)$, where $\mathcal{O}_K$ is the ring of integers of the imaginary quadratic field.

### Why Do They Matter?
Bianchi modular forms are a vital testing ground for the Langlands program, a massive web of conjectures connecting number theory, algebra, and geometry. For classical modular forms over rational numbers, mathematicians have a powerful toolkit because the spaces they live on correspond to algebraic curves (Shimura varieties). However, for imaginary quadratic fields, this geometric connection vanishes. Thus, proving that mathematical objects like elliptic curves are "modular" over imaginary quadratic fields requires entirely new, highly sophisticated techniques. 

### The 2024–2026 Milestones
Between 2024 and 2026, researchers made historic progress in this arena. Mathematicians established that elliptic curves over many imaginary quadratic fields correspond to Bianchi modular forms, solving complex cases of modularity lifting. Simultaneously, computational number theorists developed novel algorithms to actually calculate these forms over fields with complex class groups, publishing vast new tables of data. Furthermore, deep connections were explored between Bianchi forms and "paramodular" forms (a type of higher-dimensional modular form), offering new ways to study the arithmetic of abelian surfaces.

***

## 1. Introduction and Theoretical Foundations

### 1.1 The Geometric and Adelic Setup
Bianchi modular forms are automorphic forms associated with the general linear group $GL_2$ over an imaginary quadratic field $K = \mathbb{Q}(\sqrt{-d})$ where $d > 0$ is a square-free integer. Let $\mathcal{O}_K$ denote the ring of integers of $K$. Unlike classical modular forms that reside on the hyperbolic plane $\mathbb{H}^2$ and transform under congruence subgroups of $SL_2(\mathbb{Z})$, Bianchi modular forms are defined over the three-dimensional hyperbolic space $\mathbb{H}^3$, transforming under finite-index congruence subgroups of the Bianchi group $GL_2(\mathcal{O}_K)$ [cite: 1, 2].

Hyperbolic 3-space can be modelled as $\mathbb{H}^3 \simeq \mathbb{C} \times \mathbb{R}_{>0} \subset \mathbb{H}$, where $\mathbb{H}$ is the ring of quaternions. The space is equipped with the metric $ds = |dz|/ \operatorname{Im} z$, analogous to the classical hyperbolic metric [cite: 3]. The group $PGL_2(\mathbb{C})$ acts on $\mathbb{H}^3$ via orientation-preserving hyperbolic isometries (Möbius transformations extended to the upper half-space). 

Adelically, let $\mathbb{A}_K$ be the adele ring of $K$, which decomposes into $\mathbb{A}_K = \mathbb{C} \times \mathbb{A}_{K,f}$, where $\mathbb{A}_{K,f} = K \otimes_{\mathbb{Z}} \widehat{\mathbb{Z}}$ represents the finite adeles [cite: 4]. The space of Bianchi modular forms arises from the automorphic representations of $GL_2(\mathbb{A}_K)$. For an integral ideal $\mathfrak{n} \subset \mathcal{O}_K$, one defines the compact open subgroup $U_0(\mathfrak{n}) \subset GL_2(\widehat{\mathcal{O}}_K)$ consisting of matrices that are upper-triangular modulo $\mathfrak{n}$ [cite: 4, 5]. The adelic quotient space is given by:
\[ Y_0(\mathfrak{n}) = GL_2(K) \backslash GL_2(\mathbb{A}_K) / K_\infty U_0(\mathfrak{n}) \]
where $K_\infty = \mathbb{C}^\times \times SU(2)$ is the maximal compact subgroup of $GL_2(\mathbb{C})$ modulo its center [cite: 4].

### 1.2 Weight and Cohomology
A cuspidal Bianchi modular form $F$ of weight $(k,k)$ and level $\Gamma_0(\mathfrak{n})$ is a vector-valued function $F: \mathbb{H}^3 \to V_{2k+2}(\mathbb{C})$ satisfying specific transformation and growth properties [cite: 1, 6]. Specifically:
1. $F|\gamma = F$ for all $\gamma \in \Gamma_0(\mathfrak{n})$.
2. $F$ is an eigenfunction of the appropriate Casimir operators (annihilated by specific differential operators $\Psi F = 0$ and $\Psi' F = 0$).
3. $F$ vanishes at the cusps of $\Gamma_0(\mathfrak{n})$.
4. The integral $\int_{\mathbb{C}/\mathcal{O}_K} F|\gamma (z,t) dz = 0$ for every $\gamma \in \Gamma_0(\mathfrak{n})$ [cite: 6].

Because the symmetric space $\mathbb{H}^3$ is three-dimensional, Bianchi modular forms of parallel weight $k \ge 2$ do not possess the simple holomorphic Fourier expansions seen in classical modular forms. Instead, they are deeply connected to the cohomology of arithmetic groups. By the Eichler-Shimura-Harder isomorphism, there is a natural identification between the space of cuspidal Bianchi modular forms $S_{k,k}(\Gamma)$ and the cuspidal cohomology group $H^1_{\text{cusp}}(Y_\Gamma, V_{k,k})$, where $V_{k,k}$ is the corresponding local system of symmetric tensors [cite: 6, 7]. This cohomological interpretation is central to both the algebraic study of their periods and the computational algorithms used to tabulate them [cite: 1, 6].

## 2. Breakthroughs in Modularity Lifting and Potential Automorphy (2024–2026)

One of the most persistent obstacles in the Langlands program has been extending the Taylor-Wiles method of modularity lifting to number fields with complex places, such as imaginary quadratic fields. For totally real fields, the associated locally symmetric spaces (Shimura varieties) possess algebraic structures, allowing mathematicians to associate Galois representations to automorphic forms via étale cohomology. For imaginary quadratic fields, the space $Y_0(\mathfrak{n})$ is a hyperbolic 3-manifold (or a disjoint union thereof) which lacks algebraic structure [cite: 7, 8]. 

### 2.1 The Caraiani-Newton Modularity Theorems
In a monumental breakthrough published and expanded upon up to 2025, Ana Caraiani and James Newton established the modularity of elliptic curves over infinitely many imaginary quadratic fields [cite: 9, 10]. The long-standing problem was that while Wiles' proof of Fermat's Last Theorem successfully established modularity over $\mathbb{Q}$, and subsequent generalizations handled real quadratic fields, imaginary quadratic fields remained elusive due to the lack of classical algebraic geometry [cite: 11].

Caraiani and Newton proved that if $F$ is an imaginary quadratic field such that the modular curve $X_0(15)$ (which is an elliptic curve of rank 0 over $\mathbb{Q}$) also has rank 0 over $F$, then *all* elliptic curves over $F$ are modular [cite: 10, 12]. This includes fields such as $\mathbb{Q}(\sqrt{-1}), \mathbb{Q}(\sqrt{-2}), \mathbb{Q}(\sqrt{-3}),$ and $\mathbb{Q}(\sqrt{-5})$ [cite: 10, 12]. 

**Local-Global Compatibility:**
The central technical innovation enabling this theorem is a new local-global compatibility theorem for $p$-adic Galois representations associated to torsion classes in the cohomology of locally symmetric spaces [cite: 10]. Working in the crystalline case, Caraiani and Newton allowed for arbitrary dimension, arbitrarily large regular Hodge-Tate weights, and situations where $p$ is small and highly ramified in the imaginary CM field [cite: 10]. 

The overall strategy utilized a "3-5 switching" argument [cite: 13]. By analyzing the representations of the absolute Galois group $\text{Gal}(\overline{F}/F)$ on the torsion points $E[cite: 2]$ and $E[cite: 14]$, they leveraged the Calegari-Geraghty method, which extends modularity lifting to environments where the cohomology occurs in multiple degrees (as is the case for hyperbolic 3-manifolds) [cite: 9, 13, 15]. If the $\text{mod } 5$ representation is irreducible, they invoke 3-5 switching to prove modularity, successfully avoiding previous limitations and pushing the boundary of the Langlands reciprocity conjecture [cite: 9, 13].

### 2.2 The Ramanujan and Sato-Tate Conjectures for Bianchi Modular Forms
In parallel with the modularity of elliptic curves, massive progress was made regarding the automorphic representations themselves. The Ramanujan and Sato-Tate conjectures describe the statistical distribution and strict bounds of the Hecke eigenvalues (or equivalently, the Fourier coefficients) of modular forms. 

In a landmark 2025 publication in *Forum of Mathematics, Pi*, Boxer, Calegari, Gee, Newton, and Thorne proved the Ramanujan and Sato-Tate conjectures for all regular algebraic cuspidal automorphic representations of $GL_2(\mathbb{A}_F)$ of parallel weight, where $F$ is an arbitrary CM field (which includes all imaginary quadratic fields) [cite: 7, 15]. Thus, these conjectures are now unconditionally proven for Bianchi modular forms of weight at least 2 [cite: 7, 16].

**Methodology: Potential Automorphy of Symmetric Powers:**
The proof of the Sato-Tate conjecture for an elliptic curve (or a modular form) heavily relies on showing that the symmetric powers of its associated Galois representations, $\operatorname{Sym}^{n-1} \rho$, are automorphic [cite: 7, 17]. In the case of Bianchi modular forms, Boxer et al. bypassed the lack of direct geometric structures by utilizing potential automorphy theorems over CM fields [cite: 7]. 

An intriguing feature of their proof is that they establish deformation rings for arbitrary $n$-dimensional mod $p$ representations by cleverly reducing calculations to reducible 2-dimensional representations [cite: 7]. By demonstrating that the compatible system of symmetric powers is potentially automorphic—meaning it becomes automorphic after a finite extension of the base field—they could strictly bound the Hecke eigenvalues. For an inert prime $p$, the magnitude of the Hecke eigenvalue is strictly governed by $2 \cdot p^{(k-1)/2}$, bounding the local factors precisely as Ramanujan predicted [cite: 17]. This resolves decades of speculation regarding the spectral properties of Bianchi forms of higher weight, where congruences between forms of different weights are notoriously sparse [cite: 18, 19].

## 3. Paramodular Forms and Theta Lifts

While Bianchi modular forms characterize the arithmetic of imaginary quadratic fields, their interaction with higher-dimensional symplectic groups provides a mechanism to study abelian surfaces over $\mathbb{Q}$. This is largely mediated by the Brumer-Kramer Paramodular Conjecture and the theory of theta lifts.

### 3.1 The Brumer-Kramer Paramodular Conjecture
The Paramodular Conjecture, formulated by Brumer and Kramer, acts as the genus-2 analogue of the Shimura-Taniyama-Weil modularity theorem for elliptic curves. It posits a one-to-one correspondence between isogeny classes of abelian surfaces $A/\mathbb{Q}$ of conductor $N$ with trivial endomorphism ring ($\operatorname{End}_\mathbb{Q}(A) = \mathbb{Z}$) and weight-2 paramodular Siegel newforms of level $N$ with rational Hecke eigenvalues that are not Gritsenko lifts [cite: 20, 21, 22].

A Siegel modular form of degree 2, weight $(k,2)$, and paramodular level $N$ is a holomorphic function $F: \mathbb{H}_2 \to V_{(k,2)}$ on the Siegel upper half-space that is invariant under the paramodular group $K(N) \subset Sp_4(\mathbb{Q})$, defined as the stabilizer of the lattice $\mathbb{Z} \oplus \mathbb{Z} \oplus \mathbb{Z} \oplus N\mathbb{Z}$ [cite: 4, 23]. The paramodular Fricke involution splits these spaces into plus and minus eigenspaces, yielding highly intricate Hecke modules [cite: 23]. 

### 3.2 Theta Lifts from Bianchi Modular Forms
To provide concrete evidence for the paramodular conjecture, one must construct non-trivial paramodular forms and map them to abelian surfaces. A highly successful technique is the theta correspondence between the orthogonal group $O(3,1)$ (which is isogenous to $PGL_2(\mathbb{C})$, the ambient group for Bianchi forms) and the symplectic group $GSp(4)$ [cite: 4, 24].

Berger, Dembélé, Pacetti, and Şengün explicitly adapted the Johnson-Leung-Roberts theta lift from Hilbert modular forms to the context of Bianchi modular forms over imaginary quadratic fields [cite: 20, 25]. If $E/K$ is a modular elliptic curve over an imaginary quadratic field $K$ that is *not* a $\mathbb{Q}$-curve (meaning it is not isogenous to its Galois conjugates), its Weil restriction $\operatorname{Res}_{K/\mathbb{Q}}(E)$ forms an abelian surface $B_E$ over $\mathbb{Q}$ with $\operatorname{End}_\mathbb{Q}(B_E) = \mathbb{Z}$ [cite: 4, 20].

The modularity of $E/K$ corresponds to a Bianchi modular form $f$. Berger et al. demonstrated that if $f$ is not a base-change form (which is guaranteed since $E$ is not a $\mathbb{Q}$-curve), the theta lift of $f$ to $GSp_4(\mathbb{Q})$ yields a genuine paramodular Siegel cusp form $g$ of genus 2 and weight 2 [cite: 4, 20]. Crucially, the $L$-functions match exactly: $L(B_E, s) = L(f, s)L(f^\tau, s) = L(g, s)$, providing explicit, computationally verified instances of the Paramodular Conjecture originating from imaginary quadratic fields [cite: 4]. 

### 3.3 Theoretical Complications: Fake Abelian Surfaces
While the paramodular conjecture aims for a bijection, the direction from paramodular forms to abelian surfaces contains theoretical pitfalls comparable to those seen in Bianchi modular forms. For Bianchi modular forms of weight 2 with rational eigenvalues, one expects an associated elliptic curve. However, there exist genuine Bianchi newforms with rational eigenvalues that instead correspond to abelian surfaces with quaternionic multiplication (QM abelian surfaces) [cite: 26].

Similarly, in the paramodular setting, there exist "fake abelian surfaces." A fake abelian surface can be constructed by taking a fake elliptic curve over an imaginary quadratic field and applying the Weil restriction of scalars [cite: 21]. The resulting abelian surface over $\mathbb{Q}$ maps to a paramodular Siegel newform with rational eigenvalues. This demonstrates that the strict bijection proposed by Brumer and Kramer requires careful topological and algebraic geometric amendments to account for these quaternionic anomalies [cite: 21, 26].

## 4. Computational Advances and the LMFDB (2024–2026)

While the algebraic theory of Bianchi modular forms advanced rapidly, the practical computation of these forms—finding their dimensions, Hecke eigenvalues, and explicit matrix representations—achieved equally impressive milestones. Computations of Bianchi modular forms were pioneered in the 1980s by Grunewald, Mennicke, and Cremona, but these were largely limited to the five Euclidean imaginary quadratic fields ($\mathbb{Q}(\sqrt{-d})$ for $d=1,2,3,7,11$) and class number 1 or 2 fields [cite: 1, 27, 28].

### 4.1 Algorithms for Arbitrary Class Groups
In groundbreaking computational work published in 2025/2026, Cremona, Thalagoda, and Yasaki successfully extended the computation of Bianchi modular forms to imaginary quadratic fields with *arbitrary class groups* [cite: 1, 5, 29]. 

Their algorithm sidesteps the algebraic geometric limitations of $\mathbb{H}^3$ by computing the rational homology $H_1(\mathbb{H}^3 / \Gamma_0(\mathfrak{n}), \mathbb{Q})$ [cite: 1]. The methodology is broken down into a rigid pipeline:
1. **Tessellation Data Precomputation:** The group $GL_2(\mathcal{O}_K)$ acts on $\mathbb{H}^3$, and a fundamental domain is constructed using Voronoi tessellations of Hermitian forms. Yasaki and Gunnells' algorithms are employed to compute the boundaries, 3-cells, 2-cells, 1-cells, and 0-cells of this tessellation [cite: 1, 2].
2. **Class Group Decomposition:** For fields with class number $h_K > 1$, the overall problem is decomposed into a "sum" of class number 1 problems. The algorithm identifies representative ideals $\alpha_1, \dots, \alpha_{h_K}$ for the class group $Cl(K)$ and translates the fundamental domains over these coset representatives [cite: 2].
3. **Homological Eigensystems:** The homology $H_1(\Gamma_0(\mathfrak{n}) \backslash \mathbb{H}^3, \mathbb{Q})$ is explicitly computed as a vector space. Hecke operators $T_p$ (and $T_{\mathfrak{p}}$) act on this space. By diagonalizing the Hecke action, one obtains "homological eigensystems" [cite: 1, 27].
4. **Full Hecke Eigensystems:** Using the homological eigensystems, one can recover the full algebraic Hecke eigensystem, tracking the exact field of definition (the Hecke field) for the eigenvalues [cite: 1].

### 4.2 The Landmark Case: $\mathbb{Q}(\sqrt{-17})$
To prove the efficacy of their algorithms, Cremona, Thalagoda, and Yasaki provided an exhaustive table of computations for $K = \mathbb{Q}(\sqrt{-17})$, a field whose class group is cyclic of order 4 [cite: 27, 28]. This represents the first complete computation of Bianchi modular forms over a field with a class group of order 4 [cite: 27].

The computational environment utilized two independent implementations to ensure rigorous cross-verification: a highly optimized C++ package (`bianchi-progs`) developed by Cremona, and an extended Magma implementation developed by Yasaki and Thalagoda [cite: 1, 28, 29]. For $K = \mathbb{Q}(\sqrt{-17})$, the algorithms tabulated:
* Homology dimensions and integral homology structures at level $\mathfrak{n} = (1)$.
* Homology dimensions for levels with norm $\mathcal{N}(\mathfrak{n}) \le 100$.
* Complete Hecke eigenvalues and eigensystems for levels up to norm 200 [cite: 28].

These computations also integrated the Atkin-Lehner operators, explicitly computing eigenvalues for the principal operators $T_{a,a} W_{\mathfrak{q}}$ and $T_a W_{\mathfrak{q}}$ [cite: 1, 28]. Furthermore, the computations directly verified the modularity of an elliptic curve defined over $\mathbb{Q}(\sqrt{-17})$, connecting the computational data back to the Langlands conjectures proven algebraically by Caraiani and Newton [cite: 1, 28]. All resulting dimensions, Hecke fields, and normalized eigenforms have been successfully integrated into the L-functions and Modular Forms Database (LMFDB), radically expanding the repository for imaginary quadratic fields [cite: 1, 5].

## 5. Bianchi Period Polynomials and the Rationality of Periods

Understanding the arithmetic of the $L$-functions of Bianchi modular forms relies heavily on integrating these forms along specific paths—a process that yields "periods." For classical modular forms, the Eichler-Shimura isomorphism maps a cusp form to a period polynomial, and Manin's rationality theorem dictates that the ratios of these periods are algebraic numbers. Generalizing this to Bianchi modular forms has seen intense focus up to 2025.

### 5.1 The Explicit Eichler-Shimura-Harder Isomorphism
In 2025, Anderson, Harrigan, Hoback, Pugh, and Wong published a crucial synthesis and new short proof regarding the rationality of periods of Bianchi modular forms over Euclidean imaginary quadratic fields [cite: 6, 30]. 

The space of Bianchi modular forms of parallel weight $(k,k)$ on $SL_2(\mathcal{O}_K)$ is isomorphic to the cuspidal cohomology $H^1_{\text{cusp}}(Y_\Gamma, V_{k,k})$. Here, $V_{k,k} = V_{k,k}(\mathbb{C})$ represents the complex vector space of polynomials in variables $X, Y, \bar{X}, \bar{Y}$, homogeneous of degree $k$ in $(X, Y)$ and degree $k$ in $(\bar{X}, \bar{Y})$ [cite: 6]. 

If $F$ is a Bianchi cusp form, its associated differential 1-form $\omega_F$ can be integrated to produce the Bianchi period polynomial $r(F)$. Anderson et al. explicitly constructed this mapping:
\[ r(F)(X, Y, \bar{X}, \bar{Y}) = \int_0^\infty \omega_F = \sum_{p,q=0}^k \binom{k}{p} \binom{k}{q} r_{p,q}(F) X^{k-p} Y^p \bar{X}^{k-q} \bar{Y}^q \]
where the periods $r_{p,q}(F)$ are defined via integrals of $F$ along the imaginary axis in $\mathbb{H}^3$ [cite: 6]. These integrals directly encode the special values of the $L$-function associated to $F$ [cite: 30].

### 5.2 Hecke Operators and Manin's Rationality Theorem
Building on the recent analytic construction of Bianchi period polynomials by Karabulut (2022) and the definition of Hecke actions on period polynomials by Combes (2024), Anderson et al. provided a concrete, explicit form of the Hecke action on the quotient space $\widetilde{W}_{k,k}$ of Bianchi period polynomials [cite: 6, 14, 30].

By computing the precise action of Hecke operators $T_{\mathfrak{m}}$ on these polynomials and establishing integral formulas, they demonstrated that the space of periods admits a rational structure preserved by the Hecke algebra. This provided a new, explicit proof of the analogue of Manin's rationality theorem for Bianchi periods [cite: 14, 30]. This result serves as a remarkably concise alternative to earlier works by Hida and generalizes the Eichler integral mapping classical forms into the space of polynomials, solidifying the algebraic nature of special $L$-values of Bianchi cusp forms [cite: 14, 30, 31].

## 6. $p$-adic Extensions and Future Directions

The study of Bianchi modular forms is rapidly evolving into the $p$-adic realm. The construction of $p$-adic $L$-functions for genuine (non-base-change) Bianchi modular forms remains one of the most mysterious and active areas of research [cite: 32]. 

### 6.1 $p$-adic $L$-functions and Signed Selmer Groups
For a Bianchi modular form $F$ of level $\Gamma_0(\mathfrak{n})$, constructing a $p$-adic $L$-function requires $p$-refinement. Because the prime $p$ can split, ramify, or remain inert in the imaginary quadratic field $K$, the refinement process is highly complex. For instance, if $p$ splits in $K$, there are four standard $p$-adic $L$-functions corresponding to the choices of roots of the Hecke polynomials at the two primes above $p$ [cite: 32]. 

Recent work by Büyükboduk, Lei, Ponsinet, and Williams (2024) explores multi-signed Selmer groups associated to these refined forms [cite: 32]. Using Coleman maps attached to abelian varieties, they generalize the plus/minus theory of Kobayashi and Pollack to motives that are crystalline at $p$ [cite: 32]. Under the Paramodularity Conjecture, if a sufficiently generic abelian surface corresponds to a cuspidal automorphic representation of $GSp_4(\mathbb{A}_\mathbb{Q})$ derived from a Bianchi form, the Iwasawa Main Conjectures predict a strict relationship between these analytic $p$-adic $L$-functions and the characteristic ideals of the algebraic Selmer groups [cite: 32].

### 6.2 The Horizon (2026 and Beyond)
The integration of machine learning and expanded computational power promises to push the boundaries of the LMFDB further, potentially reaching class numbers well beyond 4 and into higher ranks [cite: 29]. Voight and others have outlined ambitious algorithms for mapping binary Hermitian lattices relative to $\mathcal{O}_K$ directly to orthogonal lattices over $\mathbb{Z}$, further tightening the computational loop between orthogonal groups, unitary groups, and Bianchi forms [cite: 3].

Furthermore, as the Calegari-Geraghty method is continually refined, the modularity of abelian surfaces and higher-dimensional Calabi-Yau manifolds over imaginary quadratic fields is inching closer to resolution [cite: 15]. The successful proof of the Ramanujan and Sato-Tate conjectures for CM fields definitively proves that Bianchi modular forms behave with the same rigid, beautiful symmetries as their classical counterparts [cite: 16], assuring that the Langlands program over complex places will remain a fertile ground for discovery in the coming decades.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG09a2bGAJW-EEa7o6Fb044Ch6sNQ6F2o1sioV_Cd93lS5kEs850sC83mlhebkJJlLCVQWrGGLFVuEGhJ8xuMJzy8bjvAz4O1AEJ6UYmNqu6ogly3AEdhAo)
2. [stnb.cat](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfPlz_ybmOUib02E-PGuOPUTXLQTR7--CUqDQ-NUPSGFh4bBUxYK2Uts2-QpWDgv9sQbcJfJX53OTt3dgkWZYkifZs3FWWLL2daP8ZBea2m85LuciTOuepG17ZBZPfs1ipeok1I_GtaXhvMM_-ek4588iTl2M-d4ZvoMZ_Ja0SQlSmqt1sYi0XXsjcp58Zn3khvlivtu_mUeJ3Tf2l3jP1t6Y=)
3. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGW4i1V82YA3ZjcyyzZ77BrZ04CK8KOjTXKR1FFq_LNoZQ3YNJlRM7F5QXjY1fmNSXD0hZ8QehVUejvzNeQAe-r_paLh7Nm3ZVtTl9r4CzD7x_sXZ160wWfxKB7L50x)
4. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzbKn23SkIVi-kf-zCy2EH1L6RyErtG0uIh-rq46kMDqgHy5n1VQouIvZjofnFNiB2ooATImsY27lRcFeRMQ2NE33Ew40hFKdpH197HH_Cg9OqTVwcLlR_rJZwj_X0_KT_NAoo7Ou4TsIShQ==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPHLfXkqPCkXSMuYpeKdQX1uHPUdWmYn0xCLZ4bILV_PQmXF8e6ZfHi0e5fk6liW4lsiyLIIMIQjgRx3SFJisccelU0TpexvbB-wXa5vhTx9yiByWG)
6. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGv6-CUFGH57mq-IQmWLD1NDb3iBUIBkJB666k-O_JJXi9PVyJA_Js1G5kd_piQG_PMksQdFl45GJKkXrnZkB9_vdQYpe9IcCJLv16Z3SfZ14FjMmmwKti30uxFQUw4YHk2Pw0ly7UNvJ7h8G1wR109PYjLCIBs3JKLT1GsMkXUjkdKZERFYiekp1qtw4_oiICevW02RNLMokIq2b1-db09zaLTU_CYn3aS4NxWQek2vrNED2EdgiyBH49gh0N0lVousIVrQliTaJ2ttRgwfbGF_7OpIhhT_NQwvg==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyr03EwJ8CJcoEKUVVvEZ2Sh4bHH_JKGJ93FcnAZDi8Xe8nWFlEOU25ETXkxUbsTSU9Dm9Y8LbWxxFhdynd_t3Fkg_o-NO0IfoFDAHvHM7U4guCjaL)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJ17iAjKks1lu1uh4xzQ2d0V3SZVLknObHKfGYgf7Oer6rbi5_7qf4JlIZ_IqQCDMACxAjxfm2PlkwOUrbCiMXNSA3D5tJbZ7Phw3SglUx0CCuw3X2)
9. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFy7tpu27XiwaYOQUuV4jyFFBDSwKrfttit98Agk9fuyqzCPk6M_DnQYN1m8C-4ofxVmqhxNmotvI8uGWJNlblcR3pXj_TtUJBHKWb4MGu5xRn7HI4S0NUsju-ZGB8=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGn7Q2QWlXBjjvMwcvoyeI4e1os7QYT6VXj-JbX11TT_OsKiyEbUe6PeaoKKgcQWGQZsQLjpkyYb2buy9jtdZCc3KTJ3ngiskLr2vBBFvNe-BuL8ZiQ)
11. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9C25Jnv0lA0PuWgD_OHfsfVmyodPs71ctMVKDNqW4PBh_pV8eCasxGo6UMd2IpT9v1ADJHN_lUi3-uSiAv-9b9-q1KXzUN5_b_JmvS3VaXWeElW_5QCpcAy5NRysPYc2K_XTl5by7AxwR87hmvrICXIOXkhEp5gKyGwxU4BYrOJZbQO-VBuV3uTVCVtXQN4rCeTXDP8FaZA==)
12. [imperial.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGM8x1iWaS3BLSKNBQznolA1Pzr9FtsZnFLRC1uXr4g_6RspnD44PVHsp_BPXf-dlzRUgVY9BEx-4jMY3r_fyDJWOdkvJW16uV1kqX9CVzdpa_Omtqhdsf-9QmGgdz1IJ7hRnMtFl-7yRH1tv-Ic77KREHmYZzj)
13. [warwick.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRYER2vpBFsXWtpYTvCiP6pTwlNL5JzzCtgKaTI20LHFIXYtTnrOWb42zRnwB_SvlsmdqPiBqCTjumIat1KJjj7_5a4hVzGAlX7Gv2GkFqIvFy1oBwHVTqrmS1qmZ36kLycIzPVML78Gu6vwPidL1jG5YUMByfsE3UG_HSuS3suzv1Cx68CHIiVfRj1N7_FnZBZFg=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTOYje0rw7RUJqrNIkz3iMvs7tPUiM0F5IN8YRHhhi0Xpei7kt3i2BfADxkAxiVOrTrMC7W-V_TAUCe6TmhfTb1JarXeFiqo5wxCOucsdKzumUM7iujYR0)
15. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHozPc7OvlL45XyYGmlXocaY8aUjWArCWr8b-zrlfN7hViE36gFHzzxhY69xU9PC4yLR3YgJpehUKbfaSdDbi8dcusRsiSqGlM31ct8tAF9tTQ34d19ixk_q2BX8lH7wnukySs=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtSfvhODq3J9CMZjb_iKHbqxndqYcmHOgz21ywDh2vDmFuKO2m-7UCaIhoSbTUO4Z-TaZlk2JvensJ2Gq0ADjHSYaJdKaSymbuI68L72Ga04IIoNvY)
17. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWkDp-GerTfNrmRo53f_Sv6HP3JVg7V-pQGONsSk3ZdHO45p6V-df98_8QfGVEsiNg2v_GlsAhkXNbHQoG9vqT7l3zF4HMqg61N4wcnBUClANqvbBJPDqK55d2zQcbOew=)
18. [claymath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpR8XS23Uq2UX1_8BzMoYo5Uzr5o0ESmVz09obSr2V7y-Ol-z_JvFcX5xmHatRiOqdWm3I1qdyVpkaxR2XmxKhMrg4i_gqfcfPb4clC50tOEorHI3_VKcjP9VQL79dRCMSx81x7nqnJ7RbDhpPi77CcpyBVQYM6WapHdcc7hxAVA==)
19. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRA71mm5hwyGfEt08-g0oIObbZW9u33Xx6IzjXyjNHlYHPXAvxFdP3QZIyj3r8Q9SocE5iIN3PYuxL6aXYnG_pT4O0OvMkPihVXU6Gd_L2KU9ST1K29Kzn2Eu66lAWHNq6j2gRUgccaA8FoQLkZGUed6RnV6F5n2roxPzAGLy_dHPu5967BaQHO9bCs7KabKqNlPWWEtpeD7Z9)
20. [unc.edu.ar](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEHD7VMwoyr4d6zbvbwN2hvB-LjFtCiBadr4xQhE_41zhoDKccdEoMy_0bcpF1YEz0X1WGQbXRItbMr9qZFQ_5LEjGBjFy9CwatMO7fkBJ2k7TrOW0dQ9OcHMB2CyMjL19NDkz6jLVKDaEI8x_dAhIr3y83mW3STtxRXjP)
21. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKaASjPkZuRkRNSLksJsh9ICeDekfEZfR655l-IzRd2U1_ByXKL_7x1BSYkl0VQfcJEzIliE61ga9PE0b5bfn0HvkfeWBaDpySof_AgtLTupACtQAEyNFaJ4HCT-G_Ovy2TsOR-jEsIeX8efkgpxxBg3-oTxMA45_UYsCJO92AJgvTuBN00AyM4F7f79U_BhQVOC9l1uvM3Sx3t9VvyXD9y8MDVA==)
22. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVVm0bl6azpVscDJVgHkKHoHCmG5SU3niMjMyqnVQNRe5MdXKMhD9_mQHnHpjXFkDbXBTZhmL1QfKk2lAGkw-xkBwwRXDSgmOuf81CqhTmwzgxR5cBVLX9Ty_Ij1VjWJ66GV3H4x0ulEpgGuf5HFfXqBRujAIWyGgboW4uLK4XDmusghQ4syLJvq7MYopkMnyOTajtz-Uu4Vu5Ixs2717CdIOpQyaOqyhy8jwSXPodkYA=)
23. [siegelmodularforms.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMjKArqLDblIi3p67UYmICyMk5kUsSn1JRDkFah-RklP4fMmwfC7Oajcee-bAe5F9qLuT_tAfyD9wkTPIZz3zbhRQhkRBiz2ko0hq3DqSfgH-6HKEbU9JsWB1RhKJ5F6ibNxcJYDtdiCFYc_8Jg8Cli7Epu5voabEI4WVzNPquRdkdPQ==)
24. [ukri.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsUtaAvhcgHlqEd3w7oQkelx3q1KyXNhZfWA8bM4bj9KDTaqGte539k3R8F80GxJm1n6DNg3eJ1BvGdKP1IJ_au3gJz0m3n-8uzlfQEYFYqfwADZT6BsmWZju8kIsewJKb2v8WrExzqBS-atUowenkCE-onD_Fjlw9noPMtU0qyhO4YM0eZqS1-EijsEbVmMU7oS1tPE5oLjoUv_w5pwamsPRMBkERjDyLh1LuIeQ2tf2DO2xKZz0=)
25. [doi.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEI6YgRYJArTtNimtU34s7I34CrJ4O35jk4H4zq-CyT6HDPFdCO4Dq8xpG68-fy5n79ipMNUaeaNvMYYTCNtiwrnNq21oB0JkRBk2U3vPT57JIxg1woK9q8KrP2)
26. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkBVskGgd-fkMjUOio1MGtv798cDlEWBXVgccmuhSe2kBGyAsA-c9NBWAvckQ9ZZWRTZJHYHOW9foXRsLkR3Tgp7k5nJXWRXS63OvSnKdE4cMpLcXWCp6PpyPonWt61F0IOgiIQ14rdnDLRVdUXjaw)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwNB475AbkXWVMSngoNQtNSrzUUFq_9-2caHaTxjjCHP4RefTvIIYOhHjM-8w603RRl1d0K4cMoIZQ29P4aM64VBRl8iB97_YJHlACjAUWbgqSgNFkqZf8)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGu4gbAKKr66A-pWBrzGKrqUolMNzXg8WaPmzSDoZDFsf2gKXjcO4Z1BFq_MBns01YPnN_bcrt-IV8egN7Ms7rhleMvFOqCXSdVCAdimj0oDhqOxb5E)
29. [kalani-thalagoda.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFA03rFc7HhqxUoBGqj1bwhuypsxbSsk9qDUcmghwCV-wD7Jkp7fEibaNz7vwmUiXZPJrXX_iAv7FioIHDiECR3g45v4nVyuedvJWjA_VHrf1ltYzaSUW0ziISy-zDw)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbfO4fctrKX7GC8bKMGuBCAkueS30Q487IEjbpnlatUq89xYi3JoESihXO3-f3CDGH9ttszR6sDBRBYCpV_uq_Fy4ko9MyCoYX44fylS_Gy1Mfnf44)
31. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHs-nHdp9QjXw70JAFgmXcaGsmhnfS0cgdDG5AlnBCY3erOuDSTXFVVgsQ5dNJ8vgei-OCtnRj8uEYCDepBiajPObjzgHPLUTCKRQKd7fXJLvZts0zpO7pSJ4UcGbpXHQNuStSrNFjIYL7K-3Pwq8Gdx720T5dkwj84YmPwxWFcc1sfxfdu)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_79t7ku6SLQn-QCTUI5P6sPjoyuzDnY_OvH0TSTJTflQzZNh3OpwVwW6UiS7DaS3zmuPKdmBaZr0oB7j6sc9D_nUkZ2SuNTWk2VEN3Uex0AVaPxqb)

