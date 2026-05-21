# Hall-Littlewood polynomial positivity / interpretations 2024-2026

**Pythia queue id:** 200
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcwME1QYXBLcERvMk4xTWtQcDg3VzRROBIXMDBNUGFwS3BEbzJOMU1rUHA4N1c0UTg
**Elapsed:** 253s
**Completed at:** 2026-05-21T17:45:53.598042+00:00

---

# Comprehensive Report on Hall-Littlewood Polynomial Positivity and Interpretations (2024–2026)

**Key Points:**
*   **Schur Positivity under the Nabla Operator**: In 2026, researchers successfully resolved the two-column case of the Bergeron–Garsia–Haiman–Tesler conjectures, establishing the Schur positivity of the nabla operator (\(\nabla^k\)) applied to modified Hall-Littlewood polynomials. 
*   **Lusztig $q$-Weight Multiplicities**: The classical Kostka-Foulkes positivity of Type A has been explicitly extended to Lie types B and C. Between 2024 and 2025, exact combinatorial formulas were developed using the energy functions of Kirillov-Reshetikhin (KR) crystals.
*   **Combinatorial Innovations via Multiline Queues**: Novel combinatorial interpretations of the $q$-Whittaker and modified Hall-Littlewood polynomials have been discovered using multiline queues and diagrams. By utilizing `charge` and `cocharge` statistics on reading words, researchers have bypassed the computationally heavy Ferrari-Martin algorithm.
*   **Infinite-Dimensional Harmonic Functionals**: For applications in probability and infinite-dimensional unitary groups over finite fields, the mathematical characterization of $t$-HL-positive harmonic functionals on the algebra of symmetric functions saw major structural breakthroughs in 2026.
*   **Non-Archimedean GUE Processes**: Hall-Littlewood processes have been intrinsically linked to the corners processes of random non-Archimedean matrices (alternating and Hermitian) through modules over spherical Hecke algebras, expanding their footprint in modern random matrix theory.

**Overview:**
The Hall-Littlewood polynomials represent a remarkable basis of symmetric functions that interpolate between Schur polynomials and monomial symmetric functions. Over the period of 2024–2026, the study of their algebraic, combinatorial, and probabilistic properties has seen an explosion of breakthroughs, collectively referred to as "positivity" theorems. In algebraic combinatorics, establishing that a polynomial expands positively (i.e., with non-negative integer coefficients) in a certain basis typically implies that the mathematical object is not merely a formal algebraic sum, but rather a genuine character of a naturally occurring algebraic module, revealing deep underlying geometric or representation-theoretic phenomena. This report exhaustively synthesizes the state of research from 2024 to 2026 concerning Hall-Littlewood polynomial positivity and its wide-ranging interpretations spanning representation theory, random matrix theory, lattice enumeration, and statistical mechanics.

---

## 1. Introduction and Foundations of Hall-Littlewood Polynomials

To properly contextualize the rapid developments of 2024–2026, it is imperative to establish the foundational definitions of Hall-Littlewood (HL) polynomials and their surrounding symmetric function theory. 

Symmetric functions are polynomials defined over infinitely many variables that remain invariant under any permutation of those variables. The Hall-Littlewood polynomials \( P_\lambda(x; t) \) are a family of symmetric functions indexed by integer partitions \( \lambda = (\lambda_1, \lambda_2, \dots, \lambda_n) \) and dependent on a parameter \( t \) [cite: 1, 2]. They serve as a vital interpolating basis. When evaluated at \( t = 0 \), they yield the Schur functions \( s_\lambda(x) \), which describe the irreducible characters of the general linear group and symmetric group. When evaluated at \( t = 1 \), they reduce to the monomial symmetric functions \( m_\lambda(x) \) [cite: 2, 3]. 

### 1.1 Transformed and Modified Hall-Littlewood Polynomials

Modern research often relies on specific normalizations and transformations of the classical basis. The **transformed Hall-Littlewood polynomials**, denoted \( H_\mu(x; q) \), are defined directly through their expansion into the Schur basis via the Kostka-Foulkes polynomials \( K_{\lambda\mu}(q) \) [cite: 1]:
\[ H_\mu(x; q) := \sum_\lambda K_{\lambda\mu}(q) s_\lambda(x) \]
These functions can also be defined utilizing raising operators: \( H_\mu(x; q) = \prod_{i<j} (1 - q R_{ij})^{-1} s_\mu(x) \) [cite: 1].

Alternatively, the **modified Hall-Littlewood polynomials**, \( \tilde{H}_\mu(x; q) \), are a distinct specialization derived directly from the modified Macdonald polynomials \( \tilde{H}_\mu(x; q, t) \). Specifically, they are obtained by setting the Macdonald parameter \( q = 0 \) [cite: 4, 5]. They are related to the transformed basis by a simple degree shifting: \( \tilde{H}_\lambda(x; t) = t^{n(\lambda)} H_\lambda(x; t^{-1}) \) [cite: 1, 6]. 

### 1.2 The Concept of Positivity

