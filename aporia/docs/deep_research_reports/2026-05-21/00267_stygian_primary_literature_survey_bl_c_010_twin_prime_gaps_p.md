# Stygian primary-literature survey: BL-C-010 (Twin prime gaps (post-Zhang-Maynard-Tao))

**Pythia queue id:** 267
**Tier:** T5
**Priority:** 5
**Requested by:** Stygian
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdpM3dQYXYyWEE3R3oxTWtQdE9IRHdRMBIXaTN3UGF2MlhBN0d6MU1rUHRPSER3UTA
**Elapsed:** 244s
**Completed at:** 2026-05-21T21:47:44.744360+00:00

---

# Artifact Attack Plan BL-C-010: Twin Prime Gaps (post-Zhang-Maynard-Tao) Falsification Battery

**Key Points:**
*   Research indicates that the Twin Prime Conjecture remains strictly open as of 2026; recent primary literature continues to distinguish the exact gap of 2 from the generalized bounded gaps established in the previous decade.
*   It is definitively established that Yitang Zhang proved the existence of bounded gaps (\(H_1 \le 70,000,000\)), not the exact Twin Prime Conjecture (\(H_1 = 2\)). Large language models frequently fail to capture this nuance.
*   Recent attacks (2024–2026) in the primary literature largely fall into two categories: unconditional sieve-theoretic attempts that often succumb to exactness barriers (leading to retraction), and conditional frameworks that outline the coupled difficulties required to bridge the gap between bounded differences and exact twin primes.
*   The transition from bounded gaps to exact twin pairs remains hindered by the parity barrier in sieve theory, a structural limitation dictating that current sieves cannot readily distinguish integers with an even number of prime factors from those with an odd number.

**Methodological Nuance:**
The evaluation of prime gaps is highly sensitive to the distinction between individual progression estimates and uniform control over prime pairs. It seems likely that any unconditional resolution will require a conceptual departure from the multidimensional sieves of the Goldston-Pintz-Yıldırım (GPY) and Maynard-Tao frameworks. 

**Summary of Current State:**
The literature confirms that while bounds on prime gaps have been drastically reduced unconditionally to 246, and conditionally to 6, the exact gap of 2 remains a methodologically distinct challenge. The provided falsification data focuses on recent primary literature to map the precise failure modes of contemporary attacks.

## 1. Resolution of the Modal-LLM-Emission Failure Mode

The documentation for problem `BL-C-010` highlights a pervasive failure mode in modal Large Language Model (LLM) outputs: the erroneous conflation of Yitang Zhang's theorem on bounded gaps with a proof of the Twin Prime Conjecture itself (often emitted as *"Zhang proved twin primes"*). 

An examination of the primary mathematical literature unequivocally **refutes** the LLM failure mode. The mathematical community maintains a strict demarcation between three distinct, albeit related, concepts (the HARD-5 discipline):
1.  **Bounded Gaps**: The assertion that \(\liminf_{n \to \infty} (p_{n+1} - p_n) < \infty\), where \(p_n\) is the \(n\)-th prime number. Yitang Zhang (2013) proved unconditionally that this limit infimum is \(\le 70,000,000\) [cite: 1, 2]. Subsequent refinements by James Maynard, Terence Tao, and the Polymath8 collaborative project reduced this bound to 246 unconditionally [cite: 1, 3].
2.  **The Twin Prime Conjecture**: The specific assertion that \(\liminf_{n \to \infty} (p_{n+1} - p_n) = 2\) [cite: 4]. This remains entirely open [cite: 5]. 
3.  **Prime \(k\)-tuples Conjecture**: A generalization (often attributed to Hardy and Littlewood) positing that any admissible pattern of prime gaps occurs infinitely often [cite: 6]. The twin prime conjecture is the specific 2-tuple case where \(\mathcal{H} = (0, 2)\) [cite: 7].

The literature is resolute: Zhang's breakthrough combined equidistribution properties of primes in arithmetic progressions with advanced sieving techniques (a modified Goldston-Pintz-Yıldırım method), resolving a fundamental question about bounded gaps while explicitly falling short of proving the Twin Prime Conjecture [cite: 2, 8]. To quote recent scholarship, despite dramatic breakthroughs on bounded gaps between primes, the full Twin Prime Conjecture remains unresolved [cite: 4]. Thus, the LLM hallucination is a classic categorical collapse, misattributing the resolution of a broader class problem (finiteness of gaps) to its most famous specific instance (gap of 2).

