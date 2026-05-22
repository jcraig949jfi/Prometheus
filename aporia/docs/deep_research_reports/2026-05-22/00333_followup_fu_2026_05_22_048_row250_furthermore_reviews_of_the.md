# Followup [FU-2026-05-22-048 <- row250]: Furthermore, reviews of the field in late 2025 explicitly confirm that "as of 2025, the ABC conjectu

**Pythia queue id:** 333
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdScjRQYXNERk9kS1otOFlQd3JDQW9BURIXUnI0UGFzREZPZEtaLThZUHdyQ0FvQVE
**Elapsed:** 247s
**Completed at:** 2026-05-22T02:28:15.160626+00:00

---

# Research Brief: Substrate-Grade Analysis of the ABC Conjecture's Status (2025–2026)

**Key Points:**
*   The ABC conjecture remains broadly classified as an open problem by the mainstream mathematical community as of mid-2026, despite a published proof.
*   Shinichi Mochizuki’s 2012 proof utilizing Inter-Universal Teichmüller (IUT) theory, while published in 2021, remains highly contested; the consensus heavily leans toward the presence of an insurmountable logical gap at Corollary 3.12.
*   Alternative proof attempts, notably by Kirti Joshi using Arithmetic Teichmüller Spaces, have also encountered critical resistance, with experts like Peter Scholze identifying significant flaws (e.g., Proposition 6.10.7).
*   The field is currently undergoing a "formalization revolution," with independent initiatives—such as the LANA Project and Mochizuki's own group—attempting to translate the contested proofs into the Lean programming language to definitively resolve the sociological and mathematical impasse.
*   Unconditional mathematical bounds remain exponentially weak compared to the conjecture's assertion, with the best rigorous results relying on linear forms in logarithms (e.g., Stewart and Yu's 2001 bounds).

