# Non-vanishing of central L-values (Bump-Friedberg-Hoffstein, Iwaniec) 2024-2026

**Pythia queue id:** 144
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdNeThQYXVUVkpkV1dfdU1QeWJxNXNRcxIXTXk4UGF1VFZKZFdXX3VNUHlicTVzUXM
**Elapsed:** 313s
**Completed at:** 2026-05-21T16:18:53.198154+00:00

---

# The Non-Vanishing of Central L-Values: From Bump-Friedberg-Hoffstein and Iwaniec to Modern Breakthroughs (2024–2026)

**Key Points:**
*   Research suggests that the non-vanishing of central $L$-values dictates profound arithmetic properties, notably the finiteness of the Mordell-Weil and Tate-Shafarevich groups of elliptic curves, as predicted by the Birch and Swinnerton-Dyer (BSD) conjecture.
*   The foundational theorems of Bump-Friedberg-Hoffstein (1990) and Iwaniec-Sarnak (2000) established the existence of a positive proportion of non-vanishing central $L$-values in families of quadratic twists and modular forms, linking these analytic phenomena to Kolyvagin’s work and the non-existence of Landau-Siegel zeros.
*   Between 2024 and 2026, the field witnessed a revolution, with researchers achieving unconditional asymptotic formulas for the second moments of quadratically twisted $L$-functions and their derivatives, largely driven by the work of Xiannan Li and collaborators. 
*   Simultaneous non-vanishing of central $L$-values has been significantly generalized. Researchers like Balesh Kumar et al. (2025) and Subhajit Jana & Ramon Nunes (2026) have proved simultaneous non-vanishing theorems for high-level newforms and higher-rank groups ($GL(n)$) using advanced spectral reciprocity.
*   Recent advances by Peng-Jie Wong (2024) and others have successfully bounded the joint distributions of central $L'$-values, yielding conditional evidence for the Keating-Snaith conjectures and modeling the exact statistical behavior of the Tate-Shafarevich groups.

**What are Central L-Values?**
In analytic number theory, an $L$-function is a complex-valued function that encodes deep arithmetic data, such as the distribution of prime numbers or the number of solutions to polynomial equations over finite fields. These functions generally possess a functional equation relating their value at a complex number $s$ to $1-s$. The axis of symmetry for this functional equation is the line $\text{Re}(s) = 1/2$. The value of the $L$-function exactly on this line—specifically at $s = 1/2$, known as the central point—is called the central $L$-value. 

**Why Do They Matter?**
The behavior of the $L$-function at the central point is considered the holiest grail in modern number theory. For an elliptic curve, the BSD conjecture posits that the curve has infinitely many rational solutions (a strictly positive rank) if and only if its central $L$-value is exactly zero. Proving that an $L$-function does *not* vanish at this point (non-vanishing) implies that the geometric object it corresponds to has a finite number of rational points (rank zero) and a finite Tate-Shafarevich group. Consequently, analytic bounds on the non-vanishing of these values are the primary tools used to crack open Diophantine geometry.

**The Revolution of 2024–2026**
Building on classical methods such as mollification and the method of moments introduced by Selberg, Bump, Friedberg, Hoffstein, and Iwaniec, mathematicians in the 2024–2026 timeframe have integrated new paradigms. The integration of large sieve inequalities, shifted moments, algebraic geometry (sheaf theory), and spectral reciprocity trace formulas has allowed mathematicians to bypass the Generalized Riemann Hypothesis (GRH) in several critical areas. We are now able to unconditionally prove the statistical distribution of these central values and their derivatives, demonstrating that a massive proportion of these functions refuse to vanish at the critical point.

***

## 1. Introduction to Automorphic L-Functions and Central Values

The study of $L$-functions lies at the very heart of modern analytic number theory and the Langlands program. Originating from Dirichlet's $L$-functions introduced to prove the theorem on primes in arithmetic progressions, the concept has been vastly expanded to include $L$-functions attached to modular forms, elliptic curves, and automorphic representations over general reductive algebraic groups. 

Given a normalized Hecke eigenform $f$ of weight $k$ and level $N$, its Fourier expansion is given by $f(z) = \sum_{n=1}^\infty a_f(n) e^{2\pi i n z}$ [cite: 1, 2]. The associated $L$-function is constructed via the Dirichlet series $L(s, f) = \sum_{n=1}^\infty \lambda_f(n) n^{-s}$, where $\lambda_f(n)$ are the normalized Fourier coefficients. This series converges absolutely in the right half-plane $\text{Re}(s) > 1$. By the theory of Hecke and Riemann, $L(s, f)$ admits an analytic continuation to the entire complex plane and satisfies a functional equation relating $L(s, f)$ to $L(1-s, f)$ [cite: 1, 3].

The completed $L$-function is typically denoted by $\Lambda(s, f)$, defined by multiplying $L(s, f)$ by appropriate gamma factors and exponential weights. The functional equation takes the form:
\[ \Lambda(s, f) = \epsilon_f \Lambda(1-s, f) \]
where $\epsilon_f \in \{\pm 1\}$ is the root number (or sign of the functional equation). If one considers the quadratic twist of $f$ by a primitive Dirichlet character $\chi_d$ of fundamental discriminant $d$, the twisted $L$-function $L(s, f \otimes \chi_d)$ has a root number $\omega(f \otimes \chi_d) = i^k \chi_d(-N) \epsilon_f$ [cite: 2, 4]. 

