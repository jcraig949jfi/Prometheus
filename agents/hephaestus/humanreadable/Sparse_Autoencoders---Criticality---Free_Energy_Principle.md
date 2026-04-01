# Sparse Autoencoders + Criticality + Free Energy Principle

**Fields**: Computer Science, Complex Systems, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T23:19:27.605612
**Report Generated**: 2026-03-31T14:34:55.472074

---

## Nous Analysis

**Algorithm**  
We build a *sparse predictive coding scorer* that treats each sentence as a binary bag‑of‑words vector **x** ∈ {0,1}^V (V = vocabulary size). A dictionary **D** ∈ ℝ^{V×K} (K ≫ V) is learned online with an Orthogonal Matching Pursuit (OMP) step that enforces an L1 sparsity penalty λ. For a given input **x** we obtain a sparse code **a** ∈ ℝ^K (‖a‖₀ ≤ s) by solving  

```
a = argmin‖x – D a‖₂² + λ‖a‖₁      (OMP with λ)
```

The *variational free energy* of the representation is approximated as  

```
F(x) = ‖x – D a‖₂² + λ‖a‖₁          (reconstruction + sparsity cost)
```

Criticality is introduced by adapting λ during training so that the distribution of activation avalanches (sizes of consecutive non‑zero entries in **a**) follows a power‑law; this is done by monitoring the exponent α and adjusting λ with a simple stochastic rule (increase λ if α > 2, decrease if α < 1.5).  

To score a candidate answer **c** we first extract a set of logical constraints **C** from the question and any background facts using regex‑based pattern matching (see §2). Each constraint is a directed edge (p → q) in a Boolean implication graph. We compute the transitive closure of **C** with Floyd‑Warshall on a K×K Boolean matrix **T** (O(K³) but K is kept ≤ 200 for tractability).  

The final score combines free energy and constraint violation:  

```
score(c) = –F(x_c) – μ·‖T·a_c – a_c‖₀
```

where **x_c** is the bag‑of‑words vector of the candidate, **a_c** its sparse code, and μ weights the penalty for any implication whose antecedent is active (a_c[i]=1) but consequent inactive (a_c[j]=0). Lower free energy (better reconstruction) and fewer violated implications yield a higher score.

**Structural features parsed**  
Regex patterns extract:  
- Negations: `\b(not|no|never)\b`  
- Comparatives: `\b(more|less|greater|fewer)\b.*\b(than|than\s+\d+)\b`  
- Conditionals: `\bif\b.*\bthen\b`  
- Causal claims: `\bbecause\b|\bleads to\b|\bcauses\b`  
- Numeric values: `\d+(\.\d+)?`  
- Ordering relations: `\bbefore\b|\bafter\b|\bearlier\b|\blater\b`  

Each match yields a propositional atom (e.g., “X > 5”) that populates the implication graph.

**Novelty**  
Sparse coding and free‑energy minimization are well‑studied in predictive coding neuroscience; criticality has been linked to neural avalanches. Combining them with explicit logical constraint propagation for text scoring has not been published in the NLP literature, making the approach novel, though it resembles hybrid neuro‑symbolic models.

**Ratings**  
Reasoning: 7/10 — captures logical structure and uncertainty but lacks deep semantic understanding.  
Metacognition: 5/10 — free energy provides a self‑assessment signal, yet no higher‑order reflection on its own uncertainty.  
Hypothesis generation: 6/10 — sampling alternative sparse codes yields candidate explanations, but diversity is limited by dictionary size.  
Implementability: 8/10 — relies only on NumPy for matrix ops and the Python stdlib for regex; all components are straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-28T06:32:31.370803

---

## Code

*No code was produced for this combination.*
