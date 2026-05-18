# T#29 Regularity of minimal apolar schemes (reg(X) <= d)

**Pythia queue id:** 21
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdkMzBMYXViTUFyZk0tc0FQalpfaWlRVRIXZDMwTGF1Yk1BcmZNLXNBUGpaX2lpUVU
**Elapsed:** 371s
**Completed at:** 2026-05-18T21:04:43.296841+00:00

---

# The Regularity of Minimal Apolar Schemes: Castelnuovo-Mumford Bounds and Tensor Decompositions

*   **Key Point 1:** The study of the Castelnuovo-Mumford regularity ($reg(X)$) of minimal apolar schemes is a central problem in algebraic geometry, fundamentally connected to symmetric tensor decomposition and the Waring problem.
*   **Key Point 2:** A prevailing hypothesis in the field—often investigated as whether $reg(X) \le d$ for a minimal scheme $X$ apolar to a degree-$d$ homogeneous polynomial—has been partially resolved, revealing a nuanced mathematical reality.
*   **Key Point 3:** Recent research suggests that mere irredundancy of an apolar scheme does not guarantee $d$-regularity; however, specific minimal configurations, such as tangential decompositions of minimal length, are demonstrably $d$-regular.
*   **Key Point 4:** Evidence indicates that if the cactus rank (the minimal length of an apolar scheme) of a degree-$d$ form is bounded by $2d + 1$, then non-redundancy is sufficient to ensure $d$-regularity.
*   **Key Point 5:** While the specific identifier "T#29" (or Theorem 29) may refer to distinct results in related fields (such as skew-symmetric tensor decompositions), the core inquiry surrounding $reg(X) \le d$ is robustly addressed through recent propositions on generalized additive decompositions (GADs).

**Understanding Apolarity**
At its core, apolarity is a mathematical relationship between two types of algebraic objects: homogeneous polynomials (which can be thought of as symmetric tensors) and differential operators. When a set of differential operators completely "annihilates" a polynomial (reduces it to zero), they form an apolar ideal. Geometrically, this ideal defines a shape—a zero-dimensional scheme—that essentially represents a specific way to decompose the original polynomial into simpler building blocks.

**The Regularity Problem**
Castelnuovo-Mumford regularity is a measure of the "complexity" of these geometric schemes. Specifically, determining if a scheme $X$ is $d$-regular ($reg(X) \le d$) means asking whether the geometric properties of the scheme stabilize relatively early (by degree $d$). For mathematicians and computer scientists, knowing that $reg(X) \le d$ is incredibly valuable because it limits the search space required to compute tensor decompositions, directly impacting the efficiency of symbolic algorithms used in machine learning and complexity theory.

**Recent Breakthroughs and Complexities**
It seems likely that for many "well-behaved" schemes, this regularity bound holds true. However, mathematicians have recently discovered counterexamples showing that just because a scheme has no unnecessary components (is "irredundant"), it doesn't automatically mean it is $d$-regular. The bound is mathematically guaranteed only under stricter conditions of minimality, such as when the scheme has the absolute minimum possible length (cactus rank) and falls within certain size thresholds, or when it represents specific types of tangential structures.

---

## 1. Introduction to Symmetric Tensors and the Waring Problem

The exploration of minimal apolar schemes and their regularity is deeply embedded within a longstanding mathematical tradition that intersects classical algebraic geometry, commutative algebra, and modern complexity theory [cite: 1, 2]. The fundamental object of study in this domain is the homogeneous polynomial, which equivalently represents a symmetric tensor. 

Let $\mathbb{K}$ be an algebraically closed field of characteristic zero. Consider the standard graded polynomial ring $\mathcal{S} = \mathbb{K}[X_0, \dots, X_n] = \bigoplus_{d \in \mathbb{N}} \mathcal{S}_d$, where $\mathcal{S}_d$ denotes the $\mathbb{K}$-vector space of homogeneous polynomials (forms) of degree $d$ [cite: 2]. In the context of algebraic geometry, questions regarding the decomposition of such forms into sums of simpler forms, such as $d$-th powers of linear forms, trace back to the classical Waring problem for polynomials [cite: 1, 2].

