# Prompt 07: DR-024 — VERIFY-LIVE T#93 Burgisser-Dogan-Makam-Wigderson 2026 torus-action orbit closure P-time

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChY1RFVFYXVYX0Q4SGJqckVQdm91T1lREhY1RFVFYXVYX0Q4SGJqckVQdm91T1lR
**Elapsed:** 1331s

---

# Anti-Anchor Verification: Torus-Action Orbit Closure and TOCI Coordinates

**Substrate Target:** `VERIFY-LIVE T#93 Burgisser-Dogan-Makam-Wigderson 2026 torus-action orbit closure P-time`
**Execution Timestamp:** Current
**Downstream Consumer:** T#93 catalog edit propagate; `OrbitClosureNonMembershipWitness` sub-type TOCI primitive proposal

The verification of the provided anti-anchor candidate reveals a severe chronological and mathematical conflation within the current substrate state. The candidate `VERIFY-LIVE T#93 Burgisser-Dogan-Makam-Wigderson 2026 torus-action orbit closure P-time` is **FALSE IN STATED FORM** and requires immediate inversion. The polynomial-time decidability of exact torus-action orbit closure was unconditionally established in **2021**, not 2026, and the primary author list was explicitly five authors (including Michael Walter), not four [cite: 1]. 

The 2024–2026 literature window exhibits a massive gravitational well that collapses mathematically distinct coordinates: the polynomial-time exact commutative torus results of 2021 [cite: 1, 2], the `abc`-conjecture-conditional robust commutative torus results of 2024 [cite: 3, 4], and the graph-isomorphism-hard (GI-hard) non-commutative general tensor orbit closure intersection (TOCI) class formalized in late 2024 and expanded in 2025–2026 [cite: 5, 6, 7, 8]. To prevent cascading errors in the mathematical reasoning agents, we must isolate these invariants into distinct primitive registrations and deploy a corrected anti-anchor.

---

## (a) PRIMARY SOURCE CONFIRMATION

The assertion of a 2026 publication date for polynomial-time torus-action orbit closure algorithms is a hallucinated forward-projection. The definitive primary source for the unconditional polynomial-time algorithm is:

**Primary Source:**
Peter Bürgisser, Mahmut Levent Doğan, Visu Makam, Michael Walter, and Avi Wigderson. "Polynomial time algorithms in invariant theory for torus actions."
**Preprint:** arXiv:2102.07727 (February 15, 2021) [cite: 1].
**Definitive Publication:** *36th Computational Complexity Conference (CCC 2021)*, Dagstuhl, Germany (July 15, 2021). DOI: 10.4230/LIPIcs.CCC.2021.32 [cite: 4, 9].

**Coordinate Distinction (HARD-5 Enforcement):**
The 2021 primary source explicitly defines and solves four fundamentally distinct computational problems over a continuous commutative group action (an algebraic torus $T = (\mathbb{C}^\times)^d$ and its compact subgroup $K = (S^1)^d$ acting on $\mathbb{C}^n$). The substrate must never collapse these. As articulated in the primary source [cite: 10, 11], given vectors $v, w \in \mathbb{C}^n$:
1.  **Orbit equality:** Decide if $O_v = O_w$.
2.  **Orbit closure intersection:** Decide if $\overline{O_v} \cap \overline{O_w} \neq \emptyset$.
3.  **Orbit closure containment:** Decide if $O_w \subseteq \overline{O_v}$.
4.  **Compact orbit equality:** Decide if $C_v = C_w$.

**Theorem Statement:**
The definitive result is encapsulated in Theorem 1.2 of the primary source. 
> "Given as input a weight matrix $M \in \text{Mat}_{d,n}(\mathbb{Z})$ as well as vectors $v, w \in \mathbb{Q}(i)^n$, denote by $b$ the maximal bit-length of the entries of $v, w$, and $M$. Then we can in time poly($d, n, b$): (1) decide whether $O_v = O_w$; (2) decide whether $\overline{O_v} \cap \overline{O_w} \neq \emptyset$; (3) decide whether $w \in \overline{O_v}$." [cite: 12]

