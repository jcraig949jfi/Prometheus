# Multiplicative function L-functions (Tao 2016 Erdos discrepancy) 2024-2026 follow-on

**Pythia queue id:** 152
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdaRElQYXNLa09ON0xqTWNQNV9Pa3FRNBIXWkRJUGFzS2tPTjdMak1jUDVfT2txUTQ
**Elapsed:** 251s
**Completed at:** 2026-05-21T16:31:29.280891+00:00

---

# Advances in Multiplicative Functions and L-Functions: 2024-2026 Trajectories Following Tao's Resolution of the Erdős Discrepancy Problem

*   **Key Points:**
    *   Research indicates that the resolution of the Erdős discrepancy problem by Terence Tao in 2015/2016 has fundamentally reshaped the intersection of multiplicative number theory and additive combinatorics. 
    *   It seems clear that the Matomäki–Radziwiłł framework for multiplicative functions in short intervals continues to drive breakthrough results, particularly in establishing higher-order uniformity over polynomial progressions and breaking the parity barrier via graph-theoretic expander techniques.
    *   The evidence leans toward a deep, structural correspondence between the value distribution of L-functions on the critical line, random multiplicative functions, and **Gaussian multiplicative chaos**, as highlighted by major 2025–2026 research programs.
    *   While establishing the full generalized Chowla and Sarnak conjectures remains an ongoing challenge, recent logarithmic averages and consecutive-value density theorems provide highly compelling approximations of statistical independence.

*   **Historical Context and The Erdős Discrepancy Problem:**
    In the 1930s, Paul Erdős conjectured that any sequence taking values in \(\{-1, +1\}\) must exhibit unbounded discrepancy across homogeneous arithmetic progressions. For over eighty years, this remained intractable. The collaborative Polymath5 project reduced the general sequence problem to a question about completely multiplicative functions. Building on this, Terence Tao's 2016 breakthrough utilized logarithmically averaged correlation estimates and the concept of **pretentious multiplicative functions** to definitively prove the conjecture. 

*   **The 2024–2026 Research Horizon:**
    Current and forthcoming research initiatives (2024–2026) are heavily concentrated on expanding Tao's methodologies. Academic workshops at institutions such as the University of Warwick, MSRI/SLMath, and the Simons Foundation are explicitly focused on the interplay between random multiplicative functions and critical multiplicative chaos. Concurrently, new subconvexity bounds for automorphic L-functions and the formalization of these concepts in proof assistants like Lean highlight a period of intense, multi-disciplinary innovation in analytic number theory.

*   **Methodological Limitations and Scope:**
    This report synthesizes the most recent available academic literature, conference proceedings, and preprint archives covering 2024 to 2026. While an exhaustive 20,000-word threshold is structurally limited by the constraints of this generative format, the subsequent sections provide a maximally dense, rigorously detailed exposition of the mathematical mechanics, theorems, and ongoing debates surrounding multiplicative functions and L-functions.

***

## Foundations: The Erdős Discrepancy Problem and Pretentious Multiplicative Functions

The study of multiplicative functions—functions \(f: \mathbb{N} \to \mathbb{C}\) satisfying \(f(mn) = f(m)f(n)\) for all coprime \(m, n\)—has long been the bedrock of analytic number theory, primarily due to their direct connection to the Euler products of L-functions. The modern era of this field was indelibly altered by the resolution of the Erdős discrepancy problem [cite: 1].

The Erdős discrepancy conjecture postulated that for any sequence \(f: \mathbb{N} \to \{-1, +1\}\), the discrepancy along homogeneous arithmetic progressions is infinite. Formally, it asserted that:
\[ \sup_{n, d \in \mathbb{N}} \left| \sum_{j=1}^n f(jd) \right| = \infty \]
The proof of this conjecture by Terence Tao in 2015 (published in 2016) relied on three primary ingredients [cite: 2, 3]. First, a Fourier-analytic reduction developed by the Polymath5 collaboration demonstrated that to prove the conjecture for all \(\pm 1\) sequences, it suffices to prove it for stochastic, completely multiplicative functions taking values on the unit circle [cite: 1, 4]. 

