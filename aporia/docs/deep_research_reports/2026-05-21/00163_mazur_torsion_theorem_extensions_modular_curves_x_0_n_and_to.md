# Mazur torsion theorem extensions (modular curves X_0(N) and torsion) 2024-2026

**Pythia queue id:** 163
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdZellQYXJmZElaMzFqTWNQcEkzQ21RbxIXWXpZUGFyZmRJWjMxak1jUHBJM0NtUW8
**Elapsed:** 253s
**Completed at:** 2026-05-21T16:48:33.836079+00:00

---

# Recent Extensions of Mazur's Torsion Theorem and Developments in Modular Curves \(X_0(N)\) (2024-2026)

**Key Points:**
*   Research suggests that the landscape of rational points on modular curves, originally framed by Mazur's torsion theorem, continues to yield deep insights into the arithmetic geometry of elliptic curves.
*   Recent classifications (2024-2026) have significantly expanded our understanding of sporadic points on \(X_0(N)\), with evidence leaning toward a complete determination of curves admitting such points across arbitrary degrees.
*   It seems likely that the asymptotic growth of prime-order torsion over number fields of degree \(d\) is bounded linearly (specifically by \(3d+1\)) for even \(d\), assuming certain conjectures about newforms, while remaining sublinear for odd \(d\).
*   The study of torsion structures has successfully extended to infinite towers of fields, such as \(\mathbb{Z}_p\)-extensions of quadratic fields, where it is generally observed that torsion growth stabilizes for primes \(p > 5\).
*   Investigations into the intrinsic subgroup of the Picard group offer a refined lens through which Mazur's original 15 torsion groups can be analyzed, potentially constraining the reduction types of elliptic curves.

**Introduction to the Topic**
The study of elliptic curves and their rational points represents one of the most celebrated and enduring subjects in modern number theory. At the heart of this field lies the Mordell-Weil theorem, which establishes that the set of rational points on an elliptic curve forms a finitely generated abelian group, inherently comprising a free part (defined by its rank) and a finite torsion part [cite: 1, 2]. Characterizing the exact nature of this finite torsion part over the rational numbers was a monumental task that culminated in Barry Mazur's 1977 torsion theorem. 

**The Evolution of Torsion Classifications**
In recent years, specifically between 2024 and 2026, the mathematical community has witnessed a surge in research extending Mazur's foundational work. While Mazur's theorem precisely identified the 15 possible torsion subgroups for elliptic curves over the rational numbers, contemporary research has pushed these boundaries into higher-degree number fields, infinite extensions, and more complex modular curves. These modern investigations often deploy sophisticated computational techniques and advanced geometrical theories to classify torsion structures that were previously intractable. 

**Scope of the Report**
This comprehensive report synthesizes the latest academic literature from 2024 to 2026 regarding extensions of Mazur's torsion theorem. It explores the intricate geometry of modular curves—particularly \(X_0(N)\) and \(X_1(N)\)—and their Jacobians. The text delves into the classification of sporadic points, the asymptotic behavior of prime-order torsion, novel pairings on the Picard group, and the structural stabilization of torsion subgroups over infinite Galois extensions. 

## 1. Historical Foundations: From Levi's Conjecture to Mazur's Theorem

To properly contextualize the advancements of the 2024-2026 period, it is imperative to trace the origins of the torsion classification problem. The question of which finite abelian groups can manifest as the rational torsion subgroup \(E(\mathbb{Q})_{\text{tors}}\) of an elliptic curve \(E\) over \(\mathbb{Q}\) has a rich history that predates modern arithmetic geometry.

### 1.1 Early Conjectures and Partial Results
The problem was first formally articulated by Beppo Levi in 1908 during the International Congress of Mathematicians in Rome [cite: 3, 4]. Levi conjectured that the possible rational torsion subgroups were limited to a highly restricted list of groups, effectively postulating what would later be known as Ogg's torsion conjecture. Levi himself managed to prove, using the method of infinite descent on curves of genus zero and one, that rational points of order 14, 16, or 20 could not exist on elliptic curves over \(\mathbb{Q}\) [cite: 3, 4].

Following Levi, the problem saw incremental progress. In 1940, Billing and Mahler proved that there are no elliptic curves over \(\mathbb{Q}\) with points of order 11, 15, or 24 [cite: 3, 5]. In 1952, Trygve Nagell reaffirmed the torsion conjecture without apparent awareness of Levi's earlier work [cite: 3, 4]. By the early 1970s, Andrew Ogg formally proposed a geometric philosophy: the modular curve \(X_1(N)\) should have non-cuspidal \(\mathbb{Q}\)-rational points if and only if its genus is zero (which occurs for \(N \le 10\) and \(N=12\)) [cite: 3, 6].

