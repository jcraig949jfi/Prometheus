# Low-lying zeros of Dirichlet L-functions (Katz-Sarnak conjectures)

**Pythia queue id:** 134
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdDQ3NQYXRXUkpvbWNfdU1QOTV2TWlBcxIXQ0NzUGF0V1JKb21jX3VNUDk1dk1pQXM
**Elapsed:** 311s
**Completed at:** 2026-05-21T16:01:04.622519+00:00

---

# The Katz-Sarnak Density Conjecture and the Low-Lying Zeros of Dirichlet L-Functions

### Key Points
*   **The Katz-Sarnak Philosophy**: Research suggests that the statistical distribution of the zeros of families of $L$-functions near the central point (low-lying zeros) can be accurately modeled by the behavior of eigenvalues near 1 of random matrices from classical compact groups (Unitary, Symplectic, Orthogonal) [cite: 1, 2].
*   **Families of Dirichlet L-functions**: The family of all Dirichlet $L$-functions modulo a prime $P$ is widely believed to exhibit **Unitary** symmetry, while the sub-family of quadratic Dirichlet $L$-functions exhibits **Symplectic** symmetry [cite: 2, 3].
*   **The 1-Level Density Statistic**: The primary mathematical tool used to test these conjectures is the 1-level density, which sums a test function over the scaled low-lying zeros of the $L$-functions. Analytical limits on the Fourier transform of this test function (the "support") dictate the strength of the evidence [cite: 4].
*   **Breaking the Support Barrier**: A significant breakthrough by Drappeau, Pratt, and Radziwiłł unconditionally extended the admissible support for the family of primitive Dirichlet characters beyond the "trivial range" of $(-2, 2)$ to $(-2 - 50/1093, 2 + 50/1093)$, a feat that previously seemed to require unproven assumptions like the Generalized Riemann Hypothesis (GRH) or Montgomery's conjecture [cite: 5].
*   **Applications to Non-Vanishing**: By extending this support, mathematicians can unconditionally prove that a strictly positive proportion (greater than 50%) of Dirichlet $L$-functions do not vanish at the central point, providing strong evidence for Chowla's conjecture [cite: 5, 6]. 

### A Layman's Summary
The distribution of prime numbers has long been studied using complex mathematical tools called $L$-functions, the most famous of which is the Riemann Zeta function. The zeros of these functions hold the secrets to how primes are spaced. The Katz-Sarnak conjecture is a profound idea connecting these abstract mathematical functions to quantum physics and random matrix theory. It proposes that if you look at a large "family" of related $L$-functions and zoom in on their zeros closest to a specific central point, these zeros arrange themselves with the exact same statistical spacing as the energy levels of heavy nuclei or the eigenvalues of random matrices.

Testing this conjecture involves evaluating a statistic called the "1-level density." For decades, mathematicians could only prove that the 1-level density matched the random matrix predictions within a restricted mathematical window (called the "diagonal range" or "trivial range"). Expanding this window is notoriously difficult and usually requires assuming massive unproven theories like the Generalized Riemann Hypothesis. Recently, however, researchers successfully pushed past this barrier for Dirichlet $L$-functions without relying on unproven theories. This extension is not just a technical victory; it directly proves that a large percentage of these $L$-functions do not equal zero at their central point, answering long-standing fundamental questions in number theory. 

---

## 1. Introduction to Dirichlet L-Functions and the Riemann Hypothesis

To understand the profound implications of the Katz-Sarnak density conjecture, it is necessary to first establish the foundational architecture of Dirichlet $L$-functions. These objects are natural generalizations of the Riemann zeta function, designed specifically to capture the arithmetic of prime numbers in arithmetic progressions.

### 1.1 Dirichlet Characters and L-Series
A Dirichlet character $\chi$ modulo an integer $q \geq 1$ is a completely multiplicative arithmetic function $\chi: \mathbb{Z} \to \mathbb{C}$ that is periodic with period $q$ (meaning $\chi(n+q) = \chi(n)$) and satisfies $\chi(n) = 0$ if the greatest common divisor $(n, q) > 1$. The character is said to be *primitive* if it cannot be induced by a character of a smaller modulus dividing $q$.

For a complex variable $s = \sigma + it$, the Dirichlet $L$-function associated with a character $\chi$ is defined in the half-plane $\sigma > 1$ by the absolutely convergent Dirichlet series:
\[ L(s, \chi) = \sum_{n=1}^\infty \frac{\chi(n)}{n^s} \]
Because $\chi$ is completely multiplicative, $L(s, \chi)$ can also be expressed as an Euler product over prime numbers $p$:
\[ L(s, \chi) = \prod_p \left( 1 - \frac{\chi(p)}{p^s} \right)^{-1} \]
This dual representation—as a sum over integers and a product over primes—is the cornerstone of their utility in analytic number theory [cite: 3, 7].

### 1.2 The Functional Equation and the Critical Strip
Like the Riemann zeta function, a primitive Dirichlet $L$-function $L(s, \chi)$ modulo $q > 1$ can be analytically continued to an entire function on the whole complex plane. It satisfies a functional equation relating its value at $s$ to its value at $1-s$. 

