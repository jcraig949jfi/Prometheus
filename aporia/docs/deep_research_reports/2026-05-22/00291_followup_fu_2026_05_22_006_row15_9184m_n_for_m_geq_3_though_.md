# Followup [FU-2026-05-22-006 <- row15]: 9184m)^n$ for $m \geq 3$, though tighter bounds remain open for specific composites like $\mathbb{Z}

**Pythia queue id:** 291
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChZQYTRQYXMyeUtNbmh1Z2ZhemU3QkR3EhZQYTRQYXMyeUtNbmh1Z2ZhemU3QkR3
**Elapsed:** 250s
**Completed at:** 2026-05-22T01:19:53.108530+00:00

---

# Deep Research Substrate Brief: Progression-Free Sets over Composite Moduli ($\mathbb{Z}_{15}^n$) and Slice-Rank Optimality

**Executive Summary**
*   **Core Inquiry:** The report investigates the open question of whether the asymptotic maximal size of progression-free sets over the composite modulus $\mathbb{Z}_{15}^n$, denoted as $\alpha_{3,15}$, is strictly less than the trivial composite bounds derived from its prime factors (i.e., $\min(3\alpha_{3,5}, 5\alpha_{3,3})$).
*   **Current Consensus:** The slice-rank polynomial method guarantees a general upper bound of $r_3(\mathbb{Z}_m^n) \leq (0.9184m)^n$ for any integer $m \geq 3$ [cite: 1]. However, the current consensus acknowledges that this bound is likely loose for composite numbers that are not pure prime powers, such as 15 [cite: 1].
*   **Methodological Limitations:** The current theoretical optimality of the slice-rank method is heavily constrained by structural limits when applied to rings with mixed characteristic subgroups. It is theorized that new tensor rank definitions or geometric invariant approaches will be required to break the current bounds [cite: 2, 3, 4].
*   **Future Trajectory:** Breakthroughs in this domain will likely pivot away from pure slice-rank constructions and move toward higher-order structural analysis, such as analytic rank or G-stable rank, which better capture the multiplicative interactions of composite moduli [cite: 3, 4, 5].

**Introduction for the Layperson**
In mathematics, specifically in the field of additive combinatorics, researchers study how large a set of numbers (or vectors) can be without containing certain patterns. One of the most famous patterns to avoid is a "3-term arithmetic progression"—three points spaced equally apart in a line (like 2, 4, 6). When we look at these sets in environments where math wraps around like a clock (modular arithmetic), the problem becomes incredibly complex, especially in higher dimensions. 

For prime numbers (like 3 or 5), mathematicians recently developed a revolutionary technique called the "slice-rank method" to prove that these pattern-free sets must be extremely small—exponentially smaller than previously thought. However, when the "clock" is a composite number made of different primes (like 15, which is 3 times 5), the method hits a wall. Researchers currently just mash the answers for 3 and 5 together to get an estimate for 15. The open question we are exploring is whether we can prove that sets in a "base-15" clock system are actually much smaller than these mashed-together estimates predict.

**The Complexity of Composite Moduli**
When dealing with a prime number modulus, the mathematical space acts perfectly symmetrically, allowing advanced polynomial algebra to easily spot structural patterns. But when dealing with a composite modulus like 15, the space is essentially a hybrid of a base-3 space and a base-5 space. The current techniques cannot "look" at both structures simultaneously without losing a lot of critical information. Addressing this gap requires exploring deep connections between computer science, geometry, and abstract algebra to formulate new ways of measuring the "complexity" of these hybrid mathematical spaces.

---

## 1. Brief Summary

**The Question in One Line with Prometheus Context:**
Can the asymptotic growth rate $\alpha_{3,15}$ of 3-term progression-free sets in $\mathbb{Z}_{15}^n$ be proven to be strictly less than the trivial upper bound $\min(3\alpha_{3,5}, 5\alpha_{3,3})$ derived from its prime factors, thereby overcoming the structural constraints of the slice-rank method in composite moduli spaces? 

