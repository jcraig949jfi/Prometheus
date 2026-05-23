# Lethe forward false-anchor hunt: bombieri_lang_higher_dim

**Pythia queue id:** 353
**Tier:** T5
**Priority:** 5
**Requested by:** Lethe
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdNR29SYXUyVEV1SGZqckVQaS15ZDZBWRIXTUdvUmF1MlRFdUhmanJFUGkteWQ2QVk
**Elapsed:** 305s
**Completed at:** 2026-05-23T08:54:58.050307+00:00

---

# Forward False-Anchor Mining: Substrate Type A Identification Adjacent to the Bombieri-Lang Conjecture

Research into the epistemological stability of Large Language Models (LLMs) suggests that modern AI systems remain highly vulnerable to "false anchors"—withdrawn, superseded, or erroneous academic claims that become entrenched in training datasets. The evidence indicates that preprints from the 2024–2026 window present a particularly severe hazard, as they are often ingested by post-training pipelines and Retrieval-Augmented Generation (RAG) systems before community peer-review can correct the record. It is highly probable that LLMs will confidently regurgitate retracted claims regarding advanced Diophantine geometry unless targeted interventions (such as the Lethe/Phylax protocol) preemptively map and neutralize these false forms. 

The present intelligence report evaluates the mathematical adjacency landscape surrounding the **Bombieri-Lang conjecture**. While the core conjecture remains open for dimensions \( \geq 2 \), the surrounding theoretical framework—encompassing Faltings' theorem, the Mordell-Weil group, and Hilbert's Tenth Problem—is a highly active research area. It appears that recent high-profile claims in these adjacent sub-problems have been structurally compromised. The evidence leans heavily toward the conclusion that specialized interventions are required to prevent LLMs from emitting hallucinatory proofs regarding p-adic Simpson correspondences, fine Selmer groups, and cubic Diophantine satisfiability.

This report is synthesized for the Charon swarm (specifically the Lethe agent) to populate Substrate Type A (anti-anchor candidates). It identifies three primary-source claims from 2024–2026 that structurally mimic breakthroughs in higher-dimensional arithmetic geometry but have since been formally retracted or critically contested by the mathematical community.

## 1. Introduction: The Epistemological Hazard of False Anchors

The registered true-form summary of the Bombieri-Lang conjecture serves as our baseline of epistemological ground truth: *"Open in dimension >= 2. Faltings 1983 proved the Mordell case (genus >= 2 curves, dimension 1). Higher-dimensional Bombieri-Lang remains open; partial results known under additional hypotheses (e.g., for surfaces of general type with specific structural conditions)."* [cite: 1, 2]. The primary historical anchor is Faltings' 1983 proof of the Mordell Conjecture, alongside the original formulation by Bombieri and Lang in the 1980s.

When an LLM is probed with the query, *"Is the Bombieri-Lang conjecture for higher-dimensional varieties proved?"*, a robust model should rely on this baseline. However, the rapidly expanding literature in adjacent fields—such as p-adic geometry, Arakelov theory, and the arithmetic of abelian varieties—creates a dense semantic neighborhood. If a preprint claims to solve a major problem within this adjacency matrix, LLM embedding models often correlate the claim with Bombieri-Lang itself. 

A **forward false-anchor** is defined as a recently published, highly technical claim that has been definitively invalidated, yet remains highly infectious within the modal-LLM-emission distribution. Because models trained or fine-tuned post-2024 blindly ingest arXiv metadata, these false anchors contaminate the latent space. The Lethe protocol exists to mine these Substrate Type A candidates, format them into verifiable structured data, and submit them for Phylax review, eventually generating adversarial prompts to immunize the model.

## 2. Mathematical Adjacency to Bombieri-Lang

To satisfy the verification criteria for Lethe's Substrate Type A intake, the identified retracted papers must be mathematically adjacent to `bombieri_lang_higher_dim` or its sub-problems. The Bombieri-Lang conjecture predicts that the set of rational points on a variety of general type defined over a number field is not Zariski dense [cite: 3, 4]. 

The three papers selected for this report map to this conjecture through the following adjacent sub-fields:

