# T#16 Subrank-rank duality / asymptotic spectrum (CVZ universal points)

**Pythia queue id:** 16
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdPbm9MYXVDOEl1QzBfdU1QMmJxcjBBSRIXT25vTGF1QzhJdUMwX3VNUDJicXIwQUk
**Elapsed:** 244s
**Completed at:** 2026-05-18T20:48:47.329468+00:00

---

# The Asymptotic Spectrum of Tensors, Subrank-Rank Duality, and CVZ Universal Points

**Key Points**
*   Research suggests that understanding the asymptotic complexity of tensors is one of the most central problems in algebraic complexity theory, directly dictating the theoretical limits of matrix multiplication algorithms.
*   It seems clear that the concepts of **tensor rank** (the minimal cost to compute a tensor) and **tensor subrank** (the maximum independent value a tensor can compute) are bound together by Volker Strassen's profound theory of the **asymptotic spectrum**.
*   Evidence indicates that Strassen's duality theorem recasts the seemingly intractable problems of asymptotic rank and subrank into an optimization problem over a topological space of homomorphisms called spectral points. 
*   The thirty-year open problem of discovering "universal" spectral points that apply to all complex tensors was decisively answered by Christandl, Vrana, and Zuiddam (CVZ) via the introduction of **quantum functionals**, utilizing deep connections to quantum information theory and entanglement polytopes.
*   Recent research continues to expand on this duality, exploring gaps in symmetric subrank, higher-order tensors, and utilizing these mathematical structures to resolve questions in additive combinatorics and communication capacity.

**Introduction for Laymen and Interdisciplinary Scholars**
At the heart of computer science lies the question of how efficiently we can perform basic operations, such as multiplying two matrices. While this sounds like a purely algorithmic problem, mathematicians translate it into a geometric and algebraic one by studying objects called "tensors." A tensor is essentially a multi-dimensional array of numbers. Just as a matrix has a "rank" that tells us how much fundamental information it contains, a tensor has parameters like **tensor rank** (how hard it is to construct) and **tensor subrank** (how much independent parallel work it can do). 

In the late 1980s, mathematician Volker Strassen realized that instead of studying a single tensor, we should study what happens when we combine them in massive, asymptotic limits. He proposed the **asymptotic spectrum**, a mathematical space that perfectly dualizes the complex behavior of tensors into a simpler, unified framework. However, a major piece of his theory was left blank: he could not find explicit mathematical rules (called "universal points") that governed all possible complex tensors. This puzzle remained unsolved for decades until 2018, when Matthias Christandl, Péter Vrana, and Jeroen Zuiddam (CVZ) used concepts from quantum physics—specifically, how quantum particles share entanglement—to construct the **quantum functionals**. This breakthrough bridged algebraic complexity theory and quantum mechanics, providing the long-sought universal points and offering a new lens through which to evaluate algorithmic barriers.

Due to the nature of the specific query tag `T#16`, which appears to correspond to a specific syllabus or lecture module tag in academic literature rather than a universally named mathematical constant, this report focuses purely on the exhaustive scientific elements enclosed in the query: the subrank-rank duality, the asymptotic spectrum, and the CVZ universal points. 

***

## 1. The Algebraic Complexity of Tensors

In theoretical computer science and algebraic complexity theory, tensors serve as the fundamental objects encoding the complexity of bilinear and multilinear maps. The most prominent example is the matrix multiplication tensor, whose complexity determines the exponent of matrix multiplication, \(\omega\) [cite: 1, 2]. To study the properties of these tensors, mathematicians employ various notions of rank that measure either the "cost" of constructing a tensor or the "value" a tensor inherently possesses.

### 1.1 Tensor Rank and Subrank
Given a field \( \mathbb{F} \), let \( V_1, \dots, V_k \) be finite-dimensional vector spaces. A tensor \( T \in V_1 \otimes \dots \otimes V_k \) can be thought of as a multi-dimensional array. For \( k = 2 \), this reduces to a standard matrix, where the properties of matrix rank are well understood: matrix rank is multiplicative under the Kronecker product, additive under the direct sum, normalized on identity matrices, and non-increasing under multiplication by matrices [cite: 2, 3].

