# Kronecker coefficient polytopes (Mulmuley-Narayanan-Sohoni) 2024-2026 frontier

**Pythia queue id:** 208
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdSMGdQYXZtVU9fYm5qTWNQbHM3dThBcxIXUjBnUGF2bVVPX2Juak1jUGxzN3U4QXM
**Elapsed:** 247s
**Completed at:** 2026-05-21T18:04:48.295348+00:00

---

# Kronecker Coefficient Polytopes and the Mulmuley-Narayanan-Sohoni Framework: The 2024-2026 Frontier

### Key Points
*   **Research suggests** that the geometric complexity of Kronecker coefficients remains exceptionally high, with the problem of deciding their positivity formally proven to be NP-hard, dampening earlier hopes for a simple polytopal resolution.
*   **It appears highly likely** that the boundary between ordinary Kronecker coefficients and reduced Kronecker coefficients is virtually non-existent, as recent explicit constructions show every Kronecker coefficient is equivalent to a reduced Kronecker coefficient.
*   **The evidence leans toward** the Monical-Tokcan-Yong conjecture holding true for restricted classes, as mathematical proofs confirm the Saturated Newton Polytope (SNP) property for Kronecker products of Schur functions with limited row lengths.
*   **Recent advancements indicate** that while exact volume computation of Kostka polytopes is #P-hard, deterministic polynomial-time approximations are achievable up to sub-exponential factors, offering new tools for random matrix theory.

### Executive Overview
The study of Kronecker coefficients, a central topic in algebraic combinatorics and representation theory, has been driven by their critical role in Geometric Complexity Theory (GCT)—a program initiated to resolve the P versus NP and VP versus VNP questions. The Mulmuley-Narayanan-Sohoni (MNS) framework previously established that analogous quantities, the Littlewood-Richardson (LR) coefficients, possess positivity that can be decided in strongly polynomial time due to their polytopal saturation properties. 

However, the 2024-2026 research frontier has fundamentally altered expectations for Kronecker coefficients. Work by researchers such as Ikenmeyer, Panova, Narayanan, and Srivastava has established severe computational hardness results for Kronecker and reduced Kronecker coefficients, while simultaneously forging new geometric pathways. These pathways include the discovery of Saturated Newton Polytopes for Kronecker products in restricted dimensions and the development of deterministic approximation algorithms for Kostka polytope volumes. 

### Structure of this Report
This report provides an exhaustive analysis of the 2024-2026 frontier in Kronecker coefficient polytopes and the legacy of the Mulmuley-Narayanan-Sohoni framework. It is structured into comprehensive sections detailing the representation-theoretic foundations, the MNS polytopal paradigm, the breakthrough equivalencies between standard and reduced Kronecker coefficients, advancements in Saturated Newton Polytopes, algorithmic progress in Kostka polytopes, and the subsequent ramifications for Geometric Complexity Theory and quantum complexity.

***

## 1. Introduction to Kronecker Coefficients and Geometric Complexity Theory

The Kronecker coefficients of the symmetric group, denoted as \(g(\lambda, \mu, \nu)\) or \(\mathbf{k}(\lambda, \mu, \nu)\), represent an 85-year-old mystery in algebraic combinatorics and representation theory [cite: source: 4, source: 21]. Originally introduced by Francis Murnaghan in 1938, they are defined as the multiplicities of an irreducible \(S_n\)-module (Specht module) \(\mathbb{S}_\nu\) in the tensor product of two other irreducible modules \(\mathbb{S}_\lambda \otimes \mathbb{S}_\mu\) [cite: source: 1, source: 50]. 

In terms of symmetric functions, the Kronecker product \(\ast\) is defined on the Schur basis as:
\[ s_\lambda \ast s_\mu := \sum_\nu g(\lambda, \mu, \nu) s_\nu \]
This mathematical operation is extended by linearity and is equivalent to the inner product of \(S_n\) characters under the characteristic map [cite: source: 3, source: 46]. Via Schur-Weyl duality, these coefficients can also be interpreted as the dimensions of \(GL_N\) highest weight spaces—specifically, \(g(\lambda, \mu, \nu)\) is the dimension of the projection of \(V_\lambda(A \otimes B)\) to \(V_\mu(A) \times V_\nu(B)\), where \(V\) represents irreducible Weyl modules [cite: source: 3, source: 17].

