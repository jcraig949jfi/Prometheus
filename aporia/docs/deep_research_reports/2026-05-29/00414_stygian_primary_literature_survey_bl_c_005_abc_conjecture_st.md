# Stygian primary-literature survey: BL-C-005 (abc conjecture status (post-Mochizuki controversy))

**Pythia queue id:** 414
**Tier:** T5
**Priority:** 5
**Requested by:** Stygian
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdUeTRaYXF1NEdQQ2JfdU1QdnB6WnVRdxIXVHk0WmFxdTRHUENiX3VNUHZwelp1UXc
**Elapsed:** 242s
**Completed at:** 2026-05-29T06:16:34.211137+00:00

---

# Artifact: charon/agents/stygian/artifacts/attack_plan_BL-C-005_v10.md

**Key Points**
*   Research suggests that the *abc* conjecture remains formally unproven in the consensus view of the mainstream mathematical community, despite high-profile claims to the contrary.
*   It seems highly likely that Shinichi Mochizuki’s Inter-universal Teichmüller (IUT) theory, while pioneering, contains critical unaddressed gaps (specifically regarding Corollary 3.12), rendering its proof of the *abc* conjecture broadly unaccepted.
*   The evidence leans toward recent, rigorous analytical progress favoring either the quantification of exceptional sets (e.g., proving the conjecture is "almost always" true) or the derivation of subexponential bounds for specific polynomial families.
*   Alternative structural reformations of IUT theory, such as Kirti Joshi’s arithmetic Teichmüller spaces, remain contested by both Mochizuki's camp and his critics, illustrating profound representation gaps in modern Diophantine geometry.
*   Current generative AI models demonstrate a severe failure mode by uncritically accepting Mochizuki’s proof as established fact, ignoring the community consensus which relies on the unconditional bounds established by Stewart and Yu, and more recently, Pasten.

**Falsification Battery Context**
This document serves as the primary initialization artifact for the Charon swarm (Operator: Stygian) to execute a v10-battery falsification attack on open problem `BL-C-005`. The substrate type is A (falsification data), necessitating rigorous discrimination between accepted mathematical consensus, contested claims, and AI-hallucinated proofs.

**Target Definition**
The target is the *abc* conjecture (Masser-Oesterlé), evaluating its exact status post-Mochizuki controversy (2024–2026 window). The problem posits that for coprime positive integers $a + b = c$, the product of their distinct prime factors, $\text{rad}(abc)$, is rarely much smaller than $c$. The battery must enrich the KillVector stub's `competing_hypothesis_id` field by deploying confirmed primary literature.

---

## 1. Systemic Operator Directives and HARD-5 Discipline

The `BL-C-005` problem envelope requires the strictest epistemological hygiene (HARD-5 discipline) due to the extreme degree of contamination in both public discourse and LLM latent spaces regarding its proof status. The mathematical community is fractured, with a small, localized contingent accepting Mochizuki’s Inter-universal Teichmüller (IUT) theory, while the vast majority of international experts—including Fields medalists Peter Scholze and Akshay Venkatesh—reject the proof due to an insurmountable logical chasm identified in Corollary 3.12 of IUTT-III [cite: 1, 2]. 

In executing this v10-battery attack, the following HARD-5 demarcations must be strictly observed:
1.  **Strong-abc vs. Weak-abc**: The "strong" or full *abc* conjecture asserts that for any $\epsilon > 0$, there are only finitely many triples $(a, b, c)$ of coprime positive integers with $a + b = c$ such that $c > \text{rad}(abc)^{1+\epsilon}$ [cite: 3, 4]. The "weak" variants, often framed in terms of subexponential bounds or restricted to specific polynomial families (e.g., $n^2+1$), do not prove the full conjecture but provide unconditional progress [cite: 5, 6].
2.  **Szpiro’s Conjecture Equivalency**: The modified Szpiro conjecture concerning the minimal discriminant and conductor of elliptic curves is equivalent to the *abc* conjecture [cite: 3, 4]. Attacks on one are isomorphic to attacks on the other.
3.  **Algorithmic Verification Boundaries**: Recent attempts to validate the *abc* conjecture using LLMs or automated theorem provers (e.g., the "Ghost Drift Theory" verified by GPT-4 and Gemini) are classified as systemic epistemological hazards and must be explicitly identified as invalid, pseudo-mathematical noise [cite: 7, 8]. 