The central point of the critical strip is $s = 1/2$. The study of $L(1/2, f)$ and $L(1/2, f \otimes \chi_d)$ is of paramount importance. When the root number is $+1$, the central value can be non-zero. When the root number is $-1$, the central value trivially vanishes due to the functional equation, forcing $L(1/2, f) = 0$; in this case, mathematicians turn their attention to the first derivative $L'(1/2, f)$, which may be non-zero [cite: 2, 4].

Proving that these central $L$-values and their derivatives do not vanish for a large proportion of twists or families of modular forms has been the driving force of analytic number theory for the past four decades, heavily motivated by geometric conjectures.

## 2. The Birch and Swinnerton-Dyer Conjecture and Analytic Rank

The fundamental motivation for studying the non-vanishing of central $L$-values is the Birch and Swinnerton-Dyer (BSD) conjecture. For an elliptic curve $E$ defined over the rational numbers $\mathbb{Q}$, the Mordell-Weil theorem states that the group of rational points $E(\mathbb{Q})$ is a finitely generated abelian group, isomorphic to $E(\mathbb{Q})_{\text{tors}} \oplus \mathbb{Z}^r$, where $r \ge 0$ is the algebraic rank of the curve [cite: 5, 6].

By the Modularity Theorem (Wiles, Taylor-Wiles, Breuil-Conrad-Diamond-Taylor), every elliptic curve over $\mathbb{Q}$ is associated with a weight 2 Hecke eigenform $f_E$ for the congruence subgroup $\Gamma_0(N)$, where $N$ is the conductor of the curve. Consequently, $L(s, E) = L(s, f_E)$. The BSD conjecture asserts that the algebraic rank $r$ is exactly equal to the analytic rank, which is the order of vanishing of $L(s, E)$ at the central point $s = 1/2$. Thus:
1. $L(1/2, E) \neq 0 \iff \text{rank}(E) = 0$. The curve has only finitely many rational points [cite: 1, 6].
2. $L(1/2, E) = 0$ and $L'(1/2, E) \neq 0 \iff \text{rank}(E) = 1$ [cite: 4].

Furthermore, the full BSD conjecture provides a formula for the leading Taylor coefficient of the $L$-function in terms of arithmetic invariants of the curve, notably the size of the Tate-Shafarevich group, denoted $\text{III}(E)$. 

In the late 1980s, V. A. Kolyvagin made a monumental breakthrough using the theory of Heegner points. Kolyvagin proved that if there exists a quadratic twist $\chi_d$ such that $L(1/2, E \otimes \chi_d) \neq 0$ (analytic rank 0), and if $L(s, E \otimes \chi)$ has a simple zero at $s = 1/2$ for some real Dirichlet character $\chi$, then the Mordell-Weil group $E(\mathbb{Q})$ and the Tate-Shafarevich group are finite [cite: 2, 7, 8]. This stunning reduction of the BSD conjecture to an analytic problem regarding the non-vanishing of central $L$-values set the stage for the analytic number theory community to hunt for families of non-vanishing twists.

## 3. The Foundational Non-Vanishing Theorems: Bump-Friedberg-Hoffstein

The requirement posed by Kolyvagin's theorem—that one must prove the existence of quadratic twists with non-vanishing central values or derivatives—was definitively answered in 1990 by two independent sets of researchers: Daniel Bump, Solomon Friedberg, and Jeffrey Hoffstein (often abbreviated as BFH) [cite: 1, 7], and M. Ram Murty and V. Kumar Murty [cite: 2, 9].

The Bump-Friedberg-Hoffstein theorem investigated the non-vanishing of quadratic twists of modular $L$-functions. They proved that for a weight $k$ newform $f$, there exist infinitely many fundamental discriminants $d$ such that the central value $L(1/2, f \otimes \chi_d) \neq 0$ (when the root number is $+1$), and infinitely many discriminants $d$ such that the derivative $L'(1/2, f \otimes \chi_d) \neq 0$ (when the root number is $-1$) [cite: 1, 10].

### The BFH Methodology: Multiple Dirichlet Series and Metaplectic Forms
BFH achieved this by computing an asymptotic formula for the first moment of the central values and their derivatives over fundamental discriminants. Their strategy was remarkably innovative, utilizing Eisenstein series on metaplectic groups. They constructed a multiple Dirichlet series in two complex variables, where the coefficients were essentially the $L$-values $L(1/2, f \otimes \chi_d)$ [cite: 11]. By analyzing the poles and residues of this double Dirichlet series, applying functional equations derived from the metaplectic group representation, and employing Tauberian theorems, they were able to extract the average behavior of these $L$-values [cite: 1, 7].

A crucial byproduct of the BFH theorem was confirming Goldfeld's conjecture on average [cite: 5]. Goldfeld had conjectured in 1979 that 50% of the quadratic twists of an elliptic curve should have analytic rank 0, and 50% should have analytic rank 1. BFH's non-vanishing result proved that the set of discriminants $d$ for which $L(1/2, E \otimes \chi_d) \neq 0$ constitutes a positive proportion of all discriminants [cite: 1, 5]. Subsequent refinements by Ono and Skinner improved this density to at least 1/2, aligning with Goldfeld's predictions [cite: 1, 12].

The BFH paper firmly established the "method of moments" as the gold standard for attacking non-vanishing problems. If one can evaluate the first moment $\sum_{|d| \le X} L(1/2, f \otimes \chi_d)$ and show it grows like $c X$, and evaluate the second moment $\sum_{|d| \le X} |L(1/2, f \otimes \chi_d)|^2 \ll X \log X$, then by the Cauchy-Schwarz inequality, a positive proportion of the $L$-values must be non-zero [cite: 2, 13]. 

## 4. Iwaniec's Contributions: Proportions, Mollification, and Landau-Siegel Zeros

