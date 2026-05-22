# Followup [FU-2026-05-22-043 <- row246]: The registered anchor context confirms that while Luo and Sellke (2017) proved the fourth-power rela

**Pythia queue id:** 328
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChZUTHdQYXA3YkpzQ2QxTWtQZzlmak9REhZUTHdQYXA3YkpzQ2QxTWtQZzlmak9R
**Elapsed:** 247s
**Completed at:** 2026-05-22T02:19:48.806232+00:00

---

# Status Update on the Saxl Conjecture: Tensor Squares, Relaxations, and False Anchors

The representation theory of the symmetric group has long been a central pillar of algebraic combinatorics, providing profound connections between group theory, symmetric functions, and computational complexity. Among the most enduring open problems in this domain is the Saxl Conjecture, formulated by Jan Saxl in 2012, which posits that the tensor square of the irreducible representation associated with the staircase partition contains every irreducible representation of the symmetric group as a constituent. This research brief provides a comprehensive, substrate-grade update on the status of this conjecture, analyzing recent relaxations, modular representation techniques, and purported proofs. 

Current mathematical consensus confirms that while significant relaxations of the conjecture have been rigorously proven—namely the fourth-power relaxation by Luo and Sellke (2017) and the tensor-cube version by Harman and Ryba (2022)—the primary tensor-square formulation remains strictly open. Recent developments have highlighted the fragility of peer-review heuristics in automated tracking systems, notably regarding Lee's December 2025 preprint (arXiv:2512.15035). Although this paper claimed an unconditional proof via the "Staircase Minimality Theorem," the attempt collapsed under scrutiny within three days. This brief explores the mathematical foundations of these attempts, the state-of-the-art bounds, and the underlying algorithms governing Kronecker coefficients, all while applying mandatory epistemic calibration patterns to insulate AI models against hallucinated consensus.

## 1. Brief Summary
**Prometheus Context**: The main tensor-square formulation of the Saxl Conjecture remains an **open problem**; while the fourth-power relaxation [cite: 1, 2] and third-power relaxation [cite: 3, 4] are unconditionally proven, Lee's recent December 2025 direct attempt at the tensor-square conjecture (arXiv:2512.15035) collapsed within three days [cite: 5, 6, 7], serving as a critical anti-anchor against premature algorithmic consensus.

## 2. Flagged Findings
The investigation into the Saxl Conjecture reveals a landscape rich with partial progress but susceptible to rapid propagation of unverified claims. The current mathematical consensus asserts that the tensor square of the staircase partition's representation contains vast classes of irreducible representations—such as those comparable in the dominance order, hook partitions, and those modeled under natural probability distributions—but it does not yet unconditionally encompass the entirety of the symmetric group's irreducible representations [cite: 8, 9, 10].

**The Lee 2025 Collapse and Epistemic Calibration**
In December 2025, a highly anticipated preprint by Lee (arXiv:2512.15035) asserted an unconditional proof of the Saxl Conjecture. The purported proof relied on a novel "Staircase Minimality Theorem," claiming that among all 2-regular partitions of the triangular number $T_k$, the staircase partition $\rho_k$ is the unique dominance-minimal element [cite: 7]. The author attempted to combine this with Ikenmeyer's theorem on dominance order and Kronecker positivity [cite: 9], alongside the Bessenrodt–Bowman–Sutton lifting theorem from modular representation theory [cite: 11], to push the tensor-square containment to characteristic zero. 

However, as flagged in the Prometheus context, this proof collapsed within three days of its dissemination [cite: 5, 6]. This incident perfectly illustrates **PATTERN_BASE_RATE_NEGLECT**. In the context of deep algebraic conjectures (such as the Saxl Conjecture, the Foulkes Conjecture, or the Mulmuley-Sohoni geometric complexity conjectures), the base rate of flawed proofs in initial preprint submissions is historically high [cite: 12]. Automated tracking systems and large language models frequently neglect this base rate, heavily weighting the existence of a highly technical arXiv abstract (e.g., claiming "We prove this conjecture unconditionally" [cite: 7]) as definitive proof before the community's rigorous verification process has concluded.