**Current Mathematical Climate**
The mathematical landscape surrounding the ABC conjecture is uniquely fractured. It represents an unprecedented sociological anomaly in modern mathematics: a proof that is accepted as a foundational theorem by a localized group of researchers (primarily centered at Kyoto University's RIMS) while being actively rejected or ignored by the overwhelming majority of global arithmetic geometers. The contention revolves less around discovering a blatant computational error and more around profound disagreements regarding the logical cohesiveness and definitions within IUT theory. 

**The Formalization Pivot**
To circumvent the human elements of this dispute—such as peer-review bias, miscommunication, and the sheer cognitive fatigue of parsing thousands of pages of idiosyncratic notation—researchers are increasingly turning to computer-assisted proof assistants. By encoding the foundational axioms of anabelian geometry into languages like Lean, mathematicians hope to force a binary, machine-verified resolution. This transition marks a critical evolution in how the community intends to handle ultra-complex, disputed proofs in the future.

**Scope of this Report**
This report synthesizes the current status, best-known mathematical bounds, literature, and ongoing attack vectors concerning the ABC conjecture, particularly tracking updates surfaced throughout late 2025 and the first half of 2026. It rigidly follows the Aporia 7-section template to interrogate the exact boundaries of the problem.

***

## 1. Brief Summary
**Prometheus Context Query:** Status update on the ABC conjecture as an open question, verifying the late-2025/early-2026 consensus that the problem remains unproven and analyzing the sociological and algorithmic shifts (e.g., Lean formalization via the LANA project) attempting to bridge the impasse.

## 2. Flagged Findings
**Current Consensus:** The overwhelming majority of the global number theory community, including leading arithmetic geometers and Fields Medalists, considers the ABC conjecture to be an open, unsolved problem [cite: 1, 2, 3]. The foundational claim by Shinichi Mochizuki to have proved the conjecture via Inter-Universal Teichmüller (IUT) theory was formally published in the *Publications of the Research Institute for Mathematical Sciences* (RIMS) in 2021 [cite: 2, 4]. However, this publication did not shift the global consensus [cite: 2, 5]. The primary crux of the rejection stems from a 2018 document by Peter Scholze and Jakob Stix, which identified what they described as an unfixable, fundamental logical gap in the deduction of Corollary 3.12 from Theorem 3.11 [cite: 5, 6]. 

**Where the Consensus Might Be Wrong (Or Shifting):** The assumption that IUT theory is fundamentally unsalvageable is currently being stress-tested by a completely novel attack vector: rigorous algorithmic formalization. The ZEN Mathematics Center (ZMC) launched the "Lean for ANAbelian geometry" (LANA) project in late 2023, publicly announcing it in March 2026, to translate anabelian geometry and IUT into the Lean proof assistant [cite: 7, 8]. If LANA successfully verifies the bridging logic of Corollary 3.12, the global consensus will be violently upended, validating a decade of localized persistence. Furthermore, parallel independent attempts to reconstruct Mochizuki's insights using standard arithmetic geometry concepts, such as Kirti Joshi's framework of Arithmetic Teichmüller Spaces, suggest that the foundational intuition of Mochizuki's work might harbor deep, unrecognized truths, even if the specific mechanical execution in IUT is flawed [cite: 6, 9]. 

**Calibration Alert:** In projecting the timeline and success probability for the LANA project or Mochizuki's internal Lean formalization efforts, observers frequently exhibit **PATTERN_BASE_RATE_NEGLECT**. The assumption that a theory which has actively eluded human consensus for over twelve years can be swiftly codified into a functional programming language ignores the historical base rate of formalization velocity for highly complex, heavily idiosyncratic mathematical architectures. Even translating standard, universally understood proofs (like the Liquid Tensor Experiment) required immense resources; doing so for a contested theory with contested axioms will likely be an extensively protracted endeavor [cite: 7, 10].

## 3. Problem Statement
The precise object being interrogated is the Diophantine relationship between the additive properties of integers and their multiplicative prime factorizations. 

**The ABC Conjecture (Masser and Oesterlé, 1985):**
For any positive real number $\epsilon > 0$, there exists a constant $K_\epsilon$ such that for all triples $(a, b, c)$ of coprime positive integers satisfying the additive equation:
\[ a + b = c \]
the following inequality holds:
\[ c < K_\epsilon \cdot \text{rad}(abc)^{1+\epsilon} \]
where the radical, $\text{rad}(n)$, is defined as the product of all distinct prime factors of $n$ [cite: 1, 11]. 

A highly studied equivalent formulation is the **Modified Szpiro Conjecture**, translated into the geometric framework of elliptic curves. It conjectures that given $\epsilon > 0$, there exists a constant $C(\epsilon)$ such that for any elliptic curve $E$ defined over $\mathbb{Q}$ with invariants $c_4$, $c_6$, minimal discriminant $\Delta$, and conductor $f$, the relationship is bounded by:
\[ \max\{|c_4|^3, |c_6|^2\} \leq C(\epsilon) \cdot f^{6+\epsilon} \]
or, in its original unmodified form:
\[ |\Delta| \leq C(\epsilon) \cdot f^{6+\epsilon} \]
[cite: 12, 13, 14]. The conjecture fundamentally posits that highly divisible numbers (which possess small radicals relative to their size) cannot easily sum to another highly divisible number.

**Calibration Alert:** When analyzing the implications of the ABC conjecture on geometric structures, it is critical to avoid the **PATTERN_CONDUCTOR_CONFOUND**. This error occurs when the local arithmetic properties determining the conductor $f$ of an elliptic curve (such as primes of bad additive or multiplicative reduction) are improperly mapped onto global discriminant bounds without accounting for the profound, non-effective structural rigidities that arise in the transition from integers to schemes [cite: 15, 16]. Equating the algebraic conductor directly with the integer radical $rad(abc)$ in Frey curves requires careful tracking of the primes $2$ and $3$, an oversight of which routinely confounds heuristic bounding attempts.

## 4. Status & Bounds
The ABC conjecture is currently unproven globally, existing in a state of suspended mathematical animation [cite: 3, 5]. Because the full conjecture with $1+\epsilon$ remains inaccessible, mathematicians have rigorously established only exponentially weaker unconditional bounds.

**Current Unconditional Best Bounds:**
The sharpest unconditional bounds for the ABC equation over the integers rely on Baker's theory of linear forms in logarithms. The current best general result is due to C.L. Stewart and Kunrui Yu (2001) [cite: 17]. They proved that there exists an effectively computable constant $K$ such that:
\[ c < \exp\left(K \cdot \text{rad}(abc)^{1/3} (\log \text{rad}(abc))^3 \right) \]
This bound is exponentially weaker than the polynomial bound $c < K_\epsilon \cdot \text{rad}(abc)^{1+\epsilon}$ demanded by the actual conjecture [cite: 17, 18].

**Bounds on Exceptional Sets:**
Recent breakthroughs in 2024 and 2025 have focused on bounding the density of "exceptional" triples—those that violate the bound $\text{rad}(abc) \geq c^{1-\epsilon}$. Browning, Lichtman, and Teräväinen (arXiv:2410.12234) provided a power-saving bound on the size of the exceptional set of triples within a box $[1, X]^3$, using combinations of the geometry of numbers and high-dimensional Fourier analysis [cite: 19]. While not proving the conjecture, it quantifies how extraordinarily rare ABC hits are.

**Conditional Bounds and Superelliptic Equations:**
In specialized variants, bounds are being generated conditionally on the strong version of the conjecture. For example, Karsten Müller (arXiv:2602.19061, Feb 2026) established a framework bounding the adapted power gain $G_p$ and approximation gain $G_a$ for generalized diagonal superelliptic equations $By^n = Ax^n + k$. Müller proved that under the Strong ABC Conjecture ($q < q_{\max}$), the power gain is uniformly bounded by $G_p < q_{\max}/G_{a,\min}$, rendering a theoretical foundation for the numerical observation that $G_p < 3$ for $n=2$ under the Ultra-Strong conjecture [cite: 11, 20, 21].

**Density of Solutions (Leng, Sah, Sawhney - 2024):**
For related arithmetic progression and gap metrics, the current best bounds leverage the machinery of Leng, Sah, and Sawhney, indicating that sets free of certain progressions have densities bounded by $\ll N / \exp((\log\log N)^{c_k})$ [cite: 22, 23].

## 5. Literature (Primary Sources)
The primary literature driving the modern discourse, encompassing the original claims, the refutations, the subsequent repair attempts, and recent heuristic bounds, includes:

*   **Shinichi Mochizuki (2021)**: "Inter-universal Teichmuller Theory I, II, III, IV." *Publications of the Research Institute for Mathematical Sciences* (RIMS). The foundational, highly contested papers claiming the proof of the ABC conjecture [cite: 2, 6].
*   **Peter Scholze and Jakob Stix (2018)**: "Why abc is still a conjecture." A definitive manuscript outlining the unrepairable gap at Corollary 3.12 [cite: 3, 5].
*   **C.L. Stewart and K. Yu (2001)**: "On the abc conjecture, II." *Duke Mathematical Journal*, 108(1): 169-181. Establishes the current best unconditional exponential bounds using linear forms in logarithms [cite: 17, 24].
*   **Kirti Joshi (2024)**: "Construction of Arithmetic Teichmuller Spaces IV: Proof of the abc-conjecture." arXiv:2403.10430. An attempted proof using a different conceptual framework (Arithmetic Teichmüller Spaces), which Scholze subsequently flagged for an error in Proposition 6.10.7 [cite: 1, 3].
*   **Karsten Müller (Feb 2026)**: "Gain Bounds for Diagonal Superelliptic Equations under the Strong ABC Conjecture." arXiv:2602.19061 [math.NT]. Investigates ABC-qualities in superelliptic equations [cite: 11, 20].
*   **Evan Chen et al. (Mar 2026)**: "ABC implies that Ramanujan's tau function misses almost all primes." arXiv:2603.29970 [math.NT]. Provides a heuristic and formal Lean-verified proof conditional on ABC [cite: 25].
*   **T. Browning, J.D. Lichtman, and J. Teräväinen (Oct 2024 / updated 2026)**: "The exceptional set in the abc conjecture." arXiv:2410.12234. Investigates the density of exceptional triples [cite: 19].
*   **Katalin Gyarmati (Apr 2026)**: "Ramanujan, the taxicab problem for polynomials, and the abc-conjecture." arXiv:2604.25017 [math.NT] [cite: 26].

## 6. Attack Vectors
The mathematical community has exhausted several traditional methodologies and is currently deploying novel, technologically augmented techniques to navigate the problem.

### Exhausted Approaches
**Linear Forms in Logarithms:** The techniques pioneered by Alan Baker, which look at linear combinations of logarithms of algebraic numbers, successfully broke ground on effective Diophantine equations. This approach was pushed to its absolute limits by Stewart, Tijdeman, and Yu. However, it is universally acknowledged that linear forms in logarithms possess an inherent theoretical bottleneck that restricts them to yielding only sub-exponential or exponential bounds (e.g., $c < \exp(\dots)$). They cannot, by their current architectural nature, achieve the polynomial bounds required to resolve the full ABC conjecture [cite: 17, 18].

### Live Techniques
**1. Computer Formalization (The Lean Approach):**
The most active and sociologically significant attack vector in 2025–2026 is the use of the Lean proof assistant to formally verify or definitively falsify Inter-Universal Teichmüller theory. 
*   **The LANA Project:** Initiated by Kato Fumiharu at the ZEN Mathematics Center (ZMC) in late 2023 and publicly detailed in March 2026, the "Lean for ANAbelian geometry" project seeks to construct a foundational library of anabelian geometry in Lean. Its explicit secondary goal is to map IUT into Lean to isolate the exact point of logical failure or vindicate the theory entirely. The project features heavyweights like Johan Commelin and Adam Topaz (veterans of the Liquid Tensor Experiment) [cite: 7, 8, 27]. By April 2026, members of LANA still reported facing an "insurmountable wall" at the logic translating Theorem 3.11 to Corollary 3.12 [cite: 6, 10].
*   **Mochizuki's Native Lean Code:** In response to ongoing rejection, Shinichi Mochizuki and his collaborators (including Y. Hoshi) presented a preliminary progress report on the formalization of IUT in April 2026. Strikingly, Mochizuki views Lean not as a necessary tool for *verification* (as he assumes his proof is flawless), but entirely as a tool for *communication*. He asserts that Lean generates a "precise record" immune to "false misinterpretations" and "nonmathematical accusations." His team has produced approximately 70 lines of skeletal Lean code dealing with a "toy model" of a commutative triangle to bridge the communication gap, alongside proposing a new intermediate "Theorem 3.11.5" [cite: 28, 29, 30, 31].

**2. Arithmetic Teichmüller Spaces (Joshi's Re-architecture):**
Mathematician Kirti Joshi continues an aggressive campaign to prove the ABC conjecture by porting Mochizuki's intuitions into a more conventional arithmetic geometry framework. Joshi explicitly claims to have independently established a "canonical Arithmetic Teichmüller Theory" that bypasses the necessity for Mochizuki's specific, highly contested "$\epsilon$-loops" and "universes" [cite: 4]. Despite releasing a full proof in March 2024 (arXiv:2403.10430), Joshi's approach was rapidly intercepted by Peter Scholze, who identified a fatal flaw in Proposition 6.10.7 [cite: 1, 32]. Throughout 2025 and 2026, Joshi has heavily published FAQs, letters, and provisional reports defending his framework and accusing the mainstream community of "rewinding the clock," maintaining that the framework can be repaired [cite: 4, 9, 33].

## 7. Cross-References
The ABC conjecture acts as a central gravitational node in number theory; its resolution would trigger a massive cascade of solutions across Diophantine analysis. 

**Related Open Problems and Equivalencies:**
*   **Modified Szpiro Conjecture:** An equivalent geometric rephrasing dealing with the minimal discriminant and conductor of elliptic curves over $\mathbb{Q}$ [cite: 12, 13].
*   **Fermat's Last Theorem & The Fermat-Catalan Conjecture:** The ABC conjecture elegantly implies Fermat's Last Theorem for sufficiently large exponents (asymptotically) and provides the resolution for the generalized Fermat-Catalan equation $x^p + y^q = z^r$ (where $1/p + 1/q + 1/r < 1$) indicating it has only finitely many coprime solutions [cite: 2, 5, 12, 19].
*   **The Beal Conjecture:** A generalization of Fermat's Last Theorem, proposing that if $A^x + B^y = C^z$, then $A, B, C$ must share a prime factor. ABC implies there are only finitely many counterexamples [cite: 2].
*   **Mordell Conjecture (Faltings' Theorem):** Noam Elkies demonstrated that the ABC conjecture implies Faltings' theorem, drastically simplifying the proof of the finiteness of rational points on curves of genus $g \geq 2$ [cite: 1].
*   **Vojta's Conjecture:** The ABC conjecture is intimately related to Vojta's height inequality for curves [cite: 1, 2].
*   **Ramanujan's Tau Function Vanishing (Lehmer's Conjecture):** Assuming the ABC conjecture, recent 2026 research by Chen et al. demonstrated that the set of primes $\ell$ for which $|\tau(n)| = \ell$ is strictly bounded by $O(X^{9/10}\log X)$, implying Ramanujan's tau function misses a density 1 subset of the primes [cite: 25].

**Candidate Primitives:**
*   **Frey-Hellegouarch Curves:** The translation mechanism mapping integer triples $(a, b, c)$ to the elliptic curve $y^2 = x(x-a)(x+b)$. The discriminant of this curve $\Delta = 2^{-8}(abc)^2$ connects the additive integer relationship natively to the geometric invariants targeted by Szpiro [cite: 13, 16, 18].
*   **Anabelian Geometry & Galois Categories:** The fundamental primitive underlying IUT and LANA, focusing on how the algebraic fundamental group of certain varieties (like hyperbolic curves) completely determines the isomorphism class of the variety itself [cite: 7, 8].

**Sources:**
1. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFa3jTlw5D6xrdcbB7zy6yBO1N2oszo4KfVem3M4WbcGTA8K468xsDblvMPnoMcK_QQPmzLCAN3_Cqu2FjJnXvkzeOmYFO_eguJxJ3bXqcHMZpovQfSVJtccA0fdVyCMr2K)
2. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4WY5v35wBr2xVyv7kQprvV0SAdXdpV3V6OOjOAaBuJAwYDQl4Id2f-sKSB36eKASaHuzQHJv8aTqYUSZrXT0rIuHZ6tdMqOy7Q_twbBrZGETfmB6QRYTH7ZPTOLMbwsxp)
3. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAGSf7KodUDBOQdyp_WtIbwXq4RdmwqcYmenl-OLRaZT5qcEVBcWL6PE6XliBrUHT2JoCvGN8SA9kduytv3mOV7zdKOjwXYARGFvYP5uWWDv_RLWs8OAbjLkPibFmFfjUslvJJ4Enl8YMIxjnU90L0TbZynhp371M=)
4. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGQ7-XNY-8C8FponYrGhWd2oZEjtxN_NiHQzawe4wT7b5fvOOD9rC99KmDMylKNbqzMFk5N0ZQALVUft3jd2Pe1SdTwgErd0JPO1-qb8o0JxCaLROxfPT4CrYHv2uqN2J8S_a-mTDnEV2Qi08=)
5. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhT-5A6Uh67zv-Ga2tTw5P0wrZ5X79PdZU81J8GGvGpuQ7S8FoPY5YaqfVXL4Ne_k1_e2rQazE-pXCWfn_-rHHDrAQws8fehzXuivuWNmuvu4G52Fs4ViVRstEyIeezws=)
6. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFofxOVZlgEQWmGfM1e2arF2GvzhxtzDCIfhLX0DYmbOEznQcp8tg_tFDnzD8SQi1OcrC5iO4Xcf42LEH5-wrpzMl111XldXrQ-AHJwsZz298Wqt_Pb6BeO3aaWCP_nNy9l9FQUBw6EBHzxIsAFXGGpH8LJ6FEaTwc4VQ==)
7. [zen.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUyBZNhb2FVTAB0MX4Vr0tqbZt0yogHPgora8wVPloAf5pdo5QOm1ajKiuKMpozZAale-u4CnD3AQjvZbqRcH9VS_eDXcWZT2HJ4vC8O8K-Mn_lWLRx6BhXT-0ojg=)
8. [zen.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnBP19Zm1VwmkAzM7lUzFrBoBVm0iHrZNyny5a6HbwgKdlAlESosGWb0lsghpv_8RG1eUc6OkDORLlPN0LqbTmnRWDAMFu8-d9yR-unc2Ii6WNMxsu2HpRQwigQLB-CujD)
9. [arizona.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBTiAu2q_d84sSvu7wmV9VcAwu_TVmeu-FpfPG5UIvZltn7nyFlr1bHwH4lQxZ-c9QybU-dEyD91Mj0CTQQ19244tZCH8_vi5AOHt91olOxMfk0Rl46-UnGm-T)
10. [frontier.net.ua](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUbGJKBQ0E7hrnYzwBMB6m9zb4c-S3Es1wtWuYb6aATEPBPM-rmsINhEYAhwZ1muMPUstzgeQPp-JRSzbfrd7AJ-5k9RyCEjga-I1x77MEl3NmOLt1qZrP53omZVP7P9iRxa87_BwSIo55Doowb9jnlXCIpD5vgFoDJDHZOtzeEx-b_Ee3C9eLE06yhWH5a2dXBTtdH88=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVCybVV-IZ08f9RcKGouT4Gwz90DTcD_sow9iJdABsTEezRbE8RNdm1nbqS8Yi6_oF_yLOXBZiRfvOMMkOWZxOJVFn_7HgZWXIihDwYJqeGM3EvJ71)
12. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGs1mzSZgeTxTltKdiPW5Fb-y4daBrdVHlYBudUHv9egDHWucFR9ffXON6Pu_wI03xc8hjFiL0MfE9mAGK8SpMlt22IQPeYX0j6LVzqbLT6vzuzHnvkA42ZHISKz1YepE1CAdsFuiqc1g==)
13. [wstein.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERQIGhmxkRRIwsITQQbVlZEUCx-yYp9tC4uA5u9dqb_V3u5WFV405c39Vsf8zwdWJvwqdbw_D5wnZ5fxMEhO7zY8huSChXJ2NlNmw6Z6ZWYM-zdKfYgITbixnYccN5j9uadIRLgcLgPa6d_30LP3Sh1clzRkcpn8Six5ZzSSZ-)
14. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPtch6jqYOunfLKPz28puB8yE8Bp8pj2pahBEVV2L4r4EOX87rNDI4h4OhLQYxIOyBjbfUfDrrD6BjQEc-uwGTFqTG7haaH5Vae7O1WakFx1mEmPgblLubF6HstP5Kv68=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIiwQ-yfmNLzo8OmlDE21tO7acMW6dWvNMDNVHlS8PX03QP-u0YvUOUMnxXVcBt2CEavehCBFIGQj8HKI3hYG8_2s6mMuBpI9wjgTJjb-K3Pnr6-3z)
16. [uvm.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxwlewcmwCAZRV41J9_hJnFS2UmH9_oCrMlEQvZ44W5k7i_ORXc_ZZ2oIdRJk7DXUHMmGI25dj0sarTYMEB8Rea_UhJTV1lWFmU9Rp05JDs2T05t3sXskqjYORsmJiZwwAi1RczIbjYLliEJdunopv-4w3XTpPgxZD-liPIQA=)
17. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7GuttaUiNqavmnK4dbv2fwlkdE85qaFhMX_-XiI-g7uirWhC98AITezjWAsUbQLSC3SNsc4QbApibePJ8zTOWPrBC9hvftrkttCB23xLr6-ofdXUJmaNvWhZKuMdmDFpf0QEWP_ab4SafD-Axq3W45Y9oxzP6knOSnguCzftv2s19qVVOtB6Dguoey3x-4XuRMumlclrg6Pbr61AU3jiqz7ZOYTUGX2QHV12tqdA310FUKVKzcmg73OLz6uVXM31W)
18. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHe-Si9_boz059sRt-c0QHAfqaixWs5Y5MqUT9vvAbftcVciQJ14-4quyJCNKFoCWeAoHSNtkayOg1y0jahDK_es6pXJJNn1lD5i3hETlvjcDabMweXaehFF6LodJ4xDyXXIvwT3wyFjTfg9SVrwxo=)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElSvSmhI9beuIpcisiePyWO36E5T1AVd9wXwkn3VsEyZNEE0gz0X4ThoMtvb6ifpliTnSVMzOLSvYK3iwVD8KhLUrdmMRBtIq05o3Bp1NhWz9k0Da8zBEm)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4Gso2PGiV8XeWCuj9FiQFxbKADQASN2usuFnyDKT20HLOfyDvmsTSkkMSpJYbmtfQC0Wpo2yCg9-CMJPioFkfjQGRjoqWdiOctruiB5YCDJ86jHdh)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGB3TsZLhCyrA7Bqw_BiDCYPBmwcuQA_ugdjUrMbj_SrXVXUWG1k9fZrttx2RzEenGF2kP0VeP6vXfbGHr1zCrlgLy59c_Y25_W0j4Jt8Z8E2_-cfeGJiS)
22. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHa8osbufykpa1rG9FVKMP4uTjEgGtweCs5iOyHklM9G_FLI1K95yhG-g9w-m8Lp87R87p1vp4hMnVfyTAxKmCM8Lgb1B387VarDrh9xTWz4Bhs3ySzwJoekutcruiT6nnJlmIFVqJQRq3c_vkzMuTSXQItmNngmxdRw==)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOE0MI9F7C3Fzw88ffImBdWQY-6ONZbbeGm5GfjQfVMxjddjrl6nxezUWm5pamGRuvdVrs7JGX0hxH3MuHycxB7EUJBDsFhcPSKbxNrEpdCCBKasKx7XfS2bhB_HEUCygjrMu_VVERjhenWVgI2F57SA8T-MZhAQzfNhwl5ad1UqZFMm1bEFwxx6eg6TBIhLrqeOQTUKKxMkMdtPxRR-gusSFSjPz1h_P4PKnZXTxkcO_J)
24. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhvhWzTcLX4gnLGgoKCE7tWf-G7qc5eZ-XsZwIGo078xWBUmLPEX-se66ulzqmhkh3lgBZmM4GmOu-ldjBYez-VX9_QM8XKGHFbq8mbFicq7OsJJnEjbGPYLvgK4TW1obYtwtRyJljUYmtB-sELV5w6CmAMOmqprIEkaloMYZ8u0ZNpmXcGQLAPzHlgD9gL-keKTIgZ4Y=)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwWEkLAV6fAgxvVnhmNaSM1KVHSAoHzjD-dNSeu-f8AFVt2cBcHn72reRaQsA9JddR4AMRsgPSRJjzhRJOmzRmX2OsL2raUdfJXnqHNeH_nWcq322u)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBM44uWaEdeFHTVwFSPeCp_LLq02L0PcCp2GI0OM3kmM4dILrp0qmGEpMIvxhLwZo32LHn-kLRzd0p2R-M9g4Jzwj3E0_g4YOddBtwmZwMJh9QPkWo)
27. [newscientist.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBpeRLiLQQ-NKUFIN62GHuOXVp_I6TClbyeZv_eFSMl53LnJ8_EQykfU8N2QxjTLVZjbe6e31kjvfefrjAsmOLe_GDliUOPWqAeiDRMmUb-mkO2NqGGkH4jeLNhQFfg0K_cI9mSkNdr1xReIUFbYgPRVh1oNt46_xMMbBsCJb7HD7fxhbMii29ZNqBo-B3-bx6mtUO8c8EwH9F_qfhmGWn__7HDgU=)
28. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAYSsBJA3fA5wLV3klAF2tn8JVzfBq60zwz0uAplqhypEmYCD5pgUasT41N5CdVjCr9Sb1H-Q0xpIVt51e913XDpcZbKtTaQsMZQTXA8_FSfFEpB4dZZW4hVnHbwuFJVzjxUAUBaFh_tlK3_MrxzyhUpab-8WHOTFPn2luIxxaGMTme_Rjh0iDHJ_DXSfeyM7Q)
29. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrnUCOmzK58O8m7ZkVaWLbrAveaAyn6tCjy3miH69uK6QhKwgN6yZMrV1eOQD6rIeQw8bzIAXIkSqygKiR0CSHlHb8ukZQEmIg_8pztL3TqUaptlo4XDgiQLudqIogqnh5qfUthHumwvoCmfNrZMrK_Qp-HnSP6HZy5L7eRyjOMXQ=)
30. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVGlgpEPZF4bWWYzKrzRQEjLg4hCYVlMCotfz2IseC5pIyGlM5M5iCZs9-YYphWBOvwwFHSXxv6GwofW2QWUtY-bKll6PhemDf14yO7lY7c-b5_vEUMj5tXsOdOAjmPK0WYmvOs3fROiHOiA==)
31. [kyoto-u.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzi0PtXjMeuSENyMCA3Xo2jDnnGxUmqHR9WFaNE8D5roO6ea5uaTYT0uc7vN_C1AnvDLM3DktFXigRwkrP6Rdhc-vB1jzUFI8EWH8-qND2ne9i-lytgmqqCUlgc-RONYjcVHi4vkTjRbQcjYAKSQS9WfTY0iaakXeOvqWIvyETjE2DxbPhclGn)
32. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZnjOb1bnGue07eJoIOWOHvdAfLZi_YYcAw8-fi9GcF5rUQAJiN3zbqxMELo7y8XQal-8BKmZyAvvnUgFwGg8wHEwyTdsGunqiBv2GwUK-oKGoMUP0SOZxEowA4epmg_Zf2b2TMNZ9Pl0BtfeCwWAheEk1fKhzlOXpKa3WBKtUTSOxgwk12THmYs9hS3OnNLmdrtRX07xGOV7GJbA2ZQe7zW9GF64-)
33. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlwrHZz_d1nTUkR7uwkT0mv_HQoYFT0lwg92jOzeGy1rQZ8WdGBw8uVhbcqPweq1HmnbUCRk-ICo7cHrOJYoTXcB4bLzpNw1X_Q91w6f5xCd_pJz9pYjs9cpiWoa2nfpwKa-7ENHHw4Sj8kMsIiNeHuwoVDxKpZnRHYJGm9bS8AYC8WVMdrg==)

