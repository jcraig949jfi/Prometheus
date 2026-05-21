# Sha (Tate-Shafarevich group) order computations + p-Sha 2024-2026

**Pythia queue id:** 159
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChduelFQYXNxOUt1ek8tOFlQOE5ldmlBURIXbnpRUGFzcTlLdXpPLThZUDhOZXZpQVE
**Elapsed:** 315s
**Completed at:** 2026-05-21T16:42:03.955469+00:00

---

# Recent Advancements in Tate-Shafarevich Group Computations: Order, $p$-Primary Components, and the Birch and Swinnerton-Dyer Conjecture (2024-2026)

**Key Points:**
*   **The Tate-Shafarevich Group ($\Sha$):** A central object in arithmetic geometry, the Tate-Shafarevich group measures the failure of the local-global (Hasse) principle for principal homogeneous spaces over abelian varieties.
*   **Strong BSD Verification (2024-2025):** Recent breakthroughs by T. Keller and M. Stoll have achieved the first unconditional, exact verification of the strong Birch and Swinnerton-Dyer (BSD) conjecture for absolutely simple abelian varieties of dimension greater than one, specifically modular abelian surfaces over $\mathbb{Q}$. 
*   **Order of $\Sha$ Modulo Squares:** While the order of $\Sha$ for elliptic curves is a perfect square, A. Konstantinou (2024) proved that for general abelian varieties, every square-free natural number can appear as the non-square-free part of the order of $\Sha$, proving a conjecture by W. Stein.
*   **Arbitrarily Large $p$-Torsion:** E. V. Flynn, A. Shnidman, and T. Fisher (2024-2025) demonstrated that for *any* prime $p$, there exist absolutely simple abelian varieties over $\mathbb{Q}$ with arbitrarily large $p$-torsion in their Tate-Shafarevich groups, overcoming previous limitations that restricted such proofs to small primes.
*   **Methodological Innovations:** The period of 2024–2026 has seen immense algorithmic progress in computing $p$-primary components ($p$-Sha) using isogeny descents, explicit Heegner index computations via Kolyvagin-Logachev Euler systems, and $p$-adic $L$-functions.

The study of rational points on algebraic curves and abelian varieties is one of the oldest and most profound subjects in mathematics. The Birch and Swinnerton-Dyer (BSD) conjecture, a Clay Millennium Prize problem, elegantly connects the analytic properties of an abelian variety's $L$-function to its global arithmetic invariants. Among these invariants, the Tate-Shafarevich group (denoted by the Cyrillic letter $\Sha$, or "Sha") is the most mysterious, as there is still no general proof that it is universally finite. However, the years 2024 through 2026 have marked a watershed era for arithmetic geometry, featuring unprecedented computational and theoretical successes regarding the order of $\Sha$ and its $p$-primary components (often referred to as $p$-Sha). This report provides an exhaustive, highly detailed synthesis of the most recent academic literature on Tate-Shafarevich group order computations, the exact verification of the BSD conjecture for abelian surfaces, the structure of $\Sha$ modulo squares, and the existence of arbitrarily large $p$-torsion elements. 

***

## 1. Introduction to the Tate-Shafarevich Group

To understand the computational milestones of 2024-2026, it is imperative to rigorously define the Tate-Shafarevich group and its role in Diophantine geometry. Let $K$ be a global field (such as a number field like $\mathbb{Q}$) and let $A$ be an abelian variety defined over $K$. The absolute Galois group of $K$ is denoted $G_K = \text{Gal}(\bar{K}/K)$. 

### 1.1 The Local-Global Principle and the Weil-Châtelet Group
The study of rational points $A(K)$ often begins with the local-global principle (the Hasse principle). If a polynomial equation has a solution over $K$, it must inherently have solutions over all completions of $K$ (the real/complex numbers and all $p$-adic fields $K_v$). For quadratic forms, the Hasse-Minkowski theorem guarantees that local solubility implies global solubility. However, for curves of genus $g \geq 1$ and abelian varieties, this principle famously fails. Carl-Erik Lind and Ernst S. Selmer provided classical counterexamples; for instance, Selmer showed that the genus 1 curve $3x^3 + 4y^3 + 5z^3 = 0$ has solutions everywhere locally (over $\mathbb{R}$ and all $\mathbb{Q}_p$) but no non-trivial global solutions over $\mathbb{Q}$ [cite: 1, 2].

These counterexamples are captured cohomologically. The Weil-Châtelet group of $A/K$, denoted $WC(A/K)$, is defined as the first Galois cohomology group $H^1(G_K, A)$. The elements of $WC(A/K)$ correspond to equivalence classes of principal homogeneous spaces (torsors) for $A$ over $K$ [cite: 1, 3]. 

### 1.2 Definition of $\Sha(A/K)$
The Tate-Shafarevich group is the subgroup of the Weil-Châtelet group consisting of torsors that are everywhere locally trivial. That is, it measures the exact extent to which the Hasse principle fails for torsors over $A$. Formally, it is defined as the kernel of the restriction maps from global to local Galois cohomology:
\[ \Sha(A/K) = \ker \left( H^1(G_K, A) \longrightarrow \prod_{v \in M_K} H^1(G_{K_v}, A) \right) \]
where $M_K$ is the set of all places of $K$, and $K_v$ denotes the completion of $K$ at the place $v$ [cite: 3, 4, 5]. Non-zero elements of $\Sha(A/K)$ correspond to curves that possess rational points over every completion $K_v$ but lack a rational point over the global field $K$ [cite: 6].

$\Sha(A/K)$ is known to be a torsion abelian group. The overarching Tate-Shafarevich conjecture asserts that $\Sha(A/K)$ is finite for any abelian variety over a number field [cite: 1, 4, 6]. While Karl Rubin proved finiteness for certain elliptic curves with complex multiplication, and Victor Kolyvagin extended this to modular elliptic curves of analytic rank at most 1 [cite: 1], the conjecture remains completely open in the general case. Therefore, in any computation of the "order of $\Sha$," one mathematically focuses on the $p$-primary components $\Sha(A/K)[p^\infty]$ for various primes $p$.

