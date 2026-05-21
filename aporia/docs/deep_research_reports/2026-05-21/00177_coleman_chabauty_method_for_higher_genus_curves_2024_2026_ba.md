# Coleman-Chabauty method for higher genus curves 2024-2026 (Balakrishnan, Triantafillou)

**Pythia queue id:** 177
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdManNQYXRhOEJJU2wxTWtQX3RpSTRRNBIXTGpzUGF0YThCSVNsMU1rUF90aUk0UTQ
**Elapsed:** 314s
**Completed at:** 2026-05-21T17:10:01.032052+00:00

---

# The Coleman-Chabauty Method for Higher Genus Curves (2024-2026): Advances by Balakrishnan, Triantafillou, and Collaborators

**Key Points:**
*   The classical Coleman-Chabauty method effectively computes rational points on higher genus curves but is strictly limited by the rank-genus inequality \( r < g \).
*   **Quadratic Chabauty**, spearheaded by researchers including Jennifer Balakrishnan, extends this boundary to \( r = g \), utilizing \( p \)-adic heights and geometric correspondences. 
*   Nicholas Triantafillou has pioneered the theoretical boundaries of **Restriction of Scalars (RoS) Chabauty**, identifying Base-Change-Prym (BCP) obstructions that explain why certain curves fail to yield finite rational point bounds over number fields.
*   Recent breakthroughs (2024-2026) include the successful computation of rational points on high-genus modular curves, notably settling Galbraith's conjecture for Atkin-Lehner quotients and pushing computational limits toward the genus 8 non-split Cartan modular curve \( X_{ns}^+(19) \).
*   The research relies heavily on computational number theory, uniting deep algebraic geometry (such as \( p \)-adic Hodge theory) with algorithmic implementations in SageMath and Magma.

**Overview**
The quest to find all rational points on curves of higher genus (\( g \ge 2 \)) is a central problem in arithmetic geometry. While Faltings' theorem guarantees that the number of such points is finite, it provides no algorithm to find them. The Coleman-Chabauty method and its non-abelian extensions offer a partial, yet powerful, solution using \( p \)-adic analysis.

**The Rank-Genus Challenge**
Classical Chabauty requires the Mordell-Weil rank \( r \) of the curve's Jacobian to be strictly less than the genus \( g \). When \( r \ge g \), new techniques are necessary. Quadratic Chabauty and Restriction of Scalars Chabauty have emerged as the primary frameworks to tackle these cases, leveraging higher-level \( p \)-adic cohomology and base-field extensions.

**Current Breakthroughs**
Between 2024 and 2026, algorithmic advancements have made these non-abelian methods remarkably explicit. Teams led by Jennifer Balakrishnan and Nicholas Triantafillou have not only mapped the theoretical obstructions but have effectively computed the rational points on previously intractable modular curves, providing a constructive pathway toward the effective Mordell conjecture.

## 1. Introduction and Historical Context

The study of rational points on algebraic curves over number fields is an ancient and profound branch of Diophantine geometry. For a smooth, projective, geometrically irreducible curve \( X \) over the rational numbers \( \mathbb{Q} \) with genus \( g \), the geometric properties of the curve dictate the arithmetic nature of its set of rational points, \( X(\mathbb{Q}) \). When \( g = 0 \), the curve has either no rational points or infinitely many (parameterized by a projective line). When \( g = 1 \), the curve (if it has a point) is an elliptic curve, and its rational points form a finitely generated abelian group, as proven by Mordell. 

For higher genus curves (\( g \ge 2 \)), the celebrated Mordell conjecture stated that the set \( X(\mathbb{Q}) \) is always finite [cite: 1]. This conjecture was proven in a monumental 1983 paper by Gerd Faltings, utilizing the theory of abelian varieties, moduli spaces, and Galois representations [cite: 1, 2]. However, Faltings' proof relies on the finiteness of certain isogeny classes and is strictly ineffective; it does not provide an algorithm, bound, or constructive method for explicitly determining the finite set \( X(\mathbb{Q}) \) [cite: 1, 2]. 

The search for an "Effective Mordell Conjecture" led mathematicians back to an earlier, \( p \)-adic analytic approach pioneered by Claude Chabauty in 1941 [cite: 1]. Chabauty's method embeds the curve \( X \) into its Jacobian variety \( J \) using an Abel-Jacobi map \( \iota: X \hookrightarrow J \) defined by \( P \mapsto [(P) - (b)] \) for a fixed base point \( b \in X(\mathbb{Q}) \) [cite: 1, 2]. The Jacobian \( J \) is a \( g \)-dimensional abelian variety. By the Mordell-Weil theorem, \( J(\mathbb{Q}) \) is a finitely generated abelian group, meaning \( J(\mathbb{Q}) \cong \mathbb{Z}^r \oplus J(\mathbb{Q})_{\text{tors}} \), where \( r \) is the Mordell-Weil rank. 

Chabauty observed that if the rank \( r \) is strictly less than the dimension \( g \) of the Jacobian (\( r < g \)), the \( p \)-adic closure of \( J(\mathbb{Q}) \) inside the \( p \)-adic Lie group \( J(\mathbb{Q}_p) \) has positive codimension [cite: 2, 3]. Consequently, the intersection of this closure with the one-dimensional curve \( X(\mathbb{Q}_p) \) is finite. In 1985, Robert Coleman made Chabauty's method explicit by introducing a theory of \( p \)-adic integration (now known as Coleman integration). Coleman showed that one can find annihilating \( p \)-adic differentials—specifically, regular 1-forms \( \omega \) on \( J(\mathbb{Q}_p) \) that vanish on \( J(\mathbb{Q}) \) [cite: 1, 2]. The integrals of these forms yield locally analytic functions on \( X(\mathbb{Q}_p) \) whose finite set of zeros necessarily contains the set of rational points \( X(\mathbb{Q}) \) [cite: 1, 2]. 

