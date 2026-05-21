# Local-global compatibility (Skinner-Wiles, Kisin) 2024-2026

**Pythia queue id:** 193
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdIa0VQYXRmZklwZS1fdU1QMC1hUzBBNBIXSGtFUGF0ZmZJcGUtX3VNUDAtYVMwQTQ
**Elapsed:** 250s
**Completed at:** 2026-05-21T17:34:17.774747+00:00

---

# Comprehensive Report on Local-Global Compatibility (Skinner-Wiles, Kisin) and Recent Advances (2024–2026)

*   **Key Points:**
    *   Research suggests that the long-standing "conjugate self-dual" barrier in the Langlands program is being systematically dismantled across both the \(\ell \neq p\) and \(\ell = p\) settings.
    *   It appears certain that the Taylor-Wiles-Kisin patching method remains the definitive mathematical tool for proving modularity lifting theorems, with recent highly successful extensions into definite special orthogonal and symplectic groups.
    *   The mathematical consensus leans heavily toward the validity of the Fontaine-Mazur conjecture even in highly unstable residually reducible cases, building definitively on foundational work by Skinner-Wiles and Kisin.
    *   Evidence strongly supports the resolution of the exceptional zero conjectures for \(GL_3\) via local-global compatibility established for \(p\)-ordinary torsion classes.

At the heart of modern number theory is a massive web of connections known as the Langlands program. It is often described as a "grand unified theory" of mathematics because it connects two seemingly different worlds: the world of symmetries of polynomial equations (Galois theory, providing the "local" and "global" representations) and the world of highly symmetric periodic functions on geometric spaces (automorphic forms). "Local-global compatibility" is the crucial mathematical rulebook ensuring that these two worlds match up perfectly—not just on a massive, global scale, but also when examined closely under a local, prime-by-prime microscope. In recent years, particularly from 2024 to 2026, mathematicians have utilized highly advanced techniques—such as "patching" together pieces of these mathematical spaces (pioneered by Taylor, Wiles, and Kisin) and dealing with highly unstable "residually reducible" equations (pioneered by Skinner and Wiles). These efforts are resolving decades-old predictions about how prime numbers behave within these profound symmetries.

## Introduction to Local-Global Compatibility

The global Langlands correspondence postulates a profound, bijective relationship between algebraic cuspidal automorphic representations \(\pi\) of \(GL_n(\mathbb{A}_F)\) (where \(\mathbb{A}_F\) denotes the adele ring of a number field \(F\)) and strictly compatible systems of \(n\)-dimensional \(\ell\)-adic Galois representations \(r_\ell(\pi): \text{Gal}(\overline{F}/F) \rightarrow GL_n(\overline{\mathbb{Q}}_\ell)\) [cite: 1]. The arithmetic utility of this correspondence relies explicitly on **local-global compatibility**, which dictates that the global representation, when restricted to a local decomposition group at a specific prime \(v\), must precisely match the local Langlands correspondence applied to the local component \(\pi_v\) of the automorphic representation.

Mathematically, if \(v\) is a finite place of \(F\) not dividing \(\ell\), the compatibility asserts that the Weil-Deligne representation associated to the restriction \(r_\ell(\pi)|_{\text{Gal}(\overline{F}_v/F_v)}\) is isomorphic up to Frobenius semisimplification to the Weil-Deligne representation attached to \(\pi_v\) by the local Langlands correspondence. When \(v\) divides \(\ell\) (the \(\ell = p\) case), the compatibility incorporates \(p\)-adic Hodge theory, asserting that the restriction is de Rham (or crystalline/semistable) with Hodge-Tate weights determined by the infinitesimal character of \(\pi_\infty\), and that its associated filtered \((\phi, N)\)-module aligns with the local Langlands parameters [cite: 2, 3]. 

Historically, proving these compatibilities required highly restrictive assumptions, predominantly that the automorphic representation \(\pi\) be conjugate self-dual. However, the theoretical landscape spanning 2024–2026 has witnessed aggressive expansions beyond these constraints, heavily leveraging the foundational modularity lifting and patching techniques established decades prior by Skinner-Wiles and Kisin [cite: 4, 5].

