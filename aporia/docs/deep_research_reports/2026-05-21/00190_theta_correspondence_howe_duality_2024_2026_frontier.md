# Theta correspondence + Howe duality 2024-2026 frontier

**Pythia queue id:** 190
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc0VDhQYXJMMUh2VzZfdU1QN3ZyRDBBOBIXNFQ4UGFyTDFIdlc2X3VNUDd2ckQwQTg
**Elapsed:** 249s
**Completed at:** 2026-05-21T17:28:59.769525+00:00

---

# The Frontier of Theta Correspondence and Howe Duality (2024–2026): Representation Theory, Functoriality, and Holography

**Key Points:**
*   **A Evolving Mathematical Tool:** The theta correspondence (or Howe duality) is a foundational method in representation theory that establishes a deep bijection between the representations of two commuting groups. Recent research (2024–2026) has drastically expanded its scope beyond traditional boundaries.
*   **Langlands Program Breakthroughs:** It seems highly likely that the long-standing difficulties of fitting the theta correspondence into the Langlands functoriality framework are being resolved through the application of "ABV-packets" (or micro-packets), correcting the historical failures of the Adams conjecture.
*   **Operator Algebras Integration:** Research suggests that local and global theta correspondences can be elegantly reframed using C*-algebras and Rieffel induction, providing new functional analytic tools for representation theory.
*   **Exceptional Groups and Ping-Pong:** Mathematicians have successfully proven Howe duality for exceptional dual pairs (like those involving $G_2$, $F_{4,1}$, and $E_7$) using a novel "ping-pong" strategy of K-types.
*   **Holographic Ensemble Averaging:** In theoretical physics, Howe duality over finite fields has recently been utilized to rigorously prove holographic dualities between 3D Chern-Simons gravity and an ensemble of 2D code Conformal Field Theories (CFTs).
*   **Quantum Geometry:** Evidence leans toward Howe duality acting as the fundamental algebraic structure underlying Super Landau models, bridging supermonopole harmonics with non-commutative quantum matrix geometries.

**Layman's Introduction**
The mathematical universe is built on symmetry, and the study of symmetry is called *representation theory*. Imagine you have a massive, complex geometric space (like a high-dimensional surface), and you want to understand how different groups of symmetries operate within it. In the late 1970s, mathematician Roger Howe formalized a concept called "Howe duality" or the "theta correspondence." This concept acts like a magical mirror: if you have a massive group of symmetries and two smaller subgroups that commute with each other perfectly (they are "dual pairs"), the theta correspondence allows you to translate complex information from one subgroup directly to the other. 

For decades, mathematicians struggled to fit this beautiful mirror into the "Langlands program"—often dubbed the grand unified theory of mathematics. When researchers tried to align the theta correspondence with standard Langlands groupings (called L-packets or A-packets), the mirror would sometimes crack; the translation didn't line up perfectly. However, the period between 2024 and 2026 has seen a renaissance in this field. Researchers have proposed that the mirror actually perfectly translates slightly different groupings called "ABV-packets." 

Simultaneously, this purely abstract mathematical tool has suddenly found astonishing applications in modern theoretical physics. String theorists and quantum physicists are using Howe duality to mathematically prove "holographic" relationships—showing how a theory of gravity in a 3D space is mathematically identical to a 2D quantum code on its boundary. From algebraic geometry to quantum matrix geometries, the 2024–2026 frontier of the theta correspondence demonstrates how a singular, elegant mathematical symmetry can unlock secrets across widely disparate fields of human knowledge.

***

## 1. Introduction to the Theta Correspondence and Howe Duality

The theta correspondence, widely known as Howe duality, is a cornerstone of modern representation theory and the theory of automorphic forms. Originally arising from André Weil's 1964 representation-theoretic formulation of the theory of theta series [cite: 1], the correspondence was formally defined and introduced by Roger Howe in 1979 [cite: 1, 2]. Its fundamental premise rests on the behavior of a reductive dual pair $(G, H)$ embedded within a larger symplectic group $Sp(W)$ over a local or global field $F$ (typically of characteristic different from $2$) [cite: 1, 2].

### 1.1 Fundamental Definitions
Let $W$ be a symplectic vector space over $F$, and let $Sp(W)$ denote the associated symplectic group. A reductive dual pair $(G, H)$ in $Sp(W)$ is defined as a pair of reductive subgroups that serve as each other's centralizers within $Sp(W)$ [cite: 3, 4]. 

