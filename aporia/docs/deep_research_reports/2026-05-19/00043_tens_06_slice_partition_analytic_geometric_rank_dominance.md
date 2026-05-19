# TENS-06: Slice / partition / analytic / geometric rank dominance

**Pythia queue id:** 43
**Tier:** T1
**Priority:** 1
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdseTRNYXNHUEVKM0Ytc0FQdzhUZTZRTRIXbHk0TWFzR1BFSjNGLXNBUHc4VGU2UU0
**Elapsed:** 249s
**Completed at:** 2026-05-19T09:38:25.705750+00:00

---

# Empirical Comparison of Tensor Rank Notions: Slice, Partition, Analytic, and Geometric Ranks Across Tensor Families

**Key Points**
*   Research suggests that the traditional notion of matrix rank fragments into several non-equivalent, yet deeply interconnected, rank notions when generalized to higher-order tensors ($d \ge 3$). 
*   **Slice rank** and **partition rank** capture the combinatorial structure of tensors, heavily dominating recent breakthroughs in extremal combinatorics, such as the cap-set and sum-free set problems.
*   **Analytic rank** quantifies the "randomness" or bias of tensors over finite fields using Fourier analysis, functioning as a subadditive alternative to slice rank that can seamlessly replace it in cap-set applications.
*   **Geometric rank** relies on algebraic geometry (codimension of varieties) to provide structural bounds over algebraically closed fields. It currently dominates applications in multilinear circuit complexity, particularly in proving exact upper bounds for the border subrank of matrix multiplication.
*   Recent breakthroughs (2022–2026) have established quasi-linear equivalences between partition and analytic ranks over all finite fields, though recent edge-case separations (e.g., via the determinant tensor) reveal that the ratio between partition and analytic rank can tend to infinity with the tensor order.

### A Multidimensional Approach to Tensor Complexity
The mathematical study of tensors has historically been tied to the standard tensor rank, which directly generalizes matrix rank by counting the minimum number of decomposable (rank-1) tensors needed to express a target tensor. However, researchers have found that standard tensor rank is often too rigid or analytically intractable for complex combinatorial and computational problems. To bridge these gaps, mathematicians have introduced alternative rank measures—such as slice rank, partition rank, analytic rank, and geometric rank. Each of these parameters projects the complexity of a tensor through a different mathematical lens, be it structural, probabilistic, or geometric.

### Application-Specific Dominance
The usefulness of these ranks tightly depends on the specific problem at hand. When bounding the size of combinatorial structures that avoid certain patterns (like arithmetic progressions in cap-sets or sum-free sets), the polynomial method natively aligns with **slice rank** and **partition rank**. However, when algorithms seek to minimize operations in multilinear circuits—most notably in fast matrix multiplication—the mathematical focus shifts to Strassen's subrank. In these computational complexity scenarios, **geometric rank** has emerged as the most powerful tool for establishing tight upper bounds. 

***

## 1. Introduction to the Tensor Rank Ecosystem

The generalization of matrix rank (order-2 tensors) to arbitrary $d$-tensors (where $d \ge 3$) leads to a fragmentation of the rank concept [cite: 1, 2]. For a matrix, the structural rank (the number of rank-1 matrices needed to express it), the analytic rank (related to the uniform distribution of its evaluations), and the geometric rank (codimension of the kernel) are all equivalent [cite: 3, 4]. For tensors of order 3 and higher, these equivalent matrix properties diverge into genuinely pairwise distinct functions [cite: 2].

Different types of tensor ranks have been developed to study algebraic complexity, extremal combinatorics, and quantum information theory [cite: 5]. The study of fast matrix multiplication algorithms, initiated by Strassen in 1969 [cite: 2], birthed the notion of **subrank** and **border subrank**, which act as the ultimate measures of a tensor's "value" as an intermediate computational step [cite: 5, 6]. Conversely, combinatorial problems such as the cap-set problem birthed **slice rank** [cite: 1, 7] and **partition rank** [cite: 1, 2], while higher-order Fourier analysis necessitated the probabilistic **analytic rank** [cite: 1, 3]. Finally, establishing rigorous bounds connecting finite fields to continuous fields (like the complex numbers) gave rise to **geometric rank** [cite: 6].

