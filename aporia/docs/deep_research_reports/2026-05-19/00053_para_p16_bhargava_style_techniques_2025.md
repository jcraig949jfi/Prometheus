# PARA-P16: Bhargava-style techniques 2025

**Pythia queue id:** 53
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdCa1FNYXZ2aURPU3MxTWtQcy1teW1BdxIXQmtRTWF2dmlET1NzMU1rUHMtbXltQXc
**Elapsed:** 252s
**Completed at:** 2026-05-19T11:09:54.830451+00:00

---

# Bhargava-Shankar-Style Arithmetic Statistics Techniques (2024-2026): Selmer-Group Distributions, Average Ranks, and Geometry-of-Numbers Extensions

**Key Points**
*   Research suggests that the foundational geometry-of-numbers techniques pioneered by Bhargava and Shankar have been successfully extended to arbitrary global fields, allowing for bounded average ranks of elliptic curves and hyperelliptic Jacobians over base fields beyond $\mathbb{Q}$.
*   The empirical discrepancy between observed computational data and established theoretical heuristics for 2-Selmer group distributions appears to be decisively explained by the newly proven existence of a secondary main term in their counting function.
*   Recent advances indicate that marrying Bhargava's geometry-of-numbers with dynamical point-counting methods enables the analysis of "thin families," such as unit-monogenized cubic fields, which exhibit notable deviations from the classical Cohen-Lenstra-Martinet heuristics.
*   It seems likely that weighted geometry of numbers and o-minimal geometry have resolved longstanding difficulties regarding the non-bijective relationship between reduced Weierstrass models and isomorphism classes, facilitating conditional bounds for average analytic ranks over general number fields.

**The Evolution of Arithmetic Statistics**
The mathematical landscape of arithmetic statistics has undergone a profound transformation. Historically centered on the asymptotic distributions of number fields and class groups over the rational numbers, the discipline has evolved to encompass complex geometric entities, including Selmer groups, Jacobian varieties, and rational points on weighted projective stacks. Between 2024 and 2026, researchers have vigorously extended the "Bhargavology" paradigm—the utilization of geometry-of-numbers on prehomogeneous and coregular vector spaces—into fundamentally new territories. 

**Reconciling Theory and Computation**
A persistent tension between massive computational databases and theoretical predictions has driven some of the most innovative recent work. While initial primary-term asymptotic limits successfully bounded average ranks and determined average Selmer group sizes, large-scale empirical data continuously demonstrated smaller-than-expected Selmer ranks. The theoretical resolution of this discrepancy through the derivation of precise secondary terms constitutes a watershed moment in the precise enumeration of arithmetic objects.

**Methodological Synergies**
The integration of disparate mathematical frameworks has been vital in the 2024-2026 period. By leveraging dynamical systems theory, o-minimal geometry, and Vinberg's theory of graded Lie algebras alongside classical arithmetic invariant theory, mathematicians have constructed generalized counting mechanisms. These advanced mechanisms allow for the parsing of "thin families," where imposing restrictive conditions—such as the existence of specific torsion points or unit-monogenized rings of integers—radically alters the anticipated statistical distributions.

***

## Introduction

The discipline of arithmetic statistics seeks to uncover the statistical behavior and asymptotic distributions of fundamental arithmetic objects—such as number fields, ideal class groups, and elliptic curves—when ordered by natural invariants like discriminants or heights. The resurgence and modernization of this field were catalyzed largely by Manjul Bhargava's groundbreaking geometric reformulations of Gauss composition and his subsequent geometry-of-numbers methods. When partnered with Arul Shankar, Bhargava's techniques successfully bounded the average sizes of the $n$-Selmer groups (for $n \in \{2,3,4,5\}$) of elliptic curves over $\mathbb{Q}$, leading to an unconditional bound of 0.885 for the average rank of rational elliptic curves [cite: 1, 2].

However, the period spanning 2024 to 2026 represents a major epoch of generalization and refinement in Bhargava-Shankar-style techniques. The limitations of the original methods—primarily their restriction to the base field $\mathbb{Q}$, their reliance on primary asymptotic main terms that lacked predictive power at finite computational scales, and their focus on "full" rather than "thin" families—have been systematically dismantled. 

This report provides an exhaustive, academically rigorous analysis of the 2024-2026 advancements in Bhargava-Shankar-style arithmetic statistics. It details the extension of geometry-of-numbers to arbitrary global fields via coregular representations, the extraction of secondary asymptotic terms to resolve computational discrepancies in Selmer-group distributions, the bounding of average analytic ranks via weighted o-minimal geometry, and the deep exploration of fundamentally new, restricted arithmetic families through the synthesis of dynamic point-counting and arithmetic invariant theory.

## Geometry-of-Numbers Extensions to Global Fields

One of the most persistent obstacles in arithmetic statistics has been the difficulty of translating theorems valid over the rational numbers $\mathbb{Q}$ to arbitrary number fields and global function fields. Over $\mathbb{Q}$, there is a straightforward bijection between certain integral orbits in representation spaces and the arithmetic objects they parameterize. Over general global fields, the presence of non-trivial class groups, unit groups, and the lack of a simple fundamental domain complicate the geometry of numbers drastically.

### Prehomogeneous Vector Spaces and Coregular Representations

