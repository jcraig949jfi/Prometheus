# Geometric flows beyond Ricci (mean curvature, Kahler-Ricci) 2024-2026 frontier

**Pythia queue id:** 220
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd4azRQYW92OUV0SFpqTWNQc1p5b3FBNBIXeGs0UGFvdjlFdEhaak1jUHNaeW9xQTQ
**Elapsed:** 250s
**Completed at:** 2026-05-21T18:32:33.004079+00:00

---

# Geometric Flows Beyond Ricci: The 2024-2026 Frontier in Mean Curvature, Kähler-Ricci, and Special Holonomy Flows

**Key Points:**
*   **Mean Curvature Flow (MCF) Breakthrough:** Recent mathematical work confirms the long-standing Multiplicity One Conjecture, severely constraining how singularities form in evolving surfaces.
*   **Kähler-Ricci Flow (KRF) Advances:** Proofs of the Song-Tian conjectures demonstrate that immortal solutions of KRF on manifolds with intermediate Kodaira dimension collapse to a canonical metric with bounded Ricci curvature away from singular fibers.
*   **String Theory and Non-Kähler Flows:** The Anomaly flow and $G_2$-Laplacian coflow have seen rapid advancement, establishing the geometrization of conifold transitions and new long-time existence criteria through integration-by-parts estimates.
*   **Yamabe Flow and Breakthrough Prizes:** The 2024 Breakthrough Prize in Mathematics celebrated monumental leaps in geometric flows, particularly concerning Yamabe compactness and soliton classifications.
*   **Algorithmic and Applied Geometry:** Techniques from continuous geometric flows are increasingly being discretized for computer graphics and even adapted for combinatorial optimization (e.g., the Traveling Salesperson Problem) via deterministic flow matching.

**Navigating the Post-Perelman Landscape**
The study of geometric flows—partial differential equations that evolve metrics or submanifolds to optimize their geometry—has been one of the most fruitful areas of differential geometry since Richard Hamilton introduced the Ricci flow in the 1980s. Following Grigori Perelman’s spectacular resolution of the Poincaré Conjecture using Ricci flow with surgery, the field has aggressively expanded to study higher-codimension flows (Mean Curvature Flow), flows coupled with complex structures (Kähler-Ricci, Chern-Ricci), and flows operating in spaces of special holonomy (the Anomaly flow, $G_2$-Laplacian flows). 

**The Current Era of Singularities and Solitons**
As we look at the 2024-2026 research frontier, the primary focus across all geometric flows has shifted toward rigorously classifying finite-time singularities and understanding the long-time collapsing behavior of immortal solutions. Researchers are successfully deploying sophisticated partial differential equation (PDE) estimates, parabolic rescaling, and Gromov-Hausdorff limits to decode the geometric limits of these flows. The mathematical community is resolving decade-old conjectures, proving that while singularities are inevitable in these non-linear systems, they are often governed by highly structured, canonical "soliton" models.

---

## 1. Introduction to the Geometric Flow Frontier

A geometric flow is a continuous evolution of a geometric structure, such as a Riemannian metric or an embedded submanifold, driven by a partial differential equation (PDE) related to its curvature. The archetypal example is the Ricci flow, $\partial_t g = -2 \text{Ric}(g)$, which acts as a non-linear heat equation for metrics, smoothing out irregular curvature over time. However, the period of 2024 to 2026 has witnessed profound paradigm shifts extending far beyond standard Riemannian Ricci flow. Mathematical research is now deeply entrenched in the behavior of flows with complex ambient geometries and extrinsic curvature dynamics. 

The frontier is broadly categorized into several distinct but interacting domains:
1.  **Mean Curvature Flow (MCF):** Extrinsic flows where a surface evolves in an ambient space (typically Euclidean space $\mathbb{R}^{n+1}$ or a Calabi-Yau manifold) proportional to its mean curvature.
2.  **Kähler-Ricci Flow (KRF):** The complex analog of Ricci flow, operating on Kähler manifolds, intimately tied to the Minimal Model Program in algebraic geometry.
3.  **Special Holonomy and Anomaly Flows:** Flows defined on 6-dimensional Calabi-Yau and 7-dimensional $G_2$ manifolds, originally motivated by the Hull-Strominger systems in heterotic string theory.
4.  **Conformal Flows:** Including the Yamabe flow, which evolves a metric within its conformal class to achieve constant scalar curvature.

This report comprehensively synthesizes the latest advances, breakthroughs, and open conjectures resolved in these domains from 2024 through the projected frontier of 2026.

## 2. Mean Curvature Flow (MCF): Multiplicity One and Singularity Classification

Mean Curvature Flow describes the evolution of a family of embedded surfaces $\mathcal{M}_t \subset \mathbb{R}^3$ moving in the direction of the mean curvature vector [cite: 1, 2]. The governing equation is given by $\partial_t F^\perp = \vec{H}$, where $F$ is a parametrization of the surface and $\vec{H}$ is the mean curvature vector [cite: 3]. MCF acts as the gradient flow of the area functional, effectively behaving like a shrinking soap film striving to minimize surface area [cite: 4].

Historically, fundamental theorems established the basic mechanics of MCF: Gage and Hamilton (1986) and Grayson (1987) proved that the Curve Shortening Flow contracts simple closed curves in $\mathbb{R}^2$ to a "round point," while Huisken (1984) proved a similar result for closed, convex hypersurfaces in $\mathbb{R}^{n+1}$ [cite: 1, 3]. However, for non-convex surfaces, singularities such as "neckpinches" inevitably occur before the surface can contract to a point [cite: 5, 6]. Understanding these singularities has been the core objective of MCF research.

