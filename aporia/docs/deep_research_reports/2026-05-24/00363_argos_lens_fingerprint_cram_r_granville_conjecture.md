# Argos lens fingerprint: Cramér-Granville conjecture

**Pythia queue id:** 363
**Tier:** T5
**Priority:** 5
**Requested by:** Argos
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdFYXNTYXVxX1BQZWFfdU1QZ3RPbTRRURIXRWFzU2F1cV9QUGVhX3VNUGd0T200UVE
**Elapsed:** 303s
**Completed at:** 2026-05-24T07:44:02.328821+00:00

---

# Primary-Literature Lens Fingerprint for Open Problem MATH-0369 (Cramér-Granville Conjecture)

**Key Points:**
*   Research suggests that the classical probabilistic framework for understanding prime gaps, formulated by Harald Cramér, may be fundamentally incomplete, as evidenced by cross-disciplinary models from physics and information theory.
*   The Cramér-Granville conjecture traditionally centers on whether the maximal gap between consecutive primes bounds near \( \log^2 p_n \), and whether the governing constant is \(1\) (Cramér) or \( \approx 1.1229 \) (Granville).
*   Recent theoretical proposals apply methodologies from dynamical systems, information theory, and the renormalization group to reframe prime numbers not as randomly distributed independent entities, but as deterministic, emergent phenomena.
*   It seems likely that integrating these unorthodox lenses will shift the axis of disagreement from "probabilistic expectations" to "deterministic structural constraints."
*   While these novel frameworks offer mathematically rigorous analogues, they remain largely theoretical and computational, highlighting the immense complexity of resolving open problem `MATH-0369`.

**Executive Summary**
The distribution of prime numbers has long been modelled using probabilistic heuristics. Open problem `MATH-0369`, commonly known as the Cramér-Granville conjecture, epitomizes the struggle to bound the maximal gaps between consecutive primes. Traditional approaches rely on the Cramér random model, which treats primes as independent events. However, multi-perspective methodologies drawn from advanced physics and computer science are currently being applied to this problem. By projecting the prime sequence through the lenses of Dynamical Systems, Information Theory, and Renormalization Group flows, researchers are uncovering profound alternative architectures. These frameworks suggest that primes may behave as deterministic states of complex topological spaces, optimal signal compression artifacts, or scale-invariant geometric fractals.

**Methodological Disclaimer**
The findings synthesized in this report draw heavily upon recent preprints, computational frameworks, and cross-disciplinary theoretical physics analogues published between 2018 and 2026. Given the deeply unresolved nature of `MATH-0369`, the verdicts reached by these candidate lenses represent cutting-edge, yet potentially controversial, paradigms that challenge orthodox analytic number theory.

## 1. Introduction and Formalization of MATH-0369

The study of prime gaps—the difference \( g_n = p_{n+1} - p_n \) between consecutive primes—represents one of the most fertile grounds for unsolved problems in mathematics [cite: 1]. The Prime Number Theorem (PNT) establishes that the average gap between primes near \( x \) is asymptotically \( \log x \) [cite: 2, 3]. However, determining the behavior of the *maximal* gaps has proven to be profoundly difficult. 

In 1936, Harald Cramér proposed a probabilistic model, often referred to as the **Cramér random model**, which operates on the heuristic that the probability of a natural number \( x \) being prime is approximately \( 1/\log x \) [cite: 4, 5]. Under this assumption, treating prime occurrences as independent random variables (like coin tosses), Cramér conditionally proved that the maximal gap should satisfy:
\[ \limsup_{n \to \infty} \frac{g_n}{\log^2 p_n} = 1 \]
This became known as **Cramér's conjecture** [cite: 5, 6].

However, Cramér's model fundamentally ignores the deterministic divisibility constraints inherent to the integers (e.g., primes greater than 2 cannot be even, altering local probabilities) [cite: 6]. In 1985, Helmut Maier proved a theorem concerning short intervals that contradicted the pure Cramér model [cite: 5, 6]. Building upon this, Andrew Granville formulated a sophisticated refinement. Granville suggested that the constant governing the upper bound is not 1, but rather a value modified by the Euler-Mascheroni constant \( \gamma \), proposing that the limit supremum is \( \geq 2e^{-\gamma} \approx 1.1229\dots \) [cite: 4]. Thus, the **Cramér-Granville conjecture** posits that for some constant \( M > 1 \), \( g_n < M \log^2 p_n \), with the dispute largely centering on the exact value of \( M \) [cite: 1, 4].

