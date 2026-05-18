# Forward false-anchor hunt: low-dim topology 2025-2026 'X solved Y' claims (Andrews-Curtis, slice-ribbon, etc.)

**Pythia queue id:** 9
**Tier:** 1
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdWM1lMYXFpb01kU1ZfdU1QaklxSm1BcxIXVjNZTGFxaW9NZFNWX3VNUGpJcUptQXM
**Elapsed:** 310s
**Completed at:** 2026-05-18T20:33:18.927250+00:00

---

# Forward False-Anchor Hunt: Decoding 2025-2026 "Solved" Claims and Breakthroughs in Low-Dimensional Topology

**Key Points**
- It seems likely that public claims suggesting artificial intelligence has broadly "solved" the **Andrews-Curtis conjecture** are overstated; evidence indicates that researchers have instead used reinforcement learning and automated deduction to successfully eliminate long-standing potential counterexamples.
- The famous **slice-ribbon conjecture** remains open. A historic candidate counterexample—the (2,1)-cable of the figure-eight knot—was rigorously proven *not* to be smoothly slice, ruling it out as a counterexample.
- Conversely, a new counterexample candidate for the slice-ribbon conjecture emerged in 2026: the 18-crossing knot \( 18_{\text{nh}00000601} \) was mathematically proven to be smoothly slice in the standard 4-ball but remains unknown to be ribbon.
- Research suggests that sensationalized reports claiming the "negation" of the **smooth 4-dimensional Poincaré conjecture** stem from theoretical physics papers utilizing quantum gravity and Boolean set theory models, which do not constitute a universally accepted pure mathematical proof.
- A homological generalization of the **Property R conjecture** was conclusively proven false in 2026, marking a genuine and verified refutation in 3- and 4-manifold topology.
- Bourgain's **slicing conjecture**, though similarly named to knot slicing problems, belongs to convex geometry rather than low-dimensional topology, and was affirmatively resolved by mathematicians in 2024–2025.

**Introduction to the Hunt**
Low-dimensional topology and combinatorial group theory have historically been domains where conjectures survive for decades, often leading to the proposal of intricate, highly complex counterexamples that resist immediate verification. In the 2025–2026 timeframe, an influx of novel computational methodologies—ranging from large language models (LLMs) and reinforcement learning (RL) to advanced topological invariants like involutive Heegaard Floer homology—has catalyzed a massive re-evaluation of these historic problems. This surge in research activity has inevitably led to public and academic claims that various long-standing problems have been definitively "solved." 

**Navigating False Anchors**
A "false anchor" occurs when a partial mathematical resolution, a physics-based heuristic equivalence, or an algorithmic elimination of a subset of cases is misinterpreted as a global proof. This report conducts an exhaustive forward false-anchor hunt through the recent literature of 2025 and 2026 to separate verified topological milestones from media hype and misunderstood technical achievements. We address the exact status of the Andrews-Curtis, slice-ribbon, smooth 4-dimensional Poincaré, and generalized Property R conjectures, offering clarity for the academic community.

## 1. The Andrews-Curtis Conjecture: AI Advances and Misinterpreted Claims

The **Andrews-Curtis (AC) conjecture**, proposed in 1965 by James J. Andrews and Morton L. Curtis, is a foundational open problem in combinatorial group theory with deep ties to the topology of 2-dimensional CW-complexes and 4-manifolds [cite: 1, 2]. The conjecture posits that every balanced presentation (a group presentation with an equal number of generators and relations) of the trivial group can be transformed into the standard trivial presentation via a finite sequence of elementary Nielsen transformations on the relators, combined with conjugations [cite: 1, 3]. 

The allowable transformations, known as AC-transformations, are:
1. Inverting a relator: \( r_i \mapsto r_i^{-1} \)
2. Multiplying one relator by another: \( r_i \mapsto r_i r_j \) for \( i \neq j \)
3. Conjugating a relator by a generator: \( r_i \mapsto g r_i g^{-1} \)
4. (For the stable AC conjecture) Adding or removing a generator and a relator that are identical, e.g., adding \( x_{n+1} \) and \( r_{n+1} = x_{n+1} \) [cite: 2, 4].

Presentations that can be trivialized using only the first three moves are termed AC-equivalent to the trivial presentation, while those requiring the fourth move are termed stably AC-equivalent [cite: 2, 5]. For decades, mathematicians have proposed families of potential counterexamples, most notably the Akbulut-Kirby series \( AK(n) \) and the Miller-Schupp series \( MS(n, w) \) [cite: 1, 6]. 

### 1.1 Reinforcement Learning and "Super Moves"
In early 2025, widespread media coverage suggested that artificial intelligence had "solved" the decades-old Andrews-Curtis conjecture [cite: 7, 8]. This narrative arose from a study by a Caltech-led team, including Sergei Gukov and Ali Shehper, who applied a novel machine-learning algorithm to the problem [cite: 8]. 

The technical reality of this breakthrough, while mathematically significant, does not equate to a global proof of the conjecture. The researchers framed the search for AC-trivialization paths as a large-scale decision-making process within a reinforcement learning environment characterized by exceptionally long horizons and sparse rewards [cite: 9, 10]. Recognizing that standard off-the-shelf Proximal Policy Optimization (PPO) algorithms struggled with the "maze the size of Earth" search space, the team developed a two-agent scheme capable of learning "hypermovements" or "super moves"—compressing multi-step combinatorial sequences into larger, learnable heuristic leaps [cite: 8, 9].

