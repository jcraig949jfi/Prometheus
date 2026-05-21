# T#87 Tensor rank of multidimensional DFT (d>=3)

**Pythia queue id:** 121
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChZvQ1FQYXF6UkhzM291Z2ZsMzZYSUR3EhZvQ1FQYXF6UkhzM291Z2ZsMzZYSUR3
**Elapsed:** 493s
**Completed at:** 2026-05-21T15:36:46.582810+00:00

---

# T#87: Tensor Rank of the Multidimensional Discrete Fourier Transform (\(d \geq 3\))

This report provides an exhaustive, academically rigorous examination of the tensor rank of the multidimensional Discrete Fourier Transform (DFT), particularly for dimensions \(d \geq 3\). Based on contemporary research in multilinear algebra, algebraic complexity theory, and computational optimization, it systematically unpacks the mathematical properties, complexity bounds, and algorithmic implications of representing the DFT as a higher-order tensor. 

**Key Points:**
- **Computational Intractability:** The tensor rank problem is profoundly difficult. Research has rigorously proven that computing the rank of a general third-order tensor is NP-complete over finite fields and NP-hard over the rational numbers [cite: 1, 2]. Unlike matrices, tensors do not strictly adhere to the Eckart-Young theorem, making best low-rank approximations ill-posed [cite: 3, 4].
- **The Collapsed DFT (CDFT):** A significant breakthrough in the study of DFT tensors is the introduction of the *Collapsed DFT (CDFT)* tensor. This mathematically distinct generalization of the standard even-order DFT tensor allows for the exact computation of the rank of third-order CDFT tensors when the underlying space dimension is a prime number [cite: 5, 6]. 
- **Bilinear Complexity:** The tensor rank of a bilinear operation's structure tensor corresponds precisely to its bilinear complexity (the minimum number of non-scalar multiplications required) [cite: 7, 8]. While the DFT itself possesses zero bilinear complexity inherently (as it multiplies variables only by constant roots of unity) [cite: 7], it acts as a critical operator to minimize the bilinear complexity of related operations like multidimensional convolutions [cite: 9].
- **Disambiguation of "T#87":** It seems highly likely that the "T#87" designation in the query originates from software profiling artifacts. In deep learning compilers like TensorFlow Lite's Model Analyzer, tensors within a computational graph are systematically indexed (e.g., `Op#21 DEPTHWISE_CONV_2D(...) -> [T#87]`) [cite: 10, 11]. Conversely, the latter half of the query refers to a profound problem in theoretical computer science and mathematics. Furthermore, "DFT" is concurrently used in the physical sciences to denote Density Functional Theory [cite: 12, 13], though this report focuses on the Discrete Fourier Transform.

---

## 1. Disambiguation and Contextualization

Before delving into the dense multilinear algebra surrounding the multidimensional DFT, it is critical to contextualize the terminology used within the query.

### 1.1 The Meaning of "T#87"
In the context of modern machine learning frameworks, operations and their input/output multidimensional arrays (tensors) are tracked systematically to optimize execution. Tools like the TensorFlow Lite Model Analyzer map out the execution graph of neural networks, designating operators as `Op#` and tensors as `T#` [cite: 10, 14]. For instance, a log output might read `Op#20 CONV_2D(T#155, T#88, T#9) -> [T#156]`, or involve a tensor `T#87` [cite: 11, 14]. While `T#87` explicitly denotes the 87th tensor in a specific serialized computational graph, the query pairs this software engineering artifact with a profound theoretical mathematics problem: the tensor rank of the multidimensional DFT. 

### 1.2 Disambiguation of DFT
In the physical and chemical sciences, "DFT" overwhelmingly stands for *Density Functional Theory*, a computational modeling method used to investigate the electronic structure of many-body systems [cite: 12, 13]. Advanced chemical applications even employ constrained nuclear-electronic orbital DFT (CNEO-DFT) to compute static polarizabilities and Raman spectra [cite: 13]. However, given the query's explicit reference to "tensor rank" and dimensions "\(d \geq 3\)", the subject is unequivocally the *Discrete Fourier Transform* [cite: 5, 15]. 

---

## 2. Mathematical Foundations of Tensors

To rigorously define the tensor rank of the multidimensional DFT, one must first establish the foundational properties of tensors. 

### 2.1 Vector Spaces and the Tensor Product
In mathematics, the modern component-free approach defines a tensor as an abstract object expressing a definite type of multilinear concept [cite: 16]. Given a finite set of vector spaces \(\{V_1, V_2, \dots, V_d\}\) over a common field \(\mathbb{F}\), one forms their tensor product \(V_1 \otimes V_2 \otimes \dots \otimes V_d\). An element of this space is a tensor of order (or degree) \(d\) [cite: 16, 17]. 

