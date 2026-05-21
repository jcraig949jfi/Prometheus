# Bianchi modular forms (over imaginary quadratic fields) 2024-2026 (Cremona, Whitley)

**Pythia queue id:** 183
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdhejBQYXVDeUM1Zk0tc0FQeGV6eHlBMBIXYXowUGF1Q3lDNWZNLXNBUHhlenh5QTA
**Elapsed:** 247s
**Completed at:** 2026-05-21T17:18:27.486823+00:00

---

# Bianchi Modular Forms Over Imaginary Quadratic Fields: Advancements, Computations, and the Rationality of Periods (2024–2026)

### Leading Paragraph
The study of Bianchi modular forms bridges the geometric properties of hyperbolic three-dimensional space with the profound arithmetic of imaginary quadratic fields. Research suggests that these mathematical objects are central to understanding the modularity of elliptic curves over number fields, extending the classical framework established over the rational numbers.
*   **Historical Foundations:** Foundational work in the 1980s and 1990s by John E. Cremona and Elise Whitley established algorithmic methods to compute these forms and relate their periods to the Birch–Swinnerton-Dyer (BSD) conjecture for elliptic curves over imaginary quadratic fields [cite: 1, 2]. 
*   **Computational Breakthroughs (2024–2026):** Recent literature highlights a monumental leap in computational capabilities. Algorithms have been successfully generalized and implemented by Cremona, Kalani Thalagoda, and Dan Yasaki to compute Bianchi modular forms over imaginary quadratic fields with arbitrary class groups, a significant upgrade from historical limitations [cite: 3, 4].
*   **Rationality and Period Polynomials:** Through the Eichler–Shimura–Harder isomorphism, researchers in 2024–2026—including Lewis Combes, Tian An Wong, and collaborators—have explicitly defined Bianchi period polynomials and established the analogue of Manin's rationality theorem for Bianchi periods, offering rigorous proofs for the special values of their associated L-functions [cite: 5, 6].
*   **Congruences and Database Integration:** Data derived from these new computations are actively being integrated into the L-functions and Modular Forms Database (LMFDB), while new computational Hecke actions on period polynomials have revealed rare congruences between genuine Bianchi cusp forms and Eisenstein series [cite: 3, 6].

***

## 1. Introduction to Automorphic Forms over Number Fields

The theory of automorphic forms over number fields constitutes one of the most dynamic areas of modern arithmetic geometry and number theory, forming the backbone of the Langlands program. While classical modular forms are defined as highly symmetric holomorphic functions on the complex upper half-plane $\mathcal{H}^2$ that transform nicely under the action of the modular group $\text{SL}_2(\mathbb{Z})$ (or its congruence subgroups), Bianchi modular forms act as their natural generalization to imaginary quadratic fields. 

Let $K = \mathbb{Q}(\sqrt{-D})$ be an imaginary quadratic field with discriminant $-D$ and ring of integers $\mathcal{O}_K$. The Bianchi group is defined as the special linear group $\Gamma = \text{SL}_2(\mathcal{O}_K)$ (or its projective counterpart $\text{PSL}_2(\mathcal{O}_K)$). Rather than acting on the two-dimensional hyperbolic plane, the Bianchi group acts discontinuously on the three-dimensional hyperbolic space $\mathbb{H}^3$. Because $\mathbb{H}^3$ does not possess a complex structure in the same way $\mathcal{H}^2$ does, Bianchi modular forms are not holomorphic functions. Instead, they are defined as real-analytic, vector-valued functions on $\mathbb{H}^3$ that satisfy specific harmonicity conditions—specifically, they are eigenfunctions of the hyperbolic Laplace-Beltrami operator (and related Casimir operators) that vanish at the cusps.

The intensive study of Bianchi modular forms is motivated largely by the generalized Taniyama-Shimura-Weil conjecture (the Modularity Theorem), which posits a deep correspondence between isogeny classes of elliptic curves defined over $K$ and specific weight-2 cuspidal Bianchi newforms. Although the study of these forms dates back to the mid-1960s, and heavily relies on the foundational framework of automorphic representations over global fields laid out by Weil and Miyake [cite: 4], computing them explicitly remains an extraordinarily complex task. Most of the fundamental problems surrounding their theory, particularly concerning the bounds of their dimensions and the exact nature of their periods, have remained wide open until recently [cite: 4, 7].

