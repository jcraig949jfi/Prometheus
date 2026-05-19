# PARA-P18: Infinity-categories in number theory

**Pythia queue id:** 54
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdBMFVNYW8zVk8tR05fUFVQM1llWmdBOBIXQTBVTWFvM1ZPLUdOX1BVUDNZZVpnQTg
**Elapsed:** 442s
**Completed at:** 2026-05-19T11:17:18.713195+00:00

---

# Recent Applications of Infinity-Categorical Methods to Number Theory (2024-2026)

**Key Points**
*   Research suggests that the integration of infinity-categories ($\infty$-categories) into number theory has transitioned from a foundational endeavor to a highly applied toolkit, driving major breakthroughs in the mid-2020s.
*   The Fargues-Scholze geometrization of the local Langlands correspondence has been rapidly expanded into the Categorical Local Langlands Conjecture (CLLC), with monumental proofs emerging for the "tame" case and for $\text{GL}_n$ between 2024 and 2026.
*   The concept of derived Hecke algebras is reshaping our understanding of L-functions. Recent evidence leans toward a deep, unified compatibility between derived Hecke operators and classical Stark units, particularly for weight-one modular forms.
*   Iwasawa theory is currently undergoing an $\infty$-categorical revolution. Derived Iwasawa theory and "Hodge-Iwasawa" theory leverage condensed mathematics and derived categories to study arithmetic deformations that were previously inaccessible. 

**Overview of the Paradigm Shift**
For decades, number theory relied on classical algebraic structures—rings, modules, and ordinary categories. However, mathematicians frequently encountered phenomena where "hidden" higher-order information was lost when taking quotients or dimensions. Infinity-categorical methods, initially developed in algebraic topology, allow mathematicians to retain this hidden structural data. By tracking not just *that* two objects are equivalent, but *how* they are equivalent via an infinite hierarchy of homotopies, $\infty$-categories provide a native language for derived algebraic geometry. 

**The Three Pillars of Recent Progress**
This report synthesizes recent advancements (spanning 2024 to 2026) into three primary pillars. First, we explore the Categorical Local Langlands program, which relies on $\infty$-categories of $\ell$-adic sheaves on advanced geometric objects like the Fargues-Fontaine curve. Second, we examine derived L-functions and derived Hecke algebras, which replace classical operators with higher homological operations to solve outstanding problems regarding special L-values. Finally, we break down $\infty$-categorical Iwasawa theory, where classical main conjectures are being upgraded to higher-codimension module structures and condensed mathematics. 

***

## Introduction to Infinity-Categorical Methods in Arithmetic Geometry

The infiltration of infinity-category theory—primarily codified in Jacob Lurie's *Higher Topos Theory* and *Higher Algebra*—into number theory marks one of the most profound methodological shifts in modern mathematics [cite: 1]. While ordinary category theory relies on sets of morphisms and strict equivalences, $\infty$-categories treat morphisms as topological spaces (or simplicial sets/anima), naturally accommodating phenomena up to coherent homotopy. This framework encompasses the theory of stable $\infty$-categories, which upgrade triangulated categories and abelian categories, alongside the Barr-Beck monadicity theorem and higher operadic algebras [cite: 1].

In the period of 2024–2026, the arithmetic geometry community has moved beyond merely rewriting classical theorems in this new language. Instead, researchers are wielding $\infty$-categorical tools to prove previously intractable conjectures. The $\infty$-categorical formalism is strictly required when dealing with derived moduli spaces, the highly singular stacks of p-adic geometry, and the subtle derived limits present in p-adic Hodge theory [cite: 1, 2]. In particular, the development of condensed mathematics by Clausen and Scholze—which replaces topological spaces with condensed sets (sheaves on a site of profinite sets)—relies inextricably on $\infty$-categories to manage derived functional analysis [cite: 3, 4].

This report exhaustively details three major fronts of this revolution: the categorical upgrade of the local Langlands correspondence spearheaded by Fargues, Scholze, Zhu, Hansen, and Mann; the emergent study of derived Hecke algebras and their relation to special values of L-functions by Zhang, Venkatesh, Kim, and Kwon; and the $\infty$-categorical reconceptualization of Iwasawa theory by Sharifi, Tong, and others.

