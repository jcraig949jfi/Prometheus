# Followup [FU-2026-05-22-047 <- row250]: Primary sources uniformly state that the conjecture remains open

**Pythia queue id:** 332
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdCTDRQYXNUdklyLXcxTWtQMU5XRWlRNBIXQkw0UGFzVHZJci13MU1rUDFOV0VpUTQ
**Elapsed:** 249s
**Completed at:** 2026-05-22T02:27:11.043321+00:00

---

# Substrate-Grade Research Brief: Status of the ABC Conjecture (2026 Update)

**Key Points:**
*   The **abc conjecture** remains officially open; the mathematical consensus continues to reject Shinichi Mochizuki’s 2012 proof via Inter-Universal Teichmüller (IUT) theory, despite its 2021 publication in PRIMS.
*   Recent breakthroughs (2023–2024) by Hector Pasten have yielded the first major improvements in unconditional subexponential bounds in over two decades, utilizing Shimura curves and linear forms in logarithms.
*   The study of the "exceptional set" of the conjecture has seen rapid advancement in 2024 and 2025, with Browning, Lichtman, Teräväinen (BLT), and subsequently Bernert, breaking the trivial bounds using the determinant method and Fourier analysis.
*   In 2026, the **LANA Project** (Lean for ANAbelian geometry) was launched to computationally formalize anabelian geometry and rigorously verify IUT theory using the Lean theorem prover, marking a critical shift from human peer review to machine-assisted verification.
*   Kirti Joshi’s alternative framework of "Arithmetic Teichmüller Spaces" (2021–2025) claims to patch Mochizuki's gaps and prove the conjecture, though this too remains heavily contested by both Mochizuki’s camp and Western arithmetic geometers like Peter Scholze.

**Layman Summary:**
The *abc* conjecture is one of the most famous unsolved problems in mathematics, essentially stating that if two numbers $a$ and $b$ are composed of large powers of small prime numbers, their sum $c$ usually cannot be. While a massive, highly complex proof was proposed by Japanese mathematician Shinichi Mochizuki in 2012, other top mathematicians found a flaw they believe is unfixable. Because the two sides cannot agree, the problem remains officially unsolved. However, mathematicians haven't given up; recent years have seen huge progress in proving "weaker" versions of the conjecture and calculating bounds on how many exceptions might exist. Furthermore, a new international team is now using advanced computer programming (the Lean project) to translate the math into code, hoping the computer can definitively settle whether the original proof works or not.

***

## 1. Brief Summary
**Prometheus Context Query:** *Status update on the open question regarding the fundamental validity of the abc conjecture proof, confirming that primary sources uniformly state the conjecture remains open.*

**Summary:** The *abc* conjecture remains an open problem in mainstream arithmetic geometry; while Shinichi Mochizuki’s IUT theory claims a proof (published 2021) [cite: 1, 2], it is fundamentally rejected by the broader mathematical consensus following the 2018 Scholze-Stix refutation [cite: 3, 4], leaving the 2001 Stewart-Yu bounds [cite: 5, 6], Pasten's 2023–2024 Shimura curve improvements [cite: 7, 8], and Kirti Joshi's contested 2024 Arithmetic Teichmüller framework [cite: 9, 10] as the locus of active, rigorously debated progress, prompting the 2026 LANA project to attempt computational formalization via Lean [cite: 11, 12].

## 2. Flagged Findings
The current mathematical consensus asserts that the *abc* conjecture is **unproven**. However, the landscape of this consensus is highly fragmented, characterized by deep sociological and epistemological divides within the arithmetic geometry community. 

### The IUT Impasse and Scholze-Stix Refutation
In 2012, Shinichi Mochizuki released four massive preprints detailing Inter-Universal Teichmüller (IUT) theory, culminating in a claimed proof of the *abc* conjecture [cite: 1, 2]. Despite the eventual publication of these papers in the *Publications of the Research Institute for Mathematical Sciences* (PRIMS) in 2021 (a journal where Mochizuki serves as Chief Editor, though he recused himself from the review process) [cite: 1], the global consensus firmly rejects the proof [cite: 1, 13]. 

The primary vector for this rejection is the 2018 manuscript "Why *abc* is still a conjecture" by Fields Medalist Peter Scholze and Jakob Stix [cite: 3, 4]. Following a week-long meeting at RIMS in Kyoto, Scholze and Stix concluded that a critical gap exists in IUT Paper III, specifically surrounding "Corollary 3.12" [cite: 3, 14]. They argued that the proof relies on identifying certain isomorphic objects (anabelian reconstructions) across different "Hodge theaters," and that if one removes the overwhelming surrounding subtleties to restore standard arithmetic schemes, the core inequality becomes trivial and mathematically vacuous [cite: 3, 4]. Mochizuki has repeatedly dismissed these criticisms, stating that Scholze and Stix made "manifestly erroneous misunderstandings" and invalid simplifications of his theory [cite: 1, 15]. This standoff has resulted in a complete breakdown of communication, with mainstream mathematicians considering the matter closed (unproven) and Mochizuki's group viewing the mathematical community as fundamentally misunderstanding modern anabelian geometry [cite: 13, 16].