## 2. The Legacy of Cremona and Whitley: Foundations of Computation

To appreciate the developments of 2024–2026, it is imperative to trace the historical progression of Bianchi modular form computations, which were pioneered by John E. Cremona and significantly expanded by his student Elise Whitley. 

### 2.1 Early Computations and Modular Symbols
Computations of Bianchi modular forms over Euclidean imaginary quadratic fields (where $D \in \{1, 2, 3, 7, 11\}$) were initiated in the late 1970s and 1980s by Grunewald, Mennicke, and others, who primarily looked at prime levels for $D = 1, 2, 3$ [cite: 4, 8]. In 1984, Cremona published an extensive algorithmic framework capable of computing these forms for all five Euclidean fields at arbitrary levels. This was achieved by exploiting the topological structure of the Bianchi group's action on $\mathbb{H}^3$ [cite: 1, 4]. 

Cremona leveraged the concept of modular symbols, which evaluate the homology of the quotient manifolds $Y_\Gamma = \Gamma \backslash \mathbb{H}^3$. By computing the rational homology $H_1(Y_\Gamma, \mathbb{Q})$, one can capture the Hecke eigenvalues of the associated Bianchi cusp forms. This topological approach bypasses the need to evaluate the analytically complex Fourier-Bessel expansions of the forms directly.

### 2.2 Whitley's Thesis and the 1994 Landmark Paper
While Cremona's initial algorithm successfully tackled Euclidean domains, extending it to non-Euclidean principal ideal domains (PIDs) proved highly non-trivial due to the complex fundamental domains and the lack of a Euclidean algorithm to reduce matrices. In her 1990 Ph.D. thesis at the University of Exeter, Elise Whitley successfully extended the modular symbol techniques to cover the remaining four imaginary quadratic fields of class number 1 (where $D = 19, 43, 67, 163$) [cite: 1, 8].

This computational triumph culminated in the seminal 1994 paper, *"Periods of Cusp Forms and Elliptic Curves Over Imaginary Quadratic Fields,"* co-authored by Cremona and Whitley [cite: 2, 9]. In this paper, they explored the arithmetic correspondence between isogeny classes of elliptic curves $E$ defined over an imaginary quadratic field $K$ of class number 1, and rational newforms $F$ of weight 2 for the congruence subgroups $\Gamma_0(\mathfrak{n})$, where $\mathfrak{n}$ is an ideal in $\mathcal{O}_K$ [cite: 2]. 

A central achievement of this paper was the numerical computation of the L-series $L(F, s)$ at the central critical point $s = 1$. Cremona and Whitley compared this numerically evaluated analytic data with the arithmetic invariants of the corresponding elliptic curve $E$, as predicted by the Birch and Swinnerton-Dyer (BSD) conjecture [cite: 2, 10]. They achieved numerical agreement to several decimal places, noting specifically that $L(F, 1) = 0$ whenever the elliptic curve $E(K)$ possessed a point of infinite order [cite: 2]. This provided massive heuristic backing for the modularity of elliptic curves over imaginary quadratic fields, firmly cementing the role of periods in bridging automorphic forms with arithmetic geometry.

### 2.3 Gradual Expansion of the Class Group Limit
The algorithms implemented by Cremona and Whitley were heavily dependent on the assumption that the class group of $K$ was trivial (class number $h_K = 1$). To compute Bianchi forms over fields with $h_K > 1$, the geometry of $\mathbb{H}^3$ becomes vastly more complicated, as the quotient space $Y_\Gamma$ possesses multiple cusps, corresponding to the ideal classes of $K$. 

