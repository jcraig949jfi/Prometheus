# Genus-2 paramodular L-functions (Brumer-Kramer conjecture status 2024-2026)

**Pythia queue id:** 147
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdiekFQYXFPOEQ5S1cxTWtQbnZYVDRRNBIXYnpBUGFxTzhEOUtXMU1rUG52WFQ0UTQ
**Elapsed:** 311s
**Completed at:** 2026-05-21T16:24:06.851817+00:00

---

# Genus-2 Paramodular L-functions and the Status of the Brumer-Kramer Conjecture (2024–2026)

**Key Points:**
*   **The Brumer-Kramer Conjecture:** A two-dimensional analogue of the Taniyama-Shimura-Weil modularity theorem, asserting that the Hasse-Weil L-function of every typical abelian surface over $\mathbb{Q}$ (with $End(A) = \mathbb{Z}$) exactly matches the spinor L-function of a weight 2 Siegel paramodular newform.
*   **Historic 2025 Breakthrough:** In February 2025, George Boxer, Frank Calegari, Toby Gee, and Vincent Pilloni (BCGP) published a monumental proof establishing the modularity of a *positive proportion* of abelian surfaces over $\mathbb{Q}$, marking the most significant advancement in the field since Wiles' proof of Fermat's Last Theorem [cite: 1, 2].
*   **Methodological Innovations:** The 2025 BCGP proof overcomes decades of obstacles by employing a "2-3 switch" (analogous to Wiles' 3-5 switch) and adapting Lue Pan’s recent theorems on the classicality of ordinary $p$-adic modular forms to the higher-dimensional Siegel setting [cite: 3, 4].
*   **Computational Verification (2024-2026):** Extensive algorithmic searches by Poor, Yuen, Shurman, Assaf, and Voight have exhaustively verified the conjecture for prime levels $N < 600$, confirming the existence of nonlift paramodular forms (such as at the minimal conductor $N=277$) and utilizing tools like Borcherds products and algebraic orthogonal modular forms [cite: 5, 6, 7].
*   **Motivic and Cohomological Progress:** Concurrent research by Horawa and Prasanna in 2025–2026 provides deep insights into the coherent cohomology of Siegel varieties, linking Beilinson's conjecture to the adjoint L-values of paramodular forms [cite: 8, 9].

**Summary for the General Reader:**
In mathematics, the Langlands program is a grand unifying framework that predicts deep connections between geometry (shapes and curves) and analysis (periodic functions called automorphic forms). The most famous example of this was the proof that all elliptic curves (donut-shaped curves) are "modular," a result that solved Fermat's Last Theorem in the 1990s. The Brumer-Kramer conjecture—also known as the paramodular conjecture—asks whether this same connection holds for higher-dimensional shapes known as *abelian surfaces*. Specifically, it predicts that the arithmetic properties of any typical abelian surface over the rational numbers can be perfectly described by a highly complex, multidimensional function known as a Genus-2 paramodular form. 

For decades, proving this for even a single typical abelian surface was considered almost impossible due to immense technical barriers. However, between 2024 and 2026, the mathematical landscape was upended. A team of four mathematicians (Boxer, Calegari, Gee, and Pilloni) released a breakthrough 230-page proof showing that a large, mathematically positive proportion of these surfaces are indeed modular. To do this, they used "clock arithmetic" (switching between clocks of 2 and 3) and advanced $p$-adic geometry to bridge the gap between the geometric shapes and the analytic functions. While the conjecture is not yet 100% solved for all surfaces, this result, combined with massive supercomputer verifications of the lowest-complexity surfaces, brings mathematics to the precipice of fully resolving the Brumer-Kramer conjecture.

---

## 1. Introduction: The Langlands Program and the Genesis of the Paramodular Conjecture

The Langlands program postulates profound and far-reaching correspondences between algebraic geometry, Galois theory, and the analytic theory of automorphic representations [cite: 10]. In its most celebrated realization over the rational numbers $\mathbb{Q}$, the Modularity Theorem (formerly the Taniyama-Shimura-Weil conjecture), established by Wiles, Taylor, Breuil, Conrad, and Diamond, dictates that the isogeny class of every elliptic curve $E/\mathbb{Q}$ of conductor $N$ is associated with a unique normalized weight 2 cuspidal Hecke eigenform $f \in S_2(\Gamma_0(N))$ such that their respective L-functions coincide: $L(E, s) = L(f, s)$ [cite: 10, 11]. 

As the theory of one-dimensional abelian varieties (elliptic curves) matured, number theorists naturally turned their attention to dimension two: **abelian surfaces**. An abelian surface $A$ over $\mathbb{Q}$ is a projective, connected algebraic group of dimension two. Just as elliptic curves have a Hasse-Weil L-function $L(A, s)$ encoding the number of points the surface has over finite fields, the Langlands philosophy insists that this geometric L-function must correspond to an automorphic L-function [cite: 12]. 

However, the automorphic objects corresponding to abelian surfaces are significantly more complex. They reside in the realm of **Siegel modular forms of degree 2** (or genus 2), which are holomorphic functions on the Siegel upper half-space $\mathcal{H}_2$ that transform under the action of discrete subgroups of the symplectic group $\text{Sp}_4(\mathbb{Q})$ [cite: 13, 14].

### 1.1 The Classification of Abelian Surfaces
To understand the modularity of abelian surfaces, one must classify them according to their endomorphism algebra $\text{End}(A) \otimes \mathbb{Q}$. Over $\overline{\mathbb{Q}}$, abelian surfaces fall into several categories [cite: 10, 12]:
1.  **Products of Elliptic Curves:** $A \sim E_1 \times E_2$. Here, modularity trivially follows from the modularity of $E_1$ and $E_2$.
2.  **Surfaces of GL(2)-type:** These surfaces possess real multiplication by a real quadratic field. Their modularity was established by the pioneering work of Ribet, Khare, and Wintenberger, showing they correspond to classical Hilbert modular forms [cite: 1, 10].
3.  **Potentially GL(2)-type:** These are Weil restrictions of elliptic curves defined over quadratic fields, whose modularity derives from the modularity of elliptic curves over those fields (e.g., through the work of Freitas-Le Hung-Siksek for real quadratic fields and Caraiani-Newton for imaginary quadratic fields) [cite: 12, 15].
4.  **Typical Abelian Surfaces:** These are the most general abelian surfaces, possessing trivial endomorphism rings: $\text{End}_{\overline{\mathbb{Q}}}(A) = \mathbb{Z}$ [cite: 10, 12]. 

The Brumer-Kramer Paramodular Conjecture specifically addresses this fourth category, the "typical" abelian surfaces, which previously defied all known methods of establishing modularity [cite: 1, 10].

### 1.2 The Formulation of the Paramodular Conjecture
First proposed informally in the late 1990s and formalized precisely in 2014 by Armand Brumer and Kenneth Kramer [cite: 16, 17], the Paramodular Conjecture provides a tight, testable, two-dimensional analogue to the Modularity Theorem. 

**The Brumer-Kramer Paramodular Conjecture:** 
Let $N$ be an integer. There is a one-to-one correspondence between:
*   Isogeny classes of typical abelian surfaces $A/\mathbb{Q}$ (meaning $\text{End}_{\mathbb{Q}}(A) = \mathbb{Z}$) of conductor $N$.
*   Lines of weight 2, cuspidal Siegel paramodular newforms $f \in S_2(K(N))$ with rational Hecke eigenvalues that are *nonlifts* (i.e., they do not arise as Gritsenko lifts from Jacobi forms).
This correspondence is realized by the equality of their L-functions: 
$L(A, s, \text{Hasse-Weil}) = L(f, s, \text{spin})$ [cite: 14, 18].

A critical caveat to the converse direction (automorphic to geometric) was later added based on observations by Frank Calegari: for certain conductors $N$, a weight 2 nonlift paramodular form might correspond not to an abelian surface, but to an abelian fourfold whose endomorphism ring is an order in a non-split quaternion algebra [cite: 14, 19]. 

---

## 2. The Automorphic Landscape: Siegel Paramodular Forms

To evaluate the status of the conjecture in the 2024-2026 epoch, one must delineate the specific automorphic forms involved. 

### 2.1 The Siegel Upper Half-Space and the Symplectic Group
The Siegel upper half-space of degree 2 is defined as $\mathcal{H}_2 = \{ Z \in M_{2 \times 2}(\mathbb{C}) \mid Z = Z^T, \text{Im}(Z) > 0 \}$ [cite: 14, 20]. The symplectic group $\text{Sp}_4(\mathbb{R})$ acts on $\mathcal{H}_2$ via generalized fractional linear transformations: for a matrix $\gamma = \begin{pmatrix} A & B \\ C & D \end{pmatrix} \in \text{Sp}_4(\mathbb{R})$ and $Z \in \mathcal{H}_2$, the action is $\gamma \cdot Z = (AZ + B)(CZ + D)^{-1}$ [cite: 20].

A Siegel modular form of degree 2 and weight $k$ for a discrete subgroup $\Gamma \subset \text{Sp}_4(\mathbb{Q})$ is a holomorphic function $f: \mathcal{H}_2 \to \mathbb{C}$ satisfying the transformation property $f(\gamma \cdot Z) = \det(CZ + D)^k f(Z)$ for all $\gamma \in \Gamma$ [cite: 20].

### 2.2 The Paramodular Group $K(N)$
In the classical theory of elliptic curves, the appropriate discrete subgroup for a curve of conductor $N$ is $\Gamma_0(N)$. In dimension two, the correct analogue for an abelian surface of conductor $N$ is the **paramodular group of level $N$**, denoted $K(N)$ [cite: 18]. 

The group $K(N)$ is defined as the subgroup of $\text{Sp}_4(\mathbb{Q})$ consisting of matrices whose entries satisfy specific divisibility conditions related to the polarization of the abelian surface [cite: 20]. Specifically, $K(N)$ is the stabilizer in $\text{Sp}_4(\mathbb{Q})$ of the lattice $\mathbb{Z} \oplus \mathbb{Z} \oplus \mathbb{Z} \oplus N\mathbb{Z}$, naturally corresponding to the moduli space of abelian surfaces with a polarization of type $(1, N)$ [cite: 20].

### 2.3 The Gritsenko Lift and "Nonlifts"
A significant complication in dimension two is the presence of endoscopic forms, specifically the **Gritsenko lift** (an additive lifting generalizing the Maass lift) [cite: 20, 21]. The Gritsenko lift maps Jacobi cusp forms of weight $k$ and index $N$ into the space of Siegel paramodular forms of weight $k$ and level $N$, denoted $S_k(K(N))$ [cite: 20].

The L-function of a Gritsenko lift factors into a product of the Riemann zeta function (shifted) and the L-function of an elliptic modular form. Therefore, a Gritsenko lift cannot correspond to a typical abelian surface with $End(A) = \mathbb{Z}$ [cite: 10, 22]. The Brumer-Kramer conjecture explicitly isolates the **nonlifts**—the orthogonal complement to the space of Gritsenko lifts—as the true automorphic partners of typical abelian surfaces [cite: 5, 16].

---

## 3. Computational Evidence and Constructive Verifications (Status 2024–2026)

While theoretical proofs of the paramodular conjecture lagged for decades, immense computational efforts generated the empirical foundation that guided modern theory. Between 2015 and 2026, researchers including Cris Poor, David S. Yuen, Jerry Shurman, Eran Assaf, and John Voight developed highly sophisticated algorithms to verify the conjecture for small conductors.

### 3.1 Exhaustive Search at Prime Levels $N < 600$
A major computational triumph was completed and finalized in the 2024-2025 period: the construction and classification of all weight 2 paramodular cusp forms for prime levels $N < 600$ [cite: 5, 23]. Using Borcherds products, theta blocks, and the geometry of paramodular varieties, Poor, Yuen, and Shurman proved that for prime levels $N < 600$, the space of paramodular nonlifts perfectly matches the list of conductors for which typical abelian surfaces exist [cite: 5, 24].

Specifically, for primes $p < 600$, the space $S_2(K(p))$ consists entirely of Gritsenko lifts *except* at $p \in \{277, 349, 353, 389, 461, 523, 587\}$ [cite: 20, 23]. In these exact levels, nonlift paramodular newforms exist, which aligns flawlessly with Brumer's independent calculations of the conductors of rational abelian surfaces [cite: 20, 23]. 

#### The Minimal Conductor: $N=277$
The absolute smallest prime conductor of an abelian surface over $\mathbb{Q}$ is $N=277$ [cite: 16]. The unique isogeny class at this level (LMFDB label 277.a) is represented by the Jacobian of the hyperelliptic curve:
$y^2 + y = x^5 + 5x^4 + 8x^3 + 6x^2 + 2x$ [cite: 23].

Through advanced computational methods, Poor and Yuen identified a dimension 11 space $S_2(K(277))$, whereas the dimension of the Jacobi cusp forms $J_{2, 277}^{\text{cusp}}$ is only 10. Thus, there is exactly one Hecke eigenform $f_{277} \in S_2(K(277))$ that is not a Gritsenko lift [cite: 23]. They computed the Hecke eigenvalues for $f_{277}$ and successfully matched the spinor p-Euler factors with the Hasse-Weil p-Euler factors of the abelian surface for the primes $p=2, 3,$ and $5$ [cite: 23]. In recent years, utilizing p-adic congruences and Galois deformations, the full modularity of this specific surface was rigorously proven, capping off the $N=277$ case [cite: 19].

### 3.2 Squarefree Levels and Algebraic Modular Forms
Progress has also been made for squarefree levels. Computations for $N < 300$ verified the conjecture for squarefree conductors, identifying nonlift newforms exactly at $N=249$ and $N=295$ and matching their Euler factors to the corresponding abelian surfaces [cite: 21, 24].

By 2024-2026, researchers like Eran Assaf, Watson Ladd, Gonzalo Tornaría, and John Voight expanded the computational toolkit by utilizing **quinary orthogonal modular forms** [cite: 6]. Because the symplectic group $\text{Sp}_4$ has an exceptional isogeny to the orthogonal group $\text{SO}(3,2)$, paramodular forms can be computed via definite orthogonal algebraic modular forms [cite: 6, 25]. This algebraic approach circumvents the heavy analytic machinery of Fourier-Jacobi expansions, enabling the mass generation of databases of paramodular forms and strongly corroborating the Brumer-Kramer conjecture across thousands of examples [cite: 6, 22].

### 3.3 Borcherds Products and Theta Blocks
A vital technique refined up to 2024 for generating paramodular forms is the use of **Borcherds products**. While the Gritsenko lift is additive, the Borcherds product is a multiplicative lift from weakly holomorphic Jacobi forms to Siegel modular forms [cite: 5, 7]. Algorithms developed by Poor, Shurman, and Yuen can systematically construct all Borcherds product paramodular cusp forms of a specified weight and level by examining the integral closure of graded rings of modular forms and utilizing "theta blocks" [cite: 7, 24]. 

Notably, in cases where Borcherds products only yield Gritsenko lifts (e.g., at $p=461$), mathematicians know that the paramodular conjecture's predicted nonlift must be found through alternate analytic or cohomological means [cite: 7].

---

## 4. The Automorphic to Geometric Bridge: Galois Representations

To prove the Brumer-Kramer conjecture, one must bridge the automorphic side (Siegel forms) and the geometric side (abelian surfaces) using **Galois representations** as the intermediary [cite: 10, 12].

For an abelian surface $A/\mathbb{Q}$, its $p$-adic Tate module $T_p(A)$ yields a continuous Galois representation:
$\rho_{A, p}: \text{Gal}(\overline{\mathbb{Q}}/\mathbb{Q}) \to \text{GSp}_4(\mathbb{Z}_p)$ [cite: 3, 26].
This representation has Hodge-Tate weights $(0, 0, 1, 1)$ [cite: 12, 15].

Conversely, for a weight $k$ Siegel modular eigenform $f$, modern Langlands machinery (spearheaded by Weissauer, Taylor, and others) attaches a $p$-adic Galois representation $\rho_{f, p}: \text{Gal}(\overline{\mathbb{Q}}/\mathbb{Q}) \to \text{GSp}_4(\mathbb{Q}_p)$ [cite: 12]. The Hodge-Tate weights of this automorphic Galois representation are $(0, k-2, k-1, 2k-3)$ [cite: 12, 15]. 

For the geometric and automorphic representations to match, their Hodge-Tate weights must align. This forces $k=2$, yielding weights $(0, 0, 1, 1)$, perfectly matching the abelian surface [cite: 12, 15]. This deep Hodge-theoretic compatibility is why the Brumer-Kramer conjecture explicitly dictates weight 2 paramodular forms [cite: 12].

---

## 5. 2018–2021 Milestone: Potential Modularity over Totally Real Fields

Before achieving modularity over $\mathbb{Q}$, a foundational milestone was reached by the quartet of George Boxer, Frank Calegari, Toby Gee, and Vincent Pilloni (BCGP). In a massive paper originally preprinted in 2018 and finalized in 2021 in *Publications Mathématiques de l'IHÉS* ("Abelian Surfaces over totally real fields are Potentially Modular"), they proved that every abelian surface over a totally real field $F$ is **potentially modular** [cite: 27, 28].

"Potentially modular" means that while the abelian surface $A$ might not correspond to a Siegel modular form over its base field $F$, there exists a finite Galois extension $F'/F$ such that the base-changed surface $A_{F'}$ is modular [cite: 27, 29].