## 2. 2024-2026 Primary-Literature Attacks

To populate Substrate Type A (falsification data), we isolate the two strongest and most prominent published attempts (or explicitly documented conditional frameworks) on `BL-C-010` within the 2024–2026 window.

### 2.1. Attack 1: Unconditional Weighted Sieve Integration (Chenghui Ren, 2025)

**Citation:** Chenghui Ren, "A Positive Lower Bound for the Sum of Log-Reciprocal Twin Prime Products via Weighted Sieve," arXiv:2511.12944 (2025). DOI: 10.48550/arXiv.2511.12944 [cite: 5, 9].

*   **Precise Statement Attacked:** 
    The unconditional infinitude of twin prime pairs; specifically, the attack attempts to prove \(\liminf_{n \to \infty} (p_{n+1} - p_n) = 2\) by establishing a strictly positive asymptotic lower bound for a specialized sum over twin prime pairs [cite: 5, 10].
*   **Technique/Method Invoked:** 
    The paper refines the application of analytic weighted sieve techniques. The author attempts to estimate a sum over twin prime pairs where each term takes the form \((1/p)(\log(x^\alpha/p))^k\). By analyzing this logarithmically weighted sum and calculating its integrals, the methodology aims to demonstrate that the asymptotic behavior remains bounded away from zero, which would logically confirm the infinitude of twin primes [cite: 5, 10].
*   **Verdict Reached:** 
    **Withdrawn.** The paper (v3) was officially withdrawn from the arXiv registry on November 23, 2025. The author's explicit withdrawal comment stated: *"An error in the final integral calculation of the paper led to the invalid conclusion"* [cite: 5]. 
*   **Hardness-Signature Classification:** 
    **EXACTNESS_BARRIER.** 
    This attack fits the `EXACTNESS_BARRIER` classification perfectly. Analytic sieve methods often rely on delicately balancing main terms against error terms during the evaluation of complex contour integrals or asymptotic limits. An error in the final integral calculation reveals that the method's precision was insufficient to separate the hypothetical twin prime count from the ambient noise of the sieve's error term. This mirrors the historic failure mode of previous sieve attempts where asymptotic exactness breaks down precisely at the threshold required to isolate gap 2.

### 2.2. Attack 2: Conditional Shifted Convolution Uniformity (Trey Smith, 2025)

**Citation:** Trey Smith, "A Generalized Elliott-Halberstam Conjecture Implying the Twin Prime Hypothesis," arXiv:2511.14810 (2025). DOI: 10.48550/arXiv.2511.14810 [cite: 4, 11, 12].

*   **Precise Statement Attacked:** 
    The derivation of the exact Twin Prime Conjecture from a novel, highly uniform distributional property of primes. The attacked statement is conditional: if a proposed "Generalized Elliott-Halberstam Conjecture for Shifted Convolutions" (GEH-2) holds for a distribution level \(\vartheta > 1\), then there exist infinitely many primes \(p\) such that \(p+2\) is prime [cite: 4, 11].
*   **Technique/Method Invoked:** 
    The classical Elliott-Halberstam (EH) conjecture concerns the distribution of primes in arithmetic progressions via the error term \(E(x; q) = \max_{(a,q)=1} |\theta(x; q, a) - x/\varphi(q)|\). While EH implies bounded gaps of 6, it cannot yield 2 because bounded gaps only require information on *individual* progressions [cite: 4, 13]. Smith constructs a bilinear extension (GEH-2) that moves from single prime distributions to the distribution of prime pairs. It provides a level of distribution for correlations of the von Mangoldt function: \(\Psi_h(x) = \sum_{n \le x} \Lambda(n)\Lambda(n+h)\). The technique leverages this proposed uniform control over prime pairs to bypass the limitations of the Selberg/GPY sieve [cite: 4].
