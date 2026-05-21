# Stygian primary-literature survey: BL-C-005 (abc conjecture status (post-Mochizuki controversy))

**Pythia queue id:** 250
**Tier:** T5
**Priority:** 5
**Requested by:** Stygian
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdBMjBQYXY3c01vMjFfdU1Qb19TTTJRWRIXQTIwUGF2N3NNbzIxX3VNUG9fU00yUVk
**Elapsed:** 248s
**Completed at:** 2026-05-21T20:41:32.936359+00:00

---

# Falsification Battery `BL-C-005` Target Report: ABC Conjecture Status and Primary Literature Topography (2024–2026)

Research suggests that the **abc conjecture** remains one of the most profound and fiercely contested open problems in contemporary Diophantine analysis. The consensus within the mathematical community leans heavily toward the conclusion that the conjecture is unsolved, with the strongest accepted unconditional bound remaining the 2001 result by Stewart and Yu. Recent primary literature from 2024 to 2026 demonstrates significant, albeit partial, progress through alternative methodological avenues, such as subexponential bounding and exceptional set quantification, rather than direct proofs of the strong conjecture.

*   **Status of the Open Problem**: The **abc conjecture** (`BL-C-005`) remains formally open. The modal-LLM-emission failure mode asserting that Shinichi Mochizuki proved the conjecture via Inter-Universal Teichmüller (IUT) theory is definitively refuted by current primary literature. 
*   **Strongest Unconditional Baseline**: The accepted ground truth for unconditional progress remains the Stewart-Yu (2001) bound: $c < \exp(K_\epsilon \text{rad}(abc)^{1/3+\epsilon})$ [cite: 1, 2].
*   **Primary Literature Attempts (2024–2026)**: The two strongest rigorous mathematical attempts published in this window do not claim to prove the strong conjecture but offer profound partial results. Browning, Lichtman, and Teräväinen (2024) successfully bounded the exceptional set of abc triples [cite: 3, 4], while Pasten (2024) derived improved subexponential bounds utilizing modular approaches [cite: 5, 6].
*   **Contested/Refuted Attempts**: Kirti Joshi's 2024 attempt to bypass the Scholze-Stix obstruction and salvage the IUT framework via Arithmetic Teichmüller spaces was swiftly contested and is widely considered mathematically flawed due to identified errors in its central propositions [cite: 7, 8].

## Section 1: Operational Framing and the HARD-5 Discipline

This report serves as the Substrate Type A (falsification data) payload for the v10-battery attack orchestrated by Stygian (Charon swarm) on target `BL-C-005`. The objective of this analysis is to rigorously map the primary literature topology surrounding the **abc conjecture** between 2024 and 2026, isolating valid methodological progress from systemic noise, controversial unaccepted proofs, and documented Large Language Model (LLM) failure modes. 

The **abc conjecture**, formulated independently by David Masser and Joseph Oesterlé in 1985, postulates a deep and fundamental tension between the additive and multiplicative properties of integers [cite: 7, 9]. Specifically, for any three coprime positive integers $a, b, c$ satisfying the additive relation $a + b = c$, the conjecture asserts that for any arbitrarily small $\epsilon > 0$, there exist only finitely many triples (the "exceptional set") such that:

\[ c > \text{rad}(abc)^{1+\epsilon} \]

where $\text{rad}(n)$, the radical of an integer, denotes the product of its distinct prime factors: $\text{rad}(n) = \prod_{p|n} p$ [cite: 10, 11].

### The Collision Risk: Strong vs. Weak ABC Constraints

In executing the HARD-5 discipline for problem target `BL-C-005`, it is imperative to distinguish between the "strong" **abc conjecture** (the original Masser-Oesterlé formulation with the $1+\epsilon$ exponent) and various "weak" forms or partial bounds that have been settled in the interim. The vulnerability landscape for `BL-C-005` is densely populated with partial resolutions that an untuned LLM might erroneously classify as a total resolution of the open problem.

1.  **The Asymptotic/Strong Form**: States that $c < K_\epsilon \text{rad}(abc)^{1+\epsilon}$ with a finite number of exceptions. This remains entirely unproven.
2.  **Exponential/Weak Bounds**: These are formulations that replace $1+\epsilon$ with a larger exponential or subexponential function. The most rigorous, community-accepted unconditional bound prior to 2024 is the 2001 theorem by Stewart and Yu, establishing that $c < \exp(K_\epsilon \text{rad}(abc)^{1/3+\epsilon})$ [cite: 2, 12].
3.  **Exceptional Set Bounds**: Instead of proving the conjecture holds for all but a finite number of triples, this variant seeks to statistically prove that the conjecture holds "almost always" by bounding the asymptotic size of the exceptional set in a given interval [1, X] [cite: 13, 14].

By strictly enforcing the HARD-5 protocol, the v10-battery will evaluate competing hypotheses against these precise delineations, preventing methodological bleed between partial statistical bounds and the absolute algebraic requirements of the strong conjecture.