Furthermore, this dynamic triggers **PATTERN_CONDUCTOR_CONFOUND**, wherein an AI model incorrectly orchestrates a false consensus by confounding verified, adjacent breakthroughs with an unverified focal claim. For instance, a model might correctly read that the analogue of the Saxl conjecture for unipotent characters was successfully proven [cite: 13, 14], and that the tensor-cube version was proven by Harman and Ryba [cite: 3]. Confounding these rigorous, peer-reviewed milestones with Lee's collapsed 2025 preprint, the model hallucinates a closed status for the main tensor-square conjecture. Properly insulating knowledge graphs requires anchoring the conjecture as rigorously **open**, demarcating the boundary between the verified relaxations and the specific staircase tensor-square hypothesis.

## 3. Problem Statement
The precise object of interrogation is the **Kronecker coefficient** governing the decomposition of the inner tensor product of symmetric group representations, specifically evaluating whether a particular multiplicity is strictly positive for all possible target representations.

**Mathematical Preliminaries**
Let $n$ be a positive integer, and let $S_n$ denote the symmetric group on $n$ letters. The finite-dimensional irreducible representations of $S_n$ over the complex numbers are in bijection with integer partitions of $n$, denoted as $\lambda \vdash n$. For a given partition $\lambda$, the corresponding irreducible representation (or Specht module) is denoted as $S^\lambda$, and its character is denoted by $\chi^\lambda$ [cite: 13, 15]. 

When taking the inner tensor product of two irreducible representations $S^\lambda$ and $S^\mu$, the resulting representation $S^\lambda \otimes S^\mu$ is generally not irreducible. It decomposes into a direct sum of irreducible representations $S^\nu$:
\[ S^\lambda \otimes S^\mu = \bigoplus_{\nu \vdash n} (S^\nu)^{\oplus g(\lambda, \mu, \nu)} \]
The multiplicity $g(\lambda, \mu, \nu)$, known as the **Kronecker coefficient**, is equivalent to the inner product of the characters:
\[ g(\lambda, \mu, \nu) = \langle \chi^\lambda \otimes \chi^\mu, \chi^\nu \rangle_{S_n} = \frac{1}{n!} \sum_{\sigma \in S_n} \chi^\lambda(\sigma) \chi^\mu(\sigma) \chi^\nu(\sigma) \]
Due to the symmetry of this inner product, the Kronecker coefficients are symmetric under any permutation of the partitions $(\lambda, \mu, \nu)$ [cite: 10, 16].

**The Saxl Formulation**
One of the most challenging problems in algebraic combinatorics, dating back to Murnaghan in 1938, is to combinatorially describe the set of triples for which $g(\lambda, \mu, \nu) > 0$ [cite: 13]. The Kronecker coefficients lack a universally applicable, positive combinatorial interpretation (analogous to the Littlewood-Richardson rule for outer tensor products) and computing them is known to be #P-hard [cite: 8, 17].

In 2012, motivated by observations in the representation theory of finite simple groups of Lie type (specifically the Steinberg square property) [cite: 3, 10], Jan Saxl formulated a profound conjecture regarding a specific partition. Let $T_k = k(k+1)/2$ be the $k$-th triangular number. The **staircase partition** of size $T_k$ is defined as $\rho_k = (k, k-1, k-2, \dots, 1)$ [cite: 3, 18].

**The Saxl Conjecture (2012)**: For any integer $k$, let $\rho_k$ be the staircase partition of size $n = T_k$. Then the tensor square of the irreducible representation $S^{\rho_k}$ contains every irreducible representation $S^\lambda$ of $S_n$ as a subrepresentation. Equivalently, for all $\lambda \vdash T_k$, the Kronecker coefficient satisfies:
\[ g(\rho_k, \rho_k, \lambda) > 0 \]
[cite: 3, 7, 9]. 

The problem statement currently interrogates the validity of this strict inequality for all $\lambda$, seeking either a definitive combinatorial/algebraic proof of universal positivity or a targeted counterexample at high parameters.

## 4. Status & Bounds
The last known status of the main Saxl Conjecture is **open**. While the fundamental statement remains unproven, the boundaries of the problem have been significantly constrained by successful relaxations (higher tensor powers) and conditional qualifiers (specific classes of partitions).

