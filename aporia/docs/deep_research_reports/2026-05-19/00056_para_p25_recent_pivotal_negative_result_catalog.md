# PARA-P25: Recent pivotal-negative-result catalog

**Pythia queue id:** 56
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdfVWNNYXRuU0NMR2I5TW9QeTRQN3FBdxIXX1VjTWF0blNDTEdiOU1vUHk0UDdxQXc
**Elapsed:** 316s
**Completed at:** 2026-05-19T11:27:53.607858+00:00

---

# Catalog of Paradigm-Shifting Negative Results in Mathematics (2022–2026)

**Key Points**
* The period spanning 2022 to 2026 has been marked by a highly unusual concentration of paradigm-shifting negative results in pure mathematics.
* Long-standing assumptions in harmonic analysis, algebraic topology, discrete geometry, number theory, and symplectic geometry have been overturned by unexpected counterexamples.
* These falsifications operate similarly to historical turning points, such as the Manolescu-style triangulation falsifications and Tsirelson-style operator-algebra falsifications, by breaking fundamental constraints that mathematicians assumed were true. 
* Many of these disproofs were achieved through interdisciplinary methods, computational discoveries, or the introduction of fractal and $p$-adic mathematical structures.
* The evidence points to a broader trend in which modern computational power and cross-field synthesis are exposing the limitations of 20th-century heuristic assumptions. 

**Introduction**
In mathematics, negative results—specifically the falsification of deeply entrenched conjectures—play a critical role in the advancement of human knowledge. Much like Ciprian Manolescu's disproof of the triangulation conjecture (which showed that not all manifolds can be triangulated) or the recent refutations of Tsirelson's problem in quantum information theory, the sudden collapse of a structural assumption forces an entire discipline to reorient itself. When a widely believed conjecture falls, the "universe of shapes," numbers, or spaces under study is often revealed to be vastly more complicated than previously modeled. 

Between 2022 and 2026, the mathematical community experienced a wave of profound negative results. From a teenage prodigy upending four decades of Fourier restriction theory to the collapse of the 40-year-old Telescope Conjecture in chromatic homotopy theory, these disproofs have sent shockwaves across their respective disciplines. This report provides an exhaustive catalog of these major surprising negative results, detailing the original claims, the individuals who achieved the disproofs, the methodological breakthroughs, and the rigorous citations that mark these historical milestones. 

---

## 1. Summary Table of Falsified Conjectures (2022–2026)

To provide an immediate overview of the paradigm shifts covered in this report, the following table summarizes the most surprising negative results documented over this period.

| **Conjecture** | **Mathematical Field** | **Original Claim (Brief)** | **Disproved By** | **Year & Citation** |
| :--- | :--- | :--- | :--- | :--- |
| **Periodic Tiling Conjecture** | Discrete Geometry | A tile that covers space by translations must do so periodically. | Rachel Greenfeld, Terence Tao | 2024, *Ann. of Math.* [cite: 1] |
| **Mizohata-Takeuchi Conjecture** | Harmonic Analysis | $L^2$ norms of Fourier extensions on curved surfaces bound strictly. | Hannah Cairo | 2025, *arXiv* [cite: 2] |
| **Ravenel's Telescope Conjecture** | Chromatic Homotopy | Chromatic localization $L_n$ equates to the telescope functor $T(n)$. | R. Burklund, J. Hahn, I. Levy, T. Schlank | 2023 / 2026, *Clay Award* [cite: 3, 4] |
| **Local-Global Conjecture** | Number Theory | Permitted residues dictate Apollonian circle packing curvatures. | S. Haag, C. Kertzer, J. Rickards, K. E. Stange | 2024, *Ann. of Math.* [cite: 5, 6] |
| **Viterbo's Volume-Capacity Conjecture** | Symplectic Geometry | The Euclidean ball maximizes symplectic capacities for convex bodies. | Pazit Haim-Kislev, Yaron Ostrover | 2026, *Ann. of Math.* [cite: 7, 8] |
| **Ankeny-Artin-Chowla (AAC) Conjecture** | Algebraic Number Theory | For $p \equiv 1 \pmod 4$, $p$ does not divide $y$ in the fundamental unit. | Andreas Reinhart | 2024, *arXiv* [cite: 9, 10] |

---

## 2. Harmonic Analysis: The Mizohata-Takeuchi Conjecture (2025)

### 2.1 Historical Background and Formulation
Harmonic analysis is a branch of mathematics concerned with the representation of functions or signals as the superposition of basic waves, most notably sine and cosine waves. Pioneered by Joseph Fourier in the 19th century, Fourier analysis has grown to become the mathematical backbone of modern engineering, powering technologies ranging from digital audio compression to telecommunications systems [cite: 11]. 

Within this domain lies **Fourier restriction theory**, a highly active area of research that studies the types of mathematical structures that can be constructed when frequencies are restricted to specific geometric objects, such as smooth curved surfaces [cite: 11, 12]. It was within this theoretical landscape that the Mizohata-Takeuchi conjecture was born in the 1980s. The conjecture originated from studies concerning the well-posedness of dispersive partial differential equations [cite: 2]. In the 1970s and 1980s, the mathematician Jiro Takeuchi examined the initial value problem linked to a perturbed version of the linear Schrödinger equation [cite: 2]. Takeuchi proposed a well-posed condition in $L^2(\mathbb{R}^n)$ that he claimed was both necessary and sufficient for the associated Cauchy problem [cite: 2]. Later, Sigeru Mizohata identified that Takeuchi's argument was not completely compelling; Mizohata proved the condition was necessary, but its sufficiency remained an open question [cite: 2].

