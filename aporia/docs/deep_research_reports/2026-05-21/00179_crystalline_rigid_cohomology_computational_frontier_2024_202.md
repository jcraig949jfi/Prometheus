# Crystalline / rigid cohomology computational frontier 2024-2026 (Costa-Tuitman)

**Pythia queue id:** 179
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdLendQYXRqc0RzU3gxTWtQMDRlTnNBdxIXS3p3UGF0anNEc1N4MU1rUDA0ZU5zQXc
**Elapsed:** 312s
**Completed at:** 2026-05-21T17:14:12.488362+00:00

---

# Computational Frontiers in Crystalline and Rigid Cohomology: The Costa-Tuitman Paradigm and 2024-2026 Innovations

**Key Points:**
*   **Algorithmic Evolution:** The computational landscape for calculating zeta functions and point counting on algebraic curves over finite fields has shifted dramatically from theoretical bounds to highly optimized, practical algorithms, largely driven by the foundational work of Jan Tuitman on rigid cohomology and Edgar Costa on controlled reduction. 
*   **The 2024-2026 Breakthroughs:** Preprints from 2026 demonstrate the direct extension of the Costa-Tuitman paradigm. Jeremy Booher utilizes Tuitman’s algorithm to explicitly compute crystalline cohomology and Dieudonné modules for $p$-divisible groups. Simultaneously, Batubara et al. introduce GPU-optimized controlled reduction policies that outpace both Costa and Tuitman on specific quintic curves. 
*   **Diophantine Applications:** The integration of these computational cohomology techniques into the Quadratic Chabauty method by Balakrishnan, Dogra, Müller, Tuitman, and Vonk (the BDMTV collaboration) has successfully resolved longstanding questions in Mazur's Program B, calculating rational points on complex modular curves where classical methods fail.
*   **Uncertainty and Complexity:** While algorithms run in quasi-linear or average polynomial time, practical implementation for high-genus curves, primes of bad reduction, and high-dimensional varieties (like cubic fourfolds) remains computationally intensive. The community relies heavily on heuristic bounds and precision estimates that are still actively being rigorously formalized.

**Introduction to the Topic**
Arithmetic geometry frequently seeks to understand the solutions to polynomial equations over various number systems. When working over finite fields (systems with a finite number of elements, characterized by a prime number $p$), mathematicians count these solutions and package the data into a mathematical object called a "zeta function." The Weil conjectures, famously proven in the 20th century, dictate that these zeta functions are rational and encode deep topological properties of the underlying geometric shapes. However, actually calculating these functions for specific curves is an immensely difficult computational challenge.

To solve this, mathematicians use $p$-adic cohomology theories—specifically "rigid" and "crystalline" cohomology. These theories allow researchers to lift curves from a finite field into a characteristic zero environment (like the $p$-adic numbers), where tools from calculus and differential equations can be applied. Jan Tuitman developed a highly general algorithm using rigid cohomology to count points on curves, while Edgar Costa (often collaborating with David Harvey and Kiran Kedlaya) pioneered "controlled reduction" methods to make these computations vastly faster, achieving average polynomial time. In the most recent frontier (2024-2026), these tools have been pushed even further to solve Diophantine equations (finding rational points on curves) using the "Quadratic Chabauty" method, and to calculate intricate algebraic structures like $p$-divisible groups.

---

## Introduction to Computational Arithmetic Geometry

The computation of zeta functions and $L$-functions for algebraic varieties over finite fields represents one of the most vibrant areas of computational number theory and arithmetic geometry. Let $X$ be a smooth projective variety over a finite field $\mathbb{F}_q$, where $q = p^n$ for a prime $p$. The zeta function $Z(X, T)$ encapsulates the sequence of point counts $\#X(\mathbb{F}_{q^r})$ for all extensions $r \geq 1$. By the Weil conjectures, proven by Dwork, Grothendieck, and Deligne, $Z(X, T)$ is a rational function, and its computation is theoretically bounded [cite: 1]. However, transitioning from theoretical existence to practical, algorithmic computation requires the explicit calculation of the action of the Frobenius endomorphism on suitable cohomology groups [cite: 1, 2].

Historically, $\ell$-adic cohomology (where $\ell \neq p$) provided the foundational proof of the Weil conjectures, giving rise to algorithms like Schoof's algorithm for elliptic curves [cite: 2, 3]. While Schoof’s algorithm and its variants run in polynomial time in $\log q$, they scale poorly with the dimension or genus of the variety, relying heavily on the computation of torsion points which becomes computationally intractable for genus $g \geq 3$ [cite: 2]. 

Consequently, the computational frontier shifted toward $p$-adic methods, which scale significantly better with respect to the genus and dimension [cite: 2, 4]. These methods rely on lifting the variety from characteristic $p$ to characteristic zero (over the $p$-adic integers $\mathbb{Z}_p$ or the unramified extension $\mathbb{Z}_q$) and computing the Frobenius action on $p$-adic cohomology theories—most notably Monsky-Washnitzer, rigid, and crystalline cohomology [cite: 2, 5]. The initial breakthrough by Kiran Kedlaya in 2001 provided a practical algorithm for hyperelliptic curves in odd characteristic using Monsky-Washnitzer cohomology [cite: 3, 4]. Since then, the frontier has been defined by attempts to generalize Kedlaya's method to arbitrary curves and higher-dimensional hypersurfaces, and to optimize the asymptotic dependence on $p$.

