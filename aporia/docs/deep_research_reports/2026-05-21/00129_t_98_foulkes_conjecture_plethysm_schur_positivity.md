# T#98 Foulkes conjecture (plethysm Schur-positivity)

**Pythia queue id:** 129
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChZTeWtQYXFDQ0NQMnFzT0lQdGJTemVBEhZTeWtQYXFDQ0NQMnFzT0lQdGJTemVB
**Elapsed:** 315s
**Completed at:** 2026-05-21T15:53:43.423570+00:00

---

# T#98 Foulkes Conjecture (Plethysm Schur-Positivity): A Comprehensive Academic Report

**Key Points:**
- The Foulkes Conjecture is a prominent and long-standing open problem in algebraic combinatorics and the representation theory of groups.
- It posits that the difference of the plethysms of complete homogeneous symmetric functions, $h_b[h_a] - h_a[h_b]$, is a Schur-positive symmetric function whenever $a \leq b$.
- In the language of representation theory, this translates to the assertion that every irreducible representation of the general linear group $GL(V)$ appears with a multiplicity in the module $Sym^a(Sym^b(V))$ that is less than or equal to its multiplicity in $Sym^b(Sym^a(V))$.
- The conjecture has been definitively proven for small base cases ($a \leq 5$) and asymptotically when $b$ is significantly larger than $a$, but it remains unproven in full generality.
- Advanced generalizations, such as Vessenes' generalized conjecture and Bergeron's $q$- and $q,t$-analogs, continue to be actively researched, alongside connections to algebraic geometry and partition algebras.

**Introduction for the Lay Reader**
Mathematics often involves studying abstract spaces and the symmetries that act upon them. When we have a collection of objects (like a set of variables), we can look at polynomials built from these variables. "Symmetric functions" are a special class of polynomials that remain completely unchanged no matter how we shuffle the variables around. 

One operation we can perform on these symmetric functions is called "plethysm"—essentially, substituting one symmetric function into another. The Foulkes Conjecture, named after H.O. Foulkes who proposed it in 1950, makes a specific claim about the plethysm of certain basic symmetric functions. It suggests that if we evaluate the plethysm in one order and subtract the plethysm evaluated in the reverse order, the resulting expression is "Schur-positive." In mathematical terms, Schur-positivity means that the result can be broken down into fundamental building blocks (called Schur functions) such that all the coefficients are positive numbers or zero. This implies the existence of a deep, underlying structural relationship. While mathematicians have proven this is true for small numbers using massive computer calculations, and for certain extreme cases using advanced geometry, a universal proof for all numbers remains one of the holy grails of modern algebraic combinatorics.

---

## 1. Introduction to Symmetric Functions and Plethysm

To fully appreciate the Foulkes Conjecture, one must first establish the rigorous mathematical framework surrounding symmetric functions and the operation of plethysm.

### 1.1 The Algebra of Symmetric Functions
Let $X = \{x_1, x_2, \dots \}$ be an infinite set of commuting variables. The algebra of symmetric functions, typically denoted by $\Lambda$, is a subring of the ring of formal power series in $X$ consisting of those series of bounded degree that are invariant under any permutation of the variables. The algebra $\Lambda$ is a graded algebra, $\Lambda = \bigoplus_{n \geq 0} \Lambda^n$, where $\Lambda^n$ consists of the homogeneous symmetric functions of degree $n$.

There are several classical bases for $\Lambda^n$, which are indexed by integer partitions $\lambda \vdash n$:
1.  **Monomial symmetric functions ($m_\lambda$)**: The sum of all distinct monomials that can be obtained by permuting the variables in $x^{\lambda} = x_1^{\lambda_1} x_2^{\lambda_2} \dots$.
2.  **Elementary symmetric functions ($e_\lambda$)**: Where $e_n = m_{(1^n)}$, and $e_\lambda = e_{\lambda_1} e_{\lambda_2} \dots$.
3.  **Complete homogeneous symmetric functions ($h_\lambda$)**: Where $h_n = \sum_{\lambda \vdash n} m_\lambda$, representing the sum of all monomials of total degree $n$, and $h_\lambda = h_{\lambda_1} h_{\lambda_2} \dots$.
4.  **Power sum symmetric functions ($p_\lambda$)**: Where $p_n = \sum_{i} x_i^n$, and $p_\lambda = p_{\lambda_1} p_{\lambda_2} \dots$.
5.  **Schur functions ($s_\lambda$)**: The most important basis, which can be defined combinatorially as $s_\lambda = \sum_T x^T$, where the sum is over all semistandard Young tableaux $T$ of shape $\lambda$ [cite: 1].

### 1.2 The Operation of Plethysm
Plethysm, introduced by D.E. Littlewood, is a binary operation on symmetric functions, denoted by $f[g]$ or $f \circ g$, which essentially represents the composition of symmetric functions. 

