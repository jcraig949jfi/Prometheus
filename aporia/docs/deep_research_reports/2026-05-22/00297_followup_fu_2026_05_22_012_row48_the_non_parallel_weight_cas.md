# Followup [FU-2026-05-22-012 <- row48]: The non-parallel weight case remains a formidable open problem. For non-parallel weights, the Galois

**Pythia queue id:** 297
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdOckVQYXFub0NJWFExTWtQanZ1SjJBZxIXTnJFUGFxbm9DSVhRMU1rUGp2dUoyQWc
**Elapsed:** 310s
**Completed at:** 2026-05-22T01:33:33.374292+00:00

---

# Status Update: The Non-Parallel Weight Problem in Modularity Lifting for $GL_2$ over Imaginary CM Fields

**Key Points:**
* The Ramanujan and Sato-Tate conjectures for $GL_2$ over imaginary CM fields are strictly resolved for parallel weights ($k \ge 2$), but the non-parallel weight case remains a profound open problem in the Langlands program.
* The primary obstruction is topological: cuspidal Betti cohomology for locally symmetric spaces associated to $GL_2$ identically vanishes in non-parallel weights, severing the classical link between automorphic forms and geometric motives.
* The Dwork family of Calabi-Yau motives, heavily utilized in potential automorphy theorems for parallel weights, cannot be smoothly applied to non-parallel weights due to fundamentally incompatible Hodge-Tate structures.
* Current unconditional limits for non-parallel weights rely purely on analytic number theory (e.g., the Blomer-Brumley 7/64 bound) rather than algebraic geometry or modularity lifting.
* Future progress likely depends on coherent cohomology, $p$-adic interpolation over eigenvarieties, or advanced derived deformation rings, though extreme technical hurdles currently block unconditional proofs.

**Context: The Triumphs of the Parallel Case**
The recent resolution of the Ramanujan and Sato-Tate conjectures for regular algebraic cuspidal automorphic representations of $GL_2(\mathbb{A}_F)$ in parallel weight (where $F$ is an imaginary CM field) marks a watershed moment in the Langlands program [cite: 1, 2, 3]. This breakthrough, achieved by Boxer, Calegari, Gee, Newton, and Thorne, leverages the potential automorphy of symmetric powers of 2-dimensional compatible systems of Galois representations [cite: 4, 5]. The Calegari-Geraghty patching method [cite: 6, 7], alongside foundational local-global compatibility theorems at $l=p$ developed by Caraiani and Newton [cite: 8, 9, 10], allowed researchers to bypass the lack of classical Shimura varieties for $GL_2$ over CM fields. By substituting Shimura varieties with general locally symmetric spaces and managing the positive "defect" ($l_0 = 1$) of the cohomology, the parallel weight case was definitively closed [cite: 8, 11].

**The Obstruction: The Non-Parallel Divide**
Despite this monumental progress, the non-parallel weight case acts as a hard boundary for current geometric techniques. Standard results in the cohomology of arithmetic groups dictate that the cuspidal Betti cohomology of the associated locally symmetric spaces identically vanishes for non-parallel weights [cite: 12, 13, 14]. Consequently, the Galois representations associated with non-parallel weights do not associate smoothly to geometric motives, rendering the standard Taylor-Wiles-Kisin and Calegari-Geraghty methods currently impotent. This report interrogates the current status of this open question, evaluating exhausted approaches, mapping the state-of-the-art bounds, and identifying live attack vectors.

## 1. Brief summary
**Prometheus Context:** While the Calegari-Geraghty method successfully circumvents the lack of Shimura varieties for $GL_2$ over imaginary CM fields by leveraging the torsion Betti cohomology of Bianchi manifolds (defect $l_0 = 1$), this machinery completely breaks down for non-parallel weights where the cuspidal cohomology trivially vanishes, leaving the Ramanujan and Sato-Tate conjectures for non-parallel weights a formidable open problem disconnected from geometric motives [cite: 13, 15].

