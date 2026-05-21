# Birch-Swinnerton-Dyer for higher-genus curves 2024-2026 (BCGP-extensions)

**Pythia queue id:** 160
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChczelFQYXFEV05fWFVqTWNQajdxRXdBaxIXM3pRUGFxRFdOX1hVak1jUGo3cUV3QWs
**Elapsed:** 378s
**Completed at:** 2026-05-21T16:44:11.622381+00:00

---

# The Birch-Swinnerton-Dyer Conjecture for Higher-Genus Curves and Abelian Surfaces: Breakthroughs from 2024 to 2026, BCGP Extensions, and Computational Verifications

## Leading Paragraph

**Key Points:**
- **The Birch and Swinnerton-Dyer (BSD) Conjecture** remains one of the most profound open problems in modern mathematics, linking the analytic properties of L-functions to the arithmetic invariants of algebraic curves and their associated abelian varieties.
- **The BCGP Modularity Theorems** (developed by Boxer, Calegari, Gee, and Pilloni) have largely resolved the potential modularity of abelian surfaces and genus 2 curves over totally real fields, establishing the unconditional foundation required to formally state the BSD conjecture for these spaces.
- **Exact Verifications of Strong BSD** have been achieved for the first time for absolutely simple modular abelian varieties of dimension two or higher. Algorithmic breakthroughs by Keller and Stoll (2024–2025) successfully confirmed the exact strong BSD formula for 97 genus 2 curves from the LMFDB and 28 Atkin-Lehner quotients.
- **Euler Systems for GSp(4)**, constructed by Loeffler, Skinner, and Zerbes, have yielded conditional proofs of the BSD conjecture for modular abelian surfaces of analytic rank zero. Recent innovations like "Ultra-Kolyvagin systems" appear poised to bypass traditional barriers in non-ordinary (supersingular) settings.
- **Novel Geometric and Informational Frameworks** (2026) have introduced new methodologies for constructing higher-genus hyperelliptic curves with fixed ranks, alongside experimental perspectives that attempt to reinterpret the BSD conjecture as a conservation of informational coherence on arithmetic manifolds.

**The BCGP Modularity Extensions:** The collaborative theorem by Boxer, Calegari, Gee, and Pilloni (BCGP) represents a monumental leap in the Langlands program, proving that abelian surfaces over totally real fields are potentially modular. By leveraging higher Coleman theory and the Calegari-Geraghty method, they successfully navigated the complexities of irregular weights and parity conditions. Furthermore, extensions of these techniques have established the modularity of a positive proportion of elliptic curves over complex multiplication (CM) fields, expanding the Diophantine applicability of these lifting theorems.

**Exact Verification of Strong BSD:** While the BSD conjecture has been numerically verified for specific higher-genus curves in the past, recent advancements have allowed for its unconditional, exact verification. Through sophisticated calculations of exact rational periods and \(p\)-isogeny descents to bound \(p\)-Selmer groups, computational arithmetic geometry has successfully verified the strong BSD conjecture for dozens of absolutely simple genus 2 Jacobians, even isolating instances where the elusive Tate-Shafarevich group is non-trivial and precisely matches the predicted order of 49.

**Theoretical Leaps via Euler Systems:** In the theoretical domain, controlling the cohomology of Galois representations associated with Siegel modular forms is crucial for bounding the Tate-Shafarevich group. The construction of Euler systems for the symplectic group \(GSp(4)\) using Eisenstein classes for \(GL(2) \times GL(2)\) has led to explicit reciprocity laws. These tools have established vital links between \(p\)-adic L-functions and the Birch-Swinnerton-Dyer conjecture in the analytic rank zero case, provided certain smoothness conditions hold on the corresponding eigenvarieties. 

***

## Introduction: The Birch-Swinnerton-Dyer Conjecture in Higher Dimensions

The Birch and Swinnerton-Dyer (BSD) conjecture, originally formulated in the 1960s based on the extensive computational observations of Bryan Birch and Peter Swinnerton-Dyer for elliptic curves over the rational numbers \(\mathbb{Q}\), stands as a central pillar of modern number theory [cite: 1, 2]. In its classical formulation, it proposes an intricate and deep relationship between the algebraic structure of an elliptic curve (such as its group of rational points) and the analytic behavior of its associated Hasse-Weil L-function at a critical point [cite: 1, 3, 4]. 

In the subsequent decades, John Tate generalized this conjecture to abelian varieties of higher dimensions defined over global fields [cite: 5]. An abelian variety over a field \(k\) is a proper, complete algebraic variety that is also endowed with a commutative group structure [cite: 6]. For an algebraic curve of genus \(g \geq 1\), its Jacobian—an abelian variety of dimension \(g\)—serves as the primary object of arithmetic study [cite: 3, 7]. The generalized BSD conjecture posits that the arithmetic of an abelian variety \(A\) over a number field \(K\) is entirely encoded within its L-function \(L(A, s)\) [cite: 1, 8].

The L-function \(L(A, s)\) is defined as an Euler product over the finite places of the number field, aggregating the local arithmetic data (the number of points modulo primes) of the variety [cite: 4, 9]. Specifically, if \(X\) is a smooth, projective variety with good reduction outside a finite set of primes \(S\), its global Hasse-Weil zeta function is defined as:
\[ \zeta_X(s) = \prod_{x} \frac{1}{1 - N(x)^{-s}} \]
where the product runs over all closed points \(x\) of a smooth proper integral model of \(X\) [cite: 7]. For an abelian variety \(A\) of dimension \(d\), the L-function \(L(A, s)\) is derived from the degree-1 cohomology and converges absolutely in the right half-plane \(\text{Re}(s) > 3/2\) [cite: 4, 9]. 

