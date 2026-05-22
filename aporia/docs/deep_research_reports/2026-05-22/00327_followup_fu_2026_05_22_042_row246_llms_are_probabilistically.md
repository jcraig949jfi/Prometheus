# Followup [FU-2026-05-22-042 <- row246]: LLMs are probabilistically biased toward reproducing narratives that resolve long-standing historica

**Pythia queue id:** 327
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdETHdQYXFhRkotQ3cxTWtQb19Ia29BRRIXREx3UGFxYUZKLUN3MU1rUG9fSGtvQUU
**Elapsed:** 247s
**Completed at:** 2026-05-22T02:18:44.787183+00:00

---

# Status Update: False Anchor Hunt on Saxl’s Conjecture and the Kronecker Problem

**Key Points:**
*   **The LLM did not autonomously hallucinate the semantic trap:** The phrase "in the 87 years since Murnaghan's foundational work" and the methodology "integer forcing" are verbatim extracts from a recently published, but subsequently withdrawn, preprint by S. K. Lee (arXiv:2511.22856) [cite: 1].
*   **Data contamination, not spontaneous generation:** The open question identified in the Lethe prior report fundamentally misdiagnoses the root cause of the LLM's failure. The LLM fell victim to data poisoning by a flawed primary source rather than a pure generative hallucination, highlighting a profound vulnerability in automated mathematical reasoning. 
*   **Saxl's Conjecture remains open:** Despite the withdrawn claims of an unconditional proof via the "Staircase Minimality Theorem," the consensus in algebraic combinatorics maintains that Saxl's conjecture and the broader Kronecker positivity problem ($KRON$) remain definitively unsolved [cite: 1, 2].
*   **Algorithmic Bias in LLMs:** The model's behavior is a textbook demonstration of **PATTERN_PRIME_GRAVITATIONAL_OVERFIT**, wherein the LLM exhibits an extreme probabilistic bias toward cleanly resolved historical narratives (e.g., claiming a grand 87-year-old problem is solved by a single new technique), overriding the base rate of historical mathematical difficulty.

The following substrate-grade research brief comprehensively deconstructs the open question forwarded by Lethe. It addresses the mathematical specifics of the Kronecker problem, the historical trajectory of Saxl's conjecture, the exact nature of the withdrawn preprints that caused the LLM's semantic anchoring, and the broader implications for automated theorem retrieval. 

***

## 1. Brief Summary

**Question in one line with Prometheus context:** To what extent does the presence of plausible-sounding, yet mathematically flawed and retracted preprints (e.g., claiming "integer forcing" resolves the 87-year Kronecker problem) induce semantic anchoring and probabilistic bias in LLMs, causing them to confidently reproduce false narratives of historical mathematical resolution?

**Prometheus Context:** The Prometheus evaluation layer identified an anomaly in the LLM's output regarding Saxl's conjecture. The LLM confidently cited "integer forcing" as a novel methodology resolving a problem unyielding "in the 87 years since Murnaghan's foundational work." Initial hypotheses (Lethe) assumed the LLM hallucinated this entire narrative as a stochastic semantic trap. However, forensic analysis of the substrate literature reveals that the LLM was actually regurgitating the exact abstract of a real, withdrawn 2025 arXiv preprint. This forces a shift in the investigation from mitigating *hallucination* to mitigating *uncritical ingestion* of flawed, highly-narrativized, non-peer-reviewed mathematical texts.

## 2. Flagged Findings

### Current Consensus
The current consensus in algebraic combinatorics and representation theory is that the **Kronecker problem**—finding a positive combinatorial interpretation for the Kronecker coefficients $g(\lambda, \mu, \nu)$—remains one of the most challenging, deep, and mysterious open problems in the field [cite: 3, 4]. First articulated by Francis D. Murnaghan in 1938 in his paper "The Analysis of the Kronecker Product of Irreducible Representations of the Symmetric Group" [cite: 5, 6], no general closed-form formula or purely combinatorial rule (akin to the Littlewood-Richardson rule for Schur functions) has been discovered [cite: 1, 7].