While BFH focused on quadratic twists, Henryk Iwaniec, often in collaboration with Peter Sarnak and J.B. Conrey, extended the non-vanishing paradigm to families of newforms in the level and weight aspects, introducing profound analytical techniques that remain ubiquitous in modern research [cite: 13].

### The Iwaniec-Sarnak Theorem (2000)
In a landmark 2000 paper, Iwaniec and Sarnak studied the non-vanishing of automorphic $L$-functions at $s = 1/2$ by varying the modular form $f$ across the orthogonal family of holomorphic newforms of fixed even integral weight for $\Gamma_0(N)$ with an even functional equation [cite: 13, 14]. They proved that as the level $N \to \infty$ (over square-free integers), at least 50% of the central values $L(1/2, f)$ do not vanish [cite: 13, 14]. 

To achieve this, Iwaniec and Sarnak popularized the "mollification" technique in the context of automorphic forms, a method originally devised by Atle Selberg for the Riemann zeta function [cite: 13]. A mollifier $M(f)$ is a short Dirichlet polynomial designed to approximate $L(1/2, f)^{-1}$. By computing the first and second mollified moments:
\[ S_1 = \sum_{f} L(1/2, f) M(f) \]
\[ S_2 = \sum_{f} |L(1/2, f)|^2 |M(f)|^2 \]
they were able to strictly control the variance of the $L$-values. By carefully selecting the coefficients of $M(f)$ to maximize the ratio $|S_1|^2 / S_2$, they deduced the 50% non-vanishing lower bound [cite: 13]. 

### Connections to Landau-Siegel Zeros
One of the most spectacular aspects of the Iwaniec-Sarnak work was demonstrating that any improvement upon the 50% proportion—even establishing that $50.0001\%$ of the values are non-zero—is intimately connected to the non-existence of Landau-Siegel zeros [cite: 13]. A Landau-Siegel zero is a hypothetical, extremely pathological real zero of a Dirichlet $L$-function very close to $s = 1$. The existence of such a zero would violate the Generalized Riemann Hypothesis (GRH). Iwaniec and Sarnak showed that if one could break the 50% barrier for the non-vanishing of central values in this family, it would unconditionally rule out the existence of Landau-Siegel zeros for real primitive characters [cite: 13]. 

This linkage highlighted the "simultaneous non-vanishing" phenomenon. To attack the Landau-Siegel zero problem, Iwaniec and Sarnak considered the simultaneous non-vanishing of $L(1/2, f)$ and its quadratic twist $L(1/2, f \otimes \chi_D)$ [cite: 13]. They showed that the average of the product $L(1/2, f)L(1/2, f \otimes \chi_D)$ is proportional to the Dirichlet $L$-value $L(1, \chi_D)$. If a Landau-Siegel zero exists, $L(1, \chi_D)$ is abnormally small, which conflicts with the expected non-vanishing proportions of the automorphic $L$-values. Thus, the non-vanishing of central $L$-values serves as a bulwark against the failure of the GRH [cite: 13].

### Conrey-Iwaniec and Subconvexity
In subsequent work, Conrey and Iwaniec tackled the non-vanishing of twisted $L$-functions using cubic moments [cite: 14]. They proved a Weyl-type subconvexity bound for the quadratic twists of a newform of square-free level. The subconvexity problem aims to bound $L(1/2, f \otimes \chi_d) \ll |d|^{\alpha}$ with $\alpha < 1/2$. By developing a more general Petersson trace formula for newforms of square-free level, Conrey and Iwaniec successfully bound the cubic moment, which via standard analytic techniques yielded the subconvexity bound and, consequently, robust non-vanishing results [cite: 14, 15]. Furthermore, their work laid the groundwork for what would later be recognized as spectral reciprocity [cite: 15].

## 5. The Method of Moments: Advances in Quadratic Twists (2024–2026)

Moving into the contemporary era (2024–2026), the foundational work of BFH and Iwaniec has been expanded drastically. A major roadblock in the 2000s and 2010s was computing higher moments of $L$-functions unconditionally. Soundararajan and Young (2010) had established the asymptotic formula for the second moment of quadratic twists of modular $L$-functions, but their result was strictly conditional on the Generalized Riemann Hypothesis [cite: 9, 16].

### Xiannan Li's Unconditional Second Moments
In a staggering breakthrough published in *Inventiones Mathematicae* in late 2022 and heavily expanded upon through 2024–2026, Xiannan Li successfully removed the GRH condition, providing an unconditional asymptotic formula for the second moment of quadratic twists of a modular $L$-function [cite: 9, 16, 17]. 

Let $f$ be a newform for $\Gamma_0(q)$ and $\chi_d$ be a primitive quadratic character of conductor $|d|$. The goal is to evaluate:
\[ \sum_{|d| \le X} |L(1/2, f \otimes \chi_{8d})|^2 \]
Li's method relies on establishing a large sieve-type inequality tailored for shifted moments. By shifting the complex variable slightly off the central point (e.g., studying $L(1/2 + \alpha, f \otimes \chi) L(1/2 + \beta, f \otimes \chi)$ for small shifts $\alpha, \beta$), Li was able to decouple the arithmetic complexities. A critical input in his proof is a conversion of the problem into computing an asymptotic formula for the completed twisted modular $L$-functions with large shifts. By utilizing smooth partitions of unity and Poisson summation [cite: 2, 18], the off-diagonal terms—which previously required the strength of GRH to bound—were reigned in unconditionally [cite: 2, 4].

