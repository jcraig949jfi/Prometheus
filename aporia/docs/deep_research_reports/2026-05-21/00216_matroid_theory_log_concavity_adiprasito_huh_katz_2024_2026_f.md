# Matroid theory + log-concavity (Adiprasito-Huh-Katz) 2024-2026 frontier

**Pythia queue id:** 216
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd3a3dQYXFmMkNMZWtfdU1QMzVHNmtBOBIXd2t3UGFxZjJDTGVrX3VNUDM1RzZrQTg
**Elapsed:** 325s
**Completed at:** 2026-05-21T18:25:12.076897+00:00

---

# Matroid Theory and Log-Concavity: The 2024-2026 Frontier Building on the Adiprasito-Huh-Katz Framework

**Key Points:**
*   **A Paradigm Shift:** The intersection of matroid theory and algebraic geometry has sparked a mathematical revolution. The foundational work of Adiprasito, Huh, and Katz resolved long-standing conjectures about log-concavity by applying profound "Hodge-theoretic" principles to purely combinatorial objects.
*   **The Power of Lorentzian Polynomials:** The recent frontier (2024-2026) is heavily driven by the theory of *Lorentzian polynomials*, a framework that distills deep geometric theorems into the language of linear algebra and polynomial analysis, allowing researchers to tackle previously insurmountable inequalities.
*   **Dowling's Conjecture Solved:** In early 2026, a major milestone was reached when researchers completely resolved Dowling's 1980 polynomial conjecture, lifting Mason's log-concavity bounds for matroid independent sets into a continuous polynomial regime.
*   **Tree Metrics and Economics:** Recent 2026 breakthroughs have connected matroid log-concavity to the "gross substitutes" property in discrete convex analysis and economics, utilizing sophisticated metrics derived from ultrametric trees.
*   **Topology and Hyperfields:** The abstract space of Lorentzian polynomials has recently (2025) been geometrically mapped to "thin Schubert cells" over triangular hyperfields, revealing complex topological structures representing manifolds with boundaries tied to tropical geometry.
*   **Conjectures Broken and Proven:** While Kazhdan-Lusztig polynomials of uniform and fan matroids have been proven to exhibit ultra-log-concavity, the overarching conjecture that all inverse Kazhdan-Lusztig polynomials are real-rooted was recently disproved (2025) by the discovery of a rank-19 counterexample.

**A Layman's Summary of the Frontier**
Matroid theory is a branch of discrete mathematics that abstracts the concept of "independence"—much like how vectors in a physical space can be independent of one another, or how edges in a network form loops or remain free of them. For decades, mathematicians noticed curious patterns when counting these independent structures. If you graphed the number of independent sets of size 1, size 2, size 3, and so on, the curve always seemed to swell in the middle and taper off at the ends in a very smooth, predictable way known as "log-concavity." However, proving that this shape occurs *every single time* for every possible matroid was exceptionally difficult. 

In a monumental breakthrough published in 2018, Karim Adiprasito, June Huh, and Eric Katz borrowed heavy machinery from algebraic geometry—a field that studies shapes defined by continuous polynomial equations—and translated it to the discrete world of matroids. Their success opened the floodgates. Over the past three years (2024-2026), the frontier has rapidly expanded. Researchers realized they did not always need the heavy geometric machinery; instead, they could use a new class of mathematical objects called "Lorentzian polynomials." These polynomials act as a universal bridge, making it vastly easier to prove complex counting rules. Today, researchers are solving decades-old problems, linking matroid counting to economic theories of substituted goods, and discovering bizarre geometric spaces (known as hyperfields) that govern the rules of these polynomials. 

**Hedging and Complexity**
It is important to note that while the theory of Lorentzian polynomials provides an incredibly robust framework, the absolute boundaries of log-concavity are still being actively charted. Research suggests that while many matroid invariants strictly adhere to ultra-log-concavity and real-rootedness, we are beginning to find highly complex, high-dimensional exceptions—such as the recent rank-19 counterexample to the real-rootedness of inverse Kazhdan-Lusztig polynomials. The evidence leans toward a landscape where beautiful, unified rules govern the vast majority of combinatorial geometries, but the extreme edge cases still harbor chaotic and unresolved mysteries. The 2024-2026 frontier represents an ongoing effort to cleanly map the boundary between predictable log-concave behavior and geometric chaos.

## 1. Introduction to the Adiprasito-Huh-Katz Framework

The recent explosion of results in combinatorial Hodge theory and log-concavity cannot be understood without first contextualizing the monumental breakthrough achieved by Karim Adiprasito, June Huh, and Eric Katz [cite: 1, 2]. Matroid theory, originally introduced by Hassler Whitney in 1935 to capture the fundamental properties of dependence common to graph theory and linear algebra, deals with a ground set $E$ and a collection of subsets $\mathcal{I}$ called independent sets [cite: 3, 4]. 

For decades, combinatorialists observed persistent unimodality and log-concavity in sequences derived from matroids. A sequence of non-negative real numbers $a_0, a_1, \dots, a_n$ is said to be log-concave if for all $0 < k < n$, the inequality $a_k^2 \ge a_{k-1}a_{k+1}$ holds. Log-concavity naturally implies unimodality (the sequence rises to a peak and then falls) if the sequence has no internal zeros [cite: 5, 6]. 

### 1.1 The Heron-Rota-Welsh Conjecture
One of the most famous open problems in this domain was the Heron-Rota-Welsh conjecture, which postulated the log-concavity of the absolute values of the coefficients of the characteristic polynomial of a matroid [cite: 7, 8]. The characteristic polynomial of a matroid generalizes the chromatic polynomial of a graph (which counts the number of valid graph colorings). June Huh first proved this conjecture for matroids realizable over fields of characteristic zero using powerful tools from singularity theory and algebraic geometry [cite: 1, 9]. Subsequently, Huh and Katz extended this to all realizable matroids. 

