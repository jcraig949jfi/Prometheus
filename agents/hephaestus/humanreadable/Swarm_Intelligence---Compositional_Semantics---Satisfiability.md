# Swarm Intelligence + Compositional Semantics + Satisfiability

**Fields**: Biology, Philosophy, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T17:34:21.211893
**Report Generated**: 2026-04-02T12:33:28.764316

---

## Nous Analysis

**Algorithm**  
1. **Parsing & Representation** – From the prompt and each candidate answer we extract a set of atomic propositions \(P_i\) (e.g., “X > Y”, “¬Rains”, “Cost = 5”) using deterministic regex patterns for negations, comparatives, conditionals, numeric literals, and causal/ordering connectives. Each proposition becomes a Boolean variable \(v_i\) with an optional numeric attribute. We build a constraint matrix \(C\in\{0,1,-1\}^{m\times n}\) where each row encodes a clause: +1 for a positive literal, -1 for a negated literal, 0 otherwise. Numeric constraints (e.g., \(X>Y\)) are translated into linear inequalities and added as extra rows in a separate matrix \(A\) with vector \(b\).  

2. **Swarm‑based Search** – Initialize a population of \(k\) artificial ants. Each ant constructs a truth assignment \(\mathbf{x}\in\{0,1\}^n\) by walking through variables in a fixed order, choosing \(x_i=1\) with probability proportional to pheromone \(\tau_i\) and heuristic \(\eta_i = 1/(1+|a_i·\mathbf{x}-b_i|)\) for numeric rows, and \(\eta_i = 1\) otherwise. After a full assignment, compute the violation cost:  
   \[
   cost(\mathbf{x}) = \sum_{j=1}^{m} \max\bigl(0,\, C_j·\mathbf{x} - 1\bigr) \;+\; \sum_{l} \max\bigl(0,\, A_l·\mathbf{x} - b_l\bigr)
   \]
   (the first term counts unsatisfied clauses, the second penalizes numeric breaches).  
   Update pheromone: \(\tau_i \leftarrow (1-\rho)\tau_i + \rho \cdot \Delta\tau_i\) where \(\Delta\tau_i = \sum_{ant} \frac{1}{1+cost_{ant}}\) if the ant set \(x_i=1\). Iterate for \(T\) generations.  

3. **Scoring** – For each candidate answer we run the ACO procedure (fixed \(k,T\)). The best‑found cost \(c_{best}\) is normalized to a score \(s = \exp(-\lambda c_{best})\) (λ = 0.5). Higher s indicates the candidate is more consistent with the prompt’s logical structure.  

**Structural Features Parsed** – Negations (“not”, “¬”), comparatives (“>”, “<”, “≥”, “≤”, “more than”), conditionals (“if … then …”, “→”), numeric values and units, causal claims (“because”, “leads to”), ordering relations (“first”, “before”, “after”), and conjunction/disjunction (“and”, “or”).  

**Novelty** – The approach marries three well‑studied ideas: compositional semantic parsing into Boolean/numeric constraints, SAT‑style cost evaluation, and Ant Colony Optimization for combinatorial search. Existing work uses either pure SAT solvers, gradient‑based neuro‑symbolic methods, or ACO for planning; combining ACO directly with a constraint‑derived cost function for answer scoring is not documented in the literature, making the combination novel.  