The problem is further complicated by competing heuristics, such as **Firoozbakht's conjecture**, which proposes that the sequence \( p_n^{1/n} \) is strictly decreasing, implying an even tighter bound of \( g_n < \log^2 p_n - \log p_n \) [cite: 7, 8]. While empirical evidence up to \( 4 \times 10^{18} \) supports Firoozbakht's bound, it is widely believed by analytic number theorists to be false because it severely contradicts the probabilistic models underpinning the Cramér-Granville heuristic [cite: 9].

To break this theoretical gridlock, the Argos proposal utilizes a multi-perspective attack methodology (`D:\Prometheus\harmonia\memory\methodology_multi_perspective_attack.md`), projecting the prime sequence through disparate scientific lenses (`D:\Prometheus\harmonia\memory\catalogs\README.md`).

## 2. Lens 1: `STANCE_DYNAMICAL_SYSTEMS@v1`

The Dynamical Systems lens treats the sequence of primes not as a static set of integers, but as the time-evolution of a complex system. Under this framework, the sequence of prime gaps is viewed as the "derivative field" or velocity of the primes, similar to velocity fields in turbulent fluid dynamics [cite: 10].

### 2.1. Attempt 1: Iterative Maps and Cohomological Structures
**Source:** Marzena Ciszak (2026), *Iterative maps emerging from cohomological structure of primes* [cite: 11, 12].

Researchers have recently shown that prime gaps at different separation distances follow deterministic functional relations that can be described by an iterative map [cite: 11]. By applying difference operators across the sequence of primes, Ciszak demonstrates that prime numbers are characterized by long-range correlations at any scale. 

**Summary of Lens Application:**
*   **(a) Measurement Projected:** The primary measurements are the statistical properties—specifically Gamma and scaled-shifted Gamma distributions—of the relative and subtractive residuals derived from an iterative map that predicts the global growth of successive primes [cite: 11]. The variance of these subtractive residuals is measured against previous prime values to detect local correlation jumps [cite: 11].
*   **(b) Verdict Reached:** The analysis reveals a well-defined cohomological structure governing the primes [cite: 11]. The verdict is that prime numbers are states of an asymptotically deterministic system. The local jumps (gaps) and long-range correlations encode an underlying cohomological equation, the exact solution to which turns out to be the logarithmic integral function \( \text{Li}(x) \) [cite: 11, 12].
*   **(c) Axis of Disagreement:** This approach fundamentally contradicts the Cramér heuristic of primes as a random, Poisson-like process. Instead of treating gaps as random variations, the dynamical systems lens views them as strictly deterministic local jumps that only *appear* irregular due to the complexity of the underlying cohomological equation [cite: 11, 12]. It disagrees with `MATH-0369`'s reliance on probability to define the bounding constant \( M \).

### 2.2. Attempt 2: Chaotic Residue Spectra and Symbolic Dynamics
**Source:** *Entropy* Journal (2018), *Results and Interpretation for the Gaps Residue Sequence* [cite: 10].

In order to study unbounded prime gaps using topological dynamics, researchers stationarize the gap sequence by taking it modulo \( k \). Because gaps are always even (excluding the gap between 2 and 3), looking at gap residues modulo 6 categorizes transitions into twin primes (gap 2), cousin primes (gap 4), and sexy primes (gap 6) [cite: 10].

