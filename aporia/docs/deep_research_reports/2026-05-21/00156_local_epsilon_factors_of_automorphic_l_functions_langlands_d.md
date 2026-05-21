# Local epsilon factors of automorphic L-functions (Langlands-Deligne)

**Pythia queue id:** 156
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chdvak1QYXRTQk5jZm5fdU1QcmYyZTRRWRIXb2pNUGF0U0JOY2ZuX3VNUHJmMmU0UVk
**Elapsed:** 250s
**Completed at:** 2026-05-21T16:36:46.067888+00:00

---

# Local Epsilon Factors of Automorphic L-functions (Langlands-Deligne)

**Key Points:**
*   The **Langlands-Deligne local constant**, commonly known as the local epsilon factor, is a foundational mathematical function associated with representations of the Weil-Deligne group of a local field [cite: 1]. 
*   These constants originate from the functional equations of global $L$-functions (such as Artin $L$-functions), where the global epsilon factor can be canonically factored into a product of local epsilon factors over all primes [cite: 1].
*   While John Tate proved their existence for one-dimensional representations, the existence and uniqueness for higher-dimensional representations were initially proven by Robert Langlands using complicated local methods, and later by Pierre Deligne using a remarkably elegant global argument based on Brauer induction [cite: 1, 2].
*   Local epsilon factors serve as the crucial invariants preserved under the **Local Langlands Correspondence (LLC)**, guaranteeing that the arithmetic (Galois) side and the analytic (automorphic) side align perfectly [cite: 3, 4].
*   The computation and theoretical properties of these factors are essential in resolving deep conjectures in representation theory and number theory, including the Saito-Tunnell theorem, the Jacquet-Langlands correspondence, and the existence of invariant trilinear forms for triple products of representations [cite: 5, 6, 7].

### Overview of the Topic
For a layman, understanding numbers often stops at counting, but in advanced number theory, numbers are organized into fields, and we study symmetries of these fields using groups (like the Galois group). To analyze these symmetries, mathematicians use $L$-functions, which are vast generalizations of the Riemann zeta function. These $L$-functions exhibit "functional equations," a type of mathematical reflection that relates their values at a point $s$ to $1-s$. 

When you reflect the function, a balancing constant emerges, known as the "epsilon factor." Research suggests that this global constant can actually be broken down into local pieces—one for every prime number (or "place"). These pieces are the **local epsilon factors**. Proving that these local pieces exist and behave coherently for complex, multi-dimensional symmetries was a monumental achievement in modern mathematics, credited to Robert Langlands and Pierre Deligne. Today, these constants are the linchpin of the Langlands Program, a grand unified theory of mathematics that connects algebra, geometry, and analysis.

---

## 1. Introduction to Automorphic L-Functions and Functional Equations

The study of $L$-functions is central to modern algebraic number theory and the theory of automorphic forms. The archetype of all such functions is the Riemann zeta function $\zeta(s) = \sum_{n=1}^\infty n^{-s}$, which, as established by Bernhard Riemann, admits a meromorphic continuation to the entire complex plane and satisfies a functional equation relating $\zeta(s)$ to $\zeta(1-s)$. 

In the twentieth century, this concept was vastly generalized. Emil Artin introduced Artin $L$-functions attached to finite-dimensional complex representations of the absolute Galois group of a number field. Similarly, Erich Hecke introduced Hecke $L$-functions attached to Grössencharacters. In all these cases, if $L(\rho, s)$ is the $L$-function associated with a representation $\rho$, it satisfies a functional equation of the form:
\[ L(\rho, s) = \varepsilon(\rho, s) L(\rho^\vee, 1-s) \]
where $\rho^\vee$ is the contragredient (or dual) representation [cite: 1]. 

The factor $\varepsilon(\rho, s)$ is the **global epsilon factor** (or global constant). It takes the form of an exponential function multiplied by a complex constant of absolute value 1 (often called the Artin root number). Robert Langlands made the profound discovery that this global epsilon factor $\varepsilon(\rho, s)$ can be written in a canonical way as a product over all places (primes) $v$ of the underlying global field:
\[ \varepsilon(\rho, s) = \prod_v \varepsilon(\rho_v, s, \psi_v) \]
where $\varepsilon(\rho_v, s, \psi_v)$ is the **local epsilon factor** (or Langlands-Deligne local constant) associated to the local representation $\rho_v$ at the place $v$, and $\psi_v$ is a local additive character [cite: 1]. 

The existence of these local constants for one-dimensional representations was definitively established in John Tate's celebrated 1950 thesis [cite: 1]. Bernard Dwork subsequently proved the existence of the local constant up to sign. However, the full existence and uniqueness theorem for representations of arbitrary dimension was first proven by Langlands in 1970 using highly intricate local methods, which were never published [cite: 1]. Shortly thereafter, Pierre Deligne discovered a much simpler and more elegant proof leveraging global methods and Brauer's theorem on induced characters [cite: 1].

## 2. Fundamentals of Local Fields and Galois Groups

To rigorously define the Langlands-Deligne local constant, we must establish the algebraic structures over which it operates.

### 2.1 Non-Archimedean Local Fields
Let $F$ be a non-archimedean local field. That is, $F$ is a locally compact, totally disconnected topological field with a non-discrete topology. Examples include the $p$-adic numbers $\mathbb{Q}_p$, finite extensions of $\mathbb{Q}_p$, and the field of formal Laurent series $k((t))$ over a finite field $k$ of characteristic $p$ [cite: 2]. 
Let $\mathcal{O}_F$ be the ring of integers of $F$, $\mathfrak{p}_F$ its unique maximal ideal, and $\varpi_F$ a uniformizer, so that $\mathfrak{p}_F = \varpi_F \mathcal{O}_F$. The residue field $k_F = \mathcal{O}_F / \mathfrak{p}_F$ is a finite field of cardinality $q$, where $q$ is a power of a prime $p$ [cite: 8, 9]. 

### 2.2 The Weil Group
Let $\bar{F}$ be a separable algebraic closure of $F$, and let $G_F = \text{Gal}(\bar{F}/F)$ be the absolute Galois group of $F$, equipped with the Krull topology. The group $G_F$ contains the inertia subgroup $I_F$, which sits in an exact sequence:
\[ 1 \to I_F \to G_F \to \text{Gal}(\bar{k}_F / k_F) \to 1 \]
The quotient group $\text{Gal}(\bar{k}_F / k_F)$ is topologically generated by the geometric Frobenius element $\text{Frob}$, which acts on $\bar{k}_F$ by $x \mapsto x^{1/q}$ [cite: 10].

