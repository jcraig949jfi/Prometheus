# Galois representations modulo small primes (mod 2, mod 3, mod 5) 2024-2026 frontier

**Pythia queue id:** 167
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdaemNQYXV6ZEN2eThfdU1QeHNHM29RZxIXWnpjUGF1emRDdnk4X3VNUHhzRzNvUWc
**Elapsed:** 253s
**Completed at:** 2026-05-21T16:52:53.643422+00:00

---

# The 2024-2026 Frontier of Galois Representations Modulo Small Primes (Mod 2, Mod 3, Mod 5)

**Key Points:**
*   Research suggests significant advancements have been made in computing and understanding Galois representations modulo the small primes 2, 3, and 5 during the 2024-2026 period.
*   It seems likely that the generalized Riemann hypothesis (GRH) continues to play a vital role in conditionally proving the non-existence of low-dimensional mod 2 and mod 3 Galois representations unramified outside their respective primes.
*   The evidence leans toward substantial algorithmic breakthroughs in probabilistic methods used to compute mod 5 Galois images for genus 2 curves, expanding our ability to bypass computationally intractable bounds.
*   Recent breakthroughs appear to have definitively solved the long-standing lifting problem, demonstrating that there exist modulo \(p\) representations that do not lift to modulo \(p^2\), thereby answering fundamental questions posed by Serre and Khare.
*   The study of 2-adic crystalline representations and mod-2 local Langlands correspondences remains highly complex, though new exact parameterizations for small slopes have recently emerged.

**Context and Complexity**
The study of Galois representations forms the bedrock of modern arithmetic geometry and algebraic number theory, acting as the primary bridge between algebraic structures (such as elliptic curves and abelian varieties) and automorphic forms (such as modular forms and Hecke characters). When these representations are evaluated modulo small primes—specifically \(p = 2\), \(3\), and \(5\)—the mathematics becomes exceptionally delicate. Small primes introduce "wild" ramification, exceptional isomorphisms in low-dimensional finite groups, and severe technical obstructions in the Taylor-Wiles patching methods traditionally used to prove modularity lifting theorems. 

**The Scope of Recent Breakthroughs**
Between 2024 and 2026, the frontier of this field has witnessed remarkable theoretical and computational progress. Researchers have tackled the lifting problem for absolute Galois groups, the algorithmic classification of mod 5 representations for Jacobians of hyperelliptic curves, and the automorphy of mod 2 representations associated to totally real fields. While some results rely unconditionally on class field theory and local Langlands correspondences, others necessitate the assumption of the Generalized Riemann Hypothesis (GRH) to achieve sharp bounds on number field discriminants. This report comprehensively synthesizes the latest academic literature, detailing the theoretical machinery, algorithmic methodologies, and structural theorems that define the current mathematical landscape.

## Introduction to Galois Representations Modulo Small Primes

Galois representations encode the action of the absolute Galois group \( G_K = \text{Gal}(\bar{K}/K) \) of a number field \( K \) on finite-dimensional vector spaces. When these vector spaces are over finite fields \(\mathbb{F}_p\), the resulting representations \(\bar{\rho}: G_K \to \text{GL}_n(\mathbb{F}_p)\) are known as residual or modulo \( p \) Galois representations [cite: 1, 2]. These representations arise naturally from the \(p\)-torsion points of algebraic groups, such as the \(n\)-torsion subgroup \(E[n]\) of an elliptic curve \(E\), which forms a \(\mathbb{Z}/n\mathbb{Z}\)-module isomorphic to \(\mathbb{Z}/n\mathbb{Z} \oplus \mathbb{Z}/n\mathbb{Z}\) [cite: 3]. 

The study of these representations modulo the specific small primes \(p = 2, 3, 5\) poses unique challenges and yields unique structures. For \(p = 2\), the group \(\text{GL}_2(\mathbb{F}_2)\) is isomorphic to the symmetric group \(S_3\), a solvable group. For \(p = 3\), \(\text{PGL}_2(\mathbb{F}_3)\) is isomorphic to \(S_4\). For \(p = 5\), the representation image often relates to the icosahedral group \(A_5\) or the symmetric group \(S_5\), leading to profound connections with the Langlands-Tunnell theorem and the modularity of elliptic curves [cite: 2, 4]. Furthermore, the ramification behavior at these small primes is notoriously difficult to control. For instance, the traditional Taylor-Wiles method for proving modularity lifting often fails or requires massive technical workarounds when \(p=2\) due to the failure of certain Galois cohomology groups to vanish and the presence of trivial representation components. 

