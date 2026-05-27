# Prompt 12: G14 Relation-Strengthening — v2 design audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdVWVVXYW8yOU1iMmNfdU1QcVA2NGtRdxIXVVlVV2FvMjlNYjJjX3VNUHFQNjRrUXc
**Elapsed:** 304s

---

# G14 Relation-Strengthening: Methodologies for Conjecture-Tightening and "Stronger Statement" Discovery

**Key Points:**
*   **Strengthening is fundamentally asymmetric to weakening (G13).** It is not a mere inverse operation; strengthening bounds or predicates introduces extreme fragility to outliers and edge cases, requiring fundamentally different algorithmic guards. 
*   **"Safe strengthening" requires rigorous type-theoretic constraints.** Without semantic subtyping and refinement type guards, automated strengthening frequently generates well-formed but mathematically meaningless statements (e.g., universally quantifying over an empty set). 
*   **Recent mathematical breakthroughs frequently arise from conjecture-lifting.** Published work between 2024 and 2026 demonstrates that testing a strictly stronger version of an existing conjecture can paradoxically provide the structural rigidity needed to either prove it entirely or definitively shatter it via minimal counterexamples.
*   **G14's primary utility may be region-detection.** When a strengthened claim fails at the extremes, it implicitly maps the exact boundary where the parent claim is tight. This necessitates a cross-plugin loop with G16 (anti-anchor) and G18 (minimal-counterexample).
*   **Operationally distinguishing novel mathematics from understated parents is critical.** G14 must include heuristic filters to determine whether a surviving strengthened claim represents a genuinely new theorem or simply indicates that the original parent claim was lazily formulated.

The automated discovery of stronger mathematical statements—often conceptualized as "conjecture tightening" or "predicate lifting"—represents one of the most promising yet computationally treacherous frontiers in automated theorem proving (ATP) and mathematical AI. The proposed G14 Relation-Strengthening plugin aims to walk predicates up the strength ladder, serving as the logical sister to G13 (which relaxes them). However, while relaxing a predicate generally preserves truth values over a wider domain, tightening a predicate drastically increases the probability of encountering catastrophic counterexamples, rendering the claim mathematically void. This report addresses the theoretical, statistical, and architectural challenges of designing G14 v2. By surveying state-of-the-art literature from 2024–2026 on refinement types, statistical robustness, and published instances of mathematical conjecture-lifting, this report outlines a comprehensive framework for safe, robust, and mathematically meaningful relation-strengthening. 

***

## 1. The Typological Foundations of Safe Strengthening

The fundamental risk of relation-strengthening is the generation of mathematically meaningless statements. In automated systems, moving from $\exists x \in P$ to $\forall x \in P$, or bounding a variable so tightly that its domain becomes empty, results in vacuous truths or type-level absurdities. To prevent G14 from producing junk (e.g., "all primes are 2"), the system must rely on "safe strengthening" methodologies grounded in modern type theory, specifically **refinement types**.