Let $\mathfrak{a} = 0$ if $\chi(-1) = 1$ (an even character) and $\mathfrak{a} = 1$ if $\chi(-1) = -1$ (an odd character). We define the completed $L$-function as:
\[ \Lambda(s, \chi) = \left( \frac{q}{\pi} \right)^{(s+\mathfrak{a})/2} \Gamma\left( \frac{s+\mathfrak{a}}{2} \right) L(s, \chi) \]
where $\Gamma$ is the Gamma function. The functional equation is then:
\[ \Lambda(s, \chi) = \frac{\tau(\chi)}{i^{\mathfrak{a}} \sqrt{q}} \Lambda(1-s, \overline{\chi}) \]
Here, $\tau(\chi) = \sum_{a=1}^q \chi(a) e^{2\pi i a/q}$ is the Gauss sum, and $|\tau(\chi)| = \sqrt{q}$.

The zeros of $L(s, \chi)$ at the poles of the Gamma function are called the *trivial zeros*. The remaining zeros, called the *non-trivial zeros*, are constrained to the critical strip $0 \leq \sigma \leq 1$. The Generalized Riemann Hypothesis (GRH) asserts that all non-trivial zeros of $L(s, \chi)$ lie exactly on the critical line $\sigma = 1/2$. Let a generic zero be denoted by $\rho_\chi = 1/2 + i\gamma_\chi$. The distribution of the imaginary parts $\gamma_\chi$ dictates the fine distribution of primes in arithmetic progressions.

## 2. The Random Matrix Theory Connection

The bridge between analytic number theory and random matrix theory (RMT) was famously built in the early 1970s. Following a conversation with physicist Freeman Dyson, mathematician Hugh Montgomery observed that the pair correlation of the zeros of the Riemann zeta function exactly matched the pair correlation of the eigenvalues of large random Hermitian matrices drawn from the Gaussian Unitary Ensemble (GUE) [cite: 6, 8].

### 2.1 The Montgomery-Odlyzko Law
Montgomery's conjecture states that, properly normalized, the spacings between consecutive zeros of the Riemann zeta function on the critical line mirror the spacing of eigenvalues of GUE matrices [cite: 6]. Andrew Odlyzko later provided overwhelming numerical evidence for this conjecture by computing the locations of billions of zeros at massive heights on the critical line, confirming an astonishing visual and statistical match [cite: 7, 8]. 

However, Montgomery and Odlyzko were analyzing the zeros of a *single* $L$-function high up on the critical line ($t \to \infty$). A different, yet equally profound, phenomenon occurs when one looks at $t = 0$ (the central point $s = 1/2$) not for a single function, but across a *family* of $L$-functions.

### 2.2 The Katz-Sarnak Philosophy
In 1999, Nicholas Katz and Peter Sarnak expanded the GUE paradigm to formulate a massive overarching philosophy [cite: 1, 9]. They conjectured that the statistical distribution of the "low-lying zeros" (the zeros closest to the central point $s = 1/2$) of a natural family $\mathcal{F}$ of $L$-functions, ordered by their analytic conductor $c_f \to \infty$, is governed by the scaling limit of the eigenvalues near 1 of matrices from a specific classical compact group $G(\mathcal{F})$ [cite: 10, 11].

Katz and Sarnak proved these conjectures rigorously for $L$-functions over function fields (finite fields $\mathbb{F}_q(t)$) utilizing Pierre Deligne's profound work on the Weil conjectures and equidistribution theorems [cite: 12]. In the function field setting, to each family of $L$-functions there is associated a geometric monodromy group, which is typically one of the classical compact groups [cite: 12, 13]. 

For $L$-functions over number fields (such as $\mathbb{Q}$), the existence of a corresponding overarching geometric theory (like motives) remains conjectural. Thus, the Katz-Sarnak density conjecture for number fields posits a deep universality: the arithmetic of a family of $L$-functions dictates a "symmetry type" which manifests in the zero distributions exactly matching Random Matrix Theory.

## 3. Symmetry Types and Kernel Functions

According to the Katz-Sarnak conjecture, a family of $L$-functions will fall into one of a few categories of symmetry, corresponding to classical compact groups [cite: 2, 7]:
1.  **Unitary $U(N)$**: Typically associated with families lacking a self-dual functional equation or families that are complex-valued, such as the family of all Dirichlet $L$-functions modulo $q$ [cite: 2, 3].
2.  **Symplectic $USp(2N)$**: Typically associated with families where the sign of the functional equation is mostly $+1$ and there is a specific arithmetic structure, such as quadratic Dirichlet characters or $L$-functions of elliptic curves [cite: 1, 2].
3.  **Orthogonal $O(N)$**: Associated with families of holomorphic cusp forms or Maass forms. This splits into $SO(\text{even})$ and $SO(\text{odd})$ depending on the sign of the functional equation [cite: 1, 10].

To quantify these distributions, mathematicians define the **1-level density** scaling limits. If $W_G(x)$ is the 1-level density of eigenvalues near 1 of a random matrix ensemble $G$, its Fourier transform $\widehat{W}_G(u) = \int_{-\infty}^\infty W_G(x) e^{-2\pi i u x} dx$ represents the density in the dual (Fourier) space. 

| Symmetry Group $G$ | Kernel Function $W_G(x)$ | Fourier Transform $\widehat{W}_G(u)$ |
| :--- | :--- | :--- |
| **Unitary** ($U$) | $1$ | $\delta_0(u)$ |
| **Symplectic** ($Sp$) | $1 - \frac{\sin(2\pi x)}{2\pi x}$ | $\delta_0(u) - \frac{1}{2} I_{[-1, 1]}(u)$ |
| **Orthogonal** ($O$) | $1 + \frac{1}{2}\delta_0(x)$ | $\delta_0(u) + \frac{1}{2}$ |
| **SO(even)** | $1 + \frac{\sin(2\pi x)}{2\pi x}$ | $\delta_0(u) + \frac{1}{2} I_{[-1, 1]}(u)$ |
| **SO(odd)** | $1 - \frac{\sin(2\pi x)}{2\pi x} + \delta_0(x)$ | $\delta_0(u) - \frac{1}{2} I_{[-1, 1]}(u) + 1$ |