From 2024 to 2026, the mathematical community has pushed the boundaries of what is known about these representations. The literature is characterized by a dual approach: a purely theoretical push to resolve long-standing conjectures (such as the lifting problem and the weight part of Serre's conjecture) and a computational push utilizing databases like the L-functions and Modular Forms Database (LMFDB) to algorithmically classify the Galois images of genus 2 curves [cite: 5].

## The Non-Existence of Small-Dimensional Galois Representations Unramified Outside \(p\)

A classic and foundational problem in algebraic number theory is determining the existence or non-existence of continuous, irreducible Galois representations \(\bar{\rho}: G_{\mathbb{Q}} \to \text{GL}_n(\mathbb{F}_p)\) that are unramified outside a given prime \(p\). The seminal results in this area were provided by Tate for \(p=2\) and Serre for \(p=3\), who proved the non-existence of such irreducible representations in dimension \(n=2\) [cite: 6, 7]. These classical proofs rely heavily on bounding the discriminant of the number fields cut out by the representation and applying Odlyzko's discriminant bounds to show that no such field can exist [cite: 6].

### Advancements by Ghitza and Yamauchi (2025)

In a major 2025 preprint, Alexandru Ghitza and Takuya Yamauchi refined the arguments initially proposed by Hyunsuk Moon to significantly extend these non-existence theorems to higher dimensions, albeit under the assumption of the Generalized Riemann Hypothesis (GRH) [cite: 7, 8]. 

Their work focuses on establishing the non-existence of:
1.  Irreducible mod 2 Galois representations unramified outside 2 of dimensions \(n \leq 4\).
2.  Totally real irreducible mod 2 Galois representations unramified outside 2 of dimensions \(n \leq 8\).
3.  Totally real irreducible mod 3 Galois representations unramified outside 3 of dimensions \(n \leq 4\) [cite: 1, 8].

The methodology depends on analyzing the \(p\)-Sylow structure of the Galois group \(G = \text{Gal}(K/\mathbb{Q})\), where \(K\) is the field cut out by the kernel of the representation \(\bar{\rho}\). By leveraging the property of \(p\)-length (a group-theoretic measure of the complexity of the \(p\)-Sylow subgroups within solvable or \(p\)-solvable groups), Ghitza and Yamauchi obtain tight upper bounds on the root discriminant \(|d_K|^{1/[K:\mathbb{Q}]}\) of the field \(K\). 

For representations where the Galois group \(G\) has \(p\)-length 0 (meaning \(K\) is tamely ramified at \(p\)), the situation is resolved unconditionally. For example, if \(p \in \{2, 3\}\) and the \(p\)-length is 0, the root discriminant \(|d_K|^{1/n}\) is strictly bounded. Odlyzko's unconditional tables show that for \(p=2\), the degree \(n\) must be less than 3, rendering the Galois group abelian and thus incapable of supporting an irreducible representation of dimension strictly greater than 1 [cite: 7]. 

However, for wild ramification (higher \(p\)-length), the unconditional Odlyzko bounds are insufficient to force a contradiction. By assuming GRH, the discriminant bounds improve drastically. Ghitza and Yamauchi utilized these conditional bounds in tandem with the Jones-Roberts database of number fields and explicit exhaustive group searches implemented in Magma to eliminate all possible candidate Galois groups [cite: 7]. 

### Symplectic Representations and Self-Dual Cases

Furthermore, the 2025 study investigates symplectic representations taking values in \(\text{GSp}_4(\mathbb{F}_2)\). Ghitza and Yamauchi unconditionally prove that the image of any irreducible mod 2 representation \(\bar{\rho}: G_{\mathbb{Q}} \to \text{GSp}_4(\mathbb{F}_2)\) that is unramified outside 2 must be "large" (i.e., it cannot be a small proper subgroup). Subsequently, by applying GRH, they deduce that no such representations can exist at all [cite: 7, 8]. 

In higher dimensions, they tackle self-dual 2-ramified representations into \(\text{GL}_5(\mathbb{F}_2)\). They define a representation to be of "length 2" in the representation-theoretic sense—meaning the Galois module possesses a single irreducible submodule and the resulting quotient is also irreducible. Under GRH, they establish that there exist no self-dual 2-ramified representations \(\bar{\rho}: G_{\mathbb{Q}} \to \text{GL}_5(\mathbb{F}_2)\) of length 2 [cite: 1, 7]. This length condition is the sharpest possible, because any 2-ramified self-dual representation into \(\text{GL}_5(\mathbb{F}_2)\) will inherently contain the trivial representation as a direct factor, meaning absolute irreducibility in dimension 5 is impossible [cite: 7].

## Automorphy of Mod 2 Representations for Genus 2 Curves

While the non-existence of globally unramified-outside-2 representations is a profound negative result, the study of mod 2 representations arising geometrically over totally real fields has seen positive structural breakthroughs. A central theme in the Langlands program is establishing the automorphy of Galois representations—proving that a representation arising from algebraic geometry (like the étale cohomology of a variety) corresponds to an automorphic form.

In 2024, Alexandru Ghitza and Takuya Yamauchi published a landmark paper in the *Journal de Théorie des Nombres de Bordeaux* concerning the automorphy of mod 2 Galois representations associated with genus 2 hyperelliptic curves over totally real fields [cite: 9, 10]. 

### The Geometric Setup and \(S_6\) Isomorphisms

Let \(C\) be a genus 2 hyperelliptic curve defined over a totally real field \(F\). The curve can be given by an affine equation of the form \(y^2 = f(x)\), where \(f(x)\) is a separable polynomial of degree 6 over \(F\) (e.g., \(f(x) = x^6 + a_1 x^5 + \dots + a_6\)) [cite: 10]. The Jacobian variety \(J\) of \(C\) is an abelian surface. The 2-torsion subgroup \(J[cite: 11](\bar{F})\) is an \(\mathbb{F}_2\)-vector space of dimension 4, equipped with a non-degenerate alternating Weil pairing [cite: 10]. The action of \(G_F\) on \(J[cite: 11]\) yields a modulo 2 Galois representation:
\[ \bar{\rho}_{C,2}: G_F \to \text{GSp}(J[cite: 11], \langle \cdot, \cdot \rangle) \simeq \text{GSp}_4(\mathbb{F}_2) \]
[cite: 9, 10].

A remarkable exceptional isomorphism in group theory states that \(\text{GSp}_4(\mathbb{F}_2)\) is isomorphic to the symmetric group \(S_6\). Geometrically, this isomorphism is realized by the action of the Galois group on the 6 roots of the hyperelliptic polynomial \(f(x)\). The splitting field \(F_f\) of \(f(x)\) gives an embedding \(\text{Gal}(F_f/F) \hookrightarrow S_6\). The mod 2 representation \(\bar{\rho}_{C,2}\) factors through this Galois group [cite: 10].

### Residual Automorphy to Hilbert-Siegel Modular Forms

The main theorem proven by Ghitza and Yamauchi states that if the image of \(\bar{\rho}_{C,2}\) is isomorphic to \(S_5\) and acts transitively on the set \(\{1, 2, 3, 4, 5, 6\}\) under the chosen isomorphism \(\text{GSp}_4(\mathbb{F}_2) \simeq S_6\), then the representation is residually automorphic [cite: 9, 10].

To be precise, there exists a Hilbert-Siegel Hecke eigen cusp form \(h\) on \(\text{GSp}_4(\mathbb{A}_F)\) of parallel weight two such that its associated mod 2 Galois representation \(\bar{\rho}_{h,2}\) is isomorphic to \(\bar{\rho}_{C,2}\) [cite: 9, 10]. 

The proof methodology avoids traditional massive machinery like the Taylor-Wiles-Kisin modularity lifting theorems, which are notoriously difficult for \(p=2\) due to the failure of certain multiplicity-one hypotheses and crystalline conditions. Instead, the authors apply unconditional results to construct a corresponding automorphic cuspidal representation via congruences between different types of automorphic forms [cite: 10]. They state that if the image is \(A_5\), the representation \(\bar{\rho}_{C,2}\) is reducible, allowing naive attachment to a non-cuspidal automorphic representation, but through sophisticated congruence methods, they ensure the existence of a *cuspidal* representation for the \(S_5\) case [cite: 10]. 

They further weakened the condition in subsequent corollaries, requiring only that the image be isomorphic to the Frobenius group \(F_{20} \simeq C_4 \ltimes C_5\), or to \(A_5\) under the condition that the base field \(F/\mathbb{Q}\) has an even degree [cite: 10]. This work represents a massive step forward in the residual automorphy of abelian surfaces, providing explicit families of examples using classical results by Hermite and extensions linked to 5-division points on elliptic curves [cite: 10].

## Probabilistic Methods and Computational Frontiers for Mod 5 and Mod 3 Images

While theoretical automorphy theorems handle specific image types (like \(S_5\) in \(S_6\)), the generic case for abelian surfaces remains computationally elusive. For an abelian surface \(J\) defined over \(\mathbb{Q}\), the generic mod \(\ell\) representation \(\bar{\rho}_{J,\ell}: G_{\mathbb{Q}} \to \text{GSp}_4(\mathbb{F}_\ell)\) is surjective [cite: 5]. Identifying whether a given curve exhibits a smaller (non-surjective) image implies the presence of extra arithmetic structure, such as real multiplication, complex multiplication, or unexpected endomorphisms [cite: 5].

For elliptic curves, the generic mod 5 image is \(\text{GL}_2(\mathbb{F}_5)\), a group of order 480. Computing the full 5-torsion field directly requires working in a degree 480 number field, which is vastly beyond what is feasible in computer algebra systems like Magma for reasonable time frames [cite: 11]. For genus 2 curves (abelian surfaces), the situation is astronomically more complex: the group \(\text{GSp}_4(\mathbb{F}_5)\) has order 1,440,000, making direct field extension computations impossible for a large database of curves [cite: 5].

### Mathilde et al. (2025): Mod 5 Galois Images of Genus 2 Curves

To bridge this computational gap, an October 2025 paper by Mathilde et al. (building on techniques by Sutherland, Banwait, and Chidambaram) introduced highly optimized probabilistic methods to determine the mod 5 Galois images for Jacobians of genus 2 curves [cite: 5]. 

The core philosophy of this probabilistic method is to bypass the explicit computation of the \(\ell\)-torsion field. Instead, the algorithm samples the conjugacy classes of the Frobenius elements \(\text{Frob}_p\) across a wide array of primes \(p\). By Chebotarev's Density Theorem, the distribution of the characteristic polynomials of \(\bar{\rho}_{J,5}(\text{Frob}_p)\) will asymptotically mimic the distribution of characteristic polynomials across the actual Galois image subgroup \(H \leq \text{GSp}_4(\mathbb{F}_5)\) [cite: 5].

Mathilde et al. outline a rigorous algorithm implemented in Magma:
1.  **Lattice Initialization**: Compute the entire subgroup lattice of \(\text{GSp}_4(\mathbb{F}_5)\). Initialize the set of "possibilities" as all conjugacy classes of subgroups that possess a surjective similitude character and an order 2 element with similitude character \(-1\) (representing complex conjugation) [cite: 5].
2.  **Frobenius Sampling**: For good primes \(p\) in a selected range (e.g., \(p \in [10000, N]\)), compute the characteristic polynomial of the Frobenius endomorphism acting on the mod 5 Jacobian [cite: 5].
3.  **Distribution Matching**: Compute the distribution of pairs \((P_c, d_1)\), where \(P_c\) is the characteristic polynomial and \(d_1\) is the dimension of the 1-eigenspace. Match this empirical distribution against the theoretical distributions of the candidate subgroups [cite: 5].

The team successfully applied this method to the L-functions and Modular Forms Database (LMFDB). They probabilistically computed \(\bar{\rho}_{J,5}\) for the Jacobians of 95% of the genus 2 curves in the LMFDB for which the mod 5 image was previously unknown. For the remaining 5%, they determined the exact order of the image and provided a highly constrained short list of candidate subgroups [cite: 5].

The paper features a main theoretical theorem providing an *effective constant* \(N\) (depending only on the curve \(C\)) such that sampling primes up to \(N\) rigorously guarantees the output list contains the true mod 5 image [cite: 5]. However, because this effective bound \(N\) is computationally intractable in practice, the practical algorithm relies on high-confidence probabilistic bounds [cite: 5].

### Chidambaram's Work on Mod 3 Images

Parallel to the mod 5 advancements, work by S. Chidambaram (2024-2026) has thoroughly mapped out the mod 3 Galois images of principally polarized abelian surfaces over the rationals [cite: 5, 12]. Chidambaram developed explicit algorithms and Magma code to compute the mod 3 Galois image, pushing the boundary of the LMFDB's completeness [cite: 12]. Furthermore, Chidambaram proved that there exist mod \(p\) Galois representations that do not arise from abelian varieties, clarifying the boundary between geometric representations and abstract Galois representations [cite: 12].

## The Lifting Problem: From Mod \(p\) to Mod \(p^2\)

One of the most spectacular theoretical developments during the 2024-2026 period is the resolution of the "Lifting Problem" for Galois representations. The problem asks: Given a continuous \(n\)-dimensional residual representation \(\bar{\rho}: G_F \to \text{GL}_n(\mathbb{F}_p)\), can it be lifted to a continuous representation \(\rho: G_F \to \text{GL}_n(\mathbb{Z}/p^2\mathbb{Z})\) (or more generally, to the ring of \(p\)-typical length 2 Witt vectors \(W_2(k)\))?

This question is intrinsically tied to deformation theory. If representations cannot be lifted modulo \(p^2\), then the entire machinery of Mazur's deformation rings collapses for those specific representations, as they admit no characteristic zero lifts. Serre and Khare specifically posed the question of whether such non-liftable representations exist. Florence formulated a conjecture regarding the conditions under which lifting might always be possible [cite: 13].

### Resolution by Merkurjev and Scavia (2024-2026)

In a sequence of papers published between 2024 and 2026, Alexander Merkurjev and Federico Scavia definitively solved the lifting problem in every dimension and in every characteristic [cite: 14, 15, 16]. 

They proved that for every odd prime \(p\), every integer \(n \geq 3\), and every field \(F\) containing a primitive \(p\)-th root of unity, there exists a continuous \(n\)-dimensional mod \(p\) representation of the absolute Galois group of the rational function field \(F(x_1, \dots, x_p)\) that **does not lift** modulo \(p^2\) [cite: 13, 17]. 

This result explicitly answers the question of Khare and Serre in the affirmative (non-liftable representations do exist) and definitively disproves Florence's conjecture [cite: 13]. Furthermore, in characteristic 2, they constructed continuous 5-dimensional Galois representations modulo 2 which do not lift modulo 4 [cite: 17].

### Negligible Galois Cohomology

The theoretical innovation allowing Merkurjev and Scavia to solve this problem is their complete determination of "negligible classes" in Galois cohomology, a concept initially introduced by Serre [cite: 13, 18]. 

For a finite group \(H\) and a finite \(H\)-module \(A\), the second cohomology group \(H^2(H, A)\) classifies group extensions. A cohomology class \(\alpha \in H^2(G, M)\) is deemed *negligible* over a field \(F\) if, for every field extension \(K/F\), every continuous homomorphism from the absolute Galois group \(G_K \to G\) lifts to a homomorphism into the extension group \(\tilde{G}\) defined by \(\alpha\) [cite: 14, 18]. 

Merkurjev and Scavia provided an exact formula generating the subgroup of negligible classes \(H^2(H, A)_{\text{neg}, F}\) over fields with enough roots of unity. They proved that the negligible subgroup is generated by the images of specific corestriction maps from stabilizers of elements in the module [cite: 14]. 

By translating the lifting problem of \(\text{GL}_n(k)\) to \(\text{GL}_n(W_2(k))\) into an embedding problem characterized by a specific cohomology class in \(H^2(\text{GL}_n(k), M_n(k))\), they demonstrated that this class is *not* negligible for the specified parameters (\(p\) odd, \(n \geq 3\)). Thus, they could guarantee the existence of a field extension (specifically the generic extension \(F(x_1, \dots, x_p)\)) where the corresponding Galois representation fails to lift [cite: 14, 15]. This establishes a permanent structural boundary on the universal applicability of \(p\)-adic lifting techniques in geometric Galois theory.

## Crystalline Representations Modulo 2 and Local Langlands

While global Galois representations are studied over number fields, their local behavior at specific primes \(p\) (i.e., restricting the representation to the decomposition group \(G_{\mathbb{Q}_p} = \text{Gal}(\bar{\mathbb{Q}}_p/\mathbb{Q}_p)\)) is equally critical. For a prime \(p\), local representations that come from geometry are "crystalline," a condition formulated in \(p\)-adic Hodge theory implying that the representation behaves well with respect to Fontaine's rings of periods. 

Computing the modulo \(p\) reduction of a \(p\)-adic crystalline representation is notoriously difficult. For odd primes, extensive literature exists detailing the semi-simplified reduction of 2-dimensional crystalline representations. However, the prime \(p=2\) has historically been avoided due to severe technical anomalies in characteristic 2 [cite: 19, 20].

### Bhattacharya and Venugopal (2026)

In May 2026, Shalini Bhattacharya and Arathy Venugopal released a comprehensive 53-page study calculating the explicit form of the semisimplified reduction modulo 2 of 2-adic crystalline Galois representations at small slopes [cite: 21, 22]. 

Let \(E\) be a finite extension of \(\mathbb{Q}_2\), and let \(a_2 \in E\) with positive 2-adic valuation \(\nu = v(a_2) > 0\). For an integer weight \(k \geq 2\), let \(V_{k, a_2}\) denote the unique irreducible two-dimensional crystalline representation of \(G_{\mathbb{Q}_2}\) with Hodge-Tate weights \(0\) and \(k-1\), such that the characteristic polynomial of the crystalline Frobenius is \(X^2 - a_2 X + 2^{k-1}\) [cite: 19, 20]. The valuation \(\nu\) is referred to as the "slope" of the representation.

By choosing a Galois-stable integral lattice inside \(V_{k, a_2}\), one can reduce the representation modulo the maximal ideal to obtain a representation over a finite field of characteristic 2. The semisimplification of this reduction, denoted \(\bar{V}_{k, a_2}\), is independent of the choice of lattice [cite: 19]. 

Bhattacharya and Venugopal utilize the compatibility between the 2-adic Local Langlands Correspondence (LLC) and the mod-2 LLC to compute \(\bar{V}_{k, a_2}\) explicitly for slopes \(\nu \in (0, 1]\) [cite: 21]. 

### The Bruhat-Tits Tree and Hecke Operators for \(p=2\)

The technical heart of their paper involves analyzing the action of Hecke operators on the Bruhat-Tits tree for \(\text{PGL}_2(\mathbb{Q}_2)\). The tree for \(p=2\) has uniform valency 3, and its vertices correspond to integral lattices in \(\mathbb{Q}_2^2\) up to homothety [cite: 20]. 

The reduction of the representation is intrinsically tied to the reduction of the corresponding local automorphic representation under the LLC. The authors identified critical parameters \(\alpha'(k, a_2)\) and \(\alpha(k, a_2)\) that fully determine the shape of \(\bar{V}_{k, a_2}\) for slopes in the range \((0, 1)\) and exact slope \(1\), respectively [cite: 21]. 

A striking dichotomy discovered for \(p=2\)—which starkly contrasts with the behavior at odd primes—is that if the weight \(k\) is even, the reduction \(\bar{V}_{k, a_2}\) *must* be irreducible. Conversely, if \(\bar{V}_{k, a_2}\) is reducible, then \(k\) must be odd, and the slope must be exactly \(v(a_2) = 1/2\) [cite: 20, 22]. This "zig-zag" structural anomaly highlights why \(p=2\) requires completely separate theoretical frameworks from odd primes and closes a major gap in the local Langlands literature for small slopes [cite: 22].

## Modularity, Serre's Conjecture Extensions, and Weight Parts

Serre's Modularity Conjecture (proven by Khare and Wintenberger in 2009 for the rational numbers \(\mathbb{Q}\)) postulates that every odd, continuous, irreducible two-dimensional mod \(p\) Galois representation of \(G_{\mathbb{Q}}\) arises from a classical modular form [cite: 2, 23]. The modern frontier of this field revolves around extending Serre's conjecture to arbitrary number fields (especially totally real fields) and rigorously establishing the "weight part" of the conjecture, which predicts exactly *which* weights of modular forms can give rise to a specific Galois representation.

### Projective Representations Modulo 3 and 5 over Totally Real Fields

In an influential paper extending Serre's conjecture, Patrick B. Allen, Chandrashekhar B. Khare, and Jack A. Thorne proved the modularity of projective representations \(\bar{\rho}: \text{Gal}(\bar{K}/K) \to \text{PGL}_2(\mathbb{F}_p)\) over totally real number fields \(K\), focusing specifically on the small primes \(p=3\) and \(p=5\) [cite: 2].

A representation is of "Serre type" if it is absolutely irreducible and totally odd (the determinant of complex conjugation at every real place is \(-1\)). For \(p=3\), the representations often correspond to the Galois action on the 3-torsion points of an elliptic curve. The authors successfully verified the modulo 3 residual automorphy over totally real fields without relying on the traditional Langlands-Tunnell theorem, instead utilizing the Saito-Shintani lifting for holomorphic Hilbert modular forms [cite: 2].

For \(p=5\), the projective image in \(\text{PGL}_2(\mathbb{F}_5)\) can be non-solvable (isomorphic to \(A_5\)). The residual automorphy of such representations conventionally represents a massive hurdle. However, Allen, Khare, and Thorne achieved this by carefully studying the characteristic 0 lifts of these residual representations. They demonstrated that the automorphy of the lift \(\rho: G_K \to \text{GL}_2(\mathbb{F}_5)\) can be deduced using 2-adic Galois representations that are residually dihedral, relying on automorphic induction rather than the Langlands-Tunnell theorem [cite: 2]. This provides a highly robust framework for proving modularity without the strict conditions previously required.

### The Geometric de Rham Weight Part of Serre's Conjecture

To formulate Serre's conjecture over totally real fields, one must define the "weights" of the Hilbert modular forms involved. Classically, this is done using Serre weights (irreducible \(\mathbb{F}_p\)-representations of the finite group \(G(\mathbb{F}_p)\)) and the étale cohomology of Shimura varieties [cite: 24]. 

In a January 2026 preprint, Martin Ortiz proposed a revolutionary geometric version of the weight part of Serre's conjecture utilizing the *de Rham cohomology* of the special fibers of Shimura varieties [cite: 24]. Ortiz conjectures that the set of weights defined via de Rham cohomology, \(W_{\text{dR}}(\mathfrak{m})\), is exactly equal to the classical set of Serre weights \(W(\mathfrak{m})\) defined via étale cohomology [cite: 24].

Ortiz proved this equivalence for generic weights and generic non-Eisenstein eigensystems specifically for compact \(U(2, 1)\) Shimura varieties where the local group is \(\text{GL}_3\). The proof relies on establishing a "generic concentration in middle degree" for the mod \(p\) de Rham cohomology with coefficients [cite: 24]. He constructs an exact de Rham realization functor \(\Psi\) mapping bounded derived categories of representations into the log-crystalline site of the toroidal compactification of the Shimura variety. By leveraging generalized mod \(p\) Bernstein-Gelfand-Gelfand (BGG) decompositions, Ortiz demonstrates that the geometric structural properties of Shimura varieties in characteristic \(p\) directly govern the weight parameters of the attached Galois representations [cite: 24]. 

Furthermore, a separate 2025 study on mod \(p\) Hilbert modular forms (viewed as sections of automorphic line bundles on Hilbert modular varieties) proved that for a Hecke eigenform of *arbitrary* weight, there inherently exists an associated two-dimensional representation of the absolute Galois group of the totally real field \(F\) [cite: 23]. This resolves major difficulties in dealing with non-cohomological weights and allows the formulation of precise conjectures predicting the minimal weights of eigenforms corresponding to specific Galois representations, even when \(p\) is highly totally ramified in the base field [cite: 23].

## Conclusion

The frontier of research surrounding Galois representations modulo the small primes 2, 3, and 5 from 2024 to 2026 demonstrates an unprecedented convergence of theoretical and computational mathematics. Unconditional proofs mapping the exact structural dichotomies of 2-adic crystalline representations [cite: 22] now sit alongside conditional proofs relying on GRH to map the absolute bounds of ramification [cite: 7]. The resolution of the lifting problem by Merkurjev and Scavia provides a definitive ceiling on deformation theory [cite: 15], while probabilistic sampling algorithms applied to the LMFDB break open the previously intractable problem of computing mod 5 images for genus 2 curves [cite: 5]. Through the integration of de Rham cohomology on Shimura varieties and novel applications of the local Langlands correspondence, the mathematical community continues to successfully untangle the deepest arithmetic structures encoded within small characteristic representations.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsRTKaLMcuEEmS1NaPmaudUkdH8c7wm8oOU6RgK7vsx_gE4FcWWuKNYRxgnp8Cwj1MSX3pDONVnvFjGUXIBpOtRiiMfvpTf0qREh5l0yQHJG3Rhz-IGsxb)
2. [pnas.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEM4oAs2cEW1G3127ymfdDeGf2A9BOpZbIKxk0TwFxmVsqSspTNB1mOfuOZLwofDw_pneg5o4DZd5Sm2TyJfR6FXVciuj0I0tfFIpTYLiZ4RCAagKfvcLoK7mn4TecSWUGmVfmxMg==)
3. [concordia.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFy33eLLNUowPqxET_4FTlOaoQA6-B5m_UmQ3P3cpODh3N6fOGb_TK30BjmamGPBSmIj-9uBsi6Hnl9oZsxLz6m8fdbn_iynpF_rUoimgAt2jT0Vf9qUmX70FDEQ2KFESLPoluwpxMEbyhRYvLFuaInsnoXv2PstbM_XMc=)
4. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7r2cf7dgbkeIglkbRZqFvZUJNrIDnyb7wrIaOODgwBVq-aeFyNQI48WhH4I8nMpBZqIfU6sXQa65XdRnQkUNRQGimJvbUwjHK9-KuhF6cVRr5_AYlMyZKAZiE7gvxBge-6KgljCQmvPDUroI-d5zzeA==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8IPsW6lKB_w-rkyxgHLQezfFjZzRbvxxDN7AnyGQDvFtWLXsVdPtkTae8_mLPpniU7M7tjDUwEaELPN9JxIDx9IK1oJnc3ZyJFvz9vMxJToIY15vJ)
6. [ub.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcWH1muCd8QyYWbGZ9np6zEzXxvteGxO1LN9H6LNgBr303EW83Y0TVvzNZdIGeGWa7Nh__Wk36eoUWulhPpGXWfkCPjBwWPvtsXWMWdzNfLt2EUuIYhqFT3vcH557SoczzafKYbILXvo8Jm9URWV9HZpb85zm7GbF9wJdR-wjlAYS8Hl0=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfTvJNwHHfdiNuuTuNMm6WxQAqMEDUfTKlg3GSnd-alCubYiM9_lE9GTXOF086JceZ7o9HnvvFJLFLRg_JFaN6AcGM0lRtq7_-GDkWxk5ckkmu9Ix5)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEovgYQz1Ixf-noUfNp3xqP0HyjkXtuyuSI5wVk8CYv-x3VCJtquh07GJVrzlEm0z4VTiRWYntyEminSaAZIfiAOWj1cO2dZWyTsE3SH2ayAV16G1dM)
9. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQ3DxadsrkhUDuR-0xZn_Pfmw807NVPWcMfJLgXeuqpZxeHCn6TN1sLzshqKgaXHgfnWdLGlJxKArNCAP72_KJ4WeXbxtF20A8XIiqVHif62jaDBa2m-A-20P8-wic-qmDi2GN6JuG)
10. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEJj-gpji3OZFcZ8EVF1Wsvn3IFCgEXjv9-F5IgKDYLPLlbRv6nkkxnGCycOac_U_y9X_WcKBH241MRxiflV_w9zLskSOGxlQfqC3Dpu7x16nSM9GbdswFBzM9jMF9TLMSS4tidSzi7awv36b6qk5E)
11. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVIMNXYC0RSJ89sDSiMX_A0trpcbrlUJuyhFuVYu4fH2GWQP6-lwbDzwyQQWVwkEr1SazcQ98b1WMoD1ShguyLe0BURun8DltOHDXkXEKBEwcc63T01Xsw_Z92xG3dQtq95JTxzrbG9TGFbmRYVTE=)
12. [wisc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyiOi1LfYvw_cgiEd9Z6w3H9NU7RZ4-CzmmGG1Qq1LLIvVGG7NBaescTEPZ8EYzrIaaTNFMUQ95MLPLlAGNSAfu3vaAJX_FT8mTDFwM28-HyJDlUjOjk_SgARyg_0cLwUQFgjCVsWBiEDOWOuJ)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHF7qlP8eQjyeTLVaZB1-N-W2RKlM6CEnnHCo7By3-w6Lc_anYZCRnC-tj2f4Cyd2etJlOhSD3pwm7zkvVHl8P-nbK34NEkx9Uv63wdaEvN0p0pXQSt)
14. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIW5ViQeJQbNbvB6F1Zj09DNgJgi9U4Gcc7TbRGPOCZLPr_agVsfKW7xWCGIFhbB2wHq0bynIMOhBIh1I87ovy3e6B9M7AQr30oS-gp5rRsfL7-nG5Zxq5Zxb2RuDzSVNsZHcTH3jaVtF9P4MLdVU=)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLsY9eQrZc7wRrNK0RQhezdeZQT6PplUc64myhdiBjT9VwQw9e5CbMD0wgbGNBYkp9CAljJctb0-AQZT9LfFjzlFGOI_92xMTs8d1JtH8Pehw65eTR2ghF6pOvEhxCeXWurqF5zbF53usJ-dvWFrwMdRaqurUDZJj8ylQWU0Isk_2LajxurBGeOxMctLb5iRAQ2QT2avsNnlZyfrf6ayV6esswMskoMkLUJlGnnkh3CMuWufJdp6-Q1MuXIKERHZXynlXzys0SL0_oonn6sGY8SE8Tzd7Gfi--Uw==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgEDZLlu6E0zp2uvL8BL__Rq373Mti2pnyWTl7-qDuLneFJg8d5H8WsgtPnLm3qjPBQpfFdm36zGFzeEXyOyRu1K7HWrBSUHLmgJjnlyHbR1A982bq)
17. [purdue.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgl5i7rIQI5x356lWur62TlNRH9iZyno2outvUunSVk3CfIPwLBROeK-9tOkxllT2Y7kKagzSRHEfxhS7hl9r9bl5X53WI9J5AClRtmvpTV-7XfU46HTVyWGXg60vBXvxgz7KoxEerGMuPmX0ZL8641Hg=)
18. [unimib.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH92f--0kVN3OcEvW9zO7oSOyNp72p1NiCAe6t_u2YASFyXM67j9LGzy0l_0aLnZykX-y3yBaCneHMDKuIpRpjeK8Yh9s97gEMbhzbDhJ69IruwMzao2A0zQKPCmLuKcGZ61jGq5BngzqeO41sRRp82FsaRkQTq_djq)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHc-oL7ubHhvIRj3_oqAVQ5_Mgx697AXb47cisrEQfBF6HPVDgtv_ctUHNbvIzK1ssAEY1IsbKA7_MnWSibUFBXC1lXavLC-Bnc8xcvIG8POeYP68h4)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQHrBFXiRCMbo6YaPGsV4EdeF7QoEsDWa5CjJnHDPqrlItMLC1tMlpyHHXYzXnCF3DZixq7NswxnXso_KccKAbxnWHoRJ2lRbxfoTxwCgxzyBTeeQnbaw-)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrKrv3e2MtmZw3h5Gyq_n8j-FM0P3WmIPO_PI7zyEPZdqjzfxYisMhhUlwiX-g6EG8YmvQA-FTxOlhvRoojjIb-QGgAN-ucRoT06F3X7xVVJPM5mfY)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh9IFthoJUg23OinzkEaPUR1ZXF6v8BOzH9rzQqSYs5m7-QPtX6D9MIcS1Ba2_dseYZ6r_HkDoTCLocHH96L1FVz2FumZaXGN-GV7JtZYk-8kgDXHi17j31Bj1FjFkbZNoLIWcYf8DAs_yV7jAHIO3QtldJrCaso75WtOzN6RQUxFpprzVLIx4fM3gVzgal_38GEGUB_Xyg6IF3e-q9QU3lQ==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3ZydU5D3hQxXbvQMpzuYmhkX8nD-Us2og06YBlBspfB6zORpNqJ7nCVEWZKrvW-P5OlU4AmNfv69_T_5U0T-v-ks6ibiTLoCYBazzGMfBzbH0aWfY)
24. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFN5_X6vZPgBAZZTNbzNkCL2Ddp82YD_ypRB4AbfBpw8TLUU5abiYzOTXc6Hsw0AireMoZxx7dVXVwZBfkusYKusSkD304oTAodulPhiqQoVlpR-2fSanlBWH-emJbEi6QJp9Vi4QpliR38qYzqP2AYc_guSMXJx4Pvy8dksZ4uH1Y=)