Fixing a non-trivial additive character $\psi$ of $F$, one constructs the **Weil representation** (also known as the oscillator or metaplectic representation), denoted as $\omega_\psi$, of the metaplectic cover $Mp(W)$ [cite: 1, 5]. By restricting the Weil representation to the dual pair $G \times H$, one obtains a natural intertwining space. For an irreducible admissible representation $\pi$ of $G$, one considers the maximal $\pi$-isotypic quotient of the Weil representation. This leads to the definition of the "big theta lift," denoted $\Theta_{V,W,\psi}(\pi)$, which is a smooth representation of $H$ [cite: 5, 6].

The cosocle (the maximal semi-simple quotient) of the big theta lift is called the "little theta lift" or simply the theta lift, denoted $\theta_{V,W,\psi}(\pi)$ [cite: 5, 6]. 

### 1.2 The Howe Duality Theorem
The central assertion of the theta correspondence is the **Howe Duality Conjecture**, which posits that the correspondence between irreducible representations is a strict bijection. Formally, for irreducible smooth representations $\pi_1, \pi_2 \in \Pi(G)$:
1. If $\Theta_{V,W,\psi}(\pi_1) \neq 0$, then its maximal semi-simple quotient $\theta_{V,W,\psi}(\pi_1)$ is an irreducible representation of $H$ [cite: 5, 7].
2. If $\theta_{V,W,\psi}(\pi_1) \cong \theta_{V,W,\psi}(\pi_2) \neq 0$, then $\pi_1 \cong \pi_2$ [cite: 5, 7].

Historically, this was proven for archimedean fields by Howe [cite: 8]. In the non-archimedean local field setting, it was proved by Jean-Loup Waldspurger when the residual characteristic $p \neq 2$ [cite: 2, 6]. The theorem was later proved in full generality for all residual characteristics by Wee Teck Gan and Shuichiro Takeda [cite: 2, 6], and the remaining quaternionic dual pair cases were definitively resolved by Gan and Binyong Sun [cite: 1, 5].

Between 2024 and 2026, the study of Howe duality has transcended basic classical Lie groups, pivoting toward exceptional groups, C*-algebraic functors, the Langlands program, and even holographic dualities in physics. This report details this rich, multidimensional frontier.

## 2. Functoriality and the ABV-Packet Conjecture (2024–2026)

Despite its undeniable efficacy in representation theory and automorphic forms, the theta correspondence historically resisted integration into the Langlands program's theoretical framework [cite: 6, 9]. In a 1975 letter to Howe, Robert Langlands famously speculated that the local theta correspondence might be a direct instance of Langlands functoriality, preserving L-packets [cite: 6, 10]. History and explicit counterexamples demonstrated that this was false; the local theta correspondence does not always preserve L-packets [cite: 6, 10].

### 2.1 The Adams Conjecture and its Failure
In 1989, Jeffrey Adams proposed a refinement now known as the **Adams Conjecture**: rather than preserving L-packets, the local theta correspondence should preserve local Arthur packets (A-packets) [cite: 7, 10]. Specifically, if $\pi \in \Pi_\psi$ for some local Arthur parameter $\psi$ of $G$, then its theta lift $\theta(\pi)$ should belong to $\Pi_{\psi'}$, where $\psi'$ is an explicit local Arthur parameter of $H$ depending only on $\psi$ [cite: 7]. 

While Colette Moeglin showed that Adams was mostly correct, she also demonstrated critical failures where the Adams conjecture broke down. Specifically, there are examples where a representation lies in an A-packet, but its theta lift does *not* lie in any A-packet [cite: 10]. This limitation inherently restricted the usefulness of the Adams conjecture to representations strictly of Arthur type [cite: 7, 11].

### 2.2 The Transition to ABV-Packets
To rescue functoriality, the 2024–2026 frontier has seen a shift from A-packets to **ABV-packets** (also referred to as micro-packets). ABV-packets were originally defined for real groups by Adams, Barbasch, and Vogan [cite: 6]. For $p$-adic groups, a formulation was recently rigorously established by Clifton Cunningham, Andrew Fiori, Ahmed Moussaoui, James Mracek, and Bin Xu, utilizing the microlocal vanishing cycles of perverse sheaves [cite: 6]. 

In a series of recent preprints and publications (2024–2026), researchers including Alexander Hazeltine, Clifton Cunningham, Mishty Ray, and others advanced a new conjectural framework: **The local theta correspondence preserves ABV-packets** [cite: 10, 12]. 

Because ABV-packets encompass all irreducible admissible representations—not just those of Arthur type—the ABV-packet conjecture brings the theta correspondence much closer to Langlands' original 1975 vision [cite: 7]. As demonstrated by Hazeltine in 2026, the geometric nature of ABV-packets resolves the anomalies that plagued the Adams conjecture. By passing to the algebraic geometry underlying ABV-packets, researchers have successfully provided evidence for this refined conjecture, culminating in explicit proofs for the general linear group $GL_n$ [cite: 7, 9]. This approach crucially demonstrates that for $GL_n(F)$, ABV-packets are preserved by the contragredient [cite: 7], firmly establishing the functoriality of the theta correspondence in this domain.

## 3. C*-Algebraic Methods and Rieffel Induction (2024–2025)

A major paradigm shift in 2024 was the introduction of operator algebraic methods into the local and global theta correspondences. In a landmark paper, Bram Mesland and Mehmet Haluk Sengün reinterpreted the theta correspondence as a continuous functor between categories of representations of C*-algebras [cite: 3, 8].

### 3.1 Group C*-Algebras and the Oscillator Bimodule
Mesland and Sengün built upon the explicit constructions of the local theta correspondence pioneered by Jian-Shu Li [cite: 3]. Li had previously shown that for unitary representations $\pi$ of $G$, when $G$ is sufficiently smaller than $G'$, the theta lift $\theta(\pi)$ is also unitary, giving an embedding of unitary duals $\widehat{G} \hookrightarrow \widehat{G'}$ [cite: 3]. 