## The Theoretical Bedrock: Skinner-Wiles and Kisin

To understand the breakthroughs of 2024–2026, one must parse the architectural foundations laid by Christopher Skinner, Andrew Wiles, and Mark Kisin. Their work revolutionized the study of universal deformation rings and big Hecke algebras, primarily aimed at resolving the Fontaine-Mazur conjecture.

### The Fontaine-Mazur Conjecture and Residually Reducible Representations

The Fontaine-Mazur conjecture roughly states that any irreducible, continuous, odd, \(\ell\)-adic Galois representation of the absolute Galois group of \(\mathbb{Q}\) that is unramified almost everywhere and potentially semi-stable at \(\ell\) must arise from an automorphic form (such as a modular form). Proving this conjecture generally proceeds via modularity lifting theorems, establishing an isomorphism \(R \simeq \mathbb{T}\), where \(R\) is a universal Galois deformation ring and \(\mathbb{T}\) is a Hecke algebra [cite: 6]. 

A notorious barrier in this pursuit is the **residually reducible case**, where the residual mod \(p\) representation \(\bar{\rho}\) decomposes into a direct sum of characters. Traditional modularity lifting fails here because the deformation functor is no longer easily representable. Skinner and Wiles developed a highly influential method to bypass this, circumventing the reliance on Ribet's level-lowering theorems and instead relying on a complex pro-modularity argument [cite: 4, 5].

Mark Kisin provided another monumental pillar. Kisin's approach to studying potentially Barsotti-Tate deformations and his introduction of Breuil-Kisin modules allowed for the simultaneous patching of deformation rings and Hecke modules [cite: 7, 8]. Kisin's techniques proved that the associated patched modules are finite free over the deformation rings, drastically extending the reach of modularity lifting theorems to intermediate weights and paving the way for Emerton's completed cohomology frameworks [cite: 4, 7, 9].

### Pro-Modularity Breakthroughs (2024–2025)

In recent years, the strategy of Skinner-Wiles and the subsequent geometric advancements by Pan have been generalized to yield new pro-modularity results for totally real fields [cite: 6, 10]. While Deo (2023) proved a big \(R = \mathbb{T}\) theorem over \(\mathbb{Q}\) assuming the cyclicity of specific Galois cohomology groups, extending this to totally real fields was obstructed by the global characteristic formula, rendering the cyclicity assumption absurd [cite: 6, 11].

In late 2024 and 2025, researchers successfully adapted the Skinner-Wiles and Pan strategy to overcome this [cite: 6, 12]. By studying the pro-modularity of universal pseudo-deformation rings without restrictive dimensional assumptions on the cohomology groups, they established a conditional big \(R = \mathbb{T}\) theorem over abelian totally real fields [cite: 6]. The methodology hinges on identifying "potentially nice primes"—primes that become well-behaved after a soluble base change—and utilizing these to link irreducible components of the universal pseudo-deformation ring to the big Hecke algebra [cite: 6]. This fundamentally modernizes the Skinner-Wiles architecture for the 2024-2026 mathematical era.

## The Evolution of Taylor-Wiles-Kisin Patching

The Taylor-Wiles-Kisin (TWK) method is the central engine for proving modularity lifting [cite: 13, 14]. Initially constructed for a fixed pair of types and producing a maximal Cohen-Macaulay module, the method was radically expanded by Emerton, Gee, and Savitt (building on Kisin) to perform patching simultaneously for all coefficients [cite: 13]. 

### Algorithmic Concept of TWK Patching

While patching is a deeply abstract algebraic concept, its underlying logic can be abstracted as an iterative constraint-satisfaction process.

