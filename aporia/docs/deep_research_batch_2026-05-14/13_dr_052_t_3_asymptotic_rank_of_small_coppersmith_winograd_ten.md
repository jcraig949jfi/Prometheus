# Prompt 13: DR-052 — T#3 Asymptotic rank of small Coppersmith-Winograd tensor T_cw,2 [Tier 2]

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChZZSVlGYXRkN2g2RDg5UV9hcXRTNUF3EhZZSVlGYXRkN2g2RDg5UV9hcXRTNUF3
**Elapsed:** 424s

---

# Anti-Anchor Verification: T#3 Asymptotic Rank of Small Coppersmith-Winograd Tensor 

The following report assesses the validity, coordinates, and downstream applicability of the anti-anchor candidate concerning the asymptotic rank of the small Coppersmith-Winograd tensor \( T_{cw,2} \). 

*   **Coordinate Separation is Mandatory:** The candidate correctly identifies the mathematical implication that if the asymptotic rank \( \tilde{R}(T_{cw,2}) = 3 \), then the matrix multiplication exponent \( \omega = 2 \). However, the candidate conflates the invariant targets of the prescribed tools. **Border apolarity** computes exact border rank \( \underline{R} \) for finite Kronecker powers, while **quantum functionals** bound asymptotic limits \( \tilde{R} \) and asymptotic subrank \( \tilde{Q} \). 
*   **Recent Breakthroughs (2024-2025):** The literature landscape has shifted dramatically. Work announced in November 2024 proves that asymptotic tensor rank sublevel sets are Zariski-closed and discrete from above, meaning \( \tilde{R} \) is characterized by polynomials [cite: 1, 2]. Furthermore, an explicit universal sequence of tensors has been constructed as of April 2024 to capture worst-case tensor exponents [cite: 3, 4].
*   **Actionable Substrate Inputs:** The candidate requires structural refinement. The unitary claim must be split into distinct primitive registrations: one for finite-power border rank evaluations (the \( \underline{R}(T_{cw,2}^{\boxtimes 2}) = 16 \) barrier) and one for asymptotic evaluation barriers (the irreversibility of \( T_{cw,2} \)).

These findings are structured below for direct ingestion into the Project Prometheus substrate as catalog edits, anti-anchor pins, and work-queue entries.

---

## (a) PRIMARY SOURCE CONFIRMATION

The candidate anti-anchor asserts: *"Concrete tensor anchor; if asymp rank = 3 then omega=2; needs border apolarity + quantum functionals applied to T_cw,q"*. 

Verification of the primary literature confirms the mathematical truth of the conditional implication, but necessitates strict separation of the invariants and methodologies named in the candidate.

**1. The Implication: \( \tilde{R}(T_{cw,2}) = 3 \implies \omega = 2 \)**
The core implication is unconditionally verified in the peer-reviewed literature. The matrix multiplication exponent \( \omega \) is tightly coupled to the asymptotic rank \( \tilde{R} \) of the matrix multiplication tensor \( \langle 2,2,2 \rangle \), such that \( 2^\omega = \tilde{R}(\langle 2,2,2 \rangle) \) [cite: 5, 6]. Christandl, Hoeberechts, Nieuwboer, Vrana, and Zuiddam (November 2024, ANNOUNCED-NOT-PUBLISHED for STOC 2025) explicitly confirm this relationship for the small Coppersmith-Winograd tensor: 
> "For example, it is well-known that if the asymptotic rank of the small Coppersmith–Winograd tensor \( cw_2 \) equals 3, then \( \omega = 2 \). For which tensors can we prove this property? It follows... that \( cw_2 \) has asymptotic rank at most the generic asymptotic rank of \( 3 \times 3 \times 3 \) tensors with hyperdeterminant 0" [cite: 5, 7].

**2. Coordinate Distinction: Border Apolarity vs. Quantum Functionals**
The candidate prescribes "needs border apolarity + quantum functionals applied to \( T_{cw,q} \)". This phrasing collapses mathematically distinct coordinates and must be pinned as an anti-anchor. 

