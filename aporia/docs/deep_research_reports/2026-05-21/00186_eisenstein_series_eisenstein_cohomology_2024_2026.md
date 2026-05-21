# Eisenstein series + Eisenstein cohomology 2024-2026

**Pythia queue id:** 186
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc0VDRQYW9PYUp0ZWI5TW9QemJYSmdBdxIXNFQ0UGFvT2FKdGViOU1vUHpiWEpnQXc
**Elapsed:** 251s
**Completed at:** 2026-05-21T17:24:45.965709+00:00

---

# Recent Advances in Eisenstein Cohomology and Eisenstein Series (2024-2026)

**Key Points**
*   Research suggests that between 2024 and 2026, the study of Eisenstein cohomology has significantly advanced the arithmetic theory of automorphic \(L\)-functions across multiple algebraic groups, including \(\mathrm{GL}_n\), orthogonal groups, and exceptional groups.
*   It seems likely that the Langlands-Shahidi method, when interpreted through the cohomological properties of Eisenstein series, provides a robust framework for proving rationality and period relations for the critical values of \(L\)-functions.
*   The evidence leans toward an increasingly profound connection between the arithmetic congruences of automorphic forms and the congruences of their associated \(L\)-values, heavily relying on the structural analysis of integral Eisenstein cohomology.
*   Recent structural investigations indicate that the Franke filtration of the space of automorphic forms can resolve previously intractable phenomena regarding degenerate and residual Eisenstein series. 

**What is Eisenstein Cohomology?**
Eisenstein cohomology serves as a vital bridge between the topology and geometry of locally symmetric spaces and the arithmetic properties of automorphic forms. Broadly, the cohomology of a locally symmetric space—often associated with a reductive algebraic group—can be decomposed into cuspidal cohomology and Eisenstein cohomology. While cuspidal cohomology is represented by cusp forms, Eisenstein cohomology is represented by Eisenstein series and induced representations. Because these groups can be defined sheaf-theoretically, mathematicians are able to exert precise control over their rationality and integrality properties, providing a powerful mechanism to study the special values of \(L\)-functions [cite: 1, 2].

**Why the 2024-2026 Period is Significant**
During the 2024-2026 period, the foundational framework established by Harder and Raghuram has been vigorously expanded beyond its original scope of \(\mathrm{GL}_N\) over totally real fields [cite: 1, 3]. Recent breakthroughs have systematically applied these cohomological techniques to totally imaginary base fields, exceptional groups such as \(G_2\), orthogonal groups such as \(\mathrm{O}(2n)\), and degenerate principal series representations. Concurrently, new applications involving Deligne's conjectures, the cross-ratio theorem, and \(p\)-adic interpolations have emerged, marking a highly active era of research in the Langlands program [cite: 4, 5].

## 1. Foundations of Eisenstein Cohomology

The theory of Eisenstein cohomology inherently involves the study of the relative Lie algebra cohomology of spaces of automorphic forms and their connection to the cohomology of arithmetic congruence subgroups. The foundational architecture relies on the Eichler-Shimura isomorphism, which bridges the classical theory of modular forms and the cohomology of arithmetic groups [cite: 2]. For a general linear group \(\mathrm{GL}(N)\), one considers the locally symmetric space associated with it. The cohomology of these locally symmetric spaces is studied with coefficients in a local system attached to a finite-dimensional algebraic representation of \(\mathrm{GL}(N)\) [cite: 1, 6].

### The Borel-Serre Compactification
To study these cohomology groups, mathematicians utilize the Borel-Serre compactification of the non-compact locally symmetric space. Let \(X_\Gamma\) denote a locally symmetric space. The reductive Borel-Serre compactification \(\overline{X}_\Gamma\) allows the boundary \(\partial \overline{X}_\Gamma\) to be stratified by components associated with the parabolic subgroups of the underlying reductive group [cite: 7, 8]. 

Eisenstein cohomology is precisely defined as the image of the global interior cohomology mapped into the cohomology of the Borel-Serre boundary. At a transcendental level, the classes in this image can be represented explicitly in terms of regular and degenerate Eisenstein series [cite: 1, 6]. Because the cohomology groups can be defined algebraically (sheaf-theoretically over specific fields or rings of integers), their rational and integral structures are strictly preserved. This yields deep arithmetic consequences for the automorphic forms parameterizing the Eisenstein series [cite: 6].