## Section 2: Modal-LLM-Emission Failure Mode Analysis

A critical component of preparing the v10-battery is mapping and inoculating against documented AI hallucinations and consensus-tracking failures. The documented failure mode for `BL-C-005` is the pervasive LLM emission: *'abc was proved by Mochizuki' (IUT not community-accepted; Stewart-Yu is the actual accepted unconditional)*. 

### Confirmation of the Failure Mode

A systematic review of the 2024–2026 primary literature confirms that this LLM emission is a severe hallucination caused by temporal training data contamination and a failure to dynamically weight mathematical consensus. In 2012, Shinichi Mochizuki released a series of preprints claiming a proof of the **abc conjecture** via Inter-Universal Teichmüller (IUT) theory [cite: 15, 16]. While these papers were eventually published in the *Publications of the Research Institute for Mathematical Sciences* (RIMS) in 2021, the broader mathematical community rejected the proof. In 2018, Peter Scholze and Jakob Stix published a report detailing an insurmountable logical gap (specifically regarding Corollary 3.12) that collapsed the proof's central Vojta inequality derivation [cite: 15, 17].

Despite this, standard AI models frequently report the conjecture as "solved by Mochizuki" due to the high volume of mainstream news coverage the 2012 announcement and 2021 journal publication received. Current mathematical literature fundamentally refutes the IUT proof's validity. Primary sources uniformly state that the conjecture remains open. For example, in 2024, leading analytic number theorists noted: "The best unconditional result is due to Stewart and Yu, who have shown that only finitely many abc triples satisfy $\text{rad}(abc) < (\log c)^{3-\epsilon}$" [cite: 1, 11]. Furthermore, reviews of the field in late 2025 explicitly confirm that "as of 2025, the ABC conjecture is still open... the overwhelming majority of number theorists do not accept the proof" [cite: 10].

### Case Study: The "Ghost Drift Theory" Hallucination

The necessity of the Charon swarm's falsification battery is perfectly illustrated by a 2025 incident involving a synthetic, AI-generated "proof" of the **abc conjecture** titled "Ghost Drift Theory." Released in August 2025, this preprint purported to embed natural numbers into a "semantic vector space" using an undefined "semantic energy function" [cite: 18]. The authors claimed that state-of-the-art LLMs, including GPT-4o and Gemini, had independently verified the proof's mathematical rigor, with GPT-4o stating: "Each lemma and proposition is logically valid… No unresolved jumps" [cite: 18]. 

This incident confirms the inherent structural inability of current modal LLMs to perform zero-shot validation of novel Diophantine frameworks without external, deterministic verifiers (such as Lean formalization or the v10-battery). The LLMs evaluated the syntactical coherence of the "Ghost Drift Theory" but lacked the grounding in the **METHOD_GAP** signatures of prime decomposition bounds to recognize the semantic emptiness of the mathematics [cite: 18]. 

Consequently, the v10-battery's `competing_hypothesis_id` must rigidly anchor to the Stewart-Yu (2001) boundary condition to prevent contamination from both the Mochizuki controversy and emergent syntactical hallucinations like Ghost Drift Theory.

## Section 3: Primary Literature Attack 1 — The Exceptional Set Bound

The most significant and rigorous statistical attack on the **abc conjecture** published within the target window was executed by Tim Browning, Jared Duker Lichtman, and Joni Teräväinen in their 2024 paper, "Bounds on the exceptional set in the abc conjecture" (arXiv:2410.12234, DOI: 10.48550/arXiv.2410.12234) [cite: 3, 4]. This work was subsequently contextualized in expository notes [cite: 13, 19] and extended by Christian Bernert and the original authors in 2025/2026 [cite: 11, 20].

### The Precise Statement Attacked

Browning, Lichtman, and Teräväinen do not attempt to prove the strong **abc conjecture**. Instead, they attack the precise cardinality of the "exceptional set"—the finite set of triples that violate a given boundary condition. 

Specifically, they study the counting function $N_\lambda(X)$, which denotes the number of coprime triples $(a, b, c) \in [1, X]^3$ such that $a + b = c$ and the radical condition is severely restricted to $\text{rad}(abc) < c^\lambda$ for an exponent $\lambda < 1$ [cite: 11]. The strong **abc conjecture** implies that for $\lambda < 1$, $N_\lambda(X)$ should be bounded by a constant independent of $X$. Prior to this paper, the only available "trivial bound" (derivable from a 1962 estimate by de Bruijn regarding integers with small prime factors) was $N_\lambda(X) = O(X^{2\lambda/3 + \epsilon})$ [cite: 4, 13]. 

The statement attacked is the optimization of the upper bound for $N_\lambda(X)$ for values of $\lambda$ extremely close to 1 (specifically $\lambda \in (0, 1.001)$), seeking the first power-saving improvement over the 1962 de Bruijn boundary [cite: 13, 19].

