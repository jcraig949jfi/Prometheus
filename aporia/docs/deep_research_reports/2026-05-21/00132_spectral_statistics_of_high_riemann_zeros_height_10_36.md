# Spectral statistics of high Riemann zeros (height >10^36)

**Pythia queue id:** 132
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdpaW9QYXNlekh2Q3QtOFlQN3R2dmdRbxIXaWlvUGFzZXpIdkN0LThZUDd0dnZnUW8
**Elapsed:** 371s
**Completed at:** 2026-05-21T15:59:58.494254+00:00

---

# Spectral Statistics of High Riemann Zeros: Computations and Random Matrix Theory at Heights >10^36

**Key Points:**
*   **Extreme Computations**: Recent algorithmic breakthroughs have allowed mathematicians to compute the Riemann zeta function at unprecedented heights, successfully verifying local properties around the $10^{36}$-th zero, where the imaginary part $t \approx 8.1 \times 10^{34}$ [cite: 1].
*   **The GUE Hypothesis**: The local spectral statistics of these incredibly high zeros strongly mirror the eigenvalue distributions of random Hermitian matrices from the Gaussian Unitary Ensemble (GUE), providing profound empirical support for Montgomery's Pair Correlation Conjecture [cite: 2, 3].
*   **Zero Repulsion and Large Gaps**: High-altitude computations reveal extreme values of the zeta function corresponding to unusually large gaps between zeros. Empirical data around the $10^{36}$-th zero has identified gaps as large as 5.93 times the local average spacing [cite: 4].
*   **Algorithmic Innovation**: Reaching the $10^{36}$-th zero was made possible by shifting from the standard $O(t^{1/2})$ Riemann-Siegel formula to new $O(t^{1/3})$ algorithms that evaluate quadratic exponential sums in poly-logarithmic time [cite: 5].
*   **Physical Connections**: The precise spectral spacing of these zeros continues to fuel the Hilbert-Pólya conjecture, with quantum chaos frameworks (like the Berry-Keating $H=xp$ Hamiltonian) offering tantalizing, though yet unproven, mechanical models for the primes [cite: 6, 7].

**Layman Summary:**
The Riemann Hypothesis is arguably the most famous unsolved problem in mathematics. It concerns the Riemann zeta function, a complex mathematical tool that secretly dictates the distribution of prime numbers. The hypothesis states that all the "non-trivial zeros" of this function lie on a specific vertical line in the complex plane. Proving this would give mathematicians the ultimate map to the prime numbers. While a full proof remains elusive, researchers test the hypothesis by using supercomputers to calculate zeros at unimaginably high positions along this line. 

Recently, mathematicians like Jonathan Bober and Ghaith Hiary developed ultra-fast algorithms to compute zeros at heights greater than $10^{36}$ (a 1 followed by 36 zeros) [cite: 1]. At these dizzying heights, the zeros are not just scattered randomly; they follow a highly structured, "repulsive" statistical pattern. This pattern perfectly matches the behavior of energy levels in complex quantum systems, such as heavy atomic nuclei (like Uranium-238) [cite: 8, 9]. This report dives deep into the methods used to calculate these high zeros, the massive gaps and peaks discovered among them, and what these strange statistical patterns tell us about the deep connections between prime numbers and quantum physics.

***

## Introduction to the Riemann Zeta Function and Spectral Statistics

The Riemann zeta function, denoted as $\zeta(s)$, where $s = \sigma + it$ is a complex variable, is a central object of study in analytic number theory. Originally defined for $\sigma > 1$ by the absolutely convergent Dirichlet series and its corresponding Euler product over prime numbers $p$:
$$ \zeta(s) = \sum_{n=1}^{\infty} \frac{1}{n^s} = \prod_{p \text{ prime}} \left(1 - p^{-s}\right)^{-1} $$
the function can be analytically continued to the entire complex plane, save for a simple pole at $s = 1$ with residue 1 [cite: 4, 10]. The connection between the zeta function and the prime numbers, first formulated by Euler and later extended into the complex plane by Bernhard Riemann in his seminal 1859 paper, forms the bedrock of modern prime number theory [cite: 10].

The Riemann Hypothesis (RH) posits that all non-trivial zeros of $\zeta(s)$—those residing in the "critical strip" $0 < \sigma < 1$—lie exactly on the "critical line" $\sigma = 1/2$ [cite: 6, 10]. The trivial zeros are located at negative even integers ($s = -2, -4, \dots$). If the RH is true, it implies a tightly bounded error term in the Prime Number Theorem, specifically that the prime-counting function $\pi(x)$ satisfies $\pi(x) = \text{Li}(x) + O(x^{1/2} \log x)$ [cite: 1]. Any zero found off the critical line would induce wilder oscillations in the distribution of prime numbers, upending decades of mathematical assumptions [cite: 1, 10].

### Counting the Zeros and the Function $S(t)$
To understand the spectral statistics of the zeros, one must first define their density. Let $N(T)$ denote the number of non-trivial zeros $\rho = \beta + i\gamma$ of $\zeta(s)$ in the critical strip such that $0 < \gamma \le T$. The Riemann-von Mangoldt formula provides an asymptotic expansion for $N(T)$:
$$ N(T) = \frac{T}{2\pi} \log\left(\frac{T}{2\pi e}\right) + \frac{7}{8} + S(T) + O\left(\frac{1}{T}\right) $$
where $S(T)$ represents the oscillatory error term [cite: 3, 4]. The function $S(T)$ is defined by the continuous variation of the argument of the zeta function:
$$ S(T) = \frac{1}{\pi} \arg \zeta\left(\frac{1}{2} + iT\right) = \frac{1}{\pi} \Im \log \zeta\left(\frac{1}{2} + iT\right) $$
where the argument is determined by tracking the phase from $s=2$ to $s=2+iT$, and then horizontally to $s=1/2+iT$ [cite: 4, 5]. 

