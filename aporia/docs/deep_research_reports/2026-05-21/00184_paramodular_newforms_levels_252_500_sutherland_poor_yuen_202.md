# Paramodular newforms levels 252-500 (Sutherland-Poor-Yuen 2025 extensions)

**Pythia queue id:** 184
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc2RDBQYXZUZ0RvUzBqTWNQalBuQThRaxIXNkQwUGF2VGdEb1Mwak1jUGpQbkE4UWs
**Elapsed:** 311s
**Completed at:** 2026-05-21T17:21:36.750711+00:00

---

# Comprehensive Analysis of Paramodular Newforms in Levels 252–500: The Sutherland-Poor-Yuen 2025 Extensions

*   **Key Points:**
    *   Research indicates that the catalog of rational weight-2 paramodular forms is now provably complete up to level 251, a significant milestone achieved by Poor and Yuen in 2025. 
    *   The level range of 252 to 500 represents the current frontier of computational number theory in this domain, relying heavily on heuristic tables and advanced algorithmic extensions.
    *   The Paramodular Conjecture, which posits a deep link between abelian surfaces over the rational numbers and Siegel paramodular newforms, remains one of the most compelling open questions in arithmetic geometry.
    *   While a generalized proof remains elusive, mathematical techniques such as the Faltings-Serre method have successfully proven the modularity of specific abelian surfaces in the 252–500 range, most notably at conductors 277 and 353.
    *   It seems likely that overcoming the current computational roadblocks will require novel theoretical breakthroughs, particularly because we currently lack dimension formulas and a direct analogue to the Eichler-Shimura construction for genus 2.

**Understanding the Frontier of Genus 2 Modularity**
In the study of modern number theory, the relationship between algebraic geometry (shapes and curves defined by equations) and automorphic forms (highly symmetric analytical functions) is a central theme. For "genus 1" objects—elliptic curves—this relationship is famously established, meaning every elliptic curve over the rational numbers corresponds to a modular form. Mathematicians are now focused on "genus 2" objects, specifically abelian surfaces. The Brumer-Kramer Paramodular Conjecture predicts that these surfaces correspond to a specific type of mathematical object called a weight-2 Siegel paramodular newform. 

**The 251 Threshold and Beyond**
Computing these paramodular forms is incredibly difficult. As of 2025, researchers Cris Poor, David S. Yuen, and Andrew R. Sutherland have definitively completed the list of these forms up to level 251. However, the levels from 252 to 500 represent a "wild west" of computational exploration. In this range, researchers cannot easily prove they have found *all* forms, but they can identify specific candidates using highly complex algorithms. By cross-referencing mathematical databases of curves (led by Sutherland) with heuristic tables of forms (constructed by Poor and Yuen), mathematicians are successfully finding "matches" where the geometric and analytical data perfectly align, slowly extending the boundaries of human knowledge in higher-dimensional arithmetic geometry.

***

## 1. Introduction to Paramodular Forms and the Langlands Program

The Langlands program postulates a vast and profound network of correspondences linking Galois representations, arithmetic geometry, and automorphic forms [cite: 1]. The most celebrated triumph of this program is the modularity theorem for elliptic curves over the rational numbers $\mathbb{Q}$, which established a bijective correspondence between isogeny classes of elliptic curves of conductor $N$ and classical cuspidal newforms $f \in S_2(\Gamma_0(N))$ of weight 2 and level $N$ with rational Hecke eigenvalues [cite: 1, 2]. This correspondence guarantees an equality of $L$-functions: $L(E, s) = L(f, s)$, enabling deep insights into the arithmetic properties of elliptic curves, most notably through the Birch and Swinnerton-Dyer conjecture [cite: 3].

Moving beyond $\mathrm{GL}_2$ and elliptic curves, the natural generalization involves higher-dimensional abelian varieties, specifically abelian surfaces (dimension $g=2$). Yoshida initially proposed that abelian surfaces should relate to Siegel modular forms of degree 2, which are automorphic forms for the symplectic group $\mathrm{GSp}(4)$ [cite: 4]. To formalize this, one must define the appropriate domain and symmetries. The Siegel upper half space of degree $n$ is defined as:
\[ \mathcal{H}_n = \{ Z \in M_{n \times n}(\mathbb{C}) : Z^T = Z, \text{Im}(Z) > 0 \} \]
For $n=2$, Siegel modular forms of weight $k$ are holomorphic functions $F: \mathcal{H}_2 \to \mathbb{C}$ that satisfy a specific transformation property with respect to a congruence subgroup $\Gamma$ of $\mathrm{Sp}(4, \mathbb{Q})$ [cite: 5]. The slash action for a matrix $\sigma = \begin{pmatrix} A & B \\ C & D \end{pmatrix} \in \mathrm{Sp}_n(\mathbb{R})$ acting on $Z \in \mathcal{H}_n$ is given by $\sigma \cdot Z = (AZ + B)(CZ + D)^{-1}$, and the transformation rule is $(F|_k \sigma)(Z) = \det(CZ + D)^{-k} F(\sigma \cdot Z)$ [cite: 6, 7].