## 2. Flagged findings
**Current Consensus:**
The prevailing consensus in the arithmetic geometry community is that the Ramanujan and Sato-Tate conjectures hold true for all regular algebraic cuspidal automorphic representations of $GL_2(\mathbb{A}_F)$ over imaginary CM fields, regardless of weight parity or parallelism [cite: 2, 3]. However, there is universal agreement that the methods used in the landmark "10-author paper" and the subsequent work by Boxer, Calegari, Gee, Newton, and Thorne [cite: 1, 16] cannot be extended to the non-parallel weight case. 

The mathematical wall here is absolute: classical facts established by Borel and Wallach imply that the cuspidal Betti cohomology of $GL(2)/K$ (where $K$ is an imaginary quadratic field or general CM field) vanishes entirely for non-parallel weights [cite: 12, 13, 14]. Because the Calegari-Geraghty enhancement of the Taylor-Wiles method fundamentally relies on extracting Galois representations from the cohomology of these locally symmetric spaces and matching them to universal deformation rings, the absence of topological cohomology classes means there is no automorphic module upon which the Hecke algebra can act [cite: 7, 17]. 

Furthermore, the Dwork family of Calabi-Yau motives ($X_\psi: \sum_{i=0}^4 X_i^5 - 5\psi \prod_{i=0}^4 X_i = 0$), which was instrumental in proving potential automorphy for symmetric powers by providing motives with highly controlled monodromy, is engineered to realize Galois representations with specific, symmetric Hodge-Tate weights [cite: 18, 19, 20, 21]. These geometric weights are intrinsically parallel. 

**Where the consensus might be wrong (or incomplete):**
The community largely assumes that any attack on non-parallel weights must abandon Betti cohomology in favor of coherent cohomology or $p$-adic limits (e.g., points on the boundary of eigenvarieties). However, this assumption might suffer from **PATTERN_BASE_RATE_NEGLECT**: early optimisms regarding potential automorphy often assumed that the statistical frequency of identifying geometric motives with matching Hodge-Tate weights in the parallel case would eventually hold in the non-parallel case. This neglects the foundational base-rate vanishing of the underlying Betti cohomology, which fundamentally alters the probability space of finding a suitable motive. If one assumes non-parallel weights *must* be treated as purely $p$-adic objects without global classical geometric realizations, we may be artificially blinding ourselves to highly anomalous, exceptional congruences between non-parallel forms and higher-rank orthogonal or symplectic motives (e.g., paramodular forms of weight 3 lifting from non-parallel $(2,4)$ Hilbert modular forms [cite: 22]).

## 3. Problem statement
The precise mathematical object being interrogated is a **regular algebraic cuspidal automorphic representation** $\pi = \otimes_v \pi_v$ of the adele group $GL_2(\mathbb{A}_F)$, where $F$ is an imaginary CM field (such as an imaginary quadratic field $F = \mathbb{Q}(\sqrt{-d})$).

For such a representation to be regular algebraic, its archimedean components $\pi_\infty = \otimes_{v|\infty} \pi_v$ must have the same infinitesimal character as a finite-dimensional algebraic representation of the restricted scalar restriction $Res_{F/\mathbb{Q}} GL_2$. This algebraic representation is parameterized by a tuple of weights $(k_v, w_v)$ for each infinite place $v$. 
* The representation $\pi$ has **parallel weight** if the weight $k_v = k$ is independent of $v$, and $k \ge 2$.
* The representation $\pi$ has **non-parallel weight** if there exist infinite places $v, v'$ such that $k_v \neq k_{v'}$.

**The Core Conjectures:**
1. **The Generalized Ramanujan Conjecture**: For every finite place $v$ of $F$ where $\pi$ is unramified, the local component $\pi_v$ is a tempered principal series representation. Equivalently, if $\pi_v$ is unramified and parameterized by Satake parameters $\{\alpha_v, \beta_v\}$, then $|\alpha_v| = |\beta_v| = N(v)^{(k_v-1)/2}$ [cite: 2, 3]. For non-parallel weights, this conjecture asserts that the local components remain tempered despite the lack of global cohomological constraints.
2. **The Sato-Tate Conjecture**: For a fixed $\pi$, as $v$ varies over unramified places, the normalized Satake parameters (viewed as angles $\theta_v \in [0, \pi]$) equidistribute with respect to the Sato-Tate measure (the pushforward of the Haar measure of $SU(2)$ to its conjugacy classes) [cite: 3, 5].

