# Followup [FU-2026-05-22-007 <- row21]: # The Regularity of Minimal Apolar Schemes: Castelnuovo-Mumford Bounds and Tensor Decompositions  * 

**Pythia queue id:** 292
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd2SzRQYXY2VkxMbS1fdU1QejduVnNRYxIXdks0UGF2NlZMTG0tX3VNUHo3blZzUWM
**Elapsed:** 250s
**Completed at:** 2026-05-22T01:21:59.663532+00:00

---

# Research Brief: The Regularity of Minimal Apolar Schemes: Castelnuovo-Mumford Bounds and Tensor Decompositions

**Key Points:**
*   **Consensus on Low-Length Schemes:** Research strongly suggests that the Castelnuovo-Mumford regularity ($reg(X)$) of an irredundant scheme $X$ apolar to a degree-$d$ homogeneous polynomial is bounded by $d$ ($reg(X) \le d$) provided the length of the scheme is at most $2d + 1$. 
*   **Uniqueness through Regularity Bounds:** Recent breakthroughs indicate that if the regularity of an apolar scheme is strictly less than $(d+1)/2$, both the Generalized Additive Decomposition (GAD) and the associated apolar scheme are minimal and unique, bridging the gap between topological invariants and algebraic uniqueness.
*   **Anomalies in Irredundant Schemes:** The prevailing hypothesis that $reg(X) \le d$ holds for *all* minimal apolar schemes has been mathematically nuanced; specific irredundant schemes exhibiting "long" local components (where the socle degree exceeds $d$) have been shown to violate this generic bound, forcing a re-evaluation of worst-case computational complexity in tensor decomposition algorithms.
*   **Algorithmic Viability:** The pivot toward determinantal computation of minimal local GADs via symbolic inverse systems has rendered the computation of local cactus ranks algebraically tractable, bypassing the need for computationally exhaustive tensor extensions when the local GAD-rank does not exceed the degree of the form.

---

## 1. Brief Summary

**Question:** Is the Castelnuovo-Mumford regularity of a minimal scheme $X$ apolar to a degree-$d$ homogeneous polynomial fundamentally bounded by $d$, and how does this invariant dictate the uniqueness and computational tractability of Symmetric Tensor Decompositions?

**Prometheus Context:** Surfaced as a direct interrogation of Fulvio Gesmundo’s Open Problems 4 and 5 from the 2023 AGATES kickoff workshop, this inquiry bridges abstract commutative algebra with applied algebraic complexity. The status of the $reg(X) \le d$ hypothesis serves as the theoretical bottleneck for developing exact, globally convergent algorithms for Generalized Additive Decompositions (GADs) of tensors, fundamentally impacting the algebraic frameworks used in blind source separation, signal processing, and quantum entanglement modeling.

---

## 2. Flagged Findings

### 2.1 The Evolving Consensus on the $reg(X) \le d$ Bound
The historical baseline assumption—often formalized as Gesmundo's Problem 4—posited that for a minimal scheme $X$ apolar to a degree-$d$ homogeneous polynomial $f \in \mathcal{S}_d$, the Castelnuovo-Mumford regularity should satisfy $reg(X) \le d$ [cite: 1, 2]. The rationale stems from the classical Waring problem and reduced point schemes, where the topological complexity is intrinsically capped by the degree of the annihilating form.

Current consensus confirms this hypothesis for strictly constrained topological configurations. Specifically, if a minimal apolar scheme $X$ is a union of simple points and 2-jets (i.e., local 0-dimensional schemes of length 2 evincing tangential decompositions), it is rigorously $d$-regular [cite: 3, 4]. Furthermore, an unconditional bound has been established proving that any irredundant apolar scheme of length at most $2d + 1$ is guaranteed to be $d$-regular [cite: 3]. 