However, the vast majority of matroids are not realizable over any field. To prove the conjecture for *all* matroids, Adiprasito, Huh, and Katz developed a purely combinatorial analogue of Hodge theory [cite: 1, 9]. They constructed a "Chow ring" for any arbitrary matroid, mirroring the intersection theory of toric varieties, and proved that this combinatorial Chow ring satisfies the "Kähler package":
1.  **Poincaré Duality:** An isomorphism between complementary degrees of the Chow ring.
2.  **The Hard Lefschetz Theorem:** Multiplication by a strictly convex piecewise linear function (a generic hyperplane class) induces an isomorphism between appropriate degrees.
3.  **The Hodge-Riemann Relations:** The intersection pairing possesses a specific signature (a localized alternating definiteness) on the primitive cohomology [cite: 7, 10].

The verification of the Hodge-Riemann relations for the matroid Chow ring directly implied the log-concavity of the characteristic polynomial, thus resolving the Heron-Rota-Welsh conjecture [cite: 8, 9].

### 1.2 Mason's Conjectures
Parallel to the characteristic polynomial, the enumeration of independent sets of matroids was governed by Mason's conjectures, formulated in 1972 [cite: 3]. Let $I_k$ denote the number of independent sets of size $k$ in a matroid of rank $n$. Mason proposed three increasingly strong inequalities:
*   **(M1) Log-Concavity:** $I_k^2 \ge I_{k-1}I_{k+1}$.
*   **(M2) Strong Log-Concavity:** $I_k^2 \ge \left(1 + \frac{1}{k}\right) I_{k-1}I_{k+1}$.
*   **(M3) Ultra-Log-Concavity:** $I_k^2 \ge \left(1 + \frac{1}{k}\right)\left(1 + \frac{1}{n-k}\right) I_{k-1}I_{k+1}$.

The sequence $I_k$ satisfying (M3) means that the sequence $I_k / \binom{n}{k}$ is log-concave, a property known as ultra-log-concavity [cite: 3, 11]. Using the foundation laid by Adiprasito, Huh, and Katz, the strongest version of Mason's conjecture (M3) was proved independently by Anari, Liu, Oveis Gharan, and Vinzant using "completely log-concave polynomials," and by Brändén and Huh using the intimately related theory of "Lorentzian polynomials" [cite: 3, 12].

## 2. The Shift to Lorentzian Polynomials (2020-2024)

While the Adiprasito-Huh-Katz theorem was a triumph, the combinatorial Hodge theory machinery was formidably complex. As the field matured into the 2020s, a vital synthesis occurred. The theory of Lorentzian polynomials, formalized by Petter Brändén and June Huh [cite: 12, 13], offered a way to capture the negative dependence and log-concavity inherent in matroids without invoking the full weight of Chow rings and intersection cohomology [cite: 14].

### 2.1 Defining the Lorentzian Property
A homogeneous polynomial $f \in \mathbb{R}[x_1, \dots, x_n]$ of degree $d$ with non-negative coefficients is called *Lorentzian* if it satisfies two main conditions:
1.  **M-Convex Support:** The set of exponents (the support of the polynomial) must form an M-convex set. In the multi-affine case, this is exactly equivalent to the basis exchange axiom of a matroid [cite: 12, 15].
2.  **Hessian Signature (The Local Hodge-Riemann Relation):** For any sequence of directional derivatives $\mathbf{D}_{\mathbf{v}_1} \dots \mathbf{D}_{\mathbf{v}_{d-2}}$ taken in directions from the positive orthant $\mathbb{R}_{>0}^n$, the resulting quadratic form must have a Hessian matrix with exactly one positive eigenvalue (a Lorentzian signature) [cite: 12, 13].

This signature condition is a direct, localized reflection of the Hodge-Riemann relations of degree one [cite: 13, 16]. The Lorentzian property turns out to be exceptionally stable: it is preserved under polarization, directional derivatives, and various linear operators [cite: 15]. By showing that the basis generating polynomial of a matroid is Lorentzian, the full suite of Mason's conjectures falls out as a natural analytic consequence of the polynomial's concavity in the positive orthant [cite: 5, 15].

## 3. The 2026 Breakthrough: Complete Resolution of Dowling's Polynomial Conjecture

As the theory of Lorentzian polynomials matured, researchers began attacking higher-order generalizations of Mason's conjectures. One of the most prominent open problems was Dowling's Polynomial Conjecture, formulated in 1980 [cite: 4, 17]. While Mason's conjecture dealt with the purely numerical sequence of the *number* of independent sets, Dowling envisioned a continuous, polynomial lift of this sequence [cite: 4, 12].

### 3.1 Formulation of Dowling's Conjecture
Given a matroid $M = (E, \mathcal{I})$ with $|E|=n$, Dowling defined the independent set polynomials for $0 \le k \le r(M)$ as:
\[ f_k(M) = \sum_{I \in \mathcal{I}, |I|=k} \left( \prod_{x_i \in I} x_i \right) \]
Here, $f_k(M)$ is a homogeneous polynomial of degree $k$ in the variables $x_1, \dots, x_n$. 
Dowling conjectured that the polynomial refinement of Mason's weakest conjecture (M1) holds coefficient-wise for any matroid [cite: 17, 18]:
\[ f_k^2(M) \succeq f_{k-1}(M) f_{k+1}(M) \]
where the notation $f \succeq g$ means that the difference $f - g$ is a polynomial with non-negative coefficients. This is vastly stronger than the numerical Mason's conjecture, as it asserts log-concavity across the entire multivariate algebraic structure of the matroid [cite: 4, 12]. In 1985, Zhao proposed a stronger version corresponding to Mason's (M2):
\[ f_k^2(M) \succeq \left(1 + \frac{1}{k}\right) f_{k-1}(M) f_{k+1}(M) \]

### 3.2 The Resolution by Cao, Chen, Li, and Wu
In January 2026, Shiqi Cao, Keyi Chen, Yitian Li, and Yuxin Wu published a complete resolution of Dowling's polynomial conjecture [cite: 12, 19]. Their proof represents a masterclass in the application of Lorentzian polynomials to discrete geometry [cite: 12].