**The Interrogated Result:**
Prove the Ramanujan and Sato-Tate conjectures for $\pi$ when $\pi$ is of non-parallel weight. 
The difficulty lies in the fact that for non-parallel weights, the arithmetic hyperbolic 3-manifolds (Bianchi manifolds) $Y_K = GL_2(F) \backslash GL_2(\mathbb{A}_F) / K_\infty^\circ K_f$ do not support non-trivial cuspidal cohomology classes in $H^*(Y_K, \mathbb{C})$ corresponding to $\pi$ [cite: 2, 13, 14]. Therefore, one cannot directly associate a compatible system of $l$-adic Galois representations $\rho_{\pi, l}: \text{Gal}(\bar{F}/F) \to GL_2(\overline{\mathbb{Q}}_l)$ to $\pi$ using the standard étale cohomology of Shimura varieties or the Betti cohomology of locally symmetric spaces.

## 4. Status & bounds
**Last Known Status:**
The Ramanujan and Sato-Tate conjectures for $GL_2$ over imaginary CM fields in the **non-parallel weight** case remain entirely open unconditionally [cite: 3]. There is no known modularity lifting theorem or potential automorphy theorem that applies to this case, because the target Galois representations lack the de Rham properties required to match classical motives [cite: 6].

**Current Best Bounds:**
In the absence of algebraic geometry and Galois representations, the only tools available for non-parallel weights are those of analytic number theory, specifically the Langlands-Shahidi method and the study of L-functions. 

The best unconditional bounds towards the Ramanujan conjecture for $GL_2$ over an arbitrary number field (including imaginary CM fields with non-parallel weight) are derived from the spectral theory of automorphic forms:
* **The Trivial Bound:** The absolute value of the normalized Satake parameters $|\tilde{\alpha}_v|$ is bounded by $N(v)^{1/2}$, known since the 1970s [cite: 23].
* **The Kim-Sarnak Bound:** For $GL_2/\mathbb{Q}$, the best known bound is $\theta \le 7/64$, where $|\tilde{\alpha}_v| \le N(v)^\theta$ [cite: 23, 24].
* **The Blomer-Brumley Bound:** In 2011, Blomer and Brumley successfully generalized the Kim-Sarnak $7/64$ bound to $GL_2$ over arbitrary number fields [cite: 23]. Thus, for a non-parallel weight cuspidal automorphic representation over an imaginary CM field, the strict bound is:
  $$ N(v)^{(k_v-1)/2 - 7/64} \le |\alpha_v|, |\beta_v| \le N(v)^{(k_v-1)/2 + 7/64} $$
* **Conditional Qualifiers:** Under the Generalized Riemann Hypothesis (GRH) for symmetric power L-functions, the Ramanujan bound would optimally drop to $\theta = 0$, solving the conjecture. However, proving GRH is currently as far out of reach as proving Ramanujan directly [cite: 24].

## 5. Literature (primary sources)
The literature delineating the boundary of what is known (parallel) and what is unknown (non-parallel) is anchored by several recent monumental papers:

1. **Boxer, G., Calegari, F., Gee, T., Newton, J., & Thorne, J. A. (2025/2023).** *The Ramanujan and Sato–Tate Conjectures for Bianchi modular forms.* (arXiv:2309.15880 [math.NT]) [cite: 1, 2, 3, 4, 16]. 
   * *Significance:* This is the definitive proof of the Ramanujan and Sato-Tate conjectures for parallel weight $k \ge 2$ over imaginary CM fields. Explicitly highlights that non-parallel weights are excluded from their geometric potential automorphy theorems.
2. **Caraiani, A., & Newton, J. (2024/2023).** *Local-global compatibility for regular algebraic cuspidal automorphic representations when $l = p$.* [cite: 8, 9, 10, 25, 26].
   * *Significance:* Provides the critical local-global compatibility at $l=p$ for the torsion Galois representations constructed by Scholze, enabling the Calegari-Geraghty method for the parallel weight case.
