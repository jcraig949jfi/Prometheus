# T#37 Typical rank classification over R vs C (multiple typical ranks)

**Pythia queue id:** 82
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdIQXNQYXA3ZUU4V3VfUFVQc2F1TmlBWRIXSEFzUGFwN2VFOFd1X1BVUHNhdU5pQVk
**Elapsed:** 309s
**Completed at:** 2026-05-21T13:44:50.256385+00:00

---

# Comprehensive Classification of Typical Tensor Ranks Over \(\mathbb{R}\) versus \(\mathbb{C}\): Phenomenologies of Multiple Typical Ranks

### Key Points
*   Research suggests that the fundamental topological differences between the real (\(\mathbb{R}\)) and complex (\(\mathbb{C}\)) fields lead to divergent behaviors in tensor rank classification.
*   It is well-established that over the complex field \(\mathbb{C}\), any specific tensor format possesses a single "generic rank" due to the properties of the Zariski topology.
*   Conversely, over the real field \(\mathbb{R}\), evidence indicates that certain tensor dimensions exhibit "multiple typical ranks," meaning randomly generated real tensors may fall into different rank classes with positive probability.
*   Theoretical frameworks often rely on the Hurwitz-Radon function and nonsingular bilinear maps to determine exactly which tensor formats exhibit this plurality of typical ranks over \(\mathbb{R}\).
*   The notation "T#37" in literature likely refers either to specific algorithmic test cases for cyclic symmetric rank-3 tensors or alludes to the ongoing bounds regarding the matrix multiplication exponent (\(\omega \leq 2.37\dots\)).
*   The phenomenon of multiple typical ranks appears to extend beyond standard tensor rank to include symmetric rank, typical subrank, and low-rank matrix completion paradigms.

### Introduction for the Layperson
**What is a Tensor?**
In mathematics and data science, a tensor can be thought of as a multi-dimensional array of numbers. While a single number is a scalar, a list of numbers is a vector (1D), and a grid of numbers is a matrix (2D), a tensor extends this concept into three or more dimensions (like a cube of numbers). Tensors are incredibly useful for representing complex, multi-way data relationships, such as color images (height \(\times\) width \(\times\) color channels) or human motion over time.

**What is Tensor Rank?**
To make large amounts of data manageable, scientists try to break complex tensors down into a sum of simpler, "building block" tensors. The "rank" of a tensor is simply the minimum number of these basic building blocks needed to perfectly reconstruct the original data. In matrices, the rank is easy to find. In 3D tensors and beyond, finding the rank is mathematically difficult and can change depending on whether you are working with real numbers (numbers on a standard number line) or complex numbers (numbers that include the imaginary unit \(i\)).

**The Mystery of "Typical" Ranks**
If you generate a random matrix, its rank is highly predictable; it almost always takes the maximum possible value. This is called the "generic" rank. However, if you randomly generate a 3D tensor using real numbers, a strange phenomenon occurs: it might have a rank of 5 some of the time, and a rank of 6 at other times, with both outcomes being entirely normal. This is known as having "multiple typical ranks." Understanding which shapes of tensors have one predictable rank versus multiple possible ranks is an active and fascinating area of algebraic geometry and data science.

---

## 1. Introduction to Tensor Rank and Decompositions

A tensor is a multidimensional or \(N\)-way array of elements, generalizing the concepts of vectors (order-1 tensors) and matrices (order-2 tensors) to higher dimensions [cite: 1]. The order of a tensor, also known as its modes or ways, corresponds to the number of dimensions it possesses [cite: 1]. In applied mathematics, multilinear algebra, and data mining, decomposing these high-dimensional arrays is crucial for extracting latent features from complex datasets. 

The most common generalization of the matrix Singular Value Decomposition (SVD) to higher-order tensors is the Canonical Polyadic Decomposition (CPD) [cite: 2, 3]. Originally proposed by Frank Lauren Hitchcock in 1927, the CPD expresses an \(N\)-way tensor \(\mathbf{T} \in \mathbb{F}^{I_1 \times I_2 \times \cdots \times I_N}\) as a minimal sum of rank-1 tensors [cite: 2, 3]. A rank-1 tensor is defined as the outer product of \(N\) non-zero vectors [cite: 1, 4]. For a third-order tensor, this decomposition is formally written as:
\[ \mathbf{T} = \sum_{r=1}^{R} \mathbf{a}_r \circ \mathbf{b}_r \circ \mathbf{c}_r \]
where \(\circ\) denotes the outer product, and \(\mathbf{a}_r, \mathbf{b}_r, \mathbf{c}_r\) are vectors [cite: 3, 5]. 

The **tensor rank**, denoted as \(\text{rank}(\mathbf{T})\), is defined as the smallest integer \(R\) for which such an exact decomposition exists [cite: 2, 5]. For a general tensor of format \(N_1 \times \cdots \times N_d\), the rank serves as an index of the mathematical complexity of the tensor [cite: 6, 7]. 