For higher-order tensors (\( k \ge 3 \)), the situation becomes vastly more complex. 
*   **Tensor Rank (\(R(T)\))**: The rank of a tensor \( T \) is the smallest integer \( r \) such that \( T \) can be expressed as the sum of \( r \) rank-one tensors [cite: 4]. This parameter measures the minimal cost to compute the tensor, effectively defining the arithmetic complexity of the encoded problem [cite: 1]. We write \( T \le I_r \) to denote that \( T \) can be reduced from the diagonal identity tensor \( I_r \) of size \( r \) [cite: 5].
*   **Tensor Subrank (\(Q(T)\))**: Introduced by Strassen in 1987, the subrank of a tensor is a natural extension of matrix rank that measures the largest diagonal tensor that can be obtained by applying linear operations to the different indices (legs) of the tensor [cite: 6, 7]. The subrank \( Q(T) \) is the largest integer \( q \) such that \( I_q \le T \) [cite: 5, 8]. In essence, it measures the independent parallel scalar multiplications that can be reduced to \( T \) [cite: 5].

Thus, the tensor rank defines the "cost" while the subrank defines the "value" of the tensor [cite: 4]. Unlike the case for matrices where subrank and rank coincide, for \( k \ge 3 \), these values diverge significantly, and computing them is generally NP-hard [cite: 4].

### 1.2 Additional Tensor Parameters
Modern algebraic complexity theory frequently utilizes intermediate or barrier-specific notions of rank. Below is a summarized table of relevant tensor parameters that provide upper and lower bounds on subrank and rank.

| Parameter | Description | Relation to Subrank / Rank |
| :--- | :--- | :--- |
| **Rank** \(R(T)\) | Minimum number of rank-1 tensors needed to sum to \(T\). | \( Q(T) \le R(T) \) [cite: 1] |
| **Border Rank** \(\underline{R}(T)\) | Minimum rank of tensors arbitrarily close to \(T\). | \( \underline{Q}(T) \le \underline{R}(T) \le R(T) \) [cite: 4] |
| **Subrank** \(Q(T)\) | Maximum size of an identity tensor reducible to \(T\). | Lower bound on all other ranks [cite: 4] |
| **Slice Rank** | Minimum number of slices (tensor product of a vector and a lower-order tensor) summing to \(T\). | \( Q(T) \le \text{SliceRank}(T) \le R(T) \) [cite: 1] |
| **Geometric Rank** | Co-dimension of a specific algebraic variety associated with the tensor. | Upper bounds subrank, lower bounds slice rank [cite: 1] |
| **Partition Rank** | Generalization of slice rank allowing arbitrary partitions of tensor legs. | Upper bounds subrank, relates to slice rank [cite: 9, 10] |

To operationalize some of these bounds computationally, one can evaluate "flattening ranks." A \(k\)-tensor can be flattened into a matrix by grouping its axes. The matrix rank of any such flattening inherently bounds the properties of the tensor.

```python
import numpy as np

def flattening_rank(tensor, mode):
    """
    Computes the flattening rank of a 3-tensor along a specific mode.
    This provides the 'gauge points' which act as trivial spectral bounds.
    """
    shape = tensor.shape
    if mode == 0:
        flattened = tensor.reshape(shape, shape[cite: 11]*shape[cite: 6])
    elif mode == 1:
        flattened = np.moveaxis(tensor, 1, 0).reshape(shape[cite: 11], shape*shape[cite: 6])
    elif mode == 2:
        flattened = np.moveaxis(tensor, 2, 0).reshape(shape[cite: 6], shape*shape[cite: 11])
    else:
        raise ValueError("Mode must be 0, 1, or 2 for a 3-tensor.")
    
    return np.linalg.matrix_rank(flattened)

# Example: generic 3x3x3 tensor flattening rank
T = np.random.rand(3, 3, 3)
r_0 = flattening_rank(T, 0)
print(f"Flattening rank along mode 0: {r_0}") # Will output 3
```

***

## 2. Strassen's Theory of Asymptotic Spectra and Duality

In an attempt to systematically study the optimal algorithms for matrix multiplication, Volker Strassen published a sequence of seminal papers between 1986 and 1991 that shifted the perspective from finite tensors to asymptotic limits [cite: 9, 12]. Strassen formalized tensors as elements of a **preordered semiring**, denoted \( (\mathcal{R}, \le, \oplus, \otimes) \).

### 2.1 The Asymptotic Rank and Subrank
When studying matrix multiplication, we are rarely concerned with a single tensor. Instead, we want to know the rate of growth of the complexity as the tensor is tensored with itself repeatedly (the Kronecker power \( T^{\otimes n} \)).

