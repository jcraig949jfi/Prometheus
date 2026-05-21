# Iwasawa lambda / mu invariant computations 2024-2026 (Greenberg conjecture)

**Pythia queue id:** 171
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc5emdQYXJ1NEVPMmNfdU1Qa0xLYmtBcxIXOXpnUGFydTRFTzJjX3VNUGtMS2JrQXM
**Elapsed:** 248s
**Completed at:** 2026-05-21T16:59:28.725786+00:00

---

# Iwasawa $\lambda$ and $\mu$ Invariant Computations and Greenberg's Conjecture (2024-2026)

**Key Points**
*   **Real Quadratic Fields:** Comprehensive computations by Mercuri, Paoluzi, and Schoof (2024–2025) have confirmed Greenberg’s conjecture for the prime $p=3$ across all real quadratic fields with discriminant $f < 100,000$, demonstrating that the 3-class groups remain bounded in cyclotomic $\mathbb{Z}_3$-extensions.
*   **Elliptic Curves:** Significant progress has been made regarding Greenberg's $\mu=0$ conjecture for elliptic curves. Recent work by Chakravarthy (2024) establishes that $\mu \leq 1$ for almost all primes of good ordinary reduction, while Ray (2024) proved the simultaneous vanishing of 5-primary $\mu$ and $\lambda$ invariants for a positive density of elliptic curves.
*   **Methodological Innovations:** The integration of Massey products in Galois cohomology (Qi, 2024) and novel criteria utilizing special values of $p$-adic $L$-functions (Knospe, 2024) have dramatically expanded the computational toolkit for determining exact $\lambda$-invariants. 

The study of Iwasawa invariants remains a central pillar of modern algebraic number theory. Originating from Kenkichi Iwasawa's groundbreaking work in the mid-20th century, Iwasawa theory examines the asymptotic growth of arithmetic objects—such as ideal class groups and Selmer groups—along infinite towers of number fields, most notably $\mathbb{Z}_p$-extensions. The parameters governing this growth are the structural constants known as the $\mu$ (mu), $\lambda$ (lambda), and $\nu$ (nu) invariants. Since 1976, Ralph Greenberg's conjecture—which broadly posits the vanishing of the $\mu$ and $\lambda$ invariants for the cyclotomic $\mathbb{Z}_p$-extensions of totally real number fields—has stood as one of the most significant open problems in the discipline. Between 2024 and 2026, the intersection of theoretical breakthroughs and high-performance computational mathematics has yielded profound insights into these invariants. This report synthesizes the expansive body of literature and computational data generated during this period, detailing advancements in real quadratic fields, CM fields, Dirichlet characters, and the Iwasawa theory of elliptic curves.

## Introduction to Iwasawa Invariants and Greenberg's Conjectures

For a number field $k$ and a prime number $p$, a $\mathbb{Z}_p$-extension is an infinite Galois extension $k_\infty / k$ such that the Galois group $\text{Gal}(k_\infty / k)$ is topologically isomorphic to the additive group of $p$-adic integers, $\mathbb{Z}_p$ [cite: 1, 2]. By the fundamental theorem of Galois theory, there exists a unique intermediate field $k_n$ for every integer $n \geq 0$ such that $[k_n : k] = p^n$, forming a tower $k = k_0 \subset k_1 \subset k_2 \subset \dots \subset k_\infty$. 

Iwasawa's foundational theorem states that if $p^{e_n}$ denotes the exact power of $p$ dividing the class number $h(k_n)$ (the cardinality of the ideal class group $A_n$), then for all sufficiently large $n$, the exponent $e_n$ is given by a linear polynomial:
\[ e_n = \mu p^n + \lambda n + \nu \]
where $\mu, \lambda \geq 0$ and $\nu$ are integer constants independent of $n$ [cite: 1, 2]. These constants are the Iwasawa $\mu$, $\lambda$, and $\nu$ invariants of the extension. They inherently measure the $\Lambda$-module structure of the inverse limit of the $p$-parts of the ideal class groups, where $\Lambda \cong \mathbb{Z}_p[[T]]$ is the Iwasawa algebra [cite: 3, 4]. 

In 1976, Ralph Greenberg proposed what is now famously known as Greenberg's conjecture: for any totally real number field $k$ and any prime $p$, the Iwasawa invariants associated with the ideal class group of the cyclotomic $\mathbb{Z}_p$-extension $k_\infty/k$ satisfy $\lambda_p(k) = \mu_p(k) = 0$ [cite: 5, 6]. This implies that the $p$-part of the class number remains bounded as $n \to \infty$ [cite: 6, 7]. While the Ferrero-Washington theorem (1979) established unconditionally that $\mu_p(k) = 0$ for all abelian extensions of $\mathbb{Q}$ [cite: 1, 5], the vanishing of the $\lambda$-invariant for totally real fields remains largely conjectural and is heavily targeted by computational verification.

