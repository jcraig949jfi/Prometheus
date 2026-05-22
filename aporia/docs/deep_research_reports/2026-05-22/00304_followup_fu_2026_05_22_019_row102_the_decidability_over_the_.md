# Followup [FU-2026-05-22-019 <- row102]: The decidability over the rational numbers ($\mathbb{Q}$) remains an important open question. *   **

**Pythia queue id:** 304
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdyYk1QYXRxbEZyR1pfdU1QdkxtS2tRcxIXcmJNUGF0cWxGckdaX3VNUHZMbUtrUXM
**Elapsed:** 250s
**Completed at:** 2026-05-22T01:43:04.235081+00:00

---

# Status Update: Decidability of Tensor Rank over the Rational Numbers

**Key Points**
*   The exact computation of tensor rank over the rational numbers \(\mathbb{Q}\) is an outstanding open question in computational complexity and algebraic geometry, currently unknown to be decidable [cite: 1, 2].
*   The tensor rank problem over \(\mathbb{Q}\) has been proven to be polynomial-time equivalent to the Existential Theory of the Rationals (\(\exists\mathbb{Q}\)), meaning a decidability result for one implies decidability for the other [cite: 3, 4].
*   While tensor rank over the real numbers (\(\mathbb{R}\)) is decidable and complete for the Existential Theory of the Reals (\(\exists\mathbb{R}\)) [cite: 5, 6], the \(\mathbb{Q}\)-variant borders on the undecidability of Hilbert's 10th problem [cite: 7, 8].
*   Current consensus strongly leans toward the problem being undecidable, heavily relying on the conjecture that \(\mathbb{Z}\) is existentially definable in \(\mathbb{Q}\) [cite: 9, 10].
*   Algorithmic solutions for tensor rank over \(\mathbb{Q}\) are restricted to fixed-parameter tractable (FPT) algorithms for constant rank when operated in algebraically closed extensions, but exact rank determination over \(\mathbb{Q}\) itself remains elusive [cite: 11, 12].

**Contextual Overview**
The transition from matrix rank (a computationally trivial problem in \(\mathbf{P}\)) to tensor rank represents a massive leap in complexity [cite: 13, 14]. Matrices (2-tensors) benefit from standard linear algebra paradigms, such as Gaussian elimination and the Singular Value Decomposition (SVD), which provide canonical, easily computable bases [cite: 13, 15]. Higher-order tensors (order 3 and above) entirely lack these universal properties. Rank computation becomes highly sensitive to the underlying field of scalars [cite: 1, 3]. The decidability of this problem specifically over the rational numbers \(\mathbb{Q}\) touches the absolute frontier of logic, algebraic geometry, and computer science, directly interrogating the boundary between continuous decidable domains (like \(\mathbb{R}\) and \(\mathbb{C}\)) and discrete undecidable domains (like \(\mathbb{Z}\)) [cite: 7, 16]. 

**Scope of the Report**
This report synthesizes current bounds, historical breakthroughs, and active attack vectors surrounding the decidability of tensor rank over \(\mathbb{Q}\). It evaluates the transition from Håstad's foundational \(\mathbf{NP}\)-hardness proofs to Shitov's and Schaefer-Štefankovič's exact polynomial equivalences with algebraic systems. Furthermore, it outlines how this single question serves as a keystone for broader inquiries into circuit lower bounds, machine learning tensor decompositions, and Diophantine logic.

## 1. Brief Summary

**The open question, contextualized for Prometheus:** 
*Is the problem of computing the exact tensor rank of a multi-dimensional array over the rational numbers (\(\mathbb{Q}\)) algorithmically decidable, or is it fundamentally uncomputable (equivalent to the halting problem), akin to Hilbert's 10th problem over \(\mathbb{Z}\)?*

Within the framework of the Prometheus architecture and previous Aporia deep research reports, this question serves as a central anchor for understanding the algorithmic limits of multi-linear algebra [cite: 4, 17]. While prior reports have successfully mapped out the decidable fragments of tensor theory via quantifier elimination over real closed fields (demonstrating that tensor rank over \(\mathbb{R}\) is bounded within \(\exists\mathbb{R} \subseteq \mathbf{PSPACE}\)) [cite: 1, 18], the rational numbers present a much more hostile algorithmic environment. The fraction field \(\mathbb{Q}\) introduces profound Diophantine obstructions [cite: 8, 19]. Determining if a tensor possesses a specific rank over \(\mathbb{Q}\) demands a deep synthesis of computational logic and arithmetic geometry, testing whether existential variables ranging over fractions can encode universal Turing machines [cite: 10, 20].

## 2. Flagged Findings

### 2.1 Current Consensus: Expected Undecidability
The prevailing consensus among complexity theorists and algebraic geometers is that computing the exact tensor rank over the rational numbers \(\mathbb{Q}\) is **undecidable** [cite: 2, 9, 11, 12]. This belief is rooted in the proven polynomial-time equivalence between computing tensor rank over an integral domain and solving arbitrary systems of polynomial equations over that same domain [cite: 5, 16, 21]. Specifically, for the rational numbers, determining tensor rank is exactly as hard as the Existential Theory of the Rationals (\(\exists\mathbb{Q}\)) [cite: 3, 4]. 