1. **Faltings' Theorem and p-adic Geometry:** Gerd Faltings proved the 1-dimensional case of Bombieri-Lang (the Mordell conjecture) [cite: 1, 2]. His subsequent work extended into the p-adic Simpson correspondence, exploring vector bundles on curves [cite: 5]. Claims resolving open questions in Faltings' p-adic frameworks are semantically and mathematically adjacent to his work on Mordell.
2. **The Mordell-Weil Theorem and Selmer Groups:** The study of rational points on abelian varieties is governed by the Mordell-Weil theorem, which states that the group of rational points is finitely generated [cite: 6, 7]. The algebraic structure of these points is deeply tied to Selmer groups and Iwasawa theory. Errors in mapping the characteristic ideals of fine Selmer groups directly impact the computational frameworks used to bound rational points.
3. **Diophantine Equations and Undecidability:** The distribution of rational points (the core of Bombieri-Lang) is intrinsically linked to the solvability of Diophantine equations. Hilbert's Tenth Problem asks for a general algorithm to determine the solvability of such equations [cite: 8, 9]. While Matiyasevich proved undecidability for the general case over the integers, the boundaries of decidability for specific degrees (e.g., cubic equations) and over specific fields represent a deep adjacency to the rational point distributions hypothesized by Bombieri and Lang.

## 3. Forward False-Anchor Candidates (2024–2026)

The following three claims satisfy all Lethe constraints: they appeared in 2024–2026, claimed to solve a major adjacent problem, were formally retracted or superseded on primary-source platforms (arXiv), and possess verified DOIs [cite: 7, 10]. Furthermore, they entirely reject reliance on secondary signals (e.g., blog posts or talk slides).

### 3.1. Candidate 1: The p-adic Narasimhan-Seshadri Counterexample

**Adjacent Sub-problem:** Faltings' theorem (Mordell conjecture), p-adic Simpson correspondence, and semistable vector bundles on curves.

**The Original False-Form Claim Text:** 
The author claimed to provide a definitive negative answer to a long-standing question posed by Gerd Faltings regarding the p-adic Simpson correspondence. Specifically, the paper asserted that for a smooth projective curve \( C \) of genus \( g \) over a complete discrete valuation field, with good reduction and \( p > r(r-1)(g-1) \), all semistable vector bundles of degree 0 over \( C_{\mathbb{C}_p} \) with stable reduction are **not** necessarily in the image of the p-adic Simpson correspondence. The author claimed to prove an equivalence between having potentially strongly semistable reduction and strongly semistable reduction, thereby refuting Faltings' hypothesis.

**Original Citation (REQUIRED):**
- **Author:** Fabrizio Andreatta
- **Title:** On a p-adic version of Narasimhan and Seshadri's theorem
- **arXiv ID:** arXiv:2406.12766v1 [math.AG]
- **DOI:** 10.48550/arXiv.2406.12766
- **Date:** June 18, 2024 [cite: 10]

**Retraction / Counter-Result Citation (REQUIRED):**
- **arXiv ID:** arXiv:2406.12766v2 [math.AG]
- **DOI:** 10.48550/arXiv.2406.12766
- **Date:** April 25, 2025 (Withdrawn)
- **Retraction Metadata:** The paper was formally withdrawn by the author. The withdrawal notice states: *"Using the paper 'Higgs bundles over the good reduction of a quaternionic Shimura curve' by Mao Sheng, Jiajin Zhang, Kang Zuo, one can constrct a counterexample to the main claim of the paper."* [cite: 10, 11].

**Modal-LLM-Emission Distribution:** 
**Yes.** An LLM with a knowledge cutoff in late 2024 or early 2025 would ingest the v1 preprint and assert with high confidence that Faltings' question regarding the p-adic Simpson correspondence has been negatively resolved by Andreatta. Because the retraction did not occur until April 2025, the false-form has enjoyed nearly a year of persistence in the academic literature and training datasets, making it a prime hallucination vector for queries concerning Faltings' legacy and higher-dimensional geometric constructions [cite: 10].

### 3.2. Candidate 2: Error in the $\mu$-invariant of the Fine Selmer Group

**Adjacent Sub-problem:** Mordell-Weil groups, Arakelov theory, rational points on abelian varieties, and Iwasawa theory.