*(Note: $\delta_0$ is the Dirac delta distribution, and $I_{[-1, 1]}$ is the indicator function of the interval $[-1, 1]$).*

## 4. The 1-Level Density Statistic

The primary mechanism to test the Katz-Sarnak conjecture for number fields is the 1-level density. 

### 4.1 Definition
Let $\phi$ be an even Schwartz test function whose Fourier transform $\widehat{\phi}(u) = \int_{-\infty}^\infty \phi(x) e^{-2\pi i x u} dx$ has compact support. 
For a single $L$-function $L(s, f)$ in a family $\mathcal{F}$ with analytic conductor $c_f$, the 1-level density of its low-lying zeros is defined as:
\[ D_1(f; \phi) = \sum_{\gamma_f} \phi\left( \frac{\gamma_f \log c_f}{2\pi} \right) \]
where the sum runs over the non-trivial zeros $\rho_f = 1/2 + i\gamma_f$ [cite: 2, 9].

Because the zeros of a single $L$-function are difficult to study in isolation, one averages this statistic over the family $\mathcal{F}(Q)$ of $L$-functions with conductor $c_f \approx Q$:
\[ D_1(\mathcal{F}(Q); \phi) = \frac{1}{|\mathcal{F}(Q)|} \sum_{f \in \mathcal{F}(Q)} D_1(f; \phi) \]
The **Katz-Sarnak Density Conjecture** asserts that, as $Q \to \infty$:
\[ \lim_{Q \to \infty} D_1(\mathcal{F}(Q); \phi) = \int_{-\infty}^\infty \phi(x) W_{G(\mathcal{F})}(x) dx = \int_{-\infty}^\infty \widehat{\phi}(u) \widehat{W}_{G(\mathcal{F})}(u) du \]
where $G(\mathcal{F})$ is the symmetry group assigned to the family [cite: 9, 14].

### 4.2 The Role of the Fourier Transform's Support
The constraint that $\widehat{\phi}$ has compact support is not merely a technical artifact; it is deeply tied to the mathematical tools available (specifically, the trace formulas and the uncertainty principle) [cite: 15]. 

If $\text{supp}(\widehat{\phi}) \subset (-\alpha, \alpha)$, the value $\alpha$ determines how sharply $\phi(x)$ can be localized near the central point $x=0$. By the uncertainty principle, the narrower the support of $\widehat{\phi}$, the more spread out $\phi$ must be, meaning it captures zeros higher up the critical line, diluting the focus on the "low-lying" zeros [cite: 15]. 

To distinguish between the different Orthogonal symmetry types (O, SO(even), SO(odd)), one requires a support strictly larger than $\alpha = 1$. For Unitary and Symplectic families, achieving a support $\alpha > 1$ or $\alpha > 2$ is necessary to deduce strong arithmetic consequences, such as non-vanishing at the central point [cite: 10, 11].

## 5. Methodology: The Explicit Formula

The proof of any 1-level density theorem relies fundamentally on the **Explicit Formula**, a generalization of Bernhard Riemann's original formula relating the zeros of the zeta function to the prime numbers [cite: 11, 16].

For a primitive Dirichlet character $\chi$ modulo $q$, the explicit formula evaluates the sum of the test function over the zeros of $L(s, \chi)$:
\[ \sum_{\gamma_\chi} \phi\left( \frac{\gamma_\chi \log Q}{2\pi} \right) = \widehat{\phi}(0) - \frac{2}{\log Q} \sum_{n=1}^\infty \frac{\Lambda(n)}{\sqrt{n}} \text{Re}\left( \chi(n) \right) \widehat{\phi}\left( \frac{\log n}{\log Q} \right) + O\left( \frac{1}{\log Q} \right) \]
where $\Lambda(n)$ is the von Mangoldt function (equal to $\log p$ if $n=p^k$, and $0$ otherwise), and $Q$ is a scaling parameter related to the conductor [cite: 11].

When averaging this explicit formula over the family of characters, the calculation splits into two primary components:
1.  **The Diagonal Term**: Arises from the primes $n = p$.
2.  **The Off-Diagonal Term (or Prime Squares)**: Arises from $n = p^2, p^3, \dots$.

### 5.1 Averaging Over the Family
Consider the family of all primitive Dirichlet characters modulo $q$. Using the orthogonality of characters:
\[ \frac{1}{\phi(q)} \sum_{\chi \pmod q} \chi(n) = \begin{cases} 1 & \text{if } n \equiv 1 \pmod q \\ 0 & \text{otherwise} \end{cases} \]
When the sum over characters is passed inside the sum over integers $n$ in the explicit formula, the main contribution comes from integers $n \equiv 1 \pmod q$ (and $n \equiv -1 \pmod q$ due to the real part) [cite: 17].

Because $\widehat{\phi}$ is supported in $(-\alpha, \alpha)$, the sum over $n$ is restricted to $n \leq Q^\alpha$.
If $\alpha < 1$, the only integers $n \leq Q^\alpha$ that satisfy $n \equiv \pm 1 \pmod q$ are $n=1$. The sum over primes essentially evaluates to zero trivially, leaving only the Fourier transform of the test function at zero, matching the Unitary prediction exactly [cite: 11].