The Mizohata-Takeuchi conjecture, in its formalized harmonic analysis context, proposed a specific weighted $L^2$ inequality for the Fourier extension operator associated with a smooth hypersurface in Euclidean space [cite: 2, 13]. It asserted that the $L^2$ norm of the extension of a function $f$ from the hypersurface to $\mathbb{R}^n$ could be bounded, for any nonnegative weight function, by a constant multiple of the $L^2$ norm of $f$, with this constant depending strictly on the supremum of the weight over certain tube-shaped regions [cite: 2]. To researchers, this conjecture was widely believed to be true because it aligned with the intuition that waves on these surfaces would eventually cancel each other out rather than amplifying infinitely [cite: 12, 14]. Had it been proven true, it would have automatically validated several other crucial results in the field [cite: 11, 12].

### 2.2 The Counterexample: Falsification by Hannah Cairo
In a highly surprising development in 2025, the Mizohata-Takeuchi conjecture was disproved by a 17-year-old mathematician, Hannah Cairo [cite: 12, 14]. Born in Nassau in the Bahamas, Cairo was homeschooled and entirely self-taught in advanced mathematics through remote consultations and textbooks before participating in the Berkeley Math Circle [cite: 12, 14]. While taking concurrent enrollment classes at UC Berkeley as a high school student, she was assigned a special, simplified case of the Mizohata-Takeuchi conjecture as optional homework by Professor Ruixiang Zhang [cite: 11, 12].

Cairo became obsessed with the problem and realized that standard attempts to prove the conjecture continually hit rigid barriers. She shifted her methodology, deciding instead to attempt to construct a counterexample [cite: 11, 12]. She successfully built a mathematical function comprising waves with frequencies lying on a curved surface that behaved in ways previously thought impossible [cite: 15, 16]. 

**Methodology**:
Cairo reformulated the entire problem in frequency space [cite: 12]. Using fractional calculus and carefully arranged **fractal arrays**, she demonstrated that, instead of mutual cancellation, the waves amplified each other in specific parameters [cite: 14, 15]. The interference of these waves created highly irregular, fractal-like patterns of energy concentration that expressly violated the limits posited by the Mizohata-Takeuchi hypothesis [cite: 15, 16]. Cairo noted that the counterexample required several tools, including fractals, to ensure the waves did not satisfy the universally studied property of the conjecture [cite: 11, 12].

### 2.3 Impact on the Field
* **Who Killed It**: Hannah Cairo.
* **Citation**: Cairo, Hannah (2025). "A Counterexample to the Mizohata-Takeuchi Conjecture". *arXiv:2502.06137 [math.CA]* [cite: 2].

The mathematical community reacted with profound astonishment. Mathematicians who had spent decades attempting to prove the conjecture, such as Tony Carbery at the University of Edinburgh and Itamar Oliveira at the University of Birmingham, expressed their shock at the results [cite: 14, 16]. The result even triggered the falsification of related mathematical claims; Fields Medalist Terence Tao noted that Cairo's work also established that the Stein conjecture—a weighted $L^2$ version of the restriction conjecture that would have reduced the problem to the Kakeya conjecture—was also false, assuming no epsilon losses were allowed [cite: 17]. 

This Tsirelson-style falsification radically reoriented Fourier restriction theory. By revealing that the "energy" of these functions can cluster on lines and form fractal concentrations, mathematicians now understand that the universe of wave interactions on curved surfaces is exponentially more chaotic and complex than 20th-century models allowed [cite: 16, 18].

---

## 3. Discrete Geometry: The Periodic Tiling Conjecture (2022–2024)

### 3.1 Historical Background and Formulation
The Periodic Tiling Conjecture represents a fundamental intersection between discrete geometry, group theory, and mathematical logic. Formulated independently by Grünbaum-Shephard and Lagarias-Wang, the conjecture asserted that any finite subset of a lattice $\mathbb{Z}^d$ (or continuous Euclidean space $\mathbb{R}^d$) that tiles that space by translations must, in fact, tile it periodically [cite: 1]. 

A periodic tiling is defined mathematically as a tiling that possesses a lattice of translation symmetries; for instance, in two dimensions, there must be two linearly independent ways to translate the entire tiling and perfectly map it onto itself [cite: 19]. Historically, it was well-established that if one allows *multiple* tiles (such as Wang tiles or Penrose tiles), one can easily cover a space aperiodically [cite: 19, 20]. However, the Periodic Tiling Conjecture specifically applied to a *single* tile. The conjecture was known to be true in one dimension and two dimensions ($\mathbb{Z}^2$) [cite: 21, 22]. Given these lower-dimensional proofs, many mathematicians intuitively presumed that the constraint held across all arbitrarily large dimensional spaces [cite: 22].

The problem was also intimately related to computational undecidability and the Halting Problem [cite: 22, 23]. It was known since the 1960s that if the Periodic Tiling Conjecture were universally true, it would provide an algorithm to determine whether any given single tile could cover a plane. A refutation of the conjecture would open the door to proving that the single-tile translational tiling problem is logically undecidable [cite: 21, 22].

### 3.2 The Counterexample: Falsification by Greenfeld and Tao
In 2022, postdoctoral researcher Rachel Greenfeld and Fields Medalist Terence Tao announced the disproof of the Periodic Tiling Conjecture, subsequently publishing their peer-reviewed findings in the *Annals of Mathematics* in 2024 [cite: 1].

Greenfeld and Tao initially set out to prove the conjecture in three dimensions, hoping to generalize the known two-dimensional techniques [cite: 22]. After continually encountering insurmountable barriers, they pivoted their approach, suspecting that the intuition from lower dimensions fundamentally broke down in higher-dimensional space [cite: 22]. 