*   **Verdict Reached:** 
    **Active (Conditional/Extended).** This paper has not been retracted and remains a valid conditional proof in the primary literature. It successfully establishes the implication (GEH-2 \(\implies\) Twin Primes), thus formally mapping the conceptual distance between modern sieve limits and the Twin Prime Conjecture [cite: 4, 12].
*   **Hardness-Signature Classification:** 
    **COUPLED_DIFFICULTY.**
    The paper explicitly diagnoses the failure of existing techniques: bounded gaps follow from information on individual progressions, but actual twin primes require uniform control on prime pairs [cite: 4]. This represents a `COUPLED_DIFFICULTY`—the problem of proving the twin prime conjecture is inextricably coupled to the vastly more difficult problem of establishing uniform, bilinear distributional asymptotics (GEH-2) that exceed current analytic capabilities.

### 2.3. Summary of Attack Signatures

| Attack Author | Year | arXiv ID | DOI | Target Scope | Signature | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Chenghui Ren | 2025 | 2511.12944 | 10.48550/arXiv.2511.12944 | Unconditional (\(H_1=2\)) | `EXACTNESS_BARRIER` | Withdrawn (Integral Error) |
| Trey Smith | 2025 | 2511.14810 | 10.48550/arXiv.2511.14810 | Conditional (GEH-2 \(\implies H_1=2\)) | `COUPLED_DIFFICULTY` | Active/Published |