However, unlike matrices where the rank is easily computable (e.g., via SVD or Gaussian elimination) and bounded by \(\min(I_1, I_2)\), calculating the rank of an order-3 or higher tensor is generally an NP-hard problem [cite: 8]. Furthermore, a critical divergence arises when evaluating tensor rank depending on the underlying scalar field—specifically, whether the tensor spaces are defined over the real number field (\(\mathbb{R}\)) or the complex number field (\(\mathbb{C}\)) [cite: 6]. Over \(\mathbb{C}\), tensors exhibit a single "generic rank," whereas over \(\mathbb{R}\), they may exhibit "multiple typical ranks" [cite: 5, 9].

## 2. Generic Rank over the Complex Field (\(\mathbb{C}\))

To understand the concept of typical ranks over \(\mathbb{R}\), one must first establish the baseline behavior of tensor ranks over algebraically closed fields like \(\mathbb{C}\). 

### 2.1 The Algebraic Geometry Perspective
Over the complex numbers, the study of tensor rank is deeply intertwined with algebraic geometry. The space of all rank-1 tensors in the tensor product \(V_1 \otimes \cdots \otimes V_d\) corresponds to the **Segre variety**, denoted as \(\Sigma\) [cite: 2, 5]. The Segre variety is a projective algebraic variety formed by the embedding of the product of projective spaces \(\mathbb{P}(V_1) \times \cdots \times \mathbb{P}(V_d)\) into the projective space of the tensor product \(\mathbb{P}(V_1 \otimes \cdots \otimes V_d)\) [cite: 2, 10].

Tensors of rank at most \(r\) are intimately related to the \(r\)-th **secant variety** of the Segre variety, denoted as \(\sigma_r(\Sigma)\) [cite: 2, 11]. The secant variety is the Zariski closure of the union of all linear spaces spanned by \(r\) points on the Segre variety.

### 2.2 Uniqueness of the Generic Rank
If the base field is \(\mathbb{C}\), the set of tensors of a given format with rank at most \(r\) contains a non-empty Zariski open set if and only if its Zariski closure encompasses the entire tensor space \(\mathbb{C}^{I_1 \times \cdots \times I_N}\) [cite: 3, 7]. By Chevalley's Theorem, in an algebraically closed field, there exists exactly one rank that almost all tensors will take. 

This unique integer is called the **generic rank**, denoted as \(\text{grank}_{\mathbb{C}}(I_1, \ldots, I_N)\) [cite: 3, 7]. The generic rank is defined as the least rank \(r\) such that the closure in the Zariski topology of the set of tensors of rank at most \(r\) is the entire space [cite: 3]. Consequently, over \(\mathbb{C}\), a randomly generated tensor (with entries drawn from a continuous probability distribution) will have a rank equal to the generic rank with probability 1 [cite: 5, 8]. The set of tensors possessing lower ranks forms an algebraic set of Lebesgue measure zero [cite: 2]. 

A common lower bound for the generic rank over \(\mathbb{C}\) can be approximated by counting dimensions (the expected rank), resulting in \( r \geq \lceil \frac{\prod n_i}{\sum n_i + 1} \rceil \) (or \( \lceil \frac{nmp}{n+m+p-2} \rceil \) in a projective space context for order-3 tensors) [cite: 2, 11].

## 3. Typical Ranks over the Real Field (\(\mathbb{R}\))

While the complex field benefits from the algebraic closure that forces a single generic rank, the real number field \(\mathbb{R}\) behaves differently due to its topological and geometric constraints (such as positivity constraints and the non-algebraically closed structure) [cite: 2]. 

### 3.1 Euclidean Topology and Semi-Algebraic Sets
Over the real numbers, the analysis shifts from the Zariski topology to the Euclidean topology. De Silva and Lim (2008) extensively studied the space of real tensors, demonstrating that for a positive integer \(r\), the set of real tensors with rank \(r\) forms a **semi-algebraic set** [cite: 12]. This proof relies heavily on the Tarski-Seidenberg principle, which states that projections of semi-algebraic sets remain semi-algebraic [cite: 12].

Because the set of tensors of rank \(r\) is semi-algebraic, it can have a non-empty interior in the Euclidean topology without necessarily being dense in the entire space. 

### 3.2 Definition of Typical Rank
A number \(r\) is defined as a **typical rank** of real tensors of format \(N_1 \times \cdots \times N_d\) if the subset of tensors of that rank has a strictly positive Lebesgue measure (i.e., it contains a non-empty Euclidean open set) [cite: 7, 12]. In simpler terms, an integer \(r\) is a typical rank if a real tensor generated with independent and identically distributed (i.i.d.) standard Gaussian entries has rank \(r\) with a strictly positive probability (\(P\{\text{rank}(\mathbf{T}) = r\} > 0\)) [cite: 5, 13].

### 3.3 The Phenomenon of Multiple Typical Ranks
The most striking consequence of this topological framework is that over \(\mathbb{R}\), the set of tensors of rank at most \(r\) only forms an open set of positive measure, leaving "room" in the tensor space for Euclidean-open sets of tensors with strictly higher ranks [cite: 3]. Therefore, there can be **multiple typical ranks** for a single tensor format over the reals [cite: 2, 5]. 

The smallest typical rank over \(\mathbb{R}\) is called the generic rank over \(\mathbb{R}\), and it always identically coincides with the generic rank over \(\mathbb{C}\) [cite: 3, 6]. However, real tensor formats can exhibit typical ranks that are larger than the complex generic rank [cite: 3, 8].

