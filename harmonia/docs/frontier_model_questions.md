# Questions for Frontier Models
## Harmonia Findings — 2026-04-12

Present these findings to Claude, GPT, Gemini, DeepSeek, and Grok independently. Compare answers. Disagreement between models is signal — it marks the boundary of known mathematics.

---

## Category 1: Validation — "Is this known?"

### Q1. The Megethos Axis
> We performed PCA on 47,000 mathematical objects across 18 domains (elliptic curves, modular forms, number fields, genus-2 curves, Maass forms, lattices, space groups, polytopes, materials, knots, OEIS sequences, and more). The first principal component has a 0.995 loading on log(conductor) for L-function domains, log(determinant) for lattices, crossing number for knots, and log(f-vector sum) for polytopes. It explains 17% of all cross-domain variance in the raw feature space, and 44% when restricted to L-function domains. 
>
> Is there prior work identifying a single universal "magnitude" axis across heterogeneous mathematical domains? The closest we found is the Iwaniec-Sarnak analytic conductor (2000), but that only applies to L-functions. Has anyone extended this to knots, polytopes, or materials?

### Q2. The Zero Density Equation
> We measured: n_zeros = 3.117 * log(conductor) + 1.503, R² = 0.976, over 10,000 elliptic curves. This implies our LMFDB data has zeros up to height T ≈ 19.6 on the critical line. The intercept of 1.503 appears to be the gamma factor contribution.
>
> Does this match known explicit formulas for N(T, E) for elliptic curve L-functions? Is the slope 3.117 = T/(2π) consistent with T = 19.6? What is the expected height of zeros in the LMFDB database?

### Q3. Parity Conjecture Agreement
> For 20,000 elliptic curves over Q, we find 100.0% agreement between (-1)^rank and the root number epsilon. Is the parity conjecture now fully proven for all EC/Q, or is this sample just within the proven cases?

---

## Category 2: Challenge — "What could be wrong?"

### Q4. Is Megethos Trivial?
> A skeptic would say: "Of course log(conductor) is the first PC. You put log(conductor) as feature 0 in every L-function domain. PCA found the feature you repeated." 
>
> Fair. But: (a) knots have no conductor — crossing number loads on the same axis; (b) materials have no conductor — log(volume × nsites) loads on the same axis; (c) the loading is 0.995, not exactly 1.0. Is there a principled argument that this is more than feature repetition? Or is there a test that would falsify the universality claim?

### Q5. The Sieve — Is It Useful?
> Given M = log(N) with 1% precision and M_2 = f_2 × log(2), we narrow the conductor N to a median of 1 candidate. But we computed M FROM N, so we already knew N. Is there a scenario where you know Megethos WITHOUT knowing N directly? For example: from zero counts of an L-function, or from cross-domain tensor coupling, could you recover N without ever factoring it?

### Q6. Effective Dimensionality
> PCA on 47K objects across 18 domains gives effective dimensionality 11.4, with 15 axes for 90% variance. But we padded features to 28 dimensions (max = knots), so domains with 3-6 features have 22-25 zero columns. Could zero-padding inflate or distort the PCA? What's the right way to do PCA across domains with different feature dimensions?

---

## Category 3: Extension — "If this is real, what follows?"

### Q7. Predicting Unknown Ranks
> Bathos equation: P(rank ≥ 1) = sigmoid(0.292 × Megethos - 2.225). If this holds beyond our dataset, it predicts that for conductor N = e^20 ≈ 4.9 × 10^8, P(rank ≥ 1) = 0.87. For N = e^30 ≈ 10^13, P(rank ≥ 1) = 0.97. Does this match known heuristics for rank distribution at large conductor (e.g., Katz-Sarnak, Watkins, Park-Poonen-Voight-Wood)?

### Q8. GUE Violation
> We find that while the mean normalized zero spacing = 1.0 at all conductor sizes (confirming GUE), the MEDIAN drops from 0.97 (log(conductor) ≈ 2) to 0.32 (log(conductor) ≈ 7). The standard deviation increases from 0.46 to 3.14. Is this a known finite-size effect in the GUE prediction for low-lying zeros, or is this new? Could this be an artifact of having too few zeros per curve at high conductor?