**Prometheus Context:**
This inquiry represents a critical frontier in arithmetic combinatorics and algebraic complexity theory. Following the breakthrough resolution of the cap-set problem by Croot, Lev, Pach, Ellenberg, and Gijswijt [cite: 1, 6, 7], the slice-rank method formulated by Tao [cite: 2, 8] established rigid, exponentially small upper bounds for progression-free sets in vector spaces over finite fields $\mathbb{F}_p$ and prime-power rings [cite: 1, 9]. However, for composite moduli with mixed prime factors (e.g., $m=15=3 \times 5$), the method yields the generic envelope $r_3(\mathbb{Z}_m^n) \leq (0.9184m)^n$, relying on a reduction to the weakest subgroup [cite: 1, 10]. Investigating whether $\alpha_{3,15} < \min(3\alpha_{3,5}, 5\alpha_{3,3})$ probes the precise boundary where the slice-rank method's efficacy degrades [cite: 1], identifying whether this limitation is an artifact of the current proof constructs or a fundamental information-theoretic barrier intrinsic to composite modular tensors [cite: 5, 11].

---

## 2. Flagged Findings

### Current Consensus and the $(0.9184m)^n$ Envelope
The prevailing consensus in extremal combinatorics dictates that for any abelian group structured as $G = (\mathbb{Z}_m^n, +)$, the maximum size of a subset $A \subset G$ containing no non-trivial 3-term arithmetic progressions (3-APs) is exponentially smaller than the size of the group itself. Specifically, the introduction of the polynomial slice-rank method yielded the sweeping upper bound that for every integer $m \geq 3$, the maximum size $r_3(\mathbb{Z}_m^n)$ is bounded by $(0.9184m)^n$ [cite: 1, 11]. 

This universal constant factor, $0.9184$, is inextricably tied to the analytic optimization of the integral over prime fields, specifically deriving from the function $J(p) = \frac{1}{p} \min_{0<t<1} \frac{1-t^p}{(1-t)t^{(p-1)/3}}$, where $J(3) \leq 0.9184$ [cite: 1, 10]. Because every integer $m \geq 3$ possesses at least one odd prime divisor or is divisible by 4, mathematicians leverage a trivial lifting argument: $r_3(\mathbb{Z}_{m_1 m_2}^n) \leq m_1^n r_3(\mathbb{Z}_{m_2}^n)$ [cite: 1]. Thus, any composite modulus inherits the scaled bound of its most "restrictive" factor. For $m=15$, the consensus rests on the inequality $\alpha_{3,15} \leq \min(3\alpha_{3,5}, 5\alpha_{3,3})$ [cite: 1].

### Where the Consensus Might Be Wrong (and Why)
The prevailing reliance on isolated prime bounds to define composite limits is highly susceptible to **PATTERN_PRIME_GRAVITATIONAL_OVERFIT**. This analytical anti-pattern occurs when researchers assume that algebraic bounding phenomena observed perfectly in prime fields ($\mathbb{F}_p$) or pure prime-power rings ($\mathbb{Z}_{p^k}$) will linearly or multiplicatively scale into composite integer rings ($\mathbb{Z}_m$) without emergent structural penalties [cite: 1, 5]. By anchoring the expectations for composite moduli purely on multiplicative combinations of prime-power bounds—such as assuming the behavior in $\mathbb{Z}_{15}^n$ is strictly dictated by independent projections into $\mathbb{Z}_3^n$ and $\mathbb{Z}_5^n$—the current literature overlooks the potential for synergistic algebraic constraints that emerge only when multiple distinct prime characteristics interact [cite: 1].

If we view $\mathbb{Z}_{15}^n$ not merely as a Cartesian product of independent prime constraints, but as a unified algebraic variety, the polynomial representations of arithmetic progressions must satisfy constraints modulo 3 and modulo 5 concurrently. The current slice-rank framework fails to exploit this simultaneity [cite: 1, 2]. Therefore, it is highly likely that the true limit $\alpha_{3,15}$ is strictly less than $\min(3\alpha_{3,5}, 5\alpha_{3,3})$. The consensus that this bound is the "best possible" using current tools might be wrong if a generalized tensor rank metric—such as partition rank or G-stable rank—can be tailored to evaluate polynomials over mixed-characteristic rings directly, rather than projecting them down to their prime sub-fields [cite: 3, 4].

---

## 3. Problem Statement

### Precise Object and Result Being Interrogated
The precise mathematical object under interrogation is $r_3(\mathbb{Z}_{15}^n)$, which denotes the maximum cardinality of a progression-free set in the abelian group $\mathbb{Z}_{15}^n$. A set $A \subset \mathbb{Z}_{15}^n$ is considered 3-term progression-free (or a cap set equivalent) if there do not exist three distinct elements $x, y, z \in A$ such that $x + z = 2y \pmod{15}$ [cite: 1, 8].