Despite its elegance, the classical Coleman-Chabauty method faces a rigid theoretical barrier: it simply cannot be applied when \( r \ge g \) [cite: 2, 3]. For decades, curves violating this rank condition remained largely out of reach for exact point computation. However, the modern era of arithmetic geometry has seen the development of Minhyong Kim's non-abelian Chabauty program, which replaces the abelian Jacobian with non-abelian geometric objects (Selmer varieties) associated with the unipotent fundamental group of \( X \) [cite: 3]. 

The most computationally successful instance of Kim's program is the **Quadratic Chabauty** method, which operates when \( r = g \) (and occasionally \( r \ge g \) under specific geometric conditions) [cite: 2, 4]. From 2024 to 2026, researchers such as Jennifer Balakrishnan and Nicholas Triantafillou have pushed the limits of Quadratic Chabauty and a related technique, **Restriction of Scalars (RoS) Chabauty**, creating highly explicit algorithms to resolve the rational points of critical modular curves. This report provides an exhaustive detailing of the theory, algorithms, and results surrounding these developments.

## 2. Theoretical Framework of Advanced Chabauty Methods

### The Coleman-Chabauty Method and its Limitations

To understand the advances of 2024-2026, one must precisely formulate the classical Chabauty-Coleman approach. Let \( p > 2 \) be a prime of good reduction for \( X \). Let \( \Omega^1_{X/\mathbb{Q}_p} \) denote the space of regular 1-forms on \( X \). The integration of these forms yields the Coleman integral, an analytic function on the residue disks of \( X(\mathbb{Q}_p) \) [cite: 2]. 

When \( r < g \), linear algebra over \( \mathbb{Q}_p \) guarantees the existence of a non-zero differential \( \omega \in H^0(X_{\mathbb{Q}_p}, \Omega^1) \) such that for all \( x \in X(\mathbb{Q}) \), the integral vanishes:
\[ \int_b^x \omega = 0 \]
This equation defines the Chabauty-Coleman set \( X(\mathbb{Q}_p)_1 \), which is a finite superset of \( X(\mathbb{Q}) \) [cite: 2, 5]. Combining this local \( p \)-adic data with the Mordell-Weil sieve (which uses reduction modulo various primes to restrict the possible residue classes of rational points) typically allows one to determine \( X(\mathbb{Q}) \) exactly [cite: 3, 6].

When \( r \ge g \), the space of such annihilating differentials is trivial. The Chabauty-Coleman set \( X(\mathbb{Q}_p)_1 \) ceases to be finite, and the method fails entirely [cite: 3].

### Kim's Non-Abelian Chabauty Program

To bypass the \( r < g \) condition, Minhyong Kim proposed using unipotent quotients of the \( p \)-adic étale fundamental group of \( X \) [cite: 3]. In this framework, the classical Chabauty-Coleman method corresponds to the first tier of a tower of Selmer varieties [cite: 3]. Instead of single Coleman integrals, Kim's method utilizes iterated Coleman integrals of the form \( \int \omega_n \cdots \omega_1 \) [cite: 1, 2]. 

For each depth \( n \), one defines a Chabauty-Kim set \( X(\mathbb{Q}_p)_n \). The case \( n=1 \) recovers the classical linear Chabauty method. The case \( n=2 \) is known as **Quadratic Chabauty** [cite: 2]. Kim conjectured that for sufficiently large \( n \), the set \( X(\mathbb{Q}_p)_n \) is always finite, thereby providing a theoretical pathway to effective Faltings [cite: 2, 6].

### Quadratic Chabauty and p-adic Heights

The Quadratic Chabauty method was pioneered and made algorithmically explicit by Jennifer Balakrishnan, Netan Dogra, Steffen Müller, Jan Tuitman, and Jan Vonk [cite: 4, 7, 8]. The method assumes that the rank of the Jacobian equals the genus (\( r = g \)) and that the Néron-Severi rank of the Jacobian is strictly greater than 1 (\( \rho(J) > 1 \)) [cite: 1]. The latter condition ensures the existence of a non-trivial geometric correspondence on \( X \).

The method relies on the construction of a locally analytic function \( \theta: X(\mathbb{Q}_p) \to \mathbb{Q}_p \) that vanishes on the rational points [cite: 2]. The construction uses \( p \)-adic Hodge theory and Nekovář's theory of \( p \)-adic heights [cite: 2, 6]. 

If \( Z \) is a "nice" correspondence on \( X \) given by a non-trivial element of \( \ker(\text{NS}(J) \to \text{NS}(X) \cong \mathbb{Z}) \), one can associate to points \( x \in X \) certain \( p \)-adic Galois representations (mixed extensions) [cite: 2, 4]. By taking the \( p \)-adic height \( h_p \) of these representations, Balakrishnan and collaborators construct a quadratic Chabauty function [cite: 2]. 

The global \( p \)-adic height decomposes into a sum of local height functions \( h_v \) at every finite place \( v \) [cite: 4, 9]. For a prime \( p \), the local height is computed via iterated Coleman integration and filtered \( \phi \)-modules [cite: 4]. Specifically, the method requires solving the following problems:
1. Expanding the function \( x \mapsto h_p(A_Z(x)) \) into a \( p \)-adic power series on every residue disk of \( X(\mathbb{Q}_p) \) [cite: 2].
2. Evaluating the global height \( h(A_Z(P_i)) \) for a set of known, independent rational points \( P_i \in X(\mathbb{Q}) \) to "fit" the global height pairing in terms of a basis of bilinear forms [cite: 2].