It is uniquely defined by a set of axiomatic properties evaluated on the power sum basis. Let $f, g$, and $h$ denote symmetric functions with integer coefficients. The following properties uniquely define plethysm [cite: 2]:
- $p_k[p_m] = p_{km}$
- $p_k[f \pm g] = p_k[f] \pm p_k[g]$
- $p_k[f \cdot g] = p_k[f] \cdot p_k[g]$
- $(f \pm g)[h] = f[h] \pm g[h]$
- $(f \cdot g)[h] = f[h] \cdot g[h]$

Since every symmetric function can be expressed as a polynomial in the power sum symmetric functions $p_k(x)$ (with rational coefficients), these rules uniquely determine the expression $f[g]$ for any $f, g \in \Lambda$ [cite: 2].

Alternatively, plethysm can be defined by the action of the Adams operator. The operator sending $f(x)$ to $f(x^2) = f[p_k(x)]$ is called the $k$-th Adams operator. If $f(x) = \sum_\lambda c_\lambda(q) p_\lambda(x)$, then $f[g(x)] := \sum_\lambda c_\lambda(q) \prod_{j=1}^{\ell(\lambda)} p_{\lambda_j}[g(x)]$ [cite: 2].

### 1.3 Schur-Positivity and the Core Problem
A symmetric function $f \in \Lambda$ is said to be **Schur-positive** if its expansion into the basis of Schur functions yields non-negative coefficients:
$$ f = \sum_{\lambda} c_\lambda s_\lambda \quad \text{where } c_\lambda \geq 0 \text{ for all } \lambda. $$

Finding a combinatorial or representation-theoretic formula for the Schur plethysm coefficients $p_{\lambda, \mu}^\nu$ in the expansion $s_\lambda[s_\mu] = \sum_{\nu \vdash mn} p_{\lambda, \mu}^\nu s_\nu$ is a major open problem in the theory of symmetric functions and the representation theory of classical groups [cite: 2]. Richard Stanley identified the determination of a combinatorial interpretation for these plethysm coefficients as a central open problem in algebraic combinatorics [cite: 3, 4]. The difficulty lies in the fact that plethysm is highly non-linear and traditional tools for decomposing tensor products (like the Littlewood-Richardson rule) do not directly apply.

## 2. Statement of the Foulkes Conjecture

In 1950, H.O. Foulkes observed a pattern while computing the coefficients in the plethysm of Schur functions and formulated what is now known as the Foulkes Conjecture [cite: 5, 6].

**The Foulkes Conjecture (Symmetric Function Formulation):**
For any positive integers $a, b$ such that $a \leq b$, the difference of plethysms of complete homogeneous symmetric functions:
$$ h_b[h_a] - h_a[h_b] $$
is Schur-positive [cite: 2].

In terms of character theory, expanding this difference positively in the Schur function basis corresponds directly to an inclusion of modules. 

### 2.1 Representation Theoretic Interpretations

The Foulkes Conjecture can be seamlessly translated into the languages of both the General Linear Group $GL(V)$ and the Symmetric Group $S_n$.

#### 2.1.1 The General Linear Group $GL(V)$ Formulation
Let $V$ be a finite-dimensional complex vector space. The general linear group $GL(V)$ acts naturally on $V$, and this action extends to the tensor algebra and its quotients. Let $Sym^k V$ (or $S^k(V)$) denote the $k$-th symmetric power of $V$. The complete homogeneous symmetric function $h_n$ is the formal character of the $GL(V)$-module $Sym^n V$.

The plethysm of symmetric functions corresponds to the composition of polynomial representations [cite: 2]. Therefore, the character of the module $Sym^a(Sym^b V)$ is precisely $h_a[h_b]$.

From this perspective, the Foulkes Conjecture asserts that there is a $GL(V)$-module inclusion:
$$ Sym^a(Sym^b V) \hookrightarrow Sym^b(Sym^a V) \quad \text{for all } a \leq b $$
[cite: 6, 7]. Equivalently, this means that every $GL(V)$-irreducible module occurs with a smaller or equal multiplicity in $Sym^a(Sym^b V)$ than it does in $Sym^b(Sym^a V)$ [cite: 8]. 

It is worth noting that when the dimension of the vector space $V$ is exactly 2, the conjecture is a proven theorem corresponding to **Hermite's Law of Reciprocity** (1854), which states that the modules $Sym^a(Sym^b V)$ and $Sym^b(Sym^a V)$ are isomorphic [cite: 7, 8]. This early result provided significant motivation for expecting similar properties in higher dimensions.

#### 2.1.2 The Symmetric Group $S_n$ Formulation
Through the lens of Schur-Weyl duality, polynomial representations of $GL(V)$ are intimately connected to representations of the symmetric group $S_n$.

Let $n = ab$. We consider the set of partitions of an $ab$-element set into $b$ disjoint subsets of size $a$. The symmetric group $S_{ab}$ acts transitively on this set of partitions. The corresponding permutation module over the complex numbers is known as the **Foulkes module**, often denoted $H^{(a^b)}$ or $F_a^b$ [cite: 5, 9].