Cao et al. bypassed the original, highly complex combinatorial approaches (which Dowling used to prove the conjecture only for $k \le 7$) by heavily utilizing the directional derivative operators inherent in the definition of completely log-concave and Lorentzian polynomials [cite: 12, 18]. By treating the independent set polynomials as specific evaluations of the homogeneous generating polynomial of the matroid, they demonstrated that the Hessian matrices associated with these multivariate polynomials strictly obey the interlacing and signature conditions required [cite: 12, 18].

Furthermore, Cao, Chen, Li, and Wu proved an even stronger, highly generalized result that extends the polynomial log-concavity across multiple steps of the sequence [cite: 17]:
For any matroid $M$ of rank $r(M)$, and for any integers $p \ge 2$ and $p-1 < l < r(M)$, the following holds coefficient-wise:
\[ f_l^p(M) \succeq \left( \prod_{j=1}^{p-1} \left(1 + \frac{j}{(p-1)l}\right) \right) f_{l+1}^{p-1}(M) f_{l-p+1}(M) \]
This theorem not only perfectly encapsulates Dowling's and Zhao's conjectures but fully generalizes the polynomial ultra-log-concavity to arbitrary multi-step intervals [cite: 17]. This 2026 result firmly establishes that the Lorentzian framework is not merely an alternative proof technique for numerical log-concavity, but the definitive algebraic setting for matroidal generating functions [cite: 4, 19].

## 4. Tree Metrics, Gross Substitutes, and Log-Concavity (2026)

Simultaneous to the resolution of Dowling's conjecture, another major 2026 breakthrough connected matroid log-concavity to fundamental principles in mathematical economics and discrete convex analysis. In January 2026, a team comprising Federico Ardila-Mantilla, Sergio Cristancho, Graham Denham, Christopher Eur, June Huh, and Botong Wang released a seminal paper titled "Tree metrics and log-concavity for matroids" [cite: 3, 20].

### 4.1 M-Natural Concavity and the Gross Substitutes Property
In economics, a valuation function defined on sets of items satisfies the "gross substitutes" property if an increase in the price of some items does not decrease the demand for the remaining items. In the 1990s and 2000s, it was proven that the gross substitutes property is mathematically equivalent to the concept of **$M^\natural$-concave functions** (M-natural concave functions), a central object in Murota's discrete convex analysis [cite: 3]. 

An $M^\natural$-concave function $\nu: 2^E \to \mathbb{R} \cup \{-\infty\}$ satisfies a specific exchange property that generalizes the independent sets, rank functions, and valuated matroids [cite: 3]. The open question, posed by Eur and Huh in 2020, was whether one could characterize $M^\natural$-concave set functions precisely in terms of Lorentzian polynomials [cite: 3].

### 4.2 Ultrametric Trees and the Graham-Pollak Refinement
Ardila-Mantilla et al. solved this by looking at the geometry of tree metrics [cite: 20, 21]. The classical Graham-Pollak theorem (1971) states that the distance matrix of any tree with $n$ leaves has exactly one positive eigenvalue, regardless of the tree's structure. 

The authors refined this theorem for **ultrametric trees**—rooted trees where all leaves are equidistant from the root (representing a strictly hierarchical clustering) [cite: 3]. They provided a strict rank 1 upper bound for the distance matrix of an ultrametric tree. By applying this linear algebraic bound, they mapped the metric properties of the tree directly to the Hessian signature condition of Lorentzian polynomials [cite: 3, 21].

### 4.3 The Equivalence Theorem and its Consequences
The crowning achievement of the 2026 paper is the following equivalence theorem:
*A set function $\nu$ satisfies the gross substitutes property (is $M^\natural$-concave) if and only if its homogeneous generating polynomial $Z_{q,\nu}$ is a Lorentzian polynomial for all positive $q \le 1$ [cite: 3, 21].*

This profound characterization had immediate, sweeping consequences:
1.  **Valuated Matroids:** It resolved an open question by Giansiracusa, Rincón, Schleis, and Ulirsch (2024), proving that Mason's ultra-log-concavity conjecture (M3) holds for the broad class of $M^\natural$-concave functions constructed from valuated matroids [cite: 3, 21].
2.  **Dowling and Zhao Conjectures for Ordinary Matroids:** Utilizing this equivalence, they provided an independent resolution to the polynomial inequalities conjectured by Dowling and Zhao, proving that $I_{q,\nu; k}(x)^2 \succeq (1+1/k) I_{q,\nu; k-1}(x) I_{q,\nu; k+1}(x)$ holds coefficient-wise for these generalized functions [cite: 3].

This research successfully bridged economic theory, phylogenetic/clustering tree metrics, and the Lorentzian/Hodge-theoretic framework of matroids [cite: 21, 22].

## 5. Topological Aspects: Triangular Hyperfields and Lorentzian Spaces (2025)

As the algebraic and combinatorial properties of Lorentzian polynomials were mapped out, researchers turned to understanding the geometric space that these polynomials inhabit. In August 2025, Matthew Baker, June Huh, Mario Kummer, and Oliver Lorscheid established a groundbreaking link between the topology of Lorentzian polynomials and tropical geometry via "hyperfields" [cite: 23, 24].

### 5.1 Matroids over Hyperfields
A hyperfield is a generalization of a field where addition is allowed to be multi-valued. Introduced to matroid theory by Baker and Bowler, matroids over hyperfields provide a unified framework encompassing ordinary matroids (over the Krasner hyperfield), oriented matroids (over the sign hyperfield), and valuated matroids (over the tropical hyperfield) [cite: 25, 26].

Viro introduced the **triangular hyperfield**, denoted $\mathbb{T}_q$ (for $q > 0$), to study Maslov dequantization and tropical limits [cite: 23, 27]. In $\mathbb{T}_1$, the relation $a+b+c=0$ holds if and only if $a, b,$ and $c$ can form the side lengths of a triangle. As $q \to 0$, the triangular hyperfield degenerates perfectly into the tropical hyperfield [cite: 23, 28]. 