Because the existential theory of the integers (\(\exists\mathbb{Z}\)) is famously undecidable (Matiyasevich's theorem resolving Hilbert's 10th problem [cite: 7, 8]), if one can formulate an existential definition of \(\mathbb{Z}\) inside \(\mathbb{Q}\), then \(\exists\mathbb{Q}\) would trivially inherit this undecidability [cite: 7, 10]. Poonen has already demonstrated that the \(\forall\exists\)-theory of \(\mathbb{Q}\) is undecidable by constructing a universal-existential definition of the integers in the rationals [cite: 4, 22]. The step to a purely existential definition is widely anticipated to be true, making the undecidability of tensor rank over \(\mathbb{Q}\) a strongly held conjecture [cite: 3, 5].

### 2.2 Points of Friction and Where the Consensus Might Be Wrong
Despite the strong consensus, the undecidability of \(\exists\mathbb{Q}\) (and thereby tensor rank over \(\mathbb{Q}\)) remains strictly unproven. There are significant algebraic barriers that could invalidate the consensus:
*   **The Mazur Conjecture Barrier:** Barry Mazur's conjectures regarding the topology of rational points on varieties suggest that the topological closure of any Diophantine set in \(\mathbb{R}\) should have at most finitely many connected components. If Mazur's conjecture holds, it would mathematically forbid an existential definition of \(\mathbb{Z}\) in \(\mathbb{Q}\) (because \(\mathbb{Z}\) has infinitely many connected components in the real topology), thus severing the most obvious reduction path from Hilbert's 10th problem to \(\exists\mathbb{Q}\) [cite: 7, 10]. 
*   **PATTERN_BASE_RATE_NEGLECT:** In extrapolating the complexity of \(\mathbb{Q}\), researchers frequently fall victim to **PATTERN_BASE_RATE_NEGLECT**. There is a tendency to assume that because polynomial systems over \(\mathbb{Z}\) are undecidable, and \(\mathbb{Z}\) is a subset of \(\mathbb{Q}\), the hardness inherently translates upwards. However, the base rate of decidability for fraction fields (like \(\mathbb{R}\) or \(\mathbb{C}\), which are decidable via Tarski-Seidenberg and Gröbner bases, respectively) is often ignored [cite: 8, 23]. \(\mathbb{Q}\) possesses unique local-global properties (like the Hasse principle for quadratic forms) that \(\mathbb{Z}\) lacks, which could theoretically allow for an undiscovered, highly complex but finite decision procedure for \(\exists\mathbb{Q}\) [cite: 7].
*   **Constant Rank Decidability:** While the exact computation for variable rank is heavily suspected to be undecidable, it is not definitively established that the problem remains undecidable for small, fixed constants. Recent randomized polynomial-time algorithms successfully decompose constant-rank tensors over algebraically closed fields and \(\mathbb{R}\) [cite: 9, 12]. If \(\exists\mathbb{Q}\) is decidable, it would likely be due to advanced techniques in algebraic geometry providing upper bounds on the search space for rational points on the specific varieties generated by the tensor decomposition constraints.

## 3. Problem Statement

### 3.1 Precise Object Being Interrogated
A tensor is a multi-dimensional array of elements selected from a field \(\mathbb{F}\) (or a commutative ring). While vectors are 1-tensors and matrices are 2-tensors, the primary object of complexity-theoretic interest is the 3-tensor (or order-3 tensor), denoted as \(T \in \mathbb{F}^{n_1 \times n_2 \times n_3}\) [cite: 9, 24].

A tensor \(T\) is said to have **rank 1** if it can be expressed as the outer product (Kronecker product) of three vectors:
\[ T = u \otimes v \otimes w \]
where \(u \in \mathbb{F}^{n_1}\), \(v \in \mathbb{F}^{n_2}\), and \(w \in \mathbb{F}^{n_3}\) [cite: 9, 15, 24]. Consequently, the entries of \(T\) are defined as \(T_{ijk} = u_i v_j w_k\) [cite: 3, 24].

The **tensor rank** (or CP-rank, canonical polyadic rank) of a general tensor \(T\), denoted \(r(T)\), is defined as the minimum integer \(k\) such that \(T\) can be expressed as the sum of \(k\) rank-1 tensors [cite: 1, 9, 25].
\[ r(T) = \min \left\{ k \;\middle|\; T = \sum_{i=1}^k u_i \otimes v_i \otimes w_i \right\} \]

The open question asks: **Given a 3-tensor \(T\) with elements in \(\mathbb{Q}\) and an integer \(r\), does there exist a Turing-computable function (an algorithm) that decides in finite time whether \(r(T) \leq r\) over the field \(\mathbb{Q}\)?** [cite: 8, 19].

### 3.2 Field Dependence and Anomaly Substrates
Unlike matrix rank, which is invariant under field extensions (the rank of a matrix with rational entries is the same whether viewed over \(\mathbb{Q}\), \(\mathbb{R}\), or \(\mathbb{C}\)), tensor rank is highly sensitive to the underlying scalar field [cite: 1, 3]. 