From the Riemann-von Mangoldt formula, the average density of zeros at height $T$ is roughly $\frac{1}{2\pi} \log(T / 2\pi)$. Consequently, the mean spacing between consecutive zeros $\gamma_n$ and $\gamma_{n+1}$ near height $T$ is asymptotic to $\frac{2\pi}{\log(T / 2\pi)}$ [cite: 3, 4]. The function $S(t)$ measures the deviation of the true zero-counting function from its smooth average. When $S(t)$ is highly positive, zeros are denser than average; when it is highly negative, zeros are sparser, often indicating large gaps between consecutive zeros [cite: 8, 11].

## Random Matrix Theory and the GUE Conjecture

One of the most profound discoveries in 20th-century mathematics was the realization that the local spacing statistics of the Riemann zeros mirror the eigenvalue distributions of random matrices. This connection bridges analytic number theory and quantum chaos, initiating a field often termed "arithmetic quantum chaos" [cite: 12, 13].

### Montgomery's Pair Correlation Conjecture
In 1972, Hugh Montgomery investigated the pair correlation of the imaginary parts of the zeros, assuming the Riemann Hypothesis. To study the local statistics, the zeros $\gamma_n$ must be "unfolded" or normalized so that their average spacing is precisely 1. The normalized zeros are defined as:
$$ \tilde{\gamma}_n = \frac{\gamma_n}{2\pi} \log\left(\frac{\gamma_n}{2\pi}\right) $$
Montgomery considered the distribution of differences $\tilde{\gamma}_m - \tilde{\gamma}_n$. He proved a theorem regarding the Fourier transform of this pair correlation function for restricted test functions and conjectured that, for any interval $[a, b]$:
$$ \lim_{N \to \infty} \frac{1}{N} \# \left\{ 1 \le m \ne n \le N : \tilde{\gamma}_m - \tilde{\gamma}_n \in [a, b] \right\} = \int_a^b \left( 1 - \left( \frac{\sin \pi u}{\pi u} \right)^2 \right) du $$
[cite: 3, 14, 15]. 

Upon sharing his result with physicist Freeman Dyson, Dyson famously observed that this exact integrand—$1 - (\frac{\sin \pi u}{\pi u})^2$—is the pair correlation function for the eigenvalues of a large random Hermitian matrix drawn from the Gaussian Unitary Ensemble (GUE) [cite: 8]. The GUE models systems lacking time-reversal symmetry and is heavily used in nuclear physics to model the energy levels of heavy nuclei, such as Uranium-238 [cite: 8, 16].

### The Montgomery-Odlyzko Law
The GUE hypothesis posits that all local spectral statistics of the normalized Riemann zeros—including nearest-neighbor spacing, $n$-point correlation functions, and number variance—converge to the corresponding statistics of GUE matrices in the limit as the matrix dimension $N \to \infty$ and height $T \to \infty$ [cite: 4, 17]. This phenomenon, often termed the Montgomery-Odlyzko law, implies that Riemann zeros exhibit "level repulsion": they avoid being too close to one another, much like fermions subject to the Pauli exclusion principle [cite: 4, 18]. The probability of finding a spacing near zero vanishes quadratically [cite: 19].

While Montgomery supplied the analytic heuristic, Andrew Odlyzko provided overwhelming numerical evidence. In the late 1980s and 1990s, Odlyzko computed billions of zeros near the $10^{20}$-th zero, showing an astounding agreement with GUE predictions [cite: 2, 5]. The spectral form factor, nearest-neighbor distributions, and pair correlations all mapped flawlessly onto the GUE curves, cementing the random matrix connection as an empirical reality [cite: 2, 16].

### Short-Range Universality vs. Long-Range Deviations
Random Matrix Theory strictly predicts the *local* (short-range) statistics of the zeros. Over longer ranges in the spectrum, the statistics of Riemann zeros deviate from random matrix predictions. This deviation is due to the underlying arithmetic of the primes. The GUE models do not "know" about prime numbers [cite: 9]. 

Bogomolny and Keating developed a semiclassical approach to calculate spectral statistics that combines the universal RMT limit with non-universal, trace-formula-related contributions [cite: 2, 20]. By using a generalized Hermitian random matrix ensemble and averaging over oscillatory terms related to small prime numbers, they derived precise $n$-point correlation functions that encapsulate both the GUE repulsion at short distances and the arithmetic modulations at large distances [cite: 2, 14]. The variance of the number of zeros in a given interval grows logarithmically, tracking the GUE model initially but eventually saturating and oscillating due to the contributions of the smallest primes (e.g., 2, 3, 5) [cite: 9, 18].

## Computational Milestones in Riemann Zeros

To test the bounds of the Riemann Hypothesis, the GUE conjecture, and the behavior of the $S(t)$ function, mathematicians have continuously pushed the computational limits of evaluating $\zeta(1/2 + it)$. 

### Historical Context
Riemann himself calculated the first few zeros by hand, using a highly sophisticated asymptotic expansion later discovered in his unpublished *Nachlass* by Carl Siegel in 1932 [cite: 8]. This expansion became known as the Riemann-Siegel formula [cite: 8].

Through the mid-20th century, computations were painstakingly manual or utilized early mechanical and electronic computers. Alan Turing designed mechanical gear systems and later used the Manchester Mark 1 computer in 1953 to compute zeros up to $t \approx 1540$ [cite: 11, 21]. By 1979, Richard Brent computed the first 81 million zeros, eventually pushing to 156 million and then 200 million zeros in collaboration with van de Lune, te Riele, and Winter [cite: 22, 23].

The paradigm shifted with the introduction of the Odlyzko-Schönhage algorithm in 1988, which allowed for the simultaneous evaluation of multiple values of $\zeta(1/2 + it)$ by using the Fast Fourier Transform (FFT) [cite: 24, 25]. This algorithm reduced the amortized time to compute a zero from $O(t^{1/2})$ to roughly $O(t^{\epsilon})$ per zero when computing large batches, allowing Odlyzko to reach heights around $10^{20}$ and $10^{22}$ [cite: 1, 25]. Later, Xavier Gourdon used an optimized version of this algorithm to compute the first $10^{13}$ contiguous zeros in 2004, all found to be on the critical line [cite: 5, 21]. 

