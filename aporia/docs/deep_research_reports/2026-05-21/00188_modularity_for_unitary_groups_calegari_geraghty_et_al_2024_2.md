# Modularity for unitary groups (Calegari-Geraghty et al) 2024-2026

**Pythia queue id:** 188
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdZajhQYXBMa01yV3MxTWtQNDdqTTBBOBIXWWo4UGFwTGtNcldzMU1rUDQ3ak0wQTg
**Elapsed:** 441s
**Completed at:** 2026-05-21T17:30:04.620474+00:00

---

# Modularity for Unitary Groups and the Calegari-Geraghty Framework: Advances from 2024 to 2026

The landscape of the Langlands program has undergone a profound transformation over the last decade, culminating in a series of landmark results published between 2024 and 2026. At the heart of these developments is the Calegari-Geraghty method, a revolutionary extension of the classical Taylor-Wiles modularity lifting technique. While the traditional Taylor-Wiles method is constrained by strict numerical coincidences that limit its application to essentially conjugate self-dual representations and groups that are compact at infinity, the Calegari-Geraghty framework bypasses these limitations by patching perfect complexes of modules rather than the modules themselves. This paradigm shift has enabled mathematicians to establish the modularity of Galois representations over arbitrary number fields, leading to recent breakthroughs such as the proof of the Ramanujan and Sato-Tate conjectures for Bianchi modular forms, and the potential modularity of Abelian surfaces over totally real fields. 

### Key Points
*   **The Calegari-Geraghty Patching Innovation:** Evidence strongly suggests that by replacing classical module patching with the derived patching of perfect complexes, the cohomological defect (the failure of cohomology to concentrate in a single degree) can be systematically controlled. This method relies heavily on the vanishing conjectures within the Borel-Wallach interval [cite: 1].
*   **Ramanujan and Sato-Tate Conjectures:** Recent literature indicates that the long-standing Ramanujan and Sato-Tate conjectures for regular algebraic cuspidal automorphic representations of \( GL_2 \) over CM fields (Bianchi modular forms) have been successfully resolved by Boxer, Calegari, Gee, Newton, and Thorne in 2025 [cite: 2].
*   **Abelian Surfaces:** It appears that all Abelian surfaces over totally real fields are potentially modular, a monumental result achieved by Boxer, Calegari, Gee, and Pilloni, fundamentally relying on modularity lifting theorems over non-totally real fields [cite: 2].
*   **Local-Global Compatibility at \( \ell = p \):** Research shows that local-global compatibility for torsion automorphic Galois representations—crucial for unconditionally applying the Calegari-Geraghty method—has been established up to a nilpotent ideal, largely due to recent work including Hevesi's 2024 thesis at King's College London [cite: 3, 4].
*   **Equality of L-Invariants:** Recent theorems (2024-2026) demonstrate the equality of the Fontaine-Mazur L-invariant and the automorphic L-invariant for representations of unitary groups and \( GL_n \), paving the way for proving exceptional zero conjectures [cite: 5, 6].
*   **Arithmetic Holonomy Bounds:** In a parallel 2025-2026 development by Calegari, Dimitrov, and Tang, arithmetic holonomy bounds have yielded new effective Diophantine approximations and irrationality measures for values such as \( L(2, \chi_{-3}) \) [cite: 7, 8].

### The Langlands Reciprocity Conjecture
The Langlands reciprocity conjecture serves as the grand unifying theory of modern number theory, proposing a deep and exact correspondence between Galois representations (encoding the arithmetic of algebraic equations) and automorphic forms (encoding the analytic symmetries of reductive groups). Modularity lifting theorems, pioneered by Wiles, are the primary mechanism for establishing this bridge.

### The Role of Unitary Groups
Unitary groups play an indispensable role in this ecosystem. Because direct modularity lifting for \( GL_n \) (\( n > 2 \)) over arbitrary fields is obstructed by a lack of discrete series and the presence of complex infinite places, mathematicians utilize Langlands functoriality to descend to unitary groups, which do admit discrete series and can be chosen to be compact at infinity.

### Torsion in Cohomology
Classical approaches relied on characteristic zero cohomology (Betti or de Rham). However, recent methodologies necessitate a deep understanding of torsion classes in the cohomology of arithmetic locally symmetric spaces. Mod p and p-adic Langlands philosophies have thus become intertwined with derived Hecke algebras and perfectoid geometry.

---

## 1. Introduction and Historical Context

The pursuit of the Langlands program is fundamentally the pursuit of reciprocity—a vast generalization of quadratic reciprocity that connects the absolute Galois group of a number field \( F \), denoted \( G_F \), to the automorphic representations of a reductive algebraic group \( G \) over \( F \). For \( G = GL_2 \) over the rational numbers \( \mathbb{Q} \), this manifests as the modularity of elliptic curves, famously proven by Wiles, Taylor, Breuil, Conrad, Diamond, and others. The engine of these proofs is the Taylor-Wiles method, a commutative algebra technique that identifies a universal Galois deformation ring \( R \) with a Hecke algebra \( \mathbb{T} \) acting on the space of modular forms.