To evaluate asymptotic behavior as the dimension $n$ scales toward infinity, we define the growth constant $\alpha_{3,m}$:
\[ \alpha_{3,m} = \lim_{n \to \infty} \left( r_3(\mathbb{Z}_m^n) \right)^{1/n} \]
The existence of this limit is guaranteed by Fekete's Subadditive Lemma, utilizing the super-multiplicative property $r_3(\mathbb{Z}_m^{n_1+n_2}) \geq r_3(\mathbb{Z}_m^{n_1}) r_3(\mathbb{Z}_m^{n_2})$ inherent in simple Cartesian product constructions [cite: 1, 10].

The fundamental relation bridging composite moduli to their prime factors is given by the projection inequality:
\[ r_3(\mathbb{Z}_{m_1 m_2}^n) \leq m_1^n r_3(\mathbb{Z}_{m_2}^n) \]
For the composite modulus $m = 15$, factoring into $m_1 = 3$ and $m_2 = 5$ (and vice versa), this provides two distinct trivial upper bounds:
1. $r_3(\mathbb{Z}_{15}^n) \leq 5^n r_3(\mathbb{Z}_3^n)$
2. $r_3(\mathbb{Z}_{15}^n) \leq 3^n r_3(\mathbb{Z}_5^n)$

Taking the asymptotic limits, this implies:
\[ \alpha_{3,15} \leq \min(3\alpha_{3,5}, 5\alpha_{3,3}) \]
The central open question, formally posed by Péter Pál Pach in the literature, is whether this inequality is strict:
**Question 1:** *Is it true that $\alpha_{3,15} < \min(3\alpha_{3,5}, 5\alpha_{3,3})$?* [cite: 1].

### Theoretical Implications of the Problem
Resolving this problem interrogates the deepest capabilities of the polynomial method. If $\alpha_{3,15} = \min(3\alpha_{3,5}, 5\alpha_{3,3})$, it implies that $\mathbb{Z}_{15}^n$ possesses no inherent geometric or additive constraints beyond those dictated by its most restrictive subgroup [cite: 1]. It would suggest that the optimal strategy for building a progression-free set in $\mathbb{Z}_{15}^n$ is simply to take the largest possible progression-free set in the dominant prime subgroup and lift it indiscriminately.

Conversely, proving that $\alpha_{3,15} < \min(3\alpha_{3,5}, 5\alpha_{3,3})$ would demonstrate that composite modular arithmetic enforces unique combinatorial geometries. This would require constructing a bounding tensor whose non-zero locus is strictly governed by properties unique to modulo 15 operations [cite: 1, 2]. This requires evaluating the exact point at which the slice rank of a diagonal tensor over a composite ring diverges from the sum of its independent field slice ranks [cite: 2, 6, 7].

---

## 4. Status & Bounds

### Last Known Status
The question regarding $\mathbb{Z}_{15}^n$ remains demonstrably **OPEN**. In Pach's exhaustive 2022 survey "Bounds on the size of progression-free sets in $\mathbb{Z}_m^n$", he explicitly notes regarding the strict inequality for $m=15$: "I do not see a proof of this statement" [cite: 1]. Despite vast improvements in bounds for prime powers ($p^k$) [cite: 1] and symmetric spaces using the slice-rank polynomial method, no novel technique has successfully bypassed the trivial projection limits for odd, non-prime-power composites like 15 [cite: 1, 5].

### Current Best Bounds
The bounds for progression-free sets in $\mathbb{Z}_m^n$ scale distinctly based on $m$. The absolute best current bounds relevant to the $\mathbb{Z}_{15}^n$ problem are derived from its prime factors:

**Upper Bounds:**
1.  **For $m=3$ (The Cap Set Bound):** 
    By Ellenberg and Gijswijt (2016) [cite: 6, 8], using the slice-rank framework [cite: 2, 7]:
    \[ r_3(\mathbb{Z}_3^n) \leq c_3^n \quad \text{where} \quad c_3 = \min_{0<t<1} \frac{1+t+t^2}{t^{2/3}} \approx 2.7552 \]
    This establishes $\alpha_{3,3} \leq 2.756$ [cite: 1, 12].
2.  **For $m=5$:**
    Using the general function $J(p) = \frac{1}{p} \min_{0<t<1} \frac{1-t^p}{(1-t)t^{(p-1)/3}}$ [cite: 1, 10]:
    The constant $\Gamma_5 = 5 \cdot J(5)$ defines the bounding base. From literature, we know $r_3(\mathbb{Z}_p^n) \leq (p \cdot J(p))^n$ [cite: 1, 10].
    For general primes, $\Gamma_p \leq 0.9184p$ [cite: 1, 12].
