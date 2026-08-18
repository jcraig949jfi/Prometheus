# Prompt 09: DR-041 — Survey KnotInvariantBundle Tier-F supporting lit (Burton census + Ren-Willis 2024 + Schmidhuber 2025) [Tier 1]

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdpSU1GYXNLRkF0aXZfUFVQOWNtbndRcxIXaUlNRmFzS0ZBdGl2X1BVUDljbW53UXM
**Elapsed:** 273s

---

# Tier-F (Domain-Anchor) Wave 3 Verification: KnotInvariantBundle

This report synthesizes findings regarding the verification of the Tier-F (Domain-Anchor) candidate `Survey KnotInvariantBundle Tier-F supporting lit`. It addresses the calibration of the `KnotInvariantBundle` root primitive across three primary theoretical developments: the compilation of high-crossing knot censuses, the utilization of combinatorial link homologies for detecting exotic smooth structures on 4-manifolds, and the quantum computational complexity of Khovanov homology. 

The verification reveals significant LLM gravity-well drift within the candidate prompt. The candidate collapses distinct mathematical coordinates (e.g., standard Khovanov homology versus the Khovanov-Rozansky \(\mathfrak{gl}_2\) skein lasagna module), misattributes the primary authorship of the 20-crossing knot census, and omits the strictly conditional nature of recent quantum algorithms for Khovanov homology. Furthermore, the candidate fails to separate additive approximation complexity classes from exact evaluation complexity classes. The findings lean heavily toward a necessary recalibration of the substrate inputs. While the base claims highlight verifiable mathematical milestones, their precise forms require stringent refinement to serve as effective anti-anchor pins. 

---

## (a) PRIMARY SOURCE CONFIRMATION

The candidate prompt aggregates three distinct claims. We verify each against primary, peer-reviewed, or definitive pre-print literature, distinguishing unconditional results from conditional ones.

### Coordinate 1: Prime Knot Census (1.8 Billion Knots)
**Candidate Claim:** "Burton 1.8B prime knots"
**Primary Source Verification:** 
The true form of this claim must be anchored to Morwen Thistlethwaite, with Benjamin Burton acting as the independent computational verifier. The definitive publication is Thistlethwaite's article in *Algebraic & Geometric Topology* (Volume 25, Issue 1), published in March 2025 [cite: 1]. 

*Exact Quote:* "Theorem 1.1 The number of equivalence classes of prime knots that can be projected with 20 crossings, but not with fewer crossings, is 1 847 319 428. Of these, all but 921 are hyperbolic, the remainder comprising 915 satellites of the trefoil knot, 5 satellites of the figure-eight knot and the (3,10)-torus knot." [cite: 1, 2].

*Substrate Clarification:* The candidate incorrectly anchors this to "Burton." Burton's standalone milestone was the 19-crossing census (published 2020), which enumerated exactly 352,152,252 distinct non-trivial prime knots [cite: 3, 4]. For the 20-crossing milestone, Thistlethwaite tabulated the knots in 2018, while Burton simultaneously and independently ran a verification using the software `Regina` [cite: 1, 5]. The 1.8 billion figure specifically maps to knots with *exactly* 20 crossings, not the cumulative total up to 20 crossings (which is 2,199,471,680) [cite: 6]. 

### Coordinate 2: Analysis-Free Combinatorial Proof of Exotic 4-Manifolds
**Candidate Claim:** "Ren-Willis 2024 first analysis-free combinatorial proof"
**Primary Source Verification:** 
This claim is confirmed, but requires stringent coordinate separation. The result was announced in the preprint "Khovanov homology and exotic 4-manifolds" (arXiv:2402.10452) by Qiuyu Ren and Michael Willis. Version 1 was submitted on February 16, 2024, and Version 3 was submitted on December 18, 2025 [cite: 7, 8]. 

*Exact Quote:* "We show that the Khovanov-Rozansky \(\mathfrak{gl}_2\) skein lasagna module distinguishes the exotic pair of knot traces \(X_{-1}(-5_2)\) and \(X_{-1}(P(3,-3,-8))\), an example first discovered by Akbulut. This gives the first analysis-free proof of the existence of exotic compact orientable 4-manifolds." [cite: 8].

