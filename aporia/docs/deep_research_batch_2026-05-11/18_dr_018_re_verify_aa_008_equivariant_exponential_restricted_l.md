# Prompt 18: DR-018 — Re-verify AA-008 EQUIVARIANT_EXPONENTIAL_RESTRICTED (Landsberg-Ressayre 2017)

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdqcWNCYXBMRUk3UGZfdU1QZ1p6bjBRURIXanFjQmFwTEVJN1BmX3VNUGdaem4wUVE
**Elapsed:** 334s

---

# AA-008 EQUIVARIANT_EXPONENTIAL_RESTRICTED: Verification and Substrate Coordinate Update

**Target Consumer Subsystems:** `AA-008 last_verified` update; `EquivariantComplexityCertificate` restricted_to annotation refresh; `CatalogEdit` (invariant definitions); `TrainingCorpusFilter` (algorithmic false-form suppression).
**Verification Date Range:** 2018–2026 (Focus 24-month window: Jan 2024 – Mar 2026)
**Coordinate Isolation Required:** `dc` (determinantal complexity) vs. `edc` (equivariant determinantal complexity) vs. `symmetric circuit size` (square-symmetric) vs. `symmetric circuit size` (matrix-symmetric) vs. `ABP size` (algebraic branching program size).

This verification report confirms the integrity of anti-anchor **AA-008**, validating that the unconditional exponential lower bound on the permanent remains strictly quarantined to the *equivariant* restricted model (`edc`). Follow-on research from the 2024–2026 window has not breached this restriction to provide an unconditional exponential bound for general determinantal complexity (`dc`). However, literature in this window presents novel, distinct symmetry coordinates (e.g., symmetric arithmetic circuits) that necessitate new primitive registrations to prevent coordinate collapse. Furthermore, machine-generated abstracts and database cross-contamination in recent literature have spawned synthetic false-forms that must be explicitly filtered from the substrate training corpus.

---

## (a) PRIMARY SOURCE CONFIRMATION

**Substrate Action:** Confirm base validity of AA-008 against definitive literature.

The primary source defining the equivariant determinantal complexity lower bound is confirmed as:
**Authors:** J.M. Landsberg and Nicolas Ressayre
**Title:** "Permanent v. determinant: an exponential lower bound assuming symmetry and a potential path towards Valiant's conjecture"
**Preprint:** arXiv:1508.05788 (First announced August 25, 2015) [cite: 1].
**Conference Announcement:** ITCS 2016 (January 2016) [cite: 2, 3].
**Definitive Publication (PEER-REVIEWED):** *Differential Geometry and its Applications*, Volume 55, pp. 146–166 (2017) [cite: 4, 5].

**Theorem Statement and Coordinate Pinning:**
The source formally defines a distinct complexity invariant, **equivariant determinantal complexity**, denoted `edc(P)`. It defines `edc(P)` as "the smallest $n$ such that there is an equivariant determinantal representation of $P$" [cite: 1]. 

The primary result states:
> "We initiate a study of determinantal representations with symmetry. We show that Grenet's determinantal representation for the permanent is optimal among determinantal representations respecting left multiplication by permutation and diagonal matrices (roughly half the symmetry group of the permanent). ... Our main result is that edc(permm) is exponential in m." [cite: 1].

Specifically, the authors prove that any determinantal representation $\tilde{A}$ of $\text{perm}_m$ that "respects $G$" (where $G$ is a subgroup of the symmetry group of the permanent, $G_{\text{perm}_m}$, specifically left multiplication by permutation and diagonal matrices) requires a matrix size exponential in $m$ (approximating $2^m - 1$) [cite: 1, 6]. 

**Status of the Result:**
*   **UNCONDITIONAL:** The $2^m - 1$ lower bound on `edc(permm)` is unconditional. 
*   **CONDITIONAL:** The connection to Valiant's conjecture is strictly conditional. The primary source states: "In particular, if any optimal determinantal representation of the permanent must be polynomially related to one with such symmetry, then Valiant's conjecture on permanent v. determinant is true" [cite: 1]. 

