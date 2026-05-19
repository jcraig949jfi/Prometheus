# TENS-05: Quantum functional bounds frontier

**Pythia queue id:** 42
**Tier:** T1
**Priority:** 1
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChczQzBNYXZXLU0tYWoxTWtQbU1TOHdRcxIXM0MwTWF2Vy1NLWFqMU1rUG1NUzh3UXM
**Elapsed:** 311s
**Completed at:** 2026-05-19T09:36:21.012571+00:00

---

# The Evolution of Quantum Functional Bounds: Extensions, Refinements, and Implications for Matrix Multiplication Complexity

**Key Points:**
*   **The 2017 Breakthrough:** The Christandl-Vrana-Zuiddam quantum functionals provided the first non-trivial universal spectral points for complex tensors, linking asymptotic tensor rank to quantum information theory, entanglement polytopes, and the quantum marginal problem.
*   **Recent Equivalences:** Groundbreaking research in 2026 suggests that the quantum functionals coincide precisely with Strassen’s upper support functionals, resolving a major 35-year-old open problem in algebraic complexity theory.
*   **Algorithmic and Field Extensions:** Extensions such as the "weighted slice rank" and "edge support functionals" have generalized these tools to arbitrary and finite fields. Crucially, the edge support functionals can now be computed in deterministic polynomial time via Harder-Narasimhan filtrations.
*   **Monotones for Higher-Order Tensors:** Recent work separates upper and lower quantum functionals for tensors of order four and higher. While singleton weightings characterize asymptotic slice rank, laminar weightings provide powerful upper bounds on asymptotic partition rank.
*   **Barriers to Fast Matrix Multiplication:** Quantum functionals have been weaponized to prove rigorous barriers against current matrix multiplication algorithms. They reveal that methods relying on Coppersmith-Winograd intermediate tensors cannot prove the matrix multiplication exponent \(\omega = 2\), and that the dual exponent \(\alpha\) for rectangular matrix multiplication cannot exceed \(0.625\) using these methods.

**Layman Summary:**
At the heart of computer science lies the problem of matrix multiplication—a fundamental operation used in everything from training artificial intelligence to rendering video game graphics. For decades, mathematicians have tried to find the ultimate, fastest possible algorithm for this task, searching for the true value of the "matrix multiplication exponent," denoted as \(\omega\). If \(\omega = 2\), it would mean matrices could be multiplied almost as fast as merely reading their entries. To understand whether this is possible, researchers study the "asymptotic spectrum of tensors," a complex mathematical landscape that maps out how different computational problems restrict and transform into one another.

In 2017, researchers Christandl, Vrana, and Zuiddam made a massive leap by introducing "quantum functionals." Drawing inspiration from the physics of quantum entanglement, they created a new mathematical measuring stick (a monotone) to gauge the complexity of these operations. Since then, an explosion of follow-up research has refined these tools. We now know that these quantum tools are perfectly equivalent to classical mathematical structures proposed in the 1990s, and they can be calculated efficiently using modern algorithms. Furthermore, researchers have used these quantum functionals to prove that the current best techniques for speeding up matrix multiplication have hit a hard mathematical wall, strongly suggesting that entirely new algorithmic paradigms will be needed to push the boundaries of computer science forward. 

## Introduction: Strassen’s Asymptotic Spectrum and the Quantum Breakthrough

The study of algebraic complexity theory, and particularly the arithmetic complexity of matrix multiplication, is fundamentally governed by the properties of tensors. Tensors represent multilinear maps; for instance, the multiplication of two \(n \times n\) matrices can be encoded as a 3-tensor \(\langle n, n, n \rangle\) [cite: 1]. The asymptotic algebraic complexity of this operation is captured by the matrix multiplication exponent \(\omega\), defined as the infimum over all real numbers \(\beta\) such that two \(n \times n\) matrices can be multiplied using \(\mathcal{O}(n^\beta)\) operations [cite: 1, 2]. While the naive algorithm gives \(\omega \le 3\), Strassen’s pioneering 1969 work proved \(\omega \le \log_2 7 \approx 2.81\), setting off a decades-long race that has brought the upper bound down to approximately \(2.37\) [cite: 1, 3].