*(Note: Other 2024–2026 explorations include S. Cherukupally's equivalence formulation via arithmetic progressions (arXiv:2603.08099, DOI: 10.48550/arXiv.2603.08099) [cite: 14, 15, 16], which identifies a structural mirror symmetry but does not provide an unconditional proof mechanism, further validating the `REPRESENTATION_GAP` encountered in purely algebraic approaches).*

## 3. Structural Barriers: Why Bounded Gaps Do Not Trivially Yield Twin Primes

To provide deep context for the falsification battery on `BL-C-010`, it is essential to formally codify why the Polymath8/Maynard/Tao refinements of Zhang's theorem stalled at 246 (unconditionally) and 6 (conditionally).

The machinery responsible for the bounded gaps breakthrough relies on the GPY method and multidimensional sieves. These sieves introduce non-negative weights to detect short intervals containing multiple primes. The method successfully proves that \(\liminf_{n \to \infty} (p_{n+m} - p_n) < \infty\) for any integer \(m\) [cite: 1, 11]. 

However, sieve methods are historically constrained by the **parity barrier** (or parity problem), established by Selberg. The parity barrier dictates that conventional sieves cannot distinguish between numbers with an odd number of prime factors and those with an even number of prime factors [cite: 17]. Because the GPY and Maynard-Tao sieves are fundamentally variations of classical sieve theory, they cannot unilaterally force the gap to drop to 2 without an external source of "Type II" (bilinear) information that breaks parity [cite: 17]. 

Smith (2025) perfectly encapsulates this methodological ceiling: the Elliott-Halberstam conjecture provides extraordinary control over primes in arithmetic progressions up to moduli \(q \le x^{1-\epsilon}\). Assuming this generalized conjecture, the multidimensional sieve yields a minimal bounded gap of \(H_1 \le 6\) [cite: 11]. To push the gap to 2, one must shift from individual arithmetic progressions to a distribution theory of prime pairs, requiring the evaluation of shifted convolutions of the von Mangoldt function [cite: 4]. Consequently, `BL-C-010` transitions from an isolated sieve optimization problem to a fundamentally coupled obstacle involving bilinear forms.

## 4. Falsification Substrate and Landing Path

The synthesis of this literature search directly populates the falsification data for Stygian's v10-battery execution. The parameters below ensure that the agent correctly parses the collision risk between bounded gaps and exact twin primes, inoculating the evaluation system against the modal-LLM hallucination.

**Landing Path Artifact Injection:** `charon/agents/stygian/artifacts/attack_plan_BL-C-010_2026.md`

```markdown
# Falsification Stub: BL-C-010 (Twin prime gaps, post-Zhang-Maynard-Tao)

## 1. Systemic Risk Identification
- **Modal Failure Mode:** LLM asserts "Zhang proved twin primes" or "Maynard/Tao proved twin primes."
- **Ground Truth:** Zhang (2013) proved bounded gaps ($H_1 \le 7 \times 10^7$). Polymath8 reduced to 246. Twin Prime Conjecture ($H_1 = 2$) remains fully open.
- **Verification Rule:** Any generated proof claiming unconditional $H_1=2$ via standard multidimensional GPY sieving without a novel bilinear/Type II parity-breaking mechanism must be automatically flagged as `EXACTNESS_BARRIER` hallucination.

## 2. Competing Hypothesis & Primary Citations (2024-2026)
- **competing_hypothesis_id:** `CH-Ren-2025`
  - **Source:** arXiv:2511.12944 | DOI: 10.48550/arXiv.2511.12944
  - **Method:** Log-Reciprocal Weighted Sieve Integration.
  - **Signature:** `EXACTNESS_BARRIER` (Withdrawn due to final integral calculation failure).
  - **Falsification Use:** Use as a negative control for LLM outputs that attempt analytic integration of sieve weights without rigorously bounded error terms.

- **competing_hypothesis_id:** `CH-Smith-2025`
  - **Source:** arXiv:2511.14810 | DOI: 10.48550/arXiv.2511.14810
  - **Method:** Generalized Elliott-Halberstam for Shifted Convolutions (GEH-2).
  - **Signature:** `COUPLED_DIFFICULTY` (Shifts burden from sieve mechanics to uniform bilinear control of prime pairs).
  - **Falsification Use:** Use as a positive structural control. Valid theoretical models must acknowledge that bridging $H_1 \le 6$ to $H_1 = 2$ requires structural hypotheses akin to GEH-2.

## 3. Battery Execution Parameters (v10)
- **Substrate Type:** A (Falsification Data)
- **Hardness Discipline:** HARD-5 (Strict lexical isolation of `bounded-gaps`, `twin-primes`, and `k-tuples`).
```

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHA_vD_PmmLlAiRBUiYyqRPfW0AWWrcezR5Uimj-jiOpTYB74uVkd4zHqwQV8z9uq7d_imCxylO9fSKRTaDxOQG_kMD-sT-sY1ynacOmfEbIN8xJBMbrcPMKPbYUe2aqV0GxykZIH7b0ltcTwnFULAPaijN0GNCyr617VUPnVvlaCE=)
2. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4tgpGfKK2stkntM-U1I82EiiCJAP-1GC7EyoTHJLXriICnOyLg2HNea3Imf6Iir9H3sLgA6q2WyhlfGlypV-bfbBL-RobnNoAgEC5QfL5LCjLwd-AIpQUbvIEqwXjHAllTW3ROECqhQ==)
3. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMB_yn5PiAiLqCT_lo13DwkHZLKNMVZ3ue0AYINffLG7FgB46qBFvSTQQH0ATtkOYg5sjHKwUrz7Uxo_UfFKDbPNZJ8sS_k8W-bRpDcIQyVnEtekYKQJqhVbB63lA=)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFF3WzyOJBNCXzSguLP5tC8V_joQFl2JwsCPZ9UXM-Ty_UVMqXZXaVsoNTdTmCJuZefzCxoSDPVUkSqpNOiEXLntwhaQQiJbGEKxcX1U8v6smsIHMXqQ8dO)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGr15NXOz6FJmnpV6KM-N1D8KL4z6Cav2bAPLbZ6DXvDBGgwF1KoaNh9fJ_JXiLWTHPfXjWLAEZ4_oC_6T8V1EwFXxQ88OGcFmA8quyXQamhSm313Q)
6. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrOxDQnLKmJ16PxeBwe7ICt24-IE-xfMafQHeC1Sykyjilfz2A9T2Nfhe7M135yM70mz2QyjCX-CI8TAA7iqnPlSvBT11oG5OC_cCZ_NEzyTpzFdZGtrDqdiAoWNoZLG4mDk_CXat7tQJeEQjzdjwWPW_JlgzIHCqU51nbYTmBxOISiMJE3-9DjfHG5gD2)
7. [colgate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuDzT7CNY_xvmz1BWmoUTzi7O4dgDeGvITM1L4mCSuI5mZOFFyPRkdreklYqusF0ZnZ0DfJnT8IS_L2yn3LuWxyp-hAhaJHwMXiD1m_gF4Oe8PQmvE0yI5WzWwzXzfXHZdzDI=)
8. [openbookpublishers.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFU2kGS8BvjGAkiEiFit5Q5wSXQLLpvVt5HzaNz_3HQ3gUl1zZlIbHAbOPVnmD4Im9Qlt5V4T2viuxgWwzLqy1sHl1Ipnmv-o3Veq8bU3wZJ-xfKP0vorr3SwGg7PxCsA_kwMQGampojWf_bkf6ZLfewGQ=)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnSur0R11-AG6A032SFhJUncMbpp9Y5dXYZkDqfk8FKUVjH9feo1qW4ttk7r_plNVipoDO7evDbHmPh1tmFrqTIRxHkUreBI2ZbBxzeN4IEYuGEvqDR9G35NAss9Wh2SejGYS8PRhsNbJzioqPdvjs5haIh_Vn8iY6FqW0-G6DpgQ84sbPKaCWTCi897G3qZk8697LUx4bpb4l4oYzQyN7n0nqhA9cdA==)
10. [papers.cool](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTKSPVixSCr58ZWdIT0QK1EUJUXeok7nXdMAVSY6pv40Pyih1ZBsF2IncGWmWSnrauw40Bn0xXwdl3F2D7s1KQFpkUHM6DeYvhhWWx3MXhNpRyNkETmJ9-Yw==)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjrTXwoiWT2iJAH173KoWJbJc11H0s1f5OmxtHUqPptt1ZB8ltasfe5cWARvrwGXx1sYb3_bUY0qcljisbfusVvNGCCK4qY8jduu2nnBpzyLsjm27TAMTM_RPEFb163uipEBZUt95ttfcRtShrvWbmZvKz-ZtL1wUOLNwA0h-im4b54CF-XU6zFOYl-zmAlhY4goh8ARx_zDy1vNLWmIDHZDnRFCvULFyqT0ObZPNs4nrRjwXh6hY=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWSQ5l6FdwvCVq0se9Lw8rYE9JJT43w9r7lAfdQJAgorZXEiqBvemJHgR2NQQ5jzyJ3TNFgTD3jZsI6QmUgjtyLlCJ-l2k7A7MB1iW9kLu3OiMjhOR)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnv3T8gSCDV7pYMOEA0qc3ssFpH06k_TZ-tuYqnOUCe1icSQcIrWhwqZYpxF5w5z5fYcrdEjU0n52PukHiK2rmAcnMjujL7n0ky_YC0bmqq6N4uL73)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSI_2zJIH1nI9bi6_krAhZmvHzUwsCsyqSZq6drMzTkiLMoRn6oc-uoqKnu-MNpjB9B-ZTTTs2xXf4SRacIyVoNUJe65Y6VZkAQjEOTVWwVZvhRX1g)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwECo19vEz1p-EgdjKbwftUTWl_4-NEgR2KQoj2_j14qZsTaCjfaeVj2BGFtXkPCLleweHZyk34H6uNNcsvVA0ECuf2jiN6lXqc2Z1NBM7WErPxZmACHG6jroazc1DhMIXt3cQFSGQgW2HAbLJenYL5W3QyIgMPrlWhcanKcZxqpq0sP1QZtPAFc_2Jo2WIWkccDaPnjyc0TdcMprhXzvMmGfIzv30waOFaz7rinbmITJADf0EQDYSBKBX9npKbarvA10h4npFVkQ=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkGDfPgV9OYos8Jaudz6gAuROXr0z3663eIkdnP32wijCEvoEkCq0FJU4yFIuEmjx0tVoFO9DPSWWIH_LWXlqBTlDwZs6HyJXXhTSiC8JtXGElEI1lQw==)
17. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzqIyafLD7tjZPrbTGdhoj59NCxuhk50x_lomGaVcspDpurvb-RxB1wZ4VyFP9bJ2LrGHM_gLEcGnsVDjvTSRJmrbp7jysFumrQA0XwCkD7EbKSG9barvQQS3HYASjrBxj5wAmnpDBW28vAPGTqi0EBQ==)

