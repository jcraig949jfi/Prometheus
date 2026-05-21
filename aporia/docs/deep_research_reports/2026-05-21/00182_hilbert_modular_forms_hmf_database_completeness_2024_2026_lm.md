# Hilbert modular forms (HMF) database completeness 2024-2026 (LMFDB)

**Pythia queue id:** 182
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdhajBQYXJ1N0dmQ0hqTWNQN1lLRXFBcxIXYWowUGFydTdHZkNIak1jUDdZS0VxQXM
**Elapsed:** 373s
**Completed at:** 2026-05-21T17:20:32.121907+00:00

---

# Comprehensive Report on Hilbert Modular Forms (HMF) Database Completeness (2024-2026) within the LMFDB

**Key Points**
*   The L-functions and Modular Forms Database (LMFDB) currently houses over 368,000 Hilbert modular forms, mapped across totally real fields of degrees 2 through 6. 
*   Algorithmic breakthroughs slated for 2025, notably by Hein, Tornaría, and Voight, have significantly accelerated the computation of Hilbert modular forms by mapping them to orthogonal modular forms, overcoming decades-old computational bottlenecks.
*   Completeness bounds in the LMFDB are rigorous but constrained by the underlying number field; while the database is fundamentally complete for fields of degree 2 and 3 within specific conductor norms, higher-degree fields currently rely on matching forms to known elliptic curves of parallel weight 2.
*   The period between 2024 and 2026 represents a renaissance in computational number theory, catalyzed by dedicated conferences like LuCaNT 2025 and Simons Collaboration workshops, which are rapidly expanding the data and theoretical frameworks available to researchers.

**Summary for the General Reader**
Hilbert modular forms are highly complex mathematical functions that serve as a bridge between geometry, algebra, and number theory. They are essentially a higher-dimensional generalization of the classical modular forms that helped prove Fermat's Last Theorem. To study these objects, mathematicians rely on massive, collaborative online databases like the LMFDB (L-functions and Modular Forms Database). Determining the "completeness" of this database—meaning whether every possible function up to a certain mathematical limit has been found and cataloged—is a major ongoing project. Between 2024 and 2026, new computing algorithms and supercomputing efforts are dramatically expanding this database, effectively mapping out a "periodic table" for modern number theorists. While it seems likely that the database will achieve near-total completeness for simpler number fields shortly, the computations for more complex fields remain an ongoing, monumental challenge. 

---

## Introduction to Hilbert Modular Forms

The study of Hilbert modular forms (HMFs) sits at the very core of the modern Langlands program, serving as a critical nexus between automorphic representations, Galois representations, and the arithmetic geometry of Shimura varieties. A Hilbert modular form is an analytic function defined over the product of multiple upper half-planes that transforms in a highly structured way under the action of a discrete subgroup of $GL_2$ defined over a totally real number field [cite: 1, 2]. 