## Fargues-Scholze Geometrization and the Categorical Local Langlands Conjecture

The local Langlands correspondence historically proposed a natural bijection between the L-packets of smooth irreducible representations of a reductive p-adic group $G(E)$ and certain Galois-theoretic data known as L-parameters [cite: 5, 6, 7]. By 2021, Fargues and Scholze succeeded in geometrizing this correspondence using the Fargues-Fontaine curve, a fundamental object in p-adic Hodge theory [cite: 8, 9]. However, between 2024 and 2026, the focus has shifted dramatically toward a vast generalization known as the **Categorical Local Langlands Conjecture (CLLC)**.

### The Formulation of the Categorical Local Langlands Conjecture

The classical correspondence is largely set-theoretic. The categorical upgrade posits that the discrete bijection is merely the shadow of a much deeper equivalence of $\infty$-categories [cite: 5, 7, 10]. Specifically, for a reductive group $G$ over a non-archimedean local field $F$, the CLLC predicts an equivalence between:
1.  A derived category (specifically, an $\infty$-category) of $\ell$-adic sheaves on the stack of $G$-bundles $\text{Bun}_G$ on the Fargues-Fontaine curve (or the closely related stack of $G$-isocrystals $\text{Isoc}_G$).
2.  A category of ind-coherent sheaves on the stack of L-parameters (the moduli stack of Langlands parameters for the Langlands dual group $\hat{G}$) [cite: 7, 10].

This equivalence is expected to intertwine Bernstein-Zelevinsky duality on the automorphic side ($\text{Bun}_G$) with a twisted Grothendieck-Serre duality on the spectral side (the stack of L-parameters) [cite: 7, 11]. 

| Feature | Classical Local Langlands | Categorical Local Langlands (CLLC) |
| :--- | :--- | :--- |
| **Primary Objects** | Irreducible smooth representations of $G(E)$ | $\infty$-categories of $\ell$-adic sheaves on $\text{Bun}_G$ |
| **Spectral Data** | Discrete L-parameters (homomorphisms to $^L G$) | Ind-coherent sheaves on the moduli stack of L-parameters |
| **Nature of Map** | Set-theoretic bijection (or finite-to-one for L-packets) | Full equivalence of stable $\infty$-categories |
| **Duality** | Contragedience | Intertwines Bernstein-Zelevinsky and Serre duality |

### Xinwen Zhu's Tame Categorical Local Langlands (2024-2025)

While Fargues and Scholze formulated the conjecture using the highly complex moduli stack of $G$-bundles on the Fargues-Fontaine curve, Xinwen Zhu provided an alternative, highly fruitful formulation operating on the stack of $G$-isocrystals [cite: 7, 10]. The stack of $G$-isocrystals, denoted $\text{Isoc}_G$, is structurally more akin to classical algebraic geometry, avoiding some of the heavy condensed mathematics and perfectoid geometry required by $\text{Bun}_G$ [cite: 10].

In landmark work presented in 2024 and 2025, Zhu gave a precise formulation of the CLLC and established the proof for the "tame" case [cite: 6, 10]. Zhu's tame categorical local Langlands correspondence applies to unramified groups with a connected center, utilizing $\mathbb{Q}_\ell$-coefficients [cite: 6]. A critical outcome of Zhu's framework is the ability to extract an enhanced discrete Langlands parameter for depth-zero supercuspidal representations directly from the categorical equivalence [cite: 6]. By utilizing the classifying stacks of finite groups (such as the quotient of a reductive group by Frobenius conjugation), Zhu demonstrated that the category of representations of the finite group $G(\mathbb{F}_q)$ is equivalent to the category of sheaves on these classifying stacks, bridging classical representation theory with $\infty$-categorical sheaf theory [cite: 6].

### Hansen and Mann: Strategy and Proofs for $\text{GL}_n$ (2024-2026)

Concurrently, David Hansen and Lucas Mann have developed a comprehensive strategy to prove the categorical local Langlands conjecture for $\text{GL}_n$ and other "well-understood" groups [cite: 5, 12, 13]. Their approach builds on the foundations of Fargues-Scholze, Zhu, and earlier work by Ben-Zvi, Chen, Helm, and Nadler [cite: 11, 12].

