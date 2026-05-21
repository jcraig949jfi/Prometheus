# T#39 Maximal symmetric (Waring) rank for generic forms

**Pythia queue id:** 84
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd6dzBQYXBXT0tKbU8xTWtQcTZmRC1RNBIXencwUGFwV09LSm1PMU1rUHE2ZkQtUTQ
**Elapsed:** 313s
**Completed at:** 2026-05-21T13:56:25.532401+00:00

---

# Maximal Symmetric (Waring) Rank for Generic Forms

### Leading Paragraph

*   **Definition of Waring Rank**: The symmetric rank, commonly known as the Waring rank, of a homogeneous polynomial (or symmetric tensor) is the minimum number of summands required to express it as a sum of powers of linear forms.
*   **The Generic Rank**: The "generic rank" refers to the Waring rank of a general form of a given degree and number of variables. The celebrated Alexander-Hirschowitz theorem completely classifies the generic rank, translating the algebraic problem into the geometric study of secant varieties of Veronese embeddings.
*   **The Maximal Rank Problem**: While the generic rank is well understood, determining the *maximal* Waring rank for forms of a given degree and dimension remains largely an open problem. 
*   **The Blekherman-Teitler Bound**: A breakthrough in upper bounds dictates that the maximal rank is at most twice the generic rank ($r_{max} \le 2r_{gen}$). This bound applies across complex and real varieties, as well as to general tensor ranks.
*   **Monomials and High-Rank Forms**: Finding explicit polynomials with a rank strictly greater than the generic rank is notoriously difficult. Monomials in three variables can exceed the generic rank, but surprisingly, in four or more variables, all monomials have a rank strictly less than the generic rank. 

***

## 1. Introduction to Symmetric Tensors and the Waring Problem

Tensors are ubiquitous in mathematics, applied sciences, engineering, signal processing, and machine learning, largely due to the importance of determining the shortest additive decomposition of a vector into simple, rank-one vectors [cite: 1, 2]. For a general tensor, this is referred to as the tensor rank. In the highly symmetric setting—specifically when dealing with complex or real numbers (characteristic zero)—symmetric tensors are naturally identified with homogeneous polynomials [cite: 3, 4]. 

### 1.1 The Classical vs. Polynomial Waring Problem
The study of additive decompositions of polynomials draws its namesake from the classical Waring problem in number theory. In 1770, Edward Waring conjectured that for every integer $d \ge 2$, there exists a number $g(d)$ such that every sufficiently large natural number can be expressed as the sum of at most $g(d)$ positive $d$-th powers [cite: 5]. David Hilbert subsequently proved this conjecture in 1909. While the classical Waring problem seeks to determine the minimum number of summands needed to decompose integers, its polynomial analogue translates to finding the minimum number of $d$-th powers of linear forms needed to represent a homogeneous polynomial [cite: 3, 6]. 

For a homogeneous polynomial $F$ of degree $d$ in $n$ variables over an algebraically closed field of characteristic zero (such as $\mathbb{C}$), a Waring decomposition is an expression of the form:
\[ F = c_1 L_1^d + c_2 L_2^d + \dots + c_r L_r^d \]
where the $L_i$ are linear forms and $c_i$ are scalars. The minimal length $r$ of such a decomposition is called the **Waring rank** (or symmetric rank) of $F$, denoted as $r(F)$ or $rk(F)$ [cite: 7, 8, 9]. 

### 1.2 The "Little" and "Big" Waring Problems
In algebraic geometry and multilinear algebra, the Waring problem for polynomials is historically divided into two main categories:
1.  **The Little Waring Problem**: Identifying the minimal number $s$ such that *every* arbitrary homogeneous polynomial of degree $d$ in $n$ variables can be written as a sum of at most $s$ powers of linear forms [cite: 3, 5]. This corresponds to finding the *maximal* Waring rank.
2.  **The Big Waring Problem**: Determining the number of linear forms required to express a *generic* (or general) form of degree $d$ in $n$ variables. This is equivalent to finding the generic rank [cite: 3, 5].

Determining the exact Waring rank for a given specific polynomial is a highly non-trivial computational task. In fact, computing the Waring rank of a given form is an NP-hard problem [cite: 6, 10]. Because of this difficulty, mathematicians have relied heavily on algebraic geometry to study the generic rank and to establish theoretical bounds on the maximal rank.

## 2. Geometric Interpretation: Secant Varieties and Veronese Embeddings

To understand generic and maximal ranks, the polynomial Waring problem is mapped to the geometry of projective varieties. Evaluating the rank of a symmetric tensor is geometrically equivalent to finding the minimum number $k$ such that the tensor belongs to the $k$-secant variety of a Veronese variety [cite: 2, 11].