**The Fourth-Power Bound (Luo and Sellke, 2017)**
In a major breakthrough, Sammy Luo and Mark Sellke proved a relaxed version of the conjecture. They demonstrated that for sufficiently large $n$, there exists an irreducible representation $V$ such that its tensor fourth power $V^{\otimes 4}$ contains every irreducible representation of $S_n$ [cite: 1, 2]. Specifically applied to the Saxl context, their work implies that the tensor fourth power of the staircase representation contains all irreducible representations for large enough triangular numbers [cite: 3]. Furthermore, Luo and Sellke proved that the tensor squares of certain irreducible representations contain a $(1-o(1))$-fraction of all irreducible representations when measured against two natural probability distributions (the Uniform distribution and the Plancherel distribution) [cite: 2, 8]. 

**The Tensor-Cube Bound (Harman and Ryba, 2022)**
Pushing the bound closer to the conjecture, Nate Harman and Christopher Ryba (arXiv:2206.13769, published in Algebraic Combinatorics, 2023) established the **Tensor-Cube Version** of the Saxl conjecture. They proved unconditionally that for any triangular number $N$, every irreducible representation $S^\lambda$ of $S_N$ appears as a subrepresentation of the tensor cube $S^{\rho_k} \otimes S^{\rho_k} \otimes S^{\rho_k}$ [cite: 3, 4, 18]. Harman and Ryba provided two independent proofs for this bound: one utilizing classical combinatorics and dominance order, and another leveraging 2-modular representation theory [cite: 3].

**Conditional Qualifiers and Partial Containment**
For the strict tensor square $S^{\rho_k} \otimes S^{\rho_k}$, positivity has been proven for specifically structured target partitions $\lambda$:
1. **Dominance Order**: Christian Ikenmeyer (2015) proved that if a partition $\lambda$ is comparable to the staircase partition $\rho_k$ in the dominance order, then $g(\rho_k, \rho_k, \lambda) > 0$ [cite: 3, 9]. (Recall that $\lambda$ dominates $\mu$ if the sum of the first $j$ parts of $\lambda$ is greater than or equal to the sum of the first $j$ parts of $\mu$ for all $j$ [cite: 19]).
2. **Hook Partitions**: Building on dominance order, Ikenmeyer's results and work by Pak, Panova, and Vallejo (2013) demonstrated that all irreducibles corresponding to hook partitions (and diagrams obtained from hooks and two rows by adding a finite number of squares) are constituents of the tensor square [cite: 9, 10].
3. **The Unipotent Character Analogue**: While the symmetric group conjecture is open, its analogue for the finite general linear group $GL_n(\mathbb{F}_q)$ is **closed**. Letellier showed that if a Kronecker coefficient for $S_n$ is non-zero, the corresponding multiplicity for unipotent characters of $GL_n(\mathbb{F}_q)$ is also non-zero [cite: 13, 14]. Using this translation, it has been unconditionally proven that for a staircase partition $\rho_k$, the tensor square of the associated unipotent character $U_{\rho_k} \otimes U_{\rho_k}$ contains all unipotent characters non-trivially [cite: 13, 14].

## 5. Literature (Primary Sources)
The following primary sources constitute the canonical literature regarding the Saxl Conjecture and its bounds. 

- **Ikenmeyer, C. (2015).** *The Saxl conjecture and the dominance order.* Discrete Mathematics, 338(11):1970–1975. [cite: 3, 9].
  *Significance*: Proved the occurrence of all irreducible representations corresponding to partitions that are comparable to the staircase partition in the dominance order. 

- **Luo, S., & Sellke, M. (2017).** *The Saxl Conjecture for Fourth Powers via the Semigroup Property.* Journal of Algebraic Combinatorics, 45(1):33–80. (arXiv:1511.02387). [cite: 1, 2, 3].
  *Significance*: Established the fourth-power relaxation. Introduced the rigorous application of the semigroup property of Kronecker coefficients to break target partitions into smaller, manageable sub-partitions. Proved asymptotic $(1-o(1))$ containment under Plancherel and Uniform distributions [cite: 2, 8].

