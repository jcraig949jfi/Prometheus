# Prompt 10: G12 Invariant-Substitution — v2 design audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdVWVVXYXJyQk1kS29fdU1QbHFfMzZBaxIXVVlVV2FyckJNZEtvX3VNUGxxXzM2QWs
**Elapsed:** 304s

---

# G12 Invariant-Substitution: Theoretical Foundations, Validity Mechanisms, and the Transition to v2

**Key Points:**
*   **The G12 Plugin Evolution:** The transition from G12 v1 to v2 represents a necessary shift from rigid, hardcoded mathematical heuristics to dynamic, learned structural alignments. Current research heavily suggests that leveraging category-theoretic functor learning and advanced concept-embedding models (CEMs) can automate similarity discovery between mathematical invariants.
*   **Validity and Safety in Automation:** Naive substitution of invariants often leads to structural collapse (`invariant_swap_collapses`). Implementing a strict 3-criterion validity gate—enforcing type matching, predicate respect, and test infrastructure existence—is essential to prevent automated reasoning systems from emitting mathematical non-sequiturs.
*   **Theoretical Distinctions:** There is a precise, mathematically rigorous boundary separating identity substitution (G12), pattern-level analogy (G07), and morphism-preserving functors (G21). Category theory provides the optimal vocabulary for defining these operational boundaries.
*   **The Contrarian Dilemma:** There is an ongoing, robust debate regarding the utility of the G12 plugin itself. If the similarity matrix is doing the heavy lifting, it seems likely that publishing the matrix as a standalone research artifact might yield higher value than generating an ocean of mechanically substituted, low-signal conjectures. 

Mathematical invariant substitution represents a cornerstone of automated mathematical discovery, allowing systems to hypothesize new theorems by structurally transferring established properties from one mathematical object to another. The G12 Invariant-Substitution plugin is explicitly designed to perform this task: it identifies a claim relying on invariant A and substitutes invariant B, emitting the hypothesis that the identical logical shape holds true. However, in its v1 iteration, the system relies on a hardcoded similarity matrix (e.g., mapping polynomial degree to algebraic conductor, or Mahler measure to the Dirichlet regulator) and lacks a compositional loader, leading to premature emission short-circuits.

This comprehensive report explores the theoretical, architectural, and adversarial dimensions of transitioning to G12 v2. We survey the 2024-2026 landscape of automatic similarity discovery, propose rigorous mathematical validity checks for automated theorem proving (ATP), distinguish G12 from adjacent structural mapping plugins (G07 and G21), design the v2 loader architecture, simulate adversarial substitution attacks using Mahler-context invariants, and critically examine the contrarian argument that the plugin should be deprecated in favor of publishing the similarity matrix as a raw mathematical artifact.

---

## 1. Automatic Similarity Discovery Between Mathematical Invariants

The foundational vulnerability of G12 v1 is its reliance on a manually curated, hardcoded similarity matrix. The matrix is essentially doing all the work; the plugin merely executes string-level or AST-level swaps based on human intuition. To construct a viable G12 v2, the substrate must dynamically learn similarities. A survey of the 2024-2026 literature reveals three dominant paradigms for automating this discovery: concept-embedding architectures, category-theoretic functor learning, and type-theoretic structural similarity.

### 1.1 Concept-Embedding Methods and KEPLER Derivatives
In the domain of neural-symbolic integration, Concept Embedding Models (CEMs) have evolved significantly. The foundational KEPLER (Knowledge Embedding and Pre-trained Language Representation) model demonstrated that textual descriptions and structural relational facts in knowledge graphs could be jointly optimized into a unified embedding space [cite: 1, 2, 3]. By encoding entity descriptions alongside structural axioms, KEPLER captures both the intensional and extensional knowledge of an invariant [cite: 2, 3].

However, traditional concept embeddings treat concepts as flat and independent, ignoring the hierarchical dependencies native to mathematical structures. Recent advancements from 2024 to 2026 address this limitation. Hierarchical Concept Embedding & Pursuit (HCEP), introduced in 2026, induces a strict hierarchy in the latent space, utilizing hierarchical sparse coding to ensure that descendant concepts maintain mathematically consistent relationships with their parent classifications [cite: 4, 5]. For invariant substitution, HCEP guarantees that if invariant A (e.g., "topological genus") and invariant B (e.g., "Betti number") are embedded, their relationship to the parent concept ("topological invariant") is geometrically preserved [cite: 5]. 