Progress on this front occurred incrementally through the work of Cremona's subsequent doctoral students. J. S. Bygott (1998) extended the theory to fields where the class group is an elementary abelian 2-group, explicitly computing examples for $K = \mathbb{Q}(\sqrt{-5})$ (class number 2) [cite: 4, 8]. Subsequently, M. P. Lingham (2005) adapted the algorithms for cases of odd class numbers (class number 3), and M. T. Aranés (2010) formalized the theory of modular symbols over general number fields [cite: 4, 7]. However, a unified, general-purpose algorithm capable of computing the spaces of Bianchi modular forms over a field with a completely arbitrary class group remained elusive for over a decade.

## 3. Breakthroughs in Computational Paradigms (2024–2026)

The years 2024 to 2026 marked a watershed era in the computational theory of Bianchi modular forms. Moving past the piecemeal approaches of the late 20th and early 21st centuries, researchers finally developed and implemented generalized algorithms capable of evaluating Bianchi forms and their associated Hecke algebras over imaginary quadratic fields with completely arbitrary class groups.

### 3.1 Overcoming the Class Group Barrier (Cremona, Thalagoda, Yasaki)
In a major advancement published in 2025/2026, John Cremona collaborated with Kalani Thalagoda and Dan Yasaki to present algorithms that definitively solve the problem of computing the space of Bianchi modular forms of level $\Gamma_0(\mathfrak{n})$ for arbitrary imaginary quadratic fields [cite: 3, 4]. 

The core difficulty in general class group computations lies in constructing a workable tessellation of the hyperbolic 3-space $\mathbb{H}^3$ upon which the Bianchi group $\text{GL}_2(\mathcal{O}_K)$ and its congruence subgroups act. To achieve this, Cremona, Thalagoda, and Yasaki employed an algorithm rooted in the work of Richard Swan (1971) [cite: 4, 8]. Swan's algorithm provides a rigorous framework for finding a fundamental polyhedron for the action of $\text{GL}_2(\mathcal{O}_K)$ on $\mathbb{H}^3$. 

The algorithmic pipeline presented by the authors operates in distinct phases [cite: 3]:
1.  **Precomputation (Tessellation):** A precomputation stage, which is dependent only on the field $K$ and needs to be executed only once, computes the tessellation data of $\mathbb{H}^3$ corresponding to the fundamental domain of the maximal order $\mathcal{O}_K$.
2.  **Homology Extraction:** Using the tessellation, the program calculates the rational homology $H_1(\mathbb{H}^3 / \Gamma_0(\mathfrak{n}), \mathbb{Q})$ of the quotient space. This topological space is intrinsically isomorphic to the space of unramified cuspidal Bianchi modular forms.
3.  **Hecke Action:** The action of the Hecke algebra is explicitly computed on this homology space.
4.  **Eigenspace Decomposition:** The homology space is decomposed into Hecke eigenspaces, isolating the individual normalized eigenforms (newforms).

### 3.2 Dual Independent Implementations
To ensure absolute reliability, the 2025/2026 framework was implemented using two completely independent methodological streams [cite: 3, 4]:
*   **bianchi-progs:** A complete C++ package written by Cremona that operates over arbitrary imaginary quadratic fields. It utilizes highly optimized routines for homology calculations over general domains [cite: 3].
*   **Magma Implementation:** An independent implementation developed initially by Yasaki and subsequently extended by Thalagoda in her 2023 thesis, utilizing the Magma computer algebra system [cite: 3]. 

These independent implementations cross-verified the data, proving the efficacy of the algorithms. As a showcase of their capability, the authors provided a detailed analysis of $K = \mathbb{Q}(\sqrt{-17})$, a field whose class group is cyclic of order 4 [cite: 3, 4]. In this specific case, they successfully proved the modularity of an elliptic curve defined over this field by matching its arithmetic invariants to the Hecke eigenvalues of a newly computed Bianchi newform [cite: 3, 4]. 

### 3.3 The Phenomenon of Self-Twists
An interesting mathematical phenomenon uncovered in fields with non-trivial class groups is the existence of "self-twists." For classical modular forms over $\mathbb{Q}$, twisting a form by a Dirichlet character generally results in a completely distinct modular form. However, in the context of Bianchi modular forms over fields $K$ where the class number $h_K$ is even, there exist non-trivial unramified quadratic characters $\psi$. 