### 5.2 The Topology of $\mathbb{P}L_J$
Baker, Huh, Kummer, and Lorscheid studied the space $\mathbb{P}L_J$, which is the space of Lorentzian polynomials supported on a specific polymatroid basis set $J$, modulo positive scaling $\mathbb{R}_{>0}$ [cite: 23]. 

They proved several spectacular topological results in their 2025 paper:
1.  **Hyperfield Identification:** The space of Lorentzian polynomials $\mathbb{P}L_J$ is homeomorphic to the "thin Schubert cell" $Gr_J(\mathbb{T}_q)$ of $J$ over the triangular hyperfield $\mathbb{T}_q$ [cite: 23, 27]. This means the continuous, analytic definition of Lorentzian polynomials perfectly matches the discrete, algebraic geometry of Grassmannians over generalized fields.
2.  **Manifold with Boundary:** They proved that $\mathbb{P}L_J$ is a topological manifold with boundary, and its dimension is exactly equal to the Tutte rank of $J$ [cite: 23, 27].
3.  **The Dressian:** More precisely, $\mathbb{P}L_J$ is homeomorphic to a closed Euclidean ball with the "Dressian" of $J$ (a well-known tropical parameter space) removed from its boundary [cite: 23, 27].
4.  **Hausdorff Compactification:** They showed that $\mathbb{P}L_J$ always admits a compactification homeomorphic to a closed Euclidean ball, and that the Chow quotient of a complex Grassmannian maps naturally to this compactification [cite: 23, 27].

Importantly, this work answered a long-standing question of Brändén in the negative. Brändén asked if the closure of the space of Lorentzian polynomials within the space of all polynomials is always a Euclidean ball; Baker et al. showed that due to the complex tropical boundary (the Dressian), it generally is not [cite: 23, 27]. This research provides the definitive geometric framework for the asymptotic structure of log-concave polynomials [cite: 29].

## 6. Singular Hodge Theory and Intersection Cohomology

While Lorentzian polynomials dominated the study of basis generating functions, the original combinatorial Hodge theory of Adiprasito-Huh-Katz was also undergoing a profound evolution. The Chow ring of a matroid relies on the matroid being "smooth" in a combinatorial sense. However, to resolve certain deeper topological conjectures, researchers had to develop a **Singular Hodge Theory for Combinatorial Geometries** [cite: 10, 30].

### 6.1 The Top-Heavy Conjecture and Intersection Cohomology
In 1974, Dowling and Wilson proposed the Top-Heavy Conjecture: for any matroid, the number of flats of rank $k$ is less than or equal to the number of flats of rank $d-k$ (where $k \le d/2$, and $d$ is the rank of the matroid) [cite: 10, 31]. This is a vast generalization of the de Bruijn-Erdős theorem, which states that a non-collinear set of points in a projective plane defines at least as many lines as there are points [cite: 10].

Between 2020 and 2023, Tom Braden, June Huh, Jacob Matherne, Nicholas Proudfoot, and Botong Wang constructed the **Intersection Cohomology module $IH(M)$** for arbitrary matroids [cite: 10, 31]. Intersection cohomology is a tool in algebraic geometry used to restore Poincaré duality for singular varieties. Braden et al. defined $IH(M)$ purely combinatorially and proved that it satisfies the full Kähler package:
1.  **Poincaré Duality**
2.  **Hard Lefschetz Theorem**
3.  **Hodge-Riemann Relations** [cite: 10, 32]

The Hard Lefschetz theorem for $IH(M)$ immediately proved the Dowling-Wilson Top-Heavy conjecture, as the injective multiplication maps between degree $k$ and $d-k$ guarantee the required inequalities among the dimensions (which count the flats) [cite: 10, 31].

## 7. Kazhdan-Lusztig Polynomials, Z-Polynomials, and the Ultra-Log-Concavity Frontiers (2024-2026)

A massive subfield of the 2024-2026 frontier revolves around a specific invariant derived from the intersection cohomology of matroids: the Kazhdan-Lusztig polynomial.

### 7.1 Definitions and Conjectures
Elias, Proudfoot, and Wakefield (2016) introduced the Kazhdan-Lusztig (KL) polynomial $P_M(x)$ of a matroid, which mimics the classical KL polynomials of Coxeter groups [cite: 31, 33]. The non-negativity of the coefficients of $P_M(x)$ was a major open problem, which was ultimately solved by the construction of the intersection cohomology module $IH(M)$, as the coefficients of $P_M(x)$ represent the Betti numbers of the stalks of $IH(M)$ [cite: 11, 33].

Building on this, Proudfoot, Xu, and Young introduced the **Z-polynomial** $Z_M(x)$ [cite: 34, 35]. Ferroni, Nasr, and Vecchi later introduced the **$\gamma$-polynomial** [cite: 36].

A massive web of conjectures was spun around these polynomials. It was conjectured that for every matroid $M$:
1.  The Z-polynomial $Z_M(x)$ is real-rooted [cite: 36, 37].
2.  The Kazhdan-Lusztig polynomial $P_M(x)$ is log-concave [cite: 34, 37].
3.  The inverse Kazhdan-Lusztig polynomial $Q_M(x)$ (introduced by Gao and Xie) is log-concave and real-rooted under certain normalizations [cite: 34, 38].

Because real-rootedness of polynomials with positive coefficients strictly implies Newton's inequalities, real-rootedness implies ultra-log-concavity, which in turn implies standard log-concavity and unimodality [cite: 35, 37]. Thus, proving ultra-log-concavity has been the gold standard for the years 2024-2026.