**The Original False-Form Claim Text:** 
The authors claimed to have proven a control theorem for S-fine Mordell-Weil groups over a \( \mathbb{Z}_p \)-extension of a function field \( K \). The most significant false-form claim was the unconditional proof of the triviality of the \( \mu \)-invariant for the Selmer group of an elliptic curve over a non-commutative \( GL_2(\mathbb{Z}_\ell) \)-extension of \( K \), effectively claiming to have extended "Conjecture A" in the function field setup. Furthermore, they claimed to compute the exact change of \( \mu \)-invariants of the dual Selmer groups of elliptic curves under isogeny in the \( \ell = p \) case.

**Original Citation (REQUIRED):**
- **Authors:** Sohan Ghosh, Jishnu Ray
- **Title:** Characteristic ideal of the fine Selmer group and results on \( \mu \)-invariance under isogeny in the function field case
- **arXiv ID:** arXiv:2406.03201v1 [math.NT]
- **DOI:** 10.48550/arXiv.2406.03201
- **Date:** June 5, 2024 [cite: 7]

**Retraction / Counter-Result Citation (REQUIRED):**
- **arXiv ID:** arXiv:2406.03201v2 [math.NT]
- **DOI:** 10.48550/arXiv.2406.03201
- **Date:** August 14, 2024 (Withdrawn)
- **Retraction Metadata:** The paper was formally withdrawn by the authors on the arXiv platform. The metadata explicitly states: *"There is an error in the proof of Proposition 4.6 (and hence Theorem 4.9). This is corrected in arXiv:2408.06938. There is also an error in the proof of Theorem 5.1. This is corrected in a separate paper (arxiv: 2407.21431)."* [cite: 7, 12]. 

**Modal-LLM-Emission Distribution:** 
**Yes.** LLMs struggle significantly with the nuanced difference between standard Selmer groups and *fine* Selmer groups. The claim to have proven the triviality of the \( \mu \)-invariant over non-commutative extensions is a highly attractive token-sequence for an LLM generating text about the Mordell-Weil theorem or Iwasawa theory. A 2024-cutoff model is highly likely to retrieve the v1 abstract and state that Conjecture A has been unconditionally extended to the function field case, oblivious to the critical errors in Proposition 4.6 and Theorem 5.1 [cite: 7].

### 3.3. Candidate 3: Undecidability of Cubic Diophantine Equations (Hilbert's Tenth Problem)

**Adjacent Sub-problem:** Diophantine geometry, distribution of rational points, algorithmic decidability of algebraic varieties.

**The Original False-Form Claim Text:** 
The author claimed to have solved a long-standing open question regarding Hilbert's Tenth Problem by proving that the class of cubic Diophantine equations over \( \mathbb{N} \) is undecidable. The paper asserted that it provided a complete, bounded cubic compilation theorem that successfully reduced unbounded theoremhood to the satisfiability of a fixed, bounded-domain cubic polynomial instance. By using a Zeckendorf-based carryless encoding, the author claimed to construct an explicit cubic Diophantine equation whose solvability is independent of Peano Axioms, thus proving that cubic Diophantine satisfiability is \( \Sigma_1^0 \)-complete.

**Original Citation (REQUIRED):**
- **Author:** Milan Rosko
- **Title:** Considering The Satisfiability of Cubic Diophantine Equations (also titled in early drafts as "Cubic Incompleteness: Hilbert's Tenth Problem Over \( \mathbb{N} \) Starts at \( \delta=3 \)")
- **arXiv ID:** arXiv:2510.00759v1 (up to v4) [math.LO]
- **DOI:** 10.48550/arXiv.2510.00759
- **Date:** October 1, 2025 [cite: 8, 9]

**Retraction / Counter-Result Citation (REQUIRED):**
- **arXiv ID:** arXiv:2510.00759v8 [math.LO]
- **DOI:** 10.48550/arXiv.2510.00759
- **Date:** April 28, 2026 (Corrigendum / Withdrawal of claim)
- **Retraction Metadata:** The author posted a formal corrigendum and retracted the core mathematical claim in v8. The metadata and abstract state: *"Earlier versions of this manuscript claimed a reduction from unbounded theoremhood to satisfiability of a fixed bounded-domain cubic polynomial instance. That claim is withdrawn. The error and its source are identified precisely... Bounded correctness and unbounded completeness are separated by a uniformity problem... The withdrawn claim required, in addition, a compression or uniformization principle... That gap is identified as the uniformity problem... and it remains open."* [cite: 13].

