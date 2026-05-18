# T#15 Slice-rank method optimality beyond F_3 (composite moduli)

**Pythia queue id:** 15
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChctbmtMYXI3eE85U19fdU1QaE4yb3lRSRIXLW5rTGFyN3hPOVNfX3VNUGhOMm95UUk
**Elapsed:** 371s
**Completed at:** 2026-05-18T20:49:50.895276+00:00

---

# The Slice-Rank Method: Optimality, Limits, and Extensions Beyond $\mathbb{F}_3$ into Composite Moduli

**Key Points:**
*   The slice-rank method, formulated by Terence Tao as a symmetric abstraction of the Croot-Lev-Pach (CLP) polynomial method, fundamentally revolutionized extremal combinatorics and finite geometry.
*   While initially applied to the cap-set problem in $\mathbb{F}_3^n$, extending the method to composite moduli (such as $\mathbb{Z}_4$ or $\mathbb{Z}_m$) introduces profound theoretical roadblocks analogous to those found in circuit complexity.
*   For progression-free sets over composite moduli, the method yields the general upper bound $r_3(\mathbb{Z}_m^n) \leq (0.9184m)^n$ for $m \geq 3$, though tighter bounds remain open for specific composites like $\mathbb{Z}_{15}^n$.
*   The theoretical optimality of the slice-rank method is constrained by structural limits. In disciplines like coding theory (trifferent codes) and theoretical computer science (fast matrix multiplication), the method faces demonstrable barriers that prevent it from yielding the ultimate theoretical limits (e.g., proving $\omega = 2$).
*   Extensions such as the partition rank and multi-slice rank have been developed to bypass the strict "diagonal tensor" requirements of the original slice-rank framework, enabling progress on off-diagonal problems like bounding right-angle-free sets and analyzing generalized Diophantine equations.

**Summary for the General Reader:**
In 2016, a massive breakthrough occurred in mathematics regarding how to find the maximum number of points in a high-dimensional space that do not form a straight line (the "cap-set problem"). Researchers used a new approach involving polynomials, which mathematician Terence Tao later simplified into a tool called the "slice-rank method." Initially, this tool worked perfectly for spaces based on prime numbers (like 3). However, when mathematicians tried to apply it to spaces based on "composite" numbers (numbers that can be multiplied by smaller numbers, like 4, 6, or 15), the tool hit a metaphorical wall. Moving beyond prime numbers to composite numbers is incredibly challenging and is compared to some of the hardest problems in computer science. This report explores how far the slice-rank method can go, where it hits its optimal limits, and the new mathematical variations invented to push past these boundaries.

---

## 1. Introduction and Historical Context

The polynomial method in combinatorics underwent a dramatic evolution in the mid-2010s. Historically, combinatorial problems concerning arithmetic progressions—such as finding the maximum size of a subset of a finite abelian group lacking a 3-term arithmetic progression—were attacked using Fourier analytic techniques [cite: 1]. However, these methods often struggled to yield exponentially small upper bounds relative to the size of the ambient group.

The landscape shifted permanently with the seminal work of Croot, Lev, and Pach (CLP), who introduced a novel polynomial method to prove that sets avoiding 3-term arithmetic progressions in the group $\mathbb{Z}_4^n$ are exponentially small compared to the size of the group [cite: 2, 3]. They demonstrated that any progression-free subset $A \subset \mathbb{Z}_4^n$ has a size bounded by $|A| \leq 3.62^n$ [cite: 3]. This breakthrough on a composite modulus was immediately adapted by Ellenberg and Gijswijt to resolve the famous cap-set problem in $\mathbb{F}_3^n$ (and more generally $\mathbb{F}_p^n$), proving that the size of cap-sets is also exponentially bounded [cite: 3, 4].

Shortly following the back-to-back publications of CLP and Ellenberg-Gijswijt in the *Annals of Mathematics*, Terence Tao introduced a symmetrized formulation of their arguments on his blog [cite: 5, 6]. Tao's formulation abstracted the algebraic manipulations of polynomials into a linear-algebraic property of tensors, which he termed the **slice rank** [cite: 6, 7]. The slice-rank method provided a highly elegant, symmetric framework that eliminated the need for asymmetric degree bounds, shifting the focus to the decomposition of high-dimensional tensors [cite: 7, 8].

