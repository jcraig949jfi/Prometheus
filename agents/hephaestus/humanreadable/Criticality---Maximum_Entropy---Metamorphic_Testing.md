# Criticality + Maximum Entropy + Metamorphic Testing

**Fields**: Complex Systems, Statistical Physics, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T02:32:00.236035
**Report Generated**: 2026-04-02T04:20:09.526747

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Factor Graph**  
   - Extract propositions \(p_i\) from the prompt and each candidate answer using regex patterns for:  
     *Negation* (`not`, `no`), *comparatives* (`>`, `<`, `>=`, `<=`, `more than`, `less than`), *conditionals* (`if … then …`, `unless`), *causal* (`because`, `leads to`, `causes`), *ordering* (`before`, `after`, `first`, `last`), and *numeric literals*.  
   - Each proposition becomes a binary variable \(x_i\in\{0,1\}\) (true/false).  
   - For every extracted relation add a factor:  
     *Negation*: \(\phi_{i}(x_i)=\exp\{w_{\neg}\,x_i\}\) with \(w_{\neg}<0\) to penalize true when negated.  
     *Comparative*: \(\phi_{ij}(x_i,x_j)=\exp\{w_{c}\,[x_i\oplus x_j]\}\) enforcing the direction.  
     *Conditional*: \(\phi_{ij}(x_i,x_j)=\exp\{w_{imp}\,[\neg x_i \lor x_j]\}\).  
     *Causal/Ordering*: similar implication factors.  
   - The joint distribution is a log‑linear model:  
     \[
     P(\mathbf{x})\propto\exp\Big(\sum_k w_k f_k(\mathbf{x})\Big)
     \]
     where each \(f_k\) is the indicator of a satisfied factor.

2. **Maximum‑Entropy Parameter Fitting**  
   - Initialise all weights \(w_k=0\).  
   - Using only the prompt (treat it as observed constraints), perform iterative scaling (or simple gradient ascent) to find the MaxEnt distribution that matches the empirical expectations of each factor (i.e., the fraction of times the factor should be true given the prompt).  
   - This yields the least‑biased distribution consistent with the prompt’s logical structure.

3. **Metamorphic Perturbation & Criticality Scoring**  
   - Define a set of Metamorphic Relations (MRs) on the prompt:  
     *Numeric scaling*: multiply every extracted number by 2.  
     *Order swap*: swap the conjuncts of an `and`.  
     *Negation flip*: insert/remove a `not` before a proposition.  
   - For each MR generate a perturbed prompt, re‑fit the MaxEnt weights (same iterative scheme, cheap because only a few factors change) and compute the probability \(P_{\text{MR}}(a)\) of each candidate answer \(a\) (the marginal of its constituent propositions).  
   - Compute the **susceptibility** (variance) of answer scores across MRs:  
     \[
     \chi_a = \operatorname{Var}_{MR}\big(P_{MR}(a)\big)
     \]
   - Final score combines expected likelihood and inverse susceptibility (high susceptibility → low score, reflecting proximity to a critical point):  
     \[
     S_a = \frac{\langle P_{MR}(a)\rangle}{1+\chi_a}
     \]
     where \(\langle\cdot\rangle\) denotes averaging over all MRs (including the unperturbed prompt).

**Parsed Structural Features**  
Negations, comparatives (`>`, `<`, `>=`, `<=`), conditionals (`if‑then`), causal claims (`because`, `leads to`), ordering/temporal relations (`before`, `after`, `first`, `last`), numeric constants, and quantifiers (`all`, `some`, `none`).

**Novelty**  
Maximum‑Entropy framing of logical constraints and metamorphic testing of software are each well‑studied, and criticality concepts appear in physics and complex‑systems analysis. Their conjunction — using MaxEnt to define a prompt‑consistent distribution, probing it with MRs to estimate susceptibility, and scoring answers by likelihood‑over‑susceptibility — has not been reported in the literature for reasoning evaluation, making the combination novel.

**Ratings**  
Reasoning: 8/10 — captures logical structure and sensitivity to perturbations, aligning with human‑like robustness.  
Metacognition: 6/10 — the method can flag unstable answers but does not explicitly reason about its own uncertainty beyond variance.  
Hypothesis generation: 5/10 — generates perturbed prompts (MRs) but does not propose new explanatory hypotheses beyond score variation.  
Implementability: 9/10 — relies only on regex parsing, numpy linear algebra for iterative scaling, and standard‑library data structures; no external APIs or neural nets required.

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