Consider the canonical example modifying Kruskal (1989), involving a 3-tensor of shape \(2 \times 2 \times 2\). Let \(\{x, y\}\) be a basis for a 2-dimensional vector space. The tensor:
\[ T = 2x \otimes x \otimes x + x \otimes y \otimes y + y \otimes x \otimes y + y \otimes y \otimes x \]
possesses a rank of exactly 2 over the real numbers \(\mathbb{R}\). However, over the rational numbers \(\mathbb{Q}\), its rank is strictly greater than 2 (it requires 3 rank-one tensors over \(\mathbb{Q}\) to represent) [cite: 1, 3]. 

This divergence is what isolates the \(\mathbb{Q}\)-decidability problem. If a tensor's rank over \(\mathbb{Q}\) were guaranteed to equal its rank over \(\mathbb{R}\), the problem would trivially fall into \(\mathbf{PSPACE}\) via the Existential Theory of the Reals [cite: 1, 18]. Because tensor rank over \(\mathbb{Q}\) can be strictly higher and demands rational coefficients for the decomposing vectors \(u_i, v_i, w_i\), the problem forces algorithms to search for rational points on algebraic varieties [cite: 8, 10]. 

### 3.3 Border Rank and Symmetric Rank
The problem is adjacent to two other notorious tensor formulations:
1.  **Border Rank:** The smallest number of rank-1 tensors needed to approximate a tensor \(T\) arbitrarily well [cite: 6, 25]. Over \(\mathbb{Q}\), this involves a topological closure that complicates algebraic formulations. 
2.  **Symmetric Rank:** When the tensor \(T\) is symmetric (invariant under permutation of indices), we can ask for the minimal \(k\) such that \(T = \sum_{i=1}^k v_i \otimes v_i \otimes v_i\). Computing the symmetric rank of a rational tensor is similarly known to be \(\mathbf{NP}\)-hard (confirming a conjecture of Hillar and Lim) and is subject to the identical decidability questions as general tensor rank [cite: 5, 9, 13, 16, 21].

## 4. Status & Bounds

### 4.1 Last Known Status
The exact decidability of tensor rank over \(\mathbb{Q}\) remains unproven, effectively stalled at the barrier of \(\exists\mathbb{Q}\) [cite: 3, 4]. 
*   **Over finite fields (\(\mathbb{F}_q\)):** \(\mathbf{NP}\)-complete. The search space is bounded, making decidability trivial [cite: 14, 15, 26].
*   **Over the reals (\(\mathbb{R}\)):** Decidable, \(\exists\mathbb{R}\)-complete (implies \(\mathbf{NP}\)-hard and contained in \(\mathbf{PSPACE}\)) [cite: 5, 6].
*   **Over the integers (\(\mathbb{Z}\)):** Undecidable. Proved by Shitov (2016), answering a 1980 question by Gonzalez and Ja'Ja' [cite: 5, 16, 17, 21].
*   **Over the rationals (\(\mathbb{Q}\)):** \(\mathbf{NP}\)-hard [cite: 15, 26]. Equivalence to \(\exists\mathbb{Q}\) established [cite: 3, 4]. **Decidability is open** [cite: 1, 2, 3, 22].

### 4.2 Best Known Bounds and Complexity Reductions

#### 4.2.1 \(\mathbf{NP}\)-Hardness Lower Bound
The baseline computational hardness was established by Johan Håstad in 1990 [cite: 14, 15, 26]. Håstad demonstrated that tensor rank is \(\mathbf{NP}\)-hard over \(\mathbb{Q}\) by constructing an ingenious reduction from 3-SAT. 
Given a Boolean formula with \(n\) variables and \(m\) clauses, Håstad constructed a tensor \(T\) of dimensions \((2+n+2m) \times 3n \times (3n+m)\) [cite: 15]. The 3-slices of this tensor map to variable matrices, help matrices, and clause matrices. Håstad proved that the Boolean formula is satisfiable if and only if the tensor \(T\) has rank exactly \(4n + 2m\) over the underlying field. This established the definitive \(\mathbf{NP}\)-hard floor for \(\mathbb{Q}\) [cite: 15].

#### 4.2.2 Hardness of Approximation
Not only is the exact computation \(\mathbf{NP}\)-hard, but the problem also vehemently resists approximation. A breakthrough by Swernofsky (2018), simplifying and re-analyzing Håstad's reduction, proved that it is \(\mathbf{NP}\)-hard to approximate the rank of a 3-tensor over any field within a factor of \(1 + 1/1852 - \delta\) for any \(\delta > 0\) [cite: 17, 26, 27]. This bounds the effectiveness of heuristic tensor decomposition algorithms used in machine learning (like ALS - Alternating Least Squares) [cite: 2, 27].