```python
# Conceptual abstraction of the Taylor-Wiles Patching Algorithm
def taylor_wiles_patching(galois_rep, hecke_algebra, deformation_ring):
    # Initialize the patching level
    level = 0
    patched_module = initialize_module(hecke_algebra)
    
    while not is_isomorphic(deformation_ring, hecke_algebra):
        # Find a set of Taylor-Wiles primes Q_N ensuring trivial Selmer group conditions
        Q_N = find_taylor_wiles_primes(galois_rep, level)
        
        # Augment the deformation ring and Hecke algebra with data at Q_N
        R_Q = augment_deformation_ring(deformation_ring, Q_N)
        T_Q = augment_hecke_algebra(hecke_algebra, Q_N)
        
        # Patch the modules by taking a projective limit over the levels
        patched_module = projective_limit_patch(patched_module, R_Q, T_Q)
        level += 1
        
    return patched_module # Yields a finite free module over the deformation ring
```

In 2024 and 2025, the TWK method saw aggressive expansions beyond general linear and definite unitary groups. Specifically, new research developed the automorphic side of the Taylor-Wiles method for **definite special orthogonal (\(SO_n\)) and symplectic (\(Sp_n\)) groups** [cite: 15, 16]. Establishing an \(R = \mathbb{T}\) theorem requires verifying "big image" conditions (adequateness) and constructing Taylor-Wiles primes \(\ell\) such that the local component at \(\ell\) of the irreducible automorphic representation relates strictly to the local Galois representation [cite: 15, 16]. Recent work establishes these local computations using an almost minimal \(R = \mathbb{T}\) theorem for self-dual Galois representations over finite fields that satisfy a rigidity property [cite: 17]. This verifies the Bloch-Kato conjectures for the adjoint motives attached to these representations [cite: 16].

## Local-Global Compatibility at \(\ell \neq p\)

The traditional local-global compatibility at primes \(v \nmid p\) for \(\ell\)-adic representations was robustly established for conjugate self-dual representations by Harris-Lan-Taylor-Thorne and Scholze [cite: 1, 18]. However, for representations that lack the conjugate self-dual property, constructing the Galois representations involves highly complex \(p\)-adic interpolation arguments because these representations do not naturally appear in the étale cohomology of Shimura varieties [cite: 18, 19].

In early 2024, Ila Varma published pivotal results proving local-global compatibility for regular algebraic cuspidal automorphic representations of \(GL_n\) up to semisimplification, crucially dropping the conjugate self-dual requirement [cite: 1, 18]. Varma's proof reconstructs the Galois representations \(r_{p,\imath}(\pi)\) by studying the Hecke action at all primes \(v \nmid p\). By applying the trace formula and utilizing the Bernstein center, Varma showed that at split primes, linear combinations of classical cusp forms of \(G\) yield Hecke eigenvalues that are congruent modulo \(p^k\) to those of the non-self-dual representation, systematically bounding the monodromy and ensuring compatibility [cite: 18].

## Local-Global Compatibility at \(\ell = p\)

The prime \(\ell = p\) introduces immense complexities because the local representation \(\pi_p\) inherently forgets the Hodge filtration, remembering only a coarse shadow (the Weil-Deligne representation) [cite: 2]. Consequently, one must rely on the \(p\)-adic Langlands program and integral \(p\)-adic Hodge theory to bridge the gap [cite: 2].

### Torsion Automorphic Galois Representations

A massive leap in this domain (published in late 2023 and continuing through 2024-2025) is the work of Bence Hevesi. Hevesi proved local-global compatibility results at \(\ell = p\) for the torsion automorphic Galois representations constructed by Peter Scholze, effectively generalizing earlier conjugate self-dual work by Caraiani and Newton [cite: 20, 21, 22]. 

Hevesi's research verifies the Gee-Newton local-global compatibility conjecture at \(\ell = p\) for imaginary CM fields, up to a nilpotent ideal [cite: 20, 21]. The defining novelty of this work is the establishment of local-global compatibility for \(\mathbb{Q}\)-ordinary self-dual automorphic representations associated with arbitrary parabolic subgroups [cite: 20, 21]. This allows researchers to track the behavior of ordinary parts through the intricate machinery of completed cohomology, circumventing the rigid constraints previously imposed by Borel subgroups. 

