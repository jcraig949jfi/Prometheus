# T#57 Constant-factor approximation algorithms for tensor rank

**Pythia queue id:** 99
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChZqeG9QYXBqQU1zZjd1Z2ZRdlotSkRBEhZqeG9QYXBqQU1zZjd1Z2ZRdlotSkRB
**Elapsed:** 688s
**Completed at:** 2026-05-21T14:57:04.562796+00:00

---

# T#57: Constant-Factor Approximation Algorithms for Tensor Rank

**Key Points**
*   **Fundamental Difficulty:** Unlike matrix rank, computing the exact rank of a tensor (order 3 or higher) is provably NP-hard over the rational numbers and NP-complete over finite fields.
*   **Hardness of Approximation:** Mathematical proofs demonstrate that approximating the exact tensor rank integer to within a specific constant factor (specifically, $1 + 1/1852 - \delta$) is NP-hard.
*   **Open Problem:** Whether any general, polynomial-time algorithm can approximate the tensor rank integer within *any* arbitrary constant factor remains a major open problem in theoretical computer science.
*   **Algorithmic Success in Geometric Approximation:** While approximating the rank *integer* is difficult, researchers have successfully developed constant-factor and $(1+\epsilon)$ relative-error approximation algorithms for *low-rank tensor approximation*. These algorithms use sketching, CUR decompositions, and fiber-crosses to find a low-rank tensor that is geometrically close to the original data.
*   **Broad Implications:** Tensor rank approximations are critical for accelerating matrix multiplication, modeling implicit regularization in deep neural networks, and executing exploratory data analysis in high-dimensional spaces.

**Layman Summary**
Imagine a spreadsheet as a 2D grid of numbers, also known as a matrix. Finding the "rank" of this matrix—essentially identifying the minimum number of fundamental building blocks needed to reconstruct it—is a problem that modern computers can solve almost instantly. A "tensor" is simply the 3D (or higher-dimensional) equivalent of a spreadsheet, like a Rubik's cube made of numbers. Surprisingly, when we add just one more dimension to make it a 3D tensor, finding its rank becomes incredibly complex. In fact, it is classified as "NP-hard," meaning that it is computationally intractable to find the exact answer for large datasets.

Researchers have tried to find algorithms that "approximate" this rank, getting close to the true minimum number of building blocks. However, recent proofs show that even getting an approximation within a specific small percentage of the true answer is also impossibly hard. Because determining the exact or approximate "number" of building blocks is so difficult, scientists approach the problem from a different angle: they specify a small number of building blocks in advance and use algorithms to build a "shadow" or "sketch" of the tensor that acts almost exactly like the original. These geometric approximation algorithms successfully compress data and are vital for everything from quantum computing to training sophisticated artificial intelligence models.

***

## 1. Introduction to Tensor Rank and Multilinear Algebra

The mathematical formulation of "T#57" typically refers to specific cataloged open problems or theoretical inquiries regarding the bounds and approximation guarantees in computational complexity. In the context of multilinear algebra and theoretical computer science, the query regarding "Constant-factor approximation algorithms for tensor rank" strikes at the heart of an enduring dichotomy in computational mathematics: the divergence in complexity between matrix algebra and higher-order tensor algebra. 

### 1.1 Historical Context and Definitions
Conceiving the basic theory of linear algebra was a long process centered around the 19th century, during which matrices (2-dimensional arrays) were thoroughly analyzed [cite: 1]. Tensors, representing $d$-dimensional arrays for $d \geq 3$, were scarcely studied from an algorithmic complexity standpoint until much later [cite: 1]. The first rigorous notion of rank for tensors—variously known as the tensor rank, CP-rank (Canonical Polyadic rank), or CANDECOMP/PARAFAC rank—was introduced in a paper by Frank Lauren Hitchcock in 1927 [cite: 1, 2]. It was later rediscovered independently in 1970 by Carroll and Chang, and by Harshman, finding immediate applications in psychometrics and linguistics [cite: 1, 2].