Bhargava, Shankar, and Wang have spearheaded a multi-part generalization of geometry-of-numbers methods to arbitrary global fields $F$. Their methodology partitions the problem into representations of reductive groups on prehomogeneous vector spaces (Part I) and coregular representations (Part II, published in 2026) [cite: 3, 4].

A representation of a reductive group $G$ on a vector space $V$ is prehomogeneous if there exists a Zariski-open $G$-orbit over the algebraic closure. Prehomogeneous vector spaces are classically utilized to count fields of low degree (e.g., cubic, quartic, and quintic fields) by bounding their discriminants [cite: 3, 5]. In their 2026 work, Bhargava, Shankar, and Wang expanded this to **coregular representations**, which are characterized by the property that the ring of $G$-invariant polynomials on $V$ is freely generated [cite: 6]. This condition implies that the geometric quotient $V//G$ is isomorphic to an affine space.

By applying these methods to count orbits in coregular vector spaces having bounded invariants over any global field, the authors successfully bounded the average ranks and determined average Selmer group sizes of elliptic curves and Jacobians of hyperelliptic curves over any base global field $F$ of characteristic not 2, 3, or 5 [cite: 6, 7]. 

### The Height Function over Global Fields

To execute geometry-of-numbers arguments over a general global field $F$, a rigorous and functional height metric must be established. For a hyperelliptic curve $C$ or an elliptic curve defined by Weierstrass coefficients, Bhargava, Shankar, and Wang define the height of an orbit or arithmetic object using the product formula over infinite places.

For an elliptic curve with coefficients $A$ and $B$, the height is defined as:
\[ H(A, B) := (N I) \prod_{\mathfrak{p} \in M_\infty} \max(|A|_{\mathfrak{p}}^{1/4}, |B|_{\mathfrak{p}}^{1/6}) \]
where $M_\infty$ denotes the set of infinite places of $F$, and $I$ is an associated fractional ideal [cite: 7]. This height is well-defined precisely due to the product formula [cite: 7].

The authors demonstrate a Schanuel-type count of the number of elements in weighted projective spaces with bounded height [cite: 7, 8]. This highlights a crucial mathematical difference between parameterizing objects with multiple invariants (like the coefficients $A$ and $B$ of a Weierstrass equation) and objects with a unique invariant (like the discriminant of a number field extension) [cite: 7].

### The "Q-Method" and Mod $p^2$ Sieving

Further reinforcing the foundational geometry-of-numbers extensions is the development of what has been termed the "Q-method" by Bhargava, Shankar, and Wang, discussed prominently during the Simons Symposiums on Geometry of Arithmetic Statistics (2022-2024) [cite: 9]. 

The classical geometry-of-numbers relies heavily on sieving conditions modulo $p$ to restrict to objects with squarefree discriminants or specific maximal orders. However, these classical sieves sometimes fail to adequately capture conditions defined by higher prime powers. The Q-method improves mod $p$ sieves into ones that operate modulo $p^2$ through suitable high-dimensional embeddings [cite: 9]. This technique allows for a systematic approach to counting in unwieldy and "thin" shapes, providing vital analytic leverage for proving asymptotics over thin families and lending additional evidence toward the Cohen-Lenstra-Martinet heuristics [cite: 9].

## Average Ranks and Selmer Groups over Arbitrary Global Fields

The most notable application of the coregular representation extension is the bounding of average ranks of elliptic curves and the Jacobians of hyperelliptic curves over fields beyond $\mathbb{Q}$.

### Bounding the Average Rank of Elliptic Curves

For the family of elliptic curves over a global field $F$, ordered by height, Bhargava, Shankar, and Wang (2026) obtained stringent new bounds. While the bound over $\mathbb{Q}$ is famously 0.885 unconditionally [cite: 1, 10], for an arbitrary global field $F$ (which is a number field or a function field of characteristic not dividing 30), they proved a significantly improved uniform upper bound [cite: 7].

Specifically, they proved that the average size of the 2-Selmer group over global fields is finite, which implies the boundedness of the average rank. For function fields $\mathbb{F}_q(t)$, early work by de Jong demonstrated a bound of $4/3 + o_q(1)$, and Ho-Le Hung-Ngo proved $3/2 + o_q(1)$ [cite: 7]. However, the coregular representations approach provides a generalized framework that natively captures these behaviors across all field characteristics not equal to 2, 3, or 5 [cite: 6, 11].

### Average Ranks of Hyperelliptic Jacobians

For hyperelliptic curves, the results are equally profound. A monic hyperelliptic curve $C$ of degree $m$ over $F$ has an associated Jacobian $J$. The $m$-Selmer group $\text{Sel}_m(A)$ of an abelian variety $A$ over $F$ contains a subgroup isomorphic to $A(F) / m A(F)$, meaning bounds on the average size of the Selmer group directly bound the average rank of the abelian variety [cite: 7].

**Theorem (Bhargava, Shankar, Wang 2026):** Fix a positive integer $m$ and a global field $F$ of characteristic not 2. When all monic hyperelliptic curves over $F$ of degree $m$, up to equivalence, are ordered by height, the average size of the 2-Selmer groups of their Jacobians is bounded above by:
*   **3** if $m$ is odd.
*   **6** if $m$ is even.
[cite: 7].