In 2024, it was proven that Li's explicit construction is an instance of **Rieffel induction**—a general induction procedure for C*-algebras developed by Marc Rieffel in the 1970s [cite: 3]. Let $(G, H)$ be a reductive dual pair. The researchers constructed a Hilbert C*-bimodule (the "oscillator bimodule") over the C*-algebras of the groups [cite: 13]. This bimodule interpolates the oscillator representation of one group with the regular representation of the other [cite: 8].

### 3.2 Strong Morita Equivalence for Equal Rank Pairs
For equal rank reductive dual pairs, such as $(Mp_{2n}, O_{2n+1})$ or $(U_n, U_n)$ over a non-archimedean local field of characteristic zero, Mesland and Sengün proved a profound equivalence [cite: 8]. The theta correspondence establishes a bijection between certain subsets of the tempered duals, denoted $G_\theta$ and $H_\theta$. The authors demonstrated that this bijection arises from an equivalence between the categories of representations of two C*-algebras whose spectra are precisely $G_\theta$ and $H_\theta$ [cite: 8].

This Morita equivalence is implemented by the induction functor associated with the constructed oscillator bimodule [cite: 8]. Consequently, the tempered theta correspondence is not merely a set-theoretic bijection but a homeomorphism between $G_\theta$ and $H_\theta$ [cite: 8]. It is continuous and functorial with respect to weak inclusion [cite: 8, 13]. Furthermore, the authors demonstrated that the critical compatibility condition for the two operator-valued inner products on the bimodule reduces to a non-commutative analogue of the Poisson transform, effectively yielding a C*-algebraic interpretation of the Rallis inner product formula [cite: 3, 8].

## 4. Exceptional Dual Pairs and the "Ping-Pong" of K-Types (2024–2026)

While the classical Howe duality theorem applies to reductive dual pairs within symplectic groups, the 2024–2026 period has been defined by the successful extension of these principles to **exceptional groups** (e.g., $E_6, E_7, E_8, F_4, G_2$). This work has been heavily spearheaded by Gordan Savin, Petar Bakić, and Wee Teck Gan [cite: 14, 15].

### 4.1 The Dual Pair $SL_2(\mathbb{R}) \times F_{4,1}$ in $E_7$
In a highly influential 2026 publication, Gordan Savin established Howe duality for the exceptional dual pair $SL_2(\mathbb{R}) \times F_{4,1}$ sitting inside a simply connected exceptional group $G(J)$ of type $E_7$ [cite: 16]. 

The construction utilizes the Koecher–Tits construction on Jordan algebras. Let $\mathbb{O}$ be the algebra of Cayley octonions over $\mathbb{R}$, and let $J$ be the 27-dimensional space of $3 \times 3$ hermitian symmetric matrices with coefficients in $\mathbb{O}$ [cite: 16]. The automorphism group of this cubic space gives rise to the simply connected group $G(J)$ of absolute type $E_7$ with split rank 3 over $\mathbb{R}$ [cite: 16]. This group admits a minimal (holomorphic) representation $\Pi$, within which the dual pair $SL_2(\mathbb{R}) \times F_{4,1}$ acts [cite: 16, 17].

