# Prompt 12: DR-051 — T#2 Strassen asymptotic rank conjecture (concise tight tensors) [Tier 2]

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdFb1VGYXBhUUlkT1lfdU1QdnFuLXNBdxIXRW9VRmFwYVFJZE9ZX3VNUHZxbi1zQXc
**Elapsed:** 273s

---

# Project Prometheus Verification Report: Anti-Anchor T#2 (Strassen Asymptotic Rank Conjecture)

**Key Points:**
*   **Verification Status:** CONFIRMED. The anti-anchor candidate T#2 correctly identifies the Strassen Asymptotic Rank Conjecture as a foundational coordinate in algebraic complexity theory.
*   **Crucial Constraints:** The conjecture strictly requires the base tensor to be both **tight** and **concise**. Omission of these combinatorial constraints is a documented failure mode in recent literature.
*   **Algorithmic Implications:** If true, the conjecture unconditionally bridges algebraic complexity and fine-grained exponential-time algorithms, invalidating the Set Cover Conjecture.
*   **Topological Invariants:** Recent proofs confirm that sublevel sets of asymptotic tensor rank are Zariski-closed, moving the coordinate from purely analytic to algebraic.

**Substrate Meta-Data:**
*   **Target:** T#2 Strassen asymptotic rank conjecture (concise tight tensors).
*   **Coordinates Referenced:** Tensor rank, border rank, asymptotic tensor rank, border subrank, worst-case tensor exponent, localized tensor exponent.
*   **Actionable Output:** 4 primitive registrations, 3 catalog edits, 2 training-corpus filters.

---

## (a) PRIMARY SOURCE CONFIRMATION

**Substrate Input:** Anti-anchor pin definition and primary coordinate registration.

The anti-anchor candidate traces to Volker Strassen's foundational synthesis in 1994. The definitive publication is:
V. Strassen, "Algebra and complexity," *First European Congress of Mathematics, Vol. II (Paris, 1992)*, Progress in Mathematics, Vol. 120, Birkhäuser, Basel, 1994, pp. 429–446 [cite: 1, 2]. 

**Exact Theorem Statement / Conjecture Formulation:**
Let $\mathbb{F}$ be a field. Let $T \in \mathbb{F}^m \otimes \mathbb{F}^m \otimes \mathbb{F}^m$ be a three-tensor. Strassen's Asymptotic Rank Conjecture asserts that if $T$ is **tight** and **concise**, then the asymptotic tensor rank $\tilde{R}(T)$ is minimal, specifically:
$\tilde{R}(T) = m$ [cite: 3].

**Coordinate Disambiguation (HARD-5 compliance):**
To maintain substrate integrity, we explicitly distinguish the required invariants. The gravity well of "tensor complexity" frequently collapses these. Prometheus must isolate them:
1.  **Tensor Rank ($R(T)$):** The minimum integer $r$ such that $T$ is a sum of $r$ elementary tensors.
2.  **Border Rank ($\underline{R}(T)$):** The minimum integer $r$ such that $T$ can be approximated arbitrarily closely by tensors of rank $r$.
3.  **Asymptotic Tensor Rank ($\tilde{R}(T)$):** Defined as $\lim_{N \to \infty} R(T^{\otimes N})^{1/N}$. This is the exact coordinate of Strassen's Conjecture [cite: 2].
4.  **Worst-Case Tensor Exponent ($\sigma(d)$):** The supremum of the asymptotic rank exponent over all tensors in $\mathbb{F}^d \otimes \mathbb{F}^d \otimes \mathbb{F}^d$.
5.  **Localized Tensor Exponent ($\sigma(\Delta)$):** The worst-case exponent restricted to tensors with support contained in a specific combinatorial subset $\Delta \subseteq [d] \times [d] \times [d]$ [cite: 1, 4].

