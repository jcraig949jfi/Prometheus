# Dual Process Theory + Neuromodulation + Metamorphic Testing

**Fields**: Cognitive Science, Neuroscience, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T17:11:14.025926
**Report Generated**: 2026-03-31T14:34:56.979080

---

## Nous Analysis

The algorithm treats each candidate answer as a text string `S`.  
**Fast (System 1) path** – extract a fixed‑length feature vector `f(S)` using only regex and stdlib:  
- token count, presence of negation (`not`, `no`), comparative tokens (`more`, `less`, `>`, `<`), causal tokens (`because`, `leads to`), conditional tokens (`if`, `then`), and numeric literals (converted to float).  
- Compute a linear score `z₁ = w·f(S)` where `w` is a hand‑tuned weight vector (e.g., higher weight for correct polarity of comparatives).  

**Slow (System 2) path** – build a proposition graph `G`.  
- Regex patterns extract atomic propositions:  
  * Comparatives: `(X) is (greater|less|more|less) than (Y)` → edge `X → Y` with label `>` or `<`.  
  * Conditionals: `if (A) then (B)` → edge `A → B` labeled `implies`.  
  * Causals: `(A) because (B)` → edge `B → A` labeled `cause`.  
  * Equality: `(X) equals (Y)` → undirected edge with label `=`.  
- Store adjacency in a NumPy matrix `M` where `M[i,j]=1` if a directed constraint exists, `-1` for opposite direction, `0` otherwise.  
- Run Floyd‑Warshall (NumPy‑based) to compute transitive closure `T`.  
- Detect contradictions: a pair `(i,j)` where `T[i,j]=1` and `T[j,i]=1` with opposing labels (e.g., both `>` and `<`). Let `c` be the number of contradictory pairs; `z₂ = 1 - c / (n*(n-1)/2)` where `n` is the number of distinct entities.  

**Neuromodulatory gain** – compute entropy `H` of the fast scores across all candidates: `H = -Σ p log p` where `p` is normalized `z₁`. Gain `g = σ(H)` (sigmoid) maps high uncertainty to greater reliance on the slow path.  

**Final score** for each candidate: `score = g·z₂ + (1-g)·z₁`.  

The approach parses structural features: negations, comparatives, conditionals, causal connectives, numeric values, ordering relations, and equality.  

This specific blend — dual‑process weighting modulated by a neuromodulatory gain derived from score entropy, combined with metamorphic‑testing‑style constraint propagation — has not been described in prior surveys; existing work uses either ensemble voting or MR testing in isolation, not a gain‑controlled hybrid.  

Reasoning: 7/10 — captures logical structure but relies on hand‑crafted patterns, limiting coverage of complex reasoning.  
Metacognition: 6/10 — gain mechanism provides a crude confidence estimate; true self‑monitoring would require richer uncertainty modeling.  
Hypothesis generation: 5/10 — the system extracts propositions but does not generate new hypotheses beyond constraint checking.  
Implementability: 8/10 — uses only regex, NumPy, and stdlib; straightforward to code and test.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: unclear
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
