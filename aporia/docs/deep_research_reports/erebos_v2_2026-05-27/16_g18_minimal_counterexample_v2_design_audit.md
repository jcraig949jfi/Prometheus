# Prompt 16: G18 Minimal-Counterexample — v2 design audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdkWWNXYXV2SkxZdkQtc0FQaTh2QTJRcxIXZFljV2F1dkpMWXZELXNBUGk4dkEyUXM
**Elapsed:** 242s

---

# Report on G18 Minimal-Counterexample Architecture: Gradient-Field Prediction and Structural Refutation in Mathematical Catalogs

**Key Points:**
*   **Methodological Advances in Search:** Recent (2024–2026) systems such as Isolde [cite: 1], AlphaEvolve [cite: 2], and Aletheia [cite: 3] have revolutionized minimal counterexample search through Counterexample-Guided Inductive Synthesis (CEGIS) and neural-guided evolutionary frameworks.
*   **The Epsilon Flaw:** Relying on numerical thresholds (`M_COMPARISON_EPSILON=1e-9`) to filter false positives in Mahler measure computations is fundamentally flawed due to the algebraic invariance of cyclotomic extensions [cite: 4, 5]. A structural, factorization-aware exclusion pipeline is strictly required.
*   **Gradient-Field Optimization:** Transitioning from crude modal kill-pattern heuristics to differential gradient-field optimization [cite: 6] and Voronoi tessellations over the $(d, \mathcal{M})$ space allows for rigorous, continuous approximations of discrete counterexample domains. 
*   **Substrate-Grade Protocols:** The discovery of a minimal counterexample to a foundational conjecture like Lehmer's requires an exact, multi-stage verification protocol involving exact algebraic arithmetic, formalized Lean 4 proofs, and cryptographic embargoes.
*   **Contrarian Correction:** G18's reliance on rich kill-pattern density landscapes intrinsically biases it against obscure, under-studied conjectures. Mitigating this requires synthetic kill-ledger generation via agentic, LLM-driven adversarial variant synthesis.

This report addresses the architectural, mathematical, and methodological upgrades required to advance the G18 MINIMAL-COUNTEREXAMPLE system from a heuristic-based numerical scanner to a structurally aware, gradient-guided theorem-refutation engine. Focusing on Lehmer's conjecture and the Mahler measure, it provides a comprehensive roadmap for the v2 loader design, integration of 2024–2026 state-of-the-art counterexample search paradigms, and post-success protocols for substrate-grade mathematical discoveries.

***

## 1. Counterexample Search Methodologies (2024–2026)

The landscape of automated and semi-automated mathematical discovery has shifted dramatically between 2024 and 2026. The search for minimal counterexamples in discrete mathematical catalogs has evolved from brute-force computational sweeps to highly sophisticated paradigms integrating Satisfiability Modulo Theories (SMT), Parametrized Gradient Search, and Neural-Guided Synthesis. Below is a survey of three primary methodologies and their representative state-of-the-art systems.

### 1.1 SMT-Solver Enumeration and CEGIS
SMT-solver enumeration utilizes first-order logic and background theories to systematically rule out regions of a search space, yielding minimal counterexamples when a conjecture's negation is proven satisfiable [cite: 7, 8]. Modern systems heavily utilize Counterexample-Guided Inductive Synthesis (CEGIS) to iteratively refine search parameters [cite: 1]. 

**Representative System: Isolde (2026)**
Isolde is an advanced automated reasoning tool designed to synthesize minimal counterexamples in the domain of transactional isolation levels [cite: 1]. Because the problem involves higher-order logic formulas and massive bounds on history size, exhaustive enumeration is impossible [cite: 1]. Isolde implements a CEGIS algorithm that utilizes first-order SMT solvers to synthesize precise counterexample histories that violate assumed specifications [cite: 1]. By reducing variables to their minimal possible values, Isolde systematically extracts "minimal counterexamples" that human researchers can use to refine formal specifications [cite: 1, 7].

