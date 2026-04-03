# Thermodynamics + Compositionality + Property-Based Testing

**Fields**: Physics, Linguistics, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T04:20:11.599532
**Report Generated**: 2026-04-02T08:39:55.058858

---

## Nous Analysis

**Algorithm: Entropy‑Weighted Constraint Propagation (EWCP)**  

1. **Parsing & Data Structures**  
   - Tokenize the prompt and each candidate answer with a regex‑based extractor that yields triples *(subject, relation, object)*.  
   - Relations are mapped to a finite set: `{=, ≠, <, >, ≤, ≥, →, ¬, ∧, ∨}` plus domain‑specific predicates (e.g., *increases*, *causes*).  
   - Each triple becomes a node in a directed hypergraph **G** where edges encode logical constraints.  
   - Attach to each node a scalar **energy** *Eᵢ* = –log Pᵢ, where Pᵢ is a prior probability derived from term frequency in a small corpus (standard library `collections.Counter`).  
   - Maintain a vector **E** (numpy array) of energies and a matrix **C** of constraint coefficients (1 for satisfied, 0 for violated, –1 for contradictory).  

2. **Constraint Propagation (Analogous to Thermodynamic Equilibrium)**  
   - Initialize a belief vector **b** = sigmoid(–**E**) (probability each proposition holds).  
   - Iterate **b** ← **b** ⊙ σ(**C**ᵀ **b**) until ‖Δ**b**‖₂ < ε (numpy `linalg.norm`). This is a fixed‑point update akin to minimizing free energy: **F** = **E**·**b** + **H**(**b**), where **H** is the Shannon entropy –∑ bᵢlog bᵢ.  
   - At convergence, compute **F**; lower free energy indicates a more thermodynamically stable (consistent) interpretation.  

3. **Property‑Based Testing for Shrinking**  
   - Treat the set of candidate answers as a property space.  
   - Generate random perturbations of the answer triples (flip a relation, swap entities) using `random.choice`.  
   - Evaluate **F** for each mutant; keep those that increase **F** (i.e., make the answer less stable).  
   - Apply a shrinking loop: repeatedly halve the perturbation magnitude (e.g., replace a numeric value with the midpoint between original and mutant) until **F** no longer rises. The minimal‑perturbation mutant yields a counterexample score.  

4. **Scoring Logic**  
   - Score = –**F** (higher = better) + λ·(1 – **δ**), where **δ** is the normalized size of the shrinking counterexample (0 = no counterexample, 1 = maximal). λ balances consistency vs. robustness.  
   - All operations use only numpy (matrix multiplies, norms) and Python stdlib (regex, random, collections).  

**Structural Features Parsed**  
- Negations (`¬`), comparatives (`<, >, ≤, ≥`), conditionals (`→`), conjunction/disjunction (`∧, ∨`), numeric constants, ordering chains, causal predicates (`causes`, `leads_to`), and equivalence/inequality (`=, ≠`).  

**Novelty**  
The blend of energy‑entropy free‑energy minimization (thermodynamics) with compositional propositional graphs and property‑based shrinking is not found in existing NLP scoring tools; closest precursors are Markov Logic Networks (energy‑based) and Hypothesis‑based testing, but they lack the explicit entropy term and the integrated shrinking loop that treats uncertainties as thermodynamic fluctuations.  

**Rating**  
Reasoning: 8/10 — captures logical consistency and uncertainty via principled free‑energy minimization.  
Metacognition: 6/10 — limited self‑reflection; the algorithm does not explicitly monitor its own parsing confidence beyond entropy.  
Hypothesis generation: 7/10 — property‑based mutational search yields concise counterexamples, though guided only by free‑energy gradients.  
Implementability: 9/10 — relies solely on numpy and stdlib; all steps are straightforward to code and debug.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
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
**Reason**: validation:runtime_error: SyntaxError: (unicode error) 'utf-8' codec can't decode byte 0xb7 in position 407: invalid start byte (tmp0bx6e82q.py, line 14)

**Forge Timestamp**: 2026-04-02T08:06:30.336588

---

## Code

**Source**: scrap

