# Classicality theorems for overconvergent modular forms 2024-2026

**Pythia queue id:** 192
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChczVUFQYXVHckwtYVNfdU1QM05PTHFBYxIXM1VBUGF1R3JMLWFTX3VNUDNOT0xxQWM
**Elapsed:** 251s
**Completed at:** 2026-05-21T17:33:13.997720+00:00

---

# Classicality Theorems for Overconvergent Modular Forms (2024-2026)

The study of \(p\)-adic automorphic forms has undergone a profound paradigm shift between 2024 and 2026. A central question in the field of arithmetic geometry is the "classicality problem"—determining under what precise conditions a \(p\)-adic, overconvergent modular form is, in fact, a classical modular form arising from complex algebraic geometry. Historically governed by numerical "small slope" criteria, recent breakthroughs have reframed classicality as a strictly geometric and Galois-theoretic phenomenon, intimately tied to \(p\)-adic Hodge theory and the topological structure of perfectoid Shimura varieties. 

### Key Points
*   **The "De Rham Implies Classicality" Paradigm:** It seems highly likely that traditional slope-based classicality criteria are being superseded by Galois-theoretic conditions. Seminal work by Lue Pan demonstrates that an overconvergent eigenform is classical if and only if its associated Galois representation is de Rham at \(p\), effectively resolving long-standing edge cases in weight one and providing a new geometric proof of the Fontaine-Mazur conjecture in irregular cases.
*   **Extension to Higher Rank Groups:** The evidence leans toward the universal applicability of these new classicality frameworks across higher-rank Shimura varieties. Extensions of Pan's D-module localization techniques to \(\mathrm{GSp}_4\) have directly enabled new modularity lifting theorems for abelian surfaces over \(\mathbb{Q}\).
*   **Higher Coleman Theory and Cohomological Degrees:** Research suggests that overconvergent forms must be understood not just in degree zero, but across all coherent cohomological degrees. "Nearly overconvergent" modular forms and higher Coleman theory have matured, interpolating Gauss-Manin connections and allowing the construction of \(p\)-adic L-functions in non-ordinary settings.
*   **Perfectoid Geometry as a Unifying Tool:** The use of the Hodge-Tate period map on infinite-level perfectoid Shimura varieties has become the standard mechanism for constructing overconvergent modular sheaves, leading to new results in partially classical Hilbert modular forms and beyond.

---

## 1. Introduction: The Classicality Problem in $p$-adic Automorphic Forms

Classical modular forms are holomorphic functions on the complex upper half-plane exhibiting extraordinary symmetry under arithmetic groups. The transition to the \(p\)-adic setting, pioneered by Serre and Katz, and vastly generalized by R. Coleman, introduced the notion of **overconvergent modular forms**. These are \(p\)-adic analytic functions defined on a strict neighborhood of the ordinary locus within the rigid analytic generic fiber of a modular curve [cite: 1, 2]. Overconvergent modular forms naturally occur in \(p\)-adic families, parameterized by rigid analytic spaces known as **eigenvarieties** or the Coleman-Mazur eigencurve [cite: 1, 2].

The fundamental difficulty in the overconvergent theory is that the space of overconvergent modular forms is infinite-dimensional, whereas the space of classical modular forms of a fixed weight and level is finite-dimensional. Therefore, while every classical modular form (of level \(p\)) is overconvergent, the converse is spectacularly false. The **classicality problem** asks: *When is an overconvergent eigenform for the Hecke operators actually classical?*

Coleman's foundational classicality theorem established a "small slope" criterion: if an overconvergent modular form of weight \(k\) is an eigenform for the \(U_p\) operator with eigenvalue \(a_p\), and if the \(p\)-adic valuation (slope) \(v_p(a_p) < k - 1\), then the form is classical [cite: 3, 4]. However, this numerical criterion fails or becomes extraordinarily complex at the boundary (e.g., when the slope equals \(k-1\), or in weight \(k=1\), where the slope is necessarily \(0\)). 

Between 2024 and 2026, the landscape of the classicality problem was completely rewritten. Leveraging the geometry of perfectoid Shimura varieties, the completed cohomology of Emerton, and the theory of \(D\)-modules on partial flag varieties, mathematicians have successfully removed the reliance on slope bounds in favor of deep geometric and representation-theoretic conditions [cite: 5, 6].

---

## 2. Completed Cohomology and the Work of Lue Pan

The most significant catalyst in the modern theory of classicality is the work of Lue Pan, published in the *Annals of Mathematics* in 2026 under the title "On locally analytic vectors of the completed cohomology of modular curves II" [cite: 7, 8]. Pan's work provides a totally new geometric interpretation of classicality, establishing a profound link between overconvergent modular forms and the \(p\)-adic Hodge theory of Galois representations [cite: 5].

