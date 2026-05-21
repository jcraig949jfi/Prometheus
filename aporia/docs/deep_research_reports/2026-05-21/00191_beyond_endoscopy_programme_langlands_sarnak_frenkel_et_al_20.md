# Beyond endoscopy programme (Langlands, Sarnak, Frenkel et al) 2024-2026

**Pythia queue id:** 191
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChczVUFQYXZ1M0E1ZS1fdU1QMC1hUzBBNBIXM1VBUGF2dTNBNWUtX3VNUDAtYVMwQTQ
**Elapsed:** 250s
**Completed at:** 2026-05-21T17:33:12.333735+00:00

---

# The Beyond Endoscopy Program (2024-2026): Recent Advances, the Trace Formula, and Functoriality

**Key Points:**
*   **The Beyond Endoscopy Program:** Proposed by Robert Langlands in the early 2000s, this mathematical strategy aims to prove the general Principle of Functoriality—one of the central questions in modern mathematics—by isolating automorphic representations whose $L$-functions possess a pole at $s=1$.
*   **The Role of Sarnak and the Kuznetsov Formula:** A significant branch of the program, pioneered by Peter Sarnak and advanced in 2024–2026 by Yiannis Sakellaridis and Chen Wan, seeks to bypass the non-tempered Arthur packets of the Arthur-Selberg trace formula by employing the Kuznetsov relative trace formula, naturally isolating the Ramanujan spectrum.
*   **Frenkel, Langlands, and Ngô (FLN):** The foundational 2010 work by Edward Frenkel, Robert Langlands, and Bao Châu Ngô established the heuristic of applying Poisson summation to the Steinberg-Hitchin base, paving the way for the rigorous treatment of trace formula regularizations.
*   **Recent Breakthroughs (2024-2026):** Researchers have successfully generalized the preliminary Beyond Endoscopy steps—initially proven for $GL(2, \mathbb{Q})$ by Altuğ—to totally real number fields (Emory et al.), to ramified settings (Cheng), and to higher-rank groups such as $GL(3, \mathbb{Q})$ (Deng and Espinosa). 

The following report synthesizes the contemporary progress within the Beyond Endoscopy program between 2024 and 2026. It is highly technical, addressing the evolution of trace formula methodologies, the algebraic geometry of parameter spaces, and the analytic number theory techniques required to manipulate orbital integrals. While the goal of proving Langlands Functoriality in full generality remains a work in progress, the period from 2024 to 2026 has witnessed unprecedented success in executing the rigorous local-global comparisons envisioned by Langlands, Sarnak, and Frenkel.

***

## 1. Introduction to the Beyond Endoscopy Program

The Langlands program is often described as a grand unified theory of mathematics, establishing deep symmetries between number theory (Galois representations) and harmonic analysis (automorphic representations of reductive groups). At the heart of this vast web of conjectures lies the **Principle of Functoriality**. Functoriality posits that a homomorphism between the $L$-groups of two reductive groups implies a corresponding transfer of automorphic representations between them. 

Historically, the most successful approach to establishing cases of functoriality has been the **Theory of Endoscopy** combined with the **Arthur-Selberg Trace Formula**. Endoscopy, which relies heavily on the Fundamental Lemma (proved by Bao Châu Ngô), is uniquely suited to cases where the image of the $L$-group homomorphism falls into an endoscopic subgroup [cite: 1]. However, endoscopy is inherently limited; it cannot address functorial transfers where the target $L$-group is not an endoscopic group [cite: 1]. 

To attack functoriality in full generality, Robert Langlands introduced the **"Beyond Endoscopy"** program in the early 2000s [cite: 2, 3]. The strategy is a two-step process:
1.  **Isolation of Functorial Lifts:** Isolate the packets of cuspidal automorphic representations whose associated $L$-functions (for a specific finite-dimensional representation of the dual group) have a pole at $s=1$ [cite: 4, 5]. 
2.  **Comparison:** Compare this isolated spectral data between two different groups to deduce the existence of the functorial transfer [cite: 5, 6].

To achieve the first step, Langlands proposed weighting the spectral side of the Arthur-Selberg trace formula with the order of the pole of the automorphic $L$-function [cite: 4, 7]. This weighting explicitly requires the introduction of $L$-functions into the trace formula "by hand," a massive departure from standard trace formula techniques which traditionally rely entirely on compactly supported test functions and their orbital integrals [cite: 3]. 

