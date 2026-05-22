# Followup [FU-2026-05-22-008 <- row38]: This report exhaustively details these 2024-2026 breakthroughs, outlining the proofs, the newly disc

**Pythia queue id:** 293
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdPcThQYXB2RlBQYTlfdU1Qb08tc2dBYxIXT3E4UGFwdkZQUGE5X3VNUG9PLXNnQWM
**Elapsed:** 250s
**Completed at:** 2026-05-22T01:24:06.270853+00:00

---

# Deep Research Report: 2024-2026 Breakthroughs in the Asymptotic Spectrum of Tensors and Matrix Multiplication Complexity

**Key Points:**
- **Resolution of a 35-Year-Old Conjecture:** Breakthroughs in early 2026 definitively proved that Strassen’s upper support functionals precisely coincide with quantum functionals, establishing them as universal spectral points over complex numbers.
- **New Matrix Multiplication Exponent Bounds:** The theoretical upper bound for the matrix multiplication exponent, $\omega$, has been compressed to $\omega < 2.371339$ through the introduction of deep asymmetry into the classical laser method.
- **Quantum & AI Acceleration:** Algorithmic discoveries have fragmented the classical landscape. AI models (AlphaEvolve) have discovered a 48-multiplication algorithm for $4 \times 4$ complex matrices, while Quantum Kernel-based Matrix Multiplication (QKMM) proposes an asymptotic complexity of $\mathcal{O}(N^2 \log^2 N)$. 
- **Fine-Grained Complexity Bridges:** The Asymptotic Rank Conjecture (ARC) has been explicitly linked to the Set Cover Conjecture and the Directed Hamiltonian Cycle problem, mapping algebraic tensor bounds to fundamental limits in graph theory.

**Introduction for Laypersons:**
Research suggests that the fundamental mathematical operation of multiplying matrices—a grid of numbers crucial for everything from rendering computer graphics to training deep neural networks—can be computed much faster than the classical "schoolbook" method implies. Since 1969, mathematicians have searched for the absolute speed limit of this operation, governed by a theoretical exponent called $\omega$. Recent breakthroughs between 2024 and 2026 have pushed this speed limit lower than ever before, combining tools from quantum physics, geometry, and artificial intelligence. While some of these new methods are "galactic algorithms"—meaning they are only faster for matrices so large they exceed the memory of any physical computer—others, like AI-discovered shortcuts for small matrices or quantum computing designs, show practical promise. Furthermore, mathematicians have finally proved deep, structural connections between matrix multiplication and quantum entanglement, resolving questions that have been debated since 1991. The evidence leans toward an interconnected computational landscape where the speed of matrix multiplication directly dictates the strict limits of our broader problem-solving capabilities.

---

## 1. Brief Summary - The Question in One Line with Prometheus Context

**Prometheus Context:** The original query interrogates the 2024-2026 state-of-the-art concerning the "asymptotic spectrum of tensors," specifically surfacing from a prior Gemini Deep Research report (requested by Aporia) tracking representations of directed graphs and bilinear operations. The inquiry seeks a substrate-grade evaluation of newly discovered spectral points, theoretical bounds on the matrix multiplication exponent $\omega$, and the exhaustion of specific algebraic topologies.

**One-Line Summary:** How do the 2025-2026 theoretical proofs identifying Strassen's support functionals with quantum functionals, combined with the 2024 asymmetric laser method bounds ($\omega < 2.371339$), mathematically constrain the structural topology of the asymptotic spectrum and narrow the search for universal spectral points?

## 2. Flagged Findings - Current Consensus and Where It Might Be Wrong

The recent timeline of algebraic complexity theory has witnessed rapid shifts in consensus, heavily driven by cross-disciplinary applications of quantum information theory to classical tensor rank problems. 