#### 4.2.3 Equivalence to \(\exists\mathbb{Q}\)
The exact upper bound for the problem was sharpened significantly in 2016 by two independent sets of researchers: Yaroslav Shitov [cite: 5, 16, 21], and Marcus Schaefer & Daniel Štefankovič [cite: 3, 17].
Shitov proved that for any integral domain \(R\), the computation of tensor rank over \(R\) is polynomial-time equivalent to the solvability of an arbitrary system of polynomial equations over \(R\) [cite: 5, 21]. 
Simultaneously, Schaefer and Štefankovič proved an "algebraic universality" result: determining the rank of a tensor over a field \(\mathbb{F}\) has the identical computational complexity as deciding the existential theory of that field, \(\text{ETh}(\mathbb{F})\) [cite: 3, 4]. 

This locks the complexity of tensor rank over \(\mathbb{Q}\) precisely to the class \(\exists\mathbb{Q}\) [cite: 3, 22]. Consequently, any algorithm that can compute tensor rank over \(\mathbb{Q}\) can be used to solve arbitrary Diophantine equations over the rationals [cite: 5, 22]. 

#### 4.2.4 Fixed-Parameter Tractable (FPT) Algorithms
For highly restricted cases, specifically when the rank \(k\) is a fixed constant, progress has been made. Randomized polynomial-time algorithms running in \(k^{O(k)} \text{poly}(n, d)\) time have been developed to compute tensor rank and output the optimal decomposition [cite: 9, 11, 12]. However, these algorithms heavily depend on the field being algebraically closed (like \(\mathbb{C}\)) or utilize real algebraic geometry (for \(\mathbb{R}\)) [cite: 12]. Over \(\mathbb{Q}\), determining exact constant rank is *still* not known to be decidable [cite: 2, 11, 12]. If an algorithm is executed over \(\mathbb{Q}\), it often defaults to finding decompositions in extension fields, failing to guarantee rational vectors [cite: 12].

## 5. Literature (Primary Sources)

The body of primary literature establishing the formal constraints of tensor rank over \(\mathbb{Q}\) is heavily centralized among a few seminal papers in theoretical computer science and algebraic geometry.

| Reference | Authors | Year | Key Finding / Contribution | Venue / Status |
| :--- | :--- | :--- | :--- | :--- |
| **[cite: 15, 26]** | Johan Håstad | 1990 | Proved tensor rank is \(\mathbf{NP}\)-complete over finite fields and \(\mathbf{NP}\)-hard over \(\mathbb{Q}\) via a reduction from 3-SAT. Foundational paper of the field. | *Journal of Algorithms*, 11(4) |
| **[cite: 13, 19]** | Christopher J. Hillar, Lek-Heng Lim | 2013 | Extended Håstad's \(\mathbf{NP}\)-hardness to \(\mathbb{R}\) and \(\mathbb{C}\). Formalized that most tensor problems (eigenvalues, best rank-1 approximation) are \(\mathbf{NP}\)-hard. Conjectured symmetric rank is \(\mathbf{NP}\)-hard over \(\mathbb{Q}\). | *Journal of the ACM*, 60(6) |
| **[cite: 5, 16]** | Yaroslav Shitov | 2016 | Proved tensor rank over an integral domain \(R\) is polynomial-time equivalent to solving polynomial equations over \(R\). Resolved Gonzalez/Ja'Ja' question proving tensor rank over \(\mathbb{Z}\) is undecidable. Proved symmetric rank is \(\mathbf{NP}\)-hard over \(\mathbb{Q}\). | arXiv:1611.01559 |
| **[cite: 3, 17]** | Marcus Schaefer, Daniel Štefankovič | 2016/2018 | Proved tensor rank over field \(\mathbb{F}\) is complete for \(\exists\mathbb{F}\). Demonstrated algebraic universality. Explicitly flagged \(\exists\mathbb{Q}\) equivalence and its open decidability status. | *Theory of Computing Systems*, 62(5) |
| **[cite: 27]** | Joseph Swernofsky | 2018 | Proved \(\mathbf{NP}\)-hardness of approximating 3-tensor rank within a factor of \(1 + 1/1852 - \delta\) over any field. | *APPROX-RANDOM* |
| **[cite: 9, 12]** | Vishwas Bhargava, Devansh Shringi | 2021 | Provided the first randomized polynomial-time algorithms for computing constant tensor rank over \(\mathbb{R}\) and \(\mathbb{C}\), highlighting the extreme sensitivity to the underlying field (notably failing over \(\mathbb{Q}\)). | arXiv:2105.01751 |
| **[cite: 6]** | Tillmann Miltzow, et al. | 2024 | Comprehensive compendium of \(\exists\mathbb{R}\)-complete problems, sharply defining the boundaries between \(\exists\mathbb{R}\) and \(\exists\mathbb{Q}\) and citing tensor rank variants. | arXiv:2407.18006 / *UU Portal* |

## 6. Attack Vectors

### 6.1 Exhausted Approaches and Failed Primitives