Consequently, the average rank of their Jacobians is bounded above by $3/2$ if $m$ is odd, and $5/2$ if $m$ is even [cite: 7]. 

Furthermore, applying these techniques to the problem of rational points, the authors proved that the proportion of locally soluble hyperelliptic curves over $F$ which possess no rational points over $F$ approaches 100% as the dimension $n$ goes to infinity [cite: 7]. This result represents a sweeping generalization of the analogous $\mathbb{Q}$-specific theorem proved earlier by Bhargava [cite: 11, 12].

### Average Analytic Ranks via Weighted O-Minimal Geometry

In parallel to algebraic rank limits derived from Selmer groups, the period of 2024-2026 saw major leaps in bounding **average analytic ranks** of elliptic curves over number fields, primarily through the work of Tristan Phillips. 

The analytic rank of an elliptic curve is defined as the order of vanishing of its associated $L$-function at the central point $s = 1$. The Birch and Swinnerton-Dyer (BSD) conjecture postulates that the algebraic rank equals the analytic rank. Over $\mathbb{Q}$, Brumer originally bounded the average analytic rank at 2.3 (assuming the Generalized Riemann Hypothesis for elliptic $L$-functions), which was subsequently improved by Heath-Brown to 2, and by Young to $25/14 \approx 1.8$ [cite: 1, 13].

Phillips (2025) extended these conditional bounds to arbitrary number fields, navigating a fundamental barrier: over fields other than $\mathbb{Q}$ and a finite set of imaginary quadratic fields (specifically $\mathbb{Q}(\sqrt{-d})$ for $d \in \{2, 7, 11, 19, 43, 67, 163\}$), there is no longer a direct bijection between reduced short Weierstrass models and isomorphism classes of elliptic curves [cite: 14]. 

To overcome this, Phillips exploited the geometry of the moduli stack of elliptic curves and developed a framework for **weighted geometry of numbers over number fields** [cite: 1, 14]. By relying on o-minimal geometry—specifically applying a lattice counting theorem of Barroero and Widmer to weighted homogeneous spaces—Phillips established tight estimates for the number of lattice points in definable sets [cite: 8]. 

A central construction is the weighted projective stack $\mathcal{P}(w) = [(\mathbb{A}^{n+1} \setminus \{0\}) / \mathbb{G}_m]$, defined with respect to the weighted action:
\[ \lambda *_{w} (x_0, \dots, x_n) := (\lambda^{w_0} x_0, \dots, \lambda^{w_n} x_n) \]
[cite: 8, 15]. The algebraic stack $\mathcal{P}(w)$ is smooth and proper, allowing for the precise counting of $K$-rational points of bounded height with prescribed local conditions and an error term that features power savings independent of the local conditions [cite: 14, 15].

**Theorem (Phillips 2025):** Let $K$ be a number field of degree $d$. Assume that all elliptic curves over $K$ are modular and that their $L$-functions satisfy the Generalized Riemann Hypothesis (GRH). Then, the average analytic rank of isomorphism classes of elliptic curves over $K$, when ordered by naive height, is bounded above by:
\[ \frac{9d + 1}{2} \]
[cite: 1, 14].

This theorem constitutes the first known bound on the average rank of isomorphism classes of elliptic curves over arbitrary number fields, and the first bound for average analytic ranks of elliptic curves over number fields other than $\mathbb{Q}$ [cite: 13, 14].

#### Data Summary: Bounds on Ranks of Elliptic Curves and Jacobians

| Context / Base Field | Object Class | Methodology | Average Rank Bound | Average Selmer Size | Source Year / Author |
| :--- | :--- | :--- | :--- | :--- | :--- |
| $\mathbb{Q}$ | Elliptic Curves | Coregular Orbit Parametrization | $\le 0.885$ (Unconditional) | $|Sel_n|$: $2,3,4,5$ bound known | 2013/2015 (Bhargava, Shankar) [cite: 1, 10] |
| Number Field $K$ (Degree $d$) | Elliptic Curves (Isomorphism Classes) | Weighted O-Minimal Geometry, $L$-Functions | $\le (9d+1)/2$ (Analytic, assumes Modularity + GRH) | N/A | 2025 (Phillips) [cite: 1, 14] |
| Global Field $F$ (char $\neq 2,3,5$) | Jacobians of Monic Hyperelliptic Curves (Degree $m$ odd) | Coregular Representations | $\le 3/2$ (Algebraic) | $|Sel_2| \le 3$ | 2026 (Bhargava, Shankar, Wang) [cite: 7] |
| Global Field $F$ (char $\neq 2,3,5$) | Jacobians of Monic Hyperelliptic Curves (Degree $m$ even) | Coregular Representations | $\le 5/2$ (Algebraic) | $|Sel_2| \le 6$ | 2026 (Bhargava, Shankar, Wang) [cite: 7] |
| Function Field $\mathbb{F}_q(t)$ | Elliptic Curves | Moduli Stacks over Finite Fields | $3/2 + o_q(1)$ | N/A | 2026 (Ho-Le Hung-Ngo review) [cite: 7, 9] |

## Secondary Terms in Selmer-Group Distributions