The BSD conjecture is traditionally divided into two parts. The **Weak BSD Conjecture** asserts that the algebraic rank of the finitely generated abelian group of rational points \(A(K)\)—known as the Mordell-Weil rank, \(r\)—is exactly equal to the analytic rank, which is defined as the order of vanishing of the L-function \(L(A, s)\) at the critical point \(s=1\) [cite: 4, 5]. 

The **Strong BSD Conjecture** is vastly more ambitious. It provides an exact formula for the leading Taylor coefficient of the L-function at \(s=1\). If \(A/\mathbb{Q}\) is an abelian variety of dimension \(d\) and rank \(r\), the strong conjecture states that:
\[ \lim_{s \to 1} \frac{L(A, s)}{(s-1)^r} = \frac{\Omega_A \cdot R_A \cdot |\text{Sha}(A)| \cdot \prod_{p} c_p}{|A(\mathbb{Q})_{\text{tors}}| \cdot |A^\vee(\mathbb{Q})_{\text{tors}}|} \]
Here, \(\Omega_A\) is the real period of the variety, \(R_A\) is the regulator of the Mordell-Weil group, \(c_p\) represents the Tamagawa numbers measuring the local geometry at primes of bad reduction, \(A(\mathbb{Q})_{\text{tors}}\) is the torsion subgroup of rational points, \(A^\vee\) is the dual abelian variety, and crucially, \(\text{Sha}(A)\) is the Tate-Shafarevich group [cite: 1, 4, 5]. 

The Tate-Shafarevich group, \(\text{Sha}(A)\), measures the extent to which the local-to-global Hasse principle fails for principal homogeneous spaces over \(A\); it is famously conjectured to be finite, a property that remains one of the most significant theoretical hurdles in arithmetic geometry [cite: 1, 10]. The finiteness of Sha implies that standard descent algorithms used to compute the Mordell-Weil group will actually terminate [cite: 10]. 

However, before one can even unconditionally state the BSD conjecture, a fundamental analytic barrier must be overcome: the L-function \(L(A, s)\) is only initially defined in its half-plane of absolute convergence. The Hasse-Weil conjecture predicts that \(L(A, s)\) admits a meromorphic continuation to the entire complex plane and satisfies a functional equation relating its value at \(s\) to its value at \(2-s\) [cite: 9, 11]. Without analytic continuation, the value or the derivative of \(L(A, s)\) at the critical point \(s=1\) is mathematically undefined [cite: 8]. Proving analytic continuation inherently relies on establishing the **modularity** of the abelian variety—showing that its Galois representation corresponds to an automorphic representation [cite: 4, 12]. 

***

## The Modularity of Abelian Surfaces (The BCGP Theorem and Extensions)

The modularity of elliptic curves over \(\mathbb{Q}\) was definitively established through the landmark works of Wiles, Taylor, Breuil, Conrad, and Diamond, proving that every rational elliptic curve corresponds to a classical modular form [cite: 11, 12]. This monumental achievement resolved the Hasse-Weil conjecture for genus 1 curves over \(\mathbb{Q}\). However, generalizing these modularity lifting theorems to higher-dimensional abelian varieties—and consequently to higher-genus curves—has presented overwhelming technical challenges over the past two decades.

### Modularity over Totally Real Fields (Boxer, Calegari, Gee, Pilloni)

The recent breakthrough by George Boxer, Frank Calegari, Toby Gee, and Vincent Pilloni (often abbreviated as the BCGP theorem) represents a paradigm shift in the study of higher-genus curves. The BCGP theorem states that if \(X\) is either a genus two curve or an abelian surface over a totally real field \(F\), then \(X\) is **potentially modular** [cite: 7, 9, 11]. 

An abelian variety \(X/F\) is said to be modular if its L-function \(L(X, s)\) is a product of automorphic L-functions [cite: 7, 9]. It is *potentially modular* if there exists a finite extension \(F'/F\) such that the base change \(X_{F'}\) is modular [cite: 7, 9]. The deduction of the Hasse-Weil conjecture (Conjecture 1.1) from potential modularity is mathematically straightforward in this case, utilizing the fact that the cohomology of an abelian surface is given by the wedge powers of the cohomology in degree 1, combined with known Langlands functoriality results for wedge powers [cite: 7, 9, 11]. Consequently, the BCGP theorem effectively resolves the Hasse-Weil conjecture for abelian surfaces over totally real fields, granting the necessary analytic continuation to unconditionally formulate the Birch-Swinnerton-Dyer conjecture for these spaces [cite: 7, 9, 11].

The proof of the BCGP theorem is a masterpiece of modern arithmetic geometry, navigating three primary obstacles:

1. **Irregular Weights and Higher Coleman Theory**: The Galois representations associated with abelian surfaces have Hodge-Tate weights of 0, 0, 1, 1 [cite: 7]. If such an abelian surface is modular, it must correspond to a Siegel modular form of weight \(k=2\) [cite: 7]. In the taxonomy of automorphic forms, weight 2 is considered an "irregular weight" because the Hodge-Tate weights are not pairwise distinct (for a general weight \(k\), the weights are \(0, k-2, k-1, 2k-3\)) [cite: 7]. Traditional Taylor-Wiles modularity lifting theorems fail for irregular weights. To circumvent this, the BCGP strategy relies on establishing a residual modularity in weight 3 (which is a "regular weight") and then utilizing "higher Coleman theory"—developed by Boxer and Pilloni—to interpolate \(p\)-adic families of modular forms and rigorously "change weight" [cite: 7, 11, 13].
2. **The Calegari-Geraghty Method**: The second obstacle involves the Betti cohomology of the locally symmetric spaces associated with the symplectic group. Unlike classical modular curves, these spaces lack the parity conditions necessary for the strict numerical coincidences required by the original Taylor-Wiles method. To deduce modularity lifting, BCGP deployed the Calegari-Geraghty method, which systematically manages the presence of torsion classes in the coherent cohomology of Siegel-type Shimura varieties [cite: 4, 7, 11].
3. **The 2-3 Switch**: Wiles's original proof of Fermat's Last Theorem utilized a "3-5 switch," exploiting the rationality of certain twists of the modular curve \(X(5)\) over \(\mathbb{Q}\) to pass from mod 3 to mod 5 residual representations [cite: 7, 12]. Because this specific geometry is unavailable in higher dimensions, BCGP executed an innovative "2-3 switch." They constructed a rational moduli space of abelian surfaces equipped with specific level structures. A theorem of Moret-Bailly was then used to find a totally real extension field where this moduli space has a rational point satisfying specific local conditions at primes dividing \(p\) and \(q\), thereby establishing the necessary residual modularity [cite: 7, 11]. 

### Generalization to CM Fields

While potential modularity over totally real fields is a triumph, proving strict modularity (as opposed to potential modularity) over a broader class of number fields is essential for exact Diophantine applications. Subsequent extensions of the BCGP framework have taken the first steps toward proving the modularity of elliptic curves over Complex Multiplication (CM) fields, such as imaginary quadratic fields [cite: 12]. 

We say an elliptic curve \(E\) over a number field \(K\) is modular if either \(E\) has complex multiplication itself, or there exists a cuspidal, regular algebraic automorphic representation \(\pi\) of \(GL_2(\mathbb{A}_K)\) such that \(E\) and \(\pi\) share the same L-function [cite: 12]. The modularity of elliptic curves over a CM field implies the analytic continuation of their L-function to the whole complex plane, allowing the Birch-Swinnerton-Dyer conjecture for \(E\) to be formulated unconditionally [cite: 12].

Historically, Wiles established modularity for semistable elliptic curves over \(\mathbb{Q}\) in two steps: first proving a modularity lifting theorem for 2-dimensional \(p\)-adic Galois representations \(\rho: \text{Gal}(\bar{\mathbb{Q}}/\mathbb{Q}) \to GL_2(\mathbb{Z}_p)\), and second, proving residual modularity [cite: 12]. Using an adaptation of the Taylor "potential \(p-q\) switch" combined with the BCGP modularity lifting theorems, researchers have recently proven that a positive proportion of elliptic curves over any CM field not containing a primitive 5th root of unity are in fact modular [cite: 12]. This involves proving that many residual representations \(\bar{\rho}: \text{Gal}(\bar{K}/K) \to GL_2(\mathbb{F}_3)\) (as well as for \(p=2\) or \(5\)) arise from modular elliptic curves [cite: 12]. 

***

## Exact Verification of the Strong BSD Conjecture for Genus 2 Curves

For many purposes, particularly the verification of the Birch-Swinnerton-Dyer conjecture, potential modularity is insufficient; strict modularity is highly desired to precisely analyze the L-function [cite: 7, 9]. If an abelian surface \(A\) defined over \(\mathbb{Q}\) has trivial geometric endomorphism ring, its modularity corresponds to an automorphic representation of \(GSp(4)\) (specifically, the generalized paramodular conjecture) [cite: 8, 14]. 

For years, verifications of the BSD conjecture for higher-genus curves were strictly numerical. A famous calculation by Flynn, Leprévost, Schaefer, Stein, Stoll, and Wetherell numerically verified the conjecture for the Jacobians of 32 modular hyperelliptic curves of genus 2 [cite: 5]. Subsequent efforts extended this numerical verification up to squares for select curves of genus 3, 4, and 5 without using modular methods, often relying on approximations of the real period and analytic order of the Tate-Shafarevich group [cite: 5]. 

However, between 2024 and 2025, an astonishing computational and theoretical milestone was achieved by Timo Keller and Michael Stoll. They developed the comprehensive theory and algorithms necessary to completely and exactly verify the **strong Birch-Swinnerton-Dyer Conjecture** for absolutely simple modular abelian varieties over \(\mathbb{Q}\) [cite: 2, 15, 16, 17]. This is widely regarded as the first time that the strong BSD conjecture has been confirmed unconditionally and exactly for absolutely simple abelian varieties of dimension at least 2 [cite: 15, 17, 18, 19].

### Computational Breakthroughs (Keller and Stoll 2024-2025)

The verification of strong BSD requires computing several immensely complex invariants with absolute, exact precision, rather than floating-point approximation. Keller and Stoll's methodology tackled the following components:

1. **Exact Rational Periods and L-functions**: Previously, computing the ratio \(L(A, 1)/\Omega_A\) as an exact rational number for an abelian variety of positive rank was an open problem [cite: 2]. Keller and Stoll provided a feasible algorithm for the computation of \(p\)-adic L-functions in this setting, allowing for the rigorous evaluation of the analytic invariants [cite: 2].
2. **Bounding the Tate-Shafarevich Group via Isogeny Descents**: To show that the order of the Tate-Shafarevich group exactly matches the analytic prediction, one must explicitly bound the Selmer groups. Keller and Stoll implemented \(\mathfrak{p}\)-isogeny descents for scenarios where the mod-\(\mathfrak{p}\) Galois representation is reducible [cite: 2]. By gaining an upper bound on the \(\mathfrak{p}\)-Selmer group, they could establish the triviality (or exact finite order) of the \(\mathfrak{p}\)-primary components of \(\text{Sha}(A)\) [cite: 2, 18].
3. **Tamagawa Numbers and Néron Models**: For bad primes, assessing the Tamagawa numbers requires computing the component groups of the special fibers of Néron models. Unlike elliptic curves, where Tate's algorithm suffices, higher-genus curves require sophisticated models [cite: 6]. Keller and Stoll's framework systematically computes the exact Euler factors and local integration terms required by the strong BSD formula [cite: 2, 6].

### The 97 Genus 2 Curves from LMFDB and Atkin-Lehner Quotients

Applying their new algorithmic framework, Keller and Stoll targeted comprehensive datasets of genus 2 curves. The L-functions and Modular Forms Database (LMFDB) contains 63,107 genus two curves over \(\mathbb{Q}\) with \(\text{End}_{\mathbb{Q}}(\text{Jac}(X)) = \mathbb{Z}\) [cite: 11]. Of these, Keller and Stoll identified exactly 97 genus 2 curves whose Jacobians are absolutely simple and of \(GL_2\)-type [cite: 2, 20]. By their completeness statement, this comprises all such examples with the absolute value of their discriminant at most \(10^6\) and moderately small coefficients [cite: 20]. 

In addition to the 97 LMFDB curves, their verification encompassed all 28 Atkin-Lehner quotients of \(X_0(N)\) of genus 2, and six further historic curves originally identified by Wang [cite: 2, 15, 16, 17]. For all these cases, the strong BSD conjecture was proven unconditionally [cite: 15, 17]. 

Particularly striking is their discovery and verification of an example where the Tate-Shafarevich group is definitively non-trivial. While many algorithms can easily verify cases where \(\text{Sha}\) is trivial (order 1), Keller and Stoll successfully isolated an absolutely simple abelian surface where the order of the Tate-Shafarevich group is exactly \(7^2 = 49\), a figure that precisely agrees with the analytic prediction dictated by the BSD conjecture [cite: 15, 17, 21, 22]. This provides profound, tangible evidence that the mysterious Tate-Shafarevich group operates exactly as Birch and Swinnerton-Dyer envisioned, even in higher dimensions.

***

## Euler Systems, GSp(4), and Theoretical Advances (Loeffler, Zerbes et al.)

While exact computational verification provides indisputable evidence for the BSD conjecture in specific cases, theoretical advancements are required to prove the conjecture for broad classes of varieties. The most powerful modern tool for controlling the global cohomology groups of Galois representations—and thereby bounding the Tate-Shafarevich group—is the theory of **Euler systems** [cite: 23, 24, 25].

An Euler system is a highly structured, norm-compatible family of cohomology classes defined over towers of algebraic number fields (such as cyclotomic extensions) [cite: 24, 25]. Following the groundbreaking work of Kolyvagin, Kato, and Rubin, if one can construct an Euler system for a Galois representation \(V\) and prove that the "bottom class" of this system is non-zero, one can obtain a definitive upper bound on the Selmer group of \(V\) [cite: 23, 25, 26]. Bounding the Selmer group is tantamount to bounding both the Mordell-Weil group and the Tate-Shafarevich group [cite: 23].

### Euler Systems for GSp(4)

In a monumental series of papers culminating between 2021 and 2026, David Loeffler, Sarah Livia Zerbes, and Christopher Skinner successfully constructed an Euler system for the Galois representations associated with cohomological cuspidal automorphic representations of \(GSp(4)\) [cite: 27, 28, 29]. This construction utilizes the pushforwards of Eisenstein classes for the product group \(GL(2) \times GL(2)\) [cite: 27, 28]. 

To make progress on the BSD conjecture, constructing the Euler system is only the first step. The second, immensely difficult step is proving an **explicit reciprocity law**. This law relates the localization of the Euler system at the prime \(p\) to the critical values of the associated L-functions [cite: 23]. Loeffler and Zerbes carried out this program for the 4-dimensional spin Galois representations arising from Siegel modular forms of genus 2 (automorphic representations of \(GSp(4)/\mathbb{Q}\)) [cite: 23]. 

### Analytic Rank 0 and the p-adic Eigenvariety

Using this explicit reciprocity law, Loeffler and Zerbes were able to mount a direct attack on the analytic rank zero case of the Birch-Swinnerton-Dyer conjecture for modular abelian surfaces [cite: 8, 30, 31]. 

Let \(A\) be a modular abelian surface over \(\mathbb{Q}\) which either has a trivial geometric endomorphism ring or arises as the restriction of scalars of an elliptic curve over an imaginary quadratic field (which is modular but not a \(\mathbb{Q}\)-curve) [cite: 8, 30]. Loeffler and Zerbes proved the following profound implication: **If the L-function \(L(A, 1) \neq 0\) (meaning the analytic rank is zero), and the \(p\)-adic eigenvariety for \(GSp(4)\) is smooth at the point corresponding to \(A\), then the group of rational points \(A(\mathbb{Q})\) is finite, as predicted by the BSD conjecture, and the \(p\)-primary part of the Tate-Shafarevich group is also finite** [cite: 8, 30].