### 5.1 Consequences of Potential Modularity
The potential modularity theorem had immediate and profound consequences for the **Hasse-Weil Conjecture** [cite: 27, 29]. The Hasse-Weil zeta function of an abelian surface $\zeta_A(s)$ is an Euler product over all primes. Prior to BCGP, it was unknown whether $\zeta_A(s)$ could be analytically continued past its region of absolute convergence [cite: 12, 26]. 

By proving potential modularity, BCGP demonstrated that $\zeta_A(s)$ admits a meromorphic continuation to the entire complex plane and satisfies its expected functional equation (relating $s$ to $3-s$) [cite: 12, 27]. This effectively solved the analytic continuation portion of the Hasse-Weil conjecture for genus 2 curves and abelian surfaces over totally real fields [cite: 12, 29].

### 5.2 The Faltings-Serre Method
To prove this, BCGP relied on the Faltings-Serre method, utilizing Taylor's Ihara avoidance technique [cite: 15, 26]. The strategy involved matching the mod $p$ Galois representations of the abelian surface to those of a known modular form, and then using $p$-adic deformation rings and Hecke algebras to "lift" this residual modularity to characteristic zero [cite: 26]. However, a severe technical obstacle remained: the Taylor-Wiles method for modularity lifting classically requires the automorphic forms to contribute to cohomology in only a single degree (a "defect zero" situation) [cite: 26]. Weight 2 Siegel modular forms, however, contribute to coherent cohomology in multiple degrees, resulting in a positive defect $l_0 > 0$ [cite: 26]. Overcoming this required extensive innovations in higher Hida theory and $p$-adic modular forms [cite: 26, 30].

