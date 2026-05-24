# Argos lens fingerprint: Density hypothesis (Riemann zeta)

**Pythia queue id:** 365
**Tier:** T5
**Priority:** 5
**Requested by:** Argos
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdkYTBTYXRXYUEtU1dfdU1QNW9EMzJRNBIXZGEwU2F0V2FBLVNXX3VNUDVvRDMyUTQ
**Elapsed:** 305s
**Completed at:** 2026-05-24T07:54:14.801107+00:00

---

# Primary-Literature Lens Fingerprint for Open Problem MATH-0370: Density Hypothesis (Riemann Zeta)

*   **Key Points:**
    *   Research suggests that solving the Density Hypothesis (DH) is heavily reliant on improving zero-density estimates, with recent major breakthroughs achieved via classical analytic methods (e.g., the Guth-Maynard bound).
    *   It seems likely that interdisciplinary lenses—such as dynamical systems, information theory, and the renormalization group—offer profound heuristic frameworks and conjectural bridges, though they have yet to yield unconditional proofs of DH or the Riemann Hypothesis (RH).
    *   The evidence leans toward a deep structural isomorphism between the nontrivial zeros of the Riemann zeta function and the eigenspectra of chaotic, unitary, or cyclically renormalized physical systems, highlighting a systemic disagreement between purely combinatorial bounds and physical continuum models.

*   **Overview:** 
    This report investigates the open problem `MATH-0370`, the Density Hypothesis for the Riemann zeta function, through three designated primary-literature lenses: `STANCE_DYNAMICAL_SYSTEMS@v1`, `STANCE_INFORMATION_THEORY@v1`, and `STANCE_RENORMALIZATION_GROUP@v1`. For each lens, we identify the two strongest or most representative primary-literature attempts.
*   **Problem Context:** 
    The Density Hypothesis posits that the number of zeros of the Riemann zeta function in the region \(\text{Re}(s) \geq \sigma\) up to height \(T\), denoted \(N(\sigma, T)\), is bounded by \(T^{2(1-\sigma)+\epsilon}\) for any \(\epsilon > 0\) [cite: 1, 2]. While purely analytic number theory currently drives the state-of-the-art bounds, interdisciplinary approaches project novel measurements onto this problem.
*   **Lens Methodology:** 
    Applying multi-perspective methodology, we summarize the measurement projected, the verdict reached, and the axes of disagreement for each candidate lens, systematically comparing their topological, physical, and entropic assumptions against classical zero-density frameworks.

## Introduction to MATH-0370 and the Density Hypothesis

The Riemann zeta function, \(\zeta(s)\), is a cornerstone of analytic number theory, originally defined for \(\text{Re}(s) > 1\) by the Dirichlet series \(\zeta(s) = \sum_{n=1}^{\infty} n^{-s}\) and extended via analytic continuation to the entire complex plane with a simple pole at \(s=1\) [cite: 3, 4]. The nontrivial zeros of \(\zeta(s)\) lie in the critical strip \(0 < \text{Re}(s) < 1\), and the Riemann Hypothesis (RH) conjectures that all such zeros lie precisely on the critical line \(\text{Re}(s) = 1/2\) [cite: 3, 5].

While RH implies the optimal distribution of primes, a weaker but profoundly impactful conjecture is the **Density Hypothesis** (DH). Let \(N(\sigma, T)\) denote the number of zeros \(\rho = \beta + i\gamma\) of \(\zeta(s)\) such that \(\beta \geq \sigma\) and \(|\gamma| \leq T\) [cite: 1]. The Density Hypothesis states that for \(1/2 \leq \sigma \leq 1\) and every \(\epsilon > 0\):
\[ N(\sigma, T) \ll T^{2(1-\sigma)+\epsilon} \]
The optimal exponent \(2\) is derived from the fact that \(N(1/2, T) \gg T \log T\) [cite: 2]. The validity of the Density Hypothesis would establish the Prime Number Theorem in short intervals, specifically \(\psi(x+h) - \psi(x) \sim h\) for all \(h > x^{1/2+\epsilon}\), an estimate that cannot be further improved even if the full Riemann Hypothesis is assumed [cite: 1]. 

Historically, purely analytic methods have been deployed to constrain the exponent \(\theta(\sigma)\) where \(N(\sigma, T) \ll T^{\theta(\sigma)(1-\sigma) + \epsilon}\) [cite: 6, 7]. The long-standing Ingham bound provided \(3/5\) (or \(0.6\)) for \(\sigma\) near \(1/2\) [cite: 6]. Recently, a monumental breakthrough by Guth and Maynard significantly improved this bound to \(30/13\) (approximately \(2.307\)), shrinking the gap toward the conjectured exponent of \(2\) [cite: 1, 8]. Specifically, the Guth-Maynard zero-density estimate yields \(N(\sigma, T) \ll T^{30(1-\sigma)/13 + o(1)}\), extending the known asymptotics for primes in short intervals to lengths \(x^{17/30 + o(1)}\) [cite: 1, 6]. 

