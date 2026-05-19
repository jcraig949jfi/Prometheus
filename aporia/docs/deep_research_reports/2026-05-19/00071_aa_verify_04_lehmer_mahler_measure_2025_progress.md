# AA-VERIFY-04: Lehmer Mahler measure 2025 progress

**Pythia queue id:** 71
**Tier:** T1
**Priority:** 1
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdORE1NYW9tNkdfdWRfdU1QOHFIbHNBWRIXTkRNTWFvbTZHX3VkX3VNUDhxSGxzQVk
**Elapsed:** 305s
**Completed at:** 2026-05-19T09:59:02.185803+00:00

---

# Progress on Lehmer's Conjecture and the Mahler Measure (2024–2026): A Comprehensive Academic Report

### Leading Summary
*   **The Status of the 1.17628... Bound:** As of early 2026, extensive computational searches and theoretical investigations have *not* yielded any non-cyclotomic integer polynomial with a Mahler measure strictly between 1 and Lehmer's value of $M(L) \approx 1.176280818$. The Lehmer polynomial, $x^{10} + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1$, remains the absolute record holder for the smallest known Mahler measure greater than 1 [cite: 1, 2, 3, 4].
*   **Computational Breakthroughs:** While the absolute minimum has not been breached, significant algorithmic progress has been made. In 2025, El-Serafy and McKee established the computational completeness of small Mahler measures for polynomials of specific "shortness" (length 5 and 6) bounded by specific "house" parameters [cite: 5, 6]. They discovered one new "small" Mahler measure during these searches, though it does not unseat the Lehmer polynomial.
*   **Theoretical Advancements:** A wave of new theoretical lower bounds has emerged. Laishram and Prasad (2024-2025) derived novel bounds dependent on the least common multiple of the inertia degrees of primes in algebraic number fields [cite: 7, 8]. Concurrently, the study of Mahler measure has been successfully generalized to non-commutative quaternionic polynomials [cite: 9], and applied to bound the dynamical "Parry order" of Perron numbers [cite: 10, 11, 12].
*   **Unverified Claims and Interdisciplinary Physics Models:** The 2025–2026 period has seen the publication of highly unconventional preprints (e.g., Zelenka's "Irreducible Overhead Theorem") attempting to prove Lehmer's conjecture by framing the Mahler gap as a fundamental constraint of computational complexity and "arithmetic fluid dynamics" [cite: 13, 14]. Furthermore, purported topological disproofs of the conjecture have surfaced on preprint servers but have been met with intense skepticism by the mathematical community [cite: 15]. These remain unverified.

---

## 1. Introduction: The Foundations of Lehmer's Problem

### 1.1 The Mahler Measure
The Mahler measure is a fundamental construct in algebraic number theory, Diophantine geometry, and dynamical systems. For a non-zero univariate polynomial $P(x) \in \mathbb{C}[x]$ factored over the complex numbers as $P(x) = a_d \prod_{i=1}^d (x - \alpha_i)$, the Mahler measure $M(P)$ is defined via Jensen's formula as the geometric mean of $|P(z)|$ over the complex unit circle:
\[ \log M(P) = \int_0^1 \log |P(e^{2\pi i t})| dt \]
Algebraically, this evaluates to:
\[ M(P) = |a_d| \prod_{i=1}^d \max(1, |\alpha_i|) \]
The Mahler measure effectively penalizes the leading coefficient and any roots of the polynomial that reside strictly outside the unit circle ($|\alpha_i| > 1$) [cite: 1, 3, 6]. For algebraic numbers $\alpha$, the Mahler measure $M(\alpha)$ is naturally defined as the Mahler measure of its minimal polynomial over the integers, $P(x) \in \mathbb{Z}[x]$ [cite: 16, 17]. 

### 1.2 Kronecker's Theorem and Lehmer's Inquiry
A classical theorem by Leopold Kronecker demonstrates that if $P(x) \in \mathbb{Z}[x]$ is a monic, irreducible polynomial, then $M(P) = 1$ if and only if $P(x) = x$ or $P(x)$ is a cyclotomic polynomial (i.e., all of its roots are roots of unity) [cite: 3, 17, 18]. Consequently, for any non-cyclotomic irreducible polynomial in $\mathbb{Z}[x]$, it must hold that $M(P) > 1$.

In 1933, Derrick Henry Lehmer was investigating the ratio of terms in Pierce sequences (related to the resultant $\Delta_n(P)$ of polynomials) in search of large prime numbers [cite: 9, 18, 19]. He observed that the growth rate of these sequences was dictated by the Mahler measure. This led him to ask whether the Mahler measure of non-cyclotomic integer polynomials could be arbitrarily close to 1, or if there existed an absolute constant $\mu > 1$ such that $M(P) \ge \mu$ for all such polynomials [cite: 3, 18, 20]. 

In his empirical search, Lehmer discovered the degree-10 reciprocal polynomial:
\[ L(x) = x^{10} + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1 \]
This polynomial has eight roots on the unit circle, one root strictly inside, and exactly one root outside the unit circle—a Salem number $\lambda \approx 1.176280818...$ [cite: 1, 2]. Therefore, $M(L) = \lambda \approx 1.17628$. Over 90 years of subsequent computational searches have failed to produce an integer polynomial with a Mahler measure strictly between 1 and $M(L)$, leading to the strong form of Lehmer's Conjecture: $\mu = M(L)$ [cite: 3, 12, 21].

## 2. Theoretical Baselines and the 2024–2026 Landscape

### 2.1 Pre-2024 Asymptotic and Conditional Bounds
Before delving into the advancements of 2024-2026, it is vital to contextualize the theoretical floor. The first major milestone was achieved by C.J. Smyth in 1971, who proved that if a polynomial is *non-reciprocal* (i.e., $x^d P(x^{-1}) \neq \pm P(x)$), its Mahler measure is bounded strictly below by $\theta_0 \approx 1.324718$, the real root of $x^3 - x - 1$, which is the smallest Pisot-Vijayaraghavan number [cite: 2, 19, 21]. Because $\theta_0 > 1.17628$, any counterexample to Lehmer's conjecture must necessarily be a reciprocal polynomial [cite: 19, 21].

For general polynomials, the most profound unconditional lower bound remains Dobrowolski's 1979 asymptotic theorem [cite: 17, 18]. Dobrowolski proved that for a non-cyclotomic integer polynomial of degree $d$:
\[ M(P) > 1 + c \left( \frac{\log \log d}{\log d} \right)^3 \]
where $c$ is a positive constant [cite: 17, 18]. The explicit constant was later refined by Voutier in 1996 to $c = 1/4$ for all $d \ge 2$ [cite: 17, 20]. Modern explorations routinely leverage Dobrowolski's framework. For example, discussions in 2025 on analytic number theory platforms explicitly dissect the prime number theorem integration methodologies used in Dobrowolski's original bounding of prime summations $\sum (\log n)^2 (\log \log n)^2 < p < (2-\varepsilon)(\log n)^2 A(n)$ to derive the logarithmic height margins [cite: 22].

### 2.2 The 2024–2026 Resurgence
Between 2024 and 2026, research surrounding Lehmer's problem fractured into highly specialized sub-disciplines:
1.  **Algorithmic constraints:** Replacing simple degree bounds with metrics like "shortness" (number of non-zero coefficients) and "house" (maximum root modulus).
2.  **Arithmetic geometry:** Utilizing inertia degrees of primes and ramification indices in number fields to construct new algebraic lower bounds.
3.  **Non-commutative extensions:** Porting the Mahler measure to quaternionic and slice-regular environments.
4.  **Dynamical properties:** Utilizing Mahler measures to bound the behavior of Perron and Parry numbers in $\beta$-expansions.

---

## 3. Computational Searches and Algorithmic Completeness (2024–2026)

Extensive computational horsepower has been historically thrown at Lehmer's conjecture, with algorithms often employing Graeffe's root-squaring method, lattice reduction, or structured heuristic searches through cyclotomic multiples [cite: 23]. Between 2024 and 2026, a paradigm shift occurred from simply pushing degree limits (which Mossinghoff and others pushed to $d \ge 180$ in the early 2000s) to establishing *provable completeness* for restricted classes of polynomials.

### 3.1 The Parameters of "House" and "Shortness"
In 2025, Salma El-Serafy and James McKee published a landmark study in the *Canadian Mathematical Bulletin* titled "Small Mahler measures with bounds on the house and shortness" [cite: 5, 24]. To understand their breakthrough, two parameters must be defined:
*   **House ($\overline{\alpha}$):** The maximum modulus among all the Galois conjugates of an algebraic integer $\alpha$. For a polynomial, the house is the largest modulus of any of its roots [cite: 6].
*   **Shortness (Length):** The number of non-zero monomials in the polynomial representation. Length-5 means the polynomial has exactly 5 non-zero terms [cite: 5, 24].

El-Serafy and McKee noted that for all known polynomials with highly constrained Mahler measures, the minimal polynomial $P(x)$ frequently possesses a multiple with a very short length (often length 5 or 14) [cite: 24].

### 3.2 Finiteness and Completeness for Length-5 and Length-6
El-Serafy and McKee established a strict algorithmic finiteness theorem: For any $\varepsilon > 0$, the number of monic, reciprocal, length-5 integer polynomials with a house of at least $1 + \varepsilon$ is finite [cite: 5]. 

By rendering the search space finite, they were able to execute an exhaustive computational search. They successfully computed a **provably complete list** (without imposing any arbitrary degree bounds) of small Mahler measures for all length-5 polynomials possessing a house of at least 1.01 [cite: 5, 6]. Their algorithm discovered all 15 previously known "tiny" Mahler measures (defined historically as $M(P) < 1.25$) that possess shortness 5 [cite: 6]. The polynomial with the smallest house among this constrained set was $z^{24} + z^{13} - z^{12} + z^{11} + 1$, yielding a house of $\approx 1.08376$ [cite: 6].

For length-6 polynomials, the unrestricted finiteness statement collapses. However, El-Serafy and McKee rescued the finiteness property by introducing an upper bound on the Mahler measure itself [cite: 5, 6]. They proved that if a reciprocal length-6 polynomial is a cyclotomic multiple of an irreducible polynomial, and its Mahler measure is strictly less than the smallest Pisot number $\theta_0 \approx 1.32471$, then the number of such polynomials with a house $\ge 1 + \varepsilon$ remains finite [cite: 5, 6]. 

Using explicit Rouché estimates, they proved their list of small Mahler measures for shortness-6 is complete subject to the house being at least 1.17 [cite: 6]. They successfully pushed this completeness boundary down to a house of 1.01 by restricting the non-cyclotomic part's degree to 180 and the short polynomial's degree to 512 [cite: 6].

**Result regarding Lehmer's Bound:** During their opportunistic, heuristic searches for polynomials of even greater length, El-Serafy and McKee did indeed discover **one new small Mahler measure** [cite: 5]. However, this new value did not break the $1.17628...$ floor. Lehmer's degree-10 polynomial remains securely the minimal known configuration.

### 3.3 Algorithms for Salem Numbers
As a direct corollary of their length-6 Rouché estimates, El-Serafy and McKee formalized an algorithm capable of finding all Salem numbers within any given interval $[a, b]$ (where $1 < a \le b < \theta_0$) that can be represented as the Mahler measure of an integer polynomial of length at most 6 [cite: 5, 6]. They successfully utilized this algorithm to catalog all such Salem numbers in the critical interval $[1.17, 1.3]$ [cite: 6].

### 3.4 Genetic Algorithms on Elliptic Curves
Another parallel computational avenue documented in recent literature (notably in John Clark's thesis research) applied genetic algorithms to search for polynomials with minimal Mahler measures on various elliptic curves $E_{a,b}$ defined by the Weierstrass equation $y^2 = x^3 + ax + b$ [cite: 19]. 

Unlike the classical Lehmer search—which solely focuses on univariate polynomials over $\mathbb{Z}$—this adaptation sought polynomials with minimal measure evaluated over the coordinates of the curve. The genetic algorithm utilized variable mutation rates $\mu = \mu_0 - 0.1 + \frac{n-k}{n \alpha}$ to maintain population diversity [cite: 19]. The results yielded a striking departure from classical patterns: the polynomials achieving the minimal Mahler measure on these curves were frequently non-monic and non-reciprocal, predominantly appearing at degrees $\le 3$ [cite: 19].

---

## 4. New Theoretical Bounds in Algebraic Number Theory (2024–2025)

While algorithmic completeness maps the empirical territory, pure number-theoretic bounds have also advanced, primarily by linking the Mahler measure to the ramification and splitting behaviors of primes within algebraic extensions.

### 4.1 Inertia Degrees of Primes (Laishram and Prasad, 2024–2025)
In a major advancement published in the *Bulletin of the Australian Mathematical Society* in late 2024 (and continuing into 2025), Shanta Laishram and Gorekh Prasad established deep connections between the Mahler measure of an algebraic integer and the inertia degrees of primes [cite: 7, 8].

Historically, mathematicians like Mignotte had established conditional lower bounds based on ramification (e.g., if a rational prime $p < d \log d$ is unramified in $\mathbb{Q}(\alpha)$, then $M(\alpha) \ge 1.2$; specifically, if 2 is unramified for $d \ge 3$, $M(\alpha) \ge 1.2$) [cite: 7]. Laishram and Prasad generalized this drastically, removing conditions on the ramification index and formulating lower bounds strictly in terms of the **least common multiple of all inertia degrees** of primes [cite: 7].

Let $\alpha$ be a non-zero algebraic integer of degree $d > 2$ that is not a root of unity. Consider the prime ideal factorization in the ring of integers $\mathcal{O}_{\mathbb{Q}(\alpha)}$:
\[ 2\mathcal{O}_{\mathbb{Q}(\alpha)} = \mathcal{P}_1^{e_1} \mathcal{P}_2^{e_2} \cdots \mathcal{P}_r^{e_r} \]
where the residual (inertia) degree is given by $[\mathcal{O}_{\mathbb{Q}(\alpha)} / \mathcal{P}_i : \mathbb{Z}/2\mathbb{Z}] = f_i$ for all $i \in \{1, \dots, r\}$ [cite: 7]. Laishram and Prasad proved that if $f$ is the least common multiple of $(f_1, \dots, f_r)$, then:
\[ M(\alpha) \ge 
\begin{cases} 
2^{(f+1)/4(2f-1)} & \text{if } f \neq 6 \text{ and } f \neq f_i \text{ for all } i \\
2^{1/4(2f-1)} & \text{if } f = 6 \text{ or } f = f_i \text{ for some } i 
\end{cases}
\]
[cite: 7]. 

A spectacular consequence of their theorem occurs when $f_i = 1$ for all primes lying above 2. In this scenario, the Mahler measure is bounded as $M(\alpha) \ge 2^{1/4} \approx 1.1892$ [cite: 8]. Note that $2^{1/4} > 1.17628$; thus, for any algebraic integer that could hypothetically violate Lehmer's conjecture, the primes lying above 2 cannot all have an inertia degree of 1. 

They further extended this theorem to arbitrary base number fields $K$. Let $\mathcal{P}$ be a prime ideal of $\mathcal{O}_K$ lying above a rational odd prime $p$. If $\max_{1 \le i \le g}\{e_i\} \le p$, they demonstrated that the absolute logarithmic Weil height $h(\alpha) = \frac{\log M(\alpha)}{d}$ is bounded strictly away from zero by an effectively computable constant $c > 0$ depending only on $p$ and the degree $[K : \mathbb{Q}]$ [cite: 8].

### 4.2 Heights of Generators in Galois Extensions (Jenvrin, 2024)
Furthering the theoretical study of heights, Jonathan Jenvrin (2024) investigated the heights of generators of Galois extensions of $\mathbb{Q}$ possessing the alternating group $A_n$ as their Galois group [cite: 17]. By analyzing symmetric constructions and leveraging Dobrowolski's explicit bound derived by Voutier, Jenvrin proved that as $n \to \infty$, the logarithmic height $h(\alpha)$ of these specific generators tends to infinity [cite: 17]. This provided an $A_n$ analogue to previous results established by Amoroso for the symmetric group $S_n$ [cite: 17]. This work underscores how imposing specific Galois-theoretic structures forces the Mahler measure to grow rapidly, making "small" Mahler measures an impossibility in such domains.

---

## 5. Non-Commutative and Multivariate Generalizations

### 5.1 Quaternionic Mahler Measure (Wang and Zhang, 2024)
A highly innovative theoretical leap in 2024 was the formulation of the **Quaternionic Mahler Measure** by Weijia Wang and Hao Zhang [cite: 9]. Moving beyond the complex plane, Wang and Zhang defined the Mahler measure for non-commutative polynomials over the quaternions $\mathbb{H}$.

To do this, they considered the probability Haar measure $\mu$ on the unit sphere of quaternions $T_1(\mathbb{H})$. For a slice-regular polynomial (the quaternionic analog of a holomorphic function), they defined the quaternionic Mahler measure $m_H(P)$ [cite: 9]. 

Fascinatingly, they proved that for a monic real polynomial $P(x)$ of degree $n$, the quaternionic Mahler measure observes a trivial lower bound:
\[ m_H(P) \ge -\frac{1}{2} \lfloor \frac{n}{2} \rfloor \]
where the equality holds if and only if $P(x) = (x^2 + 1)^m$ (for $n=2m$) or $P(x) = x(x^2 + 1)^m$ (for $n=2m+1$) [cite: 9].

They also explored the analog of Lehmer's problem for these slice-regular polynomials. Using the $\star$-product of quaternionic monomials, they proved that the quaternionic Mahler measure of a polynomial $P$ is bounded below by the measure of its symmetric counterpart $P_s$, giving $m_H(P) \ge \frac{1}{2} m_H(P_s)$, with equality holding strictly when $P$ is a real polynomial [cite: 9]. This demonstrates that the rigid geometric penalties that enforce Lehmer's gap in $\mathbb{C}$ have deeply structured, albeit distinctly distinct, analogs in higher-dimensional non-commutative spaces.

### 5.2 Bounds Dependent on the Number of Monomials
In multivariable and sparse polynomial research, Shabnam Akhtari and Jeffrey D. Vaaler, alongside authors like François Brunault, established new lower bounds for the Mahler measure that scale dynamically with the number of monomials $k$ [cite: 25, 26]. It was demonstrated that for a Laurent polynomial in any number of variables formed by a sum of at most $k$ monomials, the Mahler measure satisfies a bound dependent on the height $h$ of the polynomial, specifically $\ge h/2^{k-2}$ [cite: 26]. 

### 5.3 Mahler's Problem and Turyn Polynomials (2024)
While Lehmer's problem asks for the *smallest* Mahler measure for integer polynomials, Mahler's Problem (often contextualized for Littlewood polynomials where coefficients are strictly $\pm 1$) asks for the *largest* possible normalized Mahler measure $M(f) / \|f\|_2$ [cite: 27]. In 2024, researchers established a new record value exceeding $0.951$ for this normalized measure by analyzing Turyn polynomials (cyclically shifted Fekete polynomials) [cite: 27]. Although theoretically adjacent to Lehmer's conjecture, this showcases that the boundary behaviors of polynomials on the unit circle remain a fertile ground for discovering extreme limit values in 2024 [cite: 27].

---

## 6. Dynamical Systems: The Parry Order (2026)

A completely novel application of Lehmer's polynomial and the Mahler measure emerged in early 2026 within the field of dynamical systems and $\beta$-expansions. Researchers including Hachem Hichri and Kevin G. Hare introduced a new metric known as the **Parry Order** [cite: 11, 28, 29].

### 6.1 Perron, Pisot, and Salem Numbers
In the theory of $\beta$-expansions, a real number $\beta > 1$ generates a dynamical system on the unit interval. A **Parry number** is a base $\beta$ for which the expansion of 1 is ultimately periodic [cite: 11]. Three famous classes of algebraic integers dominate this space:
1.  **Pisot-Vijayaraghavan numbers:** Algebraic integers $>1$ whose Galois conjugates all lie strictly inside the open unit disk [cite: 2, 11].
2.  **Salem numbers:** Algebraic integers $>1$ whose Galois conjugates lie within the closed unit disk, with at least one root exactly on the boundary (the unit circle) [cite: 2, 11]. The Lehmer number $1.17628...$ is the smallest known Salem number [cite: 2, 4].
3.  **Perron numbers:** Algebraic integers $>1$ that are strictly larger than the absolute values of all their other conjugates [cite: 11].

### 6.2 Defining the Parry Order
Hichri et al. defined the **Parry order**, denoted $Ord_P(\beta)$, as the largest integer $n$ for which the power $\beta^n$ remains a Parry number [cite: 11, 28]. They introduced a natural partition of the set of all Perron numbers, $\mathcal{P}$, into:
\[ \mathcal{P} = \left( \bigcup_{n \ge 0} \mathcal{H}_n \right) \cup \mathcal{H}_\infty \]
where $\mathcal{H}_n$ contains Perron numbers of Parry order $n$, and $\mathcal{H}_\infty$ consists of numbers with infinite Parry order [cite: 12, 28].

In a pivotal 2026 theorem, they proved that a Perron number possesses infinitely many Parry powers (i.e., resides in $\mathcal{H}_\infty$) **if and only if it is a Pisot or a Salem number** [cite: 10, 11, 12]. Therefore, for any Perron number that is *neither* Pisot nor Salem, $\beta^n$ can be a Parry number for only finitely many integers $n$ [cite: 10, 11]. 

### 6.3 Mahler Measure Bounding the Parry Order
Crucially, Hichri and Hare proved that if $Ord_P(\beta)$ is finite (which is the case for any generic Perron number outside the Pisot/Salem sets), the explicit upper bound on this order is strictly governed by the **Mahler measure of $\beta$** [cite: 10, 11, 12]. 

Specifically, they established that the cutoff point beyond which $\beta^n$ ceases to be a Parry number is mathematically tethered to the degree of the polynomial and its Mahler measure [cite: 10, 11]. Through computational searches targeting $\beta \in \mathcal{H}_1$ within sub-intervals of $[cite: 1, 22]$, they generated vast sets of non-Parry Perron numbers whose powers transition dynamically, further cementing the Mahler measure as a fundamental gauge of dynamical chaos versus periodicity [cite: 10, 12].

---

## 7. Geometric and Topological Implications 

The Mahler measure is not just an arithmetic artifact; it dictates the geometry of manifolds and the topology of knots.

### 7.1 Alexander Polynomials and Knots
Alexander polynomials of fibered links provide a direct translation between Lehmer's problem and topology. A polynomial $P(x)$ is the Alexander polynomial of a knot if and only if it is reciprocal and $P(1) = \pm 1$ [cite: 2, 21]. 

The Lehmer polynomial $L(x)$ actually manifests geometrically. $L(-x)$ is the exact Alexander polynomial for the $(-2, 3, 7)$-pretzel knot [cite: 2, 21]. Therefore, answering Lehmer's problem is entirely equivalent to determining whether the Mahler measure of the Alexander polynomial of a fibered link can be arbitrarily close to 1 [cite: 21]. The Mahler measure here acts as a proxy for the "hyperbolicity" of the link; it is bounded below by the homological dilatation of the monodromy. If the homological dilatation is $>1$, the link map is isotopic to a pseudo-Anosov homeomorphism [cite: 21]. Thus, Lehmer's gap directly posits a universal lower bound on the pseudo-Anosov dilatation for integer-coefficient geometric systems.

### 7.2 Fuglede-Kadison Determinants and $L^2$-Torsion
By 2024–2026, the generalized Lehmer's conjecture was intensely studied via Operator Algebras. The SPP 2026 "Geometry at Infinity" program investigated the relationship between Lehmer's conjecture and the Fuglede-Kadison determinant [cite: 30].

For a Laurent polynomial $P \in \mathbb{Z}[t, t^{-1}]$, interpreting the ring as the group ring of the infinite cyclic group $\mathbb{Z}$, the Mahler measure equates precisely to the Fuglede-Kadison determinant of the associated multiplication operator $r_P : \ell^2(\mathbb{Z}) \to \ell^2(\mathbb{Z})$ [cite: 30]. 

Lück proposed a geometric approach utilizing this determinant to define the $L^2$-torsion of hyperbolic 3-manifolds. Under specific conditions, the fundamental groups of small-volume hyperbolic 3-manifolds yield matrices over the integral group ring with remarkably small Fuglede-Kadison determinants [cite: 30]. Consequently, solving Lehmer's conjecture is mathematically equivalent to placing a definitive lower bound on the $L^2$-torsion of these manifolds, uniting number theory with geometric topology [cite: 30].

---

## 8. Unverified Proofs, Disproofs, and Fringe Preprints (2025–2026)

As with many famous unsolved problems, Lehmer's conjecture attracts highly speculative literature. In the 2025–2026 window, several preprints claimed to definitively prove or disprove the conjecture. While these documents exist in the academic corpus, they have not undergone rigorous peer review and are treated with high skepticism.

### 8.1 The "Irreducible Overhead Theorem" (Zelenka, 2025–2026)
A prolific series of preprints uploaded to Zenodo by David D. Zelenka in late 2025 and early 2026 argued that Lehmer's Conjecture is not merely a number-theoretic phenomenon, but a fundamental "structural impossibility" derived from the physics of computation [cite: 13].

Zelenka's framework, titled the **"Irreducible Overhead Theorem" (IOT)**, asserts that any computational process reversing an exponential operation incurs an irreducible overhead $\Omega > 0$ [cite: 13]. Utilizing Kolmogorov complexity, he argues that exponential computational cost cannot be conserved exactly across time and parallelism [cite: 14]. 

In his 2026 paper, *Lehmer’s Conjecture as Computational Necessity*, Zelenka bridges IOT with a concept he calls "Arithmetic Fluid Dynamics (AFD)" [cite: 13]. He posits the unit circle as a "shock front" in the complex plane, completely saturated by cyclotomic roots (via Kronecker's theorem) [cite: 13]. According to Zelenka, for a non-cyclotomic root to exist outside this circle, it requires a minimum "pressure" or information cost to distinguish it from the cyclotomic roots [cite: 13]. If the Mahler measure $M(\alpha)$ approached 1, the logarithmic cost $\log M(\alpha)$ would approach 0, violating the Kraft-McMillan inequality of information theory because the non-cyclotomic root could no longer be distinctly encoded [cite: 13]. Therefore, Zelenka concludes the Lehmer gap must exist, quantized by a constant $c > 1$ representing this irreducible code-length overhead [cite: 13].

While philosophically intriguing and interdisciplinary, Zelenka's translation of continuous complex geometry into discrete information-theoretic bounds relies on highly non-standard analogies ("arithmetic fluid", "shock structure on $\mathbb{N}$") that are not currently recognized by mainstream arithmetic geometry [cite: 13].

### 8.2 Purported Topological Disproofs
On the other side of the spectrum, a preprint circulated on arXiv in September 2025 (arXiv:2509.21402) boldly claimed a *disproof* of Lehmer's conjecture [cite: 15]. The author purportedly proved that the union of the set of Salem numbers and Pisot numbers forms a closed subset of $(1, +\infty)$. By establishing an explicit lower bound and resolving Boyd's conjecture regarding the topology of these sets, the author claimed Lehmer's conjecture was inherently contradicted [cite: 15].

However, reaction from the academic number theory community (including discussions on mathematical forums in October 2025) highlighted massive logical gaps in this preprint. Critics pointed out that proving topological closure properties of the Salem/Pisot sets does not inherently invalidate the existence of an absolute minimum measure $\mu > 1$ for all reciprocal polynomials [cite: 15]. The consensus remains that this preprint does not constitute a valid disproof.

---

## 9. Conclusion

Between 2024 and 2026, the mathematical community has mounted a sophisticated, multi-pronged attack on Lehmer's conjecture. While the legendary lower bound of $1.17628...$ established by D.H. Lehmer's degree-10 polynomial in 1933 has neither been broken nor strictly proven as the absolute minimum, the darkness surrounding it has been greatly illuminated.

Computational mathematics has evolved from brute-force searches to elegant, algorithmic completeness proofs. Thanks to the work of El-Serafy and McKee, we now possess provably complete lists of small Mahler measures for specific short polynomials, fundamentally proving that localized finiteness exists when bounded by the "house" of the polynomial [cite: 5, 6].

Simultaneously, the theoretical architecture supporting the Mahler measure has been expanded into higher-dimensional non-commutative algebras (quaternions) [cite: 9], tied to the fundamental inertia degrees of prime ideals [cite: 7], and deployed as a bounding mechanism for dynamical systems via the Parry order of Perron numbers [cite: 10, 11]. 

Lehmer's question continues to serve as a Rosetta Stone, connecting Diophantine arithmetic, knot theory, operator algebras, and dynamical systems. Until a polynomial with a measure less than $1.17628...$ is found, or an unconditional proof pushing the theoretical floor up to this exact limit is formalized, Lehmer's conjecture will remain one of the most vital, generative open problems in modern mathematics.

**Sources:**
1. [lolathompson.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3fUMWqWwzxxg49-c1Xbr-eRoFfhpR_K3fOYv0chuKzhphm2osYpilSrksfYQ9PWeUmhi_WJu73FBy-smz-ZkccP_CUh9GmLlsnry9jjooCa8zngtrkxHgz2SASRnbfZno3-uIFJEer0b8S0g_9Of0B3Fu2wQWdcBTDMh-Ie41-_lwfkc=)
2. [fsu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLgTz5Vsa1Ed5koQO4-cNKocbaSs22T31oc5YLjjA55yj9LmF9xUHsHOFHzNMaH4rsYiEfsv8hFo8YhvhGZvcLqoG5nsnGGRTk-OTcwaEcYDZBMzjMWFHT71FsgOGIcRju4YUFcznvV3Hm)
3. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGf5PP-QZYi_jjaLt1mgIIrzS_fL7fUGOa-ruXB7NwiPZ4qBpRY1oPncC-OplW5A4Zyo20XYerE11uefRh2KKXK_dutvdBTd_ffqe6yu43Kpb5Lfrp0nfkDruKIkl_fDFiU6D_NKg==)
4. [wolfram.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmaZWS9G1wVernnZkaL5Fghi4A_j_kPgniHYoU1xoMl-a_scdb602zqxT4JXPOYczCwV-PHBiAMBNxNSxM-_V7i0FcHyqSi93Pbdf1sDvaCul9D0Di-Gj3Cf2RDlmqcbv-LDHCsyRjK-Ku9X2OKV0Bwgc2)
5. [royalholloway.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGx_ac0EshJzhwE48U1H7hgkvUFu4i2N6qdtdfpSnLFh99aI1EvgyBkF4KJHA5XyVjcKw2fRzMoWNhT6Txl8WQ_XF8RSjkBpZLk-CtlyNABCuFxBcSK-0xmYWHxUcIxvXgkT4x0oNC2IXFV7tqQYu-Hjxw0OnYjqun3ghisRyytOp70fPCfyJFKnE00_dyPOWwachtMSHi7BF_HgGjLTy0cG8Zq)
6. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMPa9BTyMObksRdGTIyfc6h_rhHk4et8tpFVCPBULjpEq2WXBWQPy3wqA5cGY-8xk7KTsax8FajB4qeYndR-gxVE3l3fLtJYqKJXioUbgiUEte5hyLNDfljvSAcf7amP9TUzFiCLSiBK-VBruFXfoyInsuPEDDfUwPzh8nNxAMpo-WsHoDp6WpJO-6EwtxvKjKAC9fdCvSZunI_9CleVMErahs32DRlWEOtzjaJzuO75HGt-BIfLEGbozfiCvJSPqNXisLCCWge2mlk-7mOppOBXkWKL1N-wtkEg19X2IgBIsGESAzq8B82--i1ewlIWSpWC5D8M8=)
7. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPNgmgLPWQ90Bci8dMrKRgGxX4PcK9XP2B8RSQuVjNsZaISy6wH-UYiUeT9qHrsPmaBKewWFMifIdfSnnKhlE0CA_OeHvI-gj9n4h4yuZPuycIWsrNmX52DsojWYS-i_0BzA_vOyDT51gOs-VEqSB7bBnW6tW7b4kYGPBX3njBDXVluAIuo-Gtt_exls-oopJZfAnlKU05HC4WSemXd4WZa1VmuaeHpeIgUCkvnPVJMqnnF3dtvoE_UMBqrMASKBMrBxwKi9xHA8LjX7EReR0tsvtDauiyHUrQurRTI5RBUH8JRmodsgQ2oBmPVTb1f8HvevyLM3qI9Q==)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELJn7XjMO4gD-hsdtNVu8FXtTJnjfxm7BTC_5eivtrNj4JV_Xx9rnFPVk3PSn4OMeeUKD91YfQXN-zgszIC4NeinYUvWMDbyXwQns0JuLnj7Dtb6tjWGPgpZPdvnRh06DBJOqiQIiB0TWPZ_SlCAg-LJWtUkJNKQG8cbQmLhAQKIaK594Zu8Rp_ffplPQtwg5h21VQEHvoxVdxxdIXSAyZQ1QVHxJV4R0z)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFywxaW2Qjy-keD9WLMX0HdthN89JDn8Zqym6LfBdxL-VuqDhMRznT7-v-CEMBl2QdGu3qhUbN2Uh3aMkdbFpNYhpLItrsdIGYNcae2OOA8_86FBj-X)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDaDiycHJz0bZNaPSvk_fVVbRcJfLN3d1H85Iio__NtvxX9uHiu5boA22SBZr1nwOgjLzvn_4oebpnRcXzqf1e2SCODphbNlIc7G40YhZeKw0U-vZ1)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWLSKGgaUMSx0DTcZVt0RI2GCPvj6gBFuOC3JIzbxjsRPpUgH8JBfmnc2Hk5q3keuK2fgIdO5C31jDN1EyADrz5NtYsQ3fDFN93mcPfyoSlYZ7XoH-T11accUd4HAkiM14CM1KH8A6s9MPTiTmRrHOq-upU4y0YPnzwt5OcZMU21K3jRA=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEM-HFqccnXFg8Yjtyuv2XB1KFJwlOBGOI6CPecvE5xn9xMCKE0xmzye7S3APBzaeA0UyCRuTQhZRyrnTvQ3wfXyUQN1cjwa9tTcYy9OdRKht3bRlUyRw==)
13. [zenodo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSZ6kSs11_vLNFGnaiwWul5SvZhTp6x8Q1BaR_ZyNHIy7uURmurG9jjeOX-06eTLhg-nwqWpjUfNPWMbLgH38kIwLD601Mlsj6kR0qMqUfJcNlZ_nb6-bLy8_wRkc4DIq3lmYxrFh5cSWoWvg_2tShheyic41qdNe-AZzSR1fi2k9J7Stvy8YnWEo6HjPfig==)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHI4C5gtzxVGWRj2EYA9ETacnvCw1BnoKMgUiKIm1p4upkZaYTcyMZ_PM7hwKExnZH2PSmxX32iK_PbH7_K-2TKjDHDCNbBe282pg3Y1ZzfRORXtaXa7GLCcf-kHpo99mYLYFt8Ln9ke9nij1pZ8Y8WAM5RmtK0mx2aemR4MfxOtK15jtYlc-iLnadbOXVMbBth5FZ0eewPKYXiaPC29A_Ai5BZR3psFPMtyUcjryJH8cwNev-cEnxF2lrSIR_ytfb5pEhYlhXlAPxv5LfHmdGBGso_LMm3p554CzhZqeTgyQtI5wbGNu5PE8bdljkI6aSoBPGWay-gZg==)
15. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGLAspXQTe7_7cEISuTPDAF0_alwvFZw1bLrXRwL363uR1zPqFm7QK2EiltsexC1jaOpdLDktCyhDyaLtak_bdP_v1a3I6lRI6mIZPmViIRoojimkhVPQH-aokFxl7b_iWwtFU_kF3KYhc-GOnAJUIwKHxB15ouWVlcO-tPJeUxTvIDwRH)
16. [discreteanalysisjournal.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGahAJmsVozTO8WacDcmVHpKc9P3pFWR8-xZ0fIhEh9yWduQQlwfiyr_QcJj9E6UrlX59KQar1cHXrbKZdj-y5gKJqLtM2CZlAD9RVBIcTvpBQubftKU8dBrJAy3xlsgdgfVhmU3veHjqz6jR2AVpgP33xgaDqyCs0yQLOIQ4WwFEHwIH1TW1TeazIhvVLcOnj-c1NBaQg19b3zm5I=)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE68pLHWgyGz65CLd8OXGOHFCU3N3crXDpyBl21vGFuHN8BzxBOeCKC3_aqiblxP7G_Tu_AxQd_Ur3kCyfl1MjXm8afQh-JXjXJnFfbi6mPStwaVIg-)
18. [uni-goettingen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtwygOvCsKh5JLtpzoii-E167oYUnipbeXTskkP-vP6nxK70Tsqxpe4O_d5eozkLozZfFvW2iZziujOcZwi1dinMQPjTdqu2pgzfJMIh46B8jgrK7-P1wCY1J2iaX345nTgmYPviKBUonzukSo4Cf6uX-Lkfu8_qceK8uDHSAPo7T01O8U6QPTIUPC6pFVjYLyzYElFyMoJFo4zLQAejvs9_T3lto=)
19. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjKQqwlH6hG10vWrmB-d3U4_SuddDfvlbyKftrY1ZWsBmzx3yyDhzHocAsGbaJgSKlO881FMlPQ_kEVWUGrLWuSTepPO2hmxS9GAAcdbM7IXTQS8FzjrFy7Y7Q6AtKOiIy50KsQRGSE_5bgoGHv1glQR0=)
20. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvCbXoXM1WxG3V2A_luslVrAYjE_Zg9pmWa_RBuVZg66BoD24CVLE7bhKF0-BfDJp9Dan8UqrNrLrDjzsRrREfDo8tHMllEdJCQUkOhU8QQ3mWBLffVtGWxUshjE1UZNPTZjvnQjgx4A==)
21. [fsu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsxlRCmVY5YS8wLpT0r7H09UbA-9GQgfEiTPOcGgb-fDplaYeFGEsRcImV-WWmlq_5aCTC5Gx_94V1OYAXPVEx8ZVdCY3qnwHv8Xhqv5xlVqmISfS_FBO4cnnQQcTufAiqi4BhwW0lEERf)
22. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3SWlucYUL0zPZi9L1BNFhpGOTmFIRKLz_5-ZMDaHa4tl_JLAacbtM6D6a_1jw6kcHO-YYxzZGJnrMJjX4S0-WO24SFPx_I3tjaX7UBwjHJeMMFLrzC3UQDJWtTQ1MCTnCTqtb27py8XJ1N5p2SMrDawNaWS7O62ITwUXAsLW9MZYqKA==)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyz-eaorz4rbw36rGEwiNjCe2oX6WajrKotMMYM4NnojFLgyrF0Tg1t9CUEU2BK6UKu9YHFiN2Wf8KbryLqIdEuvRljL0Fs4C3ps1AlS6O2H4m8D1i4fMGwC8fWpWOF8-iWv22EoYKAFZk2D4J-toYzgZAZkHeK8M1GELBUfC0XW5G_IHC9z3BWrbN6JFxMeH3yzk=)
24. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJpI2bE5oLxeX8Fo8zqT3vgroSG6rl7BXwJApYem5AseJLY1vUNkSWDOMlX0dZBR1cV9MNEaN16le31_DxI-Di252rZWxdcxi9W4ola_PBnZLyla3jxtmCCB8m5JfMguJuk5Qk7dmvXaAx_aAN8KsEgcMbXe-Ku3z_wLXzrDBm3j3cpn2fj97AwTtf11uv6yugBL2_iB_AIwt_Pr4apbtUdp210FWPSJWSvVBGHBQAOv9OPpAZV-uzRxDWpUjlwP57vc_WFuK4uk9XJLgJnog5py7J176la1MTAJzi0LfeC3XB)
25. [worldscientific.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzDU3-kEzB0PQZlwToe48w8dvEiOl5v5SBS7duaDdSz2NRjTK7khiLS0jy1e9y7lmNVWLkp0vNeXnLqF9kmfF_sJaFxyG37i5MsfddJlwlwuiuYdaZyNzyUoslRyfQgyvx8y1QUdtE1KfpYjwdYkmz1gYwUIeA)
26. [worldscientific.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpSan8qkuMa6RasbEJNBBbt6SzFzP9Y5StVigBkqROxdfTEvaZ7LAs5e1QxJC68Ozcw7ltdFfJDjH_CiyhgS4QICWih3FwyI_VnbxGPDXRMwiTH1P7XYseXlXZqbj52apHxbA9TgsI3nGonUEa7FoQV2tZ_vyl)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhT7QVRpi7K62V6M5TV9-N5R0YwYYtABKNdpitVOGLNArsaJn3Nfnv5ct7o6tjvyXNJaqq2cb8saUPcjA9127_kmABhbqBvloIwR1qKwmVgBlUdlI_)
28. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKqjHvJrtlV1adnqY4Bp_YWocqvbh-jq4mcfqIArSb2MVMGnqINVYBl7dDWCkAcBbq5bjxsrxUIP-HpYhgdhXm0dg9p3q66RxpQlbqPJYk4zx5nIUtHkJ64X-zGR7Sl2mWCoYmaSRHJVNtwRaz-IABRZVnwG9aL2ev2WlFhep2yElmtta-DOOWDrmFCH8U7g==)
29. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhtzSIS2K-01ToDxBM5_plo9pPRryAYQqVVEUxL8HlKIYrgqR0a8-5FlDNPnRc1KFitm5PPolXqRXeDvm7B6WBdWpPuTTQq9T5bx67SYD_2O2rFa9hsAXqna7eBCO1n_w-DspF4EDH)
30. [spp2026.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOQ7ooAHSI4MVMDvB6CFKRiuQKhGYZfPN1xeOP-U6F2nnweGOaehrlvnUMGA0bmMXuNqljgZQqTHC1F-rnDA7_FwJuTyaGa8hN-fFIi1IFxisFM9fAPyMJ5Vkeg0ejMRuNB_nlrWz6ecTgvcwzRpDtCCKvjGDZWMjpVnqlX3cOfE67m5s=)

