# Dual Process Theory + Adaptive Control + Metamorphic Testing

**Fields**: Cognitive Science, Control Theory, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T01:19:20.342310
**Report Generated**: 2026-04-02T04:20:11.697041

---

## Nous Analysis

**Algorithm**  
The evaluator builds a *dual‑mode constraint graph* from each candidate answer.  
1. **Fast mode (System 1)** – a regex‑based extractor produces a list of atomic propositions \(P_i\) (e.g., “X > Y”, “¬A”, “if C then D”). Each proposition is stored as a node with a feature vector \(f_i\in\mathbb{R}^k\) (presence of negation, comparative, numeric value, causal cue). A fast score \(S_f\) is the cosine similarity between the average \(f\) of the answer and a prototype vector derived from the prompt’s correct‑answer patterns (pre‑computed offline).  
2. **Slow mode (System 2)** – the propositions are inserted into a directed graph \(G=(V,E)\) where edges encode metamorphic relations (MRs) such as:  
   * **Ordering MR** – if \(p_a\): “X < Y” and \(p_b\): “Y < Z” then infer \(X < Z\).  
   * **Doubling MR** – if \(p\): “value = v” then \(p'\): “value = 2·v”.  
   * **Negation MR** – \(p\) and \(¬p\) cannot both be true.  
   Constraint propagation (a variant of the Bellman‑Ford relaxation) runs over \(G\) to detect inconsistencies; each violated MR adds a penalty \(p_j\). The slow score \(S_s = -\sum_j w_j p_j\) where weights \(w_j\) are adapted online.  
3. **Adaptive Control** – after scoring a batch of answers, the controller updates the MR weights using a simple exponential‑moving‑average rule:  
   \(w_j \leftarrow (1-\alpha)w_j + \alpha \cdot \text{error}_j\), where \(\text{error}_j\) is the proportion of times MR \(j\) was violated in answers that the prompt’s key marked as correct. This drives the system to up‑weight relations that reliably discriminate correct from incorrect responses.  
The final score is \(S = \lambda S_f + (1-\lambda) S_s\) with \(\lambda\) fixed (e.g., 0.4) to balance intuition and deliberation.

**Structural features parsed** – negations, comparatives (“>”, “<”, “≥”), conditionals (“if … then …”), numeric values (integers, decimals), causal cues (“because”, “leads to”), and ordering chains (transitive relations).

**Novelty** – While each component appears separately (e.g., metamorphic testing in software, adaptive controllers in control theory, dual‑process models in cognition), their conjunction into a single, numpy‑implemented scoring pipeline that jointly uses fast similarity, slow constraint propagation, and online weight adaptation has not been reported in the literature on reasoning‑evaluation tools.

**Ratings**  
Reasoning: 8/10 — captures logical consistency and numeric reasoning via constraint propagation, but limited to hand‑crafted MRs.  
Metacognition: 6/10 — adaptive weight updates give a rudimentary self‑monitoring signal, yet no explicit confidence estimation.  
Hypothesis generation: 5/10 — the system can propose inferred facts via MR propagation, but does not rank alternative hypotheses.  
Implementability: 9/10 — relies only on regex, numpy vector ops, and simple graph relaxation; all feasible in pure Python.

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
