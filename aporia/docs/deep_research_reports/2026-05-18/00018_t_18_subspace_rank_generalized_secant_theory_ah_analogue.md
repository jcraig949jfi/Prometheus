# T#18 Subspace rank / generalized secant theory (AH analogue)

**Pythia queue id:** 18
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdjWHNMYXNDeUp1T045TW9QMjVUVGlRVRIXY1hzTGFzQ3lKdU9OOU1vUDI1VFRpUVU
**Elapsed:** 578s
**Completed at:** 2026-05-18T20:59:32.670254+00:00

---

# Subspace Rank and Generalized Secant Theory: Towards an Alexander-Hirschowitz Analogue

**Key Points**
*   **Subspace rank** is a potent geometric and algebraic tool introduced to generalize classical tensor rank and Waring rank, measuring the minimal number of points on a variety whose linear span contains a given multi-dimensional linear subspace.
*   The **Alexander-Hirschowitz (AH) Theorem** fundamentally classifies all defective secant varieties of Veronese varieties. The ongoing search for an "AH analogue" aims to classify defective cases for generalized structures, such as Segre-Veronese varieties and Grassmann secant varieties.
*   **Grassmann secant varieties** represent the geometric parameter space for subspace rank and simultaneous Waring decompositions. Defectivity in these spaces—known as Grassmann defectivity—has profound implications for tensor identifiability.
*   **Cactus varieties** and **Grassmann cactus varieties** provide scheme-theoretic generalizations of secant varieties by accommodating non-reduced 0-dimensional subschemes (limits of points). Research suggests that for specific bounded ranks (e.g., $r < 8$), secant and cactus varieties coincide, while they diverge at higher ranks.
*   Recent breakthroughs strongly indicate that Segre-Veronese varieties of multi-degree $(d_1, \dots, d_k)$ are non-defective when all $d_i \ge 3$, marking significant progress toward a generalized AH analogue.

**Introduction for the General Reader**
In higher mathematics, specifically algebraic geometry and algebraic complexity theory, researchers often try to break down complicated mathematical objects—like multidimensional arrays of numbers called "tensors" or complex polynomial equations—into the sum of the simplest possible building blocks. The minimum number of basic blocks needed to build the complex object is called its "rank." In the 1990s, mathematicians Alexander and Hirschowitz proved a famous theorem that perfectly mapped out exactly when the geometry of these decompositions behaves "as expected" and when it has surprising, "defective" exceptions. 

Today, mathematicians are trying to establish an "analogue" or equivalent of this theorem for even more complex scenarios. Instead of decomposing a single object, they look at "subspace rank," which is equivalent to decomposing *multiple* complex objects simultaneously using the same set of basic building blocks. To study this, they use "Grassmann secant varieties" and "cactus varieties"—intricate geometric spaces that track these decompositions. Finding a complete generalized Alexander-Hirschowitz analogue remains one of the most active and challenging frontiers in algebraic geometry, with direct applications in signal processing, quantum computing, and statistics.

---

## 1. Introduction to Secant Varieties and Tensor Ranks

The study of secant varieties and the decomposition of tensors into fundamental rank-1 components is a ubiquitous problem spanning algebraic geometry, representation theory, signal processing, algebraic statistics, and geometric complexity theory [cite: 1, 2]. At its core, the problem seeks to understand the additive decomposition of a complex structure—such as a homogeneous polynomial, a completely symmetric tensor, or a partially symmetric tensor—into minimal fundamental units. 

### 1.1 Geometric Formulation of Rank
Let $V$ be a finite-dimensional vector space over an algebraically closed field $\mathbb{K}$ (typically $\mathbb{C}$ of characteristic zero) [cite: 3, 4]. Let $X \subset \mathbb{P}V$ be an integral, non-degenerate projective variety [cite: 3, 5]. The points of $X$ represent the "simple" or "rank-1" elements of the ambient space. For instance, if $X$ is a Segre variety, its points parameterize elementary tensors; if $X$ is a Veronese variety, its points parameterize pure powers of linear forms [cite: 4, 6].

For a point $p \in \mathbb{P}V$, the **$X$-rank**, denoted $r_X(p)$, is defined as the minimal integer $r$ such that $p$ lies in the linear span of $r$ points on $X$:
\[ r_X(p) = \min \{ r \in \mathbb{Z}_{>0} \mid \exists x_1, \dots, x_r \in X \text{ such that } p \in \langle x_1, \dots, x_r \rangle \} \]
This discrete measure describes the minimal length of a decomposition [cite: 7, 8]. 

### 1.2 Secant Varieties
To study $X$-rank geometrically, one considers the loci of points of bounded rank. The **$r$-th secant variety** of $X$, denoted $\sigma_r(X)$, is defined as the Zariski closure of the union of all linear spaces spanned by $r$ points of $X$ [cite: 4, 5]:
\[ \sigma_r(X) := \overline{ \bigcup_{x_1, \dots, x_r \in X} \langle x_1, \dots, x_r \rangle } \]
If a point $p \in \sigma_r(X) \setminus \sigma_{r-1}(X)$, it is said to have **$X$-border rank** $r$. Because taking the Zariski closure adds limits of spans, the border rank of a tensor can be strictly smaller than its actual rank—a phenomenon crucial to fast matrix multiplication algorithms and algebraic complexity theory [cite: 2, 9].

### 1.3 Expected Dimension and Defectivity
A fundamental question in the theory of secant varieties is determining their dimension. By a simple parameter count, choosing $r$ points on $X$ requires $r \dim X$ parameters, and specifying a point within their $(r-1)$-dimensional linear span requires an additional $r-1$ parameters [cite: 3, 10]. Thus, the **expected dimension** of $\sigma_r(X)$ is:
\[ \text{expdim } \sigma_r(X) = \min \{ \dim \mathbb{P}V, r(\dim X + 1) - 1 \} \]
By Terracini's Lemma [cite: 10, 11], the actual dimension of $\sigma_r(X)$ is bounded above by this expected dimension:
\[ \dim \sigma_r(X) \le \text{expdim } \sigma_r(X) \]
If $\dim \sigma_r(X) < \text{expdim } \sigma_r(X)$, the variety $X$ is said to be **$r$-defective**, and the difference $\delta_r(X) = \text{expdim } \sigma_r(X) - \dim \sigma_r(X)$ is the **defect** [cite: 2, 3]. Determining which classical varieties are defective is a long-standing challenge whose most famous resolution is the Alexander-Hirschowitz Theorem.