---

## 6. The 2024–2025 Breakthrough: Modularity of a Positive Proportion of Abelian Surfaces over $\mathbb{Q}$

While potential modularity was a historic achievement, the "holy grail"—full modularity over the rational numbers $\mathbb{Q}$ (the Brumer-Kramer conjecture)—remained heavily out of reach [cite: 31]. Traditional methods could only verify the modularity of isolated, computationally accessible examples (like $N=277$) [cite: 19]. 

However, the mathematical community was stunned in February 2025 when Boxer, Calegari, Gee, and Pilloni uploaded a 230-page preprint titled *"Modularity theorems for abelian surfaces"* (arXiv:2502.20645) [cite: 2, 3]. This paper achieved what was considered nearly impossible a decade prior: it proved the full modularity of a **strictly positive proportion** of all abelian surfaces over $\mathbb{Q}$ [cite: 3].

### 6.1 Statement of the 2025 Modularity Theorem
The main theorem of the 2025 BCGP paper asserts that an abelian surface $A/\mathbb{Q}$ with a polarization of degree prime to 3 is modular if it satisfies three primary conditions [cite: 3]:

1.  **Big Image Hypothesis (Residual Surjectivity):** The mod 3 Galois representation $\rho_{A, 3} : \text{Gal}(\overline{\mathbb{Q}}/\mathbb{Q}) \to \text{GSp}_4(\mathbb{F}_3)$ is surjective [cite: 3].
2.  **Technical Condition at $p=2$:** $\rho_{A, 3}|_{G_{\mathbb{Q}_2}}$ is unramified, and the characteristic polynomial of $\rho_{A, 3}(\text{Frob}_2)$ is not $(x^2 \pm x + 2)^2$ [cite: 3, 12].
3.  **Ordinary and 3-Distinguished:** The abelian surface $A$ has good *ordinary* reduction at $p=3$, and the characteristic polynomial of the Frobenius endomorphism at 3 does not have repeated roots (the "3-distinguished" condition) [cite: 3, 12].