The second, and most pivotal, ingredient was a logarithmically averaged version of the Elliott conjecture. Tao proved that if a completely multiplicative function \(g\) does not "pretend" to be a Dirichlet character \(\chi\) multiplied by a polynomial phase \(n^{it}\), its partial sums exhibit strong cancellation. The notion of **pretentiousness** is formalized via the Granville–Soundararajan distance metric [cite: 5]:
\[ \mathbb{D}(f, g; X)^2 = \sum_{p \le X} \frac{1 - \text{Re}(f(p)\overline{g(p)})}{p} \]
If \(\mathbb{D}(g, \chi n^{it}; \infty) = \infty\) for all Dirichlet characters \(\chi\) and all \(t \in \mathbb{R}\), then \(g\) is non-pretentious, and its logarithmically averaged correlations decay to zero. The final ingredient extended the Polymath5 arguments to rule out the remaining pretentious cases, establishing unbounded discrepancy for all completely multiplicative functions [cite: 2, 3]. 

The resolution of this problem not only closed an 80-year-old question but catalyzed a new paradigm in which the structural rigidity of multiplicative functions is probed using tools from additive combinatorics, ergodic theory, and Fourier analysis.

## Higher Uniformity in Short Intervals

A direct consequence of the pretentious framework is the study of multiplicative functions in short intervals. The landmark Matomäki–Radziwiłł theorem established that the averages of a bounded, non-pretentious multiplicative function \(f\) in almost all short intervals \([x, x+H]\) converge to its global average over \([X, 2X]\), provided \(H \to \infty\) as \(X \to \infty\) [cite: 6, 7]. 

Between 2023 and 2025, this theory was vastly generalized by Matomäki, Radziwiłł, Tao, Teräväinen, and Ziegler, culminating in the paper "Higher uniformity of bounded multiplicative functions in short intervals on average," which was awarded the prestigious Alexanderson Award in early 2024 [cite: 8, 9]. 

### Gowers Norms and Nilsequences

The 2024–2025 extensions target the **local Fourier uniformity conjecture** and its higher-order analogues. While Matomäki and Radziwiłł initially showed that multiplicative functions do not correlate with linear phases \(e(n\alpha)\) in short intervals, the higher uniformity theorems demonstrate that non-pretentious multiplicative functions (such as the Liouville function \(\lambda\)) do not correlate with polynomial phases or, more generally, with nilsequences [cite: 10, 11].

Using the inverse theory of the Gowers uniformity norms \(U^k\), the authors established that for any fixed \(k\):
\[ \int_X^{2X} \|\lambda\|_{U^{k+1}([x, x+H])} \, dx = o(X) \]
whenever \(H = H(X) \le X\) tends to infinity with \(X\). By expressing correlations in terms of nilsequences \(F(g(n)\Gamma)\), this bound facilitates the computation of short-interval averages over polynomial progressions. Specifically, it yields a logarithmically averaged version of the Chowla and Sarnak conjectures for polynomial configurations [cite: 10, 11]. For instance, for any fixed polynomials \(P_1, \dots, P_k\), it is now known that:
\[ \sum_{h_1, \dots, h_k \le H} \left| \sum_{1 \le n \le X} \lambda(n+h_1) \dotsm \lambda(n+h_k) \right| = o(H^k X) \]
This confirms that the sign patterns of the Liouville function exhibit superpolynomial complexity, confirming Sarnak's conjecture that the Liouville sequence has positive entropy [cite: 10]. The integration of these higher uniformity bounds continues to be a dominant force in 2025 number theory seminars [cite: 12, 13].

## Beating the Parity Barrier: Expansion and Divisibility

One of the most profound limitations in analytic number theory is the "parity barrier" in sieve theory, which traditionally prevents one from distinguishing between integers with an even versus an odd number of prime factors. Consequently, bounding sums like \(\sum_{n \le x} \lambda(n)\lambda(n+1)\) unconditionally has historically been considered out of reach.

In a highly celebrated line of research (presented extensively throughout 2022–2024 and deeply influential in 2025), Harald Helfgott and Maksym Radziwiłł introduced a novel graph-theoretic approach to bypass this barrier [cite: 14, 15]. They modeled prime divisibility as a graph and demonstrated that this graph acts as a strong local expander [cite: 15, 16].

### Local Expander Graphs for Divisibility

Let \(\mathbf{P} \subset [H_0, H]\) be a set of primes, and define a graph where vertices are integers in \(\mathscr{X} \subset (N, 2N]\) and edges connect \(n\) and \(n \pm p\) if \(p \in \mathbf{P}\) divides the integers. Helfgott and Radziwiłł proved that the associated adjacency operator:
\[ (A_{|\mathscr{X}} f)(n) = \sum_{\substack{p \in \mathbf{P} : p | n \\ n, n \pm p \in \mathscr{X}}} f(n \pm p) - \sum_{\substack{p \in \mathbf{P} \\ n, n \pm p \in \mathscr{X}}} \frac{f(n \pm p)}{p} \]
has all its eigenvalues bounded by \(O(\sqrt{\mathscr{L}})\), where \(\mathscr{L} = \sum_{p \in \mathbf{P}} \frac{1}{p}\) [cite: 14]. This implies the graph is an optimal expander, essentially within a constant factor of being a locally Ramanujan graph [cite: 15].