To prove Howe duality in this setting, Savin utilized a technique dubbed the **"ping-pong of K-types"** [cite: 16, 18]. The maximal compact subgroup of $SL_2(\mathbb{R})$ is $SO(2)$. By restricting the minimal representation and calculating the K-types (the representations of the maximal compact subgroups), the author leveraged a pair of see-saw identities to bounce back and forth between the representations of $SL_2(\mathbb{R})$ and $F_{4,1}$, effectively determining the structure of the co-invariants $\Theta(\pi)$ [cite: 16, 17]. The same strategy was similarly adapted to prove exceptional theta correspondences for $p$-adic dual pairs [cite: 16, 17].

### 4.2 The Dual Pair $G_2 \times PU_3$ in $E_6$
Bakić and Savin (2024) also proved Howe duality for the $p$-adic exceptional dual pair $G_2 \times (PU_3 \rtimes \mathbb{Z}/2\mathbb{Z})$ inside the adjoint quasi-split group of type $E_6$ [cite: 14, 17]. They utilized a "ping-pong of periods" to establish the exact one-to-one nature of the correspondence [cite: 15]. The ability to translate between the $p$-adic $G_2$ and $PU_3$ allows researchers to construct global $A$-packets and prove the Arthur multiplicity formula for these representations [cite: 14, 19]. 

### 4.3 Similitude Groups
Another major advancement is the systematic construction of dual pairs of **similitude groups** (e.g., orthogonal and symplectic similitude groups). In 2024, Bakić, Gan, and Savin proved that Howe duality holds for a similitude dual pair if and only if it holds for the original reductive dual pair used in its base construction [cite: 14, 19]. This significantly broadens the toolkit for studying arithmetic invariants, particularly extending Waldspurger's well-known results to higher dimensions [cite: 20].

## 5. Degenerate Principal Series and Type I Dual Pairs (2024–2025)

The fine structure of the local theta correspondence—particularly regarding "first occurrence" indices and the non-vanishing of the big theta lift $\Theta_{V,W,\psi}(\pi)$—relies on studying the **degenerate principal series**.

### 5.1 Strengthening the Conservation Relations
The conservation relations dictate the exact threshold at which a theta lift becomes non-zero [cite: 2, 5]. In 2024, Johannes Droschl investigated the degenerate principal series $I(s, \chi)$ of classical groups associated to a complex parameter $s \in \mathbb{C}$ and a quadratic character $\chi$ [cite: 2]. By 2025, Droschl published a slight but critical strengthening of previous bounds, explicitly controlling the degenerate principal series for $s \in \mathbb{R}_{\geq 0}$ [cite: 2, 5].

Using the machinery of representation derivatives (analogous to the Jacquet functors), Droschl provided a new, independent proof of the Howe Duality Conjecture for symplectic-orthogonal and unitary pairs (Type I dual pairs) [cite: 2, 5]. By examining the socle and cosocle filtrations of the induced representations $I(s, \chi)$, Droschl mapped the cuspidal support of the parameters precisely, providing granular control over the maximal semi-simple quotients $\theta(\pi)$ [cite: 5].

### 5.2 Galois Periods and the Relative Langlands Program
The local aspect of the relative Langlands program, initiated by Sakellaridis and Venkatesh, is deeply concerned with the properties of local periods [cite: 21]. The local theta correspondence acts as a powerful lever to study relations of these periods between members of a reductive dual pair.

In 2026, Chong Zhang extensively studied the behavior of **Galois periods** under the local theta correspondence for even orthogonal and symplectic groups [cite: 21]. By applying base change doubling zeta integrals, Zhang compared the multiplicities of representations related by the local theta correspondence and constructed explicit transfer maps [cite: 21]. Using the structure of the degenerate principal series alongside the base change seesaw identity, Zhang established both an adjoint relation and a relative character relation for these periods [cite: 21]. This perfectly aligns the theta correspondence with Dipendra Prasad's conjectures relating Galois period multiplicities to L-parameters [cite: 21].

## 6. Holographic Ensemble Averaging and Code CFTs (2025–2026)

Perhaps the most unexpected and revolutionary frontier of Howe duality in 2025–2026 is its application to quantum gravity and theoretical physics. Specifically, Howe duality has become the mathematical backbone for proving exact **holographic dualities** involving topological gravity and ensemble averaging.

### 6.1 The Factorization Puzzle and Ensemble Averaging
In the AdS/CFT correspondence, a sharp conceptual issue known as the "factorization puzzle" arises when considering multi-boundary wormholes. To resolve this, researchers proposed that bulk gravity is dual not to a single Conformal Field Theory (CFT), but to an *ensemble average* of CFTs [cite: 22, 23]. 

Johan Henriksson, Anatoly Dymarsky, and Brian McPeak (2025) explicitly constructed a holographic correspondence between 3D "Chern-Simons gravity" and an ensemble of 2D Narain code CFTs [cite: 24, 25]. The bulk abelian Chern-Simons theory possesses a 1-form symmetry. By gauging all possible maximal, non-anomalous subgroups of this bulk 1-form symmetry, they constructed an ensemble of boundary CFTs [cite: 24, 25]. 

