# Argos lens fingerprint: Prouhet-Tarry-Escott problem

**Pythia queue id:** 344
**Tier:** T5
**Priority:** 5
**Requested by:** Argos
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdxLThRYXJmSEhxWEhqTWNQeU5fZ21RdxIXcS04UWFyZkhIcVhIak1jUHlOX2dtUXc
**Elapsed:** 243s
**Completed at:** 2026-05-23T00:11:12.072014+00:00

---

# Primary-Literature Lens Fingerprint for Open Problem `MATH-0356` (Prouhet-Tarry-Escott Problem)

*   **Research suggests** that the Prouhet-Tarry-Escott (PTE) problem, originally formulated as a classical Diophantine puzzle, fundamentally underpins structural limits in modern computer science, dynamical systems, and quantum physics.
*   **The evidence leans toward** the conclusion that algorithmic limits in decoding logic (such as Reed-Solomon error correction) are structurally barricaded by the existence of PTE solutions, which introduce unavoidable "collisions" in algebraic subsets.
*   **It seems likely that** the algebraic symmetry inherent in the PTE problem governs continuous topological phenomena, effectively mapping discrete number theory onto the continuous spectral measures of fractal dynamics and chaotic boundaries.
*   **There is growing consensus** in theoretical physics that quantum gauge anomaly cancellations for certain hidden particle sectors are mathematically synonymous with low-degree PTE constraints, suggesting a deep link between subatomic consistency and pure integer partitions.

The Prouhet-Tarry-Escott (PTE) problem is a monumental open problem in Diophantine mathematics (`MATH-0356`), named after Eugène Prouhet, Gaston Tarry, and Edward B. Escott [cite: 1]. The problem asks whether there exist two disjoint multisets of integers $A = \{a_1, a_2, \dots, a_n\}$ and $B = \{b_1, b_2, \dots, b_n\}$ such that their sums of $k$-th powers are equal for all integers $k$ from $1$ up to a given degree $d$. Formally, $\sum_{i=1}^n a_i^k = \sum_{i=1}^n b_i^k$ for $1 \leq k \leq d$ [cite: 2, 3]. The most coveted targets are "ideal solutions" where $n = d + 1$ [cite: 2, 3]. Despite over 150 years of study since Prouhet's early conceptualization in 1851 (and precursors from Euler and Goldbach in 1750 [cite: 1, 2]), the problem remains broadly open for large $n$. Solutions are known up to $n=10$ and $n=12$, but the complete combinatorial boundary and the asymptotic existence of ideal solutions for arbitrary degrees are entirely unresolved [cite: 3, 4].

Under the Argos proposal's multi-perspective methodology, we interrogate the PTE problem through three transdisciplinary lenses: Information Theory, Dynamical Systems, and Renormalization Group theory. By analyzing the primary literature attempts within these distinct spaces, we map out the measurements projected onto the problem, the operational verdicts reached, and the orthogonal axes of disagreement that separate each lens's epistemology.

---

## Lens 1: `STANCE_INFORMATION_THEORY@v1`

In Information Theory and Coding Theory, discrete mathematics is fundamentally applied to the preservation, hashing, and recovery of data. Here, the PTE problem is typically encountered not as a number-theoretic curiosity, but as an adversarial algebraic configuration. It dictates structural limits in polynomial reconstruction, hashing collisions, and subset summations. The two strongest primary-literature applications under this lens lie in bounded distance decoding complexity and the structural resilience of cryptographic Boolean functions.

### Attempt 1: Bounded Distance Decoding (BDD) and Moments Subset Sum
The most significant computational complexity application of the PTE problem arises in the study of Reed-Solomon (RS) error-correcting codes [cite: 5, 6]. Guruswami and Vardy posed a fundamental open problem in coding theory regarding the exact boundary of NP-hardness for bounded distance decoding of RS codes [cite: 5, 7]. Recent breakthroughs by Ghazi, Kamath, Sudan, Grigorescu, and Gandikota demonstrated NP-hardness for decoding radii significantly smaller than the maximum likelihood decoding radius [cite: 7]. To prove this, they mapped RS decoding to an intermediate NP-hard problem: the *Moments Subset Sum* (MSS) problem [cite: 6, 8].