### 1.3 $p$-Primary Components and Selmer Groups
For any integer $n \geq 1$, the exact sequence of Galois modules $0 \to A[n] \to A \xrightarrow{n} A \to 0$ induces a long exact sequence in cohomology. The $n$-Selmer group, $\text{Sel}_n(A/K)$, is defined to collect the local solubility conditions:
\[ 0 \longrightarrow A(K)/nA(K) \longrightarrow \text{Sel}_n(A/K) \longrightarrow \Sha(A/K)[n] \longrightarrow 0 \]
The Selmer group is effectively computable (being finite) and bounds the algebraic rank of the Mordell-Weil group $A(K)$, while also containing the $n$-torsion of the Tate-Shafarevich group [cite: 2, 7]. The $p$-primary part of the Tate-Shafarevich group is $\Sha(A/K)[p^\infty] = \{x \in \Sha(A/K) \mid \exists m \ge 0, p^m x = 0\}$ [cite: 3]. Computations of the $p$-part of $\Sha$ ("p-Sha") involve intense techniques from Iwasawa theory, Euler systems, and $p$-adic $L$-functions [cite: 7, 8].

***

## 2. The Birch and Swinnerton-Dyer (BSD) Conjecture

To fully contextualize the computations of 2024-2026, one must look to the Birch and Swinnerton-Dyer (BSD) conjecture, which formulates a precise, conjectural value for the order of the Tate-Shafarevich group. 

### 2.1 The Weak and Strong BSD Conjectures
Let $L(A/K, s)$ be the Hasse-Weil $L$-function of an abelian variety $A/K$, defined by an Euler product over the primes of good and bad reduction. The analytic rank of $A$, denoted $r_{an}$, is defined as the order of vanishing of $L(A/K, s)$ at $s=1$.
The **Weak BSD Conjecture** states that the algebraic rank $r$ of the Mordell-Weil group $A(K)$ equals the analytic rank $r_{an}$ [cite: 9].

The **Strong BSD Conjecture** provides a leading-term formula that encapsulates the arithmetic volume of the abelian variety. Assuming the Taylor expansion of the $L$-function at $s=1$ is $L(A/K, s) = c(s-1)^r + \mathcal{O}((s-1)^{r+1})$, the strong BSD conjecture states that $\Sha(A/K)$ is finite, and its exact order is given by the relation:
\[ \frac{L^{(r)}(A/K, 1)}{r!} = \frac{|\Sha(A/K)| \cdot \text{Reg}(A/K) \cdot \prod_{v} c_v}{|A(K)_{tor}| \cdot |A^\vee(K)_{tor}|} \Omega_A \]
where:
*   $|\Sha(A/K)|$ is the order of the Tate-Shafarevich group.
*   $\text{Reg}(A/K)$ is the regulator of $A/K$ (the determinant of the Néron-Tate height pairing matrix).
*   $c_v = [A(K_v) : A_0(K_v)]$ are the local Tamagawa numbers at primes of bad reduction.
*   $A(K)_{tor}$ and $A^\vee(K)_{tor}$ are the rational torsion subgroups of $A$ and its dual $A^\vee$.
*   $\Omega_A$ is the real period of $A$ [cite: 8, 9, 10].

Because all invariants in this formula except $|\Sha(A/K)|$ can usually be computed—at least numerically to high precision—the formula can be inverted to define the **analytic order of Sha**, denoted $|\Sha(A/K)|_{an}$ [cite: 9, 10, 11]. The conjecture then posits that the true, algebraic order of $\Sha$ equals the analytic order [cite: 10].

***

## 3. Unconditional Exact Verification of Strong BSD for Abelian Surfaces (2024-2025)

Prior to 2024, the strong BSD conjecture had been unconditionally verified for many "small" elliptic curves (abelian varieties of dimension 1) over $\mathbb{Q}$ with analytic rank 0 or 1 [cite: 10, 11, 12]. However, a complete, exact verification of the strong BSD formula for an absolutely simple abelian variety of dimension $g \geq 2$ had never been accomplished, because the methods could not easily be reduced to a product of elliptic curves [cite: 9, 11, 12].

A monumental achievement in 2024 and 2025 was the publication "Complete verification of strong BSD for many modular abelian surfaces over $\mathbb{Q}$" by Timo Keller and Michael Stoll [cite: 11, 12, 13, 14]. This research represents the first time the strong BSD conjecture has been confirmed unconditionally and exactly for absolutely simple abelian varieties of dimension at least 2 [cite: 11, 12, 13, 15]. 

### 3.1 The Dataset: Modular Abelian Surfaces
Keller and Stoll focused on modular abelian surfaces over $\mathbb{Q}$, which are the Jacobian varieties of genus 2 curves that have real multiplication by a real quadratic order and correspond to classical modular forms [cite: 9, 16]. Their algorithms verified strong BSD for:
1.  All 28 Atkin-Lehner quotients of the modular curves $X_0(N)$ that have genus 2 [cite: 12, 13, 17].
2.  All 97 genus 2 curves contained in the L-functions and Modular Forms Database (LMFDB) whose Jacobians are absolutely simple and of $\text{GL}_2$-type over $\mathbb{Q}$ [cite: 10, 12, 13].
3.  Six additional specific genus 2 curves originally discovered by Wang [cite: 11, 12, 13].

For the majority of these surfaces, the computed analytic order of $\Sha$ was exactly 1, meaning the Tate-Shafarevich group is trivial [cite: 17, 18]. To definitively verify strong BSD, Keller and Stoll had to show computationally that the actual group $\Sha(J/\mathbb{Q})$ is indeed trivial for all primes $p$ [cite: 18]. 

### 3.2 Computation of $p$-Primary Components
The computational hurdle lies in bounding and computing the $p$-primary components, $\Sha(A/\mathbb{Q})[p^\infty]$. The researchers systematically dismantled this infinite problem into finite, computable parts:

1.  **The 2-Part:** The 2-primary component, $\Sha(A/\mathbb{Q})[2^\infty]$, was determined using 2-descents on hyperelliptic Jacobians. Utilizing tools implemented in the Magma computer algebra system, they demonstrated that in most of their target curves, $\Sha(A/\mathbb{Q})[cite: 19]$ is trivial, which immediately implies that the entire 2-primary part $\Sha(A/\mathbb{Q})[2^\infty]$ vanishes [cite: 20, 21].

2.  **The Odd $p$-Parts via Kolyvagin-Logachev:** For primes $p$ where the residual Galois representation $\bar{\rho}_p: \text{Gal}(\bar{\mathbb{Q}}/\mathbb{Q}) \to \text{Aut}(A[p])$ is irreducible, they employed an explicit version of the Euler system of Heegner points established by Kolyvagin and Logachev [cite: 9, 10]. The Kolyvagin-Logachev result bounds the order of the Selmer group and the Tate-Shafarevich group in terms of the Heegner index [cite: 10, 22]. Keller and Stoll designed a highly explicit algorithm to exclude a finite set of "bad" primes: those dividing the Tamagawa product, the primes over 2 and 3, those dividing the GCD of certain Heegner indices, and primes where the Galois representation is reducible [cite: 9]. For primes $p \nmid 2 I_K c(J/K)$ with irreducible $\rho_p$, the Kolyvagin-Logachev argument shows that $\Sha(J/\mathbb{Q})[p] = 0$ [cite: 10]. 

3.  **Isogeny Descents:** For primes where the Galois representation is reducible, Euler system arguments can struggle. Instead, Keller and Stoll utilized explicit isogeny descents. If an abelian surface admits a rational isogeny of degree $p$, they bounded the $\mathbb{F}_p$-dimensions of the two corresponding Selmer groups [cite: 9, 21]. Through careful diagram chasing and cohomology computations, they showed $\Sha(J/\mathbb{Q})[p] = 0$ for these problematic torsion primes without needing $p$-adic $L$-functions [cite: 9].

4.  **Iwasawa Theory and $p$-adic $L$-functions:** For primes $p$ where the analytic rank is 0, they leveraged the $\text{GL}_2$ Iwasawa Main Conjecture [cite: 21]. By computing $p$-adic $L$-functions using overconvergent modular symbols, they obtained the exact $p$-valuation of the $p$-Selmer group, effectively bounding $\Sha(J/\mathbb{Q})[p^\infty]$ [cite: 9, 10, 15].

### 3.3 The $|\Sha| = 7^2$ Milestone
A shining example in the 2024-2025 literature is the curve provided by Sam Frengley, an absolutely simple Jacobian of a genus 2 curve of level 3200 with rank 0 [cite: 9]. The analytic order of $\Sha$ for this curve, calculated using modular symbols, predicted an order of 49. In a joint appendix, Keller, Stoll, and Frengley explicitly computed the 7-descent for this surface and unconditionally verified that the order of the Tate-Shafarevich group is exactly $7^2 = 49$, in flawless agreement with the BSD conjecture prediction [cite: 11, 12, 13, 14, 15, 20]. 
Frengley's separate 2025 work, "Explicit 7-torsion in the Tate–Shafarevich groups of genus 2 Jacobians," describes a robust algorithm that outputs twists of the Klein quartic curve parametrizing elliptic curves whose mod 7 Galois representations are isomorphic to a sub-representation of the mod 7 Galois representation of the genus 2 Jacobian [cite: 16]. By applying this algorithm to families of Bending and Elkies-Kumar curves, Frengley unconditionally exhibited elements of order 7 in $\Sha(J/\mathbb{Q})$ that are visible in an abelian three-fold [cite: 16].

***

## 4. The Order of the Tate-Shafarevich Group Modulo Squares

Parallel to the exact verification of BSD, 2024 yielded a definitive answer regarding the possible group orders of $\Sha(A/K)$. Historically, a prominent piece of arithmetic folklore maintained that the order of the Tate-Shafarevich group, if finite, must inherently be a perfect square. This misconception was traced to an early misquotation of John Tate's work by Swinnerton-Dyer [cite: 1]. 

### 4.1 The Cassels-Tate Pairing
The structure of $\Sha(A/K)$ is deeply constrained by the Cassels-Tate pairing, a non-degenerate, bilinear pairing:
\[ \langle \cdot, \cdot \rangle : \Sha(A/K) \times \Sha(A^\vee/K) \longrightarrow \mathbb{Q}/\mathbb{Z} \]
where $A^\vee$ is the dual abelian variety. If an abelian variety admits a principal polarization coming from a $K$-rational divisor—as is trivially true for all elliptic curves—Cassels established that this pairing is strictly *alternating* ($\langle x, x \rangle = 0$) [cite: 1, 6, 23]. The theory of finite alternating bilinear forms dictates that any group admitting such a non-degenerate alternating pairing must have an order that is a perfect square [cite: 6, 23]. Thus, for elliptic curves, $|\Sha(E/K)| = m^2$ for some integer $m$.

However, for higher-dimensional principally polarized abelian varieties, Flach (1996) proved that the pairing is merely *skew-symmetric* ($\langle x, y \rangle = -\langle y, x \rangle$) but not necessarily alternating [cite: 6, 23, 24]. Consequently, the order of a principally polarized abelian variety can only be guaranteed to be a square or twice a square ($m^2$ or $2m^2$) [cite: 6, 23]. Subsequently, Poonen and Stoll provided the first explicit example of an abelian variety whose Tate-Shafarevich group order was exactly twice a square (specifically, 2) [cite: 1, 6, 23]. Furthermore, William A. Stein discovered examples of abelian varieties (without principal polarizations) defined over $\mathbb{Q}$ whose $\Sha$ orders were neither squares nor twice squares [cite: 1, 6, 23]. Stein conjectured that the square-free part of the order of $\Sha$ could be arbitrarily wild.