**Methodology**:
To disprove the conjecture, Greenfeld and Tao did not simply draw a physical shape. Instead, they translated the geometric requirement of tiling into a massive, multi-dimensional logical constraint system [cite: 1]. They engineered a conceptual mathematical framework they likened to a high-dimensional, infinite "Sudoku puzzle" [cite: 1, 22]. 
In this puzzle, the rows and non-horizontal lines were constrained to lie within a specific class of **$2$-adically structured functions** [cite: 1]. The researchers created functional equations that could be encoded back into a single tiling equation [cite: 1]. They then rigorously demonstrated that valid solutions to this infinite Sudoku puzzle did indeed exist, but uniquely, *all* possible solutions to the puzzle were strictly non-periodic [cite: 1]. 

Through this method, they successfully obtained a counterexample in a group of the form $\mathbb{Z}^2 \times G_0$ for a finite abelian $2$-group $G_0$ [cite: 1]. By demonstrating the falsification in the discrete lattice subset for sufficiently large dimensions $d$, they proved that the periodic tiling conjecture is false, which in turn implied the disproof of the corresponding continuous conjecture for Euclidean spaces $\mathbb{R}^d$ [cite: 1].

### 3.3 Impact on the Field
* **Who Killed It**: Rachel Greenfeld and Terence Tao.
* **Citation**: Greenfeld, R., & Tao, T. (2024). "A counterexample to the periodic tiling conjecture". *Annals of Mathematics*, 200(1), 301-363. DOI: 10.4007/annals.2024.200.1.5 [cite: 1].

The disproof of the periodic tiling conjecture ranks as a Manolescu-style falsification. The revelation that single tiles can force aperiodicity in sufficiently high dimensions radically reshaped discrete geometry [cite: 22]. It also built the foundation for demonstrating that translational tiling with a single tile may be formally undecidable in Zermelo-Fraenkel set theory with the Axiom of Choice (ZFC) [cite: 21]. Intuition gathered from two- and three-dimensional spaces was proven fundamentally inadequate for the bizarre, structured chaos possible in higher dimensions.

---

## 4. Chromatic Homotopy Theory: Ravenel's Telescope Conjecture (2023–2026)

### 4.1 Historical Background and Formulation
In algebraic topology, stable homotopy theory studies spaces (or "spectra") where the dimension is allowed to grow to infinity, smoothing out anomalies and allowing mathematicians to study the deep structural components of shapes [cite: 3, 24]. In the 1980s, chromatic homotopy theory emerged as a method to break down stable homotopy theory into an infinite sequence of periodic strata, similar to how a prism breaks light into colors [cite: 25]. 

In 1984, mathematician Douglas Ravenel formulated a series of foundational conjectures that sought to map the fundamental building blocks of complex shapes [cite: 4, 26]. Most of Ravenel's conjectures were famously solved and proven true by a combination of Devinatz, Hopkins, Smith, and Ravenel within a decade [cite: 25, 26]. However, one remained stubbornly unresolved: **The Telescope Conjecture** [cite: 4, 25]. 

The Telescope Conjecture concerned the behavior of chromatic localization under telescoping constructions [cite: 3]. Specifically, for a finite $p$-local spectrum $X$ of chromatic type $n$, possessing a $v_n$-self map, one constructs a telescoping sequence whose homotopy cofiber is denoted $T_v$ [cite: 3]. The conjecture asserted that the stable homotopy groups of this telescope $\pi_*(T_v)$ were isomorphic to the stable homotopy groups of the chromatic localization functor $\pi_*(L_n X)$ at height $n$ [cite: 3]. In simpler terms, it predicted that two specific analytical methods for computing the properties of these infinite-dimensional objects—one utilizing infinite, layered "telescoping" patterns, and another using a localization mathematical shortcut—would universally yield the exact same result [cite: 4]. 

Because the Telescope Conjecture had been proven true for $n=1$ by Mark Mahowald and Haynes Miller in the early 1980s, the principle of Occam's razor led the community to assume it was true for $n \ge 2$ [cite: 27, 28]. However, as the decades passed, mathematical suspicions began to mount against it, though it was considered entirely out of reach [cite: 26, 27]. 

### 4.2 The Counterexample: Falsification by Burklund, Hahn, Levy, and Schlank
In June 2023, the chromatic homotopy theory community was stunned when a team of four mathematicians—Robert Burklund, Jeremy Hahn, Ishan Levy, and Tomer Schlank—announced the definitive disproof of the Telescope Conjecture [cite: 24, 26]. Their work represented the resolution of the last open conjecture from Ravenel's landmark paper [cite: 4].

**Methodology**:
The team's disproof relied on discovering a new and entirely unexpected interface between **algebraic K-theory** and chromatic homotopy theory [cite: 25]. To disprove the conjecture, the team had to identify a new, hyper-powerful invariant capable of detecting properties that traditional Morava E-theory could not see [cite: 24]. 
They leveraged recent massive advances in topological trace methods, specifically the novel approaches to topological Hochschild homology (THH) and topological cyclic homology (TC) [cite: 26, 29]. They relied on fundamental work on "red-shift" phenomena (the redshift theorem of Hahn and Wilson) and descent in algebraic K-theory to construct counterexamples [cite: 26, 29]. 

The mathematicians rigorously demonstrated that for $n \ge 2$, chromatic localization and telescoping do not yield equivalent spectra; algebraic K-theory computed via trace methods and cyclotomic spectra proved that the two methods produce distinctly different results [cite: 4, 27]. 

### 4.3 Impact on the Field
* **Who Killed It**: Robert Burklund, Jeremy Hahn, Ishan Levy, and Tomer Schlank.
* **Citation**: Burklund, R., Hahn, J., Levy, I., & Schlank, T. (2023). "K-theoretic counterexamples to Ravenel's telescope conjecture". *arXiv:2310.17459* [cite: 28]. (Awarded the Clay Research Award in April 2026 [cite: 4]).