### 1.2 Mazur's Torsion Theorem (1977)
The complete resolution of Ogg's conjecture was achieved by Barry Mazur in his seminal 1977 paper, "Modular curves and the Eisenstein ideal" [cite: 3, 7]. Mazur's theorem states that for any elliptic curve \(E\) defined over \(\mathbb{Q}\), the torsion subgroup \(E(\mathbb{Q})_{\text{tors}}\) is isomorphic to exactly one of the following 15 groups:
\[ \mathbb{Z}/N\mathbb{Z}, \quad \text{for } 1 \le N \le 10 \text{ or } N = 12 \]
\[ \mathbb{Z}/2\mathbb{Z} \oplus \mathbb{Z}/2N\mathbb{Z}, \quad \text{for } 1 \le N \le 4 \]
Crucially, all 15 of these groups are realized by infinitely many mutually non-isomorphic elliptic curves over \(\mathbb{Q}\) [cite: 8, 9].

Mazur's proof represented a paradigm shift in Diophantine geometry. It relied heavily on Alexander Grothendieck's étale cohomology and the geometry of the modular curves \(X_0(N)\) and \(X_1(N)\). Mazur studied the Galois representations associated with elliptic curves and proved that the existence of torsion points of higher order would imply the existence of non-constant maps from these modular curves to elliptic curves, leading to contradictions via genus and degree considerations [cite: 3, 7]. The core of the proof involved studying the Jacobian \(J_0(N)\) and demonstrating the finiteness of certain quotients using the Eisenstein ideal, fundamentally altering the trajectory of arithmetic moduli space theory [cite: 3, 7]. 

## 2. Sporadic Points on Modular Curves \(X_0(N)\)

A significant vector of modern research involves the parameterization of elliptic curves with specific torsion or cyclic isogeny structures, a property encoded by the rational points on modular curves. While Mazur and Kenku fully classified the degree 1 sporadic points (rational points) on \(X_0(N)\), recent work between 2024 and 2026 has generalized this classification to sporadic points of arbitrary degree.

### 2.1 The Minimum Density Degree and Sporadic Points
For a smooth, projective, geometrically integral curve \(X\) over a field \(k\), the **minimum density degree**, denoted \(\delta(X/k)\), is defined as the smallest integer \(n\) such that \(X\) possesses infinitely many points of degree \(n\) over \(k\) [cite: 10, 11]. When the base field is \(\mathbb{Q}\), this is simply denoted \(\delta(X)\) [cite: 11].

A **sporadic point** \(x \in X(\mathbb{Q})\) is defined as a point whose degree strictly satisfies \(\deg(x) < \delta(X)\) [cite: 11]. In the context of modular curves, isolated and sporadic points represent "exceptional" low-degree points that lie outside the infinite families of low-degree points dictated by the curve's inherent geometry [cite: 12, 13]. The identification of these points is critical because each non-cuspidal point on \(X_0(N)\) or \(X_1(N)\) corresponds to an elliptic curve with a specific level structure [cite: 8].

### 2.2 The Derickx-Najman Classification (2025)
In November 2025, Maarten Derickx and Filip Najman published a landmark preprint detailing a complete classification of the integers \(N\) for which the modular curve \(X_0(N)\) admits a sporadic point of *any* degree [cite: 10, 14]. This work serves as the ultimate generalization of Mazur and Kenku's classification of rational isogenies over \(\mathbb{Q}\) [cite: 11, 14].

Derickx and Najman analyzed both points representing elliptic curves with complex multiplication (CM) and those without (non-CM). Elliptic curves with CM are a well-known and frequent source of sporadic points on \(X_0(N)\) [cite: 11]. Building on prior work by Clark, Genao, Pollack, and Saia (who found 50 values of \(N\) with no sporadic CM points but left 106 values undetermined) [cite: 11], Derickx and Najman resolved the remaining ambiguities.

Their primary theorem provides a definitive condition:
**Theorem (Derickx-Najman, 2025):** The modular curve \(X_0(N)\) has a sporadic point (whether CM or non-CM) if and only if:
\[ N \notin (S_{CM} \setminus \{15, 17, 21, 37\}) \]
where \(S_{CM}\) is a specific, explicitly bounded set of integers determined in their paper [cite: 10, 11]. 

For the exceptional values \(N \in \{15, 17, 21, 37\}\), the curves \(X_0(N)\) possess finitely many rational non-cuspidal non-CM points, thus inherently admitting sporadic non-cuspidal points [cite: 10, 11].

#### Methodological Innovations
To prove this theorem, the authors utilized a variety of advanced geometric and computational techniques:
1.  **Mordell-Weil Sieve:** To prove that every \(X_0(N)\) lacking sporadic CM points also lacks sporadic non-CM points, the authors deployed a highly complex Mordell-Weil sieve [cite: 11]. While the theoretical underpinning of the sieve is standard, its implementation for this generic classification was technically demanding [cite: 11].
2.  **Involutions and Genus Constraints:** To rule out degree 2 maps from \(X_0(N)\) to small genus curves, the authors exhaustively described the involutions of \(X_0(N)\) [cite: 10, 11]. 
3.  **Bounds on Gonality:** The proof leveraged recent results by Kadets and Vogt (2025) concerning bounds on the gonality of curves, establishing that if a curve \(C/\mathbb{Q}\) has \(\delta(C) = 8\) and genus \(g(C) \ge 34\), it must admit specific bounded-degree rational morphisms to \(\mathbb{P}^1\) or to a positive-rank elliptic curve [cite: 11]. A similar corollary was established for \(\delta(C) = 12\) [cite: 11].