### Q9. Cross-Domain Analogy
> In our Kosmos embedding, the analogy EC(conductor=11) - MF(level=11) + MF(level=37) lands near EC(conductor=37) in 2 out of 3 tests. This is the mathematical equivalent of word2vec's "king - man + woman = queen." If this scales, it means the Kosmos preserves analogical structure across domains. Has anyone demonstrated linear analogies between mathematical objects in different domains? Is there a theoretical reason this should or shouldn't work?

### Q10. Klados = Ramified Megethos
> We find that the "branching" phoneme (how maps ramify, how conductors factor) decomposes as M_sq = Σ_{f_p ≥ 2} f_p × log(p) — the ramified part of the Megethos decomposition. This means ramification is not independent of magnitude; it's the part of magnitude that comes from repeated prime factors. Is this relationship (ramification ⊂ conductor) formalized in existing theory, or is it only implicit?

---

## Category 4: Connection — "Does this remind you of anything?"

### Q11. The Decaphony and Langlands
> We identified 10 universal axes of mathematical structure (5 original + 5 from "island" domains). The original 5 (Megethos/magnitude, Bathos/rank, Symmetria/symmetry, Arithmos/torsion, Phasma/spectrum) reduce to 2 independent voices: Megethos and Arithmos. The Langlands program connects automorphic forms to Galois representations through L-functions. Is the Megethos-Arithmos pair related to the automorphic-Galois duality? Is magnitude the automorphic side and torsion the Galois side?

### Q12. The Product Formula and Adeles
> Megethos decomposes as M = Σ_p M_p where M_p = f_p × log(p). The product formula says the archimedean part = sum of non-archimedean parts. This looks like the adelic formulation: the object lives in the adele ring A_Q = R × Π_p Q_p, and Megethos is the projection to R while M_p is the projection to Q_p. Is this connection literal, or just analogical?

### Q13. 11.4 Dimensions
> The effective dimensionality of our mathematical Kosmos is 11.4. String theory has 10 or 11 dimensions. This is almost certainly a coincidence, but: is there any theoretical reason the "dimension of mathematical structure" should be related to the dimension of physical spacetime? Are there information-theoretic arguments for why ~11 independent axes would suffice to describe cross-domain mathematical relationships?

### Q14. Tensor Trains and Quantum Entanglement
> Our tensor train decomposition of cross-domain structure is mathematically identical to MPS (matrix product states) in quantum mechanics. Bond dimension = entanglement entropy between subsystems. We find that mathematical domains are "entangled" with bond dimensions 1-15. Is there a sense in which mathematical domains are quantum-mechanically entangled, or is this purely a formal analogy?

---

## Category 5: Equation — "Can you derive this?"

### Q15. The Bathos Sigmoid
> We fit P(rank ≥ 1) = σ(0.292 × log(N) - 2.225) with clean data. Can you derive this sigmoid from BSD, the explicit formula for the order of vanishing, and the distribution of central L-values? What does the coefficient 0.292 correspond to?

### Q16. The Megethos Equation for Knots
> For knots, Megethos = crossing number. For EC, Megethos = log(conductor). Is there a natural map from knots to L-functions where crossing number maps to log(conductor)? The colored Jones polynomial has connections to quantum invariants and hyperbolic volume — does volume play the role of conductor for knots?

### Q17. Derive the 11.4
> Given N domains with feature dimensions d_1, ..., d_N, and M total objects, what is the expected effective dimensionality of the combined PCA? Can you derive 11.4 from our specific parameters (18 domains, features 3-28, ~50K objects)?

---

## How to Present

For each model, provide:
1. The Harmonia README (harmonia/README.md)
2. The Decaphony document (harmonia/docs/the_decaphony.md)  
3. The Megethos equation (harmonia/docs/megethos_equation.md)
4. These questions

Ask each model to:
- Answer each question with confidence levels (certain / probable / speculative / don't know)
- Flag any questions where the answer is "this is already a known theorem"
- Flag any questions where the answer is "this is almost certainly wrong because X"
- Suggest follow-up experiments for any question they find genuinely novel

**Disagreement between models is the most valuable signal.** If Claude says "known theorem" and Gemini says "novel," one of them is wrong, and figuring out which reveals the boundary of mathematical knowledge.
