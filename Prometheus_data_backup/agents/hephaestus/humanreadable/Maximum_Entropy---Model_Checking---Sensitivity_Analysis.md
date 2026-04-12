# Maximum Entropy + Model Checking + Sensitivity Analysis

**Fields**: Statistical Physics, Formal Methods, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T20:34:28.158486
**Report Generated**: 2026-04-02T04:20:11.088141

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Propositional variables** – Using regex we extract atomic propositions (e.g., “X > Y”, “¬P”, “if A then B”, causal links “A → B”). Each proposition becomes a Boolean variable \(v_i\). Numeric comparisons are turned into propositions with a threshold variable (e.g., “score ≥ 0.7”).  
2. **Constraint set** – From the extracted relations we build a set of logical clauses \(C\):  
   * Negations → unit clause \(\lnot v_i\).  
   * Comparatives/ordering → chains encoded as transitivity constraints (e.g., \(v_{X>Y}\land v_{Y>Z}\Rightarrow v_{X>Z}\)).  
   * Conditionals → implication clauses \(v_A\Rightarrow v_B\).  
   * Causal claims → same as conditionals but weighted separately for sensitivity.  
3. **Finite‑state model** – The truth‑assignment space is the Cartesian product \(\{0,1\}^n\) (n = number of variables). This is the state space explored by explicit model checking.  
4. **Maximum‑entropy distribution** – We assign a weight \(w_j\ge0\) to each clause \(C_j\). The log‑linear (maximum‑entropy) distribution over worlds \(w\) is  
   \[
   P(w)=\frac{1}{Z}\exp\Big(\sum_j w_j\cdot \mathbf{1}[w\models C_j]\Big),
   \]  
   where \(\mathbf{1}\) is the indicator. With numpy we compute \(Z\) by enumerating all \(2^n\) worlds (feasible for ≤20 variables; otherwise we use BDD‑based state‑space pruning, still pure numpy).  
5. **Model‑checking score** – For a candidate answer \(A\) (a proposition or conjunction), its raw score is the marginal probability  
   \[
   s(A)=\sum_{w\models A} P(w).
   \]  
   This is the probability that the answer holds under the least‑biased distribution satisfying all extracted constraints.  
6. **Sensitivity analysis** – To gauge robustness we perturb each clause weight \(w_j\) by a small \(\epsilon\) and recompute \(s(A)\). The sensitivity vector is  
   \[
   \frac{\partial s(A)}{\partial w_j}\approx\frac{s(A|_{w_j+\epsilon})-s(A|_{w_j})}{\epsilon},
   \]  
   obtained via finite differences with numpy. The final score combines the raw probability and a penalty proportional to the L2 norm of the sensitivity vector, yielding a single scalar that rewards answers that are both probable and stable under small constraint changes.

**Structural features parsed**  
- Negations (“not”, “no”)  
- Comparatives and ordering (“greater than”, “less than”, “before/after”)  
- Conditionals (“if … then …”, “only if”)  
- Numeric thresholds and arithmetic relations  
- Causal claims (“causes”, “leads to”, “due to”)  
- Existential/universal quantifiers implied by “all”, “some” (converted to unit clauses or patterns)

**Novelty**  
The combination mirrors concepts in Markov Logic Networks (weighted logical formulas) and Probabilistic Soft Logic, but it adds an explicit sensitivity‑analysis step that quantifies how the answer’s probability changes under infinitesimal weight perturbations. While weighted model counting exists, the specific pipeline—regex extraction → finite‑state enumeration → max‑entropy marginal → numpy‑based finite‑difference sensitivity—is not described in the standard literature, making it a novel algorithmic formulation for answer scoring.

**Ratings**  
Reasoning: 8/10 — captures logical structure and uncertainty via principled max‑entropy inference.  
Metacognition: 6/10 — sensitivity provides a rudimentate self‑check but lacks higher‑order reflection on the parsing process itself.  
Hypothesis generation: 5/10 — the method evaluates given hypotheses; it does not propose new ones beyond the extracted propositions.  
Implementability: 9/10 — relies only on regex, numpy arrays, and explicit state‑space enumeration; no external libraries or APIs needed.

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