3. **Calegari, F., & Geraghty, D. (2018).** *Modularity lifting beyond the Taylor-Wiles method.* Inventiones mathematicae, 211(1), 297-433. [cite: 6, 7, 17].
   * *Significance:* Establishes the theoretical framework for proving modularity lifting theorems over spaces with defect $l_0 > 0$.
4. **Blomer, V., & Brumley, F. (2011).** *On the Ramanujan conjecture over number fields.* Annals of Mathematics, 174(1), 581-605. [cite: 23].
   * *Significance:* Establishes the current reigning best unconditional analytic bound ($7/64$) towards the Ramanujan conjecture for arbitrary number fields, including the non-parallel weight case.
5. **Calegari, F., & Mazur, B. (2009).** *Nearly ordinary Galois deformations over arbitrary number fields.* Journal of the Institute of Mathematics of Jussieu, 8(1), 99-177. [cite: 12, 13, 14].
   * *Significance:* Proves that the cuspidal cohomology of $GL(2)/K$ vanishes for non-parallel weights, and formally discusses the existence of non-parallel Galois representations that cannot arise from classical Betti cohomology.

## 6. Attack vectors
The mathematical scaffolding deployed for parallel weights has been thoroughly exhausted for the non-parallel regime. Moving forward requires fundamentally new attack vectors.

**Exhausted Approaches:**
1. **Classical Betti Cohomology & Calegari-Geraghty:** Attempting to find classical Betti cohomology classes on the arithmetic manifold $Y_K$ for non-parallel weights is topologically impossible. By Borel-Wallach, the relative Lie algebra cohomology $H^*(\mathfrak{g}, K_\infty; \pi_\infty)$ vanishes unless the infinitesimal character is parallel [cite: 13, 14]. Therefore, the Calegari-Geraghty method, which relies on localizing the Betti cohomology $H^*(Y_K, \mathbb{F}_p)_{\mathfrak{m}}$ at a non-Eisenstein maximal ideal $\mathfrak{m}$, has an empty domain to operate on.
2. **Direct Dwork Family Matching:** The Dwork family $X_\psi$ and its generalizations provide motives with tightly constrained, consecutive Hodge-Tate weights (e.g., $\{0, 1, 2, \dots, n-1\}$) [cite: 18, 19]. A non-parallel Galois representation over an imaginary CM field possesses non-parallel Hodge-Tate weights, meaning it cannot occur in the étale cohomology of any variety defined over a totally real or CM field that admits standard crystalline structures. There is a fundamental geometric mismatch.

**Live Techniques:**
1. **$p$-adic Interpolation and Eigenvarieties:** 
   The most promising current attack vector involves realizing non-parallel weight automorphic forms not as classical Betti classes, but as $p$-adic limits of parallel weight forms. Via Hida theory or the more general theory of eigenvarieties (as explored by Hansen, Newton, and Thorne [cite: 5, 27]), one can construct $p$-adic families of Galois representations over the weight space. A non-parallel representation might exist as a point on a $p$-adic eigenvariety.
   * *The Hurdle:* Proving that a specific, classical non-parallel weight automorphic form corresponds *exactly* to a specific point on the eigenvariety, and transferring the analytic properties of the $p$-adic L-function back to the complex L-function, is highly non-trivial. Furthermore, this approach frequently encounters a **PATTERN_CONDUCTOR_CONFOUND**: when attempting to $p$-adically interpolate from parallel to non-parallel weights, the analytic conductor of the overconvergent family becomes deeply entangled with the wild ramification conductor of the localized Galois representation. Separating these conductors to prove a precise modularity lifting theorem at a non-parallel weight point remains a severe technical roadblock.