To systematically study optimal algorithms, Volker Strassen introduced the **asymptotic spectrum of tensors** between 1986 and 1991 [cite: 4, 5]. The core idea is to understand the preordered semiring of tensors under the operations of direct sum (\(\oplus\)) and tensor product (\(\otimes\)), along with the restriction preorder (\(\le\)). The restriction \(s \le t\) implies that tensor \(s\) can be obtained from tensor \(t\) via linear maps applied to its legs, which algorithmically means the problem encoded by \(s\) reduces to the problem encoded by \(t\) [cite: 1, 6].

Strassen's profound duality theorem states that the asymptotic restriction preorder is completely characterized by the space of all monotone, normalized semiring homomorphisms from the semiring of tensors to the non-negative reals. These homomorphisms are called **spectral points** [cite: 4, 7]. Therefore, the asymptotic tensor rank, which dictates \(\omega\), is equal to the maximum value evaluated over all universal spectral points [cite: 8]. For more than thirty years, finding non-trivial *universal* spectral points—those that apply to the family of all complex tensors—remained a stubborn open problem [cite: 4, 6].

In a monumental breakthrough published as a preprint in 2017, and subsequently in STOC 2018 and the Journal of the American Mathematical Society in 2023, Matthias Christandl, Péter Vrana, and Jeroen Zuiddam solved this problem by constructing the **quantum functionals** [cite: 6, 7]. By leveraging techniques from quantum information theory, the quantum marginal problem, geometric invariant theory, and moment polytopes, they provided the first explicitly constructed, non-trivial universal spectral points for complex tensors [cite: 4, 5]. 

## The Mathematical Architecture of Quantum Functionals

To understand the extensions and refinements that have appeared since 2017, one must examine the original architecture of the quantum functionals. The functionals map a complex \(k\)-tensor \(\psi\) to a non-negative real number based on optimization over entanglement polytopes. 

For a \(k\)-partite quantum state (or equivalently, a \(k\)-tensor) \(\psi\), one can consider its marginals. If we normalize the tensor \(\rho(\psi) = \psi \otimes \psi^\dagger / \langle \psi|\psi \rangle\), tracing out all but the \(j\)-th system yields a reduced density matrix \(\rho_j(\psi)\). The von Neumann entropy of this marginal, \(H(\rho_j(\psi))\), measures the bipartite entanglement between the \(j\)-th system and the rest of the tensor [cite: 9, 10].

The quantum functionals are parameterized by a probability distribution \(\theta = (\theta_1, \dots, \theta_k)\) over the \(k\) legs of the tensor. The original construction by Christandl, Vrana, and Zuiddam defined the quantum functional \(F_\theta(\psi)\) effectively as the supremum of \(2^{\sum_j \theta_j H(\rho_j(g \cdot \psi))}\), where \(g\) ranges over the action of the general linear group \(GL\) applied to the tensor legs [cite: 10, 11]. This maximization of Shannon/von Neumann entropy over the \(GL\)-orbit connects directly to the moment polytopes (or entanglement polytopes) associated with the tensor [cite: 12, 13].

By proving that these functionals are monotone under restriction, normalized on diagonal tensors, additive under direct sums, and multiplicative under tensor products, Christandl, Vrana, and Zuiddam established them as exact spectral points within Strassen's framework [cite: 5, 8].

## Extensions and Refinements: Weighted Slice Rank and Field Generalizations

A significant limitation of the original 2017 quantum functionals was their dependence on the field of complex numbers (\(\mathbb{C}\)). In fields like additive combinatorics (e.g., the cap-set problem) and the design of fast matrix multiplication algorithms, the underlying field characteristic plays a critical role, making finite fields highly relevant [cite: 14, 15].

### The Weighted Slice Rank
To bridge this gap, Christandl, Vladimir Lysikov, and Zuiddam (2020/2023) introduced a powerful extension known as the **weighted slice rank** [cite: 14, 16]. The concept of slice rank was originally formulated by Tao to streamline the resolution of the cap-set problem [cite: 14, 15]. Slice rank provides an upper bound on subrank but is notoriously not multiplicative.

The *weighted* slice rank generalizes this by assigning weights to different bipartitions of the tensor's indices, thereby encapsulating various notions of bipartiteness in quantum entanglement [cite: 11, 14]. By considering the asymptotic regularization of the weighted slice rank, the authors developed a minimax correspondence between the asymptotic weighted slice rank and the quantum functionals [cite: 15, 16]. 

