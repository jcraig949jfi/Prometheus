# Information Theory + Dual Process Theory + Feedback Control

**Fields**: Mathematics, Cognitive Science, Control Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T21:31:20.948941
**Report Generated**: 2026-03-27T23:28:38.581717

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage (System 1‑like fast extractor)** – Using only the `re` module we scan the prompt and each candidate answer for a fixed set of linguistic patterns:  
   * Negations (`not`, `no`, `-n't`) → Boolean flag `neg`.  
   * Comparatives (`more than`, `less than`, `≥`, `≤`) → tuple `(subj, op, obj)` where `op∈{<,>,=,≠}`.  
   * Conditionals (`if … then …`, `unless`) → implication `(antecedent → consequent)`.  
   * Causal verbs (`because`, `due to`, `leads to`) → directed edge.  
   * Numeric values → float conversion.  
   All extracted propositions are stored in a list of dictionaries `[{'type':…, 'subj':…, 'pred':…, 'obj':…, 'neg':bool}]`.  

2. **Semantic similarity via Information Theory (System 2‑like deliberate scorer)** – For each proposition type we build a binary feature vector `f ∈ {0,1}^K` (K = number of distinct proposition templates observed in the training set). The vector for a candidate answer is the OR‑sum of its proposition vectors.  
   * Compute the empirical distribution `P` of feature vectors over a small validation set of known‑good answers.  
   * For a candidate vector `q` (treated as a one‑hot distribution over the observed vectors) calculate **KL‑divergence** `D_KL(q‖P)` and **mutual information** `I(q;P) = H(P) – H(P|q)`.  
   * The raw score is `s = –D_KL(q‖P) + α·I(q;P)` (α tuned later).  

3. **Feedback‑control adjustment (PID loop)** – Treat the deviation between the raw score `s` and a target correctness signal `t` (1 for known correct answers, 0 for known incorrect ones in the validation set) as error `e = t – s`.  
   * Update a scalar weight `w` that multiplies the information‑theoretic term using a discrete PID:  
     `w_{n+1} = w_n + Kp·e_n + Ki·∑e + Kd·(e_n – e_{n-1})`.  
   * The final score is `score = w·( –D_KL + α·I )`. All updates use only `numpy` for vector ops and scalar arithmetic.  

**Structural features parsed** – negations, comparatives, conditionals, causal claims, numeric constants, ordering relations (`>`, `<`, `=`), and explicit conjunctions/disjunctions extracted via regex.

**Novelty** – While information‑theoretic scoring and PID control appear separately in NLP (e.g., entropy‑based confidence, adaptive thresholding), their conjunction with a dual‑process‑inspired two‑stage parser‑then‑refine loop, implemented purely with numpy/regex, has not been described in the literature. Existing neuro‑symbolic or probabilistic logic systems rely on learned parameters or external solvers; this method is fully algorithmic and transparent.

**Ratings**  
Reasoning: 7/10 — captures logical structure and uncertainty but lacks deep semantic understanding.  
Metacognition: 6/10 — PID provides basic self‑correction; no explicit monitoring of reasoning steps.  
Hypothesis generation: 5/10 — limited to proposing adjustments of a single weight; no alternative answer generation.  
Implementability: 9/10 — relies only on regex, numpy arrays, and simple arithmetic; easy to code and debug.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
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