### 4.2 Konstantinou's 2024 Proof
In an April 2024 preprint and a subsequent 2025 publication in the *Proceedings of the Royal Society A*, Alexandros Konstantinou conclusively settled this question in "A note on the order of the Tate-Shafarevich group modulo squares" [cite: 1, 6, 24, 25]. 

Konstantinou proved that for *every* square-free natural number $n$, there exists an abelian variety $A$ defined over $\mathbb{Q}$ with a finite Tate-Shafarevich group of order $n \cdot m^2$ for some integer $m \geq 1$ [cite: 6, 24]. 

To achieve this, Konstantinou avoided searching for random abelian varieties and instead utilized the geometric operation of **Weil restriction of scalars** [cite: 6, 26, 27]. Given a cyclic extension of number fields $F/K$ of odd prime degree $p$, he considered the restriction of scalars $B = \text{Res}_{F/K} A$, where $A$ is a principally polarized abelian variety [cite: 6, 27]. By breaking down this Weil restriction up to isogeny and applying the Cassels-Tate formula (which tracks how the Birch-Swinnerton-Dyer invariants change under isogenies), he expressed the order of $\Sha(B/K)$ modulo squares purely in terms of the Birch-Swinnerton-Dyer constants [cite: 6, 24, 27].

Konstantinou's proof systematically reduced the theorem to showing that for a specific isogeny map, the subgroup $\ker(N_{H} \mid \Sha(B_n/K_n))$ is finite, and tracked the powers of primes arising in the local Tamagawa numbers and real periods [cite: 6]. The result acts as a definitive validation of Stein's conjecture, demonstrating that the structural parity of $\Sha$ is unboundedly flexible when one abandons the requirement of an alternating principal polarization [cite: 24, 25].

***

## 5. Arbitrarily Large $p$-Torsion in Tate-Shafarevich Groups (2024-2025)

Beyond the exact order of the group, a major computational and theoretical target is understanding the growth of $p$-primary components. The group $\Sha(A/K)$ is an abelian torsion group, so it decomposes into a direct sum of $p$-primary parts. A long-standing question in arithmetic geometry asked whether the $p$-torsion subgroup, $\Sha(A/K)[p]$, can be arbitrarily large for abelian varieties over $\mathbb{Q}$.

Historically, proving that $p$-torsion can be arbitrarily large over $\mathbb{Q}$ was restricted to a handful of small primes. For elliptic curves, arbitrarily large $p$-torsion was known only for $p=2$ (McGuinness), $p=3$ (Cassels), $p=5$ (Fisher), and $p=7, 13$ (Matsuno) [cite: 28, 29]. For higher primes, such as $p \geq 11$ (excluding 13), no analogous results were known for elliptic curves [cite: 29]. In higher dimensions, Creutz and others showed that $p$-torsion could be large over *extensions* of $\mathbb{Q}$, but doing so universally over the base field $\mathbb{Q}$ for *any* prime $p$ remained elusive [cite: 28, 30, 31].

### 5.1 The Flynn-Shnidman-Fisher Breakthrough
In an essential advancement published in the *Journal of the Institute of Mathematics of Jussieu* (2024/2025), E. Victor Flynn, Ari Shnidman, and Tom Fisher unequivocally resolved this question in their paper "Arbitrarily large $p$-torsion in Tate-Shafarevich groups" [cite: 30, 31, 32]. 

They proved the following sweeping theorem: **For every prime $p$ and every integer $k \geq 1$, there exists an absolutely simple abelian variety $A$ over $\mathbb{Q}$ with $\dim_{\mathbb{F}_p} \Sha(A/\mathbb{Q})[p] \geq k$** [cite: 30, 31]. This means the $p$-torsion of the Tate-Shafarevich group can be arbitrarily large for *any* prime $p$. As a corollary, they showed that if one selects the dimension of the abelian variety to be $g = p-1$ (for $p \ge 7$), then the $p$-torsion in the Tate-Shafarevich groups of absolutely simple abelian varieties of dimension $g$ can be arbitrarily large [cite: 33].

### 5.2 Explicit Construction of $\mu_p$-Covers
The methodology employed by Flynn, Shnidman, and Fisher bypasses the traditional reliance on $L$-functions or bounding Mordell-Weil ranks. Instead, they directly constructed locally soluble torsors that globally fail the Hasse principle.

Their construction utilizes explicit $\mu_p$-covers of Jacobians. They start with a specific family of superelliptic curves of genus $p-1$ defined by the equation:
\[ C: y^p = x(x-1)(x-a) \]
or, in a parametrized form, $y^p = x(x - 3u_k)(x - 9v_k)$ [cite: 30, 31, 32, 33]. Let $J$ be the Jacobian of $C$. The variety $J$ is birational to the symmetric power $C^g / S_g$. The researchers identified $\mu_p$-covers of these Jacobians that exhibit a high degree of local solubility [cite: 33]. 

To show that $\Sha(A)[p]$ is large, they provided a method to find explicit equations for order $p$ torsors that violate the Hasse principle. However, as noted in their paper, while their theoretical construction is rigorous, the actual algebraic equations for these torsors become immensely complex. For instance, comparing to earlier work by Radičević, even for $p=11$, the equations for such torsors are incredibly difficult for a human to write down, and as $p$ grows, the polynomial computations rapidly become intractable even for the most advanced computer algebra systems [cite: 28, 33]. Thus, their proof combines invariant theory, a geometric construction due to Pantazis, and Chebotarev density arguments to guarantee the existence of these primes and torsors without relying on brute-force computation of the polynomials themselves [cite: 33, 34].

Tom Fisher's appendix in this paper explains how to interpret the proof in terms of the Cassels-Tate pairing, utilizing descent methods to explicitly trace the non-triviality of these torsors within the $p$-Selmer group [cite: 30, 31, 33].

***

## 6. Advanced Methodologies for $p$-Sha Computations (2024-2026)

Alongside these sweeping existence theorems and BSD verifications, the literature of 2024-2026 delves deeply into refined methods for investigating the $p$-part of the Tate-Shafarevich group across various contexts.

