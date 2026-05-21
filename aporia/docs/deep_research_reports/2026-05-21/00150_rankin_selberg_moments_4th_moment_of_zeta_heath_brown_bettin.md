# Rankin-Selberg moments / 4th-moment of zeta (Heath-Brown, Bettin) 2024-2026

**Pythia queue id:** 150
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdxREVQYXZLdEdxemNqTWNQbl9pRGtBaxIXcURFUGF2S3RHcXpjak1jUG5faURrQWs
**Elapsed:** 311s
**Completed at:** 2026-05-21T16:29:20.514747+00:00

---

# Advances in Rankin-Selberg Moments and the Fourth Moment of the Riemann Zeta-Function: Contemporary Developments (2024–2026)

**Key Points:**
*   Research suggests that the synthesis of twisted moments of the Riemann zeta-function and Rankin-Selberg convolutions continues to unveil deep structural properties of L-functions on the critical line.
*   Recent breakthroughs in 2025 indicate that the amplified fourth moment of the Riemann zeta-function can be asymptotically evaluated with high precision, yielding new implications for the gaps between critical zeros.
*   The evidence leans toward quantum modularity and spectral reciprocity acting as foundational tools for understanding additive twists and shifted moments, bridging dynamical systems and analytic number theory.
*   It seems likely that classical error terms, such as those formulated by Heath-Brown for the fourth moment and Dirichlet L-functions, will continue to be sharpened using modern subconvexity and Voronoi summation methods.

**Introduction to the Evolving Landscape**
The study of the moments of the Riemann zeta-function and the broader class of automorphic L-functions remains one of the most rigorously debated and fertile grounds in modern mathematics. By analyzing the average behavior of these functions along the critical line, mathematicians seek to uncover the elusive properties governing prime numbers, quantum chaos, and spectral geometries.

**Recent Trends (2024–2026)**
In the period between 2024 and 2026, researchers have increasingly turned to sophisticated techniques, combining historical methods engineered by D.R. Heath-Brown with contemporary innovations by Sandro Bettin, H.M. Bui, and their collaborators. These newer frameworks utilize advanced Dirichlet polynomial mollifiers, amplifiers, and Rankin-Selberg integrals to crack open problems that have resisted solution for decades. 

**Scope of this Report**
This report synthesizes the latest academic literature on the fourth moment of the Riemann zeta-function, Rankin-Selberg moments, and their interconnected error terms. We will explore recent publications, including those detailing amplified fourth moments, generalized quantum modularity, and explicit mean-value theorems for Rankin-Selberg convolutions. 

***

## Introduction: The Critical Line and the Anatomy of Moments

The analytic theory of the Riemann zeta-function, \(\zeta(s)\), and its generalizations to Dirichlet L-functions and Rankin-Selberg convolutions revolves heavily around the distribution of zeros and the growth of these functions on the critical line \(\text{Re}(s) = 1/2\). A primary analytical tool for investigating these properties is the evaluation of their power moments. Specifically, the \(2k\)-th moment of the Riemann zeta-function is defined as:
\[ I_k(T) = \int_0^T |\zeta(1/2 + it)|^{2k} \, dt \]

For nearly a century, only the first two integer moments were known asymptotically. Hardy and Littlewood established the asymptotic formula for the second moment (\(k=1\)) in 1918, and A.E. Ingham evaluated the fourth moment (\(k=2\)) in 1926 [cite: 1, 2]. Despite monumental efforts by mathematicians throughout the 20th and 21st centuries, no exact asymptotic formula has been rigorously proven for any \(k \ge 3\), though conjectures based on Random Matrix Theory (RMT), particularly those proposed by Keating and Snaith, offer highly precise predictions for the leading coefficients [cite: 1, 3].

The transition from purely classical moment evaluations to the study of **twisted moments**—where the integrand is multiplied by a Dirichlet polynomial—marked a watershed moment in analytic number theory. These Dirichlet polynomials act either as **mollifiers** (which dampen the large values of the zeta-function to locate zeros) or **amplifiers** (which exaggerate specific behaviors to yield subconvexity bounds). The foundational works in this area were significantly propelled by D.R. Heath-Brown, whose techniques established rigid bounds for fractional moments and the fourth power mean of Dirichlet L-functions [cite: 4, 5].

In the current era spanning 2024 to 2026, the intersection of Heath-Brown's foundational architectures with the modern spectral techniques developed by mathematicians like Sandro Bettin, H.M. Bui, Xiannan Li, and Maksym Radziwiłł has resulted in a flurry of breakthroughs. The narrative of this report centers on these modern developments: the evaluation of the amplified fourth moment of \(\zeta(s)\) (Bui, Hall, Subira Jorge, 2025) [cite: 2, 6], the twisted fourth moment of Dirichlet L-functions (Gao and Zhao, 2025) [cite: 7], the mean value of Rankin-Selberg error terms (Huang, Liu, Zhang, 2025) [cite: 8], and the profound implications of quantum modularity applied to additive twists (Bettin, Drappeau, 2026) [cite: 9, 10].

## Historical Scaffolding: Heath-Brown's Contributions to the Fourth Moment

To fully appreciate the 2024–2026 breakthroughs, one must understand the bedrock upon which they are built, heavily influenced by D.R. Heath-Brown. 

### Fractional Moments and the Riemann Zeta-Function