**Definitional Primitives:**
*   **Concise:** A tensor $T \in A \otimes B \otimes C$ is concise if its induced linear maps (e.g., $T_A: A^* \to B \otimes C$) are injective [cite: 2].
*   **Tight:** A tensor is tight if there exist injective functions $\tau_A: [a] \to \mathbb{Z}$, $\tau_B: [b] \to \mathbb{Z}$, and $\tau_C: [c] \to \mathbb{Z}$ such that $\tau_A(i) + \tau_B(j) + \tau_C(k) = 0$ for every $(i,j,k)$ in the support of $T$ under some basis [cite: 2]. Geometrically, it is annihilated by a regular semisimple element of $\mathfrak{gl}(A) \oplus \mathfrak{gl}(B) \oplus \mathfrak{gl}(C)$ [cite: 2].

**Primary Source Qualification:** 
The conjecture was formulated explicitly for *tight* tensors because tightness provides combinatorial properties essential to Strassen's laser method [cite: 2, 3]. The primary source is PEER-REVIEWED and currently stands as UNRESOLVED (neither unconditionally proved nor disproved).

---

## (b) FOLLOW-ON WORK (2024-2026)

**Substrate Input:** Catalog edits and primitive registrations reflecting the 24-month research frontier. 

The 2024–2026 window exhibits severe gravity-well disruption. Algebraic complexity has structurally intersected with exponential-time algorithm lower bounds, and the topological properties of asymptotic rank have been rigidly characterized.

**1. Set Cover Conjecture Incompatibility (June 2024)**
*   **Source:** A. Björklund and P. Kaski, "The Asymptotic Rank Conjecture and the Set Cover Conjecture Are Not Both True," *Proceedings of the 56th Annual ACM Symposium on Theory of Computing (STOC 2024)*, June 2024, pp. 859–870. (Preprint arXiv:2310.11926, October 2023) [cite: 1, 5, 6].
*   **Result (UNCONDITIONAL proof of CONDITIONAL implication):** If Strassen's Asymptotic Rank Conjecture is true (specifically over finite fields or $\mathbb{C}$), then the $k$-Set Cover Conjecture is false. This yields an $O((2-\epsilon)^n)$ randomized algorithm for $k$-Set Cover, and consequently, an $O((2-\delta)^n)$ randomized algorithm for Directed Hamiltonian Cycle [cite: 5, 6].
*   **Refinement:** The authors prove that the full strength of the conjecture is not required; it suffices that the conjecture holds approximately for a single explicit $7 \times 7 \times 7$ tight and concise tensor [cite: 5]. 
*   **Actionable Delta:** Register a cross-domain anti-anchor pin between `Algebraic Complexity (Tensors)` and `Fine-Grained Complexity (SETH/Set Cover)`.

**2. Polynomial Characterization and Zariski-Closure (November 2024 / June 2025)**
*   **Source:** M. Christandl, K. Hoeberechts, H. Nieuwboer, P. Vrana, J. Zuiddam, "Asymptotic tensor rank is characterized by polynomials," *Proceedings of the 57th Annual ACM Symposium on Theory of Computing (STOC 2025)*, June 2025. (Preprint arXiv:2411.15789, November 2024) [cite: 7, 8, 9].
*   **Result (UNCONDITIONAL):** The sublevel sets of asymptotic tensor rank are Zariski-closed over any field [cite: 7, 9]. 
*   **Result (UNCONDITIONAL):** Asymptotic tensor rank is "computable from above." For any real number $r$, there is an algorithm that evaluates a finite list of polynomials to determine if $\tilde{R}(T) \leq r$ [cite: 7, 8].
*   **Result (UNCONDITIONAL):** The set of values that asymptotic tensor rank takes on all tensors is well-ordered (discrete from above). Consequently, any sequence of exponents of bilinear maps that approximates the matrix multiplication exponent $\omega$ arbitrarily closely from above must be eventually constant [cite: 8, 10].
*   **Flag for Premature Claims:** The authors state asymptotic rank is "computable from above," but explicitly note they *do not exhibit these polynomials explicitly* [cite: 8, 9]. Downstream substrate agents must not assume constructive polynomial availability.