### The Push to $10^{36}$
While computing the first contiguous $10^{13}$ zeros is a massive feat, analyzing the asymptotic properties of the zeta function (such as the true size of the maximum gaps or the extreme values of $\zeta(s)$) requires sampling at exponentially higher altitudes. 

By 2016-2018, Jonathan Bober and Ghaith Hiary executed a record-breaking computation, evaluating the Riemann zeta function near the $10^{36}$-th zero [cite: 1]. Specifically, they computed zeros in a local window where $N = 10^{36} + 42420637374017961984$ [cite: 1, 5]. At this index, the imaginary part is staggering: $\gamma_N \approx 8.10292 \times 10^{34}$ [cite: 1]. In their computational campaign, Bober and Hiary evaluated more than 50,000 zeros distributed across over 200 small intervals at heights ranging up to $10^{36}$ [cite: 8, 11].

The sheer magnitude of a height like $10^{36}$ defies traditional intuition. As noted in discussions surrounding these computational efforts, if one considers the number of particles in the observable universe (roughly $10^{80}$), a height of $10^{36}$ is a substantial fraction of the way up the logarithmic scale of physical reality [cite: 1]. Verifying zeros at this scale acts as a severe stress test for both the Riemann Hypothesis and the Montgomery-Odlyzko law.

## Algorithmic Innovations for Heights >10^36

Reaching $t \approx 10^{34}$ (corresponding to the $10^{36}$-th zero) is computationally intractable using standard methods. To understand the breakthrough, we must examine the evolution of zeta evaluation algorithms.

### The Riemann-Siegel Formula
The traditional method for evaluating $\zeta(s)$ on the critical line relies on the Riemann-Siegel (RS) formula. To analyze the zeros, one considers Hardy's $Z$-function, defined as:
$$ Z(t) = e^{i\theta(t)} \zeta(1/2 + it) $$
where $\theta(t)$ is the Riemann-Siegel theta function:
$$ \theta(t) = \Im \log \Gamma\left(\frac{1}{4} + i\frac{t}{2}\right) - \frac{t}{2}\log \pi $$
The $Z$-function is entirely real for real $t$, and $|Z(t)| = |\zeta(1/2 + it)|$. Because it is real-valued, sign changes in $Z(t)$ perfectly correspond to zeros of $\zeta(1/2 + it)$ on the critical line [cite: 26].

The RS formula approximates $Z(t)$ as a main sum plus a remainder term:
$$ Z(t) = 2 \sum_{n=1}^{\lfloor \sqrt{t/2\pi} \rfloor} \frac{\cos(\theta(t) - t \log n)}{\sqrt{n}} + R(t) $$
The main sum involves $K = \lfloor \sqrt{t/2\pi} \rfloor$ terms [cite: 24, 27]. Therefore, evaluating $Z(t)$ at a single point requires $O(t^{1/2})$ arithmetic operations [cite: 5, 21]. At $t = 10^{34}$, $O(t^{1/2})$ is $10^{17}$ operations. While $10^{17}$ operations is technically feasible for a supercomputer to perform *once*, it is prohibitively expensive to do so millions of times to find thousands of zeros and isolate high peaks [cite: 5, 25].

### Hiary's Quadratic Exponential Sum Algorithm
The breakthrough that enabled Bober and Hiary's research was an algorithm developed by Ghaith Hiary that reduces the evaluation time of $\zeta(1/2 + it)$ at a single point from $O(t^{1/2})$ to $O(t^{1/3} \log^\kappa t)$ [cite: 5, 21].

The core of the difficulty in the RS formula is the highly oscillatory sum $\sum n^{-1/2} \cos(\theta(t) - t \log n)$. Hiary's method relies on the theory of exponential sums and the Taylor expansion of the phase $t \log n$. By breaking the sum of length $K = \lfloor \sqrt{t/2\pi} \rfloor$ into shorter blocks, one can approximate $t \log n$ within each block by a quadratic polynomial in the summation index $k$ [cite: 25, 27].

This approximation reduces the evaluation of the Riemann zeta function to the evaluation of multiple truncated quadratic exponential sums (often referred to as truncated theta functions) of the form:
$$ F(K', j; a, b) = \sum_{k=0}^{K'-1} k^j \exp\left( 2\pi i (a k + b k^2) \right) $$
where $a, b \in \mathbb{R}$ [cite: 5, 21].

Hiary demonstrated that, using a generalization of van der Corput's method and the Poisson summation formula, these quadratic exponential sums can be recursively evaluated to high precision in poly-logarithmic time $O(\log^2 K')$ [cite: 21, 25]. The algorithm applies a shift to normalize the quadratic argument $b \in [0, 1/4]$, ensuring that with each Poisson summation iteration, the length of the dual sum decreases by at least a factor of two [cite: 25, 27]. The remainder terms—which lack saddle points—decay exponentially and can be truncated efficiently using incomplete Gamma functions [cite: 27]. 

By balancing the block lengths, the overall complexity of evaluating $\zeta(1/2 + it)$ becomes bound by the block sizes, resulting in a computational cost of $O(t^{1/3} \log^\kappa t)$ operations [cite: 5, 28]. This dramatic reduction allowed Bober and Hiary to "parachute" into specific, isolated intervals around $t \approx 10^{34}$ and quickly map the local topology of the zeta zeros, searching for extreme values and validating the RH without computing the preceding septillion zeros [cite: 11].

### Multi-Evaluation and Targeted Searches
In addition to the $O(t^{1/3})$ algorithm for single-point evaluation, Bober and Hiary employed a multi-evaluation method. This allowed them to evaluate the zeta function over a dense grid within a very small local range at slightly more than the cost of a single evaluation [cite: 5]. Using heuristics originally developed by Odlyzko, they targeted regions where Diophantine approximation suggested the terms of the RS main sum would constructively interfere, thereby predicting where $\zeta(s)$ would exhibit massive peaks [cite: 11, 28]. 

## Characteristics of Zeros at Height 10^36: Gaps and $S(t)$