Crucially, because the definition of slice rank relies purely on algebraic decompositions rather than analytic limits or entropies, the weighted slice rank can be defined over *any* arbitrary field, including finite fields of positive characteristic [cite: 11, 14]. This minimax correspondence provided the first rigorous proposal for what a quantum functional should look like outside the complex numbers, yielding new combinatorial limits for asymptotic restriction problems regardless of the underlying field [cite: 11, 16].

## The 2026 Breakthroughs: Unifying Functionals and Resolving Strassen's Conjecture

The landscape of quantum functionals experienced an unprecedented acceleration of discoveries in early 2026. A trio of interrelated preprints dramatically refined the theory, providing exact equivalences to historical parameters, extending computability, and separating functionals for higher-order tensors.

### Equivalence to Strassen's Support Functionals (Sakabe, Doğan, Walter)
In 1991, Volker Strassen had proposed a family of parameters known as the **support functionals**, denoted \(\zeta^\theta\). He proved that they were spectral points for a restricted subset of tensors known as *oblique* tensors, but it remained an open question for 35 years whether they were universal spectral points for all tensors [cite: 17].

The definitions of Strassen's support functionals and the CVZ quantum functionals bear a striking mathematical similarity, both relying on weighted marginal entropy optimization [cite: 13, 17]. In January 2026, Keiya Sakabe, Mahmut Levent Doğan, and Michael Walter resolved this long-standing mystery. Building on recent convex analysis on Hadamard manifolds by Hirai (2025), they proved that for every complex tensor \(t\) and every parameter \(\theta\), the quantum functional \(F_\theta(t)\) is exactly equal to Strassen's upper support functional \(\zeta^\theta(t)\) [cite: 17]. 

This milestone result provided a direct, affirmative answer that Strassen's support functionals are indeed universal spectral points, closing a major loop in algebraic complexity theory by showing that the pinnacle of 1990s tensor theory and modern quantum information theory point to the exact same mathematical truth [cite: 13, 17].

### The Edge of the Support Functionals and Polynomial Time Computation (Alman, Li, Pratt)
While Sakabe et al. proved the equivalence over the complex numbers, another crucial piece of the puzzle regarding arbitrary fields and algorithmic tractability was solved by Josh Alman, Baitian Li, and Kevin Pratt in April 2026 [cite: 18, 19]. 

They focused on the "edge" of the support functionals—the subset of functionals \(\zeta^\theta\) where the parameter \(\theta\) lies on the edges of the probability simplex \(\Theta\) (i.e., where at least one \(\theta_j = 0\)) [cite: 18, 20]. They proved that not only are these edge functionals universal spectral points, but they are uniquely determined by their behavior on matrix multiplication tensors [cite: 19, 20]. Furthermore, because their methods were purely algebraic rather than analytic, they established for the first time the definitive existence of non-trivial spectral points over arbitrary fields, moving beyond the characteristic zero limitation [cite: 18, 19].

Perhaps most importantly for computer science, Alman, Li, and Pratt drew a profound connection between these edge support functionals and **Harder-Narasimhan filtrations** from quiver representation theory [cite: 18, 21]. Utilizing recent advancements in algorithmic invariant theory, they demonstrated that these edge support functionals can be computed in **deterministic polynomial time** [cite: 18, 22]. This is a massive departure from typical asymptotic tensor parameters (like asymptotic rank or commutative rank), which are generally NP-hard or lack known deterministic polynomial-time algorithms [cite: 18, 23].

### Separating Upper and Lower Quantum Functionals (Botero et al.)
Also in April 2026, a collaboration including Alonso Botero, Matthias Christandl, Thomas Fraser, Itai Leigh, and Harold Nieuwboer investigated the structural nuances of quantum functionals for higher-order tensors (\(k \ge 4\)) [cite: 8]. 

The original 2017 CVZ framework established both *upper* and *lower* quantum functionals based on whether the optimization is over the \(GL\)-orbit closure or just the orbit [cite: 8, 24]. For 3-tensors (the realm of matrix multiplication), and for "singleton" weightings (where \(\theta\) only weights single tensor legs), the upper and lower functionals perfectly coincide [cite: 8, 24]. Furthermore, these singleton quantum functionals precisely characterize the asymptotic slice rank [cite: 8, 24].

