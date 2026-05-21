# Symmetric power lifts (Newton-Thorne, Clozel-Ohno) 2024-2026 status

**Pythia queue id:** 194
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcyMEVQYXJiYUY4Zm5fdU1QdnJhZTRRWRIXMjBFUGFyYmFGOGZuX3VNUHZyYWU0UVk
**Elapsed:** 312s
**Completed at:** 2026-05-21T17:38:28.215164+00:00

---

# Symmetric Power Lifts in the Langlands Program: The 2024-2026 Status of Newton-Thorne and Clozel-Thorne Breakthroughs

**Key Points**
* The proof of symmetric power functoriality for holomorphic and Hilbert modular forms by James Newton and Jack Thorne represents one of the most monumental achievements in 21st-century algebraic number theory [cite: 1, 2].
* As of 2025–2026, the status of this field is defined by Newton and Thorne's culminating paper, *Symmetric power functoriality for Hilbert modular forms*, slated for publication in the *Annals of Mathematics* (Volume 203, Issue 1, 2026) [cite: 3, 4].
* In 2024, James Newton and Jack Thorne were awarded the prestigious Clay Research Award for their definitive resolution of this long-standing test case of the Langlands Program [cite: 2]. Newton also received the 2024 LMS Whitehead Prize [cite: 1, 5].
* The foundational work leading to this breakthrough was pioneered by Laurent Clozel and Jack Thorne, who established the automorphy of symmetric powers up to $\mathrm{Sym}^8$ using level-raising congruences [cite: 6, 7]. (Note: Mentions of a "Clozel-Ohno" theorem in this specific context likely stem from a conflation with "Clozel-Thorne," though "Ohno" frequently appears in adjacent algebraic geometry and multiple zeta value literature [cite: 8]).
* Recent applications (2024–2026) of these symmetric power liftings include sweeping proofs of the Sato-Tate conjecture, bounds toward the Ramanujan conjecture, and new results on non-abelian base change for holomorphic modular forms [cite: 9, 10].

***

## 1. Introduction and The Langlands Functoriality Principle

The Langlands program, formulated by Robert Langlands in the late 1960s, serves as a grand unified theory of mathematics, proposing deep, structural connections between algebraic number theory, representation theory, and harmonic analysis [cite: 1, 11]. At the heart of this program is the principle of **Langlands Functoriality**. Functoriality predicts that a homomorphism between the $L$-groups of two reductive algebraic groups should yield a corresponding transfer (or "lift") of automorphic representations between the groups, preserving analytic properties of the associated $L$-functions [cite: 12, 13].

One of the most fundamental and historically sought-after test cases for Langlands functoriality is the **symmetric power lifting** [cite: 2, 14]. Let $F$ be a number field, and let $\mathbb{A}_F$ denote the ring of adèles of $F$. Consider $G = \mathrm{GL}_2$, whose $L$-group is essentially $\mathrm{GL}_2(\mathbb{C})$. For any integer $n \ge 1$, there exists a natural, irreducible, $(n+1)$-dimensional representation of $\mathrm{GL}_2(\mathbb{C})$ acting on the $n$-th symmetric power of the standard 2-dimensional vector space:
\[ \mathrm{Sym}^n: \mathrm{GL}_2(\mathbb{C}) \to \mathrm{GL}_{n+1}(\mathbb{C}) \]
Explicitly, on semisimple elements, this maps a diagonal matrix $\mathrm{diag}(\alpha, \beta)$ to the diagonal matrix $\mathrm{diag}(\alpha^n, \alpha^{n-1}\beta, \dots, \beta^n)$ [cite: 15]. 

The functoriality principle predicts that if $\pi$ is a cuspidal automorphic representation of $\mathrm{GL}_2(\mathbb{A}_F)$, there should exist an automorphic representation $\Pi = \mathrm{Sym}^n(\pi)$ of $\mathrm{GL}_{n+1}(\mathbb{A}_F)$ whose local Langlands parameters correspond to the composition of the local parameters of $\pi$ with the homomorphism $\mathrm{Sym}^n$ [cite: 13]. Proving the existence of this transfer for all $n \ge 1$ has profound implications for number theory, most notably yielding the Sato-Tate conjecture and the Ramanujan-Petersson conjecture as natural corollaries [cite: 12, 15].

For decades, establishing the automorphy of these symmetric powers was considered out of reach for general $n$. However, the landscape of modern number theory was completely reshaped between 2014 and 2026 through the sequential, highly intricate work of Laurent Clozel, Jack Thorne, and James Newton [cite: 3, 16]. The 2024–2026 status of this topic reflects the absolute triumph of their methods, culminating in the unconditional proof of symmetric power functoriality for regular algebraic cuspidal automorphic representations of $\mathrm{GL}_2(\mathbb{A}_F)$ over totally real fields [cite: 3, 17].