If there are \(m\) copies of a vector space \(V\) and \(n\) copies of its dual space \(V^*\), the tensor is of type \((m, n)\) [cite: 16]. When coordinates are chosen, an order-\(d\) tensor can be represented as a \(d\)-dimensional grid of scalars. Thus, a rank-0 tensor is a scalar, a rank-1 tensor is a vector, a rank-2 tensor is a matrix, and tensors of order 3 or greater are multi-way arrays [cite: 18].

### 2.2 Simple Tensors and Tensor Rank
A tensor \(X \in \mathbb{R}^{n_1 \times n_2 \times \dots \times n_d}\) is considered a *simple tensor* (or a rank-1 tensor, elementary tensor, decomposable tensor) if it can be expressed as the outer product of \(d\) vectors [cite: 16, 19]. Mathematically, this is written as:
\[ X = u^{(1)} \otimes u^{(2)} \otimes \dots \otimes u^{(d)} \]
where \(u^{(i)} \in \mathbb{R}^{n_i}\) [cite: 19, 20]. 

The **tensor rank**, often denoted as \(\text{rank}(T)\) or \(R\), is defined as the minimum number of simple (rank-1) tensors needed to generate \(T\) as a linear combination [cite: 20, 21]. Therefore, \(T\) has rank \(R\) if:
\[ T = \sum_{i=1}^R u_i^{(1)} \otimes u_i^{(2)} \otimes \dots \otimes u_i^{(d)} \]
This decomposition is widely known as the Canonical Polyadic (CP) decomposition or CANDECOMP/PARAFAC [cite: 20, 22]. An intuitive way to think of the rank of a tensor is that it measures the "orderliness" of the array, with rank-1 tensors being the most orderly [cite: 18, 19]. 

### 2.3 Matrix Rank vs. Tensor Rank
While the definition of tensor rank extends the notion of matrix rank, their mathematical properties diverge dramatically [cite: 16, 17]. For a matrix (\(d=2\)), the rank is easily computable in polynomial time via Gaussian elimination or the Singular Value Decomposition (SVD). Furthermore, the row rank and column rank of a matrix are always equal.

For tensors of order \(d \geq 3\), the situation is drastically different. A tensor has multiple \(n\)-ranks (or multilinear ranks). The \(n\)-rank of a tensor \(A\), denoted by \(\text{rank}_n(A)\), is the dimension of the vector space spanned by the mode-\(n\) vectors (fibers) of \(A\) [cite: 20]. Unlike matrices, the different \(n\)-ranks of a higher-order tensor are not necessarily the same, and the CP rank \(R\) is only bounded from below by the \(n\)-ranks (\(\text{rank}_n(A) \leq R\)) [cite: 20].

### 2.4 The NP-Hardness of Tensor Rank
The computational difficulty of determining the exact rank of a tensor is a central theme in theoretical computer science. It has been rigorously proven that determining the rank of an order-3 tensor over any finite field is NP-Complete, and over the rational numbers \(\mathbb{Q}\), it is NP-Hard [cite: 1, 2, 16]. 

Håstad (1990) demonstrated that testing whether a tensor has a certain rank over finite fields is in NP and NP-hard [cite: 1, 2]. Hillar and Lim later adjusted these proofs to show that the tensor rank problem over \(\mathbb{R}\) and \(\mathbb{C}\) remains NP-hard. In fact, evaluating the tensor rank problem over a field \(\mathbb{F}\) is polynomial-time equivalent to the existential theory of \(\mathbb{F}\) (\(\text{ETh}(\mathbb{F})\)) [cite: 1]. This means that the problem is as hard as finding a root for a system of multivariate polynomial equations, placing it deep within the complexity hierarchy [cite: 1].

---

## 3. Alternative Notions of Rank and Tensor Geometry

Because the exact CP tensor rank is notoriously difficult to compute and behaves poorly under topological limits, mathematicians have introduced several alternative definitions of rank.

### 3.1 Border Rank and Ill-Posedness
One of the most striking differences between matrices and higher-order tensors is that the set of tensors of rank at most \(r\) is not topologically closed for \(d \geq 3\) [cite: 4, 19]. 

The **border rank** of a tensor \(X\) is the smallest number of rank-1 tensors needed to approximate \(X\) arbitrarily well [cite: 19]. Mathematically, it is the minimum \(r\) such that \(X\) lies in the closure of the set of rank-\(r\) tensors. It is possible to construct sequences of tensors of rank \(\leq r\) that converge to a tensor of rank strictly greater than \(r\) [cite: 3]. For example, there exist \(2 \times 2 \times 2\) tensors of rank 3 that can be approximated arbitrarily well with rank \(\leq 2\) tensors [cite: 19].

This lack of upper semicontinuity leads to the failure of the Eckart-Young theorem for higher-order tensors. The Eckart-Young theorem guarantees that the best rank-\(r\) approximation of a matrix exists and can be found via truncated SVD. For tensors of order 3 or higher, best low-rank approximations may simply fail to exist because the optimization problem is ill-posed [cite: 3, 4].