## 2. The Alexander-Hirschowitz Theorem

The Alexander-Hirschowitz (AH) theorem is the crowning achievement in the classical theory of secant varieties. It completely classifies the dimensions of the secant varieties of Veronese embeddings of projective space, which corresponds algebraically to solving the generic Waring problem for homogeneous polynomials [cite: 5, 12].

### 2.1 Statement of the Theorem
Let $\nu_d(\mathbb{P}^n) \subset \mathbb{P}(\text{Sym}^d \mathbb{C}^{n+1})$ be the $d$-th Veronese embedding of $n$-dimensional projective space. The ambient space has dimension $\binom{n+d}{d} - 1$. The AH theorem states that the $s$-th secant variety $\sigma_s(\nu_d(\mathbb{P}^n))$ has the expected dimension:
\[ \min \left\{ \binom{n+d}{d} - 1, s(n + 1) - 1 \right\} \]
**except** in a complete and finite list of defective cases [cite: 5, 13].

The known defective cases are exactly the following [cite: 3, 5]:
1.  **Quadrics:** $d=2$, for any $n \ge 2$, and $2 \le s \le n$. (Quadratic forms are given by symmetric matrices, and generic rank is maximal, preventing the secant varieties from filling the space as quickly as parameter counts suggest).
2.  **Binary quartics / Cubics in $\mathbb{P}^4$:** $(n, d, s) = (2, 4, 5)$. Expected dimension is 14, actual is 13.
3.  **Quartics in $\mathbb{P}^3$:** $(n, d, s) = (3, 4, 9)$. Expected dimension is 35, actual is 34.
4.  **Quartics in $\mathbb{P}^4$:** $(n, d, s) = (4, 4, 14)$. Expected dimension is 69, actual is 68.
5.  **Cubics in $\mathbb{P}^4$:** $(n, d, s) = (4, 3, 7)$. Expected dimension is 34, actual is 33.

These exceptional cases have been re-proven using various methods over the decades, including K. Chandler's application of the differential Horace lemma, Brambilla and Ottaviani's streamlined Horace method with codimension-3 linear subspaces, and Postinghel's projective space degeneration [cite: 5]. 

### 2.2 The Search for an "AH Analogue"
The absolute classification provided by the AH theorem for Veronese varieties immediately prompted researchers to ask: Can we find analogous classifications for other fundamental varieties?
1.  **Segre Varieties:** Parameterizing elementary tensors in $\mathbb{P}V_1 \times \dots \times \mathbb{P}V_k$. This represents the generic rank of multidimensional tensors [cite: 1, 14].
2.  **Segre-Veronese Varieties:** Parameterizing partially symmetric tensors, embedded by multidegrees $(d_1, \dots, d_k)$ [cite: 3, 15].
3.  **Grassmann Secant Varieties:** Extending from the rank of a *point* to the rank of a *subspace* (subspace rank), searching for a classification of Grassmann defectivity [cite: 13, 16].

These open quests are collectively referred to as the search for an **Alexander-Hirschowitz analogue**.

## 3. Subspace Rank and Grassmann Secant Varieties

While classical tensor rank concerns the minimal length of a decomposition for a single tensor (a point in $\mathbb{P}V$), modern applications in signal processing, blind source separation, and algebraic complexity theory often demand the simultaneous decomposition of *multiple* tensors [cite: 2, 3]. This leads to the definition of **subspace rank** and its geometric counterpart, the **Grassmann secant variety** [cite: 9, 12].

### 3.1 Defining Subspace Rank
The concept of subspace border rank was pioneered by Terracini in 1915 and studied by Bronowski in 1933 [cite: 13]. It was formalized and explicitly reintroduced into modern tensor geometry by Buczynski and Landsberg in 2013 as a tool for studying the generic ranks of tensors and generalized $X$-ranks [cite: 2, 17]. 

Let $X \subset \mathbb{P}V$ be a projective variety not contained in a hyperplane. Let $E \in \text{Gr}(k, V)$ be a $k$-dimensional linear subspace (representing a $(k-1)$-dimensional projective linear subspace in $\mathbb{P}V$). 
The **subspace rank** (or $X$-rank of the subspace $E$) is defined as the minimal integer $r$ such that there exist $r$ points $x_1, \dots, x_r \in X$ satisfying:
\[ E \subset \langle x_1, \dots, x_r \rangle \]
When $k=1$, $E$ is a line in $V$ (a point in $\mathbb{P}V$), and this reduces precisely to the standard $X$-rank of a point [cite: 2, 16]. 

### 3.2 Grassmann Secant Varieties
To study subspace rank geometrically, we define the **Grassmann secant variety**. Let $\text{Gr}(k, V)$ denote the Grassmannian of $k$-dimensional vector subspaces of $V$. The $(r, k)$-th Grassmann secant variety of $X$, denoted $\sigma_{r,k}(X)$, is the Zariski closure in $\text{Gr}(k, V)$ of the set of $k$-planes that are contained in the span of $r$ points of $X$ [cite: 13]:
\[ \sigma_{r,k}(X) := \overline{ \{ [E] \in \text{Gr}(k, V) \mid \exists x_1, \dots, x_r \in X \text{ s.t. } E \subset \langle x_1, \dots, x_r \rangle \} } \]
In older literature, this is sometimes denoted $G_{k-1, r-1}(X)$ or $GS_X(k-1, r)$ representing projective dimensions [cite: 2, 16]. 

The border subspace rank of $E$ is simply the minimal $r$ such that $[E] \in \sigma_{r,k}(X)$. As with classical secant varieties, $\sigma_{r,1}(X) = \sigma_r(X)$ [cite: 13]. 

