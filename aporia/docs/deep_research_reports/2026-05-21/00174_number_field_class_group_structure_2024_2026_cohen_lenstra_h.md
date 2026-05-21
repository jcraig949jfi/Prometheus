# Number field class group structure 2024-2026 (Cohen-Lenstra heuristics)

**Pythia queue id:** 174
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc4emtQYXRfSEtybS1fdU1QenVheGlBaxIXOHprUGF0X0hLcm0tX3VNUHp1YXhpQWs
**Elapsed:** 375s
**Completed at:** 2026-05-21T17:05:47.880347+00:00

---

# Number Field Class Group Structure 2024-2026: Breakthroughs in Cohen-Lenstra Heuristics

**Key Points**
*   Recent research firmly establishes the years 2024–2026 as a golden era for arithmetic statistics, characterized by the resolution of multiple long-standing conjectures derived from the Cohen-Lenstra heuristics. 
*   Evidence confirms that Alexander Smith's monumental work has definitively resolved the 2-primary Cohen-Lenstra-Gerth conjectures for imaginary quadratic fields, yielding profound implications for Goldfeld's conjecture and the congruent number problem.
*   It seems clear that geometric approaches, particularly the topological study of Hurwitz spaces by Aaron Landesman and Ishan Levy, have successfully extended the Cohen-Lenstra predictions to arbitrary primes over function fields, overcoming decades of stagnation.
*   Research highlights that the non-abelian generalizations of the heuristics (Galois groups of maximal unramified extensions) and their behavior in the presence of roots of unity have been formalized through new random group models and random matrix universality theorems.
*   The convergence of random matrix theory, homological stability, and analytic number theory has allowed mathematicians like Peter Koymans and Carlo Pagano to resolve classical questions, such as Stevenhagen's conjecture on the negative Pell equation.

**Overview**
The study of the ideal class group of a number field is one of the most venerable subjects in algebraic number theory, tracing its roots back to Gauss's theory of binary quadratic forms. Despite centuries of study, the exact behavior of class groups as the underlying number field varies remained elusive. In 1984, Henri Cohen and Hendrik Lenstra introduced a revolutionary probabilistic framework, suggesting that the $p$-primary parts of these class groups behave like random finite abelian $p$-groups weighted inversely by the size of their automorphism groups. While these heuristics were overwhelmingly supported by numerical data, rigorous proofs remained out of reach for decades. 

Between 2024 and 2026, the mathematical community witnessed a cascade of extraordinary breakthroughs. The limitations of the original conjectures—namely their failure for the prime $p=2$, their restriction to abelian extensions, and their unproven status for general function fields—have been systematically dismantled. This report synthesizes these rapid advancements, offering an exhaustive academic overview of the Cohen-Lenstra heuristics, the resolution of the 2-primary Gerth extensions, the function field analogues via Hurwitz spaces, non-abelian random group models, and the broad universality of random integer matrices.

***

## 1. Introduction to the Cohen-Lenstra Philosophy

### 1.1 The Original Formulation
Let $K$ be a number field. The class group $\text{Cl}_K$ is defined as the group of fractional ideals of the ring of integers $\mathcal{O}_K$ modulo the group of principal fractional ideals [cite: 1, 2]. By Dirichlet's theorem, this group is finite, and its order is the class number $h_K$ [cite: 1]. The class group represents the extent to which unique factorization fails in $\mathcal{O}_K$ [cite: 3]. 

In 1984, Henri Cohen and Hendrik W. Lenstra Jr. formalized a suite of predictive models regarding the statistical distribution of these class groups over families of number fields (e.g., imaginary quadratic fields $\mathbb{Q}(\sqrt{-d})$ ordered by discriminant) [cite: 1, 4]. Inspired by early machine computations, such as Duncan Buell's 1976 FORTRAN calculation of millions of class groups, Cohen and Lenstra hypothesized that for any odd prime $p$, the Sylow $p$-subgroup of the class group of a "random" imaginary quadratic field behaves like a random finite abelian $p$-group $G$ [cite: 1, 5].

The core heuristic states that the probability of the $p$-primary part $\text{Cl}_K[p^\infty]$ being isomorphic to a specific finite abelian $p$-group $G$ is proportional to the inverse order of its automorphism group [cite: 5, 6]:
$$ \mu_{\text{CL}}(G) = \frac{1}{|\text{Aut}(G)|} \prod_{k=1}^\infty (1 - p^{-k}) $$
This foundational idea launched the "Cohen-Lenstra philosophy," positing that number-theoretic objects lacking obvious structural constraints distribute themselves according to natural probabilistic measures [cite: 1]. Furthermore, they predicted that the average number of surjections from these class groups to a fixed abelian $p$-group $H$ (the $H$-moments) is equal to 1 [cite: 6, 7].

### 1.2 Random Matrix Theory and the Friedman-Washington Model
An alternative perspective, which became central to modern analytical techniques, was provided by Friedman and Washington (1989). They demonstrated that the Cohen-Lenstra distribution naturally arises as the limiting distribution of the cokernel of random matrices [cite: 1, 8]. Specifically, if one takes a Haar-random matrix $\gamma$ in the group of invertible $n \times n$ matrices over the $p$-adic integers, $\text{GL}_n(\mathbb{Z}_p)$, the distribution of the cokernel $\mathbb{Z}_p^n / (\gamma - 1)\mathbb{Z}_p^n$ converges to the Cohen-Lenstra distribution as $n \to \infty$ [cite: 1, 8]. 