### 3.2 Folding Rank and Generic Rank
Diaz and Lutoborski (2017) explored the folding of a tensor into a matrix of multihomogeneous polynomials, defining a new concept called **folding rank** [cite: 5]. They also formalized the notion of a *folding generic tensor*, which implies that all determinantal schemes associated with the tensor behave generically [cite: 5]. Their main theorem states that for "small" 3-tensors, any folding generic tensor has a generic rank, though the reverse does not always hold [cite: 5].

### 3.3 Slice Rank, Geometric Rank, and Analytic Rank
Recently, to overcome the dependency of analytic rank on finite fields, Kopparty, Moshkovitz, and Zu introduced the **geometric rank** [cite: 21]. For a 3-tensor \(T\) with dimensions \(n_1 \times n_2 \times n_3\), we can view the tensor as a collection of matrix slices \(M_k\). They define an algebraic variety in \(\mathbb{F}^{n_1} \times \mathbb{F}^{n_2}\) consisting of all vectors \((x, y)\) such that \(x^T M_k y = 0\) for every \(k\). The geometric rank of \(T\) is defined as the codimension of this variety [cite: 21]. This notion extends beautifully to fields of characteristic zero, bridging gaps left by analytic and slice ranks [cite: 21].

---

## 4. The Discrete Fourier Transform (DFT) in Multilinear Algebra

The Discrete Fourier Transform (DFT) is traditionally viewed as an operation on vectors. However, when applied to multidimensional grids, its multilinear nature is fully realized.

### 4.1 The 1D DFT Matrix
The 1D DFT operates on a vector of length \(N\). It is represented by the Fourier matrix \(W_N\), where the entries are complex exponentials:
\[ (W_N)_{k,n} = \exp\left(-i \frac{2\pi}{N} kn\right) = \omega_N^{kn} \]
where \(\omega_N\) is the primitive \(N\)-th root of unity [cite: 23]. The matrix \(W_N\) is symmetric and, up to a scaling factor of \(1/\sqrt{N}\), unitary [cite: 24]. As a linear map, the 1D DFT has a matrix rank of exactly \(N\), as its columns are linearly independent.

### 4.2 The Multidimensional DFT (MDFT)
For a multidimensional discrete signal represented as an order-\(P\) tensor \(X \in \mathbb{C}^{N_1 \times N_2 \times \dots \times N_P}\), the multidimensional DFT (MDFT) is a function of \(P\) discrete variables [cite: 5, 15]. It is defined mathematically by the complex array:
\[ y_{k_1, k_2, \dots, k_P} = \sum_{n_1=0}^{N_1-1} \dots \sum_{n_P=0}^{N_P-1} X_{n_1, \dots, n_P} \exp\left(-j 2\pi \sum_{i=1}^P \frac{n_i k_i}{N_i}\right) \]
[cite: 15].

When calculating the MDFT, straightforward strategies like considering tensor product grids fail due to the excessive amount of used data [cite: 24]. However, algorithms like the Fast Fourier Transform (FFT) exploit the separable nature of the complex exponentials [cite: 24]. The MDFT can be expressed via the \(n\)-mode product of the input tensor \(X\) with the 1D DFT matrices along each mode:
\[ Y = X \times_1 W_{N_1} \times_2 W_{N_2} \dots \times_P W_{N_P} \]
[cite: 20].

### 4.3 The MDFT Operator as a Tensor
If we view the MDFT as a linear operator \(\mathcal{F}\) acting on the vector space of order-\(d\) tensors, \(\mathcal{F}\) itself can be mapped into a tensor of order \(2d\). Because \(\mathcal{F}\) is formed by the Kronecker product of \(d\) full-rank matrices, the tensor rank of the operator \(\mathcal{F}\) is simply the product of the ranks of the 1D matrices, which is \(\prod N_i\). However, defining the MDFT as an order-\(2d\) operator is often unwieldy. 

To create a more geometrically and algebraically interesting object, researchers have defined specific tensors generated purely by the multidimensional roots of unity.

---

## 5. The Collapsed Discrete Fourier Transform (CDFT) Tensor

A profound investigation into the tensor properties of the DFT was published by Steven P. Diaz and Adam Lutoborski in their 2017 paper, *Discrete Fourier Transform Tensors and Their Ranks* [cite: 5, 6]. 

### 5.1 Definition of the CDFT
Diaz and Lutoborski introduced a tensor generalization of the matrix discrete Fourier transform, which they named the **Collapsed DFT (CDFT) tensor** [cite: 5, 6]. Crucially, they note that the CDFT tensor is fundamentally different from the standard even-order DFT tensor, except in the base case when the order is exactly two (which reduces to the standard DFT matrix) [cite: 5, 6].

The CDFT acting on lower-order tensors maps them into a lower-dimensional space—essentially "collapsing" them [cite: 25]. In standard matrix algebra, such a mapping corresponds to the presence of zero eigenvalues [cite: 25].

