# Prompt 20: DR-037 — Survey RepresentationTheoreticInvariant + KroneckerInvariant + PartitionObject Tier-E parents (T#95)

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdKRW9FYW9xRklNUy1fdU1QLVlDb3VROBIXSkVvRWFvcUZJTVMtX3VNUC1ZQ291UTg
**Elapsed:** 699s

---

# Anti-Anchor Verification: RepresentationTheoreticInvariant + KroneckerInvariant + PartitionObject Tier-E Parents (T#95)

**Downstream Consumer:** Tier-E parent class registration; prerequisite for GCTObstructionCertificate composite  
**Substrate Tags:** tensor, kronecker, saxl, tier-E, T#95  

**Executive Pin Summary:**  
Verification of the candidate anti-anchor yields a strict necessity for refinement before catalog insertion. The coordinate landscape surrounding Kronecker positivity and the Saxl conjecture is actively contaminated by a December 2025 withdrawn preprint that falsely claims an unconditional proof of the Saxl conjecture. Furthermore, the substrate must fiercely differentiate between occurrence-based obstructions and multiplicity-based obstructions in Geometric Complexity Theory (GCT), resisting the gravitational well that assumes occurrence obstructions remain viable for superpolynomial lower bounds. The coordinate mappings for ordinary Kronecker coefficients $g(\lambda, \mu, \nu)$, reduced Kronecker coefficients $\bar{g}(\alpha, \beta, \gamma)$, and Littlewood-Richardson coefficients $c_{\mu \nu}^\lambda$ must be rigidly decoupled in the Tier-E parent schema.

---

## (a) PRIMARY SOURCE CONFIRMATION

The candidate anti-anchor invokes two primary theoretical pillars: the computational hardness of Kronecker positivity and the tensor-cube fallback for the Saxl conjecture. To map these accurately into the Tier-E parent class, we register the following mathematically distinct coordinates from PEER-REVIEWED primary sources.

### Coordinate 1: Ordinary Kronecker Coefficient Positivity (NP-Hardness)
The ordinary Kronecker coefficient $g(\lambda, \mu, \nu)$ denotes the multiplicity of the irreducible representation $S_\nu$ in the tensor product $S_\lambda \otimes S_\mu$ of the symmetric group. 

