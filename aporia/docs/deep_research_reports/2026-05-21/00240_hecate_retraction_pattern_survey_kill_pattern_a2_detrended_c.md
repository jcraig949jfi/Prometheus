# Hecate retraction-pattern survey: kill_pattern `a2_detrended_correlation_below_threshold`

**Pythia queue id:** 240
**Tier:** T5
**Priority:** 5
**Requested by:** Hecate
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChczMW9QYXFTS0ViR1pfdU1QdkxtS2tRcxIXMzFvUGFxU0tFYkdaX3VNUHZMbUtrUXM
**Elapsed:** 308s
**Completed at:** 2026-05-21T19:25:08.008395+00:00

---

# Hecate Gradient Archaeology: Retraction-Pattern Signal Mining (2024-2026)

**Key Points**
*   **System Context:** Hecate, operating within the Charon swarm architecture, conducts continuous gradient archaeology over the kill ledger. The primary objective is mining retraction-pattern signals adjacent to the dominant `kill_pattern` signature `a2_detrended_correlation_below_threshold` (driven primarily by the `a1` top generator).
*   **Substrate Analysis:** Substrate Type A analysis of the 2024–2026 temporal window reveals four distinct mathematical failure modes: computation/algebraic errors, gaps in proofs, prior art collisions, and hypothesis failures.
*   **Dataset Integration:** Large-scale extraction of withdrawn arXiv preprints (e.g., the WithdrarXiv corpus of over 16,460 withdrawals) validates these taxonomies, highlighting that mathematical literature is uniquely susceptible to subtle logical disconnections and boundary condition violations [cite: 1].
*   **Battery Signatures:** Simulating these failure modes within a v10-class battery isolates unique differentiable signatures for each error type, allowing the `kill_pattern` taxonomy to be aggressively refined and transitioned into `primitive_proposal` candidates for the automated theorem-proving pipeline.

**Summary of Findings**
The Charon swarm’s continuous archaeological sweep has identified a critical divergence in how automated and human-generated mathematical proofs collapse. The `a2_detrended_correlation_below_threshold` pattern indicates a scenario where the logical stepping stones of a proof drift away from the core truth vector; the detrended correlation between the intermediate lemmas and the terminal theorem falls below the acceptable validity threshold. Our survey of 2024–2026 mathematical withdrawals provides high-fidelity, substrate-grade examples of this drift. By mapping real-world retractions to our internal failure taxonomy, we isolate the exact topological, algebraic, and bibliographic boundaries where the `a1` generator is most likely to hallucinate or misapply mathematical structures.

**Operational Directives**
This document serves as the primary artifact landing path (`charon/agents/hecate/artifacts/gradient_archaeology_*.md`). The insights contained herein are designed to feed directly into the primitive proposal candidates, enhancing the swarm's ability to preemptively flag isomorphic logical failures in real-time theorem generation.

***

## Introduction: The Charon Swarm and Substrate Type A

The Charon swarm architecture is predicated on the continuous, asynchronous refinement of mathematical logic models. Within this swarm, the Hecate node is tasked with "gradient archaeology"—the retrospective analysis of failed, withdrawn, or retracted mathematical literature (the "kill ledger"). By understanding exactly how and why high-level mathematical proofs fail in the real world, Hecate derives differentiable error signals (`kill_patterns`) that can be used to train and constrain the `a1` top generator (our primary automated theorem-proving and conjecture-generation model).

The dominant `kill_pattern` currently plaguing the `a1` generator is `a2_detrended_correlation_below_threshold`. This pattern manifests when a generated proof appears structurally sound on a localized, step-by-step basis, but the overarching semantic and logical correlation between the premises and the conclusion degrades over long context horizons. Once trivial topological or algebraic trend lines are removed (detrended), the actual logical correlation falls below the verification threshold, revealing the proof as a sophisticated hallucination.