Despite these analytic triumphs, the underlying structural mechanisms governing the spacing and density of the zeros remain elusive. This has catalyzed the application of diverse cross-disciplinary lenses, attempting to map the density and distribution of the zeta zeros to dynamic, entropic, and cyclically scaled systems.

### State-of-the-Art Zero-Density Estimates

| Framework / Theorem | Exponent Bound \(\theta(\sigma)\) | Significance for DH |
| :--- | :--- | :--- |
| **Density Hypothesis (Conjecture)** | \(2\) | Optimal bound; implies primes in short intervals \(h > x^{1/2+\epsilon}\) [cite: 1, 2]. |
| **Guth-Maynard (2024)** | \(30/13 \approx 2.307\) | Current state-of-the-art global bound; bridges Ingham and Huxley estimates [cite: 1, 8]. |
| **Ingham Bound** | \(3/(2-\sigma)\) | Classic uniform bound for \(1/2 < \sigma \leq 3/4\) [cite: 7]. |
| **Huxley Bound** | \(12/5 = 2.4\) | Previous benchmark near \(\sigma = 3/4\) [cite: 2, 7]. |
| **Bourgain (2000)** | DH valid for \(\sigma \geq 25/32 \approx 0.781\) | Identifies the halfplane where the strict exponent \(2\) is unconditionally proven [cite: 1, 9]. |

## Lens 1: STANCE_DYNAMICAL_SYSTEMS@v1

The dynamical systems lens interprets the distribution of the Riemann zeros as the eigenspectrum or the absorption spectrum of an underlying classical or quantum chaotic system. Inspired by the Pólya-Hilbert conjecture, this lens seeks a self-adjoint operator (a Hamiltonian) whose eigenvalues precisely match the ordinates of the nontrivial zeros, \(t_n\), where \(\rho_n = 1/2 + it_n\) [cite: 10, 11]. 

### Attempt 1: The Berry-Keating-Connes Hamiltonian and Chaotic Operators

The most historically profound application of this lens is the Berry-Keating conjecture, later adapted by Connes, which studies the quantization of the classical Hamiltonian \(H = xp\) [cite: 12, 13]. A 2025 development further synthesizes this operator approach with modern zero-density estimates (such as Guth-Maynard) by projecting a localized chaotic operator [cite: 8, 14].

**(a) Measurement Projected**
The measurement projected by this attempt is the **fluctuation of the local level density** of the zeta zeros, analogized to the chaotic scattering in a phase space. Berry and Keating originally demonstrated that semiclassical regularization of the Hamiltonian \(H = xp\) yields a smooth counting function corresponding to the Riemann zeros [cite: 15]. Modern integrations project an explicit chaotic operator constructed from the Riemann-von Mangoldt formula:
\[ \mathcal{O}_x = -i \log T \frac{d}{dT} + \frac{1}{2} + \epsilon S(T) \]
where \(S(T) = \frac{1}{\pi} \arg \zeta(1/2 + iT)\) captures the local, microscopic irregularities in the zero distribution, and \(\epsilon\) determines the amplitude of the chaotic perturbation [cite: 8]. The bounded interior of this dynamical parameter space corresponds to the locally regular spacing of zeros, while its diffuse boundary maps to chaotic instability [cite: 8].

**(b) Verdict Reached**
The dynamical verdict is that the zeros on the critical line manifest as missing states (absorption lines) or bound states under specific regularizations [cite: 12, 13]. The 2025 operator synthesis concludes that mapping the microscopic oscillations of nontrivial zeros via a logarithmic differential structure tightly confines the spectral error terms, providing a robust heuristic algorithm that conceptually aligns with, and seeks to algorithmically sharpen, the \(T^{30(1-\sigma)/13}\) zero-density bounds achieved by Guth and Maynard [cite: 8]. The chaotic dynamics explain the Gaussian Unitary Ensemble (GUE) statistics of the zeros, confirming the presence of broken time-reversal symmetry in the analogous prime distribution flow [cite: 10, 16, 17].

**(c) Axis of Disagreement**
The primary axis of disagreement with purely analytic lenses (such as those employed in rigorous zero-density bounds) is the reliance on **spectral realization and physical heuristics versus strict polynomial bounds**. Analytic lenses rely on Dirichlet polynomial mean-value theorems and large-value estimates (e.g., Bourgain's exponent pairs or Halász's theorem) [cite: 1, 18]. In contrast, the dynamical systems lens asserts that the true nature of the Density Hypothesis cannot be resolved merely by subdividing Dirichlet intervals, but must be understood geometrically as a global attractor or a structurally constrained phase space [cite: 1, 19]. Furthermore, within the dynamical systems community itself, there is disagreement between the Berry-Keating model (zeros as discrete spectral lines) and Connes's adelic model (zeros as missing spectral lines in an absorption spectrum) [cite: 12, 13].

### Attempt 2: The Wu-Sprung Fractal Potential and Semiclassical Trace Formulae

Another prominent attempt within this lens is the Wu-Sprung model, which reconstructs a 1D local potential from the spectral data of the Riemann zeros using an inverse scattering approach [cite: 16, 20, 21]. 

