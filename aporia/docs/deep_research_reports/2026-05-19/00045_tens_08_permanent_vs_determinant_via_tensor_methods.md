# TENS-08: Permanent vs determinant via tensor methods

**Pythia queue id:** 45
**Tier:** T1
**Priority:** 1
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdGeThNYXRqM0V1S3MxTWtQNXFidjRBcxIXRnk4TWF0ajNFdUtzMU1rUDVxYnY0QXM
**Elapsed:** 249s
**Completed at:** 2026-05-19T09:40:33.196754+00:00

---

# The Permanent vs. Determinant Problem: 2024-2026 Advances via Tensor Decomposition, Secant Varieties, and Tensor Networks

**Key Points**
*   **The core mathematical mystery:** Research suggests that computing the "permanent" of a matrix is inherently vastly more difficult than computing its "determinant," a distinction formalized as Valiant's conjecture (algebraic $\text{VP} \neq \text{VNP}$).
*   **The tensor geometry approach:** Evidence leans toward the idea that viewing these mathematical polynomials as high-dimensional geometric objects (tensors) can expose their fundamental complexity.
*   **Recent breakthroughs (2024-2026):** Mathematicians have recently pinpointed the exact tensor complexity of small determinant and permanent matrices (up to $4 \times 4$), completely separating them using advanced linear algebraic methods known as "recursive Koszul flattenings."
*   **Debordering the limits:** It seems likely that "debordering" techniques—methods that strip away the limits of infinite approximations—will be crucial for finally resolving the discrepancies between exact computational models and geometric boundary models.
*   **Tensor network constraints:** Advanced theoretical computer science in 2024-2026 indicates that contracting "tensor networks" (a method of simulating complex computations) hits an exponential wall for problems like the permanent, reinforcing the belief that the permanent is intrinsically hard to compute.

**What is Valiant's Conjecture?**
In computer science and mathematics, there is a famous open question about whether certain problems that are easy to verify are also easy to solve ($\text{P} \neq \text{NP}$). In 1979, Leslie Valiant proposed an algebraic version of this problem. He looked at two mathematical operations on matrices that look almost identical: the determinant and the permanent. The determinant can be computed very quickly (in polynomial time), while the permanent appears to require an exponentially long time as the matrix grows larger. Valiant's conjecture formally states that there is no efficient way to rewrite the permanent as a small determinant, meaning the complexity classes they represent (called $\text{VP}$ and $\text{VNP}$) are strictly different.

**The Role of Tensors, Secants, and Networks**
To prove that the permanent cannot be easily computed, modern mathematicians translate polynomials into "tensors"—multi-dimensional arrays of numbers. By studying the geometric shapes these tensors form (such as "secant varieties"), researchers can measure how "complex" a tensor is based on its "rank." Recent papers from 2024 to 2026 have approached this by looking at "border rank" (how close a simple tensor can get to a complex one) and "tensor networks" (graph-based structures representing multi-linear computations). Together, these tools provide the most promising pathways to finally proving Valiant's algebraic hypothesis.

***

## 1. Introduction to Algebraic Complexity and Valiant's Conjecture

The investigation of computational hardness in algebraic models of computation centers largely on the comparative complexity of two classical multilinear polynomials: the determinant and the permanent. Introduced by Leslie Valiant in 1979, the algebraic complexity classes $\text{VP}$ and $\text{VNP}$ serve as the algebraic counterparts to the boolean classes $\text{P}$ and $\text{NP}$ [cite: 1, 2]. Valiant's celebrated hypothesis, $\text{VP} \neq \text{VNP}$, posits that the permanent polynomial cannot be computed by polynomial-sized arithmetic circuits, despite the determinant admitting efficient polynomial-sized computation [cite: 1, 3]. 

### 1.1 Determinantal and Permanental Complexity
Valiant demonstrated that the permanent is $\text{VNP}$-complete, meaning any proof that the permanent requires super-polynomial circuit size would definitively separate $\text{VP}$ and $\text{VNP}$ [cite: 1, 2]. This is typically formulated in terms of **determinantal complexity**, denoted $\text{dc}(f)$ for a polynomial $f$. The determinantal complexity of the $n \times n$ permanent, $\text{dc}(\text{perm}_n)$, is the minimum size $N$ of an $N \times N$ matrix whose entries are affine-linear forms in the variables of the permanent, such that its determinant exactly equals the permanent [cite: 1, 4].

If $\text{VP} = \text{VNP}$, then $\text{dc}(\text{perm}_n)$ would grow polynomially with $n$. Conversely, proving that $\text{dc}(\text{perm}_n)$ grows super-polynomially would prove Valiant's conjecture [cite: 4, 5]. Despite decades of effort, the best known absolute lower bound on the determinantal complexity of the $n \times n$ permanent remains quadratic, specifically $\text{dc}(\text{perm}_n) \geq n^2 / 2$, a breakthrough achieved by Mignon and Ressayre in 2004 using the geometric properties of hypersurfaces defined by the vanishing of the determinant and permanent [cite: 4, 6].