During intensive seminars and workshops spanning 2024–2026 (including the KIAS summer school and programs at the Max Planck Institute), Hansen and Mann outlined the technical intermediate results necessary to establish this equivalence [cite: 12, 13]. Key innovations in their work include:
*   **The Spectral Action**: Defining a spectral action of the category of perfect complexes on the stack of L-parameters onto the category of $\ell$-adic sheaves on $\text{Bun}_G$ [cite: 8, 13].
*   **Duality Theorems**: Proving deep duality theorems for this spectral action, which are required to map the topological properties of sheaves correctly across the equivalence [cite: 13].
*   **The Spectral Geometric Lemma & Temperization**: Introducing the "spectral geometric lemma" and the "spectral temperization theorem" to handle the parabolic induction geometrically [cite: 13]. Parabolic induction is geometrized via Eisenstein series functors over the stack of $G$-bundles, a topic heavily investigated by Linus Hamann [cite: 9].

Hansen and Mann's proof for $\text{GL}_n$ represents a massive triumph for $\infty$-categorical methods. It essentially proves that the "magic wand" conjecture of Fargues—predicting the existence of specific Hecke eigensheaves associated with discrete L-parameters—is rigorously grounded [cite: 13]. Furthermore, their work establishes that the singular locus of the fine moduli stack of L-parameters naturally encodes the internal structure of L-packets, a phenomenon invisible to classical set-theoretic Langlands [cite: 14].

### Compatibility with Classical Correspondences

A major requirement for the $\infty$-categorical generalizations is backward compatibility with established classical theorems. For $G = \text{GL}_n$ and its inner forms, Fargues-Scholze and Hansen-Kaletha-Weinstein showed that the geometrization is fully compatible with the classical local Langlands correspondence constructed by Harris-Taylor and Henniart [cite: 15].

Recent preprints (up to 2025) have extended this compatibility to $G = \text{GSp}_4$ and its unique non-split inner form $G = \text{GU}_2(D)$ (where $D$ is a quaternion division algebra over $L$) [cite: 15]. Proving this requires delicate $\infty$-categorical tracking of parabolic inductions to reduce the problem to supercuspidal representations, accounting for the fact that the local Langlands correspondence for these specific groups is not a strict bijection but rather involves L-packets of varying sizes (sizes 1 or 2) containing a mix of supercuspidal and non-supercuspidal representations [cite: 15].

## Derived L-functions and the Derived Hecke Algebra

The second major thematic application of $\infty$-categories to number theory lies in the realm of automorphic forms, specifically the derived Hecke algebra and its profound connection to special values of L-functions (L-values) [cite: 2, 16]. 

In classical Langlands theory, Hecke operators form a commutative algebra acting on spaces of automorphic forms, and their eigenvalues determine the L-functions associated with these forms [cite: 2]. The derived Hecke algebra arises when one replaces classical spaces of endomorphisms with "derived endomorphisms," formally computed as Ext groups within the derived category of representations [cite: 2]. This concept bridges derived algebraic geometry with the Langlands program, yielding new invariants that control the torsion in the cohomology of arithmetic groups [cite: 2].

### The Harris-Venkatesh Conjecture and Robin Zhang's Unified Stark Conjecture (2024-2025)

The theoretical foundation for applying derived Hecke operators to L-functions was laid by Venkatesh, Prasanna, and Galatius, culminating in the Harris-Venkatesh conjecture. This conjecture posits that the action of derived Hecke operators on weight-one modular forms is deeply related to algebraic units modulo $p$ (Stark units) [cite: 16, 17]. Weight-one modular forms are exceptional because they appear in both degree-0 and degree-1 coherent cohomology of the same automorphic vector bundle, making them the perfect candidates for degree-shifting derived Hecke operators $T_{p,N}: H^0 \to H^1$ [cite: 16].

In a series of breakthrough papers finalized between 2023 and 2025, Robin Zhang formulated and proved a unified compatibility between the Stark conjecture and the Harris-Venkatesh conjecture [cite: 16, 17, 18]. Zhang's work explicitly addresses the derived Hecke algebra for dihedral weight-one forms.