If we stretch to $\alpha = 2$ by incorporating the family of *all* primitive characters with conductor up to $Q$, the characters' orthogonality provides cancellations for primes up to $Q^2$. The interval $(-2, 2)$ is known as the "trivial range" or the "diagonal range" [cite: 5, 6]. 

## 6. Breaking the Support Barrier: Extending Beyond the Trivial Range

Extending the support of $\widehat{\phi}$ beyond the trivial range $(-2, 2)$ for the unitary family of Dirichlet characters, or beyond $(-1, 1)$ for the symplectic family of quadratic characters, is considered one of the holy grails of analytic number theory [cite: 5]. 

When $n > Q^2$, the condition $n \equiv 1 \pmod q$ implies $n = k q + 1$ where $k \geq 1$. This injects heavily off-diagonal terms that fluctuate wildly. Bounding these terms requires understanding the deep structural distribution of primes in arithmetic progressions beyond the reach of the Generalized Riemann Hypothesis [cite: 5, 6]. 

### 6.1 The Benchmark of Iwaniec, Luo, and Sarnak
For families of holomorphic cusp forms (which have Orthogonal symmetry), the benchmark was set by Iwaniec, Luo, and Sarnak (ILS) in 2000. Using the Petersson trace formula, they proved the density conjecture conditionally (under GRH) up to $\alpha = 2$ [cite: 6, 17]. Under a further deep unproven hypothesis regarding the signs of Kloosterman sums, they achieved a support of $(-22/9, 22/9)$ [cite: 17].

### 6.2 The Breakthrough by Drappeau, Pratt, and Radziwiłł
In a monumental 2023 paper published in *Algebra & Number Theory*, mathematicians Sary Drappeau, Kyle Pratt, and Maksym Radziwiłł achieved the first unconditional extension of the support past the trivial range for a family of $L$-functions [cite: 6, 18]. 

They studied the family of all primitive Dirichlet characters of conductor $q \in [Q/2, Q]$. They unconditionally established the Katz-Sarnak unitary prediction for test functions whose Fourier transform is supported in:
\[ \text{supp}(\widehat{\phi}) \subset \left( -2 - \frac{50}{1093}, 2 + \frac{50}{1093} \right) \]
[cite: 3, 5].

**Techniques Used**:
To surpass the trivial range unconditionally, Drappeau, Pratt, and Radziwiłł avoided assuming conjectures like Montgomery's conjecture about primes in arithmetic progressions. Instead, they relied on:
1.  **Linnik's Dispersion Method**: A highly sophisticated technique to average error terms in the distribution of primes across multiple moduli [cite: 5, 6].
2.  **Deshouillers-Iwaniec Bounds**: They leveraged profound bounds on cancellations in sums of Kloosterman sums, originally developed by Deshouillers and Iwaniec in 1982 [cite: 5, 6]. By writing the remainder terms of prime distributions as bilinear forms and applying the spectral theory of automorphic forms (Kuznetsov formula), they could demonstrate massive cancellation in the off-diagonal error terms.

This result represents the first unconditional realization of the Katz-Sarnak density conjecture beyond the diagonal range, a feat previously thought practically impossible without GRH [cite: 5, 19].

### 6.3 Further Extensions under GRH
While Drappeau, Pratt, and Radziwiłł's work is celebrated for being unconditional, assuming GRH allows mathematicians to push the boundaries even further. Recent works studying the $\Gamma_1(q)$ $L$-functions (a large unitary family of $GL(2)$ $L$-functions) have conditionally extended the support of the test function up to $(-8/3, 8/3)$ under GRH [cite: 17]. This highlights an emerging understanding that the arithmetic structure of the $L$-functions (e.g., being attached to $GL(2)$ versus $GL(1)$) dictates the structural mechanisms that enable support extensions [cite: 17].

## 7. Symmetry Types in Specific Families of Dirichlet L-Functions

The Katz-Sarnak conjecture classifies families based on their underlying arithmetic geometry. Within the domain of Dirichlet characters, there are multiple distinct families.

### 7.1 The Family of All Dirichlet Characters (Unitary)
As established, the family of all primitive Dirichlet characters modulo $q$ as $q \to \infty$ exhibits **Unitary** symmetry. The 1-level density converges to $\int \phi(x) 1 \, dx = \widehat{\phi}(0)$ [cite: 3, 11]. The non-trivial zeros repel each other, but they do not experience an artificial "repulsion" from the central point $s = 1/2$ beyond the standard unitary matrix behavior.

### 7.2 The Family of Quadratic Dirichlet Characters (Symplectic)
A primitive quadratic Dirichlet character $\chi$ takes values in $\{-1, 0, 1\}$. The family of quadratic Dirichlet $L$-functions $L(s, \chi_d)$, where $d$ varies over fundamental discriminants, is widely studied due to its relation to the class numbers of quadratic fields [cite: 1]. 

This family exhibits **Symplectic** symmetry. The density of zeros near the central point is modeled by the eigenvalues of matrices in $USp(2N)$ [cite: 1, 13]. The 1-level density incorporates the kernel $1 - \frac{\sin(2\pi x)}{2\pi x}$. The presence of this term indicates a strong repulsion of the zeros away from the central point $s=1/2$. Because $\widehat{W}_{Sp}(u) = \delta_0(u) - \frac{1}{2} I_{[-1, 1]}(u)$, the mathematical difficulty peaks exactly at $\alpha = 1$. Extending the support beyond $(-1, 1)$ for quadratic characters is notoriously difficult because Poisson summation yields dual characters and Gauss sums that do not easily average to zero [cite: 20].