A pervasive pursuit in this field is **Schur positivity**, which mandates that the coefficients in the Schur expansion of these functions are polynomials with non-negative integer coefficients, meaning they reside in \( \mathbb{N}[q, t] \) [cite: 4, 7]. The modified Hall-Littlewood polynomials are inherently Schur-positive. Historically, their Schur positivity was proven geometrically, as they arise as the graded Frobenius characteristics of the Garsia-Procesi modules, which encode the cohomology rings of Springer fibers [cite: 4, 8].

The fundamental basis of this positivity is determined by combinatorial statistics. In a famous result, Lascoux and Schützenberger discovered the **charge** and **cocharge** statistics on semistandard Young tableaux [cite: 8]. The Schur expansion of the transformed HL polynomial is given by the charge statistic:
\[ H_\mu(x; q) = \sum_{T \in SSYT(\mu)} q^{charge(T)} s_{sh(T)} \]
Similarly, the modified HL polynomials expand using the cocharge statistic [cite: 8]. Between 2024 and 2026, finding positive combinatorial descriptions for related operations, generalizations to other Lie types, and establishing identical positivity for generalized operator actions remained central to algebraic combinatorics.

---

## 2. Schur Positivity and the Nabla Operator: The Two-Column Case

One of the most formidable challenges regarding Hall-Littlewood positivity involves the action of the **nabla operator (\( \nabla \))** on symmetric functions. In 2026, research by Menghao Qu made monumental strides by affirmatively settling long-standing conjectures related to this operator [cite: 7].

### 2.1 The Nabla Operator and the BGHT Conjectures

The nabla operator is an eigen-operator of the modified Macdonald polynomials, originally introduced by Bergeron, Garsia, Haiman, and Tesler (BGHT). It has become a central object in modern algebraic combinatorics [cite: 4, 7]. A quintessential example of nabla's geometric significance is the symmetric function \( \nabla e_n \), whose Schur positivity follows from its realization as the Frobenius characteristic of the module of diagonal harmonics [cite: 4, 7].

Understanding the action of \( \nabla \) specifically on the modified Hall-Littlewood polynomials \( \tilde{H}_\mu[X; 0, t] \) is highly nontrivial. In an influential 1999 paper, the BGHT authors posed specific conjectures regarding this action [cite: 4, 7]. BGHT Conjecture II essentially hypothesized the following positivity constraint for any partitions \( \lambda, \mu \):
\[ \langle (-1)^{|\mu|-\ell(\mu)} \nabla \tilde{H}_\mu[X;0,t], s_\lambda \rangle \in \mathbb{N}[q, t] \]
Proving this implies that the transformed outcome is not just formal algebra but directly equates to a genuine character of a naturally occurring \( \mathcal{S}_n \)-module [cite: 4, 7].

### 2.2 Resolution of the Two-Column Conjectures (2026)

In a 2026 paper titled *"Schur positivity of the nabla operator on two-column modified Hall–Littlewood polynomials,"* Menghao Qu investigated this exact phenomenon [cite: 4]. The research successfully resolved two of the core conjectures posed by Bergeron, Garsia, Haiman, and Tesler specifically for the case where the indexing partition \( \mu \) is a two-column partition [cite: 4, 7].

Qu achieved this by establishing explicit algebraic identities that evaluate the action of \( \nabla \) on the modified Macdonald expansion [cite: 7]. The research relied heavily on manipulating \( t \)-Pochhammer symbols and tracking the Frobenius characteristics of the underlying modules [cite: 4]. 

Furthermore, Qu's methodological approach demonstrated that the established results were not isolated to a single application of the nabla operator. The proof naturally extended to arbitrary powers of the operator, \( \nabla^k \), for all integers \( k \ge 1 \) [cite: 4, 7]. By proving that the transformed polynomials map explicitly to characters in the representation theory of the symmetric group \( \mathcal{S}_n \), Qu effectively bridged a gap between symmetric function identities and geometric representation theory that had remained open for over two decades [cite: 4, 7].

---

## 3. Generalizations of Kostka-Foulkes Positivity: Lusztig $q$-Weight Multiplicities

While the classical Hall-Littlewood polynomials (and their associated Kostka-Foulkes polynomials \( K_{\lambda\mu}(q) \)) apply primarily to Type A Lie algebras (related to the general linear group \( GL_n \)), a major ongoing problem has been extending this positivity theory to other classical Lie types (Types B, C, and D) [cite: 9, 10]. The analogues of Kostka-Foulkes polynomials for other Lie types are known as **Lusztig's \( q \)-weight multiplicities** [cite: 10, 11]. 

### 3.1 The Search for Positive Combinatorial Formulas

For a simple Lie algebra \( \mathfrak{g} \) and dominant weights \( \lambda, \mu \), Lusztig's \( q \)-weight multiplicity \( K^{\mathfrak{g}}_{\lambda\mu}(q) \) is defined using the Demazure operator \( D_{w_0} \) on the Weyl group, tracking the positive roots of the algebra [cite: 10, 12]. While the theory of affine Kazhdan-Lusztig polynomials guarantees mathematically that these polynomials are non-negative (meaning their coefficients are positive integers), explicitly constructing manifestly positive combinatorial formulas for them has eluded researchers for decades [cite: 10, 13]. 