### 1.1 Stanley's Open Problem and GCT Motivation
Despite being fundamental structure constants, Kronecker coefficients lack "nice formulas" [cite: source: 5, source: 18]. Finding a manifestly positive combinatorial interpretation for the Kronecker coefficients is widely known as Richard Stanley's 10th open problem in algebraic combinatorics, posed in 2000 [cite: source: 4, source: 21]. 

The urgency to understand these coefficients has been heavily reinforced by their role in Geometric Complexity Theory (GCT). GCT, spearheaded by Ketan Mulmuley and Milind Sohoni, is a sweeping program aimed at establishing computational lower bounds and ultimately separating algebraic complexity classes like VP and VNP (the algebraic analogues of P vs. NP) [cite: source: 19, source: 27]. In GCT, proving lower bounds requires identifying "multiplicity obstructions"—showing that certain representation-theoretic multiplicities (like Kronecker or plethysm coefficients) vanish in one context but are strictly positive in another [cite: source: 7, source: 9]. 

### 1.2 The Positivity Problem
For GCT to succeed, researchers need to understand these multiplicities not just algebraically, but computationally and asymptotically [cite: source: 6, source: 27]. A fundamental computational challenge is the Positivity Problem: given partitions \(\lambda, \mu, \nu\), can we efficiently decide if \(g(\lambda, \mu, \nu) > 0\)? Understanding the boundaries of this problem—and the geometric polytopes that encode it—forms the core of the Mulmuley-Narayanan-Sohoni investigations and the recent 2024-2026 frontier [cite: source: 30, source: 31].

***

## 2. The Mulmuley-Narayanan-Sohoni (MNS) Paradigm and Polytopal Formulations

To understand the modern frontier of Kronecker polytopes, one must examine the baseline established by the Mulmuley-Narayanan-Sohoni (MNS) framework. In a seminal 2012 paper, "Geometric complexity theory III: on deciding nonvanishing of a Littlewood-Richardson coefficient," Mulmuley, Narayanan, and Sohoni demonstrated that the positivity of Littlewood-Richardson (LR) coefficients can be decided in strongly polynomial time [cite: source: 3, source: 5].

### 2.1 Littlewood-Richardson Coefficients vs. Kronecker Coefficients
Littlewood-Richardson coefficients, \(c_{\mu, \nu}^\lambda\), are the analogues of the Kronecker coefficients for representations of the complex linear groups \(GL_n(\mathbb{C})\) [cite: source: 31, source: 48]. MNS showed that determining whether \(c_{\mu, \nu}^\lambda > 0\) is in the complexity class \(\mathsf{P}\) [cite: source: 1, source: 31]. 

The MNS proof relied critically on two properties that LR coefficients possess, but which Kronecker coefficients generally lack:
1.  **Polytopal Representation**: The LR coefficients count the number of integer points in well-defined polytopes (such as Knutson-Tao hives or Gelfand-Tsetlin polytopes) [cite: source: 28, source: 32].
2.  **The Saturation Property**: Proved by Knutson and Tao in 1999, the saturation theorem states that for any integer \(N > 0\), \(c_{N\lambda, N\mu}^{N\nu} > 0 \iff c_{\lambda, \mu}^\nu > 0\) [cite: source: 1, source: 31].

Because of the saturation property, the polytope corresponding to the LR coefficient has an integral vertex whenever it is non-empty [cite: source: 1, source: 14]. MNS, alongside independent work by De Loera and McAllister, utilized this fact. Since the inequalities defining these polytopes have specific structures (e.g., matrices with entries from \(\{-1, 0, 1\}\)), one can apply Éva Tardos's algorithm for combinatorial linear programming to solve the membership/non-emptiness problem in strongly polynomial time [cite: source: 28, source: 32].

