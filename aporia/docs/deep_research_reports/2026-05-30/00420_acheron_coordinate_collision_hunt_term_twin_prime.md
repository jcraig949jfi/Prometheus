# Acheron coordinate-collision hunt: term `twin prime`

**Pythia queue id:** 420
**Tier:** T5
**Priority:** 5
**Requested by:** Acheron
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdtU3NhYXFudkJPSzBfdU1Qb3BUTy1RTRIXbVNzYWFxbnZCT0swX3VNUG9wVE8tUU0
**Elapsed:** 2525s
**Completed at:** 2026-05-30T00:55:18.841512+00:00

---

# Acheron Intake Report: Coordinate Collision and Falsification Signals in Twin Prime Literature (2024-2026)

**Executive Summary:**
*   **Mission Parameter:** Acheron (Charon swarm, HARD-5 coordinate-collision detector) has conducted a sweep of recent (2024–2026) mathematical literature, preprints, and related academic discourse to identify Substrate Type A events: cases where the term `twin prime` (or its immediate equivalent) is modeled using two or more distinct, non-isomorphic coordinate systems that are subsequently conflated, leading to a collision-as-falsification signal. 
*   **Search Limitations:** While the intake parameters specifically targeted three to five peer-reviewed primary literature cases featuring fatal proof collisions flagged by formal errata, the available corpus yields a spectrum of literature ranging from published journal articles to pre-print repositories and informal heuristic proofs. Due to the scarcity of explicitly retracted "fatal" mathematical proofs involving twin prime coordinate collisions in the narrow 2024-2026 window, this report provides the best available alternative information. It evaluates three specific candidate substrates that strictly meet the text-matching criteria (using the term `twin prime` alongside explicit mentions of multiple `coordinate systems`).
*   **Key Findings:** The investigation identified three varying levels of coordinate collision candidates. Candidate 1 (Sultanow et al., 2024) involves a transformation between Euclidean prime coordinate space and prime-index space, where the logarithmic curvature of the Prime Number Theorem alters spatial invariants. Candidate 2 (viXra preprint, 2025) involves modular toroidal inversions of primorial cylinders, where the row-index increment invariant differs. Candidate 3 (Informal Base-60 Manifold preprint, 2025) conflates binary prime density with sexagesimal "taxi-cab" coordinates. 
*   **Adjudication Status:** None of the identified coordinate collisions have been definitively flagged in formal errata, though their methodological conflations present strong falsification signals suitable for Iris's adjudication and eventual cataloging in `aporia/doctrine/substrate_vocabulary/`.

---

## 1. Introduction: Substrate Type A and the Mathematics of Coordinate Collision

The detection of coordinate collisions—specifically Substrate Type A (collision-as-falsification signal)—represents a highly specialized frontier in the automated or semi-automated verification of mathematical proofs. In the context of analytic number theory, and specifically regarding the twin prime conjecture, a coordinate collision occurs when an author maps the distribution of prime numbers into a specific spatial, modular, or geometric framework, and subsequently imports assumptions, metrics, or invariants from an entirely different, non-isomorphic framework without applying the necessary transformation Jacobians or conceptual translations.

### 1.1 The Twin Prime Conundrum

The twin prime conjecture, which posits the existence of infinitely many prime pairs $(p, p+2)$, has long been a fertile ground for both rigorous breakthroughs and flawed heuristic proofs. As noted in recent literature, while tremendous strides have been made—such as Zhang's 2013 proof of bounded gaps [cite: 1, 2, 3] and Maynard-Tao's subsequent refinements [cite: 3, 4]—the definitive proof remains elusive. Because the distribution of prime numbers exhibits both deterministic modular properties (such as those captured by the singular series $\mathfrak{S}(2)$ [cite: 3]) and pseudo-random statistical properties (as described by the Prime Number Theorem [cite: 2]), mathematicians frequently project prime numbers into synthetic coordinate spaces to isolate specific behaviors.

### 1.2 Defining the Falsification Signal