By combining this strong spectral expansion with the Matomäki–Radziwiłł theorems on short intervals, Helfgott and Radziwiłł achieved the groundbreaking bound:
\[ \frac{1}{\log x} \sum_{n \le x} \frac{\lambda(n)\lambda(n+1)}{n} = O\left( \frac{1}{\sqrt{\log \log x}} \right) \]
This bound strictly improves upon Tao's earlier estimates derived via entropy methods [cite: 17, 18]. Furthermore, their framework successfully computes averages of \(\lambda(n+1)\) when restricted to integers \(n\) with a specific number of prime divisors \(\Omega(n) = k\), yielding \(o(1)\) averages at almost all scales for any "popular" value of \(k \approx \log \log N\) [cite: 16, 18]. In 2024, C. Pilatte generalized these graphs to edges defined by rough integers, improving the error bound to \(O(1/(\log x)^c)\) [cite: 17, 18].

## Consecutive Values of Multiplicative Functions

Understanding the local behavior of multiplicative functions extends naturally to studying their consecutive values, \(f(n)\) and \(f(n+1)\). A longstanding heuristic suggests that the prime factorizations of \(n\) and \(n+1\) should behave as statistically independent random variables. 

In a significant 2024 paper published in *Discrete Analysis*, Alexander P. Mangerel investigated the exact conditions under which \(f(n) = f(n+1)\) [cite: 19, 20]. Prior results, such as those by Erdős, Pomerance, and Sárközy (1987), established that the divisor functions \(d(n)\) and \(d(n+1)\) are unequal for a density 1 set of integers. Mangerel generalized this heavily, minimizing the reliance on specific modular form coefficients [cite: 13, 19].

Mangerel's main theorem dictates that for any multiplicative function \(f: \mathbb{N} \to \mathbb{C}\), if the function does not frequently take values on the unit circle at prime arguments—specifically, if:
\[ \sum_{p : |f(p)| \neq 1} \frac{1}{p} = \infty \]
then \(f(n) \neq f(n+1)\) for all \(n\) outside a set of logarithmic density zero [cite: 21]. Conversely, for functions taking values exclusively on the unit circle (e.g., the Liouville function \(\lambda\)), the prime number theorem guarantees that \(\lambda(n) = \lambda(n+1)\) roughly half the time (in a logarithmic sense), corroborating Tao's earlier logarithmic Chowla bounds [cite: 20]. Mangerel's proof relies intimately on Tao's theorem for logarithmically-averaged correlations, applying it to the twisted functions \(|f|^{it}\) combined with continuous additive combinatorics [cite: 20, 21].

## Gaussian Multiplicative Chaos and L-Functions

One of the most explosive areas of research in 2024–2026 is the synthesis of random multiplicative functions (RMFs), the Riemann zeta function, and **Gaussian multiplicative chaos** (GMC). This intersection is the focal point of the March 2025 workshop "Multiplicative Chaos in Number Theory" at the University of Warwick [cite: 22] and the 2026 Simons Foundation "MPS Conference on Universal Statistics in Number Theory" [cite: 23].

### Critical Chaos and the Zeta Function

Multiplicative chaos, originally developed by Kahane in the 1980s, describes random measures exponentiated from log-correlated Gaussian fields [cite: 22]. Recent conjectures by Saksman and Webb proposed that integrating test functions against the absolute powers of the Riemann zeta function on the critical line \(\text{Re}(s) = 1/2\) converges in law to GMC measures. 

The case of the squared zeta function, \(|\zeta(1/2 + it)|^2\), corresponds precisely to **critical multiplicative chaos**, the most delicate boundary case of the theory. In forthcoming (2025/2026) work, Adam Harper provides the first rigorous proof of the Saksman–Webb conjecture for zeta squared [cite: 23]. 

### Random Multiplicative Functions (RMFs)

A random multiplicative function \(f(n)\) is typically constructed by assigning independent Rademacher (\(\pm 1\)) or Steinhaus (random phase on the unit circle) variables to prime values \(f(p)\), and extending multiplicatively [cite: 24, 25]. Harper (2020) originally observed that the partial sums \(\sum_{n \le x} f(n)\) behave like critical GMC, leading to a typical size smaller than the standard square-root deviation \(\sqrt{x}\)—a phenomenon termed "better-than-square-root cancellation" [cite: 22, 26].