The Waring problem asks for the minimum number of linear forms $L_i$ such that a given homogeneous polynomial $F \in \mathcal{S}_d$ can be expressed as:
\[ F = \sum_{i=1}^r c_i L_i^d \]
where $c_i \in \mathbb{K}$. The minimum number $r$ for which such a decomposition exists is called the **Waring rank** of $F$, denoted $R(F)$ [cite: 2, 3]. Finding such decompositions and understanding the geometric spaces that parameterize them—known as secant varieties of Veronese varieties—remains a highly active area of research [cite: 1, 2].

However, not all polynomials admit a unique or easily computable Waring decomposition. To navigate these complexities, mathematicians utilize **apolarity theory**, which translates the problem of additive decomposition into the study of ideals of points contained within the annihilator of $F$ under a specific algebraic action [cite: 2, 3].

## 2. Apolarity Theory and the Apolarity Lemma

Apolarity theory provides the critical bridge between the algebraic decomposition of a polynomial and the geometry of zero-dimensional schemes [cite: 2, 3]. To formalize this, one introduces a dual ring, $\mathcal{T} = \mathbb{K}[\partial_0, \dots, \partial_n]$, which acts on $\mathcal{S}$ via differentiation [cite: 3, 4]. The ring $\mathcal{T}$ can be viewed as the homogeneous coordinate ring of the dual projective space $\mathbb{P}^n$, and simultaneously as the ring of differential operators with constant coefficients acting on $\mathcal{S}$ [cite: 3, 4].

For any form $F \in \mathcal{S}_d$, the **apolar ideal** (or annihilator ideal) is defined as:
\[ Ann(F) = \{ D \in \mathcal{T} \mid D \circ F = 0 \} \]
where $\circ$ denotes the apolarity action [cite: 3, 5]. This ideal is a homogeneous ideal in $\mathcal{T}$.

A fundamental theorem in this area is the **Apolarity Lemma**, which establishes the equivalence between the existence of a specific type of decomposition of $F$ and the existence of a particular zero-dimensional scheme whose defining ideal is contained within $Ann(F)$ [cite: 2, 4]. 

Specifically, a zero-dimensional scheme $X \subset \mathbb{P}^n$ is said to be **apolar** to $F$ if its defining ideal $I_X$ is a subideal of the annihilator of $F$, meaning $I_X \subset Ann(F)$ [cite: 4, 6]. According to the classical Apolarity Lemma, finding a Waring decomposition of $F$ of length $r$ is equivalent to finding a reduced zero-dimensional scheme $X$ (a set of $r$ distinct points) such that $X$ is apolar to $F$ [cite: 2, 3].

However, the Apolarity Lemma extends beyond reduced schemes (sets of distinct points) to encompass non-reduced schemes, which correspond to more complex decompositions known as Generalized Additive Decompositions (GADs) [cite: 2, 4].

## 3. Generalized Additive Decompositions (GADs)

While Waring decompositions restrict the addenda to pure $d$-th powers of linear forms, Generalized Additive Decompositions (GADs) allow for a broader class of summands [cite: 1, 2]. A GAD of a $d$-homogeneous polynomial $F$ is an expression that may include polynomial components with specific structural properties, fundamentally linked to the theory developed by Iarrobino and Kanev [cite: 4, 7].

For example, a scheme associated with a GAD may involve a combination of distinct points and non-reduced structures (like "fat points") [cite: 4, 6]. The length (or degree) of the zero-dimensional scheme $X$ associated with a GAD provides a notion of length for the decomposition itself [cite: 6]. 

Important classes of GADs include:
1.  **Waring Decompositions:** Corresponding to reduced schemes (distinct points) [cite: 6].
2.  **Tangential Decompositions:** Decompositions associated with schemes of degree 2 [cite: 6].
3.  **Trivial Decompositions:** The trivial expression $F = F$ itself is formally considered a GAD [cite: 6].

The relationship between the schemes apolar to $F$ and the schemes associated with GADs for $F$ is a subject of intense scrutiny [cite: 6]. It is generally established that if $X$ is a scheme associated with a GAD for $F$, then $X$ is apolar to $F$ [cite: 6]. However, the converse is not universally true; there exist schemes apolar to $F$ that are not induced by any GAD of $F$, representing a profound layer of complexity in the geometry of tensors [cite: 6]. 