### 1.2 The Geometric Complexity Theory (GCT) Paradigm
To breach the barriers preventing super-polynomial lower bounds, Mulmuley and Sohoni introduced the Geometric Complexity Theory (GCT) program [cite: 5]. The GCT program shifts the focus from exact computation to geometric degeneration, utilizing the representation theory of algebraic groups [cite: 5]. Rather than studying the exact determinantal complexity, GCT often looks at the **border determinantal complexity**, which allows for arbitrary infinitesimal approximations of the permanent by the determinant [cite: 4, 7]. In this framework, the permanent and padded determinant are viewed as points in a vector space of homogeneous polynomials, and the goal is to find "representation-theoretic obstructions"—witnesses that prove the permanent's orbit closure is not contained within the determinant's orbit closure [cite: 4, 5].

From 2024 to 2026, the intersection of algebraic complexity and tensor geometry has seen a surge of novel methodologies. Researchers have increasingly focused on tensor decomposition techniques—evaluating tensor rank, border rank, Waring rank, and utilizing secant varieties—to strictly separate the complexity of the determinant and the permanent [cite: 8, 9].

## 2. Tensor Decomposition: Rank, Border Rank, and Waring Rank

A fundamental strategy to evaluate the complexity of multilinear maps like the determinant and permanent is to embed them into tensor spaces. The $n \times n$ determinant and permanent can be viewed as specific tensors, and their structural complexity can be quantified via various notions of tensor rank [cite: 8, 10]. 

### 2.1 Formal Notions of Tensor Rank
Let $V_1, \dots, V_d$ be finite-dimensional vector spaces over a field $\mathbb{F}$. A tensor $T \in V_1 \otimes \cdots \otimes V_d$ has **tensor rank** $\mathbf{R}(T)$ defined as the minimum integer $r$ such that $T$ can be expressed as the sum of $r$ rank-one tensors (pure tensors) [cite: 9, 11]. That is, $T = \sum_{i=1}^r v_1^{(i)} \otimes \cdots \otimes v_d^{(i)}$.

For symmetric tensors, which correspond naturally to homogeneous polynomials, we study the **Waring rank**, denoted $\text{WR}(f)$. The Waring rank of a homogeneous degree-$d$ polynomial $f \in \mathbb{C}[x_1, \dots, x_n]$ is the minimal number $r$ such that $f$ can be written as the sum of $r$ powers of linear forms: $f = \sum_{i=1}^r \ell_i^d$ [cite: 12, 13]. The evaluation of these ranks is historically tied to classical algebraic geometry, specifically the study of secant varieties of the Veronese and Segre embeddings [cite: 5, 14].

### 2.2 Border Rank and Semicontinuity
Because tensor rank is not lower-semicontinuous in the Zariski (or Euclidean) topology, a sequence of tensors of rank $r$ can converge to a tensor of rank strictly greater than $r$. This gives rise to the **border rank**, denoted $\underline{\mathbf{R}}(T)$ [cite: 5, 11]. The border rank is the minimal $r$ such that $T$ lies in the Zariski closure of the set of tensors of rank at most $r$. Equivalently, it is the smallest $r$ such that $T$ can be approximated arbitrarily closely by a sum of $r$ rank-one tensors [cite: 11, 12]. 

Similarly, the **border Waring rank**, $\underline{\text{WR}}(f)$, is defined as the smallest $r$ such that $f$ can be written as the limit of a sequence of polynomials $f_\epsilon$ with $\text{WR}(f_\epsilon) = r$ [cite: 5, 12]. A deep connection exists between border Waring rank and geometric complexity: any polynomial that can be approximated arbitrarily closely by low-complexity functions itself has low border complexity [cite: 7, 12].

## 3. 2024-2026 Breakthroughs in Exact Tensor Rank Separations

One of the most direct ways to compare the determinant and the permanent is to analyze their exact tensor ranks. For years, determining the exact tensor rank of specific polynomials like the $3 \times 3$ or $4 \times 4$ permanent has been an open problem [cite: 6, 15]. However, recent literature from 2025 has yielded exact separations using advanced linear algebraic methods.

### 3.1 Recursive Koszul Flattenings (Han, Ju, Kim, 2025)
In a landmark 2025 paper, Han, Ju, and Kim completely separated the determinant and permanent tensors by their tensor ranks using a method known as "recursive Koszul flattening" [cite: 9, 16]. 