### 1.1 The Taylor-Wiles Method and Its Limitations

The classical Taylor-Wiles method [cite: 9, 10] hinges on a "numerical coincidence" that equates the dimension of the adjoint Selmer group of a Galois representation to the dimension of a corresponding Hecke algebra. Specifically, for a representation \( r: G_F \to G(\overline{\mathbb{Q}}_\ell) \), the method requires that:
\[ [F : \mathbb{Q}](\dim G - \dim B) = \sum_{v|\infty} H^0(G_{F_v}, \operatorname{ad}^0 r) \]
where \( B \) is a Borel subgroup and \( \operatorname{ad}^0 \) is the kernel of the trace map from the adjoint representation. This arithmetic requirement enforces an "oddness" condition. It dictates that the method can essentially only succeed if the base field \( F \) is totally real (or if \( \operatorname{ad}^0 = 0 \)), and the representation \( r \) is self-dual [cite: 9]. 

For groups such as \( GSp_{2n} \) or orthogonal groups over totally real fields, this coincidence holds. However, for \( GL_n \) with \( n > 2 \), or even for \( GL_2 \) over an imaginary quadratic field (a non-totally real field), this numerical parity drastically fails. The gap between the required dimension and the actual dimension is known as the "defect," denoted \( l_0 \) [cite: 9, 11].

### 1.2 The Modularity Problem for Unitary Groups

To circumvent the lack of oddness for \( GL_n \), mathematicians frequently utilize base change and descent to unitary groups. Unitary groups of signature \( (n-1, 1) \) or definite unitary groups of signature \( (n, 0) \) possess discrete series representations, meaning their associated automorphic forms contribute to the cohomology of locally symmetric spaces in predictable degrees.

As highlighted in the foundational works of Clozel, Harris, and Taylor, automorphy of Galois representations can often be established using zero-dimensional Shimura varieties associated with definite unitary groups [cite: 12]. In the zero-dimensional case, coherent cohomology is entirely concentrated in degree zero, and torsion is relatively tame. Harris's 2013 assessment noted that the Taylor-Wiles method struggles with torsion in positive-dimensional locally symmetric spaces, limiting early higher-dimensional results [cite: 12]. However, the landscape has radically changed over the past decade, culminating in the 2024-2026 milestones driven by the Calegari-Geraghty framework.

---

## 2. The Calegari-Geraghty Framework: Theoretical Foundations

In a landmark 2018 paper in *Inventiones Mathematicae*, Frank Calegari and David Geraghty published "Modularity lifting beyond the Taylor-Wiles method," providing a robust framework to bypass the numerical coincidence that paralyzed previous efforts [cite: 13, 14]. This framework is designed specifically for situations where automorphic forms contribute to multiple degrees of cohomology—a phenomenon pervasive when studying \( GL_2 \) over CM fields (Bianchi modular forms) or non-regular weight representations [cite: 2, 15].

### 2.1 The Defect and the Borel-Wallach Cohomological Range

For a connected reductive group \( G \) over a number field \( F \), let \( X_U \) be the associated locally symmetric space of level \( U \). Calegari and Geraghty define the defect \( l_0 \) as:
\[ l_0 = \operatorname{rank}(G_\infty) - \operatorname{rank}(K_\infty A_\infty) \]
where \( G_\infty \) is the real points of the group, \( K_\infty \) is a maximal compact subgroup, and \( A_\infty \) is the split component of the center. 

By a classical theorem of Borel and Wallach, the characteristic zero cohomology of \( X_U \) is non-vanishing only in a specific interval of degrees, centered around a middle degree \( q_0 \). The interval is exactly \( [q_0, q_0 + l_0] \) [cite: 11, 16]. Calegari and Geraghty's crucial insight was extending this characteristic zero vanishing to torsion coefficients. The **Calegari-Geraghty vanishing conjecture** posits that for a non-Eisenstein maximal ideal \( \mathfrak{m} \) of the Hecke algebra \( \mathbb{T}_U \), the mod \( p \) cohomology \( H^*(X_U, \mathbb{F}_p)_{\mathfrak{m}} \) is strictly concentrated in the degrees \( [q_0, q_0 + l_0] \) [cite: 1].

### 2.2 Patching Perfect Complexes

When \( l_0 > 0 \), the dual of the Taylor-Wiles method—which relies on the freeness of the cohomology module over a diamond operator algebra—breaks down because the cohomology groups themselves are not free. To resolve this, Calegari and Geraghty shift the focus from patching modules to patching the entire cochain complex \( C^*(X_U, \mathcal{O}) \) [cite: 1, 9]. 