### 2.1 The Multiplicity One Conjecture

The most monumental breakthrough in MCF during this period is the resolution of the **Multiplicity One Conjecture**, originally proposed by Tom Ilmanen in 1995 [cite: 6]. The conjecture asserted that when surfaces evolve and form singularities, they do not do so by accumulating several parallel sheets (multiplicity greater than one) [cite: 2, 6]. 

In late 2023 and published/presented throughout 2024 and 2025, Richard Bamler and Bruce Kleiner provided a rigorous proof of the Multiplicity One Conjecture for mean curvature flows of surfaces in $\mathbb{R}^3$ [cite: 3, 5, 7]. 

**Theorem (Bamler-Kleiner, 2023/2024):** For closed embedded surfaces $M(0) \subset \mathbb{R}^3$, any blow-up limit (tangent flow) of the mean curvature flow has multiplicity one at the first non-generic time [cite: 3, 7]. 

The proof by Bamler and Kleiner introduces a highly sophisticated separation function that tracks the distance between potentially converging layers of the surface. They demonstrated that this separation function never goes to zero over time, no matter how geometrically complex the surface becomes [cite: 6]. In practical terms, this means neighboring regions of a surface can never dynamically stack upon each other; bad behavior is limited strictly to localized, singular points [cite: 6]. 

### 2.2 Generic Singularities and Huisken's Genericity Conjecture

The resolution of the Multiplicity One Conjecture unlocked domino-effect solutions to other long-standing problems. Most notably, it fully resolved **Huisken's Genericity Conjecture** [cite: 8].

Huisken posited that for a "generic" initial surface, the only singularities that will form under MCF are either spherical (shrinking to a point) or cylindrical (collapsing to a line) [cite: 6]. While previous researchers—including Chodosh, Choi, Mantoulidis, and Schulze (CCMS)—had made significant progress showing that mean curvature flows starting from generic embedded surfaces incur only cylindrical or spherical singularities, their work was contingent upon the assumption that singularities possessed multiplicity one [cite: 3, 7].

With the Bamler-Kleiner theorem, this caveat was eliminated [cite: 6, 7]. The current theoretical consensus confirms that arbitrary small $C^\infty$ perturbations of a closed embedded surface $M_0 \subset \mathbb{R}^3$ exist such that the MCF starting at the perturbed surface exclusively encounters multiplicity-one spherical and cylindrical singularities [cite: 3]. Furthermore, the space of weak mean curvature flows with only multiplicity-one generic singularities is shown to be open and dense [cite: 3]. 

Consequently, researchers can now perform "surgery" on these flows. Because the singularities are well-behaved (cylindrical neckpinches or spherical collapses), mathematicians can computationally and analytically remove the singularity, cap the open ends with spherical patches, and allow the flow to continue [cite: 3, 6]. 

### 2.3 Lagrangian Mean Curvature Flow (LMCF)

Beyond surfaces in $\mathbb{R}^3$, the Mean Curvature Flow of submanifolds in ambient spaces with special holonomy, such as Calabi-Yau manifolds, represents a vibrant subfield. **Lagrangian Mean Curvature Flow (LMCF)** is a nonlinear parabolic PDE with profound links to symplectic topology, complex geometry, and mirror symmetry in theoretical physics [cite: 9]. 

The LMCF provides a canonical procedure to deform Lagrangian submanifolds within a Calabi-Yau manifold to find "special Lagrangians"—submanifolds that are volume-minimizing within their respective homology classes [cite: 9]. This approach relies heavily on the foundational conjectures posed by Thomas and Yau, as well as Joyce, regarding the long-time behavior of the flow, singularity formation, and how to analytically flow past singularities [cite: 9].

Recent work by Mu-Tao Wang and others has highlighted the complexities of LMCF in higher codimensions. When a smooth map defines an embedded submanifold in $\mathbb{R}^{n+m}$, the flow's behavior is relatively well understood for codimension $m=1$. For $m > 1$, however, the geometry is significantly more hostile. Recent advances utilize a **2-area-decreasing condition**, which is closely connected to the notion of 2-convexity in Lagrangian MCF, to control the associated PDEs and guarantee convergence to a minimal Lagrangian submanifold [cite: 9].

### 2.4 Discretization and Computational Advances

As the theoretical understanding of MCF solidifies, applied mathematics and computer science are actively discretizing these flows for geometry processing, surface fairing, and mesh denoising [cite: 1, 10].

The Summer Geometry Initiative (SGI) 2024 produced advanced research on the **Higher-Order Discretization of Mean Curvature Flow** [cite: 1]. The standard first-order discretization moves the surface in the direction of the normal, scaled by the mean curvature (approximated via the cotangent Laplacian applied to the vertices of the mesh) [cite: 1]. However, explicit Euler methods suffer from severe stability issues, demanding prohibitively small time steps, while fully implicit methods can be excessively computationally expensive.

Recent implementations involve higher-order temporal discretizations, adding curvature-dependent corrections to enhance or counteract displacement [cite: 1]. By approximating the gradient $\nabla H$ and the Laplacian $\Delta H$ using finite differences and stiffness matrices, algorithms can now achieve higher numerical accuracy with larger time steps, faithfully replicating continuous PDE solutions in discrete polygonal meshes [cite: 1].

## 3. Kähler-Ricci Flow (KRF): Analytic Minimal Model Program and Collapsing Limits