### 2.1 The Framework of Completed Cohomology
Emerton introduced \(p\)-adically completed cohomology as a surrogate for a space of \(p\)-adic automorphic forms [cite: 3, 5]. For modular curves \(Y_{K^p K_p}\), the completed cohomology is defined by taking the inverse limit over powers of \(p\), and the direct limit over all finite levels at \(p\):
\[ \tilde{H}^i(K^p) := \varprojlim_{n} \varinjlim_{K_p \subset \mathrm{GL}_2(\mathbb{Q}_p)} H^i(Y_{K^p K_p}(\mathbb{C}), \mathbb{Z}/p^n) \]
This space admits commuting actions of the absolute Galois group \(G_{\mathbb{Q}} = \mathrm{Gal}(\overline{\mathbb{Q}}/\mathbb{Q})\), the prime-to-\(p\) Hecke algebra \(\mathbb{T}\), and crucially, a continuous action of the \(p\)-adic Lie group \(\mathrm{GL}_2(\mathbb{Q}_p)\) [cite: 5].

The challenge was to identify the locally analytic vectors \(\tilde{H}^i(K^p)^{\mathrm{la}}\) within this massive Banach space. Pan's breakthrough relies on passing to the infinite-level modular curve \(\mathcal{X}_{K^p}\), which Peter Scholze proved is a perfectoid space [cite: 5, 9]. On this perfectoid space, the relative Hodge-Tate filtration induces the **Hodge-Tate period morphism**:
\[ \pi_{HT}: \mathcal{X}_{K^p} \to \mathscr{F}\ell \cong \mathbb{P}^1 \]
where \(\mathscr{F}\ell\) is the adic space associated to the flag variety of \(\mathrm{GL}_2/\mathbb{C}_p\) [cite: 5, 9].

### 2.2 D-modules and Beilinson-Bernstein Localization
Pan's methodology imports the complex analytic machinery of \(D\)-modules and the Beilinson-Bernstein localization theorem into the \(p\)-adic realm [cite: 6]. By analyzing the locally analytic sheaves on the flag variety \(\mathscr{F}\ell\) and pulling them back via \(\pi_{HT}\), Pan characterized the action of the Lie algebra \(\mathfrak{gl}_2(\mathbb{Q}_p)\) on completed cohomology [cite: 10, 11]. 

Specifically, Pan determines the eigenvectors of a rational Borel subalgebra of \(\mathfrak{gl}_2(\mathbb{Q}_p)\) acting on the locally analytic vectors [cite: 7, 11]. He establishes an exact sequence relating completed cohomology to the spaces of overconvergent modular forms [cite: 5, 12]. If \(\omega^k\) is the sheaf of modular forms of weight \(k\), Pan connects the \(p\)-adic Hodge-Tate-Sen weights of the Galois representations directly to the classicality obstruction space [cite: 5, 10].

### 2.3 The "De Rham Implies Classicality" Theorem
The ultimate triumph of Pan's second Annals paper (2026) is the reproval and vast generalization of Emerton's classicality result [cite: 13]. Pan proves that any absolutely irreducible two-dimensional Galois representation that is regular de Rham at \(p\) and appears in the completed cohomology of modular curves must come from a classical eigenform [cite: 13]. 

For weight one forms, which are inherently irregular (Hodge-Tate weights \(0, 0\)), classicality cannot be detected by slope [cite: 14]. Pan's theorem successfully proves classicality for overconvergent eigenforms of weight 1 based purely on their locally analytic vectors and their Galois representation being de Rham [cite: 11, 15]. Furthermore, this provided a new geometric proof of the Fontaine-Mazur conjecture in the irregular case under mild hypotheses: if an overconvergent eigenform of weight \(k\) has a corresponding Galois representation with Hodge-Tate-Sen weights \(0, k-1\), it dictates the classicality of the form [cite: 10, 11, 15].

In 2024, Gyujin Oh further utilized Pan's geometric interpretation of the classicality of weight one overconvergent modular forms to construct derived diamond actions on weight one modular forms, formulating a \(p\)-adic analogue of the Harris-Venkatesh conjecture [cite: 12]. The obstruction to classicality acts as a \(p\)-adic analogue of taking complex conjugation on modular forms [cite: 12].

---

## 3. The Theta-Fontaine Equivalence (Jiang 2024-2026)