In 2024–2025, researchers like Besfort Shala and Jake Chinis established central limit theorems for the correlations of Rademacher multiplicative functions by leveraging point-counting on varieties and quadratic twists [cite: 27]. Similarly, the convergence of random Euler products inside the right half of the critical strip (e.g., \(1/2 < \text{Re}(s) < 1\)) has been shown to be intrinsically linked to the Generalized Riemann Hypothesis (GRH) for entire L-functions [cite: 22].

The convergence of probabilistic models and exact arithmetic functions is epitomized by the **Fyodorov–Hiary–Keating conjecture**, which predicts that the maximum of the Riemann zeta function over short intervals on the critical line behaves statistically like the maximum of a branching random walk [cite: 22, 28]. Extensive advances by Arguin, Bourgade, and Radziwiłł continue to formalize this conjecture [cite: 7, 22].

## Subconvexity and Moments of Automorphic L-Functions

Beyond the Riemann zeta function, the analytic theory of general \(L(s, \pi)\) functions attached to automorphic representations \(\pi\) remains a primary vehicle for understanding arithmetic distribution. Two central metrics of progress in 2024–2026 are the computation of high moments and the subconvexity problem [cite: 27, 29].

### Subconvexity Bounds

The Generalized Lindelöf Hypothesis predicts that on the critical line, \(L(1/2 + it, \pi) \ll (t \cdot C(\pi))^\epsilon\). The Phragmén–Lindelöf principle provides the trivial "convexity bound" \(L(1/2, \pi) \ll C(\pi)^{1/4}\), where \(C(\pi)\) is the analytic conductor. Breaking the exponent \(1/4\) is known as the **subconvexity problem**.

Recent advancements presented in 2025 focus on higher-rank orthogonal and unitary groups. Building on Hu and Nelson's 2023 subconvex bounds for \(U(n+1) \times U(n)\), researchers like Blanca Gil Rosell have developed explicit subconvex bounds for L-functions attached to the orthogonal groups \(SO(4) \times SO(3)\) [cite: 27]. By applying exceptional isomorphisms relating \(SO(4) \times SO(3)\) to the triple product \(SL(2) \times SL(2) \times SL(2)\), researchers can port spectral machinery and Rankin–Selberg moment estimates to previously inaccessible degree-12 L-functions [cite: 27, 30].

### Moment Asymptotics over Character Subgroups

While moments of \(L\)-functions over full families are well-studied (e.g., Katz–Sarnak symmetries), evaluating moments over highly sparse sets is significantly harder. In a February 2025 breakthrough, researchers obtained an exact asymptotic formula for all moments of Dirichlet L-functions \(L(1, \chi)\) modulo \(p\) when averaged over a remarkably small subgroup of characters \(\chi\) of size \((p-1)/d\), where \(\phi(d) = o(\log p)\) [cite: 29]. 

Assuming the infinitude of Mersenne primes, the range achieved in this result is strictly optimal. This deeply impacts the calculation of relative class numbers of cyclotomic fields [cite: 29]. The authors also successfully extended these techniques to extract asymptotic formulas for the second moment of the central values \(L(1/2, \chi)\) over similarly sparse subgroups, providing new unconditional evidence for the non-vanishing of Dirichlet L-functions along "thin" subsets [cite: 29].

| Feature/Metric | Traditional Bounds | 2024-2026 Advances | Reference |
| :--- | :--- | :--- | :--- |
| **Parity Barrier ($\lambda(n)\lambda(n+1)$)** | Unbreakable without GRH/Chowla | $O(1/\sqrt{\log \log x})$ unconditional | Helfgott & Radziwiłł [cite: 14, 18] |
| **Short Interval Divisibility** | Gaps in polynomial progressions | Higher order uniformity via nilsequences | Matomäki, et al. [cite: 10] |
| **L-Function Subconvexity** | $GL(2)$, $GL(3)$ known | $SO(4) \times SO(3)$ triple product | Gil Rosell [cite: 30] |
| **Dirichlet $L(1, \chi)$ Moments** | Averages over full character group | Optimal averages over sparse subgroups | 2025 Preprints [cite: 29] |
| **RMF Partial Sums** | Square-root boundary $\sqrt{x}$ | Critical GMC / "Better-than-square-root" | Harper / Warwick 2025 [cite: 22, 26] |

## Function Field Analogues and Generalizations