Strassen defined the **asymptotic rank** \( \tilde{R}(T) \) and the **asymptotic subrank** \( \tilde{Q}(T) \) as follows [cite: 8]:
\[ \tilde{R}(T) = \inf_{n \ge 1} R(T^{\otimes n})^{1/n} \]
\[ \tilde{Q}(T) = \sup_{n \ge 1} Q(T^{\otimes n})^{1/n} \]

These regularizations extract the true asymptotic cost and value of a tensor. For the matrix multiplication tensor \( \langle 2, 2, 2 \rangle \), the asymptotic rank determines the exponent \( \omega \). 

### 2.2 The Asymptotic Spectrum
Strassen introduced the **asymptotic spectrum** \( X \), defined as the space of all maps \( \phi: \mathcal{R} \to \mathbb{R}_{\ge 0} \) that satisfy the following strict properties [cite: 2, 3, 13]:
1.  **Monotonicity**: If \( S \le T \), then \( \phi(S) \le \phi(T) \).
2.  **Normalization**: \( \phi(I_r) = r \) for diagonal tensors \( I_r \).
3.  **Additivity**: \( \phi(S \oplus T) = \phi(S) + \phi(T) \).
4.  **Multiplicativity**: \( \phi(S \otimes T) = \phi(S) \phi(T) \).

Such maps are called **spectral points** [cite: 13]. Strassen's monumental realization was that this space completely characterizes asymptotic restrictions between tensors. 

### 2.3 The Duality Theorem
The centerpiece of Strassen's theory is the **Duality Theorem**, which represents a vast generalization of linear programming duality and the Positivstellensatz [cite: 9, 12]. It translates the difficult structural problems of asymptotic rank and subrank into an optimization problem over the topological space of the asymptotic spectrum \( X \).

The theorem states that for any tensor \( T \):
\[ \tilde{Q}(T) = \min_{\phi \in X} \phi(T) \]
\[ \tilde{R}(T) = \max_{\phi \in X} \phi(T) \]
Furthermore, an asymptotic transformation \( S \lesssim T \) is possible if and only if \( \phi(S) \le \phi(T) \) for all \( \phi \in X \) [cite: 8, 14].

This elegant dual characterization means that to prove a lower bound on asymptotic rank, or an upper bound on asymptotic subrank (which acts as an obstruction to algorithmic reductions), one simply needs to find a single valid spectral point \( \phi \) [cite: 13, 14]. The difficulty, however, is that Strassen's proof was strictly nonconstructive; it utilized Zorn's lemma to prove the *existence* of the spectrum without offering explicit functions, outside of trivial flattening ranks (the so-called gauge points) [cite: 8, 14].

***

## 3. The Search for Universal Points and Support Functionals

To make the duality theorem practical, researchers needed explicit spectral points. In 1991, Strassen introduced a family of functions called **support functionals** \( \zeta^\theta \) [cite: 8, 14, 15]. 

### 3.1 Support Functionals and their Limits
The support functionals were constructed using the combinatorial properties of the support of a tensor. Strassen defined upper \( \zeta^\theta \) and lower \( \zeta_\theta \) support functionals. However, these functionals were only valid spectral points for a highly restricted, strict subfamily of tensors called **oblique tensors** (tensors whose support forms an antichain) [cite: 13, 15]. 

Because they did not apply generally, they could not be used as blanket obstructions for all complex tensors. A massive gap remained in algebraic complexity theory: finding explicitly computable **universal spectral points** that apply to the semiring of *all* tensors over a field [cite: 13, 14, 15]. This open problem persisted for nearly thirty years, stifling attempts to use duality to definitively bound the matrix multiplication exponent.

***

## 4. The CVZ Breakthrough: Quantum Functionals

In a landmark paper presented at STOC 2018, Matthias Christandl, Péter Vrana, and Jeroen Zuiddam (often abbreviated as **CVZ**) successfully constructed the first non-trivial family of universal spectral points over the complex numbers [cite: 13, 15, 16]. They achieved this by importing profound tools from quantum information theory and invariant theory, resulting in what are now known as **quantum functionals** [cite: 8, 14].

### 4.1 Quantum Marginals and Entanglement Polytopes
In quantum mechanics, a pure multipartite state is represented mathematically by a tensor. A central problem in quantum physics is the **quantum marginal problem** (also linked to the N-representability problem): given a set of single-particle reduced density matrices, is there a global pure quantum state that yields these marginals? [cite: 16, 17, 18, 19]. 