Flattening a tensor refers to reshaping the multi-dimensional array into a matrix. The rank of this resulting matrix provides a trivial lower bound on the tensor rank [cite: 9]. However, for symmetric or highly structured tensors, standard flattenings are often insufficient. The Koszul flattening method, introduced by Landsberg and Ottaviani, uses Koszul complexes to define linear maps whose ranks yield much tighter lower bounds [cite: 9, 17]. 

Han, Ju, and Kim extended this via *recursive* usage of Koszul flattenings, originally suggested by Hauenstein, Oeding, Ottaviani, and Sommese [cite: 9, 17]. This recursive Koszul flattening method is particularly effective for tensors of order 4 or higher [cite: 9]. 

By applying this technique, the authors proved several powerful theorems:
1.  **Exact Rank of the $4 \times 4$ Determinant:** They determined that the exact tensor rank of the $4 \times 4$ determinant tensor over an arbitrary field of characteristic $\neq 2$ is exactly 12, $\mathbf{R}(\det_4) = 12$ [cite: 9, 16].
2.  **Exact Rank of the $4 \times 4$ Permanent:** Conversely, they established that the exact tensor rank of the $4 \times 4$ permanent tensor is 8, $\mathbf{R}(\text{perm}_4) = 8$ [cite: 9, 16].
3.  **General Lower Bounds:** They established that the lower bounds for $\mathbf{R}(\det_n)$ completely separate the determinant and permanent tensors by their tensor ranks [cite: 9, 16]. The recursive Koszul flattening provides a map where the rank evaluation strictly delineates the growth rates, providing explicit algebraic witnesses to the complexity gap at small scales [cite: 9, 18].

### 3.2 Border Rank of the $4 \times 4$ Determinant Tensor
While the exact tensor rank of $\det_4$ was resolved to be 12, understanding its topological closure (the border rank) presents a distinct challenge. Another 2025 preprint by Han, Ju, and Kim focused exclusively on the border rank of the $4 \times 4$ determinant tensor over $\mathbb{C}$ [cite: 11]. 

Using the fixed ideal theorem introduced by Buczyńska and Buczyński, and the method of Conner, Harper, and Landsberg, the researchers established that the border rank $\underline{\mathbf{R}}(\det_4)$ is at least 12 [cite: 11]. Because the exact tensor rank provides a trivial upper bound on the border rank ($\underline{\mathbf{R}}(T) \leq \mathbf{R}(T)$), and previous explicit decompositions showed $\mathbf{R}(\det_4) \leq 12$, this conclusively proves that the border rank is *exactly* 12 over any subfield of $\mathbb{C}$ [cite: 11, 19]. 

This is a critical milestone because it demonstrates that, at least for $n=4$, the determinantal tensor does not suffer from a "border rank gap" (where border rank is strictly less than exact rank), which often plagues algorithmic design in matrix multiplication tensors [cite: 7, 11].

## 4. Secant Varieties and The Geometry of Border Rank (2024-2026)

To understand border rank globally, one must study secant varieties. The $r$-th secant variety of the Segre variety of rank-one tensors, denoted $\sigma_r$, is the Zariski closure of the set of all tensors of rank at most $r$ [cite: 11, 20]. If a tensor $T$ has border rank $r$, it lies on $\sigma_r$ but not on $\sigma_{r-1}$ [cite: 20].

However, the geometry of classical secant varieties is notoriously difficult to analyze due to deep singularities. Specifically, $\sigma_{r-1}$ forms a "black hole" inside $\sigma_r$: at any point $[T] \in \sigma_{r-1} \subseteq \sigma_r$, the tangent space is the entire ambient space, destroying meaningful local geometric information [cite: 20, 21]. 

### 4.1 Concise Secant Varieties (Jagiełła & Jelisiejew, 2026)
To bypass the singularity barriers of abstract secant varieties, Jagiełła and Jelisiejew (2026) introduced a novel mathematical structure termed **"concise secant varieties"** ($c\sigma_r$) [cite: 20, 21]. 

Informally, concise secant varieties serve as modular partial desingularisations of secant varieties to Segre embeddings [cite: 20, 22]. A tensor $T \in V_1 \otimes \cdots \otimes V_d$ is "concise" if the linear maps induced by $T$ into any of its factors are surjective. The concise secant variety $c\sigma_r$ is a projective variety that is birational to the abstract secant variety, but crucially, each of its points corresponds explicitly to a concise tensor of the appropriate border rank (a minimal border rank tensor) [cite: 20].

The geometric advantage is profound: the geometry of $c\sigma_r$ at any point is smoothly equivalent to the geometry of $\sigma_r$ at a concise point [cite: 20, 21]. This eliminates the "black hole" singularities present in traditional secant varieties. 