Since its inception, the slice-rank method has been applied to a vast array of problems, including tri-colored sum-free sets, sunflower-free sets, the Erdős-Ginzburg-Ziv constant, and fast matrix multiplication algorithms [cite: 4, 6]. However, as the method has been deployed across different mathematical domains, its limitations—particularly concerning composite moduli beyond prime fields—have become increasingly apparent, prompting the development of refined tools like the partition rank and multi-slice rank [cite: 9, 10].

---

## 2. Mathematical Foundations of the Slice-Rank Method

To understand the optimality and limits of the slice-rank method, one must first define the algebraic construct upon which it is built.

### 2.1 Tensors and Slice Rank Definition
Let $\mathbb{F}$ be a field, and let $V_1, V_2, V_3$ be vector spaces over $\mathbb{F}$. A 3-tensor $T \in V_1 \otimes V_2 \otimes V_3$ is typically analyzed by its standard tensor rank, which is the minimum number $r$ of decomposable (rank-one) tensors $v_1 \otimes v_2 \otimes v_3$ (where $v_i \in V_i$) needed to express $T$ as their sum [cite: 6, 11]. 

The slice rank relaxes this definition. Instead of requiring purely decomposable tensors as building blocks, the slice rank allows building blocks that are the tensor product of a 1-dimensional vector and a 2-dimensional matrix [cite: 6, 11]. Formally, a rank-one function in the context of slice rank is an element of the form $v_j \otimes_{j} M_{-j}$, where $v_j \in V_j$ and $M_{-j} \in \bigotimes_{i \neq j} V_i$ [cite: 11, 12]. 

The **slice rank** of a tensor $T$, denoted $\operatorname{srk}(T)$, is the smallest non-negative integer $r$ such that $T$ can be expressed as a linear combination of $r$ rank-one functions [cite: 11, 12]. Because any standard tensor of rank 1 also has a slice rank of 1, the slice rank of a tensor is always less than or equal to its standard tensor rank [cite: 6, 13].

### 2.2 Tao's Lemma for Diagonal Tensors
The core utility of the slice-rank method in combinatorics stems from a fundamental theorem regarding diagonal tensors, formulated by Tao. 