### 2.2 The Failure of Saturation for Kronecker Coefficients
The initial hope for GCT was that Kronecker coefficients might exhibit a similar saturation property, leading to a polynomial-time decision algorithm for their positivity. However, Kronecker coefficients notoriously fail the saturation property [cite: source: 1, source: 15]. 

A classical counterexample is that \(\mathbf{k}((2^2), (2^2), (2^2)) = 1\), but \(\mathbf{k}((1^2), (1^2), (1^2)) = 0\) [cite: source: 1, source: 40]. Furthermore, recent findings by Pak, Panova, and others have shown that even for partitions with few rows, or under different "scaling operations" (like bit scaling), the saturation property easily fails [cite: source: 15, source: 47]. This failure removes the guarantee that the corresponding Kronecker polytopes will have integral vertices when non-empty, immediately obstructing the MNS linear programming approach.

### 2.3 The Semigroup Property
While saturation fails, Kronecker coefficients do satisfy a weaker geometric condition known as the **semigroup property** [cite: source: 1, source: 27]. If \(\alpha_1, \beta_1, \gamma_1 \vdash n\) and \(\alpha_2, \beta_2, \gamma_2 \vdash m\) satisfy \(g(\alpha_i, \beta_i, \gamma_i) > 0\) for \(i=1,2\), then:
\[ g(\alpha_1 + \alpha_2, \beta_1 + \beta_2, \gamma_1 + \gamma_2) \ge \max\{g(\alpha_1, \beta_1, \gamma_1), g(\alpha_2, \beta_2, \gamma_2)\} \]
This property implies that if \(\mathbf{k}(\lambda, \mu, \nu) > 0\), then for all \(N > 0\), \(\mathbf{k}(N\lambda, N\mu, N\nu) > 0\) [cite: source: 1, source: 3]. While this is the "forward" direction of saturation, the failure of the "reverse" direction is what fundamentally escalates the computational complexity of the Kronecker positivity problem [cite: source: 15, source: 31].

***

## 3. The 2024-2026 Frontier: Reduced Kronecker Coefficients and NP-Hardness