**(a) Measurement Projected**
This approach projects a **fractal quantum mechanical potential**, \(V(x)\), derived through fractional calculus and the WKB (Wentzel-Kramers-Brillouin) approximation. Wu and Sprung inverted the smooth average level density of the zeros to generate a one-dimensional local potential. By interpreting the density of states via Delsarte's formula, they constructed a Hamiltonian \(H = -d^2/dx^2 + V(x)\) [cite: 16, 20, 22]. The measurement of interest is the fractal dimension of this potential. The sum over prime numbers \(p\), which corresponds to primitive periodic orbits in Gutzwiller's formula, induces a fluctuating part in the potential, resulting in a calculated fractal dimension of \(D = 1.5\) [cite: 16, 20, 21]. 

**(b) Verdict Reached**
The Wu-Sprung model successfully generates a smooth average level density that mathematically obeys the Riemann zeros' distribution. The potential relies implicitly on the Gamma function and the zeroth-order Bessel function, with further iterations incorporating a weighted superposition of Weierstrass functions summed over all primes to capture the exact fractal fluctuations [cite: 20, 21]. The verdict is that the conundrum of merging chaotic dynamics with a one-dimensional integrable, time-reversal quantum Hamiltonian is theoretically resolvable if the potential is intrinsically fractal, demonstrating deep symmetries analogous to quantum chaos [cite: 16, 21].

**(c) Axis of Disagreement**
This lens fundamentally conflicts with traditional analytic number theorists on the axis of **rigor and directionality of proof**. As noted in mathematical critiques, the Wu-Sprung model is viewed by pure mathematicians as an interesting numerical heuristic rather than a mathematical solution to RH or DH [cite: 22]. The mathematical community asserts that ideas from physics must be formulated as strict, self-contained mathematical bounds; the inverse spectral mapping creates a potential from the zeros but does not independently constrain the zeros' location off the critical line (i.e., it assumes RH to build the potential rather than proving RH or DH) [cite: 21, 22]. Thus, the disagreement lies in **constructive empiricism vs. deductive proof**.

## Lens 2: STANCE_INFORMATION_THEORY@v1

The information theory lens approaches the distribution of primes and the zeta zeros as data transmission, encoding, and entropic boundaries. This perspective maps analytical continuity and error terms to channel capacity, signal-to-noise ratios, and thermodynamic partition functions.

### Attempt 1: Spectral Signal Processing, Shannon-Nyquist, and Holographic Bounds

A sophisticated 2026 application of Information Physics attempts to deliver a conditional proof of the Riemann Hypothesis and, by extension, rigidly constrain zero-density via the Shannon-Nyquist Sampling Theorem [cite: 17, 23]. 

**(a) Measurement Projected**
The projected measurement is the **Signal-to-Noise Ratio (SNR) and the spectral energy density** of the arithmetic field acting as a transmission channel [cite: 17, 23]. The explicit formula connecting primes to zeta zeros is interpreted as a spectral transfer function, with the nontrivial zeros \(\rho = 1/2 + it\) acting as discrete sampling frequencies. If a zero exists off the critical line (\(\text{Re}(s) = \sigma \neq 1/2\)), it corresponds to a fluctuation signal \(f(x) = x^{\sigma + it}\) [cite: 17]. The capacity of this "Number Line channel" is bounded by the Bekenstein Bound (Holographic Information Bound), which dictates the maximum entropy a 1D bounded region can carry [cite: 17].

**(b) Verdict Reached**
The verdict derived from this framework is that any deviation from the critical line (\(\sigma > 1/2\)) introduces an exponential gain in the transfer function (\(G(x) = x^\epsilon\)) [cite: 17]. Such a deviation generates "Hyper-Extensive" spectral noise that diverges asymptotically as \(X^{2\Theta}\) [cite: 17, 23]. This divergence fatally violates the Bekenstein bound for a 1D manifold and drives the SNR to zero, which operationally would render the integer sequence indistinguishable at the limit [cite: 17, 23]. Thus, by postulating Operational Distinguishability and Unitary Conservation, the framework concludes that the Riemann Hypothesis (and strictly the Density Hypothesis exponent of 2) is a necessary physical condition for the unitary evolution of arithmetic information [cite: 17, 23].

**(c) Axis of Disagreement**
The primary axis of disagreement lies in **ontological assumptions regarding mathematical spaces**. Pure analytic lenses treat the integers and primes as abstract axiomatic constructs unbound by physical capacity limits. The Information Theory lens controversially asserts that the number line is subject to physical, thermodynamic limits (the Bekenstein bound) and operational distinguishability [cite: 17]. Analytic number theorists reject the application of finite physical channel capacities to countably infinite abstract sets, arguing that signal divergence in the explicit formula does not "break" the integers, but simply reflects the analytical properties of the error term in the Prime Number Theorem (\(E(x) = O(x^{1/2+\epsilon})\)) [cite: 1, 17]. 

### Attempt 2: The Free Riemann Gas and Tsallis/Group Entropy Mappings

