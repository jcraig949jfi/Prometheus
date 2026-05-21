# Stable trace formula / Arthur classification 2024-2026 frontier

**Pythia queue id:** 196
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdHMElQYW9hWUZjTGRfdU1QdnJfYmlRcxIXRzBJUGFvYVlGY0xkX3VNUHZyX2JpUXM
**Elapsed:** 250s
**Completed at:** 2026-05-21T17:38:30.286654+00:00

---

# The Frontier of the Stable Trace Formula and Arthur Classification: 2024–2026 Developments

*   Research between 2024 and 2026 has significantly advanced the understanding of **weak local Arthur packets**, successfully characterizing them via microlocal geometry and wavefront sets, and proving their unitarity for split classical groups.
*   Major breakthroughs in the **relative trace formula** include the proof of the endoscopic fundamental lemma for unitary Friedberg–Jacquet periods, paving the way for the twisted Gan–Gross–Prasad conjectures.
*   Analytic applications of the trace formula have yielded new bounds on **limit multiplicities** and Harish-Chandra–Howe coefficients, directly connecting the Gelfand-Kirillov dimension to the decay of matrix coefficients.
*   Progress on **Jiang's conjecture** has established robust upper bounds for the nilpotent orbits in the wavefront sets of representations in local Arthur packets, generalizing Shahidi's conjecture.
*   Diophantine analysis has been integrated with the stabilization of Arthur's trace formula, yielding novel asymptotic formulas for integral points on homogeneous spaces utilizing **\(\kappa\)-orbital integrals**.

### Overview of Recent Breakthroughs
The Langlands program is a vast network of conjectures connecting number theory, algebraic geometry, and representation theory. A central pillar of this program is the Arthur-Selberg trace formula and its stabilized variant, which allows for the comparison of automorphic representations across different reductive groups via endoscopy. The 2024–2026 period has witnessed a surge of technical advancements in this area, particularly regarding the internal structure of Arthur packets, the stabilization of relative trace formulas, and the arithmetic applications of spectral geometries. These developments have successfully bridged abstract representation theory with concrete Diophantine and analytic problems.

### The Scope of the Frontier
This report provides a comprehensive examination of the frontier of the stable trace formula and the Arthur classification of automorphic representations from 2024 to 2026. It explores the foundational extensions of the classification to inner forms and symmetric spaces, delves into the resolution of conjectures surrounding weak Arthur packets and wavefront sets, and analyzes the application of these frameworks to limit multiplicities and the distribution of prime numbers. The report is structured to guide the academic reader through both the spectral and geometric sides of these recent mathematical milestones.

## Introduction to the Langlands Program and Trace Formulas

The Arthur-Selberg trace formula is an equality between two different expansions of the trace of an operator acting on a space of automorphic forms. On one side, the geometric expansion is expressed in terms of orbital integrals parametrized by conjugacy classes of elements in a reductive group. On the other side, the spectral expansion is given in terms of traces of the operator on irreducible automorphic representations. The stabilization of this formula, achieved in the foundational works of James Arthur, Robert Kottwitz, and Ngô Bảo Châu (who proved the fundamental lemma), reorganizes the geometric side into stable orbital integrals, which are invariant under stable conjugacy. This stabilization allows for the precise comparison of trace formulas between a reductive group \(G\) and its endoscopic groups, leading to the principle of endoscopic transfer [cite: 1, 2].

Between 2024 and 2026, research has shifted from the existence of the stable trace formula to its profound refinements, relative variants, and boundary cases. While Arthur's monumental work established the local Langlands correspondence for symplectic and quasi-split special orthogonal groups over local fields of characteristic zero [cite: 3, 4], extending this classification to non-quasi-split inner forms, exceptional groups, and symmetric varieties has remained a critical frontier. The recent literature demonstrates that the synthesis of microlocal geometry, perverse sheaves, and harmonic analysis is essential for unpacking the remaining mysteries of the automorphic discrete spectrum. 

## Refinements of Arthur's Classification and A-Packets