### 2.1 The Veronese Variety and Secant Varieties
Let $S_d(V)$ denote the space of homogeneous polynomials of degree $d$ on a vector space $V$ of dimension $n+1$. The set of all $d$-th powers of linear forms defines a projective variety known as the Veronese variety, denoted $X_{n,d} = \nu_d(\mathbb{P}^n) \subset \mathbb{P}(\text{Sym}^d V)$ [cite: 11, 12]. 

The $s$-th secant variety, denoted $\sigma_s(X_{n,d})$, is defined as the Zariski closure of the union of all linear spaces spanned by $s$ points on the Veronese variety [cite: 13, 14]. In terms of rank, $\sigma_s(X_{n,d})$ is the Zariski closure of the set of forms having Waring rank at most $s$ [cite: 1]. Since the Zariski closure introduces limits, the secant variety contains polynomials that can be approximated by forms of rank $s$, giving rise to the concept of *border rank* (discussed in later sections).

### 2.2 Generic Rank and Expected Dimension
A generic form of degree $d$ in $n+1$ variables has a rank equal to the smallest integer $s$ such that the $s$-th secant variety $\sigma_s(X_{n,d})$ fills the entire ambient projective space $\mathbb{P}(\text{Sym}^d V)$ [cite: 5, 13, 14]. The expected dimension of this secant variety is bounded by the dimension of the ambient space and the degrees of freedom of choosing $s$ points on an $n$-dimensional variety. Thus, the expected dimension is:
\[ \min \left\{ \binom{n+d}{d} - 1, s(n+1) - 1 \right\} \]
where $\binom{n+d}{d}$ is the dimension of the space of degree $d$ polynomials in $n+1$ variables [cite: 5, 15].

Consequently, the generic Waring rank, denoted $r_{gen}(n,d)$, is expected to be:
\[ r_{gen}(n,d) = \left\lceil \frac{1}{n+1} \binom{n+d}{d} \right\rceil \]
When the actual dimension of the secant variety is strictly less than the expected dimension, the variety is said to be *defective* [cite: 5, 12]. 

## 3. The Alexander-Hirschowitz Theorem

The "Big Waring Problem" regarding the generic rank was completely resolved by the celebrated Alexander-Hirschowitz Theorem, formulated and proven in 1995 [cite: 5, 16]. This theorem classifies the dimensions of secant varieties to Veronese varieties, thereby establishing the generic rank for all degrees and variables, whilst providing a complete list of exceptional (defective) cases [cite: 11, 12].

### 3.1 Statement of the Theorem
The Alexander-Hirschowitz theorem states that for all but a finite list of known exceptions, the generic $1$-Waring rank of a degree-$d$ form in $n+1$ variables is exactly the expected (rounded-up) value:
\[ r_{gen}(n, d) = \left\lceil \frac{1}{n+1} \binom{n+d}{d} \right\rceil \]
This means that a general collection of double points in projective space imposes independent conditions on homogeneous polynomials of degree $d$, barring a few exceptions [cite: 12, 15, 16].

### 3.2 The Defective Cases
The theorem exhaustively identifies all cases where the actual secant variety dimension is smaller than expected. The defective cases for forms (using $N$ variables, where $N = n+1$) are [cite: 17]:
1.  **Quadrics ($d=2$)**: For any number of variables $N$, $r_{gen}(N, 2) = N$. The expected rank is typically lower, but quadratic forms correspond to symmetric matrices, and their generic rank is simply the dimension of the space [cite: 9, 17].
2.  **Plane Quartics ($N=3, d=4$)**: $r_{gen}(3, 4) = 6$ (Expected was 5) [cite: 9, 17].
3.  **Quaternary Quartics ($N=4, d=4$)**: $r_{gen}(4, 4) = 10$ (Expected was 9) [cite: 17].
4.  **Quinary Cubics ($N=5, d=3$)**: $r_{gen}(5, 3) = 7$ (Expected was 6) [cite: 17].
5.  **Quinary Quartics ($N=5, d=4$)**: $r_{gen}(5, 4) = 14$ (Expected was 12) [cite: 17].

In all exceptional cases (other than quadrics), the generic rank is precisely $1$ greater than the expected value [cite: 18]. The completion of this theorem by J. Alexander and A. Hirschowitz involved the use of Terracini's Lemma, which describes the generic tangent space to a secant variety, effectively reducing the geometric problem to computing dimensions of specific ideals in commutative algebra [cite: 15, 18, 19].

## 4. The Maximal Symmetric (Waring) Rank

While the generic rank $r_{gen}(n,d)$ tells us the rank of a "randomly chosen" or general polynomial, the problem of determining the absolute maximal Waring rank, $r_{max}(n,d)$, for the set of all homogeneous polynomials of degree $d$ in $n+1$ variables is substantially more difficult [cite: 20, 21]. The maximal rank represents the "Little Waring Problem" for polynomials and is currently unsolved in the general case [cite: 3, 21].