### 4.2 Unrestrictions and Border Rank Lower Bounds
Jagiełła and Jelisiejew's framework utilizes "unrestrictions." They provide a characterization of tensors with border rank $\leq r$ as unrestrictions of minimal border rank $r$ tensors [cite: 20, 21]. In the context of algebraic complexity theory, this modular setup is highly applicable to lower-bound proofs. 

As noted by the authors in their open problems, concise secant varieties apply directly to proving lower bounds for border ranks of structured tensors [cite: 20, 21]. By transitioning from the abstract secant variety $\sigma_r$ to the well-behaved concise secant variety $c\sigma_r$, researchers can evaluate rank methods (like Koszul flattenings) on spaces where the tangent space weights and algebraic boundaries are well-defined and avoid catastrophic singularities [cite: 21]. This is considered a highly promising path for establishing super-polynomial lower bounds on the border rank of the padded permanent [cite: 20, 21].

## 5. The "Debordering" Phenomenon in Valiant's Conjecture

A significant hurdle in the Geometric Complexity Theory (GCT) program—and algebraic complexity generally—is the topological closure itself. Border complexity measures rely on limits. If GCT proves a lower bound on the *border* complexity of the permanent, does this translate to a lower bound on the *exact* circuit complexity? This translation task is called **debordering** [cite: 7, 12].

Debordering seeks to prove an upper bound on a non-border complexity measure in terms of a border complexity measure, effectively getting rid of the mathematical limits [cite: 7]. Debordering is at the absolute heart of understanding the difference between Valiant's original determinant vs. permanent conjecture ($\text{dc}(\text{perm})$) and Mulmuley and Sohoni's variation which uses border determinantal complexity ($\underline{\text{dc}}(\text{perm})$) [cite: 7, 13]. 

### 5.1 Debordering the Border Waring Rank (Dutta et al., 2024)
Until recently, very few debordering results were known, and most suffered from extreme combinatorial explosion [cite: 7, 12]. In a pivotal paper at STACS 2024, Dutta, Gesmundo, Ikenmeyer, Jindal, and Lysikov studied the question of debordering the border Waring rank of polynomials [cite: 12, 23]. 

The authors achieved a major breakthrough: they obtained a Waring rank upper bound that is exponential in the border Waring rank, but crucially, **only linear in the degree** of the polynomial [cite: 7, 12]. Prior to this work, all known debordering results were exponential in the degree itself, rendering them practically useless for high-degree multilinear polynomials like the $n \times n$ permanent (which has degree $n$) [cite: 7].

Specifically, if a homogeneous polynomial $P \in \mathbb{C}[x]$ of degree $D$ has border Waring rank $\underline{\text{WR}}(P) = k$ (where $k < D$), Dutta et al. proved that:
$$ \text{WR}(P) \leq \frac{2^k \cdot (2k - 1)}{k - 1} \cdot D $$
[cite: 23]. 

For polynomials with constant border Waring rank, this theorem implies an upper bound on the exact Waring rank that scales linearly in the degree $D$ [cite: 7]. Previously, such a linear-in-degree bound was known exclusively for polynomials with a border Waring rank of at most 5 [cite: 7, 12]. 

### 5.2 Implications for Kumar's Complexity and Product-Plus-Power Models
The debordering result intersects with recent findings regarding Kumar's complexity model. Kumar (2020) demonstrated a surprising result that a small border Waring rank implies the polynomial can be approximated as a sum of a constant and a small product of linear polynomials [cite: 5]. In a 2025 paper by Jindal et al., the authors proved the converse of Kumar's result, establishing a tight connection between border Waring rank and Kumar's model of computation, yielding a new formulation of border Waring rank up to a factor of the degree [cite: 5]. 

The debordering of Waring rank limits the "gap" that limits can provide in computation models. By proving that topological closures do not grant infinite computational power (bounded exponentially by rank but only linearly by degree), theorists can map GCT border lower bounds directly back to Valiant's exact classical complexity classes ($\text{VP}$ vs $\text{VNP}$) without losing the super-polynomial separation [cite: 12, 23].

## 6. Tensor Networks: Graph-Theoretic Complexity and \#ETH (2024-2026)

While secant varieties and border rank evaluate the static geometric properties of the permanent and determinant, **tensor networks** model the dynamic computation of these mathematical structures. A tensor network represents a complex entangled structure through interconnected low-dimensional tensors [cite: 24]. Contraction of a tensor network corresponds to evaluating polynomials, quantum circuit amplitudes, or partition functions [cite: 24, 25].

### 6.1 The Exponential Complexity of Tensor Network Contraction
Evaluating the permanent of a matrix is a canonical $\#\text{P}$-complete problem. If one attempts to construct a tensor network to compute the permanent of an $n \times n$ matrix, one will quickly run into the graph-theoretic barriers of the tensor network model [cite: 26, 27].