The resulting equation takes the form:
\[ \theta(x) - B(\iota(x), E(\iota(x)) + c) = 0 \]
where \( B \) is a bilinear pairing, \( \iota \) is the Abel-Jacobi map, and \( E \) is an endomorphism induced by the correspondence \( Z \) [cite: 2]. The zeros of this function on \( X(\mathbb{Q}_p) \) yield the Chabauty-Kim set \( X(\mathbb{Q}_p)_2 \), which is finite and contains \( X(\mathbb{Q}) \) [cite: 2, 6].

### Geometric Quadratic Chabauty

An alternative approach to the cohomological Quadratic Chabauty method is the **Geometric Quadratic Chabauty** method, introduced by Edixhoven and Lido, and further developed computationally by Duque-Rosero, Hashimoto, and Spelier [cite: 1, 10].

Instead of using \( p \)-adic Galois representations, the geometric method works with \( \mathbb{G}_m \)-torsors over the Jacobian \( J_{\mathbb{Q}} \) [cite: 1]. By pulling back the Poincaré torsor by a non-trivial trace-zero morphism \( f: J_{\mathbb{Q}} \to J_{\mathbb{Q}} \), one constructs a non-trivial torsor \( T \) over the Néron model of \( J_{\mathbb{Q}} \) whose restriction to \( X_{\mathbb{Q}} \) is trivial [cite: 1]. This allows the embedding of \( X_{\mathbb{Q}} \) into \( T \).

The rational points are found by intersecting the image of the integer points on a regular model of \( X_{\mathbb{Q}} \) with the \( p \)-adic closure of the integer points \( T(\mathbb{Z}) \) [cite: 1]. Recent work in 2024 has shown that the finite set of \( p \)-adic points produced by this geometric method is strictly contained within the set produced by the cohomological method, offering potential computational advantages in determining exact bounds [cite: 1].

## 3. Restriction of Scalars (RoS) Chabauty and Triantafillou's Contributions

While Quadratic Chabauty scales the rank bound to \( r = g \) over \( \mathbb{Q} \), another major challenge in arithmetic geometry is solving curves over general number fields \( K \). Here, the classical Chabauty condition \( r < g \) often fails because the Mordell-Weil rank tends to grow rapidly with the degree of the base field \( d = [K:\mathbb{Q}] \).

To address this, Samir Siksek introduced the **Restriction of Scalars (RoS) Chabauty** method [cite: 11, 12]. By taking the Weil restriction \( \text{Res}_{K/\mathbb{Q}} X \) and \( \text{Res}_{K/\mathbb{Q}} J \), the problem over the number field \( K \) is transformed into a problem over \( \mathbb{Q} \), albeit on higher-dimensional varieties [cite: 3, 13].

### The RoS Chabauty Inequality
The expected requirement for RoS Chabauty to yield a finite bound on the rational points is the inequality:
\[ r \le d(g - 1) \]
where \( r = \text{rank}_{\mathbb{Z}} J(K) \) [cite: 3, 11]. 
Naively, if this dimensional inequality holds, one might expect that the set of points cut out by RoS Chabauty, denoted \( \Sigma_C \) or \( X(K \otimes \mathbb{Q}_p)_1 \), is finite [cite: 3, 14]. However, this is not always true due to geometric obstructions. 

### Base-Change-Prym (BCP) Obstructions

Nicholas Triantafillou has made profound contributions to understanding why RoS Chabauty sometimes fails even when the inequality \( r \le d(g - 1) \) is satisfied. In a series of highly influential papers and his doctoral thesis, Triantafillou systematically classified the reasons for the failure of RoS Chabauty [cite: 3, 14]. 

If there exists a subgroup scheme \( T \subset \text{Res}_{K/\mathbb{Q}} J \) such that the rank of \( T(\mathbb{Q}) \) is "large", and a translate of \( T \) intersects \( \text{Res}_{K/\mathbb{Q}} X \) in a positive-dimensional component, the \( p \)-adic analytic variety cut out by the Chabauty functions will have positive dimension, leading to infinitely many \( p \)-adic solutions [cite: 3, 14]. 

Triantafillou defined a specific class of these geometric anomalies known as **Base-Change-Prym (BCP) obstructions** [cite: 14]. BCP subgroups are constructed out of restrictions of scalars of generalized Jacobians of curves that admit a non-constant map from \( X \) after a suitable base change, combined with generalized Prym varieties of morphisms between such curves [cite: 14]. 

Triantafillou proved that non-trivial BCP subgroups always intersect \( \text{Res}_{K/\mathbb{Q}} X \) in a larger-than-expected dimension. Crucially, Triantafillou demonstrated that BCP obstructions account for **all known failures of RoS Chabauty to date** [cite: 5, 13]. 

By charting these obstructions, Triantafillou provided the necessary theoretical grounding to safely apply RoS Chabauty [cite: 14]. If one can prove a curve has no BCP obstructions, one can algorithmically guarantee the finiteness of the RoS Chabauty output [cite: 14]. 

### Affine Curves and the S-Unit Equation