The attainable spectra of these reduced density matrices form highly structured geometric objects known as **entanglement polytopes** or **moment polytopes** [cite: 17, 19]. The moment polytopes of tensors capture invariant-theoretic data arising from multilinear actions of reductive groups on tensor spaces [cite: 17, 20]. Specifically, they define the asymptotic support of Kronecker coefficients in representation theory, linking continuous geometry to discrete combinatorial bounds [cite: 18]. 

### 4.2 Definition of the Quantum Functionals
CVZ realized that the framework governing the asymptotic limits of quantum marginals could map directly onto Strassen's abstract asymptotic spectrum [cite: 13, 16]. 

They defined a family of quantum functionals \( F_\theta \), parameterized by probability distributions (weightings) \( \theta \) on the indices of the tensor. For a complex tensor \( T \), the quantum functional utilizes the quantum entropy function and the partial trace [cite: 14]. By executing convex optimization over the corresponding entanglement polytope of the tensor, the quantum functional evaluates the "asymptotic entropic value" of the tensor.

Mathematically, CVZ proved that for all complex tensors, \( F_\theta \) satisfies all four of Strassen's strict axioms:
1.  **Monotone**: \( S \le T \implies F_\theta(S) \le F_\theta(T) \) [cite: 21].
2.  **Normalized**: \( F_\theta(I_n) = n \) [cite: 21].
3.  **Additive**: \( F_\theta(S \oplus T) = F_\theta(S) + F_\theta(T) \) [cite: 21].
4.  **Multiplicative**: \( F_\theta(S \otimes T) = F_\theta(S) F_\theta(T) \) [cite: 21].

Thus, the quantum functionals constitute the first explicit, non-trivial universal points in the asymptotic spectrum of complex tensors [cite: 13, 14]. 

### 4.3 Upper and Lower Quantum Functionals
In their formalism, CVZ actually introduced both an **upper quantum functional** and a **lower quantum functional** [cite: 22]. 
*   For tensors of order three (\( k = 3 \)), and more generally for weightings restricted to singletons on higher-order tensors, the upper and lower quantum functionals precisely coincide [cite: 22].
*   When they coincide, they yield a single, definitively rigid spectral point in Strassen's asymptotic spectrum [cite: 10, 22]. 

This allowed mathematicians, for the first time, to compute strict, verifiable upper bounds on the asymptotic subrank \( \tilde{Q}(T) \) of *any* complex tensor [cite: 14]. 

***

## 5. Connections to Other Rank Parameters

The discovery of the CVZ quantum functionals immediately yielded dividends by shedding light on an array of other tensor parameters that had been developed in the intervening decades. 

### 5.1 Slice Rank and Partition Rank
The **slice rank**, introduced by Terence Tao in 2016 as a tool to solve the cap set problem, is a parameter measuring the minimum number of "slices" required to reconstruct a tensor [cite: 1, 5, 23]. Slice rank inherently upper bounds the subrank.

CVZ demonstrated that their quantum functionals serve as strict asymptotic upper bounds on the slice rank and the related multi-slice rank [cite: 14, 15]. In fact, they proved a striking equivalency: the **asymptotic slice rank** of complex tensors is precisely characterized by the singleton quantum functionals [cite: 10, 22]. Specifically, the asymptotic slice rank is equal to the minimum of \( F_\theta(T) \) over all singleton weightings \( \theta \) [cite: 24].

Similarly, for the broader **partition rank** (which generalizes slice rank by permitting arbitrary partitions of the tensor legs), general weightings of the quantum functionals provide robust upper bounds on the asymptotic partition rank [cite: 22].

### 5.2 Geometric Rank and Analytic Rank
Other parameters like **analytic rank** (Gowers and Wolf, 2011) and **geometric rank** (Kopparty, Moshkovitz, Zuiddam, 2020) also intersect closely with this duality [cite: 1, 5, 23]. Geometric rank measures the codimension of a specific algebraic variety and proves to be an upper bound on subrank while remaining smaller than slice rank [cite: 1]. The structural rigidity provided by the CVZ universal points and Strassen's duality offers a unified framework where all these disparate combinatorial and algebraic parameters converge asymptotically [cite: 1].

***

## 6. Symmetric Tensors, Gaps, and Comon's Conjecture

While the CVZ quantum functionals apply to generic tensors, the study of symmetric tensors yields equally fascinating phenomena. A symmetric tensor \( f \in \text{Sym}^k(V) \) is invariant under the permutation of its indices [cite: 4].