### Langlands Constant Term Theorem and Cohomology
A celebrated theorem by Robert Langlands dictates that the constant term of an Eisenstein series can be expressed via intertwining operators, which are intimately related to quotients of automorphic \(L\)-functions [cite: 2, 6]. A major innovation, largely spearheaded by Günter Harder and Anantharam Raghuram, involves interpreting Langlands's constant term theorem in terms of restriction maps in Eisenstein cohomology. This purely cohomological interpretation permits the extraction of rationality results for the special values of Rankin-Selberg \(L\)-functions for \(\mathrm{GL}(n) \times \mathrm{GL}(m)\) where \(n + m = N\) [cite: 1, 6]. Between 2024 and 2026, researchers have successfully adapted this framework to handle more complex ambient groups and broader classes of number fields.

## 2. Rationality Results and Special Values of \(L\)-Functions

One of the most active domains of research in 2024-2026 is the application of Eisenstein cohomology to deduce the rationality of critical values (and ratios of successive critical values) for \(L\)-functions across diverse algebraic groups. 

### Exceptional Groups: The Case of \(G_2\)
In 2024, significant progress was made by Farid Hosseinijafari, who extended the Harder-Raghuram method to exceptional algebraic groups [cite: 4]. Hosseinijafari's research focuses on the exceptional group \(G_2\) over a totally imaginary field. The \(L\)-functions in this context are constructed using the Langlands-Shahidi method attached to maximal parabolic subgroups [cite: 4]. 

This represents the first instance of applying rank-one Eisenstein cohomology to an exceptional group to isolate rationality properties. Importantly, it is also the first documented case involving more than one \(L\)-function appearing in the constant term of the associated Eisenstein series [cite: 4]. Hosseinijafari demonstrated how the rationality of different \(L\)-functions appearing in the constant term are interconnected. Consequently, one can rigorously prove the rationality of a specific \(L\)-function based on the established rationality results of another \(L\)-function within the same constant term expansion [cite: 4]. 

### Orthogonal Groups: \(\mathrm{GL}_1 \times \mathrm{O}(2n)\)
In 2025, Chandrasheel Bhagwat and A. Raghuram published pivotal results regarding the Eisenstein cohomology of split orthogonal groups [cite: 9, 10]. Their study investigates the rank-one Eisenstein cohomology of the split orthogonal group \(\mathrm{O}(2n+2)\) defined over a totally real number field \(F\) [cite: 9, 11]. 

By exploiting the boundary cohomology of the locally symmetric spaces associated with \(\mathrm{O}(2n+2)\), Bhagwat and Raghuram established a rationality theorem for the ratios of successive critical values of degree-\(2n\) Langlands \(L\)-functions associated to the group \(\mathrm{GL}_1 \times \mathrm{O}(2n)\) over \(F\) [cite: 9, 12]. This breakthrough subsumes and massively generalizes classical results; for instance, when \(n = 2\), their theorem gracefully recovers Goro Shimura's historic results on the special values of Rankin-Selberg \(L\)-functions attached to pairs of Hilbert modular forms [cite: 11, 12]. 

### Rankin-Selberg Convolutions for \(\mathrm{GL}_n \times \mathrm{GL}_n\)
Furthering the Rankin-Selberg theory, a 2025 study by Yubo Jin, Jiang-Shu Li, Dongwen Liu, and Binyong Sun established deep period relations for the standard \(L\)-functions of Rankin-Selberg convolutions specifically for the \(\mathrm{GL}_n \times \mathrm{GL}_n\) case [cite: 13]. The cases of \(\mathrm{GL}_n \times \mathrm{GL}_{n-1}\) and \(\mathrm{GL}_n \times \mathrm{GL}_n\) are fundamental in Rankin-Selberg theory because many properties of general convolutions can be algebraically reduced to them [cite: 13]. 

Their framework targets period relations that are entirely compatible with the conjectures proposed by Pierre Deligne and Don Blasius. The primary difficulty navigated in this 2025 work was establishing the rationality of the Eisenstein cohomology defined by Eisenstein series associated to *degenerate* principal series representations, contrasting with earlier work that largely relied on regular principal series [cite: 13, 14]. 

The following table summarizes the scope of rationality results generalized between 2024 and 2026:

| Algebraic Group Context | Ambient Group Used | Base Field | Key Researchers (Year) | Core Result |
| :--- | :--- | :--- | :--- | :--- |
| \(G_2\) (Exceptional) | \(G_2\) | Totally Imaginary | Hosseinijafari (2024) [cite: 4] | Ratios of critical values of \(L\)-functions via Langlands-Shahidi method. |
| \(\mathrm{GL}_1 \times \mathrm{O}(2n)\) | \(\mathrm{O}(2n+2)\) | Totally Real | Bhagwat, Raghuram (2025) [cite: 9, 11] | Ratios of successive critical values of degree-\(2n\) \(L\)-functions. |
| \(\mathrm{GL}_n \times \mathrm{GL}_n\) | \(\mathrm{GL}_{2n}\) | Number field w/ CM | Jin, Li, Liu, Sun (2025) [cite: 13] | Period relations mapping to Blasius-Deligne conjectures. |