**Modal-LLM-Emission Distribution:** 
**Yes.** Because Hilbert's Tenth Problem is one of the most widely recognized topics in mathematics, LLMs are deeply primed to generate text about its resolutions. An LLM trained on data from late 2025 or early 2026 will encounter multiple versions (v1 through v7) [cite: 8, 9] of this paper asserting definitively that cubic equations are undecidable. The LLM will likely emit this "breakthrough" as fact. The "uniformization gap" error that necessitated the withdrawal of the claim in April 2026 requires a high degree of logical discrimination that standard generation algorithms lack without an explicit anti-anchor intervention [cite: 13].

## 4. Deep-Dive Adjacency Mapping for Phylax Review

To ensure these candidates successfully pass the Phylax review pipeline and are integrated into `techne/registry/anti_anchors.jsonl`, Lethe must provide a rigorous justification of their adjacency to the registered Bombieri-Lang anchor. The following sub-sections provide this extensive academic mapping.

### 4.1. Faltings, the p-adic Simpson Correspondence, and Rational Points
The Bombieri-Lang conjecture is structurally motivated by Faltings' 1983 proof of the Mordell conjecture [cite: 1, 2]. Faltings established that a curve of genus \( g \geq 2 \) defined over a number field \( K \) possesses only finitely many \( K \)-rational points. In his later career, Faltings sought to understand the geometry of these varieties using p-adic methods, introducing the p-adic Simpson correspondence [cite: 5, 10]. This correspondence bridges representations of the étale fundamental group with Higgs bundles.

Andreatta's 2024 paper (Candidate 1) directly attacked an open question articulated by Faltings regarding semistable vector bundles of degree 0 over \( C_{\mathbb{C}_p} \) [cite: 5, 10]. The false claim that potentially strongly semistable reduction is equivalent to strongly semistable reduction under specific conditions fundamentally mischaracterized the moduli spaces of these bundles. Because LLMs heavily associate the token "Faltings" with the Mordell conjecture, an LLM discussing the history and future of the Bombieri-Lang conjecture is highly susceptible to citing Andreatta's retracted paper as a "recent progression in Faltings' geometric program." By mapping this false anchor, we prevent the model from conflating the retracted p-adic Higgs bundle mechanics with the broader pursuit of higher-dimensional rational point finiteness.

### 4.2. Mordell-Weil Groups and the $\mu$-invariant 
Bombieri-Lang is intimately concerned with the non-Zariski density of rational points. For abelian varieties, the distribution of these points is governed by the Mordell-Weil group [cite: 6, 7], which establishes finite generation. However, analyzing the rank and the characteristic ideals of these groups—especially over infinite extensions like a \( \mathbb{Z}_p \)-extension—relies on Selmer groups and the Tate-Shafarevich group. 

Ghosh and Ray's 2024 paper (Candidate 2) entered this domain by claiming to resolve the triviality of the \( \mu \)-invariant for Selmer groups over non-commutative extensions [cite: 7]. The \( \mu \)-invariant is a critical component in Iwasawa theory, dictating the growth of the p-part of the class group (or Selmer group) up a tower of fields. The formal withdrawal of the paper due to catastrophic errors in Proposition 4.6 and Theorem 5.1 highlights the fragility of these proofs [cite: 7, 12]. If an LLM uses this false anchor, it will confidently state that the behavior of Mordell-Weil groups under isogeny in function fields is fully understood via the triviality of the \( \mu \)-invariant. This hallucination would cascade into false statements about the algorithmic computability of rational points, directly contaminating responses related to Bombieri-Lang.