Historically, much attention was paid to the principal congruence subgroup $\Gamma_0(N)$. However, the theory of newforms for $\mathrm{GSp}(4)$ developed by Roberts and Schmidt demonstrated that to obtain a robust newform theory with a one-dimensional space of invariant vectors at the local level, one must use the paramodular group $K(N)$ [cite: 5, 8]. The paramodular group of level $N$ is defined as the intersection of $\mathrm{Sp}(4, \mathbb{Q})$ with the group of matrices of the form:
\[ \begin{pmatrix} \mathbb{Z} & \mathbb{Z} & \mathbb{Z} & N^{-1}\mathbb{Z} \\ N\mathbb{Z} & \mathbb{Z} & \mathbb{Z} & \mathbb{Z} \\ \mathbb{Z} & \mathbb{Z} & \mathbb{Z} & N^{-1}\mathbb{Z} \\ N\mathbb{Z} & N\mathbb{Z} & N\mathbb{Z} & \mathbb{Z} \end{pmatrix} \]
This group stabilizes the lattice $\mathbb{Z} \oplus \mathbb{Z} \oplus \mathbb{Z} \oplus N\mathbb{Z}$ and is deeply connected to abelian surfaces with polarizations of type $(1, N)$ [cite: 7, 9]. A cusp form for the paramodular group $K(N)$ of weight $k$ is denoted $S_k(K(N))$. Within this space, there is a subspace $S_k(K(N))^{\text{new}}$ consisting of newforms, which correspond to the lowest level at which a specific automorphic representation appears [cite: 5, 8].

## 2. The Paramodular Conjecture: Bridging Geometry and Automorphic Forms

Formulated by Armand Brumer and Kenneth Kramer, the Paramodular Conjecture acts as the genus 2 analogue of the Taniyama-Shimura-Weil modularity theorem [cite: 4, 10]. It posits that there is a one-to-one correspondence between isogeny classes of abelian surfaces $A$ over $\mathbb{Q}$ of conductor $N$ with trivial endomorphism ring (specifically, $\text{End}_{\mathbb{Q}}(A) = \mathbb{Z}$) and cuspidal, nonlift weight 2 Siegel paramodular newforms $f \in S_2(K(N))^{\text{new}}$ with rational Hecke eigenvalues, up to scalar multiplication [cite: 11, 12].

The stipulation that the newform must be a "nonlift" is critical. The space of paramodular cusp forms $S_k(K(N))$ contains a subspace generated by Gritsenko lifts (also known as Saito-Kurokawa lifts). A Gritsenko lift, denoted $\text{Grit}(\phi)$, maps a Jacobi cusp form $\phi \in J_{k,N}^{\text{cusp}}$ to a paramodular form in $S_k(K(N))$ [cite: 2, 5]. These lifted forms correspond geometrically to products of elliptic curves or abelian surfaces with extra endomorphisms (like real multiplication), which are not "typical" or "generic" abelian surfaces [cite: 2, 7]. The Paramodular Conjecture specifically targets "typical" abelian surfaces, hence the exclusion of Gritsenko lifts and the focus on "nonlift" paramodular forms [cite: 1, 2].

When the correspondence holds, the Hasse-Weil $L$-function of the abelian surface $A$ perfectly matches the spin $L$-function of the paramodular form $f$:
\[ L(A, s) = L(f, s, \text{spin}) \]
This equality implies that the Euler factors at all primes $p$ (both of good and bad reduction) agree [cite: 2, 13]. For primes $p \nmid N$, the local Euler factor of the abelian surface is a polynomial of degree 4, matching the characteristic polynomial of the Hecke eigenvalue data generated by the two local paramodular Hecke operators $T_{0,1}(p)$ and $T_{1,0}(p)$ [cite: 5, 9].

## 3. The 2025 Horizon: Provable Completeness up to Level 251

The computational landscape of weight-2 paramodular forms underwent a paradigm shift in the early 2020s, culminating in the 2025 updates provided by Andrew R. Sutherland, Cris Poor, and David S. Yuen. As explicitly detailed in Sutherland's 2025 reports, current tables of rational weight-2 paramodular forms are provably complete only up to level 251 [cite: 3, 14].

The threshold of $N=251$ is not arbitrary; it represents the current absolute limit of rigorous bounding techniques for spaces of weight-2 paramodular forms. In weight 2, the classical approach of using the Selberg trace formula or algebraic dimension formulas fails because weight 2 forms lie at the edge of the coherent cohomology, rendering standard Riemann-Roch-Hirzebruch index theorems ineffective for isolating cuspidal dimensions without massive cohomological error terms [cite: 3]. 