### 1.1. The Frenkel-Langlands-Ngô (FLN) Heuristics
In 2010, Edward Frenkel, Robert Langlands, and Bao Châu Ngô authored a foundational paper exploring the stable trace formula's potential in this program [cite: 1, 8]. A central challenge of Beyond Endoscopy is that the volume terms associated with the geometric side of the trace formula (summing over regular elliptic elements) diverge if one naively completes the sum over the parameter space [cite: 7]. 

The Frenkel-Langlands-Ngô (FLN) approach suggested rewriting the geometric terms as limits of Euler products and making use of the **Steinberg-Hitchin base** (the invariant-theoretic quotient of the group by conjugation, which for $GL(n)$ corresponds to the space of characteristic polynomials) [cite: 1, 3, 9]. FLN proposed applying a Poisson summation formula to this base, despite the space of conjugacy classes lacking an obvious linear structure [cite: 3, 9]. Their heuristics suggested that the dominant term in the dual Poisson sum should equal the contribution of the trivial representation of the group, thereby providing a pathway to rigorously compute the weighted trace formula [cite: 7]. 

### 1.2. Sarnak's Early Intervention and the Kuznetsov Alternative
While Langlands focused on the Arthur-Selberg Trace Formula (ASTF), an early and highly influential suggestion was made by Peter Sarnak [cite: 10]. In the ASTF, the discrete spectrum contains non-tempered "Arthur packets" which do not satisfy the generalized Ramanujan conjecture. These non-tempered representations pose a severe analytic obstacle when attempting to evaluate the $L$-function residues [cite: 10, 11]. 

Sarnak suggested that mathematicians circumvent this problem altogether by replacing the Arthur-Selberg trace formula with the **Kuznetsov relative trace formula** [cite: 10, 11]. The Kuznetsov formula naturally incorporates Whittaker models, meaning that it inherently filters out the non-tempered spectrum (including the problematic identity representation) and strictly isolates the "Ramanujan" spectrum [cite: 10, 12]. This insight bifurcated the Beyond Endoscopy program into two distinct but deeply related methodological tracks: one attacking the singularities of the ASTF, and the other leveraging the analytic advantages of relative trace formulas [cite: 12, 13].

---

## 2. The Arthur-Selberg Trace Formula Approach (2024-2026)

In the standard Beyond Endoscopy framework utilizing the ASTF, researchers must manipulate the regular elliptic part of the geometric side of the trace formula. The pioneering success in this domain was achieved by S. Ali Altuğ (circa 2015), who completely executed the first step of Langlands' program for the unramified case of $GL(2, \mathbb{Q})$ [cite: 4, 14]. Altuğ successfully applied the approximate functional equation to control the analytic behavior of tori volumes, smoothed the singularities of real elliptic orbital integrals, and applied Poisson summation to isolate the trivial representation [cite: 8, 15]. 

Between 2024 and 2026, the mathematical community succeeded in drastically generalizing Altuğ's preliminary analysis to totally real number fields, to ramified settings, and to higher-rank groups [cite: 2, 14, 16].

### 2.1. Extension to Totally Real Number Fields: $GL(2, K)$
In April 2024, Melissa Emory, Malors Espinosa-Lara, Debanjana Kundu, and Tian An Wong published "Beyond Endoscopy via Poisson Summation for $GL(2, K)$," successfully extending the first phase of the program to totally real number fields [cite: 2, 17, 18]. 

In generalizing from the rational numbers $\mathbb{Q}$ to a totally real number field $K$, the researchers had to navigate the transition from classical Dirichlet series to Dedekind zeta functions and manage the arithmetic complexity of the rings of integers $\mathcal{O}_K$ [cite: 2, 6]. Emory et al. employed an additive Poisson summation on the regular elliptic terms of the geometric side of the trace formula [cite: 2]. By incorporating the approximate functional equation, they were able to adequately smooth the singularities associated with the archimedean orbital integrals—a critical prerequisite for Poisson summation [cite: 8, 15]. Through this mechanism, they successfully isolated and canceled the trace contributions of the trivial and special representations of $GL(2, K)$ [cite: 2, 6].

This work highlighted key arithmetic differences between $\mathbb{Q}$ and general fields, particularly concerning the behavior of class numbers and regulators of the tori that parameterize the elliptic elements [cite: 17]. The isolation of these specific representations confirms that Langlands' strategy is robust outside the simplest rational cases, providing essential momentum for the application of Beyond Endoscopy to general Shimura varieties [cite: 1, 17].

