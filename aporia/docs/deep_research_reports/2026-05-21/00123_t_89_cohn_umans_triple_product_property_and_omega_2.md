# T#89 Cohn-Umans triple product property and omega=2

**Pythia queue id:** 123
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdrQ1lQYXNPNUVfMlZqTWNQdk8yRDRBaxIXa0NZUGFzTzVFXzJWak1jUHZPMkQ0QWs
**Elapsed:** 250s
**Completed at:** 2026-05-21T15:40:59.712925+00:00

---

# The Cohn-Umans Group-Theoretic Framework for Matrix Multiplication and the Pursuit of \(\omega=2\)

### Key Points
*   **The Matrix Multiplication Exponent**: The computational complexity of multiplying two \(n \times n\) matrices is denoted by \(\omega\). While traditional methods require \(O(n^3)\) operations, a central conjecture in theoretical computer science posits that \(\omega = 2\), meaning matrices could theoretically be multiplied in near-quadratic time.
*   **The Cohn-Umans Framework**: Proposed in 2003, this approach maps matrix multiplication into the group algebra of a finite group. It relies on finding subsets within a group that satisfy a specific combinatorial condition known as the **Triple Product Property** (TPP). 
*   **Barriers in Finite Groups**: Recent breakthroughs in additive combinatorics (such as the resolution of the Cap Set conjecture) have ruled out bounded-exponent Abelian groups from achieving \(\omega = 2\). Further research has also identified insurmountable barriers in nilpotent groups, symmetric groups, and finite groups of Lie type.
*   **Infinite Lie Groups and Separating Polynomials**: To bypass the limitations of finite groups, researchers have recently extended the framework to continuous Lie groups. This introduces new mechanisms, such as **separating polynomials**, offering a promising but highly complex theoretical pathway toward proving \(\omega = 2\).

### Understanding the Matrix Multiplication Problem
Matrix multiplication is a foundational operation in linear algebra, essential to countless applications in physics, computer science, machine learning, and engineering. For decades, the standard schoolbook method was the only known way to multiply two matrices, requiring a number of operations proportional to \(n^3\). In 1969, Volker Strassen shocked the mathematical world by proving that one could multiply matrices faster than \(n^3\), specifically in \(O(n^{2.81})\) time. This discovery launched a decades-long race to find the true "speed limit" of matrix multiplication, quantified by the exponent \(\omega\). If \(\omega = 2\), it would mean algorithms exist that are almost as fast as merely reading the data within the matrices.

### The Group-Theoretic Solution
Most improvements to the speed of matrix multiplication since the late 1980s have relied on a highly complex technique known as the **laser method**. However, this method has mathematical limitations that prevent it from reaching \(\omega = 2\). In 2003, researchers Henry Cohn and Chris Umans proposed a completely different perspective: translating the matrix multiplication problem into the realm of group theory. By embedding matrices into a mathematical structure called a "group algebra," researchers can theoretically leverage the symmetries and representations of the group to perform the multiplication significantly faster. The success of this method hinges on finding three subsets within a group that do not overlap in a very specific, structured way—a condition called the **Triple Product Property**. 

### The Current Frontier
Despite the elegance of the Cohn-Umans framework, mathematicians have discovered that many standard finite groups (like Abelian groups and symmetric groups) simply do not possess the required structural properties to prove \(\omega = 2\). These negative results are not seen as failures, but rather as guideposts. Currently, the most cutting-edge research has shifted toward infinite, continuous groups (Lie groups). By utilizing geometric concepts and polynomials, mathematicians are currently exploring whether continuous spaces hold the final key to achieving the theoretically optimal quadratic time for matrix multiplication.

---

## Introduction

Determining the asymptotic algebraic complexity of matrix multiplication is one of the most prominent and enduring open problems in theoretical computer science and algebraic complexity theory [cite: 1, 2]. The computational complexity of multiplying two \(n \times n\) matrices over a field \(\mathbb{F}\) is succinctly represented by the matrix multiplication exponent \(\omega\), defined as the infimum over all real numbers \(c\) such that the multiplication can be performed using \(O(n^{c + \epsilon})\) field operations for any \(\epsilon > 0\) [cite: 3, 4]. Using a naive lower bound (as all \(2n^2\) entries of the input matrices must be processed) and the standard schoolbook row-column multiplication for the upper bound, it trivially follows that \(2 \leq \omega \leq 3\) [cite: 3, 5]. 