#### 6.1.1 Flattening and Linearization
The primary classical tool for decomposing tensors is "flattening" (or matricization), which reshapes a 3-tensor of dimensions \(n_1 \times n_2 \times n_3\) into a matrix of dimensions \(n_1 \times (n_2 n_3)\) [cite: 24]. If a tensor has rank \(r\), its flattened matrix will have a rank of at most \(r\). For low ranks (\(r \leq n\)), techniques like Jennrich's algorithm (simultaneous diagonalization) succeed [cite: 24]. Advanced flattenings, such as Koszul-Young flattenings, push the boundary to rank \(r \leq (2-\epsilon)n\) [cite: 24]. 
However, **flattening is categorically exhausted for determining exact arbitrary rank over \(\mathbb{Q}\)**. Flattening inherently relies on finding eigenvalues and eigenvectors. Over \(\mathbb{Q}\), the characteristic polynomial of a matrix rarely splits completely; eigenvalues fall into algebraic extension fields (e.g., \(\mathbb{Q}(\sqrt{2})\)). This induces **PATTERN_RANK_PARITY_LEAK**, where the algebraic nature of the decomposition leaks out of the base field \(\mathbb{Q}\) into \(\overline{\mathbb{Q}}\) (the algebraic closure), providing the rank over \(\mathbb{C}\) but failing entirely to determine if the vectors can be coerced back into \(\mathbb{Q}\) [cite: 19, 24]. 

#### 6.1.2 Tarski-Seidenberg Elimination
Another exhausted approach is utilizing quantifier elimination. For \(\mathbb{R}\), algorithms based on the Blum-Shub-Smale model or Tarski-Seidenberg can eliminate existential quantifiers to decide \(\exists\mathbb{R}\) in \(\mathbf{PSPACE}\) [cite: 6, 23]. Tarski's theorem critically relies on the intermediate value theorem and the properties of real closed fields (where every positive element is a square) [cite: 23]. 
The rational numbers \(\mathbb{Q}\) are not a real closed field. The intermediate value theorem fails profoundly over \(\mathbb{Q}\) (e.g., \(x^2 - 2 = 0\) has no rational solution despite crossing zero). Consequently, quantifier elimination algorithms designed for tensor rank over \(\mathbb{R}\) structurally halt and crash when applied to \(\mathbb{Q}\) [cite: 5, 19, 23].

### 6.2 Live Techniques: Attacking via Arithmetic Logic

#### 6.2.1 Existential Definition of \(\mathbb{Z}\) in \(\mathbb{Q}\) (Model Theory)
The most active attack vector to resolve the decidability of tensor rank over \(\mathbb{Q}\) is indirect: attempting to prove that the existential theory of \(\mathbb{Q}\) is undecidable [cite: 18, 22]. The standard method in model theory to achieve this is to find a Diophantine equation \(P(t, x_1, \dots, x_k) = 0\) that has rational solutions \((x_1, \dots, x_k) \in \mathbb{Q}^k\) if and only if \(t\) is an integer (\(t \in \mathbb{Z}\)) [cite: 7, 8, 10].

If such an equation exists, Hilbert's 10th problem directly maps into \(\mathbb{Q}\), proving undecidability [cite: 7, 20]. Current progress is tantalizingly close:
*   Poonen (2009) established a universal-existential (\(\forall\exists\)) definition of \(\mathbb{Z}\) in \(\mathbb{Q}\). Specifically, he proved there exists a polynomial \(g \in \mathbb{Z}[t, x_1, \dots, x_n]\) such that for any \(t \in \mathbb{Q}\), \(t \in \mathbb{Z}\) if and only if \(\forall x_1 \dots \forall x_n \in \mathbb{Q}, g(t, x_1, \dots, x_n) \neq 0\) [cite: 10, 22].
*   Koenigsmann (2016) minimized the universal quantifiers to exactly one, proving a \(\forall\exists\)-definition of \(\mathbb{Z}\) using the arithmetic of elliptic curves and quaternion algebras [cite: 8, 10]. 

To finally crack the tensor rank problem, researchers are attempting to eliminate the final universal quantifier [cite: 10]. If successful, it would immediately prove that computing tensor rank over \(\mathbb{Q}\) is equivalent to the Halting Problem (undecidable) [cite: 16, 22].

#### 6.2.2 Set-Multilinear Depth-3 Arithmetic Circuits (\(\Sigma\Pi\Sigma\) Circuits)
A strictly computational attack vector links tensor decomposition to circuit complexity. A tensor \(T \in \mathbb{F}^{n \times n \times n}\) can be perfectly modeled as a homogeneous multilinear polynomial \(f_T(X)\) computed by a \(\Sigma\Pi\Sigma\) (Sum-Product-Sum) arithmetic circuit with optimal top fan-in [cite: 9, 11, 12]. 
The tensor rank is precisely the smallest \(k\) for which \(f_T\) can be computed by a \(\Sigma\Pi\Sigma\) circuit of size \(k\) [cite: 9, 11]. Thus, learning an optimal decomposition for a constant-rank tensor over \(\mathbb{Q}\) is equivalent to efficiently learning a set-multilinear depth-3 circuit by black-box access to measurements [cite: 9, 12]. This transforms the algebraic geometry problem into an algebraic learning theory problem. Current algorithms use randomized black-box evaluations (e.g., Karnin-Shpilka algorithms) but remain bound to continuous or finite fields, explicitly flagging \(\mathbb{Q}\) as the persistent barrier [cite: 9, 12].