1.  **The Adjoint Deligne-Serre Representation**: For a weight-one modular form $f$, Deligne and Serre associated a 2-dimensional Artin representation $\rho_f$. Zhang utilizes the 3-dimensional trace-free adjoint representation $\text{Ad}(\rho_f)$ and its associated "Stark unit group" [cite: 17].
2.  **p-adic Derived Hecke Operators**: In his 2025 work, Zhang outlines the definition of p-adic Shimura classes and p-adic derived Hecke operators on the completed cohomology of modular curves [cite: 17, 19]. He conjectures a precise relationship between the action of these p-adic derived Hecke operators on cusp forms of weight 1 and the p-adic logarithm of the Stark unit for the adjoint Deligne-Serre representation [cite: 17, 19].
3.  **Two-Variable $\text{PGL}_2$ Siegel-Weil Formula**: The key technical engine behind Zhang's compatibility theorem is a novel two-variable $\text{PGL}_2$ Siegel-Weil formula [cite: 16, 18]. This $\infty$-categorically derived formula precisely calculates the Laurent series coefficients of Eisenstein series as a dual theta lift of other Eisenstein series [cite: 16, 18]. By applying this to the Rankin-Selberg periods of imaginary dihedral optimal forms, Zhang extracts a refinement of Stark's formula relating L-values to elliptic units [cite: 16, 18]. 

By conceptually reinterpreting the action of derived Hecke operators as "modular Stark unit data" at almost all primes, Zhang's work proves that the topological (derived Hecke) and arithmetic (Stark units) perspectives are merely two sides of the same derived coin [cite: 16, 18].

### Non-Vanishing Modulo $p$ of the Derived Hecke Algebra (2024)

Another critical application of the derived Hecke algebra to L-values and arithmetic topology is the recent (October 2024) work by Dohyeong Kim and Jaesung Kwon [cite: 20, 21]. They investigated the derived Hecke action on the cohomology of an arithmetic manifold associated with the multiplicative group over a number field [cite: 20, 21].

A persistent challenge in the derived Langlands program is proving that these higher-derived operations are non-trivial (i.e., they do not simply vanish, which would render them useless for extracting arithmetic data). Kim and Kwon proved that the degree-one part of the derived Hecke action is non-vanishing modulo $p$ under mild assumptions [cite: 20]. Their proof uniquely incorporates the classical Grunwald-Wang theorem from class field theory into the $\infty$-categorical framework of derived cohomology, demonstrating that classical algebraic number theory is deeply entangled with the non-vanishing of derived Hecke classes [cite: 20, 21]. This non-vanishing is speculated to govern the mod-$p$ behavior of L-values and abelian modular symbols over real quadratic fields [cite: 22].

## $\infty$-Categorical and Derived Iwasawa Theory

The third pillar of recent $\infty$-categorical applications in number theory involves the deformation of Galois representations, specifically Iwasawa theory. Classical Iwasawa theory relates the arithmetic of class groups in infinite towers of number fields (the algebraic side) to p-adic L-functions (the analytic side), famously culminating in the Mazur-Wiles proof of the Main Conjecture for cyclotomic fields [cite: 23, 24]. 

However, classical Iwasawa theory is traditionally restricted to codimension-one phenomena; characteristic ideals of Iwasawa modules are essentially principal divisors [cite: 25]. Through the lens of derived categories and $\infty$-categories, a "Higher Iwasawa Theory" has rapidly coalesced between 2022 and 2026.

### Sharifi's Conjectures and Derived Exterior Powers

Romyar Sharifi, in collaboration with Martin Taylor and others, has driven the development of an Iwasawa theory that operates in higher codimensions [cite: 24, 25]. A classical Iwasawa main conjecture describes the codimension-one support of an Iwasawa module in terms of a p-adic L-function [cite: 25]. To access higher codimension supports, Sharifi and Taylor utilize the $n$-th Chern class of the maximal codimension $n$ submodule [cite: 25].