### 6.2 The Role of Howe Duality Over Finite Fields
Each maximal non-anomalous subgroup is isomorphic to a classical even self-dual error-correcting code over the finite field $\mathbb{Z}_p \times \mathbb{Z}_p$ [cite: 24, 25]. Thus, the boundary theories are identified as "code CFTs." The physical conjecture is that the average over this ensemble of code CFTs is holographically dual to a bulk theory summed over 3D topologies sharing the same boundary [cite: 24]. In the case of prime $p$, this bulk sum reduces to a sum over handlebody geometries, yielding the Poincaré series [cite: 24, 25].

The main result of Henriksson et al. is that the mathematical identity underlying this holographic duality—expressed as **"boundary ensemble average = sum over bulk topologies"**—is rigorously proven using **Howe duality over finite fields** [cite: 22, 25].

In this framework, the reductive dual pair consists of:
1. The **symplectic group** $Sp(2N, F)$, which acts as the group of modular transformations of the boundary [cite: 22, 24].
2. An **orthogonal group** $O(V)$, which maps the classical error-correcting codes to each other [cite: 22, 24].

The Weil (oscillator) representation over the finite field yields an invariant unique one-dimensional subspace when acted upon by this dual pair [cite: 26]. Because both the path integral of a boundary code CFT and the path integral of the bulk Chern-Simons theory on a specific handlebody are mathematically formulated as quantum stabilizer states, Howe duality asserts the strict equality of their averages [cite: 24, 25]. This translates the holographic correspondence into an explicit algebraic identity in quantum information theory, fundamentally proving the equivalence of the Poincaré series and the Narain ensemble [cite: 22, 25].

## 7. Super Landau Models and Quantum Matrix Geometry (2026)

In addition to topological gravity, the theta correspondence has manifested as the underlying algebraic structure for non-commutative quantum geometries. In April 2026, Kazuki Hasebe demonstrated that Howe duality provides the fundamental framework for the **Super Landau Model** [cite: 27].

### 7.1 Supermonopole Harmonics and Dual Geometry
Landau models are quantum mechanical systems used to generate quantum matrix geometries. By studying the super Landau model on a supersphere $S^{2|2}$, Hasebe showed that the system possesses a hidden algebraic symmetry dictated by super Howe duality [cite: 28, 29]. 

The (super) Howe duality explicitly relates different Landau energy levels (LLs), generating a bridge between them [cite: 27]. Using super-spinor derivative operators, researchers can construct "supermonopole harmonics" in both integer and half-integer Landau levels [cite: 27]. This reveals the complete algebraic structure of the super-Hilbert space.

### 7.2 Internal-External Space Duality
Through a level projection method, one derives the matrix coordinates of fuzzy supersphere geometries for arbitrary Landau levels [cite: 27, 29]. The theta correspondence of Howe duality actively induces a geometric transformation between these fuzzy objects [cite: 27]. 

Consequently, Hasebe points out that Howe duality physically realizes an internal-external space duality [cite: 27, 29]. It serves as a general feature of coset-type Landau models, suggesting that the theta correspondence plays a highly fundamental role in understanding the geometries of Matrix models in string theory and M-theory [cite: 27, 29].

## 8. Geometric Theta Correspondence and Beyond

At the arithmetic and geometric level, the **geometric theta correspondence** replaces classical Schwartz spaces with derived categories of (perverse) $\ell$-adic sheaves on infinite-dimensional spaces (such as affine flag varieties) [cite: 30].

In the context of the geometric Langlands program, the correspondence is formulated for tamely ramified or Iwahori-level structures [cite: 30]. Equivariance under Iwahori subgroups is imposed, and Hecke functors on affine flag varieties induce commuting actions of Iwahori–Hecke algebras on these sheaf categories [cite: 30]. The geometric theta module subsequently becomes a bimodule for these algebras, providing a pure categorical description of the local theta correspondence [cite: 30]. 

This explicit geometric formalism unifies algebraic and analytic constructions, offering direct geometric proofs of relations between modular forms (e.g., the Borisov–Gunnells relations) and illuminating the cycle structure of modular and Shimura varieties [cite: 30]. It generalizes far beyond the classical $SL_2$ dual pairs to orthogonal, unitary, and symplectic groups, playing a pivotal role in recent proofs related to the arithmetic Gan–Gross–Prasad conjectures and the arithmetic fundamental lemma [cite: 30].

## 9. Conclusion

