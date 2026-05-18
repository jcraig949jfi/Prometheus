# T#10 Bini-style degeneration sequence length / epsilon-expansion control

**Pythia queue id:** 11
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdqM2NMYXJUU041cXExTWtQXzhPRnFBWRIXajNjTGFyVFNONXFxMU1rUF84T0ZxQVk
**Elapsed:** 1055s
**Completed at:** 2026-05-18T20:50:55.506681+00:00

---

# T#10 Bini-Style Degeneration, Sequence Length, and Epsilon-Expansion Control in Tensor Complexity

### Leading Paragraph

The mathematical framework surrounding **Bini-style degeneration**, **sequence length**, and **epsilon-expansion control** represents a profound intersection of algebraic complexity theory, numerical linear algebra, and theoretical physics. At its core, Bini-style degeneration leverages approximate bilinear algorithms—controlled through a perturbation parameter $\epsilon$ (or $\lambda$)—to reduce the number of scalar multiplications required for matrix operations. A landmark achievement in this domain is the demonstration that matrix multiplication tensors can achieve a **border rank** lower than their exact rank, famously exemplified by Bini's algorithm of sequence length 10 (often denoted as $T=10$ or $r=10$) for $2 \times 3$ by $3 \times 3$ related matrix structures. The control of this $\epsilon$-expansion is critical; by managing the polynomial degree $d$ of the error terms, one can systematically convert an approximate algorithm into an exact one. Furthermore, the terminology of sequence length and epsilon-expansion transcends computer science, finding direct analogies in theoretical physics. In the Renormalization Group (RG) and Stochastic Series Expansion (SSE) methodologies, the $\epsilon$-expansion (such as $d = 4 - \epsilon$) and the truncation of operator sequence lengths govern the analysis of critical phenomena and phase transitions. 

This comprehensive report explores these paradigms in detail. First, we establish the foundations of bilinear complexity, tensor border rank, and Bini's original length-10 sequence. We then detail the mechanics of epsilon-expansion control in isolating exact outputs from approximate degenerations. Finally, we examine the broader applications of these techniques in numerical approximations (such as Toeplitz matrix inversion) and in the physics of linked-cluster and stochastic series expansions.

***

## 1. Introduction to Algebraic Complexity and Tensor Degeneration

The computational complexity of basic linear algebra operations, most notably matrix multiplication, is a foundational problem in theoretical computer science. The exponent of matrix multiplication, denoted as $\omega$, is defined as the infimum over all $\tau$ such that two $n \times n$ matrices can be multiplied using $O(n^\tau)$ arithmetic operations [cite: 1, 2]. 

### 1.1 The Bilinear Algorithm Framework
Matrix multiplication is intrinsically a bilinear problem. Let $A$ and $B$ be matrices of dimensions $m \times n$ and $n \times p$, respectively. The product $C = AB$ consists of $mp$ bilinear forms calculated over the variables $a_{ij}$ and $b_{jk}$ [cite: 3]. An exact **bilinear algorithm** calculates these forms using a two-stage process:
1. It computes a sequence of products $P_t = u_t(A) \cdot v_t(B)$ for $t = 1, \dots, r$, where $u_t$ and $v_t$ are linear forms in the variables of $A$ and $B$.
2. It constructs the elements of $C$ as linear combinations of these $P_t$ products [cite: 3, 4].

The number of essential multiplications, $r$, is known as the **sequence length** or the **bilinear complexity** of the algorithm [cite: 3, 4]. In the language of multilinear algebra, this is equivalent to the **tensor rank** $R(T)$ of the matrix multiplication tensor $T = \langle m, n, p \rangle \in \mathbb{C}^{mn} \otimes \mathbb{C}^{np} \otimes \mathbb{C}^{mp}$.

### 1.2 The Advent of Approximate Bilinear Algorithms
While Strassen's algorithm achieved a sequence length of 7 for $\langle 2, 2, 2 \rangle$ matrix multiplication, bounding $\omega < 2.81$ [cite: 3, 5], progress stalled until the introduction of **approximate bilinear algorithms** by Bini, Capovani, Lotti, and Romani in 1979 [cite: 3, 6, 7]. 