## 3. Denominators of Eisenstein Classes and Arithmetic Congruences

A profound aspect of Eisenstein cohomology is its capacity to detect arithmetic congruences between automorphic forms. Because cohomology groups can be defined over integral rings (such as \(\mathbb{Z}\)), classes mapping to the boundary may exhibit denominators. 

### Harder's Denominator Conjecture
Günter Harder's denominator conjecture proposes that the denominators of Eisenstein cohomology classes of certain locally symmetric spaces are intrinsically related to the numerators of special values of \(L\)-functions [cite: 2, 15]. An elementary historical realization of this principle is Ramanujan's 691-congruence, which can be elegantly recovered by viewing the denominator of an Eisenstein class on \(\mathrm{GL}_2\) [cite: 2].

Between 2023 and 2026, Romain Branchereau made substantive progress on Harder's conjecture for Bianchi manifolds [cite: 16]. A Bianchi manifold is a locally symmetric space of the form \(Y_\Gamma = \mathrm{SL}_2(\mathcal{O}) \backslash \mathbb{H}_3\), where \(\mathcal{O}\) is the ring of integers of an imaginary quadratic field \(K\), and \(\mathbb{H}_3\) is hyperbolic 3-space [cite: 8, 15]. Previous work by Tobias Berger had established a lower bound on the denominator of the Eisenstein cohomology for these spaces [cite: 15, 16]. 

Branchereau successfully proved an upper bound on this denominator. Utilizing the results of Ito and the Sczech cocycle, Branchereau bounded the denominator in terms of a special value of a Hecke \(L\)-function [cite: 8, 15]. Notably, for imaginary quadratic fields \(K\) with a class number \(h = |\mathrm{Cl}(K)| = 1\), combining Branchereau's upper bound with Berger's lower bound establishes the *exact* denominator of the Eisenstein class [cite: 8, 15]. 