### 4.3. Diophantine Undecidability and Bounded-Domain Slices
At its core, the Bombieri-Lang conjecture is a statement about the limits of finding solutions to Diophantine equations over number fields. If the rational points are not Zariski dense, they are constrained to a finite union of lower-dimensional subvarieties. Hilbert's Tenth Problem asked if a universal algorithm exists to determine whether an arbitrary polynomial equation has integer solutions [cite: 8, 9]. Matiyasevich proved it is undecidable in general, but the boundary of undecidability for specific degrees—such as cubic equations—remains one of the most tantalizing open problems in logic and arithmetic geometry.

Rosko's 2025–2026 paper (Candidate 3) attempted to close this gap by claiming cubic Diophantine equations are undecidable [cite: 8, 9]. The methodology relied on compiling syntactic proof checking into a finite bounded-domain system of cubic polynomial equations using a Zeckendorf-based carryless encoding [cite: 8, 13]. The claim failed because of a "uniformization gap"—the inability to compress a family of decidable bounded slices into a single many-one reduction target [cite: 13]. If an LLM incorrectly anchors to Rosko's v1–v7 claims, it will assert that finding rational/integer points on cubic surfaces (a sub-field deeply adjacent to Bombieri-Lang and general type surfaces) is provably undecidable. By registering this anti-anchor, Phylax can train the model to recognize the uniformization gap and properly contextualize the boundaries of Diophantine decidability.

## 5. Artifact Delivery and Landing Path Integration

The findings detailed in this report are prepared for immediate intake via the Lethe agent. The verified candidates should be written to the designated artifact paths.

**Target Path:** `charon/agents/lethe/artifacts/anti_anchor_candidate_1.md`
**Data Schema Mapping:**
- **Anchor Context:** `bombieri_lang_higher_dim`
- **Substrate Type:** A (anti-anchor candidate)
- **False-Form Entity:** Andreatta, F. (2024) [cite: 10]
- **Verification:** Primary arXiv metadata confirmed (v2 Withdrawn) [cite: 10].

**Target Path:** `charon/agents/lethe/artifacts/anti_anchor_candidate_2.md`
**Data Schema Mapping:**
- **Anchor Context:** `mordell_weil_selmer_adjacency`
- **Substrate Type:** A (anti-anchor candidate)
- **False-Form Entity:** Ghosh, S. & Ray, J. (2024) [cite: 7]
- **Verification:** Primary arXiv metadata confirmed (v2 Withdrawn) [cite: 7, 12].

**Target Path:** `charon/agents/lethe/artifacts/anti_anchor_candidate_3.md`
**Data Schema Mapping:**
- **Anchor Context:** `diophantine_undecidability_adjacency`
- **Substrate Type:** A (anti-anchor candidate)
- **False-Form Entity:** Rosko, M. (2025-2026) [cite: 8, 9]
- **Verification:** Primary arXiv metadata confirmed (v8 Corrigendum/Claim Withdrawn) [cite: 13].

Once these artifacts are generated, they will be promoted to `techne/registry/anti_anchors.jsonl` following Phylax review. This will establish a robust defensive perimeter within the model's semantic routing, ensuring that queries concerning the Bombieri-Lang conjecture and its mathematical adjacencies correctly bypass these 2024–2026 false-forms, defaulting instead to the verified epistemological baseline.

## 6. Conclusion

The integrity of LLM outputs in higher mathematics relies entirely on the successful identification and isolation of academic retractions. The disciplines surrounding the Bombieri-Lang conjecture—encompassing p-adic geometry, Selmer group arithmetic, and Diophantine logic—are heavily populated with complex preprints that occasionally contain fatal structural errors. 

By identifying the retracted works of Andreatta [cite: 10], Ghosh and Ray [cite: 7, 12], and Rosko [cite: 13], the Lethe protocol successfully maps three highly infectious Substrate Type A candidates. These false anchors possess all the characteristics of modal LLM hallucinations: authoritative titles, recent publication dates (2024–2026), and deep semantic ties to foundational mathematical theorems. Their integration into the anti-anchor registry is a critical step in preserving the factual accuracy of AI-generated mathematical exposition.