## 2. Modal-LLM-Emission Failure Mode Verification

**Failure Mode Hypothesis:** `'abc was proved by Mochizuki' (IUT not community-accepted; Stewart-Yu is the actual accepted unconditional)`.

**Verdict:** **Confirmed.** 

Current primary literature explicitly refutes the notion that Mochizuki's 2012 proof has achieved community consensus [cite: 5, 9]. The mathematical community largely abandoned hope in the IUT framework following a 2018 report by Peter Scholze and Jakob Stix, which detailed a fundamental flaw in the proof strategy [cite: 1, 9]. Mochizuki's refusal to amend his argument using standard mathematical language, alongside his dismissal of all critics, has left his proof recognized only within a highly insular group [cite: 2, 9]. 

Consequently, any LLM emission stating that the *abc* conjecture is "solved" by Mochizuki is categorically false under the consensus metric. The actual, universally accepted unconditional results operate on a different scale entirely. For over two decades, the most powerful unconditional bound was provided by Stewart and Yu (2001), who proved that $c \leq \exp(\kappa \text{rad}(abc)^{1/3} (\log \text{rad}(abc))^3)$ [cite: 3, 10]. This remained the bedrock of accepted *abc* literature until 2024, when Hector Pasten achieved a subexponentially strict condition, proving bounds related to $\text{rad}(abc) < \exp((\log \log c)^{2-\epsilon})$ for specific cases [cite: 5, 11]. Therefore, the LLM failure mode is verified as an active threat to factuality, requiring immediate vector suppression in the Charon v10 battery.

## 3. Primary Literature Attack 1: Kirti Joshi (2024–2025)

The most structurally ambitious, yet highly contested, attempt to salvage the IUT framework and prove the *abc* conjecture in the 2024–2026 window is the multi-paper opus by Kirti Joshi. 

**Citation & Identifiers:**
*   **Author:** Kirti Joshi
*   **Title:** *Construction of Arithmetic Teichmuller Spaces IV: Proof of the abc-conjecture*
*   **Date:** Submitted March 15, 2024; revised February 24, 2025.
*   **Identifiers:** arXiv:2403.10430 | DOI: 10.48550/arXiv.2403.10430 [cite: 12].

**Precise Statement Attacked:**
Joshi attacks the full, original Masser-Oesterlé strong *abc* conjecture via Mochizuki’s Vojta Inequality framework. Specifically, the paper asserts that for any $\epsilon > 0$, the set of *abc* triples satisfying $c > \text{rad}(abc)^{1+\epsilon}$ is finite. This is formalized in the paper's Theorem 7.1.1, which purports to complete the proof of the *abc* conjecture by utilizing Mochizuki's rubric but replacing his opaque anabelian geometry with a newly defined Arithmetic Teichmüller Theory [cite: 12, 13].

**Technique/Method Invoked:**
Joshi’s method attempts to bridge the vast terminological and conceptual gap of Mochizuki’s IUT by invoking $p$-adic Hodge theory and Fargues-Fontaine curves [cite: 14, 15]. The core technique involves constructing "Arithmetic Teichmüller Spaces," which treat number fields analogously to Riemann surfaces. By creating a continuous family of "arithmetically inequivalent avatars" (deformations) of a fixed number field, Joshi attempts to quantify the deep structural shifts required to bypass the exactness barriers of Diophantine geometry [cite: 15, 16]. He utilizes the absolute Galois group and perfectoid fields, establishing a canonical geometric description of Mochizuki’s "log-Links" and "$\Theta$-Links" using the theory of untilts [cite: 13, 15]. The critical step relies on averaging over these distinct arithmetic deformations of a fixed number field to deduce the Vojta inequality [cite: 13, 17].