### 2.3 Sub-classifications: Quartic Points and Torsion
In preceding work (December 2024), Derickx and Najman achieved a complete classification of the torsion of elliptic curves over quartic fields [cite: 15, 16]. By the Mordell-Weil theorem, if \(K\) is a quartic field (\([K:\mathbb{Q}]=4\)) and \(E\) is an elliptic curve over \(K\), \(E(K)_{\text{tors}}\) is a finite abelian group. 

They proved that there are *no sporadic torsion groups* over quartic fields; every torsion group that can appear does so for infinitely many non-isomorphic elliptic curves [cite: 15, 16]. This required proving that numerous modular curves \(X_1(m, n)\) lack non-cuspidal degree 4 points [cite: 15, 16]. To resolve the non-cyclic cases, such as \(\mathbb{Z}/2\mathbb{Z} \times \mathbb{Z}/20\mathbb{Z}\) and \(\mathbb{Z}/2\mathbb{Z} \times \mathbb{Z}/24\mathbb{Z}\), they explicitly implemented the action of Hecke operators on non-cuspidal points (the Hecke sieve) for \(X_1(2, 20)\) and \(X_1(2, 24)\) [cite: 15].

## 3. Asymptotic Growth of Prime-Order Torsion

While classifications for small degree fields (like quadratic, cubic, and quartic) provide explicit lists of possible torsion subgroups, understanding the macroscopic behavior of torsion over fields of arbitrarily large degree requires an asymptotic approach. A major 2025 breakthrough by Maarten Derickx and Michael Stoll addressed the asymptotics of prime-order torsion.

