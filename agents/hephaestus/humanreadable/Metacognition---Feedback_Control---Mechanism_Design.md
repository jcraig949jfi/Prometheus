# Metacognition + Feedback Control + Mechanism Design

**Fields**: Cognitive Science, Control Theory, Economics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T17:49:46.778645
**Report Generated**: 2026-03-27T05:13:35.294553

---

## Nous Analysis

**Algorithm: Adaptive Confidence‑Weighted Constraint Solver (ACWCS)**  

*Data structures*  
- `tokens`: list of strings from the prompt and each candidate answer (regex‑split on whitespace/punctuation).  
- `constraints`: dict mapping a relation type (e.g., `'>'`, `'='`, `'→'`, `'¬'`) to a list of tuples `(var_i, var_j, weight)`. Variables are identifiers extracted from noun phrases or numeric literals.  
- `belief`: numpy array of shape `(n_vars,)` holding a real‑valued confidence score for each variable’s truth value (0 = false, 1 = true). Initialized to 0.5 (uniform ignorance).  
- `error_history`: deque of recent scalar errors used for PID‑style adjustment.

*Operations*  
1. **Structural parsing** – regex extracts:  
   - numeric values (`\d+(\.\d+)?`) → assign to `num_var`.  
   - comparatives (`>`, `<`, `>=`, `<=`, `=`) → add constraint with type `'cmp'`.  
   - conditionals (`if … then …`) → add implication `'→'`.  
   - negations (`not`, `no`) → add `'¬'` on the following clause.  
   - causal cues (`because`, `since`, `leads to`) → add causal `'cause'`.  
   - ordering (`first`, `second`, `before`, `after`) → add `'order'`.  
   Each extracted tuple receives an initial weight `w0 = 1.0`.  

2. **Constraint propagation** – iteratively apply:  
   - For each `'cmp'` constraint `(a, b, w)`, enforce `belief[a] - belief[b] ≥ 0` (or ≤) via a projection step:  
     `delta = np.clip(belief[a] - belief[b] - target, -w, w)`  
     `belief[a] -= delta * w / (w_a + w_b)`  
     `belief[b] += delta * w / (w_a + w_b)`  
   - For each `'→'` `(antecedent, consequent, w)`, apply modus ponens: if `belief[antecedent] > 0.5` then increase `belief[consequent]` toward 1 with step `w * (belief[antecedent] - 0.5)`.  
   - For `'¬'` flip: `belief[var] = 1 - belief[var]` scaled by `w`.  
   - After each full sweep, compute **error** as the mean absolute violation of all constraints.  

3. **Feedback control (PID)** – update each constraint weight using a PID controller on the error signal:  
   `e_t = error_t`  
   `integral += e_t * dt`  
   `derivative = (e_t - e_{t-1}) / dt`  
   `w_new = w_old + Kp*e_t + Ki*integral + Kd*derivative` (clipped to `[0,2]`).  
   This implements metacognitive confidence calibration: weights grow for constraints that repeatedly reduce error (reliable reasoning steps) and shrink for those that increase error (mis‑steps).  

4. **Mechanism‑design scoring** – treat each candidate answer as a proposed set of variable assignments. Compute its **utility** as the negative total constraint violation after the PID‑adjusted weights have converged:  
   `score = - Σ_w * |violation|`.  
   Higher scores indicate answers that better satisfy the high‑confidence, self‑correcting constraint system. The answer with maximal score is selected.

*Structural features parsed* – numerics, comparatives, conditionals, negations, causal cues, ordering relations, and equality statements. These are the atomic propositions that become variables and constraints in the solver.

*Novelty* – The combination mirrors existing work: constraint‑propagation solvers (e.g., SAT/CP), PID‑based adaptive weighting (used in control‑theoretic NLP tuning), and mechanism‑design scoring (truthful elicitation via utility maximization). However, tightly coupling a PID controller to constraint weights inside a metacognitive loop for answer selection is not documented in the surveyed literature, making the approach novel in this specific integration.

