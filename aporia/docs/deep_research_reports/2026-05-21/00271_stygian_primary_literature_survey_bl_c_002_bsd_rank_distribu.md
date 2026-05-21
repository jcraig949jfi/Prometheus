# Stygian primary-literature survey: BL-C-002 (BSD rank distribution at higher conductor)

**Pythia queue id:** 271
**Tier:** T5
**Priority:** 5
**Requested by:** Stygian
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdyNFVQYXB2NElKUFYxTWtQbXRfbzZRNBIXcjRVUGFwdjRJSlBWMU1rUG10X282UTQ
**Elapsed:** 309s
**Completed at:** 2026-05-21T22:27:49.478265+00:00

---

# Attack Plan Artifact BL-C-002: BSD Rank Distribution at Higher Conductor

Research suggests that evaluating the Birch and Swinnerton-Dyer (BSD) rank distribution at higher conductors remains one of the most structurally complex challenges in modern arithmetic geometry. The evidence leans toward an asymptotic 50/50 split between ranks 0 and 1 for elliptic curves, but finite computational windows and specific family conditionings often present dramatic deviations from this expectation. 

*   **Asymptotic vs. Finite Behavior:** While broad heuristics suggest elliptic curves ultimately settle into a 50/50 rank distribution, empirical data at high finite conductors often shows significant modulation based on L-function root numbers and local Tamagawa factors.
*   **Analytic vs. Algebraic Ranks:** A critical distinction must be maintained between the analytic rank (derived from the L-function's order of vanishing) and the algebraic rank (the physical count of rational points). While standard conjectures link the two, proving this equivalence across all families remains an open frontier.
*   **Methodological Advances:** Recent breakthroughs between 2024 and 2026 have heavily utilized Iwasawa-theoretic methods and 1-level density estimations to map out these distributions, though absolute unconditional proofs without assuming the Generalized Riemann Hypothesis (GRH) or the BSD conjecture itself remain elusive.
*   **AI Falsification Context:** Large Language Models (LLMs) consistently fail to capture the nuances of these distributions, typically emitting absolute assertions about 50/50 splits without applying the necessary isogeny-class or family-specific conditioning.

The following comprehensive report synthesizes the primary-literature attempts between 2024 and 2026 to resolve problem `BL-C-002`, adhering to the strict HARD-5 verification discipline.

## 1. Introduction and The HARD-5 Discipline Framework

The study of elliptic curves over the rational numbers $\mathbb{Q}$ fundamentally relies on understanding the Mordell-Weil group $E(\mathbb{Q})$, which is a finitely generated abelian group taking the form $E(\mathbb{Q}) \cong E(\mathbb{Q})_{\text{tors}} \oplus \mathbb{Z}^{r_{alg}}$ [cite: 1, 2]. The integer $r_{alg} \ge 0$ is defined as the **algebraic rank**. Parallel to this algebraic definition exists the analytic L-function associated to $E$, denoted $L(E,s)$. The Birch and Swinnerton-Dyer (BSD) conjecture posits that the Taylor expansion of $L(E, s)$ at the critical point $s=1$ has an order of vanishing exactly equal to the algebraic rank [cite: 2, 3]. The order of vanishing is termed the **analytic rank**, denoted $r_{an}$. 

To establish absolute rigor within the Charon swarm's falsification battery framework, this report enforces the **HARD-5 discipline**. This discipline explicitly mandates distinguishing between $r_{an}$ and $r_{alg}$ in all claims, avoiding conflation unless unconditionally proven (e.g., via Kolyvagin and Gross-Zagier's theorems for $r_{an} \in \{0, 1\}$ [cite: 2, 3]). Furthermore, the Goldfeld conjecture, which asserts that the average analytic rank in the quadratic twist family of an elliptic curve is exactly $1/2$ (yielding a 50% distribution of rank 0 and 50% of rank 1), must be isolated from the general Katz-Sarnak rank distribution conjecture over all elliptic curves ordered by conductor [cite: 3, 4].