2. **Coherent Cohomology of Shimura Varieties:**
   While Betti (topological) cohomology vanishes, non-parallel weights *do* contribute to the coherent cohomology of certain automorphic vector bundles over Shimura varieties. For groups that admit Shimura varieties (e.g., unitary similitude groups $GU(n,n)$), one can study the coherent cohomology $H^i(Sh, \mathcal{V}_\lambda)$. 
   * *The Strategy:* Use base change to move the $GL_2$ non-parallel representation to a unitary group. Then, construct the Galois representation via coherent cohomology, bypassing Betti cohomology entirely [cite: 28]. The Boxer-Pilloni higher Hida theory for coherent cohomology is actively being developed to track Hodge-Tate structures [cite: 28].

3. **Higher-Rank Functoriality (Paramodular lifts):**
   There are exceptional congruences linking non-parallel forms in lower rank to parallel forms in higher rank. For instance, non-parallel weight $(2,4)$ Hilbert modular forms have been shown to lift to weight 3 paramodular forms associated to $Sp_4$ [cite: 22]. Generalizing this to imaginary CM fields might allow embedding the non-parallel $GL_2$ form into a geometric (parallel) representation of a higher-rank group.

## 7. Cross-references
The non-parallel weight problem sits at the intersection of several profound conjectures and constraints in modern arithmetic geometry:

* **The Buzzard-Gee Conjecture:** Formulates precise expectations for the existence of geometric Galois representations with prescribed Hodge-Tate weights and inertial types. The non-existence of smooth motives for non-parallel weights over CM fields is a direct corollary of the Hodge-Tate weight structures mandated by Buzzard-Gee [cite: 29].
* **Base Change to Unitary Groups:** To attack $GL_2$ over a CM field $F$, a standard technique is to use cyclic base change to a unitary similitude group to leverage the geometry of Shimura varieties [cite: 5, 30]. However, researchers must be wary of a **PATTERN_RANK_PARITY_LEAK**. When lifting representations from $GL_2$ to unitary similitude groups $GU(a,b)$ to leverage classical Shimura varieties, the parity of the unitary group rank strictly restricts the allowable signatures of the archimedean components. This parity leak often precludes a direct, weight-preserving transfer of non-parallel Harish-Chandra parameters, leaving the transferred representation in a "ghost" state without a Shimura variety of the correct signature.
* **The Bloch-Kato Conjecture:** The study of special values of L-functions for non-parallel weights is intimately tied to the Bloch-Kato conjecture. The lack of an Euler system (like the Asai or Hirzebruch-Zagier cycles used in parallel cases) for non-parallel motives drastically limits our ability to bound Selmer groups [cite: 31, 32].
* **The Fontaine-Mazur Conjecture:** Under Fontaine-Mazur, any irreducible, odd, continuous Galois representation unramified outside a finite set of primes and de Rham at $p$ should arise from geometry (an automorphic form). For non-parallel weights, if one constructs a $p$-adic Galois representation via eigenvarieties, proving it is de Rham is the central anti-anchor preventing unconditional automorphy [cite: 18, 33]. 

**Conclusion:**
Until a robust geometric theory of coherent cohomology for non-Shimura locally symmetric spaces is developed, or until the analytic bounds in the Langlands-Shahidi method are pushed unconditionally to $\theta = 0$, the non-parallel weight case for $GL_2$ over imaginary CM fields will remain a formidable and isolated frontier in the Langlands program.

