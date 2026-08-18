# Prompt 06: DR-038 — Survey AsymptoticSpectrumMonotone outside-tier primitive supporting lit (T#28 CHNVZ 2024 polynomial char) [Tier 1]

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChczNEVGYXBlMEItZU5fUFVQeTQ2VG1BaxIXMzRFRmFwZTBCLWVOX1BVUHk0NlRtQWs
**Elapsed:** 424s

---

# Anti-Anchor Verification: AsymptoticSpectrumMonotone (T#28 CHNVZ 2024 Polynomial Characterization)

**Key Points:**
*   **Algorithmic Computability from Above:** The CHNVZ 2024 result successfully establishes that asymptotic tensor rank is algorithmically computable from above over computable fields via polynomial evaluation. 
*   **Topological and Order-Theoretic Structure:** The sublevel sets of asymptotic tensor rank are rigorously proven to be Zariski-closed. Consequently, the set of all asymptotic tensor ranks is well-ordered (exhibiting "discreteness from above").
*   **Open Status of Discreteness from Below:** The research definitively leaves open the question of discreteness from below, a condition that would inherently follow if Strassen's asymptotic rank conjecture were true.
*   **Rapid 2025-2026 Evolution:** Subsequent literature has dramatically shifted the coordinate space, proving that matrix multiplication moment polytopes are not maximal (March 2025) and that Strassen's support functionals perfectly coincide with quantum functionals (January 2026).

**Introduction to the Substrate Update**
This document serves as an actionable verification report for Project Prometheus. It targets the evaluation of the primitive candidate `AsymptoticSpectrumMonotone` associated with the CHNVZ 2024 polynomial characterization of asymptotic tensor rank. The findings herein are explicitly formatted for substrate integration, dictating catalog edits, anti-anchor pins, and the registration of new tier primitives. By enforcing strict mathematical coordinate separation—specifically disambiguating asymptotic tensor rank from asymptotic slice rank, asymptotic subrank, and related spectral points—this verification ensures the integrity of the substrate's representation of algebraic complexity theory. 

***

## (a) PRIMARY SOURCE CONFIRMATION

**Substrate Target:** Primitive Registration / Formalization lit confirmation.
**Status:** PEER-REVIEWED (Definitive publication June 2025; ANNOUNCED-NOT-PUBLISHED November 24, 2024).

The primary source under verification is:
*   **Title:** *Asymptotic tensor rank is characterized by polynomials*
*   **Authors:** Matthias Christandl, Koen Hoeberechts, Harold Nieuwboer, Péter Vrana, Jeroen Zuiddam (CHNVZ)
*   **Identifiers:** arXiv:2411.15789v1 [cs.CC] [cite: 1]. Accepted to STOC 2025 (Proceedings of the 57th Annual ACM Symposium on Theory of Computing, June 23–27, 2025) [cite: 2].

**Theorem Confirmations:**
The source formally establishes the topological and algorithmic characterization of asymptotic tensor rank, denoted $\underaccent{\wtilde}{R}(T)$. We confirm the exact mathematical invariants to satisfy HARD-5 coordinate separation.

1.  **Zariski-Closed Sublevel Sets (Theorem 1.2):** 
    "For any field $\mathbb{F}$, $k \geq 3$, $d \in \mathbb{Z}^{k}_{\geq 1}$, and $r \in \mathbb{R}$, the sublevel set $\{T \in \mathbb{F}^{d_{1}} \otimes \dots \otimes \mathbb{F}^{d_{k}} : \operatorname{\underaccent{\wtilde}{R}}(T) \leq r\}$ is Zariski-closed." [cite: 1, 2]
    *Coordinate Isolation:* This proves there is a finite set of polynomials whose simultaneous vanishing exactly characterizes the property $\underaccent{\wtilde}{R}(T) \leq r$.

2.  **Discreteness from Above (Theorem 1.3):**
    "$\mathcal{R} = \{\operatorname{\underaccent{\wtilde}{R}}(T) : T \in \mathbb{F}^{d_{1}} \otimes \dots \otimes \mathbb{F}^{d_{k}}, d \in \mathbb{Z}_{\geq 1}^{k}\}$ is well-ordered." [cite: 1]
    *Coordinate Isolation:* This asserts that any non-increasing sequence of asymptotic ranks strictly stabilizes. It guarantees that any upper bound on the matrix multiplication exponent $\omega$ that is sufficiently close to the true value will "snap" to it [cite: 1, 3].