In Type A, the positivity is captured by the Lascoux-Schützenberger charge statistic over semistandard Young tableaux (SSYT) [cite: 10, 12]. For Type C, Cédric Lecouvey previously constructed a cyclage operation on Kashiwara-Nakashima tableaux, conjecturing that its associated statistics might yield a positive formula, but a complete proof remained open [cite: 10, 13].

### 3.2 Breakthroughs with Kirillov-Reshetikhin Crystals (2024–2025)

Between late 2024 and 2025, a team of researchers—Hyeonjae Choi, Donghyun Kim, and Seung Jin Lee—published seminal work resolving the positivity problem for types B and C using the framework of quantum group crystals [cite: 11, 14]. Specifically, they utilized **Kirillov-Reshetikhin (KR) crystals**, which are crystal bases for certain finite-dimensional irreducible modules over quantized affine algebras [cite: 12, 15].

Choi, Kim, and Lee presented a precise, explicit combinatorial formula for Lusztig \( q \)-weight multiplicities [cite: 11, 14]. Their formulation is given in terms of the **energy functions** of Kirillov-Reshetikhin crystals [cite: 11]. The energy function on the KR crystal mathematically serves the exact role that the charge statistic plays on semistandard Young tableaux in Type A [cite: 12, 15]. 

The authors applied this method to prove positivity for:
1.  **Type C**: For all dominant weights [cite: 12, 14].
2.  **Type B**: Specifically for dominant spin weights [cite: 12, 14].

To achieve this, they utilized semistandard oscillating tableaux (SSOT) and mapped their realization to classical highest weights embedded within the tensor products of KR column crystals [cite: 13, 15]. Furthermore, the authors introduced the concept of **level-restricted \( q \)-weight multiplicities** for nonexceptional types, proving their inherent positivity by similarly providing explicit combinatorial formulas for them [cite: 11, 14]. This established a direct duality between \( q \)-weight multiplicities and tensor product multiplicities, reviving and finalizing a traditional approach to affine crystal graphs that originated with Schur [cite: 12].

---

## 4. Combinatorial Interpretations: Multiline Queues and the Charge Statistic

In the domain of statistical mechanics and probability theory, Hall-Littlewood and Macdonald polynomials manifest in the study of the asymmetric simple exclusion process (ASEP) on a circle. In 2024–2025, Olya Mandelshtam and Jerónimo Valencia-Porras significantly advanced the combinatorial interpretation of the modified Hall-Littlewood polynomials via objects known as **multiline queues** [cite: 16, 17].

### 4.1 Bypassing the Ferrari-Martin Algorithm

Multiline queues are combinatorial matrices of balls and empty sites originally developed to describe stationary distributions of multi-type ASEP [cite: 16, 18]. Specializing the parameters of Macdonald polynomials to \( t = 0 \) yields the \( q \)-Whittaker polynomials, which previous research tied to a major index (`maj`) statistic on multiline queues calculated using the deterministic Ferrari-Martin pairing algorithm [cite: 17, 18]. The Ferrari-Martin algorithm, however, is procedurally dense and computationally expensive [cite: 17].

Mandelshtam and Valencia-Porras achieved a breakthrough by reinterpreting the `maj` statistic fundamentally as a **charge** statistic applied directly to the reading words (the column words) of the multiline queues [cite: 16, 17]. This profound observation allowed them to entirely bypass the Ferrari-Martin algorithm. By taking a multiline queue \( M \) and reading its contents column-by-column to form a word \( cw(M) \), they proved that the major index resulting from the complex ASEP pairing process is strictly equivalent to the classical charge of the word [cite: 16, 17].

### 4.2 Multiline Diagrams and Modified Hall-Littlewood Polynomials

Expanding on this, the researchers naturally extended their methodology to bosonic multiline queues, which they define as **multiline diagrams** [cite: 17, 18]. Multiline diagrams are the plethystic analogues of multiline queues. While standard multiline queues correspond to the \( q \)-Whittaker functions, multiline diagrams explicitly compute the Schur expansion of the modified Hall-Littlewood polynomials \( \tilde{H}_\lambda(X; q, 0) \) [cite: 16, 18].

By establishing an RSK-esque (Robinson-Schensted-Knuth) insertion procedure, they defined a **cocharge statistic** on the reading words of these diagrams [cite: 16, 17]. This provided a totally new family of explicitly positive formulas for modified Hall-Littlewood polynomials. The procedure, termed "collapsing," can be mapped directly to Kashiwara crystal operators on Type-A Kirillov-Reshetikhin crystals, unifying the probability models with quantum group representation theory [cite: 17].

---

## 5. Infinite-Dimensional Groups and Hall-Littlewood-Positive Harmonic Functionals