Understanding which rank dominates a given problem requires an empirical comparison of how these ranks behave across specific tensor families, such as diagonal tensors, W-tensors, determinant tensors, and matrix multiplication tensors [cite: 8, 9]. 

## 2. Formal Definitions and Methodological Properties

To accurately compare these metrics, one must formalize their underlying mechanics.

### 2.1 Standard Tensor Rank and Subrank
The **tensor rank** (or traditional rank, TR) of a $d$-tensor $T \in V_1 \otimes V_2 \otimes \dots \otimes V_d$ is the smallest integer $r$ such that $T$ can be written as a sum of $r$ decomposable (simple) tensors $v_1 \otimes v_2 \otimes \dots \otimes v_d$ [cite: 10, 11]. In algebraic complexity, the tensor rank of the matrix multiplication tensor bounds the number of scalar multiplications required to multiply two matrices [cite: 2, 12]. 

The **subrank**, $Q(T)$, introduced by Strassen, operates in reverse. It measures how much a tensor can be "diagonalized" by finding the size of the largest diagonal tensor (identity tensor) that can be obtained from $T$ via linear combinations of its slices (i.e., Gaussian elimination for tensors) [cite: 8, 13]. Subrank provides lower bounds on computational complexity but is notoriously mysterious and hard to compute [cite: 5]. The **border subrank** extends this by allowing approximative degenerations in orbit-closures [cite: 14, 15].

### 2.2 Slice Rank and Partition Rank
The **slice rank** ($SR$) was introduced by Terence Tao to provide a symmetric reformulation of Ellenberg and Gijswijt's breakthrough proof of the cap-set conjecture [cite: 1, 2, 7]. A tensor $T$ of order $d$ has slice rank 1 if it can be written as $T(x_1, \dots, x_d) = a(x_i) b(x_{-i})$, where $a$ depends on a single variable and $b$ depends on the rest [cite: 7]. The slice rank of $T$ is the minimum $r$ such that $T$ is the sum of $r$ tensors of slice rank 1 [cite: 1, 6]. For 3-tensors, a rank-1 slice tensor takes the form $u(x)v(y,z)$, $u(y)v(x,z)$, or $u(z)v(x,y)$ [cite: 7]. Slice rank is sub-additive and monotonically decreases under restriction [cite: 1].

**Partition rank** ($PR$), introduced shortly after by Naslund, generalizes slice rank. A tensor has partition rank 1 if it can be factored as $a(x_I)b(x_J)$ where $I$ and $J$ form a non-trivial bipartition of the coordinates $[d]$ [cite: 2, 7]. The partition rank of $T$ is the minimal number of such reducible tensors that sum to $T$ [cite: 16]. It follows by definition that $PR(T) \le SR(T) \le TR(T)$ [cite: 3]. For $d=3$, slice rank and partition rank coincide, but for $d \ge 4$, they are genuinely distinct [cite: 2].

### 2.3 Analytic Rank
While slice and partition ranks are combinatorial, the **analytic rank** ($AR$), first defined by Gowers and Wolf, is probabilistic [cite: 1, 3, 17]. For a multilinear form $T : (\mathbb{F}_q)^d \to \mathbb{F}_q$ over a finite field, its bias is defined as the expectation over random inputs $x_1, \dots, x_d$ of the non-trivial character $\chi(T(x))$. The analytic rank is given by $AR(T) = -\log_{|F|} \text{bias}(T)$ [cite: 9, 11]. 
Analytic rank essentially measures the equidistribution of the multilinear form. Lovett later proved that the analytic rank is strictly sub-additive ($AR(S+T) \le AR(S) + AR(T)$), a highly desirable property that combinatorial ranks lack [cite: 3, 7].