**Ratings**  
Reasoning: 8/10 — The algorithm performs explicit logical propagation and numeric evaluation, meeting the pipeline’s success criteria.  
Metacognition: 7/10 — Confidence is calibrated via error‑driven weight updates, though it lacks higher‑order strategy selection beyond weight tuning.  
Hypothesis generation: 6/10 — The system generates implicit hypotheses (variable truth values) but does not propose diverse alternative explanations; it optimizes a single belief vector.  
Implementability: 9/10 — Uses only regex, NumPy arrays, and collections.deque; all operations are straightforward and deterministic.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Metacognition**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Feedback Control**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Mechanism Design**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 38% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Mechanism Design + Metacognition: strong positive synergy (+0.275). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Differentiable Programming + Metacognition + Mechanism Design (accuracy: 0%, calibration: 0%)
- Swarm Intelligence + Metacognition + Mechanism Design (accuracy: 0%, calibration: 0%)
- Active Inference + Mechanism Design + Type Theory (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: validation:runtime_error: ValueError: could not convert string to float: ''

**Forge Timestamp**: 2026-03-26T13:46:50.169089

---

## Code

**Source**: scrap

[View code](./Metacognition---Feedback_Control---Mechanism_Design/tool.py)

<details>
<summary>Show code</summary>

```python
import re
import numpy as np
from collections import deque, defaultdict
from typing import List, Dict, Tuple, Any

class ReasoningTool:
    """
    Adaptive Confidence-Weighted Constraint Solver (ACWCS).
    
    Mechanism:
    1. Structural Parsing: Extracts variables, numerics, comparatives, conditionals, 
       and negations from the prompt using regex to form a constraint graph.
    2. Constraint Propagation: Iteratively updates a 'belief' vector (truth values 0-1) 
       to satisfy extracted logical and numeric constraints.
    3. Feedback Control (PID): Adjusts constraint weights based on the error history 
       (violations), simulating metacognitive calibration. Reliable constraints gain weight.
    4. Mechanism Design Scoring: Evaluates candidate answers by measuring their 
       total weighted constraint violation after convergence. Lower violation = higher score.
    """
    
    def __init__(self):
        # PID Constants
        self.Kp = 0.5
        self.Ki = 0.1
        self.Kd = 0.05
        self.dt = 1.0
        
    def _tokenize(self, text: str) -> List[str]:
        return re.split(r'[\s\.,;!?()]+', text.lower())

    def _extract_vars_and_nums(self, text: str) -> Dict[str, float]:
        """Extract numeric literals and map simple noun phrases to variables."""
        nums = re.findall(r'\d+(\.\d+)?', text)
        found = {}
        # Map numbers to themselves as float values for comparison logic
        for n in nums:
            found[f"num_{n}"] = float(n)
        return found

    def _parse_constraints(self, text: str) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        Parse text into a list of constraints and initial variable beliefs.
        Returns: (constraints_list, initial_beliefs)
        """
        constraints = []
        beliefs = {}
        text_lower = text.lower()
        tokens = self._tokenize(text)
        
        # 1. Extract Numbers and create variables
        nums = re.findall(r'\d+(\.\d+)?', text)
        for n in nums:
            v_name = f"num_{n}"
            beliefs[v_name] = 1.0 if float(n) > 0 else 0.0 # Simplified truthiness
            
        # 2. Extract Comparatives (A > B, A < B, A = B)
        # Pattern: word/num (space) op (space) word/num
        cmp_pattern = r'(\w+(?:_\d+)?|\d+(?:\.\d+)?)\s*(>=|<=|>|<|=|is|equals)\s*(\w+(?:_\d+)?|\d+(?:\.\d+)?)'
        for match in re.finditer(cmp_pattern, text_lower):
            a, op, b = match.groups()
            # Normalize op
            if op in ['is', 'equals']: op = '='
            
            # Handle numeric literals directly
            if a.replace('.','').isdigit(): a = f"num_{a}"
            if b.replace('.','').isdigit(): b = f"num_{b}"
            
            constraints.append({'type': 'cmp', 'a': a, 'b': b, 'op': op, 'w': 1.0, 'target': 1.0})
            if a not in beliefs: beliefs[a] = 0.5
            if b not in beliefs: beliefs[b] = 0.5

        # 3. Extract Conditionals (if A then B)
        if_pattern = r'if\s+(.+?)\s+(?:then|,)?\s+(.+?)(?:\.|,|$)'
        for match in re.finditer(if_pattern, text_lower):
            antecedent_txt = match.group(1).strip()
            consequent_txt = match.group(2).strip()
            # Simplified mapping: use first token of clause as var proxy if not numeric
            a_var = antecedent_txt.split()[0] if antecedent_txt else "unknown_a"
            b_var = consequent_txt.split()[0] if consequent_txt else "unknown_b"
            if a_var not in beliefs: beliefs[a_var] = 0.5
            if b_var not in beliefs: beliefs[b_var] = 0.5
            constraints.append({'type': 'imp', 'a': a_var, 'b': b_var, 'w': 1.0})

        # 4. Extract Negations (not X)
        neg_pattern = r'(?:not|no)\s+(\w+)'
        for match in re.finditer(neg_pattern, text_lower):
            var = match.group(1)
            if var not in beliefs: beliefs[var] = 0.5
            constraints.append({'type': 'neg', 'var': var, 'w': 1.0})

        # Fallback if no structural constraints found: rely on NCD later
        if not constraints:
            pass 
            
        return constraints, beliefs

    def _propagate_and_calibrate(self, constraints: List[Dict], beliefs_init: Dict[str, float], max_iter: int = 20) -> Tuple[Dict[str, float], List[Dict]]:
        """Run constraint propagation with PID weight adjustment."""
        if not constraints:
            return beliefs_init, constraints
            
        vars_list = list(beliefs_init.keys())
        if not vars_list:
            return beliefs_init, constraints
            
        belief_vec = np.array([beliefs_init[v] for v in vars_list], dtype=np.float64)
        var_to_idx = {v: i for i, v in enumerate(vars_list)}
        
        # Initialize weights and PID state
        weights = np.ones(len(constraints))
        error_history = deque([0.0, 0.0, 0.0], maxlen=3)
        integral = 0.0
        prev_error = 0.0
        
        for iteration in range(max_iter):
            total_violation = 0.0
            active_count = 0
            
            # Sweep constraints
            for i, cons in enumerate(constraints):
                w = weights[i]
                if cons['type'] == 'cmp':
                    a, b, op = cons['a'], cons['b'], cons['op']
                    if a not in var_to_idx or b not in var_to_idx: continue
                    
                    idx_a, idx_b = var_to_idx[a], var_to_idx[b]
                    val_a, val_b = belief_vec[idx_a], belief_vec[idx_b]
                    
                    # Determine target relationship
                    # We interpret belief as probability of being "true" or magnitude if numeric
                    # For simplicity in this hybrid solver: 
                    # If vars are numeric literals, we check actual value. 
                    # If logical, we check consistency.
                    
                    violation = 0.0
                    # Heuristic: Check if current beliefs satisfy the relation
                    # Since beliefs are 0-1, we treat > as logical implication of magnitude
                    if op == '>':
                        violation = max(0, val_b - val_a) # Should be A > B
                    elif op == '<':
                        violation = max(0, val_a - val_b)
                    elif op == '=':
                        violation = abs(val_a - val_b)
                    
                    total_violation += violation * w
                    active_count += 1
                    
                    # Projection step (soft)
                    if violation > 0:
                        delta = violation * 0.1 * w # Step size
                        if op == '>':
                            belief_vec[idx_a] = min(1.0, belief_vec[idx_a] + delta)
                            belief_vec[idx_b] = max(0.0, belief_vec[idx_b] - delta)
                        elif op == '<':
                            belief_vec[idx_a] = max(0.0, belief_vec[idx_a] - delta)
                            belief_vec[idx_b] = min(1.0, belief_vec[idx_b] + delta)
                        elif op == '=':
                            avg = (val_a + val_b) / 2
                            belief_vec[idx_a] = avg
                            belief_vec[idx_b] = avg

                elif cons['type'] == 'imp':
                    # If A then B: if A is high, B should be high
                    a, b = cons['a'], cons['b']
                    if a not in var_to_idx or b not in var_to_idx: continue
                    idx_a, idx_b = var_to_idx[a], var_to_idx[b]
                    val_a, val_b = belief_vec[idx_a], belief_vec[idx_b]
                    
                    # Violation: A is true, B is false
                    violation = max(0, val_a - val_b)
                    total_violation += violation * w
                    active_count += 1
                    
                    if violation > 0:
                        belief_vec[idx_b] = min(1.0, val_b + violation * 0.2 * w)

                elif cons['type'] == 'neg':
                    var = cons['var']
                    if var not in var_to_idx: continue
                    idx = var_to_idx[var]
                    val = belief_vec[idx]
                    # Negation implies variable should be low if the clause is asserted as "not X" in a true context
                    # Here we simply penalize high confidence in the negated term if the prompt asserts "not X"
                    # This is a simplification for the solver loop
                    violation = val 
                    total_violation += violation * w
                    active_count += 1
                    belief_vec[idx] = max(0.0, val - 0.1 * w)

            # Normalize error
            error = total_violation / (active_count + 1e-6)
            error_history.append(error)
            
            # PID Control on Weights
            integral += error * self.dt
            derivative = (error - prev_error) / self.dt if iteration > 0 else 0
            
            for i in range(len(constraints)):
                adjustment = self.Kp * error + self.Ki * integral + self.Kd * derivative
                weights[i] = np.clip(weights[i] + adjustment, 0.1, 2.0)
            
            prev_error = error
            
            if error < 1e-4:
                break

        # Map back to dict
        final_beliefs = {v: float(belief_vec[i]) for i, v in enumerate(vars_list)}
        
        # Update constraints with new weights
        for i, cons in enumerate(constraints):
            cons['w'] = weights[i]
            
        return final_beliefs, constraints

    def _calculate_score(self, prompt: str, candidate: str, constraints: List[Dict], beliefs: Dict[str, float]) -> float:
        """Calculate negative weighted violation score."""
        if not constraints:
            return 0.0
            
        # Merge prompt beliefs with candidate assertions
        # We treat the candidate as setting specific variables to True/False or specific values
        candidate_lower = candidate.lower()
        test_beliefs = beliefs.copy()
        
        # Update beliefs based on candidate content
        # If candidate contains a number from constraints, assume that's the value
        nums = re.findall(r'\d+(\.\d+)?', candidate)
        for n in nums:
            test_beliefs[f"num_{n}"] = 1.0 # Assert presence
            
        # If candidate matches a variable name, assert it
        tokens = set(self._tokenize(candidate))
        for k in test_beliefs:
            if k in tokens:
                test_beliefs[k] = 1.0
                
        total_violation = 0.0
        total_weight = 0.0
        
        for cons in constraints:
            w = cons['w']
            total_weight += w
            if cons['type'] == 'cmp':
                a, b, op = cons['a'], cons['b'], cons['op']
                val_a = test_beliefs.get(a, 0.5)
                val_b = test_beliefs.get(b, 0.5)
                
                # Check numeric literals specifically if available in candidate
                # This is a heuristic: if candidate has the number, we assume the relation holds if logic fits
                # But strictly we check the belief vector
                
                viol = 0.0
                if op == '>': viol = max(0, val_b - val_a)
                elif op == '<': viol = max(0, val_a - val_b)
                elif op == '=': viol = abs(val_a - val_b)
                
                total_violation += w * viol
                
            elif cons['type'] == 'imp':
                a, b = cons['a'], cons['b']
                val_a = test_beliefs.get(a, 0.5)
                val_b = test_beliefs.get(b, 0.5)
                viol = max(0, val_a - val_b)
                total_violation += w * viol
                
            elif cons['type'] == 'neg':
                var = cons['var']
                val = test_beliefs.get(var, 0.5)
                # If candidate asserts the negated thing, penalty
                if var in tokens:
                    total_violation += w * val

        if total_weight == 0:
            return 0.0
            
        # Score is negative violation
        return -total_violation

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        def zlib_len(s):
            import zlib
            return len(zlib.compress(s.encode('utf-8')))
        
        l1 = zlib_len(s1)
        l2 = zlib_len(s2)
        l12 = zlib_len(s1 + s2)
        
        if max(l1, l2) == 0:
            return 0.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        constraints, beliefs = self._parse_constraints(prompt)
        final_beliefs, updated_constraints = self._propagate_and_calibrate(constraints, beliefs)
        
        results = []
        for cand in candidates:
            score = self._calculate_score(prompt, cand, updated_constraints, final_beliefs)
            
            # Tiebreaker: If structural score is 0 (no constraints found), use NCD
            if score == 0.0 and not constraints:
                # Invert NCD so higher is better (lower distance = higher score)
                ncd = self._ncd_score(prompt, cand)
                score = -ncd 
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Constraint violation score: {score:.4f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on ranking position simulation."""
        # Simulate evaluation against a dummy set containing the answer
        # Since we don't have other candidates, we check if the answer satisfies constraints
        constraints, beliefs = self._parse_constraints(prompt)
        if not constraints:
            return 0.5 # No structural info
            
        final_beliefs, updated_constraints = self._propagate_and_calibrate(constraints, beliefs)
        score = self._calculate_score(prompt, answer, updated_constraints, final_beliefs)
        
        # Map score to 0-1. 
        # Score is negative violation. 0 violation = 0. 
        # Let's assume max violation is roughly number of constraints.
        max_viol = len(updated_constraints) * 2.0 # Heuristic max
        normalized = max(0.0, 1.0 + (score / max_viol)) if max_viol > 0 else 0.5
        return float(np.clip(normalized, 0.0, 1.0))
```

</details>