### The Arithmetic Teichmüller Spaces Alternative
Adding extreme complexity to the consensus is the recent work of Kirti Joshi (2021–2025). Joshi constructed a theory of "Arithmetic Teichmüller Spaces" using $p$-adic Teichmüller theory and the Fargues-Fontaine curve, aiming to provide a rigorous, universally comprehensible foundation for the ideas Mochizuki attempted to express [cite: 17, 18]. Joshi explicitly agrees with Scholze and Stix that Mochizuki's proof of *abc* is incomplete [cite: 10], yet he asserts that Scholze and Stix's rigidity claim in Remark 9 of their refutation is mathematically flawed [cite: 10]. 

In 2024, Joshi released "Construction of Arithmetic Teichmuller Spaces IV: Proof of the abc-conjecture" [cite: 9]. Joshi’s intervention has been met with resistance from both sides: Mochizuki strongly disagrees with Joshi’s interpretation of IUT [cite: 19], while Western experts (including Scholze) maintain skepticism regarding Joshi’s derivations, particularly the geometric bounding mechanisms necessary to fully close the *abc* inequality [cite: 19, 20]. The resistance to Joshi’s work heavily features **`PATTERN_BASE_RATE_NEGLECT`**, where the community's exhaustion from the decade-long IUT saga leads to an immediate heuristic dismissal of any new 500-page proof of *abc* involving Teichmüller theory, regardless of Joshi's distinct methodological provenance (e.g., his use of perfectoid geometry and the Fargues-Fontaine curve) [cite: 17, 19, 21].

### The LANA Project (Lean Verification)
Recognizing that human peer review has fundamentally failed to resolve the dispute, the ZEN Mathematics Center (ZMC) launched the **LANA Project** (Lean for ANAbelian geometry) in March 2026 [cite: 11, 12]. Led by Fumiharu Kato and involving experts like Johan Commelin and Adam Topaz (veterans of the Liquid Tensor Experiment), LANA aims to digitize the étale fundamental group of schemes and computationally formalize IUT theory to verify its validity objectively [cite: 11, 22]. Notably, Kiran Kedlaya joined the project to help build consensus, indicating that at least some respected mainstream researchers believe the sociological status of IUT requires computational resolution [cite: 21]. Furthermore, Yuichiro Hoshi (a close associate of Mochizuki) recently acknowledged that translating Corollary 3.12 into Lean has revealed "some insurmountable wall" for project members, marking the first time a RIMS insider has acknowledged the profound structural difficulty identified by Scholze and Stix [cite: 21, 23].

## 3. Problem Statement
The *abc* conjecture, first proposed by Joseph Oesterlé and David Masser in 1985 [cite: 1], interrogates the fundamental tension between the additive and multiplicative properties of integers [cite: 2, 15].

**Definitions:**
For any non-zero integer $n$, the **radical** of $n$, denoted $\text{rad}(n)$, is the product of all distinct prime factors of $n$ [cite: 24, 25]. For example, $\text{rad}(10) = 10$, $\text{rad}(72) = \text{rad}(2^3 \cdot 3^2) = 6$ [cite: 26].

**The Standard Formulation:**
For every $\epsilon > 0$, there exists a constant $K_\epsilon > 0$ such that for all triples of positive coprime integers $(a, b, c)$ satisfying $a + b = c$, the following inequality holds:
\[ c \le K_\epsilon \cdot \text{rad}(abc)^{1+\epsilon} \]
[cite: 8, 24, 27].

Alternatively, using asymptotic notation, for any $\epsilon > 0$, there are only finitely many coprime triples $a+b=c$ such that:
\[ \text{rad}(abc) < c^{1-\epsilon} \]
[cite: 28, 29, 30].

**The Quality Formulation:**
The "quality" of a triple $(a,b,c)$ is defined as:
\[ q(a,b,c) = \frac{\log c}{\log \text{rad}(abc)} \]
[cite: 1, 5]. The *abc* conjecture states that for any $\epsilon > 0$, there are only finitely many triples where $q(a,b,c) > 1 + \epsilon$ (i.e., the limit superior of the qualities of all coprime triples is 1) [cite: 5, 31].