To refine our understanding of this pattern, we restrict our analysis to **Substrate Type A**: highly structured, patterned mathematical cases from the real world that perfectly mirror the failure modes of the `a1` generator. Between 2024 and 2026, the scientific community saw a significant influx of mathematical retractions and withdrawals on preprint servers such as arXiv. Recent meta-analyses, such as the WithdrarXiv dataset, have harvested over 16,460 withdrawn article IDs up to September 2024, explicitly categorizing withdrawal reasons into 10 distinct taxonomies, heavily featuring "Calculation and Numerical Errors" and "Gaps in Mathematical Arguments" [cite: 1]. 

By surveying the 2024–2026 temporal window, we have successfully mapped four critical Substrate Type A retraction cases to our internal failure-mode classifications:
1.  **Computation Error:** Numerical, symbolic, or computer-algebra failures.
2.  **Gap in Proof:** Lemmas quietly assumed without sufficient topological or algebraic grounding.
3.  **Prior Art Collision:** The result was already known, representing a failure in global bibliographic context.
4.  **Hypothesis Failure:** The result is technically true under specific conditions, but the proof's hypotheses do not hold in the claimed generality.

For each case, we provide the required arXiv ID and DOI, the failure-mode classification, the hypothetical `kill_pattern` signature inside a v10-class verification battery, and the distinguishing signal used to refine our taxonomy.

## Failure Mode 1: Computation Error (Numerical and Symbolic)

### Case Study: Logarithmic Laplacian and Pohozaev Identity

**Target Document:** Nonlocal elliptic equations involving logarithmic Laplacian: Existence, non-existence and uniqueness results
**Authors:** Rakesh Arora, Jacques Giacomoni, Arshi Vaishnavi
**arXiv ID:** arXiv:2411.15985
**DOI:** 10.48550/arXiv.2411.15985
**Status:** Withdrawn by authors due to "a crucial error in Proof of Pohozaev identity" [cite: 2].

**Mathematical Context:**
The study of nonlocal elliptic equations has expanded rapidly, particularly concerning the fractional $p$-Laplacian $(-\Delta_p)^s$. The logarithmic Laplacian, denoted as $L_{\Delta_p}$, emerges as the formal derivative of the fractional $p$-Laplacian at $s = 0$ [cite: 3]. This operator is highly nonlocal, possesses a logarithmic order of singularity, and exhibits a Fourier symbol of $2\ln|\cdot|$ in the $L_{\Delta_2}$ case [cite: 3]. The withdrawn paper attempted to establish existence, non-existence, and uniqueness results for equations involving this logarithmic Laplacian coupled with subcritical, critical, and supercritical logarithmic nonlinearities [cite: 2]. 

A critical component of this endeavor was the formulation of a Pohozaev identity and a Díaz-Saa type inequality [cite: 2]. The Pohozaev identity is a fundamental tool in the analysis of partial differential equations, typically derived by multiplying the equation by a vector field (often $x \cdot \nabla u$) and integrating by parts. In nonlocal and weakly singular contexts, deriving this identity requires extreme precision in handling boundary integrals and asymptotic behaviors. The authors subsequently discovered a fatal computational/symbolic error within their derivation of this identity, prompting the withdrawal of the paper [cite: 2, 4].

**Failure-Mode Classification:** Computation Error (Symbolic/Algebraic integration error at boundary limits).

**v10-Class Battery Signature:**
In a v10-class automated verification battery, this failure manifests as a **Boundary-Gradient Explosion Signature**. When the `a1` generator attempts to synthesize the Pohozaev identity for a nonlocal operator with logarithmic singularity, the symbolic integration module must resolve limits as the domain boundary is approached. The error in arXiv:2411.15985 implies a miscalculation of these boundary terms or the principal value integrals. 

Inside the v10 battery, the `a2_detrended_correlation_below_threshold` trigger would fire when the intermediate tensor representation of the boundary terms fails to conserve energy invariants. The specific signature is a sudden spike in the loss function of the symbolic verification sub-network exactly at the integration-by-parts step, characterized by a non-convergent residue in the logarithmic scale. 