## 4. Case Study: T#37, Cyclic Symmetric Tensors, and the Matrix Multiplication Exponent

Before delving into the broader classifications of tensor formats, it is imperative to address the specific specific query string "T#37" and its contextual appearances in tensor literature. 

### 4.1 Cyclic Symmetric Rank 3 Tensors
In algebraic complexity and tensor approximation literature, specific tensors are often indexed or tagged for algorithmic benchmarking. One notable instance refers to a cyclic symmetric rank 3 tensor defined as:
\[ \mathbf{T} = b \otimes c \otimes b + c \otimes b \otimes b + b \otimes b \otimes c \]
This tensor can be approximated by a rank 2 Border Rank Decomposition (BRD) using an infinitesimal parameter \(\varepsilon\) [cite: 14]. In literature characterizing border rank limits and decompositions, test cases are often enumerated, and "T = 37" serves as an identifier for a specific set of border rank decompositions evaluated at different precision limits [cite: 14]. For instance, snippet data shows approximations yielding \(f(U) = 3 \cdot 10^{-9}\) at a matrix norm limit, demonstrating the numerical instability and the divergence between tensor rank and border rank (where border rank \(\leq\) tensor rank) [cite: 14].

### 4.2 The Matrix Multiplication Exponent (\(\omega\))
A more globally recognized "37" in tensor literature is the upper bound of the matrix multiplication exponent, \(\omega\). The matrix multiplication exponent is defined as the infimum over all real numbers \(\beta\) such that any two \(n \times n\) matrices can be multiplied using \(\mathcal{O}(n^\beta)\) algebraic operations [cite: 15]. Trivially, \(2 \leq \omega \leq 3\).

Determining the exact value of \(\omega\) is a central problem in algebraic complexity theory [cite: 15]. The asymptotic complexity is directly governed by the tensor rank (and border rank) of the matrix multiplication tensor \(\langle 2, 2, 2 \rangle\) [cite: 15]. While Strassen published the first non-trivial bound (\(\omega \leq \log_2 7\)) using the Strassen tensor (which has a rank and border rank of 7), subsequent laser methods by Coppersmith and Winograd pushed this bound down to the state-of-the-art \(\omega \leq 2.37\dots\) [cite: 2, 15]. 

The study of typical and generic tensor ranks heavily informs these bounds, as the subrank \(Q(\mathbf{T})\) and asymptotic rank of irreversible tensors (tensors where the asymptotic rank strictly exceeds the subrank) provide barriers to further lowering the \(2.37\) threshold using current laser methods [cite: 15].

## 5. Typical Ranks of Small Order-3 Tensors

Extensive research has mapped the exact typical ranks for order-3 tensors (\(m \times n \times p\)) over the real numbers. The existence of single versus multiple typical ranks depends tightly on the specific integer dimensions.

### 5.1 The \(2 \times 2 \times 2\) Tensor
The smallest higher-order tensor format, \(2 \times 2 \times 2\), is the classic example of multiple typical ranks over \(\mathbb{R}\). Over the complex field, the generic rank of a \(2 \times 2 \times 2\) tensor is 2 [cite: 2, 8]. The secant variety \(\sigma_2\) fills the 7-dimensional projective space [cite: 2].

However, Kruskal (1989) famously demonstrated that over the real field, both 2 and 3 are typical ranks for \(2 \times 2 \times 2\) tensors [cite: 1, 9]. If one populates a \(2 \times 2 \times 2\) tensor with independent random real numbers, there is a positive probability that the resulting tensor will have rank 2, and a positive probability it will have rank 3 [cite: 8]. The generic (minimal typical) rank is 2, while the maximum typical rank is 3.

### 5.2 Tall Tensors
To systematize the classification, researchers Ten Berge, Sumi, Miyazaki, and Sakata introduced bounds based on the relative sizes of the dimensions. Let the format be \(m \times n \times p\) with \(2 \leq m \leq n\). 

A tensor is defined as a **"tall tensor"** if the largest dimension \(p\) satisfies:
\[ p > (m - 1)n \]
For tall tensors, Ten Berge (2000) and later Sakata et al. proved that there is **only one typical rank** over \(\mathbb{R}\), which is exactly equal to \(p\) [cite: 7]. Consequently, the typical rank set is \(\text{trank}_{\mathbb{R}}(m, n, p) = \{p\}\) [cite: 7]. In these formats, the tensor space does not leave room for multiple typical ranks.

### 5.3 Semi-Tall Tensors
A tensor is classified as a **"semi-tall tensor"** if:
\[ (m - 1)(n - 1) + 1 \leq p \leq (m - 1)n \]
This specific dimensional window is where the phenomenon of multiple typical ranks becomes highly complex and dependent on algebraic topology [cite: 7]. Sumi, Miyazaki, and Sakata have shown that for semi-tall tensors, the typical ranks are heavily influenced by the existence of nonsingular bilinear maps [cite: 7, 16].

Specifically, if \((m - 1)(n - 1) + 1 \leq p \leq (m - 1)n\), the typical ranks are contained in the set \(\{p, p + 1\}\), with \(p\) always being a typical rank [cite: 5, 17]. 

## 6. Nonsingular Bilinear Maps and the Hurwitz-Radon Function