An approximate bilinear algorithm introduces a formal indeterminate, $\epsilon$ (or $\lambda$, or $x$), allowing the coefficients of the algorithm to belong to the ring of Laurent polynomials over the field $\mathbb{F}$. The algorithm computes the bilinear forms with an arbitrary precision dependent on $\epsilon$, such that the result is $C + O(\epsilon)$ [cite: 3, 4]. The minimum sequence length of such an algorithm is called the **approximate bilinear complexity**, or the **border rank** $\underline{R}(T)$ [cite: 3, 8].

A sequence of tensors $T(\epsilon)$ of exact rank $r$ degenerates to a tensor $T_0$ if $\lim_{\epsilon \to 0} T(\epsilon) = T_0$ [cite: 9]. Because the set of tensors of rank at most $r$ is not generally Zariski-closed, a tensor can have a border rank strictly less than its exact rank ($\underline{R}(T) < R(T)$) [cite: 10, 11].

## 2. The T=10 Bini-Style Degeneration Sequence

The nomenclature surrounding $T=10$ or "length 10" in Bini's algorithms refers to the seminal approximate algorithm that computes a partial matrix multiplication using exactly 10 multiplications [cite: 8, 12]. 

### 2.1 Bini's $\langle 2, 3, 3 \rangle$ Border Rank 10 Construction
Bini et al. demonstrated that it is possible to compute the product of a $2 \times 3$ matrix and a $3 \times 3$ matrix (which exact rank studies suggest requires more operations) using an approximate sequence length of $r=10$ [cite: 8]. 

To apply this to square matrix multiplication, the matrices are subjected to block decomposition. A $12 \times 12$ matrix can be viewed structurally as a $2 \times 3$ matrix whose entries are $3 \times 2$ matrices, which in turn have entries that are $2 \times 2$ matrices [cite: 8]. By utilizing Bini's algorithm iteratively, the overall multiplication can be executed. Specifically, the multiplication of these block structures requires the invocation of the base algorithm three times, yielding a total sequence length of $10 \times 10 \times 10 = 1000$ multiplications [cite: 8]. 

Consequently, the upper bound on the matrix multiplication exponent becomes:
\[ \omega \le \log_{12}(1000) \approx 2.7799 \]
This marked a historic breakthrough, proving that approximate sequence lengths (border ranks) dictate the asymptotic complexity of exact matrix multiplication [cite: 3, 8].

### 2.2 Higher-Order Explicit Bilinear Sequences
In computational studies extending Bini's methodology, algorithmic sequences are explicitly written out to high lengths. For example, in the derivation of approximate bilinear algorithms of length 24, 37, and 46 for $4 \times 4$ and $5 \times 5$ matrices, the algorithm is defined by a sequence of computational steps $t = 1, \dots, r$ [cite: 4, 6]. 

The sequence step $T=10$ (or $t=10$) in these computational tables specifies a precise set of Laurent polynomial coefficients. For instance, in Smirnov's length-46 approximate algorithm for $4 \times 4$ matrices, the $t=10$ stage defines a specific matrix of weights in $\mathcal{O}(\epsilon)$ and bounded scalars (e.g., coefficients evaluated in the range $[-10, 10]$) [cite: 4, 6]. The generation and optimization of these long algorithmic sequences rely heavily on non-linear optimization techniques mapping variables to polynomial values over $\mathbb{F}[\epsilon]$ [cite: 1].

## 3. Epsilon-Expansion Control in Algebraic Complexity

A fundamental question arises: how does an algorithm that computes $C + O(\epsilon)$ lead to an *exact* computation of matrix multiplication? The answer lies in **epsilon-expansion control**, a mechanism formalized by Bini and later generalized by Schönhage [cite: 3, 8].

### 3.1 Bini's Exactness Theorem
Bini established the rigorous relationship between approximate (APA) and exact (EC) algorithms. Suppose an approximate algorithm achieves a sequence length of $r$ and is characterized by a degree $d$ of $\epsilon$-expansion [cite: 4]. The degree $d$ corresponds to the highest negative power of $\epsilon$ used in the Laurent polynomial coefficients (i.e., the algorithm requires dividing by $\epsilon^d$).

Bini's Theorem states that the existence of an approximate algorithm of length $r$ and degree $d$ implies the existence of an exact algorithm of length $(1+d)r$ [cite: 4].
By evaluating the epsilon-expansion at $1+d$ distinct points and applying polynomial interpolation (such as evaluating derivatives or taking linear combinations of the $\epsilon$-shifted instances), the error terms $O(\epsilon)$ can be systematically eliminated [cite: 4]. The sequence length of the new exact algorithm is bounded by $r$ multiplied by the number of interpolation points required to control the expansion up to degree $d$.

