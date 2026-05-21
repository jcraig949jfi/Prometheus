# Number field discriminant bounds 2024-2026 (Odlyzko, Hajir et al)

**Pythia queue id:** 175
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChRNem9QYXFCTzBxRFV5UV9UdEtCbxIUTXpvUGFxQk8wcURVeVFfVHRLQm8
**Elapsed:** 248s
**Completed at:** 2026-05-21T17:04:44.493515+00:00

---

# Number Field Discriminant Bounds (2024-2026): Odlyzko, Hajir, and Recent Breakthroughs in Algebraic Number Theory

**Key Points:**
*   The root discriminant of an algebraic number field acts as a fundamental measure of its ramification complexity. Since the 1970s, Odlyzko's bounds have established theoretical minimums, showing unconditionally that any number field with an infinite class field tower must have a root discriminant of at least \(22.3\), and \(44.3\) under the Generalized Riemann Hypothesis (GRH) [cite: 1, 2].
*   Significant constructive breakthroughs occurred between 2024 and 2026 in finding explicit number fields with infinite \(p\)-class field towers and exceptionally small root discriminants. Notably, building upon the "cutting" methods of Hajir, Maire, and Ramakrishna (which achieved a record root discriminant of \(\approx 78.427\) in 2021) [cite: 1, 3], Liu and Xing (2024) constructed new families of Kummer extensions yielding small root discriminants for \(p=3, 5, 7\) [cite: 1, 2].
*   Research in 2025 by Hamza, Lim, and Maire shifted focus toward unipotent extensions and Massey products, constructing new cases of pro-\(p\) extensions with restricted ramification that decompose as coproducts of pro-\(p\) absolute Galois groups of local fields [cite: 4, 5].
*   In a monumental development in May 2026, an OpenAI reasoning model autonomously disproved the 80-year-old Erdős Unit Distance conjecture [cite: 6, 7]. The AI utilized deep algebraic number theory—specifically, infinite class field towers of the Golod-Shafarevich type and bounded root discriminants analogous to those studied by Hajir, Maire, and Ramakrishna—to construct planar point configurations that yield a polynomial improvement over long-believed grid bounds [cite: 8, 9]. 

This report provides an exhaustive, highly detailed academic overview of the evolution of number field discriminant bounds, with a specific focus on the period between 2024 and 2026. While the problem of bounding discriminants is rooted in classical algebraic number theory, recent computational and theoretical innovations have driven unprecedented intersections with discrete geometry, culminating in the resolution of one of Paul Erdős's most famous open problems. The evidence leans toward an increasingly unified framework where asymptotic bounds on discriminants translate directly into bounds for dense graph embeddings, coding theory, and cryptography.

---

## 1. Introduction: Fundamentals of Discriminants and Ramification

In algebraic number theory, the absolute discriminant \(\Delta_K\) of a number field \(K\) of degree \(n = [K : \mathbb{Q}]\) is a fundamental invariant that measures the volume of the fundamental domain of its ring of integers \(\mathcal{O}_K\). Specifically, \(\Delta_K\) dictates the ramification behavior of the field; a rational prime \(p\) ramifies in \(K\) if and only if \(p\) divides \(\Delta_K\) [cite: 10]. 

Because the absolute discriminant grows rapidly with the degree \(n\) of the field, it is analytically much more convenient to study the **root discriminant**, denoted \(rd(K)\), which is defined as the \(n\)-th root of the absolute value of the discriminant:
\[ rd(K) = |\Delta_K|^{1/n} \]
A foundational theorem by Minkowski guarantees that for any number field \(K \neq \mathbb{Q}\), the absolute value of the discriminant is strictly greater than 1, implying that there are no non-trivial unramified extensions of \(\mathbb{Q}\) [cite: 10]. Furthermore, Hermite's theorem states that there are only finitely many number fields with a bounded absolute discriminant [cite: 10]. However, understanding the exact asymptotic behavior of the root discriminant as \(n \to \infty\) remains one of the most prominent open problems in the field [cite: 10].

The root discriminant is highly sensitive to the arithmetic of field extensions. Crucially, in a finite unramified extension \(L/K\), the root discriminant remains strictly constant: \(rd(L) = rd(K)\) [cite: 10, 11]. Therefore, if a number field \(K\) admits an **infinite unramified extension**—known as an infinite Hilbert class field tower—the root discriminant of the entire infinite sequence of fields remains bounded by the constant \(rd(K)\) [cite: 10, 11]. 

