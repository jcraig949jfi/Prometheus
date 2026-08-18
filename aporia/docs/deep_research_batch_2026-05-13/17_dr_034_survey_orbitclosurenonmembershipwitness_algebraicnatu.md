# Prompt 17: DR-034 — Survey OrbitClosureNonMembershipWitness + AlgebraicNaturalProofsBarrier supporting lit (T#92)

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdURWNFYXFyOEFhQy1fdU1QM2ZPYnVBWRIXVEVjRWFxcjhBYUMtX3VNUDNmT2J1QVk
**Elapsed:** 607s

---

# Anti-Anchor Verification: Orbit Closure Non-Membership Witnesses and the Algebraic Natural Proofs Barrier

**Key Points**
*   The Forbes-Shpilka-Volk (FSV) Algebraic Natural Proofs (ANP) barrier correctly maps the conditional non-existence of algebraic natural proofs to the succinct derandomization of polynomial identity testing (PIT).
*   Bürgisser-Ikenmeyer-Panova (BIP) unconditionally refute *occurrence obstructions* for padded permanent versus determinant orbit closures, but explicitly preserve *multiplicity obstructions* as a valid geometric complexity theory (GCT) coordinate.
*   Recent 2024-2026 results redefine the barrier boundaries: van den Berg et al. (2024) prove algebraic natural proofs can unconditionally be assumed to be isotypic; Chatterjee et al. (2025) provide existence proofs for VP equations, narrowing the barrier's absolute scope; Kush (2026) introduces an unconditional barrier specifically targeting the min-partition rank method against multilinear algebraic branching programs (mABPs).