*Substrate Clarification:* The invariant used is *not* standard Khovanov homology. It is the Khovanov-Rozansky \(\mathfrak{gl}_2\) skein lasagna module (a coordinate first defined by Morrison, Walker, and Wedrich) [cite: 8, 9]. Ren and Willis also define the distinct coordinate `Lee_skein_lasagna_module` and a lasagna generalization of the Rasmussen \(s\)-invariant, which they prove yields a lower bound on the shake genus function of 4-manifolds [cite: 8, 10]. This result successfully bypasses the conventional gauge-theoretic/Floer-theoretic gravity well (Seiberg-Witten, Donaldson, or Heegaard Floer invariants) [cite: 10, 11].

### Coordinate 3: Quantum Complexity of Khovanov Homology
**Candidate Claim:** "Schmidhuber 2025 Khovanov BQP-hard"
**Primary Source Verification:** 
This claim is confirmed but is heavily collapsed in the candidate prompt. The primary source is "A quantum algorithm for Khovanov homology" (arXiv:2501.12378) by Alexander Schmidhuber, Michele Reilly, Paolo Zanardi, Seth Lloyd, and Aaron Lauda, submitted January 21, 2025 [cite: 12]. 

*Exact Quote:* "We provide simple proofs that increasingly accurate additive approximations to the ranks of Khovanov homology are DQC1-hard, BQP-hard, and #P-hard, respectively. For the first two approximation regimes, we propose a novel quantum algorithm. Our algorithm is efficient provided the corresponding Hodge Laplacian thermalizes in polynomial time and has a sufficiently large spectral gap..." [cite: 12].

*Substrate Clarification:* 
1. **Coordinate Separation:** The BQP-hardness applies specifically to *additive approximations* of the ranks (Betti numbers) of the homology groups [cite: 12, 13]. *Exact evaluation* of these ranks is #P-hard [cite: 12, 13]. 
2. **Conditional Status:** The proposed quantum algorithm is **CONDITIONAL**. It relies on the spectral gap of the Hodge Laplacian being sufficiently large and thermalizing in polynomial time [cite: 12, 14]. The authors provide analytic and numerical evidence, but it remains a conditional quantum speedup [cite: 12, 13].

---

## (b) FOLLOW-ON WORK (2024-2026)

The 24-month window reveals critical refinements and superseding claims that must be registered to prevent the substrate from anchoring to obsolete state-vectors.

### Exotic 4-Manifolds and Khovanov Homology
The Ren-Willis (2024) breakthrough catalyzed an immediate research vector seeking to remove the dependency on the highly complex "skein lasagna module." 
*   **Nahm (October 12, 2025)**: In the preprint "Khovanov homology can distinguish exotic Mazur manifolds" (arXiv:2510.10809), Gheehyun Nahm supersedes the necessity of the lasagna module. Nahm states: "In this paper, we introduce a new, simple way of using Khovanov homology to distinguish certain exotic compact, orientable 4-manifolds; our new method does not depend on the skein lasagna module." [cite: 15]. Nahm provides an analysis-free proof for exotic Mazur manifolds using standard Khovanov homology [cite: 15]. 
*   **Manolescu (June 2025)**: In lecture notes for the VIASM-ICTP summer school ("Khovanov Homology and 4-Manifolds"), Ciprian Manolescu formalizes the pedagogical integration of the Ren-Willis lasagna module framework, validating its status as the first gauge-theory-free detection mechanism [cite: 16].
*   **Flagged Claim:** Be highly cautious of any follow-on claims stating "X proved Khovanov homology detects all exotic 4-manifolds." The current state-of-the-art only detects *certain* pairs (knot traces and Mazur manifolds) [cite: 8, 15].

### Quantum Algorithms and Knot Invariants
*   **Schuetz (January 6, 2026)**: In a purely classical follow-on, Dirk Schuetz demonstrates in "Efficient calculations of s-invariants for links" that the integral Khovanov homology at homological gradings near the minimum and maximum degrees for closed braids can be obtained in *polynomial time* [cite: 17]. This establishes a localized classical efficiency boundary against which Schmidhuber's conditional quantum algorithm must be measured.
*   **Schmidhuber et al. / Gyurik et al. (October 2024)**: Preceding the 2025 Khovanov paper, the substrate literature shows intense focus on quantum Topological Data Analysis (TDA). "Quantum computing and persistence in topological data analysis" (arXiv:2410.21258) maps the complexity-theoretic limits of Betti number estimation, forming the foundational architecture Schmidhuber subsequently applied to the Khovanov chain complex [cite: 18, 19].