Since Volker Strassen's seminal 1969 discovery of a sub-cubic algorithm running in \(O(n^{\log_2 7}) \approx O(n^{2.81})\) time [cite: 5, 6], researchers have aggressively pursued the conjecture that \(\omega = 2\) [cite: 4, 7]. The implications of \(\omega = 2\) are profound: a near-linear time algorithm for matrix multiplication would immediately yield near-optimal algorithms for a vast array of problems in linear algebra, graph theory, and beyond [cite: 7]. 

For several decades, the state-of-the-art upper bounds on \(\omega\) have been achieved using the **laser method**, a sophisticated generalization of the Strassen and Coppersmith–Winograd algorithms developed in 1990 [cite: 1, 5]. While the laser method has successfully pushed the upper bound down to approximately \(2.37188\) (achieved by Duan, Wu, and Zhou in 2022 by overcoming specific barriers like "combination loss" using asymmetric hashing) [cite: 5], various barrier results have demonstrated severe limitations to this approach [cite: 1]. For instance, Ambainis, Filmus, and Le Gall proved that the laser method, in its standard form, cannot achieve an exponent lower than \(2.3725\) [cite: 5].

To circumvent the inherent limitations of traditional tensor methods, Henry Cohn and Chris Umans introduced an entirely novel group-theoretic framework for matrix multiplication in 2003 [cite: 3, 6]. By shifting the problem from the realm of ad-hoc bilinear algorithms into the structured domain of representation theory and group algebras, this framework provided a systematic approach to algorithm design. It is conjectured to be powerful enough to prove \(\omega = 2\) [cite: 8, 9]. The viability of the Cohn-Umans approach relies on identifying groups with subsets that satisfy a combinatorial condition known as the **Triple Product Property** (TPP) [cite: 3, 10].

This comprehensive report explores the theoretical underpinnings of the Cohn-Umans framework, details the formal definition and implications of the Triple Product Property, analyzes the sequence of barrier results that have ruled out various finite groups as candidates for proving \(\omega = 2\), and explores the recent transition to infinite Lie groups as a promising frontier for optimal matrix multiplication.

## Mathematical Foundations of Matrix Multiplication Complexity

### Bilinear Complexity and Tensor Rank
Matrix multiplication can be naturally expressed as a bilinear map. The complexity of evaluating this bilinear map is closely tied to the tensor rank of the matrix multiplication tensor, often denoted as \(\langle n, n, n \rangle\) [cite: 11]. The problem of designing a fast matrix multiplication algorithm is equivalent to expressing this tensor as a sum of rank-one tensors. 

If the tensor rank of \(\langle n, n, n \rangle\) is \(m\), it implies that two \(n \times n\) matrices can be multiplied using \(m\) scalar multiplications [cite: 11]. Strassen's realization that bilinear computation operates without loss of generality is a cornerstone of this methodology [cite: 11]. If a tensor decomposition provides a method to multiply two \(k \times k\) matrices with fewer than \(k^3\) multiplications, the technique can be applied recursively to yield an algorithm with asymptotic complexity \(O(n^\omega)\) [cite: 5].

### The Limits of the Laser Method
The **laser method** essentially takes a large tensor power of a base tensor (such as the Coppersmith-Winograd tensor) and uses a combinatorial zeroing-out technique to extract independent matrix multiplication tensors [cite: 5, 7]. However, the laser method operates under constraints. As demonstrated by Ambainis et al., evaluating higher and higher tensor powers of the Coppersmith-Winograd identity asymptotically hits a strict limit [cite: 5]. 

Furthermore, Blasiak et al. identified a broader barrier by defining the "irreversibility" of a tensor [cite: 1]. They proved that any approach utilizing an irreversible tensor in an intermediate step—such as starting with it in the laser method—cannot yield \(\omega = 2\). The best upper bound achievable is strictly lower bounded by twice the irreversibility of the intermediate tensor, with lower bounds on irreversibility derived from quantum functionals and Strassen support functionals [cite: 1]. These accumulating barriers have made the alternative group-theoretic framework increasingly vital.

## The Cohn-Umans Group-Theoretic Framework

In 2003, Cohn and Umans proposed embedding the \(n \times n\) matrix multiplication problem into the multiplication of elements within a group algebra \(\mathbb{C}[G]\) of a finite group \(G\) [cite: 11, 12]. The complexity of the resulting matrix multiplication algorithm then depends intrinsically on the representation theory of the host group \(G\) [cite: 3, 9].