**3. Universal Sequences for the Asymptotic Rank Conjecture (February 2025)**
*   **Source:** P. Kaski and M. Michałek, "A Universal Sequence of Tensors for the Asymptotic Rank Conjecture," *16th Innovations in Theoretical Computer Science Conference (ITCS 2025)*, LIPIcs Vol. 325, February 2025 [cite: 1].
*   **Result (UNCONDITIONAL):** Construction of an explicit universal sequence of zero-one-valued tensors $\mathcal{U}_d$ that exactly captures the worst-case tensor exponent $\sigma(d) = \sup_{T} \sigma(T)$ [cite: 1]. By combining these, they construct a universal sequence $\mathcal{T}_d$ such that $\sigma(\mathcal{T}_d) = 1$ if and only if Strassen's Asymptotic Rank Conjecture holds for dimension $d$ [cite: 1].
*   **Anti-Gravitational-Well Enforcement:** This paper explicitly surfaces an alternative to the "Matrix Multiplication ($MM_2$) is the universal tensor" gravity well. Strassen implicitly observed in 1988 that $MM_2$ has *limited universality* ($\sigma(\mathbb{F}^d \otimes \mathbb{F}^d \otimes \mathbb{F}^d) \leq \frac{4}{3}\sigma(MM_2)$) [cite: 1]. The universal sequences provided by Kaski and Michałek bypass this limitation [cite: 1].

**4. Moment Polytope Non-Maximality (March 2025)**
*   **Source:** M. van den Berg, M. Christandl, V. Lysikov, H. Nieuwboer, M. Walter, J. Zuiddam. "The moment polytope of matrix multiplication is not maximal." (Preprint arXiv:2503.22633, March 2025) [cite: 11].
*   **Result (UNCONDITIONAL):** Proves separations between moment polytopes of matrix multiplication tensors and unit tensors, establishing a new proof of the optimal border subrank bound for matrix multiplication [cite: 11]. 

---

## (c) FALSE-FORM RECURRENCE

**Substrate Input:** Training-corpus filters and semantic-drift detection parameters.

A critical failure mode exists in the 2024–2026 literature: the gravitational pull of simplification causes authors to state Strassen's conjecture without the **tightness** and **conciseness** constraints, projecting it onto *all* tensors. 

**Specific Instances of False-Form Recurrence:**

1.  **Christandl et al. (November 2024 / June 2025) [cite: 7, 8, 10]:** 
    In the abstract of *Asymptotic tensor rank is characterized by polynomials*, the authors state: 
    > "Strassen's asymptotic rank conjecture, on the other hand, makes the bold statement that asymptotic tensor rank equals the largest dimension of the tensor and is thus as easy to compute as matrix rank." [cite: 8, 10].
    
    *Substrate flag:* This formulation omits the critical combinatorial constraint of tightness. Taken literally, this sentence asserts that *every* tensor has an asymptotic rank equal to its largest dimension, which is unequivocally false (as many tensors are not concise, and non-tight concise tensors are not covered by the conjecture).

2.  **Zuiddam / Simons Institute Lecture Descriptions (November 2025 scheduled) [cite: 12]:**
    In the abstract for the upcoming lecture *Asymptotic Tensor Rank Is Characterized By Polynomials*:
    > "On the other hand, Strassen's asymptotic rank conjecture makes the bold claim that asymptotic tensor rank equals the largest dimension of the tensor..." [cite: 12].

    *Substrate flag:* Continued propagation of the unqualified statement in institutional public-facing materials.