Furthermore, if $X$ is a scheme apolar to $F$, a partial converse exists: there is an extension $F_{ext}$ of $F$ (an antiderivative with respect to a differential operator) such that $X$ is associated with a GAD for $F_{ext}$ [cite: 6].

## 4. Minimality: Rank, Cactus Rank, and Irredundancy

When analyzing apolar schemes, distinguishing between different forms of "minimality" is crucial [cite: 2].

*   **Waring Rank ($R(F)$):** The minimal number of points in a reduced scheme apolar to $F$ [cite: 2, 3].
*   **Cactus Rank ($cr(F)$):** The minimum degree (or length) of an arbitrary (possibly non-reduced) zero-dimensional scheme $X$ apolar to $F$ [cite: 4, 7]. Such a scheme of minimal length is often termed a **cactus scheme** [cite: 4, 5].
*   **Irredundancy (Non-redundancy):** A scheme $X$ apolar to $F$ is considered irredundant (or non-redundant) if no proper subscheme $X' \subsetneq X$ is also apolar to $F$ [cite: 3, 6]. 
*   **Minimal Scheme:** In rigorous modern definitions, a scheme is termed "minimal" if its length precisely equals the cactus rank of $F$, meaning it is minimal by length [cite: 6].

It is vital to recognize that an irredundant scheme is minimal by inclusion, but not necessarily minimal by length (cactus rank). This distinction plays a pivotal role in the regularity bounds of these schemes [cite: 1].

## 5. Castelnuovo-Mumford Regularity and Hilbert Functions

To quantify the complexity and the threshold at which the geometric properties of a zero-dimensional scheme stabilize, algebraic geometers rely on the **Hilbert function** and **Castelnuovo-Mumford regularity** [cite: 3, 6].

Let $X$ be a finite, zero-dimensional scheme (such as a set of points) in projective space. The Hilbert function $h_X(t)$ measures the dimension of the homogeneous components of the coordinate ring of $X$. For a zero-dimensional scheme, the Hilbert function $h_X(t)$ is strictly increasing with respect to the degree $t$ until it reaches a plateau, at which point it stabilizes exactly at the value of the length (or degree) of the scheme, denoted $\#X$ [cite: 3, 4].

The **Castelnuovo-Mumford regularity** of $X$, denoted $reg(X)$, is defined as the first degree after the one where the Hilbert function $h_X$ reaches its stable, maximum value [cite: 3, 4]. Formally:
\[ reg(X) = \min \{ \tau > 0 : h_X(\tau) = h_X(\tau - 1) \} \]
[cite: 3]. Consequently, if $X$ is a set of $r$ reduced points, it is a known bound that $reg(X) \le \#X$ [cite: 3]. 

A scheme $X$ is said to be **$d$-regular** if $reg(X) \le d$ [cite: 1, 2]. The condition $reg(X) \le d$ serves as an essential parameter controlling the algebraic relations of the scheme [cite: 6]. For instance, if $X$ is a scheme satisfying $reg(X) \le d$, then $X$ is apolar to $F \in \mathcal{S}_d$ if and only if $X$ contains a subscheme $X'$ that is strictly associated with a GAD for $F$ [cite: 6]. 

### The Computational Importance of $reg(X) \le d$

From a complexity theory perspective, predicting the regularity of minimal apolar schemes is exceptionally valuable [cite: 1, 2]. The knowledge that a scheme is $d$-regular drastically reduces the search space for generating elements of the ideal $I_X$ [cite: 1, 2]. If $reg(X) \le d$, symbolic algorithms designed to compute tensor ranks and find minimal decompositions can operate with substantially improved efficiency [cite: 2]. The Castelnuovo-Mumford regularity bounds the maximal degree of any minimal set of generators of the ideal, thereby bounding the computational cost of effectively producing such minimal decompositions [cite: 7, 8].

## 6. Open Problems and the $d$-Regularity Hypothesis

The question of whether minimal apolar schemes are fundamentally bounded by the degree of the polynomial they annihilate has been formalized in recent literature as a set of prominent open problems. In 2023, Fulvio Gesmundo codified these inquiries in his comprehensive survey of open problems in the geometry of tensors [cite: 6].