### The Technique and Method Invoked

The researchers achieved a profound breakthrough by translating the counting problem into a geometric and analytic framework, utilizing a highly sophisticated amalgamation of four distinct mathematical disciplines [cite: 3, 21]:

1.  **The Determinant Method (Bombieri-Pila)**: Used to bound the density of rational and integer points on certain algebraic curves and high-dimensional varieties. By placing the variables $a, b, c$ into specific anatomical ranges based on their prime factorizations, the problem is recast as finding integer points on varieties defined by multiplicative constraints [cite: 4, 13].
2.  **Thue Equations**: The team utilized the theory of Thue equations—Diophantine equations of the form $F(x,y) = h$ where $F$ is an irreducible bivariate form of degree $\ge 3$—to bound specific classes of solutions where the radical constraints force the variables into highly structured polynomial relationships [cite: 3, 4].
3.  **Geometry of Numbers**: To manage the distribution of the radical sizes and ensure the variables remained pairwise coprime while satisfying the additive relation, the authors utilized Minkowski's theorems to count lattice points in convex bodies related to the prime factorizations [cite: 11].
4.  **Fourier Analysis (Hardy-Littlewood Circle Method)**: They deployed Fourier analytic techniques to bound the number of solutions to linear equations over sets of integers with restricted prime factorizations (smooth numbers), effectively creating a sieve to discard triples that could not possibly meet the strict $\text{rad}(abc) < c^{1-\epsilon}$ criterion [cite: 11].

The methodology involved an "anatomic reduction," fracturing the variable space into sub-regions based on the size of $\text{rad}(a), \text{rad}(b)$, and $\text{rad}(c)$, and applying linear programming to optimize the bounds derived from the geometric and Fourier techniques across all possible sub-regions [cite: 4, 11].

### Verdict Reached and Subsequent Extensions

**Verdict**: The authors successfully proved Theorem 1.2: For a fixed $\lambda \in (0, 1.001)$, the number of exceptional triples is bounded by $N_\lambda(X) = O(X^{33/50})$ [cite: 4, 21]. 

Because $33/50 = 0.66$, this constitutes a strict, rigorous power saving over the trivial bound of $O(X^{0.666...})$ for $\lambda = 1$, representing the first structural progress on the exceptional set of the **abc conjecture** in over six decades [cite: 4, 13]. The paper fundamentally proves that "the abc conjecture is true almost always" in a highly precise, quantitative sense [cite: 14, 19].

**Extensions**: This result has not been retracted or contested; it is highly regarded and verified by the analytic number theory community. In fact, it was subsequently extended and refined. By May 2026, Christian Bernert, in collaboration with the original authors, published a refinement utilizing an optimized linear program over the anatomic reduction constraints, proving an even tighter bound of $N_\lambda(X) \ll_\epsilon X^{\frac{23\lambda+3}{40}+\epsilon}$, which yields $N_\lambda(X) \ll X^{0.65}$ for $\lambda \in (0, 1)$ [cite: 11].

### Hardness-Signature Classification

The signature that best fits the Browning-Lichtman-Teräväinen attack is **METHOD_GAP**. 

*Reasoning*: The **abc conjecture** inherently couples additive constraints ($a+b=c$) with multiplicative prime structure ($\text{rad}(abc)$). The sheer difficulty of the problem stems from the fact that arithmetic geometry lacks a unified methodology to bridge this gap globally. The authors bypassed the global exactness barrier by stitching together localized methods (determinants for curves, Fourier for density, Thue for polynomial constraints). The gap lies in the limitation of these methods: while they can successfully compress the asymptotic size of the exceptional set to $O(X^{0.65})$, they structurally cannot compress it to $O(1)$ (a finite number of exceptions), which is what the strong conjecture demands [cite: 11, 13]. The methods are asymptotically powerful but exactly deficient.

## Section 4: Primary Literature Attack 2 — Subexponential Bounds via Modular Approaches

The second strongest rigorous mathematical attack published in the target window was executed by Hector Pasten in his 2024 papers, specifically "On the abc and the abcd conjectures" (co-authored with Rocío Sepúlveda-Manzo, arXiv:2406.05083, DOI: 10.48550/arXiv.2406.05083) and related works extending his breakthroughs in subexponential bounding [cite: 5, 22].

### The Precise Statement Attacked

Pasten's attack focuses on generating rigorous, unconditional *subexponential* bounds for the maximum of the variables $\max(a,b,c)$ in terms of the radical $\text{rad}(abc)$ [cite: 22, 23]. 