**Verdict Reached:**
**Contested / Unaccepted.** Despite translating the proof into a framework more recognizable to arithmetic geometers, Joshi’s proof has not secured consensus and is heavily contested by both sides of the original controversy. Peter Scholze has publicly asserted that Joshi's proof contains a fatal mistake at Proposition 6.10.7, arguing that the attempt to prove the *abc* conjecture by adding up local inequalities at each place is inherently flawed [cite: 18, 19]. Conversely, Shinichi Mochizuki has fiercely rejected Joshi’s work, publishing retorts claiming that Joshi is "profoundly ignorant" of the actual content of IUT and that his preprints lack "any meaningful mathematical content whatsoever" [cite: 1, 2]. The paper remains in preprint status and serves as a focal point for ongoing dispute rather than a resolved theorem [cite: 2, 9].

**Hardness-Signature Classification:**
**`REPRESENTATION_GAP`**. The entire premise of Joshi's work, and the subsequent backlash, perfectly encapsulates a representation gap. The failure of the community to agree on the proof stems from an inability to map Mochizuki's anabelian structures onto verifiable arithmetic geometry (e.g., Fargues-Fontaine curves). Joshi's attempt to bridge this gap highlights that the mathematical objects required to prove *abc* either do not exist in the manner claimed, or currently lack a rigorous, universally comprehensible representational framework [cite: 1, 14].

## 4. Primary Literature Attack 2: Browning, Lichtman, and Teräväinen (2024)

In stark contrast to the global, structural attempts to prove the full conjecture, analytical number theorists have launched highly successful, universally accepted attacks on the statistical prevalence of the *abc* conjecture's exceptions. 

**Citation & Identifiers:**
*   **Authors:** Tim Browning, Jared Duker Lichtman, Joni Teräväinen
*   **Title:** *Bounds on the exceptional set in the abc conjecture*
*   **Date:** Submitted October 16, 2024; subsequent related expository extension by Lichtman in May 2025.
*   **Identifiers:** arXiv:2410.12234 | DOI: 10.48550/arXiv.2410.12234 [cite: 20]. (Extension: arXiv:2505.13991 | DOI: 10.48550/arXiv.2505.13991 [cite: 11, 21]).

**Precise Statement Attacked:**
The authors attack the "almost always" formulation of the strong *abc* conjecture. Instead of proving that the set of exceptional triples $(a, b, c)$ satisfying $\text{rad}(abc) < c^{1-\epsilon}$ is strictly finite, they attack the asymptotic density of this exceptional set. Specifically, they study solutions to $a+b=c$ in a bounding box $[1, X]^3$ and seek to prove a power-saving bound on the number of integer triples that violate the *abc* inequality [cite: 20]. 

**Technique/Method Invoked:**
The paper eschews abstract Teichmüller theory in favor of hard analytical number theory and the geometry of numbers. The proof is synthesized from a combination of advanced techniques:
1.  **Fourier Analysis:** Utilized to count solutions to linear equations with radical constraints.
2.  **Determinant Method & Thue Equations:** Employed to bound the density of integer points on high-dimensional algebraic varieties [cite: 20, 22].
3.  **Geometry of Numbers:** Used to tightly constrain the parameter space of the radical components [cite: 22, 23]. 

**Verdict Reached:**
**Accepted / Published / Extended.** The attempt was entirely successful within its defined scope. The authors established a strict power-saving bound, proving that there are at most $O(X^{33/50})$ exceptional integer triples in the box $[1, X]^3$ which satisfy $\text{rad}(abc) < c^{1-\epsilon}$ [cite: 20]. This result provides the first significant power-savings on the exceptional set since de Bruijn's $O(X^{2/3})$ estimate in 1962 [cite: 11, 24]. The work is broadly accepted by the community and was subsequently extended in 2025 by Lichtman in an expository format that explicitly contextualizes this bound as proving "The *abc* conjecture is true almost always" [cite: 11, 21]. Furthermore, the methodology was applied alongside modular approaches by Pasten and Cuevas Barrientos (arXiv:2504.15971 | DOI: 10.48550/arXiv.2504.15971) to achieve subexponential bounds for Szpiro's conjecture in one-parameter families [cite: 25, 26].

