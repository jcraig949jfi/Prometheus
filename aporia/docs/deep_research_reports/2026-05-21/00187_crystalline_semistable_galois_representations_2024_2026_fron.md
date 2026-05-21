# Crystalline / semistable Galois representations 2024-2026 frontier

**Pythia queue id:** 187
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdJajhQYXZqNk5NZlJfdU1QNGRLTG1ROBIXSWo4UGF2ajZOTWZSX3VNUDRkS0xtUTg
**Elapsed:** 188s
**Completed at:** 2026-05-21T17:24:47.777696+00:00

---

# The Frontier of Crystalline and Semistable Galois Representations (2024-2026)

* **Key Points:**
  * Research suggests that the application of prismatic cohomology to $p$-adic Hodge theory has profoundly revolutionized the study of integral $p$-adic Galois representations, yielding new equivalences between prismatic $F$-crystals and lattices in crystalline and semistable representations [cite: 1, 2].
  * The frontier of multivariable $p$-adic Hodge theory is rapidly expanding, with 2024-2025 breakthroughs establishing overconvergent multivariable $(\phi, \Gamma)$-modules and extending Sen theory to products of Galois groups [cite: 3, 4].
  * It seems highly likely that emerging theories concerning wildly ramified Galois representations will resolve longstanding barriers in understanding the geometry of Emerton-Gee stacks and the exactness properties of Breuil-Kisin modules [cite: 5, 6].
  * Explicit computations of the reduction modulo $p$ of crystalline representations continue to yield highly complex but critical results, particularly for the notoriously difficult case of $p=2$ [cite: 7, 8].

* **Introduction to the Field:**
  The study of $p$-adic Galois representations lies at the heart of modern arithmetic geometry and the Langlands program. Formulated over several decades following Grothendieck's inquiries into the "mysterious functor" relating étale and de Rham cohomologies, $p$-adic Hodge theory classifies representations of the absolute Galois group of a $p$-adic field based on their periods [cite: 9, 10]. A representation is called crystalline or semistable if it exhibits favorable properties upon tensoring with Fontaine's period rings $B_{crys}$ or $B_{st}$, respectively [cite: 4, 9].
  
* **Recent Paradigms:**
  Between 2024 and 2026, the frontier has shifted toward integral coefficients, higher-dimensional bases (multivariable theory), and the incorporation of wild ramification. Driven heavily by the prismatic cohomology introduced by Bhatt and Scholze, mathematicians are re-evaluating classical lattices (like Wach and Breuil-Kisin lattices) and advancing the boundaries of the local Langlands correspondence [cite: 5, 11].

## 1. Prismatic $F$-Crystals and Crystalline Representations

### 1.1 The Prismatic Revolution in Integral $p$-adic Hodge Theory
The classical approach to $p$-adic Hodge theory, pioneered by Fontaine, Faltings, and others, effectively addresses rational representations [cite: 9, 10]. However, studying integral $p$-adic Hodge theory—specifically, the Galois stable $\mathbb{Z}_p$-lattices or $\mathcal{O}_E$-lattices within these representations—requires highly sophisticated machinery. The introduction of prisms and prismatic cohomology by Bhatt and Scholze has recently provided the definitive framework for these integral investigations [cite: 11].

Prismatic $F$-crystals act as the geometric avatars of Galois representations over certain period sheaves. In a major 2025 breakthrough, Dat Pham extended the work of Bhatt and Scholze (which originally applied to the case where the coefficient field is $\mathbb{Q}_p$) to finite extensions $E / \mathbb{Q}_p$ [cite: 1]. Let $K$ be a complete discretely valued field of mixed characteristic $(0,p)$ with a perfect residue field, and let $E$ be a finite extension of $\mathbb{Q}_p$ contained in $K$. Pham demonstrated that the category of prismatic $F$-crystals on the absolute prismatic site of $\mathcal{O}_K$ (relative to $E$ in a strictly defined sense) is equivalent to the category of $\mathcal{O}_E$-lattices in $E$-crystalline representations of the Galois group $G_K$ [cite: 1, 12].