This random matrix paradigm not only provided a solid algebraic foundation for the heuristics but also opened the door to proving universality theorems. It suggested that class groups could be modeled as cokernels of random square integral matrices, where structural symmetries (or lack thereof) dictate the limiting behavior of the groups [cite: 9, 10].

***

## 2. The 2-Primary Obstruction and Gerth's Heuristics

### 2.1 The Influence of Genus Theory
The original Cohen-Lenstra heuristics explicitly excluded the prime $p=2$ for quadratic fields [cite: 2, 11]. This exclusion was necessary because the 2-part of the class group of a quadratic field is heavily constrained by Gauss's genus theory [cite: 2, 12]. Genus theory dictates that the 2-torsion subgroup of the class group, $\text{Cl}_K[cite: 13]$, which is isomorphic to $\text{Cl}_K / 2\text{Cl}_K$, is entirely determined by the number of distinct prime factors ramifying in the extension $K/\mathbb{Q}$ [cite: 4, 11]. 

Because the number of ramified primes grows slowly (like $\log \log d$), the 2-rank of the class group is not a purely random variable. Consequently, the average dimension of $\text{Cl}_K[cite: 13]$ over $\mathbb{F}_2$ diverges to infinity, directly violating the Cohen-Lenstra prediction that the average size of the $p$-torsion should be finite [cite: 2, 11]. Empirical studies, such as the massive computational datasets analyzed by Wang et al. in 2024 and 2025, consistently corroborate these deviations, confirming the profound structural footprint of genus theory on the 2-part of class groups [cite: 2].

### 2.2 Gerth's Refinement
To salvage the probabilistic philosophy for $p=2$, Frank Gerth III proposed a crucial modification in 1987. Buell (1976) had already noted that if one ignores the elementary 2-group generated by the ramified primes, the remainder of the 2-Sylow subgroup appeared to behave randomly [cite: 1]. Gerth formalized this by conjecturing that the Cohen-Lenstra heuristics apply not to the entire class group $\text{Cl}_K$, but to the subgroup of squares, $2\text{Cl}_K$ (or equivalently, the square of the class group, $\text{Cl}_K^2$) [cite: 11, 14]. 

Under the Cohen-Lenstra-Gerth (CLG) heuristics, the object of study becomes the distribution of the 2-primary part of $2\text{Cl}_K$, which is hypothesized to follow the standard Cohen-Lenstra probability measure, appropriately shifted to account for the constraints of genus theory [cite: 5]. Specifically, Gerth generalized this to predict the limits of moments, such as $\lim_{X \to \infty} \mathbb{E}[|\text{Cl}_K^2 / \text{Cl}_K^4|^m]$, representing the $4$-ranks of the class groups [cite: 15, 16]. While Fouvry and Klüners (2007) successfully proved the heuristic for the 4-torsion (i.e., the $2$-rank of $2\text{Cl}_K$) [cite: 1, 17], the full $2$-primary distribution remained famously intractable for decades [cite: 18].

In recent developments, Babu, Bera, Sivaraman, and Sury (2024) extended Gerth's predictions to families of quadratic extensions over specific Galois number fields (e.g., base fields with class number 1 where the ideal $2\mathcal{O}_K$ splits) [cite: 14, 15]. Their work rigorously computed lower bounds for the average values of the 4-rank over these generalized families, confirming that Gerth's modification holds structural validity beyond base $\mathbb{Q}$ [cite: 16, 19]. 

***

## 3. The Monumental Resolution of the 2-Primary CLG Conjectures

The most celebrated breakthrough in arithmetic statistics in the 2024-2026 period is the definitive resolution of the 2-primary Cohen-Lenstra-Gerth conjectures by Alexander Smith. For his unprecedented achievements, Smith was awarded the inaugural David Goss Prize, a Clay Research Fellowship, and the prestigious 2025 SASTRA Ramanujan Prize [cite: 17, 20].

### 3.1 Alexander Smith's Breakthrough
Smith's work, culminating in his extensive 2026 publications in the *Journal of the American Mathematical Society* ("The distribution of $\ell^\infty$-Selmer groups in degree $\ell$ twist families I & II"), overcame the decades-old impasse surrounding the 2-primary part of class groups [cite: 1, 21]. Prior to Smith, the highest torsion effectively controlled was the 4-torsion; determining the 8-torsion, 16-torsion, and the exact distribution of the 2-Sylow subgroups was considered entirely out of reach [cite: 17].

Smith determined the exact distribution of the full Sylow 2-subgroups of the class groups of imaginary quadratic fields, thereby proving the Cohen-Lenstra-Gerth conjectures in their entirety for this setting [cite: 17, 20]. His methodology represented a paradigm shift, combining intricate algebraic number theory with novel techniques from combinatorics and probability [cite: 20, 22]. 

The crux of Smith's method lies in the realization that the 2-primary class groups of different quadratic twists are deeply interrelated [cite: 1]. By defining highly complex, high-order "governing fields" and utilizing a multidimensional grid of quadratic characters, Smith was able to treat the governing symbols essentially as pairings of random primes chosen independently [cite: 1, 18]. He leveraged a Markov chain model where transition probabilities between ranks are governed by the kernels of random matrices (specifically, symmetric matrices over $\mathbb{F}_2$) [cite: 1]. 

### 3.2 Implications for Selmer Groups and Goldfeld's Conjecture
Smith's machinery was not strictly limited to class groups; it was explicitly designed to control the distribution of $2^\infty$-Selmer groups in families of quadratic twists of elliptic curves [cite: 18, 21]. Let $E$ be an elliptic curve over $\mathbb{Q}$. The Birch and Swinnerton-Dyer (BSD) conjecture posits that the algebraic rank of $E(\mathbb{Q})$ equals its analytic rank (the order of vanishing of its $L$-function at $s=1$) [cite: 21]. 