*   **Coordinate A: Border Rank \( \underline{R}(T) \)**. Border apolarity is an algebraic geometry technique operating on the Haiman-Sturmfels multigraded Hilbert scheme [cite: 8, 9]. It establishes lower bounds on the **border rank** of finite tensors. In definitive PEER-REVIEWED work by Conner, Gesmundo, Landsberg, and Ventura (arXiv:1909.04785, published 2021), the authors applied border apolarity to the Kronecker square of the small Coppersmith-Winograd tensor, proving:
    > "We prove that the border rank of the Kronecker square of the little Coppersmith-Winograd tensor \( T_{cw,q} \) is the square of its border rank for \( q > 2 \)... For \( q=2 \), the Kronecker square of this tensor coincides with the \( 3 \times 3 \) determinant polynomial... we prove the negative result for complexity theory that its border rank is 16, resolving a longstanding problem" [cite: 10, 11].
*   **Coordinate B: Asymptotic Rank \( \tilde{R}(T) \) and Asymptotic Subrank \( \tilde{Q}(T) \)**. Quantum functionals are universal spectral points developed by Christandl, Vrana, and Zuiddam [cite: 4, 12]. They do not compute border rank; they evaluate the **asymptotic slice rank** \( \tilde{S}(T) \), serving as an upper bound on asymptotic subrank \( \tilde{Q}(T) \) and a lower bound on asymptotic rank \( \tilde{R}(T) \) [cite: 12, 13]. 

**Substrate Input Generation:** The primary source confirmation requires splitting the candidate into two primitive registrations. 
1.  *Primitive 1:* Exact border rank invariant \( \underline{R}(T_{cw,2}^{\boxtimes 2}) = 16 \), precluding \( \omega = 2 \) proofs via naive 2nd-power laser methods.
2.  *Primitive 2:* Asymptotic limit bounding \( \tilde{R}(T_{cw,2}) = 3 \implies \omega = 2 \), constrained by the irreversibility ratio \( i(T) = \log_2(\tilde{R}(T)) / \log_2(\tilde{Q}(T)) \) [cite: 6, 14].

---

## (b) FOLLOW-ON WORK (2024-2026)

The 2024-2026 window shows aggressive evolution in the geometric and algebraic characterization of asymptotic tensors, heavily shifting the consensus away from classical finite-power laser methods. 

**1. Polynomial Characterization of Asymptotic Rank (November 2024)**
Christandl, Hoeberechts, Nieuwboer, Vrana, and Zuiddam (arXiv:2411.15789, ANNOUNCED for STOC 2025) achieved a fundamental breakthrough regarding the computability and topological structure of the asymptotic rank \( \tilde{R}(T) \) [cite: 1, 7]. 
*   **Result:** They prove that asymptotic tensor rank is "computable from above." The sublevel sets of asymptotic rank are Zariski-closed over infinite fields (like \( \mathbb{C} \)) [cite: 1, 2]. 
*   **Discreteness:** They establish that the sequence of asymptotic ranks is a well-ordered set ("discreteness from above"). Thus, any upper bound on \( \omega \) that approaches the limit closely enough will "snap" to it [cite: 1, 2].
*   *Actionable Delta:* This result transitions asymptotic rank from a purely limiting concept to an algebraically characterizable locus. Work-queue entry: Implement zero-testing of the newly proven (though non-explicit) bounding polynomials against \( T_{cw,2} \) coordinate representations.

**2. Universal Sequences for Asymptotic Rank (April 2024)**
Kaski and Michałek (arXiv:2404.06427, ANNOUNCED-NOT-PUBLISHED) shifted the focus from the Coppersmith-Winograd tensor to explicitly constructed universal sequences [cite: 3, 4]. 
*   **Result:** They constructed an explicit sequence of zero-one-valued tensors \( \mathcal{U}_d \) that achieves the worst-case tensor exponent \( \sigma(d) \) [cite: 3, 15]. 
*   **Context:** By connecting the absence of fixed-degree vanishing polynomials on low-rank tensors to upper bounds on the exponent \( \sigma(d) \), they provide an entirely independent substrate pathway to resolving Strassen's asymptotic rank conjecture, bypassing \( T_{cw,q} \) altogether [cite: 3, 4].
*   *Actionable Delta:* Catalog edit. Add \( \mathcal{U}_d \) as a Tier-A universal sequence primitive, weighted equal-or-higher to \( T_{cw,q} \) families to resist the Coppersmith-Winograd gravity well.

