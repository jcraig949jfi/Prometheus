# Prompt 04: DR-021 — VERIFY-LIVE T#20 Manziuk-Ventura 2024 minimal border Comon n<=d+1 regime

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdCUzhFYXZld0pOZWFfdU1QdzQ2N2dBURIXQlM4RWF2ZXdKTmVhX3VNUHc0NjdnQVE
**Elapsed:** 1242s

---

# Anti-Anchor Verification Report: Minimal Border Comon's Conjecture ($n \leq d+1$ Regime)

**Substrate Target:** T#20 catalog edit propagate
**Process Context:** VERIFY-LIVE, minimal border Comon $n \leq d+1$ regime, tame/sharp classifications
**Execution Mode:** Substrate Input / Operational Readout

### Key Points
*   **Status of Primary Result:** The candidate anti-anchor derived from Mańdziuk and Ventura (November 08, 2024) is **ANNOUNCED-NOT-PUBLISHED**. It successfully proves the Border Comon's Conjecture for concise symmetric tensors of minimal border rank specifically within the $n \leq d+1$ regime, as well as for all "tame" and "sharp" minimal border rank tensors. 
*   **Distinct Coordinates Imperative:** It is crucial to strictly isolate exact tensor rank from border tensor rank, and symmetric border rank from symmetric smoothable rank. In November 2024, exact Comon's conjecture was explicitly refuted over arbitrary fields for exact rank, creating a massive gravity well that threatens to corrupt substrate representations of the *border* Comon conjecture. 
*   **Downstream Action Required:** The anti-anchor pin `VERIFY-LIVE T#20 Manziuk-Ventura 2024 minimal border Comon n<=d+1 regime` must be registered, but it requires expansion. Substrate inputs must spawn independent primitive registrations for the boundaries between "wild" and "tame" forms, specifically targeting the $n > d+1$ regime as the primary work-queue entry for potential counterexamples.

### Scope of Verification
This verification protocol assesses the primary source claims of Mańdziuk and Ventura regarding the symmetric border rank of minimal border rank tensors [cite: 1, 2]. We cross-reference their findings with 2024-2026 tensor literature to detect subsumption, contradiction, or collateral discoveries, specifically focusing on the algebraic geometry of secant varieties, border varieties of sums of powers (VSP), and unrestrictions.

### Architectural Directives
As per Project Prometheus doctrine, this report resists standard mathematical survey framings. It establishes immutable substrate coordinates, explicitly identifying alternative geometric frameworks (such as concise secant varieties and multigraded Hilbert schemes) rather than accepting scalar-rank collapses. All coordinates are maintained as mathematically distinct invariants.

---

## (a) PRIMARY SOURCE CONFIRMATION

**Source Coordinates:** 
*   **Authors:** Tomasz Mańdziuk and Emanuele Ventura
*   **Title:** *Symmetrization maps and minimal border rank Comon's conjecture*
*   **Identifiers:** arXiv:2411.05721v1 [math.AG]
*   **Date:** Submitted November 08, 2024 [cite: 1, 2]
*   **Status:** ANNOUNCED-NOT-PUBLISHED (Preprint) [cite: 1]

**Context and Substrate Primitive:**
The paper tackles a specialized, highly constrained sub-problem of tensor geometry, serving as a primitive registration for the behavior of concise symmetric tensors. To operate correctly, the substrate must rigidly define the distinct coordinates in play. Let $F \in (\mathbb{C}^n)^{\otimes d}$ be a concise symmetric tensor. The invariant $\underline{\text{rk}}(F)$ denotes the **border rank** (with respect to the Segre variety), while $\underline{\text{rk}}_S(p_F)$ denotes the **symmetric border rank** (with respect to the Veronese variety) of the corresponding homogeneous polynomial $p_F$ [cite: 3]. 

**Primary Claims & Exact Statements:**
The substrate verification pin focuses on the bounded dimension-degree regime where the border Comon's conjecture holds. The primary source establishes the following foundational target:

