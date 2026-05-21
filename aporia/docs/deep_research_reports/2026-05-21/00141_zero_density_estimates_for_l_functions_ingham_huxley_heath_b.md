# Zero-density estimates for L-functions (Ingham, Huxley, Heath-Brown) 2024-2026

**Pythia queue id:** 141
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdPUzRQYXR2SEdmVzZfdU1QN3ZyRDBBOBIXT1M0UGF0dkhHZlc2X3VNUDd2ckQwQTg
**Elapsed:** 245s
**Completed at:** 2026-05-21T16:13:35.860789+00:00

---

# Zero-Density Estimates for \(L\)-functions: Modern Developments (2024-2026) on the Foundations of Ingham, Huxley, and Heath-Brown

**Key Points**
*   **The Density Hypothesis remains a central pursuit:** While the Generalized Riemann Hypothesis (GRH) is the ultimate goal, zero-density estimates provide an unconditionally accessible path to bound the number of "rogue" zeros of \(L\)-functions off the critical line, with immense implications for the distribution of prime numbers.
*   **A historic barrier was broken in 2024:** The monumental work of Guth and Maynard shattered the 50-year-old Huxley barrier for the Riemann zeta function, establishing a new zero-density exponent of \(30/13 \approx 2.307\), significantly improving our understanding of primes in short intervals.
*   **Classical bounds have been made strictly explicit:** Between 2024 and 2026, foundational theorems by Ingham, Carlson, and Selberg were given explicit, computable bounds with optimized logarithmic factors, driven by breakthroughs from researchers like Chourasiya, Simonič, and Bellotti.
*   **Generalization to broader \(L\)-functions is accelerating:** The Density Hypothesis has seen its range of validity widened for holomorphic cusp forms (improving to \(\sigma \ge 1407/1601\)), Dedekind zeta functions, and higher-degree \(\mathrm{GL}(2)\) and \(\mathrm{GL}(3)\) \(L\)-functions, utilizing advanced mixed-moment and dichotomy methods pioneered by Heath-Brown and Bourgain.

**Layman Summary**
In analytic number theory, \(L\)-functions are complex mathematical tools used to decode the hidden patterns of prime numbers. The most famous of these is the Riemann zeta function. The Riemann Hypothesis suggests that all the "important" zeros of these functions lie perfectly on a single vertical line in the complex plane (the "critical line"). Because mathematicians have not yet proven this, they use "zero-density estimates" as a backup plan. These estimates count the maximum possible number of zeros that could "leak" away from the critical line. 

For decades, the mathematical bounds limiting these rogue zeros were stuck at a limit set by Martin Huxley in 1972, building on the earlier work of Albert Ingham and Roger Heath-Brown. However, starting in 2024, a wave of new discoveries fundamentally changed this landscape. New mathematical techniques have sharply reduced the estimated number of these rogue zeros, not just for the Riemann zeta function, but for a vast menagerie of advanced \(L\)-functions. This means we can now prove that prime numbers appear with predictable regularity in much smaller intervals than ever before. This report explores these modern breakthroughs, bridging the classical foundations of the 20th century with the cutting-edge discoveries of 2024–2026.

***

## 1. Introduction to Zero-Density Estimates

The distribution of prime numbers and their generalizations in arithmetic progressions, number fields, and automorphic representations is intrinsically governed by the analytic properties of \(L\)-functions. Let \( L(s, \pi) \) be an \(L\)-function associated with some arithmetic object \(\pi\) (such as a Dirichlet character, a Dedekind field extension, or a Hecke-Maass cusp form), where \( s = \sigma + i t \) is a complex variable. 

The Generalized Riemann Hypothesis (GRH) asserts that all non-trivial zeros \( \rho = \beta + i\gamma \) of \( L(s, \pi) \) satisfy \( \beta = 1/2 \). However, in the absence of a proof of GRH, analytic number theorists rely on statistical approximations known as **zero-density estimates**. We define the counting function \( N(\sigma, T, \pi) \) as the number of zeros \( \rho = \beta + i\gamma \) of \( L(s, \pi) \) such that \( \beta \ge \sigma \) and \( |\gamma| \le T \) [cite: 1, 2].

A standard zero-density estimate takes the form:
\[ N(\sigma, T, \pi) \ll_\varepsilon T^{A(\sigma)(1-\sigma) + \varepsilon} \]
for \( 1/2 \le \sigma \le 1 \), where \( A(\sigma) \) is a function (or a constant \(A\)) to be optimized [cite: 3]. The trivial bound, deriving from the Riemann-von Mangoldt formula, gives \( N(1/2, T) \ll T \log T \). The **Density Hypothesis** conjectures that \( A(\sigma) \le 2 \) for all \( \sigma \in [1/2, 1] \), implying \( N(\sigma, T) \ll T^{2(1-\sigma) + \varepsilon} \). The Density Hypothesis is a corollary of the Lindelöf Hypothesis (and thus of GRH) and is widely believed to be true [cite: 4].

For applications to the distribution of primes—most notably the Prime Number Theorem (PNT) in short intervals—the critical metric is the supremum of \( A(\sigma) \) over the interval \( [1/2, 1] \). If \( N(\sigma, T) \ll T^{A(1-\sigma)} \log^B T \), it directly implies that there is always a prime in the short interval \( [x - x^\theta, x] \) for any \( \theta > 1 - 1/A \) [cite: 5, 6].