### 7.3 Cubic and Higher-Order Characters
Cubic Dirichlet characters introduce fascinating complexities. For instance, the family of primitive cubic Dirichlet characters defined over the Eisenstein field $\mathbb{Q}(\omega)$ (where $\omega = e^{2\pi i / 3}$) has been shown to satisfy the Katz-Sarnak conjecture with **Unitary** symmetry for test functions supported in $(-1, 1)$ under GRH [cite: 20]. 
Extending the support for cubic characters requires averaging over cubic Gauss sums, an operation fraught with technical difficulties far surpassing the quadratic case [cite: 20].

## 8. Non-Vanishing at the Central Point

One of the most powerful applications of the 1-level density of low-lying zeros is determining the proportion of $L$-functions in a family that do not vanish at the central point $L(1/2, f) \neq 0$ [cite: 21, 22].

### 8.1 Chowla's Conjecture and Analytic Rank
Chowla conjectured that $L(1/2, \chi) \neq 0$ for all Dirichlet characters $\chi$ [cite: 11]. Understanding central vanishing is crucial. For elliptic curves, the Birch and Swinnerton-Dyer conjecture equates the analytic rank (the order of vanishing of the $L$-function at the central point) to the algebraic rank (the number of independent points of infinite order on the curve) [cite: 9, 22]. Iwaniec and Sarnak demonstrated that proving a non-vanishing proportion strictly greater than 50% for certain families of $L$-functions would unconditionally eliminate the existence of Landau-Siegel zeros, one of the greatest open problems in analytic number theory [cite: 22].

### 8.2 Using the 1-Level Density to Prove Non-Vanishing
Let $p_0$ be the proportion of $L$-functions in a family for which $L(1/2, \chi) = 0$. By evaluating the 1-level density for a non-negative test function $\phi$ with $\phi(0) > 0$, one can bound $p_0$ [cite: 11].
If a zero exists exactly at the central point, $\gamma_f = 0$, it contributes exactly $\phi(0)$ to the 1-level density sum $D_1(f; \phi)$. Thus, the average contribution of central zeros is at least $p_0 \phi(0)$.
Since $D_1(\mathcal{F}; \phi)$ converges to $\int \phi(x) W_G(x) dx$, one obtains the inequality:
\[ p_0 \leq \frac{1}{\phi(0)} \int_{-\infty}^\infty \phi(x) W_G(x) dx \]
By optimizing the test function $\phi$ subject to the constraint that its Fourier transform is compactly supported in $(-\alpha, \alpha)$, mathematicians can establish upper bounds on $p_0$, which in turn gives a lower bound on the non-vanishing proportion $1 - p_0$ [cite: 11].

### 8.3 The Race for Proportions Greater Than 50%
For the Unitary family of Dirichlet characters, if the support is strictly bounded to the trivial range $\alpha = 2$, the optimized test function yields a non-vanishing proportion of exactly $50\%$ ($0.5$). To break the $50\%$ barrier, one *must* extend the support $\alpha > 2$ [cite: 23].

*   **Kyle Pratt's 0.50073**: In an initial preprint, Kyle Pratt claimed an unconditional non-vanishing proportion of $0.50073$ using a highly complex mollifier method combining three distinct mollifier pieces [cite: 5, 24]. However, an error was discovered in this work which nullified the portion exceeding 50% [cite: 23]. 
*   **Drappeau, Pratt, and Radziwiłł's Breakthrough**: Building upon the insights of Deshouillers-Iwaniec Kloosterman bounds, the joint work by Drappeau, Pratt, and Radziwiłł correctly extended the support for the 1-level density, achieving an unconditional non-vanishing proportion of at least $0.51118$ (or exactly $\frac{1}{2} + \frac{25}{2236} - \varepsilon$) [cite: 5].
*   **Conditional Results on $GL(2)$ Families**: Most recently, assuming GRH, the extension of the support to $(-8/3, 8/3)$ for the unitary family of $\Gamma_1(q)$ $L$-functions has yielded a record non-vanishing proportion of $62.5\%$ [cite: 17].

These achievements validate the Katz-Sarnak philosophy's practical utility in extracting arithmetic data that is otherwise entirely invisible to standard analytic methods.

## 9. Lower-Order Terms and The Ratios Conjecture

While Random Matrix Theory is universally successful in predicting the main (asymptotic) term of the zero distribution across different $L$-function families, the *universality* breaks down when examining the lower-order terms [cite: 16, 25]. 

The main terms of the 1-level density depend only on the symmetry group (Unitary, Symplectic, Orthogonal), meaning they are completely blind to the specific arithmetic of the $L$-functions being studied. However, at finite levels (for $L$-functions of finite conductor $Q$), there are significant deviations from the random matrix models [cite: 16, 25].

### 9.1 The L-Functions Ratios Conjecture
To predict these delicate lower-order arithmetic terms, Brian Conrey, David Farmer, and Martin Zirnbauer formulated the **L-functions Ratios Conjecture** [cite: 16, 26]. This conjecture provides an extraordinarily powerful, though heuristic, recipe to predict the averages over a family of ratios of products of shifted $L$-functions:
\[ \sum_{f \in \mathcal{F}} \frac{L(1/2 + \alpha, f) L(1/2 + \beta, f)}{L(1/2 + \gamma, f) L(1/2 + \delta, f)} \]
By differentiating these ratios, one can extract the exact density of the low-lying zeros [cite: 16].