Dorian Goldfeld famously conjectured in 1979 that in a family of quadratic twists of an elliptic curve, exactly 50% of the curves should have rank 0, and 50% should have rank 1, with higher ranks occurring with density zero [cite: 18, 20]. Because the actual rank is notoriously difficult to compute, mathematicians study the $m$-Selmer groups $\text{Sel}_m$, which provide upper bounds on the rank [cite: 17].

Smith successfully determined the distribution of the $2^\infty$-Selmer groups for most quadratic twist families [cite: 17]. In doing so, he showed that the Cassels-Tate pairings could be forced to be equidistributed among all reasonable possibilities, allowing absolute control over the higher Selmer ranks [cite: 12]. Conditional on the Birch and Swinnerton-Dyer conjecture, Smith's results largely settle Goldfeld's conjecture [cite: 20, 22]. 

### 3.3 The Congruent Number Problem
Smith's control over Selmer groups provided a massive advancement on one of the oldest unsolved problems in mathematics: the Congruent Number Problem, which asks which integers can be the area of a right-angled triangle with rational side lengths [cite: 18, 20]. An integer $n$ is congruent if and only if the elliptic curve $E_n: y^2 = x^3 - n^2x$ has a strictly positive rank (i.e., a rational point of infinite order) [cite: 18].

Using his framework, Smith provided the first rigorous proof that the set of congruent numbers has an asymptotically positive lower density. Specifically, he demonstrated that at least 55.9% of square-free positive integers $n \equiv 5, 6, 7 \pmod 8$ are congruent numbers, verifying the BSD conjecture for a massive proportion of these specific curves [cite: 17].

| Prize / Recognition | Recipient | Year | Citation / Significance |
| :--- | :--- | :--- | :--- |
| **SASTRA Ramanujan Prize** | Alexander Smith | 2025 | For monumental contributions to congruent number problems and exact distribution of 2-Sylow subgroups, proving Cohen-Lenstra-Gerth [cite: 17, 18]. |
| **David Goss Prize** | Alexander Smith | 2022 | Inaugural winner for establishing new methods in arithmetic statistics [cite: 20, 23]. |
| **Clay Research Fellowship** | Alexander Smith | 2021-2025 | For forging a novel research program combining combinatorics, probability, and number theory [cite: 20, 24]. |

***

## 4. Geometric Analogues: Function Fields and Hurwitz Spaces

The traditional Cohen-Lenstra heuristics order number fields by discriminant [cite: 25]. However, the heuristics can be cleanly translated into the geometric setting of function fields over finite fields, denoted $\mathbb{F}_q(t)$. In this realm, the questions transform from purely arithmetic to geometric and topological ones, bridging analytic number theory with algebraic geometry [cite: 1, 5].

### 4.1 The Function Field Translation
In the function field analog, predicting the distribution of class groups equates to predicting the distribution of the $\ell$-torsion in the Picard group, $\text{Pic}(X)(\mathbb{F}_q)[\ell]$, of a curve $X$ defined over $\mathbb{F}_q$ [cite: 1]. This relies on evaluating the 1-eigenspaces for the Frobenius endomorphism acting on the Picard group [cite: 1]. A version of the Cohen-Lenstra-Martinet heuristics for function fields was originally conjectured by Friedman and Washington in 1989 [cite: 7]. 

To prove the Cohen-Lenstra conjecture over $\mathbb{F}_q(t)$, one must demonstrate that the limiting $H$-moments (the average number of surjections to a fixed group $H$) approach exactly $1/|H|$ as the degree of the extension approaches infinity [cite: 1]. Progress in this domain relied heavily on the topology of Hurwitz spaces—moduli spaces that parameterize branched covers of the projective line $\mathbb{P}^1$ [cite: 5, 26].

### 4.2 The Landesman-Levy Theorem (2024-2025)
For decades, the average number of $p$-torsion elements in class groups over function fields had only been computed for $p=3$ (originating from Davenport-Heilbronn theory) [cite: 27]. A monumental leap occurred in 2024 and 2025 through the joint work of Aaron Landesman and Ishan Levy. 

Building on foundational topological methods developed by Ellenberg, Venkatesh, and Westerland (EVW), Landesman and Levy successfully computed the moments of the Cohen-Lenstra distribution for function fields for *arbitrary* odd primes $p$, provided the size of the finite field $q$ is sufficiently large relative to the moment being computed [cite: 27, 28, 29]. 

The key input to their proof was a highly technical computation of the **stable rational homology of Hurwitz spaces** associated with conjugacy classes in generalized dihedral groups [cite: 27, 29]. In algebraic topology, homological stability refers to the phenomenon where the homology groups of a sequence of spaces $X_n$ become independent of $n$ for $n$ large enough [cite: 28]. Ellenberg, Venkatesh, and Westerland had shown that Hurwitz spaces exhibit homological stability, and that this stability is the geometric bedrock of the Cohen-Lenstra heuristics [cite: 28]. 

However, EVW's stability results applied only to specific "non-splitting" Hurwitz spaces, restricting them from verifying the full heuristics [cite: 26]. In their 2025 preprints, Landesman and Levy generalized homological stability to apply to Hurwitz spaces associated with arbitrary racks (an algebraic structure related to conjugacy classes) [cite: 26]. By explicitly computing the stable homology of these spaces, they verified the Cohen-Lenstra moments for arbitrary $p$ over function fields [cite: 27, 30]. As noted by the mathematical community, this effectively resolves the problem from a geometric standpoint, as all but finitely many characteristic classes $q$ are covered by their stability theorems [cite: 1].