**Summary of Lens Application:**
*   **(a) Measurement Projected:** The model projects the prime gaps as an underlying Markov Chain and measures the **Renyi entropies**, Lyapunov exponents, and topological metrics of Iterated Function System (IFS) attractors formed by these symbolic sequences [cite: 10].
*   **(b) Verdict Reached:** The gap residue sequence is maximally chaotic but unexpectedly displays a non-trivial spectrum of forbidden patterns [cite: 10]. By mapping the gaps to an IFS chaos game-like attractor, the geometric role of the distribution of these forbidden patterns is revealed. The sequence contains rigid topological constraints that restrict the phase space of possible gaps [cite: 10].
*   **(c) Axis of Disagreement:** While traditional models (like Hardy-Littlewood k-tuple conjectures) assume independence and positive density for all admissible configurations, this dynamical systems measurement reveals a monotonic dependence and forbidden blocks not found in pure null (random) models [cite: 10]. The disagreement lies in the assertion that prime gaps possess a geometric, chaotic structure with memory, refuting the "memoryless" assumptions inherent to Cramér's coin-toss derivation.

## 3. Lens 2: `STANCE_INFORMATION_THEORY@v1`

Information theory evaluates the prime sequence in terms of data compression, entropy, and signal processing. If the prime numbers represent a dataset, the prime gaps represent the optimal encoding lengths required to describe the sequence without information loss.

### 3.1. Attempt 1: Surface-Area Scaling and Kolmogorov Complexity
**Source:** Morgan Porter (2025), *Deriving Cramér's Conjecture from Surface-Area Scaling: An Information-Theoretic Approach* [cite: 13].

Porter presents a direct, deterministic derivation of the Cramér conjecture based purely on the informational structure of primes, completely bypassing probabilistic assumptions and unproven hypotheses like the Riemann Hypothesis [cite: 13, 14]. Primes are modeled as discrete informational events in the natural number sequence [cite: 14, 15]. 

**Summary of Lens Application:**
*   **(a) Measurement Projected:** The framework projects the **Kolmogorov complexity** and **Shannon entropy** of the prime sequence up to \( x \), establishing an information bound \( I(x) \sim c(\log x)^2 \) [cite: 13, 14]. It measures the maximal information increment between consecutive primes constrained by dimensional optimality via the isoperimetric inequality [cite: 14, 15].
*   **(b) Verdict Reached:** The Cramér bound \( g_n = O(\log^2 p_n) \) is rigorously derived as a deterministic upper limit dictated by optimal information encoding [cite: 14]. The isoperimetric inequality fixes the optimal encoding constant at \( M=1 \), ensuring that the information capacity is universally constrained [cite: 14]. A gap larger than this would require more information to encode than the sequence's structural complexity allows, creating a contradiction [cite: 13].
*   **(c) Axis of Disagreement:** Porter's thesis sharply diverges from both standard probabilistic Number Theory and Granville's modifications. It rejects the idea that \( \log^2 p_n \) is merely the statistical limit of random intervals [cite: 14]. The axis of disagreement is ontological: Cramér-Granville treats the bound as an artifact of probability (where larger gaps are statistically improbable but theoretically possible), whereas this lens treats the bound as a hard, unbreakable physical constraint of mathematical information limits [cite: 13].

### 3.2. Attempt 2: Nyquist-Shannon Sampling and the Prime Emergence Field
**Source:** *Primes, Signals, and Physics* / *Trinity Architecture* (2025/2026) [cite: 3, 16].

This framework models prime numbers not as abstract entities, but as emergent, discrete events generated by the dynamics of a continuous physical "Prime Emergence Field" \( \Delta\phi(x) \) [cite: 3]. The connection between continuous fields and discrete primes is mediated by the **Nyquist-Shannon sampling theorem** [cite: 3].

**Summary of Lens Application:**
*   **(a) Measurement Projected:** The model measures prime gaps as "sampling intervals" required to capture a continuous field's bandwidth without aliasing. It projects prime constellations (like twin primes) as **quantizer overflow events** within a Delta-Sigma (\( \Delta\Sigma \)) modulation scheme [cite: 3, 17]. The bandwidth of the field is measured to grow as \( B(x) \propto 1/\log(x) \) [cite: 3].
*   **(b) Verdict Reached:** The apparent randomness of primes is merely the necessary aperiodicity of a sampling grid required to faithfully capture a complex, non-periodic signal [cite: 3]. Twin primes and specific gap bounds represent critical thresholds where the field's rate of change causes the system's integrator to saturate, forcing rapid pulses to maintain information fidelity [cite: 17]. 
*   **(c) Axis of Disagreement:** This lens reframes `MATH-0369` from a question of integer distribution to a question of signal compression. It disagrees with the Cramér-Granville view of gaps as isolated arithmetic phenomena, instead arguing that gaps are deterministic artifacts of a "Lossless Compression Mandate" [cite: 3, 17]. Furthermore, it links maximal gap bounds directly to a spectral band-limiting condition mathematically equivalent to the Riemann Hypothesis, diverging from purely analytic number-theoretic methodologies [cite: 3].