Using this methodology alongside LLM-driven theorem discovery (synthesizing patterns from autoformalized Lean proofs), the team successfully resolved 753 presentations belonging to the Miller-Schupp family, proving them to be AC-trivial and explicitly ruling them out as counterexamples [cite: 6, 10]. Furthermore, they demonstrated the length reducibility of all but two presentations in the Akbulut-Kirby series [cite: 10].

```text
% Conceptual representation of automated search for AC trivializations
% using an automated deduction system like Prover9
formulas(assumptions).
    % Akbulut-Kirby AK(3) balanced presentation of the trivial group
    % Relator 1: x^3 = y^4
    r1 = eq(mult(mult(x, x), x), mult(mult(mult(y, y), y), y)).
    % Relator 2: xyx = yxy
    r2 = eq(mult(mult(x, y), x), mult(mult(y, x), y)).
end_of_list.

formulas(goals).
    % Find sequence of stable AC transformations to the trivial presentation
    trivial(r1, r2).
end_of_list.
```

Parallel to the RL approach, Alexei Lisitsa published a 2025 paper utilizing the automated theorem prover Prover9 to certify the stable AC-equivalence of the famous \( AK(3) \) presentation to the trivial presentation, corroborating earlier findings by Shehper et al. and further shrinking the pool of viable counterexamples [cite: 2, 5]. 

### 1.2 Verdict on the Andrews-Curtis Status
The claim that AI has "solved" the Andrews-Curtis conjecture is a definitive false anchor [cite: 8, 9]. The algorithm was deployed to hunt for non-obvious trivialization paths (often requiring millions of steps) to eliminate specific potential counterexamples [cite: 7, 11]. While this bolsters confidence in the conjecture and reshapes the landscape of combinatorial group theory, the general AC conjecture remains open [cite: 8, 11]. 

On a purely theoretical front, 2025 also saw advances by Robert H. Gilman and Alexei G. Myasnikov, who investigated the natural epimorphism from the full Andrews-Curtis group \( FAC_k(G) \) to the permutation group \( AC_k(G) \), proving that if \( G \) is a non-elementary torsion-free hyperbolic group, this epimorphism is an isomorphism [cite: 1, 12].

## 2. The Slice-Ribbon Conjecture: Fallen Candidates and New Contenders

In knot theory, the **slice-ribbon conjecture**, originally posed by Ralph Fox in 1962, asks whether every smoothly slice knot is also a ribbon knot [cite: 13, 14]. 
- A knot \( K \subset S^3 \) is **slice** in the standard 4-ball \( B^4 \) if it bounds a smooth, properly embedded disk \( D \subset B^4 \) such that \( \partial(B^4, D) = (S^3, K) \) [cite: 15, 16].
- A knot is **ribbon** if it bounds a self-intersecting disk in \( S^3 \) with only specific, mild singularities (ribbon singularities), which intuitively means the disk has no local maxima with respect to a radial distance function [cite: 14].

Because every ribbon knot is easily shown to be slice, the conjecture questions the reverse implication [cite: 14]. It is a problem of central importance because it touches upon the topology of 4-manifolds and serves as a testing ground for theories of smooth 4-dimensional spaces. 

### 2.1 The Fall of the (2,1)-Cable of the Figure-Eight Knot
For over 40 years, the (2,1)-cable of the figure-eight knot, denoted \( C_{2,1}(4_1) \), was viewed as one of the most prominent potential counterexamples to the slice-ribbon conjecture [cite: 17, 18]. In 1980, Akio Kawauchi proved it bounds a disk in a rational homology 4-ball, and in 1994, Katura Miyazaki proved it is not a ribbon knot [cite: 17, 19]. If it could be shown to be smoothly slice in \( B^4 \), the conjecture would fall.

However, in a landmark result earning the 2025 Frontiers of Science Award at the ICBS, mathematicians Matthew Stoffregen, Irving Dai, Sungkyung Kang, JungHwan Park, and Abhishek Mallick definitively proved that the (2,1)-cable of the figure-eight knot is **not smoothly slice** [cite: 14, 19]. The team utilized recent developments in involutive Heegaard Floer homology—an enhancement of classical Floer theory—combined with the analysis of group actions on three-manifolds to identify a new obstruction to sliceness that classical invariants (like the signature or Fox-Milnor conditions) could not detect [cite: 17]. 

Subsequent work in 2025 by Kang, Park, and Taniguchi extended this to show that for any non-zero integer \( n \), the \( (2n, 1) \)-cable of the figure-eight knot is not smoothly slice, utilizing real Frøyshov invariants and the real 10/8 inequality [cite: 20, 21]. Consequently, this historic family of knots has been entirely eliminated as a threat to the slice-ribbon conjecture [cite: 14, 22].

### 2.2 The Rise of the Dunfield-Gong 4-Sphere and Knot \( 18_{\text{nh}00000601} \)
As older counterexamples are dismissed, new computational techniques have generated fresh candidates. The Manolescu-Piccirillo strategy seeks a pair of knots \( K, K' \subset S^3 \) with homeomorphic 0-surgeries where \( K' \) is slice but \( K \) is not, which would yield an exotic 4-sphere [cite: 15, 16]. In 2025, Nathan Dunfield and S. Gong utilized computational methods to construct a specific homotopy 4-sphere, \( X_{DG} \), to test these boundaries [cite: 16, 23].

In a pivotal 2026 paper, Trevor Oliveira-Smith successfully standardized the Dunfield-Gong homotopy 4-sphere using Kirby calculus [cite: 15, 24]. A profound corollary of this standardization is that the 18-crossing knot \( 18_{\text{nh}00000601} \)—which was embedded in the construction—is proven to be smoothly slice in the standard 4-ball [cite: 15, 25]. Crucially, this specific knot is **not known to be ribbon** [cite: 15, 16]. Furthermore, Oliveira-Smith demonstrated that this knot bounds a fibered handle-ribbon disk in \( B^4 \) [cite: 15, 25].

