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