The definitive criterion for the existence of multiple typical ranks in semi-tall tensors revolves around the concept of nonsingular bilinear maps [cite: 5, 17]. 

### 6.1 The Nonsingular Bilinear Map Condition
Let \(u = mn - p\). Sumi, Miyazaki, and Sakata (2017) proved that multiple typical ranks occur in the format \(m \times n \times p\) (where \((m-1)(n-1)+1 < p \leq mn\)) **if and only if** there exists a nonsingular bilinear map:
\[ \phi: \mathbb{R}^m \times \mathbb{R}^n \to \mathbb{R}^{mn-p} \]
[cite: 5, 17]. 
A bilinear map \(\phi(x, y)\) is deemed nonsingular if \(\phi(x, y) = 0\) strictly implies that either the vector \(x = 0\) or the vector \(y = 0\) [cite: 5, 17]. 

Geometrically, this condition is equivalent to the existence of a linear space \(L\) in the Grassmannian \(G(p, mn)\) such that \(L\) has an empty intersection with the Segre variety \(\Sigma_{m,n}\) (\(L \cap \Sigma_{m,n} = \emptyset\)) [cite: 5, 17]. If such a space exists, any linear space in a neighborhood of \(L\) also avoids intersecting the Segre variety, which leaves a positive volume of tensors having the higher rank \(p+1\) [cite: 5].

### 6.2 The Hurwitz-Radon Function
To determine whether such a nonsingular bilinear map exists for a given dimension, researchers utilize the **Hurwitz-Radon function**. 
The Hurwitz-Radon function \(\rho(n)\) is defined algebraically. For any positive integer \(n\), write it in the form:
\[ n = (2a + 1)2^{b + 4c} \]
where \(a, b, c\) are nonnegative integers and \(0 \leq b < 4\). The Hurwitz-Radon number is then given by:
\[ \rho(n) = 2^b + 8c \]
[cite: 12, 18].

Focusing on the specific boundary case where \(p = (m - 1)n\), Sumi, Miyazaki, and Sakata demonstrated a beautiful correspondence:
*   If \(m \leq \rho(n)\), the set of \(m \times n \times (m - 1)n\) tensors over \(\mathbb{R}\) possesses **two typical ranks**: \((m - 1)n\) and \((m - 1)n + 1\) [cite: 12].
*   Conversely, if \(m > \rho(n)\), the set of \(m \times n \times (m - 1)n\) tensors has **only one typical rank**, which is \((m - 1)n\) [cite: 12].

This theorem provides an exact, computable algebraic condition resolving the typical rank plurality for the \(p = (m-1)n\) boundary [cite: 12]. For the other boundary, \(p = (m-1)(n-1)+1\), multiple typical ranks can occur even if no nonsingular bilinear map exists [cite: 7].

## 7. Geometric Probabilities and the \(3 \times 3 \times 5\) Tensor

Recent advancements by Breiding, Eggleston, and Rosan (2024) have approached the typical rank problem using probabilistic geometry and intersection theory [cite: 5, 17]. 

For many choices of \((m, n, p)\), there is only one typical rank. For instance, the \(3 \times 3 \times 3\) and \(3 \times 3 \times 4\) tensors possess only one typical rank, which is 5 [cite: 5, 17]. 

However, the real \(3 \times 3 \times 5\) tensor exhibits multiple typical ranks: 5 and 6 [cite: 13, 17]. Breiding et al. linked the rank probabilities of a \(3 \times 3 \times 5\) tensor generated with i.i.d. Gaussian entries directly to the geometry of cubic surfaces [cite: 5, 13]. Specifically, the probability that a Gaussian \(3 \times 3 \times 5\) tensor has rank 5 is equivalent to the probability that a random cubic surface in the real projective space \(\mathbb{R}\mathrm{P}^3\) contains exactly 27 **real** lines [cite: 13]. 

By expressing the probabilities of these typical ranks in terms of the number of intersection points of a random linear space with the Segre variety, they derived an expected number of real lines on such a surface (yielding bounds between 11 and 15 expected real lines) [cite: 5]. This demonstrates the profound connection between the statistical distribution of real tensor ranks and classical enumerative algebraic geometry. Furthermore, by Lucas' theorem, if the degree of the complex Segre variety (given by \(\binom{m+n-2}{m-1}\)) is odd, the format \(m \times n \times p\) for \(p > (m-1)(n-1)+1\) guarantees only one typical rank [cite: 5].

## 8. Contiguity of Typical Ranks

A natural question arises: if a tensor format has a minimal typical rank \(r_{\min}\) and a maximal typical rank \(r_{\max}\), are all the integer ranks between them also typical?

The answer is yes. It has been proven that any rank between the smallest typical rank and the largest typical rank is also a typical rank [cite: 9, 19]. This is known as the **contiguity of typical ranks**. 

The proof relies on the topological properties of the rank function. Sets of tensors with a given typical rank are semi-algebraic. The essential algebraic mechanism states that given a tensor \(\mathbf{T}\), adding a rank-one tensor \(\mathbf{v}\) increases or decreases its rank by at most one:
\[ |\text{rank}(\mathbf{T} + \mathbf{v}) - \text{rank}(\mathbf{T})| \leq 1 \]
[cite: 9]. By moving continuously in the tensor space and iteratively adding rank-one perturbations, the rank transitions smoothly (in integer steps), ensuring that no integer gap can exist between the minimal and maximal typical ranks over the real field [cite: 9, 20].