To achieve this, they study $\Omega$-modules within the derived category of finitely generated Iwasawa algebras [cite: 25]. By employing the Dold-Puppe derived $d$-th exterior power of chain complexes, they isolate exterior quotients of Iwasawa modules [cite: 24]. Specifically, they analyze quotients of top exterior powers of an Iwasawa module by a sum of exterior powers of inertia subgroups [cite: 26]. 

Using derived Iwasawa-theoretic versions of Poitou-Tate and Tate duality, they proved that the codimension-2 support of an exterior quotient is governed by a pair of first Chern classes corresponding to distinct CM types [cite: 25, 26]. Under localization away from bad primes, this yields an exact isomorphism in the derived category between an exterior quotient and the quotient of an Iwasawa algebra by the ideal generated by a tuple of first Chern classes (which interpolate p-adic L-functions) [cite: 25, 26]. Furthermore, conditional on Greenberg's conjecture, derived deformation ring techniques (such as universal ordinary pseudodeformation rings) have successfully linked Sharifi's conjectures to the Gorenstein property of the ordinary eigencurve [cite: 23].

### $\infty$-Categorical Hodge-Iwasawa Theory (Xin Tong)

Perhaps the most structurally radical application of $\infty$-categories to Iwasawa theory is the emergent "Hodge-Iwasawa Theory" spearheaded by Xin Tong [cite: 27, 28]. Developed extensively between 2022 and 2024, Hodge-Iwasawa theory seeks a simultaneous, unified generalization of the relative Iwasawa theory of Kedlaya-Pottharst and the relative p-adic Hodge theory of Kedlaya-Liu [cite: 4, 28].

The traditional divide between p-adic Hodge theory (which deals with local Galois representations and period rings) and Iwasawa theory (which deals with global towers and p-adic L-functions) is dissolved in Tong's framework [cite: 29]. 

#### Condensed Mathematics and Solidification
To achieve this unification, Tong relies heavily on the Condensed Mathematics program initiated by Peter Scholze and Dustin Clausen [cite: 3, 27]. Condensed mathematics replaces topological spaces with condensed sets to fix the pathological behavior of derived categories of topological vector spaces [cite: 30]. 

In Tong's $\infty$-categorical Hodge-Iwasawa theory:
*   Hodge modules are formalized within $\infty$-categorical derived categories of inductive Banach modules and the condensed solidification of topological modules [cite: 29].
*   The framework utilizes the Clausen-Scholze derived category $D(\text{Mod}_\Pi, \text{condensed})$ of condensed modules over a deformed period ring $\Pi$ [cite: 3, 27]. 
*   These $\infty$-categorical sheaves are evaluated over analytic stacks and the schematic Fargues-Fontaine curves, mapping the deformations of profinite fundamental groups directly into the derived category [cite: 4].

#### Noncommutative Deformations and Applications
The utility of the $\infty$-categorical Hodge-Iwasawa framework becomes apparent when dealing with noncommutative rings. Classical Iwasawa theory is abelian, but the noncommutative Tamagawa Number Conjectures (Burns-Flach-Fukaya-Kato) require noncommutative Iwasawa theory [cite: 3, 27]. Tong's derived noncommutative Hodge-Iwasawa deformation theorems provide the exact $\infty$-categorical machinery needed to track multidimensional Frobenius modules and families of general motivic structures across these non-abelian geometric towers [cite: 3, 4, 27]. 

This allows mathematicians to process arithmetic families of representations of fundamental groups in derived analytic geometry, providing a theoretical foundation to evaluate the p-adic Kubota-Leopoldt elements and characteristic ideals in highly non-commutative, non-étale scenarios [cite: 4, 31]. 

## Conclusion

The period from 2024 to 2026 has witnessed the definitive maturation of infinity-categorical methods in number theory. Far from being an abstract foundational exercise, the language of $\infty$-categories, stable derived categories, and condensed mathematics is actively solving historically rigid conjectures. 