**Gesmundo's Problem 5:** Determine the maximum possible value of $reg(X)$ for the regularity of an irredundant scheme apolar to a form $f \in \mathcal{S}_d$ [cite: 6]. This problem stems from the observation that the simple bound $reg(X) \le d$ does not universally hold for all irredundant apolar schemes [cite: 6]. 

**Gesmundo's Problem 6:** For $f \in \mathcal{S}_d$, let $X$ be the scheme associated to a GAD of minimal length. Is it true that $reg(X) \le d$? [cite: 6].

These problems highlight the delicate boundary between a scheme being merely irredundant (minimal by inclusion) and possessing a minimal GAD length. As Gesmundo noted, schemes associated with certain particular GADs are known to be unconditionally regular in degree $d$. For instance, reduced schemes (associated with traditional Waring decompositions) and schemes of degree 2 (associated with tangential decompositions) natively satisfy this regularity constraint [cite: 6]. However, the broader general case remained largely obscured.

## 7. Recent Breakthroughs: Resolving the Regularity Bounds

Significant advancements in answering these open questions were achieved in a 2024 paper by Alessandra Bernardi, Alessandro Oneto, and Daniele Taufer, titled "On schemes evinced by generalized additive decompositions and their regularity" [cite: 1, 9]. Their work rigorously investigates the regularity of 0-dimensional schemes apolar to a degree-$d$ form $F$, explicitly focusing on varying minimality conditions [cite: 1, 2].

### 7.1 The Failure of Irredundancy to Guarantee $d$-Regularity

A paramount result established by Bernardi, Oneto, and Taufer is the definitive proof that **irredundancy alone is insufficient to guarantee $d$-regularity** [cite: 1]. They demonstrate that irredundant schemes to a $d$-homogeneous form $F$ need not be $d$-regular unless they are evinced by highly specific, special GADs of $F$ [cite: 1, 2].

To substantiate this, the authors presented explicit counterexamples—specifically, Examples 5.8 and 5.10 in their manuscript [cite: 1, 2]. These examples construct degree-$d$ homogeneous polynomials that admit an apolar scheme which is strictly irredundant but explicitly fails to be $d$-regular [cite: 1, 2]. 

For instance, their research reveals specific polynomials (e.g., in degree 3 or 4) where the Hilbert series of the irredundant scheme extends beyond the degree $d$ before stabilizing [cite: 5]. A specific presentation by Taufer highlights a polynomial of degree 4 where an irredundant scheme yields a Hilbert series $[1, 3, 6, 10, 11, 12, 12, \dots]$, indicating that the regularity is greater than 4, proving that the scheme is not regular in degree 4 [cite: 5].

Crucially, in evaluating these counterexamples, the authors noted that while the schemes were minimal by inclusion (irredundant), they were **not minimal by length** (they did not achieve the cactus rank) [cite: 1]. Example 5.10 directly answers an open question originating from a prior work ([BT20, Remark 5.4]), proving unequivocally that the condition of having minimal length is absolutely essential, and that irredundancy is simply not a strong enough condition [cite: 2].

Furthermore, Proposition 5.2 of their work proves a structural limitation: the addenda constituting a GAD evincing an irredundant scheme $Z$ may never appear in its inverse systems [cite: 1]. 

### 7.2 Positive Bounds: Tangential Decompositions and Cactus Rank

Despite the failure of the general irredundant case, Bernardi, Oneto, and Taufer succeeded in proving $d$-regularity for several critical classes of minimal schemes.

**Proposition 5.9 (Tangential Decompositions):** The authors proved that **tangential decompositions of minimal length are always $d$-regular** [cite: 1, 2]. A tangential decomposition corresponds to a scheme composed of elements of degree 2 (often visualized as points with tangent vectors). If such a scheme achieves the minimal possible length for the polynomial $F$, it is guaranteed to satisfy $reg(X) \le d$ [cite: 1, 2]. This rigorously confirms a special case of the overarching hypothesis and provides a robust theoretical foundation for algorithms processing minimal tangential ranks.

**Proposition 5.12 (The $2d+1$ Bound):** Perhaps the most sweeping positive result is the establishment of a numeric boundary based on the cactus rank. The authors demonstrate that if the cactus rank (the minimal length of any apolar scheme) of a degree-$d$ form is less than or equal to $2d + 1$, then the weaker condition of **non-redundancy is actually enough to guarantee $d$-regularity** [cite: 2]. 