### 9.2 Arithmetic Factors in the Lower-Order Terms
Steven J. Miller and collaborators rigorously computed the 1-level density for the symplectic family of quadratic Dirichlet characters arising from even fundamental discriminants up to $X$ [cite: 16]. They demonstrated that the main term perfectly matched the Katz-Sarnak prediction. More importantly, they calculated the lower-order terms down to the scale of $O(X^{-1/2+\varepsilon})$ unconditionally for restricted support [cite: 4, 16].

The calculation of these lower-order terms revealed the presence of specific arithmetic factors—such as products over primes involving the Legendre symbol and the properties of the discriminants—that break the universality. The Ratios Conjecture perfectly predicts these terms, providing deep heuristic validation that the arithmetic of the specific family governs the rate at which the statistics converge to the Random Matrix limit [cite: 16, 25].

## 10. Generalizations and New Phenomena

As the field expands, mathematicians are discovering scenarios where the strict universality of the Katz-Sarnak conjecture undergoes subtle shifts or requires new perspectives.

### 10.1 Weighted One-Level Densities
Alessandro Fazzari, along with researchers like Sugiyama, introduced the concept of the **weighted one-level density** [cite: 27, 28]. Instead of averaging the zeros uniformly, the sum is weighted by the central values of the $L$-functions themselves:
\[ \sum_{f \in \mathcal{F}} |L(1/2, f)|^k D_1(f; \phi) \]
Fazzari's conjecture suggests that for families of $L$-functions whose standard symmetry type is Unitary, Symplectic, or Orthogonal, the *weighted* one-level density matches the density of eigenvalues of random matrices weighted by their characteristic polynomials [cite: 7, 28].
Intriguingly, Sugiyama observed that in a family of symmetric square $L$-functions attached to Hilbert modular forms, the symmetry type effectively *changes* from Symplectic to an entirely new density function not directly modeled by the standard unweighted Katz-Sarnak conjecture [cite: 7, 27]. 

### 10.2 Higher-Level Densities and Centered Moments
The $n$-level density extends the 1-level density to study $n$-tuples of zeros simultaneously. Let $\Phi(x_1, \dots, x_n)$ be a multidimensional test function. The $n$-level density captures correlations between multiple low-lying zeros [cite: 9, 29].
To study the concentration of these densities, mathematicians introduced the **$n$-th centered moment** of the one-level density. Assuming GRH, Cheek et al. recently proved that the Katz-Sarnak density predictions hold for the $n$-th centered moments for test functions with extended support, validating that the fluctuations around the mean strictly follow the RMT models [cite: 15, 29].

### 10.3 The Function Field Analogue
Returning to the roots of the Katz-Sarnak philosophy, recent work by Hua Lin computes the 1-level density of zeros of order-$\ell$ Dirichlet $L$-functions over function fields $\mathbb{F}_q[t]$ [cite: 30, 31]. Working in both the Kummer setting ($q \equiv 1 \pmod \ell$) and the non-Kummer setting ($q \not\equiv 1 \pmod \ell$), Lin obtained the main term predicted by Random Matrix Theory (Unitary symmetry) alongside exact lower-order terms not predicted by basic RMT [cite: 30]. This provides a closed-loop validation of the geometric monodromy theories in the very environment that initially birthed the Katz-Sarnak conjectures.

## 11. Conclusion

The Katz-Sarnak Density Conjecture represents one of the most sublime unifications in modern mathematics, tying the abstract algebraic structures of Dirichlet $L$-functions to the statistical mechanics of random matrix theory. 

Through the lens of the 1-level density of low-lying zeros, we see that the family of all Dirichlet characters embodies Unitary symmetry, while the family of quadratic characters embodies Symplectic symmetry [cite: 2, 3]. For decades, verifying these symmetries was barricaded by the "trivial range" of the explicit formula. The monumental achievement of Drappeau, Pratt, and Radziwiłł to unconditionally break this barrier has not only vindicated the Katz-Sarnak philosophy but also solved the practical arithmetic problem of demonstrating that a majority of primitive Dirichlet $L$-functions do not vanish at their central point [cite: 5, 6].

As research pushes toward higher-level densities, weighted distributions [cite: 7, 28], and the precise modeling of arithmetic lower-order terms via the Ratios Conjecture [cite: 16, 25], the zero-distribution of Dirichlet $L$-functions continues to serve as the ultimate proving ground for our deepest understanding of the prime numbers.