Algebraically, this module can be constructed via an induced representation. The stabilizer of a specific partition of $ab$ into $b$ sets of size $a$ is the wreath product $S_a \wr S_b$, which is a semidirect product of $S_b$ acting on the base group $(S_a)^b$ [cite: 10]. The Foulkes module is the induction of the trivial representation from this wreath product up to the full symmetric group $S_{ab}$:
$$ F_a^b = 1 \uparrow_{S_a \wr S_b}^{S_{ab}} $$
[cite: 5, 11]. 

The character of $F_a^b$ corresponds to the symmetric function $h_b[h_a]$ under the Frobenius characteristic map [cite: 6]. Consequently, the Foulkes Conjecture states that if $a \leq b$, then $F_a^b$ can be embedded into $F_b^a$ as an $S_{ab}$-module [cite: 5, 12]. In terms of multiplicities of irreducible representations (the Specht modules $S^\lambda$), the conjecture claims:
$$ \langle S^\lambda, F_a^b \rangle \leq \langle S^\lambda, F_b^a \rangle \quad \text{for all partitions } \lambda \vdash ab $$
[cite: 5, 11].

## 3. History and Chronology of Verified Cases

Despite its elegant formulation, the Foulkes Conjecture has proven exceptionally resistant to a general proof. Progress has relied on isolating specific base cases, employing complex geometric arguments, and leveraging massive computational power.

### 3.1 The Base Cases: $a = 2$ and $a = 3$
The history of the problem predates Foulkes' formal statement. In 1942, R.M. Thrall computed the structure of the plethysms involving $S^2$ and $S^a$ as sums of Schur functions. By explicitly computing the coefficients, Thrall effectively proved the conjecture for the case $a = 2$ [cite: 5, 11]. For $a=2$, Black and List also demonstrated that the map $\psi: H^{(b^2)} \to H^{(2^b)}$ is injective [cite: 12].

For almost sixty years, the case $a=3$ remained unresolved. It was not until the year 2000 that S.C. Dent and J. Siemons achieved a breakthrough. They decomposed the Foulkes modules $F_3^b$ and $F_b^3$ into Specht modules and successfully verified the conjecture for $a = 3$ [cite: 5, 13]. Specifically, Dent and Siemons established an upper bound on the multiplicities of Specht modules $S^\lambda$ in $F_3^b$ and a corresponding lower bound in $F_b^3$, allowing them to conclude that the multiplicity of any irreducible module in $F_3^b$ is less than or equal to its multiplicity in $F_b^3$ [cite: 11, 12].

### 3.2 Asymptotic Truth: Brion's Theorem (1993)
In 1993, Michel Brion provided a major theoretical advancement using techniques from geometric invariant theory and Lie theory. He proved that the Foulkes Conjecture holds true asymptotically; that is, the conjecture is true for integers $a$ and $b$ provided that $b$ is "sufficiently large" compared to $a$ [cite: 8, 12]. While Brion's result does not explicitly bound how large $b$ must be for a given $a$, it provided strong evidence that the conjecture is fundamentally sound [cite: 14, 15].

### 3.3 The Cases $a = 4$ and $a = 5$: Computation and Propagation
As $a$ increases, the dimensions of the representations involved explode combinatorially. For example, the dimension of the Foulkes module $F_5^5$ (representing partitions of 25 items into 5 sets of 5) is approximately $5 \cdot 10^{12}$ [cite: 16]. Direct computation of irreducible multiplicities becomes completely intractable, and standard algorithms suffer from severe integer overflow on standard computing architectures [cite: 10].

To bypass these limitations, researchers sought to establish specific module homomorphisms. In 2005, J. Müller and M. Neunhöffer utilized advanced computational algebra techniques to evaluate the "standard maps" (maps between permutation modules associated with the SWS conjecture, discussed in Section 5). They computed that the standard map is injective on the partition $\lambda = (4^4)$, which implied the Foulkes conjecture for $a = 4$ [cite: 11, 12]. 

However, Müller and Neunhöffer also discovered that the standard map is *not* injective for $\lambda = (5^5)$ [cite: 11]. This meant that the direct approach of using standard map injectivity failed for $a=5$, presenting a massive hurdle.

The solution came through a powerful theoretical bridge constructed by Tom McKay in 2008. McKay proved a crucial **propagation theorem**: If the standard map $\Psi_{a, b-1}$ is injective, then the standard map $\Psi_{a, c}$ is injective for all $c \geq b$ [cite: 7]. Because Müller and Neunhöffer had shown that the standard map for a $4 \times 4$ rectangle was injective, McKay's theorem immediately implied the conjecture for $a=4$ for all $b \ge 4$ [cite: 7, 12].

