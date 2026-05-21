# Hyperelliptic Jacobians + endomorphism algebra computations 2024-2026 (Costa, Mascot)

**Pythia queue id:** 178
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdiVHNQYXV6RE5jaVk5TW9Qd3NLQ3dRNBIXYlRzUGF1ekROY2lZOU1vUHdzS0N3UTQ
**Elapsed:** 314s
**Completed at:** 2026-05-21T17:11:04.787765+00:00

---

# Hyperelliptic Jacobians and Endomorphism Algebra Computations: Recent Advances and Developments (2024–2026)

The computation of the endomorphism algebra of a Jacobian of a curve defined over a number field represents a fundamental challenge at the intersection of arithmetic geometry, algebraic number theory, and computational mathematics. Over the past decade, researchers have made significant strides in transforming abstract theoretical constructs into rigorous, effective algorithms. Much of the modern algorithmic foundation was established by Edgar Costa, Nicolas Mascot, Jeroen Sijsling, and John Voight in their seminal 2019 work on the rigorous computation of the endomorphism ring of a Jacobian [cite: 1, 2]. 

Building on this foundational breakthrough, the years 2024 to 2026 have witnessed an explosion of new techniques and applications driven primarily by Costa, Mascot, and their collaborators. Recent efforts have expanded the scope of computations from single Jacobians to isogeny classes of typical principally polarized abelian surfaces over the rationals [cite: 3, 4]. Concurrently, there has been a systematic push to label and classify abelian varieties over finite fields using their endomorphism algebras, resulting in comprehensive new databases [cite: 5, 6]. Additionally, the study of Galois representations has advanced significantly, with Mascot developing methods to compute division polynomials for Jacobians over function fields, thereby isolating representations occurring in families of curves [cite: 7, 8]. 

* **Key Points:**
*   **Algorithmic Foundations:** The 2019 Costa-Mascot-Sijsling-Voight algorithm shifted the paradigm by combining numerical approximations of period matrices with the LLL algorithm and rigorous algebraic certification using Puiseux expansions, allowing for the exact determination of endomorphism algebras for hyperelliptic Jacobians [cite: 2, 9].
*   **Isogeny Classes and Abelian Surfaces:** From 2024 to 2025, Edgar Costa and co-authors developed efficient algorithms to compute all principally polarized abelian surfaces over $\mathbb{Q}$ that are isogenous to a given surface, employing a mix of analytic techniques and open-image theorems for Galois representations [cite: 3, 4].
*   **Classification over Finite Fields:** In 2025 and 2026, major progress was made in the deterministic labeling of isomorphism classes of ordinary abelian varieties over finite fields, providing practical invariants that map to the Honda-Tate classification via Weil polynomials [cite: 5, 10].
*   **Galois Representations in Families:** Nicolas Mascot's recent work (2024–2025) extends $p$-adic lifting algorithms to compute division polynomials for Jacobians over $\mathbb{Q}(t)$, facilitating the study of Galois representations in the étale cohomology of families of curves and surfaces [cite: 7, 8].
*   **Desingularization and Riemann-Roch:** Mascot has also introduced computationally robust methods for the desingularization of plane algebraic curves and the calculation of Riemann-Roch spaces, which are essential for integrating algebraic functions and evaluating torsion in the Picard group [cite: 11, 12].

---

## 1. Introduction to Computational Arithmetic Geometry

Arithmetic geometry studies the solutions of algebraic equations over rings of integers and number fields. A central object of study is an algebraic curve $C$ defined over a number field $F$. Associated with every such curve is its Jacobian variety $J = \text{Jac}(C)$, an abelian variety whose points parameterize degree-zero divisor classes on the curve. The geometric endomorphism ring of the Jacobian, denoted $\text{End}(J_{\overline{F}})$, contains profound arithmetic and geometric information. The structure of this ring and its field of definition have important implications for the arithmetic of the curve, such as identifying the automorphic realization of its $L$-function, proving modularity, and understanding the distribution of Frobenius traces (the Sato-Tate conjecture) [cite: 2, 9].