They rely on a highly nontrivial result in commutative algebra (the Calegari-Geraghty Lemma). If \( S \) is a regular local ring of dimension \( d \ge l_0 \), and \( P^\bullet \) is a perfect complex of \( S \)-modules concentrated in degrees \( [0, l_0] \), then:
\[ \dim(H^*(P^\bullet)) \ge d - l_0 \]
Furthermore, if equality holds, the complex has a unique non-zero cohomology group in degree \( l_0 \), which has projective dimension \( l_0 \) and depth \( d - l_0 \) [cite: 1].

In the patching process, a sequence of complexes \( C_N^\bullet \) associated with varying levels of Taylor-Wiles primes is constructed. Using minimal resolutions and Scholze's ultrafilter techniques, these complexes are patched in the limit to form a perfect complex \( C_\infty^\bullet \) over the patched ring \( S_\infty \). This restores the essential properties needed to prove that the patched deformation ring \( R_\infty \) is isomorphic to the patched Hecke algebra \( \mathbb{T}_\infty \), establishing \( R = \mathbb{T} \) [cite: 9, 10].

### 2.3 Prerequisites for the Method

The unconditional application of the Calegari-Geraghty method relies on three monumental pillars, which have been systematically dismantled and proven by the community leading up to 2026:
1.  **Existence of Galois Representations:** One must attach Galois representations to torsion classes in the cohomology of locally symmetric spaces [cite: 13, 17]. (Largely resolved by Scholze in 2015 via perfectoid spaces).
2.  **Vanishing Conjectures:** The torsion cohomology must vanish outside the Borel-Wallach interval \( [q_0, q_0 + l_0] \) [cite: 16, 18]. (Resolved for unitary groups by Caraiani and Scholze).
3.  **Local-Global Compatibility:** The properties of the global Galois representation restricted to decomposition groups must match the local Langlands correspondence [cite: 1, 17].

---

## 3. Breakthroughs in Modularity (2024-2026)

With the theoretical scaffolding of Calegari-Geraghty firmly in place, the period of 2024 to 2026 witnessed a gold rush of definitive modularity theorems. The collaboration network primarily involving George Boxer, Frank Calegari, Toby Gee, Vincent Pilloni, James Newton, and Jack Thorne systematically solved several of the most famous open problems in the area.

### 3.1 The Ramanujan and Sato-Tate Conjectures for Bianchi Modular Forms

In 2025, Boxer, Calegari, Gee, Newton, and Thorne published a seminal paper in *Forum of Mathematics, Pi* titled "The Ramanujan and Sato-Tate conjectures for Bianchi modular forms" [cite: 2]. 

**Bianchi Modular Forms:** Let \( F \) be an imaginary quadratic field (or more generally, an imaginary CM field). The locally symmetric space for \( GL_2/F \) is an arithmetic hyperbolic 3-manifold. Automorphic forms on this space are known as Bianchi modular forms. Unlike classical modular forms on the upper half-plane, they lack a direct connection to algebraic geometry (like modular curves), making their study notoriously difficult [cite: 15, 19].

**The Theorem:** The authors proved that the Ramanujan conjecture and the Sato-Tate conjecture hold for all regular algebraic cuspidal automorphic representations of \( GL_2(\mathbb{A}_F) \) of parallel weight at least 2 [cite: 15, 19]. 

**The Proof Architecture:** The Ramanujan bound states that for a prime \( \mathfrak{p} \), the Hecke eigenvalue \( a_\mathfrak{p} \) satisfies \( |a_\mathfrak{p}| \le 2 (\mathbf{N}\mathfrak{p})^{(k-1)/2} \). Sato-Tate predicts the equidistribution of these eigenvalues. Both follow from the *potential automorphy of the symmetric powers* \( \operatorname{Sym}^n \rho \) of the associated two-dimensional Galois representation \( \rho \) [cite: 15]. 
To prove potential automorphy of \( \operatorname{Sym}^n \rho \), the authors utilized the Calegari-Geraghty version of the Taylor-Wiles-Kisin patching method over CM fields. Because \( p \) can be highly ramified, they relied heavily on Caraiani-Newton's 2023 resolution of local-global compatibility at places dividing \( p \), alongside new geometric insights into the Emerton-Gee stack to avoid Ihara's lemma [cite: 15]. 

### 3.2 Modularity Theorems for Abelian Surfaces

Another crown jewel of this era is the preprint/paper "Modularity theorems for Abelian surfaces" (with accompanying 2025/2026 video lectures) by Boxer, Calegari, Gee, and Pilloni [cite: 2]. 

The classical Shimura-Taniyama-Weil theorem proved that elliptic curves over \( \mathbb{Q} \) are modular. Expanding this to higher-dimensional Abelian varieties—specifically Abelian surfaces (dimension 2)—over totally real fields has been a major objective.
The authors prove that **all Abelian surfaces over totally real fields are potentially modular**. Consequently, their Hasse-Weil zeta functions possess meromorphic continuation to the entire complex plane and satisfy the expected functional equations [cite: 2, 20].