Hall-Littlewood polynomials inherently feature a parameter \( t \). In asymptotic representation theory, when considering unitary groups over a finite field \( \mathbb{F}_q \), the inverse of the field cardinality naturally substitutes for this parameter (i.e., \( t = q^{-1} \)). In April 2026, Cesar Cuenca and Grigori Olshanski published *"Hall-Littlewood-positive harmonic functionals on the algebra of symmetric functions,"* exploring this infinite-dimensional setting [cite: 19].

### 5.1 Defining the Functionals

The problem Cuenca and Olshanski tackled was describing the set of real-valued linear functionals \( \phi \) on the quotient ring of symmetric functions \( Sym / (p_2 - 1) \) [cite: 19, 20]. (Here, \( p_2 \) denotes the second power-sum symmetric function). 

They fixed a parameter \( t \in (-1, 1) \) and defined two crucial conditions for any functional \( \phi : Sym \to \mathbb{R} \):
1.  **Harmonicity**: A functional is said to be \( p_1 \)-harmonic if \( \phi(p_1 f) = \phi(f) \) for any symmetric function \( f \in Sym \). Similarly, \( p_2 \)-harmonicity implies \( \psi(p_2 f) = \psi(f) \) [cite: 19, 20].
2.  **HL-Positivity**: A functional is \( t \)-HL-positive if its evaluation on any Hall-Littlewood polynomial \( P_\lambda(\cdot; t) \) yields a non-negative real number: \( \phi(P_\lambda(\cdot; t)) \ge 0 \) for all partitions \( \lambda \). A functional can also be evaluated against the modified polynomials for \( (-t) \)-HL-positivity [cite: 19, 20].

The intersection of these two conditions forms a convex cone \( \Phi(t) \) [cite: 19, 20]. Describing the extremal rays of this cone translates directly to describing the set of **coadjoint-invariant probability measures** for the infinite-dimensional unitary group over a finite field \( U(\infty, \mathbb{F}_q) \) [cite: 19].

### 5.2 The Mixing Construction and $p_2$-Twisted Comultiplication

To parameterize these functionals, Cuenca and Olshanski demonstrated that the set is vastly large, possessing infinite dimensionality. They provided an analogue of Kerov's mixing construction—a classic technique used for representations of the infinite symmetric group [cite: 20]. 

This required the invention of a explicit **"\( p_2 \)-twisted action"** of the symmetric algebra \( Sym \) acting upon itself [cite: 20]. By doing so, they constructed a dual map that morphs the symmetric algebra into a comodule. They successfully detailed the exact relationship between this \( p_2 \)-twisted comultiplication and the standard comultiplication map on symmetric functions [cite: 20]. Ultimately, the normalized subset of these functionals forms a Choquet simplex, providing a robust probabilistic framework for dealing with asymptotic Hall-Littlewood variables [cite: 19, 20].

---

## 6. Hecke Modules, $p$-adic Random Matrices, and Non-Archimedean GUE

Another powerful manifestation of Hall-Littlewood positivity in probabilistic contexts is found in the study of non-Archimedean random matrix theory. Between 2024 and 2025, Jiahe Shen and Roger Van Peski constructed deep connections linking $p$-adic random matrices to spherical Hecke algebras using Hall-Littlewood polynomials [cite: 21, 22].

### 6.1 The Classical Hall Algebra vs. Hecke Modules

Classically, Hall-Littlewood polynomials encode information regarding subgroups and extensions of finite abelian \( p \)-groups. This relies on an isomorphism with the classical Hall algebra \( H(\mathfrak{o}) \), where \( \mathfrak{o} \) is the ring of integers of a non-Archimedean local field [cite: 22].

Shen and Van Peski extended this elegant classical story to **groups with pairings**. They analyzed abelian \( p \)-groups augmented with either alternating or Hermitian perfect bilinear pairings [cite: 22]. By defining a module over the classical Hall algebra with its basis indexed by these paired groups, they established that the structure constants of these modules relate explicitly to Hall-Littlewood polynomials evaluated at specific values of \( t \) (such as \( t = -1/q \) or \( t = 1/q \)) [cite: 21, 22].

### 6.2 The Non-Archimedean GUE Corners Process

This algebraic foundation has direct applications to random matrix theory. The authors evaluated the distribution of singular numbers for the principal corners of a \( p \)-adic Hermitian (or alternating) matrix drawn from an additive Haar distribution [cite: 21]. This models the non-Archimedean equivalent of the famous Gaussian Unitary Ensemble (GUE) and alternating GUE (aGUE) corners processes [cite: 21, 23].

The action of the general linear group \( GL_N \) on these matrices is given by \( A \mapsto B^* A B \), which is strictly governed by the spherical Hecke algebra [cite: 21]. Through this lens, Shen and Van Peski discovered the following:
*   **Alternating Matrices**: The non-Archimedean aGUE corners process corresponds identically to a **Hall-Littlewood process**. This finding provided a structural explanation for earlier, seemingly coincidental probabilistic formulas derived by Fulman and Kaplan regarding Jacobian groups of random graphs [cite: 21].
*   **Hermitian Matrices**: The non-Archimedean GUE corners process resolves to the marginal distribution of a *formal* Hall-Littlewood process [cite: 21]. Fascinatingly, this formal process involves transition variables that yield both positive and negative "probabilities" [cite: 21, 23]. 