MSS(d) asks whether, given a set of field elements and target moments $m_1, \dots, m_d$, there exists a subset of specified size whose power sums exactly match the target moments up to degree $d$ [cite: 6, 8]. In extending their NP-hardness proofs to large degrees ($d = \omega(\log N)$), the authors identified a fundamental mathematical barrier: the Prouhet-Tarry-Escott problem [cite: 6, 9]. The existence of PTE solutions creates distinct, disjoint integer subsets with identical power sums. Over finite fields, this structural parity generates unavoidable subset sum collisions, undermining the uniqueness criteria required for polynomial-time cryptographic reductions [cite: 6, 9]. 

*   **(a) Measurement Projected**: The analytical measurement projected through this lens is algorithmic complexity bounding—specifically, the temporal complexity (e.g., quasi-polynomial time reductions) and decoding radii bounds as a function of block length $N$ and dimension $K$ (e.g., $N - K - c \frac{\log N}{\log \log N}$) [cite: 6, 9]. The metric of interest is the error-correction gap bridging the Johnson radius and the NP-hard regime [cite: 5, 9].
*   **(b) Verdict Reached**: The verdict reached is that the algebraic existence of PTE solutions acts as an absolute computational ceiling. The theoretical computer science community must recognize the PTE problem as the primary structural obstruction preventing the extension of NP-hardness proofs for MSS(d) to arbitrary degrees [cite: 5, 8]. The researchers explicitly conclude that PTE dictates the boundary between computationally hard instances and structural ambiguity [cite: 7, 9].
*   **(c) Axis of Disagreement**: The axis of disagreement with other lenses lies in the *adversarial versus generative* view of PTE. In information theory, a PTE solution is an adversarial collision that destroys algorithmic uniquely-decodable states. The problem is approached through worst-case computational reductions over prime finite fields [cite: 8, 9], rather than observing the problem over $\mathbb{R}$ or $\mathbb{C}$ as dynamical systems do.

### Attempt 2: Cryptographic WAPB Functions and Twin Smooth Integers
A second robust application in information theory and cryptography uses PTE as a constructive tool rather than an adversarial barrier. Costello, Meyer, and Naehrig utilized the PTE problem to construct twin smooth integers for the post-quantum isogeny-based signature scheme SQISign, optimizing cryptographic sieving algorithms through ideal PTE solutions [cite: 10]. Concurrently, deep theoretical work by Grenouilloux, Li, and Meaux investigated Weightwise Almost Perfectly Balanced (WAPB) Boolean functions—primitives designed for Fully Homomorphic Encryption (FHE) ciphers like FLIP [cite: 11]. 

WAPB functions must maintain resilience against side-channel attacks when inputs have predictable Hamming weights [cite: 11, 12]. The authors discovered a profound algebraic relation between Krawtchouk matrices and Vandermonde matrices that entirely reduced the calculation of a WAPB function's "corrector order" (resilience) to a localized instance of the PTE problem [cite: 11, 12]. 

*   **(a) Measurement Projected**: The projected measurements are the *corrector order* (a metric of cryptographic resilience bounded by the Hamming weight) for WAPB functions [cite: 11, 12], and the *smoothness bound* of primes used in isogeny graphs [cite: 10].
*   **(b) Verdict Reached**: The verdict reached is that PTE solutions map precisely to optimal corrector orders. Using the reduction to PTE, the researchers established that for infinitely many integers $n$, WAPB functions possess a corrector order tightly upper bounded by the Hamming weight of $n$ minus one [cite: 11, 12]. In isogeny cryptography, single PTE solutions successfully produce lower smoothness bounds for $p+1$ and $p-1$ twin primes, directly accelerating post-quantum cryptographic primitives [cite: 10].
*   **(c) Axis of Disagreement**: This approach disagrees with the macro-asymptotic view. Cryptographers seek isolated, highly specific, low-degree ideal solutions (e.g., $n \leq 12$) to formulate immediate finite-field hash architectures or isogeny steps [cite: 10, 12]. They disagree with the infinite-family / topological generation approaches of dynamical systems, focusing strictly on localized algebraic efficacy rather than infinite sequence scaling.

---

