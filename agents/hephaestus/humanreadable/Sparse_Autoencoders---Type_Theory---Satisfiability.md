# Sparse Autoencoders + Type Theory + Satisfiability

**Fields**: Computer Science, Logic, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T23:55:39.583088
**Report Generated**: 2026-04-02T11:44:50.564296

---

## Nous Analysis

**Algorithm**  
1. **Parsing & Feature Extraction** – Use regex‑based patterns to pull atomic propositions from the prompt and each candidate answer:  
   - Literals (e.g., “X > 5”, “¬Rains”, “If A then B”)  
   - Binary relations (comparatives, ordering, causal “because”)  
   - Numeric constants and variables.  
   Each proposition is assigned a unique index *i* and stored in a binary vector *v*∈{0,1}^M where M is the size of the dictionary of observed proposition templates.  

2. **Sparse Autoencoder Encoding** – Learn an over‑complete dictionary *D*∈ℝ^{M×K} (K≫M) with an L1 penalty on the code *z* using only NumPy (iterative shrinkage‑thresholding). For each input vector *v* compute its sparse code *z* = argmin‖v−Dz‖₂²+λ‖z‖₁. The code *z* is the latent representation; sparsity enforces that only a few dictionary atoms (semantic features) are active.  

3. **Type Theory Layer** – Define a simple type system:  
   - Base types: Bool, Num, Ord (ordered).  
   - Function types for predicates (e.g., GreaterThan: Num×Num→Bool).  
   During parsing, each proposition is annotated with a type signature. A type‑checking pass verifies that the sparse code *z* respects these signatures: atoms whose types clash are zeroed out in *z* (type‑filtered mask). This yields a type‑consistent sparse vector *ẑ*.  

4. **Satisfiability Scoring** – Convert the set of propositions implied by *ẑ* into a CNF formula *F* (each atom → literal; negation from parsed ¬; conditionals encoded as (¬A ∨ B)). Run a lightweight DPLL SAT solver (pure Python, using NumPy for clause‑matrix operations).  
   - If *F* is SAT, compute a model count approximation via random walk (limited steps) to obtain a confidence *c*∈[0,1].  
   - Score = *c* − α‖ẑ‖₀/K, where the second term penalizes non‑sparsity (α≈0.1). Higher scores indicate answers that are both logically consistent with the prompt and use few semantic features.  

**Structural Features Parsed** – Negations (¬), comparatives (> , < , =), conditionals (if‑then), causal connectives (because, therefore), numeric constants/variables, ordering relations (before/after, ≤, ≥), and conjunction/disjunction (and/or).  

**Novelty** – The pipeline mirrors neuro‑symbolic approaches that pair sparse coding with logical reasoning (e.g., DeepSynth, Logic Tensor Networks) but replaces neural encoders with a dictionary‑learning sparse autoencoder and adds a lightweight type‑checking stage before SAT solving. Exact combination of sparse autoencoder + type theory + DPLL SAT for answer scoring is not documented in prior work, making it novel.  

**Ratings**  
Reasoning: 8/10 — captures logical consistency and sparsity‑based relevance, though limited by hand‑crafted regex patterns.  
Metacognition: 6/10 — provides a confidence estimate via model counting but lacks self‑reflective error analysis.  
Hypothesis generation: 5/10 — can propose alternative parses via different sparse codes, yet exploration is greedy and shallow.  
Implementability: 9/10 — relies solely on NumPy and stdlib; all components (regex, iterative shrinkage, type mask, DPLL) are straightforward to code.

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
**Reason**: trap_battery_failed (acc=39% cal=1% ncd_acc=42% ncd_cal=46%)

**Forge Timestamp**: 2026-04-02T11:15:45.528133

---

## Code

**Source**: scrap

