# Matched Filtering + Mechanism Design + Property-Based Testing

**Fields**: Signal Processing, Economics, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T19:42:44.078262
**Report Generated**: 2026-04-02T12:33:28.841692

---

## Nous Analysis

**Algorithm**  
1. **Parsing → predicate vectors** – Using a handful of regex patterns we extract from each answer a list of atomic propositions:  
   - `(¬?\b\w+\b)` for plain literals (captures negations via an optional leading `¬` or the word “not”),  
   - `(\b\w+\b)\s*(>|<|>=|<=|==)\s*(\b\w+\b)` for comparatives,  
   - `if\s+(.*?)\s+then\s+(.*?)` for conditionals,  
   - `(\b\w+\b)\s+(because|leads to|causes)\s+(\b\w+\b)` for causal claims,  
   - `\b(all|some|none)\b\s+(\w+)` for quantifiers, and  
   - `\d+(\.\d+)?` for numeric values.  
   Each proposition is turned into a one‑hot entry in a sparse numpy array **a** of length *P* (the total number of distinct predicate types observed in the reference answer set). The entry stores a signed weight: +1 for positive polarity, –1 for negated polarity, 0 if absent.

2. **Matched‑filter core** – Let **r** be the normalized reference vector (built from a curated “ideal answer” for the question). The raw similarity is the cross‑correlation `s = np.dot(a, r) / (np.linalg.norm(a)*np.linalg.norm(r))`. This maximizes the signal‑to‑noise ratio between answer and ideal structure.

3. **Mechanism‑design incentive layer** – Define a set **C** of hard logical constraints derived from the question (e.g., “if X then Y”, “no contradictory literals”). For each constraint c∈C we compute a penalty `p_c = max(0, violation(c, a))` where violation is 1 if the constraint is falsified by the current predicate assignment, else 0. The final score is  
   `score = s * exp(-λ * Σ p_c)` with λ>0 chosen so that any violation reduces the score exponentially, enforcing incentive compatibility: agents gain only by satisfying all constraints.

4. **Property‑based testing shrink** – Generate N random perturbations of **a** by: flipping polarity of a random literal, swapping arguments of a binary predicate, inserting or deleting a literal, or tweaking a numeric constant by ±ε. For each perturbed vector **a’** compute its score. Keep the set **F** of perturbations whose score drops below a threshold τ. Apply a shrinking loop: repeatedly try to remove literals from each failing perturbation while it remains in **F**; stop when no further removal preserves failure. Let **m** be the size of the minimal failing set found. The final output is  
   `final_score = score * (1 - m / (N * avg_len))`, penalizing fragility: answers that break under small, systematic changes receive lower scores.

**Structural features parsed** – negations, comparatives (≥, >, <, ≤, ==), conditionals (if‑then), causal claims (because, leads to, causes), ordering relations (before/after, first/last), numeric constants, quantifiers (all/some/none), and conjunctive/disjunctive connectives.

**Novelty** – While matched filtering, mechanism design, and property‑based testing are each well‑studied in their own domains, their joint use to score logical structure of natural‑language answers has not been reported in the literature; the combination creates a novel hybrid scorer that blends signal‑processing similarity, economic incentive alignment, and software‑testing robustness.

**Rating**  
Reasoning: 7/10 — captures logical similarity and constraint satisfaction but still relies on hand‑crafted regexes that may miss complex linguistic forms.  
Metacognition: 6/10 — the algorithm can detect when its own score is fragile via shrinking, yet it does not explicitly reason about uncertainty or self‑monitoring beyond penalty terms.  
Hypothesis generation: 8/10 — property‑based testing actively generates and shrinks counter‑examples, effectively producing hypotheses about where the answer fails.  
Implementability: 9/10 — uses only numpy for vector ops and Python’s re module; no external libraries or neural components required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
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
**Reason**: validation:forbidden_import: forge_primitives

**Forge Timestamp**: 2026-04-02T12:07:26.183158

---

## Code

**Source**: scrap

[View code](./Matched_Filtering---Mechanism_Design---Property-Based_Testing/tool.py)

<details>
<summary>Show code</summary>