**Hardness-Signature Classification:**
**`EXACTNESS_BARRIER`**. This attack perfectly fits the exactness barrier signature. The mathematical machinery is powerful enough to approximate the truth of the conjecture to an extreme degree (proving that exceptions are vanishingly rare, $O(X^{0.66})$ against a trivial $O(X^2)$ background), but the methods fundamentally lack the exactness required to prove that the number of exceptions is $O(1)$ (strictly finite) [cite: 11, 27]. The analytical tools act as a sieve that cannot close completely around the final, finite set of anomalies.

## 5. Integration with KillVector Stub

The findings detailed above provide the necessary enrichment for the `BL-C-005` KillVector stub. When the v10 battery executes, the operator will inject these competing hypotheses to force the target LLM out of its local minima (the "Mochizuki proved it" hallucination). 

**Substrate A Injection Path:**
*   **Hypothesis 1 (Refutation of Proof):** Force the model to evaluate the Scholze-Stix (2018) critique and the subsequent failure of Kirti Joshi’s arXiv:2403.10430 (2024) to resolve Proposition 6.10.7 [cite: 1, 18].
*   **Hypothesis 2 (Establishment of True Unconditional Baseline):** Override the model's absolute claims by injecting the unconditional bounds of Stewart-Yu (2001) and Pasten (2024), shifting the context window to Diophantine logarithms [cite: 10, 11].
*   **Hypothesis 3 (Statistical Consensus):** Introduce Browning, Lichtman, and Teräväinen's arXiv:2410.12234 (2024) $O(X^{33/50})$ bound to demonstrate what *actual* accepted progress looks like in the current literature, sharply contrasting with IUTT claims [cite: 20, 22].
*   **Hazard Suppression:** Implement pattern-matching filters to immediately flag and penalize assertions validating "Ghost Drift Theory" (arXiv:2508.xxxx/Zenodo 16746726), a documented 2025 hallucination vector where AI models self-certified a mathematically vacuous proof [cite: 7, 8].

*Execution parameters validated. Artifact ready for v10 deployment.*