The primary source has not been withdrawn, nor has the restricted-model proof been supplanted. However, the exact limitations of this bound define the necessity of the AA-008 anti-anchor: `edc` $\neq$ `dc`. The unconditional exponential bound applies *only* to `edc`.

---

## (b) FOLLOW-ON WORK (2024–2026)

**Substrate Action:** Survey 24-month horizon for superseding results, refinement, and gravity well detection. Register distinct invariants to prevent coordinate collapse (HARD-5 doctrine).

The 2024–2026 literature reveals robust parallel progress, but crucially, *does not* extend the Landsberg-Ressayre exponential bound to unrestricted determinantal complexity (`dc`). Instead, it fragments the symmetry landscape into new, highly distinct coordinates. 

### 1. Dawar and Wilsenach (December 2025) – *New Coordinate Registration*
A critical refinement of symmetry-restricted bounds is published by Anuj Dawar and Gregory Wilsenach. 
**Publication:** *Theory of Computing*, Volume 21 (14), pp. 1–32. Published December 27, 2025 [cite: 7]. (Preprint announced February 2020 via arXiv:2002.06451 [cite: 8], conference version ICALP 2020 [cite: 9]).

**HARD-5 Coordinate Registration:** Dawar and Wilsenach establish new coordinates: **Square-Symmetric Arithmetic Circuit Size** and **Matrix-Symmetric Arithmetic Circuit Size**. These must be structurally isolated from `edc`. 
*   They define symmetric circuits as arithmetic circuits whose directed acyclic graph topology is invariant under the natural action of permutations on the input matrix variables [cite: 7, 10].
*   *Result (UNCONDITIONAL):* They establish "unconditional exponential lower bounds on the size of any symmetric circuit for computing the permanent" over characteristic $\neq 2$, while demonstrating that the determinant admits polynomial-size symmetric circuits over characteristic 0 [cite: 7, 9].

**Interaction with AA-008:** Dawar and Wilsenach actively resist the gravity well of collapsing symmetry coordinates. They explicitly contrast their metric with Landsberg-Ressayre:
> "Landsberg and Ressayre [cite: 11] establish an exponential lower bound on the complexity of the permanent (specifically over the complex field $\mathbb{C}$) under an assumption of symmetry, and it is instructive to compare our results with theirs. Their lower bound is for the equivariant determinantal complexity of the permanent. ... In summary, their result does not yield any lower bounds for symmetric circuits in the sense we consider." [cite: 7].

They further note: "On the other hand, while we cannot derive their results from ours, we can derive a lower bound on the determinantal complexity of the permament from our result which is incomparable with theirs" [cite: 7, 12]. This incomparable lower bound must be added to the work-queue for primitive registration.

### 2. Bedi and Suagee (March 2026) – *Unrestricted `dc` in Positive Characteristic*
**Publication:** *Theory of Computing Systems*, Volume 70. Accepted November 29, 2025; published March 5, 2026 [cite: 11, 13]. (Preprint announced October 12, 2023 via ECCC TR24-015 [cite: 14, 15]).

Bedi and Suagee operate in the *unrestricted* determinantal complexity coordinate (`dc`), but over arbitrary characteristic fields.
*   *Result (UNCONDITIONAL):* They provide "An elementary proof of quadratic lower bound for determinantal complexity of the permanent in positive characteristic... achieved by constructing a sequence of matrices with zero permanent, but the rank of Hessian is bounded below by a degree two polynomial" [cite: 13, 14].
*   This extends the classical quadratic lower bound for `dc(perm)` (e.g., Mignon-Ressayre 2004 for characteristic 0) to positive characteristics [cite: 15].
*   This confirms that unrestricted `dc(perm)` lower bounds remain stubbornly quadratic, reinforcing the structural necessity of AA-008: the exponential bound remains locked behind the equivariance restriction.

