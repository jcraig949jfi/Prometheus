# Followup [FU-2026-05-22-040 <- row245]: # Stygian Attack Plan: Target BL-C-008 (Vinogradov Mean Value Adjacent)  ### Key Points *   **The Or

**Pythia queue id:** 325
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdVTHNQYXM3TUJQWFVqTWNQa0xxRXdBaxIXVUxzUGFzN01CUFhVak1jUGtMcUV3QWs
**Elapsed:** 249s
**Completed at:** 2026-05-22T02:15:38.316832+00:00

---

# Status Update: Finite Field Analogues of the Quadratic Vinogradov Mean Value Theorem

**Key Points**
*   Research confirms that the original Main Conjecture of the Vinogradov Mean Value Theorem (VMVT) is definitively solved; Bourgain, Demeter, and Guth achieved this via $l^2$ decoupling, while Wooley resolved it via efficient congruencing.
*   It seems likely that the current frontier has completely shifted away from the continuous and integer Main Conjecture toward adjacent, highly constrained extensions, most notably the **finite field analogue** for sparse sets.
*   The finite field analogue replaces classical Fourier decoupling with incidence geometry; the latest breakthrough by Mansfield and Mudgal (2024) achieves a fractional exponent savings of $1/9$ for the quadratic case, proving $J_s(A) \ll |A|^{2s - 2 - 1/9}$.
*   The evidence leans toward the theoretical optimum bound of $|A|^\epsilon$ remaining an open question, bottlenecked by the limitations of current point-line and point-hyperbolae incidence bounds over $\mathbb{F}_p$.
*   Automated models frequently hallucinate the status of VMVT by conflating these highly specific, open finite field extensions with the fully resolved foundational theorem.

**Context and Overview**
The classical Vinogradov Mean Value Theorem, initially formulated in 1935, concerns the number of solutions to a specific system of Diophantine equations bounded by a parameter $N$. For decades, the "Main Conjecture" regarding the optimal upper bound of these solutions remained one of the most prominent open problems in analytic number theory. Following its simultaneous and independent resolution in the mid-2010s by entirely different methods (Fourier decoupling and efficient congruencing), the mathematical community redirected its focus toward structural generalizations. 

One of the most mathematically fertile generalizations restricts the variables to sparse subsets of finite fields $\mathbb{F}_p$. In this discrete algebraic setting, the powerful continuous tools of wave-packet decomposition and multilinear Kakeya inequalities fail. Instead, researchers must rely on entirely different methodologies rooted in additive combinatorics and incidence geometry. This report provides a substrate-grade analysis of the finite field analogue to the quadratic VMVT, interrogating the recent primary literature, current bounds, and the theoretical attack vectors actively deployed to close the gap toward the optimal $|A|^\epsilon$ bound.

***

## 1. Brief Summary

The open question regarding the finite field analogue to the quadratic Vinogradov Mean Value Theorem investigates the optimal exponent savings for solutions to quadratic systems over sparse subsets of $\mathbb{F}_p$, where the target bound of an $|A|^\epsilon$ loss remains unproven despite recent fractional advances using combinatorial incidence geometry [cite: 1, 2].

## 2. Flagged Findings

### 2.1 The Current Consensus
The primary literature universally acknowledges that the original Main Conjecture of the Vinogradov Mean Value Theorem is solved [cite: 3, 4]. It was proven independently in 2016 through two vastly different mathematical pipelines:
1.  **$l^2$ Decoupling:** Pioneered by Bourgain, Demeter, and Guth, utilizing multilinear Kakeya-type theorems and wave packet decomposition over $\mathbb{R}^n$ [cite: 3, 4].
2.  **Efficient Congruencing:** Developed by Wooley, relying strictly on $p$-adic analysis and number-theoretic modular arithmetic [cite: 5].