In 1981, Heath-Brown published a highly influential paper on the fractional moments of the Riemann zeta-function [cite: 3, 5]. At a time when researchers were struggling to move beyond Ingham's fourth moment, Heath-Brown provided unconditional bounds for small rational moments and conditional bounds for larger moments assuming the Riemann Hypothesis (RH). Specifically, Heath-Brown proved that:
\[ I_k(T) \gg T(\log T)^{k^2} \]
for any rational \(k \ge 0\), and established the corresponding upper bounds for \(k = 1/n\) where \(n\) is a positive integer [cite: 5]. Under the assumption of the Riemann Hypothesis, Heath-Brown extended the upper bounds to all \(0 \le k \le 2\), ensuring that the actual growth rate aligns perfectly with what would later be predicted by Random Matrix Theory [cite: 3, 5]. 

Heath-Brown's method involved deep convexity arguments, which he later refined in 1993 using inequalities involving the derivatives of \(\zeta(s)\) [cite: 5]. These fractional moment frameworks directly influenced how modern mathematicians, including Sandro Bettin and Maksym Radziwiłł, approach the upper bound principles for moments of L-functions today [cite: 3].

### The Fourth Power Mean of Dirichlet L-functions

Beyond the Riemann zeta-function, Heath-Brown was instrumental in evaluating the fourth moment of Dirichlet L-functions in the level aspect. In 1981, he established an asymptotic formula for the fourth power mean of Dirichlet L-functions for prime moduli \(q\):
\[ \sum_{\chi \text{ mod } q}^* |L(1/2, \chi)|^4 = \frac{q}{2\pi^2} \log^4 q + O(q \log^3 q) \]
where the asterisk denotes summation over primitive characters [cite: 11].

Heath-Brown also provided a full asymptotic expansion for the second moment (\(k=1\)) of Dirichlet L-functions, a result so enduring that it continues to inspire new proofs and generalizations. For instance, in 2025, a paper by Dasgupta and co-authors offered a new proof of Heath-Brown's full asymptotic expansion using analytic continuation and stationary phase analysis, extending it to a twisted first moment of Hecke-Maass L-functions [cite: 11, 12]. These historical benchmarks remain the gold standard against which modern power-saving error terms are measured [cite: 4, 11].

## The Twisted and Amplified Fourth Moment: Developments (2024–2026)

A pivotal evolution from the pure fourth moment is the **twisted fourth moment**. Here, the Riemann zeta-function is multiplied by a Dirichlet polynomial \(A(s) = \sum_{n \le N} a_n n^{-s}\). By optimizing the coefficients \(a_n\), researchers can extract immense amounts of arithmetic data. 

### The Hughes-Young and Bettin-Bui-Li-Radziwiłł Foundations

The modern era of the twisted fourth moment was arguably initiated by Hughes and Young in 2010, who evaluated the fourth moment of \(\zeta(s)\) twisted by a Dirichlet polynomial of length \(T^{1/11 - \epsilon}\) [cite: 2, 13]. 

This barrier was substantially shattered in 2020 by Sandro Bettin, H.M. Bui, Xiannan Li, and Maksym Radziwiłł. In their landmark paper published in the *Journal of the European Mathematical Society*, they increased the permissible length of the Dirichlet polynomial up to \(T^{1/4 - \epsilon}\) [cite: 2, 6, 13]. To achieve this, Bettin et al. relied crucially on Watt's theorem concerning averages of Kloosterman fractions, which served as an optimal replacement for Selberg's eigenvalue conjecture within the context of the twisted fourth moment [cite: 13]. Their work significantly simplified the combinatorics of the main terms by introducing a smoothed averaging mechanism over the variables in the associated quadratic divisor problem [cite: 6, 13]. 

### Breakthrough in 2025: The Amplified Fourth Moment

Building directly upon the Bettin-Bui-Li-Radziwiłł architecture, a major breakthrough was published in November 2025 by Hung M. Bui, Richard R. Hall, and Martin Subira Jorge. Their paper, titled *"Amplified Fourth Moment of the Riemann Zeta-Function and Applications"*, fundamentally shifts the utility of the twisted fourth moment toward **amplifiers** [cite: 2, 6].

In L-function theory, one often takes a Dirichlet polynomial to mimic either \(1/\zeta(s)^r\) (a mollifier) or \(\zeta(s)^r\) (an amplifier) for some \(r > 0\). Prior to this 2025 paper, known results included the mean value of the fourth power of \(\zeta(s)\) times the square or the fourth power of a mollifier, or merely the square of an amplifier [cite: 2, 6]. 

Bui, Hall, and Subira Jorge successfully derived the asymptotic formula for the fourth moment of the Riemann zeta-function multiplied by the **fourth power of an amplifier** [cite: 2]. The integral in question takes the form:
\[ \int_0^T |\zeta(1/2 + it)|^4 |A(1/2 + it)|^4 \, dt \]
where \(A(s)\) acts as an amplifier mimicking \(\zeta(s)^r\).

#### Applications to Gaps Between Zeros
The primary application of this amplified fourth moment formula lies in the spacing of zeros of the Riemann zeta-function. Let \(\rho = \beta + i\gamma\) denote the non-trivial zeros of \(\zeta(s)\). The normalized gap between consecutive zeros on the critical line is a subject of intense study, often quantified by a bounding parameter \(\Lambda\).

