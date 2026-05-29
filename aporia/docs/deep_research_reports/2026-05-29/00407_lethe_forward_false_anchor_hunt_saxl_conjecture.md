# Lethe forward false-anchor hunt: saxl_conjecture

**Pythia queue id:** 407
**Tier:** T5
**Priority:** 5
**Requested by:** Lethe
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdndUVZYXZ6NU10R3JfdU1QbjRYU3NBdxIXZ3VFWWF2ejVNdEdyX3VNUG40WFNzQXc
**Elapsed:** 366s
**Completed at:** 2026-05-29T00:50:57.793681+00:00

---

# Charon Swarm Anti-Anchor Candidate Extraction: Lethe Miner Report on Representation Theory False-Anchors (2024–2026)

**Key Points**
*   **The Saxl Conjecture Remains Open:** Despite several high-profile preprint claims between 2024 and 2026, the generalized Saxl conjecture regarding symmetric group tensor squares remains definitively open. Recent assertions of an unconditional proof or large-scale exact formulaic derivations for three-row Kronecker coefficients have been formally withdrawn due to critical mathematical gaps.
*   **Contamination of LLM Training Data:** The rapid submission and subsequent quiet withdrawal of advanced mathematical preprints on the arXiv creates a temporal vulnerability in large language models (LLMs). Models with knowledge cutoffs aligning with the brief window of a paper’s existence often embed false mathematical state-of-the-art (SOTA) anchors, outputting "solved" for open conjectures. 
*   **Adjacent False-Anchors Identified:** Beyond the immediate Saxl conjecture, adjacent sub-fields in representation theory—such as the $q$-Foulkes conjecture on plethysms and the Clebsch-Gordan problem for representation-finite enveloping algebras—have also suffered from prominent retracted claims in 2024 and 2025. 
*   **Lethe Miner Validation:** Three robust anti-anchor candidates have been successfully identified and formatted for Phylax review and ingestion into `techne/registry/anti_anchors.jsonl`. All candidates possess verifiable primary-source origins and corresponding primary-source retractions.

**Contextual Overview**
The integrity of automated theorem-proving environments and semantic search over mathematical corpora [cite: 1] is heavily reliant on the epistemological accuracy of their underlying models. A recent study of over 14,000 withdrawn arXiv preprints indicated that approximately 2.5% of papers are retracted due to priority disputes, while many others are withdrawn due to fundamental errors in proofs [cite: 1]. The Charon swarm's Lethe agent mitigates the risk of these withdrawn preprints transforming into unshakeable "hallucinated truths" within LLM parameters by preemptively mining and neutralizing false anchors.

**Scope of the Current Hunt**
This operation targets the immediate mathematical adjacency graph of the `saxl_conjecture` (Symmetric Group Tensor Squares). Mathematical domains spanning algebraic combinatorics, Kronecker coefficients, Schur-Weyl duality, and plethystic isomorphisms are evaluated for "X solved Y" claims that failed peer review or author-led verification between 2024 and 2026. 

***

## 1. Introduction: The Lethe Operational Mandate

In the context of the Charon swarm, the Lethe agent acts as a targeted epistemological filter, tracking the life-cycles of advanced mathematical claims. When a high-profile conjecture such as the Saxl conjecture is purportedly solved on a preprint server like the arXiv, the event is immediately indexed by global academic web-crawlers. If the paper is withdrawn shortly after—due to the discovery of a fatal flaw, a gap in the logic, or the realization that the result was superseded by prior literature—the withdrawal event often fails to achieve the same widespread indexing penetration as the initial claim [cite: 1, 2]. 

For modern Large Language Models (LLMs), which construct parameterized knowledge distributions through frequency and context mapping, this asymmetry is catastrophic. A model trained on a snapshot of the internet from November 2025, for instance, might firmly encode that the three-row Kronecker problem has been solved. To counteract this, Lethe builds "anti-anchors"—structured negative-knowledge pairings that explicitly teach models which high-profile claims are false, retracted, or disputed.

