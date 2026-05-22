# Followup [FU-2026-05-22-034 <- row219]: # Ergodic Theory and Multiple Recurrence: The 2024-2026 Frontier of Furstenberg and Host-Kra Structu

**Pythia queue id:** 319
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdHYmtQYXAtYkRmeThfdU1QN0otNnVRURIXR2JrUGFwLWJEZnk4X3VNUDdKLTZ1UVE
**Elapsed:** 185s
**Completed at:** 2026-05-22T02:05:07.154881+00:00

---

# Ergodic Theory and Multiple Recurrence: The 2024-2026 Frontier of Furstenberg and Host-Kra Structure Theory

**Key Points**
*   Research strictly confirms the breakdown of the Abramov system conjecture in low characteristics; specifically, a Host-Kra $\mathbb{F}_2^\omega$-system of order 5 is not Abramov of order 5, revealing deep non-measurability obstructions for the $U^6$ Gowers norm.
*   The structural theory of Host-Kra factors for bounded-exponent abelian groups has been revolutionized by the introduction of Polynomial Towers, which bypass the need to extend the underlying group.
*   The Bergelson-Tao-Ziegler (BTZ) conjecture holds for $k \le p+1$ but fails fundamentally at $p=2, k=5$.
*   Every ergodic $\mathbb{F}_p^\omega$-system of order $k$ is structurally a factor of an Abramov $\mathbb{F}_p^\omega$-system of order $k$, resolving a critical fallback question despite the BTZ breakdown.

**Contextual Overview**
The mathematical intersection of ergodic theory, additive combinatorics, and higher-order Fourier analysis has experienced profound phase transitions between 2023 and 2026. The initial optimism surrounding the universal applicability of classical Abramov structures to Host-Kra factors has been permanently adjusted. While the high-characteristic regimes behave predictably, low-characteristic regimes possess deep algebraic and cohomological anomalies. The evidence leans heavily toward the conclusion that these structural obstructions are not merely pathological edge cases, but fundamental features of nilpotent structures over low-characteristic fields.

**Methodological Shift**
To resolve these newly discovered algebraic dead-ends, the field has pivoted away from naive classical polynomial mappings toward sophisticated nilspace-theoretic fibrations and the entirely novel framework of *polynomial towers*. These approaches do not require intermediate extensions in the system to perfectly mirror Host-Kra factors, thus providing the necessary flexibility to integrate exact polynomial cocycles.

***

## 1. Brief Summary
**The question in one line with Prometheus context:** How can we algebraically and dynamically classify the limits of multiple ergodic averages (Host-Kra factors) for bounded-exponent abelian groups, and to what extent do low-characteristic cohomological obstructions invalidate the Bergelson-Tao-Ziegler conjecture regarding Abramov systems?

**Prometheus Context:** Within the Aporia deep-research tracking architecture, this query represents a critical node in the resolution of structural theorems in higher-order Fourier analysis. It explicitly bridges the combinatorial "inverse Gowers theorems" with continuous topological dynamics (Furstenberg-Host-Kra theory). The 2024-2026 paradigm shift—marked by the refutation of the BTZ conjecture and the synthesis of Polynomial Towers—acts as a fundamental baseline correction for our models of nilspace fibrations and measure-preserving dynamical systems.

## 2. Flagged Findings
The current consensus in the field has rapidly solidified around a set of breakthrough results from 2023 to 2026, fundamentally altering our understanding of measure-preserving systems of order $k$.

**Consensus on the Failure of the Bergelson-Tao-Ziegler Conjecture:**
It is now universally accepted that the Bergelson-Tao-Ziegler conjecture—which posited that every Host-Kra $\mathbb{F}_p^\omega$-system of order $k$ is an Abramov system of order $k$—is false in low characteristics [cite: 1, 2]. Specifically, Jamneshan, Shalom, and Tao demonstrated that the conjecture fails catastrophically for $p=2$ and $k=5$ [cite: 3, 4, 5]. They constructed a Host-Kra $\mathbb{F}_2^\omega$-system of order 5 that is strictly not Abramov of order 5 [cite: 6, 7, 8]. The consensus highlights that this failure is deeply tied to the fact that the $\sigma$-algebra of the system cannot be generated modulo null-sets by phase polynomials of degree $\le 5$ [cite: 9].