### 3.1 Defining the Sets \(S(d)\) and \(S'(d)\)
Following the nomenclature of Kamienny and Mazur, researchers define \(S(d)\) as the set of all prime numbers \(p\) such that there exists a number field \(K\) of degree \(d\), an elliptic curve \(E/K\), and a point \(P \in E(K)\) of exact order \(p\) [cite: 17, 18]. A related set, \(S'(d)\), is defined as the set of primes \(p\) such that there are *infinitely many* elliptic curves \(E\) over number fields of degree \(d\) (with distinct \(j\)-invariants) possessing a \(K\)-point of order \(p\) [cite: 17, 19].

The set \(S'(d)\) is intricately linked to the gonality of the modular curve \(X_1(p)\). Previous results established the exact sets for small \(d\):

| Degree \(d\) | Set \(S'(d)\) [cite: 17, 19] |
| :--- | :--- |
| \(d = 1\) | \(\text{Primes}(7) = \{2, 3, 5, 7\}\) |
| \(d = 2\) | \(\text{Primes}(13) = \{2, 3, 5, 7, 11, 13\}\) |
| \(d = 3\) | \(\text{Primes}(13) = \{2, 3, 5, 7, 11, 13\}\) |
| \(d = 4\) | \(\text{Primes}(17) = \{2, 3, 5, 7, 11, 13, 17\}\) |
| \(d = 5\) | \(\text{Primes}(19)\) |
| \(d = 6\) | \(\text{Primes}(19)\) |
| \(d = 7\) | \(\text{Primes}(23)\) |
| \(d = 8\) | \(\text{Primes}(23)\) |

*Note: \(\text{Primes}(x)\) denotes all prime numbers \(p \le x\).*

### 3.2 The Derickx-Stoll Asymptotic Bounds (May 2025)
In their paper "Prime order torsion on elliptic curves over number fields. Part I: Asymptotics," Derickx and Stoll studied the set \(S(d)\) as \(d \to \infty\) [cite: 18, 20]. Generating unconditional limits on \(S(d)\) has historically been stymied by the difficulty of computing the analytic ranks of modular Jacobians. 

Assuming standard conjectures regarding the sparsity of newforms of weight 2 and prime level that exhibit unexpectedly high analytic rank, Derickx and Stoll established strict asymptotic bounds for the maximum prime order [cite: 18, 20]:
1.  **For even \(d\):** \(\max S(d) \le 3d + 1\) for sufficiently large even \(d\) [cite: 18, 20].
2.  **For odd \(d\):** \(\max S(d) = o(d)\) as \(d \to \infty\) [cite: 18, 20].

The profound difference in the asymptotic behavior between even and odd degrees is deeply rooted in the geometry of the modular curves. For even \(d\), the presence of hyperelliptic involutions and points mapping to the \(j\)-invariant zero (where the covering \(X_1(p) \to X_0(p)\) ramifies with index 3) permits rational effective divisors that yield prime torsion up to the linear bound \(3d+1\) [cite: 18]. For odd \(d\), these geometric structures do not trivially factor, resulting in a sublinear \(o(d)\) bound [cite: 18].

## 4. The Intrinsic Subgroup of the Picard Group

While Mazur's theorem characterizes the isomorphism classes of the rational torsion points (identified with \(\text{Pic}(E)_{\text{tors}}\)), deeper arithmetic information can be extracted by studying symmetric pairings on these groups. In a November 2025 paper, Takao Yamazaki, Yifan Yang, Hwajong Yoo, and Myungjun Yu introduced and analyzed the "intrinsic subgroup" of an elliptic curve [cite: 8, 21].

### 4.1 The Biadditive Symmetric Pairing
Let \(X\) be a geometrically irreducible smooth projective curve over a field \(k\). The authors defined a biadditive symmetric (though not necessarily perfect) pairing on the torsion part of the Picard group:
\[ \langle \cdot, \cdot \rangle : \text{Pic}(X)_{\text{tors}} \times \text{Pic}(X)_{\text{tors}} \to k^\times \otimes \mathbb{Q}/\mathbb{Z} \]
[cite: 21, 22]. This pairing is an analog and generalization of the Frey-Rück (or Lichtenbaum-Tate) pairing, which was originally constructed for finite fields and shown to be perfect when the cardinality of the field \(|k| \equiv 1 \pmod n\) [cite: 21]. 

The **intrinsic subgroup** of \(X\), denoted \(\text{Pic}(X)_{\text{tors}}^{\text{is}}\), is defined as the kernel (the radical) of this pairing [cite: 21]. Specifically, for an elliptic curve \(E\) over \(k\):
\[ E(k)_{\text{tors}}^{\text{is}} = \{a \in E(k)_{\text{tors}} \mid \langle a, b \rangle = 0 \text{ for all } b \in E(k)_{\text{tors}}\} \]
[cite: 21].

### 4.2 Refining Mazur's Torsion Theorem
Yamazaki et al. utilized this intrinsic subgroup to refine Mazur's torsion theorem. Mazur identified the 15 possible full groups \(E(\mathbb{Q})_{\text{tors}}\). The 2025 work determines precisely *which subgroups* of those 15 isomorphism classes can manifest as the intrinsic subgroup \(E(\mathbb{Q})_{\text{tors}}^{\text{is}}\) [cite: 21, 22]. 

The utility of the intrinsic subgroup lies in its ability to encode the reduction type of the curve. The authors demonstrated that if \(X\) has good reduction with respect to a discrete valuation of \(k\), there is a stringent restriction on the values of the biadditive pairing [cite: 21]. As a result, computing the intrinsic subgroup of an elliptic curve over a number field imposes distinct, testable constraints on its reduction type (e.g., distinguishing between good and bad reduction such as in Tate elliptic curves) [cite: 21].

## 5. Torsion Over Infinite Extensions: \(\mathbb{Z}_p\)-Extensions and Cyclotomic Fields

Another natural extension of Mazur's work involves replacing the base field \(\mathbb{Q}\) or a finite extension \(K\) with an infinite field extension \(L\) of characteristic zero [cite: 23, 24]. Since 2024, significant strides have been made in classifying \(E(L)_{\text{tors}}\) where \(L\) is an infinite Galois extension of \(\mathbb{Q}\) or of a quadratic field.

### 5.1 Cyclotomic Extensions of \(\mathbb{Q}\)
In his 2024 and 2025 work, Omer Avci investigated the torsion subgroups of rational elliptic curves over cyclotomic extensions [cite: 9, 25]. Let \(\mu_{p^\infty}\) denote the set of all \(p^k\)-th roots of unity, and consider the field \(L = \mathbb{Q}(\mu_{p^\infty})\) [cite: 9, 25].

Avci built upon previous results by González-Jiménez and Najman, who showed that if \(K\) is any number field with an extension degree not divisible by 2, 3, 5, or 7, then \(E(K)_{\text{tors}} = E(\mathbb{Q})_{\text{tors}}\) [cite: 9]. Avci enhanced this paradigm by relaxing the condition from "not divisible by 2" to "not divisible by 4" when the extension \(K/\mathbb{Q}\) is Galois [cite: 9, 25].

Avci demonstrated that many torsion points arising in these extensions are either rational points directly on \(E\) or correspond to rational points on a quadratic twist of \(E\) [cite: 9, 25]. This mapping back to quadratic twists allows researchers to brutally restrict the possible group structures of \(E(L)_{\text{tors}}\) by directly applying Mazur's original theorem to the twists [cite: 9, 25]. For example, if a curve \(E_d\) (a quadratic twist of \(E\)) is an elliptic curve over \(\mathbb{Q}\), Mazur's theorem explicitly forbids \(E_d(\mathbb{Q})_{\text{tors}} \cong \mathbb{Z}/N\mathbb{Z}\) for certain \(N\) (like \(N=14\) or \(N=18\)), effectively eliminating these as subgroups of the base extension [cite: 9].

### 5.2 \(\mathbb{Z}_p\)-Extensions of Quadratic Fields
In May 2025, Avci expanded this methodology to \(\mathbb{Z}_p\)-extensions of quadratic fields [cite: 23, 26]. Let \(K\) be a quadratic number field, \(p\) an odd prime, and \(L\) a \(\mathbb{Z}_p\)-extension of \(K\). Avci proved a powerful stabilization theorem:
**Theorem (Avci, 2025):** If \(p > 5\), then \(E(L)_{\text{tors}} = E(K)_{\text{tors}}\).
[cite: 23, 26].

This theorem states that the torsion does not grow up the \(\mathbb{Z}_p\)-tower for primes strictly greater than 5. Because the torsion subgroups over quadratic fields were already exhaustively classified by Kenku, Momose, and Kamienny, this stabilization theorem yields a complete classification of the groups that can be realized as \(E(L)_{\text{tors}}\) for these infinite extensions [cite: 23, 26].

For instance, over a quadratic field, the torsion subgroup can be isomorphic to \(\mathbb{Z}/N\mathbb{Z}\) (for \(1 \le N \le 10\), or \(12, 15, 16\)), \(\mathbb{Z}/2\mathbb{Z} \times \mathbb{Z}/2N\mathbb{Z}\) (\(1 \le N \le 6\)), \(\mathbb{Z}/3\mathbb{Z} \times \mathbb{Z}/3N\mathbb{Z}\) (\(N=1,2\)), or \(\mathbb{Z}/4\mathbb{Z} \times \mathbb{Z}/4\mathbb{Z}\) [cite: 9]. Every group in this list (except \(\mathbb{Z}/15\mathbb{Z}\)) appears for infinitely many rational elliptic curves. The rare \(\mathbb{Z}/15\mathbb{Z}\) torsion is exhibited by specific curves, such as 50B1 and 50A3 over \(\mathbb{Q}(\sqrt{5})\), and 50B2 and 450B4 over \(\mathbb{Q}(\sqrt{-15})\) [cite: 9, 23]. Avci's theorem definitively maps this quadratic classification directly onto the infinite \(\mathbb{Z}_p\)-extensions for \(p > 5\).

## 6. Rational Cuspidal Subgroups of \(J_0(N)\)

To understand torsion on elliptic curves through modular parameterization, one must understand the geometry of the Jacobian variety \(J_0(N)\) of the modular curve \(X_0(N)\). The rational torsion points of \(J_0(N)\) encode deep arithmetic properties.

### 6.1 Generalized Ogg's Conjecture
Ogg originally hypothesized about the structure of the rational torsion subgroup of \(J_0(N)\). A generalized version of Ogg's conjecture asserts that the rational torsion subgroup of \(J_0(N)\) is exactly equal to the **rational cuspidal subgroup** of \(J_0(N)\), denoted \(\mathscr{C}_N(\mathbb{Q})\) [cite: 27]. 

The rational cuspidal divisor class group of \(X_0(N)\), denoted \(\mathscr{C}(N)\), is generated by the equivalence classes of cuspidal divisors of degree 0 [cite: 28]. 

### 6.2 Determinations by Yoo and Yu (2023-2025)
Between 2023 and April 2025, Hwajong Yoo and Myungjun Yu (often in collaboration with Jia-Wei Guo and Yifan Yang) made decisive progress on this front [cite: 28, 29]. 

In 2023, they proved that the rational cuspidal subgroup of \(J_0(N)\) is equal to the rational cuspidal divisor class group of \(X_0(N)\) when \(N = p^2M\) for any prime \(p\) and any squarefree integer \(M\) [cite: 28, 30]. 

In April 2025, Yoo and Yu completely determined the structure of the rational cuspidal subgroup of \(J_0(N)\) for cases where the largest perfect square dividing \(N\) is either a single odd prime power or a product of two odd prime powers [cite: 29, 31]. They proved that for such an \(N\), the rational cuspidal divisor class group of \(X_0(N)\) definitively constitutes the entirety of the rational cuspidal subgroup of \(J_0(N)\) [cite: 29]. This resolves generalized Ogg's conjecture for this broad class of levels \(N\), ensuring that no "exotic" non-cuspidal rational torsion exists in the Jacobians for these levels.

## 7. Synthesis of Computational and Theoretical Methods

The rapid advancement in classifying torsion subgroups and rational points on modular curves from 2024 to 2026 is largely attributable to a synergy between abstract algebraic geometry and modern computational algorithms.

### 7.1 Chabauty-Coleman and Chabauty-Kim Methods
When the genus of a curve is greater than 1, determining its rational points becomes profoundly difficult. Hashimoto, Keller, and Le Fourn (2025) explicitly utilized the Chabauty-Coleman method to calculate the rational points on the modular curve \(X_0(p^k)^*\) [cite: 32]. For curves where the genus is 1 and the rank is 0, they computed the torsion subgroup directly to find the rational points. For higher genus cases, Chabauty-Coleman, sometimes in combination with the Mordell-Weil sieve, was strictly required [cite: 32]. 

Similarly, the quadratic Chabauty method (a specific instantiation of the broader Chabauty-Kim method) has gained traction for determining isolated and exceptional points on modular curves, offering a path forward where classical descent methods fail [cite: 12].

### 7.2 Explicit Moduli Descriptions and Descent
The theoretical barrier of constructing explicit moduli descriptions for \(X_0(N)\) (which historically lagged behind \(X_1(N)\)) has seen alleviation. Work by Yamazaki et al. extended uniform methods for constructing explicit generators of the function field \(C(X_0(N))\) [cite: 33]. This concrete moduli interpretation of cyclic \(N\)-isogenies yields explicit formulas for sporadic rational points on \(X_0(N)\) [cite: 33].

Furthermore, explicit \(n\)-descent algorithms on elliptic curves—pioneered extensively by Michael Stoll, John Cremona, and others—remain crucial for computing the Selmer groups and determining the rank and free part of the Mordell-Weil group [cite: 34, 35]. These descent algorithms allow modern computer algebra systems (like MAGMA and SageMath) to rule out the existence of rational points of specific orders by showing that the corresponding Selmer groups are trivial [cite: 10, 35].

## Conclusion

The legacy of Barry Mazur's 1977 torsion theorem is not merely a static list of 15 abelian groups; it is the theoretical foundation upon which a massive, ongoing mathematical enterprise is built. The research output from 2024 to 2026 demonstrates that the study of elliptic curve torsion and the parameterizing modular curves \(X_0(N)\) and \(X_1(N)\) is experiencing a renaissance. 

From Derickx and Najman's exhaustive classification of sporadic points on \(X_0(N)\) of arbitrary degrees [cite: 11, 14], to Derickx and Stoll's asymptotic bounds on prime-order torsion [cite: 18, 20], the mathematical community is rapidly mapping the outer limits of Diophantine geometry. Simultaneously, finer algebraic invariants—such as the intrinsic subgroup of the Picard group identified by Yamazaki, Yang, Yoo, and Yu [cite: 21, 22], and the stabilization of torsion over infinite \(\mathbb{Z}_p\)-extensions proven by Avci [cite: 23, 26]—reveal that Mazur's original classification still harbors deep, untapped connections to the arithmetic reduction types and Galois module structures of elliptic curves. As computational capacity and theoretical frameworks like the Chabauty-Kim method continue to evolve, the full geometry of modular curves and their Jacobians moves ever closer to complete demystification.

**Sources:**
1. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFT1Xu0eL1cbKA1iiriOg3ShZ_vSI18cxqPTxGJEF5HEdpHb9kCo-4bzmjVMTQ0dQG8ACTOaYAG8maltPQqxOnxwoDG9ryEDkYHxlEGsMHsaCVE9YSloNAO2SZIxNdZ0sxX0DEsKEdt84yFXJlYDA=)
2. [uconn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1LWjb6-AB-JNHL7F5cV-WcQIYYNB8sFEO1RgKyNi7AHMWO4ps7xw44n5zi_4xYicD0Ts5O1u7FMn7ASjywdx1xLanZNUnaCqNYN6jI-7rMHN5005zc7mXtOLWS299btz_72VkrvHqFsNNPMnfNVxezI7VWAK3fcaQPxRl1sJI_8FzWrJH4HvwwVRl3oXJI32WSgORuOK-ATzruRIHHQu35jKK0PEhQPp2tA==)
3. [celebratio.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEybir_59NmANxeQbL6hrwXF7hh6bZ9fnm2HXgvk52b85X8BN0hbJi8DE1Tndc-ZdYgYmlOm9z8SDvHxESnrF5xVmnMD7aHe-vqCRVeZ6q3TV4srK_vBkj6ix5YJyQ8tpqMFv4=)
4. [maartenderickx.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8ajusvRiNydwWGoaIBbYL02laPkfFw0UXwcGQURCMLILou1T4nEXAkDYVLnGVsOhXdBtsizII-oKBS10wcZPBO0swh-9F2iSR4D4pymYgf1LbJQDu_ZEcMefoVFpY7ZioBISxwgEoy2kjmBgg)
5. [uni-bayreuth.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxgZW-XQ1hlEtnA65L1G8Eyioo6QB4l91kQ4Fm_xHjBvGIqlmRQE0e_MVpQk2ciFXkz12Rekl6b8sgKirsvAkGtcWiM7D-xtCDCfUhQd4NqhxKFS40suv7NcHzoIr0f3lSK-OjE4j9G-lQgKNlQD1gAjicM-ne75A5dEQXnur_-pldDkF2Cg==)
6. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJF6GgY0BSCPm43hXTjNmXq7buvx8Cxy2uF5kfuWZtsHHM7wRmrXo96PnJ8rmggE0vtcc2cmD2mImPncQspzusEpjCbm8Mz-7a0Oj-2tuvDh4guvvqINODqmT6oK_vp53Qim9dgJaNv9BhianBtqW0nAegIYTxwt75Doi1_mAnN0OhUA7znb5juNVmILWttp9fux2te4cZeHYovyG8aVwwSS3bQ48rSdl239opl6ZpnOkQ_X_Ut15GNQjTKPG-7PUjhiwe7oNRl8dV_3Cn7g==)
7. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFoyUaGNZqPov0H1wPbIsETheoJjPFzyjvHI_A0feWoaGm90hRtUdJCDQt72WR9mqLiaOwProu4opga6iih472LPp2FTj7wfSL3kuAUA2SXcLeUNgnaNh5RVb_JzHU=)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwD1LENHX1STx2M01FZrxFcTxdJ4aQJ5Fk8XLBYYlwIHGN52Efw_QoHXF3rynNZDHfhQ0ZH7uFKC0J3uPF4vkgfZNhVciWiYfbHnkypE3znpWpjj2e_Yc0IQ==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFGZ8tESBLcXZrbjQNDvCL7ceJYbdKVVdFk-WWbo-A-ByrMf2E9gBeckjG9MmDVNT_CoMWQwBD_iYqV9lnhZk--BEcnhEdYjFvwxgGmt8lh2lSaae_n7lwiqnWNg==)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSRDvA4vipT8Zo2YZvXE6PAidPrUNXL8EA2CkkoN1PV3TR1TPOCa5AAqEj1nQmcIWhYJ4MmEjEPSX9wh-0q5IJ-FCPsNCV4SJu5A6bJlSSx175BeiuY1hnEhN3jaBOZcmm8xHCF8_wUJ_lnNouolgBXRr1uJuPCNBsNzM6ScstHA==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfBxMOmpfylRa7XFWYlEE0fmzHeZChXMZufEI9yDykSYb4L_s6QOdS7rCyIVNHeK7qZpDRsudPEXlaRcDpwPXclmNF6C-CMjX_wpwofXAZ6tZU-oWtxA==)
12. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVk7K4iJmZW38qQGg6TwSw6TRvsxjN36VY_YpmJjBNuJOnAgOf27U-xDpjUIOnPy_hm05cSB1lBJ7PjdpNMOYYuKEbCXMcBkMvkPO6OlKPPxf6BWMUwMbGUl8EPU3LWO7ft5NqEACGt6RTe-JN_Ro=)
13. [warwick.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGXu5U8gqDFltkQ1UzAeG0b8SPUD4BAFjZoxwewxnyYu2fVk0II8gunPClC1DpWzAsxpdjDTPz8x0yJYjxwslaMgvoTavn9mnfECFFhaDvvQAwxRI0haV1_OtVmTrcacrDCHO5I5vQLjeMqcLGD-uziQ4haGNf4uM-9lR7P8Q5tQnw422t7GMLdZd9p3QT9p8rOg==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRt2jiPqJe5TNFTHyVMCILDAVFvPcutoBKiFMd_oqcK78xyvSLrGfB7UyAB4qqsCVOkjjECIHlMy1UPeYVe6q3hInDyJNWCeoEASh_aEZ2XcRRxWLA9Q==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzMn901Z26-vc2TX6jOqCK0UxUs5b1xyvysUhVhKk4kDH23NReka5W_-0TuNbvOarN6yHMneOKiZifmlQtPYAvgoTw8lIJ9kUDG79PR5X_SmCwUwVq4Q==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHTquFe3LYj6_Htb7vZ-5Jb0ddIe-bzyoINLzsCWTRDzzgv2s6zrFwo1fEQcUm6mf0XV1NbZ2Q3lI2p3pxG1AGQF4Gl_Z2yCTF1GlUC84sZ7g4gbJDgQ==)
17. [uni-bayreuth.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZZyXjjyw1Fa3ad21A9seZUk2j1Wy85co8mhNRXr3x9PB7sl_RfIJmPqtwplx0k5WITOvQDy2GG2fuf0kjiPEl0_BpoTJj_AWylQwegDzDY_4D0oy8ah8I_Y46s1qLWMsxsZcTtYbXOPmu05gjCkhg1w==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-DqkW2kMrkAaLGXyFDiuw24cu-KuMdcQ7Q0ZJmw-XJJkf3wjFVqpCLL0NgTi-pNCnuRWdtdB-05lapblB3Y1ihQQqJ1YYfMKbiwK77Z-aNfc5e5d4jw==)
19. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_xGbNExZ3KTWNagz0jC69_gpFMymKDwQ3ZJlSSLle8e1WXhNqElGJ8L6XzSHvZr5VmGjJKavMaaa3Wgwi_tKYuYu3zO9co9QxveWC2e_4cmXeC2vrtv5DjQNpGw6gY87XlNxXNmYaqQ==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8d1gYBQ031B-O5gwFgp0kVL-hA9cmA-g1nMV3d7IgjqYznSQWfLo4NRI_7rPnzXSJVEPDioy0LwqN-0M061qGGowj53_U4F-39iVvxVRyQSzB5ejPJA==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiDRjhf_ar3bAmlPD0EAbR5I4lW0ITVheCXnxGR2yXW3liW36fUbJ1CtdqNbq8x-4L_Axq31RuohlllF7-P3PJOO0If3nbblwWE_ZYo9NDP8AwNotWIQ==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERlDKjEVpKa-zA5ig-I5FM4ZHVBlO17ZL3RYAJ0CsZhWXxDc744Jrepvyn3oPuAlQnOETO848AdZsmDSW1IdX5W9pFJnqc_opzZQVqcLmP1-2lM1rIcA==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGoaJi1tXp3Tge8nB0L_61fJsCa0oIsr7NlIKKhtYcvFHAGvVkDICd7L4ip7u907-Mw7jo0QCjdy9-tbJyPbVYdhoCE8wyS24FsRqmKLTqJ0oN4MF3hBrh3Xg==)
24. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5o7WCxQisqNu_4RASSbO7vzvOTZ2DEqF9x-ssh221HwlWtpxWjn1fbslW0YJOWt8Z_YrTuz00jKyy_wPdrUDrrb-Hl_ZK0ICRUaxMg1BeHxTr_2L6VNivlN0-HrNiI-l3LQDnZmqNpXN5jxFVUmwXkiiK_FV0OTDIGu8doSX2GxGmdqs=)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXMgF7hg7gJi8vRVRPr0NRuCSFQlXgY-xhzO9HwmlQG8GeUr912b2h_wp5nGLXaxtra7Vyoecf2pwsGQX1kZRQp5_Dywznt6Q9oP1UH8SxudTOzW9L1dQfpw==)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKMv47GHnuyYdWo0IevH5HdObZ9Gr2HNbAi8iuVRpdhrzRgMTnGgNfnetUwPHfjo0c4RROjXjflq53Tb8FEvDpJWt7mAu6ySCCY_zUcKYSfWQiwX1SUJyJknChjSw2-AGjFCst3GX2YvuUr3b4wGkje2iSALCRWQKTVW_vjOAIeHDgZmLLnSW_Fh_PJelOxdgtz50nxeNXL5nk80doLLOnc_4hrwWZIuOktr_z5wjDA9ZlkLViQAhcAcXP4KGFaw==)
27. [snu.ac.kr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLakIXcmEu0JJdI0e-ZNy2PxtzLuMxBYihjIeuFBSty9ZUzcplBVJ4xLw-Xk4wm-JHGQPeEi8pimR-0bdBI3OuIqm4z9bndwt6c9u-n7WIkvu9Yrt9P61Yshc8nGNpDcqkSLv5VH-MC1mxWFcQgS61fWQyy3tMor2srfa3NZCunyiG22MO3OhJN51wcEpIO7VVgIWhzc8yBIpmT1Q=)
28. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMXy0v_cftzLbj4hG_mAMZ1Koh_kvXwdOqX8ulNSabO8J6HjDoUp0REkHZE2QPxWfI0meXGRg-0FIGl4yS4qSd8ewrR14dn28szWDxBh2PykozcIWlL_E61wpuAPQFHFEZAownBJ_0OQ==)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtsj84hvSlpPet4xo8Rt6B7WDjnfLQZC8FKbT9SGPcvkUCqlVycfDU9B81lTX0xNMMj7X1QcCYvBXEbrrP9qRyYH4g-BJkY3IVoZagGULZO1CjoRgeuQ==)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUoSZt2XCpm5u5XFi4UoSmCgztqO9r3Eneep8RicSU6Er_F1nF4IR5JcDielErb4Ml5QjYfvUFHy9bSyKx4uv0NM6eO1zKwJDp29_RzFureM8NPqf4uDkZUbyMkFNcdGjsfzjUPGc=)
31. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtny9y1cRoSeBygofJzELocj2ieNM-kFo8xEfQ77Tvk2cZwTiuNdaNEp59Vv1RKKJlSsaFnuh0rKrVE2mWAyfHWBZpqR7QNWE6nhMkLB7vVNemPoThjfWwYJSuGDIhv-gOiKRQ7hxMhiP5UtWtFcow5zhxXbQomvigtxdFwCMl1U4zoe5DgauHuns33zTE4w==)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGv1qA2p4EqDTuwwzG3-IoWwHfvO63fq9K8-Skw9Qz1ArpF0tWmQvvxsQ886vWhXCkeSVwD00rOLD6AYDiIxTG9MgQFlS9FKKjTwKhwMltGKuYFs2kzvA==)
33. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1ljMNwnZxVfaWcnugkgeU0tqX2uRj7J7ZTE7-fsodr_nE_vtOPeVBC90lIjYP_yGuGyp23MQazCYsWDfHk5LVBAdK8W-v_EhYFERiaiXigH-6RREryUsWWpB1DpiMmZT4WjpnYDibdPMBUJTlmmvDm8vQsO-_oWcprPvYbn9rtd1iDZfloSFP7sNbdSwjCboghApajdXjcLiWKhBWTzwfm7xc7SDFo3sj2uHrIz-zKSQd_ZDgrXe17WtGgMJNwQ==)
34. [clemson.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-smbvY9dvG4mjCkOJpUwnC-C28sr1K3E4osZydYGnWEGIlRH_fPxsyxHZxJJlJi_88U-kxm3t1K5oWL_ah_eMfO9A3dEMpxABlq73ZBAgX8utjeV2ltwJ-hKgMEB4SkUPylarfJcQb1A9OkUFZ4Ud0gi0khn5Dtw2Brz8X2W01iC6a2DeaVB4aQ==)
35. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFi6SDXZ8SQ8_RkcIgcYbQanPjVvM1UJAW8rrHWdRd6M9Q5pnFW-MyxbDfhjKFTAHHmTXXYdHMi0elq6-FvEce5H22GuCmp8qiEZ5rkKuEdsUz9jkZvSiFqXlkkCgmZjLhgBJ0F_Ah)