This proof constitutes a masterful application of the Calegari-Geraghty framework. For an Abelian surface \( A \), the associated Galois representations are symplectic (valued in \( GSp_4 \)). The authors had to work with non-regular weight representations and utilize modularity lifting theorems over non-totally real fields [cite: 12]. By demonstrating that certain auxiliary Abelian varieties could be found where the mod 3 and mod 5 representations coincide with those of known modular surfaces (a "fortuitous coincidence" exploited via the 3-5-7 trick), they boot-strapped the modularity lifting to unconditionally prove the potential modularity of \( A \) [cite: 21].

### 3.3 Local-Global Compatibility at \( \ell = p \): Bridging the Final Gap

A strict requirement for the Calegari-Geraghty method is knowing that the global Galois representation corresponds locally to the predicted automorphic representations at all primes, especially at \( \ell = p \) (the characteristic of the p-adic field) [cite: 1, 17]. 

In a pivotal 2024 PhD thesis at King's College London, Bence Hevesi (supervised by Ana Caraiani and Fred Diamond) proved local-global compatibility results at \( \ell = p \) for the *torsion* automorphic Galois representations constructed by Peter Scholze [cite: 3, 22]. 

Generalizing previous work by Caraiani-Newton (who worked with characteristic zero classes), Hevesi verified the Gee-Newton local-global compatibility conjecture at \( \ell = p \) for imaginary CM fields up to a nilpotent ideal. The core innovation of the thesis was establishing local-global compatibility for \( \mathbb{Q} \)-ordinary self-dual automorphic representations for arbitrary parabolic subgroups [cite: 3, 4]. This result effectively unblocks the Calegari-Geraghty method for torsion coefficients, confirming that the patched Galois representations exhibit the correct p-adic Hodge theoretic properties and monodromy ranks necessary to run the \( R = \mathbb{T} \) argument [cite: 4, 22].

---

## 4. Torsion Cohomology and Non-Compact Unitary Groups

The shift from compact to non-compact unitary groups represents another vital development of the 2024-2026 period. Early modularity lifting theorems (like those by Geraghty in 2018 for ordinary Galois representations) often imposed the restriction that the unitary group be definite (compact at infinity) or that the Shimura variety be compact [cite: 12, 23]. 

### 4.1 Overcoming the Non-Compactness Obstacle

Non-compact unitary groups, such as the split unitary group \( U(n,n) \) or \( U(n-1, 1) \), present extreme difficulties because their associated Shimura varieties have boundary strata. Torsion classes in the cohomology of these non-compact spaces can potentially "bleed" into the boundary (Eisenstein cohomology), complicating the isolation of cuspidal components [cite: 17, 24].

Caraiani and Scholze (2019, with subsequent applications realized fully in 2024-2026) proved that the generic part of the mod \( \ell \) cohomology of Shimura varieties associated with quasi-split unitary groups is strictly concentrated above the middle degree, even in the non-compact case [cite: 17, 25]. 

This concentration of torsion cohomology is the exact geometric manifestation of the Borel-Wallach bound generalized to mod \( p \) coefficients. The implication for the Calegari-Geraghty method is profound: it guarantees that the defect \( l_0 \) can be safely bounded and that the patching of perfect complexes will yield a module with the correct dimension [cite: 1, 17].

### 4.2 The Geometry of the Hodge-Tate Period Morphism

To control this torsion, researchers leverage the perfectoid geometry of Shimura varieties. Let \( X_\Gamma \) be a Shimura variety. In the limit of infinite level at \( p \), one constructs a perfectoid space \( X_{\Gamma(p^\infty)} \) equipped with a Hodge-Tate period morphism:
\[ \pi_{HT}: X_{\Gamma(p^\infty)} \to \mathscr{F}\ell_{G,\mu} \]
mapping the perfectoid Shimura variety to the flag variety [cite: 18, 25].

By analyzing the fibers of \( \pi_{HT} \) over the Newton stratification of the flag variety, researchers can relate the cohomology of the Shimura variety to the cohomology of Igusa varieties [cite: 17, 25]. This deep geometric method allows one to prove that the "strongly non-Eisenstein" localized cohomology vanishes outside the Calegari-Geraghty expected range, validating the preconditions of their patching lemma [cite: 16, 26].

---

## 5. Connections to L-Invariants and Exceptional Zeros

A remarkable corollary of the deep understanding of p-adic deformations of automorphic forms—central to the Calegari-Geraghty machinery—is the resolution of longstanding conjectures regarding L-invariants. 

### 5.1 The Fontaine-Mazur L-Invariant