## 4. Lens 3: `STANCE_RENORMALIZATION_GROUP@v1`

In quantum field theory, the Renormalization Group (RG) program is used to systematically remove divergences by analyzing how physical systems behave at different energy scales [cite: 18]. Applied to number theory, this lens investigates whether prime gap distributions exhibit scale-invariant geometric symmetries that flow between fixed points.

### 4.1. Attempt 1: Prime-Zero Duality and RG Flow
**Source:** Zhengqiang Li (2026), *Prime-Zero Duality: Fractal Geometry, Renormalization-Group Flow, and an Information-Ontological Framework for Number Theory* [cite: 19].

The explicit formula of analytic number theory connects primes and the non-trivial zeros of the Riemann zeta function globally [cite: 20]. Li addresses whether they share a hidden, scale-by-scale geometric symmetry—a local duality that persists at every resolution [cite: 20].

**Summary of Lens Application:**
*   **(a) Measurement Projected:** The research measures the joint fractal structure of a prime residue class (e.g., \( p \equiv 1 \pmod{16} \)) via its box-counting dimension (\( d_P \)) and the zero-distribution regularity index (\( \zeta_R = 2 - H \)) derived from the Riemann zeros [cite: 19]. The combined **duality measure** is projected as \( K = 1/d_P + 1/\zeta_R \) [cite: 19].
*   **(b) Verdict Reached:** The duality measure \( K \) is remarkably stable across scales (varying by only 17% compared to 43% for \( d_P \) alone) [cite: 19]. The data reveals a finite-size scaling law representing a renormalization-group flow. The system flows from an ultraviolet (microscopic/short-scale) fixed point of \( K_{UV} = 11 \) to a universal infrared (macroscopic/large-scale) fixed point of \( K_{IR} = 4 \) [cite: 19]. 
*   **(c) Axis of Disagreement:** The RG lens challenges the assumption that the statistics of prime gaps can be uniformly bounded across all scales using a single classical model. It disagrees with the Cramér-Granville focus on a static supremum limit, suggesting instead that the distribution characteristics (and thus the behavior of gaps) undergo a dynamical RG flow depending on the resolution scale, establishing a conserved information current between arithmetic and spectral domains [cite: 19, 20].

### 4.2. Attempt 2: Primorial Anomalies and Non-Hermitian Arithmetic Systems
**Source:** LiuGongshan & Claude (2025), *Primorial Anomalies in Prime Distribution: Towards a Non-Hermitian Arithmetic Dynamical System* [cite: 21].

Drawing inspiration from Wilson's renormalization group ideas regarding critical phenomena, this framework investigates "scale symmetry" tied to primorials (\( P_1=2, P_2=6, P_3=30, P_4=210 \dots \)) [cite: 21].

**Summary of Lens Application:**
*   **(a) Measurement Projected:** The framework projects deviations in prime distribution utilizing a newly defined Dirichlet series, \( G(s) \), independent of the Riemann zeta function \( \zeta(s) \) [cite: 21]. The model measures systemic local deviations near primorial values, projecting these as structural "anomalies" [cite: 21].
*   **(b) Verdict Reached:** There is a systematic "Primorial anomaly" where prime distribution exhibits significant modulation effects near primorial values [cite: 21]. The standard theory (Riemann zeta alone) misses approximately 8% of distribution information. The verdict is that a dual-layer arithmetic structure is required, and prime gaps are heavily modulated by these primorial scales [cite: 21].
*   **(c) Axis of Disagreement:** The classical Cramér-Granville conjecture relies on the Prime Number Theorem and Riemann's foundational structures. This lens posits a radical disagreement: the Riemann \( \zeta \) function does *not* encode complete information about prime distribution [cite: 21]. By asserting the existence of a secondary modulating function \( G(s) \), the expected bounds for prime gaps must be fundamentally recalibrated to account for the interference patterns at primorial renormalization scales [cite: 21].