### 2.4 Geometric Rank
Motivated by an open problem to extend analytic rank beyond finite fields to algebraically closed fields (like $\mathbb{C}$), Kopparty, Moshkovitz, and Zuiddam defined the **geometric rank** ($GR$) [cite: 1, 6]. For a $d$-tensor $T$, the geometric rank is defined via algebraic geometry as the codimension of the algebraic variety formed by the vanishing of specific bilinear forms associated with the tensor's slices [cite: 6, 11]. 
Specifically, for a 3-tensor $T \in \mathbb{F}^{n_1 \times n_2 \times n_3}$, $GR(T)$ is the codimension of the set of elements $(x, y) \in \mathbb{F}^{n_1} \times \mathbb{F}^{n_2}$ such that $T(x,y,z) = 0$ for all $z \in \mathbb{F}^{n_3}$ [cite: 6, 11]. Geometric rank is lower-semicontinuous, meaning the set of tensors with $GR(T) \le m$ is closed in the Zariski topology, allowing it to upper bound the *border subrank* seamlessly [cite: 6, 18].

***

## 3. The Rank Hierarchy and Theoretical Equivalences

Comparing these ranks mathematically yields a definitive hierarchy that bounds the computational value of any tensor. The generally accepted sequence of inequalities for any given tensor $T$ is:
\[ Q(T) \le \text{Border } Q(T) \le GR(T) \le PR(T) \le SR(T) \le \text{Flattening Ranks}(T) \le TR(T) \]
[cite: 5, 6, 15].

### 3.1 Equivalence of Partition Rank and Analytic Rank
A long-standing objective in additive combinatorics has been to prove that structural complexity (partition rank) and pseudorandomness (analytic rank) are equivalent [cite: 9, 19]. 
*   **Lower Bound:** Lovett, and independently Kazhdan and Ziegler, proved that analytic rank is always at most the partition rank ($AR(T) \le PR(T)$) [cite: 2].
*   **Upper Bound:** Determining whether $PR(T) \le C \cdot AR(T)$ has required a massive timeline of research. Green and Tao (2009) obtained the first qualitative bounds, which were quantitatively improved by Janzer and Milićević [cite: 2]. Recently, Cohen and Moshkovitz achieved a linear equivalence over large fields [cite: 2]. Moshkovitz and Zhu (2022) achieved a quasi-linear equivalence over *all* fields up to logarithmic factors by introducing **local rank**, a vector-valued tensor rank analyzed via random walks on the zero sets of polynomials [cite: 2, 16]. 

### 3.2 Equivalences Involving Geometric and Slice Ranks
Over algebraically closed fields, geometric rank provides a characteristic-zero analogue to analytic rank [cite: 6, 18]. Recent independent works have confirmed linear equivalence between analytic rank and geometric rank [cite: 15, 20]. Furthermore, geometric rank, analytic rank, and Derksen's G-stable rank are all equivalent to slice rank up to a constant factor [cite: 14, 21, 22]. The linear equivalence among these ranks is intimately tied to the stability and asymptotic additivity of partition rank [cite: 20].

***

## 4. Empirical Comparisons Across Tensor Families

The theoretical equivalences up to constants hide the nuanced empirical performance of these ranks on specific tensor families. Different tensor families expose the strengths, gaps, and separations of these rank concepts [cite: 13, 23].

### 4.1 Diagonal Tensors and the Cap-Set Problem
The **cap-set tensor** is a diagonal tensor $I_n$ corresponding to the indicator of the equation $x+y+z=0$ in $\mathbb{F}_3^n$ [cite: 2, 7]. 
*   **Slice Rank Performance:** Slice rank accurately captures the deficiency of this tensor over characteristic 3 [cite: 22]. The asymptotic slice rank of the cap-set tensor takes the non-integral value $\approx 2.755$ over $\mathbb{F}_3$ [cite: 13]. Slice rank historically bounds the subrank perfectly for this family.
*   **Analytic Rank Performance:** Analytic rank perfectly mirrors the slice rank capabilities for diagonal tensors. The relative analytic rank $AR(T)/AR(I_1)$ upper bounds the size of the largest principal subtensor of $T$ that is diagonal [cite: 15]. Analytic rank offers empirical advantages because it avoids the combinatorial overhead of slice rank decompositions [cite: 3, 24].