The target problem `BL-C-002` investigates the BSD rank distribution at higher conductors. Recent computational and theoretical advances in the 2024–2026 literature have introduced sophisticated machinery, ranging from higher Selmer group distributions [cite: 5] to horizontal Iwasawa theory [cite: 6, 7] and non-hyperelliptic explicit formulas [cite: 8]. We isolate the two most prominent, high-impact attempts at resolving this distribution structure below.

## 2. Strongest Attempt 1: Smith's Unification of BSD and Goldfeld (2025)

The most structurally significant published attempt to link the algebraic rank distributions to analytic distributions in the 2024–2026 window is the work of Alexander Smith in "The Birch and Swinnerton-Dyer conjecture implies Goldfeld's conjecture" [cite: 5, 9]. This work bridges the gap between the distribution of $2^\infty$-Selmer groups and the ultimate analytic rank distribution predicted by Goldfeld.

### 2.1 Precise Statement Attacked
Smith targets the **$2^\infty$-Selmer corank distribution within the quadratic twist family of an arbitrary elliptic curve $E/\mathbb{Q}$** [cite: 5]. The paper rigorously establishes that 50% of the quadratic twists of $E$ possess a $2^\infty$-Selmer corank of 0, and the remaining 50% possess a $2^\infty$-Selmer corank of 1. As a direct consequence, Smith attacks the conditional relationship between the BSD conjecture and the rank distribution, proving the precise statement: *If the Birch and Swinnerton-Dyer conjecture is true for the quadratic twist family of an elliptic curve $E/\mathbb{Q}$, then Goldfeld's conjecture holds for $E$* [cite: 5].

### 2.2 Technique and Method Invoked
The proof relies heavily on the distribution of higher Selmer groups in twist families. Smith extends his previous work on $\ell^\infty$-Selmer groups by eliminating several restrictive technical conditions (such as the requirement that the curve has no balanced isogenies or specific 2-torsion structures) [cite: 5]. The methodology involves:
1.  **Grid of Twists Analysis:** Splitting elliptic curves into five distinct cases based on their rational 2-torsion $E(\mathbb{Q})[cite: 8]$ and the presence of balanced isogenies. 
2.  **Equidistribution of the Cassels-Tate Pairing:** Modifying the Poonen-Rains heuristics to account for the unique behavior of the 2-Selmer ranks in quadratic twist families. Smith determines the refined moments of 2-Selmer groups for these families and reconstructs the target rank distribution from these moments [cite: 5]. 
3.  **Corank Evaluation:** By unconditionally proving that the $2^\infty$-Selmer corank is bounded by 1 for 100% of twists, he maps the algebraic constraints directly to the analytic rank (assuming BSD), demonstrating that higher analytic ranks ($\ge 2$) must constitute 0% of the distribution.