The current computational era is defined largely by the algorithms introduced by Jan Tuitman, who generalized the $p$-adic point-counting framework to wide classes of curves via maps to $\mathbb{P}^1$ [cite: 3, 6], and Edgar Costa, whose work with David Harvey and Kiran Kedlaya on "controlled reduction" has enabled the computation of zeta functions in quasi-linear and average polynomial time [cite: 1, 2]. As we move into the 2024-2026 computational frontier, the Costa-Tuitman architectures are being aggressively extended. They are no longer just tools for counting points; they are actively deployed to compute Dieudonné modules for $p$-divisible groups [cite: 7, 8], to lift $L$-polynomials of genus 3 curves [cite: 9, 10], to explicitly resolve Newton strata of cubic fourfolds [cite: 1, 11], and to find rational points on modular curves via the Quadratic Chabauty method [cite: 12, 13]. 

## Foundational Cohomology Theories

To understand the computational techniques employed by Costa, Tuitman, and their successors, it is necessary to rigorously define the cohomological frameworks that support $p$-adic point counting.

### Monsky-Washnitzer and Rigid Cohomology
Monsky-Washnitzer cohomology was initially introduced to lift affine, smooth varieties over $\mathbb{F}_q$ to a characteristic zero setting while preserving a well-defined action of the Frobenius endomorphism [cite: 2]. For a smooth affine variety $\overline{U} / \mathbb{F}_q$, one finds a smooth affine lift $U / \mathbb{Z}_q$ and considers the weak completion of its coordinate ring (the dagger algebra $A^\dagger$), consisting of overconvergent power series. The Monsky-Washnitzer cohomology is defined as the de Rham cohomology of this dagger algebra. 

However, Monsky-Washnitzer cohomology is primarily restricted to affine varieties. Berthelot’s rigid cohomology extends this by providing a unified $p$-adic Weil cohomology theory that applies to arbitrary varieties over finite fields, including singular and non-proper schemes [cite: 8, 14]. It is defined using the de Rham cohomology of strict neighborhoods in a formal scheme over the Raynaud generic fiber [cite: 8]. A pivotal result by Baldassarri and Chiarellotto connects these theories, demonstrating that for smooth affine varieties, rigid cohomology is isomorphic to Monsky-Washnitzer cohomology [cite: 15]. This isomorphism allows algorithms to operate on affine patches using explicit overconvergent differential forms and then patch the results or use excision sequences to compute the rigid cohomology of a projective curve [cite: 8, 16].

### Crystalline Cohomology
While rigid cohomology provides coefficients in the fraction field $\mathbb{Q}_q$, crystalline cohomology is defined over the base ring (such as the Witt vectors $W(\mathbb{F}_q) = \mathbb{Z}_q$) and behaves well for smooth and proper varieties. Crystalline cohomology intrinsically captures the integral structure of the cohomology [cite: 8]. Specifically, $H^1_{\text{crys}}(X / \mathbb{Z}_q)$ is a free $\mathbb{Z}_q$-module, and it admits not only a Frobenius operator ($F$) but also a Verschiebung operator ($V$) such that $FV = VF = p$ [cite: 8]. 

The distinction between rigid and crystalline cohomology becomes practically significant when computing $p$-torsion and $p$-divisible groups. Rigid cohomology effectively computes the isogeny class of a $p$-divisible group (since it works up to isogeny over $\mathbb{Q}_q$), but the finer arithmetic invariants—such as the exact structure of the Dieudonné module—require the integral lattice provided by crystalline cohomology [cite: 8]. Recent computational leaps in 2026 have focused on extracting this exact crystalline lattice from Tuitman's rigid cohomological data [cite: 7, 8].

## The Tuitman Algorithm: Generalizing Kedlaya's Framework

Jan Tuitman’s pivotal contribution to computational arithmetic geometry is an algorithm that generalizes Kedlaya’s point-counting technique from hyperelliptic curves to an extremely broad class of curves [cite: 3, 6]. Prior to Tuitman, algorithms were largely restricted to hyperelliptic curves, superelliptic curves, $C_{a,b}$ curves, or non-degenerate hypersurfaces [cite: 6, 17].

### Mechanism of the Tuitman Lift
Tuitman’s algorithm operates on a smooth projective curve $X$ of genus $g$ over $\mathbb{F}_q$ defined by a possibly singular plane model $Q(x, y) = 0$, where $Q \in \mathbb{Z}_q[x, y]$ is a polynomial that is irreducible and monic in $y$ [cite: 8, 18]. Tuitman exploits the projection map to the coordinate axes (e.g., the map to $\mathbb{P}^1$ given by the $x$-coordinate) to establish an explicit basis of differentials for the rigid cohomology [cite: 8, 19]. 

The algorithm requires a "nice" lift of the curve to characteristic zero [cite: 7, 8]. Tuitman defines a matrix of Frobenius acting on the rigid cohomology $H^1_{\text{rig}}(X)$ using the connection on a suitable vector bundle (the Gauss-Manin connection) [cite: 3, 8]. The precision tracking in Tuitman’s algorithm is highly complex, as it relies on bounding the $p$-adic valuation of the matrices when solving the differential equations required for lifting the Frobenius [cite: 19].

### Complexity and Impact
Let $\omega$ denote the exponent for matrix multiplication. Tuitman, in conjunction with Pancratz, and building upon Harvey's baby-step giant-step improvements, established that the complexity of computing the zeta function using this method scales in a way that is vastly superior to naive counting. However, standard implementations of Tuitman's algorithm (as available in Magma) still exhibit a running time that is quasi-linear in $p$, meaning it scales as $O(p \log^{O(1)} p)$ [cite: 3, 9]. While polynomial in the genus and degree, this linear dependence on $p$ makes the algorithm sluggish for medium-to-large primes [cite: 4, 9].