**Sources:**
1. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8vTeHzwpQljmJq3GcHR6EahRvNrMZIv39fRrwfWhlWvHvSo9XlglaDokUEbV8VVDASRhWexoo0Y4T3COtsj0DRFgX9VYF-Ejd8mPaSuQ1XQ8o7ZjSJDKZqXZbGSKAneM29-SbA8w6)
2. [williams.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHh8fmkPcw0FZkU6icEBMgdpgkNn32L1DFGiX9Xw2TCazQpban9ARGQnfVdd0NNsV9NEllQTNu2NGlqW50gRrynpch9IzYaxUOpr6hqfuTTgcJL6nPC2DAJc7D9xSF9VqfwZuLC52WUDGiNPe0IwUyzeJS6aqgoj32JMd0NwjSQAh4Jo_7_xxboFm7vy3anpn5_xgnhCy1k9PMZPg==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkBzGdNYf-M4c25MjPZk6ORIEf-0sCAXpDDBdyR_kpd0SeHtfT9uDt8JjSV6nhV9HOolAr_9RO-WJuOE4Xj_hb0VsHv8sxsVUZAJg7PCbDt4sdXcSTK8MA)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBKHFQpZ6ml18accFKe5_Mqbbh0WV6HxCPIManewnWTAzIoJ-RS69IGIi8uKRjZNpBRr4ouE3sBoWPkiXGeTyUd6iaCpQuN02wK5iXkpaCHl6wE48q)
5. [cnrs.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErunDACbXOQQQcEXe0UYmmTg6FKyMtigYdzmkFMVRQsXfy5LCI1h3Z8bWQk-Z7rnS_Ii3cFK4NzKSi7y6aQiBMWZ6vOhCUiCaMCgLWfEM5cpowG2cyo9U6-timSIUibUYPO38G24fkFc31Mjjcw09_KIdccWJTT3Q=)
6. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBpW9RUuloDQ5MndqCAevPe3wgtbbUjdD0Jnf-DM5s_FzofSlgNBLuy9VUWL9xVfHClh2FmxXEX6RPNi-9LHVoLobSzo251C0VUHaQzkacC0aDYPK-NkZyNz8aLcGZy0oYnYFmkds7)
7. [kyushu-u.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJw7_gHMq3yynyK1hML7nuyR1Q5p7YRnSgq08AshS27IKuoXnK8NjHnNIC_MRmPOPXmRX-lvK3aJBGKscXGupXXHzSsvG9wbYee4gDnIcANUA7qPL4kfYe3zLvqY43tY77KGxKsWN1-kH3XcLrRfqp9sXdRPFpCxVFwiDq)
8. [vanderbilt.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElZrsfR2-tZ3rn9ooHc63aKyAKEpaiztrOOlnhkoxbJBLivkwzUsJpnYCHkZymnKWt587bU91LBbJABIYb6Ob7G6wJxK8hYNYY-l4Jiey6bqXwHJQy-d9xRf-txlStMxysbLA8szazZlK1LUS91RZSvfbSN-SDS-QKzvuCR3SYy6U4cVZgpmHVemyMIYCK3KtynpM6)
9. [williams.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkGO1_zG7ls4LCGVf9liLUlufBG9JGRDTE3Qs7WWnx8MN_GZerl6uSnSuGjVGS2LaajpWerGub26g-zdL1PW4QSmbWUcne_IF-R7drHs5MHzHoXC41ifqadDnkVF_8pBY_Sts4WHWrBH1q9EHi05iQXJOkTbW4RTXO_ngmDQzQFQT4-1vOuHRrCLISMZIqtCOidpm3KAlx4FE=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdiFumb8fawEdyFb9SL_VrSCixUMP8_0_BlfgFGyH51ypoJpSDv2HNi9WYxkxjK0etCL531tZzPT0Pi1y2Eb-sTz1c5n4xcisrb-lgeOLdFGfYXD8=)
11. [bilkent.edu.tr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuyRNwf952lo7nLaaR_C42wCQaTrUCG5mTPGtgeFHiNu3rg_MW9_aTNmLO5prBYB8zKVQlf_tnPESnhqlKMv9ocpBZsT6Tv7gBsz4Aq7kqluOKG2YNIEpVn6ayxvGxPoI8lkkoAB-Bi1kTcJM8X8zc0K2iNXLfXF9m7iLE7sX5eO_MBdzmcFYylaCbMDV3aA==)
12. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaXDAozKZJlQpuT0MTpUtxArNjhsh7ahaWlEcaZCZPrv2vQG390XCEO6_WGZGQs6TFHDnoQFryWzWNhw-QEq19U9zt8VsZLJ1mqxwbEtEYmLFmFz237CMvdr13UuOo1KC-6Q9ZCF-HDrRvEvM1OnNclghcRIUs1iWGzGQfzRpqKrCAZFFb9JxjTiMjGAle)
13. [williams.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcrnW02nI_NWLdh5eIgrLHOZB1juPcAtEPmKh6kisZHG14ak4X2RVV454xi5Sfe3vRGcaGn14qg0TPU2q7rtyZmW5wyAMNw5NZv1XDSt3tlLKUu2tW1T3kJ0MF2TKWKyUikUNUVbSryY89Z6_dnoIGlF1FG64-JNyxe8m0-jTckE8ExhCmaUF_ZWB0unG3vzAkG5gi)
14. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhd3xSqkkAgAuDkuIzkBay0FHDHCxAVbYk5G46jNLOhTL0UZ50lEP-_4V9nxkxU9h6jk45V53n-vh14f8tpgfoyol-SA--ECogIqZzvMSfof1tBgbxlbe9kT3jDQ_c2SE_yTHexyZF0C-u1ZQu99u1Q3EynLQ=)
15. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4ThhAVdR9E7MLhgSlba3Hrp1Qt57MMe8IQZtCZSSSptAXEzk6VUD1ooNXt-uZcoargk_lI0CpTZM7QRvnXEMCL2kpBOEnzLGcuvxNV-8mrz1xddy4I83zP6XgKeO9R5TtSurlzoOvBUe134aq)
16. [williams.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMLNN5sc8oHKDiUsX6FGiOvd75W25pk6_qMyDbcOjNtKchUiT8myrH-CXzHZynTIhffbZNmglvcQ5Kqtj-b7BoWjfDRCC6vhseAo7r4w-0Ch37R1nZOHy0lMnG1yIjbbvK9HHjV4Aq6VMAXh83nDuB0CVL3VKqT6tMGQ6UkaPwwJpsgxpIbJwv_5P3_llhZII-iRCJoTtHFYTfcl3pCSt2kfSGNGlTZ6_In6F4uc4B8IgD)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGs-9-NCCcQPvYt-IIukqJh45JUdD1N4NHcf4-YILlR4ELADvOlD8KfvDUXru7pX7uCrCculGFpUbDv6KBcEaweB2k3SiqlKP9Km_g8RkhV7E2wwMfGlTU)
18. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG82xy6d5Lbf5s8qopeIbMpEs6M3J33DH6ugNB8N7qIsXpPCjoRLVeD85g0bN8ub5mTLH1zk1Kx0CGJlj-U1uO7HmKVyJRvCfcdZ2IHOx_fhXQFXxOJtUxSdCMV2g==)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAFsatsloptUfbOIluqwhbeCTp5qbjdWQqf8UCaHtqOASQfIFcK_UFKKPqjCDWVb92BX_CNGsiPJBS1tcGCzlYE1-b_5DQM3r7vWgWBAS2aSkUzgyNbFayptujIdpGi1yQ5MCOt4Kmj7JhsbR5PLkDu0tkFUmOv4hiGlO9o0CMBsIlnSFQnQ1whLoHBI0KukqynFK5EA3d8P-Csc-0U5PFOlAuadW6Ktk6LpK314dUkMi2MCIOptpjVa-mU8nUy_o5VuS01en2ONM9ij35Jw==)
20. [bilkent.edu.tr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6svd0kI_Ju_jjWUm9Bs3qFAFy0UZWSHwqvSu6Y7ri9DnFdIuEq1nYIrPQ1Ul0XFRCI1H9GHyUbGbDuffki0CvJYBBgB0RxUGuR5iCiqTCbBaSQjIa7-wT5SXg7FjJW8lMR2sVQt8=)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZSe13HhowXMvhGCkhD07ftI2BPXiqbAurK57GeNH6eCrIWxCOl7rNcU0V8J83A6vVTE9iWxdnFfybFgg4fdfywUNGBFh37RmnPY9gsuq38OLbaZaN)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-OK65rMOxiodLYSCiezn2n6-eUflfhfY7O77afclBxLEauE2BoptP3CzyFxvMNpbWIVb0T0wFNJyw6JRJHC0L3P9g1-1D-fMVn--Jts51tdTq9TD6)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKrmgH0IkQNkbOR9AIh-Jdst-lgUGco9pGu-YWYXFPqsFbAENc0iC8E8GS8yQsWoKOrMC35BoL-62U7HhPz2i67req1BfxjLFIypZHAigVm4OvTlk5J3Uw)
24. [illinois.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHx_FUR-RpSWLBZQTWcGgeGzaLY0D91KYxwkFAaD95JnwpVxSoZLcuWzEbekbHFVAek-BwIqvSX7Toz1rIM5PX0aWTErVUsb9X2d3LpnK4Ls0PW8s5O68g8iEFCgcymOC-otCOXoq36ekuIkFiAkVnhkVZMA2PAWtbeHLLQ)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHadcmneyY3ILVkRDc0A4J8--B05QtNU-bMC4Jy37azRuJbMRI5lq7uNSaq5SE9Ppe_A9CST6VXnMXERVQIT126PcfIA5uANrTad2t7ZgiCLXU6JfRL)
26. [gu.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXh3vTXANunT0mn852TmopnYgFhpYYRslE9oITUAcayjMIrZtlHUQcP_k-hbMiYjVXaLqf_wHQ3AvNqAsPEInSpVGgyQ7D4EC3VpOlX9quk8U5eSp9185LHIMFfeO5ghaNKxIBAZevIn2Twvq5WpZjpKuwiLnr)
27. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7baDaRI8nrIpp8voEY6CjddHrJMbGQJYAJZrZDzLZmgwrTBtC7_gZIGMqD5q2x9YdT9LfcxkX50wwbFtSKkJvBB1io2XH8VFqtDDWayP6iP8OVY9dQFW6TexsAQ==)
28. [polito.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRJJAHZaoU2Sw7vx8D7LMX5aQ4A71rWB8mCitHdlciCjeE-SP-B8BL1x3ztI6vBemObn_h8b-FTiCwjc-ArP4WPOyz2QqTLIBAliDX064ViY_KNWGTXdaWutH729rZdjph68XL7P9s1vXvwA8eYoktQD2I72Lu)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIlFz-_OVkKcWzLU8tN5IO51md04czI-74xunO3XXtE03si12GQFFBWRKPmhxaL6c6E2uHEKL0c_oYeMZQbHB_6wlmMQnqUE7SZGkBjhkBk_cZ0Y4w)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVvPPv_Fx2dIwLr33YjVQpFyyWQ3UbXum57BsYJcRa1c5ee2sbot0cMdOPsaGqlY40aP3c5LemdZ_RoAcvHI1zcH2IuxiBw1DfO4XYniUeMFsyC64z)
31. [mathtube.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoKilPC4eKtux2gqBbilFTsrBfR7WXVI1RadyNbJnkwgsIa623pg-xKkQI_AfiBQH5oyA8lqFLWmMO9tpZ5fUxsHJozpftZsp0YDWbteWlB9N6fHAHOs-UwFlgIOvk5cExvt4B_8rbIt5gO1besNso7ADBJZBsSSImcAXD78tT-xwOjkR8n5EeNQw-Ajq9GrmjmTbCdnScQ-Zd)