**Non-Measurability of the Inverse Theorem:**
A critical flagged finding accompanying the BTZ failure is the "non-measurability" of the inverse theorem for the $U^6(\mathbb{F}_2^n)$ norm [cite: 6, 10]. The researchers produced a bounded function $f: \mathbb{F}_2^n \to \mathbb{C}$ with a large $U^6$ Gowers norm that correlates with a non-classical quintic phase polynomial $e(P)$. However, all such phase polynomials are "non-measurable"—meaning they cannot be well approximated in $L^2$ by functions of a bounded number of random translates of $f$ [cite: 1, 2, 5]. This implies that the algorithmic extraction of polynomials (e.g., via a Goldreich-Levin type bounded-time randomized oracle) might not be possible in bounded time for higher degrees in low characteristics [cite: 3, 4, 10].

**Consensus on the Positive Factorization Resolution:**
Despite the BTZ conjecture's failure, a positive fallback has been definitively proven by Candela, González-Sánchez, and Szegedy: every ergodic $\mathbb{F}_p^\omega$-system of order $k$ is a *factor* of an Abramov $\mathbb{F}_p^\omega$-system of order $k$ [cite: 11, 12, 13]. This answers a follow-up question posed by Jamneshan, Shalom, and Tao, and is achieved by studying $p$-homogeneous nilspace systems [cite: 9, 13].

**The Paradigm of Polynomial Towers:**
For arbitrary abelian groups of bounded exponent, the consensus now relies on the newly developed Host-Kra and inverse Gowers theory utilizing *polynomial towers* [cite: 14]. Jamneshan, Shalom, and Tao proved that Host-Kra factors $Z^{\le k}(X)$ admit extensions with the structure of polynomial towers—a finite iteration of abelian extensions of the trivial system by polynomial cocycles [cite: 15, 16, 17]. All such extensions are Abramov and have the structure of $k$-step translational systems [cite: 14, 15].

**Where the Consensus Might Be Wrong (Flagged Vulnerabilities):**
*   **Algorithmic Implications:** The assumption that the non-measurability result entirely destroys the possibility of *any* polynomial-time algorithmic inverse theorem may be overly pessimistic. While bounded-time randomized oracles fail, the space of deterministic structured algorithms utilizing global nilspace properties has not been fully exhausted [cite: 3, 4].
*   **Calibration Note:** Historically, researchers exhibited `PATTERN_BASE_RATE_NEGLECT` by assuming that the high-characteristic structural equivalence of inverse theorems would seamlessly translate to low characteristics, ignoring the baseline base-rate of unique cohomological obstructions endemic to $p < k$ regimes [cite: 3, 18]. This base-rate neglect led to overconfidence in the universal applicability of the classical BTZ conjecture.

## 3. Problem Statement
The central mathematical objects being interrogated in this frontier are measure-preserving dynamical systems, Host-Kra factors, Gowers uniformity norms, and Abramov systems. The precise problem is the structural description of the limits of multiple ergodic averages and the exact algebraic nature of the spaces characterizing these limits.

**Measure-Preserving $\mathbb{F}_p^\omega$-Systems:**
Let $p$ be a prime. We consider a measure-preserving system $(X, \mathcal{X}, \mu, T)$, where $X$ is a probability space and $T$ is a measure-preserving action of the countable discrete abelian group $\mathbb{F}_p^\omega = \bigoplus_{i \in \mathbb{N}} \mathbb{F}_p$ [cite: 4, 9].

**Gowers-Host-Kra Seminorms and Factors:**
For $f \in L^\infty(X)$, the Gowers-Host-Kra seminorms $\lVert f \rVert_{U^k(X)}$ are defined inductively via multiplicative derivatives $\Delta_h f(x) := f(x+h)\overline{f(x)}$ [cite: 3, 4, 9]. The $k$-th Host-Kra factor, denoted $Z_k$ or $Z^{\le k}(X)$, is defined up to $\mu$-null sets by the property that $f \in L^\infty(X)$ is $Z_k$-measurable if and only if for all $g \in L^\infty(X)$ with $\lVert g \rVert_{U^{k+1}} = 0$, we have $\int_X f \bar{g} d\mu = 0$ [cite: 9]. A system is said to be of order $k$ if it is isomorphic to its $k$-th Host-Kra factor [cite: 9, 19].