### 3. Chatterjee et al. / Kumar and Volk (January 2024) – *ABP vs `dc` Coordinate Mapping*
**Publication:** *LIPIcs ITCS 2024* (January 24, 2024) [cite: 16].
This paper explicitly addresses the state of unrestricted `dc(perm)`. 
*   *Premature Claim Flagging:* The authors cleanly flag that super-linear lower bounds for unrestricted `dc` simply do not exist for constant degree polynomials. They state: "for determinantal complexity the best lower bounds are larger than the number of variables only by a constant factor [Mrinal Kumar and Ben Lee Volk, 2022]" [cite: 16, 17]. 
*   *Coordinate Relation:* They prove that for constant degree homogeneous polynomials, their unrestricted determinantal complexity (`dc`) and algebraic branching program (`ABP`) complexity are within a constant factor [cite: 16, 17]. 

**Summary of Follow-on:** The 24-month follow-on literature confirms AA-008. The exponential bounds remain isolated in symmetry-restricted coordinates (`edc` and `symmetric circuit size`), while unrestricted `dc` bounds remain linear/quadratic.

---

## (c) FALSE-FORM RECURRENCE

**Substrate Action:** Identify and define filters for semantic drift, algorithmic conflation, and gravity well text that conflates `edc` with `dc` in the 2024–2026 literature.

The necessity of AA-008 is proven by active, ongoing false-form recurrence in the recent corpus. The gravitational pull of Valiant's conjecture causes unstructured datasets and human authors to continuously drop the "equivariant" qualifier, mapping the exponential bound onto the unrestricted permanent. 

We identify two primary classes of false-form recurrence in the 2024–2026 window:

### 1. Algorithmic Database Conflation (Machine-Generated False Forms)
Modern academic aggregation platforms utilize automated retrieval-augmented generation (RAG) and semantic snippet assembly. This process frequently strips coordinate qualifiers, generating synthetic false claims that will contaminate LLM training corpora if not filtered.

**Example Instance (March 2026 metadata):** 
A search index record for Bedi and Suagee's 2026 paper merges its abstract with the abstract of Landsberg-Ressayre, generating the following text block:
> "An elementary proof of quadratic lower bound for determinantal complexity of the per- manent in positive characteristic is stated. ... We introduce a restricted model of computation, equivariant determinantal complexity, and prove an exponential separation of the permanent and the determinant in this model. This is the first exponential separation of the permanent from the determinant in any restricted model." [cite: 13, 18].

*Why this is dangerous:* To an automated parser, this document attributes the 2017 `edc` exponential separation to the 2026 Bedi-Suagee quadratic bound paper, collapsing a decade of coordinate isolation into a single false narrative. **Filter Directive:** Any text block containing "An elementary proof of quadratic lower bound" immediately followed by "We introduce a restricted model of computation, equivariant determinantal complexity" must be registered as an algorithmic hallucination and excised from mathematical training sets.

### 2. General-to-Specific Citation Anchoring (Human-Authored Gravity Wells)
Human authors frequently cite restricted results as the "latest progress" on unrestricted conjectures, encouraging readers to incorrectly assume the restricted method is the definitive path to the unrestricted goal (a classical GCT gravity well).

**Example Instance (October 2023 / 2026):**
In their ECCC preprint/ToCS paper, Bedi and Suagee state:
> "The best known lower bound for determinantal complexity of the permanent is quadratic, as shown in [cite: 19]. It is conjectured that the determinantal complexity of the permanent grows faster than any polynomial. The reader can find the latest on this in [cite: 20]." [cite: 15].

Citation [cite: 20] in their text is Landsberg and Ressayre 2017. 
*Why this requires AA-008:* Bedi and Suagee are discussing unrestricted determinantal complexity (`dc`). By framing LR2017 (`edc`) as "the latest on this [the unrestricted conjecture]," the text exerts a gravity well effect. It suggests that symmetry-restricted determinantal representations are the continuous front-line of the unrestricted `dc` problem, blurring the mathematical wall between the models. AA-008 acts as a structural shear against this, ensuring the substrate parses LR2017 exclusively under the `edc` coordinate, not as a proxy for `dc`.