### 7.2 Successes: Uniform, Fan, and Equivariant Matroids
Significant progress has been made on proving these properties for specific, highly symmetric classes of matroids:
*   **Uniform Matroids:** In May 2024, Siyi Wu, Matthew H. Y. Xie, and Philip B. Zhang published a landmark paper proving that both the Z-polynomials and the $\gamma$-polynomials of uniform matroids are strictly ultra-log-concave [cite: 36]. This heavily supported the real-rootedness conjecture and allowed them to provide a new proof of the $\gamma$-positivity of sparse paving matroids [cite: 36].
*   **Fan Matroids:** In 2026, building on work for thagomizer and paving matroids, researchers calculated the explicit generating functions for the inverse KL polynomials of fan matroids (a class of graphic matroids associated with fan graphs) and proved that their coefficients form a log-concave sequence with no internal zeros [cite: 34].
*   **Equivariant Invariants:** In 2026, Gao, Li, Xie, Yang, and Zhang extended the concept to group actions. They introduced the concept of "induced log-concavity" for a sequence of representations of a finite group. They successfully proved the induced log-concavity of the equivariant Kazhdan-Lusztig polynomials of $q$-niform matroids (equipped with general linear group actions) and uniform matroids (symmetric group actions) [cite: 39]. This heavily supported Elias, Proudfoot, and Wakefield's overarching log-concavity conjectures [cite: 39].

### 7.3 The Counterexample: Breaking the Real-Rootedness Conjecture
Despite the overwhelming success in proving log-concavity, the absolute frontier of 2025 yielded a shocking counterexample to the real-rootedness conjectures. 

Xie and Zhang had previously conjectured that the normalized inverse Kazhdan-Lusztig polynomial $\mathcal{B}(Q_M)(x)$ is real-rooted for *every* matroid, a property they verified for all paving matroids [cite: 33, 38]. 

In October 2025, Luis Ferroni, Jacob Matherne, N. Nepal, and Tom Braden investigated the behavior of inverse KL polynomials under matroid deletion [cite: 33, 38]. They successfully derived complex deletion formulas for both the inverse KL polynomial $Q_M(x)$ and the inverse Z-polynomial $Y_M(x)$, which provided closed formulas for matroids of corank 2 and glued cycles [cite: 38]. 

However, utilizing these powerful new deletion formulas and computational searches, Ferroni et al. proved a negative result: **There exists a matroid of rank 19 on 21 elements whose normalized inverse Kazhdan-Lusztig polynomial is NOT real-rooted** [cite: 33, 38]. 

This 2025 discovery effectively kills the universal real-rootedness conjecture for inverse KL polynomials. It establishes a firm boundary: while ultra-log-concavity and log-concavity are extraordinarily pervasive and likely universal for KL invariants, the strict algebraic property of real-rootedness breaks down in high-dimensional, highly asymmetric matroids [cite: 38]. This perfectly illustrates the current tension at the frontier: separating the universal Hodge-theoretic truths from the algebraically fragile conjectures.

## 8. Bimatroids and Morphisms (2024)

Beyond standard matroids, researchers are pushing log-concavity into broader generalizations. In February 2024, Felix Röhrle and Martin Ulirsch published a study on the logarithmic concavity of sequences associated to **bimatroids** [cite: 40, 41]. 

A bimatroid is a generalization of the collection of regular minors of a matrix. Kung originally observed that bimatroids can be used to characterize morphisms between matroids [cite: 40]. Röhrle and Ulirsch utilized the theory of Lorentzian polynomials to prove a weak version of logarithmic concavity for the number of bases of a morphism of matroids [cite: 40].

More profoundly, they demonstrated that for realizable bimatroids, the "regular minor polynomial" acts as a volume polynomial (a specific subset of Lorentzian polynomials that measure the volume of Minkowski sums of convex bodies). Applied to morphisms of matroids, they proved that the weak basis generating polynomial of a morphism is a volume polynomial [cite: 21, 40]. This confirmed a conjecture by Eur and Huh for morphisms of nullity $\le 1$ and provided a deep, algebro-geometric explanation for Mason's log-concavity conjecture strictly within the realizable case [cite: 40].

## 9. The Current Ecosystem and Future Directions

The 2024-2026 period has seen an unparalleled synthesis of combinatorial Hodge theory, Lorentzian polynomials, discrete convex analysis, and tropical geometry. The momentum is captured perfectly by the institutional focus on the subject. For instance, the renowned Oberwolfach Research Institute for Mathematics hosted an *Arbeitsgemeinschaft* (working group) in 2025 dedicated entirely to "Combinatorial Hodge Theory" [cite: 29].

Organized around matroids, Hodge theory, toric methods, and Lorentzian polynomials, this 2025 workshop consolidated the new foundational theories [cite: 29]. Researchers focused heavily on the Baker-Bowler framework for matroids with coefficients, Chow rings, wonderful compactifications, and matroids over triangular hyperfields [cite: 29]. 

### 9.1 Generalizing Beyond the Positive Orthant
A critical emerging frontier (late 2024-2025) is the generalization of Lorentzian polynomials beyond the positive orthant. Traditional Lorentzian polynomials are defined with respect to the standard positive orthant $\mathbb{R}_{>0}^n$. Recent work by Blekherman, Dey, and others has introduced $\mathcal{K}$-Lorentzian polynomials, which are defined over arbitrary proper convex cones $\mathcal{K}$ [cite: 13]. 

These $\mathcal{K}$-Lorentzian polynomials require that directional derivatives in the interior of the cone $\mathcal{K}$ maintain a Lorentzian signature [cite: 13]. This extension is actively being used to connect matroid log-concavity to stability analysis in dynamical systems, continuous capacity bounds, and broader optimization frameworks where the constraints are defined by complex non-polyhedral cones [cite: 13].

### 9.2 Open Questions
Despite the massive resolutions of Dowling's conjecture and the tree metric equivalence for gross substitutes, several deep questions remain open as of 2026:
1.  **Topological Classification:** While Baker et al. (2025) mapped $\mathbb{P}L_J$ for polymatroids, a full topological classification of Lorentzian polynomial spaces for all geometric compactifications remains elusive, especially regarding the exact combinatorial structure of the Dressian boundaries [cite: 13, 23].
2.  **KL Log-Concavity:** While the *inverse* KL real-rootedness conjecture was broken by Ferroni et al. (2025) [cite: 38], the foundational conjecture by Elias, Proudfoot, and Wakefield that the standard Kazhdan-Lusztig polynomial of an arbitrary matroid is unconditionally log-concave remains fully open, having only been verified for specific classes like uniform and sparse paving matroids [cite: 35, 37].
3.  **Algorithmic Complexity:** With the equivalence between Lorentzian polynomials and the gross substitutes property firmly established via tree metrics [cite: 20, 21], finding fully polynomial-time approximation schemes (FPTAS) or exact algebraic algorithms for computing permanents and capacities in these broader Lorentzian cones is a highly active area of theoretical computer science [cite: 13, 42].