### 3.3 Expected Dimension and Grassmann Defectivity
The expected dimension of the Grassmann secant variety $\sigma_{r,k}(X)$ is derived by a parameter count. Specifying $r$ points on $X$ requires $r \dim X$ parameters. Their span is an $(r-1)$-dimensional projective space. Choosing a $k$-dimensional vector subspace (i.e., a $(k-1)$-dimensional projective space) inside this $r$-dimensional vector space requires $\dim \text{Gr}(k, r) = k(r-k)$ parameters [cite: 2].
Thus, the expected dimension is:
\[ \text{expdim } \sigma_{r,k}(X) = \min \{ \dim \text{Gr}(k, V), r \dim X + k(r-k) \} \]
If the actual dimension of $\sigma_{r,k}(X)$ is strictly less than this expected dimension, $X$ is said to be **$(r, k)$-Grassmann defective** [cite: 16].

The defect is given by:
\[ \delta_{r,k}(X) = \text{expdim } \sigma_{r,k}(X) - \dim \sigma_{r,k}(X) \]
Classifying Grassmann defectivity is the direct generalized analogue of the Alexander-Hirschowitz theorem for linear systems of tensors [cite: 18]. 

### 3.4 Connection to Simultaneous Waring Rank
When $X = \nu_d(\mathbb{P}^n)$ is a Veronese variety, a $k$-dimensional subspace $E \subset \text{Sym}^d \mathbb{C}^{n+1}$ represents a linear system (or a collection) of $k$ homogeneous polynomials of degree $d$. 
The subspace rank of $E$ with respect to the Veronese variety is exactly the **simultaneous Waring rank** of the collection [cite: 13, 18, 19]. This is the minimal integer $r$ such that there exist $r$ linear forms $L_1, \dots, L_r$ such that *every* polynomial in $E$ can be written as a linear combination of $L_1^d, \dots, L_r^d$ [cite: 13].

Terracini explicitly noted in 1915 that the Veronese variety has a Grassmann secant variety filling the ambient Grassmannian if and only if a generic collection of $k$ forms of degree $d$ can be expressed as linear combinations of the powers of the same $r$ linear forms [cite: 18]. This establishes the simultaneous Waring problem as a central motivation for analyzing Grassmann secant varieties.

## 4. The Geometry of Grassmann Defectivity (The AH Analogue)

To establish an AH analogue for Grassmann secant varieties, researchers have developed mechanisms to translate Grassmann defectivity into classical secant defectivity on multiprojective spaces. 

### 4.1 The Second Terracini Lemma and Dionisi-Fontanari
In 2001, Dionisi and Fontanari generalized an observation by Terracini regarding the Veronese surface, proving a powerful structural connection between the Grassmann defectivity of a variety $X$ and the classical secant defectivity of the Segre product of a projective space with $X$ [cite: 16].

**Theorem (Dionisi-Fontanari, 2001):** Let $X \subset \mathbb{P}V$ be an irreducible non-degenerate projective variety. Then $X$ is $(r, k)$-Grassmann defective with defect $\delta$ if and only if the Segre product $\text{Seg}(\mathbb{P}^{k-1} \times X)$ is $r$-defective with the exact same defect $\delta$ [cite: 16].

This profound equivalence allows mathematicians to convert the difficult problem of determining the dimensions of Grassmann secant varieties $\sigma_{r,k}(X)$ into the problem of computing the dimensions of standard secant varieties $\sigma_r(\text{Seg}(\mathbb{P}^{k-1} \times X))$ [cite: 13, 16]. Specifically, if $w = \min\{k-1, r-1\}$, the exact relation of dimensions is:
\[ \dim \sigma_r(\text{Seg}(\mathbb{P}^{k-1} \times X)) = \dim \sigma_{r,k}(X) + k \cdot w - 1 \]
This implies that proving an AH analogue for Grassmann secant varieties of $X$ is mathematically equivalent to proving an AH analogue for the standard secant varieties of partially symmetric tensors in $\mathbb{P}^{k-1} \times X$ [cite: 3, 16]. 

### 4.2 Known Results in Grassmann Defectivity
Thanks to the Dionisi-Fontanari reduction, much of the research on Grassmann defectivity has focused on specific classes of $X$:
1.  **Curves:** It is a known result by Catalisano, Geramita, and Gimigliano (2002) that algebraic curves are *never* Grassmann defective [cite: 3]. 
2.  **Surfaces and Threefolds:** A complete fine classification of Grassmann defective smooth surfaces and threefolds was developed in works by Chiantini, Ciliberto, and Copland [cite: 3, 19].
3.  **Veronese Varieties:** The classification of Grassmann defectivity for Veronese varieties $\nu_d(\mathbb{P}^n)$ translates to studying the secant varieties of the Segre-Veronese embedding $\mathbb{P}^{k-1} \times \mathbb{P}^n$ via $\mathcal{O}(1, d)$. For instance, Ballico, Bernardi, and Catalisano classified all Grassmann $(2, s)$-defective Veronese varieties, discovering that $\nu_a(\mathbb{P}^n)$ is $(2, s)$-defective in very narrow cases, such as $a=3$ and $s=5$ [cite: 3, 20].
4.  **Buczynski-Landsberg Bounds:** Buczynski and Landsberg (2013) introduced the subspace rank to explicitly derive new upper bounds for the rank of a tensor and uniquely mapped out the ranks of partially symmetric tensors in $\mathbb{C}^2 \otimes \mathbb{C}^b \otimes \mathbb{C}^b$, leveraging Kronecker's normal form for pencils of matrices [cite: 2, 17]. Because $k=2$ corresponds to pencils of matrices, the Grassmann secant varieties $\sigma_{r,2}(X)$ form the backbone of these bounds [cite: 2].

## 5. Segre and Segre-Veronese Varieties: The Frontier of the AH Analogue

Because the Dionisi-Fontanari theorem reduces Grassmann defectivity to the secant varieties of Segre-Veronese varieties, solving the AH analogue for Segre-Veronese varieties has become one of the most critical endeavors in modern algebraic geometry [cite: 16, 21].