Between 2024 and 2026, the theta correspondence (Howe duality) has proven to be an inexhaustible wellspring of structural truth across mathematics and physics. In pure representation theory, the transition from Adams' A-packets to ABV-packets has resurrected the Langlands vision of functoriality for the local theta correspondence [cite: 6, 9, 10]. The use of C*-algebras and Rieffel induction has provided powerful topological and functional analytic lenses to view the tempered duals of reductive groups [cite: 8, 13]. 

The methodical dismantling of the exceptional groups ($E_6, E_7, G_2$) via the ping-pong of K-types demonstrates the sheer computational and structural reach of the duality theorem [cite: 15, 16]. The refining of degenerate principal series bounds extends our grasp over the exact conditions of non-vanishing theta lifts and their relationships to Galois periods [cite: 5, 21].

Perhaps most stunningly, Howe duality has crossed disciplinary boundaries. In 2025–2026, it supplied the exact group-theoretic architecture necessary to rigorously prove holographic ensemble averaging—equating 3D Chern-Simons topologies with 2D Narain code CFTs using finite field representations [cite: 22, 25]. Furthermore, its realization in Super Landau models points toward a fundamental reality: the mathematical symmetry that Roger Howe formalized in 1979 is deeply woven into the non-commutative geometric fabric of quantum mechanics [cite: 27, 29]. 

The frontier of Howe duality is no longer just the classification of admissible duals; it is a unifying language connecting the arithmetic of automorphic forms, the geometry of perverse sheaves, and the quantum symmetries of spacetime itself.