**3. Finite-Power Elementary Proofs (July 2025)**
D. Kawabe (arXiv:2507.13126, ANNOUNCED-NOT-PUBLISHED) submitted a preprint explicitly addressing the border rank of Kronecker products of the Coppersmith-Winograd tensor [cite: 16, 17].
*   **Result:** Provides a detailed, elementary linear-algebraic proof of the Conner-Gesmundo-Landsberg-Ventura (2021) result that \( \underline{R}(T_{cw,q}^{\boxtimes 2}) = (q+2)^2 \) [cite: 17, 18].
*   **Flag:** The author claims the ideas "seem to extend to the case of the Kronecker cube, pointing toward the conjectural value \( (q+2)^m \) (\( m \ge 4 \)), although a full proof is left for future work" [cite: 17, 18]. *Caution: Prometheus must flag the \( m \ge 4 \) bound as CONDITIONAL and unverified.*

---

## (c) FALSE-FORM RECURRENCE

The substrate must defend against two distinct LLM/literature gravity wells regarding matrix multiplication complexity. 

**False Form 1: "The Laser Method applied to CW tensors is the sole viable path to \( \omega = 2 \)."**
*   *Recurrence:* Many algorithmic complexity surveys inherently frame the search for \( \omega=2 \) exclusively through the lens of finding optimal zeroing-outs of \( T_{cw,q}^{\boxtimes n} \). 
*   *Correction (Anti-anchor needed):* The literature clearly shows the Laser Method is hitting structural barriers. Alman and Vassilevska Williams proved that the Universal Method (which subsumes the Laser Method) applied to any Coppersmith-Winograd tensor \( CW_q \) cannot yield a bound on \( \omega \) better than 2.16805 [cite: 19, 20]. Furthermore, Christandl, Vrana, and Zuiddam proved an "irreversibility barrier" showing that irreversible tensors cannot prove \( \omega = 2 \) via standard reductions [cite: 6, 14].
*   *Alternative surfacing:* Group-theoretic algorithms (Cohn-Umans) using Lie groups [cite: 21], universal tensor sequences (Kaski-Michalek) [cite: 3], and the direct polynomial characterization of Zariski-closed sublevel sets (Christandl et al.) [cite: 1, 7] must be weighted equal or higher.

**False Form 2: Collapsing exact border rank bounds into asymptotic rank guarantees.**
*   *Recurrence:* "Using border apolarity, we determined the border rank of the CW tensor square is 16, therefore its asymptotic rank is high." 
*   *Correction (Anti-anchor needed):* This violates the HARD-5 distinct coordinates constraint. Tensor rank is not generally multiplicative under the tensor product [cite: 7, 22]. A strict submultiplicativity result for a low power (e.g., \( \underline{R}(T_{skewcw,2}^{\boxtimes 2}) \le 42 \) despite \( \underline{R}(T_{skewcw,2})^2 = 64 \)) [cite: 23, 24] demonstrates that finite-power border rank evaluations using border apolarity do not safely linearly extrapolate to the asymptotic limit \( \tilde{R} \). Asymptotic rank requires evaluating the rate of growth \( \lim_{n \to \infty} \underline{R}(T^{\boxtimes n})^{1/n} \), which is why quantum functionals (which operate asymptotically) must be registered separately from border apolarity (which operates on finite geometries).

---

## (d) RECOMMENDATION

The anti-anchor candidate must be heavily refined prior to ingestion into the Prometheus substrate.

**(i) Evaluation of Candidate True Form:**
*   **Status:** Needs Refinement and Splitting. 
*   The raw mathematical claim \( \tilde{R}(T_{cw,2}) = 3 \implies \omega=2 \) is correct [cite: 5, 7]. However, stating it "needs border apolarity + quantum functionals" is structurally malformed. Border apolarity is deployed for finite-power border rank \( \underline{R} \); quantum functionals are deployed for asymptotic rank \( \tilde{R} \) [cite: 12, 25]. 