### 5.1 Segre-Veronese Embeddings
Let $\mathbb{P}^{n_1} \times \dots \times \mathbb{P}^{n_k}$ be a multiprojective space. The Segre-Veronese embedding of multidegree $(d_1, \dots, d_k)$ maps this space into $\mathbb{P}(\text{Sym}^{d_1}\mathbb{C}^{n_1+1} \otimes \dots \otimes \text{Sym}^{d_k}\mathbb{C}^{n_k+1})$ via the sections of the sheaf $\mathcal{O}(d_1, \dots, d_k)$ [cite: 3, 15].
*   When $k=1$, this is a Veronese variety (AH theorem applies) [cite: 3, 5].
*   When $d_1 = \dots = d_k = 1$, this is a Segre variety (modeling generic tensor rank) [cite: 14, 22].
*   Mixed degrees model partially symmetric tensors [cite: 3, 15].

### 5.2 Defective Segre-Veronese Varieties
A vast literature has been dedicated to classifying defective Segre-Veronese varieties. Abo, Brambilla, Catalisano, Geramita, Gimigliano, and Ottaviani have iteratively built a conjectural list of all defective cases [cite: 21, 22, 23].
It has become apparent that defectivity is common when degrees are low (e.g., $d_i = 1$ or $d_i = 2$). 
*   In 2011, Abo and Brambilla proved the existence of previously unknown defective secant varieties of 3-factor and 4-factor Segre-Veronese varieties, significantly expanding the known lists [cite: 23, 24].
*   For the bidegree $(1, d)$ embeddings of $\mathbb{P}^m \times \mathbb{P}^n$ (which correspond directly to the simultaneous Waring rank of $m+1$ forms of degree $d$), classifications have been intensely studied. Abo and Brambilla showed that there are no defective $s$-th secant varieties except possibly for a narrow band of $s$ values, a gap that was closed further by Dolezalek and Ken for large $n \gg m^3$ [cite: 3, 25, 26].

### 5.3 The "Degrees $\ge 3$" Breakthrough
A major milestone in establishing the AH analogue for Segre-Veronese varieties occurred recently regarding higher degrees. In 2013, Abo and Brambilla conjectured that Segre-Veronese embeddings are *never* secant defective if all degrees $d_i \ge 3$ [cite: 21, 22]. 

The proof required establishing non-defectivity for base cases like bidegrees $(3,3), (3,4),$ and $(4,4)$. In 2021, Galuppi and Oneto successfully solved the base cases [cite: 22, 27]. Building on this, in 2024, Abo, Brambilla, Galuppi, and Oneto formally published the definitive proof:
**Theorem (Abo, Brambilla, Galuppi, Oneto, 2024):** Let $X$ be a Segre-Veronese embedding of multidegree $(d_1, \dots, d_k)$ with $k \ge 2$. If $d_i \ge 3$ for all $i=1, \dots, k$, then $X$ is never secant defective [cite: 21, 28].

This powerful result drastically narrows the search for the complete AH analogue. It proves that defectivity in partially symmetric tensors is strictly a low-degree phenomenon, much like how the AH theorem restricts defectivity primarily to quadrics and a few specific cases of cubics and quartics [cite: 5, 28]. 

### 5.4 Techniques for Proving Non-Defectivity
Proving non-defectivity generally relies on demonstrating that the generic actual dimension matches the expected dimension. The primary geometric tool is **Terracini's Lemma**, which states that the tangent space to the secant variety $\sigma_r(X)$ at a generic point $p = x_1 + \dots + x_r$ is the linear span of the tangent spaces to $X$ at the points $x_i$ [cite: 10, 11]:
\[ T_p \sigma_r(X) = \langle T_{x_1}X, \dots, T_{x_r}X \rangle \]

To calculate the dimension of this span, researchers reformulate the problem as an interpolation problem involving **fat points**. A 2-fat point is a scheme defined by the square of the maximal ideal at a point [cite: 21, 27]. The defectivity of the secant variety is equivalent to the failure of the linear system of hypersurfaces of multidegree $(d_1, \dots, d_k)$ to impose independent conditions on a generic union of $r$ double (2-fat) points [cite: 22, 27].

To bound this, researchers utilize **degeneration techniques**, such as the "collision of fat points." By allowing general points to collapse into specific configurations (e.g., a 3-fat point with points infinitesimally close), the dimension of the linear system can be upper-bounded. If the upper bound matches the expected dimension, the variety is proven non-defective [cite: 22, 27]. This specific degeneration tactic was instrumental in solving the bi-degree $(3,3)$ base cases [cite: 22].

## 6. Cactus Varieties and Border Rank Obstructions

While secant varieties measure the rank of points constructed as generic finite sums, modern algebraic geometry introduces **cactus varieties** to handle the limits of these spans. Cactus varieties are crucial because they form a natural geometric obstruction to computing lower bounds on tensor rank [cite: 29, 30].

### 6.1 Definitions of Cactus Varieties
A finite subscheme $R \subset X$ of length (or degree) $r$ is a zero-dimensional scheme whose coordinate ring has dimension $r$ as a $\mathbb{K}$-vector space [cite: 9, 31]. If $R$ consists of $r$ distinct reduced points, its linear span is simply the span of those points. However, $R$ can also be non-reduced (e.g., points with tangent vectors or higher-order infinitesimal structures) [cite: 13].

The **$r$-th cactus variety** of $X$, denoted $\kappa_r(X)$, is the Zariski closure of the union of the linear spans of all finite subschemes of $X$ of length at most $r$ [cite: 4, 9]:
\[ \kappa_r(X) := \overline{ \bigcup_{\substack{R \subset X \\ \text{length}(R) \le r}} \langle R \rangle } \]
By definition, because any $r$ distinct points form a scheme of length $r$, the secant variety is always contained within the cactus variety:
\[ \sigma_r(X) \subseteq \kappa_r(X) \]
The concept extends naturally to Grassmann secant varieties. The **$(r, k)$-th Grassmann cactus variety**, $\kappa_{r,k}(X)$, is defined by considering $k$-dimensional vector spaces contained in the linear spans of finite subschemes of length $r$ [cite: 9, 13, 30]. 

### 6.2 The Cactus Barrier
Cactus varieties are fundamentally linked to the **Apolarity Lemma** and multi-graded Hilbert schemes [cite: 4]. The cactus rank of a point $p$ is the minimal length of a subscheme $R \subset X$ such that $p \in \langle R \rangle$ [cite: 31]. 