To define tensor rank formally, let $V_1, V_2, \dots, V_d$ be vector spaces over a field $\mathbb{F}$. An order-$d$ tensor $T$ is an element of the tensor product space $V_1 \otimes V_2 \otimes \dots \otimes V_d$ [cite: 3]. A tensor $T$ is called a "pure tensor" or a "rank-1 tensor" if it can be expressed as the outer product of $d$ vectors: 
\[ T = a_1 \otimes a_2 \otimes \dots \otimes a_d \]
where $a_i \in V_i$ [cite: 1, 4]. 

The **tensor rank** of $T$, denoted as $\text{rank}(T)$ or $R(T)$, is defined as the minimal integer $r$ such that $T$ can be expressed as a sum of $r$ rank-1 tensors:
\[ T = \sum_{i=1}^r T_i \]
where each $T_i$ is a rank-1 tensor [cite: 2, 4]. If $T$ is the zero tensor, its rank is conventionally zero [cite: 4]. 

### 1.2 The Divergence from Matrix Rank
In the matrix case ($d=2$), computing the rank is a well-understood and easy task [cite: 5]. Algorithms such as Gaussian elimination or Singular Value Decomposition (SVD) calculate the matrix rank in polynomial time [cite: 5, 6]. Furthermore, matrix rank obeys several canonical properties: the rank of a block diagonal matrix is the sum of the ranks of its blocks, and the matrix rank satisfies the multiplicativity property $\text{rank}(A \otimes B) = \text{rank}(A)\text{rank}(B)$ [cite: 1].

However, many basic properties that hold for matrix rank completely fail when extended to tensors of order 3 or higher [cite: 1]. For instance, tensor rank only satisfies a submultiplicativity property $R(T \otimes S) \leq R(T)R(S)$ [cite: 1]. Furthermore, a longstanding conjecture by Volker Strassen regarding the additivity of tensor rank for disjoint variables was eventually disproved by a counterexample published by Shitov in *Acta Mathematica* [cite: 1]. Another critical issue is the absence of canonical forms. Whereas every rank-$k$ matrix is equivalent, through two changes of basis, to a $k \times k$ identity block completed with zeros, a counting argument demonstrates that such a reduction cannot be hoped for in the case of tensors of order 3 or higher [cite: 1].

## 2. The Computational Complexity of Tensor Rank

The algorithmic hurdle in tensor analysis fundamentally stems from its computational complexity. While finding the minimal number of rank-1 matrices to reconstruct a matrix is easily computable, doing so for a 3-tensor is notoriously intractable.

### 2.1 Hastad's NP-Completeness Theorem
The complexity of computing tensor rank was definitively classified in 1990 by Johan Håstad [cite: 1, 4]. Håstad proved that calculating the exact tensor rank of a given three-dimensional tensor is NP-hard over the rational numbers $\mathbb{Q}$, and NP-complete over any finite field $\mathbb{F}_q$ [cite: 1, 4]. 

Håstad's reduction relied directly on the 3-SAT problem [cite: 7]. By converting boolean satisfiability constraints into multilinear polynomials, he demonstrated that finding a minimal pure-tensor decomposition is equivalent to satisfying the boolean formula [cite: 4, 7]. This result established that, unless P = NP, no polynomial-time algorithm can compute the exact tensor rank. Consequently, much of the research following Håstad's 1990 paper has shown that most problems involving tensors are inherently hard to compute [cite: 4].

### 2.2 Algebraic Geometry and Field Dependence
Tensor rank is highly field-dependent [cite: 2]. A real-valued tensor may have a different rank when considered over the real numbers $\mathbb{R}$ compared to its rank over the complex numbers $\mathbb{C}$ [cite: 2]. The same is true for the real quaternion algebra, where a complex tensor can have different ranks over the complex field versus the real quaternion algebra [cite: 8]. 

Furthermore, unlike the matrix case, there may be several distinct group orbits for the same tensor rank [cite: 3]. For example, even in the relatively simple tensor space $\mathbb{C}^2 \otimes \mathbb{C}^2 \otimes \mathbb{C}^2$, which has finitely many orbits under the general linear group action, there are four distinct orbits for tensor rank two [cite: 3]. This algebraic complexity prevents simple linear-algebraic operations from yielding the rank, forcing algorithms to search through a complex, non-convex geometry.