**Extensions and Variations:**
1.  **Explicit *abc* Conjecture:** Formulated by Alan Baker (2004), proposing specific computable constants. For instance, determining if $c < \frac{6}{5} \text{rad}(abc) \frac{(\log \text{rad}(abc))^\omega}{\omega!}$ where $\omega$ is the number of distinct prime factors [cite: 1, 26, 31].
2.  **$n$-term *abc* Conjecture:** Generalized by Browkin & Brzezinski (1994) for $n \ge 3$ terms: $x_1 + x_2 + \dots + x_n = 0$. The bounds are adjusted based on the number of terms [cite: 1, 8].
3.  **Algebraic Number Fields:** Generalizations bounds to algebraic integers, replacing the absolute value with the projective height $H_K(a,b,c)$ and ideals norms, investigated heavily by Győry [cite: 6].

## 4. Status & Bounds
Given the rejection of Mochizuki's claimed proof and the pending verification of Joshi's work, the highest-grade established mathematics regarding the *abc* conjecture resides in bounds that limit the size of $c$ relative to $\text{rad}(abc)$ unconditionally, and bounds on the size of the "exceptional set" of triples that violate $\text{rad}(abc) \ge c$.

### Unconditional Subexponential Bounds
For decades, the best unconditional result was due to Stewart and Yu (2001) [cite: 5, 6]. Using $p$-adic linear forms in logarithms (an extension of Baker's theorem), they proved that for $a+b=c$:
\[ c < \exp \left( K_3 \text{rad}(abc)^{1/3} (\log \text{rad}(abc))^3 \right) \]
[cite: 1, 5, 32]. Because the exponent $1/3$ is applied to the radical, this bound is exponential in $\text{rad}(abc)^\alpha$, falling vastly short of the polynomial bound $c \le K_\epsilon \text{rad}(abc)^{1+\epsilon}$ required by the full conjecture [cite: 8, 27].

In **2023 and 2024, Hector Pasten** achieved a watershed breakthrough, establishing the first major improvements on subexponential bounds in over two decades [cite: 7, 33, 34]. Pasten cleverly combined the transcendental methods of linear forms in logarithms with a modular approach relying on **Shimura curves** [cite: 7, 35]. Pasten's methods allowed him to separate primes with large exponents from those with small exponents, achieving new unconditional bounds. Furthermore, he adapted this to the 4-term *abc* conjecture, proving unconditional bounds that do not depend on the radical of one of the variables [cite: 8]. 
*(Note: A classic cognitive trap found in analyzing Pasten and Mochizuki's work is **`PATTERN_CONDUCTOR_CONFOUND`**, where non-experts conflate the bounds on the minimal discriminant ($\Delta$) with the conductor ($N$) in Szpiro's conjecture, leading to misinterpretations of whether the analytic rank fundamentally alters the exponential gap. Pasten's Shimura curve parameters correctly scale with the conductor, bypassing classical limitations on discriminant bounds [cite: 7, 36].)*

### The Exceptional Set Bounds
A weaker form of the *abc* conjecture asks: exactly how many "exceptional" triples violate the bound $\text{rad}(abc) < c^\lambda$ for $\lambda \le 1$? 
Let $N_\lambda(X)$ denote the number of coprime triples $(a,b,c)$ such that $a+b=c \le X$ and $\text{rad}(abc) < c^\lambda$ [cite: 29, 37, 38].
*   **The Trivial Bound:** Derived from basic divisor density, $N_\lambda(X) \ll X^{2\lambda/3 + \epsilon}$ [cite: 29, 37].
*   **BLT Bound (October 2024):** Browning, Lichtman, and Teräväinen produced the first power-saving improvement over the trivial bound near $\lambda=1$. Using a combination of the geometry of numbers, the determinant method, Thue equations, and Fourier analysis, they proved:
    \[ N_\lambda(X) = O(X^{33/50}) \quad \text{for fixed } \lambda \in (0, 1.001) \]
    [cite: 29, 30, 39].
*   **Bernert Bound (June 2025):** Christian Bernert further optimized the BLT methods, showing that by restricting to just the geometry of numbers and Fourier analysis, the bounds could be structurally improved. Bernert proved:
    \[ N_\lambda(X) \ll X^{\frac{23\lambda+3}{40}+\epsilon} \]
    For $\lambda = 1$, this yields $N_1(X) \ll X^{0.65+\epsilon}$, entirely subsuming the $0.66$ BLT bound [cite: 37, 38]. Bernert also noted numerical refinements could push this to $N_1(X) \ll X^{8/13+\epsilon}$ ($X^{0.6154}$) [cite: 37].

## 5. Literature (Primary Sources)
*Note: Due to the template constraints, this list strictly contains primary sources explicitly generating state-of-the-art bounds, refutations, or structural theories.*

| Author(s) | Title | Date / Journal / arXiv ID | Contribution | Citations |
| :--- | :--- | :--- | :--- | :--- |
| **Stewart, C.L., Yu, K.** | *On the abc conjecture, II* | May 2001 / *Duke Math. J.* Vol 108 | Established the best unconditional exponential bound $c < \exp(K\text{rad}^{1/3}\log^3\text{rad})$ via $p$-adic linear forms in logs. | [cite: 5, 6, 40, 41] |
| **Mochizuki, S.** | *Inter-universal Teichmüller Theory I-IV* | 2012 (arXiv) / March 2021 (*PRIMS*) | Proposed a proof of the *abc* conjecture via anabelian reconstructions and Hodge theaters. | [cite: 1, 2] |
| **Scholze, P., Stix, J.** | *Why abc is still a conjecture* | July/Sept 2018 (Preprint) | Detailed refutation of Mochizuki's Corollary 3.12, establishing current negative consensus. | [cite: 3, 4, 19] |
| **Pasten, H.** | *The largest prime factor of $n^2+1$ and improvements on subexponential ABC* | Dec 2023 / *Invent. Math.* (2024) (arXiv:2312.03566) | Broke the Stewart-Yu barrier using Shimura curves, giving the best known subexponential bounds. | [cite: 7, 35, 42] |
| **Pasten, H., Sepúlveda-Manzo, R.** | *We revisit a subexponential bound for the abc conjecture...* | June 2024 (arXiv:2406.05083) | Expanded bounds to the 4-term *abc* conjecture without dependency on $\text{rad}(a)$. | [cite: 8, 27] |
| **Browning, T., Lichtman, J.D., Teräväinen, J.** | *Bounds on the exceptional set in the abc conjecture* | Oct 2024 (arXiv:2410.12234) | First power-saving bound $O(X^{33/50})$ on the exceptional set $N_\lambda(X)$ near $\lambda=1$. | [cite: 29, 30, 39] |
| **Bernert, C.** | *The exceptional set in the abc conjecture* | June 2025 (arXiv:2506.13364) | Optimized BLT to $N_1(X) \ll X^{0.65+\epsilon}$ using anatomic reductions and Fourier analysis. | [cite: 37, 38] |
| **Joshi, K.** | *Construction of Arithmetic Teichmuller Spaces I-IV* | 2021-2024 (arXiv:2106.11452, 2403.10430) | Alternative proof framework using Fargues-Fontaine curves; directly contested by RIMS and Bonn. | [cite: 9, 17, 18] |
| **Cuevas Barrientos, J., Pasten, H.** | *On the greatest prime factor of polynomial values and subexponential Szpiro in families* | April 2025 (arXiv:2504.15971) | Further applications of the Shimura curve / linear forms method to elliptic surfaces. | [cite: 36, 42] |

## 6. Attack Vectors
### Live Techniques
1.  **Shimura Curves + Linear Forms in Logarithms:** Pioneered by Hector Pasten (2023-2025). This technique connects transcendental number theory (Baker-Matveev bounds on logarithmic heights) with arithmetic geometry (Shimura curve parametrizations of elliptic curves) [cite: 7, 8]. By separating primes with large exponents from those with small exponents, Pasten bypassed the geometric rigidities that stalled Stewart and Yu [cite: 7, 33]. This approach is highly active and yielding results in related Diophantine problems (e.g., $P(n^2+1)$ bounds) [cite: 7, 36].
2.  **Determinant Method & Fourier Analysis (Exceptional Sets):** Used by BLT (2024) and Bernert (2025). This involves converting the *abc* constraint into bounding the density of integer points on high-dimensional varieties [cite: 30, 37]. The equation $a+b=c$ with constraints $\text{rad}(a) \sim X^\alpha$, etc., is attacked by bounding $B_d(\mathbf{c}, \mathbf{X}, \mathbf{Y}, \mathbf{Z})$ [cite: 30, 38]. Bernert showed that combining the geometry of numbers (Minkowski's theorems on lattices) with symmetric Fourier analysis provides optimal sub-trivial bounds [cite: 37, 38].
3.  **Computational Formalization (Lean / LANA):** The transition of anabelian geometry to interactive theorem provers. The LANA project aims to use functional programming (Lean) to rebuild the fundamental theorems of absolute anabelian geometry (Belyi cuspidalization, Kummer theory synchronization) to completely evaluate the logical structure of IUT without human sociological bias [cite: 11, 12, 22]. 

### Exhausted Approaches
1.  **Pure $p$-adic Linear Forms in Logarithms:** The method of Stewart and Yu (1991, 2001) effectively plateaued at the exponent $\alpha = 1/3$. Without geometric intervention (like Pasten's Shimura curves), classical transcendental constraints prevent pushing this exponent toward $1+\epsilon$ [cite: 8, 27].
2.  **IUT Theory (Human Verification):** Mochizuki’s original 2012 formulation, operating via Hodge theaters and mono-anabelian reconstruction [cite: 4, 23], has exhausted its runway for consensus via standard mathematical peer review. The Scholze-Stix refutation demonstrated that human experts cannot reconcile the required multi-universe diagrammatic commutativity with standard arithmetic schemes [cite: 3, 4, 13].

## 7. Cross-References
*   **Szpiro's Conjecture:** The geometric origin of the *abc* conjecture, predicting a bound on the minimal discriminant $\Delta$ of an elliptic curve in terms of its conductor $N$ ($|\Delta| \le C_\epsilon N^{6+\epsilon}$). Mochizuki’s IUT technically claims to prove Szpiro's conjecture, from which *abc* follows. Pasten’s recent work also heavily interrogates Szpiro bounds in families of elliptic curves [cite: 1, 36].
*   **Vojta's Conjecture:** A sweeping generalization of *abc* to algebraic varieties of higher dimensions. Scholze and Stix noted that Mochizuki's claimed proof implies a uniform version of Vojta's inequality for curves, which behaves well under branched covers [cite: 3, 4].
*   **Fermat's Last Theorem & The Beal Conjecture:** Fermat's Last Theorem for large exponents is a trivial corollary of the *abc* conjecture. The Beal Conjecture (if $A^x + B^y = C^z$, then $A,B,C$ share a prime factor) is intimately connected; the *abc* conjecture implies there are only finitely many counterexamples to Beal [cite: 1].
*   **Liquid Tensor Experiment (LTE):** An anti-anchor / precedent. Scholze successfully challenged the community to verify a highly complex theorem in condensed mathematics using Lean [cite: 11, 12]. This proof-of-concept for formalizing cutting-edge mathematics directly inspired the 2026 LANA project's attempt to formalize IUT [cite: 11, 12]. 
*   **Fargues-Fontaine Curve:** A candidate primitive heavily leveraged in Kirti Joshi’s 2021-2024 work on Arithmetic Teichmüller Spaces. Joshi replaces Mochizuki's highly idiosyncratic pilot objects with rigorous $p$-adic geometric objects (untilts of $\mathbb{C}_p^\flat$), creating an alternative, formalized "Rosetta Stone" for Teichmüller deformations [cite: 18, 19].

**Sources:**
1. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzCb9PxTJTTq3FjIw-UJGa-2zkKXBhETIXqhYS1-bVrbw0thLzhxSn7J85QDpYH7Zjvcwz36RaC2eght1riQ4vWTwV_NlaUNYMw0UIykoQsLdkySKDVihtskfqrcW7b249Dg==)
2. [kyoto-u.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF58_CZ7D_OLwmUdQoH7j5x1eM5MCZn5ZNM-dpyTXduB39lPMadHFNf1xua2CVnJHoh9GLFPB1wfVLCkwD40Pb_eiSV9Oa2mvRJWxmHrVeb8z-iAydF0jAKuZ7NZCVcdHK2ZWSOHK0Vn_qvXWFVOm6f2v0xdOYb5g5ovA==)
3. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEj5yg3BKwWDALIx4La7G1UclLWuBNK1nx3YkopgmpwSEPqUwU0iNDxDsQld2ebbopuMI04A-qIJhMVeg20gcTSpNlJX0fZFv56qbrH_wdihFhyFJYo5m7FQ6Hxy3BwUp9ZvxpBUhomprgQSglFAzhxNesgnNwY)
4. [uni-bonn.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKeq9gdkQJ62KnKAjuFdavqbj6ncA0AS-hhrDjwobk7kCXogS1CoiOuLzYqL7E1pukMQIzkujrF5-7Vw0fp6DvN9_2gVMZ9qD8Qi0Qyc5MSvR1s32GLkRWCNbCMFaZBh1T9KFDtrZJ3HLeMcPB14ETqyrd6tklwonlXFThUYE=)
5. [ubc.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHI6wfStEU5FXEV6O3xssrYol5gga5uaqko-kz4vhlQs8BmPfVr8dESiw-9mA_EzidpLJR3YGFU3cXGnx8D2opSsFjk-KCKP6Z__Uzgl8M-tvPzDzjbNq7Obqvl7jDhg1WlK8x3xfzzrzR2xWDW0L4D)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJTHKGAdjW9TLv3w0of0u-hxfsx0SJ5IoYX_hzQ5qR0yeNNCkl4PpW3YsTowB4ZeVIO_jB7TTavMJqIsVh_vUUpUudTrOddUiBWQKoBJgHh6S-otcGkcaW8l-k_4prGWvGCGZQ1UFgxSMqUhwRYAAStwf2oUT9aSYtjQuv1NBO_E4=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHROVRP4l8K4yHmPeKK2pt-Bvo0CAWSvCa5PpUbGYk2T56ATtefEXxtMfmTW_F045pJzqDSEtcPcWIhpai8avF8ArGeyIuIRHHfAHYsp9GeMB0K7f448g==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLjMshuC_UocEgfHTh8M0mbXIzc5Y40sMpGekg1mI6O2Ouh5mMQpc-UE9hfjTZ4U1CkTV0ss2I7VgmOTeT9i2Xcnga3Whk_PKD1nQxgHIcgz8JYG8LnQ==)
9. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsTFmhxPe2NMyA8tiHmpplNp5NvB6er-ZwqLN1kf_kgyKS5D-pL2zYhArwZJTaqbXai6YeJRWb9pSjr6QOu4FO2TZohDJLxEHJRnCuYK9axoSpyzzBhB6rXtlDH47tTg==)
10. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFj1zKDZFY3fyaNDcRNxHguBowG20_syh5QraPzEvNT7ZkPRebvD1rPsbyu8aXXb27JZ57knYZG2dj10SSN-lX47B_CDbElqj4WMQWSC9rrbA-6TWv8NmnnB3ywWnJF_7zImCVzcemchvR1ZxOiY4pjP39uZkQkxMYIF3YLySESZ7_wG7rPTzC-wUchg8XJYa6t_aqNLm9FhmymrP5LTuOTZQBKIoXTrx3fG-3-aePz2_8IO0=)
11. [zen.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsJR36TefxmllP2BXiGJUs6cUB3tOAVyRZ_l0uyPaFekWGnWu2s6dgmSfNpGJiThZ5yploJxcQjTigncQ1jQhfmVzA_UUT-4BZ3N2wv62A5XXJmrX4h7K8cEGUW5uk)
12. [zen.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_GqjEMNNCiU_ySxOs-rcqUnlQCoyBdF_GEwboneSCPhQ6wBqc2e5K0o0VCeopxloxXJ9b7vI8jlqo_8M2tyvOuBNJNphO83fPeb8YBMdZlJ8u3Ksnn29SIcVyV89a9d0NRA==)
13. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBrfknF6TAJDoOWv-5G9DlGwGpydEZawLNrtdBxrtmKDPwj2lEq3e1Yy5dXfSTzLdXIkZm5Moe58kZowjNMcq8SDgipbPf-qawKwIULffefz9L7snY_TodoubrejIdyw_8NP4ymaH01K4hdcx33-0RNgpq7fM7fVrUM72ywkJXOQBheBfMxjFtb42MqKSeMvEsYNUzD64=)
14. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEa1ePwf5mPRLPkf4CbR_js8VoYuUMv0u_A1TIFe8UaveQLvoN_OtrYQgVChimDpFFHuvsm1K6qd9c6KuaTKIrAHvVifNHlFBDDQKyyru4qMm0JU11DoBW6cNgE_95IQdMyGwPBci4kfh6BWOZnK-_zpA==)
15. [wellesley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrPzny7701CESpmnS5q-99mRwY-AO1zxzxOsSNkHpKOE3kiZXSIuCjfwKk1aQa6c8lpZK2ysQfK0h4v4KS9BwfCMFoA6v5Q1cozBCHFn20Pr7LuIIyo7QdQ7BQEsSDvbnELMXyntR9iaeaLP6pH7vV6cyAB5lxYzOVxuJ3CMEa2XwgyvBIhGPHXw==)
16. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcpuRGIGIlVS1hzEdjQiZ1RHe3rWH64guH8u9pyQlN3a4mZQ05Bv3vgpgXxTr_w12kBZIXvZvQoTu8rcPiipQUhP5Ktz36a-h_LUtw1KZtOZbKJEATQ7YsDQ36huXHo0bjfsU4kc_gyRe6B-QUiPuMyOiH2Jwzm-rNNJX_fcy6VaX9S6ac8CGxfnOHrjI_Z1AxnfwS0nfqPMoT2wGm2zYXVG-VCNqpcneKYP-L4YgGbnp04JzcD0JL1LMcABg6HgdtYQ==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDnYMsElGLln1Es58FP5ZVDrucmc0Hx-Cq2tBFysRpKPXK6srKxHVqOJAn18lEQZfs_IIQabzZ4GutARRqzYOTv127jqdJiClnLgsFS6xyq7aLWrh1Nw==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRodsRiwJixbibWvJZGrvjKSTku4lUl2aR1tKcTrwCD7UrCx56N1IT_98ygV-4Ztr-S11gHytTxaXkahYGG306dVSVpjZ6CJlWJekvph-9mkJ_89ji3A==)
19. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzsZF85BcegkT6EyXQlQS4HvyEXGfRV2vTP32EH9gyfqV4dgf8PBexrD0NStkZoKc9_oDjTnLepGGzNrKfdb11UFGeHQ-w1r_fNDhMVZtzZJVFdqKQPwOE0LHIJJqBt-_rOGWBYzbwzXy9V2oW)
20. [arizona.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHR2gw97MLjYMhHy4azkfO-hTkxZrPrmzs4Z5CSlCj6dMEbhR78x7YPUIf5UY_7UBZsFgkqdb6-8cMmzwscYf1UVLajAy7nyJVGrE6lwoayeJtWgsC1BR_s0fc92w==)
21. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwhxfkuFcCwy1PZS5gyQLxoCe4nr1FSrqG1UEEEBvoKyXizpsH3qtCmKpZZiloOCHYc4w_X0WvCdpqpSFnKSWMQsGOv0EVT4AJHkWw4w6D3qdYaOFk0YJpGBJVukcPQ2XSKVa_CF2-QzT-K7cvGUODYp5Jn5cnbyr3rt5CD3v-gnLMCROM_qFdsa9s83vh)
22. [cnrs.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJT89IgQTwbSuM811IYY0dznhfDW2UnqGhfFQYuyYENks_PjRCoPydu8I2BdLvj8vSzIjw__yK_cAYga2tRxgFxC2Vz6FGLSO3yfQjZj_BP3PYEEwnpIrUmQEtIPdqs8m9rpVrf4BVkJnpQElQvoVXlfgHQayj9hMOwp9atoTTqKj5htCG4A==)
23. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRCIwzMJs0Obus89545ZblDx299qy7ec9Gk1VCrznrabDcCfIyKnkRJPrzWJxua0IFxeiGBYT4E0QAN7Y2JHGTRIJqJ6ipHyi37SmQ6ZU_DEjmlzdQgNrpk7aKsc5gC47WPBe47_8f6_7OrbGEdO8z_nXsdsjKpNdqRzw=)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9aI-5dMVPkAU4rX7k-nRGZEwoS-ENqqlVbofwNOYIcBqPpdT_OFAA2WpD4v40eHTbx4bz7kFJ_QHmfUiseLQ6ZTJUK67lj3Hs45FMFsiQ97PnUYO8z41a35mS6B3JMd76Wy4ensd0h9HAO1NHNjb2nWlQ5Lw0N7G7oQB3SuJohiQkV2w2ZRR_cXhUw6unjjmz)
25. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQPJzR1D1WYK0dUg_sZTQJslI0EB3acLsz3tH0nnJw25gQgk8oedhxcQYl1Gc1GlcPI17LDx23m-jdB6oo1QdaS0UTCFmeB8MuL1laQwO7gayzwfaHesYtm0sHFvRhbQyqoI9iqcc=)
26. [dartmouth.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPVTtR2vnYpZdiSfTl_lHCuWq5j2ROq8L_1kBMqFy-4w9jv54P4F3qMi3GGVd0hBR96HrNa_NY2AoJqefVkADLcfj_RqgVmdviRjQYQM5iyN6LWjrkOoTwvJEbumw5cFiN1fk=)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFK1w553MRhxMd9zqF-xj8C6NsyOSUTw2bajvTxFEdvuJ6L4soIlqwRVauiWp3CtduFxs60gjTBZcIK_2OUSqPjALjtUK3X1cspxg05pYyKYLTTxW2mE8vqBg==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwze9WuontvGcOVMjE184RSS7VG4Hk78TMZj70SsjoJJLau_r_8t45316MLVe3c5kToRdLYd-9nbBBSs9lYMdcuflX7DvEBxhcMgq7RvfBgcMZ9MbePS_MSg==)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0KIHY4jWys8xICGd4luoYnDp9A14di4zjv582y8mT2mIePw1v5ISbAifH2U5beJoFxkYFFD1RpHjY9jT25NNyT6RU-GOot7hPC3uvTY_W_bKbjA0TpA==)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8KpZnuj3qvryQoglS277htu-e7nuNRjVLISG66SAMmWcQ_TVpQxRBkNqTQMTMUMtiXmh0yrEO0NzF73vatyszo_W4RURvDxJxYW8I-Bb49EsbfnbA8lzAs4k6pFsCIPGuiJTseTnyGMMzyD0uedvwWVGZp2q0c05rXp0FYyUxCbtvHNdCKb0OovKUdXw7doBZwhF0tLOPEIENPfs=)
31. [gjaets.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEC3kGC-fq936mewsZVpwuRsoHVInmiFmCsxarHQar1hXin6e0VzHrmrxJE51KaugacCcPIvdgzwwZCPiIfa9ipPlEKK2gpQDkFnZtl1O4Cu4-u1wixUi24gO7b2hzxVSt_6yfxvVnw2_cc0DmdY8NO)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHq_siYX11ZsjJHUtgCxrBi3ledzUguFiMaMOwcAUtpo4wovDO0v_VFH4tNYosD-omx-iJ9TMyyvGhf0H6M0K5Si7aeLXpfJx0BdWOu67OvmznRTwLemw==)
33. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQET64b8LNFdm9ErlXb0aAcunfCGEq0kfmp5Rk-9qjOBmuf2_Ux7NhIOkQzbvsEFQ4hFWK_-MQZUKUz1g0xL_LYd1W4GMgt-vcCKBzXV61M1AhTqDGo4V4b3UQ==)
34. [generaciondecambio.cl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1Vdwv2AfeaspdpQmGghkaYjhHdpr2_2sW3TKpr9QshTY0ChQQsE5j3q8hnuVanD2MRm5mdf6UU6CHDons1hpAeEO4xfLVAIXjMVRZY2gbQ40Azbqw3Tkd6sGD5jGNE5oaf36xxQFW0gsbuldlA2h6zzh24E8vePn_cWpII5SpCX2k1OQQ8VNIC_SiNo5RXevEABwXUwH9-FMZgw==)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYR_NxTrEdygwh94ftWnuOCbqJ11t-3BHOQ9tdAPSalIjrAyIAzdn5B0HND_wn7L3uXa16OCkSITPlJIGE6t88-ftvdlKtAFiiTgZBGrIyEbJRUgZrTw==)
36. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOCUGM2tDoa16aas4FsuNKSZ7eHwFlBT9eIt4o5rwo562o00ywpYRQs4jGvs8II77p2BopKXvIVxC8M547JJfLP9gOWah9CoMIsahS8THPmIRd8GPhnw==)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtiuvNq7aQPRfz1ZbfL7jMM-usoeoG8gfm93PhsTUtmjaaW4HHQe0OOd9muOwBQzVn6LefuAmKSkpExMiLgvhF0-4IbKfBrH8SF0qn6BoPr9HlvfENCA==)
38. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOZ8Tfj0K6ZoykI9q_0RCOyu63mZj6BjXC2o6EurO103KisIjunvphdaVtZXCxyHXUqjOGe04VBpxU4odmhzf8lORZC5boXUJpDnTbb8WqFhNxvddf2lDZGnSsoE9wRSaiO5TzRiI5s6msxsT5NtsgtHmfUxJKcbbEuBq-Czv5s2dhFGqm)
39. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEORcymwy2CI2ggNBbkuGacs4Yf6vq5KozBVlD8F-cZhSNPYOTc7p2JfVAR-23LgOxw6JpLzLhY4vt1TgLxTNEoz36fQXyjFQxteXeTlYa7Ov3MG64U7Q==)
40. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-hXkrfSLwAo6IRKD21cbthLRuFtIHXUuqJsA-530-vvwb-jpTraahLcZrc8orSb5EdxcCpectggKWw-GU0qtDYho4F0_qHQF3f20IdfuMvPhYf94ExmIFCvwiP_HyVao2exOTj_vpESEkvzzSDZHfZV40FUsQ9B_kM5x9Pym-xUioIGQWp5Qnu-YnSO8K44zNcGo3G9KezPodSbEWQzX2kQvtHq7uxyoys7I=)
41. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFF6q9IYEU2sJMstTDJuECy_flrCqJ9C98iNV6J0DUBZisFAvABuQU3UBsM-OuCy2d95E5wdj821A6XmvdCsy-EBtSS7-QsOSVO-ssh02dYEsRLQL_t_w5ahKVOJEk5vPIXnDYrmLdlziptB2kB2sXSRDZJm64HTNjo2uvyXDA9mdXbta_qjsakdi24YZ-WU1aYwk5Lijx-ak-kET7E9P7Ev6IPteP7g1F-gGHKZyjm9Q7HTqCV7Z4jEWMaG1qv2RrEQ==)
42. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFltkXkwOYFDTs6AxuFUdMn5VyfD169lEqrB8Lfc5q-v0OSHFxwes1BNUd_0gofSgsBWKtkBz8_XyixWknkHjky9ewIcBpw-BP0EzoCQJbPElcNE6WL3bhBhRKqFMDps_2YgDmtETrQcR7KFQdBYWP7gSEMjXxOwmQdVKAR7IWqOXcwKEZK2cZ-FpODmqvzA3ucQnl4O5UgWHu2ef4CKNUyPL4u74d99ai2nd-bGHoU)