**Phase Polynomials and Abramov Systems:**
A function $P: X \to \mathbb{T}$ is a phase polynomial of degree $\le k$ if its $(k+1)$-th derivative vanishes identically. We denote the group of such polynomials by $\text{Poly}_{\le k}(X)$ [cite: 4]. An ergodic $\Gamma$-system $X$ is an **Abramov system of order $\le k$** if its $\sigma$-algebra is generated (modulo null sets) by phase polynomials of degree $\le k$ [cite: 9, 14]. 

**The Interrogated Result (Bergelson-Tao-Ziegler Conjecture):**
Conjecture 1.2 (BTZ): For every ergodic $\mathbb{F}_p^\omega$-system of order at most $k$, the $\sigma$-algebra of $X$ is generated by the polynomials in $\text{Poly}_{\le k}(X)$ [cite: 4, 19]. Essentially, every Host-Kra $\mathbb{F}_p^\omega$-system of order $k$ is an Abramov system of order $k$ [cite: 1, 2].

**The Interrogated Result (Inverse Gowers Theorem):**
Conjecture 1.3 (Strong Inverse Conjecture): If a bounded function $f$ has $\lVert f \rVert_{U^{k+1}} > \eta$, then $f$ correlates with a phase polynomial $P$ of degree $k$, and furthermore, $P$ is "measurable"—meaning it can be approximated by some combination of random shifts of $f$ [cite: 2, 3].

The frontier of 2024-2026 interrogates exactly where these structural equivalences break down (at $p=2, k=5$), how to bypass these breakdowns using nilspace fibrations to find Abramov factors, and how to construct exact polynomial towers to retain inverse theorems without requiring the Host-Kra factor to strictly equal an Abramov system [cite: 1, 13, 14].

## 4. Status & Bounds
The landscape of bounds and structural status has been drastically updated. The dichotomy between high and low characteristics is now formally rigorous.

**Current Known Status:**
1.  **High Characteristic ($k \le p+1$):** The BTZ conjecture is **TRUE**. It was verified by Candela, González-Sánchez, and Szegedy that for an ergodic $\mathbb{F}_p^\omega$-system, $Abr_k(X) = Z_k(X)$ for $k \le p+1$ [cite: 1, 9, 12].
2.  **Low Characteristic ($k > p+1$, specifically $k=5, p=2$):** The BTZ conjecture is **FALSE**. A Host-Kra $\mathbb{F}_2^\omega$-system of order 5 is not Abramov of order 5 [cite: 1, 5, 6]. The strong inverse conjecture for the $U^6(\mathbb{F}_2^n)$ norm is simultaneously **FALSE** [cite: 4, 6, 10].
3.  **Factorization Status:** **TRUE** universally. Every ergodic $\mathbb{F}_p^\omega$-system of order $k$ (even in low characteristic) is a factor of an Abramov $\mathbb{F}_p^\omega$-system of order $k$ [cite: 11, 12, 13].
4.  **Inverse Theorem for Bounded Exponent Groups:** **TRUE** qualitatively. A large $U^{k+1}$-norm implies large correlation with a polynomial of degree $\le k$ on the same group, even when the exponent is not square-free or is divisible by small primes. This resolves the question without extending the underlying group, utilizing Polynomial Towers [cite: 14, 16].

**Current Best Bounds and Conditional Qualifiers:**
*   **Degree Bounds:** In the high characteristic case ($p > k$), all non-classical polynomials are classical up to constant shifts. In the low characteristic case ($p < k$), a polynomial $P$ of degree $k$ has $pP$ of degree at most $\max(k - p + 1, 0)$ [cite: 3]. This degree drop is the algebraic root of the difficulty.
*   **Weak Inverse Bounds:** A weaker version of the inverse conjecture holds universally, where the polynomial $P$ is of degree at most $C(p,k)$ rather than $k$, for some constant $C$ depending only on $p$ and $k$ [cite: 4, 5, 13].
*   **Correlation Bounds:** The function $f$ constructed to disprove the $U^6$ measurability theorem exhibits correlation with a quintic non-classical phase polynomial $e(P)$, but any approximation requires an unbounded number of random translates [cite: 1, 2].
*   **Nilspace Bounds:** The structural theorem for finite $p$-homogeneous nilspaces describes them as images under nilspace fibrations of a simple family of filtered finite abelian $p$-groups. The nilspace $X_{5,5}$ (and its simpler version $X_{5,1}$) provides the bounded exactness necessary to disprove the conjecture [cite: 12].