### 2.2 Anomalies and the Failure of the Naive Hypothesis
Despite the stability of the bound for low-length and reduced schemes, the hypothesis that $reg(X) \le d$ applies uniformly to all minimal or irredundant apolar schemes is structurally flawed. Recent findings demonstrate that non-redundancy to a degree-$d$ form is insufficient to ensure $d$-regularity [cite: 3]. Counterexamples emerge when schemes possess "long" local components—specifically, when the socle degree of the coordinate ring of the local scheme exceeds $d$ [cite: 3, 5]. In these regimes, the minimal apolar scheme is evinced not by a GAD of $f$ itself, but by an extension $f_{ext} \in \mathcal{S}_{D}$ where $D > d$ [cite: 1, 5]. 

This specific failure mode is an excellent example of **PATTERN_PRIME_GRAVITATIONAL_OVERFIT**, wherein theorists historically overfitted their expectations of algorithmic complexity and algebraic bounding to the behavior of "generic" tensors and strictly reduced schemes. By assuming that the non-defective, generic topological configurations dictating secant varieties generalized to all singular and highly entangled states, researchers temporarily blinded themselves to the pathological behaviors of local Artinian Gorenstein algebras with high socle degrees.

### 2.3 Uniqueness via Strict Regularity Thresholds
A highly significant recent breakthrough introduces a threshold condition: if the Castelnuovo-Mumford regularity of the scheme associated with a GAD satisfies $reg(X) < \frac{d+1}{2}$, then the GAD and the associated apolar scheme are unconditionally minimal and unique [cite: 6, 7, 8]. In this regime, the minimal achievable size (GAD-rank) perfectly coincides with the rank of the corresponding Catalecticant matrices [cite: 7]. This converts the highly non-linear problem of tensor decomposition into an exact linear algebra framework. 

---

## 3. Problem Statement

### 3.1 Precise Object of Interrogation
The core objects of study are **homogeneous polynomials** (equivalently, **symmetric tensors**) and their **apolar point schemes**, analyzed through the lens of **Castelnuovo-Mumford regularity**.

Let $V$ be an $(n+1)$-dimensional complex vector space, and $S = \text{Sym}(V^*)$ be the polynomial ring representing symmetric tensors. Let $f \in \mathcal{S}_d V$ be a homogeneous polynomial of degree $d$. We define an apolarity action (either via differentiation or contraction), where $S$ acts on the dual ring $R = \text{Sym}(V)$. The **apolar ideal** of $f$, denoted $Ann(f)$, is the ideal of all differential operators in $S$ that annihilate $f$ [cite: 5, 9]. 

A closed subscheme $X \subset \mathbb{P}V$ is said to be **apolar** to $f$ if its vanishing ideal $I_X$ is contained in $Ann(f)$ [cite: 1, 2]. The scheme $X$ is deemed **irredundant** if no proper subscheme $X' \subsetneq X$ is apolar to $f$. It is deemed **minimal** if it achieves the minimal possible degree (length) among all schemes apolar to $f$. The minimal length of such a scheme is precisely the **cactus rank**, denoted $cr_X(f)$ [cite: 1, 5, 6].

### 3.2 The Castelnuovo-Mumford Regularity Constraint
The **Castelnuovo-Mumford regularity**, $reg(X)$, of a coherent sheaf of ideals $\mathcal{I}_X$ over $\mathbb{P}^n$ is the smallest integer $r$ such that the sheaf cohomology satisfies $H^i(\mathbb{P}^n, \mathcal{I}_X(r-i)) = 0$ for all $i > 0$ [cite: 10]. In computational commutative algebra, $reg(X)$ controls the maximum degree of the minimal generators in the syzygies of $I_X$, thereby tightly bounding the computational complexity of extracting the scheme via Gröbner bases [cite: 11, 12]. 