Consequently, as a direct corollary of Proposition 5.12, **all schemes of minimal length apolar to degree-$d$ forms with a length smaller than or equal to $2d + 1$ are unconditionally $d$-regular** [cite: 1, 2]. This provides a massive, easily checkable criterion for mathematicians and computer scientists: if the apolar scheme is relatively small compared to the degree of the polynomial, its complexity is strictly bounded by $d$.

**Proposition 5.3 (Independent Linear Forms):** Additionally, the authors mapped out conditions based on the linear forms driving the GAD. Proposition 5.3 guarantees $d$-regularity for schemes evinced by GADs under the condition that the underlying linear forms $L_i$ are linearly independent, and their associated multiplicities $k_i$ are sufficiently small, independent of whether the scheme itself achieves absolute minimality [cite: 2].

### 7.3 Inverse Systems and Local GADs

Recent advancements have also focused on localizing these problems. In the study of local GADs, researchers leverage Macaulay's correspondence to compute the length of a scheme evinced by a local GAD by analyzing the dimension of symbolic inverse systems [cite: 7]. The minimal length of a local scheme apolar to a given $F$ is referred to as the local cactus rank [cite: 7]. Interestingly, the local cactus rank of $F$ does not necessarily need to be evinced by a GAD of $F$ itself; if a scheme is an irredundant local apolar scheme, it may be locally defined by the annihilator of a different polynomial whose degree-$d$ tail matches the original form [cite: 7]. This further underscores the complexity of bounding the regularity, as the local cactus rank may actually be evinced by a GAD of a polynomial of degree $d' > d$ [cite: 7].

## 8. The Ambiguity of "T#29": Skew-Symmetric Tensors and Curves

The specific user query included the designation `"T#29"`. In the landscape of algebraic geometry and tensor analysis, alphanumeric codes like "T#29" usually refer to a specific theorem numbered 29 in a foundational text, a specific chemistry temperature variable (e.g., $T=29^\circ$C [cite: 10, 11]), or potentially a reference to skew-symmetric tensors.

While the primary literature concerning $reg(X) \le d$ for symmetric apolar schemes relies on Propositions (e.g., Propositions 5.9 and 5.12 by Bernardi et al. [cite: 2]), there exists a notable **Theorem 29** in the closely adjacent field of skew-symmetric tensor decomposition, authored by Gesmundo and colleagues [cite: 12, 13]. 

In their paper "Skew-Symmetric Tensor Decomposition," Gesmundo et al. introduce the "skew apolarity lemma" [cite: 12, 13]. They formulate a skew-symmetric analog to the ideal of points and the standard apolarity action. The apolarity action for a skew-symmetric tensor involves the interior product (or contraction) operating on exterior algebras rather than polynomial rings [cite: 12, 13]. 

**Theorem 29** in that context states: Let $t \in \wedge^3 \mathbb{C}^8$ be a skew-symmetric tensor with 8 essential variables. Then the skew-symmetric rank of $t$ is exactly 4, except in a few highly specific exceptional cases (such as when $t$ belongs to specific orbital types like type XVI) [cite: 12, 13]. While this theorem is a cornerstone result for computing minimal decompositions of tri-tensors in exterior algebras, it structurally differs from the Castelnuovo-Mumford regularity bounds of symmetric polynomial apolar schemes, though both fall under the broad umbrella of tensor decomposition geometry.

Additionally, another text references a "Theorem 29" regarding the properties of a smooth curve $X$ of genus $g$ and degree $d$ [cite: 14]. However, the most direct and scientifically accurate resolution to the core parameters of the query—the regularity of minimal apolar schemes and the boundary $reg(X) \le d$—resides in the synthesis of Gesmundo's Open Problems and the decisive proofs offered by Bernardi, Oneto, and Taufer [cite: 1, 9].

## 9. Computational Implementations and Machine Learning

The theoretical bounds on $reg(X)$ are not merely abstract topological curiosities; they have immediate, practical applications in algorithmic design. Tensor decompositions are heavily utilized in machine learning, statistics (e.g., recovering parameters of Gaussian mixtures from moment tensors), and signal processing [cite: 15]. 