According to the 2025 paper, evaluating the amplified fourth moment provides a rigorous mechanism for bounding these gaps from below [cite: 2]. Historically, Hall used a variant of the Wirtinger inequality involving the \(L^4\)-norm of the Hardy Z-function to show that \(\Lambda > 2.63\), which was later improved by Bui and Milinovich to \(\Lambda > 3.18\) [cite: 2]. By deploying their newly proven amplified fourth moment, Bui, Hall, and Subira Jorge provide a vastly superior framework for pushing these bounds further [cite: 2].

The theorem established by Bui, Hall, and Subira Jorge explicitly utilizes the theorem of Bettin, Bui, Li, and Radziwiłł as a foundational lemma (Theorem 3.1 in their paper), confirming the enduring legacy of the 2020 result [cite: 2]. They note that while they focused on the simplest choice of \(r=1\) to demonstrate the efficacy of the method for studying gaps between zeros, higher-degree polynomial choices could significantly improve the numerical bounds for \(\Lambda\) [cite: 2].

### Table 1: Evolution of the Twisted Fourth Moment of the Riemann Zeta-Function

| Year | Authors | Key Contribution | Length of Dirichlet Polynomial |
| :--- | :--- | :--- | :--- |
| 1926 | A.E. Ingham | Un-twisted fourth moment asymptotic formula. | N/A |
| 2010 | Hughes & Young | Twisted fourth moment asymptotic formula. | \(T^{1/11 - \epsilon}\) |
| 2020 | Bettin, Bui, Li, Radziwiłł | Optimal twisted fourth moment using Watt's Kloosterman fractions. | \(T^{1/4 - \epsilon}\) |
| 2025 | Bui, Hall, Subira Jorge | Asymptotic formula for the fourth moment times the fourth power of an amplifier. | Arbitrary within \(T^{1/4 - \epsilon}\) limit |

## Dirichlet L-Functions: Fixed Moduli and Power-Saving Error Terms

While the Riemann zeta-function provides the prototype for moments on the critical line, the transition to Dirichlet L-functions \(L(s, \chi)\) over varying moduli \(q\) introduces complex character sums and hyper-Kloosterman variations. As discussed, Heath-Brown's 1981 evaluation of the fourth moment for prime moduli \(q\) was a landmark achievement [cite: 4, 11].

### The 2025 Evaluation by Gao and Zhao
In July 2025, Peng Gao and Liangyi Zhao published a definitive paper titled *"Twisted fourth moment of Dirichlet L-functions to a fixed modulus"* [cite: 7]. This paper addressed a critical gap in the literature: evaluating the twisted fourth moment on the critical line for the family of Dirichlet L-functions to a **fixed prime power modulus**, while simultaneously securing an asymptotic formula with a **power-saving error term** [cite: 7]. 

The expression under consideration is the average over primitive characters \(\chi \pmod q\):
\[ \sum_{\chi \pmod q}^* |L(1/2, \chi)|^4 |M(1/2, \chi)|^2 \]
where \(M(1/2, \chi)\) is a Dirichlet polynomial mollifier.

Gao and Zhao's methodology relies upon applying the approximate functional equation for products of L-functions, representing the sum as a convergent series over variables \(m\) and \(n\) [cite: 7]. A main term arises from the diagonal contribution, while the off-diagonal terms require delicate partitions of unity to localize the sums [cite: 7]. 

Crucially, when the variables \(M\) and \(N\) are far apart, Gao and Zhao deployed techniques involving the Voronoi summation formula [cite: 7]. By converting longer sums over \(n\) into shorter sums, they leveraged bounds on divisor-like sums in arithmetic progressions to show that these terms contribute strictly to the power-saving error margin [cite: 7]. 

#### Implications for Mollified Moments
The importance of evaluating this twisted, shifted moment lies heavily in its downstream applications to **mollified moments** [cite: 7]. As highlighted by Gao and Zhao, having precise asymptotic formulae for twisted moments allows mathematicians to utilize the upper bound principles developed by Maksym Radziwiłł and Kannan Soundararajan [cite: 7]. These principles allow for the establishment of sharp bounds on all central moments of the Dirichlet L-function family below the fourth moment [cite: 7]. Moreover, by incorporating various shifts into the moments, the higher-order poles that complicate the main terms in standard asymptotic formulas are reduced to simple poles, vastly demystifying the algebraic structure of these main terms [cite: 7].

## Rankin-Selberg Convolutions and Mean Value Estimates

The Rankin-Selberg method, originally developed to estimate the Fourier coefficients of modular forms, naturally extends to the construction of L-functions attached to pairs of automorphic forms, denoted \(L(s, f \times g)\) [cite: 14, 15, 16]. The study of moments for Rankin-Selberg L-functions is notorious for its difficulty due to the high degree of the associated Euler products and the complexity of the functional equations.

### The Rankin-Selberg Error Term \(\Delta_1(x; \phi)\)

In classical analytic number theory, the Dirichlet divisor problem seeks to bound the error term \(\Delta(x)\) in the asymptotic formula for the sum of the divisor function. The Rankin-Selberg problem generalizes this by examining the sum of the squares of the Fourier coefficients of a modular form. The error term in this classical Rankin-Selberg problem is denoted \(\Delta_1(x; \phi)\) [cite: 8, 17].

In August 2025, Jing Huang, Yukun Liu, and Deyu Zhang published a highly significant paper in the journal *Mathematics* (13(16), 2681) titled *"On Some Mean Value Results for the Zeta-Function and a Rankin-Selberg Problem"* [cite: 8, 18]. Their research connects the classical error term of the Rankin-Selberg problem with the mean square of the Riemann zeta-function [cite: 8].