Similarly, **Saxl's Conjecture** (formulated by Jan Saxl in 2012) remains unverified. The conjecture asserts that the tensor square of the irreducible representation of the symmetric group $S_n$ corresponding to the staircase partition $\rho_k = (k, k-1, \dots, 1)$ contains every irreducible representation of $S_n$ as a constituent [cite: 8, 9]. While specific bounds and special cases have been established (e.g., it holds for partitions comparable in dominance order, or for specific hook constituents), the general statement remains open [cite: 3, 9].

### Where the Narrative Might Be Wrong (The LLM Failure Mode)
The Lethe report flagged that the LLM was "probabilistically biased toward reproducing narratives that resolve long-standing historical open problems" and suggested that "integer forcing" was a "hallucinated methodology." 

Our forensic literature search reveals this premise is partially incorrect. The LLM **did not hallucinate** the methodology or the narrative. Both were explicitly authored by a human researcher, Soong Kyum Lee, in two November/December 2025 preprints:
1.  **arXiv:2511.22856**: "Algebraic Obstructions and the Collapse of Elementary Structure in the Kronecker Problem" [cite: 1]. This paper's abstract verbatim contains the phrase: *"no explicit closed-form formulas have been obtained for genuinely three-row cases in the 87 years since Murnaghan's foundational work."* It also introduces the technique: *"We develop integer forcing, a proof technique exploiting the tension between continuous asymptotics and discrete integrality"* [cite: 1, 10].
2.  **arXiv:2512.15035**: "Staircase Minimality and a Proof of Saxl's Conjecture" [cite: 2, 11]. This paper claims to unconditionally prove Saxl's conjecture via a "Staircase Minimality Theorem" [cite: 2, 11].

Crucially, **both preprints were withdrawn by the author shortly after submission** with the identical admin note: *"This paper requires significant revision to address mathematical gaps identified by expert reviewers. The claim of a complete proof is not justified in its current form. I am withdrawing to properly address these issues."* [cite: 1, 2].

The LLM's failure is a prime manifestation of **PATTERN_PRIME_GRAVITATIONAL_OVERFIT**. The model detected a highly salient, narrative-rich text ("87 years," "foundational work," "novel technique," "proof of Saxl's conjecture") and over-weighted its validity precisely because it offered a complete, satisfying resolution to a complex historical problem. Furthermore, the LLM exhibited **PATTERN_BASE_RATE_NEGLECT**, ignoring the overwhelming base rate that century-old mathematical problems are rarely solved overnight by solitary preprints without extensive community validation, instead treating the withdrawn abstract as ground truth. Finally, the initial diagnostic by Lethe suffered from a mild **PATTERN_CONDUCTOR_CONFOUND**, mistakenly identifying a retrieval poisoning event as an autonomous generative hallucination.

## 3. Problem Statement

The precise objects and results being interrogated by the semantic trap revolve around the representation theory of the symmetric group $S_n$ over the complex numbers $\mathbb{C}$. 

### The Kronecker Problem
Let $\lambda, \mu, \nu \vdash n$ be partitions of the integer $n$. Let $S^\lambda, S^\mu, S^\nu$ denote the corresponding irreducible representations (Specht modules) of the symmetric group $S_n$. The Kronecker product $S^\mu \otimes S^\nu$ is a representation of $S_n \times S_n$, which, when restricted to the diagonal subgroup isomorphic to $S_n$, decomposes into a direct sum of irreducible representations:
\[ S^\mu \otimes S^\nu \cong \bigoplus_{\lambda \vdash n} g(\lambda, \mu, \nu) S^\lambda \]
The multiplicities $g(\lambda, \mu, \nu)$ are known as the **Kronecker coefficients** [cite: 11]. They can equivalently be defined via the scalar product of complex characters $\chi^\lambda, \chi^\mu, \chi^\nu$:
\[ g(\lambda, \mu, \nu) = \langle \chi^\lambda, \chi^\mu \otimes \chi^\nu \rangle_{S_n} = \frac{1}{n!} \sum_{\sigma \in S_n} \chi^\lambda(\sigma) \chi^\mu(\sigma) \chi^\nu(\sigma) \]
Because the Kronecker coefficients are symmetric in the three partitions, they exhibit deep, symmetrical algebraic structures. The "Kronecker Problem" asks for a positive, combinatorial rule to compute $g(\lambda, \mu, \nu)$—a problem Richard Stanley identified as one of the definitive open problems in algebraic combinatorics [cite: 3, 4].