The Kähler-Ricci flow (KRF) is defined on a compact Kähler manifold $(X, \omega_0)$ by the evolution equation $\partial_t \omega = -\text{Ric}(\omega) - \omega$ (for the normalized flow) [cite: 11]. Since Cao's 1985 alternative proof of the Calabi conjecture, KRF has been utilized to study the moduli of Kähler metrics [cite: 12]. Today, KRF is deeply intertwined with the Analytic Minimal Model Program (MMP) proposed by Tian and Song, which aims to classify algebraic varieties through geometric evolution [cite: 11, 13].

### 3.1 Immortal Solutions and the Song-Tian Conjectures

An "immortal" solution to the Kähler-Ricci flow is one that exists for all positive times $t \in [0, \infty)$ [cite: 14, 15]. A major focus of the 2024-2026 frontier is understanding the asymptotic behavior of immortal KRFs as $t \to \infty$. 

In a landmark 2024 paper published in *Forum of Mathematics, Pi*, Hans-Joachim Hein, Man-Chun Lee, and Valentino Tosatti successfully proved Conjectures 1.1 and 1.2 originally posed by Song and Tian regarding collapsing immortal Kähler-Ricci flows [cite: 14, 16].

For a compact Kähler manifold with a semiample canonical bundle and intermediate Kodaira dimension ($0 < \text{Kod}(X) < \dim X$), the KRF collapses the manifold along the fibers of the associated Iitaka fibration [cite: 11, 16]. Hein, Lee, and Tosatti proved that:
1.  The flow collapses to a canonical metric on the base of the Iitaka fibration in the locally smooth topology [cite: 16].
2.  The Ricci curvature of the evolving metrics remains locally uniformly bounded away from the singular fibers of the fibration [cite: 15, 16].

This was achieved through the derivation of a highly rigorous asymptotic expansion for the evolving metrics, mirroring earlier work on collapsing Calabi-Yau metrics [cite: 16]. The evolving metric $\omega(t)$ shrinks in the fiber directions while maintaining a bounded size in the base directions [cite: 16]. The result demonstrates that the scalar curvature is uniformly bounded, providing a robust metric geometry verification of the Analytic MMP under the assumption of the Abundance Conjecture [cite: 15, 17].

### 3.2 Finite-Time Singularities and Type I Blow-ups

When the maximal existence time $T$ is finite, the KRF develops a finite-time singularity. A singularity is classified as **Type I** if the blow-up rate of the Riemann curvature tensor is bounded by $C/(T-t)$; if it grows faster, it is **Type II** [cite: 18].

Jian Song established that for general finite-time solutions of the KRF, the Type I blow-ups sub-converge in the Gromov-Hausdorff sense to an ancient solution on a family of analytic normal varieties (with suitable choices of base points) [cite: 15, 19]. This extends Perelman's legendary scalar curvature and distance bounds from the Fano KRF to the general finite-time setting [cite: 15, 19].

Furthermore, a heavily investigated conjecture posits that *all* finite-time singularities of KRF on Kähler surfaces (complex dimension 2) are Type I [cite: 18]. Recently, Conlon, Hallgren, and Ma proved this conjecture under the additional assumption that the flow is volume non-collapsing [cite: 18, 20, 21]. They demonstrated that any non-collapsed finite-time singularity of the Ricci flow on a compact Kähler surface is modeled on the shrinking Ricci soliton of Feldman-Ilmanen-Knopf [cite: 20]. Jiangtao Li has also investigated volume-collapsing KRF on Hirzebruch surfaces, showing that tangent flows at the singular time slice correspond to nonflat gradient shrinking Kähler-Ricci solitons with finitely many orbifold singularities [cite: 18, 22].

### 3.3 Gradient Kähler-Ricci Solitons

Solitons are self-similar solutions to geometric flows, evolving only by diffeomorphisms and scaling [cite: 23]. They act as the primary models for singularities. 
*   **Shrinking solitons** model finite-time singularities [cite: 5, 24].
*   **Expanding solitons** model the behavior of flows continuing out of conical singularities [cite: 24, 25].

Researchers have successfully classified various solitons. Conlon, Deruelle, Hallgren, and Ma have extensively studied complete non-compact shrinking and expanding gradient Kähler-Ricci solitons [cite: 20, 26]. Notably, it has been shown that certain Kähler cones can be desingularized by complete asymptotically conical (AC) expanding gradient Ricci solitons, but *not* by Kähler-Ricci solitons, indicating subtle topological restrictions inherently forced by the complex structure [cite: 26].

### 3.4 PDE Estimates: The Parabolic Complex Monge-Ampère Equation

Analytically, the KRF is reducible at the potential level to a parabolic complex Monge-Ampère equation [cite: 12]. Recent advances in this domain are driven by obtaining uniform $L^\infty$ bounds for the flow without relying on heavy curvature bounds. 

Guo, Phong, and Tong successfully ported the elliptic PDE techniques (which led to the breakthrough on constant scalar curvature Kähler metrics by Chen and Cheng) into the parabolic setting [cite: 12, 17]. They derived an $L^\infty$ estimate for the solution to the flow independent of the maximal time $T$, relying instead on uniform integral estimates of Green's functions and volume density bounding ($L^{1+\epsilon}$ bounds) [cite: 12, 17]. This allows the KRF to be analytically extended through more severe geometrical degenerations than previously thought possible.

## 4. Special Holonomy: The Anomaly Flow and $G_2$-Laplacian Flow