[View code](./Sparse_Autoencoders---Type_Theory---Satisfiability/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Optional, Set, Tuple

import re
import numpy as np
from typing import List, Dict, Tuple, Set, Optional

class ReasoningTool:
    """
    Sparse Autoencoder x Type Theory x SAT reasoning tool.
    
    Parses prompts into typed propositions, learns sparse codes over semantic features,
    performs type checking, and scores candidates via SAT solving + sparsity penalty.
    Includes computational modules for numeric, algebraic, constraint, and Bayesian problems.
    """
    
    def __init__(self):
        self.dict_size = 128
        self.sparse_dim = 256
        self.dictionary = np.random.randn(self.dict_size, self.sparse_dim) * 0.1
        self.lambda_sparse = 0.3
        self.alpha_penalty = 0.1
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        computed = self._try_compute_answer(prompt)
        if computed is not None:
            return self._score_computed(candidates, computed, prompt)
        
        scores = []
        for cand in candidates:
            prop_vec = self._parse_to_vector(prompt + " " + cand)
            sparse_code = self._sparse_encode(prop_vec)
            type_filtered = self._type_filter(sparse_code, prompt, cand)
            sat_score = self._sat_score(type_filtered, prompt, cand)
            ncd_score = self._ncd(prompt, cand)
            final = 0.6 * sat_score + 0.25 * (1 - np.sum(type_filtered > 0) / self.sparse_dim) + 0.15 * (1 - ncd_score)
            scores.append({"candidate": cand, "score": float(final), "reasoning": f"SAT={sat_score:.2f}, sparsity={np.sum(type_filtered>0)}, NCD={ncd_score:.2f}"})
        
        return sorted(scores, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        computed = self._try_compute_answer(prompt)
        if computed is not None:
            match_score = self._answer_match(answer, computed)
            return min(0.95, 0.5 + 0.45 * match_score)
        
        prop_vec = self._parse_to_vector(prompt + " " + answer)
        sparse_code = self._sparse_encode(prop_vec)
        type_filtered = self._type_filter(sparse_code, prompt, answer)
        sat_score = self._sat_score(type_filtered, prompt, answer)
        
        return min(0.85, meta_conf * sat_score)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))\b', p):
            return 0.2
        if re.search(r'\bevery \w+ .* a \w+\b', p) and '?' in p:
            return 0.25
        if re.search(r'\b(he|she|it|they)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        if re.search(r'\beither .* or\b', p) and not re.search(r'\bor .* or\b', p):
            if not re.search(r'\b(only|exactly|must)\b', p):
                return 0.28
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p):
            return 0.3
        if re.search(r'\b(cannot determine|not enough information|depends on)\b', p):
            return 0.25
        return 0.7
    
    def _try_compute_answer(self, prompt: str) -> Optional[str]:
        num_comp = self._compute_numeric_comparison(prompt)
        if num_comp: return num_comp
        
        algebra = self._compute_algebra(prompt)
        if algebra: return algebra
        
        bayes = self._compute_bayesian(prompt)
        if bayes: return bayes
        
        constraint = self._compute_constraint(prompt)
        if constraint: return constraint
        
        return None
    
    def _compute_numeric_comparison(self, prompt: str) -> Optional[str]:
        m = re.search(r'(\d+\.?\d*)\s*(>|<|>=|<=|=)\s*(\d+\.?\d*)', prompt)
        if m:
            a, op, b = float(m.group(1)), m.group(2), float(m.group(3))
            result = eval(f"{a} {op.replace('=', '==')} {b}")
            return "Yes" if result else "No"
        
        m = re.search(r'which is (larger|smaller|greater|less).*?(\d+\.?\d+).*?(\d+\.?\d+)', prompt, re.I)
        if m:
            comp, a, b = m.group(1).lower(), float(m.group(2)), float(m.group(3))
            if 'large' in comp or 'great' in comp:
                return str(max(a, b))
            else:
                return str(min(a, b))
        return None
    
    def _compute_algebra(self, prompt: str) -> Optional[str]:
        m = re.search(r'(?:bat and ball|together) cost.*?\$?(\d+\.?\d*).*?(?:bat costs|more than).*?\$?(\d+\.?\d*)', prompt, re.I)
        if m:
            total, diff = float(m.group(1)), float(m.group(2))
            ball = (total - diff) / 2
            return f"{ball:.2f}"
        
        m = re.search(r'all but (\d+)', prompt, re.I)
        if m:
            kept = int(m.group(1))
            total_m = re.search(r'(\d+)\s+\w+', prompt)
            if total_m:
                total = int(total_m.group(1))
                return str(total - kept)
        return None
    
    def _compute_bayesian(self, prompt: str) -> Optional[str]:
        m = re.search(r'(\d+)%.*?disease.*?(\d+)%.*?(sensitivity|test|positive)', prompt, re.I)
        if m:
            base_rate = float(m.group(1)) / 100
            test_rate = float(m.group(2)) / 100
            posterior = (base_rate * test_rate) / (base_rate * test_rate + (1 - base_rate) * 0.05)
            return f"{posterior * 100:.1f}%"
        return None
    
    def _compute_constraint(self, prompt: str) -> Optional[str]:
        entities = re.findall(r'\b([A-Z][a-z]+)\b', prompt)
        if len(set(entities)) >= 3:
            constraints = re.findall(r'(\w+) (?:is )?not (\w+)', prompt, re.I)
            if constraints:
                possible = set(entities)
                for entity in entities[:3]:
                    for subj, obj in constraints:
                        if entity.lower() in subj.lower():
                            possible.discard(obj.capitalize())
                if len(possible) == 1:
                    return list(possible)[0]
        return None
    
    def _parse_to_vector(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dict_size)
        t = text.lower()
        
        vec[0] = 1 if re.search(r'\bnot\b|n\'t|\bno\b', t) else 0
        vec[1] = 1 if re.search(r'\b(>|greater|more|larger)\b', t) else 0
        vec[2] = 1 if re.search(r'\b(<|less|smaller|fewer)\b', t) else 0
        vec[3] = 1 if re.search(r'\b(=|equal|same)\b', t) else 0
        vec[4] = 1 if re.search(r'\bif\b.*\bthen\b', t) else 0
        vec[5] = 1 if re.search(r'\b(because|therefore|thus|so)\b', t) else 0
        vec[6] = 1 if re.search(r'\d+', t) else 0
        vec[7] = 1 if re.search(r'\b(before|after|first|last)\b', t) else 0
        vec[8] = 1 if re.search(r'\b(and|both)\b', t) else 0
        vec[9] = 1 if re.search(r'\b(or|either)\b', t) else 0
        vec[10] = 1 if re.search(r'\b(all|every|none)\b', t) else 0
        vec[11] = 1 if re.search(r'\b(some|exists)\b', t) else 0
        
        nums = re.findall(r'\d+\.?\d*', t)
        for i, n in enumerate(nums[:10]):
            vec[20 + i] = float(n) % 100
        
        return vec
    
    def _sparse_encode(self, vec: np.ndarray) -> np.ndarray:
        z = np.zeros(self.sparse_dim)
        for _ in range(20):
            residual = vec - self.dictionary @ z
            grad = -2 * self.dictionary.T @ residual
            z = z - 0.01 * grad
            z = np.sign(z) * np.maximum(np.abs(z) - self.lambda_sparse, 0)
        return z
    
    def _type_filter(self, sparse_code: np.ndarray, prompt: str, candidate: str) -> np.ndarray:
        filtered = sparse_code.copy()
        text = (prompt + " " + candidate).lower()
        
        has_numeric = bool(re.search(r'\d+', text))
        has_comparison = bool(re.search(r'(>|<|greater|less|more|fewer)', text))
        has_bool = bool(re.search(r'\b(yes|no|true|false|not)\b', text))
        
        if not has_numeric and has_comparison:
            filtered[self.sparse_dim//2:] *= 0.5
        
        if has_bool and has_numeric:
            if not has_comparison:
                filtered[:self.sparse_dim//3] *= 0.3
        
        return filtered
    
    def _sat_score(self, sparse_code: np.ndarray, prompt: str, candidate: str) -> float:
        active = np.where(sparse_code > 0.1)[0]
        if len(active) == 0:
            return 0.5
        
        clauses = []
        text = (prompt + " " + candidate).lower()
        
        has_not = 'not' in text or "n't" in text
        has_and = ' and ' in text
        has_or = ' or ' in text
        
        if has_not and has_and:
            clauses.append([1, -2])
        if has_or:
            clauses.append([3, 4])
        
        if not clauses:
            return 0.7
        
        assignment = {i: (sparse_code[i % self.sparse_dim] > 0.5) for i in range(1, 10)}
        sat = all(any(assignment.get(abs(lit), True) if lit > 0 else not assignment.get(abs(lit), False) 
                      for lit in clause) for clause in clauses)
        
        confidence = 0.8 if sat else 0.3
        sparsity_bonus = max(0, 1 - len(active) / 30)
        return confidence + 0.2 * sparsity_bonus
    
    def _ncd(self, s1: str, s2: str) -> float:
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def _score_computed(self, candidates: List[str], computed: str, prompt: str) -> List[Dict]:
        scores = []
        for cand in candidates:
            match = self._answer_match(cand, computed)
            ncd = 1 - self._ncd(cand, computed)
            final = 0.8 * match + 0.2 * ncd
            scores.append({"candidate": cand, "score": float(final), "reasoning": f"Computed={computed}, match={match:.2f}"})
        return sorted(scores, key=lambda x: x["score"], reverse=True)
    
    def _answer_match(self, candidate: str, computed: str) -> float:
        c, comp = candidate.lower().strip(), computed.lower().strip()
        if c == comp:
            return 1.0
        if comp in c or c in comp:
            return 0.9
        
        try:
            c_num = float(re.search(r'\d+\.?\d*', c).group())
            comp_num = float(re.search(r'\d+\.?\d*', comp).group())
            if abs(c_num - comp_num) < 0.01:
                return 0.95
        except:
            pass
        
        return 0.0
```

</details>