Before this 2025 milestone, Poor and Yuen had established extensive but partially heuristic tables up to $N \le 1000$ [cite: 15]. By employing a novel technique known as "Humbert restriction"—developed by Breeding, Poor, Shurman, and Yuen—they managed to bound the dimension of nonlift newforms [cite: 9, 16]. Humbert restriction involves restricting the paramodular form to various Humbert surfaces embedded within the Siegel upper half space. If a form vanishes on sufficiently many such divisors, it must be identically zero. By proving that the space of forms with a given set of initial Fourier-Jacobi coefficients is bounded by the known Gritsenko lifts and explicitly constructed Borcherds products, they proved completeness up to level 251 [cite: 6, 16].

A fascinating insight from the $N \le 251$ database is the extreme scarcity of generic abelian surfaces. The provably complete list up to level 251 includes only *one* generic case: level 249 [cite: 3]. In $S_2(K(249))$, there is a one-dimensional space of nonlift newforms with rational eigenvalues [cite: 15]. However, despite the existence of this form, the geometric counterpart remains elusive: as of 2025, mathematicians have yet to prove the existence of an abelian surface over $\mathbb{Q}$ of conductor 249 that possesses this exact $L$-function [cite: 3]. This discrepancy highlights a fundamental asymmetry in the Paramodular Conjecture: while we can compute forms (albeit with immense difficulty), constructing the corresponding geometric varieties is an entirely separate and sometimes harder problem.

## 4. Traversing the 252–500 Level Range: Methodological Extensions

With rigorous completeness halting at $N=251$, the level range of 252–500 serves as the primary testing ground for the Sutherland-Poor-Yuen 2025 extensions [cite: 3]. In this intermediate regime, researchers transition from global completeness proofs to heuristic tabulations accompanied by targeted, rigorous proofs for specific conductors.

### The Construction of Heuristic Tables
To explore levels 252–500, Poor and Yuen rely on classifying initial Fourier-Jacobi expansions [cite: 6, 15]. A Siegel modular form $F \in S_k(K(N))$ can be expanded in a Fourier-Jacobi series:
\[ F(Z) = \sum_{m=1}^{\infty} \phi_m(\tau, z) e^{2\pi i m \omega} \]
where $Z = \begin{pmatrix} \tau & z \\ z & \omega \end{pmatrix} \in \mathcal{H}_2$. The coefficients $\phi_m$ are Jacobi cusp forms of weight $k$ and index $Nm$ [cite: 9]. 

The heuristic methodology assumes that a paramodular form is uniquely determined by a small number of these Fourier-Jacobi coefficients (FJCs) [cite: 6]. By constructing spaces of Jacobi forms and enforcing the paramodular condition (which imposes infinite systems of linear equations on the coefficients), Poor and Yuen can identify the "apparent" dimensions of $S_2(K(N))^{\text{new}}$. 

In the 252–500 range, these heuristic tables reveal several isolated nonlift weight-2 newforms. For instance, the tables identify dimensions of nonlift newforms at levels such as 277, 295, 349, 353, and 388 [cite: 15]. The current "Humbert restriction" work in progress (as of 2025) aims to push the boundary of rigorous completeness from 251 up through 388, systematically confirming that the heuristic dimension is indeed the true dimension [cite: 16].

### Constructing Paramodular Forms via Borcherds Products
When a heuristic computation indicates the presence of a nonlift newform, mathematicians must explicitly construct it to study its Hecke eigenvalues. One of the most powerful tools for this in the 252–500 range is the Borcherds product. 

Borcherds products allow for the construction of meromorphic Siegel modular forms whose divisors are linear combinations of Humbert surfaces. To construct a holomorphic weight-2 cusp form, researchers first build a Borcherds product of higher weight (or with poles), and then multiply it by other modular forms (such as Gritsenko lifts) or divide it by forms of lower weight to isolate the weight 2 object [cite: 2, 17]. 
For example, Poor, Shurman, and Yuen utilize "theta blocks" to build Jacobi forms, which are then lifted to paramodular forms. Ten specific weight 2 theta blocks (denoted $\Xi_1, \dots, \Xi_{10}$) were instrumental in constructing the paramodular form at level 277 [cite: 1, 2]. The resulting form is often expressed as a rational function of these Gritsenko lifts of theta blocks [cite: 1].

## 5. Algorithmic Innovations in Computing Paramodular Forms

A major hallmark of the 2025 extension era is the diversification of computational algorithms. Because Fourier-Jacobi expansion calculations become prohibitively expensive as $N$ grows toward 500, researchers like Gonzalo Tornaría, Gustavo Rama, Eran Assaf, and John Voight have developed alternative approaches utilizing orthogonal modular forms [cite: 4, 10].