Because rank is not a semi-continuous property, the Zariski closure of the set of polynomials of a fixed rank $r$ can contain polynomials of rank strictly greater than $r$ [cite: 22]. This implies that there exist specialized or "degenerate" forms whose Waring rank strictly exceeds the generic rank.

### 4.1 Historical Upper Bounds
For a long time, the only trivial upper bound for the maximal rank of a form $F \in S_d(\mathbb{C}^n)$ was the dimension of the vector space itself. By choosing a basis consisting entirely of powers of linear forms, one can trivially deduce [cite: 6]:
\[ r_{max}(n, d) \le \binom{n+d-1}{n-1} \]
J.M. Landsberg and Z. Teitler improved this bound to [cite: 13]:
\[ r_{max}(n, d) \le \binom{n+d}{d} - n \]
This bound, however, is only strictly sharp for binary forms ($n=1$). Later work by Jelisiejew provided a slight improvement by subtracting $\binom{n+d-6}{n-3}$ [cite: 17]. Ballico and De Paris presented another complex upper bound, but these traditional bounds largely scale with the dimension of the ambient polynomial space, meaning they grow roughly like $O(d^{n-1})$, which is exceedingly loose [cite: 17, 22].

### 4.2 The Blekherman-Teitler Bound
A major advancement in understanding the maximal rank was established by G. Blekherman and Z. Teitler, who demonstrated that the maximum value of rank is at most twice the generic rank [cite: 1, 13, 14, 23]. 

**Theorem (Blekherman-Teitler)**: Let $X \subset \mathbb{P}^n$ be an irreducible nondegenerate variety over an algebraically closed field. Let $r_{gen}$ be the generic value of rank with respect to $X$. Then the maximum rank $r_{max}$ satisfies:
\[ r_{max} \le 2 r_{gen} \]
*Proof Sketch*: The proof relies on a remarkably elementary but powerful geometric observation. Every point in the ambient space can be represented as a sum of two general points. Since general points possess exactly the generic rank $r_{gen}$, the maximal rank of their sum is at most $r_{gen} + r_{gen} = 2r_{gen}$ [cite: 1, 4, 14]. 

This theorem applies not only to classical Waring rank (where $X$ is the Veronese variety) but also broadly to regular tensor rank (Segre variety) and antisymmetric rank (Grassmannians) [cite: 14]. Blekherman and Teitler also provided a slight refinement: if the Zariski closure of vectors of rank $r_{gen}-1$ forms a hypersurface, the bound improves to $r_{max} \le 2r_{gen} - 2$ [cite: 1, 14].

Despite being an elementary upper bound, $r_{max} \le 2r_{gen}$ is drastically better than previous dimensional bounds and remains the most robust general upper bound currently known for higher dimensions [cite: 1, 23]. For example, asymptotically, the maximum rank is constrained to the interval $[r_{gen}, 2r_{gen}]$ [cite: 9]. 

## 5. Specific Cases and Known Maximal Ranks

Determining the exact value of $r_{max}(n, d)$ or finding explicit families of polynomials that achieve the maximum rank has proven possible in only a handful of specific dimensional cases.

### 5.1 Binary Forms (Two Variables)
The classical case of binary forms ($n=2$ variables) was completely solved by J.J. Sylvester in 1851 [cite: 18, 19, 24]. Sylvester's Theorem relies on a classical algorithm using apolarity and Catalecticant matrices [cite: 10].

For a binary form of degree $d$, the generic rank is $\lceil (d+1)/2 \rceil$. The maximal Waring rank for a binary form of degree $d$ is exactly $d$ [cite: 9, 17, 19]. This maximum value is attained precisely on forms that can be factored as $L_1 L_2^{d-1}$, where $L_1$ and $L_2$ are linearly independent linear forms. A canonical example is the monomial $x y^{d-1}$, which has a Waring rank of $d$ [cite: 9, 17, 19, 23]. 

### 5.2 Ternary Forms (Three Variables)
For ternary forms, the exact maximal rank is known only for small degrees:
*   **Ternary Cubics ($N=3, d=3$)**: The generic rank is $r_{gen}(3,3) = 4$. The maximal rank is $r_{max}(3,3) = 5$ [cite: 9, 13, 17].
*   **Ternary Quartics ($N=3, d=4$)**: This is one of the Alexander-Hirschowitz exceptional cases. The generic rank is $r_{gen}(3,4) = 6$. The maximal rank is $r_{max}(3,4) = 7$ [cite: 9, 13, 17, 21].
*   **Ternary Quintics ($N=3, d=5$)**: Some explicit monomials provide a strict lower bound, but determining the exact maximal rank generally for higher degree ternary forms remains challenging, though it is known that $r_{max}(3, d) = d^2/4 + O(d)$ [cite: 25].