> **Conjecture 1.1 (Border Comon's conjecture for minimal border rank).** Let $F \in (\mathbb{C}^n)^{\otimes d}$ be a concise symmetric tensor of minimal border tensor rank, i.e., $\underline{\text{rk}}(F) = n$, and let $p_F$ be its corresponding polynomial. Then $\underline{\text{rk}}_S(p_F) = \underline{\text{rk}}(F)$ [cite: 2].

Mańdziuk and Ventura do not prove this conjecture unconditionally for all $n$. Instead, they prove it conditionally within strict operational boundaries. The verification candidate successfully anchors to two major corollaries and one theorem in the text:

1.  **The $n \leq d+1$ Regime Registration:**
    > **Theorem (Corollary 5.4).** If a concise symmetric tensor $F \in (\mathbb{C}^n)^{\otimes d}$ has border rank $n$ and $n \leq d + 1$, then $p_F$ has minimal symmetric border rank [cite: 2].
    
    *Substrate Note:* This strictly improves upon prior bounds (e.g., Buczyński, Ginensky, and Landsberg, who required $d \geq 2r - 1$ without conciseness) [cite: 2]. This confirms the exact anti-anchor candidate text.

2.  **The Tame Tensor Registration:**
    > **Theorem (Corollary 5.5).** If a concise symmetric tame tensor $F \in (\mathbb{C}^n)^{\otimes d}$ has minimal border rank, then $p_F$ has minimal symmetric smoothable rank. In particular, $p_F$ has minimal symmetric border rank [cite: 2].
    
    *Substrate Note:* This requires a distinct coordinate registration for **symmetric smoothable rank** ($srk_S$), emphasizing that the result is routed through the smoothability of the apolar algebra. A tensor is "tame" if its smoothable rank equals its border rank; otherwise, it is "wild" [cite: 2, 4].

3.  **The Sharp Tensor Registration:**
    > **Theorem (Theorem 5.13).** If $d \geq 3$ and $F \in (\mathbb{C}^n)^{\otimes d}$ is a symmetric sharp tensor of minimal border rank, then $\underline{\text{rk}}(F) = \underline{\text{rk}}_S(p_F)$ [cite: 2].
    
    *Substrate Note:* This generalizes the notion of $111$-sharpness (introduced by Jelisiejew, Landsberg, and Pal for 3-tensors) to degree $d$ tensors [cite: 2].

**Methodological Substrate Pins:**
The authors achieve these results not through standard flattening maps (which bound the strictly distinct **cactus rank**), but by constructing a desymmetrizing morphism $\Upsilon$ and a symmetrizing ring map $\pi: S \to V$ (where $S$ is the homogeneous coordinate ring of $(\mathbb{P}^{n-1})^{\times d}$ and $V$ is that of $\mathbb{P}^{n-1}$) [cite: 2]. This algebraic machinery operates on the border varieties of sums of powers ($\underline{\text{VSP}}$), mapping ideals that encode symmetrizations. 

*Conclusion for (a):* The primary source confirms the exact text and bounds of the verification candidate. The preprint remains active and has not been withdrawn or supplanted as of the latest substrate crawl.

## (b) FOLLOW-ON WORK (2024-2026)

The 24-month horizon following the primary source exhibits significant branching. Literature from 2025 and 2026 integrates the Mańdziuk-Ventura boundaries into broader geometrical substrate tools, but refrains from claiming an unconditional proof of the generalized border Comon's conjecture for minimal border rank.

**1. Integration into $GL(V)$-Invariant Lower Bounds (August 2025):**
S. V. Gondi (arXiv:2508.17845, August 25, 2025) explores non-trivial lower bounds for the border rank of $GL(V)$-invariant tensors [cite: 5]. While focusing on Young flattenings (building on Koszul flattenings by Landsberg and Ottaviani, and Wu 2024) [cite: 5], Gondi explicitly anchors to the minimal border rank regime, noting that apart from small Coppersmith-Winograd tensors, few families of concise 3-way tensors are known to *not* possess minimal border rank [cite: 5]. In broader literature reviews (e.g., EmergentMind 2026 synthesis), Gondi's work on Kempf collapsing is directly juxtaposed with Mańdziuk et al. (2024) as defining the boundaries of minimal border rank investigations [cite: 4].
*   *Flagged Claim:* Gondi does not claim to supersede Mańdziuk-Ventura; rather, the follow-on work operates strictly parallel to it, shifting the coordinate focus to representation-theoretic lower bounds rather than symmetric vs. non-symmetric equality.

**2. Concise Secant Varieties and Unrestrictions (April 2026):**
A critical evolution of the substrate occurs with J. Jagiełła and J. Jelisiejew (arXiv:2604.24879v1, April 27, 2026) in their paper *Unrestrictions and concise secant varieties* [cite: 6, 7]. 
*   *Geometric Alternative:* To resist the scalar rank gravity well, Jagiełła and Jelisiejew construct $c\sigma_r$, the "concise secant variety," which serves as a modular partial desingularisation of the abstract secant varieties $A\sigma_r$ to Segre embeddings [cite: 7]. 
*   *Relevance to Candidate:* Every point in $c\sigma_r$ corresponds to a concise tensor of minimal border rank $r$ [cite: 7]. They characterize tensors of border rank $\leq r$ as unrestrictions of minimal border rank $r$ tensors, extending this to Veronese and Segre-Veronese cases [cite: 7]. This 2026 framework provides a completely new operational vector for studying the $n > d+1$ regime where Mańdziuk and Ventura's proof stops. By mapping minimal border rank tensors as universal unrestrictions, Jagiełła and Jelisiejew provide the very geometric scaffolding needed to search for wild points that might violate Border Comon. 

**3. Classification of Small Minimal Border Rank Tensors (2024-2026):**
Work by J. Jagiełła and J. Jelisiejew (preprint 2024, published in *Transactions of the American Mathematical Society*, 2026) titled *Classification and degenerations of small minimal border rank tensors via modules* explicitly classifies minimal border rank tensors for dimension $m \leq 6$ [cite: 4, 8, 9]. Their classification counts isomorphism classes (e.g., 107 classes for $m=5$) [cite: 8]. 
*   *Substrate Impact:* The classification of 1-degenerate minimal border rank tensors provides the empirical dataset against which the Mańdziuk-Ventura criteria (wild vs. tame, sharp, $n \leq d+1$) can be tested computationally.

*Conclusion for (b):* Follow-on work strictly respects the operational boundaries defined by Mańdziuk-Ventura. No author in the 2025-2026 window claims to have resolved the conjecture for the $n > d+1$ wild regime. The mathematical focus has instead shifted to building geometric desingularisations (concise secant varieties) and module-based classifications to handle the complexities of wild minimal border rank tensors.

## (c) FALSE-FORM RECURRENCE

The Project Prometheus doctrine highlights the danger of LLM and human "gravity wells" where distinct coordinates collapse, or where conditional boundaries are eroded over time. A scan of the 2024-2026 landscape reveals two massive, active false-forms that threaten the integrity of this anti-anchor.

**Gravity Well 1: The Exact vs. Border Comon Collapse (CRITICAL)**
In November 2024, roughly contemporaneous with the Mańdziuk-Ventura preprint, a paper titled *Higher rank substitutions for tensor decompositions II: Comon's conjecture* was announced [cite: 10]. 
*   *The Result:* This paper explicitly refutes the Exact Comon's conjecture over infinite fields with characteristic $\neq 2, 3$ [cite: 10]. The authors state: "Theorem 3. There exists a symmetric tensor with $srk(T) > rk(T)$." [cite: 10].
*   *The False Form:* A highly probable recurrence in natural language mathematical synthesis is the assertion: *"Comon's conjecture was refuted in November 2024."* This is a catastrophic coordinate collapse. Exact rank $rk(T)$ and exact symmetric rank $srk(T)$ are distinct coordinates from border rank $\underline{rk}(T)$ and symmetric border rank $\underline{rk}_S(p_F)$. 
*   *Actionable Verification:* The substrate must actively reject any correlation between the refutation of Exact Comon (Higher Rank Substitutions, Nov 2024) and the status of Border Comon for Minimal Border Rank (Mańdziuk-Ventura, Nov 2024). The latter remains true under the bounded $n \leq d+1$ conditions.

**Gravity Well 2: The "Smoothable = Border" Collapse**
Another frequent false-form recurrence lies in the conflation of border rank and smoothable rank, driven by classical vector bundle flattening techniques. 
*   *The Phenomenon:* Flattening maps provide lower bounds for **cactus rank** and **smoothable rank**, which are often treated heuristically as proxies for border rank [cite: 2]. However, Mańdziuk and Ventura explicitly highlight that "wild forms" are precisely those homogeneous polynomials whose smoothable rank is strictly larger than their border rank [cite: 11]. 
*   *The False Form:* Assuming that Border Comon applies universally to all minimal border rank tensors because it applies to tame ones. As noted in EmergentMind 2026 syntheses, "The equivalence [of vanishing Hessian and wildness] fails in the non-minimal border rank regime" and "Minimal border rank tensors may have border-VSPs with distinctive geometry... reducible for wild cubic series $F_n$" [cite: 4, 11].
*   *Recurrence Quote:* In literature abstracts, bounds derived for smoothable rank are occasionally stated generally as "border rank bounds" without proving tameness. The anti-anchor must force downstream agents to request a tameness check before inheriting a symmetric border rank bound.

## (d) RECOMMENDATION

Based on the verification protocol, the substrate operations surrounding T#20 and the Border Comon's Conjecture must be updated immediately to reflect strict primary-source boundaries and coordinate isolation.

**(i) Anti-Anchor True Form Status**
The anti-anchor candidate `VERIFY-LIVE T#20 Manziuk-Ventura 2024 minimal border Comon n<=d+1 regime` is **CORRECT AS STATED**, but operationally insufficient. It needs refinement to explicitly encode the parallel valid regimes (tame, sharp) to prevent false-negative rejections by the substrate.
*   *Refined Anti-Anchor Pin:* `ANTI-ANCHOR: Border Comon minimal-rank validity bounded strictly to [n<=d+1] XOR [tame] XOR [sharp] (Mańdziuk-Ventura 2024). All n>d+1 wild forms unresolved.`

**(ii) New Sub-Anchors and Companion Anti-Anchors**
The primary risk to the substrate is the collapse of distinct coordinates discovered during this crawl. I mandate the registration of the following new constraints:
*   **PRIMITIVE REGISTRATION (HARD-5 Coordinates):** Register exact rank $rk(T)$, exact symmetric rank $srk(T)$, border rank $\underline{rk}(T)$, symmetric border rank $\underline{rk}_S(T)$, smoothable rank $srk_{smooth}(T)$, symmetric smoothable rank $srk_{S,smooth}(T)$, and cactus rank $crk(T)$ as mathematically isolated tensors parameters. 
*   **COMPANION ANTI-ANCHOR (Exact vs. Border Isolation):** `ANTI-ANCHOR: Do not apply exact Comon refutations (Nov 2024 srk>rk) to Border Comon hypotheses. Coordinates are geometrically distinct.`
*   **COMPANION ANTI-ANCHOR (Wild vs. Tame):** `ANTI-ANCHOR: Do not inherit smoothable rank lower bounds as border rank lower bounds without a verified [tame] flag.`

**(iii) Work-Queue Entries**
The findings from Mańdziuk-Ventura 2024 and Jagiełła-Jelisiejew 2026 generate highly specific, actionable mathematical search targets for Prometheus.
*   **WORK-QUEUE ENTRY 1 (Counterexample Search):** Initialize a search routine for a counterexample to Border Comon's Conjecture in the lowest possible unverified regime. Parameters: Concise symmetric tensor $F$, minimal border rank $n$, where $n = d+2$. Focus specifically on $1$-degenerate "wild" forms where the smoothable rank strictly exceeds the border rank, utilizing the concise secant variety $c\sigma_r$ desingularisation mappings from Jagiełła-Jelisiejew 2026 [cite: 7] to compute the border VSP limits.
*   **WORK-QUEUE ENTRY 2 (Ideal Map Extension):** Evaluate whether the symmetrizing map $\pi: S \to V$ (mapping $\alpha_{i,j} \mapsto \beta_j$) and the ideal $I_R \subset S$ constructed in [cite: 2] can be computationally extended using Macaulay2 to wild cubics in $n=5$ ($d=3$, $n=d+2$), specifically checking if $\pi(J_{(d,0,\dots,0)}) \not\subseteq \pi(J_1)$ for all $J \in \underline{\text{VSP}}(F, n)$.

**Catalog Edit Propagate:**
Execute `T#20 catalog edit propagate`. Update the `MinimalBorderRankComonWitness` sub-type to conditionally require `n<=d+1` OR `is_tame == True` OR `is_111_sharp == True` for automated equality assertions between $\underline{rk}$ and $\underline{rk}_S$. Status confirmed and updated based on primary source arXiv:2411.05721v1.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0FXmg1p8uNeb8GZus1acxm1cJp1HhOBO1r5guc66jWKhq6MsrnWl-3nIecUi7CHDpgLBaWiyU_90dMTMdw9JDQyzcoAaCN_sid-hMub1n8ztYPRqIdA==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGETIK9v8PQTMN3w8oE1I68PEPG7SDKTYhvcNYiPT16gdU0ak3EzLWpMnsxp3Hs9PUepThj7QN7mfhfC-MWB3FIysYfzJRdjBpcD5YMwShCiwjledZKhQ==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwrSQmxn0ZCtyhicxYf9I-CjUSin0LFR10D3A-ZVFlVQBqh_VjzUsJfJz5pqx4jdnfYnfXa-hsSWDKoGpq5zxKHmEGgrmXh1Wax3r5B-UmZqDKBi160rgn6Q==)
4. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtL9D62TIVdv2uozY49UwmhDsFobMX9_VZkWEW663HPlLSdYxQbD0NS7WntwKODWPql58xizR02KzPkXzAHxAV2qm3ZVd5cffKQUF8GwNaSQ3JKnOhZOhMpYBUda3hFjQ4Qtn0lrrDe7RKPzuaCjjl8M5y_nU=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEt_Mlve_y24aA0z9yzTpTItcC7FEXCanhSnE60eDm_Ju9WHUsh96Eel02WhoDcUeyM2k5j1rkt25fYlEByiqw5abWIYZ9PywTqND3BaAqt23lSymHizwU3FQ==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoDECBt-Rxetv4bam7DzifcuThgRxm2A9yOeQkvAXvuUX2FEsw8QJu6ySBg9ADBpQzYnsfiK8lP4I-CheDZ5MY0xzuxFbfkxA4pslCzqqWfmbBLBrf2g==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGiA58XISijKC6aoIVtFK1Uhhln7zDGqELbHbL1TQd4ZU29mH09Aby14595yQNT6g8LsNbUjOnt5ZvXxH84rS0OEUlmSF3Khvu8gLdqTS93astdGsHKLQ==)
8. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9QsHeTLUuAP0MO6aISMTIGGxVjl0ov6VPlrbHHjlFMIP54HnR_ub1Jlbf8e9yrfg8S5kHAU_B6qQ5o7lyMq53ic8ExdQcFRqNtIVZ5SMKf0YX1v8otxXqKR6udVgHlgCCAB3D1CVICAEBKGAPJTMxGwTk7QnHx9A_8Q9rsPjcr1J3BZCs4NUncU0QChinSwjZe36YKGMCcemVIQIYPmDjs60MeTExPAj7UO1DJA==)
9. [mimuw.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVcNvstlJ4P0-wvsjTjERWIsRFzuaCh9rNmq4SZp-HZOR9Nl8kEHJyx_WWQwy5Wfuk7yDY89bR2cRFYEnoqPbUau6vZcumE7TwvEDptMXSUqgxAKA65K_zUJaJxPyj48Eb7QmdbkuQTR6G6_S2)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzim1bat2tOsuPcsZD1ignHagRAvvZm8iPOdkDw16gz-GwzbfvHjPKb7RjT6xEXjunNzstauiVvfdXBqluT94PH1Z0HHRoXT4O_kuzy1XMwzcfEJHlRhwsPGi5H4jnAgxoKTg2sGcKA4jOMNF6xmsXS1RRFmcbxxMYWci3BwiGkdvrx5V5B3lgwyEPlJ1Y3z8eu6IlE0ismkFyNa0z3pD3OKWrLR3Jt0DR1nq_ZCYNf6Wf)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7wvl8ZQ9fyhnbi3oEMHa2f5VOtppTXeqndmlBe8eNlLSszbAFB2rAcpXM83GIB0vlWasGrIaA7izHF28PBuo8_kccbojsr68uhWfucg8F8qQZBxVfWe6kbalSKBpdpLQUX6e4wcxxd5V4V1lEM1dxeXofDbLURvlxWMixiL2NG-l-YzJlkxR4IKT8c-XfRPLz3Az--rRH771E)