String theory, particularly heterotic string theory and the Hull-Strominger system, requires manifolds that exhibit specific supersymmetric properties. Standard Calabi-Yau metrics (which are Kähler and Ricci-flat) are too restrictive for certain string compactifications. Thus, researchers utilize non-Kähler complex manifolds and 7-dimensional $G_2$ manifolds [cite: 27, 28].

### 4.1 The Anomaly Flow and Conifold Transitions

The **Anomaly flow** was introduced by Phong, Picard, and Zhang as a geometric flow designed to naturally evolve non-Kähler Hermitian metrics toward solutions of the Hull-Strominger system [cite: 27, 28].

A major application of the Anomaly flow is the geometrization of **conifold transitions** [cite: 27, 29, 30]. A conifold transition is a geometric process where a Calabi-Yau 3-fold is deformed into a topologically distinct manifold by contracting specific curves to conical singularities and then "smoothing" them out [cite: 27, 30]. Reid's Fantasy postulates that all Calabi-Yau 3-folds might be connected through a vast web of these conifold transitions [cite: 27, 30]. However, this transition explicitly breaks the Kähler condition [cite: 30].

In 2024 and 2025, Caleb Suan, working with Sébastien Picard and Benjamin Friedman, proved that conifold transitions are continuous in the Gromov-Hausdorff topology using conformally balanced and Hermitian Yang-Mills metrics [cite: 27, 31]. 

Furthermore, Suan extended the Anomaly flow by computing integral **Shi-type estimates** along the flow for a general slope parameter $\alpha'$ [cite: 27, 31]. Because the Anomaly flow contains terms that are not concave (meaning standard maximum principle techniques fail), Suan utilized an integration-by-parts argument to control the higher-order derivatives of the curvature [cite: 27, 28]. This resulted in a specific smallness condition on $\alpha'$ that strictly guarantees long-time existence, allowing the flow to be extended from a maximal interval $[0, \tau)$ to $[0, \tau + \epsilon)$ [cite: 27].

### 4.2 Flows of Conformally Coclosed $G_2$-Structures

On 7-dimensional manifolds, the natural geometric structures analogous to Calabi-Yau metrics are $G_2$-structures. The goal is to find torsion-free $G_2$-structures (which have holonomy contained in $G_2$) [cite: 31]. 

Karigiannis, Picard, and Suan (2025) studied the principle of dimensional reduction: natural geometric flows in $G_2$-geometry rigorously reduce to natural flows in complex geometry [cite: 32]. 
*   The **$G_2$-Laplacian coflow** serves as a 7-dimensional lift of the Kähler-Ricci flow [cite: 32].
*   They constructed a specific 7-dimensional lift of the Anomaly flow on complex threefolds, which deforms conformally coclosed $G_2$-structures coupled with a dilaton field [cite: 32]. 

By analyzing these flows on $S^1$-fibrations over Calabi-Yau threefolds, they proved that closed and coclosed $G_2$-structures evolve strictly according to specific Monge-Ampère flows on the 6-dimensional base manifold [cite: 27]. This directly connects the highly non-linear PDE behavior of 7D special holonomy with the somewhat better-understood behavior of 6D complex geometry.

## 5. The Yamabe Flow and Conformal Geometry

The Yamabe problem, formulated in 1960 and resolved over several decades, asked whether every compact Riemannian manifold of dimension $\geq 3$ admits a conformal metric with constant scalar curvature [cite: 33]. The **Yamabe flow**, $\partial_t g = - (R - r)g$ (where $R$ is the scalar curvature and $r$ is its mean), was introduced by Richard Hamilton to evolve a metric continuously toward this constant scalar curvature state [cite: 33, 34].

### 5.1 Simon Brendle and the 2024 Breakthrough Prize

In late 2023, the 2024 Breakthrough Prize in Mathematics (often dubbed the "Oscars of Science") was awarded to Simon Brendle (Columbia University) for his transformative contributions to differential geometry [cite: 35, 36, 37, 38]. 

Brendle's legacy in geometric flows is unparalleled in the post-Perelman era. His awarded work spans Ricci flow, Mean Curvature flow, and Yamabe flow [cite: 35, 36]. Specifically, his contributions include:
*   **The Differentiable Sphere Theorem:** Proved jointly with Richard Schoen using Ricci flow, establishing that any compact simply connected manifold with pointwise 1/4-pinched sectional curvature is diffeomorphic to a sphere [cite: 39].
*   **The Lawson Conjecture:** Proved by Brendle, showing that the only minimally embedded torus in the 3-sphere is the Clifford torus [cite: 35, 36].
*   **Singularity Formation in Flows:** Rigorous proofs of the non-compactness of the Yamabe solution space and establishing the precise mechanics of singularity formation in MCF and Yamabe flow [cite: 36, 39].

Brendle's work solidified the methodologies required to study high-dimensional manifolds and sharp geometric inequalities [cite: 35, 38].

### 5.2 Resolution of the Yamabe Soliton Perelman Conjecture

Similar to the Ricci flow, understanding the Yamabe flow requires classifying its singularities via Yamabe solitons [cite: 34]. The "Yamabe soliton version of the Perelman conjecture" hypothesized that any nontrivial complete steady gradient Yamabe soliton with positive scalar curvature must be rotationally symmetric [cite: 34].

While earlier work by Daskalopoulos, Sesum, Cao, Sun, and Zhang solved the problem under the restrictive assumption of local conformal flatness [cite: 34], a significant breakthrough occurred recently when Catino, Mantegazza, and Mazzieri completely removed the locally conformally flat condition [cite: 34]. They proved that any nontrivial complete steady gradient Yamabe soliton with positive scalar curvature is indeed rotationally symmetric, fully resolving the conjecture [cite: 34]. They achieved this by relaxing the requirement of strict positive sectional curvature to non-negative Ricci curvature (positive at some point), relying heavily on generalized maximum principles [cite: 34].