3.  **For $m=15$ (Composite derived):**
    Plugging into the trivial bounds:
    \[ \alpha_{3,15} \leq \min(3 \alpha_{3,5}, 5 \alpha_{3,3}) \]
    Given $\alpha_{3,3} \approx 2.756$, we have $5 \times 2.756 = 13.78$. 
    By the universal bounding principle $r_3(\mathbb{Z}_m^n) \leq (0.9184m)^n$ for $m \geq 3$ [cite: 1], we can also bound $r_3(\mathbb{Z}_{15}^n) \leq (0.9184 \times 15)^n \approx 13.776^n$ [cite: 1, 11]. 

**Lower Bounds:**
Lower bounds represent explicitly constructed progression-free sets. 
For a general even modulus $m$, Pach established a lower bound of $r_3(\mathbb{Z}_m^n) \geq C_m (\frac{m+2}{2})^n$ [cite: 1, 10]. However, for odd moduli like 15, lower bounds are typically built by taking Cartesian products of known tight bounds in low dimensions [cite: 1, 10].
For $m=3$, Edel established the lower bound $r_3(\mathbb{Z}_3^n) \geq 2.217389^n$ (from a construction in dimension 480) [cite: 9, 10]. 
Consequently, the lower bound for $\mathbb{Z}_{15}^n$ is at least the product of the lower bounds of its components, implying $\alpha_{3,15} \geq \alpha_{3,3} \times \alpha_{3,5}$. If $\alpha_{3,3} \approx 2.217$, the theoretical floor remains substantially below the upper bound envelope of $13.78$ [cite: 1, 9, 10].

### Conditional Qualifiers
The validity of the $(0.9184m)^n$ upper bound relies fundamentally on the condition that the progression is strictly an arithmetic sequence $x + z = 2y$. If the progression equation is altered (e.g., asymmetric weights), the underlying polynomial support matrix loses its diagonal structure, completely invalidating the slice-rank reduction [cite: 1, 2, 7]. Furthermore, for $m$ containing a large number of distinct prime factors (highly composite numbers), the divergence between the true maximum size and the trivial projection bound is theorized to widen drastically, though standard computational verification is impossible due to state-space explosion [cite: 1].

---

## 5. Literature (Primary Sources)

The body of literature directly addressing the polynomial method and composite modulus limits is highly specialized. The following represent the critical primary sources establishing the mathematical substrate of the problem:

1.  **P. P. Pach (2022). "Bounds on the size of progression-free sets in $\mathbb{Z}_m^n$". *Uniform Distribution Theory*, 17(1), 1-10.**
    *   *Significance:* The canonical modern text that explicitly raises the $\mathbb{Z}_{15}^n$ question. Pach extends the Croot-Lev-Pach and Ellenberg-Gijswijt methodologies directly to arbitrary moduli $m$ [cite: 1, 11, 13].
    *   *Core Finding:* Establishes the universal $(0.9184m)^n$ bound. Formulates the trivial projection boundary $r_3(\mathbb{Z}_{m_1 m_2}^n) \leq m_1^n r_3(\mathbb{Z}_{m_2}^n)$ and explicitly asks "Question 1: Is it true that $\alpha_{3,15} < \min(3\alpha_{3,5}, 5\alpha_{3,3})$?" [cite: 1].

2.  **J. S. Ellenberg & D. Gijswijt (2016). "On large subsets of $\mathbb{F}_q^n$ with no three-term arithmetic progression". *Annals of Mathematics*, 185(1), 339-343.**
    *   *Significance:* The breakthrough paper resolving the cap-set conjecture [cite: 8, 14, 15].
    *   *Core Finding:* Proven that $r_3(\mathbb{F}_3^n) \leq 2.756^n$. The authors adapted the polynomial method previously restricted to $\mathbb{Z}_4^n$ to fields of odd characteristic, bypassing decades of stagnant Fourier-analytic bounds [cite: 1, 6, 8].

3.  **E. Croot, V. F. Lev, & P. P. Pach (2017). "Progression-free sets in $\mathbb{Z}_4^n$ are exponentially small". *Annals of Mathematics*, 185(1), 331-337.**
    *   *Significance:* The Genesis paper for the new polynomial method paradigm [cite: 1, 14, 15, 16].
    *   *Core Finding:* Introduced an implicit hypermatrix rank definition (later formalized as slice rank) to prove that $r_3(\mathbb{Z}_4^n) \leq 3.61^n$. This proved that polynomial techniques could defeat Fourier methods for composite prime-power rings [cite: 1, 16].

