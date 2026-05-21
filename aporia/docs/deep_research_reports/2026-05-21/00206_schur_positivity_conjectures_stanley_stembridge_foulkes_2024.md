# Schur positivity conjectures (Stanley-Stembridge, Foulkes) 2024-2026

**Pythia queue id:** 206
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdSa2NQYXJEbEEtSzBfdU1QdnR1dXdBNBIXUmtjUGFyRGxBLUswX3VNUHZ0dXV3QTQ
**Elapsed:** 254s
**Completed at:** 2026-05-21T18:00:37.125746+00:00

---

# Schur Positivity Conjectures: Breakthroughs in the Stanley-Stembridge and Foulkes Conjectures (2024-2026)

**Key Points:**
*   **Stanley-Stembridge Conjecture:** Recent research indicates that the longstanding Stanley-Stembridge conjecture regarding the $e$-positivity of chromatic symmetric functions for $(3+1)$-free graphs has likely been resolved. Tatsuyuki Hikita presented a probabilistic proof in late 2024, followed by an independent algebraic proof by Griffin, Mellit, Romero, Weigl, and Wen in 2025 using the $\mathbb{A}_{q,t}$ algebra [cite: 1, 2].
*   **Foulkes Conjecture:** Substantial progress has been achieved in the study of plethysm coefficients. The stable version of Foulkes' conjecture was proven by Bowman and Paget utilizing Schur-Weyl duality and the partition algebra [cite: 3]. Furthermore, the $q$-Foulkes conjecture for Gaussian coefficients saw new results by Gutiérrez and Szwej in 2025 [cite: 4]. 
*   **Claw-Free Conjecture:** The broader Claw-free conjecture remains an open frontier. However, novel combinatorial tools such as "special rim hook $G$-tabloids" have successfully proven the Schur positivity of specific graph families, such as generalized nets [cite: 5, 6]. 
*   **Distributive Lattices:** Richard Stanley's 1998 conjecture that the incomparability graphs of all distributive lattices are Schur-positive (and thus "nice") was definitively disproved in 2024 [cite: 7]. 

**Summary:** 
The period between 2024 and 2026 has been marked by seismic shifts in algebraic combinatorics, specifically concerning Schur positivity and $e$-positivity conjectures. The apparent resolution of the Stanley-Stembridge conjecture bridges decades of work linking graph colorings to symmetric functions. Simultaneously, leaps in representation theory have allowed mathematicians to crack long-standing variants of the Foulkes conjecture by mapping symmetric group representations to geometric and algebraic frameworks. While structural mysteries—such as the full resolution of the Claw-free conjecture and the Shareshian-Wachs conjecture—remain, these years have provided powerful new machineries that redefine the boundary of known combinatorial mathematics.

---

## 1. Introduction to Positivity in Algebraic Combinatorics

Algebraic combinatorics frequently investigates the structural properties of algebraic entities whose coefficients harbor deep combinatorial, geometric, or representation-theoretic meaning. Within the ring of symmetric functions $\Lambda$ over a base field $\mathbb{F}$ (typically $\mathbb{Q}$ or $\mathbb{C}$), there exist several classical bases indexed by integer partitions $\lambda \vdash n$: the monomial symmetric functions $\{m_\lambda\}$, the complete homogeneous symmetric functions $\{h_\lambda\}$, the elementary symmetric functions $\{e_\lambda\}$, the power sum symmetric functions $\{p_\lambda\}$, and the Schur functions $\{s_\lambda\}$ [cite: 8]. 

A central, overarching theme in this pursuit is the quest for **positivity** [cite: 8]. A symmetric function $f \in \Lambda$ is said to be *Schur-positive* if, when expressed as a linear combination of Schur functions $f = \sum_{\lambda} c_\lambda s_\lambda$, all coefficients $c_\lambda$ are non-negative integers (or polynomials with non-negative integer coefficients in the presence of parameters like $q$ and $t$) [cite: 8]. Establishing Schur positivity is of profound importance: it typically signifies that the formal algebraic sum is the genuine Frobenius characteristic of a naturally occurring $S_n$-module, thereby revealing deep underlying geometric or representation-theoretic phenomena [cite: 8]. 

Similarly, a function is *$e$-positive* if its expansion in the elementary symmetric function basis $\{e_\lambda\}$ yields non-negative coefficients. Because the elementary symmetric functions are themselves Schur-positive (a consequence of the dual Jacobi-Trudi identity and their representation-theoretic origin as the sign representation twisted with permutation modules), $e$-positivity is a strictly stronger condition than Schur positivity [cite: 9]. 