***

## 5. Stevenhagen's Conjecture and the Negative Pell Equation

The intricate behavior of the 2-part of class groups is tightly coupled with classical Diophantine equations. In 2025, Peter Koymans and Carlo Pagano published a landmark paper resolving Stevenhagen's 1993 conjecture concerning the negative Pell equation [cite: 1, 31]. 

### 5.1 The Negative Pell Equation
For a square-free integer $d > 0$, the standard Pell equation $x^2 - dy^2 = 1$ always possesses non-trivial integer solutions [cite: 31]. However, the *negative* Pell equation:
$$ x^2 - dy^2 = -1 $$
does not always have integer solutions [cite: 31]. A necessary condition for solvability over $\mathbb{Z}$ is that the equation is solvable over $\mathbb{Q}$, which by the Hasse-Minkowski theorem implies that all prime factors of $d$ must satisfy $p \equiv 1$ or $2 \pmod 4$ [cite: 31, 32].

Even when $d$ satisfies this condition (let $D^-$ denote this set of potential values), the negative Pell equation is not guaranteed to be solvable [cite: 33]. In 1993, Peter Stevenhagen conjectured that among the valid integers $d \in D^-$, the equation has a solution for exactly 58% (precisely, a specific mathematically defined density) of the values [cite: 32, 33]. 

Stevenhagen's conjecture was explicitly formulated as a test problem for the 2-primary Cohen-Lenstra-Gerth heuristics [cite: 33]. The solubility of $x^2 - dy^2 = -1$ is equivalent to the fundamental unit of the real quadratic field $\mathbb{Q}(\sqrt{d})$ having a norm of $-1$, which in turn is equivalent to the ideal class generated by $\sqrt{d}$ being trivial in the narrow class group $\text{Cl}^+(\mathbb{Q}(\sqrt{d}))$ [cite: 32].

### 5.2 The Koymans-Pagano Resolution
Koymans and Pagano recognized that proving Stevenhagen's conjecture required unprecedented control over the 2-torsion of class groups [cite: 31]. While Alexander Smith's work on the 2-primary heuristics provided the necessary framework ("a cannon to shoot at the problem," as Koymans described it), Smith's exact methods could not be directly copy-pasted due to differences in the base fields and units [cite: 33].

To bridge this gap, Koymans and Pagano introduced **new reflection principles** based on Hilbert reciprocity in multiquadratic fields [cite: 31, 32]. They generalized a classical reciprocity law due to Rédei to describe the 2-torsion of narrow class groups, utilizing a symbol similar to the spin symbol defined by Friedlander, Iwaniec, Mazur, and Rubin [cite: 31]. By constructing Markov chains of matrices over $\mathbb{F}_2$ to model the 4-ranks and 8-ranks, and coupling this with their generalized reflection principles, Koymans and Pagano computed the exact limiting density, proving that the relative density of soluble $d$'s exists and completely validating Stevenhagen's 58% prediction [cite: 17, 31].

***

## 6. Generalizations: Non-Abelian Extensions and Global Fields

The original Cohen-Lenstra-Martinet (CLM) heuristics primarily considered class groups (which are abelian) of abelian extensions [cite: 1, 11]. However, modern algebraic number theory demands an understanding of non-abelian generalizations, specifically the Galois groups of maximal unramified extensions of a global field $K$, denoted $G_{\emptyset}(K)$ [cite: 6, 34]. By class field theory, the abelianization of $G_{\emptyset}(K)$ is isomorphic to the class group $\text{Cl}_K$ [cite: 6].

### 6.1 The Non-Abelian Random Group Model
Boston, Bush, and Hajir previously attempted non-abelian generalizations for quadratic extensions [cite: 6]. However, in a major 2024 paper in *Inventiones Mathematicae*, Yuan Liu, Melanie Matchett Wood, and David Zureick-Brown successfully formulated a rigorous, predictive model for the distribution of $G_{\emptyset}(K)$ as $K$ varies over arbitrary $\Gamma$-extensions of $\mathbb{Q}$ [cite: 1, 4]. 

Their breakthrough was constructing a **random group model**. They de-abelianized the Friedman-Washington random matrix model (which generated abelian groups via cokernels) into a system of random generators and relations for profinite groups [cite: 1]. The Liu-Wood-Zureick-Brown heuristic posits that the unramified Galois groups admit a balanced presentation and are distributed according to this random group model [cite: 35]. This implies surprising structural phenomena regarding the pro-$C$ completions of $\text{Gal}(K^{unr}/K)$ that were completely unknown prior to 2024 [cite: 36].

### 6.2 Further Generalizations by Willyard and Liu
In 2025 and 2026, researchers like Ken Willyard further extended these non-abelian heuristics. Willyard (2026) demonstrated that these canonical quotients have specific presentations for $\Gamma$-extensions where the base field $Q$ is not just $\mathbb{Q}$, but an *arbitrary* global field (including function fields) [cite: 6, 7]. This introduced additional complexities, such as avoiding primes dividing the class number of the base field, and ensuring the avoidance of characteristic primes in the function field case [cite: 6]. Similarly, Peter Koymans and Carlo Pagano (2025) proved that these unramified Galois groups always admit a balanced presentation when finitely generated, offering robust theoretical support for the Liu-Wood-Zureick-Brown random group model [cite: 35, 36].

***

## 7. Roots of Unity, Bad Primes, and Composite Torsion