4.  **T. Tao (2016). "A symmetric formulation of the Croot-Lev-Pach-Ellenberg-Gijswijt capset bound". *Terry Tao's Blog*.**
    *   *Significance:* Formalized the "Slice Rank" metric [cite: 1, 2, 3].
    *   *Core Finding:* Tao, along with Will Sawin, provided the symmetric, basis-independent definition of slice rank for tensors [cite: 2]. They established that a diagonal tensor $T(a_1, \dots, a_k) \neq 0 \iff a_1 = \dots = a_k$ has full slice rank [cite: 2, 7, 16]. This blog post became the de facto foundational literature for subsequent algebraic bounding techniques [cite: 1, 2].

5.  **A. Naslund & W. Sawin (2016). "Upper bounds for sunflower-free sets".**
    *   *Significance:* First major application of the slice-rank method outside of arithmetic progressions [cite: 2, 7].
    *   *Core Finding:* Demonstrated that slice rank could be applied to subset intersection structures (sunflowers), proving that subset structures mapping to specific tensor evaluations could be tightly bounded [cite: 2, 7]. 

6.  **H. Derksen (2020). "The G-stable rank for tensors and the cap set problem".**
    *   *Significance:* Introduces advanced invariant theory to tensor rank problems [cite: 4].
    *   *Core Finding:* Proposes "G-stable rank" as an alternative to slice rank and border rank, offering a theoretical pathway for capturing structural constraints in varieties where traditional slice rank fails to be semi-continuous or tight [cite: 4].

---

## 6. Attack Vectors

### Live Techniques: The Slice Rank Polynomial Method
To understand how the $\mathbb{Z}_{15}^n$ problem might be attacked, one must dissect the live technique currently governing the space: the slice rank method. The method relies on constructing a function $P: A \times A \times A \to \mathbb{F}$ (where $A$ is the target progression-free set) such that $P(x,y,z) \neq 0$ if and only if $x = y = z$ [cite: 2, 6]. 

1.  **Tensor Rank and Diagonal Tensors:**
    By definition, the slice rank $sr(P)$ is the minimum number of "slices" required to sum to the tensor $P$. A slice is a function of the form $f(x)g(y,z)$, $f(y)g(x,z)$, or $f(z)g(x,y)$ [cite: 2, 3, 6, 7]. Tao's foundational lemma proves that if $P$ is a purely diagonal tensor—meaning it is supported *only* when $x=y=z$—its slice rank is exactly equal to the cardinality of the set $|A|$ [cite: 6, 7, 16].
    
2.  **Polynomial Formulation:**
    For a cap set in $\mathbb{Z}_3^n$, the condition $x+z=2y$ implies $x-2y+z = 0$. In characteristic 3, $-2 \equiv 1$, so the condition is symmetric: $x+y+z = 0$ [cite: 1, 11]. We construct a polynomial $P(x,y,z) = \prod_{i=1}^n (1 - (x_i + y_i + z_i)^2)$. Because $A$ has no 3-APs, $x+y+z=0$ only occurs for the trivial progression $x=y=z$. Thus, $P(x,y,z)$ is a diagonal tensor on $A \times A \times A$ [cite: 1, 11].
    
3.  **Monomial Degree Bounding:**
    We expand $P(x,y,z)$ into a sum of monomials. The total degree of $P$ is $2n$. In any monomial $x^a y^b z^c$, the sum of the degrees is $2n$. By the Pigeonhole Principle, at least one of $a$, $b$, or $c$ must have degree $\leq 2n/3$. This allows us to factor the polynomial into a sum of slices (e.g., if $\deg(x^a) \leq 2n/3$, we group it as $f(x)g(y,z)$) [cite: 4, 7]. The number of possible monomials of degree $\leq 2n/3$ is exactly the slice rank bound, which evaluates to roughly $2.756^n$ [cite: 6, 7, 8, 12].

### Exhausted Approaches & Systemic Failures (PATTERN_RANK_PARITY_LEAK)
When researchers attempt to apply this exact live technique to $\mathbb{Z}_{15}^n$, the method breaks down completely. The equation $x - 2y + z = 0 \pmod{15}$ is no longer cleanly symmetric because $-2 \not\equiv 1 \pmod{15}$. Furthermore, 15 is not a prime, so $\mathbb{Z}_{15}$ is not a field; it has zero divisors (e.g., $3 \times 5 = 0$). 