### 2.2. Incorporating Ramification: Yuhao Cheng's Work (2025-2026)
Another major limitation of Altuğ's original breakthrough was its restriction to the unramified setting. In May 2025 and 2026, Yuhao Cheng successfully generalized the first step of Beyond Endoscopy for $GL(2, \mathbb{Q})$ to the ramified case [cite: 16, 19, 20]. 

Cheng considered the setting where ramification occurs at a finite set of places $S = \{\infty, q_1, \dots, q_r\}$ with $2 \in S$ [cite: 16, 19]. The presence of ramification introduces severe irregularities in the local orbital integrals at the primes $q_i$, obstructing the direct application of standard Poisson summation [cite: 4, 16]. Cheng's methodology adapted Altuğ's approach by carefully evaluating arbitrary smooth test functions at the places in $S$ [cite: 19, 21]. 

By modifying the approximate functional equation to account for the ramified local $L$-factors, Cheng ensured the analytic validity of the Poisson summation formula on the space of characteristic polynomials [cite: 16, 21]. Cheng subsequently computed the residues of the resulting specific functions to rigorously isolate the desired specific representations (the residual part of the spectral side) in the elliptic part of the geometric side [cite: 16, 21].

Furthermore, in a follow-up preprint titled "Beyond endoscopy for $GL(2)$ over $\mathbb{Q}$ with ramification 2: bounds towards the Ramanujan conjecture," Cheng utilized this generalized trace formula to establish a new proof of the $1/4$ bound (the Selberg-Kuznetsov bound) towards the Ramanujan conjecture for the trace of the cuspidal part in the ramified case [cite: 20, 22]. This proof utilized a sophisticated contour shift method and the Riemann-Lebesgue lemma on the spectral side, proving that Beyond Endoscopy can yield deep analytic bounds even in the presence of arbitrary finite ramification [cite: 20, 21].

### 2.3. Scaling to Higher Ranks: $GL(3, \mathbb{Q})$ 
Perhaps the most mathematically daunting generalization required by the Beyond Endoscopy program is scaling the trace formula manipulations from $GL(2)$ to groups of higher rank, such as $GL(n)$ for $n \ge 3$. In March 2026, Taiwang Deng and Malors Espinosa achieved a monumental milestone by publishing "Beyond Endoscopy for $GL(3, \mathbb{Q})$: Poisson Summation" [cite: 14, 23, 24].

The jump from $GL(2)$ to $GL(3)$ is non-trivial. For $GL(2)$, the regular elliptic elements are parameterized by characteristic polynomials of degree 2, which correspond directly to quadratic orders [cite: 12, 14]. For $GL(3)$, the characteristic polynomials define cubic orders. The arithmetic of cubic orders is substantially more complex, lacking the straightforward parameterization of quadratic fields [cite: 14].

Deng and Espinosa's framework was built on several key innovations:
1.  **Yun's Zeta Function:** To reformulate the regular elliptic part, the authors associated a specific zeta function—first studied by Zhiwei Yun—to these cubic orders, defined through their overorders [cite: 4, 14]. They proved a functional equation for the completion of this zeta function.
2.  **Approximate Functional Equation:** As in the $GL(2)$ case, they applied an approximate functional equation to this zeta function to rewrite the elliptic term into a form suitable for Poisson summation [cite: 14].
3.  **Periodicity and Moduli:** A critical arithmetic input was a newly proven periodicity theorem showing that the relevant coefficients depend only on the parameters modulo a finite modulus. This periodicity was the key that unlocked the ability to perform Poisson summation on the integral parameters indexed by the cubic data [cite: 14].
4.  **Local Kloosterman Sums:** After applying the Poisson summation formula, the resulting main terms on the dual side were governed by highly complex local Kloosterman-type sums and an associated double Dirichlet series [cite: 14]. Deng and Espinosa explicitly evaluated these Kloosterman sums for various local conditions (e.g., $(q, 6p)=1$, $q=p^k$, $p=2$, $p=3$) [cite: 14].
5.  **Isolation of Traces:** By evaluating this double Dirichlet series, they applied the residue theorem to find the trace of the trivial representation as a geometric residue. Furthermore, they recovered the contribution of the $GL(3)$ counterpart to the "special" representation (the representation obtained by inducing the trivial representation on the Borel subgroup of $GL(3)$) [cite: 14].

Deng and Espinosa’s work is the first instance of the Beyond Endoscopy Poisson summation strategy being successfully carried out for a group of rank greater than 1, proving that Langlands' vision is mathematically viable for higher-degree characteristic polynomials [cite: 14, 15].

