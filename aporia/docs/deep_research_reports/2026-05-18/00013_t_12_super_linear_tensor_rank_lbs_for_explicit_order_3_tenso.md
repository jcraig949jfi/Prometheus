# T#12 Super-linear tensor-rank LBs for explicit order-3 tensors (Raz)

**Pythia queue id:** 13
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdoM2dMYXBHeE43SGlfdU1QN2RUdXlROBIXaDNnTGFwR3hON0hpX3VNUDdkVHV5UTg
**Elapsed:** 368s
**Completed at:** 2026-05-18T20:43:36.860308+00:00

---

# T#12: Super-Linear Tensor-Rank Lower Bounds for Explicit Order-3 Tensors and Their Implications

**Key Points:**
*   **Fundamental Discrepancy:** While matrix rank is computationally tractable via Singular Value Decomposition (SVD), computing the rank of tensors of order 3 and higher is rigorously proven to be NP-hard.
*   **Raz's Breakthrough:** Ran Raz (2010) established a profound theoretical bridge demonstrating that proving super-linear tensor-rank lower bounds for explicit order-3 (or higher) tensors would directly yield super-polynomial lower bounds for arithmetic formulas, solving a major open problem in complexity theory.
*   **Explicit Constructions:** Alexeev, Forbes, and Tsimerman (2011) advanced this pursuit by analyzing "permutation tensors" and "group tensors," providing conditional super-linear lower bounds for explicit order-3 tensors based on representation theory.
*   **Practical Paradigm (T#12):** Despite extreme theoretical hardness, as highlighted in the ICASSP 2017 Tutorial T#12, tensor decomposition remains practically viable and theoretically unique under mild conditions, driving major advances in machine learning, signal processing, and chemometrics.

The study of tensor rank bridges the deepest theoretical questions of algebraic complexity with the most pressing practical challenges in signal processing and machine learning. At the theoretical extreme, the inability to compute or even approximate tensor rank underpins our failure to separate major computational complexity classes. Ran Raz showed that if one could merely find an explicit multilinear array (a tensor) that has a high, super-linear rank, it would prove that certain mathematical functions require exponentially large arithmetic formulas to compute. Concurrently, in the applied domain—as summarized in the seminal ICASSP 2017 Tutorial T#12—practitioners rely on the unique properties of tensor rank (specifically CP decomposition) to disentangle mixed signals in brain imaging, wireless communications, and spectroscopy. This report exhaustively synthesizes the mathematical foundations, algebraic lower bounds, and applied signal processing frameworks surrounding tensor rank, explicitly addressing the quest for super-linear lower bounds for explicit order-3 tensors.

***

## 1. Introduction to Tensor Algebra and the Concept of Rank

Tensors serve as a natural multilinear extension of matrices. While a matrix represents a linear mapping between two vector spaces, an order-$d$ tensor represents a multilinear mapping across $d$ vector spaces. Let $F$ be a field, and consider a tensor $T \in F^{n_1 \times n_2 \times \dots \times n_d}$. The elements of this tensor are indexed by a $d$-tuple $(i_1, i_2, \dots, i_d)$. 

### 1.1 Formal Definition of Tensor Rank
The most common definition of tensor rank, often referred to as CANDECOMP/PARAFAC (CP) rank, is the direct generalization of matrix rank. A tensor is said to be of rank 1 if it can be expressed as the outer product of $d$ non-zero vectors. That is, $T = v^{(1)} \otimes v^{(2)} \otimes \dots \otimes v^{(d)}$, where $v^{(k)} \in F^{n_k}$. Consequently, the entries of a rank-1 tensor are given by $T_{i_1, \dots, i_d} = \prod_{k=1}^d v^{(k)}_{i_k}$ [cite: 1, 2].

The rank of a general tensor $T$, denoted as $\text{rank}(T)$, is defined as the minimum integer $r$ such that $T$ can be expressed as the sum of $r$ rank-1 tensors [cite: 3, 4]. Mathematically,
\[ \text{rank}(T) = \min \left\{ r \;\middle|\; T = \sum_{j=1}^r \lambda_j u_j^{(1)} \otimes u_j^{(2)} \otimes \dots \otimes u_j^{(d)} \right\} \]
where $\lambda_j \in F$ are scalars [cite: 3].

### 1.2 Divergence from Matrix Algebra
For $d=2$ (matrices), the tensor rank definition precisely coincides with standard matrix rank (the dimension of the column space or row space) [cite: 5]. Matrix rank benefits from equivalent, highly tractable definitions: it can be found via Gaussian elimination in polynomial time or via the Singular Value Decomposition (SVD) [cite: 5, 6]. 

However, for $d \ge 3$, tensor rank fundamentally diverges from matrix intuition. The maximum rank of an order-3 tensor $T \in F^{n \times n \times n}$ is not $n$, but rather $\Theta(n^2)$ [cite: 7]. Despite a general tensor having high rank with probability approaching 1, proving that any *specific, explicitly constructed* tensor has a high rank is notoriously difficult [cite: 4, 8]. Furthermore, tensor rank is not semi-continuous. It is possible for a sequence of tensors of rank $r$ to converge to a tensor of strictly greater rank; this anomaly necessitates the concept of "border rank," which is the minimum rank required to approximate a tensor arbitrarily closely [cite: 9].

***

## 2. The Computational Complexity of Tensor Rank

The difficulty of proving lower bounds on tensor rank is intrinsically tied to the algorithmic hardness of computing it.

### 2.1 NP-Hardness and Inapproximability
A landmark result by Johan Håstad (1989/1990) established that determining whether the rank of an order-3 tensor $T: [n]^3 \to F$ is at most $r$ is an NP-hard problem over finite fields and the field of rationals [cite: 5, 10]. This computational barrier forms the bedrock of why explicit lower bounds are so elusive. Part of the difficulty in classifying the approximation hardness of tensor rank is that any gap-preserving reduction from an NP-hard problem to tensor rank would automatically yield super-linear lower bounds for explicit tensors [cite: 11].

Recent theoretical work has cemented this hardness. It is NP-hard to approximate the rank of an order-3 tensor over any field to within a factor of $1 + 1/1852 - \delta$ for any $\delta > 0$ [cite: 4]. If a reduction from SAT to 3-tensor rank outputs a tensor of dimension $n$ that always has rank at least $cn$ (for $c > 3$) on unsatisfiable instances, it would instantly provide explicit high-rank order-3 tensors, bypassing decades of manual mathematical construction [cite: 4].

***

## 3. Ran Raz's Theorem: Tensor Rank and Arithmetic Formulas

The central motivation for finding explicit tensors with high rank lies in algebraic complexity theory. A long-standing "holy grail" of theoretical computer science is to prove super-polynomial lower bounds for the size of general arithmetic circuits or formulas computing explicit polynomials (like the Permanent) [cite: 7, 12].

### 3.1 Strassen’s Connection
The connection between tensor rank and algebraic complexity was initiated by Volker Strassen in 1973. Strassen demonstrated that the tensor rank of order-3 tensors is inextricably linked to bilinear complexity [cite: 7, 11]. Specifically, if an explicit tensor $A: [n]^3 \to F$ has rank $k$, then the smallest arithmetic circuit computing the corresponding bilinear form $f_A$ has size $\Omega(k)$ [cite: 7, 10]. Because the maximum rank of an order-3 tensor is $O(n^2)$, Strassen’s approach can, at best, yield $\Omega(n^2)$ lower bounds for arithmetic circuits. While this provides super-linear lower bounds in the number of variables, it falls drastically short of the super-polynomial lower bounds required to separate complexity classes [cite: 7].

### 3.2 Raz’s Super-Polynomial Lower Bound Framework
In a breakthrough 2010 STOC paper (later published in JACM 2013), Ran Raz fundamentally elevated this approach [cite: 13, 14]. Raz studied higher-order tensors $A: [n]^r \to F$ where the order $r$ is super-constant, specifically bounded by $r(n) \le \log n / \log \log n$ [cite: 7]. 

Raz proved that if one can find an *explicit* tensor $A$ in this regime with tensor rank strictly bounded below by $n^{r(1-o(1))}$, it would immediately imply an explicit super-polynomial lower bound for the size of general arithmetic formulas [cite: 7, 12]. 

The proof relies on depth reduction and homogenization. Raz showed that if a set-multilinear polynomial of degree $r$ can be computed by a fan-in 2 formula of size $s$, it can be transformed into a homogeneous, set-multilinear formula of depth 3 with only a polynomial overhead in size [cite: 7, 8]. Because the size of a depth-3 set-multilinear formula is directly governed by the tensor rank of the polynomial's coefficient tensor, an exponentially large tensor rank forces the original arbitrary-depth formula to be super-polynomial in size [cite: 7].

### 3.3 The Specifics of Order-3 Tensors
While Raz's primary theorem requires super-constant $r$, the search for super-linear lower bounds on *order-3* tensors remains a foundational stepping stone. Raz's framework implies that if the tensor rank upper bounds are tight, proving super-linear tensor-rank bounds for explicit order-3 tensors implies structural rigidities that could be generalized to order-$r$ tensors [cite: 11, 15]. For a tensor $A: [n]^3 \to F$, an explicit lower bound of $\Omega(n^{1+\epsilon})$ is necessary to bridge the gap between trivial bounds and super-quadratic circuit lower bounds [cite: 1]. 

***

## 4. Explicit Tensors and the Challenge of Super-Linear Lower Bounds

To utilize Raz's framework, the tensor must be "explicit." A tensor family $T_n$ is explicit if its entries $T(i_1, \dots, i_d)$ can be computed by an algebraic circuit of size polynomial in the bit-length of the coordinates, i.e., $\text{poly}(d \log n)$ [cite: 10, 11]. 

By a simple parameter counting argument, a random order-3 tensor has rank $\Theta(n^2)$ with high probability. However, explicit constructions have historically stalled at linear bounds. 

### 4.1 Folklore Reshaping and Trivial Bounds
A trivial way to generate lower bounds for an order-$d$ tensor $T \in F^{n^d}$ is by "flattening" or "reshaping" it into a matrix. By partitioning the $d$ indices into two sets of size $\lfloor d/2 \rfloor$ and $\lceil d/2 \rceil$, the tensor is viewed as an $n^{\lfloor d/2 \rfloor} \times n^{\lceil d/2 \rceil}$ matrix. The matrix rank of this flattening provides an automatic lower bound for the tensor rank. This yields a folklore lower bound of $n^{\lfloor d/2 \rfloor}$ [cite: 10, 11]. For $d=3$, this flattening yields a matrix of size $n \times n^2$, whose maximum rank is $n$. Thus, this method cannot exceed a linear $\Omega(n)$ bound for order-3 tensors [cite: 1].

### 4.2 The Alexeev-Forbes-Tsimerman Constructions
In 2011, Boris Alexeev, Michael Forbes, and Jacob Tsimerman presented novel techniques to break past the trivial flattening bounds. For odd $d$, they constructed field-independent, explicit $0/1$ tensors $T: [n]^d \to F$ with rank at least $2n^{\lfloor d/2 \rfloor} + n - \Theta(d \log n)$ [cite: 11, 16]. 

For the critical case of explicit order-3 tensors, their construction yielded a lower bound of $3n - \Theta(\log n)$ over any field [cite: 10]. While this is a strict improvement over the $n$ reshaping bound and the $2.5n - \Theta(n)$ bound achieved by Bläser for the matrix multiplication tensor [cite: 11], it is an exact analysis—meaning the bound cannot be pushed to the super-linear $\omega(n)$ territory required by complexity theorists [cite: 10, 17]. Implicit in Håstad's earlier work was a bound of $4n/3$ [cite: 11].

***

## 5. Permutation Tensors and Group Tensors

To hunt for higher ranks, Alexeev, Forbes, and Tsimerman investigated a generalization of permutation matrices, which they termed **permutation tensors** [cite: 10, 16]. 

### 5.1 Permutation Tensors
A tensor $T: [n]^d \to F$ is a permutation tensor if its entries are exclusively 0 and 1, and there is exactly one 1 in every "generalized row" (the 1D fiber created by fixing $d-1$ indices) [cite: 10, 11]. Since all permutation matrices (order-2) have maximal full rank, it was naturally conjectured that permutation tensors would possess near-maximal tensor rank [cite: 10, 11].

Via a counting argument applied to Latin squares (which correspond identically to order-3 permutation tensors), it is straightforward to prove that there *exist* order-3 permutation tensors with super-linear tensor rank over finite fields [cite: 10]. However, this argument is non-constructive; it does not yield an *explicit* tensor.

### 5.2 Group Tensors and Representation Theory
To instantiate an explicit permutation tensor, the authors defined a highly natural algebraic construction called the **group tensor**. For a finite group $G$, the group tensor $T_G^d: G^d \to F$ is defined by:
\[ T_G^d(g_1, \dots, g_d) = 1 \iff g_1 \cdot g_2 \dots \cdot g_d = 1_G \]
where $1_G$ is the group identity [cite: 11, 18].

Since group multiplication is explicitly computable, group tensors are completely explicit [cite: 11]. The crucial question became whether group tensors maintain the super-linear rank promised by the existence of Latin square permutation tensors.

Alexeev et al. proved two devastating upper bounds showing that group tensors have surprisingly *low* rank, severely eliminating them as candidates for Raz's framework [cite: 11, 18]:
1.  **Representation Theory Bound:** Over large fields (like $\mathbb{C}$), the rank of $T_G^d$ is bounded by $|G|^{d/2}$ [cite: 11, 18]. For $d=3$, this implies a rank of $O(|G|^{3/2})$, which is $O(n^{1.5})$. Furthermore, using the exponent of matrix multiplication $\omega$, they tightened this to $\text{rank}(T_G^3) \le O(|G|^{\omega/2}) \le O(|G|^{1.19})$ [cite: 18].
2.  **Interpolation Bound:** For Abelian groups over *any* field, Fourier interpolation techniques show that $\text{rank}_F(T_G^d) \le O(|G|^{1+\log d} \log^{d-1} |G|)$ [cite: 11]. 

### 5.3 Conditional Super-Linear Lower Bounds
While group tensors fail to possess maximal rank $\Theta(|G|^{d-1})$, their analysis yielded a critical conditional result. Alexeev et al. demonstrated that **if the representation theory upper bound is tight, then super-linear tensor rank lower bounds for explicit order-3 tensors would immediately follow** [cite: 11, 16]. Specifically, if the rank cannot be compressed below the $|G|^{d/2}$ threshold, then for $d=3$, the rank is $\Omega(n^{1.5})$, thereby crossing the super-linear threshold for an explicit tensor. Although unconditionally proving this tightness remains an open problem, it presents one of the most viable pathways to satisfying Raz’s criteria.

***

## 6. Advanced Theoretical Approaches to Tensor Rank Lower Bounds

Beyond permutation tensors, several other advanced mathematical frameworks have been employed to search for super-linear tensor rank lower bounds.

### 6.1 Low Bias and Multilinear Forms
Swastik Kopparty and colleagues explored the relationship between the "bias" of multilinear forms and tensor rank. Bias is a measure of pseudorandomness; a tensor with low bias behaves structurally like a random tensor [cite: 19]. They proved that for an order-$d$ tensor, low bias strictly forces high tensor rank. For $d=3$, this approach offers a natural route to non-trivial lower bounds [cite: 19]. 

Specifically, they showed that trilinear forms (order-3 tensors) with nearly minimal bias of $2^{-(1-o(1))k}$ must possess a tensor rank of at least $2.409k$. Furthermore, an exact analysis of the finite field multiplication tensor using this bias framework yields a lower bound of $3.52k$, matching the best-known explicit tensor rank lower bounds for 3-dimensional tensors initially established by Brown, Dobkin, and the Chudnovsky brothers [cite: 19].

### 6.2 Strassen's Commutativity and Border Rank
Tensors satisfying Strassen's commutativity equations are intimately related to spaces of commuting matrices [cite: 9]. An order-3 tensor $T \in A \otimes B \otimes C$ is "A-abelian" if its corresponding endomorphisms commute [cite: 9]. Exploring these tensors allows theorists to study "border rank"—the smallest $r$ such that $T$ lies in the Zariski closure of the set of rank-$r$ tensors [cite: 9]. Strassen’s additivity conjecture posits that the border rank of a direct sum of tensors is the sum of their individual border ranks, a property that holds true if one of the tensors has a border rank of 3 [cite: 20]. 

### 6.3 Slice Rank and the Cap Set Problem
A recent revolution in tensor theory was the introduction of "slice rank" by Terence Tao, building on the work of Croot, Lev, and Pach to solve the Cap Set Problem [cite: 21]. Slice rank is a less restrictive notion than tensor rank; a tensor has slice rank 1 if it can be factored as $u \otimes V$, where $u$ is a 1D vector and $V$ is a tensor of order $d-1$ [cite: 21]. While high slice rank implies high tensor rank, slice rank is much easier to upper-bound via polynomial methods. Counterexamples utilizing lattice subsets and antichains show that requiring high slice covering numbers for explicit tensors remains just as formidable as classical tensor rank [cite: 21].

### 6.4 Sum-of-Squares and High-Rank Decomposition
While finding explicit high-rank tensors is hard, algorithmic *decomposition* of random high-rank tensors is equally challenging. Standard unfolding algorithms cannot decompose an order-3 tensor if its rank exceeds $n$ (the linear barrier) [cite: 1]. However, utilizing the Sum-of-Squares (SoS) hierarchy, researchers have developed quasi-polynomial time algorithms capable of decomposing a random 3rd-order tensor even when the rank is super-linear, specifically up to $n^{3/2}/\text{poly}\log(n)$ [cite: 1]. The SoS algorithm utilizes higher-order "pseudo-moments" to bypass the unbalanced dimensions of order-3 flattenings [cite: 1].

***

## 7. T#12: Tensor Decomposition in Signal Processing and Machine Learning (ICASSP 2017)

The theoretical roadblocks observed in complexity theory stand in stark contrast to the practical utility of tensors. The ICASSP 2017 Tutorial 12 (T#12), titled "Tensor Decomposition for Signal Processing and Machine Learning" by N.D. Sidiropoulos, L. De Lathauwer, X. Fu, and E.E. Papalexakis, represents the definitive applied framework for tensor rank [cite: 5].

### 7.1 The Paradox of NP-Hardness and Practical Utility
Tutorial T#12 heavily emphasizes a profound paradox: Determining higher-order tensor rank is NP-hard (as proven by Håstad), and low-rank tensor decomposition is identically NP-hard [cite: 5]. However, unlike matrices, which have an infinite number of low-rank decompositions (e.g., $A B^T = (AM)(M^{-1} B^T)$ for any invertible $M$), **tensor decomposition is essentially unique under extremely mild conditions** [cite: 5]. 

Kruskal (1977) proved that if the sum of the Kruskal ranks of the factor matrices is sufficiently large, the CP decomposition of an order-3 tensor is completely unique up to permutation and scaling [cite: 1, 5]. This uniqueness guarantees that the latent factors discovered by tensor algorithms represent genuine, physical, underlying components rather than arbitrary rotational artifacts.

### 7.2 Applied Tensor Formulations
In signal processing, practitioners observe data as $X = L + N$, where $L$ is a low-rank tensor and $N$ represents noise [cite: 5]. To perform the decomposition, algorithms typically bypass exact rank computation, opting instead to fit a tensor to a specified rank $r$ using continuous optimization techniques, most notably Alternating Least Squares (ALS).

**Tucker Decomposition:** Another focus of T#12 and related literature is the Tucker Decomposition (or Higher-Order SVD) [cite: 22]. Here, a tensor is factorized into a dense "core tensor" multiplied by factor matrices along each mode [cite: 3]. If the core tensor is restricted to be perfectly diagonal, the Tucker decomposition collapses back into the CP model [cite: 23]. Because CP rank is non-convex and non-smooth, practitioners sometimes use the "nuclear norm" of the tensor's unfolding matrices as a convex surrogate for tensor rank, allowing for robust machine learning applications [cite: 3].

### 7.3 Real-World Applications 
The uniqueness of tensor rank decomposition enables powerful signal analytics:
*   **Chemometrics:** In fluorescence spectroscopy, researchers observe 3D data arrays (Excitation $\times$ Emission $\times$ Samples). CP decomposition accurately and uniquely extracts the independent emission and excitation spectra of unknown chemical compounds without a priori knowledge [cite: 5].
*   **Neuroimaging:** Electroencephalography (EEG) and functional ultrasound data are inherently multidimensional (Space $\times$ Time $\times$ Frequency). Analyzing this data via CP or Tucker models avoids the severe information loss associated with flattening the data into a matrix, allowing for highly interpretable isolation of neurological stimuli [cite: 23].
*   **Dynamic Networks:** Temporal social networks are represented as order-3 tensors (Node $\times$ Node $\times$ Time). Tensor decompositions extract shifting community structures, allowing for the clustering and tracking of network multiplexes over time [cite: 22].
*   **Quantum Information:** Tensor rank dictates the entanglement complexity of multipartite quantum states. The GME (Genuine Multipartite Entanglement) of a 3-qubit state is directly classified using the rank of its 3-way correlation tensor. If the correlation tensor rank is 2 or 3, it signals a GME state [cite: 24]. Furthermore, "purification rank"—the minimum dimension of an ancillary space required to purify a mixed state—corresponds to the positive semidefinite factorization rank of a tensor slack matrix [cite: 25].

***

## 8. Conclusion

The concept of tensor rank inhabits two radically distinct worlds. In the realm of algebraic complexity, it serves as the ultimate gatekeeper. Ran Raz's theorems dictate that isolating explicit order-3 (or higher) tensors with super-linear tensor rank will unlock super-polynomial lower bounds for arithmetic formulas, solving decades-old questions in computational hardness [cite: 12, 13, 15]. The work of Alexeev, Forbes, and Tsimerman pushed this boundary to its absolute limit, providing exact $3n - O(\log n)$ bounds and laying out a blueprint—via the representation theory of group tensors—for conditional super-linear bounds [cite: 10, 11]. 

Conversely, in the applied universe chronicled by ICASSP 2017 T#12, the theoretical NP-hardness of computing tensor rank is a mere footnote to its practical supremacy [cite: 5]. Because tensor CP decomposition is unique, it has become the de facto standard for latent factor discovery in machine learning, blind source separation, and signal processing [cite: 22, 23]. 

The eventual discovery of unconditional super-linear tensor-rank lower bounds for explicit order-3 tensors will not only rewrite the foundations of algebraic circuit complexity but will likely yield deep geometric insights that will cascade into the algorithmic optimization techniques currently driving modern artificial intelligence and data science.

**Sources:**
1. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjEIAKAtCZDBiKyAaxYhyUPDQNYfeH9iAkFFgqIdDpdbOHHzrINJPLfAIWxAq3mtktWuv0wqaR6V1GVCwmdp98Gu4TXY656AYLp67jU2XUhlBXlWEx)
2. [tensornetwork.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTDqupWlkDeFh5j1BLkYIMrLnot3s4tjsTrrTkrsrQYV68R5CDuWYjISuuIa4Fvyd-B7u7X5U_QL2aaVw8EU9SY-Gy5uRGR9kQZzaJrPLuDg8hnZq43o0=)
3. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBN5nQm7Zb1YbH7jAnIjV2EnOx1V4IlfPzTA1sdlomB8gF6DYcNTfTZZkEDhMkyQOTHSuU0HXNnG7iFGvpB88Cm4PAuK3Zq5Yv4fcahnJdmc7ki3UkdZiZUfxIETxXz3OUJnMVPfqqdB-pk2XwGFZeKv8LEAbv-U8jidY=)
4. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHu6RpValzhPSpD9F-7PXu_4YtvjUTiFMBLxS7az1Z6yqE1ZLoc4PvLUlbaTY1RNPL9j1zjm4vh_O_6M_dPNlNg8l4VEwl5xHo1Jo0pSTO1JhNhKZf_9nJO55mp4wkyAR-bkst6i4HZ0Oh0TjO9f0Zh_HCaxM9f1awQL8bcWstN0Mjl5vkPTHqoVNa7UzazrWE2EHn2CkViYqKt5-e7Df-L1AvR-WBh8-Tq68VREi-JFAE4rJqaP2jIFREKzDIjAg==)
5. [oregonstate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPyiXTvwplUGFj6heGcVtsqMDmPC5886yUKWEgaN0dr6iQdQCuRFUxud8mq1ObV0FKZS5jTfNCcGCNAK-1Et6IVCgQO54Q1_aJt2Ph6JsptvHqajk8u0fuI-cMyDASBJAtdKzQy8CTXg3Oc5IewbmMdLOsAHd3)
6. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpq53MAUPejPFU6NPGIlrB7G4wHFgTUsXbc5nNqaUD-qxD-KvoCnJ3r27HQFAnh8H9axBnOi_82XaALcT30HotgHGGa17jkmBkm6qG__jDWhgOuBRgW4xrhwHAyPUvvEi56aoWtHXPhG3sgxZIgc7-)
7. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnizvHEZOzZPEVof3zNtsanFloyrSKjxyxxEw04zdMGIussrLD2K_a2GYxXqbAVYmvi1ayaRHZd6TTdtAuAcK1fUG7NccJ9KWfPS0iyr7lNMSM3VWQmCAPrYsDxsKMY9kbscEWud49VEaQCEw7oERtZIQ0fxGqqkqI)
8. [bitbucket.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqxhs6sapRLhcbQ8EM6pg2POtX7ohBZjHMhdT2ZfBGmV6RzoaDxCBYZxhzTa6g1sIg3shA-59O51KO6nLp4BrGGCu328LQ6AxXC092tNBY3gcWTBLy4SxEgMsuddB5KRMbhXpO5RIqKCw=)
9. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuFABVZOquNj2M01HgZdTJc6LBUmil6qXuXBLHgxJT-CD_6YAowNqPP3phnFY8t4Fz6ad68gCPEGd5SxxVK4hYSO_Ip7I0velHiFYxtuElvVT1KYsDeKNhE5L60hiWqtPP5RI=)
10. [borisalexeev.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHf8Qm-vtX1AJfCe5g9HWnolhCTQ913xby2hMQP7cDgKzj2lRI8f_2FmptqmnvxTCrgeu2l4CES3m0CVKVA0BXvGPVutdkbXWaXmg8Uqdyo0UUwDSo1q4uRuQ==)
11. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECfktt4rMq8B_toGqTeOsM13mR9w8DJdb_-u7a555Y5iBcxQdLGqW5j45-VFLMrv74NAsHdv0dPFP72p9g_3Mmy_kLuh_XZTl4A4NfOFBVUC47H-v1rpLQQHpCdsS4ewUFJCk37zUlnm3h3g==)
12. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOGBMV9JHJqx5UoW2OumGjYBz4DaaVO6nS16GN_LDMbzAvk4e2Md7e5etPpJLv1mi0y5a_AnMU5GM_AH47hshyfMycYoWjqibM09W9xeA6ZF09X_gI4nUa9PY0pq4T0wnK51qYDQwTU5t0eHTCt9u20wc74cDhKZQ=)
13. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWeiT7YuY070N7z8CfgNvyyya1uPpgTUsFy1DTUItzmqvsXge0A2VbF7HiiwwNMA-QEHImlFXSfeNyXfvSbKkwINfrwlBDbAGra38tws5pFHOBTel8Diyc4Jjg5VvN1x_RXrYXB5uQADBQnzVRP0H90xZ3Nja1v_3UkQ==)
14. [amanote.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFR2Cz5HG714fgeEzpvgPyFJ0pEl4pik7axiYtZgMJ6wN93xWK-GHYbPse4r9DpW5Dd82PiofjwHV0Ud1iOFIwZbBdWqOSpxX8YEAkOZD5OgemNETjJin2YrJa9ErHi73vP_Z0rjSlUjuulSpBxXgNT_zlh7isoJUzZR9thEzM4Lqjht0jVnR6qvlfVZ10acBBwSHGN0UttSs5NPe7YRLATDHQafkg3QGg=)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWCLZu8hk_J3dg82FI3YmanoAFzBcZh8QEgDYeNP1Z5a0X_jL-afGCz-_VlJOxVJqaX0sXO9HuCbG4kBOd9JSeyCOYF3iza3rC-lpQTJOSs70lGML1C6GebR-tsX_3i6nEQEkLyQYkTpo3xYu3vstN5aoUEhU-Z1NkSYbiW-eVUtzya_A=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgRDb9kuxp5NS9JMyxYxIj0EDP42pO7Zoqjg33p8OGqMMqLfDrvGEuhRXLcyHeWmrVBmVAF4Iqt8sVTuP6v3WDUF43LgkPlwOS10YkruznUW5JGgES)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4J4WuQnDOPHLE6NLiaoG8FE5dFuInxZ6au87m37V-iA5PS3r1nAY5e5IrgV53LLH1Gp3GDGYJsynoJvg9sSP93weQlSTyiaCgu_VJSZr5cr0iClK1)
18. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFU1Iu_cbfYxgDNzPcCTMmhPCuE25cUvc1og1tVo_Mp0LYq8UYv-zKn9LK7pNnp0pRkf4eACSUvEqG5mUvfMQ8D--XCKOJ9NS1dZnFgEhEgyyv23FUOglvZS30dTnfZKE7LRYs=)
19. [toronto.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSiNK0ASQijoCWi6cns_2PeLjscnpCQCVQoNgAYE1lufN0tvUdSmCuXoO-6o0iZpNp-OEEjMYmeVfOSbqMhOPWMAkAYbLndcWr9RU_z2gWNmJVAhJGgfGtvXRagwhy6zvj64gyPwkhAy9PPL1hhcg=)
20. [mimuw.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBPOUpFF3FUMTE7MZSBdjNiliU3kiRBXmqUv5IbXgCv6pnuMpXYeRDqtvN05MzvcEiQYq9Bg-0wj7tQK1b_vS__p3ZV4jTioyWQUO1kWkZ_lbM79zsXVdOEeGw7mK67NvBERBg9NbRXvfjHb1n2lSAQ2O1Fu2tt_9HvCCU7oQ=)
21. [cam.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnU7-O-1IagETnfMyp1S8NMNk6R6C9oHSJ1isLBDe5pJapGlm0t7YJmyXNmf_btcLXI9kJA55KT1PJ1ftRW2-W1AK6y7QVRpznDRGG2ggOqLf99--WFm1yfMoocAVRndZ0IsvbTFQFa8JwUcGn4jP2sb1Q4x0LYH7avYpWz7ZLV3TdoJzs87lrXzLHts-UjA==)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGY0MGNcIJSIb-XluoRK9VtU1UiziFlenhjm1nokqngHhG2La6JNihu8ZmzVBw8f6y3U8_RB3ic5tdP-4WF9DQZRj7b-SIOJt9wxatLQdeBX1yWtBrCmMe6jCX1xRolabkPLQGHnEtdEo5pI3CzjU5Qwsymz9Wcn7H1PyLvOQBXVmUU4A-XK6iC8lFfXt57pwnqOwT6uT3Ir2KVnRnEsaCj9cI30zkJpXadG51jdg==)
23. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFe5Z2WAgZOuca14c7ZYt2AxyYqsSwBrc1V5AcDHGDOsHJKzKp-fhqp4lBG0dd_29g3-9Az_A97--e87J6iD7qJSD3Auel7i4Ti3ryAr9EkohOsgtGm7UXWXSNyLktWf_eRP9c6n8-pi_sSfoG6VwJpxIYYVA==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh7_v9VfR7gEYy7zhkLk9-Iehi6revfLsLNWEC5bTAy8pi0c_UUciEq39tOJBInRspu2RPyCZrVQpCHGQ5Sdon5b6AO7VbwJ4ExIHHvtf8iTcUTPxNFg==)
25. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEH-72k56-RGnorddTcvQJX6ONFUy-YlEpEKSaNHpviCS07K4-leaeD37_gTuv2XdglpqR1iPsGZcmZR-hxD3q8_flzguDdruG8NcXULkWn6NYq8rgo5b58vkhhtBJlkyeIGjvyp4ykmhKgVCKC7MK8twZkaLAMupPhItm6W6-rQBDNXD0AGDYM14CygYyr4n-K32H1HJJ2Vz0wD0EJLWvU7z4sxH0oKqpVLp-Y4O4hM6UB)