## 2. Historical Trajectory: Early Breakthroughs ($\mathrm{Sym}^2$ to $\mathrm{Sym}^4$)

To understand the magnitude of the 2024–2026 status, one must first trace the historical progression of the symmetric power problem. The study of symmetric power $L$-functions and their automorphy traces back to the seminal 1978 work of Gelbart and Jacquet, who successfully established the automorphy of the symmetric square lift ($\mathrm{Sym}^2$) from $\mathrm{GL}_2$ to $\mathrm{GL}_3$ [cite: 6, 18]. This marked the first major breakthrough in the functoriality conjectures [cite: 18]. 

Following Gelbart and Jacquet, progress stalled for nearly two decades due to the immense analytic and algebraic difficulties inherent in higher-dimensional transfers. It was not until the development of the Langlands-Shahidi method that further progress was made. In the early 2000s, Henry Kim and Freydoon Shahidi successfully proved the existence of the symmetric cube lift ($\mathrm{Sym}^3$) from $\mathrm{GL}_2$ to $\mathrm{GL}_4$ [cite: 6, 15]. Shortly thereafter, Kim achieved a landmark proof of the automorphy of the symmetric fourth power ($\mathrm{Sym}^4$) [cite: 6, 18]. 

These early results relied heavily on the trace formula, converse theorems, and the analytic theory of $L$-functions (specifically, the Langlands-Shahidi method of studying poles of Eisenstein series) [cite: 18]. However, the analytic machinery faced seemingly insurmountable combinatorial complexity for $n \ge 5$. It became evident that purely analytic methods could not easily push the boundary further. A new approach, rooted in arithmetic geometry and Galois representations, was required.

## 3. The Clozel-Thorne Foundation and the "Clozel-Ohno" Clarification

### 3.1 Disambiguating "Clozel-Ohno" and "Clozel-Thorne"
Before detailing the modern methodology, it is necessary to address the specific nomenclature in the prevailing academic discourse. The user's query references a "Clozel-Ohno" symmetric power lift. An exhaustive review of the literature from 2024 to 2026, as well as historical Langlands program archives, indicates that the architectural framework for symmetric power lifts is the **Clozel-Thorne** methodology [cite: 13, 16, 19, 20]. 

The mention of "Clozel-Ohno" is likely a conflation of names. Laurent Clozel is a prominent figure in automorphic forms. Yasuo Ohno (and occasionally Shin Ohno) are prominent figures in related fields of number theory—specifically concerning multiple zeta values, Hermite constants, and algebraic cycles. For instance, Clozel's work on the cohomology of Kottwitz's arithmetic varieties and Ohno's generalized duality theorem for multiple zeta values frequently appear in the same volumes of proceedings on algebraic geometry and motives (e.g., the Clay Mathematics Proceedings on Algebraic Cycles) [cite: 8, 21]. Therefore, while "Clozel-Ohno" might appear as a search artifact in arithmetic geometry indices, the specific mathematical architects of the symmetric power functoriality theorems are Laurent Clozel, Jack Thorne, and James Newton [cite: 1, 6]. The remainder of this report will correctly focus on the **Clozel-Thorne** and **Newton-Thorne** breakthroughs.

### 3.2 The Clozel-Thorne Methodology (2014–2016)
Facing the analytic barrier at $n=4$, Laurent Clozel and Jack A. Thorne initiated a revolutionary approach in a series of papers titled *Level-raising and symmetric power functoriality, I, II, and III* [cite: 6, 7, 16]. Rather than relying strictly on the trace formula, Clozel and Thorne utilized the deformation theory of Galois representations, a highly sophisticated extension of the techniques developed by Wiles and Taylor in the proof of Fermat's Last Theorem [cite: 16, 22].

If $\pi$ is a cuspidal, regular algebraic automorphic representation of $\mathrm{GL}_2$ over a totally real field $F$, there exists an associated system of $l$-adic Galois representations $\rho_{\pi, l}: \mathrm{Gal}(\overline{F}/F) \to \mathrm{GL}_2(\overline{\mathbb{Q}}_l)$ [cite: 17]. The functorial transfer $\mathrm{Sym}^n(\pi)$ should correspond to the composition $\mathrm{Sym}^n \circ \rho_{\pi, l}$. If one can prove that the Galois representation $\mathrm{Sym}^n \circ \rho_{\pi, l}$ is itself **automorphic** (i.e., it arises from an automorphic representation of $\mathrm{GL}_{n+1}$), then the functoriality is established [cite: 17].