Despite the bottleneck at large $p$, Tuitman’s algorithm fundamentally unlocked the ability to compute $p$-adic integrals (Coleman integration) on general curves [cite: 6]. Tuitman's rigid cohomology Frobenius matrices form the computational bedrock for virtually all subsequent advanced applications, including the extraction of crystalline cohomology [cite: 7, 8] and the Quadratic Chabauty method [cite: 12, 20].

## Costa's Paradigms: Controlled Reduction and Average Polynomial Time

Edgar Costa’s research, primarily conducted alongside David Harvey, Kiran Kedlaya, and Andrew Sutherland, addresses the primary limitation of Tuitman’s and Kedlaya’s standard algorithms: the time and space complexity dependence on $p$. 

### The Abbott-Kedlaya-Roe (AKR) Method and Non-degenerate Hypersurfaces
For higher-dimensional spaces, such as smooth projective hypersurfaces (e.g., K3 surfaces, cubic fourfolds), the Abbott-Kedlaya-Roe (AKR) method generalized Kedlaya's approach. However, it suffered from dense polynomial swell [cite: 1, 2]. Costa’s major contribution was the refinement and optimization of the AKR algorithm using *controlled reduction* [cite: 1, 5]. 

A hypersurface $X$ defined by a polynomial $f$ is considered non-degenerate with respect to a Newton polytope $\Delta$ if it satisfies certain smoothness conditions on the algebraic torus [cite: 1, 21]. Costa and his collaborators reduced the computation of the Frobenius action on the de Rham cohomology of non-degenerate toric hypersurfaces by preserving the sparsity of the polynomials during the reduction process [cite: 2]. By carefully managing how differentials are reduced modulo the relations in the Jacobian ring, controlled reduction prevents the intermediate expressions from expanding exponentially, thus reducing the time dependence on $p$ from polynomial to quasi-linear, and dramatically improving the space complexity [cite: 1, 2].

### Average Polynomial Time
A revolutionary advancement by David Harvey, subsequently implemented and expanded by Costa, Harvey, and Sutherland (CHS), is the concept of "average polynomial time" algorithms [cite: 9, 10]. If one wishes to compute the $L$-polynomial $L_p(T)$ of a curve defined over $\mathbb{Q}$ for all primes of good reduction $p \leq B$, computing them individually via Tuitman's or Costa's controlled reduction takes $O(B \cdot p \log^{O(1)} p)$ time.

The CHS algorithm computes the mod $p$ reduction of the numerator of the zeta function for *all* $p \leq B$ in total time $O(B \log^{3+o(1)} B)$, yielding an average time of $O(\log^{4+o(1)} p)$ per prime [cite: 9]. This relies on an adaptation of the "accumulating remainder tree" technique applied to matrices with entries in a quadratic field, combined with Nussbaumer's fast polynomial transforms [cite: 22]. Costa, Harvey, and Sutherland successfully implemented this for smooth plane quartics (genus 3 curves) [cite: 9]. This shattered the quasi-linear barrier, pushing the frontier of data collection for Sato-Tate distributions and modularity testing of higher genus curves and K3 surfaces [cite: 21, 23].

## The 2024-2026 Computational Frontier

The intersection of Costa's optimization and Tuitman's theoretical frameworks has resulted in an explosion of computational capabilities in 2024-2026. Preprints released in early 2026 highlight how researchers are actively modifying these algorithms to bypass previous theoretical roadblocks.

### Crystalline Cohomology and $p$-Divisible Groups (Booher, 2026)
In January 2026, Jeremy Booher published a preprint detailing an explicit algorithm to compute the $p$-divisible group $Jac(X)[p^\infty]$ of a curve over a finite field [cite: 7, 8]. The $p$-divisible group is a crucial geometric invariant that generalizes the $p$-primary part of the class group of the function field and dictates the curve's Newton polygon and Ekedahl-Oort type [cite: 8]. 

Prior to this work, computational approaches to $p$-power torsion could only compute the isogeny class of $Jac(X)[p^\infty]$ using rigid cohomology (with $\mathbb{Q}_q$-coefficients) or the $p$-torsion using de Rham cohomology (with $\mathbb{F}_q$-coefficients) [cite: 8]. To explicitly compute the Dieudonné module—which requires an exact basis over $\mathbb{Z}_q$—Booher builds directly on Tuitman's algorithm [cite: 7, 8]. 

**The Algorithmic Synergy:**
Booher's algorithm takes the "nice" lift $\widetilde{X}/\mathbb{Z}_q$ required by Tuitman's point-counting framework [cite: 7, 8]. Tuitman's algorithm relies on the projection map to construct a basis of overconvergent functions [cite: 8]. Booher contributes a method to realize the crystalline cohomology $H^1_{\text{crys}}(X)$ as the de Rham cohomology of this lift $\widetilde{X}$ using enhanced differentials of the second kind [cite: 8]. He calculates exactly how this integral crystalline lattice sits inside the fractional rigid cohomology $H^1_{\text{rig}}(X)$ [cite: 8]. 

By determining this integral structure, Booher can extract not only the Frobenius operator $F$ (which Tuitman calculates) but also the Verschiebung operator $V$ by solving the relation $FV = p$ modulo $p^N$ [cite: 8]. The runtime of this algorithm is polynomial in $p$, the degrees of the projection maps $d_x, d_y$, the extension degree $r$, and the precision $N$ [cite: 8]. This represents a milestone: transitioning Tuitman's point-counting algorithm from a tool that computes rational zeta functions to one that identifies exact finite flat group schemes.