### 6.1 Symmetric Subrank
Motivated by symmetric problems in combinatorics and complexity, Zuiddam and others formalized the **symmetric subrank** \( Q_s(f) \), which restricts the linear operations applied to the tensor to be identical across all legs [cite: 6, 7]. 

A longstanding open question in tensor theory was Comon's conjecture, which posits that the symmetric rank of a symmetric tensor is equal to its general rank. While the exact finite version of Comon's conjecture was proven false via counterexamples (such as those by Shitov) [cite: 7, 25], Zuiddam proved a remarkable theorem for the asymptotic subrank: for any symmetric tensor, the generic subrank and the symmetric subrank are **asymptotically equal** (\( \tilde{Q}_s(f) = \tilde{Q}(f) \)) [cite: 6, 7]. This proved the asymptotic subrank analogue of Comon's conjecture and forged a strong connection between the general and symmetric versions of Strassen's asymptotic duality theorem [cite: 6, 7].

### 6.2 Gaps in Subrank Growth
Another profound application of the asymptotic spectrum and subrank duality lies in establishing gaps in tensor growth rates. Strassen initially proved in 1988 that there is a strict gap in the subrank of a tensor when taking large powers: either the subrank of all powers is bounded by 1, or it grows exponentially as a power of a constant strictly larger than 1 [cite: 23, 25].

Recent work by Christandl, Gesmundo, and Zuiddam has vastly sharpened this. They precisely determined this gap constant for tensors of any order [cite: 23, 25]. Furthermore, for 3-tensors, they proved the existence of a *second* gap in possible growth rates [cite: 23]. They characterized this by examining whether a tensor's orbit closure contains specific highly structured tensors, such as the W-tensor (analogous to the W-state in quantum mechanics) [cite: 23, 25]. This expanded upon similar gaps proven for slice rank by Costa and Dalai in 2021 [cite: 23].

***

## 7. Recent Advancements: Higher-Order Tensors and Laminar Weightings

The behavior of the asymptotic spectrum for order \( k \ge 4 \) has remained a frontier of active research. While CVZ proved that upper and lower quantum functionals coincide for 3-tensors, establishing definitive spectral points, it was long an open question whether this coincidence held for higher-order tensors [cite: 22].

In an April 2026 preprint, Nieuwboer, Christandl, and colleagues demonstrated that for higher-order tensors, the upper and lower quantum functionals **do not generally coincide** [cite: 10, 22]. However, this divergence was not a failure of the theory. Instead, they proved that these functionals "anchor" new spectral points [cite: 22]. 

Specifically, they expanded the domain from singleton-supported distributions to distributions over bipartitions. They proved that for a subset of distributions satisfying a specific condition—termed **laminar weightings** (originally called "non-crossing" in CVZ)—the quantum functionals yield rigorous new spectral points [cite: 10, 22]. This significantly expands the map of the asymptotic spectrum beyond the singleton case, explicitly addressing geometries that include embedded 3-tensors and W-like states [cite: 10, 22].

***

## 8. Broad Applications of Subrank-Rank Duality

The theoretical machinery of the asymptotic spectrum, bolstered by the explicit CVZ universal points, has triggered a renaissance of applications across discrete mathematics, combinatorics, and information theory [cite: 9].

### 8.1 Matrix Multiplication Barriers
The quest to determine \( \omega \) currently relies on the Strassen laser method and the Coppersmith-Winograd construction [cite: 26]. However, the asymptotic subrank establishes rigorous limitations—barriers—on how far these specific methods can go [cite: 1, 26]. By computing the quantum functionals of the Coppersmith-Winograd tensors, researchers can mathematically verify that the "slack" in these tensors prevents them from achieving \( \omega = 2 \) via current degeneration techniques [cite: 27]. 

### 8.2 Additive Combinatorics and the Cap Set Problem
The cap set problem asks for the maximum size of a subset of \( \mathbb{F}_3^n \) containing no three-term arithmetic progressions. The breakthrough resolution of this problem by Ellenberg, Gijswijt, and Tao (using the slice rank method) fundamentally revolutionized additive combinatorics [cite: 1, 5]. 

CVZ showed that the cap set problem, and related questions like tri-colored sum-free sets, can be cast entirely within the framework of Strassen's asymptotic spectrum. By evaluating the quantum functionals on the "reduced polynomial multiplication tensor" (a prime example originally studied by Strassen), one recovers the exact bounds on the cap set problem [cite: 13]. The asymptotic spectrum is thus a strictly more generalized, foundational topological space from which specific combinatorial bounds manifest as simple shadows [cite: 13, 15].

