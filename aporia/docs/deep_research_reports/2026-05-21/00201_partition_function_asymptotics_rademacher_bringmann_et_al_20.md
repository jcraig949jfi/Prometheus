# Partition function asymptotics (Rademacher, Bringmann et al) 2024-2026

**Pythia queue id:** 201
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdGVVFQYW9lV0dOdVo5TW9QaEpuVXdBNBIXRlVRUGFvZVdHTnVaOU1vUGhKblV3QTQ
**Elapsed:** 251s
**Completed at:** 2026-05-21T17:46:58.006960+00:00

---

# Partition Function Asymptotics: Rademacher-Type Exact Formulas and Modular Innovations (2024-2026)

This leading section provides a synthesized overview of the recent advancements in partition function asymptotics, centering on the period from 2024 to 2026. The points below summarize the core developments in the field, followed by introductory context. 

*   **Key Points:**
    *   Research suggests that the classical Hardy-Ramanujan-Rademacher circle method can be rigorously extended to mixed mock modular forms, successfully yielding Rademacher-type exact formulas for complex combinatorial objects like partitions without sequences [cite: 1, 2].
    *   It seems likely that false-indefinite theta functions and mock Maass theta functions provide a robust framework for determining precision asymptotics and exponentially growing terms for partitions with parity restrictions [cite: 3, 4].
    *   The evidence leans toward the conclusion that the generating functions for moments of reciprocal sums of distinct partitions, while lacking standard modularity and Eulerian product expansions, exhibit profound connections to Maass Eisenstein series and sesquiharmonic Maass forms [cite: 5, 6].
    *   Recent mathematical methodologies indicate that Rademacher-type exact formulas are highly effective tools for establishing delicate combinatorial inequalities, such as log-concavity, higher-order Turán inequalities, and the positivity of higher-order finite differences for various restricted partition functions [cite: 7, 8].
    *   It appears that exact formulas for partition rank generating functions, originally approximated asymptotically, can be summed to infinity to produce convergent Rademacher-type series involving vector-valued Kloosterman sums [cite: 9, 10].

**Background and Historical Context**
The integer partition function, denoted \(p(n)\), represents the number of ways to write a positive integer \(n\) as a sum of positive integers, disregarding the order of the summands. Originating with Euler's formulation of its generating function as an infinite product, the study of \(p(n)\) experienced a paradigm shift in the early 20th century. Hardy and Ramanujan pioneered the "Circle Method" to derive an asymptotic formula for \(p(n)\) [cite: 11, 12]. Subsequently, Hans Rademacher refined this method, leveraging the modular properties of the Dedekind eta function to transform the asymptotic expansion into a remarkably exact, convergent infinite series involving modified Bessel functions and Kloosterman sums [cite: 6, 7]. 

**Recent Trends in Modular Forms and Combinatorics**
In recent decades, the intersection of analytic number theory and combinatorics has expanded far beyond classical modular forms. Ramanujan's enigmatic mock theta functions have been formalized as the holomorphic projections of harmonic Maass forms, thanks to the foundational work of Zwegers. Between 2024 and 2026, researchers, prominently Kathrin Bringmann and her collaborators (including Walter Bridges, William Craig, Caner Nazaroglu, Byungchan Kim, Eunmi Kim, and Koustav Banerjee), have aggressively pushed the boundaries of the Circle Method. They have adapted Rademacher's techniques to analyze mixed mock modular forms, false theta functions, and non-modular generating functions, achieving unprecedented precision in partition asymptotics [cite: 2, 4].

**Impact on Partition Theory**
These analytical breakthroughs have resolved long-standing conjectures regarding the combinatorial properties of partition sequences. By establishing Rademacher-type exact formulas with highly controlled error terms, mathematicians have been able to rigorously prove properties such as log-concavity for unimodal sequences, asymptotic behaviors of partitions separated by parity, and intricate statistical distributions of partition parts in arithmetic progressions [cite: 8, 13]. The period of 2024-2026 marks a renaissance in the analytical study of integer partitions, merging deep geometric and automorphic structures with discrete mathematics.

---

## 1. The Foundations of Partition Function Asymptotics

To fully appreciate the innovations of the 2024-2026 period, one must first understand the rigorous foundations of partition function asymptotics. The unrestricted partition function \(p(n)\) is a sequence that grows exponentially. Leibniz was among the first to note the sequence of partitions—referring to them as "divulsions"—observing that the integer 3 has three partitions, 4 has five partitions, and 5 has seven partitions [cite: 14]. 

The generating function for \(p(n)\) was famously established by Euler as an infinite product:
\[ P(q) := \sum_{n=0}^{\infty} p(n)q^n = \prod_{k=1}^{\infty} \frac{1}{1-q^k} = \frac{1}{(q;q)_{\infty}} \]
where \((a;q)_\infty\) denotes the standard \(q\)-Pochhammer symbol [cite: 2, 6]. 