### Congruences for Ratios of Rankin-Selberg \(L\)-Functions
Building on the principle that congruences between geometric objects dictate congruences between their attached \(L\)-values, P. Narayanan and A. Raghuram published investigations into the Rankin-Selberg \(L\)-functions (2025-2026) [cite: 17, 18]. Their theorem asserts that if two holomorphic cuspidal eigenforms \(f\) and \(f'\) are congruent modulo a prime \(p\), this congruence propagates to the algebraic parts of the special values of their \(L\)-functions when convoluted with another test cusp form \(g\) [cite: 18, 19].

Specifically, they proved an instance of this principle for the ratios of critical values for Rankin-Selberg \(L\)-functions attached to pairs of holomorphic cuspforms [cite: 18, 20]. To achieve this, Narayanan and Raghuram had to significantly refine the standard machinery of Eisenstein cohomology to operate over *integral* cohomology rather than rational or complex cohomology [cite: 18, 20]. This framework over \(\mathrm{GL}(4)\) provides a robust platform for verifying deep congruences via the boundary mappings of integral Eisenstein classes [cite: 19].

## 4. Degenerate and Residual Eisenstein Cohomology

A critical technical frontier in the 2024-2026 literature involves moving beyond regular principal series representations toward degenerate and residual Eisenstein series.

### Degenerate Principal Series
In mid-2025, Y. Jin, D. Liu, and B. Sun investigated the Eisenstein cohomology defined by Eisenstein series associated with degenerate principal series representations [cite: 14]. A degenerate principal series representation is induced from a parabolic subgroup that is not a Borel subgroup, meaning the Levi factor is non-abelian. By rigorously computing the constant term of the Eisenstein series—which is a sum of intricate intertwining operators—they proved a rationality result that serves as a direct analogue to Harder's classical theorems for regular principal series [cite: 14]. This rationality is highly sought after as a prerequisite for studying special values of complex \(L\)-functions [cite: 13, 14].

### The Franke Filtration and the Jacquet-Langlands Correspondence
The structure of spaces of automorphic forms is heavily reliant on the Franke filtration [cite: 21, 22]. The space of automorphic forms \(A(G)\) is filtered into a finite descending chain where consecutive quotients are described in terms of representations parabolically induced from discrete spectrum automorphic representations of Levi factors [cite: 22, 23]. 

Research by Harald Grobner in 2024 and 2025 demonstrated unexpected phenomena within the Franke filtration for the general linear group. Grobner revealed that degenerate Eisenstein series arising from parabolic subgroups of the same rank do not necessarily contribute to the same quotient of the filtration [cite: 21]. Furthermore, Eisenstein series arising from parabolic subgroups of higher relative rank might contribute to a deeper quotient of the filtration than previously expected, disproving older structural conjectures [cite: 21]. 

Applying this refined understanding, Grobner examined the automorphic cohomology of \(\mathrm{SL}_n(\mathbb{Z})\) right outside the "stable range" (i.e., degrees \(q = n-1\) and \(q = n\)) [cite: 24]. Grobner established qualitative non-vanishing results, proving the existence of non-trivial cohomology classes that are representable by everywhere unramified degenerate Eisenstein series and lie explicitly outside the image of the traditional Borel map [cite: 24]. Furthermore, Grobner extended these methodologies to establish a functorial Jacquet-Langlands correspondence for quotients of spaces of automorphic forms spanned by derivatives of these degenerate Eisenstein series [cite: 22, 23].

### Residual Eisenstein Series and Vanishing Theorems
In 2026, Sam Mundy published a highly detailed study on the residual Eisenstein cohomology of semisimple groups [cite: 25, 26]. Residual representations arise from the poles of Eisenstein series. Mundy focused on maximal parabolic subgroups that remain maximal over the real numbers \(\mathbb{R}\) [cite: 25]. 

Mundy demonstrated that under certain general hypotheses, these residual representations are cohomological one degree below the middle dimension, and one degree above it. However, the classes positioned above the middle dimension universally vanish in the full automorphic cohomology [cite: 25, 26]. Mundy's proof construct an explicit cochain in relative Lie algebra cohomology that provides a primitive to the image of the nontrivial class. This explicit cochain is remarkably valued in regular Eisenstein series [cite: 25, 26]. Additionally, Mundy proved that the archimedean component of the relevant induced representation contains a subrepresentation—comprising the sum of two discrete series—where the intertwining operator vanishes to an order of exactly 1, heavily utilizing Harish-Chandra parameters [cite: 25, 26].

## 5. Motives, Periods, and Functoriality

The intersection of Eisenstein cohomology and the theory of motives saw rapid theoretical progress, much of it aimed at resolving cases of Deligne's conjecture. Deligne's conjecture asserts the rationality (up to specific determinental periods) of critical values of \(L\)-functions attached to pure motives [cite: 27].

### Multilinear Algebraic Structures on Motives
In a landmark 2024 paper, Pierre Deligne and A. Raghuram explored the functorial transfer of motives [cite: 5]. Given a pure motive \(M\) over \(\mathbb{Q}\) equipped with a multilinear algebraic structure \(s\), and an algebraic representation \(V\) of the group of automorphisms respecting \(s\), they described a functorial transfer \(M_V\) [cite: 5]. This acts as the motivic analogue of the Langlands transfer.

Deligne and Raghuram formulated explicit criteria ensuring when the two topological periods—\(c^+(M(s))\) and \(c^-(M(s))\)—of the motive \(M_V\) are equal [cite: 5]. This equality has direct implications for identifying the exact critical values of the \(L\)-function attached to \(M_V\) [cite: 5]. Their theory seamlessly applies to tensor product motives (connected to Rankin-Selberg \(L\)-functions), orthogonal motives (connected to the standard \(L\)-function for even orthogonal groups), and twisted tensor motives (connected to Asai \(L\)-functions) [cite: 5]. 

### Extensions of Hodge Structures
Operating under the Bloch-Beilinson conjectures, Jitendra Bajpai and Mattia Cavicchi (December 2025) constructed candidates for extensions of Hodge structures associated with families of Hecke characters \(\phi\) over a quadratic imaginary field \(F\) [cite: 28]. The Bloch-Beilinson conjectures predict that the order of vanishing of the \(L\)-function \(L(\phi, s)\) at the central point \(s = -1\) should match the dimension of the space of extensions of the Tate motive \(\mathbb{Q}(1)\) by the motive associated with \(\phi\) [cite: 28]. 

Assuming the sign of the functional equation of \(L(\phi, s)\) is \(-1\), Bajpai and Cavicchi accomplished this construction via the cohomology of variations of Hodge structures over Picard modular surfaces associated with \(F\), utilizing Harder's theory of Eisenstein cohomology [cite: 28]. They successfully demonstrated that these extensions are naturally realized within specific biextensions, opening pathways to prove their non-triviality [cite: 28]. 

Furthermore, Y. Jin, D. Liu, and B. Sun (2026) provided a full proof of Deligne's conjecture for critical values of Hecke \(L\)-functions, successfully fulfilling a strategic blueprint originally sketched by Harder and Schappacher [cite: 27]. Their proof integrates the study of a toroidal integral for Eisenstein series with the modern rationality results of Eisenstein cohomology [cite: 27]. 

## 6. Categorical, \(p\)-adic, and Higher Hida Perspectives

As the purely complex and rational theories mature, scholars have begun transporting Eisenstein cohomology into \(p\)-adic and categorical settings. 

### Higher Hida Theory for \(\mathrm{GSp}_4\)
In early 2025, Hung Chiang detailed a construction of a higher Hida cuspidal Siegel Eisenstein family for the group \(\mathrm{GSp}_4\) [cite: 29]. Eisenstein series generated from parabolic inductions of cuspidal representations of the Levi subgroup of the Siegel parabolic subgroup of \(\mathrm{GSp}_4\) contribute heavily to the degree-1 coherent cohomology of automorphic vector bundles on Siegel 3-folds [cite: 29]. 

Because the constant terms of these series involve special values of the standard \(L\)-function for \(\mathrm{GL}_2\), their \(p\)-adic integrality is of prime interest [cite: 29]. However, the absence of a conventional \(q\)-expansion principle in higher cohomology degrees inherently limits the classic methodology. Chiang bypassed this obstacle by constructing explicit families of these Eisenstein cohomology classes that are integral specifically within the framework of *higher Hida theory* [cite: 29]. 

### Relative Completed Cohomology
Simultaneously, D. Liu and B. Sun generalized Matthew Emerton's completed cohomologies to define "relative completed cohomologies" for arithmetic manifolds [cite: 30]. While classical period integrals cannot be natively executed on \(p\)-adic manifolds due to the absence of a generic \(p\)-adic Haar measure, modular symbols offer a robust topological alternative [cite: 30]. By defining modular symbols for their relative completed cohomologies, Liu and Sun proved that these spaces successfully interpolate the "nearly ordinary part" of classical automorphic cohomologies [cite: 30].

### Categorical Langlands Program
From a more geometric standpoint, Matthew Emerton, in joint work with Xinwen Zhu, Dougal Davis, and Kari Vilonen, proposed a conjectural description of the cohomology of Shimura varieties (and congruence locally symmetric spaces) entirely in terms of Galois-theoretic data [cite: 31]. Operating within the categorical Langlands program, this conjecture specifically isolates and maps the Eisenstein eigenspaces in cohomology, providing a massive structural roadmap for viewing Eisenstein series as categorical functors [cite: 31]. 

## 7. Major Academic Conferences and Global Initiatives (2024-2026)

The surge in breakthroughs concerning Eisenstein series and cohomology has been catalyzed by several high-profile academic gatherings, underscoring the topic's centrality in contemporary mathematics.

1.  **ESI Workshop (September 2025)**: The Erwin Schrödinger International Institute for Mathematics and Physics (ESI) hosted a dedicated workshop titled *"Eisenstein Series, Spaces of Automorphic Forms, and Applications"* [cite: 32, 33]. Key themes included the fine structure of spaces of automorphic forms, degenerate Eisenstein series, and the Jacquet-Langlands correspondence [cite: 33]. Notable presentations included Laurent Clozel's report on the invariance properties of automorphic \(L\)-functions based on Deligne's conjectures, proved via Eisenstein cohomology [cite: 34].
2.  **MPS Conference on the Eisenstein Ideal (2024/2025)**: Celebrating 50 years of Mazur's Eisenstein ideal, this conference featured talks by Jaclyn Lang on Eisenstein-cuspidal congruences in weight 2, and Romyar Sharifi on maps from the homology of Bianchi spaces to \(K\)-groups of ray class fields modulo the Eisenstein ideal [cite: 31]. 
3.  **ICTS Program on Automorphic Forms (July 2026)**: The International Centre for Theoretical Sciences in Bengaluru is slated to host an advanced program featuring a mini-course by A. Raghuram directly on *"Congruences and Eisenstein cohomology,"* further cementing the pedagogical formalization of the Harder-Raghuram methodologies for the next generation of researchers [cite: 35]. 

## Conclusion

The years 2024 through 2026 have represented a paradigm shift in the study of Eisenstein cohomology. The framework has successfully broken out of its traditional confines—namely, \(\mathrm{GL}_N\) over totally real fields—and has been robustly applied to orthogonal groups (\(\mathrm{O}(2n)\)), exceptional groups (\(G_2\)), and totally imaginary fields. Concurrently, the exploration of degenerate and residual Eisenstein series using the Franke filtration has unveiled structural behaviors that were previously obscured, allowing mathematicians to extract rationality results, bound cohomological denominators, and formulate precise \(p\)-adic interpolations. Through the lens of Eisenstein cohomology, the intricate arithmetic symmetries governing \(L\)-functions, motives, and Galois representations have never been clearer.

**Sources:**
1. [academybooks.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJA7cgb85kkAYodFmzMcuZeq7WRhZ7g1hV8aizWv4eeVQdV8iZA5g1e_3HAvku9-t4u_xDO1tixA0Ivp3b1BG0MMOCwm1_eg9k6A4SeMm7qycn95iljOuicO8ltD-FHjZbSCe_Ar78WBB6tervSCTNvs5ruuZGblA7fTVeTH4J_EZYJqBQzkmFAoAg76G6AabXCQ==)
2. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMjGxJyuNiF7VneXkneYZ7LkDbRCud6TZg0CGJIpwVXh5DvhX6-d08BK8POQM0QRhvISe4QecQXjkB5Hz5LyVzS43q117Kv_nrnyVEHU0vLEpGwFJyWx9SxmdboEvAm5DxVlkmdAA713S7nA==)
3. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4Hon4ax4p7k75QLKbmDRnGacRrMxb7k-Es7Zt0OuMd7QbVbU6IxLBvxVZ2U8zfo97qHgzp1SvylUURT9skL1_q4xh6BFDdCiFFccIHlzA_RmaOUOlHbMfIq70A6vQAEsfxJOj5TWAkOGUhsaxhg7Va9lcsoB8BGV_yj7ahWGDHUKyMnLdu4GnukCqgxDqWhp27QCOy8D-ZBDLrwg8GQ==)
4. [purdue.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyfuANz_DgoZ4el-jjlvCUbRYW3kaRef7BYdA-Poc9It7HchtjYuVOXiCh7n0AVqZPKYCEGMTZzge07JfB59fCYMdtCsAnrx-rROmhJl_Py-f4I62VZDPCu-lHGO1lHwYy3jR2GCN8fNvPrABczYOQgJwomEu7D-LPD5aBX-hJY2vBA1njUho-VNmpdf2bGc_OlnuN0CTKSFtFVNChqJXz9w==)
5. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2Q0vm9-ZG9QjW8wxWYblaH6mDOtrnX3UXzAEewRqFBEPr-t7fQYxK3fUjVyBhEam315c4X-sTvaehRt2Xs_wcSv24O9xadShVaeaxBcr6ddU6-XFDP6bSe92N_36mqPwyQGvuujyGgkRL1D2Vq9boC-YmR0gOTqyeDpGqrMLCyerROuG2Gf9v_-1csuqbLOMG1zP1ZzhoUQ==)
6. [target.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNu9tN3E-5HL60Anuce3MqECAdIDlj8UzvAuxujK4syWHD8iOeR6Yen3i4SqB6PSkxesBqID36erT-I0RO7zsIBQWZU4lCZqRNN170JOdU3E2fNPuVM35jfV3qCgZuSC9Nxz22DVwahXQMSTU2xZrSnJqndQQLncfA2L9ukA_WFhv1WnZMyGYBAD7awalcwiYoEe-P42StVn9xktIIy7cVNqM17EVxuurOpFo3TU3jBuFAWNWInF68f9kzf7q3CyEehb04owBkVuuX5IT2zJ-LwZjjcYxuHsWd)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHn3Syc9jZ67x_f4VAgHNe4jkJZwAld0h6ff6umfqarbdPeULVZjq_Gsr6lav-k6gto4BWIZdNAWQWt08x0iovr5mmfbvj06IA2240q5pjXKl1rCKUVIg==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1-zv1ARa05C0-vJc9wSCIyfoJD-1uZchA2aIAu68gauBTBStPAhqdtX4Ud7Og_KJMK3r_5uGDZR4BW1vIZJ4dybLwZ8J3ZKu4AlDyCEU0xWoC2bqHFw==)
9. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJXQAuDV9lLyjM2QOxmHtlhLSjs5kZNeJ-ls8Pi9nmhsEKfEvmaBsSXvlf-MoP-ylHDU4o__vPRk_7xKerkCZsSktUy_DLW3EeZFBBkRUEqwePfamli4Omwiq-_d3Xp8D8aVSXAYEc5d5nbBv6fxvMypx_1YCZsLt8BCbT_rT-EoYijvWV7s7zym1N0t4ElUrrna4y71SEzK0VxYMNv4LCnT_aBx6UXLX9WlV8Oi7H_9g=)
10. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEiYNu7yF9QpQ54tGzz6_gdBmZe9ewM_38njzM5xQv3t4F6qDOFDJZR-36_qLKRd_IpcBY147KfXEecde8n0pgYkQpBigwrjsnCHUmtvnDQ46qB2EYkb4lZwl0pTQqixlGvFYXEz1kwV1kd-_k16UpXG77Og==)
11. [iiserpune.ac.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpBEqzq6IaVd8rRtAHJqAxP7Qy_Efmz4-1kNEJEk6_nm52kqEifxl6d5zMVW_Ga6IeFbUBU_A5LDSQryl6IaUUrWLm2M1i9LMVPGxuSIhFaljwOe3ZOTQvdM4YLCuGcUIlV57Z-80_0ZESFsI0O4sLDQ==)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNY2OU4HKx62sX5kpYzLHOsvwse2Kp_2iJz9fVw4g4JXPURwZD2Ci5BmvsskbP76X5LSU9wgOwSR01xFfSi-CeGlfT7IDcOLNB3h4Ua9wwv3Uh-0IO93uusDYgbH7v39c7G7CAuUgn_DfRL5goofx5lb2s7hTqhmIGLCUi4FHvnXiSpzlzdewsamOMUss__YPAKaEXCP9cSS2oNr_m6dZOhtnPxf2nyRJlVgpazABHKu_-S4kl6_H91YhfNxkUuYytKIerS7PKHg==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuvTfa4o0A9qk8O14ESRUw0poiTXD7LnBZkvVP-yGIEz7v-gvhgRgVCrwy5pzQmoIj0KuOtVL6FrwZjKpRDhiqu8ej6TG7R22c1jW6yV3XSLda_GjWOg==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxndGMNV7XQhHJoE4p_typ-IO_ahdky2pQtA5C4nPx2sugxHVQIPutCBnCwHRvcBeAwF6ymra92-6VAyawKtGb97lfAHnfzdNENru9sllG3ux4P8PR8Q==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_tompteASrX4BFp4gNMmLjaUg0YROUui40oGFmBVNCTyQl9y-eAU5ycs2JXcQrVl4f_ASgRdSLXUuqVr2MPKTPsGJhbaXZWk-lC4LthSsBBag781qyw==)
16. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGO4rHHIAGTFyh0hTXQxlj0TS7qTNWaVrH2Mqb2fz5ZPAqhsO4vhdOifq_1H3YTsDPyhQyl9L3XM9O1SqWrp38gw6_c058TM5n5CpAxkjhHt-UJ9jDcG6A7zDH_PBRqlG5_2I1pwBrnmhKIIsbglBgI)
17. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGl3bowwQEAtKFKPdBtZIw6K4VdFjpkJNTiusz2BQnmNtyzWrZIK-GMsGUgCA1XeHE3EJLrjAS3ywAwJk_TcfGXFzKCoION5Fu__LvsVWyi1NEbxzRcxHzvS6-gKNpG-QdR6twiBHc=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3Zoi7oLQbxiXioWJpEqYzHTG_KBurbxtuV5m0T8wvnruUrxmNBxbU_hkqJZQAqULigJK7jkdIIlnnWkSsfdoNJzuxWovEz3eGKyvS9FwWUlOJLS8wsQ==)
19. [ucsd.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEtXo4A3mMD8C7Fbn840vyZ81fbXZATQwNrNoFQtXZbPZwFzHM_DIG04kjIVKpX0g729hdwjVDOA_mYPRNxFAohF-B1hbKplYVBfR_3mKyH-V88Z-A_XDY7BPWMMBPsckT7chWXHydqYipoBM2_hz1fXWfD7ju1-2-ptO_U5A=)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGanFpLarpMMMDVmIQGOHgLLVzbbB2atJIGQBM4pjWCt9D2zZPOkcuQ_adxF2pGuPJSQYq0i3H3r7F7bkzUET3Y4TPgbybD74k4S17ROG-XT3QgmzJ8Bn5ACJJvDc6VkAQ5d0OqpxkhNHJ7cwsfblAwdrLKLjN9vfk0X7yyfiOy)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbO2be0REYY7Mmo9gMhNdeaqgDjyc41YFbFrkq2VvyNfbCBGI4KPgZpBqGJx0mI4Xou2So7CkUliJMiOAFC7Zn6O9YjH46Foy9cg4HnEGDn1MFvIwwNKj_LMgQxZmUe-N-CJgtB1ZxXseLZ2eGLzTX_hdAMUJ79IUvB_q4PZ09KamygA==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpZmbZLCZTuySrASkA_QIEspmKN8JKu8BR1rnuESHf5iO2emTLs6Exj_dSwFX6rKJ2Pr8J3RUKuXzV9_FjSeQ7CMJ9803r5LOiH2PYctJa0RxjSGVd_Q==)
23. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGF5eGopuI4EwLarV9Qt4LxUaZaCoOG5RhezeQlEXaWs8GEUvyrSwHK9W4SiFC9AtPmnTslnNy7CkxAMRvroKer_vmz6xMStnjz2NXTbsvInGHIApz6i5YohUpEitprO0dG8RD8_bAgJg335n4qwDQW)
24. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjK-srmrUGZEQnLui7xqpx20FK9if6pKhRLnLjDkMU7Ow6ifjc3PhPxuVOK90O4FoCqW00JrlCh8khNUrm-vXbL3y_QSaDZ76Vyab-1o6EQdkjqTW-Wd9yqbEMK6e57S1V1KEPX1Ha47AukObm03RiIT0oDbNR)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkS6BEZOZGGOj_Y5-pwMFWAV7B5GQJXPNB5IhJhYlgZIiBIu_WfFcWqHX6LiwdS34GJA3hy8oOB_nL-fLWlJwkzEwfgEV3mWl4YU94nHnFCrVGpUG9YA==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGW4eo99JRHjA-sugv6I2N9nL_XXqDveDJg4WvxvN6tuwJJFJhVHPXHSNN4x1u03IicsJscE8dG_Xm8HFYpwZ0k9RAgf5NtqknksuwBjUB50P7dFqfxrQ==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEG8SW_VCQVRHCaS5gN889v_tOc4IO1IUTUyLY_Cxx0tFtvhw9gjrIlOb5x3KkGsTCHHM3j4cnVuwrt2_spflneC2Wz6laXDLBrb1hhXCxWTeAXE0hxqg==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIsWEfG6rNctaHnBJYn55Nxnnbg5upg9ftxraxJuIwQfqmtU48CI1CPewDP0Shg0qK0FwcjPbRF6l8JF5xocR91UhAFmR0aIGH87cNmyAV0nVA7HWYQqZ27w==)
29. [umich.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPVJy-8DQevkWPHsnaYgBxr3-eI9rOdOJebJcHRiI9Hr35hI0gMFovGyo7gdw217RmV0ikoHiRqK-lFc7VRB0ySqY4bl1nrVONWgpDc-Y-uyynk5Yvp04z5d3NM_L6TANSnQRLuv-poxNPlqLlcgLjYtO81SLYfk1j3XNvTeGsMNeOy_WGystZ)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZJ5vmU8DLrloNO4EkNTQrvQd0EwYx6QsbACvT5iGue38Qa2onQSpnbfaY0sciRXYR-xwVUiOP7z3ZVAGRKWwCzWD4axVvCDruAEiX5bDSlFCU8WEr-Q==)
31. [simonsfoundation.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0A9OXAWkp6sTsX2nhr4efkMSwda125C5bMaystWItYgBYbLOVc_v2cMXB58RI-dOD8i6GECF5VUSry2xoCU6Cdhd5vagsYTTxb9Df09iMLaZ-5bKX4XwCWtGCQUkzPyCOSv6MhCUU4oLnd0Lge6MnIEFKF30a2Bgx2vs1AMopXfm9ZcDtbGsM9Lze1K-yroB5bV7ltY1ohGEyjZNjCzqQTFw0xNM7guj3cupRvCdfXc7xrcDfR2KNIwXYKKt1XQ==)
32. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF30Go5IPbP3yewpSzCa4wogjCLwODQre0D5eV-7RZalVZNSG3k0A1QwBNF97chI8T5N4qceN2U75EZRMd5fvLLNwKidqIOUnvbCapdzvCz0Hb88gVCERbYv11GSPH_GSuk6ig=)
33. [esi.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwy_iO3Do_0wfRRHYOYztumxt6b0p6dv8VCmPEhIsQUWRjFVw6ET4ilqORZ2gy7_YsgYlDKdalnWfEQExXZEOZtNpVQflWk7CRFZ1rw44fegSZSM17P0Ba)
34. [esi.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHP7F0jyG85xekE6SyfYSZwVC6XMeGuR1ybKd09332ODhWiRfxNXz7PKAfTN7SoY5Y0LsiJt8eMTHT7rxWGcl1FJBfsgav2wCmkEVxiflHXywzvGWNncJpgCQ==)
35. [icts.res.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-Zwm74CEYZZuGcuCYtsTlcLWq2qkd4OKOJ348_FfD3CFvJg2LleaIDgwMKToeYQSwm9vQq1cvmF7eMeC9TOw76hIvcDTAQXufo93GAylxzkYBvamxF7hZBa5Xdw==)