### The Ibukiyama Correspondence and Orthogonal Modular Forms
The Langlands program predicts that paramodular forms for $\mathrm{GSp}(4)$ correspond to automorphic forms on orthogonal groups. Specifically, Ibukiyama conjectured an explicit correspondence between paramodular forms and modular forms for a compact twist of the symplectic group, specifically a definite orthogonal group $\mathrm{SO}(5)$ associated with a quinary quadratic form [cite: 4, 10].

A quinary quadratic space $(V, Q)$ over $\mathbb{Q}$ allows one to define algebraic modular forms. Let $\Lambda \subset V$ be a $\mathbb{Z}$-lattice. The space of orthogonal modular forms of level $\Lambda$ and weight representation $\rho$ is essentially the space of functions on the class set of the lattice $\Lambda$ [cite: 4]. Because the class set is finite and the group is compact, computing these forms reduces to finite linear algebra [cite: 10, 18].

For a prime level $p$, the algorithm selects a specific genus of positive definite integral quinary quadratic forms with discriminant $p$. By utilizing $p$-neighbor graphs (following Kneser's algorithm and Plesken-Souvignier lattice isomorphism testing), researchers can compute the action of the Hecke operators $T_{p,1}$ and $T_{p,2}$ [cite: 4]. 

This method was heavily utilized to compute spaces of paramodular forms of weight 3 (which correspond to trivial weight representations for the orthogonal forms). Hein, Ladd, and Tornaría computed orthogonal modular forms for prime levels $p < 500$ [cite: 10, 19]. In 2023–2025, Assaf, Rama, Tornaría, and Voight extended this framework to non-squarefree levels and cohomological weights, finding an average speedup factor of roughly 11 compared to traditional methods by implementing algorithms in C and PARI/GP [cite: 4, 8, 18]. This orthogonal approach bypasses the need to compute millions of Fourier coefficients, generating Hecke eigenvalues directly [cite: 10].

However, the Ibukiyama correspondence has limitations. While it beautifully captures forms of generic type (G), one must carefully filter out forms of Saito-Kurokawa type (P) and Yoshida type (Y) which appear in the orthogonal space [cite: 8]. Furthermore, extending this method from weight $\ge 3$ (cohomological weights) to the crucial weight 2 (noncohomological) remains mathematically troublesome, though active research is bridging this gap [cite: 8].

## 6. Abelian Surfaces and Genus 2 Curves: Sutherland’s Computational Database

The other side of the Paramodular Conjecture requires finding the abelian surfaces that match the automorphic forms. Andrew R. Sutherland, alongside collaborators like Andrew R. Booker, Jeroen Sijsling, John Voight, and Dan Yasaki, has spearheaded massive computational efforts to tabulate genus 2 curves and their $L$-functions [cite: 8, 20].

An abelian surface over $\mathbb{Q}$ is often, though not always, the Jacobian variety of a genus 2 curve [cite: 3]. If an abelian surface is not a Jacobian, it is a Weil restriction of an elliptic curve over a quadratic field, or a generic abelian surface embedded in high-dimensional projective space (e.g., $\mathbb{P}^{15}$ defined by 72 quadratic forms, which is computationally abhorrent) [cite: 3].

To find these curves, Sutherland's team employed massive parallel computing on Google Cloud Platform, using over 100 vCPU-years to enumerate more than $10^{19}$ genus 2 curves looking for those with small conductor [cite: 20, 21]. The computational strategy involves iterating through the coefficients of hyperelliptic curve equations $y^2 + h(x)y = f(x)$ using highly optimized monomial trees to rapidly test the discriminant $\Delta$ for smoothness. Testing if $\text{rad}(\Delta) \le 10^3$ can be executed in under 5 nanoseconds per curve using SIMD parallelism and AVX-512 instructions [cite: 20].

By 2022–2025, this effort produced over 66,000 curves in the LMFDB (L-functions and Modular Forms Database) up to conductor 1,000,000, yielding over 20,000 distinct $L$-functions [cite: 20, 21]. 

For conductors $N \le 1000$, assuming the Paramodular Conjecture, Sutherland established that there are exactly 456 $L$-functions of abelian surfaces. Breaking this down:
*   360 arise from products of elliptic curves (matching Gritsenko lifts).
*   17 arise from weight-2 newforms with quadratic coefficients.
*   2 arise from Weil restrictions.
*   77 arise from generic abelian surfaces, of which at least 67 are Jacobians [cite: 21].

A crowning achievement of this search was the discovery of a genus 2 curve of conductor 903 [cite: 20, 21]. The $L$-function of its Jacobian perfectly matched the Hecke eigenvalues of the paramodular form of level 903 computed by Poor and Yuen [cite: 20, 21]. Prior to this, the level 903 form was the last explicitly known paramodular form from Poor and Yuen's tables that had not been matched to any known abelian surface [cite: 16, 20]. The discovery of the 903 curve essentially completed the empirical verification of the Paramodular Conjecture for currently computable explicitly known forms [cite: 20].

## 7. Case Studies in the 252–500 Range: Rigorous Modularity Proofs

While compiling tables and matching $L$-functions computationally provides overwhelming evidence for the Paramodular Conjecture, it does not constitute a mathematical proof. To prove that $L(A, s) = L(f, s)$, mathematicians must prove that their associated Galois representations are isomorphic. This has been achieved for a handful of conductors in the 252–500 range, representing the vanguard of the 2025 extensions.

### Level 277
Level $N=277$ holds a special place in the theory. By the work of Brumer and Kramer, 277 is the smallest prime conductor for which an abelian surface with trivial endomorphism ring exists [cite: 1, 13, 22]. In their heuristic tables, Poor and Yuen identified a 1-dimensional space of nonlift paramodular newforms at this level [cite: 1, 15]. They explicitly constructed this unique form as a rational function of Gritsenko lifts of ten weight-2 theta blocks [cite: 1, 2]. 

Using the Faltings-Serre method, researchers extracted the 2-adic Galois representation attached to the paramodular form $\rho_f$ and the representation attached to the abelian surface $\rho_A$. By computing the characteristic polynomials of the Hecke operators modulo 2, they showed that the residual mod-2 representations share a common image in the symmetric group $S_6$, specifically the subgroup $S_5^{(b)}$ (up to conjugation) [cite: 2]. After establishing congruence modulo 2, the Faltings-Serre method dictates that one must verify the equality of traces (Hecke eigenvalues) up to a computable bound. For $N=277$, matching traces for all primes $p \le 43$ was sufficient to categorically prove that $\rho_f \simeq \rho_A$, thus proving modularity for this abelian surface [cite: 1, 2].

### Level 353
The conductor $N=353$ is the next prime level where an abelian surface exists (LMFDB label 353.a). Following a similar playbook, Poor and Yuen constructed the nonlift paramodular form explicitly [cite: 1, 15]. In this case, the residual Galois representation modulo 2 has its image in the wreath product $S_3 \wr S_2$ of order 72 [cite: 1, 2]. By matching Euler factors and applying Faltings-Serre, the modularity of the 353.a isogeny class was rigorously proven [cite: 1, 2].

### Level 587
Though slightly beyond the 500 threshold, level 587 demonstrates the flexibility of the 2025 methodologies. The form for $N=587$ was not represented as a rational function of Gritsenko lifts, but rather as a Borcherds product [cite: 2]. The mod-2 Galois image was the full symmetric group $S_6$ [cite: 2]. Tracing the eigenvalues computed by Breeding, Poor, and Yuen proved the equality of $L$-functions here as well [cite: 23].

### Levels 295, 349, and 388
Within the strict 252-500 range, composite levels like 295, 349, and 388 have heuristic dimension 1 for nonlift newforms [cite: 15]. Humbert restriction techniques have isolated these forms, and algorithms continue to evaluate their Galois representations to extend the list of rigorously proven modular abelian surfaces [cite: 16]. Notably, composite levels add complexity to the local newform theory (specifically calculating the $T_{0,1}$ and $T_{1,0}$ operators which can mix Fourier expansions at different zero-dimensional cusps) [cite: 5].

## 8. The Faltings-Serre Method for Siegel Modular Forms

The engine driving the rigorous proofs of modularity in the 252–500 range is the Faltings-Serre method [cite: 2, 11]. Originally developed by Faltings to prove the Mordell Conjecture, and adapted by Serre to show Galois representations are isomorphic, its application to degree 2 Siegel modular forms was pioneered by Boxer, Calegari, Gee, Pilloni, and explicitly executed by Brumer, Pacetti, Poor, Tornaría, Voight, and Yuen [cite: 2, 22].

To establish paramodularity for an abelian surface $A$, one investigates the absolute Galois group of $\mathbb{Q}$, $\text{Gal}_{\mathbb{Q}} := \text{Gal}(\overline{\mathbb{Q}}/\mathbb{Q})$. The abelian surface provides a 2-adic Galois representation $\rho_A: \text{Gal}_{\mathbb{Q}} \to \text{GSp}_4(\overline{\mathbb{Q}}_2)$ acting on its Tate module [cite: 2]. 

Conversely, attaching a Galois representation to a weight-2 Siegel paramodular form $f$ is a monumental task. The archimedean component of the associated automorphic representation is a holomorphic limit of discrete series, meaning it does not unconditionally appear in the interior cohomology of the Shimura variety [cite: 2]. Recent breakthroughs in $p$-adic overconvergent modularity lifting and completed cohomology by Boxer, Calegari, Gee, and Pilloni have allowed for the rigorous construction of these representations [cite: 1, 11].

Once both $\rho_A$ and $\rho_f$ are secured, the Faltings-Serre method proceeds in two steps:
1.  **Residual Isomorphism:** Show that the mod-2 residual representations $\bar{\rho}_A$ and $\bar{\rho}_f$ are isomorphic. This is done by computing the Euler polynomials $Q_p(f, T)$ modulo 2 for a few small primes $p$ (e.g., $p=3, 5$ for $N=277$) and identifying the common finite image in $\text{GSp}_4(\mathbb{F}_2) \simeq S_6$ [cite: 2].
2.  **Trace Verification:** Construct the finite extension $K/\mathbb{Q}$ over which these representations factor. If the representations agree modulo 2 and lift to characteristic zero, there exists a finite, effectively computable set of primes $S$ such that if $\text{Trace}(\rho_A(\text{Frob}_p)) = \text{Trace}(\rho_f(\text{Frob}_p))$ for all $p \in S$, then $\rho_A$ and $\rho_f$ are strictly isomorphic [cite: 2].

Because Poor and Yuen specialize the paramodular eigenform to a modular curve, they can compute the power series in one variable exactly, deriving the exact eigenvalues necessary to check against the Hasse-Witt matrices of Sutherland's curves [cite: 22, 24]. This elegant synthesis of high-performance computing and profound algebraic number theory is what permits the rigorous verification of the Paramodular Conjecture on a case-by-case basis.

## 9. Structural Roadblocks: Dimension Formulas and the Eichler-Shimura Deficit

Despite the massive progress encapsulated in the Sutherland-Poor-Yuen 2025 extensions, generalizing these results beyond level 500 (or achieving provable completeness up to 1000) faces formidable theoretical roadblocks.

First, there are **no dimension formulas** for weight-2 paramodular forms [cite: 3]. In the elliptic curve case, calculating the dimension of $S_2(\Gamma_0(N))$ is trivial using the Riemann-Hurwitz formula on the modular curve $X_0(N)$ [cite: 3]. For $K(N)$, the associated Siegel threefold has a highly complex geometry, and weight 2 sits perilously on the boundary where the Hirzebruch-Riemann-Roch theorem produces unmanageable error terms related to non-cuspidal coherent cohomology [cite: 3]. Hence, the true dimension must be bounded explicitly by techniques like Humbert restriction, which scale terribly as $N$ increases [cite: 16].

Second, there is **no analogue of the Eichler-Shimura construction** [cite: 3]. In the classical case, if one finds a rational newform $f \in S_2(\Gamma_0(N))$, Eichler and Shimura provided a geometric mechanism to literally construct the corresponding elliptic curve $E_f$ as an abelian subvariety of the Jacobian of $X_0(N)$ [cite: 3]. For paramodular forms of degree 2, the converse of the modularity conjecture is actually false for $g=2$: finding a rational paramodular newform does *not* guarantee the existence of a corresponding abelian surface over $\mathbb{Q}$ [cite: 3]. Even if it did, we have no geometric "factory" to build the surface from the form. 

This forces researchers into a blind search: Poor and Yuen must compute the forms from the top down (using Fourier-Jacobi and orthogonal lattices), while Sutherland must compute the curves from the bottom up (enumerating sextic polynomials and checking smoothness) [cite: 20]. They then meet in the middle by matching Euler factors. If Sutherland's search space misses the surface (perhaps because it is a generic surface requiring 72 quadratic equations in $\mathbb{P}^{15}$ rather than a hyperelliptic curve), the form remains "unmatched," as was the case for $N=903$ until very recently [cite: 3, 21].

## 10. Conclusion and Future Directions

The investigation of paramodular newforms in the level 252–500 range, heavily advanced by the Sutherland-Poor-Yuen extensions of 2025, constitutes a golden era for computational arithmetic geometry. By establishing provable completeness up to level 251 [cite: 3] and aggressively pushing into higher levels through heuristic Fourier-Jacobi tables, Borcherds product constructions, and orthogonal modular forms [cite: 4, 10], researchers have laid an empirical foundation that firmly supports the Paramodular Conjecture.

The successful proofs of modularity at conductors 277, 353, and 587 using the Faltings-Serre method demonstrate that the deep connections posited by the Langlands program are structurally sound in genus 2 [cite: 1, 2]. Moreover, the discovery of the conductor 903 curve [cite: 20, 21] highlights the immense power of synchronized parallel computing and mathematical insight.

Looking forward, the community faces the dual challenge of theoretically grounding dimension formulas for weight-2 paramodular forms and improving the search algorithms for generic abelian surfaces. Until an Eichler-Shimura analog is discovered—if one even exists—progress will rely on the brute-force elegance of matching massive datasets of automorphic forms with equivalently massive libraries of algebraic curves, expanding human understanding of the arithmetic universe one level at a time.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFE5vgh5AA5_SaZrgobajtzrIHMN-xwPHC7gtqDdcGM6bG_Y60jpAZyWPS0rlVzeufbPr1Uf4r9c5xMw-CAxrxU_5jkmaVeYGh25Yy_FqNl11evB2LTfw==)
2. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKIKIIeZlx6TkzSFgcHpUo1yD4jGdnmOquY7FHvQiNDrKYmFJvn9hZCek3CFRTPPdcjELlT10G4jMbfmLBJNA2PJve8Y34vKiXGPVJBJ4y7gGXf-G_G5XLowueGKzaTi-QwfChx_nNOIF1fWz3JhbBMvacMaF1v6h8)
3. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWF7DinAFtOu-xKqc7Fd8XDj2MGJQplGVH2ImmVLVuBxL2ANI23eO-fd4fU3p1BvlXQCZnSku4alvwMmJwJtJGdO-Z0toTfSXXBJBhhpTGUFH5KyvbmOG2mcxm)
4. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFm4JxzIVs4-oVTdwAcWzfYtObiz4rjkVUgsSAdwVIhRrtHXcD1GPRk7oezuFth_5fA7G7eA4I3ZRp8aRhaACwvqWHANm5BrYdDS0MlCk7vFfBJRWqvQHEUgqOxn2v5s3wOkCpvdSobkeJgzx9jpA2pnp8vXyQT0dyddxwoP_-mkSJb6dWh-8ra)
5. [ou.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE38PTqioAhEd-294LayI0k746kteaKJfRd50IG22u5M7_D_9WhnYcfh_s6N13W7z8_4w_g1baIZ_R_OZ90A4dqhmuPM-C4ZujPFwX4knDH5pqb5fSyXQOm2RD6ZJpzKPoHJMgMENqdH9wjMAlT4RiRbkNEOorl5ZN8W28_)
6. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCHQNrGjiv7JAd3LBfgwDIexCl6B8ERpTItfPFR6PKawRY0c5oNcUoMfnWufl4g9VuDH1w5guqmxg_0L0AZseixZPt0kc03vyvz0I5LsCtMGlpxWvC8LJAG1T_nB4aV3a8Uo8xKanY2r64RpHL4AxqK6ki9Kj5neTQtuE-CXuxrFOxcexe7HK5guxQK8-2eZYEc-kSipX6bwyghN6BttR1BQrO_PuntqfbcxJ9txpxKww=)
7. [siegelmodularforms.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsIftNfxchOT7bCYkPSg-PvmhSGtVpd3BWOBsbmtdoD0y4YsxoBTL0GyeKW7oumTB7fGt_vLMlINU4rJIHH2RKTtIi2_Rrduae748m7y1zz2pn5SHlKKfYhyarTiWeTxxVCWSM-v6yvjjoGPvPNY_Ar1DVri7nFb7DIDS1m0UADNNcoTg=)
8. [lucant.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEm3SVlZmfcB7gr4KjFHYT2t1TjW-xmNSKEQkH4M9L9evVZ4ycIyaBuApSVLqmx_WQWUxDvb5v92cbD2V1BZ3YdxNfE4CbyqHYiqgb6zlOEIJHHd37a93EXGR0C5XtKDV0gAGBzWA==)
9. [uni-mainz.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGO9Dlghz4r-Yq54KWxHyFpOktJO6p3xmznEah8idxFD18FLCj3d0_s1SN4KJ3to6y01F49RxIJCDmFXHPPWROrD5sI2ZXa6W6D92Z-rgw7AeV4TZhIBLKzRt5MUUUqJdf5-tkDfEYtAF2uzTGr1_aqSN8Ca94V9N9le_kcr7aBKAaogfwFsjlCRKSIPA7p0H1QLSZHdEE0ggsLpb2g3qkTZnei80UpBd1tHuxrmmFyQmMWCb-g94X4ZOYA1-Dv1pBvZk-7twsDFyVQ3vUniCkwfR33QSQo6VTxU97nEuPny4msrb2H2CBaenvTspL6jDSdhzR_WtfX3Bk=)
10. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCW9ZeKJHceSEHcY9CYEwhrJ7SC_ZPIp9nYO5WaexKbUnmkZ5Xgu0GIm03oF_4aeuq0ga1TrQZBjBrS1mt27acbIbgejaxzH6e8CV_d4XJ5VZnhGmsWCbzI5RO-Adf9HRBpoStWos=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKh4umeQKYzbmGjnkt5GzOPQdmqr_ozvLrV9ihOCt_Hg8iO3vwFn9hYzF8AwOADQVqNJVJTSydfW250wUP44NgLq1Jlghi3kGDa-2AdydiAo2qB1A0bHBkMw==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqhFG3UR0n_ZzwQElb04jghLQ3FYMcrUV0l01-56F1RL6QeAKE9KPP8Zr2dNgRw455KE3SBNi8Uxpfu2saMoD56w4cdUJvaITYjGwEXkas0IDXwreI_Q==)
13. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQuSZ-aQXXvQ8b1J_CRScLZF6rskTPnyp_jJOU54cHtWAYcoqiE6XDYu9YJ6L1X7w60ri4zzVozCL3a9whxDKboPP-VSkrrNv5BhOwCG9xDLT6CCn2zAi2OuII8XclAdkF6AQm)
14. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGY4eKNhQin-ljY9mYE6-xzuMHeyH3JSKZD6hAvkQYxKPyfbsD6x73qtiC_svFbv-MR0GBHOBm9W-mXTLxjPsZDQD42wv2przwWMHeffS3-1rnpYHmkMe7jxjtQoFpvtIAtg3efAvNC)
15. [siegelmodularforms.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGN2Rbsu8VgSTY5svW1hnzpBPs2saCeUc6CP-GHCZ6XifET-XI5Zka86no5czyvxVwD1KdCqeD12J5yS-NwPxpWja3c85J7yJHPqSm-_2JRnGiPFf_D_5JQUtGQSujb4Ar9iJYi8n4PbJfcuodHO5OqtiB4CqxkPj2x_zjle0SpeXy7ScmRbqPhZ2sa8pWy)
16. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcBgvYYK6kSQm2tyoyobRuRKB-Rm9OD91_2hviiu2nE9Z4V1YS41Yc7Xz50zI-9cyI5n0nvPpGOv5pbkcHeyj5gWKxioBcaEVd7juqovTvJdijww0Nw-JTpkz0_BhmbFie-O0JnA-v4VGc)
17. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEYdHNfw1ePZojT6wpsUm2KUYNkx5yNcTVMG5VZnvwmyj0m0r-3i87_5v3fuezRRDktdXyX42x39CPfsS7Mjd7TTXChxGzXm-M_jEOErNUOfUjbyzLkAQGLvOqeILVDw==)
18. [udelar.edu.uy](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLYVyj3AbIHl1xVnn-Uvwel5X9XlZz5TpFtKWxuTxAsKl9FCxivJai7ykuPU6CFrXDBp1NetenbneSneKI0S7YUofS9DH5-4lsmVGFoGSHMcYkzxqzwYx11fEDeT7YsTWAR4F3Ta7O6kv6fW0K37P_w0ejcRVXOcdkNFQk3sE55V62VtkWA_oVHsoMI8c=)
19. [auckland.ac.nz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFz9Qq6pI_H2JhtVu5wflp99-bSREzvG17b-SP0tJ4QfBiJw5oZImdxTf_nWKwpqr0uXVvs_4pE1xs0K6tHUuex7XNTM2f0WbOvl8DW2LC7CgN1rgFxKMEJZTX3o4gKK-c4HaKcqCkZkkZaasCp_QARENpUCRE22whtw8cF)
20. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcFPL6QQivC7VOAyfUdF8UBjwA1EY4C8MG3zD-4vlgUMXMcY3ox_gC3qAa8AQLn6_40ZQHwUPZz_CLXF8wwIoIhMzjkvuE_MtqkPWhf-QCMmYHWStrYJHrzuQLChCtw1AbUM3Z)
21. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7nPF2n-QgTXXRAFn9gUXEwlUkJApeuqJzLSb5dLChQ0GJc17hFgpl3c82-pMKhRsvwtj9jp96rtZpZWaefV3afNp1dNU54oZU_xdGB8PlBkCrCYaqzH2if7YrVpq0uH8=)
22. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzLgrCMwWdfIn_kbuYKrA4et3NZOZMdxKfh-J1v1UwJj4VAK28AY_DLLCI7QKpc81CBB1EBPYpPzl0GNiQlp85vHkKWEJl6j_yrENwKX0v82c5Kvw6HotVLHN4yGLhyaErKHrs)
23. [kyoto-u.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5lY34JLGuYTr40dkZaD4I_2poH7XyMU1XI59kFSRZpT4GTWtiPyqy_jc8sW0LWOj1ia1tQJnLRd3uPtWqUbIE4mQjDjpfBLj-e1SM0kCC2SvIyU05RG0OpOgNANwCfWDcW-i_9F8bRw6P2QWqmWMZC3z-HnlRVPjUk6qfwa9vuQ==)
24. [antsmath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsfE9gL1uWlQMG-hX3NeuKPv-BqUVofoW9PdFXgMPvDAbPvs6_I-Rq2Ib-46rY8mApGzQUwhQq-hX64DC6iqNutJypLRVUVREnTI5ataDeXcicxwXZpFoDw5m4PqN7EOyQHZt2mbunOGl4tKKYckAnew==)