---

## 3. The Kuznetsov Formula and Separation of the Residual Spectrum

While the ASTF approach has seen tremendous success in smoothing orbital integrals and isolating specific representations, the analytic difficulty of dealing with the non-tempered Arthur packets remains a formidable obstacle for general $GL(n)$ [cite: 10, 11]. Sarnak's early suggestion to use the Kuznetsov formula has been championed in the 2024-2026 timeframe by Yiannis Sakellaridis and Chen Wan [cite: 10, 25].

### 3.1. Circumventing Non-Tempered Packets
In the development of Beyond Endoscopy, a disproportionate amount of effort has focused on finding a geometric expression for the "Ramanujan" spectrum of the ASTF [cite: 10]. The Kuznetsov formula natively filters out representations that do not admit Whittaker models, effectively eliminating the non-tempered Arthur packets and the trivial representation from the spectral side [cite: 10, 12]. 

In a joint project spanning 2025 and 2026, Yiannis Sakellaridis (Johns Hopkins University) and Chen Wan (Rutgers University-Newark) undertook a direct, rigorous comparison between the Arthur-Selberg trace formula and the Kuznetsov formula for $GL(n)$ [cite: 10, 11]. The goal of this non-standard comparison of trace formulas is to map the spectral terms of one onto the other, identifying precisely how the geometric sides correspond [cite: 10]. 

### 3.2. Explicit Calculations of Transfer Operators
To formalize this comparison, Sakellaridis and Wan computed explicit "transfer operators" that isolate the non-Ramanujan spectrum in low rank [cite: 10]. 
*   **For $GL(2)$:** Their work served as a massive generalization of Zeev Rudnick's 1990 PhD thesis (which compared the simple Kuznetsov formula with the stable trace formula for holomorphic discrete series) [cite: 9, 10]. Sakellaridis and Wan demonstrated that for $GL(2)$, this transfer operator coincides perfectly with the Fourier transform on the affine parameter space of orbital integrals [cite: 10]. This is exactly the Fourier transform that appeared heuristically in the works of Frenkel-Langlands-Ngô and rigorously in Altuğ's work [cite: 9, 10]. 
*   **For $GL(n)$ ($n > 2$):** The researchers discovered that in higher rank, the transfer operator takes a fundamentally different and far more intricate form [cite: 10, 11]. It is no longer a simple Fourier transform on the Steinberg-Hitchin base, reflecting the deep geometric complexities of higher-rank orbital integrals and the combinatorial explosion of the non-tempered spectrum [cite: 10, 11].

This work establishes a rigorous bridge between the standard trace formula and relative trace formulas, verifying Sarnak's intuition. By understanding the exact geometric nature of these transfer operators, mathematicians can now extract the Ramanujan spectrum from the ASTF without having to manually smooth and sum the trivial representation's singularities [cite: 10, 11].

### 3.3. Implications for the Relative Langlands Program
Sakellaridis and Wan's research is heavily motivated by the **Relative Langlands Program**, a vast generalization of the Langlands program that deals with spherical varieties rather than just reductive groups [cite: 10, 15, 26]. 

In the Relative Langlands Program, non-standard comparisons of relative trace formulas are hypothesized to prove conjectural relationships between the periods of automorphic forms and special values of $L$-functions [cite: 10, 11]. By establishing the exact transfer operators between the ASTF and the Kuznetsov formula, Sakellaridis and Wan have provided a concrete template for how functorial transfer between spherical varieties can be executed, directly advancing the study of automorphic periods [cite: 10, 26].

---

## 4. Analytic Automorphic L-Functions and the Braverman-Kazhdan Program

Beyond Endoscopy is inextricably linked to the analytic properties of $L$-functions. Langlands' core insight was that to detect functoriality, $L$-functions must be introduced to weight the trace formula [cite: 27]. Therefore, understanding the functional equations and analytic continuation of general automorphic $L$-functions via geometric trace formula methods is a prerequisite for the program's success [cite: 15, 27].

### 4.1. Beyond-Endoscopic Treatments of Functional Equations
In January 2025, Chung-Hang Kwan and Wing Hong Leung published "Trace Formula and Functional Equation," presenting a fully "beyond-endoscopic" treatment of the functional equation for the standard $L$-function of a holomorphic cusp form with level and nebentypus [cite: 22]. 