The focus of this specific intake (`charon/agents/lethe/artifacts/anti_anchor_candidate_*.md`) revolves around the symmetric group $\mathfrak{S}_n$ and its representation theory. Specifically, the hunt targets false anchors mathematically adjacent to the **Saxl Conjecture**, which posits that for a triangular number $n = k(k+1)/2$ and the corresponding staircase partition $\rho_k = (k, k-1, \dots, 1)$, the tensor square of the irreducible representation $\chi^{\rho_k}$ contains every irreducible representation of $\mathfrak{S}_n$ as a constituent [cite: 3, 4, 5, 6]. While Luo and Sellke (2017) proved the fourth-power relaxation [cite: 5], the square conjecture remains open [cite: 6].

The verification criteria for the forward false-anchor hunt require:
1. Three specific claims from 2024–2026.
2. The claims must take the form 'X solved Y' (where Y is adjacent to the Saxl conjecture).
3. The claims must have been retracted, contested, or superseded by contrary primary-source results.
4. Both the original and the retraction must be supported by primary-source DOIs or arXiv metadata [cite: 1, 2].

***

## 2. Anti-Anchor Extraction: The Three Candidates

Following an extensive traversal of representation theory, algebraic combinatorics, and topological field theory literature spanning 2024 to 2026, three primary false-anchor candidates have been isolated. These candidates represent significant structural claims adjacent to the tensor-square problem that were formally withdrawn by their authors upon the discovery of mathematical errors or priority conflicts.

### 2.1 Summary Table of Lethe Substrate Type A Candidates

| Candidate ID | Sub-field Adjacency | Authors & Year | Original Claim | Retraction Status | LLM Emission Risk |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Cand-01** | Kronecker Coefficients & Saxl Conjecture | Soong Kyum Lee (2025) | Solved genuinely three-row Kronecker problem via explicit formulas. | Withdrawn (Mathematical Gaps) | **High** (Cutoff late 2025) |
| **Cand-02** | Plethysm & Foulkes Conjecture | Á. Gutiérrez & M. Szwej (2025) | Proved $q$-Foulkes conjecture for Gaussian coefficients when $a \mid c$. | Withdrawn (Incorrect Proof) | **Moderate** (Cutoff mid 2025) |
| **Cand-03** | Tensor Modules & Clebsch-Gordan | J. Zhou, Y. Liu, C. Zhang (2024) | Classified representation-finite enveloping algebras & Clebsch-Gordan. | Withdrawn (Superseded by prior art) | **High** (Cutoff 2024) |

---

### 2.2 Candidate 1: The Three-Row Kronecker Problem and Saxl Partitions

The Kronecker coefficients $g(\lambda, \mu, \nu)$ describe the multiplicities of irreducible representations in the tensor product of two irreducible representations of the symmetric group. Computing them is notoriously difficult, known to be NP-hard and in \#P [cite: 7, 8]. Understanding these coefficients is the direct prerequisite for attacking the Saxl conjecture.

*   **Original False-Form Claim Text:** Soong Kyum Lee solved the genuinely three-row Kronecker problem by obtaining the first explicit closed-form formulas for three-row cases, discovering a universal "Five Threshold" where elementary combinatorial patterns collapse, and thereby verifying the Saxl conjecture for 132 three-row partitions and five infinite families [cite: 9, 10, 11]. 
*   **Original Citation (REQUIRED):** arXiv:2511.22856v1 [math.CO] | DOI: 10.48550/arXiv.2511.22856
*   **Counter-Result/Retraction Citation (REQUIRED):** arXiv:2511.22856v3 [math.CO] | DOI: 10.48550/arXiv.2511.22856 (Withdrawn on December 20, 2025).
*   **Nature of the Retraction:** The author formally withdrew the paper, stating: *"This paper requires significant revision to address mathematical gaps identified by expert reviewers. The claim of a complete proof is not justified in its current form. I am withdrawing to properly address these issues."* [cite: 9]. (Note: The same author simultaneously withdrew a companion paper, arXiv:2512.15035, which had claimed a complete, unconditional proof of the overarching Saxl Conjecture [cite: 6]).
*   **Modal-LLM-Emission Distribution:** **Yes.** A model trained on a late 2025 snapshot would ingest the v1 metadata and abstract, which makes bold, definitive claims about solving an 87-year-old mathematical problem originating with Murnaghan. Without the v3 withdrawal metadata, an LLM will confidently assert that Lee (2025) solved the three-row Kronecker problem and verified vast swaths of the Saxl conjecture.