## Lens 2: `STANCE_DYNAMICAL_SYSTEMS@v1`

The Dynamical Systems lens maps the discrete integer summations of the PTE problem onto continuous trajectories, symbolic dynamics, ergodic theory, and spectral continuous measures. In this realm, PTE is viewed as the discrete fingerprint of scale-invariant continuous geometries, and its solutions are generated through the recursive evolution of formal dynamical operators.

### Attempt 1: Substitution Dynamical Systems and the Prouhet-Thue-Morse Sequence
The deepest mathematical bridge between dynamical systems and the PTE problem was implicitly laid by Eugène Prouhet himself and formalized by Axel Thue and Marston Morse: the Prouhet-Thue-Morse (PTM) sequence [cite: 13, 14]. The PTM sequence is a binary sequence obtained by repeatedly appending the Boolean complement of the existing sequence (0, 01, 0110, 01101001, ...) [cite: 13]. In symbolic dynamical systems, this sequence is the fixed point of the substitution map $a \to ab, b \to ba$ [cite: 14, 15].

Dynamical systems mathematicians, such as Bufetov and Solomyak, extensively study substitution automorphisms, translation flows, and discrete topological dynamical systems over Cantor spaces through this sequence [cite: 16]. Bufetov and Solomyak have proven that the spectral measure of such substitution dynamical systems exhibits a continuous, non-periodic behavior with a specific log-Hölder modulus of continuity [cite: 17, 18]. Astonishingly, the PTM sequence is not just a dynamical object; it is a universal algorithmic generator for the PTE problem. If one partitions an arithmetic progression of length $N = 2^{k+1}$ into two sets based on the indices of the 0s and 1s in the PTM sequence, those two sets form an exact, non-ideal solution to the PTE problem of degree $k$ [cite: 2, 13, 14]. 

*   **(a) Measurement Projected**: The measurements projected include topological entropy, pair correlations, translation flow eigenvalues, and the Hoelder asymptotic expansion of continuous spectral measures around zero [cite: 17, 19]. Measurements focus on frequencies of finite words and bounds on measure continuity [cite: 17, 18].
*   **(b) Verdict Reached**: The verdict reached is that the solutions to the PTE problem are an inescapable algebraic shadow of self-similar symbolic substitution. The PTM sequence guarantees infinite families of PTE solutions with an exact $2^k$ regularity [cite: 20, 21]. Dynamicists view the PTE equality not as a coincidence of integers, but as a theorem of substitution ergodicity where all odd-order correlations of the balanced sequence inherently vanish [cite: 17].
*   **(c) Axis of Disagreement**: The axis of disagreement is *Discrete Algebraic Searching vs. Continuous Metric Generation*. While number theorists (and information theorists) search for specific, minimal "ideal" solutions (where $n = d+1$), the dynamical systems lens dismisses minimality to focus on infinite, universally scaled generation (solutions where $n = 2^k$) [cite: 1, 2]. Dynamicists disagree with treating PTE as an isolated polynomial constraint, instead treating it as a byproduct of measure-preserving group actions and ergodic flows [cite: 16, 18].

### Attempt 2: Sudler Products and the Erdős-Szekeres Problem
A secondary dynamical attempt to frame the PTE problem focuses on polynomials vanishing at $1$ and their behavior on the unit circle, intersecting with complex dynamics and the Erdős-Szekeres problem. Researchers like Peter Borwein and Colin Ingalls demonstrated that the PTE problem is structurally equivalent to finding polynomials with coefficients in $\{-1, 1\}$ (pure products) that have a high-order root at $z=1$ [cite: 3, 22].

This directly connects to the asymptotic behavior of Sudler products $\prod_{r=1}^N |2\sin(\pi r \alpha)|$ for quadratic irrationals $\alpha$, which represents the Birkhoff sums over irrational rotations on the unit circle [cite: 23]. Under this lens, the discrete power sums of the PTE problem translate to the derivatives of a generating function evaluated on the boundary of the complex unit disk [cite: 24, 25]. The maximum norm of these polynomials grows at an exponential rate correlated to the presence of PTE configurations [cite: 22, 25].