Building on Akshay Venkatesh's thesis (which used the Kuznetsov formula to establish functoriality from tori to $GL_2$), Kwan and Leung utilized Petersson's formula and "spectral reciprocity" to derive functional equations [cite: 22, 27]. Their work is a prime example of using geometric sides of trace formulae to understand arithmetic invariants—specifically root numbers—of $L$-functions [cite: 22]. By avoiding standard Rankin-Selberg or Langlands-Shahidi methods, this approach proves that trace formula comparisons contain all the necessary analytic data to continue $L$-functions, fulfilling a major theoretical requirement of Beyond Endoscopy [cite: 22, 27].

### 4.2. Connections to Braverman and Kazhdan
Around the same time Langlands proposed Beyond Endoscopy (c. 2000), Alexander Braverman and David Kazhdan initiated a program to generalize the Godement-Jacquet proof of the functional equation to arbitrary Langlands $L$-functions using non-standard test functions and generalized Fourier transforms [cite: 15, 25, 26]. 

The 2024-2026 period has seen a synthesis of the Braverman-Kazhdan program and Beyond Endoscopy [cite: 15, 26]. Recent works have derived Kuznetsov-type trace formulas incorporating these non-standard Godement-Jacquet sections [cite: 27]. In this framework, the Poisson summation formula naturally yields the functional equation for the standard $L$-functions of $GL(2)$ [cite: 27]. As discussed by Freydoon Shahidi and others in recent workshops, intertwining operators can be normalized to act as Fourier-like transforms, and the theory of Eisenstein series provides the exact analogue of the Poisson summation formula required by Frenkel, Langlands, and Ngô [cite: 26].

---

## 5. The Global Academic Community and Future Trajectories (2024-2026)

The explosion of results in Beyond Endoscopy between 2024 and 2026 is reflected in the intense concentration of high-level academic conferences dedicated to the topic. 

### 5.1. Key Conferences and Working Groups
*   **The Fields Institute (August 2025):** A major international conference titled "Trace Formula, Endoscopic Classification and Beyond: the Mathematical Legacy of James Arthur" is scheduled to take place at the Fields Institute in Toronto [cite: 28, 29]. This conference directly addresses the transition from Arthur's endoscopic classification of classical groups to the Beyond Endoscopy techniques required for general functoriality [cite: 28]. Key presentations include Sakellaridis on the Kuznetsov comparison [cite: 10].
*   **Aarhus Automorphic Forms Summer School and Conference (August 2025):** Hosted at Aarhus University, Denmark, this two-part event features a specialized summer school on Galois Representations, Relative Langlands Duality, Beyond Endoscopy, and Relative Trace Formulae [cite: 29, 30]. 
*   **AMS Special Sessions (March 2026):** The American Mathematical Society's Spring 2026 meeting features a dedicated Special Session on Automorphic Forms, where leading researchers like Yiannis Sakellaridis and Chen Wan are slated to present their findings on transfer operators and the Ramanujan spectrum [cite: 11].
*   **BIMSA Conferences (Beijing):** The Beijing Institute of Mathematical Sciences and Applications (BIMSA), home to researchers like Taiwang Deng, has hosted continuous working groups on representation-theoretic and analytic foundations of the Langlands correspondence, specifically targeting trace formulas and $L$-functions [cite: 23, 31].

### 5.2. Future Directions and Limitations
Despite the monumental breakthroughs in $GL(2)$ and $GL(3)$, the Beyond Endoscopy program faces significant challenges before general functoriality can be proven:
1.  **Arbitrary Rank $GL(n)$:** Deng and Espinosa's methodology for $GL(3)$ relies heavily on the specific properties of cubic orders and Yun's zeta function [cite: 14]. Generalizing this to $GL(n)$ requires an understanding of degree-$n$ orders and generalized zeta functions whose analytic properties are currently deeply mysterious [cite: 14]. 
2.  **The "Transfer Operator" Complexity:** As shown by Sakellaridis and Wan, the transfer operator that bridges the Kuznetsov and Arthur-Selberg trace formulas becomes non-linear and highly complex for higher ranks [cite: 10, 11]. Mapping these operators for arbitrary reductive groups will require new geometric insights into the moduli space of bundles and the Hitchin fibration [cite: 1, 11].
3.  **Limits of the Geometric Trace Formula:** The ultimate goal of taking the limit of the weighted trace formula (e.g., $\lim_{s \to 1} \sum \dots$) to isolate poles requires absolute bounds on error terms that are currently at the edge of analytic number theory's capabilities [cite: 4, 12]. 

---