- **Consensus 1: Convergence of Support and Quantum Functionals.** Since Volker Strassen founded the theory of the asymptotic spectrum in the late 1980s, a central challenge has been explicitly constructing new spectral points [cite: 1, 2]. In 1991, Strassen proposed the upper support functionals $\zeta^\theta$ as candidate spectral points [cite: 1, 3]. In January 2026, Sakabe, Doğan, and Walter proved conclusively that Strassen’s support functionals exactly coincide with the quantum functionals over the complex numbers [cite: 3, 4]. This establishes them as universal spectral points—functionals that are monotonic, normalized, additive, and multiplicative under tensor products—resolving a decades-old open problem [cite: 3].
- **Consensus 2: Unique Determination at the Spectral Edge.** Following the January proof, April 2026 research demonstrated that when the parameter $\theta$ lies along the edges of the foundational simplex (the triangle $\Theta$), these edge support functionals are not just spectral points, but they are uniquely determined by their behavior exclusively on matrix multiplication tensors [cite: 1, 2]. Because the methods used are entirely algebraic, this corollary established the existence of nontrivial spectral points over arbitrary fields for the first time [cite: 1, 2].
- **Consensus 3: Asymmetric Lowering of $\omega$.** The theoretical upper bound for $\omega$ was updated in April 2024 to $\omega < 2.371339$ by Alman, Duan, Williams, Xu, Xu, and Zhou [cite: 5, 6]. This improved upon the January 2024 bound of $\omega < 2.371552$ by circumventing a fundamental limitation of the traditional laser method, which previously required two of the three tensor dimensions to be treated identically [cite: 6].
- **Consensus 4: AI and Quantum Primitives.** AI-driven optimization via AlphaEvolve achieved a novel algorithm for multiplying $4 \times 4$ complex-valued matrices using only 48 scalar multiplications, breaking Strassen’s historic 49-multiplication barrier for this specific subset [cite: 7]. Concurrently, Quantum Kernel-based Matrix Multiplication (QKMM) proposes a dual-parallel extension algorithm utilizing Vector-to-Vector (V2V) inner product correlations to achieve an asymptotic complexity of $\mathcal{O}(N^2 \log^2 N)$ [cite: 8].

**Where the Consensus Might Be Wrong (Flagged Vulnerabilities):**
Despite these monumental theoretical victories, the reliance on highly abstract combinatorial machinery introduces critical epistemological blind spots. The classical bounds for $\omega$ are almost entirely derived from the Coppersmith-Winograd tensor family. We must highlight a severe `PATTERN_PRIME_GRAVITATIONAL_OVERFIT`: the algebraic complexity community's relentless, decades-long optimization of the laser method may represent a gravitational overfit to the highly specific algebraic structure of the Coppersmith-Winograd tensor. By hyper-focusing on this single structural topology to squeeze out microscopic decimal improvements (e.g., from 2.371552 to 2.371339), researchers risk completely ignoring entirely distinct, undiscovered tensor families that might more naturally yield $\omega = 2$. 

Furthermore, regarding the quantum acceleration consensus, the proposed QKMM complexity of $\mathcal{O}(N^2 \log^2 N)$ [cite: 8] must be viewed with intense skepticism. Theoretical quantum complexities frequently ignore the massive data loading and state preparation bottlenecks required to encode classical matrices into quantum states. This perceived asymptotic dominance is likely a `PATTERN_VRAM_TRUNCATION_ARTIFACT`. By truncating the analysis strictly to logical gate complexity and assuming cost-free state preparation, the literature artificially inflates the algorithm's real-world viability, generating a theoretical artifact that cannot survive actual hardware deployment constraints.

## 3. Problem Statement - Precise Object/Result Being Interrogated

The core mathematical objects being interrogated are **tensors**, the **asymptotic spectrum**, and the **matrix multiplication exponent ($\omega$)**.

**The Semiring of Tensors and Asymptotic Restriction:**
Let $F$ be a field. A 3-tensor $t \in F^{n_1} \otimes F^{n_2} \otimes F^{n_3}$ represents a bilinear map. The study of tensor complexity is governed by the asymptotic restriction preorder, denoted $s \gtrsim t$. This preorder asks if the $n$-th tensor power of $t$ can be obtained from the $(n+o(n))$-th tensor power of $s$ by applying local linear maps to the tensor legs as $n \to \infty$ [cite: 9, 10]. The tensor operations of direct sum ($\oplus$) and tensor product ($\otimes$) equip the space of tensors with the structure of a commutative semiring [cite: 11, 12].

**The Asymptotic Spectrum of Tensors ($\Delta(X)$):**
To systematically study the asymptotic restriction preorder, Strassen (1986) introduced the asymptotic spectrum [cite: 11, 13]. The asymptotic spectrum of a semiring $R$ is the topological space of all "spectral points"—maps $\phi: R \to \mathbb{R}_{\ge 0}$ that preserve the semiring structure (additive, multiplicative, monotonic, and normalized) [cite: 9, 10]. If one can identify all universal spectral points (points valid for the semiring of all tensors), one completely characterizes the asymptotic subrank and asymptotic rank of any tensor [cite: 9].