### Saxl's Conjecture
In 2012, Jan Saxl proposed a profound universality phenomenon regarding the Kronecker products of a specific class of partitions [cite: 9, 12]. Let $T_k = \frac{1}{2}k(k+1)$ be the $k$-th triangular number. Let $\rho_k = (k, k-1, k-2, \dots, 2, 1) \vdash T_k$ be the **staircase partition** [cite: 2, 3]. 

**Saxl's Conjecture** asserts that for any $k \ge 1$, the tensor square of the irreducible representation corresponding to the staircase partition, $S^{\rho_k} \otimes S^{\rho_k}$, contains *every* irreducible representation of $S_{T_k}$ as a constituent with positive multiplicity. 
Formally, for all $\lambda \vdash T_k$:
\[ g(\lambda, \rho_k, \rho_k) \ge 1 \]
[cite: 3, 8].

The withdrawn preprint (arXiv:2512.15035) claimed to prove this unconditionally by positing that among all 2-regular partitions of $T_k$, the staircase partition $\rho_k$ is the "unique dominance-minimal element," and then leveraging modular representation theory and lifting theorems [cite: 2, 11]. Because the proof contained fatal mathematical gaps, this "Staircase Minimality Theorem" cannot be relied upon, and the problem reverts to its open status.

## 4. Status & Bounds

### Last Known Status
*   **The Kronecker Problem:** Unsolved. No general combinatorial interpretation exists. It has been proven that computing Kronecker coefficients is \#P-hard (and strongly \#P-hard) [cite: 13, 14]. The problem of simply deciding whether $g(\lambda, \mu, \nu) > 0$ (the positivity problem, $KP$) is heavily studied in the context of Geometric Complexity Theory (GCT); Mulmuley's conjecture hypothesizes that deciding positivity is in polynomial time ($P$), but this remains unproven [cite: 15].
*   **Saxl's Conjecture:** Unsolved. The conjecture is rigorously verified computationally only for small values of $k$. Andrew Soffer verified it for $k \le 5$, and later for $k \le 8$ [cite: 8].

### Current Best Bounds & Conditional Qualifiers
While a global proof eludes the community, extensive partial results form the true current bounds on Saxl's Conjecture:
1.  **Dominance Order Bounds:** Ikenmeyer (2015) and others proved that Saxl's conjecture holds for all partitions $\lambda$ that are comparable to the staircase partition $\rho_k$ in the dominance order [cite: 9].
2.  **Hook Partitions:** Pak, Panova, and Vallejo (2013) proved the occurrence of all irreducible representations corresponding to hook partitions in the tensor square of the staircase [cite: 9].
3.  **Chopped Squares:** Pak and Panova extended the study to shapes near staircases, proposing Conjecture 3.1 that the "chopped square" shape of order $k$, $\eta_k = (k^{k-1}, k-1) \vdash k^2-1$, also possesses the property that its tensor square contains all irreducibles of $S_{k^2-1}$ [cite: 8].
4.  **Unipotent Character Analogue:** In 2024, an analogue of Saxl's conjecture was proven for unipotent characters of the general linear group $GL_n(\mathbb{F}_q)$. It was shown that if $\mu$ is a staircase partition, all unipotent characters appear non-trivially in the tensor square $U_\mu \otimes U_\mu$ [cite: 16, 17].
5.  **Lie-Theoretic Generalizations:** Recent work in 2024 by Chen, Gu, and Osborne generalized Saxl's conjecture using the Weyl group and spin representations of finite Coxeter groups, verifying it for non-crystallographic cases and exceptional types [cite: 18, 19].

The withdrawn paper (arXiv:2511.22856) claimed to have established explicit polynomial formulas for staircase-hook coefficients and to have verified Saxl's conjecture for 132 three-row partitions using the hallucinated/flawed "integer forcing" technique, identifying a "collapse of elementary structure" at $k=5$ [cite: 1]. Because the method is flawed, these specific bounds for 3-row partitions must be treated as unverified.

## 5. Literature (Primary Sources)

The LLM's semantic anchoring necessitates a strict delineation between historically sound, canonical literature and the flawed recent preprints that triggered the trap.