## 6. Conclusion

The 2024-2026 period represents a golden era for the Beyond Endoscopy program. Moving far beyond the theoretical heuristics proposed by Langlands, Frenkel, and Ngô, mathematicians have developed the rigorous analytic and algebraic tools necessary to execute the program. 

The successful generalization of Poisson summation techniques to ramified fields by Yuhao Cheng [cite: 16, 20], totally real number fields by Emory et al. [cite: 2, 17], and to $GL(3, \mathbb{Q})$ by Deng and Espinosa [cite: 14] proves that the geometric side of the trace formula can be successfully manipulated to isolate specific automorphic data. Concurrently, the rigorous comparison between the Arthur-Selberg trace formula and the Kuznetsov relative trace formula by Sakellaridis and Wan [cite: 10, 11] has validated Peter Sarnak's early intuition, offering a viable path around the intractable non-tempered spectrum.

As the program becomes increasingly intertwined with the Braverman-Kazhdan program and the Relative Langlands program, Beyond Endoscopy is no longer just a hypothetical strategy for proving functoriality; it has matured into a robust, active subfield of mathematics. While the complete proof of Langlands Functoriality remains on the horizon, the mathematical machinery built between 2024 and 2026 guarantees that the trace formula will continue to unveil the deep, hidden symmetries between geometry and number theory.