### 3.2 Strassen's Laser Method and Kronecker Powers
The control of $\epsilon$-expansions was vastly expanded by Schönhage and Strassen. Schönhage introduced the $\tau$-theorem (Asymptotic Sum Inequality), which demonstrated that approximate algorithms applied to disjoint sums of tensors could be controlled globally [cite: 8]. 

Strassen developed the **Laser Method**, which relies on the submultiplicativity of border rank under Kronecker powers [cite: 9]. Given an auxiliary tensor $T$ with a small border rank, one can compute its $N$-th Kronecker power, $T^{\otimes N}$ [cite: 1, 9]. 
1. The border rank of the sequence scales as $\underline{R}(T^{\otimes N}) \le \underline{R}(T)^N$ [cite: 1].
2. Through sophisticated zeroing of basis vectors (a process of projection and degeneration control), the large tensor $T^{\otimes N}$ degenerates into a massive matrix multiplication tensor $\langle M, M, M \rangle$ [cite: 9, 13].
3. The epsilon-expansion is "lasered" to kill off cross-terms, leaving only the desired matrix blocks.

This controlled suppression of $\epsilon$-expansion artifacts allows one to map the asymptotic complexity directly to $\omega$ without paying the $(1+d)$ penalty at every recursive level, as the $(1+d)$ factor is absorbed into the asymptotic limit as $N \to \infty$ [cite: 1, 8].

## 4. Epsilon-Expansion and Sequence Length in Physics

The terminology of "sequence length" and "epsilon-expansion control" is not unique to algebraic complexity; it is also a cornerstone of theoretical physics, specifically in quantum field theory, statistical mechanics, and many-body systems. The underlying mathematical philosophy—using a continuous parameter to approximate a discrete or intractable problem—is remarkably similar.

### 4.1 The Wilson-Fisher $\epsilon$-Expansion
In the study of phase transitions and critical phenomena, exact solutions are typically unavailable in three dimensions. The **Renormalization Group (RG)** theory, pioneered by Kenneth Wilson and Michael Fisher, introduced the $\epsilon$-expansion [cite: 14, 15, 16]. 

Here, the dimension of space is treated as a continuous variable $d = 4 - \epsilon$ [cite: 16, 17]. At exactly 4 dimensions, the scalar field theory (e.g., the $\phi^4$ theory or $O(N)$ model) exhibits a Gaussian (trivial) fixed point. By expanding the beta functions in powers of $\epsilon$, physicists can locate the interacting Wilson-Fisher fixed point at order $\mathcal{O}(\epsilon)$ [cite: 18]. 
The expansion takes the form:
\[ \beta(\lambda) = -\epsilon \lambda + c \lambda^2 + \dots \]
Control of this $\epsilon$-expansion is vital. Because the series is typically asymptotic (often divergent), techniques like Borel resummation are required [cite: 17, 19]. The "control" involves identifying stable fixed points and truncating the expansion to extract physically meaningful critical exponents (such as $\nu, \eta, \gamma$) [cite: 15, 18, 20].

### 4.2 Sequence Lengths in Quantum Expansions
In quantum physics, **sequence length** plays a crucial role when simulating Hamiltonians using numerical techniques such as the **Stochastic Series Expansion (SSE)** or linked-cluster expansions [cite: 15, 21, 22]. 

When analyzing a quantum phase transition using SSE, the partition function $Z = \text{Tr}(e^{-\beta H})$ is Taylor-expanded into a power series of the Hamiltonian $H$. This results in an infinite sequence of operator strings. To make the computation feasible in quantum Monte Carlo simulations, a strict **sequence length** $L$ is introduced [cite: 15, 21]. 
1. Sequences with an operator count $n < L$ are padded with identity operators to reach length $L$ [cite: 15, 21].
2. Sequences where $n > L$ are mathematically discarded [cite: 15, 21].
This truncation is physically justified because the probability weight of sequences exceeding $L$ is exponentially suppressed when $L$ is chosen to be sufficiently larger than the mean energy $\langle H \rangle$ [cite: 15, 21]. 

Just as Bini's sequence length bounds the number of tensor operations, the SSE sequence length bounds the complexity of the quantum Monte Carlo update step. Both frameworks manage a dimensional expansion (either the loop expansion/$\epsilon$-expansion in RG or the Taylor expansion in SSE) by controlling the cut-off length to balance computational feasibility with exactitude.