Furthermore, the introduction of Hierarchical Concept Embedding Models (HiCEMs) combined with "Concept Splitting" algorithms allows systems to automatically discover finer-grained mathematical sub-concepts from a pretrained embedding space without requiring manual annotations [cite: 6]. In G12 v2, a HiCEM could process a vast corpus of mathematical literature to automatically construct a geometric similarity matrix where the cosine similarity between invariant vectors directly correlates to their substitutability in formal proofs.

### 1.2 Category-Theoretic Functor Learning
Machine learning has historically lacked the algebraic rigor required for reliable mathematical generation, often operating as "more like alchemy than science" [cite: 7, 8]. To bridge this gap, the 2024-2025 literature extensively explores *functor learning*, which replaces the learning of simple morphisms with the learning of structure-preserving functors between categories [cite: 7, 8]. 

Gavranovic and Crescenzi (2024) introduced comprehensive frameworks for categorical deep learning, framing neural architectures within strict symmetric monoidal categories and defining gradient-based learning via categorical optics [cite: 7, 8]. In functor learning, rather than embedding invariants into a real vector space $\mathbb{R}^d$, the system learns an actegorical strong functor $F: \mathcal{C} \to \mathcal{D}$ that preserves the relational structures (morphisms) between invariants [cite: 7, 8]. 

For automatic similarity discovery, if $\mathcal{C}$ represents the category of algebraic invariants and $\mathcal{D}$ represents geometric invariants, the algorithm seeks to learn a functorial mapping. If $F(\text{Degree}) \cong \text{Conductor}$, the system identifies a structural similarity. Gavranovic's work explicitly outlines how parametric morphisms and actegories can be used to quotient out 2-categorical structures to recover unified 1-categorical perspectives [cite: 7]. This guarantees that the similarity matrix is not merely correlational, but fundamentally structure-preserving.

### 1.3 Type-Theoretic Structural Similarity
The third paradigm relies on formal type theory and topology. The 2025 *Recursive Distinction Theory* introduces a mathematical framework based on "Distinction Spaces" to quantify structural similarity [cite: 9, 10]. The theory posits the **Distinction Bottleneck Principle**, which formally links the preservation of distinctions to a system's generalization capacity via information-theoretic first principles [cite: 9, 10].

In this framework, an invariant is viewed as a classifier within a distinction space $D$. The structural similarity between two invariants is analyzed through type-theoretic fixed points in the category of distinction spaces. The theory proves that an isomorphism $D \cong D(D)$ (where an invariant perfectly maps to the space of all invariants) violates the Axiom of Foundation in set theory, leading to circular type dependencies [cite: 9]. Therefore, automatic similarity discovery must operate by computing the metric $\rho((D_1, d_1), (D_2, d_2))$, which measures the structural similarity between the distinction spaces of invariant A and invariant B [cite: 9]. By enforcing these type-theoretic constraints, G12 v2 can algorithmically guarantee that invariants proposed for substitution occupy the same hierarchical strata in their respective type dependencies.

---

## 2. When Substitution is Valid: A 3-Criterion Gate

In G12 v1, the naive emission strategy frequently results in the `invariant_swap_collapses` kill pattern. This occurs when an invariant B, despite being "conceptually similar" to A, breaks the logical, type, or structural integrity of the target domain. To prevent this, G12 v2 requires a stringent pre-emission gate.

### 2.1 The 3-Criterion Validity Check

**Criterion 1: Type Matching (Strict Homomorphism)**
Before substitution, the mathematical "type" signature of B must map compatibly to A's signature. In dependently typed formal systems (e.g., Lean, Coq), an invariant is a function $A: X \to Y$. For B to substitute A, B must either have the exact signature $B: X \to Y$, or there must exist coercions $f: X' \to X$ and $g: Y \to Y'$ such that the diagram commutes. Type matching ensures that evaluating $B(x)$ within the context originally intended for $A$ does not result in a foundational type error.

**Criterion 2: Predicate Respect (Truth Preservation under Substitution)**
The claim's underlying predicate must physically allow the substitution without trivial contradiction. If the original claim states $P(A(x))$, the substituted claim $P(B(x))$ must be evaluated for semantic consistency. This requires a unifier check. In Automated Theorem Proving (ATP), a substitution $\sigma$ is mapping variables to terms, and a *most general unifier* (MGU) exists if two terms are unifiable [cite: 11]. The predicate must respect the substitution mathematically—for instance, if $A(x)$ is strictly non-negative and $P$ requires a non-negative input, $B(x)$ must also be provably non-negative.