Because \( 18_{\text{nh}00000601} \) is definitively slice but lacks a known ribbon disk, it currently stands as one of the most viable, low-crossing potential counterexamples to the slice-ribbon conjecture [cite: 15, 24]. 

### 2.3 Verdict on the Slice-Ribbon Status
The slice-ribbon conjecture remains definitively unsolved. Claims that it was "solved" by the elimination of the figure-eight cable are false anchors [cite: 14, 17]. The field has instead experienced a paradigm shift: classical candidates have been obstructed using advanced Floer homologies, while modern algorithmic searches have generated entirely new, highly specific candidates like \( 18_{\text{nh}00000601} \) that require investigation [cite: 19, 24]. Additionally, related structural work continues, such as Andrew Lobb's 2026 proof establishing Khovanov concordance minima for the (4,5) torus knot, generalizing the notion of slice-ribbon minima within concordance classes [cite: 26].

## 3. The Smooth 4-Dimensional Poincaré Conjecture and Physics Crossovers

The **generalized Poincaré conjecture** asks whether every homotopy \( n \)-sphere is homeomorphic to the standard \( n \)-sphere. While solved in the topological category for all dimensions (Freedman for \( n=4 \), Perelman for \( n=3 \)), the **smooth 4-dimensional Poincaré conjecture (SPC4)** remains one of the greatest open problems in mathematics [cite: 27]. It posits the non-existence of exotic 4-spheres—smooth 4-manifolds that are homeomorphic, but not diffeomorphic, to the standard \( S^4 \) [cite: 27, 28].

### 3.1 AI Searches and the Elimination of Exotic Candidates
A standard approach to finding an exotic \( S^4 \) involves finding two knots, \( K_1 \) and \( K_2 \), that share the same 0-surgery, where \( K_1 \) is smoothly slice and \( K_2 \) is not [cite: 28, 29]. If such a pair exists, it would definitively disprove SPC4 [cite: 29]. In 2025, Sergei Gukov, James Halverson, Ciprian Manolescu, and Fabian Ruehle applied Bayesian optimization and reinforcement learning to hunt for ribbon disks (which imply sliceness) in massive families of knots sharing 0-surgeries [cite: 28, 30]. By finding ribbon disks for 843 pairs of knots where one was previously suspected to be a counterexample, their algorithm effectively ruled out hundreds of potential counterexamples to SPC4 [cite: 28, 31]. 

### 3.2 "Negation" of SPC4 via Quantum Gravity Models
A prominent false anchor surrounding SPC4 in 2025–2026 stems from interdisciplinary research at the intersection of mathematical physics and set theory. Physicist Jerzy Król and mathematician Torsten Asselmeyer-Maluga published a series of papers, including in the journal *Universe* (April 2025), claiming the "Negation of the Smooth Poincare Conjecture in Dimension 4 and Negation of the Tsirelson's Conjecture Shed Light on Quantum Gravity" [cite: 32].

The authors approach the integrity of spacetime during a gravitational collapse (e.g., inside a black hole) by utilizing Boolean-valued models of Zermelo-Fraenkel set theory with the Axiom of Choice (ZFC) and the mathematical technique of forcing [cite: 32, 33]. They argue that extending quantum mechanics into this singular domain requires extending 4-diffeomorphisms by automorphisms of Boolean models of set theory [cite: 32]. In this specific classical limit of "fragmented spacetime," they claim the limit naturally leads to exotic smooth 4-spheres acting as gravitational instantons in semiclassical Euclidean gravity [cite: 32]. 

Consequently, they state this "leads to the negation of the smooth 4-dimensional Poincaré conjecture before its final resolution by mathematicians" [cite: 32]. 

### 3.3 Verdict on the SPC4 Status
While the work of Król and Asselmeyer-Maluga represents a fascinating application of exotic smoothness and forcing to quantum gravity, it is imperative to distinguish theoretical physics postulates from pure mathematical theorems. Assuming the existence of an exotic 4-sphere to satisfy a physical model of a black hole singularity does not constitute a rigorous topological proof that an exotic 4-sphere exists [cite: 32, 33]. Therefore, from a purely mathematical standpoint, SPC4 remains entirely open in 2026 [cite: 30, 34].

## 4. The Generalized Property R Conjecture: A Verified Refutation

In 1987, David Gabai proved the famous **Property R conjecture**, establishing that performing 0-framed Dehn surgery on a knot \( K \) in \( S^3 \) yields the manifold \( S^1 \times S^2 \) if and only if \( K \) is the unknot [cite: 35]. 

Attempts to extend this profound result to multi-component links led to the **Generalized Property R Conjecture (GPRC)**, posed as Problem 1.82 in Kirby's list. The GPRC predicts that if a framed surgery on an \( n \)-component link \( L \) in \( S^3 \) produces the connected sum \( \#^n(S^1 \times S^2) \), then \( L \) must be handleslide equivalent to an unlink—the most trivial, obvious way to construct such a surgery [cite: 35, 36]. Handleslide equivalence allows one to slide components over one another, reflecting the algebraic structure of the handle decomposition of the resulting 4-manifold [cite: 35, 36].

