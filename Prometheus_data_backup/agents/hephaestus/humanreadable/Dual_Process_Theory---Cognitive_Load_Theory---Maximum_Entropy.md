# Dual Process Theory + Cognitive Load Theory + Maximum Entropy

**Fields**: Cognitive Science, Cognitive Science, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T00:41:33.587541
**Report Generated**: 2026-03-31T19:12:22.145301

---

## Nous Analysis

**Algorithm**  
1. **Parse** the prompt and each candidate answer with a small rule‑based extractor (regex + spaCy‑like token patterns) to produce a set of grounded propositions \(P = \{p_i\}\). Each proposition is a tuple \((\text{subject}, \text{relation}, \text{object})\) where the relation can be equality, inequality, comparatives, negation, or a conditional antecedent→consequent.  
2. **Build a constraint matrix** \(C\in\{0,1\}^{m\times n}\) ( \(m\) constraints, \(n\) propositions ) where \(C_{kj}=1\) if proposition \(p_j\) participates in constraint \(k\). Constraints encode:  
   * transitivity of ordering (if \(a<b\) and \(b<c\) then \(a<c\)),  
   * modus ponens for conditionals,  
   * consistency of negations ( \(p\) and \(\neg p\) cannot both be true),  
   * numeric equality/inequality from extracted numbers.  
3. **Maximum‑entropy inference**: treat the truth vector \(x\in[0,1]^n\) as probabilities of each proposition. Maximize \(H(x)=-\sum_i[x_i\log x_i+(1-x_i)\log(1-x_i)]\) subject to \(Cx = b\) (where \(b\) encodes the required truth value of each constraint, e.g., 1 for satisfied, 0 for violated). Using Lagrange multipliers, the solution is an exponential‑family distribution:  
   \[
   x_i = \sigma\!\bigl(\sum_k \lambda_k C_{ki}\bigr)
   \]
   where \(\sigma\) is the logistic function and \(\lambda\) are obtained by iterating Newton’s method on the dual (all operations done with NumPy).  
4. **Cognitive‑load penalty**: compute a load score \(L\) for each candidate as the weighted sum of (a) number of distinct propositions, (b) depth of nested conditionals, and (c) count of numeric entities – all proxies for intrinsic+extraneous load.  
5. **Final score** for candidate \(c\):  
   \[
   S_c = \underbrace{\sum_i w_i \log x_i}_{\text{max‑entropy likelihood}} \;-\; \alpha L_c
   \]
   where \(w_i\) gives higher weight to propositions that are central to the question (identified via dependency‑parse heuristics) and \(\alpha\) balances likelihood against load (chosen via a small validation set). The candidate with highest \(S_c\) is selected.

**Structural features parsed**  
- Negations (“not”, “no”)  
- Comparatives (“greater than”, “less than”, “as … as”)  
- Conditionals (“if … then …”, “unless”)  
- Numeric values and units  
- Causal verbs (“cause”, “lead to”, “result in”)  
- Ordering/temporal relations (“before”, “after”, “precedes”)  

**Novelty**  
The approach fuses three well‑studied ideas: (i) symbolic extraction of logical constraints (common in logic‑based QA), (ii) maximum‑entropy principle for deriving a least‑biased probability distribution (Jaynes‑style log‑linear models), and (iii) cognitive‑load weighting to penalize overly complex candidates. While each piece appears separately (e.g., Markov Logic Networks, Probabilistic Soft Logic, load‑aware scoring in tutoring systems), the specific combination—using a pure NumPy solution of the max‑entropy dual to obtain proposition probabilities and then subtracting a load‑derived penalty—has not been described in the literature to the best of my knowledge, making it novel for a lightweight, non‑neural evaluation tool.

**Rating**  
Reasoning: 8/10 — captures logical consistency via constraint propagation and provides a principled likelihood estimate, though it depends on the quality of the rule‑based extractor.  
Metacognition: 7/10 — the load penalty mimics System 2 monitoring, but the model lacks explicit self‑assessment of uncertainty beyond the entropy term.  
Hypothesis generation: 6/10 — generates hypotheses implicitly through the space of proposition truth assignments, but does not propose novel external hypotheses; it only evaluates given candidates.  
Implementability: 9/10 — relies only on regex/spaCy‑style patterns, NumPy linear algebra, and simple iteration; no external libraries or APIs are needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T19:10:07.346649

---

## Code

*No code was produced for this combination.*