## 9. Typical Symmetric Ranks (Waring Rank)

The study of typical ranks extends beyond standard tensors (Segre varieties) to symmetric tensors, which correspond to the Veronese variety [cite: 20, 21]. A symmetric tensor is unchanged under any permutation of its indices, effectively acting as a higher-order generalization of a symmetric matrix [cite: 4]. 

Decomposing a symmetric tensor into a sum of symmetric rank-1 tensors (i.e., \(\mathbf{a} \circ \mathbf{a} \circ \cdots \circ \mathbf{a}\)) is related to decomposing a homogeneous polynomial (quantic) of degree \(d\) in \(n\) variables into a sum of \(d\)-th powers of linear forms [cite: 4, 20]. The minimal number of such terms is called the **symmetric rank** or Waring rank [cite: 4].

Just like standard rank, the symmetric rank can differ between \(\mathbb{R}\) and \(\mathbb{C}\) [cite: 4]. Over the reals, symmetric tensors also exhibit multiple typical ranks [cite: 20]. 
*   **Ternary Cubics (3 variables, degree 3):** There is a unique typical symmetric rank of 4 [cite: 19, 20]. 
*   **Quaternary Cubics (4 variables, degree 3):** These exhibit multiple typical symmetric ranks, specifically 5 and 6 [cite: 19, 20]. 
*   **Ternary Quartics (3 variables, degree 4):** The typical ranks are 6 and 7, and it is bounded such that all typical ranks lie between 6 and 8 [cite: 19, 20].
*   **Ternary Quintics (3 variables, degree 5):** The typical ranks are known to lie between 7 and 13 [cite: 19, 20].

The generic symmetric rank sequence (in terms of set inclusion) increases up to the complex generic symmetric rank, then the sets decrease in volume thereafter [cite: 4]. The classic Alexander-Hirschowitz theorem classifies the generic symmetric rank for all dimensions and orders over \(\mathbb{C}\), but over \(\mathbb{R}\), characterizing the maximum typical symmetric rank remains an active area of real algebraic geometry [cite: 4].

## 10. Extensions: Subrank, Matrix Completion, and ND-Rank

The plurality of typical behavior over the reals permeates other tensor-related complexity measures and restricted factorizations.

### 10.1 Typical Subranks
The **subrank** of a tensor \(\mathbf{T}\), denoted \(Q(\mathbf{T})\), is dually related to the rank. It is the largest integer \(r\) such that there exist linear maps allowing the tensor to restrict to an \(r \times r \times r\) diagonal tensor [cite: 9, 15]. Subrank is pivotal in algebraic complexity theory.

Just as with tensor rank, while algebraically closed fields have a single generic subrank, over \(\mathbb{R}\), there can be multiple typical subranks [cite: 9]. 
*   For a \(2 \times 2 \times 2\) real tensor, the typical subranks are 1 and 2 [cite: 9].
*   For \(2 \times n \times p\) tensors (\(n \geq 2, p > 2\)), the unique typical subrank is 2 [cite: 9].
*   For \(3 \times 3 \times 3\) and \(3 \times 3 \times 4\) tensors, the unique typical subrank is 2 [cite: 9].

Contiguity holds for typical subranks as well. If \(r\) and \(s\) are typical subranks with \(r \leq s\), all integers between \(r\) and \(s\) are also typical subranks [cite: 9]. This relies on the lemma that adding a rank-one tensor to \(\mathbf{T}\) decreases its subrank by at most 1 (\(Q(\mathbf{T} + \mathbf{v}) \geq Q(\mathbf{T}) - 1\)) [cite: 9].

### 10.2 Typical Ranks in Low-Rank Matrix Completion
While standard matrices (order-2 tensors) have a unique typical rank over both \(\mathbb{R}\) and \(\mathbb{C}\) (which is \(\min(n, m)\)), the problem of **matrix completion** reintroduces multiple typical ranks [cite: 11, 22]. Matrix completion aims to complete an \(n \times m\) matrix from a generic set of specified entries [cite: 11, 22]. 

Over \(\mathbb{C}\), a matrix with a given entry pattern completes to a unique generic completion rank [cite: 22]. Over \(\mathbb{R}\), however, certain specified entry patterns yield multiple typical completion ranks [cite: 22]. Dressler and Krone (2025) studied unspecified sets defined by bipartite circulant graphs, finding that families like the circulant graph \(G(4,1)\) are the smallest examples exhibiting multiple typical completion ranks over \(\mathbb{R}\) [cite: 22]. 