If these conditions are met, there exists a cuspidal automorphic representation $\pi$ of $\text{GSp}_4(\mathbb{A}_{\mathbb{Q}})$ (corresponding to a weight 2 Siegel paramodular form) such that $L(s, H^1(A)) = L(s, \pi)$ [cite: 3]. Consequently, $L(A, s)$ has a perfectly *holomorphic* continuation to the entire complex plane (removing the "meromorphic" uncertainty of the 2018 result) and satisfies the expected functional equation [cite: 3].

By imposing these relatively mild conditions (which amount to congruence conditions at finitely many primes), BCGP ensured that their theorem applies not just to isolated examples, but to a statistically positive proportion of all abelian surfaces over $\mathbb{Q}$ when ordered by conductor or height [cite: 3].

### 6.2 The Core Mechanism: The 2-3 Switch
A critical component of the 2025 proof is a technique known as the **2-3 switch** [cite: 3]. This is a highly sophisticated, higher-dimensional generalization of the "3-5 switch" famously employed by Andrew Wiles in his proof of Fermat's Last Theorem [cite: 12, 32].

Wiles needed to prove the modularity of the mod 3 Galois representation of an elliptic curve. When the mod 3 representation was too degenerate to apply his modularity lifting theorems, he found another elliptic curve that shared the same mod 5 representation but had a "good" mod 3 representation, proving modularity at $p=5$, transferring it to the new curve, and switching back [cite: 12]. He utilized the rational geometry of the modular curve $X(5)$ to find this auxiliary object.