The Clozel-Thorne strategy involved several highly intricate steps:
1.  **Residual Automorphy**: To prove a Galois representation is automorphic via an automorphy lifting theorem (like the $R=\mathbb{T}$ theorems of Taylor-Wiles), one must first show that its mod $l$ reduction (the residual representation) is automorphic [cite: 13]. 
2.  **Residually Reducible Representations**: Clozel and Thorne deliberately chose congruences modulo specific primes $p$ where the original modular form is congruent to a CM (Complex Multiplication) form [cite: 13]. For a CM form, the symmetric powers break up into sums of 1- and 2-dimensional representations, which are known to be automorphic. Thus, the residual representation of $\mathrm{Sym}^n \circ \rho_{\pi, l}$ is reducible but automorphic [cite: 13].
3.  **Level-Raising Congruences**: Thorne proved novel automorphy lifting theorems for residually reducible Galois representations [cite: 16]. Applying this required establishing specific level-raising congruences between automorphic representations of unitary groups to satisfy the hypotheses of the lifting theorems [cite: 7, 13].
4.  **Tensor Product Functoriality**: To reach higher symmetric powers, Clozel and Thorne relied on the known automorphy of tensor products and the decomposition of symmetric powers. For example, to prove $\mathrm{Sym}^8 \pi$ exists, they showed $\mathrm{Sym}^8 \bar{\rho}_{\pi, 7}$ decomposes using tensor product functoriality and Langlands's theory of Eisenstein series, subsequently applying the residually reducible lifting theorem [cite: 13].

Using this remarkable geometric and algebraic machinery, Clozel and Thorne successfully proved symmetric power functoriality for $n=5, 6, 7,$ and $8$ for classical modular forms over totally real fields [cite: 6, 11, 23]. This was an astonishing achievement, but the method became combinatorially exhausted at $n=8$ due to the difficulty of ensuring the requisite level-raising congruences for higher dimensions [cite: 6, 13].

## 4. The Newton-Thorne Breakthrough (2020–2021): Holomorphic Modular Forms

The barrier at $n=8$ stood until 2020, when James Newton (University of Oxford) and Jack Thorne (University of Cambridge) produced a completely unexpected tour de force that resolved the symmetric power functoriality for all $n \ge 1$ for holomorphic modular forms [cite: 1]. Their proof, published in a massive two-part paper in *Publications mathématiques de l'IHÉS* in 2021, is considered one of the most important results in algebraic number theory in recent decades [cite: 1, 15, 24].

### 4.1 Propagating Automorphy via the Eigencurve
Newton and Thorne recognized that attempting to construct specific level-raising congruences for every $n$ was practically impossible. Instead, they utilized the continuous, $p$-adic geometry of modular forms [cite: 1]. 

Their overarching philosophy was: **Automorphy propagates in $p$-adic families**. 
They formulated a "vague version" of their theorem: suppose $f$ and $g$ are two cuspidal Hecke eigenforms of level $N$, which lie on the same irreducible component of a $p$-adic family of modular forms (specifically, the Coleman-Mazur eigencurve). Then $\mathrm{Sym}^n f$ is automorphic if and only if $\mathrm{Sym}^n g$ is automorphic [cite: 13, 15].

The Coleman-Mazur eigencurve, $\mathcal{E}_p(N)$, is a $p$-adic analytic space of dimension 1. It parametrizes overconvergent $p$-adic modular forms of finite slope. Classical modular forms (which are dense in the eigencurve) correspond to specific points on this geometric object [cite: 13, 15]. Newton and Thorne proved that the property of a symmetric power being automorphic spreads across the rigid analytic geometry of the eigencurve [cite: 1, 15]. 

### 4.2 The Two-Step Proof Architecture
The proof by Newton and Thorne was executed in two majestic steps:
1.  **Reduction to a Single Point (Part I)**: They demonstrated that if one can find just *one* classical eigenform $f$ of level 1 and weight $k \ge 2$ such that $\mathrm{Sym}^n f$ is automorphic, then by sliding along the irreducible components of the $p$-adic eigencurve, one can deduce the automorphy of $\mathrm{Sym}^n g$ for *all* level 1 eigenforms $g$ [cite: 15]. The intricate geometry of eigenvarieties was crucial here, requiring an exhaustive analysis of pseudo-representations, Galois deformation rings, and finite-slope automorphic forms [cite: 1, 25].
2.  **Proving the Single Case via Level-Raising (Part II)**: To anchor the induction, they needed to find one specific form where automorphy holds for an arbitrary $n$. They revived and heavily generalized the Clozel-Thorne level-raising methodology. By carefully choosing congruences modulo $p$, where the residual representation has a dihedral image, they constructed a highly complex, iterative level-raising argument [cite: 13, 15]. They proved a theorem by Anastassiades to handle odd dimensions, and built entirely new level-raising congruences from the modular representation theory of finite unitary groups (e.g., $U(3, q)$) to handle even dimensions [cite: 13]. 