### 10.3 Nondecreasing (ND) Rank and Nonnegative Rank
When constraints are added to the vectors forming the rank-1 outer products, typical ranks shift. 
**Nonnegative Rank:** In many data analysis applications (e.g., chemometrics), tensor factorizations are required to be nonnegative [cite: 6, 23]. Sumi, Miyazaki, and Sakata (2018) proved that an integer \(r\) is a typical nonnegative rank for a format \(N_1 \times \cdots \times N_d\) if and only if it lies between the complex generic rank and the maximum nonnegative rank (which is \(\prod_{i=1}^{d-1} N_i\)) [cite: 24]. 
**Nondecreasing (ND) Rank:** A tensor has an ND rank of \(r\) if it can be represented as a sum of \(r\) outer products of vectors, with each vector satisfying a monotonicity constraint (defined by a partially ordered set or poset) [cite: 23, 25]. Finding an ND factorization often equates to finding a nonnegative rank factorization of a transformed tensor [cite: 23, 25]. Any rank between the minimum typical real rank and the maximum ND rank is a typical ND rank [cite: 23].

## 11. Practical Implications and Ill-Posedness

The theoretical divergence between real and complex tensor ranks, particularly the presence of multiple typical ranks over \(\mathbb{R}\), has profound implications for numerical computing and data science.

### 11.1 The Ill-Posedness of Low-Rank Approximations
One of the most critical applications involving tensors is finding the best low-rank approximation (e.g., via Alternating Least Squares) [cite: 21, 23]. For a given tensor \(\mathbf{T}\) and a target rank \(r\), the goal is to find a rank-\(r\) tensor \(\mathbf{B}\) that minimizes the Euclidean distance \(\|\mathbf{T} - \mathbf{B}\|\) [cite: 21].

In matrix theory (order 2), the Eckart-Young theorem guarantees that a best rank-\(r\) approximation always exists and can be found via truncated SVD [cite: 1, 26]. For higher-order tensors, the set of tensors of rank at most \(r\) is **not topologically closed** in the Euclidean space (unless \(r=1\) or \(r\) is the maximum possible rank) [cite: 4]. 

Because the set is not closed, sequences of tensors of rank \(r\) can converge to a limit tensor that has a strictly higher rank [cite: 4]. This creates the phenomenon of **border rank** [cite: 2, 3]. As shown by De Silva and Lim (2008), for any order \(k \geq 3\) and dimensions \(d_i \geq 2\), there exist tensors of rank \(s\) that have no best rank-\(r\) approximation for some \(r < s\) [cite: 3, 26]. In numerical optimization, this manifests as "diverging components," where the norms of the rank-1 factors \(\mathbf{a}_i \circ \mathbf{b}_i \circ \mathbf{c}_i\) tend to infinity while their sum remains bounded [cite: 3]. 

The existence of multiple typical ranks exacerbates this issue. If a data tensor generated from a continuous distribution falls into an open set corresponding to a higher typical rank, attempting to approximate it with the lowest generic rank may plunge the algorithm into an ill-posed convergence failure [cite: 3, 11]. 

### 11.2 Applied Tensor Regressions and Medical Imaging
Despite these theoretical challenges, tensor ranks are extensively utilized. In medical imaging, the reconstruction of symmetric second-rank tensor fields (such as those used in tensor tomography and MRI) requires filtering back-projection algorithms [cite: 27]. These physical tensors are parameterized into solenoidal and irrotational components [cite: 27]. 

Furthermore, in industrial applications predicting human motion via Tensor-on-Tensor regression, real-time prediction relies on flattening tensors into matrices or utilizing constrained typical ranks to ensure that continuous real-world Cartesian/angular data avoids the divergence traps of higher-order multilinear spaces [cite: 28]. 

## 12. Conclusion

The rank of a higher-order tensor is not a monolithic property but a fluid metric heavily dependent on the algebraic rules of its base field. The generic rank classification over the complex field \(\mathbb{C}\) provides a clean, unique integer value driven by the closed nature of the Zariski topology. However, when operating over the real field \(\mathbb{R}\)—the domain of physical data and continuous signal processing—the Euclidean topology fragments the tensor space into multiple open sets of positive volume, birthing the phenomenon of multiple typical ranks.

From the foundational discovery of dual typical ranks in the \(2 \times 2 \times 2\) tensor by Kruskal to the precise algebraic boundaries defined by the Hurwitz-Radon function in semi-tall tensors by Sumi, Miyazaki, and Sakata, the classification of typical real ranks represents a triumph of real algebraic geometry. As researchers continue to probe formats like the \(3 \times 3 \times 5\) tensor using the geometric probabilities of cubic surfaces, and bounds on the matrix multiplication exponent remain tethered to the complexities of border and subranks, the understanding of real tensor geometries remains a vibrant and critical frontier in both pure mathematics and computational complexity theory.