However, Botero et al. demonstrated that for tensors of order four and higher, the upper and lower quantum functionals generally **do not coincide** when considering "laminar" weightings (weightings on subsets of legs rather than singletons) [cite: 8, 24]. By leveraging the Kempf-Ness theorem from geometric invariant theory, they provided both qualitative and quantitative separations [cite: 8]. Despite this separation, they proved that wherever the upper and lower functionals do coincide (such as on embedded 3-tensors and W-like states), they anchor new universal spectral points [cite: 8, 25]. Crucially, they showed that general laminar weightings provide tight upper bounds on the **asymptotic partition rank**, an algebraic complexity measure central to additive combinatorics [cite: 8, 24].

## Applications to the Matrix Multiplication Exponent \(\omega\)

The most high-profile application of the quantum functionals, and their spectral counterparts, lies in defining hard barriers against the methods currently used to search for fast matrix multiplication algorithms. 

The prevailing upper bounds on \(\omega\) (currently \(\omega \le 2.372\dots\)) rely almost exclusively on the "laser method" generalized by Coppersmith and Winograd, and later refined by Stothers, Williams, Le Gall, and Alman [cite: 1, 26, 27]. This method utilizes a large intermediate tensor, specifically the Coppersmith-Winograd (CW) tensors, and leverages a process of degeneration and asymptotic restriction to yield algorithms for matrix multiplication [cite: 1, 28].

### Barriers from Irreversibility
In 2019 (journal version 2021), Christandl, Vrana, and Zuiddam utilized the asymptotic spectrum—specifically anchored by quantum functionals and support functionals—to prove severe limitations on this entire family of approaches [cite: 1, 26]. They introduced a tensor parameter known as **irreversibility**, denoted \(i(t)\).

Irreversibility measures the asymptotic failure of Gaussian elimination to bring a tensor into a diagonal form. Formally, it is the ratio of a tensor's asymptotic rank to its asymptotic subrank, and by Strassen's duality, it can be computed by maximizing and minimizing over the asymptotic spectrum: 
\[ i(t) = \max_{F \in \Delta} \log F(t) / \min_{G \in \Delta} \log G(t) \]
where \(\Delta\) represents the universal spectral points [cite: 1]. 

Because the matrix multiplication tensor \(\langle n, n, n \rangle\) is reversible (i.e., its asymptotic rank equals its asymptotic subrank if \(\omega = 2\)), any reduction to an intermediate tensor \(t\) and back implies that the efficiency of the algorithm is bottlenecked by the irreversibility of \(t\) [cite: 2, 26]. Specifically, Christandl, Vrana, and Zuiddam proved that if a method uses an intermediate tensor \(t\) via degeneration, the best upper bound it can possibly yield for \(\omega\) is strictly bounded away from 2, and is limited quantitatively by \(2 \cdot i(t)\) [cite: 2, 26]. By calculating the quantum and support functionals of the small and big Coppersmith-Winograd tensors, they proved definitively that these tensors are highly irreversible, meaning **the current laser method applied to CW tensors can never prove \(\omega = 2\)** [cite: 1, 26].

### Barriers for Rectangular Matrix Multiplication
Following the square matrix multiplication barriers, Christandl, François Le Gall, Lysikov, and Zuiddam (2020, published in *Computational Complexity* 2025) turned their attention to **rectangular matrix multiplication** [cite: 29, 30]. 

The complexity of multiplying an \(n \times n\) matrix by an \(n \times n^p\) matrix is characterized by the exponent \(\omega(p)\). A fundamental constant in this domain is the dual matrix multiplication exponent \(\alpha\), which is the supremum over all \(p\) such that \(\omega(p) = 2\) [cite: 30]. The best known lower bound for \(\alpha\) hovers slightly above \(0.32\) [cite: 30].

The authors constructed a generalized barrier framework encompassing all previously used notions of reductions (monomial degeneration, restriction, etc.) [cite: 3, 30]. By heavily leveraging the quantum functionals and support functionals as "adequate tensor parameters," they numerically computed exact barriers for the degeneration of the Coppersmith-Winograd intermediate tensors [cite: 3, 30]. 

Their findings were devastating for standard approaches: they proved that any lower bound on the dual exponent \(\alpha\) obtained via degenerations of the big Coppersmith-Winograd tensors **cannot exceed \(0.625\)** [cite: 3, 31] (refined to \(0.6218\) in highly specific sub-cases [cite: 32]). This strict numerical barrier greatly improved upon prior limitations (such as those by Alman and Vassilevska Williams, who found bounds around \(0.87\)), proving that while the CW tensors can give *better* bounds than currently known, they are fundamentally incapable of reaching \(\alpha = 1\), which would be necessary to prove \(\omega = 2\) globally [cite: 3, 30].