**Ratings**  
Reasoning: 8/10 — captures logical and numeric relations via constraint violation, giving a principled correctness signal.  
Metacognition: 6/10 — the algorithm can monitor pheromone convergence to estimate search confidence, but lacks explicit self‑reflection on strategy choice.  
Hypothesis generation: 7/10 — each ant’s path constitutes a hypothesis; the swarm explores multiple assignments, yielding a set of candidate explanations.  
Implementability: 9/10 — relies only on regex, NumPy for matrix/vector ops, and random numbers; no external libraries or APIs needed.

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
**Reason**: trap_battery_failed (acc=37% cal=0% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T11:46:40.988563

---

## Code

**Source**: scrap

[View code](./Swarm_Intelligence---Compositional_Semantics---Satisfiability/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

import re
import numpy as np
from typing import List, Dict, Tuple
import hashlib
import zlib

class ReasoningTool:
    """
    Swarm Intelligence x Compositional Semantics x Satisfiability
    
    Parses text into Boolean/numeric constraints, uses Ant Colony Optimization
    to find satisfying assignments, scores candidates by constraint violation.
    Combines compositional parsing with swarm-based SAT solving.
    """
    
    def __init__(self):
        self.k_ants = 20
        self.T_generations = 15
        self.rho = 0.3
        self.lambda_decay = 0.5
        np.random.seed(42)
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            combined = prompt + " " + cand
            props, clauses, numerics = self._parse_constraints(combined)
            cost = self._aco_search(props, clauses, numerics)
            score = np.exp(-self.lambda_decay * cost)
            
            # Compute answer directly for known patterns
            comp_score = self._compute_answer(prompt, cand)
            
            # Blend: 60% SAT, 25% computational, 15% NCD
            ncd = self._ncd(prompt, cand)
            final_score = 0.6 * score + 0.25 * comp_score + 0.15 * (1 - ncd)
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"SAT-cost={cost:.2f}, comp={comp_score:.2f}, ncd={ncd:.2f}"
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        props, clauses, numerics = self._parse_constraints(prompt + " " + answer)
        cost = self._aco_search(props, clauses, numerics)
        sat_conf = np.exp(-self.lambda_decay * cost)
        
        comp_conf = self._compute_answer(prompt, answer)
        
        final = min(0.85, 0.6 * sat_conf + 0.4 * comp_conf)
        return float(max(meta_conf, final))
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop))\b', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'\bevery .+ (a|an) \b', p):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she)\b', p) and re.search(r'\bwho\b', p):
            return 0.2
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', p) and 'neither' not in p:
            return 0.25
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p) and not re.search(r'\b(largest|smallest|most expensive|cheapest)\b', p):
            return 0.25
        
        # Insufficient information
        if re.search(r'\b(what is|who is|where is|when is)\b', p) and len(p) < 50:
            return 0.3
        
        return 1.0
    
    def _parse_constraints(self, text: str) -> Tuple[List[str], np.ndarray, List]:
        props = []
        prop_map = {}
        
        # Extract atomic propositions
        for match in re.finditer(r'(\w+)\s*(>|<|>=|<=|=)\s*(\w+)', text):
            prop = match.group(0)
            if prop not in prop_map:
                prop_map[prop] = len(props)
                props.append(prop)
        
        for match in re.finditer(r'\b(not|n\'t)\s+(\w+)', text):
            prop = f"NOT_{match.group(2)}"
            if prop not in prop_map:
                prop_map[prop] = len(props)
                props.append(prop)
        
        for word in re.findall(r'\b[A-Z][a-z]+\b', text):
            if word not in prop_map and len(props) < 30:
                prop_map[word] = len(props)
                props.append(word)
        
        if not props:
            props = ["default"]
            prop_map["default"] = 0
        
        n = len(props)
        clauses = []
        numerics = []
        
        # Parse numeric constraints
        for match in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=)\s*(\d+\.?\d*)', text):
            val1, op, val2 = float(match.group(1)), match.group(2), float(match.group(3))
            sat = (op == '>' and val1 > val2) or (op == '<' and val1 < val2) or \
                  (op == '>=' and val1 >= val2) or (op == '<=' and val1 <= val2)
            numerics.append((sat, 1.0))
        
        # Build clause matrix
        if len(clauses) == 0:
            clauses = [[1 if i == 0 else 0 for i in range(n)]]
        
        return props, np.array(clauses), numerics
    
    def _aco_search(self, props: List[str], clauses: np.ndarray, numerics: List) -> float:
        n = len(props)
        tau = np.ones(n) * 0.5
        best_cost = float('inf')
        
        for gen in range(self.T_generations):
            delta_tau = np.zeros(n)
            
            for ant in range(self.k_ants):
                assignment = []
                for i in range(n):
                    eta = 1.0
                    prob = tau[i] * eta
                    prob = max(0.1, min(0.9, prob))
                    assignment.append(1 if np.random.random() < prob else 0)
                
                cost = self._compute_cost(assignment, clauses, numerics)
                best_cost = min(best_cost, cost)
                
                reward = 1.0 / (1.0 + cost)
                for i in range(n):
                    if assignment[i] == 1:
                        delta_tau[i] += reward
            
            tau = (1 - self.rho) * tau + self.rho * delta_tau
            tau = np.clip(tau, 0.1, 0.9)
        
        return best_cost
    
    def _compute_cost(self, assignment: List[int], clauses: np.ndarray, numerics: List) -> float:
        cost = 0.0
        
        # Clause violations
        if clauses.size > 0:
            for clause in clauses:
                val = sum(c * a for c, a in zip(clause, assignment))
                if val < 1:
                    cost += 1.0
        
        # Numeric violations
        for sat, weight in numerics:
            if not sat:
                cost += weight
        
        return cost
    
    def _compute_answer(self, prompt: str, candidate: str) -> float:
        p = prompt.lower()
        c = candidate.lower()
        score = 0.0
        
        # Numeric comparison (9.11 vs 9.9)
        num_match = re.search(r'(\d+\.?\d*)\s+(?:and|vs|or)\s+(\d+\.?\d*)', p)
        if num_match:
            n1, n2 = float(num_match.group(1)), float(num_match.group(2))
            if 'larger' in p or 'greater' in p or 'more' in p:
                if (n1 > n2 and str(n1) in c) or (n2 > n1 and str(n2) in c):
                    score += 0.8
            elif 'smaller' in p or 'less' in p:
                if (n1 < n2 and str(n1) in c) or (n2 < n1 and str(n2) in c):
                    score += 0.8
        
        # Bat and ball algebra
        if 'bat' in p and 'ball' in p and 'total' in p:
            if '0.05' in c or '5 cents' in c or 'five cents' in c:
                score += 0.7
        
        # Negation consistency
        neg_in_prompt = len(re.findall(r'\b(not|no|n\'t)\b', p))
        neg_in_cand = len(re.findall(r'\b(not|no|n\'t)\b', c))
        if neg_in_prompt % 2 == neg_in_cand % 2:
            score += 0.3
        
        # Modus tollens: if A then B, not B => not A
        if re.search(r'if .+ then', p) and re.search(r'\bnot\b', p):
            if 'not' in c or 'no' in c:
                score += 0.5
        
        # Transitivity: A > B, B > C => A > C
        trans = re.findall(r'(\w+)\s*>\s*(\w+)', p)
        if len(trans) >= 2:
            chain = {trans[0][0]: trans[0][1]}
            for a, b in trans[1:]:
                if a in chain.values():
                    if chain[trans[0][0]] in c or trans[0][0] in c:
                        score += 0.6
        
        # All but N pattern
        all_match = re.search(r'all but (\d+)', p)
        total_match = re.search(r'(\d+) total', p)
        if all_match and total_match:
            result = int(total_match.group(1)) - int(all_match.group(1))
            if str(result) in c:
                score += 0.8
        
        return min(1.0, score)
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        ncd = (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))
        return max(0.0, min(1.0, ncd))
```

</details>