Let $F$ be a totally real number field of degree $d = [F:\mathbb{Q}]$, with ring of integers $\mathcal{O}_F$. The real embeddings of $F$, denoted $\sigma_1, \dots, \sigma_d$, allow the group $GL_2^+(F)$ (matrices with totally positive determinant) to act on the $d$-fold product of the complex upper half-plane, $\mathcal{H}^d$, via fractional linear transformations [cite: 1]. Given a fractional ideal $\mathfrak{c} \subset \mathcal{O}_F$, one can define the Hecke congruence group $\Gamma_0(\mathfrak{c})$. A Hilbert modular form of weight $k = (k_1, \dots, k_d)$ and level $\mathfrak{c}$ is a holomorphic function $f: \mathcal{H}^d \to \mathbb{C}$ satisfying the transformation property:
$$ f(\gamma z) = \prod_{i=1}^d (c_i z_i + d_i)^{k_i} (\det \gamma_i)^{-k_i/2} f(z) $$
for all $\gamma \in \Gamma_0(\mathfrak{c})$, alongside appropriate growth conditions at the cusps (though for $d > 1$, Koecher's principle implies that holomorphy at the cusps is automatic) [cite: 1, 3].

When these forms vanish at all cusps, they are known as cusp forms. The space of cuspidal Hilbert modular forms is finite-dimensional and is equipped with a suite of Hecke operators, $T_{\mathfrak{p}}$, which are self-adjoint with respect to the Petersson inner product [cite: 3, 4]. A primitive Hilbert modular form (or newform) is a cuspidal eigenform for the Hecke algebra that is "new" at its level and is not derived from a base change of a proper subfield [cite: 2]. These primitive forms are the primary objects of interest for arithmetic applications, as they yield well-behaved, analytic L-functions with Euler products, and allow for the attachment of strictly compatible systems of $\ell$-adic Galois representations $\rho_\lambda$ [cite: 2, 3].

## The LMFDB Project and Database Infrastructure

The L-functions and Modular Forms Database (LMFDB) is an open-source, collaborative project designed to map the mathematical universe of L-functions and their underlying arithmetic objects [cite: 5, 6]. The LMFDB provides a structural, searchable interface for complex arithmetic data, utilizing a backend primarily written in Python (80.2%) and HTML (14.6%), alongside elements of JavaScript, CSS, and computational backends leveraging SageMath and Magma [cite: 7, 8].

A defining philosophical pillar of the LMFDB is its stringent adherence to documentation regarding the "completeness, reliability, and source" (often abbreviated internally as RCS) of its datasets [cite: 7, 9]. The framework is divided into overarching sections—such as L-functions, modular forms, varieties, fields, representations, and groups [cite: 6, 9]. For every mathematical object cataloged, the database attempts to assign a mathematically meaningful, permanent, and human-readable label [cite: 7]. Furthermore, the database utilizes "knowls"—expandable informational widgets—to define mathematical terms intrinsically within the browser without requiring the user to navigate away from the primary data page [cite: 6, 7].

For Hilbert modular forms specifically, the completeness and extent of the data are tracked continuously, with relevant metadata securely logged under the URL structure `rcs.cande.mf.hilbert` [cite: 9, 10]. This specific page outlines exactly which finite subsets of the theoretically infinite spaces of HMFs have been successfully computed, verified, and uploaded [cite: 9]. The reliability of this data is also publicly interrogated, detailing any heuristics, unproved conjectures (like the Generalized Riemann Hypothesis, where applicable), and consistency checks employed during computation [cite: 9].

## Current State of HMF Data Completeness (2024-2025)

As of the 2024-2025 period, the LMFDB contains exactly 368,356 computed Hilbert modular forms distributed across 400 totally real number fields of degree 2 through 6 [cite: 5]. This represents a staggering achievement in computational arithmetic geometry, requiring thousands of hours of supercomputing effort to resolve Hecke eigenvalues and Fourier coefficients [cite: 5, 11]. 

The completeness of the HMF database is deeply intertwined with the completeness of the database for elliptic curves over totally real fields [cite: 12]. The Langlands program—specifically through the modularity theorems generalized from the work of Wiles, Taylor, and others—predicts a strict correspondence between isogeny classes of elliptic curves over a totally real field $F$ and primitive Hilbert modular forms over $F$ of parallel weight 2, trivial character, and rational coefficients [cite: 12]. 

The LMFDB leverages this correspondence to establish strict completeness bounds:
1.  **Degrees 2 and 3**: Over totally real fields of degree 2 (real quadratic) and degree 3 (totally real cubic), it has been definitively proven that *all* elliptic curves are modular [cite: 12]. Consequently, the LMFDB's catalog of elliptic curves for these fields is deemed absolutely complete up to certain field-dependent conductor norm bounds, achieved by directly cross-referencing the rigorously computed database of Hilbert modular forms [cite: 12].
2.  **Degrees 4, 5, and 6**: For totally real fields of these higher degrees, unconditional modularity for all elliptic curves is not yet a fully proven theorem. However, the LMFDB guarantees conditional completeness: it contains elliptic curves matching *each* of the computed Hilbert modular forms (of parallel weight 2, trivial character, and rational coefficients) present in the database up to the specified conductor norm bounds [cite: 12]. Thus, the database contains all *modular* elliptic curves within these parameters [cite: 12].

By way of contrast to totally real fields, the LMFDB also catalogues Bianchi modular forms—the analogues of HMFs over imaginary quadratic fields. For imaginary quadratic fields with an absolute discriminant less than 100 or class number one, the database is conditionally complete up to a specific level norm bound, assuming the (yet unproven) general modularity of elliptic curves over imaginary quadratic fields [cite: 12].

## Algorithmic Breakthroughs Driving Future Completeness (2025-2026)

The primary barrier to expanding the Hilbert modular form database has historically been the sheer computational complexity of evaluating Hecke operators on spaces of forms defined over fields of higher degrees. In 1991, Bryan Birch proposed an algorithm for computing classical modular forms using the Hecke action on classes of ternary quadratic forms; however, Birch himself noted that his method frequently yielded only half the required information and failed entirely when the level of the modular form was not square-free [cite: 4].

A major leap forward in the 2025-2026 timeline is the refinement and implementation of a new algorithmic paradigm by mathematicians Jeffery Hein, Gonzalo Tornaría, and John Voight. In their June 2025 preprint, *"Computing Hilbert modular forms as orthogonal modular forms,"* they successfully generalize and expand upon Birch's foundational method to compute HMFs efficiently [cite: 4, 13]. 

This algorithm represents a profound shift in computational efficiency by translating the problem from the realm of complex analysis and $GL_2$ automorphic forms into the arithmetic of definite orthogonal groups [cite: 4, 14]. The Hein-Tornaría-Voight algorithm proceeds as follows:
*   It operates on a totally positive definite ternary quadratic space $V$ over the totally real base field $F$ [cite: 4]. 
*   By utilizing the even Clifford algebra $B := \text{Clf}^0(V)$, the researchers mapped the problem onto quaternionic modular forms [cite: 4].
*   Through the Eichler-Shimizu-Jacquet-Langlands correspondence, a Hecke-equivariant bijection is established between these quaternionic forms and spaces of Hilbert cusp forms [cite: 4, 15].
*   The algorithm computes Hecke operators via Kneser's theory of $p$-neighbors, which provides a highly effective method for computing the class set and Hecke action on algebraic modular forms [cite: 4, 14].
*   To solve Birch's original issue of missing forms, the algorithm utilizes characters defined by sign vectors (radical characters) to isolate the previously lost data [cite: 4].

The computational output of this algorithm is exceptional: it rapidly yields all Hilbert modular forms of even weight and trivial character, bypassing previous computational bottlenecks [cite: 4]. There is, however, one highly specific mathematical limitation to this algorithm: it fails to produce the complete space of forms *only* in the case where the totally real base field $F$ has an odd degree and the level of the form is a square [cite: 4]. Outside of this edge case, this algorithm is expected to trigger a massive expansion of the LMFDB's HMF database extending into 2026 [cite: 11, 14].

## Geometric and $p$-adic Perspectives on HMFs

While the algebraic computation of Hecke eigenvalues via orthogonal forms addresses the practical population of the database, deep theoretical work continues to contextualize these forms geometrically and $p$-adically, contributing to the "Knowledge" (`rcs.cande`) sections of the LMFDB [cite: 9, 10]. 

### Modularity, Geometry, and Shimura Varieties
The geometric realization of Hilbert modular forms occurs on Hilbert modular Shimura varieties. For a totally real field $L$ of degree $g = [L:\mathbb{Q}]$ and an ideal $\mathfrak{c} \subset \mathcal{O}_L$, the quotient space $Y_0(\mathfrak{c}) = \Gamma_0(\mathfrak{c}) \setminus \mathcal{H}^g$ is a complex orbifold of dimension $g$ [cite: 3]. The Baily-Borel compactification of this space, $X_0(\mathfrak{c})$, is a projective algebraic variety, but it suffers from severe quotient singularities and singular cusps [cite: 3]. The landmark 1953 work of Hirzebruch successfully resolved these cusp singularities for real quadratic fields, opening the door for the intersection homology theory of these varieties [cite: 16]. 

Recent developments documented in the 2024-2025 period have expanded on the period integrals of these varieties. Work by Goresky explicitly explores how the Fourier coefficients of a Hilbert modular cusp form with nebentypus can be expressed in terms of period integrals over Shimura subvarieties, providing a higher-dimensional analogue to the classic theorems of Zagier [cite: 3]. 

### $p$-adic Families and Characteristic $p$
The arithmetic geometry of HMFs also heavily relies on their reduction modulo primes $p$, and their interpolation into $p$-adic families. Based heavily on the foundational work of N. Katz on the geometric definition of modular forms, recent efforts by Eyal Goren and others have systematically developed the theory of HMFs in characteristic $p$ [cite: 17]. 

A major focus has been determining the ideal of congruences between HMFs modulo $p^m$. Goren's work established a canonical notion of "filtration" for HMFs, wherein a $q$-expansion modulo $p$ arising from a modular form actually originates from a modular form of minimal weight [cite: 17]. The q-expansion kernel modulo $p$ is generated by a set of relations derived from partial Hasse invariants, $h_i$, which are modular forms of weight $p-1$ whose divisor corresponds strictly to the non-ordinary locus of the moduli space of abelian varieties [cite: 18]. These partial Hasse invariants allow researchers to construct explicit $U$, $V$, and $\Theta_\psi$ operators in characteristic $p$, proving that ordinary eigenforms belong to prescribed boxes of weights and enabling the construction of $p$-adic L-functions attached to $p$-refined cohomological cuspidal HMFs [cite: 17, 19]. Such L-functions are pivotal in Iwasawa theory and are increasingly being targeted for inclusion in the "L-functions" section of the LMFDB [cite: 19, 20].

## The Oda-Hamahata Conjecture and Theoretical Confirmations (2024)

An exciting theoretical development intimately tied to the LMFDB's completeness criteria occurred in late 2024. The modularity of an elliptic curve $E/\mathbb{Q}$ is traditionally expressed geometrically by stating that $E$ is a quotient of the modular curve $X_0(N)$ [cite: 21]. However, for elliptic curves defined over number fields, this geometric notion diverges from the analytic notion of L-function modularity.

The Oda-Hamahata conjecture posits that for every elliptic curve $E$ defined over a totally real number field $F$, there exists a direct geometric correspondence between a corresponding Hilbert modular variety and the product of the Galois conjugates of $E$ [cite: 21]. In a November 2024 preprint titled *"Rings of Hilbert modular forms, computations on Hilbert modular surfaces, and the Oda-Hamahata conjecture,"* mathematician Adam Logan proved this conjecture via explicit computation for numerous cases where the elliptic curve is defined over a real quadratic field and the geometric genus of the resulting Hilbert modular variety is exactly 1 [cite: 21]. This result provides strong geometric validation for the pairing of HMFs and elliptic curves utilized within the LMFDB to verify completeness bounds [cite: 12].

## Future Milestones: Conferences and Infrastructure (2025-2026)

The momentum of computational number theory in this era is heavily supported by dedicated global collaborations, workshops, and grant-funded initiatives. The Simons Foundation, the US National Science Foundation, and the UK Engineering and Physical Sciences Research Council are primary benefactors maintaining the servers and funding the researchers building the LMFDB [cite: 6]. 

Several key events in the 2024-2026 window dictate the pace of updates and the expansion of the completeness bounds for the HMF database:

1.  **Simons Collaboration Annual Meetings (SCoAGNTaC)**: The Simons Collaboration on Arithmetic Geometry, Number Theory, and Computation held its annual meeting in January 2025 [cite: 22]. The summit explicitly addressed the future growth of the LMFDB [cite: 22]. During the meeting, researchers presented on explicit inverse Galois theory utilizing Hilbert modular forms (Sam Schiavone), and John Voight detailed the past, present, and future trajectories of computing modular forms for the LMFDB [cite: 22].
2.  **LuCaNT 2025**: The second conference on LMFDB, Computation, and Number Theory (LuCaNT) took place at the Institute for Computational and Experimental Research in Mathematics (ICERM) at Brown University in Providence, Rhode Island, from July 7–11, 2025 [cite: 23, 24, 25]. The conference featured presentations directly impacting the HMF database, including talks by Haochen Wu on deriving Hilbert modular forms from orthogonal modular forms on binary lattices [cite: 26]. The proceedings of this critical conference, edited by John W. Jones, Jennifer Paulhus, Andrew V. Sutherland, and John Voight, will be published in June 2026 as Volume 840 of the American Mathematical Society’s Contemporary Mathematics series [cite: 25, 27]. 
3.  **LMFDB Workshop 2025**: Hosted at MIT in Cambridge, MA, from July 14-18, 2025, this workshop allowed core developers to directly implement the algorithms discussed at LuCaNT, pushing updates to the Python backend of the site, establishing new completeness bounds in `rcs.cande.mf.hilbert`, and integrating the newly generated orthogonal modular form data [cite: 23].

## Open Problems and Continuing Work 

As the calendar moves toward 2026, the LMFDB stands as an unparalleled achievement in collaborative mathematics. However, the work on Hilbert modular forms is far from finished. While the Hein-Tornaría-Voight algorithm has solved the computational impasse for the vast majority of totally real fields, the specific mathematical blind spot—odd degree base fields with square levels—remains a target for future algorithmic innovation [cite: 4].

Furthermore, the integration of related mathematical objects is ongoing. Researchers are currently utilizing HMFs to map Hypergeometric Motives and Ramanujan’s alternative bases, connecting special values of L-functions of CM Hecke eigenforms to multi-dimensional Galois representations [cite: 28]. Computations of Stark-Heegner points (conjecturally algebraic points on elliptic curves) and Gross-Stark units via analytic theta cocycles on the $p$-adic upper half-plane are also expanding the scope of what data can be attached to the home pages of HMFs within the database [cite: 29].

In conclusion, the 2024-2026 period is characterized by explosive growth in the Hilbert modular forms database within the LMFDB. Driven by the translation of GL(2) automorphic challenges into the computationally tractable realm of orthogonal modular forms on ternary quadratic spaces, the database is rapidly approaching a state of high completeness for low-degree totally real fields [cite: 4]. Certified by geometric theorems bridging abelian varieties to Shimura surfaces, and supported by rigorous metadata tracking (`rcs.cande.mf.hilbert`), the LMFDB continues to fulfill its mission as the modern, definitive periodic table of the Langlands program [cite: 6, 10, 11, 21].

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0ReY1Ilas02Rby1OwODM0uOy76aJxTG6eWKgP40u6E3gqZrAV_-JLF0M3QO3PhBKt6yHcxxuZS3Ch5xRJYLqqUfnv3sEuQkb4H6iCCSMxFMlrpS9GxGzQ4A==)
2. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlZmFWUN0MIZuGqyRR6Nd1zlg5d2Ec4Dr7nNPVk5of1cAdGq4e5xnpmece63Lhly3nKHB6hfdwGONzBdrakOLIeXHu2d2dtvW74BmzRFEcI6BVmt2urKy0QqYmqNnHlKKzGohaUg-Tw1rkF260kkXmYVa-i9Stl8ef)
3. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWlJur_giP0_1aLOtKWi_N-Nt3vcKw3fuf2iSHSPP4Iuz3QyvV_SXqh-Z6lQVSZ7yInTJTRGcSpfsuqglIBlBXWpn8mbJ7EG136gemNE0P_R8o_JqW3bUWl5C8mQWPL-sCEJpHj6c=)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbwxyG1xjjQK6BBWPh8v1Q7cCkKRSp2NUuKnOqWhO6erLQGiVvbEK3P8w-1o2KtemAvx3tAIlekwSBnkAnTYigDEMwohe-yca5CTbfZdxjU3bxaLkbvQ==)
5. [lmfdb.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDL_ql_701XRSUTlkZlBKbv1CT9FmQSS5s2DqnapV4nnYZg0H5YAQc3aiGBDqrQoabWWZPw5iKdqSTbnUoDD8ECrN1--g96IFaViKfK7ALJTsohWBUUu0eghSmE9s9APhi26ZE_aCCpA==)
6. [lmfdb.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUPZQpKPph1xRKtR74FMwXmN1DndO9qdFe1hAGKp4XKLQMr2glycrcTKdYQILdOQ_E67fn3cogMfSIqZOIgkb2qoWa2QQnBsbP8Meh)
7. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGx54rfM8hpCZbDnvHkwNCWyfvm8Gr1a-X4rdL4oe7fSIozsj5tGLlHRWVzUCAWz36F7acj4VS8LB3qa7_FEZraROcmjo_g7bfVJ8QJ3P8QCreqYT0=)
8. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTYDgRtqzrz-WZm3rWrjgMLBN6E45ODLuAyf9eaOws1tpDD_LNWrCq4t_r5_rWRAI12CHfcUCQGTq3NNNahSpAtl0xhbxuJ4MOZvl5Hd3i0VyH5uSHAD7HRJh9fby4)
9. [lmfdb.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcLMX9cRpwQ3Oj0pX-yxWLck3-cGXszqVFcDH0ZuT6v4vKCzaxNoxg-G8Q0nfkWvriyRSduLlPoHMuGFeBUxxj67hcmAMZWOgEZY5N6IvwqEWodRHX_8UYtyIq5g-Q)
10. [lmfdb.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxvkAC-UBJzhUgfYVJGjpqi7xhL9IAfY0ooe5qfkRdskrLQFNHXZ_BRGPD6HeCnznJT6Mq75UMLbJe84E-j46XGwZCqw6RqY53S5pHG9e7S4eaSs5okg==)
11. [asu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQlCkGKE1kT_lVuREmHdgG2Q1gvIgcxwkXl80Sm_4C2P-37G2AkfD-F65KwO7bvaIBleNnsGVNRXL9TGGJ-wR6eDVL3bJJI2EGbraembVh3eQaQ-2sVyjg7Lv0iT-xw88ug5aGC3q_6yQ5tTUBLOFWcZN4vB9boIlqmpOuBnyryYu96aAb52wg6Fxn)
12. [lmfdb.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-_4aZfBnDKZ3YQ3GjQSTdTvkStT1Q96n2odVTMh2EIfHB-LUmoZ5Av9AtY6MZDO_Oi1TOZmeA2BUh85VVg4Zvi3yFo9kPuC09037fRPxXGNbnqi0EgT0fa-1GfdlgK7LyW6dHIuU=)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgzXA6D-fBDE8kD8KpsJ2PT4bc4ZmaMOXyO-aa7tJVhWoXUkemxKEEX846W4nqlB2YctKgHADHhMql5VA5yf_s1RijuXeVXSbBSPF-ei0jzImtcq2UMg==)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzMRLlaed_rFQECm7Oe5RY-5uAWy6bSHF8nF-LCQp-IN4yRzsR1MUqf43a_97xFqQ9g5voIkRrWX8Rvb5uxyw4JD_z2t5vXEOsW47MIAR23SwcPhsdXiM06qUY6Czs06tVjzaDgPv652eCJaURo-Hk2Pr5cIrhnfKcN9ei5Kxm7w==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXESJ1LidntHDBaRl215TdFMDWnqDIFnEK197nAEMrIqg_5tNZMo0aJy7NXVQMHTRuELXqtxhF_El4fE6RL6roEDHrXEXVK9C0LyqXmyBykbZhywzMzw==)
16. [canterbury.ac.nz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-TENJHers3W299cmp21Uz5diUM_7PIh_wH_hHMbmuIUSydHixW5Aqba_IJWylG57be6Eztt8gnisIoDAghfZDj6u2UrO1N__c914eddEcEimueMknpnJcKIEe0_5yaJ26-j6b3Ovrzd19U3BgC8FesD-E3c8Wxwrbr6qVE65b7P9fWB0=)
17. [mcgill.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMC2cPvfvNAINqM74Ab-TjS5lygS_BkcxG_aElFuxUPJMw9jGTDhGWwuKOUYmHwxad1-m3AN-I4T1DdGY6PUpePm80-aQYIaX0gIbl102FgFoWagnxO8gTsSoVcLZMuTAfuYeRP4qgTFfZ-mq9tCeqIYX9Bw==)
18. [wstein.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHof1IM_mhDMgVhKlbhP9bOlVO06trbKccy6yZwk8yqwhVA_8JOz0T1ijc7Dr6qHVwiIzLHB_bCbm6Teb3cQSIGVqpNMjyqIN31zXi8hqR-6J_6hmuyz7ebUWmRpNj4YJezaFjiiac=)
19. [davidrenshawhansen.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4Lrp7EPFE-CaHyY5ju8plcetXVuHaU2-IIZ7xEngWi4cJDFz_Xgsn1R41Jr6fzQhF8Vy3OOVZys_XfbzxH18GbuMQQx7hE4ismr8NRrDLb8DTbMmx26xbhTr3Tpt4sWU=)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHS6tNlXLaWcRogd-6q7a_5hwzkwrMGvnGCjuNFXDAm0svUCx53SQKr13ZFBWVCnmQJ1qtbbkf5VNNiNQ8C3WPElnjUKs9DUjkEIOqVOJfXgc3oyxrNKBluOcy0uhND5sRqQ_9KL4wywh2Hnb6A9nclueiXCQR1NHWd7p67NgBeu1eO)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEd4-h999qcUZmF59c4qbYO1H3P8tMBaX9InSySFa9czQ0V8SAyP09GUpXOixA7ClqJ08S0Z9XgqlC1eRuww70oZn5p8XEiSfYITQkWZyX29V4QkpyYyQ==)
22. [simonsfoundation.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmhR7XSPwuLL72BPNvpFiehlO4N3Imjuli5Lnlr8gnQ-h479QOa14inD3axA560FRVbyPxRgX0jX0p5TXdQDTS4tlNE_recFmPYqxmA5T5RwD7pcs1a04VM0AMy3RLnKRy8S7QBtmvnEeZ08l3AFLw2aQ7wq6vGSaWlk26hV16QnmfFTfWff1Ejvu9ffRXCUTjQ1zjOmDeuy1CBIbqvQ7kx5OVxjMfDBXu2zQMKJBX4WRqkeT7Zad1HOcUWQ==)
23. [lmfdb.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFHklTlqVpvaKHuZ1M0YNAgmmq7IZq2Xo-3RBjJoyS-OuBX8yt0IZlp6biNa4o5ASBHuOzVKuJfj1fJnJ4gWe_Wd5QO_jA6HZ_-ctES5RET2KOZ3nsGt18sULpazZ8OR6ZqCtv_g==)
24. [lucant.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnQTPdnpfOtTROviqihItSleffcmTMryEtaK_fy3TKVBIQdOiXC2G8WGnvb9cD6KI8LGKxifJShEPnSTfZxod6iZgDDe4knQed)
25. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtOpsz88VVmx1xaZ6OKoLn9v3dD5f0Phwa5yn-8M6WoexBdqWV2nnFFUytwNKrgg_gEv9JVxREQ0v2JOP6L43J1b4DmyVrcjptVTMx0kv2NcHTJnipLdaLYNS26MTlpGXV6XIZVrp7qpM46Pe8460ZvxK5lfTf)
26. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHc6AvOkWxtL5wiByMawypsPsfnVM_Slx95etwY8C_yBJzCfS_9tWtbScukgBJp2pZlcmP7G2KIiih56w0vjrG43WBze5mIHGjHNwB0ZwKSVhv8n_b3-7bk-3GvdDZne_kbPtjwjxPb1UMnWNHX-TTzY2KB)
27. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGiQSgcLzrNV1LyQ_1J3E6wSDldHtqG5sm7XvqglE9cnqZL5S_glIu2AraASPu6ni5wd3nBQQLk0qv8z2wq_CV2uL8JUZSp4Ebjl83_Y1DsEjYBw3kozVNz4KzdOvNU2cN0glA=)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeJKHJ0nbhit5vwvXeMZxT66qMiNg95gH41r5XCglZ9AfI6twSgu1Xvf4KKD4qwLmLb0XfMA5TesuA89DJs59MPpuVUT3qRpP3yMJGB6UeIJErE-kHqg==)
29. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2hqFTT2gWPf75iqVh2PXaSHXUS9rhRppej6e-mlIX1yATQU3s_8pBe-DYe9nCb-_UHVlqwqRrDrt4fDrpeQzTKI_bYOjDekA7gO--OdIYygLenqd08bvJKVM01U9HV5q3)