## Broader Implications: Quantum Information and Combinatorics

Beyond algebraic complexity theory, the evolution of quantum functional bounds has catalyzed deep connections across mathematics and physics.

### Entanglement and Quantum Networks
The framework underlying quantum functionals heavily relies on the **quantum marginal problem**—the challenge of determining whether a global quantum state is compatible with a given set of local reduced density matrices. The geometric structure of these compatibilities forms the entanglement polytopes [cite: 4, 7]. 

In quantum information theory, quantum functionals serve as multiplicative **entanglement monotones**. They have been actively utilized to bound the feasibility of asymptotic transformations between pure quantum states via Stochastic Local Operations and Classical Communication (SLOCC) [cite: 4, 33]. If the quantum functional of a source state is less than that of a target state, an asymptotic transformation between the two is strictly impossible [cite: 9]. This has significant implications for understanding the resource theory of tensor networks (like PEPS) and optimizing the contraction of tensor networks in many-body physics [cite: 9]. Furthermore, related asymptotic analyses have influenced limits on noisy quantum communication, establishing threshold theorems for practical quantum hardware [cite: 33].

### Additive Combinatorics and Geometry
In additive combinatorics, the slice rank method originally emerged to prove that subsets of \(\mathbb{F}_q^n\) without three-term arithmetic progressions (like the cap-set problem) are exponentially small [cite: 34, 35]. The realization that the singleton quantum functionals exactly characterize the asymptotic slice rank over \(\mathbb{C}\), and that the weighted slice rank characterizes it over all fields, has provided a profound geometric and representation-theoretic backbone to what was originally a purely combinatorial trick [cite: 15, 24].

This has paved the way for addressing geometric properties of tensors, such as the *geometric rank*, which further unifies algebraic geometry with the subrank of matrix multiplication [cite: 36]. The partition rank, bounded by the laminar quantum functionals, has similarly seen applications in understanding the limits of decoding corrupted error-correcting codes via bounded depth circuits [cite: 34].

## Conclusion

Since the landmark 2017 construction of the quantum functionals by Christandl, Vrana, and Zuiddam, the mathematical ecosystem surrounding asymptotic tensor complexity has undergone a renaissance. The quantum functionals solved the three-decade-old problem of finding non-trivial universal spectral points for complex tensors [cite: 4, 7]. 

Over the last several years, culminating in a burst of breakthroughs in 2026, the theoretical community has established that these quantum tools are perfectly equivalent to Strassen's classical support functionals [cite: 17]. Algorithmic advances have shown that the edge cases of these functionals can be computed in deterministic polynomial time via quiver representation theory, and field-agnostic extensions like the weighted slice rank have brought the power of the asymptotic spectrum to finite fields [cite: 14, 18]. 

Most impactfully, quantum functionals have provided the sharpest known barriers against the world's best matrix multiplication algorithms. By quantifying the irreversibility of Coppersmith-Winograd tensors, they have proved that new, undiscovered intermediate tensors—or entirely novel mathematical paradigms—will be required to prove that the matrix multiplication exponent \(\omega = 2\), and that the dual exponent \(\alpha\) cannot surpass \(0.625\) using current leading techniques [cite: 1, 30]. The convergence of quantum information theory, algebraic geometry, and theoretical computer science in the study of quantum functionals stands as one of the most remarkable unifications in modern mathematics.

