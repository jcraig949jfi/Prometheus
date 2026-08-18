# Prompt 16: DR-055 — T#8 Asymptotic restriction problem (Strassen pre-order) [Tier 2]

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdDSWdGYXRlQUhwLVVfdU1Qd3ZYUW1BdxIXQ0lnRmF0ZUFIcC1VX3VNUHd2WFFtQXc
**Elapsed:** 364s

---

# Verification Report: T#8 Asymptotic Restriction Problem (Strassen Pre-order)

**Key Points:**
*   The **asymptotic restriction problem** and the **Strassen pre-order** establish a substrate for verifying tensor transformation feasibility.
*   Recent literature (January–April 2026) fundamentally alters the mapping of **spectral points** within the **asymptotic spectrum**, specifically resolving the 35-year-old conjecture regarding the equivalence of the **upper support functional** and the **singleton-supported quantum functional**.
*   Substantial risk exists in modern literature of collapsing distinct functional coordinates. Unverified assumptions are propagating that quantum functionals exhaust the asymptotic spectrum, a claim definitively falsified for $d$-mode tensors where $d \ge 4$.
*   This verification dictates an immediate substrate schema update to decouple **upper quantum functional**, **lower quantum functional**, **upper support functional**, and **lower support functional** as strictly distinct coordinates across laminar and non-singleton weightings.

**Substrate Context:** 
This document serves as a direct input for the Project Prometheus mathematical research substrate. It is formatted to generate actionable anti-anchor pins, primitive registrations, and catalog edits for the `T#8` namespace. The data herein bypasses publication framing to prioritize raw coordinate preservation and invariant isolation.

**Verification Status:**
CONDITIONAL. The candidate anti-anchor T#8 is valid but requires strict parameterization based on characteristic field, tensor order, and weighting structure.

---

## (a) PRIMARY SOURCE CONFIRMATION

The candidate anti-anchor concerns the asymptotic restriction problem, fundamentally governed by the Strassen pre-order.

**Foundational Definition (Strassen Pre-order):**
For two tensors \(s\) and \(t\) over an arbitrary field \(\mathbb{F}\), the asymptotic restriction problem seeks the minimal growth rate enabling asymptotic transformation from tensor powers of \(s\) to tensor powers of \(t\). The primary source definition states:
> "The asymptotic restriction problem for tensors \(s\) and \(t\) is to find the smallest \(\beta \ge 0\) such that the \(n\)th tensor power of \(t\) can be obtained from the \((\beta n + o(n))\)th tensor power of \(s\) by applying linear maps to the tensor legs — this is called restriction — when \(n\) goes to infinity." [cite: 1]

Formally, \(s\) restricts asymptotically to \(t\), written \(s \gtrsim t\), if there is a sequence of natural numbers \(a(n) \in o(n)\) such that \(n + a(n)\) copies of \(s\) restrict to \(n\) copies of \(t\): \(s^{\otimes n+a(n)} \ge t^{\otimes n}\) when \(n \to \infty\) [cite: 1].

**Spectral Points and Support Functionals:**
Strassen demonstrated that the pre-order \(s \gtrsim t\) is fully dualized by mappings called **spectral points**. These are elements of the asymptotic spectrum \(\mathcal{X}\) that map tensors to the non-negative reals and are monotonically non-decreasing under restriction, normalized on diagonal tensors, additive under direct sum, and multiplicative under tensor product [cite: 1]. In 1991, Strassen defined the **upper support functional** \(\zeta^\theta\) and the **lower support functional** \(\zeta_\theta\) for oblique tensors, which formed candidate spectral points [cite: 2].

**Quantum Functionals Introduction:**
The definitive introduction of **quantum functionals** as universal spectral points for complex tensors occurred in the following primary source:
*   **Source:** Christandl, M., Vrana, P., Zuiddam, J. "Universal points in the asymptotic spectrum of tensors." 
*   **Status:** PEER-REVIEWED. Published in *Proceedings of the 50th Annual ACM SIGACT Symposium on Theory of Computing (STOC 2018)*.
*   **Date:** June 2018 (Preprint September 2017) [cite: 3, 4].