The authors successfully established an upper bound for the integral:
\[ \int_0^T \Delta_1(t; \phi) \left| \zeta\left(\frac{1}{2} + it\right) \right|^2 \, dt \]
Furthermore, for fixed integers \(2 \le k \le 4\), Huang, Liu, and Zhang derived a precise asymptotic formula for the higher power moments integrated against the zeta-function:
\[ \int_1^T \Delta_1^k(t; \phi) \left| \zeta\left(\frac{1}{2} + it\right) \right|^2 \, dt \]
[cite: 8, 17].

#### Methodological Innovations in the Rankin-Selberg Mean Value
To evaluate these highly complex integrals for \(k=2, 3, 4\), the authors relied heavily on previous estimates of the power moments of \(\Delta_1(t; \phi)\) combined with the classical error term \(E(t)\) from the mean square of the Riemann zeta-function [cite: 8, 17]. 

A critical component of their proof involves the **truncated Voronoi summation formula** and the method of large value estimation [cite: 8]. When evaluating the fourth moment (\(k=4\)), the authors dealt with a configuration of frequencies \(\Omega := n_1^{1/4} + n_2^{1/4} - n_3^{1/4} - n_4^{1/4}\) [cite: 8]. The spacing and cancellations of these frequencies dictate the size of the error term. Using splitting arguments, the authors were able to tightly bound the off-diagonal contributions [cite: 8]. This builds on a historical continuum of bounds stretching from Deligne's bound on Fourier coefficients (\(|a(n)| \le n^{\frac{\kappa-1}{2}} d(n)\)) to Heath-Brown's classical improvements on the limits of moments without absolute values [cite: 8].

### Rankin-Selberg Coefficients in Large Arithmetic Progressions

Another major facet of Rankin-Selberg research in this timeline (2024–2025) involves the distribution of Rankin-Selberg coefficients in arithmetic progressions. Emmanuel Kowalski, P. Michel, and W. Sawin have laid extensive groundwork here [cite: 19, 20, 21]. Very recently, building upon the work of Kowalski, Lin, and Michel concerning Rankin-Selberg coefficients in large arithmetic progressions, Bingrong Huang made further strengthenings to the exponent of the error term, achieving an exponent of distribution \(\theta = \frac{2}{5} + \frac{1}{260} - \eta\) under the Ramanujan-Petersson conjecture for GL(2) Maass forms [cite: 19]. 

This level of distribution is crucial when analyzing the shifted moments of L-functions because it governs how aggressively one can truncate the Dirichlet series during the application of approximate functional equations without drowning the main term in the error margin [cite: 19].

## Quantum Modularity and Spectral Reciprocity (2024–2026)

One of the most fascinating developments over the 2024–2026 period is the geometric and dynamical re-interpretation of L-function moments. Specifically, the interplay between **quantum modular forms**, introduced by Don Zagier, and the **additive twists** of L-functions has revolutionized our understanding of error terms and reciprocity formulas.

### Sandro Bettin and Sary Drappeau's 2026 Breakthrough
In January 2026, Sandro Bettin and Sary Drappeau published *"On quantum modular forms of non-zero weights"* in *Compositio Mathematica* [cite: 9]. This paper provides a sweeping dynamical framework for understanding functions \(f\) on the rationals \(\mathbb{Q}\) that satisfy a quantum modularity relation:
\[ f(x+1) = f(x) \quad \text{and} \quad f(x) - |x|^{-k} f(-1/x) = h(x) \]
where \(h(x)\) possesses specific regularity conditions [cite: 9].

Bettin and Drappeau focused on the case where \(\text{Re}(k) = 0\). By iterating the quantum modularity relation and utilizing periodicity, they expressed \(f\) as a twisted **Birkhoff sum** of \(h\) evaluated along orbits under the Gauss map, with the twist provided by a multiplicative automorphic factor [cite: 9]. 

The monumental achievement of this work is proving the existence of a limiting function that extends \(f\) continuously to the real line \(\mathbb{R}\) in a specific topological sense [cite: 9]. Consequently, Bettin and Drappeau deduced that the values \(\{f(a/q) \mid 1 \le a < q, (a,q)=1\}\), appropriately normalized, tend to **equidistribute** according to a stable limiting measure, which under natural hypotheses is proven to be diffuse [cite: 9]. 

#### Applications to Automorphic L-Functions
How does this connect to the moments of the Riemann zeta-function and Rankin-Selberg convolutions? Bettin and Drappeau applied their quantum modularity theorems to obtain limiting distributions for several arithmetic functions directly tied to L-functions [cite: 9]. Specifically, they proved that the **central values of additive twists of a cuspidal L-function** define a quantum modular form [cite: 22]. 

This directly implies a **reciprocity law** for the twisted first moment of multiplicative twists of cuspidal L-functions, operating much like the reciprocity laws discovered by J.B. Conrey for the twisted second moment of Dirichlet L-functions [cite: 22]. As Drappeau and Bettin demonstrated in their ongoing collaborations (including joint works with Jungwon Lee), central modular symbols associated with a holomorphic cusp form for \(SL(2, \mathbb{Z})\) exhibit a Gaussian distribution, validating statistical models of automorphic forms [cite: 10, 22].

### Subconvexity and Degree-8 L-Functions
The concept of reciprocity is not merely a structural curiosity; it is a powerful computational tool for breaking the convexity bound of L-functions. In a 2025 paper, researchers extended level aspect reciprocity formulae concerning the moments of the product of L-functions in different families, building on the works of Blomer, Khan, and Zacharias [cite: 23, 24].