**Sources:**
1. [theoryofcomputing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzdU4-LUy1EuUbzDGr_mKxL_9IOdl60F4qDj-hZAT5xjyuw8ce6m9-qKAmfk4HgkcuK-IUFJjbGRZeLNX4Gid_cETQMF05Ta8_WbyxhJ80oIAxgVQDqRi21N7SoCGMX7aDP1Q3w9Jkko-kWvMSDx-nCFY=)
2. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmzX4m87kUjWX7SGny47_Ex_Kt3pOYFkfTfRsx-mumI-OVkmjJ0ATg5sUaIG9BRTTGnAWNv9Z2ibd_jGfeK1FJD10P1Gp0viee8tFtDDt6hfJ5WexLbiPTrDZ95SS8nqlrfAeE5i2v-f979-jtQ_P3Vt4TsVpFHEN1DmCYJY98x-bG3iZrqzMpMQ==)
3. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRq1L_BTzTBOftAbBBjVo4u0CbQXxbKvSoNDyJcp9OOD7MMjCuCOybgKFvHMZ0DsD8gU5HRsZy0z3I0K4KHJ0GrIc6SeQtJnPMpnA6FJob1lL5dxL8jjjkuRi0rQHMpdxDv9HwXunX-ng2LHfVyKFQ6FVRPSHQNTSbCzu8bxX2_xQyjX6nTBlUwNyFQ00=)
4. [ku.dk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBIYZXVc04_eAJc7LFmJHetQ2aXUf-sPGil97JVTAVtHipXBZhaAKG3EkyjqVeIA-tL2zesgNNxuATgudqOwrGXpARFAgDuKAwY3Kw5EUJ7P14gHEnU8ZYfi4ef2nVq5ruYWjI8_TFvautJF9avgndO8ijBIOqBO1QzNkEyWvACyfoE9MywllJL8R5tc5KMkWZBkQKW6uLlKwVrT0=)
5. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5NVNBWfAY97YSu5dJ60uDXaeIvj2KZ9VXFtNPwwK535gr36MUu_pyk1T7-0Qec5myx0bVrbonKNw5oifqPVMmjB-O2bUWXJIbUUo6_LY-khl4HKUd0J4Pqhe9mJXIxV-gzn5ikrOoIuvYAZ0HVWco3vh7tWt31qnNWTt1wRLKnxqjmZLiLrGMZVf7QKjR3golbXty)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6sQAOd74FLetTKI_GNkt_fIGvKABQF9S4I2xyW3lxvTljUVKkZwwh9CdwmYj4icRtFPruWYNzOmc3sngcldyH0yyZoYTVWU81_cFVyn-O_oVInGF1wg==)
7. [uva.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8swRCsDRqVH_YVM2dg3aSFmYePXi_IglFL_ecDF-51bJR6DoOaotPo310XFWERpstu_jyFZGhqFfkAvmQRRFkePeTkh2OGhEo4IvJiEr4wElPdgjtjmeP2vmsqXrw7fIBO2FttSt3cJiqHi4vBOix-sTRnBR5TIZfln7RwasKEVu6bqUJSz8BEMKRxdfxlEZDnjIrbTmuxqRJjFhnlp0C66fbSpiGGaBTYJ-ru6WVURfY8X4tyyRymSKmeawNrrNMM2MBbO6w_H60)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsPGloh_L7nwtL3x9yv9N7lj_-vq_hxlNHc6MlI4MUJKKjHcfarlfT0uda_F8DGKb8bDnxKumV9lYjKnkXKzEwYCfTQqXxjQypLBvxeMJrENxU_2wynzBdAg==)
9. [quantum-journal.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBwumvZdt5JtvVJKxhk-I8Gzgsmcuk_9MHIr5csgK5J07kE3K-qZHr9ygBSlmdOMV1zKeUdISRNxWz1jbkFrYHs0aReI2ZAa9xNCU4REPEqcJwkAvXGYdYl7MyPoRHJZXtAE0fuoVC_qgjyew2LfAAzaX5XdSt8W3wEnWkqteRf7eq)
10. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMEIttki3BpUgygUBrzL9O5gjvHE1PFnI489lzzRPzqOV6_lDRgRg3O5TkYi8VeDb4ag8qnqy-nhLioW8bmqYp2dOrz9KODVRdBvm_ci0TRDPtDQczNPYFYn4_jYs9-Y2r6Z9rNa4jXQ==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzwtiHl4Tj5rSIzVcevCaFxJVSZAKsZFJ-6HpBUqlDoH1YUnxSNN4ppcZ5rUSp7jJPD84weF6t-oCVZxgkFcAyF0JLuGU9OI5cFD9w6l9O5YmQpQidFQ==)
12. [qutech.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHz38oBReHH1zwfB4XhtbgeU2u8MB_OKvpFjgclojp19liLsWcHzulpzBFh3FSP8kuJtsP1TUnDHi9ve4Yf3Le9Qat1_UtGsQlN7WBijnLayvvQdpu3gtWe8LuK_lMFO1lAklX0P9Fea6NXg-XCC2Yn9-0PxjNi0Zf3mYL0ZQmQDGqcs4JI5siMzA==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8PhToC9rAfrGefaFWtepoRhxpquC0omO9mmi01m4GEPRpFgRE8xHtRaUzAPKMb0uGqPVwop2NPsJk00WweTgVqOAZV0cxovNbjOgPwHt8grMfDGqX4A==)
14. [uva.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHj8aivA7UqVkDGrKSmZO8qTm2D6vfuG4IBbQ8ugENsC1SRsJ-PqToilDP_qDNvU9iu8aZCAaQ7mLSGdvQjbcH09dW6LU9WAiWo7bLpMOoB2iL78_TlYomYdtwe7KH_AvZcyx81A4Kb5u8cu3nA_1ljSpf_9Dk=)
15. [ku.dk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkCuZfZ04i2YRT_li80OrKD2Ey1POzBo3WkplPOZKBya2fjUQQzKNmkzlnLJBZu7skW3A-KjQd2WoZX7K0tvKLoEGt9V3lWP_c3m7raSEzAgU88vqgRmPRVFLAA_ea_k0PiJFDofgDjdJGRwNK_7EI2s3mVcQA3hrWJ4eJhrJECsx6RsNnjGlh22Te_VDSeTFYjpO6rnII2W2k7v6mZfKtmi7dPbYTcA==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmYXO_X3PzRPxrbGXpo4cmFVDcLtyrqEG-wZohqPK_Wh2niYlDK6IfHA8rYRc2c_JmjgqC2Ux0iRbodZd0XOCOqyiFXYl5umUvRwa8mgVsXujv07Pv6w==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHR3f6of0rSfjqENhvOutzNBsxornh5oi62NR0j6kZ4L7i6fvFvmNAHLjAw8NN6uAW0k1FQnJeKJqlLRjm0lcNjGf_fxo9pPS_7vO1h04Y5y0C3dN9fxPa4Nw==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqWViQ-oUq7LA7dKZQYPWHvIZuZZ0MvxK0y6F4NQmW1HPtDES4fB27E7KK2Mab6VODwgC_Sj163DR7L50fSxSpuAO6Bn9gLXP_KWXrRlchAjli2z8Y1bKN7g==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJ8CIsND2efEulCdwrXG5v_w4qNUJB-bsRXbsBM6bKStYZ8LeUlYkhQd8STxF3SMINwlRs0vWV9D_cI73wMeaYdGL5sgNqDEa5wU0F8WzY7IOZfzrX8w==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9mGIQelt4NBAHQF3bJrRytNfZgCEMM-RHDEr4sLq_l9RxRUD2Pl7ATxSEO8S4pTwAf1j8aWSO3m81x885J67IBRRNYKOtPUOe99NBKqUsFBlsqst8rg==)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGphHD9IYvaUBk-uaFaZ87gjmySRhGQRmIEUY_hDwUokt3S3aq25sXELgGeg4aE138Xq-SZySun6TxfhbXqc6IniDXT3LDsUTpBcedOLxQ9-N_xrPxZwCxrBIrDCzqOGRDCNsVe5P-2utfG3Zerqcapn_lT2vt-yNLCzQ4_csc4NoF3hK8EwHFe93aVg0uWQvjdVSdMYcPrtq6EhPLOWy1uk0Ou_HkcxI9hZdyR5wLO4wtvg8lkqT50sJtwlacBSAVK3F4=)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHV5dag5wSQXjpUQEmBqA89SDSrZKRdCN7gThSCyT5f5u6IQe-Jj5nOL1D0Er61tvw-0_CWPfKKjnlL9xfKy0YZ4VETHwGSVp7cyv1ivSshMoHWvxtwrLO5nI2S7gv1wnNPMrLZ31PcgOzuOi446U6lcJoT-D4vPr_ocVH4Z2lsHJCtsoebkf-GWA-B6yYOCjLbnNH-oDM=)
23. [acm-stoc.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdGq1Z3bWCHn43v7ZE-tqWCit_LHTJPiBW1sHmdUqKx0r-g-kRKohXqadObMZe9_kylr2rHp6pWGrTzn3KUJdJUwpYq2ZeobQWQhZ0xsjcH1eMzN3SHACCJSfKZw==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9OyPpJTWNeTWmspBXx_ISCVq3y3OZUcLAjpsWNWjsXmPIjkZ3myhvsPRPYXCibk6Ib5YlWdLC0XnH0A2I_iu7Ox36EiAGYEqiEsPrBgAjhUQrF2aN5g==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMvrpt8SB_F4PWyUek4xgksiTXpih_nr-5ehZ_kQdH298fzm7bloEeHyzHMBs1LCmRdRmbXvcWeaYBYobH1FtMYDd5z4QuJo5wS09qyOwd7YeDzpZOiw==)
26. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPgHfcMrsq_Yq_adcZjRP2qPm_P52iL8G9GNBCCVSKQ9TEF-JbQCjXjMUZl237jES3Jyq-8VpIrgPoTU4g3JMAL8HRdEitEgjaezoTtwrzHq-WQ6ZFlfl145CBPMDEqkMX5JQzq4qvMbx3ugmarsZ0mXenpHAb_2hxyb9m)
27. [huji.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0P74zBjXa8M_D6DtcS1tiMAG2M05kmOqhnWf-VdRQ0OYGGTHC7kDel7WoUjZ2wZytphF_tFhzef9eikXBsZ1HGdqwSgO6gcBg1Y-NrtsJcWuugDWIaJci7CWhSAOP6rnPOAPt8nBAy0D1JBMLSJc6mESUh8yY9ytLkg1QEbZ8Ivs=)
28. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBM66MBJZQruA2l2DiOrgwojeUk_g20P9RUng3QfNrC_-4Ps9wFN-OSFIfcu1C-DUS7L1_DN-8ho6TaEYtOlfxe2W21iM3RAGL5qdk_N1cFd10NAPMETh2TreXFrqFI5IXmhmZemEe8BC16w==)
29. [ku.dk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdWOPTwSzL8s1Yf2zFfvZrDqfiHN7LOSoUEeZVsuVsEsYG9G267zs4RorIi9YHb5xZ5xB8SVT4DGeUhcGGhvd4FUXz3h9k4G9RFkpDvye4xjLD6BjIl3RFLLHwyWUUKdZz8dY_BN6YUPLVfssenOWnoZJe54k2axB8gt7hnO9LL1seuCti94phsEi_JMqV6rvv2J6W)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKX_jwhS5HDBa_vuxnkXHK1kqk-cyJ9bBrBc-R6utAzzv_Z6pxBG-TjTj5kTKE4H31BmEDA1RuZ5TkiDZTlmapvTP-62g5inIo6MxtIMKwRF2BxazcCfdgKg==)
31. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwFlGYhK0PXi_HmN_9oXbXfvLQGb-7R9YRQGqS19Bu2RqAjvFUaLy3nlCQ9w64XWgigxyu-154iHeNinOeGVEOt_8iD4ACDq6aoWTISg8W_0Hd0KBelI3N0r-ELT-zynMsfPTp3R5e7SqT1B7ba6NM66ifJQQgeEFp0hPLhs9-eYeC8lhlZgV7ssja)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEA19Xm9e4Q-z0PW_gyH_Ix5p11V1S3nHC1BbI_ktP_lAw1h2_a55vMZRACsx0k0WMNu3BBs_b7007OEnoHDSF0LFXUlqLdisspmHc8-qU-FSoNgNA7iw==)
33. [eqsi.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlPsURZHn59G0SZmMCgYXg9RU4CNR64keTwpBczzlOn7Hfw7g47xbja0o4KGaTaSqM6qynWU_QcMY7mj1x_pq7VCSifYMymKobjxRz9iXE6HsXKmFdoEmwI8WPWt-fW9KXXCc_2BZIFQ==)
34. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHS_oS9Rgjbk42qmtV8C93Qa3-WbSnLZ0V7Oa0O4svTkztfFtl81oi0GGtXml-q4e7zaV2MTdQWRg7yzgpjPga48n0vhgfh2xq0NVCOnWrnCTyb7Kgndo5Ok6Q1)
35. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKNcWnbgFvUrXRdU-Bc1utI6a0d1btEfxpRLJW5ZvjV_ETMUzDsqY3ZYrawaHWf5XiyWb9Eos71lyE0yyo6yIqdSt3_nr0YO4vigx96wlz_NfV2KhjfNwvWiWnQYarZSpPAeKkDiJ1YnY52ecvWRluuG3qnC5n9cc10XROFQ5XOSjA5dZ9dlRmfy6L6JCAEqlzwh2OWSfEh9AdY8NWUm5umZDz78oouf54mqs=)
36. [google.lu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtDWI-suMN6gxLKaerzuddprGYkvhRyZ-eEwUbNsIH7jF-AfODWno_0PtKtNr-dq6hUh-mRVT88Tr8qxxdEKzQ4IMgHsdXvVXHjufBqnWHwBLc2sBWrOE10C2dXI8WGf1OEWvsPQe3vC1HCKh1S-EnxA==)