3.  **Completeness over $\mathbb{C}$ (Theorem 1.4):**
    "Let $\mathbb{F} = \mathbb{C}$. For any sequence in $\mathcal{R}$ that converges, the limit is in $\mathcal{R}$." [cite: 1]

4.  **Extension to the Full Asymptotic Spectrum (Theorem 1.5):**
    "For every $F \in \Delta(\mathbb{F}, k)$, $\{F(T) : T \in \mathbb{F}^{d_{1}} \otimes \dots \otimes \mathbb{F}^{d_{k}}, d \in \mathbb{Z}_{\geq 1}^{k}\}$ is well-ordered." [cite: 1, 4]
    *Coordinate Isolation:* $\Delta(\mathbb{F}, k)$ defines Strassen's asymptotic spectrum of $k$-tensors over $\mathbb{F}$. This extends the well-orderedness property universally across all restriction-monotone semiring homomorphisms [cite: 1, 2].

**Mathematical Distinctions Required for the Substrate:**
Prior literature (e.g., Briët, Christandl, Leigh, Shpilka, Zuiddam; ITCS January 2024 [cite: 5, 6]) proved the lack of accumulation points for **asymptotic subrank** $\underaccent{\wtilde}{Q}(T)$ and **asymptotic slice rank** $\underaccent{\wtilde}{SR}(T)$ over finite fields, and $\underaccent{\wtilde}{SR}(T)$ over $\mathbb{C}$. The CHNVZ 2024 source uniquely establishes discreteness from above for **asymptotic tensor rank** $\underaccent{\wtilde}{R}(T)$ over infinite fields, solving a distinctly harder coordinate problem. The substrate must separate $\underaccent{\wtilde}{R}(T)$, $\underaccent{\wtilde}{Q}(T)$, and $\underaccent{\wtilde}{SR}(T)$ as three distinct entries in the invariant catalog.

## (b) FOLLOW-ON WORK (2024-2026)

**Substrate Target:** Work-queue entries / Catalog Edits.
The 24-month window immediately following CHNVZ 2024 displays aggressive, paradigm-shifting advancements across the asymptotic spectrum. The following ANNOUNCED-NOT-PUBLISHED preprints must be ingested into the substrate.

**1. Moment Polytope Non-Maximality (March 28, 2025)**
*   **Source:** van den Berg, Christandl, Lysikov, Nieuwboer, Walter, Zuiddam. *The moment polytope of matrix multiplication is not maximal.* arXiv:2503.22633 [cite: 7].
*   **Coordinate Addressed:** Moment polytope inclusion $\Delta(T) \subseteq \Delta(S)$ vs. Asymptotic restriction $T \lesssim S$.
*   **Substrate Input:** This work proves separations between moment polytopes of matrix multiplication tensors $M_n$ and unit tensors. Explicitly, it yields the UNCONDITIONAL result that $\Delta(M_n)$ is strictly contained in the corresponding Kronecker polytope [cite: 7, 8]. 
*   **Anti-Gravity Flag:** This provides a definitive "no-go" result for a natural operational characterization of moment polytope inclusion in terms of asymptotic restriction [cite: 7], severing a suspected equivalence bridge.

**2. Resolution of the Support Functional Conjecture (January 29, 2026)**
*   **Source:** Sakabe, Doğan, Walter. *Strassen's support functionals coincide with the quantum functionals.* arXiv:2601.21553 [cite: 9, 10].
*   **Coordinate Addressed:** Strassen upper support functional $\zeta^\theta$ vs. Quantum functional $F^\theta$.
*   **Substrate Input:** This resolves a 1991 open problem posed by Strassen. It proves UNCONDITIONALLY that the support functionals $\zeta^\theta$ exactly coincide with the quantum functionals $F^\theta$ (which are defined via entropy optimization on entanglement polytopes). 
*   **Algorithmic Anchor:** The proof relies on a Fenchel-type duality theorem on Hadamard manifolds due to Hirai (2025) [cite: 9, 10]. The substrate must link $F^\theta$ and $\zeta^\theta$ via an exact equivalence mapping.