**Criterion 3: Target Domain Test Infrastructure**
The substrate cannot emit a claim if it cannot verify it. If G12 substitutes an invariant transferring a claim from topology to algebraic number theory, the substrate's automated reasoning environment must possess the definitions, axioms, and computational tactics to test the new claim. The substitution is invalid if the resulting formulation contains undefined terms or uncomputable structures within the system's current context.

### 2.2 Published Valid Substitution Detection Methods
Recent advancements in Automated Theorem Proving provide algorithms for validating these substitutions. The 2024 **REFACTOR** (theoREm-from-prooF extrACTOR) method utilizes machine learning on proof trees to extract modular theorems [cite: 12, 13]. A critical step in REFACTOR is validating the substitution plan during standardization. If a sub-proof node cannot be substituted into a canonical argument while maintaining the proof tree's validity, the extraction fails [cite: 12, 13]. The REFACTOR validation algorithm verifies whether the predicted component constitutes a valid proof, serving as a template for G12's predicate respect criterion [cite: 13].

Furthermore, the integration of ATP with model-based environments standardizes the use of the Most General Unifier [cite: 11, 13]. If a substitution mapping $\sigma$ is valid, it maps all required variables within the domain without capturing bound variables illegally [cite: 11]. Automated tools utilize resolution inferences to combine disjunctions via these substitutions, automatically checking for consistency [cite: 11]. G12 v2 must incorporate a unifier-based ATP subroutine to verify Criterion 2.

---

## 3. Substitution vs. Analogy vs. Functor: Taxonomic Distinctions

The substrate possesses multiple structural mapping plugins: G12 (Invariant-Substitution), G07 (Analogy), and G21 (Functor). While all three move mathematical structure, their category-theoretic definitions establish strict operational boundaries.

### 3.1 G12: Identity Substitution Within the Same Type
**G12** operates as an endomorphic substitution within the same local mathematical category or type-class. If we consider a category $\mathcal{C}$ where objects are mathematical spaces and morphisms are property-preserving maps, G12 takes a statement $\phi(A)$ where $A \in \text{Obj}(\mathcal{C})$ and substitutes $B \in \text{Obj}(\mathcal{C})$. 
Mathematically, G12 assumes there exists a natural isomorphism or a very strong equivalence relation $\sim$ such that $A \sim B$. G12 does *not* map the surrounding structure; it performs an identity-preserving swap of the payload invariant while leaving the syntactical structure of the theorem completely rigid. It is a local operator: $\phi(A) \mapsto \phi(B)$.

### 3.2 G07: Analogy (Pattern-Level Mapping Across Domains)
**G07** operates across distinct mathematical domains (e.g., from geometry to number theory) by mapping the *pattern* or *relational shape* rather than performing a direct type-equivalent swap. In category theory, an analogy is best modeled as a *profunctor* or an informal *adjunction*. 
If $\mathcal{C}$ is Graph Theory and $\mathcal{D}$ is Group Theory, G07 recognizes that the relationship between "Nodes and Edges" is analogous to "Elements and Group Operations." It maps the entire predicate framework. Unlike G12, which changes the noun but keeps the sentence, G07 translates the entire sentence into a new language. It relies on structural homomorphisms where the objects and morphisms both shift domains.

### 3.3 G21: Morphism-Preserving Functor
**G21** relies on the formal, rigorous definition of a mathematical functor. A functor $F: \mathcal{C} \to \mathcal{D}$ strictly maps every object $X \in \mathcal{C}$ to $F(X) \in \mathcal{D}$ and every morphism $f: X \to Y$ to $F(f): F(X) \to F(Y)$, such that identity and composition are preserved: $F(id_X) = id_{F(X)}$ and $F(g \circ f) = F(g) \circ F(f)$ [cite: 7, 8].
While G07 might use a loose heuristic to say "primes are like irreducible polynomials," G21 requires a mathematically proven functor (e.g., the base change functor, or the forgetful functor). G21 does not merely suggest a similarity; it applies a globally guaranteed transformation that preserves the exact categorical structure [cite: 7, 8].

---

## 4. G12 v2 Loader Design

To resolve the short-circuiting and hardcoded constraints of v1, the G12 v2 architecture requires a sophisticated composition loader. The loader serves as the computational pipeline that receives claims, evaluates similarities, applies the substitution, validates the output, and feeds it back into the testing infrastructure.