### 5.2 Ranks of the CDFT Tensor
Determining the rank of the CDFT tensor represents a significant theoretical milestone. Diaz and Lutoborski studied the action of the CDFT tensor and achieved the following main results:
1. **Monotonicity of Rank:** They established the monotonicity of the tensor rank with respect to its order [cite: 5, 6].
2. **Bounds on Rank:** They provided strict upper and lower bounds on the rank of these generalized tensors [cite: 5, 6].
3. **Exact Computation for Prime Dimensions:** The crowning achievement of their work was the exact computation of the rank of third-order (\(d=3\)) CDFT tensors specifically when the dimension of the underlying vector space is a prime number [cite: 5, 6].

Given the NP-hardness of tensor rank computation [cite: 1], finding exact closed-form ranks for a specific class of tensors is highly non-trivial. The algebraic structure of the CDFT (comprising roots of unity) allows for polynomial simplifications that yield exact bounds over prime fields.

### 5.3 Eigenvalues and Orthogonal Decomposability
Generalizing the concept of eigenvalues and eigenvectors from matrices to higher-order tensors is a recent development in multilinear algebra (pioneered by Lim and Qi) [cite: 25]. Diaz and Lutoborski generalized the theory of eigenvalues and eigenvectors for symmetric tensors to the tensor products of symmetric tensors, applying this directly to the DFT [cite: 5, 25]. 

For the CDFT tensor, they successfully computed its symmetric rank in certain cases [cite: 5, 25, 26]. A symmetric tensor is orthogonally decomposable (odeco) if it can be written as a sum of symmetric outer products of mutually orthogonal vectors. Diaz and Lutoborski mathematically proved that the CDFT is *not* orthogonally decomposable [cite: 5, 25, 26]. Furthermore, for the CDFT tensor with order \(n \geq 3\) and \(N=2\), they explicitly extracted all eigenvalues and eigenvectors—a remarkably rare outcome for an arbitrary order tensor arising from practical applications [cite: 25].

---

## 6. Bilinear Complexity and Tensor Rank

The study of the tensor rank of the multidimensional DFT is not merely an abstract geometric exercise; it directly intersects with the theory of **bilinear complexity**.

### 6.1 Strassen's Framework
In the late 1960s, Volker Strassen showed that the multiplication of two matrices could be achieved in fewer than \(O(n^3)\) operations by viewing the multiplication as a bilinear map [cite: 7]. A simple but central observation in algebraic complexity theory is that every bilinear operation is characterized by a 3-tensor [cite: 8]. 

If \(U, V,\) and \(W\) are vector spaces, and \(\beta: U \times V \to W\) is a bilinear map, we can associate \(\beta\) with a structure tensor \(T_\beta \in U^* \otimes V^* \otimes W\). The tensor rank of \(T_\beta\) quantifies the bilinear complexity of the operation—specifically, the minimum number of non-scalar variable-by-variable multiplications required to evaluate the map [cite: 7, 8]. The equation is expressed as:
\[ \text{rank}(T_\beta) = \min \left\{ r : \beta(u, v) = \sum_{i=1}^r \phi_i(u)\psi_i(v)w_i \right\} \]
where \(\phi_i \in U^*\), \(\psi_i \in V^*\), and \(w_i \in W\) [cite: 7].

### 6.2 The Bilinear Complexity of the DFT
When considering the bilinear complexity of the DFT itself, the answer is trivially bounded. The standard evaluation of a DFT involves multiplying an input variable vector \(x\) by a matrix of fixed constants (the roots of unity \(W_N\)). Because multiplications by constants are considered scalar multiplications and are "free" in the strict bilinear complexity model, the bilinear complexity of computing the DFT or FFT is formally zero [cite: 7]. As noted by researchers, one can often bound the number of additions and scalar multiplications strictly in terms of variable multiplications [cite: 7].

However, the MDFT plays a paramount role in minimizing the bilinear complexity of *other* operations, most notably the convolution of multidimensional arrays and polynomial multiplication.

### 6.3 Convolution, Polynomial Multiplication, and the NTT
The DFT defines an isomorphism between a polynomial ring \(\mathbb{K}[x]/(x^N - 1)\) and the vector space \(\mathbb{K}^N\) [cite: 27]. This isomorphism provides the foundation for the most efficient algorithms for multiplying polynomials over fields. 

Because the MDFT avoids the direct \(O(N^2)\) variable multiplications of convolution by transforming the problem into a pointwise multiplication (which requires exactly \(N\) multiplications), it vastly reduces tensor rank constraints. In fields of finite characteristic (e.g., cryptography), the Number Theoretic Transform (NTT) acts as the DFT over a finite field [cite: 9]. The module in NTT must be large enough so the finite field contains special roots of unity [cite: 9]. 

To compute convolutions of dimension \(d\), multidimensional NTTs are deployed. Recent advances combine the "Preprocess-then-NTT" technique with Karatsuba multiplication to relax modulus constraints while keeping asymptotic time complexity lower than classical algorithms [cite: 9]. Bounds on the tensor rank of multiplication in finite field extensions rely heavily on these additive analogues of the DFT and multidimensional DFT approaches [cite: 28, 29].