**Support Functionals vs. Quantum Functionals:**
Strassen proposed the upper support functionals $\zeta^\theta$ (where $\theta$ ranges over a probability simplex $\Theta$) as candidate spectral points [cite: 1, 2]. However, his initial proof relied on nonconstructive methods via Zorn's Lemma [cite: 9]. In 2018, Christandl, Vrana, and Zuiddam introduced "quantum functionals" $F^\theta$ derived from quantum information theory—specifically, utilizing entanglement polytopes, quantum entropy, and the quantum marginal problem [cite: 10, 14]. The precise relationship being interrogated and definitively resolved in 2026 is the exact mapping $\zeta^\theta(t) = F^\theta(t)$ [cite: 3].

**The Asymptotic Rank Conjecture:**
Strassen's Asymptotic Rank Conjecture (ARC) posits that for a concise and tight tensor $Q \in F^{c \times c \times c}$, the tensor rank of its $n$-th tensor power is bounded by $c^{n+o(n)}$ [cite: 15, 16]. Since the matrix multiplication tensor for $2 \times 2$ matrices is a $4 \times 4 \times 4$ tensor, the truth of the ARC for this specific tensor would immediately imply that $\omega = 2$ [cite: 15, 16].

## 4. Status & Bounds - Last Known Status, Current Best Bounds, Conditional Qualifiers

**1. The Matrix Multiplication Exponent ($\omega$):**
- **Last Known Status (Classical):** $\omega < 2.371339$ (Established April 2024 by Alman et al.) [cite: 5, 6]. This galactic algorithm relies on severe asymmetric analysis of the laser method, superseding the brief January 2024 bound of 2.371552 [cite: 6, 17].
- **Small Matrix Exact Bounds:** AlphaEvolve has bounded the exact scalar multiplication count for $4 \times 4$ complex-valued matrices to 48 operations [cite: 7].
- **Last Known Status (Quantum):** The QKMM framework claims an asymptotic complexity of $\mathcal{O}(N^2 \log^2 N)$ for $N \times N$ matrix multiplication, bounding the quantum exponent to effectively $2$, though gated by the aforementioned state preparation artifacts [cite: 8].

**2. Asymptotic Spectral Points:**
- **Current Bounds:** The upper support functionals are now proven universal spectral points over complex numbers [cite: 3].
- **Arbitrary Fields:** For the first time, nontrivial spectral points have been proven to exist over arbitrary fields (positive characteristic) specifically along the edges of the simplex $\Theta$ [cite: 1, 2]. 
- **Computability:** These edge support functionals can be calculated in deterministic polynomial time using Harder-Narasimhan filtrations from quiver representation theory [cite: 1, 2].

**3. Conditional Qualifiers (The Asymptotic Rank Conjecture):**
The Asymptotic Rank Conjecture remains globally open but tightly coupled to fine-grained complexity limits. 
- *Qualifier A:* If the ARC is true over field $F$ (or even approximately true for a single $7 \times 7 \times 7$ tensor), then the Set Cover Conjecture is demonstrably false [cite: 13, 16].
- *Qualifier B:* If the ARC is true, there exists a randomized algorithm deciding the Directed Hamiltonian Cycle problem in $\mathcal{O}((2-\epsilon)^n)$ time, breaching a massive wall in graph theory complexity [cite: 15, 16].

## 5. Literature (Primary Sources) - arXiv IDs, Journal Cites, Authors, Dates

*Note: The following represents primary substrate-grade literature detailing the 2024-2026 shifts.*