When a modular form \( f \) has split multiplicative reduction at \( p \), its p-adic L-function \( L_p(f, s) \) frequently vanishes at \( s = 1 \) due to an "exceptional zero," even if the complex L-function does not. Mazur, Tate, and Teitelbaum conjectured a formula relating the derivative \( L_p'(f, 1) \) to the complex value \( L(f, 1) \), connected by an arithmetic constant called the L-invariant, denoted \( \mathscr{L}_f \).

The **Fontaine-Mazur L-invariant** is defined purely in terms of the p-adic Hodge theory of the local Galois representation restricted to the decomposition group at \( p \). It measures the position of the Hodge filtration in the associated \( (\phi, N) \)-module [cite: 5, 27].

### 5.2 Automorphic L-Invariants and Their Equality

Conversely, the **automorphic L-invariant** is defined via the p-adic local Langlands correspondence and the derivatives of Hecke eigenvalues on the eigencurve (or eigenvariety). Greenberg and Benois generalized the exceptional zero conjecture to much higher rank groups, predicting a vast equivalence between analysis and arithmetic.

In a series of major papers culminating in 2024-2026, researchers (including Gehrmann, Rosso, and others) proved the equality of the automorphic and Fontaine-Mazur L-invariants for representations of \( GL_n \) and definite unitary groups under mild assumptions [cite: 5, 28]. 

The proof heavily intertwines with the Calegari-Geraghty approach. By utilizing local-global compatibility at \( \ell = p \) for Galois representations attached to p-ordinary torsion classes (confirming conjectures by Hansen) and studying the étaleness of eigenvarieties via the Calegari-Mazur conjecture, the authors established that the Fontaine-Mazur L-invariant (which is independent of the degree of cohomology and sign) precisely matches the automorphic L-invariant [cite: 5, 6]. This equality is an essential ingredient in proving the Greenberg-Benois exceptional zero conjecture for \( GL_3 \) without any self-duality assumptions [cite: 5, 6].

---

## 6. Arithmetic Holonomy Bounds: A Parallel 2025-2026 Development

While Frank Calegari's work on the Calegari-Geraghty method for unitary groups reshaped Galois representation theory, his output in 2025-2026 has been equally transformative in the realm of transcendental number theory and Diophantine approximation. In collaboration with Vesselin Dimitrov and Yunqing Tang, Calegari introduced the theory of **Arithmetic Holonomy Bounds** [cite: 7, 29].

### 6.1 Apéry Limits and Irrationality

In 1979, Roger Apéry famously proved the irrationality of \( \zeta(3) \) by constructing rapidly converging rational approximations. Calegari, Dimitrov, and Tang significantly expanded this paradigm by formalizing "Apéry limits." They utilized arithmetic holonomy bounds to quantify the dimension of the vector space spanned by certain sequences of period integrals [cite: 7, 29].

Their landmark 2025/2026 result proves the irrationality of the Dirichlet L-value \( L(2, \chi_{-3}) \) [cite: 8, 30]. Specifically, they established the linear independence of \( 1, \zeta(2), \) and \( L(2, \chi_{-3}) \) over the rational numbers. This is considered the first explicit Dirichlet L-value to be proven irrational since Apéry's theorem, marking a historic achievement [cite: 8, 30].

### 6.2 Effective Diophantine Approximation

The quantitative refinement of their holonomy bounds yielded completely new methods for effective Diophantine approximation on the projective line and the multiplicative group [cite: 7, 29]. 

By applying these bounds to a dihedral algebraic construction, Calegari et al. derived effective irrationality measures for high-order roots of algebraic numbers. This creates a multivalent continuation of the classical hypergeometric methods of Thue, Siegel, and Baker. Consequently, they provided algorithmic resolutions for the two-variable S-unit equation, the Thue-Mahler equation, and the hyperelliptic and superelliptic equations [cite: 7, 29]. This parallel line of research emphasizes the profound arithmetic invariants that govern both automorphic forms (via L-invariants and modularity) and classical period values (via holonomy bounds).

---

## 7. Congruences on Unitary Groups and the Bloch-Kato Conjecture

An important auxiliary application of modularity lifting and the theory of automorphic forms on unitary groups is the validation of the Bloch-Kato conjecture. The Bloch-Kato conjecture relates the special values of L-functions to the size of Selmer groups of Galois representations. 

In the context of the unitary group \( U(2,2) \), researchers like Klosin and Brown have utilized congruences between different classes of modular forms to prove specific instances of the Bloch-Kato conjecture [cite: 31, 32]. By finding congruences between CAP (Cuspidal Associated to Parabolic) and non-CAP Hermitian modular forms, they mimic Ribet's classical proof of the converse to Herbrand's theorem [cite: 31, 33]. 

Through these congruences, one constructs irreducible, residually reducible four-dimensional Galois representations. Modularity results proved via the Calegari-Geraghty framework directly feed into this ecosystem. By ensuring that the universal deformation ring \( R \) is isomorphic to the Hecke algebra \( \mathbb{T} \) (even for non-ordinary or residually reducible cases without self-duality conditions), one accurately computes the dimension of these Selmer groups, thereby providing lower bounds on their p-adic valuations that exactly match the p-adic valuations of the symmetric square L-function [cite: 31, 33].

---

## 8. Synthesis and Future Horizons

The mathematical epoch of 2024-2026 will be remembered as the era where the Calegari-Geraghty framework came into its full, unconditional maturity.

### 8.1 Resolving the Remaining Conjectures
The conditional aspects of the 2018 Calegari-Geraghty paper have been thoroughly vindicated. The existence of Galois representations for torsion classes was achieved by Scholze. The vanishing of torsion cohomology outside the Borel-Wallach interval for unitary groups was achieved by Caraiani and Scholze. The crucial local-global compatibility at \( \ell = p \) for these torsion classes was completed by Caraiani, Newton, Hevesi, and others [cite: 4, 17].

### 8.2 Beyond Unitary Groups
With the modularity of Abelian surfaces over totally real fields established, and the Sato-Tate conjecture for Bianchi modular forms solved, the next frontier in the Langlands program is to extend these patching techniques beyond \( GL_n \) and unitary groups to arbitrary reductive algebraic groups [cite: 2, 15]. Furthermore, extending the modularity of Abelian surfaces from totally real fields to arbitrary number fields remains a monumental challenge, one that will likely require resolving the torsion cohomology behavior of more exotic non-compact symmetric spaces.

### 8.3 Conclusion
The sheer diversity of applications—from resolving the Ramanujan conjecture for \( GL_2 \) over CM fields to proving the equality of Fontaine-Mazur L-invariants and bounding arithmetic holonomy for transcendental number theory—highlights the interconnectedness of modern arithmetic geometry. The Calegari-Geraghty method of derived patching over perfect complexes has definitively proven that the lack of discrete series and the failure of numerical coincidences are not impenetrable barriers, but merely technical obstacles that yield to the combined forces of derived commutative algebra and perfectoid geometry. The results from 2024 to 2026 not only answer century-old questions but lay a comprehensive foundation for the complete realization of Langlands reciprocity.

**Sources:**
1. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwBmjBz5Zs4YTQ6_Gyt7Y67ZAzKQ5JJJGQ6--iuoQXE19VV8riWw2PgW4gEaJHRuVJ1qgGCj7UHMbd5cgyGA7X9lVdht-FZbBSNeSl1oapPXppTi3XtbtEZr-iaieTUTdpxVnpjls=)
2. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTIhRywCOKxkLbTTgnkI86FpFsavwjuKigF7YuP5QETLij7DFx1CGsPOwedXHfmEFtM_2iMWofUadzUp0ISbKDJ-4iOXq8DbBcQm_VHQCIJBndTEWRbksz104FBYjFlFVh7RFt)
3. [kcl.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpqIMTb2dwUw86D3UOCzpgOpr_njFWGvIuEeuKPj-egudBjyVWINmJzn2si8dlHfkh1aWXQTrkUdbnVBodiHtsQdlI-N6XBFawyiUT6KvviEhGt4wAFv87WinIFQqXxt-JhqOv9SeNfQcfb8YWKqGQnuj-e4kwGch_1aBaJ0N0N527BTYsMYjhwq2dJ-BHK-lahOUMDS53I8yx8xu7MsgvHbprbZA=)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLfT7PKRxBtRWn0DxqHBpZbKYLU4QHfkspYanjRqXaZsldmlrTIHY_7ZqZYZcrwzztusOOJIIAQUixGQj_N8XegJSM9xTEk_whvouzTshTMWJkAultMw==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIVH4RG7EFQ5Zp5pIiCR73twXJCpZCyRCnvGIjYjzdk3MsNs3iWHhTePn3qvr4EdRKtuOgXLwK-2tXE7e-ecginwO_sw8ZQ5OKY6rTYiAY0pPbQgoEzw==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFll6_N8sCGZ6dPPWGiE0H-LHs-ZrEUFT-KR9c9qnDVo95V8kT3DUwEyVYR9Qgi96VrLiBRyI7CDEp27jLKgqv_-_fd-csQynWaptUdgfWhwr_NYvalJw==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCgYtonnIpDwvslgp_Qyo2-dJuInR3l3wobN9PbiSMqYzs_F9j0edIV6PyjQv9ZvKa-FeBZR5VUDM4q1EcBfbr9DR-V9vV1y3F1wVGSxHjaF7-X4TW6g==)
8. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElGq8NzWC-nefhbGAWFJnsIfacB_EvOtkYCjhkgMTQESnT9TBAhnlKQeAhzQyWdixPEXnzmCAO-hxeEYa432uNj0s8cXaEUxRNgUaFOQUd01zOuQtmntl2tqRnPPEzhsBUsysYT_IiFXjXOV7iCrgNjVGYv8VBiw4Gh-Tbfy8zRbC4Ew-X4tMamHxYrhLC--dDTBeTcRPyYKYaf-CG4wBDKwzIpZUgwDLVnWxhaUfpCSnRwO5n4Yq9x73fX6xsFZ4RXKZUJ_W4kZY05_B9UxbxQgbKm7pLwl4m45JsNgpvl0lO-mT73bUZNISsczdf11v3mgRTIiaFPQLAsLLZRIpoLGVC)
9. [cam.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfJP6GmsoGhIQrmKipEMr5IhafhYtENtLJAIpPlxKwBCRA20KewEKefFffY2BzeCIFWzsa6JlmFtrhwbJfKYQhl4GgEtiacdASRcZCHXcPlG0Jg4NtPxOO_eZx-YZtJ60CMOJTnQ==)
10. [fgispert.cat](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFCYs1OXYmmcAhd0QbR9x6edqdCzo4WaPlvAF6SP3J1C9mX9EjPe_vsmbUXsJ7K2dKpCwgCd80Wy0czmQH1KOPRBWPIKVqr5VWETcX0lll1P6gE0Yb0rFR41JtFY9q7OjQsm15lynoHIcA3AJ5)
11. [mfo.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3A3Jp7PBuOCjb4gWOTc8BeayRc3Izg2KZTcvtu36yDUDk5rJbApC5R-dhJJ2iSt2S2nk1BrjAfSHHPPlpA_39HzDVrznHidEoAzM6XZYecLRhBpOE34xqafFerCS2OSW50QAVSVSW9yVLmz4XhPPb5kKIJJUAT82gzRZfiaGnzsZyJ7qeSjtkbcxjiIZF6ZDcOA==)
12. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPcSwA_uYZjh0KFJVJkaaPXQSZp30aKZf9QtrYE2FANAjykKqjrh9F8B5AEsMGOqXL1RsoKVpmJecXrn0SVd38239itVoSbspU5mDbO6H5fyKx9jWswfzT3HIvJMILovQMHtwW-RrwHYPLEhvC5ES5zUrd2sE3yPOHRP20i3yMXBOqUFeQtWqS_KhQ2SQ5yedzxuN8bENgqhoK)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEau__4ybCt4HDy4hpkQRRljn2DwksmkpBBkqAK4A0Yth1MpQBjD2MjFzbxnhv06CJQAIi2Pg1WZhYlWFcy-1mzAG1SXWlE7kdicxPEB5b0UoyS--TE)
14. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0i9iOfsqUjuOByrdqSxeWI2X2tSp1hpFrAcSphmagbp9CxkIprAOL7qFcN5jIvtBry5fq_vtaGddHVSqwBfVTVtKR5hyuP5rB67_9isQyyjkmemOF3l-eovDzv92JVi1y9_PWyqkPf26o)
15. [imperial.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMZcOEJ6hHYOhUBvB6Ghj4VtYC2vcZ_xE2P9oB-CVmms3qDnAudgpwPrlGKkw2_kYB0tzfz9BD-jFc7v-3JOA2rQ0_fjq_i3ndIYnG-sTFcwtx9q3_Qt1L5H2as0vR1Wgrx2JGEQgsLvUR0x7atv_puA==)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFoVUDxwJDOeuyZtbSORuQSkCE2bbjEQc5lLTfte0IGQMcA24KCtjMYtbG-M62toaGEvN-dl-oyifK7EIZHP5um9yRPvVizTxXxz4SjcFWavyiYzHsEi-3g6KhPHibcTDOVi3DtymlNfoYsLwuRr0zOqkaGAK2Ts9SEvG_n5PFLbjfefWMoh_SkYh-s5BbW6K5ORK-j2y2JhYi5kQ8anHAZUqBqi4bFc2oymHiEfALLR66uIOBjIAKH)
17. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHK7Z0UPSayXkqQqFte1MlIBfr2DztZjnw8YExZmigSb8W6t_p3rR9YAYL8ccvesKXXxtWTL1XrXSyDKMkr0ny4wq_ejAY29HXxZ8rmV4Dd81FdZn2vNizRWwrAePS-dxT8C1oIPmOzEA8MUic=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUNjD3p-rf8HIEKivm2RQLTA5k0s5sqgKIIg2qeDmtmNX8DQkVlUhJvT40_gE_5EBPB842pA9IPHsjbdYkGOLj5VPaNUGC1mePkHv1k3JNU0Xnkh6RIA==)
19. [kab.ac.ug](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqTMthrUw_lP7ruxCL9VPnJYT80gHPh7Dau7ABWsQHGHcVU3TZ7blQGxjFVL6MG_95WYYTuLiprSAi0cRp7EcfaoEaCd84kljgFdBS5s2zsiWDNYTuP1Brr5qnETjKfCr6AeZmP-JD-eUSIgDKGipr52wu6TDLpEAgCBu_AAEmV-uEO3MmnPGOfu-4xg==)
20. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcnTrztPq58VdaczwwSWxq6XtvSrKJxehm5vD3w6nsTqCKGnC0iXSML2j5Egbpukkj5qudQW3CT3Z3mby35AvLV6M22l7cuAiKHn53Dw6fdS7MPV386_-y5VdFUjF2keqHktsnSLnZ24DOKmkE0sDy1w==)
21. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8-L5aMWwbEW7sPgRzQyQyf3vbJ0vbLKlOqSYWA9y4F5SWeUK2yzkOTtDeSzhiwhFcmwt2MCLVvBnwEeyeIvGjJBRc5bYxkLhu4m_00eJAjK5mgSbgCg28yz6QpDNX_oOd)
22. [kcl.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-HOUSAyHufQERJ-vWCC9ppxWzkBZa0hr5RS_7KVBrBGHWdUFrQMjXMnOQ4KFWq6gHPlHqT6aYUByAIdHaRyjdbydolxHNFIXjDxeXCNQWi-9b6zbz8HnTTyngibjoliWr99BEZ-XTKrm6sVpcWQ0yxSQH4zc5nCkGkuHNHscTpQEoICXfZ4K7r-asd-fr-LxKu8faY1k=)
23. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1AHxUUYopRMnfme9rBmBsq0HFUcCDXSl2_3RTwVUc7XET_NL1ma2yoDh_Qsl71VgTo2qJTTUU8N5Ul2W-Tv16Th3ya0Rcxl7UtV6HGtWk5WwDJtWJLBOCbVDtq2nqVDsBeBJkzI_V7vV-_qR5IIa13RKhMizq8LoSkh81mVry5HLwOd1Rp_ot0qLeO-rAVRlhfulBOvEKJ1YYDvZXlMV4Wvh0H7Si4Ei1XMhUA0Vq35xEmtd_mhAtky18yvE6)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCHvOu4Xmp95IAkBxNmSupKXNN_-E5mtfRHtpFwaZRk30RCuG_KwmpyO-1mcOB5zISniBKvId5B7rdMU_GxJlN2BTN0Mp0GH1zlJYCwA1oNY4BxyHy-w==)
25. [euromathsoc.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTKrmPGwB0eMXbMH2UoWbWXt_y-hZbxlZoLFiMgcqlQ5HYaPqymzcuS9NXDHm0csMwfIknh0ivTMkCcQSFo-tYpvsOJXrq5xFbTKcaLmhfHq4YzfMVTYm_pIxE53lh9xzT)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFf9LQt0wCGw6ZHzsPXdW91LBFViqQeZcVEznxLp9P0ieiM2asizYKyIBns-zIwduFFV5CBxCTzfKOAlxyu1Glr1yvKWWFg9-HXAMcLEcU_aw7fPnqWQ==)
27. [brynmawr.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpl0H77x6iw7LknsTX2ew7UVyGSsw4mTJLLCMHBLrs-89kLTtI7IWcnJzSkov38AV_zjiB6l687FQ_GkKdtijJy6wkBFRL_RdwQo2FkJ8MrCGWUH0yK9-ckgwLNaZD6wOT1sMPJmHOrc8Frsb3RdvwMaaWESWSr8i6U6cHzNV8FUJd709CZ3WY)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF366M8dByumpct8G5smoW0KFVCvndfIJy8NKBsKq3ebyY_pi3QbpuvZUJS6ELqu05IJ6_eHgFGXyy7EL5Ab4hQdHeGGDE1uRl_ujVIrXOIhSVbF77MVQ==)
29. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVTFL-I5kV3MEAmRhfhifia2NWiHtftKALnt3S8RaxT-JaSu-jbwVv2jIGlUeWiz4f63mxaCxDAJ2wLcRKQ0m0SXp_qVE35E0h4RsDgvswzFXKQAvvg9S4i3nmg_0w)
30. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFegLdoGuZSzBnE6C2IhxHeMxXXXTeugMQY-8IbXyx0bl7mXv6XAnJLY8ncwxfb4Iv-HQpPcT1U3nGAXxsgoFHT5gzxicw6gxBUVmTnB1lzj-Zlj37zaQw7hSEu_tIQdSWh_eWGHEKG8mOZrgb5G2lyT9i1euyKxaQ=)
31. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgB85RrkVB4_iraPWJ97_hzBYnISWxwl_Vp9CxPmtvW1lgkVvoloOcTYgbd5jYm4-_7vLE0zKIo0va9IBIZe3CpAVyc8wXaBor3HtyvGgYgttsbtkDFqelJmJugLe6GiUIgNcqlkc=)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMJluB3HwzNXz8qdeH_LV4p4DX99Bzxf5WfbaLWTk7PwcKMvfc-GxbsdZTHq750OWEhfy_HBEd1TtbXyVb9CUrEfG1ZQXgtSTja0YRnAJS9NdEVaogWg==)
33. [worldscientific.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlmnoi01cR6bOPM0LdFXDjkj-apq8NcUYo_ryq5NqX-INYZiz4rSdBKLyHeQ8Wd7uu-lMCXFKB-Kt6kqFtu1Bt2TAJBa3SnNtQNxf4N4exSB504mZpMX2T5AMP30VMVIK35V5tYP2HyNFq7qxkK57W6j9_mfWBXQU=)