Cremona, Thalagoda, and Yasaki noted that it is possible for an adelic Bianchi modular form to be its own twist by a nontrivial unramified character $\psi$ [cite: 3, 4]. This requires $\psi^2$ to be trivial. A form $F \in S(\mathfrak{n}, \chi)$ twisted by $\psi$ maps to $F \otimes \psi \in S(\mathfrak{n}, \chi\psi^2)$. When $\chi\psi^2 = \chi$ and the form equals its twist, it is said to admit a self-twist [cite: 3]. The first concrete example of a self-twist newform with a trivial character was found at level $\mathfrak{n} = (8)$ over a specific field, representing the base-change of a classical cusp form with complex multiplication [cite: 4].

### 3.4 Population of the LMFDB
The vast arrays of data generated by these arbitrary-class-group computations are not merely theoretical curiosities; they have been tabulated and actively deposited into the L-functions and Modular Forms Database (LMFDB) [cite: 3, 4]. This open-source repository now houses details of Bianchi newforms—currently prioritizing those with rational Hecke eigenvalues—making them accessible for researchers studying the Langlands program, Galois representations, and arithmetic geometry across the globe [cite: 3].

## 4. The Rationality of Periods: Advancements by Anderson, Harrigan, and Wong

While Cremona and Whitley's 1994 work dealt with the numerical approximation of periods to test BSD [cite: 2, 9], proving the exact arithmetic nature—specifically the algebraic rationality—of these periods has remained a challenging theoretical frontier. In the classical case of modular forms over $\mathbb{Q}$, Manin's rationality theorem (1973) asserts that the periods of a cusp form, when normalized by appropriate complex periods (often denoted $\Omega^+$ and $\Omega^-$), yield rational numbers or algebraic numbers residing in the coefficient field of the form. 

In late 2025 and early 2026, Gradin Anderson, Peter Harrigan, Louisa Hoback, McKayah Pugh, and Tian An Wong published a paper titled *"Bianchi Modular Forms and the Rationality of Periods,"* which decisively establishes the analogue of Manin's rationality theorem for Bianchi periods [cite: 11, 12].

### 4.1 The Eichler–Shimura–Harder Isomorphism
To understand the rationality of periods, one must analyze the Eichler–Shimura–Harder isomorphism. For a classical modular form $f$ of weight $2k+2$, its periods are defined by integrating $f$ against polynomial kernels of the form $(X-z)^{2k}$. This integration yields a map from the space of cusp forms to a space of period polynomials, explicitly realizing the Eichler–Shimura isomorphism [cite: 5, 12].