For abelian surfaces, Boxer, Calegari, Gee, and Pilloni utilized a rational moduli space of abelian surfaces to execute a 2-3 switch [cite: 12]. The process unfolds roughly as follows:
1.  Start with an abelian surface $A$ satisfying the theorem's hypotheses [cite: 12].
2.  Find an auxiliary genus two curve $X/\mathbb{Q}$ with Jacobian $B$ such that $\rho_{B, 3} \cong \rho_{A, 3}$ [cite: 12].
3.  Ensure that $B$ has good ordinary or semistable ordinary reduction at 2, allowing the researchers to prove that the mod 2 representation $\rho_{B, 2}$ is modular [cite: 12].
4.  Lift the modularity of $\rho_{B, 2}$ to the full characteristic zero representation, establishing that $B$ is modular.
5.  Since $B$ is modular, its mod 3 representation $\rho_{B, 3}$ is modular.
6.  Because $\rho_{A, 3} \cong \rho_{B, 3}$, the mod 3 representation of $A$ is modular.
7.  Finally, apply modularity lifting at $p=3$ to deduce the full modularity of $A$ [cite: 12].

### 6.3 Overcoming the "Clock Arithmetic" Barrier
A popular science article in *Quanta Magazine* (June 2025) beautifully summarized the struggle behind the 2-3 switch [cite: 4]. The team needed to match Galois representations (which act like numbers on a clock face, i.e., modular arithmetic). They found a trove of modular forms whose representations were easy to calculate using a clock of 2 (mod 2). However, their abelian surfaces required a clock of 3 (mod 3). Bridging these two distinct mathematical "clocks" required immense geometric maneuverability, culminating in an intensive 12-hour-a-day summit in Bonn, Germany, in the summer of 2023, where the team finally cracked the switch mechanism [cite: 4].

---

## 7. The Role of $p$-adic Geometry and Lue Pan’s Classicality Theorem

Even with the 2-3 switch, the Taylor-Wiles method strictly requires that the $p$-adic limit of the modular forms behaves "classically"—meaning it genuinely corresponds to the standard Siegel modular forms predicted by the Brumer-Kramer conjecture [cite: 3]. 

As previously noted, weight 2 Siegel modular forms suffer from a cohomology "defect," occurring in irregular weights and multiple cohomological degrees. To bypass this, the BCGP team relied on **higher Coleman theory** and **$p$-adic Eichler-Shimura theory** [cite: 3, 30]. They utilized overconvergent $p$-adic modular forms, which are $p$-adic analytic objects defined on rigid analytic spaces that extend classical modular forms beyond their usual convergence domains [cite: 3, 29].

However, not all $p$-adic modular forms are classical. To guarantee classicality, BCGP required a novel theoretical bridge. This bridge was provided by the recent work of Lue Pan (Princeton University) [cite: 4, 33].

### 7.1 Lue Pan's Breakthrough on Modular Curves
In 2020-2022, Lue Pan published groundbreaking results regarding locally analytic vectors in the completed cohomology of classical modular curves [cite: 33, 34]. Pan’s work translated the complex-analytic Hodge theory (specifically, the theory of linear differential operators or $D$-modules that govern Hodge decompositions via the Laplacian operator) into the $p$-adic realm using Galois cohomology and Sen theory [cite: 3, 33]. 

### 7.2 Adaptation to Siegel Threefolds
The BCGP team realized that Pan's techniques, originally designed for 1-dimensional modular curves ($GL_2$), could be adapted to the higher-dimensional setting of Siegel threefolds ($\text{GSp}_4$) [cite: 4, 34]. 

In their 2025 paper, they formulated a **new classicality theorem** for ordinary $p$-adic Siegel modular forms [cite: 3]. They proved that under mild technical hypotheses, if a $p$-adic Siegel modular form has an associated Galois representation that is both *ordinary* and *de Rham* (a deep $p$-adic Hodge theory condition equivalent to being Hodge-Tate for ordinary representations), then the $p$-adic form is automatically a classical Siegel modular form [cite: 3, 30].

This Pan-style classicality theorem was the final missing pillar. It allowed the BCGP team to use powerful $p$-adic deformation rings to prove modularity, safe in the knowledge that their $p$-adic limits would resolve into the exact classical weight 2 Siegel paramodular forms predicted by the Brumer-Kramer conjecture [cite: 3].

---

## 8. Coherent Cohomology, Motives, and Beilinson’s Conjecture (2024–2026)

While BCGP attacked the paramodular conjecture via Galois representations and p-adic geometry, another profound line of inquiry progressed simultaneously in 2024-2026, spearheaded by Aleksander Horawa, Kartik Prasanna, and others [cite: 9, 35]. This research explores the Brumer-Kramer conjecture through the lens of **coherent cohomology** and **motivic action** [cite: 8, 9].

### 8.1 Automorphic Sheaves and Motivic Cohomology
Classical modular forms for $GL_2$ contribute to the singular (Betti) cohomology of modular curves. However, weight 2 Siegel modular forms on $\text{GSp}_4$ are not cohomological in the standard sense; they do not contribute to the singular cohomology of the locally symmetric space because the space is Hermitian symmetric [cite: 9]. Instead, they contribute to the **coherent cohomology** of automorphic sheaves [cite: 8, 9].

Horawa and Prasanna proposed a sweeping conjecture (inspired by earlier work by Prasanna and Venkatesh on singular cohomology) that explains the contributions of a Hecke eigensystem to coherent cohomology in terms of the action of a **motivic cohomology group** [cite: 8, 9]. 

### 8.2 The Adjoint L-function and Beilinson's Conjecture
Specifically, in the context of the Brumer-Kramer conjecture, if $A$ is a rational abelian surface of conductor $N$ corresponding to a paramodular form $f$ of weight $(2,2)$ and level $N$, Horawa and Prasanna examine the motive $M(\pi_f, \text{Ad})$, which equals the symmetric square $Sym^2 H^1(A)(1)$ [cite: 8, 9]. This motive can be realized in the cohomology of the product surface $A \times A$ [cite: 8].