### 6.1 Anticyclotomic Iwasawa Theory and Heegner Cycles
In the realm of modular forms, a 2025 paper by Matteo Longo and Stefano Vigni (as referenced in arXiv:2307.13134) refines the anticyclotomic Iwasawa theory for modular forms [cite: 35]. Let $f$ be a cuspidal newform of weight $k > 2$. They provided a new algebraic definition for the $p$-part of the Shafarevich-Tate groups, denoted $\Sha_{p^\infty}(f/K)$ and $\Sha_{p^\infty}(f/K_\infty)$, over an imaginary quadratic field $K$ satisfying the Heegner hypothesis, and over its anticyclotomic $\mathbb{Z}_p$-extension $K_\infty$ [cite: 35].

Their central theorem states that if the basic generalized Heegner cycle $z_{f,K}$ is non-torsion and not divisible by $p$, then the $p$-primary Tate-Shafarevich groups $\Sha_{p^\infty}(f/K)$ and $\Sha_{p^\infty}(f/K_\infty)$ are rigorously trivial (equal to 0) [cite: 35]. This is proven by analyzing the $p$-adic Galois representation $W_p$ attached to $f$ by Deligne, performing Tate twists $V = W_p(k/2)$, and studying the self-dual lattice inside $V$ via $p$-adic Abel-Jacobi maps [cite: 35].

### 6.2 Bipartite Kolyvagin Systems
A major theoretical tool used in 2024 for proving the modularity of Tate-Shafarevich classes is the "Bertolini-Darmon bipartite Kolyvagin system." According to a 2024 paper (arXiv:2402.07317), under suitable assumptions, $p$-torsion Tate-Shafarevich classes for elliptic curves over $\mathbb{Q}$ are "visible" in quotients of Jacobians of modular curves, exactly as predicted by the Jetchev-Stein conjecture [cite: 8]. 

The key ingredient is demonstrating the non-triviality of the Bertolini-Darmon bipartite Kolyvagin system $Z_{BD}$, which implies that suitable cohomology classes form a basis for the Selmer group modulo $p$ [cite: 8]. The existence of a non-trivial bipartite system for $E[p]$ is mathematically equivalent to the $p$-parity conjecture for $E/K$. The researchers employed the Iwasawa Main Conjecture—specifically the divisibility results by Skinner and Urban—and multiplicity-one theorems for Shimura curves to deduce that every class in $\Sha(E/\mathbb{Q})[p]$ is modular when $E$ has good ordinary reduction at $p > 3$ [cite: 8].

### 6.3 $p$-Part of $\Sha$ for $y^2 = x^3 + px$
Specific families of elliptic curves provide fertile testing grounds for $p$-Sha computations. Research highlighted in 2024 (arXiv:2411.12316) focused on the 2-part of the Tate-Shafarevich group for the curve family $E: y^2 = x^3 + px$, where $p \equiv 1 \pmod 4$ is a prime number [cite: 3]. Through explicit 2-descent calculations, researchers determined how quadratic extensions and prime twists affect the size of the 2-part of $\Sha$. For instance, they demonstrated that under the assumption that $\Sha$ is finite, there exists a prime $D$ such that $\Sha(E_D/\mathbb{Q})[cite: 19] = 0$. Conversely, for the curve $y^2 = x^3 + 257x$, they proved that $\Sha(E/\mathbb{Q}(\sqrt{-D}))[cite: 19]$ cannot be rendered trivial for *any* $D$ [cite: 3].

### 6.4 Parity of Ranks and Local Root Numbers
In a highly relevant sequence of papers leading into 2025 (including "Parity of ranks of Jacobians of curves" by V. Dokchitser, H. Green, A. Konstantinou, and A. Morgan), researchers linked the Shafarevich-Tate conjecture to rank parities [cite: 26, 36, 37]. 

They investigated Selmer groups of Jacobians of curves admitting non-trivial automorphisms. Assuming the finiteness of $\Sha$ (the Shafarevich-Tate conjecture), they proved that the parity of the Mordell-Weil rank of an arbitrary Jacobian can be expressed entirely via *purely local invariants* [cite: 26, 36, 37]. These local invariants act as an arithmetic analogue of local root numbers, which under the BSD conjecture govern the parity of the algebraic rank [cite: 36]. This framework yielded a brand-new proof of the parity conjecture for elliptic curves, avoiding standard global constraints and relying on Brauer relations and the decomposition of $L$-functions of Galois covers [cite: 26, 36, 37].

***

## 7. Synthesis of Algorithmic Approaches and Software

The era of 2024-2026 is defined not merely by theoretical existence proofs, but by the physical execution of massive algorithms computing $\Sha$ data. 

*   **Magma and 2-Descents:** For calculating the 2-primary component of $\Sha$, computer algebra systems like Magma utilize classic 2-descent algorithms. These involve computing the rank of the Selmer group by analyzing homogeneous spaces and testing for local solubility at all completions [cite: 21]. For the hyperelliptic curves utilized by Keller and Stoll, the triviality of $\Sha[cite: 19]$ was algorithmically confirmed for almost all curves in their genus 2 database [cite: 21].
*   **Isogeny Descents:** When $p$-torsion primes exist, computing $\Sha[p]$ transitions to isogeny descent. If $J$ has an isogeny $\phi$, one computes the Selmer groups $\text{Sel}_\phi$ and $\text{Sel}_{\hat{\phi}}$. The computation relies heavily on tracing Galois cohomology sequences and determining the local Selmer ratios (Tamagawa factors) $c_v(\phi)$ [cite: 21, 38].
*   **Modular Symbols and L-functions:** To compute the analytic order of $\Sha$, researchers must calculate the leading Taylor coefficient $L^{(r)}(A, 1)$. This relies heavily on the use of overconvergent modular symbols and algorithms developed by Darmon and Pollack for $p$-adic $L$-functions [cite: 10, 20]. The analytic values are strictly exact rational numbers (often returning results like exactly 1 or exactly 49) rather than floating-point approximations, achieving strict verification [cite: 10].
*   **The LMFDB:** The $L$-functions and Modular Forms Database remains the central hub for storing pre-computed data regarding $\Sha(E/\mathbb{Q})_{an}$. Almost all modern arithmetic algorithms pull initial data regarding conductor $N$, Tamagawa factors $c_p$, and real periods $\Omega$ from this repository to cross-reference their exact $\Sha$ descent verifications [cite: 39, 40].