**Theorem (Tao's Lemma):** Let $A$ be a finite set and $\mathbb{F}$ be a field. Let $T : A^k \to \mathbb{F}$ be a tensor such that $T(x_1, x_2, \dots, x_k) \neq 0$ if and only if $x_1 = x_2 = \dots = x_k$. Then the slice rank of $T$ is exactly equal to the cardinality of the set, $|A|$ [cite: 9, 14].

This mirrors the analogous property in basic linear algebra where the rank of a diagonal matrix is equal to its number of non-zero entries [cite: 1, 15]. In applications, researchers construct a polynomial (tensor) $T$ that evaluates to zero on all $k$-tuples of a set $A$ that exhibit a certain forbidden property (e.g., an arithmetic progression), but is non-zero when the inputs are identical (the trivial progression). By proving an upper bound on the slice rank of $T$ (usually via polynomial degree arguments), one immediately obtains an upper bound on the size of the set $A$ [cite: 1, 9].

---

## 3. The Cap-Set Problem and Prime Fields ($\mathbb{F}_p$)

The most famous application of the slice-rank method is the cap-set problem, which asks for the maximum size of a subset of $\mathbb{F}_3^n$ that does not contain any 3-term arithmetic progressions (a "cap-set"). 

Using the polynomial formulation, Ellenberg and Gijswijt, and later Tao, proved that for primes $p \geq 3$, the size of a progression-free set in $\mathbb{F}_p^n$, denoted $r_3(\mathbb{F}_p^n)$, is strictly bounded by:
\[ r_3(\mathbb{F}_p^n) \leq (J(p)p)^n \]
where $J(p)$ is a decreasing function of $p$ [cite: 3, 14]. The precise value of the base constant is critical to the optimality of the method. It is known that $0.8414 \leq J(p) \leq 0.9184$, with $J(p)$ trending toward $0.8414 \dots$ as $p \to \infty$ [cite: 3, 14].

For $\mathbb{F}_3^n$, this yields an upper bound of approximately $2.756^n$, establishing that cap-sets are exponentially sparse [cite: 3, 4]. Behrend's classical construction provides a lower bound of $p^{1-o(1)}$ for $\mathbb{F}_p$, meaning $r_3(\mathbb{F}_p^n) \geq p^{(1-o(1))n}$, confirming that the slice-rank upper bounds are relatively tight and fundamentally optimal for single prime fields up to the specific constants [cite: 3].

---

## 4. The Frontier of Composite Moduli

While prime fields behave elegantly under algebraic methods due to the absence of zero divisors, analyzing progression-free sets over composite moduli (e.g., $\mathbb{Z}_m^n$ where $m$ is not prime) represents a massive leap in mathematical complexity.

### 4.1 The Roadblock of Composite Moduli
In the study of arithmetic circuits and computational complexity theory, prime vs. composite moduli is a well-known barrier. For instance, polynomial size bounded-depth circuits can easily compute the parity function if given modulo-$p$ gates for a prime $p$, but proving lower bounds for circuits equipped with modulo-$m$ gates where $m$ is composite (e.g., $\mathbb{Z}_6$) remains one of the greatest open problems in theoretical computer science [cite: 16]. 

Similarly, applying algebraic tensor methods to composite moduli is described as a challenge "reminiscent of a roadblock in circuit complexity" [cite: 16]. Because composite rings contain zero divisors, polynomials over these rings lack the pristine factorization and evaluation properties found over fields.

### 4.2 Croot, Lev, and Pach's Foundation on $\mathbb{Z}_4^n$
The genesis of this entire revolution actually occurred on a composite modulus: $\mathbb{Z}_4$. Croot, Lev, and Pach proved that any subset $A \subset \mathbb{Z}_4^n$ free of 3-term arithmetic progressions has a size bounded by $|A| < 4^{\gamma n}$ where $\gamma \approx 0.926$, yielding a bound of roughly $3.61^n$ to $3.62^n$ [cite: 10, 17]. Specifically, the bound is analytically presented as $|A| \leq 3.61 \dots ^n$ (or strictly $3.6108^n$) [cite: 3, 17].

This result showed that for $m=4$, the exponent is strictly less than 4, proving exponential sparsity. But generalizing this to all composite moduli requires intricate decompositions.

### 4.3 General Bounds for Arbitrary Composite Moduli $\mathbb{Z}_m^n$
For an arbitrary composite integer $m \geq 3$, researchers have successfully extended the core slice-rank logic, although the optimality of the bounds often degrades compared to prime fields. 

It has been established that for every $m \geq 3$, the size of a 3-term progression-free set $r_3(\mathbb{Z}_m^n)$ satisfies the upper bound:
\[ r_3(\mathbb{Z}_m^n) \leq (0.9184m)^n \]
[cite: 1]. 
This bound is fundamentally derived from the worst-case behavior of the $J(p)$ function over prime factors. Specifically, if $m$ is not a power of 2, and $p$ is an odd prime divisor of $m$, the bounds inherit the slice-rank constraints of the prime divisor [cite: 1]. 

#### The Case of $\mathbb{Z}_{15}^n$ and Open Questions
To illustrate the limits of the method's optimality on composite moduli, consider $m = 15$. By standard properties of direct products, one trivial upper bound is derived from its prime factors:
\[ r_3(\mathbb{Z}_{15}^n) \leq \min(3^n r_3(\mathbb{Z}_5^n), 5^n r_3(\mathbb{Z}_3^n)) \]
[cite: 17].
A major open question posed by researchers is whether this composite bound can be improved using a dedicated slice-rank approach directly on the composite space. Specifically, is it true that the asymptotic growth rate $\alpha_{3,15} < \min(3\alpha_{3,5}, 5\alpha_{3,3})$? [cite: 17]. Current iterations of the slice-rank method do not natively "see" the cross-interactions of the Chinese Remainder Theorem components efficiently enough to break this minimum bound trivially, indicating a limit to the method's raw structural optimality on mixed composites [cite: 17].

### 4.4 The Erdős-Ginzburg-Ziv Constant for Composite Groups
Another area where slice-rank interacts heavily with composite moduli is in bounding the Erdős-Ginzburg-Ziv (EGZ) constant, $s(A)$, for a finite abelian group $A$. The constant $s(A)$ is the smallest integer $\ell$ such that any sequence of length $\ell$ in $A$ contains a zero-sum subsequence of length equal to the exponent of $A$ [cite: 18, 19].

For groups of the form $A = (\mathbb{Z}_k)^n$, Harborth classically determined that for powers of two ($k = 2^a$), $s(A) = (k-1)2^n + 1$ [cite: 19]. 

For prime powers $p$, Naslund adapted Tao's slice-rank method to prove a breakthrough upper bound:
\[ s(\mathbb{F}_p^n) \leq (p-1)2^p \cdot (J(p)p)^n \]
where $0.8414 \leq J(p) \leq 0.9184$ [cite: 3]. 

To extend Naslund’s prime-based bounds to arbitrary composite numbers, researchers rely on structural inductions and conjectures, such as "Property D." Property D posits that every sequence over a group $A$ of length $s(A)-1$ lacking a zero-sum subsequence of length $k$ must take a highly structured form (specifically consisting of $k-1$ copies of some subset) [cite: 18, 19]. Assuming Property D holds for prime components, researchers have stitched together new exponential upper bounds for arbitrary composite abelian groups. However, the reliance on structural conjectures highlights that the pure algebraic slice-rank method requires external combinatorial scaffolding to maintain optimality when crossing from prime to composite regimes [cite: 18, 19].

---

## 5. Extensions: Partition Rank and Multi-Slice Rank

The original slice-rank method relies heavily on Tao's Lemma, which requires the underlying tensor to be strictly diagonal (i.e., $T(x_1, \dots, x_k) \neq 0 \iff x_1 = \dots = x_k$) [cite: 9, 14]. However, many combinatorial problems define forbidden configurations that are *not* strictly diagonal. To push beyond the boundaries of the original method, mathematicians generalized the rank definition.

### 5.1 The Partition Rank
Introduced to handle variables that must be distinct but not necessarily identical under evaluation, the **Partition Rank** is a broader generalization of the slice rank [cite: 8, 10]. 

While slice rank splits a tensor $T(x_1, \dots, x_k)$ into a sum of products of a 1-variable function and a $(k-1)$-variable function, the partition rank allows the tensor to be split according to any valid partition of the variables. For example, a tensor could be split as $T'(x_i) \cdot T''(x_1, \dots, x_{i-1}, x_{i+1}, \dots, x_k)$, which has a partition rank of 1, but it also allows splits into components like $f(x_1, x_2)g(x_3, x_4)$ for a 4-tensor [cite: 9].

This added flexibility is crucial for achieving optimality on complex geometric problems. For instance, the partition rank was successfully applied to bounding the size of sets $A \subset \mathbb{F}_q^n$ that avoid right angles (where three vectors $x, y, z$ form a right angle if $(x-y) \cdot (z-y) = 0$). By utilizing a "partition indicator" rather than a strict distinctness indicator, researchers substantially reduced the theoretical rank, proving that right-angle-free subsets are exponentially small, significantly improving earlier bounds [cite: 4, 8, 9]. 

Similarly, this methodology was used to prove that sets avoiding equilateral triangles in $(\mathbb{F}_q^n)^2$ are exponentially small, circumventing the need for diagonal tensor restrictions [cite: 14].

### 5.2 The Multi-Slice Rank
The **Multi-Slice Rank** is another variant introduced to capture finer arithmetic structures, notably extending a result of Tao and Sawin [cite: 20, 21]. This has found profound applications in analyzing exponential Diophantine equations and Fermat/Euler quotients.

By leveraging the multi-slice rank method, researchers successfully bounded specific subset capacities, demonstrating that:
\[ \mathfrak{s}(\mathbb{F}_p^n) \leq 3(p-1)p! (J(p)p)^n \]
[cite: 22].
The multi-slice rank provides an optimal theoretical bridge for applying analytic polynomial methods to number theory. It has been used in conjunction with the theory of Galois representations and modular forms to completely solve ternary Diophantine equations of the shape $Ax^n + By^n = Cz^3$ [cite: 22].

---

## 6. Limits of Optimality: Matrix Multiplication and Circuit Barriers

A crucial question in theoretical computer science is whether the slice-rank method can prove that the exponent of matrix multiplication, $\omega$, equals 2, or conversely, if slice-rank barriers prevent this. 

### 6.1 Matrix Multiplication and the Universal Method
Algebraic matrix multiplication algorithms rely on bounding the rank of matrix multiplication tensors and recursively applying them [cite: 16]. The current best theoretical bounds on $\omega$ rely on the laser method applied to Coppersmith-Winograd (CW) tensors, achieving $\omega < 2.37286$ [cite: 16].

Recent studies have analyzed the **asymptotic slice rank** of these tensors to determine the absolute limits of current methodologies. It was definitively proven that the "Universal Method"—a framework subsuming all known approaches to designing these algorithms over the last 30 years, including those utilizing CW tensors—cannot yield a bound on $\omega$ better than $2.16805$ [cite: 23]. 

This establishes a firm, quantifiable boundary on the optimality of the slice-rank paradigm in this subfield. The slice-rank barrier explicitly shows that any tensor with a low slice rank cannot be used successfully in the asymptotic sum inequality to push $\omega$ down to 2 [cite: 24].

### 6.2 Group-Theoretic Algorithms and Non-Abelian Moduli
Researchers have also attempted to use group-theoretic algorithms to achieve fast matrix multiplication. While abelian groups yield trivial bounds ($\omega \leq 3$), non-abelian groups offer more promise [cite: 16].

However, the slice-rank method again reveals structural roadblocks. For example, in the group $G = \text{PSL}(2,p)$, the largest multiplicative 3-matching is bounded by $O(p^{8/3})$ [cite: 16]. Yet, the slice rank of the group algebra's multiplication tensor is at least $\Omega(p^3)$ over any field [cite: 16]. This massive discrepancy between the size of the 3-matching and the slice rank indicates that for highly mixing, non-abelian composite structures, the slice-rank method does not tightly correlate with the matching size, failing to yield the optimal bounds necessary to revolutionize $\omega$ [cite: 16].

---

## 7. Limits of Optimality: Coding Theory and Trifferent Codes

The slice-rank method's limits of optimality are perhaps most starkly visible in the study of **trifferent codes** (also known as 3-hash codes). A trifferent code $C \subseteq \{0,1,2\}^n$ has the property that for any three distinct codewords, there exists a coordinate where they all differ [cite: 25].

The central problem is to determine $T(n)$, the maximum size of a trifferent code of length $n$. 
*   The classical upper bound, via a relatively simple probabilistic pruning argument by Elias, is $T(n) \leq 2 \times (3/2)^n$ [cite: 25].
*   The lower bound by Körner and Marton is $T(n) \geq (9/5)^{n/4}$ [cite: 25].

When the slice-rank method emerged, researchers hypothesized it could drastically lower the upper bound for $T(n)$, just as it had for the cap-set problem. However, Costa and Dalai explicitly demonstrated the limits of the slice-rank method for the trifference problem [cite: 25]. While the method brilliantly bounds 3-AP free sets in $\mathbb{F}_3^n$, it structurally fails to improve upon the $O((3/2)^n)$ bound for general trifferent codes [cite: 25, 26]. 

Improvements have only been found under strict conditions:
1.  **Linear Trifferent Codes:** If the code is restricted to be a linear subspace of $\mathbb{F}_3^n$, the upper bound can be dropped to roughly $3^{0.3483n}$ (Bishnoi, D'haeseleer, Gijswijt, and Potukuchi) [cite: 25, 27].
2.  **Low-Length Computer Searches:** Using exact optimized search algorithms and number-theoretic arguments, Fiore, Gnutti, and Polak showed $T(n) \leq 1.09 \times (3/2)^n$ for $n \geq 12$ [cite: 25].

The inability of the pure slice-rank method to break the $(3/2)^n$ barrier for arbitrary non-linear trifferent codes serves as a canonical example of its boundaries. The tensor representing the trifference property does not possess a slice rank significantly lower than the trivial bounds, forcing researchers to rely on probabilistic methods, Lovász Local Lemma, and expurgation methods to study these combinatorial structures [cite: 26].

---

## 8. Algorithmic and Computational Complexity of Slice Rank

Finally, the optimality of the slice-rank method can be viewed through the lens of computational complexity. Is it possible to efficiently calculate the slice rank to automatically derive optimal bounds for arbitrary combinatorial problems?

The answer is overwhelmingly negative. Determining the slice rank of a given 3-tensor is deeply connected to the orbit closure containment problem and the null cone problem in geometric complexity theory [cite: 6, 12]. 

Specifically, computing whether the slice rank of a given tensor $T \in \mathbb{F}^n \otimes \mathbb{F}^n \otimes \mathbb{F}^n$ is at most $r$ is **NP-hard** [cite: 11, 12]. This was proven by reducing the problem to finding the minimum vertex cover of a 3-uniform, 3-partite hypergraph [cite: 11]. Tao and Sawin demonstrated that for every such hypergraph whose edge set forms an antichain, the slice rank of the associated tensor equals the size of the minimum vertex cover [cite: 11]. 

Because calculating the slice rank is NP-hard, mathematicians cannot rely on algorithmic assistance to evaluate the tensors generated by new combinatorial problems. Instead, finding optimal upper bounds relies entirely on human ingenuity to identify clever polynomial decompositions or to invent new rank variants (like partition rank) that neatly align with the problem's geometric structure [cite: 9, 12].

---

## 9. Conclusion

The slice-rank method represents one of the most profound paradigm shifts in modern extremal combinatorics. By abstracting the Croot-Lev-Pach polynomial method into a symmetric tensor property, it cleanly resolved the cap-set problem and revolutionized our understanding of progression-free sets over prime fields.

However, as the methodology has been pushed beyond $\mathbb{F}_3$ and into the realm of composite moduli ($\mathbb{Z}_m^n$), non-abelian groups, and off-diagonal geometric constraints, its theoretical limits have come sharply into focus. The structural properties of composite moduli—specifically the presence of zero divisors—introduce severe roadblocks. While worst-case bounds like $r_3(\mathbb{Z}_m^n) \leq (0.9184m)^n$ have been established, optimizing these bounds for specific mixed composites like $\mathbb{Z}_{15}^n$ remains an open challenge.

Furthermore, definitive impossibility results now map the boundaries of the method's optimality. In theoretical computer science, the asymptotic slice rank guarantees that the Universal Method for matrix multiplication cannot beat an exponent of $2.16805$. In coding theory, the slice-rank method cannot meaningfully improve the upper bounds for non-linear trifferent codes beyond Elias's probabilistic bounds.

To transcend these limitations, the mathematical community is actively developing generalized frameworks, such as the partition rank and the multi-slice rank. These newer methods sacrifice some of the elegant simplicity of the original slice-rank theorem to gain the flexibility required to tackle complex, off-diagonal, and composite-modulus problems, ensuring that the legacy of the polynomial method will continue to expand into new domains of mathematics.

**Sources:**
1. [mtak.hu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtXpm2NE8OsUA2vHovyMw8haFG2GL2AYDqcALJbgRVatHQ7g6Xd_jz3qjI1StucU8X61lw4F6yg-FpeeT-n3mSsbaeCa_N91ypJlVxY-Jr4B80VzNAtTpMRRZ_NSn9yzu_mMIR9h_gqVyN7SwdYWg=)
2. [renyi.hu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3zmMiWNhQ0-AOh5sXLXIHTeZ0PQuu08JqG8bXDxxVXKE3UysFwE_Q0d49dSyQ5nwouS1B5pC1-yHQNyJfoAOo9W8t9BoVxUkYWpUeC_6scwYEyOvvdzVSbfbe1c_5Wxt9dP_Yhg5ju7Zb1N5H1lJmXnzLbmgyDGocMatkDQ==)
3. [combinatorics.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHr_7M4twVBXpES5SA8caBCp0SZuQvdnw9jhl5ozpHZ185TOoOv1y03HkorRQ3-T1Pk4LRlizaMmiwQr_fLBqUg2hnomRjh62OIjE-49ar5yOGkPbezsQtMIDQW571_xpBIFezhLk0N89aFnlfgra3qSo7SONqYoTvwQ7ebHvCJpw==)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkkuNuyoJ0HEc5i1nFlslTWbSWCmboQxPpvoFOyUUdt6mG2pOzEP1ejpxxHMFeutfLrAa6uWDIP8rynnf6ShHrDjbFu76R9ZYI4297zcThgILA8KvaZ0Oq6L79GoBNw1KfqoO_Yajqp_Og8NRuSBdt6cXJJvcGV4KXfuDRULi--IweG2cBXH66dInRbVTj7fxArmokAmUWytMGcZ2pD8P5Jn9DGqMoI6BwFQRYdt42L1zBow==)
5. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGONJbK_mt7NpGyE1LgfolPkZ82UhNgP6rgBsYYPF9Bkmh2pJql6JotnHKGh8T_Jn30_5rrLnZEe0wHWrOkIK4YS445UiPjADbN8Ft7M0AksfQcZIuu1r5f0PTHYSZNbKYpLEkacBcq4f-kRHlDa3iK8NMHfTa4Klf-e-lN5ULdSV5c5Q==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFX6vtpeCa-KCIWtWoa93hRxrLLk2vDM1891_PNKsszEDLxAwO412ZMFygo5oGGeyuVD44gLZFkgCQPKcd-2xRq9n9xJdVKGCAUTzT828W0zz_wF0g9)
7. [unito.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoIQzwVU4dTzr80gagm-r80bpRC9KP6GVBrboGl89zqlxu91Edj2tLRYiGBJzH8XlMcKLNoFxGvV5n3jPWN5_bN-cX2mdrpQZjD_eOLB1oCwX697ZTd2WhayoUhxraSDMvHf81CfKLbjPGTJm9uASbLuQ=)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0ZmjpBc8geUP2itV3IAOI_PkkH63M0NNwopCigxDF_EP8YitA6xoucLtjxaO9Ol3FNDYBW0lfXZi-RS90-TvFCPYOjfnQJ-Q3Ryj3B5aWpxscI_OhoNLtyvblqDC7NcUSwcXpsGfW_m2FeZ7aWiiZyd37oa45PnwvWS3zC4bpmPs3jU3pgjRWwHlaBRtGyA==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFa1qY_Tit130_0dfPooVG0SX_NCDAoLWmJaNXIP0eiL06C05Xt34bNqh3srks_Z7VPzsdUrfrkqKUEknkRnI5dhBGneA9iMaI8gsDqoNZxcNVDVPX5)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcuIi5g4tx5Wc7xUv0JQX3PaaVIcakYmNI5mdtTSdxOamQdRAEw-Lvyk9O8m8GHa3W4bxeAVj4vDPdwgK9i9KqWVXtK3xAO_Lhk9EEAtfEMo9aZyBUrLtTXFl4EIcQI30zaBsG3kdgHAdx6-QYqdepGaFhfX6aJlBTs_3kBqPBYjLASeEF0xs392tRCD4r4Qz6mPUOc-TZfsxhHOnz03gY09c5DSA=)
11. [liverpool.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXVzrkQ0AVEdFnx7mq7gKYR6M-gvWqQl_0SHVInRFAQR0NhUvKx23zhexnDFLhs9h2kb4dC0gW7_N4HRndQjZmbaFUV_zK3oaR-m3BM3TutjtyLxp7Y-EvAPq-qAV1C8rOSJtIycfiR-ckZs55WQ==)
12. [uni-saarland.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpbkl2o7KHGh3R_jj_cKMTwpYU5PuCSHKRGeLg8B4qAsxm8MEs9Ecq9TFsvwNV31c7W1m5J6BLy5wI5YYDt_ObFFO24Wr5aFrKFP-L5TDeOS5bclXBgCaAk6OkLAjAVPEn5agC7KejC1JYpZ5rTyxhiyvpdMS4xmWXI2IuZp0gjY6CWfP6N2wp2HIkdndz3_XlmVbKCZ2P)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlkBSJadJih4363nvKcbujEyF8tgo7GEGSnmAk36ZbyPWKlH8Da6AgYnnSI3u9fOKlJEplxaIbw7YK4WwCndIKELn7DDAS2JrGQxUX16rM7ZhQ6OEMS-905vf0WW_aRcWuF4nd9fKQZ_zL7B0JJnGIooJ5JYYjh2VhO325Es-ogZbwM3LOgw==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5NqLVvqNc9OzC591Kg8BEQLMA3VIColZgEIl2YbJzHoFRyC0PBn94V2Ut0Y30X-84ZouZK-7zYI2ZvIw2dkkarTbJVEAIEDEUggYFrz677zImt0tD)
15. [theoryofnumbers.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMVzSkNfed3j6Cxc9lw1_kYQNr2s9DeErv1QXI92xskSUHypFg0O4VP73RT4-sS6fkQP9L3BSa6-FZwTU253cZ1wLQDJUfCsDqFo5dZvqPFQTh1GdagfcQE6gHZKfRJM0M82kvwjImfKXlGrjoPksv)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELSwE0_alBstMEBNkOPpMSs2RfFCezJUPiCF7PgHhaqWGQWY6VO-egrFtztIVAdCwdbC4rLAGf4C1raeoYuFXieYOp0ObNgJMtE9Z-qacTDEWxF_cgMkBsJhZ7M1wDZxlOjnF5bViOiuZe7sCzWRq9V_CpwMTmzOOw6e0PcZ3_pnsKCy1Fq0KhWAL3u6Mu5QNK92lWvowE6RT7)
17. [bme.hu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbiibqSzX560hB8Ufhi9iRHlx9PwHFs2k5w9-0DRO6E4BWSvpF0f2KHwSdk4ur9qaxYRBah0A8XKehNbGcd9jhZQudk-KNsw3WgnuJKgnrjC9Q93xd5cpTusUt7yCWUptgAWZLUg==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1CQT07qk_emh4ddkkX7nQCoZUmavuPHbtaNul4EX1Cki9h3mJGJoY2YlFZaPBA34GG3_dstxmF0IXlaySA_LR5A8GY7rbfA7FTwRwAZapMQycb_hq)
19. [colgate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIjZ1Q9P83jx5gV1bgWU0nMn4Nn6acAxx62nf1L0eXLD180HNvFxI5LVo45WUETC9QWD_9t4xbUpgTfM5X3mOkbuBWYoPfcSy3N8xApwIv8Z2yks27bUUmtt0rHYzVQaEek88=)
20. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzExsAqNXAsaY1f7glJd9Vz_VDSrGBZX_Zudsq1KlAqzt9DGCCgDTPjv21rPq-JBJBs2GHQpShZoevKJ3OtpNv-EcwouKoPF5_Z6H8OaYEX1lpDWAn762mk3JuhoGuXV74_e3VLYA4AUg7R1MTTlaN-Mva2RCahQ7jzfA3HuS_DaWaMXUjZNZTvgB_HYgN6AEoF9dUq2nSozZYEm7yv9ehOOG-EBDvNWQJfq3IBfUSANCCeV3y6Y_OlwdrpthByBH2FDI-A7-Y23WRGLvw)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExUNCkVpRw1gPziCZsUShD9u3OpvfhX7FEL7YtQ07mbSmjP9xGZjbCWZEXuA8JjguOd6YLwBVWVrm-6SXMvdYx7Qg6NRu3gsRb8WoacqJO1mypRqYCKwSihUbwxs2MJEY-d5W9-nDNGF8ppnQLUz8cK24DbmmyVHamEoreAl_DmblUPWvN_P1oOwlrK7yc48NJcvrC)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrcL1p_NvemADlc1ReV5gX2uXzS0IKiEwXAjgL6DuJ-ORCFqG-gqH5N7OHcSiS8-gk1N_CACCXP9cVQRgdF_zeC7ifjF3H-Yo0K8b_X5gOKVsYiPtJ35HojNiV_SXcXa3vv4IN97opQDywXtJPipH1Nd6PSOVGSh6HdUpdG-3Ycn9r9A0xIZBUOZ33Rk0SwlXTRqEpyDh8shtgsB5fFcduJVXL4QdG1wiPgA==)
23. [northeastern.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDcpvr3C562xeIQUX6LjGWQFaHXRzPp1bRmbKUqlESzb5keH_ePw9TsFlpxGkcyXrQhb6tNIvoCnZGnj0GDbYvRxLU7TGgaKCQ4UOp465xioj6YhHfrErGQ9a6-hmbHILSR2vUHiOpjA==)
24. [cmu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhBlL0iugwcUyo5qgR9P5ssTeIq6_QufDj_kDV2zUARC7hrWDb4zMYGlJEsAIdTKYPUVqxR3Gh3I2xwbTdIL8qN4fVZYgJN9tp9m3yZZlEA6IZl3sZWNyUyZKF8iINmJP1mk5loY8oU5XU0vqva_msK6YHhGaV)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_vy6HkzS5RaRa5TOaLb2ED-h4tBHph72vdsAltlx6ZAC76mxNYlAp63iITWje8vzTvBzc58IlmySWMbtpIFNLdpSFH-HQr8ejBntld04Z-tA_s4LB)
26. [unibs.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLZnRRLIc7d1ULAXADXZ063fURFXC00_yuTEJlXA6FNU7mwHj1GKJv59-lwp0vwvarxBKKflVp2jxQWoZgE4uduq7WgZVcaw0YvDCpGYhkwo9b-Q1eRLFXv2qHYpxmZFrOI0M0Ig0d7q0QRhAPFfGkUQ==)
27. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4DmxgbGSxUE3YdVRtMhc20crtVZ5cFTkeBneC2PjqkmN5S9TaEDqWqiZPa9-ZUe6xEv7CIK0QbMBXQLlVxUzMPQFEGr6yu7IqtkP77JESoR1DeR3pzGQHQA==)