### The "10-Author Paper" Strategy

Simultaneously, a landmark collaborative effort—often colloquially referred to in 2024–2026 literature as the "10-author paper" (Allen, Calegari, Caraiani, Gee, Helm, Le Hung, Newton, Scholze, Taylor, Thorne)—provided a critical framework for extracting semistable local-global compatibility from highly complex Hecke algebras burdened with nilpotent ideals [cite: 23, 24]. 

The 10-author paper established automorphy lifting for Galois representations over CM fields without assuming conjugate self-duality. Modern 2024-2025 applications use a generalized degree-shifting argument from this paper to address cases where \(p\) ramifies in \(F\), culminating in weak semistable local-global compatibility [cite: 23]. Furthermore, by leveraging the smoothness of characteristic \(0\) local deformation rings, researchers successfully eliminated nilpotent ideals in patched Hecke algebras, validating the vanishing of adjoint Bloch-Kato Selmer groups and proving the rigidity of these representations [cite: 23].

## Exceptional Zero Conjectures and \(\mathcal{L}\)-Invariants (2025)

Perhaps the most arithmetically striking application of local-global compatibility in the 2024–2026 timeframe is the resolution of exceptional zero conjectures. If an elliptic curve has split multiplicative reduction at \(p\), its \(p\)-adic \(L\)-function possesses an "exceptional zero" at \(s=1\), irrespective of the complex \(L\)-value [cite: 25]. The Greenberg-Benois conjecture predicts the exact behavior of the derivative of the \(L\)-function at this zero, relating it to an \(\mathcal{L}\)-invariant [cite: 24, 25].

In August 2025, Daniel Barrera Salazar, Andrew Graham, and Chris Williams released breakthrough work unconditionally proving an automorphic exceptional zero conjecture for \(p\)-ordinary regular algebraic cuspidal automorphic representations of \(GL_3(\mathbb{A})\) that are Steinberg at \(p\) [cite: 24, 26]. Crucially, their work operates without any self-duality assumptions [cite: 24, 26].

The proof requires two massive pillars:
1.  **Automorphic Side**: Using \(p\)-arithmetic cohomology to establish a formula relating the \(p\)-adic \(L\)-function to Gehrmann's automorphic \(\mathcal{L}\)-invariants [cite: 24, 25, 26].
2.  **Galois Side**: Proving the strict equality between the automorphic \(\mathcal{L}\)-invariant and the Fontaine-Mazur \(\mathcal{L}\)-invariant [cite: 24, 25, 26]. 

Achieving this equality inherently demands a robust local-global compatibility at \(\ell = p\) for Galois representations attached to \(p\)-ordinary torsion classes for \(GL_n\). Barrera Salazar et al. confirmed a conjecture of David Hansen in this exact setting, explicitly adopting the strategy from the "10-author paper" to deduce the equality of \(\mathcal{L}\)-invariants for \(n=3\) [cite: 24, 26]. This establishes a purely \(p\)-adic bridge between analysis and arithmetic, marking a watershed moment in the study of higher-rank Birch and Swinnerton-Dyer analogues [cite: 24, 25].

## Geometric and Analytic Frameworks

The period from 2024 to 2026 has heavily favored geometric interpretations of the Langlands program, specifically utilizing stacks and analytic spaces to resolve compatibility issues.

### Extremal Serre Weights and Breuil-Kisin Modules

The weight part of Serre's conjecture relies on characterizing the modularity of Galois representations via Emerton-Gee stacks [cite: 8, 27]. Recent work analyzes Breuil-Kisin modules to enforce structural bounds on the set of modular weights \(W(\bar{r})\) [cite: 8, 27]. By enhancing extremal weights with specialization data, researchers have uncovered Weyl group symmetries: if two extremal weights are related by a simple reflection, the modularity of one mathematically necessitates the modularity of the other [cite: 8, 27]. This combinatorial "weight elimination" relies heavily on the Taylor-Wiles hypotheses and local-global compatibility for generic Serre weights, pushing the bounds of what can be proven for unit groups of division algebras [cite: 8].