An analogous and equally critical conjecture exists in the Iwasawa theory of elliptic curves, also formulated by Greenberg. It states that if $E/\mathbb{Q}$ is an elliptic curve with good ordinary reduction at $p$, and the Galois module of $p$-torsion points $E[p]$ is irreducible, then the Selmer group of $E$ over the cyclotomic $\mathbb{Z}_p$-extension of $\mathbb{Q}$ has a $\mu$-invariant equal to zero [cite: 8, 9]. The pursuit of these two conjectures has driven the intense computational efforts documented between 2024 and 2026.

## Computational Verification in Real Quadratic Fields (2024–2025)

The most definitive computational triumph regarding Greenberg's original conjecture in recent years was achieved by Pietro Mercuri, Maurizio Paoluzi, and René Schoof (published 2025). Their work focused on the prime $p=3$ and involved an exhaustive computation of the 3-class groups $A_n$ for the cyclotomic $\mathbb{Z}_3$-extensions of all real quadratic fields $F = \mathbb{Q}(\sqrt{f})$ with discriminant $f < 100,000$ [cite: 7, 10]. 

### Algorithmic Methodology and Galois Modules

To computationally verify that the order of $A_n$ is bounded independently of $n$ (which is equivalent to $\lambda = \mu = 0$), Mercuri et al. studied a specific finitely generated $\mathbb{Z}_3$-module, $C(f)$, defined in terms of cyclotomic units [cite: 7]. For an intermediate field $F_n = \mathbb{Q}(\sqrt{f}, \zeta_{3^{n+1}} + \zeta_{3^{n+1}}^{-1})$ of degree $3^n$ over $\mathbb{Q}(\sqrt{f})$, the ring of integers $\mathcal{O}_n$ contains a subgroup of cyclotomic units. The 3-part of the quotient of the unit group $\mathcal{O}_n^*$ by its cyclotomic subgroup is a finite group $B_n$, which shares the same cardinality as the 3-class group $A_n$ [cite: 7]. 

The inverse limit $C(f) = \lim_{\leftarrow} C_n$ is a cyclic module over the Iwasawa algebra $\Lambda = \mathbb{Z}_3[[T]]$, allowing it to be expressed as $C(f) \cong \Lambda / J$ for some $\Lambda$-ideal $J$ [cite: 3, 7]. Greenberg's conjecture is true if and only if $C(f)$ is finite, which occurs if and only if $J$ is a proper $\Lambda$-ideal of finite index. The computational strategy employed Nakayama's lemma: letting $\omega_n(T) = (1+T)^{3^n} - 1$, the module $C(f)$ is finite if and only if the shrinking ideals stabilize, i.e., $J + (\omega_n) = J + (\omega_{n+1})$ for some $n \geq 0$ [cite: 3, 7]. By computing these ideals iteratively, the researchers could definitively bound the growth.

### Empirical Results for $f < 100,000$

The algorithm was executed over all 30,394 real quadratic fields satisfying the discriminant bound. The results provided spectacular numerical evidence in favor of Greenberg's conjecture:
1.  **Universal Boundedness:** In 100% of the cases tested, the module $C(f)$ was proven to be finite, confirming that Greenberg's conjecture holds for $p=3$ and $f < 100,000$ [cite: 7, 11].
2.  **Trivial Modules:** For the vast majority of discriminants, the module $C(f)$ is identically zero. Specifically, $C(f)$ was non-zero for only 3,359 out of the 30,394 fields, representing approximately 11% of the dataset [cite: 7].
3.  **Maximal Ideals:** Among the 3,359 fields with non-zero $C(f)$, 2,218 had the defining ideal $J$ equal to the maximal ideal $(3, T)$ of $\Lambda$. In these specific instances, $C(f)$ has an order of exactly 3 [cite: 7].

For discriminants categorized by their residue class modulo 3, the data was parsed further. For instance, among the 11,394 fields with $f \equiv 2 \pmod 3$, exactly 1,250 yielded a non-zero $C(f)$ module (approx. 11%), with 781 cases satisfying $J = (3,T)$ [cite: 7]. This massive computational undertaking not only verified the conjecture in an unprecedented range but also provided a rich repository of $\Lambda$-ideals for structural analysis [cite: 7, 12].

## Biquadratic, Multiquadratic, and Even K-Groups

While real quadratic fields provide a foundational testbed, computational Iwasawa theory from 2024 to 2026 heavily explored higher-degree fields. 