### 8.3 The Asymptotic Spectrum of Graphs and Shannon Capacity
Inspired by Strassen's tensor spectrum, Zuiddam formalized the **asymptotic spectrum of graphs** [cite: 2, 3, 8]. Just as tensor rank defines computational complexity, the Shannon capacity of a graph captures the zero-error communication capacity of noisy channels in information theory [cite: 2, 3].

The graph spectrum yields a parallel duality theorem: the Shannon capacity is characterized precisely as an optimization over spectral points of graphs (which include known parameters like the Lovász theta number and fractional Haemers bounds) [cite: 2, 3, 8]. This highlights that the mathematical philosophy of duality—translating asymptotic properties into optimizations over homomorphism spaces—is a deeply fundamental feature of preordered semirings, applicable to both quantum computing arrays and classical communication networks [cite: 9, 12].

### 8.4 Algorithmic Optimization and Scaling
To compute the values of the CVZ quantum functionals explicitly, one must optimize over moment polytopes. Because these polytopes have exponentially many facets, traditional algorithms fail [cite: 18]. Recent research has focused on **scaling algorithms** to compute moment polytopes for reductive algebraic groups [cite: 20, 28]. By solving the membership and optimization problems over these geometric invariants, computer scientists are generating efficient algorithms that not only compute tensor complexities but directly solve specific instances of the quantum marginal problem [cite: 18, 20, 28].

***

## 9. Conclusion

The theoretical landscape of algebraic complexity theory has been irreversibly altered by the synthesis of subrank-rank duality, the asymptotic spectrum, and quantum information theory. Strassen's prescient formulation of the asymptotic spectrum reframed the messy, intractable arithmetic of massive tensors into an elegant topological duality. 

For three decades, the theory suffered from a lack of explicit, universal coordinates. The introduction of the **CVZ quantum functionals** by Christandl, Vrana, and Zuiddam finally furnished this abstract space with concrete, computable universal points, drawn from the physics of quantum entanglement and marginal states [cite: 13, 14, 15, 16]. 

Today, this framework is the absolute vanguard of computational theory. Whether establishing barriers for fast matrix multiplication [cite: 26], resolving combinatorial puzzles like the cap set problem [cite: 13], characterizing the Shannon capacity of communication channels [cite: 2], or exploring the diverging topographies of higher-order laminar weightings [cite: 10, 22], the subrank-rank duality and the CVZ universal points stand as a profound testament to the deep, unifying geometry underlying all of theoretical computer science and quantum physics.