Furthermore, in double scaling limits—where both the loop expansion parameter $\lambda^*$ approaches 0 and the operator charge (sequence length) $n$ approaches infinity—the physics is controlled by a classical parameter $\lambda^* n$ [cite: 23]. This behavior mirrors algebraic complexity, where the asymptotic rank of matrix multiplication is analyzed as the dimension $n \to \infty$ while carefully managing the $\epsilon$ limits [cite: 9, 23].

## 5. Sequence Length Degeneration in Tensor Networks

The synthesis of tensor algebraic complexity and theoretical physics crystallizes in the study of **Tensor Network States (TNS)** and **Matrix Product States (MPS)**, heavily utilized in both quantum chemistry and machine learning architectures (such as Transformers) [cite: 24, 25, 26].

### 5.1 Cycle-Free Tensor Networks and Sequence Lengths
In quantum many-body physics, the wave function of a system is represented as a high-order tensor. To avoid the exponential explosion of parameters, the tensor is degenerated into a network of lower-rank components. If the tensor network satisfies the criterion of being cycle-free (e.g., a Tree Tensor Network State), it bypasses complex border rank complications that arise in loopy graphs [cite: 24].

The complexity of these networks is governed by the **bond dimension** (analogous to the sequence length $r$ in bilinear algorithms). Algorithms like DMRG iteratively optimize this sequence length to approximate the exact ground state tensor, much like Bini's algorithm approximates the exact matrix multiplication tensor [cite: 24, 25]. Notably, the linear span of uniform matrix product states (a translation-invariant tensor network) is strictly contained in its ambient space as long as the physical sequence length (number of sites) scales quadratically with the bond dimension [cite: 25].

### 5.2 Sequence Length Challenges in Language Models
In modern computational linguistics, Transformers face significant hurdles regarding **sequence length** complexity [cite: 26, 27]. The attention mechanism requires a sequence length complexity of $O(N^2)$. Techniques to manage this involve approximating the full attention matrix via low-rank degenerations. 

Furthermore, models trained on self-generated data experience a phenomenon termed "model collapse" or "degeneration" [cite: 26]. This generative degeneration occurs as sequence lengths grow and recurrent errors compound. Control mechanisms, including deduping algorithms and prompt-tuning, seek to enforce "non-degeneration conditions," ensuring the output probability tensors maintain full rank and do not collapse into minimal border-rank localized states [cite: 26].

## 6. Numerical Precision and Bini's Toeplitz Inversion

Beyond abstract algebraic bounds, Bini's epsilon-expansion algorithms have direct, practical applications in numerical linear algebra, specifically concerning **Toeplitz matrices** [cite: 28, 29, 30].

### 6.1 The Challenge of Ill-Conditioned Sequences
In linear evolution problems (like discretizing the heat or wave equation over time), the computation often yields a semidiscrete lower triangular Toeplitz matrix sequence [cite: 29, 30]. Explicit exact inversion of these matrices requires $O(N^2)$ operations.

Bini (1984) proposed a fast $O(N \log N)$ algorithm for the approximate inversion of these special Toeplitz matrices [cite: 29, 30]. The algorithm uses purely algebraic transformations, specifically the discrete Fourier transform, to map the Toeplitz matrix to a circulant matrix [cite: 29, 30].

### 6.2 Managing the Epsilon Error in Double Precision
This structural degeneration is fundamentally an approximate algorithm. Because it relies on $\epsilon$-style perturbations (e.g., shifting polynomial roots), the original Bini algorithm suffers from precision loss, restricted to an accuracy of $\sqrt{\text{eps}}$, where "eps" is the machine precision [cite: 29, 30]. In standard double-precision arithmetic, $\text{eps} \approx 10^{-16}$, meaning Bini's uncorrected algorithm only yields an accuracy of $10^{-8}$ [cite: 29].

To control this numerical $\epsilon$-expansion, advanced algorithmic corrections are applied. By introducing a specific correction term, the maximum accuracy can be dramatically improved to $\text{eps}^{2/3}$ (or roughly $10^{-10}$ to $10^{-11}$) [cite: 29, 30]. This allows the decoupling of parallel time steps in evolution problems with high fidelity, proving that theoretical border-rank constructions can be carefully adapted into floating-point numerical libraries provided the $\epsilon$-expansion is properly regularized [cite: 30].