The disproof of the Telescope Conjecture is recognized as a milestone achievement that has exploded the universe of topological shapes [cite: 4, 24]. By proving the conjecture false, the team revealed that in very high dimensions (e.g., a 100-dimensional sphere), the mathematical mapping of one sphere to another is infinitely more chaotic and complex than previously theorized [cite: 24]. 

The fallout from this negative result led to immediate international workshops (such as at the Isaac Newton Institute in 2025 and the SLMath workshops) aimed exclusively at understanding the "next horizons" of algebraic topology [cite: 25, 26]. The structural categories of spectra are no longer cleanly equal, pointing to a vastly rich structure of intermediate subcategories that will define homotopy research for the 21st century [cite: 29].

---

## 5. Number Theory: The Local-Global Conjecture for Apollonian Circle Packings (2023–2024)

### 5.1 Historical Background and Formulation
Apollonian circle packings are ancient mathematical constructs—dating back to Apollonius of Perga—consisting of fractal arrangements of tangent circles [cite: 6]. In a "primitive integral" Apollonian packing, every circle in the infinite fractal has an integer curvature (the reciprocal of its radius) [cite: 5]. The collection of these integer curvatures forms an orbit of a **"thin group,"** which is a subgroup of an algebraic group possessing infinite index in its Zariski closure [cite: 5, 30]. 

For over two decades, number theorists accepted the widely trusted **Local-Global Conjecture** for these packings [cite: 30, 31]. It was known that the integer curvatures appearing in any primitive integral packing must fall into specific allowed residue classes modulo 24 [cite: 5]. The Local-Global Conjecture stated that, up to finitely many exceptions, *every* sufficiently large integer that aligns with these allowable modular residue classes will inevitably appear as a curvature somewhere in the infinite packing [cite: 5, 6, 30]. 

This conjecture was deeply rooted in the philosophy of the Hasse principle (local-global principle) in number theory, which posits that if a phenomenon occurs in all local domains (modulo constraints), it must occur globally [cite: 32]. Time and again, massive computer searches and theoretical evidence seemed to support the conjecture, cementing its status as an assumed truth in the field [cite: 6, 32].

### 5.2 The Counterexample: Falsification by Haag, Kertzer, Rickards, and Stange
In a stunning reversal during a Summer Research Experience for Undergraduates (REU) at CU Boulder in 2023, the Local-Global Conjecture was unequivocally disproved by a collaborative team comprising graduate student Summer Haag, undergraduate Clyde Kertzer, postdoctoral researcher James Rickards, and Professor Katherine E. Stange [cite: 31, 32].

**Methodology**:
While exploring the curvatures using code developed by Rickards, the team identified anomalies that defied the accepted conjecture [cite: 32]. They proved that for infinitely many (and likely most) Apollonian circle packings, the conjecture completely fails [cite: 5]. Specifically, they demonstrated that certain entire families of numbers—such as perfect squares ($n^2$)—are entirely "missed" by certain packings, despite fulfilling all the modulo 24 local conditions [cite: 30, 31]. 

The disproof hinged on the discovery of novel **quadratic and quartic reciprocity obstructions** [cite: 30, 31]. The mathematicians proved that these obstructions are strictly a property of the thin Apollonian group itself, and critically, these obstructions do *not* exist in the group's Zariski closure [cite: 5, 30]. This mathematical behavior is highly reminiscent of a Brauer-Manin obstruction in Diophantine geometry, representing a fundamental breakdown between local modular conditions and global geometric manifestations [cite: 5, 30].

### 5.3 Impact on the Field
* **Who Killed It**: Summer Haag, Clyde Kertzer, James Rickards, and Katherine E. Stange.
* **Citation**: Haag, S., Kertzer, C., Rickards, J., & Stange, K. E. (2024). "The local-global conjecture for Apollonian circle packings is false". *Annals of Mathematics*, 200(2), 749-770 [cite: 6].

The falsification of the Local-Global Conjecture caused a massive paradigm shift in the study of thin groups and fractal number theory [cite: 6]. Furthermore, this negative result initiated a cascade of similar falsifications. By late 2025, subsequent research directly extended Haag et al.'s methodology to disprove the Local-Global Conjecture across four other types of integral generalized circle packings: the octahedral, cubic, square, and triangular packings [cite: 33]. The field has thus rapidly reoriented to catalog these newly discovered quadratic reciprocity structures, completely abandoning the classical local-global assumptions for fractal packings [cite: 33].

---

## 6. Symplectic Geometry: Viterbo's Volume-Capacity Conjecture (2024–2026)

### 6.1 Historical Background and Formulation
Symplectic geometry is a branch of theoretical mathematics deeply tied to Hamiltonian mechanics and the physics of phase space. Phase space is a unified geometric structure that encodes all possible position and momentum states of a physical system [cite: 34]. In the 1980s, Mikhail Gromov revolutionized the field with his "Non-Squeezing Theorem," which demonstrated that symplectic manifolds possess an intrinsic global property—**symplectic capacity**—that prevents a large symplectic ball from being "squeezed" into a smaller symplectic cylinder [cite: 34, 35]. Symplectic capacity acts as a rigorous mathematical invariant measuring the "size" of a domain in phase space, remaining constant under symplectomorphisms [cite: 34].

In 2000, mathematician Claude Viterbo proposed the famous **Volume-Capacity Conjecture**. Viterbo hypothesized that among all convex domains of the exact same volume, the standard Euclidean ball strictly maximizes every symplectic capacity [cite: 35]. The "weak" version of the conjecture stated this maximal property of the ball [cite: 34]. The "strong" version of the conjecture went even further, asserting that all normalized symplectic capacities (such as the Ekeland-Hofer-Zehnder capacity and Gutt-Hutchings capacity) actually coincide and yield the exact same value when restricted exclusively to the class of convex domains [cite: 7, 34].