This theorem represents one of the strongest theoretical results towards the BSD conjecture for higher-dimensional abelian varieties to date. The condition regarding the smoothness of the \(p\)-adic eigenvariety at non-regular weight points is a technical hypothesis necessitated by the geometry of the deformation rings, but it is highly plausible and widely expected to hold [cite: 8, 31]. Furthermore, for cohomological automorphic representations of \(GSp(4)\), Loeffler and Zerbes removed these restrictive hypotheses entirely, as smoothness of the eigenvariety is automatic in the cohomological case [cite: 8, 30].

### Bloch-Kato and Iwasawa Main Conjectures

The consequences of the explicit reciprocity law extend beyond BSD. It yields a proof of one inclusion of the cyclotomic **Iwasawa Main Conjecture** for the spin motive of genus 2 Siegel modular forms, as well as the **Bloch-Kato conjecture** in analytic rank 0 for their critical twists [cite: 8, 23]. The Bloch-Kato conjecture is a vast generalization of BSD that applies to the L-functions of arbitrary motives over number fields, providing a unified framework for special values of L-functions [cite: 29]. By controlling the Selmer groups of these 4-dimensional spin Galois representations, Loeffler and Zerbes have significantly advanced our understanding of motivic cohomology [cite: 23].

### Ultra-Kolyvagin Systems and Non-Ordinary Selmer Groups (2025-2026)

A major limitation in the traditional application of Euler and Kolyvagin systems is the requirement of "ordinarity." To formulate a version of the Iwasawa Main Conjecture for a Galois representation \(V\), one typically assumes that \(V\) satisfies a strict ordinarity condition at the prime \(p\) [cite: 26]. When an abelian variety has supersingular (non-ordinary) reduction at \(p\), classical Kolyvagin machinery fails because the required Selmer groups lack a natural integral structure [cite: 26].

A 2013 theory by Pottharst showed how to define a variant of the Main Conjecture under a much weaker assumption—relying on the Robba-ring \((\phi, \Gamma)\)-module associated to \(V\) having a submodule of a specific rank [cite: 26]. However, the absence of integral structure makes bounding Pottharst's Selmer groups using Euler systems exceedingly difficult [cite: 26].

In late 2025 and 2026, Loeffler and Zerbes published preprints introducing a revolutionary concept: **Ultra-Kolyvagin systems** [cite: 26, 32, 33]. Drawing upon insights originally introduced by Sweeting, they demonstrated that Kolyvagin classes can be "patched together" using non-principal ultrafilters [cite: 32]. This topological approach allows the construction of limiting objects directly in characteristic zero, completely bypassing the need for an integral structure [cite: 32]. 

Assuming that the local condition satisfied by the Euler system is "closed," this property propagates to the ultra-Kolyvagin system [cite: 32]. This groundbreaking methodology allows the Euler system machine to directly obtain bounds on non-ordinary (supersingular) Selmer groups with orthogonal local conditions [cite: 32]. As a result, the barrier of ordinarity in the Bloch-Kato and Iwasawa Main conjectures is currently being dismantled, opening up entirely new families of modular abelian surfaces to theoretical verification of the BSD conjecture.

***

## Alternative Interpretations and Novel Constructions (2024-2026)

While algebraic number theory and Langlands functoriality dominate the pursuit of the Birch-Swinnerton-Dyer conjecture, recent years have also seen innovative geometric constructions and radical informational re-interpretations of the conjecture.

### Geometric Constructions of Higher-Genus Hyperelliptic Curves

Testing the BSD conjecture often relies on finding curves with specific, known properties. For genus \(g \geq 2\), the dimensions of the moduli space of principally polarized abelian varieties of dimension \(g\) is \(\frac{g(g+1)}{2}\), the moduli space of curves of genus \(g\) is \(3g-3\), and the moduli space of hyperelliptic curves is \(2g-1\) [cite: 3]. For \(g \geq 3\), the hyperelliptic locus is a very thin subset of the moduli space of principally polarized abelian varieties [cite: 3]. Consequently, the naive strategy of taking products of lower-dimensional abelian varieties (e.g., multiplying elliptic curves) rarely yields the Jacobian of a hyperelliptic curve [cite: 3].

To address this, 2026 research introduced a sophisticated geometric strategy: constructing a new hyperelliptic curve by taking the fibre product of two chosen hyperelliptic curves of smaller genus [cite: 3]. By carefully selecting the foundational curves, the Jacobian of the resulting higher-genus curve is isogenous to a product of the Jacobians of the original curves [cite: 3]. 

This methodology has allowed researchers to explicitly construct infinitely many hyperelliptic curves of any genus over any number field whose Jacobians have fixed, guaranteed positive ranks (specifically, ranks 0, 1, and 2 for any genus \(g \geq 3\)) [cite: 3]. Furthermore, specific constructions have proven that ranks of 3 exist over \(\mathbb{Q}\) for genus 3 to 6, and ranks of 4 exist for genus 3 and 4 [cite: 3]. Providing abundant families of higher-genus curves with verified positive rank is invaluable for the continued numerical and exact verification of the weak and strong BSD conjectures [cite: 3].

### Informational-Geometric Perspectives: Viscous Time Theory