In a comprehensive 2026 study, Liu established a unified complexity framework for tensor network contraction [cite: 24]. The computational complexity of contracting a tensor network depends crucially on the underlying graph's separator properties (e.g., planar graphs, finite element graphs, and $H$-minor-free graphs) [cite: 24, 28]. Liu developed edge separator theorems yielding sub-exponential contraction algorithms for certain minor-free topologies [cite: 24, 29].

However, for completely dense or highly entangled networks required to compute symmetric Holant problems or $\#\text{P}$-hard counts (like the permanent or the matching polynomial), the runtime scaling is highly restrictive. Liu proved that under the **Counting Exponential Time Hypothesis (\#ETH)**, a sub-exponential time lower bound firmly holds for contracting these dense tensor networks [cite: 29, 30]. Specifically, there is no deterministic algorithm that can contract Boolean symmetric tensor networks of bounded dimension in $2^{o(N)}$ time for planar or minor-free graphs representing canonical $\#\text{P}$-hard evaluation problems [cite: 24, 31]. 

### 6.2 Treewidth, Pathwidth, and the Barrier of the Permanent
The performance of tensor network contraction algorithms is dominated by the **treewidth** (or linear rank-width) of the associated network graph [cite: 25]. The time and space complexities are strictly bounded by $2^{\mathcal{O}(w)} \cdot \text{poly}(m)$, where $w$ is the treewidth and $m$ is the number of tensors [cite: 25]. 

Earlier work by Austrin, Kaski, and Kubjas (revisited in recent 2024 literature) noted that while tensor networks can yield an $\mathcal{O}^*(2^n)$ time algorithm for the permanent of an $n \times n$ matrix, there are unconditional lower bounds [cite: 26]. Specifically, an $\Omega(2^{0.918n})$ time lower bound exists for computing the permanent via standard tensor network contraction [cite: 26]. Liu's 2026 results tighten this understanding by showing that even accelerating algorithms by transforming high-dimensional tensors into low-dimensional "gadgets" cannot bypass the $2^{\Omega(N)}$ lower bounds under \#ETH [cite: 24, 30]. 