Between 2024 and 2026, the landscape of zero-density estimates has undergone a renaissance. This report details the synthesis of classical methodologies—chiefly the large value theorems and mixed-moment estimates of Ingham, Huxley, and Heath-Brown—with modern harmonic analysis and dichotomy arguments, leading to groundbreaking new bounds for the Riemann zeta function, Dirichlet \(L\)-functions, automorphic \(L\)-functions, and beyond [cite: 7].

## 2. The Classical Foundations: Ingham, Huxley, and Heath-Brown

To contextualize the breakthroughs of 2024-2026, it is imperative to outline the historical pillars upon which modern zero-density theory rests.

### 2.1. Ingham's Density Estimate
In 1940, A.E. Ingham provided a profound zero-density estimate for the Riemann zeta function \( \zeta(s) \), leveraging the mean value theorem for Dirichlet polynomials [cite: 8, 9]. Ingham proved that:
\[ N(\sigma, T) \ll T^{\frac{3(1-\sigma)}{2-\sigma}} \log^5 T \]
This bound is particularly powerful near the critical line. For \( \sigma = 1/2 \), the exponent becomes \( \frac{3(1/2)}{3/2} = 1 \), which matches the trivial order \( O(T \log T) \). As \( \sigma \) increases, Ingham's bound provides the strongest known estimates up to \( \sigma \approx 0.7 \) [cite: 9]. Ingham's theorem fundamentally connected zero-density bounds and zero-free regions to the asymptotic distribution of primes in short intervals [cite: 5, 10].

### 2.2. Huxley's Bound and the $12/5$ Barrier
In 1972, Martin Huxley introduced a subdivision argument built upon the Halász-Montgomery large values estimate. Huxley proved that for \( \sigma \ge 3/4 \), the exponent could be bounded by \( A \le 12/5 = 2.4 \) [cite: 4, 11]. Thus:
\[ N(\sigma, T) \ll_\varepsilon T^{\frac{12}{5}(1-\sigma) + \varepsilon} \]
For over 50 years, this remained the world record for the uniform density exponent \( A(\sigma) \). Because the prime number theorem in short intervals \( [x - x^\theta, x] \) depends on \( \theta > 1 - 1/A \), Huxley's bound established the unconditionally proven existence of primes in intervals of length \( x^{7/12 + \varepsilon} \) (since \( 1 - 5/12 = 7/12 \approx 0.583 \)) [cite: 6, 12]. 

### 2.3. Heath-Brown's Moments and Double Zeta Sums
D.R. Heath-Brown advanced the field exponentially through his estimates on the moments of \(L\)-functions and the distribution of their zeros. Notably, Heath-Brown established the 12th power moment of the Riemann zeta function, which yields the zero-density bound \( N(\sigma, T) \ll T^{3(1-\sigma)/(3\sigma - 1)} \). 

Furthermore, Heath-Brown provided foundational weighted zero-density estimates used in sieve contexts, working in conjunction with Iwaniec [cite: 5, 10]. For Dedekind zeta functions \( \zeta_K(s) \) of a number field \( K \) of degree \( n \), Heath-Brown proved in 1977 that the density near the 1-line scales as \( B_K(\eta) \le n \) [cite: 13]. Heath-Brown's intricate bounds for double zeta sums also remain a vital ingredient in contemporary dichotomy approaches for automorphic forms [cite: 1, 14].

## 3. The Guth-Maynard Revolution (2024)

In 2024, Larry Guth and James Maynard published a historic paper that finally broke the Huxley barrier of \( 12/5 \), representing the first major uniform improvement to the global zero-density exponent \( A \) in over half a century [cite: 6, 11].

### 3.1. Large Values of Dirichlet Polynomials
Zero-density estimates are inherently linked to the frequency with which a Dirichlet polynomial \( D(t) = \sum_{n=N}^{2N} b_n n^{it} \) (with \( |b_n| \le 1 \)) takes large values [cite: 15]. The traditional Halász-Montgomery-Huxley machinery bounds the number of well-spaced points \( t_r \in [-T, T] \) where \( |D(t_r)| \ge V \). 

Guth and Maynard identified that the critical bottleneck for Huxley's \( 12/5 \) bound occurs at \( \sigma \approx 3/4 \). At this point, the "worst-case" scenario involves Dirichlet polynomials of length \( N = T^{4/5} \) taking values of size \( V = N^{3/4} \) [cite: 11]. Huxley's classical large value estimate bounded the number of such extreme points \( R \) by \( R \le T^{3/5 + o(1)} \) [cite: 11, 16]. 

Guth and Maynard introduced an entirely new harmonic analysis approach, bounding the large values through multi-scale incidence geometry and decoupling. They established the new large values estimate:
\[ R \le T^{o(1)} \Bigl( N^2 V^{-2} + N^{18/5} V^{-4} + T N^{12/5} V^{-4} \Bigr) \]
Applying this to the critical parameters \( N = T^{4/5} \) and \( V = N^{3/4} \), their theorem yields \( R \le T^{13/25 + o(1)} \), a profound improvement over \( T^{3/5 + o(1)} = T^{15/25 + o(1)} \) [cite: 11, 16].