Similarly, in solving Toeplitz least-squares problems via hierarchically semiseparable (HSS) matrix approximations, algorithms encounter highly ill-conditioned prolate matrices with condition numbers scaling to $O(10^{12})$ [cite: 28]. Applying stable structured direct solvers (transforming Toeplitz to Cauchy-like matrices via displacement equations) allows the computation of operations in nearly linear complexity, maintaining robustness even against Bini-style condition degeneration [cite: 28].

## 7. Mathematical Classifications of Border Rank Tensors

To round out the discussion of tensor degenerations, we must examine the formal classifications of tensors that exhibit minimal border rank, which are the building blocks of Bini-style algorithms.

### 7.1 Concise Tensors and 1-Degenerate Minimality
A tensor $T \in A \otimes B \otimes C$ is deemed **concise** if its induced contraction maps (e.g., $T_A: A^* \to B \otimes C$) are injective [cite: 1, 10, 31]. If a concise tensor satisfies $\underline{R}(T) = \max(\dim A, \dim B, \dim C)$, it is classified as a tensor of **minimal border rank** [cite: 10, 31].

These minimal border rank tensors are highly prized because they serve as the optimal structural tensors for smoothable algebras [cite: 31, 32]. In small dimensions, they can be entirely classified up to isomorphism. For example, for a sequence length $m=5$, all 1-degenerate concise minimal border rank tensors are "wild" (having continuous moduli), and they collapse into exactly five distinct isomorphism classes [cite: 31, 33]. 

### 7.2 Koszul Flattenings and Lower Bounds
When proving that a sequence length (border rank) cannot be lower than a specific value, researchers employ algebraic geometry. An adversary attempting to lower the border rank of a degenerated tensor is thwarted by polynomial invariants [cite: 13]. 

**Koszul flattenings** are a class of linear maps constructed from the tensor whose ranks provide robust lower bounds on the border rank [cite: 10, 13]. If a tensor is "tight," the border substitution method is applied, analyzing finite filtrations to evaluate explicit non-zero polynomials [cite: 13]. These techniques recently broke long-standing barriers, proving explicit sequence tensors to have border ranks strictly greater than $2n$ [cite: 13].

## 8. Conclusion

The conceptual thread linking **T#10 Bini-style degeneration**, **sequence lengths**, and **epsilon-expansion control** illuminates a profound symmetry in modern applied mathematics and theoretical physics. 

In algebraic complexity, Dario Bini's discovery that a $2 \times 3$ by $3 \times 3$ block matrix could be multiplied with a sequence length of 10 using an $\epsilon$-expansion redefined the limits of computation. It proved that tensors could degenerate across algebraic boundaries, possessing border ranks strictly lower than their exact ranks. By formally controlling the degree $d$ of this epsilon expansion, computer scientists can extract exact, sub-cubic algorithms for matrix multiplication.

Simultaneously, the physics community relies heavily on identically structured logical frameworks. Whether it is tuning the sequence length $L$ in Stochastic Series Expansions to isolate low-energy quantum states, or managing the $d = 4 - \epsilon$ expansion in Wilson-Fisher Renormalization Group theory to bypass non-renormalizable infinities, the tactic is universal: introduce a controlled parameter, accept a temporary degeneration or approximation, and isolate the exact asymptotic truth.

As computational models grow increasingly complex—from the multi-billion parameter attention sequence lengths in machine learning to the deep tensor network states of quantum chemistry—the principles of Bini-style algebraic degeneration and epsilon-expansion control remain indispensable tools for ensuring theoretical stability and computational efficiency.