Because \(P(q)\) has a natural boundary on the unit circle in the complex plane, extracting the coefficients \(p(n)\) analytically requires sophisticated contour integration near the roots of unity. Hardy and Ramanujan's seminal 1918 paper introduced the Circle Method to estimate these coefficients, producing the famous asymptotic approximation:
\[ p(n) \sim \frac{1}{4n\sqrt{3}} \exp\left(\pi \sqrt{\frac{2n}{3}}\right) \]
as \(n \to \infty\) [cite: 6, 11]. 

In 1937, Hans Rademacher revolutionized this approach. Rademacher exploited the transformation properties of the Dedekind eta function \(\eta(\tau)\), defined as \(\eta(\tau) = q^{1/24} \prod_{n\ge 1} (1-q^n)\) where \(q = e^{2\pi i \tau}\) [cite: 14]. By precisely bounding the minor arcs and summing the contributions of the major arcs (Farey fractions), Rademacher transformed Hardy and Ramanujan's asymptotic formula into an exact, convergent series for \(p(n)\):
\[ p(n) = \frac{2\pi}{(24n-1)^{3/4}} \sum_{k=1}^{\infty} \frac{A_k(n)}{k} I_{3/2}\left( \frac{\pi\sqrt{24n-1}}{6k} \right) \]
where \(I_{\nu}(x)\) denotes the modified Bessel function of the first kind of order \(\nu\), and \(A_k(n)\) represents a specific arithmetic sum known as a Kloosterman sum [cite: 6]. The Kloosterman sum is defined as:
\[ A_k(n) := \sum_{h \pmod k^*} \omega_{h,k} e^{-2\pi i n h / k} \]
where the sum runs over integers \(h\) coprime to \(k\), and \(\omega_{h,k}\) is a multiplier phase arising from the modular transformation of the Dedekind eta function, inherently related to Dedekind sums [cite: 6, 7].

Following Rademacher, Zuckerman generalized this exact formula to the Fourier coefficients of all weakly holomorphic modular forms of negative weight on finite index subgroups of \(SL_2(\mathbb{Z})\) [cite: 7, 11]. However, the generating functions of restricted partitions and specialized combinatorial objects frequently lack the standard modularity required by Rademacher's original proof. The years 2024-2026 have witnessed a concerted effort by Kathrin Bringmann and colleagues to extend these exact formulas to functions with anomalous or "mock" modular properties.

## 2. Mixed Mock Modular Forms and Partitions Without Sequences

A central milestone in the 2024-2026 literature is the derivation of a Rademacher-type exact formula for the number of partitions without sequences, accomplished by Walter Bridges and Kathrin Bringmann [cite: 1, 2]. A partition without sequences is a partition in which no parts form a sequence of consecutive integers. The generating function for these partitions, extensively studied by George Andrews, is known to be the product of a standard modular infinite product and Ramanujan's third-order mock theta function \(\chi(q)\) [cite: 15, 16].

### 2.1 The Challenge of Mixed Modularity
Mock theta functions, introduced by Ramanujan in his final letter to Hardy, are intrinsically non-modular. However, Zwegers established that mock theta functions are the holomorphic parts of harmonic Maass forms, meaning their transformation under the modular group produces an anomaly governed by a "Mordell-type integral" [cite: 16].

When a mock theta function is multiplied by a modular form, the resulting generating function is termed a *mixed mock modular form*. The generating function for partitions without sequences possesses an overall modular weight of 0 [cite: 2, 15]. Historically, exact formulas have primarily been restricted to weakly holomorphic modular forms or harmonic Maass forms of negative weight. The non-modularity of mock theta functions typically gets absorbed into the error terms of asymptotic expansions (as seen in earlier works by Dragonette and Andrews), but creating an *exact* formula for a mixed mock modular object requires entirely new analytical machinery [cite: 16].

### 2.2 The Modified Circle Method
To achieve an exact formula for partitions without sequences, Bridges and Bringmann deployed an extended version of the Hardy-Ramanujan-Rademacher Circle Method [cite: 2, 15]. The methodology necessitates splitting the contour integration over Ford circles and carefully isolating the main asymptotic terms from the anomalous Mordell integrals.

Crucially, the evaluation requires rewriting and bounding generalized Kloosterman sums. Because the generating function mixes modular and mock modular behaviors, the multipliers \(\omega_{h,k}\) interacting with the phases yield highly complex exponential sums. Bridges and Bringmann established robust bounds for these sums, showing that the Kloosterman sum \(A_k(n)\) for this mixed object satisfies:
\[ A_k(n) = O_{\epsilon}\left(k^{2/3 + \epsilon} \gcd(|n|, k)^{1/3}\right) \]
which is vital for ensuring the absolute convergence of the resulting Rademacher-type infinite series [cite: 2]. 