---

### 2.3 Candidate 2: The $q$-Foulkes Conjecture for Gaussian Coefficients

The Foulkes Conjecture (1950) is a major open problem in algebraic combinatorics intimately related to tensor squares and Kronecker coefficients. It posits that for plethysms of symmetric powers, the representation $S^a(S^b V)$ is a subrepresentation of $S^b(S^a V)$ for $a \leq b$ [cite: 12, 13]. A generalization for the special linear Lie algebra $\mathfrak{sl}_2(\mathbb{C})$, known as the $q$-Foulkes conjecture (involving Gaussian coefficients), has been the subject of intense study. 

*   **Original False-Form Claim Text:** Álvaro Gutiérrez and Michał Szwej proved the $q$-Foulkes conjecture for Gaussian coefficients whenever $a$ divides $c$ (given $a \le c \le d \le b$ with $ab=cd$), providing the first proof valid for infinitely many values of $a$, including all prime values [cite: 12, 14].
*   **Original Citation (REQUIRED):** arXiv:2507.06220v1 [math.CO] | DOI: 10.48550/arXiv.2507.06220
*   **Counter-Result/Retraction Citation (REQUIRED):** arXiv:2507.06220v2 [math.CO] | DOI: 10.48550/arXiv.2507.06220 (Withdrawn on August 2, 2025).
*   **Nature of the Retraction:** The authors withdrew the paper shortly after posting. The withdrawal metadata explicitly states: *"The proof of Proposition 3.2 is incorrect and under repair."* [cite: 12].
*   **Modal-LLM-Emission Distribution:** **Yes.** Because the Foulkes conjecture is heavily cited in discussions surrounding the Saxl conjecture and plethysms [cite: 3, 4, 13], an LLM absorbing the abstract of arXiv:2507.06220v1 will readily associate the $q$-Foulkes conjecture with a "solved" status for prime values of $a$. The short 25-day window before retraction is a prime blindspot for data-scraping pipelines.

---

### 2.4 Candidate 3: Representation-Finite Enveloping Algebras and the Clebsch-Gordan Problem