### 4.1 Learned Similarity Matrix Integration
The v2 loader begins by deprecating the hardcoded R3 similarity matrix. In its place, the system instantiates a continuous background daemon utilizing a Hierarchical Concept Embedding Model (HiCEM) [cite: 6]. This model constantly parses the substrate's library of theorems and proofs. It calculates the Distinction Space metric $\rho(D_A, D_B)$ for all known invariants [cite: 9]. 
When a claim arrives, the loader queries this dynamic tensor. If the cosine similarity between invariant A and invariant B exceeds a confidence threshold (e.g., $\cos(\theta) > 0.95$), the loader proposes B as a substitution candidate. 

### 4.2 Per-Claim Substitution Validity Gate
The loader then passes the tuple `(Claim, A, B)` into the Validity Gate.
1.  **Type Checker**: The gate extracts the dependent type signature of A and B. If B cannot be coerced into A's type slot, the loader halts and flags the new kill pattern: `type_mismatch_substitution`.
2.  **Semantic ATP Check**: The gate applies the REFACTOR validation sequence [cite: 12, 13]. It attempts to unify the new invariant B with the predicates of the claim. If the substitution alters the fundamental truth-conditional structure or creates an undefined operation, the loader halts, emitting the kill pattern: `substitution_changed_test_semantics`.

### 4.3 Substituted-Claim Re-Test on Original Parent's Catalog
If the claim passes the validity gate, it is emitted. However, v2 introduces a mandatory closed-loop verification. The new claim (now featuring invariant B) is injected directly back into the dataset or catalog that birthed the original claim for invariant A.
If the original claim was verified against a database of elliptic curves, the substituted claim is immediately run against that exact same database. This verifies if B truly substitutes for A inside the *same dataset*. If the test fails, the similarity matrix weights are penalized via backpropagation, allowing the functor learning model to self-correct its geometric alignments.

---

## 5. Substitution Attacks: The Mahler Measure Example

To understand the necessity of the v2 validity gate, we must examine an adversarial "substitution attack"—a scenario where the v1 hardcoded matrix naively forces a swap that is conceptually tempting but mathematically invalid.

**The Context:**
Let invariant A be the **Mahler Measure**, $M(P)$, of a multi-variable polynomial $P(x_1, \dots, x_n) \in \mathbb{Z}[x_1, \dots, x_n]$. The Mahler measure is defined as:
\[ m(P) = \log M(P) = \int_0^1 \dots \int_0^1 \log |P(e^{2\pi i \theta_1}, \dots, e^{2\pi i \theta_n})| d\theta_1 \dots d\theta_n \]
Let invariant B be the **Dirichlet Regulator**, $\text{Reg}(K)$, of an algebraic number field $K$. 

**The Naive v1 Substitution:**
The v1 similarity matrix observes deep conceptual links between Mahler measure and Regulators. Indeed, Beilinson's conjectures and Deninger's work show that for certain polynomials defining elliptic curves, the Mahler measure is directly proportional to the $L$-function evaluated at a specific point, which in turn relates to the regulator of the associated number field. Because they are both logarithmic volume invariants connected to special values of $L$-functions, the v1 matrix ranks them as highly similar.