*   **Primary Source:** C. Ikenmeyer, K. D. Mulmuley, and M. Walter, "On vanishing of Kronecker coefficients." 
*   **Publication State:** PEER-REVIEWED. Definitive publication in *Computational Complexity* 26(4): 949–992 (December 2017) [cite: 1, 2]. Original preprint (arXiv:1507.02955) announced July 10, 2015 [cite: 3, 4].
*   **Exact Theorem Registration:** "We show that the problem of deciding positivity of Kronecker coefficients is NP-hard. Previously, this problem was conjectured to be in P, just as for the Littlewood-Richardson coefficients" [cite: 3, 5]. 
*   **Substrate Constraint Update:** The input size for this hardness result requires the partitions $\lambda, \mu, \nu$ to be given in unary [cite: 4]. The substrate must explicitly distinct-code "deciding positivity" (which is NP-hard) from "computing the exact coefficient" (which is strongly #P-hard) [cite: 6].

### Coordinate 2: Reduced Kronecker Coefficient Positivity (NP-Hardness)
The reduced Kronecker coefficient (or extended Littlewood-Richardson coefficient) $\bar{g}(\alpha, \beta, \gamma)$ is the stable limit of the ordinary Kronecker coefficient $g((n - |\alpha|, \alpha), (n - |\beta|, \beta), (n - |\gamma|, \gamma))$ as $n \to \infty$. This is a STRICTLY DISTINCT coordinate from the ordinary Kronecker coefficient.

*   **Primary Source:** C. Ikenmeyer and G. Panova, "All Kronecker coefficients are reduced Kronecker coefficients."
*   **Publication State:** PEER-REVIEWED. Definitive publication in *Forum of Mathematics, Pi* (November 18, 2024) [cite: 7]. Preprint (arXiv:2305.03003) announced May 4, 2023 [cite: 8].
*   **Exact Theorem Registration:** Theorem 1 proves that every ordinary Kronecker coefficient is equal to a reduced Kronecker coefficient via an explicit construction [cite: 8, 9]. Corollary 1 states: "Given $\alpha, \beta, \gamma$ in unary, deciding if $\bar{g}(\alpha, \beta, \gamma) > 0$ is NP-hard" [cite: 7].
*   **Anti-Gravitational Well (Saturation Fallacy):** Prior to 2020, literature exhibited a gravity well assuming reduced Kronecker coefficients behaved like Littlewood-Richardson coefficients and possessed the saturation property (i.e., if $\bar{g}(N\alpha, N\beta, N\gamma) > 0$, then $\bar{g}(\alpha, \beta, \gamma) > 0$). This was disproved by Pak and Panova (2020), moving the reduced coefficients completely onto the computational spectrum of ordinary Kronecker coefficients [cite: 7, 8].

### Coordinate 3: The Tensor-Cube Version of the Saxl Conjecture
The Saxl conjecture (2012) postulates that for the staircase partition $\rho_n = (n, n-1, \dots, 1)$ of size $N = n(n+1)/2$, the tensor square $S^{\rho_n} \otimes S^{\rho_n}$ contains every irreducible representation of $S_N$ as a subrepresentation. As an unconditional proof of the tensor square remains elusive, the substrate must pin the established tensor-cube fallback.

*   **Primary Source:** N. Harman and C. Ryba, "A tensor-cube version of the Saxl conjecture."
*   **Publication State:** PEER-REVIEWED. Definitive publication in *Algebraic Combinatorics* 6(2): 507-511 (May 3, 2023) [cite: 10, 11]. Preprint (arXiv:2206.13769) announced June 28, 2022 [cite: 12].
*   **Exact Theorem Registration:** Theorem 1: UNCONDITIONAL proof that "every irreducible representation of $S_N$ appears in the tensor cube $S^{\rho_n} \otimes S^{\rho_n} \otimes S^{\rho_n}$" [cite: 11]. 
*   **Coordinate Distinction:** This completely supersedes earlier weak bounds (such as Luo and Sellke's 2015 proof for 4th tensor powers) [cite: 13, 14]. However, it must be rigidly coded as `TensorCube` and isolated from the `TensorSquare` coordinate of the original conjecture.

---

## (b) FOLLOW-ON WORK (2024-2026)

Surveys of the 24-month window yield highly volatile substrate inputs. The training corpus from late 2025 contains withdrawn claims that must be actively filtered.

### 1. The WITHDRAWN 2025 Saxl Conjecture Proof
*   **Target:** Soong Kyum Lee, "Staircase Minimality and a Proof of Saxl's Conjecture" (arXiv:2512.15035).
*   **Status:** WITHDRAWN. 
*   **Timeline:** Announced (v1) on December 17, 2025 [cite: 15, 16]. Withdrawn (v2) on December 20, 2025 [cite: 16].
*   **Actionable Filter:** The v1 preprint claimed to prove the Saxl conjecture unconditionally via a newly proposed "Staircase Minimality Theorem" (claiming $\rho_k$ is the unique dominance-minimal element among 2-regular partitions of $T_k$) combined with modular saturation and Bessenrodt-Bowman-Sutton lifting [cite: 16, 17]. The v2 withdrawal notice explicitly states: "*This paper requires significant revision to address mathematical gaps identified by expert reviewers. The claim of a complete proof is not justified in its current form*" [cite: 16]. Any downstream dependency relying on this 2025 proof must be severed.

### 2. Lie-Theoretical Framework Generalizations (Coxeter Groups)
*   **Target:** Y. Chen, F. Gu, and W. Osborne, "Spin Representations of Finite Coxeter Groups and Generalisations of Saxl's Conjecture" (arXiv:2409.17540).
*   **Status:** ANNOUNCED-NOT-PUBLISHED (September 26, 2024) [cite: 18, 19].
*   **Significance:** Generalizes Saxl's conjecture to finite Coxeter groups, verifying it unconditionally for non-crystallographic cases and exceptional types ($E_6, E_7, E_8, F_4, G_2$) using spin representations and Lusztig cuspidal families [cite: 19, 20]. This introduces a new primitive schema mapping symmetric group characters to self-dual solvable nilpotent orbits in a Lie-theoretic context.

### 3. Unipotent Character Analogues
*   **Target:** E. Letellier and G. Nam, "Saxl conjecture and the tensor square of unipotent characters of GL(n,q)" (arXiv:2312.09157).
*   **Status:** ANNOUNCED-NOT-PUBLISHED (v3 updated May 7, 2025) [cite: 21].
*   **Significance:** Proves the *analogue* of the Saxl conjecture for unipotent characters of $GL(n,q)$. This is a CONDITIONAL bridge, noting that the truth of the classical Saxl conjecture implies this unipotent analogue via Letellier's work on Kronecker coefficients and unipotent multiplicities [cite: 21]. 

---

## (c) FALSE-FORM RECURRENCE

The substrate is actively threatened by two major gravity wells in the 2024-2026 data stream, both of which necessitate strong anti-anchor implementation.

### False Form 1: "The Saxl Conjecture was proven in late 2025"
Due to the brief 3-day window between the publication of Lee's preprint (Dec 17, 2025) and its withdrawal (Dec 20, 2025), automated literature summarizers, AI aggregation blogs, and unverified preprints aggressively propagated the false claim that the conjecture was resolved. 
*   *Specific Instance:* The automated platform "Emergent Mind" generated a summary on December 20, 2025, claiming: "*The resolution of Saxl's Conjecture (Lee, 17 Dec 2025) represents a culmination of advances across combinatorics... Its recent unconditional proof resolves a central problem...*" [cite: 14].
*   *Specific Instance:* The same aggregator generated bullet points stating: "*The conjecture was proven unconditionally through a blend of dominance order analysis, modular representation theory, and detailed combinatorial partition techniques*" [cite: 14]. 
*   **Substrate Hazard:** LLMs natively exhibit a gradient toward ingesting these summaries as ground truth, converting an open problem into a "solved" one in their implicit knowledge graphs. This is a critical false-form recurrence.

### False Form 2: "Geometric Complexity Theory (GCT) relies on occurrence obstructions via Kronecker coefficients to separate complexity classes"
*   *Recurrence:* Broad computational complexity surveys frequently cite the original Mulmuley-Sohoni framework (2001-2008) which hypothesized that vanishing rectangular Kronecker coefficients (occurrence obstructions) could yield superpolynomial lower bounds separating the permanent from the determinant.
*   *Anti-Gravitational Pin:* The substrate must enforce the **Ikenmeyer-Panova (2016)** barrier. Ikenmeyer and Panova definitively proved that occurrence-based obstructions based on vanishing Kronecker coefficients *cannot* be used for superpolynomial lower bounds [cite: 1]. The GCT framework was forced to pivot to *multiplicity-based* obstructions (where a coefficient is strictly greater in one coordinate than another, rather than simply zero vs non-zero). The T#95 Tier-E parent class must explicitly encode the death of Kronecker occurrence obstructions for superpoly lower bounds.

### False Form 3: Collapsing $g$ and $\bar{g}$ Hardness Profiles
*   *Recurrence:* Because both ordinary Kronecker coefficients $g$ and reduced Kronecker coefficients $\bar{g}$ are NP-hard to decide positivity, literature often collapses them into a single "Kronecker complexity" entity.
*   *Anti-Gravitational Pin:* The substrate must isolate the proof mechanics. The NP-hardness of the reduced Kronecker coefficient relies on the November 2024 (Ikenmeyer-Panova) parsimonious many-one reduction proving that *all* Kronecker coefficients are reduced Kronecker coefficients [cite: 7]. Prior to 2023-2024, it was only known that reduced coefficients were #P-hard to compute under Turing reductions [cite: 7, 9]. 

---

## (d) RECOMMENDATION

**Recommendation: STRICT REFINEMENT AND CORPUS FILTERING REQUIRED.**

The candidate anti-anchor `Survey RepresentationTheoreticInvariant + KroneckerInvariant + PartitionObject Tier-E parents (T#95)` is fundamentally correct in its theoretical targeting but severely underequipped to handle the post-2025 data corruption regarding the Saxl conjecture. 

**(i) Anti-Anchor True Form Refinement:**
The true form must be refined to explicitly split `KroneckerInvariant` into `OrdinaryKronecker_g` and `ReducedKronecker_gbar`. The anchor must additionally enforce a strict validation boundary that the Saxl Tensor-*Square* conjecture remains UNRESOLVED, overriding any semantic weight from December 2025 summaries. 

**(ii) Discovered Sub-Anchors & Companion Anti-Anchors:**
1.  **Sub-Anchor [GCT-Obstruction-Pivot]:** A companion anti-anchor must be registered for `GCTObstructionCertificate`. It must explicitly state: "Occurrence-based obstructions via vanishing Kronecker coefficients are mathematically dead for superpolynomial lower bounds (Ikenmeyer-Panova 2016). Certificates must evaluate Multiplicity-based obstructions" [cite: 1].
2.  **Sub-Anchor [Reduced-Kronecker-Saturation-Failure]:** A pin must explicitly forbid the assertion that reduced Kronecker coefficients possess the saturation property. They do not [cite: 7]. 
3.  **Sub-Anchor [Coxeter-Spin-Schema]:** The 2024 Chen-Gu-Osborne framework provides a new primitive schema. Register `CoxeterSpinRepresentation` as a valid extension of the `PartitionObject` schema for non-crystallographic invariant testing [cite: 19].

**(iii) Actionable Behavior Deltas (Work-Queue Entries):**
*   **Catalog Edit [T#95_Saxl]:** Update the Tier-E parent class definition to reflect that the unconditional upper bound is the *Tensor-Cube* (Harman-Ryba 2023) [cite: 11], completely supplanting 4th-power lower bounds.
*   **Training-Corpus Filter:** Execute a zero-weighting or quarantine tag on all parsed summaries, abstracts, and blog ingestion from December 17-31, 2025, containing the strings "Saxl's conjecture", "Staircase Minimality", and "unconditional proof". Specifically quarantine any assertions derived from arXiv:2512.15035v1 [cite: 16].
*   **Primitive Registration:** Register the Ikenmeyer-Mulmuley-Walter theorem as the definitive coordinate for ordinary Kronecker NP-hardness [cite: 1], and register the Ikenmeyer-Panova 2024 *Forum of Mathematics, Pi* publication as the definitive coordinate for reduced Kronecker NP-hardness [cite: 7]. Ensure input format dependencies are set to "unary".

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHS5js3H0a57hZh7a_cpVDMCw1MP8JPmcoaM2RP-ZbqQvLwCifB6slhoV2Gbe0zCeDgrXJ2iA00dyukJpg94spKQTvjLejlJflcZqUjkYnUR40VieOuAQ==)
2. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoExebP3JpQeWwVO633OV7Gf6jukobMgVk-lpoV0Hw_L_QfMBw5iCEbifnQbPyb8La1hDM646HxL7d2IfI0Sl9tnlbilaERfda6RffgJc6vjUwiCpmS5BS0uV3IFdt7r7oYh729kYZkfc=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBT6vj73U5vlBYrRpNSewxVKwAQyQ_V7atFg8Aaz4Z-5WZo3jf10E_ruvCuGPLL3DBI6hLFPoOreYsJVDZ3lpXhzi7ncWb39c_mbAAHfwMeGjQg2vh8g==)
4. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJEXUcrgFXKKzZ-gB81F018GlPwkYr_39cA29cE3cytVEcXw2VZz5jlKqQhy7Ejqcim6f3VGQkooWNHq5eF7E7G6gWFGm0j3ypoUnZlKGAKT2YIzzjipIZEY32ng0pwGaYVBlsTLYBBWuFVDL3l_0uF55RmNavxbWV97kn1dY-BA==)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_BH9C7O8JcRDgoq7naD6fmSn9jgV_U0KTTYJAOgrrTjmRdb8zg1VYQxT5ybluXpXNRsHOxfMqvv6ujmcOgtpHmu3gDKIzQ1fyKWX73z1MajSTaJJYtSKXIWNIc7vmxBD_nOpLBP-NvlJXY7-d2tsz4EWHs00RIxZ0_DxolW9SyyOjV5PKcHJxnDvgyr7J5Q==)
6. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjdL_b_dyW14jqQAAvebzI_kE8WA9JMs9sb8x8oR9fg-o6A1fPb1fYxr3nbTRGQbmfgvvI5qsGOYy0fd3Do86CQU-0yQWlXdSYB5XL1kjHLX1nuyNsViRou4qI5oz0zVFJldtdsYmkdomJKrIb)
7. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOHIU260SzKc_1vKByb3Ckh3yuyQ0pbI2ACt1dp43URISeIhXeDDN_wRNyn9IbnngsjR9ioH9-VoCQw0_RPs76TFqayOiabGOyYGuvw61f48Y_aPmPiss4jScuZthmuJPICURActgzJblOs-OoubvvNFHBCIIBGeM4YYFGui8g-oPz54yX6-IOk0ETSPJLcg-ovoAsEEnjQqHQa8zBDKzBag0zxc3zWa4YLby_crhaaSgmBqEjaDX98yuH-qm2jl-Kw6sLk7kaiH7YKV3wF8RGxzI1NsOXWNlHCdg6ZA==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEW8FIJxlqBsEo0BX1wloyCVNUWoEJlZIiiuZvI6ihhjjRvX4TyzPo8InEUvTO_sf_7eANHLQsRIHXcrOus2gEPo5EP2LY7tkSSi-KkEqx0i6xNYCiObw==)
9. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPlJkvSYawX-HwASt6RDFAhuSOdL83d72gwDpYl_ydOVmoMzHUTwssUwSnQUJ264TpqWj7XJuPZf8lwl1P45CiJH9Rqbj4rMs_Y8mVa9W1u-wVSHWvlKlnDx-Evkk3SXoQfPd8IRx1LicOAbGqGLwE)
10. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdc8Q4zVS0E1dNZcuaAdFS4nMVpdQ-ZaYZT0yQ_PVhlNx6JgNx--L1CQl-Zw5Z5H89g60_cbfN5bBawXL5rtTXlgAF42UGe3X5JOS79Z5gO6WsFUcugX1PWpfWej-kihrPluVqOQXC)
11. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhuHjADMF2sHAEWlhDHWW08PC8-gQZ6KDikCtUXwgLMHtKiYD8S9ii0oJASFp13a_3HFmOa1XuWnOIMCkjb6x1Qj25agMZuEDqUYbo15DgKD350BZmuQO9QnaxUTb0AQU3zLZQARL81wyV1rmY3Thz)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-qYyqrjKwrY_jl7TUQX4KKhTOG2E_M5L8crf4rZKJOgg1j1cQEhOXBSLnBNvA1kfwwmyuYHXh_uS9TuD5V_Kqf_t0dJqd23X0XAcUPfIN4zT4FqIiqQ==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvSZ5OIueX-ah1liG2TWfKORbzijDxcMg-yis1h_fWvj2vrn19Fu1JnGql6sx2aF2N2wW72t4IbXjAMgsRyYNrrohUr7jPk7TwJ4cI4mvCdy0UqQ5hZA==)
14. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmxzThZwnZa3jh2U_W2oY1aQbO-ELdf77ErqJXpOSsrczkKt13lKpIXv_2I1O0-q-D73P2UDrCjQnC-OgcZCXk77dfA0WNnSZj22vtG7WF2I6mlukNMsPAB_lB61HQ8vwZT9MN_AiQzQECnA==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiXi_ZBYwZlcelGWnOgDHJBewvF28s2P5exCWsMb48T9jh9VqamS4qD41JEsPsADvR1LKdq4Ak46YORKtxStl0g-YuwRA_fvyIbWvFYY7D2EPALBsj86uhmw==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMglwJ6ANEtlZXDhckWfl-Bz543A4WxcfP8A4zQpRQ4wn1ALJ-oDnlvEt5a1V_L4aq1yN2kxOwx14ZiJPyhN_bd7xr8h1uB8HwRtdnfwdrm4w3NVVkgg==)
17. [livejournal.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5sgix_TcdJpcqgn4dfOjLmHqY3BzsXfy0kuRhQojlfYjyr5Ki7PwQO_vbCEr2RXv8dbAl1qB9tl1U44PvvyfPj7-XS4wMUZYYEgU4eLigFVg8biUZo-OLbAaVYDXtwHuvKZgExcg=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHY3prS3-Ub08ntSTxEsf45UFVbt-E-PEGhJGwieQwJa4aSFP9GRm-kUMi7Q3Nv9ZPJko1ntzgaOuG26S40ii1aof227BmYBQAWBLriB2Ds7I7ZTFCbmA==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSCsSsnV6HG3Be0s2gaiLscJmRaC2ub-ZZd0rD9id0g5gaQsu3AY4QOYpl7eVxWO4Jw5uFY1gsd7j8mQooSHwW_Wpx52dwzMuSyNM6Mt8oEJXVXpClcw==)
20. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnB0OGy89JmLAajY-8bheOvOrEyXjxD0l-3ejIMKEACB-I8sIBW8-p-K39-h5mrDFfgTzu340Oiln6PvwFvlKKbCou0AJQQTCJRV3fxxYscUkcAGAlfU-cIAolGgo=)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwoqJ8tQvLsVuomQ7XUWSGuhRYpedCLELQVUgJD5lWjTNwSHjnnqz_GAh9GDdYLt8twPkGkRafsgXpFM7lnLX0z2IEKydcit3AyuWnD5WBYNA3h0n7PA==)