Viterbo's conjecture was heavily supported by immense amounts of theoretical evidence [cite: 7]. It was profoundly influential because a special case of it was proven to be mathematically equivalent to **Mahler's conjecture**, an 85-year-old open problem in convex geometry regarding the volume of centrally symmetric convex bodies and their duals [cite: 7]. 

### 6.2 The Counterexample: Falsification by Haim-Kislev and Ostrover
In 2024, researchers Pazit Haim-Kislev and Yaron Ostrover published a preprint completely disproving Viterbo's Volume-Capacity Conjecture. Their work was formalized and published in the *Annals of Mathematics* in March 2026 [cite: 7, 8, 35].

**Methodology**:
Ironically, Haim-Kislev was initially attempting to *prove* Viterbo's conjecture when she formulated her counterexample [cite: 34]. She and Ostrover utilized the dynamics of **Minkowski billiards** to identify specific convex domains that break the supposed limits of symplectic capacity [cite: 7, 35]. 

The specific counterexample constructed by the team is remarkably simple in hindsight: it is generated by taking the **direct product of two pentagons** (specifically, a symplectic 2-product of Lagrangian convex polytopes) [cite: 7, 35]. Through combinatorial formulas calculating the symplectic capacity (EHZ) of polytopes, they demonstrated that this pentagonal product structure achieves a larger symplectic capacity relative to its volume than the Euclidean ball [cite: 7, 34]. Because the domain is convex and violates the maximal capacity boundary, it decisively disproves the weak version of Viterbo's conjecture [cite: 7, 34]. Consequently, because it proves capacities can diverge based on the shape of the convex body, it automatically disproves the strong version of the conjecture (i.e., capacities do *not* all coincide on the class of convex domains in classical phase space) [cite: 7, 8].

### 6.3 Impact on the Field
* **Who Killed It**: Pazit Haim-Kislev and Yaron Ostrover.
* **Citation**: Haim-Kislev, P., & Ostrover, Y. (2026). "A counterexample to Viterbo's conjecture". *Annals of Mathematics*, 203(2), 603-622. DOI: 10.4007/annals.2026.203.2.5 [cite: 7, 8].

This negative result has reoriented both symplectic geometry and asymptotic geometric analysis. Mathematicians had long presumed that convexity functioned as a rigorous geometric constraint that homogenized symplectic invariants [cite: 34, 36]. By proving that some convex domains can achieve substantially larger capacities than previously thought possible, Haim-Kislev and Ostrover have forced the field to re-evaluate the deep interactions between convex geometry and Hamiltonian dynamics [cite: 34, 36].

---

## 7. Algebraic Number Theory: The Ankeny-Artin-Chowla (AAC) Conjecture (2024)

### 7.1 Historical Background and Formulation
In algebraic number theory, the properties of the fundamental units of real quadratic fields $\mathbb{Q}(\sqrt{d})$ are objects of intense study, intrinsically linked to the computation of class numbers [cite: 9, 10]. In 1952, mathematicians N.C. Ankeny, Emil Artin, and Sarvadaman Chowla formulated a question that was subsequently elevated to a formal conjecture by Kiselev, Slavutskii, and L.J. Mordell by 1960 [cite: 9, 37]. 

The **Ankeny-Artin-Chowla (AAC) Conjecture** is formalized as follows: Let $p$ be a prime number such that $p \equiv 1 \pmod 4$. Let $\epsilon = x + y\sqrt{p}$ be the fundamental unit of the real quadratic integer ring $\mathbb{Z}[\sqrt{p}]$, where $x$ and $y$ are unique positive integers. The AAC conjecture claims that the prime $p$ will never divide the integer $y$ ($p \nmid y$) [cite: 9, 37]. 

The primary motivation for this conjecture was its utility in computing the class number $h(p)$ of the quadratic field via Bernoulli numbers and rational congruences [cite: 9, 38]. The AAC conjecture was backed by substantial empirical data; it was computationally verified to be true for all primes up to $2 \cdot 10^{11}$ [cite: 9]. Despite heuristic arguments (based on the Cohen-Lenstra heuristics) suggesting that counterexamples *might* infinitely exist if Bernoulli numbers modulo $p$ were sufficiently random, no actual counterexample had been found in over 70 years [cite: 9, 39].

### 7.2 The Counterexample: Falsification by Andreas Reinhart
In late 2024, mathematician Andreas Reinhart officially disproved the AAC conjecture through the discovery of a targeted computational counterexample [cite: 9, 10]. 

**Methodology**:
Doubting the veracity of the conjecture due to anomalies found in related composite squarefree integers and "fake" real quadratic orders, Reinhart developed an AAC-specific algorithmic search using Mathematica and Pari/GP [cite: 9, 38]. Implementing small-step and large-step algorithms, Reinhart explored vastly higher prime intervals [cite: 9]. 

Reinhart successfully proved that the prime $p = 331,914,313,984,493$ completely fails the AAC conjecture [cite: 9, 39]. For this specific prime, $p$ does indeed divide $y$ in the fundamental unit equation. Reinhart noted that this counterexample is particularly remarkable because it is one of only two known examples of a squarefree integer $d \ge 2$ where $d \mid y$ and the norm of the fundamental unit is $-1$ [cite: 39]. Additionally, using similar algorithmic techniques, Reinhart concurrently disproved a highly related assumption, **Mordell's Pellian Equation Conjecture**, by finding the counterexample integer $d = 39,028,039,587,479$ [cite: 10].

### 7.3 Impact on the Field
* **Who Killed It**: Andreas Reinhart.
* **Citation**: Reinhart, A. (2024). "A counterexample to the conjecture of Ankeny, Artin and Chowla". *arXiv:2410.21864* [cite: 9, 39].