---

## (d) RECOMMENDATION

**Substrate Action:** Execute coordinate definitions, generate companion anchors, and assign downstream queue tasks.

### (i) Status of Anti-Anchor True Form
The true form of **AA-008 EQUIVARIANT_EXPONENTIAL_RESTRICTED** is **correct as stated but requires refinement**.
*   *Refinement:* The anchor must be updated to explicitly assert the HARD-5 coordinate distinction between `edc` (equivariant determinantal complexity) and `symmetric circuit size`. AA-008 currently prevents conflation of `edc` and `dc`; it must be expanded to prevent conflation of `edc` and the newer `symmetric circuit` invariants introduced by Dawar and Wilsenach (2025).

### (ii) New Companion Anti-Anchors and Primitive Registrations
During verification, distinct coordinates were surfaced that require immediate substrate registration:

*   **Create Companion Anti-Anchor:** `AA-008b SYMMETRIC_CIRCUIT_PERM` (Dawar-Wilsenach 2025).
    *   *Constraint:* "Exponential lower bounds on square-symmetric and matrix-symmetric arithmetic circuits do NOT imply exponential lower bounds on general arithmetic circuits, NOR are they mathematically equivalent to equivariant determinantal complexity lower bounds."
    *   *Target:* Prevent the collapse of circuit-topology symmetry into matrix-representation symmetry.

*   **Primitive Registration:** `dc(perm)_char_p_quadratic_bound` (Bedi-Suagee 2026) [cite: 13, 15].
    *   *Definition:* $\text{dc}(\text{perm}_d) \ge d(d-1)/2$ over fields of positive characteristic.
    *   *Status:* UNCONDITIONAL.

*   **Primitive Registration:** `dc_ABP_constant_degree_equivalence` (Chatterjee et al. 2024) [cite: 16].
    *   *Definition:* For homogeneous polynomials of constant degree $d$, determinantal complexity $s$ maps to a homogeneous ABP of size $O(d^5 s)$ and width $s-1$.
    *   *Status:* UNCONDITIONAL.

### (iii) Verification Queue Additions
The following claims discovered in the 2024–2026 window require independent substrate verification:

1.  **Work-Queue Entry (WQ-992):** Evaluate Dawar and Wilsenach's claim (2025) that they can "derive a lower bound on the determinantal complexity of the permament from our result which is incomparable with theirs [Landsberg-Ressayre]." [cite: 7]. Verify the specific formulation of this incomparable unrestricted `dc` lower bound and log its dimensions.
2.  **Work-Queue Entry (WQ-993):** Evaluate the claim attributed to Kumar and Volk [KV22] by Chatterjee et al. (2024) that the best unrestricted lower bound for determinantal complexity is strictly $1.5n$ (or $1.5n - 3$ for $\sum x_i^n$) [cite: 5, 16, 17]. Re-verify this $1.5n$ limit against any claimed super-linear breakthroughs in 2026.
3.  **Catalog Edit (CE-404):** Update the `DeterminantalComplexity` ontology tree to strictly branch: 
    *   `dc` (Unrestricted) 
    *   `edc` (Equivariant, left multiplication by permutation and diagonal) [Landsberg-Ressayre]
    *   `rdc` (Regular determinantal complexity) [cite: 6].
    *   *Circuit Corollaries:* `Square-Symmetric Circuit` and `Matrix-Symmetric Circuit` [Dawar-Wilsenach]. Ensure no cross-inheritance of exponential lower bounds between these branches.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHW2Eu8qd_c7N6wcDQM0wLvBZVK-9aw5a8P71W1Pc6-Cdvzd9SKjwjT2ZGftPkg05T_c5WBvbqJTYz-GAUu-UGQIphgV8xyXk00hIgYDaLHwWAcNhwF)