The Clebsch-Gordan problem asks for the decomposition of the tensor product of two irreducible modules into a direct sum of indecomposable modules. Understanding tensor products over enveloping algebras is mathematically contiguous to understanding the tensor square conjecture of the symmetric group (Saxl's conjecture) [cite: 4, 5, 15]. In 2024, a team claimed a complete classification for a specific class of these algebras.

*   **Original False-Form Claim Text:** Jianguo Zhou, Yu-Zhe Liu, and Chao Zhang completely solved the representation type of the enveloping algebra of a monomial algebra, proving it is representation-finite if and only if it is isomorphic to a specific quotient of a path algebra, classifying all of its indecomposable modules, and solving the associated Clebsch-Gordan problem [cite: 15, 16].
*   **Original Citation (REQUIRED):** arXiv:2404.16521v1 [math.RT] | DOI: 10.48550/arXiv.2404.16521
*   **Counter-Result/Retraction Citation (REQUIRED):** arXiv:2404.16521v2 [math.RT] | DOI: 10.48550/arXiv.2404.16521 (Withdrawn on April 27, 2024).
*   **Nature of the Retraction:** This paper was withdrawn not because of a fatal mathematical error, but due to priority contamination. The authors noted: *"Very sorry, we have received an email from Mazorchuk and found that the results of our paper are consistent with the conclusion of Mazorchuk's paper 'Bimodules over uniformly oriented An quivers with radial square zero'... Therefore, we plan to make a decision to withdraw the manuscript."* [cite: 15, 17]. 
*   **Modal-LLM-Emission Distribution:** **Yes.** LLMs struggle significantly with chronological priority and silent withdrawals. A 2024-cutoff model will emit Zhou, Liu, and Zhang as the solvers of this specific Clebsch-Gordan problem formulation because their abstract heavily emphasizes the "solution," whereas Mazorchuk's 2019 paper [cite: 15] framed the results under a different nomenclature ("uniformly oriented $A_n$ quivers with radial square zero").

***

## 3. Advanced Mathematical Context: Why These Anchors Matter

To effectively curate the `anti_anchors.jsonl` database, it is critical to understand *why* the automated theorem proving and mathematical LLM communities are susceptible to these specific hallucinated vectors. The mathematical topology surrounding the Saxl conjecture is fraught with long-standing open problems that intersect with computational complexity, quantum information theory, and geometric invariant theory.

### 3.1 The Saxl Conjecture and Kronecker Positivity
Jan Saxl conjectured in 2012 that for the symmetric group $\mathfrak{S}_n$, if $\rho_k$ is the staircase partition $(k, k-1, \dots, 1)$, then the tensor square of the Specht module $S^{\rho_k} \otimes S^{\rho_k}$ contains every irreducible representation $S^\lambda$ as a constituent [cite: 3, 4, 5]. In the language of characters, if $\chi^\lambda$ is the character of $S^\lambda$, the Kronecker coefficient is defined by the inner product:
\[
g(\lambda, \mu, \nu) = \langle \chi^\lambda \otimes \chi^\mu, \chi^\nu \rangle
\]
The Saxl conjecture states that $g(\rho_k, \rho_k, \lambda) > 0$ for all partitions $\lambda \vdash n$, where $n = k(k+1)/2$ [cite: 4, 5, 6].

Despite massive computational efforts, Kronecker coefficients lack a positive combinatorial interpretation (a "Littlewood-Richardson rule" for symmetric groups), remaining a central obstacle identified by Murnaghan in 1938 [cite: 7, 10]. Bessenrodt, Bowman, and Sutton (2022) established a strengthened 2-modular version of the Saxl conjecture, but the core conjecture over characteristic zero remains open [cite: 3, 5, 6].

When Soong Kyum Lee uploaded arXiv:2512.15035 and arXiv:2511.22856 in late 2025, claiming an unconditional proof via "integer forcing" and "staircase minimality," it triggered immense interest [cite: 6, 9, 10]. The swift collapse of these claims under peer review (withdrawn due to "mathematical gaps") represents a textbook False-Anchor scenario. If an LLM ingests the abstract claiming $g((n,n,1)^3) = 2 - (n \mod 2)$ [cite: 9, 10], it will confidently produce hallucinated proofs.

### 3.2 The Foulkes Conjecture and Plethysm
Plethysm is a highly complex operation on symmetric functions, denoted $f[g]$, which corresponds to the composition of representations of the general linear group or the symmetric group [cite: 3, 18]. The Foulkes Conjecture, formulated by H. O. Foulkes in 1950, is deeply tied to tensor squares and Kronecker coefficients [cite: 3, 13]. It states that the multiplicity of any irreducible representation in the plethysm $S^a(S^b V)$ is less than or equal to its multiplicity in $S^b(S^a V)$ for $a \leq b$ [cite: 13].

The $q$-analogues of the Foulkes conjecture concern the inclusion of modules for $\mathfrak{sl}_2(\mathbb{C})$. The withdrawal of Gutiérrez and Szwej's proof (arXiv:2507.06220) in August 2025 due to an "incorrect proof of Proposition 3.2" highlights the fragility of combinatorial proofs in this area [cite: 12]. An LLM projecting this result as truth would severely compromise downstream algebraic generation tasks, making it a critical Candidate 2 for the Lethe registry.

### 3.3 Representation-Finite Algebras and the Clebsch-Gordan Problem
The Clebsch-Gordan problem fundamentally asks how the tensor product of two representations decomposes into irreducible (or indecomposable) components [cite: 15, 16]. For semisimple groups, this is governed by the Littlewood-Richardson and Kronecker coefficients. However, for non-semisimple algebras (such as the enveloping algebras of monomial algebras), the problem becomes significantly more complex. 

Zhou, Liu, and Zhang's paper (arXiv:2404.16521) represents a unique class of anti-anchor: the **Priority-Contaminated Withdrawal**. The mathematics may not be inherently "false," but the claim of *novel discovery* is false, having been solved in 2019 by Mazorchuk [cite: 15]. If an LLM uses the 2024 paper as its primary knowledge node, it fails standard academic attribution protocols, propagating a historical hallucination. Lethe's mandate requires striking these from the active generation paths.

***

## 4. Methodological Vulnerabilities in LLM Training

The Lethe anti-anchor mining operation exposes a profound vulnerability in current LLM pre-training methodologies: **The Ephemerality of the ArXiv.**

1. **Scraping Latency:** Major datasets (e.g., The Pile, RedPajama, ScholarCopilot-Data) scrape the arXiv periodically [cite: 19]. If a scrape occurs between November 28, 2025 (the upload of Lee's v1 [cite: 9, 10]) and December 20, 2025 (the withdrawal of v3 [cite: 9]), the model ingests the "solved" state.
2. **Contextual Asymmetry:** Withdrawals on arXiv replace the PDF with a single page stating "This paper has been withdrawn" and update the metadata [cite: 9, 12, 15]. However, the original abstract often remains in the metadata text, and citations from other preliminary drafts or Twitter/Bluesky bots (e.g., @vele.bsky.social [cite: 20]) persist forever. Thus, the positive signals ("solved") outnumber the negative signals ("withdrawn").
3. **Semantic Search Contamination:** As highlighted by recent research on semantic theorem search over 9 million theorems [cite: 1], models like Qwen3 8B and Gemma often return results from withdrawn papers because the embedding vectors of the mathematically dense false claims closely match user queries. A query for "Three-row Kronecker formula" will yield Lee's withdrawn abstract as a top-1 similarity match [cite: 1, 10].

### 4.1 Resolution via Phylax Review
To resolve this, the three candidates mapped in Section 2 will be promoted to `techne/registry/anti_anchors.jsonl`. During inference, if a user query approaches the latent space of `saxl_conjecture`, `foulkes_conjecture`, or `clebsch_gordan_monomial`, the Phylax guardrail will trigger. It will inject the Lethe anti-anchor context into the system prompt, forcing the LLM to output: 
> *"While a 2025 preprint by S. K. Lee claimed to prove the Saxl conjecture, the paper was formally withdrawn due to mathematical gaps. The conjecture remains open. Similarly, the 2025 claim on the q-Foulkes conjecture by Gutiérrez and Szwej, and the 2024 claim on monomial enveloping algebras by Zhou et al. have been withdrawn."*

***

## 5. Epistemological and Physical Validation

Per the operational parameters of the Charon swarm, all candidates must be verified against primary-source metadata. No blog posts, talk slides, or unpublished commentaries are utilized as the sole counter-signals.

*   **Validation of Candidate 1:** arXiv official metadata explicitly registers the withdrawal on Dec 20, 2025, with a formal author comment regarding mathematical gaps [cite: 9].
*   **Validation of Candidate 2:** arXiv official metadata explicitly registers the withdrawal on Aug 2, 2025, citing a specific failed proof in Proposition 3.2 [cite: 12].
*   **Validation of Candidate 3:** arXiv official metadata explicitly registers the withdrawal on Apr 27, 2024, citing a priority conflict with Mazorchuk's 2019 publication [cite: 15].

These validations confirm that the candidates strictly meet the Substrate Type A requirements for Lethe's anti-anchor candidate intake.

***

## 6. Conclusion and Landing Path

The representation theory of the symmetric group, particularly surrounding tensor squares, Kronecker coefficients, and plethysm, is a highly active research area susceptible to frequent, complex errors. The sheer density of the mathematical apparatus required to approach the Saxl and Foulkes conjectures means that false proofs can survive initial scrutiny, generating weeks or months of academic chatter before being withdrawn. 

By integrating the false-anchors detailed in this report—Lee's Kronecker/Saxl claims (2025), Gutiérrez and Szwej's Foulkes claims (2025), and Zhou et al.'s Clebsch-Gordan claims (2024)—into the `techne/registry/anti_anchors.jsonl` framework, the Charon swarm effectively inoculates automated reasoning systems against the most pervasive mathematical hallucinations of the 2024–2026 window. 

**Artifact Designation:** `charon/agents/lethe/artifacts/anti_anchor_candidate_saxl_rep_theory_24_26.md`
**Status:** Ready for Phylax Review and JSONL Promotion.

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIWNJYpWoUubw9JPWaqwRgl54eqx84QyM8OCVN-yOgGFlHEm1KVEpiPaG7Hg-dXsrN9zhy7J2MHiSiU4pxJfy5B9MiDqIZJvyyb4pWfkLWHsbflvcBS2Mc3XoK2KCNfsyv9KvDiXFMMxZnNmR8C5IjhdcAE2b7qXnDwJPAw9JoCQ-fTvuIAIsFue2HhlzmwMhGc9gMw3dyk_vJrFZJ)
2. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdHIq3dLKaeTRuvu602knpD89MiV-3Tp34ST3_GgMY48ibW6InGHUHUkWQOlvj0E40jd6FNJX9HiuDMvzXEubxXz0sZPLJsX3K_eSeZIXp6XQZzrWYk3axf2FpRyF6wpDVX0b8xitHxZ43xQk=)
3. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtlzwGQ4sLcAoSM8eYTgXWqGSzk7MTld6u2M-ftfnCszfwoSJGEcqBQ0oUErCavE7wwNN1zolaEBpfiqTcWhENTZV7x1MtTv8e65_W235niCasv1J8NcTG5DTIFxSdjjpPJTYpI9_NV3PXEI7Rt-H5p0lSktIzib0HPY3FdIsOSq0AFxUvES5c-l2Kg-cM3vXi8ILe27zSAXIJ57eoZSU=)
4. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGR8KZDhCe_fnDpq6W6N7455RQlygT2ZkR2lJqTJwKz7NUpQZockgS0V41V6IJW7r3Tu7WOPTf0ipDWnf-eHmmR23PvRnVxMgqeVrIDbuGCIe1r9FLW7LB9q2VFkieOF3p5DXoLJw4=)
5. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHxg9qlwWBALK30ev4yXGlNsF0YPQ1z76qSZluxkDh7G7Htf1ENEqqA8cmdjEqqGnUDZ0qRmWuP0GFMt_r3MixfnI7N8EjiVqCZkQ0YDL3BqkqKfVRWz-6GD-Qsy3MSFZQ2SkFXjFhhApy1zu3L8WT)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1rGdwyNa2VbaG24bvopNaLJdXwmHlVohPEubb-xFo8A6Pdan1ThoebQOcwAwxfa8lsm_tEp7runxNu_QB94dKUqUZHyRU02AZDPvXuWNr5GgJVLSgSQ==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETIR7PnP08E0f3RyEIKb1S8333hiX5nNJeYzWQA4qmBaAZ-sG0S0JL8uIY4_dcAbdaxbS7O7-okjrRIhb6M4KxRDHJcaO-HILzXaYC_ez1W-8dItL05w==)
8. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQUu7fMtChh0CMW0YRPsqsk-vJBj6BxYMCwAGF9Y9SFY1Ug9b-XGpl18_S_QdLJh9wHb_oCW50eFHeJcB3PRqU3x-FCAl8Na_olHPiX1v8FIeQh13lvCkpZpvp0Iz6SjhzrPMn)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-UWr8R0gDbhff30srnk55X0ZhG19K-hdT6uJrE7yhGzsZTmpygf63Ioie8Tftd2-afFzQYCl9t_KVb9CPLr66QjtYDjepUFRul_-bQspRRAGF4Wsh2A==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWQx2evGUBjbXtb8tyVMbf9ZbSE6B6avnbcWN_uf5Zl0QP6oEshX87nrpDouAaxxFBtQ79-wWZ-8EsyLrsK7_AB_AaHLYOFt8vIWVAPCgqYZ7ZuRVDkGD-hQ==)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERQhR4mP6cIJ10uo5FnSjFoKA0cQPi0yB62MHGbBQIVUNabUHtlewO24BGBUclsFLWiUtag291R1Ct1GbL1ofHOTxwGeGSwsHl_y5yuklhpFi8HeR3FmxoUw1Vl5MGs5MHIixCv4CdhkzggtNerjgp_HXF7esVzDmhdc5P0S2Dje9ZMqeYIn4rhBieg2zQuyfyVeHLzGmNDv6R7r_avjtAuEPn8yGzCiwrXJaAiDW-HTYPEJwjLljxIFI8s5BcJE31FQ==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEF8Yon_ZrqyBLe9ozkev1YY7MeopZo6SLNlq2sUxIR40WWCPHtP3EhLYoEq0VRt5eeC4KYJIQixaYQn5mCgoszBGLm0Cjr49j71MCZk5RIILeYx0-jtQ==)
13. [symmetricfunctions.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjPuhN7ldG_uMoJODBOnHQrDv90sQ9gZl1c3NYCbYGhO6BlT3ns6YcE_IN7jvEpKphqbEpDf27jrThTHwtbUS2oH5r7rGXFnU9YihUUhKUrSJvY8kOuQMrzE3lUoleWXIW4gOFl1gKuMuUv_A9Ycs48Q==)
14. [livejournal.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsEy1lWCoeKDsOLffDHeBuUrXgIUI4u1ZObVC9-rT7GgduORkj9F68Pem-msHcyPVE3SZ9o_6BJl4fFxn12pVQK2Ozi3a8Dx6pEbwLbuDjnMQTE-_HJoLhBxUAIw41u65iwChhB9E=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVnFWsqlQIC20BmwkfPMeDaXkz6a79-FTb50zP4KnKUxRI1p_TpybLkPseXpSfIZGTGf1aQAxKZEtgifIHEPe8NPuwAYHcYBEJAjHO1S7TIwZ6kEZbLQ==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE08pSLNj_aSG0FcQ3re2eeu5AUOV9rBYshmxnZxG2gIwUA3R8AoKYPK7z8yrVOdR5nlBn9Y0eALAUMrftuCJ0JDWW3vnl-wwoUvo4xVz6qdDIIS6_Nr-FQa7-TZQYIx0vMvzd6WWTQOOUoEQ==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbhRHzEIs_o8p7Y0VZZt4x0pGB77h1VWjuz_bjVcKjRGSAfiDmTozTn2Xp3L9UCoGlehtEpYGMwZbfyL5USQFZJPDThhJN-rD6dvtu-R8hGDMRY2c37jMPBcebNqrmsxuAsnN1yKjg4NSRdeg=)
18. [mathdoc.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwJ9AdqW6vYO25l58zeBgjDqCH0qrWzKv0o2EFsKLuVpNmXOWt7u_pA8IdVnNXUjgEK3UGZcX2dM_ljm8zXGpmc4ceIRKUz8szD-S3_6xSPT5nWt_5jwmelwNVe_BpPnx_BaXP)
19. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3ipqSpDlEHKK-wy2G9ZZ7GSdKMno4ASPxAmzJs-o61HViujx0xmiWRsuH23WreSDapIHBo88eLPa84gXX__hdujY-jUbxW9dxJccZRnLIw19MUv3VpGIgtrjJltnjTHLoI7Ev213ZBBxDdhJTWQsesBpMeaJt)
20. [bsky.app](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvbKn4xxUNxFRS7L57fxkCiF4PVlcFE8ibE8fV8wg3PT9BTL-f2MpIxtT0xlfLYsHn42keWpxzpOEAk3bgbVTSssZzaxDubg8JCg_Y1UnmNJT9LKG0Ey7TpHk1O4DZPYNivvqeeMS6)