The computational campaign around the $10^{36}$-th zero was not merely to check if the zeros remained on the critical line—they did—but to probe the spectral statistics at extreme limits. A central focus was the interplay between extreme values of the zeta function, large gaps between zeros, and the $S(t)$ function [cite: 8, 11].

### Extreme Values of $\zeta(1/2 + it)$
Bober and Hiary explicitly targeted regions where $|\zeta(1/2 + it)|$ (and equivalently $|Z(t)|$) was expected to be exceptionally large. The largest value they found was $Z(t) \approx 16244.8652$ [cite: 11]. (Note: subsequent distributed computing projects, such as the RS-PEAK algorithm run on the SZTAKI Desktop Grid by Tihanyi et al., found a slightly larger value of $Z(t) \approx 16874.202$ near $t \approx 3.106 \times 10^{32}$, underscoring the extreme volatility of the function at these heights [cite: 29, 30]).

### Zero Repulsion and Large Gaps
The GUE statistics dictate that zeros typically repel one another, making zero gaps (very closely spaced zeros) rare. Conversely, unusually *large* gaps are also statistically suppressed [cite: 12]. However, when targeting extreme peaks of $Z(t)$, an undeniable correlation emerges: massive values of $Z(t)$ are strictly accompanied by extraordinarily large gaps between the adjacent zeros [cite: 5, 8].

Bober and Hiary summarized this phenomenon as a compensatory mechanism: "It is always the case in our computations that when $\zeta(1/2 + it)$ is very large there is a large gap between the zeros around the large value. And it seems that to compensate for this large gap the zeros nearby get 'pushed' to the left and right" [cite: 8, 11].

In their dataset, they observed a specific gap between zeros that was **5.93 times the local average spacing** [cite: 4]. For a gap of this magnitude, the surrounding local statistical configuration is heavily distorted. The immediate neighbor gaps surrounding the massive 5.93 gap were observed to be highly compressed—approximately $0.32$ times the average spacing [cite: 4]. If a hypothetical gap were 15 times the average spacing, its immediate neighbors would be squeezed to $0.1$ times the average, gradually relaxing back to the mean spacing of 1 further down the line [cite: 4]. This perfectly illustrates the "spring-like" repulsive forces modeled by random matrix theory and the Dyson gas model.

### The Behavior of $S(t)$
The function $S(t) = \frac{1}{\pi} \arg \zeta(1/2 + it)$ is intricately linked to these large gaps. Since $S(t)$ counts the deviation from the expected number of zeros, an isolated large gap of $K$ times the local average spacing mandates that the value of $|S(t)|$ must exceed $K/2$ [cite: 4]. 

In the targeted intervals around the $10^{36}$-th zero, Bober and Hiary found extreme values of $S(t)$. Prior to their computations, the largest observed absolute value of $S(t)$ was roughly $-2.9076$, reported by Gourdon [cite: 11]. Bober and Hiary shattered this record, observing 11 instances where $|S(t)| > 3.1$, peaking at $S(t) \approx 3.3455$ near $t \approx 7.7573 \times 10^{27}$ [cite: 11, 28].

A consistent topological trend emerged in the zeta landscape: surrounding a massive peak in $Z(t)$, the function $S(t)$ is typically very large and positive immediately *before* the large value (indicating a high density of zeros "pushed" to the left), and becomes very large and negative immediately *after* the peak (indicating the zeros have been pushed to the right) [cite: 8, 11]. This effectively carves out the barren, zero-free gap that allows $Z(t)$ the "room" to continuously grow to its massive maximum without crossing the zero axis.

The growth rate of $S(t)$ is bounded by analytic number theory. Unconditionally, it is known to be unbounded, but under the Riemann Hypothesis, Littlewood proved that $S(t) = O\left(\frac{\log t}{\log \log t}\right)$ [cite: 5, 15]. The current best explicitly calculated bounds are $|S(t)| \le 0.111 \log t + 0.275 \log \log t + 2.450$ [cite: 5], and limits involving the constants $\frac{1}{4} + o(1)$ have been achieved [cite: 5, 11]. The values of $S(t) \approx 3.3455$ at $10^{27}$ align well with these slow-growing logarithmic envelopes, preventing the "tightly packed spikes" that some mathematicians hypothesized might violate the RH at extreme heights [cite: 8].

## Lehmer Pairs and the De Bruijn-Newman Constant

While large gaps isolate the zeros, another critical spectral statistic is the occurrence of unusually *close* zeros. These are known as **Lehmer pairs**, named after D.H. Lehmer, who first discovered a pair of exceptionally close zeros near $t=7005$ [cite: 8]. The study of Lehmer pairs at extreme heights is directly tied to the analytical proof strategies for the Riemann Hypothesis via the de Bruijn-Newman constant, $\Lambda$ [cite: 8, 31].

### The Backward Heat Equation Deformation
In the 1950s, N.G. de Bruijn, and later C.M. Newman, studied a continuous deformation of the Riemann $\Xi$ function (a modified, entire version of the zeta function). They introduced a real deformation parameter $t_{dbn}$ into the Fourier transform definition of the $\Xi$ function, creating a family of functions $\Xi_{t_{dbn}}(x)$ [cite: 31].

The evolution of the zeros of $\Xi_{t_{dbn}}(x)$ as $t_{dbn}$ changes is governed by the backward heat equation [cite: 31]. De Bruijn and Newman proved the existence of a real constant $\Lambda$, now called the de Bruijn-Newman constant, such that for all $t_{dbn} \ge \Lambda$, the function $\Xi_{t_{dbn}}(x)$ has *only* real zeros (which corresponds to the zeros lying strictly on the critical line). If $t_{dbn} < \Lambda$, complex zeros exist [cite: 31].

Therefore, the Riemann Hypothesis is precisely equivalent to the statement:
$$ \Lambda \le 0 $$
Newman boldly conjectured the complement, $\Lambda \ge 0$, famously stating that "the Riemann hypothesis, if true, is only barely so" [cite: 31]. Recent collaborative projects (like those by Brad Rodgers and Terence Tao) proved Newman's conjecture that $\Lambda \ge 0$, establishing that if the RH is true, $\Lambda$ is exactly equal to 0 [cite: 8].