## 2. Odlyzko's Discriminant Bounds

To establish theoretical lower limits on how small the root discriminant of a number field can be, analytic number theorists employ the Stark-Odlyzko positivity technique [cite: 12, 13]. This method evaluates the logarithmic derivative of the Dedekind zeta function \(\zeta_K(s)\) using explicit formulas, integrating against carefully chosen non-negative test functions [cite: 12].

A. M. Odlyzko's monumental calculations from the late 1970s and 1990 established rigorous lower bounds on \(rd(K)\) that apply asymptotically as the degree \(n\) approaches infinity [cite: 12]. Odlyzko's bounds demonstrate that the root discriminant cannot be arbitrarily small. For a number field with an infinite class field tower, Odlyzko's unconditional bounds imply that the root discriminant must be at least \(22.3\) [cite: 1, 2]. Furthermore, if one assumes the truth of the Generalized Riemann Hypothesis (GRH), which forces the zeros of the Dedekind zeta function to lie on the critical line \(\Re(s) = 1/2\), the lower bound for the root discriminant dramatically increases to \(44.3\) [cite: 1, 2]. 

These bounds set a strict floor. It is mathematically impossible to find an infinite class field tower where the base field (and hence all subsequent fields in the tower) has a root discriminant smaller than \(22.3\) [cite: 2]. As a result, constructing specific number fields with infinite class field towers and a root discriminant as close to this theoretical floor as possible has been an active theoretical pursuit for decades [cite: 1, 2].

## 3. Class Field Towers and the Golod-Shafarevich Criterion

The pursuit of minimal root discriminants is inextricably linked to the theory of class field towers. The Hilbert class field \(K_1\) of a number field \(K\) is defined as its maximal abelian unramified extension [cite: 2]. By iterating this process, taking \(K_{i+1}\) to be the Hilbert class field of \(K_i\), one generates the Hilbert class field tower:
\[ K = K_0 \subseteq K_1 \subseteq K_2 \subseteq \dots \]
If this sequence does not stabilize (i.e., \(K_{i+1} \neq K_i\) for all \(i\)), the tower is said to be infinite [cite: 2]. Because each step is unramified, the root discriminant of every field in the tower is exactly \(rd(K)\) [cite: 10, 11]. 

Historically, it was unknown whether infinite class field towers existed until Golod and Shafarevich provided a positive answer in 1964 [cite: 1, 2]. They proved that the quadratic field \(\mathbb{Q}(\sqrt{-3 \cdot 5 \cdot 7 \cdot 11 \cdot 13 \cdot 17 \cdot 19})\) possesses an infinite 2-class field tower [cite: 1, 2]. Their criterion relies on group cohomology: if the \(p\)-class group of a field has a sufficiently large \(p\)-rank \(r\) relative to the degree of the field, the Galois group of the maximal unramified \(p\)-extension is infinite.

Subsequent refinements focused on finding fields with much smaller root discriminants. In 1986, Schoof provided a robust methodology for constructing infinite class field towers, producing infinitely many quadratic fields with infinite 2-towers [cite: 1, 2]. Martinet later achieved significant milestones by identifying fields with drastically reduced root discriminants. For instance, Martinet discovered the number field \(K = \mathbb{Q}(\zeta_{11} + \zeta_{11}^{-1}, \sqrt{-46})\) which has an infinite class field tower and a root discriminant of approximately \(92.4\) [cite: 1, 2].

## 4. The "Cutting" Method: Hajir, Maire, and Ramakrishna (Pre-2024)

Following Martinet's work, Farshid Hajir and Christian Maire, later joined by Ravi Ramakrishna, led a concerted effort to minimize root discriminants for infinite towers, particularly by studying tamely ramified towers [cite: 10]. If an infinite tower is allowed to ramify, but only tamely and at a restricted finite set of primes \(S\), the root discriminant will increase, but it can be bounded [cite: 3, 10, 14].

Hajir and Maire established that using \(S\)-tamely ramified 2-towers over a fixed field, one could push the root discriminant bound down to \(\approx 82.1\) [cite: 1, 3]. In a landmark 2021 paper titled "Cutting towers of number fields," Hajir, Maire, and Ramakrishna introduced the "cutting" method [cite: 1, 3, 15]. By strategically quotienting out (or "cutting") specific ramification data from the Galois modules while preserving the conditions necessary for the Golod-Shafarevich criterion to hold, they successfully suppressed the growth of the discriminant [cite: 1, 3]. This breakthrough lowered the root discriminant record for an infinite tower to \(\mathbf{78.427}\) [cite: 1, 3].