### Igusa Varieties and Completed Kirillov Models

In June 2025, Sean Howe introduced a weak local-global compatibility theorem for functions on Caraiani-Scholze Igusa varieties [cite: 28, 29]. By describing the cuspidal functions on the ordinary Caraiani-Scholze Igusa variety for \(GL_2\) as a topological completion of the smooth Kirillov model for classical cuspidal modular forms, Howe identified a variant of Hida's ordinary \(p\)-adic modular forms [cite: 28, 29]. This explicitly links the coinvariants of an action of \(\tilde{\mu}_{p^\infty}\) to local-global compatibility for eigenspaces [cite: 28, 29]. This framework is highly anticipated to yield an analog of Hida theory for natural spaces of \(p\)-adic automorphic forms [cite: 28, 29].

### Fargues-Scholze Shtukas and V. Lafforgue's Global Correspondence

Concurrently, the categorical approach to the \(p\)-adic Langlands program has fused V. Lafforgue's global Langlands correspondence with the Fargues-Scholze semisimplified local Langlands correspondence [cite: 30]. By developing an analytic version of local shtukas—and demonstrating that the analytic moduli problem perfectly aligns with the formal moduli of Kisin-Fargues modules—researchers canonically lifted Fargues-Scholze's construction to a non-semisimplified local correspondence for positive characteristic local fields [cite: 30]. This formally proves local-global compatibility on the level of excursion algebras, successfully answering open questions posed by Fargues, Scholze, Hansen, Harris, and Kaletha [cite: 30]. 

## Summary of Key 2024–2026 Literature

To synthesize the dense theoretical landscape, the following table highlights the most consequential research directly impacting local-global compatibility, the Skinner-Wiles pro-modularity methods, and Kisin patching within the 2024–2026 window:

| Authors | Year | Focus / Contribution | Key Methods / Theories |
| :--- | :--- | :--- | :--- |
| **Ila Varma** | 2024 | Local-global compatibility for regular algebraic cuspidal automorphic representations (\(\ell \neq p\)). [cite: 18] | Removes conjugate self-dual hypothesis; uses trace formula and Bernstein centers. [cite: 1, 18] |
| **Bence Hevesi** | 2023-2024 | Local-global compatibility at \(\ell = p\) for torsion Galois representations. [cite: 20, 21] | Generalizes Caraiani-Newton; uses \(\mathbb{Q}\)-ordinary self-dual representations for parabolic subgroups. [cite: 20, 21] |
| **D. Barrera Salazar, A. Graham, C. Williams** | 2025 | Exceptional zero conjecture for \(GL_3\) and equality of \(\mathcal{L}\)-invariants. [cite: 24, 26] | Employs "10-author paper" strategy for local-global compatibility at \(\ell = p\) without self-duality. [cite: 26] |
| **Sean Howe** | 2025 | Completed Kirillov model and local-global compatibility for Igusa varieties. [cite: 28, 29] | Caraiani-Scholze Igusa formal scheme; topological coinvariants of \(\mu_{p^\infty}\). [cite: 28, 29] |
| **Anonymous/Various (e.g., Deo, Pan)** | 2024-2025 | Pro-modularity in the residually reducible case for totally real fields. [cite: 6, 12] | Adapts Skinner-Wiles and Pan strategies; proves conditional big \(R = \mathbb{T}\) theorem. [cite: 5, 6] |
| **Peng, Whitmore et al.** | 2024-2026 | Taylor-Wiles method for definite special orthogonal/symplectic groups. [cite: 16, 17] | Taylor-Wiles-Kisin patching for non-GL groups; verifies rigidity and adequateness. [cite: 16, 17] |

## Conclusion