*   **(a) Measurement Projected**: The metrics applied are the maximum norm of bounded-coefficient polynomials (the sum of absolute values of coefficients) [cite: 22, 25], the growth rate of Sudler trigonometric products, and the bounding constants of the Erdős-Szekeres products along continued fraction convergents [cite: 23].
*   **(b) Verdict Reached**: The verdict is that non-ideal, symmetric solutions of the PTE problem define the theoretical minimum degrees required for pure product polynomials to maintain prescribed high-order vanishing [cite: 3, 22]. Analytically, it was proven that any $n$-factor pure product has a norm strictly greater than $2n$ for certain values natively restricted by the absence of small PTE solutions [cite: 22, 25]. 
*   **(c) Axis of Disagreement**: This approach disagrees with both the algebraic subset paradigm of Coding Theory and the logical reductionism of cryptography. Instead of treating PTE elements as separate multiset members, it fuses them into a single complex polynomial whose geometric behavior (Birkhoff summations and periodic variations) across the unit circle $\mathbb{T}$ projects the Diophantine bounds [cite: 23, 24]. It fundamentally relies on analytic bounds rather than discrete algorithmic combinatorial searches.

---

## Lens 3: `STANCE_RENORMALIZATION_GROUP@v1`

The Renormalization Group (RG) lens evaluates scale transformations. It investigates how systems behave as one integrates out short-distance degrees of freedom or iterates local scale changes. Strikingly, the PTE problem materializes at the extrema of these transformations, dictating the bifurcations of chaos in topological maps and determining the fundamental anomaly-free limits of quantum field theories.

### Attempt 1: Piecewise Smooth Maps and Morse-Thue Renormalization
In nonlinear dynamics, scaling limits at the edge of chaos are frequently governed by renormalization group equations. Glendinning, Sidorov, and Hege explored the boundary separating parameter spaces with positive topological entropy from those with zero topological entropy in piecewise smooth maps [cite: 26, 27]. The topological boundary of chaos corresponds directly to the survivor sets of open dynamical systems [cite: 26, 27].

To evaluate these survivor sets (especially in $\beta$-dynamical systems with a hole at zero), mathematicians apply renormalization schemes built upon combinations of local substitution rules [cite: 28]. The anharmonic route to chaos identified by Glendinning is defined by an infinite cascade of bifurcations that asymptotically converge to the standard "Morse-Thue renormalization" [cite: 26, 27]. This renormalization process scales interval sizes by invariant factors based strictly on the sequence operators inherent in the PTE-generating PTM sequence [cite: 27].

*   **(a) Measurement Projected**: The projected measurements are the Hausdorff dimension of survivor sets $K_\beta(t)$, the critical parameter value $\tau(\beta)$ where topological dimension drops to zero, and the local topological entropy of the induced parameter space maps [cite: 27, 28].
*   **(b) Verdict Reached**: The verdict is that the geometry of the chaotic boundary is literally parameterized by the Prouhet-Tarry-Escott sequences. The renormalization cascade requires a strictly alternating sequence of operators (B and D renormalizations) that mimic the integer partitions of the PTE problem to prevent the topological box sizes from collapsing to zero [cite: 26, 27]. Consequently, PTE combinatorial structures serve as the invariant fixed points of the renormalization operators [cite: 26].
*   **(c) Axis of Disagreement**: This lens diverges significantly from pure Information Theory or pure Number Theory by mapping the PTE problem into a continuous fractal parameter space. The combinatorial equality is not interpreted as an arithmetic identity, but rather as an invariant scale factor (a topological scaling modulus) that maintains structural integrity across infinitely regressing geometric transformations [cite: 27, 28].

### Attempt 2: Quantum Anomaly Cancellation and Minicharged Particles
Perhaps the most unexpected and revolutionary lens applied to the PTE problem comes from high-energy particle physics and quantum field theory (QFT). In quantum gauge theories, the spectrum of fundamental fermions is tightly constrained by the requirement of anomaly cancellation—if anomalies do not cancel, the theory loses gauge invariance and mathematical consistency under renormalization [cite: 29, 30]. 