For decades, determining the endomorphism ring of an arbitrary Jacobian was treated as an abstract existence problem rather than an algorithmic one. Early theoretical work provided bounds and structural classifications (such as Albert's classification of involution algebras), but practical computation was limited to elliptic curves (genus 1) and very specific families of higher-genus curves. It was only through the convergence of high-precision numerical analysis, lattice reduction algorithms, and rigorous algebraic geometry that general-purpose algorithms emerged. 

The algorithmic framework proposed by Costa, Mascot, Sijsling, and Voight [cite: 2, 13] addressed a problem posed by Bjorn Poonen in 1996 regarding the algorithmic decidability of the endomorphism ring of a genus 2 Jacobian. By combining numerical integration to approximate the period matrix with rigorous $p$-adic and Puiseux-series verifications, their method provided a fully certified endomorphism ring. Between 2024 and 2026, Costa and Mascot extended these methodologies to handle broader questions. Costa focused extensively on the moduli spaces of abelian surfaces, creating exhaustive databases of isogeny classes [cite: 3], classifying abelian varieties over finite fields [cite: 5], and studying connections to K3 surfaces [cite: 14]. Mascot, on the other hand, pushed the boundaries of computing Galois representations, tackling families of curves over function fields $\mathbb{Q}(t)$ and developing new tools for desingularizing algebraic curves [cite: 8, 11]. This report provides an exhaustive, highly detailed synthesis of these developments.

---

## 2. Fundamentals of Hyperelliptic Curves and Jacobians

To comprehend the advancements in endomorphism algebra computations, one must first establish the rigorous mathematical framework governing hyperelliptic curves and their Jacobians.

### 2.1 Hyperelliptic Curves

Let $F$ be a perfect field (typically a number field or a finite field) and $\overline{F}$ its algebraic closure. A hyperelliptic curve $C$ over $F$ of genus $g \geq 2$ is typically given by an affine equation of the form:
\[ y^2 + h(x)y = f(x) \]
where $f(x), h(x) \in F[x]$. If the characteristic of $F$ is not 2, we can complete the square and simplify the model to $y^2 = f(x)$, where $f$ is a squarefree polynomial of degree $2g+1$ or $2g+2$ [cite: 15, 16]. The points of $C$ consist of the affine solutions $(x, y)$ along with one or two points at infinity. The curve $C$ admits a natural hyperelliptic involution $\iota: (x, y) \mapsto (x, -y - h(x))$, and the quotient $C / \langle \iota \rangle$ is isomorphic to the projective line $\mathbb{P}^1$. 

The function field of $C$, denoted $F(C)$, is a quadratic extension of the rational function field $F(x)$. The arithmetic of the curve is governed by its divisors. A divisor $D$ on $C$ is a formal linear combination of points $D = \sum n_P P$, with $n_P \in \mathbb{Z}$ and $P \in C(\overline{F})$. The degree of $D$ is $\sum n_P$. The set of all divisors forms a free abelian group $\text{Div}(C)$. Divisors of the form $(f) = \sum \text{ord}_P(f) P$ for a rational function $f \in \overline{F}(C)^*$ are called principal divisors and form a subgroup $\text{Princ}(C)$. The Picard group is the quotient $\text{Pic}(C) = \text{Div}(C) / \text{Princ}(C)$. Because the degree of a principal divisor is zero, the degree map descends to $\text{Pic}(C)$, and the kernel of this map is denoted $\text{Pic}^0(C)$ [cite: 2, 9].

### 2.2 The Jacobian Variety

The degree-zero Picard group $\text{Pic}^0(C)$ can be endowed with the structure of a projective algebraic group variety over $F$, known as the Jacobian variety $J = \text{Jac}(C)$. For a curve of genus $g$, the Jacobian is a principally polarized abelian variety of dimension $g$. Over the complex numbers $F = \mathbb{C}$, the Jacobian has a beautiful analytic description. The curve $C(\mathbb{C})$ is a compact Riemann surface of genus $g$. The space of holomorphic 1-forms $H^0(C, \Omega^1)$ is a $g$-dimensional complex vector space. The first homology group $H_1(C(\mathbb{C}), \mathbb{Z})$ is a free abelian group of rank $2g$. Integration of holomorphic 1-forms along homology cycles yields the period map:
\[ H_1(C(\mathbb{C}), \mathbb{Z}) \to H^0(C, \Omega^1)^\vee \cong \mathbb{C}^g \]
The image of this map is a full lattice $\Lambda \subset \mathbb{C}^g$. The Abel-Jacobi theorem states that there is an analytic isomorphism:
\[ J(\mathbb{C}) \cong \mathbb{C}^g / \Lambda \]
This isomorphism translates the algebraic group law on divisor classes into simple vector addition modulo a lattice. Computing this period lattice $\Lambda$ numerically is the vital first step in algorithmic investigations of the Jacobian [cite: 15, 17, 18].

### 2.3 Riemann Relations and Principal Polarizations

Not every complex torus $\mathbb{C}^g / \Lambda$ is an abelian variety (i.e., not every torus can be embedded into a projective space). A complex torus is algebraic if and only if it admits a Riemann form. Let $\Pi$ be the $g \times 2g$ period matrix whose columns generate $\Lambda$. A Riemann form is a skew-symmetric integer matrix $E \in M_{2g}(\mathbb{Z})$ such that:
1. $\Pi E^{-1} \Pi^\top = 0$
2. $i \Pi E^{-1} \overline{\Pi}^\top$ is a positive definite Hermitian matrix.

For a Jacobian $J$, the intersection pairing on $H_1(C(\mathbb{C}), \mathbb{Z})$ naturally provides a principal polarization (a Riemann form $E$ with determinant 1). By choosing a canonical symplectic basis for homology—cycles $\alpha_1, \dots, \alpha_g, \beta_1, \dots, \beta_g$ such that $\alpha_i \cdot \alpha_j = \beta_i \cdot \beta_j = 0$ and $\alpha_i \cdot \beta_j = \delta_{ij}$—the matrix $E$ takes the standard symplectic form $J_{2g} = \begin{pmatrix} 0 & I_g \\ -I_g & 0 \end{pmatrix}$. This structure is heavily utilized when searching for endomorphisms [cite: 16].

---

## 3. The Theory of Endomorphism Algebras of Abelian Varieties

### 3.1 Endomorphisms and Homotheties

An endomorphism of an abelian variety $A$ is a regular map $\alpha: A \to A$ that is also a group homomorphism. The set of all endomorphisms defined over $\overline{F}$ forms a ring, denoted $\text{End}(A_{\overline{F}})$, with addition given by pointwise addition in the group law, and multiplication given by composition. Since abelian varieties are torsion-free as $\mathbb{Z}$-modules in characteristic zero, the endomorphism ring is a free $\mathbb{Z}$-module of finite rank $\leq 4g^2$. The endomorphism algebra is the finite-dimensional $\mathbb{Q}$-algebra $E = \text{End}(A_{\overline{F}}) \otimes_{\mathbb{Z}} \mathbb{Q}$ [cite: 16, 17].

Over the complex numbers $A(\mathbb{C}) \cong \mathbb{C}^g / \Lambda$, an endomorphism lifts to a $\mathbb{C}$-linear map on the tangent space $\mathbb{C}^g$ that preserves the lattice $\Lambda$. Thus, an endomorphism corresponds to a complex matrix $M \in M_g(\mathbb{C})$ such that $M \Lambda \subset \Lambda$. If $\Pi$ is the period matrix, there must exist an integer matrix $R \in M_{2g}(\mathbb{Z})$ representing the action on the homology basis such that:
\[ M \Pi = \Pi R \]
This relation is the cornerstone of numerical algorithms [cite: 13, 16]. The matrix $M$ is the analytic representation, and $R$ is the rational representation. Note that $R$ determines $M$ uniquely, and $M$ determines $R$ uniquely since the columns of $\Pi$ span $\mathbb{C}^g$ over $\mathbb{R}$.

### 3.2 The Rosati Involution and Albert's Classification

A principal polarization $\lambda: A \to A^\vee$ (where $A^\vee$ is the dual abelian variety) induces an anti-involution on the endomorphism algebra $E$, called the Rosati involution. For $\alpha \in E$, it is defined as:
\[ \alpha^\dagger = \lambda^{-1} \circ \alpha^\vee \circ \lambda \]
In terms of the rational representation $R$ and the symplectic form $E_0$, the Rosati involution corresponds to the adjoint with respect to the Riemann form:
\[ R^\dagger = -E_0^{-1} R^\top E_0 \]
The Rosati involution is positive definite, meaning $\text{Tr}(\alpha \alpha^\dagger) > 0$ for all non-zero $\alpha$. This positivity implies that the endomorphism algebra $E$ is a semisimple $\mathbb{Q}$-algebra, and in fact, a product of division algebras. 

Albert classified the simple factors of such algebras into four types [cite: 16]:
*   **Type I:** A totally real field $L$.
*   **Type II:** A quaternion algebra over a totally real field $L$ that splits at all infinite places.
*   **Type III:** A totally definite quaternion algebra over a totally real field $L$.
*   **Type IV:** A division algebra over a CM-field $K$ (a totally complex quadratic extension of a totally real field $L$).

For a Jacobian of a curve of genus 2, the dimension of $A$ is 2. The possible endomorphism algebras are highly restricted. They can be $\mathbb{Q}$ (generic case), a real quadratic field (Real Multiplication, RM), a CM quartic field (Complex Multiplication, CM), an indefinite quaternion algebra over $\mathbb{Q}$ (Quaternionic Multiplication, QM), or a product of fields (when the Jacobian splits into a product of elliptic curves up to isogeny) [cite: 2, 17].

### 3.3 Tate Modules and the Tate Conjecture

For an abelian variety $A$ over a number field $F$, the $\ell$-adic Tate module is defined as $T_\ell(A) = \varprojlim A[\ell^n]$, which is a free $\mathbb{Z}_\ell$-module of rank $2g$. The absolute Galois group $G_F = \text{Gal}(\overline{F}/F)$ acts continuously on $T_\ell(A)$, giving rise to an $\ell$-adic Galois representation:
\[ \rho_{A, \ell}: G_F \to \text{Aut}(T_\ell(A)) \cong \text{GL}_{2g}(\mathbb{Z}_\ell) \]
Faltings proved the Tate conjecture for abelian varieties over number fields, which states that the natural map:
\[ \text{End}_F(A) \otimes_{\mathbb{Z}} \mathbb{Z}_\ell \to \text{End}_{G_F}(T_\ell(A)) \]
is an isomorphism [cite: 16]. Consequently, the endomorphism algebra can be probed by studying the characteristic polynomials of the Frobenius elements $\text{Frob}_\mathfrak{p}$ acting on the Tate module for primes $\mathfrak{p}$ of good reduction. The roots of the $L$-polynomial of the curve modulo $\mathfrak{p}$ dictate the structure of the endomorphism algebra. This local-to-global principle is central to providing theoretical bounds on the size of the endomorphism ring [cite: 9].

---

## 4. The CMSV Algorithm: Rigorous Computation of the Endomorphism Ring

In 2019, Costa, Mascot, Sijsling, and Voight (CMSV) published a comprehensive algorithm to compute $\text{End}(J)$ rigorously for a curve over a number field. The methodology is split into numerical approximation, lattice reduction, and rigorous exact verification [cite: 1, 2, 13, 18]. Their work remains the engine driving the 2024–2026 discoveries.

### 4.1 Numerical Integration and the Period Matrix

The first stage involves embedding the number field $F$ into $\mathbb{C}$ and approximating the period matrix $\Pi$ of $C$ to high precision. For hyperelliptic curves, CMSV utilized the algorithm by van Wamelen and Molin-Neurohr, which requires identifying the roots of $f(x)$ to find the ramification points of the hyperelliptic map $x: C \to \mathbb{P}^1$ [cite: 15, 17]. 

The homology $H_1(C(\mathbb{C}), \mathbb{Z})$ is generated by loops around pairs of ramification points. To avoid numerical instability near singularities or branch points, the integration paths are carefully deformed using Voronoi cells of the roots. The fundamental group $\pi_1(\mathbb{C} \setminus S, x_0)$ (where $S$ is the set of branch points) acts via deck transformations, and paths are integrated using arbitrary-precision ball arithmetic (often utilizing the Arb library or PARI/GP) [cite: 15]. The resulting period matrix $\Pi = [ \int_{\gamma_j} \omega_i ]$ is accurate to hundreds or thousands of decimal digits. By applying symplectic reduction, one obtains a normalized period matrix $\Pi = (\tau \;|\; I_g)$, where $\tau$ is in the Siegel upper half-space $\mathcal{H}_g$.

### 4.2 LLL Lattice Reduction and Candidate Endomorphisms

With the high-precision period matrix $\Pi$, the goal is to find integer matrices $R \in M_{2g}(\mathbb{Z})$ and complex matrices $M \in M_g(\mathbb{C})$ such that $M \Pi = \Pi R$. Because $R$ dictates the endomorphism completely, one translates this equation into a linear dependency problem over $\mathbb{Z}$. 

By separating the real and imaginary parts of $\Pi$, the condition $M \Pi = \Pi R$ becomes a set of linear equations in the coefficients of $R$. The Lenstra-Lenstra-Lovász (LLL) lattice reduction algorithm is employed to find short vectors in the lattice of approximate relations. An approximately short vector corresponds to a matrix $R$ whose coefficients are small integers. The precision of $\Pi$ must be strictly greater than the expected height of the endomorphism matrices to prevent false positives [cite: 13, 16].

Moreover, the Rosati involution restricts the possible matrices $R$. For any endomorphism $R$, the matrix $R E_0$ must be symmetric if it corresponds to an endomorphism fixed by the Rosati involution (which generates commutative subrings). CMSV restricted their LLL search to matrices satisfying these Rosati-induced symmetries, significantly lowering the lattice dimension and dramatically increasing the speed of the search [cite: 9].

### 4.3 Tangent Representation and Algebraic Correspondence

Once a putative integer matrix $R$ is found, the corresponding complex matrix $M$ is recovered via $M = \Pi R \Pi^+$, where $\Pi^+$ is the pseudoinverse. If this matrix genuinely stems from an endomorphism $\alpha: J \to J$, then $M$ is the pullback action $\alpha^*$ on the space of holomorphic differentials $H^0(C, \Omega^1)$.

However, $M$ and $R$ are merely numerical artifacts. To provide a rigorous mathematical proof, one must construct $\alpha$ algebraically over the number field $F$ (or a finite extension $K$). The endomorphism $\alpha$ corresponds to a divisor (an algebraic correspondence) $Y \subset C \times C$. CMSV defined a method to interpolate $Y$ [cite: 2, 9]. Let $P \in C(K)$ be a base point. The endomorphism maps the divisor class $[P - P_0]$ to another class $\alpha([P - P_0]) = [Q_1 + \dots + Q_g - g P_0] \in \text{Pic}^0(C)$. 

To avoid the complexities of multi-dimensional interpolation, CMSV introduced an infinitesimal approach using formal power series. Let $t$ be a local uniformizer at $P_0$. We can formally expand a generic point $P(t)$ around $P_0$ using Puiseux series in the completed local ring $K[[t]]$. The relation $\alpha([P(t) - P_0]) = \sum_{j=1}^g [Q_j(t) - P_0]$ translates via the formal group law of the Jacobian to a set of differential equations on the formal coordinates of $Q_j(t)$. The matrix $M$ dictates the linear leading terms of this formal integration. By computing the series iteratively (Hensel lifting), CMSV derived exact algebraic expressions for symmetric polynomials in the coordinates of $Q_j(t)$. Finding the annihilating ideal of these expressions proves the existence of the endomorphism over $K$ exactly [cite: 2, 18].

### 4.4 Day-and-Night Algorithm and Upper Bounds

The CMSV paper also outlined a rigorous termination criterion. How do we know we have found *all* endomorphisms? Following an idea of Davide Lombardo, one uses a "day-and-night" strategy [cite: 9, 16].
*   **By Day:** We compute lower bounds. We run the numerical LLL algorithm, find candidate endomorphisms, and rigorously verify them. The algebra generated by verified endomorphisms is a subalgebra of $\text{End}(J_K)$.
*   **By Night:** We compute upper bounds. We calculate the characteristic polynomial of the Frobenius endomorphism modulo multiple primes $\mathfrak{p}$ of good reduction. By Faltings' theorem, the dimension of $\text{End}(J_K) \otimes \mathbb{Q}$ is bounded above by the dimension of the centralizer of the Frobenius elements in the Tate module. 

When the dimension of the verified subalgebra matches the upper bound derived from Frobenius distributions, the algorithm terminates, yielding a certified endomorphism ring [cite: 9, 13]. This algorithm has been implemented in Magma, making it accessible to the broader mathematical community [cite: 17].

---

## 5. Edgar Costa's Advances: Computing Isogeny Classes (2024)

While the CMSV algorithm successfully resolved the computation of the endomorphism ring for a single Jacobian, it naturally led to questions about the broader landscape of abelian varieties. From 2024 to 2026, Edgar Costa, alongside collaborators Raymond van Bommel, Shiva Chidambaram, and Jean Kieffer, tackled the formidable problem of computing entire isogeny classes of abelian surfaces over $\mathbb{Q}$ [cite: 1, 3, 4, 19].

An isogeny is a surjective morphism $\phi: A \to B$ between abelian varieties with a finite kernel. Isogeny defines an equivalence relation. For elliptic curves (genus 1), Mazur's theorem restricts the degree of prime isogenies over $\mathbb{Q}$ to a small finite list ($\ell \le 19$, and $\ell \in \{37, 43, 67, 163\}$). Thus, computing the isogeny graph of an elliptic curve is a finite, highly optimized problem [cite: 20]. However, for abelian surfaces (dimension 2), there is no known analogue of Mazur's theorem bound, and division polynomials for large $\ell$ are computationally prohibitive.

### 5.1 The Algorithm for Isogeny Classes

Costa et al. developed an algorithm [cite: 3, 4] taking as input a principally polarized (p.p.) abelian surface $A$ over $\mathbb{Q}$ whose geometric endomorphism ring is trivial ($\text{End}(A_{\overline{\mathbb{Q}}}) = \mathbb{Z}$). The output is the complete set of p.p. abelian surfaces over $\mathbb{Q}$ isogenous to $A$.

The algorithm operates on the premise that any isogeny $\phi: A \to B$ can be factored. Since we are restricted to p.p. abelian surfaces, the kernel of the isogeny must be isotropic with respect to the Weil pairing induced by the polarization. The possible subgroups in $A[\ell]$ that preserve the principal polarization up to scaling lead to specific types of isogenies, specifically 1-step or 2-step $\ell$-isogenies corresponding to maximal isotropic subspaces.

#### Open Image Techniques and Dieulefait's Tests
To bound the primes $\ell$ for which an $\ell$-isogeny can exist, Costa and his coauthors utilized explicit open-image techniques for Galois representations. If the Galois representation $\rho_{A, \ell}: G_{\mathbb{Q}} \to \text{GSp}_4(\mathbb{F}_\ell)$ is surjective (i.e., has "open image" covering the full symplectic group), then no rational $\ell$-isogeny can exist because a rational isogeny requires a Galois-stable subspace in the $\ell$-torsion [cite: 3, 19].

They applied the criteria of Dieulefait. By computing the $L$-polynomials of $A$ at various primes $p$ of good reduction, one can examine the trace and determinant of the Frobenius element $\text{Frob}_p$ modulo $\ell$. If the characteristic polynomial of $\text{Frob}_p \pmod \ell$ is irreducible and does not fall into specific restricted conjugacy classes of $\text{GSp}_4(\mathbb{F}_\ell)$, one can conclusively prove that $\rho_{A, \ell}$ is surjective. By sifting through a finite list of small primes $p$, the algorithm rapidly eliminates all but a finite, easily manageable set of candidate primes $\ell$ [cite: 3, 19].

#### Igusa-Clebsch Invariants and Siegel Modular Forms
For the surviving candidate primes $\ell$, the algorithm must explicitly construct the isogenous surfaces. Since every p.p. abelian surface with $\text{End}=\mathbb{Z}$ is the Jacobian of a genus 2 curve, Costa et al. framed the search in terms of Igusa-Clebsch invariants $I_2, I_4, I_6, I_10$. These invariants specify the isomorphism class of the genus 2 curve.

The transformation of invariants under an $\ell$-isogeny is governed by Siegel modular forms of degree 2. A genus 2 curve determines a point $\tau$ in the Siegel upper half-space $\mathcal{H}_2$ up to the action of the symplectic group $\text{Sp}_4(\mathbb{Z})$. An $\ell$-isogeny corresponds to moving from $\tau$ to $\gamma \tau$, where $\gamma$ is a matrix in a specific congruence subgroup representing the isogeny kernel. By numerically evaluating Siegel modular forms of weights 4, 6, 10, and 12 at these transformed points $\gamma \tau$ to incredibly high precision, Costa's algorithm generates the Igusa invariants of the target surface $B$ [cite: 20]. 

If the invariants are rational integers (after suitable normalization), they indicate a genuine isogenous surface defined over $\mathbb{Q}$. Mestre's algorithm is then applied to reconstruct the hyperelliptic curve equation from the invariants. This spectacular combination of analytic techniques and algebraic theory allowed Costa et al. to successfully compute the isogeny classes of over 1.4 million Jacobians of genus 2 curves in the LMFDB [cite: 3, 4].

---

## 6. Labeling Abelian Varieties over Finite Fields (2025–2026)

Moving from number fields to finite fields, Edgar Costa, Taylor Dupuy, Stefano Marseglia, David Roe, and Christelle Vincent addressed a critical infrastructural problem in computational number theory: how to unambiguously and permanently label isomorphism classes of abelian varieties over finite fields [cite: 1, 5, 6, 21, 22]. 

### 6.1 Weil Polynomials and Honda-Tate Theory

Over a finite field $\mathbb{F}_q$ (with $q = p^a$), the Honda-Tate theorem states that isogeny classes of simple abelian varieties are in bijection with conjugacy classes of Weil $q$-numbers. Equivalently, the isogeny class is uniquely determined by the characteristic polynomial of its Frobenius endomorphism, known as the Weil polynomial $h(x) \in \mathbb{Z}[x]$. A Weil polynomial of degree $2g$ has all its complex roots on the circle of radius $\sqrt{q}$ [cite: 5, 21].

While the Weil polynomial uniquely identifies the *isogeny class*, an isogeny class typically contains multiple *isomorphism classes* of abelian varieties. Prior to 2025, there was no canonical, algorithmically robust way to enumerate and label these distinct isomorphism classes, causing fragmentation in databases like the LMFDB.

### 6.2 The Deligne Equivalence and Fractional Ideals

To resolve this, Costa et al. utilized Deligne's equivalence of categories for ordinary abelian varieties. An abelian variety $A$ over $\mathbb{F}_q$ is ordinary if exactly half of the roots of its Weil polynomial are $p$-adic units. Deligne proved that the category of ordinary abelian varieties over $\mathbb{F}_q$ in a given isogeny class is equivalent to the category of fractional ideals of a specific commutative order in a product of number fields [cite: 21, 22].

Specifically, let $K = \mathbb{Q}[x] / (h(x))$ be the endomorphism algebra generated by the Frobenius element. This algebra is a product of CM fields. The Frobenius endomorphism generates an order $R = \mathbb{Z}[F, V]$ within $K$, where $V = q/F$ is the Verschiebung. Any abelian variety in the isogeny class corresponds to a fractional $R$-ideal $I$. 

Costa, Marseglia, and coauthors constructed a deterministic algorithm to enumerate the isomorphism classes of these fractional ideals. The algorithm computes the maximal order $\mathcal{O}_K$, identifies all overorders $S$ such that $R \subseteq S \subseteq \mathcal{O}_K$, and computes the Picard group $\text{Pic}(S)$ for each. Because $R$ is not generally maximal, ideal multiplication is complex. They defined weak equivalence classes of ideals and computed their multiplicator rings to exhaustively classify all fractional $R$-ideals up to isomorphism [cite: 5, 22].

### 6.3 Polarization and Practical Labeling (2025)

The 2025 paper "Labeling abelian varieties over finite fields" provides a concrete labeling scheme [cite: 5]. A label is of the form `N.i.w.j`, where:
*   `N` represents the isogeny class (derived from the Weil polynomial).
*   `i` identifies the endomorphism ring $S$ (an overorder of $R$).
*   `w` indicates the weak equivalence class.
*   `j` indexes the exact isomorphism class within the Picard group.

Furthermore, Costa et al. provided labels for the *polarizations* these varieties admit. A polarization on $A$ corresponds to a totally positive purely imaginary element $\lambda \in K$ satisfying specific trace conditions relative to the ideal $I$. By mapping polarizations to elements of the endomorphism algebra, the authors successfully deterministically cataloged polarizations of low degree [cite: 5, 22]. 

In a subsequent 2026 paper, "Ordinary abelian varieties: isogeny graphs and polarizations" [cite: 10], Costa and collaborators expanded this framework to dynamically compute the entire graph of minimal isogenies between these fractional ideals, exploring phenomena in higher dimensions that do not occur for elliptic curves, such as bounds on the diameter of the graph and its decomposition into orbits under the Picard group of the Frobenius order.

---

## 7. Nicolas Mascot's Contributions: Galois Representations and Families of Curves (2024–2025)

Parallel to Costa's work on abelian surfaces and finite fields, Nicolas Mascot focused extensively on the computation of Galois representations and the arithmetic geometry of curves over function fields [cite: 7]. His recent work addresses a deep theoretical and computational challenge: understanding the variations of Galois representations occurring in the étale cohomology of surfaces and families of curves.

### 7.1 Division Polynomials over $\mathbb{Q}(t)$

Let $C$ be a curve of genus $g$ over $\mathbb{Q}$. The action of the absolute Galois group $G_{\mathbb{Q}}$ on the $\ell$-torsion of the Jacobian, $J(\mathbb{Q})[\ell]$, provides a continuous Galois representation $\rho_{C, \ell}: G_{\mathbb{Q}} \to \text{GSp}_{2g}(\mathbb{F}_\ell)$. The image of this representation determines the splitting field of the $\ell$-division polynomial $R_{C, \ell}(x)$, whose roots correspond to the $x$-coordinates of the $\ell$-torsion points [cite: 7, 8]. 

In 2020, Mascot published a highly optimized $p$-adic algorithm to compute these division polynomials by Hensel-lifting torsion points from a finite field $\mathbb{F}_p$ up to $\mathbb{Z}_p$, avoiding complex analytic approximations entirely [cite: 23, 24]. 

In a 2024 preprint, "Explicit computation of Galois representations occurring in families of curves" [cite: 7], Mascot generalized this $p$-adic lifting technique to curves defined over the rational function field $\mathbb{Q}(t)$. A curve $S$ over $\mathbb{Q}(t)$ can be viewed as an algebraic surface fibered over the projective line $\mathbb{P}^1$. The $\ell$-torsion of the Jacobian of $S$ yields a family of Galois representations parametrized by $t$, encoded in a bivariate division polynomial $R_{S, \ell}(x, t) \in \mathbb{Q}(t)[x]$ [cite: 8].

Mascot's generalized algorithm computes $R_{S, \ell}(x, t)$ by treating $t$ as a formal parameter. By working over the ring of formal power series $\mathbb{Q}_p[[t]]$ and employing multivariate Hensel lifting, the algorithm identifies the division polynomials characterizing the entire family. For any specialization $t = t_0$ where the fiber is of good reduction, the polynomial $R_{S, \ell}(x, t_0)$ dictates the Galois action on the specific Jacobian $J_{t_0}$ [cite: 8]. 

### 7.2 Degeneration and Ramification at Bad Fibers

One of the prime motivations for Mascot's 2024 work was to investigate the degeneration of Galois representations at places of bad reduction [cite: 7, 8]. When a curve family degenerates (e.g., acquires a node or a cusp at $t=t_0$), the Jacobian becomes singular, and the Galois representation exhibits specific ramification behaviors governed by the Néron-Ogg-Shafarevich criterion.

By computing the division polynomials globally over $\mathbb{Q}(t)$, Mascot was able to explicitly factor $R_{S, \ell}(x, t)$ over the field of Laurent series $\mathbb{Q}((t - t_0))$ near a bad fiber. This local resolution via Puiseux expansions allows for the precise determination of the inertia group action at the bad fiber. This approach provides a computationally explicit proof of abstract cohomological properties of algebraic surfaces, particularly in isolating mod-$\ell$ representations within the second étale cohomology group $H^2_{\text{ét}}(X, \mathbb{F}_\ell)$ of a surface [cite: 7, 8]. Although the resulting division polynomials for surfaces proved formidably large, the algorithm successfully isolated representations over $\mathbb{P}^1_{\mathbb{Q}}$ with controlled ramification, including representations attached to modular forms over congruence subgroups of $\text{SL}(3)$ [cite: 7].

---

## 8. Mascot's Algorithmic Desingularization and Riemann-Roch Spaces

The computation of geometric properties of curves—whether for endomorphism rings, division polynomials, or simply integrating algebraic functions—frequently encounters the problem of singularities. Plane algebraic curves defined by a polynomial $F(x, y) = 0$ over a field $K$ naturally possess singular points where the partial derivatives vanish. Most theoretical constructions (like the Jacobian) demand a smooth, projective model of the curve [cite: 8, 11].

In 2024 and 2025, Nicolas Mascot presented streamlined algorithmic approaches to the desingularization of plane algebraic curves and the computation of Riemann-Roch spaces [cite: 11, 12, 25].

### 8.1 Puiseux Expansions and Local Parametrizations

To desingularize a curve $C$, Mascot's algorithms bypass the traditional, computationally heavy technique of iterative blowing-up. Instead, they rely on computing local parametrizations via Puiseux series. At a singular point $P = (x_0, y_0)$, the polynomial $F(x, y)$ is analyzed over the completion $K((x - x_0))[y]$. By utilizing the Newton-Puiseux algorithm, the polynomial is factored into linear terms of the form $y - \sum c_i (x - x_0)^{q_i}$, where $q_i$ are rational numbers [cite: 12]. 

These fractional power series provide a bijective map between the branches of the smooth completion $\tilde{C}$ and the singularity on $C$. Mascot implemented these local parametrizations efficiently in PARI/GP. This representation is deeply integrated into the computation of the genus, where the number of branches and their intersection multiplicities directly feed into the Riemann-Hurwitz formula [cite: 12].

### 8.2 Computing the Riemann-Roch Space

The Riemann-Roch space $L(D)$ for a divisor $D$ on $\tilde{C}$ is the vector space of rational functions $f \in K(C)$ such that the divisor $(f) + D$ is effective (non-negative). Finding a basis for $L(D)$ is essential for executing the group law on the Jacobian (via Khuri-Makdisi's or Cantor's algorithms) and for exact algebraic verification in the CMSV endomorphism algorithm.

Mascot's strategy constructs $L(D)$ by precomputing the integral closure $\mathcal{O}_C$ of $K[x]$ within the function field $K(C) = K(x)[y]/(F(x,y))$. By determining a common denominator $d(x) \in K[x]$, any function $f \in L(D)$ can be written such that $d(x)f(x, y) \in \mathcal{O}_C$ [cite: 12]. The local Puiseux parametrizations are evaluated at the poles defined by $D$. Linear algebra over $K$ is then used to find the specific combinations of functions whose polar parts vanish at the required orders. This algebraic-analytic hybrid method proves highly robust across arbitrary characteristic-zero fields [cite: 12].

### 8.3 Application: Integration of Algebraic Functions

In a 2025 presentation at the University of Tor Vergata [cite: 11], Mascot demonstrated an unexpected application of these algorithms: the exact integration of algebraic functions. The seemingly calculus-based problem of finding the antiderivative $\int y(x) dx$ for an algebraic function $y$ satisfying $F(x, y) = 0$ is deeply connected to arithmetic geometry.

An algebraic function has an elementary antiderivative (involving only rational functions and logarithms) if and only if the differential $y dx$ corresponds to a divisor that is torsion in the Picard group of the curve. By utilizing the desingularization and Riemann-Roch algorithms to test whether specific divisors are torsion (via efficient addition in the Jacobian), Mascot established a complete integration algorithm for algebraic functions based purely on arithmetic geometry [cite: 11]. 

### 8.4 Forcing Positive Mordell-Weil Rank (2024)

In another short but highly impactful note in 2024, Mascot provided a novel trick to ensure that the Jacobian of a smooth curve over a number field has a strictly positive Mordell-Weil rank [cite: 23]. The Mordell-Weil theorem states that $J(F)$ is a finitely generated abelian group, $J(F) \cong \mathbb{Z}^r \oplus J(F)_{\text{tors}}$, where $r$ is the rank. Finding curves with specific ranks is notoriously difficult.

Mascot proved that if a smooth curve has a rational divisor class of degree 1, no rational non-trivial 2-torsion, and no rational theta characteristic, then the Mordell-Weil rank of its Jacobian must be at least 1 [cite: 23]. He utilized his division polynomial algorithms to compute the étale algebra of the Galois set of torsion points, creating explicit families of curves where the rank is guaranteed to be strictly positive without having to explicitly search for points of infinite order.

---

## 9. Advanced Theoretical Context: K3 Surfaces and Modularity

The techniques developed for hyperelliptic Jacobians do not exist in isolation. They are intrinsically linked to the study of K3 surfaces, complex multiplication, and modularity, areas heavily researched by Edgar Costa from 2024 to 2025 [cite: 1, 14].

### 9.1 K3 Surfaces and the Picard Lattice

A K3 surface $X$ is a simply connected complex surface with a trivial canonical bundle. Like abelian surfaces, K3 surfaces possess a rich intersection theory. The second cohomology group $H^2(X(\mathbb{C}), \mathbb{Z})$ is a lattice of rank 22 equipped with an intersection pairing. The algebraic cycles on $X$ form the Néron-Severi group, or Picard lattice, $\text{Pic}(X)$. The rank of the Picard lattice, $\rho(X)$, ranges from 1 to 20 over $\mathbb{C}$. 

Costa's research involves computing the Picard lattice explicitly. Similar to the endomorphism algebra of a Jacobian, the Picard lattice can be constrained by local information. Costa uses controlled reduction in $p$-adic cohomology (like the trace formula of Harvey) to compute the zeta functions of the reduction of $K3$ surfaces modulo finite primes [cite: 1]. The Frobenius traces yield upper bounds on the geometric Picard rank. 

### 9.2 The Kuga-Satake Construction

A profound link between K3 surfaces and abelian varieties is provided by the Kuga-Satake construction. For a polarized K3 surface $X$, the Kuga-Satake construction associates a complex abelian variety $A$ of dimension $2^{19}$ such that there is an embedding of Hodge structures connecting the transcendental lattice of $X$ to the cohomology $H^1(A) \otimes H^1(A)$ [cite: 1, 14]. 

Even though this construction is theoretically central to proving the Weil conjectures for K3 surfaces and exploring their modularity, finding explicit equations for the Kuga-Satake abelian variety is formidably complex. In a 2025 paper with Elsenhans, Jahnel, and Voight, Costa explored explicit examples where K3 surfaces with complex multiplication (CM) are related to hyperelliptic Jacobians of low dimension (specifically abelian threefolds) that also possess CM [cite: 1, 14].

By assuming CM, Costa matched the transcendental motives of the K3 surfaces to explicit algebraic Hecke quasi-characters. These characters dictate the $L$-function. By comparing the Hecke characters of the K3 surface to those of specific hyperelliptic Jacobians, Costa provided substantial, rigorous evidence that a power of the hyperelliptic Jacobian $A$ corresponds exactly to $X$ under the Kuga-Satake correspondence. This represents a monumental step in making the abstract Kuga-Satake correspondence explicit and algorithmic [cite: 1, 14].

---

## 10. The L-functions and Modular Forms Database (LMFDB)

The overarching goal of the algorithms created by Costa, Mascot, Sijsling, and Voight is not just abstract computation, but the compilation and structuring of mathematical knowledge. All of the discussed innovations (endomorphism ring certification, isogeny classes of abelian surfaces, labeling of finite field varieties) funnel directly into the **L-functions and Modular Forms Database (LMFDB)** [cite: 1, 5, 21, 26].

The LMFDB is a vast, interconnected digital atlas of mathematical objects—number fields, algebraic curves, abelian varieties, $L$-functions, and modular forms. The Langlands program posits deep, unifying symmetries between these distinct classes of objects. For instance, the $L$-function of a genus 2 curve over $\mathbb{Q}$ is conjectured to match the $L$-function of a degree-2 Siegel modular form [cite: 20, 26].

The lack of empirical data has historically hindered the precise formulation of the Langlands program's broader predictions. The algorithms from 2024 to 2026 populate the LMFDB with provably correct, certified arithmetic data [cite: 1]. 
*   **Costa's Isogeny Data:** The 1.4 million isogeny classes of abelian surfaces computed by Costa, van Bommel, Chidambaram, and Kieffer provide the geometric side of the Langlands correspondence for genus 2 [cite: 3, 4].
*   **Finite Field Labels:** The deterministic labels for abelian varieties over finite fields (Costa, Dupuy, Marseglia, Roe, Vincent) allow researchers to search the database using a uniform language, connecting Weil polynomials directly to algebraic structures [cite: 5, 6].
*   **Mascot's Galois Representations:** The polynomials parameterizing Galois representations provide explicit polynomials with specific, controlled Galois groups (like $\text{PSU}(3, 9)$) and constrained ramification behavior, contributing to inverse Galois theory and the database of number fields [cite: 7].

---

## 11. Synergistic Implementations: Magma and PARI/GP

A critical aspect of the 2024–2026 period is the maturation of the software implementation of these theories. Advanced arithmetic geometry relies heavily on two primary computer algebra systems: Magma and PARI/GP [cite: 7, 15, 17, 23].

### 11.1 The Magma Ecosystem
The original CMSV algorithm for the rigorous computation of the endomorphism ring was implemented in Magma, leveraging Magma's powerful arbitrary-precision real and complex arithmetic (the `AnalyticJacobian` package developed originally by Paul van Wamelen) alongside its robust LLL and lattice reduction routines [cite: 13, 15, 17]. Costa's later algorithms for searching isogeny classes also relied heavily on Magma for evaluating Siegel modular forms and executing Mestre's algorithm to reconstruct curves from Igusa invariants [cite: 4, 20].

### 11.2 Mascot's PARI/GP Branch
Nicolas Mascot has been a major contributor to the open-source system PARI/GP. His $p$-adic algorithms for Hensel-lifting torsion points, computing division polynomials, and his recent 2024–2025 algorithms for desingularizing plane algebraic curves and calculating Riemann-Roch spaces have been actively developed in a custom branch of PARI/GP (the "nicolas-KKM" branch and the `LiftTors` repository) [cite: 7, 12, 23]. 

Mascot's algorithms notably utilize Makdisi's moduli-friendly Eisenstein series. In his research to compute Galois representations occurring in the torsion of Jacobians of modular curves, Mascot adapted his $p$-adic method to evaluate modular forms at $p$-adic points. This brilliant maneuver dispenses with the need for explicit, highly complex algebraic equations for modular curves or expansive $q$-expansion computations, drastically increasing the speed compared to complex-analytic approaches [cite: 7].

---

## 12. Deep Dive: The Mathematics of the CMSV Verification (Formal Expansion)

To fully appreciate the rigor underlying these developments, we must look deeply into the exact certification step of the CMSV algorithm, which transforms a floating-point endomorphism matrix into an absolute, proven geometric truth [cite: 2, 9, 18].

Recall we have a curve $C: y^2 = f(x)$ and a candidate endomorphism represented by a matrix $M \in M_g(K)$ acting on the holomorphic differentials $\omega_i = x^{i-1} dx / y$. We know $M$ is correct up to 1000 decimal places, but that is not a mathematical proof. 

Let $P_0 = (x_0, y_0)$ be a rational point on $C$. We take a local parameter $t$ at $P_0$. For example, if $y_0 \neq 0$, we can choose $t = x - x_0$. The curve coordinate $y$ can be expressed as a formal power series $y(t) \in K[[t]]$ by substituting $x = t + x_0$ into $y^2 = f(x)$ and extracting the formal square root using Hensel's lemma. This yields the formal point $\tilde{P}(t) = (x(t), y(t))$.

The putative endomorphism $\alpha$ acts on the divisor class $[\tilde{P}(t) - P_0]$. Because the Jacobian is of dimension $g$, by Jacobi's inversion theorem, there exist exactly $g$ points $Q_1, \dots, Q_g$ on the curve such that:
\[ \alpha([\tilde{P}(t) - P_0]) = [Q_1(t) + \dots + Q_g(t) - g P_0] \]
The coordinates of $Q_k(t) = (x_k(t), y_k(t))$ are themselves formal power series (typically Puiseux series, meaning they may involve fractional powers of $t$).

By taking the derivative with respect to $t$ on both sides and applying the chain rule to the Abel-Jacobi map, one obtains the identity on differential forms:
\[ M \begin{pmatrix} \omega_1(\tilde{P}(t)) \\ \vdots \\ \omega_g(\tilde{P}(t)) \end{pmatrix} = \sum_{k=1}^g \begin{pmatrix} \omega_1(Q_k(t)) \\ \vdots \\ \omega_g(Q_k(t)) \end{pmatrix} \]
This is a system of nonlinear differential equations. Because the matrix $M$ is known exactly over the number field $K$, one can expand both sides as power series in $t$ and equate coefficients order by order.

The algorithm proceeds by undetermined coefficients. The lowest-degree terms of $x_k(t)$ are determined by finding the roots of a specific polynomial over $K$. Once the leading terms are found, the higher-order coefficients are determined by solving a sequence of linear Vandermonde systems [cite: 13, 18]. 

Once the series $x_k(t)$ and $y_k(t)$ are computed up to a precision $O(t^N)$, CMSV construct symmetric polynomials in the roots, specifically the polynomial $E(x) = \prod_{k=1}^g (x - x_k(t))$. By Newton's identities, the coefficients of $E(x)$ are formal power series in $t$ with coefficients in $K$. Remarkably, because $\alpha$ is a genuine algebraic endomorphism, the relation between the base point $x$ and the symmetric functions of the target points $x_k$ must be an algebraic rational function. By applying Padé approximation or recognizing linear recurrences, the truncated power series perfectly reconstruct the exact rational functions defining the endomorphism algebraic correspondence $Y \subset C \times C$ [cite: 2, 9]. The vanishing of the ideal defining $Y$ under the endomorphism constraints provides a rigorous, 100% certified proof of the endomorphism.

---

## 13. Future Directions and the 2026 Horizon

As of 2026, the trajectory established by Costa and Mascot points toward several highly ambitious open problems in arithmetic geometry.

### 13.1 Generalizing to Higher Genera and Non-Hyperelliptic Curves
While the CMSV algorithm is technically applicable to any curve, highly optimized implementations currently exist primarily for hyperelliptic curves. Mascot's recent work on desingularizing plane algebraic curves [cite: 11, 12] paves the way for efficient period matrix computations and formal series expansions on *smooth plane quartics* (genus 3) and higher-degree non-hyperelliptic curves. Costa has already begun publishing on counting points on smooth plane quartics in average polynomial time [cite: 1, 27], signaling a shift toward systematizing non-hyperelliptic data in the LMFDB.

### 13.2 Machine Learning in Number Theory
A fascinating development in Costa's recent publication list (2025–2026) is the integration of machine learning into arithmetic geometry. His recent preprints involve "Murmurations, Mestre-Nagao sums, and Convolutional Neural Networks for elliptic curves" and "Machine learning the vanishing order of rational L-functions" [cite: 27, 28]. This interdisciplinary approach suggests that neural networks are being trained on the vast datasets generated by the algorithms discussed in this report to detect hidden patterns (murmurations) in the coefficients of $L$-functions and modular forms, potentially guiding new theoretical conjectures in the Langlands program.

### 13.3 Cohomology of Constructible Étale Sheaves
Mascot's algorithms for division polynomials over $\mathbb{Q}(t)$ represent the first step in explicitly computing the cohomology of constructible étale sheaves over surfaces. As demonstrated in 2025 research schools [cite: 25], isolating Galois representations in the second étale cohomology group $H^2_{\text{ét}}$ of a surface remains an intensely active area. The ultimate goal is to provide a unified computational framework for the full étale cohomology of arbitrary algebraic varieties, bridging the gap between Grothendieck's abstract topological formalisms and explicit, bit-level computer algorithms.

---

## 14. Conclusion

The rigorous computation of the endomorphism algebra of a Jacobian, initiated as an abstract query, has evolved into one of the most dynamic and fruitful domains of computational arithmetic geometry. The 2019 framework laid by Edgar Costa, Nicolas Mascot, Jeroen Sijsling, and John Voight demonstrated that high-precision complex analytics could be seamlessly married to rigorous $p$-adic and algebraic verifications. 

Between 2024 and 2026, the field has undergone a rapid expansion. Edgar Costa's derivation of complete isogeny classes for principally polarized abelian surfaces and his deterministic labeling schemes for abelian varieties over finite fields have provided structural clarity to the chaotic landscape of higher-dimensional arithmetic. Simultaneously, Nicolas Mascot has cracked open the computational boundaries of Galois representations, pushing $p$-adic algorithms into families of curves over function fields and redefining the algorithmic handling of singular algebraic curves. 

These advancements transcend mere computational exercises; they populate the LMFDB with the raw empirical data required to probe the deepest unproven symmetries of mathematics, from the Sato-Tate conjecture to the Langlands program. As computational power grows and algorithmic theories mature, the work of Costa and Mascot continues to illuminate the profound geometric truths hidden within the arithmetic of equations.

**Sources:**
1. [edgarcosta.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlj_rb81IIE0FjH0Hvb9X6aZ4cYTciLzlVI-RDHGW7fBUZtMQZx9SYOsdHtSzm6faq59YHOSAae0j4XPI3bpuZL7--HeO5Lw6lId-R_0J5DVLc0MQI8EhDKNB7AqyEpN3Lse951A==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1RTmh636srhyVxwaum2uF_s3BIqMm9GkuBJ4vIZcG3XKjCnz-LFmvvOJtkvqfJCpFGslM1e0zkqkryoliakq2ONar-kUugPhX7lmMry6-2R8K_pI03Q==)
3. [wisc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiNPENNq3O8f40BhFNLv0--jVL7nFGiWri6al2qTctXPd2f4pEHszrpALToaNRyV1uVov998erDOnvdxRf_fJMEJQf8sfCqNGQ5eFbRoRFq12BacCfYY7UHQ5dF1dzGa4wxmOEkP_zOEEqsXw2JwOW4v5Mgdy6pne0hCLNnkoK4wo=)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdwmZHVQFcLlXvVA3F5UZv7TtmEtusu3ayb6cltup7fxUkPLRXhLcnQRW5JobuyMhGoQVPKQRCPXYEtvyBircq_mScze8v1dkWZcXyH6o4jKL50iKvDg==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2G-dvgPLngN6H5xtH_eev3ZMTozvMSju8c16oOqgEVc-bXRI7qqwmnD5aY6--FSwosMmgViS-wd-8wZLYuFVvTJZ7tm8iZBOUQbxNbMeEg6p98LTWfQ==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUQzI063AVopK4sm58S7_5IcSTbFBNaz2lhf72f7VqQqD_PUJWItPC40at4fX-YkMK7dqXL_bHaLrv64W5fKQ4fswLAJcCDIyhNBOsAVRzdL3ZAvScWw==)
7. [tcd.ie](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMocb0DQ9YibbikkDRqnJHSABZ5ToFfgzQPE6M3-2ROGwzqI22rve7SBN4L94RFSVz41WtlUYM-MSG9GLPIPqlO_pbXTxL8cgeDqWViQC_jcP9V4K0J8u1)
8. [u-bordeaux.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwLrNcQ9os41ClRKKqH76DJn9vUBEBM4xUNf5wjNnxTSmbOEpDrqi1DVYXVz1ODGPMFvPL6HAxOnjb775dl3zdJHQjKJZGNu5_Hk4Ypxx_7GKuL5I8GUYpk5VnW2EXr0qqBZFjLEw9Hym6fap-1aFuBUglZeWiNA==)
9. [aub.edu.lb](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHslZsVAPNaqyLMYzvCW6NVsI4CZfT5JayfahXQt_2TgJl_Gj5YogzBntmPXb-WjPCQBFYP-hYZ6xMMDJG2WOR0iQjnEiNuoBSwwd0Yiw3K7sbXm851koU_G0PB94cnj8l2i3ZvnObx7FOgdPtBvyrmHOptZWQ-cavvx1FZrPQF2ENj16IhNTjreNWSxtDm)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHW_eeK1aeAFojtDWJplIpX240TTJX80AMnLyyjqn92dvPKBr0pEdxlumCeuavHhJCwcWIcChrZcroQ8qRrZjs7_VsLy9rOChjTWT5eyAlNvUgERn-Biw==)
11. [uniroma2.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHt_3Pk9LK_cLgYCt4d8aA4QqAtB7CIZNVBiecMA_UoJhTpwgkE8oZiQeydLRSe-ErcW17-DonR_TneERqgr_9A_eqSbPUyayPNZR63UJCEmpike_RE1NBHntYYhXXORucMGSLwKMxH8vUOSN3yGpx3yf1Wawz2YUXtHHbqOq5UMT8wul-VQLnDidE=)
12. [u-bordeaux.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCWZbweWIHdpp76_cqHPFwQAei40ohJny9h1vyI2FnGpy4paX2vwnPtdFwm-ycywSRIpSTY1UeVnAkpfw7er1vmRk3Kno-fy8rPOgWr1ZeAl9m3NjCMSLXEJaXTVlSv2D4KygDoAcnK1WYqfS16yJiTDVvFtj5kiGHGQ==)
13. [lebesgue.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFc23gpFweq9XNGc7weg8rQq6QsN22mHLHM2wOztBYdE7do9kPhT-3NWMuaig_PAXp4iqpXG1lEqH3dN380P7ms1oHuFCNiw9eAJySAEbr1ewtoyoxkt1RX0uwtY9uTQ0-aRS3DxzIK56lf_-wAPqOdqAVlS_c=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXwVu-oKB3IYv1ANu5E9xF-W4kXzXHxkR3BN1nDb6_C_fdN0zxXZ7VAQjwilJEzM3u5N6ay5d2E1b04PsnPxAFf4PkzDE-QkSFTFrgMN8Dy4iQ8ZOPfQ==)
15. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErpjC6g5-D4TwXcD4rSzyfDbRwReZtMYDVKWQ6hTLV___MslNo3Q2a-1J37ysqcV35dBOc7T3S9XvgSO2K7QxIO8Bp3bZYME8i3MDKMhD0Et2Y38vICzzHABSye3ukdIma_QfZJy0=)
16. [bris.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9ZaDrKUMzCI-VUiG9lwcFGuFTLfX4zWStxNNmRRYlbemXitnGvIarTfKz3ktobBOSIC561Lp5qvCCQ-TyAgvwKcg9SEl-qtYu5GBXy3L-dP_l0aC35HMKdEdFUke3oHu4rGbeXS1vcb5npjkKrT6oeDJEGDNe2gW6iQ==)
17. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxkG9vfP-qoNJEqZdAE-3YFb3FZQmj-h7kUMN7bpsen7ZWvLKwNhvXKmw5VEe3EpdWGBLjHQb9amaRwspPqau_So1vjzVn7qEf7cPNmW3opc3B5GljXFxWOwpcRuvsZaSfFxAk24d96tn54M8tUmeVuY8KZr0M149KrA9JcozlLA0dljNjAx1p9je4ZWalgg0BacdQPOw=)
18. [bris.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9uwiQdV3qZU2a-FL672P2bUj8w9HtPMlHZC48MoZF5p0fYy3dItV4gxxoe764w2Hv43WDoTthZ8avxNxqp1Njv7WLHHPcN2oEU54Sup1JMSjrAy5KQ3F-GrwueuNJMl0CZbEMIf9E-Q95NIcT5RzxXX-cj4gaJIeLJxWqU82WD05j1Zd4G1d7WeGO9QIeHoWFRw1-QK-6Ox_Op91MbcaBkJ7g)
19. [edgarcosta.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZfoH421f5U5T5LADeq0_K1QtawWt1PArS3Dl-p8xflI82cswn2jJDX9Eq_4BbJIWKu0BIu9LA1JuoPXMlAEXpIGx4xK-uK5NBkmxyFhm1mpFWwu84-QZpt1xgvlNXgBXWho8cyo1aiQ==)
20. [edgarcosta.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0EehHUcWSp-FHh7yovWQE9L96EVFMn-X5GtiTd9Ltjtv5EKk0Fdb14r67p9N7yqzeSjoh4n2K3lKWu0IqtCyu3wDjF7CV0GdWoLtA3RdH8SvKgrvc7vWE79wAI0JzbQN1TBzwsgV_)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMBt236GRE6OEIj-FHFJuj4a9LCzgvYfYJ5FSvvdWG7rL0JL7DjGShR7Zx1oUAaF3PmRBqkTp--8nsxxvCzKnqj6oW2pm-ARNcJ7oLzCr2g1RIyt9ceKYW_WR1i_MdiVG0sGNbrAMf4xb2KaKRqGFKljilrWs2BdoZpqYXCBhBVWh6eQxD1DN7UexmWvU4j1aE1Pi8UTc=)
22. [lucant.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQ8onQMUgQxVuzXTXwiNJ6ad7D5AMkM4gzHQQ3fsAzVhajawztU1ogB4tPwlUYuB4oymlowH9U2jQzvz-vOUih9-Z2iYTvZIScA5YS8u_9s9Gr65QSSavjUi1B7TmuvgPNO2emZA==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8ICE47xx4JFcnAE1xpjmyuJyj5YbcBjJM22h5g8n9nETY2hN4AdZSaSfNxTaxrcvoizOjjZhsURhmfLAu841Ct7OwEgoZBBC-5cMRxqxRnsZJsqp-TQ==)
24. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFR78NansZQ8vBS5BUW5Tx6Abo3oVjEB5olsKURkKLEQY3uiHKGvOnad58bcVuAi5cS26uU8BLNAWDY-Mj3Dl72Nv5BY_QIvyj3TcrrLSqxuErzi8Owhm_54Zus7jOODM5ajXLgnAI541esyxv6SPf8sWQ=)
25. [femto-st.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMk4QS6EsegInOYjtZ82dWJZvGeT4bj2y91tOO_MQGUnetsfcvfENEEwvuEofk_6IRgJeFlYt-YWsTR7LzHvVR58lOXMX_ef83Pej8E1Nmu2ZOlUaMwvUuclHBmvL3FrITVk004VbDYH3DE_r1pKMIR2gmNNzf8Lq-azRHJ_rGAwA0xQBulN8-RUtWa2ql94e2U7FhvDMGrRupiyq1mcpkFGVtvKWgKNczNb1wmYKaK9pUmXaIBfIM5cVfbH7LgF_KUaITby01dnynoA==)
26. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0hlVEF1DgLVwTiLy2VaXwBw3zQnI8k6X3UWugvWXWSQRiA0vQShpIllQCR79q9KOjO9YVeZ6TdBQMvHefBibFEjg4M_Hi3cEGzJEQ8BUretNkeFjENNQ-cj4q-LC3oP9bd8Eh7Te34hY4zcBDl4s=)
27. [edgarcosta.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4KAcgx68Ji80sjcDugTTsJzpvQQpegyFVlXXSZVQNoMzEuOFi5d4I1PAfWFyK0zBG_hGsnS_ixwtPouP3ivAz8tt_Us7vsgCmhq-qRySrv8wtTy9e)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSA95HlvDh25qXylOiYmvlDwmPs2QzsgsOKAxYpPnaFgtU5KU-WU_ie8xOfoZ0olY1_Dl4kb9Zl7_NlCG7yGjQfKBfGS7mPynvrwWqnkpuo8ee7g==)

