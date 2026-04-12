# Phase Transitions + Falsificationism + Maximum Entropy

**Fields**: Physics, Philosophy, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T04:37:43.138105
**Report Generated**: 2026-04-02T08:39:55.094856

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex to extract from the prompt and each candidate answer a set of grounded literals:  
   - *Entities* (noun phrases) → IDs.  
   - *Predicates* of arity 2: relations like “greater‑than”, “causes”, “is‑part‑of”, plus polarity flag for negations.  
   - *Numeric constraints*: values attached to entities (e.g., “temperature > 80”).  
   Store as a list of triples `(s, p, o, w)` where `w∈{+1,‑1}` encodes polarity (‑1 for negated). Build a sparse constraint matrix **C** (n_constraints × n_variables) where each row encodes a linear inequality/equality derived from a literal (e.g., `x_s - x_o ≥ 0` for “greater‑than”).  

2. **Maximum‑Entropy inference** – Treat the unknown truth‑values of entities as a real‑valued vector **x** (continuous relaxation). The MaxEnt distribution satisfying the expected constraints `〈C x〉 = b` (where **b** is the RHS of each literal) is  
   \[
   p(\mathbf{x}) \propto \exp(-\boldsymbol{\lambda}^\top C\mathbf{x})
   \]  
   Solve for Lagrange multipliers **λ** with Generalized Iterative Scaling (GIS) using only NumPy (matrix‑vector products, logs).  

3. **Energy and susceptibility** – For each candidate answer **a**, compute its feature vector **xₐ** (1 if the literal is asserted true, 0 if false, 0.5 for unknown). The *energy* is  
   \[
   E_a = \boldsymbol{\lambda}^\top C\mathbf{x}_a .
   \]  
   To inject the phase‑transition idea, evaluate the *susceptibility* χₐ = Var_{δ}[E_{a+δ}] where δ is a small random perturbation (±ε) of **xₐ** (sampled 20 times). High χ indicates the answer lies near a critical point where tiny changes flip the energy dramatically → less robust.  

4. **Falsification score** – Count the number of constraints that, if violated (flip polarity of the corresponding literal), would increase Eₐ by more than a threshold τ (e.g., τ = 0.5·mean|E|). Call this **Fₐ**.  

5. **Final score** –  
   \[
   S_a = -E_a \;-\; \alpha \, \chi_a \;-\; \beta \, F_a
   \]  
   with α,β ∈ [0,1] tuned on a validation set. Lower energy (higher plausibility), low susceptibility (away from criticality), and few easy falsifications yield higher Sₐ.  

**Structural features parsed** – negations, comparatives (>,<,=), conditionals (“if … then …”), causal verbs (“causes”, “leads to”), ordering relations (“before/after”), numeric thresholds, and existential/universal quantifiers hinted by “all”, “some”.  

**Novelty** – The blend resembles Markov Logic Networks (MaxEnt + logical constraints) but adds a *phase‑transition susceptibility* term and an explicit falsification count, which to my knowledge is not present in existing pure‑numpy reasoning scorers.  

**Ratings**  
Reasoning: 8/10 — captures logical consistency, uncertainty, and robustness via energy and susceptibility.  
Metacognition: 6/10 — the algorithm can monitor its own susceptibility but lacks higher‑order self‑reflection on strategy choice.  
Hypothesis generation: 5/10 — it evaluates given hypotheses; generating new ones would require additional search mechanisms not included.  
Implementability: 9/10 — relies solely on regex, NumPy linear algebra, and simple iterative scaling; no external libraries or GPUs needed.

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

**Status**: Scrapped
**Reason**: validation:runtime_error: TypeError: 'NoneType' object is not iterable

**Forge Timestamp**: 2026-04-02T08:02:32.060340

---

## Code

**Source**: scrap