### Real Biquadratic Fields

M. M. Chems-Eddin and H. El Mamry (2024–2026) conducted extensive research on the Greenberg conjecture for real biquadratic fields, specifically regarding the cyclotomic $\mathbb{Z}_2$-extension [cite: 13, 14]. They investigated the stability of the 2-rank of the class group and successfully identified several families of real biquadratic fields $K$ where the rank of the 2-class group $A(K)$ equals the rank of the 2-Iwasawa module $A_\infty(K)$, strictly bounded by $\text{rank}(A(K)) \leq 3$ [cite: 13]. 

A critical component of their methodology relied on computing unit groups via Wada's method and applying Fukuda's theorem [cite: 14]. Fukuda's theorem stipulates that if $k_\infty / k$ is a $\mathbb{Z}_2$-extension where ramified primes become totally ramified past layer $n_0$, and if $\text{rank}(A(k_n)) = \text{rank}(A(k_{n+1}))$ for some $n \ge n_0$, then the rank stabilizes for all subsequent layers [cite: 13, 14]. Chems-Eddin and El Mamry determined the complete list of all real biquadratic fields exhibiting a trivial 2-Iwasawa module, confirming Greenberg's conjecture for these infinite families unconditionally [cite: 13]. Furthermore, they computed exact 2-class numbers for heavily ramified fields of the form $\mathbb{Q}(\sqrt{2}, \sqrt{p_1}, \sqrt{p_2})$ for primes $p_1, p_2 \equiv 1 \pmod 4$ [cite: 15].

### Even K-Groups of Rings of Integers

Beyond class groups, Iwasawa invariants possess deep topological and algebraic K-theoretic implications. Li-Tong Deng and Yong-Xiong Li (2026) published an asymptotic formula determining the order of the 2-primary part of the even K-groups ($K_2\mathcal{O}_{K_n}$) for rings of integers in the $\mathbb{Z}_2$-extension of real quadratic number fields [cite: 16]. By analyzing the 2-adic divisibility of Dirichlet $L$-series at negative integers, they successfully extrapolated the exact Iwasawa $\lambda, \mu$, and $\nu$ invariants for these K-groups. Notably, for specific fields such as $\mathbb{Q}(\sqrt{p})$ or $\mathbb{Q}(\sqrt{2p})$ with $p \equiv \pm 3 \pmod 8$, they determined the complete structure of the 2-primary tame kernels, effectively porting Iwasawa-theoretic bounding techniques into algebraic K-theory [cite: 16].

## Analogs for CM Fields and S-Ramified Extensions

While Greenberg's conjecture natively targets totally real fields, researchers have formulated and tested analogous behavior in CM (Complex Multiplication) fields. Peikai Qi and Matt Stokes (2024) studied CM fields $K$ with maximal totally real subfield $K^+$. Under the assumption that primes above $p$ in $K^+$ split in $K$, they isolated a set $S$ containing exactly half of the prime ideals in $K$ above $p$ [cite: 17, 18]. 

Assuming Leopoldt's conjecture is true for $K$ and $p$, they demonstrated the existence of a unique $\mathbb{Z}_p$-extension of $K$ unramified outside of $S$, termed the $S$-ramified $\mathbb{Z}_p$-extension [cite: 17, 18]. Because this extension mimics the behavior of the cyclotomic $\mathbb{Z}_p$-extension for totally real fields, Qi and Stokes conjectured an analogue of Greenberg's conjecture: for the $S$-ramified $\mathbb{Z}_p$-extension of a CM field, the invariants $\mu = \lambda = 0$ [cite: 18]. They successfully proved that the order of the group $B_n$ is bounded as $n \to \infty$, generalizing earlier criteria developed by Greenberg [cite: 18]. Furthermore, they provided a numerical criterion for the vanishing of $\mu$ and $\lambda$ for imaginary biquadratic fields, expanding on earlier computational frameworks established by Fukuda and Komatsu for real quadratic fields [cite: 17, 18].

## Methodological Innovations: Massey Products and Bockstein Maps

A major theoretical advancement enabling new computations of the $\lambda$-invariant came from Peikai Qi (2024–2025), who linked Iwasawa theory to higher algebraic topology via Massey products [cite: 19]. Historically, calculations of $\lambda$-invariants for imaginary quadratic fields and cyclotomic fields often hit computational bottlenecks when attempting to explain why $\lambda$ could exceed 1. 