This research successfully placed the structural results of Hironaka and Sato regarding Hecke algebras directly into the Macdonald process framework formulated by Borodin and Corwin, effectively linking p-adic integration spaces to symmetric function positivity [cite: 21].

---

## 7. Lattice Enumeration and Hall-Littlewood-Schubert Series

In April 2025, a separate advancement explicitly tied Hall-Littlewood structure to $p$-adic lattice geometry via the introduction of **Hall-Littlewood-Schubert (HLSn) series** [cite: 24].

### 7.1 Defining the HLSn Series

The HLSn series are multivariate rational generating series defined algebraically in terms of polynomials tightly related to Hall-Littlewood polynomials and semistandard Young tableaux [cite: 24]. 

For a tableau \( T \) of degree \( n \), an invariant known as the **leg polynomial**, \( \Phi_T(Y) \), is assigned to it. The HLSn series, denoted \( HLS_n(Y, X) \), is formulated as a finite sum spanning all *reduced* tableaux (tableaux where the columns are pairwise distinct):
\[ HLS_n(Y, X) = \sum_{T \in rSSYT_n} \Phi_T(Y) \prod_{C \in T} \frac{X_C}{1 - X_C} \]
This construction effectively records the label sets of the columns of the tableaux, serving as an expansion of the classic Feigin-Maklin formula for Hall-Littlewood polynomials [cite: 24].

### 7.2 Applications to Lattice Intersections

The HLSn series were designed to solve specific enumerative problems. Primarily, they enumerate the finite-index sublattices of a fixed \( p \)-adic lattice according to the elementary divisor types of their intersections with the members of a **complete flag of reference** within the ambient space [cite: 24]. 

Because the maps tracking these intersections naturally factor over the infinite set of tableaux \( SSYT_n \), the HLSn series acts as a generating function calculating the fibers of these geometric maps. Consequently, taking specific variable substitutions of the HLSn series explicitly recovers the **Hecke series** associated with groups of symplectic similitudes over local fields (originally studied by Macdonald), proving long-standing conjectures in algebraic number theory related to Bruhat orders and Stanley-Reisner rings [cite: 24].

---

## 8. Generalizations to Superspace and Non-Symmetric Polynomials

The pursuit of positivity has also naturally migrated into the theory of non-symmetric polynomials and superspace. Between 2025 and 2026, research investigated the space of **\( m \)-symmetric functions**, denoted \( R_m \) [cite: 25, 26]. These functions consist of polynomials that are fully symmetric in variables \( x_{m+1}, x_{m+2}, \dots \) but exhibit no special symmetry across the first \( m \) variables \( x_1, \dots, x_m \) [cite: 26].

By \( t \)-symmetrizing non-symmetric Macdonald polynomials, researchers constructed \( m \)-symmetric Macdonald polynomials, forming a basis for \( R_m \) [cite: 26]. Parallel to this, they defined \( m \)-symmetric Schur functions through dual bases and Hecke algebra generators [cite: 26].

A major positivity conjecture formulated during this period stipulates that the suitably normalized \( m \)-symmetric Macdonald polynomials expand positively in terms of \( m \)-symmetric Schur functions [cite: 26]. Crucially, as the parameter \( m \) becomes infinitely large, the \( m \)-symmetric Macdonald polynomials devolve into standard non-symmetric Macdonald polynomials. Therefore, this generalized positivity conjecture asserts that non-symmetric Macdonald polynomials expand with positive integer coefficients when expressed in the basis of **non-symmetric Hall-Littlewood polynomials** [cite: 25, 26]. This aligns with efforts to expand Macdonald superpolynomials natively into modified Schur superpolynomial bases [cite: 26].

---

## 9. Geometric and Cohomological Connections: $\Delta$-Springer Modules and Hilbert Schemes

As previously mentioned, Hall-Littlewood positivity usually guarantees the existence of a corresponding algebraic module. The classic relationship links the modified Hall-Littlewood polynomials \( \tilde{H}_\mu(x; q) \) to the Garsia-Procesi modules, which are the cohomology rings of Springer fibers [cite: 8]. 

### 9.1 $\Delta$-Springer Modules

In 2024, researchers expanded this topological analogy to what are termed **\(\Delta\)-Springer modules** [cite: 8]. Stemming from the Delta Conjecture in algebraic combinatorics, the \(\Delta\)-Springer varieties introduced by Levinson possess cohomology rings whose graded Frobenius characteristics can be decomposed using symmetric functions [cite: 8].