## 10. Conclusion

The frontier of matroid theory between 2024 and 2026 has been defined by the maturation and explosive application of the Lorentzian polynomial framework, a direct descendant of the combinatorial Hodge theory pioneered by Adiprasito, Huh, and Katz. By stripping away the necessity for complex algebraic varieties and relying on the continuous, analytic properties of Hessian signatures and M-convexity, mathematicians have systematically annihilated decades-old conjectures.

From the total resolution of Dowling's polynomial conjecture by Cao, Chen, Li, and Wu in 2026 [cite: 12, 19], to the elegant synthesis of economic gross substitutes and ultrametric tree distances by Ardila-Mantilla, Eur, Huh, and colleagues [cite: 20, 21], the field has achieved unprecedented unification. Furthermore, the deep geometric dive into the topology of these polynomials via triangular hyperfields by Baker and Lorscheid [cite: 24, 27] ensures that the visual and spatial understanding of these combinatorial bounds is as rich as their algebraic proofs. 

Simultaneously, the rigorous testing of intersection cohomology invariants—such as Kazhdan-Lusztig and Z-polynomials—has proven that while log-concavity is an extraordinarily powerful and pervasive force in nature, the strictest algebraic properties like universal real-rootedness still shatter against the complexity of high-dimensional matroids [cite: 36, 38]. As the mathematical community moves forward from the 2025 Oberwolfach symposiums into the late 2020s, the blueprint left by Adiprasito, Huh, and Katz continues to be the most fertile ground in discrete mathematics, seamlessly weaving together geometry, combinatorics, and continuous analysis.