## 7. Cross-References

The computational chasm represented by tensor rank over \(\mathbb{Q}\) acts as a nexus point linking multiple disparate areas of theoretical computer science and mathematics.

### 7.1 Anti-Anchors: Problems That Are Equivalently Hostile
*   **Minimal Rank Matrix Completion:** While finding the standard rank of a fully observed matrix is easy, the problem of *Minimal Rank Matrix Completion* (filling in missing entries of a matrix to minimize its rank) exhibits identical complexity to tensor rank. Over \(\mathbb{Q}\), minimal rank matrix completion is exactly \(\exists\mathbb{Q}\)-complete, answering open questions by Buss, Frandsen, and Shallit (1999) [cite: 3, 5, 16].
*   **RAC-Drawability on a Grid:** In computational geometry, determining whether a graph can be drawn such that all edge crossings occur at right angles (RAC-drawing) is \(\exists\mathbb{R}\)-complete [cite: 22]. However, asking if a graph has a RAC-drawing *specifically on an integer grid* forces the variables into the rationals. This grid variant is explicitly proven to be \(\exists\mathbb{Q}\)-complete [cite: 22]. If tensor rank over \(\mathbb{Q}\) is undecidable, then there are graphs for which it is fundamentally impossible to compute if a grid RAC-drawing exists [cite: 22].