**Sources:**
1. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRovd2mB4t2THCcgpD5qVlRCLuVoVl8UIF8PdSk6AxgKose1LV3J-AKuhKCGPAQP5wL0HhdDlGcix1r2K5iKInX1ZCMmE19XIlwuZO34Lvz5mOri9tWhUeGK4ZFVo1cHsKdQ==)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9XY3ALM-QAhb6sw6h7jprArUNMJyxFsPMb14bhNbwHMnr7XM5MXUx44ByDJkQDvqFDD407gDhiLVqlwREKD1sZxUJg3ShRiSamWbtUIvs08T2-Qa-QFkabvMswewy3D3Yw6zal7Q2VyMPUIrZwWhQ_npu7p1WbjWnRiOnfhoc6-ULVK74PyhhWE73bAW1QQKfqghqsePil6FX8_7-)
3. [academia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQED635oyKTYG5TvIMNZ0k1dUF9ByCiQZ6I4--Opor60xddJi2mayAIFLKOo9xoqGuiaZbR-gxKx-VL2Hn1Xvo0Z5RaGcqWiJIx4y8dvyt4uc1JPTIatRazHU_uv5BlxmJVl3pxqK1fmWokyh8INM0kV4GhVxkT_c2jia-jc0VHvsMDXdOOWzjji_RgDmCHcIkeYGNM9-zwyJxyurSZDT_vq3pgIYMMF9V-Vm6BP)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpVilx8rcmazO_Gv_iVBDiZkFEFsiMM3eWBoZS7iE9389D7VN6f7bqEGXeFEDO4Hs2vhY-QaNSxfJ-IG4S6ysYMgo21XZ7ZS9kvlstiClGV7sI81m2eo0420EZtWcTC2F4JiZwr2_cqgmcGFaJq7iXqcY3lXs1tLSmqLMqYURGKJVl5usuwXl_G_MxMSwFanFZAjSrlmHUBewnJ0SOemEPaPgE08es1Y6dOllWGHmUzdxCoDNoPULvWI5SMDPJ)
5. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaQMz0J0p5cQDDYmuab57vqAocE8Ir_4vTi7gNmGVg8vcHOPvYjRgAHnhhey2yyQIWVMWcc8EVHSlZYCfdgTEd0BrFN5ZbX9j8hBlnehGWk5CZxxs-VX4s6-8pGljmKZ0Lh2cmQaivfDF24dYEfuLUMkOXH51nhw==)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjF1qKrrTxwkEXqKDYfiShsrLJbjmpc6ywYkF4qy3H5Oy83kDGAEF5sludQur3p0cztFnQvopftnRfqNxyJEdne0utZKJIXfjNbe4iC5v9-AKzr8AD9cl7aZbg0CFGETzkWuaKagAsjClNL_BpNlEP9wVGpl5dD7nivVoPoxZPDTvf_9O2s8x1wNBR4PIWkw6yqT-4nN7Smyy1_PqL9H7XUX-BZMc1RIlqLwfjCvHYuPkSK0dHZxz8sLQpcsY=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVep5_85W8TGLNz3btj26gc8n37AjAhRpHXnlSZKx9E-PwEdWbtM0f6H43_VOXLxuZlMZYYAu0qIcWLe2ZdhKDIBt3nYMMxiwGkwpY-_A5VKrri9g3)
8. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFByfLS6cD4Q2e0rBtnoQx_CRG0sef84i6Odj_be7OsUy75459Qsw_ojd240V22SkNvaiICGw2fk7SlgPKEpbmF9QIWb9egDryfHuNxQkarKDlHDS6pfUnBF9gUTC507vcErXeP3Q3gAw==)
9. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRfQFwEPeWnOqS-5FH9kO-EwadK-4qwIWP3LWbeXiSNab4m-_0dAViBsLLGpq1hlCWWBCMUB1CDE5Jm32MXr96LNWFVr67A3XpjNl8PTBor2Z-49f_IdpQgTQ6VjZTfsNDn70Ltg==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEks5G4IoQnzismYtTBlYr0lmgvhU6NN-8ZvnvUDPXbVSQppr2jgV6ZmlX6HRIrVe3mdp9TZq1jYZWRA0HyNaLp77jFAaNVs38vcqzqymWuVSYWhoIZ)
11. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuR3fsDIC5PqnBWZOewZ0LOLIBKwgMDhondU4thez6pbCLLYiKKyecR-bI7pSXytEw5r0HGgHxLDS_jbkzRn_z5JRpLmnYwUUuMWW5Q0yJ5x3Kg1af983VI5KPlpVCY9aR7g==)
12. [uoregon.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaRtvb_mDgul7P5WZKVsYK4ApH6WHQ5wMC3jGno5bf08Wrbj2udBrNL26UvP9DEhga7VWRxR40kaSJMLmXzd8GjhjL2yjhvnJZwS39ftIfsW8xCg_3A5K_fB69ZBI0g08WtvadMnW5bHojrA5qpfvH2THra12ZpNugM_fURr2LRDKd)
13. [theoryofcomputing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8aRve6QnQoyP3d1r8hI8HQ3ZMj1YQjWD_jxkvMlUk1n2OfNCsz4oiUjTCiVi6Nq9XWnu5sKBq4R8mbLupTiVWdL4lsUhOFO-qoh8QpQuz1-AqWrTWy_2zU_N91XKOvL3eliYijD6W90oKR4ZO0CtO)
14. [iiserkol.ac.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFL95Y52r17muRZhl-_VKp65olZPh7neJYdRu2ROUMHb5LiXe2-VC69msNskFpc7r7FigWHnEEZDOSGPT7tbMVvzPXGUtZyqxubjbYpXEgCbWpq_q2pJW3T_QNC-L6RJPCSsiBKgGN8CqVyfFDJCULfsOmkism7lvpCVJQGORBD9Fq98JEmP63NZyuioLZFIqG7IBM4XOJnviG5mtATWi4ZEgk44PmV3XCBAVPBLFo_DAR8XrIrBsLa_BWLG4xfy2Mi2N2c3qiacK7dMqb9BWCqmfabFQo=)
15. [dokumen.pub](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHW4phBRPfHWQTrK_-dPZ8SITlQNUOeg00SzUENysPQZBcxfbFlHX1xbRJ3VWD_8dYYfnif7VaChI-pAmN8D1gJqczJwmhMKgiem5b4Z4604DpUNw4noYcNwzd91N44m99bSmo6tnMJSQGPYjMIF5sWoUD33ye2OcVB4FnI24LrX78DTkH4VxbpeN726EtksSXRV1LTUy9pp6LNQah-5Q==)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHY2dXpsL8bZ2LGyp0Ucp4y3nCaU81mbRxTGl--kpdScnK-EQ3OrU2p-gHAQorI4oFOOLroLN8Nh1I9u6hZb1KckrNC2oDkXNyGjvOqquRNq5iCeSDc61j5t2RCsYJ4gRu0UheFqbFhWgzIIj3P_Oi2Iu6HPfJu4ZgbQsNTuZkxzqkOeDGPIhw0gmEvvuHWw8BktdAFhbhrEGSROQ==)
17. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDRGB5AStdFWTFLUSqHUTAan_aOJ4L4DioivUYoomurVmA6JSCkfa9cNKSSWisxTmkL5R5yIlKFZs9fX7mx3ba7wlLC79yXkG13IusJwmqPbA5cXijFcGjJgK17RV-E68mzZHxaExP-oqpmHBBBb68i_ka3vq-Vpeca_YOA6uILG4qjyhboBSOH_VifQ==)
18. [cern.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8GcF6lLSoebavkCuczqwDw88IQKgE5n3rBMNdljxfLgHmSLbjCMhsYTVWRGJjzFSpBTPsqoCJTjdVxs9pELnYC6MjJIQomnpwrKJ204hXKwn2uR8qFND3l0e7nClAzcsBybosooOHy2VZzc442JGseJfNqBMEuhvhHilhWKSDPyFyNZLtJjOqPMTwlOznM-8-A0E--GxX3PFFhVTt)
19. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGG2zrvEhrrA04JkUmxrk3DwnvZzynYrr4z2Lhve5BFl9_hwnm-3Fi8RXpjE3JNAubyUxSkayzJbElFpDlOca4eA8NFwtNWm5ikAQGceQLbfR3aC_HZUENqtac12akuo9c=)
20. [acs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzisSE3nLJL3qTGt7-qa9Inxbnq2sW93JEZymtTOvg94Yxi12V2U4NQ68AN49iBkXkfnLvxGCfOKlp8cASP-GCJlqJnAaiVnx7th-B_KpU5hDnaSAtcZaP72b0m69ykSppXC8cSQ==)
21. [mdpi-res.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwF-m5Okfw2u7d94hQQlOCSj0d5uAiEIUHLcPInfEU4Nec6S0wxIp0PnJMy5XL8mKnsmFcIh4-OnkqHYJoqctg9TL3kYTIQfpkttbkHP4z0bbrzVJZS5IpzeDLZXHuzTEPy9fEcn0fYIhqQq_qfF0upaln7v003b09zPUZXnvj-pNl-sHcVsIjqxIZTLcKZqTsUyzGRH41qOA9FznijwTcREJDSyzYbnVc287eftFyPbvISq0j3HM=)
22. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUbf1eQXZipqvsYbeM83ol2uZJlIr3MYnW-OQ0pS2dbNOM2vA8kY26up6tJy7-tIhnkntZona2jawHxKf9pux5fUyk5qY-B4kuPkBUqdcCwkpndxSfxm7Az2nTjEo1OFNc-dQ-dECV)
23. [unige.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpChvAMzauxstvbwb9JbA6wIX9tNMWBmcPr3x1y3qNUvbhTkRm8_g66Pp2KE7kyjt7htH6832-9oGiu8AAqPij-wcTmo427cxawrU4NnaM1Me8GW9njsHCt9IOw2P6cg7Tk4RcSzgIljmu-4EznEjYqmDC-n5RAXVFdjmAN6PqeNbJ2WcGba4l4IVY-7CWNCEMCdehtuLxJ0Yc)
24. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4ddGmppMuyoBS-u6ZFzREk0I18NMhccVE15RjRiAUAFNuX1iinbLgURbTpjFWndSNMsiARwxHdUFpcfpGvENsoa29pedSVYUq5TkmUi6bW1TSkI5cyCT1HUx6a03nk2EeslpcQW8F_pu9JISz)
25. [unitn.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELVilRYzXRmKLP70My4mfVvWXZ7SAwEAII-UwaOZijVlHx8_KMOTzuhsMgweY7yXcNGmJ_4Z4jSGIuRT5zhqIbntEZykOUZw1sfL63xDb_eyy8ZxigWAxkNVWpKQUK9iotSIC88MlXn2MKG4ZIZv1GasTlvZFViyXoyujQYzW-tWyNOhm33Ark7hFUPidOwP2M0AYj75dC_A==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvgYWuwwgCcl9s1IHc3278jhAXKkUctvQ7o7G4YJ7qD-s3NqoPmAF2hhPXCkh66MMweTqUwHsyIdXj4EqN6c09197CW_r57_cQhHrbx9U0Cytq_IuJPRQ1)
27. [lonepatient.top](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAzQXCjZGtSJJvRFdxbyTV_9TNLGLrP9DUcvimU8TVY3P9NN6cdUN9bai-NIHxph3TwU9nf_9EEB5lcb3JbcJoQS2bACFEZwEpNDU9NihFCkayKVlLgEjpTUaGOFU46E8auPh1jMfOK9DFeQDoEg==)
28. [purdue.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWwxW9tmpHbqaGensqQcl2jr94XGCrnh5NfupDLAtI8gNYu8IjYESmRXsK7slXjNoZdkUwajAVUCPau45AuDifL3xNu5cs5R-EUJ7qZDGt9wYyuutIrktOpOR-BaWG3f44VCJ3_QM=)
29. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYTttRpev5Z4BysBZ5vIE1K2w0Ce1L35T27Updqhu-9U5JWnrgfP9umWo5Y5o_PKFCmErSuDjArAafk2CnOFUlNbrHMxiMYxI9jGqi8WNfsE1XUJk=)
30. [kobv.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVyprObjqWfYEmAF9EfSwXE5oAkvVvsCMPhBW6Gge_RKRhKXd6IxtYGYtafd3dzi8hhok12b2_PJFq357qhZNlAzC9hlKBOSw-fyUPI3V2JHN3vtH-LDz16zOxRn20wWhbUPE0VtXnfJ4qW9ivl0xoZnMXSQpt)
31. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFt44j1em8xT9_SCu38QRt9H3U-bFzpyampWd2TnJtTjYW5lACoaFe9-nPXh4p9u0gOVkBLtgp3btAcRao-LWS2zbeVTTC5Rxb4mrv7HXR2hPXtcjDWGPDJGzIQ8JhRjmauqqmWLhf5yzeEQ8Auk_MM5f5GMA==)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrJLx0NZ2RO9-FH8YNR0X3K5nY3yMNvrmM9OhuykaAy6cnuqLQ0ylXmtYUZPWjmztuib-g9Xh-HYQyVFJvOqnj3zzTQ2zqeMBfHsKPIis1VeY2wwlzr3K3)
33. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTHsUjqT7_rg9Tmo5-02xJAh6-gou6ztOwa5e3g5pBtjXzUJcIu-LCMrF4EMDgxTNh3Er4YFgU5u3DtvIbUzsrcvhOFBuIoscrEdBifoB_IJv2Kq2WcfDV8b6wG7xEvykaquaVL6rSgSPbS_FckpYC2_FLpN0nXV6x7YT7nChsYyHlSbmYiscZQGB5H7pcCtHJ2y2wDTGnJAhMeb-5xslRXo4mbQwrCAuqt4Cq)