The authors explicitly note that the Euclidean topology and the Zariski topology coincide for these closures [cite: 10, 11]. Furthermore, Corollary 1.5 of the 2021 paper provides a vital downstream component: if $\overline{O_v} \cap \overline{O_w} = \emptyset$, the algorithm construct in polynomial time an arithmetic circuit computing a separating invariant monomial that serves as a non-membership witness [cite: 12].

**Verdict on Candidate:**
The primary source was neither withdrawn, supplanted, nor qualified, but the candidate string's date (2026) and author list (missing Walter) are strictly incorrect. The result is UNCONDITIONAL and PEER-REVIEWED [cite: 2, 9]. 

---

## (b) FOLLOW-ON WORK (2024-2026)

The 24-month window spanning 2024 to early 2026 reveals a bifurcation in the literature. Researchers expanded the 2021 exact commutative result into two highly distinct coordinates: **Robust (Approximate) Commutative Actions** and **Exact Non-Commutative Actions (TOCI)**. The substrate must weight these alternatives explicitly to prevent gravitational-well collapse.

### Coordinate 1: Robust Orbit Problems (Commutative)
In 2024, the exact same five authors (Bürgisser, Doğan, Makam, Walter, Wigderson) investigated the complexity of approximating the distance between torus orbits, shifting from exact algebraic algorithms to numerical robustness.
*   **Source:** "Complexity of Robust Orbit Problems for Torus Actions and the abc-conjecture."
*   **Preprint:** arXiv:2405.15368 (May 24, 2024) [cite: 3].
*   **Definitive Publication:** *39th Computational Complexity Conference (CCC 2024)* (July 15, 2024). DOI: 10.4230/LIPIcs.CCC.2024.14 [cite: 4].

*Findings:* The problem of approximating the distance between orbits in $\mathbb{C}^n$ up to a factor $\gamma > 1$ is mathematically distinct from exact closure intersection. The authors proved a CONDITIONAL result: solving this for an exponential approximation factor $\gamma = \exp(\text{poly}(n))$ is in polynomial time **if and only if** a version of the number-theoretic `abc`-conjecture holds [cite: 3]. Conversely, for smaller approximation factors ($\gamma = n^{\Omega(1/\log\log n)}$), the problem is UNCONDITIONALLY NP-hard via reduction from the closest vector problem for lattices [cite: 3]. 

### Coordinate 2: The Emergence of the TOCI Complexity Class (Non-Commutative)
Parallel to the robust commutative investigations, a massive structural effort mapped the non-commutative case (actions of the general linear group on tensors). 
*   **Source:** Vladimir Lysikov and Michael Walter. "Complexity theory of orbit closure intersection for tensors: reductions, completeness, and graph isomorphism hardness."
*   **Preprint:** arXiv:2411.04639 (November 07, 2024) [cite: 5, 13].
*   **Definitive Publication:** *66th IEEE Symposium on Foundations of Computer Science (FOCS 2025)*, Sydney, Australia (December 2025) [cite: 14, 15].

*Findings:* Lysikov and Walter formally defined the complexity class **TOCI** (Tensor Orbit Closure Intersection), capturing the power of orbit closure intersection problems for general tensor actions under continuous groups like the general linear group [cite: 6, 16]. Unlike the polynomial-time commutative torus setting, TOCI encompasses problems with extreme computational hardness. They UNCONDITIONALLY established that Graph Isomorphism (GI) is Karp-reducible to TOCI-complete problems (e.g., the equivalence of 2D PEPS tensor networks with constant physical dimension), rendering $GI \subseteq TOCI$ [cite: 6, 16]. This constitutes the first rigorous lower bound for general orbit closure intersection [cite: 16, 17].