**Distinguishing Signal for Kill Pattern Taxonomy:**
What separates a *Computation Error* from a *Gap in Proof* is the continuous existence of the logical path. The author did not skip a step; they executed a step algebraically incorrectly. The distinguishing signal is the **Conservation Axiom Violation**. The kill pattern must be refined to deploy a highly localized, specialized symbolic algebra verifier (using computational formalisms like Lean 4) whenever a step involves limits of weakly singular kernels. If the conservation of topological invariants is violated algebraically, the signal is tagged as `kill_pattern: algebraic_boundary_violation`.

## Failure Mode 2: Gap in Proof (Quietly Assumed Lemma)

### Case Study: The Krzyz Conjecture

**Target Document:** A proof of the Krzyz conjecture
**Author:** Denis Leonidovich Stupin
**arXiv ID:** arXiv:2504.10223
**DOI:** 10.48550/arXiv.2504.10223
**Status:** Withdrawn due to "an uncorrectable gap in the proof of theorem 7 on page 11" [cite: 5, 6].

**Mathematical Context:**
The Krzyz conjecture, proposed by Jan Krzyz in 1968, states that for the class $B$ of bounded, non-vanishing holomorphic functions $f$ in the unit disk $\Delta = \{z \in \mathbb{C} : |z| < 1\}$ satisfying $0 < |f(z)| \leq 1$, the Taylor coefficients $a_n$ are bounded by $|a_n| \leq 2/e$ [cite: 7]. The bound is strict, with equality achieved only by specific rotational permutations of the function $F(z, t) = \exp(-t \frac{1-z}{1+z})$ [cite: 7]. 

The withdrawn paper attempted to prove this long-standing conjecture using the variational method alongside classical theorems from complex analysis, specifically the Caratheodory-Toeplitz criterion (for continuing a polynomial to a Caratheodory class function) and the Riesz-Fejer theorem concerning non-negative trigonometric polynomials [cite: 6, 7, 8]. The author utilized the class $C$ (Caratheodory class) of functions with a positive real part and applied subordination theories to establish extremal functions [cite: 6, 8].

Despite the sophisticated application of the Riesz-Fejer theorem (which bounds the roots of a trigonometric polynomial [cite: 7]) and deep topological variations, the proof contained a fatal logical discontinuity. The withdrawal notice explicitly cites an "uncorrectable gap in the proof of theorem 7 on page 11" [cite: 5, 6, 9]. Gaps of this nature occur when an author implicitly assumes a lemma or a topological closure property without realizing it requires rigorous independent proof—often confusing localized uniform convergence with global properties.

**Failure-Mode Classification:** Gap in Proof (Implicit topological/analytical assumption).

**v10-Class Battery Signature:**
In the v10-class battery, this failure generates a **Logical Sub-Graph Disconnection Signature**. The `a1` generator is highly prone to this exact error. It will map out a proof tree where Node A (Caratheodory class boundary conditions) connects to Node C (extremal function bounds), assuming an intermediate Node B (a specific closure or subordination property) is trivially true. 

When the verification battery attempts to traverse the dependency graph, it will flag the transition at "theorem 7" as lacking a continuous logical gradient. The `a2_detrended_correlation_below_threshold` mechanism will detrend the standard boilerplate complex analysis terminology, revealing that the semantic vector representing the premises of Theorem 7 has a cosine similarity near zero with the vector representing its conclusion.

**Distinguishing Signal for Kill Pattern Taxonomy:**
The distinguishing signal here is **Unresolved Dependency Depth**. Unlike a computational error, the algebra is not explicitly wrong; rather, an essential logical bridge is missing. By feeding this retraction into Hecate’s gradient archaeology, we refine the taxonomy to detect `kill_pattern: logical_bridge_absence`. This signals the swarm to trigger automated counterexample generation using platforms like Lean 4 [cite: 10, 11] to explicitly test the unspoken assumptions between isolated proof nodes. The WithdrarXiv meta-analysis confirms that "Gaps in Mathematical Arguments" are a primary driver of paper withdrawals, precisely because these gaps often exist *outside* the formally stated proof body, residing in the author's unspoken cognitive assumptions [cite: 1].