### 4.2 W-Tensors and Sunflower-Free Sets
The $W_k$ tensor is defined by having coefficients in $\{0, 1\}$ and a support given by permutations of a single entry, such as $W_3 = e_2 \otimes e_1 \otimes e_1 + e_1 \otimes e_2 \otimes e_1 + e_1 \otimes e_1 \otimes e_2$ [cite: 8]. 
*   This family is heavily used to study sunflower-free sets [cite: 1, 8].
*   The asymptotic slice rank of the W-tensor equals $2h(1/3) \approx 1.88$, where $h$ is the binary entropy function [cite: 13]. 
*   Recent gap theorems by Costa and Dalai, extended by Christandl et al., proved that any tensor parameter that is a "normalized monotone" (which includes slice, partition, analytic, and geometric ranks) must exhibit an asymptotic gap. For any tensor, its asymptotic rank on tensor powers is either exactly 1, or bounded strictly away from 1 by a specific constant dependent on the W-tensor [cite: 8, 23].

### 4.3 Determinant Tensors and Asymptotic Separations
The determinant tensor $\det_n$ represents the multilinear form of the determinant of an $n \times n$ matrix.
*   **Separation:** In a 2025 breakthrough, Lampert utilized the determinant tensor to empirically separate partition rank from analytic rank for $d$-tensors. While previous generic random tensors failed to yield separations (a random $d$-linear form of partition rank $r$ has analytic rank roughly $r$), the determinant tensor proves that the ratio of partition rank to analytic rank can tend to infinity with the dimension $d$ [cite: 9, 19]. 
*   Specifically, $PR(\det_n) \ge \log_2(n) + 1$, whereas the analytic rank of $\det_n$ is roughly bounded near 2 [cite: 19].

### 4.4 Matrix Multiplication Tensors ($\langle m \rangle$)
The matrix multiplication tensor maps $m \times m$ matrices to their product.
*   For a 3-tensor representing $m \times m$ matrix multiplication, Strassen originally used his laser method to bound its border subrank by $\approx 3/4 m^2$ [cite: 6, 15].
*   **Geometric Rank Performance:** Slice rank and analytic rank struggle to concisely lock in tight bounds for border subrank in matrix multiplication. Conversely, geometric rank evaluates precisely to $\lceil 3m^2/4 \rceil$, matching Strassen's bound perfectly [cite: 6, 15]. 

***

## 5. Domain Dominance: Which Rank Dominates Where?

Returning to the core of the user's inquiry, we analyze the dominance of these rank parameters across three primary domains: the cap-set problem, sum-free sets, and multilinear circuit complexity.

### 5.1 The Cap-Set Problem
**Dominant Parameter Historically:** Slice Rank.
**Dominant Parameter Modernly:** Analytic Rank & Geometric Rank.

*Context:* The cap-set problem asks for the maximum size of a subset of $\mathbb{F}_3^n$ containing no non-trivial three-term arithmetic progressions ($x+y+z=0$). Croot, Lev, Pach, Ellenberg, and Gijswijt solved this by applying the polynomial method, yielding an $O(c^n)$ bound where $c < 3$ [cite: 1, 2, 10]. 

*Why Slice Rank dominated:* Tao translated the polynomial method's degree-constraints into the language of tensors, proving that the solution heavily relied on bounding the slice rank of an identity tensor versus an indicator tensor [cite: 1, 2, 7]. Slice rank was tailor-made for the combinatorial structure of induced hypergraph problems [cite: 22].

*Recent Shifts:* Analytic rank was shown by Lovett (2019) to be capable of completely replacing slice rank in the resolution of the cap-set problem [cite: 3, 17, 24]. Because analytic rank is strictly subadditive—meaning the analytic rank of a sum of two tensors is at most the sum of their individual analytic ranks—it easily bypasses the clunky combinatorial summations of slice rank [cite: 3, 24]. Furthermore, geometric rank is directly equivalent to slice rank up to a constant and can provide identical cap-set bounds when analyzed algebraically [cite: 6, 21]. Thus, while slice rank is the most famous for this problem, analytic rank provides a more robust mathematical framework.

### 5.2 Sum-Free Sets and Sunflower-Free Sets
**Dominant Parameter:** Slice Rank and Partition Rank.

*Context:* A tri-colored sum-free set is a collection of triplets $(x_i, y_i, z_i)$ in an Abelian group such that $x_i + y_j + z_k = 0$ if and only if $i=j=k$. The Erdős-Szemerédi sunflower problem looks for sets without "sunflower" structures.