### 3.2. The New Zero-Density Exponent: $30/13$
Incorporating this newly forged large value estimate into the zero-detection machinery, Guth and Maynard derived the new record zero-density estimate for the Riemann zeta function:
\[ N(\sigma, T) \ll T^{\frac{30}{13}(1-\sigma) + o(1)} \]
The new exponent \( A = 30/13 \approx 2.307 \) substantially improves upon Huxley's \( 12/5 = 2.4 \) [cite: 4, 11]. Consequently, the supremum of the density exponent over the critical strip shifted, allowing the researchers to bypass the previous obstacles.

### 3.3. Implications for Primes in Short Intervals
By plugging the new zero-density exponent into the explicit formula for the Chebyshev function \( \psi(x) = \sum_{n \le x} \Lambda(n) \), the error term in the Prime Number Theorem can be tightly controlled. The bound \( \psi(x+h) - \psi(x) \sim h \) is now unconditionally valid for \( h > x^{1 - 1/A + \varepsilon} \) [cite: 4, 6].
Using \( A = 30/13 \), Guth and Maynard established that the Prime Number Theorem holds in short intervals of length \( h = x^{17/30 + \varepsilon} \) [cite: 4, 15]. Since \( 17/30 \approx 0.566 \), this thoroughly supersedes the classical \( 7/12 \approx 0.583 \) benchmark [cite: 4, 12].

## 4. Explicit Formulations and Computational Implementations (2024-2025)

While asymptotic bounds like \( \ll T^{A(1-\sigma)} \) are of immense theoretical interest, computational number theory, cryptography, and explicit verifications of prime distribution require bounds with completely specified constants. The 2024–2025 period saw an explosion of papers rendering classical density estimates explicitly computable.

### 4.1. The Explicit Ingham Zero-Density Estimate
In 2025, Shashi Chourasiya and Aleksander Simonič achieved a fully explicit form of Ingham's zero-density estimate [cite: 8, 9]. The authors provided precise numerical constants \( C \) and a refined logarithmic exponent. 
Ingham's original 1940 paper proved \( N(\sigma, T) \ll T^{3(1-\sigma)/(2-\sigma)} \log^5 T \). Chourasiya and Simonič optimized the logarithmic factor to yield an explicit bound of the form:
\[ N(\sigma, T) \le C \cdot T^{\frac{3(1-\sigma)}{2-\sigma}} \log^{\frac{7-5\sigma}{2-\sigma}} T \]
for \( 1/2 < \sigma \le 0.7 \) [cite: 8, 9]. This is currently the most powerful explicit zero-density estimate for values of \( \sigma \) close to the critical line. The proof relied heavily on explicit bounds for the fourth power moment of the Riemann zeta function. Following Ramachandra's proof structure, Chourasiya and Simonič established an explicit estimate with an asymptotically correct main term for the fourth power moment \( \int_0^T |\zeta(1/2 + it)|^4 dt \) [cite: 8, 9]. They utilized Gabriel's convexity theorem to elegantly bound the relevant cross-terms [cite: 9, 17].

### 4.2. Bellotti's Explicit Log-Free Bounds Near the 1-Line
For values of \( \sigma \) very close to 1, Chiara Bellotti (2024) formulated the sharpest known explicit log-free zero-density estimate for the Riemann zeta function [cite: 18, 19]. For applications in bounding the difference between consecutive primes and analyzing the Vinogradov-Korobov zero-free region, eliminating the logarithmic penalty is highly advantageous. 
Bellotti proved that for \( \sigma \in [\alpha_0, 1] \), where \( 0.985 \le \alpha_0 \le 0.9927 \), and for \( 3 \cdot 10^{12} < T \le \exp(6.7 \cdot 10^{12}) \):
\[ N(\sigma, T) \le C T^{B(1-\sigma)} \]
For example, for a uniform upper bound covering \( \sigma \in [0.9927, 1] \), Bellotti establishes \( B = 1.448 \) and \( C = 1.62 \cdot 10^{11} \) [cite: 19]. This log-free bound provides immediate utility to algorithmic searches for large prime gaps and explicit Chebotarev density computations. Work is currently underway to translate Bellotti’s framework from \( \zeta(s) \) to arbitrary Dirichlet \(L\)-functions [cite: 20].

### 4.3. An Explicit Carlson Bound
Complementing Ingham's estimate, another classical bound by Carlson was made fully explicit in December 2024 [cite: 2]. Carlson's density theorem typically states \( N(\sigma, T) \ll T^{4\sigma(1-\sigma)} \log^{O(1)} T \). The explicit 2024 result established:
\[ N(\sigma, T) \le 0.78 \cdot T^{4\sigma(1-\sigma)} (\log T)^{5-2\sigma} \]
for \( T \ge 3 \cdot 10^{12} \). The proof requires obtaining an explicit second moment of the mollified zeta function and applying Littlewood's classical lemma to count the zeros [cite: 2].

## 5. The Density Hypothesis for Automorphic and Higher-Degree \(L\)-functions

The standard zero-detection method partitions the zeros into two classes using a mollifier \( M_X(s) = \sum_{n \le X} \mu_f(n) n^{-s} \) [cite: 4]. Using the approximate identity \( L(s,f)M_X(s) \approx 1 \), a zero \( \rho = \beta + i\gamma \) implies that either the associated Dirichlet polynomial is anomalously large (Class I zeros) or the error integral involving the critical line values of \( L(s,f) \) is large (Class II zeros) [cite: 4, 21]. The Density Hypothesis is proven for a range \( \sigma \ge \alpha \) if we can guarantee \( N_f(\sigma, T) \ll T^{2(1-\sigma)+\varepsilon} \).