## 5. Cross-Lens Synthesis and Tabular Summary

The application of non-standard lenses to `MATH-0369` highlights a fascinating epistemic shift. The classical mathematical perspective debates the *degree* of randomness (whether divisibility alters the probability matrix sufficiently to shift \( M \) from 1 to 1.1229). In stark contrast, modern computational physics and information theory entirely reject the premise of randomness. 

### Table 1: Matrix of Theoretical Disagreement on MATH-0369

| Lens / Stance | Fundamental Nature of Primes | Cause of Prime Gaps (\( g_n \)) | Postulated Upper Bound | Disagreement with Cramér-Granville |
| :--- | :--- | :--- | :--- | :--- |
| **Classical Number Theory** | Probabilistic/Heuristic | Statistical clustering / coin-toss variations | \( O(\log^2 p_n) \) (with dispute on \( M \)) [cite: 4, 5] | Baseline for comparison. |
| **Dynamical Systems** | Deterministic States | Topological jumps / Phase-space forbidden blocks | Regulated by Logarithmic Integral / IFS Attractors [cite: 10, 11] | Rejects stochastic independence; gaps have memory and geometric constraints [cite: 10, 12]. |
| **Information Theory** | Optimal Encoding / Signal Compression | Shannon limits / Nyquist-Shannon sampling intervals | Strictly \( 1 \cdot (\log p_n)^2 \) due to isoperimetric limits [cite: 3, 14] | Rejects probability entirely; bounds are hard physical/informational limits [cite: 14, 15]. |
| **Renormalization Group** | Scale-Invariant Fractals | RG Flow variations between UV and IR fixed points | Modulated by Primorial scales / Dual-layer Dirichlet series [cite: 19, 21] | Rejects static bounds; gap behavior flows dynamically based on resolution scale [cite: 20, 21]. |

## 6. Conclusion

The Cramér-Granville conjecture (`MATH-0369`) remains an unyielding fortress in analytic number theory. Through the standard lens, the debate between Cramér's \( M=1 \) and Granville's \( M \approx 1.1229 \) hinges on the probabilistic weighting of prime divisibility [cite: 4, 5]. However, the primary-literature lens fingerprint reveals that interdisciplinary approaches—specifically `STANCE_DYNAMICAL_SYSTEMS@v1`, `STANCE_INFORMATION_THEORY@v1`, and `STANCE_RENORMALIZATION_GROUP@v1`—are aggressively converging on a paradigm of **structural determinism**. 

Whether viewing prime gaps as the deterministic residuals of a cohomological equation [cite: 11, 12], the necessary quantizer overflows of a Prime Emergence Field [cite: 3, 17], or the scale-invariant fractal manifestations of a renormalization group flow [cite: 19], these novel frameworks collectively argue that the maximal gap between primes is not a statistical anomaly, but a rigid structural necessity of the mathematical universe. As these computational physics methodologies mature, they may ultimately provide the tools required to bypass the probabilistic limitations of the Cramér-Granville heuristic and rigorously resolve `MATH-0369`.