*Why Slice/Partition Rank dominates:* The slice rank method was aggressively adapted by Blasiak, Church, Cohn, Grochow, Naslund, Sawin, and Umans to obtain tight bounds on the sizes of tri-colored and multi-colored sum-free sets in Abelian groups with bounded exponents [cite: 2]. Furthermore, Naslund used the closely related partition rank to bound the size of subsets avoiding $k$-right corners and to exponentially improve bounds on the Erdős-Ginzburg-Ziv constant [cite: 1]. The algorithmic problem of deciding whether $SR(T) \le r$ (closely related to orbit closure containment) continues to use slice rank to generate algorithmic bounds for progression-free and sum-free problems [cite: 10]. 
While analytic rank *can* be used to bound independent sets, slice rank and partition rank explicitly match the polynomial factorization needed to exclude solutions to linear equations over $F_q$, making them the uncontested operational tools for sum-free and sunflower-free bounds [cite: 1, 10].

### 5.3 Multilinear Circuit Complexity (Matrix Multiplication)
**Dominant Parameter:** Geometric Rank.

*Context:* In algebraic complexity theory, calculating the exact exponent of matrix multiplication, $\omega$, is equivalent to finding the tensor rank of the matrix multiplication tensor [cite: 2]. The subrank and border subrank evaluate a tensor's ability to simulate independent scalar multiplications.

*Why Geometric Rank dominates:* Slice rank is an upper bound on subrank ($Q(T) \le SR(T)$), but for complex tensors like the matrix multiplication tensor, slice rank is loose or computationally intractable [cite: 5, 6]. Subrank itself is highly mysterious and notoriously difficult to compute [cite: 5]. 

Kopparty, Moshkovitz, and Zuiddam introduced geometric rank specifically to remedy this gap [cite: 5, 6, 25]. Because geometric rank is a property of algebraic varieties over continuous fields, it behaves elegantly with approximation limits, making it *lower-semicontinuous*. This ensures that geometric rank easily bounds the **border subrank**, the approximative version of subrank heavily utilized in matrix multiplication lower bounds [cite: 6, 18]. 

By analyzing the codimension of the variety $x^T M_k y = 0$, Kopparty et al. proved that the geometric rank of the $m \times m$ matrix multiplication tensor is exactly $\lceil 3m^2/4 \rceil$ [cite: 6, 15, 25]. This identically matched Strassen's 1987 lower bound limit derived from the laser method, proving geometric rank's unmatched supremacy for multilinear circuit bounds [cite: 6, 25]. Additionally, geometric rank cleanly bypasses the finite field limitations of analytic rank, making it the premier framework for characteristic-zero circuit complexity [cite: 6].

***

## 6. Recent Breakthroughs and Empirical Results (2023–2026)

The convergence of algebraic geometry, combinatorics, and Fourier analysis has accelerated the production of recent breakthrough theorems regarding these rank parameters. 

**1. Quasi-Linear Relation Between Partition and Analytic Rank (2022-2024):**
Moshkovitz and Zhu solved a major open conjecture in additive combinatorics by proving that partition rank and analytic rank are equivalent up to a logarithmic factor over any finite field [cite: 2, 16]. They introduced an intermediary vector-valued tensor parameter called **local rank**. By simulating random walks on the zero sets of polynomials representing the tensors, they successfully established stability bounds, bridging the gap between structural (partition) and pseudorandom (analytic) parameters [cite: 16].

**2. Asymptotic Gaps for Normalized Monotones (2021-2023):**
Costa and Dalai originally established that a $k$-tensor over any field either has an asymptotic slice rank of exactly 1 or bounded below by a threshold dependent on $k$ (e.g., $(3/2)^{2/3} \approx 1.889$ for $k=3$) [cite: 23, 26]. Building on this, Christandl et al. formally determined that for *any* "normalized monotone" bounded by flattening ranks—which empirically covers slice rank, partition rank, analytic rank, geometric rank, and G-stable rank—an asymptotic gap exists [cite: 8]. If a generic tensor avoids collapsing to 1, its powers under tensor products will grow at an explicitly computed constant strictly larger than one [cite: 8, 26].