**(ii) Sub-Anchors and Companion Anti-Anchors Discovered:**

| Coordinate Invariant | Notation | Evaluator / Tool | Foundational Status (2024-2026) |
| :--- | :--- | :--- | :--- |
| **Border Rank** | \( \underline{R}(T) \) | Border Apolarity (Hilbert Scheme) | \( \underline{R}(T_{cw,2}^{\boxtimes 2}) = 16 \) (Maximal/Barrier) [cite: 10, 11] |
| **Asymptotic Rank** | \( \tilde{R}(T) \) | Limit of polynomials; Zariski-closed | Computable from above; Discrete limit snapping [cite: 1, 2] |
| **Asymp. Slice Rank** | \( \tilde{S}(T) \) | Quantum Functionals / Support functionals | Universal spectral points [cite: 12, 13] |
| **Irreversibility** | \( i(T) \) | \( \log_2(\tilde{R}(T)) / \log_2(\tilde{Q}(T)) \) | Establishes absolute barrier for \( \omega=2 \) via laser method [cite: 6, 14] |

*   *Companion Anti-Anchor Pin:* "Monomial Irreversibility vs. General Irreversibility." Do not collapse standard irreversibility (which uses asymptotic subrank) with monomial irreversibility (which uses monomial asymptotic subrank and applies to group-theoretic methods) [cite: 6, 14].

**(iii) Verification Queue Additions (Work-Queue Entries):**
1.  **WQ-01:** Register the explicit universal sequence \( \mathcal{U}_d \) defined by Kaski and Michałek (arXiv:2404.06427) [cite: 3, 4] as a Tier-A primitive alongside \( T_{cw,q} \).
2.  **WQ-02:** Investigate the specific polynomials defining the Zariski-closed sublevel sets of asymptotic rank introduced by Christandl et al. (arXiv:2411.15789) [cite: 1, 2]. Determine if the algorithmic evaluation of these polynomials can be mapped to a classical compute instance to definitively test \( \tilde{R}(T_{cw,2}) \le 3 \).
3.  **WQ-03:** Flag Kawabe's July 2025 preprint (arXiv:2507.13126) [cite: 16, 17] for follow-up regarding the conjectural bound \( (q+2)^m \) for \( m \ge 4 \). Tag as `CONDITIONAL/UNVERIFIED` until the proof extension is rigorously validated. 