The "cactus barrier" dictates that many linear rank methods (such as those using catalecticant matrices and flattenings to compute lower bounds on border rank) are actually testing membership in the *cactus* variety rather than the *secant* variety [cite: 13, 29]. If $X$ is a sufficiently high-dimensional variety, the cactus varieties $\kappa_r(X)$ fill out the ambient projective space much faster than the secant varieties $\sigma_r(X)$ [cite: 4, 32]. Therefore, linear rank methods can never provide a lower bound for the $X$-border rank that exceeds the generic cactus rank [cite: 29].

For example, for the Segre embedding of $\mathbb{P}^{a-1} \times \mathbb{P}^{b-1} \times \mathbb{P}^{c-1}$, the $g$-th cactus variety fills the ambient space at $g = 2(a+b+c-2)$, while the secant variety requires a much higher $r$ to fill the space [cite: 29]. This highlights why distinguishing between $\sigma_r(X)$ and $\kappa_r(X)$ is critical in complexity theory [cite: 30].

### 6.3 Equality of Secant and Cactus Varieties ($r < 8$)
A pivotal question is: when do the secant variety and the cactus variety coincide? 

For the Veronese variety $\nu_d(\mathbb{P}^n)$, it is deeply connected to the smoothability of local Gorenstein algebras. If every finite local algebra of degree $r$ is smoothable (i.e., can be deformed into $r$ distinct points), then the limits of their spans perfectly mirror the limits of secant planes, meaning $\sigma_r(\nu_d) = \kappa_r(\nu_d)$ [cite: 13, 33].

A celebrated result dictates that for small ranks, specifically **$r < 8$**, the equality holds universally for Veronese embeddings:
\[ \sigma_{r,k}(\nu_d(\mathbb{P}^{n+1})) = \kappa_{r,k}(\nu_d(\mathbb{P}^{n+1})) \quad \text{for all } d, n, k \ge 1 \text{ when } r < 8 \]
This was explicitly proven for standard cactus varieties and extended to Grassmann cactus varieties [cite: 13]. The threshold $r=8$ is exactly where things break down. The Hilbert scheme of 8 points in affine space of dimension $\ge 4$, $\text{Hilb}^8(\mathbb{A}^n)$, becomes reducible, possessing a non-smoothable component [cite: 31].

Specifically, Cartwright, Erman, Velasco, and Viray (2009) classified the components of $\text{Hilb}^8(\mathbb{A}^n)$, showing that for $n \ge 4$, there exists a non-smoothable component [cite: 13, 31]. Consequently, the $14$-th secant variety and the $14$-th cactus variety diverge, e.g., $\sigma_{14}(\nu_d(\mathbb{P}^6)) \neq \kappa_{14}(\nu_d(\mathbb{P}^6))$ [cite: 13]. Similarly, the $8$-th Grassmann cactus variety of $3$-dimensional spaces diverges from the Grassmann secant variety $\sigma_{8,3}(\nu_d(\mathbb{P}^n)) \neq \kappa_{8,3}(\nu_d(\mathbb{P}^n))$ [cite: 13].

To explicitly identify points that lie in the cactus variety but *not* the secant variety, researchers look for polynomials divisible by a high power of a linear form (e.g., a $(d-3)$-rd power). Advanced algorithms have been developed to distinguish points in $\kappa_{14}$ from those in $\sigma_{14}$ using border apolarity [cite: 13].

## 7. Apolarity, Identifiability, and Applications

The generalized secant theory is not merely an abstract geometric pursuit; it has direct operational consequences in determining when tensor decompositions are unique, a property known as **identifiability** [cite: 5, 34].

### 7.1 The Apolarity Lemma
The Apolarity Lemma is the fundamental algebraic bridge connecting the geometry of secant and cactus varieties to the algebra of polynomial ideals [cite: 9, 13, 30]. It states that a homogeneous polynomial $F \in \text{Sym}^d V^*$ can be written as a sum of powers of linear forms $L_1^d + \dots + L_r^d$ if and only if the ideal of the scheme of points $\{[L_1], \dots, [L_r]\} \subset \mathbb{P}V$ is contained in the apolar ideal $\text{Ann}(F)$ [cite: 4]. 

In the multigraded setting (for Segre and Segre-Veronese varieties), border apolarity and "border cactus decompositions" use multi-homogeneous ideals in the Cox ring of the toric variety to witness membership in specific cactus varieties [cite: 4, 30, 32]. The extension of apolarity to linear subspaces corresponds exactly to the simultaneous Waring decomposition represented by Grassmann secant varieties [cite: 4].

### 7.2 Generic Identifiability
A tensor rank decomposition is identifiable if it is unique up to the trivial permutation and scaling of the rank-1 factors. In practical applications (like blind source separation in signal processing, where the rank-1 components represent independent physical signals), identifiability is paramount [cite: 3, 34].

A criterion for identifiability is considered "effective" if it is satisfied on a dense, open subset of the algebraic set enclosing the rank-$r$ tensors [cite: 34]. Knowing that a variety is non-defective (has the expected dimension) is a prerequisite for generic identifiability [cite: 5, 35]. 
If a secant variety $\sigma_r(X)$ has the expected dimension, then for a generic tensor of sub-typical rank $r$, the number of decompositions is finite. If further numerical bounds are satisfied, the decomposition is absolutely unique (1-identifiable) [cite: 23, 34]. 

Kruskal's criterion is one of the most famous identifiability conditions, and its effectiveness is bounded deeply by the underlying secant dimensions [cite: 34]. Recent results using Grassmann secant varieties and Segre-Veronese defectivity thresholds have beaten several classical bounds on tensor identifiability [cite: 23].