The work by Hajir, Maire, and Ramakrishna proved that topological and cohomological manipulations of the Galois group \(G_K\) can effectively bypass some of the rigid algebraic barriers that inflate discriminants, a realization that would deeply influence the field from 2024 to 2026.

## 5. Major Developments in Algebraic Number Theory: 2024

The years 2024 to 2026 saw a flurry of activity aimed at generalizing Schoof's and Hajir's constructions, leading to new theoretical formulations and highly specific root discriminant bounds.

### 5.1 Liu and Xing: Generalizing Schoof's Method (June 2024)
In June 2024, Qi Liu and Zugan Xing published results extending Schoof’s 1986 theorem from cyclic cases to arbitrary finite cases [cite: 1, 2]. They systematically constructed a class of Kummer extensions over cyclotomic fields, specifically \(\mathbb{Z}/m\mathbb{Z} \rtimes \mathbb{Z}/\phi(n)\mathbb{Z}\) extensions of \(\mathbb{Q}\), where \(m\) is a power of 2 or an odd integer [cite: 1, 2].

By doing so, Liu and Xing successfully constructed new number fields possessing infinite \(p\)-class field towers with explicitly calculated, minimal root discriminants for odd primes \(p = 3, 5, 7\):
*   **For \(\mathbf{p=3}\):** They demonstrated that the number field \(\mathbb{Q}(\zeta_9, \sqrt[cite: 16]{7 \cdot 181})\) has an infinite 3-class field tower with a root discriminant of \(\approx 776.7\) [cite: 1, 3]. This was a remarkable constructive bound for a 3-tower, refining earlier work by Jonah Leshin (who had established a bound of \(\approx 1400.4\) for the field \(\mathbb{Q}(\zeta_3, \sqrt[cite: 16]{79 \cdot 97})\)) [cite: 1, 2].
*   **For \(\mathbf{p=5}\):** They proved that the number field \(\mathbb{Q}(\zeta_{40}, \sqrt[cite: 2]{3 \cdot 41})\) yields an infinite 5-class field tower with a root discriminant of \(\approx 1196.2\) [cite: 1, 3].
*   **For \(\mathbf{p=7}\):** They identified the number field \(\mathbb{Q}(\zeta_{35}, \sqrt[cite: 17]{5 \cdot 71})\), which possesses an infinite 7-class field tower with a root discriminant of \(\approx 1608.8\) [cite: 1].

While these values (776.7, 1196.2, 1608.8) are numerically much larger than the 2-tower bounds (\(\approx 78.427\)), they represent state-of-the-art upper bounds for minimal root discriminants associated with odd prime \(p\)-class field towers, illustrating the increasing difficulty of controlling ramification as \(p\) grows [cite: 1, 2].

### 5.2 Bhattacharyya, Kadiri, and Ray (January 2024)
Simultaneously, Arindam Bhattacharyya, Vishnu Kadiri, and Anwesh Ray explored the asymptotic growth patterns of class field towers [cite: 11, 18]. In their paper, they investigated finitely ramified Galois groups over various number fields within a \(\mathbb{Z}_p\)-tower. They utilized the definitions of Hajir, Maire, and Ramakrishna concerning root discriminant bounds in tamely ramified Golod-Shafarevich groups [cite: 11, 18]. Their results provided precise asymptotic lower bounds for certain \(\mathbb{Z}_p\)-extensions in which a specified prime above \(p\) splits completely [cite: 11, 18]. This work reinforced the non-analytic properties of pro-\(p\) Hilbert class field towers, utilizing the Golod-Shafarevich-Vinberg criterion to show that the exponential growth of subgroups in the Zassenhaus filtration guarantees infinite extensions [cite: 11, 18].

### 5.3 Hajir, Larsen, Maire, and Ramakrishna (January 2024)
Furthering their collaborative legacy, Farshid Hajir, Michael Larsen, Christian Maire, and Ravi Ramakrishna released "On tamely ramified infinite Galois extensions" in early 2024 [cite: 19, 20]. The team sought to characterize the finitely generated pro-\(p\) quotients of the maximal tamely ramified algebraic extension \(K^{\text{ta}}\) [cite: 20]. 