Triantafillou expanded the scope of RoS Chabauty beyond smooth proper curves to include affine curves, aiming to compute \( S \)-integral points [cite: 14]. In 2024 and 2025, Triantafillou published preprints demonstrating how embedding an affine curve into its generalized Jacobian (analogous to early insights by Skolem for genus 0) can yield bounds on \( S \)-integral points [cite: 14, 15]. 

One of his most notable applications is to the **S-unit equation**, a classic problem in Diophantine number theory seeking solutions to \( x + y = 1 \) where \( x, y \in \mathcal{O}_K^\times \). By modeling the unit equation as integral points on the thrice-punctured projective line \( \mathbb{P}^1 \setminus \{0, 1, \infty\} \), Triantafillou applied affine RoS Chabauty to prove that if the degree of the number field \( [K:\mathbb{Q}] \) is not divisible by 3, and the prime 3 splits completely in \( K \), there are **no exceptional units** in the field [cite: 16, 17]. This provided the first infinite class of fields where RoS Chabauty succeeded while classical Chabauty could not [cite: 16].

Furthermore, recent 2025 work by Triantafillou (with collaborators like Leonhardt) provided explicit upper bounds on the number of \( S \)-integral points on affine curves satisfying certain rank-genus inequalities, bounding the Abel-Jacobi image using arithmetic intersection theory [cite: 15]. 

## 4. Quadratic Chabauty on Modular Curves: Balakrishnan's Computational Breakthroughs

The abstract machinery of Quadratic Chabauty achieves its highest impact in the realm of modular curves. The modular curve \( X_0(N) \), parametrizing elliptic curves with a cyclic subgroup of order \( N \), and its various quotients carry deep arithmetic significance [cite: 2, 18]. 

Between 2024 and 2026, Jennifer Balakrishnan has led a massive computational initiative to map out the rational points on high-genus modular curves, integrating Quadratic Chabauty with high-performance computer algebra systems. Her work, alongside co-authors such as Nicholas Triantafillou, Steffen Müller, Netan Dogra, Jan Vonk, Francesca Bianchi, and Alex Best, has resolved longstanding conjectures [cite: 2, 6, 19].

### Atkin-Lehner Quotients and Galbraith's Conjecture

The Atkin-Lehner involutions \( W(N) \) act on \( X_0(N) \). The quotient of \( X_0(N) \) by the Fricke involution \( w_N \) is denoted \( X_0^+(N) \), while the quotient by the full group of Atkin-Lehner involutions is the "star quotient" \( X_0^*(N) \) [cite: 18]. Rational points on these curves parameterize **$\mathbb{Q}$-curves**, which are elliptic curves isogenous to all of their Galois conjugates [cite: 18, 20]. 

In 2002, Steven Galbraith conjectured that for prime levels \( N \) where the genus of \( X_0^+(N) \) is between 2 and 5, the curve contains exceptional rational points (points that are neither cusps nor CM points) if and only if \( N \in \{73, 103, 137, 191, 311\} \) (along with composite levels 91 and 125) [cite: 2]. 

By applying Quadratic Chabauty, Balakrishnan and her collaborative network completely resolved Galbraith's conjecture. As presented in Balakrishnan's February 2025 VaNTAGe seminar, the computations were divided into blocks based on genus and level [cite: 2]:
*   **Genus 2** (\( N = 67, 73, 103 \)): Computed by the team of Balakrishnan, Best, Bianchi, Lawrence, Müller, Triantafillou, and Vonk [cite: 2]. 
*   **Genus 2 and 3** (\( N = 107, 167, 191 \) and others like \( 97, 109, 113, \dots, 239 \)): Computed by Balakrishnan, Dogra, Müller, Tuitman, and Vonk [cite: 2].
*   **Genus 4, 5, 6** (\( N = 137, 173, \dots, 359 \)): Computed using algorithmic extensions of Balakrishnan's framework by Adžaga, Arul, Beneish, Chen, Chidambaram, Keller, and Wen [cite: 2, 6].

Table 1 summarizes the key prime levels where exceptional points were confirmed or ruled out using Quadratic Chabauty [cite: 2, 6].

| Curve | Genus | Result / Exceptional Points | Method Used |
| :--- | :--- | :--- | :--- |
| \( X_0^+(73) \) | 2 | Has exceptional points. | Quadratic Chabauty + Mordell-Weil Sieve |
| \( X_0^+(103) \) | 2 | Has exceptional points. | Quadratic Chabauty + Mordell-Weil Sieve |
| \( X_0^+(67) \) | 2 | No exceptional points. | Quadratic Chabauty + Mordell-Weil Sieve |
| \( X_0^+(191) \) | 3 | Has exceptional points. | Quadratic Chabauty |
| \( X_0^+(137), X_0^+(311) \) | 4, 5 | Has exceptional points. | Algorithmic extension by Adžaga et al. |

This collaborative triumph proved that Quadratic Chabauty can be effectively weaponized to survey vast classes of modular curves, conclusively proving the non-existence of specific Galois representations. 

### Non-Split Cartan Modular Curves: From Genus 3 to Genus 8

Another critical application of Quadratic Chabauty targets Mazur's Program B, which seeks to classify the possible modulo \( \ell \) Galois representations of non-CM elliptic curves [cite: 10]. This classification heavily involves the non-split Cartan modular curves \( X_{ns}^+(N) \). 

In a landmark 2019 paper, Balakrishnan, Dogra, Müller, Tuitman, and Vonk used Quadratic Chabauty to compute the rational points on \( X_{ns}^+(13) \), a curve of genus 3 with rank 3 [cite: 4, 7, 10]. They proved that the only rational points corresponded to CM elliptic curves, settling a major open question [cite: 4, 10]. 