1. **Sakabe, K., Doğan, M. L., & Walter, M. (January 2026).** *Strassen's support functionals coincide with the quantum functionals.* arXiv:2601.21553. [cite: 3, 4]. (Proves the exact equivalence between $\zeta^\theta$ and $F^\theta$ via Fenchel-type duality).
2. **Sakabe, K., Doğan, M. L., & Walter, M. (April 2026).** *The edge of the asymptotic spectrum of tensors.* arXiv:2604.01386. [cite: 1, 2]. (Establishes edge support functionals, quiver representation connections, and arbitrary field universality).
3. **Alman, J., Duan, R., Williams, V. V., Xu, Y., Xu, Z., & Zhou, R. (April 2024).** *More Asymmetry Yields Faster Matrix Multiplication.* arXiv:2404.16349. [cite: 5, 6]. (Establishes the current $\omega < 2.371339$ bound).
4. **Björklund, A., & Kaski, P. (June 2024 / February 2025).** *The asymptotic rank conjecture and the set cover conjecture are not both true.* Proceedings of the 56th Annual ACM Symposium on Theory of Computing (STOC 2024) / Innovations in Theoretical Computer Science (ITCS 2025). [cite: 13, 16]. (Links ARC to Hamiltonian cycles and Set Cover).
5. **Kaski, P., & Michałek, M. (February 2025).** *A Universal Sequence of Tensors for the Asymptotic Rank Conjecture.* ITCS 2025, LIPIcs Vol 325. DOI: 10.4230/LIPIcs.ITCS.2025.64. [cite: 13, 18]. (Constructs explicit universal tensors characterizing worst-case tensor exponents).
6. **Xiong et al. / QKMM Authors (February 2026).** *Quantum Kernel-Based Matrix Multiplication Algorithm.* arXiv:2602.05541. [cite: 8]. (Proposes the $\mathcal{O}(N^2 \log^2 N)$ algorithm).

## 6. Attack Vectors - Live Techniques; Exhausted Approaches

**Live Techniques:**
- **Entropy Optimization on Entanglement Polytopes:** Leveraging the quantum marginal problem, researchers are actively optimizing quantum entropy over moment polytopes to extract precise values for asymptotic slice rank and subrank [cite: 3, 14]. 
- **Fenchel-Type Duality on Hadamard Manifolds:** Hirai (2025) introduced asymptotic duality theorems on Hadamard manifolds. This non-Euclidean convex optimization is actively utilized to bypass the non-constructive Zorn's lemma barriers, rigorously pinning down spectral points [cite: 3, 19].
- **Algorithmic Invariant Theory & Quiver Representations:** By linking edge support functionals to Harder-Narasimhan filtrations, researchers have successfully translated abstract algebraic limits into deterministic polynomial-time computability [cite: 1, 2].
- **Asymmetric Laser Method:** The dominant attack vector for $\omega$ currently relies on deep asymmetry, mathematically uncoupling the historical requirement that two of the three dimensions of the decomposed tensor must be treated identically [cite: 6].

**Exhausted Approaches:**
- **Symmetric Laser Method:** The classical laser method analyzing the Coppersmith-Winograd tensor hit an insurmountable barrier around $2.371552$. Further reductions explicitly required breaking structural symmetries [cite: 6, 17].
- **Non-constructive Spectral Search:** Strassen’s original methodology for proving the existence of universal spectral points relied on abstract partial orders and Zorn's Lemma. This has been entirely abandoned in favor of explicit constructions via quantum information invariants [cite: 9].

## 7. Cross-References - Related Open Problems, Anti-Anchors, Candidate Primitives

**Related Open Problems:**
- **The Cap Set Problem in Positive Characteristic:** A major frontier involves translating these spectral points to arbitrary fields. In combinatorics, bounding progression-free sets (like the cap-set problem) relies heavily on the slice-rank upper bound degenerating in specific characteristics (e.g., characteristic 3) [cite: 2, 9]. 
- **Higher-Mode Tensor Spectra:** The spectrum of $d$-mode tensors (where $d \ge 4$) contains points entirely distinct from quantum functionals. Identifying these hidden points remains a primary target for extending computational complexity bounds [cite: 2].

**Anti-Anchors:**
- **Gauge Points (Flattening Bounds):** The most fundamental anti-anchors in the asymptotic spectrum are the $2^{k-1}-1$ flattening ranks. In a 3-tensor representing matrix multiplication, these correspond to the three vertices of the simplex $\Theta$. For decades, these were the *only* known spectral points in positive characteristic, acting as rigid boundaries that repelled further spectrum mapping [cite: 2, 9].

**Candidate Primitives and Calibration Confound:**
Candidate primitives for future matrix algorithms heavily feature quiver invariant primitives and V2V (Vector-to-Vector) direct inner product quantum mappings [cite: 1, 8]. 