They introduced a unifying paradigm: the concept of **stably inertially generated** pro-\(p\) groups [cite: 20, 21]. They demonstrated that any finitely generated pro-\(p\) group that is stably inertially generated can be realized as a quotient of the Galois group \(G_K^{\text{ta}}\), provided \(\mu_p \not\subset K\) [cite: 20, 21]. This framework integrated seamlessly with the local "tame liftings" utilized in the classic Scholz-Reichardt theorem [cite: 20, 22]. The research further specified classes of groups that *cannot* be realized as quotients of the tamely ramified Galois group over \(\mathbb{Q}\), adding topological precision to the bounds on tamely ramified field discriminants [cite: 20].

## 6. Developments in 2025: Massey Products and Unipotent Extensions

The theoretical machinery governing discriminant bounds pivoted toward deep Galois cohomology in 2025, heavily focusing on the presentation of absolute Galois groups.

### 6.1 Hamza, Lim, and Maire: Restricted Ramification (August 2025)
In August 2025, Oussama Hamza, Donghyeok Lim, and Christian Maire published "Massey products and unipotent extensions with restricted ramification," a pivotal paper analyzing the strong Massey vanishing property [cite: 4, 5, 23, 24]. Realizing a finite group as a Galois group typically injects massive, uncontrollable ramification, violently inflating the root discriminant. Hamza, Lim, and Maire mitigated this by constructing new pro-\(p\) extensions with strictly restricted ramification and specific splitting behaviors [cite: 4, 5].

A **unipotent extension** is a Galois extension whose Galois group is isomorphic to \(U_n(\mathbb{F}_p)\), the group of \(n \times n\) upper triangular unipotent matrices over \(\mathbb{F}_p\) [cite: 4, 5]. Building on Mináč and Tân’s Kernel Unipotent Conjecture (which predicts that the Zassenhaus filtration of absolute Galois groups corresponds to the kernels of unipotent representations when the field contains a primitive \(p\)-th root of unity) [cite: 4, 5], the authors proved that their constructed pro-\(p\) extensions satisfy the **strong Massey vanishing property** [cite: 4, 5]. Consequently, these extensions admit incredibly large unipotent quotients while maintaining a remarkably small number of ramified primes, effectively putting a tight leash on the growth of the absolute discriminant [cite: 4, 5].

### 6.2 Maire and Ngiza Mfumu: Genus Theory (October 2025)
In late 2025, Roslan Ibara Ngiza Mfumu and Christian Maire developed an expanded genus theory for number fields \(K\) subjected to tame ramification in a set of primes \(T\) and splitting conditions in a set \(S\) [cite: 25, 26]. By extending the approach to the class group via a "governing field," they formulated the \(S\)-\(T\) genus number of a cyclic extension \(L/K\) of degree \(p\) as the rank of a matrix constructed from Frobenius elements [cite: 25, 26]. This matrix representation allowed for algorithmic control over tame ramification, providing computational tools to search for explicit number fields that yield low discriminants without breaking the Golod-Shafarevich criterion [cite: 25, 26].

## 7. The 2026 Breakthrough: Artificial Intelligence and the Erdős Unit Distance Problem

The most spectacular application of the Hajir-Maire-Ramakrishna discriminant bounds and infinite class field towers occurred outside the traditional bounds of algebraic number theory. In May 2026, an artificial intelligence system trained by OpenAI utilized these exact algebraic structures to resolve an 80-year-old conjecture in discrete geometry [cite: 6, 7, 27].

### 7.1 The Erdős Unit Distance Conjecture
In 1946, Paul Erdős posed the planar unit distance problem: Given \(n\) points in a flat 2D plane, what is the maximum number \(u(n)\) of pairs of points that can be situated exactly one unit apart? [cite: 27, 28]. Erdős originally proved a lower bound of \(u(n) = n^{1 + \Omega(1/\log\log n)}\) by utilizing an \(\sqrt{n} \times \sqrt{n}\) grid, and he offered a $500 prize for a matching upper bound [cite: 9, 28]. 

For decades, the mathematical consensus strongly leaned toward the grid configuration being asymptotically optimal. The best known upper bound, derived by Spencer, Szemerédi, and Trotter in 1984 via crossing numbers, was \(O(n^{4/3})\) [cite: 9, 28, 29]. The prevailing conjecture suggested that \(u(n) \leq n^{1 + C/\log\log n}\) [cite: 28].