While the derivation of primary asymptotic terms provided revolutionary global limits on average ranks, it inadvertently sparked a profound mystery when subjected to computational verification. This discrepancy between the mathematical limits and empirical datasets led to one of the most critical theoretical developments of the 2024-2026 timeline: the discovery and rigorous formulation of secondary main terms in the first moment of Selmer groups.

### The Empirical Tension: Data vs. Conjecture

The Bhargava-Shankar theorem states that when elliptic curves over $\mathbb{Q}$ are ordered by naive height, the average size of the 2-Selmer group is exactly 3 [cite: 16, 17]. The Katz-Sarnak and Goldfeld conjectures predict that the average rank of elliptic curves is 0.5 (with 50% having rank 0 and 50% having rank 1) [cite: 2, 18]. 

However, immense computational efforts led by researchers including Balakrishnan, Ho, Kaplan, Spicer, Stein, and Weigandt, who analyzed the arithmetic invariants of elliptic curves compiled by height, revealed a startling paradox: the empirical data showed a persistently smaller average size of the 2-Selmer group than the theoretical limit of 3 [cite: 16, 17]. Concurrently, the average rank appeared numerically *larger* in the data than the predicted 0.5 (often peaking near 0.98 before slowly declining) [cite: 2, 18]. This tension indicated that the primary asymptotic term alone was fundamentally insufficient to model the distributions at computationally accessible heights.

### The Shankar-Taniguchi Theorem

The resolution to this paradox was delivered in a collaborative tour-de-force by Arul Shankar and Takashi Taniguchi (2024-2025). They postulated and proved the existence of a **secondary main term** in the counting function of the 2-Selmer groups of elliptic curves [cite: 16, 17]. 

To formalize this, let $X$ represent the height bound for a family of elliptic curves $E \in \mathcal{E}$. The primary main term for the counting function of the 2-Selmer group elements of curves bounded by $X$ was established by Bhargava and Shankar to be of order $X^{5/6}$ with an error term of $o(X^{5/6})$ [cite: 18, 19]. 

Shankar and Taniguchi developed a sophisticated "slicing technique" to isolate the next order of magnitude in the asymptotic expansion. 

**Theorem (Shankar-Taniguchi 2024/2025):** The counting function of $|\text{Sel}_2(E)|$, for elliptic curves $E$ having height bounded by $X$, possesses a secondary term of order $X^{3/4}$, alongside a power-saving error term. Specifically, the counting function takes the form:
\[ \text{Primary}(X^{5/6}) + C^\pm X^{3/4} + O_\epsilon(X^{3/4 - \alpha + \epsilon}) \]
where $C^\pm$ are explicit constants, and $\alpha > 0$ is a power-saving factor (specifically, $\alpha$ can be taken to be $1/3804$) [cite: 18, 19]. 

This represents the first improvement over the original $o(X^{5/6})$ error term [cite: 18, 19]. The existence of a negative secondary term mathematically justifies why the empirical averages of the 2-Selmer size remain systematically depressed at low and moderate heights: the $X^{3/4}$ term acts as a drag on the primary $X^{5/6}$ term until $X$ reaches astronomically large values [cite: 16].

The constants $C^\pm$ in the Shankar-Taniguchi theorem are expressed as the limits of the values at $s=1/2$ of certain Dirichlet series, which converge absolutely only to the right of $\text{Re}(s) = 1$ [cite: 18]. To prove this, the authors utilized a slicing method on the space of binary quartic forms, adapting a technique originally used by Bhargava, Shankar, and Tsimerman to obtain secondary terms for the number of $\text{GL}_2(\mathbb{Z})$-orbits on integral binary cubic forms [cite: 18]. By constructing periodic approximations to the relevant local functions and acquiring sharp density estimates, they definitively verified the convergence of the sum dictating the secondary term [cite: 20].

### Geometric Secondary Terms in Function Fields

Parallel to the work over $\mathbb{Q}$, research into secondary terms expanded into global function fields. Michael Kural's 2025 doctoral dissertation at Harvard analyzed the geometry of secondary terms in arithmetic statistics over $\mathbb{F}_q(t)$ [cite: 21]. 

Kural proved the existence of a secondary term for the count of cubic extensions of the function field $\mathbb{F}_q(t)$ with fixed absolute norm of discriminant. While Davenport and Heilbronn originally established the primary asymptotic for cubic fields over $\mathbb{Q}$ [cite: 21, 22], identifying secondary structures requires deep geometric insight. 

Kural's work established that the number of cubic extensions with absolute norm of discriminant equal to $q^{2N}$ is given by:
\[ c_1 q^{2N} - c_{i,2} q^{5N/3} + O_\epsilon(q^{(3/2+\epsilon)N}) \]
where $c_1$ and $c_{i,2}$ are explicit constants, and $c_{i,2}$ is periodic, depending only on $N \pmod 3$ [cite: 21]. 

This was achieved by utilizing the geometric parameterizations of Miranda and Casnati-Ekedahl, viewed as a geometric enhancement of the classical Davenport-Heilbronn binary cubic forms [cite: 21]. By sieving for smooth curves embedded in Hirzebruch surfaces, Kural managed to bypass topological homology methods (which suggest "secondary stability" in Hurwitz spaces) with a direct, rigorous algebraic geometry framework [cite: 21].

## New Families Analyzed: Thin Families and Symmetric Varieties