### 5.3 Quaternary Forms (Four Variables)
For four variables, specifically quaternary cubics ($N=4, d=3$), the generic rank is $r_{gen}(4,3) = 5$. The maximal rank is exactly $7$ [cite: 9]. For $N \ge 4$, forms that have a Waring rank strictly higher than the generic rank are exceptionally rare and mathematically "mysterious" [cite: 26]. 

## 6. Monomials and Forms of High Rank

A crucial avenue of research into finding forms with maximal rank involves computing the Waring rank of explicit families of polynomials, such as monomials and sums of coprime monomials [cite: 9]. 

### 6.1 The Waring Rank of Monomials
The Waring rank of monomials was definitively resolved by Carlini, Catalisano, and Geramita [cite: 9, 22, 24]. For a monomial $M = x_1^{a_1} x_2^{a_2} \dots x_n^{a_n}$, ordered such that $0 < a_1 \le a_2 \le \dots \le a_n$, the complex Waring rank is given by the elegant formula:
\[ r(M) = (a_2 + 1)(a_3 + 1) \dots (a_n + 1) = \prod_{i=2}^n (a_i + 1) \]
Notice that the smallest exponent $a_1$ does not factor into the multiplicative result [cite: 9, 22].

### 6.2 Monomials Exceeding the Generic Rank
Do monomials ever serve as examples of forms with a Waring rank strictly higher than the generic rank? The answer depends fundamentally on the number of variables.

Let $\bar{r}_{mon}(n, d)$ denote the maximum rank of a monomial in $n$ variables of degree $d$. 
*   **In 3 variables**: Carlini, Catalisano, and Geramita observed that for ternary forms, there are indeed monomials with a rank strictly greater than the generic rank. Specifically, $\bar{r}_{mon}(3,d) > r_{gen}(3,d)$ for all degrees $d \ge 5$ [cite: 9]. Asymptotically in $d$, the maximum rank of ternary monomials approaches $(3/2)$ times the generic rank, providing an infinite family of forms exceeding generic rank [cite: 17, 27]. For example, the monomial $x y^s z^s$ has rank $(s+1)^2$, while $x y^{s-1} z^s$ has rank $s(s+1)$ [cite: 2].
*   **In 4 or more variables**: A surprising transition occurs in higher dimensions. For $n \ge 4$, researchers proved that *all* monomials have a Waring rank strictly less than the generic rank [cite: 9, 17, 27]. Asymptotically, the maximum rank of monomials in $n$ variables is $d^{n-1} / (n-1)^{n-1}$, whereas the generic rank grows as $d^{n-1} / n!$. Because $(n-1)^{n-1} > n!$ for all $n \ge 4$, the maximal rank of monomials falls far below the generic rank for sufficiently large $d$ [cite: 17, 27]. 

Thus, in four or more variables, there are absolutely no monomials with higher than generic rank [cite: 9, 27]. Monomials fail to provide examples of high-rank forms in higher dimensions.

### 6.3 Sums of Coprime Monomials
Since single monomials in $n \ge 4$ variables do not exceed generic rank, researchers analyzed sums of pairwise coprime monomials. However, similar restrictive bounds apply. With exactly three exceptions (up to variable reordering), every sum of pairwise coprime monomials in $n \ge 4$ variables of degree $d \ge 3$ has a rank strictly less than the generic rank [cite: 9, 27]. Consequently, researchers must search elsewhere (e.g., reducible forms, specific algebraic surfaces) for polynomials that saturate the Blekherman-Teitler upper bound.

## 7. Real vs. Complex Waring Rank

The discussions above primarily assume an algebraically closed base field, namely the complex numbers $\mathbb{C}$. When considering symmetric tensors over the real numbers $\mathbb{R}$, the geometry and the definition of generic rank change significantly [cite: 23]. 

### 7.1 Typical Ranks
Over the complex numbers, a "generic" property holds on a Zariski open, dense subset of the space, meaning there is a single, unique generic rank. Over the real numbers, a Zariski open set is not necessarily dense in the Euclidean topology. Consequently, the space of real homogeneous polynomials is partitioned into several semi-algebraic sets with non-empty interiors [cite: 1, 23]. 

The ranks associated with these positive-volume sets are called **typical ranks** [cite: 1, 28]. A single real tensor space can possess multiple typical ranks. For example, the real rank of the monomial $x^2 y^2$ is 4, whereas its complex rank is 3 [cite: 8].

### 7.2 The Real Blekherman-Teitler Bound
Blekherman and Teitler extended their maximal rank bounds to the real numbers. They established that the minimum typical real rank is precisely equal to the complex generic rank [cite: 1, 4]. Furthermore, they proved the following robust limit on the maximum real rank:

**Theorem (Real Maximal Rank)**: Let $X \subset \mathbb{R}\mathbb{P}^n$ be an irreducible nondegenerate real projective variety. Let $r_0$ be the minimal typical rank with respect to $X$, and let $r_{max}$ be the maximum real rank. Then:
\[ r_{max} \le 2r_0 \]
Because $r_0$ equals the complex generic rank, the maximum real rank is also bounded by twice the complex generic rank [cite: 1, 14]. This finding provides one of the strongest known bounds on maximal real tensor rank, a metric notoriously harder to evaluate than its complex counterpart. Furthermore, it is known that any integer between the lowest typical rank and the highest typical rank actually occurs as a typical rank for real varieties [cite: 4].

## 8. Apolarity and Computational Aspects

Understanding how specific Waring decompositions are constructed relies heavily on **Apolarity Theory** and the concept of the apolar ideal [cite: 3, 10, 24, 29].

### 8.1 The Apolar Ideal and Apolarity Lemma
Symmetric tensors (polynomials) naturally act on dual spaces. If $S = \mathbb{C}[x_0, \dots, x_n]$ is the polynomial ring, we define a dual ring of differential operators $T = \mathbb{C}[\partial_0, \dots, \partial_n]$. The polynomial ring acts on itself via differentiation. For a homogeneous polynomial $F \in S$, its **apolar ideal** $F^\perp \subset T$ (also called Macaulay's inverse system) is defined as the set of all differential operators that annihilate $F$:
\[ F^\perp = \{ G \in T \mid G(F) = 0 \} \]
[cite: 21, 30].

The fundamental bridge between apolar ideals and the Waring rank is the **Apolarity Lemma** [cite: 10, 30]. The lemma states that a homogeneous form $F$ admits a Waring decomposition $F = \sum_{i=1}^r c_i L_i^d$ if and only if the apolar ideal $F^\perp$ contains the vanishing ideal of a set of $r$ reduced points in projective space $\mathbb{P}^n$, where the coordinates of the points correspond to the linear forms $L_i$ [cite: 10, 29, 30]. 

### 8.2 Waring Loci
The **Waring locus** of a polynomial $F$ is the collection of linear forms that can participate in a minimal Waring decomposition of $F$ [cite: 24, 26, 29]. In other words, if a linear form belongs to the Waring locus, it can be "subtracted" to decrease the rank of $F$. 
*   If the Waring locus is dense in the space of linear forms, a randomly chosen linear form will successfully reduce the rank. This phenomenon generally occurs for forms with a rank *strictly higher* than the generic rank [cite: 24, 29]. 
*   If the Waring locus is restricted to a proper subvariety, finding a minimal decomposition requires solving constrained algebraic systems, corresponding to selecting specific eigenvectors or critical rank-one approximations [cite: 7, 24, 29]. 

Algorithms utilizing the apolarity lemma to compute minimal Waring decompositions have been effectively implemented for binary forms (Sylvester's algorithm) and low-rank tensors (via software like Macaulay2) [cite: 10, 24, 30]. However, evaluating the precise rank for an arbitrary input polynomial continues to remain NP-hard [cite: 6, 10].

## 9. Advanced Concepts: Border Rank and Simultaneous Rank

The complexities of Waring rank are further illuminated by two prominent extensions: Border Rank and Simultaneous Waring Rank.

### 9.1 Border Waring Rank
As noted, the standard Waring rank is not lower semi-continuous. A polynomial can possess a rank $r$, but be arbitrarily closely approximated by a sequence of polynomials having a strictly lower rank [cite: 6, 22, 31]. 

The **border Waring rank** of $F$, denoted $\underline{r}(F)$ or $R(F)$, is the minimal integer $r$ such that $F$ is the limit of a sequence of polynomials each having Waring rank at most $r$ [cite: 6, 22, 31]. Equivalently, $F$ lies in the Zariski closure of the $r$-th secant variety $\sigma_r(X)$ [cite: 22]. Border rank heavily bounds and informs true rank; if $F$ has border rank $r$, then tensor flattenings (creating matrices from the tensor) will have a matrix rank bounded by $r$ [cite: 22].

Debordering bounds—which restrict how much larger the true Waring rank can be compared to the border rank—show that if a polynomial of degree $d$ has border rank $r$, its true Waring rank is bounded linearly in terms of the degree for fixed border rank [cite: 6, 31].

### 9.2 Simultaneous Waring Rank
The concept of Waring rank can be expanded to collections of polynomials. Given a family of homogeneous polynomials $F_1, \dots, F_k$ of degree $d$, the **simultaneous Waring rank** is the minimal number of linear forms required to simultaneously write *every* form in the family as a linear combination of their $d$-th powers [cite: 8, 30, 32]. 

The generic simultaneous rank is connected to defective Segre-Veronese varieties [cite: 32]. Explicit combinatorial formulas, often resembling inclusion-exclusion principles, have been derived for the complex simultaneous Waring rank of specialized sets of monomials [cite: 30].

## 10. Conclusion and Open Directions

The problem of establishing the maximal symmetric (Waring) rank for generic forms sits at the intersection of classical algebraic geometry, multilinear algebra, and modern computational complexity. While the generic rank is completely mapped via the Alexander-Hirschowitz Theorem [cite: 5, 15, 16], our understanding of the maximal rank remains framed by the broad Blekherman-Teitler limit ($r_{max} \le 2r_{gen}$) [cite: 1, 14, 23]. 

Explicit polynomial families achieving maximal ranks are scarce, especially as dimensions scale. Monomials in four or more variables demonstrably fail to exceed the generic rank [cite: 9, 17], making the identification of highly degenerate, high-rank forms an active frontier. Furthermore, connections between symmetric rank (Waring rank) and general tensor rank—captured by Comon's Conjecture, which posits that for a symmetric tensor, its symmetric rank equals its general tensor rank—ensure that breakthroughs in polynomial decomposition continue to exert a profound impact across applied mathematics and engineering [cite: 3, 4, 10].

**Sources:**
1. [su.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSBiNSS8zVr3w3i_ZHNbvxJgrx4uCu0mVernmdKAx8iBkNfHx02O_nk2aZxlqEByMHwyH_eC3xuXl89HiR2iPsLgp8bxfsfBM03FPJ5aQ2fhdl8PIGJMrNYicP_bm6mcxWm6EZte4vwRDFhfaC8T1HkQSSeEtZUM_7c5c=)
2. [mdpi-res.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEF6i_PDimswO8zwcfjd0HNtRyMtPxsTwcoVd1bHD7s2Z0iW1aM18PVBE6vhz3mlCKjTNmak-PF_yCwZ_4-foGS1Nh8nDnjtrmwvDCNhUOSkIT0JwjGlUfcwRstohE4wshzLINayWFgoRyxSjNaXPRI9ox64sswzrZ9zWntoVcQP48XdDxfr-FvaUw=)
3. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjS6MhfpUYnLlvv4ArcRqFbjZlYqfQmCuNOrD5d6rOIPaOObmsWG7MSZ4FCwl_86bXSOonmdXk545EeAO0M99UWRaWXYTEO2b_8kt8_ODWVbP9kNWkIwbn2L8VAFA=)
4. [polito.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEOl5bTlajSTCwfKMbSYEKmQgezx9LW8faTnAKsqW0GgHmLHQrwzaNhlAk2rQvYmGrGy1Zxq-u5miAFIBTg8Y7RIRo2AJ5yVlbx55w5mOlizN1KOBZ7WItILoTty5FOF5GVtSF_96ow9SxxoIRAwTDXfqC2nrY61CpFSZtehNXoErQNLVuWexoovlw3WKOSM3lRDuQ0y40dNKO0vZJrm7ozm_89Lm2LRGgKWA0I5i_RtLmHWY=)
5. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRAjNFJLaJMt1lJELdjQaVdb0HiAqTfnKbbmIa7fF9ECRY4Vbs1mWeYCI84LKLCoa7Qg1C9D7urXLBEXp-Gyxzv_MT_Qgb6UQs8_BZTCHyS1CbLs-F59SLM_rspy0=)
6. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeM1hT5C4b8qcUo--ronN8jYR5VBEfMPQGsD-tApfuRMlYb-Z4Nujruj_oD1HE9BJEQx_fmZpiwnJNbZRFyZAx6HrFdCPyx28z6nzDDxGXo3_RDhV3M7L_XwnFd0vR_a3XQ8bgrFZlT3sAlb_K6tKl3fe8gfORjdpE3UUboLXxe__cQvG3MQ_scf6v)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUhP5I-9zMgzoLlWQkQwgznBsp9lKOXLt0q_uCrLb9rXvshgaEOj8xf0H9nJtozXPpJQL6h4f-Sw0g4MW9kNQfgLP3gvClIQDcTgZHZx9ZpjY1IAvbn9yGew==)
8. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9rBXNAAIqGqoWkcryBU7uwY-Fb-t_A__GRL-WSyXBFdHk_c_yE0lNuDiZ6eLxKuIFGu-SZNj38tFHlSgG_TNhX-GzALClpHNKf166WbXucDhp9KaWI6Pe6ud3W3Bw8X7v9XIFAwSWYvqawJsAL7I1rlYu6Ph3)
9. [boisestate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETIoUBHQ_mu3IDKsjhJ3wZH0HEDIkvoFZhvf4iBl8kM8jj3ndODGZQgEaTHB0XLpEsh7mjPq6Q92ZY3T313XVNVewWBb5Tdewu04uJfXVmcNQ6emdHbrCxduz2PT09s5-rwW7iKHhQUmio4i7tRORlDxpKn3zRtTNJ1Us_6s8eJJqg-H2il_JOw-EJRZ8RVA==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdSoTb8yJXbjgTYKnA-uy4KjdGitcQ_ozw6gBRfTKRIRye_eV3id6xL0kyw3G1IQUqnkhfTJpQj6PSEXwOwasgYJXAweSYBQmjqp76TX0ju8JMNJInEQ==)
11. [unitn.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQZQIBvDdJ73W7w7IAeo8SDOuOUp3bbGx6Dgn0CmQViaQD_y0BFSPTxE_REl0SZCB6YgrZkdrfqvk3vtNk8gTbNhhBi5I-hGCyiSJtLR84mqB7ON9UAyPI351Q4xsN7lJSps6BM6eMg46h8ZM7rhQc42bEvwht3vOuSt9dwrHoTh5Ef_DUkHmhke6iA-907VJ7Ag==)
12. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfeLYe7peHxPZ1wcXA94MZntzpKvDXuWPGRnTJytbrULRqP-h4KkZfFIgy6s6hDfpBXGrc9Xy_ygBgC2eIxBL-Md7cCmrBfUjLdsKql28RrHih-lKR3YevN7if)
13. [unict.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRT_kbe0AeUgKm8QBYcnWHvtV5OfX1KijKtwuh_rsZLSXV-36j0E_El8WF3yWwevit2407jmt_LzPjicOss1v1DDoJBTexvZebShHkLdOxFTC13G8yew3bYt85QvLe2scwqOT2xF_81LdrvQL2hSl76RO-dqm008xKs0hPoMP4uFgqT5rFJd7_tgfk)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQeS1QEIFnAtVlWBgLA-fygNR1EkB7dOGn0cp1x7QcQVWau7dpC07waJ2s5XTqwfw7V0mu7d4HsuLJyODHJ8YxqdbHLHxh0uLAwhoj1X3VlBiXGRfNchmMOYvGWw7q_XPPkjfYvFdU-LPL44OWar38zhbK43GepeBQ2YoXMph5fWUUNSHK8f7mLh36t2s=)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuquw90uuAvQ1a1ELSluztbKPehfRE2_jj7srQLgSVntgBt7GPrtZwGWZhnbm552u5lPTYrWPx6MqI5XHaFYLwQxMUi9PJKon64nkHI7tqspAhlQZOmjSqDSSppKNg9Mv-pv-uhnmFO9kJ5r2MljZUqQlCcPCKdly_uzt9L4CJYKrdIB5l2rrOwyjMJCeOIB7rdC17EVAYqnyBcwVrzvAbtiFBLULh36uzC7B0uwCUtyd96cwhwggSMTz9rx5WUAZe7NiXDN9sAgGOJhBwBJGV286TyVsdStNfLCHPoz_-EUkjJqwCRJR2fXx25bw5vT2Ci1ebMUrzFFAeH1ynBb_GATl-LsQv-Ra6)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUwK9FbABnixUamD5iB5NXwndCvW-aXFkPATAhWAFbqTxVJPzupYuK27JHi47MaEA9vppdcNQgehtl77p8pRfyH5M22iRfXRtM2jygIhZN_3qxRiKSIhkLUq5qXlFSD5h46bytMOxEHG-fZt0MdgxkzZv5sYPIa4t2OiRx313UMI1N4wb-tB8r_Rr4Dao=)
17. [su.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELLdy6vldTVAuE5CnrhzioJ7v0BTE1ypBcG_ZjEfG7voM-xW_lnD1IfiK2O0ud0Xndt9lNvPjZTU_ig2R4KA4SqXfTRhmlODiCl2xmUJvJQVQq9hIzTmsqMU2K_0fphlbdvVtEnT260OQRY0dNpLS0Vw==)
18. [su.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHORZ5Nld6kYuz-pHkp3rGbUrHq4eUEAXFSOYeYxaxt0QWE1DAQ7xJ5KQMqAL8INUD4g03IVqvHRhlMkHsAHqJC3TWHL6_wXNR8G4IU-jgbUs569WSs_15a3AH6-OLVEJqxItZylQQR3DFTWyIlnO8j6xztKLQ=)
19. [su.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYGWWtlWj1O3gWXSHkdyQzgfFdlJqcIX-PZhvSo_WshqLOd4hCm6JSnMoFDwkAhVm3HgUVdhMZMyn4HI8DNKmeNol38yq6v7UkH0Ros5DslS3ngYpJ5s67AYp6tsobDAuS-FWiNlLg-iqexA9g)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVGUrGYKvtzXJqBqfebdH9BqRN4XW_D9fblz_r-sxqqw5G4Q6cwoplwG5xGtqh9lA6zs0sDx2G4hpXjRutVzsup9YcKln2rkDZih0xWeWxaPCFoZnW)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFV0Icucf9mjn-ijeQez01CXNswjHHm4r-NxD9-bOfan0fJHV_nku0zyGv2lCjdEQ2h4Wlk_kD_V3OP-v1zpefgNZriglxCRDzpXBw5eteBR8cya4nv-Xlejzlr68187TmL4BlniXD01UVrWAXykCZffUZNkhhyEN1nOqEfKXNhj8fGIAJf3YlpkYAr_muHTMFw_R0-ck=)
22. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtHovaiaYhBKUSWl5H1EcZRyorAx83cgBjD9Da3fKzdiHi72yTA6Fnl-tBe_iSmMrfLtk4O-l9GUtNqNhZWTY-rh1nDSMm147b9kvPpKtGbww231TvxZSsujqhQB_7GIunbcvu0PaONeDMJyYE5fr-rcKMFA==)
23. [stonybrook.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzJbOy9zZXJSH79aS5rFdKfJrVgO37ZiJ3RfTs6_Nh6OddlxqcZVeqC-72dAAdnT88mfXl6nSbft1ZXv85l29a_KVvet9FljnU-W54SMWlyuH9xbA-7q6c7U7KXgOZp6wOg-z-MzzBtcR5cfpbZvOhWNjDFFT8)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuiPAPa_teHO90JIjxvnjBXlB-axfvviYuY7_YtvkytD6Tpx19gBwnS5Duzdk0pqTtzgJRKe6gZaC7kd_Wgij4SiECEQwUzlhdOfIrOgiGy3ZDIAmPXA==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF67tw4YHuruF3Cm4TxF_zVs4A-cEQLzPI1jvOVTR3_ETidOEZTGJKRQ9is0U8014jnBcKlWV9omUhKFyn_qSiZp06xRbeyXjqupdNcXDPvK0bRmwv3yQ==)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOx6D2uQpYl433q2fKkX-xOt0iailjckSRCxuLE5bUfPWzfurBbuzlzGfNHBIHIiIPuzM0-X4XF0yK6o45u36dnxAYmCV7pVaPOK5q43dVmIYVAyExOTqHMg28TRfKS2R8MRqv4HhN9WJ-tJKtmW_dnmtHJ56T58SsOoyGhYz176JCPu4K1meLbF1jw8ar9mRriDu-yifICHGmFzUPYRoApyl2aIWzgrIxR-4=)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhQu3IyXdPX0cfZHecausVLqdQUgk8MSfU9ieGBr2XL_YWvLP3U4pP58UJr7heJrEbb6Y8D5NONP82bzK1Bnpf8dy4lrnD5rHV6aZUCdaNXZ5rJvdb)
28. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGskLmRwkmFvwlxwTqHIYWxctpYHqRY9PWCJj6bYqY9DY9aes9TJND9F9L4Q1R-uPAzHk4TaTW7yh1SDClCx3ydvfRi87d-oyPvCp1ZNHcLCEsjy9_sstcbbpx)
29. [unitn.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8rmqavqrslfg0dZV8Tzjr4Ocrm_a-s5R0yyABtvNjg3owFDvwSswGsbwg20SM9k9Kh7O7jexuuScUtZBGRGv_8t2ImMnBrZgkK6nTQcpJTQ7KK-Tx9wRKDAkclgUhVd8nXsbadnNLMV2ulA5T9o_A2Ew6w5A-0HnmIbJR3FDf6UnT8v3o_A==)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGynwK7aCP0AvAi5AC3wQ6pEaeVR_g-ZcZILoVhgN5_sNCY-P-Q2l5zyCofH413ZPv2QPTfmg5ET3SYaq3SGVS0zPpsxL7GyiKz7w-tDbKEqTOcRD78Q==)
31. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPfammc7QTjdU38ngzge4TyK7hUgLuXKoEOwFqgbaeGMuKGw18NHgE9JFAiBrReWPl7RNba2Bes18DCkAuV1YM-zYmI5XQ-gQi0evDmlCe-LsAdPYDe24I20gTN6yOFcZEPhUTlf1YyG9nWUsny09WWYrkE6PJELEzH9dTYygpY9Fbj6vwPa2QWVAAXV21yz5HKSXRni1-yxpBr5t5CynIhjlyBsGQ)
32. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErCfTP1QGdGPrCg6UBU7I0LiXi4ERU56fwwrfjIf2k2OOxGolSBBHulIEhl4s-4xzjhBsBc4kSRm1bjBf9bLxMafSH7WkufgGw69hOp8m2y48c5TxrrcfSfCBSGijiJaB93dzYIGqDp0rE8dHL728aUR8D7HA5_lhNzDgBB45bAUMMcID1Yq2QlSPr0E4uoIKdzYfpzRZj5xyve9QF5zWHG6GzHDEwJhYjb1vYJPLszlxFhe_KwnzBjuOyycLaNVHFi08_N3wg9_MB3xtQbR7oGzTzx9YAR5r4Okr4)

