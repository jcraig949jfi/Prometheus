# Littlewood-Richardson coefficient algorithmic computation 2024-2026

**Pythia queue id:** 209
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdoMGdQYXVfQ0lvVExqTWNQanBqbDRRaxIXaDBnUGF1X0NJb1RMak1jUGpwamw0UWs
**Elapsed:** 247s
**Completed at:** 2026-05-21T18:05:51.917083+00:00

---

# Algorithmic Computation of Littlewood-Richardson Coefficients (2024-2026): Complexity, Quantum Advancements, and Novel Combinatorial Models

### Key Points
*   **Computational Complexity:** The general computation of Littlewood-Richardson (LR) coefficients remains #P-complete, meaning no efficient classical algorithm exists for all arbitrary inputs unless P = NP. However, research between 2024 and 2026 has identified specific polynomial-time algorithms for certain parameter regimes.
*   **Quantum vs. Classical Algorithms:** A significant academic debate emerged in 2024–2026 regarding quantum speedups. While early 2024 research suggested superpolynomial quantum advantages for related representation-theoretic multiplicities, subsequent 2025–2026 research demonstrated that classical algorithms can also compute many of these bounded cases in polynomial time, narrowing the scope for exclusive quantum supremacy.
*   **Novel Combinatorial Models:** Recent breakthroughs have introduced new algorithmic rules, most notably the use of "peelable tableaux" and "shuffle diagrams," which offer computationally faster methods for generalized LR coefficients compared to traditional skew-diagram approaches.
*   **Branching Rules and Symmetries:** The development of the "quantum Littlewood-Richardson map" has algorithmically formalized new branching models (e.g., from general linear to symplectic groups), providing combinatorial proofs for previously theoretical symmetries.

### Introduction to the Topic
The Littlewood-Richardson coefficient is a foundational mathematical value used heavily in algebraic combinatorics, representation theory, and geometric complexity theory. Put simply, these coefficients count the number of ways certain mathematical symmetries and shapes (represented by "Young tableaux") can be combined. Because they govern how tensor products of representations decompose, finding an efficient way to calculate them via computer algorithms is a highly sought-after goal. 

### The 2024-2026 Research Landscape
Between 2024 and 2026, the algorithmic computation of these coefficients saw a surge in interdisciplinary research. Physicists and computer scientists attempted to use quantum computers to calculate these numbers faster than classical computers. Concurrently, combinatorial mathematicians developed new visual and structural models (like "peelable tableaux" and "LR-Sundaram tableaux") to streamline classical computation. The synthesis of these approaches has fundamentally updated our understanding of what can and cannot be efficiently computed in representation theory.

***

## Foundational Complexity of Littlewood-Richardson Coefficients

