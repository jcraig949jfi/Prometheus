# Dual Process Theory + Adaptive Control + Multi-Armed Bandits

**Fields**: Cognitive Science, Control Theory, Game Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T18:22:07.339173
**Report Generated**: 2026-04-01T20:30:44.119110

---

## Nous Analysis

**Algorithm**  
Each candidate answer is treated as an arm of a multi‑armed bandit. For every answer we first extract a fixed‑length feature vector **x** ∈ ℝⁿ using only regex‑based structural parsing (see §2).  
*System 1* (fast) computes a heuristic score:  
`s₁ = w·x` where **w** ∈ ℝⁿ is a weight vector updated by adaptive control.  
*System 2* (slow) builds a tiny constraint graph from the prompt and the answer: nodes are propositions extracted from the text; edges represent logical relations (implication, ordering, equality). Using numpy we propagate constraints (transitivity, modus ponens) and count the proportion of satisfied constraints, yielding a consistency score `s₂ ∈ [0,1]`.  

The combined score for arm *i* at round *t* is:  
`Sᵢₜ = αₜ·s₁ᵢ + (1‑αₜ)·s₂ᵢ`, where αₜ ∈ [0,1] balances fast vs. slow reasoning.  

**Adaptive control** updates **w** and α after each batch of evaluated answers by minimizing a simple squared‑error loss against a small validation set (ground‑truth correctness). Gradient steps are performed with numpy:  
`w ← w – η·∇L(w)`, `α ← α – η·∇L(α)`, projecting α back to [0,1].  

**Bandit policy** decides which answers receive the expensive System 2 evaluation. We maintain for each arm an empirical mean μᵢ of its System 2 score and a pull count nᵢ. The UCB index is:  
`UCBᵢ = μᵢ + c·√(log T / nᵢ)`, with T total pulls so far. At each step we select the arm with the highest UCB, run System 2 on it, update μᵢ and nᵢ, then recompute Sᵢ for all arms using the latest w and α. The final ranking uses the latest Sᵢ.  

**Structural features parsed** (regex‑based): negation tokens (“not”, “no”), comparative/superlative adjectives, conditional conjunctions (“if”, “unless”, “provided that”), causal connectives (“because”, “therefore”, “leads to”), numeric expressions (integers, decimals, fractions), ordering words (“more than”, “less than”, “before”, “after”, “greater than”), quantifiers (“all”, “some”, “none”).  

**Novelty** – While dual‑process models, adaptive controllers, and bandits appear separately in cognitive science and ML, tying them together to dynamically allocate deliberate reasoning effort via a UCB‑driven bandit, while continuously tuning the fast/slow blend with gradient‑based adaptive control, has not been reported in existing answer‑scoring or reasoning‑evaluation tools.  

**Ratings**  
Reasoning: 7/10 — captures logical structure but lacks deep semantic modeling.  
Metacognition: 6/10 — adaptive weight updates give limited self‑regulation.  
Hypothesis generation: 5/10 — bandit encourages exploration of answers yet hypothesis space is shallow.  
Implementability: 8/10 — relies solely on numpy and stdlib; all components are straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*
