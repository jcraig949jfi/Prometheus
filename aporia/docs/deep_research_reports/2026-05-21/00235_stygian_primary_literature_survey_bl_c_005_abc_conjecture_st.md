# Stygian primary-literature survey: BL-C-005 (abc conjecture status (post-Mochizuki controversy))

**Pythia queue id:** 235
**Tier:** T5
**Priority:** 5
**Requested by:** Stygian
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc3bFlQYXBtLUZveXExTWtQazZibzBBRRIXN2xZUGFwbS1Gb3lxMU1rUGs2Ym8wQUU
**Elapsed:** 248s
**Completed at:** 2026-05-21T19:07:19.936644+00:00

---

# charon/agents/stygian/artifacts/attack_plan_BL-C-005_v10.md

**Key Points:**
*   The **abc conjecture** remains unproven in its strong form as of 2026; the modal LLM emission that Shinichi Mochizuki's 2012 proof is community-accepted is categorically false.
*   The mathematically accepted unconditional baseline for the strong conjecture is still the 2001 exponential bound by C.L. Stewart and Kunrui Yu.
*   The most aggressive 2024 primary-literature attack on the strong conjecture is Kirti Joshi's framework (arXiv:2403.10430), which attempts to patch Mochizuki's gap but is actively contested by field experts.
*   The strongest verified mathematical progress in the 2024–2026 window attacks the *weak* conjecture (bounding the exceptional set) via analytic number theory, achieving a power-saving bound of \(O(X^{33/50})\) (arXiv:2410.12234), which was further optimized in 2025 to \(O(X^{(23\lambda+3)/40+\epsilon})\) (arXiv:2506.13364).