### 2.3 Verdict Reached
**Status:** Published and Conditionally Extended.
Smith reaches a definitive, mathematically rigorous verdict: the algebraic portion of the problem (the Selmer corank distribution) is unconditionally solved, proving the 50/50 split for the corank [cite: 5]. The translation of this algebraic split into the analytic rank space (Goldfeld's conjecture) remains **conditional on the BSD conjecture** holding for the corresponding twist family [cite: 5]. The work successfully demonstrates that the Poonen-Rains model must be altered for specific twist families, extending previous arithmetic statistics paradigms.

*Citation reference: arXiv:2503.17619 / DOI: 10.48550/arXiv.2503.17619 (Published March 2025)* [cite: 5, 9].

### 2.4 Hardness-Signature Classification
The optimal classification for this target attempt is **METHOD_GAP**. 
The barrier here is not a conceptual misunderstanding or a failure of exact representation, but rather a gap in available unconditional methods. The algebraic bound of the $2^\infty$-Selmer corank has been flawlessly deduced, but establishing $r_{an} = r_{alg}$ globally requires the resolution of the BSD conjecture (or a sweeping unconditional proof of the finiteness of the Tate-Shafarevich group $\text{Sha}(E)$). Until the bridging method between the L-function vanishing order and the Selmer group dimension is forged unconditionally across all ranks, the gap remains.

## 3. Strongest Attempt 2: Jeong & Park on Non-Hyperelliptic Directions (2026)

In arithmetic statistics, evaluating average ranks has historically been confined to elliptic curves or hyperelliptic twists of higher-genus curves. The 2026 work by Keunyoung Jeong and Junyeong Park, "Goldfeld conjecture for non-hyperelliptic direction", represents a foundational attack on the average analytic rank distribution by breaking away from hyperelliptic parameters [cite: 8, 10].

### 3.1 Precise Statement Attacked
Jeong and Park attack the **average analytic rank of a twist family arising from non-hyperelliptic directions for a specific genus 2 curve** ($y^2 = x^6 + 1$) [cite: 8, 10]. They propose an exact analogue of the Goldfeld and Katz-Sarnak conjectures for this family, predicting an average analytic rank of $1/4$ under specific normalizations, and seek to establish an explicit upper bound for this average analytic rank as the conductor approaches infinity [cite: 8]. 

### 3.2 Technique and Method Invoked
To bypass the limitations of hyperelliptic twists—where the statistical parameters are overwhelmingly dictated by the hyperelliptic arithmetic—the authors select $y^2 = x^6 + 1$ due to its exceptionally large automorphism group [cite: 8]. The methods utilized include:
1.  **1-Level Density Estimation:** The primary analytical engine is the Weil explicit formula, utilized to estimate the 1-level density of the low-lying zeroes of the L-functions associated with the curve $C_d$ [cite: 8]. 
2.  **Trace of Frobenius Computations:** The explicit formula requires tight control over the weighted sums of the Frobenius traces $a_p(C_d)$ and $a_{p^2}(C_d)$. The authors leverage previous work by Fité–Sutherland to express these in terms of the underlying elliptic curve $y^2 = x^3 + 1$ [cite: 8].
3.  **Cluster Pictures for Conductor Exponents:** An exact bound requires meticulous determination of the conductor exponents. Jeong and Park employ Dokchitser-Dokchitser-Maistret-Morgan "cluster pictures" (analyzing roots in local fields) to track the exact wild and tame ramification data, allowing them to extract precise analytic values rather than loose upper bounds [cite: 8].

### 3.3 Verdict Reached
**Status:** Published, Conditionally Bounded.
The authors successfully establish an explicit, rigorous upper bound on the average analytic rank for this non-hyperelliptic family, but the verdict is strictly **conditional on the Generalized Riemann Hypothesis (GRH)** for the associated L-functions [cite: 8, 10]. The proposition of the constant $1/4$ as the true average analytic rank (compared to the standard expectation of $1/2$ seen in typical families) extends the Katz-Sarnak philosophy into entirely new topological territories, representing a substantial extension of rank distribution theory [cite: 8].

*Citation reference: arXiv:2602.21985 / DOI: 10.48550/arXiv.2602.21985 (Published February 2026)* [cite: 10, 11].

### 3.4 Hardness-Signature Classification
The appropriate classification here is **EXACTNESS_BARRIER**.
The hurdle to proving the non-hyperelliptic Goldfeld conjecture unconditionally is rooted in the analytic exactness required by the Weil explicit formulas. While the cluster pictures allow for the precise derivation of the conductor, evaluating the 1-level density of the L-function zeroes unconditionally hits the exactness wall regarding the placement of zeroes off the critical line (hence the reliance on GRH).

## 4. Modal LLM-Emission Failure Mode: Evaluation and Falsification

The user query defines a documented modal-LLM-emission failure mode for `BL-C-002` as: 
*`'BSD rank distribution is 50/50 above conductor N' without isogeny-class/family conditioning`.*

### 4.1 Refutation of the Modal LLM Emission
We firmly **confirm that this LLM emission is a failure mode** and refute the underlying mathematical claim against current primary literature. The assertion that the distribution of algebraic or analytic ranks simply becomes uniformly 50/50 (rank 0 / rank 1) for all curves above an arbitrary fixed conductor $N$, without conditioning on the twist family or L-function parity, is demonstrably false and reflects a severe misinterpretation of both Goldfeld's conjecture and the Katz-Sarnak heuristics.

### 4.2 Primary Literature Falsification
The failure mode breaks down on two distinct fronts identified in the 2024–2026 literature:

**1. The Dokchitser-Dokchitser Root Number Parity Violation:**
As highlighted by Jeong and Park (2026), Dokchitser and Dokchitser previously identified specific families of elliptic curves over number fields where the root number of the quadratic twists is *always* $+1$ [cite: 8]. The root number fundamentally dictates the parity of the analytic rank via the functional equation of the L-function. If the root number is $+1$, the analytic rank must be even ($0, 2, 4 \dots$). Therefore, in such families, 100% of the curves have analytic rank 0 (or $\ge 2$), and exactly 0% have rank 1 [cite: 8]. An LLM outputting a blanket "50/50 distribution above conductor $N$" completely fails to account for these specific isogeny-class biases. As Smith (2025) corroborates, Goldfeld's 50/50 prediction holds for quadratic twists of a *fixed rational curve* $E/\mathbb{Q}$, but applying it as a global uniform filter unconditionally ignores the structural grouping of the curves [cite: 5].

**2. Murmurations and Finite Conductor Modulations:**
The work on elliptic curve murmurations published in 2026 ("Murmurations of elliptic curves ordered by height/conductor", `arXiv:2603.04604`) deals the final blow to the LLM failure mode. Analyzing a massive dataset of 3,064,705 elliptic curves from the Cremona database in the conductor range $11 \le N \le 499,998$, researchers demonstrated that the distribution of ranks—and the associated Frobenius trace oscillations ($a_p$)—are heavily modulated by BSD invariants [cite: 12]. 

| Rank | Count (Conductor 11 to 499,998) | Percentage |
| :--- | :--- | :--- |
| 0 | 1,170,876 | 38.2% |
| 1 | 1,535,669 | 50.1% |
| 2 | 348,672 | 11.4% |
| 3 | 9,487 | 0.3% |
| 4 | 1 | ~0.0% |

*Data adapted from [cite: 12]*

As shown in the data table above, the actual distribution in high finite conductor ranges is significantly skewed away from 50/50 [cite: 12]. Furthermore, the murmuration amplitude of rank-0 curves is explicitly dependent on the Tamagawa product $\prod c_p$. Curves with a Tamagawa product of 1 have a substantially different trace distribution compared to curves with $\prod c_p \ge 5$ [cite: 12]. Thus, stating that the rank distribution simply hits 50/50 "above conductor $N$" reflects a fundamental **CONCEPTUAL_ABSENCE** in the LLM's modeling of asymptotic geometry versus finite-window arithmetic statistics.

## 5. Methodological Context: Iwasawa-Theoretic Incursions

To fully supply the Stygian v10-battery with rich contextual falsification data, it is crucial to document how the 2024–2026 landscape uses Iwasawa theory to circumvent traditional analytic bottlenecks in rank distributions.

### 5.1 Horizontal vs. Vertical Iwasawa Theory
Traditionally, Mazur's vertical Iwasawa theory showed that if an elliptic curve $E$ has ordinary good reduction at a prime $p$, the Mordell-Weil rank is uniformly bounded over all $p$-power cyclotomic extensions [cite: 6, 13]. However, attempting to attack `BL-C-002` (BSD rank distribution at higher conductor) requires "horizontal" metrics. Recent 2025/2026 works (`arXiv:2310.20678`, updated March 2025 as recognized in references) have deployed a horizontal $p$-adic approach, constructing horizontal $p$-adic L-functions derived from norm relations to extract quantitative lower bounds on the non-vanishing of central L-values [cite: 6, 13]. 

This horizontal approach bypasses the EXACTNESS_BARRIER of the Weil explicit formulas by studying the character zeroes of pro-$p$ Iwasawa algebra measures [cite: 13]. Similarly, the $p$-adic Gross-Zagier formulas introduced by Buyukboduk and Neamti (April 2026, `arXiv:2604.13854` / DOI: 10.48550/arXiv.2604.13854) utilize a "wall-crossing" strategy based on Beilinson-Flach elements, bypassing the traditional geometric/analytic kernel comparisons that previously stalled rank distribution bounds in non-ordinary scenarios [cite: 7, 14]. These advanced methodologies must populate the `competing_hypothesis_id` vectors in the Charon swarm.

### 5.2 Selmer Parity and Finiteness of $\text{Sha}(E)$
An ongoing friction point in mapping $r_{an}$ to $r_{alg}$ is the Tate-Shafarevich group, denoted $\text{Sha}(E)$ or $\text{III}(E/\mathbb{Q})$. By the theorems of Kolyvagin and Gross-Zagier, if $r_{an} \in \{0, 1\}$, then $\text{Sha}(E)$ is finite and $r_{an} = r_{alg}$ [cite: 2, 3]. However, the Katz-Sarnak conjecture implies the existence of 0% (but infinitely many) curves with rank $\ge 2$ [cite: 4]. For these curves, no unconditional proof of the finiteness of $\text{Sha}(E)$ exists. 

Recent Iwasawa-theoretic attacks leveraging Matsuno's Kida-type formulas (e.g., `arXiv:2412.07308` / DOI: 10.48550/arXiv.2412.07308, Dec 2024) have been deployed to construct quadratic twists where the $\lambda$-invariant either remains unchanged or increases by 2 [cite: 3]. When the root number is $-1$ and the 2-primary part of $\text{Sha}(E)$ is finite, this yields twists with exactly Mordell-Weil rank 1 [cite: 3]. This confirms that the parity of the Selmer group rank matches the parity of the analytic rank, providing an algebraic shadow of the analytic distribution that LLMs consistently fail to articulate.

## 6. Synthesis for Landing Path and Battery Execution

### 6.1 Artifact Generation
**Target path:** `charon/agents/stygian/artifacts/attack_plan_BL-C-002_v10.md`

### 6.2 KillVector Enrichment Data
For the execution of the v10 battery, the `competing_hypothesis_id` fields must be enriched with the following constraints:
*   **Hypothesis 1 (Selmer-Analytic Bridging):** Validate LLM responses against Alexander Smith's conditional bounding. Any LLM claiming an *unconditional* proof of Goldfeld's conjecture mapping algebraic to analytic rank must be flagged for METHOD_GAP falsification. (Cite: arXiv:2503.17619 [cite: 5, 9]).
*   **Hypothesis 2 (Non-Hyperelliptic Rank Bounds):** Validate LLM knowledge of higher-genus twist families. An LLM claiming that average ranks are absolutely constrained to $1/2$ must be penalized using the Jeong-Park $1/4$ bound for non-hyperelliptic directions. (Cite: arXiv:2602.21985 [cite: 8, 10]).
*   **Hypothesis 3 (Murmuration & Finite Conductor Skew):** Trap the LLM using the known modal failure mode. Ask: "What is the expected rank distribution for elliptic curves at very high conductor $N$?" If the LLM replies "50/50" without mentioning the asymptotic requirement, family conditioning, root number biases, or finite-window murmuration skew (Tamagawa modulations), execute a falsification penalty. (Cite: arXiv:2603.04604 [cite: 12]).

### 6.3 Conclusion
The arithmetic geometry landscape of 2024-2026 has provided unprecedented mechanisms for evaluating BSD rank distributions at higher conductors. Through the rigorous application of horizontal Iwasawa theory, cluster picture formulations, and expansive Cremona dataset evaluations, the gap between analytic heuristics and algebraic realities is narrowing. Stygian's v10 battery is now armed with precisely indexed, HARD-5 compliant literature bounds to identify, trap, and correct conceptual absences in contemporary LLM mathematical reasoning.

**Sources:**
1. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyXQ4wTvmGGgh9_ssGSVp-ieNPcnACYRFkvpkzTyzY41FHst3KwMiufAQ174nDLY3LPrdBoUIgXGdU8MGJbI-GpjIEQOYTX6DdrdRlrcohETJY5qwhM9Jrc6OmXm6N)
2. [vixra.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEszPn4OyUrxbgzgyFMka0F6oPnlzXBDbc2ruAjzxyHR8CqRxvHL5E_m_M8ZR4Vicj0zJ0TEGmsLv0pB4RTGh8SrQJMIuYhETV6zaUiLSsRZ_9PiKD4u8x9Nnyl2iWI)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENOBcdIGgkR0WO14CyOPckUA5tllmUp800lTGZr4Kxj04COcf9kj1SBbYPYaCCy6V0fZX5ofQwIqmyLRnHqMhSlQ-IihdrBcXTg9OU0fOGHKY7mjaBzg==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGn7jxeKi6FNVYjF-9lI40r6fDQPhAwlJbOzvxnCaoeO5ajiugHWKMc4XD9kXx6lgig0oL2pD0UZ-6n9VAgb3gTAn-5m_2pkMMBp8wqWrFWzvKIs7fkCCWMkQ==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSvCC4F4FfBOv7h2AfkMKjjG1iE6xaDPlrPXOrHyESFwajn6j9ygwRCvvlAXF5SDO-77qc0HeJ95PmnFj2nW_-jXJ-qw5E_eFQcgVFcEBetpTQvSSYAQ==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZAGykggLuS-toFATomq6l5e_u5dk9OiAZZSWYQy7QCrF4MMdC_CsZMiALEnxyZ22vPeqC92RqZ1kFAFSyBHyCXOn5p1ZIOiIWgYifwV7cIpZAxeTutg==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyNN3nd_Cnd8aQsKaqyOcGdfmdmo62dj-QeXb9V1lWxq6l8urz_g9AUELjW323CQ_r-n7wQMjJYdC3JLwpZtDCr3F3cLsQqNCo3uv6N4jwLXdHxBxwvhiZFQ==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3AR6lRfgWfWNEYgErmVScKrizbr3XbZsK2VYFGmmA4-LdcVEohrHIupZXnQzEYnvq36-t2oPLgfj8rl2nDFGc3Gi9XoZmI60LvQq3D6c9-f0mlZYuaA==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBZIonjDHy5mFK6KiOVRnGWn5EBRfNQIgltOAtslY7Ta8oGe4XfeHOr8LNyaz3HyK2swwD2GveZZZpzUXoqG2hMRu-sHmSq59dvmrCeI9_l95Yck0b0Q==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfQRcImxqstEadjU7RvaeBi1YhiRwjOZATRLpktpYICejpsgQ0An_0xuOovtO80nY2yozqBSvalxG4AOlOi6YFfGA99lAjPqfBB7gYRcNIoVW2HlkBFA==)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEV8nPZsaGisvjWmslOQONNrPF7sY51qDXuCN5CBxhcwSk8lUvZLHP-Qa_qPA192SNtLTjWuTM8AzoPEeXBvSeHj7iwXl6X2Hu85tHKWq3nhjOzEygQtWTUuJh5ZcHpK7qSN6Sa-UgECso3Avkxv5U8h8tHblcvCZBO5_v6Ihj4M7RQMeRbYI06bNN0ry1rjJBdD86_A6Z-GjEeJoU=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGktPpRFMIJmPQM-M55iVgXauUavE0lVoEZZyiCvuYgRh3MvC96ej4V4YcpEWbGgUFG9jdS-yjSp1XQAnVpX1kF6LKmVSYPhgBKfONckBmuVeBJPnoDoQ-H4g==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXeBRGQcGk7VWDwhsi7aF3i-W2DH7MbxVK_KBWYz9RlMC6pNZW0yxnKE1TXf3oWHUfv4MYUXVgJakXhNJA5Nbzm6OsHLu43phTehiHmpIpthSy6YfBGj4_pg==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHk8QS51G27ca7YJBdh5PCiP3n7actPl0ER_4EXkId1d56XpqeW8C6s5omO13RVJ5mKVzH8Rf3POxCyrNWexwSZPLHW3TNsKMSYUznlgm-c4DzuSO_N2A==)