Research demonstrated that the symmetric function found at the evaluation \( t=0 \) inside the Delta Conjecture admits a simple Schur expansion described entirely by the Lascoux-Schützenberger cocharge statistic over "battery-powered" tableaux [cite: 8]. This allowed for the representation of the graded Frobenius characteristic of the \(\Delta\)-Springer modules in terms of modified Hall-Littlewood polynomials [cite: 8].

### 9.2 Hilbert Schemes of $n$ Points

The bigraded \( \mathcal{S}_n \)-representations are deeply related to the geometry of the Hilbert scheme of \( n \) points in the complex plane [cite: 6]. A 2025 paper demonstrated that in the quotient expansions within an infinite-dimensional Grassmann manifold, the palindromic numerators of the bigraded symmetric orbifold Hilbert series can be exactly identified as sums of products of Kostka-Foulkes polynomials [cite: 6]. This establishes a new geometric characterization of Hall-Littlewood polynomials as the parameterizing variables tracking the motion of points across Grassmannians [cite: 6].

---

## 10. Chromatic Quasisymmetric Functions and Graph Theory Interpretations

Positivity constraints also govern intersections between Hall-Littlewood polynomials and graph theory. In 2025, researchers focused on the **chromatic quasisymmetric function** \( X_G(x; q) \) of a graph \( G \), originally introduced by Shareshian and Wachs [cite: 3]. When \( q=1 \), this function reduces to Stanley's original chromatic symmetric function.

For a specific class of graphs—namely, the incomparability graphs of natural unit interval orders (often generated from Dyck paths)—the function \( X_G(x; q) \) is strictly symmetric [cite: 3]. Because the Hall-Littlewood polynomials interpolate between Schur functions (\( q=0 \)) and monomial functions (\( q=1 \)), expanding the chromatic quasisymmetric function into the Hall-Littlewood basis provides a highly natural \( q \)-analogue to standard Schur expansions [cite: 3].

Researchers successfully provided a precise combinatorial description of the Hall-Littlewood expansion of \( X_G(x; q) \), demonstrating that the expansion coefficients obey strict modular laws and multiplicativity properties (satisfying the Abreu-Nigro criterion) [cite: 3]. As a corollary utilizing Carlsson-Mellit relations, this resulted in a positive combinatorial description for the expansion of unicellular LLT polynomials in terms of modified transformed Hall-Littlewood polynomials, bridging geometric graph theory with symmetric function theory [cite: 3].

---

## 11. Data Synthesis: Domains of Hall-Littlewood Positivity (2024–2026)

To fully summarize the rapid branching of Hall-Littlewood polynomial research, the following table maps the distinct mathematical fields to the relevant polynomial variants and the newly developed combinatorial or representation-theoretic models resolving their positivity constraints.

| Mathematical Domain | HL Polynomial Variant | Mechanism of Positivity / Combinatorial Model | Key Contributions (2024–2026) |
| :--- | :--- | :--- | :--- |
| **Algebraic Combinatorics** | Modified HL Polynomials (\( \tilde{H}_\mu \)) | Schur positivity under the \( \nabla^k \) operator for two-column partitions. | Qu [cite: 4, 7] |
| **Lie Theory / Crystals** | Lusztig \( q \)-weight multiplicities | Energy functions on Kirillov-Reshetikhin column crystals for Types B & C. | Choi, Kim, Lee [cite: 10, 14, 15] |
| **Statistical Mechanics** | Modified HL / \( q \)-Whittaker | Cocharge and charge statistics applied directly to reading words of multiline queues. | Mandelshtam, Valencia-Porras [cite: 16, 17] |
| **Infinite-Dimensional Rep. Theory** | Hall-Littlewood basis (\( P_\lambda \)) | Extremal rays of \( t \)-HL-positive \( p_1 \)-harmonic functionals via \( p_2 \)-twisted mixing. | Cuenca, Olshanski [cite: 19, 20] |
| **Random Matrix Theory** | HL Polynomials / Hall algebra | \( p \)-adic GUE/aGUE corners mapping to Hecke modules of paired abelian groups. | Shen, Van Peski [cite: 21, 22] |
| **Algebraic Number Theory** | HLSn Series | Leg polynomials over reduced semistandard Young tableaux for lattice intersections. | Feigin-Maklin extensions [cite: 24] |
| **Graph Theory** | Transformed Modified HL | Chromatic quasisymmetric functions and unicellular LLT polynomials expansion. | Shareshian-Wachs analogues [cite: 3] |

---

## 12. Conclusion and Future Directions

The span of 2024 to 2026 has marked a renaissance in the study of Hall-Littlewood polynomial positivity and interpretations. The resolution of the BGHT conjectures for two-column partitions under the nabla operator [cite: 7] firmly cements the geometric realities of these polynomials in the representation theory of symmetric groups. Simultaneously, the successful construction of manifestly positive formulas for Lusztig \( q \)-weight multiplicities in non-A classical Lie types using Kirillov-Reshetikhin crystals [cite: 14, 15] represents the culmination of a decades-long pursuit in quantum group theory.