**Final Downstream Consumer Directive:**
Execute T#3 catalog edit. Deprecate the collapsed tool-chain assumption. Instantiate distinct coordinates for \( \underline{R} \) (Border Rank) via Border Apolarity and \( \tilde{R} \) (Asymptotic Rank) via Quantum Functionals/Polynomial Characterizations. Implement the CW-tensor-specific Tier-B witness sub-type subject to the strict submultiplicativity bounds proved in CGLV22.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrk8KxocqTOpREGubzXSuLBtsu4dtTvmBra1xtJ3jts2f6Sw9v5vwb3F9AQV_Z-i0dkL8ICwT8bot-cdF9WEJ1tKd7fqK_0qJO8s71R-ov8cf0gxuS)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEi1-3-KApgddrJKm5YsBPjpILk5juy1Bi1UHqrFcXfZwRh_-GPZ2u7C-9uCVyP-y7kZDdlvvI3MV_56zGCIZr1YvcDuUn5wQy-3gj430CgSZu3q1D6T3xthLKkLDHz8vyQvmDnNRBw94cr-q7qdVu-kAbF02UF35zhGaH8ATWsxufPxaaVJJqppVPOvLfdJQO1i6AZoV-9Zp-Im5PNJQ==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZB23mbPt4P71WS2VoTUNivJaBwl8mMoWoX4eNEaNlpqI0IExusCmorArAKigS3-0WnCqZsPhD84z3AOvwUd3WIgzbHTlvdnkU6f5ncnLW1GuqSFSV)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-XVhsbWbnirkV3WdcieKLrilrSRoWIau721jvX8Rv0Kh175p8Q9WbISSxBdfgBUs6iWcMT8GSjoagHpwv3lah5w0UGGlxdnA0yd526MaaMKAZaNMC-dDL)
5. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVS-ZVX5LOCuy5chYNlzocm5VnONZb75GYusYCvbsvGSEVREaEx29uNjqHv4gkyKZAjQ7sU4jJxTicFx6och-X6TGiuzxyDOj8x0MdXRfiFelxf7l5PI_pxEM=)
6. [theoryofcomputing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzwEwID2FPRcJ-BF1wAM92VollRfc2Q1aSf1Qxq28JOHJJZSLT1jRg20Bqrh-IIr3m8BHMCIWSRaJ-eYqNbX5qn8HTlEdzORobNaOx8kK3zxH77worzCe4XjVMOKmNnoIBwCRjC555c0FLa6IkrUNyTw==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFChO598c39FkYJU1-cS-3kpX6rxO274KI6tPNUetRWfsaQkGUDWoPlXKwzG821vgQIBvFJWhuVLyjkuDmavlN_vnRnSB0dxXgT7ygIxmGvYyV7GSSu)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5WMaidyWxTXvM1Bosx-rcU651G0CjFE1rhHcvVrAFFmUX8b2VjTyF9IfbraTZD9C_iRp5l64iCK1RtUcDptn_wD-VSYVVkz8PhEuEPzLngyd2jGjb)
9. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRfoz8qlwuLYABJwMjzZYwiJmvWcTUafJYSqD1XzP3KY_j3nMIh9v9bPWfLffuZ8qLGNyoocPd75DKda3sWWi10KZOV1H7zfeOBZfZZd61ZJy_wx2dH6XUgU9CCTIMWk9cd9jzW7iDBuB2hJrNN-QADvtoPdoKazvvBFtg-GmCfyYV5ji5WWOR1wpMbpdwIQyg3EpGYxhUjNPaxvmi898WbowOHg0uJBO79RmmFaQWMa6reKE84krtnv-0V9Dj0cTW9YLH81wCyM4cXCOEit54xGmkTUU6nptrLQ==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCyyj2fzQS69HyoX6JEGBX-Ba71POBR_kVWn7qBUcqdOP_EQEEXxQJhe9gwXBZeoDawznkn-R14f0e0do2wzhAJ7tpYZADGP7MWWG8qvq9v4HcxPiQ)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh-l0QL-56wiin6-sEQcUlvf-VInE3Jum2EhhXG99qc8JiRyrAuB3F2Lgo4CCaADnacvTzahxf3jjd9c99klm4ohtdy83uOSwAQ0oE1rTFU3bh-nb5)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbdNSPFXbZCiEvlQVp1gBuSd4Ii0Uz1ZXVYjsRg9ffbA0lXfHenm53gPO5E-T8a4V7lALn_gxC6f9zbEaDrpnppoZvW0uuY-mzihuCWQ8-59jACaKI)
13. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxMOi41FLIhQ2YofcDWmQHQ9bejFwc84_VGxs6IA-49gdgv1CHfez8utv_bU9fua9tPBea44jP7rQwzFRL11skaNO3qKaIUcyysyOj1NzhFnV7NIJlvXfkKXE4Ogj0X4-HF5ZYhrlJSOGL8YCS9sLoiA6kQx1bxJzkznpE7orQ7-UzjI3hzTmqaNtbvBvHxbMIpAOFVhm7AmhOVPxGMp4=)
14. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXGeGlTmtXL2iu7QdckzxB5EcDKcVhnHanE_I0qZ0gg99yrQnXPD9rR7IwhINbHSLiEsPlrxdqOsPW6_K0oIs9ezckVCBEtVjna8mhfezHmN8mv0jki8oc6nvmJA0l7x0L47R2fDmSatyj_gNWXBHCOvfUqZ909rl4Uqbd_iaPr66MbdO1eXzY)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvJsYmGDb0y9H0IDduD3PyidkSZcpQvl5JNAVtMtBiojoFsVI8HHcyGWCwhUllUhOxGMQSPKYv_DMTytjbLIK3F-QjItjhaL6zHOazUtH29LvKVR-K)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMuo2LkyeIoVjL0YfcRT435ia9XYYSrLM0KbhZN5M6l5csjUnQYAjPOcCGcL9QpJUiDx_vydoRm6R26g0hvYR4X0epNRliat_0mcnHMyEFYh9RqtmQ)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBYAcegZyUJeOCxzSyEVwYIH1NMlm7ecSbYObOVZWtGIJEtWYgHe5C--HkD8pQdom3lO6Rv5RzZFSzf9SsAbJoIHDCqbCI7AZ8YJjMPeukkqAwWj6v)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpKxKX0VX9vhs7rhAKb2WrYQgiWcTPASnwEWsF7zIWaKvHwc0h7GNomdCxO9f841IF7bGEYKacq0Z_RLTFBxA62GfVQsppGeg4cCszM5qUkm89VDiYAht36-nYGJYxmK2L0_bohaNvLR6hYQ15vxDpVLrP2c3RT275EnjlCUyTIGE_2oOaxyMWpcTqDo5DACFleRbuK_b-zylYlVcNwc-VquPYeZOC-s6hryGX5O-NSiAwVG5BRj3pLhH4M3xIDtKpvQ==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGT6-aHNUuJJIKdc8UeraUfJoZL2c7qlpUHMMcfpA1agS1A69v9leOLRC6f3typQLlgfVDHNJBB6bU9gahsWFDbUzcz-IDKI8Pyp6JFgrb1sC1_4hAG)
20. [ieee-focs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_nTLtDsemHI2vZ78dOHyUFABc2aOcbop8hvdDhvE5DegcONdMijREiaAXBw4JlBkKWrEZfA7K0vFP32yHPg3Q9qmpcvYfFliC92vkOC74IBlo2_udzW1VvcWm0Y-uwPvYoiHZDkOHWyDKew==)
21. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHF2FoFoTwE8uX6sHHtKk6kzaP_v9u1LES5Lstb8DqFna1Gw-wTjhJJvG_HWMzCEsYURZyX29m37hrXiTkcfzgr6086rYecbS86tOE_okXB38Jq1g0pIiO-hSPEhbAh2MiNOaVrp3iDujk1jvTy1-0MShFcT1w03NdiNU_7)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFa3SZcEYRaV-T93y1Uk6-iu4NIDP6SLnV5cefu4vymSfvmpgAD8yqxAGdsv0U48sqdIf92gTdPUbRIGXaDVHXRxq_ogZzrAVe5dqbzb8ebXfEFHcTH-pP370GXOpRVJ4XO-JMK8XDow1LpSWkS3JFqn-0os15Wz0V2ZCVhLRSRHOXAK-SSUovFTJzeiG9k7nW3QP35_BjIF2Sslylpxctc0E6Ml9Ev)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxMYD_OPnpcxNYm9JSTBKvSS3M5adCNC2yZ_RAi0nx5UOTfy0oobEy2gxgeunY1BUYdGgWVj5p76LQGIjTj7No9vJhzjZfTyH7I7yx1ty8WH8cCgjetRy0Z8RgTBU6WL5zuLe4Ow-qTCplFqugTLy_71YHuqWpwxUZzNYmKc0Lmw==)
24. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEybSHfZxngC37_-_h1VbgT5n4miM02gmvlZ2Oh8xro57CaOHZjdXdOZcSqRQwaqutpNupDcf9_uduoitxdeyXxkOR8zg2_FFGs7iouxqvEZqXT9Zme43EWTrXjqlElsZFtQS6m)
25. [slmath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5aYV-Uee7hO2tcAIs2ejz3QHxIlPC9PsF-nIX_fVilD9VuwH8UXfAqbNU2vn8S29nneCh6-lr0e06Bxcv3vxoOGULee_NES45JXNIRO7jFsMdHJqQ-bLe1Fn956zdMqO55z-2Ivo8fqDehWidNZeFCroXeyR6aDUVn1LQxw27fx-oxrBBni8gddg=)