Because this original conjecture is settled, the current consensus identifies the active frontier as existing in generalized, adjacent domains—specifically, continuous diameter-free estimates for sparse subsets, and algebraic analogues over finite fields $\mathbb{F}_p$ [cite: 1, 6]. In the finite field setting, standard Fourier analytic techniques yield optimal power savings only for dense sets (e.g., when $|A| > p^{1/2}$), while they fail to produce non-trivial power savings in the sparse regime ($|A| \ll p^{1/2}$) [cite: 2]. Consequently, the consensus dictates that progress in the sparse finite field regime strictly requires additive combinatorics and geometric incidence bounds [cite: 1, 2].

### 2.2 Artificial Intelligence Hallucinations and Calibration Errors
When tracking the status of this highly specific mathematical problem, artificial intelligence models and automated literature reviews routinely exhibit catastrophic categorization errors. We flag two specific algorithmic failure modes that require immediate manual override in mathematical literature review pipelines:

*   **PATTERN_BASE_RATE_NEGLECT:** Modern automated summaries frequently exhibit **PATTERN_BASE_RATE_NEGLECT** by analyzing 2024–2026 preprints with titles containing "Vinogradov Mean Value Theorem" and falsely concluding that the overarching theorem remains unproven. The models fail to integrate the historical base rate—that a nearly century-old conjecture was definitively closed in 2016. They misinterpret contemporary attempts to solve the *finite field analogue* as evidence that the *original continuous conjecture* is still open.
*   **PATTERN_VRAM_TRUNCATION_ARTIFACT:** Furthermore, when attempting to synthesize the methodologies used to attack these problems, LLMs display **PATTERN_VRAM_TRUNCATION_ARTIFACT**. The context relating to Bourgain-Demeter-Guth's continuous $l^2$ decoupling over $\mathbb{R}^d$ is erroneously truncated, stripped of its spatial parameters, and incorrectly mapped into explanations of discrete $\mathbb{F}_p$ contexts. This conflates continuous analytical wave-packet methods with discrete combinatorial point-line incidence methods, creating mathematically nonsensical attack vectors. 

### 2.3 Where the Consensus Might Be Wrong
The consensus asserts that achieving the conjectural optimal bound of a purely $|A|^\epsilon$ loss in the finite field setting is a matter of optimizing current incidence geometry techniques (such as bounds on modular hyperbolae). However, the assumption that Szemerédi-Trotter-type bounds can be incrementally pushed to yield arbitrary $|A|^\epsilon$ savings may be fundamentally flawed. Geometric incidences over positive characteristic fields possess algebraic obstacles (like subfield obstructions and Frobenius morphisms) that do not exist over $\mathbb{R}$. It is highly possible that a phase transition exists, whereby current combinatorial methods will asymptote at a hard fractional exponent (e.g., bounds stopping at $1/7$ or $1/6$) and completely new algebraic geometry tools will be required to cross the threshold to $|A|^\epsilon$.

## 3. Problem Statement

### 3.1 The Original Vinogradov System
To precisely interrogate the finite field analogue, we must first mathematically define the object in its classical context. Given $s, k \in \mathbb{N}$ and a finite set $A \subseteq \mathbb{Z}$, analytic number theorists seek to count the number of solutions, denoted $J_{s,k}(A)$, to the system of $k$ symmetric Diophantine equations:
\[ \sum_{i=1}^s (x_i^j - y_i^j) = 0 \quad \text{for } 1 \leq j \leq k \]
where all $x_1, \dots, x_s, y_1, \dots, y_s \in A$ [cite: 1, 2].
In the classical setting, $A = \{1, 2, \dots, N\}$. The Main Conjecture, now a theorem [cite: 4], states that for all $\epsilon > 0$,
\[ J_{s,k}(\{1, \dots, N\}) \ll_{s,k,\epsilon} N^\epsilon (N^s + N^{2s - k(k+1)/2}) \]
The exponent $2s - k(k+1)/2$ represents the theoretical ideal limit where the variables are constrained only by the degrees of the manifold [cite: 1].