**Sources:**
1. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhFZy-SEY99Aw2HXuC2KRWfZoxGWVRJxpjcKMitnOtJtopaaLAoNcAMg4cKZGS7PdeKunENtqZ0SyBbLThJTpRS35hSI8dpnkP_PTVnGMts_jCF6Tff6vJ06lel9aPHY4EtBn6xI_klQ==)
2. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkrmL7GstjxHDazKzmbmmRih5xO3-fOqyjMqvjuuN3zBeiAr_hSzgDtM326PbWCpeu1nDpAAuz1YqEm8s6TCjts3YTaOWMTk6j2MxRKYC2YUtDxfNQFJzJJgxrC3ACJvBKe07U8dRjisRtNnu1bWO20WzvF0OibpbsEM74drL-mt_9661G-NnY2GNPMyhM7BBuCrhCWPi82ATHwv8kmMWXjWLQPEk4XznVEX-owfbdIR7E8RDaOmIG_MZn4pLAIvMamZ3wEmk70k_l0unMGDl1KG8lxcQ9DgnAqQlgo6beA-xw0g==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEG9qzA9kgo0Quvl4NFm-Jz0OqHGMcTDJaiOwf_7_TM_9eg-j29bjPGa0UmjQRQn1VVAnGinVMA_mnfGP5Pek-t2QSInVR8QaUVVnVV0_c2LX8-56ugjQ==)
4. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGatVSrfX1S4BO8GMfHETrKkUmH3a7I-79EMmfdNBG2YDu0hif3W8ApSWv0my049ycehPK6Py2CrhVqTaP6BqdYreZBdaiPHDfmu9e2v5TW4wsgWN04LR9NTCI8xUtofLR5drGXqrM=)
5. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKHGBQQ56rWjyy8RSTS_a2Oyx5-7Bt3FiOpq-8HpNzMhzzdSlQ5gHQ1ZSBFlgQaAvCdCKXml3vb_FdGtFDAskuqGi89pHwFo_juJh8dj71vl8lZ9QFC2K9s18Avp69_eWg_EAlguZ_QBAp8EXhnZGG7yJw)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtCYtN0CuQEJPRYhRMM_ZUiHyXVm6mK6uayFrxXksdKjGB6FbV59Xz3KoDbdvPeblAjSIlWOTr49kuceFUUPrPfBQc_9vQwSyro2i28RECgiYCA5MrpisV-Q==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJ8zwvtf6p-hD5Dvib4ZB8hDuwIpmY4q-VBuQ9KgF7iuo-LOqsz0sHVTy7wJilE6E4GX4utZN3MJagbTFAYbMPKo97t4iD4EX4lC4nEmMJhZyuP62GuA==)
8. [universiteitleiden.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0DF9FjGphvgO7oqg9TsphiDkRPcbJRKRW_IKD8UdVA_PQWPqPQ21owmoW70aovQR25ctDwz3vzfhrEWQ3VYh840lV_FeDoYeJ7ODzUBFA2nfGX91OxFYL2iw8Fju9g-wP9Eji1K0C4OZhQKSLK0diGApakSsq3ulTbfOASnLSR4Px3sJaScLD)
9. [okstate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_nLgOkJ-Owqn-cJFDTqZmIn260tTBqsObKRS8chquI2_SmghG06I5utE6EwLPMENsNNI631h62pFNkl4g2gEvhiRMj_Xe-mir8_pCjv8p416UqpufkTxbsg4lvO1gnBdqCZyxwCh-J3a9B_nEY5FWUnJ6zsN97g==)
10. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHy0NWbihNvRsgTFY-qRL9ub3lnes1olT-v7cqWYbzwHY5T-ItAU7kGV4toL4ewp2Mp_7vF-hZp-ZR05WnMETb_DLeYB3pwKSw7gCkEALgRcWn4dg0j0QALdSY4-a6QWhUkQHqvHzLWyNwviULu-vGDCvPFOw==)
11. [math.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF__2hu7zNiDNAwglHv77krNQLS6IwnJCyW_9hMEhVc27NeYMOao9p9bRfQ400rqouZoqxN8awYgXJr4l7TCGDCbopgUMp0STy9_nDFq6hR1LXhSKHCreDKWaQM6yI0bONRpG_Qfut6cEYcuDF9K1N3Jg==)
12. [ams.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0RTuzSPBwvaYt_pAKnYPe3JDw8otCc_h7Pr6q2IC6PzPOmz0_oHUyCB-1HLZOc5JdnYbRT1VM6fYFXnFdxX01SnoB9UZ_67JiOdyyvBZb7kg5CaKIOAF2bIxeyoOaJJL33rK5Mx9NO0zqPZpoVBfDtcrU0hEbkehXUw==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuSkbakRNrVi0UeR-3coCknIfhz4mrDN_FmBWCseBHcPT4BaQUCr1Ep9CVWDafr4ShZgVcdCsb1NkBXetPU6xWJySVxkTNeUhQhk7hHgsyaRDNbUPe1w==)
14. [utah.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZufS1TG07eaYAuW4HAVVs8Sorog9q4kp2iggkTlswJF3cC8DWDfd-_ULAiWTBqSNXB1_n1-MYdSS34usx9lHOeuPjzgzbRssuo5wRJuPzMqSrXaNe2WaxVE7iKaeRYhW84PQY)
15. [amss.ac.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpLxMgsE9wvxuuXX499RCmLAHyI24iXmp8boS8ruPcGRK60TCJtxMgLo8Cj4J2hWc5oMhzYKqsnARC8jWrPc3K2hM7uczJMLLChoA8KpfPSEruSANGAC1KIbBMiWsUmT_Cd7bnbNslE5lDXyVjTygbaaxYkIQaSg5LGQtx_m1mq0cQp3Xasz1DmBkh_JwUd1vjzTPCJJA22Q_zgQ==)
16. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0v5fkQzVXnExJ_QjMCt12VGZMrTdU52zu0HCnxu2z1_MGUufFRWCAT_oVzs4Gk1Zep324-W5IH47XtQAMvvm3nqloxQrQbIdShoCch6gdgbrweLwT6UTZbJ9MKE_CUx6krqYN7TW9Dm7I)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFy9nitL0ElX8kDnr_BvTBwDI1CGRtzRbO0WgQT43V10fI2EhW4u-JdlCxOE7ZyWtSZdUCynFJ_7mIv6rvI91Dz0jhw2uuB068st4LgpCilvzulzpWod3_GHQEfNUAWbTa0m2UMDrJy-nOy9AkmKaRITBNohmG0ybl4nreo4NLxtlkoJRsC1Ep_ZNoHhF6Q-nTzQpjciyl8dnTpn5DDTNGcsePKRhuvtQ==)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFx3E7bJmuQIGErBwqjXtHNpvZ2ygdyC3BS0LmDMP5jEBNxlvgf-drxpFsS3LNy1zXq1MmmxwC8jP9OxFl0F8Gi4Ve-lWBAsRmPYv9s8swjpguucoHizaNEcI7Dux7w_9LMHYN6z4L4ctWfAOKPKf2YDg9qI6kEBVXgQWwfgFABe5EzVkFWyrOagPhLB6u8bcKXoJMtDQ6TCojeKFab9MK5Lm5Q2hX2rbxd0xuugUvJBaxxsKdYbXQ=)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSwXL4E_Y7ak6wkLFzGzJFWh2owKLAf76hQCLHeIbTOf7kSH5HgWbbyaOx7UbJ46ItlMdD763MKkrhtVGbUOiBTXSWrbSJmFvmqGkhVnkahrCC_xc9fLa8GlWExZen75TlO-j0yiY=)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxycKpf5E8t2aE-M7__tPFzgP5CviTLyx5QrgwNdz3YRFe-J-6s_qvo7ocWYZQsWEB5mNYn8283Z5oDcxN-yBgdN_VvT8UCV0mDIKG6o3J-lCPScYNCp9wiaCic5Eb7FiPC5202tcdvismzhN7dmk0jQVjAPjcUzK1-C2ryBUUHrn2815aZesrBtUSZGC7l7UFlEEzpMQGuvCoQtO00w==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6L3-S6sRnxo1eaAYbQmQ1pdpJ9JXEFg4U4eRsq5SmfV1tn63bl_mr7y5FBFrkg4AQvQLPOY2woCIXoKOsBdERKciJQPlwER2audvOQl-drxGW_mtFAuozug==)
22. [cern.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcIcMedgmSD8uouq-3BSmFHAgCTeKCYHrh1-xx0r1GPZcjz6RBq3-bh4fgftOuZskn51svMV1-6PhlWfhYciIyCnVnfY0ly1VcnApYOUbygbWaTEFfmh_-XdZ09L6l0c1d24qidS12JL9x_Zz9NnDSCOAQou67rTtWPTzk_zU3MpvWK1Q8mo5iEheuPgqP1oohU1bV8lMgcrW2xuTEH5rP9dmW6tGXKRt9)
23. [su.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrv8jofdG5gbfeKoR0uUxM2Cj2-VFXYfDgJckcjDewkNqvQ5j3XpnSZIEZP7Z4Zcu8HmBg4uWNLb2eAAvG7sSoVh2RaAEreaqTBFXd6oxeTPBwo2ZBbPF4jDVkXeyE6cxdFGcIZdy8SO6lpYIR9slKlk4QSav8eBkc6XP_YcyXGz5hRFqNuM4Mv3eXNGqhvuQNaGE9xhqgguS5XIpi7yyt-tw=)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZL4vzLZ3JU45vY9EE1gIFE_KhHIWmK0F26CZzT-5-gmD-ugGnJD18DtXaiVdGtGA61l77aH7YTk7s4yFo3Z8X-IT2kErEMq3VcXzYQbd75O8j1tfewODecwSszspSUwypkn6GCGzOwvo5svTqxFs8edVFcCYOulyzvtRZXwW1tiqw2AVwo7_RJlYW3Ct8hb0a9rSAagrm4OcW5TtdllCiWwZpr_myxAplLG9okvA6V-hlooFs3UxWOLZAwh-UH68=)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEW6Hwls9MLgzjynPdK00hoIeol4YfqZ_gB5zgQsxf_TLNRiWLZVBp6orRuywZy4C9j8EEukYIXKtwK6gdBT1vr18ATpJrphqGDr7tZXr-oZyS2mn3kU1pbyg==)
26. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcRPgeOqI4u-FBHXd2BLJHEDZE13VBy9SiiLRirb4cAA06E8rjsdUjy9dK6YlukxMj5ACGDpAQXmmASevxJ1EJq2nAqvQLeCT-XmAmDxbJ7VIiCmDZRglssI3Wdc8fhJxN)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHt9vPdqkNCnTiFh5slO9kXP1YiUWEy9jjpzpbDqkUwA0AI4MFyArGHwT8usoRsU0TNDCf_o026vEthCXyIRc7agRozDHqkWq5bC0NeYWl9wDrBDq2JNA==)
28. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGorJxjI-Fel4mSoFJRb0IVxlsDz3E1Yn2okzb0Ct40CeF10UTj6MUS9iBeapRQmnrOvYoqE89tQnxjJsY1F3xLObqNVv83umohoYVXin_JEZh7XI2Vpr7RirCM8On8mYKH0u3A4KPCzaccoDS3AOtf92YeUJ635RUNshYu6xPSdrHxGgMX7_ROK9rbpx31jCyZjmwG154dPshPRb8nLcrRU0R8vh9CguGjqUomWGyEgWIDWA=)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_j7pmQw-xk-mf1LGUSfHJSbgwplRJh0aBJDNS_0lLuBbCWGv30lta6Tn0INgZvoyDHcPgN64GTOsIp81Gt4qQj_gfKPHrfKjZGpfch-8HtgqgezT-rD0aKQ==)
30. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEz43GDfsdrRyf-qmQtma1fqJjDIA8-m7eDuOckaViOvr4oPX9YFuXEFI3rTyYbWoHDEmjvqWlTGMpRj1T65d4Gu8Y1Ey4b3Pe2nZGvkxUfpXDIcMOtM54QGntLKtuuYzmVFYZ90En2njSeabz13rPYdaAvfPxbR8M=)