The translation of number-theoretic problems to the ring of polynomials over a finite field \(\mathbb{F}_q[t]\) frequently elucidates structural mechanics obscured by the archimedean properties of \(\mathbb{Z}\). In extensions of the Erdős discrepancy problem documented in 2026, researchers have comprehensively classified the limiting behavior of partial sums of multiplicative functions \(f: \mathbb{F}_q[t] \to S^1\) [cite: 1].

It was demonstrated that the discrepancy of a completely multiplicative sequence over \(\mathbb{F}_q[t]\) is strictly dependent on the topological definition of the interval. When using a natural lexicographic ordering, the discrepancy is always infinite (answering a question of Liu and Wooley) [cite: 1]. However, for "short interval" discrepancy over function fields (for \(q\) odd), bounded short interval sums exist if and only if the function coincides with a modified Dirichlet character to a prime power modulus [cite: 1]. This precise structural rigidity validates the function-field analogue of the Polymath5 conjectures.

## Formalization and AI in Number Theory

The years 2024 and 2025 have also marked a systemic shift toward the formalization of multiplicative number theory using interactive theorem provers and Large Language Models (LLMs). The L-functions and Modular Forms Database (LMFDB) has undergone massive expansions to verify the accuracy of arithmetic datasets [cite: 31]. 

Crucially, the Lean mathlib library has successfully formalized over 7,400 lines of rigorous code establishing the analytic continuation and functional equations of L-functions, Dirichlet characters, and the Birch and Swinnerton-Dyer (BSD) conjecture verifications for specific elliptic curve ranks [cite: 32]. 

```lean
-- A conceptual representation of multiplicative function formalization in Lean 4
def is_completely_multiplicative (f : ℕ → ℂ) : Prop :=
  f 1 = 1 ∧ ∀ m n, f (m * n) = f m * f n

theorem tao_erdos_discrepancy (f : ℕ → ℝ) (hf1 : ∀ n, f n = 1 ∨ f n = -1) :
  ∀ C : ℝ, ∃ n d : ℕ, |∑ j in range n, f (j * d)| > C :=
by
  -- Formalization of Polymath5 reduction and Elliott's logarithmic conjecture
  sorry
```
While full formalization of Tao's discrepancy theorem is still a work in progress (often hindered by the complex continuous additive combinatorics required), the algebraic core of character theory and L-function analytic continuation has been entirely verified up to 2026 standards [cite: 32]. Furthermore, AI and machine learning techniques are actively being deployed to find counterexamples and optimize bounds in discrepancy problems and Cap-set problems, representing a methodological fusion of computer science and pure mathematics [cite: 31, 33].

## The 2026 Horizon

Looking toward mid-2026, the analytic number theory community is heavily mobilized around the stochastic properties of multiplicative functions. Scheduled events, such as the "Probability in Number Theory" workshop (June-July 2026) and the "Arithmetic Statistics Workshop" (March 2026) at the Centre de Recherches Mathématiques in Montreal, underscore the permanence of this probabilistic turn [cite: 33].

The resolution of the Erdős discrepancy problem by Tao was not a terminal endpoint but a catalyst. By demonstrating that multiplicative structures possess inherent entropy and interact with additive structures only through tightly constrained "pretentious" channels, Tao unlocked new algebraic and graph-theoretic approaches [cite: 4]. Today, whether one is analyzing the maximum of the Riemann zeta function via Gaussian multiplicative chaos, binding the subconvex geometry of $SO(4) \times SO(3)$, or constructing Ramanujan-like graphs to bypass the parity barrier, the conceptual DNA of the 2016 breakthrough remains heavily present. 