Qi utilized the generalized Bockstein map—a cohomological tool introduced by Lam, Liu, Sharifi, Wake, and Wang—to compute the Iwasawa $\lambda$ invariant in terms of Massey products in Galois cohomology with restricted ramification [cite: 19]. In situations where the class group can be decomposed into pieces annihilated by $p$, if a specific $p$-primary piece is non-zero (isomorphic to $\mathbb{F}_p$), the $\lambda$-invariant corresponding to that piece is $\geq 2$ if and only if a specific Massey cup product vanishes [cite: 20]. 

This cohomological translation provided a new, unified proof and generalization of older results by Gold and McCallum-Sharifi [cite: 19]. By comparing the estimation of class group sizes via traditional Iwasawa $\Lambda$-modules against the relative sizes evaluated through generalized Bockstein maps, Qi derived explicit descriptions of the cyclotomic Iwasawa $\lambda$-invariants for imaginary quadratic fields entirely in the language of Massey products [cite: 21, 22].

## Computations of $\lambda$-Invariants via $p$-adic L-Functions

The Iwasawa Main Conjecture (proven by Mazur and Wiles for $\mathbb{Q}$) intimately links the algebraic Iwasawa invariants (derived from class groups) to the analytic Iwasawa invariants derived from the $p$-adic $L$-function, $L_p(s, \chi)$ [cite: 5, 23]. Heiko Knospe (2024) significantly advanced the algorithmic capacity to extract $\lambda$-invariants for Dirichlet characters $\chi$ of arbitrary order [cite: 24]. 

By the Ferrero-Washington theorem, the $\mu$-invariant associated with $L_p(s, \chi)$ vanishes, meaning the corresponding Iwasawa power series $F_\chi(T)$ factors into an invertible power series and a distinguished polynomial of degree $\lambda_p(\chi)$ [cite: 23]. This $\lambda$-invariant precisely counts the number of zeros of $F_\chi(T)$ on the open $p$-adic unit disk [cite: 23]. Knospe leveraged special values of the $p$-adic $L$-function and its derivative to establish highly efficient computational criteria to differentiate exactly whether $\lambda = 0, 1, 2,$ or $\geq 3$ [cite: 23, 24].

When the $p$-adic $L$-function features a trivial zero at $s=0$ (e.g., if $\chi\omega^{-1}(p) = 1$ where $\omega$ is the Teichmüller character), Knospe utilized the formulas of Ferrero-Greenberg and Gross-Koblitz to dictate strict lower bounds, identifying conditions where $\lambda_p(\chi) > 1$ or $> 2$ [cite: 23, 24]. Additionally, Knospe extended the classical twisting methods of Ernvall-Metsänkylä and Dummit et al., calculating $\lambda$-invariants by twisting $\chi$ with characters $\psi$ of the second kind and explicitly evaluating $L_p(s, \chi)$ at negative integers $s = 2-p, \dots, 0$, as well as leveraging the value at $s=1$ [cite: 23, 24]. These algorithms were integrated into SageMath, permitting the generation of massive datasets regarding the statistical distribution of $\lambda$-invariants when fixing either the prime $p$ or the character $\chi$, subsequently compared against $p$-adic random matrix heuristics proposed by Ellenberg, Jain, and Venkatesh [cite: 25, 26].

## Iwasawa Invariants of Elliptic Curves and Selmer Groups

Greenberg's conjecture extends profoundly into the arithmetic of elliptic curves. For an elliptic curve $E/\mathbb{Q}$ with good ordinary reduction at $p$, the dual of the $p$-primary Selmer group over the cyclotomic $\mathbb{Z}_p$-extension, denoted $\mathcal{X}(E/\mathbb{Q}_\infty)$, is a finitely generated, torsion $\Lambda$-module (as proven by Kato and Rohrlich) [cite: 4, 27]. Greenberg conjectured that if $E[p]$ is irreducible as a Galois module, the $\mu$-invariant of this Selmer group vanishes ($\mu = 0$) [cite: 8]. Between 2024 and 2026, severe dents were made in this conjecture through both deterministic bounds and statistical density theorems.

### Bounding the $\mu$-Invariant

In August 2024, Adithya Chakravarthy achieved a major theoretical milestone regarding Greenberg's elliptic curve conjecture. While initial drafts suggested $\mu=0$ for almost all primes, the peer-reviewed correction established a rigorously proven upper bound: if $E$ is an elliptic curve over $\mathbb{Q}$, then the Iwasawa $\mu$-invariant satisfies $\mu \leq 1$ for all but finitely many primes $p$ of good ordinary reduction [cite: 8]. This effectively tightens the geometric growth rate of the Selmer group exponentially, bringing the mathematical community to the absolute precipice of Greenberg's full conjecture.

### Statistical Density of Vanishing Invariants