A Substrate Type A collision arises when these synthetic spaces are fundamentally incompatible. For example, treating a sequence of primes strictly as a linear vector space (where distance is defined by $p_{n+1} - p_n$) and simultaneously treating it as a logarithmic density space (where distance is measured by $\pi(p_{n+1}) - \pi(p_n)$) without acknowledging the nonlinear deformation between the two coordinates leads to a mathematical paradox. The "falsification signal" is the specific mathematical invariant—such as arc length, topological genus, or orbital energy—that holds a particular value in Coordinate System 1 but is demonstrably altered or broken in Coordinate System 2. When a proof implicitly relies on the invariant holding true across both without a valid bridging theorem, the collision falsifies the proof. 

Historically, such gaps in mathematical reasoning—where diagrammatic or geometric representations fail to translate perfectly into formal coordinate logic—have driven the evolution of mathematical rigor. For instance, the realization that the intersection of two circles in a standard diagram might not exist in a purely rational coordinate plane exposed critical gaps in Euclidean diagrammatic reasoning, prompting the development of stricter axiomatic foundations [cite: 5]. Modern coordinate collisions in number theory operate on a similar, albeit vastly more complex, epistemological fault line.

---

## 2. Acheron Intake Methodology and Search Parameters

The Acheron intake protocol relies on a rigorous lexical and conceptual sweep of the provided academic corpus. The specific constraints of the current search were as follows:
1.  **Temporal Window:** Literature published or drafted between 2024 and 2026.
2.  **Thematic Core:** Usage of the specific term `twin prime` or its immediate conceptual paraphrases (e.g., gap 2 prime pairs, Polignac's conjecture for $n=2$).
3.  **Structural Requirement:** Explicit reference to two or more distinct, non-isomorphic coordinate systems within the same localized text (paper, proof, or citation neighborhood).
4.  **Verification Output:** Mandatory extraction of the arXiv ID, DOI (where available), the precise quote demonstrating the coordinate duality, the identification of the specific invariant acting as the falsification signal, and the status of any formal retraction or erratum.

### 2.1 Limitations of the Current Corpus

It must be explicitly stated that finding highly rigorous, peer-reviewed proofs by professional mathematicians that contain *unnoticed, fatal coordinate collisions* which perfectly fit this schema is exceedingly rare in top-tier journals. Often, when professional mathematicians map primes between coordinate spaces, they correctly account for the transformation. However, in the vast ecosystem of mathematical publishing—which includes open-access journals, preprint servers like arXiv and viXra, and independent heuristic manuscripts—these collisions are rampant. 

Because the strict prompt instructions require extracting 3-5 primary literature cases, and the provided research results yield a mixture of genuine arXiv publications, viXra preprints, and independent scholarly texts, Acheron has identified the three strongest available candidates from the corpus. These candidates represent the best available data points reflecting the phenomenon of coordinate conflation in twin prime research.

---

## 3. Candidate 1: Logarithmic Deformation in Elliptic Curve Mapping

**Source Designator:** Sultanow, E., Amir, M., Hatziiliou, A., Tfiha, A. D., Tehrani, M., & Buchannan, B. (2024/2025). 
**Paper Title:** *On families of elliptic curves $E_{p,q}: y^2 = x^3 - pqx$ that intersect the same line $L_{a,b}: y = \frac{a}{b}x$ of rational slope.*
**Identifiers:** arXiv:2401.00215 [cite: 6, 7, 8, 9, 10]. (Published in an MDPI-affiliated journal context) [cite: 11].

### 3.1 The Conflated Coordinate Systems
This paper attempts to derive sufficient conditions for the existence of non-trivial rational points on a specific family of elliptic curves parameterized by odd primes $p$ and $q$ [cite: 2]. In doing so, the authors map the problem into two distinct spaces:
1.  **Euclidean Value Coordinates $(p, q)$:** A spatial mapping where the axes represent the actual integer values of the primes $p$ and $q$.
2.  **Prime-Index (Logarithmic) Coordinates $(\pi(p), \pi(q))$:** A spatial mapping where the axes represent the index of the prime (i.e., its position in the sequence of primes, governed by the prime counting function $\pi(x)$).

### 3.2 The Collision Quote
The authors explicitly recognize the coordinate transformation but encounter structural anomalies (arcs instead of straight lines) when shifting between these non-isomorphic spaces. The critical lines where both coordinate systems and the mathematical tension between them appear are:

> "The transformation factor between both coordinate systems is logarithmic due to the prime number theorem [cite: 12, 13] stating that the i-th prime number pi grows roughly like pi ∼ ilog(i). Hence, p ∼ π(p) log(π(p)), q ∼ π(q) log(π(q)). The function xlog(x) is locally curved, hence the figures of cases 17, 40, 47 and 56 show arcs instead of..." [cite: 2].

And parallelly articulated as:
> "The transformation factor between the two coordinate systems is $\frac{\log(p_{max})}{\log(q_{max})} \approx \frac{\log(\frac{1}{16} q_{max})}{\log(q_{max})}$" [cite: 11].

The direct link to the twin prime structure is established within the exact same methodological framework:
> "According to Polignac's conjecture [cite: 11] (which is not proved), there are infinitely many cases of two consecutive prime numbers with the difference n if n is even [cite: 14] (p. 295). If a = 1, this is well known as the twin prime conjecture [cite: 15, 16]" [cite: 11].

### 3.3 The Falsification Signal (Invariant Failure)
The invariant in this collision is the **linearity of the geometric distribution (local curvature)**. In a purely arithmetic Euclidean coordinate system $(p, q)$, constraints such as $q - p = 2a$ (which reduces to the twin prime conjecture when $a=1$) represent strict linear relationships [cite: 11]. A set of twin primes plotted in a linear coordinate system $(p, q)$ would fall on a perfect straight line parallel to the identity diagonal. 

However, when transposed into the index-coordinate system $(\pi(p), \pi(q))$, the distribution undergoes a logarithmic deformation. Because the prime number theorem dictates that the density of primes thins out at higher magnitudes, a linear relationship in Euclidean space becomes a non-linear "arc" in index space [cite: 2]. If a mathematical argument or graphical proof relies on geometric intersection properties (such as lines intersecting specific orbital fields) holding true across both visualizations, the proof experiences a falsification signal. The topological straightness (curvature $\kappa = 0$) is broken, as "the function xlog(x) is locally curved, hence the figures... show arcs" [cite: 2].

### 3.4 Erratum / Flag Status
There is no currently recorded formal erratum, correction, or comment paper explicitly flagging this mapping as a fatal proof error in the corpus. The authors themselves note the curvature artifact. However, as an Acheron candidate, it serves as a high-grade example of how attempting to link the structural rigidities of the twin prime conjecture with the logarithmic density of the prime index space generates distinct coordinate friction.

---

## 4. Candidate 2: Topological Inversion in Primorial Sieve Mechanics

**Source Designator:** Anonymous / Independent Author (2025).
**Identifiers:** viXra:2501.0157v1 [cite: 17]. (Note: viXra is an open repository; no formal DOI is typically assigned).

### 4.1 The Conflated Coordinate Systems
This manuscript attempts to address the Hardy-Littlewood K-tuple Conjecture [cite: 17], of which the twin prime conjecture is the foundational case. The author models the prime sieve using a continuous bitstring representation that wraps around upon itself, creating a topological cylinder based on the primorial $p_n\#$. The two coordinate systems at play are:
1.  **Linear Modular Sequence (Standard Bitstring):** A flat, 1-dimensional array extending infinitely, where a twin prime is defined strictly as a specific subsequence pattern, e.g., "(1, 0, 1)" [cite: 17].
2.  **Inverted Primorial Cylinder Coordinates:** A 2-dimensional toroidal mapping where the linear string is wrapped into rows and columns modulo $p_n$, creating a geometric structure that can be inverted.

### 4.2 The Collision Quote
The author explicitly attempts to map the twin prime bitstring pattern onto two competing coordinate geometries, leading to topological inversion constraints:

> "Let a candidate twin prime be a subsequence in a bitstring that matches (1, 0, 1). The bitstrings of S are periodic over the entire number line, so we include the candidate twin prime that would be formed when joining the ends of a bitstring... The coordinate systems of the two cylinders are inverses of each other, and transforming one into the other is akin to turning a punctured torus inside-out, whilst ensuring the symmetries are maintained. We seek a formula for $J_{p_n}$, the increment in row index modulo $p_n$ per increment in column index." [cite: 17].

### 4.3 The Falsification Signal (Invariant Failure)
The invariant under threat here is the **row index modulo increment ($J_{p_n}$)** and the **integrity of the neighborhood topology**. In standard linear arithmetic coordinates, the gap between twin primes is rigidly defined by the scalar value 2. However, in the dual-cylinder coordinate system proposed by the author, turning the "punctured torus inside-out" requires an isomorphic mapping of distance metrics [cite: 17]. 

When the linear distance is wrapped around a primorial modulus, the adjacency required to define a "twin prime" (the `1, 0, 1` pattern) is subjected to boundary conditions. The falsification signal occurs if the metric space is inverted but the index increment $J_{p_n}$ is not proportionally translated through the inverse Jacobian. The author states that "$J_{p_n}$ is an integer greater than 0 and less than $p_n$" [cite: 17]. If one assumes that a pattern matching $(1, 0, 1)$ at the "ends" of the bitstring in the linear coordinate system translates isomorphically to a continuous twin prime in the inverted cylindrical coordinate system, the topological invariant (the Euler characteristic of the punctured torus, or the continuous arc length of the sequence) breaks down without severe compensation. 

### 4.4 Erratum / Flag Status
As this is a 2025 viXra preprint, it has not undergone formal peer review, nor is there an associated comment paper or erratum. It stands as a prime Substrate Type A candidate for automated theorem provers because the conflation of a linear bitstring space with an inside-out toroidal coordinate space fundamentally alters proximity metrics.

---

## 5. Candidate 3: Base-60 Manifolds and "Taxi-Cab" Prime Hexagons

**Source Designator:** Informal Preprint / Self-Published Manuscript via Reddit Academic Sub-communities (2025-12-09).
**Identifiers:** No formal arXiv ID or DOI available. Title cited as: *Let's solve the twin prime conjecture together as...* [cite: 18].

### 5.1 The Conflated Coordinate Systems
This candidate highlights a profound coordinate collision characteristic of outsider mathematics attempting to resolve deep number-theoretic issues. The author attempts to prove the twin prime conjecture by abandoning base-10 mathematics and utilizing a sexagesimal (base-60) grid. The two systems are:
1.  **Standard Base-10 Arithmetic (The "Lens"):** The traditional linear progression of natural numbers, which the author claims induces an "illusion" of computational complexity and random prime distribution [cite: 18].
2.  **Sexagesimal "Babylonian" 2x3 Tiled Space:** A synthesized 2-dimensional grid where every integer is assigned a coordinate on a hexagonal or tiled manifold. Within this grid, distance is measured using "taxi cab geometry" [cite: 18].

### 5.2 The Collision Quote
The author explicitly juxtaposes the standard approach with their novel coordinate system, stating how the twin prime signal stabilizes when the coordinate system is shifted:

> "My current idea on how to do this is to represent the entire Natural number line as a 2 by 3 tiled space, so every natural number has a specific coordinate on this grid. In taxi cab geometry all tiles on this grid are size 3... By returning to the Babylonian coordinate system, we have documented the eternal clockwork of the universe." [cite: 18].

Further illustrating the coordinate collision when attempting to measure the twin prime distribution:
> "In the Sexagesimal Solution, P = NP because the 'Search' for factors or primes is an illusion caused by the wrong coordinate lens... As the coordinate scale increases, we observe a radical 'bundling' of the tracks... The 'Signal' of twin primes does not decay; it merely stabilizes into the permanent grid capacity of the 60-base manifold." [cite: 18].

### 5.3 The Falsification Signal (Invariant Failure)
The primary falsification signal here is **Isotropic Sieve Pressure (Twin Prime Density)**. In traditional probabilistic number theory, the density of twin primes decays logarithmically, bounded by expressions involving Brun's constant [cite: 16] and the Hardy-Littlewood conjecture, leading to a vanishing density $O(x / \log^2 x)$ [cite: 3, 16]. 

However, by shifting to a 60-base "taxi-cab" coordinate system, the author claims that the signal "does not decay; it merely stabilizes" at a "16.67% mean" [cite: 18]. This is a severe coordinate collision. The metric of prime density is fundamentally invariant to base representation (a prime is a prime in base 10 or base 60). The author conflates the modular regularity of numbers non-divisible by 2, 3, and 5 (which indeed form a repeating pattern of 16 'slots' every 60 integers, roughly 26.6%) with the actual density of prime numbers. The invariant (asymptotic density of primes) is falsified because the author assumes that the geometric properties of their synthetic 2D coordinate system inherently represent prime distribution, rather than simply representing modular arithmetic constraints. The use of taxi-cab metric spaces to bypass standard Euclidean distance measures further scrambles the analytical limits.

### 5.4 Erratum / Flag Status
This text is an informal pre-print / forum dissemination. While immune to formal academic errata, it is a perfect pedagogical instance of a Substrate Type A collision. The author explicitly names the coordinate mapping as the solution, and the resulting mathematical output contradicts fundamental theorems of arithmetic density.

---

## 6. The Broader Context: Coordinate Collision as an Analytical Tool

The phenomenon tracked by the Acheron system is not merely a catalog of errors; it represents a fundamental boundary condition in mathematical modeling. The transition between linear spaces, logarithmic spaces, toroidal spaces, and modular grids is fraught with "differential invariants" [cite: 13]. 

### 6.1 Parallels in Hybrid and Dynamical Systems
Interestingly, the concept of coordinate collision and the preservation of invariants is rigorously defined outside of pure number theory, specifically in the realm of hybrid computing and continuous physical systems. As noted in the literature surrounding the verification of hybrid systems, "numerical approaches can be used for falsification... but not (ultimately) for verification" [cite: 12, 13]. In tasks like tracking "roundabout maneuvers in air traffic management and collision avoidance in train control," analysts rely on differential invariants $\mathcal{F}$ [cite: 13]. The formula $\nabla_D \mathcal{F}$ serves as a directional derivative of $\mathcal{F}$ in the direction of the dynamics of $D$ [cite: 13]. If the gradient vector violates the continuous invariant boundary, a physical or coordinate collision is detected.

While analytic number theory operates discretely, the mapping of prime numbers onto continuous functions (like the Prime Number Theorem or logarithmic mapping) essentially borrows from these continuous dynamics. The failure to maintain the invariant (such as the linear gap between twin primes $2k = 2$ [cite: 16] when translated into a logarithmic space) is the discrete analog of a differential invariant failure. 

### 6.2 Structural Persistence and Spectral Formulations
When properly handled, coordinate transformations can illuminate deep truths about twin primes. As highlighted in discussions of spectral formulations, the structural persistence of twin primes can be modeled through correlation functions. The prime two-point correlation is given by $C(h) = \lim_{x\to\infty} (1/x) \sum_{n \le x} f(n)f(n+h)$ [cite: 3]. When researchers project this into a spectral representation, the singular series $\mathfrak{S}(h)$ measures the "phase coherence between prime modes" [cite: 3]. 

A rigorous mathematician understands that mapping from integer space to frequency/spectral space requires a Fourier transform ($\sum f(n)f(n+2) = \int |\hat{f}(\theta)|^2 e^{2i\theta} d\theta$) [cite: 3]. A coordinate collision occurs precisely when an author skips this transform, attempting to read the structural persistence directly off a naive graphical coordinate mapping (as seen in the "taxi-cab" geometry or uncorrected Euclidean-to-Index mappings).

### 6.3 The Necessity of Base Symmetry
The recurring issue in these collisions is a misunderstanding of scale separation and binary structure. As seen in recent explorations of prime binary representations, odd integers function as a "directed binary boundary with asymmetric Hamming neighborhood" [cite: 19]. Twin prime pairs $(p, p+2)$ have specific carry dichotomies depending on their residue classes modulo 4 [cite: 19]. If an author maps these properties onto a new coordinate space (like a base-60 hexagon or a toroidal cylinder) without maintaining the integrity of these binary carry operations, the spatial logic breaks down. For instance, the "shared ancestry horizon" ensures that for a twin-prime pair $p$ and $p+2$, the integers share identical upper-bit ancestry [cite: 19]. A coordinate system that folds or wraps the number line indiscriminately will destroy this bitwise ancestral invariant.

---

## 7. Substrate Terminology and Lexical Vectors in the Periphery

During the Acheron sweep, several other notable usages of coordinate mapping related to prime numbers were detected. While they do not feature the rigorous conflation of two specific coordinate math spaces *within the same proof*, they demonstrate the pervasive conceptual bleeding of physical spatial geometries into prime number theory.

### 7.1 Prime Number Orbitals and "Matter"
In a highly speculative manuscript, the twin primes $\{2, 3\}$, $\{3, 5\}$, and $\{5, 7\}$ are treated as "3-perpendicular vectors," allegedly giving "s-orbitals their spherical 3D embodiment and an x, y, and z spatial coordinate system" [cite: 20, 21]. The authors argue that overlapping these twin prime pairs defines $p$-orbitals [cite: 20]. This operates less as a coordinate *collision* and more as a complete superimposition of quantum mechanical coordinate systems onto number-theoretic sets. The "invariant" here is the Fine Structure Constant ($\alpha \approx 137.036$), which the author attempts to reverse-engineer using property sets of twin primes [cite: 20]. 

### 7.2 The Nexus Recursive Universe
Similarly, another text characterizes the "Mass Gap" in physics as the "physical manifestation of the Twin Prime Gap," arguing that the universe "enforces a gap of '2' (in dimensionless lattice units)" to preserve reality resolution [cite: 22]. This text explicitly divides space into "Left-Right Dimension" (Sequential) and "Front-Back Dimension" (Orthogonal) [cite: 22]. While these are not formal mathematical coordinate systems used in analytic proofs, they map exactly to the lexical patterns of Acheron's intake constraints, showing how the term `twin prime` operates as a gravity well for exotic spatial theories.

---

## 8. Conclusion and Next Steps for Iris Adjudication

The Acheron intake process successfully isolated three primary structural candidates for Substrate Type A coordinate collisions involving the term `twin prime` within the 2024-2026 target window. 

1.  **Sultanow et al. (arXiv:2401.00215):** A high-value candidate demonstrating the mathematical friction between Euclidean prime mapping and index-logarithmic coordinate mapping. The invariant falsification signal is topological curvature. 
2.  **viXra Primorial Cylinder (viXra:2501.0157v1):** A medium-value candidate showing the breakdown of sequence distance invariant $J_{p_n}$ when a 1D linear coordinate is mapped to an inverted 2D modular torus.
3.  **Base-60 Hexagonal Manifold:** A pedagogical candidate demonstrating how taxi-cab coordinate mapping induces a false stabilization of prime density metrics, explicitly falsifying the Prime Number Theorem.

**Landing Path Recommendation:**
These extracted quotes and invariant maps will be deposited into the `charon/agents/acheron/artifacts/collision_candidate_[timestamp].md` intake manifold. Iris's adjudication protocols should specifically focus on cataloging the `Euclidean -> Index-Logarithmic` transformation failure as a foundational vector for `catalog_edit` candidates against `aporia/doctrine/substrate_vocabulary/`. By explicitly recognizing how uncompensated spatial Jacobians falsify heuristic prime proofs, automated theorem provers can be better calibrated to reject false positive twin prime solutions that rely on implicit coordinate shifts.

**Sources:**
1. [ycombinator.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-wSoZ8ad2C_kDJaKeSXJwzp5uxwDeTUKKrn5rKhMSUyYKjGVWqwSlUn-x7EQcf_7rFODqmOU6NB0v8vlmns01ett3ZSEbQAS7LMmoj1fmDZzPxv2IbO2OaoYBGAXkWnvf7C8=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDj1uMGYek_Brv4F9FM5ykw0bYPM4qi3dARhdM4BaM1qJ-mRNciMB2XwyB75apMVTjJ-4-nOlUsk2gbesiRcYNnSdGrkePnu1LkaoIhXOKr32lTLBYIg==)
3. [christosenergy.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFb6x8pcag3jBX439mvOMadjsiROJLykjQceeocKRw_2NhIQ2j4Tkfeq6jqioalEBYWXIu5Mo8vi5A95468jKTu33iLYSOOGBIhFHJegS7J-ZKOAgKotyeIetsOEDb-aw3bmzIyEWGJ82kEgPOHKBRHaYeyZNKMQLvFkqlzVivDsjAEPnY2DbU8hzPb)
4. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFew4r0CMlhPp5c9rWfDfq3WKLUiLVlTGqdVED-jKhOAethKvtWfOU5qMqpx-lw7A4X0NWIoUQ0eqWd3CGlHDqqLT1IGAgiGtjjHt9EoH_a6TZXfIwE75OdQ5aaoPB3BAehbIob)
5. [scholaris.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcwG4Dz30NZDCuQvFcI_u8o89G7xSm6OZAAMI1GefEBYl4Eu0P1kGpEWWR-1ojq3gOp_8NKv4NHRiGtQkrV-le0Cy0HFJQK1JMWRaVIX2550HX46T0C8Yi8P6_xow2aOeZuHL8MBknwr7j5AFFtHF_9Ksih3jPvXuZof8U0hW6Vs4rKstX3e5yt5uf3Q==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExyuzLZ1LoExoOt_eOkl6ghJQPOJTmTXeazefvx4u598as4dQBgsZF3rcEWI9Wewr-ti_eh_a4GU9eCcu7M4ZW9kUJMNnlrNewm-yFqxO_4Jx_iVyrTj1K6_28yyOrFceZRvUuWXz7ncU=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-rPYFWfPa3xfhbmxAc6E3G0_ura1IYwJs5TxHiswFZCE8u1CLmfFDZV0hRR-fBwtEn4dSwEFbYbhOLAjbVVb942nL3O81xwTGXom2xw41t0tCpii4JA==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3wYah5Ie5Tz4N8982O2GER70Ipa0KnpwcbT40nfiTrArwV9EyNySK790uBazK4iWbNeYJtibhDiXj8qV3PZYAmdZueEsiKPTRI0y0Q_4RVQi4FmZASYB5ig==)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6ZRS2bxLHMMQRLaK1ub0FjS5jWdbwX_VwL0Qhft1UBKkyHw6ZGC2TxmV8GlAHPapdl7vheBktQqrsDLX-FBGWJFLbjBqYOoIFsfZ_onGoFub4MSmSFCyL5HtqOfFvJIN9-msfZKdL1WYakELn6ra9WG8n_3x3nPamTpHxBEoob0PnlgTqcmoQjwth4Q==)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEf_biRxW8f0MNHGaV4k5HcX3S3RfflayU30fYMdxn1igi0CWztf7HF_fM8aBvOo9dlo2Fs7w7mYShNzy-GKBwsMhiIK_1pHYRMznfyT7fAMn4Q_2dRscRZio63J_CRHA69_6bJJ9f9tz80s8h53DhFgtTEXUfmo68CDA==)
11. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETWFBfaDhNwGgBjEL1I4mVOhRth6PRZwAYlKAxwoRb8bUSyy0LWhOIFzLshzQRlyFghE8SBGWWXvPW6VhhaUrsLx9bvSYanI5uNFoiBocSOX-F58wzfyqYX2Hu)
12. [dtic.mil](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsnYua7EANzkV_jXIq6V5VC6e6ItG56BZ_lbrPHe_h1T9R-BpmxAVM33U0wllP-qLceP6E0s1oUP9IaY2tXb12VsVtXj6hBzjf266f6n9LAN8N7U7pQKTVNbe78aEeMqaMFwHm)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkk4LR8sIiI5qqROCyiF82vXrx4kj7_yjRHlnk9fdxIztz01QJe_TAMqqsNELvVNyMQ2ycRXdmotsCxr3tBBmHQL01C-5S_HO-HGYh9ITQY67Y-YVkRmGn7v-nERR3DidrzCQsNVMrn4IpYs_kk1eJygBcU7yIn30JbHrVp3Ba4Ksa8Q409tnHMGZ7W4HqwEKAlybNO_UvL9Qsfkheeu1vIUZwJbpXNc-QJW4=)
14. [quora.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtcz0EdTLnbs6TB4ZBxojNZUm8FktkMFWjqUoa2LctiKh7RnQQK9hvsPy6kLth1HpKYXEc-YP5dcpdrjZR4MGTa6ku5-YeFRwWeKTz4zF-02-5I9-faUZFXqxzNUxkHf6K9Gry1EFFCbcDKQ9dAbAqXFWK1DwWrQuCHmGlOXiJk9_Nh6n6FHXQn7o=)
15. [kappamuepsilon.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpgFr9osyiaDHRnDD2Hd_cAVnrNnb21T0HdYUzWVl6UmpaTHa87OnpB_-1-cW6gX8wRgaSyw4QMVhh5JV4pPeIdK9PM8NeGLa7yUVfvL82bTDSpvhWl9jYj50VshV19QKKpZNsnnVvx73QInw2qG2eWCSJcEFFaohwKg==)
16. [rapiddoctools.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvgwdUw8Y5_qI-NYW7wlrxkpmBBxRiFsSNAHelEQ6t-tKTXNyFrIDMHQGSQfkZTyhxlOus0_S4tLSTyl7O6NpLkR4yOgziOQgKEU887tvzYesEwu4_gPqZ4ZhFzJiiw6TfPknjABXRRyBYZ1FQwRJ8MRX6XR_-dHSCOOE2VP8YGlzGM6IXINvksedB59hjDw0GPZ0n)
17. [vixra.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpWCaY4ml54U6TilBEbA9sltxlYylO2aCgiS1X-F8woWEwM6QWMSEZ4FIlckjdDfr2iMWc1tx5oZ0MQgjeKXQniPbgDGfwoES95q6KEXzM9Xj7XzXWj-rmey2C)
18. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbtCLT5Rmzm4_OZaYmo57185PbkGgizLMZyXfN6ibgVvAyQqv9fCsU13tvh1Td5iKxBh2BUDM73jy365xIwN0rdNgJ7HcrLzSqNN5vKkH1Advf5mBei-CUC3zlK-78ktc5mxYWGNYsWie0DtSJllxpOadc4O2Ryee_JsTdDXRo0AXYK69gGbblloU0jqnvWm9zHptBA1MO2e10allQ)
19. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOEdF9qO2rA33J9ocl5XiJPZIXHQ4udupBPIST0PVmzP_beMPHsc-aTnuB-AdmCjZFGDWRv7RQdbuSzC6an_3aXvc03LVBegFOomiggilKHwZMkVXFFRz_-RAweK-Ne6dyQZc8toBOdsr37d7RPPuw_njAdujeBfJui1pQDn4DVa31cXW5R-Ih0pH1KghczchWzd3l21ijOuFnLyg=)
20. [scirp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcUsBaC_q97xw475nx77bOPwLRd5C694C1bqxIjJey1nFepfWiqDtv5s2gcww92NQM0R4-7SuWA-mpKza-Z4M2zX1Gj7PNueOHIrjs_1zIF20P9H2sNKd-rL22mKz25JpioI7dAH39rNhQUNYc-vplekI_)
21. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsObPLDu1z3gPeChYLRnYmXBjB_9W5jvOntbF_pQVQJDD0bCK7yk1n5bgts5SYhumk2_KyxDefJ-Fnt1uMTz02WZVQnO7lFNQDQ8cA6_m7KocrG4R5fQsy2L1Qmv3imGadBe4EuM6pUv3HXUDchQMhh80OjnjfpuL6qcfooOEoBIDY0bAEZiM7TWj0_mx-Nmu0B2uzQw==)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrzSIzRTJG50o5icGdiWLDbhXZ_CejmnAFiFEErRFDr1QFkcsTbdz8dDcSQEvhZB3qjoBwftmvPODY720HHSTpI-BXRtGzpcrxQxvf_HHgTBZJVzLzKNOLlFSOLhE1VQ77BT9w9CL0mB_nxnyIdWxFvl8-KoTHty9IpdUROkf88c3gsSFHh3YWSww=)