Until recently, Bhargavology was largely applied to "full" families—such as all cubic fields, or all elliptic curves. However, major efforts in 2024-2026 have shifted toward **thin families**, where the imposition of specific arithmetic or geometric conditions profoundly alters the foundational statistics.

### Dynamical Point-Counting on Symmetric Varieties

The mechanism for evaluating thin families was constructed by Arul Shankar, Artane Siad, and Ashvin A. Swaminathan (2025-2026), who published highly influential work on counting integral points on symmetric varieties [cite: 23, 24]. 

A critical limitation of earlier geometry-of-numbers methods was the difficulty of counting points within fundamental domains when the target orbits resided on restrictive symmetric varieties rather than full representation spaces. To bypass this, Shankar, Siad, and Swaminathan successfully combined Bhargava's geometry-of-numbers methods with the dynamical point-counting methods of Eskin-McMullen and Benoist-Oh [cite: 23, 24].

The dynamical approach of Eskin and McMullen leverages ergodic theory and the mixing properties of group actions on homogeneous spaces to count lattice points. By synthesizing this with Bhargava's fundamental domains for coregular representations, the authors produced a powerful hybrid technique tailored for counting integral points on symmetric varieties lying within these fundamental domains [cite: 23, 25]. 

### Deviations from the Cohen-Lenstra Heuristics

The most striking application of this new dynamical-geometric method is the analysis of the 2-torsion subgroup of class groups in thin families of cubic number fields [cite: 23, 24]. The Cohen-Lenstra-Martinet heuristics represent the gold standard for predicting the statistical behavior of class groups, typically asserting that the probability of a specific class group structure occurring is inversely proportional to the size of its automorphism group [cite: 24, 26].

However, when investigating the subset of **unit-monogenized cubic fields**—fields whose ring of integers is generated by a single unit element—Shankar, Siad, and Swaminathan discovered significant deviations from the Cohen-Lenstra predictions [cite: 24, 27]. 

Their results demonstrate that when considered as a "random variable" valued in finite abelian 2-groups, the distribution of the 2-primary parts of the class groups over the thin family of monogenized degree-$n$ fields differs substantively from the distribution predicted for the full family of degree-$n$ fields [cite: 24, 27]. Specifically, their results mathematically suggest that the existence of a generator of the ring of integers with a small norm has an actively increasing effect on the average size of the 2-torsion subgroup of the class group [cite: 23, 25].

### Thin Families of Elliptic Curves

The Shankar-Siad-Swaminathan dynamical counting technique was simultaneously applied to the distribution of 2-Selmer groups in thin families of elliptic curves over $\mathbb{Q}$ [cite: 23]. While the full family of elliptic curves yields an average 2-Selmer group size of 3, imposing the condition of specific marked points, torsion subgroups, or isogenies structurally shifts the lattice counting space to a symmetric subvariety. 

This builds off previous observations by Bhargava and Ho, who determined that the average size of the 2-Selmer group in the family of elliptic curves with a marked point is 6 [cite: 28]. Using the newly developed dynamic point-counting techniques, a vast array of highly specific thin families can now be rigorously parameterized and analyzed for their precise Selmer distribution [cite: 23, 24].

## Self-Dual Isogenies and Vinberg Theory

The traditional approach to measuring average ranks involves analyzing Selmer groups associated with multiplication-by-$n$ isogenies (i.e., the $n$-Selmer group). Between 2024 and 2026, researchers like Jef Laga successfully extended Bhargavology to Selmer groups of isogenies that are *not* standard multiplication-by-$n$ maps [cite: 29].

### Vinberg Representations and Graded Lie Algebras

Laga's work is predicated on the insight that many representations used in arithmetic statistics arise from Vinberg theory, which concerns the study of graded Lie algebras [cite: 29]. Earlier literature by Thorne had already connected Vinberg representations of $\mathbb{Z}/2\mathbb{Z}$-gradings of simply laced Lie algebras (types $A_n, D_n, E_n$) to families of curves that arise as deformations of simple surface singularities [cite: 29].

Laga advanced this significantly by utilizing a novel orbit parameterization associated with the non-simply laced **Dynkin diagram of type $B_{2n}$** [cite: 29]. The specific representation $(G, V)$ evaluated is the Vinberg representation tied to the stable 2-grading of the root system of type $B_{2n}$ [cite: 29]. 

By exploiting this Lie theoretic structure, Laga determined an upper bound for the average size of the Selmer groups associated with certain **self-dual isogenies** related to the Jacobians of hyperelliptic curves [cite: 29]. 

If one considers an isogeny $\phi: J_b \to A_b$ and its dual $\psi: A_b \to J_b$, such that the composition $\psi \circ \phi$ acts as multiplication-by-2, Laga parameterizes the elements of these specific Selmer groups via integral orbits of the reductive group $G$ acting on $V$ [cite: 29]. The stabilizer structure $\text{Stab}_G(v)$ is demonstrated to be isomorphic to the kernel of the norm map $\text{Res}_{L_2/K} \mu_2 \to \mu_2$, fundamentally tying the arithmetic of the isogeny to the algebraic invariants of the Vinberg orbit [cite: 29].