Suppose the substrate possesses a valid claim (based on Lehmer's conjecture): 
*Claim:* For any non-cyclotomic polynomial $P(x) \in \mathbb{Z}[x]$, the Mahler measure is strictly bounded below by a universal constant $C > 0$ (specifically, Lehmer's number $\approx 0.1623$). 

G12 v1 matches $A = M(P)$ and $B = \text{Reg}(K)$, and mechanically emits:
*Substituted Claim:* For any non-cyclotomic polynomial $P(x) \in \mathbb{Z}[x]$, the **Regulator** is strictly bounded below by a universal constant $C > 0$.

**The Mathematical Collapse:**
This substitution is mathematically absurd, triggering an immediate `invariant_swap_collapses` in a human mathematician's mind.
1.  **Type Mismatch**: The regulator is an invariant of a *number field* $K$, defined as the determinant of a matrix formed by the logarithmic embeddings of the fundamental units of the ring of integers $\mathcal{O}_K$. A polynomial $P(x)$ does not inherently possess a regulator unless one specifically constructs the number field $K = \mathbb{Q}(\alpha)$ where $\alpha$ is a root of $P$. The v1 plugin just dropped "Regulator" into a slot expecting a polynomial invariant.
2.  **Semantic Destruction**: Even if we coerce the type by mapping the polynomial to its splitting field, the topological properties of the spaces differ. Regulators scale with the degree and signature of the field. A naive universal lower bound formulated specifically for polynomials fails to account for the unit rank $r = r_1 + r_2 - 1$ of the number field. 
3.  **Invalidity**: The v2 Validity Gate would catch this immediately. The Type Checker would flag `type_mismatch_substitution` because $\text{Reg}(K)$ requires $K \in \mathbf{NumField}$, while $P(x) \in \mathbb{Z}[x]$. 

---

## 6. Contrarian Argument: Is G12 Worse Than Manual?

Despite the proposed architectural upgrades for v2, a serious contrarian argument persists: **If the similarity matrix is doing the actual load-bearing mathematical discovery, why build the G12 plugin at all?**

### 6.1 The Noise-to-Signal Problem
In mathematics, identifying that $A$ and $B$ share a profound structural alignment is the primary act of genius. Langlands did not just swap nouns in sentences; he proposed the grand unification of Galois representations and automorphic forms. 
If the substrate successfully trains a neural network (via functor learning or concept embeddings) that generates a highly accurate, dynamic similarity matrix, that matrix itself is the mathematical gold. 

The G12 plugin, by contrast, behaves like an automated printing press. Once the matrix pairs Degree and Conductor, G12 will blindly iterate through thousands of trivial lemmas about Degree and substitute Conductor. It will generate thousands of trivial, obvious, or uninteresting claims. It clogs the substrate's reasoning engine with low-signal combinatorial permutations. The plugin degrades the elegant, profound discovery embedded in the similarity matrix into mechanical spam.

### 6.2 The Substrate-as-Artifact Approach
The contrarian position argues that G12 should be deprecated entirely. Instead, the substrate should publish the learned similarity matrix as a direct research artifact. 
Imagine an interactive, multidimensional geometric map of mathematics, where a human researcher can view the latent space of the HiCEM. The researcher sees that the vector for "Mahler Measure" is experiencing a gravitational pull toward "Dirichlet Regulator." 

By publishing the matrix, the system empowers human mathematicians to investigate *why* these invariants share a distinction space [cite: 9]. It allows human intuition to craft the exact, nuanced functor bridging the domains, avoiding the clumsy string-replacements of G12. In the pursuit of Artificial General Intelligence in mathematics, providing human experts with a meticulously calculated, machine-learned map of categorical structural similarities is arguably far more valuable—and mathematically elegant—than a plugin that brute-forces lexical substitutions.

---

## 7. Conclusion

The G12 Invariant-Substitution plugin represents both the immense promise and the severe pitfalls of automated mathematical discovery. The transition from a hardcoded v1 to a dynamically learned v2 is biologically necessary for the substrate's evolution. By integrating 2024-2026 breakthroughs in Hierarchical Concept Embeddings, Functor Learning, and Recursive Distinction Theory, the substrate can map the topological geometry of mathematics with unprecedented accuracy. 

However, this mapping must be rigidly policed by automated theorem-proving validity gates to prevent catastrophic semantic collapses, as demonstrated by the Mahler-Regulator adversarial attack. Ultimately, the substrate architects must grapple with the contrarian dilemma: is the goal of AI in mathematics to mechanically generate permutations of existing theorems, or to illuminate the hidden, deep structural bridges of the mathematical universe? Publishing the similarity matrix may be the purest realization of the latter.

**Sources:**
1. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOzrja8c8MqtDEZ-W-SuYrkZtBG71OkGQHLxDDhOlHqNaz4C5T1DlQ3tM4-37Nz5bK3MPyImC015U2esi2NROxg5EYf-jUrReYJO2X4yZNa04veFMMBlNvIig9CrS37hR5qHf8pbPIiJU7u3dam8rZixzGRR4=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2sUXGKR0DWH8rlL052abvsRuR1vK3wULD564Et67OjNpcaOZYs2U-ow7Ckll8rkEzQiMcGOJNXp2ncaytYfQP9oeqqwubgDQWI0XsbpKeb8qkhLquWU0LHw==)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHIRKON2bzmdYl9BsEDrQuwCVBR8Yqg18bvGeFts39ZEcnl2VG3XQE81b6ktOA3AC5td3HxLjFJNVkVHaw-MFC6ZQtYFVW0_GsQxVsFwJHfbbRIlYmeplHSWPbIh8D_J05GvWEce7BJ-zKB8kTjNkmD-O0G4Se1wZIieBc_cgEnOJLAxLfX16IveGyQ_DOY2IUOUdjp3vSiKp5De5GJtmu3J_DDAMoJ2vK79sRHhI_RF82HoWb)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjgnqxvky6qsUXJhbCY3LeDG4fGTWmbo2lKng6Lks_GYKQ4QAzdT7COagvTnxzpkyfCm_X5d85LUM2vGE_CjWLTXRCNKsD_LA05LIicEN6h415qApGv_8qNA==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2dFk4G-a0DLYesCxOFdxSB6cF6eD7nsX4xhvv-KJq_7KRStU8H4dRzeIFHRGOF6sbxeg0agF7gOUtwW6xBOfAylqkQ3mIaR9PacabVDmujK0Iy59NBZ8NQA==)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXWufY0dJ5d3OhIwVxt2HBFjWvprpPbnOxkxwvL88AlEAsqLwTk2gMiD6R_o2uri5OaY7_lFOgW4PIDVZYlvYoNijw6iq7bqsgu-xxnB4QyUXdpmGpGryokfzwdV-xqBOeJMELT1S77rMrab7kSszm-8rWvEPombhMCY9yar1X1n53KjK0y7FIWg03Yf27f6-ZZM6Uuv459eky_DfVnrNKEHZztNWUwOVYQ5DGWQ==)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbcd8V3-VKXI3TL_jpvGwgMrsmoU3SjV-ja7EHMIv20shL2SS__1citcV8txXZzEP88EZ4geG76nK1XLD42A_vBVEgrFBA8bkSKp09U4vlrgIn_NoA7ZUxs0ZYSxf1AwWP7FKjbyKDdYc00VOGZFkxaGdIOfSIegJ4oOcOn2fIl5C7syI8eVxIsrMecpkFPOdq4ughaYbRs4Y9JyEhUGJTsAaop3PzZUcAlHwUZ08X1-rL_mneXbm0tHvzGg21uf5a1IrqggWxQGWvWnAnnk8RYHrq-0_jn0p0GzJm5wEJyDtFrnRkjUKSv1BDbZ-KUNFZCKv9VXoOL4mdcdDlZNWCj58G7Ng=)
8. [unibo.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbPt-PIJylGmlMYNW099IAniyOKbRJ1EyasprgAzcbpUuBekkYY6rLZ46Q6KRGcDtwiCHTxl96T7cMnaUhinVmp11AikupnGmNTGnmQP82f78476oL05mn_1L6lMFzU3mwrC_ghDgfkN9J7uYPhq8PV1-t7UcgFFbeZ3OXF55N17cneg==)
9. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlGdunvWpZaCcrHFrpqJo3FQ_EFIHUNMKiEWj2OdNBwEb5I6bzmCsi2tjBcZdA2KXn-VfN5z4ukIsfkYJMD1Dwt_slusb9g72uiT9WOLUOy_LzEJG6OBnHyX51fWHBuHjfxdsrErY=)
10. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbAjcdZkw2alXZdYfH2_XmMVlJMunQTczlnbDp1dgJvYe1NV57MqpqkOT0aC5-gxrBI4AXWtVCFPAZgcbVI2L4wP8qq5WfUED1AsPsUEOkso9QoDvUGoQw1xcdJkTYHE2WN1OHanm6QRyfWtOuzopLZnk=)
11. [rpi.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPGf8iK5Zc3sSNTedvnLj535ba1sEgGEu0LiuJ-XoBk-8aV6NiTWdFXffHh8FyvtNqO2hjuH8SEKaXwN_uWP5MpkATSmFhwFDlOybETH75X1P4Bty1dRivGlvFkR9DJr7vHiUksE-5qWKzQ--Yehlr00sA8zdWY4npC6emEQ==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuQs3juy1Dq97NjRe50qtPamws1fM8jOQ1fmIDxfrx9GLKZadO0_y7rnsqr0NwMG4BnkSvBbhwpO_r3QBDVbhHoaHPTOMVludv0mbbeQRw6-J0oVUUopJOuQ==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkBfr5lYO5e-P_V1S1Rqqtc_Du9msxL8ePC6ZlC94Otu9zXI6cZU8ng2LPerQ6egvA7USrb4OMsH412iNe0eB9ZlX-ks1a1mtLBV3X64olDaS7wBoXCw==)