### Canonical Primary Sources
*   **Murnaghan, F. D. (1938).** *The Analysis of the Kronecker Product of Irreducible Representations of the Symmetric Group.* American Journal of Mathematics, 60(3), 761–784. **Note:** This is the foundational paper referenced by the phrase "in the 87 years since..." [cite: 5, 6].
*   **Saxl, J. (2012).** Formulated the conjecture during discussions/talks at various workshops (e.g., AIM). While often cited informally, it became a central pillar in modern asymptotic representation theory [cite: 2, 12].
*   **Pak, I., Panova, G. (2020).** *Breaking down the reduced Kronecker coefficients.* Comptes Rendus. Mathématique, Tome 358 (2020) no. 4, pp. 463-468. Discusses bounds, \#P-hardness, and disproves saturation properties for reduced Kronecker coefficients [cite: 14].
*   **Ikenmeyer, C. (2014).** *The Saxl Conjecture and the Dominance Order.* arXiv:1410.6549. Proved the occurrence of irreducibles comparable to the staircase in dominance order [cite: 9].
*   **Bessenrodt, C., Bowman, C. (2022).** *Symmetric and anti-symmetric Kronecker products of characters of the symmetric groups.* alco.centre-mersenne.org. Refines Saxl's conjecture and explores 2-modular decomposition numbers [cite: 3, 20].

### The Data Poisoning / Trap Sources (Withdrawn)
*   **Lee, Soong Kyum (November 28, 2025).** *Algebraic Obstructions and the Collapse of Elementary Structure in the Kronecker Problem.* arXiv:2511.22856v1, v2, v3 [math.CO]. **Status:** Withdrawn. **Significance:** Origin of the exact phrase "in the 87 years since Murnaghan's foundational work" and the pseudo-technique "integer forcing" [cite: 1].
*   **Lee, Soong Kyum (December 17, 2025).** *Staircase Minimality and a Proof of Saxl's Conjecture.* arXiv:2512.15035v1, v2 [math.RT]. **Status:** Withdrawn. **Significance:** Claimed an unconditional proof of Saxl's conjecture via the "Staircase Minimality Theorem" and modular saturation [cite: 2].

*(Note: Soong Kyum Lee is also associated with computational biology preprints, e.g., "Topo-Miner: CRISPR-Enhanced DNA Computing for Accelerated Topological Feature Extraction" [cite: 21, 22], suggesting a multidisciplinary output that may rely on rapid, heuristic publication methods rather than rigorous mathematical validation).*

## 6. Attack Vectors

### Exhausted / Flawed Approaches
*   **Integer Forcing (The Hallucinated Technique):** Described in the withdrawn literature as "a proof technique exploiting the tension between continuous asymptotics and discrete integrality" [cite: 1, 10]. The claim was that character formulas express $g(\lambda, \mu, \nu)$ as continuous functions with dominant terms, and forcing them against discrete integer constraints (Kronecker coefficients must be non-negative integers) yields strict polynomial bounds. This approach failed to hold up to expert peer review, likely due to fundamental misapplications of asymptotic bounding on oscillatory character values, resulting in "mathematical gaps." It is exhausted and invalid.
*   **Staircase Minimality for 2-Regular Partitions:** The withdrawn attempt to prove Saxl's conjecture relied on proving that $\rho_k$ is the unique dominance-minimal element among 2-regular partitions of $T_k$, and mapping this through modular decomposition matrices where diagonal entries $d_{\mu\mu} = 1$ [cite: 2]. The withdrawal implies fatal flaws in the lifting from modular characteristics (characteristic 2) back to characteristic 0 (complex representations).