### Embedding in Group Algebras
The core concept is to define a mapping from matrices to elements of the group algebra. Let \(A\) and \(B\) be matrices. The framework seeks to map \(A \to \dot{A} \in \mathbb{C}[G]\) and \(B \to \dot{B} \in \mathbb{C}[G]\) such that the entries of the product matrix \(AB\) can be precisely read off from the coefficients of the convolution product \(\dot{A} \cdot \dot{B}\) in the group algebra [cite: 10, 12].

The group algebra \(\mathbb{C}[G]\) consists of elements of the form \(\sum_{g \in G} a_g g\). Because the group algebra is semi-simple, it is isomorphic to a block-diagonal matrix algebra [cite: 11]. Computing the product in \(\mathbb{C}[G]\) is analogous to the fast polynomial multiplication using the Fast Fourier Transform (FFT) [cite: 12, 13]. If the irreducible representations of \(G\) behave "nicely", and the embedding structure allows for efficient coefficient extraction, one obtains a fast algorithm [cite: 12]. 

Specifically, the number of multiplications required in the group algebra is bounded by \(\sum d_i^\omega\), where \(d_i\) are the dimensions of the irreducible representations of \(G\). The standard approach uses the trivial upper bound of \(3\), requiring at most \(\sum d_i^3\) multiplications, but since \(\sum d_i^2 = |G|\), a group that supports a highly efficient embedding can drastically reduce the computational complexity [cite: 4, 11].

### The Triple Product Property (TPP)
For this embedding to avoid catastrophic "collisions" (where different products of matrix entries sum to the same group element), the group \(G\) must contain three subsets \(X\), \(Y\), and \(Z\) that satisfy a combinatorial disjointness condition known as the **Triple Product Property** (TPP) [cite: 2, 5].