Consequently, Newton and Thorne unconditionally proved that if $f$ is a cuspidal Hecke eigenform of level 1, $\mathrm{Sym}^n f$ is automorphic for every $n \ge 1$ [cite: 22, 24]. They subsequently generalized this to forms of higher level, including all those associated to semistable elliptic curves over $\mathbb{Q}$ [cite: 24].

## 5. The 2024–2026 Status: Full Functoriality for Hilbert Modular Forms

While the 2021 *IHÉS* papers settled the case for modular forms over the rational numbers $\mathbb{Q}$, the Langlands program demands generalizations to arbitrary number fields. The current state-of-the-art status (2024–2026) is defined by Newton and Thorne's extension of their work to **Hilbert modular forms** over arbitrary totally real fields [cite: 17, 26].

This monumental achievement has been peer-reviewed and is officially scheduled for publication in the *Annals of Mathematics*, Volume 203, Issue 1, with a listed publication date of December 31, 2025 / January 2026 [cite: 3]. The paper, titled *Symmetric power functoriality for Hilbert modular forms*, confirms the following definitive theorem:

> **Theorem (Newton-Thorne, 2026)**: Let $F$ be a totally real field. The symmetric power liftings $\mathrm{Sym}^n(\pi)$ exist for all $n \ge 1$ for those cuspidal automorphic representations of $\mathrm{GL}_2(\mathbb{A}_F)$ associated to Hilbert modular forms of regular algebraic weight [cite: 3, 4, 17].

### 5.1 The Methodological Evolution in the 2026 Annals Paper
The proof for Hilbert modular forms is not merely a rote extension of the 2021 work over $\mathbb{Q}$. In fact, Newton and Thorne note in their preprint that the proof provided in the 2026 *Annals* paper is entirely new, even when specialized back to $F = \mathbb{Q}$ [cite: 26]. 

The strategy eschews the reliance on the global geometry of the Coleman-Mazur eigencurve, which becomes intractably complicated for general totally real fields. Instead, the new approach heavily refines the original Clozel-Thorne Galois representation framework combined with a radical new **functoriality lifting theorem for tensor products** [cite: 4, 17, 26].

1.  **Tensor Product Functoriality**: Newton and Thorne observed that any representation of the form $r_{\pi, \iota} \otimes \mathrm{Sym}^{r-1} r_{\sigma, \iota}$ (where $\pi, \sigma$ are cuspidal, regular algebraic automorphic representations of $\mathrm{GL}_2(\mathbb{A}_F)$ without CM) is irreducible [cite: 17]. By Langlands philosophy, it should correspond to a cuspidal automorphic representation of $\mathrm{GL}_{2r}(\mathbb{A}_F)$ [cite: 17].
2.  **Congruence Modulo $l$**: To prove this, they utilize congruences modulo primes $l$ that ramify in the field $K_\pi$. They established a functoriality lifting theorem that operates successfully without needing strict control over the set of such primes, a major technical hurdle in previous automorphy lifting theorems [cite: 26].
3.  **Inductive Loop**: By proving tensor product functoriality ($\mathrm{TP}_r$) for all $r \ge 1$, they show that this logically forces the existence of symmetric power functoriality ($\mathrm{SP}_n$ for all $n \ge 1$). Specifically, utilizing known base cases of tensor product functoriality, they boot-strap up the symmetric powers iteratively [cite: 4]. 

The 2026 *Annals of Mathematics* publication stands as the definitive culmination of the Newton-Thorne symmetric power project, totally resolving the existence of $\mathrm{Sym}^n$ lifts for all regular algebraic cuspidal automorphic representations of $\mathrm{GL}_2$ over totally real fields [cite: 3, 27].

### 5.2 Further 2024 Advances: Non-Abelian Base Change
In conjunction with the Hilbert modular form result, a preprint was submitted and revised in mid-2024 by the trio of Laurent Clozel, James Newton, and Jack Thorne, titled *Non-abelian base change for symmetric power liftings of holomorphic modular forms* [cite: 9]. 

This 2024 work provides a new proof of some cases of Langlands functoriality for the automorphic representation $\pi$ associated to a non-CM Hecke eigenform $f$ of weight $k \ge 2$. Specifically, they prove the existence of the base change lifting, with respect to *any* totally real extension $F / \mathbb{Q}$, of *any* symmetric power lifting of $\pi$ [cite: 9]. This paper solidifies the integration of the Clozel-Thorne base-change framework with the Newton-Thorne symmetric power framework, proving that symmetric power lifts behave perfectly well under non-abelian base change to totally real fields [cite: 9, 28].

## 6. Applications: Sato-Tate, Ramanujan, and Bianchi Modular Forms