While driven heavily by computation, the disproof of the AAC and Mordell conjectures settles a seven-decade-old question surrounding the divisibility properties of fundamental units [cite: 9, 10]. The result proves the danger of the "law of small numbers" in algebraic number theory; mathematical properties verified for the first 200 billion primes may still catastrophically fail at $3 \cdot 10^{14}$ [cite: 9, 39].

---

## 8. Conclusion

The epoch spanning 2022 to 2026 will likely be remembered as an era of foundational correction in mathematics. Driven by the advent of massive algorithmic computation, novel combinations of disparate geometric sub-fields, and the introduction of young, unorthodox mathematicians to high-level research, the community has seen its structural heuristics radically dismantled.

From the Tsirelson-style collapse of the Telescope Conjecture to the sudden falsification of the Periodic Tiling Conjecture, each of these "negative results" serves as a profound positive leap forward for human understanding. As demonstrated by Cairo in harmonic analysis, Greenfeld and Tao in discrete geometry, Burklund et al. in homotopy theory, Haag et al. in number theory, Haim-Kislev and Ostrover in symplectic geometry, and Reinhart in algebraic number theory, the failure of these conjectures invariably points to deeper, richer, and far more complex structural truths lurking behind the veil of assumed symmetries.

**Sources:**
1. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuoEV32_6tzRSEpYr6ZY4nhB-jJJEGT4D17kxLACga_OLWYyFwBT-a_HybYbMxL2i6d5ZT4b0gJBo9m-uUnsoa1LP7vtMlT57l8ltaBna96K9qR2cKNzMO1xOl22SXhKU64d0oEuw=)
2. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHve1E3gCAflJR73VOCR11UdJ1pP--PgOiLTsqDSIrLmr-En__CFpgTrcVwmd6S-_TaElafwQhFJs57pjpOg3wKy1SAk8v9LtKqdCsxm5VK54neYOYQelewrGGwqGZYz16zNP8VMXeQSn7I7TsCVDLWRO9I2Zy3pnY=)
3. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6IYMRb95-HCwZ9bwh6UbokxmD--SEMlrF2h_1AQjGift8N5H1JJsp7_jJpQ3wdiUFPQV1pY551psNNN3sxCrqiO1xaJLtG7K1kXAEsYInfU36zX835qj_gyICJOSYAlnBoOBiKxvs5yHwZ1aJFX6pzjFSp0vbpw==)
4. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTsC0l39xdnz49-_6sluZ9BhXnlLHUc9J2Io_RzpQrF94dd9P3OUbwFMVZHznpR7EOPhdWTV-dmGzyW9t2X3oeSZQ_bCNxMnHHjNFY8bXFfCoax6X7UMZ0XttFtZePocAX-dw9yyg13fb2kUMf_J5V-srfe6tDkkRAXccaWUr06cg-Uw==)
5. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFoa98EVZqKa8BUFCmapj_rTSfXWfq9B9CYJ8zEKMgxjuQQjY8R0zjiCTbqOpae0ZviZNLq7ryP9jUyc7nzYqAVhjbJdbooJDynFErE_w1uwgK3NicAaeM5vrJZlHJ44Es=)
6. [uni-bonn.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHp_tSOieWe7Cc3jaQBaddkFEQR6kF5I0z9kl43NQg1XXcgZMHgiPGh5GuigDkjWgcJxK-w_vDFOHO8urDGTj7PRTx-jjkpE3r3eFBRz-h3XuJdhCAATrw3MvWaJIOGDk4DnxNlF2K3dLTQGo1G0Ygu4YahTYN5JmFVCtV57BwGHSUh2xI=)
7. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbiximXN3cEBhagzJdQGmYEfSjWCBYASbfX07h43bTsou0gQnUU5gDBXEwkmRwp4KLzWBekM_9lpJMaq8SxOyGBQXlVOV_5HGLY_0f_TkvbpjpVP2KcWyOs2WrgCnNTW6og-D83dzLazkMJYJjufpuPxK5mocNCreDSX1KbFv9vu4wFmZwBoGnYiCS)
8. [tau.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUqptNBmB2apNHEGpEVFobOtRYP8qvu7JX6uBAMV44KCNUYrk60afBQiLxn4diUfgae3gnZIiIjs17Ssvmq1HXqul_EWZPMYVUynJnHxrd94mtR3qrwVjSOxkihB_JxXopQHlfl-mlwFb121GRZ-09h7vDgkttx4v9QSSHJAjid-u07UpG)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6GIWkRaU-_Q0rwcFYF-mNQ0T43KIYTYoO2XxmQuJDvsksDVZXAC3-4jyWNephvJkoacujdN6WOln-irZpZrrXFmu8OmuVOD6QRGJc-swwao29E9cI7w==)
10. [uni-graz.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESMt3Zjc94gaEGqoIRibudYka9X1Y-MHWSVbMGdzyhzHsGZlsi5XB87hooHIiNs7dpfqjIYl_z4Vf0BGVViVR_VyAHdnvl7VFhKxZmenwuVSWqRXg6onalfc5djWAgIRdOttTUcXU=)
11. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLA0QzI7ZPwASWRonAMSJW5IVN12Gq4YqE17bKa_n36WIW8OVY7bzXSg5hg1ezLTKn6VHFrgpc0kT9Wo9CRQB81e-OYf0DocdAf2ppyjCg8pm_5glAPgfd-Vvr6z1YViIyUVL1I4l1Hrj42R8TUsYUfFfV_m1JFqEtSG0ntEFThlRc7zGJw6-aafscIJA7NGop7Q==)
12. [elpais.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxTUgNXrmVUrgVkk1Qo5_HISU6TQ_uFuLcOU1to9PDcJVURB72H1-gvVh3j6kV1E3fOkgz4BN-l7qKDce6lDfT-bhj_YwBA9q0PKbGkC4VsO3nCv00Ng6eISyjQvjkL_0zbI6x6SdVBPPYns9Fh20mruArURpuqWAYPzHXAxm_rAxpe-JOyKmotScTIEWcFDqYC1vpnVtb_gFngLt9g4DJJOk7O3W2ngzES3OYbu5CKX5_KY-YULRhCw==)
13. [bham.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJbZ4-zJnqXh3NZNehAotQMVLhQcSDf7HgynxmStn58bKi4TfxE2t9Zrms7Jg-JvLPHVZcc_xgWTQ-kFYWtH4pxnAyHXk8wewVXwPZL0yUkob960ktck0JZx2PKeRNIGMo35bDaXomzDzjc3ui1qPKf-vsHPkJ)
14. [futurism.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLaTb7db4_hbnYnxFlToEpP5hSm-pybb93AupDeRoct6ul0SDfQCQdjSK74S6FDydgxZ5jcdTajGB3JXWe5s50b1AgPXph-Pz_xdNAZqEmnrgy_2j2Q7HSQYo_t2OZYEEbiF-IqOoriNTMUhBwLQ==)
15. [sgmk.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCHEEk6j6vdu1LjOUkGumsSa6pmE-blPNRY1DnjeyeSFNLtzfdNxRxjU4uy1m5ztuXkC5gLKYbjNtc3xkMWDzRDBdgTutjLYvX6dPO9nTMNbpBgsVlPBR1t-LyqZiwLddLHgKYF14U6rdUIUtGZfxz2sigl-JCpGA3jeVOTlGgebjSTKSz)
16. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEeVBPXsWbxK1yE-hBidTjBmVtcw7v8VJemqElYLwdEuOp3BY-yiX29xj-pBrakVr4BPNLnRBF5_yYG1jlZKk710msWxnWEcuVo_qHNX_D7hurqV0l5uiINCiX5sV77QZJ8Efpe8I2bWyzBhw-KVLhY1ETTyZ3CCZ31CvHgtGmUW2c-AqGV9CfJwoWnMts=)
17. [mathstodon.xyz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExJ79Y064PIDyjkE1GTxyBHhPrIKDVZ9HB7m7QbyFSFdVaRZE6bwlh_NrqTqtHeVYDOCYIO6qn1U9qNoAIQh1vhMQ1bQPxTv1GWUtloEm0Ub-m4j4W9tlqBY3aZaGYGqPMWIva)
18. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFj-9qAICYQvr0zgfkNq8XP1MJGLJfRSQL0nihHkN5llR1U8ZYoy9lI3BbsC0L9J8VjhV6fbqW6R6uL13nBCSF7Mm_XtTylD-Mu3wXDeyDg7P1yRP70vDzKt4pGxaWWR1pbZWBFJpQ3zigASMPrEZ0lu-gxqcFGE0BIx0xnrzud6Q==)
19. [mathstodon.xyz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_GOwyR28KUuHKEPTTEtyUDO2C7J0Vx5tQGI_ktiNIpSzMV36tV2JpAeL_olB7MC9_dQSzeu7vCcTGSGyVqYrypNhgyK1yRYSQgYkrRCoIZDIr_WicgfXpxloTQfBiqAe80aeA)
20. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1ulqCWtl9XqfcHAk8ks3LwoG50VFM18FSoP0bAmbEeDIiweBokzuG578CrnHt-OblNq7V6axTW2mlbZiZ2S3ICFqv8BfAfmnLkJThID55I2DapQohH1kdOULsbfbSG3kpb0AlxiGoFvVzCWoNEIO7WidwAQ==)
21. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMQdNQAqG9g15CgczLst_8jkMjo9upXojypSvyFzqZxlPs1zog_co5csnDSjnP_DBj-7FPj7Lh7E_NesGVaHxH6pxnCq0BIhahUs2oSGiJ4MsgkuXJlOJeGUcQEW8U3yfQKAAyv-Ij2PoBVG5K378tk5pCHWUaTm9q-NOPU2ZxLvRJRFDzQOLpbq9mzg1Z_fbZZm0=)
22. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0IO27d0xrYUmau7rXWi56qnJS-Q5HQVCgkZwBhO2Y3xU0Lost4bRyauHvPomiVHA6ktYUMN7g9T4FG3Rfgx7bHrfhvLeDw7PiqQlWAQ2nOe7dB4empCSfeofESIfHwnA3bZmaeKA7jOXO8k_4N3JnIuLNRvfU5CNibRRvLR_YCDGgIDDRhmAyZdnSWTvmtvGV8Q==)
23. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENBOwckQAKS6CglgedRueYS9tQl4KbTD6ESf_FsQvlYjEZQjPIcT9KY1e6g-kYQ67T70CYCgzxoKVKeW8g2ea4rp0fOC6QCfSf108wk_Q1cpvYuMa9T3BXQ2Q-4bMfs0pBxAJbDXX0kPDuJVXCFtDpoqVtQj_YQ_6Bm8UC1KM=)
24. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfanldI5sle_K4RY8kC0mEjs0eHJ3msBuLahR7eThzQNAlOEmhh_DFkwnR8fJ44JOywIqD4gNrk4c-0CXBGEL-wsqTMV9MpkFSyy66r5-Km1xg8JvN_CJSeo5eKhzjNAu5UKQfO7_NJpAn0o57CqI0WtBfqG4H3Mfh5ktW9PWf5i63MmuJn0PIu4CvRwGshUszLogeYQQCiPygIoE=)
25. [newton.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5m-0PvvjKjzFDENsUnfHJuT1irsqr4UAhdhXxuHyMQuUvcMes1I3ZDtcIqxbQvlLGtQjAxHOS6KNEkzZAEwDYCNJZtbqoqFRebgCw0MJoZWmD7GiSAaCSj0Ci3w==)
26. [slmath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGM4EXyOdtfCat-lKFVKZd40wA1_eoUrv_k0aWiOaqzxhS-wyVnm1zozXnd2vPnyklw8u8ZsWGWO_3HPg6aVKDANF6NOC-nHt8gRkcIw8tmqsF2KWdmYZdrTOmW)
27. [mfo.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpPWNGiUHYjyXmOEnDPHjugL1lGFwHpZ2JoWWG2dS07CJZMbvlCqXvVZozY5l52F_72VhzkgxYNZaq1byfSFLi20bjjZQLNDkPanYB33cyIgEmE8r2LeTPqsF7p7FJXoTm0sBp_CV5cMIcveTolyKC8IA1WG1q4MtOEYlm6Hdefe0AoC4b_CYHt79blK_sESdaOA==)
28. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIRn8QryN6p_R2nWzsJBcajH_PH8ZnBkk3S0yoWUK51IOSXXO4m1cSIQl7GrMnVsvimZ33yWE5ZCusJZiNhK2c028K0Zo1HyAIvNSLBa9yaJZKDEF34__8QidbOQMw3PYCnm-ved9tdg==)
29. [strickland1.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMKVyMdX7Ytix2puiG7RjKslczhCi0r-JEld4HmifoasCh9zIVFfqAFaH0NwpNJS0tV3YdNb20ciLjNKboXXhlsET5fVGrYzkMKsaGhjN13KEwC-1gYLsCtAuSt6h8tR0KeA==)
30. [oregonstate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpmNBfaN6V9VWPx9_WfrXmzWdBzpIY7QkcRhHhbmS11hVVo8fsTPNEorN0gyuygjAMRfUgNbdmXppB7mTGHpsQ9K7EKztybEBc2gRCk_7QU5jMD4ATnSgvTQxW_sKa3yjF8gRWQbbJaiFPO0ALoCT2Cjq4tK-EzY_TvcqnKcT-tmTm9Ycrz_qMjvAt2gSUhdtD5WxwQRzJPkwzppORVRjulfU0pFe10cMsACGAo90tVA==)
31. [colorado.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkh0zMLH-h2SQqhu92DFxWmH3Se3jfaeN3XnT9efScrnGE8ZLsO3_XtsVCfvVurFUtDjiWGGEDvxhx71h4d_aTE0I88DbokaJ8J1Rnqx86au1vzz6p20JaM2klPDnmsbHMahe0xKjNiRByIv5HTUl-A72FfcbJZZ1T65WY8C4FfYT6hbMqTQ-U6ZyQloXB-A==)
32. [colorado.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJZQ43MZF1RYw3WKK0g00dvVdzhk5Nfnj_yvO40l7JkfTz8Nr2Vm_GPhkrcMsddVZzxPzug0FzTLdGEpUtHnytAL9bbPkZe_dOY69pWQyxXYDNDHkzofs_7ftkOrX5n644rl8E6-7E9pftpnEZwsjyIzZZijygZKpi4QHmEE2C498N182uiNES6mg_WeAPt6t0M6O_rNytnsJno3c=)
33. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGcCXSCUDUYFtqyYChkWTeR8MrOC-wTzayzERSZThzD70B8C_HusB-hv2rjs4NjtJpR0CsAEkqczILZTel72WYqFJCeoYUqHUyXPIBcO73OS6gZdRJmQ==)
34. [mathinstitutes.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEU-or_vLrvdsnSJG0o1Wz8n1uFw2DwlTMZB3Fty9RlEv05c55VYVP02H0Am5DmBUTg2WMEzYpvH180tl7lOJHw3NCsTOUPmVVln1JvIqb5na4yEN7M6_WUWu18HlY15Z0fsX3ZEnuMc0OwksjLy4KL2uPm9JjkXEUUEwF6DD_WYgyc5bhtrXcHzSCguKDsF2_LjAIK93lA4WHkWCplIDXQtf8-jw==)
35. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvK5p7CJcX_VIuwQIAewxGWGpy9OhslUOe46Vzsc20zpFDN19DW15biUdSBcBRw5VyxgTogFKoP8z7z_dx2klnjsOb0rBWgogLH38x39xML2cmBr96H_zdd8JFGR6hKF1Y6YFZiITkQtmhtmCGJ4-PSq4sWNR3MjL4uFrQ2giPKhCT9o89tUnQOjlytyAcG0q_YBgdSEjKObU2LocmaCvHUQv3djut1nk=)
36. [huji.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFszMHr-BlTtW019iqa-qEPVZW1CYNhqJDYwULPPkqC0YDV78ghrJLCuZsmGzSsATSGO8TDk9tP9iDKfc23LwNmdeJYK6qOpAo9Y9yGDpaEh0KnPqUbvJVSR2Vdbstx16QzqRgtTUVz437P3innm7cUu2X6ymwdlADo8Mg2lQstTzxzKHrg3ZrMOma1Wia0vNnXGM0AIws=)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0x5cp0ce6VItgE75X9RdkJzYMtRcU40gmiLz6qbba6lVbx-_dRnA3MyYaaSkkwdEeC3MJOq9jYsSRkpA-v9_wL4XSo83kO99VBHCFVsBoZfLD4pnDh01pDg==)
38. [uni-graz.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_FD2TirtjjPZd30F0fJLBpYpxKXRQzg7rDXuH54p6Fnx6f_gGQIWW4PvP18mwIvg9P2G-qS-SjpOEIBaYvdGczGIWfWYGp3irf5zFLAyiYB9y4eLs8NjwmX5yztpnlQ==)
39. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEr8y0X_mdNr3OZBncvyFo2NnG1Mlv3wx_3kiHBi8mUmuzHpKDekK2UQ7saM41Bitm3RYL1Cw7metET1SQT__yrzquJem7lQX1QZ9DxjgQmI98mXpfO9UMPqQ==)