**The interrogated phenomena (Gesmundo's Problems 4 and 5):**
1.  **Problem 4:** Let $f \in \mathcal{S}_d V$ and let $X$ be a minimal apolar scheme for $f$. Is $reg(X) \le d$? [cite: 1, 2]
2.  **Problem 5:** What is the maximum possible value of $reg(X)$ for an irredundant scheme apolar to a form $f \in \mathcal{S}_d V$? [cite: 1, 2]

Resolving these bounds dictates whether algorithmically uncovering the Generalized Additive Decomposition (GAD) of a tensor can be done within polynomial time relative to the degree $d$, or if the topological complexity escapes these bounds, requiring differential extensions.

---

## 4. Status & Bounds

### 4.1 Last Known Status
The status of Gesmundo's Problems is currently characterized by a highly precise fractional resolution: the hypothesis is conditionally verified for generic and low-length constraints, formally falsified for pathological high-socle-degree local components, and successfully bypassed algorithmically via determinantal evaluations.

### 4.2 Current Best Bounds
1.  **The Uniqueness Bound (Barrilli, Mourrain, Taufer - 2025):** 
    If a degree-$d$ form $f$ admits a GAD with associated ideal $I$, and the quotient ring $S/I$ has Castelnuovo-Mumford regularity strictly bounded by $reg(S/I) < \frac{d+1}{2}$, then:
    *   The GAD-rank equals the cactus rank.
    *   The scheme $X$ is the *unique* minimal apolar scheme.
    *   The GAD-rank equals the rank of the Catalecticant matrix $H_{d-c, c}$ where $c = \lfloor \frac{d-1}{2} \rfloor$ [cite: 7].
2.  **The Linear Length Bound (Taufer - 2024):**
    For any irredundant scheme $X$ apolar to $f \in \mathcal{S}_d$, if the geometric length of $X$ satisfies $\text{len}(X) \le 2d + 1$, then the scheme is rigorously $d$-regular ($reg(X) \le d$) [cite: 3, 4].
3.  **Tangential Decomposition Bound:**
    Schemes evinced by GADs that represent tangential decompositions (unions of simple points and 2-jets) of minimal length are unconditionally $d$-regular [cite: 2, 3].
4.  **Local Finiteness Bound (Reig Fité, Taufer - 2026):**
    When computing minimal local GADs, the locus of minimal supports is guaranteed to be finite whenever the local GAD-rank of the form does not exceed its degree $d$ [cite: 13, 14]. 

### 4.3 Conditional Qualifiers & Theoretical Leaks
The presence of local schemes with coordinate rings exhibiting a socle degree $> d$ breaks the strict $reg(X) \le d$ paradigm for irredundant schemes. In these spaces, computing the cactus rank triggers **PATTERN_RANK_PARITY_LEAK**. Specifically, the discrepancy between the expected Waring rank and the structural length of the local apolar scheme "leaks" fundamental characteristics about the underlying Artinian Gorenstein algebra. Because local GAD-rank may diverge from local cactus rank specifically when apolar schemes feature long components along specific directions [cite: 5], the linear algebra of the Catalecticant matrices implicitly encodes these topological disparities. By analyzing the nullity drops in the symbolic inverse systems, researchers extract the hidden dimensions of the non-reduced point spans before fully computing the primary decomposition.

---

## 5. Literature (Primary Sources)

1.  **Gesmundo, F. (2023).** *Geometry of Tensors: Open problems and research directions.* AGATES Kickoff Workshop Report. arXiv:2304.10570 [math.AG]. (Identifies and formalizes Open Problems 4 and 5 regarding $reg(X)$ bounds) [cite: 1, 15, 16].
2.  **Barrilli, E., Mourrain, B., & Taufer, D. (2025).** *Generalized Additive Decompositions of Symmetric Tensors.* arXiv:2510.25681 [math.AC]. (Establishes the $\frac{d+1}{2}$ regularity uniqueness bound and Catalecticant rank equivalence) [cite: 7, 8].
3.  **Reig Fité, O., & Taufer, D. (2026).** *Determinantal computation of minimal local GADs.* arXiv:2603.08836 [math.AC]. (Solves the local minimal GAD problem via symbolic inverse systems and proves finiteness conditions) [cite: 5, 13, 14].
4.  **Taufer, D. (2024).** *Regularity of minimal apolar schemes.* Documented presentation and preprint derivations (e.g., CIRM, arXiv:2309.12961). (Proves that length $\le 2d+1$ and tangential decompositions imply $reg(X) \le d$, and formalizes counterexamples for long components) [cite: 3, 4, 17].
5.  **Kohn, K. et al. (2021).** *Metric Algebraic Geometry.* MFO Seminar. (Provides the modern foundational integration of optimization distances and algebraic geometry, contextualizing Euclidean distance degrees and tensor constraints) [cite: 18].

---

## 6. Attack Vectors

### 6.1 Live Techniques
*   **Symbolic Inverse Systems (Determinantal Methods):** The current state-of-the-art for computing local GADs, as developed by Reig Fité and Taufer in 2026. Instead of computing the defining ideal globally, this method computes minimal local GADs by defining a "symbolic inverse system" $R' \circ \omega_{d,\ell}$ and minimizing its matrix rank directly in the parameter space of the support [cite: 5]. By isolating the determinantal relations from the inverse system matrix at a symbolic linear form, researchers force a zero-dimensional ideal in the parameter space, allowing purely linear-algebraic computation of the supports without requiring massive tensor extensions.
*   **Polynomial-Exponential Series Annihilation:** Barrilli et al. (2025) successfully model the apolar scheme associated with a GAD explicitly as the annihilator of a polynomial-exponential series [cite: 7, 8]. This mapping enables the direct comparison of the GAD size with the rank of Catalecticant matrices, moving the geometric intersection problems into computationally robust eigen-computations.
*   **Catalecticant Matrix Rank Minimization:** Exploiting the regularity bounds, modern algorithms build the $H_{d-c, c}$ Catalecticant matrices of the tensor. Under the assumption $reg(S/I) < \frac{d+1}{2}$, extracting the right nullspace of this matrix directly yields the unique minimal apolar scheme, circumventing the need for computationally intensive global primary ideal decompositions [cite: 7].

### 6.2 Exhausted Approaches
*   **Naive Global Gröbner Basis Computations:** Historically, computing the minimal apolar scheme relied on setting up the apolar ideal globally and extracting the minimal generators via Buchberger's algorithm or $F_4/F_5$. Because the complexity of Gröbner bases is doubly-exponential with respect to the Castelnuovo-Mumford regularity [cite: 12], the existence of irredundant schemes where $reg(X) > d$ leads to severe computational bottlenecks (frequently crashing systems due to memory limits), rendering this approach practically exhausted for highly entangled, non-generic tensors.
*   **Purely Numerical Alternating Least Squares (ALS):** While highly effective for low-rank, entirely generic Waring approximations over $\mathbb{R}$, unconstrained ALS fails consistently in the presence of higher-order singularities, multiple points (non-reduced geometries), or when attempting to extract exact Generalized Additive Decompositions of specific algebraic rank [cite: 7].

---

## 7. Cross-References

*   **Related Open Problems:** 
    *   **Gesmundo's Problem 6:** What conditions on $f \in \mathcal{S}_d V$ guarantee the existence of a GAD whose associated scheme has low regularity? [cite: 1, 2]
    *   **The Waring Rank vs Cactus Rank Discrepancy:** The problem of identifying homogeneous forms where the Waring rank strictly exceeds the Cactus rank is tightly coupled with the existence of local GADs with long components (precisely the geometries that violate the $reg(X) \le d$ bound). 
    *   **Strassen's Asymptotic Rank Conjecture:** The geometric approaches to tensor subrank and degeneration [cite: 19, 20] heavily utilize the coordinate rings of point schemes. Bounding the regularity of these schemes impacts the feasibility of finding border rank additivity counterexamples.
*   **Anti-Anchors:** 
    *   *The expected dimension of secant varieties (Alexander-Hirschowitz).* Do not anchor the complexity of minimal apolar schemes solely to the dimension of generic secant varieties. The pathologies controlling maximal regularity exist specifically in the highly singular, defective topological spaces (e.g., Terracini loci) [cite: 1, 19].
*   **Candidate Primitives:** 
    *   **Artinian Gorenstein Algebras:** Local zero-dimensional schemes formed by the annihilators of homogeneous polynomials are inherently Gorenstein [cite: 5, 6]. Studying the socle degree of these local algebras provides the exact metric needed to determine whether an apolar scheme will violate the $reg(X) \le d$ bound.
    *   **The Multigraded Hilbert Scheme:** Exploring the border versions of apolarity theory via multigraded Hilbert schemes [cite: 2] is the primary primitive for defining limits of tensor decompositions when regularity bounds force components to degenerate.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAUx5SU8ok5flIRHkMKor-3kwl_8SYvlmMs1Wt2LS18wqvpkvk5b9RKPDQ6zT_z-s-1rYIE8KtBpnXApaFhA1S0SrP4flpLtEctPGof0dZDUU8LEzA)