**Sources:**
1. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHASIjgU4tja2TCLgIjJuix-leXDGruDYVBH4j_y0BXEoGh-dIdA0ug3ZSN9toi0uYLUNs19klkoFj9nJYiQGiGUgzImRhGPRi2XpySJrN8Sq_IGzwG4-D8k2C9LVDAQgV-F0AsBA4tI_GmJKA=)
2. [international-maths-challenge.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHy6n7gbHBJs-CZvi_gyOk-m1NMNhnT_BWYYqffaucvSxJUAHoXT7oGFfVukuyFXaNRl22bH0Pwg8pjqaQY3y1nXLuuEEC6QkHdICIcrGtazAGxH6w6gD_fXjBOzmh2DEHfA4MfS581wMhF4b5eSFbwX-SGhddTmxxXTPF2xI6GMUc7ozKEBf39HllMWiQDMwdbLnXbS5za5_Jt21w0xvU=)
3. [imj-prg.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsvEIUUFeaisx2YOOTw7ChSknUpedim11ozfUZiBUM1DwNuRpyoNTPNUxoFgJJ99b8r1KfRmlSSHFIC9-9udA6o2lwY210IltiRTb5IYu9TA0Q4aHngxWyYGZeQSzkcQk68hf-taGPb9YvUd6fT-8Jrdr8TZFlM-n1GeXKyz2Q8U2eNNWNl4MCFAzX)
4. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0BFOoWLKomp1xkYH-uG_tYZbQYaI8feYqplEZZ5N294uSIKOGkPK0v-v1rZY4xr941HFkFX-YW_Qn6Z0zp-CN2nuQr1kqrDJkej8eHAGWuwlYCcyq0vmOES9FcmiZnCciMA==)
5. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzho3rHS7WsWqe5_xVRCv2ZrHPK22pfgUOTrXiCM3-4f1gOjseYnd0FPzsdHCB7vE9ZvIsrFe5X6JLMvOc_5Al6sZ9pWdFJAvM1FG-0IxoALc-z8UkE7w84DKwpHaYVFTtx7lQzzDqa0gdfvxJN4l7ST-I7QFQPRpT2ftuIe3OVG2q1ddeT4r3jpcZJMKEIcMYfQ65ryBnpzKhRbVHJCn6DaLm7ByL)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlcYtMzE0MS66b5MMzWYysqHMEUeg4FtS80xmQAuoj8SJW0dgxoHsJgeXBzo3XprkyDRz0s_TsisQEjSXv-wno4FQGKXx7dqdZhXn0CWu7WfJ7Bh78dg==)
7. [ycombinator.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyRivNlRoCB8ePDdvd1r-_4IUce9vtR7vWLX5-YBSJ9fzr0YFOf67iLwOdyzCJkP4jcqYKknWsDtrqC5LcxRVr2kxRjSaCG_VQ2PSGwQb_wA618aCVjuR0noqvwYwDjh38e7A=)
8. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGj3M40ZxJDB3kCA582IhUyMcZWZ8g0LhLbVZzmmHBUqpc3GOf-vQ3Nr7UM6zLozMNFe2Jh4tiVZw9Yr-ikJ-T7EyLfyQLYB0v9atNaEo07ZrPrWZkpt6ig7shLOHttq6dozbsDahEo5ozIWwcEKh5hPTtwDh8Gp3ykXzuXb4EK7zh5Y4gvMYuzcMIYle96Xn74gcw5NhOHeBc3Lax1doXZVB5sMsO9pT6YH1D5w4s=)
9. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxt2_-Aqe8XliGfec145vuzlApEIboFSRW2QoN_bzmLZN4QULTbIo0Wm-RXnVT6h5dllGoWpIdAg-2zJEAEED3ylgmjt0wHVXUGO5mewoXg_dYLkg_xfZLSicmkO312IA0SDgCBV1jnLlqQiGtuUxPBLbqvgDboHkP)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQl0mSHEjNgnwxnkbqupoiiUxJxsUZBCHdUyVBr4GUBtW112HSYjGY7bPRHN0K2-NwSh7kBAqSVlnIIEiIQxLK-nz0M3rUI6cUV-7y-ZsZMfdE7nEO35FDsQ4Z-Nd1vrhncef7j_OwLShbTk_pirE16-6agoystoWYT3QNbI9wDxc=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuBT3HK83DEbeTLCtAhSov9BP11rsQFpcitb1J8nckztzwf_F9kAOs6EiXCZ-96nmI2lLlJwyMS1kk9segg-715bAks4dkkKJdIxfsvjFYMtFQGJ9EvA==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGY6La6oy9IVc1YdScjaZkmm6hAEJXiESKf6HDOhUdewSUCiMDTKmprBVQMOsehkvrMEeYtoX8C3VaokyVOEuuzi9q33hyjjXUpuaBKC2VtWJuXWwAyJw==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2wYf6j14lKCnjJ4qJUL1cxtJ8wgjSrGGul9CBuGy4ZWSFIu7gVuWhE1cVp2vr3UKPOT9TK0O6dqp68wr2G6HYw3Pg0oIKhml_vYml1YoMQcaX5koxWA==)
14. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLvnNY9qcUR549L9YccI3fP_DebwYBlEL5RrdYVnX9-wrFeubJYHIrOpQKNjGU8_cFUc-64u9hLVUTqM1j2pIxnP-KltJMo_48cTVT2ptyQ6mgQolTgEQQ8a2LFyttwAkHJA==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_0fIP8M8RylMOzKtqIswQYh5Fhfp8RZU_c2skxHwYB1P8Ld02PR10fAFlgmPLpw8HlcGa4ofBi3U17CuaSzSCRiWDCgvYN2iud19WMvszFRlueAQG4tFAlg==)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5aYYIPSXX7j23MJX5ibsb67nL3r9EngJH7QGgQm2gtuuQ-6Sdb9Dp8S9G20FMVWstDMSl6c0flsNlvjYdnEfaE_jQJvQtXWnjcEqQ_e5HafgANp062bET1Te6j4YFZhqryEmtkL5p_m02UcnfdcWJbIlUxdmPGxDq3ge0aYU86DhtfkO3YUor-o_TmNiqNpzOqg==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3IYODbikIUrLAuyIXDLl73wEpxBKuIVeAS5vrwf1JZn311AjssDpe2tUfQVJ8_IXNX3oQnFnvh1amwuI8pNGbNGE5vFBFJWTDDsOdrHxnrc104pqrm7D6ig==)
18. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEP-1rPHfncexAyNIPVC7Ji-wPYFLf6x5tFtef5Cfg_wkOIWy9U-wsvkAe6ro2_IMx73eS9MqifPN3Pr-yRMIcTNiERVWAoXKEtDbDZ3VjHZHEnHwbCceM3xcQ4BYc2F0AQV4My4QRdJlxTIJ__xMN-T2iTV3B2TqOtTVa_908NkC5oN5_SiPnX7Mso)
19. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpd0kSdUHAoLBZFbEcG8vFmp2PDgKb5p7mSXjjCXwX3kyy3KaHOb9hEwmw7-mqAQ2oI6IeE66ERze6fJ1YeuhTSmhaQ33x1tMrkhXYKyM44z3bASsENSkxjdPKlidZ8Vat_gITyN7ZmuQi6LYyZi3W8_bsvC06V_wMKJaBQIaoOjNI1jc6rzbYB2X74_KlEKExnA==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHU0bBLZylLc5CB0cVnFpNDj0EaRzCQF2jcoFeO2U11qElgk8kZMDlWWpiBDz5vLybz7qpUA4ZJAxT1v3rPgZmLXVaYPmt6_blDWWPSX8opHj9X70FOng==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTrJIs_ijY4k1ABht2Lx4QapE6nnTp03pqNZv9pqkTG9kOLFRcvVNlWbHV6VkLLijySg4nTuHgLCYl22xkW1IyG_fFOya2lC_pUodAhcFCEiiKaW7sCQ==)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVXTF9cZ_dIgdiocBB7Mgj2maCUa7OgbG6UMRmXkZnPrKJotMCmxjNmk4nXj1aOg2IdoJymxBrGvG8WYYsmozsYAvxDefmnw6Af9o63hSwasW1ELx9SG9V6x0lNKcQqTryu447srFcmuXDCcPpUjrS6YOHo7YAZ5BuAalTNw-6d-MQJyoebexarGPGZyiY8kx3beB8U7my-3wUjTs=)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHta7lQ75QiLSbfJ2sWWAoWlvFnhw6ESI2oLKQx2NHGbCp1mE-aqXHhV0a5mhSbmb7zYG1B8tX1I1ViFQnAMCaOZ2Q0FyhfIzvUpQwc7yLS0nzNZe88eUD1fQ==)
24. [cirm-math.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRjAe6u2hbiN4VZpucknCoOppm1sRdslUXOm98LEXVGuj1nUNIO4ZaKEwLvpMeL9AEF4GSZscXpuBb86lzyFLdC_b4JssyknfN-njpJ9KvjoQOzbr-n8PPC5DROq3v4VtjUKaUJltUUElnMkvc5o3Gt3m0tQ==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHms8rymdwOi1uVezAX9EkcT82T982csdXzyS2NRKfU82a-wFO0r-lHRpY05QlSnaIcV1_w0gB6-10qypFxMyLVlchxNDhOMyDbZlUqvU-sGvkxmAv8Wg==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZyIrPxkbSODALweUxQeh5e5VxoYWBy1AdOcga7IZMWOWRKYOqWvKAfSbHaoW0ZVpI7xbjFTHvlLCNUnGKgl9TJOfqQppFdjdeQZFsELmywSwcHrrlLg==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjjwYsYIysgkzI-p7EMQLLO33bFQndFyJRb-6IBNdkEWlysWuZbd_3_LVsSxYDIItInxmQJXKH37BjcOZRucOKbbI7B8rY_97N-x1BVkkFygTFFBs-BA==)