**Definition 2.1 (The Triple Product Property)**: Three subsets \(X, Y, Z\) of a group \(G\) satisfy the TPP if, for all \(x, x' \in X\), \(y, y' \in Y\), and \(z, z' \in Z\), the equation:
\[ x (x')^{-1} y (y')^{-1} z (z')^{-1} = 1 \]
implies that \(x = x'\), \(y = y'\), and \(z = z'\) [cite: 2, 13, 14]. 

Alternatively, using the quotient notation defined in the literature, for any \(s \in Q(X), t \in Q(Y), u \in Q(Z)\) (where \(Q(S) = \{s_1 s_2^{-1} \mid s_1, s_2 \in S\}\)), the condition \(stu = 1 \implies s=t=u=1\) [cite: 4, 11, 14].

If the subsets satisfy this property, one can safely embed an \(|X| \times |Y|\) matrix \(A\) and a \(|Y| \times |Z|\) matrix \(B\) into \(\mathbb{C}[G]\). The embedding is constructed as:
\[ \dot{A} = \sum a_{x,y} (x y^{-1}) \]
\[ \dot{B} = \sum b_{y,z} (y z^{-1}) \]
The coefficient of the term \((x z^{-1})\) in the product \(\dot{A} \cdot \dot{B}\) perfectly isolates the corresponding entry of the matrix product \(AB\), exactly because the TPP ensures no other combination of \(x', y', z'\) can evaluate to the same group element [cite: 11, 12].

### The Simultaneous Triple Product Property (STPP)
To achieve the optimal bounds approaching \(\omega = 2\), the framework was generalized to the **Simultaneous Triple Product Property** (STPP). The STPP deals with a collection of disjoint matrix multiplications [cite: 7, 13]. 

An STPP construction involves a collection of triples of subsets \(A_i, B_i, C_i \subseteq H\) inside a group \(H\). For all \(i, j, k\), the subsets satisfy the condition:
\[ a_i (a'_i)^{-1} b_j (b'_j)^{-1} c_k (c'_k)^{-1} = 1 \implies i=j=k \text{ and } a_i=a'_i, b_j=b'_j, c_k=c'_k \]
[cite: 12, 14]. 

When properly formulated, the overall efficiency of an STPP construction relies heavily on the packing bound:
\[ \sum (|A_i| |B_i| |C_i|)^{\omega/3} \leq |H| \]
[cite: 14]. If one can find a family of groups and subset triples such that \(|A_i||B_i||C_i| = |H|^{3/2 - o(1)}\), this framework is mathematically capable of proving \(\omega = 2\) [cite: 4]. 

In 2005, Cohn, Kleinberg, Szegedy, and Umans formalized conjectures proposing specific families of groups (including wreath products and Abelian groups) that, if containing subsets satisfying the STPP with optimal sizes, would establish \(\omega = 2\) [cite: 3, 6, 11].

## Analyzing \(\omega=2\) Conjectures and Additive Combinatorics

The 2005 conjectures heavily intersected with problems in additive combinatorics [cite: 3, 15]. Evaluating the TPP in Abelian groups translates directly into questions about sum-free sets and progression-free sets [cite: 14, 16]. 

In an Abelian group, the TPP condition rewrites to:
\[ (x_1 - x_2) + (y_1 - y_2) + (z_1 - z_2) = 0 \iff x_1 = x_2, y_1 = y_2, z_1 = z_2 \]
[cite: 12]. This is structurally identical to asking for sets that avoid certain linear equations, fundamentally linking matrix multiplication complexity to objects like Salem-Spencer sets (sets lacking three-term arithmetic progressions) [cite: 10, 13]. 

Additionally, constraints placed by the TPP have implications for the "corners problem." The corners problem asks for the maximum size of a subset \(S \subseteq [n]^2\) containing no three points of the form \((x,y), (x, y+\delta), (x+\delta, y')\) for \(\delta \neq 0\) [cite: 15]. Shkredov established upper bounds for this problem, while Petrov provided lower bounds. The theoretical overlap indicates that proving bounds like \(|S| \leq O(n^{1+\epsilon})\) for the corners problem would inherently rule out obtaining \(\omega = 2\) via large families of Abelian groups within the Cohn-Umans framework [cite: 6, 15]. 

The connection between the TPP and the Erdős-Szemerédi sunflower conjecture, as well as the Coppersmith-Winograd "no three disjoint equivoluminous subsets" conjecture, further highlights how algebraic complexity theory is deeply tethered to extremal combinatorics [cite: 6].

## Barrier Results: Ruling Out Finite Groups

While the Cohn-Umans framework encapsulates all state-of-the-art upper bounds on \(\omega\) (including the \(O(n^{2.37286})\) limits) and initially seemed like a limitless path to \(\omega = 2\), rigorous barrier results over the past decade have systemically eliminated almost all natural families of finite groups as viable candidates [cite: 4, 8, 16].

| Group Family | Status for Proving \(\omega=2\) | Key Mathematical Tool/Reasoning | Source |
| :--- | :--- | :--- | :--- |
| **Abelian (Bounded Exponent)** | Ruled Out | Cap Set Conjecture, Slice Rank, Tricolored Sum-Free Sets | [cite: 3, 14, 17] |
| **Nilpotent (Bounded Exponent)** | Ruled Out | Polynomial Method, Augmentation Ideal Shrinkage Rate | [cite: 8, 16] |
| **Symmetric Groups (\(S_n\))** | Ruled Out | Young Subgroups Limitation | [cite: 8] |
| **Finite Groups of Lie Type** | Ruled Out | Irreducible Representation Dimensions, Gowers' Quasirandom Sets | [cite: 1, 18, 19] |

### The Cap Set Breakthrough and Abelian Groups
The earliest major blow to the 2005 conjectures came from the resolution of the Cap Set conjecture. A cap set is a subset of \(\mathbb{F}_3^n\) containing no lines; equivalently, if \(u, v, w\) belong to the set, then \(u + v + w = 0\) implies \(u=v=w\) [cite: 14]. 

In a breakthrough sequence of papers by Croot, Lev, Pach, Ellenberg, and Gijswijt, the polynomial method was used to severely bound the size of cap sets [cite: 3, 20]. Blasiak, Church, Cohn, Grochow, Naslund, Sawin, and Umans extended this result to bound the size of **tricolored sum-free sets** in Abelian groups of bounded exponent [cite: 3, 14, 21]. 

As a byproduct, they utilized a variant of tensor rank introduced by Terence Tao—known as **slice rank**—which provides a quantitative understanding of unstable tensors from geometric invariant theory [cite: 14, 16, 20]. Partition rank (introduced by Naslund) and hyperdeterminants also generalized these lower bounds on tensor ranks [cite: 16]. Because the size of TPP sets in Abelian groups of bounded exponent is strictly limited by these combinatorial bounds, the packing inequality \((|A_i||B_i||C_i|)^{\omega/3} \leq |H|\) can never be satisfied with parameters tight enough to yield \(\omega = 2\) [cite: 14]. Thus, Abelian groups of bounded exponent were decisively ruled out [cite: 3, 17].

### Nilpotent and Symmetric Groups
Following the failure of bounded-exponent Abelian groups, researchers pivoted to non-Abelian groups. However, similar barriers quickly emerged. 

In 2017, it was shown that a large class of non-Abelian groups—specifically, nilpotent groups of bounded exponent satisfying a mild additional condition—cannot prove \(\omega = 2\) [cite: 8]. The proof technique generalized the polynomial method used in the Cap Set conjecture by examining the shrinkage rate of powers of the **augmentation ideal** in group algebras. This shrinkage rate was shown to be similar to the shrinkage rate of the number of polynomial functions over \((\mathbb{Z}/p\mathbb{Z})^n\), heavily constricting the group's capacity to host large STPP triples [cite: 8, 16].

Furthermore, the symmetric groups \(S_n\) were analyzed. A natural strategy for constructing TPP embeddings in symmetric groups involves using three Young subgroups—subgroups of the form \(S_{k_1} \times S_{k_2} \times \dots \times S_{k_\ell}\). However, it was proven that embeddings via three Young subgroups cannot yield any nontrivial bounds on \(\omega\) [cite: 8].

### Finite Groups of Lie Type and Matrix Groups
The next logical candidate family was the matrix groups, specifically finite groups of Lie type (e.g., \(GL_n(\mathbb{F}_q)\), \(SL_n(\mathbb{F}_q)\)), whose usefulness within the Cohn-Umans framework was relatively unexplored until recently [cite: 18, 22, 23].

In 2023, Blasiak, Cohn, Grochow, Pratt, and Umans published a critical result in ITCS demonstrating that finite groups of Lie type cannot prove \(\omega = 2\) [cite: 1, 4]. Their proof relied on a sophisticated representation-theoretic argument identifying the **second-smallest dimension of an irreducible representation** of a group as the key parameter dictating its viability [cite: 19, 23]. 

Building on Timothy Gowers' results concerning product-free sets in quasirandom groups, they showed that the dimensions of the subsets \(X, Y, Z\) satisfying the TPP cannot be large enough compared to the group size to satisfy the optimal packing bound [cite: 4, 18]. Moreover, they established another barrier that rules out natural matrix group constructions relying on subgroups that are far from being self-normalizing [cite: 19, 23].

These highly specific bounds cover most non-Abelian finite simple groups, although technically they do not completely rule out artificially massive constructions like direct products of non-Abelian finite simple groups (though Sawin demonstrated in 2017 that using a family of constructions solely in tensor powers \(G^k\) cannot yield \(\omega = 2\)) [cite: 21].

## Transition to Infinite Lie Groups

Faced with a landscape of finite groups seemingly littered with mathematical roadblocks, the Cohn-Umans program executed a significant paradigm shift. The barrier results left open a few natural paths for matrix groups, leading researchers to explore the continuous setting of **infinite Lie groups** [cite: 19, 23]. 

### A New Framework for Continuous Groups
In their 2024 and 2025 works, Blasiak, Cohn, Grochow, Pratt, and Umans fully developed a framework for obtaining bona fide finite matrix multiplication algorithms directly from continuous Lie group constructions [cite: 2, 18, 24]. While Cohn and Umans had originally observed in 2012 that a TPP triple exists in the infinite group \(GL_n(\mathbb{R})\), there was previously no method to extract a finite algorithmic complexity upper bound from it [cite: 2].

A construction in a continuous space allows researchers to evade the two specific barriers associated with finite groups of Lie type and quasirandomness [cite: 19, 23]. The continuous setting utilizes the geometric and topological properties of the Lie algebra associated with the Lie subgroups [cite: 1, 18].

### The Role of Separating Polynomials
Translating a TPP construction from an infinite Lie group into a finite matrix multiplication algorithm requires a fundamentally new design component: **separating functions** [cite: 2]. When the underlying ambient group is \(G = GL_n\), these separating functions take the form of invariant polynomials [cite: 2].

The problem of bounding \(\omega\) is theoretically reduced to finding optimal-degree separating polynomials in a ring of invariant polynomials determined by two out of the three Lie subgroups that satisfy the TPP [cite: 1, 18]. This machinery critically combines the notion of **border rank** with the structural properties of Lie algebras [cite: 1, 25]. 

**Theorem (Informal)**: A construction within a Lie group utilizing "half-dimensional" subgroups (subgroups whose dimension is asymptotically half the dimension of the ambient group) equipped with a separating polynomial of optimal degree directly implies \(\omega = 2\) [cite: 1, 2, 18].

### Constructions in \(GL_n\) and Unitary Groups
As a running example, in the general linear group \(G = GL_n(\mathbb{R})\), researchers identified a triple satisfying the TPP:
1.  \(X\): The subgroup of lower unitriangular matrices.
2.  \(Y = O_n(\mathbb{R})\): The subgroup of orthogonal matrices.
3.  \(Z\): The subgroup of upper unitriangular matrices.
[cite: 2]

The dimension of the ambient group \(G\) is \(n^2\). The dimension of each of the three subgroups \(X, Y,\) and \(Z\) is \(n^2/2 - n/2\) [cite: 2]. As \(n \to \infty\), the dimension of each subgroup approaches half the ambient dimension, perfectly meeting the geometric packing bound necessary for optimal complexity [cite: 2, 11].

Recent papers culminated in a construction within a **special unitary group** that successfully achieved separating polynomials of the optimal degree [cite: 1, 18]. However, in this specific instance, the subgroups approached half the ambient dimension just slightly too slowly (\(\dim G / 2 - \Theta(n)\) instead of the required \(\dim G / 2 - o(n)\)) [cite: 1]. The classical features of these specific Lie groups make it unlikely that they can produce intermediate bounds on \(\omega\) unless they outright prove \(\omega = 2\) [cite: 1, 18]. 

The current identified pathway to \(\omega = 2\) via this continuous framework involves lifting the existing successful separating polynomial construction from the special unitary group back to \(GL_n\), and finding a way to improve the subgroup dimensions to the requisite \(\dim G / 2 - o(n)\) [cite: 1].

## Conclusion

The pursuit of the true algebraic complexity of matrix multiplication has driven some of the most profound theoretical innovations in computer science and modern mathematics. The Cohn-Umans group-theoretic framework radically transformed the methodology for designing matrix multiplication algorithms, elevating the problem from ad-hoc recursive tensor identities (the laser method) into the rich, structured domain of group algebras and representation theory [cite: 5, 6, 7].

The formulation of the Triple Product Property (TPP) and its simultaneous generalization (STPP) offered a clear, combinatorial checklist for proving \(\omega = 2\) [cite: 3, 13]. However, over the past twenty years, an escalating series of barrier results—originating from the Cap Set breakthrough and extending into deep bounds on tensor irreversibility and quasirandom group representations—has systematically proven that almost all standard finite groups (Abelian, nilpotent, symmetric, and finite groups of Lie type) lack the mathematical capacity to reach \(\omega = 2\) [cite: 1, 4, 8, 14]. 

Despite these setbacks, the negative results have acted as vital directives. The rigorous ruling out of finite groups has shepherded researchers toward infinite Lie groups [cite: 19, 26]. By bridging border rank, Lie algebras, and invariant separating polynomials, the latest iterations of the Cohn-Umans framework have generated continuous constructions that evade previous barriers and sit tantalizingly close to optimal mathematical parameters [cite: 18, 25]. Whether an optimal separating polynomial in \(GL_n\) with half-dimensional subgroups can finally be realized remains an active, fiercely pursued open question—one that holds the potential to permanently settle the complexity of matrix multiplication at \(\omega = 2\) [cite: 1, 19, 23].

**Sources:**
1. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGoy_bYbFzJVHG-fuyiOh4cZcOTqLqfEQ8lg4DBGZSIAUv683eMtbEU_aXSv_rY2yUfCzTOCykI_9NjHV8EuH7CnSPBEyHkO1UVAzZgzyKA3-o4z6NXLM6o5w3PuFD-xxUtihkJNuMDofBli2UasoeYclAhadaOCGfg_927GBWhww==)
2. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEq6pUjE0i-QAm7vb-0-eK7u_R_gN21iCD1FkbXVfEr6cBcwrAIYOrGLBH88UUfLrku2s_TWRNBONp0sSJpMDAU9N787EagnMGUxHva-gjTYlx-AYPEYQrIuUnQ6InGyz469ahajnnzHYfei13cy3qZVg1zEI8a_Oz8-d-n7JLkkKYbH4sukHrUQOpyKfehmOr_W8wE1V0ZT2RspckbdCYD8nk=)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHulY8Ap5nvEAD5d1trxCb_nlP1x3rOnpq8RpfwEvUmfBtZ13h5_xK9WYylQgpmn4NCGhCJ-v2xjFzqqvS8adCrCsz34RnGwRM8G2OEJRkaSY9_WKLYQyY0fuTUNXKN2dC-RH3ZwIs8_LxOj6zgS_zmZm7UZckaumji00hm7u1XF50ksl0w_6kBcODYUDwW84d8_ZvMjEUkemomEn3avA==)
4. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGM1Up_5F7uiHx9LFbNRR45T1VizW288Jgi6uFrE-FmMh4xK9tobWkEeoVi9e3BTeACoVCkZAYwV2xd3j2uLIRcyZ9mBYxhVqbHEcx1clHUyy-7-_0WI8-hrLxEIIeOOsDdQognCaOxk5ROKaKtYDjVHjG07eGXYL6v1uNNkYldLEf49lu2uof-aLeyhHds1yjQSLeSxT4EnvpBKydfcYx7nQY=)
5. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9i4M-qevoEP6F06N8lwAWcb4rkOqvntlYdstMLYyR-0_66Bl7xp0e69iKvUJjmRb67mNU2DTpLaShusvqwbxbNfeIuLQlIWXYGALVjNM7eN2z2Q3Ge7tO3f_JFOdMz_PovEtV420OSf8AzrLvJ7J8xvop72kfJO1_3CPsn2XIhksLDH4=)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6bhcxO0Q0SN9oq2UD3pOShNw_kHn51m9to03Cs2mJ4maY_tV1SShTRmQBlmo6bn-qSe9y04xtSns5DHFF3q08I09bbkIn8Y8FeFvQTEsiavDIGIuU6C-xNehFTd2FiEJCL_Xcp0laj8bpbGkQ4SZk61BHwJ60g-zpEb596kKMIRN8FHMOdnDNK_eILkgVK2Y0mF9etisxhnrNUIPc5g==)
7. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEO54uMzI3wL4QfuxEWAptoKQ949voXAkXZ3LPBY1p0irReCSPGgEcZyAuY9YQoO4fVBo1NusOi3Vn9S9nc9Q6mHt2TC4czSuhvjyE5TzUgqcux4negzRhoBMHmv16gDkCgXQ4kEEvjNcxVsPLr23jGiKuS1AYK6GLtkpewofo3hvP5ukJRdJbQJOjVn2-Dbbg=)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEm_k2IxOKngYy6mX0TdZQTq7mkk4Q_EkO98HWf27dBFzxjukoAPRxD6LqjkxMv_l_5yzpPUaLwu2uCjyO_xnPe3U4OYPnNcUoGCROOy_4xGz3DJU_v)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTp-xo4Yktt4NOD_hHks7Nb79kYNKQ2-BRcBH41SPgwRJr-W0cTJggPq9ozkLk1O7JxPAtVJ6nqPhZgM2eYblpMBbBzmDifSvDsjIHFNcLws0jNzWnDeC5UbHh2sDwoGTVv7UlV75Oxw==)
10. [ntua.gr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFL9QXDk6QRY8ufucPEvdE8CPRfnj5553PF1IjOlPEogOw_YSPXs7MD3XSFkKbyS4wG_np-1apbeqixofPKuAhmfjnazjA5LR1DX24PmQBOPwBlkOfuK-oNAxPxAiHevGuEgUhvfXAr0vuQdeaNCPp8)
11. [ucsd.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1_N_w1sWm9wWR61JwK4Pl7H8PbynxeBpuEAfBIm04EHV_8kvAU80IwOcnEXVf5VxdVCV5d1VzzDLF8q8Nd9XkPOKBYLkmFGjFH3qs_YJnjaNPkcZRhv6QWBRDfaL32sr5Ubyr7pYbn4vs89JoZfZuOO6wi07M_Ht902K3Ozved13B93De)
12. [tau.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmMzVW9U21-vWDUSSAUbIVzAA5Gd7MkKArMHZY7grYS0ETP9flgiHlcjpVQASTYyNVPmegx7aXbOyVFCHl21nDKjrxoR9heiHAgfRS9X1y8HPmr-J566C1v9iWedffFt7xjuEevwPn)
13. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFA-vziJrRfs5dnA_nBW1bdSuA04saljUDVnsGvII2HceoGICeFsuL7bepFfJ3VJ-f70iNDcLcghNAPVX2vRiY-lb5CDyGXi42vUYfpTnUfZf_cZr7WmQbbLNYMxM8_IEc=)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGoXh5CamoVoUBnzin-_POIysumkef8KL-o46mopZOA3ypth-ocELbIL4QDW1zN0jroigG0fhcfHRG9MQoLP-IRApxTazw27gnUbmdMaTXpWROLVrlnhRS4IHIxZVrQ8R3d-DQQtKXrug8h2Wlw8w5ad3piyP_MInazpMCqjjhhlsbQ23iwVzNP0kn19tglZj6sTo2S_kPi9hEoZx194irtjM2w4PnwAvtKMcVBVw==)
15. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEK9Y9Rvz1F-RZAZhacYV2B4TIZ_VzixnoEkg5yAs5wRiD1WbzXTHXzuAN_n0mGL66SXl-Pi5jTqLpwjh9nEneADVKU-9qAUv4_OyZmIVWW-3UB_Il2hIFhQylWC9FdEYZQ2eBB4pS4Uy_rqivHE8qr0-ZUPKeq0kzsze6T)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPDH280HM_RSYvrAWtXLV--84J3nfKCzHYz_BiroaoFQztL4Rd6LwTXVrhE06NjP3-1n8eyS6Px_5SW5pOOYCBAWbMPjsyz9EStjjhka9z1V5L2qjmAkbaFXK3vBXx6E62FIC96UiBbPGYDfkun_M4-G0du3Cvgo53YbGw9EJNMKTVzmO1EqqhyH4foGaZgJNhydRGvjxBI3hzOEwTGZK8ubPq9iirn_HqNvyzP6KCGahddA==)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_5l2TGLDGKeDwIAlPVmBQhwk9CN9w61a73gHyfeuFjHc16IKhY4nRY5Kxzs3PsL894Iws3VssJsAjtXhbfBcOm_gyIlLTmzz2jaRGJLUIIhZ9QLpXk-yLOE8-bw6q-ohShpV2WAZHUnkF3MbSHsAM6U3rsbs9mpbAaat548VI5qvtUin5LlpKgMLCqT0MFw==)
18. [colorado.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQED48aKMpTZMuynfv4z1rRSLuON6NZY_835-eCfTY-Ivj3xznoj0RFGowqawfhzF66VHSFNqF-yOIc7jfnrxUZOLH7U_OZVxbwpYggddhC_lqgE5wNB7ssApuaDE0U9vQmkxL5JiQ==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJ1W6th-HZZR7vcY0v0S8nKsz1avRsV1YWqQfxVdJMK2wr4PQ-L-ztU_IJ0B2xXVEmz-k7IY4nrk7wNb4ciQH4bCjOH0TFUgZEnAWafOPV2MYH3kDm)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVzBqOjtuiV4GBLXFxQRWpgrzBOEkLF9ntMhzcDZsdliMsBcUzl4TyQlqeqHzaHuFlcajmq4puTOAfQJVUSi6kzkGB8BmoIslhQVDSIe4Y58mb5Tqu)
21. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJkY04FVwR2aqhXMNrQ88qYTulEjsCBotCTquIXk4zMDor4GtDctuBTV6c4Vx3oT-jQoa9T1WLPXsAPYVl8foSTFOmezCxUYyhN4CWuK_Cg27hsNsh88_PzSmilwxUYIjp9gJJHuX2UQKJmxPptsVpNRf8-r2226Vxbw-98arAB72o3ltArBd9Q7nnnLP3KoFgeeodup1q4a6QU0LhzTknog==)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuXxR8mCgxsQvbmXoYHfjXxdJ-ukj01-haznhAODHi3NKZTmdKcPUhQFb7dxAJtZ-Ww-lK7CIzZxexuXf1knvb3DipFLU9ppgzW_eVvA4GjXr2mM4gfQVlZlflG903TCsUWPX93wB6edML3aRStwww897CxmTYlPXelAV1SADfJ1maa897TmrbMhg7GmKzKLIgoBO8UraSlrQO)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZBMPDx-lcZTDPtGbHoww6BvHsg0BGe-WaYGomtEtDJAlCeYtNdDdzkXkPLmRargdqDeoQndMs3RU6W-HIoOHfrGk1J2qiPDEEby-A7_-ZGgWC61CN82wcyfjeqD5KtZgcog5ULbSYfH_s6i9buMkdxIZOD2xT7R8O49DEN73y)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpo-elzwvMDGDNL-YmjK-SGHZSlfsya7P3n1TxesXOrkloOHz6mSyNr_K5wbQ9l23n7JTKX-I5KkeJwE3i3cXTTXhb5Te6GSj1Rd0brHVHCgQw258d)
25. [cnrs.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFoqDPegQ3hkEhrNM6Rb3BYyOZc8wOFrNLVhSLfICHV68HanrSAAj4BYfa4yID5N7hX3jOJHbtrZEalr9bStVAHHX4WZHgKZzl4UsHSpRQ9ZnM4gOiRcKnF79cv0Skr-LxtJyxBmGR8bo8kSJI59dA=)
26. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLIE1pJek1rFewX8W6JqcAXzgUuGVyZRw2JeTIuRTPy_eAN5TVrbFW9pLkdMOb51TDvHICM2e1tJf77epcYAP7CYPQlS6iDKNKAVloeBEobbZ0--82_W39nsvODn70jgBzfkHXkZV2ag==)