### Second Moment of Derivatives of Twisted L-Functions (2026)
Following Li's unconditional second moment theorem, a consortium of researchers including Li, Sumit Kumar, Prahlad Sharma, Kummari Mallesham, and Saurabh Kumar Singh published a series of preprints in 2023–2026 targeting the derivatives [cite: 2, 4].

When the root number $\omega(f \otimes \chi_d) = -1$, the central value vanishes, and the first derivative $L'(1/2, f \otimes \chi_d)$ takes precedence. In 2026, these authors proved an unconditional asymptotic formula for the second moment of the first derivative of quadratic twists of modular $L$-functions [cite: 2, 9]. The asymptotic features three leading-order main terms, significantly improving upon earlier conditional results by Petrow [cite: 4, 9]. 

The completed $L$-function $\Lambda(s, f \otimes \chi_d)$ satisfies $\Lambda(s, f \otimes \chi_d) = - \Lambda(1-s, f \otimes \chi_d)$. Taking the derivative and evaluating at $s = 1/2$ yields:
\[ L'(1/2, f \otimes \chi_{8d}) = - L(1/2, f \otimes \chi_{8d}) \left[ \log \left(\frac{8|d|\sqrt{q}}{2\pi}\right) + \frac{\Gamma'(k/2)}{\Gamma(k/2)} \right] \]
(Note: this relation holds in the context of limits approaching the central point with root number -1) [cite: 4]. The evaluation of the second moment $\sum^\flat |L'(1/2, f \otimes \chi_{8d})|^2$ involves differentiating the shifted moment formula twice with respect to the shifts $\alpha$ and $\beta$, and then taking the limit as $\alpha, \beta \to 0$ [cite: 2]. The authors carefully executed the Poisson summation over fundamental discriminants, isolated the main terms involving the symmetric square $L$-function $L(1, \text{sym}^2 f)$, and strictly bounded the off-diagonal error terms using Li's large sieve inequality [cite: 2].

These exact asymptotics for the second moments of the derivatives are critical for providing rigorous lower bounds on the non-vanishing proportions of rank 1 twists, fulfilling the modern requirements of Kolyvagin's theorem unconditionally.

## 6. Simultaneous Non-Vanishing of Central L-Values

While proving the non-vanishing of a single family of $L$-functions is difficult, proving that *multiple* distinct $L$-functions simultaneously do not vanish at the central point is exponentially harder. However, as noted in the Iwaniec-Sarnak Landau-Siegel zero work, simultaneous non-vanishing is often required for deep arithmetic applications [cite: 13].

Between 2024 and 2026, massive strides were made in simultaneous non-vanishing, expanding from GL(2) modular forms to higher-rank groups.

### Large Prime Level: Balesh Kumar, Manickam, and Shankhadhar (2025)
Published in *Forum Mathematicum* in 2025, Balesh Kumar, Murugesan Manickam, and Karam Deo Shankhadhar investigated the simultaneous non-vanishing of twisted central $L$-values for two distinct modular forms [cite: 14, 19]. Let $f$ and $g$ be two normalized holomorphic primitive cusp forms. The authors established a quantitative lower bound with respect to the level $p$ for the number of quadratic twists such that both $L(1/2, f \otimes \chi_d) \neq 0$ and $L(1/2, g \otimes \chi_d) \neq 0$ [cite: 14].

Their proof relied on producing a power-saving asymptotic formula for the averages of the twisted central $L$-values over newforms of large prime level $p$ and even weight $k$, as $k, p \to \infty$. By applying the Petersson trace formula and bounding the error terms arising from Kloosterman sums, they quantified the size of the non-vanishing set [cite: 14]. This generalized earlier work by Duke and extended Kohnen's results to higher level forms [cite: 14]. Furthermore, their work utilized the cubic moment techniques pioneered by Conrey and Iwaniec [cite: 14].

### Spectral Reciprocity and Higher Rank Groups: Subhajit Jana and Ramon Nunes (2026)
One of the most spectacular results of 2026 was published in the *American Journal of Mathematics* by Subhajit Jana and Ramon Nunes, titled "Spectral reciprocity for GL(n) and simultaneous non-vanishing of central L-values" [cite: 20, 21]. 

The concept of spectral reciprocity originates from Motohashi, who remarkably showed an identity connecting the fourth moment of the Riemann zeta function on the critical line to the cubic moment of central automorphic $L$-values on GL(2) [cite: 15, 22]. Conrey and Iwaniec implicitly used reciprocity formulas in their subconvexity proofs, and later Petrow, Young, and Blomer developed these ideas further [cite: 15]. Reciprocity formulas relate the average of a product of $L$-values in one family to an average of $L$-values in a seemingly completely different (dual) family [cite: 15, 23].

Jana and Nunes elevated this concept to the higher-rank groups GL(n). Let $F$ be a totally real number field and $n \ge 3$. Let $\Pi$ and $\pi$ be cuspidal automorphic representations for $PGL_{n+1}(F)$ and $PGL_{n-1}(F)$, respectively [cite: 21, 23]. They proved the simultaneous non-vanishing of the Rankin-Selberg $L$-values:
$L(1/2, \Pi \otimes \widetilde{\sigma}) \neq 0 \quad \text{and} \quad L(1/2, \sigma \otimes \widetilde{\pi}) \neq 0$
for certain sequences of $\sigma$ varying over cuspidal automorphic representations for $PGL_n(F)$ with conductor tending to infinity in the level aspect [cite: 21, 23].