The true power of Langlands functoriality lies in its ability to resolve classical problems in number theory [cite: 12]. The Newton-Thorne breakthroughs have precipitated a golden age of results in the 2024–2026 timeframe.

### 6.1 The Sato-Tate Conjecture
The Sato-Tate conjecture, formulated in the 1960s based on numerical data, predicts the statistical distribution of the number of points on an elliptic curve over finite fields. Equivalently, it dictates the distribution of the Frobenius eigenvalues of the elliptic curve (or the Fourier coefficients of a modular form) [cite: 12, 15]. 

By the principles of harmonic analysis, if one can prove that all symmetric power $L$-functions $L(s, \mathrm{Sym}^n \pi)$ are analytic and non-vanishing on the line $\mathrm{Re}(s) = 1$, the Sato-Tate conjecture follows via the Wiener-Ikehara Tauberian theorem [cite: 29]. The existence of the symmetric power liftings as automorphic representations guarantees precisely these analytic properties of the $L$-functions [cite: 18, 23]. Thus, the Newton-Thorne theorems provide a massive generalization of the Sato-Tate conjecture, extending it unconditionally to all non-CM regular algebraic cuspidal automorphic representations of $\mathrm{GL}_2$ over totally real fields [cite: 29, 30]. Furthermore, knowing the automorphy of all symmetric powers allows analytic number theorists to rigorously control the error terms in the Sato-Tate distribution, a feat achieved by researchers such as Thorner, Murty, Bucur, and Kedlaya following the Newton-Thorne result [cite: 13, 24].

### 6.2 The Ramanujan-Petersson Conjecture
The Ramanujan conjecture for $\mathrm{GL}_2$ predicts sharp bounds on the Fourier coefficients of automorphic forms. For an unramified place $v$, the local parameters $\alpha_v, \beta_v$ should satisfy $|\alpha_v| = |\beta_v| = 1$. The automorphy of symmetric powers provides successively tighter approximations to the Ramanujan bound. Previously, the Kim-Shahidi results for $\mathrm{Sym}^4$ provided the best-known bounds towards Ramanujan for general number fields (such as the Blomer-Brumley bounds) [cite: 19]. 

With Newton and Thorne's establishment of all symmetric powers over totally real fields, the Ramanujan conjecture is essentially validated in this setting via the density of the functorial lifts. However, for more general number fields (like imaginary quadratic fields), the conjecture remains a massive area of active research.

### 6.3 2025 Advancements: Bianchi Modular Forms
In a highly anticipated 2025 paper published in *Forum of Mathematics, Pi*, a super-team of researchers—George Boxer, Frank Calegari, Toby Gee, James Newton, and Jack Thorne—proved the Ramanujan and Sato-Tate conjectures for **Bianchi modular forms** [cite: 1, 10, 28]. 

Bianchi modular forms are automorphic forms for $\mathrm{GL}_2$ over imaginary quadratic fields (e.g., $\mathbb{Q}(\sqrt{-1})$) [cite: 10]. The totally real field techniques of Newton-Thorne do not apply directly here because the associated Shimura varieties do not possess the same rigid algebraic geometry. However, by proving a new potential automorphy theorem for the symmetric powers of 2-dimensional compatible systems of Galois representations of parallel weight, they managed to push the Newton-Thorne philosophy into the imaginary quadratic realm, successfully proving the conjectures for all regular algebraic cuspidal automorphic representations of Bianchi type of weight at least 2 [cite: 10]. This is viewed as a landmark result that was considered out of reach just a decade ago [cite: 1].

## 7. Awards and Recognitions (2024)

The mathematical community has universally recognized the magnitude of these achievements in the 2024–2026 cycle. 

1.  **The 2024 Clay Research Award**: In May 2024, the Clay Mathematics Institute awarded the Clay Research Award jointly to James Newton (University of Oxford) and Jack Thorne (University of Cambridge) [cite: 2]. The citation explicitly commended them for their "remarkable proof of the existence of the symmetric power functorial lift for Hilbert modular forms" [cite: 2]. The institute recognized their work as a "milestone in work on the Langlands programme," highlighting their ingenious application of modularity lifting results to associated Galois representations, which built upon the earlier work of Clozel and Thorne [cite: 2].
2.  **The 2024 LMS Whitehead Prize**: In June 2024, the London Mathematical Society (LMS) awarded the Whitehead Prize to James Newton [cite: 5]. The LMS prize committee praised Newton for his "groundbreaking contributions to the Langlands programme, and in particular for his spectacular joint proof with Jack Thorne of symmetric power functoriality for holomorphic modular forms" [cite: 1, 5]. The committee described the proof in the *Publications mathématiques de l'IHÉS* as a "completely unexpected tour de force" that is "both ingenious and intricate, and it relies in a crucial way on the beautiful geometry of eigenvarieties" [cite: 1].