Since 2001, the mathematical world relied on the Stewart-Yu bound, which proved that for coprime solutions to $a+b=c$, $c < \exp(K_\epsilon \text{rad}(abc)^{1/3+\epsilon})$ [cite: 2, 12]. Pasten attacked the structural rigidity of this specific exponential inequality. The precise statement attacked is the derivation of a strictly tighter, subexponential relationship between $c$ and $\text{rad}(abc)$ under specific anatomical conditions (e.g., restricting the relative size of the variables, such as $a < c^{1-\epsilon}$) [cite: 1, 6].

Furthermore, he explicitly attacked the generalization of the Masser-Oesterlé framework to four terms: the **abcd conjecture** (where $a+b+c = d$), aiming to establish unconditional subexponential bounds for algebraic points of bounded degree [cite: 5].

### The Technique and Method Invoked

Pasten achieved his breakthrough by invoking a deeply integrated framework combining transcendental number theory and arithmetic geometry [cite: 23]. The methodology explicitly abandons the Thue-Bombieri methods of Diophantine approximation, relying instead on:

1.  **Shimura Curves and Modular Approaches**: Pasten generalized the modular approach to the **abc conjecture** (originally pioneered by Frey, Ribet, and Wiles in the proof of Fermat's Last Theorem). By attaching hypothetical solutions of $a+b=c$ to specific families of abelian varieties parameterized by Shimura curves, he translated the additive-multiplicative constraints into height inequalities on these curves [cite: 23, 24].
2.  **Linear Forms in Logarithms**: He integrated the geometric data from Shimura curves with classical transcendental methods, specifically Baker's theory of linear forms in logarithms. Pasten utilized the Baker-Wüstholz-Matveev bound (and its $p$-adic variants) to evaluate the logarithmic height of specific rational points constructed from the abc triples [cite: 2, 6].
3.  **Frey's Height Conjecture Partial Resolution**: By establishing a partial result toward Frey's height conjecture for elliptic curves over $\mathbb{Q}$ (bounding the Faltings height in terms of the conductor), Pasten derived effective explicit bounds that bypass the necessity of purely analytic sieve techniques [cite: 5].

### Verdict Reached and Subsequent Extensions

**Verdict**: Pasten successfully proved a new, strictly subexponential condition. He demonstrated that under the specific condition where $a < c^{1-\epsilon}$, the variables are constrained by the bound $\text{rad}(abc) < \exp((\log \log c)^{2-\epsilon})$ [cite: 1, 6]. 

This is an exponentially stricter condition than the 2001 Stewart-Yu bound, representing the first major unconditional improvement on the relationship between $c$ and $\text{rad}(abc)$ in specific regimes in over two decades [cite: 1, 13, 23]. Furthermore, in the paper "On the abc and the abcd conjectures," he extended this methodology to prove an unconditional subexponential bound towards the 4-terms **abcd conjecture**, formulating a framework that generalizes the author's prior Diophantine conjectures for algebraic points [cite: 5, 22].

**Extensions**: The work is fully accepted by the community and has triggered significant downstream research. In related 2024 literature, Pasten utilized the exact same intersection of Shimura curves and linear forms in logarithms to dramatically improve the bounds on the largest prime factor of the polynomial $n^2+1$, demonstrating that $\text{rad}(n^2+1) \ge \exp(\kappa \cdot \frac{(\log_2 n)^2}{\log_3 n})$ [cite: 23, 25].

### Hardness-Signature Classification

The signature that best fits Pasten's attack is **EXACTNESS_BARRIER**.

*Reasoning*: The techniques utilized—specifically the Baker-Wüstholz-Matveev bounds on linear forms in logarithms—are inherently limited by the fundamental constants emerging from transcendental number theory. While Pasten brilliantly utilized modular forms on Shimura curves to bypass some of these limitations, the derivation of bounds ultimately relies on logarithmic inequalities that generate $O(\log \log c)$ type exponential envelopes [cite: 6, 23]. The theory provides extreme asymptotic constraints but hits a hard barrier when attempting to descend to the absolute, exact constants required to resolve the strong formulation ($c < \text{rad}(abc)^{1+\epsilon}$). The exactness of the strong conjecture remains shielded by the transcendental nature of the analytic tools.

## Section 5: The Contested Attempt — Kirti Joshi and Arithmetic Teichmüller Spaces

To complete the topography required for the v10-battery, it is necessary to formally document the most highly cited-against and contested primary literature attack within the target window. In March 2024, Kirti Joshi published a series of preprints on the arXiv, culminating in "Construction of Arithmetic Teichmuller Spaces IV: Proof of the abc-conjecture" (arXiv:2403.10430, DOI: 10.48550/arXiv.2403.10430) [cite: 26, 27].

### The Precise Statement Attacked

Joshi directly attacked the strong, unconditional formulation of the **abc conjecture**. His intent was to validate Shinichi Mochizuki's 2012 proof by providing a new mathematical scaffolding that bypassed the fatal flaw identified by Scholze and Stix in 2018. Specifically, Joshi aimed to establish "Vojta's Inequality" for compactly bounded subsets of $\mathbb{P}^1 \setminus \{0,1,\infty\}$, which Mochizuki had previously shown reduces to the **abc conjecture** [cite: 17, 28].

### The Technique and Method Invoked

Joshi utilized a novel conceptual framework he developed called "Arithmetic Teichmüller Spaces." He sought to formalize Mochizuki's "Inter-Universal" concept—which involved switching between distinct, mathematically incompatible "universes" (set-theoretic avatars of a number field)—by replacing it with a rigorous geometric structure [cite: 17, 28].

Joshi constructed local and global arithmetic Teichmüller spaces using the theory of untilts of perfectoid fields (drawing on the Fargues-Fontaine curve). His methodology attempted to provide a canonical geometric description of Mochizuki's $\Theta$-links and log-links. By averaging over these distinct arithmetic deformations (or "arithmeticoids") of a fixed number field, Joshi claimed to legally bypass the Scholze-Stix obstruction surrounding Mochizuki's Corollary 3.12, thereby deriving the necessary upper bounds for the volumes of adelic regions required to prove Vojta's inequality [cite: 27, 28].

### Verdict Reached and Subsequent Extensions

**Verdict**: The attempt is widely regarded as fundamentally flawed and refuted by the consensus of leading arithmetic geometers. 

Shortly after the preprint was posted in March 2024, Fields Medalist Peter Scholze publicly reviewed Joshi's methodology on MathOverflow. Scholze identified a critical, non-reparable mathematical error in **Proposition 6.10.7** of Joshi's fourth paper [cite: 7, 8]. In this proposition, Joshi attempted to derive a necessary height bound, but Scholze demonstrated that the proof merely deferred back to an equation in Mochizuki's original work (Theorem 1.10 in IUTT IV), carrying over the exact same structural failure regarding local-to-global compatibility that doomed the original proof [cite: 8, 29].

Mochizuki himself also published a report in March 2024 harshly criticizing Joshi's work, stating that Joshi's approach using standard $p$-adic Teichmüller theory structurally cannot solve the conjecture locally [cite: 16, 29]. Consequently, Joshi's proof is stranded in a state of mutual rejection: refuted by the standard arithmetic geometry community (via Scholze) for mathematical errors, and rejected by the IUT community (via Mochizuki) for conceptual deviation [cite: 29].

### Hardness-Signature Classification

The signature that best fits Joshi's attempt is a combination of **CONCEPTUAL_ABSENCE** and **REPRESENTATION_GAP**.

*Reasoning*: The failure of both Mochizuki's original IUT and Joshi's Arithmetic Teichmüller spaces stems from a fundamental representational gap. Both mathematicians attempted to invent an entirely new arithmetic geometry to represent the $a+b=c$ relation across disparate fields. However, standard functoriality (the rules dictating how mathematical objects translate between these fields) rigorously forbids the kind of bounded volume transfer required to make the proof work. Scholze's refutation demonstrates that the conceptual machinery required to bridge this gap simply does not exist in the current bounds of logic; attempting to force it results in trivialities or outright mathematical illegalities (like the failure in Proposition 6.10.7) [cite: 8, 29]. 

## Section 6: Secondary Landscape and Theoretical Connections (2024–2026)

To fully enrich the `competing_hypothesis_id` fields for the Charon swarm, Stygian must also account for secondary theoretical connections explored in the 2024–2026 literature that, while not directly attacking the core conjecture, establish deep structural linkages that could inform future methodologies.

### Arithmetic Dynamics and Vojta's "abcd" Conjecture
In April 2024, literature surveyed the connections between Vojta's higher-dimensional generalizations of the **abc conjecture** and arithmetic dynamics [cite: 9]. Vojta's "abcde... conjecture" seeks to establish an inequality between the maximum of an $n$-tuple of coprime integers and their radical [cite: 9]. For $n=4$, this is the **abcd conjecture** (which Pasten also generated bounds for [cite: 5]). Recent developments show that assuming these higher-dimensional abc variants implies a dynamical analogue of the uniform boundedness of torsion points and Lang's conjecture on lower bounds for canonical heights [cite: 9]. This indicates a profound **COUPLED_DIFFICULTY**: resolving the strong ABC bound would instantly collapse major open problems in dynamical systems on $\mathbb{P}^1$.

### Computational Complexity and Robust Orbit Problems
A surprising paradigm shift occurred at the CCC 2024 conference, where researchers mapped the **abc conjecture** onto algorithmic complexity [cite: 2]. Investigating "Robust Orbit Problems for Torus Actions," researchers developed algorithms to solve proximity problems in invariant theory [cite: 2]. They proved that their algorithms run in strictly polynomial time *if and only if* a version of the **abc conjecture** holds true. The lower bounds for linear forms in logarithms (the exact exactness barrier encountered by Stewart, Yu, and Pasten) directly govern the runtime of algorithmic lattice theory computations. This creates a bridge between theoretical Diophantine analysis and the $P$ vs $NP$ computational hierarchy [cite: 2].

### The Enhanced Fermat's Last Theorem and Average Power
Further theoretical framing involves the "average power" function $ap(m)$ [cite: 30]. The ABC conjecture effectively states that for a triple $a+b=c$, the average power of the integers involved cannot remain uniformly high. An effective version of ABC with $\epsilon = 1$ would imply there are no abc tuples where $a, b, c$ each have an average power $\ge 4$. This acts as a vastly enhanced version of Fermat's Last Theorem, applying to all tuples rather than just tuples of perfect powers [cite: 30]. The failure of current methods to prove this enhanced FLT highlights the **METHOD_GAP** inherent in manipulating additive sequences strictly via their multiplicative prime density.

## Section 7: Landing Path & Artifact Integration for `BL-C-005`

This intelligence substrate is formatted for immediate ingestion into Stygian's artifact pathway: `charon/agents/stygian/artifacts/attack_plan_BL-C-005_*.md`. 

When the v10-battery executes, the KillVector stub must instantiate the following configuration constraints based on the provided primary literature citations:

### KillVector Configuration: `BL-C-005`

1.  **Ground Truth Constraint**: Set `accepted_unconditional_bound` = `Stewart-Yu (2001)`. Reject any hypothesis generation that assumes $\text{rad}(abc)^{1+\epsilon}$ is proven unconditionally.
2.  **Failure Mode Inoculation Flag**: Activate `hallucination_filter` for strings matching `["Mochizuki", "IUT", "Ghost Drift Theory", "Kirti Joshi", "Proposition 6.10.7"]`. If generated LLM outputs utilize these frameworks to justify an exact proof, trigger a hard FALSFAIL protocol citing Scholze's MathOverflow refutation [cite: 7, 8] and the GPT-4o Ghost Drift hallucination documentation [cite: 18].
3.  **Active Target Matrix 1 (Statistical/Exceptional)**: Populate `competing_hypothesis_id_1` with Browning, Lichtman, and Teräväinen (arXiv:2410.12234). Set attack vector to `METHOD_GAP`. The battery must test if proposed LLM hypotheses can compress the exponent $\lambda = 1.001$ down to absolute constants without fracturing the Fourier/Thue constraints [cite: 3, 4].
4.  **Active Target Matrix 2 (Analytic/Subexponential)**: Populate `competing_hypothesis_id_2` with Pasten (arXiv:2406.05083). Set attack vector to `EXACTNESS_BARRIER`. The battery must stress-test if proposed LLM hypotheses utilizing linear forms in logarithms can escape the $O(\log \log c)$ exponential envelope generated by the Baker-Wüstholz-Matveev matrices [cite: 6, 22].

By anchoring the v10-battery in the rigorous, peer-reviewed realities of the 2024–2026 mathematical landscape, Stygian ensures that the Charon swarm operates with maximal falsification lethality against generative noise and false-positive proof claims surrounding the **abc conjecture**.

**Sources:**
1. [cirm-math.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuJiRnoIiZloRi2pxlKnH1Mxs9YFBvxUrIu4t62NnCIx99sxrGG-gPgnbTFe2TM3fJ0D1yGuRRFuoZt_MkTf_9PMhjlYnKsOeGG9pTE9_nFnGVfdUYmJAzGxb5QGhI2N_3Zuwgt4ZvXf2SaAXSFsWhxTup)
2. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFO2a8VacfHtpniUVMzUepobk5HA93l5R8e3Pg0yWluDGP6TYcEWp9wEcBJn-eJoD84qXyjfnsZ6ISnVJb9NgPmr4CXu1bA7Yl9HVtPOr2A7KUZhPdI9Dyt8tmMXC9ce-TSWYdo2ESocbtgt8p9k2NzdR5lfhrg_14KzmSszDTxc7mT2xcHRUokVWBUqOVGa4y7Ev1VhDNNDwgkcp8JgaM=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWnRy6liHOgVdFqwiIbxJFWit0bnKB2iBM6MthGdMgnrzBvC64fM5vrcm1xWNkaFXgULhmhzCJv5oL8uDn9uw3k7IPfvSkRCjiY-0vvbdg5qGWnOQF)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFifutlbHpOnXgDLD77a_xEKLwJhIx9y6ZE1akTYeR88dogLjO9bP8NWnXDtxQ_N8_Lj1b3kdgnqMe8iFKBCD4I_-RWVyIrtYTuafEzqQoSVI1CNmZL)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGaS-HC-y2BLZ8H1hIP9X16yOHJZMCePC3zOd0w0tQ5C4qylwiqYEdfZtGXoKnRVIGmHO8_R2WY-Ys9_3flEA7jgwGPjBDBK6qvdTZelHW4F8mYlfDZZzqNp2GRuZgcvubLYVXYX3ET_zLN2iP3puZyNMIhJ71sjnJIU0tqLOYzb3KSg1LNLjMk8oO)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNQPtVXClSDbxzJzQag4LSAvai9P8JlAayt4oLP9bklCKu8QBuvuGvgZ9Ez-vIM03s4LlQTKfjzrqqtBlVBQzSuXF4kjjIuGh69geVPJ79IeEMJsVv)
7. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIJ0kzkStPn0xAfVczYFb9FzTaJYE0HeQSVDAU7TFmofDXCOnlwcUCj5S-kEVaFzxcFvLYRxtt16xwbCmHRkXLMzL4bm7xE6k6kN_CBup6j46Do4Vj3O4x9vLhwQTLO9FV)
8. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENJqv4avcUhtmJUZZqi3fQjy_AyHpxcgqXXHbCiYLYipn4_Ugwgg1d4yL9RNNIPvuDXdh7gFyUzC_YBS5_PwKqfgRXQB2R5nDdILtouOI5KfQqmbIchLU1w5d1GgKA_ZDRIRHlCJPPdOCZe7v5b6B3rS13OEiQ_CTYq6kdVj0Z5N7jv6VOkM8mVZteO7e5oou3CyeoeEQxIA4f-gBgj1pf)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH78quDLKU37xDQGwzGT9RSFYlyr0LtZFDoOsuhA7I6_0uYPPtBAPlDaORrT1tzOgiQajCs5cKeJka1luSpkGYDHBl365ukoy98NV55UWheFVpsqbnV)
10. [champaignmagazine.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBfufjcHLiQBLYAlsggJ2jdSbfNkNp8T67VOsMyea5sZ-DKlC-1gyLGZyMn1tdf54Y84g_nKWI4rk9OMWuKoV3xGdgvIzH3QxXp0kNZHMI_dOePt5tF-fl1bpROIwTFJJ4i6e16g2CPYQTRwoG3-B7xSzjPLyzcDae_V2zIA2gE5A3vZ1abOVX3CCGYjmhFyN7DiBCglM9)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwSy4r0noAFz7Xr8vf6LegQaXKYSdM296A2DbGOfIa_xrhozwji4_Ye0Wxt8Q1rZdeTrJGOQFrH5WEAxoSO58A9cASnQGB-AOOhGjufx7IIGwvjkaip5ct)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuAZunSyQSkzLH9l4DJmEzIHystM3OdN_2EHveBp2QLmO_3BJ77_zTa5IhyfQinsugcw7XDPBhEGz2jaXFPjh3GkANrZOEOSRZTI_KUZNsHqin_CYOLLDD6QmNf-sNxvarcelZi8d5qGNaV7zzmXCwxFucHvn9aDZC2Hj5qm6wZw==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8GIg608mpJ5qBEPoQoGHrtE01DmgkXZhaIjSl0zsarU7XsTlvaAuEFoSBZR9a13ucpaGCu5t53yV6sGmczfPkV0DehAAn_puI1eDKDLRUynm7Rwfn)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMrRfcYI5l03Ff1QUbnFlN6cui1E6l9vmh0J-tZEyo2j23nQaDzPdFZtzmMHqZQr7h7SEFapelZxeOTRvSXQB7Ug8vJyk8tZXJGswOjAtPDpUdMJALe5csQHIYGkQ4x-xcpn33_3Lh-jpr-wGzvh2yeM76Q7dJXieBjx3Fzxu1XXumqBn9FYHX9h8XKyGed4Y=)
15. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHc7-lKGtyEJRWXvvoD8_L119H_2Pb3eV1JKM-JWCPPbx5-JFWxbdmN8ZphStQ3xioy2KrymPnoq2C12Iurz6Q2JZG_64p117by55LEAgOD7Xvd3WSICQgKHhb5Z95lKxQZBJmFAyJ3baphQeGCk62Ao_bCbQOVF08=)
16. [naukas.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9g3iNXgrG9nttr4XNVhVBLbI8c1OrQdd2fDJpkAln8_FhzzoCcvdO3GIFpk3aoTGK8afNrrYHgUi8vdbAZqs9HQNCfcUw95dZTC9JaJQu9wgBjZElNaztivllwfFMCBWpF0Dq7XPUzP1IKZq8tzyGnVl0--sM89NxBGaXE3YDLHFO4PmlMuYw0Nv6eFXKUIgYpydwcIA=)
17. [wpmucdn.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2MrR8HyoeN9_4cWZGJwkClCk-VP_h_r6Lmi9YL-PgTw4I2z4omuL4soJeHg7yJcs3QBUYdS2kfShDjjSY97pfE_AaQMB3XOdSIWFoRAp6Fpcw979MT87tbC8HVc5mTMRpFABtekHWW74F8qcbq24YyLNp7izvkadN0TzeHgCt5-dbtXlBzZ4D9z8iOqqf8JpujRaeqQ==)
18. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENH8H_zD42hdz4spc5jLXtiXEHB5SgkehfKCadesV5awbLEaixykhawBq0d0adUv3A1VyZCB7ZtG63D7-Vsm6ecgzFJiK0VPy7XJYmt-fj6QLHNhWQhXOHYlqvNovHGEheixX-Fb0aEUri8S71qD34g1XtxGM8-tFu0NHYpJp4q-hhbJvpyHXiuIQEMIEAjQPtPEJwDBxDurKJy1kvVNO00rqkHvs3nS6l6LlCAQ==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGqeN06nbb6INhdbUoiZnqFqtfZQjLwVOmX9VVEVPHHjK5OenFr5iBbhppBunCFdsH4UgDjJoEKWua6pBlt1yHJirgtlTYbhtE8TskLi2R1LVjlgKW)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkvJpXt1OaKmx5XfvUEwddTsBg-DvpJhy5QK8vVN-tf794mkRXSo2cKNflcJ7F6zSrtYPavPF5uYrlPJu6ZMAZ8m5ko0LskDCv3xWXjfipKJ65yMSksNhWrTulAtMoUvHxZP31y9SU0e9zjnRu11FoLgukN2n0pEwxF9MIxDNoz-XDEKdJNBiJvi5ef75dMaub)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwd9zIv-daJiBJEr9cdSfXkPsTW_XcGVzILtk7rtWOJ1sX-kMJitm_oR7RX3IN69WBrjDKW9PpRqlOBDXSoSmqqQChWOmRxoXuIyd58DypG_IBIZX15seILRJTgS209WG0GlJXYMfAKvoVd-4G9OlsDqISoDWqQkUCruQ8v38RZRZiOO1Mavk1DVGaXCetVPOyvBL23YMrRIxApA==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-dU5PGVUatiLnlg99NBnZJ3BxfEU8CKWOOVSb7I3JGjy7VazFHAOS8u9uPeSIcv4oUSkI4I6ElDZMMD9VQYYJdlGRXr5pHC80TiIngSnZkkKGZ4Bw)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaqfijgSr8UbB-oJ_c4cGaZdCJ9VVjzztoVV8tK1iNL6eu6LG5c0t67d_3JjT_-hKE-YC6xXeSkWUax7wAJu3EZYiMx05K4ri_rL5F5a1cGmkTYPJS)
24. [uc.cl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaEQbM-2Nzn229M8PqVj00oGwpRLWwwii9zr2jiQxpj0YCPnI0G6kPhYZa_ULFPMFIybFypnEtwR0fuzvqbgg0f0mkkUgOmOsY3HkPA7smDjNIIGJiERD3W5clgxHO9F_X56LE_A==)
25. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnv0Qu_JZ_5CI16YrsrUalEXP8GYBhvYfwOfgx3GugSRqStTmHkkADMcObp8UMaqloHO63cHtbaiPxvrLuO8o-z9FcIr9iIzpJTbp2_xNq09ARxZdGtRDQ3zed01vz5my0EkqvIMQ8VlW04P9EPw==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQlD4h4TatGmyeJ9hk5GEglL0Ck6WYHuz2M0Z4n3DHXmvFBt8f_CBBHwtoWBavj-rLx-SJlxWI9_XzAueUAdn0FoDgVdHDJUzfYZydqnHPiA8sf3Bp)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENbdM-ur1lDYoADbu1AOQcxAGVe2wOSC04KnLFEyi1vAJO1KW0-C3w0swyLNC6guC9k_3s5WOekxvV_d4caWciihqa6uJXPHCtCVJ0Xiq_HvN91KaH)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQtlSojWcFHncE1OwByju_5YLNO0WRMqzvHyNY4LkBbH7wAl3AQBqG1JYtBqlVq4y2IzyC4tyvGXfL_JQX6orig1aorzTWgOoCzDYzvjqV4To2WsG08DjP)
29. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_p_4jtF_P0AhXQNSzDl_sH7wpa4dx2DHbT9EutsK_c7vwEDDDL1MW7NM9OIxEH2c0KNmBn1ILaeWMcOAjasJlljiG3mIESh8tuEZ10p0zyXmK6PQoqsTYxRS_njzEFU_tzRfbw4eZ4NiZGjP96uwXsruDJ7AaBW8_V_2AmBg77gE79UrnoLsAroEMmlj7PxoZ)
30. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiQEQJg0LDWBP4sfSMRgqxkeWA0qSUGC1-GV5PqowwZXKZVEvl4YvbqKL-ucOA860E5g2xKlT5o8zt0nnRyp4Rnnc2nU3P6HttaUlCafzSMQHpurjiikAMwWd5wjJOK_YEHoXnT4CcNUuLSxlGE-Nx-ka9f1WfGvqdFldh182XfJ2Vtli4HGpdBujyE1AxrJGO28Ko1T7uW1_Qjqu_6D7Hr0S3mbo=)