**Sources:**
1. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmF1Z_r-eS_vN_wtDxFH59e_QekqfnVSAtqR02ceLOhN4Jazwqdkl2dbrhz1qy3tMrIkIQfEVXnYsldi3Pti5rjnartfZp0bibibu5jmPnq-OI9j07eCyShMapC6FSgMEj2OH2a6u0GEAdv8_TCB9P2UHQqX_zsZhKNfa3iMj8I3uA-bTuSL3rpqWkfBsYYA859mQJ8IoclTYLIL57Drlho_aFXZLjb8DXCxFgXum0P9IUVgZUvbQei-9dXOetEaEf41YEwaXVpLHEIBVT5pI1)
2. [osu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpHbW8R3Ldp-5Wt_dkI9zcGmaahSNuHBnTKPnEFI3JyDUbWwvkCeZClRPxIUrT5nesONZ1SaYYBYczsamQPrXwFj5f7whz-PkZFdK1VUmB3desBlg4iNKj4cY=)
3. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF01elt-FrEWFD7Awoi_Db0WN3EyZfUhMQ4OtcdpEgsOv0jGzegoq8fqJqSQ4nGyNyrQLgP5jiQy63gjC_x1n7YwED-ByeOgtD2NIAnAG9nR6RiWoh-NOSMADPFX9YXkAsFsbw=)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAC7MtczGFvA6tLuxKYnhxrs4x26iMNjHdzZwAUrP0zoY4gf8qgjkhEC52GtFejT7JsQ9mfLIVQcu7Era4IjR3FNLP2w09MmPoK_uHAJdhD8kCGTtnuQ==)
5. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-CnwKeyH-ZJ9pQEZqfphIe-fi5DuYNTwwUQBViYIPkg3HdHav0Cbr63O_8iTsKkzXrwvaWC4-XbRMTlzcn9rvibS_XgFi2hvi3668lRpjwTGIyWbc371CKBGxjJMCr4_ICRbLPt8=)
6. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKSX4hQO_DS976Km7c6RQB7CK06LfHGQ-GMgEJa4pfU8UzO9xHJ32zjhNrJscXKUnUtwaY3r7zgQVlR1jskxQN_JfuaIoPkPHYGrY62e3-CDqzB3derS4Q4dNHTGUyKJ9i74Gwk8ZSEXWZ1jgVIDCLK1rqNwk5bhHqFNsOs54z0Ka_St_yGGb_SA6YhrtCb9cSNYe22_cHC-mecPxgNnP5SzprxMogN-JLz6Opi_ZI)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUSBx3CSLzSN06OlnH2npAjAQle5d9SqJxxobPyuYoBBkPNjk6YTnQSmsnXoEGPNmsN7PfM_WLnWzQLU11NDGbb7UAxq4NdvbOCFVmpYVmLPb75TkKgg0eh_Yxz0tiv1jz1ohpaMYkaxusQcd9FZvqEqbWn-Wte_gmUyzuaFu9_OZENNnYryHuLFKy0EOCTc4aozB3y_uk)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdHZV5RN_M-AuRmAcO__Db1ka8-Z_AeiS1S3iQy7L7s8tkJapIAIp9ZpumF3_ZzMiUMKvN7NCJKNoq-H8gNcSBpqvTlutl-jNPgkvz4Kv8uKX2WBVODw==)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzSBq4Isglpye4roSqseRQNjSNKF-UJJQskbA2Cbd474EJOwP3MmJD2nH93thwDz8OoEpu5V--80DTzHTgJZasRIblFlcyDGAcFz0aUoZDRAVCFix0Ddv_258RcBX4osQSffUzDrGHhAXat8I1iacMndiKc3z54xqtKbinMccfj7HXGRzgkIiAjqF04PeI380LszJrjDVXQqjFNadSF-UW8ufebxHXb_k50L81H-wzzR79)
10. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_8lGCQRBTqN7dsCAw_tFUxAaiAR46av36dwX5ECwaHqG4e7WGcTR6xno1a9tF9FzpXrT_y5D7M_o_Am7gMH6_eDibhnTtUDSVkq4Y5yJvD4zE2tcU-_zkJmcpQlLwqYRCMk3MYg1lRbBiVA==)
11. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvQ38x1iqcqFhE5XDcGGdFskbn_jio1sAk8kiydLfP8GAcKsg3jpucXwf-pkqkIz1fgUqRTfhLrjp1JuIW9qAxu66qExDxR3sZYZS8HQ-hpGziZ-QnHrL56OEBNz6-r9QgsWHUrg==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0RMQ2B5WG6nOtjM1A1_DhPlUDc7fwqJ0U2foyX5jFoukJ7piy4xls8M4kIxnc8Zrx37ph29qaHSO-ZCsg7My5ZruMiLR8MBW5q7DPjCyMAap-OuC6a5YoCA==)
13. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHm5NftUlJrUBxvPk3S6V1AKDRdlc4xRdQ3uFclGKAxmbTQaiGLslVLND3Spp3W8d6j11t2LhG1aQljP84Ca4KcNrsVwZuTsMQQ620WEBMp8RUoBvD-byt7qFC5TJpTQhKOsPWs--dPh21YNJTKzXo=)
14. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1QKbnOXTSfBrKy-9AuMTYS4pqmsZB3_3ZBqfp3itTxjZ5P0_REbCfWsLmQijmZcTJ19tiX8Umep1Ii4lNQn29wymyAuemClLPgvQRATcXCdALTGfmHkujnBb0tSufpUZ2hIKbG3so4s53FYMuaC-h)
15. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsabpQEbmt5dOUUCzGmADAEOWzPyHXLDCmzH_VKjXDKN7OsVYoD_ikPHs3gtmGIrkg87KRTxSl50VUsSbO5-sA-Kya0riVd3_ATLIOAYco77bDLFcnJZ9_Jx4xALkYXuJwWQv4A7A04g==)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaqFHfzx_efLr4EppG_NDq5JvpS3NC6as_G2YSrb7QQkwvjZz7hUTlUG48sB0WwOGDXKkAsAQtapZm64nE7GTtcb4s3X0FN6FdkbSH6x2cfGrTrov1lBcTJ-kdPtOIC2WUGYwQGnsapzGz_PBAsmnyPiPGOUHzVMAuxmKsarke)
17. [smartchair.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgzWQxszRzziF2oveAVKVxKlqEjhTKyUI9MdrgvEYCKE3p3mEumVoOZk5bLxG7_wUm_Mn-Y1hsrubioNncbazYSF4RS3h2WbwvRGwG7gxZmZtzC1zY99POo1hVIxVZSDG0mbvxoCLHYuDZStAQwDT-e8XnkJ-hIWp6dRl5x5le8u3lLZ4Og9tNtwUaLoUsBSeMNwyzEoSxaDrzpfM=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTVoUPqnbNQ4DCYTM41rx5eSYkpKHp3jhffCjiKukxsJMV0B2YtqJx9gC5PcZhIW9YQIykfZ1z6xktYnPI_2G7BXVrE4CNaQwxV_qfy9tXxnOq3mTde_rIWQ==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGwW0gOZc4Dx8OAHUu7PpvqZjko8T4YEPewPffD7WfDG3BtgEFSuoYyZDLrZuE-6IxP2wyR9OyH5POJS3GXSv2A4gyX2dlHV5NhlzpkAMffMEJeHgcGw==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmHYys2WOKxffSDN6RPDtN7kkiJiW31U6u5QzqJ7irJLncPtJE_o0JoNmvYGrGe9fR6BeKPvX7NVeVIoyTnGdghgwZGVKmp8nHV1Hn0eSYF5myyma1tw==)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsLuOoT_k3fVTtx4jwZaAnWO1CPWv2P6mUQCs3A0nbHBjGel1nKYiGOiV3kxxwGxCpIQT1zgrzHbUxNWRiToOri9nzvu8dLdZDVCzOKE5hktYsbVTzE76IBisvOASYs2yfSnpF4qhiP04gHWzxHxdyfHTQKzOL2KXQKbrmpuX4)
22. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1TLQiwhp5GjLS-CryxwUbMo_0U1t1zFBQTQ9n6KEjI-PnZwS-7TbTHurYo8iSjrPgho5Iw1L4YlUgnDdSAo9bADV139m0yvzE-BsTpSPTUko88qm9MsE14oLXGuD6FTUMAiONlo4TK8qz21cDVj9a_XLg5Rf-NAQdLulviKCXqbCHJpnz8wZ9L8pTOoGrXRUTm3T5zlNGFUiwTmunLe-dCcQHvu1SC_9KJQgiAVpcFtn9N1P6YKvIHJM-6_tHBfBE4d_LtRhJ-NgK_Sc=)
23. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiEBFGvstHZ9agCaPZYCGyw6GtMucL-oyqEG0Bs8FcJqHtWyCAZvMgpWN6v-MObr4kNBOjrKriUuHcQ5RltsMGCmxrwssvDQEecphEaYXX0zGsHGARP45KYfwpAtgSpVqylHSg976vhQ==)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGH5ooPn31Nq0x9pkPbcxXED6SA9KenSgwhUGtPKbCSaiZ7SXqUQNXPYbdCZ-d6WYmdmxKLIIvQ8D5NklQ0oLLprLLypT4TzgvmI9HnE60U0y7C6dJ0oLu-CdAT-xtPPzRD-5ttHUeNilBgy3w8a8CO6PC61KO9jkvL-niupYrvXeUpHEDGTluzuLIzArGLdaPLXhR2rLT6qhDnDY2JGOscHSuImokuC5VxuDrICx5A76vcMsUabcXfCbxp5MTCcg==)
25. [usp.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmiF3OEfeTezj6--EQ9o1gOloWVYBPpE51WQ4rhCV_i_68LVUIhx2Rj7aKrgfyT8L41DXxJe2eFYSYNKGLVIWXmMUewplUALwlu98_31EDAhoZg_ElyROcgc2csRnnzQrhlcNkqtnqB6ii1A==)
26. [kias.re.kr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEO1sqz6XXoHqjj9Cw2bWVCDmyib44qdVk4rTlY_LVT4DzAjlXjbFKZo83ampqdSsVoBScB2f1cXOw804xHdmhnhJHThFKLOVjhnSGaVIVKx6xXkvdAuvxq2tOFckf4xV8AdRN4VoBVdNeCpiJo3hE2XLilwmx5zQCelupEvuVx_r_wNj0ZinTdLInzJDnN2M5h)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhNHA8UJAA2QDMYRBVCNiu2JGBfGQUXpzg0ETpZkNISXSBri7n3E7jinMzNZ0K3HvJsOlp7EMTzKKiVJE6Lb36nR2hi2aoqVU6osLgGEr0ZF0IymLXLQ==)
28. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYVrRQSqhYWR_3HRqxswwfoJ2WQgFXxowEoPLt5Ac-ksNP_Je7kIb2YwS35Y0ot8UVzQkxskEcvWsDTH4KOOE65q2aIp24EyYYF83lM-CBRGNNDDJirZb2KeZuyxDjs3Xt)
29. [mfo.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyEvw8t1Wn09SmnEZsPvMaqJJRiWusIcrV01K65qJWPEyvI_RgZJmv1euCC2xBiWwe8Pff3Az9_OseMvVgLkenQHutKQCpZT_E-wcVUwOUYjZDQyVOw1O0nLyi1Tn31CGBkeaMrKM24NSDT8B24GRxYb_4BX3FUY9K4YSq3b6hx-t4DrA8e1rbtxT4o3m1n1cYDQ==)
30. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEih-SJCGDjPXMbHVYySChK1XOPNF7zi1rpu_cDGX5vHr5-AJQ1NVnOu40sPoP_5QivQEaBTUxe-sDrUbHCQR2CbRLCQJYvg1eNIsco6wizHqW8r2y6B79hT52lxzrNlNSS-hVX)
31. [queensu.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxAYtMPOavY_I22d9pAHjOgWn3_ijG506zajTm3xOP6CUX9OjwI0xDmvf5tsUuDV72aI2sHljvI6WWyom64D_eGZ-OIRU3z6IOLUC91sRlfSXg2XqLdn4Q5_Sn_gW8vny2nkJ5ncK-ad1YVtx38CZUoeku)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVpP6Z5gKkE0sVdStLsWCBUrUqFXwNHK5lQpcdh_DzsOCmrgCLxKyRZrt5RKCBJf7-shLxqqDCOgzgbD8fSwpsJ199Thdx-fBtdJ55nLW6tdSpR-7Fng==)
33. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiXSLh7Zg3YnJcSEvAvrf0N7biLyUKiOj6SpPA-mtUvTTtYa6EJJUX6ux3VyH3M35zi2D7nqWYEn6IyLGEL7tSQccxh7_3OrdPwgdTdFW9EVo-EnK4pQ==)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEg76l62bIWVCTMWdxLgUpJXJEd_8uJZa17Dwant_mfxmawMGKNTSGy2oZsleuNe3wghPTUmV9Xq_UU2tAdfmR8oVTXSzQxQYQoAaF33NYBJ8NFTkTAns1WDA==)
35. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUy7pmPonCzsWfrDmVkzz5RSuXIAKPbI6xSkiZ-7Kc5JJS4qQclFjLhtRxU7J62pMI3P88kUPDS0ldjW1-6AJK65TIUQy0nktQapv_v1wQZ7ZYdvgF02hSuMAq6ciyuVewJVl3w0pu_lFJhdCymaL1)
36. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7NNUMv6AOYVV1fppox-31-kXpLmBgg2ZxYOKFbYTeCegJdUv6l9XzFbP32qNate8-qTIsdUX0KCWL0IfzHrFRzdlxZ9uWDQBUlsZkRcJmgDwX9KakG75x_CUAoBGltMrHFjWA0G-nyt0eHY-6nT0FrpzyLL8Big==)
37. [ncsu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGD83aal7js_cEBkwHUsvHVHARRj63zlvlaI_gG3YCJ93PNQ0Li58L2jahXqaalz0nj1MGFQf6WR70JKRro7lu0qJyppmMP2LEIiLxwq6lS-W3KrluKkvjYvprXO_2MiV_XaX1RdEr4jTQnXQ==)
38. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEK5Wm3EU4yjM5XZ0REcmZ2lKOXWvxaYw5PqfqrJCT64Q9ShfnWmedkGGAQRE3QZedlRx_zOafIRmiTzcYp2u8JHJw4vO203tyYL1GXyeBSJRU7V26PeWXy_w==)
39. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWKrZZjbeV_4syDxqmsJL6SwKS2mO_AbPk5uAerMS44TSwMIn8zChvX1d0A3wkCo_-P1eagFlo0o3CNf5vEgEif4AUEmZtnyrqsGltTr2IZol7vgruPSLELD0kcQBVN3IZpoAcNM4=)
40. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6whoFZt5nXV2j7ebz9K1MUnaqfS38ZokrzJPYaZHg5FB-rB55BQCuzIw8PVj3VLSE5zEds6Dd7muBhtGK5WWBzTShnzB1iY-oJ6bVt1K83IR938wpAw==)
41. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLMzJvyk5WFPnkuzb1rc2gNsatgavho_uXp4qmuVZ7OvsL9yduvK6TSRcVCKkbPvRWS4o2W_XD8XjYG8EU5AXcVyDSVaO8mLDUUZ0iPyUz5HbLL9ayFEHm9PYJMZLRackWMbN4mCjZ21pF-buIl_zpla2dkFaTmctqVtURPAgDv09L8pc6yWR49Q84exYWG5OYGL6Oko5ZSFOg-wRynNd4xBXfbQIK0_IQ2uceWrkv-lXeObWCub84tvE2tRnhm5wp22xtK63a)
42. [cmu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoU0Scu-UMllEZXtHImpU1D9Jr6TWe6LLXGdjQGg17VIpz-IurVA5DWvkdC9yWtOICv8cgTEyL0bKt6TDPtfOEMCLBVRSWJZT6lFEUUmVrFKJ-B8z9glNj32oPZd3wAaYzKh1f)