Valentin Blomer and Rizwanur Khan had previously established a non-symmetric reciprocity formula expressing the fourth moment of automorphic L-functions of level \(q\) twisted by the \(\ell\)-th Hecke eigenvalue as a twisted mixed moment of automorphic L-functions of level \(\ell\) [cite: 24]. These formulae feature a product of L-functions of total degree 8 [cite: 23, 25].

In 2025, this symmetry-breaking reciprocity was leveraged to obtain subconvex bounds of \(O(q^{5/6 + \epsilon})\) for L-functions of degree 8 and the Lindelöf average bound for L-functions of degree 10 [cite: 23]. These subconvexity bounds are critical for evaluating Rankin-Selberg moments because they allow researchers to tightly constrain the off-diagonal elements in the Kuznetsov trace formula and the Voronoi summation [cite: 21, 23, 24].

## Methodological Synergies: How the 2024–2026 Results are Proved

To write an exhaustive report on this subject, one must dissect the specific mathematical machinery that allowed Bettin, Bui, Heath-Brown, and others to achieve these results.

### 1. The Approximate Functional Equation
At the heart of any moment calculation is the approximate functional equation. For the Riemann zeta-function, it essentially states that \(\zeta(s)\) can be approximated by two truncated Dirichlet series. When evaluating the fourth moment \(\int |\zeta(1/2+it)|^4 dt\), the integrand is expanded as a product of four Dirichlet series (two for \(\zeta\), two for \(\bar{\zeta}\)), resulting in a sum over four variables \(m_1, m_2, n_1, n_2\). The diagonal terms (\(m_1 m_2 = n_1 n_2\)) produce the main polynomial in \(\log T\), while the off-diagonal terms (\(m_1 m_2 \neq n_1 n_2\)) are heavily oscillatory and must be bounded [cite: 26].

### 2. The Delta Method of Duke, Friedlander, and Iwaniec (Refined by Heath-Brown)
To handle the condition \(m_1 m_2 - n_1 n_2 = h\), mathematicians employ the delta method, pioneered by Duke, Friedlander, and Iwaniec, and famously refined into a smooth version by D.R. Heath-Brown [cite: 27, 28]. Heath-Brown's version replaces the strict arithmetic condition of the Kronecker delta with a smooth analytic weight, allowing the sum to be decomposed into continuous integrals and additive character sums [cite: 27]. 

This exact mechanism was heavily utilized in the 2020 paper by Bettin, Bui, Li, and Radziwiłł to solve the quadratic divisor problem smoothly averaging over all variables, which simplified the extraction of the twisted fourth moment of the Riemann zeta function [cite: 6, 13]. 

### 3. Kloosterman Sums and Watt's Theorem
When applying the delta method or Voronoi summation, the additive characters inevitably cluster into **Kloosterman sums**. Bounding these sums is historically tied to the Weil bound and the Ramanujan-Petersson conjectures [cite: 13, 29, 30]. In the context of the twisted fourth moment, Watt's theorem on the averages of Kloosterman fractions acts as the optimal replacement for Selberg's eigenvalue conjecture, providing the necessary square-root cancellation to extend the length of the Dirichlet polynomial mollifier up to \(T^{1/4 - \epsilon}\) [cite: 6, 13].

### 4. The Kuznetsov Trace Formula and Voronoi Summation
For Rankin-Selberg L-functions and Dirichlet L-functions, the GL(2) and GL(3) Kuznetsov trace formulas provide a spectral decomposition of sums of Kloosterman sums into a continuous spectrum (Eisenstein series) and a discrete spectrum (Maass forms) [cite: 26, 31, 32]. In the 2025 results concerning the Rankin-Selberg error term \(\Delta_1(t; \phi)\) evaluated by Huang, Liu, and Zhang, truncated Voronoi summation formulas were deployed to expand the error term into a series of Bessel functions and Fourier coefficients [cite: 8]. The subsequent integration against the mean square of zeta required sharp upper bounds on the oscillatory integrals, often utilizing stationary phase analysis [cite: 8, 12].

### Table 2: Methodological Toolkit for Modern Moment Calculations

| Technique | Primary Usage | Notable Practitioner / Paper |
| :--- | :--- | :--- |
| **Delta Method** | Separating variables in quadratic divisor problems (\(ab - cd = h\)). | Heath-Brown (1996) [cite: 27], Bettin et al. (2020) [cite: 13] |
| **Kuznetsov Trace Formula** | Translating sums of Kloosterman sums into spectral parameters. | Blomer & Khan [cite: 25, 31] |
| **Voronoi Summation** | Converting long Dirichlet series in off-diagonal terms into shorter dual sums. | Gao & Zhao (2025) [cite: 7], Huang et al. (2025) [cite: 8] |
| **Quantum Modularity** | Extracting continuous limit distributions from additive twists via Birkhoff sums. | Bettin & Drappeau (2026) [cite: 9] |
| **Wirtinger Inequalities** | Bounding gaps between critical zeros using \(L^4\)-norms of Hardy's Z-function. | Hall, Bui, Subira Jorge (2025) [cite: 2] |

## Synthesis: From Heath-Brown to the 2026 Frontier