Following this, the methodology was refined to tackle higher levels. Balakrishnan and her team extended their algorithms to compute the rational points on \( X_{ns}^+(17) \), a curve of **genus 6**. They successfully proved that \( \# X_{ns}^+(17)(\mathbb{Q}) = 7 \), with all points corresponding to CM elliptic curves of specific discriminants (\(-3, -7, -11, -12, -27, -28, -163\)) [cite: 4, 6].

#### The Genus 8 Frontier: \( X_{ns}^+(19) \)
Moving into 2026, the frontier of Quadratic Chabauty has advanced to unprecedented heights. At a scheduled April 2026 seminar at Harvard University, Balakrishnan is set to present work in progress with Steffen Müller and Jan Vonk on the non-split Cartan modular curve \( X_{ns}^+(19) \) [cite: 21, 22]. 

This curve represents a massive computational challenge:
*   **Genus:** 8
*   **Jacobian Rank:** 8
*   **Complexity:** The underlying computations require explicitly computing a basis for the de Rham cohomology \( H^1_{dR}(X_{ns}^+(19)/\mathbb{Q}_p) \) and executing highly demanding local height computations [cite: 21, 22]. 

As the rank and genus increase, the matrices representing the Frobenius action on the \( p \)-adic cohomology grow quadratically, and tracking \( p \)-adic precision loss becomes a severely limiting factor [cite: 6, 22]. Balakrishnan's 2026 work highlights algorithmic optimizations to make these extreme cases computationally feasible, demonstrating the continued scaling of the Chabauty-Kim method.

## 5. Algorithmic and Computational Developments (2024-2026)

The theoretical beauty of Quadratic Chabauty is matched by the extreme complexity of its algorithmic execution. The implementation requires computing \( p \)-adic heights through the lens of Nekovář's continuous homomorphisms and \( p \)-adic Hodge theory. 

### The Algorithm for Quadratic Chabauty

To compute the finite set \( X(\mathbb{Q}_p)_2 \), the modern algorithm developed by Balakrishnan, Müller, Triantafillou, and others follows these broad steps [cite: 2, 6, 23]:

1.  **Geometric Setup**: Determine the rank \( r \) of the Jacobian \( J(\mathbb{Q}) \) and the Néron-Severi rank \( \rho(J) \). If \( r = g \) and \( \rho > 1 \), identify a "nice" non-trivial correspondence \( Z \in \ker(\text{NS}(J) \to \text{NS}(X)) \) [cite: 2, 4].
2.  **Cohomology and Differentials**: Compute a basis for the algebraic de Rham cohomology \( H^1_{dR}(X) \) over \( \mathbb{Q} \). Isolate the regular differentials \( \Omega^1(X) \) [cite: 2, 24]. 
3.  **Local Heights (Filtered \( \phi \)-modules)**: Utilize Tuitman's algorithm for explicit Coleman integration to compute the Frobenius structure on a specifically constructed vector bundle with connection \( (\mathcal{M}, \nabla) \). Evaluate the local height contributions \( h_p(x) \) at the prime \( p \) by expanding them into \( p \)-adic power series on every residue disk of \( X(\mathbb{Q}_p) \) [cite: 2, 6, 24].
4.  **Global Heights**: Find a set of known, independent rational points \( P_i \in X(\mathbb{Q}) \) and compute their local heights at all bad primes to deduce their global \( p \)-adic heights [cite: 2, 4]. 
5.  **Fitting the Bilinear Form**: Use the global heights of the known points to express the global height pairing in terms of a basis of locally analytic functions. This yields a specific, computable locally analytic function \( \theta(x) \) that must vanish on \( X(\mathbb{Q}) \) [cite: 2, 10].
6.  **Root Finding**: Compute the roots of \( \theta(x) = 0 \) on each residue disk using \( p \)-adic Newton iteration [cite: 10, 24].

### The Mordell-Weil Sieve

The output of the Quadratic Chabauty root-finding step is a finite set of \( p \)-adic points \( \Upsilon \subset X(\mathbb{Q}_p) \). While \( X(\mathbb{Q}) \subseteq \Upsilon \), the set \( \Upsilon \) often contains "extra" roots that are defined over \( \mathbb{Q}_p \) but do not correspond to true global rational points [cite: 10]. 

To eliminate these spurious local points, the algorithm invokes the **Mordell-Weil Sieve** [cite: 6, 24]. The sieve uses information from the reduction of the curve modulo various auxiliary primes \( q \neq p \). By computing the image of the known rational points in \( J(\mathbb{F}_q) \), one can restrict the possible residue classes that a true rational point can occupy [cite: 6]. If an "extra" \( p \)-adic root from the Quadratic Chabauty set reduces to a forbidden residue class modulo \( q \), it is mathematically proven to be irrational and can be discarded [cite: 6, 24]. 

Triantafillou and Best played crucial roles in optimizing these sieving techniques for higher-genus modular curves, as documented in the supplemental numerical data for the \( X_0^+(67) \) computations [cite: 24]. 

### Software and the `QCMod` Package

A defining feature of the 2024-2026 research landscape is the open-source dissemination of these advanced algorithms. Balakrishnan and Müller heavily updated the `QCMod` software package for Magma, which automates the Quadratic Chabauty method for certain modular curves [cite: 10, 25]. While initially restricted to hyperelliptic genus 2 curves, ongoing efforts aim to expand the automated tools to higher-genus non-hyperelliptic curves [cite: 6]. Furthermore, Triantafillou and colleagues have contributed heavily to SageMath implementations for cyclic covers and superelliptic curves [cite: 16].

## 6. Applications to Exceptional Points and Uniformity

### Q-Curves and the Moduli Interpretation

One of the fascinating geometric implications of Balakrishnan and Triantafillou's work relates to the moduli interpretation of exceptional points. An exceptional rational point on \( X_0^+(N) \) corresponds to a \( \mathbb{Q} \)-curve: an elliptic curve over a quadratic field that is isogenous to its Galois conjugate [cite: 18, 20]. 

Recent developments presented at the January 2024 AMS Special Session on Arithmetic Geometry highlighted the mystery of *why* these exceptional points arise. While Galbraith noted that exceptional points on \( X_0^+(N) \) for \( N = 73, 103 \) arise from the hyperelliptic involution, the geometric origins of exceptional points on non-hyperelliptic curves (such as \( X_0^+(191) \)) were poorly understood [cite: 26]. Joint work by Boya Wen, Jordan Ellenberg, Sachi Hashimoto, and others (inspired by the Quadratic Chabauty data generated by Balakrishnan, Triantafillou, et al.) aims to use the moduli interpretation directly, rather than relying solely on explicit affine equations, to compute rational points [cite: 10, 26]. 

### Uniform Bounds on Rational Points

While explicitly computing \( X(\mathbb{Q}) \) is the ultimate goal, bounding the size of \( X(\mathbb{Q}) \) uniformly is a parallel objective of immense theoretical value. The original Chabauty-Coleman method allowed for uniform bounds, famously improved by Michael Stoll and later Katz, Rabinoff, and Zureick-Brown, who proved that if \( r < g \), then \( \#X(\mathbb{Q}) \) is bounded by a constant depending only on \( g \) and \( r \) [cite: 10].

Generalizing this to Quadratic Chabauty, Balakrishnan and Dogra (2019) provided bounds based on the number of roots of the quadratic Chabauty function [cite: 10]. In 2024 and 2025, researchers like Alexander Betts expanded this by attaching Hilbert series to Selmer varieties, allowing for explicit "global < local" bounds on the number of rational points for higher levels of Kim's program [cite: 10]. Triantafillou's work on affine Restriction of Scalars also directly contributes to this effort, yielding explicit upper bounds on the number of \( S \)-integral points for curves satisfying generalized rank-genus constraints [cite: 15].

## 7. Future Directions and the 2026 Horizon

The period spanning 2024 to 2026 marks a golden age for the effective computation of rational points on algebraic curves. However, significant challenges remain on the horizon.

### Overcoming the Rank \( > g \) Barrier

Quadratic Chabauty essentially handles cases where \( r = g \) (with the requirement that \( \rho > 1 \)). But what happens when \( r > g \)? 
Minhyong Kim's non-abelian Chabauty program theoretically extends to depth \( n = 3 \) (Cubic Chabauty) and beyond [cite: 8]. If \( n \) is chosen large enough, dimension counting on the Selmer varieties suggests that the Chabauty-Kim set \( X(\mathbb{Q}_p)_n \) will always be finite [cite: 2, 3]. However, making Cubic Chabauty explicit and algorithmic is currently one of the most formidable problems in arithmetic geometry. Balakrishnan, Bianchi, and Dogra have begun preliminary investigations into \( p \)-adic elliptic polylogarithms and Cubic Chabauty, which represent the next logical leap in this research program [cite: 8].

Furthermore, combining Quadratic Chabauty with Restriction of Scalars—a synthesis of Balakrishnan's and Triantafillou's distinct specialties—promises to unlock exact point computations for curves of high rank over number fields. Dogra has laid the theoretical groundwork for Quadratic RoS Chabauty [cite: 5], but fully automating this over arbitrary number fields requires overcoming extreme computational bottlenecks in \( p \)-adic precision and matrix inversion [cite: 5, 27].

### Collaborative Initiatives and 2026 Seminars

The momentum of this field is sustained by tight-knit collaborative networks. The Simons Collaboration on Arithmetic Geometry, Number Theory, and Computation (which includes Balakrishnan as a Principal Investigator and Triantafillou as a key contributor) held its highly anticipated annual meeting in January 2025, focusing on the synthesis of computation and theory [cite: 28]. 

Looking toward 2026, the community anticipates Balakrishnan's Harvard seminar on "Quadratic Chabauty in higher genus" (April 8, 2026). This talk will detail the successful navigation of the computationally prohibitive local height operations required to solve the genus 8 curve \( X_{ns}^+(19) \) [cite: 22]. Such a milestone will set a new benchmark for what is computationally possible in algebraic geometry, proving that the abstract towers of non-abelian Chabauty can indeed be grounded in explicit, absolute truth.

## 8. Conclusion

Faltings' proof of the Mordell conjecture altered the landscape of mathematics by proving that higher genus curves possess only a finite number of rational points. Over forty years later, the mathematical community is finally developing the tools to pinpoint exactly where those points lie. 

The Coleman-Chabauty method provided the first effective window into this problem, but its strict rank-genus inequality limited its scope. The development of Quadratic Chabauty, driven by the algorithmic brilliance of Jennifer Balakrishnan and her collaborators, effectively broke the \( r < g \) barrier, extending our reach to curves where \( r = g \). Concurrently, Nicholas Triantafillou's rigorous theoretical dissection of Restriction of Scalars Chabauty, specifically his discovery of Base-Change-Prym obstructions, has safeguarded these methods when applied over arbitrary number fields.

From settling Galbraith's conjecture on Atkin-Lehner quotients to scaling the computational cliffs of genus 8 non-split Cartan curves, the period from 2024 to 2026 has witnessed unprecedented progress. Driven by the deep geometric insights of \( p \)-adic Hodge theory and powered by modern computational algebra, the Chabauty-Kim program is steadily transforming the effective Mordell conjecture from a theoretical dream into a computational reality.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNxcup9GUi9qEsmSCn0EA-TtDJGsFfSTX2c3rzoTDCQdXtLeUG5VQIPivmZjkyOYdT561B_oCPMoyn7L-Gxm1qgNlE8Vz54md-xpwxhXHTs6Un2-xGzw==)
2. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWi7DeSvIMfV7EWyIdg_0fQPhPFfWT1iWyT3JArSn8dMPtWMIaWjBh7_VYTn4fFw6nXTCrFdvcYT3zART2WRrFvyHr8GWvsnmEBvWquqmb-wB5OE0CAHWvt0LZcjVgYJX6gS80iv5GOU-bH3dNpyfP)
3. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGXa3LHdf7qjeVSUKLMWPoCrmepvCHLlqifNAg81AktMg1GArbPNtDvczHc23gukzXInboCsAtAdy6vqnoa0CfYrICjGIj86KK8C7gyRfwbCTKJArZxMB03ZYhA1OcJvI0ezR9Esk13p3Dz7FfsV2_ai6UqcvG)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFb7JbqGpr_OJrndkVFLOdcs9bhmtbOjeQa2e1qrHJfTeRAPYz6a598SFMln9VHxI7znKB9Qk5oubtstnTzesDk90HsSQFCGpFxm7RVtfVoo1zci_VKog==)
5. [cnrs.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtBn9WV1qtPqge4hC8dYQmPF6iubsqmQKga61csefkxEdsyEVy7tqjXeGQ3z5w1vRQSQ1TLD_IUfqMKTGkh5qF0gZ0o71ARpRwqBHURDwT-Sic5APOWIvDlHBy01eofP2gPsHjBMmb_h-C_LBonphCfCqfND-kly54Drm-349ofwdR)
6. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlY5hl0iI3ZV9ce31V3BdwArBtcGBbB65B_2gNXtUTclZPMJ8aLTjd5A-PS3lp_CqOq00lJwg_mXoL1pn6yGJ36FXJQ0bWpnjNbNYmkXDiRUt38A0dnUcIWPf2_5WbobzPIHmnnAWRPZZsJEZQaGpXHhx3R9lzmvfgUWjdtJaxmzmm26VoB82BxkTRiyceFrIfa89wtSEuuRAWtvwbaZ6tu8fptlWCBcTAxibClSnhP-LfvfhyQvrIhg0fe7AOWVoijd8JWis73hm7aYJ6pL6LVpK6ylGl87ZOdfSF)
7. [leidenuniv.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGr9ZWSL8D9tArlAuyCiDlupYp10PaNkhEsjvV63nyvdv1PNizpmOU83-vBoIfjA-z4iT1sXtS4ywMVJXlEnMzQkXm2UnKB8U0WbHPpiwfuwp33SeiTlW50j2lychZd2_sVrGeQGYrwY1m-U4UjAMPgooXqhw==)
8. [bu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDbNc-o43C1xfkcxMveehuTCYlPqSPKL_wgSXi2ccPADQw-vjxjgM46njyKyyfnUZUCxb9wu7Zhe5pHuOemoxKxGd_LKLNVUraAjKD4n2PcW13VHIgXQ==)
9. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdIGq3f0eLMJEp7gcuvpk_nl3evYXW9PUc9wjneDiry3hq1ktCbtqsP2BXbMU8Fmj3yGvIMCHecpaLoXhOdI-7btA97bgXflYTWedNLtI_ddQDxDxyHpkKN7qggeykNvmuBpaEXl0=)
10. [mordell.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGlChyT5PWc930PSgBCnFbNlyoObMRsVF0foQfpa1wSnABUAQQamaNBaS3Zsd-GBeiMl2blaGZ7jlBrS1k1Z_CmUoKlwNjLcudAIDlgZNAxloFZ29R2K6VFV0=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEluWkPvdoxpPh2Q0AKKpx4NOUqh7fxWmK-6dQUgmbgka2eGwdbjZYKvw9oO1bG34L8PIN42xCDCUnDL3Q3ZW2R1en10DxyKdzVX69jg373pB47CUjslQ==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNbcj-efhmRxy-eICZq8jw-d9-ou8vlkrj1zheD8M7er8vCnXbgw2G5cR4kFb0uaabC7tHCz9etKV5A-MT28w8HmyJaVivLBwnlsfXyxpYgophhcynvQ==)
13. [mcgill.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFv89h9R2ST3M6qyxp7bOC-wU1Zn1PlhTnUAnvKRuQhY0gsupHnYodD5tbABZmwBnHQSBzIEAJ8cwwcsDhib6lkMh5hShkiN2oWm4bQffVogqFByYCG53Ryc7UES6C_S8V4lEKHe_nmgNfeO3YLyuzMSxHoNd4=)
14. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDjjVgIgkd_GztdohqW9Z3A0B5o-o3aG2Qz4l1D4fbw7-zTkMHRtU7QRNCgeXuLzr10v2hi0VCb1xq0qvyr30ky5do1w-bgkwAzNZI5oJz3Q4CFVn7_i6AZzgWVTx4JI-aNz3UCeyq)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGznVW-JZKVpjLSMAENLEH9CnpbBCtBm_9GYhStAhqaH8WUdHdSIfcl-xg7uLCzaN9Ewtr35Y6kJFLT2KwF-7R7cI8eLoRcdeYF1Ua2yfL2nNb27ehMSg==)
16. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYv_vnqKRkJLuFqQM6mvaA7ki-he6UF0OzXJI8QkYfUQsd7SIGMyWdvANQMjQu8QtRpUWERsvO6BskBGVBzbzKKrJcW2-tcZoNYkHfbAOeC1faCkPrQIF-O7C-5tfB)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1BggvxXnqFA85tP8L1T0W79UCCckOjKBDhtnAIGydUjQ3Vp6aMDCWMtvj4E3TQ4Ycqd9FKLvpoFVcepHT7tm_H9wF3NJg_7c0rbniuN2bSnGF1ifminjQ3y1Xza84eN_URvh_Uufh_2_ydAtYI36Hszrw)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJtiPuo1xOtHNSnBJzJiX9aJKz8q2JNIOUGwxuQCMfoUKHIIsoO4zWPkkD1yxy55hDyuPabLwl7mKmphZdzsmgjHQ02qV-MViYzmyXVCh1iso4cj3A4Q==)
19. [rug.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIIfgnQ4HE6sjFD8WXOVt2hWZMk1fet1BqLs_bgBGgMeH21cU584czqfYtHemN_l9zYe6JDLSjcDB7W401jo0O5yGDdMWXSSR35gVS-7EwwNMiliZI4Igq7PuHhFo6m2OQDipC6I1psv3cTyOZ93V6iYZn1uOFqPkIUWjh6nlUVxOKnpGM1w_xslJGtz_rYS3l1ytCaM1AutmpVhdUAeFT)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyevXDvmLosHBRvoqJQ5a_Y-uXO_4YGB5TU1sXiCJqgaCO4pdbOjgGM4dgc3sZBGLdzC_4bGKzKZ-lmd-Vp0nS0T8nW9S67Bpdw5f1_vSls827vo-YmEtGAZTjLVi23hOlGroT3la9T0YCS5Eh-Lq4yQFBNRLjF_PlosprSgWZIPC5inV146kZeZxQh9TUEpUaYT6iNDbvK--SkJQe)
21. [ucsd.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-R4xABbNhEkCD1BYv_fhNZBzS0PKpa8PGyYL8mEqKCMW6TBbByRsZ8UJd2Tro8dgXHUBTvL4g1MtH0f6cCgkb9dUSibXN1lcy1hdryFyZSHPeE8k_75HYUjsmBIB3nwxoAAsjvbPalBevBm4Htwi8d9fQ)
22. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEm_wv6-DOxHkwJxvsnASqeoP2iZnxDn9baQcT6gmsmdpg-vgEt6IKV32_AOivAlKH_TSC3pZIQ1_L5Uw5mbrUpg9tEn5D2-axSlkgyFNgAANFpBFayF7BtdcECrVCbGkePEG__zyOzDzEH1aFXIfVMDk2fHRJjoIRcVlL6)
23. [bu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzafkbCtLq9jEA6gnBfzR3KQXio7jjPAaQ5yoTatxNNIPcPHiV_wOMq6kODoZJl_XB0SqLLkgs8WOq-zfAsTAaL05dZf3dixJZx8iPRb1s7W5MbeRUSFkAJp-lxPFrbrVmtEBL12CCfJlIDSnbg83yQFLye3PiJg==)
24. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZw7UmzeVqEuTzcWlHxEbqQyjxWPPiDRUKHVe55vyFZO3KVwWM1iEmwzYTk1LmcsW2ZLQ_Vf2LT-lksXBzbeIYhm7BirtzpvrrX3FLxIEBLsHKH2FrOnAolx5nt38HsML4n_j_BffTKQ==)
25. [universiteitleiden.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3jjybe4IMvkhMVCTnydHoDaipn9GMvAs_6jzcIZcru6wGb7wdjufF1mWFI1xaayFbr-ViyinWwn_KUqG1KuJKbAr3zV3xiyBbbpW3kKyaO0K9EBeVg6woV1FRcm0CeSwSjg7YP2SrWMmHZDkR2SKeTB3pa5NWMyI_clOLe369lWYdfYw=)
26. [ams.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1_GPCCz3cw5a2PTd_cjyz-nwrJFt_DRLgp93ufISqL2JjGoN4X019QR0GVizG6-Oj-R7_H7dysF1Gj-6Z2vho4H9TA8QYXfuLoszFFvV-KnMLy5DK9AetXmo8lKx3rxYb-FUdmhQdGbsgT-5nZdmXIO5-8rs5)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGX9JVawLR4g-_056Nm4JYu8QQElH6-bVD3XnIPJ0Cte2Cp64vMIVqyY4c6sbIsSR7jQD1mZ2rIO9Xz5omIc5ftlIVN1N1I5ZJMYYDDKK__nupjtCRKJw==)
28. [simonsfoundation.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmlkfPVZMsE5E68sORtMBaZ51SeBSgRVq2BQ9Wa_1brRau7fT_9VqzhldBYmKiM7npacsU_H_degrhQTBX29y4zOXb-xDEis_-wN-qLRTqmkxpau4sU3ijebeNU-h9yAnFM0O1hfyUpB1viKwds1_YDeKNUB10RpkMG_0dHXBrWazEoctiRrjWdl9OvnD2H-dtry1bGINSDcQF4yiCnsEc3WCGZFhBaym0X0MopxVw9vpbGkYqjkTxevnRGQ==)