A second major theoretical mapping comes from the intersection of statistical mechanics and information theory, pioneered by Bernard Julia and extended by others (e.g., Bost and Connes), which reframes the zeta function as a partition function of an abstract "Riemann gas" [cite: 24].

**(a) Measurement Projected**
Here, the projected measurement is the **entropy and macroscopic thermodynamic state** of a numerical gas composed of prime numbers. The Riemann zeta function is exactly identical to the partition function of a free bosonic gas where the primes act as the fundamental energy states (primes as "particles") [cite: 24]. Extensions of this logic measure the *informational bias* in prime distributions using Shannon entropy inequalities on the Liouville function [cite: 25]. Furthermore, the universality of the Riemann zeta function (Voronin's theorem) is viewed as possessing infinite mapping entropy, suggesting that different zeta functions are associated with specific universal classes of group entropy, such as Tsallis entropy [cite: 26].

**(b) Verdict Reached**
The application of this lens yields the verdict that the analytic properties of \(\zeta(s)\)—specifically its pole at \(s=1\)—correspond to a spontaneous symmetry breaking or a phase transition in the thermodynamic model [cite: 24]. When primes are treated as a "signal" in the sense of information theory, empirical analysis reveals a scale-invariant 1/f noise (flicker noise) in their distribution power-frequency spectrum [cite: 24]. The structural necessity of the zeros lying on the critical line represents an entropic equilibrium—a geometric manifold where identity, coherence, and truth achieve an entropy-flat curvature [cite: 19, 27, 28]. 

**(c) Axis of Disagreement**
This model disagrees with purely arithmetic approaches (like the sieve methods used by Maynard and Tao) primarily on the axis of **randomness versus determinism**. While sieve methods and bounded gaps rely on the quasi-randomness of prime distributions up to strict congruence limits (using the pigeonhole principle) [cite: 25], the entropic gas model views the distribution as a deterministic outcome of an infinite network of interdependent correlations governed by macroscopic thermodynamic laws [cite: 26]. Additionally, mapping zeta functions to non-extensive statistical mechanics (Tsallis entropy) introduces parameters that pure mathematicians view as extraneous to the intrinsic algebraic properties of Dirichlet L-functions [cite: 26, 29].

## Lens 3: STANCE_RENORMALIZATION_GROUP@v1

The renormalization group (RG) lens analyzes the scaling symmetries and scale-dependent properties of the zeta function. This approach views the distribution of zeros and the density hypothesis as emergent properties of a system flowing toward a critical fixed point or a limit cycle across different energy/length scales.

### Attempt 1: The Cyclic "Russian Doll" Renormalization Group

The most mathematically sophisticated primary-literature attempt within this lens is Germán Sierra's formulation of the cyclic "Russian Doll" Renormalization Group, heavily collaborating with A. LeClair and J.M. Román [cite: 30, 31, 32].

**(a) Measurement Projected**
The measurement projected by this framework is the **scale-dependent flow of the pairing coupling** in a quantum many-body system, specifically mapped to the Berry-Keating Hamiltonian. Sierra et al. mapped the \(H = xp\) model into the Russian doll (RD) BCS model of superconductivity [cite: 32]. The RD model features a pairing scattering phase that breaks time-reversal symmetry [cite: 30, 32]. The key measurement is the cyclic RG flow, where the coupling parameter \(g\) flows periodically with the scale, manifesting bound states of Cooper pairs whose energies scale geometrically as \(e^{-n\lambda}\), where \(\lambda = 2\pi/h\) is the period of the RG cycles [cite: 32].

**(b) Verdict Reached**
The verdict of this attempt is that the smooth part of the Riemann counting formula for the zeros is reproduced exactly by this consistent quantization [cite: 13, 31]. Remarkably, the nontrivial zeros of the Riemann zeta function emerge not as direct eigenstates, but as **missing states** (or absorption lines) in the spectrum of the RD model, seamlessly agreeing with Connes's adelic formulation of the Riemann hypothesis [cite: 13, 31, 32]. The general zeta series for \(s \neq 1\) is shown to be strongly renormalizable, and its renormalized vacuum energy aligns perfectly with the Riemann zeta function, suggesting that the Density Hypothesis bounds are constrained by the exact solvability and cyclic universality of this scale-invariant flow [cite: 31, 32].

**(c) Axis of Disagreement**
The fundamental axis of disagreement with other physical lenses (like the Wu-Sprung potential) and pure analytic bounds is the **nature of the spectrum and symmetry breaking**. While the Wu-Sprung model forces the zeros to be direct eigenvalues of an artificial fractal potential [cite: 16, 21], the Russian Doll RG asserts the zeros are *absences* in the spectrum driven by limit cycles rather than fixed points [cite: 32]. From the perspective of analytic number theory (e.g., the Guth-Maynard large value estimations [cite: 1]), the continuous scaling limit approach struggles to provide explicit hard bounds on the error terms \(N(\sigma, T)\) for specific regions of the critical strip (e.g., \(\sigma = 3/4\)), remaining heavily reliant on semiclassical approximations [cite: 1, 15].

### Attempt 2: Number-Theoretic Deformation Parameters and Critical Scaling Methods

Another dimension of the RG lens explores the regularization and direct fractional scaling of the zeta series, as well as connections to topological field theory and quantum criticality [cite: 31, 33, 34].

**(a) Measurement Projected**
This approach projects the **renormalized value and scale invariance of divergent sums**. One primary sub-attempt uses a double Cesàro mean and scaling parameter \(k^2\) to evaluate the analytic continuation of \(\zeta(-1)\) and extends this to the critical strip [cite: 33]. Another profound application exists in the Topological Geometrodynamics (TGD) framework, which investigates the renormalization group equations for magnetic flux tubes. It measures the critical values of the inverse Kähler coupling strength, \(1/\alpha_K\), projecting that its imaginary roots or proportional values align identically with the nontrivial zeros \(s = 1/2 + iy\) of the zeta function [cite: 34]. 

**(b) Verdict Reached**
By utilizing techniques of dimensional and analytic regularization, researchers identify infinite-order difference operators (Bernoulli operators) that classify weakly renormalizable series of Dirichlet type [cite: 31]. The probabilistic renormalization is shown to be entirely compatible with analytic continuation. The TGD framework posits that quantum criticality is directly realized in terms of the zeta zeros, suggesting that the sign of the oscillatory real and imaginary parts along the critical line constraints the Kähler form, forcing the zeros into a rigid geometric spacing that fundamentally rejects the existence of zeros off the critical line (validating both RH and the Density Hypothesis) [cite: 34].

**(c) Axis of Disagreement**
This approach diverges from standard perturbation theory and classical polynomial bounding. Analytic bounds (e.g., Ingham, Huxley, and Guth-Maynard) derive zero-density estimates using rigid, discrete Diophantine systems, Weyl sums, and discrete decoupling [cite: 1, 35]. In contrast, the RG lens heavily employs **continuum scaling limits, fractional calculus, and counterterms** (e.g., introducing a "Riemann mass" to cancel divergences in odd-dimensional space-time) [cite: 31]. Number theorists often express skepticism toward defining rigorous zero-density exponents via divergent series regularization, as renormalization schemes frequently introduce arbitrary constants or rely on physical symmetries that lack pure arithmetical counterparts [cite: 31, 35].

## Comparative Synthesis: Axes of Disagreement and Future Trajectories

The ongoing effort to resolve the Density Hypothesis (`MATH-0370`) reveals a stark epistemological divide between classical analytic number theory and interdisciplinary physics-based models. 

**1. The Combinatorial vs. Continuous Divide:**
Analytic approaches, culminating in the Guth-Maynard bound of \(N(\sigma, T) \ll T^{30(1-\sigma)/13}\) [cite: 1, 6], operate on the discrete translation structure of integers. They rely on dissecting Dirichlet polynomials, decoupling, and Strichartz estimates [cite: 1, 35]. Conversely, the Dynamical Systems and Renormalization Group lenses treat the zeros as continuous phase-space phenomena, whether via chaotic operator flows [cite: 8], cyclic limit flows [cite: 32], or fractal semiclassical potentials [cite: 21]. The disagreement centers on whether the structural gaps in primes can be captured by macroscopic continuous flows without losing the microscopic discrete rigor required for strict inequality bounds.

**2. Ontological Status of the Number Line:**
The Information Theory lens explicitly challenges the boundless abstraction of the number line. By applying the Bekenstein Bound and Shannon-Nyquist theorem [cite: 17], it asserts that mathematical spaces cannot encode "hyper-extensive" noise without violating the operational distinguishability of the integers. This physical constraint is categorically rejected by pure arithmetic frameworks, which do not recognize thermodynamic or signal capacity limits on abstract spaces. 

**3. Direct Eigenvalues vs. Missing States:**
Within the physical frameworks, a fierce internal debate persists regarding the spectral origin of the zeros. The Berry-Keating and Wu-Sprung models generally attempt to manifest the zeros as direct quantum energy levels (bound states) [cite: 15, 16]. In contrast, the cyclic Russian Doll RG model, aligning with Connes, models the zeros as *missing* states in an absorption spectrum, pointing to a radically different underlying symmetry class [cite: 31, 32].

### Conclusion

The primary-literature fingerprint for the Density Hypothesis illustrates a mathematical landscape at a profound crossroads. While pure analytic bounds systematically carve away the parameter space—moving from \(12/5\) to \(30/13\) and inching toward the optimal exponent of \(2\)—the interdisciplinary lenses (`STANCE_DYNAMICAL_SYSTEMS`, `STANCE_INFORMATION_THEORY`, `STANCE_RENORMALIZATION_GROUP`) argue that these combinatorial methods may asymptotically exhaust themselves. These physical lenses propose that the ultimate proof of the Density Hypothesis, and the Riemann Hypothesis itself, will require acknowledging that the primes and zeta zeros are governed by scale-invariant limit cycles, chaotic operator matrices, and holographic informational boundaries.

**Sources:**
1. [ugent.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHL8t4iQ9d7KuNluZf-xYPBIcoAmHJ6PElhUmwHT1QuocFslNhpnnU-8XgyFwfTli6o-EKf7kpBl5VyqwtZ1rRbWw7qxHapZ-rxR8RMIbto3newq9i-Y2gYLCT2zxS2J4ne1PptLOhfzHwdY5vwQ3gfA==)
2. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvwgqaHGcazcgAvxjsSUgX5R5a6G_zMnF1LuPRBrL2dFnCrU-o2CWU2Cchpr--phwAaaxueeT3b1LJJjOQ765g6-0FN54uXKQU8k27y9kizZMWl8KIkAo_Z9gkmu2FpK__JjNgh8_CteEUp_ZbxorfCXDP8YoLUFKpBrQhM6J9JX_kk7CEG0N8OkOyzKz5V2i1-rCxlSyCrj_Z5RyDX9TABJ06)
3. [wjarr.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQWb5G0if6VFZOANE1G8f6hCd46VePuJJpPj39us4TIX33qwwgIKDiYnGRAiy9nz3gNQO5QJyMfLTzWdst4ExVIhWcOQ2qWJCMCpKB1vB_Sax0W24eYbK6-Mr7zIkeBcuPWTuSfw1xpYnj5xhJzb7PM51nAl2fHTc2TERz)
4. [hit-u.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4I_3E1meApsbbXfeqLknHdnT-Gs_JB2k89Sm6DxWqFFHCJh3ISaa6nzDyFrxyaK-QazeAzVl--dYgwXGjy4ta9B8Lwp5wVl2aSSVwJLPnYSI0KZfIkxQbqSWTLSBhzT9PW9oDnrTbBUgtFJB_Ho0fD94M)
5. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGK2dqWKFqv8LN-vQm-k4oOYO3NkjMpSJoxh1dOPxQyNjhp0zPWlL8jCYZdqtIuFPSbq6AT6QG6YnYFagETmBlCVJdONe7QN4v5t6l1wvMiD7WBeE-otLSScIcRf35zqIkkQ82hZE19bk=)
6. [mathstodon.xyz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1V5uufN_AVLUoITTok8HtiQqb3CUhd9p06ez4z0wG3LKaCUTa3W8SlH6HsUelQ4fz4IcomrjBFlRKnHkrNsDj0ZW6Qz_n4EjS1PCbrWt5QFad1UJoYhQMesFpToY63PrmQrgL)
7. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhrKWK9NE9FqKnFWip2lrer9DHRybMKkOYfbkV3k-EaD40o7ExluncwoLF4nRq5IHwGtaOtyUMTX6d21_0w662uloV1Le_D2Hc9jWiiIqCjc_wgEQdZIYLWBQj48FYJFfVSbxqgeA9S64BjJmLQrPohCb8o0eUiGyks3k=)
8. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRn8kGv_JB6QgImJ5QQEgtkW8_hw5kwvt65CjXBXUbdTgeEBAVCfuG_ogP-M_jhQRRuf8fXItPxmozhzTaI0Ks2vTo9Iiywcc2bki3ZDXOXRbUvm4B07AmPOBdxW2Akr4p4IO0_l0=)
9. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEExl13JF8kDg5rafA7M0gjvPMF4nRDKCsZehzvr5pFBcCekWD7pjXE5aYypGJbfC-GbB364ACa9XVnJ6abIEdTqoet3ocX3qTBF8wmjeFb7YMWisCdr2jjmxxmV8zxoD5oerfRklJ2x0tVwWg6QixA_tLikFV8X8o=)
10. [scholarpedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIZjUWerRgVsLANVY2rN6PuS9LdY7gxUbG4J-siDTDDPHrIedWC0zHg93wvXVozq-nkYSu6S80t1am9Y7uNynd4q4BvZC4FobCeMX5Pv40-PE-mBGRGVjwvPGLocZCuCvab707ZnyaK9RIfhiEWsMpmBNeUok26QfR)
11. [ex.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5zt8rKYWcZIsWxgOr8D1MNsiDlSAVdRl7J-0Zz41ZSZ0TItGbuEvCrkgsOzYVfpAbq6fh2cGrzDrYT_r7PtOE6gLYoF60bh_TgH65UmtjSQo-D4-T1Ic7Hhv_ppYrOZsVmohVlbp9GNoAGFDwW6bmsOVwHlSkxFk=)
12. [cern.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3v1auhpnW_FJqnliddqhgQfuFs-ULkEjM2L96vllpaqcWRgMgjVu6kRcLnB-twUEcOgFtbJPU1fr9HaKfhiOxrc5HoO03itaQEmCvyedjQJsH3lDEqW9RyOk2qPCdnCEPZKj3bpdkXnrKaxM1mku_PdMgRO84k2xOT3A90Dg=)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEafLGwfKPNj4Lyv783c1sst4w9ekm4QMdyq2AuIUKojI3ajW4wg_Za2Ctx4TxU8wPX-X_kRugLEey0qZfVcGS968jh532tS4Ww2a6adZou4t0P4pCzx0Rf)
14. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJ0PGIkROBo6CJZAJpsWBx-TTS7DgM3RnPVNfLFnCUCcMEpy7EVw42Gckxuya_NBVaaeZLbwCxwYr-dV4f3-89MwhSp6PyqX6w9tG3q1HgOaDU5pWHTs_NfE7aDRbhrSmhEp4KqX1NgKB-X37QCuswTgA=)
15. [csic.es](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2tSuMCBL2zwgjzwf-c5EidU8zbE3mwtKcVcIUVoIbj_BBqqnZ1wl0P54dmaeP0I-qryOdLHDANrzxQOAfKXAjVBPb22EVXkmAHD1_KOzC5Shwziy9Lzjd9Fjqe51fUDl0nm0aQXHxgu9iLTeFLdlOc39VHL0tBi8=)
16. [ex.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMd1pMynsd9aqXS35mgXCAy3DgzhX7AKpbnZIGJW2bdyTsLB37RD3Y_kYtxMMRlLEEfx39HCIXfkzXuMcYrirgymyJ4eSgBPqdigNDtMr7d6_OipT_FLxBs57zzTBQx7QykhbS-9Td2UD4nMiZoyCoW9KI89W78AFz2c8=)
17. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJe3wW7PZ3WxSRa6XzGlPsCBtX7Kkz7aRjfKYInEhose_wkGnU6dDXWSwrJGgHgpg9grCZ9Ed5g3XhuL-xRew7UCRrlNCo0PSD-hCExKWnDkimMz-SnyarJmZc6Q_94bw8CvVyPm8=)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFTxjYWhPdsn3QtNxKsfyzS2-OyzcK_TWmCY2haKT-CmFmBjUVwakZkxlgnJ80QWGYQnOqMmXp_Adn3abajVQZ6Ph15d-xw0shG8qnbeeRZmbp9Kh1HETThe0QrewtKXF1zaK7kHnpG929LK3jS06-fLjbLhVBrd4vc21_4MYQxCXoExauIq0mxDk=)
19. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaz-1VhHXm8JzU5ARvZLTvhEXLEkBHxem0fqxXBwuOCSHTHJ50qkLBP_yVldSYFhORCKYm8xC_qs4gN2X0Qpy2L9Er3XsOMf98H5yvn1eJd8lIzeaosxr3tNjco9jbh2LZMUUDY5ZdgnjlTXfStME7QJNqhMsBcq06YB0IvSSEth1IqoErgHRMKy344WNEx-jTxn9otIIwsIac0cqtLqqatWNxDq6x344MEpr-5T9oMM_q)
20. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFG1EbCXFVmXjo7StSUDO3sPJf5OK4e0nfXiD4FTc8Pt7flDllA75O8AFA8A-BRLQTjhi8F2cSYZ4s_p67_e78nUb8XEXEv6KIQtoUKlD6quk8p0cDSlul9I2kO2j2uIGOgxYqno-5PBMBFpeNuZN4=)
21. [ex.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWFarhB2SOFoSTiQLH44vbcCbHnaAzcyczKxhmmmWkIGfMuX6doV1dzKlBq9oAVnBMSCn8VeUTh0Yosd7Z6vpHFUklg0Dmym3GG5H1EXrrHx01GNXec9Lz1aXMjbCvjJh9hbfqgEeWLhMSfylPIU5mOzLwkXM2GnNYjQ==)
22. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIi3WP-5IOae2G2bLRv36AynBdJqdYlhaOCgmq9fJYu2gy-X7PYBaJAvfLyfRWV39_0mCq-ArwYA4-dIQnQXftBhIBMMvlCxAR-ELKyYAORZI29PAqc_SWtEa6DkldTiq20MIPUVRbl6P4tIVq0jWIfFRllnhBoNIBPhHPIjf5LqP5E7XJudMHdl3sgIo4x7xw_8XcwO96qS-sPHi0vUj9PuSCkDjkLEpkUrTKqsIvpxY=)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKTfaqpkL404wDzOWhnMDmLxxUt8-KfsH9cv2BsBGCe9rcPUFM0JSj1uAoJ6a1I6ts0uNeWCqoq9Bj6U0E22vOPP8Mk33TwDfix9CXa-KrwOogt79HHyjlLJFiN7n3_aGTDE11eC74IOtvtl9LNxqv-cqjnydq08UCawXHzJ6x-3NIIQeMUImKbksyDfWBBsSbtPOZnN3nACwdtUqbkPOKUdu9l_FRWbyGDCpbHcDND77GM_dfHNCNGVcEh36kXP3Kh0_3rxVHdOM9eFTnSlj8LoKshNs2qCQKg51sqO8fHp8GE3loq91ETAxnhh65kmmComV17Q==)
24. [ex.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFV3LsRBLzmYMFB4tja9XHrU-ge_2Qr8WrMiMbPmd0iLZ19Fofz1VlUiGHuqNbIe8GX5r9uQjJgETquSKugY_a9JGzOYszYfbjjlvMg9mWRspRrnuQk9ygamZlYHnig2I2x4MFuBNJga6pQeh1t4kJmWgL4UpcjFIujUg==)
25. [icmu.ua](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6vYkxSNrwiXn2jZM0_zaDZakwx53_0AOut_5XB7xTzjVM81kfONqIDvH1oLS72-8mFk91EHWFZgu3-kGSZGZhCsp0wjDjs59cqk6kLPhRX03NWLq9YvDAeH2GHO53vhy0EbOaDhI9o-GI4iVo1RWsQJf8RpDsab1C8ge82aciOScHemFjkNbQ)
26. [hurqualya.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGOucMlSe3sTD4bKZwxux211yd23t8Ajw4__evKksdLSRFS1NmF-ACJsSFuoa3byUiXGn8xBKGkuN3-50mTdLdM7MkeDqGBxv2eih765Ez70PH0cMEMs0JvdWlNBZxGQ906q4fWrKajIQ=)
27. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFu7NJ_E8GGhncyg_5U7O8sG6T0KJF2tObF14Vz5JLLw8AtKbGJN_W9UH3edKrHqFqH_JsUgbFIrxeDQJ-lt6a0GtHkQGNhezz7QZGwHF1xW8tnOPSSJI_EPRoEhsFfVj2Wi2NtvaBNFtIb6t4K32QSmdF60v1Ct2Z_ID3IuUUl60umsxYKGHkCvRVruQB1WbPlyVRq0MVIklIyQNgl5w==)
28. [zenodo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBrP1dmtIBpBBOjIhT9F7-HVpoKehgMtMKL06qfIaU30k8fJv-8I2VyYG3akKU5YXZnGO7ucVu_-JKwl-sg8aSgg0-j-X04NZxTa_IspaOXPbXwIDEtnetDGPcFc0qaMT17e92Z-DhdpBm56WgKpcwh5rBOL64uUG5gmktArnXrYJY649E4n49oQmIZ7OIRwpyW8j2HdXltQ0yTomBbNzYFPUE5XOr0KgHwiOehvdZO6exrTvw7NZU8aRgYEqoVowwOITuj_zOLZmwS3sAig==)
29. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpmRYbJyDRMnndNQeTh0J1NSel4TW8pEVGL75N8XM3NaV2PR38hEKd8jSPWTmnL28aG1KuY6t1QXs0iAUyaWrbd7VHGCBdEcRI2B9akOuRLmYQ55nVlcxCoHXJdZcKJOsHHGdYDPP7ahKw4-iELWsiY7WrILW-qbSQv_p0vIusOIKS12pKQRvBOdvyv0v-JS2UcR47GZmKgFXqJ47bgHxLabI9B3Qj2Ufqp3Kc4rGl5DBQHmDec30W5_N-eHbyUDbeogRnL26LH1cK6YYqTOSl7RB8SxZpgxPAftqVeI0Fqrw0buWXL2PxgxAm4TQDL0t2bZ8krU8KlOLWS0ePV-fufw==)
30. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjl6D8GNTOd3YMHz0YLayxKQycVljfLJSXp7PjA8Ybhu1KhvGJZgdR3ve86s_1iWpjOe12BGf_ZxsfVeH4JzwMHFf7MOH7TKUdA6qiz8vEUgMJXM4PbdUa6vjewH8xp4je53_V4L4=)
31. [ex.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWUQoZqmUghD_vTE2ldKKv8yrQAQfkjxxhxDmBkCgYfBp90OZz3oyh0noLZTNMCizZIsAvtah1iFDIppPyetCq_FqfSHCI-k5pQml6UczUXEbOCBfA56sLSIN26hxl2oVy6keZ55Pq1UAjlVEvc_V7ZEukWChNozbaEoUchDas)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVK-y3HNfg8aAU8RGqWvs64AYhrg4hiFSQhyKYI_RxhaQlooFNFDx0tOUnb2wlFlpN_vaf85lBufAB_weA89sFZsXPwlyP_s-xPC7-Ny45dYLgK2B0_G5e)
33. [aimspress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElnLAvbgfLn95U5Lr1f9tGoTvdELyoND36akQ-S6GFaRa0Fg0ywjoS67xvGihJwNeJZCfUrolkmYZHIKSvSAzFdTXdQV0KBswGztt5jmLOokNV2nJbOvApDvNQcg9MRw==)
34. [blogspot.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyW8XSxi5sgP4H24KKr60fJ8A2msZCUGfeZswD9cpDTZ8aT7OQEdwcHvj8qQrtPrg1FkISo9HnrfXn88r5SorlyLwdhEN8tSDkJOcITLXRZ8--vASiG4RXmR8kd-ietrKfZFh8vEIazB0Dw4PPRvgFxoFy9ZGJf5jmZ8ZsrfQQwHu4)
35. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEloMOgIOb3EVPuJ7xLRecOj-TmKDvdPWymaQD2Yr6ifJT0xsg7P2bHaPYvgwz2d6IlOCm8zaGJoYRfHc6wvAHgccmDp3kNm0ZfSSXVGcNiWHJSS91KPaTR98VoaRBaTVzY5nKk8Ybndw==)