### 7.2 Related Open Problems
*   **Hilbert’s 10th Problem over \(\mathbb{Q}\):** As repeatedly highlighted, the decidability of \(\exists\mathbb{Q}\) is a modern restatement of Hilbert's 10th problem localized to the rational numbers [cite: 7, 8, 10]. A definitive algorithm for tensor rank over \(\mathbb{Q}\) would miraculously yield an algorithm for Hilbert's 10th over \(\mathbb{Q}\) [cite: 3, 7].
*   **Partition Regularity (Hindman's Conjecture):** Recent efforts to map the complexity of polynomial equations into Ramsey theory and partition regularity have touched upon \(\mathbb{Q}\). Determining the partition regularity of specific equations over \(\mathbb{Z}\setminus\{0\}\) connects deeply to the lightface hierarchy (\(\Sigma^0_1\)-completeness) established by Hilbert's 10th problem [cite: 28].
*   **Quantum Information (W-States):** In quantum mechanics, the tensor rank defines the entanglement complexity of multipartite states [cite: 1, 29]. For instance, the tensor rank of the tensor product of two three-qubit W-states is exactly 8 [cite: 29]. Understanding the minimal rank of rational probability amplitudes directly invokes the complexity limitations of \(\exists\mathbb{Q}\), presenting hard theoretical boundaries for quantum state tomography and tensor network synthesis [cite: 1, 29].

### 7.3 Candidate Primitives
Should a breakthrough occur, it will likely emerge from bridging non-linear algebra with automated theorem proving over specific rings.
*   **Polynomial Equivalence by Scaling:** Testing whether two given polynomials are equivalent under non-singular linear transformations [cite: 17]. This primitive is closely related to tensor isomorphism and border rank identification.
*   **Algebraic Universality:** Schaefer and Štefankovič demonstrated that tensors exhibit *algebraic universality* [cite: 3]. This means that the realization space of a tensor rank decomposition can be forced to be stably equivalent to any arbitrary semi-algebraic set over \(\mathbb{Q}\) [cite: 3]. This geometric primitive guarantees that there are no "shortcuts" in tensor rank; the problem expresses the full expressive logic of the rational numbers without compression.

**Sources:**
1. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9BnsETOXWDFzK_28eabwooSlLi174BVUss3CKbjLra_rw3RZTwKckGy_NIye_rb3CP6l_qaDSTf_xyFiHm_EpcKDtvqAnyZdOebamikV1PXV5ktiyz13-baIie0TCbXlnayzEhkCMb3YEj_hMMKo_wcsGs1MnLZW-Q6FTh5CALuokSTece2H4buk_8FLzQ_ZP5sm-UxQY)
2. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVjaiGA3KonsAxYnvZ0xhb2pK2CWtt7JXM_cTZx0RpEl-Yt1vWvhyMQ82O0oW9XTbHyroFLnuCLiTGPSwusIs64oP7yJ1RalBBDRHEpE9CFBWt1XwZMVuC1WbHsqk0fDQP2ZDBPZSlCsKz)
3. [rochester.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3dik0XOzoyZ-Y2OzOh2jMeA8Lg7CibTmEcz3fLyJDcOb8EvLRIB3iv0fc9BDIjhQjnQCVCPiJXADGB1oJGupQDBQkWR4kvkavzp9KUs9S9SjwU9xlTucb6m8iHEEC6ABPDNaT_VX_OwStKN2vWOiA4Q230A==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnf64jSVZwhLa4F5ZZlI04IdsKlGHDE9kQf3wWQds65D11iGv9_7gHNbTumRjsTqHMtgTJDd_ryYRx1uucB1PfDFRa0Ra60Q0fma2j3qf8jhCqYGcbrjYU)
5. [vixra.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfGMpOkU3p3AFN3H_M0t20dal5S6UaOPK1YnYKNUssfE-KuAoKarr8UVfre8HFsuiMTUuycj406_avzsK8g_tlN4e3OLSaXAFg9J1Jj_Sd238VJmn5bPovQXw=)
6. [uu.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNWE7QL40FhdSYw--cz2fslyBV2JOCQYh8oneELbxr85BlUVX8yftpCTsKLmNAHgJPc_GAIkDvnvvD3h3u7OgVlIMRoD66g_q3O8-tqfsTOOSGmQKBLNS5psBpE81m9keWCtMjjcHivZy2Vdwha1eHlZM5Wlt6BCkYropb0CICO2amug==)
7. [tcd.ie](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHC4r2bjVc6HAaXa4lZCVP9RDNlKT1fvzmeBg4tGEl-51DR3cDkVPeWA4ITl1BWw-yKAxW7mf0kNcMiRfwqgo6Crj8w0AwR2z25fcNxh3CKVRC7FlDrVYIIyaW6wksokJtro5YKHFtIlg==)
8. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyEPHzEp98wyGYGQqCPrHWX6DQ_IM4cF_grm-WJ3xBHDngF2Bu4gTGmeEa1PA-zUzqMUNKQ7tBaA6cKtCJHPu476O-NmsCLHFH0N1NmlMDK0UAi1WY6dibulh7hn5riN_zoU1uWOZZ-mF4eTaCrusQUMUXmW_flTwJULdoAd1__Gy2)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGt78qZCErnx7XljLP6aKH5e7dWAHnAKNzcW-DjxvrT1cp2EvTUlnwwLwMy3Kt4OY4dVGmXGvs63VBDY00uAJ5CaONBTnsnCOvUG71vpVVqVRkTfwz6)
10. [core.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEffKDAnMUy3ucFHpQYaXf3pdeXNsupTp7_V-6HJ3RXVE15J6h4FsaR64trhvHa1mtCsltIYoE9dHTbaUEsFzPcSPol4VpeHHisjtwfpfdLHmi7S0qQMJAfy2KA9Jji0ViYWCh1VkBjtsw)
11. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoKJ7mNs4elgz66E40c9o4QcnMM_5nLXp6BSMF9XQCj5ULXK7ll7o4W8dTasEqqCl5UOOIglyv-wQBa9_aV_zj-HM1N84px4DouJObvcI_RsVO4WRpQJu2Ftg_3A2C00s2_58Rpe2XicpHM44bX7HrwaY47mSZHTUzXt1ftltQkB4DH21fIO5HoIGcqSK3ggV17KYJeMJh9qPvDlYc8EMJbhPlQ-E=)
12. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElK6B-KtgLhpTaz8KxPRo426utk-U8ep_vkA37_WLFBrxmuEyqGlBFDcCkhRTlRHcwcIZPY0mgkwFu3BJ4zR32_9a7Rehm-iraH8Dn6F8tIThz0xFG7BGb9uqwnRorIQ==)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmaPnV6HdcUSAT6eh-QukPyyVGzWyyMu5_XMmm435uoqUlO0fUvgdhxLA_Aqu7RyQaKUIJl-N7xirtI2YGBBe_a1VYpJiYAf0c87s0Pd0YHmxvR9Th4qYK6IHzVXWWPbC5y6wI63EM5-xCNTm9geiJveUavfIGljDO0sc6C9zGTOauhueM)
14. [cornell.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuIvRctIUVbD7FrqK3qAEMHQM5N_NAH2VwIYfi1PNKScSrQBpCMQUHwh6e_Z4AB8dKSXYKfYT7JHmdQ3l2uhmUn80JE3mUmhpp8wl5EOmShic1nYD2M4aowI1YxpL8VyCMWLvL89ZkZcc-U5VmRj7cbb8MUyqMk95RN5mg61OJ6e8zvg==)
15. [kth.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3go6vIb82vTd4KWEZ5tWmOJBT_rC0vS4ghhSxy7V8_gXEQbCNFHFEcHtGQRu_VV3mXfCe_nVos0ZBlubUbQVkaONaA2sGbOCAemeGtj44SZ3KOrraEvHupfNL-o-KyQbtzg==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEONBDx6ZFWJXQZtFiec0RwdtfqYgi3UNY4yb8thzWfOl-NwJ54Gg0_GkPfyeAJUO-u7oKqs8plYlI3f9EdYhyyWoxzzocHNJtl_Hi9J17g4N_xany5)
17. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMdFLP_18es8s3auQA0zYM9aXNLn-dQ-3Qd6Kb0hX19C38xHFXPsdSgE4Ox70Eit8G8zSXYmL08eaSyODvU_8hxJbBpio-fEOGowD62tH0qbL4EPVxV_flMXynbyqwq4cljiSXPLKF5tVtq9b5s5exxGxb85GHxBH5vAJ2r4-ssqtj4pgOhcSb-aLUNgtZLZrm2oWnVFY1HSfJEQvxwyfYk4qzxOLMRBQzrduHQEY738C5hpUoTK0=)
18. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4UhMrDPgFyXNrWI2lpuTxcspnzhI5H25B-0Pp2Jp7JEH9J77W1SftgdZss9AcWme6F-a5pZri72AwjiBcnlibcNvJFBrx1C7tyiCiyI3SrDVoK25YlagIM73nT-e1RVQT91Et5Ld6cto-moE_Mnt7uxQ1T7vB9HYB9zph6C-bbOYbUaE0LkAtOJvB60mLOSg_0QqN2f5E1Chm8VSkouNSASaxpBlU_JycmIweGIodo4fWAzd6I2Iy)
19. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0tTZlX_uVgsTwf9yk0xRXX027e-_cp2Qb0ifleq9ClcyXjoXeZPCAFzt_bOhP7A10MMMpFw-lZmF8ZFVaUtrsVE-gjCWO3Z0l5zVAabzux19faPVM96rY52hvB1GxzdKMasyNI7D1K1Q=)
20. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjE1XPKiWFjJMq1AY1ZRxgs0XeqMLLF8xURDI5UJOvGMoU0wuliD9XR2rgQL2-j4Ks3I4i3RzvBh_UQ6YcWfuswvTy5mXmp4e2kV-RlanKYonpeAfwnId3h4RAo76rin-ikNkh-d_JqIjFGxBXhglYXRz-lMvoF6voH7zalKNKOj5KyozskoJbvoY-_G2u1_IT-27GtSgbrehPQhbPhOipSBoPW1eSDa-pi5CLH-W9ByONabpT5A==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYC8XNL41vC04vV_ZROlm6lvusNAJw9vlAVO0WxxJaYRDl2EUgQoaaiXZto9qtNb-ChI3K4b8NAMDoP-hLko-9swWDtzkPLIuafBumj7q_cUvtW3Iz)
22. [jgaa.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEW5KpCoy-TkFjyrw8GVC5-DNcyTHn840awu5K7_FHE0PvMHgh6NQ6BzjdrIa5E9I5DMNJMGIoVLdRT251xGSApT8jp8v_yDyJr00tiv6AayiU_hCAY3q5QdHdtVZdTqziLkLyHO9Zammzsrc7-h3bQMbGDgA==)
23. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMr5w74l5hczKm72eX2wKXTrwdA4V8d3oHIsz5kxwdrIE4fOfO9v_ygu-2GqwEwDw6noubrfPY2vw9IXDVx42eosnjt5hHwS1HSqZAI2uOrUHkd1w=)
24. [ucdavis.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGgzy9eZjf8RKN0HGe0i22SJPRx-pAkGz2I3ZF4FUIIxCjz0O4pDstrNapfs2-16YFF1qv3HrRQlewoMG7F1IulP6zTefdAqBbRzrR5MbvkdE6hQzLoZm651kD0k_1vBTXsWPEzY2T4fjAiLXGMv--9HPSGNp_SyAhpVY=)
25. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFH87BmQaZpxvuo1T13zYwRwsq_nZM70IubdiypCUYV4pjj4_xH1UBrlyYfpBGYCuEJV2uPuln349HxOPC5y28SLraatDZI4Q9J5smeoxacUMLHGHyBtd5fFozH8mXB3VCsgo2Vec24sSRIplOtUw==)
26. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZTpU5mc1Nzyy-bRTPfzubwmXoo7qMdprtzDypFw8SWrBEcyDnS9zf8lrbcGYiIazB14IDSwhZConLa6L4LufB-ZXUHrGE7VUhH6tbqjPlTAo9myEnnsevLmeoGR6bGxVLtp13v5maz_h5-CN4HTksXAazTdtvetPkdTRQ2f6C9zKYJC4hL1w5fu-WvQr-n-XlSRHeP9a13BTPU3CKsp-pe9gZvr_DPDcFmg==)
27. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYl-VLIMMPZAhI38o8b4B2WlH9QaZfNNjjS1OmrAxrdrRKTmuhMdacE-vxXSTKeyda9RROolSxSpwQQKxo4kdZ4xv5n17qobbBV7_w3STZvckvzfqLZLnHKrsyfFVlIGdHqpsabenuo4xHFAAtv-4l3Ovtn7DXeFvhGyv_ZDTIluCJXGG1nCENwcz5inAp2nhJvIStTnb8KnDWhuBs3FVF9pb17IyJ9PY1VQEvnm7_m8XIiqe6sIIFhegisj-l)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKA0HcR_MYolTImtLgz9nfH_UkrRav_Q6Q7Eg7v0dF2eIwdRpuz6JXTwQbxl2KgIb9EoivEUptQrZ2nkDeoK0HPOOXIFfRmEpEf94F06JJk5wchdBr)
29. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEC20HYhk7fuEI1R9iy7NE1nCk06nnJtIxXZXu7DNbHRNnjojgGfA0GoPl_y05YeNdV9lWrwvkA4fjSwtiLc1iC66lbFYqXml56RPGJXMDWw_rpXt-bplT-GkI0G08ag2Qex1jfJbdxnd0sznfBMETjvqQXWqnpBgg8YNv0Toh5j2oZPomSXnV4xbfJ7JoU14JSdw==)