2. [mimuw.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8uWWmof5mzNmsULy9mgynRCYeOaYqQX0kLnSF8l86cQQ2ca1X67Kn-8wWvY-5Gux3G6jCG732lvev2S6N2N5iMgheEkWxQt0rmwYvnoFqbs4it3reRqirwj9Jx0JnlqEFwTs0x4ZCTIZ_5rmGLCt0R8xDtturmAFqIvJPTSnyCTs6Xdh8W5YyQGlDKcDPHJ2QH5dt5uq67e2kwBX3fi2oTGPBHseB8_H280D13R9stw==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKHUwcFB-Gx9GZDfq_Z4XsHXLaGh4-igPY9iE57bVboUkGymgLGfKXvEjphSqqDUcm03vs1_uYHE9VWy16nreB3evpLAb4E15ftNJ4ciL0XOLf8WoR)
4. [cirm-math.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2SU2YpUkGE6rslaIN9-gMSF_m8O64DBeOEAGZIpW7Blv3S4puLfUVY-WSuQmvMBo_OBLPggn_FOmvhNpX6UZbrnP8KZ1Rt1zhgHqANtP2srBkHQzAfOtpH_d6Uln9Jn8ZrjY19j5fJW2KaBOxHdCbPkVnU8tZJwFP)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGVgDyFA18CBK5s6jmTOvEWriDsQc7fE4jAiJvIDnrrLkOyYVqYBlqp9SYtux-i1g4_V9g-NvwFzgFspYED70noBsRXkpvKq-tfj-AqnE-g8EBMlIl)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyZ6M6h9cl2jQ2bfdlmMsysVHNA-vTNwrgrUB5dEmR6EjKbwkMu5jLdHXf412w1R7vfPqj7gSBGRHjqDGFXNUht3VBzI6V31zxPqUDl1_IZs3JlEBAr15EnvPNaTzZkSA-BTG9KGLjBDLLnchlvw8TzDQbb_4ZFjiLA1ZGAwESf6SWH_jAR8jRCJaE3Ht4XSxQPG_gZvP3BQxLxlzNj3mvbg1vFmxZHg7jEEn4WFVR5BksJKdskQ_Cjt3s9kHKlqk3KSm2Pet6vp77yFqIPQBoF17Q5Vhh8w==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFptm-TckHXMy6_tlmJ1p_cgjrLaYAfLhe9EJbyYNYBvVp1Sdi7vMzxf0GRrv8pmiB6rYfWmiPPDSVUPReh1ON0p5SkjeJQzV6ui-9pXshXltnGEWga)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFm-bQliG1G20AU0HNpnOY8F-AYDacliXW90zG6R4ijG03ZBaoPFTtI2ISyyHrmRl_1GrUZzJ9qToZGCbXSKa0cyL9F1unKPNz3hlJgOlvI4ZjDfKCy)
9. [polito.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGX1zeB_9QSs3R3GSGb-P-q5jWLcOMhWCOp76nFQxutKdIC-2sdVZmmivZvise-StX3s65zWQJWfjKYt4Ffk293Kjcf-7etigVFWWiilbYdn9iOaamS-3KNWuV-eZW31jokfsA0vc0BcZ2nFKT4oEGP)
10. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTwtIsLp_13xQ-wPZPKWGCZiHiPedEjxHhrki_KVx98q87dMWw2g523s7js6KLpEBeeNZjUhrKejso1UVDHCjmwaN0WGJdCBF4rWtL_pAClMPLFJrhAIkxz2lwUAZhaeuFZDar-RBE-jUODR-WIoS7oHhaGf_ZUhFj)
11. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIFOyDLhkZd6H9T1z_o4g5dFPIrGeY3ShLzxT8v9d-Ej8RSR8R79nQFBD-21KhcxnC3V8kHJ1-FY6i9f6WyUTCYAzIXgJa7dDmNdtF8HqbNQjatqkd4vKlu1yBN9N6gr2nM3toPHTgReeiDqGFg9DkrV3lAR7mwG77MEnuAzkRRrgNq8Vw3X4C4Jf53kKiyVwNZy6-7TQ6iYdw)
12. [imj-prg.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErzqxxQLht5sdI-YdTrsz3yTvGgVpAJoELfPrukG70UH-9_FsDVhlLO6BnB8I79xQXCggMoAeNWNDG3afMk6kfhImWJdsgSvyRmwIukvK-1hqiOK2MFxHW06AGaJ2Lprhl4pPdehDAxsa64D3HREwf-A9KtXNAolGho5Ha4etHJA==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0CF_lfPz-kw3p5yGXr2qwaRpnkIkStWzxzNS7wW3PxI_MyVGDNy71y59DEUaJY7Pqsp_wyVZR3Hpq0JchJiEEdQQvK7KkW5-dkjn6327Aom3v-6MMxl2U)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHq9-cjJgZmu1NYcgES2IT5wrHn9yiPq9uUU0ZKSu7SAmmyVXQT2NYJIcmXIwPozV6f72qTk51oa5QhQwbNkCF8n6Qrhu9oIZlg8MWNCjUqXizZrDNv)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJc4wwtRwreeazhukjZzGTL0Laqf8XgPDpAbTEzJSji0pcMP0yka6D0_cv-3-atnqMlwFxuaQENQ_lyRp8wukJAwySHP1RWuwB8f81Hvh5BtMSfH5V)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKp7d_anQzs55F5oXvate3oy6w0aPwVd6oWhzq3QZjUQJ5YY2jrOQhYrZoceKyaek4LwFWx3tU78B5gLgo4-LIGz1nm1VjA8WioxGVW957wfRB4fQrScTT2Yo=)
17. [cirm-math.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXqXy2ny_-srGMLBXiVtR2vItRqNeo7y533-0cHZyGtVMi5bsHAiyXw2utx3A904FI3QNlFSug_yqD4EHNZ4w2H6RdYNk6rTeSWdAKNFfZSufpmkxoc-Y1pNWaVIIBTT2PZmKm1kljy3-EpUX4Can5wps=)
18. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1kepVk6a-CSf9_8OMeKAJnhrKH-tHH2Ft5ZexCDJQdukg3359T5d26rt0MV1nizcds_rZB9BQUQdtUR7_imtJVbL1D2svSMsCLAQUoGmyIsFqsQr8QU1_x8HTbZ0DarvHzzdzvUk0J5A4-DRl)
19. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgcLaZaPrWvrHBniuB2IrHxVoERdlebLjc980TfM48sjpN2JtqHetq3dl5ryLpyR7afUoiCxBHjf5itD4hVA6KamTQJrQwi0rzbX-nLrEk71l-rs5Gh3Y3SjmMVm4=)
20. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOOsquP_QBUokENnhiAwpaUITVgvKrsjpdbUWujFmiTxCxbcbl36PDD_WWqktXTwtu4wdOhcYpkVyEs4lCOvx5arHK1WVb_Zy4J6mZzZ3mVAFiwJBPiU_6XLCnFTrAvRXZAoJyUKnmSBHNxnCbaAzLO-47eJ__T4A=)