### Bounding $\Lambda$ with Spectral Statistics
How do high-altitude spectral computations interact with $\Lambda$? Csordas, Smith, and Varga demonstrated that the Ordinary Differential Equations (ODEs) governing the motion of the zeros under the heat equation imply that if two zeros are incredibly close together, they exert a strong repulsive force on each other [cite: 31].

If a Lehmer pair (two zeros $\gamma_n, \gamma_{n+1}$ with an unusually small gap) is found, this tight spacing can be leveraged to compute a strict lower bound on $\Lambda$ [cite: 8]. An exceptionally close pair, known as a "strong Lehmer pair," pushes the lower bound of $\Lambda$ infinitesimally closer to zero [cite: 8]. 

Computational campaigns at heights like $10^{36}$ or $10^{20}$ actively search for these Lehmer pairs. By evaluating the Riemann-Siegel formula and using the $Z$-function to track sign changes, researchers have compiled extensive lists of Lehmer pairs [cite: 8]. Soundararajan's Conjecture B posits the existence of infinitely many strong Lehmer pairs as one goes arbitrarily high up the critical line [cite: 8]. If this spectral property holds true—that no matter how high we search, we will continually find tighter and tighter Lehmer pairs—it strictly forces $\Lambda = 0$, thereby proving the Riemann Hypothesis [cite: 8]. However, verifying this requires searching through datasets of billions of zeros, necessitating the ultra-fast $O(t^{1/3})$ and FFT-based algorithms [cite: 8].

## Quantum Chaos and Physical Interpretations

The striking confirmation of the GUE hypothesis at $t=10^{36}$ reinforces the perspective that the Riemann zeros are not merely numbers, but behave exactly like the resonant frequencies or energy levels of a physical system. This is the domain of the **Hilbert-Pólya conjecture**.

### The Hilbert-Pólya and Berry-Keating Conjectures
In the 1910s, George Pólya and David Hilbert independently suggested that the Riemann Hypothesis could be proven if the non-trivial zeros $1/2 + i\gamma_n$ corresponded to the eigenvalues of a self-adjoint (Hermitian) operator $H$ in a Hilbert space [cite: 32, 33]. Since self-adjoint operators have strictly real eigenvalues, this would guarantee that all $\gamma_n$ are real, proving the RH [cite: 33].

In 1999, physicists Michael Berry and Jon Keating proposed a specific semi-classical Hamiltonian to satisfy this: $H_{cl} = xp$, where $x$ is position and $p$ is momentum [cite: 6, 7]. Because the classical trajectories of $H=xp$ are hyperbolas ($x(t) = x_0 e^t, p(t) = p_0 e^{-t}$), the system is unbound and chaotic. When quantized, with appropriate boundary conditions to make the operator Hermitian, the dynamics of this chaotic system exhibit periodic orbits whose lengths correspond to the logarithms of prime numbers ($\log p$) [cite: 6, 7].

Berry and Keating showed that the spectral statistics of the Riemann zeros (such as the pair correlation) map perfectly to the semiclassical quantization of this chaotic Hamiltonian [cite: 6]. The Riemann-Siegel formula itself can be physically interpreted as a relationship between long and short periodic orbits in this chaotic system, providing profound insights into quantum spectral fluctuations [cite: 6]. The confirmation that GUE statistics hold robustly even at the $10^{36}$-th zero supports the assertion that this hypothetical "Riemann dynamics" is fully chaotic, lacking time-reversal symmetry, and governed by random matrix universality [cite: 6, 16].

### Dirac Fermions and Rindler Spacetime
Alternative physical realizations have also been proposed. One recent model involves the propagation of a massless Dirac fermion in a region of Rindler spacetime, subjected to delta function potentials localized exactly at the square-free integers [cite: 32]. By tuning the self-adjoint extension of this Hamiltonian to the phase of the zeta function on the critical line, the Riemann zeros emerge as physical bound states of the fermion [cite: 32]. 