**Sources:**
1. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOxUHbbN5Sx7EnrLEEzc1Ru3PtKnsaVum6m0HVHTlGhlv7yxuiIAabI6KOeGvAkyT3mkpr7pIfyvuyDjtSdRYFARtcSvH1vrc9_KnDrzPc7q6d1hoAn1T5if6WTmzQ3BGEEpVw_NhQgYpmFiDxL-PgekKvxo5Qa96Tic1wSMkELe8uivmVHW2WR6KgJdpcvozteE8cfAREBKNvsBYxPzXr)
2. [mathinstitutes.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOQKLpCyKYrJlWmVdzIsfttthbULEdHBdWAFdkcfbWMm41q75puSachRtPubPR_Rd9VVX5WT9nVd34oozCRleCNDi-As5qyR23Pp9O4Z_AVcT84KrLp5MgJ2lguAP8Kp8=)
3. [uva.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGW7RYzfWC1qYlyKs3KMt9BcoHY86dgOfjKo4kGlVY0egjSZleR8ZNRQuKWgPu8__W1hoes5kCfaLbPpjIgR8mPQFgXiuW8hEPd72KR5p89IBZyVMxsyumTQWf7xGvl6bhi)
4. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3xNH-Vzd4wp929XZi-3Zx1V7eRb6r_ukXldqXl9fvJPxzjXa3lJF0CgpT-YIO-OWbVRJb5dtbtSdGO_2fxdOf3gJQQmcDvlccJhyIYXkE8Y_LHMd1rpbhzJ78Bkz5sZjH13536w==)
5. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH972JynP5LmC_Js8WAMbAcKdkjnCJwFKVLXKs8b4obZmVSFbAetOAogGOPuYoT430WuzeMtrzF6W1-CrF460FF9R1txhtXeatTF0EJvajnBnfop2m3D0ocJt3haQPZlLBztgWzHqv0AiAjnjwz64qgq7Tq7qh_jk06vFh6YwmlXCWCMWqCcQN3b_UqLV2D0OLlYzPxE3vngsArWmnKLA==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhyLtyXvC1j0jL_NEDr0AAF6XDzlhcrlrB9TEOyZXiciq1F_qy_cNx8_9Qu2ApTS2LCETh7ButAAZGQ2D0XZ-0dtZGbg2jo_876f9IqHgcdO2JkbVlfg==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwSK3IX_VA4G8vSRSJcpoOcrdGP9KIRZo6GICHTar8Hdxa0aDzro1YaICm9vLWiOHM4j9uEAJh_WKA874clmHZ3kHhV9hL0SCeVw4DlGVGI57cDFJRGA==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMHFJb6_hbo84hDAPx9Eyk0VEbq2fPKs2b3qngYlikiaGmBFKbTa7tJwj5kqampx2xZy-cQH6F5AvDWMuCqJkqPxYL3eGxlBK723E5ouhvBZjd-LkkAG9zQw==)
9. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7HdpX4A-_7VSnbWEwFPbf_BkS4c2Uwkj7bfdHnRzY5ZN8LPq3nvwfumYYtdCtOkE-ud6esxTjR5SBUN99oT5JN7glfMC_Xb_D9AewGnSZkTza6w5FzpIaEAVRf_5puMQ1PTZmuNVaQIqX4r26tfDSWouo-Fhi5iocWs8EeMLVshZlY6A=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3a_VZqnDi8NJQq_XfuzdBojxGjIZaEL8_EOBsz1vqvVxgypJrIRkXRw-iVFdEKBAFAfM5IfgpNS9sZ1Q0nAJM78AeHLG8RFmIONaZnegfGob1252jlCU9dg==)
11. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIPdxhlPQOyUd_Cu1zRBz5zRwm4ChH5qEvJr60czCDTwJ07WSVsk7vX7EasiLleEt0CaNV7-CxRneOy4fcZM5Y8AH5FbBwkpHAWmermDVZAWEpEOpGw0ZnKV0cgkcl4Oa8J2tfUxBceoLP27Z3bXHdhiOwx9zZ_Bk1GoRFpufujBsKXHR6)
12. [uva.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNBtu8565MRMYv4bfYymE3D66fvoNxrEHirFiPPrjsq9bLYxbVSyQZ7SyIAGP8yshUGmmCy4pJ3rcDkO4PrJxYoWmhrwSnHPOt4YgtEGVb-67eFN17YH5Lqi1nG_1IWWzMg0UHkr_seIXakob_knk=)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaIV9VfkNLz0Eg897kKC9UJK3vDXzJH-eEYAAXarUNN1JTxUOjkhcQuOTghAPevxROOw0iL92WD2Y-0drjVrxjCHS7Oiikxkf_N48J6LvYfRIAem6f-A==)
14. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4MsEud5-qiOeBSv5mws3OlL4VegNwuxvc2Jt7P4mC-aW7PWUFYIkit5mEsPtOmhXWoEqMzK6I8P2uEe6JRRcd60-5n5wMEIV7lC2jTO9Vq2zGU398bQPY61xMfRBM40Kt35YPIF3Ix0yTtPjZjrdz7pt-7oF_rs6M11sxH0o5ts9BlP4dN7aimvlG01RTyIW0KLiw)
15. [ku.dk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFl5zhq4QsTLC_Fy3yBTiMHK4NC177waLuu1dk81MTfnspYdCAS4B88VpdM9bLo9wpXLiRi6-SIyr57REdKODCEYOGYOjFv9YJ-ZckO9q-5wNhVhnahGPIa9ucFVFUeZCHHOxmBWBZz9gdEhFd2ZvcAItSrUlFqOwgMzorKZ_53VJ3b07LBCT0MVQFSvOKitr3pqBBbeVyalQFJUU4=)
16. [uva.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFywwStC7O5ow-FmtHTbuIiBpeTMDC_Crv5nztEuggBcAnHvwBiXsXYBqk6wOBsLvu8OiIpeb5f5UtaFRwM6aCrcI1l41SoH_tVWftPPFOIkHR6tyKyHf8-egrs8-WG0Fq2k9jLqEM0rh-FiQabn3nXLV0ZUxpU8IXGDhf4pl23RuxhzcK6TV3kLoltCCpSUJak2GdWyB2EbnR8IknGd9eAd-O5zESooLXuLzRDkgAFfX51E-Du_YzwV_0-F7nu3q4YAXStP9HB51aW)
17. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoeGBQIt66S1WcBG1qaU7gt09AWjMaqbnFA0gYQpTns-jL9NZ0QTpdcYLg1VHob1f6GzWT37mcN3Y7iruQYqkAVlUxGN14HyuVVFVDL6EmUl79CJZtItJ_sdGRJP5ADqPT9FGIQDSgGzrMeGm_cqkmOFg9FMw=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtN-CtbtAjvY2ae4jV0NBuX2E34IFORc2F870Ip4E-cPdq4U5yENMv4QJtTB_gplVotGiYViijWd2D5e9LcjaAnGB40lGkcGaoFdD7lL5GBQYgt2vfew==)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0u7gGJjb7CxiI_9WhZhbJbrZcBpnh5T4ykyDjZpLAGY792CzED98C-h5toMmDXR7AHpxZrL6o7kEJDAEunMpO6Qann__ZALAJoGJnXFdm0-FPUcbzeE1H8VouLrX_v3RS2Rlq31-l11RWdbPgIuBAeN_6HwgiX4c5KCaRcy5rocQS6-zegxL9QJesv3JXeCgJIzTvbpU=)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEveMktvBFQz5eFe5eNEJTqRdXwwRW8obXc4SQJ-sQXxLN6Okiy1Rc2LUEe-C3INaXX4DCk01HFdCRQHo40KU3WfYDbY7bMYjd7Enyxi1eNhEC-CoMF7g==)
21. [qutech.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbcOcan3uajWotQe3GVPy4Z7T1LomUj-c9A264omZS8C3smhdjdAsmRwurXT5ABibZIuutegWVwZil9JljM6J5RDL6yAL6ds7uLAqYpcx2aZ8R3hS4V-Bjh5Io98NgNfFMlaTlVAg4KLhHMp0MlCR5oXowb496nm7HqDu4vUu6ENxTFI6Q_GKzjw==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWRtYvO8z1REL1fYcQFaeCYStyqw6bbMkEabaZMMdOpHtHq36o_GROVjA0D5MElPlI5OPfjjA1lwUwQl_8u1xgG8RJ3BHmBpxFTPDGRYQY2IWBlx6E-w==)
23. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGP_oxzEEe151N8a5XMsk5iG6yMliOMKE6SGhiq1LJUagnZqhRanjJoBplpt5opdKclariqMclPDsq8aVDn9M311bziIa7HMXOsSjgkdHorliD5v-oG9oC63Wd8)
24. [uva.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBCb0r-1XxwlOF4DV6uBO2QOh-8pZ3MG70PmuvKZ3akX-a9pgWO7yIxSzrCmlCT-ZaRCi4wQFnCEBYQLtI9CFyONx82_mQCQbhzsTKG2bwE46ch5bOLMTnvWp2UUNvhl_KZ1e6iIy8B_LV)
25. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQQuZyNa04kgFweeJZPAP17ZXMn4Hv_8TpExSX1EkMjrbb6rJmMQVHMPjH-HUMHvGL3de5Y-2DEYcb4KHzUfMc-j22Oxz4yKgvAjWJ0s0rX6UiZOlmf83YbGZVd42CN30MEh0bHBq8ZWuN16_MeLMyWbC2f5XdqQ4PRxDQh7m5X_DcPlfHL6M9JfjqTPxQByS0La3WsCGPdUWGSN77hWZ9VvxnSY6K0rgAFCarxghNFuR2CQ==)
26. [theoryofcomputing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEM0j7aUECHNon_1DrYUv6h29MBQ3ucRWndE8TLcaUadqey7jIYdIdCbYu6tJsXr1mnIlGLK49f69DFzILmO6UdJG67vgtMiArAO772yQy7MdVqQY5dsVfK6sJ_GteqhETZthuLY_TO-0fKm2NCiDC9mAw=)
27. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHihJm0rkhoILZhxCohOZSCD6jttRxqG5iUwrmsJHZP0E4RmeR2_NtKupoL78mXpu6qZ_Q_jbXWyBGFJo98T9-grkTocvuklWYlnNbxlrlj97ZaAjFZfjnewDct8HzZkPLrJ5Pm02FzQuWX3GH_V4oxlQ5Fc_Gs2Pk9TRQUpUIId8U=)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXY_up6ok_YiS44jtXFN6HAADj9QEQnbK8iDNwENrg5rWZdLfAidgl2_ivRGXkoqxBcvhenkio7TflrfoCidtxh_I3WccolIsK5p2efprwKjKnfh1ZAQ==)