### 6.4 The Cohn-Umans Method
A potent technique developed for studying the bilinear complexity of matrix multiplication is the Cohn-Umans method, which embeds matrices into appropriate group algebras [cite: 5, 8]. This method leverages the representation theory of finite groups, specifically utilizing the multidimensional Fourier transform over finite groups to block-diagonalize the group algebra.

Researchers have generalized the Cohn-Umans method for bilinear operations other than unstructured matrix multiplication [cite: 5, 8]. By viewing structured matrices (Toeplitz, Hankel, circulant) through the lens of group algebras and DFT tensor rank, optimal algorithms with the theoretical minimum bilinear complexity have been discovered [cite: 8].

---

## 7. Algorithms and Software Frameworks

The theoretical insights regarding the tensor rank of MDFT directly inform the architecture of highly optimized computational software.

### 7.1 SPIRAL Framework
The SPIRAL framework is designed to automatically map computational kernels (like the MDFT) to highly efficient code across varying parallel platforms [cite: 30]. SPIRAL abstracts away tensor rank entirely, converting all higher-rank objects to vectors [cite: 31]. 

SPIRAL uses a mathematical formalism called Operator Language (OL) to cast the synthesis of kernels as a tightly constrained optimization problem, solved via a multi-stage rewriting system [cite: 30, 31]. By transforming formulas like the MDFT via breakdown rules (e.g., data flow transformations and DFT transposition properties), SPIRAL synthesizes an exact algorithmic rule tree that is provably equivalent to the original tensor specification [cite: 31].

### 7.2 FFTW and Hardware Adaptation
The "Fastest Fourier Transform in the West" (FFTW) is a widely used C subroutine library for computing the DFT in one or more dimensions [cite: 32]. It is not tuned to a fixed machine; instead, it uses a *planner* to adapt algorithms to the hardware [cite: 32]. The input to the planner is a multi-dimensional loop of multi-dimensional DFTs. It applies Cooley-Tukey decompositions, essentially treating an MDFT as nested tensor factorizations, optimizing the path of execution to minimize memory bottlenecks and CPU cache misses [cite: 32].

### 7.3 Advanced Krylov Methods and the t-Product
In computational mathematics, extensions of traditional Krylov subspace methods to third-order tensors rely on specialized algebraic constructs. Unlike flattening the tensor (which destroys the multidimensional structure), researchers utilize the *t-product* [cite: 22]. The t-product relies on circular convolutions computed efficiently via the 1D FFT along the tube fibers of the tensor. This allows third-order tensors to be multiplied analogously to matrices, maintaining a strict multilinear framework [cite: 22].

---

## 8. Applications in Science and Engineering

The tensor structure of the multidimensional DFT is not isolated to theoretical computer science; it has broad applications across various disciplines.

### 8.1 Quantum Chemistry and Micromagnetic Interactions
While DFT typically means Density Functional Theory in chemistry, computing long-range micromagnetic interactions requires the Discrete Fourier Transform. Researchers utilize FFT-based Kronecker product approximations for structured tensors of order \(d\) [cite: 3]. Because tensor rank is not upper semi-continuous [cite: 3], approximating a physical tensor of order \(> 2\) is unstable. Thus, specific ALS (Alternating Least Squares) algorithms like the Higher-Order Orthogonal Iteration (HOOI) are employed alongside the MDFT to accelerate computations to quasi-linear complexity in the number of collocation points [cite: 3].

### 8.2 Computer Vision and Optical Flow
In image processing, multidimensional signals (spatiotemporal data) are routinely represented as tensors. The MDFT is utilized to extract distributed spatial structure and constant motion [cite: 23]. The tensor rank of local motion types explicitly defines the structural complexity of the spatiotemporal neighborhood (e.g., a constant brightness with no apparent motion corresponds to rank 0, while a distributed spatiotemporal structure without coherent motion corresponds to rank 3) [cite: 23]. 

### 8.3 Differential Privacy and Multimodal Fusion
In data privacy, mechanisms have traditionally focused on unimodal data. Recent advances propose local differential privacy (LDP) frameworks for *multimodal* representation learning [cite: 5]. By fusing different modalities into a joint representation subspace via multidimensional discrete signals, the MDFT is applied to provide robust binary encoding and Fourier-based noise injection [cite: 5]. The tensor properties defined by Diaz and Lutoborski ensure that high-dimensional fusion tensors can be manipulated efficiently without compromising data utility [cite: 5].

---

## 9. Conclusion and Open Problems

The study of the "T#87" prompt—unpacked as the tensor rank of the multidimensional Discrete Fourier Transform for \(d \geq 3\)—reveals a rich intersection of computational complexity, multilinear algebra, and applied algorithm design. 

The intractability of computing general tensor rank underscores the significance of specific, structured breakthroughs, such as Diaz and Lutoborski's explicit calculations for the Collapsed DFT (CDFT) tensor over prime dimensions [cite: 5, 6]. The failure of the Eckart-Young theorem and the divergence between topological limit bounds (border rank) and exact CP tensor rank continue to pose challenges [cite: 3, 19]. 