These $E$-crystalline representations, originally introduced by Kisin and Ren, are representations where the induced filtration on the de Rham module $D_{dR}(V)_{\mathfrak{m}}$ is trivial for all maximal ideals $\mathfrak{m} \neq \mathfrak{m}_0$, where $\mathfrak{m}_0$ corresponds to the multiplication map $K \otimes_{\mathbb{Q}_p} E \to K$ [cite: 1]. To achieve this equivalence, Pham established a general full faithfulness result for specific vector bundles on the prismatic site [cite: 12, 13]. Crucially, this was done by adapting a lemma of Du and Liu, thereby refining the descent step in the Bhatt-Scholze approach without needing to invoke the Beilinson fibre sequence [cite: 12, 14]. The proof relies extensively on realizing the relevant objects as vector bundles on the Fargues-Fontaine curve associated with $E$ and the fixed embedding $\tau_0 : E \hookrightarrow K$ [cite: 1, 13].

### 1.2 Log Prismatic $F$-Crystals and Semistable Local Systems
The prismatic theory has also been expanded to accommodate semistable Galois representations and local systems. In their 2024 and 2026 series of papers, Heng Du, Tong Liu, Yong Suk Moon, and Koji Shimizu systematically developed the theory of completed prismatic $F$-crystals and log prismatic $F$-crystals [cite: 2, 15, 16].

For a smooth $p$-adic formal scheme over $\mathcal{O}_K$, they proved that the category of completed prismatic $F$-crystals on its absolute prismatic site is equivalent to the category of crystalline étale $\mathbb{Z}_p$-local systems on its generic fiber [cite: 15]. Pushing this further to the semistable case, they utilized the absolute logarithmic prismatic site to study $p$-adic local systems on a rigid-analytic variety equipped with a semistable formal model [cite: 2]. 

A central outcome of this research program is the **Purity Theorem for Semistable Local Systems**. Fontaine and Mazur's longstanding conjectures motivate the need to understand when local systems arise from geometry [cite: 17]. Du, Liu, Moon, and Shimizu proved that a $p$-adic local system on $X$ is semistable if and only if its restriction to each "X-Shilov point" corresponds to a semistable Galois representation [cite: 2]. An X-Shilov point corresponds to a rank-1 point defined by the fraction field of the completed local ring at the generic point of an irreducible component of the special fiber [cite: 2]. By analyzing Breuil-Kisin log prisms, the authors establish a prismatic purity theorem that subsequently yields the purity theorem for semistable local systems, representing a major leap over earlier work by Tsuji that handled only the crystalline, good-reduction case [cite: 2].

## 2. Reductions Modulo $p$ of Crystalline Galois Representations

### 2.1 The Small Slopes and the Case of $p=2$
Understanding the reduction modulo $p$ of a crystalline Galois representation is highly vital for the local Langlands correspondence and modularity lifting theorems. The mod $p$ reduction of a crystalline representation $V_{k, a_p}$ depends intricately on its Hodge-Tate weights ($0$ and $k-1$) and the slope $\nu = v(a_p)$ of its crystalline Frobenius [cite: 7, 8]. While the structure of the semisimplified reduction $\bar{V}_{k, a_p}$ has been deeply studied for odd or sufficiently large primes, the prime $p=2$ has historically been avoided due to severe technical difficulties [cite: 8].

In May 2026, Shalini Bhattacharya and Arathy Venugopal released comprehensive computations filling this gap [cite: 7]. They computed the explicit form of the semisimplified reduction modulo 2 of the 2-adic crystalline Galois representations $V_{k, a_2}$ at small slopes in the range $\nu \in (0, 1]$ [cite: 7, 18]. 

The methodology leverages the compatibility of the 2-adic and mod-2 local Langlands correspondence (LLC) [cite: 7]. The mod-2 LLC provides an injective correspondence, meaning that one can determine $\bar{V}_{k, a_2}$ by reducing the associated unitary $p$-adic Banach space representation $B(V_{k, a_p})$ modulo 2 [cite: 8]. Unlike odd primes, the formulation of the mod $p$ LLC for $p=2$ does not involve a variable $r$, operating instead on representations of the form $\pi(r, \lambda, \eta)$ which classify smooth admissible irreducible representations of the group $G$ over $\bar{\mathbb{F}}_p$ [cite: 7].