However, we must apply `PATTERN_CONDUCTOR_CONFOUND` when assessing the push to extend complex-field spectral geometries into finite, positive-characteristic fields. Positive characteristic fields introduce severe algebraic irregularities where continuous geometric tools (like gradient flows on Hadamard manifolds) abruptly fail. Trying to blindly map complex-field spectral points directly to arbitrary fields without accounting for modular arithmetic properties risks a profound conductor confound. The invariant "conductor" (the characteristic of the field) confounds the expected topological continuity of the asymptotic spectrum, causing assumed universal points to artificially degenerate or exhibit false sub-multiplicativity. Future research attempting to bridge algebraic complexity and additive combinatorics must mathematically isolate the characteristic conductor to prevent topological misinterpretations.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3ovZzcCFlgEeBaMYscKZj2vaU4CDdwNf37nriJIb63QLEzDiE-KdoDnth3D2pUuIAvbrTZKqNWoMaRBENrxdQUB8H3HFLodqi-aL8BAT-Ib6ZOaIQKw==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9RsehWxn3PvKwr4vCmNKZI7QOJIFqvJtEfAUMBcym41hz8q8v0eMzwIKfRJgwyXQseXfg1D2CCYrd_nU51wFhMni3ON6Dn9G43Req-Gai3ZRQVwKpKckvVQ==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_YSwNWOSEtppshY86DorDlJc7rwB9sQIMPtEmC9BKvtJzC3ApGN_TYfzXDoRoKQ0Ed8RNlrAor84mGwyuvX005VEkTw9HZ2l6kANAXM6kD4gChD_iaxTMYw==)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGlfRsoTQOgwNJTQ_m4eoPqj8YHhAjTMf_NwW2mfSWhs7wvBwuIQyW6vIeonhz5-NFMYXbVQfTpEjJXgQ04FqMssqTpGyoYLlwtWpQ8VsBTHgj2iSJ1PEw-ZuoEycS1YH9sf4emK0FUVGxqALLqqKdWdXAYUW4s8LGa7x7AWRCK1xi7fs-iGQKzVg7X2qPQBa_7shydYQ==)
5. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDaF6OvB68o5ezhHXLBGKpDjjBxcyD6MBBbTChCx0-r_XcOkt2DHeBsha1OsXqDJeQR5J0t3vOvLAcojQ7knTOXzz80OKVMPw2R89LTWIsQt7x_Fwe10xSUjIYAWhGKFcLpJzB0grvyKOu69O0HhwMg6Rm)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjkMF9Kz2YQBUDI1z2q_gPEYM-_qYfWrA8_CwSSoT3hM9m2qhvwnRmHAB6xxTRaZ0hHsiMci0GVGUERqMWOkeArojJIFb1iEBs-dGFvQRQGSw649Y61Q==)
7. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPCUWbP7W8M38oX4BPxbfeYxnR1ixY6IqrwT-xpM7tjaDGjX_3O__yqEIlizQrLr4RXY7GKQL_lzteyY5s-PwcglM-6unktcN4vr71UOOK7dFjpo6-PIgq0tRwqFjBT2A90Chmyzc7aIuDWbQG2njgU2xyw0nHkmTycGZKqqOCu_1milACj6GXX-pb8aYkwtX3DkXKQPQQarFhvMuPs1aLMZkWzYqfchuu39r3fG0pp5-eCc_wbQXv)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-a-3BOMWlSQyA84W3Q3SLROlR6D0XB-idfcI1bBLI1tYWkYdd8OGSW_FLIKrowYO0-8vt2_3T9T7V7dWtJJE3IlL-NZozCH9gQRotr_Tzvy2kFKHJc2T2ow==)
9. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQsOd909hVZjsAnZX9-_3_QsRDVMaiB1GpzSqfXByiwcj2Lj48dGJlESTpKXDoz1pIQx5UmmWgT43x2aeq8tTQJCjvSsfygNnM9Wx4mwqRgXqOX7so1Wlik9sWuebongQT0biYPv6-UY-pOtESK59p1QtENYz-eFiiSC_tW6jIxi8oOxs9oj38M19T1EMq3H_-50rn)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgxUjP9_fsk10U-M2RtndvgXSb2rlbPPNnmnnC-hJUjHEj_vomtUULriDOAXZwom4cTMN_x3Zy8Bu0SzK0-AgFsOvLTLLUdADpk-Pz0D_K5r7JvnRG1g==)
11. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFX6TyY9SbbZSBgsxjqMK1q_edV1nAmYMUYyw0hNZBvN4Vli3TXiQYfm01x542fAYzByRbf-ESys3MrVBorDWpIGbPsMyei6c-VKZM-xxjG40jbOYay5NLfWjCLIW0Wg_UY7RG4lf-brFAIxYGvPJdT_6aJAOSF1Od0plUL0TdLZ5dDcvg=)
12. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvsQfMDI19YVfZcrztZ7jQq090qviXQ23uEypy4HBxjexLRmIpVez8wePf5Nkhg5_qyW9KE2f3GdYOtOr_fGXhH7-pkuBOZuiMz58z2YwxYG5pz7TQv1TBYFTrjStAY3ZymN4KcaWPVHDhFhys166xxOeos2uWQCm9fl5O8oLmHfk=)
13. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmz_bmOJdCKjIGazgF2JnBEwoukLvg7onyRONWpUAtR9vOtwdO6R6uokO8e_RnV8UtyAYuQv4RK1locwiAyAhM8mYQndI4ZMoal3fhnzZA_knXC3j1U58o3oxBfqVSAg-T1qrRzXu4OWySVk3RaxbRjVJcxIcShGEbhQ5nLQ==)
14. [uva.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbdK8iEtZX_eBj5lVAatXBQoXSrNzPBD9CTg7F5GFcGsg83_THB0GWPZJCNlMRyWHaLRWxypL1hcUNQPtoQ7ygG50KbBcchYnRgFUTTUvK4JdGESwqDrKCcKKocq-PMtjEtutstRvMuxquWf5LF5Ua57Jr07eawivNaBNStCcIGfNFvvfAEGX1uKZVt6fX2uZq5JDOkpM8wJgWD-hWMkTBOImoQULUXFoXqDewTDatWwM-aICC_W9xFwPWMu4_kVh3Vbv-szbfJWP3)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE72bfXGqKjoVeyxOFZ1yhdLJ0W2bibd1VAomAvP0DF6njJL6Pug41ZHPPzBt5ZOdkDsY_eakwNJhShGoTcIUjuML4QBoosYz3bLIQDXwqtE-z6dO9-1g==)
16. [aalto.fi](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEUz-4Z-rUzy6ohHAM-kXjG0VdvdDAcdYU-fLe_nhLPEDyilL30ph0wO3hnLZGWshGv6-7Gvu6jyZ4EkalHO92B80QweATHGdkO3CyCqh3zpKZVDvhs1KJfghfw9SbzzcpVMliJtbqRbl7saPQRbfygmV-CZPg7CB6HSri1HZ8SCBKN3pcb6I5aF9Rgyk=)
17. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFR_K88HfT_035ZkcYpEnvs_oCmDxQCwgd3jHxbI9GZVRHv0TPf-wU-jB33tDxAQjhQ2g2lu-UrGKYaGyjkgJqbmOA8G69rzbO1HY7nHt95GYSXOA2OEdGuBEoOS9y14Z5z_QriL4cDFF59sXilvpL9k_RlOOIi-1ClP38Edz4GM-BMEdfyxW1GYoKHAAh7mVPcq-UkKN9Y5a2ZFxw=)
18. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5xijZW-jtsgQLeRBicXm2D_VSKYrQNvWuJFlNGA_jXk8OAQtlIGkm8ibA2U8lcurunRZ0lvMuloGhrsIWsejrnzLZAjIm459qxafbdJJLIQIegUgZV9MHfAnhSuSRS0tv_GAefTnVa5fPug0g1ozLcQ==)
19. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhe8S4Eeo036eJCoI8ZwhkmqAJdQMHf2MZcUBxY2LBe4Sxaz24xUB-Mc8_BLFcpdmjst7JsM5IkmGKNlWPgnYtqU9J_oCrdCGNpvEBCcKh64ug7fB0y2PDnbPByAVzOGePnZ0x05r8PTNcdnxlX60b9bpzqutaPcU-d_mafPqq5dwHcXeO8w3YnbnUu5Z85Yx0hdyW6z1yWEdM0NaumCml2kMHUvHOb4VvcEtk69oLpSQAuVZhVujzFdcbc5hfGHrwTtO-X7ZG)