### 5.1. Holomorphic Cusp Forms: The Work of Chen, Debruyne, and Vindas
A monumental step forward in establishing the Density Hypothesis for automorphic \(L\)-functions was achieved by Bin Chen, Gregory Debruyne, and Jasson Vindas in 2024 [cite: 1, 14]. They studied \(L\)-functions \( L(s, f) \) associated with normalized Hecke eigenforms \( f \) of even integral weight for the full modular group \( \mathrm{SL}_2(\mathbb{Z}) \).

In 1989, Ivic established that the Density Hypothesis for such forms holds in the range \( \sigma \ge 53/60 \approx 0.8833 \) [cite: 1, 22]. Chen, Debruyne, and Vindas successfully widened this range of validity, proving that:
\[ N_f(\sigma, T) \ll_\varepsilon T^{2(1-\sigma)+\varepsilon} \quad \text{holds for } \sigma \ge \frac{1407}{1601} \approx 0.8788 \]
To achieve this, the authors engineered an intricate synthesis of multiple classical methods [cite: 14, 22]:
1.  **Halász-Montgomery Inequality:** To handle the Class I zeros [cite: 22].
2.  **Ivic's Mixed Moment Bounds:** Leveraging mixed moments of the Riemann zeta function to bound the large values of Dirichlet polynomials. They updated Ivic's original estimates using modern exponent pairs (like Bourgain's \( (13/84 + \varepsilon, 55/84 + \varepsilon) \)) [cite: 4].
3.  **Huxley's Subdivision Argument:** To refine the spacing of the zero-detecting points [cite: 14, 22].
4.  **Bourgain's Dichotomy Approach:** A sophisticated technique separating points based on whether they cluster heavily or remain sparse [cite: 1, 14].
5.  **Heath-Brown's Double Zeta Sums:** They applied Heath-Brown's 1979 estimates for double zeta sums, which bounds the interaction between pairs of points in the critical strip [cite: 4, 14]. 

The success of this fusion approach not only pushed the boundary of the Density Hypothesis for \( \mathrm{GL}(2) \) forms but also serves as a robust template that can be applied back to the Riemann zeta function and Dirichlet \(L\)-functions [cite: 1, 21].

### 5.2. $\mathrm{GL}(2)$ Twisted $L$-functions and Maass Forms
Progress for higher-degree and twisted \(L\)-functions has mirrored the cusp form breakthroughs. In May 2025, Sun, Wang, and Yu established an unconditional Selberg-type zero-density estimate for the family of twisted \(L\)-functions \( L(s, f \otimes \chi) \) in the critical strip, where \( f \) is a holomorphic primitive cusp form and \( \chi \) is a primitive Dirichlet character of modulus \( q \) [cite: 23]. Using this zero-density result, they obtained an asymptotic formula for the even moments of the argument function \( S(t, f \otimes \chi) = \pi^{-1} \arg L(1/2 + it, f \otimes \chi) \), proving a central limit theorem for its distribution [cite: 23].

Simultaneously, zero-density estimates for Maass cusp forms were advanced using the relative trace formula and Halász-Montgomery methods. Research on \( \mathrm{GL}(2) \) \(L\)-functions attached to Maass forms yielded power moments and zero density bounds applied to understand the equidistribution of fractional imaginary parts of zeros [cite: 24].

### 5.3. $\mathrm{GL}(3)$ Hecke-Maass Cusp Forms
The envelope has also been pushed to \( \mathrm{GL}(3) \). A December 2024 preprint demonstrated a weighted zero-density estimate for \(L\)-functions associated with Hecke-Maass cusp forms for \( \mathrm{SL}(3, \mathbb{Z}) \) in the spectral aspect [cite: 25]. By establishing an asymptotic formula for the twisted second moment of these \( \mathrm{GL}(3) \) \(L\)-functions, the researchers unlocked zero-density bounds that possess profound applications in spectral geometry and subconvexity [cite: 25].

## 6. Dedekind Zeta Functions and Beurling Generalized Numbers

### 6.1. Improved Estimates for Dedekind Zeta Functions
For a number field \( K \) of degree \( n = [K : \mathbb{Q}] \), the Dedekind zeta function \( \zeta_K(s) = \sum_{\mathfrak{a} \neq 0} (N\mathfrak{a})^{-s} \) exhibits a zero distribution highly sensitive to the field's degree. Defining \( \eta = 1 - \sigma \), zero density theorems near the 1-line take the form \( N_K(1-\eta, T) \ll T^{B_K(\eta) \eta + \varepsilon} \) [cite: 13]. 

Historically, Heath-Brown established \( B_K(\eta) \le n \) [cite: 13]. In a 2026 breakthrough, János Pintz proved significantly improved zero density theorems for Dedekind zeta functions in the vicinity of \( \Re(s) = 1 \). For example, for cubic fields (\( n=3 \)), Pintz's bounds approximate the Density Hypothesis, yielding \( B_K(\eta) \le 2 + O(\eta) \), a massive upgrade over Heath-Brown's \( B_K(\eta) \le 3 \) and Sokolovsky's bounds [cite: 13]. Pintz's proof relies on a general zero-density theorem for Dirichlet series, drawing deeply from the foundational mechanics established by Halász and Turán [cite: 13].

These bounds directly inform the Chebotarev Density Theorem. Explicit asymptotics and zero-density estimates (such as those by Thorner, Zaman, and Viglino) enable precise estimations of the density of primes splitting in specific Galois representations, significantly advancing van der Waerden's conjectures on Galois groups of random polynomials [cite: 26].

### 6.2. Beurling Generalized Prime Systems
Zero-density techniques have also been generalized to abstract frameworks like the Beurling generalized numbers. In 2024, Broucke, Debruyne, Révész, and Pintz investigated the Beurling zeta function \( \zeta_B(s) \) [cite: 27]. Using Halász's method and assuming Knopfmacher's Axiom A alongside the Ramanujan condition, they derived a Carlson-type density estimate for \( \zeta_B(s) \). This generalized bound comes surprisingly close to the Density Hypothesis for \( \sigma \) near 1, establishing that the structural mechanics of zero-density are not strictly tethered to the arithmetic properties of the integers, but rather to the analytic footprint of generalized Dirichlet series [cite: 27].

## 7. Primes in Short Intervals: The Synthesis of Zero-Density and Zero-Free Regions

One of the most consequential 2024-2026 developments is the rigorous clarification of the interplay between zero-density estimates and zero-free regions, spearheaded by Valeriia Starichkova [cite: 5, 10]. 

### 7.1. Generalizing Ingham and Heath-Brown/Iwaniec
Classically, bounding the difference between consecutive primes \( \psi(x+y) - \psi(x) \sim y \) depends on the sum over zeros:
\[ \sum_{|\gamma| \le T} x^{\beta-1} \]
Ingham's 1937 theorem dictated that if \( N(\sigma, T) \ll T^{A(1-\sigma)} \log^B T \), the PNT holds in intervals \( y = x^{1 - 1/A + \varepsilon} \) [cite: 5]. However, this ignores the contribution of the zero-free region (e.g., the Korobov-Vinogradov region \( \sigma > 1 - c(\log T)^{-2/3} (\log \log T)^{-1/3} \)). 

Starichkova (2025-2026) published a generalized version of Ingham's theorem, explicitly demonstrating the multiplicative dependence of the interval length \( y \) on the *combination* of zero-free regions and zero-density estimates [cite: 5, 6]. She similarly generalized the Heath-Brown and Iwaniec weighted zero-density estimates [cite: 5, 10]. 

### 7.2. Pushing the Boundaries of Short Intervals
By treating the interval length as \( y = x^\theta g(x) \) (where \( g(x) \) is a sub-polynomial function like \( \exp(\log^\alpha x) \)), Starichkova proved that if the Density Hypothesis ( \( A=2 \) ) holds, the Prime Number Theorem is valid in the exceptionally short interval:
\[ [x - \sqrt{x}\exp(\log^{2/3+\varepsilon} x), x] \]
This drastically refines the classic unconditional interval limit of \( [x - x^{1/2+\varepsilon}, x] \) associated with the Riemann Hypothesis [cite: 3, 5, 10]. Furthermore, by translating these generalized Ingham metrics to Dirichlet \(L\)-functions, Starichkova extended these refined error terms to the prime number theorem in arithmetic progressions, showing that almost all short arithmetic progressions exhibit perfect prime regularity under generalized density assumptions [cite: 3].

## 8. Extreme Values, Moments, and the Resonance Method

The behavior of \(L\)-functions on and off the critical line dictates their zero-density. If an \(L\)-function exhibits frequent, massive spikes in magnitude (extreme values), Dirichlet polynomials will register large values, driving up the zero-density bound. 

### 8.1. Joint Extreme Values via the Resonance Method
In May 2026, Athanasios Sourmelidis published critical findings on the joint extreme values of \(L\)-functions on and off the critical line [cite: 28]. He proved unconditionally that any number of distinct primitive \( \mathrm{GL}(1) \) and \( \mathrm{GL}(2) \) \(L\)-functions can *simultaneously* attain extremely large values on the critical line. This unconditionally improved a theorem by Heap and Li, which previously required the GRH for three or more \(L\)-functions [cite: 28].

To the right of the critical line, Sourmelidis utilized zero-density estimates to study the joint distribution of \( \mathrm{GL}(m) \) \(L\)-functions, improving upon the works of Mahatab, Pańkowski, and Vatwani regarding the Selberg class [cite: 28]. The primary machinery employed was the resonance method of Soundararajan and Hilberdink/Voronin. Crucially, on the critical line, Sourmelidis introduced a variation of **Heath-Brown's method for the fractional moments** of the Riemann zeta function. This allowed the avoidance of utilizing zero-distribution information for \(L\)-functions of degree less than three, bypassing massive technical obstacles [cite: 28].

### 8.2. Low-Lying Zeros and the Katz-Sarnak Heuristics
Zero-density estimates also heavily influence the statistics of low-lying zeros near the central point \( s = 1/2 \). In 2025, a study on the harmonically weighted one-level density of low-lying zeros of holomorphic newforms (of weight \( k \) and prime level \( N \to \infty \)) utilized zero-density estimates for Dirichlet \(L\)-functions as a primary analytical novelty [cite: 29]. 
Building on the Katz-Sarnak heuristics previously proven for test function support in \( (-3/2, 3/2) \), Ricotta and Royer extended the admissible support for all \( k \ge 2 \) to \( (-\Theta_k, \Theta_k) \). Using modern zero-density frameworks, researchers showed that \( \Theta_k \) tends monotonically to 2 asymptotically five times faster than prior bounds, representing a massive leap toward confirming the GRH-predicted symmetries of automorphic \(L\)-functions [cite: 29].

## 9. Alternative Frameworks: Dynamical Systems and Spectral Operators

While classical analytic number theory relies on contour integration and Dirichlet series bounding, 2025 also witnessed highly novel, interdisciplinary approaches to zero-density estimation. 

Rafik Zeraoulia (2025) proposed an algorithmic and heuristic solution to zero-density problems combining spectral, dynamical, and fractal techniques [cite: 30]. Inspired by the Hilbert-Pólya conjecture, Zeraoulia constructed a chaotic spectral operator \( O_x \) derived from the Riemann-von Mangoldt formula [cite: 30]. This operator mathematically captures the microscopic fluctuations of zeta zeros via a logarithmic differential term perturbed by the arithmetic signal \( \arg \zeta(1/2 + it) \).

By mapping the zero-density decay to the phase flow of \( O_x \) and computing its effective Lyapunov exponent (found numerically to be \( \lambda_{\mathrm{eff}} \approx -0.7 \)), Zeraoulia extracted a "chaotic filtration" mechanism. This yields a heuristic zero-density bound of:
\[ N(\sigma, T) \ll T^{1.7 + o(1)} \]
While currently a heuristic estimate, \( 1.7 \) is substantially smaller than the rigorous Guth-Maynard exponent of \( 30/13 \approx 2.307 \), suggesting that deep dynamical constraints suppress the density of zeros far off the critical line, offering an entirely new trajectory for future rigorous proofs [cite: 30].

## 10. Future Trajectories and the 2025-2026 Academic Horizon

The flurry of breakthroughs from 2024 to 2026 has set the stage for an explosive near-term future in analytic number theory. The mathematical community has quickly moved to absorb and expand upon these results. 

The **Clay Mathematics Institute** organized a major international CRC Workshop at the University of Oxford from September 29 to October 3, 2025, strictly dedicated to "Zeta and L-functions." [cite: 7]. The program explicitly highlighted the profound 2024/2025 momentum, focusing on:
1.  New zero density estimates for the Riemann zeta function (highlighting the Guth-Maynard \( 30/13 \) exponent) [cite: 7].
2.  Progress on the sub-convexity problem for \(L\)-functions [cite: 7].
3.  Connections between zero-density, probability theory, and random matrix theory [cite: 7].
4.  Progress on understanding moments in number field and function field settings (with emerging connections to algebraic topology) [cite: 7].

Looking to 2026 and beyond, the ongoing challenge remains translating the Guth-Maynard large value estimates to general Dirichlet \(L\)-functions \( L(s, \chi) \). As noted by researchers in the field, while Bellotti's log-free estimates and Chourasiya's explicit Ingham bounds are currently being generalized to the Dirichlet setting, extending the \( 30/13 \) decoupling bounds to the \( q \)-aspect (the modulus of the character) or to the spectral aspect of automorphic forms represents the next great hurdle [cite: 9, 20]. 

## 11. Conclusion

The landscape of zero-density estimates for \(L\)-functions has fundamentally transformed between 2024 and 2026. The half-century reign of Huxley's \( 12/5 \) bound was finally ended by Guth and Maynard's \( 30/13 \), redefining our unconditional understanding of the Prime Number Theorem in short intervals [cite: 4, 11]. Simultaneously, classical milestones set by Ingham and Carlson were fortified with explicit, computable parameters by researchers such as Chourasiya, Simonič, and Bellotti, directly aiding computational and cryptographic number theory [cite: 2, 9, 19].

Beyond the Riemann zeta function, the methodological legacy of Heath-Brown—spanning double zeta sums, 12th moments, and algebraic field extensions—has been expertly weaponized alongside Bourgain's dichotomy methods. This synthesis has allowed Chen, Debruyne, and Vindas to vastly expand the Density Hypothesis's validity for holomorphic cusp forms [cite: 1], and empowered Pintz, Sun, Wang, and Yu to establish new bounds for Dedekind and twisted \( \mathrm{GL}(2) \)/\( \mathrm{GL}(3) \) \(L\)-functions [cite: 13, 23]. 

Together, these advancements prove that zero-density estimation is not merely a fallback for the unproven Riemann Hypothesis, but a vibrant, highly sophisticated discipline driving modern mathematics closer to fully decoding the fundamental distribution of prime numbers.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDOVLkSG_mYsCy5xwNEGf-E_KEE0QSpvfeAUaSFQwP521SOh9qE_k22Mebz4oIzvYFZ9t3ApeXi0Z2T21-1gtXr1WomlP8iDGZx6Kuhj13ctEJj_biQw==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHysFbhTk8p878eBTKypFhJxz5Ru29APYhx5us7lowAkRSYAKUUVBK0pu2dTf5nPP6AcKDa-ZG7bFapzzmHYXBJYD5zIUKUlJb7S4XiFzlWNGnviY-2Qg==)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGC0nmHcxuyaJAam2cAFPDV4SYKxBcppuj3Jt4GSRm5VoT_1rdFB5JI2K7IR0AT5KAX5PlH__TIj_klIlJXhwxruy58dS57h1eMIJ_nRB83cTbNsTjkH7ybpSyltrwZU3njSIu-mq8BnrkK65A6jckD4u0GtjuA48ZKXXHIwyBJE36IkMysGZUblisofQQ5L76FP1Irsl-ACcZGFcoNSY_r8SNzCIurLXIPhcXi8r5i3qFrvDsaGIXRYw==)
4. [ugent.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2knAOcMR7uO3Vi_ALSXHZV1CpgOevohvV1zH_m_vC4HVNvryBTk8FgKXPGjhTdpShgee4cE7ogaaEBKjXWoabqzt4RUWF8-MErnpXei4RzH6nBOv9X9FhytTcZZuWw1rSPMK_dYi-vUkkFwLnuT4Www==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsysbhMOjeI4ErnYw3Mbx8DBmhxGXdNNvPDaVsLkZcs0yWC8y996V0U8ntglkS5RvDW7ug0yG2SSg6V4BCMchcGCfzcyo1PCAIymrpZ0DR4LqGXAuTCA==)
6. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGy2c--a77BHr1-YcXtagGWLzzO0UsvVEF33hYTNLckn5rDE0CL5THVmkBfIL9dNLFEAoNo8syNH9Mzw96yqKFR81x2xbdgq9iCAfh82mliSd_Gkwif2WHgneFpaG_UjVKqWnvZ5pG_CoDKjfvC6WZZCU4XFSB0HwD-oWKZbltV_mYUQVOY1hnpQjgZ1VbH4BMmAYHRwHbseRONToiFoFDm5b3CBly3vx1qLxk--rDuTNPY39JO99j6Mwd53cvigiCXFXdlfBMO5EwrRupl0gckudZ76Ze4WgVii_tzbdqcyw0EQTdY67H_)
7. [claymath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGf5EgRv9bs5-RUoTRbne2YNjjoPUzShyeMQvmj5oq0tU0O-Z4MT2UQblvBq8A3Fx9s3LAvBr3bn0bCzRjf8OQsroMrat3KkemBwNma1A10z-WjhnqWvbqZPp7he_4eloJ4US74W_KfiOuMfw==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGE1b6MSPkZQsw1LX8bqe6TvYg7BM3kI2_jWJsXy6kkY71jYcKb_tMWaE93tHgPV63cVWvthFi30n6lTCLFtRCerv6GDG_GyaD7tSpRxkcabasUfIGNnQ==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmRP13_gs8CXWAWfPwWzV25J2k0dKtiHCi3XDJLFO4-1XefFMt583UjkFqaSgLr40NMSCBTHucCYMEQtj8eYxVVLBvGJb2z4soDvqvTizIhvPlUX8xm3e7cw==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4wxeTP2h_atJ4lbyqqqSt9osdf9MFbn_W2VcaBaAzBQJPpKsr4G8gp3BwNQ1UQNZTrtQMGrMiZkX7FPFWgwvAZgy1d-SECY8ORHEpLkdrXjXLeSUMcQ==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsJ3F22yqs5sq14bLiHJbcHB3eQdLArOeav0omytL66T-3ILlgN_8a6A-se1a6teZLRJZ8fqe1AWICXzPOEe09tFYIx1WioXIAT4JiFLpuzf5N7lkN4cLIUw==)
12. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZSoEkefKY4qPxFO6Tkwx_RhGVA5SEPAFehTPn0nN_GgaT-uDpv0ymtrBSrgx2F7mRZgL_zgjlwf4wBcrOarwXGn7wl0sofi0TC0WWjQe3WdDB8sTJRZ3mAGHO)
13. [akjournals.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4nxYb-CQT5nU4MSKcNY0Ul15xCM8ZJYwExAIssEsGBseR_IIVgasSIR4NMtpuYxru18KU1X4HuSASLHzJ0A9UnMbtwmbFl6Kawp3dgyFvhLNeCU7g66XnrF_Qmk6BVP5oQMnzhxOx2u7a9JQVeWEAALel3CdK-ifAGPAqF3HdAKQKS4simdH2)
14. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYmPIneFuJ3KGjBtJ702vMCiuwPE2R3nq-58c-O-OFRCZmdB5dqtqdzftzePH2vZpzhvn5ig7LZSf8QXP3yBHdrds194K7YSJQfpS0tZLAzESiXmeh-0Yg77VzyQfRHagj7_GsYto=)
15. [mathstodon.xyz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYl6WR0pPsO4UHQM3kYwIG7xR3JXKDD2_ego9bsg6XteZVY-irKAwj8RpjwEwqIB903Aicf3kUpoK_ci8o2gtnuYB77AZNf81NupwAzleWlkAC1g9z2KZs0DjXy1Do0ZV9A08E)
16. [mathstodon.xyz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFG5h7pVABZu_LQD-9BQqq5aFGagKQ-yPcNFyIXXrmWSDiSkIurzky0eH1KD4cvcvwosEYmRixGFIjGGsNtbqdRlCTMwoyezGsvh0jRVUBwqjnu6Tm1Zam57DA8Eualzfunqh73)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_twVWIXKNagEg_2P96d2rxMJajHO7HlaVSR9DlBUqnGQEubPWJML3YzOQ-p6JMVVhsFkWTOAFbjn5Ezmsdl-d_0wWBWl3ljBb5Rrop9UPN5hKjtYOncXWMg==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEL9AhKRSvQX59F-42gDbGKRwh0F6w5LXAJRD52IMSwNNjww4BSz0I1_9dYuJv-FGae6zPSeegEqQlCqDeNUeky-29bOcGipNkiRCKXaTt4SAHfEwkTug==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH29Hvziy5Hpol2OKskPsy2uChfu-KpENoih6pmbVcrneUl5tNpwMTIqbAL1dWGZ1-fO3LwkuDWdJTukHO79UhzBeKmvHehiad9kOYUtLLCts2I8kg2CQ==)
20. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEV2a2Z7JpCDOijPXXXWe0BWFqprxyScs_hhziwmE4PR3vIm7GYvEQWFlCdraONyHTLGn8vHLBUtUZ92XTbAa45ngw-5CWwG3Czfu7NHa2TKJzqFX8Uh81Dzz-Q3VuFuyRk1HxZwffUrSwUKrOuVpeemhnjyNK3-1W5jxkg4Obs1cvnga66Pae1c8wS5bOej6bLE7tFsJPD51fJIkrL8zZ6yHCV)
21. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUXquHMh5ywQ6iH6JxsYhCTGk1U4V1P5jjBTIRkkdWphMem391abvzyXkpiwWiBG60w2HvD5G2s3IvHyCYtIqpDE_WeBeOjuIFfp3koJBT4QMQXgO9MT0-j2g9RZlCiMv4AgR2Km_FwdFf)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjP57VXTb2BeJyAmLVN7U3XgLU7FTLMwcVwVfuJUOPVwHlwoLcCpXn7IEhaBqnrI6L1cdnv1G46ifXGsLKK4HGQCTFO0iBNFZ3zUc9XGVZyMkZbgsYAg==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuJYTY3Fdxme5Ejz18_RD8kbbXhp3pj7D-dfR7TDNXObFPS_lRTEBcbhPFukAArKX6ca431UzMcsbO-ruFdBEEkPXWVOkKlH0_Fubggs_aAZ7Gs5yHkQ==)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZEajVqdzrFWwkxRwWO0Ymd82OuHVcNSyzaa3qmwjCoIbDA6o_Yl1OZak7VTBTwo4Wj5YEC8C_lkGjrx-moQeGwF7OCoCGnxwtntLCU0vrNXfZGAcfMMDEpIs-vswMtO6pR6pDVvNeAq82p4qQ88BXG7Hm_4LV9P9uzKvOW7TuDJfHKwkL3oJfML-5clwEzvuSSbq7RwKraCE9W2D2hozCxtpYlnq9XHJa_BQBxuK3m_HYeC7ORuoubY0=)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFu98VPwpv3Z2QMm-M_yakzA3s_Hq7M3EIJYRY6gG3726PFZAXTNVwxc-k9PU_DNxMLD8VxCgleLQszsbQPAKkuu0dcRlHFPctGBrKMM781U67kbHOVcw==)
26. [ethz.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE93j8Yx9r0xYjmrPg7Hvj-NidSXrL-fyOALFLgCfcjMz9xhPuK_sBl-Eg6Zc5U_rQ3ZkRNG3ftAi2HUv3na0DXzjFMlkvuyWhBO1k8GnqUEDjZDXW9tNb7Wj3j0grAxKIdrSPa1NpUM9qRD40CoC36lMZeEZap7bDGusSBI_iehftXsd8_S_Aqy6NRcw4irfLFqE13Pm4=)
27. [mtak.hu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDLZU6OUBWctH_bIi95AD756MhxAwbHY3y2fLJqyiwYnG1DvfNzrbfdwcmzC4kfO3uomFlEKjLCqRJSM3jMBWGJh649ivDZ8zUySQZ9IaPgJuqZtcd25BIyfAsA2h4Pi6No0yK)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXrWYkPS4OtjfMY6G_bn2v9ibVlUdd1S2aO9oy2Ygc6Sy1XF0XJDbXYXbqkBV28KG86RDnG11Ag-Pjoh8Q_8BT9-Jm6uBiu6wAUON9UTZ5hj2Rtn3dXQ==)
29. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKNvoCizPc0cd3xnNOEbpKaLyuUqg5_4NpOW2SmUmqF_CUS-MQqTtIxZtCnZLCTtKhPuQDLj8dELJHocuO8ExNr07ntBGrh34jZTMLMaoBrf5Dnf6jYMNK7rmJjGQ=)
30. [sciety.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEluU0pyr6J1zrEMFic7QmhXZ3T4rV6nnRI8TCLLPtIBXiySbGWFkgTfUlqslYyABdSrJqcZfs3dwXygoA8-XtuBPtSRyAMWmnldTZeQJb8BsFM7ni6BHN3mYi8Vp6PTNtc4HcsARQxfZ5H5pQnf2M2BUi5leioAJW9Pi1wcRb-R0HibD7oJ5coO6Q2aKOmlAwV9AalgFYqXpuIdpKLgp0=)