**Open Problems in the Field:**
1. **Exact Rank for Arbitrary Dimensions:** While the rank of the third-order CDFT tensor is known for prime dimensions [cite: 5, 6], deriving exact formulas for arbitrary dimensions \(d > 3\) and non-prime underlying spaces remains a deeply open problem.
2. **The Matrix Multiplication Exponent (\(\omega\)):** Utilizing multidimensional DFT structures via the Cohn-Umans group-theoretic embedding to push the matrix multiplication exponent closer to 2 remains highly active [cite: 8, 33]. Current "galactic algorithms" leverage block decompositions and sophisticated MDFTs, but translating asymptotic gains into practical, real-world computation is elusive [cite: 33].
3. **Analytic vs. Geometric Rank in Characteristic Zero:** Further exploring the pointwise equivalence of the Koltchinskii-Pollard entropy to combinatorial dimensions and geometric rank properties for generic tensors [cite: 21, 34] will provide better bounds on tensor identifiability.

In summary, the multidimensional DFT is much more than a fast algorithm for signal processing; when viewed as an algebraic tensor, it is a key that unlocks fundamental limitations and capabilities of multiplicative complexity in higher-order geometries.

**Sources:**
1. [rochester.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERcAQT02Nz40NLsY31oMVpkIFDlMesBUFGwSanzgAJ-v6k5mMau_azr_D4ePIYNFgoXZNy5Ob6WGDqBVXP6Nbv-wqJkxcmtnQE3ZsK95O5JzmCX7zKaI8zQxE5j5pSsvmCZinDD40urIONX1aGTtgn3pUpEw==)
2. [kth.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHu0S166BbH5mRDI7WgxMZu3DF2RiFdBI4NJL6RxtfeswRxx2q82uwGhRnfoLfJEDi2jj8vO_GfWrZsKP4uGpE0Wa8asJXsHVVLG0D2r4UYi8PoBDbEmSonrYAPgnzw-xZtpA==)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcFEuULWeOkz1hMD3dTLzzjdLoHF3FQZG6-y_VCleCvoi-GrAeJNMpmA4xFPlnBM30a5apF3M98UjYMtYc0T1M7jechB8IJsQBw1fmcPOzHwL-qyQK3o3FZFIyyRT-tFhnWXMjtqdGO7AfXFmmOosctpKDbEASayFV6_Qa1LYUyk8jCMyRcV3RGQe1vws1MiuRlHe6gL2w8z2kzSyYNAQa9pQRseCXQcgm4l_M98dQdbAvP7vHB-nrKyP9)
4. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFicRmmMWNmE6UyhLoFM-ClDeoTXB-MPtt4eR5kr592yivszK_H5yTvRL817mOG9c0d4fvi8aGgf-LcqoiOtxLm9Bm72OS1c1tp6fAAinjUPpI75qZtgCHfqKmM7TLQtntH)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHK-F0wWE8-sc7qp0GP4naiLM0IbQJKg1pJVC9wuVfuyiIG-RUc4H339i8BYIzw7BFhfsCXPCfatpJnFTM0tN80wT46lgJjyvA3ulKE-aNTJcuxZe9fwIOK3BBAhNPjXj0y9IL59uQNK-XzRptLvfAXhcwYY9lKT72rShJSmZgzrCE_ai1VhRK2FmyNNOnY_pRQF5L4GioQNnxt)
6. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE03FWcEQjkkFs6kO66rFXtmBrF2H6zYceVXyaDh-iuR8BzJt0zVihHCyom-xCaO64Do7G6T6Kh2EDqhWP-dsj45HL9D7OQMRNMXnQx4dgVOI7PkaHFYkI7J8cGbCOWmtS1Cw==)
7. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGC_IqLO1bi2TM00vPiyNzXW1a9M1-4nYbyiXIiMZOZRS12zN2WmThJGZ0khhT653CaikxrO7HqTTQD6GMXT8P5L5vVTODE1zI8kn2YLJQ9-WtkhVDTBTo8QQb9h5wlZyWn4Gwz4T9jSaeuu48=)
8. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmn9vd59CpQ-p2AMJjW2Pb_OrFZ2kDpybcTY5VLL3IigCSLenJesCBTytBri2qL6OCSaig94t2OCRPMA6c8fBVgpQbsof9YDSWzpf0XTnDOm81QWkLH6Ja-UzvTt1lYp15OTEGMFeXNsk=)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGucuRwt53KC7tA78_BfjbP011JkukZB_mSHhmSNknZ89ML6AAFyM-kuQKBiKtjEl08KhcO6tFOPyvU3ra0QRijLUFPmI_fgAV8k9m1GG_NQsbWBNcBKEmu3DwflmmBCMo-8sIhmGDKwWlPPONoZ_xdSxW95ZMiB9KS5cpXIhQ1ASZszQUddHbCd2t0iITyrFRcT7Iyt3gZr_5YYWf_JBqTSqOo-0jl6Gw=)
10. [tensorflow.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQDlSJoKgXi54KEfTchc8se8NOIk4ChDkAfOSFdAICd_Md9PxM23_cl1REJkaVx6n5IhDcMKHUn1epbFUGtrtshbSTYMU2sDIo-X0jIQ6Nup_TYW9GSuGpOFR-mUnzo7KFmvFkDNEu6BSukwynrZZSr5c=)
11. [kaggle.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgb-uI3VLECpftAfoiW0i7IASyXu1HMxi2tAjhXUlJ_PBuqXRRSU-cz-SjtweYyjUfDG06tLySYLix3WmgnPEc-fdmnz1_Vm8iRwkZ6gd0PBqSYBirvHfA45lPDYyuEPZlMvENh6FpdbHuHu1l00G1wzHYxkHRtRdjxy8=)
12. [acs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwwC2N_vdwPf-EHPRrQuMy1LNo8LXrDShrXAfqJpOGuo7cNb3H4mIaFuG1t3O2lIydeLI4KHW1s7fiMNmKOkE_OIo48TdyswYuoE8tH2P_KOq5hg1R7htjFxYxyg1twXPupe_-wSc=)
13. [aip.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEih7b-eVwfiaXFJq4sUdFRDgDb6VF3RBiDPiE5AfC1fJb_SoKJW4vooC-95uDkREIBTChS6lrQlowOAvdSofpKXYpVVX7ASXb5dZizrOHtEFibMvCM_EDbLji--oyABWf7coZEdD6jsoeGE80fsfxLJnecqQSlvXZvn0dU1hY-osL2GNs5bvcR-Qr6btF14-LtsrUBsoM8HpEHOPGJ)
14. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzeU1Zw1SYpy_v-0dwuE1pjyxLRuMdFlFatxi-jQpWIAf4faiuaJ37ODME2Y_hZJqEdyMP7rnsHul8MQeSIHXod7cFWyIvTDrn-n-xF5-D30VXRgrn32QgNMG92oczoSrf1-g1-w7jrINU)
15. [ufc.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsPS7k6CLB4oHonALJLmKpI_5-e5EiNQOgFmpUJw5t6j2temM2PI0vfLTKaHEsaxnTVrKT3vDM8ZTVpkm03Gq4FgHvg0BaQlSkN8ZkkRQOC5KpSJFyOyBnbIqvgrZxuypygRJFdsMOqkxjD7CfKUoBNhLygjgJ_HjpGII2pfkeYQ==)
16. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHi5cOaF9oNHU894ugcLGkL9wLo-RmiMzwWTAfBDz2LZ8pqoYf3nIcEos-8yB6dnnUoeRtKBidot48felcsQYt9FZ3gH4chO5zVh6tWlE1NZULuADEtpmaoE1QGUJTvL1XyP6KyEHJKhkhsFv4uBzEI)
17. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiNaaAqwKUFTQ3ENaHxe54J793wMLCe1sqU5o23YR1XawjBC-yOTyBrtozrsqmkYdBJXcePT6dEEFndMg8ERjEO8C1qTxfK80JNFARywHhdz1MKg3V0hxQ7NaXzSY3UPapQvMN_46D3gUYqwq4fg==)
18. [wolfram.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGP8Fqwz1CRa4nmPRWW7be0RsS6BH8SczKVeVsin5-fMGA6wnRD7L1GwzQtkkrsOBQbJhMlbKCVYEeKNLR6ZLDaq_m8G7qaa5xGwTw-A85_uNH9TWSzMNiI0r0rTal8uEmbDA==)
19. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0wMPkVm9zkbO2O1O3KYq6dS2Fzzvza3Fdk1DhWUZy02q4lbAJsbh9T-TYVHdPdtcfn-m3-XISvr5titOt2MYZjZL7iOkGy_nhNW0VaqZ4Cia6wDu0eB2GXhzRUQISLBmpzqM881HeJ22GrFLz0w==)
20. [uzh.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8O4IUWziAsmuCgMPyTgePifobBEqBxMrbjdmQYa_ccjf45WP_WZEcqHAgSCGN-I4CKeu8s6EF03pByo8dN8zER-wJjsofB-S3TgjSVtv_9IppL4fg7I_QeD_1MQuvIsMmNmuxzt59_rUSPO7uiui9sTHT86Pp5JyCaQ6Z_8XgyBvnKshl_AkXhDc=)
21. [discreteanalysisjournal.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjB25kqiCYvkvNQJm6u_kwUw1MGClOADh-hw9vFn9Uno0sFJtCOj_tTthYACVtnUivzozzcJ-gDXUYhaHQujZzMSnGFEL6OejPe3-P9yEtTt_prtvgyddIX3TFwI5hrKJU4_6plcZmr0vRjP2OEi6n7E3YvPDKCDu7Od06K2CTl2AYzSuneP3HYth5IQj0Vbk_3CPA0ppynjLZzBXz48LEMQNnvvc=)
22. [tufts.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDrIVR4lgtrW4cDOPzj4eNVWQZEhOIBs6J6Q1Of311C0m8ucn4gFZL48guYk_piJTlok2aL-1JjrihnDpS-lCnr4jENG8b5iNLzzG6vINHD4lm47bjDedxK7q8Ce6jDu7eEaEsuOM8ri2WwolNQ5JStIMkuF4PLA==)
23. [academia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCZmck1TsLn69GiboUhNZO5gn2-sCD04RVFYHlf9u--K1vwOA7eqW1Ao7YOeZ0WyO7cjnPrF6sAi_r3KT4-WzcWtV9WMwNa7UMbEvLXHme3Oq17FVvXuEKbYJmD2absnJZiO8gz1x25gbbKQhvFuy8p7af6xs_Q-4TqDBaBXTUdG9o-uJFxRdKsGMyieUeWvJLxn9N3oz2LL6Ow15HfA==)
24. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFi24KF_SJEdnOTdMlAfcPifSfNjy1xzjAr5AJunJ2jo7h0meOkvtcLUv4NhPjwvg-yfbwL1MTBk8wGsu2H6jNhFneafpnGHbS5mnhG9tOa8mgi4IQ=)
25. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpoMNH8GIVmuSY7pRRzD0ZHQaTl8Sedz7xnj5x98LS-mWGVlKXlBBMzDeC5rj7rRBZ2PJ0zxwlB5x70-ywS19TxGf4Zmqn0l58opeX0PAzyZpHNZqKidI3NJhUHkK_JcuiZFi93YqRGpTNdvCu3UXO71YixMxl)
26. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0eXfwEf5DUPPNO1UYa4-aFeB1Ro6-UNg0tokBPITVztX-LMMTItRO4a1D748khf96yMbiRKZlJJvhZ3HbUnw72YaPEVbk_2__jpWI_RdLvlLQBd5QVoEgHHOSMjGQAD6KZjsu4R_VjpQK6V876cXNVBB1uDTL)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHx28_v7lBFkt9c6YHklqAf78tPD_-13LJ83LR2t4iUesGiAlHAp7xJNCwt0n0-0skmRvaufzb1kB9OYaaKKVAp2MVsIAg6q27HfrNaTI3gUFoLmRwC60EozjsLbcGCs-U-L9jZMsIvcJcuJvuSEhjONCDVubJH)
28. [cyberleninka.ru](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkZ1x8R5vGGbxcdBlVValzbIlbbJSjY6lZxIOW9lpQX0uG2YcyS6r63lNUaHYLWlwJ8uJs28RVl-odzBEkXZjHv5FAkTfFkTX1xoSFrJn_K-E_up1orv-VtO6bGgHqCDBq)
29. [texmacs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzbUqNOPhRfJt1Nw_oxYFZiYdr5Es0tHu7ws3B0wnHKYvGeiz4xUsSyYUibKr53o8xK0RhOq4KgiG2ZubuuoWY6vmG6zAhINFnrMYOXG911fhwBrU2Z9GM7Euu39DSTZbpw7c=)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHphSTB3FPVKe0PNXPlkmDm42pDep2fjrq8o5cAxTxmVBWCLm7l3mVOoquAOpklvEetynhoL0fdHc78d1MUdnBUAN-7d5XQsVmOQ8NU8C7y7UihD-k9PWrM0WJIQPHPnmBKX2W-MeXUZXbgC_iC3kMP_0DTpI-sJe41YrMw97ZSxxda_zJOJZtuLot-1cCE)
31. [cmu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIPoS3sTtL66Rebh2BaTmKE6JSPmnWyhfmIE0mnCKDYux70t3dBFoevflMp-j9Ow9eXi2v0tmJO39kMPc9T6DwqPBkxUeBEC_FT9jORMtvc66aUow9wPPDNg6mNIcZqgpj3oI_s2zWljXMOQ5Yv8_lKv_TXSizVkiXR5o=)
32. [fftw.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG39oHzuWfiquQcijD0E3J8XS5gJdrWTmsWxT1fm_R4HK6YD0TpLjOluFYXfiwuRSli843Dfp6kPRm6YGEjAR-eGgYoO8rSlquWA6alPk_KonAN_E-tR2_LQg==)
33. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyl4DrdyK-tKmsb4qFT3byBnn5cXat_EtExlM6vywLZrU8--8Mjs2n3s0BcEptk2jINX-L_73m5rCaXKJ7RScAfdG08IseHwENiLG6dq4oCLV1-_ZSGXJyq7ZhbHpomlc1fIk=)
34. [uci.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwTKox84nxsJkM_ENO5emSuGEeluyp3t472ho7hyBNOZQZrPd_mAcySNGkW4rmQzpsQWJuiMlTLDYpTszeEyTt2oTiwpVritIivW6DHt4RA85HhzjAgXQZWv8kfdv8uTYBJT5M3sW5A0cxnHTpBeg=)