The identification of multilinear models relies on algorithms that can symbolically decompose symmetric tensors. If a tensor's apolar scheme is known to be $d$-regular, an algorithm can safely truncate its search for ideal generators at degree $d$, preventing infinite loops and combinatorial explosions in memory usage [cite: 1, 2]. Researchers have implemented these apolarity functions, natural apolar schemes, and schemes evinced by GADs in computational algebra systems like Magma and Macaulay2 to test these bounds dynamically [cite: 7, 16]. 

When algorithms attempt to compute the rank and minimal decomposition of polynomials, bounding the Castelnuovo-Mumford regularity dictates the absolute computational complexity of generating the algebraic varieties formed by the parametrized entries of the tensors [cite: 2, 7].

## 10. Conclusion and Future Directions

The mathematical inquiry into the regularity of minimal apolar schemes represents a vibrant intersection of commutative algebra and complexity theory. The hypothesis that $reg(X) \le d$ for a minimal scheme $X$ apolar to a degree-$d$ polynomial serves as a critical dividing line between computationally tractable decompositions and highly complex, irregular geometric structures.

Through the rigorous work of mathematicians like Bernardi, Oneto, Taufer, and Gesmundo, the mathematical community now understands that mere irredundancy is a trap—it is an insufficient condition that allows for wildly irregular schemes that exceed the degree $d$ bound [cite: 1]. However, absolute minimality, particularly through tangential decompositions or schemes constrained by the cactus rank bound of $2d + 1$, guarantees the stabilizing behavior of the Hilbert function by degree $d$ [cite: 1, 2].