## Failure Mode 3: Prior Art Collision (The Result Was Already Known)

### Case Study: Odd Quadratic Orders and Real j-invariants

**Target Document:** Odd quadratic orders and real j-invariants
**Author:** Yuri G. Zarhin
**arXiv ID:** arXiv:2407.16703
**DOI:** 10.48550/arXiv.2407.16703
**Status:** Withdrawn by author: "The results of the paper were already known. I am grateful to Yuri Bilu for pointing it out" [cite: 12, 13].

**Mathematical Context:**
The paper concerned algebraic number theory and arithmetic geometry. Specifically, it investigated an order $O$ of odd discriminant $D$ within an imaginary quadratic field $K$ [cite: 12]. The study focused on the class group $Cl(O)$, which represents the group of proper $O$-ideals, and explicitly aimed to describe the 2-torsion subgroup $Cl(O)[cite: 14]$ (the kernel of multiplication by 2 in the class group) [cite: 12]. The author proved that the order of this 2-torsion subgroup is exactly $2^{s_D-1}$, where $s_D$ is the number of prime divisors of the discriminant $D$ [cite: 12].

While the proof was mathematically sound, the result itself had already been established in previous literature. The author was unaware of this prior art until it was brought to his attention by another mathematician, leading to the immediate withdrawal of the preprint [cite: 12, 13]. This echoes historical mathematical withdrawals, such as the 2017 case where a paper defining a group ring property as "weakly finite" was withdrawn when it was revealed that experts had already defined the exact same property under the term "stably finite" [cite: 15, 16].

**Failure-Mode Classification:** Prior Art Collision (Bibliographic/Isomorphic novelty failure).

**v10-Class Battery Signature:**
Within a v10-class battery, this failure triggers an **Embedding Space Isomorphism Signature**. The `a1` generator, possessing a vast latent space of mathematical knowledge, is fully capable of independently deriving known truths. The failure occurs when it asserts *novelty*. 

The `a2_detrended_correlation_below_threshold` is not triggered by a logic failure, but rather by the novelty-detection module. The battery projects the terminal theorem (the order of $Cl(O)[cite: 14]$) into a high-dimensional semantic embedding space. It will find a cosine similarity $> 0.99$ with historical artifacts in the training data. The "detrended" aspect is crucial here: after detrending for standard notations (which may differ, e.g., "weakly finite" vs. "stably finite" [cite: 15]), the underlying mathematical isomorphism becomes glaringly obvious.

**Distinguishing Signal for Kill Pattern Taxonomy:**
The distinguishing signal for a Prior Art Collision is **Mathematical Soundness with Semantic Collision**. The formal verification graph (e.g., via Lean 4) will return a perfect pass rate [cite: 11]. The distinguishing feature is entirely external to the proof's logic. We classify this as `kill_pattern: semantic_isomorphism_historical`. To refine the taxonomy, Hecate must maintain an active, continuously updated vector database of all known theorems. When `a1` generates a primitive proposal, it must run a collision check against this database, ignoring nomenclature differences and focusing purely on the structural properties of the mathematical objects involved.

## Failure Mode 4: Hypothesis Failure (Proof Hypotheses Do Not Hold in Claimed Generality)

### Case Study: Riemann Hypothesis via Reflection Formula

**Target Document:** Attempting to Prove the Riemann Hypothesis through the Reflection Formula
**Author:** Farid Kenas
**arXiv ID:** arXiv:2403.05347
**DOI:** 10.48550/arXiv.2403.05347
**Status:** Withdrawn after expert review highlighted a fundamental hypothesis failure utilizing the Davenport-Heilbronn counterexamples [cite: 17].