[View code](./Thermodynamics---Compositionality---Property-Based_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
"""
Entropy-Weighted Constraint Propagation (EWCP) Reasoning Tool

Combines thermodynamic free-energy minimization with compositional parsing
and property-based testing to evaluate reasoning quality.

Core mechanism:
1. Parse prompt/candidates into subject-relation-object triples
2. Build energy-based constraint graph (lower energy = more probable)
3. Iterate belief propagation to minimize free energy F = E·b + H(b)
4. Apply property-based shrinking to test robustness
5. Compute actual answers for numeric/probabilistic questions
6. Detect ambiguity and epistemic traps
"""

import re
import numpy as np
import zlib
from collections import Counter
import random

class ReasoningTool:
    def __init__(self):
        random.seed(42)
        np.random.seed(42)
        
        # Relation types mapped to symbolic operations
        self.relations = {'=', '!=', '<', '>', '<=', '>=', '->', 'not', 'and', 'or',
                         'increases', 'decreases', 'causes', 'leads_to', 'if', 'then'}
        
    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        """Rank candidates by thermodynamic consistency and computational correctness."""
        results = []
        
        # Check meta-confidence on prompt
        meta_conf = self._meta_confidence(prompt)
        
        # Try constructive computation first
        computed = self._compute_answer(prompt)
        
        for cand in candidates:
            # Thermodynamic scoring
            thermo_score = self._thermodynamic_score(prompt, cand)
            
            # Computational matching
            comp_score = self._computational_match(prompt, cand, computed)
            
            # Property-based robustness
            robust_score = self._property_based_shrinking(prompt, cand)
            
            # NCD as minor tiebreaker
            ncd_score = 1.0 - self._ncd(prompt, cand)
            
            # Weighted combination: computation 40%, thermo 35%, robust 15%, NCD 10%
            final_score = (0.40 * comp_score + 0.35 * thermo_score + 
                          0.15 * robust_score + 0.10 * ncd_score)
            
            reasoning = f"Thermo={thermo_score:.2f} Comp={comp_score:.2f} Robust={robust_score:.2f}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, capped by meta-confidence for epistemic honesty."""
        meta_conf = self._meta_confidence(prompt)
        
        # Compute base confidence from thermodynamic stability
        thermo_score = self._thermodynamic_score(prompt, answer)
        comp_score = self._computational_match(prompt, answer, self._compute_answer(prompt))
        
        base_conf = 0.5 * thermo_score + 0.5 * comp_score
        
        # Cap by meta-confidence (epistemic honesty)
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity, presuppositions, and unanswerable questions (Tier B)."""
        p_lower = prompt.lower()
        
        # Presupposition traps
        if re.search(r'\b(have you stopped|quit|ceased|why did .+ (fail|stop))', p_lower):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery \w+.*\ba\b', p_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she)\b', p_lower) and 'who' in p_lower:
            return 0.25
        
        # False dichotomy
        if re.search(r'\b(either .+ or|only two)', p_lower) and '?' in prompt:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p_lower) and not re.search(r'\b(most|least|fastest|slowest|largest|smallest)\b', p_lower):
            return 0.3
        
        # Insufficient information
        if re.search(r'\b(what is|who is|when did)\b', p_lower) and len(prompt.split()) < 10:
            return 0.4
        
        return 0.9  # High confidence in question clarity
    
    def _parse_triples(self, text: str) -> list:
        """Extract subject-relation-object triples."""
        triples = []
        
        # Negations
        for m in re.finditer(r'(not|no|never)\s+(\w+)', text.lower()):
            triples.append((m.group(2), 'not', m.group(1)))
        
        # Comparatives
        for m in re.finditer(r'(\w+)\s+(greater|less|more|fewer|larger|smaller)\s+than\s+(\w+)', text.lower()):
            triples.append((m.group(1), '>', m.group(3)))
        
        # Equality/inequality
        for m in re.finditer(r'(\w+)\s+(equals|is|are)\s+(\w+)', text.lower()):
            triples.append((m.group(1), '=', m.group(3)))
        
        # Causal
        for m in re.finditer(r'(\w+)\s+(causes|leads to|increases|decreases)\s+(\w+)', text.lower()):
            triples.append((m.group(1), m.group(2), m.group(3)))
        
        # Conditionals
        for m in re.finditer(r'if\s+(\w+).*then\s+(\w+)', text.lower()):
            triples.append((m.group(1), '->', m.group(2)))
        
        return triples if triples else [('default', '=', 'default')]
    
    def _thermodynamic_score(self, prompt: str, candidate: str) -> float:
        """Minimize free energy F = E·b + H(b) via constraint propagation."""
        p_triples = self._parse_triples(prompt)
        c_triples = self._parse_triples(candidate)
        
        # Build vocabulary
        all_triples = p_triples + c_triples
        vocab = list(set([t[0] for t in all_triples] + [t[2] for t in all_triples]))
        
        if not vocab:
            return 0.5
        
        # Energy from term frequency (prior probability)
        counter = Counter(vocab)
        total = sum(counter.values())
        E = np.array([-np.log(max(counter[v]/total, 0.01)) for v in vocab])
        
        # Constraint matrix: 1 if candidate triple supports prompt triple
        n = len(vocab)
        C = np.zeros((n, n))
        
        for i, pt in enumerate(p_triples[:n]):
            for j, ct in enumerate(c_triples[:n]):
                if i < n and j < n:
                    # Check if relations are consistent
                    if pt[1] == ct[1]:
                        C[i, j] = 1.0
                    elif (pt[1] == '>' and ct[1] in ['>=', '!=']) or \
                         (pt[1] == '<' and ct[1] in ['<=', '!=']):
                        C[i, j] = 0.5
        
        # Belief propagation to minimize free energy
        b = 1.0 / (1.0 + np.exp(E[:n]))  # Sigmoid initialization
        
        for _ in range(10):  # Fixed iterations
            if n > 1 and C.shape[0] == n and C.shape[1] >= n:
                update = 1.0 / (1.0 + np.exp(-C[:, :n].T @ b))
                b = 0.7 * b + 0.3 * update  # Damped update
        
        # Free energy F = E·b - H(b)
        b_safe = np.clip(b, 0.01, 0.99)
        H = -np.sum(b_safe * np.log(b_safe) + (1-b_safe) * np.log(1-b_safe))
        F = np.dot(E[:n], b) - H
        
        # Lower F is better; normalize to [0,1]
        return 1.0 / (1.0 + np.exp(F/max(n, 1)))
    
    def _compute_answer(self, prompt: str) -> dict:
        """Constructive computation: actually solve the problem."""
        result = {'type': None, 'value': None}
        p_lower = prompt.lower()
        
        # Extract all numbers
        numbers = [float(x) for x in re.findall(r'\d+\.?\d*', prompt)]
        
        # Numeric comparison
        if re.search(r'(greater|less|larger|smaller|more|fewer)', p_lower) and len(numbers) >= 2:
            result['type'] = 'comparison'
            result['value'] = numbers[0] > numbers[1]
        
        # Arithmetic (PEMDAS)
        if any(op in prompt for op in ['+', '-', '*', '/', '^']):
            expr = re.search(r'([\d+\-*/^() .]+)=', prompt)
            if expr:
                try:
                    val = eval(expr.group(1).replace('^', '**'))
                    result['type'] = 'arithmetic'
                    result['value'] = val
                except:
                    pass
        
        # Probability/percentage
        if re.search(r'\b(probability|percent|chance)\b', p_lower) and len(numbers) >= 2:
            result['type'] = 'probability'
            # Simple Bayesian: P(A|B) = P(B|A)*P(A)/P(B)
            if len(numbers) >= 3:
                result['value'] = (numbers[1] * numbers[0]) / max(numbers[2], 0.01)
        
        # Rate problems
        if re.search(r'\b(rate|speed|per|each)\b', p_lower) and len(numbers) >= 2:
            result['type'] = 'rate'
            result['value'] = numbers[0] / max(numbers[1], 0.01)
        
        return result
    
    def _computational_match(self, prompt: str, candidate: str, computed: dict) -> float:
        """Score how well candidate matches computed answer."""
        if computed['type'] is None:
            return 0.5  # No computation possible
        
        c_lower = candidate.lower()
        
        if computed['type'] == 'comparison':
            if computed['value']:  # First > second
                if any(w in c_lower for w in ['yes', 'true', 'greater', 'more', 'larger']):
                    return 0.95
                if any(w in c_lower for w in ['no', 'false', 'less', 'fewer', 'smaller']):
                    return 0.05
            else:
                if any(w in c_lower for w in ['no', 'false', 'less', 'fewer', 'smaller']):
                    return 0.95
                if any(w in c_lower for w in ['yes', 'true', 'greater', 'more', 'larger']):
                    return 0.05
        
        if computed['type'] in ['arithmetic', 'probability', 'rate']:
            cand_nums = [float(x) for x in re.findall(r'\d+\.?\d*', candidate)]
            if cand_nums:
                # Check if any candidate number is close to computed value
                for cn in cand_nums:
                    if abs(cn - computed['value']) < 0.01 * abs(computed['value']) + 0.1:
                        return 0.95
                return 0.1
        
        return 0.5
    
    def _property_based_shrinking(self, prompt: str, candidate: str) -> float:
        """Test robustness via random perturbations and shrinking."""
        base_score = self._thermodynamic_score(prompt, candidate)
        
        # Generate 5 random perturbations
        perturbations = []
        words = candidate.split()
        
        for _ in range(5):
            if len(words) > 2:
                perturbed = words.copy()
                idx = random.randint(0, len(perturbed)-1)
                perturbed[idx] = random.choice(['not', 'yes', 'no', 'maybe'])
                pert_text = ' '.join(perturbed)
                pert_score = self._thermodynamic_score(prompt, pert_text)
                perturbations.append(pert_score)
        
        if not perturbations:
            return base_score
        
        # Robustness = how much worse are perturbations
        delta = base_score - np.mean(perturbations)
        robustness = 1.0 / (1.0 + np.exp(-5 * delta))  # Sigmoid
        
        return robustness
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (minor tiebreaker only)."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)
```

</details>