The trajectory from D.R. Heath-Brown's seminal 1979 and 1981 papers to the 2025/2026 discoveries illustrates a profound compounding of analytic technologies. Heath-Brown's original evaluation of the fourth power mean of Dirichlet L-functions set a high-water mark for error term precision [cite: 4, 11]. When Sandro Bettin, H.M. Bui, Xiannan Li, and Maksym Radziwiłł pushed the twisted fourth moment of the Riemann zeta-function to accommodate Dirichlet polynomials of length \(T^{1/4 - \epsilon}\), they unlocked new paradigms [cite: 6, 13].

In 2025, Bui, Hall, and Subira Jorge masterfully redirected this tool. By evaluating the fourth moment of \(\zeta(s)\) multiplied by the fourth power of an amplifier, they circumvented the traditional mollification barriers, yielding stronger lower bounds for the gaps between the zeros of \(\zeta(s)\) [cite: 2]. Their ability to push the spacing boundary \(\Lambda > 3.18\) (and conceptually further with higher degree polynomials) relies intimately on the exactness of the twisted fourth moment main terms derived in 2020 [cite: 2].

Concurrently, the treatment of Dirichlet L-functions saw symmetrical advancements. Gao and Zhao's 2025 derivation of the twisted fourth moment to a fixed prime power modulus provided the power-saving error terms required to deploy the Radziwiłł-Soundararajan upper bound principle [cite: 7]. This ensures that the moments of the Dirichlet L-functions behave just as strictly as the Riemann zeta-function under mollification.

On the Rankin-Selberg front, the physical manifestation of these error terms—specifically \(\Delta_1(t; \phi)\)—has been integrated directly against the mean square of the zeta-function by Huang, Liu, and Zhang in 2025 [cite: 8]. By utilizing splitting arguments and higher power moments of the Riesz mean error term, they provided explicit upper bounds and asymptotic formulas for \(k \in \{2, 3, 4\}\) [cite: 8]. This synthesis connects the continuous spectrum of the zeta-function directly with the discrete modular forms governing the Rankin-Selberg convolutions.

Finally, the philosophical shift led by Bettin and Drappeau (2026) regarding quantum modular forms suggests that many of these highly oscillatory error terms and twisted moments are not merely analytical artifacts, but possess intrinsic, continuous geometric distributions when mapped appropriately through dynamical systems [cite: 9]. The fact that additive twists of cuspidal L-functions form quantum modular forms directly yields the spectral reciprocity required to break subconvexity bounds for higher-degree L-functions, as demonstrated by the degree-8 results of Blomer, Khan, and Zacharias [cite: 22, 23, 25].

## Conclusion

The 2024–2026 epoch in analytic number theory represents a golden age for the evaluation of L-function moments. The legacy of D.R. Heath-Brown—defined by rigorous fractional moment bounds and the smooth delta method—has been fully absorbed and weaponized by modern mathematicians. Through the work of Sandro Bettin, H.M. Bui, Peng Gao, Sary Drappeau, and their respective co-authors, the twisted and amplified fourth moments of both the Riemann zeta-function and Dirichlet L-functions are now understood with power-saving precision. 

The integration of these moments with the Rankin-Selberg problem reveals an interconnected web of mean-value theorems, where the error terms of modular Fourier coefficients are perfectly counterbalanced by the continuous spectrum of the zeta-function. As researchers push toward the sixth moment of the Riemann zeta-function and explore the quantum modularity of higher-rank groups, the mathematical tools synthesized in the 2025–2026 publications will undoubtedly serve as the foundational bedrock for the next generation of number theoretic breakthroughs.