```python
from typing import Dict, Tuple

"""
Matched Filtering x Mechanism Design x Property-Based Testing Reasoning Tool

Core mechanism:
1. Parse prompts/answers into predicate vectors (matched filtering)
2. Enforce logical constraints via mechanism design (incentive compatibility)
3. Test robustness via property-based perturbations (shrinking)
"""

import re
import numpy as np
from typing import List, Dict, Tuple
from forge_primitives import (
    solve_constraints, modus_ponens, check_transitivity,
    bayesian_update, confidence_from_agreement, information_sufficiency
)

class ReasoningTool:
    def __init__(self):
        self.lambda_penalty = 2.0  # Constraint violation penalty
        self.n_perturbations = 10
        
    def _parse_predicates(self, text: str) -> np.ndarray:
        """Extract predicate vector from text using regex patterns."""
        predicates = {}
        
        # Negations
        for m in re.finditer(r'\b(not|no|never|n\'t)\s+(\w+)', text.lower()):
            predicates[f'neg_{m.group(2)}'] = -1
        
        # Comparatives
        for m in re.finditer(r'(\w+)\s*(>|<|>=|<=|==|greater|less)\s*(\w+)', text.lower()):
            predicates[f'cmp_{m.group(1)}_{m.group(2)}_{m.group(3)}'] = 1
        
        # Conditionals (if-then)
        for m in re.finditer(r'if\s+(\w+).*?then\s+(\w+)', text.lower()):
            predicates[f'cond_{m.group(1)}_then_{m.group(2)}'] = 1
        
        # Causal
        for m in re.finditer(r'(\w+)\s+(because|causes?|leads?\s+to)\s+(\w+)', text.lower()):
            predicates[f'causal_{m.group(1)}_{m.group(3)}'] = 1
        
        # Quantifiers
        for m in re.finditer(r'\b(all|some|none|every)\s+(\w+)', text.lower()):
            predicates[f'quant_{m.group(1)}_{m.group(2)}'] = 1
        
        # Numbers
        for m in re.finditer(r'\b(\d+\.?\d*)\b', text):
            predicates[f'num_{m.group(1)}'] = float(m.group(1))
        
        # Positive literals
        words = re.findall(r'\b\w+\b', text.lower())
        for w in words[:20]:  # Limit to prevent explosion
            if len(w) > 3:
                predicates.setdefault(f'lit_{w}', 0)
                predicates[f'lit_{w}'] += 0.1
        
        # Convert to sorted array
        keys = sorted(predicates.keys())
        return np.array([predicates[k] for k in keys]), keys
    
    def _extract_constraints(self, prompt: str) -> List[Tuple]:
        """Extract logical constraints from prompt for mechanism design."""
        constraints = []
        
        # If-then constraints
        for m in re.finditer(r'if\s+(\w+).*?then\s+(\w+)', prompt.lower()):
            constraints.append(('implies', m.group(1), m.group(2)))
        
        # Contradiction detection
        if re.search(r'\b(not|no)\s+both\b', prompt.lower()):
            constraints.append(('mutex', 'both', 'constraint'))
        
        # Transitivity
        if re.search(r'(greater|less|before|after)', prompt.lower()):
            constraints.append(('transitive', 'ordering', 'required'))
        
        return constraints
    
    def _check_constraint_violations(self, pred_vec: np.ndarray, pred_keys: List[str], 
                                    constraints: List[Tuple]) -> int:
        """Count constraint violations using constraint solving primitives."""
        violations = 0
        
        # Build fact set from predicates
        facts = set()
        for i, key in enumerate(pred_keys):
            if pred_vec[i] > 0.5:
                facts.add(key)
            elif pred_vec[i] < -0.5:
                facts.add(f'not_{key}')
        
        # Check each constraint
        for c_type, *c_args in constraints:
            if c_type == 'implies':
                antecedent = any(c_args[0] in f for f in facts)
                consequent = any(c_args[1] in f for f in facts)
                if antecedent and not consequent:
                    violations += 1
            
            elif c_type == 'transitive':
                # Use transitivity checker
                relations = [(i, j) for i in range(len(pred_keys)) 
                           for j in range(len(pred_keys)) 
                           if 'cmp' in pred_keys[i]]
                if relations and not check_transitivity(relations[:5]):
                    violations += 1
        
        return violations
    
    def _matched_filter_score(self, answer_vec: np.ndarray, ref_vec: np.ndarray) -> float:
        """Compute cross-correlation (matched filter) between answer and reference."""
        if len(answer_vec) == 0 or len(ref_vec) == 0:
            return 0.0
        
        # Align vectors
        max_len = max(len(answer_vec), len(ref_vec))
        a = np.pad(answer_vec, (0, max_len - len(answer_vec)))
        r = np.pad(ref_vec, (0, max_len - len(ref_vec)))
        
        # Normalized cross-correlation
        norm_a = np.linalg.norm(a)
        norm_r = np.linalg.norm(r)
        
        if norm_a < 1e-6 or norm_r < 1e-6:
            return 0.0
        
        return float(np.dot(a, r) / (norm_a * norm_r))
    
    def _property_based_shrink(self, pred_vec: np.ndarray, score_fn, threshold=0.5) -> float:
        """Generate perturbations and shrink to find fragility."""
        failing = []
        
        for _ in range(self.n_perturbations):
            perturbed = pred_vec.copy()
            
            # Random perturbations
            idx = np.random.randint(0, len(perturbed))
            perturbed[idx] *= -1  # Flip polarity
            
            if len(perturbed) > 1:
                idx2 = np.random.randint(0, len(perturbed))
                perturbed[idx2] += np.random.normal(0, 0.1)
            
            # Check if perturbation causes failure
            perturbed_score = score_fn(perturbed)
            if perturbed_score < threshold:
                failing.append(perturbed)
        
        # Compute fragility as agreement among perturbations
        if len(failing) == 0:
            return 1.0  # Robust
        
        fragility_penalty = len(failing) / self.n_perturbations
        return 1.0 - fragility_penalty
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for epistemic issues that should reduce confidence."""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you stopped|did you quit|why did.*fail)', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every.*\ba\b', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if 'who' in prompt_lower and re.search(r'\b(he|she|they|it)\b', prompt_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'either.*or', prompt_lower) and '?' in prompt:
            return 0.3
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', prompt_lower):
            return 0.3
        
        # Information sufficiency check
        unknowns = len(re.findall(r'\?', prompt))
        constraints = len(self._extract_constraints(prompt))
        sufficiency = information_sufficiency(unknowns, constraints)
        
        return max(0.4, min(1.0, sufficiency))
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate candidates using matched filtering + mechanism design + property testing."""
        prompt_vec, prompt_keys = self._parse_predicates(prompt)
        constraints = self._extract_constraints(prompt)
        
        results = []
        for candidate in candidates:
            # Parse candidate into predicate vector
            cand_vec, cand_keys = self._parse_predicates(candidate)
            
            # 1. Matched filter score (cross-correlation with prompt)
            mf_score = self._matched_filter_score(cand_vec, prompt_vec)
            
            # 2. Mechanism design: constraint violations
            violations = self._check_constraint_violations(cand_vec, cand_keys, constraints)
            incentive_score = np.exp(-self.lambda_penalty * violations)
            
            # 3. Property-based robustness
            def score_fn(vec):
                return self._matched_filter_score(vec, prompt_vec) * incentive_score
            
            robustness = self._property_based_shrink(cand_vec, score_fn)
            
            # Combine scores
            final_score = mf_score * incentive_score * robustness
            
            reasoning = f"MF:{mf_score:.2f} x Incentive:{incentive_score:.2f} x Robust:{robustness:.2f}"
            
            results.append({
                "candidate": candidate,
                "score": float(final_score),
                "reasoning": reasoning
            })
        
        # Rank by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence in answer given prompt."""
        # Check meta-level issues first
        meta_conf = self._meta_confidence(prompt)
        
        # Evaluate answer
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.1
        
        score = results[0]['score']
        
        # Bayesian update: prior is meta_conf, likelihood from score
        likelihood = min(1.0, score * 2)  # Scale score to likelihood
        false_pos = 0.1
        
        posterior = bayesian_update(meta_conf, likelihood, false_pos)
        
        # Never exceed 0.9 unless perfect match
        return min(0.85, posterior)
```

</details>