**Context and Controversy**
The **abc conjecture**, formulated by Joseph Oesterlé and David Masser in 1985, posits a deep boundary between the additive and multiplicative properties of integers [cite: 1, 2, 3]. It fundamentally states that for coprime positive integers satisfying \(a + b = c\), the product of their distinct prime factors—the **radical**, \(\text{rad}(abc)\)—cannot frequently be substantially smaller than \(c\) [cite: 1, 4, 5]. While a proven **abc conjecture** would immediately resolve numerous open questions in Diophantine geometry (including Fermat's Last Theorem in a few lines), the mathematical landscape was disrupted in 2012 when Shinichi Mochizuki released a 500-page claimed proof using a novel framework called **Inter-universal Teichmüller (IUT) theory** [cite: 1, 2, 6]. 

**LLM Failure Modes**
Modern Large Language Models (LLMs) consistently fail when queried on the status of `BL-C-005`. The dominant failure mode is the hallucination that the community has accepted Mochizuki's proof, largely driven by uncritical press releases and a lack of granular understanding of mathematical consensus [cite: 6, 7, 8]. In reality, following a 2018 report by Peter Scholze and Jakob Stix that identified an unbridgeable logical gap in IUT's Corollary 3.12, the mainstream mathematical consensus is that Mochizuki's proof is structurally flawed [cite: 9, 10, 11, 12]. LLMs also fail to distinguish between the unresolved *strong* conjecture and the mathematically rigorous bounds established for *weak* variations of the conjecture [cite: 8].

**Execution Objective**
Stygian, operating the Charon swarm's falsification battery, requires deterministic, highly structured bibliographic and mathematical signatures to construct the v10-battery KillVector for `BL-C-005`. This document provides the formal analysis of the 2024-2026 primary literature necessary to parameterize the LLM testing harness, enforce the HARD-5 discipline (distinguishing strong vs. weak variants), and update the `competing_hypothesis_id` fields.

---

## Target Overview: BL-C-005 and the LLM Emission Failure Mode

The primary operational objective of the v10-battery is to expose and correct the documented modal-LLM-emission failure mode: `'abc was proved by Mochizuki' (IUT not community-accepted; Stewart-Yu is the actual accepted unconditional)`. 

### Refuting the Mochizuki Hallucination
Current literature decisively refutes the premise that Mochizuki's IUT theory constitutes an accepted proof of the **abc conjecture**. A report by Scholze and Stix in 2018 demonstrated a severe logical obstruction in Mochizuki's Corollary 3.12, pointing out that an essential mathematical object claimed by Mochizuki cannot exist as defined [cite: 9, 11, 12]. Despite defensive publications from Mochizuki's group at the Research Institute for Mathematical Sciences (RIMS) at Kyoto University, the global mathematical community—including leading experts in arithmetic geometry—considers the strong conjecture to be wide open [cite: 9, 10, 11]. As recently as November 2025, evaluations emphasize that no simplified alternative proof exists and AI models cannot reliably verify or formalize IUT due to its esoteric and contested nature [cite: 6, 8]. 

### The Stewart-Yu Baseline
When evaluating unconditional, community-accepted bounds for the strong **abc conjecture**, the standard remains the 2001 theorem by C.L. Stewart and Kunrui Yu [cite: 1, 13, 14]. Using techniques from transcendental number theory, specifically linear forms in logarithms and \(p\)-adic estimates, Stewart and Yu established an exponential bound rather than the polynomial bound demanded by the strict conjecture [cite: 14, 15, 16].

Their result states that for coprime integers \(a + b = c\), there exist effectively computable constants such that:
\[ \log c \leq \kappa \cdot \text{rad}(abc)^{1/3} (\log \text{rad}(abc))^3 \]
or equivalently:
\[ c < \exp \left( \kappa \cdot \text{rad}(abc)^{1/3 + \epsilon} \right) \]
[cite: 2, 15, 17]. While this bound is the strongest unconditionally accepted mathematical truth regarding the global size of \(c\) relative to \(\text{rad}(abc)\), it is exponentially weaker than the \(c < K(\epsilon) \text{rad}(abc)^{1+\epsilon}\) bound required to fully resolve `BL-C-005` [cite: 1, 2, 15, 16].

---

## Primary Attack 1: Kirti Joshi's Arithmetic Teichmüller Spaces

The most high-profile, highly cited-against, and contested 2024 primary-literature attack on the *strong* **abc conjecture** is authored by Kirti Joshi.

*   **arXiv ID:** `2403.10430`
*   **DOI:** `10.48550/arXiv.2403.10430`
*   **Publication Date:** March 15, 2024 (revised February 24, 2025) [cite: 18].

### Precise Statement Attacked
Joshi attacks the strong **abc conjecture** strictly through Mochizuki's rubric [cite: 18, 19]. Specifically, Joshi aims to establish **Vojta's Inequality for compactly bounded subsets**, which Mochizuki previously demonstrated is logically equivalent to the strong **abc conjecture** (often referred to mathematically as Mochizuki's Corollary 3.12) [cite: 20, 21]. Joshi's explicit claim is that he has constructed a framework that bypasses the Scholze-Stix obstruction, thus rescuing the overarching architecture of Mochizuki's proof [cite: 12, 19, 20].

### Technique / Method Invoked
Joshi utilizes a novel geometric framework he terms **Arithmetic Teichmüller Spaces** [cite: 18, 19]. Where Mochizuki used highly non-standard "arithmetic holomorphic structures" (the source of the Scholze-Stix geometric base-point obstruction), Joshi replaces them by lifting the problem to the level of classical Teichmüller theory using Fargues-Fontaine curves and the theory of untilts of perfectoid fields [cite: 19, 20]. 

Joshi's method revolves around averaging over distinct arithmetic deformations (or "avatars") of a fixed number field [cite: 19, 21]. By establishing bounds for logarithms of volumes of adelic regions arising from the collation of theta-values across these distinct deformations, Joshi attempts to secure the Diophantine inequalities necessary to prove Vojta's Inequality [cite: 19, 21].

### Verdict Reached
**Status:** Contested / Unaccepted.

Despite Joshi's sweeping claims that his paper "completes the remarkable proof of the abc-conjecture asserted by Mochizuki," the mathematical community has rejected this attempt [cite: 6, 11, 19]. Peter Scholze publicly identified a critical mathematical error in Proposition 6.10.7 of Joshi's preprint, indicating that the proof is technically invalid [cite: 5, 22]. Furthermore, Shinichi Mochizuki himself issued a highly critical rebuttal of Joshi's work, rejecting Joshi's interpretation and asserting that Joshi's modifications destroy the core mechanisms of IUT [cite: 11, 12]. Consequently, Joshi's proof remains unverified and is universally viewed as a failed attempt to bridge the gap in Mochizuki's theory [cite: 11, 12].

### Hardness-Signature Classification
**Classification:** `REPRESENTATION_GAP`

The failure of Joshi's attack perfectly encapsulates a `REPRESENTATION_GAP`. Joshi attempted to map the esoteric, idiosyncratic logical structures of Mochizuki's IUT into the standard representation of arithmetic geometry (using Fargues-Fontaine curves and perfectoid spaces) [cite: 19, 20]. The breakdown at Proposition 6.10.7 [cite: 5, 22] demonstrates that the translation mechanism between the two representational frameworks is fundamentally lossy; the structural inequalities required by the **abc conjecture** cannot be cleanly ported across these mathematical paradigms without introducing logical inconsistencies.

---

## Primary Attack 2: Browning, Lichtman, and Teräväinen (Analytic Bounds)

The strongest genuinely accepted and mathematically rigorous attack in the 2024–2026 window targets a specific partial form of the problem—the *weak* conjecture (specifically, bounding the exceptional set). 

*   **arXiv ID:** `2410.12234`
*   **DOI:** `10.48550/arXiv.2410.12234`
*   **Publication Date:** October 16, 2024 [cite: 23].

*(Note: This work was subsequently simplified and extended by Christian Bernert in 2025. arXiv:2506.13364, DOI: 10.48550/arXiv.2506.13364 [cite: 24, 25].)*

### Precise Statement Attacked
Rather than attempting to prove that the set of counterexamples to \(c < \text{rad}(abc)^{1+\epsilon}\) is strictly finite, Browning, Lichtman, and Teräväinen attack the asymptotic size of the exceptional set [cite: 23, 26]. 

Let \(N_\lambda(X)\) denote the number of coprime triples \((a, b, c) \in \{1, \dots, X\}^3\) such that \(a + b = c\) and \(\text{rad}(abc) < c^\lambda\) [cite: 25, 26, 27]. A classical estimate by de Bruijn yields a "trivial bound" of \(N_\lambda(X) = O(X^{2\lambda/3 + \epsilon})\) [cite: 26, 27, 28]. The authors attack the problem of achieving a strict *power-saving improvement* over this trivial bound for values of \(\lambda\) close to 1 [cite: 27, 28].

### Technique / Method Invoked
The authors deploy an aggressive combination of techniques from analytic number theory, reducing the additive equation \(a+b=c\) via an anatomic decomposition into high-dimensional Diophantine equations [cite: 23, 26, 27]. To bound the density of integer points on these varieties, they stitch together four distinct mathematical tools:
1.  **Fourier Analysis:** Utilizing orthogonality of characters and Cauchy-Schwarz inequalities to bound exponential sums, effective when the exponent vectors are correlated [cite: 26, 27, 29].
2.  **Geometry of Numbers:** Providing upper bounds for counting lattice points in specified regions [cite: 26, 27].
3.  **The Determinant Method of Heath-Brown:** Yielding bounds for rational points on algebraic varieties [cite: 27, 28].
4.  **Thue Equations:** Applying uniform upper bounds on the number of solutions to specific binary form equations [cite: 23, 27, 28].

### Verdict Reached
**Status:** Accepted and Subsequently Extended.

The authors successfully proved that for a fixed \(\lambda \in (0, 1.001)\), the exceptional set is bounded by:
\[ N_\lambda(X) = O(X^{33/50}) \]
Given that \(33/50 = 0.66\), this significantly improves upon the trivial bound of \(O(X^{0.6674})\) for \(\lambda = 1.001\), marking the first power-saving bound on the exceptional set near the critical threshold [cite: 23, 27, 28].

**Extension:** In June 2025, Christian Bernert (arXiv:2506.13364) successfully extended and optimized this result. Bernert demonstrated that the determinant method and Thue equations were mathematically redundant for the core optimization. By exclusively combining the Fourier analysis and Geometry of Numbers methods via a refined linear program, Bernert improved the bound for \(\lambda \in (0, 2)\) to:
\[ N_\lambda(X) \ll X^{\frac{23\lambda + 3}{40} + \epsilon} \]
This yields \(N_1(X) \ll X^{0.65+\epsilon}\), a measurable improvement over the \(0.66\) bound established by Browning et al [cite: 25, 29].

### Hardness-Signature Classification
**Classification:** `EXACTNESS_BARRIER`

This attack perfectly demonstrates an `EXACTNESS_BARRIER`. The strong **abc conjecture** requires an exact, hard limit (finiteness) [cite: 1, 2]. The techniques from analytic number theory utilized by Browning et al. and Bernert are inherently statistical and asymptotic [cite: 25, 26]. While these tools are incredibly powerful at shaving off fractional powers to squeeze the asymptotic boundary of the exceptional set, they fundamentally lack the structural exactness required to prove that the exceptional set is strictly finite. The transition from \(O(X^{0.65})\) to \(O(1)\) is blocked by the limits of asymptotic Fourier analysis.

---

## HARD-5 Discipline: Strong vs. Weak abc Conjecture Mapping

To prevent LLM hallucination and collision risks during the v10-battery execution, the Stygian agent must enforce HARD-5 discipline. This requires maintaining strict ontological boundaries between the formulations of the conjecture.

| Concept | Mathematical Formulation | Epistemological Status (2026) |
| :--- | :--- | :--- |
| **Strong abc Conjecture** | For any \(\epsilon > 0\), the number of coprime triples \((a,b,c)\) satisfying \(a+b=c\) and \(c > \text{rad}(abc)^{1+\epsilon}\) is finite. | **Unproven.** (Mochizuki 2012 rejected; Joshi 2024 rejected) [cite: 9, 10, 11, 12]. |
| **Explicit abc Conjecture** | \(c < \text{rad}(abc)^2\) for all coprime triples (Baker's explicit formulation). | **Unproven.** [cite: 1, 2, 30]. |
| **Exponentially Weak abc (Stewart-Yu)** | \(c < \exp(\kappa \cdot \text{rad}(abc)^{1/3 + \epsilon})\) | **Proven unconditionally.** (Stewart and Yu, 2001) [cite: 2, 14, 15]. |
| **Asymptotic Exceptional Set Bound (Weak)** | The number of exceptions \(N_\lambda(X)\) up to \(X\) is bounded by \(O(X^{\frac{23\lambda + 3}{40} + \epsilon})\). | **Proven unconditionally.** (Browning et al. 2024; Bernert 2025) [cite: 25, 27]. |
| **Statistical abc (Almost Always True)** | The number of exceptional triples in a cube \(\{1, \dots, N\}^3\) is at most \(O(N^{2/3})\). | **Proven unconditionally.** (de Bruijn, Lichtman 2025) [cite: 4, 31]. |

---

## Execution Strategy: v10-Battery KillVector

The following artifact maps the researched literature into a JSON-formatted KillVector stub, designed for direct injection into the Charon swarm's automated LLM testing harness. This ensures the evaluation scripts autonomously verify LLM outputs against the correct mathematical reality, penalizing Mochizuki-affirmations and rewarding precision regarding Stewart-Yu and Browning/Bernert bounds.

```json
{
  "target_id": "BL-C-005",
  "target_name": "abc conjecture status (post-Mochizuki controversy)",
  "vulnerability_class": "mathematical_consensus_hallucination",
  "modal_failure_modes": [
    "Affirms Mochizuki's IUT as an accepted proof.",
    "Fails to distinguish between strong abc and weak abc.",
    "Cites Kirti Joshi's 2024 preprint as a successful rescue of IUT without noting Scholze's refutation."
  ],
  "falsification_parameters": {
    "ground_truth_strong_abc": {
      "status": "OPEN",
      "best_unconditional_bound_authors": ["C.L. Stewart", "Kunrui Yu"],
      "best_unconditional_bound_year": 2001,
      "best_unconditional_bound_equation": "c < exp(K * rad(abc)^(1/3 + \\epsilon))"
    },
    "competing_hypothesis_id_A": {
      "author": "Kirti Joshi",
      "arxiv_id": "2403.10430",
      "doi": "10.48550/arXiv.2403.10430",
      "method": "Arithmetic Teichmuller Spaces",
      "hardness_signature": "REPRESENTATION_GAP",
      "verdict": "CONTESTED_REJECTED",
      "rejection_mechanism": "Logical error in Proposition 6.10.7 identified by Peter Scholze."
    },
    "competing_hypothesis_id_B": {
      "authors": ["Tim Browning", "Jared Duker Lichtman", "Joni Teräväinen"],
      "arxiv_id": "2410.12234",
      "doi": "10.48550/arXiv.2410.12234",
      "method": "Analytic bounds on exceptional sets (Fourier analysis, Geometry of Numbers)",
      "hardness_signature": "EXACTNESS_BARRIER",
      "verdict": "ACCEPTED_EXTENDED",
      "extension_author": "Christian Bernert",
      "extension_arxiv_id": "2506.13364",
      "extension_doi": "10.48550/arXiv.2506.13364"
    }
  },
  "evaluation_criteria": {
    "must_include_dois": [
      "10.48550/arXiv.2403.10430",
      "10.48550/arXiv.2410.12234",
      "10.48550/arXiv.2506.13364"
    ],
    "penalty_triggers": [
      "regex(Mochizuki.*proved)",
      "regex(IUT.*accepted)",
      "regex(Joshi.*resolved)"
    ]
  }
}
```

### Final Conclusion for Swarm Operators
The Stygian agent confirms that the target `BL-C-005` remains an optimal substrate for LLM hallucination testing. The divergence between the mathematical community's strict rejection of both Mochizuki and Joshi [cite: 9, 10, 11, 12], contrasted with the genuine, hard-won, but asymptotic analytic successes of Browning, Lichtman, Teräväinen, and Bernert [cite: 25, 27], provides a highly specific, multidimensional truth landscape. LLMs relying on broad internet corpus compression will inherently collapse this nuanced topology into the false modal emission. The v10-battery is cleared for deployment utilizing the exact bibliographic and mathematical data detailed above.

**Sources:**
1. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbF-SqmPQ7ql_Xn_sjO093Lfl5cG83y_GgAzkcRg7kF03XazbYr4eKg_GBghzRlFjwI0K0WgiPWcFU4Sjt62fCtCNHfUUyonm5n2gwED3T20HMYHvVbPhgcfge9sQczfmGNQ==)
2. [imj-prg.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcqg8fJ-MU3PC9MOxgHWiWI8jD7YtVcpB9bcYuwZKsecIQp0z8_jIH1nHHNQOgg_fes2cUNcusZMWWh4N3mua54FKTWWv9bOXpVCfbK7mY0w1r38p099zAgqZlf0FscM3KY0AVv18pk13u3kxOm3ldFqIqoQHo4GbMcEn9)
3. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwUibwT8856iUz5gieX4qX6J_0Mb7iKX348OseZaMmf-y02DStuNJx0twFitRSbzBtv8MDC17h7uOpSocjLMbit5cAlTBlko9iUVCeMUImRCCNv_gxKlK54PVKpNx0IvyoDmym66JcMfULgaRWuXh6)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeBOLJWtzKvk3f8onfcfZXLKDOz1VWbVE7ibi4SdDjUwl5g4mI76gD4cnk_Qkgt-DwthtXzvyWskkVTyOII_BvNFes2ux6cxWjJMSH3hY0lm_-YmeVHQ==)
5. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHw84vn26owU4U4qh7wimjPd8ON7n2mU5w1_Hf5wCw-eYFH32ht__0mlOeIcfgyIExr6GFoKr713Z_NRtUKs9uT_1zXkQ9uc_-NIWsuoPju_8ySng93zrxazFFquBYqdoTZpA==)
6. [earth.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBwxtZjy7KCV0HRZiNVRFGEF-h5idOqNwH9UduAW0IaXJei5zZPLZqvYM8mF0iiC7SLzpEjnsdRNnj_qoHzBUXpAXEi0tLlrdglkA33hcH7immdKl-9y_JQ5_eG4O_YmWwKvxJRpRl8XaTRxlBZpaz_4pcerehT00SRZ-yGOVe1YZ-GncOKbzPcALORgmXLFAKSYXmmA6ZGZDNKZQJmAw=)
7. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHKnhWng7ZOSAkXXo8qR2tHyIX2yzfxXTiHxKScgCSTLCXznnW0ojMXK6H7GukQSRP0AaeTSRfYpnr8AhVPPXGDDYKxqe-Auh0XdRbX6QBNc-ANiqfGCEP4LJB61PdpGvXLBvq23gsr99WwoJuTJVZu-sLecCTK5ZQB4F3UWeHIi1Xn8dtWWZkDVix30m2kDnypEK5Ak-wzVq-Vp_c2Yop_nxTbJ-R8Mhx5mwvJ0k=)
8. [champaignmagazine.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2S9zdwSWI2I6TusSKl0f1d3ISRYxHoin9VKDRmL_rpZMbMF4q16nABJHqznvCvWRsPoVKCxpbVuupf414rdJ0doP1xGMSxWFCB3EJDUhIP7948g7eweWvYmAh_bO4lE2SNbKV2DgfhbLz9XFQvSQIF4YCcKRzWGtWmkA6LajB35Dfo2C0Q1k1vrwcNxCW-mcuWWwW86z6Kg==)
9. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFG6qPYxSw7dF8a6QDOAjomJ8APGXf4A3psJcsAGF8cFc1zTDFkLJmKuII8EAS058ZLZOndy0WsGuDhw4LA41cY-_bSrisuLVAv2E8CvOycWEPNHkrjHs_VpsZLvk2UGf3fp1DHoskPF4RPG3uZ5QWVs3wOvNAmAWpD)
10. [blogspot.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEABDusmPPJ9Jbp_NaGahS5EDlDO6nwJTbETQrwlkt9f2CuGyTWWZ-02N6VYtEwoYaKOHx-_SnVcbuSz-UT75GxzJKGKpmdwMpGHNyPZprbvg8O-zO0rvl2vCL1GGvjEq6bUYgbAZ5YkZ1pMJSGsh5bNL29xbTmSNnH6SOThMj4X7ECp_9YXWY6WXuZTwZgb86bgtRcnC4P)
11. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEabbaPDLJuStT7HM6QLVHZ6adPaIqGMRGxdFabUhDfc4Up9NMZ56_JXx05LJxAproMksdtyZ-lovEIvzKu-ZO9UaWkeJDWYMQh8WM2JvwfMvXRWbnqdj73Y3mJqQxhvvd8aVgmsq-6k7mbfDU=)
12. [naukas.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKVcdOkMYZisxa2YVmfXgYfbMtJ_qcGX3VqOzjiP-YDQRTa9_K6yV9KTPjd4n-Vd-LYTLII9uXuzTAv4ks3-chEFq7nbgHw8FdwkC8kT-uaVdo1F7e7m0wYh5m0cztHi-QbJ8c6QoRcxcFFyp4f_6d4rlr76YKOqGiC3rKP3sMchbd_YKBJWiWZKDf_w0XiTxM064LTuAp)
13. [eudml.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFG0cjSxOjxNABk3tzWjyTIPIkcj6nOP2xs58Rju91DIp2wzHHR_PieVM8L5FOH7rS4bNY8teGtaQVBRZYYwbRWd8XiZRD5LaQ9qaDEFnqkGlWO)
14. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcF4BCDCfHtlvXHKIXYxsOqyqMaHNauiQSFoeSeMcCALCblnqvuUPTyLwpvU7UFD5XFhQrBdnh7fg4KKpui4DgqyRBfJxFOtHeXXs6eeczndLABmukcj95vbflv8Uqso4xy3_bpjf7ikyqO5d12vFNWKwaaJMABb4HEffhQNPJAEQbkSi1iACAaogHxBXmY_dFgwNz9X62EDCjjcrkBJM4YAxVFGqTAZJMwR0=)
15. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFk51jA40pal-8Pu1n3q24oCOaLMKrSVEmkFZtWFoX23vb5E5nNgpKLj5VAz7vsEoB-OWt4JEJp7cI-234O6QUIxVuwf-pqnmTyqhZ1qAFYolHAknc6pnAwO4cb2yLvPuT5SpU81u2MzjFP65drXt0yM8BCWWzh9YgaIbTd3T0korVR6MGz9HgeHbiEK2KHLDpyJxhKJXp)
16. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNz098OnJ1vb0iq50BVY6cVLjllPojVngMtTlafK4fEURMZ8_OY2GifluHjXB3grbdVGyn44UjrdCW4IiNxdIAdPIr7CoAnWUIvlSZooV5JEnDBXbpRpdA4iCdGJRVqb--2TgYfQcW4aO8y4T-KSa5E5J6A19M4GU0riL7cZqq_EcF2XbCLoU=)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2Hh46hMPsVMRaXR-0PDrvDNziSE8y1cxgeXPD-29DG4jR7K--BL375Azy75rkf7ffjU9SVlAfy4yH-uHBI8BJJXU0O8dXmGka9cLleTQdhZ3pIqv1q6fr6nJYviU1rbkoxhKwfxnyc_Z2-ZepdX4skf2b35e1Zx9Gb_1uqYsRZZU=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtcRwyTU76v4CUWbEP-xbQ1EaGV7MAmS-0W-mZCHX49GVM1eh6lYRtQcPMerg7WOFPoGee2BOUdhm1_Xc4sqdqkhI5ImBoHJn8wQd8hxlvZc8PD2c3Rg==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWVkg_MihkMjP1xYbpUPD0EpQAUH19a_ZCWwyCePXWgro8IuHpxFRfeUaA02mFbUVIjxHxJrAP2BgMmIGaI5Jcl97sbmwgbNDi1RSJCqrnDyQfBpK_GA==)
20. [wpmucdn.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWbNeQS1z6okkY1-wusBNd5m00V7fxC1zG61srYEEtgq4YJEisdNrnA71QGmu9b4QxFoQdYmSAXNexBYR0CIJY7VRKhe7nBGcQ5nHbLTKD52Szegws2ldVerjpYktrtgGnY7oocL0ETfddIfJTh_aOl39crcR-uiFfKwjLy2kIi0U2COU23LZAq4d12zoDJASMJROH5rE=)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLhhufKT-l6KXi8q3jNubt33uIl801_J3UKkaThDw9sjw-dx_QEC1FaqF66ILInw1sRTcsXVOz4DwNltR8YSF5pwvUMHYmOPfX-NdITHEAnxQobDPBI0L_Rw==)
22. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFj8Gflmp8BDWX84Byk2vBBgpb47UP-CBxmdSbVTSc6Mlh3cwV1O9lA2YG2YXOvdAasdnTQRePB8hHMsR2xdqR3HD_-6XgWOEEIFlHDfB8ihp4WDBXTK3MdsO0Wn5VmnR6QATllJ3TAuZWSs37mpl1wkvMK7D9MmFsL)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEW0-OiYuYEWezn8uY0BgA04tvUTs1ofmJWAm4XawevXsVxNVA94ZEn7EFBthqESuyQpB96tTJiKQ4cM4qgLF-yahi72-hYatGbDT361h6AVuJ5fXgunA==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKapnuHqz1V62DW6TffyW7qeCKfiPvjXDKXqf2R3752zIU10FMSZZwweEK6-qPj_VUR98BaJjvTMbdp9BoG1FljpmMyy6p_J_2X2FSs6ZqzBDoZcOuEA==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHG8p45O-n2-Vu3jdfg9wyqdVqN-Iw6pDpEMT__-dNipM2ckP-LXaKWN3vbYWF-M-WMvRQhJW0otXqMZdxQknfF9Bys666zL2bi3ifJHq_dTIiLowfNlg==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9KEpIaZEklPgG0YLM93lqg4ZLGieFU2jEnPxuDwmHrVvWiw47Jf9O4axjip0rYZE6j1LyDqryTLJC9eLCi38pNpQy2tZqTtClJXlfW9na9VK8bOM88h3gvQ==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgwPvf3pW_mJgMbAWNilPKD3KTJ5C5XusgwE2_g5mUlnz0e8N8x-7M2DSbZLrEhzmSeAVA3pMGFP1ull3jidIPl2597Y5QsryQJeSuRB7ULIUGtaHhdw==)
28. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHOWlSsFXUlJ1wZTdBGUmIdiLkUfZS7HS8zm7w-GDkdQAiKg0By0ABqnCu8Cu1OPzG2f83ySjwS9Z0OVKZAk3iAYHmxwqiD4UWLEPEyAbI6q6EjoidEHJYDltVNL7k-27C--WZk0Jmcsi3fwgs5Wc_qeFfS8uIpL_KlhPvoqS72maz80uyMvJudmT0JQMaHSapZmO2yyMqJv7XMgg=)
29. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEDKWxHGqEh5_Dg6gT86GWfOXwEzvr2HIrkRcd0t1QwtLvkl-KlNyWgJFSEl7Y8Xn5-L8FOzdA1BdBCHeYK8egDATlo4ISvE-3f7HPIV2Fw02e2j4ezH-XOxVrwfJ7CeN75yVdawOc4j9zogV7isGW7v-UQv4xdbgI4RlaFLCdb2MTaQRQ)
30. [dartmouth.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQED9Y8wI6acsWjzNCh_6w0lyNTL4AvZvuY_TgM8V0XICfU5vjrMD-b3fFUtLF3WbX_h_RVIRfwUWFWcfKWVpLwyuLP0W1qBQPdHH3Bh9yObiXJo3jjjO8U2kmKDq-mU8p-D5Xc=)
31. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBi6GdKmRnNitRXlv9MaPBafK_iJiLDcXQyU7YsCIm-6hULUqTo2cqsvhmJ2QEK9ChfIGKaR2TdcYUumnod8I8BIBqR96EPUL6Olb5KLlV2_C-ii7wzBW1zBqdiBz7mKIKhKR1xizFgRYfA_Y6K6gqpBAx38lAvFceYiJAAh3dvI8aeLSeGlwjG1t6d1xcOVPQ)