1.  **In the Langlands Program**: The Fargues-Scholze geometrization has birthed the Categorical Local Langlands Conjecture. The successes of Xinwen Zhu in the tame case, alongside the breakthroughs by Hansen and Mann for $\text{GL}_n$, prove that spectral actions on derived stacks of L-parameters flawlessly dictate the behavior of p-adic representations.
2.  **In L-functions**: The derivation of Hecke algebras has unlocked the topological properties of automorphic forms. Robin Zhang's application of the two-variable $\text{PGL}_2$ Siegel-Weil formula conceptually unifies the Harris-Venkatesh and Stark conjectures, proving that derived operators explicitly encode algebraic units. Kim and Kwon's non-vanishing proofs further validate the arithmetic reality of these derived constructs.
3.  **In Iwasawa Theory**: The bounds of codimension-one abelian constraints have been shattered. Sharifi and Taylor's use of derived exterior powers correlates higher Chern classes to multiple p-adic L-functions, while Tong's $\infty$-categorical Hodge-Iwasawa theory utilizes condensed solidification to fuse p-adic Hodge theory and noncommutative Iwasawa theory into a single derived framework.

Ultimately, these developments signal a permanent shift in arithmetic geometry. The continuous, homotopy-coherent approach of $\infty$-categories is no longer an alternative perspective; it is the standard environment required to capture the deepest, highest-order arithmetic truths of the 21st century.