This connection bridges the gap between arithmetic statistics and higher-order Lie theory, demonstrating that nearly all geometric parameterizations required to bound Selmer groups can be unified under the umbrella of graded Lie algebras [cite: 29].

## Unbounded Average Selmer Ranks in Torsion Families

While much of the 2024-2026 research successfully bounded average ranks and Selmer sizes, an equally vital branch of research identified specific geometric constraints under which the average Selmer size is provably unbounded.

Tristan Phillips (2025) provided rigorous asymptotic lower bounds for the average size of the $p$-Selmer group of elliptic curves over a number field, specifically for curves possessing a torsion subgroup isomorphic to $\mathbb{Z}/M\mathbb{Z} \oplus \mathbb{Z}/MN\mathbb{Z}$ [cite: 30, 31]. 

For modular curves $X_1(M, MN)$ having genus 0, and allowing $p$ to be a prime divisor of $MN$, Phillips analyzed the family of elliptic curves maintaining this prescribed torsion structure. By combining weighted geometry of numbers with an exhaustive tally of local conditions, he demonstrated that in many such cases, the average size of the $p$-Selmer group is **unbounded** [cite: 30, 31].

This unboundedness implies a geometric phenomenon where the imposition of specific rigid torsion structures forces an artificial inflation of the $p$-Selmer rank [cite: 30]. The existence of rational $p$-torsion drastically alters the cohomological structure of the Selmer group, rendering the standard Cohen-Lenstra stabilizing heuristics moot and driving the average size to infinity as the height bounds increase [cite: 28, 30]. This serves as a stark counter-example to the general boundedness of Selmer ranks in "full" families and provides an essential boundary condition for the formulation of future distribution conjectures.

## Conclusion

The period between 2024 and 2026 marks a structural maturation of Bhargava-Shankar-style arithmetic statistics. The original paradigm—while revolutionary for rational elliptic curves and simple field extensions—has been aggressively transformed into a universal algebraic toolkit. 

The extension of coregular representations to arbitrary global fields has emancipated arithmetic statistics from the confines of $\mathbb{Q}$, yielding uniform bounds on the ranks of hyperelliptic Jacobians [cite: 6, 7]. Tristan Phillips' innovations in o-minimal geometry and weighted projective stacks have simultaneously resolved the complexities of counting isomorphism classes, delivering rigorous conditional limits on analytic ranks over general number fields [cite: 1, 14]. 

Perhaps most crucially, the synthesis of arithmetic statistics with disparate branches of mathematics has solved outstanding empirical paradoxes. The integration of the "slicing technique" by Shankar and Taniguchi yielded the secondary main terms necessary to explain the Balakrishnan computational Selmer anomalies [cite: 17, 18], while the application of Eskin-McMullen dynamical counting enabled Shankar, Siad, and Swaminathan to unveil the idiosyncratic behaviors of thin families and symmetric varieties [cite: 23, 24]. Finally, the deeper exploration of Vinberg theory and Dynkin diagrams has proven that the parameterization of Selmer elements is deeply intertwined with the fundamental symmetries of Lie algebras [cite: 29].