**Sources:**
1. [uleth.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2Ocu8kUw3xm6UfNG2mpTj5qbFtmMj7vFt9B11OU3_ErntaPNz5-DZ1Ukbh3vtzNp4Qp3ECfU0vlyL5hwyfF7NnVGBroHkxLkv_5kShaP5apBOzKi2vPvlxo5DIdirR1AUdiMVomx8DKBTzvaoW8kseUcnwpf-)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHthk0lCUdOoSPEhV1aQMAE3s6oQ8DTozJDNz6Fyt0cj4Cie-ZlgX5lXnNLQpKEwUUcUAhqfCO5qqEG3VIQw_-mJWG7Kg13TH5irv3Hcqodmx2s6V4yQ==)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcNc7eymtx5BEQL2ympC2SgZixyqKcUbTOYd6HzJ_gSiKdEaSY6sQ-vNopTTSzq04mla-_jVApgz5bXDtZVqT7wuj6W_Mu0DMPeeQvVPDSyDvO3t18WU3OpVWSSoo10eJqujvEfOisLdegRyBYCkemZeBqtBqj2JEbPK92c3kTaHrD0Puoke7X8Vf9OrPdj3eeD-_gEp8X6J9cx2wg2XI7yjPUpVQVLQc914iTwz0Hjg==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdL7-1LyjPEQj_xpStlWvBujcjwPaAIq4Vi0xUDmQErABnle_bMciAOq_5uOr6iFg0I8ShPr_wO4EcqJ1ARh_EZdLfRGdQgnEsg2cocsf-m7bjk8Dlcg==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9_iOx3Z1H-paSi5FPV65Zw88cZ1oLa0OQB3w4h0ehmIc18hpN7ddvRNt9_2P1ViZLcD2yOVWsRZrogDZnQB72QYdGbKcKaLxopzneY6FnGR6DPp0dig==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEYDJQYy6M5cLu0RUeUa0ywYw6CC-0KcMyU044UurX-qriW9zmWJl_0mnNsVse9hYwJSwiGMN5bb0bBxSiDzlQfXhDOjI9-mSlwiq0UW9PopcNYy3kCA==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNSDYWjQtmx3h8Qbb5QircaPJRNQ_92BrsMpYDt5u5O0aa3ENrkr-sQ4-Nbxlh7ENfcdHRr79XsumSP3-DChYXPK2k1qaZSOJoiH2_OaDUXB2U9e3XIg==)
8. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8L5g31YGp077eFn8ybotsiHat8d1EovOdN4H2sjRIgym2J20VzCCUCjkJcAlKI-ayNGLhisoInE_jFL-H_-nzbvky0p99tG8yUJlvBfW6iisBd2_Xd92Qrxgwl9M7Bg==)
9. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKkW8foLUnhSdcYry6vdn74_KAXQ0i9ORzHvdXwm-JrnaRzKlMaJTsF-_4dSaiTAavYRB846_JtbTJ9YH63z0Jhm7BlIKYYgabbFEAmU7zRIfgyUH1_scHZsMQRqpVKxcxtWNFDmMVib6CukF43qBExt6dCrHFsKKnEz5Tpbq4GiQajZRwXy6IJOJk9s2aamx6h5CtcDxYDD4bXHFf94JqjTXct1POo9bJjXTWnMKgbelYkhYsoD91XUJSqD8PJVfUgYRo4H_smJEZ__fX3twUyRvLowvo8tMTGcUDV60yd9lPtJcNpA==)
10. [cnrs.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGb-ioE_SfirfxOrJ0hblTnd9M4B43iSxSnxzSmi0lvXShemvgGLrPtxgo3-3lN5RMNF4XUEUj2I0SryiZahgMSzwI8bwrQtMDt0N5n78x30Zrcm2U9XqHZgPOwkk6Zrr18W-pQSrScQw6npmCMOG6Gb5ph_QU=)
11. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6Wo4D5yU-gc413-UNMKTVGaHCycpyCMFY3TPwiqUeUOokYBr0iueis9gWZ6BsV8-1iqhuj14oTcG158kWi-G0kZGXe5VeGWPhd3zDBmX50qffUNHWobfqxscG_-xaacjGAOKUsueWlIlNiB2ouOFrrLx86IU0UkbcSjuN9z0GkLSudg1K96KNsL2JZAiUPuDzAVLAr8ZyLjPe9owf_caDTicyMuI5uhZUhVnZ84vwgb-ga4VOUU-rhsKgUhFu95Kca3SFqJJD_FwcOaT16zLcgjoCI2uPrIRg)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVXf_aoCmO7h8RYS6jxxVVNcpMYS0PjjlwIMu8QyLbHtxD4TS96kasHhlpPyDeKIf4u17r8c7CJN7GQJYJf852k-C4kpyGK8yXUnpBcfhAey9ZxlDHBg==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgKfWoXJFjLZhimXt8GFrB0ZY7seam2Zvja1irCVc3AgywyMDCZJMvEMAZdJat-kL2T-b-UDTix5fB11NCrzY8e5PK_5a8zlqleGDnpsvFva1L1FK5wg==)
14. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGot4UkwTzbc3FWDof6pNPbBVVMB6wdpoDkedxDTkrU7nOpP-vCCApsl3pHL2xynjvJp5_5COViyaVsWjG6fSXjkTjmJfCzCgYAS0igU_3WLJHeT7NI9h3OL74cdDze-hnpeYFUy6KezIpa)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3Xu5l4DwGLqLVj8VljVU8_gi4npmDMttqfJKCORKnwD14Tjn-JwZYXdFvE3-KJfZWHdoP4PV31jxeqSGG9leUeejJE9Pl_ISZ6IRJvr1LzxigWg-MbzcEN69FJX3_TKFYCn2N6-iKKgIVWyRCgD68BlYcvO3DrK7bZklwPoIsFSE6rmvwJJVXct4oz0QVVR_LVJiQB29AOVirfKfkQYYM4KtxfJTV1kK5JxMggjGkTr6p-PQ1uc0WyvYF51CQKYSAnP8SYlI=)
16. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlsoyQtddXC93aRe-8KPAb10emtfR7tklnN9MGdBmgUP-pAbKFkOgWZb4QBivMuS5B4PSJX0OJaaV2MrPWjCr43U1SrAmz5a67G5D-k5saQbC2O_UauNVZ-Wi1m2onLMa41XCxwMZOVHWv1ke3iA==)
17. [sciprofiles.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOcUTv8-jTPHWlCLf3JtPAXSTXmbEocLdNidXUrzksL47PdTBQDxNB4d-OCAMAzL4aoI6lNmiTn7qUXnAzuySjoSjNqBkNpM063-eDnQwi6ZIb08abClB2Jy9f2bo=)
18. [repec.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXDquGv4ljVhpjaOeuaxuepOlF_UAHnnv13gat4EJWmAtWiDn7ZwcZIdDj7Jk52yfO2rZJcTpvPhrAcamppLU1-CsqT7gq0reaFpyLwXq3mdV8Luin8RBMHwazhNwDTPLtO7L-XA6aHalien4S1dmqatOFSmcBAE5w)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJwhNjmaYXyLczJOw-AlpEx4zNmA9Bv97bban1mUpjsBcIpNg9n_oKSi7lkmLwhWStsBVqojNDKOANh6y3eOeacHcklPcoiEMeFJeCmqlnNrFuZ_mQD4TpoYOM4aEOet9ecvlN7KToCByLEpzyaP8U4w7ipTwII5Z_oESr7_bGr061OvfOjyxVImLuXuC64swQvedM6fliV2oe_SAGty-5vOgH9nk=)
20. [ethz.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaJh35tO-6QSJ4ZxbTsMX6hheRmQF0iBIYEER6LqFkYQd_0hb8wgzGXO3KQe5Kwu-6XYaYUyZzBYcPnqG9v7ccmA7D_gwyttPAFSNC-GrCQN0sd_2ESBnwgXiK5ICApM5dLiolPfoeR-K4LwMvMw==)
21. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5G5p5G40U9A5I7oJ4R0nZfXGEami4zAlpnAxIBBWZVFPHutiRaGHXgKO2WEerLWUu5CoQYZagxibwP9JJ_SWQLOKI2eG1G_wKux3JUXgfnfmfPuOuhU5xM6eWLGo5xPNCM8ekrP8=)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGts_hN6Qe7tRu13kZlErR_0q1W7XWEGhrd4HogDxMmOEFD5iSiWQdCyPD0Hr-C2iylhcVX57J62EKeKpRbXI7jxxY7Ex-Xf58uYNQEZxFKk4CTeHcEtQmwHqLZUQyxL5gxy0u5Kq9qFURWUpUcA0f7mK_LF8QRgP_-1cUnprN_OujVyelV1TGLduJsmgL5xHXSLPyKi_LUWWVpnoQw8WUcSul5YzbCBfwNI6ki)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeW-WfD8E8i6SwbIYKmzvgkNJAR4PR3VdDB5IKrSeJKD6ka36_jGj61muNOLL558CAFwMoA1ONwyU1TH5kPGUsqPdu45CdckPIzm4FYTU5a971NhABWKXCr2Cf-thbpilGaQ-JByuopuIpX2OAP2jLWydjnoF_RbhM7bGwBZ-TgNojGgm0s9Jf4pJpHVxuww0ISnNkEWtTYNB5Jl-G3_8=)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRc0Nk4jq9JGvH-QpdAYgWLmKgfUtamXqvANn38uQSgbFhXcQH-WbUPgpR8JexZ-baat6gP1uf8wlVnDTB6X5Fghcuft4sCC7ThBF5yPosCNwN5vKjAQ==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTbbkErTvvNxzHNp7QysGPKe_apyvQNZ6W_Tyxl3ipja-ldcrFHCREGpUHyfFmsrpQU1Dy3avoBW9zeYTR5Wtd295DBWZqDGvrtxg9SgzwOgLX-habQg==)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJpVlPvj2a81962T0SEr5hF_2_7vdTp6FYgrBkzHFyZquuwR2wD0DW5FCbUILX-Hxzv0jmfn3eCUeyri01ohPYSdG0j-6R3Uxl7F2EGRJV7SE2T2t2yuRXzLQpCUz-Ol3R_jzo27T6iNEqT0ylyTKPm_s8tr9NMx4fCzzMx4d-c68UZfwl3Q==)
27. [jhu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPuxR30B682UtxfEbUq6Sk5PFlqVor7JtYyEXV35YjQqd2ltXPpfLVMSp5B0ChtmKhz4qoByIVc-Ynv3gFjS2nL4ntalVmScoYdcLJwTaNF9Tsn_k9ew_jRQBc_MOfdek8_Lnx2tvpHHJiDUwt1kzf6El7Qa-RhVPLfqLxmyHPjGwokZbzmS701CnG)
28. [ntwebseminar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkAK72VpVmLf_f9JF0XVFYIeH3lgrHmcWPVItmNSRIMlx9vW-QRb4qr9G5916mdGY70ueW2ZDWW-K5udlVS-G4ZMdtixnau9w2bhD0UbkQ5Zw935lxGXvbqeRT16esF_zb)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAdYAeEos80SOERB7n_-DuPy6YMQWfxW57adUCBOVFVRUwFvAm-ylzd9IxsSx0HkTUOw7LOudqvnAMErCDCqoa5WRwO7uNO2CjF6jpjVOknWro_Wq6)
30. [unsw.edu.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFh-e6R9o2GVruOo4wgjpbMZ9J8hlC20Ra25c8lmJgl8Xl5EhYnXGTTLJbWIqaF8he6n6cKo_KNS88NXcROhOBroGWHKoUPcKqbGFXIdFtchRTHuhizwnPNLFs38gEIaRGVR1LxBMuE3ufcG3Qch80=)
31. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPM8lp39SjVDovYQdQzFG2vTDd7HMtTXsSMy1HPKLBTyHefaC4St3zgQ-2JSNAGqXZPILMy6UX9uOliDkTSfolqYyIf_FmuIjg6bzg9xR3eDPaSuesc0qmPc9qcIU5bRoCYMH7Nt7toeyPDnFJ0qGlPxFq8x99fYDBtuOzxlJaM0YW3JQfAe16uizyoj8X86Cs7t8w0sEA1Gl1n6OnKfrr)
32. [worldscientific.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHluScytOHRS3IYTOlJEYiyfGrQBmCkSYxnqpz31Yfow39UKoKS5GmPT2J7odEbZ6zpVqVpsfCMKhCKYl0Z-_2a-XCTxW6oC937fTC5KpVKCOX8hCoi_0M39P36Vmw_5s-dgAXiIfUL1lIrKLz1yDW10QvA)