## 5. Literature (Primary Sources)
The following primary sources strictly define the 2024-2026 revolution in Host-Kra structure theory and additive combinatorics. 

1.  **Jamneshan, A., Shalom, O., & Tao, T. (2026).** *Polynomial towers and inverse Gowers theory for bounded-exponent groups.* arXiv:2601.00961 [math.DS]. 
    *   *Significance:* Introduces Polynomial Towers. Proves that Host-Kra factors $Z^{\le k}(X)$ for bounded-exponent groups admit extensions with the structure of polynomial towers, which are Abramov and $k$-step translational systems. Solves the inverse Gowers theorem for these groups natively [cite: 14, 17].
2.  **Jamneshan, A., Shalom, O., & Tao, T. (2023-2026).** *A Host–Kra $\mathbb{F}_2^\omega$-system of order 5 that is not Abramov of order 5, and non-measurability of the inverse theorem for the $U^6(\mathbb{F}_2^n)$ norm.* Mathematische Annalen (2026) / arXiv:2303.04853 [math.DS].
    *   *Significance:* The definitive counterexample to the Bergelson-Tao-Ziegler conjecture in low characteristic. Demonstrates the non-measurability of the inverse theorem for the $U^6$ Gowers norm [cite: 2, 4, 5, 6, 8].
3.  **Candela, P., González-Sánchez, D., & Szegedy, B. (2023-2024).** *On measure-preserving $\mathbb{F}_p^\omega$-systems of order $k$.* Ergodic Theory and Dynamical Systems, Journal d'Analyse Mathematique (2024) / arXiv:2308.06322 [math.DS].
    *   *Significance:* Proves that every ergodic $\mathbb{F}_p^\omega$-system of order $k$ is a factor of an Abramov system of order $k$. Analyzes $p$-homogeneous nilspace systems to bypass the BTZ counterexample [cite: 11, 13, 20].
4.  **Candela, P., González-Sánchez, D., & Szegedy, B. (2023).** *On higher-order Fourier analysis in characteristic p.* Ergodic Theory and Dynamical Systems, 43(12):3971–4040.
    *   *Significance:* Established the truth of the BTZ conjecture for the $k \le p+1$ regime using nilspace fibrations [cite: 12, 20].
5.  **Jamneshan, A., Shalom, O., & Tao, T. (2023-2024).** *The structure of totally disconnected Host–Kra–Ziegler factors, and the inverse theorem for the $U^k$ Gowers uniformity norms on finite abelian groups of bounded torsion.* Communications of the American Mathematical Society (2024).
    *   *Significance:* Structural description of arbitrary Conze-Lesigne systems and inverse theorems using topological dynamics [cite: 8, 10, 21].

## 6. Attack Vectors
The mathematical methodologies deployed to dismantle the existing conjectures and erect the new Polynomial Tower framework represent the absolute cutting edge of topological dynamics and cohomological algebra.

### Live Techniques
**1. Nilspace Theory and Topological Abramov Systems:**
A dominant live technique involves utilizing compact finite-rank nilspaces, specifically $p$-homogeneous nilspaces [cite: 9, 12]. To prove that every ergodic $\mathbb{F}_p^\omega$-system of order $k$ is a factor of an Abramov system, Candela, González-Sánchez, and Szegedy constructed a topological dynamics space $\text{hom}(\mathcal{D}_1(Z), X)$, where $X$ is a $k$-step nilspace [cite: 11, 19]. By analyzing the natural shift action of $Z$ on this space, they identified single orbit closures $\text{orb}(f)$ that form minimal distal nilspace systems [cite: 11, 19]. Because the underlying nilspace $X$ is an abelian group nilspace, this space inherently forms a topological Abramov system of order at most $k$ (where continuous phase polynomials are dense) [cite: 11, 13]. The ergodic system is then embedded via a fibration $\phi: H_{p,k} \to X$ [cite: 9].