Future research in this domain will likely focus on expanding the $2d + 1$ boundary, investigating the exact geometric nature of the counterexamples that break the regularity bound, and translating these rigorous algebraic bounds into optimized code for tensor network varieties and machine learning models relying on Gaussian moment tensors [cite: 6, 17]. The resolution of these regularity bounds continues to unravel the profound and subtle geometry underlying algebraic forms.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjMoumM5YpS14bBT4NGTMvgLBssoatPWkQswWEklGvoKB-EkA-QiAZbYJACOFnWnVWBPCnVJm8ONqEkamgEuhblVh2HXjaylEEISm0NHuD1vEKCHNPuw==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF56LrS8tZojG_LOny3VXxX4xASt-_LWJBAq_vKDXuxi07xtDISPPbdmEBAPIB71VUuiCpyj4QHfRXMyBoMn2-thj4SApa4-xJJ4anYE1BWkmnlWd9erjuPuA==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH89WYZhSj_nzLR-_ZGDC28un6_L3uBMAeLSods-9kMBLwutYGIHFFELMt7o8929wU9LP3YpzNITgWVLFxyf77ZRJnUEP-_XSOKTHcrKjmGRAn_WjnT2A==)
4. [puremath.no](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFC9Jbvd7Y42CQ63AwouzLYhC2cGzeT4andleTdzHnpyEXnZ387SMv27emIZxMzsxC5gQmydja6oy8u9oZ8g1ndn-MeUXyj3wA5OFu3ZZTK64z05zX78UmxlEG5PxFOWp29lN5M_psCqas4DIVD4JMKI5rKVZYASH-bMw==)
5. [mimuw.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgqc8ii9s3m3dE3hPEkMdLPwBdFc30PoCZcQWGMqZPnmhU8TAwd0RCuxwSC-gU2Nree6Vb1wyVpDUlnIinJvaf_1Aixe5R1QGcqaSQ8QYI2b8dLdaiYb2G64fauGbRtVXPlJ-Kef3WomytUsobcJnqJZHnCIhEOQPYW9hb)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaA79ADT_Zr0WngIVs9twbq427u9iOQDODhPhSJ5o8KcTB2qGG-L2Cbg3V1GTpg0tEdhQkNK0LIkBu9fJ2aN3Lan2v7GvIibFFgKNFL29mWs8Z-dN-nw==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1XTwVHX-0Sc3zZ3fwM7bbrTaxWvj-vv0MYVav4EWE7SPOvAFaMUuPQrKhgssK8WwR2aTgm8T13EkrLPvF1wgSxk9DVvVQgIMW-pUsHtjTgOHSSh4Hqig2Dg==)
8. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWKu_hLKiMnybeddVuwuaCRUSLs0qk2FLyDe5a0jDzQBMzngFudtJ8k9AxWIcrKk9nFcYk8gqtrW1JpMIznMaG6TooZM-vPBS4OmWPl9bkMiUwgT-pxGSmfXmq36UFkN_Wx5NdlJI18UPY7SeNBaNtarKbHxA=)
9. [unitn.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYzcfjAyKbfzMCVQ7ge4UOpbR7COcUjnWYil7riF66icS6mjkezXwYHONrB-XpoHL3wob6eAY6LEprstV74ZBFJclAD7nLFBVOYbKBhhNDLpnAJbLEadC9HSBWbJmptQ==)
10. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGG4xGXEYJij9Fo5IWN7H7tL9KHzDH9KyAU5qyNVwNTYPxcIVriLt8WtREuBukWWIOp7nV0ld4oBotRPST4nhFQo_x-zZpSoCXK3QEF4hRQBDtr_Q6YtHLfUDWPEW_b74utYLgStTNTbqQshvnufFZcD1B9B6GeW0l1SOJm_R-o3bCvEvAxi--PZfhIZJHrbeGKPksalP5g0ek=)
11. [acs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWycaL3d3VjqiymIGd_xqqIQXyQvIlVxGNj5DTbeijs2R6GyeE8unxDC3K2VtlUxo8NzzkFD4SwhU1F1WFUuoVtzcvmxNBINY5p1PWzOSuwP722Jw38bvBvqXstwoFtur8RJMyPjCft2GrFg==)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBHVFWTcXjcX99e75zw7sBuW8lAG2oGi7IQtBqSYG0LtetxTanMPW0RNufhsPs1R1URIXUvqkNT41CxkDO4Du76AstpGO-21C3hVn_zvTzkEp8nYGn0GSMRCNRMGG98b1Qq9owqqrs-ry_Ybo3SZvJmbB85bhcic3ZgRqlAeXBGPhGIM29hj4vZnMm2A==)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiFD8FdYOVIolABTfIpLCe8jJHzw7Lw6gjAXBRPXfuVy_VCmaVQ_BFfc077caA4lqPw3TDmSvagRLEg4ojykj0NseCV6X-pSgheaGiBaQIUWYt1VBN_VQEsEYLGRTVjHQOp7YQvihwLQTR0KLYrKr5B56ejvYgqUsUWpZZIYHIBmAoQ7jqo2u0scEVMg==)
14. [polito.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZR6WJak0mnHVrKP42cbQ6TSSlhZTP6ZECsB-PW8cPWvVJBDUpUk3fIoENzud2nZ7nJ3iyMASeylr2x_t7Ys2-tQkCVq9Dbta509AymcC44q5Gfbfq-S9_pCYCSyUkI0IHku6XdN09p3IczRUcI5lfRg==)
15. [mimuw.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzx42JvMCcI0GFauaSVstn5uZvFnCFZCy5YqrVQpFz_hbGzp_NriimXv17GvFLcxSeXdaTTR_XjuGBFV_nGSDuyqERvGXRouEiaqVR2yaIIK0dLWH0IFv4SOnAHPtCRbxmVZHk9gAuWut2k-0JDlost15PKeKuJWnlTEbrYhJP2F8BuXT-XXA32nQyA3WLRv5TokwAeDNuZ5ycOtc9AbA=)
16. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH596jRAD_g6VNb9MPiemuQh-YOk2yEb1zlccomuqW_1Ps0P9ihQIP8Q5tJ63UO-ErXAwUkVWzoJeKI8L8YwGZV0pYz42icnHBAgqLNooVM26nk_YbHOI8gIahwbXj6ChqKZiOKSg==)
17. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0Ie8ARCYijLPbXMRSKmcDFvnsy4iQFuvCVky8D1ypayAo55phMvJ9DcKZ_fGLNu1m1qgEeRbQtUKaXophsqkQlsUvpVpJHy5SUw28LFtH0JGYmu2dfDUsl8yArmHl11s2lPyBZYGHTQkfiwGbOTl3W528KKZ6gG0B)