### 6.3 Quantum Tensor Networks and Weight Enumerators
In quantum computing, tensor networks are employed to calculate the quantum weight enumerator polynomial (WEP) of stabilizer error-correcting codes. Cao et al. (2024/2026) applied the "Quantum LEGO" tensor network framework to this counting problem [cite: 32]. While tensor networks offer speedups over brute-force counting when the code has area-law entanglement (low treewidth), calculating the WEP (which scales similarly to the permanent in its \#P-hardness) remains computationally hard for general networks [cite: 32]. This reflects the same algebraic obstructions observed in Valiant's conjecture: structured, easily separable graphs allow polynomial-time evaluation (akin to the determinant), whereas highly entangled, dense connections require exponential contraction time (akin to the permanent) [cite: 24, 32].

## 7. Synthesis: Bridging Geometry, Rank, and Graph Theory

The concerted effort across 2024–2026 literature reveals a multipronged attack on the Permanent vs. Determinant problem. By viewing Valiant's conjecture through the lens of tensor decompositions, mathematicians have identified precise structural differences between the two functions:

1.  **Exact Algebraic Separations:** At small dimensions (like $n=4$), the recursive Koszul flattening method completely isolates the tensor rank of the determinant from the permanent [cite: 9]. The determinant tensor achieves higher maximal ranks ($\mathbf{R}(\det_4) = 12$) compared to the permanent ($\mathbf{R}(\text{perm}_4) = 8$), indicating fundamentally different invariant properties [cite: 9, 16].
2.  **Geometric Resolutions:** The introduction of concise secant varieties by Jagiełła and Jelisiejew provides a robust geometric scaffolding that bypasses classical singular "black holes" [cite: 20, 21]. This enables rigorous application of algebraic geometry to border ranks of dense tensors, paving the way for asymptotic proofs.
3.  **Collapse of the Border Gap:** Dutta et al.'s debordering theorems ensure that proving a lower bound in the continuous, topological limit (border Waring rank) guarantees a strict lower bound in the exact Waring rank, avoiding exponential blow-ups in the polynomial's degree [cite: 7, 12]. This rigorously connects the Geometric Complexity Theory approach back to the standard $\text{VP}$ vs. $\text{VNP}$ domain [cite: 5, 12].
4.  **Network-Theoretic Hardness:** Liu's work on tensor networks proves that the topological contraction of structures capable of generating the permanent requires exponential time under \#ETH [cite: 24, 31]. Unlike determinant evaluations which can be compressed into polynomial-time tensor pathways, the graph-theoretic treewidth of permanental evaluations fundamentally resists sub-exponential contraction algorithms [cite: 24, 25].

## 8. Conclusion and Future Directions

Valiant's conjecture, $\text{VP} \neq \text{VNP}$, remains one of the most elusive holy grails of algebraic complexity theory [cite: 1]. However, the state-of-the-art lower-bound techniques utilizing tensor decomposition have matured rapidly between 2024 and 2026. 

The successful implementation of recursive Koszul flattenings to lock down the border rank and exact tensor rank of $4 \times 4$ matrices represents a critical proof-of-concept for representation-theoretic rank methods [cite: 9, 11]. As researchers attempt to generalize these exact methods to asymptotic dimensions ($n \to \infty$), they will rely heavily on the non-singular frameworks provided by concise secant varieties [cite: 20, 21]. Furthermore, the debordering of the border Waring rank acts as a vital safety net, ensuring that findings in these geometric closures hold their weight when translated back to practical arithmetic circuit sizes [cite: 7, 12]. 

Simultaneously, the lower bounds proven in tensor network contractions under the Counting Exponential Time Hypothesis provide an unyielding computational argument: the permanent is inherently resistant to structural decomposition [cite: 24, 29]. Ultimately, the fusion of tensor rank bounds, secant variety geometry, and tensor network complexity provides a converging theoretical framework that, according to the latest research, brings the mathematical community closer than ever to finally resolving Valiant's determinant versus permanent problem.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzI41zq2Pxcy8lQgQe3-LnbWi3jTfpYUXy0wrHBa9VKt60MY7-qgq3gXrv-owQmI_aYEYyZWkz_hK2i001KIPLUTd_r24RH4s5OgztPUsxoi5BLYN7jQ==)
2. [theoryofcomputing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9OgBkGeQeoua54h0vah5uORJfPMoglk0r9DzlIwNWnXjO0YXLr6VWYcPOLlt8E_jjrOK-3gCQdd25zgycTKVv7JN5N31-inuoBwYL739o0_jzRuEr8NekfAZ8Jsn9T3YyTlWkdAEJGhsO3-o=)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7FoAjEZsu_u5FczkXa0hBMS5UKCEqxfN4TNHjbropb_Gg4XHWLtMCCDXdvQI_iVgNnwKBpBvtnGfWJa70zCSUsjIyZEqhajjDKxfbfNiGobtb-S20NDwOP5wL70tucKePxMxRITRuwQ8iZm1r3rE4dbZD31JrvgJ20OBTF_YFOm24)
4. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCmVpFG9scSaGA4a7lvwa7Kk7rr0cQzqtzyepK1djczRf8m7lR_8wJ_-d_UZZzP7HrzM37qTK5o5_FAdilBIuw6t8Z54CwKnmFFHoZKvXDLCD3oHq7UcUdv0vcEoE9rdUJYy146EoKv5DO_e3Nhn3N_8iwT62-bLCpuY9YQxlAWPh0uDobhBuuV7V1FNtQcfQ5AqPKrZFZtNyvfPyD3OHL4bg6iv005zljLaeoLooxFo9l)
5. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPp__yGGkVtphu5PUu-wqKaw_IJp6BbS3pGZU35bU_KvsG8SehyHg4OFxlgjNAolqQUWPrTpb4jIPcFWoNAJRqKQxWU-SyLHtTZYWOQeRm8iLjKTASAsJHJFqsYS0mGQbvvUQ6dVUchCU=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDI2elF9TV3EogM2bmRg-yCXaxL-6ZkXhV9-ImEM1lrTBHUoFnWz91lrv5-TQkBGWWqsomfFYA4wW3x6-8helRlYyfovKn5oWJpAGlCwKQ4k16VtbrrQ==)
7. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAhM_-ZqH31BxM8uhQAUvr_KfVaavpIMpKgketcqREtBa1zYt56VwE2AVllS5-I7Gul2lLV63iWJu97xL3sxmdUXK69BuaysMIGeQHUsXmLTfkg3gd6GdEA0RRBXaESl7GNnzFtOBVyMP6U5fSRcDx0jrP-MPACkyZix3ghSQ=)
8. [warwick.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRHmI5lSLf7ahuYDBI90fA6A-8ofoYBWKzuenmBhYDtKPEcjSPuPowsM3UnXVh98npsp2_jj_xa5YUjw3dCw64y1h1Igmk9reIvFRAaEaXHgWLBUPlYib3qyZfpeZYDCEjeifuqFpTXJvksVKo3dlSMCMOszfsW6zwoPolEcr0F34m28dRWydG)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExnYeKbYbV6G5SkT7Ef7DFc5rsa6moDaZAfk0QiyrMH7ifOK7ictRyYcPj9KWyqDFz1na0yna45j1otpU6f0E3wudp98-hGx6ziTMaSjQqslv7m0VOGQ==)
10. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1LKQ4AAqe2JW7__zKiaEqVewh5ENdQBqnOWAif6tToo_10NU7TdetKCay6RwGj78OFyjB85tz7wAWhU-kn4pHXmKoD8MVYnjdNhSqNpDcGJ2rSQkmNvmcwXYhBJUAd1ycVpfZCmOms8KBtBjRzUgbya-d-50ZLzQIYPXP4xofD1N01qUud8v-2JNDN3DIga824_JxBaysoeT_J1sQ16ySqAIfGkxicBfXxI61A6clvv5w5HRZRayNX4XHd1ePg09UsB3L5mtvniZbehxKwV62pnC0N1NsBWSw2Q953rFTt96U4t_2_7hLKkN6HDy5T_5TfTwnp-JvFtg=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE44ytPvTDLmuJzmwFKWA3eGCyDgFR8t2R7peLg5xURDgJJwlBhmD3syR8kBuOZeA6votUuOjy0nkAqWq37-3zzPOdz1BigqYmJv1HGl1nN-mJ5slJ9lA==)
12. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3SHp_ejHKug4Qg479BWtOsMuS9o_ifFLWzLvZcTi2krfQljmIhFr7gSlWjpe1_pkJymsZJSkEz_MS3KuHpqrIo8ip7VwZL9I6rvPW7VfDj7zvzWrd0XgXKfD8VBlUobavJk1tLBDcNVzpeY01YbEh1Vx1PV_D1vqlvOctvn6f8-2QN08to3grSfCjA-FGk5DeMvisndCGYB6hm3qU7kenyLO4E9Vi)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAf4YPQx6ydrGqcyXlYzsv4yQ38FTxNFgWpP5mvMBsNr8INVU0Nr71XShGAS0a8p-oc-3dfSkHfk1SKIlcMpFk54N8iE7akG16hlB1ihbFmHJ7pvn6kw==)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZdohE-48JWl8TvL5Gr5ngU_mSpx-Ix7sLQeIO8sGXGdoyoaCFZmVw1b1xRv6-uw8p4Dkn6dR0R3sl9Dg4bE2NNQ32N34qRJVyBSVwgr_Y3I1xPwSBcVyavr2B4so5JAtBmkynaS3p9ZGnkdTMUQoFOFI1bft1mdqgXVkyheoddHvm7fNOjEXm6oZqLeoLphT8RBqEwdxaQhO1QkLgBimw08CkYe6mMA==)
15. [mines.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETWj9q6QHxe9bCt1hthYAnjVE0oMK7DcQdie3TsAqOg-qF6UbLuosHLMaSri1KcuAQ8-ERf4BE3C3L6HjcyPxHnlF-e1RS1ksTJat1cN8L3nTXaX04VrmBU33WlYpPa0bo_6eP6HrL8mjCmHZWtyNF-IoQBSw3VCymT-G6-EpeWcDvClvK-hbcoiw29VNQpkjKOQN_g4aggTDT6fGcrBTe_eNZ-N45C5UqYey9DOPXh1MXw4QLdqKZVRLs)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvVDmiubSBFeVb9wXbwtKNBpispQvYDwJ765WPtqzq3k3dO9qcC6zXRrkZ3JYNekg6w3aG27r8pDM-Q3WQcSiV7JAfLDdl0IVdnaqqEMvEK9bjQXh31Q==)
17. [auburn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFc95gCkLzx0Y8V_A_asbwq7dGnHAQVKYZQ2rEEyTw8G6oOoPUbfaNO8gcYLKrKXQVgQw43Sk0kpJ24dqrkUbzk3OC77F67KXTrUGZJDf8q_MSC1wJF9Vff-a6c0NPKOGuc-R8RIag59KFQl4Q=)
18. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEijxk606u93NDGKZOntMjN0HADU9GvLbWOP-8zZ0HeAKB6vS3l3v8YzRc844UGnQyCY7jn7CMbVvXnxN580s-NScpNN4S271E7FTLcw_sOB3Glne0UsEersTHKe18hhYOa_9DNtD88b2MSL7GxlNATb6aiI8eqCt5q5ZDjxA_1TDkpvcFnnT1Gd51dpw3I1zmrRSLgZiPc4C8g-2Bi)
19. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEF5CxgKfeSpt2BoF6Ym96iomH2CXXPHV4me_gZbigbNPNatQLakjv0r4Fcs1E0uREmro4ajbLPjajaseqQwnCj-cpLfNVUfJttGJg_qYnVXD-GE6MRuJ3opALa4tDqkDpttQWJWhUksotH)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyHCq85FB9k_AJfIFlmNkErRaXduqp5KHlqprhy3UC_0uIgSIoRHkesAPJPAllurzEw8Ya13_V-lQ7HlXgl2TNq9UZMvAF4LEmj1-utPNLwWPzA-M-yA==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkOQI3tS5NhkmEfCTpvzh9ESBfFGLsjai0bClrNSX3H0YnRkLJWsRCNPXAJytOlId_STBt_5hpLm1Y_KKSsjzg3g1_0qKw6mWaQdueN8qtoNdNBnAWz5bo6A==)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHM3HKVNtVgbZkixnL4XUTGaq-O9Z7WSo7NGKBHB7vOCsVaU4z1tQ1Iy990j9p7u1RDdWxfQf2Zd9DxGkXNlL5mPuc7MKIpxpmJWqpIHGLikwGcXLkcdSeCVt4qAy9XQjkHq5dWKctte4UrV9lh)
23. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4lcgwNMobpRL95Y_mXRQnTh7HQ-noIgOfmmPWRXnCFbZG4kDx9C3de3gxLjNJlrfKyZcF0s7z3hVaZkv3SFqW5MoJH7Hd3yUVC5PAvp9B2Mihr0J0C4qMjoXDCmmCWjwrBjkFk6TFxO7haw4=)
24. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyLws3hZcQbyQIVC3Cli4YrCxeJKlaW2p_v-upRIW0zjpdrhd73sKQVCEvmy29615YmpN-uGMTb7s-B6ehvBiI1ZA58ZadqqpRoCdFuYYoRzKg5Y80meA1iRdPSj_xhe8PcMUTfdxd5ZIJb_OXbw==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQ1aUVvhen4jgtSIicPLcDteBx1dWkArbVSPYf59If5H5trdA_t0rjd9Fmk-fNMJqoXJgXrtw_HUnwE7n-tRWzpE6lSuO0olZkuZilqPv3LszytP9mdkXVEg==)
26. [kaiekubjas.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgyKYrp5nEsRJOzxCUXKBgFBF-cKu8areaj7k2CKrbTzvPlhTfVKbWx_JTLg04agxcnC0_rjWRHf0aVkhYobUX65GQ5D8aJwwxIAWV-Iiw6nk8Zbfc1TgrCKQmOYkt05Fe5KF4U3a1QJ9gKIMEL7_tkQ==)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXVCzjTp3UIhW-DnXQtIY_kk8FThg9sIpQJc_XzJR3fxqqrl1tAL3TBzU9s2r_TsWOw5TYcvI11pj81y5z07-wedURUzUDTPg7z2RmR6LdcPMjtpR7YhUbpX1y8Kfq4unuWcPwVo2tM0yEo9kotR1K6RNGJ4KdL6zy0ScTi3kFuLvwSzvEGAa52I28vrA978yZ-3LGgk8=)
28. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpOuL7fKafX6zgJm8Htx8hbupTHmyszXyNNyJfh-8PpXxa6C8AnasheSjnrU-S6IBlVBZKMaJx07LrCVsaMR5X90hQYtw8-dlBYn6-WElJ8X2Y6nknTGNYR20Sifod8FjqX9Idwy3XlErUSARG1hxu8BGeL7JUSwQ7fM2pxM4MQxvkaVdIPzpEbgQKOdZQJUeUkgu5blN1U5Y=)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3nxLOI8JBMIbFwyZz4ucGsB5JMTzn6kaY_iyZ-7mLPDBAhKQV8wLaMvBiduIPZMeEHrThdPrbm6Q6C4-bta5i6d_o03e4A-y5dAXT2UyYWOK6YeuFEsn9wQ==)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLjMK2dKUNXY6ZKsvUcHQH24GHNWrttLv8JTtux3GqjrqswB9-3Yr-V3IzEOe3gsBytqpLBZ0ajJ27DuD7S0AVC0c0gb2jIam1y5u_POJIpZD804lnXw==)
31. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHe-Z5SsTsFgOECjhb9qwtmgQHN4Q6ZVGzW5mmRuWDKyrit27vyeq6e03OQ8yw7NRXtPqteU40krfJ0bF8REusoQjLmaTvQ1SBXKRsUS7saYhhbTVOqdJ5TxOdguPIZ7jJowa5D6YkXrrtP1ZrYQnWP3HWHdvRqoafzh71rxkN7LWo3eme6SFQMq3sALJUhhZniIe988lySit2T4YGB03GVKzZtv6px)
32. [quantum-journal.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbKMjHf81Kvs5_XWHMB7XSUCSvSaJmHx0Kjb0ytkvG23svTt5OlSlKtjdj_eOoVrCJv1rbxmvipO8bexJnLglzZNESrdL73q6E-kCvU8fC7u9NKD1XekH_K6ZmVcQdkoIlXGzgwb8kq_baXg==)