In this physical framework, the semiclassical energies $E$ (in units of Planck's constant $\hbar$) correspond to the Riemann zeros, while the spatial cutoff parameters map to the Planck length. While these models do not yet offer a mathematical proof of the RH, the unbroken continuum of spectral statistics matching physical quantum states from $t=10$ to $t=10^{36}$ suggests the connection is fundamental, not coincidental [cite: 32].

### Arithmetic Statistics and L-functions
The implications of these spectral statistics extend beyond $\zeta(s)$ to a wider class of functions known as Dirichlet L-functions and generalizations. In the context of function fields (where the Riemann Hypothesis was proved by André Weil), Katz and Sarnak demonstrated rigorously that the zero statistics of families of L-functions mirror the eigenvalues of random matrices from the classical compact groups $U(N)$, $O(N)$, and $USp(2N)$ in the limit of large finite fields [cite: 20, 34].

For the Riemann zeta function itself, its zeros match the statistics of the Unitary group $U(N)$ equipped with the Haar measure [cite: 20, 34]. When one studies the "murmurations" or pair correlations of these more general L-functions, the Random Matrix Theory models formulated by Keating and Snaith accurately predict not only the main terms of the correlations but also the detailed arithmetic correction factors (the lower-order terms) [cite: 17, 20, 35]. The computations by Bober, Hiary, and others at extreme heights ensure that these correction factors behave exactly as the hybrid RMT-Arithmetic models predict, confirming that the "music of the primes" is tuned to the laws of quantum chaos [cite: 6, 36].

## Limitations and the Future of Extreme Computations

Despite the success of analyzing spectral statistics at $10^{36}$, severe limits constrain how much further numerical verification can go. 

### The Horizon of Computation
Odlyzko has noted that determining if the Riemann Hypothesis fails via brute force computation might be impossible if the first counterexample exists at an astronomically high value, such as $10^{10^{10}}$ [cite: 1]. As a practical threshold, even $10^{100}$ might be reachable in the coming decades with significant algorithmic leaps, but values like $10^{1000}$ will not be verifiable before the "sun becomes a red giant" [cite: 1]. The number of arithmetic operations performed by all computers in human history is on the order of $10^{23}$ to $10^{25}$, meaning comprehensive, exhaustive checks of all zeros up to $10^{30}$ or $10^{36}$ are physically impossible [cite: 8].

Therefore, modern computational number theory relies on the targeted interval sampling utilized by Bober and Hiary [cite: 11]. By using Diophantine approximation to predict where $Z(t)$ will be exceptionally large, and deploying the $O(t^{1/3})$ quadratic exponential sum algorithm, researchers can sample the deepest anomalies of the zeta landscape [cite: 28, 30].

### Outstanding Questions
1. **The Maximum Growth Rate of $\zeta(s)$**: While Bober and Hiary found $Z(t) \approx 16244$ near $10^{32}$, it is highly unlikely this is the absolute maximum for that range. Extreme values are incredibly rare and highly localized. True bounds on the maximum size of $\zeta(1/2+it)$ remain conjectural, though theories based on Random Matrix Theory combined with models of random primes suggest specific growth envelopes (e.g., the Fyodorov-Hiary-Keating conjecture) [cite: 5, 15].
2. **The Exact Value of $\Lambda$**: Finding stronger Lehmer pairs to push the de Bruijn-Newman constant $\Lambda$ exactly to 0 remains an ongoing computational quest.
3. **The Illusive Operator**: A rigorous construction of the Hilbert-Pólya operator $H$, whose eigenvalues are exactly the Riemann zeros without requiring ad-hoc tuning for each zero, remains the Holy Grail of arithmetic quantum chaos [cite: 32].

## Summary and Conclusion

The numerical exploration of the Riemann zeta function has traversed vast computational landscapes, from the manual calculations of Riemann and Turing to the algorithmic masterpieces of Odlyzko, Schönhage, Bober, and Hiary. The recent mapping of spectral statistics around the $10^{36}$-th zero (at heights $t \approx 8.1 \times 10^{34}$) stands as a pinnacle of experimental mathematics [cite: 1].

By leveraging the $O(t^{1/3})$ algorithm to evaluate quadratic exponential sums, researchers have bypassed the $O(t^{1/2})$ computational barrier of the Riemann-Siegel formula [cite: 21, 25]. The data retrieved from these stratospheric heights confirms that the Montgomery-Odlyzko law holds firm: the zeros of the zeta function repel each other in strict accordance with the Gaussian Unitary Ensemble of Random Matrix Theory [cite: 3, 4]. 

Furthermore, targeted searches have revealed the extraordinary topology of the zeta function when driven to extremes. Massive peaks in the $Z(t)$ function, reaching values over $16,000$, are mathematically intertwined with vast, barren gaps between the zeros—some expanding to nearly 6 times the average spacing [cite: 4, 11]. These gaps are sculpted by the wild oscillations of the $S(t)$ phase function, which spikes positively to cluster zeros together, then plunges negatively to tear them apart [cite: 8, 11]. 

Through these extreme computations, the Riemann Hypothesis has not only survived but has revealed a deep, symphonic connection to quantum chaos, statistical mechanics, and random matrix theory. While a formal proof of the Riemann Hypothesis remains unwritten, the spectral statistics at height $10^{36}$ provide the strongest empirical evidence yet that the prime numbers conceal a universe of profound, chaotic order.

**Sources:**
1. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG90gHW8oal0yMjsNhIrgosobJKznUbrlOhJxN5GBzynK8YmXvpcjuBkrEape9k7lhQ86YNVqleD_JzxIarhsHtJbqKe0d2m_bg9HsiUUppUgPEp4Idy4S_-HRtx8UtH-nURztednXJ78mHTaIq_M-RbbxYQe2WqtjDFgOv6py8Fcesi4ZZvB_wK7acS_4zHw==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUSmmLyKylCLgVcxX0OJAPoh5yW9Y8zzP2suy62rcy9QuQmrGW5KfK9Me9t5Q94axfj0_Bc6zl8vA6LYRXgFKk3kBrvvu00ILdMkhgCEOiLAd7Qz48)
3. [umontreal.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELT8ZHqnIMIE2AUh55HPto1Oi2AB81UKY0DWmgXZuQwJDLfWYmuaojbWomx4kE765m6Ki70ka8vt9eJJmrHIQjUNB8oBIYp-2WXlM3JpEoK9CnMJD6Lm5Jbzu-Kmk0PlX-Ig==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcW74V9RfavDfqS4SD3gNW-veWRGvvZaZINdvXkun0wkZ0NJkAre2luVQOZHNdHjjccjw3uJ9u5TliWdImFKpNSWEB4izLZYh8quUXxeTvaUCvSWulKiqAdA==)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnfVWHLP5qR_v0h_Ns7pRtbu64Z1z4epBLGVlj0xXSzbuylAPwApcm03tgIQYFIf_Ii5fSpB0zgTkVNHDAoR222hhJgEAqIJoWRlY4k_QcTUdQY9AyrJJGuMmt2SdxxJWe97Cax5HH40Eo2Gkc-ntvCpnivvAOmIn0Ht06527V1UfIg86VIpd5mCCZGWRZJkfFbVRhwI2h-OmZ9PcxzYEWnurVAeBVdLIPiVs=)
6. [ex.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkNkdjifK8D_9wHp-ainmjbiNyZbqNJwgn8VBmNCl17M5ukb3NZVKXrIoxo4RbpVneptQ6HpkxbuNWr5M0TRxZPaQmVSSYzd_Rny9rDyQqESi6wkTBRLgy2kDvaRofy5FJRlSpOvpZF_sCKkgi8xaij5Z5t-E9wIGzAbvuPVw=)
7. [ex.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGi2tF3QUmG9U0TJz6983Un53IF9flOO9gK25BGflVW8RYNrtbv99A_VUQySEUGqLqqnQoVfEU6Xha_izjtkhpVN876ihJGk2nsCxn21uVmgiFTsoRQekwJ7sg39goH2fX2gjpnKSvvRBPYI_wK4Svn7ZE3M_4=)
8. [scienceforums.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7DbNTh9Cm-6IPmY9SU4_bn6rf41AWIBObSkzdV_x8CypElvPlRgX7z_UdTdzbZPeHU53WIUq4DeKk__pZM6ejq6uGsLHsfEmN2SIrwcRKqxBknzHW6ajHGuyWYifvtjiF_d2XJcrRkDYpH0PMf2zZUyO6o5-ycdYi3sdk0V35KUemSA7x6vDHG25s4WR9bCoeq95f29WoAJ0ql49gD07xdtY=)
9. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8KM6KulEC1yN8_EcDOsFssw4FJ7OTOznFXC0cQ7cZDlPUMx-MRd-l7JZIlILyCvLJAmHfC8_tFqzLfeF67TPSD7-Yr1efkS5UbQ1oWJtoA-0TRHvfU92yCQy4uktLW-ehoQ==)
10. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSyiAlrSF7aRCdcAoae2ZxyAEhnOmt-pHqCOKhcOVeVobJCrl_zuR7kA2fHZhDgSByMKLOX-zizX2iwLwwnup0Efd7J3j5ukYTpdHy54ZZ2C0mUbmZSNO_SQY5-eW1YYqnVt9eTSQ=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvhmHEAqswksnRR960AorWIBFixjswSCHBuEVaGRREE2YdoKZFGUzqSGXlTGgDjJhCEevz0NNc6AlsIAvIVReFR5Q8oT4Oa48sOf8kQrEGCuTdqjo6nQ==)
12. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHovofZKdnQ0pv4CXutBfJQMW9tGAD3pyoKjiVFKZtP6luIdJIH_vB6EnW1yxXfExisV-IiMwQPZF16HCiT79vCzx8rVXzfN2l1xRIL791kibltjAWgfe1eRctp83m9yFtxS02acOwfILYRZWRKpP8S1ULyUAcLxgCqS9tQBv3XtEA=)
13. [eolss.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_QGqyA-Yx_7rALYHaEA87RvtkRddND3b2qGoH6zAOMuHj1hMWpWNLS9rtBQdDXaDstUmRhyZHiy87FPW0xcL7QJ_CmmXB407CY6XWr3qlwnxrddQJmVzBel4Wvghc-mScCab2_ZntGDLHVoM=)
14. [ex.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3ECmdyrW8zPEI1Bkf5w2LNK9iFvwNyplm0vJfnq-Aoi8eMT2ptAXYY8sCwnmKwi0IT3Y3NtoL8ZzMZbrsTlOnOvvI_Tdzv_KtPlHPZPZAEhjuG0Fgp6ZT6frVj5v3XuErsgD_N-CbhZRASA0Ts8PXUH8cjXYF)
15. [nyu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6mc1yQfxnnS3pRmsRF6uWvXMhXE2gPXumILwxX6gp47ndZKexZpQcF9pXP4NrDZWBT9lK1SM2FhxjLSDZ1dQnyS2zmE9R3T5mYiLo1oigpeDIyAM8YspUc8wLJ8rXzJPMLTT-3uMOAUyeUlI=)
16. [uni-erlangen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrDT9yerNSROFOKWIbZwhtlu8LDTzsga7j5346FOxH5hNhTiV001uM-IsBgIU3392sPY6EMHdEAF7XH0TR_rNOBeFRIkQyW5c0_2z_yma5OD2OJRbX5Pm3HzldtHOIVX0JS7IJhX2ioQ2AGWZsWrFoV1dk03eIwJQ3k4MvGVYSr_RtmzEOEGbzsBqsn05mCjk=)
17. [shiftleft.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEf0RJBmM08UxJpI1jb3Hg1NjSatGc6leaWBeHxWTGWg6cZIJrWcVcZAdioBtqt9oTu9I0BIiuTf-TcUzEeA7ue4HkooSdDg-teH4LiFS0246q5ohnECMtkruo83C7cM1HBaSBVtu56oiVhNpbBAD8YhCgbVVrXWGduiwhYK43Nu1fjCgUiQtJkVA==)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbTGeNvkUV8tXhlMEXte8g4nQtyeMKdQSOPaqymM_Igaw-PsRTA8s31LYOEB0YXGKyfWZ8VMsLzRJVfrOFDnt5hC0rgDtsLjIFNTbQFj41AUAtMZjLczkYqwuDiGBlGc7BrCTop6AAN7FvkggSeMr7yaEE1dR38n47yZZOzXFXupqEUDGaXczz6lw_Zap5V49oU9oBWUR0XxoS_8aTi_rfdirGHVZ0xaLDgbNhLPMokf0=)
19. [williams.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2YriIkTw4VnbbFQS8URG_PpyC0TTNF6CDDgfg_2dfAwsaUZOon31ghrSGKsD3fhsoiIjT_3qOLt5uqWjzqapY1xhVV1yDsSF8PRsg9jS6iNfCnVvalu3nTQFjkpxChFQSyGd_G0xJMa6tpQF35TXEfq-W6v_ZL70RSS47NkXVD6fpAhvWmg22Z5y4NV8IA2mOaPE=)
20. [dtic.mil](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUoq_1OYihA0XUCgTQcEB-4Ewhjum0_zqN73dm0hy3mfHIB_k3Q9Ee5vlCyBidQbIYB9i_uGe6ZqQp8lsj9fUMA_eMMC5Ybk6bb1gZKHo9nmPDS7BjH146P77ws04puXYx9RK8)
21. [bris.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0zorSR6PbWRtNqM3ks-hWwaCCHJBuol0hWH35w5Hk7X5W0cm-i2eCtUGE0X6e6P3uS5dNu4iGTpFQVP7zd_E9_u4pgYptwxwZyVZXRB9D7HhErT1bJItWQ9fkXXtVE1wDyXAkx9OdUied4daE2O7o2C9hZ7XrE1jcFqc4jO8=)
22. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG30vNnYPF_x-JWvXJ4B27_nPsmEYj7mTm9VGdgYkLMzagqy0es-WEj5hFKM3ySrAhVVge7iQazceC5XYiMkcbiX0e82HTcpvNSAObiDRGe8N7VtbApQM5DBo8=)
23. [tsu.ge](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFj-E3WN0Yw0tpuqItkB-kJAHTFCVZGLLZAuKiNDsoRUGQYpT7QW5GjuuPChs-RTElVrG6UfUL0PJ77yywhJXGo6qE8G7d0uRzy85xEiamQGJRN-clPxaWXtOGyU1afp60aSLlWIcdgLjuWsGqN9SarDSn3Tg==)
24. [quora.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDf9JJo-agPn0_W5B5QUXu9kj7pxsOFbg3dvy_lZtLnZ5EFfMsX-62743bewvhd1wXUxdCwAu2dwSdxVF7Etcmd48YhpMZgtriBN9sqrqA7fIpEUcXGETK2SL6asQyjbsgkBH0VbEuYHh3Fy_E6cH5wI3U5l9bJWyh-aPkL5LvfJwuqfaYkoz_mAKtbnPa6jRN1_jJYfyaUhQGMpg=)
25. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIujbYO-iSbr8cxZgFUD5S82MEDKKhjejukG0d7dcnnfMO6DXwEIa0t_kMGk2k-h36_tdfOPzf5Se0odQB8EBwp_sA2t0yImCiPOQNbbQxPgOUY5oYCout0vASt_0WucHaBeTImUBt59AuWXURyPnmTup41eVFV_lV7OZjzI8SNkjUdw==)
26. [uic.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHaZaZN6mXNA0u7TunR5hEYW9OC71jgJGTR6zvlCAeUiq9HuygRmykuIU74H4Jhafsvu7B7D2BojodsI6naHFt4zEuy4-CssSZZU7qdU7X7447rjzhX4GMla4Eu569FduJjTETvtC6R4liXCtUu2sfJiEYfdw9jefI)
27. [osu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFagU39qmG_DIRbLYuEry65mJNP82C0ubq4HHyb17KTESMkr45rSTgpYHgokOoGxP2qrU92CRWmbqvmKVlnN_6ovs2ttbXeG8AMVweVdMPiBw0daaNau-7bgmNLEFQe40IPjg==)
28. [osu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHffSYI7HLlAB1cCBS5wojuqWBCH3GHOZ1re-T66kpV1gKTrrhJOarxfKvyaYWiPg7dc0z7-i21rUUusv7DCvuJd0OiBoV5yLG64Y60hvjwekCPk7JR61WzPP4FeltOTEgCgLkjpaZSQI9u)
29. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgew2E0cz-GWcmhdvUFMlOcDeR8TcxYECScObfg3cKBovkiMR_SlDpiWDoKKwn-E1L8a3wL5J4dNJXv5Ml2eEJ89oX_MiHG8WHxEbMxsXc1OYx7XiJZoAxGhUITJ1N4O9yF-WLmQehsFhH7h8oNS2HH3ZHB0W_J4M-KNZhchAFQ1YWdDKUWjQeZGoJQn_a0Y6u9Y-nlxDAItsivibKFUBUZ06nJzBNDWbQul15Ck_P92QuNBj-2bCYl8DVdfxnuDqJJg==)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjqox-kYXj8I0LeIR1qDV4plWuqj3pN_QAdBtctRQiht02KM-KTW3lVn6sFuRnAVB2zxnIwWeMzEWHRcMpvphWRJx0SE3vJtGW6HP6mhMVLiP4jrn2d1RE3ssRe0p1H2LcJlOYoWYzS2dvVGW1f44nyiJ3dmyRqJSHcNBm82W37BnHAmUoNHH90Cd7uta-Xt7EtWOrv8JLE1QQKmpUQJo3eo11EBI2JNefasmyud0yPVXnDdHOC5CU)
31. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNeLtjV1o7gYbLWa3XfavM7IFbf1sycuazfLbcfslsyhEofNhrOMgYa6UMq88DaQSayTp49RYfwIGFvWY8wiXwD-tczwSfKx8adcGGQGeHz5O2keUmgIEKyRNrI_4RQeAFkNVM1RuK-m6e32Q0kb0-2k-31xk_MidLUoHh_jZz9Pgr30hZE_cXivifXcoi-iojTTOJdAfUr9pEhLObZ-WGv03P73sn2L-n8tUKQKr01g==)
32. [cern.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCR920uOmC04kpxitgIZpTh4CxybLqKRXUc9Mxoni6uik6BfL93ygfSyJB1jlIvYjRPYx8yUndkSO6DMrx5T0kuNPuXePu2MPl5oVOWSYqDgD0rVoQFszdYQzhR2bpptJiACVbgpjvcNJhgHzBh5nzzLsjUaJTMteixNZwD8k=)
33. [ex.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaeF_wA7KRcaPPHvNDvBGKPeHQ-Lmw3UX0_N08w30q_LqcyFf20a0OJksxUW3V-caT8FgBvzXBI4DrpZmpEorZNteWQdqyMbU81MgW8IxaNgBdVtTN5t6GwHMNTGmiRKj2EjNoh1wjLHZeJVVGR5S-BQ2oh0yHXOo=)
34. [bris.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRPBDpPKBl8MlKi1TeeQRQUGGMa-jAuYC5P15h0JdaVK2MHShuv6tUHfpsHXIFAvFa52AQmIlEpGHodk9BapW_1D0gDnGDFUOM8GIcTa0PovBSzh0djBT_NUWnsQQxSWK0Eh6RFp6o1Km2ltJv3-aQqT-IjF2iQilJ_A==)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFP9laYpBJgkIY77miZYNIXZ_vym5pv7b_g2vSgsLCVoyCjE3qcXCZXTyWZihFqik5qk3Hub2OVfDe5FsRzWbkJglhWvXWG7F1pBhnFTZ-aY60ZFGwJpg==)
36. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqj4Mn4hBW-Jov-cJjOcwWUpXbpRfokIl4TA6TOK8vxOMRzRy_o_ETHbaYCm48qWjZwZPhZiZY0jbGWEhQdqjK8oULk7Uc3QhWGn6xRGKsmvjDaHNCZ5dHb5tPWJcktLiDJJ4cHS9IWQ==)