In an intriguing departure from classical arithmetic geometry, a January 2026 manuscript proposed an "informational-geometric" reinterpretation of the Birch and Swinnerton-Dyer conjecture [cite: 1]. Working within a framework termed *Viscous Time Theory (VTT)*, this approach attempts to map traditional arithmetic invariants to measurable quantities that govern "informational coherence" [cite: 1].

In this paradigm, the classical BSD identity is not viewed merely as a numerical coincidence between analytic L-functions and algebraic Mordell-Weil groups. Instead, it is hypothesized to be the manifestation of a deeper conservation law—a "Law of Informational Coherence Conservation" that regulates the persistence of coherent informational structures on arithmetic manifolds [cite: 1]. 

The VTT framework explores higher-genus and synthetic informational models, observing that these models exhibit systematic coherence suppression that is remarkably consistent with known arithmetic phenomena (such as the behavior of Tamagawa numbers and the Tate-Shafarevich group) [cite: 1]. While the authors explicitly state that this work does not constitute a mathematical proof of the Birch and Swinnerton-Dyer conjecture, it offers a coherent explanatory framework that geometrically aligns analytic and arithmetic invariants [cite: 1]. By clarifying the internal structure of the conjecture through the lens of information theory, it opens novel avenues for conceptual investigation, suggesting that the deep link between \(L(A,1)\) and \(\text{Sha}(A)\) may be a fundamental property of how arithmetic information is conserved across dimensions [cite: 1].

***

## Conclusion and Future Directions

The period spanning 2024 to 2026 has been an era of unprecedented acceleration in our understanding of the Birch and Swinnerton-Dyer conjecture for higher-genus curves. The modularity of abelian surfaces—long considered an insurmountable hurdle due to irregular weights and non-parity symmetric spaces—has been largely resolved over totally real fields through the brilliant integration of higher Coleman theory and the Calegari-Geraghty method by Boxer, Calegari, Gee, and Pilloni [cite: 7, 9, 11].

Simultaneously, computational arithmetic geometry has evolved to a point where exact, unconditional verification of the strong BSD formula is a reality for absolutely simple abelian varieties of dimension two, thanks to the pioneering algorithms of Keller and Stoll [cite: 2, 15]. Their identification of a genus 2 Jacobian featuring a Tate-Shafarevich group of order 49 stands as a testament to the absolute precision of Birch and Swinnerton-Dyer's original insight [cite: 15, 17].

Theoretically, the construction of Euler systems for \(GSp(4)\) and the formulation of ultra-Kolyvagin systems by Loeffler, Skinner, and Zerbes have forged the definitive link between the analytic vanishing of the L-function and the algebraic finiteness of the Mordell-Weil and Tate-Shafarevich groups [cite: 23, 30, 32]. 

As research moves forward, the immediate goals involve stripping away the remaining technical hypotheses (such as the smoothness of the eigenvariety in non-cohomological cases) and expanding exact computational verifications to dimensions three and beyond. Whether viewed through the rigorous lens of Euler systems, the geometric construction of hyperelliptic fibre products, or the avant-garde theories of informational coherence, the complete resolution of the Birch and Swinnerton-Dyer conjecture for higher-dimensional varieties appears closer now than at any point in history.