### 7.1 The Presence of Roots of Unity
One of the most notoriously difficult aspects of the Cohen-Lenstra-Martinet heuristics was their failure when the base number field contains $p$-th roots of unity. As observed by Achter and Malle, the original heuristics give incorrect predictions for the Sylow $p$-subgroups of class groups in these scenarios due to additional algebraic symmetries and reflection principles (such as Kummer theory) [cite: 1, 9]. 

In a pivotal 2026 paper in *Mathematische Annalen*, Will Sawin and Melanie Matchett Wood established a modified, highly convincing version of the CLM heuristics over arbitrary number fields that explicitly accounts for roots of unity [cite: 1, 9]. They provided the precise probabilistic corrections required to model the distributions, heavily backing their claims with function field analogies [cite: 1].

### 7.2 The Problem of Bad Primes ($p \mid |\Gamma|$)
When analyzing a family of $\Gamma$-extensions of a base field, primes $p$ that divide the order of the Galois group $|\Gamma|$ are deemed "bad primes." For these primes, the standard CLM moments often diverge to infinity, behaving qualitatively differently than predicted [cite: 11, 25]. 

In late 2024, Yuan Liu published results investigating the distribution of the $p$-part of the class group for these bad primes [cite: 11]. Utilizing a discrete valuation ring lattice approach over $\mathbb{Q}_p[\Gamma]$, Liu proved that a specific quotient of the class group is too large to have finite moments, while an ideal-scaled subgroup remains equidistributed according to a Cohen-Lenstra-type measure [cite: 11]. Crucially, Liu developed a **weighted-moment technique** specifically designed to extract finite data when the traditional moments (obtained via Hurwitz space point-counting in the function field case) are infinite [cite: 11]. 

### 7.3 Composite Torsion
Gerth's original conjectures primarily focused on prime $p=2$. However, newer frameworks address *composite torsion* $n = \prod p_i^{r_i}$ [cite: 5]. A generalized heuristic suggests that the average size of the $n$-torsion parts of class groups factors neatly as the product of the averages for the individual $p_i^{r_i}$-parts, implying a profound conjectural independence between distinct prime parts [cite: 5]. In December 2025, Koymans and collaborators confirmed this factorization rigorously for $n=6$ (the product of 2-torsion and 3-torsion), representing the first major proof of composite torsion distribution rules [cite: 5].

***

## 8. Random Matrix Theory: Universality and the Surjection Moment Method

The mathematical engine driving many of these breakthroughs is Random Matrix Theory (RMT). The insight that class groups can be modeled as the cokernels of random integral matrices transformed arithmetic statistics into a branch of probability theory [cite: 5, 10]. 

### 8.1 Wood's Surjection Moment Method
Melanie Matchett Wood fundamentally advanced the field by inventing the **surjection moment method** [cite: 10]. This technique determines the limiting distribution of a random finite group by analyzing the expected number of surjections from that random group to every possible fixed finite abelian group $H$ [cite: 10, 37]. If these moments match the moments of the Cohen-Lenstra distribution, the random group converges to the CL distribution [cite: 10].

Wood proved that for a broad family of random integral matrices with independent entries (satisfying mild $\epsilon$-balanced anti-concentration conditions), the cokernels inherently satisfy the Cohen-Lenstra distribution [cite: 9, 10]. This **universality** means the exact distribution of the matrix entries does not matter; the macroscopic class group structure emerges naturally from randomness [cite: 10].

### 8.2 Matrices with Symmetries: Symmetric and Alternating
Class groups often possess pairings or dualities requiring symmetric or alternating matrices [cite: 8, 10]. For instance, Rédei matrices (used to study 4-torsion) are symmetric [cite: 8]. Furthermore, the sandpile groups (critical groups) of random undirected graphs are defined as the torsion part of the cokernel of the graph's Laplacian matrix [cite: 38]. Laplacian matrices are necessarily symmetric, meaning sandpile groups carry a canonical perfect symmetric pairing [cite: 10].

Wood, along with collaborators like Clancy, Kaplan, Leake, and Payne, conjectured and partially proved that sandpile groups follow a modified Cohen-Lenstra heuristic, where the probability of a group appearing is inversely proportional to $|G| \cdot |\text{Aut}(G)|$ (accounting for the pairing-preserving automorphisms) [cite: 38, 39, 40]. 

In a January 2026 preprint, Jiahe Shen achieved a major milestone by providing a new proof of **quantitative universality** for the cokernels of random matrices with symmetries [cite: 10]. Shen reproved the symmetric universality theorem of Hodges and the alternating universality theorem of Nguyen and Wood [cite: 10]. Crucially, Shen's approach bypassed the classical surjection moment method to yield *exponentially small error bounds* (and stretched-exponential bounds for $p=2$), explicitly answering Wood's open questions about the exact rate of convergence of these random matrix cokernels to the Cohen-Lenstra distributions [cite: 10].

### 8.3 Symplectic and Orthogonal Distributions in Combinatorics
The universality of Cohen-Lenstra distributions has also unexpectedly permeated combinatorics. In October 2025, Jason Fulman and Dennis Stanton demonstrated that Anzanello's conjectures regarding the proportion of derangements in affine classical groups over finite fields are intimately related to **symplectic and orthogonal Cohen-Lenstra-type distributions** on integer partitions [cite: 41]. The symplectic distribution applies to integer partitions where all odd parts occur with even multiplicity, while the orthogonal distribution applies to partitions where all even parts occur with even multiplicity [cite: 41]. This reveals that the CL philosophy governs structural randomness far beyond class groups and matrices, extending deep into the symmetric group and representation theory.

***

## 9. Conclusion