Lee and Takahashi proposed a framework for light minicharged particles (mCPs) under a hidden Abelian gauge symmetry $U(1)_H$ [cite: 29, 30]. Because this symmetry kinetically mixes with Standard Model hypercharge, the hidden matter states acquire effective minicharges [cite: 30, 31]. To be quantum mechanically consistent, the sum of the cubes of the chiral charges must equal zero (due to triangle loop anomalies) and gravitational anomalies enforce linear constraints [cite: 30, 32]. Lee and Takahashi proved that these anomaly cancellation conditions for $U(1)_H$ are exactly, mathematically equivalent to finding a degree $k=3$ solution to the Prouhet-Tarry-Escott problem [cite: 29, 30, 31].

*   **(a) Measurement Projected**: The measurements are physical fermionic mass eigenstates, chiral gauge charge patterns, and cosmological abundance limits for dark matter (e.g., limits like $\Omega_{mcp}h^2 < 0.001$) [cite: 30, 32, 33]. The QFT renormalization group equation for the fine-structure constant $\alpha_X$ also bounds the scaling of these charges [cite: 29].
*   **(b) Verdict Reached**: The PTE problem forces a specific physical reality: the hidden gauge sector *must* contain at least four minicharged states (an ideal $k=3$ PTE solution requires $n=4$) [cite: 29, 30]. Furthermore, because the minimal ideal solutions for $k=3$ are structurally dominated by symmetric affine transformations, the physical mass spectrum generically predicts a near-degenerate doublet structure for dark matter mass states [cite: 30, 33].
*   **(c) Axis of Disagreement**: The physical quantization axis forms a stark contrast to all other lenses. While dynamical systems view PTE as a fractal limit, and computer science views it as a polynomial collision, the quantum renormalization lens views the PTE problem as a *fundamental selection principle of physical reality*. It dictates that only specific, number-theoretically balanced multiset charges can survive quantum loop corrections [cite: 29, 32]. The disagreement lies in the fundamental ontology of the mathematics—here, the integer multisets correspond directly to actual physical particles in the universe.

---

## Synthesis of Axes of Disagreement

The application of `STANCE_INFORMATION_THEORY@v1`, `STANCE_DYNAMICAL_SYSTEMS@v1`, and `STANCE_RENORMALIZATION_GROUP@v1` to `MATH-0356` highlights profound epistemological divergences regarding what the Prouhet-Tarry-Escott problem "is." 

1.  **Obstruction vs. Generation vs. Selection**: 
    *   **Information Theory** conceptualizes PTE algebraically as an **obstruction** [cite: 8, 9]. Solutions are zero-sum algebraic faults that destroy unique decodability, serving to define the NP-hard floor of subsets.
    *   **Dynamical Systems** conceptualizes PTE analytically as a **generator** [cite: 16]. It is the inevitable combinatorial output of measure-preserving maps, continuous spatial flows, and iterative symbol logic.
    *   **Renormalization Group** conceptualizes PTE physically and topologically as a **selection principle** [cite: 26, 29]. Whether selecting the invariant edge of chaotic bifurcations or enforcing anomaly-free fermionic spectra in U(1) extensions, PTE serves as a universal filtering mechanism that stabilizes scaling.

2.  **Discrete Localism vs. Continuous Asymptotics**:
    *   Cryptographers and subset-sum theorists seek **finite, minimal** (ideal) solutions as targeted tools or localized adversarial limits [cite: 6, 10]. 
    *   Conversely, ergodic theorists and topological dynamicists analyze the **infinite, non-ideal** sequence (like the Thue-Morse sequence of length $2^k$) to understand limits, spectral frequencies, and continuous analytic unit-circle polynomials [cite: 17, 22]. 

## Conclusion

The Prouhet-Tarry-Escott problem (`MATH-0356`) transcends its origins as a pure Diophantine equation. Traced through multi-perspective lenses, it functions as the structural boundary of computational complexity [cite: 5, 6], the algorithmic heart of translation flow dynamics and pure product polynomials [cite: 16, 22], and the underlying arithmetic mandate for quantum gauge anomaly cancellation in particle physics [cite: 30]. The distinct measurements projected by each field—ranging from polynomial decoding radii to Hausdorff dimensions and chiral charge arrays—affirm that the equality of power sums in integer multisets reflects a profound, universal symmetry operative across the computational, geometric, and physical strata of science.