### 7.3 Connections to Mathematical Physics and Quantum Information
Beyond signal processing, subspace rank and the decompositions parameterized by generalized secant varieties have deep ties to quantum mechanics. 
1.  **Quantum Entanglement:** An elementary tensor represents a separable (unentangled) state in a multipartite quantum system. The tensor rank measures the cost of generating an entangled state using operations and classical communication (LOCC). Secant varieties of Segre products directly stratify quantum states by their entanglement border rank [cite: 36].
2.  **Quantum Analogues:** While the prompt queries regarding an "AH analogue", in mathematical physics "AH analogue" frequently refers to Acoustic Horizons or analogue Hawking radiation in fluid acoustics [cite: 36]. In the context of secant theory, however, the AH analogue is strictly the Alexander-Hirschowitz generalized non-defectivity mapping [cite: 1, 14]. Both utilize highly advanced tensor network models to simulate microscopic Hamiltonians, reflecting the dual utility of tensors in pure geometry and applied quantum sensing [cite: 36].

## 8. Matrix Pencils and the Grigoriev-Ja'Ja'-Teichert Theorem

To see subspace rank in action, one looks to the work of Buczynski and Landsberg (2013) on partially symmetric tensors in $\mathbb{C}^2 \otimes \mathbb{C}^b \otimes \mathbb{C}^c$ [cite: 2]. A tensor in this space can be viewed as a 2-dimensional vector space (a pencil) of $b \times c$ matrices. 

By applying Kronecker's canonical normal form for pencils of matrices, Buczynski and Landsberg systematically mapped out the generic ranks and maximal ranks in these spaces. 
Kronecker's classification partitions any matrix pencil into a direct sum of specific block types:
*   Right/Left singular blocks
*   Jordan blocks for finite eigenvalues
*   Jordan blocks for the infinite eigenvalue

Using subspace rank and the exact geometry of $\sigma_{r,2}(\text{Seg}(\mathbb{P}^{b-1} \times \mathbb{P}^{c-1}))$, they provided a rigorous proof and symmetric generalization of the Grigoriev-Ja'Ja'-Teichert theorem on the ranks of matrix pencils [cite: 2]. This stands as one of the clearest testaments to the power of Grassmann secant theory: by translating a tensor rank problem into a subspace rank problem, classical algebraic tools (like Kronecker forms) can be forcefully applied to yield exact rank bounds [cite: 2].

## 9. Conclusion and Open Directions

The quest for a universal analogue to the Alexander-Hirschowitz theorem for generalized secant geometries is one of the most vibrant areas of algebraic geometry. 

**Summary of Progress:**
*   **Veronese Varieties:** Completely solved by the original Alexander-Hirschowitz theorem [cite: 5, 12].
*   **Grassmann Secant Varieties:** Through the Dionisi-Fontanari theorem, reduced to the study of Segre-Veronese defectivity [cite: 16]. Defective cases heavily mapped, particularly for $\sigma_{r,k}(\nu_d(\mathbb{P}^n))$ linked to simultaneous Waring rank [cite: 18].
*   **Segre-Veronese Varieties:** Solved for all multidegrees where every $d_i \ge 3$ (they are never defective). The remaining defective cases are confined to linear and quadratic multidegrees, though a complete and proven classification list remains elusive [cite: 21, 28].
*   **Cactus Varieties:** The structural divergence between cactus varieties and secant varieties is now understood to initiate at $r=8$ due to the non-smoothable components of the Hilbert scheme of points [cite: 13].

**Future Trajectories:**
1.  **Completing the Segre-Veronese List:** Formally proving that the currently known conjectural list of defective Segre-Veronese varieties is complete, effectively finalizing the exact AH analogue for partially symmetric tensors [cite: 10, 21].
2.  **Equations of Secant Varieties:** Finding the actual polynomial defining equations for $\sigma_r(X)$ (e.g., via flattenings and catalecticant matrices) remains difficult due to the "cactus barrier." Finding explicit ideal generators for secants of Segre products (like the Salmon conjecture) is a massive ongoing effort [cite: 1].
3.  **Algorithmic and Complexity bounds:** Utilizing Grassmann secant defectivity to improve computational bounds for simultaneous Waring decompositions, pushing the limits of Fast Matrix Multiplication algorithms and addressing $\text{P}$ vs $\text{NP}$ via Geometric Complexity Theory [cite: 1].