Ultimately, the arithmetic statistics of 2026 is defined by its precision. By capturing secondary terms, exploring thin sub-families, and deploying geometry-of-numbers across arbitrary global fields, researchers have transitioned from proving that fundamental arithmetic structures are simply bounded, to detailing the exact geometric and algebraic constraints that govern their distribution across the mathematical universe.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGo-qMCnekTa1t6oUWlHfpmLz5cE62o4uQ_dfqYLmABcM4A8YBC4RG17hkD63Du_e-kEiwJzxYRutAL4pDH2BRIX91Niy8iP8l3HGH4f319gzoKTfTVvRry)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7oFr1HbZR7IlOJLpO-k9FV3JSFLATMBGi41KWm4KgJg4ySxzDmA4OLxoRQ72ddXoIWM-YxXEcohf5fWmfCtY4l4TBHu1lpx7oITw6hS5-7CQ4hRRq7x-oOCzMoytLgDE0oLZiAhlIN16GhzBYIkwAdoO3FX0ntrSummkwb2nBMglbsPKLExb1zv22KNjGh45RdUlnjMyt2qTMNC6CqeOgVEhsp348A6Vel_M=)
3. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHu_sMqOkFmch81zcGBUDyykJM3RJK4PgKskPoCBfnNUl5A1osCN8dH1UE6oP6uTuFGBnxXZDbKU3D6ktefvoF9MhTI2qmuq_xlyC8tg0XBK2WX1Z4V3ixDz4bUxEuXg_GCCamoufoDmdmjp-qzZ7E=)
4. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtYaDWCiRI054NIqFm_OSKNdXaZTP2M-DypMzKxP8CUOHwCTBfRoZ8Wh_pmWRkimrEjSmC1bltXFA5qsiAZwIcXuDgkT6hw0ypjSNGeAsR_PoZczfyEa9jhmirRcHvKydQnF0pl_9y8Riq6vHlffx0vD3CJzRX1gbsL9PDh0lYInqrzX8g0pkMu3ku3X901_tAidt2OXFUSLyTxO0A4JAMuA09xny_3rth0AiNcIRjdJqsHxo0fjYcn0s4cOrK7ij0crzEBmInO5Ei)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGP02Xn2SY_dCD9cGm41tARzuLzBSc3dIq-4pymx12ZWTDoAIOWYUuUcS-7L7pgvOeIuEDIvEHpMJ0lxj-TAJglxj7HriCA5sPq0PYfmS0jq4aHPd8e)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-VVDJKXMQS9uT_NiJdMmXL-hrVJJCD1J2Hr7cQQI6NDMQrUNK8mHGW72lsw7GSnw86sswSULPqGzEHlddDDZJnorBamitIgTVuY_uuLukjrQSlCkU)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHa9KSGRxHQyyPbAnxwZZyxy3gqy6yKKNa4gd33Khp1qkCVAM048zZ5KhSwxjPikM8QABtVnO7VZe96fzXJmtoxiupJ0IMPDBceA0RNtPi2B336dmnx5IWp)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5sQP4clkx3giq9hii5_2OvwJaUWkd7Ssu4as_ygfv7R_S9Oy4MbzhnbxEj9omZ16JPkKBEs2zew_8wwd6LckUMwGuV_K9Z-FL83iDOLnB-RN5Ioml)
9. [simonsfoundation.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWCnzIo985-kRYTFPMi9LejgMG44jtnD2Ly9DJAmLDi-zbhfQdh5yFaSlFBsap26YJWIsT7VULkqYOOVkg4K3HrKg2-XSzk3hGegT9E8LoIf1_t0uGF7pTarTTyPLQb94sXTSYXmht5_ssHwnu1-xDoeerrEYRYlZicTKs8B98JLcuZg==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuhSif7oqNsVpd8OKw3jvlO0T6LzXIb45gmJ7mYfmJHljTh8t7_9v6-VeU1Z1mS_noszW3qbN34aVRkLBneX9c9MJtwnVGQAdhssEjkg0g-aQsA8SE)
11. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2cTdMazWYlwhOTd2m8Ba9fEzjy2q2SsYB7j_sQHj2pFm7vJdr7EucXa2hOuLNTwKFn_l68SerEG7XC9RogEPeYlRXVTY72dECow2jZOa0emyIiPK_NYSDNG9lJK_PMCUwwXHguJ6pVQ9UvjtKzK91)
12. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnUaPV7ZN1_OVFpAtjun1VfW-AuPERXnh-_rGOMrmICxYRtxS5z8AFBgpeZpMpnKsYKs9lA40Q2jnsSWsly6j9TfyZvY5kAeaOJucV75buX0xt4bleb-9vbS312OrqV1vtKpq6vw==)
13. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEiV8WVMqpxdLRnUlopDQhBQZdRkedoV16MB6Ld88Ha3Csh9jF0oXPiNlyv-SerLOP_15WRKpx-D7EcJF2xEtgzmKBFYjCaoel1file6dBS7VbN3tSLhjywpeoerbpRAwMxtjd4zce5cF84HYyLbTMHvzcS4VPawpTEquK9JlCrcr-1_eZGadnjJKrLQ1GkSwWmDmhICVuO87lbpuVXgb6r7kIrIL9e98fLqwrcsNa95tnHSETagKzLwP0D1bl_b9r7JSWm0s91yaulw3xKmVTGrYUz1t6Qqn22ynoN4XY2tUT4QQhKJMJQGJPfH8MdCMD_dmlzzg=)
14. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWXGrDV9RBtQsKqfne9-3rbxnQ3PMUuOzvspRfgoNYPnMy92D3zaiE-nOrG4XegI-t-F1rb894zM75QowIhzCES9JZZlfSr72VNnu7WckdbsbMirjy8pm3Xf4y8p2aA2KiuQgYi5s-xHawsz2P9HIhg-v239rjNcwtY-GDLVdtJ5qQpFRmguca2C-Z_6BUlpbYvOOeZglY6sZmlCU0wdNTa0GrwpMcdoQPdHcupKawnFm5C0LI-T_5sdcslN4aWdF6vbrhBBbLmTDwLVHH5tjUUZl7qwWH7b2Qy7lgzdg=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjDtwi4QSZ-xrlh7xIcxiZhBsRnTwykB2rbSjRphHP54Rkj8mjRuyRfKxJKDM6aLhMfsCrRCnEhUxWFpqtQdb8RSD8ezy0ygpl24FCkhak_CqpcZEi)
16. [simonsfoundation.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHymqGxj7OZGHoT7uKcrRL7RbWLb1dcAHGwGYZjeh4GHjfx5JRAs52EqG7k-Vlr8olkbaACvQlPEAj0RUfMk4EIUByRogOclSSc8crcSLaIfrJ-NijMLCEMZXZD3ozoP8ZhBTk5ic2_YhiUFNAVF-3v2uYXpn1rGVdossWhAGlEIZIibPbpqvUW6lcXyMsDWEkK9WoMVB1SByVMwF6cadNm-cxRs-YgbV1-v0TTZgt3GJzzdSGNtZofUXLF)
17. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBHZ26FmuaoeaOhgNxRdA8nCSXchC0-8SALq26o82hwgVn9HRvVeeYd5EHMocii9MoXBhO-C_btUTK-wx_Sl04TyiL32NGc7RDSRIOI56LgUxe5Zl0y6AwB34Y1aGp8KW8DdV8vx-lebQ_sSsNvcUlBuWb73ROHMhZlmAELYjmrKNChHpKZs7wFob4vAraZ2JSIQE1jikG_ZPZHSuXcK_FjJ6KOUDCA8jtnxfy)
18. [kobe-u.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHayPawOwxqinWAqRxszovFqhzIDeX-uXp7_oz00c9zT1qahPywzKuec2yDU_vXMYtkvPw9_eHwMGonp4ttCE4M6mn1SOpIHFeJHf-po19vPuv3eKWB5RMy1P0E7XUmf0Nun81nrEYyBMjz_g==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsnh7wOoSm5MC02MODrOzo2zXcXebUacBkUQJszMOp8se3gS_Kq-YWH0kWdy7OpO6Ce3EnOSPZ-LB7S5Ra7CuSZ2jfb69qN3sxEpbQo2cBJ7KEo29t)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEy4b41N-IeVz2yS-9XUqtmb9y6_FsGZvO5Zc9zKRghOja8a5DVshWpKA0ot7aeB3YTiRF14aLUTMzNFBnQmjIyEJBpOjXajDpWhTVDI0JjuvydQxbc)
21. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEY6JEbUIvBnNi2s6wGw-EjSIJGT2SiyHKFC9tQrV3SAyf8TOKCGHqow651kY8r8_nz3U_Dg5Vei6NFVfsHPXEJ4c28h_AO0jYfLOayq0zdXyby25gZoKbAz2b9PWf6nXbjT61bBxZoiT1oCwVNyashDr3k70muQ9tLoG036X3qRgEVqT-phQ==)
22. [toronto.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbXJcy6YEkgL7waxC-vqnP8rYdm7k7ypKvhN8R9QlaWNLqeT6j81RU1sqjrEI_fq5jAKrpLYMb9uAEc2JOLCwmwtrxUUA02D1ABN3Vu3yvS_nJ4f31tpADHzBwLhywPsvSW2qvabDlJM8=)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyE8VSrBNptwEyaGbM818xPyrM960qFrIfAgsjUluX3hZsJKnWbMsBO7pbSWl-qT2L0I2tgIGCEAKXAoyXOobzFACwiEMAaHMkXqZpgis6PbtazhSW)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLzE4zRw_F4DD9mjRo7ywEtG_jiawQG79zY5TX5wiptc0G0yVgAVbcphlgFLm5U_H_nk0w23QbbPlqYt-y7L09ZPj5RVIX35q7AVg-UGOqBIIONfTxn40Y)
25. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEB2O6ZQk9ectg3XUfV3i6pBirguxCgjLcPiuW0XdbzXqO13EYd0huojYXxPPVNbUg3o4g79IALlcS7P4gwKdBWYhz1XunHwscRzR19xtwG1tuD3DjgjjKfQw00yQN9I0e0pwJgXQBy1eedTdNtod-u9tPtp9cnM19nab1uw2cFBWkx-12soTPic8FbKm_o)
26. [bimsa.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPcmhQNDwW1NxbjQg9Ig78Xp2Ewxt0AuYeMmPEA3u2IF9lK_7RRqmtDrhAXSWtXJ8a_Si9QqN0vuVvGF2jHrdT4qEKkM0cHcwTvj9AAqYJGzRM2xZ2Obd0lmhebDJloQE_QZfNZoYCdvB263yKHx5l1o_C)
27. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNSHA5EqJuYtQPV6YRuVs5dGUbiGKZNmQTNLOBZAevSe7ms-xgPySCDI5JkquKX3haXQOCMf7AezU7V2LiCWCL1h28X_48D_pPxXHB8bywmVhIdsfxX_OFuPNfvrIS_68=)
28. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENELloPYLCozsjm5_0VIT1esGtMKGbmYwTtPnQ3PONoyNXKiidIoT7HnYTShlXaYtAzeu3hgE4OK02bi2CAhdZAemGCfgurD4mkPz_wGooAOnSW4COHklMSwVhyC4Vigm3uoXF7YURcryv_SCy1N9u4aR33QnC7aoU99SFSXwXYNMw1eDE9Z8HufNA3WpxlEwyco3qN9fdKRHegpWvcMX5Y-qW6lfYawh9SXSbbK4njQUDF32mlfuazr8iQkwIRTtO-E8=)
29. [cam.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdwnguurYpb6XqcblWbmGB96MtpsaLXeXFRs_UbJFN4YZx8qoc6wSunWvK5s69aGBsTUdc5jndUrwB6WSCKR4VS1pn_0MTgd-flobUZzJOLyIzpzAWecx617LNLVsW)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdQ7GEtlWzVMfOV6jIvKbISebnFRKrJtwzVG43JV_vUrsMSPCWL2q9iidLGqg2yyuNn35lOb8CjCz96CcXQpYIjx6eNiCBuekStz_FGcuL3ZcyaqaI)
31. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVLVO92TemBmrWgXJhooUZL977BaVmFwYrjHAXHDAUBNPFGbrw85enhZqL5H3fpF5F1DFcSoMaj2YdEx4aTb8Xf3CcIfwy3yuUaBsoUEMrEp08LuKRRJeA0fiez2-B5Ccglalh5vijDABHSwp_tg5_2OtnFQyCtG5gLKOXThGbvmNO8g==)