**Sources:**
1. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvpqdZ7Nm55BKgvkKFkHyvyIs99oZMGiulM3JjuLrd_xgKDhFLWBeZkaBoNO15Low8qEqCT_k5nYjRysJzh4gm8pqaLK4-wouptMQrHWKluIA0Zo_ySr0RTAibpM8PnpwSucqKeZE=)
2. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuNmodEFJ4A7CrRFmjpX1nbmYQgYqzWNl8MsFFbtCi77LLL-JfJDtKy1m5KcXt4nxkiRSaXVdO1uGw6x6vl7MqxEFOwH7xR7CAtwDmz_45ZtWSNMEXX5uiv22eOsAcMu5xKD8y6sFKs61G7gk2Vclncj6TRfL8i6rxy6fQO6cMvmjF68RcsogFCdUiUshpN4g5LmsRKZ-dzMa9JJXe_yUNGIDGx9pn0fNS0CTyQEoh5s7GbEUJqCcy6t_Zjcdo-nI0jJHHcEfvoEl2Y9VCExaqaemAMgw4Eb3067acJXqHv2qsaIb--MUeJb67sQsltX6JGh6cQKg=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgDrpTHUZ2lEKfea9b2FIjO8GLxAhQ7-rYPnFFFxzsjcm1smcM3FCpnfnj5dQHrSFGK-wEtk9eO9OyXAi7SUZ_rdCHD_DOM0lL7fR5rfm9dsbFNiHPkC7c0A==)
4. [cam.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpzw2_otecMomWQ-S-XsbCGB4gO08DbANUy9XQ4cvfvJCXZ4ok4wb6qW9sSdupK7X9ADdGygGT_MCs7nLlKQTgWiAFD_gW06yXOhy2JtTngkjeUWoSzAfB5j5Ktr7c1V8=)
5. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZSPZBQRUMJ5Pvy-b1QvrlUFaYey6yZ9xK9DwZEncbtncSfJH_b2Ihuh3Tu9Wm_FZ0zwWLBtaBp-9B5x0YjLYpkTbRN4Wdxi8bs9tA1Vbf8SwACZ7ONyst1YTVYe9Wg01dsbCUqAMA5BRVaRUfdJgPCay0J__x6yg=)
6. [raymondvanbommel.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxr0K5tD46YIvm9TjqE6YWsE954EwZCsmzUUmRzKuNfkms4FXFoV1aPYZoDEyn6U3y-CVYSCjx9tlolfcHYBaeBBbV9h1xQiTxFwRRrWPUcmexiFXQ2a3u6N-exZEDs3qPo9hR7_M=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxjSTmmO-mRYSxWpWW4rMSlk4tQQ9rmQgHuPkVL71kYhsk5SL9noA0GmdIP0vYQa_l4UCpKJeZ4LeG3pQaVLBnXVKfS99RNCCu0NwnXwEwUfJSptddfJDJmg==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElUPNleN7Th_h9H3hkAkjCR9qPF7kNhl_Irkvj8zYRTQwshwotmEvc2coYlJ4bQM1M-PJ7riMTa_8eA3MlmS8dNbXL8qRbzI8KDkpxGKoFboMVL9c4tQ==)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEM3ndxiHpxH4luPFq01uiKKUL3LAS-LAz_0e-QyoSgoJeY9GxxiOFIsjtZ7__KSIp1vOF9oZPNXWhwQkBNwbieHtnyN5T__Ld3WASjp2p1esuIaP8fBu3w6mZvtOhXUoEVfgW-n5_Nu0sJGbscb3hZS47zguRHlqqm4pc_WiikE3ix-14tSP9pYxVOYhb6BOUu)
10. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJuN38akWYDXKwW3XXROThmWp-_GgAFAxblcNzcclWnmJ3BRraPDa5Gp98_rLJNPo7IV-eDCL3rk6q-SPTb_XZoca9A0iT9qFd0o1bCOb9epbaEjP7rpglbxVX2NuEOOqz56Y6_Vc2bEA=)
11. [imperial.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGghnF8CgGaCaYCDeX4moitK_hl6DLnnWOJY1aRUat8_W8_FjpeznY29Ec4r5DAMv9ZkQeDq0gKwMNgcR23ClRvVpi5Dbd1sp-EYxhvm-wCkjCh1fmDJDSB5ROvvDhlfLVAcJltLhDXdSXugfguMfPB)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH16GP_fFuoiTY4qs_4AwVqzxkUi3ZG7fOLver7zbqN1i3t9sJs_bPn9hNDcAJVgCQwpzKKgMKDeNh6P6BlHrfGTuhZaUuVaRO4cA9niJckcjyvKI6_0Q==)
13. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQYBCvnhv6aUOc4yyPRNvMAvTBpBdoUawcm837h624dpt6txpBU73oSSZ_Wu-13hFMAfIXNsPmr_1QKo6v8w-ofiVd4kKgFxKsmFot3687gOSARGV3FJFP2gssnb_IoTx4dd1SuI9iTgA9jHZeZs8Jtq8=)
14. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7mSMZDCKv77eNhd3PVLw2zbQbA7seuWun8z1v2dIAc8c3Gfonc4nFd2X8dBzXkiKjXuED9sQRxYAmYq8Y6RYa_bfdYfmmi888s7ZxXROuEJh3EQIhQSDdN5mHbTp7tRchIVZIP0nH_StVWXciMNNWpxycfrxHeh40QBRI0mp_FsC09O_zN0a6T73Bz-DEwDFSxHKFI4wSLqYO62A58bQRrA==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5WKFqxwP7gbteOAOiPKBcD6pRstJuugc4VGHASA3dc9p78qe83FxZxLoQmNaBMdfDogXcFS0g-P7JiwmkRwfMs5dGKtssMCdVOVbWFJBE8RbjC0EJ8B1E0w==)
16. [uni-bayreuth.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEd8ZPUk30FggHaGBGK2Z7FuCBxbjzqnCcxccI1T-XNNvT-1gBtwmG1ruNfR21OC88OYn95vRHEIzXO_2wyjteqHC6nVgOH7KMybL88d4IDonHeYHcP0HweqAoLNeAR0yKEF-kjcFvGK4i-oVVtfRwZZnpeNOD5Aw==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFM7peXd1BuAKWZGfJ6mSdkE3bIBI-qI8ndCKvQAQfcODX5zMRssDPt98rTG51l6ApcOV5MUgTAY0gJjI8ZOq7gS-R9E9khIZtvOxHF5ZnZYjCJ4NFIBw==)
18. [timo-keller.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkbzQVoCSh95DCRaLHmVv2BR4YGYsgTgEJypkQmx7KTCg9t1Kc6kwg_ZdhZmew8pYD76yPs1HQl0tfKKBWWGw7UBvHW5oN6Oh7wqX_hRoph9aTxGijC7lw8g1kCNJ0sJfUAA==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-AdDDht8Obw2uAG4CrHVF2IGYeHvGHj9DeLwfo7nc5irGGshwigv5OIH_2G13j4Juy3roLh4ISltnj4aKv03LvxbNV-2Z4K-c6_ZeK82rzNXqi3r9Jg==)
20. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFP9DfLqbTUgO2cVUChDbmT2HNZmqiUsoPNdoBzFZaFz-ma97pP0IOsWhWYs08yO70D-9WhlKIWIyDOdrIPgiWZMTVxDOaB_eQe5g0y3kz-DlGjTiesNF13UGV__Fs4xcyV_zFF5S71C0EYr5qDcSYGTczwU6RxckIS04yaAZhazb0BIj63jQKcnO3UN4F8Az1Wh6gbEuoL2OaCFrehb4WLmji_9mfwmHmSl5KsK8rGsd4_34ZMylqq1QubpQ7mAlipM7QKscNJFT43MlvLOBIe18zXJ1WYEsM66jU-6Jd9QWJOAFucDOvKWLDzXGSvTzk2o-R5SOz1obZVcgs-uM4XftLkhAYcAfliEM9l-oMMp8D5RW0KiimY2ZE=)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwwjRRMewTjtyeA1gc5jNR-WYZ859uv8ikuBT1Ik_s7NmbPtOcyhQngT_pb7bCYfb0Fwga_cbCUAWnypjIyFkUwGsAl9Ulkb8dkw43qpE52S4woAQC3gDuD6pxYPka4wAOyM84C0DtvH-d7e1wnHxq_0noHwgdjXTjjvB5PXsy3E4O)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAQQ43w4UnmbIlR6HT315jaxT52O6HjA5KZsTfTe5kz6_MCz2h8-9SCN7cLDjdr0dJ9tmKgmqAh0XLW4OOit0IDGpHxQCO7CpRGHOvcegphVLf8LnRtlqZrKtnzUtmCXihLqTK5vtmA-Hr6CWKHATG-bV3o343SrVAP3EumwmfrYE=)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSmzfg1aGr9Rdf2wWHJRC9lWCisKcBXAGoaPv4DZ8V4QAREFQcDibQuVHXA7cI72jEsQwn2zXDgtQQFHY1MsqnayrviWTF3yrOBv1c-liHjMKKH2wDHA==)
24. [keio.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQES_MMBKWj1hw66O3pGJwFAOaijLxJN2NrsoZ_g-U3BTxDvAg18ghVF757HXHdr7EUCrXMyUPDgtIjEbIkqKWX6CT9VnVOR9Ulod9TsqZyFmiNPQGxdxzGqZwTifQIqXWBC28MvQVqGpG-_uQ==)
25. [bourbaki.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUEE29yGh4JXWJapsi2N6MzY1d-VJzPuS6UG4ZVuAMCliIS3ZOwfQ2aZTk36v7Q0zhHvbVIalJafF-9_ZAwizucGTLraQdU0xzEiQRA_dsTj0iegOXN3b0b9hZ2sg9qliWeLyOG2b3tA==)
26. [esaga.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxaPjz-k8uPdwl0qJM7ySyiyKmxhvE2DuB_zH_H5nA0UTy4mOpPEE7Q7GGlX7ArrVx_2m91zNnt_jsVX4rYuVmeSBJLaZKHye7SF-hfUq-J4uE_eXv0ntATf7kcvKtAA==)
27. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWY-G2J31qXf_A7556lzC7ujwoRWpOA4U-XIvk5HIeIYPUkicEsHPFRaMIuJPjIDpNBPy1QQI2LIEiE1ruXBwHB7xhq00L2oKAG8G0cOIOjNKO5D6yzWlV31fqXo8CvXA8FUQiSOc=)
28. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFN3TRW5SDslD_PfNqlWIhAjBzj_YtDJsyTE880FsBpwmPqcrt0i-GFwwyF_I0afwYLWxpDrGsQGbu-hUo50eEakT1znmdz2r2d4DN0dPNhJmJMCu1VXA8roTlhS2ye1d8f0et9QYuYCLRzOzu11XA9IJqDYVVmrke7G1KcP-A=)
29. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHJd_OE2-FsTzsphPnbaZvFilZQ-aEVYh6SOuKKQhlpkWeSs6RJZzsG2JBi6SCB1OfYizFXzunOPqp_ydiaudYrf3BpZIoVqdrEG0Kvy_1u1mKgsVIiM4N6m9hEJT3DU6ZleVW3svkupFVL3YUH7L6vAg0uq2kfQ==)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKr_swlEp64r7oHWe7RuLsFJI0BvkWVZwfYyj3nNxWU05wauNrv4w9uh0VaVQIM2OJJJVYIF9jb_M7SR7gtamKZJy2LOS0o6rbwrcFlZPLdh_yhbaBDQ==)
31. [carmin.tv](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmG_g_kFC1JqKI_VrKCJGvWYSHw-xlZmkwMLYVcmrMN7PtYNmLIlxPSk6xG2E8EJaVXAIDzH-8pENR2fcxtjnMoJPgw83oB94n5FVjjfk68PIlZV8sxitUYkYVAopOopK9avxhzRFhm20iyyo1-IZbU06TC7aWGePCsDhgge5maU5CtweLq_9ze7_AZoqZWjXRhAlmzr9BQuTsh0OP8M_YNB0qPOQlEGUEnQQIKEoYHpX-v5MLUWLcx0wL84BiwKkO8uzmcuGQnUymbZvbfO_f-bdOX-EoBfRL18upbbkoxv4IyV-doRHQw4BPP38EVtDGYGSQRc1jYqZFs7QgBlm8)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUUkfOu7CggsnxUU-kcCpuQ2aJqo3htr3_Ysh0pyZibEFAKZhkQaLVvOB6M5NFe8PbVuHdRZbS0U0hbC-N9WUA4CKjnW0B9XlBpNgnSiArosTel3HyAg==)
33. [unidistance.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQvOMWeRplt2DPsiDyARI5Pfjq_2RRYX4ZglTK_jDVDAFNFgtkBbCQssNShUdxVlLDNZZZCeJVTRsVcSNdGfN_JXsxx5QkgraTVmMHv0UmEeWEU6AQ6gOBHN6Zd9HD6cjgMBhfZZI=)