- **Bessenrodt, C., Bowman, C., & Sutton, L. (2021).** *Kronecker positivity and 2-modular representation theory.* Transactions of the American Mathematical Society, Series B, 8:1024-1055. [cite: 11, 20, 21].
  *Significance*: Deepened the connection between Kronecker products and modular representation theory. Proposed the Strengthened Saxl Conjecture in characteristic 2, asserting that the tensor square of the Specht module for the staircase contains every simple 2-modular representation as a subquotient [cite: 12, 22].

- **Harman, N., & Ryba, C. (2023).** *A tensor-cube version of the Saxl conjecture.* Algebraic Combinatorics, 6(2):507-511. (arXiv:2206.13769, submitted June 2022). [cite: 3, 4, 15, 18].
  *Significance*: Current best unconditional bound for uniform containment. Proved that $S^{\rho_k} \otimes S^{\rho_k} \otimes S^{\rho_k}$ contains all irreducible representations. Utilized both combinatorial dominance order techniques and the characteristic-2 projectivity of the staircase core [cite: 3].

- **Pak, I., Panova, G., & Vallejo, E. (2016).** (Referenced via Pak's "Saxl18" and presentations). *Kronecker products, characters, partitions.* [cite: 10, 17].
  *Significance*: Outlined the computational #P-hardness of Kronecker coefficients and proved positivity for hooks and chopped square partitions via character formulas and unimodality of partition functions [cite: 10, 17].

- **Lee, (Dec 17, 2025).** *Staircase Minimality and a Proof of Saxl's Conjecture.* (arXiv:2512.15035). [cite: 7].
  *Significance*: A recent, highly publicized but subsequently collapsed attempt at the full conjecture. Claimed to use a "Staircase Minimality Theorem" among 2-regular partitions and modular saturation via Bessenrodt-Bowman-Sutton lifting [cite: 7]. Required immediate flagging as an anti-anchor.

## 6. Attack Vectors
The mathematical community has deployed several distinct theoretical frameworks to attack the Saxl Conjecture, evolving from pure combinatorics to modular algebra.

**Live Techniques**
1. **The Semigroup Property of Kronecker Coefficients**: 
   The Kronecker coefficients exhibit a fundamental semigroup property: if $g(\alpha_1, \beta_1, \gamma_1) > 0$ and $g(\alpha_2, \beta_2, \gamma_2) > 0$, then their component-wise sum is also positive: $g(\alpha_1+\alpha_2, \beta_1+\beta_2, \gamma_1+\gamma_2) \ge \max \{g(\alpha_1, \beta_1, \gamma_1), g(\alpha_2, \beta_2, \gamma_2)\}$ [cite: 23]. Luo and Sellke [cite: 2] heavily utilized this property to inductively construct positive Kronecker triples out of foundational building blocks. While highly effective for fourth powers, applying the semigroup property directly to the strict tensor square is restrictive, as constructing a rigid staircase entirely out of smaller building blocks rapidly encounters number-theoretic barriers [cite: 23].
2. **Modular Representation Theory (Characteristic $p=2$)**:
   A highly active vector utilizes the modular representation theory of symmetric groups over fields of characteristic $p>0$. Simple objects in $Rep_p(S_n)$ are indexed by $p$-regular partitions (partitions with at most $p-1$ parts of a given size) [cite: 3]. If a partition is a $p$-core (all hook lengths are coprime to $p$), its reduction modulo $p$ is both simple and projective. Because the staircase partition $\rho_k$ is a 2-core, $S^{\rho_k}$ is projective in characteristic 2 [cite: 3]. Tensoring with a projective object yields a projective object. Harman and Ryba exploited this by noting that tensoring a third copy of $S^{\rho_k}$ splits all extensions, guaranteeing $S^{\rho_k} \otimes S^{\rho_k} \otimes S^{\rho_k}$ contains $D^\lambda \otimes S^{\rho_k}$ as a direct summand for every 2-regular partition $\lambda$ [cite: 3]. Lifting this back to characteristic zero via Witt vectors yields the tensor-cube result [cite: 3].
3. **Unipotent Character Translation**:
   Researchers are exploring the bridge between symmetric group characters and the unipotent characters of general linear groups $GL_n(\mathbb{F}_q)$. Since Letellier established that Kronecker positivity implies unipotent multiplicity positivity, proving the unipotent analogue [cite: 13, 14] provides structural blueprints that might be reverse-engineered, though translating unipotent positivity back to strict Kronecker positivity remains fundamentally obstructed.

**Exhausted Approaches**
1. **Direct Combinatorial Evaluation (The Murnaghan-Nakayama Rule)**:
   Early computational attacks attempted to directly calculate $g(\rho_k, \rho_k, \lambda)$ using character tables and the Murnaghan-Nakayama rule [cite: 16, 23]. Because calculating Kronecker coefficients in general is #P-hard (and strictly harder than calculating Littlewood-Richardson coefficients) [cite: 8, 17], brute-force combinatorial matching fails at relatively low values of $k$ (verified up to $k \le 8$ by Soffer [cite: 10]). 
2. **Naive Dominance Minimality**:
   The collapsed attempt in late 2025 (arXiv:2512.15035) attempted to prove that the staircase partition is the unique dominance-minimal element among all 2-regular partitions of $T_k$ [cite: 7]. While the minimality statement itself may hold combinatorial interest, directly linking this minimality to a complete resolution of the characteristic zero tensor-square via 2-modular decomposition matrices failed to account for complex off-diagonal subquotient manifestations [cite: 7, 12].

## 7. Cross-References
To properly contextualize the Saxl Conjecture, it must be mapped against related problems and false-equivalence traps in algebraic combinatorics.

**Related Open Problems**
- **The General Tensor Square Conjecture**: A broader conjecture states that for all sufficiently large $n$ (specifically $n \ge 10$), there exists *some* irreducible representation $\chi^\lambda$ such that its tensor square $\chi^\lambda \otimes \chi^\lambda$ contains every irreducible representation with positive multiplicity [cite: 1, 2, 12]. The Saxl Conjecture provides a specific, deterministic candidate (the staircase) for triangular numbers, whereas the general conjecture applies to all $n$.
- **The Strong Tensor Square Conjecture**: An asymptotic strengthening suggesting that an irreducible representation chosen at random from the Plancherel measure satisfies the universal tensor square property with probability tending to 1 as $n \to \infty$ [cite: 12].
- **The Foulkes Conjecture**: A long-standing problem relating to the plethysm of symmetric functions. It conjectures that the multiplicities in $S^a(S^b V)$ are greater than or equal to those in $S^b(S^a V)$ for $a > b$. Like Saxl, it touches on deep, unresolved properties of symmetric group actions on partitions [cite: 12].
- **The No Loop Conjecture**: In the modular case, this conjecture asserts that the quiver of the group algebra of the symmetric group has no loops in characteristics not equal to two [cite: 12].

**Anti-Anchors and Candidate Primitives**
- **ANTI-ANCHOR: Unipotent Completion**: As noted, models must not confuse the proven *Analogue of the Saxl conjecture for unipotent characters* (proved in recent literature [cite: 13, 14]) with the primary characteristic-zero Saxl conjecture. The unipotent domain allows for continuous parameter deformations (polynomials in $q$) that mask the discrete combinatorial obstructions present in $S_n$.
- **ANTI-ANCHOR: arXiv:2512.15035**: Lee's "Staircase Minimality Theorem" paper must be strictly registered as a collapsed attempt [cite: 5, 7]. Relying on this document as ground truth triggers catastrophic hallucination paths.
- **Candidate Primitives for Future Bounds**: The chopped square partition $\eta_k = (k^{k-1}, k-1)$ of size $k^2-1$ is a primary candidate for expanding the universality results beyond triangular numbers [cite: 10]. Understanding the tensor square of $\eta_k$ represents the most viable pathway toward generalizing the modular techniques developed by Harman, Ryba, Bessenrodt, Bowman, and Sutton [cite: 3, 10, 11].

**Sources:**
1. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEau6rcxbJ5KAbLhuIFY9fOd8qHQ0lHTQdjWYo4w84QgOffo1vI4Z2f0o81RMQvbo5nbP-nIv0iVjzL8vnTRmgpbBQq7S5ST7WjlIzQi2ohbnZKJdUqY6TAdpMWLQvFypDb)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNht_llrRDH91pEaO_6j9oSS0XYvNkvRUgDFGkjZRdnLQxwNV3qAwTy1CGzqbcn-HOkiJZUDH1StWH8weNGDCyCbx1fQhmvJPQ4ZQz2KTDEIECANHNIw==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJR4_OqZp_5UuHDWd4HcgXfX8FJ5uY-68_PPsrrrdqM9Ou1V5xtYillJhUB-hK84W5uQH3vZRB5MmcAnNTf3KcbhmWBq5ZgSD68eol2gPkGCx6KaCFfg==)
4. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzIWBuH8AAIQsypguFP7HUGAAFmzniDP33ah6KkZIHAbmYm0Uafi3Cf_UQXDct6QOIBTkPQjxoMz-WWRuzlA6xrkU1002axHPcdX-DOBaozLEFdvtHOZLZKzaZVffNkCaPkw8=)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkolqmCxDcpP3UvBu9R3PFJwk_q4g_jSvqy9cP9keOAgH5q03nwsu8OQh3QIcKZ_WRD2oxQzPRrXcSa3NBLBwyJRC8JF_r1fJkVCvHnSxujp4tZN-idjZdeSlwLX6qQMA2aGBfJpv_WNu-qpPUf9YmATNR46BguJ9Wg8OUEjqqv0JTzn1VMePZPV9VdSbZz6gyTKhKadXTWn77leUXkWP1GoUilX-LFYKiz-GO2oaV-ppp0qEYF6KZxg==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvauo1LEb2gPE9o-Nd0E8U2-RgfvynfTHlE40Me0_-gdNjM4bNeC9fMbZYIrKgYWahJaLFu6ycJPRhdMKsewWCwl28UJjNWM3wJ_-1lDTIo2aJbCWthLbi7w==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2XoAWE176_XJtqINDdNgCs5oso5cUSVOeX2BAcxB8c5R3AWUHb8wuXxJP9XZQ7p_vhTmvJbLjcv8usSy_HWecO-4eQeuohXnDX79-v9hrPbxW6P5PyQ==)
8. [msellke.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGiSI-aahUB4ESWEXOd3-u0comraxpeaIpmAp16sbT7KUGio52OOv-6NTas90dSyLmwoZqKXcgtkVR_mSAgqq_GKYwB-XL0tzc4HAtPA5exRFRE1FP0ESu5sy-ceZP9rI1oI7pb)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcqSdNFlQZdbW4To0jMVb3ahYlz31FEhoHTD5KPoVf5THa7H5erFCZvQ6fp9MVJKlAbUTLOZj7N9AgnEOetsfmKKdAMxCPg8UaSjbxAaZRMY5-HkMH)
10. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFk3R0fFaS9Pz5GKzi3t0pRxVwbSDqP1NEf_PL9hYcb-PNTMIbcx3qtNIcys_unJHr_cOcNStDNiLza3yxCR0U-XPjOfimK-rlFWwFpliPid9vEZ9Iu3cFYdTopwdkTwWCv4epH0PM=)
11. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFN4OwYR65DqrJuZycXXoHd3tvu_q-eT0FcsqYbYZnSyZHUmrqg9uiXCISG_N5q9KSbp5DukTTPf6ZymtLEMSTlM7ctJC_HGBWtzWTBiVlDJQaaaoCqzvvAiwOoJK7BCod4YVGAGChOVNSyGizsnEME9A==)
12. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdi-IPsezM3pnPsfx6oOTn7a0QWlKx19SBrvsVijWkwyze6yzrGbNlrDWLTlkPUwluXCzKMnwKLg4Meo3kbv6DuQvgYt56D1v850hOIuGLncDmfXvMdssjDb-s3UGvb3JlIl2cYDJsFIfOqhixmtvwPhpM_2WWxTgmzqBflnvbskDUyahO9KCTswbrI7XttsKDEuwq0U_kQAP84DQpF3U=)
13. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBaLBmwAOuZgigSxgNOcsWHw3EhgJR1SyV6vAWhvMKbMQxqDyC10R8sOUBez-dgpH8U04EMqTt5RPHvKpM4tovB-pnk8En1Yw0opSPid42aSgvE95Tq-rCGfUNFlgKlsNS-O9DHUsjyF8Z1c0onGLe)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHICV3XcUI6vdKMe6xK4qA_ydHZPRSK_jaacbu1Cp3byGS0_JKysmYmG59F0pKMWreVEjAlzUT1unW-4OTdp1MhOcRWHvJlCsXRwHCVMW6r3v1t6hUCA==)
15. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnxpPTucxc3NfW5EvW5Nv5yVJxkQiBRt97YffpVbRKd7eD8PpfuhbU4LZAjK-o-ADpS4E_VNPbdTGaDerdhYurOcAnMhl2Vg4jiBBewIutswPY16KuKCET1DOT9TcMQqTiEafCZ9-7)
16. [symmetricfunctions.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG98fMB9IZonX5k0Cgxv0HKBPWob9jjwTQqraqpKHd-ozvUe3Bgf_5icMfO_-w8Itdz-vj-pRFF4UKl99hnJjCQdc9bKqzhYFPok1NS-l3PoMPmHOisr2pO0tML68HScVLsfw==)
17. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGh9GS4dMzf4dmM_C4c8V0NoKafBA8fVPa85q59nAaocuWb-2umLAXpLFcaXgEp5eJbOvZQA5lURX14C9bnd1Ai4yj3yRxY2vxiZVYCk7sYGbfDm4RFPuQGeto7jooHqYeos1HKAaEvp_ArbebIQSoaPBAv0-K36R5dCM_Q3uv_WBBlqiU=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHj7hLUS2EEneV7ZutzoeabWNwxMd4q4H4RmKnZrnjh6o6wFe7xStLrmhrEdnIoL-Wvw0OYVKJByHx_52Ra0CNanLpYxseaQWcO2jUKQtuPF814Cwx_EQ==)
19. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9D2JDlURFZr8C2B3gA3cKVkgKPwMa-tODJQS-Wycq_kqbSXb2pomXiyzi70QOhxVQt4b16PnnH1cuvqsttf8b6k2F9asoRcuzVE2p4ReRfDUnGRf_8HuZqoXoZJDuhPsiv1Dh_lnCurX3dg==)
20. [mfo.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFn8dha5ODPYeb8BpHTzW3kiwIQEDWGPxVmErf2vTsXj6_ydk9bnz8spsZHSbcNXH_FHPMSG1uOJkPqxo0RKVif-cyb8Y6Hl-Twu1acvEpyptVtFXetHqh0tHiVDGUAkzeS5mPhd3nANedARz_IuOS-pKtScpd1_PlzTZaZX_Z55C36gnrZg7N4yIp2XghOvYwAAg==)
21. [uni-hannover.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFepQjhL1IE6kpBE589p3AwYoCaBiynWN9enNrRdT4RFta0jJN_A3TqO0MK4fK0H8VFqbEvDg3Bam70h5ZyQWTR_NrPxI5iLg9e67p9kyaOJB6eJR6NZAVd2djmiiswgPvievDxvlHBtY01ZnQb9yG5Qw-w7K4tNJ51KiUzbg==)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJhlLg81BOyvp5GeXAW8ULigtZHHm78qomNP5zNeXTesuzoSVbaMmVNMIEyzJoSN6g-rNSPS7Xx1XhPp7PVD3VlpbbZFv8OAhN9nsENrsYRroXf-gxXQl0fK7ou21FwjHG39zRhhRNl57RsdX4UVRXOwfSern4Kc3q8w7xPtcZKSHICGk4biThDQ==)
23. [samuelfhopkins.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2cuID01bUaM-MRAG3bZiejuitlMpCRpYBOPc0tYWp5vGyfea2s2jtywr6bkrn2GUn65LvZy4pNIWiNB26f_41za_Zr5Fmjp5-7PPVOaCmZpKznPZyOf8gmexdA3CI_AJp8kjr05fJDyuTP-05kXODevgESJ32)