Building on Pan's framework, Yuanyang Jiang achieved a major refinement published in the *Journal de l'École polytechnique* (2026) titled "Theta operator equals Fontaine operator on modular curves" [cite: 16, 17]. 

### 3.1 The Theta Operator and the Obstruction Space
For an overconvergent modular form \(f\) of weight \(1+k\) (with \(k \ge 1\)), there is a well-known differential operator, the Atkin-Serre \(\theta\) operator, which acts on \(p\)-adic modular forms and shifts the weight [cite: 18, 19]. The obstruction to an overconvergent form being classical usually lies in the image of certain differential operators acting on forms of lower weight. 

Jiang investigated the connection between the \(\theta^k\) operator and the **Fontaine operator** (from \(p\)-adic Hodge theory) [cite: 18, 19]. Let \(\rho_f : G_{\mathbb{Q}} \to \mathrm{GL}_2(\overline{\mathbb{Q}}_p)\) be the global Galois representation associated with an overconvergent modular eigenform \(f\) of weight \(1+k\). Assuming \(\rho_f\) is irreducible, Jiang proves that \(f\) is classical if and only if \(\rho_f\) is de Rham at \(p\) [cite: 18, 19]. 

### 3.2 Method of Proof
Jiang's approach clarifies the relationship between the completed cohomology and overconvergent modular forms without restricting to the finite slope or ordinary parts [cite: 9]. By proving that the theta operator \(\theta^k\) literally coincides with the Fontaine operator in a suitable category of \(D\)-modules and sheaves on the perfectoid modular curve, Jiang demonstrated that the condition of the Galois representation being de Rham (which forces the Fontaine operator to act trivially in a specific sense) perfectly eliminates the obstruction to classicality [cite: 18, 19]. 

This provides a drastically simplified, purely geometric proof of classicality compared to the analytic continuation techniques previously used by Buzzard, Taylor, Kassaei, and Pilloni [cite: 19, 20]. Jiang has also recently extended this methodology to Hilbert modular forms (arXiv:2605.18426), proving similar classicality theorems for regular parallel weights [cite: 16, 21].

---

## 4. Modularity of Abelian Surfaces: Generalizing to $\mathrm{GSp}_4$

While Pan and Jiang resolved the geometry of classicality for \(\mathrm{GL}_2\) (elliptic modular curves), a monumental achievement in 2025 was the extension of these techniques to higher rank groups, specifically \(\mathrm{GSp}_4\) (Siegel modular threefolds) [cite: 22, 23]. This was the primary driver behind the Boxer-Calegari-Gee-Pilloni (BCGP) proof of the modularity of abelian surfaces [cite: 4, 6].

### 4.1 The Paramodular Conjecture and Abelian Surfaces
The Hasse-Weil conjecture and the Langlands program predict that every abelian surface \(A\) over \(\mathbb{Q}\) is modular, meaning its \(L\)-function \(L(s, A)\) coincides with the \(L\)-function of a cuspidal automorphic representation \(\pi\) of \(\mathrm{GSp}_4/\mathbb{Q}\) [cite: 4]. If an abelian surface is modular, the associated Siegel modular form must be of weight 2, because the Galois representation attached to an abelian surface has Hodge-Tate weights \((0, 0, 1, 1)\) [cite: 4].

Weight \(k=2\) for \(\mathrm{GSp}_4\) is an **irregular weight** [cite: 4]. In general, a weight \(k \ge 2\) Siegel modular eigenform has Hodge-Tate weights \(0, k-2, k-1, 2k-3\), which are pairwise distinct if \(k > 2\) (regular), but overlap at \(k=2\) [cite: 4]. As in the case of weight 1 for \(\mathrm{GL}_2\), the irregular weight poses immense analytic difficulties because classicality theorems based on slope (in the style of Coleman) are insufficient [cite: 4, 24].