**2. Polynomial Towers and Exact Cocycles:**
To bypass the limitations of strict Host-Kra factors, Jamneshan, Shalom, and Tao engineered **Polynomial Towers**. This technique involves a finite iteration of abelian extensions of the trivial system by polynomial cocycles [cite: 14]. The critical breakthrough is that the intermediate extensions do not need to equal the Host-Kra factors $Z^{\le j}(X)$ [cite: 14, 15]. 
To successfully build these towers, three highly technical properties are enforced:
*   **Exactness:** The cocycles must obey a sharp correspondence between their type and their degree as a polynomial cocycle. Essentially, they must be "as polynomial as possible." [cite: 22].
*   **Large Spectrum:** The set of eigenvalues of the system must form a specific countable dense subgroup of the Pontryagin dual of the acting group [cite: 23, 24].
*   **Purity:** The sampling map that translates polynomials on the system to polynomials on the group must be injective for almost every fiber, landing in a pure subgroup. This allows the roots of a polynomial in the system to faithfully correspond to roots on the group [cite: 22].

**3. Cohomological Obstructions (The Counterexample Engine):**
To break the BTZ conjecture, the authors framed the problem as a cohomological one: finding finite abelian 2-groups equipped with a cube structure that support 2-homogeneous $k$-cocycles which are *not* $k$-coboundaries [cite: 12]. Through standard linear algebra and Smith normal form calculations on finite-dimensional vector spaces over $\mathbb{F}_2$, they identified the symmetric polynomial $S_4$ in $\mathbb{F}_2^n$ which has a large $U^4$ norm but does not correlate strongly with any cubic polynomial [cite: 1, 18]. This combinatorial anomaly was then scaled to $U^6$ to construct the non-measurable quintic phase polynomial [cite: 1, 2].

### Exhausted Approaches
*   **Naive Classical Polynomials:** Attempting to map Gowers norms directly to classical polynomials in low characteristic regimes ($p < k$) is entirely exhausted. The degree drop phenomenon ($pP$ having drastically lower degree) guarantees that non-classical phase polynomials cannot be globally normalized into classical ones without losing the correlation bounds [cite: 3].
*   **Direct Host-Kra Equivalence:** Attempting to prove that intermediate Host-Kra factors $Z^{\le j}(X)$ perfectly match Abramov systems of order $j$ for bounded exponent groups is a dead end. This rigid requirement was the primary roadblock that the Polynomial Tower architecture bypassed [cite: 14, 22].
*   **Calibration Note:** In evaluating the exactness of polynomial cocycles within the new tower framework, researchers must strictly avoid `PATTERN_CONDUCTOR_CONFOUND`, where the continuous properties of the abstract Host-Kra factor are erroneously assumed to natively transfer to the discrete intermediate extensions of the polynomial tower [cite: 14, 15]. The separation of the tower's intermediate steps from the strict $Z^{\le k}$ factors is the exact conductor that resolves the confound.

## 7. Cross-References
The resolutions within Host-Kra structure theory radiate out into several adjacent open problems and fundamental mathematical anchors.

**Related Open Problems:**
1.  **Algorithmic Gowers Inverse Theory:** Does the failure of the measurable inverse theorem for $U^6(\mathbb{F}_2^n)$ unconditionally destroy all polynomial-time algorithms (e.g., Goldreich-Levin types) for approximating the non-classical phase polynomial $e(P)$? Currently, the probabilistic bounded-time oracle is disproven, but deterministic or alternative structural algorithms remain an open question [cite: 3, 4, 10].
2.  **Polynomial Freiman-Ruzsa Conjecture in Bounded Torsion:** The techniques developed for bounding $U^k$ norms and handling bounded exponent groups share deep connective tissue with the recent resolution of Marton's conjecture (the Polynomial Freiman-Ruzsa conjecture) by Gowers, Green, Manners, and Tao [cite: 25].
3.  **Partition Rank vs. Analytic Rank:** The separation of structure and randomness for tensors in low characteristics is closely tied to these cohomological examples. Random tensors of partition rank $r$ exhibit analytic rank $r - o(1)$, answering stability conjectures related to the Adiprasito-Kazhdan-Ziegler conjecture [cite: 1].