The period of 2024 to 2026 marks an era of aggressive generalization in the Langlands program. The rigid constraints of conjugate self-duality and regular weights, which defined the field throughout the early 2000s, are being systematically dismantled. Local-global compatibility—once a fragile theorem requiring highly specific conditions—is now proven across torsion classes, parabolic subgroups, and non-self-dual representations at both \(\ell \neq p\) and \(\ell = p\) [cite: 18, 20].

The mathematical community continues to rely heavily on the geometric patching techniques pioneered by Kisin and the residually reducible frameworks established by Skinner and Wiles [cite: 4, 5, 6]. As seen in the resolution of the exceptional zero conjecture for \(GL_3\) and the extension of Taylor-Wiles methods to symplectic and special orthogonal groups [cite: 16, 24], local-global compatibility remains the indispensable bridge connecting the algebraic geometry of Shimura and Igusa varieties to the profound analytic properties of \(L\)-functions.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHf8CJtdiF6x8vUMy9BWKGlFkp0bJeIGY4DeDohXXnjsocpgolPjoK78Ny_vxAM391yg11W9a90y3DXCtabKstTiRR-TmmhaVvQ2kUxUPi1p7t6rdeO)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-JalCHb3h2u2PrNFtesYsvy0xhYHwDWJL9OGWA2SUgXHCFfV5guXU08jnJo6Tu5D53iNn4WyM9YNG43kmjiMUigETMU1Q_KT6b9fdPzMq5CTRjbkY)
3. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFL-C9uTznPU6-hFfWMRfZMhN6WW8s8eduLDAabE__cdV8B0gzCpNDnsTf--eoycNcp5WEJt5NJKJANupGgQN2fonKBczailU9Q_fEm0qZC61HmCaIpgY3Mqbnihx0mEqazAnKXGptWRw0lc2dQxWUfrAjjomQDv3Nvtx_V5guoV-3yaE5bypGwWKsi4QjkQzwzNzI=)
4. [mathunion.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGApKagftXYm1uYKQcdBJW1bQU3TcqAueDVe9TSqQ10Lt10tDkiqgfRaUDhSeIkx9HF1Wn-LwTjggUjNg2BzLjn_u1zaqd4g8AK8jFp-N5WU4jUqrmX3fxarNOsI9hufoKDGwxfoSGCfjluwpxipqCVdGPN8rzURmh7gxNdVHbvTsF6gOdu6bPtiyO8CgC1ow==)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHU_OqBNrhav-HP1um7U4zXxMIf2mimMyBj_2J3Gfo9V6fQsFcpq0dMilmzzCsW2BP3hww45Zz09PUKoaFvC-89c4vdYNk9-ElQi3s2oZS9KDnx1esiStx1-TQ_ozyIwiVq5AFyJMUkxJJY8oScUTk3zovyek3x3KKe1IVN5Yayz0Wn78CpUtDnVXR_n0SW)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpXXD6V3rzi_gxKvoHpHP28OIHuoHFbBbtWa_ecVW2hhz9yGXUM_my2dvW6zwb0rbBVVintsspHGzNvzyB3YWEHOWDoU8eYD7QE3WS0GycEttB5yv7)
7. [kyoto-u.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbTrCJBKX0-dkIsRQEOZMfE3sw8xt9Bt1ZcKntG-i4q76_QIwHZ8CnNd_yKrz2zbNW6jtwKzJWRP4vsnlUaP6ac-rgiP_GtyI-G6wjTqrZATKXv8N4w575PwTLuIKkdDF0dqSK2mOG02E=)
8. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFVCzo-l-5lKq1EZOB-0ZRUTULW-Ws7fwXQRR22301eN9Q09cV-SP3jm8f_WtcGY5jVno4Pl5Ul4Vuf6sEjXd3nPW8W3sqF-r--hianff43pVxFfvffZ2n-KKhXRluaw==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHajYYE3SR4bxJpL2_EStf7lVNEtL2RS52EE728uOu-ZekOzw__KJhz-nDe6PN7jRLFyN66sLDxXwV-tzoSH49dvhgoUnduHDmcV_oNLyo7drT1J7PC)
10. [u-tokyo.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9Jvi71Q3DcVVqiEJz7_5zp1fkteiBK-e-XgUTlPwVPO0eZUjJxFm5BCklhrW7y5fnK0Qgcp_14ntbaYoB384nJVagf2VsSABLTORUitOQiFzB5CwOg5KBiXxLTIaAeia6ZNEyrbGYGA==)
11. [u-tokyo.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcnUackIIAjzzgQq57MKUAH_PpMn8xykjg9oZITY1RfvepgGlCkDUd6fv3lFK3SxkoMcDI8JDxMkVFpdssYWvK5MkBX56FIBTzfT5tHIv3_v79lR5Y3I0ZWUOikT-PNwJl1SU76bOyK5xW5xhSTkk=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkkxSvD5i9jcItCYPqbQiBXpDXC58v99C3HDHDL7fBAv4h8ZPpO3pbM6yxtkIOul56UagJGq5GFgUe7IoWZmuR5ysIRZPzkyvz7KV9u1JIc-AVZ57Y)
13. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6NBCEPSTxs4npluiO_tSVUhmaX1CePhUd2N-5sB-4MDb8vhG5pH8hD9JI_pr3h0oOqY-b5h1_DEFLL1A7J_azBuf1pXcdYD4vu1aZLdJkAkI1QD35Hh9qJv7IWp_jBaDp_QsFILG0qVOi9jk=)
14. [imperial.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2yj14GeJou5ziDXBTyDuDcIBLsEnIcA6bufwiYjhWVQkRLAQ0ngCw6ZcqeoJW49uoGZJf1DcvMHH1dIRhcJhfifk5shMRnQZtRaHWHQOlJuLmUkQS-YG-6-dfBNCTWJLkbrBwkMQWuxO9Ej_wu_mouuM0ysoAnMbmuSnXBiUaZgo=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFB0arsAPoDLiCYGgzgI-Kc-CFk7tmheTlMH8gdHR0fSAuSqwS6o1jC2q2FTnBwbJW9qE7wOu-7EGQVES9I7o1fj9IEJXpzGolC1dJmH5hLaiGC4rfxJr9D)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEG4R5-BV48nfP_nF8ovPW9Mu955smj3js9a0sTonNRCPaksidCa70omksXZ34oxiZdUw5Jtmy7IUjPgqUx6AFAYg0NGrp8s-O_6Ji1JQG38JMxQCb5)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHh8ugqSrwD7T0-N_1Y_fuQHVCwn9XfBg2aytp9V9f7kiGG_LI0eblPE0MKJIgJ9oDvpoyCb9rhXzMayyFVlXgWQfomR9Oo8eMJ2JLK1TBlr-5s2QX8eQIo)
18. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8J8jN3odtde42g4ldRoeHFts8rqi7BGIFpgyu5SeI-K2oRuAsKyVC_FZWyBhlvuEb-aZbD3TTntOJppKmaCFqI73DXllUs5Uli_rWi32U8yO17A5oMwM7h5vx2AvDlL9kFxad40lj3W2CYt32nSno5aeprwvM-qxQzYELfef9dq7fgFdR8jXAQqXnBYTbEvT979aBmpJNKsBD2MgGsIGFNQ3H0DIIZoBSAWSfjVWlZwtuJ8qsDui3mQFCvYCmSHD4S0p45JscpWhaPSOxGCxMqVMRHKY9MVj7d5H_UzO6VV3j3Ye_sxex6G2x-ANpHgiX2TVOdJDyD_X0xBq4NtiRtK2hexc=)
19. [imperial.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpF2jc0mrF9i9tCqJYz9AV-lVPfOg5cJdIbiKngCuaBIONbYFd_MolugNJXGNx0n2BYF_ZQ_cGNRWjty_70pKUxLGdCKd8MhNVi86kkdNkMM9ABvfk7EwZ35kpLL37FlP4dlJP8tLNfaS7p7MhspZM2XhHQ9hVHhwNxg==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQVx0WmpMn2lckpG0TbwN4PjWanrnM0AwR6WFD2YEFCehF3PjL9GItwpA7sRZ88YjsqcS8GUnz_6LRn-JZE1EUlNdfqmmxExr-nvHE1Z01EsGFUmph)
21. [kcl.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbtoG0F8vu5W2YFZvUrUQzni3iVf9Z3eO2I-dzyJhkC8nJU5ZXrI1O7QxGKHsK0mcdw8jA5Y9iSk4PjAIlaweDW_hTvxbtVvM2m8GHZdhJlBrrsHa0_k18ubZ8rqN9f6p2oc1uoaa6tma3hbG4FjnmF88BWVT8SVbaL5DGD68UcQ1QGtQNvWsDq_agGYRpgI1pNU-OUQn09EUg84uTxm4-z2cnFA==)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFP6kdfal8GTwT9cuMgw37zHpwW8lOEE1_x4d8HZsDd3NhFKPar9f8NFniz5rSZ4h3tgHoZ90hPX54POxkFpqTCjfoI5yI_mcIKXeSI16WhqugA7N8y3ooKRDhzmLbtyB-I65M6fVux13uxeQmTnXNrY_s8ToygtoGVg_d9jVIYKtlvGwNqBd9brOsTfyvt0xI4oV3df3Lb_R9E2Cpn)
23. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKKb2pZhGlffWnw_LbOHv7JM-ih8A7UMJ-A6QXdr7g8x3rg1tQCgJvq_mj-x5IP9i8ElNCrkI8Z9Pep7MN2S1JR5mRbfUiM8U4oBDnpPA1qn79HutL8GnN9PJ2y88iwQJjjlHaZ23seaoCKtPmcg==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQ9OgoINNieMfoWiMNGM5ZVSduB1jmxfn3SpDtECFMgxArfZn63sdR4-ICmtSqXqD4d_ljiK2eKA6Y8En8eYHvcq4ao_itsNSaJXTRPP-uch7jq4bY)
25. [antoniolei.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXLH1j-or1jCJqJK7CuRHAM4oxGzMruHJwviCtr1Nu9xR7Ktx3E7nNS164ptl6iFSOoeLphMZ-K0DKp_pjJu_ugJf6c8Ecflydi50AX7Fdf7RboebH2bjOBeNDBFAKtmLlFqtYb7SG-snah3OEELQOpgV1a-2GmkKKqlqgxEc=)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHl6LGPF5OZ3e0jF_iuAhVwTFwjqyrx-_6vwzGX5qPTCnd53h4nTL8S2b8bdotU3Y_86MqrfAsppp8VtqJ6Mwe3ujrVouh-YFwZ-gQc_JvvtbyhLIfN)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEZ2xs6MhLlfcMb-9CvN54-BzxgpZBxnNomVsL15Se94Kdqvcobu4izQQBKJ6qLrXjNZsu5xecYdK7jyJQc-dW0F6ibaUOerS8IK0Uev0OLVa0L01NiAfI)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2ARe9akoL3oLgKUUx2OvRiFlVbcgJyab25D0GaZKxwd1mTPZjqNvB1vV3zT236bDjinpRRbpZvZqgQCKjwTaRCxI9M3M7wFyPqDXOBM--e225Qay0)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3JqhrVYXD1rrxZPJl-paW_AuoA7Mi0Q3LaMGO4weaygcLeu-sOin8OfYEsEJlUjY-KU0BUjPbn1U1t_wc8pIST-CyA592d4S5xVFB10AQAenzNaHK)
30. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHo88vx_O24vZuhDRHRG4CcKOzvYVk0-DkgFWcgM5k0fDNiUCRBnN1JZaJ7mrdEXwyTtNGZgPNlafpfo5tJ4E8RLH71HPmk5EieZTIroXYyo1YdFE5yZNwN_7HgxCllUmE=)