[View code](./Phase_Transitions---Falsificationism---Maximum_Entropy/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from collections import defaultdict

class ReasoningTool:
    """
    Maximum Entropy reasoning with phase transition susceptibility and falsification.
    
    Parses logical literals from text, builds constraint matrix, solves for MaxEnt
    distribution via Lagrange multipliers, computes energy + susceptibility for each
    candidate, and applies falsification scoring. Includes meta-confidence checks
    for ambiguous/unanswerable prompts (epistemic honesty).
    """
    
    def __init__(self):
        self.alpha = 0.3  # susceptibility weight
        self.beta = 0.2   # falsification weight
        self.epsilon = 0.1  # perturbation size
        self.n_perturb = 20
        
    def _meta_confidence(self, prompt):
        """Check prompt for ambiguity/unanswerability markers."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did.*fail|why did.*stop)', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\b(every|each|all).*\ba\b', p) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|they|it)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either.*or)\b', p) and not re.search(r'\b(only|must)\b', p):
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p) and not re.search(r'\b(largest|fastest|highest|most expensive)\b', p):
            return 0.3
        
        return 1.0
    
    def _extract_numbers(self, text):
        """Extract all numeric values from text."""
        return [float(x) for x in re.findall(r'\b\d+\.?\d*\b', text)]
    
    def _parse_literals(self, text):
        """Extract grounded literals: entities, relations, comparisons."""
        literals = []
        text_lower = text.lower()
        
        # Comparatives: greater/less than, more/fewer
        if re.search(r'\b(greater|more|higher|larger|bigger)\b.*\bthan\b', text_lower):
            literals.append(('comparative', 'greater', 1))
        if re.search(r'\b(less|fewer|smaller|lower)\b.*\bthan\b', text_lower):
            literals.append(('comparative', 'less', 1))
        
        # Negations
        neg_count = len(re.findall(r'\b(not|no|never|none|neither)\b', text_lower))
        if neg_count > 0:
            literals.append(('negation', neg_count, -1))
        
        # Conditionals
        if re.search(r'\b(if|when|whenever)\b.*\b(then|will|would)\b', text_lower):
            literals.append(('conditional', 'implication', 1))
        
        # Causal relations
        if re.search(r'\b(cause|lead to|result in|due to|because)\b', text_lower):
            literals.append(('causal', 'causation', 1))
        
        # Temporal ordering
        if re.search(r'\b(before|after|during|while)\b', text_lower):
            literals.append(('temporal', 'ordering', 1))
        
        # Quantifiers
        if re.search(r'\b(all|every|each)\b', text_lower):
            literals.append(('quantifier', 'universal', 1))
        if re.search(r'\b(some|any|few|several)\b', text_lower):
            literals.append(('quantifier', 'existential', 1))
        
        # Numeric values
        numbers = self._extract_numbers(text)
        for i, n in enumerate(numbers):
            literals.append(('numeric', i, n))
        
        return literals
    
    def _compute_ncd(self, s1, s2):
        """Normalized Compression Distance."""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def _build_constraint_matrix(self, prompt_literals, candidate_literals):
        """Build sparse constraint matrix from literals."""
        all_types = set([l[0] for l in prompt_literals + candidate_literals])
        n_constraints = len(all_types)
        n_vars = max(len(prompt_literals), len(candidate_literals), 1)
        
        C = np.zeros((n_constraints, n_vars))
        b = np.zeros(n_constraints)
        
        for i, typ in enumerate(sorted(all_types)):
            prompt_count = sum(l[2] for l in prompt_literals if l[0] == typ)
            C[i, :] = 1.0
            b[i] = prompt_count
        
        return C, b
    
    def _maxent_inference(self, C, b, max_iter=50):
        """Solve for Lagrange multipliers via Generalized Iterative Scaling."""
        n_constraints = C.shape[0]
        lambda_vec = np.zeros(n_constraints)
        
        for _ in range(max_iter):
            exp_term = np.exp(-C @ lambda_vec)
            Z = np.sum(exp_term)
            if Z == 0:
                break
            expectations = C @ exp_term / Z
            diff = b - expectations
            if np.linalg.norm(diff) < 1e-3:
                break
            lambda_vec += 0.1 * diff
        
        return lambda_vec
    
    def _compute_energy(self, lambda_vec, C, x_candidate):
        """Energy E = lambda^T C x."""
        return np.dot(lambda_vec, C @ x_candidate)
    
    def _compute_susceptibility(self, lambda_vec, C, x_candidate):
        """Susceptibility = variance of energy under small perturbations."""
        energies = []
        for _ in range(self.n_perturb):
            delta = np.random.uniform(-self.epsilon, self.epsilon, len(x_candidate))
            x_perturbed = np.clip(x_candidate + delta, 0, 1)
            E_perturbed = self._compute_energy(lambda_vec, C, x_perturbed)
            energies.append(E_perturbed)
        return np.var(energies) if len(energies) > 1 else 0.0
    
    def _falsification_score(self, lambda_vec, C, x_candidate, threshold=0.5):
        """Count constraints that would increase energy if flipped."""
        E_original = self._compute_energy(lambda_vec, C, x_candidate)
        count = 0
        mean_E = np.mean(np.abs(lambda_vec))
        tau = threshold * mean_E if mean_E > 0 else 0.5
        
        for i in range(len(x_candidate)):
            x_flipped = x_candidate.copy()
            x_flipped[i] = 1 - x_flipped[i]
            E_flipped = self._compute_energy(lambda_vec, C, x_flipped)
            if E_flipped - E_original > tau:
                count += 1
        
        return count
    
    def evaluate(self, prompt, candidates):
        """Rank candidates by MaxEnt energy + susceptibility + falsification."""
        prompt_literals = self._parse_literals(prompt)
        prompt_numbers = self._extract_numbers(prompt)
        
        results = []
        
        for candidate in candidates:
            cand_literals = self._parse_literals(candidate)
            cand_numbers = self._extract_numbers(candidate)
            
            # Numeric comparison (constructive computation)
            numeric_match = 0.0
            if prompt_numbers and cand_numbers:
                if any(re.search(r'\b(greater|more|larger)\b', prompt.lower())):
                    if cand_numbers and prompt_numbers and cand_numbers[0] > prompt_numbers[-1]:
                        numeric_match = 1.0
                elif any(re.search(r'\b(less|fewer|smaller)\b', prompt.lower())):
                    if cand_numbers and prompt_numbers and cand_numbers[0] < prompt_numbers[-1]:
                        numeric_match = 1.0
                else:
                    numeric_match = 1.0 if set(prompt_numbers) & set(cand_numbers) else 0.0
            
            # Build constraint matrix
            C, b = self._build_constraint_matrix(prompt_literals, cand_literals)
            
            if C.shape[0] > 0 and C.shape[1] > 0:
                lambda_vec = self._maxent_inference(C, b)
                x_cand = np.array([1.0 if any(cl[0] == pl[0] for pl in prompt_literals) else 0.0 
                                   for cl in (cand_literals or [0])]) 
                if len(x_cand) == 0:
                    x_cand = np.array([0.5] * C.shape[1])
                elif len(x_cand) < C.shape[1]:
                    x_cand = np.pad(x_cand, (0, C.shape[1] - len(x_cand)), constant_values=0.5)
                else:
                    x_cand = x_cand[:C.shape[1]]
                
                E = self._compute_energy(lambda_vec, C, x_cand)
                chi = self._compute_susceptibility(lambda_vec, C, x_cand)
                F = self._falsification_score(lambda_vec, C, x_cand)
            else:
                E, chi, F = 0.0, 0.0, 0.0
            
            # NCD tiebreaker (max 15%)
            ncd = self._compute_ncd(prompt, candidate)
            ncd_score = 1 - ncd
            
            # Structural score (60%), numeric (25%), NCD (15%)
            score = 0.6 * (-E - self.alpha * chi - self.beta * F) + 0.25 * numeric_match + 0.15 * ncd_score
            
            reasoning = f"E={E:.2f}, chi={chi:.2f}, F={F}, num={numeric_match:.2f}, ncd={ncd:.2f}"
            results.append({"candidate": candidate, "score": score, "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt, answer):
        """Return confidence 0-1, capped by meta-confidence for ambiguous prompts."""
        meta_conf = self._meta_confidence(prompt)
        
        # Evaluate answer
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.3
        
        score = results[0]["score"]
        
        # Map score to confidence (sigmoid-like)
        base_conf = 1 / (1 + np.exp(-2 * score))
        
        # Cap by meta-confidence
        final_conf = min(base_conf, meta_conf)
        
        # Never return >0.9 unless we have strong numeric match
        prompt_numbers = self._extract_numbers(prompt)
        answer_numbers = self._extract_numbers(answer)
        has_numeric = bool(prompt_numbers and answer_numbers)
        
        if not has_numeric and final_conf > 0.7:
            final_conf = 0.7
        
        return np.clip(final_conf, 0.0, 1.0)
```

</details>