**Context and Scope**
This verification report assesses the target anti-anchor "Survey OrbitClosureNonMembershipWitness + AlgebraicNaturalProofsBarrier" (T#92). The scope spans the primary sources establishing the ANP framework (FSV 2017/2018) and the GCT occurrence obstruction refutation (BIP 2016/2019), continuing through the contemporary 2024-2026 landscape. Findings strictly differentiate mathematical coordinates, notably segregating occurrence obstructions from multiplicity obstructions, and delineating various algebraic complexity metrics (e.g., border Waring rank vs. min-partition rank vs. completion rank). Outputs are structured as direct substrate inputs for Project Prometheus, yielding actionable anti-anchor pins, primitive registrations, and work-queue entries.

---

## (a) PRIMARY SOURCE CONFIRMATION

The candidate anti-anchor addresses two distinct but interconnected phenomena in algebraic complexity theory: the Algebraic Natural Proofs (ANP) barrier and the failure of occurrence obstructions in Geometric Complexity Theory (GCT). Both require precise alignment with their primary sources to prevent the collapse of conditional statements into unconditional ones, and the conflation of distinct algebraic invariants.

### 1. The Algebraic Natural Proofs Barrier
**Primary Source:** Forbes, M. A., Shpilka, A., and Volk, B. L. "Succinct Hitting Sets and Barriers to Proving Algebraic Circuits Lower Bounds." 
*   *ANNOUNCED-NOT-PUBLISHED:* arXiv:1701.05328v1 [cs.CC], January 19, 2017 [cite: 1]. STOC 2017 [cite: 2].
*   *PEER-REVIEWED:* Theory of Computing, 14(1): 1-45, 2018 [cite: 3, 4].

**Result Statement:** The FSV framework formalizes an algebraic analog to the Razborov-Rudich natural proofs barrier in Boolean complexity. The result is **CONDITIONAL**.
*   *Exact Quote:* "Following a similar result of Williams in the boolean setting, we show that the existence of an algebraic natural proofs barrier is equivalent to the existence of succinct derandomization of the polynomial identity testing problem. That is, whether the coefficient vectors of polylog(N)-degree polylog(N)-size circuits is a hitting set for the class of poly(N)-degree poly(N)-size circuits" [cite: 1, 5].
*   *Coordinate Distinction:* The barrier relies strictly on the existence of *succinct hitting sets* for the polynomial class $\mathsf{VP}$, rather than cryptographic pseudorandom functions as in the Boolean setting [cite: 2, 6].

**Companion Primary Source:** Grochow, J. A., Kumar, M., Saks, M. E., and Saraf, S. "Towards an algebraic natural proofs barrier via polynomial identity testing."
*   *ANNOUNCED-NOT-PUBLISHED:* arXiv:1701.01717 [cs.CC], January 2017 [cite: 7].
*   *Result Statement:* Independently formulated the identical barrier, phrasing it via defining equations (metapolynomials) that evaluate to zero on the coefficient vectors of easy polynomials [cite: 7, 8].

### 2. Orbit Closure Non-Membership (The "BIP" Barrier)
**Primary Source:** Bürgisser, P., Ikenmeyer, C., and Panova, G. "No occurrence obstructions in geometric complexity theory."
*   *ANNOUNCED-NOT-PUBLISHED:* arXiv:1604.06431v1 [cs.CC], April 21, 2016 [cite: 9]. FOCS 2016 [cite: 10].
*   *PEER-REVIEWED:* Journal of the American Mathematical Society (JAMS), 32: 163-193, 2019 [cite: 10, 11].

**Result Statement:** This theorem is an **UNCONDITIONAL** geometric obstruction, but highly specific to one mathematical coordinate: *occurrence obstructions*.
*   *Exact Quote:* "The permanent versus determinant conjecture is a major problem in complexity theory that is equivalent to the separation of the complexity classes $\mathsf{VP}_{ws}$ and $\mathsf{VNP}$. Mulmuley and Sohoni (SIAM J Comput, 2008) suggested to study a strengthened version of this conjecture over the complex numbers that amounts to separating the orbit closures of the determinant and padded permanent polynomials. In that paper it was also proposed to separate these orbit closures by exhibiting occurrence obstructions... We prove that this approach is impossible. However, we do not rule out the general approach to the permanent versus determinant problem via multiplicity obstructions as proposed by Mulmuley and Sohoni" [cite: 9, 12].
*   *Coordinate Distinction:* The literature exhibits a severe gravity well that collapses "representation theoretic obstructions" into a single failed path. BIP explicitly isolates **occurrence obstructions** (representations occurring in one coordinate ring with strictly zero multiplicity in the other) from **multiplicity obstructions** (representations where the dimension of the highest weight vector space differs). The substrate must rigidly maintain this distinction [cite: 9, 13].

## (b) FOLLOW-ON WORK (2024-2026)

The 24-month window fundamentally restructures both the ANP barrier and the GCT obstruction landscapes. The literature demonstrates a pivot from general conditional barriers to unconditional limits on specific proof techniques (e.g., min-partition rank) and a resurgence of multiplicity-based geometric approaches. 

### 1. Unconditional Barrier for the Min-Partition Rank Method
**Work:** Kush, D. "An Unconditional Barrier for Proving Multilinear Algebraic Branching Program Lower Bounds."
*   *Date:* April 1, 2026 (arXiv:2604.00746v1 [cs.CC]) [cite: 14, 15].
*   *Substrate Input:* **[PRIMITIVE REGISTRATION]** `MinPartitionRankmABPBarrier`
*   *Result:* Kush proves an **UNCONDITIONAL** barrier demonstrating that the min-partition rank method cannot prove superpolynomial lower bounds against multilinear algebraic branching programs (mABPs) [cite: 14, 16].
*   *Behavior Delta:* Overcomes the quasipolynomial upper bound $N(n) \le n^{O(\log n/\log\log n)}$ formulated by Fabris, Limaye, Srinivasan, and Yehudayoff (2026), proving exactly $N(n) = n^{O(1)}$ by biasing a symmetric random walk. This establishes that new techniques separating $\mathsf{mVBP}$ from higher classes in the multilinear hierarchy are strictly required, bypassing the min-partition rank [cite: 14, 15].
*   *Coordinate Definition:* Ensure *min-partition rank* is registered as a strictly distinct coordinate from *Waring rank*, *border Waring rank*, and *tensor rank* [cite: 14, 17].

### 2. Isotypic Projections of Algebraic Natural Proofs
**Work:** van den Berg, M., Dutta, P., Gesmundo, F., and Lysikov, V. "The complexity of highest weight metapolynomials."
*   *Date:* July 15, 2024 (CCC 2024, LIPIcs Vol. 300) [cite: 13, 18].
*   *Substrate Input:* **[ANTI-ANCHOR PIN]** `IsotypicAlgebraicNaturalProofEquivalence`
*   *Result:* Proves that in the algebraic metacomplexity framework, the decomposition of metapolynomials into their isotypic components can be implemented efficiently (with only a quasipolynomial blowup in circuit size). 
*   *Significance:* "In the context of algebraic natural proofs, it means that without loss of generality algebraic natural proofs can be assumed to be isotypic" [cite: 13, 19]. This rigorously bridges the FSV barrier with GCT: if an algebraic natural proof exists, a highest weight vector (HWV) forming a representation-theoretic obstruction can be efficiently synthesized.

### 3. Conditional Existence of Algebraic Natural Proofs
**Work:** Chatterjee, P., Kumar, M., Ramya, C., Saptharishi, R., and Tengse, A. "On the Existence of Algebraic Natural Proofs."
*   *Date:* February 3, 2025 (arXiv:2004.14147v4, merging FOCS 2020 and STACS 2022 results) [cite: 20, 21].
*   *Substrate Input:* **[CATALOG EDIT]** `ANPExistenceConditions`
*   *Result:* Provides evidence *against* a blanket natural proof barrier. Proves that the subclass of $\mathsf{VP}$ containing polynomial families with bounded coefficients *has* efficient defining equations. Over finite fields, this holds without restriction on coefficients [cite: 20, 22]. 
*   *Caveat:* Conversely, over fields of characteristic zero, $\mathsf{VNP}$ lacks efficient equations *if* the permanent is exponentially hard for algebraic circuits, acting as a conditional hardness generator for metapolynomials [cite: 21, 22]. 

### 4. Resurgence of Multiplicity Obstructions
**Work:** Dutta, P., Gesmundo, F., Ikenmeyer, C., Jindal, G., and Lysikov, V. "Geometric complexity theory for product-plus-power."
*   *Date:* May 28, 2025 (arXiv:2211.07055v3 [cs.CC]) [cite: 23, 24].
*   *Substrate Input:* **[WORK-QUEUE ENTRY]** `MapMultiplicityObstructionProductPlusPower`
*   *Result:* Directly bypasses the BIP 2016 occurrence obstruction dead-end. The authors successfully implement the GCT approach against the power sum by debordering the orbit closure of the product-plus-power polynomial. They obtain "new multiplicity obstructions that are constructed from just the symmetries of the polynomials" [cite: 23, 24]. 

## (c) FALSE-FORM RECURRENCE

The primary failure mode in the literature is the gravitational pull of simplified narrative arcs—specifically, the assertion that "GCT is dead" due to the BIP barrier, or that the FSV ANP framework represents an unconditional "no-go" theorem for algebraic complexity.

### Instance 1: Conflation of Occurrence and Multiplicity Obstructions
**Recurrence Type:** Collapsing distinct coordinates (HARD-5 violation).
*   *Observation:* Various sources frame the BIP result broadly as refuting "representation-theoretic obstructions." For example, semantic indexing systems frequently truncate the scope of the BIP paper, classifying it under generic tags such as "No Occurrence Obstructions in Geometric Complexity Theory" but summarizing it as "it is proved that the approach to separating these orbit closures by exhibiting occurrence obstructions is impossible... and it is proved that the approach to separating these orbit closures is impossible" [cite: 25]. 
*   *Counter-Force:* Dörfler, Ikenmeyer, and Panova (ICALP 2019) explicitly published "On Geometric Complexity Theory: Multiplicity Obstructions Are Stronger Than Occurrence Obstructions" to combat this exact false-form recurrence [cite: 26]. Recent work by van den Berg et al. (CCC 2024) carefully reiterates: "However, it is known that occurrence obstructions do not work in certain setups... Theorem 1.1 makes no statement about the viability of the method of multiplicity obstructions" [cite: 13]. 
*   *Action:* The anti-anchor is **strictly needed** to pin the divergence between `OccurrenceObstruction` (provably defunct for standard padded perm vs det targets) and `MultiplicityObstruction` (active research vector, proven strictly stronger).

### Instance 2: Overstating the Generality of the FSV Barrier
**Recurrence Type:** Treating conditional bounded-coefficient metrics as universally binding.
*   *Observation:* Literature frequently draws a 1:1 parallel between the Razborov-Rudich (Boolean) barrier and the FSV (Algebraic) barrier, implying that virtually all current algebraic lower bound techniques are doomed to halt at $\mathsf{VP}$ vs $\mathsf{VNP}$ separations without a paradigm shift.
*   *Counter-Force:* The 2024-2025 work by Chatterjee et al. explicitly demonstrates the false-form nature of this broad assumption: "Thus, in this setting of polynomials with small integer coefficients, this provides evidence *against* a natural proof like barrier for proving algebraic circuit lower bounds, a framework for which was proposed in the works of Forbes, Shpilka and Volk" [cite: 21, 27]. 
*   *Action:* The anti-anchor must enforce the conditionality of the FSV barrier, specifically highlighting its dependence on characteristic zero and large/unbounded coefficients, which was not natively scoped in the Boolean RR framework.

### Instance 3: Rank Coordinate Collapse
**Recurrence Type:** Collapsing limits of specific rank methodologies.
*   *Observation:* The informal propagation of "rank methods cannot prove lower bounds," citing works like Efremenko et al. (2018) or Garg et al. (2019) [cite: 28].
*   *Counter-Force:* Deepanshu Kush's April 2026 paper distinctly isolates the *min-partition rank method* for multilinear algebraic branching programs [cite: 14, 15]. This is a fundamentally different coordinate from *border Waring rank*, *completion rank*, or *border completion rank*, all of which possess distinct geometric and algebraic properties (e.g., border Waring rank relates to limits of sums of powers of linear forms, while min-partition rank pertains to set-partitions in multilinear polynomials) [cite: 15, 17]. The substrate must reject the umbrella term "rank methods barrier."

## (d) RECOMMENDATION

Based on the primary source tracking and recent 2024-2026 literature, the following substrate modifications are mandated:

### (i) Assessment of the Candidate Anti-Anchor
The candidate anti-anchor, **Survey OrbitClosureNonMembershipWitness + AlgebraicNaturalProofsBarrier**, is conceptually sound but **needs refinement**. 
*   **Inversion required on GCT dead-end claims:** It must explicitly invert the gravitational well that BIP 2016 killed GCT. It must restrict the BIP negative result strictly to `OccurrenceObstructions`, while simultaneously elevating `MultiplicityObstructions` as valid and actively productive (via Dutta et al. 2025). 
*   **Refinement required on ANP Barrier:** The FSV ANP barrier must be modified to acknowledge the Chatterjee et al. 2025 boundary conditions. It is not an absolute barrier; $\mathsf{VP}$-equations *do* exist for bounded integer coefficients. The true barrier is conditional on both succinct derandomization of PIT and unbounded coefficients in characteristic zero.

### (ii) New Sub-Anchors and Companion Anti-Anchors
The verification process surfaced several critical invariants that mandate distinct registration to prevent coordinate collapse:

1.  **[PRIMITIVE REGISTRATION: IsotypicANPEquivalence Tier-B]**
    *   *Definition:* Any algebraic natural proof against an invariant complexity measure can be assumed, without loss of generality, to be an isotypic metapolynomial (a Highest Weight Vector).
    *   *Source:* van den Berg, Dutta, Gesmundo, Lysikov (CCC 2024) [cite: 13].
2.  **[PRIMITIVE REGISTRATION: MinPartitionRankmABPBarrier Tier-A]**
    *   *Definition:* An unconditional barrier stating that the min-partition rank method cannot prove superpolynomial lower bounds against multilinear algebraic branching programs, due to the $O(1)$ upper bound on balanced-chain set systems.
    *   *Source:* Deepanshu Kush (April 2026) [cite: 14, 15].
3.  **[ANTI-ANCHOR PIN: Multiplicity vs Occurrence Tier-C]**
    *   *Definition:* Explicit structural pin preventing the collapse of representation-theoretic obstructions. Multiplicity obstructions are strictly stronger than occurrence obstructions and survive the BIP 2016 impossibility result.
    *   *Source:* Dörfler, Ikenmeyer, Panova (2019) [cite: 26]; Dutta et al. (2025) [cite: 24].

### (iii) Work-Queue Entries
1.  **[WORK-QUEUE ENTRY: T-ST-T92-1]** Map the exact geometric boundary between border Waring rank and the product-plus-power orbit closure debordering established in Dutta et al. (May 2025) [cite: 23, 24]. Ascertain whether the newly identified multiplicity obstructions scale to separate $\mathsf{VP}_{ws}$ from $\mathsf{VNP}$, or if they remain constrained to the power sum polynomial.
2.  **[WORK-QUEUE ENTRY: T-ST-T92-2]** Formalize the coordinate separation between *completion rank* (NP-hard to compute) and *border completion rank* (NP-hard to approximate) as defined in the context of algebraic natural proofs and generalized matrix completion by Bläser, Ikenmeyer, Jindal, and Lysikov (2018) [cite: 29]. Cross-reference with the bounded-coefficient $\mathsf{VP}$-equations found by Chatterjee et al. (2025) [cite: 21].

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZVICiA01-Gk_iQGRwLsTtHhl2-h0HPFPSPGmIZEQNALImAAVdC-Ibmy8GOpqPFHZxUPaeR08A8m6tQpv2VM83u3yQhhLG0N06guvhkVqfapBxiOw46w==)
2. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNsBO_TTk2WXA9W8HbY3zQ30WZdiP18WlFxHNXWZbSYViRfs_LwbMfSnyoWxVENCFhytU-1gBNuDlBNQ9NDWK_1nCs0rxTN5sfmC2wcj89wpNbPoFPBZBhimxc6gtA-sQ=)
3. [dblp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwywVwsuhjke1T72fK75OEo6aeEkt-rT9SWvb6j5BtrBfgF3Kv8h6BrKnZ8v2m_nR6_t6QTJNlSxXJ_Hs0_JuXIk7GjIb0umhdf-oGJMUMoH7Lcg==)
4. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQZuC4hsOjBPhmcPgBDtxpNRm1blbUykqLqCyT_gDxmEza1P_8WQftFtMYl-BGk12gK6YqGT79YLFeCd8HuLkgaR1HpnXQtvHZwCmJwBxewTGFfsAp4YiT8kFSZd3DWyPiCA==)
5. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEe4RhTl2baQkF_s2qm_hcOqepYBTVh4nw8AhBPjgwpI4i9QBTTe8IY2erB_Jb3PpcaCJ4gVkX6iPzMpTEDSAxmMsSX1DSF1wd3wX2TrLdiToAmrEwlVRJPfHg3QqhPxRgNkiB9xU0J0jQOyu_DyFme3_8MQOahwZxOJS_FmzYiQMdj1-eMsbrZp64HHfX4qQ-OeWSuyr5FZqkYVOnc2En_IDy7Pj3j7URGLRaDvkn88i8_K-ozgvxvOTEr38qDe0UJ)
6. [bitbucket.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFW64AU-3_MHNytaJdO7Gy-ApcqDql4mZhWvbi1DDBfH1gibprSP2ZrJgAYjskkMtM0BXSzqWTTGEAiD0VHKu_sa2HXnaAvRZ9-XvIF24SQGy-NjZj4QdYKP4Oe1ylkvwWR3w8)
7. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGH8kRJtwNz4Nca6TPvw2bFP6526AgXFxTj1MIwvnGfb5DZiqAlNym7W_1mkNMk4J34bK2NSTdXG1kZQBhioWAjru3wyuWwO87rarn_uYn4IckHOZ8lFKuMPib4IHoZyD1uUoxD6LDwU2oyPI8ADRU_-_kScfPlcvISbCY0)
8. [rutgers.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6ODcolVkdM7i-wDDUjf_LXggXqmD7aw4ycMtD1U-bPs-zuqYOkOjcHv7K2kLyDb5eBFEp8b_GcPR9QyWinFGrm_n-sFaTpU-0Wh3A_b__eoTZQmlN_RatprPRWKyIqGGVQV4cOx3tj-x0)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEm3hy3r6NExsgOiLv4ShhRn-dIOxsYcXS_UtnKQRnceidr7tN_Knlo62nr7LltAwqh7oupI-uPQPxL9Ve7k5tLcrChJcLSzFqq3bqYTmztNKeX5ANEvA==)
10. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF75hS3ZAXjNcNNUDfqggGl236YISeJlLK7JzqK0ZADE3-64wChkyDTybsXRSkvtMps3Q9hbNl94bG61JTLnTzOU3BIlwrUxUkhr4RxsGP3MZjlF3riegzX1BIsxWFKtawuzoTonAT4lwAp2imt_gPMK37pMgSzS5ckgubK)
11. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwu9noIzBi4bWPzJcQSJ7BuAjnXpe4yEvER6KCPL5f5XbSntitIjEGvYYVAySfiXpFFW7JbcxUAYrNUR0cH6n9xDwcZ3iqLjtv4KP5Xw2bNKRSY9iZNFlAupILNx_Wx7aOPBQ=)
12. [upenn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIzRaaa0ethg5rkI958w8p3QesFKi5Hl_Z0OR4YfCc9XMFp931v0y0kgW0ljCns8_ay8bCOHZaenv7LeEmF8pwvOf5Cv0bnbOJWRUrLOsWsOBccJlqnQMMr5m4FlJvUN7mnCEizsg=)
13. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHk3_iWGjo_gmzRCSk6sdf242u76H0kTuCTS9FUbWjA4VnTGCD6G5GhiMI6FzKQvZAL6SKvABLNABR7DRRx9DjeBYtGRQCnFnB49YVUNoL_-aQg9kCGoAI2QS_n_EUr44FbKazNmUtEKQcOZ_IpxKn05ulnEE8sfXozzSKYU_qbS7nBXMklxB8GGS1DEULFndWKUE02J-pZcOBBEH69swNk)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXeDruF0P7FkglRiuZVVXW3akebXWaadMkoAAEHVxNXPXqtuXJl_kAMPUUQKMlz1K7B7rqBobL9Skt_dW8IzoS1FatPF7JcRbHFQo1MMaBvIMfuC-wug==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEeSFYP-WfMO23XFWuiT6B1FAgug_2qdriBEIhsP_dQbALAsISuWbOvv91evHIedeeCOHAboqBL409ZFF4Ll1Kp8aC7EPHsPl6u06ejUDu5E-k_DuWgfA==)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_97mWKC2LbytnODI4YW1n2PxAbM524qyRUgRJl7vbeH2xLyXoTLwVQhAdLReit_cEk_PGRt9joBZK9cwZsL8aO0wWQAlG4FCBTrnlbi8oCOJNq9G0rbh4gC2Hdnk4wRr39MerxpgAZr6EHfwpof-IIy2tr5ozAuVoi9t5dD8ha2VStwCnqyGCOjlGtXnZjy_jxLaACOtpgCse-HBkcG4mQ9EceXIzcBlmEhB1lr_tDGwQpqCmXv9UxabMwFI6ZseGplo=)
17. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_xLx6x_TymE9pCw86CwLREgLpc2KG2knZ-3IW4x11CN9wrAHKujdLMKN4nRs56uofuXbpDaImh7wWSjHW1samQLWxyqJciiAin5fVD-Bl2fvUaY2qHuZBfb9uUPeZFunw)
18. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTDrzXRCdpOkc9d5YmB-FNKLgLWgyj-xG8BbXQvJv3sSCgAudYj8xo5arR8EcxYIIW-GA24hDQyykZc1BoHklArIAVGCr0NCi3pIFSUCX-BT8i1Nb4RlHajppO8bOs8NhmrcNisJjOGDAN0vf5sq_UpA==)
19. [claymath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDN-yjmExKzMoYcXhAPEE0BEFUOf5z9xz0gFvMzCNrI6B23DVwIBFIlUM_G60HV0K-yzBPopuhU2amPZziS81qOLVhWYnkPprX5Fuj7hOD7gpS3kR9HML6OrokZZmcmt3E31nBfrZh98hgowAv3pKccVIFwtm7Pev2d2RW)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUta-S0Qt_FoSUaK048cSDXMbe7RS25szkmwAUuYJC3eA-juLXsfAHvGQBwiR9_jtv5HYwSnas14WFILL4KPdO5_1MnlmjO73ge7hQpE_q1u7YLx4nyw==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkE--LER8qlqFfV7hwbD8Le7Z4wlewyWmS_JXPX2iMMWTbr7YiYhOwNFp77hlLEHGdo8mvDPjjxCakuCTV1sN7K3lZLPAEkBIAFozNxv0RHsX0_6i0og==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOFcjUeQErsKztKcQMoMnUCaYdo4E9iob6Co9cMoU5z30-oHIPFw56Kqg8kVjLSAFABk6Py1CaEd-Sv6HAREoeyMxF85d3mfcoakhpXGu47v7nS3r4XiTbCg==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsaNhMZZFNIUO2mJYLkW3xDtVZDmv9smIO3jJTN6XMrIuaD1ceT7DPtJEzZCear5e-xoHOWbrcVUKTzkIZ9lFQp3u0xlwvQ2g2_JZWSgp2qbrS3wqVZw==)
24. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5L50LZCKysQ4lA9DxqWuM9KtGcgsHIfuDE3XU5YkRUHSnTIIpSSV1CBN_jem5fspL2wdtz34y04bdUiatCI7L3nIdpdyoMkVi4P2ZqSmmbcN3evVd8P6NFMAvxjvK0xWnIiHjcumvbyY=)
25. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAIzp38sDH3rvs1KXPFSJEXaMOZwL2LYiOK8Z_1XnLBhJsweQG0gT7MEl9QGX_NZ8EbTVzX8ukrTWRkKRm9dIw0W4lhTPM-ifFwcNaSxVf1z8fCJZo9CiEVbbEFAwaD8ZQnEeCWz_dok8dXl8nPB3vPaKmAK4GSFrhSo_LgZANcBlVOIfaujjt6HCe_4GOiuBXs6XzI77cGsv0EMcO2SCyk0yC2gvrVCdrJpGV6I1Q8jfLMIJ_RR4NxLPixVg_9nyS_qO8HYXvZWPYvfr2th7hbw==)
26. [rwth-aachen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRSKW6n7vNSSHwqyhsABM9eumgkeq7QVD8BYmiD2uxq96nm8dZb6OlSJwRwP0yOS0NE7wrkevPc-JmPrF-3W6kv-6jA5MAF1OxswoH1BG19W1LCLtAYbiKvjk7beI96jOFMrzqOL2Uv5q23MTWMGP_gHSa_G5fF073uDoWIlL564M=)
27. [hpi-web.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0UakF0h0p12irtjfFVklvPH65QRDL7Te9Us8VJnB8kXeEhxXAGUgEkmgAwR95ppJ5Lc94WCDhYwE5BGLCu_PICHHPkGcJUpNm9NpcnM12naF5kKDQapiFglNKuPA=)
28. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLoQnEbE6wCoieoqK6aPvybxHl6cqfnp_Q2mrMJeFqOW-eOVHT2R3xK2I3xVJAHaXzaLMaX6Q6lovZOxTJlgyKwGxypEfGja4EObDVyzCF_1io1ArjAcrDlJig83ZJYqipiBYZTCOVX2NO5NNqOItzxngJIiXZ)
29. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEx2PNKmIHW5hXw679leE23wss9nBaP7AoKVAHaLCxW2ZueT7XHrd0jJCLQHaJuHXOlzH3B-ZxBZMKNk4DMwduHB_m07HAM7mo5opXo65p8OTobOBMihl1dFOjA1GQYGdnK0fvDnO-SPrKnpw==)