### 7.2 The OpenAI Disproof (May 2026)
On May 20, 2026, OpenAI announced that an internal, general-purpose reasoning model autonomously generated a mathematical proof that disproved the grid-optimality conjecture [cite: 6, 7]. The AI provided an infinite family of point configurations that yields a polynomial improvement over the previously assumed upper bound, establishing that \(u(n) \geq n^{1+\delta}\) for some strictly positive \(\delta > 0\) [cite: 6, 28]. The proof was rigorously validated by renowned mathematicians, including Fields Medalist Tim Gowers and combinatorialist Noga Alon [cite: 6, 9]. Following human refinement by Princeton mathematician Will Sawin, the improvement exponent was explicitly quantified as \(\delta = 0.014\) [cite: 6, 8].

### 7.3 The Role of Number Field Discriminants
The AI’s proof completely abandoned the geometric intuition of square grids. Instead, it executed a cross-domain leap into deep algebraic number theory [cite: 6, 7]. The core mechanism of the proof relies on constructing point sets via algebraic number fields of an arbitrarily large degree that possess exceptionally small root discriminants—exactly the structures studied by Odlyzko, Schoof, and Hajir, Maire, and Ramakrishna [cite: 8, 9].

To maximize the number of unit distances, the proof replaces the standard Gaussian integers \(\mathbb{Z}[i]\) with a fractional ideal \(\mathcal{O}_K\) of a **CM (Complex Multiplication) field** \(K\) [cite: 8, 9]. The geometric density of the point lattice directly depends on the discriminant of \(K\): the smaller the root discriminant, the denser the resulting unit-distance graph [cite: 9]. 

Because the required degree of the field \(K\) must grow towards infinity to support \(n\) points, the root discriminant would normally blow up. To suppress this, the AI applied the **Golod-Shafarevich criterion** to embed \(K\) as a finite layer within an **infinite class field tower** [cite: 9, 28]. Since unramified extensions do not change the root discriminant, the fields in this infinite tower possess a bounded root discriminant, perfectly circumventing the geometric penalties [cite: 9, 10, 29].

Furthermore, to guarantee an abundance of unit distances, the fields require many elements of complex absolute value 1 across all embeddings [cite: 9, 29]. This was achieved by ensuring a fixed rational prime \(q\) splits completely throughout the tower [cite: 9]. As highlighted in human-verified summaries of the AI's proof, to keep the inertia degrees small and maintain the Golod-Shafarevich condition, the AI argument quotiented out a fixed power of the Frobenius element [cite: 8]. This highly technical maneuver was explicitly noted as reflecting the "cutting towers" methodology pioneered by **Hajir, Maire, and Ramakrishna** [cite: 3, 8, 9]. 

By successfully uniting the topological constraints of tamely ramified Golod-Shafarevich towers with the combinatorial geometry of unit-distance lattices, the AI synthesized decades of purely algebraic research (including the Odlyzko bounds and Hajir-Maire constructions) into a revolutionary geometric counterexample [cite: 6, 7, 9].

## 8. Broader Applications: Coding Theory and Sphere Packing

The 2026 resolution of the Erdős conjecture is the most publicized application of number field discriminant bounds, but the implications of minimal root discriminants extend heavily into computer science and information theory.

Infinite class field towers with bounded root discriminants are the backbone of advanced lattice construction in coding theory [cite: 9]. As established by Tsfasman, Vladut, and Zink (and expanded by Lenstra), algebraic curves over finite fields with many rational points yield excellent error-correcting codes that break the Gilbert-Varshamov bound. In the number-field analogue, infinite class field towers provide lattice packings (such as those studied by Litsyn and Tsfasman) that exhibit incredibly dense asymptotic properties [cite: 9]. 

The bounds computed by Liu and Xing in 2024 (e.g., the root discriminant \(\approx 776.7\) for a 3-class field tower) [cite: 1] directly correlate to the minimum distance and alphabet size of generalized algebraic-geometric codes constructed over number fields. Every time the bound on the minimal root discriminant is lowered—such as Hajir, Maire, and Ramakrishna's push to \(\approx 78.427\) [cite: 1, 3]—the theoretical capacity limits for specific sphere-packing lattices and multiplicative codes improve [cite: 9].

## 9. Conclusion and Future Trajectories