## 8. Conclusion

The computational landscape surrounding the Tate-Shafarevich group and the Birch and Swinnerton-Dyer conjecture has experienced a dramatic expansion during the 2024-2026 period. The monumental achievement by Keller and Stoll, verifying the strong BSD conjecture completely and unconditionally for absolutely simple abelian surfaces, bridges a decades-long gap between dimension 1 and higher dimensions. Their successful identification and verification of an abelian surface with an exact $|\Sha|$ of $7^2=49$ serves as a crowning computational triumph.

Simultaneously, the foundational structure of the group itself has been deeply clarified. Konstantinou's 2024 proof that $\Sha$ can harbor any square-free component dismantles classical assumptions tied to principal polarizations. The collaborative work of Flynn, Shnidman, and Fisher establishing that $p$-torsion in $\Sha$ can be arbitrarily large for *all* primes $p$ closes one of the most stubborn open questions in Galois cohomology and Diophantine arithmetic. Supported by profound advancements in Euler systems, $p$-adic $L$-functions, and isogeny descents, the "p-Sha" literature of 2024-2026 showcases arithmetic geometry operating at the peak of its computational and theoretical power.

**Sources:**
1. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHI3rDB0V5J3UUF_2owmwfqNgO1C8dxx07zi21OGelinYIbifq_FnMWZLwVLTXTtd35w1-FT_fHO-wm_t9XeedZbJrQcM2eI74CO0LY7t8Mxhyq48dvgJAtOqQst_QWwqsFLkXSdeaC8khtfaExMGB7ZNE=)
2. [timo-keller.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPMgCbEv8h1p3VectpjRexHyDSKqBSDkx4HnBvEEjneK-GipzBsqXBNccTaLcNapyeZG6IEkyQC_HuqSQ34WYcHitbyKt2Nz2i20YtTWCHPJpdYyeLakhrL7PvfKIDuRCdGw==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEC1uwPICSJdwZEJlIM0J5xlhVXGrFbCqSTfzCSb3vfuHcSxwJV0TKRjs_NQelOlKdoxO0nZCp6kvDM13tcGQJlz6A_Snt9M-dtXe3sT2zcbNGMFn-qWQ==)
4. [sagemath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbcVGrKQk-VPZvNVkAGp-X5RDR0_jeDixPXh_YE3UN0SYuL5oJEsW8dQjMxQnUOnozdi1P3KmMZ2fg2uT_R59Jo5VPufG9NTYuHv9o2tQ3ut4BusjWVNyNCZR3mqVDQledS4OzfxJtiFossUN1yFO2dt8d7RhhBKfsYUZ20SS2dkHaWQdxhSM1nBKHaNRMeKtOHoGQviGJugl3RhXV)
5. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzHrrWI536_EaL8JroZM-mlN0lqOn9ECPC84O3GrKy0dNrqnvZJxiUdPcnDIJtXV_JgHLcKXAoZ5ETAS8ZA9kaKL-j9kRwtAicAoPOSfqJ6r5QaCEEyV230miw8X_7wKNl0eJ05faY_c4uWQjE5CUNz8IUbAhvZK0PISP3yIbpd1VnhYMiUrRJCj-SZficcw==)
6. [royalsocietypublishing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbtwHhJUA87xvhdJJONZcLnWR2e_dZxRpyQ0KFMpdMLJYYNZVSL6c_F7_6v5gx1lcKTGN1QsiQw_hd7Rby4GuE90Ca4Tcv7dh-2IePScdJr7Hgg_LfRhZAt_ciblkytlBIOzDcnE5r8OV_qP_PiQUZsAkDf1LkRRSiJ8ZpUQbEjXmYGH9aQhmr-4FMW4u7aosEEXZpiWRJMWHaGbsWzPCykyQdZ8eBaBjYyIHYk5cOgg==)
7. [utrgv.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkj8tinEds_1RBz7qKAOvO0wyQ4zsfF7lq30btAUmT6eLYCqptlWhQzcqV7AL0uqvQD0hwdSG5yfhPckfCfr8xB8U4eqvn8dlCw6ndzuGb3BPYaFM6bGFfwMIKoU1gvJSAoZT-1XZXeAs_JpfZd-FAuRbSOuNmLligEkc461Z17kwd13Z3)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYw58wcgzMjtMi86totjBVqejP7IwMXBydwi7Cz0pzh16aUFfyhcqmz29cUjy3aUTT0NB6E8OlhLsJy0TZNv7u1JWPgzZ_OtXrhMdbEEw3hSLiy8p0Aw==)
9. [timo-keller.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmgQpTdxtZhb8jwKuPE0wCru1WbMb0XTuoBQi1ItCHV-jxnE1ZXojOFFKQNPslVmvzNFcHdBAXu_as_JIKIL-A9py4z0kkqm7TnZySQT4Q3LytHN6tAeav2FyW)
10. [timo-keller.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbR7fhwIvpVzi5H1Z01s6DMM1WjCAH-tZt96XFPSTE1rdkZX_x_1ZlIXC-JnCy2e8NAYRrkFlKdN0ewJQB0-JUNyHg5s37ICMxOga04j1_6TtKaQPJCALzzvuyvRcxnAswBM0SGU_XGuQVQ6ttuMyBGsw=)
11. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKo_JXZKGkZ8HhE7QBwPSwr2mYbmkCwTGCH6kdluHGN1sYz3w_jxz-hHs7hjDRYbUzBmENwolJteKE18VMSebKQWuCf-_OaxToS-MwTg9KkHFiJKSrpZIYNseLqaySLhcn2o7ro1r4YRtgWmPrNhpfDS5RV9V_fngKkD_OYy9WjjvgQy69Kqix-bALLaIr8yPlZzVj54iaa0oBdOKeGzhGjtflXqtjDN0efea2wbEHUmF6nGJMXfvLzzNh6-odemo5tJALZBAazcun0d_5AV87GcdBmffM8i6P8oChaou9BH6VqpjtQ7vO14oBxnGxZkPJpHW6BYo=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3y2gEbleQGOIBdylfIeOQxTPSkjNL3NdttmUYXpv0Gb2pU6xIh4ervWhzt1SAsyghLoxEFmafDXa31m-rsFWcESnMrwPImWSgFNTofzVu9bIhRZoh_lTEVw==)
13. [timo-keller.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjfpq_ueYw6ruChnlmyvM6dyF7YcjREQhy6Oq9hc1LgFZWbkLgT08avfAKRVWrLYASMEF8-GsGKM-uUuBW_W4AtfmABfuJKg0xcIt67NVd76pvwAHGJNOEwGgYe0vfdi_miw==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWUMxZao8b1JP604BNBZApgkFt6cHVhmUsRAfx-V1hX68bqrZgub-V5SjE7ZBpnZ3LKDU_gUSbJm8WUOjKEFn6HfOvg6SZKB06Qy0WUXgiz38KzST1AQ==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGm5yQoKVpc-sgk13dDOjnzD8V5E-kkF0V5bvJcIx_VjSt5lQ6MEDROtVtF4qe6IdZ-em15evu7IkkH4mI6bJ9mQlCetM_EZYxbmR5PUaBhEDujZU-ivQ==)
16. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPo-QzsZ9qc6mO4Dc3e1s2iNQWecr1e9IPxgVeUgGpT_DIYq24LfxselEdPkGhgSUJQ9IJNSbJ1hTGvVzUX6_pV4RgcpHFoCGNRO5oF0L0pblVKjNoO15BuhI6M840Xu0krIRjgYRL_7zK0w10yr2Ifu0=)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3S_GgPOlVj-A_uvTzv4dg2oVMF-ok8_TJXSKhWjY5BfqB55g2ZcGcQJ5ShWE6STxICTjGuNrzVpVB9mcrC8QQDdK_hgPh2-yUx-pzv7_BGz2JsqAd7w==)
18. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIitsKUD28xhqqChvqpnRXFe2PHsysi9xgftDtBu2QdeP2jHaUetKF4qPrxPc89X3GcayNFhySGkoAykifY0yrDnqHNSwwIUNY82shi9mh1TFZHTfLHCdPv-x9gOY4)
19. [fub.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrDAepkIkWKfgiFBZAoD0WZBhc-V_V8JJjE50CrkSEbj7i3I-f4FcS46887qjrf7XO8YF2xJHP8Xr-ptmyJEh-6kJmJ_Q2gdLCclV0LzqjWfYq8MLVD8a2Yd_SkpjsWz2iO6IKDlXbWDFxaE5VQyEpvLAqrN5AmBk4InwZp-mwvgqn3FdX17BBoZVIqVk=)
20. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhlkogc_RDA8NWsOYGynVRXqVGV8dwkhZnZFnEf6cH7UFnqOo5dDcIFVx0xE6Q5P7h3pHcXl6vWnkEP1X6YJ-htA_IsjKHzlNhLjEad4jqrBUgw7fMDsa-02zAFIVzSFuycbCn0515IepVaYcjehwnvPizyRaIFF3tozovmccvDG_4EzQpQVhpa9wO4uW66maN8HDG0aLhGWfI9le4Hvw2XPjtKNQtrn09L0McfmamfM8bR-2MIrMKIVeY4kFmmVJW_vKnaz68qMxmSVj9t869Xi9lK8ikHNfOT0F9NBITXtGwDzDqyz3acqgNWZsuJXtzHyFJPA_JslH-miGrq_hn_rTRYjVJgCjCTF-_DZzqK93Z2GLbUkmqLYc=)
21. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYX1xSlwofGDFi_XL4LbK-TxPNEZ4iuf3XZoM3ucGpHWEtYHaFG_DoAxQWzkwD_FwRQVd5NuIGh_1GDxoaipEWvjWhKQL5Dr689rngK4zUeR8r7tzIBzNHcsOoXTeB_2IToA90iyHpNg==)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGl8E8AOzg_B3IvdbihFUF7RqU0Z5UC0zEWqLpI2sx4qfRSwPGbispVY6LAb6ZfSPBcbn32rUD5S0eESt29jsEKwjmH5_F1nDu8RnUWhv98qYtRTmOw70xTzUOTKSZUcZ4b32N6M6cC5l8KaN5psP2HO1frV45rzvg8qbqzIdGXimqfywHh5c_UHLVITGBewWP_ERowdxlgTH0kX43y7oAd)
23. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZMzXltS5uU1Tu0zy45UfeuBNp1StAPJG9K7ShpAz-GHdulyguluFXyY4-wSnSlicCcfB_p8gKbJByYu_W5uz3NgsRhvdqzREcMfrX1n4irZDcIH4CF6w5sTlvJaVyVl-6jDyNHE1NXn_7wffolve61nIUjobtp-9jOiYkcOcDCU8=)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkn7V3k1siMF415481HQg3NFkxQOlTHqJHQiPa3k4hHmXGrCC0dYEq1hWQBOVt2qeX1UwN8HAguu6nGZGD-b453JOuYwKXcSRLFkRKa1GUVyIS70zrOme1Bw==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHV_6qEseperrm74RpUVFVVA1TC6CNCKw8smwTIMRnD218x8s6Ax1tbbzMXLLWIHyySbt_80Ti8HX00j3qs-_bawpjV47I5si0umNBdGnieeQAC_lukkA==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEa9ebNsBfESs9eXVgEQHrskoqTQMOaZ_QW64uL34_UvJH7iwQdFcDz4qoDQQV5Ow5ybZnCFLMbpsIbxwPT1IupVL0xqYtIvZIJi6JgIpKYZySqUr4UFw==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7U90geJtP5ya77IPoh7V2l5lCfDqjMUSd3FZsXc2YOpDcUQs6ErcC8QE5TclXTZCUsyxbD-8_Qq69nVXj4--RslEry1svsRWMpEe37UGxipc3jBED_g==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfZdFYiOrDa8gmeg1wPCqug0Hoj7giQUNFpNpJutU7iuwDqEu3s79b8OipZGqyxWZqP7D_xVyf72_GCh7DgTKewYt646zTlhrJCCO0ObbVGy0vjI2hrA==)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAXnYAffFBqitRLq93Q4iFIe0HkugyWpC9im-7lnA-UKDveJWld3id9YKklFpWewA5ldB7sD_Wt95RT49mCB7Sk1N8_5F1fHW60goSBhxUrZfH5iwAwQ==)
30. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQ9L-DM5YbWTqVIU424D7F2kiB8tPRt3x_tnJdHKVOXLKlztrDRF-UVBsYAjScYyze_C7dKGz-vJ1vR60TopxuhvbDHMZiE2gTLO2GQOQn1rBJdd-e13dh_uedvXSHfyR4WceY8uA5F-XlBGqyZndAdc_mgxgiGBOsOeSvxaxRFgp4zJ7P-StPvn7e-18eiHbMf73R9e5ETfNlvS536GR_eLyvqKu5RaeRJFKorF7dk89r9dfhDSElDFLqfzmBj5XrMmuTowzxsFvSNUTMy1GD_0LR8FRgAa5FLURZk8RiIBKv_8Dr5Zn860gVgZeFIA==)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEzGqUkO5enhYZeQNlcohQcYIL2FwpBoVFm2ItGEpY7romZAmmSz_iUP5RZ2Kzi_PHB_OKqS8EVSFE-tqnlijkAjw592FA0QtHxQlQXE1Q6W0xjuC-sd3DhA==)
32. [huji.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGowYM1iClhBZH9wdYpFhrVyfbVnSbCI1-Fqt_tQobjCYqyQa5I5Jq-3zcXsyF5X9Dw3tm3TmbjDHMBytddRmV3aMY2AHYESDgR44C3FGxyMDNa-Fso_G_NeE1ZevLCkZSc6NYdhxRg-o0BcBhlOpT0Z2IrfIr3OMiKlk5fND4OirBYbYz-3wQ-jCO8uQAslcOEVBYJ8Q==)
33. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGt-5Nrp6O58oLAZWSmOxuE64yrOtNA46yvkMgCTN8sGFo4zvo0U_ZxjJTzA9Wfprj-fu35f9m2-jFwRmhs00DSMiRDh6f3moidgKdwAkKubb0Sr8PdQrqjnXoHBPn08U3uK69bOYmobw==)
34. [cam.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-uS3FGXlKq7mCBacy-iob0w7lcjUqtkFHITXRdDHImKRbC9iEKvHfMZmz3NKOtNVi7JKpJfDIXKVEPz_xLC7Gw1Wb2L0wgMQfgDJngVA8JIbS6_-vrbaeo6Kx4kLwEd1Y3HUnU7N4FEJjKT2AaW88vm30kAwE4kqcBMzIwS1iGag=)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAu58l7hykBd63XpNVn3M1ItKKx8ct08a05G2jWkXf3FhxNDdZLte-WxstF7wMsBVJ2nViQEL4JvKmd46wv1Z_55WlQxty6HspcnQgcOMULuXMN-Aq8w==)
36. [bris.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfwrK7UxlxcJuYaqIlZiTRVcX5MB7gpW2Uz8V3uKBp_30bMtvgNrW57ujyK9hZVaeWOeFOYNyMT7dIiuWeuXpSjp03vNIj4UvdMDB0Jd3wpz6t7uy3ovAuSwdupnGDvagff6lN6ykP7ESTC9PiWTmNHTbCgHonoSM003_wAI9K1ca8AjRHJbu3C9YTNeSv2K9Useqnrw==)
37. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyNimwjVg-5PVSLpsETf0pGP_K9cyr2Fu5PhboQXkVta6DVfU3Q9cZslyJFDbsFiouaziYQB8PTSXUTIE83xoAydSin7fx7WinYB6UQSTCSZWoDT5UcduW5V8KKd3s0G3q2coh2NYv7qQQylbwnjxpe8DCY39-uYxcu8MWhiuV51hJntVsMPMFwrSoB_Co5w==)
38. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRjAZ3BmjNIp1Pq4rR6CdLsOzOUD_7WDJSUzJOGXTSfHNWMq-_XzQnTOieErsDEtsd6hvdrsbVmqBxV9sWkWh0aPE-VViLA90NgfTM8lO3oP_mqs_DQjTT3hy1OBhTLlrgnqUYPGhrpXfF_1re56EF1NhKAkbk8SdQUsxULXzlv6sr2Wlbnp0qMeqUKpaZNt4kX4uEJasR03TYFEee-qMqHtPDinbX7JcVPvIXG63pyH_8avhh0eLlPev3uy_Q1kTQbix2UxGNCAV3Z3SvDYF3VgvRboLEgd9Nqv7Nu8vnKAmVtC4VwjoTjedq1MDQ-CuB2_7ZXQyu)
39. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZe0MZp4UNsXwO-0MGwY5S-KkBNL6SfH0N5eHqA3KzWjTlTtuRnkWW-gS09Hugwak-tnLBjAPpWPj_yUUzHoNkrE6OTmYcO7NGeAyFBD3h1lJc7_B9Rw==)
40. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEl0aq58LOUGVN55ypgyxg-GuMAAmCtBZl8S7UrMwuL95__hVdnSnlRUjMMGeR1S6qm-_j-Dlw5LisDI8OXdw6SypFawO3CfFidJ1MuFC1EZXMGpCQaRw==)