### Lifting L-Polynomials of Genus 3 Curves (Shi, 2026)
In February 2026, Jia Shi addressed the missing link in the Costa-Harvey-Sutherland average polynomial time algorithm [cite: 9, 10]. The CHS algorithm computes the $L$-polynomial $L_p(T)$ *modulo $p$* in extremely fast average time [cite: 9]. However, to recover the exact integer polynomial $L_p \in \mathbb{Z}[T]$, one must lift the result from $\mathbb{F}_p$ to $\mathbb{Z}$.

Shi introduces a Las Vegas algorithm that takes the mod $p$ output of Costa, Harvey, and Sutherland's algorithm and computes the full zeta function for smooth plane quartics (and hyperelliptic genus 3 curves) in expected time bounded by $O(p^{1/2+o(1)})$ for a single prime, and $O(p^{1/4+o(1)})$ on average over all inputs [cite: 9, 22]. 

**Implementation Mechanics:**
The lift requires efficient arithmetic on the Jacobian of the curve $Jac(C)(\mathbb{F}_p)$ to perform a baby-step giant-step search [cite: 9]. While efficient Jacobian arithmetic is known for hyperelliptic curves (via Cantor's algorithm) [cite: 9], smooth plane quartics present severe challenges. Previous implementations by Flon, Oyono, and Ritzenthaler were limited to curves possessing a rational flex point (which only covers about 63% of quartics) and could only add "typical" divisors [cite: 9]. 

Shi provides a fully general hybrid implementation of the group operation [cite: 9]. A divisor $D = P_1 + P_2 + P_3 - 3P_\infty$ is "typical" if the points are non-collinear, lie on an affine patch, are pairwise distinct, and have distinct $x$-coordinates [cite: 9]. Shi’s hybrid algorithm uses rapid typical addition when possible and smoothly falls back on a generalized, albeit slower, naive addition algorithm (utilizing ideal intersection via Faugère's F4 algorithm and resultants) when atypical divisors or identity elements are encountered [cite: 9]. This provides the first fully general implementation of group operations on smooth plane quartic Jacobians uniquely identifying group elements, acting as the critical final step in the CHS computational pipeline [cite: 9].

### GPU-Optimized Controlled Reduction and Newton Strata (Batubara et al., 2026)
Simultaneously in late February 2026, Batubara, Garzella, Huang, and Mellberg tackled the $O(p)$ bottleneck of Costa and Tuitman's algorithms for higher-dimensional hypersurfaces [cite: 1, 11]. Building on the theoretical framework of controlled reduction from Costa's thesis, they formalized the central bottleneck of the algorithm as an optimization problem, introducing the concept of a "reduction policy" [cite: 1, 11]. 

A reduction policy determines the precise sequence of algebraic manipulations used to reduce dense polynomials modulo the Jacobian ideal without inflating intermediate $p$-adic coefficients [cite: 1, 11]. The team implemented a high-performance variant using GPU-optimized linear algebra code and a novel data structure for linear recurrences [cite: 1, 11]. 

**Outperforming Costa and Tuitman:**
Their implementation achieves state-of-the-art performance. For instance, their algorithm successfully beats the implementations of both Tuitman and Costa on many examples of quintic curves [cite: 1, 11]. Furthermore, they executed the first systematic computations of zeta functions for quintic surfaces and were able to compute the zeta function of cubic fourfolds at $p = 7$ [cite: 1, 11].

With this increased computational throughput, they deduced explicit examples of varieties with highly specific Newton polygons [cite: 1, 11]. The Newton polygon (the lower convex hull of the $p$-adic valuations of the coefficients of $L_p(T)$) is bounded below by the Hodge polygon [cite: 1]. Batubara et al. explicitly realized cubic fourfolds that are neither ordinary (Newton = Hodge) nor supersingular, identified quartic K3 surfaces of various Artin-Mazur heights, and found quintic surfaces possessing all possible "domino numbers" [cite: 1, 11].

## Diophantine Applications: The Quadratic Chabauty Method

Beyond abstract point counting, the rigid cohomology matrices produced by Tuitman’s algorithms have revolutionized the explicit solution of Diophantine equations over the rationals [cite: 20, 24, 25]. The central framework for this is the **Quadratic Chabauty method**, operationalized by the "BDMTV" collaboration: Jennifer Balakrishnan, Netan Dogra, Steffen Müller, Jan Tuitman, and Jan Vonk [cite: 20, 24, 26].

### From Chabauty-Coleman to Non-abelian Chabauty
By Faltings' theorem, a curve of genus $g \geq 2$ over $\mathbb{Q}$ has only finitely many rational points [cite: 27]. The classical Chabauty-Coleman method provides a practical way to find these points when the Mordell-Weil rank $r$ of the Jacobian $J(\mathbb{Q})$ is strictly less than the genus $g$ ($r < g$) [cite: 15, 24]. The method uses $p$-adic integration (Coleman integrals) over a prime $p$ of good reduction to construct locally analytic functions that vanish on the rational points $X(\mathbb{Q})$ inside the $p$-adic points $X(\mathbb{Q}_p)$ [cite: 24, 28].

When $r \geq g$, Chabauty-Coleman fails. Minhyong Kim’s non-abelian Chabauty program generalizes this by replacing the Jacobian with higher Selmer varieties [cite: 15, 29]. The Quadratic Chabauty method is the explicit, computable "depth two" realization of Kim's program [cite: 15, 30]. It applies when the rank $r = g$ and the Néron-Severi rank (Picard number) of the Jacobian satisfies $\rho(J) > 1$ (specifically, $r < g + \rho(J) - 1$) [cite: 15, 31].

### The Mechanics of Quadratic Chabauty
Quadratic Chabauty restricts the rational points by defining a global $p$-adic height function $h: X(\mathbb{Q}_p) \to \mathbb{Q}_p$ that decomposes into a sum of local heights $h = h_p + \sum_{\ell \neq p} h_\ell$ [cite: 18, 31]. 
1.  **Local Heights away from $p$ ($h_\ell$)**: For primes $\ell \neq p$, Betts and Dogra demonstrated that these local heights factor through the reduction map to the irreducible components of the special fiber of a regular semi-stable model, meaning they take values in a finite, computable set $\Upsilon_\ell$ [cite: 18, 25].
2.  **Local Height at $p$ ($h_p$)**: This is where Tuitman's rigid cohomology is essential. The local height $h_p$ is calculated using $p$-adic Hodge theory via the explicit description of the Dieudonné/filtered $\phi$-module $\mathcal{D}_{\text{crys}}$ associated to a unipotent bundle $\mathscr{M}$ with connection $\nabla$ [cite: 24, 25]. The Frobenius structure of this bundle is characterized by universal properties, and its restriction to an affine patch requires Tuitman’s reduction algorithms in rigid cohomology to compute [cite: 25, 32]. 

By computing a combination of Coleman integrals and these height pairings using a "nice" correspondence $Z$ (an endomorphism in the Néron-Severi group), the BDMTV team computes a finite set $X(\mathbb{Q}_p)_2$ that contains the rational points $X(\mathbb{Q})$ [cite: 15, 18]. 

### Triumphs in Mazur's Program B
In a landmark 2019 paper published in the *Annals of Mathematics*, Balakrishnan, Dogra, Müller, Tuitman, and Vonk used Quadratic Chabauty to resolve the rational points on the split Cartan modular curve of level 13, $X_s(13)$ [cite: 20, 26]. This curve is of genus 3, and its Jacobian has rank 3, placing it entirely outside the reach of classical Chabauty [cite: 24]. Because $X_s(13)$ has everywhere potentially good reduction, the local height contributions away from $p$ are trivial, and its Jacobian has a Néron-Severi rank of 3 [cite: 24]. The BDMTV team proved that $X_s(13)(\mathbb{Q})$ consists of precisely seven points (all CM points), thereby completing the classification of non-CM elliptic curves over $\mathbb{Q}$ with split Cartan level structure—a major open question in Serre's uniformity problem [cite: 20, 24, 26].

Continuing into 2023 and beyond, this collaboration formalized algorithms for broader classes of modular curves associated with Mazur's Program B [cite: 13, 25]. They calculated the rational points on $X_0^+(N)$ for genus 4, 5, and 6, the non-split Cartan curve of genus 6, and specifically proved that $\#X_{S_4}(13)(\mathbb{Q}) = 4$ (one CM point, three exceptional) [cite: 12, 18, 25]. These achievements represent the absolute pinnacle of applied computational cohomology, marrying profound $p$-adic geometry with massive, highly optimized computational algebra.

## Computational Bottlenecks and Methodological Challenges

Despite the immense progress from 2024 to 2026, several rigid computational bottlenecks persist, driving current research.

### Precision Tracking and Loss
One of the most persistent issues in both Costa's and Tuitman's algorithms is the loss of $p$-adic precision during linear algebraic operations. When computing the Frobenius matrix on $H^1_{\text{rig}}(X)$, algorithms must repeatedly divide by $p$ (due to integration of power series of the form $\int x^{n-1} dx = x^n/n$) [cite: 17]. In Tuitman's setup, tracking the $p$-adic valuation of matrices $M_s$ is critical [cite: 17, 32]. To achieve a target precision of $O(p^N)$ in the final zeta function, computations must often be carried out at significantly higher internal working precision, which drastically slows down arithmetic operations in $\mathbb{Q}_q$ [cite: 6]. Balakrishnan and Tuitman have provided detailed precision loss estimates, yet optimizing this bound remains an active software engineering problem [cite: 15, 25].

### The Limits of Quadratic Chabauty
While Quadratic Chabauty succeeds when $r < g + \rho(J) - 1$, modular curves frequently possess Jacobians with large Mordell-Weil ranks and trivial Picard numbers, rendering even this advanced method insufficient. When $r = g$ and $\rho(J) = 1$, higher depths of Kim’s non-abelian Chabauty (e.g., cubic Chabauty or motivic Chabauty) are required [cite: 4, 33]. Furthermore, the numerical stability of algorithms is often hampered. Jia Shi notes that when searching for rational torsion subgroups on the Jacobian without relying on height bounds, points must be represented as $Q_1 + Q_2 + Q_3 - P_1 - P_2 - P_3$ to avoid numerical instability associated with atypical divisors [cite: 34]. 

### Scalability to Higher Dimensions
Costa’s controlled reduction enabled the first computations of cubic fourfolds and quintic surfaces, yet scaling to higher primes ($p > 50$) or higher degrees remains computationally prohibitive [cite: 1, 11, 35]. The memory required to store the dense multidimensional tensors during the reduction of differential forms can quickly overwhelm standard RAM, necessitating the GPU-optimized approaches pioneered by Batubara et al. [cite: 11].

## Future Trajectories

As indicated by the 2024-2026 data, the computational frontier of crystalline and rigid cohomology is branching into several high-potential trajectories:

1.  **Prismatic Cohomology and Homotopy Theory**: Theoretical frameworks are advancing rapidly. At a 2025 Simons Foundation meeting, Jacob Lurie and others outlined how the new prismatic cohomology (a vast generalization of crystalline and $p$-adic Hodge theories by Bhatt and Scholze) provides a cohomological machinery that may soon yield algorithmic analogues in $K$-theory and topological Hochschild homology [cite: 36].
2.  **Machine Learning Integrations**: Edgar Costa’s most recent publications in 2024 and 2025 demonstrate a pivot toward utilizing Machine Learning to predict arithmetic invariants. Papers such as "Learning Euler Factors of Elliptic Curves," "Machine learning the vanishing order of rational L-functions," and the use of convolutional neural networks for Murmurations highlight an impending hybrid era where AI heuristic predictions guide the resource-intensive exact cohomological point-counting algorithms [cite: 23, 37].
3.  **Wider Classes of Curves**: Extensions of algorithms to handle highly singular curves, non-hyperelliptic genus 3 and 4 curves lacking nice plane models, and superelliptic varieties in characteristic 2 are seeing active development, relying on intricate algorithms to compute Picard lattices and Riemann-Roch spaces directly [cite: 22, 23, 38]. 

## Conclusion

The period from 2024 to 2026 has witnessed the transition of $p$-adic cohomology from a theoretical apparatus proving the Weil conjectures to a highly optimized, industrial-scale computational tool. The legacy of Jan Tuitman’s broad generalization of Kedlaya's rigid cohomology algorithm, coupled with Edgar Costa’s aggressive optimizations through controlled reduction, has laid an indestructible foundation. 

Preprints from Booher, Shi, and Batubara et al. in early 2026 prove that the Costa-Tuitman paradigm is not a closed chapter; it is an actively expanding frontier. By leveraging these algorithms to uncover crystalline Dieudonné modules, lift $L$-polynomials, and map out the Newton strata of higher-dimensional surfaces with GPU computing, the arithmetic geometry community continues to unveil the deepest structural properties of equations over finite fields. Concurrently, the BDMTV collaboration's use of these exact rigid structures within the Quadratic Chabauty method demonstrates a triumphant synergy: using the geometry of characteristic $p$ to solve the oldest equations of characteristic zero.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGD7UU2xXKXrPoFnP6fd-KBYCXej1CPIM5HKSbwH8GxxNsgid288ATVWEGhk2K44z8DZvGljMlOdsll53dpaKgtJ99FeaAdy9yplpeZMFrTfEH2AWPWQ==)
2. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFgd47zQ-VMvHeeqDNSFiB3reLmWj8I9qcxgvHaeMRycM_7-bQ0XfdSkVzoJleCEH7JOHyINce1jBZdOcgFPddz3oKxwBxWlHwEveGjaK9sguTaKaNzWa9lELrI2cq714=)
3. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFD8UXNhFmtGg7BM0C4T8HnPkdiD-27mKK0kFEpgUB0tQiK0uYbhiLdGt19u_ATraKdQk_Iv0LGulB0c7bOFfQFb8yl2HhomW5NtSUDydHEt5TqlAXJmHVTvvj0)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFROkzOp2T07GezDK1C7ABlqJHb_1CSnJR0Ha-qaQtlWVj6_9-yrAHsXwnTUxm7g8gd-wWU1PeSLdTlRD7-IQXYsf2nW4TMxRR1RRs-XQ-DeAhjO_rukh0EsE7mTlfDXIlN2bpcZyYmJySN25983i54TsjiglKL7XWP28oV1NpRKVfL0CsuhHkEu_12bGnw9dPhJAdUgvKimdM_GxQWhs9b34zbe3Ocs596WFpoxIsUts=)
5. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGs4JDP10wOeBRZ4sl9EvPUD9I-mS0Qm4WVmGnqD_MAsq2_cdwffETkArnPF2FIgj-SuO96WGuckNhJHRo2yKCwD-3i05_4fjNAwWA1WPEIPBsn9ACDEWagQA6RHLzxSs9wsp_L6PBx5B08bbuEj5saPIJMoyRmrOOX19ktAqhMeNJUqWg2crkVMlpylKmRltftmhSTLxYHPn_VaO2VK1I47yLBgH1lBlA6F2nyhYFhgVx4Mca5Y6WwMUg=)
6. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNyWDUfCfnc8EZSYOFA1COFgTJu4kNi2Cp1Azvs0myO3GlCuK5i5qSW7lndgJGY_S_aPvRhhD5tfyL6wNbERSVVbTshJxyzb9d8zrVKQfnVKWZ9eShKyt4XxToQTuuUBG1A8oyjgz4MA_f8eA8PMrTXkM=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9sxqGMQz-w2Vv2yAQX_Ku9HQdlAXPgX37vb-2SxeIVXZNzKWZ0jt--AUI_2Cpt3_63zHshijNYHAbfro1QRgpvV7lSsgmdcQSpgaoaRUgUrqBazS48g==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmZ1wEykhKB3SBVwITcmAj_om7Cr-HyypX0yF7ZbC_YcvmqlMxdCDS8MVWRXFz8wrL10WMJRha9R6D1N1kdkqzKy4EmslV-QN4AXqtW_LNRZiKCCWT4w==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFD02FRbGSh6kVw8Bfq0afoygs0fIqkJBWojbvVRSQkuAvE1uVwRxpDzFBgPx2jRLQbaiuTelvxh2gvSYe0M8KwA1ftZm6ncAFz2yWdX5MpAV5WmGE3xQ==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpNKXlwk65Kqu6dBIS4ueWjDnFnmmYFhXRP6gKMWkSnYLPtSQZ4Aog6VP2_WK4xQhQoU1-p-N7DiyUJoASWMaop9JOipzi8iexOOQqZz_CX4V8kPCrUw==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgwkVaFTlQWX6FJff9P0vevUlGkyZcw9BvBkmwvj3J7g6EDSK2JuOTiCQUFQcVchYk-BP5qFD3XOAt6UEQO4D5vtUHRMz34HELFFsMFIrwJ-oHbSdq6w==)
12. [kcl.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjfGLoXGjtln7-M2_MEdhPX9AKqUNQbGLquId2COZrmijjn_GTmn1PHtYrpEzKx9tmdFhq3ueeZRmoCLvgsiwhJJMfbhgu2OEvI1iiV3Eebx6uNpfLC2oulmdWsxNCMWgsR6IGbfkafcgs5qbOoTHKcSmY1DV6BBhQDMcHmXaqWiyyWVp-CIaU8PisputpetKdRXYhXZestr1C9Qzr_OueR4BJEfA=)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYIQbPNYu19dzEsi46ZUKuaKK-HeKI1LLH1BL4Vy_FTPfeUkl0_Nm2sjYo3xczxijvTeXgn86sah9GHD_4VhcoEmMIQffB91A0yhGV0QIO8r-D0R6-FQ==)
14. [antsmath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEs0XH_UAu6EX9SoYA23XzlAkswFIpKm3eRg0R8COmxtbHmPOsMjJ2_Sh-7WR-cb_wCllkCIhJdQ_ajEAoVC1hHE8ZMaRIvwgCSe_vPPvB5POco6-ZgDJ0G5RVqUt-K61QqvY4v09KTKownpJ-B1R8vcA==)
15. [bu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEanijs5xHGX94CIXImSp04QbmlVOjVSGLMLKJW9NR9Z2Ez5nq1gtwJoW_NE1Fin4FiuAK7S1RWnjlLC1QtOAhDuXT6NRpBj-IeyufEjJ9eYntU1ZBfdVhLJMxpr0ct32SMxrBuwbBpfEQVDesQoInFaJIB0C369A==)
16. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFR_fJ2eGaUiiL1_MorOxOVrqcY630ddfCn6Xyguv3O2mh7Lf-lLDiRQX344E1gKp70Bqe_fKlUky89AVBn6usZWs3Ly5rLiaCwQK7xRGpwRgvUSFIuh8qdX4Hmk8tNUh-UpFuhISGSS7n8KQ==)
17. [edgarcosta.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGgfKkysPRTnu-1xSdPdFJxJYzXiNmEFu9wswayIxDIvSpMZknCSmmGZjait1X-HHcIKVU_lfiM6Gcta4TSZk-uQMYJTfA_74JXOR5oFSDtK2FH9lFpXN1w9OFzIIoAXQcJaHAUnd8eA==)
18. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXVAStrWUUhk6MSUTg0kPaxhmQodwwFI9WXE7avw1NySPw5uBs16IqDgjhVadFt0Qyvz9jTJwgMnAcLBWG07pSrXPgvNh4x55hFLtMIU-ZaqViAzCWqitr_PV7pidSRPM=)
19. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFm3BtTCL_YlrR7GBdsPeYbPKbMpLAKDzwgPQvvUMzZQoRxB5DT8Ylx6dwR2H_GT9jFGmSPaMRKFQpn4FYOmGGvixD95p1na5-VynUcKgldt-8=)
20. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXCQ0nRIkjjugCMjFV64mGETUGFq4FO2jOXXh3llGHs99oeY3H8sZ-Z7bMxOvlhnD5S9l1FhtYG66zuiCUQMW8Q0A5Sx7jxGbmC4qdqxeg8y5D66Hj8IBnsRioxExUuslLdUmzWgE=)
21. [edgarcosta.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkRH2qmSqmFA9NxtPR7QY27NZEhHdiF0Rh15ESzgFxnR-57qYYM-3t-ZQa4GMLdyMpzbJ0iBNm9EXocRVbeyOyy-E2N1-B4id4CB2L4W7OTww_Sp1iTm1BmH8TuSrkKT3kGmCV9ugL5f0=)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjTbH0-ar27Uo83tTEUkGrSxuS8DNdNIhSdew1TrZRAjheYIGwA_it3WqfEpt2SrMkpQfqOKbsOyXB6dGPdYp6qSDJQRxWnWHkbKqNdu7do5gkENQEsQlTbT5G6Cd5JRS2Ur_w8YmSGvJeNPh8JGhTzky7fs4z-VALVNaBAnkK-fedvO5Xkzjs_-rq_gvNMYo=)
23. [edgarcosta.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyXEsmeWfPm7POqaM7wShkC9OEhaCVmzcYjwAPlaoUmrO_hpslVOvUss-s9tF_mqOIc7zEFwQN2Tzd_JPgcr77LcfmuA5XxIvQTsHEbQswwYj8K_W3LYCqpTHAuS1rk-TfdbjUTA==)
24. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8nfqmHkYg_HYZRM8ZCPstYkPUrnP9vpDpDgf0lG4g-21LTu0ou33DBMR5PjmVNE9-N19q9lqYNeMd5s559KqkwBlfTyWJCvw1qndm0zE0K4_MxXDY9Sh7drMX_Tq_Mfyp7hFIU9d5mGbq)
25. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYzNIozVyTM8QJG9-NMa_RDfBO5Fr7_d1_LIBJ_9YbFR9yhBgl9KJHPpN5fecMJEzS01CjuWgEwlUwG1hNYZpv88XVC1rbfs0IXkHF2B-FLbCUVQ8OgAH7wLeQC8y1I6ilcThKqU93rRPfHZQvTBWSFn5-x5BirFr6C2dI7qksTYwn1Pq0ADdcC88N4w606ky47CA0fByUsiw-ti2YyN1WgSB_qagV2ajjbUPXValWOHJIF6nzC9DUfeLSeZ-0XGEYqbJVcFRlPrK9R3AzoJNbc1UNJ5cJ_hBc-JrU)
26. [leidenuniv.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdfcjn-XdtjNrZzy5GwmH7nMeTRQZrOvMJYuH_bowETHAZaK30I5vblCtG0KP6L2dN4zPvssRTAZQSCD6FYCMfuaRJYUEt1TyJyceyePVNf-zvCPu-7bYFMfr-yXPLO0wikeIYsH0A_pzyNi6pc2qp9xrn_Q==)
27. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYamGGcesq241AejNJi3xmSwtLHUKADdJ3loldNOeKiyNzwnK46oJXhhtmumLPo-XtzpSQLBVfbS52tYGlWTiXSVcy7D_EzSh6kvrtdAkZ9vzDxhVLN5kzY7yqoh2BHeponYDSDNRg9v4_YNY=)
28. [kskedlaya.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEe_SJM9NN9jpAPCA051Fg8JgnYvfk7SdmSSVu54fMR8ePrnDjE3GomUTuX7yACgvFjfqlln5hdy4PFA7ujA-wX9ngkdOCbOuqY2aq2raurcRmBsnd9s4CmiJjmjUzuyZ6VAwzyRfk2)
29. [leidenuniv.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOjXcXkciju5nUhSf5s38KOehrGgjx3eJvRYI2yoMSs8w3V0czGkIt6WAWSZ-qc2lZxeL2Gt6RDZc7iPZFdX7KU_gPaDBMLMxQOETsogsjFrIBILJBcbof7t--mmrJi8jgxwI9iPKcfSFd3h8c2jkhQNzxW74=)
30. [bristolmathsresearch.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvcRYlmH-Wukt34XLHwxUMWsZCOFX4wSdv5YCXUtDINDgS0I03LbQSjeSF6vfJ2hHdsP-fNWzpdA1dBfXXgeem0mli3m7oIi2H3nssldOhV9vnyIkJ7zAwKlvvmm57Igfva-HikUHR8lkO4KoOdhCITDs=)
31. [githubusercontent.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFv-8lvsnRi6dBNAEKP91uKwYJc77w40SQDTNQm9RJuLUhhA6HzcEYa4hYk_7d1_MTT_a9YN06-MIGDnBHG2sSwYxCpxWoFAovS6GRMo5hVCCyZvnwfT8uysslcJo4aMq-IpG81RanvDGV9X2a14W7rN65IcbY_8nSWn4Sjp3UcvIa0JAPByfJtlquW2GKqzipYDwnwArVdwidAwTa8TUIlAw8fQcD)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhhvjU5fhGBy7Yx85J_hZTCbmaekh9npyrsfuqPQ6eMn4A6J7M9eL5pq4rDg69niEVGbPAPBdC9JfqljELmrwU9jgosa-GYi-b0d5L_frG_ggT_mNBWQ==)
33. [ucsd.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGH2oLVxCkBDa0AVecHGR7ImaiK274EFGndy17y6blFlG9OZUzsR7y6giTupXI36Kmnf-0UIVFNwUhZwTW5OX5wCRMLRrdwEr8hwAK9AxMSCsZ6HB_6RaMWmdQiaohJFlsXF2NnmvI2wLmc3CuZ)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDDN2rQo0FJ05-H5dSis6QRhXnZH8GDtbnJ9LZXExyDrXU7LheOczXIfsMY1M8VsnGQQh6TTuQ68qF4znBNZGQ1flJ07MVIuqlmKFwpuoGVJ0taC9KYY-xDw==)
35. [edgarcosta.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEeFK_u0J9STL82DcHkbC9OXZ3dgJAWp2_Sg0UJeMEGxOf4p6Ep69HgkhBVMjpJr8wOdOmV8WyjsGswj4MWwXzrwQze8PipjehH3GRa9MMXZl5MQZ67Hatg67sbMsbSdw4TnWM=)
36. [simonsfoundation.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQBLeOAZsZcKHGg0I3MGyZX516-uqYYgr391hsCqhJS0Ph55Q2akAnV4lt5wnpUjrRfAPuTETrh07Rs1_ehrtJVkJFPWJXMr4PdwjId5hrtrz2SHHmQMfoyMjUwblm5Nf1xmwCtujTXqH4f7nVLA_eV1l52EEh24JHiAUi8yr7DEMNDCGFeTv6PLckrIGZSa6CXEUiJA9AStFSInHMXc1iaXYed1_9klLUKia8EMLbhGflAIqB)
37. [edgarcosta.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFM629jZa61tzAeVcxwlDeUZu8jwYSkfqIPRkO6NSL9CzE5z47_QW-mJYA3Iut25mjaIa_usIH0mHE7ueLfxp9Z0wqPrC_R2Fsvpn0hGo-nyqZiODzZ)
38. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbbr7UqggjSFka_M0GnhCc5QcOn1bM3zkUX2A_pvW8YRyfE5P_X-Liq2Q_P6kVgbN4hTJ0nc1vBQbl_4Ybfdsj7pOJP6MrUkB4RuqgTuCOtRwHA9g4WaRdIugO2fJFii4306lD4FS6DsiJgA54cZ2xTLeDOeBfs6Jbj7IXA_pQvkq6u65YDc-e6l3hxbVLKgoq8ow_aTa7lLTF9mM29QUHTirLBoV0bqhRvJ2ocCROmEPw5_H_DBt3qXr6ARAtQw==)