For Bianchi modular forms, the situation is dimensionally higher. Let $k$ be a non-negative integer. We define $V_{2k+2}(\mathbb{C})$ as the complex vector space of homogeneous polynomials of degree $2k+2$ in variables $X, Y$ [cite: 5, 12]. A cuspidal Bianchi modular form $F$ of weight $(k,k)$ and full level $\Gamma = \text{SL}_2(\mathcal{O}_K)$ is a function $F: \mathbb{H}^3 \rightarrow V_{2k+2}(\mathbb{C})$ satisfying strict invariance under $\Gamma$, vanishing under specific Casimir differential operators ($\Psi F = 0$ and $\Psi' F = 0$), and exhibiting rapid decay at the cusps [cite: 5].

The Eichler-Shimura-Harder isomorphism establishes a profound connection between the space of Bianchi cusp forms $S_{k,k}(\Gamma)$ and the cuspidal cohomology of the arithmetic group:
$$S_{k,k}(\Gamma) \cong H^1_{cusp}(Y_\Gamma, V_{k,k})$$
where $V_{k,k}$ is a specific coefficient module built from the polynomial spaces [cite: 5].

### 4.2 The Space of Bianchi Period Polynomials
Building upon the analytic construction of Bianchi period polynomials recently introduced by Karabulut (2022) for Euclidean imaginary quadratic fields, Anderson, Wong, and their co-authors explicitly constructed the Bianchi period polynomial in a quotient space $\tilde{W}_{k,k}$ associated with a given Bianchi cusp form $F$ [cite: 5, 12]. 

This was a highly non-trivial task because the generalized "Eichler integral" for Bianchi forms must account for the action of $\text{SL}_2(\mathcal{O}_K)$ across complex boundaries. By evaluating the cuspidal cohomology class such that its image in the modular symbol space $\text{Symb}_\Gamma(V_{k,k})$ is the modular symbol $\psi_F$, the authors successfully identified its image in the quotient space $\tilde{W}_{k,k}$ [cite: 5].

### 4.3 Proof of the Rationality Theorem
With the explicit structure of Bianchi period polynomials mapped out, Anderson, Harrigan, et al. computed the action of Hecke operators on these Bianchi periods. Using this explicit Hecke action, they obtained integral formulas for the periods [cite: 5, 12]. 

Their main theorem can be summarized as follows: Let $K$ be a Euclidean imaginary quadratic field, $F$ be a normalized Bianchi Hecke eigenform, and let $K(F)$ be the number field generated by $K$ and the Fourier coefficients of $F$. Then there exists a complex transcendental period $\Omega \in \mathbb{C}^\times$ such that the normalized periods of $F$ lie strictly within the algebraic number field $K(F)$ [cite: 5]. 
Specifically:
$$\frac{1}{\Omega} r_{p,q}(F) \in K(F)$$
for all bounds $0 \leq p, q \leq k$ [cite: 5]. 

This result not only establishes the analogue of Manin's theorem for Bianchi modular forms but also serves as a new, shorter, explicit proof of a broader theorem originally formulated by Hida in 1994 regarding the special values of L-functions of Bianchi cusp forms [cite: 5]. It confirms mathematically what Cremona and Whitley had observed numerically decades earlier: the periods of Bianchi modular forms possess a strict, algebraically rigid rational structure deeply intertwined with the arithmetic of their coefficients [cite: 2, 12].

## 5. Hecke Actions and Congruences of Bianchi Period Polynomials

Parallel to the rationality proofs of Anderson and Wong, the structural properties of Bianchi period polynomials were also deeply investigated by Lewis Combes in a 2024 paper titled *"Bianchi period polynomials: Hecke action and congruences,"* published in *Research in Number Theory* [cite: 6].

### 5.1 Duality and the Heilbronn Matrices
Combes focused on the Bianchi group $\widehat{\Gamma} = \text{PSL}_2(\mathcal{O}_K)$ where $\mathcal{O}_K$ is the ring of integers of a Euclidean imaginary quadratic field of class number 1 [cite: 6]. Combes successfully proved a formal duality between the space of Bianchi period polynomials and the second cohomology group of the arithmetic group, $H^2(\widehat{\Gamma}, V_{k,k}(\mathbb{C}))$ [cite: 6]. This mirrors the classical duality between weight $k$ modular symbols and period polynomials.

Using this duality, Combes resolved a significant computational challenge: how to define and compute a Hecke action directly on the space of Bianchi period polynomials. In the classical case, Hecke actions on period polynomials are often computed using Heilbronn matrices. Combes adapted the theory of Heilbronn matrices to the Bianchi setting. By treating the period polynomials as elements of the coefficient module $V_{k,k}(\mathbb{C})$ mapped through the Eichler-Shimura-Harder embedding $\tau$, he established a Hecke-equivariant map:
$$\tau : S_{k+2}(\widehat{\Gamma}) \hookrightarrow H^1(\widehat{\Gamma}, V_{k,k}(\mathbb{C}))$$
where the image of $\tau$ in $V_{k,k}(\mathbb{C})$ acts as the precise space of Bianchi period polynomials [cite: 6].

### 5.2 Discovering Moduli of Congruences
The primary motivation for introducing an explicit, computable Hecke action on Bianchi period polynomials was to find arithmetic congruences between different Bianchi modular forms. In classical modular form theory, Ramanujan's famous congruence $\tau(n) \equiv \sigma_{11}(n) \pmod{691}$ corresponds to a congruence between the unique weight 12 cusp form $\Delta$ and an Eisenstein series, indicated by the appearance of the prime 691 in the denominator of the normalized period polynomial [cite: 6].

Combes implemented his Hecke action algorithms in a computer algebra system to conduct numerical investigations. By inspecting the prime divisors of various quantities derived from the period polynomials, he detected highly elusive congruences. Notably, over the Euclidean field $K = \mathbb{Q}(\sqrt{-11})$, Combes exhibited congruences between genuine cusp forms of level 1 and two distinct entities:
1.  An Eisenstein series, modulo the prime ideal above 173.
2.  The base-change of a classical cusp form, modulo the prime ideal above 43 [cite: 6].

These findings represent the very first documented records of such congruences between higher-weight Bianchi modular forms in the mathematical literature [cite: 6]. The detection of these congruences represents a monumental verification of the profound arithmetic structures hidden within the cohomology of the Bianchi groups, echoing the classical theories of Ribet and Mazur but in a vastly more complex geometric domain.

## 6. Synthesis: The Evolution of Computational Number Theory

The trajectory of research on Bianchi modular forms over imaginary quadratic fields, stretching from Elise Whitley's thesis in 1990 and her joint 1994 paper with John Cremona [cite: 1, 2], to the modern 2024–2026 breakthroughs by Thalagoda, Yasaki, Wong, Combes, and Anderson [cite: 3, 6, 12], outlines a perfect arc of mathematical progress.

In the 1990s, Cremona and Whitley were constrained by processing power and the lack of a generalized algorithmic geometry for non-Euclidean fundamental domains. They relied on numerical estimations of L-series to heuristically link Bianchi forms to elliptic curves (the BSD conjecture) [cite: 2, 9]. Their results strongly suggested that the arithmetic of Bianchi forms was as rigid and rational as classical forms over $\mathbb{Q}$, but it remained largely empirical.

By 2025/2026, the theoretical and computational landscape had been fundamentally transformed:
1.  **Algorithmic Universality:** Cremona, Thalagoda, and Yasaki successfully utilized Swan's topological algorithms to bypass the class number 1 restriction entirely, creating C++ and Magma implementations capable of computing the full space of Bianchi modular forms and extracting exact Hecke eigensystems for imaginary quadratic fields with arbitrary class groups [cite: 3, 4].
2.  **Theoretical Rationality:** The exact algebraic nature of the periods computed numerically by Whitley and Cremona has now been rigorously proven through the Eichler-Shimura-Harder isomorphism by Anderson, Harrigan, Hoback, Pugh, and Wong [cite: 5, 12]. Their explicit construction of Bianchi period polynomials provides a direct, short proof of Hida's rationality theorems.
3.  **Arithmetic Congruences:** The translation of these period polynomials into computationally viable Hecke modules by Combes has opened entirely new branches of study, proving that congruences between Bianchi cusp forms and Eisenstein series exist and can be isolated systematically [cite: 6].

### Conclusion

The period between 2024 and 2026 will likely be viewed as a golden era for the study of Bianchi modular forms. The combined efforts of Cremona's continued algorithmic refinement and the fresh theoretical frameworks introduced by Thalagoda, Yasaki, Wong, Combes, and others have dismantled long-standing barriers in the field. With massive new datasets being uploaded to the LMFDB and the rationality of their periods now firmly established as mathematical law, the study of automorphic forms over imaginary quadratic fields is poised to unlock deeper truths within the Langlands program and the general modularity of abelian varieties.

**Sources:**
1. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVb30rARA8F-yMoe_kQ-0QZimQE8fMzmcj_84CGl7S95U0vaxxo1AnugL0Zpe-ZBx47FfGIDRur0XTtn-wQDmfktF18DslzLixofme4Gc_0svGohj_MVLzJCr2OjAZ3d7XNmVXo4Hofn3iF3OwwVqsto2YMgSFx9PPxCjMLQjw54gqawjeIwba6NshEiWmS9ezjKT9Ww029uqFA_tvcppdht8L0RmDbAPTPKfSbLSrI2fc-aFn16ZDFFEqq6Y2bCadn8suG9_uAl4Z6Q4nbSwsZTeCNEdnY73b2prlUig=)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDfhO_RjVczNagsxC927G0RHi8LVmB9ayrHXoGUSwpR2BHGu_lqwXhS4qtL7CmAhzMTZTtctS-irRnqfjA0EWfbF0Mv-SyF03Fya5-PRnu_SwNoVPBu0vVD_W8SV35uEPIjeV9zFYgnQe-Xmhqh5Bqi8hw6Xk7EcjyEvpDRPvtcyuKnkoxdExCZ6_lRGbh_vZ2refCQ3b7kUZ6HTRhZ_31rcEuPiGPQHviNQ5ry2RJNtLa)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBG7DNxowkesQp6hSMjbaL--2YJJK064fZYyns-RX3hQdLQhc9EacxkDx_uGKcfY2oudo4NmZvWME0hL-blv5QEPIzs0CaDe-Y0R5SqgzlKev4Ikq60ccEpw==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrqCm80Dy_jpRM80GhebAkL_lKp2UjbsbLkOwIWewulYl75welucEYpEqbCgzd0r8EmasAuKx8UYOFMMWX1JFHBeKARteLnVH_sVukN0iHz4AfPpkr8Q==)
5. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFv8NZNaZyNEGcS3ofDatW9rC41C9_3xgsBCFLZeK9xhej_K3cuuY8lM__i0va2EemL2Rdvfw4DM1SJ0f1uH5-fGSe1TNHXENaNUX3gt26sFYQ0ZGslpQmrmhpYKI09x5xQ-V8ih7hy36TtkUQ-PkkfS1tGGbPZmiRs-TJHgyY2F-DFKVrsvuxqvjIStCs7mmnAWMcZFPzekVTzvc2HId8oChveS6_cwTn64LVrV9b5yKf3Y6WKJCIRfwMxxxTgOm37QXLfajk3aGRwJb_M68rxG_ubeF6CGXWUGzo=)
6. [whiterose.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9BThT88HNTK1qKGGsgLzcryH2gPB4ZhPqkq_aKMpzYlp06MLtRbMbZUw8fWvAlYF8037WC_MozV4JRjg6060HOPMFQ5ZbL8gVplyNe1yGbMavBScEdgW_KR3HPklJPYdwODGrvPet7wLl557QjuWkmOW5xvonryWK4ARpSSCE)
7. [whiterose.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlt4SKtzuCwtHHVt50Gxu48oSOfqfTBw1KGbw7wrT3JZbhtKk8uqu9Dfw2v1WZkIdnFgjV-ABYTwvqAqqUIgDoGiwSyHBq8LzaEc2H4dGaUXUorFtkcLdr3m6At9IVXbwv8ljYNpVe23fYQxqK2CTrDPuQrzvN9A==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyCE4Q5wNeS8p3WVWB6q6O94HV2GwacaQNAY6ShGa6jdTenCTwQUOZhTCcy7ITNrWn70L_CEQIhgnW6sh8VxrX3mI8oagjiCHL7Fg1jmxaEDJUSwuJGCZKhw==)
9. [mathnet.ru](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTUka4NLap5h2LfJnIEpw2C3_Hyh3vHgW8RRCRRydphG8bZ5QY6LzVQ59t1YBP3wb3HxGG6EAX1dMqD5IlbS4cHoDon3kZYhCgVu10vtOQQ0mYesWUXYc=)
10. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEenUTUqG1iaoDny32J03_KFu0mvc2at1gAjvrBakr08oEcL8MJ3bzrvzudAFov-5SpxTHV7f25nvYvCe9u-AK0RIIATOWATP-TN--vKlJwYmY4PdI35pi5sdcfbDlrV2yLCJAa)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG10myPQY0l5qEgO7cnOnCfyE4q23zHjRpaHOWzP2kIqV7mTUlzyyu1GN6B0CAe3Znf8H2THNRqBZygIVKZMkvtw637a78AbOcxC3eWCbHg_UmVi7sdjw==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBcf3g_hI7Q-LppcZ25NMcVcIhuhiDeB0LmFgD-jgNCcx9Hw9dggVr0uPAJljSPLd6RXjDaZJuEvqZ5hgAE6_iKQBykkDq8lLJpXf91u-9jbHcgRuSErkx1Q==)