**3. Deterministic Polynomial Computability of Edge Functionals (April 1, 2026)**
*   **Source:** Alman, Li, Pratt. *The edge of the asymptotic spectrum of tensors.* arXiv:2604.01386 [cite: 11, 12].
*   **Coordinate Addressed:** Edge support functionals $\zeta^\theta$ (where $\theta$ lies on the boundary of the simplex $\Theta$).
*   **Substrate Input:** Extending Sakabe et al. 2026, this work proves that edge support functionals are uniquely determined as spectral points by their behavior on matrix multiplication tensors [cite: 11, 12]. 
*   **Algorithmic Anchor:** Uncovers a structural isomorphism between edge support functionals and Harder-Narasimhan filtrations from quiver representation theory. Consequently, it proves these functionals are computable in deterministic polynomial time [cite: 11, 12].

## (c) FALSE-FORM RECURRENCE

**Substrate Target:** Anti-anchor pin deployments.
An analysis of the literature and anticipated systemic gradients reveals multiple false forms that must be actively countered by the substrate. 

**False Form 1: "Asymptotic rank is computable."**
*   **The Gravity Well:** Because CHNVZ 2024 proves the sublevel sets of asymptotic rank are Zariski-closed and evaluated via finite polynomials, there is a strong gradient toward collapsing this into full algorithmic decidability.
*   **The True Form:** Asymptotic tensor rank is ONLY "computable from above." For any $r \in \mathbb{R}$, there is an algorithm to decide if $\underaccent{\wtilde}{R}(T) \leq r$ [cite: 1, 3]. There is currently NO known algorithm to compute the exact value of $\underaccent{\wtilde}{R}(T)$ in the general case, nor is it known to be computable from below.

**False Form 2: "The values of asymptotic tensor rank are discrete."**
*   **The Gravity Well:** Equating well-orderedness with full topological discreteness.
*   **The True Form:** The set of values $\mathcal{R}$ is well-ordered, meaning it has "discreteness from above" (any non-increasing sequence stabilizes) [cite: 1, 13]. CHNVZ 2024 explicitly states: *"We leave open whether asymptotic rank is also discrete from below (which would be implied by Strassen's asymptotic rank conjecture)."* [cite: 4, 13]. Pinning this anti-anchor prevents the substrate from hallucinating bidirectional isolation of spectral values.

**False Form 3: "Strassen's support functionals are spectral points." (When dated prior to January 2026)**
*   **The Gravity Well:** The literature frequently references Strassen's upper support functionals $\zeta^\theta$ alongside spectral points, leading to a retroactive assumption that they were always known to be elements of the asymptotic spectrum.
*   **The True Form:** Strassen *proposed* $\zeta^\theta$ as candidate spectral points in 1991. They were NOT definitively proven to be universal spectral points until Sakabe, Doğan, and Walter proved $\zeta^\theta = F^\theta$ in January 2026 [cite: 9, 12]. The substrate must strictly enforce this timeline constraint.

## (d) RECOMMENDATION

**Substrate Target:** Tier placement, Anti-anchor deployment, and Work-queue execution.

**1. Assessment of the Anti-Anchor Candidate**
The candidate `Survey AsymptoticSpectrumMonotone outside-tier primitive supporting lit (T#28 CHNVZ 2024 polynomial char)` is **VALID BUT REQUIRES REFINEMENT**. 
*   **Action:** Do not register it simply as "polynomial char." Register the primitive exactly as: `Algorithmic Computability from Above for Asymptotic Tensor Rank`.
*   **Action:** Deploy a companion anti-anchor restricting the interpretation of "discreteness" to strictly "discreteness from above / well-orderedness". Do not permit the substrate to infer discreteness from below.

**2. Tier Placement Decision**
*   **Action:** Elevate from an outside-tier primitive to a **Tier-1 core primitive**. The finding that the sublevel sets of $\underaccent{\wtilde}{R}$ are Zariski-closed over infinite fields ($\mathbb{C}$) fundamentally alters the parameter space for algebraic complexity. It directly bridges topology, optimization algorithms, and algebraic geometry, satisfying the highest substrate impact criteria.

**3. New Sub-Anchors Discovered (HARD-5 Enforcement)**
*   **Action:** Register the equivalence mapping $\zeta^\theta \equiv F^\theta$ (Strassen support functional equivalent to Quantum functional) anchored to Sakabe, Doğan, Walter (Jan 2026) [cite: 9, 10].
*   **Action:** Register the non-maximality of $\Delta(M_n)$ anchored to van den Berg et al. (Mar 2025) [cite: 7]. This must be pinned with a strict decoupling from asymptotic restriction equivalence.
*   **Action:** Register deterministic polynomial computability for edge support functionals anchored to Alman, Li, Pratt (Apr 2026) [cite: 11, 12]. Link this explicitly to the primitive `Harder-Narasimhan filtrations`.