**Sources:**
1. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG98tVs_mj5-6nRWXIa54hrJcOyLGWQAOyiZJZipbQ-HgOtRSMTfPNNWcW2YZnoSL6LkNHHS4zqcX37ihVlV73SHrcFz6Fv7zU1NNBLJ5Bitf2rYHPu8sS8B2nlQ9fVr9bQYwvvrzadHgIG-lU-XhkxOUAAOZoRxhUYK3cvrtebow==)
2. [grad.hr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSgyY_Jaclk8SuQYjUAYxRlXsg-C0ktmNLbxe_M04ZbkjrquBDwYP123_9htq0my_xjfTW06UBPB2K3iHdw3scEBySOtAjzEa3tv41kq6Mlj9O8i0mtT1zG6Fts5LmyrOKZPWR9Qq8)
3. [sfu.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmjPftoeMJW1tYwWkjBiCglqPKGypj8iVvPVSfNpcmb7m0ADA70ciR0-FTNj7kAMjADo-CrUaveYSll4P-ov8o4Zqh5K1uFozlGoW6pQreOo6MwRxFQkK1oT-a3ouMxi2J8IQwiw==)
4. [proquest.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnXik4VjiIDTg-uGueUleVcMu4Yp3DmTwJ_DXuKzw3sx-kYvnL9wfowf6XxDpZgNeCtZcajcqkO5CTr_LDXNiy6l94K4IviWKynd1VnltcLk1ewxHFGgokCs5lv0H3xjBVmM-NPWbF8UeLizSziPNIXhSTwgnEIQDKAVlY6-U5Dtea-7ifJMbnS67J1k9Eetgqkdp5tkVOVTehw5XTXcujtGDgmG3a8A==)
5. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_kJyxyNz8S_DRLUqgWSNzP3eYjKkusICI2DaCcjyEXniJVH_xvtz9hzYOqJ6R5XeXaI-AXFWUDRat-QWT1D64ujEzCDSQm65if0Lg3x-uEjR8pu7H1yCTegXDwBbb_bl9GRI=)
6. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBbo3qPRuyYgMEcYARJhqeLmMtRC2ug9fr4qhmUgRBQhb4urdrN1Lb0w8w1mg25dRC3jz5XRPcYknDDwaQav39de-vdboeHg4d2KLoaC25nibIMppQxhAG-ZqxWND2SYfGSV62uPAmf4_MFH78hA==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE88iPL-HKKeQ6Ea_R3K7vp4gK5PowKXt30D-UxieNpfIc3uIgTuMeXd4q4_JkilS2l6mhqahVS443KYD02xk37jXl1MXtqpfqqE6LLkEO63d7AYJNTlg==)
8. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgZj6g3DWkWjvKF03JI_jahEnuk6mvNH_eXYEyukdFyNr2mrfk2DvXyCCV5dZUlNmOCMN2OZ-w7PTpg1G04WUGeZBanDbYJx8xunuihXst9UvDVQ-ZezfxzpSGhaRbgKwMd9tQ9wIzy54v5j8J)
9. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7B_GVIU3EQbXU4Xp9xd6gBJpTUDQ5OT_la2j_HEhVfMGCZke7lkVnHyODt8raLrUR4TvSE_pPrh9nfPW4Z0iNjTFQMw4LEMAT03gX7vKecaZcNVGZXjTKTAC0f0A7IbsFTaxT-vcaRbXx)
10. [cirm-math.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFa_kueZ30drgHojuI3EYVHvOgconpL6mJkV0Kq_jr9bEYLeEDfYXQl5b0krFjXwGj6QuTMgTbrtuRbRDbxCfhYVIZ6g4Q6h90TOwCNyu7GLMEMisJy6NaUbACORvLNAQSGArP0ziQUskie_f1RfjDkSrP9cj9ekCphrMxPCzHWegs=)
11. [uni.lu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHADj0n89Fmk4WfZRKtpX05deMLgnN6jR_mEUOuMtbEiH6fq4vAg0bbHOGAtiAnAU4j6nR4hs8wnYeT0I3sdRkv37xFWb437yegzru5Ebi_rOCxKGI3YGBhPIZ35HIg)
12. [uni.lu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQw6X45d9kg6B_qsgfaAMvuM5hP7haUrsRHh1n1Qhqi2r4z6LNZVzJZMF9__0dn1t8qoATjgplQ3BK5KSnph3ElffSMlAh6UuAybrGsSMyJP1hKOKkuTgy_LN6J8G1cztgirWfbGMq5fxdNvGF6Kw=)
13. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEnRHArZc3Jf0A-B2-h69TbClyMPGh_D13jkUQ-M6TjUuvCIvuCLSf83444PturRt7lpYSLXU8KmrvpL2Rd887qZow4WCR2dEewSMNeKtZ1B9IfUwYEu0zU2sUf2uYIaSdmwmohTCWSKJ5cHhdQao=)
14. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgoY86F_8N7bfvOlDvMGriR6Q_feyOItwGjUWfqNIOzonAB3ynbu8mG2-iKWuP9J7WfuDLLczeGob91tiks0QGbTZpRf_nx0NcKQl5y6VvoByEFKtFdpvI-RtfPQyXt7MufHxJEIo=)
15. [univ-mlv.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKMMQXjElUyNrTDm7WKYUeeZ347jo0RXR_FZS86hrsyPjoApdPrKtp7VGehfHGV8wQXbPe_RLejuzkT_oKU6_0XGpPOQv-TMoxiWULBTtmn5SKpQ0Rr0Xz-TNoi8qX2Y9HcvZbNFnUWj3Nhu6T7iT9-t4=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3YgvQcIZ3VbYvyRXFR-RygApYw_Z__OAxtXPB4SCdL3V5nHlgxZnXODZAG2WJJ2jH9cVHQG_XOBtgalG0o83keSnALW-LJgJbTTij_-KOMhwSRAIXlg==)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGoRO9cBrOALz77Qei9ugDymkLB7zdoAVau_rao_riHMTfJlo3DLl4EDNfQAZjAfrrEBYthMIOyzuM4iaoBTRFo687WuCg-CjJzBa9GV6ZpjuG2x9DSyTvzvNOIxSrAqZ6o2Rd8nRQOo7qKPltZfLToSpOn0z6mfFkH5ql7YjzKUO5UzZcPn38aOzGX9xf-1vRy)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEV8Z2IUsypnG3amZwLbM8j9hDTPkFOOFYZpCv13V3ySUyY80fJEOPdBtbVBVlEPPNOw5Jv3Lzyt1pv9bGg3lGSklNrOn9LgkXZ_NxhY0cVKR1XNEcF0mGPsNcw9Va_ZxrSjBCHx2OyYNdhJjtV9UzauaCMsYQg1ndatmFNj8kul5Q92ALTozd0MqKPg39LBw==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-LGX7uMNgv9nyoY7xWnauEEKdcLXuXuec_3__I3HwTea_jjeNBduUilx724lWtWlCodji_e7b9FdIGKx00an2n8ZjO6woeACX60Wijt3QvGuquRm8Kw==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJBCmbWArCKpITsMEoiQgMQ1ME2I6ZCh2q41U5voDnfnAfz0OJXJ31C1yEF7kARPC_9jiR_MYisR2L4tmDL4Jos6uewU82MrkhRoVmTQYQ43ZIg1xV)
21. [intlpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwEDfNnTvVelWaC_divMmMddFB_B0P3YCYo52lYhOHkt7bCzDt3wStPkrjHJABRsLmJbKO4SCIDJC8roZcEHAVRckz0nW99hTOd_FACfTBfEs_XgWLi7q3WFgSDeHsmeCcZqfnOy2powdD96VpULClRIlY4Q-aLPxnAqzrpvMXBYd3EClh8nUassR9D-_cpuJM5yWloAD0cxcnfwSoEqgc)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_HzXKYGHSXqek35B8IrEfHf2B5TkEnCsnI3osEryC6KJfW6zNLB8kYOt_lW17-b13u20hLEDZuImR0BOIWQN0mWsOvNk7Ou1l_wInfDgojONh2UjgVnckL-UA6xYMVuP4m-yC-uQiDL02WcLPVZTIaOD6IlCDEb9n8Ggip43Yw8cq56NYpoZpkM1EpP18Kpi1Mc3qTsC7X4jKnW-LhpQ=)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH55LDY-Km222kCCx7rN0j1Cd6soT-T_xQYMuWIWM1pbjlE5NXPVRj7WVY7Z53mlibazOoXW0j9T5UxlhWSoxrjgNQ5hgDi74aI8WmSqie9VDay07spv4Rx3sgDVnamIwmLeQkJDhhbCmgH05j0WHeMVzoEiTPC-JPuRNwxrGpdrK403WaSjdxoqIMW3A==)
24. [gatech.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaIfA5a9qm36tBPevcHO0h4gtiIWEAXyKC0Qr82pV2J9odUNZZE8h8oSrj1nEGNFISqaUxYIAB-T6fNfU5r8ssuXV3380MAIWAvmLEHt1pKYbz0NjZil1ZQUccPX4MMcLsNRRLIIG8c-d6TxFTf5bg-Y93FLKUQfKhbjGp8lpzO9u29cX6X43TjaYD4YQJeA==)
25. [icm.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJm6vq7QpwWHpf91lg8WBEOkve2gMSv3L_unrYGLxMwTlBzv-vG3pBmSghdCl24Ey4sO8STYNq-fmroZf6-NU752ni4A747rljRI80aUx7BIwvZfbDREJcQozAIV2vbg_98toD1ZMkOjg=)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGG9I5srGp-zk4Zjmp7wNFjZ5sljtMQjw0Wb9hsriyf4qzgSSHIU6tFIeSfPmj0Ypl1GCgEjHvVrZnkDblT2yNCCZWTV22J-dDPhN8xGdOW55VWwP5gN4MeKgJ9EirggI9ftvvlIQlaJYH1046meVRM-Gc1MsoW1LS_zOmw9o5Uqsv7XAOmJx1V4DROve1Ka6FL)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOBL5NOS_NJ3PxA4xJZVP3XIjxPh6CToBIybYPZH3vaw9eW19-MuSpLFTYDotkN4g8yvRhV3_NB9QwLFeNxn_wvNDBRytTzyOUMP1PIPVjYpigvhUGuw==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnREboMovHv-QGXWooTTtGPXR2BchdMQQOt93vQvn1SAjushDOpE6_XnUqflS-pG0TYj5Z0d11jxPQaHNjLCPE-h5LhuLFU4SfRHX9RNyEC41rP5JECw==)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvRSlj8n3yGE_MzOX5x-183IE5nIZEVAt5yJr6iMUQiWq7uZ23R_7cd3t2_fu5e4etDhCCqr1SoUvKlpwfbRJ_HGy3BenH_g7nAxT-Lwfr1Bln2_KFlHkKQw==)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIVjSFi-AT3Y0FYss56IGBszDJeEucRMsIhCUxJsz4_pBgbcSvkPZhTAMxJYYQKDtw1C8rJupFO3UKaOzsNZ2uP2ggzuLx-qPCw0tUyjD4p56sy_m-HA==)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4u9vn6S-j48ODgcKQYOPeWBaMSdL2tMULmkeiY5M4vOC9amklYc_ZSzakTWm5EQIEfbt1ltMEabYIbCzEePnysGHlaGE3UPFMM5wOzRz3pJAEAqw1yA==)
32. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKKPS2EXSlYOpeTQOdfs5mIN9HgDS-7XMzssMPqXV1SH31bcZdSYh22BGUdQ8vRG3d9PdExLBSPbD1PeFKuNkpUC4z8VFOtoUXtNOU8f4nr3xNyLee4Eo-Scnlpm5S4k2YtqARlDfmNUl5y8OllUyenSOo_Y0nSv2u-hq8fTQSe0v3euvlf28PPMM_XL1K4TaC2hWlxixd38LayAxmLv4nzBNtgyiR6YoyYxJZ_z76je9VS3M4thB4dfWxJq2cnJLce3y_5Q==)
33. [sinica.edu.tw](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlfvlACrAWNrMhsp7FlM7gmobIe4ynf1FTto7yiF1I3xox7QNA2mRf59Tka7WALrcX6WwsS0du2fgA_PoFfkeLWGejK9ZJaWX6NsZ-Uxm72Ho4x-qZsj5ryTOh6zv2h9B_MPZcFbRoVLMekw==)