### 1.2 Neural-Guided Proof-Counterexample Synthesis
Neural-guided systems employ Large Language Models (LLMs) to traverse vast, unstructured combinatorial spaces. Instead of traditional deterministic enumeration, these systems treat algorithms and mathematical objects as evolvable code, using LLMs as semantic mutators to iteratively improve candidate solutions against automated evaluators [cite: 2, 9].

**Representative System 1: AlphaEvolve (2025)**
Developed by Google DeepMind, AlphaEvolve is a Gemini-powered evolutionary coding agent specifically designed for general-purpose algorithmic discovery and mathematical counterexample generation [cite: 2, 10]. AlphaEvolve pairs the creative problem-solving capabilities of LLMs with rigorous automated evaluators in a closed-loop evolutionary framework [cite: 2]. It evaluates candidates on open mathematical problems (e.g., matrix multiplication, kissing number configurations) and iteratively prunes invalid paths [cite: 2, 9]. In 2025, AlphaEvolve successfully traversed discrete mathematical catalogs to break the 56-year-old Strassen matrix multiplication record [cite: 9]. Its methodology explicitly balances "counterexample-search-first" and "proof-first" modes, allowing it to navigate dense mathematical substrates effectively [cite: 2, 11].

**Representative System 2: Aletheia (2026)**
Aletheia, built upon Gemini Deep Think, is an autonomous mathematics research agent that iteratively generates, verifies, and revises mathematical solutions end-to-end in natural language [cite: 3, 12]. In a massive semi-autonomous evaluation, Aletheia was deployed against 700 open conjectures from the Erdős Problems database [cite: 3]. Utilizing a natural language verifier mechanism to identify flaws in candidate solutions and narrow the search space, Aletheia successfully synthesized autonomous solutions to four previously unsolved open Erdős conjectures [cite: 3, 13]. Aletheia's decoupled Generator-Verifier-Reviser architecture mitigates hallucinations and effectively acts as a neural-guided search for structural counterexamples [cite: 12, 14].

### 1.3 Parametrized Search with Gradient Hints
**Representative System: CodeScientist (2025)**
CodeScientist is an autonomous scientific discovery (ASD) system that reframes ideation and experiment construction as a form of genetic, parametrized search over code blocks and research artifacts [cite: 15]. While heavily focused on agent architectures, CodeScientist evaluates mathematical and algorithmic bounds by generating execution environments, tracking performance surfaces, and establishing new empirical bounds [cite: 15, 16]. It performs an end-to-end search utilizing multidimensional feedback (similar to gradient hints in discrete spaces) to zero in on optimal or counter-indicative structures [cite: 15, 17]. 

***

## 2. Structural Exclusion: The Fallacy of the Epsilon Band-Aid

The current v1 loader relies on `M_COMPARISON_EPSILON=1e-9` to catch false positives when hunting for minimal Mahler measures. This numerical approach fundamentally misunderstands the algebraic nature of Lehmer's conjecture and the behavior of the Mahler measure over $\mathbb{Z}[x]$.

### 2.1 The Mathematical Inadequacy of Numerical Epsilon
The Mahler measure $\mathcal{M}(P)$ of a polynomial $P(x) = a_0 \prod_{i=1}^D (x - \alpha_i) \in \mathbb{Z}[x]$ is defined as:
\[ \mathcal{M}(P) = |a_0| \prod_{i=1}^D \max(1, |\alpha_i|) \]
Lehmer's conjecture posits that there exists a universal constant $\mu > 1$ such that for any non-cyclotomic integer polynomial, $\mathcal{M}(P) \ge \mu$, with the smallest known value being Lehmer's polynomial at $\mathcal{M} \approx 1.17628$ [cite: 4]. 

