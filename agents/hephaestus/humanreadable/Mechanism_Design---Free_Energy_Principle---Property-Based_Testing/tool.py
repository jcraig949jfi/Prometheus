import re
import numpy as np
from itertools import product
from typing import List, Dict, Tuple, Set, Any

class ReasoningTool:
    """
    Implements a hybrid reasoning engine combining Mechanism Design, Free Energy Principle,
    and Property-Based Testing.
    
    Mechanism:
    1. Parsing: Converts text to Horn clauses (rules) and literals (facts) with signs.
    2. Free Energy: Scores candidates by minimizing prediction error (E) + complexity penalty (C).
    3. Property Testing: Generates synthetic worlds to falsify candidate mechanisms.
    """

    def __init__(self):
        self.alpha = 0.1  # Complexity weight
        self.lambda_param = 0.5  # Free energy tradeoff
        self.gamma = 0.2  # Minimality weight
        self.n_samples = 20  # Worlds to sample per candidate

    def _parse_text(self, text: str) -> Tuple[List[Dict], List[Dict]]:
        """Extracts rules and literals from text using regex patterns."""
        rules = []
        literals = []
        text_lower = text.lower()
        
        # 1. Extract Negations
        neg_patterns = [r'\bnot\s+(\w+)', r'\bno\s+(\w+)', r'\bnever\s+(\w+)']
        for pat in neg_patterns:
            for m in re.finditer(pat, text_lower):
                literals.append({'pred': m.group(1), 'args': [], 'sign': -1})

        # 2. Extract Comparatives (Numeric)
        comp_pat = r'(\d+\.?\d*)\s*(>=|<=|>|<|=)\s*(\d+\.?\d*)'
        for m in re.finditer(comp_pat, text):
            v1, op, v2 = m.groups()
            literals.append({'pred': 'cmp', 'args': [float(v1), op, float(v2)], 'sign': 1})

        # 3. Extract Conditionals (If A then B / A leads to B)
        # Simplified: head :- body
        if_pat = r'\bif\s+(.+?)\s+(?:then|,)\s+(.+?)\b'
        for m in re.finditer(if_pat, text_lower):
            body, head = m.group(1).strip(), m.group(2).strip()
            rules.append({'head': head, 'body': body})
            
        causal_pat = r'(.+?)\s+(?:leads to|causes|implies)\s+(.+?)\b'
        for m in re.finditer(causal_pat, text_lower):
            body, head = m.group(1).strip(), m.group(2).strip()
            rules.append({'head': head, 'body': body})

        # 4. Extract Base Facts (Simple subject-predicate approx)
        # Look for "X is Y" or "X does Y"
        fact_pat = r'\b([a-z]+)\s+(?:is|does|has|contains)\s+([a-z0-9\.]+)\b'
        for m in re.finditer(fact_pat, text_lower):
            subj, obj = m.group(1), m.group(2)
            literals.append({'pred': subj, 'args': [obj], 'sign': 1})

        return rules, literals

    def _generate_worlds(self, base_preds: List[str], n: int) -> List[Dict[str, bool]]:
        """Generates random truth assignments for base predicates."""
        worlds = []
        if not base_preds:
            return [{}]
        
        # Deterministic sampling based on index for reproducibility
        for i in range(n):
            world = {}
            # Use bit manipulation of index for deterministic pseudo-randomness
            for j, pred in enumerate(base_preds):
                # Simple hash-like determinism
                val = ((i + 1) * (j + 1)) % 2 == 0
                world[pred] = val
            worlds.append(world)
        return worlds

    def _check_rule(self, rule: Dict, world: Dict[str, bool]) -> bool:
        """Checks if a rule holds in a given world (Modus Ponens approx)."""
        body_str = rule['body']
        head_str = rule['head']
        
        # Very simplified matching: check if body tokens exist and are true
        # In a real system, this would map variables. Here we check keyword presence.
        body_tokens = set(re.findall(r'\w+', body_str))
        head_token = re.findall(r'\w+', head_str)[0] if re.findall(r'\w+', head_str) else ""
        
        # Check body satisfaction
        body_true = all(world.get(t, False) for t in body_tokens) if body_tokens else False
        
        if body_true:
            # If body is true, head MUST be true for the rule to hold without error
            return world.get(head_token, False)
        return True # Vacuously true if body false

    def _compute_free_energy(self, candidate: str, prompt_literals: List[Dict]) -> Tuple[float, float, str]:
        """Computes F(M) = E(M) + lambda * C(M)"""
        rules, cand_literals = self._parse_text(candidate)
        
        # Complexity Penalty: Length of rules + vars
        complexity = self.alpha * (len(rules) + len(cand_literals))
        for r in rules:
            complexity += 0.1 * (len(r['head']) + len(r['body']))
            
        # Identify base predicates to generate worlds
        all_preds = set()
        for lit in cand_literals:
            all_preds.add(lit['pred'])
        for r in rules:
            all_preds.update(re.findall(r'\w+', r['head']))
            all_preds.update(re.findall(r'\w+', r['body']))
            
        base_preds = list(all_preds)
        worlds = self._generate_worlds(base_preds, self.n_samples)
        
        # Prediction Error
        total_violations = 0
        min_counterexample = None
        
        for w in worlds:
            violations = 0
            # Check internal consistency of candidate rules
            for r in rules:
                if not self._check_rule(r, w):
                    violations += 1
            
            # Check against prompt facts (if candidate contradicts prompt literals)
            # Simplified: If prompt says "X is true" and candidate implies "X is false"
            for lit in prompt_literals:
                if lit['sign'] == 1:
                    # If prompt asserts P, and candidate world says not P (approx)
                    if lit['pred'] in w and not w[lit['pred']]:
                        violations += 1
            
            if violations > 0:
                total_violations += 1
                if min_counterexample is None:
                    min_counterexample = str(w)

        error_rate = total_violations / len(worlds) if worlds else 0.0
        free_energy = error_rate + self.lambda_param * complexity
        
        reason_str = f"Error:{error_rate:.2f}, Complexity:{complexity:.2f}"
        if min_counterexample:
            reason_str += f", Counter: {min_counterexample[:50]}..."
            
        return free_energy, error_rate, reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_rules, prompt_lits = self._parse_text(prompt)
        results = []
        
        for cand in candidates:
            f_energy, err, reason = self._compute_free_energy(cand, prompt_lits)
            # Score is inverse of free energy, clipped to [0, 1]
            # Lower free energy = Higher score
            score = max(0.0, min(1.0, 1.0 - f_energy))
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        # Evaluate single candidate against prompt
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
        return res_list[0]['score']