### 3.2 The Finite Field Analogue ($J_s(A)$ over $\mathbb{F}_p$)
The object being interrogated in the current open problem is the exact analogue of this system, translated to a finite algebraic field. Let $p$ be a prime, and let $A \subseteq \mathbb{F}_p$ be a non-empty finite set. We restrict our focus to the **quadratic** case ($k=2$). We define $J_s(A)$ as the number of solutions to the simultaneous system of equations:
\[ \sum_{i=1}^s (x_i - x_{i+s}) = 0 \]
\[ \sum_{i=1}^s (x_i^2 - x_{i+s}^2) = 0 \]
where $x_1, \dots, x_{2s} \in A$ [cite: 7].

### 3.3 The Optimal Bound Conjecture
By trivial combinatorial limits, $J_s(A)$ has a maximum possible value of $|A|^{2s}$. Elementary considerations regarding diagonal solutions establish a trivial lower bound of $|A|^s$, and non-diagonal continuous symmetries suggest an expected threshold. The open problem seeks to prove that for any arbitrary sparse set $A \subseteq \mathbb{F}_p$, the number of solutions respects an upper bound equivalent to the continuous Main Conjecture:
\[ J_s(A) \ll_{s,\epsilon} |A|^\epsilon (|A|^s + |A|^{2s - 3}) \]
For large $s \geq 3$, the dominating term is $|A|^{2s - 3}$. Thus, the conjectural optimal bound for the finite field quadratic VMVT aims to prove power savings that push the exponent down from the trivial $|A|^{2s-2}$ to exactly $|A|^{2s - 3}$, modulo an $\epsilon$ loss. Currently, no mathematical framework has proven this exact threshold for generic sparse sets over $\mathbb{F}_p$ [cite: 1, 2].

## 4. Status & Bounds

The pursuit of the optimal bound is heavily contingent on the density of the set $A$ relative to the characteristic $p$ of the field. The status of the problem fractures into two distinct regimes: the dense regime (largely resolved via Fourier methods) and the sparse regime (the active frontier).

### 4.1 The Dense Regime ($|A| \gg p^{1/2}$)
When the cardinality of $A$ is large relative to the field size, standard methods from analytic number theory and additive combinatorics—specifically Fourier analysis over finite groups—are highly effective. 
As proven in recent literature, for any integer $s \geq 3$ and any non-empty set $A \subseteq \mathbb{F}_p$, the number of solutions is bounded by:
\[ J_s(A) \ll_s \frac{|A|^{2s-1}}{p} + |A|^{2s-2} p (\log|A|)^{2s} \]
When the set $A$ is sufficiently dense, specifically when $|A| \gg p^{1/2 + 1/(4s-6)} (\log p)^{c}$, this bound matches the theoretical optimum up to multiplicative constants [cite: 2]. Because classical exponential sums and Gauss sum bounds naturally capture the cancellation in dense subsets of $\mathbb{F}_p$, the problem is not considered open in this domain.

### 4.2 The Sparse Regime ($|A| \ll p^{1/2}$) - The Open Frontier
The difficulty strictly emerges when $A$ is sparse, i.e., $|A| \ll p^{1/2}$. In this regime, the Fourier-analytic error terms (the $p$ in the numerator) overpower the main term, rendering continuous decoupling and classical discrete Fourier restrictions useless; they fail to provide any non-trivial power savings beyond the trivial bound of $|A|^{2s-2}$ [cite: 1, 2].

**Current Best Known Bounds:**
The most advanced status of this problem was published by Sam Mansfield and Akshat Mudgal in 2024 (Quarterly Journal of Mathematics) [cite: 2, 8]. By pivoting entirely away from Fourier analysis and deploying combinatorial geometric estimates, they broke the trivial barrier to achieve a fractional exponent savings.