---

## (c) FALSE-FORM RECURRENCE

A search of the 2024-2026 literature and general LLM outputs reveals strong gravitational wells asserting false or collapsed forms of the candidate claims. If these are not explicitly pinned as anti-anchors, the substrate will regress to false coordinates.

**False Form 1: The "Burton 1.8B" Attribution Collapse**
*Recurrence:* General mathematical summaries frequently attribute the 20-crossing census solely to Benjamin Burton due to the prominence of his `Regina` software suite and his undisputed sole authorship of the 19-crossing census (2020) [cite: 3, 4]. 
*Evidence of Need:* Mathematical databases and LLM generations increasingly state "Burton's 1.8 billion knots." The anti-anchor is strictly needed to enforce the coordinate `Thistlethwaite_20_crossing_census_1847319428`, with Burton's role mapped as `independent_computational_verification` [cite: 1, 5].

**False Form 2: The Quantum BQP-Completeness Generalization**
*Recurrence:* The literature exhibits a strong gravity well toward equating the complexity of the Jones polynomial (which admits an unconditional BQP-complete additive approximation via the Aharonov-Jones-Landau algorithm) [cite: 20, 21] with its categorification, Khovanov homology. 
*Evidence of Need:* Statements such as "Schmidhuber proved Khovanov homology is BQP-complete" or "Schmidhuber gave an efficient quantum algorithm for Khovanov homology" drop the critical modifiers. The anti-anchor must enforce that exact calculation is #P-hard [cite: 12], and the proposed efficient algorithm is **CONDITIONAL** upon the Hodge Laplacian thermalization and spectral gap bounds [cite: 12, 14]. 

**False Form 3: Collapsing Skein Lasagna into Standard Khovanov**
*Recurrence:* The distinction between `Khovanov_homology` and the `Khovanov_Rozansky_gl2_skein_lasagna_module` is routinely collapsed.
*Evidence of Need:* Ren and Willis specifically utilized the skein lasagna module (a 4-manifold invariant derived from link homology) [cite: 8]. Until Nahm (Oct 2025) [cite: 15], standard Khovanov homology was insufficient for analysis-free detection of exotic 4-manifolds. The anti-anchor must aggressively enforce the distinction between 3-manifold/knot invariants and 4-manifold lasagna modules [cite: 8, 9].

---

## (d) RECOMMENDATION

The candidate prompt requires immediate and significant refinement before it can be integrated as a substrate input. 

**(i) Anti-Anchor Refinement State**
The candidate's true form is **needs refinement**. 
*   **Modify "Burton census"** to `Thistlethwaite-Burton_20-crossing_census` (distinguishing the 1,847,319,428 exactly-20-crossing primes from the 352,152,252 up-to-19-crossing primes) [cite: 1].
*   **Modify "Ren-Willis 2024"** to explicitly specify `Khovanov-Rozansky_gl2_skein_lasagna_module` as the coordinate for the first analysis-free proof, differentiating it from standard Khovanov homology [cite: 8].
*   **Modify "Schmidhuber 2025"** to explicitly tag the algorithmic efficiency as `CONDITIONAL_BQP` (dependent on spectral gap) and distinct from the unconditional `#P-hard` exact evaluation [cite: 12].

**(ii) Discovered Sub-Anchors / Companion Anti-Anchors**
*   **Sub-Anchor 1:** `Nahm_2025_Mazur_Manifolds` (arXiv:2510.10809). This serves as a vital companion to Ren-Willis 2024, demonstrating that standard Khovanov homology—without the skein lasagna module—can detect certain exotic contractible 4-manifolds [cite: 15]. 
*   **Sub-Anchor 2:** `Schuetz_2026_Polynomial_Braid_Boundaries`. Companion anchor to Schmidhuber 2025, establishing that classical algorithms can efficiently extract Khovanov homology at extreme homological degrees for braids, narrowing the regime where quantum speedup is practically necessary [cite: 17].

**(iii) Verification Queue Additions**
Inject the following actions into the downstream consumer work-queue:

```yaml
substrate_inputs:
  - action: catalog_edit
    target: KnotInvariantBundle
    delta: |
      Register distinct coordinates:
      - Khovanov_homology_exact (#P-hard)
      - Khovanov_homology_additive_approx (BQP-hard, CONDITIONAL algorithm)
      - Khovanov_Rozansky_gl2_skein_lasagna_module (Ren-Willis 2024)
      - Lee_skein_lasagna_module (Ren-Willis 2024)
      - lasagna_s_invariant (Ren-Willis 2024)
      
  - action: anti_anchor_pin
    target: Tier-F_Introduction
    delta: |
      Resist attribution of the 1.84B 20-crossing knot census solely to Burton.
      Enforce Thistlethwaite primary authorship (AGT, March 2025) with Burton as independent verifier.
      Never conflate the 19-crossing 352M count (Burton 2020) with the 20-crossing 1.84B count.

  - action: work_queue_entry
    target: Wave_4_Calibration
    task: "Verify Nahm 2025 (arXiv:2510.10809) methodology for detecting exotic Mazur manifolds using standard Khovanov homology."
```

**Sources:**
1. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_fWbpQTUAqJhyVK238u4ZEbtNANFZPmVmX0oS7vQo5KZ3Xni7adwSQPHf73ACGg-n8D-flP1v2Ht5VS0qYrDeVhbSiKEbQGz6ylw8_W47Ln-p1dD8LloYaK6WT1DU6CYKOdH3t9kLwg==)
2. [utk.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvmnCLiMPQCaI24ZFvTGVXRQMO18wtn2yUQemE-EBDdNBzJnsaRXSjfTcQ8CqHcpzSUOhhmqtDHDOhxXLO6YJv1WbgP50ymvw_cNmXhE38y_3FxfkBBNrKSLBfloLJ3a8=)
3. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECAKxbdvLwOvMdvhOdKkWFaXXfx7ytQ3EYP96WvW7xMdbAqE27UC6rEz0drk7dkmyIawJdXy2TwE6Po-AjcYv43BlsSwbMHkjr9xjfAnLzaLYmHBtfC1bHQSniI17MaDe55Qehe3-hrf-yLGSwm7cZ10Gpf9XTZMCxYTXuD1NbQppQ0B7O4urURs5RoL4JLKlfOPnqj-GONB8LMqyEjTe5S203)
4. [international-maths-challenge.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRP_Y5cuhyk0KhQKF-Y9uAkgslSjFY5Zf9SAfohkNtkURrLZ1mxzJ6Ch7ivguGeEuxX2JiXdez2SA5UREbpGOeI44RXaFeQnYmsSXVYyRvQDL7U4szhsosfUMGHSxGFuZIWWHT7eHOhXYtqJ2FiCCE2esdlVMW-A8pYIp3CFmvfndd4v-2urjDF3Saevr5pb6YCh5yb1uex1GrQvQP_yTrA_oKVQ==)
5. [utk.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcQtPlNziamy53HqH4M5-YAEKMUkGEOVSKwk6_1nyYvA_PxJEhxnPzJeR_yyY0TB8rC9tpHlXtVEdf7z4cUZxNmw9dzDvsJeQFfK89b12hg31y_LS_LsCuymMIgEkqOLQ=)
6. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkPMqw1DThEx1Mi8vESorPUtAINjev0gokoq-X1DhtfELXLioA5Giv0uKooLGJyBzXIauLi_ijlt_-GNndQB1S29UDadxOmwmW2yfm9pT33C2jKS_BpB0j5I-m32tc6fZhSms5BMF2Av2DxQH6HN7OWWH8GNib)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqKyU2-31VOn5HapvRTvEwfF9jWoePxklwn590wbI_xutxLMM0oYGp8-sqBYtVsRbX1FO3vcWHXepKofksFG1xGpf4lx5Z_kXpC-FRVwdVYHlxPlPrHg==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRy1dwHr0DpYC4w02uaCW_eALP4ftPGx11cnpqbnUwm5Qjt9bFzECWtlLfmCTT7OQkP7Dnjjgs0P6pQv_4l2Sa3-niTnuykA3RTGxCix7yEEM3vfLNhSJJ-w==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCY4Jv8BG4tFJo99PVTOLLfwYp05-9fGJJ4Fcq7K1Dry7pkYaMmmq80RbmfI9vyqTfPdn73meKdKwNs6mX_Gt1zpMJujWEy4Z0vi8xsZ1oI8ISA2vEBw==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8TUN968pObtM4fx3lhb_LHYiRpngLr0cxP5IHsCTOF5_43cmNvvv8IQBS6_aCTquhyVHRjTtmXkJRnkDo9UPprI2K5K-HfAKPlIS-dkToNCEp3R40SyrbNw==)
11. [renyi.hu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFadbvxGGOhDrjDqG1t7H9Qi3d3JXPS4BoPKlUJrx-JGES354e6B1Y8TimHW-fPjcQm0gpfz6NKBtpjUO4sAWVnqDMO_R7mLPeLGP68H_CmCANWysNwBd3ix698rMAgQAIMroScx_v76NNwRVSqePiVVAGkfqvynzmGF7uiNBN325EvkUL7PTyE7oQJZ67VDzxk)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUfyTz-hJ2xgdQ4TlMxwsOJ9Ge8OzkZHL231kGhlKG8qid7tg6EQrHfOrChVBNi1g5y0yNcnFUoFIawmErLQpd2EiHMFYazbpmzF6OJzD681AK1cTZsA==)
13. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVGTirPtMDfyyFJgsN3ec0W_bvGQ9ngv6A3bd-fQXQeBfUaFGXK8pdEnaHe24xdIMOefYI1G38SKsTnLv3ZnXBX6eJYKLnpK5d_0MGHVpHk3FPeCbGWg8U8GxEPP3J112ruKgxXsL11aCIuU_QcNfOyA4y2bA_PA==)
14. [ictp.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESsKOYBZdiT6AqOHGEMKVbnjeoRYHA8WIsvEHxsEJLp6qiXB3uFoXJLAibR7sccCnSTx34mHcxkPioyvdklpyaf43AS6j0BaR6I5nFExq5d6m6kbkI7WApWaAF6JBiFObORoNtLV-2pQ92RINhzJUeUkZ4HTFYFQI_nTNo02Hpn9XpKak=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfiSJkiblN4NhfyvPf_gpiWs244h3t2hJZZ1Pqf-cNnDcN-XAf_8ha-TOdkMifLmjVd3u_RCTfo95nql6mQTmTiG5ww6sLX04s3mQcl8gBiLG9elzGeA==)
16. [viasm.edu.vn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3tRXKYeTvAv2n2plqrmgZCNulFcCir3xNpGeEK1K007IuiQ_Y3QxPQLdXrM2NfO-miXhgtd4o717FhE6zEExmPilmkX90-SzpyiPmoYkJ3Z3prTLBmN5W-fRW9zPof-QCPSztDD99-okB5Vs8Gg7kRTfiJydUDYcFBAHcqK8yB2GAM8mgWbe8lb6JeuCQL-YE_aXDjYZAY8_GMuU=)
17. [dur.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzsEm_BbeqEYmulGidPCk2jyB3ZB0bNSOTNEq2hIwiN-ige3-AR2nuRK8mX9vJ8rSgwCI2Fnx1-Z9YH7tItWCrrBNkwK68KTAuzVXPn3vitZy3vh8U-waEi3VBTy7mrLg7mzr05REqmw==)
18. [quantum-journal.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0LaNAq36jJicF2vp3KuSrUd7IDC2NHwAOfOTkggWfQgoALzhxxeR6SyePwyBNtgetMQsxyITuQW9oCnVCDWJ1rE7LD8_O-I4_O_RaNE7UplZApVVFVbvnV6cuj1R3QRZnW5koWdSCQuRTyg==)
19. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnVzv98aVdAJevZHh6bVW7bgE97xoNm2qDYWCTTS-LE-PfEhKXo49a-PxN1RE-T7GI9kTQIlH148Rbnyx3vkwzRiPI3lAWePHvRGTQT8W9phr9iM0fymkZuYsNWWG_cA==)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGekY29QbmDjtc9Vlc4fLih5hb43bzf5mLLYQ2ANAHaDIoAa4q-FGRX0yxUooLQWIjtdg-9RzMvhiodYlSrr-kDBrItHqzm0_kvQtqtv7pnIW7DfREReBsCipJGyi6vLb63gYvma-XMCvBiAYk3D6Q6fwXQjyJ5UaMC61gK94hxi6-hvv-Q3cSbYvugqbPkdYTNwuPKBGVkadpZ_La3)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE60Zlr9CAStH7aPGxpZdvXyoNdvleHzgkVch9RUgm3BW9R64JKPAfcPeNJ0UVkP4LF4MI18QDiMUmkCqVZYKtFdbvvmmdC4N4AErNH5w4AbEG5NsTEeOhGag==)