## 3. Hardness of Approximating the Tensor Rank Integer

Given that exact computation of tensor rank is NP-hard, the standard algorithmic recourse in theoretical computer science is to seek an approximation algorithm. A "constant-factor approximation algorithm" for tensor rank would take a tensor $T$ and output an integer $k$ such that $R(T) \leq k \leq c \cdot R(T)$ for some universal constant $c > 1$.

### 3.1 Swernofsky's Inapproximability Bound
In 2018, Joseph Swernofsky established a stringent lower bound on the approximability of tensor rank [cite: 9]. Swernofsky proved that approximating the rank of a 3-tensor to within a factor of $1 + 1/1852 - \delta$ (for any $\delta > 0$) is NP-hard over any field [cite: 9]. 

The proof was accomplished via a sophisticated reduction from bounded occurrence 2-SAT (also known as MAX-E2-SAT) [cite: 9]. In a MAX-E2-SAT instance, the input consists of variables and disjunctive clauses of size exactly 2, and the goal is to maximize the number of satisfied clauses [cite: 9]. Swernofsky's construction was a re-analysis and simplification of Håstad's original 1990 reduction [cite: 9]. He showed that if bounded occurrence SAT is used as the starting point for the reduction, significant extra rank can be guaranteed from unsatisfied clauses compared to the rank in a perfectly satisfiable case [cite: 9].

### 3.2 Technical Roadblocks in the Reduction
The difficulty in proving inapproximability for tensor rank lies in the algebraic behavior of tensor slices. A 3-tensor can be viewed as a sequence of matrix "slices." In matrix rank, eliminating rows or columns behaves predictably. However, in tensors, as Swernofsky noted, the non-eliminated (leftover) slices can possess a rank greater than 1, making it highly unclear what the overall rank of the combined tensor is [cite: 5, 9]. Secondly, even the task of choosing which scalar multiples to use when adding one slice to the others is NP-hard, a property explicitly exploited in showing the NP-hardness of tensor rank [cite: 5, 9].

Independently, around the same time, Bläser et al. proved a similar inapproximability result, albeit without an explicit numerical constant and using a slightly more involved argument [cite: 9].

### 3.3 The Open Problem of General Constant-Factor Approximation
While Swernofsky established a lower bound of $1 + 1/1852$, a massive gap remains in the upper bounds. Swernofsky explicitly articulated the outstanding open question: *is tensor rank hard to approximate within any arbitrary constant, or within a specific unbounded function?* [cite: 5, 9]. Furthermore, it remains an open problem to discover *any* non-trivial approximation algorithm that can guarantee an output within a constant factor of the true tensor rank [cite: 5, 9]. Because the highest rank known for an explicit family of 3-tensors is $3n - o(n)$ despite dimension counting showing that tensors with rank at least $n^2/3$ exist, the mathematical tools available to upper-bound rank computationally are incredibly weak [cite: 5, 9].

## 4. The Shift to Low-Rank Tensor Approximation

Because finding an approximation to the *integer value* of a tensor's rank is mathematically prohibited (at least within small constants, and potentially altogether), the computer science and applied mathematics communities have reframed the problem. Instead of asking "What is the approximate rank of $T$?", researchers ask, "Given a fixed rank $k$, can we find a tensor of rank $k$ that approximates the geometric data of $T$ within a constant factor of the minimal possible error?"