Applying standard slice-rank bounding directly to $\mathbb{Z}_{15}^n$ suffers from **PATTERN_RANK_PARITY_LEAK**. This occurs when the polynomial evaluation designed to isolate the trivial diagonal $x=y=z$ inadvertently "leaks" rank dimension because the polynomial cannot sharply distinguish the $\mathbb{Z}_3$ and $\mathbb{Z}_5$ subgroup constraints simultaneously within a single tensor field [cite: 1, 2]. 

Specifically, to build a polynomial $P$ over $\mathbb{Z}_{15}$ that vanishes *unless* $x=y=z$, one must ensure that $P \equiv 0 \pmod{15}$ for all non-trivial progressions. Because 15 has zero divisors, a non-trivial progression might yield $x-2y+z = 3$. If we raise this to a power or manipulate it, we cannot easily force it to vanish without requiring excessively high polynomial degrees [cite: 11]. The higher the degree of the polynomial required to isolate the diagonal, the larger the pool of available monomials, which exponentially inflates the slice rank upper bound [cite: 4, 7]. Thus, the tensor rank bound "leaks" upward, becoming substantially looser than the trivial projection bounds $\min(3\alpha_{3,5}, 5\alpha_{3,3})$ [cite: 1, 2]. The direct slice-rank approach over the full ring is exhausted.

### Alternative Attack Vectors
To breach the composite modulus barrier, novel mathematical primitives are required:
1.  **Analytic Rank (Lovett, Gowers, Wolf):**
    Analytic rank measures the bias of a tensor when evaluated on uniformly random inputs from the group. Lovett proved that analytic rank is subadditive and bounded up to a constant by slice rank [cite: 3]. Since analytic rank operates using Fourier-analytic phase evaluations (characters), it might naturally handle the composite splitting via the Chinese Remainder Theorem more efficiently than slice rank [cite: 3].
2.  **G-Stable Rank and Geometric Invariant Theory:**
    Introduced by Derksen, G-stable rank connects tensor rank to the geometric invariant theory of algebraic groups [cite: 4, 5]. Unlike standard tensor rank, which is not semi-continuous (the limit of rank-2 tensors can be rank-3, leading to border rank disparities), G-stable rank operates strictly on Zariski-closed varieties [cite: 2, 4]. By mapping the progression-free constraints of $\mathbb{Z}_3$ and $\mathbb{Z}_5$ as simultaneous intersections of secant varieties (Segre varieties), one could define a defectivity metric that proves the geometric intersection in $\mathbb{Z}_{15}$ is strictly smaller than the product of independent varieties [cite: 4, 17].
3.  **Partition Rank:**
    A generalization of slice rank, partition rank allows for slices to be functions of arbitrary variable groupings (e.g., $f(x,y)g(z)$). While partition rank coincides with slice rank for 3-tensors, generalizing the progression constraint to higher-order interactions (hyper-progressions) in the composite space might force the partition rank to drop below the trivial bound [cite: 3].

---

## 7. Cross-References

The barrier encountered with $\mathbb{Z}_{15}^n$ is not an isolated mathematical anomaly; it mirrors fundamental roadblocks across theoretical computer science and extremal combinatorics.

### Related Open Problems
1.  **Matrix Multiplication Exponents ($\omega$):**
    The study of progression-free sets is deeply intertwined with bounding the tensor rank of matrix multiplication [cite: 5]. Generating optimal matrix multiplication algorithms relies on bounding the rank of the associated multiplication tensor. The recursive methods used heavily penalize structural inefficiencies, leading to massive constant factors [cite: 5]. Identifying a "roadblock" in handling composite moduli for polynomials exactly mirrors the roadblock in circuit complexity when trying to optimize read-once polynomials over composite bases [cite: 5].
2.  **The Erdős-Ginzburg-Ziv (EGZ) Problem:**
    The EGZ theorem guarantees that any sequence of $2m-1$ elements in an abelian group of order $m$ contains a zero-sum sequence of length $m$ [cite: 12]. When researchers attempt to bound higher-dimensional equivalents of EGZ, they routinely reduce the problem from composite $m$ to prime $p$ [cite: 12]. The inability to natively compute tight EGZ bounds for composites directly parallels the $\alpha_{3,15}$ failure.
3.  **Sunflower-Free Sets and Tri-Colored Sum-Free Sets:**
    The slice-rank method famously solved the asymptotic bounds for sunflower-free sets (Naslund-Sawin) [cite: 2, 7] and tri-colored sum-free sets [cite: 2, 5]. In these problems, the combinatorial structure can be directly modeled as a matching on an antichain, where the tensor's support equates precisely to the minimum number of slices [cite: 2, 7, 14]. Determining if a composite modular structure can be mapped to an antichain constraint remains a live cross-disciplinary target.