**Anti-Anchors (What we know is False):**
*   The assumption that $U^4$ norm bounds in characteristic 2 guarantee strong correlation with a cubic polynomial. The quartic symmetric polynomial $S_4$ explicitly violates this, serving as a powerful anti-anchor for low-degree structural assumptions [cite: 18].
*   The assumption that topological inverse limits of nilsystems are identical to Host-Kra factors in all characteristics. The deviation between Host-Kra factors and Ziegler factors, while occasionally overlapping, must be rigorously distinguished [cite: 11, 13, 19].

**Candidate Primitives:**
*   **$p$-Homogeneous Nilspaces:** As primitive algebraic objects, these nilspaces provide the exact topological dynamics environment needed to construct Abramov factors globally [cite: 9, 12, 18].
*   **Conze-Lesigne Factors:** As the second Host-Kra-Ziegler factor $Z_2(X)$, this primitive controls all complexity-two recurrence properties and serves as the base case for understanding exact polynomial cocycle integration [cite: 14, 21].

***
*End of Report.*

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH94hf_Y74xfB9eW-mre_JPpTYuqGN3UmIjfL2LonksR-g-FINjsr9rV25_VG_R5B8QvQaE4ZbOaAF8TD6RqUeVp4_TOVXChNpcgmk8AFlNlkhaM5X0P3N3S5NUljUsOO4hA5yaT2PlNivwkx34Thv17Iuyq06UBJtlS0O7h6W-WrUdjnsapDn7E5apMtf5TpjGhceZKHPU4NUN5WNzlBR30bAz4QIjR0GYGUvz0g70lpezOwNGJRnGeW_24NFaC_g=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoVEo2QjnGnql-eNXTGhjUZf1W38xqbVtoRhEUDIf7lEVSljKYpofHub8R8wI3eiL20PJnEgFSPaWIhMfLj0GDhK5jKWiRdcJOHrS9OuPBoqiBjEKnHVeSYg==)
3. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG25eg8iJuLMdbvkrl7NahCvCuQr08lgUGwpUkzgdmLA_opERQxfDG7zAWMbyC0VvS_-nuxc-wTnv3biawYVXn6vByVXMftSuzc8Whcy6yb3ASwRkltql7-bod5mD21rFpo_Jf4FAqCcwKxOWyB78O5e3Mdzx6cruwca_AVOmrSbnRCCNY=)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEeZy5pmcvmjAhY2n8MkrioScp7b9mYhQNle8nzfujv8g78DbjjYGWruYMQJ6sRj1DmXpJtrD8oOwhzXJ1z7lyA505rSFV46ik-DCDT69aNqfBMyDCSdQ==)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE778oX_nZ3cqbriwGWZyRsEmST6tRoT6Tp45umGcaH5vANf0_1rV0oTuHO7qNhcXy21bro46RZiziH30oZfxSRY7aRc9Wu3vMbCkcvsQdlj3EsKgDLlQW7AjXdHhuzpzSVCcUK7l8tpGQfDX9XhE1ciUGlg2BmTxTFLByabjOGSgb-u5RwgzzBcaqyC8HslDpw3T_k7-H2zkIZ6p41WKmE3fzMRxRo8SqpzOVRe4oxhZVOL9agfrcJi_oeLzJNL-z-ydQ2o77BN3DJ5cy4nhYsaGvftvBcRb8bPk7_f4AUzv1-rRsUIKOoi_YuDGwsO66lGk2hWFXkwdL5lG0nVg==)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFVqoFAPHCab4q-j3BqiGJeUUm9GRwV7dHslmCWhGGUk7pGcRIpA5G_c6xA9_vHgtP2XCRGiHkId4F4fqqb5r0CuEF_PPiB62b0gaMN9uOOZ0OtYqThnS8fVI23bt3EZFi5Gc0mdyMRKXO7Dr8RnVVScyJbB7sC9oCsEcOXZAKgLJaNtolxQ_OT7iOF1N4XjFBomzmWNN6ZTDjmmaN6a3IUVipd_zRb9Pb9O5NxmBekb_IKCHyVDOtApb4cwBtUZr2RONrXtZQeglfPGmJh3M97UfphOPTeVH6Bh3M09Uy4QxKHdVQRk4cEZ5kjNy3Oqlddi1VYBvgMqPl2OW17g==)
7. [biu.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3qI_cLFbz3umhAEQ3Q2mj9K3ngCiP6W-5JG3RMk6xv0PhM1C1dATMcNaIaoLNKvoXsZUfS7lk2jmkrsKDlbfO30Spmq0wEEii6pWhLQ8HfmfP6x4CnPz4E07BIGB3MantZzYUgtpsIwIFgFGhLaJhT4ifgva31hiXWKnSeb45eMey9Y3uE7bLf-WP1t-UGWKxvztuuz_UJXdYWe9tJY1Uh9V7kwUWI3qMNS_sO21Grl8=)
8. [biu.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOWoRKXQpfCskdAdvUnkO57JAQwYFmX3HchDWDiBgEpWU7zqO6nOoxMv5gPrv2DjlM9b8yU-mtEdKe191fy8gzRawxf7VdjUJuoiT7QN3YkQrhl-FM7sQ=)
9. [wpmucdn.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEladFM2rpuO3jIDYWt7DzRXFlvfk8He7UNQAkBM8q1Wmv_8Uc78wbqOlcXp0wQuldEnLqulGu-vAB2wiyDwAg-daS9RwZImdLrbWr6XhrjyZmqQfV9VRNcnleW1b6_z1CJYmB2nIKMEXzjLuV_adAQ2WfiY_tgyyRrI7yHznhW1bmdcHfxtMhpaO_pvWpgJDyRYiDAqmaMa1KG)
10. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSV-G8sUkYYXP4rpQ6sDcemuXSQWNlqq47xwE8y7wjz3myTIlsyUZbAwZrz13LvGnD8pYKomQp8OOdHQeeeuNIQgSPUA70rQ97qUWNoWOOjHyYpl-S08XqH04Ym-SFdhop-ykVrTXpTHYzdEiyBltgI4GQunygMGNhgVg_4TMqKeSWRi-RVWAj8CtR5_XeWjiY8vDy4Dd61gpiHmh2hNiJR2U6XFxjywfBiziTvrlGTOo-oLMTrqkeIoDzCRNxbhlNMgM_02q49oDzlrTtPTp0azqX2bcSMN2EOLbork-cxeIg3Z_Gu2DAOHi8aXQobpsgRJqaFtrI0qwr7niJnCikX_eXWCFLuBUcBbXmJ8O7IclA1g==)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqxuVBD22SRBQoaoqVjQHtKehCfUs_vljiur7lrghtDgcfhyA2bnZM38L3vBC6yul_T5DGOxu69fIi7yQnfa9hrqGB4GxR7WqK59QO1EawhbxerJmE-KiIMctHFpL8ZVW5SiqUd_uSW3k7yJycF8sLNOOCi6Td4lQBC1i62ffZRwFcVuzX973UyGveSUJOFTcM39-0zlo=)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGX6lpNUWomqidl8zNy-38br6HhB8k6bK6ZyTCvunCvQR3dpo83SZ8Gdd_4cSV9t4-WTw_0mvBwbda6lvSJ9pll9aPsk6JkZe80bnt0xg8ryGEmaJ9H0frUjn2JGo_cltFpWGa7UuM-iNrCFaZKW8go9-WjvhwucHZ982Cn3iSmLR4-pgk=)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTvoLJcVsmyVsL1dB6jszRIiWN1BPNOdrbhXHQrAVrng9FuJ5OYNJjCLx2GRGfdNXzBsbNDQN8IxGbbhk55DKdLuMoTF1nW4LJV2iRTrzPL6Yx_D898w==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0cx7Gw0xb7LOaRwrqjq1N5CRVnvPw7gXlcqnECaoX33Qd5bmg0nA2vA9shDvOyct3Ari_YCv4On9a0XfUoUqbCV1Cm3BJIYVSiINFlNxmpv2aoYkRlQ==)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-CQDeBTOtSAkAw9RfOeVsVASr15omt0xZzSUQk0v4wAnLiPCrrKISBcCqsKKBU6nF4cHB0UkcOIQYXf3OeUEnTSUFofojGn1WD4QfI1BMbbeCrl__xNA97z1k6ZXe9uaLauucWuJeLxj26R6ORwo0qBTqWJN7z0aJkhHgH9r_dw==)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAfXpdyL15JalO45olz2mdzkZogqCiP1bAUtGSbzNLF801SKI_V9W7w77lVoCkI4zSK7oaQCCwP7KnQRLfurhK7Yc08fo9AroBUZaN-EwdMHIRfzQFgq-PQWlLezy5hen1eBMZnzMorYxtORqwycHDuAFy4xZ5j7Bt9BYlXpaqlwL_XkdYyN0gs9KnagHXwFqIhe-PY-Sai8wfS8m7K3VIZAyzZ-tZLpiCKWLfd9fZyQ==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyItNz62x9OKpTwED1GsDhP9UezarjQh1dTS9PNCYo-pr92FwpOE0I-IYiMjErUXLJ_QaiU0786WPYyxHbjCfosRl7SGxmuQ0vMuq3kfHr4m_JsuiQNA==)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0SgnfoMQmBgY2CAQfPTaSKEXP6-jMxzH5_TkZ6Ygtix0O31ZOI2vPf8KHQNbLN-CkhfU_FSjOQyshTUw6yIJILeORQByVLpBT9s5u9myCtrtxB3chseyWHvoEWg6xSCwlrM9gyS07Ma3KoG2Gtzejy6FbszDJrmd5PZTWb6-4St2gBQPov9cWAhrKxgaPc_-8rAuDNqKqMaMsDp3LF8ovzxBwYzZh1PQ=)
19. [csic.es](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpbKDcNJphVj9Oi2qmjjJ_xfEhJ2fBGbY6rOk8zmPNHURxyxOfFqAZsakEL824D1-6VexpklaDgImbxOiAZIit9nGYljGk5ZGefUwxpTDouzfrCxYTklCjYGz-FTVS12RDTGgmReGp_rWxFUGJ-ZCqSTIFxvFbWIlqLJ5z)
20. [otka-palyazat.hu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEl-vaWi3d5tf0Fwp_BvTObZRQzBK6KX7zXbUgu8rtG6SSlr6-HRcvsHOBDnr1uhGClwOVOQsrJCnFu6emoX5Uig6xSz899LFRabExta0FGToFH_02IqT6HSQOvpTZpAecka8dG-LbUoXAxRWkY7p7hUmbM3dscgD_G-BlkvRjXSibVQQ==)
21. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFg6ZLJBQ78m6whKSnrRq3XzCl-lIxYMe9kJh3yUXW0aQUbVSRhtVKDq30PLM_zro7FlYRBCzOUszpSjSj296uCCxQc5xqprSs5f3xLog0JjeZ_2jK7oViGqjPYn3ZSslitcfw=)
22. [math.hr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFELzs7nhOKizGeSLCirQUZf3RRXLx0vN4N6wcqZ1neinRfzeim3vpWxs5olovu09uVOmejrYSTDcd-WbrhRQLu7AFELNxDA4rC-nKmYotsijqzZN8oGoYVHCNd)
23. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgqldwddakVNhR3146xb-Ni_3tAzN7gIFMc3co69C00JjGql9K8wn1um9emMyvbaSbf-xc83zonXsHVI1R730CQfNput7-W5ZWdUoM8t7HWf0b03WKziLNbext1g3yIlTMheRd7Haw8x8z45DUgD-L0WG8)
24. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtdi3uwIObtzOHrB2mUFQw3IllYaCQ4yO5ndjcy828Y4XA9PrQigyjCIMT59qIKHPClxowpAI9GnNHw5p1vRcl9o6fZSxnHZ6YKufN6QJJk7MMqVtngWv8i_AcU_7IKio5Bjs4YJjXNy_lrliaCqJcABRJuZGxpam4lvzKMzePl9HGbqnds0eF99UUXWN_M1lf-A_9nluuOxRIH49b7mc7j5oKI1T8q8o=)
25. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZUDtgUjIwp-3qITQ14I4NH5lyGk31XX7IL2sl_1GCrHVJ02k7RnrqasR3cSgp6ZSyzIYecAHFRiANI4bqCgn2cAzIQ4AHQtDX_lCV8CmwLtqORqnrCG88um1d9OG8esmJg7LVWB-hfrelww9vQHt36b_wcNmjo-dYNQ4WOLn6)