The timeline spanning 2024 to 2026 has unequivocally redefined the landscape of arithmetic statistics. Henri Cohen and Hendrik Lenstra's 1984 realization—that the unfathomable complexity of class groups could be tamed by viewing them as random variables weighted by automorphisms—has evolved from a numerical curiosity into a sprawling, rigorously verified mathematical doctrine. 

Alexander Smith's brilliant taming of the 2-primary obstruction resolved the longest-standing flaw in the original heuristics, triggering a domino effect that advanced Goldfeld's conjecture and the Congruent Number Problem. Concurrently, Aaron Landesman and Ishan Levy leveraged homological stability of Hurwitz spaces to conquer the function field analogues, proving that geometry and topology are indispensable tools for number theory. Peter Koymans and Carlo Pagano utilized these statistical frameworks to settle Stevenhagen's conjecture on the negative Pell equation. Furthermore, Melanie Matchett Wood, Yuan Liu, and Will Sawin expanded the horizon to encompass non-abelian unramified extensions, roots of unity, and robust random matrix universality.

Today, the "Cohen-Lenstra philosophy" stands not just as a set of heuristic predictions, but as a proven fundamental law of mathematical nature: in the absence of explicit algebraic constraints, arithmetic structures will reliably and universally embrace the elegance of randomness.