For the $a=5$ case, since the $5 \times 5$ map had a nontrivial kernel, researchers had to look further. In 2015, M.-W. Cheung, C. Ikenmeyer, and S. Mkrtchyan tackled the problem. They performed an extensive combinatorial calculation on a computer to prove that the standard map is injective for the rectangular partition $\lambda = (5^6)$ (i.e., a $5 \times 6$ rectangle) [cite: 11]. Having established injectivity at $(5^6)$, they applied McKay's propagation theorem to conclude that $\Psi_{5, c}$ is injective for all $c \geq 6$. Combined with prior knowledge, this verified the Foulkes Conjecture completely for $a = 5$ [cite: 7, 17].

In their proof, Cheung, Ikenmeyer, and Mkrtchyan translated McKay's theorem into the language of weight spaces and projections onto invariant spaces of tensors, providing an elegant and computationally feasible path forward [cite: 18].

## 4. The SWS Conjecture and McKay's Standard Map

The techniques used to prove the cases $a=4$ and $a=5$ are deeply rooted in a related conjecture concerning representations of the symmetric group.

Let $\lambda \vdash n$ be a partition, and $\lambda'$ be its conjugate partition. Consider the module $H_\lambda$ (analogous to the Foulkes module, but defined for any partition shape). The **Siemons, Wagner, and Stanley (SWS) Conjecture** hypothesized that if $\lambda$ dominates its conjugate $\lambda'$ ($\lambda \unrhd \lambda'$), then there exists an injective $S_n$-homomorphism from $H_\lambda$ into $H_{\lambda'}$ [cite: 11, 12]. 

When $\lambda$ is a rectangular partition $\lambda = (b^a)$ (representing $a$ parts of length $b$), its conjugate is $\lambda' = (a^b)$. The dominance condition $(b^a) \unrhd (a^b)$ holds precisely when $b \geq a$. Therefore, restricting the SWS conjecture to rectangular partitions yields exactly the Foulkes Conjecture [cite: 11].

While the SWS Conjecture is elegant, it has been refuted in general; counterexamples exist for various non-rectangular partitions [cite: 11, 12]. However, in 2008, Tom McKay proved that a specific "standard map" associated with the SWS conjecture holds under certain structural conditions.

McKay's theorem involves the concept of a "good column." A left-most column of a partition $\lambda$ is defined as *good* if, for all $i$, the hook length $h_{i1}$ has an arm at least as long as its leg. McKay proved that if $\lambda$ is a partition whose left-most column is good, and $\mu$ is the partition obtained by removing this left-most column, then if the standard map $\psi_\mu$ is injective, the standard map $\psi_\lambda$ is also injective [cite: 12]. 

This theorem allows one to "propagate" the injectivity of the map by appending columns to a partition, provided the starting conditions are met. This is the theoretical mechanism that enabled the proofs for $a=4$ and $a=5$ by checking only a finite computational base case and extending it infinitely [cite: 7].

## 5. Generalizations of the Foulkes Conjecture

As researchers have grappled with the classical Foulkes Conjecture, several natural generalizations and analogs have been proposed, expanding the scope of the problem into new algebraic and combinatorial domains.

### 5.1 Vessenes' Generalized Foulkes Conjecture
In 2004, Rebecca Vessenes proposed a significant broadening of the classical statement [cite: 6, 19]. 

Let $a, b, c, d$ be positive integers such that $ab = cd$ and $a \leq b, c, d$. (By convention, we can assume without loss of generality that $a \leq b$ and $c \leq d$). Vessenes' Generalized Foulkes Conjecture states that the difference of plethysms:
$$ h_c[h_d] - h_a[h_b] $$
is Schur-positive [cite: 6, 19]. 

In the language of symmetric group representations, this hypothesizes the existence of an embedding from $F_a^b$ into $F_c^d$ [cite: 11]. 

Setting $c = b$ and $d = a$ immediately recovers the original Foulkes Conjecture [cite: 8]. Vessenes successfully proved her generalized conjecture for the case where $a = 2$, and further proved that every irreducible character occurring in $F_3^b$ also occurs in $F_c^d$, utilizing tableaux construction techniques pioneered by W.F. Doran IV [cite: 11]. Empirical evidence heavily supports this generalized statement; it has been checked explicitly using computer algebra for all instances where the overall degree $n \leq 36$ [cite: 8].

### 5.2 Bergeron's $q$- and $q,t$-Analogs
In 2016, François Bergeron proposed further generalizations by introducing $q$- and $(q,t)$-analogs to the plethystic conjectures [cite: 6, 8]. These analogs elevate the problem from the realm of complete homogeneous symmetric functions to the more complex settings of Hall-Littlewood and Macdonald polynomials.

In Bergeron's $q$-analog, a divided difference of plethysms of Hall-Littlewood polynomials $H_n(x; q)$ replaces the analogous difference of $h_n(x)$ [cite: 8]. 