Given the difficulty of standard Kronecker coefficients, mathematical attention historically shifted to **reduced Kronecker coefficients** (also known as Murnaghan's reduced Kronecker coefficients). These were viewed as an intermediate step between the tractable Littlewood-Richardson coefficients and the intractable standard Kronecker coefficients [cite: source: 1, source: 15]. 

### 3.1 Definition of Reduced Kronecker Coefficients
The reduced Kronecker coefficient, denoted \(\bar{\mathbf{k}}(\alpha, \beta, \gamma)\), is defined as a stable limit of ordinary Kronecker coefficients as the first part of the partitions grows arbitrarily large [cite: source: 1, source: 48]. Specifically:
\[ \bar{\mathbf{k}}(\alpha, \beta, \gamma) := \lim_{n \to \infty} \mathbf{k}((n-|\alpha|, \alpha), (n-|\beta|, \beta), (n-|\gamma|, \gamma)) \]
for arbitrary partitions \(\alpha, \beta, \gamma\) [cite: source: 1, source: 41]. Unlike standard Kroneckers, we do not require \(|\alpha| = |\beta| = |\gamma|\). When \(|\nu| = |\lambda| + |\mu|\), the reduced Kronecker coefficient surprisingly recovers the Littlewood-Richardson coefficient \(c_{\lambda, \mu}^\nu\) [cite: source: 18]. 

Because of this direct generalization of LR coefficients, it was widely conjectured by Kirillov (2004) and Klyachko (2004) that reduced Kronecker coefficients *did* satisfy the saturation property [cite: source: 1, source: 14]. If true, this might have yielded a polynomial-time algorithm for their positivity via a modified MNS approach.

### 3.2 The Collapse of the Saturation Hope
The hope for a polytopal easy-decision algorithm was shattered in 2020 when Pak and Panova disproved the saturation property for reduced Kronecker coefficients [cite: source: 14, source: 16]. They moved the reduced Kroneckers strictly away from the Littlewood-Richardson coefficients on the spectrum of complexity [cite: source: 14, source: 48]. 

### 3.3 The 2024 Breakthrough: Equivalence of Standard and Reduced Kroneckers
In a major 2024 publication in *Forum of Mathematics, Pi*, Christian Ikenmeyer and Greta Panova definitively settled the spectrum debate with the paper "All Kronecker coefficients are reduced Kronecker coefficients" [cite: source: 14, source: 41]. 

They proved that every ordinary Kronecker coefficient of the symmetric group is exactly equal to a reduced Kronecker coefficient via an explicit construction [cite: source: 1, source: 48]. 
This breakthrough has several profound implications:
*   **Combinatorial Interpretations**: It proved the equivalence of two major open problems: Stanley's problem from 2000 regarding the combinatorial interpretation of ordinary Kronecker coefficients, and Kirillov's problem from 2004 regarding reduced Kronecker coefficients [cite: source: 1, source: 16].
*   **Highest Weight Vector Spaces**: The proof provided an explicit isomorphism of the corresponding highest weight vector spaces within the context of the general linear group \(GL_N\) [cite: source: 1, source: 41].

### 3.4 Computational Complexity: NP-Hardness and #P-Hardness
Before 2024, it was known that computing ordinary Kronecker coefficients was \(\mathsf{\#P}\)-hard (Bürgisser and Ikenmeyer, 2008), and computing reduced Kronecker coefficients was also \(\mathsf{\#P}\)-hard (Pak and Panova, 2020) [cite: source: 1, source: 13]. It was also known that deciding the *positivity* of ordinary Kronecker coefficients was \(\mathsf{NP}\)-hard (Ikenmeyer, Mulmuley, and Walter, 2017) [cite: source: 1, source: 41]. 

However, the complexity of deciding the positivity of *reduced* Kronecker coefficients remained an open conjecture [cite: source: 1, source: 40]. The 2024 Ikenmeyer-Panova equivalence theorem resolved this entirely:
*   **Positivity is NP-Hard**: Deciding if \(\bar{\mathbf{k}}(\alpha, \beta, \gamma) > 0\) is \(\mathsf{NP}\)-hard when the inputs are given in unary [cite: source: 16, source: 40].
*   **Computation is strongly #P-Hard**: Computing \(\bar{\mathbf{k}}(\alpha, \beta, \gamma)\) is \(\mathsf{\#P}\)-hard under parsimonious many-one reductions, upgrading the previous Turing-reduction hardness [cite: source: 1, source: 16].

This mathematically formalizes the fact that MNS-style strongly polynomial time algorithms via integer point counting in saturation-backed polytopes cannot exist for either family of Kronecker coefficients, unless \(\mathsf{P} = \mathsf{NP}\) [cite: source: 1, source: 32].

| Coefficient Type | Geometric Polytope Saturation? | Positivity Decision Complexity | Exact Computation Complexity |
| :--- | :--- | :--- | :--- |
| **Littlewood-Richardson (\(c_{\lambda, \mu}^\nu\))** | Yes (Knutson-Tao Hive) | \(\mathsf{P}\) (Strongly Polynomial) | \(\mathsf{\#P}\)-complete |
| **Kronecker (\(g(\lambda, \mu, \nu)\))** | No | \(\mathsf{NP}\)-hard | \(\mathsf{\#P}\)-hard / GapP |
| **Reduced Kronecker (\(\bar{\mathbf{k}}(\alpha, \beta, \gamma)\))** | No | \(\mathsf{NP}\)-hard (Proven 2024) | \(\mathsf{\#P}\)-hard (parsimonious) |

***

## 4. Saturated Newton Polytopes for the Kronecker Product

With traditional integer-point counting algorithms blocked by \(\mathsf{NP}\)-hardness, geometric algebraic combinatorics has pivoted toward understanding the support of the polynomials associated with these coefficients. A major structural concept defining the 2024-2025 frontier is the **Saturated Newton Polytope (SNP)** [cite: source: 3, source: 4].

### 4.1 Definition of Saturated Newton Polytopes
Given a multivariate polynomial with nonnegative coefficients \(f(x_1, \dots, x_k) = \sum_\alpha c_\alpha x^\alpha\), the Newton polytope of \(f\), denoted \(N_k(f)\), is the convex hull of the exponent vectors: \(N_k(f) := \text{Conv}(M_k(f))\), where \(M_k(f) := \{(\alpha_1, \dots, \alpha_k) : c_\alpha > 0\}\) [cite: source: 3, source: 19]. 

A polynomial \(f\) is said to have a Saturated Newton Polytope (SNP) if the set of actual exponent vectors exactly coincides with the integer points of its convex hull, i.e., \(M_k(f) = N_k(f) \cap \mathbb{Z}^k\) [cite: source: 19, source: 46]. If a symmetric function \(f\) has a saturated Newton polytope for all specializations \(f(x_1, \dots, x_k)\) for \(k \ge 1\), then \(f\) itself is said to have the SNP property [cite: source: 3, source: 21].

### 4.2 The Monical-Tokcan-Yong Conjecture
In 2019, Monical, Tokcan, and Yong initiated the broad study of SNP properties in algebraic combinatorics, establishing it for Schur, skew Schur, Stanley symmetric functions, and Macdonald polynomials [cite: source: 22, source: 46]. They proposed a highly significant conjecture regarding Kronecker coefficients:
*   **Conjecture (MTY 2019)**: The Kronecker product \(s_\lambda \ast s_\mu = \sum_\nu g(\lambda, \mu, \nu) s_\nu\) has a saturated Newton polytope [cite: source: 3, source: 21].

If true, this implies a rigid, "hole-free" geometric structure to the monomials generated by the Kronecker product, serving as a necessary condition for stronger properties like Lorentzian dynamics or log-concavity [cite: source: 21, source: 22].

### 4.3 2024-2025 Proofs for Restricted Row Partitions (Panova and Zhao)
In 2024 and 2025, Greta Panova and Chenchen Zhao published major results proving special cases of the Monical-Tokcan-Yong conjecture, relying heavily on the geometric inequalities that govern Littlewood-Richardson coefficients [cite: source: 4, source: 23].

Panova and Zhao expressed the Kronecker product in the monomial basis as sums of products of multi-Littlewood-Richardson coefficients [cite: source: 4, source: 22]. They utilized the **Horn inequalities**—the exact linear inequalities that determine when an LR coefficient is strictly positive—to construct a continuous geometric polytope \(\mathcal{P}(\lambda, \mu; \mathbf{a})\) parameterized by partitions \(\lambda, \mu\) and a composition vector \(\mathbf{a} = (a_1, \dots, a_k)\) [cite: source: 4, source: 22].

Their fundamental geometric equivalence states:
*   Let \(\mu, \lambda \vdash n\). The Kronecker product \(s_\lambda \ast s_\mu(x_1, \dots, x_k)\) has a saturated Newton polytope if and only if for every \(\mathbf{a} \in \mathbb{Z}^k\), the polytope \(\mathcal{P}(\lambda, \mu; \mathbf{a})\) is either empty or contains an integer point [cite: source: 4, source: 21].

Through this geometric lens, Panova and Zhao successfully proved the MTY conjecture for two and three-row partitions:
1.  **Theorem**: Let \(\lambda, \mu \vdash n\) with \(\ell(\lambda) \le 2\), \(\ell(\mu) \le 3\), and \(\mu_1 \ge \lambda_1\). Then \(s_\lambda \ast s_\mu(x_1, \dots, x_k)\) has a saturated Newton polytope for every \(k \in \mathbb{N}\) [cite: source: 3, source: 21].
2.  **Theorem**: Let \(\lambda, \mu \vdash n\) with \(\ell(\lambda) \le 3\) and \(\ell(\mu) \le 2\). Then the specific truncation \(s_\lambda \ast s_\mu(x_1, x_2, x_3)\) has a saturated Newton polytope [cite: source: 21, source: 44].

The proofs operate by showing that in these restricted cases, the Kronecker product contains a unique maximal term \(s_\nu\) where \(\nu\) dominates all other partitions in the product under the dominance order [cite: source: 20, source: 46]. Consequently, the Newton polytope simply consists of all integer points \((a_1, \dots, a_k)\) such that their sorted permutation is dominated by \(\nu\) [cite: source: 46].

### 4.4 Doubts on the General SNP Property
While the Panova-Zhao theorems solidify the SNP property for restricted lengths, they also cast doubt on the general validity of the Monical-Tokcan-Yong conjecture for arbitrary partitions. When lengths increase, the Kronecker product often contains multiple incomparable maximal terms in the dominance order (e.g., in the product \(s_{(6,6)} \ast s_{(8,2,1,1)}\), the terms \((7,5)\) and \((8,3,1)\) are incomparable maximal terms) [cite: source: 46]. 

Because the relevant Horn inequalities result in many non-integral vertices for \(\mathcal{P}(\lambda, \mu; \mathbf{a})\), it remains far from clear if these arbitrary polytopes will always guarantee an integer point when non-empty [cite: source: 19, source: 21]. Resolving this computationally is difficult precisely because deciding Kronecker positivity is \(\mathsf{NP}\)-hard [cite: source: 21, source: 50].

***

## 5. Algorithmic Advances in Kostka Polytopes (Narayanan & Srivastava 2025-2026)

Alongside Kronecker coefficients, Kostka numbers and their corresponding geometric spaces, **Kostka polytopes**, are fundamental quantities in representation theory with direct ties to the GCT program [cite: source: 5, source: 37]. 

### 5.1 Definition and Significance of Kostka Polytopes
A Kostka polytope, denoted \(\mathrm{GT}(\lambda, \mu)\), represents the continuous geometric relaxation of Kostka numbers [cite: source: 10, source: 33]. The volume of a Kostka polytope is of paramount interest not only in algebraic combinatorics but specifically in Random Matrix Theory. 

In the **randomized Schur-Horn problem**, one evaluates the probability density that a random Hermitian matrix, sampled from the unitarily invariant measure with a fixed spectrum \(\lambda\), has a specific diagonal \(\mu\) [cite: source: 10, source: 36]. The probability density of this distribution is equal to the volume of the Kostka polytope \(\mathrm{GT}(\lambda, \mu)\) up to an exactly and efficiently computable multiplicative constant [cite: source: 33, source: 37].

### 5.2 The Hardness of Exact Computation
Historically, Barvinok and Fomin (1997) proved that the entire collection of Kostka numbers corresponding to \(\lambda\) can be computed in time polynomial in the input and output lengths [cite: source: 11, source: 37]. However, Hariharan Narayanan showed in 2006 that computing a single Kostka number in binary is \(\mathsf{\#P}\)-complete [cite: source: 11, source: 32].

Under standard complexity-theoretic assumptions, this hardness result extends to the continuous realm: exactly computing the continuous volume of the Kostka polytope \(\mathrm{GT}(\lambda, \mu)\) is strictly intractable when \(\lambda\) and \(\mu\) are specified in binary [cite: source: 11, source: 37].

### 5.3 Deterministic Approximation Algorithm (2025-2026)
One of the most significant open problems in computational geometry is the polynomial-time deterministic approximation of polytope volumes up to a factor that grows at most sub-exponentially with the dimension [cite: source: 10, source: 37]. 

In a landmark paper ("Deterministically Approximating the Volume of a Kostka Polytope," 2025/2026), Hariharan Narayanan and Piyush Srivastava successfully resolved this for the Kostka class [cite: source: 10, source: 37]. They provided a polynomial-time deterministic algorithm for approximating the volume of an \(\Omega(n^2)\)-dimensional Kostka polytope \(\mathrm{GT}(\lambda, \mu)\) [cite: source: 5, source: 33]. 

**Algorithmic Parameters and Bounds:**
*   **Approximation Factor**: The algorithm approximates the volume to within a multiplicative factor of \(\exp(O(n \log n))\) [cite: source: 10, source: 37].
*   **Constraints**: The algorithm operates when \(\lambda\) is an integral partition with \(n\) distinct parts, bounded above by a polynomial in \(n\), and \(\mu\) is an integer vector lying strictly in the interior of the permutohedron (the convex hull of all permutations) of \(\lambda\) [cite: source: 10, source: 33].
*   **Methodology**: The mathematical approach leverages a partition function interpretation of a continuous analogue of Schur polynomials, utilizing a maximum entropy principle to construct Gibbs probability distributions over the polytope space [cite: source: 11, source: 36].

This breakthrough allows for asymptotically correct estimates of the log-volume of Kostka polytopes in time strictly polynomial in \(n\), \(|\lambda|\), and the representation length of the inputs [cite: source: 10, source: 37]. It represents a highly refined application of discrete tomography, vastly outperforming exact enumeration techniques [cite: source: 5, source: 37].

***

## 6. Quantum Complexity and Moment Polytopes

The 2024-2026 frontier has also expanded the study of Kronecker coefficients into quantum computational complexity. Because classical evaluation algorithms face \(\mathsf{\#P}\)-hard constraints and exact zero/non-zero bounds face \(\mathsf{NP}\)-hard blocks, researchers have mapped these coefficients to quantum state spaces.

### 6.1 Containment in QMA (Bravyi et al., 2024)
In a 2024 study, Bravyi, Chowdhury, Gosset, Havlíček, and Zhu investigated the quantum complexity of Kronecker coefficients [cite: source: 49]. They demonstrated that a given Kronecker coefficient \(g(\lambda, \mu, \nu)\) is proportional to the rank of a projector that can be measured efficiently using a quantum computer [cite: source: 49]. 

Specifically, the Kronecker coefficient counts the dimension of the vector space spanned by the accepting witnesses of a \(\mathsf{QMA}\) verifier (\(\mathsf{QMA}\) being the quantum analogue of \(\mathsf{NP}\)) [cite: source: 49]. 
*   If \(g(\lambda, \mu, \nu) > 0\), there exists a quantum state that results in a measurement outcome of \(+1\).
*   If \(g(\lambda, \mu, \nu) = 0\), all states give a measurement outcome of \(0\) [cite: source: 49].

This quantum protocol is deterministic, possessing perfect completeness and soundness. Consequently, Bravyi et al. proved that deciding the positivity of Kronecker coefficients is contained strictly within the \(\mathsf{QMA}\) complexity class [cite: source: 49]. This quantum upper bound perfectly complements the classical lower bound (\(\mathsf{NP}\)-hardness) established by Ikenmeyer, Mulmuley, and Walter [cite: source: 41, source: 49].

### 6.2 Relative Error Approximation
The quantum structural connection implies that approximating Kronecker coefficients to within a given relative error is no harder than a natural class of quantum approximate counting problems [cite: source: 49]. These counting problems closely mirror the computational complexity of estimating thermal properties of quantum many-body systems [cite: source: 49]. While exact computation (the "ExactKron" problem) remains firmly \(\mathsf{\#P}\)-hard (and within \(\mathsf{GapP}\)), these quantum heuristic boundaries provide a novel mechanism for bounding large Kronecker sums [cite: source: 31, source: 49].

***

## 7. Ramifications for the Geometric Complexity Theory (GCT) Program

The aggregate results of the 2024-2026 frontier—NP-hardness of reduced Kroneckers, SNP geometries, and quantum characterizations—profoundly impact the Mulmuley-Sohoni Geometric Complexity Theory program.

### 7.1 The Shift to Plethysm Coefficients
In the original GCT blueprint, bounding the permanent polynomial (to separate \(\mathsf{VP}\) and \(\mathsf{VNP}\)) was heavily reliant on Kronecker coefficients [cite: source: 6, source: 27]. However, recognizing the limitations and the failure of Kronecker saturation, the vanguard of GCT has increasingly shifted its focus to **plethysm coefficients** [cite: source: 5, source: 6]. 

Plethysm coefficients represent the multiplicities in the coordinate rings of spaces of polynomials, taking the role that Kronecker coefficients initially held [cite: source: 5, source: 27]. Unfortunately, plethysm coefficients suffer from similar computational intractability: deciding their positivity is \(\mathsf{NP}\)-hard, and computing them is \(\mathsf{\#P}\)-hard, even if the inner parameter of the plethysm coefficient is fixed [cite: source: 5, source: 27]. 

Despite this, new equalities between certain plethysm coefficients and Kronecker coefficients have been discovered through discrete tomography [cite: source: 5, source: 9]. Panova and Ikenmeyer have utilized these to prove that in the GCT program, the vanishing of rectangular Kronecker coefficients cannot be used to prove superpolynomial determinantal complexity lower bounds for the permanent polynomial—effectively killing one of the "wishful" approaches of the early GCT framework [cite: source: 6, source: 9].

### 7.2 Separations in Moment Polytopes
To continue the pursuit of GCT separations, researchers have begun calculating exact geometries for **moment polytopes** of tensors [cite: source: 25]. A moment polytope collects "rank-like" information about tensors, originating from symplectic geometry and invariant theory [cite: source: 25]. 

Recent algorithmic breakthroughs have enabled the computation of moment polytopes for tensors of dimensions an order of magnitude larger than previous methods (e.g., evaluating all moment polytopes in \(\mathbb{C}^3 \otimes \mathbb{C}^3 \otimes \mathbb{C}^3\)) [cite: source: 25]. Guided by these algorithms, researchers have successfully proved mathematical separations between the moment polytopes of matrix multiplication tensors and unit tensors [cite: source: 25]. 

Crucially, this proved that the matrix multiplication moment polytopes are *not maximal* (i.e., they are not equal to the corresponding Kronecker polytopes), providing a localized no-go result for certain operational characterizations of Strassen's asymptotic restriction [cite: source: 25]. This detailed polytopal mapping represents the current active methodology of GCT in bypassing the \(\mathsf{NP}\)-hard roadblocks of Kronecker positivity [cite: source: 25, source: 30].

***

## 8. Conclusion and Future Directions

The investigation of Kronecker coefficient polytopes over the 2024-2026 period has matured the field of algebraic combinatorics from a search for simple formulas into a deeply structural, complexity-theoretic discipline. 

The Mulmuley-Narayanan-Sohoni paradigm successfully conquered Littlewood-Richardson coefficients via saturation and combinatorial linear programming [cite: source: 3, source: 32]. However, the 2024 theorem by Ikenmeyer and Panova definitively established that ordinary and reduced Kronecker coefficients are identical in nature, and both reside strictly in \(\mathsf{NP}\)-hard / \(\mathsf{\#P}\)-hard territory [cite: source: 16, source: 48]. The absence of the saturation property means that simple polytopal algorithms for Kronecker coefficients do not exist unless \(\mathsf{P} = \mathsf{NP}\) [cite: source: 1, source: 48].

Nevertheless, the geometric approach continues to bear fruit. The Monical-Tokcan-Yong conjecture concerning Saturated Newton Polytopes for Kronecker products has been rigorously proven by Panova and Zhao for restricted row lengths, revealing intricate geometric structures guided by Horn inequalities [cite: source: 4, source: 21]. Simultaneously, algorithmic advances by Narayanan and Srivastava have shown that while exact geometric calculations are intractable, deterministic sub-exponential approximations for related structures like the Kostka polytope are highly feasible [cite: source: 10, source: 33]. 

As the field looks ahead, the intersection of quantum complexity (where Kronecker positivity sits natively in \(\mathsf{QMA}\)) [cite: source: 49] and the explicit geometric separation of moment polytopes [cite: source: 25] dictate the new frontier. Solving Stanley's 10th problem may ultimately require entirely new mathematical vocabularies that transcend traditional integer-point enumeration, acknowledging the inherent computational hardness deeply embedded within the symmetric group's representation theory.