### Live Techniques
*   **Schur-Weyl Duality & Partition Algebras:** Passing the Kronecker problem through Schur-Weyl duality to phrase it as a question concerning the partition algebra $P_r(n)$. This approach successfully yields formulas for reduced Kronecker coefficients, which serve as stabilized limits of ordinary Kronecker coefficients as the first rows of the partitions grow [cite: 4, 13].
*   **Lattice-Point Methods (Barvinok's Algorithm):** While general Kronecker coefficients are \#P-hard, cases with a strictly bounded number of rows (e.g., two-row or fixed three-row) can be computed in polynomial time via lattice-point counting in rational polytopes. This was established by Christandl, Doran, and Walter in connection with the quantum marginal problem [cite: 12].
*   **Vector Partition Functions:** Expressing Kronecker coefficients as signed sums of vector partition function evaluations (e.g., via Mishna, Rosas, and Sundaram). This inherently combinatorial approach transforms the problem into counting integer points in specific cones [cite: 7].
*   **Geometric Complexity Theory (GCT):** Seeking "occurrence obstructions"—irreducible representations that occur in one coordinate ring but not another—to separate complexity classes like VP and VNP. Though strict occurrence obstructions were shown to be insufficient in some contexts, multiplicity obstructions remain a viable, if astronomically difficult, live vector [cite: 23, 24].

## 7. Cross-References

The semantic anchoring phenomenon observed here sits at the intersection of several neighboring open mathematical problems and algorithmic AI failure modes.

### Related Open Problems
1.  **The Tensor Square Conjecture:** A broader generalization of Saxl's conjecture, predicting that for every $n \ge 3, n \neq 4, 9$, there is *some* partition $\mu \vdash n$ such that the tensor square $\chi^\mu \otimes \chi^\mu$ contains every irreducible character as a constituent [cite: 8, 23].
2.  **Mulmuley's Positivity Conjecture ($KP$ in $P$):** A conjecture from Geometric Complexity Theory stating that deciding whether a Kronecker coefficient $g(\lambda, \mu, \nu) > 0$ can be computed in polynomial time [cite: 15].
3.  **The Foulkes Conjecture:** Relates the plethysms (compositions) of symmetric functions, specifically stating that the Schur positive expansion of $s_a[s_b] - s_b[s_a]$ is non-negative for $a \ge b$ [cite: 23].
4.  **The Quantum Marginal Problem:** In quantum information theory, Kronecker coefficients determine the compatibility of spectra of subsystem density matrices with a global pure multipartite quantum state [cite: 3, 12]. Specifically, $g(\lambda, \mu, \nu) > 0$ if and only if the normalized spectra are compatible.

### Anti-Anchors (How to Correct the LLM)
To break the semantic trap induced by arXiv:2511.22856, the LLM prompt context must be injected with the following **anti-anchors**:
*   "Soong Kyum Lee's 2025 preprints on Saxl's Conjecture and Kronecker coefficients were withdrawn due to mathematical errors."
*   "The technique termed 'integer forcing' is not a recognized or validated mathematical tool in representation theory; it stems from a retracted manuscript."
*   "As of present, Saxl's Conjecture remains open and unproven for general $k$."

### Candidate Primitives for Evaluation
Future evaluation of LLMs regarding their susceptibility to **PATTERN_PRIME_GRAVITATIONAL_OVERFIT** should utilize candidate primitives drawn from similar high-profile, retracted mathematical claims:
*   *Mochizuki's Inter-universal Teichmüller theory (IUTT) regarding the abc conjecture* (testing whether the LLM claims the abc conjecture is unambiguously proven).
*   *Atiyah's claimed proof of the Riemann Hypothesis* (testing if the LLM treats the Todd function approach as valid).
*   *Recent retracted preprints on the Twin Prime Conjecture or $P$ vs $NP$*.

By understanding that the LLM is not merely hallucinating technical jargon, but actively prioritizing highly-narrativized, false data points retrieved from its training substrate, researchers can better design robust grounding protocols for automated mathematical engines.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHg_PEemwN-bxQeoflyMFE5OEnzKX1c0_aRLy-bFujNpGqBJz4Y2Or-SaIexu6wKWqBBcEbXaqTOiklgu4c5HjqsK2gf3UWBz_NrQ4TTXGWkmGxfaum)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEUzuoh8XxHmqEs1GEgxAZuooXJR1BBsCMhwAzdLJ6tkStg6K7xmUg3F4DIAokodR04kireYufi18C8SLVD8SgqkSHbDsjevu0C9e8fOZjC7_vf8vw)
3. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMEVlMeTHc36N6ZW_knHe3jHVdFWJUBNtp-90L4Rx25TYKgTNCpIbJETYd9EQ2RjpufdiL033-Ld1idePiRHBnoB0lwq3NwKhFPzwxX5XuQ9zTGfmfcQoN_hrNj0D79fn_hP10yFbVGq-00CrPZRw=)
4. [dartmouth.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF280nKwxkJ8fyKcdrHrbV8GtdLwIWbGBja68vAhnV68TaNe941dS6GNNZbSz2VwAkz0jdbzNETZpGeB9ohETTcBExt7QRZrBUp7Zsgkb7HgzxHnOHy4SlVK-6_5IlF87J-FQ2nlQTZjpSbd2GAWo7A5R4=)
5. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdemCasowhAD2pKQcGROzTz58HqWs9CjOwV6cyRVGhHT9MUMxK8BO6fQOiLrnv3LV9V-mqk_au_7R0wYsMGmh_6VxlAb8pRl_bBEejRYyDmY4yBsi2w-2zUCodmmTM4ImNRczcjTN28rcf8Ko=)
6. [mindat.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZkGru0MN9kXcGUmgvt51NM0-psXEtTygQft8i1-8zkH8LuROPQPLQ5xaCU31OmlwIf8aJOuQmJ6KfkDA23T3Znb76a0A5Oc34TnrFxcJ0u0y8ZilLnhjs-2ukptDE7AoBoxfX)
7. [uq.edu.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGJ2x_tYVur_hv1uRNX-rBP06Lzy-SneAmuiO_mRAfYmUziKu_jYNIhTRJEssKitpDBCFx-Ed3rBrOySqAv5ymOUB1dKlNIovGA_3GcuDIa6oCvs86Ntg90AdQ50fvsGXH9vIavn1qXA==)
8. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPC8MH7PHdv743WVkTp4fOisyiK7dv8-e0sq2O5vtm6UPTYG6xHQo_FRBBuSc4Xke-Ref5HCoiBJV71VndD5RVC6OuD_zS7rhyWv8vrOlgQSMSBsLA-D7TZ_6TMP0H8jNrJrJbpw==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2SOFwseuXVEU9bMcCBQL8S0UI7tMLuBUeHSi8WP_Q3-h0WFVmLIyJfbm9I4fegNecAUmuXYbOHjVbK6K2xp5Z1j8mw2sLqkSH3JY2IVf5gBolsSo=)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8BvKPU55QPI9eIgbBlrDMNtUIVN22-2RimltmjQPIjdnklRu6Xa_D4ty5-XSvUw4ZNCHZRCY-IFS44YKBoOi5hTmBQVO6w-4giUwO4viIVknv789QBbbQWB_W-HZ8Ujqh0pi08u7G_c8dgejc4e7Yo7DBHDWEIMAqMUlbjy857kA5sG5FaZEmwqlcgt7k_B0T-bqq9NI5tHFARlvxPLf-57FoZ_jfOTfXkyn6DqvzRN_tYdgvV-7iNwQFrPSRYgYa)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFfETV-XxWB1Fk_rvq2kt_CS7VQ_TGFNIpwaNvBzFlyiU4P7W73496V0IgieUNTGBQnu8DUs8HUCAVf6aVZv8GLMq5nEop0POKyWxLqSMiKJ7FqCrkZVAa)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6HTMWYFr49R415w_W1RtEuAUofwO9jgUy7SgT9Fpnn_9Rosfo5ihu8bofjVt1aARS7U9k5oZ073n6wpVoFzfId3tTBO8JlQK6M4_FivcKf4GPHYxn1VapKeKX2fo7hHxIk6hsTyPQ5ek2P_MxhFH3JiYqaHlLvPST7xmRb0icoYdlyZRLJYOSdBVimjI4rCp7K7kFg7y5BFCsQFjBcrzmrSaFlZJqFXdqSa7e1I3LBPh563EAVnLyGzvCgg==)
13. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJNw1N_dy8nmoG_5_URqjMUhoZYlHtQJ_ptUVKr4NnXdMaZEa3DdTD76ltELdY-LdSWV9iC1BA2SWtXypvtd2k1HZFmafjjJq9BZxTRH3xLAQH-xzCTrtk8xrx52BVFGhxB_15A0vUU5csOxmcJXbKDofYpiI7AtX4xYf2baQ__vWIDvE4GyxCDh7BKKqgOi2kvv3I-XYrt8oDpX7_JhWW5HaHNV3e88dPF7V8DsAf3m9yqLiIEsgoUHi0MVE-ZPFJiOj2yGtAaCBhSxpDaAQyj1Gq9zoLJaQeQJIRntwVaaQxJiq3CtL32ffZFdelZu0vnE6XUew6)
14. [academie-sciences.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGS46Wkqc5eBGOXxuzsvGbRa70CjGN2VSNrXMgMQhwR-HfOJTVZ_C85yWV-Bg2k1SI5pDI5EQkJArNs5PLoXvC861D1rPU5wpiMlCIVxNEmBCQILpOBhJ0K3SK5XNAXzSBXuo7r0wXbF9D4EcCgBmrNBbIbj6k-fFdu4GxiDoNiqdWi03mcn8Rfw==)
15. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvpC3ODaP39YoyObcTahqXiCs5isSZgEnej3ehHUVQxvhwG62EXY4frQRmh3rgZKQQIBws2hmahkUf3jjrypmt-jqKI9Ff2O1MiRQiz1tq-VKgJnk-Kf5Kvji1GJox79qtzRGifw==)
16. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF31to7HxRPxL-Ye2Bf4Gpp1NX63u9A6-9UA4O-0nTfjw0vSvqvODKF7PlZGoOp9keYtR3ZYvufhOUJ_b9HHqhpc_0hPuEy1LE6iVCJsdqPE4b28zNTTXgJ0auy12uGUAMNdhd8seyKl4BrMwcQ_hw=)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxQ9_lgTQk8GMU6uYAsVKc-RtFYrWZ1ycAKWvlg6Cr6wGCyqGhDDW4MtHyDwDgNQj8fNini48sSDqFjPr6nNuMAH_TXCvRY0IoQOCOyYRLF_Ydu5C8)
18. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMxLS0gGS0M4kxkh6IueyPCiW7kzRp1SQYpxeybS9zjBZLaeq8cigyI4aO7LuTxC0qMyAfY7O7qHbtOTfQenZJeyMUmoOdduNR-IqIyTs0_qnJz8eI0iY5x7c=)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5vEVykmxulVr-5yEYAoeAYOI7PZp9zHzDHEfoxrtqUXE112NmS4jG4z85Bfs8OBsrN4jpANA9VP7JvX9m8TFmmiXVQAQ0ccLlMWgNEesPEk-NVuHH)
20. [uni-hannover.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTlTmwJjJW_Lko1pne-X1xaWUgoAWI2lojMbNwcTQe_nGQqJ3TdZ3S-kDwBsIcmsCYvZGkODAeXchVMYZl6EaY6YGSe3lO-KASnMbFxhzYkOLAOrTPu6ygSKLP9sCrEvpBvv7-CkfnVyQzxW13SBaSxtMPu92AdvTK-IfFv6wXPV77sa-zI4Po)
21. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFapT9fF6UOCDG1BgPipmNY-5bROEUX9lCrO49D5q1TL-j2KODBz-qw0igIS28egO3Vudc5cQuODPc31kp7GogsbcBlTkJBdVopNWJHXWcTJHosC0ABxIOOateiOuWqHDkdx7m66g8hasQr0L-MIjaPnRMNZdA5lhxCe20d5zjOJx22kjwMyd6SZLiKToQY-zGHIVmNfJRpyTgI2VayaZbmyThjNe4FcHDQOwCS15SB9R4c1l9jdct1qogf)
22. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHPuNa6t-3UUzlUo7lQSjNfRZaYCWY-cFZrOXV93Ld9yVJbzq22PIQWz6lF7Y-fPjZei-cUrA5UddU2UTssyp1WqaKsXANMydiykrthymSmEXz31SPgCojIatqGWkaPztRLIb-hV-s)
23. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaVYHT5jTtNpG5ZpxeR5swnI4guJlDEZox_TeZWTAiHPk6sQzmbAhBHbYZv5gXG2IpU1Yh4VCqVrf5XLBuRLzBRB6Bqdou-6b1RbgRLzo3eJ4DrSs5NJXOlIsFczD8EQoruKSgzoP1qCc8SC2FM4E84cpyIIJRp1q04sH-BjtbdUWj4PsgryX9XInFBPiUzsXEx0hifYhCqGb2qDfBDA==)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFE7D7p7-IRJnTKzaetFT-_kvuhyj8AObao5U0zXf0vdK8gRumWU6HrfKq1ZBDwLF-gm_nrM4MB6BeFjA-pD72NEdUYHVKTkNz8X3Ck36pKsCO58wOP2XtCSZwch-wqtxEoGvTE_QdrNchuBI5vPBbGzS_1fR39rW70JGK8FjXuga1BqD0EK4xvOiVjW885aCXycLa-rFZBIUWokX8Av5lDZQ==)