### 4.1 The Standard Approximation Problem
In this reframed optimization problem, we are given an order-$d$ tensor $A \in \mathbb{R}^{n_1 \times \dots \times n_d}$, and we want to output a rank-$k$ tensor $B$ for which the Frobenius norm of the difference is minimized [cite: 7]. Let the optimal distance be defined as:
\[ \text{OPT} = \inf_{\text{rank}(A') \leq k} \|A - A'\|_F^2 \]
The goal of a relative-error low-rank approximation algorithm is to find a $B$ such that:
\[ \|A - B\|_F^2 \leq (1+\epsilon)\text{OPT} \]
or, for a constant-factor approximation:
\[ \|A - B\|_F^2 \leq c \cdot \text{OPT} \]
for some constant $c > 1$ [cite: 7].

### 4.2 The Ill-Posedness of Tensor Approximation
A fundamental barrier to solving this continuous optimization problem is that it is often mathematically ill-posed [cite: 2, 10]. In a seminal 2008 paper, de Silva and Lim demonstrated that the set of tensors of rank at most $k$ (for $k \geq 2$) is not closed in the standard Euclidean topology [cite: 2, 10]. 

Because the set is not closed, the infimum distance ($\text{OPT}$) might never be achieved by any actual rank-$k$ tensor [cite: 2, 11]. A sequence of rank-$k$ tensors can converge to a tensor that has a strictly greater rank [cite: 2]. This limit tensor is said to have a "border rank" of $k$, even if its exact tensor rank is much higher [cite: 3]. Therefore, algorithms seeking the "best" rank-$k$ approximation may diverge, as the parameters of the rank-1 components grow to infinity in magnitude while canceling each other out to approach the target tensor [cite: 2]. 

## 5. Algorithmic Frameworks for Low-Rank Approximation

Despite the ill-posedness of the CP-rank approximation problem, breakthrough algorithms have been developed to provide constant-factor and $(1+\epsilon)$-relative error approximations, bypassing theoretical pitfalls by utilizing specific data structures, randomized numerical linear algebra, and alternative tensor formats.

### 5.1 Sketching and Oblivious Subspace Embeddings
To achieve constant-factor regression and low-rank approximation in tensors, researchers have deployed "sketching" techniques. Song, Woodruff, and Zhong (2018) provided the first relative error low-rank approximations for tensors under a variety of robust error measures [cite: 7, 12]. 

The primary challenge in tensor sketching is avoiding the "curse of dimensionality" that occurs when flattening a tensor into an exponentially large matrix [cite: 11]. Song et al. designed constant factor approximation oblivious subspace embeddings to bypass standard limitations [cite: 7]. A key innovation was the use of an explicit mapping based on uncertainty principles and randomness extractors [cite: 7]. After applying known oblivious subspace embeddings, this mapping quickly spreads out the mass of the vector, rendering random sampling highly effective [cite: 7]. Crucially, this refined technique avoids the logarithmic factors typically incurred in the sketching dimension from matrix Chernoff bounds [cite: 7]. This yields polynomial-time algorithms that guarantee a $(1+\epsilon)$ relative error or a constant-factor approximation to the optimal rank-$k$ approximation [cite: 7].

### 5.2 Fiber-Crosses and Black Box Approximation
Another highly successful paradigm for constant-factor tensor approximation is the use of "fiber-crosses." An order-$d$ tensor contains "fibers," which are the 1-dimensional equivalents of matrix rows and columns (e.g., keeping all indices fixed except one) [cite: 13]. 

Espig, Grasedyck, and Hackbusch (2009) introduced a black-box type algorithm for approximating tensors in high dimensions [cite: 14, 15]. The algorithm adaptively determines the positions of entries of the tensor $A$ that need to be computed or read [cite: 12, 14]. For efficiency, these positions are strictly located on intersecting fibers, known as "fiber-crosses" [cite: 14, 15]. Using a remarkably small number of these entries, the algorithm constructs a low-rank tensor approximation $X$ that minimizes the Euclidean distance between $A$ and $X$ at the evaluated positions [cite: 12]. 

### 5.3 Cross Tensor Approximation (CTA) and CUR Decompositions
Building on the fiber-cross concept, Cross Tensor Approximation (CTA) operates as a generalization of the CUR matrix approximation method [cite: 13]. In matrix CUR approximation, a matrix $A$ is approximated by $C U R$, where $C$ consists of a subset of actual columns of $A$, $R$ consists of a subset of actual rows, and $U$ is a small intersection matrix [cite: 14].

For a matrix $A \in \mathbb{R}^{m \times n}$, one chooses a submatrix of $p$ columns to form $C$ and $q$ rows to form $R$ [cite: 14]. By selecting columns and rows thoughtfully (or via specific randomized distributions), researchers obtain improved relative-error and constant-factor approximation guarantees in worst-case analysis [cite: 14]. This represents a significant advancement over much coarser additive-error guarantees [cite: 14]. 

When generalized to tensors, CTA samples a subset of fibers or slices. Because existing decomposition frameworks (like unrestricted CP decomposition) do not preserve the natural structure (like non-negativity or sparsity) of the original data, CTA uses parts of the actual tensor data to ensure structural preservation [cite: 13]. This method drastically mitigates the complexity of high-dimensional low-rank approximation, rendering it applicable to real-world datasets in linear or sublinear time [cite: 13].

## 6. Advanced Tensor Formats: Bypassing CP-Rank Limitations

Because the standard CP-rank is difficult to approximate and ill-posed, modern computational mathematics has embraced alternative definitions of tensor rank that admit robust, polynomial-time low-rank approximations.

### 6.1 Tucker Decomposition and Higher-Order SVD (HOSVD)
The Tucker decomposition, sometimes referred to as Higher-Order SVD (HOSVD), decomposes a tensor into a small "core" tensor multiplied by orthogonal matrices along each mode [cite: 2, 11]. Unlike the CP decomposition, the Tucker format forms a closed set, making the best low-rank approximation problem well-posed [cite: 2]. A polynomial-time algorithm exists for identifying if a tensor is of rank 1 using HOSVD, and while it does not directly yield a minimal CP-rank, it provides deterministic constant-factor approximations to the optimal Tucker core [cite: 2].

### 6.2 Tensor Train (TT) and Hierarchical Tucker (HT)
To completely circumvent the curse of dimensionality—where an order-$d$ tensor of dimension $n$ has $n^d$ entries—Oseledets introduced the Tensor Train (TT) format, and Hackbusch developed the Hierarchical Tucker (HT) format [cite: 11, 16].

In these formats, the "rank" is defined differently. The TT-rank (or compression rank) is defined by the separation ranks of the tensor unfoldings [cite: 16]. A critical mathematical result proves that the TT ranks of a tensor are unique and equal to their respective separation ranks, provided the components fulfill a maximal rank condition [cite: 16]. 

Furthermore, the set of TT tensors of fixed rank $\overline{r}$ locally forms an embedded manifold in the tensor space [cite: 16]. By preserving the essential theoretical properties of the Tucker format but vastly improving scaling behavior, the TT format ensures that approximation algorithms operate on a smooth manifold [cite: 16]. By introducing gauge conditions, researchers obtain a unique representation of the tangent space of the TT manifold, allowing for stable, efficient gradient descent and alternating optimization algorithms that converge to local optima reliably [cite: 16].

### 6.3 Quantized Tensor Train (QTT)
When dealing with function-related tensors—such as discretizations of partial differential equations—the Quantized-TT (QTT) format is highly effective [cite: 11]. By applying quantization to each mode, a tensor of dimension $N = 2^D$ is reshaped into a tensor of order $d \cdot D$ with dimensions $2 \times 2 \times \dots \times 2$ [cite: 11]. The TT decomposition of this heavily folded tensor allows functions with varying levels of smoothness to be approximated with logarithmic parameter complexity [cite: 11]. QTT provides extremely fast approximations for the FFT, convolutions, and evaluations of boundary integrals [cite: 11].

## 7. Quantum and Sublinear-Time Algorithms

As the size of tensors grows to billions of parameters, even linear-time algorithms become computational bottlenecks. Consequently, recent breakthroughs have targeted sublinear-time and quantum approximations.

In classical randomized numerical linear algebra, coresets and sensitivity sampling are employed to select a tiny subset of the data that provably acts as a proxy for the entire tensor [cite: 10]. For instance, sensitivity sampling assigns a probability distribution over the entries based on their importance, allowing for a constant-factor approximation to optimal distances [cite: 10]. 

Recent literature (e.g., 2025 advances) has introduced the first quantum sublinear-time algorithms for low-rank approximation that do not rely on data-dependent parameters [cite: 10]. Operating in time $\widetilde{O}(n d^{0.5} k^{0.5} \epsilon^{-1})$, these algorithms rely purely on sampling rows and columns recursively via Grover search and quantum amplitude estimation [cite: 10]. These methods are subsequently extended from matrices directly to tensor low-rank approximations under the Frobenius norm, vastly broadening the range of achievable approximations in extremely high-dimensional spaces [cite: 10].

## 8. Theoretical Applications and Implications

The quest for approximating tensor rank and discovering low-rank approximations is not merely a theoretical puzzle; it underpins critical problems across mathematics and computer science.

### 8.1 The Complexity of Matrix Multiplication
The most famous application of tensor rank is characterizing the complexity of matrix multiplication, encapsulated by the exponent $\omega$ [cite: 6, 17]. The procedure for multiplying two matrices can be entirely encoded as a 3-order tensor [cite: 6]. If one computes the exact tensor rank of the $n \times n$ matrix multiplication tensor, the value dictates the minimum number of scalar multiplications required [cite: 6]. 

Volker Strassen's revolutionary algorithm for $2 \times 2$ matrix multiplication requires 7 multiplications (compared to the schoolbook 8). This perfectly aligns with the fact that the rank of the $2 \times 2$ matrix multiplication tensor is exactly 7 [cite: 5, 6]. However, the exact rank of the $3 \times 3$ multiplication tensor remains an open problem, with current bounds placing it between 19 and 23 [cite: 5, 9]. Because calculating tensor rank is NP-complete [cite: 4], researchers cannot simply compute the decomposition to generate the most efficient algorithm algorithmically [cite: 6]. Thus, $\omega$ is heavily dependent on understanding "asymptotic tensor rank," a notoriously difficult parameter to bound [cite: 17, 18]. Structural results on asymptotic tensor rank show that the set of achievable asymptotic ranks is closed under the application of polynomials with non-negative integer coefficients, implying discrete but highly complex behaviors [cite: 17].

### 8.2 Combinatorics and The Cap Set Problem
The mathematical intractability of standard tensor rank led to the development of alternative ranks, such as "slice rank" [cite: 1]. The concept of slice rank was introduced by Terence Tao to reformulate the breakthrough solution to the Cap Set problem by Croot, Lev, Pach, Ellenberg, and Gijswijt [cite: 1]. By analyzing the upper bound of the slice rank of a tensor indicating $x + y + z = 0$ against the full rank of an identity tensor, they resolved a decades-old problem in additive combinatorics [cite: 1].

### 8.3 Machine Learning and Implicit Regularization
In modern machine learning, tensor rank serves as a rigorous measure of complexity for deep neural networks. Recent empirical explorations motivate that tensor rank perfectly captures the implicit regularization of non-linear neural networks [cite: 19]. Low-rank tensor models of joint Probability Mass Functions (PMF) allow algorithms to circumvent the curse of dimensionality by learning principal components of the joint distribution directly [cite: 20]. This enables highly efficient exploratory data analysis and classification performance without explicitly computing exponentially large tensors [cite: 20].

## 9. Conclusion

The problem of computing the tensor rank bridges algebraic geometry, computational complexity, and applied algorithms. On one side of the chasm lies the fundamental hardness: Johan Håstad proved exact calculation is NP-complete [cite: 4], and Joseph Swernofsky proved that even approximating it within a factor of $1 + 1/1852 - \delta$ is NP-hard [cite: 9]. The existence of an algorithm capable of approximating the tensor rank integer within an arbitrary constant factor remains a tantalizing open mystery in computer science [cite: 5, 9].

On the other side of the chasm lies practical algorithmic success. By changing the objective from calculating the exact rank integer to finding a low-rank geometric approximation of the tensor itself, mathematicians and computer scientists have developed a rich library of techniques. Utilizing fiber-crosses, sketching, oblivious subspace embeddings, and formats like Tensor Train and Hierarchical Tucker, modern algorithms can achieve constant-factor and $(1+\epsilon)$ relative error approximations in polynomial—and occasionally sublinear or quantum—time [cite: 7, 10, 13, 14]. 

These advancements ensure that, despite the NP-hardness of the underlying algebraic property, tensors remain one of the most powerful and scalable tools for understanding high-dimensional data, optimizing machine learning networks, and probing the ultimate limits of computational speed.

**Sources:**
1. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHR9rv65I4akMx_Wo2xgDnmiLK1xaqXRz_rtXP3-pgKiU5EeFRPNye-njmlDYzR7dLerkCGJmVXjRE-V_2IE_3RMWXZqq-25muEnxMahEwy6SA2I8uCJya02m3G)
2. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_0zMi41jrjfAqF-q-0U3r3jvWFpiO7MVRXhcYwR6tFmiXQ-Jbar8E8_k92ortEdu9eDdWOI1P_2ulHPgWxkpzx4a3BsJrrWY36ToIO16RqV8UD5KPDdmHwSLiDvhjlNC_ndXEon3C48v0NqgX)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3nu0Oab6HtlCZj3TaNMsfBxR6G15YrWDozF1OG-rFg4-9pnevXGuwqef5EUNTtE3EDpHGIxZvIYiAXvc6Fios60gctF9lBbST_-9G-lOm49A66RWNMw==)
4. [jeremykun.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwDqJiFZCvU6NxIvDxCg1XHl6djWEzvr2lY07iP0Xe3osTO5de2HaBlzR883vZfaZkR6lE6oyfOOsdt0kTGOT96_LHYf98ljLFLNAQAqt27J0M5S_HtWOHyVTuRGDfw-4UKWYMwztfLGZEub9A9piLOmuabqvz-Q==)
5. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvdfgib-Ibs1J2voa0a5LH_GdYpF23yZlU5v78vPv5VQ3tU3tT_gSlhgThxxRzOT7l6WFQGNQ-InAHF3WJKMEMb7jSGq2Ddq9ZVfht66iVhk-69qEUQxmS3SIt7Ua5WxwHub4vx0lO52Eaug==)
6. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGemTq79y3Z-Fx5XDNspYAABsbymW_KW-PgLL-cShi7-OYb1lclh9UHuTCVbQkuQOCyiYnd52dldJ4p0EZKJmIFf-8qsXeItm87awu-gIVwRq_WjQ0KaJv-ICCL2UuKpYmaxaptVhOSZQ==)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHK_YFNwraHlqhWibWjVu6j9sfVFi9MsesxxzNbuu6EmnlgFr5A5dOZOCxr9WGYtYB6eai0y-v2yHqYVM-AWjH6ljoVlArSdy4ofRisQw3CkfdwFcPaTcc48OEhsMJd7Mnm5w7KTbgH83c9B-y7Ov-mxHxEkf-PJw0J_2jLGy_lLG003PqHLPMjBr1f2Ng=)
8. [umanitoba.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7UHnDIOsb8Jy_jmEcHpeDAr-TrHtoyucx-4lnqMgo-wey2qeWWYGu0E0-pUhIq9hpjPznIhOVHpOS8cmV_5dOxvwTHRbs9hFp7ksIjoI3TUzkgVz9Mf5H9Ls2nhizDSUqY4kpJcr77OnHiHfXtnlh5ywGuMoUvxZ81Kr6QkXLrAoixqWZzzVoaNn_JRJGua481El1XFaLKQxIOen1)
9. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGlhFEWC3pImCMM5Hn7UjybP4ChFwHmKpMdJT4oMiDSOWJ2GeTwvB6aTCHpFn3AddNjxnX6Vh0fBQnZXgBY5xSx9pNGwSdCNC0U52aho_m7h9K479VLZpEzJyNx_EOogEyLiqwZwjFV2lfpslhtpD4OWyLikMn-8TyC4u2LMhaKt9xeVOg4CDGP4QvA5_5viS7THZPcY-dGggG3Xh8vEnMK0tHr3Ai-EInJHyn1cvQf6ZaQ-_fqZ01UN8sPdYVDCw==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhxgTeq1shg8BaKN9awQx5a5IltrWxCw70zqe4d8OXpHAX41g90HN1M5wMvtq01RFgH6aujl9NdWMAGrdreBRPxXcevpgzPsbb4PTY2EZU6G9x5uU61A==)
11. [epfl.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCtwBF5_RL_1eaaLxtl5scixI2lF_pEB98po9X8oQjMurYacGST3uN7gEGi5tGoz-zGAna0ExzT7Rj_bN1fYY1WeOXk_iw1JcC99bQsywEhm4ShoLWwXTlPjgM_WrIm5YOhT8BGkwTe-FfyWz8A7fvR9vNxQ==)
12. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-nT6g77qBFMKrd-sw9OUYwcH5xLESaxJU1rKu35EQt5ZLCOnRYwrkNhk25F5I59O62uWJZIZEGkFqrp6cuewe8qHyiXAoLeN-I83XTY86huDxhPfrGks0BEfor9tFIZm-ekQbuuyzl0n9DtrEQzSXCZ2x0VROUmsaTkjIA2kmIGZOHF4ZZzBGrJVUDCsHsxBBz0bgwyPP3WthjSJrQyH_4SYnjPiXn3GeSSp5mv3kFNCIOYmZ6ojRPSnr5OB8r3bCFBmruQ==)
13. [unlp.edu.ar](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkI2_oJVE0kqWU3mG6M1NXgrBgfBdP2zYVubZiwejXBtQgDe1zoTnjhEutMNDiBLV5DK64FWaAojaSq4wxGgh7LleNzjarLdntOhLwjvVO5qVCXDfIpgvMQawoaXNfpzmWd56s9AZUz7qK8cQq3YlpnY0rtII=)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6E5F91MZaPGvFxwOE6XpnxNSRDJdWz0zcQ0bfohw8A9ZFyjx9t0To4VMuYpU6tLM7YGyaIBZLW1ONl2Wk4uWD6FmcyYGRBwtE2g7DgKsulO3KhZsKkHAY2287QKV6BQM2VkUoD94iD8U8F3mRcsdiWLHoP75IP2zEMMwmcy6cauGQfPn_DGNaQvTAPUodZO3Sa0avJvZ7u92i4Saq)
15. [sci-hub.box](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGv3sxmXfgs-b_fhOD9Zgc-SDIzsWnCtTsXcRiT_WF_DAFCo76mWZ6tnLXCDuEcfeSLCAC0ifIGjmK_M1T8POtlyLrujMmQPFWvHhlqZidvUnEnmWoUvXwApL-kWH7fzGFPuqOAEB9)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfstIKAEQOyMgbKx-pdcBxYH93XhajDzxTsX4j_pkBrC1hZiUPxx2jkUBgtjxf2vwgwQmcFrzSNoT3qnoFRukh-PxTHEoK9h2L39C5UVxqSDEOLzyaLrN7__Cm1VxMfz9CrPU_3e2OiQgyHMWl4BBsSHLHk6eeKb8l0PZep28TyvpIsPbup3J5enuJxxk93r-l)
17. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcPDGLSrO1AjRtLCgnWAWKi04H9mcLpULsS4dfTcDvCChZ28FACH_0gRb2tFMiSaQr1-cw8QH3BsHfYwGPuFPKjQccib6YvAFIhKFJdbcPtzBEsUKOtZVG9Iih)
18. [conference-publishing.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqnam89mspgu9vpLjCvaU2n_2wiRLA5eCONzCp6fvIctzdLaGwZM8rgaKu-1-jlazF9EL93w-waQyeSUgToxvDsriLojmeo3ALEsdKIejHbSu0ZvHTd6EqFYcyKn6drIKJQNnXcBtM-zqz)
19. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2nNkWYOMg0eKXr7tD_54RdR5DM-MefKwBIMpDQNTG4JgMnMZcA1xoDch1HNQ8gGvgz140YAdTFe8BKZ8-LMvxBf6bNCSRgQz3nSRx0gXHKi3IwpKEKmWYqyskuU6yD7M=)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRcasdEovZ_Cgw6VZkFRQHSiJS-iv57hVvKKcCa-tw8rMX9jZD_AUrh1252Yq457fDElwuT9ikcjOgIn2ptH4vSs5Dd0Tc-I80rUezhc084R-7mfH-WU2W1loH6KwIo_Rl-LgWeaN-cjJCCz1n4JtZ5mPoGg542DRqUGPgeywYRNfYi0L_Esz8OmRB9gIs189kKfIHrYeuZh7I4rCUw8PpUmZQUItsSjpRS3r0D17oNLuFRy3f)