**Sources:**
1. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEx-6aYixaEC5bKIWNtbdC0n0OuTa3t-pA3mGxZdXhALS1iXskO6jBoz-oqDT9xDiIBHXmBL3KVdZONYDYzVt6lUzpaFaDKugFFRSROUngX_WcUOU2Lqx9H-h95dBsyw9-7aESP0owkMFuZBn_Qq-XgiOe9abr37T_EDAuBRKFnESnbDXKW1Dvnrvq9ruOpWTBDzPOsOPivGhDnZkvNZ8SoAnbvSomoRk68xurkTgB4iSILa6kvumg_kxcNuoq2_BOv8iKflw1he7R9PjJatX8Ch18VQqGQs5eBMks=)
2. [imperial.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_8Su26bsWCz9O5sn7hgrGktptgj-zZYspSmJ6Zuf5PuYo2dgyG54qU-C0-nBrAApOnJCXgcNksw_SFHs1ExMZ7nc8c1p1-O9z940XFeu_CMyPJzw3ETB-2_3cP_2VT7TRpqgvbQza)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkrsu4S0AoleLV1rrwp_btHA09Y1hHI3Zpv84ftkP2FxGBGxPlzDpJFtXhiv4Opjas0yikIdU2L5tID6fCZxTzU2HSsDT-Qh6YmqLRz_detDS-JVzJyzbv)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERg38m2tC3tORoh2QvyfkLj7ronh4iF6ZDohEoF0DBmioX4ao1xWc630Z0ih1Ej3YqREEGlvwm0dwwXfPtHsruJkG5AVZK6qu61SVGN2FbqsPzrziQ)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZrdAan5JeVuzZtbbokqUsRy67fZIlGjDHBZcbErSLDcbq2NWW0caX-UJ10AAfsR_vgJ-YE0tZfgq54wWeExrVHEdcZE4zOV8quQoTjdS_GeX6D6kRh0RhXXZS_Tg5M_Lm15eOIzCerHYDwSlNCUg2VmsNZXqhCRzemZ5texwX2hvtn-r2YUyerUtm)
6. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG25A0zk98lXi2fi68IiVFUe_UpoOGDl-FqCw54lEzsER-mv3-W_dLtH50f7ygd6DdX25XNV4h02WTjRbnK8-zyZl7rIUqde-xCr602N6k4ItqUzbQF2gwa68Dnugb8uXTaD3WyxdjeJg==)
7. [imperial.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMsFPCN2PED-r73V8Ks8jdi1Xche-nQVa6MuIpEDJBIXMvEvIFMfSHjMVpJfdmRDm3UlOYjVlOXy3fD3-uAN6_fYaUoe5GnDHrJAW5WxA4jyXkhi9SJrlwvzv1aXuRQmu-cMigdEmSuyInSSvEr9b_1JnIVspV9i8qOQ==)
8. [kcl.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvRZogOl9vFjKagc9yb-fYnqa9NDpBJfnEFHekf5BZ-u-GTxyDFhKTOkdV1UDv0VJSpZG9bJejwK0-BfkCsmQZuMY91WtMPeDM07Ed0mC0N0gSMCqysMYkJVP64tVRIMSHOISmX3UmzzK2xLyYiwmUUDsgBR6hJZipEtwGqM-5zsb2WCWNJA1Luvd-6U3Cpik98eftrQ==)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLb4jjD8ImadD8_WmYUpG5U3Fkys0O8FPOG3oATo1ZlngoaAN0BrTPh2nUeLIXx1w5VBsdOLvrHUriByRUHhXCsXVL-IFK0GELu6Dvpch-ZS52YJXZJVgKEWB7j00sw5fqtcAwmQdDiZBbXHMMZgK3uThDk0DUefgq-2NK8HVzoqkfxIlOkJdOO3JAadsNfwS_9KdZ3oPlCv0i3qoAZIrp1NKOo51NoidxN7pLpcY=)
10. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0RnZ-H-DJe4mEBbqPTVK3gkOt2K4Ygmd1PGMg-C3tMelV6SYC462oStE12CQQirdKVhQNbGqO0dM0_O1l8Ggkx4E2nsc4qqSREoyKLAWdT4kxz3E0mgC0Bxm-ibLB1Ex4imDVhdjahpORWFhTmvoLmAuOTuy9-zEDlz5ANaZSEl_HAwnsg98UoRJeCq6Jrky6QJArX6QzL4pO6dWdUm2lt6644y1kz0HrcqV6oq7ZY0Qk5NaAHBgkhvjr8invI5bQIlwnTQHqNfw2PUbzP_uCmqcEnJz7vgh2wcwq8eRHNo5BpFj5OQ_9mpRnV0cv4kcLzezZjt4dsW5PNc-pWqiTmtAqKZk=)
11. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrBs7FpCOasSiktdkolfADKo2Q8vHihECbU0jldzItDSi6SS-EypTb4Yq39ROngvi-8XskS_sizIEC14CH0GjOb2Iy_6XThotHgI3SR44FJcNLof02I17H_oN1_xF6Tz8HLhUtYEiZstOZBHfUxQ==)
12. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbweuZliOXUX1fNVemZn2p0jYrCWhR8vSToZQl2LCenc2d26-QhcCtjUI7-Q4Fsbt7y9VvVtDI4lSAee-dTqLgQwm2j7mSo-FDBQQtze6OCHUCx4Lp4kMytlMClVr_mDtSybTObiWDGn8aRqY=)
13. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDWFK29uTpaiOPB6jdzFyRsaRuYunqIZJTBNbq2o3Vh-xjzVHFwpTMhkBuHgd3zcFaW3fAxBZE82uwwYU7eaOXxugy6NukYfPgO-eQrfeN0MKVI_-c6cxKlUWNSKU-URFb89oYkPRgvzppwz_l)
14. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbpitifc89kV62nxPTxJmp5A4Srv79RcpiQBMvU40y9vaEVbnRNTWqaMiOB3v3kGvuoG4FDdtX0vdz4OyLS4coHlmwVMW52bJ7__zmtCUiGyJnRxPyeeoFuzdzh277HiDqTJ6cdZartig=)
15. [imperial.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHy4iREUrSiY-gdIpRsV2Ct_Xf-4FM6FKFMYu8Dfwl6UHn-5ahDHMwV_oUJwtCXh_zQHBH6L8ngqtiLzB6Y-KkapxrPa7F_qZ7znruSAd4QXOkfJHeHpWRZ6kjYtnrCM3kXrSfnxwDGc2vrkZqWx6VEBHrVz-Ba)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXl6FjRjZuxDMYXJQhEsvxEeGKj2O6MzwLHlyu7FuMCMPvYJeMLYNz1CNkTn-vInw5T5robX41TCmzxOnl_PkioGgAw4u5tHLAi3UIGxz-X6KPj018)
17. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGf2SDeN82yHw1hxsU8L4t0c8pTaOZ7E_vyxNASIkTKNpZt7tYUKF8DjgQ_0xx4bd962hc0B-8MXRCT8QVRaSEsCuCVybmR0Tla2yhdA-hS6H594ao-NNcdGhB-UJWZSz-t1rzwdZBk)
18. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyCYCYv9NgDB_PmLs4YrkGohaRbi9h9Tn8jrHqLu_FOqc-55f61oFRGXqcM9ZBSCed__HYoqLOah_OiK5fNxiZOOB68ahWz852_Rr8kRUW_D1EojU8gwObLwYFzuIV-GNM8pfy1OVtAmwyNA==)
19. [brandeis.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxhj0n4c5PTQEUOyiGJ4Csdfvd3bkTXAKma3tFjYedwO_Gz-D-21KuUt-eZHfVar95zvy_xLx08yLasIjkBb14gcsXcjNzUtOiLLUQCGdaqAV98SBm5WX3BaxtkhjleJXdPQB4WFPffrFN-iqD)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuCvgB5H6Gy3XDwe-aDfgKIz6F_KIb2r3zAwVfoycnkcWfRQaz9nWyCDXjPNKH45TbwwMWX5z5FwEGDK08W5V_-y2mk_4VwsGZcP-VJ_Ep8b3ODNwR)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAyUPiDPFziAOyS5VpL2iyIyz7H94ZCqiUPDEt3wvum3WIZkJxE8bZq3gSKSzFgiDBK5VGuLuYtMBFXECjtKElZ7JZsavJ_95AanIrnZHflYceBCqs)
22. [uni-mainz.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEufHCcGzF3vGTCfNtfyQL27-Ij4fmDBpwnT4iFn_z3Z7bmBx46BNW5UVx0txxSo-LMDjBRUIRiYIvV5YlYSUdauqCKMT8O4gwBefXzNjM657UVtsnVZ0jd0ufXsbcLi8N9ZZvwZuGnioTtlXi7xgHX-SJrt4764KmH9bpNyxc7rTm9-lR5I6DoAKYjP8Cg9l6TqZ-3n0omTaWFzUjATovC4hTvQ5I5v8qw3GUYGzg2v2WCuTZgekUzdUBGvE5ip2NsvBlX)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBQ-wcCnfvWVCZh34liFHGRPKbAxvhwZaArqdcBo44-qu-ZMh3UhknO-l6i_rHSmzTy3_uFP_hrN7eLl-ijcWyn59iXQROgX9q8ZcpeVkUIMgSf2fv)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMyKXdquaV8xkPLNF31GVeNmX2YoyamJ1qICIyGGmBxN7Bi8Tb2tAdQ_52kV3gJM_K8Va5_XcPIxdvG4Ajn-gwhfBHfDjYHvDF8yD2neck1CLtxvI0)
25. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3QOX83_YuKUGpepnUKyNxxCpgBe50oIRNGXBcfHEIQCyhCqgVk5aPEPfNCvt72pBplbt0fq5lZJ1X5Es6Wlvy7c_AakeXH_WTP9o4Vam6H2uYF5ELXL-BnDzVgTrzlNf9GdM=)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYtIlIVdr-NXmHhJhDWEdiNV8shkO2d-9iR_co31iIwdBs_4iUOnnNTD2BqM5KO3IELbEI3wsOCffbbzKcgbIZoI-S7xnLsMr-H3L5RYWQclcb0Bfz)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGC6GZtSQFukWF4tI9D02f8fU3QZoNAHeSnognJoEel4L-Nuoj7Pe_muNgXlA5mUyu8yZfEgSnb-oKVcWnyWZjn2j0O1Yx8CDftFH6fmTgWtpQSzBx3Abe1CpnjfOjd9jAu3NQHQo12xPfgp10USW2sOYDEBbaL-NZpPFkVosgv6kbL)
28. [claymath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3nt1_P9wIxIM_gYMl26ZVrS1SFMLhhhF0bf2INO9cBt82eWLENDpH7RoAOWZx-fqHB8Y1PiWgmApgwaWBPrFJ9p-sNqtuV8rZYO06mt3p6MUlR42NoJbpDhYybbaOw-lj8MY2tbvqUH9aX1Hkoqv3XrTeeg4qcKZb1FIiF2ObGQ==)
29. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjg0TDrXymIIUE269OiBs6HtNDq5ueA3u5RJuvlXUS1XltSTT2LbCe6EhBvpJ-li1mXIHLduvngL4l3yHR7MY9nRYPFIXsX3liO0eZh2XpM3G9RIFVcIcxTuL-JdJnOHLOZNU=)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQER9wnHSOGLxAPhHrQknKqY_EZs84_TnTqMJ65QFJgmfZbfDy3zxoZtaYnO1HIC8in3jHXGq-dgaaL0D5rFAlJQeHafeYmpa6MPhzQ_xpaiKxLZv9z3_eEYEmVNtc75FT9G4okUzliTOtVppOKgkCqoS9rjH4sZaD8myRDuB74bgymCigXGGsrzZq07bAJLvn3Br7UQ3U-R2Vo_mV6B)
31. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSaAX8nC6CB_4LET5uA2P2bRIOHC85lvWMvIsUsmB7aYIkTFsDCO4-ZwFXOIOKaWEwJKu59jHfKOyjZmqBECWZ85IXLFNZzBJnnamDPqMqy1RPsEYTDe4-FYx1AT18vuzXJCPeWQg=)
32. [ucsb.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7NSxJgaXeF18YqhV-50VXHxQjG56auXVWsX6IZtBiswdaqcD66ex8-Q8y8NuIFzzdPc8g7U7U6BM_W9mAvcS6zQKsvqEgLVaNWNC67nGzaW36zyF-zvsbNfeMWbfj)
33. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNcjlpoEeOOrg_2cAxrFpv5JzYGnzQ2ELq87zT7MMV91-5ApXT9TGh1OF2kNeRlTOQkl848SuBt8pUJsjgABy0175BNVFdb7EeZEmtIjsHeoflhJw=)