In an extensive 2025 paper ("Coherent Cohomology of Automorphic Sheaves"), Horawa and Prasanna proved that their conjecture regarding the motivic action on these coherent cohomology classes is mathematically equivalent to **Beilinson's Conjecture** for the adjoint L-function of the paramodular form $f$ [cite: 8, 9]. Beilinson's conjecture predicts that a specific subspace of the Chow group $CH^2(A \times A, 1)$ has rank one, and that the leading Taylor coefficient of the adjoint L-function at a critical point is rational modulo a specific motivic regulator period [cite: 8]. 

By connecting the Whittaker periods $c_W(f)$ of the paramodular form to Deligne periods using non-vanishing theorems of twisted spin L-functions (proven by Radziwiłł and Yang), Horawa and Prasanna provided a structural, motivic explanation for *why* the Brumer-Kramer conjecture's L-function equality $L(A,s) = L(f, s, \text{spin})$ governs the deep arithmetic geometry of the abelian surface [cite: 9].

---

## 9. Synthesis and Open Problems (Beyond 2026)

The period of 2024–2026 has unequivocally been the "golden era" for the Brumer-Kramer paramodular conjecture. The situation has rapidly evolved from sparse computational evidence to a massive foundational theorem proving modularity for a positive proportion of all surfaces.

### 9.1 Summary of the Current Status
1.  **Computational Certainty:** For prime conductors $N < 600$, the conjecture is exhaustively verified. Every predicted nonlift paramodular form has been found, and its Euler factors match the corresponding typical abelian surface [cite: 5, 23].
2.  **Theoretical Modularity:** The Boxer-Calegari-Gee-Pilloni theorem (2025) guarantees that if an abelian surface is ordinary at 3, 3-distinguished, and possesses a large mod 3 Galois image, it is definitively modular [cite: 3]. 
3.  **Analytic Continuation:** Because of the BCGP results, the Hasse-Weil zeta functions for these surfaces are now known to be unconditionally holomorphic over the entire complex plane [cite: 3, 27].

### 9.2 The Path Forward
Despite this staggering progress, the Brumer-Kramer conjecture is not yet 100% resolved. Several hurdles remain for researchers in 2026 and beyond:

*   **Removing the "Ordinary at 3" Restriction:** The current 2025 theorem requires the surface to have ordinary reduction at $p=3$ to apply the Pan-style classicality theorem [cite: 3]. Extending the classicality theorem to the supersingular/non-ordinary locus remains a major open problem in $p$-adic Hodge theory [cite: 34].
*   **The "Big Image" Hypothesis:** Abelian surfaces with highly degenerate or small mod 3 Galois images (that are nonetheless not of $GL_2$-type) currently fall outside the BCGP theorem [cite: 3, 11]. Handling these will require either new "switches" (e.g., using primes larger than 3) or entirely new modularity lifting theorems.
*   **The Converse Theorem (Automorphic to Geometric):** While the community has made leaps in proving that an abelian surface yields a paramodular form, the reverse—constructing an abelian surface directly from a given weight 2 nonlift paramodular form—remains profoundly difficult [cite: 36]. Unlike elliptic curves, where the Eichler-Shimura construction uses the Jacobians of modular curves to literally build the elliptic curve from the modular form, there is no direct geometric analogue of Eichler-Shimura for paramodular forms that guarantees the construction of the abelian surface [cite: 36].

### Conclusion
The years 2024 to 2026 will be recorded as the epoch when the modularity of abelian surfaces transitioned from a speculative mathematical dream to a proven geometric reality. Through the synthesis of computational algorithms tracking Borcherds products up to $N=600$ and the staggering theoretical frameworks combining $p$-adic higher Coleman theory with clock-arithmetic switches, the Brumer-Kramer Paramodular Conjecture stands today on the precipice of total vindication. The Langlands program's assertion that the universe of algebraic geometry is intimately mirrored by the universe of automorphic forms has secured one of its greatest victories in dimension two.