**Analysis of the Drift:**
The authors are utilizing this simplified framing purely for rhetorical contrast in abstracts (comparing the difficulty of finding the rank of $MM_2$ against the "bold claim" that asymptotic rank is just the matrix dimension) [cite: 8]. However, for an automated mathematical substrate like Prometheus, this semantic drift is catastrophic. It conflates **Conjecture 1** (Strassen's Asymptotic Rank Conjecture for *tight* tensors) with **Conjecture 2** (The Extended Asymptotic Rank Conjecture for *all concise* tensors) [cite: 4]. 

As Kaski and Michałek explicitly note in ITCS 2025:
> "A yet stronger conjecture (cf. Bürgisser, Clausen, and Shokrollahi [16, Problem 15.5]...) states that the least possible exponent is shared by all concise tensors... [Conjecture 2 (Extended asymptotic rank conjecture)]" [cite: 4].

**Conclusion on Anti-Anchor:** The anti-anchor is strictly NEEDED. The training corpus must filter or flag these abstract-level rhetorical simplifications to prevent the substrate from attempting to prove or utilize the false form (that $\tilde{R}(T) = \max \dim(T)$ for absolutely any $T$).

---

## (d) RECOMMENDATION

**Substrate Input:** Work-queue entries, catalog hierarchy updates, and actionable system behavior deltas.

**(i) Anti-Anchor True Form Status:**
The anti-anchor candidate **"T#2 Strassen asymptotic rank conjecture (concise tight tensors)"** is CORRECT AS STATED but needs **refinement** to explicitly codify the distinction between the original and extended conjectures. 
*   *Catalog Edit:* Rename T#2 to `T#2_Strassen_AsympRank_TightConcise`.
*   *Catalog Addition:* Create sibling coordinate `T#2_Extended_AsympRank_ConciseOnly` to capture the Bürgisser-Clausen-Shokrollahi generalization [cite: 4].

**(ii) New Sub-Anchors Discovered:**
1.  **Sub-Anchor T#2-A: Topological Algebraicity of AsympRank:** Sublevel sets of asymptotic tensor rank are unconditionally Zariski-closed over any field (Christandl et al., 2024/2025) [cite: 7, 10]. This is a massive structural primitive shifting the invariant from analytic geometry limits to algebraic geometry ideals.
2.  **Sub-Anchor T#2-B: Asymptotic Rank / SETH Bridge:** Conditional on T#2 being true for a specific $7 \times 7 \times 7$ tight concise tensor, the $k$-Set Cover Conjecture is false (Björklund & Kaski, 2024) [cite: 5].
3.  **Sub-Anchor T#2-C: Limit Approximations of $\omega$:** Due to the discreteness from above of asymptotic rank, any non-increasing sequence of bilinear map exponents that approximates the matrix multiplication exponent $\omega$ arbitrarily closely from above will "snap" to it and become eventually constant (Christandl et al., 2024/2025) [cite: 8, 10].

**(iii) Work-Queue Entries for the Verification Queue:**
*   **Queue Item 1 (Constructive Algebraic Geometry):** Trigger a search module for the *explicit* polynomials guaranteed by Christandl et al. [cite: 8, 9]. Since the authors only proved existence via general algebraic properties, the actual extraction of these polynomials for small dimensions (e.g., $3 \times 3 \times 3$) is an open primitive registration target.
*   **Queue Item 2 (Universal Sequence Evaluation):** Ingest Kaski and Michałek's ITCS 2025 construction of the universal sequence $\mathcal{U}_d$ [cite: 1]. Register the sequence generator in the execution environment to test localized tensor exponents $\sigma(\Delta)$ [cite: 4].
*   **Queue Item 3 (Subrank Barrier Extension):** Verify the March 2025 preprint by van den Berg et al. [cite: 11] regarding the non-maximality of the matrix multiplication moment polytope, extracting the "optimal border subrank bound for matrix multiplication" as a new verified coordinate independent of asymptotic rank [cite: 11]. 

**Behavior Delta Executed:** The Prometheus multi-agent substrate must permanently severe the conceptual link between "tensor rank" and "asymptotic tensor rank" in its symbolic reasoners, heavily weighting the "Zariski-closed" properties of the latter [cite: 9, 10], while deploying a training-corpus filter to rewrite all instances of "Strassen's conjecture" that drop the tightness constraint.

**Sources:**
1. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGboqFbUIlmCbitODG7Dy34H-2DFe311jw8I8P0p8_IFK3oZ5e3I6EIUY3az01NEfhIZYrWP12k1_AY7CJ0AIyg8sfTJZaJowpkah4aQ5VC-jGAkrpmLNV0zO7FoAjXXZip_82N7vYGAcTj-MZXySymxzDeLi3_ItwY-F1SBQ==)
2. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbq7KhijAfqm_-lsJ02fOe_3MqRV8kNymcDUpqaPn8WqHRCXrSBOJuHnBLWftbQSNmC9rsOFKnki35wAiSxpMVOG9AxjuQkYxRiAwc4XF7OmXv9tGmeUQzie5cxO9V2LNnvXkBW_7Z)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHajDK7Vf3tupWyWvyOboirAPvgZdSH06Yxwyakqa2wFFD34AtNgCW0PqPftDRQMQkfa7fbxlxVdDGGm4pbe4PAynqvb_iXVsuyrDrrf3DRRPN_DdhPcw==)
4. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJiNUC3BAvgugQb4PhLjbm71hw6L8IRd-qm6FvlKv6_D0WLYQfISDh7sJtlAhwygDYTa9gKQ48ru6Rt50RctmbEjzuohX9gbrN3CMpRcd1hbwO-A94KTcQ0NE1GSIZ03jHUZ_jGfYqz1SR0E9esqdaflB8v61SfGtC5cASSMyS8sL-5_PtL-42i5og1tH32-bTYUjxr9D06sADvKMMgN_uf_SA)
5. [aalto.fi](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3cAYgQzRoV6dfBMdRDzs5J_7IxesVCguRfYPnjRprUTi_xLS_lFdhryX2EP6l5hbrkXsyDe_sqtEjxR26whgpzId2XeEhx8nAWZZXRFTvBtS-NXeJ7i_y0zILzK29EeJhpBIWaWpqhPnEKwW-ehsUnhZo9OJOFUVZW69MxcauAlFkZLC3HEXARj6zJCQ=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHV1LOZcoBSlnbRbVYMgSXCS7Q6pPXH8uVYACyxvMru8E_JrYp1Xc4OkFo0nbEu5RqC5INU7OHVdJnr1RQ4kWV4mckX6coBKQNeoLCdC_p4R-CY_x1V4g==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeiUsow_-7WPbU7v2R4ki6tRmmFYmqSVnByRxOTLh0mONvQ8S9OtE7S--d9nDHoYQNIqcgC1_p9raViGJ7QEjpVFMyWfT7g7HY1USsGQk7cwbjk8dZlQ==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRPgL0R-JLE7X3pS_0E1SGJZOa4jJnOaITy43OblW08q07zMuKz2Wy3283ENjquanv_o9axskqQtl5gcV4Hd0ZkuUf0GjD5DeiqTZyhIGO8QORZ9oi8w==)
9. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtMA9j2lK9u_1VCITJ8gwoLMUs7l_zNr7FLarjk59IpVJd4wHiY4r9C7RBkQ9xvS87XFX240BHZGHcK-yTbFNuntxkan4PPWk_CiMhf7g9fRaWzCrtObgLgtWi)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG68C4GOS0oq4gmsHdwP0nboo9KVesSCBOenf16Q3DOHv7IJZPYkY9BMxFEetunKxSo8ydBPMQWKwYMyqBTyPlOLWV2hmsYFbRt5-8Q5oQwfhf0_b7E7dukRA==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUMba7KavQgAzYFRloLkxWRJIatdpzz9KxJyf_XyAuoe4tuuYcgJf0QKgNyn_E39tBL_bGuhQlCQHXA0otsKIT1KO5I4AhlGU448SOEGAH2EE7Yae_lg==)
12. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBxMGNf8nR2y15CXJCs1nAQFSgVgM5GehBsXsvuaunSJpVlaJvF8HpKA6Z9ZYaL7vo5YjBAL8DranInCpLllvENQOdWySc7lH_d_xu4EyjUVtSH6_-TJ6x9N_UIThPkeiHJEpf4DcDD0LxxffJEQc37UgUoxcV1oQU5hJssqqrvyUAdIxhYBbV2A==)