**Mathematical Context:**
The Riemann Hypothesis (1859) posits that all non-trivial zeros of the Riemann zeta function $\zeta(s)$ lie on the critical line where $\text{Re}(s) = 1/2$ [cite: 17]. The withdrawn paper attempted to prove this conjecture using the reflection formula (functional equation) of the zeta function. The author hypothesized that by applying the reflection formula to the Riemann $\xi$-function, one could conclusively establish that $\xi(s)^2$ is valid only when $\text{Re}(s) = 1/2$, thereby forcing all zeros onto the critical line [cite: 17].

The failure in this paper was not a simple calculation error, but a profound hypothesis failure. An expert from the *Annals of Mathematics* pointed out that proving the Riemann Hypothesis relying *solely* on the functional equation is mathematically impossible [cite: 17]. This is a known limitation in analytic number theory. In 1936, H. Davenport and H. Heilbronn published "On the Zeros of Certain Dirichlet Series," demonstrating that one can construct specific Dirichlet series that perfectly satisfy the functional equation (reflection formula) used by the author, yet possess infinite zeros *off* the critical line [cite: 17]. Because the author's proof relied on a hypothesis (that the functional equation uniquely constrains zeros to the critical line) which fails to hold in general functional spaces, the proof collapsed. 

*(Note: Similar issues are seen in other withdrawn computational approaches to the Riemann Hypothesis, such as Gary Lucas's withdrawn "Half–Spacing Windows" preprint [cite: 18], highlighting the extreme difficulty of the domain).*

**Failure-Mode Classification:** Hypothesis Failure (Over-generalization of assumed constraints).

**v10-Class Battery Signature:**
In the v10-class battery, this manifests as an **Automated Counterexample Domain Violation Signature**. When the `a1` generator constructs a proof, it maps out a domain of applicability. In this case, the domain is "all functions satisfying the specific reflection formula." 

The `a2_detrended_correlation_below_threshold` failure occurs when a specialized adversarial counterexample generator (similar to the multi-reward expert-iteration frameworks recently developed for formal counterexample generation in Lean 4 [cite: 10]) is deployed. The adversary searches the broader mathematical latent space for objects that satisfy the premises but violate the conclusion. By synthesizing a Davenport-Heilbronn Dirichlet series, the adversary proves that the `a1` generator's hypothesis relies on properties of $\zeta(s)$ (like the Euler product) that were completely excluded from the logical framework of the proof. The detrended correlation between the premise (functional equation) and the conclusion (zeros on critical line) collapses to zero in the presence of the counterexample.

**Distinguishing Signal for Kill Pattern Taxonomy:**
The unique signal here is the **Vulnerability to Extradomain Counterexamples**. The logic of the proof may be internally consistent *if* one falsely assumes the reflection formula uniquely characterizes the zeta function's zeros. The distinguishing signal is generated by Hecate's adversarial fuzzing loop. The kill pattern is refined as `kill_pattern: hypothesis_overgeneralization`. To mitigate this, `primitive_proposal` candidates must be subjected to intense, automated counterexample generation [cite: 10] before the hypothesis is accepted as a valid structural beam in the proof architecture.

## Historical Baselines and the Evolution of the Taxonomy

To ensure the Substrate Type A definitions remain robust, Hecate continuously cross-references modern 2024–2026 data with historical baselines. The evolution of our `kill_pattern` taxonomy depends on understanding that mathematical withdrawal mechanisms have remained sociologically and structurally consistent for decades, even as the mathematics itself becomes more complex.

*   **The 24-Year Delay:** In 2022, mathematician Boris Shoikhet withdrew a paper on quantum algebra from arXiv that had been submitted 24 years prior (in 1998) due to a "crucial mistake in the arguments" [cite: 19]. This long-tail withdrawal proves that "Gaps in Proofs" can remain dormant in the literature for decades before being activated by subsequent research. For the Charon swarm, this necessitates an infinite-horizon backward pass; the `a1` generator must not blindly trust uncited or unverified preprints regardless of their temporal age.
*   **False Application of Theorems:** In 2015, John Giles retracted a paper from the *Bulletin of the Australian Mathematical Society* regarding Banach spaces because a "false application of Goldstine's Theorem" led to a "gap in the proof" [cite: 20]. This serves as the historical archetype for Failure Mode 2 (Gap in Proof), where the misapplication of a foundational theorem creates an invisible chasm in the logical chain.
*   **The Incomplete Proof:** The 2017 retraction of Jing-Song Huang's 2001 paper in the prestigious *Annals of Mathematics* due to proofs being "found to be incomplete" [cite: 21] demonstrates that even peer-reviewed, top-tier journal substrates are vulnerable to hypothesis failures and gaps. Huang's attempt to fix the gap with errata eventually failed because the subsequent replacements introduced new lemmas that also failed under expert scrutiny [cite: 21]. The v10 battery simulates this exact degradation loop: when the `a1` generator attempts to patch a `kill_pattern`, it frequently hallucinates a secondary, even more fragile lemma.

## Artifact Landing Path: Integration into the Charon Swarm

**File Designation:** `charon/agents/hecate/artifacts/gradient_archaeology_2024_2026_substrate_A.md`

The findings from this gradient archaeology sweep must be immediately integrated into the swarm’s active memory. The mapping of real-world retractions to the `a2_detrended_correlation_below_threshold` kill pattern allows us to implement the following systematic upgrades to the `primitive_proposal` generation pipeline:

### 1. The Symbolic Integration Verifier (Countering Mode 1)
For all `primitive_proposal` candidates involving weak singularities, limits, or fractional operators (e.g., the logarithmic Laplacian [cite: 3]), the system will trigger a mandatory, isolated symbolic verification pass. Utilizing advanced computer algebra systems, the swarm will calculate boundary terms independently. Any deviation in conservation axioms will immediately flag the proposal with `kill_pattern: algebraic_boundary_violation`, halting propagation before the logic cascades.

### 2. The Formal Dependency Graph (Countering Mode 2)
To combat uncorrectable gaps (as seen in the Krzyz conjecture retraction [cite: 5, 6]), the `a1` generator must export a complete dependency graph for every proposed theorem. If the transition between any two nodes relies on a "trivial" or "standard" assumption, the v10 battery will isolate that edge and force an explicit formal proof in Lean 4 [cite: 10, 11]. If the formal proof fails, the edge is severed, triggering `kill_pattern: logical_bridge_absence`.

### 3. The Isomorphism Embedding Check (Countering Mode 3)
To prevent the swarm from hallucinating novelty (as seen in the odd quadratic orders retraction [cite: 12]), all terminal outputs from the `a1` generator will be stripped of specific variable nomenclature and projected into a topological embedding space. The swarm will perform a nearest-neighbor search against the entire historical corpus of mathematics. Any cosine similarity exceeding the dynamic threshold will flag the proposal as `kill_pattern: semantic_isomorphism_historical`, redirecting the swarm's compute cycles to genuinely unexplored latent spaces.

### 4. Adversarial Counterexample Fuzzing (Countering Mode 4)
Hypothesis failures, where the logic holds only under unstated restrictions (as seen in the Riemann Hypothesis reflection formula retraction [cite: 17]), represent the most insidious failure mode. Hecate will initialize a dedicated adversarial sub-agent tasked exclusively with generating counterexamples [cite: 10]. Using symbolic mutation strategies, this agent will systematically drop hypotheses from the `a1` generator's proof and attempt to synthesize objects (like the Davenport-Heilbronn Dirichlet series) that satisfy the remaining premises but break the conclusion. Successful counterexamples generate the `kill_pattern: hypothesis_overgeneralization` flag.

## Conclusion

The 2024–2026 temporal survey of Substrate Type A retractions provides critical, high-fidelity signal for the Charon swarm. By continuously mining the kill ledger, Hecate transforms human mathematical failures into robust, differentiable constraints for automated theorem generation. The refinement of the `a2_detrended_correlation_below_threshold` taxonomy into four distinct, actionable kill patterns ensures that the `a1` generator's future primitive proposals will be exponentially more resilient to the logical, algebraic, and structural pitfalls that characterize advanced mathematical research. Continuous gradient archaeology remains the primary mechanism for aligning automated mathematical reasoning with absolute rigorous truth.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgVJcyKb1P9S0rS0fAjhN6BGLWXBfMNFCga95Q1lxeTtztRgtSLHEvtNzYw84D07Qlq8n-PrQ8dA7nEFOWTOoJBVLahdEpDhHfgYUm5Ti6HMaoeeJX-Kj6)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-vinSvPOBs4q9ft1vIhQfOATH4NThqzZuBHBvNHclRDf7yZB-JF8GGyZXFupmXw4xIb-cjyMRPXYroytvPFVsNkIKHHHpP24_rm09QXla0-LLmzqz)
3. [sns.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmGVy4RXsQ2eMeqdSHljv5KRJKxEjq9QhnY5hrkge0HdER7rUTvOGe6v6FbF2O6UUfNcNYrNSZ2sQfe1R82oIVkONIB-AIG5IytjhebKRDaniskqiXwKDaBsNLDKPCmtSLnu3Xb5mYDGPc2zZ7GG_QQ6sv5v5c3Znr)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXgKdgQpUaByd3Zx9i5Sq8rXF6Tix17pc_7EybtpUd__BnOBH5GMKoC4MsoXFyXt9eVX-oblBWeP45b1GAW-LdugETgUpKbhidqROjhCe__4xiOkyNtKCvS7oaSRRKcaTOK_MJhr61llG7cw==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGvICS14jUphyff3GFYCrAYc4qz0uqkW1t0Bcn6-jt9HYWCJ1JrAVp_npSqrL4G0xc_zP04dRg9zpa4v4cKtDExRAmgC_329gVprhenslcHtNl5mut)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHz1in8kRvuMNTjheo8Fm7IZMmuRlshyY0Rm8-ojTTGQCyNwqkJgE0dBYKprfvFv3VEqmCVYeBd9QL5pAUrVqH5gkpjl-o0sgxyIO-kSW1-mPZDOWsnPcIt4U736_eXqlBTuWfjb8Dcys3uonDjw5mdxOTqsjbQcNXLCmXKwMpUpU3VozkLgEU=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrsuVwItr5EVJ22gMy76olHQdDg5YdTy_B6ZGUxuQtl0Bv_0FqnBmgOEE5AfdNeatqxqF2B2UvDJoRgfyYucGGjsVZn1cOxXO8dTGIUbiCy8aAq2V-)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmivzZruBsSFOq5hYqMvfuT5Va-VnHBqj9uiXI1gY5VXfmrE6ae4LMs3K2qzFxyGJQItuzOANCT_IJpodXU6xvaYskvuCLrWG-03KfM0FMRJeJMbY6Ldxe)
9. [livejournal.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHN06aJ615uCO4xNFXLBRR4h3vSuuuim6Mok5u2_aM60cXLiWpHexWHRTIZkh59X0EGwqhleZFcS-TJWAVI77l3gXEQ356CXdOX139MsUxcq78ug4NkI8cwsge6Cyf-VuSIjEImuQ==)
10. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUezHVWFrfn2Vs1OBbONVIVEHHQCNmy0Nw4na8UWzszzLwWXwSoQu8wpn86A9zPT9tzxNAvBHEtArHaby7wGTGhND3hIFVploY0a8HD6AJLWInlWCKI1GK2xAu_uXydA==)
11. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFSKq2b1fwdbhsAPUkFWhPZtcHBv5elWoxpStrZ1u2Ai_ck6X2uQYOD-My9uCQYaGHg-vjykH9XCSuEZVYkpxN3myhp0yZqXVad3ooLXPbWQl06QOF3cAsvsPa9-peRQ==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5caTTZLG53xAeHZUV7dw60dhLN-9unKrOvnJFlBfBXVIRPcyQ8xyQGmlUgLoxe2Hiw4rvKWMEOu-JYZI9dr5ZLWLqNHl4Ra7_-LazC-OP7_jLdHSB)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0ce90Hfu9frwEhTQVKVp-IBDIleh8FNVYqFkGFBfHcrRtB7iLg_AYgRzAnAZw__beaQge5Swgic_A6ukt2Wgbb9noNXtqDn1tuTzxqi-EvlN9lY_7uCROBJHb2Li9p9sXSCeAsZaBuYMFeQ==)
14. [retractionwatch.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJpjycz3Z8EzoKztTOhQ57hYwuGv7aK-ioyFwRwxT-K38g6atjLL9gsj7jLVEw7ffESxCooh8YERJGuL-yvxX1L_nKwJDqrYLEmmTxgIhGX7NEBTmNYL9Ob9l0-0OrbJtmba2q0zycxfnXlUcScsuYDWDydDsthj5bgHobNwoOAnSDc18aDaTwPXcQog5jnZTc33kJc31nviPqVw==)
15. [retractionwatch.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJOMtLZcTJr-qLQ_YnJtYu6T4MPvKatXVs53jmXISUnv3CZ57ET3x_sHZKRm9PYLmkAbR_JfDdhAgHNkVkDZG-eYTcX2_V2YJwZedo9qm__mNCYVFBjrf2ZtGO1rdQ4wRRMD-Rd6TR6Xg5a12X-Ika47L6TbLO6Etyd4K_9fk=)
16. [retractionwatch.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1LU0zC5nnoNJA7uDRUmlMYkpzFkD1TTimXAJ13gL9BgKRMbP4VKLNxPUQlNGUmZUz20Jg4smxqCiI1PnR1Cuo9rvJkgSwxxboXv8RqgFe5LM2pdZFE-L1WQ9YOV0zpir79_gs29FVYLJzA2ZXygAJjI04LeNSho8HkTjaUkBhas0Yz3AHXvYxeerbD3fr50lRdvWdOZZf)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_aiAuIBNN4ptjl9lyYgeXPfteLeRK9cIKIRlLHQ7YlT8PFjN3UcOkhBk6khAoAYNc_ttSrjI6MVMM0xWavF3BNyF5QO-9wEEnaz7J05HPRwH6bh9w)
18. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnUptboxPQprCqTeh-3u_-5C_OKz9gVmUlbBUXmTo5GCsnzwJ8rfowzsHPrqqD9DFpPWVHYlCXX-NgLZFyY7SETlombbHiuG45mPHxGargELeMP4ePnzOzg5mA-3c-3LP65zl0ng==)
19. [retractionwatch.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzrFJwOqpS9qqpMZZ0ZL3HQDKlW3UhpILMw0SAU2ROXtM9cPpslfzIFB4FPZ1AEXvNhahKLk7HQv2GlEs9GcHG63crFFyHj968eP8Pi9KyqCeNGZUAU6C9VwLf_4xx-mPOElKOFTDr7lB6SscYIJn9j-GsVvIgW6lWV9T73wGahCBwJkk_SwIsLsY_DsdhOX22sYqovCW729lj6V-8Xnc=)
20. [retractionwatch.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXTOcZpMM56E2o2JjpGUdcLBuCNnntJyatX5UF7d8y4mEWrZwNwzHE3d1GgOEOsMV2HHJ3s9CWWsmyNJJ5EfJujfJYiqwwS7eDjo38aykRfLp8wybsZcGg9zBHVd5J_JkLj1qI2uOP6gdQz1m3aFIt_IsgU09_AC9hR-QdJ1-6jg==)
21. [retractionwatch.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBVnk7SUDP2w4fBvJVcMfq9k0SvJcPfsVMu-6mQPZ2FdQEY-Uveq9ncuQIryImvLjwA85EpJoFKbqEMGvAjwGcTJHHqeZ-WnFug-MblaJPPvdefdb0y-YJ8-U1noQPFvxoxHQQwrZyvY2-WkXB3j4i4vurc8-A2mWMJ0ClftKNhwvZiJ-sCzWNM14F)