### 4.2 The 2-3 Switch and Residual Modularity
To prove modularity, BCGP employ a "2-3 switch" mechanism [cite: 24]. The outline of their strategy is:
1.  **Residual Modularity at \(p=3\):** They find a finite extension \(F'/\mathbb{Q}\) and a genus two curve \(X/\mathbb{Q}\) whose Jacobian \(B = \mathrm{Jac}(X)\) shares the mod 3 Galois representation with the target abelian surface \(A\), while having a mod 2 representation that is induced from a 2-dimensional representation and is thus known to be modular [cite: 4, 25].
2.  **Modularity in Weight 3:** By switching primes, they prove residual modularity in weight 3. Weight 3 is regular (Hodge-Tate weights \(0, 1, 2, 3\)), so standard classicality results and Taylor-Wiles lifting techniques apply [cite: 4, 24]. 
3.  **Changing Weight and Classicality in Weight 2:** Once modularity is known in weight 3, the representation is \(p\)-adically modular and belongs to a Hida/Coleman family. They then specialize to weight 2 to hit the abelian surface. [cite: 4, 24].

### 4.3 Rodríguez Camargo's Extension of Pan's Theory
The final, crucial step in the BCGP proof relies heavily on a new classicality criterion for weight 2 ordinary Siegel \(p\)-adic modular forms [cite: 4, 24]. To achieve this, Juan Esteban Rodríguez Camargo successfully generalized a massive portion of Lue Pan's \(\mathrm{GL}_2\) D-module and completed cohomology work to \(\mathrm{GSp}_4\) [cite: 4, 5, 24]. 

As discussed extensively in the 2025 ARGOS seminar in Bonn (led by Scholze and Rodríguez Camargo) [cite: 6, 23], this involved building the category of \((\mathfrak{g}, G)\)-equivariant sheaves on partial flag varieties, tracking the horizontal action of the Lie algebroids \(\mathfrak{n}_0, \mathfrak{p}_0, \mathfrak{m}_0\), and applying Beilinson-Bernstein localization functors on Siegel threefolds of infinite level [cite: 6]. By analyzing the locally analytic completed cohomology of \(\mathrm{GSp}_4\), Rodríguez Camargo established that a \(p\)-adic Siegel eigenform in the irregular weight 2 whose Galois representation satisfies the appropriate de Rham conditions (like the one coming from an abelian surface) is strictly classical [cite: 4, 6].

This yielded the definitive classicality theorem:
**Theorem (BCGP 2025):** *Let \(f \in H^0(Sh_{K^p}, \omega^{(2,2;2)})^{ord}\) be an ordinary overconvergent Siegel modular eigenform with Galois representation \(\rho_f\). If \(\rho_f\) is de Rham with Hodge-Tate weights \((0,0,1,1)\), then \(f\) is classical.* [cite: 4, 24]

This breakthrough finalized the modularity theorem for a vast class of abelian surfaces over \(\mathbb{Q}\) [cite: 4].

---

## 5. Higher Coleman Theory and Nearly Overconvergent Forms

While completed cohomology handles classicality via Galois representations, the internal geometry of the eigenvarieties themselves has been expanded to non-ordinary, finite-slope settings in higher cohomological degrees. This is termed **Higher Coleman Theory**, as pioneered by Boxer and Pilloni [cite: 3, 26].

### 5.1 The Need for Higher Degrees
Historically, Coleman's theory only applied to the \(H^0\) of the modular sheaf \(\omega^k\) [cite: 1, 12]. However, when associating a Shimura variety to a reductive group \(G\) (like \(\mathrm{GSp}_4\) or unitary groups), classical automorphic forms often appear in the coherent cohomology of automorphic vector bundles in degrees \(i > 0\) [cite: 1, 27]. Boxer and Pilloni developed local cohomology techniques to study the finite slope part of the coherent cohomology of Shimura varieties, creating spectral sequences (like the Cousin spectral sequence) from local cohomologies to classical cohomology to obtain vanishing and classicality results [cite: 6, 26].

In 2026, Boxer and Pilloni published refined slope classicality theorems for modular curves of arbitrary level. By utilizing completed cohomology classes attached to overconvergent modular forms, they constructed an embedding of the obstruction space for classicality (in either cohomological degree 0 or 1) into a unitary representation of \(\mathrm{GL}_2(\mathbb{Q}_p)\). Unitarity forces the slope of the \(U_p\) double coset operator to vanish, yielding classicality [cite: 3].

### 5.2 Nearly Overconvergent Modular Forms (2024-2025)
Another vector of massive progress in 2024-2025 was the geometric interpolation of the Gauss-Manin connection and the formalization of **nearly overconvergent modular forms** [cite: 15, 28]. 

Classical nearly holomorphic modular forms contain powers of the non-holomorphic term \(1/\mathrm{Im}(z)\). In the \(p\)-adic setting, this corresponds to the unipotent circle action on the space of \(p\)-adic modular forms [cite: 15, 29]. In a 2025 paper, Graham, Pilloni, and Rodrigues Jacinto provided an optimal geometric definition of the space of nearly overconvergent modular forms \(\mathscr{N}^\dagger\), defining it as the space of overconvergent functions on the closure of the Igusa tower inside the analytic de Rham period space \(\mathscr{P}_{\mathrm{dR}}^{\mathrm{an}}\) [cite: 28, 29]. 

This space was designed to possess a robust spectral theory for the \(U_p\) operator (allowing the definition of \(\le h\)-slope parts) while permitting the full \(p\)-adic interpolation of the Gauss-Manin connection, removing restrictive analyticity assumptions from earlier work by Andreatta and Iovita [cite: 28, 29]. 

### 5.3 Applications to p-adic L-functions
The development of nearly overconvergent forms in higher degrees was the missing ingredient for constructing \(p\)-adic \(L\)-functions in highly non-ordinary settings [cite: 27]. 
*   **The \(\mathrm{GSp}_4 \times \mathrm{GL}_2 \times \mathrm{GL}_2\) Trilogy:** In November 2024, researchers successfully constructed four-variable \(p\)-adic \(L\)-functions for the spin Galois representation of a Siegel modular form of genus 2 twisted by cuspidal modular forms varying in Coleman families [cite: 27]. This required working with cohomology classes in higher degrees of the Siegel threefold and interpolating Maass-Shimura differential operators using the nearly overconvergent sheaves [cite: 27].
*   **Asai L-functions:** In April 2025, a nearly-overconvergent version of higher Coleman theory for Hilbert modular surfaces was deployed to study the \(p\)-adic interpolation of critical values of the Asai (twisted tensor product) \(L\)-function for Hilbert modular eigenforms over real quadratic fields [cite: 30].

---

## 6. Hilbert Modular Forms: Perfectoid Approaches and Partial Classicality

The classicality problem for Hilbert modular forms (over totally real fields \(F\)) introduces additional subtleties because there are multiple primes \(\mathfrak{p}_i\) dividing \(p\). In 2024-2025, Mladen Dimitrov and Chi-Yun Hsu developed the theory of **partially classical Hilbert modular forms** [cite: 2, 31, 32].

### 6.1 Perfectoid Infinite Level Constructions
Dimitrov, Hsu, and others [cite: 33] provided a purely analytic construction of \(p\)-adic overconvergent Hilbert modular forms utilizing Scholze's perfectoid Shimura varieties at infinite level. By applying the Hodge-Tate period map, they gave a definition that closely resembles complex Hilbert modular forms—as holomorphic functions satisfying transformation properties under congruence subgroups [cite: 33]. 

This approach proved that classical Hilbert modular forms of integral weights are overconvergent in this new geometric sense, and showed that the resulting spaces are isomorphic as Hecke modules to the earlier cohomological constructions of Andreatta, Iovita, and Pilloni [cite: 32, 33].

### 6.2 Partial Classicality and the Eigenvariety
In their 2025 paper "Eigenvariety for partially classical Hilbert modular forms", Dimitrov and Hsu formalized that for each subset of primes in \(F\) above \(p\), there exists a corresponding space of partially classical forms [cite: 2, 32]. 
*   If the set is empty, one recovers fully overconvergent forms.
*   If the set is all primes above \(p\), one yields fully classical forms.

They proved a partial classicality theorem using analytic continuation methods: when the slope of the \(U_{\mathfrak{p}}\) eigenvalue is small compared to the subset of weights corresponding to the chosen primes, an overconvergent form is guaranteed to be partially classical in those directions [cite: 32, 34]. They constructed the corresponding equidimensional eigenvarieties, successfully \(p\)-adically interpolating the classical modular sheaves over weight spaces of maximal dimension [cite: 2, 32]. 

Parallel to this, in 2024 Yichao Tian achieved cohomological proofs of the classicality of overconvergent Hilbert modular forms by analyzing the global geometry of Goren-Oort strata on Hilbert modular varieties over finite fields, ultimately applying these insights to the Tate conjecture and the Beilinson-Bloch-Kato conjecture [cite: 35].

---

## 7. Synthesis and Outlook (2026)

The period spanning 2024 to 2026 marks a watershed era in the theory of \(p\)-adic automorphic forms. The geometric reinterpretation of classicality—shifting from rigid bounds on Hecke eigenvalues (slopes) to profound statements about the de Rham nature of associated Galois representations—has resolved decades-old roadblocks. 

Lue Pan's integration of Beilinson-Bernstein localization with Peter Scholze's perfectoid Shimura varieties [cite: 5, 6, 9] provided the absolute baseline. Yuanyang Jiang refined this mechanism into an explicit equivalence between the Atkin-Serre theta operator and the Fontaine operator [cite: 18, 19]. Almost immediately, the community, led by figures like Rodríguez Camargo and the BCGP collaboration, scaled these tools from \(\mathrm{GL}_2\) up to \(\mathrm{GSp}_4\), culminating in the historic proof of the modularity of abelian surfaces [cite: 4, 24].

Simultaneously, the perfection of Higher Coleman Theory and the formal geometric definition of nearly overconvergent modular forms [cite: 3, 26, 28, 29] unlocked the ability to build multivariable \(p\)-adic \(L\)-functions in finite-slope, non-ordinary settings across complex topological signatures (such as unitary and Siegel threefolds) [cite: 27, 30].

As of 2026, classicality theorems for overconvergent modular forms are no longer just analytic technicalities; they represent a fundamental, geometric bridge connecting the \(p\)-adic Langlands correspondence, locally analytic representation theory, and the arithmetic of Shimura varieties [cite: 5, 11].

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYzp2gK0q6BrkjLP1SQ7cBgueqSnpjdhz74zWuQasaE2S-sLssRPk3IVKmNKJ0RrgaeqfXt6nMzji1K6Elvgn9EYnNzSIyn7HKFcP8II0DJJAbZnsG)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQxA-V1yTTjSKWWR17VBQH8Y6_Vwi3FADq4DUKx2Q2l0_SqwBtWVjMrqSa5sH0T-nLwaOS-tee1_YA_nCGtajyU6yTseaSKJ0QtcW2oo9cr37mLkcd)
3. [pnas.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtObs8OyuL9C88L8y8KDi2VEc4bZVR9HyqezOOsfjh1kv2apc1qSi9b_fRvz2A1kC1cqiJzPNCVcF8KByl96FOcNPYoFNNo_b2RtAUA-4Ca39ijh4RPUl9G0iF9FRxiK-PsJV8Yg==)
4. [imperial.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFoL3gzKihn-uKiIDd3GElrMwF6-w1Zl9Z6GWbVNq3HxJafqG1GYcQ2QJgFWCwozPQqf7EubtZm6TXS3qGZ0HfuTTgsyN3DmzFnhdg6hRAf2hwvbhnRmbdbRIfatIP_62UrODuheG_wzCPBmhyhSPw=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhT1_nwyf59vujbzytc6wZaLiReGNYCAFxMYpm-_E8zOSMWlNWHOPcH6dZepNOIH3Y84i2139-AOmG6mQZlv8Ibqn_KYVdUsJjSHJZL851edzCk_sy)
6. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhmRr1i2yRZ0a7j6HEI9YkkuY2BER5NvMw58ox02JNjWFbZDU81bttfHfOhDl9R1ZjzU9xad8BldmCNLcqdrMqRJzkp2PJtdBn04EJI70ePCj89u54S7Vcd68OaSnz-z8tRIMQ8zT6DeOycYtBbui0YQ==)
7. [researcher.life](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYFaviQnTMBoU-PsXj8BIlmFNz1F1dsHwJBc57-AsxrkymHkwt5lGE_zPbiPeazdT7vAKEqtp7Gmzk8J49igxl5pTZ7gTOdJvAm1isGjaaL9D69Gxtd6t0B5HnPI4qajjrdo9sSlfZXMad2MLzPhdb8ku3ICWNRA2ypTjHvPAgNF9qgXDTh1ZfKu-ciwbdExb9YdvdagKTB-bNtJ0VCbbWu-g7GBYC06-DWCnvkGGyKip1RFJmmgg3m2WiDtS94kRhTuXThlxsGiKz_Opc)
8. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLjXaZQt0_seGfXP8rBptHY5F3BwrZ8nRkotG96O8NGPAHaYDD6aEMyEdK8pEm_z56CLWnKskDBz9p7KKc5xfi91F_yTc-UHKrJXgoDlP2cLi3WI0jNTOR3WzNwycEep9I)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmgFrNj5aqvJ2USidxUUlJgAGaypeMnSs7vTLaATsv6p4GLb68hywnfnYVDSLTF3OWx-JZMv7wTRGFfrxLcFVTZi3qEFMwdvZOsKrtzQ1XgrChRSVBrQ==)
10. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_gVloipYwgWaH53Oc6RS4ecVRk8jTmFeO5kR0PBRp8-7Mdl1dPB8TpRj-sy4PRPjFlh4CaKcSccMgrI8oT83mB1BRpxStSSVw_jQIGe5bUvJyde9yWKTfztuMbCuAlWTsbZadqpnnBSFxqm649uVmD0b44UswTInw6KcKT54rmvh4planY3JFpsaMeOum-k7_WQ==)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE79UNicn23zSTszhdsT7OIAP4ovwOsKNX_8kMDZ1hK_e1TON5u-PAkxurExggQuW4USTQjdcXjYlTYWyfmK4onofXKfMZwnNZ3bRPwaq4WkFy9T8rkRbWiPYKJucXm_ZfNwHxfGg6yS3CVARhd4HV6oyAINY-YiS5VYs6OcIIa5moGqMi2nqglDeO8VBCTIWy0VDj9n3RmfNBCNwDZiOtSPVfZSoG087jU5kZVsV8GpMLrgXmj6eCamoHcwJiPdA==)
12. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbqhz-ilCXdDJsH7FozEkfad3FXQsAn6C3NSPJAvo7gtmbdc1QpAjusE4inkrhsGs_LsoaPq0p-IMEJCAF1NfLsp92G4FpM5t_wKzTRCYmBKKyLs6n6dR6quaMDB9FfmZ6dm7mvb7OPX_gAo6V)
13. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9TEt1ffDi_kG3h-WDGw6mT73go8nqvidd5Fg7lKK9zamYihfwqt1-DbMMSPaet1NsRXI934KNv7QOSGO6Ga_oHHGKKZCGJxpIxOx-gcCKUhZ__vop2oaBgrHXeGOPVJZ2dot37fcsGTAa-mNkxUNa4De9iM4JPJsI3PgHOjKEJNUFvHXNZqxIiX8=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF06rHLfEE3Iy9cTuD0akECWFs__TZPtMRClhBVwwKvQ6mGVuXY6vHl4z4gW39FSkTmnOaI5t0-88x8Hh3DJX9X_31ogqR5OV3XZzLzTKNOFveQYyU7tTgq)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfeWfSUwWyvSl3M8iJPcdyKgdhzZEniCMG3vFpMFfxtt5Ah38SKojGrwpdcrq4wFprC88xTaMr5M2w9n2DlKVjuCOoddJ0PKc3pytEWzbXE7AEewS-xvHOmHptRMnHs93VZ7KCfYEUAiuHs2ypn0qE-S4pA3_4ybmtw-wNTEqXbMtx4wo=)
16. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCZKq-DhD1evzcycWCBEoKN3vAmNo6CDcRXCFq2IQFBga-oWkiUgk8USFo6N_2xGHfuygSVcxnzqimWGzcO1DiYWKZ7N4NE9kcA3LWg3bOsQEuygp3s-QvekUV-csdhD5Ch-QJvM6EQu49)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGiF9jB5g3bYsfSSGzUaOACWQMvLpZQpqtoOEK7ZDepNQHA8QJyTlxxmwR1Flr-5bniLSTycZ6c6OM3R2DUKNovHqYlCOcmn5p6n-yr4V0NTx5tpFF5SwFMLr6dnmUjKLItgOlJrlAEtowFlOhM24u3dEkQEhHtYQYRWmePZtadyoyaQH26k3IIrcEl8ZYyYrsoOqCVKstj-pWZfFCCOxW1NA==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3SQKlpVHph3PgLhFkT8z8wd1piTk8INrFgJrcuwKKt89NHf-wcO88k9He8XtQdQRNmQGxZKU1mnbBvTK9racgG-RkNj6Senl0xsJcS3091sQzs5KA)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEErM6w3386xHv3kj7bpG2jv7bY95XByqemrndhBUzms7KRUeMbEbglNfmjdmUbY1MxmjQKdUyV3WpkXToojMhekBJtBFs0_Pmi4G98lyorWooIVe6j)
20. [univ-paris13.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERyxhrbV9aOSl7tKC_r5dlGUUVcywNHJ5u1n7xDDPgtsYleyucCmDQKSb0olzhvpor8AYxtj5Lf0f8s_sE8Ad-YxPkQOJfY7EW7YX5HxnG5JCNp9pdSXTuQ_WXz6dyXQ6uDYmHviKIKobAYIxap1sgPHC3Wan398hIkSJC5aPzYmIXL3oxmx09cgBr8fOTtTMg9ng=)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFOs03RqFpx_BHMZrp6LOJuLQ3oT08Yqa1S2ktw2d6SpQ20oKm3IYvUHQp0KWd7a9qVaz-cJOjQ92yKPTnJvs9ta0TjX5cE-49hSPw1YAcN2QAZaS2i3HG)
22. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNqZViMZqk4dOp1p4Nb_IShOisBXb3JzdpccrlIMR4yLU_b-PPtgUrioVZhoNtoSV84_BfkZSk2bbEML10gBmM0AzdDkckGGEB1VcgFhBaoWP-BzMOmluVqMb2gB0AehxEdk4es5DsF_Y=)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZUMMwVzrmxPu7OLKbmgWdi9yU4mGOw4h2KJOAsdhIjMzie4C8zZ2ZUaj8wBeXUAWpUSCDoLa9Hud1gTwrXPp-8cKR-cOOAH0GW5gfnU1WiOjJsuxD)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTrp6ZBGxKpfvY-IW2cxNCkSApmzkKouyqXLXE1Iq7rMk61wZWGbYuYGHAvHBWpAp3aIYw_j5kkiFIZx3Pzv78qybOHHOl8SnSKg6_8nhaEeC6YGL3O0taINm5o0s_PoQFbgwHfnm_heQ9KqlQlSIluDe0rqOS0bbwYeujlT0OyVS_aOXyfh1l2NZKgGyznoM=)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5apx5gScU_Ujg3GkGBpl69rQ4Wtslj_sO0Go8IcDcw_icTxbfg4Zrx4M1plm1-I604DoKm52bHlaJLWXEoMszJjzW5o0Tp5S_ewoM90lEE8AjpZbqMXay)
26. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFqVt5PHZ77MpJw0pC8ZElbUEaB4LaaceHmdfeolw_7pA2xHHSXWM1ThInlwaLr9F7COMa75QXqc_4SGm3iUKG5YsuvA3BU7LReSebMrfQRdQ6cpgCTzqeTsB91u25FU1uu2eoDF1IdetXaxDMlRkxo7I2cQWyZXC_a3aQg24LKuOJAA==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLUy3TvzfLRi2Fc2oZySLDAd_OsrOxxagYWHQ-0GiuwDr7p4GIp8JHxNqr4YatKASiQrLfmSZJKNNq452He3o8O_NsANP2-Klo9ucBEo8J4KUIBBBF)
28. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFS4lur3MnCAArnLHAiLGwombvhFWTjaAzpxqJwlbXpW8sIGb3zgCfuMgki44cXbSUYFosckeIzNV69yXZ80a9y5KTlG7n1CyuAgDFqTocNtxS7zpAMkVKY9HtSej77SgElpiH0lKGpnO0Vd1KiHM2DcyKQmKR_7nof4c53DF4J6w-DWdsgWhH2)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERVjAg1YS62W9VPiGotpEVNxJrlizH8rpSERHrciU36edQtkPWhF74zhJPMBXRo2jrwX7EnACEU_TnrTbbt4P_mJl8vMIFkCY3peQNtMxIVZ1V_-hn)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTmTxwKC6UA9cnY-xbdNZUePtFyahWm-_LK7mC4YpQ9jGkNUtToqcEqlF3Q12CCy36YVVIbRAwFz5bOs1aYJG-eRn7uj7S5vjrJAedY5BVtRrwnv1s)
31. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpelmVVzYjljYxqRG61wZ9HhtuKpkrlWgbdSKPn6dG6tXVHRLqpVer4XxR6Kd_Crv0a43DTdghfbJp6AXpnSNcYyXVlMrfuFnkjZ6_MTVo6erkMJGE8n3ULfFrarSJ7c9zrHWsSQ==)
32. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkOffaeSGa22gP2dCfMJNJlDGxVnVpZ-Hw9T5yivdU10oB8nnX4JUG43vrqFCmMp2DvzVAGwYsVT_5Mc-JlOIr_ZGRPdTiFlYsPjJbVAYAxXMpQV4-N9GIxwa4qT4vlDVYvft_oo_vsaibkA8cp7DNdB86OssIMfL7uO-tDXdx22gXlnxFy_ANf64arG_NXIMYE1TC4KLfvETaE1EkAgqDoVc=)
33. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkknXq_wP9uN9kRq_oy_ZuF_mrY7fiBIW8PYA4xKtvdzzN5-jPa-Cns0eFWPcEuy_ODrZR1exsuu70vfYXyc28ZILXZKFLF_aNTVVuysOZC-a150EZP4x0IQqjlIAXiNwu2RB4fSNFqeHJMtJsXBk=)
34. [osu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkv9Md1UiEUmA17mSeUNxXXYpv1ynN7Q_sVJLfflagEp6ZnFMaFPqDwaavF7E4pOmzcTlR2TpLflMPd-h4MWS4p75BQnPtx5lRnKy-wBD5xYFDhaUPaouMvCQ4C8Vn-Mc=)
35. [cas.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHV5e7Dhn1LxIWnw9oXvTZeucm4lSN59W-e6pm3TnGIBSmFEHg5YlTxWxZrVhzj7x5BBMa_mpAlfGKhKPy2fDNeTrKgN9P70ZjKhRvaioQa5kosQjj-VZyLLeFEVtbqL1ff3dWMnDZrbSHAHTDM7SsVsq6aO2NSwI3dM7WvmxA=)