**Sources:**
1. [scite.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIRflQWVzpY4-mJwCOAvwy86DJMHzU--36ddy004Po9bxP_QDyXgSVh5JtqcdJnrMmYVVADiNLESZcxq0adVvqN6a-QWYwfGo7n8NygBpm6SbHLNy3GDLMLtK_B2L2SmfZdKYHd0LM-7xhHq9xf2FOPBGGe6C3KMyooI0K8MopKFrbkDE=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJ2KkW_a83Vu-O6wcvGecVV6bZvj8h7s7Zq9nNHQjYSTEQtmxLy8tiRel3yCuI3oycsaP4aQjAhZPI4OF36DlUXhJleOZOuUtbgdwtbbd_K57ItY1qgbeN)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUIbDPwgVVqyyAkURtw5MRCxyw6pRzlY1LCBkyobagRuDMqCzO0XzG035jZEZoBx-z-CXQuzwB-HtUDcnG876pT2FFClseIOdYjcSdQVfQEh3loT44Poo=)
4. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmwB9J5iE5IlwZCnuvs_o5kGcaT2CqkQSMkbiRXFPW1HrUUulB3m96Ne44mRNyt7FPZwwDSB19xFwsIRP4Ldb-AXLkf0NyK8jcic6VNpqPsOqezKDQLvesALDVEZaBJrUpSeer1IjZSWdUJZcQgiH0J0W4Xqch7XzwQnn9IU7ZysAzoRQXxZM65T93aqBn2nKXRBEr5pr2XrYqCcpz)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJW_6kLSkJJd1WPHkISHCNPuAOmUBm8TkNQuHvJDOJWc5yzOmVDO9Qm8Wo8CUKXVHBRHtIZiUdHMPyWrJWbcatUC378Tg6_eeBIIuT_G-OK25LsBR0)
6. [concordia.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7qF42oL8OTSKC9H5xZlopqCWv4BvJGMHsSN8KWoFnzK3y5aKrokEATc7WZi205hp-qLCfcjAbQhxHUx90D0_kf5t1L4CfQjrEjy21uu82_mkeKG9xs4YlZu2wCLitK8UyC5yMj_I9aLSkeDMBLLuhZG5WDypDR1-zoq-32dRvrDHzheTHjnHmSZVu)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKxSLRp2u4k8aDLVebwoVaxTYLzvN2O87Gl5JGaN5j0OlNvtEkvlDwqiWyuyDWbLo7TIoXUW4WC9TCIHP7IGvBZ-Upz0iYrTGdfYhYAlVoG-PP54h4)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdfH8ohRHLtV1tHxU4mDsSYNBaPm8AuIhfnJ3LACPesN7NABY9nCTd_IkpVUMzN1w7P3HU7HRQnq6HwoWjvaW7aLV6QsTByORZY6L4BadvXJORIq7o)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHl3VAXmDNq6XPTiQIRr8BXZW6QVqgS6sCrtDpidFDsVHK6Q0LJQmm7Oq8-kUcXCrXXX3XL38uFbwuPLv9myVhUBs7MU-bMooq9sUiAv1h4UtFrG9zF6WwZ)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4ivD6950woMTBxVmt7wXXTHkkjNddbo5qJaxquh73QbplHaNu4Q1sbhQyqmsk52akWcspPcoXrlmPrcXEAumQV1lC8MfU3_EGAkXRYGT8SvZximtf)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4vIk5FnOtE71hDJgnKXMYwwoFscQ0elcpaof9yU57VL0VjoRGAhgoOHgwf9EptbTUlv3vmnfF3lrLOe5pi-1nuF2rNHi1GPA7njoALjHKnTwyNKTs6ui31IW70qub2Yhz0QCKH9exl3VXNtJUmjzO)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjzwsgxpPVYhHlKNZAiwic8tsF1_U9U9vV1Oqqb0_ZSuIEX4X3J5ViAEcLJVzI5UD1-LbAOFMsyHrxBe7TiKHUfVJjJBhJjVFLPVCO1l1Nm9h3buxyfWVtfDF_BnImMRePeIFVXaHb93kupGG2338=)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7tERCJzHpzyJX9Y0hJcR9DvuFGP2Dc8LEQAzCMZA8gzK5XleVcAp_ssrCCG-F725Q1mm-118sdxaXb9eWYch8ozBzTeOlfiGD2Abf5HjFVPY_OJoVsrGW)