Furthermore, moving away from heavily algorithmic combinatorial generators (like the Ferrari-Martin algorithm) to direct statistic evaluations (like the charge on multiline queue reading words) allows for far greater computational flexibility in statistical mechanics [cite: 17]. The intersections with non-Archimedean probability theory—where Hall-Littlewood processes dictate the spectral behavior of \( p \)-adic random matrices—underscore that Hall-Littlewood polynomials are not just artifacts of symmetric function theory, but rather fundamental, invariant descriptors of symmetries found throughout all mathematical physics and algebra [cite: 21]. 

Looking forward, the immediate mathematical horizons involve fully resolving the nabla operator Schur positivity for arbitrary partitions (moving beyond the two-column restriction), finalizing the positivity of non-symmetric Hall-Littlewood polynomials using the \( m \)-symmetric superpolynomials [cite: 26], and charting the formal Hall-Littlewood processes possessing negative transition probabilities generated by Hermitian Hecke modules [cite: 21]. The pervasive requirement for "positivity" will undoubtedly continue to drive the discovery of new, foundational mathematical structures.

**Sources:**
1. [symmetricfunctions.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgGJHSTDy8X1DZxhtnv58Vlz8MPF28N_HxkxnVnMltZQiWQ6OGEcmLdmHnpAIP1SulsvWGMXlfETM-fkvvS5XMsVwFfIsLzLR0qexN98TZECSw8FM6qNK45PcWclHXrCGQ143MiQllh3fC)
2. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-9OvnrdbVhSlyFfWSrI6VATvlG7XCNedBZHiCdpzFeveztdN5spcUB8ozpEhg9wbcZb1jpw83YDsmG6t2IOgQOUp2DnTF_h5w2MGmDEN39ImVhgNKUbJMMRwdiPqmGW_OLDaEQZ1FkguVQnyz5DU-iN0nZsCS)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmeZjQPlu8nRkO6lnTEFN3LQSRCGCCZRXp71CCVq0QNXnKpiy2MuPSIhgh2T1-1zOriJceWjnqWNsztEQi-uldNiMMq6eSrSAPxAl-B8IApSjociQi)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2CZGZghkuCoWOWPVj6XQKyT0-0m4-kbbnsU1bnAFW-vo02tXYeCx8_TakVl24yIG2tVfB_DSejKQfQH2hxTopu_u1lRx4le-LjimXx0KQXKIM4igmNVaD)
5. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqO6u2XOO6DkSpfwgerEyaM3u1ZuLId5wqAVaT00YSstcU6sYmLQYTAu43Q80epMUhKWok2ReMhFn544E5b45ToBoghl7L9T1BOKL2dX89ZP_bG_1sBzxk7uAega4BgszH45igxngd-dCzA0_URxJP)
6. [cern.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFjA8lDGTZ78QVzPZwutjrTg_VFq_eCTgRHyz5wOreLI1dJ54UrGOjDMsBVUXx_gi8j1jAeje_NTpr9czUqpMIKHS3TaL_AA5y2wDqHIlvp4dlfPheNBsagAGB679JurTBQeOhu26lwNV0WeGLZ5BZdV3QxI0xasgw0T-AAibKsX_WSKczGSsQDI5ZIoPEYaq4ZZVOwVQ1NRk=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEV_EN8W3Ju_nzQzpIfOYdm7aiEkRU34xvnVxSl9VyCaRTjvonf_JN839KyJjdgA4tq9JEOkVM3w_Lsb3vUnIPISHlJ2OQwvcKKan00oYwJQ98QbUn9)
8. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKhl1i4fYUBHEnYLpjLPpJ9xxVgUWFPIa0kGeNaanjJgLONi8g1P5eEVwnSMfz4BDBKmd8lE-ZpkEEy3bs3sOri4lCW3cuzWrm7zck2nXL-lvIH_tQmGt0JdvVLJU9BTKJC-Jm8BjMt24Ci2l0on87)
9. [iisc.ac.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9s2MSORTAQiffO9Hjx-yBMgs_5bBqXTydFvDM3EoSvXhEo9-w8bUqtdKAVHZzZNjSfq2wZpLzIOZXv0onhSYPChBtli6mPiTdY0fBe2LJI8v9L0shL-dyvHXmsKZZnmiPG3U=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoGXdUsRT_6I5SBLjf6lMLB8zkB-RAKP-o5w_-OTGw8gjGO-BWnNGXoZTXbMQHaLOD-bktDOPNCaej3vMsVHmHNAzW7pD52zFXLpfm6pxjEH8kTEct)
11. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcljYT5Mx-_J3y-WiVrruaA-JVzs1YfweQEbHpGGSEBMQSfEqeL87PwMlPYM7I2up5Cnc5z4LPRtewrCOD3Pnev5LPX_S2jqKaAeAQdtacnRRR8hBiPXd-xacj1-HD4WHv2L6asAf5Fopd8-NToM2B)
12. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQET4FerF_7YdwKxTCz0zDd7uwVuf3QZpjHRDOmE7PZGuIdisl3EW6G_HMad96we-lCWdybq4y31gKy_JKfJ31y-FpYqBasa-oYPmVn5Mqh3pRU8krKbsPBQwc-0QHV5792y4amhkMxecqwUj_sOwUycGZ55T9XSrJ0V-S1q2YA6ljVmcQzeVKJmixCi)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESWDhUKszjM02hPhMrEA6XiTFNnJI6W-IFxsBoF-G0tEA6xy1ksyWMknYeNp05JRaHzp1k7brGJL9d4NRmvKgc5RPvUI8hknKeitqLRTagrzRsTW52zyMD)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFg49rCmHd3qRF-sO6bgtM6iQk-bqxCyazTUqh9BIO8t8PBl3l-oBKsNQHcA11I4UHz49GaqSiz1i_Nrqkq59lJnukAMVfklwOExPio4HDt-n1wFjk)
15. [hokudai.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFD6zzAYuzbt2KSE-fr1H-6zTxfgHEHPZiDvjyqPgozjMx4YK6geWbJo8-W_0llgFjSd00BglHFSNfkYR69Q_ifhTmPKwrNKsRG6dhBrTsG7QhT-krVBNGly5uiKbbOkW-Xaoe6bSQT8ZgdipOVTUyq1GGvEI4nHlqyBEim8Sg=)
16. [rub.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdWcz8PP3bDRAZBBTbJ8oeoNUpCs1Tu1ybNqYhdBwnNKfy4JUxHV3eEiCpavyPHTb8W-_Jfng96TAa66MpxGGJrKm0LtivF9i7Pl-clqDLpovgIj92Kcg5w3xiw2q4RlfO6328DwLu4Bz7admyA56mVx5r_J3Vc6lgQCY=)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMKQcmzqgsBJksR8NpSZy-bPyjkUVvaocWX9DfHPCbvmnWX6Ks_1W0nxrdU6a73h7v9l6w7Ptzigv96jfKfPUSICkZc4Xl-z_oY3lyHWeh9DXFg0uV)
18. [rub.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWrz0IQI_hcLweJu8kkSD79W57A6liz0n8XZarko7p910_Ja7_D_eXkhZzxf9wcSzfJvQYgMH1nby5IUA-pCJH9ZR45Og1bJKhwA1djNNlZCiaBKtd3p-8mw-HjRrmKGPhcxh87abtr-n5UH8rA1bNU7QIEzHgUYV8tQ==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2o0UluF4GiKL5JhvsaSKr_yf3rX1FZ9GOyjf3DX0GhXsjBfapNKvX5gFDPsFKPx2zIxNj6Oj9CreE1mmQJStpcUbK8fJZKt7DQKKsLXufBcdExUMk)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_yCQt1p6_6uj7yt23VNW9bDUr4LqiBeizb_tZs9R4zxDuFosiPfgqhBhbZAM-ayaT_m-QrXUIaxkHuzy_VT0VLQWEDOH7rvdHnBdOV1x3lAiTcGxPm5P5)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtng2KOQ0wpD5rZvnNFRf2qPX5xwVOEo-_pVjTX1Ok6OdpQV0LfAb7rfFClAciE-5O9IiwUuJU6toGbObsoJJxyfDTiSjNc4vSXO_KQy8sAOBkF2ts)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzNqxk7vGbB578AyBaaJBFMHf11ShLQmtmcSduNLOL-JDm_992ymbjQcHO78a4Rkm0x4vvxX_dFhOq9IYUAFciutlZB9bxzQ4UNs6eRzoNQJIaaIa3)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG64mt1cGjecUNgJBWaae0F_XtPcDp6FQFbMjsnbct0VMFTCljadpv4hlFPUIE0bfHHYKIdBO-88A1UAUgO0VprM16jIZp-lWD5Xzi-rl3qvbOotb0DZ1cE)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbpxVtpJmLLWJ4wcyKmdjBxnI9OWIjKQnqEdjp_40koG3o18CQjI1s9Yu3jRHJ5uJ876aqNsdTWsv-Qe-m9tB7QDqlj5trdAjOy1aUDe4b89BcIigC)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYtNwQktIUdib-4nN3WhySSGAYUC9N4QIM2QxubAnMiXCfRasruqMsGEs4QcVe5vqmGKAJpl8BR7UCCPwwDyqLZtkw2_Z8HtAk1gvTmDgzrvi4eN_c)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZ2oMqLudEgf0klabhv5slM0jrSgC_wRn539hpHL9GMtDcrshp8pdpZKpf5_I6fgZcLnQolSUbPgMFN2ylBTtO4PxAlGDjbLzGf5_fLIy27j9jsF2hUHaGiZAjl5CHCYvq1Fl2RRZGdzMeITWX2TRRfo0ovkqdcPTQQJvy_Xc4EmYO7_DqKWwmQ8gMQXWmNsKOAVOX7-RRUZcW522TFxRa45ZqyyAFOpbAASAG2sCfihlwSpNw5L0DYtcU0g==)