**3. Bounding Geometric Rank via Subrank over Algebraically Closed Fields (2025):**
Subrank normally acts as the absolute floor of the rank hierarchy ($Q(T) \le GR(T)$). In June 2025, Lin et al. established novel inverse relationships. They proved that over any algebraically closed field, the geometric rank of a tensor is bounded by a mathematical function of its subrank [cite: 20, 27]. For order-3 tensors, they precisely proved that geometric rank is bounded by a quadratic polynomial of its subrank [cite: 20]. This provides an astonishing "de-bordering" result, ensuring that subrank growth rates are at most quadratic under field extensions [cite: 20].

**4. Asymptotic Separations Using Determinants (2025–2026):**
While Moshkovitz and Zhu proved that analytic rank and partition rank are quasi-linearly equivalent up to constants depending on $d$ (the tensor order), a preprint by Lampert (September 2025) proved that this dependence on $d$ is mathematically necessary [cite: 9, 19]. By analyzing the determinant multilinear form $\det_n$, Lampert showcased that $PR(\det_n) \ge \log_2(n) + 1$, establishing an asymptotic separation where the ratio between partition rank and analytic rank tends to infinity as $d$ increases [cite: 9, 19]. 

## 7. Conclusion

To evaluate the empirical utility of tensor rank generalization:
*   **Slice rank** and **partition rank** reign as the absolute combinatorial tools for Ramsey theory, cap-sets, and sum-free sets due to their synergy with the polynomial method [cite: 1, 2]. 
*   **Analytic rank** serves as their subadditive, probabilistic counterpart, smoothing out algorithmic inequalities in cap-sets [cite: 3, 24]. 
*   **Geometric rank** transcends finite fields, granting geometric insight into border subrank that tightly answers Strassen's matrix multiplication bounds, thoroughly dominating the multilinear circuit complexity domain [cite: 6, 25]. 

Ultimately, while the bounds and values generated by these ranks often align asymptotically, their mathematical derivations—varieties, Fourier biases, and partitioned outer products—guarantee that no single rank parameter will universally eclipse the others. Research dictates that modern tensor analysis requires selectively applying the appropriate rank relative to the field constraints and the required operational bounds.