**Sources:**
1. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmZ67w-AKWW8_KgUE0Qv1TsvYXWVtImqLRj-2KMrOzWMPIZTjnU2Sp-6kMRUm1d9aMSRRa2PH8z1WJAWxLOIeyRrTjDE3Mld0ZwH4xrM93FzwIgWW-lrPwMCTp9k3rYE-DDM3Bh5k=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzGDpFNS1DZfReIHX9hWT0pIi-VIcwE2WcMM98LVITIHDyaCrU9OApS6GRFXGr5V53oWxL_M6321hIq3hzSxkn5bNbChfB8kL8RoqQ-RJ-qoe6AN17Mg==)
3. [jhu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWdg06ssLlXaFqKxw_6BQ-Ex5QneeDVid6XJSjGAdtagrrfKSc96hjYMhRQXuWkd_hUvip4IAMFYKQHYgBwe-zWYEoa_pCbRQGLF9hXlQ2z1R2GwxS4OTHQbKTnV0XVA==)
4. [bimsa.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-MfNTloZkhemtiOo6s_4e9yJZ2vb2M5GWCAt-LnXsN0khZ_n4Ma842AhP7auIXVIE7RbezEE9jIW0J1dVyp001TfwWQuvhugNWEpCU97iwK0fWn9yWfh1T3fFR2LQJ1vF)
5. [duke.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBxocnnvlovWuEcVw27-VM-UzUvoIr0vDF27oEnv0POwfRH9K46kFeyYTURXQRpXJ2tFclLSY8G2uy6iZ3Z-BE-5gx7tnXctPJf8XZNfoj99Po5aI10qBFKSgLoFhLGxFSoOtSV3JUoDkqY0SiAzNzBYkCZXhpYoeYyDE4P8XwqE_TryQ=)
6. [lsu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqX2HKOFWubSMQG7___n8gypdh-2Tk33HIwy3_9Dr8yYWH9xnGbueUEV1Ipa4UjRN7KW6-Z40MZh42BiNqRhYISEwWn4r2O5wGh5HosbAb-Nqx0ZSlI8HkblGAGoO8ZYvmsnHdoclutfo_La7rlCXOGHGmnWqECqbu)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEE_2nqhOEniJOlFW4MF-FcwK7plv5dVHnk_z5wYBpKRQUGq01EES16Alg-QDwPDBjTF1Z0-fdcC20uggzh7G3iCE9S9zIFXkViFh4JZy17ZUdub8i7dA==)
8. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsA-pF2lHbFWSYW3w9lQYFKap8XqvRHdUyTbTezDA5DMHzQByHqKja_3osQkBY4zYVZ1Qqygi28q8oT4wbgfAUaVNUfrFXgLcHVNbzDVIeXs6jnTYv1Kp5kQWBt0P9Hc6ljJLX6OV2DJpORKRnsNs62FAjoWsN1EbKUZFxBSbCEuUySx3ifUwCQQIp6QYKEmVmiLv5zyuFCSYDO-8L-B_-aPCUuctxMpIMqQvujRVtJrd92bbRGsqBPr3xcRyD0rj9G6ejst5h1yjPv9mtdkOskeb41VRcyPo28vrDoJN3or6mj07Dg27DG1vKuVxi6mcT9IedtGaxk9WRvK00A40O9A8=)
9. [cirm-math.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3wcbJ7NGriVMLHbrYtwn80dvHltOZsJZqd10514UzZQvjNKseRlDUVDsPaCghQXIpMy51BDfowywrddhwrPUte4RUBFJHhE5HDXVNz0LIBL4NKvOaVfwg2s7E3lIzMfTzLaOd3RSh6z-w8A8DpWGAqZV8)
10. [utoronto.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfq4Zm0j40B_E3bZtq_DD9fryBfe8ukmGYv8ZBG0mKGH-iEcDFUZdR1n8OIbFCD5_mWXOojKo-u4YS-Yl7kXT8grTY67d9zg5i3bKx6-A5KgOsA3huX6IDlx3ievZYrzF0bJkgDEerB_8kclQOog8uldRz7xtlE8xB--EX5C-cB-ng_X703DOWueQhcLzsN1ilNgLIiYqEwanrCKXKI7e5pLouXwNXW8xl)
11. [ams.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXQIPLw574t2pVYKNbgXOgRsJtyanIxSaaaqLHMkKcSzylcjVKSLY8TKSXBs3B3Xs8jJnqhT7FvahZclJFHK55w4JzI57vIqlTGSqO-g_m_f6wHQJwaSCOWJjS1-o5D2YCUHBmwQ9NYnTxr9P7XaAxMBuStVaaf9onvA==)
12. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_hFQvxP6xEHToQxmCpZbSNpsRNCgQD7uDm74G7xdsl2R9oYh6i4Jaipuoya480u739M8-rpC5mY1wQjmqPDvSp7jQNPckZYQD2Ic3ZJdBJFgiKmM3RH_kE5HWOVvF6Lx7vf-vDck=)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgC8TDQXrWDCqt9ZA3Djbz3ZSQIi9P70Am5_hy5xd5lTAjHafr8iVzTfYNkp64nRd_FUYClNZMPzT1aMYNDVgwHBYsn5HnKZb9srI3fwgTgcBXzXctEQ==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZQVIpD7oRrn-GsFkAtKshTOixOC-1MGvZSBjVn0iSLY5RIYHGNwJtEYthWtPNEKPh7S55ZNQMoO2p-AxwlPM9t4rLCP--rdZpL4HKbtExg7uurRPKPA==)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpZfIbp25KaMv954tt9pmlNJuzLVDG05ILwaVWqGFgtQkyAw7SoicbChwUqFTKdB50uQYQ7NJByJ_DJQU0-w1nsv5XWDnq3pyY3Zxy8zOuM6TUpI_B8X5JPTMXOUdNvvNmbfdQXnH3nnooJVCV0cczm5e5oayapQaiFvUsxcUzG7y9bPnw9Gk1mTHc7L-eNADAsMTHqjEFm8TvCbnOieVr5OrSZUWX7LmGEdxLLALLdPl8Rie15AO9bazVJFKNYrbLatYTqlYyUatlCR6NTX0X8A==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHG4EZF2VOcB6qYQv4ECRshHQKCPQ00fKbXVPkEoBBCfR1qhKSvCNWYF-h7Dbw1mJOebOcKtgrDGaRymiKvs8JNkjHpxZKt22uRQ7fnx_KYs9xQ5TlrZA==)
17. [math.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqqjwYL_TfPtkOXj-Tm5KjzzIx038kCsKcpIOn4Ft5b55YuoP3eR3KCXjfPegLezpzHVBvCepMEv_0MnY2gXsGeUrWAYkET2DWZjPdbWUCAWJ6cZsLkvvK2H2Mk6cgP-ITtN6HXl4Zped7-3Rh1A_j)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEVI2ZMdFNX1oaX8fNR6Dguy-uKOIMCz_nZlfnp8R2_v-a6sSlRL9GEzzF0rPVP9krEE08wy_VlELWjD-gaaqht5y7dUkloSDMHO2Kznabx7i3tDhp5t6mNPDOvLPR06gzoUb2Abv9S1HSMBZUpd1pWcBlfMoIDpiXNjDhhiNq-NdL6fWinCw1MxIqlw==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG51ajrJYN3VeapQFTjzgv2RwOEwtYa---6k2at8ytDOHDKNq6J9lnuc0we3OTqplS3FCqCRdNRSG4wjELIK-GmTvzBYkUaoRQ2DQoh5BtNVm6KSQRi23FPQQ==)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEHCUqhb8shDb66Ho9ABjhGBgpyjZnpdkz8bExl4sXR6jkWiMdBSivTGTQ-pQahQ3gfdaE4-vgosCMCuoFJDY_USX7Hclt4Qpvk81KIxe9ic10IObQHBjP4eFtiJ1NubPnOl9GSQuwZsl2RuK7mxt26kBgDwBdQHuZZTrS7zTmuMQpWAeX8GzAxC7y_W1N27nJ2riqrrcMVVEpYus35rZyh7WZDUTTzAHsySeVlcGxZS3v6mi7FQOMGUlpHRI3gNZGJO1urakwFZVdzjbkxP2hs38=)
21. [papers.cool](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFB6iP99Nax_NpLg5GGuQAbkE8Zz4ShZuLt5fl9w7YwVwQGSkKOsuFrtRMxgjODJg3riCjxakGLC-jkaM4XMkxN6S4C8mV96IZMGlpJ9sYOhhTnoqv6M-Q=)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5i1F3Oxki26xPLB1wtbVgLnh0IsynJWdxsvf4mN0U8Y54g6ihM9o3ow1vgMTuAqcwK4yOTlX0NkP7fsJINMAoNeAYdtXFPjlufh6i4li8db7q6ljHfw==)
23. [bimsa.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6gqUc48Uz0wKEXt7Nktxt3B57VHpvXV3uFbU70NN2SQhnHr52ZJlwrfFQqB4fksBrhOByw-NIZZJuA3zwUPzeS7aW1Fg_ngMZraZ2FIh0oLSQpu0E4VFvQWvLY2A=)
24. [bimsa.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEASwB28qZIEm52wCJg2mZbw_N5G8LblajVpsN0fb5nCsqJyH3CajrKl_FyZlnTC7ZcTWuPWvjd5vP9c9AebtXfAHdKo_e28ADHeAR2P_1wlnzSr6tpew==)
25. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoT9CxaGdPSNW4aYT-GUjTL3NWQrj7SP6E_6K7fJA8T8ytaq11tDX7bGt6KjdXMGzbyPMTD3bbW4xdtMIi3Cr1jPkGo_N2fCNYqa_wWIaIccDACehB1F2xkTeBtqQj1XNzCuMNnDGcWAHkE95R9yx8q4CKXLn09v286K-I0g5sP3In)
26. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-RieAWv-cD9QMlGpcSP0858IiErlpuBiZ-EaCrzUE3PIdYSeAxQ8VIw3s1syQ77tQAViE93_aWTf-zAL3uBMQzH0juYEsWMn1QrTtJK3wa-rfDoxTFsJ5Cdzbq9Zzuet6-GSv_tXA3J1Z2IYQ)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIdXCY-rUM9dW0zv9iZzeD9LOSdJuBK9eHctCewXBO39JuJFCeGXawsx5hTdaRcKrJ2DX_iCb-rcFqFL_tFeij-F5eHbyv-c4grZYBhzX27HdrXjesbg==)
28. [utoronto.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFU0Wb1o4vd38cKeGYima1GSLXKnz81e0Ccutlrk1rmKsStENHflKeyWkg3tGYX9pFK5U1E6YjzdN5KORKNIpwec34HVZdJ-xm5-QfdLO3k4wZDhTU_mzypaYN3h4ZunXgb8NncB_Dm0Dumuw==)
29. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNJ6MgIMrruzXH3JPYE5YCrq-Xv_221RHjSozb-NFO4gJ-pdDcbm2xKl8yYozDxm5EBXR65lx_q7s7df3fF6K6KciN7NHXIMbSY7CIyQ7mAB0CLJ8S7txNthApTpxYVClkPJALkaIruz9RFKBLkCB6M2QV)
30. [numbertheory.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbJU_voXx-O1MwcMPYUDQ455D-wOF50AVKkhxAzYgeSwNf8jv1qKs7e_shHD-VC2buA24W3ykIOO3siL0xp_SNJ24sNXOAQiaE2vv-Q5DNU1XUYxdLyrvzjohn5Sk=)
31. [bimsa.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsnAlkRLtfP8-LvKr3ZNZTcyMx5CzwQ-UzWuAy7FMhtf9UkUYF7whl4nVPbSihncNCC1wP3N9HwXlKokJyI-BuEL42g4iStzjFBlWXtSICc-86uNbz-WyyhKTxZPhUruC15xeu)