Richard Stanley’s influential survey on positivity problems in algebraic combinatorics enumerated a central list of conjectures that have driven research for decades [cite: 10]. The period from 2024 to 2026 has witnessed the resolution or significant advancement of several of these major problems, most notably the Stanley-Stembridge conjecture (Problem 21 on Stanley's list) and the Foulkes conjecture [cite: 10, 11, 12]. This report provides an exhaustive, highly detailed synthesis of these breakthroughs.

---

## 2. The Stanley-Stembridge Conjecture

### 2.1 Formulation and Historical Context
In 1995, Richard Stanley extended the classical concept of counting proper graph colorings by introducing the **chromatic symmetric function** $X_G$ of a graph $G$ [cite: 5]. For a graph $G = (V, E)$, a proper coloring is a map $\kappa: V \to \mathbb{Z}^+$ such that $\kappa(u) \neq \kappa(v)$ for all $\{u, v\} \in E$. The chromatic symmetric function is defined as:
\[ X_G = \sum_{\kappa} \prod_{v \in V} x_{\kappa(v)} \]
where the sum is taken over all proper colorings $\kappa$ of $G$ [cite: 13]. 

The seminal Stanley-Stembridge conjecture, originally formulated in 1993 in the context of immanants of matrices and reformulated by Stanley in 1995, asserts that if $G$ is the incomparability graph of a $(3+1)$-free poset, then its chromatic symmetric function $X_G$ is $e$-positive [cite: 12, 14]. A poset is $(3+1)$-free if it does not contain an induced subposet consisting of a chain of three elements and an isolated element. Equivalently, the incomparability graphs of $(3+1)$-free posets are exactly the claw-free incomparability graphs.

In 1996, Vesselin Gasharov made significant headway by proving that $X_G$ for claw-free incomparability graphs is Schur-positive, using a sign-reversing involution on a combinatorial object called a $P$-array [cite: 7, 9]. However, the stronger condition of $e$-positivity remained elusive. Guay-Paquet (2013) later reduced the Stanley-Stembridge conjecture to the case of **unit interval graphs** (which correspond to posets that are both $(3+1)$-free and $(2+2)$-free) [cite: 12].

### 2.2 The Shareshian-Wachs Refinement
In 2012, Shareshian and Wachs introduced a $q$-analog of the chromatic symmetric function, known as the **chromatic quasisymmetric function** $X_G(x;q)$, which refined the proper colorings by counting the number of "ascents" (edges where the smaller vertex has a smaller color) [cite: 13, 15]. They conjectured that for unit interval graphs, this refined function expands into the elementary basis with coefficients that are polynomials in $q$ with non-negative integer coefficients, i.e., $c_\lambda(e;q) \in \mathbb{Z}_{\ge 0}[q]$ [cite: 1, 13]. This is known as the Shareshian-Wachs conjecture, which strongly refines the Stanley-Stembridge conjecture (recovered by setting $q=1$) [cite: 15].

Shareshian and Wachs also established a deep geometric connection, conjecturing (and later proving with Brosnan and Chow) that the involution $\omega X_G(x;q)$ represents the Frobenius characteristic of the equivariant cohomology ring of regular semisimple Hessenberg varieties [cite: 15, 16]. 

### 2.3 Hikita's Probabilistic Proof (2024)
In October 2024, Tatsuyuki Hikita of Kyoto University posted a preprint providing an affirmative proof of the Stanley-Stembridge conjecture [cite: 1, 12]. Hikita's approach was highly innovative, bypassing heavy algebraic geometry to give a direct probabilistic interpretation of the $e$-expansion coefficients $c_\lambda(e; 1)$ of the chromatic quasisymmetric function for unit interval graphs [cite: 12]. 

Hikita analyzed the elementary symmetric function expansion of $X_G(t)$ (a specialized normalization evaluated at $t \in \mathbb{R}_{>0}$) and constructed an inductive, positive formula for the coefficients $p_\lambda(e; t)$ [cite: 14]. By extracting this probability distribution on the set of partitions of $n$, Hikita provided an explicit formula (often referred to as "Hikita's (6)" in discussions) [cite: 1, 14]. 

The probabilistic process operates as follows: Given a unit interval graph $G$ naturally labeled on the vertex set $\{1, \dots, n\}$, let $h'_i$ denote the number of vertices less than $i$ that are not adjacent to $i$ [cite: 1]. Hikita described a random process for generating a standard Young tableau with $n$ boxes. Box $i$ is placed sequentially based on alternating segments of bits $\delta_j$, determined by whether the partial tableau has a box in column $j$ whose entry exceeds $h'_i$ [cite: 1]. Using continuous random variables $X(a_1,b_1,\dots,a_m,b_m)$ distributed on the real line, Hikita proved that the probability of generating a tableau of shape $\lambda$ exactly matches the scaled $e$-expansion coefficient [cite: 1, 13].

The verification of this formula relied heavily on the "modular law" recurrence for chromatic symmetric functions, pioneered by Abreu and Nigro [cite: 13, 17]. The modular law allows the reduction of the computation to cases where the complementary Hessenberg function has a specific simplistic form, enabling a complex algebraic induction [cite: 13, 18]. The consequence of Hikita's theorem is that $c_\lambda(e;t) \ge 0$ for all real $t > 0$, and setting $t=1$ perfectly resolves the classical Stanley-Stembridge conjecture [cite: 14].

### 2.4 The Algebraic Proof by Griffin et al. (2025)
Following Hikita's elementary and probabilistic breakthrough, a team consisting of Sean Griffin, Anton Mellit, Marino Romero, Kevin Weigl, and Joshua Jeishing Wen posted an independent algebraic proof in April 2025 [cite: 1, 2]. 

Griffin et al. sought to explain Hikita's formula using the advanced algebraic machinery of the $\mathbb{A}_{q,t}$ algebra, originally developed by Carlsson and Mellit in their proof of the Shuffle Conjecture [cite: 1, 17, 18]. They successfully constructed a "master formula" for $q$-chromatic symmetric functions, expanding them into **Macdonald polynomials** with the inclusion of an extra parameter $t$ [cite: 2, 18]. 

By applying specialized values to the parameter $t$, Griffin et al. were able to derive multiple historic expansions:
1.  **Setting $t=1$:** The master formula recovers Hikita's explicit elementary basis formula, yielding a second, structurally distinct proof of the Stanley-Stembridge conjecture [cite: 2].
2.  **Setting $t=0$:** The formula yields an expansion into Hall-Littlewood symmetric functions [cite: 2].

This alternate proof firmly roots the Stanley-Stembridge conjecture within the landscape of modern representation theory and moduli spaces, specifically tying the combinatorics of parabolic flag Hilbert schemes to graph colorings [cite: 18]. It should be noted that while both Hikita's and Griffin et al.'s proofs settle the original $q=1$ Stanley-Stembridge conjecture, the full Shareshian-Wachs conjecture stating that $c_\lambda(e; q) \in \mathbb{Z}_{\ge 0}[q]$ as a polynomial remains an open frontier of active investigation [cite: 1].

---

## 3. The Foulkes Conjecture and Plethysm Coefficients

### 3.1 Understanding Plethysm
Plethysm, denoted $f[g]$ or $f \circ g$, is a binary operation on symmetric functions introduced by D.E. Littlewood. It is most naturally understood through the representation theory of the general linear group $GL(V)$ [cite: 19]. If $U, V, W$ are vector spaces over $\mathbb{C}$, and we have polynomial representations $\phi: GL(U) \to GL(V)$ and $\psi: GL(V) \to GL(W)$ with respective characters $f$ and $g$, then the composition $\psi \circ \phi: GL(U) \to GL(W)$ has the character $g[f]$, the plethysm of $g$ and $f$ [cite: 19].

In the context of the symmetric group $S_n$, plethysms correspond to induced modules from wreath products. The plethysm coefficient $p(\nu, \mu, \lambda)$ is the multiplicity of the Schur function $s_\lambda$ in the plethysm product $s_\nu \circ s_\mu$ [cite: 20, 21]. For partitions $(h)$ and $(m)$, the decomposition of the plethysm $s_{(h)}[s_{(m)}]$ into irreducible $S_{mh}$ modules corresponds to the decomposition of the **Foulkes module** $H(m^h)$, denoted algebraically as $\text{ind}_{S_m \wr S_h}^{S_{mh}} \mathbb{C}$ [cite: 11, 22].

### 3.2 Formulation of the Foulkes Conjecture
Formulated by H.O. Foulkes in 1950, the Foulkes conjecture asserts that for any integers $a \le b$, the Foulkes module $H(b^a)$ is isomorphic to a submodule of $H(a^b)$ [cite: 11, 23]. In the language of symmetric functions, this is equivalent to stating that the difference $h_b[h_a] - h_a[h_b]$ (or $s_b[s_a] - s_a[s_b]$) is Schur-positive [cite: 19, 23]. Alternatively, let $p((m), (n), \lambda)$ denote the plethysm coefficient; the conjecture claims $p((m), (n), \lambda) \le p((n), (m), \lambda)$ for $m \le n$ [cite: 22].

A more robust variant, known as the **Foulkes-Howe Conjecture**, posits that a natural candidate map $\psi_{a,b}$ between the permutation representations of set-partitions has full rank whenever $a \neq b$ [cite: 24]. The calculation and bounding of these plethysm coefficients are considered some of the most critical open problems in algebraic combinatorics, bearing heavy implications for Geometric Complexity Theory (GCT) and the resolution of complexity class separations via occurrence and multiplicity obstructions [cite: 24, 25].

### 3.3 Bowman and Paget's Resolution of the Stable Foulkes Conjecture
Before 2023, Foulkes' conjecture was only proven for small values of $a$ (e.g., $a=2, 3, 4, 5$) or asymptotically when $a \ll b$ by Brion [cite: 22]. A massive leap occurred when Chris Bowman and Rowena Paget utilized Schur-Weyl duality to attack the stable version of the conjecture [cite: 3].

In a series of papers published in the *Journal of Algebra* (2024) and *Advances in Mathematics* (2024, alongside Mark Wildon), Bowman, Paget, and Wildon shifted the paradigm by connecting wreath products of symmetric groups to the **partition algebra** and the **ramified partition algebra** [cite: 3, 20, 21]. They interpreted arbitrary plethysm coefficients as the multiplicity of a composition factor in the restriction of a module from the ramified partition algebra to the standard partition algebra [cite: 20, 21]. 

Bowman and Paget proved that for any arbitrary partition $\lambda$, and for sufficiently large integers $m, n, p, q \ge |\lambda|$, the stable plethysm coefficients satisfy:
\[ p((q), (p), \lambda[pq]) = p((n), (m), \lambda[mn]) \]
[cite: 3, 22]. By establishing this stability, they demonstrated that an isomorphism in the partition algebra effectively "does not see" any difference between $m$ and $n$ once they are sufficiently large [cite: 3]. Consequently, they proved that discarding a finite list of values, the **strengthened Foulkes conjecture holds for stable plethysm coefficients** in a uniform and elementary fashion [cite: 3, 22].

### 3.4 Gutiérrez and Szwej: The $q$-Foulkes Conjecture (2025)
Parallel to the symmetric group approach, the Foulkes conjecture possesses several generalizations, including the $q$-Foulkes conjecture regarding Gaussian ($q$-binomial) coefficients [cite: 4, 26]. For the special linear Lie algebra $\mathfrak{sl}_2(\mathbb{C})$, these generalizations assert that given $a \le c \le d \le b$ with $ab = cd$, the representation $\mathrm{Sym}^a\mathrm{Sym}^b\mathbb{C}^2$ is a subrepresentation of $\mathrm{Sym}^c\mathrm{Sym}^d\mathbb{C}^2$ [cite: 4]. 

Combinatorially, this implies that the polynomial $( \begin{smallmatrix} c+d \\ c \end{smallmatrix} )_q - ( \begin{smallmatrix} a+b \\ a \end{smallmatrix} )_q$ has non-negative coefficients [cite: 27]. Justin Troyka (2024) explored this via lattice paths, interpreting the non-negativity as showing that the number of size-$n$ partitions fitting inside an $a \times b$ rectangle is at least the number fitting inside a skinnier $c \times d$ rectangle of the same area [cite: 27].

In July 2025, Álvaro Gutiérrez and Michał Szwej posted a breakthrough preprint presenting a short proof of the $q$-Foulkes conjecture in the case where $a$ divides $c$ (or $d$) [cite: 4]. Because their proof applies when $a$ divides $c$, it inherently includes all prime values of $a$ [cite: 4]. This marked the very first proof within this family of conjectures that is valid for infinitely many values of $a$; previously, only the highly restricted cases of $a=2$ and $a=3$ were known (the latter proven by Zanello in 2018 using Zeilberger’s KOH theorem) [cite: 4, 27].

---

## 4. The Claw-Free Conjecture and Graph Schur Positivity

While the Stanley-Stembridge conjecture limits its scope to $(3+1)$-free incomparability graphs, a broader question was posed by Vesselin Gasharov in an unpublished 1998 work (popularized by Stanley): Are all **claw-free graphs** Schur-positive? [cite: 7]. A graph is claw-free if it contains no induced subgraph isomorphic to the bipartite claw graph $K_{1,3}$, which famously serves as the smallest graph that is neither $e$-positive nor Schur-positive [cite: 5, 9]. 

Gasharov's 1996 theorem successfully proved that all claw-free *incomparability* graphs are Schur-positive using $P$-arrays [cite: 9]. However, the general Claw-free conjecture—which removes the incomparability condition—remains one of the central unsolved problems in chromatic symmetric function theory [cite: 5, 9]. 

### 4.1 Combinatorial Innovations: Special Rim Hook $G$-Tabloids
In late 2024, Ethan Shelburne and Stephanie van Willigenburg introduced a novel combinatorial method to attack the Claw-free conjecture [cite: 5]. They defined a new object known as a **special rim hook $G$-tabloid** (SRH $G$-tabloid) [cite: 5]. 

For a graph $G$ equipped with a partial order on its vertices such that non-adjacent vertices are comparable, an SRH $G$-tabloid is a special rim hook tabloid whose cells are filled with the vertices of $G$ such that [cite: 6, 9]:
1. Cells spanned by the same rim hook form a stable (independent) set in $G$.
2. Reading the vertices in a rim hook in northeast order yields an increasing sequence [cite: 9].

Using this framework, they generalized a formula to compute any Schur coefficient of $X_G$ [cite: 28]. Applying sign-reversing involutions on these SRH $G$-tabloids, they derived recurrence relations for families of claw-free graphs known as **generalized nets** [cite: 5, 6]. A generalized net $GN_{n,m}$ is a complete graph on $n$ vertices with $m$ degree-one vertices appended to distinct nodes [cite: 9]. Shelburne and van Willigenburg successfully proved that the entire family of generalized nets is Schur-positive, providing a new methodological pathway for resolving the broader Claw-free conjecture [cite: 5, 29]. 

Furthermore, full Schur-positivity classifications for complete multipartite graphs were established, extending Wang and Wang's earlier results to show that a complete multipartite graph $K_\lambda$ is Schur-positive if and only if $\lambda_i \in \{1, 2\}$ for all $i$, or $\lambda = (3, 2^\beta)$ for some $\beta \ge 1$ [cite: 9, 30].

### 4.2 Distributive Lattices and the "Nice" Property
Another major avenue regarding Schur positivity was Stanley's 1998 conjecture concerning distributive lattices. Stanley hypothesized that the boolean algebra $B_n$ was Schur-positive, and more broadly, that the incomparability graph of *any* distributive lattice is Schur-positive [cite: 7]. 

Stanley defined a graph $G$ to be "nice" if, whenever $G$ possesses a stable partition of type $\lambda$ (the partition obtained by arranging the sizes of the independent sets in decreasing order), it also possesses a stable partition of type $\mu$ for every partition $\mu$ dominated by $\lambda$ ($\mu \unlhd \lambda$) [cite: 7]. It is a known proposition that if a graph is Schur-positive, it must be nice [cite: 7].

In a 2024 paper published in the *SIAM Journal on Discrete Mathematics*, this long-standing conjecture was resolved in the negative [cite: 7]. The authors constructed explicit families of distributive lattices whose chromatic symmetric functions are not Schur-positive. Consequently, this demonstrated that distributive lattices need not possess the "nice" property, shutting the door on Stanley's optimistic 1998 hypothesis [cite: 7]. 

---

## 5. Advanced Geometries: Macdonald Polynomials and the $\nabla$ Operator

The pursuit of Schur positivity frequently intersects with the geometry of Hilbert schemes and the theory of Macdonald polynomials. Haiman’s celebrated proof of the Macdonald Positivity Conjecture demonstrated that the symmetric Macdonald polynomials $\tilde{H}_\mu(x; q, t)$ expand into the Schur basis with coefficients in $\mathbb{Z}_{\ge 0}[q,t]$ [cite: 8, 31]. This was achieved by identifying the polynomials as the Frobenius characteristic of the doubly graded Garsia-Haiman module [cite: 8].

A central object acting on these polynomials is the Bergeron-Garsia nabla operator $\nabla$, defined as the eigenoperator such that $\nabla \tilde{H}_\mu = T_\mu \tilde{H}_\mu$ [cite: 8]. The operator is intimately tied to the Shuffle Conjecture (proved by Carlsson and Mellit in 2018) and the Delta Conjecture, which provide combinatorial parking-function formulas for $\nabla e_n$ and $\Delta'_{e_{k-1}} e_n$ [cite: 8, 31]. 

The Schur positivity of $\nabla e_n$ can be gracefully deduced through its formulation as a weighted sum of **LLT polynomials** (Lascoux, Leclerc, and Thibon), which Grojnowski and Haiman proved are unconditionally Schur-positive [cite: 8]. 

In 2026, research by Menghao Qu further expanded this frontier by investigating the Schur positivity of modified Hall-Littlewood polynomials (which are Macdonald polynomials evaluated at $t=0$) indexed by two-column partitions under the action of the $\nabla$ operator [cite: 8, 32]. Qu successfully resolved two conjectures posed by Bergeron, Garsia, Haiman, and Tesler, demonstrating that the Schur positivity holds not just for $\nabla$, but can be extended to arbitrary powers $\nabla^k$ for all integers $k \ge 1$ [cite: 8, 32]. This ongoing work highlights the deep structural unity between $q,t$-symmetric functions, flag varieties, and representation theory.

---

## 6. Computational Complexity and Geometric Connections

The problem of calculating plethysm coefficients, Kronecker coefficients, and resolving Schur positivity is not merely an abstract structural exercise; it is intrinsically tied to computational complexity. In the framework of **Geometric Complexity Theory (GCT)**—spearheaded by Mulmuley and Sohoni—the separation of complexity classes (like P vs NP) was originally hypothesized to be achievable via "occurrence obstructions," which rely on the vanishing behavior of representation-theoretic multiplicities in coordinate rings of specific group varieties [cite: 24, 25]. 

While the existence of strong occurrence obstructions was disproved by Ikenmeyer, Panova, and Bürgisser (2016-2019), more nuanced approaches involving "multiplicity obstructions" remain viable and open [cite: 24, 25]. The computation of plethysm coefficients is widely believed to not lie within the $\#\mathsf{P}$ complexity class, implying that positive combinatorial formulas (like the Littlewood-Richardson rule for Schur multiplication) may fundamentally not exist for generalized plethysms or Kronecker coefficients [cite: 24]. 

However, the recent successes by Bowman, Paget, and Wildon in computing stable plethysm coefficients using partition algebras [cite: 3], as well as Griffin et al.'s algebraic expansions using the $\mathbb{A}_{q,t}$ algebra [cite: 2], provide powerful new algorithmic and geometric pathways to bypass these complexity barriers in specific, highly structured subcases. 

---

## 7. Conclusion

The years 2024 through 2026 will be remembered as a renaissance period for positivity conjectures in algebraic combinatorics. 

1.  The **Stanley-Stembridge conjecture** has transitioned from a stubborn 30-year-old mystery into a resolved theorem, thanks to Tatsuyuki Hikita's brilliant probabilistic synthesis and the subsequent algebraic verification by Griffin, Mellit, Romero, Weigl, and Wen [cite: 1, 2]. The chromatic symmetric functions of $(3+1)$-free graphs are definitively $e$-positive, cementing the deep relationship between poset avoidance and symmetric function bases.
2.  The **Foulkes conjecture** saw its stable regime completely demystified by Bowman and Paget using the partition algebra [cite: 3], while Gutiérrez and Szwej shattered the small-parameter barrier for the $q$-Foulkes conjecture [cite: 4].
3.  While Stanley's distributive lattice conjecture fell to negative counterexamples [cite: 7], the introduction of special rim hook tabloids offers a beacon of hope for eventually cracking the overarching **Claw-free conjecture** [cite: 5].

As combinatorialists continue to leverage heavy machinery from representation theory, Schur-Weyl duality, and moduli spaces, the boundaries of what is considered computationally and algebraically "positive" are rapidly expanding, promising an even deeper unification of geometry and discrete mathematics in the years to come.

**Sources:**
1. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBgRwePsyneVcCqy3PMtiMKu1yVkWEKQseumzSVvNLLHPKZ_Fkfn6bDTo8pKhRPOiFWSA9uV7t-xfHdlEqKIBtPIy-5GVGZeVV42REnWW_fnfwdEVFW8-YHYS-r8T25oMQC_8Y0Tqrb52Z8L6zzk8sKmw0L6GZM_Z510dVI-seciR9D2GlleFF0h4=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwwZux5WP06ToHXtaK5Fk85mDwU3n6Byb14HjNObxfZHj_Qd_gprQB1O_5OT-IKdS_foDFXquU_ewC08UOXwCtvqoP6wjDOA4KUzRH0lfL9eIUX58m)
3. [kent.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEw5x9HRagqk_fbT9wTUTmTXKuKyiLK-OzNmjq_p_b_kw8FoR532Z_q0wxpkJxvlGa92A2XqpBE5P-FMj99qSgXN_3TGSFG4ZKnAr__P87Q2vo4Bm8e3u1kKhNgWLTyZA==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFo1ghfbA4onS2_WzedKkrBTm4__i64BwHRhLzjW22gCz_RW7TdmzupDsAyMNyAdopZjLKWiHubYYm7EUIQ7A3t-_7LXZXalp7_dGr11zpkiq7P26j_)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGXdnVc8SRCUTC0WTdwV3pM92wQXbKlDM0akt4dHaDVSk9I3pQU66ZCJwP0raUqlAYhkz8X9KdtGOvBf4ZQ1mArGvG60Nb9ThN7hjiJfuFpUFtngxB)
6. [haifa.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXm-jnbs-AjPgg3HETiczpORMWmwGqMVNvNn85Bl9OZ66oENGfY56Xq7hvBaZWSiH7PV2kb5x-9Bw3y4iuMZUF_QM6vULJ-1oDGJftSiLN99xMiOEJEm6mmJSnCrVTZ6WO97lZR6Lgl5mfMjdAfVw=)
7. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEynJBRwdWgdJaLVzwUP93lrgeJd3ZT94HoeOHrSE6_3BMVZt_w6loj11r_ne35H1-h4WS7k8x2GMg1DVM_41bWhdK96qSL-rfalYC1tk2NCPbuWe7qz5gTSPGqhVWErj6V5w==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwurfD8s30-caY_Sn-TYdVmP_DkN4Db6h12VbKHp205h3pyU3KTMqn7H70G85JK2Y8wb3gQsCzSrgkYhuZadvX9ekrVdiXxWunM0d3F8nm7iqF4QMG)
9. [wm.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnP5vBsc20RorTYvq84cPsFvgnQbAtFc0OMSzvUlGm_Qt71tJxwYa5UkU4Mbn2u5_7q7DWAq-s0MNt1wAwUrhbyk2ox_34qrVQQ_OB9_DMQImu2MxdmSB2wQ1nkaHfhbVgfFBuY59YvyxnKfLTLgQ=)
10. [ijsret.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0Tlh-EPVjAnPuKXofJh-zFPLgYL6oqvaKhHQjAKlU8oUcqNqoThR1_GTplC22W49-_eVvg18agLKqxYIbTTKNub6TOsoqwE2dbq2PcOH4Q1SUcO3zhJ7vKa_Ml2dObC5R3Akc6LvjerndIxK2XlXV8g-73Q==)
11. [royalholloway.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGiZFrabY2DxsbRCb_QrhqIJgDG2RX_q_Qx9-v0UjACVc_CCKD1iJRK6xkH4tCXiclfukLS68jxnqcbaA2hLVhxk6AWJ74JbKmmjAPfx8MfZ25FShuyHJQbRcT5CXzhz_pRh7RVRB0RFL-sVGeUKNyjaq33)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFI719tmWigyu_38Lh6lsAnTpdXJLG0m29U5cW13LiB7IiQ5O3p3eBSCyPczgHnJYQDa1fMpVJygWTRdojc977LefiK86j4uJ6ESXsb05FTvQ4lndLgxnXx)
13. [mathematicalgemstones.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvtTcCTIveeisla2RzvcgE0gweFVZGUDHZ6GrSVlLIWaDbUqf04wetKNn_TiMPErb-xltu_qgKB7-dxEe-o1I2aKtNbOVk1KA1WZwb15JvSPup33WJ33ERInqeV53xMXUzm0eHP5cTrtjjYwLq7SjCMBjQ1YsRDP0b5Q==)
14. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7-5HoYuYNOJLCrZkxZsyEbcydOv8zTJDo1PG8Tlep9z-0FV8HM2x-KvczfhzMr535bkILf2DhpO42h-NilplYm4Y9ynTjaDColoutxoVFeTHeKeMWJEL3NAi35p3SXORD0s-t48NSsI18TSug2oM=)
15. [symmetricfunctions.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFR6TfRoCndJ_azgQ9UzZInXD8Bz0-hOqVmAyrOvvbqy4jf47wXg3_oEszjAlroE-9rLUuecmAk7dbezEYYjDcYUMaIeOL5MaoVAZ2qYNacciyWjIkB9a1Qn192i5kyEwTI2uK5SBDpi_PWNUci6u1IOu8O)
16. [washu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvfWqB4c0Nk3FC65wr4o-VRNlEGXuVul2wydNxLdN6b80NaYqxLqnmWKOry8JXB9o_wpZHguSTSzq9X11daGSUjLkkNiSj8aVRoqnNpccOBiv3AJfS37FAyI4LV-060Deukcl6lIiw68qXc0m8W6g97FmI4UxabMYdpNEb75i2yiETVt1n4LOaziHAYl3_jjLwYc813HQbi4KUi9pFiXcR5n73GG4l8A4=)
17. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzNh3uRLRg37O1wCdDzax6kAxKB8yTvcZHxFKA_nrHMl_334HIrnFij13KZQ5-uGZTbDSo6Zip828k6bAPoUAQ0hhFMt_woeqNjm-BqYT6Z5uRRHGHCWobGOIkuGiGBp6-hGSBfDON3mQtsRZcbMcv)
18. [wustl.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHksn4skMn726EZWNYza8TGitmnVFbUO4Cl8W1xZgzrAlu0FPGRc0_GOJblZnGopXa2NdApLp3E508FR-ygBBaAIxIiesdywxfYIheywQd6PeM8-BImuvIet5kFmKDbkUiV8ZCQNDuLg_h7t2yhMumLq_r32smA2bmfM_E0tCu1f-Ie7xD8MdSZ3JAh_2Uzf6_edwoQ8XRYmouBW-p7eOTrrZkbjKkvTQWmuZrjGZqxx80=)
19. [symmetricfunctions.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDjTWRR6thj-74RyQvK3pnqhIWpOZRbaZk0yvSaMVkHdp0DY_KAlH9Ow7us8YHrEOmIefS2cNktRwxOqMtty6abWFGv4SAb1djzroszOrKpPo6o_A3rFHYxlMc38FG5BE7fH2w)
20. [kent.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8YuezUoasadR5k2LOIxUdxfleMxAM6lWD263dFHIRE6f889RNPk37bwkk6sXC4CY4PZrYwzkYgnrdbk4Fa4eaR7u1asZrCId_NcDekGyr4X9Qra6ERLevs1DjDHO5Z36wa2ri9N_ZvRi2HzvTloPIwDZ464wt)
21. [rhul.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFR6oTsxS7U3IXanSP3edgvVHoTpgJRb3CBSfM03_gWgysHQh7ULzQSH6SdWEbjeQFHeNETNa1QMIq-mnAjHSHTLe_M_jzDFFe8nIGggVps_EZhejpNxV0iZhpD6A5LZjvL-P_7zvuzAX9K8X08GgfdXQ==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0gqoT01QHppEqIA_zEs86_0JZKnEalG1Rv650VHqBhuhEltVi_w3dtkGJtKJfxmoPqfOF_8IS9FIgaYc0GFb8qhMBHSZwwJmHrUqfyWsQ2fUV-Sxg)
23. [symmetricfunctions.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpv2wK8FJm3fiP5jfZuIWYDPjk5dmHlLboHfx8zau2ZPXcCwU07gP_hYaeWqkSge1jKA4eGgDXszjuqxq4L0VQFZHeucs63Cav8T1Bh3FC5B4p5oU2b-zj5FitPweIEJBH7fNUxPqGqemvQGU_bw0m)
24. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNp8-OLdZNY9GnXEmKa9sRDgxs_q6Han0F3MJMLqmVV37-2qVZc9Uu-9AeYPybeDNUZ71E-dntLQU1FH5tppb-0hcMDVSs7mlNM1s5ajQE0UdK5xGniIq1Fgh5mw18UbYY9xKNh2QH5ROh_W24o6gSjmnuR4rOYaBpep-2lEWlSeADb-4YgMcDuf10JSXO6VDFC_CYCnhnAXw7jpximg==)
25. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwIkZt_HvaQkNaz50T8rlixlJFIPEMZYO5vE6ToiqTRbK4DLGxeh4bORGLGP-81g3GXHfRYT_ngUTjoG64h860NxUUYuqwacPGj9dSV_PJ31qdJvsS-KXi1gEK4VTe1bu-fw==)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFs6NFO_WwNd0BRd1WR-ntTfkP9SK5xTUJ8ynTCP4m2nFqTsDRJoCDCExeJpCA9D8aDfSrL3-XQ0ZoAp1xMVSxZb6XWzYaTgIHaPI-TVSFifARE5DAzZBj8QtQI23JdMbnkMVh3iBcOVZpibeoLwbi-O83pMX-cC8MX8F8QMdM8p9AgZwwi5l8T6gTpRl7Qoos8pYn7ddYc63dM6JkJl2PkhElvL56EnA==)
27. [msu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_FPLM5AS7F3VoBgPuDtWo3-VXW-bepjkA-DTmu_9_-s22iY-n51Vh21LREkO5nzWX-3zVut4XR9tOR715mSllp2sGmeG3FRWeLtnLMvoJpRkX3eQ0QFNU5Wd4F_MuAf9Ypx0VJLq4ptvHt0jNKDiLgI9_LWu4CvlR1vutdrPF0OxQrQ==)
28. [ubc.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFduR9lBb2IQoJNFKnDy1YQ16WyT0PuFk_VtiQVubxriSM8T2mIe0ghjOe7tTZbvjGbjqaBnrhPmZ68xwuZ4Sggqyq13RZgO2Okm7NSt5sMcQOnffX4fpt0a0S-ND9Q1h1qYrigrfKDVvOwuDOT0AsC)
29. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJTxoq4BgLfnxwZnQC7_ksDOfg9k7vwiGD8WrCz9N4WwU94vhgsT5kwxlufPMRs75zvQYdoowUfdeVt5dldWktoxZJeDzcWARoy8aXGTdGT11zD11DS5hZ9oiMYVTcfzXQNraH2qUQ8iEE2vmqykWYH8qdqteci4jw_gB4uYB5biASG9IkcSM9IchQszD2Cdg=)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxSGXLrCsfSKzDJI4CwmZrW52lB4BwRjyzg4jAsz28KuaQZT4BjT78xEFWDzJtCBEcHfsCklbiMe_fea9F0yRROFQMGgq-YJm4eY4ixKhs0rnY5sCp)
31. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqNmF6zHx2Hth3mjGD4IsVYCYC6zZSEjVpoBP72eQVQsFztn_xx3BMY9NUPPO6qjjyAD9NKC9v0CFa6pc002IAIQxDhn84SZ8hKoqVxtzPBOzurJ_0f1x8T_pew-60FSdCRM0subQX08whQuJlMtzI)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkjRIgj9MvFnkbV7eEu_bECB29wO_wOfeM6dTusy01KqXJwhzQBel0Hm06vp8lg0cXTvfj9dOJMFUPP0a8AUr8rFFHJnTLTlF1oVp_z8jSeU1s7bU1Nr0L)