The interplay between subspace rank, secant defectivity, and multi-graded apolarity continues to demonstrate that decomposing complex spaces into simple components is as geometrically rich as it is analytically complex. The eventual completion of the generalized AH theorem will mark a monumental unified theory of tensor geometry.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQER78NN2G7OXDehWrpo-yRsPqAxvAl9AI84kVr8qaR5jwm-q_0519-ajl2d0zHZuvA0-trjJmSxzktfov-VofgNIpUf8TczgN-kqTP39xNYh0ooSdcmzg==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERKuERBfqnx93enkstkmBtwLMSEnllJGyyRrMVt77Ps-kngt5MErs8YrRo_FIcvvMaeUVvF3g7whqzLk47GoBERjVs31Vf7RgCvXMHKGzSABSy90_L)
3. [unibo.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtzgoGzyc4c3aH1Xw6ye4IJlLYZMIZQ-uzmS_6_xOf4obWQ0kme63E1Pw-1ZUO8Z2h-b2UpOJV2zBosUebIZNk9HWOJkTXmdZ0eOSIFkPPZ0oqxnfw2KDZMkT4rl3pnj0k7lk=)
4. [mimuw.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6feyMAaSg7fh9YmQK3G-JtpTFhWuv1rbtPdEn5W0QhqtYzZJdRQoeN5ZfyiLhw4CSMnS4_SEfFhtgf7k18Hu24Fa1Y1jvRhTOSLbaNLd5Jq0dgJUQ7SPorZ5gyPiVWbhmzGsb27Lmf6lijsIO)
5. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhaz-guQ9T3yj3cUmKwOvLxkdGXzwqpH7BOygRuPLg1-PM_tsAuqIL1ySNBdrOXgqjtlifOLqAWpqxFDcFU33xTPOni8x1LuzM0Hr7VtM9pHJmhXiEpboGXoF-RZ4=)
6. [mdpi-res.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEygh_ZMyhsO7yCE3UhHZ6HHYy8E1HQZkVcKlOeBsuXOMD-BP0snUWW_Su70m7dLL0005ItG_LzApmyVU5hUMTVunKyqqNF4elemCT5yF39UOvl7UF36HqV3Tf8TZ95fKVkUBzcu9fkWMONMML--ccuDCQZo4ehOtbkRW7_tk5Mz_jewYfViur3xQ0=)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEt_zt2VU96OH---qWxnF4vkq8AZrfKZFDvAjbOc-hzSP8iPNhEkhtfVXbHptFPKHFM0L5xMKlLclfIQtO-lWYEH8YAJNfgw_hcZQ0_g2Co5ZDQdz9Y7FDNyKDUIKzAP82BUVWOin4kJ3gVT_o3lbmVgalrgRJHmQypvKqGkasLDStfDruXliloubvj0g==)
8. [mimuw.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3EWxqGr8V0o58DfhovtxTmogO1_IHa0-5RY0JSxEkUaUo6ZD-lYHmR0dkSbMi27C4DEdSJP6MdnVECoZNjQ9l3ZlelqVLyaMBNLzMq2MSgLaDA5XsAm-zGVQAy3aDa4PTXXYDnKbpTA0zr-IlYYOK53yWMgk-g3EPzpyv4Q==)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHL9K-muXE16bA9EfHYFx4EBfLVYQ2ePm0CE1Y_9s6yHQBwUl0oj6ohix4WpDo8OJcBy_l-Ta3_R-y50eC65V3jMxconuw_i6DQAYZwF-5ajuK_QFISGwC39wBPoflYTYBfLNuR80e2H2a3c0Jt)
10. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEljI2AXiqRGrxGTR8Qeqlix_Es2IjbA53KT6bGm5iBRqSEBA28DFzBCsgz1bZEVzeUPjSNBOo44tKXWcOr9GObdqWVNyX9_GKqc9oaeM4NN283bhyltmWG-VnXcY-bimTmY1SpmnXB2hgb-trlzeqqJPaF1xqnaZm5aFfFNhS7HPWKBla_Hqk5TLPagNeKnQ9wjcAZjarkDUofhEDgj5rNXhiusjylB-TATEJPuPU3unF52h-WZ2SQnk1OVT4kyJiIQdb5QFjl3XgpzHn7Z6PWhFH8WXY1JMM=)
11. [nd.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEssNKSJg00E4_JuQunspxyCNixENA-_3Zj30h1Uu-Adse_QP9JIwutMwFo8sBszGk04UySXMYIXVsavAQQzFexft3ZQO0f3NNbXRuhB7bgzIRgcw-fglilY6J5Y74AxuDv1JQbeaUVYSQgk8lQH-whKQOEFKZC8Eno)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFe68nBWMyRX0_pG-TuzKqJWOmGiAdCHIoTGy0h-BOQX1jYdwKD0o6N2PhA8UMIxKoPXz8V8dgYV-sAcOzxBoX_ocfQ5R1EHIdxo9cUOqEBCJYqyK8tmKRnaCXYhnGIXAFZyOOV3ltFHVjGwA-2N7KoLxxSP1EgyvWTbK1fTFSz2hQOqydx03TtKryH0mw6yq0KzatNA5RjNbAgx73o644quZIBJJs87fxDBzH-0J3zg==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvUlD4SRjX2Hdp1p8BaJySFlsHdBOACr0BrL1INRHzGMumIW6jzRNPrN3jZqYPS5YggxYwd5V29h3ETADn_BRG37-5ieF6Yy0yBIvUZjIeIuoi4zyRUw==)
14. [kuleuven.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9RvVKg2eccj9DR2dNyXt6Amjx_OcYa9iGLt2tbw2u6U5myXHlBZguyFb37np5uwl5Avx6J4fqrJUKIvm77QtskrShxQF7liY3cRtKwc85a6auhuXiRi9fv08dvYw3l4Q=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaHI2qNnb9BuJuu5ueK57ZQ2VOwENQ3UqKZoGOAYx7H0Prm7ACvcGzBKUOy9QfaM6eaCfE8F5BoWizgSEZH_flV-a_M1FMtWM2g5VnTi172y-iExtBesH4)
16. [unibo.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZUKYg2NaSaCBkYhiYJQul_DiwyxzykEY37erd2n7cN5IzUADOxsyMjHffskD4x0BaXhalTIKEvUtlp7-3g_xoLFRTRQr3f_LlK641cSX0NwI05TejIAjCJ6xVDvSREQ==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqZ6RJw9Vp8iDpuTJTdeClh2V_dmqsvrPZ9qMHimIIU0kvrMG9ZzVtllTBcu2clm2VrZu9nJFj69X7NlwD5A_PlC7foxPbwEGE0J0yz5nhAGI6KT8v)
18. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDlAbPWMhf0-CPTYxuXe7K0UZy8kK82u3qmMpmJ-S2D6oCPyLoakiqPTY20BSKyLcOBYY6y2YjtIte9IEsN7auaBDXxeU6zju0-5Ku8LlBD_Rieepm85DynhMhqSRUgBBbTaVf2jtFGh3cLOmiMLDi7pou9QtAmnj2fsBhjJzq3aiTpu1pIUyKoiDYW2toMv-tUs0hMsPG1ebXgwl4RkS8uEqlNsI9MqmXBIBE4R02jV_HpVgZBC6Q9gMCVUMijxJPtVcnVPHbbD-EvwLaXaSKwkw5WuVbpN4SDfwa)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFi-BkLOj80a25UVLSMF6ahLDRZ6_Fvz0R3pBRUnfIFjCv7OGMXCr1lrjsz3BOOzByOpFJGqlJ5_fnZXJ46z_A_JBwGjvGLNo0fIx054ZPLnZF6S10qXRq6fboBlzX9uUYa7fz5Loy7jpsx4k8IHCj-GhQdNoFeDjh7rbw-HaXjgZi5b-Tt39v1NCVXxo5dJL6v5cbypsc1aQ==)
20. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaM6hQfc_R7ye7fz55ZVtRz2AKb61oeIUmaPPS_VCR8QLOS_0u4vVyOpjbHXulUQWnK-6pzfnvAF01azY-jNCWdjN_39elMF26qCcqnVhEXP4hZAozEFR5BRF_gEG33N-OmmoasaGs2vgqMt4cim0OJYZNZZVp)
21. [unitn.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExvzx5mLBITK84vGBNb3tE3_tbN5XA4llmn6ldT2iUjLa02ArFdElZ6OFAjoe-L0qOQhU5EMRPzbzlxmo8MHHoPDSXeHXbJfL6m8UlqHKnGb2Pzi80ZlLA0z364e26U_wO88NQjzwNwcnnoqy1GMFJYoWuEkeJxuUmhiA4DSHIy9iEMCeJug==)
22. [puremath.no](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4S7qaOUJ-xnIu1-S9N7QLYPc3uPYX5L6L5X2udxNsLsCEU5dauF3YiRlvsbGF2oDzmQ_PqwB3of8v8bLOgKCP8wcnUQ1DdCFYUymgc6JXMoUiAKXzCYuDT0WeDSJ4rKBTcNzC6nzaf2PhADy6RJdraWzrp2zAUQyAVw==)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhOk9HzaxJVSK3-5DxWDfpaqvIDZcT5s8aAeTgX4gpCe4AMzEsHXtXhyQIw39bayCTQln1g4X0I__AO-9rGHMvF4JkujOpQyJjHE4A61a7609MwsI3VMQzU_EencrxY9gMRtTleSxqvfivwLRDKPMf_EEZcY7lSYXvhddc_8N3UlEPHgGftr4fwHb1RT1DYxjsIHuSZvAVBY9EvcaCiSu1kNsmLszjYJM3PPQAwhk=)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbuOc03xjNNVSndgYsZNc634Su2Og6HrIc3X4BJUeZu1z3CMel_iThEx4XgUbBbJ1CfZDVLw8o79Fvgn1JnPjW-HSETn5FhxhNV5PU0ObBvL0SWRZ5)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSMPKpA26OqHd7cJl5kYVTFIMGEOOBlBXu9cBtjBFEC8YZmuYHDIHdptEbehHxOrmnTZLZgxek7MZq7w64eYezUMnmyIAJBbNG9aU6373qIuKABnOu)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKWQnTcetUURMn-yjYlYvj9UTKE4mUmF8uIBowLYUjUC_eHWtzPbIJ6BTP3wyqOmsScnQ9VtyddHi2DnfVWvJCiEtpmn4FjwAziwBmkGD0Ew_3AwvIMQ==)
27. [polito.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETi5CgdG7m--5ztF00TRmpoA1IUhBAGiNA-m1pkr5_318gudgIShe2E8e_bE_WEx32EdDEbacUGohpHBJHL9uqbX6-yhSaCvppRH13OLEygQxKILefXxXaPF0DWovD0yZvUvFLyj2VZr3_dsS0zVY_6c-y)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFJyfXhbCtNlGdv0exPvABSGiXSd7Bx13VMGdsN_FkXVeAgCHEimjH7f1_Ky9eqQw1zLtOZOmLHbzabM-xiPJ-_-b0q7cb5W80hpAlcuZXHLKUo-2QWw==)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE42xSM8YJD6GmsfFeFCorI5PkfyEtyvbFqVRJ_ZF_wvmPVoD69j6P1YQy4Z9GUbrPJ6xBAeVUC-ZgACcVUZ36r3_XvIJjlTmM74XXkdf1U3kpjQ8CzQbJBuw==)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtAet6TGkupZarBqnPH6LVgnyMAFUU576e3ev2IZpW3iwUsvCb5xrNCyts62ZK1t9vB-GJTe_O0thej6cBPCa0l657pcwcbPOZDvwRTnIlFQUz0mpLH7WDtZEH3vhgKTIOf6csnRXv489-WW8gPaoqe7cyeGGlb-z78tgUSIfm-ulEkD0aiopUcIES47ylfcG0sDijD19PEi3g)
31. [uw.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9ESJHzXmNyOF6hsnPEdeaXNUtVkYnyA2Vaw10aoX4_Dx2KnG7toF_66oYIhBEFyIX1MI_LbJY1TiwWIVo3AGKBy_LKIHnXUiO_WwY_xjtfvH-EQRymdCQ6uyksMyKwVxo5DToTS2LCsEyDv59OWRD05M6znQlCITwP_mjdKw-6x0I2eTwdtwYFFQID_0=)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFewEyTd8zZA63DtEtWkmhjCAFOiRQeP0PV-niL7Zjt9G8qdzLjazPalmh_aN14px0KmVgykrJFysGrDiIqIx4kj6_B2N3hg2WMQ-WW5tq52QwpHFwL9gWjfQ==)
33. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYnGIAtruqm1BFp-B2Vq86zkujTKY4ZAmnTdGGlvfjyTNb5HGgIM14Ug2e6KvG7hpbByJjgZGZsBkr2j8jDeSzOzVVVQ2jxubXaASphHSznz0b1ju3KA==)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvQhCMUgqofKCjo5EtLlmtqrf2AVyrtrqTA8vCcz60JE8q3y4TCnG_2PiENmZv-0nNjbJplspO2DN6zlsBh6lqFu8UTbebiBrii6WqFyuT9bD7eLI5CQ==)
35. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuna4Goxd_Gae_iG4CtnKPCqdCYrhN6nxeIkvv0T7I5sXjRqKJlyjWP9YpuZt6nFlSg_DAxSAeZTb3YCm2MFxZldD7x5yje7K0u6jGqOA7kNnCBGJsVdZSRpVkF1ibuvS4Mv_-04Z7_fagwAac2bOugp2tkwiTCZfjkCR_MwoxDdOH9LqULZzLlo3WmqSjYXs43Rl5OUQTCZhyp4dOaiV_NglK6AFyzsHKmAH3MMjBAXr3kDtgMF5GxhPvPMulVZo4KCY3BAeRLme8H1m7Xboe6VwNA1iOj3Y=)
36. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExkGiyLPQh8NODvethZEByWewjp0wRwcIjLt5dV767GPXyFwEbKgwPYT_Ni0Ujh69SAQxr8QOrw1pCgDYlMbd_0M4NC0PTYievdSqcBq75EqtWa5h6-UhmplvTRQ==)