*   **For $s \geq 3$:** The last known status proves:
    \[ J_s(A) \ll |A|^{2s - 2 - 1/9} \]
    This establishes an unconditional power savings of $1/9$ against the trivial bound, standing as the strongest finite field analogue to the quadratic VMVT for arbitrary sparse sets [cite: 7].

*   **For higher dimensions ($s \geq 4$):** Mansfield and Mudgal provide slightly better exponents for larger $s$, at the cost of restricting to even sparser sets. The conditional bound is given by:
    \[ J_s(A) \ll_s |A|^{2s - 2 - 1/7 + \eta_s} \]
    where the modifier $\eta_s$ is defined precisely as $\eta_s = (4/11)^{s-3} \cdot (2/63)$ [cite: 2]. 

*   **Continuous Diameter-Free Comparison:** For context, in the continuous setting (where $A \subset \mathbb{R}$), Mudgal independently achieved "diameter-free" estimates for the quadratic VMVT. In 2023, he established that $E_{s,2}(A) \ll_{d,s} |A|^{2s - 3 + \eta'_s}$ (where $\eta'_3 = 1/2$, and $\eta'_s \to 0$ as $s$ grows) [cite: 6, 9]. This highlights that the continuous sparse problem is remarkably closer to the $2s-3$ optimal bound than the finite field sparse problem, underscoring the severe algebraic obstructions inherent in $\mathbb{F}_p$.

## 5. Literature (Primary Sources)

The body of primary literature defining the current state-of-the-art for this problem is highly concentrated among a few authors actively bridging additive combinatorics with incidence geometry.

### 5.1 Foundational Resolutions of the Main Conjecture
While not the finite field analogue, these papers form the mandatory theoretical baseline:
*   **Bourgain, J., Demeter, C., & Guth, L. (2016).** *Proof of the main conjecture in Vinogradov's Mean Value Theorem for degrees higher than three.* Annals of Mathematics, 184(2), 633-682. **arXiv:1512.01565**.
    *Significance:* Resolved the original VMVT utilizing $l^2$ decoupling and multilinear Kakeya-type theorems [cite: 3, 4].
*   **Wooley, T. D. (2012 / 2016).** *The cubic case of the main conjecture in Vinogradov's mean value theorem.* Advances in Mathematics, 294, 532-561. 
    *Significance:* Independent proof of VMVT via efficient congruencing, establishing $p$-adic attack vectors [cite: 10].

### 5.2 The Finite Field Breakthroughs
The specific open question is documented and advanced in the following primary sources:
*   **Mansfield, S., & Mudgal, A. (July 2024).** *A quadratic Vinogradov mean value theorem in finite fields.* The Quarterly Journal of Mathematics, 75(3), 1007–1029. **arXiv:2310.02950** (Submitted Oct 2023). [cite: 1, 7].
    *Significance:* The principal source for the current state-of-the-art bounds. Introduces the $1/9$ exponent savings using incidences between Cartesian products and modular hyperbolae [cite: 1].
*   **Mudgal, A. (2023).** *Diameter free estimates for the quadratic Vinogradov mean value theorem.* Proceedings of the London Mathematical Society (3), 126(1), 76-128. **arXiv:2008.09247**. [cite: 6, 9, 11].
    *Significance:* Establishes parallel bounds in $\mathbb{R}$ that do not rely on spatial decoupling, providing the theoretical bridge to combinatorial methods that bypass structural diameter constraints [cite: 6].
*   **Mansfield, S., & Mudgal, A. (2024, related presentation).** *Geometric and arithmetic structure in finite point sets.* (Thesis/Presentations referencing the squeezing method and incidence geometry bounds for Möbius hyperbolae) [cite: 12].

### 5.3 Related Incidence and Sum-Product Foundations
*   **Roche-Newton, O., et al. (2024).** *A better than 3/2 exponent for iterated sums and products over $\mathbb{R}$.* Mathematical Proceedings of the Cambridge Philosophical Society [cite: 8].
    *Significance:* Provides the underlying energy estimate frameworks (e.g., bounds on $E_s(A, B)$) and Szemerédi-Trotter applications that Mansfield and Mudgal successfully adapted to the $\mathbb{F}_p$ setting.
*   **Mudgal, A. (2024).** *An Elekes-Rónyai theorem for sets with few products.* International Mathematics Research Notices, 2024(13), 10410-10424. [cite: 11, 13].
    *Significance:* Highlights the translation of incidence geometry constraints (like non-degenerate polynomial expansions) into algebraic fields [cite: 13].

## 6. Attack Vectors

The methodology for attacking the finite field VMVT represents a radical departure from the classical continuous theorem. The shift from analysis to combinatorics is absolute.

### 6.1 Exhausted and Ineffective Approaches
Before detailing live vectors, it is crucial to understand why standard tools fail, mapping the boundaries of the problem space:
*   **Continuous Fourier Decoupling ($l^2$ Decoupling):** The Bourgain-Demeter-Guth pipeline relies on wave-packet decomposition and the partitioning of parabolas into $\delta$-caps [cite: 3, 4]. It uses multilinear Kakeya bounds to estimate how spatial "tubes" or "plates" intersect in $\mathbb{R}^n$. In a finite field, particularly for a sparse subset $A$, there is no natural topology or metric that permits $\delta$-scaling. The spatial geometry of tubes intersecting transversally does not map to $\mathbb{F}_p$ without severe dimensional collapse.
*   **Classical Weyl Differencing and Efficient Congruencing:** While efficient congruencing succeeds for the integers by leveraging the density of primes and $p$-adic metrics, sparse arbitrary sets $A \subseteq \mathbb{F}_p$ lack the required arithmetic structure (like intervals or complete residue systems) necessary to execute the nested congruencing iterations [cite: 5].
*   **Standard Exponential / Gauss Sums:** As shown in Section 4.1, evaluating $J_s(A)$ via indicator functions $\mathbb{1}_A$ and applying Plancherel's identity yields bounds dominated by the field size $p$. When $|A| \ll p^{1/2}$, the error term expands beyond the trivial combinatorial bound $|A|^{2s-2}$, rendering the technique inert [cite: 2].

### 6.2 Live Attack Vectors: Incidence Geometry
The current dominant attack vector, which successfully extracted the $1/9$ exponent savings, is **Combinatorial Incidence Geometry**. The strategy reformulates the algebraic equations of the Vinogradov system into geometric intersections in $\mathbb{F}_p \times \mathbb{F}_p$.

**Step 1: Reformulation into Hyperbolae**
To bound $J_3(A)$, one fixes variables to reduce the degrees of freedom. Let $m, n \in \mathbb{F}_p$. The quadratic constraints of the Vinogradov system can be algebraically manipulated to represent coordinates intersecting a specific family of modular hyperbolae [cite: 1, 2].
Specifically, pairs of elements $(x,y) \in A \times A$ are mapped to hyperbolae defined by the equation:
\[ (m - x)(m - y) = \frac{m^2 - n}{2} \]
Let $h_{m,n}$ denote this hyperbola. The quantity of solutions $J_3(A)$ is mathematically bounded by counting the number of geometric incidences between the point set $A \times A$ and the family of curves $h_{m,n}$ [cite: 2].

**Step 2: Finite Field Incidence Bounds**
In the continuous plane $\mathbb{R}^2$, point-line and point-curve incidences are tightly bounded by the Szemerédi-Trotter theorem, which states that $I(P, L) \ll |P|^{2/3}|L|^{2/3} + |P| + |L|$ [cite: 8, 14]. 
Over $\mathbb{F}_p$, Szemerédi-Trotter fails globally because lines can contain up to $p$ points. However, local finite-field incidence bounds (such as those pioneered by Stevens and de Zeeuw) allow one to bound incidences provided the sets of points and lines (or curves) are sufficiently small relative to the field characteristic (precisely why the condition $|A| \ll p^{1/2}$ is mandated).
By employing these modified combinatorial bounds on the Cartesian product $A \times A$ and the specialized family of modular hyperbolae, Mansfield and Mudgal constrained the maximum number of times the curves can intersect the variables, capping the solution count [cite: 2].

**Step 3: Plünnecke-Ruzsa and Higher Energies**
To extend the bounds from $J_3(A)$ to higher dimensions ($J_s(A)$ for $s \geq 4$), the attack utilizes the **Plünnecke-Ruzsa inequality** and higher additive energy metrics [cite: 1, 2]. The Plünnecke-Ruzsa inequality dictates that if a set has a small doubling constant (i.e., $|A+A| \leq K|A|$), its multi-fold iterated sumsets ($|sA|$) remain strictly bounded [cite: 1]. 
By treating the Vinogradov solutions as an expression of additive and quadratic energy, researchers construct a bootstrapping mechanism: the incidence bounds on $J_3$ serve as a base case, and structural graph-theoretic arguments limit the expansion for larger $s$, yielding the $(2/63)$ decay modifiers for higher $s$ [cite: 2].

### 6.3 Future Avenues toward $|A|^\epsilon$
To push the bounds from $1/9$ to the optimal $|A|^\epsilon$, the live attack vectors must undergo a paradigm shift:
1.  **Bypassing the Cartesian Product limitation:** Current incidence bounds fundamentally rely on the Cartesian product $A \times A$. The $2/3$ exponents inherent in Szemerédi-Trotter variants cap the extraction of power savings. Breaking this requires new incidence theorems over $\mathbb{F}_p$ that do not require Cartesian structure.
2.  **Möbius Transformations and Rigidity:** The hyperbolae $(m-x)(m-y) = c$ can be analyzed as actions of the Möbius group $PGL_2(\mathbb{F}_p)$. Future vectors involve studying the growth of sets under the action of non-commutative finite groups [cite: 2], directly translating the quadratic constraints into matrix-commutativity problems [cite: 11, 15].

## 7. Cross-References

The finite field quadratic VMVT does not exist in isolation; it is deeply interwoven with a network of combinatorial and algebraic problems. Tracking these cross-references is essential for identifying candidate primitives capable of breaking the current bounds.

### 7.1 Related Open Problems
*   **The Sum-Product Conjecture over $\mathbb{F}_p$:** Formulated initially by Erdős and Szemerédi over $\mathbb{Z}$, the finite field variant states that for $|A| \ll p^{1/2}$, either the sumset $A+A$ or the product set $A \cdot A$ must be close to $|A|^2$ [cite: 8]. The combinatorial engines driving sum-product estimates (Elekes's incidence geometry proofs, squeezing methods) are the exact same primitives used to bound the finite field VMVT [cite: 13, 14]. Breakthroughs in sum-product lower bounds natively translate to stronger upper bounds for $J_s(A)$.
*   **Discrete Fourier Restriction for the Parabola:** The finite field VMVT acts as a direct algebraic analogue to the discrete Fourier restriction phenomenon for the parabola in $\mathbb{R}^2$ [cite: 2]. Understanding how $L^p$ norms of exponential sums behave over curved manifolds in $\mathbb{F}_p$ provides a dual framework to the combinatorial counting of $J_s(A)$.
*   **The Polynomial Szemerédi Theorem:** Bounds on multi-linear polynomial ergodic averages and progressions [cite: 10] share deep topological similarities with the Vinogradov system's constraint equations, relying on similar degree-lowering techniques.

### 7.2 Anti-Anchors (What this problem is NOT)
*   **The Kakeya Conjecture:** While the resolution of the continuous VMVT relied heavily on multilinear Kakeya-type theorems (intersecting $\delta$-tubes in $\mathbb{R}^n$) [cite: 3, 5], the finite field VMVT does *not* utilize Kakeya sets. The geometry of lines in $\mathbb{F}_p^n$ behaves fundamentally differently, and researchers attempting to port Kakeya insights to sparse subsets of $\mathbb{F}_p$ will encounter an anti-anchor.
*   **Balog-Szemerédi-Gowers (BSG) inverse theorems for continuous sets:** While Mudgal developed a BSG variant for the Vinogradov system in $\mathbb{R}$ to prove subsets exhibit structured products [cite: 16], this non-linear generalization fails structurally when transferred raw to the finite field due to torsion and subgroup obstructions.

### 7.3 Candidate Primitives
*   **Stevens-de Zeeuw Incidence Bounds:** The current workhorse primitive for bounding $J_s(A)$ in $\mathbb{F}_p$. Any improvement to the exponent in this specific point-curve theorem immediately lowers the $1/9$ savings in the VMVT [cite: 1].
*   **Elekes-Rónyai Theorem:** Used to prove unbounded expansion of polynomials. If a polynomial $F(x,y)$ is "non-degenerate", the set $F(A, A)$ expands [cite: 13]. Translating the Vinogradov constraints into an expansion problem over non-degenerate polynomials provides a candidate primitive for extracting $|A|^\epsilon$ bounds by proving that any configuration failing the bound must belong to an algebraically constrained sub-variety.

**Sources:**
1. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_XzJ3E3M6Aatv-CnfDGF-oIqYxE-3bkSCWdovoEYz95jAl2DB5dZ3GWQ-FSjlm9g6s3D86_yjZcnLGNI4xpTWXCsw0f251HY2vVvFGjCfGM3mqtH8uSZnzwBQHPM-wCU80QmjBgFmAwgEyyJJt_sek3KLdSYoWcviGDHkv7B_LQ==)
2. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKqDeTaqkVcF7GLQYTgSQE5QGMZgUSw2YMtTMJUj9V4ZPP378uJ-rBV8h7iJ9M4-aDtxd5i1LQB1Rgmnc80M0ZlVNNRgWrTraQdRvvmtibzSFNED60IFiwg5ACAC0z6vqgNixkAXN_MYTVqK0h2fc=)
3. [wisc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOj8OqYfg8CNf-LdeYK9mcuTzp3gid99typBYjAbhfEjcte_EeWPzqy1AkikIIfSaSIcC54ZdiU2NNRKdNXO8W7H4CGK1Senp74QEVRMQMVD9rr0z58NKfX2sQqVa03waavwaX12hFdm8aa-bllo31JkwUxT7v-A==)
4. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKhBifOaChmpM5TJOU36tcG032U410jSSl7ofeJJ5g9tYmEYHGKfbzDM1wn_8Nvuy52ZEVKn_VdUcI6bWlI8elVkb9gMDQ35i_CjR5MkFhQUf3pEBb16u7gWTk5VYiJc0v7Yat8EG-hLb0V8d2aH1W8zyUPVZLjoKDhotwfIIIBXpo5w==)
5. [bourbaki.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkrQZN-vzccwxfnj74G6Oq93WwzqmOW4pNVMI9mMqxL2dgjqdoYvAZgahOQx_8vn6Vp9UF6r9Vx5cxmiOxPeuHcZcs9bHWzoz--SYV4NQ_EQdeN5eEbegIap5JKXw=)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTjeH2EvZj6FMAf2Ei-TqpDwZG3ajoK8KjWI9P7dH9FeV5RdxfBvEIi91XHSHeEbSM3yZ6AFqXZMWLhoXID22xvViXUG39ydiZGV5FtBHHc25bD7FwBVJ9kOZ0wEaChoHoA6YfaP2HzDLy)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVWzfQykAV7c1mbM1DA2HrY2Q4s_eCpJmjbc05Gjjew_qMqVCcrLt-GyZUZ-4TkNoMxet2fTXfY888QXpS5jV0G55z-YRuS2N0ujp6eBShEV9PUxUc-A==)
8. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjGOC8AXQt7oWkHyo9YTMPzqw1aMIk5N80iRKVnoU1t3xieaMCmHv1C5Vl8tfvdVzumvQIEv0yCpNqIO48jYe72oQFhTDb6HDS62WrhkMlqwk7v8pnxL4ItLn0rX9FOFoG3-pN_INSF_mTkE-6ErVdvK4mUYqYFwhMCezI7CzYAKxrRk4krxILW_cKLielT1wmfY3nCEFfJpvNDr0WoQ0-YQRL0WcEznFBuIgaZbXGSLu70ZZ263EGzGLkg-Yv6C-_mNiYCBz3RTO1TXn1imNDt0mHjn5H-camGRep6Sg5lyp8sCJ6wIpWzkpj)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGL5RzzkdrP_RvLtpDyrjp6qIk6fT08GCuUpeDwZ22BXWQahdYkiZjPbZ__z6pa9HnPYlPj3tv5_U-PxfHigrVRC9BA4C-yW95F-t0Sv1qJZNKxjNQB6Q==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmbhmSSanYiLWv5xTLW20rVNaUisaMgMf16u5HoxApWKHws3X01eZaju8d8RSQANvALDdWFo0BVPlDMv3oRNgDaLgZXmDY_VzfYEkK8O0Qtz-A7j8n9A==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_qlde6mmeh7WoYytz_Pp1gIYb6aIkeFf8OQSQDa2kvX_9Ykj0iOBJbkMA9Uq_UP8dESsdalnj09eHZ0SzaHRUmWjo7ZsJWz6MfDchdmV507eO8GPgSg==)
12. [bris.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjS-jm9Mv4WizMRZEOPVK3OoHacFEBWZJGVsD3qdhp-7P2uxUZvc_Kx-jQvYhqtnmHdd6eQPzoOVisAr7u_HUa73ILHGU6iP69pbEdnIyylMrJe8sPcJlz7EmzeJ0cPlmQcwD1cyGsQAGejk8l3WkOkxh80ndtB6lSEvtZijTLiv3I5-5IaENdfEFf2lonMccEdz5hfM0lM5SRbsvz6TUNttkrZ_aaMA==)
13. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGszSUpSThhoGr9UIaLGwgMWd7ElGgFEzPU4pyuor_njJGi64Q95txQLQ4IebT2aLzVgOywT5bkAsd7wRrGVS6AgDuMdID27ONausQjNUeI86ccTK3HHg2XRQ36TrPgZspRqKpC_uVGQxbAvFx1mOMxRA==)
14. [elte.hu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnATu4JZgf_i2sJgsiayNIw9a-Nn73OuRCFJoWs7FHzXDDJIGCrc8vQhKMGXo5r2Myqh2KSNhHiZUWGJ65ymFSQ5PA8v4IEkbprJMwFXELb3e8McQWcb16Q8iHwe3DSJw8-4MpVyt48g==)
15. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWrip1jmRBQKreVU8xtbqQbGkDepb1mobx1JaxnecrjjG79MQXuZnUNQQjqcg5mFU2o7tlUcD7F1pCFgO27sjkLgEXvWdILBu5-_JJOcLOLzbNtqTkqogdZt5YTqXHEmDuqHFfMf0ZOQc=)
16. [bris.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPMtoWJuEjsFgbUhcnBFPiem_RqsUjnN_knOV1qTjDYBSNGj4Vov9K_6cbXaakW4KEIUF4_mLeHodrX5aBcrBzq6vOLplGxpJVH_Qq5N74PP3th80VkLVnXAkcgGvOGX77RoRAtx98Bu8Sc5o9LEeqPcqkniTlQyxrWFkVz4DsA93J36gkilE9eOu-pCWeahrXIY4dsgfDXSJpnBOTVnyZtOwZZGHs14bJYnRJH7W46mE=)