### Mathematical Definition and Traditional Computation
The Littlewood-Richardson (LR) coefficients, denoted as \( c^\lambda_{\mu\nu} \), are defined primarily as the structure constants that appear in the expansion of the product of two Schur functions:
\[ s_\mu s_\nu = \sum_\lambda c^\lambda_{\mu\nu} s_\lambda \]
where \( \lambda, \mu, \) and \( \nu \) are integer partitions [cite: 1, 2]. These coefficients are strictly zero unless \( \mu \subseteq \lambda \) and \( \nu \subseteq \lambda \) [cite: 1]. They satisfy several profound symmetry properties, most notably \( c^\lambda_{\mu\nu} = c^\lambda_{\nu\mu} = c^{\lambda'}_{\mu'\nu'} \) [cite: 1].

From an algorithmic standpoint, the traditional Littlewood-Richardson rule states that \( c^\lambda_{\mu\nu} \) counts the number of skew semistandard Young tableaux of shape \( \lambda/\mu \) with content \( \nu \), subject to the strict restriction that the concatenation of the reversed rows forms a "lattice word" (or Yamanouchi word) [cite: 1, 3]. A word is considered a lattice word if, for every prefix, the number of times an integer \( i \) appears is at least as many times as the integer \( i+1 \) appears [cite: 1, 3].

### The #P-Completeness Barrier
The fundamental bottleneck in the algorithmic computation of LR coefficients is their inherent computational complexity. In 2006, H. Narayanan definitively proved that computing both Kostka numbers and Littlewood-Richardson coefficients is generally #P-complete [cite: 4, 5]. The #P complexity class includes problems that ask "how many" solutions exist, rather than simply "is there a solution" (which belongs to NP). Narayanan achieved this by reducing the known #P-complete problem of computing the number of contingency tables with given row and column sums to the problem of computing Kostka numbers, which was then reduced to computing LR coefficients [cite: 4]. 

Because the computation is #P-complete (specifically, #P-hard even when the input partitions are encoded in unary), there are no efficient polynomial-time algorithms for computing arbitrary LR coefficients, assuming the widely believed computational hypothesis that P \( \neq \) NP [cite: 4, 5]. Despite this worst-case exponential barrier, the decision problem of determining whether an LR coefficient is strictly positive (i.e., \( c^\lambda_{\mu\nu} > 0 \)) is known to be in the polynomial time class P, a fact established via the Knutson-Tao saturation theorem and the geometry of Gelfand-Tsetlin polytopes [cite: 5, 6]. 

## The Quantum vs. Classical Algorithmic Debate (2024-2026)

One of the most active areas of research spanning 2024 to 2026 centered on whether quantum algorithms could bypass the classical #P-complete bottlenecks inherent in representation-theoretic multiplicities. 

### Larocca and Havlicek's Quantum Algorithms (2024)
In July 2024, physicists M. Larocca and V. Havlicek proposed a suite of quantum algorithms designed to compute Kostka numbers, Littlewood-Richardson coefficients, Kronecker coefficients, and plethysm coefficients [cite: 7]. These multiplicities are critical in Geometric Complexity Theory (GCT), a field attempting to establish lower bounds to separate complexity classes like P and NP (or their algebraic analogues VP and VNP) [cite: 8, 9]. 

Larocca and Havlicek successfully demonstrated that these multiplicities could be computed using quantum algorithms in polynomial time whenever the ratio of the dimensions of the representations is bounded polynomially [cite: 7]. Specifically, their quantum algorithm computed the LR coefficient \( c^\lambda_{\mu\nu} \) in time \( O(f_\lambda / (f_\mu f_\nu)) \) [cite: 10]. 

While they discovered an efficient classical algorithm for Kostka numbers under these same dimension restrictions, they explicitly conjectured that such classical algorithms would *not* straightforwardly translate to Kronecker and plethysm coefficients [cite: 7, 11]. They posited that their quantum algorithms would lead to a superpolynomial speedup for these specific calculations [cite: 7, 11]. Regarding LR coefficients, Larocca and Havlicek hypothesized that an analogous classical algorithm operating in \( O(f_\lambda / (f_\mu f_\nu)) \) time should exist, mirroring the Kostka case [cite: 10].

### Panova's Classical Refutation and Polynomial Algorithms (2025-2026)
The landscape shifted significantly between 2025 and 2026 when mathematician Greta Panova published comprehensive research refuting several core conjectures of the Larocca-Havlicek paper. Panova demonstrated that in many of the bounded cases where Larocca and Havlicek claimed a potential quantum speedup, classical algorithms could also run in polynomial time [cite: 10]. 

Panova's findings vastly limited the mathematical scenarios in which a superpolynomial quantum speedup could actually be achieved [cite: 10, 12]. By analyzing the asymptotic growth of dimensions, she proved that if the partition shapes fall within certain regimes, classical computation is highly efficient. For example, she established that if \( \lambda(n), \mu(n), \) and \( \nu(n) \) are families of partitions of \( n \) such that the dimension \( f_\nu(n) \le n^k \) for a fixed constant \( k \), then the Kronecker coefficient \( g(\lambda(n), \mu(n), \nu(n)) \) can be computed classically in polynomial time \( O(n^{4k^2+1}\log n) \) [cite: 12]. This specific bound actively refuted Conjecture 2 of the Larocca and Havlicek paper [cite: 10, 12].

Regarding Littlewood-Richardson coefficients specifically, Panova expanded upon the classical bounds, exploring their computation to see how closely they aligned with the Kostka number reductions [cite: 10, 12]. She confirmed that, just like Kostka numbers, specific cases of LR coefficients bounded by polynomial dimension ratios can be tackled classically without requiring a quantum framework [cite: 12]. Panova's work emphasized that the lack of a "nice positive formula" for these coefficients (which would natively place their counting in #P) does not preclude efficient classical calculation in constrained spaces [cite: 10].

### Classification in #BQP and GapP (2026)
Adding to the complexity discourse in 2026, P. M. Posta published work analyzing these coefficients through the lens of quantum complexity classes [cite: 13]. Posta proved that a broad class of representation-theoretic multiplicities—including LR coefficients and the notoriously difficult plethysm coefficients—are natively in the complexity class #BQP (the quantum analogue of #P) [cite: 13]. 

Posta obtained this result by executing multiple applications of the Schur transform, improving its dependence on local dimensions [cite: 13]. Furthermore, the research complemented Panova's classical work by proving that these same multiplicities exist in the classical class GapP (functions representable as the difference between two #P functions) [cite: 13, 14]. Posta provided a generalized approach demonstrating how polynomial-time classical algorithms can be derived when specific parameters of the partitions are held fixed, unifying the algorithmic theories developed over the previous two years [cite: 13].

## Algorithmic Breakthroughs via Combinatorial Models (2025-2026)

Parallel to the debates in computational complexity theory, algebraic combinatorialists developed new structural models between 2025 and 2026. These models provided alternative algorithmic pathways for computing LR coefficients that are practically faster and theoretically richer than traditional skew-tableau counting.

### Peelable Tableaux and Temperley-Lieb Immanants (2025-2026)
A major advancement in 2025 was the introduction of a new formula for LR coefficients using "peelable tableaux" compatible with "shuffle tableaux," developed by researchers including Nguyen and Pylyavskyy [cite: 15, 16]. 

Traditionally, evaluating the Schur expansion of the product of two skew-Schur functions required working with skew diagrams \( \lambda * \mu \) [cite: 16]. The new algorithmic rule replaces the skew diagram with a "shuffle diagram," denoted \( \lambda \circledast \mu \) [cite: 15, 16]. The generalized LR coefficient \( c^\kappa_{\lambda/\mu, \nu/\rho} \) is shown to exactly count the number of shuffle-diagram peelable tableaux of shape \( \kappa \) [cite: 15]. 

This method proved computationally superior for generating generalized LR coefficients, particularly when dealing with **Temperley-Lieb immanants** of Jacobi-Trudi matrices [cite: 15, 16]. Temperley-Lieb immanants are a tractable subset of Lusztig's dual canonical bases, and evaluating them computationally has historically been difficult [cite: 17, 18]. Because generating peelable tableaux is algorithmically faster than checking Yamanouchi conditions on standard skew tableaux, this breakthrough provided an efficient pipeline for computing Schur expansions [cite: 15]. 

In 2026, this algorithmic approach was expanded to prove that Temperley-Lieb immanants evaluated on "ribbon decomposition matrices" are Schur-positive [cite: 18, 19]. The peelable tableaux framework is deeply rooted in crystal base theory; it was demonstrated that certain graphs on shuffle tableaux satisfy Stembridge's axioms, forming type A Kashiwara crystals [cite: 15, 17]. Counting the highest weight tableaux of these Temperley-Lieb crystals natively yields the Littlewood-Richardson coefficients [cite: 15]. The researchers also proved that their algorithmic rule interacts perfectly with Bender-Knuth involutions, mathematically recovering the standard symmetries of LR coefficients [cite: 15, 16].

### The Quantum Littlewood-Richardson Map of Type AII (2026)
In 2026, algorithmic computation was further enriched by the formalization of the "quantum Littlewood-Richardson map." Initially proposed algorithmically by Watanabe, this map establishes a bijection between semi-standard Young tableaux of a partition shape with at most \( 2n \) parts, and pairs of tableaux consisting of a symplectic tableau and a recording tableau of skew-shape [cite: 20, 21].

Watanabe's original algorithm provided a new branching model to compute the multiplicities from the general linear group \( GL_{2n}(\mathbb{C}) \) to the symplectic group \( Sp_{2n}(\mathbb{C}) \) [cite: 20, 21]. However, the surjectivity of this algorithmic map was originally concluded indirectly via the representation theory of a quantum symmetric pair of type \( AII_{2n-1} \) [cite: 20, 22]. 

In March 2026, Olga Azenhas provided a rigorous combinatorial algorithm and proof for the surjectivity of the quantum LR map [cite: 21, 23]. Azenhas achieved this by analyzing the "slack data" of the recording tableaux, proving that they are equinumerous to **LR-Sundaram tableaux** [cite: 23, 24]. Azenhas demonstrated that the algorithm computing the inverse of the quantum LR map relies on enriched slack information that packs suitable reverse Schensted column insertion routes [cite: 24]. 

Crucially, Azenhas's algorithmic proof exhibited the exact restriction of the LR orthogonal transpose symmetry map (where \( c^\lambda_{\mu,\nu} = c^{\lambda^t}_{\nu^t, \mu^t} \)) directly to LR-Sundaram tableaux [cite: 21, 23]. This allowed for linear-time bijections between recording tableaux sets and LR-Sundaram tableaux sets, greatly accelerating specific instances of branching multiplicity computations [cite: 21].

### Polynomiality of Stretched LR Coefficients (2025)
Another area of algorithmic interest involves "stretched" Littlewood-Richardson coefficients, denoted \( c^{t\lambda}_{t\mu, t\nu} \), where the partitions are scaled by an integer \( t \). The fact that this coefficient behaves as a polynomial function in \( t \) was famously conjectured by King, Tollu, and Toumazet, and later proven by Derksen and Weyman using semi-invariants of quivers [cite: 2]. 

In 2025, Warut Thawinrak published a highly streamlined, shorter algorithmic proof of this polynomiality [cite: 2]. Thawinrak utilized Steinberg's formula (as derived by Rassart) combined with a simple geometric argument regarding the chamber complex of the Kostant partition function [cite: 2]. By showing that the coefficients act as a polynomial in the variables \( \nu, \lambda, \) and \( \mu \) provided they lie within certain polyhedral cones, Thawinrak's approach bypassed the need for complex quiver theory, offering a more direct computational route for evaluating stretched parameters [cite: 2]. This geometric perspective is closely related to the behavior of Newell-Littlewood numbers, where stretching coefficients yields a quasipolynomial with a period of at most 2 [cite: 1].

## Practical Software Implementations and Classical Rules

Despite the theoretical #P-completeness barrier, practitioners frequently require the exact computation of LR coefficients for applications in symmetric functions and algebraic geometry. Various software packages and recursive rules exist to handle these computations in optimized, practical time for moderately sized partitions.

### `lrcalc` by Anders Buch
The standard bearer for practical computation remains the **Littlewood-Richardson Calculator** (`lrcalc`), a highly optimized C library authored by Anders Buch [cite: 1, 25]. Integrated natively into computational mathematics systems like SageMath, `lrcalc` is designed for the fast computation of single LR coefficients, products and coproducts of Schur functions, skew Schur functions, and fusion products [cite: 1, 25]. 

The algorithm underlying `lrcalc` operates by systematically generating and iterating through LR skew-tableaux (Yamanouchi tableaux) of the appropriate shape and content [cite: 25]. To optimize computation, the software utilizes symmetry reductions; for example, because \( c^\lambda_{\mu\nu} = c^\lambda_{\nu\mu} \), the algorithm redundantly prunes pairs of partitions where the weight of the first is less than the weight of the second, halving the search space [cite: 25]. Furthermore, `lrcalc` features an extension for computing the products of Schubert polynomials, bridging the gap between symmetric functions and Schubert calculus [cite: 1, 25].

### Alternative Combinatorial Rules
When scaling to larger matrices or highly specialized partition spaces, researchers deploy alternative computational rules that vary in algorithmic efficiency:
1.  **Molev-Sagan Recursion:** For calculating entire expansions of \( s_\lambda s_\mu \), the Molev-Sagan Littlewood-Richardson rule for factorial Schur functions provides a robust recursive framework. This recursion is highly structured and can be adapted to compute Jack polynomial LR-coefficients, even though a pure combinatorial interpretation for Jack polynomials remains elusive [cite: 1, 26].
2.  **Sottile's Pieri Rule / Divided Differences:** For computing Schubert polynomials, methods utilizing divided differences on factorial elementary symmetric polynomials can be reduced to Sottile's Pieri rule. This method often outperforms traditional Lascoux-Schützenberger transition equations when implemented in software [cite: 26].
3.  **Linear Equation Systems:** For exact computations involving massive parameters where combinatorial generation fails, algebraic approaches involve expanding the product as a linear combination of Schur functions using finite variables. By specializing the variables to generic real numbers, the system reduces to solving linear equations for unknown coefficients—a technique utilized heavily in custom algorithms [cite: 26].

## Generalizations to Other Mathematical Frameworks (2026)

As the algorithmic bounds for standard LR coefficients become better understood, research in 2026 pushed the LR rule into more abstract algebraic territories. 

A notable example is the work of Hikari Hanaki, who successfully derived a Littlewood-Richardson rule for **Schur P- and Q-multiple zeta functions** [cite: 27]. Inspired by the tableau representation of standard Schur P- and Q-functions, Hanaki demonstrated that while the product of two Schur P-functions expands linearly into other Schur P-functions, a similar expansion holds for Schur P-multiple zeta functions by taking summations over the symmetric group permuting all variables [cite: 27]. 

Hanaki's algorithm incorporated a shifted analogue of the plactic monoid (originally defined by Lascoux and Schützenberger) using shifted Knuth relations and Haiman's mixed insertion [cite: 27]. Because the Knuth relations hold rigorously within this new algorithm, it provided a simple, definitive proof of a long-standing conjecture by Stanley regarding shifted Young tableaux [cite: 27]. Furthermore, Hanaki introduced an expansion formula for skew Schur Q-multiple zeta functions, capable of being refined by restricting the symmetric group to specific subgroups [cite: 27].

## Conclusion

The period from 2024 to 2026 represented a critical inflection point for the algorithmic computation of Littlewood-Richardson coefficients. The initial optimism that quantum algorithms could trivially shatter the computational limits of representation-theoretic multiplicities was carefully tempered by rigorous mathematical proofs demonstrating that classical algorithms, when properly optimized for dimension growth, remain polynomially efficient in the same regimes. 

Simultaneously, classical algebraic combinatorics advanced immensely. The shift away from traditional skew-tableau counting toward more efficient models like shuffle diagrams and peelable tableaux has accelerated the practical computation of generalized LR coefficients and Temperley-Lieb immanants. Furthermore, the algorithmic formalization of the quantum LR map of type AII has provided deep, computable bridges between the general linear and symplectic groups. While the worst-case #P-complete nature of LR coefficients remains mathematically absolute, the boundaries of what is practically and theoretically computable have expanded significantly, ensuring that these fundamental structural constants remain at the forefront of both computer science and algebraic geometry.

**Sources:**
1. [symmetricfunctions.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFk9Q2o9IBt27Or2thO_F0m1WxBOwkTwVjE1KYYbDrkHNBSzSxVFIYSj-zaSg0H8zyXQGO-ynwOjxGRV9wYPIGM9nUOzCaFmMDxhBT7mwKs_styWRnIvZsX8XsyNWmwJWPy8kfUnTmht14xDCsMsdhcCQ==)
2. [combinatorialpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3nTWquYsOeoQaPJpyoDotYIv-ovDQu_2L_UsbdP2YefqGcwOqIsYUGjZi--tAkcl1FCJI0DSJEtpmWbJ7vyU7mIBUils6MFakdM2HC8Mv6L0OgDqnS5CHmaVpSb2rIa-TeellK6-RPTdzGSu_qVfZLOGNqT4Rk8Vd7Ip0qbmzmrZSi11QlN0uPCiXVK7tEhm0jPYZ-ngtyB2tOPtir6ZttLIUx1f1t_kAK5Fn51NdlqBCMTnavpRmBZyKUv_w4ZqbmcofdHU=)
3. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8QSl3Ui2_-qQF9OkejqBqp69BN1QVTEbkpdP9B66AktVuVBeq9NSheXZ-BRLHvN5EnolsJk5e_sYEouqb3QuYbiR2MOVF27tCTFhQGHAc9WLolMAwl1pEE9O4eU_iexUzK5LCWbp_wyRKtIYmIqjhARbfMfAlaiic0Wnp4b_NNWA-tdGdNJgto0n_00Sq8w==)
4. [washington.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkEGV-9AN2JaC2MRXLMU9g5rXDGoDT4Yi8V1UmCWxgFIZq3xhkK1bVjsXG4R6o83RrSnppToC5oZkIEco9vuQ_SetwcYbsbSkY-j_07VAqo2edW-BXbJG6656MLzlstvVquIoQ)
5. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSuv91_r7pvNvFq0uUphuV7rR02zsC7ng2eOAZX3R5uumKB64cMjbX1K5w1vQKJZSRkItrmDvWlgz-zxseUYgJMrInVKkHs5ODFcn2CoGIwj641T7A6In8tyjDGZYUL5jgGAdSypRmsHX1wOpCjdNr)
6. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUEHbByj4ICRrnGZIN3FcApcmGdulQbHrFOLSEL4n5l2tN5nSTuDOPljjrVtswFUGoXRDLvd-ziK4sjuRF14aR_UZv_FZMGD5UXXiJBeq78YwTI2Rimh3Ho0dAndu0ub4=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAmrS3D3fzNDydCeRYKmxSU1QsbKlyNY9i9VdLXYnzXniugfW7JgNJL-n87dwgvt-ALvKEIgy1uqKaEcDitud-sA2lYL9M2n2w2WeiOeWwBR7IDZGSMA==)
8. [uqam.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiBg-EGy-KFBdSQ3LqrPE2jZiZ1UOKTLA9nnN5o8pJu4XQaRMGmQAcTWcE3y-1Ly9lfihudd56Jr3Ss7CvYRpdgP8lv4HW-UW6Yl0cj3eYS0I=)
9. [samuelfhopkins.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxvC7Ydu8ttIGX5v64j73KxOMISBItcJ-LVFMPCM2K1PbOgnePG0W0odzYCe2KkyTKTmXc_KKCXtu9uPw9BNBfv92arpOPx7ksQ56RE7U5-u9YAM9f7aH99HoyX9TvmrXyfZ_T0P06dsXqti7yqyVv8fufxgi-)
10. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFboXN1rj82T3biwr87hPqv0PU45rJW91Vv3OhZK3l08Mt9eYbBd4y6VKIEALeNsBZw3kAPCtR4-kobXcuOEHGJ1ItME7Ph826CLEKWc4SuojBkiHGx)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbnGsqgLPzgJ4JZ2ZuheoS2GBxa4oW-wdmLf4sr2Fwfpm5mZ8_8nK1t1y-qoHKyTWReXeVyr-SFWbAPK1BG3ntjw3T0xv6esqlXoiyhwZgCQsxZzlXww==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGrR0Zq3-3gkJkozfL91-pX0yH6nIgMBnBTo5hh0BcE7RYbUzP1q2OHolIHRMsAuLJXszjpBI6zRpbwRyYBWec6LXyFHNiKBs87d8N3yorm8EM14usuWKzuQ==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAFxOlGY6PBKxwgs6xlky4M1yYAYnHzBEOduacnDs2qD_AYCwKtIiXLyF9YiQtf9CLLEquZ4sFRi_qCRsgjSdA7TvfeFq1dFepuQW8FcCiMgw8oNr4bQ==)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHobyFX_OIvCxpOGPSdXrDazTW_dHks9o218dAOUwecxy257dHSnu_UtzyRvlQuCjGkNvUiVyZgRxFfrudHPbwYcXyiuN3ez5rp-OLtXZbGbF8xFeYg2aG7mij2nf32Qhlwsu-tun1RDrJwpK64yYgmRg0XlcTQYMB2X7G9P7F7hJTzQ3NaxPf6g71A65wkmhb8PLFe8-g0KD8aMA==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJX6QPmG4KawKr6JIF7ew3WRuKlEf37Do_O4WXCMLLNGWXLgPWZeIFNP37UehvOJkTJn7MbXjtlny1OlrwCVDu1SJXdqnaV-0dAgLU-b3id6ra9mrsGQ==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIrlWE99vBbixEvD-eGswm6vk5y4Yh4EIY2AYXTZsgiU2HqYkMYX6K7L48weVfcNQ0N7fR3gYpgbbungHc0XSjeiO2mUvwSKwIwIbQHuVZ9zTtTHwGg-mJeA==)
17. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrV4LG2e-h8DmC9IT0ILfDejlSyZyYlXjK4R3tCW4KyEfciXoLvRg_9zqlBD6g4RViuSwE6vxiOlpwb-l6xxEXcRzcF3e-lY-OzrIgeHWZrZqQw2Az6NSlC4fypRN6BGNMThl4CgytM8-wJVGK0eZxaTaTamhzyfVt8ME=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJhn80zfDq8-vfKLMhtDEVcJr1_7H3gK2D5DY5FrdmVMlMV8i7cGBMS9AI-FZ_-fKo41t8ZubDOWWEVarHFrp2nBZMHll7Phh5bhcXWSiSoxD8GBk68A==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEF_ggAoFYdsHVLVZVFrhHSvqofP3e2-3ZHh-5jHV1PCyiVcpTwJ5SY5if1Fy1UlpVELys6uTsQXQARVFqQ0kWrV_BopRRt2EzjKe20h0Vwj8b_ggFEdA==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzf5zjNDOv36izce-Uck61RW3umeWJSJC6j45_oUVAOLj9JAZ0k907DlUJPmziFirSLIYpDftM3QbzDil2G7H-jBq7QStbEBcSM1lzZwx4w-p1KL5d4w==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkiREn3Om23vTZyKojxvy2tY0saU28GPX5Qi3Thv9QSgcEgk7SqukoyoEi0eK-E9dgSCnIG5tfk6p3AETzWLfyZwdzf-nKNwo6qJJlpSfhS-MPlt7RuQ==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuCyRMN65QvTBSgV_rX9CJz9xjjt1i9_uCwIVaUToFGy3kGDpBqK3GY0UWBhoDdkAJBAHOAjyeIggebiGaWOwD-gUlHvVLf8vvqOML7p6xhnG4cy_Glg==)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFmCv5OrVzqCrl8cDTrn3fPeea4bgvG630JAu_J7X7zeN0lzSgvEbw96NQdJc6S9ETxOKZmLqUmuFzmBZZdACGsFY4blhNmOGrbvezYokJtKTAaTU_UkzYFt_CMJGS3EEFPfCEiHbFjGyz3kXlStlpyPrqrR1XBAJhSCMLNjqZhMP0faFixgZBvb0iKLt0TjYjUdw49N-Kjsid7eihuCrH5HERJm_Cq6VA1R5gMN21EIdR9s-Es562MRddYhB1CmMOwiq_y0KVydsM7Au3eE38m2LW)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGV6SWDEO2DjjdNydWgvg0yNcxdSC9Gc95OqgJNZefkWb3v_57rM2uCKfxuzZrv550hGKvaK0_FmV80qKS2BxgK8b9Aynl2RzJt1JCYvTBCk557abkYTR722spRMrjFbjLXNSWEkR5aBkqFeaJMSJWMqrMoOCyujUoE3fUMiwKqfkA=)
25. [sagemath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETBE47fqB4SAae2bMRBT0rdXctw1vgmChToiiwca5cqthlRWoVzSGxJniu8KzeqpuCRvjyo2wPEFsNDYAumuwRq9FXdPqE8s_MRf6F5kLcmO7OqDkP7xVc5QU5VfyxK6k0s4xdNvDo2NDlM2gi54vr4oUHPtH-Cp81YGX30qfuY6h3)
26. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhI_MYnb0zkroiKNr5LrcWFFqS_3PfyGVkVXpwvkG8xtPw0495dkk86hiE9nGjWnWSWFAwJTBGLShdNQjbpmNhOSlIMtMOC2ZMGnhfky_UmdabjY-e9I6aKv7Tqb-VMpu7uktlJuAeIRTfq_BwqUZbW84CM_E0554-VvIMVzeaOw-12GUj7_Obi8mP7yYoAleGZXq1s4ZNg8Y=)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFasc5oWThn58KGpRM_oDrAgK1PvfO599llcQ23Dz0KagDMzA2S35ZQTI5NgZ7s9bPxlru53UP1L07-roj7wOOD6P_4Mh3T70jxMf0KMZlRZp6i33gCl1TA3rCVrtuRPsdI6vcgzXFYU1YluTRa4Ihyq1hvD6KlEeB2W8f67VxQUGU-xgSeHeMyRRaX9m8e8ZuUaK10DM9NyXjVWgeEtmAE7kGqGhhk1stcjpB8SBg=)