As the boundaries between random matrix theory, statistical mechanics, and L-functions continue to blur, the trajectory of multiplicative number theory throughout 2024–2026 guarantees that the statistical independence of prime factorization will yield even more of its long-held secrets.

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF11C-0o8Jb8Q33TBbMdymXzSVnoxvMUZ4XC7mEw_jFO2tr_pCNXR-1CzBKEw4FL4JRiCdidGMV1KQQM0A0WYhUPGsYCvG847tCjbddByN_8sUTbNgBkU4dQ9Fok5NoWCjOLJ2EIgN8-cSnScwOrsayzV2aQoajkyXuCL2ZnljkE5V9PJ8URQ==)
2. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHb9RTGhdRYHT6ZhYGciTDz3H0ySqH2MB1JMY6ZBnMKglhbRxlj5wMMcUF16qLDpaiv2_fLii5lZ5KRBvbCi4JyuOzBz-Zw6Pmtv8tqOVInZjdeVieJ8OPYne-Pffa4iKyvapN3N4Zw4edM7cvdX-rcnmF5hKnwhRYqmTj3KQ==)
3. [aperiodical.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCHUys1mtYR0UxPi36si9Hvu_PcRGZua8ZGUVkQuWhL4cnVZJ-HPxrVQmTkB46dA_7WGNQAGiJkgB7ykNWfVnF2GZLGkqDlyAb-lWxeJ67ikKdTP5uMAjXNoTMCTNpHbSzsAlF6EoPTCguaDR8s3WrHhF9r9eOWmfLJ6gRZyY3YjJbKdGMKlCNklkz)
4. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyxUSoGlMHXnJc1jvDFSL-VL56JnILxrLzvQHd3OG1EsfpAzdtTDZfIf7u2g4x5XZbFzX7NZ6kqE-nyzsPqn4iImr66oEN6cOlxR0k64IOE2SOfAWyeiZpOT4DJVhriJgB7zs0MYUL_hIlEVr3jjt5yR-lH2qP9j-MYCQVP3CRdZOhsoSdprTa)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFc7aedebn7P6BSsN5bK4zEMGPL1pJEiQvNDaOPwhI0KAntJMFoP1MO1H6d3RA6Dh62s8ImwvkxBvwdg08bYOY2Auft_UR4EGkPuGZmq5gZblwriu-qzoTq7st7hS3X3052YBVTOaFl6ZySZWkTk02JuuIVEcbeKnzmpjT-Ef0o7vtz2mP3SlANlP43h-QBOfXKDtYQ7QA6l88SKo5II1qWw0zpXXGm1FGsmohqkVqD6c0lQQ==)
6. [mathinstitutes.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3JhLwYiRywWYxf7MAx4VQEyaI5n6p7ADcbJ3N-5u_XjK8A8Kfp9xOo5VohweOyG3aSM-DDtcBUE-JbdAjPsDZhFqiPqCQMs-sfHpQBDec0aB7xdxF6iCD1IcHmQX_SxHHDVW3sxc=)
7. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9tZwi7GZfE-olVn_hn3_dq19j7K16WtLVI5kWujPy-7QwzHqwtobyRFDOg6605JaWm1F-2Y3M9vLJ_54PT0zNmPen0eNr3uSyHplGYgUtC5GchKCCMiBGlQ==)
8. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyb0YGYSxciamc_LQrbTyiYasVvqaLGQmaT60Xb1L3X2lNceW5zLiMbIFvPPbDtKyxuoYL7T-HC0dTXNC6CK6QmDf7bMakwjgENtFGuaWQwTnQEC5Cw8i_AaEm-0TFVmNg1oUgCXKW)
9. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdkwSUcifv7jzz-fpLLARaSGz8-O3mQq8pS0zTjTwK73byrbKX3zXUf43gJ5eX8BNRrmntapWyU_fUyEFo7KJtlAI6NXY0BqznAipLeN0lDuJ9BrLRYTTtd14ch98UiWnV)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzJzqlKlM4r-vC-hMg5y5Tc8zO6Jf-nivMo1v49Y-qKfjHM9oGnskBMhKLYCo8ISDZU13mk-Xy79zNsN7XOV6w1vCGwkspKe8BQGlYM6cRB-USVNZG97FEynHVEvWljRPnw394PoVzDRZbI4-S1cyZgsuxxGA2tP7rj5XIrohBbQ2KXI4SjWRcPkZ7WYbOagmaFH8HUXP5nZZ0buF-fXjV6DAx9vEeoh62lmUuKfOATlQMSU1ueVLdJaG4924=)
11. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgSkHty25DYpXcxLIV8dVPnqiXiyaa_11x_kQ9dU4zllkNk5slr5rclNRigtvReCCvksRQpYYKfwbcEXByLZ_AtKRTavD7ikgiciu1aevk-7Dm-y5KFxdPhTqsTNGzVBoF0MI-6BuHhwik)
12. [dctabudhabi.ae](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2yJZ9sxREZhHYUf3soybz2NhUjxkBw9u3CMMrjHjX3KgBnSKo6sM_s_HnyIiyAQdkqiONjfNsV8S1gw48MNsjOdLT6k6dsO11gLqFPoUoAvDKKLE60Ime6v63HuA40CUBUrEqoXYXAx1ieNqgB3BSIfKF3xBXTv4YJbzLiG3a2gqP_wU7-NnJww0LDRIvNKGpsyzwbtlRaHs78P-3twQ1Ckze3SE1SC6eqXyynTwkrlrZz_-VvNhOW8_7jlP0yw==)
13. [illinois.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcWcnmXeVzgmOgE6ztCf9wGMd5P31heWjzMmsgssGGk1DX-snsrlGPYnyo4PQ9Ivh4I97mAVTdD_ZDHezwpj2lC4o2F9qe9DwZy1gMKA0UHDHrIsPScCxWcCIvRCYadhWHkeeKhPtxSXC6)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGckgEsoxwO8WjreEYc6xDoJ1-LP0pIVfU8zYYzIr36VhY_hXDu-_PRzJHbbcup38h9M61nDKRwUh82g4BSuLiaXbyh4KbbbVnv4oBLHQd-jF04HkzhEw==)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEE7NdVeBuEq-0gaw4-76Ut68ntbckngpSA-573weHixCpD7f7sisQlARE4QUSn-KjMrni-xXBaYvjK5uBwYHjwTx6VBqr_s5tzQJjK1kWPc7TrEdFP9ClNC35a9IdSHmHmAXBfSygvvevgnw7HPHYMGqHxJCs8s94mFSuV6zde-b9Nc6tWP9taxcFx8kj3jJEvqQglvdYOv54=)
16. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYTjJydmBT8VNH-W-89M_LZa7s_Kafyd9vT0zHEY3CB0DZPUEqRr6rGgUDHqRUiT-aIap4qVV6gICr7d_XXwmqPTl-U5f5Lu9NIeIfuqatqgLmluSMwTc1Nr6PAg8kInepswSES6fH7K8bJMdXiLapZal3sPWaqrpDbn0JgZylhozewlXDarb5mcSRu8xeH3mrW7Lkwcs=)
17. [ethz.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGp1eekzUqlirLlt13PSWter4Mcn-D9TpNgLNCze_rfAkmH02jJcdwqSYd_MyxX9GRadr_LgHFFjKddCNgLXRBI5DJGk_LRGSU2YkwM8rOYnokSu_FcGxozh5wWBQ4opzn9vB56PKiwUHlO897XHWSPkWNsMHRgJ42hzMZ0uK-LQEepKklnEG8w24zyFIsURT1oo9CmIvyXPg==)
18. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERjlTJDdHncaGGSa1KFBZjuK9rEqtfqUPcJ8XIH_mQsNFhI8Obv0lL-cevgfN2Bh3Ggb8l_p8u51IjZy6Jr1vOJbYciNy-GrPboAbIem-HuW0hDmwx5B_Y3xkZMtnKP5NribopnxXTDFXL7DSXqjJSXQ==)
19. [discreteanalysisjournal.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7QD29bH-oDY5S80XDxGKuW9UOVmeVH5j5WOIdiXBb86FjfUt_KRoelAyDfWiup2LH9MfIbK19KFpthtJ08VZGoCUTF5PCKBPUzwZzM0XM3xUxjdhyylLIQ1M3qy4VxUuWyAyK4lqs58T1520UxOKDs6XYpYlL8tzrhoh2gOPRT3Wyz4gFz3r9a4JKycqqpjA2R2xkbXPCoVuDrTFFmpCX)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvIGspW5E25pX4SEoKaNfP2SK5q-ZVjWXYbALMa2lBqRJkSVlXbjyVYKWACIhSNDRWiBEqhs8VLODndPPGvjz1cNyqXSUmpA0TLtHG12D1xbeY_WkPhEVOMZB901Ufo04lltjKHGuSoufQvMb8bCiNWTpRIbJ_LTkmwWYYxfpeXyP_hewRPKJUiLDcq8yKnmVhpTuLPzHDglvfJQdaQ6uh)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEda_mESbIQfv9mKr0nMG0T_eSOfIOaqJDLgVuR8ezB10tbh5kgqcBn14PmTZIs4X9cIvXMTezQHQLAXpAsJXxTw54aNy1A00yBYK5k96zsm6JN3G02xQ==)
22. [warwick.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHANc5lYSmz1vCuXY2YuMU05ZT3_fVpTZpSlTHU8GTnBH_YHkXtPy00BSsyJGTCkFRmTIJWs7p10aFdm5JUsmDyYIGJjRfJN2xs0CVbhVBsCuqdpZO1kEHEHbrKHth63umVqbpwTBYY0qXJNpVWcjXIKRkBYiH9BONKht40Z3pPXAOTfmSKbSUq)
23. [simonsfoundation.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjenOdGE4Q3nXCTVeIU_0YnhzMFqmeWsC69-dtAvylgRoUWQpCUDvAfjrPFl_uqFcz5ZZG-OHO3XmrAbWny6_yiPvygp3jKCDNMezYqDqmH7jrjNNqfge6d2Sev_QwntbCtUbw5unYn7gC0P_wAl2vvD4JDMZVCC5gQkikdACyT55TaA3VJagPeskLGKnmKfOJV76ZAg==)
24. [osu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXZUmrKl5drgHgjynL0t4weUqgjOMmiuIZ3GJdgx8eRaGqU6WEjnlesg3foKZglBl7Cojhxb0YgSqYRCM1AfD3P-0IT39JTf4t7Apwvf1mPGbRh2M8vQhzDRQdFhOXQYMcHCN8Bd-ptpqkCn443u4XQ_6EqH73m78HwVL2YdqXrwSY6_aIbGSxr8RFSHdVAsE48BdOkZS8ZOvaGLqPli-SFvtMcmaUlmVO7Fj28iwAH_UAtg==)
25. [maximgerspach.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEa_WoUwcKLKGjHvv60cxNz3pz9zaJ2324ek9LaitcPIRq8tRejIy1NDrSoZRpQKMTqeuk0ansbEv_4ySvGI4ag_nQzHLkupM2iBjB2AJbl-piEQVvV0X0tJNE4SN4=)
26. [duke.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnfhlMLGcCl85oxXbqdtXwt4-pQjAGGn5iI2PLCRm_UFn4OmReHZpsw2ouLIvMKGXi0Knv0X8rX-eXs29xa5z88PZp1Ex5UyNiXN2AzHpySi9AKXvBHAFA_jRUuVqjUm2cTJLOzwdZeLCS68gEv1dc7Zg84-yxTHbBUbpOOv7IH3DmPJfm1mITu3_92Vk=)
27. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4sAM8LzhZhUTo244yPwuz7LARNcEfdVGo-9oT7cRS17E2mLG0jYu7KlMtHOM6b_6m1Y6UD8KPnKnfFMcVqsoG42HYvIth4dYkbgOiWOjLuYMsLJAKk92gFhg69nUTu0H3AvwCF-h1JBEbceCxgJg=)
28. [uqam.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgIJe2uznHmEX_KzcNFT4SaeaEFigWSqGxOqCwJ8TaxcvnjfE0tfNhKDkF5uQOnF-2plcjrv_Fan97hdiFTCBE15bLqb5qI9uNlaCboN9R-Xl8t6pTqu0n8sTjP5V5qmmOByaWT-JoYSQVn4rgpw==)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0_kOMS_Hb3SY1QT8CsIYG5ZoNPtBu5_ASU4kYcABWXuJVMTJi3Wvb369_6XSPb7qj3p0SOUHSjpp_WGXTBV27jHvxOAbj_aBhSGp62M2wCF8eeVr2Iw==)
30. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzAhdOO93FvOwN4kYHJN9P-BW5TiuCVakNozYtGfVBT5XWnHzPY93yCXQt7nTzNidjsplA63RLjrVXsPZINTZLC3_-KNV42OS-KmZgjFt1rphUIl-dBD03gbpzRGMI107KWA8=)
31. [dokumen.pub](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhCKmkaovNhbbHFrRxJDtJsdR9BLL_6X7Tgc0wipK_TBWj0Vn2vRdr4ybk0g-4rW9nOam77qn13lq9zXazn8WBQTPkwDSdfXt10MnQzMnQpFXhXY3xj5WthIbSsTwV735jX3NMGBjTu-GK_-pHUBDtTBXY89hB3hgpu193dnExHODzhW0XzbLcwVBVSJBXc5raMz8yOy5vogCeSJ-f9hZgvz6ofhVYpITTdeiNmd6IGlOdxLuXqyQxBMf-zoVBqrW8kd56cM8YBQIwnc7S08z6ZVk43GXba6YVkj4GZAIfM7R-NXILWD9uhXlhbfXIhjKjC6sbmDq565O8v150Mh9Lsl6AaoChBRb-4m1IkCsAPRIQEw==)
32. [leangenius.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpcMwpy0azCRwdilghW-YyBGZCKJvtJ8rBHAB-c7oqTSxJZEWEsFxZGjFLqiW84S5ftXR4dtHUdTT0ZSt6LmvoXgZ41japT5MvHbXphA==)
33. [numbertheory.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlkquoSWQ5NINjjar6_NsLVgVlK5YgqQBBfWEbea1Pt8MrQvB40ine2vhyzwJUIQH8HT6VVOBjg1VeOsLzMA4Jec8Gf5fbDBmx_i_KGIg5b8AIoEMTFvEjGeAhTtI=)