Arthur's classification organizes the discrete automorphic spectrum of classical groups into specific multisets called **global Arthur packets**, which decompose locally into **local Arthur packets**. A local Arthur parameter is a continuous homomorphism:
\[ \psi : W_k' \times SL_2(\mathbb{C}) \times SL_2(\mathbb{C}) \to G^\vee \]
where \(W_k'\) is the Weil-Deligne group, and \(G^\vee\) is the complex Langlands dual group [cite: 4, 5]. The representations within these packets are parametrized by purely geometric data associated to nilpotent orbits in the dual group.

### Extensions to Inner Forms and Exceptional Groups
A persistent challenge has been extending Arthur's classification beyond quasi-split groups. Recent work by Hao Peng has addressed the stable trace formula and the theory of endoscopy for even special orthogonal groups, specifically \(SO(2n)\) [cite: 3, 6]. While Arthur's original classification for quasi-split even special orthogonal groups was given for irreducible representations of \(SO(V)\) up to conjugation by \(O(V)\), Peng's framework works directly with \(SO(2n)\) to establish compatibility between the Fargues–Scholze local Langlands correspondence and the classical local Langlands correspondence [cite: 3, 6]. Peng's methodology assigns a "theta packet" via theta correspondence, consisting of \(O(V)\)-conjugacy classes of irreducible unitarizable representations, achieving an endoscopic character identity for \(G\) [cite: 3, 6].

In the realm of Siegel modular forms, Yamauchi and Dalal have utilized Arthur's invariant trace formula to study equidistribution theorems for families of holomorphic Siegel cusp forms of general degree [cite: 7]. Their research estimates unipotent contributions in the geometric side of the trace formula uniformly, utilizing Shintani zeta functions. Crucially, they demonstrated that "nongenuine forms"—forms originating from nontrivial endoscopic contributions via Langlands functoriality from smaller groups—are statistically negligible in the level aspect [cite: 7].

Further insights into the Arthur classification have been provided by Linus Hamann, who examined the global automorphic representations of \(GSp_4\) and inner forms [cite: 8]. By analyzing the discrete part of the stable trace formula, Hamann distinguished parameters based on the number of supercuspidal members in the associated L-packets, contributing to the strong form of the Kottwitz conjecture for \(GSp_4/L\) and \(GU_2(D)/L\) [cite: 8].

## Weak Local Arthur Packets and Unipotent Representations

One of the most active subfields in 2024–2026 has been the formalization and structural proof of **weak local Arthur packets**. While standard local Arthur packets are constructed using endoscopic transfer, they do not always partition the set of smooth irreducible representations, and they are sometimes not disjoint [cite: 9]. To organize this complexity, researchers drew inspiration from the representation theory of real reductive Lie groups (such as the Adams-Barbasch-Vogan geometric construction) to study unipotent representations with cuspidal support [cite: 5, 10].

### Definition and Geometric Construction
Motivated by the theory of real local Arthur packets and utilizing the wavefront sets of representations over non-Archimedean local fields, Ciubotaru, Mason-Brown, and Okada defined weak local Arthur packets [cite: 4, 11]. These packets consist of irreducible \(G\)-representations whose Gelfand-Kirillov dimension is minimal among those admitting a given unipotent infinitesimal character \(\chi_{\mathcal{O}^\vee}\) [cite: 12]. A weak local Arthur packet, denoted \(\Pi_{\psi}^{\text{Weak}}\), is formed by applying Aubert-Zelevinsky duality to all representations parametrized by local systems on orbits within the special piece of a unipotent conjugacy class \(\mathcal{O}^\vee\) [cite: 5].

### The Weak Arthur Packets Conjecture
The central conjecture posed by Ciubotaru, Mason-Brown, and Okada asserts that every weak local Arthur packet is a finite union of genuine local Arthur packets [cite: 4, 11]. Between 2023 and 2025, Liu, Hazeltine, and Lo, alongside independent work by Gurevich and Okada, proved this conjecture for split classical groups, specifically \(Sp_{2n}(F)\) and split \(SO_{2n+1}(F)\), assuming the residue field characteristic is sufficiently large [cite: 4, 11, 12]. 

This proof has profound implications:
1.  **Unitarity**: The theorem guarantees the unitarity of the unipotent representations that constitute these weak Arthur packets [cite: 4, 11].
2.  **Ramification and Sphericity**: Gurevich and Okada demonstrated that the fine composition of weak Arthur packets is governed by the partition of the unipotent locus into special pieces [cite: 12]. They showed that "weak sphericity"—the property of containing vectors fixed by a maximal compact subgroup—matches precisely with representations belonging to Lusztig's canonical quotient spaces [cite: 5, 12].
3.  **Generalization to Anti-Tempered Parameters**: By replacing the geometric wavefront set with the canonical unramified wavefront set, the researchers generalized the structure to anti-tempered local Arthur parameters [cite: 11].

## Wavefront Sets and Jiang's Conjecture

The **wavefront set** is a critical geometric invariant of an admissible representation, measuring the singularity of its character distribution at the identity. For a representation \(\pi\), the geometric wavefront set is defined as the set of maximal nilpotent orbits \(\mathcal{O}\) for which the twisted Jacquet module (or Fourier coefficient) is non-zero [cite: 4, 13].

### Bounding the Wavefront Set
A major theoretical bridge linking the local Arthur parameters to explicit harmonic analysis is Jiang's conjecture. Proposed as a natural generalization of Shahidi's conjecture (which states that tempered L-packets of quasi-split groups have generic members), Jiang's conjecture posits that the wavefront sets of representations in a local Arthur packet \(\Pi_\psi(G)\) possess a natural upper bound completely determined by the local Arthur parameter \(\psi\) [cite: 14, 15]. 

Significant progress on this frontier was published between 2024 and 2026. Dihua Jiang and Baiying Liu successfully proved the upper bound for Fourier coefficients of automorphic forms in Arthur packets for all classical groups over any number field [cite: 13, 16]. Their work establishes that:
*   The structural bounds on the wavefront set are controlled by the endoscopic classification and the associated induced unipotent orbits [cite: 13].
*   Under specific assumptions, the enhanced Shahidi conjecture holds true, proving that local Arthur packets of quasi-split groups contain a generic member if and only if they are entirely tempered [cite: 4, 15].
*   For split classical groups (\(Sp_{2n}, SO_{2n+1}, O_{2n}\)), the wavefront sets of the unramified unitary dual can be explicitly computed under the assumption of the closure ordering conjecture [cite: 13].

Further independent research by Baiying Liu and Freydoon Shahidi has partially proved Jiang's conjecture by confirming the relation between the structure of wavefront sets and local Arthur parameters via the matching method of endoscopic liftings [cite: 15, 17]. By applying the character identities of local Arthur packets, the researchers reduced the study of the upper bound to the properties of wavefront sets of the corresponding bi-torsor representations of general linear groups [cite: 17, 18]. 

### The p-adic FPP Conjecture
Related to the wavefront geometry is the p-adic FPP (Filtered Positivity Property) conjecture. Assuming that \(G\) is a pure inner form to a quasi-split group and the local Langlands conjecture holds, Jiang, Liu, Lo, and Mason-Brown (2025) provided a framework establishing weak dominance for the co-roots associated with the unitary dual [cite: 14]. This arithmetic wavefront set methodology provides a precise calculus to explicitly determine \(\text{WF}(\pi)\) for any \(\pi \in \Pi_\psi(G)\) when \(\psi\) is generic [cite: 14].

## The Relative Trace Formula and the Endoscopic Fundamental Lemma

While the standard trace formula deals with the \(G(F) \backslash G(\mathbb{A})\) spectrum, the **relative trace formula (RTF)** introduced by Jacquet allows mathematicians to study the "periods" of automorphic forms. The nonvanishing of such periods is intimately tied to special values of L-functions and Langlands functoriality, most notably formulated in the Gan–Gross–Prasad (GGP) conjectures [cite: 19, 20]. 

### The Endoscopic Fundamental Lemma for Unitary Periods
A historic bottleneck in the stabilization of relative trace formulas has been the proof of the fundamental lemma for symmetric spaces. In a landmark 2025 publication in the *Annals of Mathematics*, Spencer Leslie proved the **endoscopic fundamental lemma for the Lie algebra of the symmetric variety** \(U(2n) / U(n) \times U(n)\), where \(U(n)\) is a unitary group of rank \(n\) [cite: 21, 22]. 

This symmetric space represents the first major step in the stabilization of the relative trace formula associated to the \(U(n) \times U(n)\)-periods of automorphic forms on \(U(2n)\), commonly referred to as **unitary Friedberg–Jacquet periods** [cite: 22, 23]. Leslie's methodology involved:
1.  Reducing the problem to the tangent space at the \(H(F)\)-fixed point, identifying the geometry with \(\text{End}(V)\) [cite: 23].
2.  Developing a new comparison of distinct relative trace formulas to establish smooth transfer via a globalization argument [cite: 23].
3.  Defining relative stable orbital integrals and transferring functions matched in terms of Hironaka and Satake transforms [cite: 24, 25].

### The Twisted Gan-Gross-Prasad Conjecture
Building upon the endoscopic fundamental lemma, a collaboration between Spencer Leslie, Jingwei Xiao, and Wei Zhang culminated in a sequence of preprints (2024–2025) successfully utilizing the RTF to prove the **twisted global Gan–Gross–Prasad conjecture** for \(U(V) \subseteq GL(V)\) [cite: 26, 27]. 

Their breakthrough establishes a global conjecture for the automorphic period integral associated to symmetric pairs defined by unitary groups over number fields, generalizing Waldspurger's toric period theorem for \(GL(2)\) [cite: 26, 28]. A highly novel feature of their approach is the integration of **relative endoscopy** into the RTF comparison. By comparing global representatives, local distributions, and nilpotent orbital integrals, they established geometric decompositions of relative trace formulas using normal representatives via Galois theory [cite: 20]. Their work proves the twisted GGP conjecture on Asai L-functions in any dimension under certain local unramifiedness assumptions [cite: 20, 27].

Table 1 summarizes these critical advances in the RTF:

| Research Focus | Authors | Symmetric Space / Group | Key Contribution |
| :--- | :--- | :--- | :--- |
| Endoscopic Fundamental Lemma | Spencer Leslie | \(U(2n) / U(n) \times U(n)\) | Proved the fundamental lemma for the Lie algebra of the symmetric variety, enabling RTF stabilization [cite: 21, 29]. |
| Relative Satake Transform | Spencer Leslie | Jacquet-Rallis Transfer | Formulated a relative fundamental lemma for a relative spherical Hecke algebra [cite: 30]. |
| Twisted GGP Conjecture | Leslie, Xiao, Zhang | \(U(V) \subseteq GL(V)\) | Proved the twisted global GGP conjecture on Asai L-functions using relative endoscopy [cite: 20, 27]. |

## Asymptotic and Diophantine Applications of the Trace Formula

The structural rigidity provided by the Arthur classification and trace formulas has birthed a new generation of analytic results, pushing the boundaries of asymptotic representation theory and Diophantine geometry.

### Limit Multiplicities and Cohomology Growth
Mathilde Gerbelli-Gauthier's recent work utilizes Arthur's stabilization of the trace formula alongside the endoscopic classification by Mok, Kaletha, Minguez, Shin, and White to derive upper bounds on **limit multiplicities** for non-tempered representations of unitary groups \(U(a,b)\) [cite: 31, 32]. 

As the level of a principal congruence subgroup \(\Gamma(\mathfrak{p}^n)\) grows, the multiplicity of a cohomological representation \(\pi\) in the regular representation of \(G\) on \(L^2(\Gamma(\mathfrak{p}^n) \backslash G)\) governs the growth of the Betti numbers of the corresponding locally symmetric spaces. Gerbelli-Gauthier achieved uniform upper bounds on the limit multiplicities of specific cohomological representations, verifying instances of the Sarnak-Xue density conjecture for groups that do not contain a \(U(2,2)\) factor at infinity [cite: 32, 33]. 

Furthermore, her 2025 research establishes a direct, quantitative relationship between the Gelfand-Kirillov (GK) dimension of a unitary representation \(\pi\) of \(p\)-adic \(GL_N\) and the rate of decay of its matrix coefficients [cite: 34]. By providing uniform bounds on the Harish-Chandra–Howe coefficients via the Langlands and Zelevinsky classifications, she solidified the analytic invariants required to perform spectral-side bounds of stable trace formulas [cite: 34]. 

In a joint work with Rahul Dalal, Gerbelli-Gauthier also investigated the root numbers \(\epsilon(1/2, \pi)\) of self-dual cuspidal automorphic representations of \(GL_{2N}/F\). While orthogonal representations identically have a root number of 1, their research proved that for symplectic representations, the root numbers equidistribute between \(\pm 1\) as the infinitesimal character \(\lambda \to \infty\), provided the conductor is sufficiently ramified [cite: 35]. This result represents a highly sophisticated application of the endoscopic classification and Arthur's trace formula to statistical families of \(L\)-functions.

### Diophantine Analysis and \(\kappa\)-Orbital Integrals
Yuchan Lee's 2025 research successfully applied the pre-stabilization mechanisms of Arthur's trace formula to classical Diophantine counting problems. Lee considered a homogeneous space \(X \cong G_\gamma \backslash G\) over a number field \(k\), where \(G\) is a simply connected semisimple group and \(G_\gamma\) is an anisotropic maximal torus [cite: 36, 37]. 

Lee formulated an asymptotic formula for the number of integral points on \(X\) bounded by a fixed norm \(T\) as \(T \to \infty\). The novelty of this approach lies in expressing this asymptotic growth entirely in terms of **\(\kappa\)-orbital integrals**, which are the fundamental building blocks in the stabilization of the geometric side of the trace formula [cite: 36, 37]. Because the asymptotic formula coincides directly with the contribution of the stable conjugacy class of \(\gamma\) to the trace formula, Lee was able to deduce general Euler-product deviations and compute exact asymptotics for the number of \(n \times n\) integer matrices with a fixed characteristic polynomial, expanding dramatically on the classical Eskin-Mozes-Shah theorems [cite: 36, 37].

## New Perspectives on Explicit and Twisted Trace Formulas

Beyond stabilization, efforts to make the trace formula explicit or to alter its convergence properties for specific groups remain highly active.

### The Coarse Trace Formula for GL(4)
A known difficulty with the general Arthur-Selberg trace formula is that the geometric and spectral terms diverge, necessitating Arthur's complex truncation operator to define convergent distributions. In 2025, Haoyang Wang published an explicit derivation of the **coarse trace formula for \(GL(4)\)** [cite: 38]. Wang's analysis circumvented standard truncation by proving that the divergent terms on the geometric and spectral sides of the \(GL(4)\) trace formula are identically equal, thus cancelling out. Wang also obtained explicit formulas for the ramified orbits on the geometric side, paving the way for highly computationally effective trace formulas for low-rank groups [cite: 38].

### Beyond Endoscopy and Rigid Inner Forms
Tian An Wong has expanded the "Beyond Endoscopy" paradigm utilizing weighted stable trace formulas and primitive trace formulas for \(GL(2)\) over number fields via Poisson summation [cite: 39]. His research focuses on smoothing the singularities of elliptic orbital integrals to isolate non-endoscopic functorial transfers [cite: 39].

Simultaneously, Tasho Kaletha has constructed a rigorous global framework for **rigid inner forms** via fpqc gerbes over global function fields [cite: 2]. Kaletha's cohomology \(H^1(\mathcal{E}_{\dot{V}}, Z \to G)\) provides a bridge between refined local endoscopy and classical global endoscopy. This formalization proves expectations originally held by Arthur regarding the decomposition of the adelic transfer factor \(\Delta_{\mathbb{A}}\) into normalized local transfer factors, cementing the explicit pairing between adelic L-packets and their corresponding component groups [cite: 2].

## Conclusion

The 2024–2026 frontier of the stable trace formula and the Arthur classification has been characterized by deep structural synthesis and arithmetic application. Representation theorists have pushed the boundaries of Arthur's initial quasi-split local classification, establishing the geometry and unitarity of weak local Arthur packets through wavefront sets and microlocal perverse sheaves. In tandem, the geometric side of the trace formula has seen historic resolutions, notably the proof of the relative endoscopic fundamental lemma for unitary symmetric spaces, which effectively unlocking the twisted Gan-Gross-Prasad conjectures. 

Concurrently, analytic number theorists are wielding these stabilized formulas with unprecedented precision. The ability to bound limit multiplicities, dictate matrix coefficient decay via GK-dimensions, and count integral points on homogeneous spaces using \(\kappa\)-orbital integrals highlights the robust utility of Arthur's trace formula. As researchers continue to refine the explicit trace formulas and trace the contours of Beyond Endoscopy, the unified vision of the Langlands program continues to coalesce into a concrete, calculable reality.

**Sources:**
1. [dntb.gov.ua](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQHHMMR-H9sHvIo5FkA77KLTltB8X1_LjkHBDC3Fo6cEoRRynpJGxmSJQxM4H5Yy8APTlXEe4T1Wqx5pgw5BG1EjqBSFexJlr95ZYEhYGTZhpLhIi2kcXYstKD1td9EKYV)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGINH8spEUWuaiEleHP0IOZZgJ4P96bE538GQgVoEnzPI7wVX-Mp5QGYxSLiIPNXmBCsIuVUI8k-pFQvWtgwRO9bIzrfzAltzoWHF6Eao5sk1z5RwMzzX8nZjZus02xzMKzztPx3TOQZMAXRnIRx7tvJPMnbYmM5ZLA8qVu06ED7eeR8sF0ZXdo9_YMz-bZP14TVj6D1m7jXbQvkL4MvsTAq_zb8g-_sYY=)
3. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHflFw7iQeahwy8n2hwetBNElbMWBXb92ExFQm8-svQNUNVP3c8aDMqScgu9UWQrhIZ162NGPTuu5O1pZBmWLGpE-u4PAr_VL-HCs1UJMcZBuyEZHpB-oFNO20tbSNiuUCesSx167w6pmZzFk=)
4. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1JdffvvkEDBOimuqBipfpDNs-kxiJJ6uXw5xIYY5-H3a4elMT77KauUkIKLzJCFvYvieJKH7bPO7RRlBVTinJVTHISjJAm7wW69qsBHsBUO6QVGuGYAyY6Kz45kNoBfs=)
5. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElyvRak6Ryu36QDr6waZDYR-c4IiWR-IccoOSagAOlNURrz7CtC8NOP_Ve9-HPYdF7EMZvJN0ux2j8J_fwOS0IDTd6_-Xk8cH-OkxSrwxa53mu0j9j-rsHf-DYqoa-lkn5z4_82PSlzyXDpSzPjgIEbLZmHt1DQ9xdwbQaibenS-eRBscZTCZNKg==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9PL34Kebm3sqx2cUVZaId96zYFbowEFXlBiO_D7YAX7bIwDubB7CzGp74Ly1jps6sjtW5MCgzRIxm0jYQ5oZYfWeTPfDlKk8nbIWPudFcp0Qoky4F_o254Q==)
7. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUVUA07rOo-CBx6CO6rWtQBUSnmdva4csvKcwxsGYmOZOuM_C0rqKIu56lQUr8bnfnq4SLZH9G-CUKx9kr67RS3NJ8Tio3AkE-EgN2juEBelCiVhAGeW0dAvXgq3u6G8RKe0Bhb028Rw==)
8. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJKTVg3SfCBCZcP5L9gHWYTri4ySb7Zqd4dTdYam8FaAV9_P0iWxrXkYnoDhhj6vh_0DEGnuH8AKfmXR67cJQIvZDQAynNdqgJoE7b2VwaA0g0iWK_BTw6-USBiTJhhXFvz7cyw001_sL6ZRri1dQ=)
9. [umdearborn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGU0950wUEAqdEj0ql4-AaKtYuHCfcBFt7uJErI2FuARkcdKee945N8z9Por6krpZIR1pNWJGse5vzWvaj4hlvsOXf_vbARWkmDgjtDF1o1c8oVVNpGt5SCcIC8-RTchBrlO5IymT3sXUI8WCokYcva4_YR7GgrFUDWleVrviaXNLyvgbjTWEs1DNgu0w5_Bk1xkg==)
10. [emileokada.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEkLYxFvkOdbAWupjI5yueyhaQoSx7MFt9wU-ZXlV2M1eYKGzvIYYF6_0INLp_79euOvmyH3YTha6fpXIIUo_kG1xpMLJxoWjf6L790nJYk_1OqlMiTRipRjEKP_c7CmA=)
11. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEM5Pkrz1nE_Qabmo6qvPeqMoPJaajvcXceYKY8Urn7ND-UwqCLwCdxkBEHGUlFq_X7pLlHOrpB7WUElWMzCMxVfn3w_imYzKidizoLkvgmmd_bXC23EN6J4eciZLIk2UfSNbZUkmQL9WWpiHMeKREzg==)
12. [nus.edu.sg](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVwnI8mY1Utjq2kZYmKSLOYwrbykUvx7p3lzwx897l0NQaErm5aePgXfwUtJuW0cB6iw0dRnVwakqkLkb1xsTSP_iJo18ssgEhtOjUN0I6MxyIBigopG-NYZ9hMGRA0qMRt4ApsXVWZnQqPwXTe2s9YZios80RukS1CJKe2bq2s5Q8NyrLOIW0MUjFDn99XvS3o3GmJ9LpCEn7ZhVTHN16OXlW2uLzezx6f3luktWKzoUDmiJd8WrRguaKQFPw4sKxTA==)
13. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoGyh5YZC3D8daZiWOH7C7RZkxiEZNbLOSYUYtz5ey48XEOYR326cMIiIXWansPEUIp5CLoyMaF0-qwCtwB5dqY1vjHsiBO34xFVY22RiMi4kzAp-JdiMlzuoFF3wQh1i_Fcba6a8JLs7tCZ4YgtsaIiyqxslkZyaRPUUvLHGImm8J56X-JNJEhjDTdfsMgNnUyJ7T6dW0DUOaUTmVjeax)
14. [utoronto.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0lph0kTPJc9u8cdjPduLjj_p_s8bOaLtG1y1IkX-tQMnUo1zq7Jh91zoyMzHkuaR0UqHgRQdyVLUKINwV_LSYlX6mq-af-TXDJLmG0GnnEgexzKHmlVYnVH1eArvFEAK5022Wva0RDUznWCl9KEwenmg=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5QfaeTSn7fXGEtQm6Aygn0F2O3_x9Uc4JeYnHXzymcO--gUHchOfENKUGcWjZJC-LPwFknlrXR0R34Z0CIH5LJASX3ZFNJdC4P6zECLwyPuV4NVQLtg==)
16. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7tx7QcCaCIprIB2sXa0RV9oV5GHmyqQyW1C-GGBC3tMRTNhr61t6uCs0m96VvL0Z6PnKJgB_CM01DQPE3HKRr79RGeNPu_maoX8-ouTuQ7tT2BTNahJekWAcqSR6idEQdRIovbdZ8)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEx4Vrg5OrAuFbluSLI4_pU3KyOvTFHqQX_w0mKsyNF_IWsol7nWfsyofvcTl-PA1viaNp4JbtTs-SGBzj6lIcMN7L5egIJbusXIjnXQiTptCV1qo5DjQ==)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-HO4_Qb2yXlRrFXRWV2BFly-d9CO5ZZumkO80EmbO8R_RvkWrRzFClzLl1iml66JHa8jVA4iMEEXvm_CUjwhkAf-0R4tkkyZi5o7IdOtDG6RBIQEcjoPSDgmT5y2eI4Fx597CXumgrpPxP1PuQ-N9i9g9hnA_R647aSTWgi0p5Sz9YvWWTSte9CbyU4y5irMs87137mISty7o5t8WseqkE4ar7FxTnH25NoPwlKizYdp3zb0diVoDxKk=)
19. [anr.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-3CQPwi1S6DZhjgZDbwKYMWLb67ZUwO0Ujr2Og56pt2RQuO2nTYSNRkFy3wAsE7u5JislYP7vQzb-9r0k1uyT357oUg9Luo436zURSfOSfhrlcRg7LqdfwD-L5qw=)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8zaJ0QOQPpXI6hm111cDI2t2HZJq0tiYxOtanqq5wC4gdGoxlQOMEKUsY5hOuFZ3PgjKJuNf6zte5JxOcMFi7pDPmKj85YzTO62GZPacaJAW57R7PRw==)
21. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPHy-0css0de61_i759Hwle2nUdl-7K3wztQcC-viB_dwqyYAbtf-DHbPBlR4gVRuZ7ec_dbY72iAm-0SVJyc8XPExvME6CEiCCyGMwf04Nypmu-WC_dQSXXdDU3FSHZ-UfT-tMibpoX79rMH3Yqd3I9mzvmQLcdqFoR2ZkvuSJCYWXte9sTouH_bxqh5LZru6Lvn3yjGsC2efqlId8buWN7XJhiAAmumZZK-jbFEfvZgTJ7yFqR2_COkUBvoM7rIjxiqDbEi8iK6geBCZjjCqOhr6SX2Y07RUvN0S5UTALorozUJSCF1s8fJkKw==)
22. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxNmEVoGxWIgK_vW6jkosVDcYL9_UgxKmbAqOB-tJSiwjNiSYpU3T5RpkUMzAJgzjzmH4RbDgE3mDS3lqdtLA_9ZQH0xJkzlr_pJ_oKuHacK6G9q17-9LicZo_dHJMVwDnl81VqgU=)
23. [spencerleslie.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHx7xRwCq4iAHIpqukn8GP8aolcyM7CzW7FngNE3pEf9ZUER7ztu9gBysi8AbHjm6XZ55hF2IlBC4BHnqm71nOHzF99Bja8firCJEG4BH5q8nnwjdHI5oI38ptoDQ3dBIKO2L6F4Q4XsNDBx7jLfYhpSmZs-c4A_yiNbCH7GQ==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWrN-g1i_5wwzczntaol6GSZa_F6GZe-NIuwLkbz5sxIkrz377Ddm_7WK589F4PfPtO2E22UXYttYV-cKwpcA6kBg5m7NL-D1q8jm1v_RZosSzY8fAFQ==)
25. [bu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEC-K6KZ_FwhHkfajHdeaKslhAr08d61Solx-U7mc9ZW2TZYYf0IRcR72VFgfAYRYPsoWChrU7hkBlCLlCF4r39T6GB962hg9odLlmkI9CJORrlJGsD_VFL_jaY2xUKvlPIBQ==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCBhBqXW_luUptyxH-RVjKXkgvBArGJfXbk0A_Eu2J_EppidTBDniRigZft_8M-Sz-Pg175lhiez4ED4P_5jcdMxb9P_xBF7A2iB4s_sg5pexQ1T0T71YXPg==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSmAIBqB2n5kOV1tytNptYagy9tGMoT0_9Hcwmf6um_ukQBEoIzVSAvFEN9gy-XPKY3wKWcZ4iXK_W9C2XUP_7k-iOsMHTh8pF7smpEcEhjDxNOFO3IQ==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHokbrXmlwFz5iXNslCGrtNY9Zq3EeFnYdb_CjqynxpJvxvGk240aZ0WCeFpjDqGMyNplraCb4MgfvI3i3dG-kcRgebkB-E6-Skgu4I18bCcVEDLeC5eg==)
29. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQReWga-WdNqvcurUJIKJqQicgHZADQ0gun5KaYzFCXfmDKghEs1RobvG3TDQfqJhmbX_mw9HFTcFcrzq7MJXFwAokcYohWDsTEHwSGTsVX_gn4YQBt43EbbIFUScoj-o5W0BA84QV6GCB4ykkeRutwYn4uuTuxCE_bKqkIOdS7flbvSBNddE4mjyj)
30. [spencerleslie.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsl-ui5VsD3xMqC-66IKMCWRU2lW9HkzUwdOVo5wHcf2JUDaQA1XW29bl3g080qj4ycdfts0ZTWbvCn7fDk3W7iAqxVksbD1t0gusevOhY95szQDu0Xnvqq5MinYAgU5qUxE4glRPV4vT4kQ6lwAUFCxHN5p7vGX-jFBoUB1Kn4vbYrm6e7ZkjBg1WfDCGsAcMQyGFxA==)
31. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6lwTXiwS2o8rNMggpS-zoeWlk2UgEAohyzx2HZzBb4UArTmNLuWWrIsgjW1D46DO9_dCdj1oDcMg-0oaXX6NJcsQyJK-S56566CTWHdJJE8HB1ZoNguV9NhzZAAS9)
32. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwHigQvnDi08yQ4TgW4BqGs3vJ1VtAAtxKSWOgSKLhll9ee282Y4WhNc3Bet2sXvwiyC9u1kf0_knTuKvxRgqGyYTFnHZrgkwelA33YD4-pqsxIc64OPnyHNCBH_KFtl9mSsjM1yRAaWQL)
33. [jhu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOIguqEH79W31f30BbFoXtScW-kVUrY0D8SJRkOdrKXy46rsS1DTr6x7kIOlwaKoEli8WfEeySg-G0mlKip6gitg5-KfL4khy6PEeSSoLVofh7bkwwe3XQf9DfZA9NbirICKIAi-4siyM=)
34. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkZ2imHS9zoZhUdVLJvzcLOPpkcwQPPo0Ho91v6EJYkruaPnNERtYbu-7ULncQmRThiJAA2-09g7Wp5E7OZveXukaCOdvVtY-opm_U7ZpwV_rtXefaLQLO7CFHA2foTf7hQT9u98-LOi1B5jUa7Fg7K-Meo9rs3QyYcue59Jj_kwGToBI5JuTTNQhRhcmUGnh7F-HXlooalTYrOZJMJMhOkzRFokg9uIc3-6WEP5mtky1LfOoeFDhvkU82XS0=)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFu11eqlNYz0CDNfReuOEZVA9fG9v5bT6j29LqfYU_vKFVvXVuM_YmBFb6LSB7CCmEsJNOl8ZKAJYt7eAjxg7F-GdZRdEZ-FoF0Saqfw55QR_aTRh8e2Q==)
36. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsap6H7ZRidv1Fw49twSHwLUQ5eaVDPNNUg-WnmJymjui4FQiyHWCdUKSMsxcwCUe6J21LXUwX_Gk1AG0xALKizwENWwLThXi5gLiSLw_gt3rK2jo-aA==)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZ2m8CiAjDleD67hdcExARwKDIdqg4ww2fdq0NlvLCmlVbFe8oBdcagpqtCNRlI2g-5X_YqYGVMhFWYvfILZMNU1F5hGWZBBF-NaXuF9P9NyiiDi_dOjo=)
38. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDEDkrBABDNrwsFqCMo0-c1bVdu_CE1sv_DlNGbtwD1QeUmGLZBBIHVyHKzcVWCEnyKQ5Z9xWY3h7YNZz8vsQNFegqVnDGvFBnjC9sDZpmnTDEi12T7A==)
39. [umich.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHG2R8dHLXbq8ZYIQljht4jNsoXAMkzqw08KgEvXwy_vp6mzuAIML8M-U2F30I2OruDVs6nzyrfgAAxWjlVZHIeLMJGfhZN8YqvjDnuhqMLhBlVWediTtJ9M_ld8EZgW_sPsQ==)