## 6. Emerging Intersections and Applications

### 6.1 Chern-Ricci Flow and Non-Kähler Metrics
The Chern-Ricci flow, introduced roughly a decade ago by Valentino Tosatti and Ben Weinkove, is an evolution of Hermitian metrics by their Chern-Ricci form [cite: 40]. It generalizes the Kähler-Ricci flow to complex manifolds that do not admit Kähler metrics [cite: 40]. Research in 2024–2025 has focused heavily on the Chern-Ricci flow on compact complex surfaces (such as Hopf and Inoue surfaces), exploring how the flow handles the non-closedness of the fundamental $(1,1)$-form. It remains an active frontier for classifying complex surfaces outside the algebraic minimal model program [cite: 40].

### 6.2 Applied Geometric Flows in Machine Learning and Optimization
Interestingly, the theoretical rigor of geometric flows is bleeding into computer science. Recent advances in Neural Combinatorial Optimization (NCO) for solving NP-hard problems like the Euclidean Traveling Salesman Problem (TSP) have leveraged continuous geometric flows [cite: 41].

Friedmann and Dym (2026 projected research/recent preprints) introduced a framework called "CycFlow" that utilizes **Deterministic Conditional Flow Matching** rather than stochastic diffusion models [cite: 41]. Instead of classifying an $N \times N$ adjacency matrix, their model treats the TSP as the evolution of $N$ coordinates in $\mathbb{R}^2$ [cite: 41]. By regressing a deterministic vector field between the input metric space and a canonical circular arrangement (the solution geometry), the model achieves state-of-the-art accuracy while being orders of magnitude faster than standard diffusion-based inference [cite: 41]. This highlights the immense applied power of treating combinatorial topology problems through the lens of continuous geometric transportation and flow.

## 7. Conclusion

The frontier of geometric flows from 2024 to 2026 is defined by a shift from broad existence theorems toward the granular, highly precise classification of singularities and limit spaces. 

In Mean Curvature Flow, the proof of the Multiplicity One Conjecture by Bamler and Kleiner has irreversibly changed the landscape, proving that surfaces cannot collapse into dense layers of parallel sheets, thereby ensuring that generic singularities are perfectly manageable spherical and cylindrical pinches. In Kähler geometry, Hein, Lee, and Tosatti's proof of the Song-Tian collapsing conjectures cements the Kähler-Ricci flow as a practically flawless analytic tool for carrying out the Minimal Model Program. Meanwhile, the cutting-edge exploration of the Anomaly flow and $G_2$-Laplacian coflow by Picard, Suan, and Karigiannis is bridging the gap between highly abstract heterotic string theory and rigorous, PDE-based differential geometry.

Propelled by laureates like Simon Brendle and supported by an influx of cross-disciplinary computational research, geometric flows continue to represent one of the deepest, most dynamic frontiers in modern mathematics, yielding profound insights into the fundamental shapes and structures of our universe.

---
### Tables of Flow Definitions