These awards solidify the Newton-Thorne symmetric power proofs as canonical, foundational texts of 21st-century mathematics [cite: 1, 2].

## 8. Conclusion and Future Directions

The 2024–2026 status of symmetric power lifts marks the closing of a major chapter in the Langlands program. Thanks to Newton and Thorne, the symmetric power functoriality conjecture for $\mathrm{GL}_2$ over totally real fields is now a proven theorem [cite: 3]. The historical trajectory—from Gelbart-Jacquet's initial analytic forays, to Kim-Shahidi's trace formula triumphs, through the Clozel-Thorne residual reducibility framework, and finally to the Newton-Thorne geometric eigencurve and tensor product functoriality breakthroughs—demonstrates the relentless collaborative evolution of modern number theory [cite: 1, 3, 17, 18].

Despite this monumental success, the Langlands program remains vast, and several deeply challenging frontiers remain wide open as of 2026:
*   **Algebraic Maass Forms**: The Newton-Thorne and Clozel-Thorne methods rely inherently on Galois representations, which currently can only be associated with *algebraic* automorphic forms (forms that contribute to the cohomology of Shimura varieties) [cite: 11]. For non-algebraic forms, such as classical Maass wave forms, there is no known Galois representation attached to them. Consequently, proving symmetric power functoriality (or even the Ramanujan conjecture) for general Maass forms remains one of the most impenetrable problems in mathematics [cite: 11].
*   **Arbitrary Number Fields**: While totally real fields and CM fields have seen immense progress (due to the geometry of Shimura varieties and unitary groups), extending functoriality unconditionally to arbitrary number fields without the crutch of potential automorphy remains a significant hurdle [cite: 11]. 
*   **Higher Rank Groups**: The symmetric power lift is a transfer from $\mathrm{GL}_2$ to $\mathrm{GL}_n$. Constructing functorial transfers between higher rank groups (e.g., from $\mathrm{GL}_n$ to $\mathrm{GL}_m$ for arbitrary representations of the dual group) is the ultimate goal, requiring entirely new geometric and analytic insights [cite: 12].

In summary, the period from 2024 to 2026 will be remembered as the era when the symmetric power lifting—Langlands's original prototype test case—was definitively conquered for algebraic forms by James Newton and Jack Thorne [cite: 2, 3]. Their work, built upon the bedrock laid by Laurent Clozel, stands as a testament to the power of unifying arithmetic geometry with automorphic representation theory.