**Sources:**
1. [kolda.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhYMKpObcISBlF90ZUMAhtVJPoKRJWcWnCsQB9fwdS4PEVp5XHv8kSKSTYG2RVaNN-2hbGa_TOTUGKr5hGMKOXaGxRZ1RTWOryLZEVSl6pNcgpSao5mXEYrNs7LsbXOrltNh-oZN2k)
2. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxl2elo9t3M5LSCwwrEupwttW9JQEW4rt4L9FKwCk1EM0-3fk_F4u1YeqS-AkyABO2c2V9BuYPnbX8y6GWMiz3IN2vDxXRIMPOau8yXMiB3RJipe0DCvI9JzWj7c0UHe2V54zOcsS8_8Nw)
3. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGlfYz9rdenUfazTeaszKG7wwkUXsYxf6I57eCoLEVBEEx00zUelrchfJv454xSPdtLnMXjfkLnBTI3hs1m6fzFDsl8c7AYBKOI9Bm9sa9-OKkrjTUVzNuWVWJcyFjvb4oY8s2zWskXv77BWzU=)
4. [grenoble-inp.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHISXps8q_0O5lP8fKRfps-cMLlMH74ifjnfWvTsuvOFYMYsumGO4LRaD8XhG34b0ivsyqT24M5pkeuYSeQOlozFBgTCFnU2SKr3VQCNXhk2deYnQCdL4eC-0bHaXsJBqimtnLTidLv0gV0LtyE6ggP1YvGYnB-r8PyL2ULYTwn94Sosda5g4aC)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-M-q0eXgplVuPw2SksnQFg3bLLwqweBqbjjmDC8KSk5yCrezQqhwVxXFSHc7tVanFL6udQVKSxKNfGpclQ-K7Utlux9wTL8XeXNJyZ3kE7X73u-dF)
6. [ethernet.edu.et](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFElhj0Mq2MgDxSmzS1GHbadQjTA8tFF4TPr--2WFrFoMylZKWuXNf94C43eW0fnmYAWC13B9X4XYUtZeE8DHxtp73lD7QZu8FveM7aIl98GvGMilx2WrW8l_Nu5amI4Dhlx8cXIGb8zXihxOmhE_De06KX)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgUPemDLQFXxsClWNwrv8oyz4CfzsAH3Fe3KtTPP1izq0XyJGyG17VLSFIVbZxHf9IHr7PAplZ90a-cs918y-fLJhwL4QzyAVU9aq3pboidxp0F-98)
8. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEg9Ud5HE71yBR_CmAVAzz_dz8-T2eDjK7YSV8YR6-3yuld89VUkYvJRtbAsWcRj9aU317w4KTfNi4gekndM2FBxuzm0mAjZ6-G0jR86lIbfLE3sP5f9ejbI9AorNwqSqPIKxTkODIdKxcY5i53sDwZ0cjixkkecRxQCsMO01fMyzSBKB4--IqmqqIPpPsE8jhQyNwrkM3A57hSn4p39-ZGJkG9ZY_vQEdJBsBEg3_8)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUcPMVJHzoGrDEJb_lho-SZjgpod60sBLKDZ6xC2URkUp61QXl-BK14Q3drzwIFgQW-PWkQmvZpGWZgf5jtEB2pKwhfIgn-0hzTZ_smnbsyzXt4bdk)
10. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpHPLdAwqZHiZTumzDdD9iyCewpUygfF7TLQETsj_zDBN53Y5xET86JGJqExQVQNpSiW4KSJOBRmd5TpHFpqiTnnu61uSiKvLAPMBgH_8ERL2mjXHzfIgMkODGMT5vKWjCt6S3hWoqjwSMNZFSgeuj)
11. [uga.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFU5PIf1m7gOYO1vwJECCuqQaJbw5osX3qIdzV6VQJoPvJvvTqLsZbAcTw9u-s6ykguTBdT6BV79hg3_l2whK2Ia1PEFRfUoHZFCnurENLzAn0ucmUgaJJyRDNntLVwVKoceFFjfgvef4skW4KhE4alkmQBy66dBn6e7r0XFR1tXbNyHbZ7KQ2GUJFGiTJeW7pOu1XWgRuOw==)
12. [kyushu-u.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWzrlRRJq7nRAbv2SYVoKD_gP8yBcAb0SSx3Q6i0a64YjIQI2XPFFYUVracq3UEDgx0UWL5ahT5mUha88RihHcqjEfJlN14LzahUIL75AXCJHhDhjy8PhblDTqg6iyZ_PXv0DEE04MLzixHiPvvXPMX0-k75wBztT1cmzGZQO__MICO6rParb4)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6gSmNNLV_pGot6UkNIixiJLVztzImxeNLWmoA_oQAhI1vHtKpOVd7AHDck3Wyl49ncptOoU7jM62zmffnpmkN6FT4-_XUJCBRaiuSFjIEbng8ttYPVXb9gOPyZHZR_B1xTJtPp62U-P4-uTV0IQ8zv_taIHmLM_u33FqUtx1fW2SoxcwoBht2FrAPuU6Qoh4-NyM=)
14. [kuleuven.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpMzQq6n-cELNzKC0RUYqB52ugS6Ege7FbxpaXEXW3_LizyvBHEa5_ibphQqhD2CScz5n2Wsqn7LRz0REvDDE-Cw35vltBrjH7OVsVt9ddi-DjRSkNlReTg7zq9KYDcyHgBFlAxMvwrNSu8N3QJ85NK0hlcmK3HyA3sjxiuAQ=)
15. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEu7Pp8TSoVQ11xBSy7NFuWO2cQIYoSqb0RDpSRVXJvqMbMv3KeJV_Nqr6RTBa3Pq9Ct2BIf7ADsJ0ZeyXDrrjMRjtEO2ZmF4qWr2Znz-qmRRfu1X9GZ3lbifKCAuI27LJFMpNjYOj0rDDNY4G0DkEyobnMPr4qjR1HH9a0U6MJVopoVoQENT4L)
16. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZIHdhaAbq7iORNfQNmZmtiEOotAOc_LQ3tCrzHogLh7yjsiXmm6gMC7Kc7jtIPrQzhYbyZ0Zxwzn-Y4X_-0gRtl53LI55SiRZ7lYCRtIXCxwqwhqgkWtmhoyJbHurGqrk7UKQAUfVmWrGA6YltPd7xywP_emB)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAGQHaTZjl8tphzg3v9kJ0CsyVOs9Z-aegynCX1yudpyOBls_SXo-mRLzZV83TuMAINVCZuyb5RbKUJHKF5f4LQekibnr8rSYICYOf90ySYKK7AsZV_6oa)
18. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFy_3VbNH-zzhpMCwfc3dx25dZwXrZYLJXBgrNkDNt-gIkD569xREToE20rFhhWxkNFHOaTXWfEzt3gwlgo7thfX1JAoOL9tuhdyziSSWJAtLssQUErPYPnrEGO_rz4B7vL0CclEX1-hVZyCTn8TmphwUf4MI=)
19. [unitn.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-0hC6h6yfr9PNQTQsIjjf0OEUXJCyrI1dBMUt-6JO5DcuGHTEWV6iqcW4gwQUbYS6RdSJLkf7sTAdUunfieFppXMXOiS-_rvSBGE92NNRKLnVwaJOKhP6S3Jkntc8q4hEh801QC6EsJ8Rj-va2RDz9SDB0O9zCiaGxU_FZmP06-LItC3xAbk=)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvOQKKHKLqyD2L5DsK1AYM_DK47X5LpioDC0CsiXbOV5_FVm_-_amcLj0QpKImAW0_i4dZmK5Q2IhKlWuVw0w35084vm1KQDExDEYU7TnAWUI7rqhtUO1MBlH_FcKVy1eRudMWo4IDvCVAyyGD_EdR_K85Vk1w5pcP5xX8lQ==)
21. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7e50Vdwjmin1oGYxVFLq4YmMZgkWxMcwKhxejRIQen1_oNHaWWGWHT3_pBOBQAlOGOnZxRBo5caiBLNhjtQkdaXSYBCv7rn1xTEHwekqJntOKZI-bh5nGdiSXinEvTgXO3jI3fmmRW77f6jqH)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCAqd9-O9AussqfjF3ovK7FzkTh06ThoVu_FLQEl0ibE08UTwkqbZAnkyfN2tARQBU7nszU6TWFPwOCfn-YfjpVwElMmSe6Wj-4ImHA9L6uHisSzhsLFdK)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELhgaZmoUW03iFW5TlMjfBjrb3V_sAHb-orfcA5_AcBX779LunfDSyxVwNxA2Osa-uIypzMNQ69ijWmmjsfIRPdwL1Lycujr18f5kvIKWfPqyAKsVD)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTVwXwbyZMa3MefZXT44piFA9w38GWoqm-3DhdgHxlEWI_0oxGXpdd53ae-qSE97a3iSgUg2naBwpVJ5HWdqgFbmzZYAgEbz9noZLLRNad24w7tbN7)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDec7zg3ZSOdc9XzRVJfwLvd8Rxub_s4jt_Fgx4UM0mId_ZrpSbEYTH53VFx-X6hWKcDI4PAazcsWA8Hs45qd1G0XsULnTKgwWrhfmqY-X7qUUb0UL9Lgx)
26. [cornell.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSdbhiS5ezk3wvJnKYTviP0xnseq9IdIPkFb9oOMP18G16aHUcHs6u-yEBE9NoF1g8AfQyX5TRMXUy6G8vnQN_qNuHqJL36po1SR7xe4sZ3MvQ-KWMEXw2vLVZL-gjE3h7Ld30kksjPGM26P1fV5yern0cYKAYBGKt1wyKnapdMMVXaxmiUG2f7XJ4)
27. [escholarship.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbXhP3hj2aorCalzFgwoAvkftofgh00RFYShDcjlLwwj0-JGb-bIF6-3fRM8dsgqP2oxjbEzl7xuLLENUmiwQqDFmvxB9eqZIObPCOx5xAgnSipdihMaACrin2ViExkAJouGncejgqsuOsyDDRt8U=)
28. [kaernten-digital.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGR92Xgw9dMan1LYNXJqp1DVBlBwwdEAY6KFXbxq949VOj4QdTayJUD6X0_0F1nQp2NVU2xur7YFfnzNmBMcELUdaxJF8na6JnS0bbMtZWh0fHcfyDkPtzfcuDZGkkuwGHo3c42qWX1mcQLa7MGeWcXxlrN8HyNkM9Vde-qsJ8WAmu2Nu9aTLNuroUYB6tD2YfVYRsLgi7rFHbEshru-rtmT717iiXQPL3WCnGwHjVINVWYKQ41nDBgbxRC0kCuza_pZjcXt9azPN7Sv_vckfZEQlL4DqZldNQiyUeWbZGKJ37TlOBIn5CRXABH9tWRzVqUSBHrX8f2Y4B5ORpznFmUTh4FGGnkPOqG9kjRVwzrKxPjX5cJkRSyT68p9-iD6os7arT6dtMBDMdyF05OONcMNNnkZm-eHJBrVe1prlhhRAPT3ZdgDwQqoH1gTksDjqvQzvNM8g==)