### 4.1 The Homological GPRC
Given the difficulty of obstructing handleslide equivalence for classical potential counterexamples (like the Gompf-Scharlemann-Thompson links), mathematicians considered a slightly weaker, homological generalization. It was reasonable to expect that if an \( n \)-component link in \( S^3 \) surgers to the connected sum of \( n \) three-manifolds that possess the *homology* of \( S^1 \times S^2 \), then this link should be handleslide equivalent to an \( n \)-component split link [cite: 35, 37].

### 4.2 The 2026 Refutation
In March 2026, topologists Tye Lidman, Trevor Oliveira-Smith, and Alexander Zupan published a definitive refutation titled "A homological generalized Property R conjecture is false" [cite: 35, 37]. 

The authors explicitly constructed 2-component framed links in \( S^3 \) that surger to a connected sum of homology \( S^1 \times S^2 \)'s, but proved that these links are **not handleslide equivalent, nor even weakly handleslide equivalent, to any split link** [cite: 35, 37]. To achieve this, they utilized results from Hedden, Kim, Mark, and Park, as well as Johnson, regarding specific families of Seifert fibered spaces that cannot be obtained by surgery on a knot in \( S^3 \) [cite: 35]. By building links \( L_n \) with surgeries to \( Y_n \# Z_n \) where \( Y_n \) belongs to this impermissible family, they successfully obstructed the weak handleslide equivalence to a split link [cite: 35].

### 4.3 Verdict on GPRC Status
This is a genuine, mathematically verified "solved" claim (in the negative direction). The homological generalized Property R conjecture is definitively **false** [cite: 35, 38]. While the strict GPRC (yielding exactly \( S^1 \times S^2 \)) remains technically open, this refutation of the homological variant represents a massive step forward in understanding the limitations of link surgeries and 4-manifold handle decompositions in 2026 [cite: 35, 36].

## 5. The 11/8 Conjecture and 4-Manifold Geography

The geography problem for 4-manifolds investigates which pairs of integers can be realized as the signature \( \sigma \) and the second Betti number \( b_2 \) of a closed, simply connected smooth 4-manifold [cite: 39, 40]. For spin 4-manifolds, Matsumoto's **11/8-conjecture** asserts that \( b_2 \geq \frac{11}{8} |\sigma| \) [cite: 39, 40]. 

While Furuta's famous 10/8 theorem established that \( b_2 \geq \frac{10}{8} |\sigma| + 2 \) using Seiberg-Witten invariants, closing the gap to 11/8 has remained a formidable challenge [cite: 40, 41].

### 5.1 Recent Equivariant Advances
In late 2025 and 2026, significant progress toward the 11/8 conjecture was achieved through the study of Pin(2)-equivariant stable homotopy theory and the families Bauer-Furuta invariant [cite: 39, 42]. By analyzing maps that satisfy the "diagram property" (Furuta-Mahowald classes), researchers extracted new adjunction inequalities for embedded surfaces in 4-manifolds with contact boundaries [cite: 41, 42]. 