### Coordinate 3: TOCI Completeness and Holant Equivalences (2025–2026)
*   **Source:** Jin-Yi Cai and Ben Young. "Vanishing Signatures, Orbit Closure, and the Converse of the Holant Theorem."
*   **Preprint:** arXiv:2509.10991 (September 13, 2025) [cite: 18, 19].
*   **Definitive Publication:** *17th Innovations in Theoretical Computer Science Conference (ITCS 2026)* (January 2026). DOI: 10.4230/LIPIcs.ITCS.2026.32 [cite: 7, 20].

*Findings:* Cai and Young proved that if two sets of tensors (signatures) $\mathcal{F}$ and $\mathcal{G}$ are Holant-indistinguishable and quantum-nonvanishing, their $GL_q$-orbit closures intersect [cite: 8, 19]. They UNCONDITIONALLY proved that Holant-indistinguishability is complete for the TOCI complexity class formalized by Lysikov and Walter, proving that finding a converse to the Holant theorem is inherently GI-hard [cite: 7, 8, 19]. 

### Coordinate 4: Average-Case Easy Unitary/Orthogonal TOCI (March 2026)
*   **Source:** Anonymous. (Preprint covering average-case algorithms for Tensor Orbit Closure Intersection). 
*   **Preprint:** arXiv:2603.27128 (March 28, 2026) [cite: 15].

*Findings:* This 2026 work proves that tensor orbit closure intersection problems under orthogonal ($O$) and unitary ($U$) groups are **average-case easy** (in polynomial time), specifically allowing one to test whether a Haar-random tripartite quantum state is locally unitary equivalent to an arbitrary state in polynomial time [cite: 15]. 

---

## (c) FALSE-FORM RECURRENCE

The substrate query targets the false candidate `VERIFY-LIVE T#93 Burgisser-Dogan-Makam-Wigderson 2026 torus-action orbit closure P-time`. Why does this false form exist? A forensic trace of the 2024–2026 literature reveals an acute semantic blending (a gravity well) where LLMs and human authors routinely conflate the baseline 2021 exact torus result with the 2024–2026 emergence of TOCI and average-case results. 

The most egregious instance of this false-form recurrence appears directly in the text of the March 2026 preprint, arXiv:2603.27128. 
**Quote:** 
> "First, the tensor orbit closure intersection problems under orthogonal and unitary groups are average-case easy, in contrast to evidence for their worst-case hardness (Bürgisser–Doğan–Makam–Walter–Wigderson, CCC'21), as well as for the average-case tensor isomorphism under the general linear group action (Grochow–Qiao, SICOMP'21)." [cite: 15]

**Analysis of the Recurrence:**
This 2026 primary source *incorrectly attributes* evidence for the worst-case hardness of orthogonal and unitary tensor orbit closure intersection to the 2021 Bürgisser et al. CCC paper [cite: 15]. 
1.  The 2021 paper by Bürgisser et al. proves **polynomial-time** decidability for commutative (torus) actions [cite: 1, 2], not worst-case hardness for non-commutative orthogonal/unitary actions. 
2.  While the 2021 paper does mention the NP-hardness of general orbit closure containment in its introduction (referencing independent 2018 work by Garg et al. regarding border rank) [cite: 2, 21], it is mathematically incoherent to cite the 2021 torus paper as the origin of worst-case hardness for TOCI under orthogonal/unitary groups. 
3.  The actual hardness results for TOCI were established by Lysikov and Walter in late 2024 ($GI \subseteq TOCI$) [cite: 5, 6].

Because 2025 and 2026 papers (like Cai & Young 2026 [cite: 7, 8] and arXiv:2603.27128 [cite: 15]) heavily cite the 2021 torus result as a preamble to discussing their novel 2026 non-commutative tensor network and quantum algorithms, language models scraping arXiv automatically collapse the 2026 metadata with the Bürgisser et al. author list. The substrate then falsely pins `Burgisser-Dogan-Makam-Wigderson 2026 torus-action orbit closure P-time` by dropping Walter and lifting the publication date of the citing 2026 papers.

Therefore, the anti-anchor is absolutely required to block this gradient, but the true form must be meticulously registered to separate the coordinates.

---

## (d) RECOMMENDATION