The full $(q,t)$-conjecture states that for integers $a \leq c, d \leq b$ such that $ab = cd$, and any positive integer $k$, the divided difference:
$$ \frac{H_c \circ H_{[d \times k]}(X; q, t) - H_a \circ H_{[b \times k]}(X; q, t)}{1 - q} $$
expands in the Schur function basis with coefficients in $\mathbb{N}[q, t]$ [cite: 6]. Here, $[d \times k]$ stands for the integer partition possessing $k$ parts of size $d$, and $H_\mu(X; q, t)$ denotes the Macdonald polynomial indexed by $\mu$. 

By setting $q = 0$ and $k = 1$, the properties of Macdonald polynomials dictate that $H_\mu(X; 0, t)$ simplifies in a way that recovers Vessenes' generalized conjecture, and by extension, the original Foulkes Conjecture [cite: 6]. Bergeron has shown that his version holds at the specialization $q=1$ [cite: 8].

### 5.3 Combinatorial Interpretations via $q$-Binomial Coefficients
All of these algebraic conjectures concerning symmetric functions can be specialized into combinatorial statements regarding $q$-binomial coefficients [cite: 20].

The $q$-binomial coefficient $\binom{a+b}{a}_q$ is a polynomial in $q$ of degree $ab$ that counts the number of integer partitions whose Young diagrams fit inside an $a \times b$ rectangle, graded by the size of the partition (the area under the lattice path) [cite: 19]. 

The combinatorial version of the Foulkes Conjecture, proposed by Bergeron, states that if $ab = cd$ and $a \leq b, c, d$, then the polynomial difference:
$$ \binom{c+d}{c}_q - \binom{a+b}{a}_q $$
has non-negative coefficients [cite: 19].

Combinatorially, this translates to a striking geometric inequality: the number of partitions of size $n$ that can fit inside an $a \times b$ rectangle is *less than or equal to* the number of size-$n$ partitions that can fit inside a "skinnier" $c \times d$ rectangle of the identical total area [cite: 19]. This purely combinatorial statement was proven for the case $a=3$ by Zanello in 2018 using Zeilberger's KOH theorem [cite: 19].

## 6. Stability of Plethysm Coefficients and Partition Algebras

A major recent breakthrough in understanding the structure of plethysms and the Foulkes Conjecture has come through the study of stability properties, heavily utilizing the machinery of partition algebras.

### 6.1 Stable Plethysm Coefficients
It is known that the Schur plethysm coefficients $p_{\lambda, \mu}^\nu$ stabilize under certain operations of adding or joining partitions [cite: 2, 3]. As $m$ and $n$ grow large compared to the size of the partition $\lambda$, the sequence of multiplicities of $S^\lambda$ in the plethysm $S^m(S^n(V))$ becomes ultimately constant [cite: 21, 22].

For example, a theorem established by Bowman and Paget (2018) shows that for a partition $\gamma$ of $r$ and $m, n \geq r$, the stable multiplicity $\langle s_n \circ s_m, s_\gamma \rangle$ reaches a fixed limit. In particular, they proved that the stable version of the Foulkes Conjecture holds with equality. This means that as $n, m \to \infty$, the multiplicities in $h_n[h_m]$ and $h_m[h_n]$ completely agree [cite: 21, 23]. 

### 6.2 Schur-Weyl Duality and the Partition Algebra
To prove these stability results, Chris Bowman, Rowena Paget, and Mark Wildon pioneered a new approach using Schur-Weyl duality between the symmetric group and the **partition algebra** [cite: 21, 24, 25].

Classical Schur-Weyl duality relates the representations of the general linear group $GL_n(\mathbb{C})$ and the symmetric group $S_k$ acting on tensor space $V^{\otimes k}$. If one considers the symmetric group $S_n$ as a subgroup of $GL_n(\mathbb{C})$, a generalized instance of Schur-Weyl duality emerges between $S_n$ and the partition algebra $\mathbb{C}A_k(n)$ [cite: 1]. The partition algebra, originally defined by Paul Martin, is an associative algebra with a basis given by set partitions, which centralizes the action of $S_n$ on tensor space [cite: 24].

Bowman and Paget (2024) constructed a partition algebra isomorphism which fundamentally "does not see" any difference between the parameters $m$ and $n$, provided both are sufficiently large [cite: 22, 24]. This isomorphism provides an explicit, positive formula for the multiplicities and yields the first deep conceptual explanation for *why* the Foulkes Conjecture "should" be true—because at the stable limit, the algebraic structure governing both plethysms is identical [cite: 21, 24].

In their subsequent work, Bowman, Paget, and Wildon studied the "ramified partition algebra," proving that plethysm coefficients can be recast as branching coefficients for restriction to a subalgebra of the ramified partition algebra, allowing for sharp upper bounds on these coefficients [cite: 25, 26]. 

Furthermore, entirely combinatorial proofs utilizing "plethystic semistandard signed tableaux" (tableaux with both positive and negative entries) have been developed to classify stability bounds and multiplicity-free plethystic products [cite: 3, 27].

## 7. The Foulkes-Howe Conjecture and Algebraic Geometry

The representation theory of $GL(V)$ naturally intersects with algebraic geometry, providing another arena where the Foulkes Conjecture plays a pivotal role.