Specifically, applying these equivariant families allowed topologists to prove that the boundary Dehn twist on the punctured manifold \( K3 \# K3 \setminus B^4 \) is a non-trivial, exotic diffeomorphism in the smooth mapping class group [cite: 42]. 

### 5.2 Verdict on the 11/8 Status
The 11/8 conjecture remains open, though the bounding constants continue to be refined by advanced equivariant gauge theory. Claims of a complete proof have not materialized in the accepted literature as of 2026.

## 6. The Unknotting Problem: Algorithmic Complexity

The **unknotting problem** asks for an algorithmic method to determine if a given knot diagram represents the trivial knot (the unknot) [cite: 43, 44]. While Wolfgang Haken proved the problem is decidable using normal surface theory, identifying the exact computational complexity of the problem has been a prolonged saga [cite: 44, 45].

In 1999, Hass, Lagarias, and Pippenger proved the problem is in NP [cite: 44]. In 2011, Greg Kuperberg proved it is in co-NP assuming the generalized Riemann hypothesis, a condition Marc Lackenby removed in 2016 to provide an unconditional proof of co-NP membership [cite: 44].

### 6.1 The Quasi-Polynomial Time Claim
In 2021, Lackenby announced an unknot recognition algorithm that runs in quasi-polynomial time, a massive algorithmic breakthrough that would suggest the problem is close to being in P [cite: 44]. However, as of late 2025 and early 2026, this highly complex result has still not been fully published in peer-reviewed literature [cite: 44]. 

### 6.2 Verdict on Unknotting Status
While simpler instances of unknotting are easily handled by modern software (like SnapPy or KnotPlot) using Reidemeister moves and Khovanov homology, the general theoretical complexity bound remains in a state of pending verification [cite: 45, 46]. Determining whether the unknotting number can be calculated in polynomial time (class P) remains open [cite: 44, 45]. 

## 7. Bourgain's Slicing Conjecture: A Resolution in Convex Geometry

A frequent source of linguistic confusion in mathematical reporting is the conflation of knot theory "slicing" with **Bourgain's Slicing Conjecture** (also known as the hyperplane conjecture) [cite: 47]. This conjecture resides entirely in the realm of asymptotic convex geometry and probability, asking whether every convex body \( K \subset \mathbb{R}^n \) of volume one possesses a hyperplane \( H \) passing through its centroid such that the \( (n-1) \)-dimensional volume of the cross-section \( K \cap H \) is bounded below by a universal constant \( c > 0 \), independent of the dimension \( n \) [cite: 47, 48].

### 7.1 Affirmative Resolution
In a triumph for the field, Bourgain's slicing conjecture was **affirmatively resolved** in 2024–2025 by Bo'az Klartag and Joseph Lehec [cite: 47, 49]. Building on a recent technical bound related to the covariance of isotropic log-concave measures established by Qingyang Guan, Klartag and Lehec combined Milman's theory of M-ellipsoids and the stochastic localization process to prove that the slicing constant \( L_n \) is indeed bounded by a universal constant [cite: 47, 48]. 

### 7.2 Verdict on Slicing Conjecture Status
Unlike the topological slice-ribbon conjecture, Bourgain's slicing conjecture is genuinely, unequivocally **solved** [cite: 47, 50]. 

## 8. Summary Data Table of 2025-2026 Topological Claims

| Conjecture/Problem | Mathematical Domain | Claimed Status (2025-2026) | Verified Mathematical Status |
|--------------------|---------------------|----------------------------|------------------------------|
| **Andrews-Curtis** | Group Theory / Topology | "Solved" by AI [cite: 9] | **False anchor**: AI only eliminated specific counterexamples (Miller-Schupp, AK) [cite: 6, 10]. The general conjecture is Open. |
| **Slice-Ribbon** | Knot Theory | Counterexample eliminated [cite: 19] / New Counterexample found [cite: 24] | **Open**: The historic (2,1)-cable of \( 4_1 \) was rigorously eliminated [cite: 14]. However, \( 18_{\text{nh}00000601} \) was proposed as a highly credible new candidate [cite: 15, 24]. |
| **Smooth Poincaré (4D)**| Differential Topology | Negated by Quantum Gravity [cite: 32] | **Open**: Physics-based derivations of exotic 4-spheres via ZFC forcing do not equate to a rigorous topological proof of negation [cite: 32, 33]. |
| **Homological GPRC** | 3- and 4-Manifolds | False [cite: 35] | **Verified False**: Counterexample links were explicitly constructed, refuting this generalized conjecture [cite: 35]. |
| **Bourgain's Slicing** | Convex Geometry | Solved [cite: 47, 49] | **Verified True**: The slicing constant is strictly bounded by a universal constant [cite: 47, 48]. |
| **Unknotting Problem** | Computational Topology | Solved in Quasi-Poly Time [cite: 44] | **Unverified**: The quasi-polynomial algorithm is still pending peer review; standard complexity technically remains NP and co-NP [cite: 44]. |

## 9. Conclusion

The landscape of low-dimensional topology in 2025 and 2026 is defined by a rapid acceleration of computational techniques. Reinforcement learning, automated deduction, and modern algorithmic invariants have proven incredibly adept at navigating search spaces that were historically deemed insurmountable. 

However, as this report demonstrates, one must exercise extreme caution when interpreting "solved" claims. The Andrews-Curtis conjecture was not solved by AI; rather, its search space was aggressively pruned of false counterexamples. The slice-ribbon conjecture did not fall with the (2,1)-cable of the figure-eight knot; instead, a new Hydra-head emerged in the form of the 18-crossing Dunfield-Gong knot. SPC4 was not mathematically negated by theoretical physicists, though their work highlights profound crossovers between Euclidean gravity and exotic smoothness. 

Genuine resolutions do exist—such as the refutation of the homological generalized Property R conjecture and the proof of Bourgain's convex slicing problem—but they are highly specific and rigorously bounded. Moving forward, the true utility of AI and machine learning in topology lies not in instantly toppling century-old conjectures, but in acting as a sophisticated sieve: eliminating false anchors so that human mathematical intuition can focus on the true underlying structures of low-dimensional space.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsd1gqJNqQTn66cIYhR6PTUjH2Hw38UYJuyHsTeElJ530WQpFAxqJP-qc_3nYbPVCJmcC8jReWdKyyuzHBARfC7gSPRof5UyeeH_k77K8_ku3sJGSs)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0IwW67ucQHXg9yLl57RnHZHULE7zCuGSLVFHDcoIheOmpnOa4nCU62aMRBbkh1E0XejUM4fnWHU_Khei-pdh4us4pVbN6Js-QmcfXQ7FJ0XRVqpZxSwqu)
3. [quora.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxX0-v3qKmsCnJ3rNdfDr6NSxFPTKiYZ3DXAsTqKfTkIeC-p3IHUdSShwKH1fMQAo1rnRe3qp3dQ7fSaYTirIiUUKOasTs5NxEJJen7iG_tUpPJgToz3Aoi5ZnKtSFF7OYpAttltUwIAe3k6avAYPRf7KkrmUyC4iyF2bjGe6z2ExjqrXn9G3UiPRtaQcdSUFT1an_YAQkb8qVf57sucX2zh3i75xhg9x5iE8PXoHOp6QmrhnB8hH8bw-B4oLd09FNgmtSEOOTvEI=)
4. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFeNXke6kNctURQYZH5GOhDOgqQRO55a0TiWhmRAyK8olcXKBBsY5gpeuECu58wVKomaCJE2OO6RTtwvy5Zgcdg03HNJJX8GzX0YESdnWIxx1vSGqLqpcshdDaNFEclnO5IAGR4noR)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcQEcrw7Z3O2mOjOaUsBuniGXlD6QfU9rSDeW5jT3ulDHv5G4PLp9EQL7Kqbu4quehC-ACNyFq7MdzBF3eZr_V0hOOqShkZYzPjksNlPVv8dinrQ7b)
6. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiAcfUhZPK_8Xq1QqRJ0yyJqNnwgtTha6Qe3SaeBF_ndumCfChpeqYXczxwZiKFlXuLPIOhRz-wKflYrEPezJA31E-42QAG05Imcaa_rNyXZf553CmXQ1ogz8x)
7. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyRtdJd5aej84C4j7w1fo_LMjuCzbmB11DP4e7_l2EgXssqi782kFAJCMboWm_EZI1UKrXKbMMng7180Z4rE_Aog8aT-8IRs96H5-zAmQyUDb93U_w6O06O_4_P5uAMqzRWSm2Xy6NjADTTqM0cLdMV7V8QoZX9QJs0YKd4cQoPfJTg7BZ6BC4noq9ig2JZvR00Cmwlc9Z-YSYeM-Vvw==)
8. [gizmodo.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHDlwwaZqTNjiw0ZSkeIvJTzIRN7_J9qJx7Bq1ivI4Lh0wBia6vxYmDovdb0TtVcaFteaM8w97EKH0xPfu_fwTQSyj-_SxzrWPLVBgvvhglCsdSQ-oW5mAve5XFdImYLKZftceIvystDDamHDBl28OargeS9ch807WXcZluwqoR3ZQKk9nQei7Qk_hOh3VeSAP6arm-OGKkqPrDlhi22J7mN7S2hc=)
9. [edutimes.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXovO-oNcFom9FOSALmD2H_O64Wb63ehAe4fuUAfy3Lkf-MOqD-GuYT2XZzNuB7fCY3KFeovateIbQfui4Dm7JJpWtL7AGg4yPNWzj0hHhU-kNCkXdAcuS9SEXXqxv_lwSfGs=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUC9_UUmTWrPtqcY6of63On2SUGBKoYbrqsU6DOOU6KD01yOs7xuJcOYUHZTKMiMHJ0MO95KXtEDHGQ7F9e6D3UwW6Qz0m4U_e3my5TsGU_R44rtgY)
11. [caltech.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRNksG3GvS06TmXQntD5Ks9847cTNNJNS3vzFwagjQyXgvZAiV4P64urdWRYeeO5lXN3eznqi7ZuaQ41n-SAo1i2U1qVHzhuHPxSnkfPIzhs2J9kQuI4LqzY--4zEPMlWlVFlOGWhkKej0z4gVQfQW808Ftos_1Xa6Ro0ZcYABmNW2j2Sdh0WoP-kMlVvRpiufbkH_C7shleA=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdQboKl9IpwLtX1qsTEOWsh1DobU8VMe_bMEaMV5F-8RNe53NkYYNDjrSv8KPOkGKMf6MBn0ey2sbc8rFR3zDBQeF9DZDW1QfAcom63AscNY-yZwnk)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFt9DrbyRcAMCSRWKDuRXlfGf-PNxiGK_YWeFFmujW_rVmlv12fuXK9jvEqKu-P9JBgTzySPL_FSPIFivOkl8_xhI_tg1Rp8jccegnYwMJbV55EPftRY6e5)
14. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGatUIvV4_58fcXdyDPiobch0Z1W1GVKsQEoGaqzyguM580ZcFQ-jM2dwp4bw-IxLDGdNq8Zn4fnATzCcDXNky9jR1RkHtbE_Aud4udxAR40n8uXiqHszHlFwVIylY3)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-CF0SfGJLp-IBc9ME-y3KNDcFuE-uIAQJnpg8LN8WGfiaPw9qE9QTTcYfIDC4-F0UNIN2VU6EobEIz68mGFjK6z08HD4LKbpeDGIZsNxMi_6NQiqHAknj)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1W1cpmbR95KoMz3TYLG26mEW7iJyv8O7DZCcaPVDSJJdJwghQ-ZzM8FuIjyNrtDKJdnflAOAHqAxXp_sud8-0Gb7OEs6RSjcvNvEWVAQ8qTi2-WiZ)
17. [kaist.ac.kr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMCn0vF1v3ebANoQ4gW1X-iR-JRAR7__duRm8yZ0sdfSi8lb-luIW7BFzrEIwohORVySP-HEFybjb486XieO1E6FNoijviTP5WgoQ2HGqhJskYkB_a1Od4qvDhEurF1Md2tIvKSlPd6X-SOao2QRH1CrigaY-hk0i3uqI1SMNH4FJWxjtWWTretO9A6gYj8gwWlIwAcnXuRqxGbA==)
18. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaZODAbH-CgugH50eXOT5HehKzcdWReP4qL1L1jIZ2cDA56LY8nW0VY8hZXpy5W3FmfOFf3azlmRxj2QP2KO0XkQ-L4IcPY6km_-pOgRTVftuZriu8BA89lkBBxoQCN6M=)
19. [msu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIoMJNRYXZIPaIvKOjhgdFrNdX5WP7vPr_SjHS-btanPS8TuUydek7jlfhTCGaHEtFvI3eU1r_V7CuYu4rfKgVGC8BbZZzjtjd0POFdArOPL4Jaa-RJbZ8TMFt6LeEIgbUinXOae9g9MP2CrXecpX0fp1H)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtPi2ApnH3cxfHhMYIQHZhT3AwMGHtNzkDz87VkomgN_--_5WpeBKGa7rn6XJKGTDHb-ZsYYwklusDYQbSBghPATp1dumc5VO_zdz1lqLAr4AgkI29MeCx1SRtdG2Q_AmYY12jL9sDsKmOPdhRBwtGU5z1sJulkOSO5cHvtLbdDc2Rz8QoWtTMz9xKAPaYDoMwklzLSWO5g65L9JqeFGGp005HWA==)
21. [raspberryip.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFisabf_NWNm1rszfWmVcHGzHPfCU2RGUZY3L7vl6z8agwfsMjjJVaExtLt1mizYDJPIbIgDXRuU-dxjiz1FkmmEUtjjCkh4pJW9SQL1b9vcn1r9eU76fODBugLmgBYZglPwjPN8k2oiLRF8DcQp2Qwv_LmHB3Rp-_kTrKQ73H5h_5F0JH7QWi4lofs6l2Qb17fkbWf1M94ZLg=)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEH8r1XLxpm9JNjlLtMS9WS4B9bJzzFiUyvZjI1nUO7eoCdh4To55SZJG6N7orbp8TLpf87oXW4_3XXsWMbVAWLAZ-b7XqFzarraCvH6j5ytHPcOCjj)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXTkBe9lBzrVWGHxP73EGNUkQ_RwqPL_tCN4nkvwgt3nH1eBkaAC5qD8S2IKbQ0v6ndhycV9oTwDpRJY4fg6MGzArCBGgumbD2xIP2VBufcY03Fg_G1U_7UVhV0IrVGiCfcvrPq8Udh5J9Q2PVSHTreYRBPYv48RXmNoUpWmF0sFkvRYMW-FrWGb1hU9Mh5rA6jmD8nhVL1cxZJrM8KygXHp4ptO2AXUFnrXhJqQkJEDrpLIfXiOv1BQ2RCJu4-jDwr9CYqCoYpCJWzvADpE4=)
24. [toronto.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuVkhs7S1JR2iU4XMicNVms8SYhjSHJjlWHqf3RNfWGx20xmNWPXw_mMznthB-t-ND8OBxzkZ01wp9qWH4Upe3tfPq1HJrGH6k5y1fdxnHKgHhkulTmRixUBsPHII97LNPspNC7ZJJ)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIZtMH-N9jbLPPYhlZFzEF3QYNw1jU0fhqyoe95xOBqoKIzvKJICgDDGXlaJhM76fsFPxbFZvL9IY5yVqc-zbvPzY1-wFhZ6fq4rFzJXOk-BQyCvIU)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMAarsibwGWQ47zEQoZy6l4taB-nwfMdXrevt2QCPp-c5Nl8XRpiiAW0mj1FjffASrRmZScCY4BHzcyyOadMMSQmrcTK46n8GvxnD9nx2NEBrBIxKW)
27. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFa9JIPZoOd-D_Ul5XusFg_LuYk1ibbB6Tmf8h74iBI8lY_KijoYurlNiHOI5DWyBovX5JJ2-_snin7NkPViOS2JSEXQgWnw9xMjn4apOGhlj0q9LIq5qO9e0Cm7B_rYW9KtJoE2uXlGWDzRbhVcpprjXCOpjpQMw==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6JZf51yi8eTm-h78CNiTUFjlYmx0a6y80lJz9STdrNcnBB88_yAh6b6tgO5ZNysg0v9UpIwyhkyKrRJ88rFCa0PfWBH2KkmNxULzDxTlD5YdxorrEf_ah)
29. [albany.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFu4QMo8a1JGhdF7XR-5S5dHNrJ6oAT2kjcZmWJLNaTLy3Muupto3yvxfE9yxYNkh7HEuLcnb0AiuzuRvHhJGQqWQBfLHsdfamzmgOhwPPlCJDGA8ULVM3va4zO4Uqo)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRyNq24wWannqWojWybq5n1Wg3tIZLklbbYZs-3rGMzY64R7np-651-eOKLT-jPCd6Hu2Q4Mffjhc6qpKTdg2FJsFejONyZ5yDIw9VHhLm9deihj0NxZKN7zoqrtf-WIXODIPhVCRFvRbV9QHhDcdOU8IyaWtWpK5TzFLebQ2QDRDo4mNh22R2beotApF4WbT_13fgeBqHY_eodo-GEGp8M6AcAnDaFWmdlVG6rHdhg6IN)
31. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLK5tk_nGtvvOaETJ9vilOkP99juWMYYL6MJicrXtvJ5f0e-iYi3hWXpCH4wloqIEwNEJNHe13O_LrOjRREUZKUaQrMuRumF9Tu18dh00tKxANE8trsNwn9FSg2gFysnOZgMOE8QbdFMzuew==)
32. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeeH3dbkuu03xpEDd6m10giciXEF12m31XKYzE5dO-rxfMJ7aUAx2R2rbw7YRbenOxx8kSIJezBVaFHK4rt4cnxEMd0F0oDWxxTZ6w5y8RklRW7ilHd5suZgm0DA==)
33. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElxDpzJ19BFn0QGpL_cSzoy7izgDKm0NWEELu21a6iIOpvieRqZDJv49dOJ4CYKLnI--ZoFq8CfV8TFIs2NgCn_c-7vKRYE2iDLcEovodwaF3FEvIyhyHr4kDSzeSM5AwFYfGiAn36)
34. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1qGuO4cVt5nrOcQxYRkmGl_WOdgrXlW0_W7YY8jWmh4vXnoFeh94CcYFQlvFgvgRhued1mDnQrk0SwZ_KnR0xa8JAV0y_ZuESZe5Sr_uo1gOgs-xNeDV8gGEOA3Ope9XeFRj0yqeUth-GtLJUxab0hwdPkSkjaXYzUWs=)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-dW7yVmz3zJNNLMKSjDJRFb4D-IBdRNRhSaUDkVj_7wk0ESwkf-rFsGCZWWGdaUNVY2rsQOkMzqbtE2tOL0v94Vx_Z8PGXdKji8thehpGoCPVTvJT)
36. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETvR8JRqGjBb6FqQi3hwQfNlHfrrZObf8uCdYsm5IzgmWXZsVd8MgS-666kx5ngL8do2f8HcUESrKfWDBtDflV2i1FCHGU68Lk_IhNZOCadltlziA5ITo5nypfd72Cg1b_AC1NfYFKV5hAt1rGirrFXP2znr7rltRK0GhhKSg9ETx2hh45)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDJCBeMTISRP-QprMY4ZLRSiVY33k3vGjYH9OYrXuViieBIyMivvLdYdocKfl_c1tetSm629pJi-Mfhql4xI2sqSghM7ijqdd-HW4eItEXXX4dYhmn)
38. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF63hmDLpseAgGmiZfhkKrBs53uCK4g9kAoo7l5aQri47siySuWTnfIgFL2IKqSuheKESg_r4HO4g0pdMVU4eDmlXVAOhwWuvs-bihaFo5Ebp-rQPvsHluA4fT9sDndSfjA2ekj_frhDLnIew-gGZaQ83f9h9XOsg==)
39. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfzRq-Hbr1aZQ0hsHjeWXMBP8UgNnLUt8uE2CpsmB8ihwzMGxrrjn-6GG6K24PeOD5LXlGuFSjbWR9xN0ZqOQxR064q55-JZYjbJldFoAK2o8k2FZOJ5pyHxCvwh3Zu_7PFG16vICSbA==)
40. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfmfo5un1yQfwOWG2R9ber9QSjglmryvePXVyh2_fg_zLOkbaLIwmgkl8EvwHIwa9tygrmIV-fV-M3hSCIRbbCPukA7FNJ1DQMSCZpCHx4gI-9c6dJ9oSJA0uraVaWBDYELf_DaYwa1fa25WYq437mi8mPTayUAK9fi8-RjJ82eRRRd_A5hPsYeBhk9ZBVkpdgw6sx)
41. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEawMcBzT5Dpk962HXV0Y953q0WaXj_ElzY0m47HxBnug4s5G-yspSEs0vcHDJO_WjXCZWWOeOsixlyGhFS_mYt1P6C80BCmKhyeF6a0VVXbiozOUHqhEsm_P0OGYnl_PjPKEny5JeAQRA7OddZgkjO4I0fi7k4RLlgiEzdBP1bvyl497N844ubh_OpGKrUVHrM9Rqjm9HSPXb95LJqarO8N13r5Q==)
42. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHU8_TTYVHy9nugxMP2r2I6CJLGMNKBWTxKLd0KMneAccxKZ4UiFJ6Jt-NObFYNw7L3m-P-f6u3LrlCKU9vtukmvTPvdysQnherVR6ShuSUZVlmDtLx)
43. [c-linkage.co.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHik3TKQr854eE8wx4eoEgEhQ3H-ALVOQFOcdbbYZPeMybRD-dNPa1gIGGVBv0cREOJhUROOOyLjG-e5EutQ4eAXuaOW7RKZr0YeftnJ1Gf3Une1SiPY6q4oIjV118Vr8e85yR8JfdPmhLj_Cae8PbmbQS48SHOFgiDxy-i_CuOgVYQRnW2DG3olbqvYeo=)
44. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyMZ3Vv1QrCFXSYiptzGlrgd3KLraGyA2sTSzsONrsuzbkp3OxViOZOkjFwZR5BXslXTxHZFTjg8n_QzIhjvWATHNFfZCEZiqJyQwBOgJ6YfvfoPnkvv3iF07Mkv2Z27pZPOyNwA==)
45. [epoch.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZQ_GxYAycyXXPABY3mk3IXWWailqdCYLeo9f0mRsMPEu-8y3xyVdQG0IIwhuI7G62Fs2hDWpNxQHqyeK9TW5uz-ippniUKIRbxrrtuBYB_tC3AtaeKyWzyoUN2zVi_Wec4cRT2bXL5lDRejwZP04=)
46. [horizonofreason.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuU30HSW7EcURUNRGGFW78pTxLKbU6WtUTPwIh_AnWh9VyZSBduiMyacGAOdueDBSGlUb1wFyFFcJj86JMkua1WCaYWAQNMCh0tQhvEwX4-8veRigoWrjlFgbyVGsVePsGOsQo-8iof_GKE-ctO7BPjRaZ_aWhERhgbXjbBiFGFLo=)
47. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6_ZSxhPnsTI6J5RwGmeoJhXLnNGDz0gW0gyE72NrJT-7eRQey1Ml2DZEX3i0Mna6r1kFg2Fya9-fSmYWJIy9f0Fc7fECqgmls-L8DVhzrVg3vYzGyIwmVsERKm77RRN7wbKwrfJ989NDgo4Ji7SQwtN0PDq7Hf8VIjtDM9tNbfB0e1yhAu2zDH_xrFtkdJEShqLmnnLLY9cFCNjDtnp_d4lw_-yPR2A==)
48. [gatech.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFL1cL6-b7gROYALaXZcsQiE0hGUC8vfXsBzddW1W9tBzycGYF3zKCDbn5LBWEX0IjpUAJr7KL3hEW-zCcwPZK42ecT5PuJcsLJh8B2WdQ3rTUTdKGgZniIB4KRQgBsBcNzpnq9YuK_PzY=)
49. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGl4i1q1-G6o0W0lrX7elLMOpoc7aNiUZAMmOrub9YEqIu_OFQDt3r6z_I66ijDMvtyNtZKKcavugVdrMCTM3qA6d8lXlBMhj4RqWiSGdZr3_kQ9Ld)
50. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtaTm3SwvTXP9KkWw65VoWd-LVCLkKRuTbrM4evHu4yo_QZiGubMcIqH72Z7v-k5lzRMSUeC8WFb5sUalo8zFTJ2vNgXlWfwHBbgQNxMzassAzBr-QNmz6)

