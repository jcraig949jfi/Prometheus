# Information Theory + Hebbian Learning + Free Energy Principle

**Fields**: Mathematics, Neuroscience, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T15:44:58.500987
**Report Generated**: 2026-03-27T16:08:16.963259

---

## Nous Analysis

**Algorithm: Predictive‑Error‑Weighted Mutual Information (PEWMI)**  

1. **Parsing & Symbol Extraction**  
   - Tokenise the prompt *P* and each candidate answer *Aᵢ* with a regex‑based tokenizer that captures:  
     - Predicates (verb‑noun pairs)  
     - Negations (`not`, `no`)  
     - Comparatives (`greater than`, `less than`, `more … than`)  
     - Conditionals (`if … then`, `unless`)  
     - Causal markers (`because`, `due to`, `leads to`)  
     - Numeric literals and units  
     - Ordering tokens (`first`, `last`, `before`, `after`)  
   - Each token type is mapped to a symbolic ID and stored in a sparse binary vector **x** ∈ {0,1}^|V|, where *V* is the vocabulary of extracted symbols.

2. **Hebbian Co‑occurrence Matrix**  
   - Initialise a symmetric matrix **W** ∈ ℝ^{|V|×|V|} (zeros).  
   - For every prompt *P* observed during a brief offline “exposure” phase (e.g., a corpus of training Q‑A pairs), update **W** with Hebbian rule:  
     ```
     ΔW = η (x_P ⊗ x_P)          # outer product
     W ← W + ΔW
     ```  
   - After exposure, **W** approximates the joint probability of symbol co‑occurrence (up to a scaling factor).

3. **Prediction (Free Energy) Step**  
   - For a candidate answer *Aᵢ*, compute its symbolic vector **xᵢ**.  
   - Predicted activation: **p̂ᵢ** = softmax(**W**·**xᵢ**) (numpy only).  
   - Treat **p̂ᵢ** as the model’s belief distribution over symbols given the prompt.  
   - Compute variational free energy as the KL divergence between belief and the answer’s one‑hot observation:  
     ```
     Fᵢ = KL(δ_{xᵢ} || p̂ᵢ) = -log p̂ᵢ[xᵢ]   # δ is one‑hot at observed symbols
     ```  
   - Lower *Fᵢ* means the answer predicts the observed symbols with high probability (i.e., low prediction error).

4. **Information‑Theoretic Weighting**  
   - Compute mutual information between prompt and answer symbols using the empirical joint distribution approximated by **W**:  
     ```
     I(P;Aᵢ) = Σ_{v,w} P(v,w) log [P(v,w)/(P(v)P(w))]
     ```  
     where *P(v,w)* = W_{v,w} / ΣW, *P(v)* = Σ_w W_{v,w} / ΣW, etc.  
   - Final score: **Sᵢ** = I(P;Aᵢ) – λ·Fᵢ (λ balances informativeness vs. prediction error; set λ=0.5 by default).

5. **Constraint Propagation (Optional Refine)**  
   - Extract numeric constraints and ordering relations from **xᵢ** (e.g., “X > 5”, “Y before Z”).  
   - Apply simple transitive closure and modus ponens using numpy arrays to detect violations; add a penalty *Cᵢ* proportional to the number of violated constraints.  
   - Final adjusted score: **Sᵢ′** = Sᵢ – Cᵢ.

**Structural Features Parsed** – negations, comparatives, conditionals, causal markers, numeric values with units, ordering tokens, and predicate‑argument pairs.

**Novelty** – The combination mirrors the Free Energy Principle’s prediction‑error minimization, Hebbian learning’s statistics‑based weight update, and Information Theory’s mutual information as a relevance measure. While each component appears separately in cognitive modeling (e.g., predictive coding networks, Hebbian LTP, info‑theoretic relevance scoring), their joint use in a pure‑numpy, symbol‑based scoring engine for Q‑A evaluation has not been reported in the literature, making the approach novel in this specific implementation.

**Ratings**  
Reasoning: 8/10 — captures logical consistency via constraint propagation and prediction error, but relies on shallow symbolic parsing.  
Metacognition: 6/10 — the algorithm can monitor its own free‑energy term to gauge confidence, yet lacks higher‑order self‑reflection.  
Hypothesis generation: 5/10 — generates implicit hypotheses through predicted symbol distribution, but does not explicitly propose new candidates.  
Implementability: 9/10 — uses only numpy and stdlib; all operations are matrix multiplications, KL divergence, and simple regex parsing, making it straightforward to code and run.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

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