**4. Verification Queue Additions**
*   *Work-Queue Entry:* Verify the exact relationship between the newly defined deterministic polynomial computability of edge support functionals [cite: 11, 12] and the existing lower bounds on the matrix multiplication exponent $\omega$. 
*   *Work-Queue Entry:* Assess the implications of Alman et al. 2026's warning that "Even over $\mathbb{C}$, higher-order quantum functionals are not completely understood" [cite: 12] against current quantum marginal models within the substrate. Ensure `higher-order quantum functionals` are isolated as distinct coordinates from standard $F^\theta$.

**Sources:**
1. [Link](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqcF787PvKYBfcuHXh7wmJ6DS5IPLwQ16J1LD9V3E_L6726XKMlRlK_zUI1vKhbFmkE45Kciz6a8oDxiArJ-VqrzElw49cOxbrmiJMwLHeko0m87oyOIkE_Q==)
2. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEb4mLGCjNhgymbOZJc3Fk4_Rswj_QuN63COuoGNLyDu5IgoW2TKCBjqxl_Ca1jjCuUfpItvtgrUNQd-LbJni7KUOo2sxc3nA6jNWJ9oUXewn_iZa_vRfIyfv_7)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEu0pvNL4eFQBDCHh8ilwl9g6lazuqWH5zyatvLDjnv4SPuCayq_rZGDDzwgpzX2iahNZJKmYx-e4jJulEn4bs5xgEGeMR7GA9tXw7MiYtD1XTTKWTfjg==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdgqBha9Up8hHPKXqM_o5ixFEuOLpoERAFqw4QGin9E4jZkCNznlJVnliu616SsfPigdlknH28ehS0h1knZFpcOJYX5kFbk_FYwy9zWxoeVlC6MJzbwQ==)
5. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRhMjoKVK-j7Lj5HxvMujMbLBsdcmemM2MMCsMMhGzZl56qUXEaDp-9rvmD9dqO2Nkuh-H4kwYDbls3GnYe4jjuPIGnJsvQQEiYd_aueWECFG9_-2pVbx1k03Z)
6. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvSxHG6b0M3OK1JHnjTaUpjV5i-nQT4Iq54abM8-oLsWLKqrEJslA8FW5go2u_s0-48ESBT6cOsH9ElDsROYmgUKzJ9nynZmvXgO23cAKAq2r3Uyrx-1n6-5FCxolPqpnqINwU2VS6OJATMVfsRMNJznRsF9WDQ9iQNQL2rw==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE86KP6UkOwDOyK0K4jAFq26ucNTyHB7js1XDosUiQg7MrE1d7dqZO-uUBQy39zWxS50bmDvWkwHtTvoPPWbQIfJrgk-5kvo7FKbibjI0K_cDyHaIl6QQ==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkaD8fR7DNDMgXUxA_DsV_iXqkKgdV1l8UZmnhegMU1fORtqhCAVdtcRJH3QQWzCKhwnhaMkYdeCMumKNqVwm4cVJq-H550Y1MDZePDutyUYrPbk3gww==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlxjSzI0IgI9r18Z9tbbx8w4U_iUkxy6ROqTI_2tG4iLZ3L01zCBOitDEMj_bQk7eXm-HksTjP_ZFxBkA94qmL-aH9lB6eI1j8Kww93wCjfCyN0M-fNs4uGg==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLjMaBWWVNHsi5xv4c5W60wpqyNZczgMx63AmbXMWtM_UYWM8_HeY9jjKQ4udF-l3fQ7cf6JwI0hSLfTEx7au4urmUOfqqIs0MM_w9aSiRrh-DZJ0U3Q==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZSfd8upVxkVlaulAJ3-Md5QJHzS1-s1r763NDoAwzhKE9qKfSJhSv7I7eqMs0ZJc2RpQqjROynMubo-3Pb80e867ZEcSkjkP6Q-dnyjY_7oioJDVOow==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgYFK-U0siVg_QiutiKxzquuxvIKj8UliWf7bvnPA1rsyIDMGBkA0YYDQY8snjL-XGH4gbuuRWkv-3d64JrQQfLZ25fPkLuPcSliwDL__Vpp0N5Az0YYmz_g==)
13. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3L_lOm0NnXIVczaLvnO0F8exvNjCEmDfbvDGriJw757o_Z5yUnpoxK99dA7idJx41guOPVtj3B0uomCd4MGfMw55iCbZ1CsOMo7gYsTFshVg=)