### Refinement Types and Semantic Subtyping
Refinement types allow for the specification of a base type constrained by a logical predicate, written as $\{x : T \mid \Phi(x)\}$. In the context of ATP systems and verification-aware programming languages like Dafny or Liquid Haskell, safe strengthening is inherently tied to the principles of semantic subtyping [cite: 1]. For a strengthened predicate $\Phi'(x)$ to be considered a "safe" strengthening of $\Phi(x)$, it must satisfy the subtyping relationship $\{x : T \mid \Phi'(x)\} \subset \{x : T \mid \Phi(x)\}$, while critically maintaining that $\{x : T \mid \Phi'(x)\} \neq \emptyset$.

Recent advancements in verification languages explicitly support methodologies for safe predicate strengthening without breaking modular verification. For instance, the Dafny programming language features a specific `Predicate Strengthening` directive [cite: 2]. This directive allows a refining module to take an existing predicate and safely tighten its body—essentially changing the definition to the conjunction of the original body and the new, tighter constraints [cite: 2]. To prevent this from breaking client modules that rely on the original predicate's preconditions, Dafny restricts this operation to predicates marked as `protected`, ensuring that the strengthened form is contextually contained [cite: 2].

### Well-Typedness and Over-Approximation Minimization
In automated mathematical discovery, a safe-strengthening methodology guarantees that the stronger form is at least well-typed by ensuring the habitation of the newly defined type. For example, when tightening robustness verification bounds in neural networks, researchers must compute the "neuron-wise tightest linear bounds" by minimizing the over-approximation zone [cite: 3]. This guarantees that the tightened linear constraint remains a valid upper/lower bound for the function space without crossing into mathematically impossible geometries. In G14, a "safe strengthening" guard must perform an existence proof (or a fast SAT check) to ensure that the tightened domain is inhabited. If the tightening results in a domain that fails the SAT check, the strengthening is rejected at the type-checking phase before any empirical testing occurs.

## 2. Asymmetry of G13 and G14: The Statistical Fragility of Strengthening

A naive implementation of the G14 plugin would simply invert the logic of G13 (Relation-Weakening). If G13 replaces strict inequalities with non-strict ones ($<$ to $\leq$), G14 would replace $\leq$ with $<$. If G13 expands bounds from $X \leq Y$ to $X \leq Y + \epsilon$, G14 would tighten them to $X \leq Y - \epsilon$. 

This "inverse-of-G13" shortcut is fundamentally flawed. Weakening and strengthening operate under vastly different statistical and logical failure modes.

### The Robustness of Weakening vs. The Fragility of Strengthening
From the perspective of statistical robustness and extreme value theory, weakening a hypothesis increases its breakdown point. If a claim holds for a specific domain, relaxing the bounds slightly incorporates a buffer against numerical noise, outliers, and extreme edge cases. Weakening is an entropy-increasing operation; it creates "safer" theorems that are easier to prove but carry less specific information.

Conversely, strengthening is an entropy-decreasing operation that exhibits extreme fragility to outliers. When a bound is tightened, the mathematical statement is pushed closer to the absolute extremal boundary of the underlying mathematical object. In statistical literature, estimators that attempt to capture exact boundaries (like the maximum of a uniform distribution) are highly sensitive to single anomalous observations. In mathematical conjectures, a single pathological graph or a highly specific prime constellation can shatter a strengthened claim. 

A quintessential 2024 example of this fragility is the resolution of the Bunkbed Conjecture. The conjecture posited a seemingly obvious monotonic behavior in percolation theory (that the probability of a path on the same "bunk" is always greater than or equal to the probability of a path shifting to the upper bunk) [cite: 4, 5]. For decades, partial results weakened the context to make it provable, but the strong original claim was finally proven false by Gladkov, Pak, and Zimin [cite: 6, 7]. They discovered that on a highly specific, massive planar graph with 7,222 vertices, the strict monotonic strengthening breaks down by an astronomically small margin (on the order of $10^{-6500}$) [cite: 6, 7]. 

This demonstrates why G14 cannot operate like G13. G13 can freely step down the strength ladder and broadly sample normal cases to gain confidence. G14, when stepping *up* the strength ladder, cannot rely on average-case sampling. It must employ adversarial, outlier-seeking sampling to probe the extreme tails of the distribution. If G14 uses standard average-case testing, it will falsely promote strengthened claims that are actually false at the extremal limits.

## 3. Conjecture-Lifting in Published Mathematics (2024–2026)

To understand how G14 can be applied productively, it is instructive to look at recent published mathematics where researchers actively engaged in "conjecture-lifting"—taking a known theorem or conjecture and testing a strictly stronger version to yield new findings.

Below is a survey of three major 2024–2026 mathematical papers where strengthening an existing conjecture yielded a significant breakthrough.

### Table 1: Recent Conjecture-Strengthenings in Published Literature

| Original Conjecture/Theorem | Strengthened Conjecture | Authors & Year | What the Strengthening Tested / Result |
| :--- | :--- | :--- | :--- |
| **Truncated Jacobi Triple Product**<br>Guo and Zeng conjectured that the truncated Jacobi triple product series has non-negative coefficients. | **Merca's Stronger Conjecture**<br>Merca (2021) proposed a much tighter, stronger strict bound for the coefficients $q^n$ over specific coprime ranges. | **Xiangyu Ding & Lisa Hui Sun (2024)** [cite: 8] | Ding and Sun mathematically tested this tightened bound, proving it holds for sufficiently large $n \geq N(r,s,k)$. They used partition theoretical methods and the circle method to verify the stronger constraint [cite: 8]. |
| **Tree Unimodality Conjecture**<br>Alavi et al. (1987) conjectured that the independent set sequence of every tree is unimodal (ascends, then descends). | **Tree Log-Concavity Conjecture**<br>The conjecture was strengthened to claim the independence sequence is *log-concave* (a strictly stronger condition implying unimodality). | **David Galvin (2025/2026)** [cite: 9, 10] | Galvin tested the log-concave strengthening using AI-enhanced computational tools. He discovered the strengthening fails; he found a parameterized family of trees that breaks log-concavity at arbitrarily many places, refuting the stronger version [cite: 9, 10]. |
| **Harmonic Measure Decay**<br>Harmonic measures on graphs decay rapidly as the distance from the origin increases. | **Calvert-Ganguly-Hammond Stronger Conjecture**<br>Predicted the exact asymptotic exponent of the least positive value of harmonic measures on $\mathbb{Z}^2$. | **Zhenhao Cai, Eviatar B. Procaccia, & Yuan Zhang (2024/2025)** [cite: 11, 12] | The authors tested the vertex-removal stability on 2D lattices. They successfully confirmed the stronger version of the conjecture, proving the precise exponential decay bounds $[\lambda(G)]^{-n+c\sqrt{n}} \leq M_n(G) \leq [\lambda(G)]^{-n+C\sqrt{n}}$ [cite: 11]. |

In the first and third cases, the strengthened conjecture was proven to be true, providing much tighter bounds and deeper structural insights into the underlying objects (partitions and 2D lattices, respectively). In the second case, the strengthened conjecture (log-concavity) was highly susceptible to edge cases (specifically constructed path-trees) and broke entirely [cite: 9, 10], generating a spectacular counterexample.

## 4. Architectural Specification: G14 v2 Loader Design

To automate the successes observed in the literature above, the G14 v2 plugin must be architected with specific constraints, loaders, and kill patterns.

### (a) Safe-Strengthening Type Guard
Before a tightened conjecture is empirically tested, it must pass a static analysis type guard.
1.  **Semantic Check:** The system extracts the domain $D$ over which the tightened predicate $\Phi'(x)$ applies.
2.  **Habitation Proof:** An underlying SMT solver (e.g., Z3, as used in Dafny environments [cite: 13, 14]) is called to find at least one witness $w \in D$ such that $\Phi'(w)$ is true. 
3.  **Degeneracy Filter:** If the SMT solver proves the domain is empty, or if the solver returns a witness that is mathematically trivial (e.g., the zero vector in a vector space bound check), the strengthening is marked `type_guard_failed` and discarded.

### (b) Mahler-Context Loader
To apply G14 systematically to numeric bounds, we implement a "Mahler-context loader." This is heavily inspired by recent computational work on Lehmer's conjecture (the Mahler measure problem), which posits a strict lower bound on the canonical height of non-torsion points on elliptic curves [cite: 15, 16]. Recent 2025 experiments by Cats, Clark, Dombrowsky, and Orvis tested Lehmer's bounds over massive datasets of quadratic fields [cite: 16, 17, 18]. 

The Mahler-context loader operates as follows:
1.  **Take a PROMOTED bound:** Assume the system has verified a parent claim $X \leq Y$.
2.  **Epsilon-Strengthening:** The loader automatically generates a family of strengthened claims: $X \leq Y - \epsilon$, $X \leq Y/c$ (where $c > 1$), or "X is strictly bounded by Y, not just $Y \pm \epsilon$".
3.  **Adversarial Re-test:** Using the data corpus that verified $X \leq Y$, the loader sorts the empirical data by proximity to the bound $Y$. It then re-tests the $\epsilon$-strengthened claim *exclusively* on the top 1% of data points that were closest to saturating the original bound.

### (c) New Kill Patterns
G14 v2 must feature customized kill patterns to accurately categorize how a strengthening fails, as this failure contains valuable mathematical data.
*   `kill_pattern: strengthening_breaks` (v1 legacy): The claim outright fails globally.
*   `kill_pattern: strengthening_fails_at_extremes`: The strengthened claim holds for 99% of the average-case sample but fails specifically on the adversarial/extremal dataset generated by the Mahler-context loader.
*   `kill_pattern: strengthening_holds_only_on_subset`: The tightened bound fails globally, but the system's decision tree identifies a well-defined topological or algebraic subset (e.g., "holds only for bipartite graphs") where the strengthened claim perfectly survives. 

## 5. Strengthening-as-Region-Detection: The G14-G16-G18 Tripartite Loop

The insight that G14 frequently fails at the extremes (`strengthening_fails_at_extremes`) transforms G14 from a mere "theorem improver" into a highly sensitive **region-detector**. If a parent claim is $X \leq Y$, and the strengthened claim $X \leq Y - \epsilon$ fails, the failure points precisely map the extremal region where the original parent claim is tight. 

This naturally connects to G16 (Anti-Anchor, which seeks to prove that a bound is not just true, but tight/un-improvable) and G18 (Minimal-Counterexample, which shrinks failure cases to their core components).

**The Proposed Cross-Plugin Loop:**
1.  **Phase 1 (G14 - Probing):** G14 takes a verified parent claim $P$ and generates a stronger claim $P_{strong}$. It tests $P_{strong}$ and triggers the `strengthening_fails_at_extremes` kill pattern, outputting a set of complex counterexamples $E$.
2.  **Phase 2 (G18 - Minimization):** G18 receives the set $E$. It applies graph-reduction, algebraic simplification, or topological trimming to reduce $E$ into a set of minimal counterexamples $E_{min}$ (e.g., reducing a 7,222-vertex graph down to the precise structural motif that causes the log-concavity or percolation monotonicity to break).
3.  **Phase 3 (G16 - Tightness Anchoring):** G16 receives $E_{min}$ and the failure differential $\epsilon$. G16 formally uses $E_{min}$ to establish an anti-anchor for the parent claim $P$. It promotes a new meta-theorem: *"The bound in claim $P$ is absolutely tight, and cannot be improved by any $\epsilon > 0$, with the minimal tight boundary represented by the structures in $E_{min}$."*

This loop essentially weaponizes G14's failures, turning the fragility of strengthening into a formal proof of tightness for the parent conjecture.

## 6. The Contrarian Critique: Distinguishing Novelty from Understated Parent Claims

A persistent critique of relation-strengthening is that it often produces "mathematical junk"—not in the sense of being false, but in the sense of being trivial. If a strengthened claim empirically survives G14, there are two distinct possibilities:
*   **(a) Genuinely True Stronger Statement:** The system has discovered a profound, mathematically novel bound (e.g., Merca's stronger conjecture on Jacobi series [cite: 8]).
*   **(b) Understated Parent Claim:** The original claim was lazily formulated. For instance, if the parent claim was "For all positive integers $n$, $n^2 > -5$", and G14 strengthens it to "$n^2 \geq 1$", G14 hasn't discovered a new theorem; it has merely fixed a trivial, understated parent.

When G14 produces scenario (b), the correct architectural move is to **upgrade the parent in place**, replacing the weak statement in the ATP database, rather than promoting the G14 output as a novel discovery. 

### Operationalizing the Distinction
To programmatically distinguish between a profound stronger statement and a trivial upgrade, G14 v2 must measure the **Information Gain** and the **Gradient of the Bound**.

1.  **Gradient of the Bound (Continuous constraints):** If the parent claim was an inequality, G14 evaluates the residual distance between the empirical evaluations and the parent bound. If the average residual is massive and strictly bounded away from zero (e.g., the function evaluation is never closer than 100 units to the bound), the parent was understated. The system automatically shifts the bound to the empirical tightest fit and *upgrades the parent*.
2.  **Information Gain (Discrete predicates):** If G14 lifts a predicate (e.g., from "graph is connected" to "graph is Hamiltonian"), the system checks the known implication hierarchy. If the dataset used to prove the parent claim consisted *entirely* of Hamiltonian graphs by coincidence of the sampling generator, the strengthening is a trivial artifact of biased data. The system must prompt a data-generator module to search for a connected, non-Hamiltonian graph. If it finds one, the strengthened claim is rejected, and the parent is preserved.

By implementing these diagnostic filters, G14 ensures that only structurally profound mathematical strengthenings are promoted as novel discoveries, relegating trivial constraint-tightening to routine database maintenance.

***

### Conclusion
Strengthening a mathematical conjecture is inherently more complex and volatile than weakening it. It requires navigating the extreme boundaries of mathematical spaces where outliers dictate truth values. By implementing a safe-strengthening type guard based on refinement types, transitioning from an inverse-G13 model to a Mahler-context adversarial loader, and harnessing kill patterns to feed a G14-G16-G18 loop, automated systems can safely replicate the high-reward process of conjecture-tightening seen in cutting-edge 2024–2026 mathematical literature. Ultimately, understanding when a tightening breaks—and exactly *how* it breaks—is just as mathematically valuable as finding a tightening that holds.

**Sources:**
1. [sigplan.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsDcuLyMadHKOVtOMQeze9Q6J1nuMDVG228F9sk3ZNP0B-90cifbVQHO5dFwMtf3KY1VSts-qwCKgmOUNRLMonDE_gc6e3heJjeUZ9kVKLFSHtDoDM8JK7GplmjeLLnHA=)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0gbUFGHzmVgzDvOwwPs18rF_JF1c7b6rSft3Yb_XudEDMh2Wqd2greOTKeMfmZUnxho2ME5juCSZntcpGtnYLQRF6RDQfgWpdZvpOL_4SSgeEw5peXZ5Zxi37td3WAyxZVkPIBlyUeksU8rDSU9hg17_QUnyhscQyLaVvO_dIk_ta7EPChQcjV6tfmfA6B11YEVE7)
3. [thecvf.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHU2aXS_i60PgHi06-jAb38pWw8s2d2rZCuTYqXf85IeT5Uxbqwf5jItBVEegtXRTfjqHOokcYKu1FjQMETHJQ5sTOPyOaml6u1JkOM_-yA_hi0vmV8IUHK9P5vcKvAKPVpu9BF3rs=)
4. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxbCbcfGXVK7Tt-hum1lCpUDfU3Fwx6y0AuL4hHGgCacWlo8n_jy-9y2c6NdY-NXx1hxAH2D6rdcNBrGgVZxulPHuqUQ6q_JJT8ni0qQoQNQ6AJPJBxZR7uOyPBXY7YrAvw7mNBg==)
5. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQbbfVKW0Llj9wabe5TX5Au0MhH5UrO3wSCdFd7LYG1QH6cNUZUAADHCkZ1puV9q9wA7eVGgKLoyq_C6C11_fvugCkHmjzDsdQRyMAMyGhv11XG-tIvxI7uP1M-zH2makuf_BYFkISeV3pOyHw4sWXmYif13u0kS9Cm0Gne8-OhpvwT7VauvYc)
6. [pnas.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9G8bFPUIhOEZIIlsDZSLUMHQcx2bSDD7hBnvgcocvgkYin2D-wJEcBaugDCAqawASji-TXZOFww39-pFy5vjnHYdnM4Zu-wc82GcPx3MXeXltnaP_LvIO2OtbaToUdvGjPDI11w==)
7. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiWeLpTcXwjxaSM_XOhdgE9ajQ2OfFWI8Czw8YsFexgYoBFpHT9dI1lIaLP7oyGS7jMCfywocdv2E4sN0R65SNY7Z4de_RjEYhIQvBVe8bCki_g1m4nO5yPDEOJYhHRuWqWE6N4S_Q)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdLO6Viph5_twYz5hjDUM_BrWFLlcxR33Dga5YIoHjq7HXNkjvLexYDELl59m5ldtO2TpscPQOLG1XsP5aQTpsWGz1sRTQL2fPA68L94tvz-joddF1)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2lYMS3KLpCFP4vD3XNvA9625U3z2cAjrm_wxeZt2qy5ilauT6ZNfjUOz_1UhIg2iYn7pgauzcnbspCiMUm6XUOnepJ-uUVw54Y7BCpvI2m9jh5l7Y8hlg)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEa3cIevAMxkC7dhAleIfrqo46NBHDC-JR3y0SSqdYqMHkS8qYIaekm0hDvKbQVFwC1CtwsR6w5rB9U9JU-htG_MBPfZwW6qVin0PdYDOL2PArxgAmdipMI)
11. [sciprofiles.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPqLYJHSKyYytwvBwplupks0oHRQV5eW4vbJimRgBMP0apv43tCmTpx8c1Vkua8xr7DpO1ke-n6SCAMa9f8_0-ub2NsHLeK9Zikyd7XOa_O5VDbO1a6PsMOfjoIw==)
12. [technion.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEa7HnKtnMuU7UqrKjG2AX0901Sf9qbXReNHtQS8Q09VeSPR1_hGtSuyTF5KNLt0zZQvnGT6kaS3JudL-1KGNK3dsrabqIDkKpYoptgTvuVQ_lCxAVROcQIgjPw31qHl7mDTrDqGbY8A_f_fFLYaKmJajuXFi7SguSLlCknINyTo_TSTx3Kb9C7_Jojoj7VClzrwjhvqcAK1ZaziLXSaiS55s-1)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAkL9a4BAhjUxuZlw1CHJSSW0TVIBukTMryQmDsDqrEjGGim3e5qLBoY0lDdUV9H6vjgOcJfk-toj6DELJRi85Vd2TicImmEXwLG2NdrkAbuyRQrYAB5Id)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHo5Ge_U5OVYq6K26q-zteXkSZoR9lRSd2uqTycr7s2tJeSlZe-5Aj5Fvq8os8EfjZr6NPpovHyUzGOJFuZmEebnucLA2C_scfiXYcCuJsW72901DMXrkh0)
15. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGX5lsIc0SPYfSQ-zg_qKuBxBkuYM1EVTdgT-Vm93nKw7knzuh6Y0-gJm0fA5bRyIlDrqSpIOF9NLJocVFOagwR9-TtKam2r-hLv-ocygwKUeqoQFGO9O_8Ch9nZPFP-houxh7F9S0lug==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAxnnZMgpqsMGrBBscE-1W0g5k_adx-QF9YPK0B1o7icehOel3R2POoFtdRby9IZ8KTnrSD2u3pjlq0qvgIcAzpyhwjy7xtsYDD_YLv87rlYA0lMmdEOqh)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9zIuQNtX9aRNOTwI_DIDJV5PGADNClSg-4SBE0h9789ljA3ZoqPq7RgbICblEtakvG09KK2uPYQwguUrJYDW7o4adSc9QoB0rT_UfDKHVUgkUbTrY)
18. [lucant.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEg7x6I3gvqc0OUSpCwo6pYmUF9TGYzk5DfnZoSl3NYW33zbXuUrNRIHAnIynN1N_3h52rBEH0wLiSNAtevK1tEZP9_LcbSGxyqKvxbFZNMuIHRBj0T_EcmIZfDzLJnhHGEGt1i)