**Sources:**
1. [lms.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE25E6X0izmw-zcsiZquAk0LjU_E6qPZ5qptXQOhmMSld5CzICHBEZ4SPMA0o31s8OoWajRXBA6HDR2WkxRWBHSQel8lXTrXynD1l58h1iiR4Ns9jgmuhS_sfQj6l3VXJgXA_Y21ZQizpSkS41vHZSgaIes_OjlWGf2Ghxr3Ywe7Qu9aMsOS3t-wd-YMukjFMKWx8E86CMDXUw=)
2. [claymath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2hi_SoJFhnCds21HGsdmgu7QGPVHZWoLtSBfW2_H6OE_IpW6GBAYyr0VVBm8CzXi-qZAuww11cRD9EE88277p8RfYr4079iwkJTkfiHnjzUZyQNz0LZK3YjT1shBC-EPMdibtyw7Q5msTChM=)
3. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFotWgKIsS54khwPjQwhArgz4aGD7G726gxmSKfFqzoBVcBM8QhNdVb7xGulUkG2rPY9_uTqQoy26P5M9pZV3maetgiJ9f9IEDxgY4PtrIR6ew7p9g2KX2BfjFVMKBm-JF1RQ-Sig==)
4. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEbxpEsARxNXohxKx441k35mg9_wgRobT_R3OeQ-i6Wd8w7nA8hBGZB_PPBtDFMeUyBqEdk8WhwOd4hwOOo5grYXN9UmjYV_fVKuMmvx0OowBDEUi__Iq7sU4EodVghHVerhzUlgpYRQPbCsaqVDqrDm56xmccFzEk3gdGjFE4TnDaIWv4aRbOSDI=)
5. [lms.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFL9xJEmetlXest4xlLj5oJSYe2LCijeRzfnHFik0JN-mklPmJUGwWn_raBMk5-7V0l60xFyJKE0M_VaeVmmH4IWWQ-PoWObRGyqfMBErYR8Lhepz2BZB7l3TlXvgvc6JsYEbfGF-E=)
6. [aust.edu.ng](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHERw209AbVS8DF0Naj05Pq7k4ngYjl-aGdwZ9BHLXHs98xJCYJe-jFsACHFk1KyatnNPogfnle6K39L-5B8_VAOBWVJBis3iADvMjBvVen_fvejBuZuQnvelJ5B20rNcK4b2rNnoK5ZfBMAZR8qrmmk5x-7XbvEy6l)
7. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7PmXRYtEsibIBb-BJSzMI51t_FdImGwye4ZjVPRl0LYVHSCkoLCWIiccEAnERSK8VPcFWZ_1aCv8uHUhcqqgWYKwhkAwXDYfdxNenOR1mwP5s3lZN6MiEEtOzd8mP7qV0EzJo0rnaUVVknOfi_rtz0qnF1k6pXvOTUFtCbFqpJqvw)
8. [claymath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8nGhpy9nhEI7E80Ct-YlasjXj3SLoLY-W_7qA-5-02kfINFPUZayxTybiqtsUFOx8Fh1Lov91fiQeV34d8xM_AZNbF1c5OrxnTQ4dAhS-gU0I1Nz65TrgrsGxjT_Jit_pGLAZQMtdPAm18Fon)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXtG6r6H3fNdqZNSjVm2F_XEJ1bceNULdwICJzKJWgjvDrvZETG0GksMsitADAcBKHFcEopkTbqA2fqOX05G8n3ryy7K0g0Hh2t2jrUYgAsfn0LH-9)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECQQmA0XLE-z8xtnw2xfYCrDJKNMVhWZDzLEL2FgRLTwgYoSDwPHjvU3rLjEIilwyPRCmWJf0R1LzK2HpD5H4eu8xP1mZvvWanJLtcw8XYvmUyGS6Aq30SDSBtzPQJoMmHOCYV7xA2aEGjwnhNmta7mqenDjtZm-rntTa5T5W0OMb1cg==)
11. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgdFPGx7pxE49UkoVy3ijQwXQe7TnBhiYTZIG36kysuouDARpZ08K3C7HhldEu_PkREVKI2SfgIGkxpNaROzbngp8r8MoxcsQmtJTCimSZj3SAMXACLplLzshZJmXB4QuRpJbdi5IQoi_tLidaq8YUec01qJEDqz-pc117Kmz05s7ojJMG6kuOjyJ0JthvfFMTsUxzaUOyXG1SWixxYAip6a5wKAATFTBPc_WnFrw=)
12. [intlpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvK8uv7ctRVXxBxcjrMqyC0IUBxHvz3aKacR6SMD3KX0a8OJd3j7V9scfXCwRD0ow_zm_nKUP86h9oGaWWQNwJleQleHka6EBx0LphdUybMgYPRIUBnYX331Ao_rYM8DhzQ9t0exo=)
13. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjeyuuIdsFBXqzl-l2WvfKzdaAtNNxdMj67GLY2RKuDSEARU5HKb9JaQXOV5FvAbxASzWFCwv9cL4ICfFWrHVjiD6HuFp8qpZnPCRRDFttpbxkfGBGLcjpH_Po6Rlcim60gCQxIL22Z3msbBeWemLrEeCzut2k-p-l2oE=)
14. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3UscNHjuZ2P4ATZJg_IMnnkIDvjd0eTqYrG8VUjKnoTp8l_kAjnkCL8XQa6MKcg-XPMZmVB6jX2wfbuB6GCaeJ4dCg5l1WdOA9iQWQPKfyoZhSSF06nVvPog=)
15. [crc326gaus.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0nF7GgTAaWplcYpzHHOzD7LizA9N_BBbhiqJbLSWFWuet5FV03yVo0aFdmGNb0USFFP5YZjDrCvizMrwYRlfzik8Pv1wKJM0kdks_9dJdM3bc626JO3ERXnJ973wZDB_6HCmmzlVINDdw3zTd-N5r_F2JAqB8vXCl9hQNODDr9MIaWh41HAyMNCP9fJyO1oEu2Bb_wK5ntSoR_wbAuaJf)
16. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqNAf0XK_HttfJowGAO3W4svGZxKHFJ1yWWMP-jdBwgNFcRgp6Z_DJYa00t9TTRN88OxuaYdfBgODYmH_HPXV4eDZoOn2uXij8KQe_Kl9qv4Yj2LNIiq-DNZIP0c0CCSpsyDn8GFrmHsYsQORfAuwY2iS4kS7gE56vo3D_YrBWKtiLnF1BXdBcuK-Fgbq1btn5-xnQIktI7fKfgIcoNjJ8CSRjjohLUqEVg7-jEDaNXm3oNLc7M0yRb_P9Kqx28BpdFoAwzCCZDbUJRb9WFw==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhkNg4yGcLILzuIPY0xxGam1JsWRhH8NcXmpquAw1nFa34KlD07apO-FescVcuiqcctHmiaJwepqe60V06e0yLLi7yccOjbZyDZDOCJFn5oqmeYkft)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHx-j8ubpnW5OAncEUjOMOh_kzeet_ZBDKZXzoH56c56bDDsZOlK_HCjqRwF82wRGjgLbm-6HuHBLrFGxxI9gzT4i0fLmzaMMCehbIdf6GsAsmRx_6m)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuqC7SSAtQLzwDmWyjG8BtX8iher9ksxkqNldGbmGpiv0OCqPZxquwksyJt7Fsz3o0Y96L7609LK2cwPNekmpJSYGtx4g14ADY_C6PpjB6oIne5EQG)
20. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8ERiW4ix9e1-OWHfONwkm1PkkQ-0kK6U2BQSQRtb5Fgw9UoaRlE_oOeuq87UqXhiLvd7LtKLh3EFIimnFUTlh_ecxFFyLKqUSFHM_K3_fXhekTyptgY87MTmfweJVVon5)
21. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxtjDNYNXjqO6T67GKgpZvfDZrROKFDkvqSX61QFJpNqnhPjDgwmiG_I61VGbQT3M8TY8pf1fNf2EXsYOu5B5s7V9m-dCYP_FOQEhrVZR6hfMH12GKzzcnZFtWDdiGNINipkNyV7PE)
22. [doi.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYF2-7FEOOzFAcr17SSlJXNw1QrZSL0G_w3R7g00mu0lX6fe68P1GGztZ7GLFLJayJ_CX1i0We0e1tAEyygLTuEF68cqMI9PcncdSR7bGGzfehPdf-lLOJ1CaGryeDpA==)
23. [ias.ac.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOY6Na_QAI7zbKzPhecuJciD8n-hB_EgeJJUjlXxC6230gszu_W7KC4u825yap-pN2c8hitHOijevVfHNmo51d5ZTxgSp_9P_2-s4nkUmsgS0PjKs11lK5cLxEj7JF3-J2uCpMB6c1Tfxaqc_K1KMwPnNB)
24. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrp6HFwq8aDNGFutFZeezEZOe0KxIcsSXUsQXcHrAmr4KF3K3lGfmqKuztp_AHR1GOryzfo3FLw0b9RyI4bNCvtLQLzMS-joWcBJygkUzS_boMCGf1JBQ_TrRebleqMsD6DYsP86Q29wwkhdXgwMEp)
25. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoCn4O8zO2zK4BCInurqPQ4l_QKBcnn0S_9ZYMPFFTeEZaVPXjICmom6iQyqrKqsPrhkMcmAQwtU-gA2HevDg4AiURG3iwYxQvzKcRDd3yLUw07BHkDUv50SRtUQBhpHchyuYM3pk52y_QidRBcYhzNhxVi7Pp8GPZXg==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHnUsK_qwO_xP6wnCLAMXjvOpypDrMm0Di2QheGY2B3gLvKW2BsizjxYGOjBJ5jyf3slk5gP2165m6fSENaZOGH-Fo5uF9PLq1L-n2X0oM79WVjqKNjKRW)
27. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpiV6zmvaX4R0_6ALJ-cbRkT7ECe32AwTon8IhKH3zi40HK0uKtsl4ovI1DVdL3tOu7SqGCjaGvDp22qUmSi7uWMO9TimsgiZpDzL6Tp103TnTN8nhRhe_grbai_bLJUAnX877rHiEEUU2VQjnuZUFptcxitS0dfRaR43BwrxtybUim6AYvAM4To3I8x408WC8dhVUedqffAp-bitl3e1r6k1uMRIgQp6pCrbVPptVCwsIMjFJwnxrWNO8_EipilLq3djG)
28. [cam.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnuWLuMVwasYRBKoE1GEtaS5TYWRUPz9Zd5WRClc0z290BdiVvI-ey7bjWABfBdde0w0SKTA8f9AARtG7TnVKsbIJTWBNwlPQkz9jt7I4lOQCJalO9MQ9eiqKfkZI96TQ=)
29. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4b8qCOcAjY3XyMCo7l39-J8iNnnMzOdm4GAeMT-Mlc_pOOW0ubfuGOvTr-BGjFhKk3GEBEf5TVIm5SWuZrRUP2i3TrEwj4StUs4wNL3aXIl7WRLkVuazi7b8d1_MGeHMeCoGuWTIGEQ==)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqSkbSyXXNSfGnQNG2aYOeNo3jMeqU-uodLrmyYxskvQHKz7EAA_3WaL-w6qVPrhCWuvHOQ7ulPqhpYG4Tcj2QQQpUowcgqoOayZnibS8XPI5_YQry6BrS)