**Sources:**
1. [bourbaki.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdRr4nAjvXwSAJdcloReNipgAx1jVSAvmX0I69af1nFw-slXtXPDaN65nnbuxvWkWz3pDvl2DUXdSM82zPlxX7vlRNSG5bs1IIbInACFt_fec6ixysAKQ92o09B1c-XMXurtFs_GitpRTp)
2. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFzQnUd2p0bveFS3rMs0UCEZRY-UfOrbo55W2gCBE95l-zeSsmEAuZ5032XlW-gw8dtSE1IOYPW_CGeWPNU6BW75EE00iMSvtwWi6v9YhfbQs4OQQyYrxV566IhQ==)
3. [universiteitleiden.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYT78DJ8UqrETvPKdNS9EifMuGogA_hgc8NP998OyVQZSqhl2o08aLVKq3Xfh9rYlryf2FhXR9fqd785OhbYuwZg9XzykozPWqWTy_0DX72YEE9hucC-SbeJA0foWhCcsJNtZ8NSemNzxglprhXn10Md1n5BTMPAug2r3U7l7VMhsCvM2E0lnLQiS1XmTjT73ioPw03PE=)
4. [nieuwarchief.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvNMqjii8OfCa0GOroonPFqmH1Xe2QN8Dg-kFkGsgt6trM_XVSdjC3LFrVUskWdlAJ8bazmQmETH2HGwQMBXEieeDqK3hFYzBEVURNTVUmfKhhu7IqIux9uhinRTBIpLzFuoFPvxtX9dzCTOpeA1zOkRgT)
5. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcdTvkKGYMvTZdPBGIezRdWBk8iFYZnKGrw3vz-EP1nOt-KoqdSgcdKJvh8FEqCjQhdvHrDOaDpMfbP1YFhVeV_ESb92Uxk0I5n9T0heqsRp5v3qzHyPwpCOUhXBIUHOMDwsLAQGgx0u30Yy56LGZGeWtNIURJ0Vc=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEH9OwwAA8eUQTDkWzhPrvldhbvgD5eY0B5Iw-35NYn_WMwDMcLke6f9JeL7sanOzXia-vAWhrc9NFRSDEac83Q2V6qpKQvsG1BPgloLwi-2nx9Fxccg69RLA==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGg3BU6ts3IQFzIWXYIdzqPOvXRx53YDMKH_p1u5d-VNSTduxWL8Qm2d-eLIkKdjwyZPBVN8VFjcF1gZspsuiXCbCsvj2VBiAjz8zmDJVO8oG6_Xt8SEw==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQFNuTlKxyVsmx9JGaOdTYr9ybusFT1uLaPPjWtfCU290lptHkHHwmxGUOp8aUsMAsNv-2fMQgMUyRcIU2mK3rgH711EWM3y0zmjbnCaDEFUoGsoVzng==)
9. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPVtK3Ex9vW0URh43luS52a09t6-yQtdtj3hqQBEELy4fqTCR_Gh6OY4oSFw-Un4C1bKTvRv--fJbfPq_VeyakNEh3S_8noDjXM48R9VKtVluJw56cLVfSQllvjMhp82paCVAGXDHIOp-ViA==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxFDwJRBIbve-4_t6mIqeFMG1bQjOUJkNHGTk0lVztlzOA6wVMShAi9Ae1udoA9p04Crg2dLfx3sgKmFwiwR8kWMPKRb3QNcJUUFu1-a5iybG-hQJ8Yw==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzevB_HgFdGQ9aqDDLm7nPAINYyCBiVE0y_M5TX3RFU-SEUXoKu7GVzCQK1EbZvS9OfYIp1jNtyRY3TduMUWFwGlSwoR1xzn0JIkg3Yby5jH841hoEyg==)
12. [osu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJlRTFQsY_eIWWmoKNN9UO1MHNfuGEPJxvJTM8xkWRzIgwZDuYpXTdhdApIn6afinWjiPp7n83UWaI-fCwKdyAxMxdjDQdATRKH6HdIxluGLYv6cb0Of-HLsUWl-SUhxabdY07HO2v_PXJ2MWwWA1KpfqIYP2oe6I=)
13. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECOGIJhyAESHAWf_WsgqtMACNHV3M81LNgldFuRC1C3ui5RhO3MDwXnXW2Apio0qz4JxG24eK5axooPT1NIzZEkFsL1tFysk9T6ZUd1XTvmTuGWdTytZY_PjMUqk--pgacys0_wSgDKikODTxZIv3Ko3QuETwD2-qvP-pvO1ZBcJhvs_fR9XbWCcx1n32ykfFfxWA1GyxBJM-NamAFykG8kL5x4ErohZLS1kk=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEePOm7KVqtq0rqU61I60TGgxIGpQ6JFRclVWwRu8ncEhWe6sXOLyMsr_gvxgxaQ8GLzkj2y6jx_2skG3oMUmUTv0ElB1b0qY6OrqaQia0ccWm4O7hY1tvMlQ==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKJmSeRD0qA4NdP2IiPRd-re4UKt5tixKLZl2It3DbRrqUiucF2YqMmaB4Bs3CltAO2aFiYr6MS-7tRx5NcFkDPnbJpE2kRxHF7c_wIs5iqcBo1_QvCA==)
16. [isibang.ac.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-EJKK2wsC-1ZvGIIMvEFgpWoFEqAbq7acHQa8bRpHOKWVQGvp6kEWvnSRvOjZfHdGqgC5sKEJhwVEFPC-I3cwXCW3BHMST4eeogQX7haMHtrEi-HoIYHWDeRQWUKY2JtPcvpAjGI=)
17. [qseries.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEd89DbOP8sa9rAejqOwRB8TeIV4xsgmd3j___Ds0F4T6j4MQ4uBUeBbxK8FKJ8s-roF0p5veUpKgtyoGZU9sSi09AxVLyhS26z730vpfq_Xup0ksW1ZLNK8JjIg_p5SQ==)
18. [jupiterscience.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyeyO4d7-vCC79LnxOitU2xHPUPWRBghZtQORP0LkXGEPaUurRoPQu3A1c91kyrn-qHxVUtPy1l_eQUbzads4Vzv8yhBh48-C8bNpEhx_l6JnnUjRkWe7GPHFv-TCfzafGAaOvqN2HgFA-q9Sd7eRVdlEy_xD3gldWA6Tfl3t_E3euflDNSJm9CCrlBg==)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsq_Ri5H63dfalRpFepBSJsXDN45_SaMxlY_JTGasjHAqBqAcqI4W0U-K5OlMET6TVEY7QWMvGEimGFjEFkofAeLtQPUNmV8jWWE0O3XaJd-VGZ_usHD5QN85_xz4SLc0ViApxBXT0CtShVPFpOtuAfNa0oay17D7zUyxXyqkaHBAikiST)
20. [claymath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH97JZm0bpBCjb_unO-lsyVj78q0QzEpIcOJyIb6-k4sC6annGBxmQFXzyn1zphsLR-PiUzj_3tu4H3oRA7h8YkKrcUrtcrPTOZiJKj7pMILEnJZ_sXkD7o2khncWihX1jQDDXJn9U=)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0IKtk0CV4DYcwwJQ3HHCjxe2Le2XNw_qcHnC4kL9Fb9TWx8TBFzwfayPsInM4XuqWPgyJIZR1-weg1gYVjSrnBkzi4O2ZW--ahEtWqZK-pmhCqLbzIQ==)
22. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMbmZSTGeOQhVefYvwx4buErEfRU1pCZbaAd8fsGcNfkQbtyeFXPz2Foi9prO5b_bDuATjmoS8QIfhzWruuPwM1w_rwIRnsdlRK607GEzHfsWzA2_nDitEbO_NOe0UAH544KMJ2snSZywIU30ur3sMx0tLxNX_GwmGmYavPFgAI0lg8e4=)
23. [numbertheory.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcn7qAroue8avEg9XO8ljFHBYQwf-1hhzhxvd13qsrWs2XNF6edpmrbsUsdBfmXgauHeiW3GfnPaNBKGiUalTwnLCeRwPuow1BGQa7Jn7k5EU-Xn7lIC9nLTTcm1nm)
24. [qq.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7MH4KQM0A3iboA0U8XkRjILhbzNaPxQMW58E8_oYCH0C3TwdGYFR-5BcZMMlQn6QDGRKQOYMwWwCnJZrlA2yngVQK5cSOBHWzoOG5JFT8vodelBa6eWrXRzceUOZYS4RpwQ==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiltMETe-E2K7Q3OG8yyD9oZ252rWcl9FJIhT5fwZh88kjUvWA4NjFIHgT8GWptYcoL1R5sM_tjXCw6Li7haYXVkNRKzME3omTTrZMpKTeM-hqMPwfNQ==)
26. [rochester.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEI7-sWy1oSzEHpjN0xvgoatxDfyOKzr6R4fbzYJJXol6VGlkRWbQdRM8B8HE8ISmuEDK6JZ_873QZyPqJb4qnEQzVuBt6MGnFfxAtdIam_THgzrk52oHdiOO9mrl2NbFgI3I1zulCr6k_TNA35vZZYIFYiYFXXvsD8Zmbu34w=)
27. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmG3vOPq8surY3un0zIj-LmKGLw-KxZNF3_trDxDlU6voR2TxCQ64uCENHsRFzKyVCAKlu6WY16SjCEeqX4dmdrPchBfwkjW38qluKBuNDKwd95Uzl5ZLKnGyKTPAQl7V6d6twM8xCb0gemQCy-nn2zcT4ite6-iF28ae-D474IEeEJnlaQzlsZTFHQla0jHHJszb1tJtkkw==)
28. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcGFcwo8zZuKAYp38qj4RoTZr57AqNK7riHv_b6acI7rJZnLXG8bmM6MzD6Xcl8udQVLpZOvtAB1o_v96Xp-6CtLNaqdadH6CTMQyoHdh1SRQRP5fIQLsQqm2pQ40_7cp3)
29. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEbv2iDDBWt5__dFJ694aa3zy9QDRAHVNYF7dopO3yNCU3wCGp3seB61Oetrt5ZP4RX0bGYGXrbHBrQd8rTGN_VuXlQiAeS1O9djt5CdVn7tnwfckK9ZGaUnmVdG2hNJxqt_ZvGlwNCa8w4vac)
30. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJwOwtK7kquqVV8yw0MI5zRcfWS-zBsa7Ajb515kasO1vM7LlPvITy8ZS_qYFZixq-umzseGhwxdKG12mClQUaHt8nqpgFSH2Nf2gfA60MsaSqaJLcYXTh6EQr5-xdESC0f31AdVcnCteO)
31. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUzCMeNldO9SwpHhTPT_J4QZ9LH7S4nehcdVqUKjo6pABiFVndHBjUh-PE7cb_42gikTEJgCJ4iZygfTMR2IbuHYb6uQav_puxHDKsrv6r6u1Lk2dgXBVcyjVDHhP-GiBxGwLpOuAGhQtasdCRFFf0tv5T_ifZeA==)
32. [uu.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFThhZGVvE-BmkXr4jZ8syqjg8baQW4eZNTza126tB963eDL0vi58YjkMf0SSS8uwo2aEKlefmlcFdEaFV4OtDfbEdE-5nk6fIw_0Oz6xpfs8sPl_uJPHdFIhVWNYoTTwjUGK3aTSsr8m8BibCQ)
33. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzzmWUt5Lx1OsaAzslnUU7R0TbfpCEU3lWO8XWEXMwHTPzO035n6LE_EatyGycuL0CfloR0kqrtb5PzHlovgA8-SrvfMkJ0pGmXtR3kJolXEtpCGYha-lUYS066bUTTfsVkyPTz_RWo5TTeSrb8k-6VJFipnL7hbbRtEGEneOHwhiS0p9hOGl_7S8wQAwG__Q=)
34. [nd.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtOEfju-cMpYdBTAKx-_m2NELrY_Jdf1Qmen1t_jYDebZsF9zPTeu42b7AFPfMtg3PrSarBdMporTX9hfjn5UiUxXBwiJ63zIUS3qK86dRnf7KiZZNElUgNjlhRi8RNzcNZJn3PTEUcfvkcRUf8Ev-ygBC2F9XctBOfQDaIVd1sYaxM06U15dm)
35. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEkKl59YN2yVhPapN2uaq_ADxAnCILxr0OPYMTQt8riPXApboSLqBIV18UBF3zi_daVnh8QPf7Ptp6utHmkOWTe3notLORj61NGsYvFC97A23-jp6ne9FTxBmf_hF4VbBugXbJDnNX1g==)
36. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFooschHN8gLBogbqQbAm5NVUVNF8Fpzi9_ezqFUdA5NvD0ppMPbjSCnvHIxZizAQAaLeuhxTyup8lWO-k50caG53pj5yuWewT7hZJ0yABirzmo7jn3ppzHftBxu2EVYkvOVG5Z)
37. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnvczDxhMza_nv1jUOFIVyvpIVNPgw0ZAGVPS4HTHKCF_ZG6ijpmIBkZmcVg-SOQaiRY0krOFeSK1Ktz4Ogk1RyaWh0bjGwaN6N47IGqx0jYacUpJeXLAIjWa1owxDzharrTKCZLGbhONcB8j84Fk6iSmWi96Ph4dCGdIQqKcoDvIZA5odpYqa69UW2ixUcsjwuqcUtA1h0N9SaddT)
38. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbw27GQSxcHXMBl0MwjXp8gI3SGt0AoNHOURVPcX_3WisuMdyG4s-3OEKaypdk6UWBHdlaUVy2yaLf3vCto9sfbJ-6o3R5pglL1AG-W_Dlu8p6rpm0Cw==)
39. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEboxb5TtFwuaKM2rTOU0VjKTVdTYWsprKLW9-Ki28wLnp0cAsmcOlT1k_ktznYDoBteht3cPkuKoy1_rm8Umd0OQ-bqSOd8Haj3MP9jRCk3nAQaTtyJl1wO5vw-TQWBA9pgTtj9Z9l6OniGhrMG7BsUEboT2L7BvctTUuvGdkPQGnXZ3YkN_bV4zceeEzwoQJfbK7zCjhtCMdGT52M6H_iMrK0sTWhiLFdbg==)
40. [dokumen.pub](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXjrPTLpgzjMwGveT_mZIaIO9iny8LQKrEJlTrVoiHNbpxfhbc9PdBDaUxydVCV2odbDafE0-9CMUG5_YeLv5V3TzKgtbXtuniGSsEYFIJc3w5Lo4iJ0c-hROxBwvCSG1c2s3D2GDUzNwCFuQgDUtNn6eesw9Il0L2-Xv4BICVJIc39RrBYlikxkduQajgRBdo00Fvla5pju-AngZXkrhmH6wBk10T9j3ScVyhp3UP70_pdGMyi1xLEBxjoI6m2xI1ObIngpi0eBF7XNKJbJYsNwa6mt4UiwzZ7y0IVuucgXSpDAo=)
41. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFq1t-Q3V_fpbRMkQk8CeZMgKQIGc4x4fWfSrXlAmYi2YjK3sGbOthFp2QcRqSEg6TlKkQPNsF5mFRoxSezmLewurcntopvCCejKWjeaQsFcEaw5n-9lQ==)