Anwesh Ray (2024) approached the $\mu=0$ conjecture using arithmetic statistics. For the prime $p=5$, Ray proved that both the 5-primary Iwasawa $\mu$-invariant and the $\lambda$-invariant simultaneously vanish for an explicit positive density of elliptic curves $E_{/\mathbb{Q}}$ [cite: 28]. The curves evaluated feature good ordinary reduction at 5 and were ordered by height. Ray's proof heavily leveraged the pioneering work of Bhargava and Shankar on the distribution of 5-Selmer groups of elliptic curves [cite: 28]. 

Further statistical heuristic work by Katharina Müller and Anwesh Ray (2024) extended the topological heuristics of Poonen and Rains. They conjectured that the density of 2-bridge links for which the $\mu$-invariant vanishes is 1 (100%), backing this with substantial computational evidence. By framing the vanishing of $\mu$ as the intersection $M_1 \cap M_2$ of two Iwasawa modules in a specific inner product space, they set new directions in arithmetic topology and statistics [cite: 29]. 

### Additive Primes and Hida Families

Historically, Iwasawa theory for elliptic curves required the prime $p$ to be of good ordinary reduction. However, cutting-edge research has extended invariant computations to additive primes. Antonio Lei, Robert Pollack, and Naman Pratap (2025) investigated the $\lambda$-invariants of Mazur-Tate elements of elliptic curves defined over $\mathbb{Q}$ at primes of additive reduction [cite: 4]. They established strict bounds, showing that $\lambda(\theta_{n,i}(f)) \leq p^{n-1}(p-1)$ for $n \gg 0$, and correlated these additive invariants to the potentially supersingular and potentially ordinary reduction types, validating their theoretical bounds via extensive SageMath computations [cite: 4].

Robert Pollack (2025) further studied Iwasawa invariants within the context of residually reducible Hida families [cite: 30]. He demonstrated that the vanishing of the algebraic or analytic $\mu$-invariant for a single modular form lifting a residual representation $r$ implies the vanishing of the $\mu$-invariant for *all* such forms in the family. Furthermore, Pollack derived explicit formulas showing that, assuming $\mu=0$, the $\lambda$-invariant is strictly constant across branches of the Hida family of $r$ [cite: 30]. Similar congruences were proven by David Delbourgo and others regarding the transition formulae for the analytic $\lambda$-invariant modulo $p$ between congruent elliptic curves, establishing that if the Iwasawa Main Conjecture holds for an elliptic curve $E_1$, it holds equivalently for a congruent curve $E_2$ provided $\mu=0$ [cite: 31].

## Generalizations: Artin Representations and Drinfeld Modules

The rigid algebraic structures of Iwasawa theory have also been translated into geometric and higher-dimensional representation theory recently.

**Artin Representations:** Peikai Qi and collaborators (2025) investigated the Iwasawa invariants associated with Selmer groups of Artin representations [cite: 2]. For a finite, totally imaginary Galois extension $K/\mathbb{Q}$ and an irreducible Artin representation $\rho: \text{Gal}(K/\mathbb{Q}) \to \text{GL}_d(\overline{\mathbb{Q}})$, they evaluated the Euler characteristic formula of the Selmer groups over $\mathbb{Q}_\infty$. They developed explicit criteria for the vanishing of the algebraic Iwasawa invariants, establishing a direct relationship between the vanishing of the Selmer group and the "$p$-rationality" of the field $K$ [cite: 2]. For instance, if $K$ is $p$-rational and $p$ does not divide the class number of $K$, the Selmer group $S_{\chi,\epsilon}(\mathbb{Q}_\infty)$ strictly vanishes [cite: 2].

**Drinfeld Modules:** In the function field analogue, Hang Chen (2025) presented breakthroughs regarding the $\mu$-invariant of fine Selmer groups associated to general Drinfeld modules [cite: 32]. Let $F$ be a global function field over $\mathbb{F}_q$ and $\phi$ an arbitrary Drinfeld module over $F$. Chen proved that on the constant $\mathbb{Z}_p$-extension of $F$, the Pontryagin dual of the fine Selmer group associated to the $P$-primary torsion of $\phi$ is a finitely generated Iwasawa module whose $\mu$-invariant strictly vanishes, confirming the analogue of Greenberg's conjecture unconditionally in this geometric setting [cite: 32].

## Conclusion

The period from 2024 to 2026 marks an era of aggressive computational confirmation and deep structural re-evaluation in Iwasawa theory. Greenberg's conjecture for totally real fields has survived extreme computational stress-testing, with Mercuri, Paoluzi, and Schoof confirming it without exception for 3-class groups up to discriminant 100,000 [cite: 7, 10]. Concurrently, the $\mu=0$ conjecture for elliptic curves has seen its theoretical boundaries aggressively compressed, with $\mu \leq 1$ established for almost all good ordinary primes [cite: 8] and positive density validations achieved for $p=5$ [cite: 28]. 