### Anti-Anchors and Candidate Primitives
*   **Anti-Anchor:** Do not rely on the assumption that limits of polynomials over fields identically map to rings with zero-divisors. The Combinatorial Nullstellensatz, which dominated extremal combinatorics before slice rank [cite: 11], notoriously fails when coefficients can annihilate each other modulo a composite [cite: 1, 11].
*   **Candidate Primitives:** 
    *   **Representation Theory over Mixing Groups:** Recent breakthroughs in circuit complexity have bypassed composite moduli roadblocks by using representation theory over "mixing groups" rather than abelian character theory [cite: 5]. Applying non-abelian representation theory to the commutative group $\mathbb{Z}_{15}^n$ by embedding it into a larger non-commutative geometric structure may yield the necessary strict inequality for $\alpha_{3,15}$ [cite: 5, 18].
    *   **Derived Moduli of Graded Modules:** In algebraic geometry, the derived scheme of stable sheaves over finite graded modules (using Maurer-Cartan equations) handles composite moduli efficiently by treating them as differential graded Lie algebras [cite: 18]. Transporting the $\mathbb{Z}_{15}$ tensor into a graded module could mathematically bypass the slice-rank parity leaks [cite: 18].

---
*End of Report.*

**Sources:**
1. [bme.hu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEezCcHHktIZJTG4GYoByi_n2GbIYde60fLn7E7KetKskUKtm3q0LlLsuV1mzFOLFRQiDeLrx7zdsZxgAzKQ4OVv5qzp6xh-MJRFoiRl2hxhOdoOPPBYUH8sHpSEQms8XWvRVcuBLo=)
2. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLOJLORDNjNvo4PXJZhJf3kv4W9NS0GsKeKXvHWbGVaWc1RS34eENP1nnXFtEN29XKYsQwkUP89jbJD0wiNdzZM8kWDtuLgT0ryCdXotc-9k6OMLnLm5bNyNd__HrZdcmhIW6jOcA0ZSy1RMKIm8F3F8nwy9L_QJif79enc1gbGKyD2g==)
3. [discreteanalysisjournal.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCiaPZB54Ltc1jNM24wmTpyVBG02Sg2aM89kkyAhHDatDDvUwkJGLQP5B6kcL5lPRvbQkD4UaGy2vFW63Cng26Lk9DLNGrnNgB0CxqbEYhN5Bi5OafGUkqzUr9D_U88eXUQnjR60cZEcj_vcQOrk4jmT7U4_OuJWukGM7hwiBT6TZijShXLWgto622Q1di1-jyLSExicXsdXo=)
4. [umich.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDt8ugFmzOy1H891mBhsZqSPCISnpC18sntIkuPMDnAyZmr06XvSy_uuVhWRt478TegpWyEioHJ6nttRXdFq2wtVGvRKwsM-6tQARkz1Tl4qLBe-ltMhd-uMHNVliVuoI1vGUWMOEtuIpvQAF733gAzcYRrWbsI3jTlTSQ-zMbHudD9CF4uWNOOlAxz-i7UFDrpug=)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6sA-msREQQpSQuSXvFnM8TyqfPSnJoiRr_7oLji__rHtxGryF-acDYGtO983736heHEYptrJ280rUvymrP7BhUyo2nPpmSxc2Wacy6XkCUFfR5W-pBCuv28P_sv6nCg5PYOQ8rSVbpJDfQnGsApuvgB4Ri9rTwh27KpwSNkqxJAfI_xOnPrmxnpzNN0NhkwJg6F8mPOCFy1Q7gw==)
6. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEs-eYbvAXXGBmwnITJ1X-94JAqU8zQoQDto3WN5F-QwwRIZQ-WdlsvV7wrIhkIcRfgu8XMsPXCATQFxTQocwzSwNT0e2_VhmQNgolax4SqNMP9JJbYGnFfo9CoEHEmlJudzBqHJMxrGbPjnbOQ2xSoWYQljBCpjWM=)
7. [univ-mlv.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEhR_UPB6crqTwYp1Pd86MVzWnMnruLVp8o-zdfuS78-v1s7uDfkgzlaMoJ6I4K2KisW1y6gQDAho2aSVHnh7V7OKWflo5ypPg59r0aX7E9vDaW8DAiH9rgKQPlS0IGNqc5Qg3C6UVE2AihVMlTQ==)
8. [mathplus.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTP2nsSit1lNYrEe10MNnz81hgsGzUXGD_k-3x_9uRaSsFIbaDviCxx8N4IAk8qAi0ReTo3F4g0Du-tkHnSjn_tU9xVH5RbLUDg8VS6jhOzWJD3L1wWbKe3KpDuLTFiboHRf2dvLLZ-elnv9QsB65ttuVHXNpFkJEvnREasFBEPISN8a5xOPj8OfYDl0f9emUZWc_z9qqKZn5LVwFAPcCJ7AQfsYqVGMofs3YBUa71hB2TXhZcGDA3H7AKGfBnld0Q)
9. [liv.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmPHksPwT3PsMoM6KbHnzNNifslIfXJ7y8y1Xrp8TsDS0XAo5Ej-xBhDghunUWCE5rt2NqPZDJEZHaaqxxHy1bo1zrE-ulxhOEqoiwmP3nf7POZEQ3A0Jm-sn7BnHJu4r4gBgRifP-vrU7jXHCXXGzXGUqPjvPdzbVaCICk4BXUg==)
10. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGUOHX2LyR9lOagHDjpCfQ-cMhtaAgIlRif9dcB2bbqLiNAkfiy7F0V1nY3XfkkrviwcN2ENvAqgK88176eC51YLWVjOtBHMKXaYeN8gZBmOPH6rN1Bm9rJ3mjOgivrobVDlzaQOil)
11. [mtak.hu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcbqy5-Bv-zaW9VmedIAzs9SLTdhoaCVE8SOncMOg1yUNFsSI5VcsvqY0TyOCRvR6HA1YpDn1wASJEZN64rT4Lx8B-JuZxqHX6MesxBlop9HRpLH61dyuvVmJBEez1-9fEdOVNd83k6LLlv8gaXKNM)
12. [rub.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFh4JhKbCxb1pziipOLdMWiVl6qSUKFOsjLmXO5l6QDMPNIaICzNih8rFrY54LtLYwCVXPhw87F8nZa1KDZR9BHolJfGZyOj38Lc1zZpoXjoUcDzZ-KEtE5TLMorBZFksahEvDd1r7Wk9rl)
13. [elte.hu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcvI0LzVPnWr9ysRZ19jKAHzMEfy9rVFAv904MSmHpCCWzV9GJwLqzOZhs01XqV89_nV03HZqlxqJxWUCwCcPi48iftTH--RH7TxVp_eSzk6Bo0inBbndGSWRS5ZQAa-dMROI7GBN6iq0DYxd3M14LyU2p9D8gFkLPRcLHK23zv5SA)
14. [theoryofnumbers.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7GeRsy3otAa8yltvFxgugN68x7RGgtYuqY_zvauELpTZwsmIma8kXFD-xsZ2-5LJ9JWf5ep0DkkKl7YmOW7cqROPUW8qqNUwxwbGL9M9COUZrSz7b1x88j9dCzoLWUc9ZkvxJGbDLEef5s_knugtk7g==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_lUgJik6aIXtc3FskSy1Fga0EE63s2xSCQbZO0BAQp5gEBtYk3q0RlNNCaRDIDsGNJlcCZIgz64QjCLJd_6dG63ZT16LK-2nAafgcOvIcpvuq9rGorw==)
16. [uq.edu.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEp1Vdn5O-lMONG7mBxaXk_jYfS5dNhYIjVQT-qsC_wPJjnezwgcDucFt_viMiu4LFMoPMT-uPUdYe5WZjF4o57RUtBYccXnbNmg7QMYiPmDt6_FCwgC_mJCPAhbImuZET7QscMKFjaFCA=)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFt8ifGXedlsz1w3ZInUINa5l5z13ABI9U5Kj3QNwvvXOLSy-545rLV-tgG6eKqAw13GRfTCurYgnuLWPkLiAR8-O8pgXJ4Lc7N88vrImxLl7y0olSVDyitJYg9KLM1CHdfGYzvJhPOHqUtmvfcaqJqb5ZfGboyIgfciZAOaAqA9kkyp2qGNK-Ei8HchyCmHJlnLyo=)
18. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfPnnVGPJHzmjLFX1H5x8ha0Cbi4ku_X22fcyNp5XTrVgsrGEM_okqlyH9tVUqXavdyXQxCv-Fx2u2fjnKliZjKGtejPMHIUXcMxwIgOxil2UXUisdy3rgR3wT2Nfoy7Wwvw==)