### 7.1 The Foulkes-Howe Map
In the late 19th and early 20th centuries, mathematicians studying invariant theory analyzed maps between symmetric powers. As mentioned, Hermite proved that $Sym^a(Sym^b V) \cong Sym^b(Sym^a V)$ when $\dim V = 2$ [cite: 15].

Generalizing this, one can define the **Foulkes-Howe map** $\Phi_{\delta, d} : S^\delta(S^d V) \to S^d(S^\delta V)$. The map is constructed by first including $S^\delta(S^d V)$ into the full tensor space $V^{\otimes \delta d}$, then regrouping and symmetrizing the blocks to $(S^\delta V)^{\otimes d}$, and finally symmetrizing again to land in $S^d(S^\delta V)$ [cite: 15].

### 7.2 The Chow Variety
Jacques Hadamard observed that the kernel of this Foulkes-Howe map is precisely the degree $\delta$ component of the ideal of the **Chow variety**, $I_\delta(Ch_d(V^*))$ [cite: 15]. The Chow variety parameterizes algebraic cycles of a given dimension and degree in projective space; in this context, it is associated with forms that can be written as a product of linear forms.

Hadamard famously conjectured that the map $\Phi_{\delta, d}$ is always of maximal rank (specifically, that it is injective for $\delta \leq d$) [cite: 7, 15]. This assertion became known as the **Foulkes-Howe Conjecture** [cite: 7, 15]. Roger Howe later wrote that this conjecture was "reasonable to expect."

### 7.3 Disproof of the Foulkes-Howe Conjecture
While the general Foulkes Conjecture asserts an inequality of representation multiplicities, the Foulkes-Howe Conjecture asserted a specific strict geometric injectivity. 

In their 2005 computational breakthrough, Müller and Neunhöffer did not just prove $a=4$ for Foulkes; they also proved that the Foulkes-Howe Conjecture is false [cite: 7, 15]. By executing exact calculations, they demonstrated that the map $\Phi_{5,5}$ (the map $S^5(S^5 V) \to S^5(S^5 V)$) has a nontrivial kernel, meaning it is not injective [cite: 7, 15].

Despite this failure of injectivity for $\delta = d = 5$, the analysis of the Foulkes-Howe map remains highly relevant. The work of Cheung, Ikenmeyer, and Mkrtchyan (2015) utilized the non-triviality of the map at $5 \times 5$ to explicitly decompose the vanishing ideal of the 5th Chow variety in degree 5 into $GL(V)$-representations, and proved that there are no degree 5 equations for the 6th Chow variety [cite: 7, 17]. Brion's asymptotic results also apply here, proving that the Foulkes-Howe map is injective asymptotically (when $\delta \gg d$), giving an explicit but massive bound for $\delta$ in terms of $d$ and $\dim V$ [cite: 15].

## 8. Conclusion and Future Directions

The Foulkes Conjecture remains a titan among unsolved problems in algebraic combinatorics. It represents a fundamental gap in our understanding of how polynomial functors compose and how wreath products restrict to symmetric groups.

Significant strides have been made:
1.  The conjecture is unconditionally proven for the base cases $a \in \{2, 3, 4, 5\}$ through a mixture of representation-theoretic bounding, geometric analysis, and heavy computation leveraging propagation theorems.
2.  The asymptotic truth of the conjecture is established.
3.  The stable version of the conjecture has been proven via the deep structural isomorphisms of partition algebras.
4.  Robust generalizations into $q$-analogs, Macdonald polynomials, and combinatorial bounds heavily suggest that Foulkes' original observation is merely a shadow of a much deeper mathematical truth.

However, the general problem for arbitrary finite $a$ and $b$ remains fiercely open. The primary obstacle is that plethysm coefficients are notoriously difficult to compute, lacking a universal combinatorial rule akin to the Littlewood-Richardson rule for tensor products [cite: 2, 4]. As Richard Stanley noted in his survey of positivity problems, without a general combinatorial interpretation of plethysm coefficients, proving inequalities between them globally remains an elusive goal [cite: 3, 4]. 

Future progress will likely require either the discovery of a completely new family of injective module homomorphisms that bypass the failures of the SWS standard map, or further revelations in the stable representation theory of partition algebras that can be systematically "de-stabilized" to yield finite bounds. Until then, the Foulkes Conjecture stands as a profound testament to the intricate complexity hidden within the simplest operations on symmetric functions.