**Sources:**
1. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGt7igFxTSpyTVKmQT6pAom2vBWRmtYyKlsRr0dLz9ER-I5yPA9jmtQ7iaSCRU9zHu7P_mBUiuLfc208qogdFGnUtjveGPx33ZGB_aNMrvSeSWhci8oErBJxTYXs65zC9Gu7R23-5sDEJ-qjCdKa-eWcznBpEA8FPc9BugCcptiHzfiNNdrpul9pVJAamteqQ==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVsDyjH231o7nT-jRetLMB6uTJVwejcZQq_Es_1KQ4HfKw-KP774GJs9YFcfnQEXug9cYIs8UJvRNENk8AgobsK_f31tPOuTUdLHaTY5CWCJ1vcKNQBQ==)
3. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQ333tyADefvQftUj_1TBoIWPoBqohbHhamMuzqrt5VUlHSuubV5zZ6EIPFE-411q6uZtZGkbd27NHB925vYwam3-owOI5MucboyXLnGGRy4Rpp-R-hGW8RmB3fjEIjPDqb8ZgjoKWldBF9SA=)
4. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjGpuBr4pgVN57DsIzif6wTmnPEGCyU8UiC4kQOdlRS54zeLimV5LzkL18ojf_JK-EZbQ8edXzc1LNZUbs_m7kD8HFbDY7igI0NxuIPvNu1jrviav8eH0XP-EVNaAOBwl2SrW7FRfgL2PTp4S3tESimA3NtBiwjgVoz6WYCxUUl-LHv4rUBLLhvCvZvjj5OGjpNz8o2Q==)
5. [kms.or.kr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_35vQIWJSCiYFKyxNWpOZgyRwZ9IMO3w1w-Hwi1FVN7g79slFqAA1lHFtayTQfnrcppQnki2NlBN1L5V9eGX4r2mUrG5J3U0LQ1s7MDFs-JAVsY2p-Ankvx35b5XEUzxzN3xYslq-HmnwHv7UrCx4RVFZVcIwGGMQJ30=)
6. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDyl7K0z4eBXI9tEUBxBPwF9asD-E_3DkRQLZZo8eb9IB6nHZPYJtaPqTyqhB1Xli-lzgcAZG6bxMZBw_bSpFlg2SDyYm-t8B9GmUfvCF80e4SnkaO)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6f2mOROElsRPMa8dH8HwaiRroLDwcpZvhwLZgVy63kpBjJ64xJmFsoOFFtj2j5B8cNTRGrPDwr0371BeClnBTUSX9u9lo6V3AgVNkrY21XN9P9oKplA==)
8. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGR5tv1CqFJBBGgmpuBTxby1ypamZIpiLR8HB69etR6tQXDrLPUOpe9REVDc3AJcOI6QEAo8UPCNOMB9ooKA1EADlDMwj3Eq2bo-8xDhG8EWHhpzcr2hCcwYHTyuZFDOIp3KMcSVQ==)
9. [uni-bonn.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHd5gKz6KfypeAtBa1g6LKJIy6eC055vt59S6HIcoOluY4IULUe9HXCo27huY1j86EiAXHZR0JiDUDTXuSDT-L6q5Iu3DqhOe918oOYPQk6OD-pYpjj7YmMWghZUNYdgoqDXIJ2RaTsfSXc)
10. [tu-darmstadt.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEC1J3Rvv3Nbuyx6Y0IYh9DRsp3dXA-ZI7x5rqCjbua-Ghhi18TE6VeLq3WY2ORC4opf14pSZ32wLKGCYuGRpHT20D3qfph3DyHGmII-o1NyaB6hu7JFoPyV0rgpAHICK_CmQlguLHue-9_5N2nt1_LfJhUTRMpm4qKBMM=)
11. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHe_i5B8u1qe_ee_a2JVCPYyKeQj-EL5MXzOiUw2nzamChvFGe0cTTvo_ohhSiVnPKY8gqRiv1BLe3g69Rxmf577C70WLRiztmwa9yi8uZI-OrBockCLvLFUorgtVXwwolG)
12. [imperial.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSxT_KfhtYyjETZ_ipgn8FzBWNtM0Uaaxku3vDx6AbIm2S9DRGwtAqsHoxwfIo0ez8WL7NcWwb_TK7X2kpJlkyXFcRjNmvwpr0vrv-xWHlwEDWkCPDbkmzgn8EskJ8e2veNBcyF-AC--NajbovnaiM)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0uLKJQfZw6TjH0dySuBBq8uZ3o6nEWS9XaYFIbID2FlFSXGMY3G4g11ql9By9WaF89_xbNdQySoL63ep35md13tKh5tysVpTQnSl5oTyEWUU4PtLAScwDwA==)
14. [kyoto-u.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHapm4pkUkzJIhgEj-vnELyLLpuRjPQWZSvPfMvw-HTP2ncvXkYh6dK0IlHZrukTQ_T8xvg7tXK6FO2njmyazmnFP9-hMOdCQ8ViCfvcpU07E2W68LyAT3oj3xEycZmZQpDNKQEhRYUidhQ7KlY7HXOhfwHgtHfPD1rAfdQT7sh3w==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGg4fmRpljhZKN_X9eePWUm4VIfJ2vWfjNuA-O6qzOnuxJCsva1eZTk_DfsYywqNT-u362syOSNa_9xN05ldhprrfdeAZu940-2nLkPw57ERCAcpT1r_hda8A==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGy8Vtfq_L9gmZYQgc0nayTLOC-QwgrGh00iyknA8DDQ0ehHOCiaoSbKMIFGIG8RsBi6vX0AcmeXRLQ5Oh77jXm6_Jjx92S4k7r2repNfYbfkhZsdU2)
17. [osu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7JIi5cgbty6QVO_RtunH1ki23tRm64KyeJ085gPis03Zu0OBnccFXmSVVrNILveTjDQNJI3YmGSbd9-XPJHfpIDtLRdFRPwxIL90CdEJ37VH6VujLI2mGW31qE--J7jtd)
18. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvC8IlRbk6cs_jKX_qciUF3uLq5utZGRa10-IHTz5OqfV73hojPmjVOzTDLTDW7Z_lJedrYtwwJuP6Gf5yNACptQVL8dRkUz5EOft39E7OKpKsjVeWz4NqJ-y6cpLUYewZT21hxg9eK6xI9vkwnw0Qh6RHRhAuzzpN6ZBLhpPBw-dksxddiF9KaONdq2ZzSW6pKzsDOT9rMNx9nk5MGsayfdzkUIw_CZ4qL0BHGblSDu6L)
19. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEeuMZMbgcPxaqQJA9XAKVwp1JgSI_H1FrGCEqQN_vgh7xawZwIcP5A8emPkdbVzait6qameZ5VUYnB3KEuIgiEJTJ9cyaPX769HuOYLch7XPTQL5m4558DcNIaPY2h-WP0A9dF1asrkIc9oiYmXZf__Ssv_RJe8Lqx)
20. [siegelmodularforms.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfYWAmsdf2eOUtIM7CRIriu_sM38Ci5UKk0bgsElzt2QWsDw3225nto1Rk8OMDEQAxJAFbiNKu0fMo3ZGtTG_F2Lqj609944_7O2vPWl0iKor_UmTI8Pak8fFwtK1AlpmSgEMBCeRDtNV8c2VS0NS72utOFWjKs8lDMTVVQ0eqsQICWBY=)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMHmD6DNqXSecsu_NaJ39AfrmW8Mr-hX4zTE55A709S_zbsO7tRyfPyIAMzZk_1OG3frgemUIYt5CBWBmggevR7E7U3mKG_tkKV_tuZK1ASzHHZSSvPzng03MAMtEjpRgbX1Zn0xd00gtkKvOWDCakRpnAqPYVLpHn34EsOOC8SXTAZMV4axwhbAqsPKmP5V3_IwXnLlgoNl1LpK-WCZ3r1nmVDoTjk-8KtwWd-oQrZP8ANomGichEOyc9LnYBvaEkDoRKOvz7cUYV5z2WRqGBbXm4y2zvusVwFVq6YPDPYYrFQu5FUaAGPcxixDX9rCplfFV7fcJAQDB7xY78aq2nwydHtwnTVO-3Q_M523w63kLELFo=)
22. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPWeULJiyGsjN-3VUM9g-AP3aTPtQvBKqJzx5eh6vwSUQVwr0CU59zf6hkpmPChqJNLMWEMbYo4TtDDiykJQGs1Uqa6QytcZ_WMsoM5iUIUgf_zz4LDzYc5LUNPCEkjS9F0Rg5kcQ=)
23. [asu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEP-wLDhZwP7B-UC8ugFG6kT2pGjFatvVoVTlXBWvYBItPlr5lQeTp_dv0ThqZXSwOr3_iMscsJRlM5SdqY91RCWBm45zxwGmFN6vLNvARO3L44olnc75wtgAsUiicILw==)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEu13uAaLt0g7drxuVtKvs2YHsmoXYqkflV6-xS2PccGELf1SkqSTn9qSVaNznZ4t2EeGg0648aHUuWumCGMflJJNCmrADboW5UTMTSvinJGvOyZTOPGZDpo3DFt13HE0g0bZR1MvzHU3RvvnbWyXR40hmn5Je_LSybAWyl0MZdbkXBKv4=)
25. [whiterose.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECifhvJXnPnFOCubNrPF5IzgqLl_WKjUzovqemy3Xg94xU4Y6VKgZpK5V4Aj5-690KAfTm26gEfuE9e8esNIEBSFswTBpGAk6LXxlW9mpaIeIMvoX1g0LybB9ROXtOR5LGr3otkNwM0LVympFeg02hc73iCz8XeiVdinJk7ZLMU4tm5RHJcrFslw==)
26. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMDV8rzfDvhdOx52dlVenkCBVAytXjJRTE8YslOvA8Oxk-zYBoXsjczvDbiiV7d7aLFLxYkhTHF323T1LY9I-zMUjr7E_glQVljPkisXtf1_jBmANbhvmW2X6UahzsFX41YJgZ6TatLRk=)
27. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYWd0Qp4gtgvjvZaVDEQWH0TE6gfAcXGe94gh1UD-XrTlJp5YMNinyexhmCyk-FRXt6M5BBDpRJd0W2PF0xTh_Ka25vlOx6J1ecJ_QXBBeAqJmyl1PuwHEf4xoCmiGFyeoFKFBIeIyqsNWCSmc5Wev)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETxuLe316qi2BJuflbWhs5uusie4CBb0KHMwbD90FAuvjZPnZyCs2vOEDnXll_ypX2_AuXuUpivu0AJWeCwymXcW3XmsYae7tHaEcSIcjngT7P4qMWOg==)
29. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-zlp7pZZFIwudPA373EX996QFvTzMcM2hlrAi_bwXV0M0wTCx_US_9MehCCLUSL4SqNxXX6XOWQJzh6y5GvwwD9lDzsyqUaVJQgP6lWfaxg_gj3aMU7yy9c2RoaR4Wsnu)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLYXUNmVN7aWPzShE44yx3LQd9XX-GMqmWPwCUo5JxYmGh6l2y1LRiPlPbw5h4y-7rtOE4J3Phf0oDKQBjxXpzkIwetTKAT159Y9cA6yE9x1B-T2iyt_HJL7go36MrM2-fUOYB-lCGrUGR7eUykgvhNWo0_nqW2r8NDPG9AzEu4jPmk1kCevq5UfECrB7PZNTL)
31. [warwick.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOUPPgJCgtrG7ctLVdJBXxw8xVhbyx8WVk5AHOy9l5UVzg_8CvHYU3zE06EDL_btf8OixyyjnNXmTrsL6VilAIEfjpziFLqEpu6ayeON4mnBplBtrge2Lx4Cb1esuM0UWUuv3WriPteCcd2XuajWIjHJaSm8YImv8uTfTkhc0=)
32. [cam.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGd3mOGWGxwneN2imWH5ifwglcjYM84TLAh2xwuVnLKEGaHq5StX1Tw6KbaWEfrXAYnNdTf2P4ve-h6OpOGcBC17j0tyyehtc-q_3oNDJWR4T6eN90cxhu8pCzpe0LwFoI=)
33. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECH0vw92DM8YCNHYQGzFkeyggtTCOUjXDHQUR-SWfejY8WYTqK03RMm_3cuL8MMn8nO7x4xI8zFia41LCqZ6FqQfZHd9-iCAJV6QEp8kwH0MQ6b9nL666Hd2apVgtba0IX5t4ECSu7LPO8RMoG7SdVpIA=)
34. [imperial.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWNh4ziifBRYdbTjJpifTK3VnhNsNF6YK6x3zlprVkadWrujhRsup-hztEgyNopZDgTA2HbrdZ8Xg5ELLRmbL3S8-5Nodhb7DdAIEceSVVq0BI4U_tLdtcm3u4Dle4qBzHPlh_Ujakwd8ioR6v_P1Wz0lgfvVrJrTL)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKyfae4z31t_2aIY6RR4ERfJL5_78qMCEE9gYX-Oj3WQFe_lHIDTjpRZ0uhnaoPcvxxOLuZfQVjG5_PqvAXpSkqAqLBaZOgVRgHKQh0thdvHi7Gy0eow==)
36. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLhf1AIIOJqfc3G5eaKKsTwOFmMryu6UUqOGNiKdLYeFUHQYQleBOPNH5ZeZiz-q7pDyV0sNiyXP7HKoH1IEdTVS07nSUEmWn6ji3Jyp-HWXn3lRnKykaRSmyNTFM-NtsumKkvpsAQO3JanWQM1quucA==)