**Verdict:** The anti-anchor's true form is **incorrect as stated and needs rigorous inversion.** 

**Actionable Substrate Edits:**

**(i) Anti-Anchor Refinement:**
Replace the current false candidate with the following verified anti-anchor pin:
*   `ANTI-ANCHOR PIN: BDMWW 2021 (CCC 2021) established EXACT P-TIME for commutative torus-action orbit closure. Do NOT attribute 2026 dates to this finding. Do NOT attribute worst-case general TOCI hardness to this paper. TOCI complexity class (GI-hard) was established by Lysikov-Walter 2024/2025. Robust torus approximation is abc-conditional P-time (BDMWW 2024).`

**(ii) New Primitive Registrations (HARD-5 compliance):**
We must register the distinct computational coordinates mapping to their respective primary sources.
*   `Action: REGISTER_PRIMITIVE`
    *   **ID:** `TorusExactOCI_PTime`
    *   **Source:** Bürgisser, Doğan, Makam, Walter, Wigderson (CCC 2021; arXiv:2102.07727) [cite: 1, 9].
    *   **Definition:** Exact decision algorithms for orbit equality, orbit closure intersection, and orbit closure containment for rational representations of tori.
    *   **Status:** UNCONDITIONAL, PEER-REVIEWED.
*   `Action: REGISTER_PRIMITIVE`
    *   **ID:** `TorusRobustOCI_ABCConditional`
    *   **Source:** Bürgisser, Doğan, Makam, Walter, Wigderson (CCC 2024; arXiv:2405.15368) [cite: 3, 4].
    *   **Definition:** Polynomial-time algorithm for exponential approximation factor of orbit distances.
    *   **Status:** CONDITIONAL (requires abc-conjecture), PEER-REVIEWED.
*   `Action: REGISTER_PRIMITIVE`
    *   **ID:** `TOCI_ComplexityClass`
    *   **Source:** Lysikov and Walter (FOCS 2025; arXiv:2411.04639) [cite: 6, 14].
    *   **Definition:** Tensor Orbit Closure Intersection class for non-commutative general linear group actions. 
    *   **Status:** UNCONDITIONAL ($GI \subseteq TOCI$).
*   `Action: CATALOG_EDIT`
    *   **Target:** `OrbitClosureNonMembershipWitness` sub-type TOCI primitive proposal.
    *   **Delta:** Reject conflation. Orbit closure non-membership witnesses (via invariant polynomials) can be synthesized in poly-time for commutative torus actions (per Corollary 1.5 of BDMWW 2021) [cite: 12], but computing such witnesses for general TOCI is at least GI-hard (per Lysikov-Walter 2025) [cite: 6]. Update the T#93 catalog to reflect this architectural split.

**(iii) Verification Queue Additions (Work-Queue Entries):**
The extraction of the 2024–2026 literature surfaced two high-value claims that require independent substrate verification.
*   `Action: ENQUEUE_VERIFICATION`
    *   **Target Claim:** Holant-indistinguishability is TOCI-complete (Cai and Young, ITCS 2026; arXiv:2509.10991) [cite: 7, 19].
    *   **Context:** Check proof dependencies on the quantum-nonvanishing constraint.
*   `Action: ENQUEUE_VERIFICATION`
    *   **Target Claim:** Tensor orbit closure intersection under orthogonal and unitary groups is average-case easy (poly-time) (Anonymous, arXiv:2603.27128) [cite: 15].
    *   **Context:** Verify the statistical bounds for the Haar-random quantum state local unitary equivalence algorithm. Confirm if the cited worst-case hardness misattribution (to BDMWW CCC 2021 [cite: 15]) structurally damages the paper's primary proofs or merely serves as flawed introduction framing.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF56mOWS05ZBWw4Xb1-uiwpLdebmGqva6r5oZcxQ7KllxOeMnmK3SbL08ZyS7Kq32OSL41XrBbmIR_2HYEBSGVFsROOKk-70HnMEtebAZw-VBrHbh8vfQ==)
2. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGB-phF62O7U5ddLJpEjgqobRMGtjbG_CPAMJQyhDSVe8wWhV0BpkN7mKJvjjKDqtS5-MPA1aY1vB-JixTPh3tr-6GUBFvN7I5tPtbWIn5HnmAE0lfw2w8QYjUkAfB_KzUqxgfMe23jc8X87Rjzhi8bVlOTlFBaHXUe0TB7ybreR84GwGA8J6_5gUiF5aepvstbWe_3KORiBacl3_OAB1Uc)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGlwapCBsMzk5V64amLnwxbbiz-OUh0rpyeIyUfmEGeQT7ye0AOsCvz13-6JHM1FYHwpEnuh_0oEtZwFivvRs5LiWILUz5rZAvjdKt14kO3oAt4CV23iQ==)
4. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBpFhrafKKjymyAqadFoejyuaQmcWiqgJy_mEonKhWOGpO1KWVpfmAu6sUiNeqc2P5PumCtVa7UH-iEKnq_ILechBR-GwXNyujdKY7tH1fs-Gkd5AM7CEHTD7qjK_F_l_BPMAZ62Yw3guhBXbtIzij2XagIB0D0r8GVeF8)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFj_PvpDYkZi9qi_zeSW2fxPL0oRem72yONUPk5gsK10G-JyjYrw4x9H46Pst8xC9fyjo7YhDcvg8l6b_Jc8S89JJ44qtUAfCNngus9Gv-c9Rb6bPCwaQp6t7sy8lgBwNRla00EcZuFhuTWHB3BzLBMzmbzn1y1-x_RBT3PaG1ckgNP0k9_WgVCJI38PiRfxhUqXXh-mNTvuD94Y4yQ1dzEVnvK2NePWSBWxmQxKG4ocs-m5wn4gA0uD8SPEqMEzAElZll5ZQzNJ9pUhM-Pf1RBvGHkjE2o0_rcIY1o)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHj971wvGnDLzfd2v3sLIT1-ssEuTR4M88934MtGxZ6zQbzTxzLvx3TZYGHANBFEPpV9kvNusVwkXHfWfOUyKH8ZD-XDRgDP-9xE5HGKX7wYUy77FzNXdz71g==)
7. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7Ug61XmNiyx-Cv1Uk331YpvdFyF0VPgu99PCW5Xo5YrLj7ImI4pkQ2IwvV4nvQKK7BI0E4G2ELRfMC6EJy-D1K3q2oD_Ym-lO8b19FBnwfexXJQz4E7Vka-uf2HDCBG3jn6XvcYCo8IkkxEnaEpIPmwfT4ateKcPpA0JoEg==)
8. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0DsDncGBqvBLpZ5b1JHOOAphgN9u5Tz3YXFENBbDwOgZFuIH7WjNccXEz42Vl-WlWhXh9xAT1Fy-PfPst7v7FjbknzOc3eoNFLKhCPILKQLw1Z-PljPc7cFwTMuI1LiXMaYTxB_-lfnF70URkynu-ifIjhcPf4iY3Y8XOqjRU6DOpnCTMYhJh_JCAkCJTiH2-f27kc0yVwgULmvyEwcFXTfRi)
9. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCtAqPWJpLX8EwXL7AQkM3558CHb28S21fF7I2q4YjgqlgwHxJb8IOPeGl7BEHzJZ7TR8d2WSu9Wj-KLs3jaX10L21k0t6fzSMAorDk99hC3gxdtmlhXLRK7Vayr_3BAV2DjvFTsKdAU04oqcABSvAVvTZ-hXMLcEMY77f)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHO3slauzFnDqaZSjPvu2Wnm4D07AWhHyE_AxYU0G39MWlvSavY5ubnrTkNJf-VyBr24eZS9I_awlQ9ZnK7FYHfsGz59Gon1RjpR5bDeQHA7z9EqgMLHQ==)
11. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwvMrdaZVagOtYCLbqjvcqsuADc_wdSgZJKqgv1oPaCLW2pi89tBV-djPpkujJ9YyHnnQhXTBIrR5_bWMK2WkmaujU6A9PwNqXBhaeHoxnit2PL8r3EzsQpHZRlCn8thANPg8ooarKVU8WVV7SNAuHUxi0JbyswyLOx6HqXjKDgRsB8pr9_IU8dI5O5mhk7DtN4WPPD50UioyCPLlb0a3q)
12. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVIBmHIl_LSARt10E7RCbm-IBURi-Lsr7Wj298827DlmnXbgHB86AsMQ5T_XK3Shvv_PcUl1aoHZwuzoxZac6nW3c72QeO6P5LmF7kSs8ADQ9fGRcJI86b4jJbbHvF9FYCl8O701KAShArU6_KHxLdEy3o-DidsXqohTU=)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdMWLQmckqRyvOwRsIvVk5MTlC-5MRafHPHkFR9RE9LhZ9_3072kuGpOAgt3pn2zRxg8bMX8-G0sbNbXR4Opa5VXAT9BoDWKhxIL3N6GjrNN-T6bpmnw==)
14. [michaelwalter.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZ4oNjJ87FkigGrVYvcPJSZAsArgS7ZN6RvhiDacXF_XJ7kzQo4aSsSaZ0GBa2Ielt3PhHeygaE0BTV1b7QIE8cs9AoKB66QIFXm-bc-muy5VCKA39bg5RpcdHr8Y=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjOUAWZi3gMq3t_9fR-uC4lpi-oEv_O7TxsbEa0flfT2y1kH9ni78LtgQCNkI_B9SXFg3am-LriEeZ2SepWmWinYSdglkgdp6WuHyQSmDXNhnB1WbEfSzK8A==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHT4jEc9GF7YTKUQaMWbV-ofljd5xwzM3qbDk603aw6cpIX-tvoA_Vz9VohxuGuARs1wGeKo137LxQRYuJCH4amC1O0ClLE4nj5vuBiSdSUh70CrKvC5g==)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEooIU_uy1adaSYSJXBM-8QvJdTZDQSZKzUsNyFZPXsJ8dvGXzq6XYjbBvbLPTX9kAHEPGIJCIq3o6Igq2uXWdML492JQ-mVR989Xn4PD-vXNOyNSqm7l7i5jB8iGsbNDCyL8TGkDnT1zq65f-58kz7x4YNum6mj-VKniJDmLLhZRx3y_K-fpExjSZFltAmGu9tF3rBV-TcvrtyrFQmzPVoYEeMGSoUaM9rMwbApVu1369NjigHx8e3pkTapITuBVtChuzd3N0YNvox-UX8Wh0=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHPm864z8uhUvZZLD0GGD_dBy5se18JPShNEA2or3GEmlUQ7K7Kw17uJ7T-U43BHFcbRag8hp5yi7L5GK5RrGmHZLnfCuuBjPm-5Jbcgtdq_lI3vNOng==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJ2Blq6IRR0BRuV6joQLtqG_Z1UF3_yLKqUHx3hd47eovXjLE9IHxMrnxrsCocQDGl25G82KGCxR0goaBtXd6C5Qxq9Zv6FTyfEz8IsTaegdpFbuLhuw==)
20. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwJ-PS05X3egMwyx3eWt_Qq5saGJndfskvPKEkM0QmFYZyN6XLVVojIA8Xzh1UZ7BSBhTVHR8ayxAGQJQ3FNYIyn_tdsg-kX3r-lcY70Kc-zRZWuf6Le5m0oqWY_kN7QHy6RQyL56_d-Cy-GYknhirEA==)
21. [liverpool.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgDmoeMAFkZRYlccvxAv4kBqsdcm9V5W86WZUk-_To_cD9kCciu1yAndnesLwjxMlhwSsmJ4iNO8DzXJFSlSwPQEDeKZFYTNXwHpxD-75syGB9EwJV0JGEsXgkEBzmPu5fCQOOgPOxLmUH0blhils=)