**Sources:**
1. [wolfram.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQpNjECaEUUtxtAa9A46E_pCAE4-rUn8e0wpoHqrqKqsETkkNrg4-oUug9-LF8sNpzPdOt84mHd1P3BymgaWB2YPpDs_drjVlZWjkO3mbdIBVNGdgTRgZwkJ3bZj6mOtrsIrjwNXMWlGlsAqYWt4Z6aePv)
2. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIzPjZ3lbPU6yojS1vhgiMhdW0Jte9kuKoI2WhrNQYyjWVL97ZdHhs8bBilAGqIcY-ckcEXs-A7oxyryJw8saw6t2VdeOCT7gyprOZBKSTfl_DaqXIGHRUBMh1eglhGn0wuHj3ESPXFYuhg-J8CiDJcY7pRf2Jsmk=)
3. [Link](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFREnDljcKGcohe9j0jUdABekT8O7NKFnOcdk_SWBIAWeh6Js3EOqul5u9FvTfqBnHjyqWRdyVap0xzRT4-p3fvDotHG7XGZ0AkSVyVo-4FoCT5m9DO4fQ5vTogJcgImHzRrlhNgJcdx4ycDPEiAs9M6oCGtDHqnrgJDoYh9VBXR_tmaOoztfmffTN7QzKS2e110A==)
4. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSxDnuarcRD5TIL5uHdX3T9VqzZ638s6NPAx7TL6DtYC6e5CIkRmcUcE9OeykEtzLv26pmNGabKLAZaEjBz41AYi0QxKUWDsZ7knjMZkNhEvYRdRBA9n9l04psuGqEuDVmjzfUBqjafTvsA-xuo2BZH2hCYtdRTrZelehsVxLEfr5FKry81uweNaZzT6wAFXosvkmEgHWKrTzc1C9FGCdb_JbdscUnfZ_R)
5. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF87chNw9g-zVBrnQoniUCpeHndZA0RKOz02R3TVxnzNe5vRvAjfjVZgBIUn7avBwSPROChXE0L4DYVp5YtpFjS-7vngMTw2tH8F8eM_Ps4uaU4aYC5bo1Jkx-Ylza8J8B92lAjckOnM2dW3EYNwg==)
6. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIARE7yVRN-pgXnf0gFZR6Z2PAJ8XfNGceoXbQEpfIHGO9zCERw8GTgkIliwfU262QII0k4zaSBmseLzDchmgvaeV92RQ8YnY-15cETlYN-taGh_GXa2VKtWY8ysa9cozCO1AtZA_9sChDrlljk3p1ekK9uRr2RSok3ydmcISqtMCcSvNGPuw=)
7. [oeis.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG18FsRqgreafnirvEsKM1I7YzWVr44PDzrksBJXOiW0LGf03nHEYTzBSt5A0QXMIwTqXwEmHKxIviw8tOYjSnkpHdkaPUES_X6yec1_20=)
8. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_x_k-BZOewv6zuUAeY4P0tjNRfflUkmM7bOpD9DtwKaDvLxkbvtiPczWhtPuGlnqio-F-d-ny1kxWqgnkxSBUD41IlLbK8ECIWQTOOX7Oy2vlye2Mqmgz80CqPwgEcxcXFmxI3JQmA7_KvqkZ6VN9WATQQ0J1wZPS59In-xhepOS88DWcsT67Xg==)
9. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQnG2pIxa1UANkaT9S0pNTOVCW7QtaAUdUV1U96ljw_6ww22ZCD8CtDqjZDwJSjYJPIyy3INp8SiYFXapzKKIJFn0MBpcimXQhrf0ruJ4jFOBLBpglez5qzvRSNx5-7lvgKW8tBB1628VGiJGUTp-3LOeU0mkgHByXuU6oGiGovmuZWPu_sr2X52QPiI7x3ECtynpdZmJgbGpa)
10. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNll5vqdAQd0K8pXfp3ALFQX9ZQa1DgsY8mECGHLwinm7O3akFXKbxr_bfyTskKGu08BFbrH_UoAb-ulEH3US0o3Omxy3nVBsHSJhWmsksAQ8s9R9xhXnJut59TtA=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJbGKWdnhcyOp3JK4DWr43F2HOQk7BjTcppqFWaJ3rkO02tgYpweKMezTAafDAnSooVzgkeUuIzbMFy9bSk2jg8mvo9peKWuRFEP6uTdUWn4BKy5slw1C2ig==)
12. [papers.cool](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQtDGNImU811IKwrtvS2LOK9XcusalxNw_UFcWonic-A9zQm7jcNSeFTgWfJQ8abBzfaXPsA8X0KgJ0zCF3eUrgGLAaSzdN1KxJymohqJDbD1xhIjHAByn4tE=)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUmjFlML_8kLvvQp-Nj4KirK8kdoJKRYxoFcjDpUJDYBoBrwKk5MIbRw-zt-tbmARvKd-884GnM9rb6LyvrU18AhdzJ4jNzdzPGZB_C4mryloYw1kTklXKIqAnamECP_wuWtiEQpukrV0krMBt3RnbztWZurhth4Z9K824Mc-u5c8hLVQB1_qeA7j6L6hKRuNC_-sETKFRU7nhSMazEMZwUrR-VLRCNjlFpR49X-U9TappkLpQ9IvkHXQhx8bGjQCCyQ==)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQ9l3ZYVLA3UwBF05zeYRscEHxUanxUIsE5xZw23rBQGfqSn3Q-mJ20iH2h5lGoSxxsiuhBknae9ESGzLO7hRzNcbsL9IdwKFmrKOh-cJAIukZiwyxxNwsoGq6NsSZyztKmsXVl1GLNaAKMRR0ZV0jISqhwaFEl5A-azKbJpao_mIlKw==)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsgaQu66g6U19Aj2GCYWBWyxDJJuT5MkfPlysrrnksWVXf2UPRiR0vm2B8hvY9pwgk2QTiMCS2yEwWFv1UHioZv0z3GXIpCSR73LlreHflosoDtuVWGLPgsg3zb3bLtTU5eAs2OstQaSh0YCyUujla2TjGt1ulvawRtkxAB85U_UTR8nEHilA7A_CeJpqJqXYzQFOwzZG1YPaihz0M8GaMR_WHpucYyscvOnPpG7ElQurVrJiiwuqtapdft7RG7Ern)
16. [osf.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEye3o-zi8JWfYFTiR0RgCAL81F2Jg6b-AlGwvBcmPLGWbH8h4ViVJ_A1wFrcXjQ4J0KqR2tn-2Ql0oeXJhgNRWCN6Zkz1l8Wz0ABtmHTq2KeE-9g==)
17. [zenodo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_9dssKcy1q7e_UcJjpoHcq3TIoYgJSQVLFu0ih1N8XF5hf17DLuFdFq-fZi-pbyA5ZvFDyonvYOqS5PGE86hR_uy2MulYiAFcW04rUjPxBp6CPtE4WXMkzQ==)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyw1wbS0VmwBexpalrgtVGA6J9vVrDU7feNF30SsHtm01TH9aHtY1nc3Ngq0NSmQ6UwCdt3MWXRez1DAcrvBZG9NWawB-1lX-r_f9lLJTsGbbDZVXodOoVbM10Oz_SWenl35r9mBFnnPsNPW0oWYfIdX6dZ-Tmlek5hBW6Nj0zkXjxZdvNUsR_cSkQwkQq5-GlUETWeDF2aQ3gC2tJ_muWlyYIifgM0bvkPszi34JaVRWxTIxKDE9_fwSup8A0In7LzMgzZCo8C1dftIzl_k4YESrGSBOQ1WipQlamvVbkBrKl1pfewwaHDS0B8idLwaZqQ7sIm72YDBCRCbDJKU36FHdwNhZmyKJw4s0oqUpquvpJ9g==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKIRktTkOIuMnYZzMJwxlYmZMPOIqITMNUMoFd0e5qQMuxJRWPm8gG-iaw2MrDq-ybJIvOyP-ElppjOCr8YgKJ6D0zFOm0pnM26PiugPFFaQUDzFSnbK4_KQ==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwntiZUBcDwsEojKsZ2EwFtqU3Fwwc6wm4ThzHzELBDQ-xs6zpJngeZWNe4gNbosVWg747p7Vd81xSwQhBKwsbcKWyMKGjKX7mazVk1t2SxTzbmBrNoQ==)
21. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHw_73ISPLCaTYfGeknOgNC98jlem83-FnD1dI1MpMdHaxd3_XEtatcBymyXuiMd4KxmDjDJwEmkhNORWcpaIRmEKuQ3myIY-keqaGkINW_h1EuB63Dxbw_01j521DW4RS3Mpg_s1oDhG_Ac1LBmXgmYDlWhgWkNPDxDrSgcH3qHYRYrxL8ideU15t_Rh-SrkVPhy4X-tQ_huE=)