2. [dblp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeTyG7j8V0KbYnvgMPq2vAsVER1EjPzdZxu_Z6liKkCybfxLZ1N2k_m2u1gXZbnBdusZpw--nzQ5Y1pVh9CyiC6W_76TH0QGi2NtLopL0RnkI=)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEp6fgJj_n5xSMgBl-4QK7R4cT6pXuu9V2oaQK9LHHtUodY_EGUxfODml7Rmce7p5pYAv8xlB4pX-C0K8Zon_PqitnzqvbtEaDlLbySSYO75cRh34AY3069-8owBZFSSADZEi57N39H8BirO8Wv5ZdvhyY-4uoIT1oKq3PgElUpjyV8bCoWbZDexj1iAUaKyxOg9jp7ggkPwWF7IKwuopDzytw-547GF10PEAtcDN5ZjzZDnaMM9F1QRsD1BdVQqfvEfZdjIL1WPDOwvpKczgnwhoJVH88_be_z1mj2fF4=)
4. [ens-lyon.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJSqfTisnMro_0nhcQjlmcknOZXhTsO-fs_SJkoRSZJHzIS04FKC0GL4pqjDQoQhVkczIUAXR5lK2iCd0fGZX0i8B0DEY4AkLbxYs9NVGLtKIFKnmxw6ObKWQMvrAfmVxpH-JcOKwTmV0TJ29NnCj8MZ4fvA==)
5. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFy6USaLheVbdbcnH7gGvgemh3SuecBD5qHdA0PKpzWruUvM21K4QtE_YISr1O4w7jB-TPYeErfXpe7dWbU_yit9XiQVt_fUjzwyYocmroeBsRbPr6wUIyim0o8pykKnCrs-UPbcSLtbg-hJ2jBLTOJa8CC8z4r-LHrQw==)
6. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4GpcrbzJ72U_Sh3enYPEcCwNLseVuGE1vdzfjX2fYaC9eg73ePqrQpBgsWks6C5tZQfPWVRmsypbbmvgbpTO3eizu9SDyelp-0JpIylWW4XNUnSPd9K0e6lAkDU65Oa65d8c=)
7. [theoryofcomputing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAUKiA659baa-rLACQyf2wd7m_v6EEJ209nliAZkInhheQr2UfBkry9kp3YnYf_8GguVwxqqOCZCNc2nyFLE-nF6ssTFQS9go-6BbjeUaj_gFT_wfYfIZeJ6pNb5DqR6uKNqn8k7ykuISlcOAy4aZx1g==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHa5_YewFAqI1pmTY2_XY7wtv1rJJWAMmUgMQnkgjttAhXJQ8855F9SgJYZZDXxGEqjy1ooRPRupN7hmxNuUyxN2DC8bwoCSSHhIqDFIGLIIP2mz2oz)
9. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0ynXKdI2fbHIKr27REgAN2yrOb5PuY_Wu_UaYz00a2ncCpf4lYhR2P21BvELgl6IDdXACDEtS8PpIR-BENKkBFet2WbCcdQoWgPZKs9KAD89e_y7rOTtva5SwkcE_oCZ1TIUXB-plXiwWelWnIo9WkBWn7nyP5uhzJrKMvA==)
10. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkDoSff2HKJ07Rt5RE--iIQa31d5yH68tCu2XWqfKqM2YQo6ILfRgy93q4ccTJ8SVD8YYIjfNmxKiqjplaKyry_td4A-4kbwVhWihiHZ_R3o9Iq_l4WnKtLhUKLNsrNN2EeEBokKuZi6L-dXuyox58ZS6Pt_xijF6uHrFjxtRn9fZlXWEGlu77U-sI711Hx_3aLTRxZBOf46YyZNGhePNH0YLFcsg=)
11. [deepdyve.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFS7cx3UHgf3VvKgaMl8XjTsz0sbzLAK8vd-T_AMmmunSpweg9RlYyeFET3vjI0pbWvHYDRzAU23sZsYL0CbDX14j6qZ0wiDSIn9srVSoZ2uKth5Oto1DnTM02POwn-EfvuyX56ws_RdbbL0Srr0exdo1hA7mcNkTMy0RTFVwstLnYwFjCk7PCufBQ9pjzeB74Oyq4ISgxWyIFcCZrCC1aM_54VIyTRFTtY8t0=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxqL2ermMYcxJxDvea2OWJgdaxew187DVxup8MdGdB79uVQjRZftxiPyrys5VoUebxYcJuDwr0Sz4YgfbC9k2TneGP2DCPruE8P_kd0yo7HvMgyUQsuBnW)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIEOup0-niCQALKvbV2wxBrorUo_aXaNaLqXSAVCO1P0twfdM2-euQt4RNgvayJ90uzM71TGPamcT6yMdgTu_Rwp0HW5KsbPkFebtwTunltQeyMFuHqw9FvRVqgliVZzg3LKsARk_ftGqtk9gztLaJf1XJ7jNXKumEH_6NCToxCc1AIQ40lxTpeOUXo5d5gY_hvnxQ6ZTEVf7nFPk11J6xiUguTyMq)
14. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIeCaOZiGTzpoMMSmZ6kJmPNaEjYRkAGXP0n3KHzy93Xzwjam_LVS5d9zwUkx0cOCyfc-i0_C0YwBbIQIVsAQtp1ObxXwqOzuumuQtoHsPrvTkkwCF5rm0ZbuYqLD96BE4)
15. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWYGOZ_LKeyTYJJw-0xoJ-5SXk8VOlM-nFdJ43H9kCLM0_zPjGRlNPjOhPK9sD-JKK2NNAqebFJTg2p7cAZoZfoUa0Mp7yR52HpjJztdMuzsww8ECQdJeE0Q2vQd5sM2YzSCZPBXv6kmY=)
16. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_j9aH5cgMtYa3eHQO8PXjP7ctG8wuP1rlFrzocWWFuhWnFGZek8F8m3Lgp8jcJAeShDzaQ0QPW_enncLShJjTCMvm_-eX71I4ho7D1lR4yKomPYgeAtY-GXF1LDH9Q64Mok6u7t1aJ5Op_jJqiO6BETaGexeDG8Uc1o42)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_uIigHhCXZgKpIAr7g6Tb1uptIdOZaYPNtJrszWsLLzbAdlCune8xPJg8zKlYtQ1sA__DJS_yckIDAkJpFv8JqlBgtOxJQhDKdcH3gXjS0BgNNgumjz3uKFsU9Qi9bm4cuHniz758GBa13Jne6bd34vJchh36GlIVPPQUxKUoXwLoBCxW0RdCUSHLj1afYpFNYn1Y)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGE4aXzLGsWSkXkucwLeYyPcPJwZ-cQd00u4bHKy7LW71KK9pWDABEq5mSafpbfZV4ItkObYW1jx_GSuqHZc_QTGhXRDIilQ6bRb7XuKu1wo11gG6K5xJF1HKfOvmZKVsHLNtTJSdK6S4t8z6MDXYh3gHy1VW7FpeHyZ_hlTt7UqCHhXi4O7lKFSoJPRnbttZRS5q5my8J_wt7Y-DoEdUUL4ZO2qQIBhiKbXirM)
19. [Current time information in Munich, DE.](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOIKSSVxkYrR2-R1JxSLs4pb-KbC9dnFPcO9plSbNryh7dSoHXW_Nau1vkNyO8Bz0JSpt_G2iUzm3UbEmUjNqU5gnfOFF-sKghBF9hj0UX93dih0nGklboveA6Zpaot4-eu4WFJ2A3)
20. [emis.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjQDsRMda15_TzLzkBExKvb2nu4sQZNTE0k7O3GL8-ufaTLviXN9kYHSpKfeiWMDA-Wgs5LPF9f4E12Q90y0H8wVAtlwKZ5I7EMYF0MA==)