Furthermore, the Mordell-type integrals introduced by the non-holomorphic part of the harmonic Maass form were rigorously evaluated [cite: 15]. The error terms associated with these integrals were bounded by splitting the integration limits \(z = k(N^{-2} - i\Phi)\) across adjacent Farey fractions in the Farey sequence of order \(N\), where \(-\vartheta'_{h,k} \le \Phi \le \vartheta''_{h,k}\) [cite: 2, 16]. By letting \(N \to \infty\), Bridges and Bringmann successfully derived the first Rademacher-type exact formula for the Fourier coefficients of a mixed mock modular form [cite: 15, 17]. This formula closely resembles Rademacher's original 1937 formula, demonstrating that the non-modularity of the mock theta function \(\chi(q)\) does not fundamentally destroy the structure of the exact formula, provided the Mordell integrals are appropriately handled [cite: 16].

## 3. Partitions Separated by Parity and False-Indefinite Theta Functions

Another highly innovative vector of partition theory from 2024 focuses on "partitions separated by parity." Initially introduced by Andrews in connection with Ramanujan's mock theta functions, these partitions feature structural requirements where parts of different parities (odd and even) are separated by specific rules [cite: 18, 19]. Andrews investigated eight distinct families of partitions separated by parity, producing generating functions with a rich array of properties, including false modular forms and mock modular forms [cite: 18, 19].

### 3.1 Asymptotic Main Terms via Tauberian Theorems
In March 2024, Kathrin Bringmann, William Craig, and Caner Nazaroglu utilized Ingham's Tauberian theorem to extract the asymptotic main terms for each of the eight partition functions studied by Andrews [cite: 18, 19]. The rationale behind studying these partitions relies heavily on the \(q\)-hypergeometric series that count them, providing a combinatorial lens into the mock and false modular properties of the series [cite: 18, 20].

By applying Ingham's Tauberian theorem, Bringmann, Craig, and Nazaroglu successfully computed the main asymptotic behavior as \(n \to \infty\), finding terms of the form \(e^{C\sqrt{n}}\). The proofs required extending multi-dimensional Euler-Maclaurin summation formulas and evaluating limits of two-dimensional variables within specified domains \(D \subset \mathbb{C}^2\) of sufficient decay [cite: 18]. 

### 3.2 Precision Asymptotics and Mock Maass Theta Functions
While the Tauberian approach yielded the main terms, finding *precision asymptotics*—which include all exponentially growing terms—required far deeper modular techniques. In September 2024, the same team (Bringmann, Craig, Nazaroglu) published a framework dealing with precision asymptotics for partitions separated by parity by relating their generating functions to **false-indefinite theta functions** [cite: 3, 4].

A false-indefinite theta function operates on a Lorentzian lattice and resembles the well-known indefinite theta functions defined by Zwegers, but it features the insertion of extra sign factors, analogous to the relationship between classical theta functions and false theta functions [cite: 4]. 

Thanks to the works of Lewis-Zagier and Zwegers, there is a deep understanding of the relationship between \(q\)-hypergeometric series, real quadratic fields, and Maass forms [cite: 3, 4]. In particular, Zwegers built a framework for *mock Maass theta functions* in analogy with his earlier resolutions of Ramanujan's mock theta functions [cite: 3, 4]. Utilizing this framework, Bringmann, Craig, and Nazaroglu systematically distinguished the class of false-indefinite theta functions linked to Maass forms [cite: 3, 4]. 

By developing a generalized Circle Method adapted for these false-indefinite structures, the authors extracted detailed asymptotic expansions containing all exponentially growing terms for partitions separated by parity. Their work proved that Hardy-Ramanujan-Rademacher type exact formulas are achievable under the right conditions for these highly anomalous objects, paving the way for analyzing a vast ecosystem of combinatorics linked to real quadratic fields [cite: 3, 4].

## 4. Reciprocal Sums over Distinct Parts and Sesquiharmonic Forms

The landscape of partition asymptotics in 2024-2026 also encompasses moments of statistics defined *over* partitions. One of the most computationally and analytically demanding problems involves the reciprocal sums of partition parts. For a partition \(\lambda = (\lambda_1, \dots, \lambda_{\ell})\), the reciprocal sum is defined as \(\operatorname{srp}(\lambda) := \sum_{j=1}^{\ell} 1/\lambda_j\) [cite: 21]. To understand how this statistic behaves over the set of partitions into distinct parts (denoted \(D_n\)), researchers defined the moments \(s_k(n)\), which sum the \(k\)-th powers of reciprocals of parts across all partitions in \(D_n\) [cite: 21, 22].

### 4.1 Lack of Classical Modularity
In 2024, Kathrin Bringmann, Byungchan Kim, and Eunmi Kim undertook a massive study to improve the asymptotics for \(s_1(n)\) (the sum of reciprocals) and \(s_2(n)\) (the sum of squares of reciprocals) [cite: 6, 22]. Prior asymptotic investigations into these moments relied on Wright's Circle Method to find asymptotic means and variances [cite: 6]. However, achieving precise asymptotic expansions for \(s_1(n)\) and \(s_2(n)\) is significantly more complicated than standard partition statistics because their generating functions are *not* modular forms and do not possess standard Eulerian product expansions [cite: 6, 22]. 

Bringmann, Kim, and Kim bypassed these barriers by revealing hidden modular architectures. In their December 2024 preprint (later detailed in the *Journal of Combinatorial Theory, Series A*, 2026), they established that while the generating functions are non-modular, they are intricately linked to higher-order modular concepts [cite: 6, 23]. The team obtained detailed asymptotic expansions featuring logarithmic terms, showing that the expansion of \(s_1(n)\) contains dominant terms scaling like \(\log(3n)\) layered atop the exponential growth characteristic of distinct partitions [cite: 6].

### 4.2 Sesquiharmonic Maass Forms and Maass Eisenstein Series
In a follow-up April 2025 paper, Bringmann, B. Kim, and E. Kim formally determined the modularity properties of the generating function for \(s_k(n)\) [cite: 5, 21]. They proved that the generating functions for \(s_k(n)\) are fundamentally related to **Maass Eisenstein series** and **sesquiharmonic Maass forms** [cite: 5, 21]. 

A harmonic Maass form is annihilated by the hyperbolic Laplacian \(\Delta_k\). A sesquiharmonic Maass form \(f\), conversely, satisfies an equation where \(\Delta_k f\) is not zero, but maps to a harmonic Maass form, essentially requiring the application of the Laplacian twice (or a fractional/mixed derivative formulation). The authors demonstrated that the generating functions for the reciprocal moments correspond to higher-order derivatives of generating functions that exhibit this sesquiharmonic behavior [cite: 21]. This revelation is profound, as it maps purely combinatorial moments (reciprocals of parts) directly onto the spectral theory of Maass forms, expanding the applicability of automorphic form theory to non-product-based combinatorial generating functions [cite: 5, 21].

## 5. Log-Concavity and Higher-Order Turán Inequalities

A primary motivation for deriving exact formulas and highly precise asymptotic expansions with explicit error bounds is to resolve combinatorial inequalities. The sequence \(p(n)\) is known to be log-concave for \(n \ge 26\), meaning \(p(n)^2 - p(n-1)p(n+1) > 0\). This was proved independently by Nicolas and by DeSalvo and Pak, who relied heavily on the explicit error bounds formulated by D. H. Lehmer for Rademacher's exact series [cite: 8, 24]. The Hardy-Ramanujan asymptotic formula alone is insufficient to prove log-concavity because the inequalities require comparing terms whose differences are smaller than the asymptotic error [cite: 7].

Between 2024 and 2026, researchers leveraged new Rademacher-type exact formulas to prove log-concavity and higher-order Turán inequalities for restricted partition sequences.

### 5.1 Unimodal Sequences and Partitions Without Sequences
Walter Bridges and Kathrin Bringmann applied their Rademacher-type exact formulas to prove log-concavity for the coefficients of mixed false modular forms [cite: 8]. Specifically, they analyzed the number of **unimodal sequences** of size \(n\). Unimodal sequences increase to a peak and then decrease. Utilizing a recent exact formula for false theta functions (developed by Bringmann and Nazaroglu), Bridges established the log-concavity of unimodal sequences [cite: 8]. 

Similarly, for partitions without sequences (denoted \(p_2(n)\)), Bridges and Bringmann conjectured that the sequence is log-concave for \(n \ge 482\) and all even \(n \ge 2\) [cite: 16]. During the review of their 2024 paper, Lukas Mauth mathematically established this log-concavity utilizing the precise asymptotic expansions and explicit error bounds derived via the exact formula [cite: 15, 16]. 

### 5.2 Turán Inequalities and Colored Partitions
A sequence \(a_n\) satisfies the Turán inequality if \(a_n^2 - a_{n-1}a_{n+1} \ge 0\) (which is equivalent to log-concavity). Higher-order Turán inequalities and Laguerre inequalities trace deeper polynomial invariants. 

In May 2024, Gargi Mukherjee studied the \(24\)-colored partition function \(p_{24}(n)\), which represents the Fourier coefficients of the inverse of the modular discriminant function \(\Delta(\tau)\) [cite: 25]. By studying the asymptotic expansion of \(1/\Delta\) (a modular form of weight \(-12\)) using Rademacher-type formulas involving the \(I\)-Bessel function, Mukherjee proved that \(p_{24}(n)\) satisfies 2-log-concavity, the Turán inequality of order 3, and Laguerre inequalities of order \(m\) (for \(2 \le m \le 8\)) eventually [cite: 25]. This methodological paradigm allows Fourier coefficients of Dedekind-eta quotients to be sharply bounded.

### 5.3 The Combinatorial Approach: Koustav Banerjee's Contributions
While analytical methods involving Bessel functions and Kloosterman sums provide sweeping proofs of log-concavity, combinatorial approaches offer structural insights. Koustav Banerjee (a postdoctoral researcher at the University of Cologne under Bringmann in 2024-2026) deeply investigated these inequalities [cite: 14]. 

Banerjee analyzed the higher-order shifted differences of partition sequences. The backward difference operator \(\Delta(a(n)) = a(n) - a(n-1)\) and its iterates \(\Delta^r\) were conjectured by Good in 1977 to alternate in sign up to a certain \(n(r)\), and then remain strictly positive [cite: 24]. While Odlyzko proved Good's conjecture using the Hardy-Ramanujan-Rademacher series in 1988, Banerjee aimed to prove positivity through purely combinatorial means, explicitly constructing injective mappings between sets of partitions [cite: 24].

Banerjee's work successfully constructed a non-empty subset \(X_2^p(n,j)\) of integer partitions to establish combinatorial proofs of the positivity of the second shifted difference \(\Delta_j^2(p(n)) = p(n) - 2p(n-j) + p(n-2j) \ge 0\). He extended these techniques to overpartitions \(\overline{p}(n)\) (partitions where the first occurrence of a part can be overlined) [cite: 24]. Furthermore, Banerjee, along with Peter Paule, Cristian-Silviu Radu, and WenHuan Zeng, produced infinite families of inequalities for \(p(n)\) bounding ratios like \((1+C/n^2)p(n-1)p(n+1) < p(n)^2\), utilizing the full analytic force of Rademacher's explicit error bounds [cite: 26].

In 2026, Kilian Rausch, Koustav Banerjee, and Kathrin Bringmann also published a Rademacher exact-type formula for \(pod_2(n)\) (partitions where odd parts are distinct), generalizing the Zuckerman formula for specialized Dedekind eta-quotients and applying it to deduce congruences and log-concavity [cite: 15].

## 6. Exact Formulas for Partition Ranks

The concept of the "rank" of a partition was introduced by Freeman Dyson in 1944 to combinatorially explain Ramanujan's legendary partition congruences modulo 5 and 7 [cite: 9, 15]. The rank is defined as the largest part of the partition minus the number of its parts. 

The generating functions for partition ranks are intrinsically tied to Ramanujan's mock theta functions. For instance, the mock theta function \(f(q)\) corresponds to the partition rank modulo 2 [cite: 10]. While the Rademacher exact formula for \(p(n)\) was proven in 1937, finding an exact formula for the coefficients of the mock theta function \(f(q)\) took much longer, finally being established by Bringmann and Ono in 2006 using the theory of harmonic Maass forms [cite: 10].

In 2009, Bringmann used the Circle Method to prove an asymptotic formula for the Fourier coefficients of the generic rank generating functions [cite: 9]. However, the leap from an asymptotic formula to a fully convergent Rademacher-type exact series for these specific functions remained elusive. 

This barrier was broken in October 2024, as presented in a seminar by Qihang Sun (and linked to joint work with Bringmann). Sun proved that Bringmann's 2009 asymptotic formula, when summed up to infinity and applied to prime moduli, rigorously converges and transforms into a Rademacher-type exact formula [cite: 9, 10]. 

Crucially, this exact formula for ranks involves sums of **vector-valued Kloosterman sums** [cite: 10]. By establishing highly specific vanishing properties of these vector-valued Kloosterman sums, Sun and Bringmann provided a completely new, purely analytic proof of Dyson's rank conjectures modulo 5 and 7 [cite: 10]. This highlights a monumental achievement: closing the loop between Dyson's combinatorial ranks, Ramanujan's congruences, and the analytic continuous techniques of the Rademacher exact formula.

## 7. Generalizing the Infinite Product Asymptotics

In a broader context, integer partitions are a specific case of objects generated by infinite products of the form \( \prod (1-q^n)^{-a_n} \). When \(a_n = 1\), this counts integer partitions; when \(a_n\) takes other values, it can count irreducible representations of Lie algebras, colored partitions, or multi-dimensional partitions.

In January 2024, Walter Bridges, Benjamin Brindle, Kathrin Bringmann, and Johann Franke published profound results on asymptotic expansions for partitions generated by infinite products [cite: 27, 28]. Classical work by Meinardus (1954) provided an asymptotic expression for the coefficients \(c(n)\) generated by \( F(q) = \prod (1-q^n)^{-a_n} \), assuming the associated Dirichlet series \(L_f(s) = \sum a_n n^{-s}\) has a single simple pole on the positive real axis [cite: 28]. Recently, Debruyne and Tenenbaum generalized Meinardus's work for parts drawn from specific sets of integers.

Bringmann, Brindle, and Franke generalized this even further, creating asymptotic formulas for configurations where the set of parts is a multiset of integers, and most importantly, where the associated zeta function has **multiple poles** [cite: 28]. 

By defining the associated \(L\)-series as \(L_f(s) = \zeta(s-d)\), and verifying specific analytic continuation and growth conditions (e.g., \(L_f(s) = O(|t|^a)\) in vertical strips), the authors proved uniform asymptotic behavior for the coefficients [cite: 27]. This allowed them to derive precise asymptotic formulas for highly complex structures, such as the number of \(n\)-dimensional representations of the Lie groups \(SU(3)\) and \(SO(5)\), and partitions into \(k\)-gonal numbers [cite: 27]. 

Furthermore, the team established general criteria for the log-concavity of these specialized coefficients. They proved that for sequences generated by certain orbifolds and symmetric products, the coefficients \(N_{\ell}(n)\) are strictly log-concave for \(n\) sufficiently large [cite: 27]. They also connected this to generalized multiplicative inequalities, demonstrating that \(N_{\ell}(a) N_{\ell}(b) > N_{\ell}(a+b)\) for \(a,b \gg 1\), significantly expanding upon earlier 2016 theorems by Bessenrodt and Ono [cite: 27].

## 8. Partitions in Arithmetic Progressions and Related Statistics

Further diversifying the application of the Circle Method, Kathrin Bringmann and Caner Nazaroglu published research in September 2025 regarding the asymptotics of partition parts in arithmetic progressions [cite: 13, 29].

Improving upon previous literature, Bringmann and Nazaroglu used Wright's adaptation of the Circle Method to derive sharp asymptotic formulas for the number of parts in all partitions of an integer that fall into a given arithmetic progression [cite: 13]. They also derived exact asymptotic constants, proving formulas such as:
\[ \sigma_t^2(n) \sim \frac{(\pi^2 - 6)\sqrt{6n}}{2\pi^3} \]
for related partition statistics [cite: 13]. 

The authors also proved distributional results for combinatorial hook lengths. They demonstrated that the distribution of the number of hook lengths that are multiples of a fixed \(t \ge 4\) in partitions of \(n\) converges to a shifted Gamma distribution with parameter \(k = (t-1)/2\) and scale \(\theta = \sqrt{2/(t-1)}\) [cite: 13]. This links the purely additive theory of partitions with probabilistic distributions, governed by the analytic behavior of the underlying modular generating functions. Moreover, their study heavily involved finding modular completions for false theta functions, which enabled an efficient computation of their obstruction to modularity—a critical step in evaluating the exact error bounds required for their statistical distributions [cite: 13].

## 9. Conclusion

The timeline spanning 2024 to 2026 represents a watershed era in the analytic theory of integer partitions and modular forms. The pioneering work initiated by Hardy, Ramanujan, and Rademacher over a century ago has been vastly generalized to encompass the wild, anomalous ecosystems of mock modular forms, mixed mock modular forms, false-indefinite theta functions, and sesquiharmonic Maass forms. 

Led by researchers such as Kathrin Bringmann, Walter Bridges, William Craig, Caner Nazaroglu, Koustav Banerjee, Byungchan Kim, and Eunmi Kim, the classical Circle Method has been surgically upgraded. The derivation of Rademacher-type exact formulas for partitions without sequences [cite: 1, 2] and exact formulas for partition ranks [cite: 9, 10] proves that non-modularity does not preclude the existence of highly convergent, exact infinite series. Simultaneously, the resolution of precision asymptotics for partitions separated by parity [cite: 3, 4] and moments of reciprocal sums [cite: 5, 6] showcases the deep connectivity between discrete additive counting problems and the continuous spectral theory of automorphic forms.

Ultimately, these exact analytical formulas serve as the engine for solving discrete combinatorial inequalities. Log-concavity, higher-order Turán inequalities, and properties of shifted differences are no longer restricted to objects with simple Eulerian products; they can now be proven for highly restricted partitions, unimodal sequences, and multi-colored variants, pushing the boundary of both analytic number theory and enumerative combinatorics to unprecedented heights [cite: 8, 24, 25]. The robust frameworks constructed in 2024-2026 will undoubtedly serve as the foundation for the next generation of partition asymptotics.

**Sources:**
1. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwMYTNvhFa3YZ6ZXaT3oZ8drZw_xZ61PBZzmoDTymFJzS99_wqaMQVjZqUezSihdyXmc8PECYLM9gCFKC35TowI0jiGGgwhj2b3DtopQs2KrJ7UqJ8417_1BbFOWyjOZQrzrsfn6aJEd7lK_u45FY58XnPsSQr3g==)
2. [uni-koeln.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpe5vivqJQdr6La1f7FBdww2_FgZsceZ15HWUAB1OQOookVw0K9Q9YQO7i71NgpZptVwqXH4Vdr3KzSkilI_MucZKxXXDOgL2cCPQacTpiMtTq9Je8tqq0W8oUKYz3zMgvNWdSseHAqKXLRc8y1xhWlMPL5IzN44zf)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6pPrFxQgbZZM-T0EyQJ9xILsLx1upKc-QYzunDBwG8OtGUXW9XXpYTtVlqOYJ5xMWvOgfjo-7aKvxjQAQOrrnzMQZVPYHgz5DynrnRCJ2HW87T8LhRw==)
4. [uni-koeln.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHV39w9FvgEUgcU1vUp-QuwiHhdz7eVj4JxpK9IMwDaoHGEOe6jSPmGoi2XdfccgaEuQw-6NIrq6HPaqqfKmtldrLVefQYKhDKoLNhlgEoB86-P4-oswKKsVVLzhON3ni6_vXfch4FsHmgoK1pPRsXWUBm4lNZh_1BQYTHOx5I_iJz75coy)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHwz2-mWIV8DVuH56ZO3DhOTBcYYJaOr7QnlHmF6MXsQN3pnwhHnfxu-APBoTkwxwex4SMrQrpctm3YRzYzyU84xbphKQlFWeYKvaAXaGUChGJFy76nw==)
6. [uni-koeln.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2m4wo32mOvojW8-EQQvIMRQ5xrKsmZfMjcJev_-LJLxbB7CDQGJArSef8vz8rIE0TXZxkSJ8yYSt6Qcgzixq4OsdWn9g5KxdLEe_uwLCK-xh3RvxvRAgKTyLRDXSymcOCUvZYxJrPorMBXr_LSewU0B_Bon22SDE1CATfeO5TTlrF0SY_fYe3VWIlAbwDWMjDHRlTpagbsDDUgby9QNqydFP5UGlX4WmA8LkpPAH-748KFnan2PzgJZwAD4rJaxC5MEanqvYH3L7_hOk=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESZy9nJwRVv1WXghJqCv6wi_Sbid8jL2uSSYmKjuBZU4P5UOgO9sNeUSQQnx99nUhMnOBgrIzIatJXtqFiNaQXcJsDP88Sw01e4P6v5JNnYNDB5Ks2nQ==)
8. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDsgkwY7ur1c4coPhk8gkpBHQTT1300gsnVFUd0Lwc5B5tbGuU2FrOchIjH98b7oL3p8Jgvf-9M65PrYiGeZdRrpSxj7qiK0uWklcQvKbKVQdxyXPgnEnkYlZqVGg9xpagg6UXNwd0MQ==)
9. [crc326gaus.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECYLzEnS0CDJ6SFaWndWLLFdAfu7aQeFzb_8OhfPmmEwNIS4n10FRvL12nJUThqCykswJtLso3KZLKjzUBHTDyZB2zzO0ZJiYaFTQR62z5JOSY9n-fOeCJwgA=)
10. [mtu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwzkGKzocBe6olYsMi-wqVkpkpUPgOoDe02lseazBU_XPPHBHOLl5Bx9EO0VZfpRhLqiM9OATvYkh_bV7pza0tKimc3cbyio6yfMhMcFRwqXII7hdfelBkMOua60pmubpjH-j1MrWHmoh4-AWZLCv8)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE63CXwaSbImZYyoRr5aKY2QLub_sephWQi82Xakc7ljf0NpMptPULiY0eIBjJA4PH89F13E8bSTn8eWIV0kJMmUydR5yqf8UkKKAlK6HqNmwk_Ki0t6A==)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1I7M-jalBkrN5EoIkNFxVhZo0LSMa69Wg3HnsbUz8Z3ny8bndpuntBEFbwBf4Kydn3l5WUEWojhMge42HatPlrkanvnPBS7eSQ707tm2UKVGiSPdvLsS1j0OtYuFKN0YI9fKLt9KsjGwC02sCvlVahEsntMcBPyWWKrEFSBaqnosCFR84VA120wfBQqXLE2_qHGlBS4I3_A==)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8iAvw3WGsCQj3fReCyNxJLMrKNEuxbdIUr4KMN3_EYQDxyOQXKSz1RGol1ZOqkMgyQLxoQHHQnqjOLIaz9rfq9-8uCvIeN02qMuThQdgcgPvT5iMmE0EdojB8L-i1WGAhoxTHPQa8loPjG35EYpkdprI8iIwdapt-A-efATf381Vy5ReNbcdyX2QfSS_0Bbi8J0c7JwKka_6sNoXuhaAhc3M=)
14. [iiserkol.ac.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJUJreupGmh_99GXPs4bEDcJl911WABuPmgqVTZLz4B4BFagLZVMbuuuGcND0pzoDOrHdLVcM5g_x0jjO-cAAPgUxiBbYcoO0hG7boxEHoqvUyBWVHp6K9_TJu9o0uNK0wBz_rCJt68fKvQjYVDOkmvDWsGeKi)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrlb7I8JyrX6qqWqzePK1pVe_fZQcNZbgS31Jo_gYG9fnVdPz4g-yZMr4aHv8UhrNAXK7TN-oeyhOiAe2EE32EdKxknNHH23oevEf92Y5nodL8_BslpQaE5DXMzpC2iHWxgAEM6BMMo6R07xN2aK6cEOm8n7MfIhLzeYhNsNTaG34BliQZe-KlkIVMrGG3vLDTjWg=)
16. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHBvgsmd2rfJnf3-slwFdsxEQMd0BkR8BqZuF5qbzK1UWpkNXGdVgkfgluBH6IG1JdpE5p9dflvwC9Hb49Fp_ii5f1yWadukrg-uzqpdVgR3xFRw18T98Qm0BI29QUBe_JacV4qBN0b7TE8Bt_-pdJEFH7_qsic_00iMPhCuj8)
17. [jhu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDmOPcciTFvPNc7wDMEg29tL41RmRePJl7YK91VqXSLXyqA7ULu8cXfvldJEWNDvkU2tzqV1IR3WtU4l8ML-gFgf70fEc5IPVKI_r6BYwIhAtZgcuimimJiCKL7Xk46_jx)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFi3hCLgzY48zli9kdtTj0Gq0cFY9olE_7yHcjr2haAllxyY47xnIku3eRRdbrlPYG3l5oM1_mhIDNPMJYgp4PDEiVaF_FHXawX6lWvcImdhqwpyTWF6w==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE14AylY091aDWRom8PlF4OaFKMCw_Vr5DKYb3PaD-rDJSUPBG_TLgq5_4yBpRmIlHLGpLRzdU6KBDYsgXEU8E0jV6yrhtsnu5S71lTqRUNjPTx_nvWIQ==)
20. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_k56kzUi5RcMGKH8KQbwaHdTdFJq9xPsO3QTeG-PgZmp_I5BGqbw6XSnL5J2hHLfJHOlJBLlhZP6YIGqKPuhUkltyYrHy-hUD_MdHU7Kj_UUA4wrUnbIrQo9LEzFqD6g4w72kuqsLeKrmTHwWDmeRKolWPoGfPuqPX6ks6FbbjSrv3FI=)
21. [uni-koeln.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEUI3JFGTwjhlSsFaKWmYhrxxw20mX_cr2jbRHsqI-hQCIuOYnOe_LZe6SzSMA85p3MertXT7BZ4CVjMBAGjxD_bOgoPwkpvbYNov3EqFtr3O2hpRGoh7_YHwjPUM8ZSoncLLe_f1r_jtu4mHw79Sp8qC-ggTGYWHHC4Ymo65AEincsl6a)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHL9jHKPeHDKUoSenAZRBkkQac8ae_kkttESuQd264TeJzha59J9pNke2DXaInrZojVmGb1GSqHGMvS8O0zq38jXTaaaWtTj0Nq0k-W_CB8_HG02YOCFQ==)
23. [dblp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGpOxKsVCwoEpirlzhlP_F6BGMPjte8RUu0GdrXPz7F-BLYkYhvoxBkFtPyaBItyGHBoE9tmGcaHjfrCieHydDkpPjJyVAIFvTN5oW-8yV5s4=)
24. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8fd2O6GH_XHELlT5sc_uhCchfI6ns0QsL9iNYIADmhrZth1MftQRDXHNe1EDtXaR5vsXiyvXGBYRW0_sCDDVnGGuXFhx79_qX03dPmxRCdMoNEdrCT4QKMyCxz8Lz1deSjvC-TkylhjXn42tHkUso1HzGzelTe1AFEc3iB53SnCmvXus=)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPrq08xv3i2e6BI7JgmDnriymUq1IGtED145G8cCKnyr10uPI1oPGHvYtTIWxncLXT0PlariC0b5rE4DJ1H0sF4rLqnKDkizOH1xgleRfh_p9i0_OWnQ==)
26. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhUEu40xFUEMGzWOyd2Q04uQiaUVXjNEtXIf1ZW1CfQloGm4uoT9w5vK4VBWuPd3-JVzVdctSImV-6YOjWsa6u707ljLB15Kod7WEfhyxRkyTMNIk2iB47HVvTI0L0UwrVfnDuOdTvoA==)
27. [uni-koeln.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHT2H0FBnk7kJ_jgYK59BH3gl07wftkRFbBSgBlBiZlQe_M7nN7MczR8lwl5WmNbfzv3g__ieWfkEjDeFp2-NWbnslSBNVPmP78-gkIWUYqi9YwWpKj7NQWmg3SsEf8paKYjoVJsKvHkRyTZT8lZY5_raXHWT8ypXQuDsxDzwyn)
28. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFCDyjRlhaiR_x3QUV8yYwMSZox93TLdctFiK-xE1y1wUY66wowMfBSLmGrqvnTjk_HW6s3AahKQ8LTbL7E663D5U_rrQdLckbrU7W14vfQNMOcSfmOEPItGu3bCUbH6Fgv1sERCn_4g==)
29. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLrEqtQfMBT94AGTyTX41GNSWXQweEB1nai7VJfAB7yjai-m21kJI_oKMtghTvqp-Uh5B6T6MU_HvLWOLYx8tl4anAiWIMY5ZVR4MeoMjZuWTqEwDW49qBeJIIff4dMRsKIKDc6H6EvjspH-D5G8tdv1OZK_WXebBaRXPmP5iC-noRIENqwZbM8MRKigYUDkHAt1vVPpno__XwHJOmKLVhFjKVhBN0NYarB4JWxLakZVfPug2v3Q9oo0RzGAoYpVDE8mOn6wA=)