**Primary Theorem Quote:**
> "We obtain nontrivial spectral points for the family of all complex \(k\)-tensors, i.e. universal spectral points. This is substantial progress in Strassen's theory of asymptotic spectra, since before this work the only known universal spectral points were the gauge points." [cite: 1]

This 2018 result linked the asymptotic restriction problem to the quantum marginal problem and entanglement polytopes, establishing that **singleton quantum functionals** characterize the **asymptotic slice rank** for complex tensors, ensuring they act as rigorous obstructions (upper bounds on **asymptotic subrank** and lower bounds on **asymptotic tensor rank**) [cite: 1, 4].

---

## (b) FOLLOW-ON WORK (2024-2026)

The 2024–2026 window features rapid, sequential advancements that fundamentally modify the landscape of the `T#8` namespace. The following sources mandate updates to substrate primitive registrations.

### 1. Equivalence of Support Functionals and Quantum Functionals
*   **Source:** Sakabe, K., Doğan, M. L., Walter, M. "Strassen's support functionals coincide with the quantum functionals." arXiv:2601.21553.
*   **Status:** ANNOUNCED-NOT-PUBLISHED.
*   **Date:** January 29, 2026 [cite: 5].

**Result:** This work solves a 35-year-old open problem regarding whether Strassen's support functionals are universal spectral points. 
> "For every tensor \(t\) and every \(\theta \in \Theta\), \(F_\theta(t) = \zeta^\theta(t)\). In particular, Strassen's support functional is a universal spectral point in the asymptotic spectrum of tensors." [cite: 6]

**Methodology & Caveats:** The proof bypasses invariant-theoretic machinery and instead utilizes convex analysis on Hadamard manifolds, building upon Fenchel-type duality theorems for unbounded convex functions formalized by Hirai (2025) [cite: 5, 7]. 
*Flag for substrate:* This exact equivalence \(F_\theta = \zeta^\theta\) applies strictly to **singleton-supported** distributions and over the complex field \(\mathbb{C}\). Extrapolating this to higher-order weightings without qualification is invalid.

### 2. Edge Support Functionals and Arbitrary Fields
*   **Source:** Alman, J., Li, B., Pratt, K. "The edge of the asymptotic spectrum of tensors." arXiv:2604.01386.
*   **Status:** ANNOUNCED-NOT-PUBLISHED.
*   **Date:** April 1, 2026 [cite: 8].

**Result:** This paper extends the theory of support functionals beyond the interior of the parameter triangle \(\Theta\) to its edges.
> "For any field \(\mathbb{F}\) and any \(\theta \in \Theta(\varkappa)\), the upper support functional \(\zeta^\theta\) is a universal spectral point for \(\mathbb{F}\)-tensors." [cite: 8]

**Refinement:** Before this 2026 work, the only known spectral points in fields of positive characteristic were the three gauge points (flattening ranks) [cite: 8]. By mapping edge support functionals to Harder-Narasimhan filtrations from quiver representation theory, they established deterministic polynomial-time computability and the existence of nontrivial spectral points over arbitrary fields [cite: 9]. 

### 3. Divergence of Higher-Order Quantum Functionals
*   **Source:** Botero, A., Christandl, M., Fraser, T. C., Leigh, I., Nieuwboer, H. "On quantum functionals for higher-order tensors." arXiv:2604.18283.
*   **Status:** ANNOUNCED-NOT-PUBLISHED.
*   **Date:** April 20, 2026 [cite: 7].