The evolution of number field discriminant bounds between 2024 and 2026 represents a paradigm shift in both pure and applied mathematics. Odlyzko's foundational limits (\(22.3\) unconditionally, \(44.3\) under GRH) remain unbroken [cite: 1, 2], serving as the bedrock guiding algebraic number theorists. However, the space between Odlyzko's absolute floor and the constructive ceilings has shrunk considerably due to the meticulous manipulation of tamely ramified towers, unipotent extensions, and Massey products engineered by Hajir, Maire, Ramakrishna, Lim, Liu, and Xing [cite: 1, 4, 5].

The astonishing crossover of these theories into combinatorial geometry in May 2026—via an autonomous AI resolving the Erdős Unit Distance Conjecture [cite: 6, 7]—proves that bounding the root discriminant of infinite class field towers is far more than a niche algebraic exercise. It controls the fundamental topological and metric properties of infinite-dimensional lattices [cite: 9, 29]. 

As research progresses beyond 2026, the focus will undoubtedly shift toward utilizing artificial intelligence to further optimize the "cutting" methods of Hajir and Maire, potentially identifying explicit number fields that approach Odlyzko's absolute bounds even more closely. The intersection of deep Galois cohomology with machine-driven discrete geometry signals a new era, where the rigid constraints of ramification theory unlock the solutions to decades-old geometric puzzles.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEU-_e4Hisy6UMC6aQZ0aRWTIVdt_pEZcqPppjgqt8jcz6PPQmm0SL6LO7xlqkgkuXpxTkYzeL_hjLz-SdoKCme22JL0LM9iEKb-e5mJxA3vzzrDAm-7S8K_w==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6yHOdbpMgeGJfDpqjfWEgFXD3SNNvL9SHIBJUB4FkSfl93ELvw3noEkWUUi9EocwkqTNWgj1kawM4nZOFgbg4JEmPfJuauMhGibntLYqh3c7dXdir)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzyamxFxVIzKk-zBvAYr9gDCL3O2KOMBbhNXogIbQ9lqgeRrWOkGHhlWMi1PcnXP7ch2K6OGCtMu-gG7F7OxVdMpcdvh1bMAlc2757TH71MfIqPviX6SVlkQ==)
4. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2VQHlJOnw_Blin0NHEE1MYm3i1O4ivYfYRSUk3b5eF3opxeUBwom8VB1zBzFijuhy_qfN9AV8gkVH4HWlPFSEQfxcAKStoDEpaJzWri8JZjDfjzkQsxKZ18hAcm9-ORAz4nPKA3gmKvsKj9zWygHoAGIZj1E=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoVzttiFM0KonO_lYCZV1ZvjUAjgKXctdCZhw3yHybiMkJW5bjLxtL_7PgJpqJnl4ZnEfQ9La2hmYbZyfd-9hHQRayOr0dxw4DghoARHtNQl5mH5__Xw==)
6. [resultsense.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvq4TH92qngWW3eCdpRMieQqPCoY8RnSm9PMXOeuXGFJ6apJ-qhFrnBd4nwQj1DFDuEX8hTvoxNQ3ylX6IvoHMC7fvZqBUN0T4usOsbZSv1SRLi8-PVVCPdmT2Pw7UibU7qXTiBPUMAPJcGm3JhJ0DyGpRs7ifgzBHvUl98dJgVAMoM6uuA8cGIso4uNoeNhk7fw==)
7. [qwe.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7Zz1e8p-e5ryA6AHyb-cy9mHGBUDgkHkr_Y-jIgfcPEYP7OSZ29FtBq9KVYBVp5rBvOEiyJzgZYQyqCFXp8SmumD2-r4OZFjV9CUqby7KnfXSMoIOXgEaIaq0Rzxa97QmyzI0fHgXqSxRqJNIIo4Zx1G8Q_R5xiXCLuC3kU5ooHn2pQ==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRQDm2y7JNtCEITSfj_4k790URahqJUcfmnqM7Z2Q-282sIfQSmHwJngWAUH-3N60tsaXGj7T_8tD7QD4f_L-gzT473Xe5Q4CcilMs3SrRX4S8mqFuQpmMtQ==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKSofW5bWtPKIeFHkDnK1yaWP_TXTQ15H4Uo2xcZ7Y4T5-KVHx9k426_3LMXc_HkXviA0GZE2qf7_9qdAXpMYnF2fcc84pjsDvNBsLLFKE-WwefXkSYl4AXQ==)
10. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTi5qiPAjdoy2wFU373egQ9zIbEGVVNmH8pcNw3kYZLIEm9UvCpCDpu8QZbwyQ3LvtjtY2Ju7We4iMAq6zNM40lwmhuawRjiTytzw4mzdp0pf2BXsQt193H5HNEY2A9hk0z4fqXl-B7QhhjvAyXipo0e97geaNL2Vk17yGAA==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUy6S0IvXQ7NPuwL_bbOjypvNLvub5QHDYa76dYSEyn5ctCYhHTfFMFIQSJNlmCCFKW_Ns66B2vdlPkYJ6maoktqAI5Z0Y4i4kA1nIqUJKS47TTQ-pzQ==)
12. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjUmUPl6j7anU3p_zDydnU151kKVsRzmMcvVAX1caXSfRmzeWPO8zJM62WUrn5C_RbwWgNTo2Nyisr8cGjuLSU1KVVujK67OByyjesEzuYGIjzNmp3h6br4_E5Fdhdb6RoiT8J-yJRVXZ8sd_WZR5DnpUi9A==)
13. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETSNe_mITChIxG35R4UAkX6XkPvWM43sjzJ0wAZtSwud22-kqJ4m-6dAf45O-l80RhUpZ4P0g_ojk6WJ0bkGXx5UkVh88fMRHa-DewaZ3euRwX7EIWgIZVnbPxhWodl7t99p8BID8_-0ZOkYwLdjw=)
14. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpL8W7hA0ts2hCqoK7q34-cAZnLBCnhOjP2iuQIyQdsjEyIPapt57WNIPVcAgUX3HJUK8PsZ8s_A7DpuyNp8y7wDW69qunFcCfDYIc3J8wx69PlKoEvMb2U7J0Y9IIJy5XZ7zDBpqhy40BO1A1byyZRkvPu-vhUnGLpqh3sfMHh-eBJri69gFd6At6y-bsGrJatCkIhH-hsVIo32E52QtGeThuulK_YO8fQkpDWQW7NalJYg-Ybd2Vi81oS4ffSjbhLl-_5J4i7vbOFZCX13XzL8SM2TvUecOXP7vTBHkN)
15. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvCLBtJVYqvTI-oabWnVGLiDL4T0bDVIekD2g-jhwycrWekTVHlbvi7PulVdnwK4_HpovC9FbJWH6BjAeRmUrSNQUnXfEbRYdjf97GypEeRoN5OoE_e19k-t4tVM9kPPem1hUbMLvCBrYT3EuYxIyYCqOzEK1k)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9poUBH9iFtStDO3dR44IN28bKdtxuqwu7G_WwrFLIQ6_lxJnNA0wTsi9bUplUSFXkz-EQoFgi66ORP3Pm9LTNsF9FsFepmJRXlVE3Phok9A4dKAHUPslLFrqWoxltX00hwvoj5kNILKrPrm6gGNhUpB_wtUP7liKKZU5UZh4fvFoEWylFra7OrbIjWM4zKLv-VtKbSGU7sKiVnsFPEj8zsHkMaQ0=)
17. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHssGkLm1vL5sROZXhzwbPmnCaNo61hC6pPQOH80-0d42ejEr6HyWNejrpvgIry1a9hzMcVm2oWpxQb6vLq_a9ZiUoitnTqNtJkw2-zUoxreJ025VG9viw_q0pMzdwYefUFEQyLaP4qvtJfSWAJhKg1VXZIze-iNOwz-3ZL92nwWsmstPwt2CSKJinPhk2DHLrlaxNlzZSzY_9rREZjHOa6TTA=)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6QZDyLsrvd7f5az9n8f7tfRU59dHGrH3AFtvBfAh2iBbsIpxvTO084QPwVEW2CI4DF85wzST2wamXge8oJ8Hjmo-sPIz78eWxPAIFH-jBLuCXTRuWrPDRdk51r6BUPu8SKcAvfLTPhoe6CcLz0tH_5xzBdDOSOkDF2BLl98_3lcuSBumuP9CbSod02v2BjLGKgJxUoGebStMwFy53qofWcTBF8Ghj-58hUCH9nexzFsI=)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgp5RILvE966B1zrPEx1gtVVJEKJhK7v6Uj3T-CCGxOFUJhsD9d_mtLXcAmfVn3dgow1OqXuHBEfAUPr0qoIGpb2-B5_2Q25QMkI7LorxhYuze-MbkQK63Dw==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElgCGKYCGZlddBAKKiUSqPb5tNgytbim29A4DarVenxxBnTeuSCHwDoLVPae1rbJYqsD4aRjASScPMQ8wXRlfN3ir0nieaBr4hY8waZDc1cL_A95T81w==)
21. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxzAptOm8MgHnA86d-8b871PLmMInnLiixUlZlmXVi6r0E1KpVlfFH12O2dJ0IqhDUr46hIAaJwsulNAnmRQ1GVy5wXG9bQ1F7P2v3u5pHKNZq8UJ_lvs-3ZJhzG-dsAqFOvd8iOya100Gb4UN6eDqpwd0YLPcA3fepg==)
22. [femto-st.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_4zSq1Gp5osgyvUIRcgTij7SEDwxzwLGGQTnwHx0erysy5s9fZBpT_k-ROYJQsOuxBVmqcpZhV_AeOKtvMcDOzb_jGd2FDbp84GQY5zD_kSdl9U43WtsXLmcp12X9n2TeslOk8G618ZnZcDPZnsDZG_MkixRUsCQAnj3sVPYXhCjvvET63xghCnS_aN9O1Ke9qPFAMpAR_fl5QIvjHmYa9bSLSBiaIRt7jNSG_a3Emg==)
23. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdc1m_41TRADstqfWHk2uAs4w6YvFC_zApXs4kQKCmWaXOHAzzcWxBvZc39umqVHI9Olpnlfh01K4G4AkXfSbK35_GTmfvjoJn1nyV08vqtdVyMNj2zRVyJb8FdPv4wzElLvbKQa454SiTZDQjZqjIUjJT8RSaGJBi65SE5O09YUUbgbq8CtBZxc1rspmsbNk8nzI2U4h2SS1GW8pXbx-DFFRZdG-Jn9bnFdPWbjnb1BLpNbSO9VFSrlCA2mU=)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQuBdk6VcvOqkaU1_6zTknf-Nft9p0QS8a8SsM2-QxMXvplu-oldHMVH_AED6y8QgBeU2EgDMCRwCOVj4mnKmA2cCg8Y4lt8O9robmaYo_m3eGaHf4LA==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtVjb4lde7vBjrtOjzWtlGyYJ4aOpCpEFEgJ_UvvyL2LcXYA8gSOgDl5uVmcCAq50ocHYnRs1yhbsgY6jQW06_LOh5Zn9zzMEnQqpoaHYmoLEDa5m-pQ==)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1cBbO7e2gfBWSTbg1S3vitbzjBPx2GVsqQgk9bYyOvtpaO6sN42D3VcXEKSgnwD77v-bmso37WtGatk2HosUO99qK0u_A-NxlVXzibx3EDs1RegCA4JutR04Ahtw7TyGPygMLLEklXJNw)
27. [news9live.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuwSFGjLNiUmHsaiHEcmYLGEdyIDA9251Hzh71waNyVHwGQ_u4Afc68zzEdwmn2WurIM5-UxF6HftNo6UWOs3MrO652-bh0K8JmTw1s1En22g7S40wcQw_lUs_ZgKR96Nefz3V1Kx99gJjXjQtlK3YfDYOaT_kBFR6NsuVHD8drDXHMeA5nXIrrCg3e1O1ht5Utab-89y1OkN68QUv5Vo2oC44umorUDHedXY=)
28. [wolfram.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyQWydFF2QBQ0D8X9OG07HV6r-f4mqYtCam39dQ2ZzmhO72W3AidsxUoAbW2NWN_U0ojhlLNF6YJw1zqA2tOY0fxXYQk0IXyjzqaJxWeuG6ECQLRZ2H3p-Tq0yMu8XxGtHqJcC5mZf6vkITfha6QwrWQ==)
29. [openai.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESIZgA8IqB8_Jebuc40obxeywhLWRC7P8NXCj684-7g7AcDV8psQWK3YDRCQ5ZOkwhq1h3QVhBn_Y1zLStMp4tz3fU2sVgi5FNDbke8o4Y9rAbE9wTYc2iF6lOd5nogiAeNs8t7N-CBrmDl_KuXTqLrZ5bYVzceRPexhNvk5G1Hzhg0g9KkzWub4rs0Sc=)

