# T#97 Stretched Kronecker positivity (quasi-polynomiality)

**Pythia queue id:** 128
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdUQ2dQYXBlZkxPdmtqTWNQeVlpd3VBdxIXVENnUGFwZWZMT3Zrak1jUHlZaXd1QXc
**Elapsed:** 443s
**Completed at:** 2026-05-21T15:51:36.652377+00:00

---

# T#97 Stretched Kronecker Positivity and Quasi-Polynomiality: A Comprehensive Academic Report

### Leading Paragraph

**Key Points:**
*   **Kronecker Coefficients:** These fundamental integers describe the multiplicities of irreducible representations in the tensor product of symmetric group representations. Finding a positive combinatorial formula for them remains one of the most prominent open mysteries in algebraic combinatorics (famously known as Problem 10 on Stanley's list).
*   **Positivity is Intractable:** Recent breakthrough research suggests that deciding whether a single Kronecker coefficient is strictly positive is NP-hard. This implies that a simple, efficient rule to determine their non-zero status likely does not exist unless P = NP.
*   **Stretching and Quasi-Polynomiality:** When the parameters of the Kronecker coefficients are multiplied by an integer scaling factor \(k\), the resulting "stretched" coefficients behave as a quasi-polynomial function of \(k\).
*   **Asymptotic Positivity:** While exact positivity is NP-hard, determining whether a stretched Kronecker coefficient is positive for *some* scaling factor \(k\) is equivalent to checking membership in a geometric shape called a moment polytope (or Kronecker polytope). This membership problem is demonstrably easier, lying in the intersection of the complexity classes NP and coNP.
*   **Applications:** The behavior of stretched Kronecker coefficients has deep implications for Geometric Complexity Theory (an approach to resolving the P vs. NP problem), as well as the quantum marginal problem in quantum information theory.

**The Combinatorial Challenge**
For decades, mathematicians have sought to understand the structure constants that emerge when multiplying representations of the symmetric group. While the related Littlewood-Richardson coefficients boast an elegant combinatorial rule and well-behaved geometric properties (such as saturation), Kronecker coefficients exhibit no such simplicity. Their values can fluctuate unpredictably, and exact computation becomes exponentially difficult as the inputs grow.

**The Power of Stretching**
To bypass the chaotic nature of individual coefficients, researchers apply a technique called "stretching"—scaling the inputs uniformly. By doing so, the discrete, jagged nature of the coefficients gives way to a continuous, geometric structure. The stretched coefficients follow a quasi-polynomial growth rate, meaning they act like polynomials whose coefficients cycle periodically. This bridge between discrete counting and continuous geometry (Ehrhart theory) allows mathematicians to use sophisticated tools from symplectic geometry and computational complexity to estimate bounds, even when exact counting is impossible.

**A Crossroads of Physics and Computer Science**
The theoretical abstraction of Kronecker coefficients has surprisingly concrete applications. In theoretical computer science, they serve as "obstructions" in Geometric Complexity Theory, utilized in attempts to prove that certain computations (like the permanent of a matrix) are inherently harder than others (like the determinant). Simultaneously, in quantum physics, deciding the positivity of stretched Kronecker coefficients is mathematically equivalent to the quantum marginal problem—determining how the parts of a complex, entangled quantum system relate to the whole. Thus, the study of these coefficients unites pure algebra, theoretical computer science, and quantum mechanics.

---

## 1. Introduction to Algebraic Combinatorics and Representation Theory

The intersection of algebraic combinatorics and representation theory has long provided a fertile ground for discovering profound mathematical structures. At the heart of this intersection lie the symmetric group \(S_n\), the general linear group \(\text{GL}_n(\mathbb{C})\), and the structure constants that dictate how their representations combine and decompose. 

The irreducible representations of the symmetric group \(S_n\) (often called Specht modules) are naturally parameterized by integer partitions \(\lambda \vdash n\) [cite: 1]. A partition \(\lambda = (\lambda_1, \lambda_2, \dots, \lambda_\ell)\) is a sequence of weakly decreasing positive integers that sum to \(n\). These partitions are visually represented by Young diagrams—left-justified arrays of boxes where the \(i\)-th row contains \(\lambda_i\) boxes [cite: 2].

When we consider two irreducible representations of \(S_n\), denoted \([\mu]\) and \([\nu]\), their tensor product \([\mu] \otimes [\nu]\) forms a new representation of \(S_n\) via the diagonal action. Because the irreducible representations form a complete basis for all finite-dimensional representations of \(S_n\), this tensor product can be decomposed into a direct sum of irreducible representations \([\lambda]\). The multiplicities of these constituent representations are known as the **Kronecker coefficients**, denoted \(g(\lambda, \mu, \nu)\) [cite: 1]. 

Formally, the Kronecker coefficient is defined by the isomorphism:
\[ [\mu] \otimes [\nu] \simeq \bigoplus_{\lambda \vdash n} g(\lambda, \mu, \nu) [\lambda] \]
By Schur-Weyl duality, these coefficients also manifest in the representation theory of the general linear group. Specifically, \(g(\lambda, \mu, \nu)\) represents the multiplicity of the \(\text{GL}(V) \times \text{GL}(W)\)-irreducible module \(V_\lambda \otimes W_\mu\) in the decomposition of the \(\text{GL}(X)\)-irreducible module \(X_\nu\), where \(X = V \otimes W\) [cite: 3].

Despite their elementary definition, introduced by Francis Murnaghan in 1938 [cite: 4, 5], Kronecker coefficients are notoriously elusive. Unlike their well-behaved cousins, the Littlewood-Richardson (LR) coefficients, Kronecker coefficients lack a general, positive combinatorial interpretation. The pursuit of such an interpretation is recognized as Problem 10 on Richard Stanley's famous list of open problems in algebraic combinatorics [cite: 2, 6]. 

## 2. The Mechanics of Kronecker Coefficients

### 2.1 Character Theory Definition
Using the character theory of finite groups, the Kronecker coefficient can be computed as the inner product of characters over the symmetric group. If \(\chi^\lambda\), \(\chi^\mu\), and \(\chi^\nu\) denote the irreducible characters corresponding to the partitions \(\lambda, \mu, \nu \vdash n\), the Kronecker coefficient is given by:
\[ g(\lambda, \mu, \nu) = \langle \chi^\lambda, \chi^\mu \chi^\nu \rangle = \frac{1}{n!} \sum_{\sigma \in S_n} \chi^\lambda(\sigma)\chi^\mu(\sigma)\chi^\nu(\sigma) \]
Because the characters of the symmetric group are real-valued integers, the Kronecker coefficient is perfectly symmetric with respect to any permutation of the three partitions \((\lambda, \mu, \nu)\) [cite: 4, 7].

### 2.2 Lack of Combinatorial Formulas
A "positive combinatorial formula" in algebraic combinatorics typically means expressing a non-negative integer quantity as the exact cardinality of a well-defined set of discrete objects (e.g., specific types of tableaux, integer matrices, or lattice paths) whose validity can be checked in polynomial time. For the Littlewood-Richardson coefficients \(c_{\mu, \nu}^\lambda\), the Littlewood-Richardson rule states that the coefficient equals the number of LR-tableaux of shape \(\lambda / \mu\) and weight \(\nu\) [cite: 5].

For Kronecker coefficients, no such rule exists in general, though partial combinatorial interpretations exist for strictly constrained partition shapes (e.g., hooks, two-row shapes, or specific bounds on lengths) [cite: 2, 3]. The difficulty of finding a unified combinatorial interpretation suggests deep inherent complexity within the coefficients themselves.

## 3. Stretched Kronecker Coefficients and Quasi-Polynomiality

To understand the macroscopic behavior of Kronecker coefficients, researchers study their asymptotic properties by uniformly scaling the input partitions. For a positive integer \(k\) and partitions \(\lambda, \mu, \nu \vdash n\), the **stretched Kronecker coefficient** is defined as the function:
\[ k \mapsto g(k\lambda, k\mu, k\nu) \]
where \(k\lambda = (k\lambda_1, k\lambda_2, \dots)\) denotes the partition obtained by scaling each part of \(\lambda\) by \(k\).

### 3.1 Ehrhart Theory and Quasi-Polynomials
The stretching operation connects discrete representation theory to the geometry of convex polyhedra via Ehrhart theory. A function \(f: \mathbb{Z}_{\ge 1} \to \mathbb{Z}\) is called a **quasi-polynomial** of degree \(d\) if there exists an integer period \(m\) and a set of polynomials \(P_0, P_1, \dots, P_{m-1}\) such that \(f(k) = P_{k \bmod m}(k)\) [cite: 8, 9]. 

Motivated by computational complexity applications, Ketan Mulmuley proved that stretched Kronecker coefficients \(g(k\lambda, k\mu, k\nu)\) are quasi-polynomial functions of \(k\) [cite: 7, 9]. This result implies that the coefficients enumerate the number of integer lattice points inside certain scaled rational polytopes.

### 3.2 Piecewise Quasi-Polynomiality and the BVW Algorithm
The behavior of the stretched Kronecker coefficients over the entire parameter space of partitions was extensively formalized by Velleda Baldoni, Michèle Vergne, and Michael Walter (BVW). They established that the stretched Kronecker coefficient \(g(k\lambda, k\mu, k\nu)\) is a **piecewise quasi-polynomial function** of \((k, \lambda, \mu, \nu)\) [cite: 1]. 

More precisely, the domain of non-zero Kronecker coefficients—known as the Kronecker polyhedron—can be decomposed into a fan of closed polyhedral subcones called **chambers**. Within each chamber \(C\), there exists a specific quasi-polynomial \(p_C\) such that:
\[ g(k\lambda, k\mu, k\nu) = p_C(k, \lambda, \mu, \nu) \]
whenever \((\lambda, \mu, \nu) \in C\) [cite: 1]. 

The BVW algorithm implements this theoretically using methods from symplectic geometry and Jeffrey-Kirwan residue calculus [cite: 10]. The algorithm symbolically computes the stretched Kronecker coefficients as exact quasi-polynomials for partitions of bounded lengths. For instance, for partitions where \(\ell(\lambda) \le 6, \ell(\mu) \le 2, \ell(\nu) \le 3\), the software can output the explicit quasi-polynomial valid on an entire polyhedral chamber [cite: 10, 11]. 

Despite the highest-order term of this quasi-polynomial (the volume function given by the Duistermaat-Heckman measure) being strictly polynomial, the lower-degree terms exhibit highly periodic oscillatory behavior [cite: 1].

### 3.3 Vector Partition Functions
An alternative approach to the quasi-polynomiality of Kronecker coefficients comes from viewing them through the lens of vector partition functions. A vector partition function counts the number of ways to express a target vector as a non-negative integer linear combination of a fixed set of vectors. 

Mishna, Rosas, and Sundaram utilized this to express \(g(\lambda, \mu, \nu)\) as an alternating sum of vector partition function evaluations [cite: 12, 13]. Because vector partition functions are known to be piecewise quasi-polynomials on the maximal cones of their chamber complexes, this explicitly confirms the quasi-polynomial nature of the stretched Kronecker coefficients [cite: 14]. This perspective has allowed for computationally efficient software implementations (like those available in Maple) to calculate the coefficients for partition lengths up to \(\ell(\lambda) \le 8, \ell(\mu) \le 2, \ell(\nu) \le 4\) [cite: 12, 13].

## 4. The Computational Complexity of Exact Positivity

A central problem in geometric complexity theory and representation theory is the **Positivity Problem**: Given partitions \(\lambda, \mu, \nu \vdash n\), decide whether \(g(\lambda, \mu, \nu) > 0\). 

### 4.1 NP-Hardness
For many years, the complexity of this decision problem was unknown, with some researchers hoping it would reside in the complexity class P, much like the analogous positivity problem for Littlewood-Richardson coefficients. However, a landmark result by Christian Ikenmeyer, Ketan Mulmuley, and Michael Walter proved that deciding the positivity of a single Kronecker coefficient is **NP-hard** when the input partitions are given in unary [cite: 14, 15].

This NP-hardness result carries profound implications for Stanley's Problem 10. If evaluating whether \(g(\lambda, \mu, \nu) > 0\) is NP-hard, then computing the exact value of the coefficient must be at least as difficult, placing the exact counting problem firmly in the class #P-hard and within GapP [cite: 3, 4, 16]. Furthermore, assuming \(\text{P} \neq \text{NP}\), this rules out the existence of a purely saturated polyhedral combinatorial interpretation (like the LR rule) whose non-emptiness could be checked efficiently via linear programming [cite: 17].

### 4.2 Quantum Complexity and QMA
Recent developments have recontextualized the Kronecker positivity problem within quantum complexity theory. Gosset et al. established that deciding the positivity of Kronecker coefficients is contained in **QMA** (Quantum Merlin-Arthur), the quantum analog of NP [cite: 6, 18]. 

Specifically, the Kronecker coefficient \(g(\lambda, \mu, \nu)\) is proportional to the rank of a specific projector that can be measured efficiently by a quantum computer. Consequently, a Kronecker coefficient effectively counts the dimension of the vector space spanned by the accepting witnesses of a QMA verifier [cite: 6, 18]. This links the problem of approximating Kronecker coefficients (to within a relative error) to the complexity of estimating thermal properties of quantum many-body systems, proving that the approximation problem is polynomial-time reducible to quantum approximate counting [cite: 18].

## 5. Moment Polytopes and Asymptotic Positivity

While exact positivity of a single Kronecker coefficient is NP-hard, the *asymptotic* or *stretched* positivity problem exhibits drastically different complexity. The question here is: Given rational weight vectors \(\bar{\lambda}, \bar{\mu}, \bar{\nu}\), does there exist an integer \(k \ge 1\) such that the stretched Kronecker coefficient \(g(k\lambda, k\mu, k\nu) > 0\)?

### 5.1 The Kronecker Polytope
Geometrically, the set of normalized triples \((\frac{\lambda}{k}, \frac{\mu}{k}, \frac{\nu}{k})\) for which the Kronecker coefficient is positive forms a dense set of rational points inside a convex polytope known as the **Kronecker polytope** (a specific instance of a moment polytope) [cite: 19, 20, 21]. 

Moment polytopes arise in symplectic geometry and geometric invariant theory, classifying the spectra of moment maps of vectors in orbit closures [cite: 22]. The Kronecker polytope specifically captures the asymptotic support of the representation-theoretic multiplicities of the symmetric group [cite: 21].

### 5.2 Membership in NP and coNP
In a striking divergence from the NP-hardness of exact positivity, Bürgisser, Christandl, Mulmuley, and Walter proved that deciding membership in the Kronecker polytope (and general moment polytopes for finite-dimensional unitary representations of compact connected Lie groups) lies in **\(\text{NP} \cap \text{coNP}\)** [cite: 15, 23].

This complexity classification means that if a point belongs to the polytope, there is a short, easily verifiable proof (an NP certificate), and if it does *not* belong to the polytope, there is equally a short, verifiable proof of its exclusion (a coNP certificate) [cite: 19, 21].

1.  **The NP Certificate:** The membership of a spectrum in the moment polytope can be certified by explicitly constructing a state (a tensor realization) with the prescribed marginals. The geometry of the polytope ensures that finite precision is sufficient, and the walls of the polytope are "not too steep," allowing for a polynomial-sized certificate [cite: 19, 21].
2.  **The coNP Certificate:** Non-membership is certified by providing a **Ressayre element**—a specific one-parameter subgroup that defines a separating hyperplane (a facet-defining inequality) between the point and the polytope. Evaluating a highest-weight "determinant polynomial" against this element efficiently proves that the point lies outside the feasible region [cite: 20, 21].

The containment in \(\text{NP} \cap \text{coNP}\) strongly suggests that determining asymptotic stretched Kronecker positivity is not NP-hard (since if an NP-hard problem were in coNP, the polynomial hierarchy would collapse, which is widely disbelieved) [cite: 20, 24]. It suggests the possibility that asymptotic positivity might eventually be resolved in polynomial time (P) [cite: 20, 25].

## 6. Geometric Complexity Theory (GCT)

The intense interest in the computational complexity of Kronecker coefficients is largely driven by **Geometric Complexity Theory (GCT)**. Initiated by Mulmuley and Sohoni, GCT aims to resolve fundamental questions in computer science—such as the P vs. NP and VP vs. VNP problems—using algebraic geometry and representation theory [cite: 3, 26].

### 6.1 Permanent vs. Determinant
A core milestone in GCT is to separate the complexity classes VP (functions efficiently computable by arithmetic circuits) and VNP (functions whose coefficients are efficiently computable). This is algebraically framed as proving that the permanent of an \(m \times m\) matrix (which is VNP-complete) cannot be expressed as the determinant of an \(n \times n\) matrix (which is in VP) for any polynomial bound \(n = \text{poly}(m)\) [cite: 17, 27].

GCT proposes to separate these complexity classes by analyzing the orbit closures of the padded permanent and the determinant under the action of the general linear group. If a specific irreducible representation appears in the coordinate ring of the orbit closure of the determinant with a certain multiplicity, but appears in the coordinate ring of the permanent's orbit closure with a strictly lower multiplicity (or zero), this discrepancy serves as a **representation-theoretic obstruction** [cite: 26, 27].

### 6.2 The Role of Rectangular Kronecker Coefficients
To find these obstructions, GCT relies on understanding the multiplicities of representations, specifically **plethysm coefficients** and **Kronecker coefficients**. A critical subcase involves **rectangular Kronecker coefficients**, denoted \(g(\lambda, d \times m, d \times m)\), where the partitions \(\mu\) and \(\nu\) are rectangles of height \(m\) and width \(d\) [cite: 2, 28]. 

Initially, it was hoped that the vanishing (positivity failure) of specific rectangular Kronecker coefficients could provide the necessary obstructions to yield super-polynomial lower bounds on the determinantal complexity of the permanent. However, subsequent research by Ikenmeyer, Panova, and others demonstrated a "no-go" theorem: the vanishing of rectangular Kronecker coefficients cannot be used to prove superquartic (or super-polynomial) lower bounds for the permanent [cite: 2, 28]. In almost all relevant cases, either the rectangular Kronecker coefficient is strictly positive, or no corresponding highest weight vector exists to form an obstruction [cite: 28]. 

While this specific obstruction pathway was stymied, the structural study of Kronecker quasi-polynomiality remains essential for refining the GCT approach and analyzing asymptotic bounds [cite: 29].

## 7. The Quantum Marginal Problem

The rich geometric structure of stretched Kronecker coefficients extends deeply into quantum physics, specifically addressing the **Quantum Marginal Problem**. 

Consider a multipartite quantum system, such as a tripartite pure state \(|\psi\rangle \in \mathcal{H}_A \otimes \mathcal{H}_B \otimes \mathcal{H}_C\). The local states of the individual subsystems are described by their reduced density matrices, obtained by taking the partial traces over the other systems (e.g., \(\rho_A = \text{Tr}_{BC}(|\psi\rangle\langle\psi|)\)). The quantum marginal problem asks: Given three spectra (eigenvalues) \(\alpha, \beta, \gamma\), does there exist a global pure tripartite state whose reduced density matrices exhibit these exact spectra? [cite: 30].

Remarkably, by a correspondence known as state-channel duality, the set of admissible spectra for this tripartite quantum marginal problem is precisely the **Kronecker polytope** [cite: 19, 30]. Therefore, determining whether a set of local spectra is physically compatible with a global pure state is mathematically equivalent to deciding the positivity of stretched Kronecker coefficients [cite: 19, 25].

The fact that membership in the Kronecker polytope is in \(\text{NP} \cap \text{coNP}\) implies that the tripartite quantum marginal problem for spectra avoids NP-hardness, unlike more general instances of quantum marginal constraints which can be QMA-complete [cite: 15, 30].

## 8. Saturation and Reduced Kronecker Coefficients

To fully grasp the complexity of Kronecker coefficients, they are often compared to the **Littlewood-Richardson (LR) coefficients** \(c_{\mu, \nu}^\lambda\). LR coefficients dictate the decomposition of the outer tensor product of symmetric group representations (and equivalently, the tensor product of GL-representations) [cite: 3].

### 8.1 The Saturation Property
A hallmark of LR coefficients is the **Saturation Theorem**, proven by Knutson and Tao in 1999 [cite: 3, 14]. The theorem states that if a stretched LR coefficient is positive, the unscaled coefficient must also be positive. Formally:
\[ c_{k\lambda, k\mu}^{k\nu} > 0 \text{ for some } k \ge 1 \implies c_{\lambda, \mu}^\nu > 0 \]
Because of this saturation property, the exact positivity of an LR coefficient is equivalent to its asymptotic positivity. Since asymptotic positivity corresponds to checking if a point lies in the Horn polytope (which can be done via linear programming), deciding if \(c_{\mu, \nu}^\lambda > 0\) is solvable in polynomial time (P) [cite: 3, 5].

### 8.2 Failure of Saturation for Kronecker Coefficients
In stark contrast, the Kronecker coefficients **do not** possess the saturation property. The standard counterexample is:
\[ g(2,2,\; 2,2,\; 2,2) = 1 \quad \text{but} \quad g(1,1,\; 1,1,\; 1,1) = 0 \]
[cite: 5, 16]. Because saturation fails, the presence of "holes" in the Kronecker semigroup means that a point can geometrically belong to the Kronecker polytope (implying \(g(k\lambda, k\mu, k\nu) > 0\) for some \(k\)), yet the actual unscaled coefficient evaluates to zero [cite: 1, 21]. This structural lack of saturation directly underpins why deciding exact Kronecker positivity is NP-hard, while polytope membership is in \(\text{NP} \cap \text{coNP}\) [cite: 14, 21].

### 8.3 Reduced Kronecker Coefficients
An important intermediary between LR and Kronecker coefficients is the **reduced Kronecker coefficient**, introduced via the stability property discovered by Murnaghan in 1938 [cite: 4, 5]. Murnaghan observed that if one takes partitions \(\alpha, \beta, \gamma\) and appends a long first row of size \(n - |\alpha|\) (and similarly for \(\beta, \gamma\)), the Kronecker coefficient stabilizes as \(n\) grows large. 

The stable limit is the reduced Kronecker coefficient, denoted \(\bar{g}(\alpha, \beta, \gamma)\) [cite: 5, 16]. For a long time, researchers hypothesized that reduced Kronecker coefficients might occupy a "middle ground" and possess the saturation property, similar to LR coefficients [cite: 5]. This conjecture, independently formulated by Kirillov and Klyachko in 2004, stated that \(\bar{g}(k\alpha, k\beta, k\gamma) > 0 \implies \bar{g}(\alpha, \beta, \gamma) > 0\) [cite: 5, 16].

However, in 2020, Pak and Panova conclusively disproved this conjecture, demonstrating that saturation fails for reduced Kronecker coefficients as well [cite: 5, 16]. They showed that every ordinary Kronecker coefficient can be realized as an explicit reduced Kronecker coefficient, proving that, structurally and computationally, reduced Kronecker coefficients share the deep intractability of the ordinary Kronecker coefficients [cite: 5].

## 9. Parallel Phenomena: Stretched Schubert Coefficients

The quasi-polynomial behavior of stretched coefficients is not strictly unique to the Kronecker setting. A parallel line of research investigates **Schubert coefficients**, which are the structure constants for the multiplication of Schubert polynomials.

For a permutation \(u \in S_n\), one can define a scaled permutation \(k * u \in S_{kn}\) by scaling its Lehmer code. The **stretched Schubert coefficient** is defined as:
\[ f_{u,v,w}(k) := c_{k*u, k*v}^{k*w} \]
where \(c\) denotes the standard Schubert structure constant [cite: 7, 9, 31]. 

Pak and Slonim recently proved that the function \(f_{u,v,w}(k)\) is **eventually quasi-polynomial** [cite: 7, 9, 31]. This resolves a 2004 conjecture by Kirillov, demonstrating that the generating function for the sequence of stretched Schubert coefficients is rational [cite: 7, 31]. 

The proof utilizes the combinatorics of pipe dreams to express Schubert coefficients as alternating sums of integer points in certain polytopes that scale linearly with \(k\). By invoking Ehrhart theory, they achieve the eventual quasi-polynomiality, echoing the methods applied to Kronecker coefficients [cite: 7, 31]. Notably, just as with Kronecker coefficients, the saturation property fails for stretched Schubert coefficients [cite: 9]. 

## 10. Algorithmic Tools and Modern Implementations

Despite the #P-hardness of computing Kronecker coefficients for arbitrary partitions, mathematical software has advanced to handle bounded cases symbolically and practically. 

### 10.1 The Maple `Kronecker` Package
The `Kronecker` package for Maple, developed by Baldoni, Vergne, and Walter, stands as a premier tool for computing both exact and stretched Kronecker coefficients [cite: 11, 32]. It utilizes an optimized version of the Jeffrey-Kirwan residue algorithm [cite: 10, 11]. 

A unique feature of this package is its ability to handle symbolic scaling parameters. By inputting \((k\lambda, k\mu, k\nu)\), the package returns the exact quasi-polynomial \(p(k)\) governing the sequence [cite: 11, 32]. For example, the software computes that for \(\lambda=(10,6,2), \mu=(10,8), \nu=(11,7)\), the stretched coefficient is:
\[ g(k\lambda, k\mu, k\nu) = \frac{3}{8} + \frac{5}{8}(-1)^k + \frac{3}{2}k + \frac{7}{4}k^2 \]
demonstrating the oscillatory (period 2) quasi-polynomial nature [cite: 11, 32]. The software handles partitions with lengths bounded by 3, or unbalanced bounds like \(\ell(\lambda) \le 6, \ell(\mu) \le 2, \ell(\nu) \le 3\) [cite: 11, 12].

### 10.2 Vector Partition Algorithms
Building on the work of Mishna, Rosas, and Sundaram, newer computational tools have been developed that leverage vector partition functions to expand the computable bounds to \(\ell(\lambda) \le 8, \ell(\mu) \le 2, \ell(\nu) \le 4\) [cite: 12, 13]. These implementations bypass the heavy machinery of symplectic geometry, instead relying directly on polyhedral integer point counting [cite: 33, 34]. Furthermore, analytic combinatorics in several variables is actively being explored to extract continuous asymptotic formulas from these vector partition summations, offering a promising avenue to estimate where Kronecker coefficients vanish [cite: 34, 35].

## 11. Open Problems and Future Directions

The study of Kronecker coefficients remains a vibrant, evolving field populated with formidable open questions:

1.  **Combinatorial Interpretation:** Stanley's Problem 10 remains unsolved. While a fully saturated, P-time verifiable rule is highly unlikely due to NP-hardness, researchers still search for alternating sign formulas or non-polynomial-time verifiable positive combinatorial objects [cite: 2, 6, 36].
2.  **Log-Concavity Conjectures:** While saturation fails, there is mounting evidence that certain log-concavity properties hold for the stable tensor products of irreducible symmetric group representations (related to reduced Kronecker coefficients) [cite: 4]. Generalizations of Okounkov's log-concavity conjecture for LR coefficients are being tested against Kronecker variants [cite: 4].
3.  **Hook Stability:** Recent literature points to new stabilization phenomena, such as "hook stability," where Kronecker coefficients stabilize when cells are added simultaneously to the first row and first column of the indexing partitions [cite: 35, 37].
4.  **Complexity of the Multiplicity Operators:** Determining the exact multiplicity of eigenvalues within the moment polytope covariance operators remains an open problem in both statistical imaging (like DTI) and pure representation theory [cite: 38].
5.  **Quantum Algorithms:** As Kronecker positivity sits in QMA, investigating whether specific quantum algorithms (such as variations of Quantum Phase Estimation or QAOA) can provide heuristic superpolynomial speedups for exact Kronecker evaluation continues to draw significant focus from quantum computer scientists [cite: 24, 39].

## 12. Conclusion

The "T#97" inquiry into stretched Kronecker positivity and quasi-polynomiality uncovers one of the most theoretically dense intersections in modern mathematics. What begins as a question of counting symmetric group representations explodes into a landscape involving Ehrhart geometry, P vs. NP, quantum entanglement, and symplectic moment maps.

We now know that multiplying the size of the partitions by a scalar \(k\) smooths out the combinatorial chaos, revealing a piecewise quasi-polynomial structure managed by chambers of the Kronecker polytope [cite: 1, 10]. While extracting the exact value of a Kronecker coefficient is a demonstrably NP-hard task [cite: 14], discovering if the scaled partitions eventually become positive is much easier, lying in \(\text{NP} \cap \text{coNP}\) [cite: 20, 23]. The absence of the saturation property ensures these two regimes—exact and asymptotic—remain irrevocably split [cite: 5, 16].

Ultimately, the stretched Kronecker coefficients continue to serve as the critical testing ground for Geometric Complexity Theory and quantum state tomography. Even as classical and quantum algorithms inch closer to mapping their boundaries, the Kronecker coefficients proudly retain their status as one of algebraic combinatorics' most enduring enigmas.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJTX-0afjVFoI-Gh9fzcgQfeort0ckVa-w_4g-4ek3nJt8bNP0pHG9_aYRUodIK3yEPxY7zVlwRSxEOD2eQxTzb5AvzT67knZ3mb8zGOpKCEewNdk=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0mkkXGA56Fc79IcLPF4zvpa2HJmq5PqRuxcb2Dpro0I3jUS4cmeyb9_YCCEVUMd79FIvIqYsZMJao_9I_5XVNF3aUaOjdERpRiELRmXwSLPTvbnyQ)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGiYiGDdzDNvfPMnPQE8K-LXCIiaueKVpouuzgHPOrBdgcrWZSOG0NLTTXV0o7nx5Vy6Pt2RN2-GlSYHk7nItERb-_8yyMsFX9g2HWCEGX2wXH1VDg7jbt6H0dV7164Y452DqBwAczAd8ey1LwM7bhbLNzrLahYKt8NoJ4rUEYkamw2GyAqE8c8zfLxjZK2wx6WjPBhZ6RJicLVCC5en0ulWBc0o5_BOc_xB8TAMnUEirGyKnS2rbSHWQ5JPA==)
4. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGloXJK3kOh94UEDqc1m3HnyFAv90rtdw9zj5bvduwjggiB-bVRTQ4u-eDHcKq2ScnMQpL_uI78bQQMGdorF9QwGs9Th9jiaQkNhhSxMhY2IHJSG5-glloOhvG9vd0estt0z5czZm8MDMueQ4DJSQ==)
5. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtD6a_XW7tWA9dxoax1LVCq7rOfhTww9T47A_JK-7v987xB6pd7ehzPQRXI68Az4hXBG-4sno_6o8xa5PZLIEP4-TQ28czNCkVbFzRIsdxg8yQOKUWm6WIfATJB7ZFFvCTuSqIrCvnQtPe-tmFRDPqi_Gu5M7Rp9R0IWQP4MExrO_GuSalJe9-zCqMn9YwLi3eNmdxA3QISRNNmxdGaJ4DT4_gxG-NjXz7oHHlmGqq7GEoVuU3q5G4jcZnWvD6STt86xXzq0KWZXe5Yu4Mqv6XxRAj_Fr-D5Uv5Wtr)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbRHPcitWWvenz5HhcoN60mnbY-TUUarXVKC-Czv6LgzYgeQ2NU-MnIilAEXEtAV4Oov1AJff9yYcSVkGxQzhhoDNYnmk6XG9oYXh5WlfLH4zv9m8dw9w0)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAe38EkqjdPMXji6JKWxMitA35VxTUmxuikHT7ri8Y28W-ZUlXCBqigJ15QCQG8dgwF36cvm3ZWjRLoDm8vsZKhhrobmnBfcz1J3P0kGxa9NngoDrz-zJ1)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZOXkaeaczrJhuVcHrk09aVG-DKeiw-q_tXH2PVhGPMq8p_t9Pla5W8qVoa-XHq3ZSTQ51k5TjLqOTHxjr6keQcgfYEB0QD6WpFIrw2dxegaMHcUj0)
9. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJ1ucJR8eA0ureOph59Sr4DR_d1cw8-jaJdz5KpfIC4yO-kVwYKj6Mnk0pcpBTNZyoeRxjKXMrjhPGIzs9dOEUi-vBg2wvUXuAOxJjeQ91rKPluWMRHQqxeOhtLUr9CqT-eR4llde7GN3j0zuuV53jTC8=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3_mJrPtyT35sv-yNv-n6-efOhlkxmD3bux5Ov6hMDobteh5wMAa2Ckpgr-HCqcW0it7xk6wBmJtph_HfxSwAytmTtCQYu4V9h2etHDcn9e7jfvlEZ)
11. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjE_3MaENyJoWd22VndpDYvFqrSaxDAhx0Pz78AGxeAYxMwpieJ57jTtj51dZkLS3drc-ynjfhhz7ipME1gfyIaY77cqKCVYUTWBdsLBeiJXuYAIVjPFgi)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF53dGxqUgfeM0v0P6aLZ-Cppuj4VZnmN08g9bXe_cleDGAB-2Fl50Y-neGxWDXXMqQwWNCOpFbfXTpaTXPgcY2XbqJrfxwdoQZwbvnOqxNsVaonTES)
13. [uq.edu.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGXAWJc_BkjO9Y50hoS2Nzy4AaALwmWR0waRCvu2DzXfsvd94pc84oG-SW9cNN9cLIYo9Bd1OUfxdBQ62kCp2xp_k28e6R2267c1lxjZeBJiygqdB2jjwT1extERYuNX6vFDQjUBB90A==)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3nYT_paXV7ZlFh3KvIqmrvHoFPJXIHB4c_1w6r37F8keQkJGO_HeRK8QeYfHDhbb8Nqxc4ap_2y_vQk58AWFWtf2271h9SjIdJBBwhqFgMaEp3NqDi1UsYF7DJZc0UIsdlpooAR03W6yAoRzq5yqq0bhev0yOdl2Kn2Z_6F9CPOcv6dRcwecHyRN_Mxqv)
15. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEum_jpC9LsVPHpUyrN9uk_0cNoykGIhe2UbQlVVKLL7hOmzJcST86OrYn8BD8LliOR7uN27p8TMxhqAwzWASJ9ULaIOV5TpgtJb5WWibsu9oUM76940H3Gs5KWIPQN2qW_NA==)
16. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3FgGXW-aXUnS4lrE4Q9VlHjggaCLFhK4dvv4u08ovP80EY_6Se9VYA9WGbSn87VYBSoQ0JZHqulyahEfKwOSHo72IhMH1W2zcWxjlTbBTvZJZVvntEDDgqIkFr8B3Oi9rwc8LTojNN6johCs=)
17. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxik0XTkVGiIcg5Ipzqgdts-RbGY4WPKLrdh-xIwtTIrQQFquRqX4-NF54BuyJxMygC0k6-5VCgrt1d8ROVYo7P1mrIOAHq0hbV6CbKm_8mojbXHaitx0dbAtJp2MwwBsA2Gp8g-OgiNL3NTJ2iI6pztXsTthF3x1QjWs45mLFHe7hivGj4pJZ7gaYeAr7Rvn8O5boizlFJqm4mplP_WeqdYBXfhrrskJsDDdkHdtQ)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIOHGEfU2LcCoGlz43ff2Tu4o1NDB0IQb6b7yZDsu6kawhvpPzA9zzby8iV3k-6tFjDNcujllp6trk2BPJxbzJOuiydWyk6b1BRqPfsbs5roc5in1x)
19. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9yPvy8MlsxmXFvWDVjjYYnipDfjQ36dm3ljZlPXg79hhOdYJ1cOYciZ9myaNAboArY7qxpQ7GqjppB20X8MTZGaS0yqs5Ph2pmrzxgwCZKYGMwl5yMUvCFnBWqQe_NXonRFpumAjR6Rf60KLSy_iBMZ2_LQ==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOozha8A42ZSi1PHcfLbZVWIFGJlzhssuqdsSSiLsYwgC08iHj0brzocGVz9MzyrG662YLjPn2bedEoJVkU9IW13h4TSKh9OFa4eRTHoP_xdVXyJRG)
21. [michaelwalter.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFucjpHb05fXq4P40FiE4WgYkyP6M-U4SPnJc85nxOws1sTQgUbi_yb5YnO663Yh5q9DYERHcK9RYsOgQ36HRjjMnK6LTnwcIbL_Lbq6kH9JGM8tGV41F2DnrvTpeMuJs6hjaG4fQ8QiAxgtg==)
22. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXEG95JMeTEGADjn3HXSZwamTbEV4TEF0dIxc91w0CCyczcBoybekM_0DnmrOhwfqBjubgBM8QN19gKWnHBpzgzCqTgsnTRDNhAnhxBxM0EcS2W1KUQbNAqz5crBhkWXNhibSwfJ2i11kejXdvV1GTgRcOfBdMiTxpJ2ZL1yZA7w==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE87er9bfQVh4ibxU1b6hjPm59o_RXyC5fCAZ-1_21ra0tZs8_kr_pBtoHgsJKSBJD2LsiRVdtbRDJaZv7mTb4o-xWzaYGVuOLRIhzXq6WftdfdhrYt)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzzaQ5HvuKPgGtjEA5TRYPhx6JhVrsRg3weK_lIGfSb9q2uzlYkfnPNwHIuqLZxYkx6135J6zZRmv41N4CCCWIG3XUhB_Qp8ct9tddYudxUqQnfFfzqPXaOn-eJ5KJ_bJlKSKo_-xH9OegupOYYitApiF9405ZLkgHN9fiegE6cXz_IG0DeUubufYsKdco9BNqgBthouOmXA==)
25. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGbYx7aNyuXqqyxxlGML5zkINid0zWHotf9KD2KQ7Ht2dYw4Jr1RxzkPBbdSSkL36NhR3AQAziE89f5aB5LPjPbDXDK8dWh5P9xqFQES_WYypVwe5Qv8DQ3ZFHWZlS-tDg7kY3fbM=)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2LqDtll4j2zr6Upvw3onIhw6eWyI5ZxApgpZYZKp3rfeY055EOdjZjrgQKcC3Gop0uofbWW-JbxuhWwqJEN-_UqbIXz5J0bmqGv9vLnTvMHEcpjpf)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-We2VuQYHZyaN--uV98dRNL5oCI093z4YdkU85l82pLZgCRSB-FtHwUlejvcwj2cyLVVmYbjqnfx8HfGta916Nsf7K9Ki9mpxbwppXvS2ulJZY5c2rFN6WRNhkzrRkD3k1h6pJzsZvJgR)
28. [tau.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXk7PV4B0b7gRP3H9DwcvH1-MvuCybs-flOugXihskRFyMgxS1D7ccPMcGES_qtidaHagR7-5rNJVyYpEf-8H1xtFrQhSHA0wlhmvUUaBWAxpoDMvxeJI94b1KhgtgsbZIzw-yzvkpOKFDqTYoT8RoJhWL6SNg98decgXXuk89zr0AmDl1)
29. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwoDeimdtaMPk7OPA21qBryQqx9Ve1P7JCL2J1SeVBbt4-DjIKjUA_1Va_S9p5umgy4BA0s82ML1GUPoUyrX-nQYJnIJmcBvu_FZdVKNee_Hh4E94mbAFD6JAnZEhmY4RDME8RsDRP2VgvN9vYnZfQPFm6kbBe902TkQBXqgXFa8Qb8cGkz7T9FCCBW8TCKaZV2WtdGYP8y9fSgzyKHqeMte4=)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEXj-CEDo-quZywrbBVyJx51JN2GvVmBYUVzVzJo8eA5pEcxhz8sdcS5x2TgIegprjF-stjOh0td9qhMxNRy1-jK6Sd2nqICNuHoqKuPJRHxuozeO4)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOE7RaE8m4wS43NW8f5GPAWm2VqYambPm3dbfxIJnuWZzR4AJqV0EpLDuQ9mOrQqgw8N6IjqZo3xMmELaKPyVkjSQK17Ou-YNmNAvfSNVWLRCpDNi7)
32. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiDSUnX1rwf5WM2nMQJfdKtx7RQ_Fjk0cTdJIxGe5Af9oDFxf1iVDaRxUNP51cQjF2b_mNaKa42Xgsma5LRXzeTE0miP5TfSgCfbSExigkVW4OvzNEBAM=)
33. [sfu.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHT1oQtuGyWHKwTNFUYbMcXWis0ntCDTQao_Fc-Hvb8JyZDop5NlNl22UuiG5Z0AfFRVnEuXjpqZGVTri-jNuN1-4X8YwuWj8GEAnIWIV0xQdlFK-MEb65x0XluZe89WOjBJCU2hNYL8bkLZ7Dk36NL5w==)
34. [math.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWV6-OEvDkgiq9gNVhFaVqmEli_sVqC_1-lhDbrqS_kTZcOiyJfr5rJp0A_y-nUKI4T_FBtvli32sYcXEK1tHS561RexTIgCAVAmxG0x23FbBH6MspWcuSLnmpg94Jk8tgxy47Yg8Dow2saZZ0sSb5)
35. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPav1KWQepHk22k4z-09MhaNJF42fnRBLDwxGXYCWurH91BJ9YmDi8BK_-Pk082RtIawJx87jUpDXdOni1LBs2m81bberQBkIWtw2Uvzj_tMvEAg8ZS0fmXxD9T_-wy9ms0HUy42XMCsiKhf1Amuh2a-1JzxZGIDSiLoNih9rMuNRmfsIkwccdFvM8giyUJCjNYNcvns0jSxaj-Ga0s_99wQ==)
36. [samuelfhopkins.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHizMqXHYjase5bNQeJT41YSyjf_mSm6hOqtlS2ymLQ-qqY9iwWwaE_2M90OU9GEIfP1-hiiw_2UMQo5t2_p3F8jH9xID0jH66PG2kT0al2b4VbIQ8WQxVZHXcCorIKNTIyhAJ30oeK8aSIdt0EcuxD1sDPGrQ=)
37. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIbm-fN4Bv-xmk1jjd45RebyqskB40WI-qCntrHmjIco79gLnAklf8dT8r-qd6smK02sMJf28j5uKnCBt2oi4O7O8UUs65F33eqSrlexCUuOMJKm-cwIn6ghTNNVaAuLFKwfcA6Acr1_XZqyyWSQK_sNc9WDq9sp1tFw0=)
38. [ism.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfsjOxmyZ0ePy3I8mkgV7wR5YihMzyLxsYYVSAJnTiAXFrgKXC2w7GLLepOEzmDKzrAhe4I5W5uLfIvpBOBPVlzw7xj3ItxebS6Uf1kEX7IQyLzPmnh0ZgErX0qwVuN7DOggqCWO0wnkA8-tmi4BkQw5k=)
39. [osti.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5K4YwT-UKLlpdL1UTFl7FYzBAvgX-6xk5nk7Yqc4KL34pry-8JbqHFBrqqQzfsGNlrbmJp006KjUGSFjEKnFgH2lVUl1i1zhRI4Tre68ChULCs7Ej30do)