**Sources:**
1. [yorku.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwvVFH8XmbfVj5OHmWQXivlw0oUHIO3sS3NGr7QTJQSLf16P8LPB84Ml9O9BEeZ71i8pOG30DmkV9xllf3xmDgfYtY_zbn_lhLT3lRJhmnIlQHJwCG2tdElVEw6_fjKnOHj2rLiQN9iU7t)
2. [symmetricfunctions.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDvEzarIY5jz4Y4VWr-8lHDstMLODixGU8llosxy5abLuLAJBP6d1zugNuKvbzV3suv3AAi1nCYb_rHjyoySsq9WH1xLNa2g-sqGediMr8osP3fBNcSH_du28lH-0ir6BsyraU)
3. [rhul.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1frBTHW8CAmnA-Iy10mSXZo-wlxjfAqynkqb6M8_66S-NPfkHggDTkUCF84zDbEaHRFVC9v9E-hFam36o0k2R0pANCw3CUnwohjAqD46pFuQHycUeiNRFSGIxY7C6XnYmdy9ktDx1IDCc1P3Z8g9klmQtJcvxTGyqDQ==)
4. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbxkLr2sdx6ABxlcw3b8DWsFV8LnScs7WJBuU3GMj5BvUBCWT4gR1upqFqG_F5VIuErzCEiQcPeS7BHf8jEBp42Q3eUvswiuaocWX3dMH5CdSKcbzAR8hgciVKUY_lcY4X-yJLs23ZCNBaTLKE1N4q3i6iih8ZxBCfWLonQ9yNHsUVgvZKLwdpHUrhdf4ARaJ0nK5cbIyecKH3908f8vaF4XREs1SWL-zZSc72x_Y=)
5. [ceu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGyW51q8z920hqe_z1Xcf-93ZIxT3WDYNCdNlkWZGVtU6iZk62wPhFNqO6biDBlNxRNZpzHQ3B32TJUSBRXJJVnU0nJF16NQ6uk3fMjnI8XA-MOaKNBKs-whJldd22U0jLmG4=)
6. [uqam.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsvG8Fl3MkAwKABUJPlCvRc95XCZRajJHXp-R0hCvu_EgD3awnYTDgmvdlzX7ZYwjKI4F8LZ_MM00zU-9pbFJwx6HAQGfMdH3_c-tRXqfpVRRm0U-7x527732EUgy0MfgYfUMyDlaA17vkWMquQHqH3KINqNTzI8px2mws9qw=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8_QxwQbkbz_UfyszKWWHwbm2Fz18l1zBpDqXb9aNSa091XROnMSnPyfmEJSZwgsz1-SD1oZPoXFBmBFQ5jdUblfA9aISqySKj7GXIsGneBdu-YZpR)
8. [combinatorics.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEN62lpyxGGVYc2aye45xYEx6J8mubDMq2Ku1Nx35cD7brmlRBFjIQR2LzKN7ze44BWm3DvInjZoiu4BAhNS3e4q5wFIYUdfhn61oCWdI6ootyhZP-3z3GJdrNsdWWpTEPfDk9VI8--vMLkj-heWBgnqRkmUXOBX-3qbyzjpOQ1YJZyqiU=)
9. [rhul.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGq50lATtEGhUNONTiLWoDTOnxTkJcKnxcBg6ziawaB7zUfXb7sKOWK7IL9Asun3EPF96jJvoUtILiQIqBcuLJ8JCpJ1jDBAwEfNXjv4fi282TmuzqK73yB_E7wEciXc8kzyr_o_zha8ukx4kA=)
10. [rwth-aachen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNUG97zi0vUquOzB0MiYIiAG_LBW-hicLTh06nA83lr1aYjlRUg0fNvhxpp06wzvoP1oTT56q62l3ewrUzjH-ddBeSnOTXFVjmHHecetjxN267eFp8rsFyOExtOvRuOl-CutdEpsRH36TlcVaLgrlrd0SVbj23ng==)
11. [ceu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG767kdWtXE4MZKuoZZ3EwR7T1YlmQ0vAyQUaGGHjTHwRTOP3aN9_PDlYxiLRBNRf0jiuhMd52_-9mOBbDqyunZbo-3DoqR-h18_4aDsiBJgEeDXcCUh1aBLjczWCZSzFRd444=)
12. [core.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuzc77rA2sgzI74dASMxWzpcDurxVW7qRDHdFW2-MaxPCuvRMxNyIr-avfv-eYDIZg_ribGYkkpoKxegYATDumsln141wRJcKvbd06V_Ubfc-hnquJLVggkDKpizrIzKw_)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGimwOlhtbN7BaVHkpdfIBkzzP0X8wMxsKPKpBE8YuG21y9dlB_vAgCYE47GaWNcUfbZNDqZ2MB_XrnOhNTmmZBN4FRil8mwCLRWncvYmFkJs9yROWkQxkcRM97mlvlJW0NG_kJ_Oz_79ukdHtrVx0Kq87v0zBE8ulDl3QdfkBMOJqwml6CmLFGThXQiKUC1OjFMN1zQIEBbpOw)
14. [uea.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrG-Zjp1jGYypGyObWKttIganzR0wi9tiaTqn4-L1oI3vCYbmOPlkMZ7UgX2VkWa86eh3iMqeAyKWtjDy-6PtQjcf9riCEDlcPCbamz-6tvAWKeZFhmSoISQLZ7DZ63JJ_kgo8lsj5HCBf9A==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHf6G3s4m8-ctvFlLJ4S75hr7kBm-Z6Pv-0cTJYtjOYCYcw2693Q1H92nDsmihliwLDnXnF5rj7Z0Aau0Es_k2bN5wh22IDNK9GBwbZhCkKhmtg0iXz)
16. [us.es](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGj75GkBENdoYOuK7d947MWOE6IoBh9dox1LQVbIFkVMhx9teWRGXpxVxzNQqIE8CDTLORTZl_bD0HQnBIFPg4xWXJhY3fo-VHC7d73sbSEk8Vh2dNJZspekXbcZi-_4Jt15zscVKVeNMJon1SKPkFnog==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEwe_CE0cyJXI-F33CjZ3zvDAemJdHbpW1Zvf9xSnt0y6RcN0wMB10M3BdTOfWfto1Q1GkRegNdJgI_T3HK7C88EOt2RIBQucKgp2aB1I8AFPZ4E9A)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOWtwu9RRP5mG4_7B_9BOd08kIIJvlxjOCwukK6WP5oCJsrsiZxOMljrytaJg-wVK3fsBB41R4-DU7V3dLuiVGEAFdbHsQc_H4iIubV_gyv4mE-X8t)
19. [msu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEuO3Aqd3GFljgafY4PE0fjEn2DY385vJYJjCVp0IHiokqG9a-GQkxi_An-4AduZBVdOsmrYWgDlQD4e8enkWK9v53L5EFXeHjVzJCWby8WY5AOqtEkvqD7HdVHjTQlLyXllrENVkGMZaiov-9_2jSnANVNRbsQMA0ZiAa_RX6mhObkw==)
20. [utoronto.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEW-0nr2D2SJ2OoTtIWz7sEPXVUDaTljMWY4m5zkf-NaB_3TEbfG4vhbhRcTRHui69w40pDnIfzYoXpTIkiizU4FIEb00mtYKJKlh9PuDAcdsSEEJi1TPtN_KQRTD4hp2p7Pe30rBQimEBg5tSeYDRuCSn7o8aEvtUZCnGkla30FfnDiw==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6EqWewvn-T5oLNZrJPh7UspP3WIr0znstXkuleTweFxI8t8GESXnKRpUqkVJaJAhaSgFwtiEvoQaRvW15Vsure7hVt_eAwKRoSSIfr8NFYf2B4tHd)
22. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwPolRiKJzdd8cbEgZJuqrBrgtX0QHRMZGmZjos8ETppheystLTJ-w3YHjtfvmlZIVp_e_xRADYKaPt6k94S5NaLSkz5H0b8ljY3Nlag2q4MrlgnzR2jRN4nO4OssC5H2KyOKpSgYFptMN-TS_fz2MLyLvjcUpP44=)
23. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGf3wbe6oC8wHX--Xb1AUlEUuKzajOCoqKu9__wuSjiQwUrNQJdStaHUH02sMEVYr6jUQZOMXEbCNo_priE6yRDB6MubQxfLweMks4QeiYbdfCEZk6RRCkGWBk8yZfQII-eMTexMeA82lP6IvDtqgHQR6MI)
24. [whiterose.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvJAhfr7ps64wJ8Dzk3xbCEpuLhcIoD2K1fruFTLXn2PiItxdLqiMVO1yG_sy2w-dKxugY19quLtP4ALZ82XRjI0cF3p02goJoYMtdPFV1lXLL6GoYXAZP0_Chh94U8dokiq6LFiLy_D28MA0ihM3dn-OgwHKTix1QdWCjF3cwOFhOqKFj88vCdw==)
25. [york.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEacTGespop_0Wo1mR3Aj_IZPKNDFDAIcmjPP9A2CVWKhV79dC4wZiEKtw_l_Y9-uUcJyjEWdTGk6WqucIynq-HeQiuOc9bMV-tuFYThthFcI0fpDjJcGSqIPHrG9j3PYRmRV-c4Z_vcsrx0y4WqMDiu1IfnQ8r0GWGUHiKJMm4qPqFlhpU)
26. [kent.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGud0wzszLt3RuZuEju_nQSV_gEovU5rpWbSslD8tj77cbEKF3pnvBQy-4FgW9ReQsqtBAOawRitx5OkoEHYDPbalTvT1ZVtaEy5n0gLJuooLmvVH_07es0G5DfW8dJtw==)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgSNM4uRC4i8SvgtUBTNeSqChW9zzwzpkXCafPTjp0U5bjxg_p6Kmf3nCCBmBP_fuNSiQc8XnET0VMJsIbynAvkLIMoFi4mKVdeXCbjMLk6nH4WEDS1JOsY_76woxOmymQcZf6JHrLt0TLWgWc187xsIopw439g9xHiLK75sNG4Se3Fs8i9ulDBPAqCiB69lCAg1sdRJeRytHj7zbi1iz-cg5ziBvIyEwxIjEj6msVoh0Ihve1jzhu)