The **Weil group** $W_F$ is defined as the dense subgroup of $G_F$ consisting of elements whose image in $\text{Gal}(\bar{k}_F / k_F)$ is an integer power of $\text{Frob}$ [cite: 8]. The topology on $W_F$ is not the subspace topology induced from $G_F$; rather, the topology is defined such that $I_F$ retains its profinite topology and is an open subgroup of $W_F$. Thus, $W_F / I_F \cong \mathbb{Z}$ discretely [cite: 10, 11].

By local class field theory, there is a canonical isomorphism, the Artin map:
\[ \text{Art}_F : F^\times \xrightarrow{\sim} W_F^{\text{ab}} \]
where $W_F^{\text{ab}}$ is the abelianization of $W_F$. This map normalizes uniformizers to correspond to geometric Frobenius elements (or arithmetic Frobenius, depending on the chosen convention; Deligne's convention typically uses geometric Frobenius) [cite: 12].

## 3. The Weil-Deligne Group and its Representations

While the Weil group is sufficient for characterizing representations of Galois groups with finite image, the study of $\ell$-adic Galois representations and automorphic forms requires a slightly richer structure: the Weil-Deligne group.

### 3.1 Definition of the Weil-Deligne Group
The Weil-Deligne group $W'_F$ can be thought of conceptually as $W_F \ltimes \mathbb{C}$ [cite: 10]. A finite-dimensional complex representation of the Weil-Deligne group is defined as a pair $(\rho, N)$ where:
1. $\rho: W_F \to \text{GL}(V)$ is a continuous homomorphism (with respect to the discrete topology on $\text{GL}(V)$, meaning the kernel of $\rho$ is open in $W_F$).
2. $N \in \text{End}(V)$ is a nilpotent endomorphism.
3. For all $w \in W_F$, the relation $\rho(w) N \rho(w)^{-1} = |w|_F N$ holds, where $|w|_F = q^{-n(w)}$ if the image of $w$ in $W_F/I_F$ is $\text{Frob}^{n(w)}$ [cite: 10].

### 3.2 Frobenius Semisimplicity
A Weil-Deligne representation $(\rho, N)$ is said to be **Frobenius semisimple** (or $\phi$-semisimple) if the representation $\rho$ of $W_F$ is semisimple, which is equivalent to saying that $\rho(\text{Frob})$ is a diagonalizable endomorphism of $V$ [cite: 10]. Note that if $\rho$ is an irreducible representation of $W_F$, then $N$ must necessarily be zero, because the kernel of $N$ is a $W_F$-invariant subspace [cite: 10]. 

By a theorem of Grothendieck (the Monodromy Theorem), any continuous $\ell$-adic representation of $G_F$ (for $\ell \neq p$) naturally gives rise to a Weil-Deligne representation over $\mathbb{C}$ upon fixing an isomorphism $\overline{\mathbb{Q}_\ell} \cong \mathbb{C}$ [cite: 10, 13]. Furthermore, any Frobenius semisimple Weil-Deligne representation decomposes as a direct sum of indecomposable representations of the form $\rho_0 \otimes \text{Sp}(m)$, where $\rho_0$ is an irreducible representation of $W_F$ (hence $N=0$), and $\text{Sp}(m)$ is the special representation of dimension $m$ corresponding to a specific nilpotent block [cite: 10, 14].

## 4. Tate's Thesis and One-Dimensional Local Constants

Before analyzing the representations of arbitrary dimensions, it is imperative to construct the local constants for one-dimensional representations, an achievement that forms the backbone of John Tate's thesis [cite: 1].

### 4.1 Haar Measure and Characters
Let $F$ be a local field. We fix a non-trivial continuous additive character $\psi: F \to \mathbb{C}^\times$ [cite: 2, 14]. Let $dx$ be a Haar measure on $F$. Let $d^\times x$ be a Haar measure on the multiplicative group $F^\times$. 
A continuous homomorphism $\chi: F^\times \to \mathbb{C}^\times$ is called a quasicharacter. By the local Artin isomorphism, $\chi$ can be viewed as a one-dimensional representation of $W_F$ [cite: 12].

### 4.2 Local Zeta Integrals and Functional Equations
Let $\mathcal{S}(F)$ be the space of Schwartz-Bruhat functions on $F$ (locally constant functions with compact support) [cite: 14]. For $\Phi \in \mathcal{S}(F)$, Tate defined the local zeta integral:
\[ Z(\Phi, \chi, s) = \int_{F^\times} \Phi(x) \chi(x) |x|^s d^\times x \]
Tate proved that this integral converges for $\text{Re}(s) > 0$ and admits a meromorphic continuation to all $s \in \mathbb{C}$. 

Let $\hat{\Phi}$ be the Fourier transform of $\Phi$ with respect to $\psi$ and $dx$:
\[ \hat{\Phi}(y) = \int_F \Phi(x) \psi(xy) dx \]
The fundamental local functional equation in Tate's thesis states that the ratio
\[ \frac{Z(\hat{\Phi}, \chi^{-1}, 1-s)}{Z(\Phi, \chi, s)} = \gamma(\chi, s, \psi, dx) \]
is independent of the choice of the test function $\Phi$ [cite: 2].

### 4.3 Definition of the Local Epsilon Factor
The gamma factor $\gamma(\chi, s, \psi, dx)$ contains the poles of the local $L$-functions. Tate defined the local $L$-factor $L(\chi, s)$ as follows:
- If $\chi$ is unramified (trivial on $\mathcal{O}_F^\times$), $L(\chi, s) = (1 - \chi(\varpi_F) q^{-s})^{-1}$ [cite: 2, 14].
- If $\chi$ is ramified, $L(\chi, s) = 1$ [cite: 2].

The **local epsilon factor** $\varepsilon(\chi, s, \psi, dx)$ is then defined to strip away the $L$-factors:
\[ \varepsilon(\chi, s, \psi, dx) = \gamma(\chi, s, \psi, dx) \frac{L(\chi, s)}{L(\chi^{-1}, 1-s)} \]
It is an exponential function of $s$ of the form $c \cdot q^{-ns}$ for some constant $c \in \mathbb{C}^\times$ and integer $n$ [cite: 14].

As highlighted in the academic literature [cite: 2], the definition of the local factor is highly subtle: it is the ratio of two of Tate's local integrals divided by the ratio of the two local $L$-functions. In the unramified case, choosing the characteristic function of $\mathcal{O}_F$ as the test function $\Phi$ makes the integral exactly equal to the local $L$-function. Consequently, everything cancels, and $\varepsilon(\chi, s, \psi, dx) = 1$ (assuming $dx$ gives $\mathcal{O}_F$ volume 1 and $\psi$ has conductor $\mathcal{O}_F$). However, in the ramified case, the local $L$-function is 1, and the integral naturally yields a Gauss sum. Thus, the epsilon factor for a ramified character essentially reduces to a local generalized Gauss sum [cite: 2].

## 5. The Langlands-Deligne Local Constant: Formalization

Having established the epsilon factor for one-dimensional representations, Langlands asked whether this could be extended to arbitrary finite-dimensional representations of the Weil group $W_F$, and by extension, the Weil-Deligne group $W'_F$. 

### 5.1 The Langlands-Deligne Theorem
**Theorem (Langlands–Deligne):** Let $F$ be a local field. There exists a unique system of local constants $\varepsilon(\rho, s, \psi, dx)$ associated with finite-dimensional complex representations $\rho$ of $W_F$ satisfying the following characterizing properties [cite: 1, 12, 14]:

1. **One-Dimensional Consistency:** If $\rho$ is one-dimensional, it corresponds via local class field theory to a quasicharacter $\chi$ of $F^\times$. In this case, $\varepsilon(\rho, s, \psi, dx) = \varepsilon(\chi, s, \psi, dx)$ as defined in Tate's thesis [cite: 1].
2. **Additivity on Exact Sequences:** For any short exact sequence of representations $0 \to \rho_1 \to \rho_2 \to \rho_3 \to 0$, we have:
   \[ \varepsilon(\rho_2, s, \psi, dx) = \varepsilon(\rho_1, s, \psi, dx) \varepsilon(\rho_3, s, \psi, dx) \]
   This implies that $\varepsilon$ is uniquely defined on the Grothendieck group of virtual representations $R(W_F)$ [cite: 1, 14].
3. **Inductivity in Degree Zero:** Let $E/F$ be a finite extension, and let $V$ be a virtual representation of $W_E$ of dimension 0. Let $\text{Ind}_{W_E}^{W_F}(V)$ be the induced virtual representation of $W_F$. Then:
   \[ \varepsilon(\text{Ind}_{W_E}^{W_F}(V), s, \psi, dx) = \varepsilon(V, s, \psi \circ \text{Tr}_{E/F}, dx_E) \]
   where $\text{Tr}_{E/F}$ is the trace map and $dx_E$ is the suitably normalized Haar measure [cite: 1].

### 5.2 Notational Conventions and Parameter Dependence
There are several conventions regarding the parameters of the local constant [cite: 1]:
- **The complex parameter $s$:** The parameter $s$ is often redundant because twisting a representation by the unramified character $|\cdot|^s$ handles the $s$-dependence: $\varepsilon(\rho, s, \psi, dx) = \varepsilon(\rho \otimes |\cdot|^s, 0, \psi, dx)$ [cite: 1].
- **The choice of Haar measure $dx$:** Deligne's convention explicitly includes the Haar measure $dx$. If $V$ has dimension $n$, rescaling the measure by a positive scalar $a$ scales the epsilon factor: $\varepsilon(\rho, \psi, a\,dx) = a^n \varepsilon(\rho, \psi, dx)$. For representations of dimension 0, the choice of measure completely cancels out, which is why property (3) above is independent of the normalization [cite: 1, 14]. Langlands' convention fixes the measure to be self-dual with respect to $\psi$.

### 5.3 Extension to the Weil-Deligne Group
For a representation $(\rho, N)$ of the Weil-Deligne group $W'_F$, the epsilon factor is defined purely via the representation $\rho$ of $W_F$, while the $L$-factor depends on both $\rho$ and $N$ [cite: 10]. Specifically, Deligne defined the arithmetic epsilon factor $\varepsilon_0(\rho, \psi, dx)$ [cite: 8, 9]. The operation of taking epsilon factors for Weil-Deligne representations is not strictly additive in exact sequences because taking coinvariants of $N$ is not exact [cite: 14]. However, it is fundamentally derived from the underlying $W_F$ structure.

## 6. Brauer Induction and Deligne's Global Proof

The core difficulty in the Langlands-Deligne theorem was proving the existence of an $\varepsilon$ satisfying the inductivity properties. Langlands' original 1970 proof utilized local, incredibly complex analytic methods that evaluated constants across various field extensions. Because it was so unwieldy, it remained unpublished [cite: 1].

In 1973, in his famous "Antwerp II" paper *Les constantes des équations fonctionnelles des fonctions L*, Pierre Deligne offered a stunningly simplified proof relying on a global-to-local argument and group representation theory [cite: 2, 13].

### 6.1 Brauer's Theorem on Induced Characters
Deligne's proof fundamentally rests on Brauer's theorem [cite: 1, 2, 15]. For a finite group $G$, let $R(G)$ be its Grothendieck group (the free abelian group on the isomorphism classes of irreducible representations). Let $R_+(G)$ be the free abelian group with basis given by the isomorphism classes of pairs $(H, \chi)$ where $H \subseteq G$ is a subgroup and $\chi$ is a 1-dimensional representation of $H$ [cite: 2, 15].

There is a natural map $R_+(G) \to R(G)$ given by $(H, \chi) \mapsto \text{Ind}_H^G(\chi)$. Brauer's induction theorem states that this map is surjective: any complex representation of a finite group can be written as an integral linear combination of representations induced from 1-dimensional representations of subgroups [cite: 2, 15]. 

To define $\varepsilon$ for an arbitrary representation, one writes it as a sum of induced 1-dimensional characters (whose epsilon factors are defined by Tate's thesis and property 3). However, one must prove that this assignment is well-defined. The kernel of the map $R_+(G) \to R(G)$ is generated by specific relations (such as transitivity of induction and relations arising in solvable groups). Checking that the local constant assignments respect these relations purely locally is exceedingly difficult [cite: 2].

### 6.2 Deligne's Global Argument
Deligne observed that for global L-functions (associated to global Galois representations), the global epsilon factor is unconditionally well-defined via the meromorphic continuation of the $L$-function [cite: 2]. Because global L-functions behave perfectly under induction, global epsilon factors inherently satisfy all the desired properties.

To prove the local existence theorem for a local field $F$, Deligne [cite: 2] executed the following strategy:
1. Realize the local field $F$ as the completion of a global field $K$ at some place $v$ [cite: 16].
2. For an arbitrary representation $\rho$ of the local Weil group $W_F$, construct a global representation $\sigma$ of the global Weil group $W_K$ such that $\sigma_v = \rho$.
3. Since local epsilon factors "exist in the unramified case" (being trivially 1 or just an Euler factor), and Tate had shown existence for 1-dimensional characters, one can leverage the product formula for the global epsilon factor $\varepsilon(\sigma, s) = \prod_{w} \varepsilon(\sigma_w, s, \psi_w)$.
4. By cleverly twisting with highly ramified global characters, Deligne isolated the local place $v$. Because the global constant is well-defined and respects induction, the local constant at $v$ must also be well-defined and respect induction.
"The proof is basically trivial, coming from good behaviour of the global epsilon constants... a clever twisting argument," as summarized in Kevin Buzzard's notes [cite: 2].

## 7. The Local Langlands Correspondence (LLC)

The most prominent role of the Langlands-Deligne local constant in modern mathematics is its indispensable status within the Local Langlands Correspondence [cite: 3]. The LLC represents a profound link between arithmetic geometry and harmonic analysis.

### 7.1 Statement of the LLC for GL(n)
Let $F$ be a $p$-adic local field. The Local Langlands Correspondence establishes a canonical bijection between two vastly different sets of objects [cite: 9, 17, 18]:
- **Arithmetic Side:** Equivalence classes of continuous, $n$-dimensional, Frobenius-semisimple representations $\rho$ of the Weil-Deligne group $W'_F$ over $\mathbb{C}$.
- **Analytic Side:** Isomorphism classes of smooth, irreducible, admissible representations $\pi$ of the general linear group $GL_n(F)$.

This bijection, denoted $\rho \mapsto \pi(\rho)$ (or $\pi \mapsto \text{rec}(\pi)$), is not arbitrary; it is rigidly characterized by the fact that it preserves $L$-factors and epsilon factors of pairs [cite: 3, 4].

### 7.2 Preservation of Epsilon Factors
For any two representations $\pi_1$ of $GL_{n_1}(F)$ and $\pi_2$ of $GL_{n_2}(F)$, one can attach a Rankin-Selberg $L$-function $L(s, \pi_1 \times \pi_2)$ and an analytic local epsilon factor $\varepsilon(s, \pi_1 \times \pi_2, \psi)$ via the zeta integrals of Godement and Jacquet, or Jacquet, Piatetski-Shapiro, and Shalika [cite: 4, 13, 14]. 

The Local Langlands Correspondence is uniquely characterized by the property that for all $\pi_1, \pi_2$:
\[ L(s, \pi_1 \times \pi_2) = L(s, \text{rec}(\pi_1) \otimes \text{rec}(\pi_2)) \]
\[ \varepsilon(s, \pi_1 \times \pi_2, \psi) = \varepsilon(s, \text{rec}(\pi_1) \otimes \text{rec}(\pi_2), \psi) \]
where the left side involves the analytic factors of representations of $GL$, and the right side involves the Langlands-Deligne local constants for tensor products of Weil-Deligne representations [cite: 3, 4, 14].

The LLC for $GL_n$ was proven independently by Michael Harris and Richard Taylor in 2001, and by Guy Henniart in 2000 [cite: 4, 9, 16]. Harris and Taylor's proof heavily utilized the geometry of Shimura varieties at places of bad reduction, computing vanishing cycles infinitesimally to match the local and global correspondences [cite: 4]. Henniart utilized a numerical counting argument combined with global automorphic results. Both proofs are "global" in nature, embedding the local field into a global number field, because the very characterization of the correspondence relies on epsilon factors of pairs whose existence is rooted in global functional equations [cite: 16].

### 7.3 Level Zero Supercuspidal Representations
For a highly specific subset of representations—the tamely ramified (level zero) supercuspidal representations—Ian Macdonald had established a correspondence much earlier, matching representations of finite general linear groups $GL_n(k)$ to tamely ramified Weil-Deligne representations. It is a vital result that Macdonald's correspondence naturally matches the Godement-Jacquet epsilon factor $\varepsilon(\pi, \psi)$ with the arithmetic Langlands-Deligne epsilon factor $\varepsilon_0(\rho, \psi, dx)$ [cite: 9]. For such tamely ramified representations, the epsilon factor can be made fully explicit and is expressible as a product of local Gauss sums [cite: 9]. 

## 8. Godement-Jacquet Theory and Analytic Epsilon Factors

While the Galois side utilizes the Langlands-Deligne constant, the analytic side requires its own intrinsic construction of local epsilon factors. This was achieved by Roger Godement and Hervé Jacquet [cite: 9, 13, 14].

### 8.1 Zeta Integrals for GL(n)
Let $\pi$ be an irreducible admissible representation of $GL_n(F)$. Godement and Jacquet considered the space of Schwartz functions $\mathcal{S}(M_n(F))$ on the space of $n \times n$ matrices over $F$. For $\Phi \in \mathcal{S}(M_n(F))$ and a matrix coefficient $c(g)$ of $\pi$, they defined the zeta integral:
\[ Z(\Phi, s, c) = \int_{GL_n(F)} \Phi(g) | \det g |_F^s c(g) dg \]
This integral converges in a right half-plane and admits a rational extension in $q^{-s}$ [cite: 13, 14].

### 8.2 The Functional Equation
Let $\hat{\Phi}$ be the Fourier transform on $M_n(F)$ defined via the fixed additive character $\psi$. Godement and Jacquet proved the fundamental local functional equation for $GL_n$:
\[ Z(\hat{\Phi}, 1-s+\frac{n-1}{2}, \check{c}) = \gamma(s, \pi, \psi) Z(\Phi, s, c) \]
where $\check{c}(g) = c(g^{-1})$ is a matrix coefficient of the contragredient representation $\pi^\vee$ [cite: 13, 14].

Just as in Tate's 1-dimensional case, the factor $\gamma(s, \pi, \psi)$ determines the analytic epsilon factor $\varepsilon(s, \pi, \psi)$ after removing the contributions from the standard $L$-functions of $\pi$ and $\pi^\vee$. It is this analytic epsilon factor $\varepsilon(s, \pi, \psi)$ that Langlands conjectured, and Harris-Taylor/Henniart proved, exactly equals the Langlands-Deligne local constant $\varepsilon(\rho, s, \psi)$ attached to the Weil-Deligne parameter of $\pi$ [cite: 4, 9, 14].

## 9. Applications to Distinction and the Saito-Tunnell Theorem

Local epsilon factors are far more than bookkeeping devices for $L$-functions; they rigidly control the structural branching laws of group representations. One of the most famous examples of this phenomenon is the Saito-Tunnell theorem and its connection to the Jacquet-Langlands correspondence [cite: 5, 19].

### 9.1 The Jacquet-Langlands Correspondence
Let $D$ be the unique quaternion division algebra over the local field $F$. The local Jacquet-Langlands correspondence states that there is a canonical bijection between the irreducible, finite-dimensional (dimension $>1$) representations $\pi'$ of $D^\times(F)$ and the irreducible, discrete series (square-integrable) representations $\pi$ of $GL_2(F)$ [cite: 6]. 

A foundational property of this correspondence is that it preserves local epsilon factors. Specifically, for any character $\chi$ of $F^\times$, the Godement-Jacquet epsilon factor of the twisted representation matches:
\[ \varepsilon(s, \pi \otimes \chi, \psi) = \varepsilon(s, \pi' \otimes \chi, \psi) \]
Recent work by Weinstein provides a Fourier-analytic construction of this bijection where the preservation of epsilon factors is made absolutely explicit through computations on finite ring quotients of orders in $M_2(F) \times D$ [cite: 6].

### 9.2 The Dichotomy Principle and Saito-Tunnell
Let $E$ be a quadratic extension of the local field $F$. A central question in representation theory is determining whether an irreducible representation of $GL_2(F)$ or $D^\times(F)$ contains a specific character $\chi$ of $E^\times$ when restricted to $E^\times$ (which embeds into both $GL_2(F)$ and $D^\times(F)$).

The **Dichotomy Principle** states that for a discrete series representation $\pi$ of $GL_2(F)$ and its Jacquet-Langlands correspondent $\pi'$ on $D^\times(F)$, the character $\chi$ of $E^\times$ (matching the central character condition) will appear in *exactly one* of the restrictions: either in the restriction of $\pi$ or in the restriction of $\pi'$, but never both [cite: 5, 19].

The **Saito-Tunnell Theorem** [cite: 5, 19] dictates exactly which group wins this dichotomy, and the arbitrator is the local epsilon factor! Specifically, the dimension of the Hom-space is determined by:
\[ \dim_{\mathbb{C}} \text{Hom}_{E^\times}(\pi, \chi) \neq 0 \iff \varepsilon(\pi \times \text{Ind}_{W_E}^{W_F}(\chi^{-1}), 1/2) = \chi(-1) \]
If the epsilon factor evaluates to $1$ (relative to the required character parity), $\pi$ admits the linear form. If it evaluates to $-1$, the quaternion algebra correspondent $\pi'$ admits the form [cite: 5, 19].

### 9.3 Waldspurger's Global Theorem
The Saito-Tunnell theorem is the local analogue of a profound global result by Waldspurger [cite: 5, 20]. Waldspurger's theorem considers a global automorphic representation $\Pi$ of $PGL_2(\mathbb{A}_F)$ and asks whether its period integral over an embedded torus $T(\mathbb{A}_F)$ associated with a quadratic extension $E/F$ is non-zero. 

Waldspurger proved that the global period integral is non-zero if and only if:
1. The global $L$-value $L(1/2, \Pi_E)$ is non-zero.
2. At every local place $v$, the local representation $\Pi_v$ is distinguished by the local torus, a condition completely governed by the local epsilon factors $\varepsilon_v$ [cite: 5, 20].
This highlights a stunning local-global principle: the local epsilon factors act as obstruction classes that dictate global non-vanishing [cite: 21].

## 10. Trilinear Forms and Triple Product L-Functions

Building on the principles of Saito-Tunnell and Waldspurger, Dipendra Prasad famously extended the study of local epsilon factors to the domain of triple products of representations [cite: 5, 20, 22, 23, 24].

### 10.1 Prasad's Multiplicity One Theorem
Let $\pi_1, \pi_2, \pi_3$ be three irreducible admissible representations of $GL_2(F)$ such that the product of their central characters is trivial. One may form the tensor product representation $\Pi = \pi_1 \otimes \pi_2 \otimes \pi_3$ of $GL_2(F) \times GL_2(F) \times GL_2(F)$. One asks if there exists a $GL_2(F)$-invariant linear form on this triple product (where $GL_2(F)$ is embedded diagonally). 

Prasad demonstrated that the dimension of the space of such invariant linear forms:
\[ \dim_{\mathbb{C}} \text{Hom}_{GL_2(F)}(\pi_1 \otimes \pi_2 \otimes \pi_3, \mathbb{C}) \le 1 \]
Thus, multiplicity one holds [cite: 7, 22]. 

### 10.2 Triple Product Epsilon Factors
Similarly to the $GL_2$ dichotomy, there is a dichotomy between $GL_2(F)$ and the quaternion algebra $D^\times(F)$. Let $\pi_i'$ be the Jacquet-Langlands correspondents on $D^\times(F)$ (if they exist). The question of whether the invariant form lives on $GL_2(F)$ or $D^\times(F)$ is governed exclusively by the Langlands-Shahidi **triple product epsilon factor** evaluated at the central point $s=1/2$ [cite: 5, 7, 22, 24].

Since the central characters multiply to trivial, the epsilon factor is a sign:
\[ \varepsilon(1/2, \pi_1 \otimes \pi_2 \otimes \pi_3) = \pm 1 \]
Prasad's Theorem (completed by Loke for certain residual cases) asserts [cite: 7, 24]:
- If $\varepsilon(1/2, \pi_1 \otimes \pi_2 \otimes \pi_3) = +1$, the invariant trilinear form exists on $GL_2(F)$.
- If $\varepsilon(1/2, \pi_1 \otimes \pi_2 \otimes \pi_3) = -1$, the invariant trilinear form exists on $D^\times(F)$.

This elegant sign determination reveals how the Deligne-Langlands local constant intrinsically "knows" the internal geometry of the representation spaces [cite: 20]. Furthermore, Ichino's formula equates the absolute square of the global period integral of a triple product to the central value of the global triple product $L$-function, weighted by these local invariant forms [cite: 7, 20]. Venkatesh later utilized these period bounds, bounded by the local epsilon considerations, to establish subconvexity bounds for $L$-functions in certain level aspects [cite: 7].

## 11. Functoriality and Tensor Operations

A cornerstone of the Langlands program is the principle of functoriality, which conjectures that homomorphisms of $L$-groups map automorphic representations to automorphic representations while preserving $L$ and epsilon factors. The robustness of the Local Langlands Correspondence demands that it respects natural algebraic operations on the Galois side, such as taking symmetric or exterior powers [cite: 3, 9].

### 11.1 Exterior and Symmetric Squares
Let $\rho$ be a Weil-Deligne representation of dimension $n$, and let $\pi(\rho)$ be its associated $GL_n(F)$ representation under the LLC. One can form the exterior square representation $\Lambda^2 \rho$ and the symmetric square representation $\text{Sym}^2 \rho$. On the analytic side, Langlands and Shahidi (as well as Jacquet and Shalika via integral representations) defined analytic exterior square and symmetric square gamma and epsilon factors for $\pi(\rho)$ [cite: 3, 9].

A major theorem by Cogdell, Shahidi, and Tsai proves that the LLC perfectly preserves these operations locally:
\[ \varepsilon(s, \Lambda^2 \rho, \psi) = \varepsilon(s, \pi(\rho), \Lambda^2, \psi) \]
\[ \varepsilon(s, \text{Sym}^2 \rho, \psi) = \varepsilon(s, \pi(\rho), \text{Sym}^2, \psi) \]
This confirms the compatibility of the arithmetic and analytic functional equations [cite: 3]. 

### 11.2 Highly Ramified Twists and Asymptotics
The proof of this compatibility relies on a deep, robust deformation argument. A crucial step involves demonstrating the stability of the analytic gamma factor under highly ramified twists when the representation $\pi$ is supercuspidal [cite: 3]. By expressing the gamma factor as a Mellin transform of a partial Bessel function, the authors analyzed the precise asymptotics of these Bessel functions. This methodology, inspired by the theory of Shalika germs, ensures that the complex integrals mimic the algebraic stability properties of the Langlands-Deligne constants [cite: 3].

## 12. Epsilon Factors in Arithmetic Geometry

While local fields naturally arise as completions of number fields, the theory of epsilon factors extends remarkably into arithmetic geometry over fields of positive characteristic $p$, notably through the lens of $\ell$-adic cohomology and $p$-adic rigid cohomology [cite: 25, 26, 27].

### 12.1 $\ell$-adic Sheaves and Epsilon Cycles
For a smooth proper curve $X$ over a finite field $k$ of characteristic $p \neq \ell$, let $\mathcal{F}$ be an $\ell$-adic sheaf. Inspired by the Langlands program, Deligne posited that the constant appearing in the functional equation of the $L$-function of $\mathcal{F}$ factors into a product of local contributions (epsilon factors) at each closed point of the curve [cite: 25]. He famously conjectured a product formula, which was verified by Laumon in $\ell$-adic étale cohomology [cite: 25, 27].

More recently, research has refined this by studying local epsilon factors of vanishing cycles in positive characteristic, yielding a refinement of the classical Milnor formula [cite: 26]. By constructing epsilon cycles of $\ell$-adic sheaves, mathematicians have proven pullback and product formulas analogous to characteristic cycles, without ambiguity on the roots of unity [cite: 26].

### 12.2 Arithmetic $\mathcal{D}$-modules and $p$-adic Epsilon Factors
Moving away from $\ell \neq p$, one can study $p$-adic coefficients via the theory of rigid cohomology and arithmetic $\mathcal{D}$-modules [cite: 25, 27]. Let $M$ be an arithmetic $\mathcal{D}$-module on $X$. The global epsilon factor of $M$ appears in the functional equation of its $L$-function. 

The local epsilon factor of $M$ at a closed point $x \in X$ is defined up to the choice of a meromorphic differential form $\omega \neq 0$. To define it, one restricts $M$ to the complete trait $S_x$ of $X$ at $x$ [cite: 25, 27]. A monumental theorem by Marmora (2014) proved the product formula for these $p$-adic epsilon factors of arithmetic $\mathcal{D}$-modules [cite: 25, 27]. This established the analogue of the Deligne-Laumon formula in rigid cohomology, confirming a long-standing conjecture for overconvergent $F$-isocrystals [cite: 25, 27]. The proof leveraged microlocal techniques to establish a theorem of regular stationary phase for $\mathcal{D}$-modules [cite: 25, 27].

## 13. Current Research and the Quest for a Purely Local Proof

Despite the ubiquitous application of the Langlands-Deligne local constant, its foundational reliance on global methods remains a philosophical irregularity in the Langlands Program. 

### 13.1 The Global Dependency
As discussed extensively in mathematical community circles [cite: 16], all currently accepted proofs of the existence of the Langlands-Deligne epsilon factor, as well as the proofs of the Local Langlands Correspondence by Henniart and Harris-Taylor, are inherently "global." They embed the local field $F$ as a completion of a global number field, utilize global automorphic $L$-functions and Shimura varieties, and extract local data from the global product formula [cite: 2, 4, 16]. 

The question remains: *Is there a purely local proof of the Local Langlands Correspondence?* 

### 13.2 Non-Abelian Lubin-Tate Theory and Carayol's Conjecture
To have a purely local proof, one must first possess a purely local characterization of the epsilon factor and the correspondence. For one-dimensional representations (Local Class Field Theory), a purely local proof is famously achieved via Lubin-Tate formal group laws [cite: 16]. The maximal totally ramified abelian extensions of a local field are obtained by adjoining the torsion points of a formal module of height one, completely bypassing global L-functions [cite: 16].

Extrapolating this to $GL_n$, Henri Carayol conjectured the existence of a "Non-abelian Lubin-Tate theory." He posited that the Local Langlands Correspondence could be realized directly in the cohomology of deformation spaces of formal modules (now called Lubin-Tate spaces) [cite: 16]. Harris and Taylor actually utilized this geometry to prove the correspondence for supercuspidal representations, but their characterization still relied on the global epsilon factors of pairs [cite: 4, 16].

More recently, Peter Scholze's groundbreaking geometric proof of the LLC over $p$-adic fields introduced sophisticated new techniques via perfectoid spaces. While Scholze's geometric framework is profoundly local in its mechanics, the rigid characterization of the representations matched still defers to the preservation of the Langlands-Deligne local constants, whose very existence currently demands global algebraic number theory [cite: 16]. A "purely local" proof of the existence of the local epsilon factor—one that does not invoke a global number field—remains an elusive target that would conceptually revolutionize the foundations of the Langlands program.

## 14. Conclusion

The Langlands-Deligne local constant is arguably one of the most intricate and ubiquitous invariants in modern arithmetic geometry and representation theory. Born from the functional equations of global $L$-functions [cite: 1], extended locally by Tate [cite: 1], and universally generalized through Deligne's masterstroke of Brauer induction [cite: 2, 15], the local epsilon factor acts as the ultimate arithmetic scale. It balances L-functions, uniquely characterizes the Local Langlands Correspondence [cite: 3, 4], dictates representation dichotomy via the Saito-Tunnell theorem [cite: 5, 19], and controls the non-vanishing of period integrals in triple products [cite: 7, 20]. 

From the topology of the Weil-Deligne group to the geometric depths of $p$-adic $\mathcal{D}$-modules [cite: 10, 25], the epsilon factor remains a testament to the profound interconnectedness of mathematics, bridging the discrete world of Galois theory with the continuous domain of harmonic analysis.

**Sources:**
1. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-sEsJz9h7QuQnlR9xBOUMq0PlVeDYiKPLFmfjaZ8x6LJyqRQT5y2kniUC5gFlo4Z8ENX7_6JFw3IWICR_jsaWVc4zYS5N3ye3UIsvqsI8YAM9CkmTMCcwayC7nk4dBqD4INzJmNQ7s8-Rfw6CqiBpBGfCQFhfXYU_ZL0=)
2. [imperial.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSlIZTuI_dWkfHWkic3uXFWfVLwETl8fau7QzEOwE8CKU15RR6iPi2g5Plji421BlWzW4lsnDJE4vecpjxruR58n4hIBPvW7dEAbEutd0tjGX6UplP2C2ntypgRStrzrxQQfGwx-ARfGuk9fxuPE1eFK5PShQI-5mMIJOGvZpmH4nEBIx8pw==)
3. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIJBpHc9XSbDUoQ2UZAG87JwjAoCgTE34MXpOd60uGiP2e9Y-f9qIL-csAlMiUx2AQx_Alvt71rZ1KlN5PVTTXZvhPNGchDvT8bNv7PC_Qa5Wzn6uU5EzWxAOXTfKkRKHN_a8Kcvs1ydsRkQxsWXnr_hGo3T4hDX1lRw83uqFiGPS3koeuLOH_wg5YNS20Wi5216LWe0FbGQIrvZwOHh2HqvvIySARxEfVYFOFRdbz5iwecxgN-0k9TyirIRu5zPnI3ZDF5vTUSPMYKt0751w3S2JWz_zmr2Rh8FAHxDei47bog-j7p9OFofpoUg==)
4. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmqKAGDAkswVK7ln4px_pHcWyVzEfoVAkpHTU5IR6znuUDDWgp6Gxh59vMQvkB15SGvXt6Gb5j5Rrm2eEYy3OJMOhcXZFiNBkzqhpHiYIWnrhF0rBEgGrjjmDZmsAa1l3SwzeH5GS70LjiFw==)
5. [iitb.ac.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvI3JVKJuPfn-KmUbgBM6KC7RYas_a-PlkayVeI31Hz3N-ds5Xav22ZXZnts9yMieFXR7PvJch1EAv9OuBceLoPOs9EcTVKWggdbSUZp0P2YnlWQfKF9HTiVihJ5d386nr3ZA3yA==)
6. [bu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbA4NEAoAXT74AnUY7XiEXPtUIj4Zk_5I50fjrkoVHzwYt0qA-hizZ4gWmT4agPyBzuDs19G8csN6onJyaJkfS5CMYpoQ9Qpyt3oYx0B6jdaoiGxxhfui16t51yQ4tdjk3Pvs7jCI=)
7. [uni-koeln.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0JXyjzq9SVVs83e_SatoMZ7RPoa64v2AxqeihA_yLUjXKyfiSldWp2l2Xsu6JNSPwN96uInkrCY7HdiTFys3tLv3T_0PK_BHDL3TOCCKyt98rhHtuc55lVfMf6FkkG1MhmHoSXWLot75wzSdTWXrk)
8. [u-tokyo.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkn71sm33QjWjS5TFwwKxH1JbPWsRNpGse1gkmhXx9g83viEK556awuJFACdwt2YB-Geh4-YUzavIh46BLpIHGFGzVD6OZ9cK0S0-m_-ToeXAIkd5jW6cTQ8pDZ_HbSnHfZ4VHDhz8_oWwpQ==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGivHviZr2FFoX-k3yFGgls4tPP7QjhcELdQ2hNY3gPY159RFmE9CNq83z8urvfvKHeXqmjCtNxoXMC_XtR-X53mZuDkewevw9bpKjVFMArWUhoXVvJ)
10. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_inI1s1enjnWSk4bw_R3Kh5QHilWLalxaMByx-ONitAkRN31OqrVxIMCtfsEMzRXDJOlkh3ax9Q1kbanwM9a4UXCXNVAdwHn6-S58KEJTa8o8pGjX8VBAuoei_fcVWzf9i7wHKL_heXMKTo2DIg==)
11. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUyeGOU66ZBUpJG0Z459mIz3fnGMhBgd4S4jVxH-uGh-LgWWjzdfMyxyM9iR-JZtE_EhTCW1g1dhXlHr5ruYIuLYAg8cyIFXUMj5wDcFtWahZKR3ICM386V6zNXQHU2mo9UUk16lCv5D1_9LpVHLsjhdtK8-xOP6OZzbjLwNRV6apMj2zavUtbYtbu5oT8)
12. [srcf.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOivwYAzYS9uCmgk4atvkcfreVZi4ralTkC0-hUIbAy1n6tcC17QeuRXcx455LAcLkfESSIWxB8sH2e095W2lAXFwdWh-cP9e0L75n9uZuf6j6mc_4ZqYrCfIkCpyePuVVN4iHfvFAXL-WC3PUgP6AM5Ofr3pzNwVgrBmjE85WyKs=)
13. [uni-bonn.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFypgrtjWmiJ7GMbVJQJ1nr6lfhWsAwz88jcEzzz-5hfh3gr7_1okx4jppZRSbUu4vQJMr8m2i2DUCclVeevdrDS0e3muuMXIiD7_WILMTaZoZ2EHmARLrWpjS5qG4tjJ_EXphCiJlKR6AynygNOs5_MusGuN5-SPYhUoyDUpvX8-8U1ZGlEQxnG56KTFvP80h4qPwEch3Zq4dhK-wxtYg1x7qUinwARzJR4se-D-HhoUjC21Ht-EeBACg=)
14. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAo0HW6u3HeHOTnorpLY8G-79XliUty2CphSamEdbgRJDmUpYkRk_p3BpPunqWXsW6waTFlo-mVyJQmnn2JKwPnnq_zbCZU9U5r-iPM5nMh3p5-74KPRe4JwpSlteqAhdTt8M4Kzwq9XlYfvDzRhbmp6qvlq-ltdpjRuHhiA==)
15. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbFO5qUEyP3nJ31JkrUHlQSFRVEsArnHYMXWOta1WtaiNOTyuOvlzO2ir3vYdJwEBBTvR1GXBA-a8CGkq8_p-5Fg02DU7YTeXqsfJ5MMAFIcUW34-KrIRo4tTexf0r0Sbaw66kAXfmQBnUswiyMpF_-FUHeDGZQJrV_PlzI_cIdArWrnd1UT9TeE5eNozMb1FT1SlaVy_x6OzQx1keh_kFglH6eq0Xky90EXlG7Fx93mF-64OEXdUSFH-ZzpoHI9dyEoRMc7zvbX9IcokS_IoXqDYDkmBZm693NZ6e3J7v_zlDPza9h5Q=)
16. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLaZa0TfVqiDAbGIt6hf26tuz7HlpMxgo_wdn7FqpPzILFD7jfkyFiFJ_ZIXQeCrCKZhDiLv2FFrqcc3G0leb7yGhpaoUUvDEAExHytV9gOMjfLJQeHr9f-i9asqEVx39D-7se4DJ1Q_Q6-kqoKp6LhRqw96Ab_lxYszhDqmvBx9JV5A==)
17. [proquest.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxkXrc6EIvhhB-UMJAP3160D82z4UgiZZH9YZ5mlw06fCcq6tA9vU_a_4Lq6uz-hd_GwL6qT8BlX5VZJN34L0tOWUVoa68MTuX0lls4FdvWofHJ-zBZzhtQtEKZ3g9m1jO8uQfgIjLdZ-yaUNr_pTa1RoFarnsV6-ugjq7bifZDsiR6bMVZQV6-21InL9zdhg5WaS6ms0b6ICLoBzdYDZofsk=)
18. [purdue.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7WTx0vBHph7crzTHxNf07T1TKF1SE_IIKUA4AMJirpC1JTE9q6gDTMXhTQkFq_Xv9geZwhePl7TNJ6qa_a7SCkzsJhzw4EDxFlQa0F-3G-NSvxm9MdN89VqrBIn9V8hgO7dtCWE8_pYiCw61YzxnUwSAAIB0omm53qLtybP74xrsqxg86wv6HuRHLfVFERfYq7wOwbJl7Jj9k3Jkt8-laoxT3xuI=)
19. [iitb.ac.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmDcS6v1-HsA5RJRlBOvTtzF5Hg9JIoj2bUM6vDTJex1fPBJl6X3SknHhfw9iVxtvDf5wGhji4PqL21UtQidl4MtVJQ6c2ct9VnkmM019AUiHOC9yWn10-oSi-j5zVM8V_5noyIJ0=)
20. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvaKLaoPjFN7MTy5bfSNOkenipuVpawlsFruXy3-VddOGAqrkCd6CVAJcf1y7Gd2Dg9uTuudHEbBrZRDPindBhDky8mZ-t_DjZLUqPjjZKhYUMQb0UZdg5d-RQ57YLct1QDCmjbWbVKjg39VfrsBeRG4AN8rj6)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGMBgdK6GRB4y8CwsqmCjRVtVz5f5bEaQoYGNI3tvyQX5huMUOGXS_kiOE5FU_Uvl2-QBb8ZDPWSAl-CDXayLUjfwozjQTIUqgojwvz7NGQ590I-k=)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5X60mvrdHCqx9jWIjZbY5ANO1YOwuJ5D1UM1qfYGmsQF4LsTbX4UdWsXkMgbsgjS_5D7gS58RcjTVY4MKhkqI1f9U0x1k-Vqw52n3jOTP7sD0eOr50mw=)
23. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGO20aaVI42dDS2nJzyJAkuvQ89qCQO2oxgrUb_Dgsu0K6gbDQb-s_XtgrCC3M4xgC8ho_BLPY1gBC9PhNJtKqAN7cn5kQZsf7UKp8mDBhKLQGps_dpZqmkxpk=)
24. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWK6Vp2dZVUx1gLmHoliGlTzPIKY3UQWyhpgTQwcmDXWEdXOIg_2ccWY9jPtlpgNILKHolL3yH4HvFJoAG_jMQta7fHCaeXYpCyk9vilhiShsnQI30Z2fiW9oNhW5vX-dl-g==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE89RfQfJAgwP8jIpN6H0qlVTjLpSckMK_7-6BQUiCmc3-mw62aOkm07rJbNrH7_N1npK2VBLNUhbHP4M5nISqV74CUWK0dHmgPBZTJaL57FkM1KyE=)
26. [u-tokyo.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVW7-B5I2qCQpEHakbCOHEZYiZ0_2s54NG1zA-pXWhq6YbE8OZOIatAd0yZ5k_CU0g8giKqUav9t7Il0H8NLbZoz29oSVoEC9vImYrvA1OLj94WlbmhySsvDvqHrZeWWNvbRsOeXDiCtuh9OdrtaQC8vzi0-eCxrh9Q8jrR8TBKJF7v2A=)
27. [unistra.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTke2x1FNobhyoFCEtymYDQ4e707qzB9g0-0VHhIHNXCJoAmmEUcKAu6lzZpbrLnnnRn94izVjlm6SKTR4Mg5I9ZqM1COQKhnyMvDOpAvZ_ZRCH3_XMozP24NpgrrRy2UHZOl0CitoIuAK4_A=)

