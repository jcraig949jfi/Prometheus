from typing import Dict, Tuple

"""
Dynamical Systems x Predictive Coding x Maximum Entropy Reasoning Tool

Core mechanism:
1. Parse prompt into linear belief constraints (Ax <= b)
2. Gradient flow on prediction error minimizes surprise (Predictive Coding)
3. Maximum entropy distribution over constraint-satisfying beliefs
4. Score = negative free energy (error - entropy)
"""

import re
import numpy as np
from typing import List, Dict, Tuple
import zlib
from forge_primitives import solve_constraints, entropy, bayesian_update, confidence_from_agreement

class ReasoningTool:
    def __init__(self):
        self.eta = 0.1  # Learning rate for predictive coding
        self.max_iter = 50
        self.epsilon = 1e-4
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Score candidates by free energy over belief dynamics."""
        results = []
        
        for candidate in candidates:
            context = prompt + " " + candidate
            score, reasoning = self._compute_free_energy(prompt, candidate, context)
            results.append({
                "candidate": candidate,
                "score": score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1, with epistemic honesty for ambiguous prompts."""
        # TIER B: Meta-confidence checks
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        context = prompt + " " + answer
        constraints, propositions = self._parse_constraints(context)
        
        if len(constraints) == 0:
            return 0.2  # No structure parsed, honest uncertainty
        
        # Compute free energy
        score, _ = self._compute_free_energy(prompt, answer, context)
        
        # Map score to confidence, capped by meta-confidence
        raw_conf = min(1.0, max(0.0, score))
        return min(raw_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B reasoning traps. Return <0.3 for ambiguous prompts."""
        p_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop|end))\b', p_lower):
            return 0.15
        
        # Scope ambiguity: "Every X ... a Y"
        if re.search(r'\bevery \w+ .+ a \w+', p_lower) and 'same' not in p_lower:
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|they)\b', p_lower) and 'who' in p_lower:
            if re.search(r'\b(told|said|informed) \w+ (he|she)', p_lower):
                return 0.2
        
        # False dichotomy
        if re.search(r'\b(either .+ or|must be (A|B))\b', p_lower):
            if 'only' not in p_lower and 'neither' not in p_lower:
                return 0.25
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p_lower):
            if not re.search(r'\b(measure|metric|criterion|score)\b', p_lower):
                return 0.25
        
        # Unanswerable: "What is X's Y?" when X not mentioned
        if '?' in prompt:
            entities = re.findall(r'\b([A-Z][a-z]+)\'s\b', prompt)
            if entities and not any(re.search(rf'\b{e}\b', prompt[:prompt.index("'")]) for e in entities):
                return 0.2
        
        return 0.85  # Default high meta-confidence
    
    def _parse_constraints(self, text: str) -> Tuple[List[Dict], List[str]]:
        """Extract propositions and constraints from text."""
        constraints = []
        propositions = []
        prop_map = {}
        
        # Extract numeric comparisons
        numeric = re.findall(r'(\d+\.?\d*)\s*(>|<|>=|<=|=)\s*(\d+\.?\d*)', text)
        for match in numeric:
            left, op, right = float(match[0]), match[1], float(match[2])
            is_valid = (op == '>' and left > right) or (op == '<' and left < right) or \
                       (op == '>=' and left >= right) or (op == '<=' and left <= right) or \
                       (op == '=' and abs(left - right) < 0.01)
            
            prop = f"numeric_{len(propositions)}"
            propositions.append(prop)
            prop_map[prop] = len(propositions) - 1
            
            # Constraint: x_i = 1.0 if valid, 0.0 if invalid
            constraints.append({
                'type': 'equality',
                'indices': [prop_map[prop]],
                'value': 1.0 if is_valid else 0.0,
                'weight': 2.0
            })
        
        # Extract comparatives (A > B, A before B)
        comparatives = re.findall(r'(\w+)\s+(greater than|more than|before|after|less than)\s+(\w+)', text.lower())
        for match in comparatives:
            subj, rel, obj = match
            if subj not in prop_map:
                propositions.append(subj)
                prop_map[subj] = len(propositions) - 1
            if obj not in prop_map:
                propositions.append(obj)
                prop_map[obj] = len(propositions) - 1
            
            if rel in ['greater than', 'more than', 'after']:
                # x_subj >= x_obj
                constraints.append({
                    'type': 'inequality',
                    'indices': [prop_map[subj], prop_map[obj]],
                    'coeffs': [1, -1],
                    'bound': 0.0,
                    'weight': 1.5
                })
        
        # Conditionals: if A then B => A <= B
        conditionals = re.findall(r'if (\w+) then (\w+)', text.lower())
        for ant, cons in conditionals:
            if ant not in prop_map:
                propositions.append(ant)
                prop_map[ant] = len(propositions) - 1
            if cons not in prop_map:
                propositions.append(cons)
                prop_map[cons] = len(propositions) - 1
            
            constraints.append({
                'type': 'implication',
                'indices': [prop_map[ant], prop_map[cons]],
                'weight': 1.5
            })
        
        # Negations
        negations = re.findall(r'\b(not|no)\s+(\w+)', text.lower())
        for _, prop in negations:
            if prop not in prop_map:
                propositions.append(prop)
                prop_map[prop] = len(propositions) - 1
            
            constraints.append({
                'type': 'equality',
                'indices': [prop_map[prop]],
                'value': 0.0,
                'weight': 2.0
            })
        
        return constraints, propositions
    
    def _predictive_coding_flow(self, constraints: List[Dict], n_props: int) -> np.ndarray:
        """Gradient descent on prediction error (dynamical system)."""
        x = np.random.uniform(0.3, 0.7, n_props)  # Initial beliefs
        
        for _ in range(self.max_iter):
            x_old = x.copy()
            
            for c in constraints:
                weight = c.get('weight', 1.0)
                
                if c['type'] == 'equality':
                    idx = c['indices'][0]
                    target = c['value']
                    error = x[idx] - target
                    x[idx] -= self.eta * weight * error
                
                elif c['type'] == 'inequality':
                    i, j = c['indices']
                    coeffs = c['coeffs']
                    bound = c['bound']
                    violation = coeffs[0] * x[i] + coeffs[1] * x[j] - bound
                    if violation < 0:  # Constraint satisfied
                        continue
                    x[i] -= self.eta * weight * coeffs[0] * violation
                    x[j] -= self.eta * weight * coeffs[1] * violation
                
                elif c['type'] == 'implication':
                    ant, cons = c['indices']
                    if x[ant] > x[cons]:  # Violation
                        error = x[ant] - x[cons]
                        x[ant] -= self.eta * weight * error * 0.5
                        x[cons] += self.eta * weight * error * 0.5
            
            x = np.clip(x, 0.0, 1.0)
            
            if np.linalg.norm(x - x_old) < self.epsilon:
                break
        
        return x
    
    def _compute_free_energy(self, prompt: str, candidate: str, context: str) -> Tuple[float, str]:
        """Compute negative free energy: F = error - H(beliefs)."""
        constraints, propositions = self._parse_constraints(context)
        
        if len(propositions) == 0:
            # Fall back to NCD
            ncd = self._ncd(prompt, candidate)
            return 0.3 * (1 - ncd), "NCD fallback"
        
        # Dynamical system: predictive coding gradient flow
        beliefs = self._predictive_coding_flow(constraints, len(propositions))
        
        # Compute prediction error
        error = 0.0
        for c in constraints:
            if c['type'] == 'equality':
                idx = c['indices'][0]
                error += (beliefs[idx] - c['value']) ** 2
            elif c['type'] == 'inequality':
                i, j = c['indices']
                violation = max(0, c['coeffs'][1] * beliefs[j] - c['coeffs'][0] * beliefs[i] + c['bound'])
                error += violation ** 2
            elif c['type'] == 'implication':
                ant, cons = c['indices']
                violation = max(0, beliefs[ant] - beliefs[cons])
                error += violation ** 2
        
        # Maximum entropy refinement
        beliefs_clipped = np.clip(beliefs, 0.01, 0.99)
        H = entropy([beliefs_clipped, 1 - beliefs_clipped])
        
        # Free energy: lower error + higher entropy = better
        free_energy = -0.5 * error + 0.3 * H
        
        # Normalize to [0, 1]
        score = 1.0 / (1.0 + np.exp(-free_energy))
        
        reasoning = f"Parsed {len(propositions)} propositions, {len(constraints)} constraints. " \
                   f"Error={error:.3f}, Entropy={H:.3f}, FreeEnergy={free_energy:.3f}"
        
        return score, reasoning
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0