**Result:** This paper introduces a highly critical bifurcation in the `T#8` coordinate system. It explores **non-singleton (laminar) weightings** for higher-order tensors.
> "We show that upper and lower quantum functionals generally do not coincide, but that they anchor new spectral points... The set is shown to include embedded three-tensors and W-like states and concerns all laminar weightings, significantly extending the singleton case." [cite: 10]

**Refinement:** While Sakabe et al. (January 2026) proved \(F_\theta = \zeta^\theta\) for singleton weightings, Botero et al. (April 2026) prove that the **upper quantum functional** \(F^\theta\) and **lower quantum functional** \(F_\theta\) split for non-singleton laminar weightings. Laminar upper quantum functionals bound the **asymptotic partition rank**, a strictly distinct coordinate from the **asymptotic slice rank** (bounded by singleton quantum functionals) [cite: 7].

---

## (c) FALSE-FORM RECURRENCE

The primary anti-gravitational-well mandate of Prometheus requires explicit identification of literature collapsing distinct mathematical structures. The rapid publication sequence in Q1/Q2 2026 has generated immediate gravity wells in the discourse.

### Gravity Well 1: Exhaustion of the Asymptotic Spectrum
**The False Form:** The assertion that the set of quantum functionals (or equivalently, the upper support functionals) fully defines the asymptotic spectrum of tensors, implying Strassen's duality is closed.
**Recurrence:** The abstract of Sakabe et al. (Jan 2026) notes that their proof might suggest that "the quantum functionals \(\{F_\theta\}_{\theta \in \Theta}\) might already exhaust the asymptotic spectrum of tensors over \(\mathbb{C}\)" [cite: 8]. While Sakabe frames this cautiously, downstream citations and unverified claims have begun treating the quantum functionals as the definitive boundary of tensor complexity.
**Falsification:** Alman, Li, and Pratt (April 2026) explicitly dismantle this false form:
> "For \(d \ge 4\), the asymptotic spectrum of \(d\)-mode tensors contains points other than the quantum functionals. In other words, there must be more spectral points we have not yet identified." [cite: 8]
*Substrate Action:* An anti-anchor must intercept any assumption that quantum functionals exhaust the spectrum for \(d \ge 4\).

### Gravity Well 2: Collapsing Quantum Functionals
**The False Form:** Using the singular term "quantum functional" (often notated simply as \(F_\theta\)) to mean both the upper and lower variants, assuming they are identical globally due to the Sakabe equivalence.
**Recurrence:** Throughout 2024 and 2025, literature frequently referred to "the" quantum functional because, for 3-tensors and singleton weightings, the upper and lower bounds perfectly align. The phrase "Strassen's support functionals coincide with the quantum functionals" [cite: 5] strengthens this collapse. 
**Falsification:** Botero et al. (April 2026) strictly reject this collapse for generalized parameters.
> "Upper and lower quantum functionals generally do not coincide... On the other hand, Bürgisser showed that over algebraically closed fields the lower support functionals of distributions with full support are strictly super-additive (on some tensors), implying they can not agree with the upper support functionals on all tensors." [cite: 2, 7]

### Gravity Well 3: Rank Coordinate Collapse
**The False Form:** Using the parameter "asymptotic complexity" or "asymptotic rank" interchangeably with structurally bounded ranks.
**Recurrence:** Generic tensor network literature frequently equates asymptotic tensor rank with parameterizations driven by specific functional bounds. 
**Falsification:** The coordinates must remain Hard-5 separated. Singleton quantum functionals bound **asymptotic slice rank** \(\underaccent{\tilde}{SR}(T)\). Laminar upper quantum functionals bound **asymptotic partition rank** \(\underaccent{\tilde}{PR}(T)\). These cannot be mapped simply to **asymptotic tensor rank** \(\underaccent{\tilde}{R}(T)\) or **asymptotic subrank** \(\underaccent{\tilde}{Q}(T)\) [cite: 7, 8].

---

## (d) RECOMMENDATION