| Geometric Flow | Canonical Equation | Primary Ambient Space | Geometric Purpose |
| :--- | :--- | :--- | :--- |
| **Ricci Flow** | $\partial_t g = -2 \text{Ric}(g)$ | Riemannian Manifolds | Uniformize curvature; topological classification. |
| **Mean Curvature Flow** | $\partial_t F = \vec{H}$ | Euclidean / Calabi-Yau | Area minimization; minimal surfaces/Lagrangians. |
| **Kähler-Ricci Flow** | $\partial_t \omega = -\text{Ric}(\omega) - \omega$ | Kähler Manifolds | Analytic Minimal Model Program; limits of complex structures. |
| **Anomaly Flow** | $\partial_t (\|\Omega\|_{\omega} \omega^2) = i\partial\bar{\partial}\omega - \frac{\alpha'}{4}\text{Tr}(R \wedge R) + ...$ | Non-Kähler Complex 3-folds | Hull-Strominger system; string compactifications. |
| **Yamabe Flow** | $\partial_t g = -(R - r)g$ | Conformal Classes | Achieve constant scalar curvature. |

**Sources:**
1. [summergeometry.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGiHw70842grMWcINe7Hq5fYftzOCGmJxdg3hA-uqSWydGS3XOTp1g5X8AsY1osQCHeqA80BcFeIZ9hjzwQhNTcP4oJHJsHyW7rJTVKcUMRN6MA4ODfOCUkPiNm9mrpplvSmM55CXaH99o60IM9tDgQGLBznzUfZTGsReJ06Q4TxkwLV-nfQTS7B_UFJQ==)
2. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqp2csj8UapBm33NI6xa4_kQGznzMDviLqD4-UD-YtBgeEQRfwgxowqJN3ESfup6WmUktpqF9zK8OQ21jqhmGfNpeb1kk_9pqgWHCgbZ8ML9LOKCLd3ebochUSv9DLpTYVv_m8KWOpr7IfL4INAw==)
3. [warwickmathssociety.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyFrAmYRa6pCzWcNJ3S_j5OAghKyHiXXY9mBfWF-lEeMXPK5I-WJHF7ncmVQmhvUmag8moXA37-jAldtgS7t9gLRZTej5P4D5tPUe-_7dtFHS5RL9_Mjw7CT6h3kkpO4F8atHliA9tTrZBQMIk2c2lAUT8rI3ytEoBkBUH_o0fY4ow-T5JV_RQ1hBU3iX7rKoqzHeiItKvSUzC9A-PrLhx8Ns=)
4. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3AstScVZO-0t7msLBNDSNYGkBvvL22A2XLTHSTdpd3tDIrMqlYWoew3bc1mEFF-fhnOAN62phzK1xSVk4JLhY_1b4cF5RWOPAnL_5UQAz3-bh7ihon5KHuyg-Hqt2GGnv)
5. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJC4tuhrULLoG3Wr-3s77n76pxO6xJjKXxIbLbuwbH6ENXSGXbpO8c34c4QUTNSG-rLbXW8jqvLVcdW9-N7YFBNBf4ZHK0nt4f1w81dGDI3WZ1LhLEjd8GYuuA2nXYGah9)
6. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIE-WF-aPus0DDM9X6j7st3mQg5vDFJf5YH-wzcmid2sb-JeSzfNgwdcHPKA-Zg88SnvkPlkBau_7DjHyvl1oOxRiURq8dGwyQ0SBUrZx6ZHtClav732I9ShgiRCCGPs45CruKMwHdpDzMI5--FLitGNNoeVQ74ZJcSN3wfd9_TgTyE8P1VYA1Wkk=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6DbuYl_Lav77iHqPlOtjxP6pBLJ2gXbcvstT79ywOBTUVa2Am1jD2CTQ-pbT4OPfStyTE1h-CSl8aBBsqM1DVQoW9gycX_wdk1oksaXq7qFG-9I3Hqg==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGECECyE8BekTSS50s4c3E3qhhDlvYILwALy0tWTtiOLOETVGSoJTIxLJuJqNLLDEXXcgDU0AP_delR7AslI8UM8ZljKlmNfIfkLuj3CIqUuK_5rdVfWw==)
9. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxNrh7TuQaqda6bTUAG-m28l3kEzXfIk2E9zT0CqLCjVdxspvd7mioVUudZz2-UtY11UHuPUbclHrg9HYfef2CQgQAZFEl8NA9-0AxoTBqPmitvRfUWXmVbCQJz81Q6woCNJ8EizmnZETpr9oUATI107N1DsTnvMfrzKk=)
10. [ukri.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1SAS1XGq6lY4--4-PpiuGt8X_i7KD3tXWSRgzjloXxf1soO73x_lf4gd5ApAMfrYI9GAONuRRZNOptTHLil9H0YZn4E7Oce4OZW5yN4BFUJyKN9s1wpizOUSb03IcdzT1nEWXvT_lpQ==)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHt_XK43gIsvbhES02KpHpeVG3yisVmhSigR0TaQV0RPdrRL0RguC1NSRlWaFhq6itDRWHQDVcLm-5cSPZ5nW24VB9bwAW8y7FO7wC1CxLancKiPtTTXIj_n3EwYCfnCmaUf6x5Q-EMmolBkEG3Pu7Fk-pgSKgwsCbfxN8wctmaIlQCOz3dzZdRdHomdd7vTXJXx89NsIsIEGDfSlgrrAG2sbPVV4iFvICkB0ZkpKflGqqCNf5MaT1iHDvTCdOu-9nGp-M=)
12. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkHCKFpA1B63mHP5oxJut7ZZKL7FsCKbwOYBpCVP7L031nX1YCRqXNaGAojfLH9ofcWXUMzQkgU5EtiOdmZpjrnCh3qVd8Sh4SFBPqz7INZwWkHqUK0CJLUvdBUEHfMMFOeYCtyr4SXNYw)
13. [westlake.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPxkz0-jz8CAxGC18X_V8td_aw4F1xw5SX370w4Dab7uXBOB5dUacnVxN14BDj6JEvtjlbL41K-PA9LbfAElqlNzdCT4MBWkLEWVs-rhkyRZ4nH2aYRB1HFYGW9l5i5viAEQ2x)
14. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhG08NJuEqa5wze2jUH-r1iyGsEg8MdUSlayPg09Ems9tC5jVW2lKMNwFymwI9iAXcXpj3KSyGtkIuN1JL3sceW5JUIUl9cc5EPRuqBIwB_xAxhCKtVGn1mDFw2hBlzAOdAM3cgxx-oq7FTJ-3b4JTbj1Qc2US73qC8TAbizBMgLYpNWEm-gBh9GOdAl7MjbgdDxqG0r2N2evpImxxF7F_Xhc9rDfJ3MGJPDQcRvzPlPrcwQfLzuR2Cgk=)
15. [crmath.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYVj6-D189VBc8neEM9iIS8mTwGebVb6MJYF6np4XUt_OJZbsATLYMYK7ofiDvqYmMIs11_TtEWg71arEpjX9f5hkkwfi4uyH9yMZcBxdrEzfHBsbgWmvlOrSD0sT0Eu11c5dlOCokYc2dqS3Pz9hZdzs=)
16. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZzv3zbfa_uo3EqR1RfoH6zxYSN-hlmcA24gvObDhKVdq5hwCHnVZeCyQ2PcVroQG-HMFgD7cQ83ZsktBu0JVlIySBdLBeQ4UgSI6gsEH1Zc7TH017qMfyX5u-ZxN01DoxeQxxdPCkWroB2PTyVylVPbWVc7HnOC6nZmeCZB0jOETwAqQPo-rvaWCMMjVNajvwMkuekBcnSmplN3fRon89as9FK7ptt_arbqYnCMwkUH4GRGD0rBrqKWDIh_ipsEVXE3coIyloBBkQON88zV2LqwqJiOKXdZZYbTGqG-rpFM4=)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTj-4MfQSG-fMu-JEtRz5CyL-PSHutPL2GRW3X440wH_KB1AfHtuppHcTLpq-i9h70Q5ORldsvG4Ro0A_64dRkKeq5w_KpQLj-vCE30jtaoMGwAM8Yli_E5_7Bks70r6OnWzm1dOS9aT1lZ6AZkGXpv48FarycI-1WLV-tvmjjHP94XICXOw3bWGaRqXaSPSiwETE1Q4qJdZCmcxw0wyAEZ_F1HcA54fb3ZcdZmWYaLLrcgDV2fVQ=)
18. [worldscientific.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFR4Ldu6szWhcp8bJuJDAxauesQ8L0oLlZh5WGju8sXW1S7C49Giv7o4cXcbvR-MBf0cBe00Jkhtzx3tc4cR2TULTsn8WvOOQkZoobOSGDygECm4DtDId3wIjBG6tzwXgle-TpSRM2vsmCObERNbcfSrP9d6XRmFQ==)
19. [crmath.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQ6JIHFkuTOeSrkdGCR9DoKRzOHYKpJPKux8WUyV5qQ7yXQr901Nb8tVFgC8LiwrB_qVw_VH-ijyDjjwxttQFPztDT2LHGikLaW4CRuxLvhPdKl9u1xHGJ1vML0XNyyesWRocPX9qVjJAXrst2)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVe84PBLt_gn7O9S-SWR-_c2ZvOecMKTawS186c8rPjKCQ8JyYGu8nngI3IqOR6YvJq2Dn8gnCJmluAEQIl0KuumyIhFxUzyKQmpG3ZcaO_9_9VfFAnDYRKJjqASGkwG__sHAVtJ9sZZf-ckbH17TZwKRxRlJYMJC16Os-WMy52vDfpS2Ay-61QHuPlj_UxB5zQCMOMfBsduj88bcU1vT5J6OWHT3jYwONkc1L3ITrFoUb0ifaVn3BQKHsBYA8sJKGc7hKcJLc_TOr2dbIFlLH-g==)
21. [lims.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExsk8_14CotSQD6hIJh6n1VfpYtV11zTqXLSP-BjEwQwXIqGEeMHK9ZQBtSNV2tAHZxg7xBAnI8LIEx-XB_iAmQrwwRqXk0a4seJux913HktHrl8mkXFnnX0Dylv4=)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzj_F5n8a6-c4cvFuG0COZ0kXKCy-nDAlsZKKr03sWfpx-33p_huuOdrhoBHDXVpl4QnEx9jcDzzlGhg6wbMwYZraQavxE5nenfsAErJcBFf3GjISNp1CLDfdYWzFILYQs-aykMLshZ1pLg1DkCxPeKlY6vIc1nvBjPJP1j58zl-uP3HxfOY_wvYyvkR-QQMhoeeRd7zIjhOAM-8DFWt-WUBI1SGmXd3C2nHm2u5vNqnJB-cNDkoBp)
23. [rutgers.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIXlJHjX71xkL46O_eBG9g_pX9CqfKdYl-pdUSFBKNfloI2bgJ0ytAPqD4PvquUkEJqfiP6diszxJCIrUQCtC8O3ioyabZSbz0lY2a18KniJXWOwMCEvdCDV36qJ0_MmJZDRRtfBWmlucVRCQuHtRkKzluq946NA==)
24. [ucsd.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPu6vSl3XtKvdZtU-5H2YnN5lPZzplziybOT-a0nKbumS7C9kjt2A4BKkdzIM7qSlQ_8xWyv8KakQp9YD4fxfXjUgHGRhE9rWpn5H_TkogfqOk1fZauVjmxoEZadqBbDyYtqWGvg==)
25. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_bOosEMP7Y9M-eab7WeFk4cRsi8ZGEzHfyZUj423qz4EqdUo505lIAwIoUVJk-lpZiLWNuBiSqANpHNuFIu4560_kMRFGPe3jHuzdmu2JTcqx9mmEZ_2UnVEkXPX5_nqjBKD_kw05-WqB2_ve9YTs8tAix0O1nhwe-HqwJbzdX4uxTRDijcxjB5SlgPm2OQpdga6tO4JtHk0l_cr4-yMap2snOzzyggIXmfFQgsvkV2AF)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEt5Q5KpZkLB7TC8sXi-K9UQkptMaopcrR-sgJ6oaAB5ufnWO1wcwIodTaZzU9PISx0TUclLcBTkoUJyjGqEowPT0vlksxZ64IRSorcqre-kn1d-xy08WRClNYaAuESQ4d856Pz43Tn54vsC6lqKM9nHHveMp3pLDk-FuV1HiuiiYr5LzEQ9rZpXtGyVNhG440MrqpXURe3zSW5NS70VQvHNkE8ZDM4q---qhZSNLCkArwlgQFhe3Fp80Pd)
27. [ubc.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdA1mtbTiiAGsE7DceFuyDppa1yQFW9R8mKqCp5mPyfS1LPf6U38RRoo0tLtX5kU_6Nyf9fsOrzOjOUqOEhSfsAqJB3YQX0LK2wRPF4o7ygG26jY8bKNJNEvlAN3Km0hAYDyhWOAqhVGcGHTQLBZ_O)
28. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESjRq0jNpcfV6up_2KR9xeiDqpLG6PYnv7CGsQbKuYpqx6mDdjY-MGhmH2GJtvmK_2vlZ6wWA_0bAE0hY9X1G7B2j13FSz8yQCNwE0qbtvc9STOq7H-IT6RgKROeqz2FwNRtmv05o1z067z6V70AScGvxh1CD6sLx7QKx3bVX5jH0LUX2p4Kv0sD8eOBzXXZFo)
29. [ubc.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErKnV3JMfqTgIc6G55Se7NymttxOTbLQrE_4npccbrgBYSrnG_ylaT-AFO5sG6J0DVBTT2O29lVDvCDdHJ4VuA1uAQlQkJQyReB6UxdNtfGLp_DcnIbnD0HSHpPQ-OqX39QfN5SJdYg_4bWlkCSZgLEj0p95Rx4Ua2gpNdhDsZATotnNCZ)
30. [hkust.edu.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrfglus9jHym7Hv4Sx3a2ZHkN1RmpkUKAeTXOK9NyE5VDB3UiAblGn_scIT4JNXPj48_MbGU5dhvSFJWN6gR_Z6rkBahA29rVZcs9_uRt6na4zXPZ0s4mQmCSRb5sjuL6a-8qxv6WpebdmtFwQDcYOjo8aQsEuK4JlTOBIUPzAeH_w3Jqd2cEwteiZMQhf1ZMCEhM_oNyx8Kc_PZ1fKUcmtcAb65U7byb3fI32CZs3HQ==)
31. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrnkkxseX5Vl89YhFlB1seI7F4LfONrkxXrxMcaTK_SK6YFM1XtHz0RQUqvihZ6jgx_X8UVO7Zx1v67CjTsFK5RwVOkanpaMC1SfhxRvE6x0-5)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHP8knAJPJ8J0TUlnq7BFpHP18wOCkO9yljhW_OE7DXhXWAtq4jPuJZmYp6CM-XEtbWCIlWd0C4pvqyHroeN9eadJZDojYVoNpua3yXsygj0DlEDY72mQ==)
33. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFU2zlTLbSnCJvKeHKGHq6pjcSWiufaXTjIgkP2agJ5JRzHHk2AfqwN2Kstl_NJpI-z-SozT4fT06i829qxIEgu7KxHvvZVcqgmyMZYa-1Vrk7CZOKOPKYLZei38YAQKq0=)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5P6MGgEQpjsvf7b6ogspaUaF_haEYmMyYJWUZ9hob80OAoSAiJWrsS_0TWQmOcRF9h-XKTL8lhMK9r6zHpAfbl1g57_mRMSCSc_pp0RXid4CoeqkmO1LmXg==)
35. [spp2026.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMlbAK8m9tQgumVzCTlzTOtXf3-2_e-S_LlYqfCteE8DyPMkkR_fHIzouMzzRIn65zLLo-yeXnOIjkJhrwWHMD3uDVVUIc0JfybNOLaN2t2vxzhwSja4MT9s2pcyzU2EHpvdyQHsjU0zIY1QPMlA6BzUs0fxU=)
36. [simonsfoundation.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4MrXS2dluzH_bhbpAsjb6at3Xg-6HUdPuronUti2wJc5ojpPgLTl4OfkLtl5VBnHW5_nDKJ4O8Pe7hugXGxlrFlJlfRowiI0GBfMBz8h03bF8Bm5w4Z3I7vB_rp76LV7mEI9zFMRzGNKD8lrl0BN8NmnB9uncxEZx2cqsIPDo_ftTjnFyM6MU4bUxgsef0DWW9xVd74eo5BmHXZVjYY9PiRc5JTYXkflwDkh_hR0=)
37. [columbiaspectator.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFUPAy57-BwwF9GXMpV3rZ8matHjHTgC7dwjgAliCrLWezb1DB5liWk10Bisxz91ATJz3vZmH2OOdeuYoCRRWRtAlJxIWHtCidWFiCGsEGzZFZma5Td1hadpPxc-2ZJryTPVHr-zsPK0hHeTLLagl2ByMFK1sfs6A9FjPHM7HGDDBnP_PLl0Kup5qfQN1fKbn_Y82ytjgWs65X_AKn-ZQt5pGo85U=)
38. [breakthroughprize.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2YASD5yffNhTFd4Uu74XLWSQNyE5BLXfV5q_vB51QZzEzUZSPm60OCtbOR5l6ITtax-Tr4egoyofRzI6wqdKt2HxVQHFiY4fUlGi0i09Mv_wWUeWD4b4UhxwE)
39. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBRGEArpuRcpU_-v5RWhv2SBbpJua5aV3e3g2rXjogrL5scyvoD94dMU0OANHIrqzZheMpKssDxcMd-bVG7jWsk9X9JbDt_X7Tk8q_fTMCukP79NRY51RyJfV4o1WrFAHNdfJzYWwlxr-jHHj7XfCprLdJssfEGjqHgMLBkl2nTmc-lWOLfktp11ZAB552yKeJAf8AtF1Q)
40. [mcgill.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2hS8TIOgRyiLWLoY5i7osGx-oR_mLT4vfbRWcARPFyjNfu56sfqvHaAgON9PX_oy5qcwzPFKQQ7JSou3DhcLqZo2Z_KLVIQZuf7kWX9QaOnISw6Mq)
41. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_hR274FlHg2QS4ZSKBPY838v3gspo-52L2iN6UkDC2NQPr0OqtcUNI77h0kXzNyipkdwYEUlw_c1tucv58EPqo1ZfO_3mALdVp6vhDmY2LWOaCdcqBjlTgg==)