To achieve this, they proved a massive spectral reciprocity formula for the average of the product of Rankin-Selberg $L$-functions $L(1/2, \Pi \otimes \widetilde{\sigma}) L(1/2, \sigma \otimes \widetilde{\pi})$ over a conductor aspect family of $\sigma$ [cite: 23, 24]. By equating this average to a dual period identity, they could bound the dual side using advanced analytic techniques, thus ensuring the original product does not vanish for a positive proportion of representations. This was a ground-breaking step, as even the non-vanishing of $L(1/2, \Sigma \otimes \sigma)$ when $\Sigma$ is a cuspidal automorphic representation for $GL(n+1)$ was previously unknown for $n > 2$ [cite: 23].

## 7. Trace Formulas and Hilbert Modular Forms (2024–2025)

The trace formula—in its various guises (Petersson, Kuznetsov, Arthur-Selberg, Relative)—is the engine driving these average results. In 2024 and 2025, trace formulas were extended to yield uniform non-vanishing results over totally real fields and complex fields.

### Wei, Yang, and Zhao's Relative Trace Formula
Zhining Wei, Liyang Yang, and Shifan Zhao (2024/2025) published extensive work on the uniform non-vanishing of central $L$-values of Hilbert modular forms using the Regularized Relative Trace Formula [cite: 25, 26]. Let $\mathcal{F}(\mathbf{k}, \mathfrak{q})$ be the set of normalized Hilbert newforms of weight $\mathbf{k}$ and prime level $\mathfrak{q}$ over a totally real field. They proved that as the size of the family approaches infinity, a strict positive proportion of the central values $L(1/2, \pi)$ do not vanish:
\[ \lim_{\#\mathcal{F} \to \infty} \frac{\#\{\pi \in \mathcal{F}(\mathbf{k}, \mathfrak{q}) : L(1/2, \pi) \neq 0\}}{\#\mathcal{F}(\mathbf{k}, \mathfrak{q})} > c > 0 \]
[cite: 25, 27].

The classical difficulty with Hilbert modular forms is the presence of harmonic weights in the trace formula, which skews the natural density [cite: 27]. Wei, Yang, and Zhao utilized regularized relative trace formulas to strip away the harmonic weight and obtain the natural density limit. Their result matched the strength of the best-known results in both the level and weight aspects, solidifying the non-vanishing proportions across totally real fields [cite: 25]. 

### Michel, Ramakrishnan, and Yang on U(2,1) × U(1,1)
In a related 2025 preprint, Philippe Michel, Dinakar Ramakrishnan, and Liyang Yang calculated the asymptotics of the second moment of the Bessel periods associated with holomorphic cuspidal representations $(\pi, \pi')$ of the unitary groups $U(2,1) \times U(1,1)$ [cite: 7]. Averaging over $\pi$, they obtained quantitative non-vanishing results for the Rankin-Selberg central $L$-values $L(1/2, \pi \times \pi')$. 

These $L$-functions are of degree twelve over $\mathbb{Q}$, presenting an extreme analytical challenge. Standard methods fail because they operate in a "conductor dropping" situation. The authors overcame this by explicitly evaluating the orbital integrals in the relative trace formula rather than merely comparing them via the fundamental lemma [cite: 7]. The non-vanishing of these critical degree-12 $L$-values has direct geometric implications, proving that certain associated Selmer groups have rank zero [cite: 7].

## 8. Value Distributions and Tate-Shafarevich Groups (2024)

While positive proportions of non-vanishing are analytically satisfying, number theorists also seek to understand the statistical distribution of these $L$-values. The Keating-Snaith conjectures (2000), heavily inspired by Random Matrix Theory, predict that the logarithms of central $L$-values in families of quadratic twists follow a normal (Gaussian) distribution [cite: 10, 28]. 

### Peng-Jie Wong's Generalizations
In 2024, Peng-Jie Wong published significant advancements on the distributions of $L'$-values and the orders of Tate-Shafarevich groups (denoted $\text{III}$ or Sha) in rank-one families of quadratic twists [cite: 10, 29]. Building on the revolutionary techniques of Radziwiłł and Soundararajan—who established conditional bounds for distributions of central $L$-values via the one-level density of low-lying zeros—Wong successfully extended these methods to the derivatives $L'(1/2, f \otimes \chi_d)$ [cite: 10].

Wong evaluated the conditional lower bounds for the joint distributions of central $L'$-values. He proved that under the Generalized Riemann Hypothesis, the distribution of the normalized Tate-Shafarevich group size, specifically the quantity $\log(|\text{III}(E_d)| / \sqrt{|d|})$ as $d$ varies, is approximately Gaussian [cite: 10]. Wong explicitly calculated the mean and variance: the mean scales as $(\mu(E)+1)\log\log|d|$ and the variance as $\sigma(E)^2 \log\log|d|$ [cite: 10]. 

Furthermore, as an application of these distribution models, Wong derived a simultaneous non-vanishing result for central $L'$-values in families of quadratic twists of *triples* of holomorphic modular forms [cite: 10, 29]. By analyzing the joint value distribution, he demonstrated that at least a quarter (25%) of the central $L'$-values of triples of modular forms are simultaneously non-vanishing [cite: 10]. This conditional non-vanishing result bypassed the need to calculate the extremely complex mixed moments of three degree-two $L$-functions, highlighting the immense power of value distribution theory [cite: 10].

## 9. Angular Restrictions and Sheaf-Theoretic Methods (2026)

One of the most sophisticated integrations of algebraic geometry into the analytic theory of $L$-functions occurred in early 2026 with a paper by Fouvry, Kowalski, Michel, and Sawin [cite: 18]. They studied the non-vanishing of central $L$-values over *toroidal families* with angular restrictions [cite: 18].

A toroidal family of $L$-functions is generated by twisting a base $L$-function by Dirichlet characters restricted by algebraic relations. Fouvry et al. sought to answer whether one can guarantee non-vanishing if the angle (the phase) of the character $\chi$ is restricted to be close to a specific angle $\theta$ [cite: 18]. 

Their approach combined the classical mollification technique with the general theory of trace functions over finite fields [cite: 18]. The two main ingredients were:
1. **Classification results of Katz:** Using $\ell$-adic cohomology and sheaf theory (specifically, "gallant sheaves"), they classified the geometric monodromy groups associated with the trace functions of these restricted families [cite: 18].
2. **Bilinear forms with Kloosterman sums:** Utilizing recent bounds by Fouvry, Kowalski, Michel, and Sawin on bilinear sums of trace functions, they handled the off-diagonal terms that arise in the mollified second moment [cite: 18].

By applying a smooth partition of unity and the Pólya-Vinogradov method to reduce the summation range, and relying on Poisson summation to convert trace functions to "gallant" ones, they successfully deduced the non-vanishing of a positive proportion of central $L$-values subject to these strict angular restrictions [cite: 18]. The mollifier played a crucial dual role here: not only did it control the variance, but it also tamed the contribution coming from the tail of the Fourier series used to approximate the angular interval [cite: 18].

## 10. Geometric and p-adic Perspectives

The complex analytic results of 2024–2026 also parallel deep strides in $p$-adic $L$-functions and explicit Diophantine geometry. 

### Kezuka and Li on the Gross Family of Elliptic Curves
In 2023–2025, Yukako Kezuka and Yong-Xiong Li proved non-vanishing theorems for the central values of $L$-series of quadratic twists of the Gross elliptic curve with complex multiplication by the imaginary quadratic field $\mathbb{Q}(\sqrt{-q})$ [cite: 30]. They specifically targeted primes $q \equiv 7 \pmod 8$. This work completed the classical non-vanishing theorems by Coates, which were restricted to $q \equiv 7 \pmod{16}$ [cite: 30]. By establishing the non-vanishing of these central $L$-values, they unconditionally obtained the finiteness of the Mordell-Weil group and the Tate-Shafarevich group for these curves. Additionally, they proved a converse theorem for the rank 0 case and verified the $p$-part of the BSD conjecture for higher-dimensional abelian varieties obtained by restriction of scalars [cite: 30].

### Horizontal p-adic L-Functions
Another major development was the construction of "horizontal $p$-adic $L$-functions" [cite: 11]. Traditional Iwasawa theory studies the $p$-adic variation of $L$-values in "vertical" towers of field extensions (cyclotomic towers). A 2024/2025 breakthrough defined horizontal $p$-adic measures associated with the $L$-values of twists of elliptic curves by characters of $p$-power order and conductor prime to $p$ [cite: 11]. By studying the zeroes of these horizontal measures within digit algebras, researchers obtained strong quantitative lower bounds on the number of non-vanishing central $L$-values of finite-order twists [cite: 11]. This effectively bypassed traditional multiple Dirichlet series approaches, utilizing congruences like $\chi \equiv 1 \pmod \lambda$ to track non-vanishing through $p$-adic interpolation [cite: 11]. 

Furthermore, this $p$-adic framework allowed for advances in the analytic rank $>1$ scenario, heavily utilizing Kolyvagin derivatives of $L$-values instead of strictly complex analytic variations, yielding new "Birch and Swinnerton-Dyer type" formulas for Bloch-Kato Selmer groups of central critical twists [cite: 6].

## 11. Conclusion

The landscape of the non-vanishing of central $L$-values has been entirely reshaped between 2024 and 2026. The monumental legacy left by Bump, Friedberg, Hoffstein, Iwaniec, and Sarnak—characterized by the method of moments, mollification, and multiple Dirichlet series—has been pushed to its absolute limits and combined with newly formulated tools. 

Xiannan Li’s unconditional establishment of the second moment of quadratic twists and their derivatives represents a watershed moment, freeing the field from the shackles of the Generalized Riemann Hypothesis for these specific bounding techniques. Simultaneously, Balesh Kumar, Subhajit Jana, and Ramon Nunes have extended simultaneous non-vanishing into the realm of large levels and higher-rank reductive groups via spectral reciprocity, proving that the non-vanishing phenomenon is deeply woven into the fabric of the Langlands correspondence.

With the parallel infusion of algebraic geometry (sheaf theory by Fouvry et al.), relative trace formulas (Wei, Yang, Zhao), and probabilistic value distribution modeling (Peng-Jie Wong), the analytic theory of $L$-functions is experiencing a golden age. These non-vanishing theorems are no longer just analytic curiosities; they are the exact scalpels used to dissect the geometric nature of elliptic curves, to map the structure of Tate-Shafarevich groups, and to inch ever closer to the ultimate resolution of the Birch and Swinnerton-Dyer conjecture.

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiUA8uQ3XxgRG5nWYkqnfWsrliRDOQtVLp0rhcgjpirl1kF6ztAly0rCpCXdPCUZARPitKR5DO_8doKcHgGBQy-kzD0f3b4uUNlbaIHOvUYPu_VDDKOvRWsZMOtD1io74BLT8-qcsyRcebPL5UXpqKAhDmecglJvrIg8fVNH5I6WQsv7xz63MdesvTOtSiujJUmazpHFQYIsJ1OUPW__wUMw==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDuVV05VkvJJSkzDe4dfKVpmJrMA_M_1KY0ImIzHiXM-LI_Y1wQbBQgs1dza65RmNqE_fM0HHPuiu6ciDbCNIeY3GnE7eOqh1Flcm7qrHROiuvcnsuOw==)
3. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6GCHQbe73fmBDY0dJe1DFHUrlcwB7tGjhYCy1jwuMq8h20mz4dhhPdBMNmEZcLTbSHKW42o0ISv99GkaeQQzB_Gf4huX3zJw_0IOyAbPuDy2iIwQ3HII_kxGCudGyeDdYsnZ_i8sD9Ee7kvC0WMGKPQ_E_zK5x-XiSOBR9zwLwmQG5rNu_2wO_m379J-0btmaKgXKey6D6ubHj4_8NwH5RmfEWJe8p_yJ7Tcojwn4Eh25na6GlzmIvpB_PP8QLKTvyFaIEhAivV7s2NXvFRbCaTj_g9RlJQ==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpzuBFx2phxzy6Q35o4vSFqmyx2fvvu3oMdfhDkMEsi7ZHjSD6aDzaweXxLaWcMiY8BBxSwq-tu-eXWqJsMTiL8-RLxVkq_74AIueEYGLet7ER1gSPfg==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_FSApV8I5kkp1EWQ-BDkYjIsPEZYmzS3PyvBcDYXp_xIz4ZIZbTE_aOIFJ7ebGykrHS4_QsqLkGCQDwklTmMM4L18f9-l9c3HuC40KckSAQBxePxwKA==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbOuz2rFOjab78EOgK2pjR3gjSxJiRpdVP3IFXEidGuf1ORy-uvJpsl4C3HQuBpgN-yw18ujzbDkXLUF-mZi15tY3MUE46Y9E1NNhAjoAm_A1yD7lELg==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4kUngEPxd9IxOyDy0amFT0DtKiX8VoWaG34IL6XxO4UN6AXqhxG3GUMIGHG7yvhlhRXHlLcN8o-dpcxLotaT9rP8FfrbEaHkqUXYdwRPLd9hqfRExsQ==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGlNsPHeWlDcmZVs5FVgU_o_oDKZg_6xvEXV1rgJhmwA_48EKuddFZocm0CuJcUreLy7bTKi09LUPty8GlTiX2rwOdE1WzDNWt1F65kUR7hCBiICWsFdg==)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmCyZ7wfmORjeBImy9flsj3RqBxLASczFz_UIAKCXs1fzp3pPpGhuDqdlhVncYYXiP_H4ILwxJQOHyq9DJGPqG8U5aaF5QvsDS7EO0g4BwQ9fzD0r7GEeV0CtKZwaSNAKzwn8G7iX53vNrNnEyENWBYcnE9wPEBn8gChQQ94U4H_lUNoZvRweiXIuQU-gHLcAJS-9bmZrogoZsd1G9FzPmus6pCXais5eHVyovxhldlzACLrA=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWtxt4boZq9Ie0dOQzG-SL3_PFD5LZxgqidBAOuRO8qxsQW3HQd9V-1_eYu0pddVzaFE912YlRWY7ixCVuzQVm2XTEfv7T6Njh5EkacbFpT5IoyDzbew==)
11. [unimi.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbFy_11aVsB_GDI4Vo-_yy3b6-SmwOBIvkN5AjGYZ_kB3DT7TYgtiv6ThiiGj_fq26k1-CbvKjlym6wCZehjjyPlbMvWmMnJaxIezti8OTah6187xVTswjrEaHEnC6K-CgijgchwntEpJ1XBB50VNwV1u8DCEHpShVQhL237MU12EmydlLWPXIc-leyg5hb2A7r-pC)
12. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlL9M2WYsis4bA-rnjSQvTQCT3Hu73LyZUxf46ls9OA3FOlpHm4VA0lj003tRRQq8an2XzUf3KgHh8g_pnv3FejV0fhISaswrsHgj2XSmXBjjiILMUtavyEKgPU6PIKYY2t02_8iERwdUXjrr68G-n_t23aEGsx91QzouOP7WPjlx05ha1SIsLLjuOZCFvnywkkEXuJrp1rxHmnGCRtZNseEYmKdyQ9aiBB0xRmsUfnY2ci_o35pycLQYL0f1qMr0PBt_Nh_am-j_6acw2SO1XZRe9Sn5Qyw_PhBYjzr5TKKDWM_NF9rQHI8GvYpe45KHexrnIfpwd)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3-3L8exGrJcpvYxXnV6Kro8Bu38fF7zbN4KtzHzL8m0eTc-FBZ3OOQfAo9NY0nRmIsmeX9Dtpm3tKJhVmfWuEy3H8bgBoe5ymUX8RaLfkEOzgzJVmQs6eTEipOWl0r14prEq7PKVIA_KI0Loc8Q27clcTnttbPKov5j0_UHr1NGZoJMBQB8h8wGs5fv9xpxQ5opmLLRLOgbTeX_g9qoIj5gRvTSke-odW-ItQzus_KEnfnKJirljB5JyTApJNgXU=)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrkyL_SeA4YU8qg8_C-Sgmkr6QZRgR2Q80zvLq8AC6SWSQgF7zlOhGReozxeDJCKRc9R63EoRmWLlOJ-lbgs7tJlD9SMMojRHXn8Ru7qjm0oZnYzg5Ivp_hT_7fg9t7M2cXOJE95nML3-1BK3G7NlihbR4KQh5J_nEWz3VJ4TBKEbzP3xdTv6y2sEHOI6v4JktsEydeOMnYC2XQlcghI1lWsZzVzzVJ0E=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZU9y9GB3sAvTxgJ37aJzInTQESCPDz08zLU_ZhZBYYtacByARwMi3XoZAr0uJjgger8qbIxPaVdgeF7rSd6of_24HIDCzFfqlQm4s54Ji6fESICabPrYCXw==)
16. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcOsOd8KAALn0GYMr3L6YecuHspnubrBHXuzm9MoymW5D0mSlfV_e1DYqmEAdFfXzIfqU6np1-ijHzwOhIMP-oILq0mu_f_JX1IAAihYQ-1R1R3fxXvrTQ5YKPGckzFfF39TLAPTeGaIvLyryHtAtUCuyCI8ywbGja7JeEwGXEYJ9NnzJusmhr94ujOiJZxaEkzwAjRrFonqD9D3e9nD6rKRgLqVE4MZLTF5IoVAo=)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFm4bKDa6ECFpW5ix8AFYmDWK3IPuLT0vYXikIziNN4wnCU6mFp58-NHrLIvLav_3-JKeTDHJYhtJ_-PvM3NjkwfcXrnKk9Dv4xE9fk1uZV7FUpZIjHneuhxAZ_RvGljzneqb33kxD7ffEZ3NWW_-ZISwmslCEeGwdplZVJCFFMIBQ2x-rvztRXUCvEVffkAuDUFqjpfB26jcS7)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEowdHQgWhtwbuyKm8i8PJIwg44s4kQKeeiVytTBpO5Io1embOmhJ-FW0qdbh0cmNdbcJEYr8aRVEreaTS8Y3OMU-7CD51Q-MDm9nBeqaAd04eQDvWQ5w==)
19. [iitrpr.ac.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENTxKSHMvHisM1a4LWp8c5LlTqIeHc7YHPDe80jMpeRRhF5m54WzUtMluUNwZfb6OIXo_PjxqwQiFNwcg7iVruZCIUeR-AmSa1UHFNL5uhxigPWoaa5kJCnaOlxxvwymDmVA==)
20. [qmul.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3ZDfyhqzIkMlX2WjjnkTiN2rwDK23e-3jFfcu-Sibsejgk1Rb3VLHcrn2CXa8zNu387rGyKdjI9DmuWF9wavxia1Aq4tCvjH7A_X0BLe2x3aBasRpwyQnOZNCiVqjvyO_jbLaZ60=)
21. [jhu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExoTrUBvzqrZ14bsDBnki-b1bNdUv8NyYdJOZUiZ4ly5AtguqsqkHuT9_TANG4E90JB1WTewltBwqRZ5zejGem0Xu_ivL4yk6n51ZVoFUOqFtYpKEC4py7oDwTgDA74nHj)
22. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpqbomJWptnM0A-KqfC48FsNZF9iH1o-31uZlbq-HRb0ukur06nFXSKINoNj-usiw_dM3Wa8d68IVidjMDozOIJcPg_ueztDEMWu58V65lVzgbyBK8m18mQ13EsCrWj0w12AGzXJAr)
23. [jhu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIpvI5PebFp1wv0OhVbJb7IQDQDHpXKp6PcHSyoB0Y3pfOAXXurZlcn0dEXOm1Y3wrVq4jdVZPWepalEaGJZyyYzEOQFhrICW_knKBh2XW_DZLLZ9UR5t72MBFKqCczBszvasedC_aOlAbiHSX-YeiSZeor3iq6Q-L9Z9vz-vA)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFenN2x2wP7m29_FzFWMr-y8NE5AKwA4S7k5fR265xEwUJcgNJSDjnfsqMiMMhDGeFHSM5sB9M1qjLK8HPG8aw2dsLZpus-1fD0h6vy8O4g4FgNMv8uUA==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJTKTNL4Z_DNnzeDbkNSc63tTNAIUBa-fKS31hGbQXACBKTYhJsFzsHLk24XZ_sGyyXAtwAUAZtFDO9fb-Fslv-cyCxSiVvs80fDsKPPYXfklk5hgHqw==)
26. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgB1p8LCH4f6OOomsE00VZoT08BMeyfklAoAEamakXYjeWHPxC6AMbA89tDvkJgvE10AZIc33HoC0KN0dHVOlOVhiGNs41jWydLxYZ9PrP8_pkUOGxk0M_-rMBL_Owt-Ip4RqljelIsKHKIKmWj9hSp3oWpw==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERfbZ4PQ5p7IzNNuR4IkAKZ8Ykbm0bmUtMyuWvwieiQueOoj70FL7VSEo6jAs8KtXWgnx6eNfPFXgm2iEtsJTwZ33lVJulZbmHAJSeXdNVBmGYUbvtqA==)
28. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhvQQ3t0mJiaEjW0270pnhgLb3RVvLncfI4fYb9NlkjDbzIaYTX9puvrxL6czKMy38DdShcESrh-OmTRTN3-K4vD48NxHDcmijZ2VjlWDOvW9XdEyFhIbTrF92GRozA95cWGLgGgHy-W-LmXNWZrykAr43btZSV1ZX3dAd3tVnWlA7fb5fMCY=)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdB0MrXsIj4-SiHhPXq2WpEUX8-awX5F8TQLrB4A-3pEI2IViSbM5hfy1b79aE8n31Wes4rqRAtKl2d2g1luuFilNc1MKuUGQ818mIcZjgjSreRfrUCw==)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcPPRfm3-0yVWyOu2euqHrllASpet6Gy5kJzcm8m9GFRTZL1sqBtr1avyOh-CrlmXOjVEbfBZW7ytFMGbLnvBqwla_a8eiiBmnI1cmW94d4RQnnrIcEQ==)