By a classical result of Kronecker, $\mathcal{M}(P) = 1$ if and only if $P(x)$ is the monomial $x$ or a cyclotomic polynomial $\Phi_k(x)$ (whose roots are all roots of unity) [cite: 5]. The Mahler measure is completely multiplicative: $\mathcal{M}(P \cdot Q) = \mathcal{M}(P) \cdot \mathcal{M}(Q)$. Therefore, if $P(x)$ is multiplied by *any* cyclotomic polynomial $\Phi_k(x)$, the Mahler measure of the extended polynomial remains exactly the same: $\mathcal{M}(P \cdot \Phi_k) = \mathcal{M}(P)$ [cite: 4, 5]. 

When the v1 loader encounters a cyclotomic extension of a known polynomial (e.g., Lehmer's polynomial $\times \Phi_{16}$), it computes a Mahler measure practically identical to Lehmer's. Because the roots of high-degree cyclotomic polynomials lie exactly on the unit circle ($|\alpha| = 1$), floating-point numerical root-finding algorithms will yield roots like $1.000000001$ due to Unit in the Last Place (ULP) errors. Setting an epsilon of `1e-9` simply truncates these precision errors, but it does **not** solve the problem that the polynomial in question is just a trivial factorization of a known entity, not a novel minimal counterexample.

### 2.2 Structural Filtering v2: Factorization-Aware Lookup
To permanently resolve this, v2 must abandon floating-point filtering in favor of exact structural algebraic geometry. 

**The v2 Structural Pipeline:**
1. **Irreducibility Verification:** Lehmer's conjecture inherently applies to *irreducible* polynomials [cite: 5]. Before any root-finding or Mahler approximation is attempted, the candidate polynomial $P(x)$ must be factored over $\mathbb{Q}[x]$ using the LLL (Lenstra–Lenstra–Lovász) lattice basis reduction algorithm.
2. **Cyclotomic Stripping:** For each irreducible factor $f_i(x)$, the system checks if $f_i(x)$ is cyclotomic. This is computationally cheap: a polynomial is cyclotomic if it is monic, has integer coefficients, is reciprocal (or anti-reciprocal), and its degree $d$ equals Euler's totient function $\phi(k)$ for some $k$. If $\mathcal{M}(f_i) = 1$, it is stripped from the evaluation [cite: 4].
3. **Monomial Stripping:** Factors of $x^k$ are structurally ignored.
4. **Exact Algebraic Measure:** The Mahler measure of the remaining non-cyclotomic, irreducible core is evaluated. If this core is identical to a previously cataloged polynomial (e.g., Lehmer's degree-10 polynomial), the entry is structurally tagged as a `known_entity_cyclotomic_extension` and bypassed.

By evaluating the exact algebraic factorization ring rather than relying on IEEE-754 precision heuristics, G18 eliminates cyclotomic false positives with absolute mathematical certainty.

***

## 3. Gradient-Field Region Prediction in Discrete Catalogs

The v1 loader's reliance on the "modal kill_pattern" to predict where a counterexample lives is statistically primitive. It assumes that the most frequent point of failure directly adjacent to a counterexample bounds the counterexample itself. To achieve a substrate-grade prediction, v2 must map the discrete catalog space into a continuous manifold and apply gradient-field methodologies.

Recent advances in 2025–2026, such as those by Wang et al. utilizing differential gradient field optimization for complex scene reconstructions [cite: 6, 18], provide a framework for navigating highly restricted, non-convex spaces. We adapt these continuous field dynamics to the discrete mathematical catalog.

### 3.1 Minimum-Mahler Trajectory (Per-Degree)
We define the state space over $(d, \mathcal{M})$, where $d$ is the degree of the polynomial and $\mathcal{M}$ is the Mahler measure. For each degree $d$, there is a known absolute minimum Mahler measure $\mathcal{M}^*_d > 1$ for non-cyclotomic polynomials (e.g., for $d=10$, $\mathcal{M}^*_{10} \approx 1.17628$). The sequence of points $(d, \mathcal{M}^*_d)$ forms a discrete trajectory. By interpolating this trajectory, we establish a topological boundary curve in the search space. Predictions are geometrically weighted to follow the first derivative of this minimum-Mahler trajectory, anticipating where the curve dips below the current universal minimum.

### 3.2 Kill-Density Voronoi Tessellation
Instead of relying on a single modal kill pattern, we project all historical `kill_ledger` entries onto the $(d, \mathcal{M})$ continuous Euclidean plane. We partition this space using a Voronoi tessellation, where the seeds of the Voronoi cells are the dense clusters of previous computational exhaustions. 
*   A Voronoi cell $V_i$ with a high density of `region_R_exhausted_without_counterexample` tags represents a heavily barren substrate.
*   "Gaps" in the tessellation—regions where the Voronoi polygons are exceptionally large—indicate areas with low search density. These become the primary target areas for structural searches [cite: 15].

### 3.3 Gradient Computation on Frequency Surfaces
To target the exact degree-band for the v2 loader, we construct a probability density surface $S(d, \mathcal{M})$ of finding a counterexample. This surface is inversely proportional to the kill-pattern frequency. Applying principles of differential gradient field optimization [cite: 6], we compute the continuous gradient $\nabla S$.
*   The gradient vector $\nabla S = \left( \frac{\partial S}{\partial d}, \frac{\partial S}{\partial \mathcal{M}} \right)$ points toward the steepest ascent of "unknown territory".
*   The search algorithm performs gradient ascent along this continuous field. When the gradient dictates moving to $d = 37.4$, the search is parameterized to sample the discrete mathematical catalog at degree bands $d=37$ and $d=38$. This maps the efficiency of continuous gradient-field optimization onto the strictures of a discrete polynomial catalog [cite: 6].

***

## 4. v2 Loader Design: `g18_lehmer_v2`

The concrete specification for the `g18_lehmer_v2` loader incorporates the structural algebraic filters and the continuous gradient-field predictions into a unified, high-performance architecture.

**System Architecture Specification:**

1.  **Component A: Factorization-Aware Pre-Filter**
    *   **Input:** Polynomial candidate $P(x)$ generated by the search heuristic.
    *   **Process:** Computes $P(x)$ over $\mathbb{Q}[x]$ using the Cantor-Zassenhaus or LLL algorithm. Checks if $P(x)$ is self-reciprocal (a necessary condition for minimal Mahler measures) [cite: 19]. Strips all factors $f_i(x)$ where $f_i(x)$ is cyclotomic ($\mathcal{M}(f_i) = 1$) [cite: 4].
    *   **Output:** The strictly irreducible, non-cyclotomic core of $P(x)$. If the core is empty or matches a previously known polynomial, the iteration aborts.

2.  **Component B: Voronoi-Cell-Based Region Prediction Engine**
    *   **Input:** The global `kill_ledger` database containing $(d, \mathcal{M})$ pairs of all historically evaluated polynomials.
    *   **Process:** Generates a 2D Voronoi tessellation of the search space. Computes the gradient of the inverse kill-density surface $\nabla S$ [cite: 6].
    *   **Output:** Outputs a dynamically bounded search region $R = [d_{min}, d_{max}] \times [\mathcal{M}_{min}, \mathcal{M}_{max}]$ focused on the maximum gradient norm (the area of highest uncertainty).

3.  **Component C: Cross-Degree-Band Sweep**
    *   Unlike v1, which statically searched the Mossinghoff degree-band [cite: 14, 20], v2 sweeps dynamically based on gradient hints. If the gradient field points toward higher degrees, v2 seamlessly bridges across degree bands (e.g., $d \in [cite: 12, 13]$), optimizing coefficient bounds dynamically using Smyth's bounds and Breusch's lemmas [cite: 19, 21].

4.  **Component D: Enhanced Kill Patterns**
    *   `prediction_was_in_excluded_cyclotomic_band`: Triggers when the gradient field predicts a high-probability zone that is mathematically proven to consist solely of cyclotomic extensions of known low-measure polynomials.
    *   `region_too_sparse_for_test`: Triggers when the target Voronoi cell lacks enough surrounding data points to compute a valid discrete gradient, indicating a need for randomized parameter sampling (similar to techniques used in CodeScientist) [cite: 15].

***

## 5. Post-Success Protocol for Substrate-Grade Discoveries

If G18 `g18_lehmer_v2` successfully identifies a polynomial $P(x)$ such that $1 < \mathcal{M}(P) < 1.17628$, it has discovered a minimal counterexample that fundamentally refutes Lehmer's conjecture. This is a substrate-grade mathematical event. To ensure mathematical rigor and prevent hallucination-based false positives, a strict post-success protocol must be executed.

### Phase 1: Local Triage and Exact Verification
1.  **Symbolic Re-evaluation:** Floating-point approximations are entirely discarded. The roots of $P(x)$ are isolated using Sturm sequences with exact rational arithmetic.
2.  **Galois Group and Irreducibility Verification:** $P(x)$ is rigorously proven to be irreducible over $\mathbb{Z}[x]$. The Galois group is bounded to ensure it conforms to Amoroso and David's parameters for non-cyclotomic minimal measures [cite: 19].
3.  **Interval Arithmetic:** The Mahler measure is computed using arbitrary-precision interval arithmetic to guarantee that the upper bound of the interval for $\mathcal{M}(P)$ is strictly less than $1.17628000$.

### Phase 2: Formal Verification
1.  **Auto-Formalization:** The steps proving irreducibility, root locations, and Mahler measurement are translated into a formal proof script for the **Lean 4** or **Coq** interactive theorem provers. 
2.  **SMT-Solver Cross-Check:** Utilizing SMT paradigms akin to those in Isolde and CEAM, the polynomial coefficients and roots are formatted as a Satisfiability Modulo Theories assertion to mathematically prove that no cyclotomic reduction exists [cite: 1, 7].

### Phase 3: External Audit and Embargo
1.  **Cryptographic Commitment:** A SHA-256 hash of the polynomial coefficients and its exact Mahler measure is published to a public ledger or preprint server (e.g., arXiv) to establish chronological priority without revealing the counterexample.
2.  **Independent Reproduction:** The Lean 4 proof is distributed to an independent verification cluster (e.g., utilizing an agent like Aletheia for automated proof-checking) [cite: 3]. 
3.  **Human Review:** Once the automated theorem provers certify the `.lean` file, the plain-text polynomial is released to the mathematical community for peer review, fulfilling the ultimate requirement of algorithmic transparency [cite: 2, 15].

***

## 6. Contrarian Perspective: G18's Bias Towards Known-Open Conjectures

### The Steelman Argument: Structural Limitation to Famous Conjectures
G18 MINIMAL-COUNTEREXAMPLE fundamentally operates by tracking the `modal kill_pattern` and utilizing gradient computations on `kill_pattern` frequency surfaces [cite: 6]. This methodology intrinsically requires a massive, pre-existing landscape of data. 

For famous, heavily researched conjectures like Lehmer's Conjecture, the Riemann Hypothesis, or the Birch and Swinnerton-Dyer (BSD) Conjecture, the mathematical community has spent decades generating boundary conditions, near-misses, and limit points [cite: 4, 22, 23]. For Lehmer's conjecture, Mossinghoff, Boyd, and El Otmani have provided vast tables of polynomials with Mahler measures slightly above $1.176$, mapping out a dense "kill-density" topology [cite: 21, 23]. G18 thrives here because it has thousands of data points to generate Voronoi cells and compute reliable gradient vectors.

Conversely, for obscure, recently formulated, or highly niche combinatorial conjectures, the mathematical catalog is practically empty. There is no historical `kill_ledger`. The Voronoi tessellation consists of a single, infinitely large cell. The gradient of the frequency surface is flat (zero). Because G18 relies on the failures of previous searches to predict the location of a counterexample, it is completely blind in a zero-shot environment. Therefore, G18 is structurally biased to only fire on famous, high-density unverified claims.

### The Enhancement: "Agentic Substrate Seeding"
To open G18 to obscure conjectures, we must synthesize the missing kill-density landscape. We achieve this by integrating the generative capabilities of neural-guided synthesis frameworks like Aletheia [cite: 3] and AlphaEvolve [cite: 2].

**The Enhancement Pipeline:**
1.  **LLM-Driven Adversarial Mutation:** When given an obscure conjecture with no prior search history, an LLM acting as a semantic mutator (akin to AlphaEvolve's methodology [cite: 2]) generates hundreds of slightly weakened or relaxed variants of the original conjecture [cite: 9]. 
2.  **Synthetic Refutation:** A fast, shallow SMT-solver pipeline (like Isolde [cite: 1]) is deployed to quickly find trivial counterexamples to these weakened variants. 
3.  **Topological Seeding:** The properties of these synthetic counterexamples to the weakened conjectures are logged into the `kill_ledger`. 
4.  **Gradient Bootstrapping:** These synthetic data points act as the initial "seeds" for the Voronoi tessellation. Even though they do not refute the main conjecture, they create a synthetic topological gradient that points G18's search heuristic toward the most mathematically complex, unstable regions of the discrete catalog [cite: 6, 15].

By artificially seeding the substrate through neural-guided variant refutation, G18 transforms a barren, obscure conjecture into a rich, navigable gradient field, enabling the discovery of minimal counterexamples regardless of a conjecture's historical fame.

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbLSfTpSEdhTw7or8f6CMmv4GM2GpptDpqwflY7Xl-iOh_EGELx_tP-8CrQYH78fegSVmqKJjZXgfrrA_Hq-DznxYNiKujKd0p3HStj-Ksme3SjKyXJDMnJM-6Q1ixChwO62FzdnorttSJk21LMRhRRYJBnn6z82m77xBUa03mcxKtHkCepvsbq4orzPXU1Lz9uxoXdAmotU5ES7h6IdDBVxs=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmYQW8dJbkkIGxTE-9Tt-ou_8Wd0qcYRziWusqj3reZreKrmwmf5zmYJafTZA-66c7Nxxu6SoeZQ6fLslqsAWhm-eu2IfZdn_M55276Ls6XcUGjPi4)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFv7Tw4qFeAuOZllewkkZjmCm1gTLIcZjCYOBC8KA9xjSh-XNFIvpdzcYcHFdj7-bBvz0M7cyp5IcKC8SnlFhFZhxxzGWUR_4xJKlbJhgMlE8yWnPwZ_6_m)
4. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8r-ByZbL9M-ijfG_SBi0EqcpObpsk_M-sIZKGmle7CkadqyqiX6A3LT2dKiKP3XPLqWDjehSfEy9tl2_dRqUs1n9w2I9wmxpX5r8EYztghvBaPqfdZ9dOzDTKMw3hDQSGXndj08iOOw==)
5. [uni-goettingen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrXd2fjf54pkwpH9kLyfCzqFQqRLNWGGhnk4wWk5xf1doPTuBPMCs2uMvtmTCQ-8MA_07T9qqkRikxE9yv6nNPlfzIUv1ysyKJi1FOSI0mhB3-vsm7trimD_HzqEt_ovGa2hjqdJknfxF9KWlJkBRjk2jZptQYu5SDCigeH2nRGMez2GfT5aHHO8gpdap2CDNwD5Bz3brL0yNSw9Ks7BRexi-H8G0=)
6. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmX1RJnlSV20u0fFIJHWMJX6evxEnQVoVyH8kJHmQkp00iDn6laQKAxNDWIwQltlssSmBY4GjC3hoH_rOpOLnHc8DpDLtY1ym0KdeWE2CVSM59p230jkMoIOxX5YRW)
7. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3VxY4blM2WAtxU7ucEJHG33QCdy_e3kTWiWHObYfWuCyvU8MYVuERJAPPVJX_Rus2KXKawxegKd9BQeof85GJ8CgbmvMIfw1pXmpMDyxCEhvCIuY0VOZJQMz4kKL-RO8dcGZu2PzMe5L1YfYocmK-ldsVL7TQ_EXhJTbU-A7h1vWjmgsmhoi0ww==)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYrKY8bM0nx3EORj1hR4FmGjrb2nn36mATuIi_UvYgjjvtX5iaseygQgWRtbcyVy6yN-YpJbEvxsv7XYYPCqOX_muVqOd7Z1dZqrdagtfeu9FXmxNWacM45h1oth_aEyRyk51i6V5-RoO7gYOaQpgHpHmKsSabUKpZk8inemTg8AXFvYS_a2J9cbnZMO2WpTUAyD1py7TdK7FVfFomTLmUlJmAF8DC0jVsfo7ocAAT3Js=)
9. [rewire.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQRwatJBENCjk_U8ZXRkk76UKLJ_UXgCf47jfWZHvT7nqXB2k-aQLbKNwck3VtOlb57-I2rFJ5MqvOTFskjx_oSbJItI0_MRFuom4TTQbpaOa3h3DRhAP2kdFFFhJ_Pa0xVPTW8fjCjsoBOe7QmE-AmL9NJxkuXLd7louBtHCTSIE_CSa3)
10. [deepmind.google](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhJERDTynMy2-LwObL5EaB46zHZ31HWLmMMNWYwYrZc-yNs1OcoGAoxwn7djgYdqQjhSXBD9hwdJG0sWHCAxpfwIaTgDDel1uFlCe0D2KlROMZWoQ6rVC8lQCeMlBmaansO15RnwnoH-qjwbxWNpAoWOZK8meesWEzXlz3goGUmz5vp1_V5x_EnEtkr2S6ZSv727KLOCip7csmJV1uCA==)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNspDjz-RMikB1s4w3SeqKDwr_wFpdyhfKD-7Lj4fI3V3TOgmAFmgIOPiYwritRnPilbYLrDDEqPMVnkdwn6jRrEuubQKV8lPixYOzAQl1trY5HPRItW7JZeLgk-sDjaKbG90E-QXzp55YZYn2MyLsEWXJB963cRNUq9ix8Q-VpcJ-n7fJIe0-4nvsN3tolVFmBce1gHxRgx8dC12jnJxcens9lsxsD3iiR9_ZHrWArOUZWRu3cbWJZXw=)
12. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJDHdXFfLVesXjbv1LSWiW8YiAHi2mXKucPbhMFvhB1P0GB-W4dmAgiEwA1mRDJit0Nd99V21f6ezGCwvvcUQzx1X8oWfjXDdPh3VLbX-fRPfCY3duZe6U6La4JLE=)
13. [deepmind.google](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSVcZnhFAw-EGEk9tl82lzlPpp2TFwA9cbNBOtMDmyLM7UqVyiYq-6AQ6urE34fS0Lu0ZAdrWh2RzCyarOzDv2tj42M84znN4esF25mnwOu9D2bwwZkrdlKkfvlE_PbZDHmAci7cc87DFJdA3AxVY3hfilv2_SUDWpkjZ82ITTd4pSVHetx27d8vK7mnA8Re_6xjpZAN9mueTAJQY=)
14. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0axBCxko-tIChV8yV7iOKeVNMVd5jz8LLJlhNcdVCy5cRMmJHw91Q32seldRWmf2W_TIL3cXLcg8DgaxC4P4wA3thbeor__31pvbvK3qe_3FtkEZvXrU7Bc8wSzZdgznDJ_s=)
15. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkINLk-TQbtnJY_wB2lONtg7mGeF1Rc21KyGCniZw13SkJMluZ9UUqo4FT6ZgCEUj-GCANyMdZMu_qnl-y3aQntbxo7R5dJB-tGO_MW3hPpJ539xjOFznbHVgBcv4DYo0ARCfM)
16. [learnprompting.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-2d9KIczpKoH-HDYoF9oGXKwLNM_oHla-uoTIgldcpoungJEPY0vnh_gHcMor36lIFUkJoSQHhVneE2LZoGJaVZEoxjkdoxdGm76E7ZcjsPw0qwi6u5DrWZL3kLqsmrsk3pZ2TQkE)
17. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGa8Bqwd6IIC5jjgD3rnBSXM8srQlMZgAAHMoFCUzg8ukGGTYBPSGPkerPkSQs9YFrG1ncD5mShIGIkr8VXzz2_1JN71-mz2BXCVmferaJPv7jGpXvPoFT3FqZOUktU_w6-3OZmr4TcgeRO5npvhWGWBLQx-7XvAPA7U1Cyk0bjF_yraFZk15GHAc01Ado26tBwdJqPLW13aqHpSRPGkLxavDdGkUzhehHLTN66D1LmAxqN_jMkaISzfKL8yjbXChf-VRpr-xCssAY=)
18. [sciprofiles.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFx2NNRld_xEafSniBXenRN5sdGs9Db_WN-ZoTzhPZ5HxB3-2Jug7lVVOLugNyfJd8Gx29CuL1GlSO9uSHS6hU6cdP_6a9j1kupALsYoy5Mqx7rMPMEo1R4ZtFPvQ==)
19. [wisc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF44l2iNFIC8DWRLrhaMJVVKvU0XPWxAQB0AT_dOPfp9Fn4v9lZsLN_Nmtc8Q1fCG4nn15g4NpkE2YFrjMVHovLRLv-mqFB6Oclyns_x-WoKfm86Ic9X3_FFgVWzVYtzxraCl98NwTBXa97)
20. [sfu.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGvLS4WQMRSzUT_gmTIok-iOtXvpjfllP3JywtI1bn7R5MiqNtPy4na48irV7X7bkzlg--TswJsrUxKcGUxfWpvyOQsBNBxPlIe44r9hNgD4URTSwaTVGRx36JFZym2DY9RCM=)
21. [bau.edu.lb](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4YPj0F4frrBtUG42U2otyiDr6QOeMus_B_kMGpjE7gmoTQXJA7HD1aTKauf7ZVtZqyhJZ39P1k3VGx9rr4rxmbELwl0zqMavAtR67aGiHoVesGGmvVtSbMvSE41BScrBT4uXo6EoJksptUwhx_FHiyNRS3MEK0DAYf3bFix954wRx5LFneR9aqw==)
22. [zenodo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSZxWyIrI31aR3oS2lDN0pSkcUm5-J-dlgWSjqeX0N9MoosHFiKNIZZc2IOUpZFAd3loAwfUZA5FRWcaWprlWZmCQuuI4jb1O3SqpXOIXB4P6b2e5mRutbUnqCCwaFV1FjAoUW6ULojv_-3GYOfYAPOAbtx3Tzf6OT66rAK4gtloiMl5NS6LXr8SNE7P7YluCj153wXk2Xgf5kkxNL93Y7n3mtHApduBCOXqVRO0M_WTWP9igO4vLn9i3mjlvcSbdlVfNPS3H6my7h60Tu)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTdYWXluzIQufSdL_I33g8WjX6ok8aNSTDb4f_6MwcQfI878JMrsQ4PXEaRZl8WsXnljdCqfZ6uFeuNMkhXGs-_SYjTGlSdBzeAXQsWZ63gWm0BmrZpCcYTJvLy88rhAAAglh9mVxjq9if0_l2ZSuPMpwtXErh4YRpXnJTvcaI7U8XBBOcj4Kbeb2vXpM=)