**Sources:**
1. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBCHU_KqOVCoCJEjx0M-43XEBu-f78UwwiYJfaC6UP54RnH312_nahLwJd1X9u5bPVucVtOZFFdBmjnzsCmU5C6L_5gVABsoVFXzl0fLxcPFQFw2oYdRZ8UYnXau7bjhpGoQE=)
2. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSmXJW6eOk2MVjQgHhKAw32w3N_S9Kms_rmMPw4eZkKhRggHojttQX6_iD0Rlrlvf2fvXxJGzoVa6RTspIUXw3Vf_ScAvhTlC_x83LHmos4Cy5Wg--hB6B-gq2)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElLoaN0_FjOjqgMRo_pp_YmzbZNDhoIpybKcqAlnGB5y-M26EtcSgirjPCwnQ3Aj1Er25ViiyS1M7ozNoj4GqSoEOn-YNgjCIXnm69YsuNH2KncD3K_Q==)
4. [rochester.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHVHPzpjGsknkaoCMwOT53R_5fl48r-Ietu08XnLKbrccMxmeaAc5AMAKaITE5iUY0ZRJQIZK_0r8Flhc47WMA-k6sPG6iTuMk11TZ7mTvBqhQtj38aD3RtKI2Q8vYkfl-oIHgXr48xB04gAkC6bc-_ka960ygTE0n0aa3G7tnayH0EH_YtheWhlTspw==)
5. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSghZhcZTvx6TMwbco1rNbAyYQWbrGoWx9vgsJwLSw-nO6dJ4kOVpgm8YIimvHHLKXhuAtrQT3FsMve_Y2E8LJtiowiYsS3mbL7AQiQagHjdjwEQ1JLJyDS_SdrOnCoyxJhP0ik5GfiWXDFw==)
6. [toronto.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcZgtysr_VfpxXvgzO_I6LP9GDCIZ75L9RVFoDaw74vkdp74LvUPgpjjpCQ6myzKkazZqLWWbAPaKTjIoXRbS-VNLV8yfyTzr_WCfbPlvEl66GWRucJBGTUcmcSyLIgAl9dNnUkSkohA==)
7. [discreteanalysisjournal.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWbwqj07_6gMHvtMSnYEJEA-uwAULfjPyBcA-cx3nq8_Zicv-gxgDBJ19h-jhRgHbt_XHAxDiO6HkfZx585g-_rfvjq8lXOgTcEQjow8UnqsaR9Zdfs6KotAkWh73o0NXPkWa0GBJas3lg0v0y7BfhJuuuDdqLJTadQptW2JCucFD54x3bITxFSVTZJ3uAMWMCVGalq7pNkD4=)
8. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXns1OBcwVmIJ3cIRSOc77YasogaeVyLGuuqphLjcWgGkBiZqPU5oeyA5k07CTi_Q0O8WWZ67kmFzVNHbl9r3p4BYkB7bZ8O2bC42rdQVXcUwyz0_RLtBHa0i8)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_MEmDDR6pNNdSNrZM-I1ajC0aa48DMqYl6DfsEFj7o8Ie0YUFDYEHAMoJESNa23eg-QjtF5aDRgL67i2664GCz07_onkrE0po7UJu7Hj1_-RfF9T0q0_1nQ==)
10. [liverpool.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAGdJbOj6s6wsPadDNecdtMohWAMgTDNK2A4Pl99xyvH2m91sXGeqP_udMojKg1_hxvLHBKdKWBce7tbs9dty1D-9FCeKkcb5H5VshhnbJ-0rscc6uvCKijG5JobwTjbGQE1cvLxms1vpOItYxaY8=)
11. [combinatorialpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyYX18fULRM4MBgj5TRTZons5Ii_ZVdHBg6V51gs9jNpVlF-YSCL7yxU0sbZe3ce5uqbZMp5Tx7IzZAP0anyDCAlgQle23PheK5w_kPvr99SPrCD-tKMwKCqWHxovSX1zFF-gLgEz4YMraUKx-BKQ=)
12. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF33jyL5wEr0sxaL2jCIySnaiJaE4ekWGj_MxqktZa5fZwIL3E3w6FBOMUG-0dGGP-AkDR8-mjjspHVGe1GVvKjTf8pTFVmUN1ODi4i2XCknJrUSC0MQXVStOkCm-C6mCTt)
13. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFY5UM-cb78xQNjeHGrIWHTY-tgkpEKYT5yLCYP_fh4BzGCAUXPEAauIG3NkigAVTrh-rrxhMdqt05bvAXauMMOXiDIa4j0aQ1H6AYbO1HdMR5yX1hHDTmatTbC)
14. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7ogUBkfjFguwxvRxNrcXIhGgQzsoRJYv7ZlBp-K8DYon2ah4B2_gKP-lGsbj-R4_XCPdpw3Nm1Q3_5r7TqbtHIh_HQBtL1tDWgBQtQKoS9PKX2m1BjlBjaKqF9Yw8qbiMjtpB2YOUBmqXWcVlmrtr3Hx-nVpPOfHZzIUOadSgALh8spXQPeUtiT9eTIBGLnrMEDHSNYOQKmKrJdYpfw==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0fq9FZhLXzfciQ-AecVTOmUJxf9lzLPb7cbX6doRZu-djb47hxdQeAnHmq0mYQoNRj8xYoj74LmRB1z83hiK-ySLRfozlknJSCVzyBDdcqI5tlwObkg==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbNl3DOP0RMNv9pKHPJSecefolvBPa44YaVRWDaVCmgeMQDhThKkZGQupY0s3A7FWjBLHN9IgqgKgZ-Zaf-ib5glSaefN6HkX2a__iv-oOnEjjvgzvlg==)
17. [discreteanalysisjournal.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuEgUCosnO155xCs1f8kJg8zO0DSblPvgQeHyA-C5xU7Nb5uTw47-OL0ictOaD59ZM7Qt6nA917UWj7P-h20d5MNUa2dl8wU8IwWLSjkzA9qTVPj4O1hax2ONVkDbJhiFtuT4DcIrZ2x3IcWpOslmYUuGvni-hbBhtextWzHxTGg2gnPqh-otI7lGVexM_zC03aDpIXI8sQw==)
18. [uva.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaoBcTvwIwZKu9WIxdt6BwQGZ0D2bnJB-vEzOiTH_653OY8t-NlUoHod3fE1DAVxlYpWCKB28rkMnjAw9irhQ0jBcgPkTuLyWGgAmIXclyvG6iSB4dwJrWc8vwrjSGZBGB2Kntr7U7-mukkZhHcOPhPgOuPqyHRti8sKcNfMxOMjN4Z1a8PzG5kF_3gZ5GrHA28s_MYg9SElQh6wV7Lak=)
19. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnzA5HEHK9R7090440YUfNr04nw_by6lqUDRpx0ON1jEH5UfbKgRQrx-PJvx9SJ1JHCytGbJjSRa55crodTXgu6q7hfIjNenVwO36BB4u6kBZU1srNYnY0jU4vtxaasN--9u-hFACdbbj8DD57Ry8c-CRnhtf4gQUjYo4dx3PeNDCYykfmc-fIG7Yn37hMQ5O8dQDoDi4rHPT2ziA1xvGNEq8m)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSa_O8vOxS2k8Wmh59NEHrEWX5VoOdbUCdw3GqfoexA3N5ca53CrDJF-zBqygc1C6NM_DOAcFKyfLFspkyVmOw_ny51NtI_QpAnyfpqR_eO9BPgjTqzA==)
21. [acm-stoc.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1VinC4D9Q4dSuIk8Uq_Eq_RhFLGiYJYoOf8bNwa6SHFFGVQAlZ35puicMhilYMu2vXUUPmuPwolE2ygiVTpJ07P8NN5vguYag2n-6QmHAawpebBE-Kgm8tYylsQ==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqx17CfyuDjTll0lHkig7C4JXe4YSnZi8gFtw_vJkfthOy6RpVAeLePiGjVv4dL7EaC2LK_KQJFj25BT9XvGesKaZV0Hl2WbU8bspmSSD5RJza7iinBoua1Q==)
23. [unibs.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVMDUt_6RRYD3J9XaWy30_eZMnPDqX4uEYlMm9enYCRKIp6j19uisBvQlW0BpWlOTaHk0Z0L6sKSpp34Ifak1TeqzAFnqrJGC_8bQQYhVrq5a5EWwp1OUz0GmNWgDNIUAmxqkHcFCOSi0FpqeXBjBaenHdOA-mNEhAnSIVxQy-FY1E9S6QQUHd1VL_JzKmPNOzuEj3qUDzMP8CiFI=)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhlrhURUv-HTJPUdkajBwVesCoEApXgwCgqY4j5aT0rxsYsUEDvFD8z0an5aRgC5Ay_qGHvq8c1USx1_y7vCY0IX5Eg9wEtgbux_tmoic9FW-Nmd42fg==)
25. [discreteanalysisjournal.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFi93j5la1TDZfiuv6aImLicjAyDfdCQX8vvZCtx3ql1FUHeGhKsVi1Y4UxzhE3M4HPynnDMkwQxZSptDTjlWl4HcbPMdUcDkKK77wkzWwmAs7NlmiS2X-xXIQOiFvxtwYi_38h0kdXb8bh8SfIkL-lvZ_WrScT9RrWVD9a6V5qjAq6ikqmvdqFUBwG7VJqND2Ir6naOI7DlCvfinodGQPA2H076Iyz)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiIzIrbsVAPuyrS8bqmRKdEoEB0HdXau5liG6A4VRp0wKrMRRY-Pmy_SQFOu4xtFAmcFpW_zdo62t8z11hMMvU7nI6JeJhYyZFG-duZwXIeHoQQmK6Og==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8yHIAEa7oz8Y2LWvwrx06E41z1zipxVh_eTjmhfHuzB7JqUGr9fyn0gDz4QVT8pBGKKCIYKkA7ko-OqDFuOHsMGzUQGZORKIvz_yz8CK2oZVtUJUKH602gg==)