The introduction of novel methodologies—such as the utilization of Massey products by Qi to resolve the algebraic origins of the $\lambda$-invariant [cite: 19, 20], and the deployment of twisted $p$-adic $L$-function algorithms by Knospe [cite: 23, 24]—has equipped number theorists with algorithms capable of probing depths previously obstructed by computational complexity. As researchers increasingly link these invariants to random matrix heuristics, topological Bockstein maps, and Hida families, the ultimate resolution of Greenberg's conjectures appears increasingly tethered to the synthesis of highly optimized algorithmic computation and advanced Galois cohomology.

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERjX9kV0YEhT2MWDNVpKf37nCZlmCm6Vw0RRC1PtVpS_DMezY0EBen9uz2kV1mwOY8-sEKaFzhIZu_3jcCm5OQ39lkQUESvsOZUCATTHGjVKtqdtI1FOB12Aml8zPxm3dKVxKIX7NJdRZLw83IxiXHTiSslAC_dyYcu8ubF2IKcJb2ByWbK9w3OO7JR4QuyHakMnzC8k8ndlBG-UA9fVVaAFsS8rEtCsdBVAIzmzYz)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFe8Rmeu3-dSfWbKvNInqG9r7k7Q_R74rvNpRbR-UzSDsyd8H2NcV0DduPWO_-C2ZgB4e5M89y7XTkelVooLg4_2AsnpPwhYMSLbsK89JS6Ps-SNRUj)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZHhSpP4KQqEtlJ04CzROPcdJROoC-2Th4nyfUsV6C5ClsxNuuEgBAa5fx5kSlzEUTlu5YjkqIhy-XiYijbbtJWLuVCUR3cemnKqnbuX6BE44ebLRuaDvqTVU7lDKBtnud3Zitp5AbgTKTVUIylC18rlUKUpZO1GLyPx_SX8cDZKO0GtSTNs5VDuYR95CsbjFJ8QuBbFbUiGEpy7ypxHU=)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGveIjDZhVoPObSjpimcJypyIBYHQN1PsUMTFfNpexfTHxL1j6GnESpUmGTTKLjn6X8n2ynp_8DbgdpXk5nqMZ3Fl9L-TPqfsb_Tfbx2M2tN9Kk2xoXKvse)
5. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHU1H5eS6nuLm8zKmQmDtWSFI-EgXscrPyNqXfg8zxsQAId94jUw70q0U8Fshi7iGdKNVnvVZ7Al-4y9pE5yHGVY8TP74GFiVimIN42eTLVSCANb-uaydHYd-ZZrw0LMxqJx4qqTOwT6WlcGsYrX3JSV0lVbayj4wWHcHKa0dhxC17gU9irupJXPsFrCfJ3ESxe4hthpGZUC1fizNsv9K7IMUJoqevcuAayZreuBzHxH2opTclr2j8cY7tSmBjKQkeD5FoFv3GoeOYvghEjOPWdE2hVioQHxq8Fog==)
6. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIAuzelLNe75uNKccyIAx50g7zvmbE1uj5-Y6LL1ESXcuDEfScpP6cnCN6RP90p1vooF4mMFWH01k51KQRyxTrb1dEeOmc9vw3K3co3D4F6IwPPkuN0yemuJRaRitEU0yXqq--PGO-G9HjOrs=)
7. [uniroma2.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXxeWCJ3gSqTwO2vuHxeDz3Z4mV1XE0lnKehenYsREz4Obtg8Qle4K0cDQaXhw-4UTaMF9hC4ade9SWs1miDA_OwwtfWnyuYqJoX26NKP022MpZ5Z8680XuORCrwyh0ISlwOaNQ0Kqmo4=)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBxAYapUzYeMvJnYcLKhcHImz-__77-XFrh3kpHMTTimz9HP_Yu9CQbKbTdEFqsGxsewaGb5hk57pKTYL2lOwUTgu05LJVD7_2ZS56MBMRkAOanmS0)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHa4q92KzKgcm51_R2cHjX1KAKmPX9OciOp4T_EigqQDt_EGFtcszmgn_xViiPiHTeiaLUeJ--1W6h3caNacZotQ_r7zl61mY6RebuERA5GlZrcNrCbJUBNBca9U-7P-xt_V2R_zN3WbkrsNWRijabXdlpqqprkkC_zKhC8G9SkF7CrIG4lwpyqlMzAJwbJYfGrf_xd_re1F9fLoqpZF7FK)
10. [jexpmath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxusZPC_aS1XNzzN5oI2-RFd5hEYUKILxWGaM--Ua93ZDk9NGb2M2jk_HFp07G4yvFNhL8pjw6LMuD227Pv_-mCivuHLGr8L93nS4pNGKlpZ-eYTZFeLPHnrwTYBXmgZ2CppK_OJrw9ndxOOAON69bgVb1ZTy3M3Y=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdOJvO8YBeZioLUbSA4kgfxLfJT8bTj7tSAgh9Oia4dlNhveVToh6XRrT9Q7_HPzjNUOI9OapaLG1UpJcZitPDvUVq9EGtum3WhtvaXDzEMohy-TDt)
12. [amathr.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHJHaHM87EYuUkk7JeLxAbypBGDxOXVLmBDovWrWO-DIq_APIJRvHb8mKHYfREnEsF4qHSiQrMRbMzFqZ1jJg6wDRtuzYpiei6CYUe757zMt0Q-OS0RukHGMsaDj9OIWgwCNmI6tU7vNw3tNoq)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVnRzta6vNXK1Ba1P80UMUH2SoNZSp6JjMcm1wMu_o8Im13gW5GweX9x0mBTj-VB_OMjtCv3HA1mlGdgSnxgTh18zqQTg8P6bpATLjqHrbyFyKhjR9)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8yirA81BqsDhE5bjkfxvGZbpP9iqZlQlNHTNn0ObbtT3Tyk-HIz8PIXXK2Gz22iSGZAZo6VuP4ihmOd8vvVpT72ckFaOzt7OIe1EtSA112JaNwWjp)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGj46eBFl-fDnasgk4dVCItyXyipIhji3zcgPibLp1o2geXue8tDQXGxoiqViRqtjnQ6TWueDOc-DbOv750l039dlboezlnL9sYl8h7L1xXovcd4tSl)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEL_49S2yyfE42n3ArOsKVhUVsaV_LIPtC42TzYUF5gQ5HIMKehlBFLGenqdfHKMXTUuQTbqCGKtdVee6hUNjxQulgnwoSV682EeeY79h_KcvceThiYZ-X63sGwI5ucN9VnNKGF1PtfLF_qznTGhRrS_pqRA0htKIXRZYAp1IUQRhGuOg0txQ70HIiYqiEfhDiW6eX_aOi5wxV7cWxQjwys33X2feJOrifRgvKC-QbhV396vxoyoE2i4Rcm0jHOP5RsNZ_s2m4nxiXdkPKTcKC_w4q1HXd0OehBln_njQKlrC3o)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0BAIe1yhnmipaEUJLhl7OJw-KeVcKsnWdVrBJNBIqTVJ5pRokRx-D22gZnOpzeLQJV_zsmkrzIUp0945M-G6VKA31y0jieDECvkHBvLDT52PqzIH_)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPIzmwkIyCNN6KtSwCOjHrUuVmM1CWhdsYoZnVYlrA3lDAuwjYl35Fzn7C2FhMrlcwIrwgRtXDYs7b9ODhSY_BtcMgo9c4VTtqARoG_wBZQ-rmAqLt)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdnltObz4xuQWovmRBUcCDjFOBhb-dsHMSbRY0vAbASwJPBOVYgy1AqxW8zdteVC0mJVBWj67VadAlkpLIYot1CKQ_LfT-bEZDNRY9yWTFjc6rNdLw)
20. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmouR5oE5KTYnX7habK4vuDQgcmXPY84HMbRrIyNJz5lrxx8sK3XsIzzGZmajC8NotzyOT7Z_9eroxAy6qlY-RzTl7nyX9lchO6qcoSJrHBMfdh3pzF1td5Ny7N6v0E-o=)
21. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFg0DM83l8up42L2_0ViLnxIJJKBQ_k6wiOpOvpbO32legXWJFS2TvAS6Uesbhq3V6YGbtBFgwmnj13osbIC8pr6_2DtPxEYKNZs62kan6rCx8CSLet_5ztWE4NyIHbNOEDLWJNGI4JcL1LY4kJr4ENdjj47Yj5W4l6bhXdzvDDEHU4IJEnvA==)
22. [temple.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEXh6uIqUiwZhzE2_Tkm1_2eWIvCJ18ATr502y8RqO2g2YUPTknzBmxlNOEDGdnDLwXpSxYuJez-zN0UQ_8jUEj8FZl87BN73dIYhsO_qWVMtssdpgqxb0IsxWSeYr40qlG_JL9lMpw9Y=)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaBioRcVt1UtJGNhQj4f0uYNUS0vsSGWsFzGECbPLH6dyPkFwNj6qwiDFepuj5-So0LbbxHLhWJbr4pN5RF5XUNncPdbzOyCra1qiIGMgY9Aw-FFih)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDL8_FUD9c58TCDNTEAUkQdCd8evJX4zua2zf-utYBY0MKmG7nKEKymymEA-r0-gdXMfOZgyJ5RTO8sweB4PeXzCrw6uDF6DbwDpTIwQ3WQF_E2_2W)
25. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHi_h0twMlmdd77XjOuaKQQfJJ9lxqjrk0R3lJY2scgp5UrgbJF4V6zpf1uKhILnW9hSiqJDDtTJAOdtE3ytyWgyt5YiIZNKWMhZ6VxirvJ5IbfhvoWDA==)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEL5LZJNNAz_BH66szCcVZw4wMiiS0FHDTwzlars2FxoCdDmOh6DFI0bXqwoZSFPKf7Vbjgzh_rxzTsxh8H90TjlOzkVb_OUwkwJ6ML7DQgGPPC5evB67h2P6oTcEOqpe0FHxTm88KbtsnSBb-xXiwyu5YaDSq1z28s5ULxf2d0CH3h)
27. [union.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJ7-i-j7DBoAGjJXtC0OZ47Ck4uCCW5BWPiy6X_toYFLu2isx0pFp36j_BLVKtr9htWkMqbGSqPlBFHmH-DlGgxZgKA2nfP_oFSq_4bxZM3YaUy7kQEuryyjVKQ0J-BsXBaYiSyB0=)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE72u4YfJsqu-d5Wacbu84ObuDRO8vDReBIHPG_ACNlUMzddffUTe-LCgJokO8GFGCSH1542WibiVM8isaB9wdO72oaXWIGHpLsVQKqK7Hvgicj9WZ9)
29. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuUyZqFdqnouY9x76vrBIcmgCkUehz0u4zjeN6xIUwa6OrQUTspuEkwLiFBv9g8IlKtNA10Z2RcgZlNv83Aow7CLFL9Y0u_aDT40WfGKbRlLF5JEgPMPSvm0A2injCzZQtXxT9PjBDLYvi208Ro7CWsxtsmHJc6xF1cFuKdyE4MsrMi74_bF57hhrS_PNGvTlEt-mEktLskQJKpLhQrk_NmNEtVv0zvzaFfxzk2gWkzy2Q47cPqlHt3ngJvimEpG-nEn2A2jiXzTDokexJos2TBwr7zTbz_2gW0keXYXDcjW6f5eGIMLjf9KPkuSFiIDr3LYv__eBbz-eP_0ktcA8CHeULlPDqKBAaRxqiMybmjxVHR7_41_I5D6KCmuD4SoUh_MwQ2Mdb-bhc8cJNhSx1iw==)
30. [researcher.life](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvxllQ8PETw7AffXn0PXkMF7CcVSxaXh2m5Hm9AkO7HnAf32kaLe39mg0Np7-ZVdmZI58vU8PUoEAA1VxEKfsiggYncmqEnn051EPpD4vSaE0MvFnmeDkmkxwSMhJ7qKrdcPzTyrhWAm625O1fGA1jDeMW7N2yX9nQlVWujI4B6x69tSBbivC6O8Hl-Dm1eZenePCV3WrHaJUfhLxiTFpICD3L1FLEq4DCSpy0HkBrzpK0c_UIeO6_lA==)
31. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaErQN8yVuU4WyB7i184ot2Z8sH1fGvTjS4zOTrmUnNRQOzlk6OO_ginaFxDaFAR1o4K5criF_KofEwaYWTmnnnWSwAAIXXAmFVgpPAwnGZSLK_rC1HJcfOiwiECCAhb5vwAL_KecOh_Vw8USs9A5H3cvPQhCOylYeWMrwH6m4Sj1WO1EFRZD_yZo_eKAmeo0dubxc9taaTg4TRmKsGTihSTe16iC1JNvNQTg1OgB_DQew4B29WMiWzhzFsJppi6kMe9OdUUtp12I_lW0nEs5JRiWYYcAzkg_MF4UPDMZW_kDZ0FR-VpHP5OCbe2jJM32itKXf-AbKiZJbCrD3w4qGxgka2LKstHhMmH3VPX1tH4MCCTtY)
32. [westlake.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH26tYrPhsdIeZTAdiZ37Tnj8G12zfqZeqmeZosjsnzMXMbb2fFaXHTdVqS7D2cAYeiBzOMb0c02ZipNC3A1EqjbpwybSMgo4tHuf_P_RuVarmlaYysfchx7wFi2MeKH3Pi57Q=)