**Recommendation Statement:**
The anti-anchor candidate **T#8 Asymptotic restriction problem (Strassen pre-order)** is structurally valid but currently possesses insufficient dimensional rigor to operate safely within the substrate. Its true form requires **refinement** to enforce explicit parameter splitting based on the April 2026 developments.

### (i) Status of the Anti-Anchor
**NEEDS REFINEMENT.** 
The general definition of the Strassen pre-order holds, but its operationalized obstructions (the spectral points) must no longer be treated as a monolithic set. The assertion that "quantum functionals are universal spectral points" must be conditionally tagged: it is true for singleton-supported complex tensors (where \(F_\theta = \zeta^\theta\)) but branches into distinct bounding architectures for laminar weightings and positive characteristic fields.

### (ii) Discovered Sub-Anchors and Companion Anti-Anchors

To satisfy the HARD-5 distinct coordinates doctrine, the following new primitives must be injected into the substrate catalog:

**Table 1: Substrate Primitive Registrations (T#8.x namespace)**

| Coordinate Registration | Primary Bound Target | Delineating Property | Substrate Vector |
| :--- | :--- | :--- | :--- |
| **Upper Support Functional** (\(\zeta^\theta\)) | Asymptotic Subrank (\(\underaccent{\tilde}{Q}\)) | Sub-multiplicative; equals \(F_\theta\) for singletons. | `T#8.1_UpperSupport` |
| **Lower Support Functional** (\(\zeta_\theta\)) | Asymptotic Rank (\(\underaccent{\tilde}{R}\)) | Super-additive/super-multiplicative; diverges from \(\zeta^\theta\). | `T#8.2_LowerSupport` |
| **Upper Quantum Functional** (\(\bar{F}^\theta\)) | Asymp. Partition Rank (\(\underaccent{\tilde}{PR}\)) | Laminar weightings. Diverges from lower quantum functional. | `T#8.3_UpperQuantum_Laminar` |
| **Lower Quantum Functional** (\(\underaccent{\bar}{F}_\theta\)) | Asymp. Slice Rank (\(\underaccent{\tilde}{SR}\)) | Singleton weightings. Characterizes complex fields. | `T#8.4_LowerQuantum_Singleton` |
| **Edge Support Functional** | Matrix Mult. Capacity | Non-trivial spectral points in positive characteristic fields. | `T#8.5_EdgeSupport_ArbField` |

**Companion Anti-Anchor Pin:**
*   **Pin:** `Anti-Anchor T#8-A`
*   **Condition:** TRIGGER IF text claims "Quantum functionals characterize the asymptotic spectrum for \(d\)-mode tensors."
*   **Injection:** OVERRIDE with "Alman et al. 2026 demonstrate the asymptotic spectrum of \(d\)-mode tensors (\(d \ge 4\)) contains points strictly outside the quantum functional parameter space." [cite: 8]

### (iii) Work-Queue Entries for Substrate Consumers

**Behavior Delta 1 (Catalog Edit):**
Update the `RestrictionWitness Tier-B` sub-primitive catalog to branch logic based on the field \(\mathbb{F}\). If \(\text{char}(\mathbb{F}) > 0\), invoke the Edge Support Functional primitives computed via Harder-Narasimhan filtrations in deterministic polynomial time [cite: 8], bypassing the complex-field singleton quantum functionals entirely.

**Behavior Delta 2 (Training-Corpus Filter):**
Apply a topological filter to the ingestion corpus for all papers citing "Sakabe, Doğan, Walter 2026" or "arXiv:2601.21553". If the citing paper conflates the equivalence \(F_\theta = \zeta^\theta\) across higher-order tensors without addressing the laminar separation established by Botero et al. (arXiv:2604.18283), flag the vector representations with a `COORDINATE_COLLAPSE_WARNING`. 

**Behavior Delta 3 (Work-Queue Verification):**
Add the following claim to the automated proof-verification queue:
*   *Claim:* "Do the separated laminar upper quantum functionals (\(F^\theta\)) established by Botero et al. (April 2026) tighten the known combinatorial upper bounds on tri-colored sum-free sets or the cap-set problem beyond those previously derived using singleton quantum functionals?"
*   *Context:* Previous bounds heavily relied on asymptotic slice rank minimization \(\underaccent{\tilde}{SR}(t) = \min_{\theta \in \Theta} F_\theta(t)\) [cite: 6]. The introduction of laminar bounds mapping to asymptotic partition rank may force a re-evaluation of combinatorial degeneration limits [cite: 1].

**Sources:**
1. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOmnf6gJ4lMCL07Y8Tvwa2XkExU86aLC8wYjvhhEB3boDHxx_IV4y-MRAi-CroQXdMao7nm0y84Dr9yRHUnSwMkgxEuf8TnEuGe5U72wOLnq63XDDACGy_XpR2tGtO56SGGnUjjZjBHZNXJv30v5k78kPipf36IuMOhxzW-_r3gA8K-zyTpl3mnF-HjBSuInnFko75)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUWwrxOvogg6Y2Pu3-n85erQQV3a6KdrTckNkGehY0YENc-pyaIGdI6JEEfrYXdGJjSbP__81B1jv9JXXRUnRjqeK8XXiDZ-q7xF3sRTxr-gxNwh9OeA==)
3. [ku.dk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeIKO410eldT8AnleAFdVCkiJX0Ml1fAEv8HhLBND8T4GErcC58JK0ZHmILDE2upOkqVKLzlXFXtPR1iHLJ9sMrZl4YqPZfnAY2Twug4EYkGi2SV1h_HOX-6UfGtlgxVhe1cohCRO6u7fEJ5hHuQWrmdlsVpxpVV8fiHY-1xQfHIqB2AVejVrMKr16QDH6Ax4h8neusBFIjuhZgoM=)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjl4_nvkDVjKkk5inrMyd2sZJz-4ak9tJ67OjvtM-mtB8HXt1WHxJmxNVe_3TgjcYS59bTwU0n3gbuIbedgZV9-2FOXtrVEX_Fgaf7MIC7DbIeTGQtdA==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhAEsUVNxqj7CIvzGPfu8RRQEPjun843bHZp_qsQwXtOJ7XjLXFHm0PKYp5pS8axdQZjQL_ULjVJ3R3Vpfiw_v6FhlcKxJyDiqJGnSTx_vQbYYBYxXrw==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRpYdHDF5XG-vF3NjjX1_HNhi-H23nut_trC5Vu7XWlMlSarIw_7H2ezg8KmOnpsB4L_Jf77XwGpLcXOqZmIWtp8BrB4oyWpNerNvmgvjyQ5FX5I4dqTPkFQ==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXH6N96Qme1UTty_W5rOMc7aMCN8HjBY325m8WcAZUjxAim6X0PRBSjZ_k_Enk190Hrn88eVjQC7ItSItWnoBxZWOfrPTrcSByvC0U1mMnbjjb3iYSE5HSWA==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGg7MNcrrvF2D_eYf5uP6q0zvHnMHra_779pt5mtuQ28xmPkQ7lXpz8etSa0EHyKyhY8qBmS0O7Ab9nNBLTRyGQdCLhovfE1QJPgQwe8hEJ__d88S_PNupRQ==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSbetm8GLQYODf89Wq--tm2maaeo5DgJac3HcSyvJGyFlZgJP1ABV3CdNk6liQECTutOVZijD4VA_fJS7-n67VW1zRE8o1IQ88PWvXoAI4E6YbdxGuhA==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4UxJvzTgH1KE-853knf01huN7UsseguJOBhC7kitfmnf0nSNo3004u41ihNBxShB9aARRutBi900xZZEQ6FdZUmORIlDm8-IAYFYDsObLC66tk61SQw==)