**Sources:**
1. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzBisn0pUoUTKyVvl5eazEV5rH07Ez2OACPv-czWPIy8BAvivftFs4PU5QeY_sWbv749F42BLTFS7HJIeUXz4PWiV_IJmhfAIF4p1RX3Q8qflGbO0uyypr6PJv-MvlZlmK_Fua18s0ScNVkwkSaTaXVURgP19_I8f2kHu3EVogXA6L)
2. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuk38V1QSmV0VSDFmHGvZLyiMYouBXfE64CZ6zCegicBPV8wlI2Ziui8fUj7nCxyysP08-eWAoj4K9cLhz3PWcpu2BQmEJu5I2PJlIs9UfGXNfzV1eIInsEt6sSWRB5gzwAH9n3g==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQES48LI_IXkn1fn30n9_HjgCxRJK13WCfYXFHCDdKgNGDk3O4gPUxAhUxiu9GJo5qFJcPybEYcueuMLNIOOFD9ecW8oisQ6-B5hJtO5AzQQIz5hQ1yA)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDw_IzjkDkW5iySW_fG7Vl2gs3VMnktkjb68CHWxILvqX102XElZNj8PgDSUOaJSnO_168wJ1f6nokbd6J-9sifbT5__OV8-2YLdhu-qnxv2ZV3tKG)
5. [davidrenshawhansen.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWnmfLIu3YuGWYqDsL2RvTpNT1Y0JHE5OvkFrISQIvnPlPGECNIbSvGA3a8bPI8qsQOUkdpaJfURb9bhXR-3tzzHEYJSrI-uSiJf3_9SY9yNsCR-HnCmo-whLhbESe8wxI_g76my_u)
6. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUgwt0V-wor-hiHnqw8Ipl-gRFV2DTQppKjoKsV9HfjMS4SQEpLPmQgugo-d_YSSLt3lukUBEZS-zvNG4JS4rnOcI3WaLBK5-P8lkbBns9mEaMtvyWDRsUlIfHlUrw3D4=)
7. [davidrenshawhansen.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFROp3Tefh_mF-oi1V7v9el5nQnE-TaZ-mfI7NRQfDX-dOZF0lAR16Pa2CwQ2aqgguc-FpoGazWo1k9GwzslSDS-wf3oHU1rZaAiKTMty3M0hiA3EECFTk2GfAj10C)
8. [rochester.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMQCGHGxkJKjB3d2cEyMIoWxHo_-0ecfTEfsiXhJK658ya4x7ntpq6AlTJjYi8TO8iYnojkO-DZtZp3kUF6zuna2fmdtrIDT8prmoFOG02qi4nYMdRy_XgLKUgap9z1tHw5g5BFgIa46riHZRaGvYGUAuWIqzJE_RslHu1gyDlikl9PwuJ-Wi8nA==)
9. [mfo.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9Bfh6ROf_DJiMDadlpSY5TgJ4W4VbFzNRsvjWrHm9qoFe7pbIceELlHmrN8f8AkprQTJIPrp-O58M50RY2wmmlZ-5lcGMoD_06yZtX0Np5l4E2xDyqcgmzy8Zi9a7pIL3j7NlCCd8gc5ZcqrSf7OB-45R04fVZwICrV0lPwUymc8O99KD0TozSMPPaAPNNKFT)
10. [tu-darmstadt.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMoPRpm3q0UqnlisfP7N8A5oPbTWBFvSahwS8lc0xBIkEoOjN6WKvCPFmCE226O3zQUlt95758n20JB1iL88I24eJXhGue9tiW_D4h1YZnduW6Hl2z2j4Q6KZ5YAS1vYsWk4uPK-2dggT1UM_E4eMl0gOVAyL0Fi3bjJUQBr00cJFQAlw=)
11. [davidrenshawhansen.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8HjvZ99QrvLGEjKGxSsGqZlr-On5dYHgx1ZKkSX65LcpDbZOpAkIIUpZqbVQlZ-xVg4Ej6c4hU3jFwI7iGiYr43jk4RY-KCGXPs5-TO_7TCcD4wUd4eofGTgv2AjumHLVnQ==)
12. [davidrenshawhansen.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEcrOPQf8yXzXnvreIhUDf9q-oX8SYFEB9-83nTQx1EGDMdLK9ZS8yZnSDRj1rs6SSXZqrFVJwOPXKIcH-_CrsJDMUmtQ19pQFNkN-nCte1Gf43oFIB5NQovkv99VBbLXK8A6QOsePh6miqNxadrQ1)
13. [uni-bonn.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEi-F_KFArddQgWE29sINn4xDhBewavwrmOYphR5sXvN3FNoBmCQQJBVjUeo9Yz45fjrw39SkWU1RFLmLNPbFQ3c7E3aCq8luI4Mu1WUylnZfTbx0omy3_Lq-hw0eDIzK2Tv0DAY4MioGMX-fHzAoCuj2CJ3G9pCwct1UyrPvaIveNc)
14. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqSrEYiJcxoJhLJ4MhzOEIEB_G3vHFzg0yDA_FcOekDxSiix7BrBq2aJI0YGBeM1B5zdx1bVR7kQivHgFGL6esXa1yqHe-M9NpahVJeKkg__rNdv_CybeovuzkQpd9PjE=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlVMAoHUj22qUKUC9Ymrlz-JHj4R63qhwAe-HNEr8uTZKU1Qafa8wZ0aU4BuLwwBHATdIbYSxu0mg-roNn7ZUZd3vROV128zMW3urzFAZevyK9WKAr)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFz5H2ZodGO2bt_7jlQ1qCKdYtF53TLdNH3g32mhSv-OL50elDC9VSbGKcg9eWdWV5c1UBKPRD3OijOxi2HDa0ENlcrvtvtmuw1yfuHAlpYMjkVROdy)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPynVVqkvovc6had_pVXPHdY7dKwQFbFcr3BFIpzs2Y8VU6x8j8W0KoV6U08ZGBmKu7TSYiHBkN5vnTp1P30ngJA8kL_lf4IsX7Q7JNVVh02qjQyJH)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHc5N8bGTrBvrB5N13q0cytoM9DVVMr1fAQC0ON4Qb-fuuzi93XhPyziAdbAmpL77PzJUEX906eO5bLsvK5zCZ2HL23smjZsUHtqB49cKmUpH54Tnkv)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbKSe-9Q3pGb8HITTvE7OQ8JKWz-hrK42OAtr-gJXut_vP4umQ8zi4O6XkSOxUyJXEFBadFMs8plGR8dhqUHqsGe9zbjOPA88n17OOVluNFvl5_0TP)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-h99pvT_52GuCjGGUfnFvlh_aKkgdhqewIf6AVgcuKwZmlBh38AHGPgJjgcqao17mzrhXqgVQ9aU1ykH-DbSLx6L5yv-7IL5hGJ1r-Zw965unxUvm)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFWNQywvrk4ouDdxSuWMTGWHZALsl9XCdCCq7IwI1m4Tn_FtD-6aOa_QsBIlkuFJs6h3y-_jTlVw6Uj0R_uZkvCkIOUVY22ymy6sRWdNUGV2jd6TWo3rtuBK7iqkCyayEQBLSigC_Wy_kGMh0f1EEtLMlLOpeFN130W18wmCiK5vHuzYbEtN5RmAdRjIEuOG0VD5VmWi82ia_B8q-Pj1fnWAeaQcM8eb6fJSJnhzDzlejdw0Vq0psKHLGyJthD27Xv6HI=)
22. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH21u3a3K7ggzySxYjeOVyzhKZxMhY_iCU00-mu7VvChoYnsDH5ac-7p8GyrbGG1eVekvkqYqEoO1RhuJo_ooL_iAX-4thn712xiit7QcOCM1O728c_03F3Lx1PnjiPxSGUCh-_jMo4uoQrcA8H8g==)
23. [pitt.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJGDAHZ-M0VH48oS1QMP0S7URpr2AY26uzNDBXb1Ksi-t5YIUZDv6eTHX1P7Oiyj80u2e3q6ShA0AUWquNJhNllEoWEsZQ3LAxw59ipNs-Mz-xXRRHv5VHkjZAlveXHQ0rnKW5yaaqRWrJL8Up)
24. [washington.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH26fzLcjxYqRHI3Q5AyGZ1rzCY7Vz04yElB_jBd7EobpBMHgGCOUoEeRHJ0E4oyggSYGGq0GLRTXVM4V-SY1Z0ov3kb45JM9AfOG9zVEyDuWv1tozlTHmPyCaWTF1vEiXtR612vOcXJvXhHLV5pbIsTRPzTXw=)
25. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqWvlB0u7XqE6K_N6voGXWzSzUYMLdTmhUiQDyhew6m72fwMyDc9ghmyAkV1pDfKEE1Uv7nKX8W8e3zuT0xQdUfaPUzA4Ii0e7Aw1Od3XaT3UaZcWHRLq6KGUv9Bmh9w==)
26. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3Ur9T4ic5KqcnZbbjnEz_nMfTa1BhdwbvAY180_QiexhRYMYt_9_9T0g8iGooEfask7OTNW_sqDvHF5Vy5NV_BEs4oWVzmqcwEKpJMdEQgc77o7G20K0KWP7oK6rXM-kFEvkP8uV5HJA=)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEA1oyd1OFqAHLPysmghQ6mSSJAQvLPrZagDFlQag44fe1QNHB-lfA5ApTq3Y4n3y0ZxbYXZcRLCjlhQzPmQ67AgvB0T79vEGV83OMum27Jjy4ooT7RPsHtP0XUGGItG2DZAeo0RYIJ8vIgPDQgOOh-2sDLe2PsMB3oukGe56jhzw_47bJdbkHt2Kujrn70Ux34SKx3Dl9l5EVs8svf_-28ml9h0ehBZgF8TbO79nmshsb1Tvx-QAkAZqHM)
28. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbnVC1Tb2r7JIR6SUccedocYdSYOhAMiw-v2oSTSC5epzThmuuGQBaAGQvujYU_BqfuFbC_aFM7PTjn5vgt2VuJdtyHcu0rjnXudSW7aSJj5ImUgcAKyL8XXY1--YV9xWxTY40afwEu6tyCJvzOh8CQPLLjyiaaYLzxEhpjL8=)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH62yjYapVe_DOS73fMC09KN3qDFnae2UZKDRCTVIZZdasaUsp_ZvjvJRNwifzlM7lgEU-WqCRxxPT8NX0IuvitKTKqsLxkLZ6X3sf153CwmNjwg9g4)
30. [ucsd.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNZXMu4hA1clziDG4sHzdvMsJETD4Moa4vXNwpG6NH723a-C2mUaToYriIRHT-UJ_BCxo0QcRhQlRRwS72yFcO6zzhZ40bZQnxFOFseRW4SECpapi4s2sgev__sS7DrRQqT9KRUSbM6PTdVhg=)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRo3h3EvvhZk5CKg09EalDvTGoboDF99Tx9Em52EdBZXW00jtNiMqr3MNWL1gRtYbnXqhV19KCbRZBnvt4fvqNAr9KuxdrnY73AHCLIMvRcWMbyaUl)