Bhattacharya and Venugopal identified critical parameters, $\alpha'(k, a_2)$ and $\alpha(k, a_2)$, which dictate the behavior of the reduction [cite: 7]. For slopes $\nu \in (0, 1)$, if $\tau' = v(\alpha') < v(r-1)$, the reduction splits as an induced representation $\text{ind}(\omega_2)$ [cite: 7]. Furthermore, their analysis yielded quick consequences based on the parity of the weight $k$: for instance, if $k \geq 2$ is even and $0 < v(a_2) < 1$, the reduction $\bar{V}_{k, a_2}$ must be irreducible [cite: 7]. This structural mapping over the Bruhat-Tits tree for $p=2$ addresses a critical frontier in understanding reductions in mixed characteristic [cite: 19].

### 2.2 Prismatic Approaches to Inertial Weights
Beyond explicit slope computations, prismatic methods are shedding new light on the inertial weights of mod $p$ reductions of local $p$-adic Galois representations. In a March 2026 seminar, Toby Gee detailed joint work with Bhargav Bhatt and Mark Kisin outlining new structures on Breuil-Kisin modules derived through the prismatic framework [cite: 20]. These new structures allow for a profound re-evaluation of the weight part of Serre's conjecture and the Breuil-Mézard conjecture, linking the crystalline structures directly to the inertial profiles over $\mathbb{F}_p$ [cite: 20, 21]. Dat Pham has also contributed substantially to this domain by offering a new stack-theoretic proof controlling torsion in the graded pieces of the integral Hodge filtration of a crystalline Galois lattice, heavily inspired by Gee and Kisin's work on the shape of mod $p$ crystalline Breuil-Kisin modules [cite: 22]. Pham constructed a so-called Sen operator $\Theta$ from a differential operator $\mathcal{D}$ mirroring the structures of the diffracted Hodge complex [cite: 22].

## 3. Wild Ramification, Emerton-Gee Stacks, and Breuil-Kisin Lattices

### 3.1 The Challenge of Wildly Ramified Types
One of the most active frontiers in integral $p$-adic Hodge theory from 2024 to 2026 has been the integration of wildly ramified representations. Historically, to construct and analyze potentially semistable deformation rings (as per Kisin) and the moduli stacks of $(\phi, \Gamma)$-modules (as per Emerton and Gee), mathematicians relied on finding suitable $\phi$-stable lattices, such as Wach lattices or Breuil-Kisin lattices, inside étale $\phi$-modules [cite: 5].

However, when a Galois representation exhibits a wildly ramified Weil-Deligne type, or when the underlying reductive group is wildly ramified, the relevant $\phi$-modules frequently lack $\phi$-stable lattices entirely [cite: 5, 23]. Consequently, the structure of wildly potentially semistable deformation rings remained highly opaque [cite: 23].

### 3.2 $\phi$-Unstable Lattices and Emerton-Gee Stacks
Recent breakthroughs by Zhongyipan Lin, partly in joint work with Y. Min and S. Morra, have addressed this barrier. Lin demonstrated how the study of carefully chosen **$\phi$-unstable lattices** within étale $(\phi, \Gamma)$-modules enables the construction of Emerton-Gee stacks for wildly ramified reductive groups [cite: 5]. For any embedding ${}^L G \to GL(V)$, the corresponding morphism of Emerton-Gee stacks is proven to be relatively representable by algebraic spaces of finite presentation, even in the wildly ramified context [cite: 5, 23].

Furthermore, for wildly potentially semistable Galois representations with cyclically ramified Weil-Deligne types, Lin, Min, and Morra are developing the precise expectation for the correct notion of "Breuil-Kisin lattices" [cite: 5, 23]. These newly theorized lattices differ from traditional Breuil-Kisin lattices but maintain a close functional relationship that allows for local models to be formulated [cite: 23]. 

### 3.3 The Weight Part of Serre's Conjecture and Breuil's Lattice Conjecture
Concurrently, the exploration of wild ramification has accelerated global arithmetic applications. D. Le, B. V. Le Hung, B. Levin, and S. Morra achieved a major milestone in 2024 by establishing the weight part of Serre's conjecture for three-dimensional mod $p$ Galois representations under generic conditions, crucially removing the assumption that the representation must be tamely ramified at $p$ [cite: 21, 24].

This work also proves a generalization of Breuil's lattice conjecture and establishes the Breuil-Mézard conjecture for generic tamely potentially crystalline deformation rings of parallel weight [cite: 21]. The foundational insight driving these proofs is a deep investigation into the geometry of the Emerton-Gee stacks $X_3$, utilizing specific local models for Galois representations [cite: 21, 24]. This permits the bounding of support cycles and establishes local-global compatibility in the mod $p$ Langlands program, expanding boundaries into settings where the base fields are CM fields [cite: 24, 25].

## 4. Multivariable $p$-adic Hodge Theory

### 4.1 Products of Galois Groups
While classical $p$-adic Hodge theory studies the absolute Galois group $G_K$ of a single $p$-adic field, contemporary approaches to the geometric Langlands program—particularly as developed by Drinfeld for $GL_2$ and V. Lafforgue for other reductive groups—naturally invite the study of products of Galois groups [cite: 4]. Specifically, one considers $G_{K, \Delta} = G_{K_1} \times \cdots \times G_{K_t}$, where $\Delta$ is a finite set indexing the $p$-adic fields [cite: 26, 27].

G. Zábrádi initiated the multivariable analogue of Fontaine's $(\phi, \Gamma)$-modules. In this framework, representations are classified by étale $(\phi_\Delta, \Gamma_{K, \Delta})$-modules over a ring $E_\Delta$, which is equipped with $t$ distinct partial Frobenii [cite: 4, 28]. Unlike the classical setting where étaleness is straightforwardly checked on the Frobenius, the multivariable étaleness condition inextricably involves the Galois action [cite: 4]. 

### 4.2 Overconvergence and Colmez-Sen-Tate Descent
A crowning achievement in this domain between 2024 and 2025 is the work of Léo Poyeton and Pietro Vanni on multivariable $p$-adic Hodge theory [cite: 3, 29]. They solved the problem of attaching an overconvergent family of multivariable $(\phi, \Gamma)$-modules to a family of $p$-adic representations of a product of Galois groups [cite: 3].

Their methodology heavily relies on constructing multivariable period rings by taking completed tensor products (over $\mathbb{Q}_p$ or finite extensions) of copies of classical $p$-adic period rings [cite: 4, 26]. Leveraging non-archimedean functional analysis, Poyeton and Vanni proved that the completed projective tensor product of rings with principal ideal topologies coincides with their adic completion, and importantly, that group invariants commute with these completed tensor products under the right Fréchet space conditions [cite: 26]. 

They achieved a multivariable Colmez-Sen-Tate descent, extending classical Sen theory to families [cite: 3, 26]. They showed the existence of a unique free module over a multivariable Sen ring that is fixed by the Galois group and stable under the Sen operators corresponding to each variable [cite: 4, 26]. This establishes that multivariable representations overconverge, acting as the critical analogue to the classical Cherbonnier-Colmez overconvergence theorem [cite: 4, 26].

### 4.3 Multivariable Crystalline and Semistable Periods
Poyeton and Vanni further formulated the concepts of multivariable crystalline and semistable representations [cite: 3, 4]. Instead of traditional single-variable period rings, they defined multivariable analogues such as $B_{crys, \Delta}$ and $B_{st, \Delta}$ by evaluating the completed tensor products of classical period rings [cite: 4, 26]. A multivariable representation is thus defined to be de Rham, crystalline, or semistable by assessing its tensor product with these rings and evaluating the invariants under $G_{K, \Delta}$ [cite: 26]. This framework entirely subsumes and recovers previous results by Brinon, Chiarellotto, and Mazzari on multivariable $p$-adic Galois representations [cite: 3].

### 4.4 Perfectoid Spaces in the Multivariate Setting
To further anchor the geometry of the multivariate theory, Poyeton and Vanni also introduced a systematic study of perfectoid spaces within multivariate $p$-adic Hodge theory [cite: 27, 30]. When forming the completed tensor product $K_\Delta = K_1 \hat{\otimes}_{K_0} \cdots \hat{\otimes}_{K_0} K_t$ of perfectoid fields, the resulting ring $K_\Delta$ is not a field. Rather, it is a reduced ring of dimension zero whose localizations are all perfectoid fields [cite: 27, 30]. By classifying the prime ideals of these tensor-product rings, the authors provide the foundational bridge for an Almost Purity Theorem in the multivariate setting, paving the way for a diamond-theoretic view intrinsic to the multivariate framework [cite: 27, 30].

## 5. Bloch-Kato Selmer Groups and Breuil-Kisin Functors

### 5.1 Exactness Properties
Integral $p$-adic Hodge theory predominantly takes place in exact categories (in the sense of Quillen) rather than abelian categories, because categories of lattices are not abelian [cite: 31]. The mapping between Breuil-Kisin modules, strongly divisible modules, and Galois representations must be rigorously managed to preserve exact sequences [cite: 31].

In early 2026, Pavel Čoupek and Evangelia Gazaki addressed the exactness property of Breuil-Kisin functors and their relationship to Bloch-Kato Selmer groups [cite: 6, 31]. They constructed a category of Breuil-Kisin $G_K$-modules to classify integral semi-stable Galois representations, drawing upon Breuil-Kisin-Fargues modules [cite: 6]. Notably, they demonstrated that the standard functor $M_{st}$ from $G_K$-lattices to strongly divisible modules is generally not even left exact [cite: 31]. However, using a Harder-Narasimhan theory for Kisin modules (generalizing Fargues' work for finite flat group schemes), they proved a tensor product theorem—that the tensor product of semi-stable objects remains semi-stable [cite: 6]. 

Moreover, they applied these exactness principles to geometric settings, showing that for abelian varieties with good reduction, the Kummer sequences factor through an $\text{Ext}^2$ group of strongly divisible modules, directly mapping to the Bloch-Kato Selmer group structure [cite: 31]. They also formulated a prismatic Herr complex using a prismatic version of $(\phi, \tau)$-modules attached to a log-crystalline representation, effectively computing the Bloch-Kato Selmer group and linking it to the cohomology of the corresponding $F$-gauge [cite: 5].

### 5.2 Vanishing of Adjoint Bloch-Kato Selmer Groups
From a global perspective, rigidifying these Galois representations is a prominent goal. A 2024 advancement successfully proved the vanishing of adjoint Bloch-Kato Selmer groups of automorphic Galois representations over CM fields [cite: 32]. This vanishing asserts that these representations are "rigid" in the sense that they possess no non-trivial deformations that remain de Rham and are almost everywhere unramified [cite: 32]. A crucial component of this proof required demonstrating that automorphic Galois representations over CM fields are themselves de Rham, utilizing a weak semistable local-global compatibility theorem generated via a Taylor-Wiles patching lemma that capitalizes on the smoothness of certain characteristic zero deformation rings [cite: 32].

## Conclusion
The mathematical period of 2024-2026 marks an era of intense cross-pollination in arithmetic geometry. The descent of prismatic $F$-crystals into the study of lattices in crystalline and semistable representations has completely reformed integral $p$-adic Hodge theory [cite: 1, 2]. Simultaneously, the explicit calculations at extreme boundary conditions—such as the mod-2 local Langlands correspondence for small slopes [cite: 7] and the inclusion of wildly ramified types into the Emerton-Gee stack framework [cite: 5, 25]—are resolving deep foundational blind spots. Lastly, the crystallization of a fully functional multivariable $p$-adic Hodge theory, complete with overconvergent descent and period rings, guarantees that the representations of products of Galois groups can now be studied with the same robust tools as their classical counterparts [cite: 4]. Together, these advancements ensure that the geometric and arithmetic properties of crystalline and semistable Galois representations will continue to be a fertile, fast-moving frontier.

**Sources:**
1. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVvFeA2RinG-w2ZCP55PaBqDaIjFXM2fzoICcJOc91Lsy2CZfCuo3dWbaBvqx4r7qQBNl6guPZYdvmaqEMDr4dUt-yb3tJZJvL3cT6fEd4hitKNqV7Spw8bhb22HXWQsJb2PzHoUKC5SHGKCk=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHgRmaDy1Ue__uKBq7t5GtY-uuQyWCc2TiRGfYEe6el5xBOcGGjKdtvSO5RAp6XioNPxrVrGKXVzdtF3NXJX-EvKufW2sHICdL2d3nbYzP2CIYK7kI)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQSN6ovyt1XaOXsLUZNcZ4d6WowI0a7C9VXeUNOuonl0Pa6HQO0Q6_Hq9zODvTnCxP2MrlSk1wGRPlwCZxF541bUY_Df9LVPRuAE6gr357GA4nXSfJ)
4. [u-bordeaux.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIvEY31XUtXLewh1zr__NtcT2mHHH0FMiUNhWYbltbfdSdf6Nei5CVWi1aAntc_9HBI23_NfVYN16UUjObyfD7EcEpDx8gF_idPjnjhzh-oDJDMQ6hVTjeQF7oGSNa8tDN5Uw8uAy-grmHeRIUiLH1AZnqkGNSiUMO2Nk=)
5. [tsinghua.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOH91y1sseiui5d2zD6rrqfMnUQzvKhy5m7LZ9Z2vu4Xxp_mA3cdmteiy-uqfsfMtuuZwuKUhivcU2rIZNq6S_IqGMJgmrsjfSRfjbnuN6kT3xVTsPn1FltGilFon_rVt7186D)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJtGoK0e3-Gdo4nQGIC2Mpucjn9F0m_QMSQlsz5hOctIzkuDizcMB6lGuRMn7oSLn0w7vuUsnZDEaUkULxLRZZqABMZgW2kgGAK91sgWGAePQ5d-d7zbq6Lnaj_cQXUHBlSV7MyO_ZpO6Y3NgGjXXq-CSEw2p9xLTRMox7ZsZa7S4pduqFEqW6Kw09EPgEjltb3rBWUtYAEzLEfON-YCS0nuN99AxcL2k_zyedrNIbHw==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_EonC2TR4oF7TRjmt4x0xHl4peLbTD7x_grDhtc79MlK9JpvKQ4qPOYp4RPA541cFUurG4l9nAvJfqFN6ojlI6IHWV-8q0M-St5DcM8c27uBKXE7i)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFB2FREjQMtfV-_ThQWPugZM0h-bMubIm-Hd5roch9GN-7GA1rHzGSU8X3fhQwHDB7nMaShn409G5Hv87CvyDt2pHsNmdpXkbXkG_zrNlobKOXMdZ7LoZ3O)
9. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfH9MbfIH7l1uq48fmuv0zdO-ZR0T0_fnhimS7JEc_T0cg1uxfgQdpRjHfLW5Z25NteUHRavMwwH7lPeOIGeWy8cBfFwGJ1_b1aAuNnvGMXbyS6523TndscfEAcjoVmah4x7tY8wc=)
10. [emath.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdXy3KW3TU_kVSSKwXxIA6PBWFfKu0eP_dJjm1phAi1F0cojOw0J-toHxrfqeV0HhQxx9NxNCR_3w-VBJPYLLDupvvnCG5Acd3p9gb5ECHas2nT2-qQdJMYO5I2V9VKQ0O1Q6SKD6Gd-mh69_TRKE7yX86e5o48U13RMk3KY2i)
11. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-IcFCG8QOdBCDBsuNElKcOFpvDc5HATndmhyMqQhKlJtLkxy5F30CQbvZUJKClsIJps2XAKgZx4nsYyFj-8pLTN3hkIfdlPnNNYKaXgUHOuocvMQEWkYankS1DMvuLF9ucYze3J_3pg==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcEKKofH9LrQbgIU7AZacMa1iBIJw9h-kSe0oWZtGjO3KwAFaIUN97apN6Pv3TVVRAUwL4WmRi74jCuixG2ncj7EhmTJ7yIuXLpS4S8LCItWEy3tT2)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsI8_KJhFog2QwUGxqMJw7tuQO8L3FUdDZ2kJxNyNky3rYUqRlV5TmRmVhc6Zn-upDyFUS_hge29CGuIm6l0w-qGIRe89mPo-Yv9kjZutIT5ziD1mt)
14. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHc6Dfbizm_g84wQ0gjtDCA9bSVH_2d4Or4TIXESXZP4ihdXSLC5dxzBr73agoHKlkSDwYF3XuSXb2Fs2uBCTVWbDOfSQ4fpUgN5bOVVsl_Rt1jNm_KUY55CnpYmq0Oi6zFjs=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtGBko4UK9OPjXYq8bHVh7X2O5QzWQTUO5NppoKavr9DVwHJwt_kqHnoInbiVYLjLGsTAV3-pE26Jecxcml_s4tXScJeCAaOs3a_RANy6t3a-Mzx-4)
16. [hengdumath.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHE75dbQKrMPFVEGMaw2rC6-xYOuvKottrgD16LOTfe3G0V6fUDMem20v7htBIeinY_F-fMC2IEcPI1-ySVfyZV76i1UOzZ5zuyDE6RfQxGKmcXNNkcOIs0)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLG2VHYTw1FpV_3eF6cVXoBaMFNIRDR3iC1UqSVS0rm66QseOf2MuiJXfbMm-tRwfxrB8KXGM_GNWtGGTf-wtCPCi35lVJaMDj8uBqcv27NQgGKFkE)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-kjjEGzB6j6rfoOY79ojcN0ewH60Zy1l1QFTjMI23MmMwIJi119xfNk8vl4gY8MPqnHZog1Nnrkx6bZJJK1Glhqh6rkuS-gvczVESwHLuRhnEUmWR)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLvnks5Nq0VELx2ehNlURJ4GPjgplYB2pl1FUN2MPB-w8t3PxKTwbgZOh3qHF11IjhAahn0eYHYLxh2n5HDevlyhG2skl4X92B8EMRrECmq4B8hMNmvRFtA8LjlkGnuwWkUM-Rka_49EVz1u54aFIkm_2GTBR9cNpt9owVImtjMg==)
20. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYiVpB03QPcboz1rFyFoOcNROnpEP_7KD-yegLYuuGwrWmW2HoSXi-zVpJ1fv5TM35IC0C0mhpoR-4HkKtiLh-G_q09GVai2RbhUY4jcMYNEymo8joK5hBD8bSncMdNFA0K7IqmxUUwudBHXzVOBg0RqJ5wRhFtwCgT8uOSZ7LKhkmjIEjJ3tIqgRYMxqgaIQ50aMq8Y0FBhiu2KaOR90=)
21. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFr15LDfdNgNu2M5QgbYDnuoSsET-obATLN8lLNDLNMw29pit1mvhMw5ltmYLUCBm_B3RhE9DMzCotfyhrr_Pfp_5xv-26szGJTF4Qb5HGWpCqtGnlEmWmKzE5D647X-AT8FZWDwtrK)
22. [imj-prg.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJOpXZ_eclsiDw77yn6X6u4g9tMFiObPRiZQbRK97_tAfWKkse9imq4MOqC9OoSgn9Mn4QxqCkIg-AX_7WOf2kEvN3y4SEYIdAQ2LQ-3z6uSfQ0E1lEAxuyEMp2xLri6ZqGX8CApTl5u3zDZsttLepr7Et)
23. [bimsa.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8WlY_aud6IEGyX1MTjfdyjfxIA_1I2D4LpIiwj5n-IpzOIMbCjh7ES5yWRoobmGc6J9y6etMR-CLmj-R5qFNZd2xX5hdN18G9uzh2nqg2GR-Q1iQ-zeUE9g==)
24. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2y52EkBFdeLUyvicUbSplRYWjYNfL-nSlcfp1CVyrDthy6mmXrobmmkN-OyMbKst55GdwzfQUeW-zMPT_EXrzFFvEnEtrSMTsm7OPwgvRHzXs47hH840YgsUVV60ozGYodts=)
25. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7qd0Ix4LKAsW8UqO0dknwlcN9EGljeSaLdHQHXB6agG0ba--NrTMGLL1okYYv5e683agv--8dvDKxhe-ymbT6njbz5HYwvJmR_VTZ5CHaoqvIUL3bHtRKz6fgXFx3IUmwcVvei_AH_AtgJw58oW6X8ow_cyMjtNCdyrtpCRAR4DOeAM-zskRp2d4A6g-k1jJkC8XbGrm9Z6ckvMI=)
26. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdCmY-eI0WSFpWCCCvls-qr89rlh8QQYgVfgxwljvSnbS9IsqoTJWfFdc_MANuv3nq3LkoAg2IsRTfQPrmPNv7r-BEZvaWlzZCm_piRkufAgD-MY5p6FrYiAjEF_rw4NvrJdujWOPWRPclGZkZIPXC2sa59DTy_m1pdBYLKiRhhBAn5YmjKO2VI2el8ka41P6EVPKRv9HpM_lP)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUVnEusb7JmEpPpavrwI42gKF8T4Qomm4OasTsWvUohy10EOrCxcjVLFV_mJerR_4FlrW96o9lUnPjsEzXD4pMIeInCV1qfmpA2fyiPVNfEsz6hATR)
28. [elte.hu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtYFLIIQr_YACgvJqR4UvJ3mNuRdTR9tBsp1ZYhZ7u4400kk3HyB1QAITBVoZJCen0Cb2CCsb8E-xiTjEjm2fMCpby_-r2JRPvFjBBJQrztdIsNlubCdBMDdsKSuyZqqHW8Oo=)
29. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGErU-uJIGNG6WL4i_tr9LUwaxorIdC4ZKAPFX8ALsbFZoUPoWtP5XKfuOQuwVNJyXsbUWouvMnI7YigedTAd3Crh3UfJ3M7dykbe5jfoZwbmufvi1hxsAwD5iVVj7548wTW23tTKpsfb2E-KJlRjFtBoOwpB3gHBqs1NPBR8ug_v6QHqkZTAAdofrusBTXXW4aBDVdmOCAwWfVHxmbgxCje8HhADK8Sw==)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiSiciN7sqplxSSYoih6IPUYBCAdZRWiV1nfY1XgVDQGgIwxDXWoI8drWmoKQ8wWqMSGZgrJ0cn_Nu_zsYHLQrSJMxOrHIoHdEa510FI9JBGUZDaa8-OT7aahCKb6Emao5ycBkFkXrQeTPIpF6sa3w6Qj4cZYwS7K1iJmocE2VoZENkyJaOVTMkXZU2FkGT3swQtXBI3ptBZfLKydD)
31. [unistra.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9oSAjxGfisq2pE-d7KVtD8OkTZPaS9OkTau233wMvC8CLag0aYb17ufnXjbwlVUKfXFXwTDaV3BvPE6p1z7AVE6fJ8Uq7xg-US3vFJDIaP-IRPLGJi4HxudcGLRvcGxVSfGAmS6vm8B9Vjg==)
32. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6LowU1WH0iyZO02cmdaFAK2L_XRWO_qg_K-d1okQf5fc2ZzsdF07XpTQFo1bucwqG61O5RvebkVUTVgOfFPLnF_MuPHdgFArYJq_Krloa4S2opFm1D-v1PmQpJiUOe0QNb6Ix8dqZ93dLYqCqGg==)

