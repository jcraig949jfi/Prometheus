from typing import Dict, Tuple

"""
Chaos-MaxEnt-Property Reasoning Tool

Combines Maximum Entropy constraint satisfaction, Lyapunov stability analysis,
and property-based perturbation testing to evaluate reasoning answers.

Core mechanism:
1. Extract structural constraints (comparatives, conditionals, negations)
2. Build MaxEnt model P(a) ~ exp(lambda^T f(a)) over constraint features
3. Generate perturbations and measure chaotic sensitivity (Lyapunov exponent)
4. Track state evolution as dynamical system across premise sequence
5. Score = log P(a) - alpha * Lambda(a) + dynamics_stability
"""

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    def __init__(self):
        self.alpha = 0.1  # Chaos penalty weight
        self.beta = 0.3   # Dynamics weight
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        constraints = self._parse_constraints(prompt)
        premises = self._extract_premises(prompt)
        
        results = []
        for cand in candidates:
            # MaxEnt constraint satisfaction
            features = self._compute_features(cand, constraints)
            weights = self._fit_maxent_weights(features)
            log_prob = np.dot(weights, features)
            
            # Chaos-theoretic stability (Lyapunov)
            lyapunov = self._compute_lyapunov(cand, constraints, weights)
            
            # Dynamics tracking
            dynamics_score = self._track_dynamics(cand, premises, constraints)
            
            # Structural + computational score
            struct_score = self._structural_score(prompt, cand)
            comp_score = self._computational_score(prompt, cand)
            
            # NCD tiebreaker (max 15%)
            ncd = self._ncd(prompt, cand)
            ncd_score = (1 - ncd) * 0.15
            
            # Combined score
            score = (log_prob - self.alpha * lyapunov + 
                    self.beta * dynamics_score + 
                    0.3 * struct_score + 0.2 * comp_score + ncd_score)
            
            reasoning = f"MaxEnt={log_prob:.2f}, Lyap={lyapunov:.2f}, Dyn={dynamics_score:.2f}"
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        constraints = self._parse_constraints(prompt)
        if len(constraints) == 0:
            return 0.25
        
        features = self._compute_features(answer, constraints)
        satisfaction = np.mean(features) if len(features) > 0 else 0.0
        
        comp_conf = self._computational_confidence(prompt, answer)
        if comp_conf > 0.8:
            return min(0.9, comp_conf)
        
        base_conf = 0.3 + 0.5 * satisfaction
        return min(meta_conf, base_conf)
    
    def _parse_constraints(self, prompt: str) -> List[Dict]:
        constraints = []
        text = prompt.lower()
        
        # Comparatives
        for m in re.finditer(r'(\w+)\s+(>|<|>=|<=|greater|less|more|fewer)\s+(\w+)', text):
            constraints.append({"type": "comparative", "data": m.groups()})
        
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', text):
            constraints.append({"type": "conditional", "data": m.groups()})
        
        # Negations
        for m in re.finditer(r'(not|no|never|none)\s+(\w+)', text):
            constraints.append({"type": "negation", "data": m.groups()})
        
        # Causals
        for m in re.finditer(r'(\w+)\s+(because|leads to|results in|causes)\s+(\w+)', text):
            constraints.append({"type": "causal", "data": m.groups()})
        
        # Numeric relations
        for m in re.finditer(r'(\d+\.?\d*)\s*([<>=]+)\s*(\d+\.?\d*)', text):
            constraints.append({"type": "numeric", "data": m.groups()})
        
        return constraints
    
    def _compute_features(self, answer: str, constraints: List[Dict]) -> np.ndarray:
        if not constraints:
            return np.array([0.5])
        
        features = []
        ans_lower = answer.lower()
        
        for c in constraints:
            if c["type"] == "comparative":
                feat = 1.0 if any(w in ans_lower for w in c["data"]) else 0.0
            elif c["type"] == "conditional":
                antecedent, consequent = c["data"]
                feat = 1.0 if (antecedent in ans_lower or consequent in ans_lower) else 0.0
            elif c["type"] == "negation":
                neg, term = c["data"]
                feat = 1.0 if (neg in ans_lower and term not in ans_lower) else 0.0
            elif c["type"] == "causal":
                feat = 1.0 if any(w in ans_lower for w in c["data"]) else 0.0
            elif c["type"] == "numeric":
                feat = self._check_numeric_relation(c["data"], ans_lower)
            else:
                feat = 0.0
            features.append(feat)
        
        return np.array(features) if features else np.array([0.5])
    
    def _check_numeric_relation(self, data: Tuple, answer: str) -> float:
        try:
            left, op, right = data
            left_val, right_val = float(left), float(right)
            
            if '<' in op and left_val < right_val:
                return 1.0
            elif '>' in op and left_val > right_val:
                return 1.0
            elif '=' in op and abs(left_val - right_val) < 1e-6:
                return 1.0
        except:
            pass
        return 0.0
    
    def _fit_maxent_weights(self, features: np.ndarray) -> np.ndarray:
        # Simple MaxEnt: weights proportional to feature presence
        return np.ones_like(features) * (1.0 / (len(features) + 1e-6))
    
    def _compute_lyapunov(self, answer: str, constraints: List[Dict], weights: np.ndarray) -> float:
        perturbations = self._generate_perturbations(answer)
        if not perturbations:
            return 0.0
        
        base_score = np.dot(weights, self._compute_features(answer, constraints))
        divergences = []
        
        for perturbed, edit_dist in perturbations:
            perturb_features = self._compute_features(perturbed, constraints)
            perturb_score = np.dot(weights, perturb_features)
            div = abs(perturb_score - base_score) / (edit_dist + 1e-6)
            divergences.append(div)
        
        return np.mean(np.log(np.array(divergences) + 1e-6)) if divergences else 0.0
    
    def _generate_perturbations(self, answer: str) -> List[Tuple[str, int]]:
        perturbations = []
        words = answer.split()
        
        # Single word swaps
        if len(words) > 1:
            for i in range(len(words) - 1):
                perturbed = words[:i] + [words[i+1], words[i]] + words[i+2:]
                perturbations.append((" ".join(perturbed), 1))
        
        # Negation insertion
        for neg in ["not", "no"]:
            perturbations.append((neg + " " + answer, 1))
        
        # Numeric perturbation
        for m in re.finditer(r'\d+\.?\d*', answer):
            try:
                val = float(m.group())
                perturbed = answer[:m.start()] + str(val + 1) + answer[m.end():]
                perturbations.append((perturbed, 1))
            except:
                pass
        
        return perturbations[:10]
    
    def _track_dynamics(self, answer: str, premises: List[str], constraints: List[Dict]) -> float:
        """Track state evolution as dynamical system across premise sequence"""
        if not premises:
            return 0.5
        
        state = np.zeros(5)  # 5-dimensional state vector
        trajectory = [state.copy()]
        
        for i, premise in enumerate(premises):
            # Update state based on premise-answer interaction
            prem_features = self._compute_features(premise, constraints)
            ans_features = self._compute_features(answer, constraints)
            
            # Reservoir-like dynamics: tanh(W*state + U*input)
            input_vec = np.concatenate([prem_features[:3], ans_features[:2]]) if len(prem_features) >= 3 and len(ans_features) >= 2 else np.random.randn(5) * 0.1
            state = np.tanh(0.8 * state + 0.2 * input_vec[:5])
            trajectory.append(state.copy())
        
        # Measure convergence stability
        trajectory = np.array(trajectory)
        if len(trajectory) > 2:
            deltas = np.diff(trajectory, axis=0)
            convergence = 1.0 / (1.0 + np.mean(np.linalg.norm(deltas, axis=1)))
        else:
            convergence = 0.5
        
        return convergence
    
    def _extract_premises(self, prompt: str) -> List[str]:
        sentences = re.split(r'[.!?]', prompt)
        return [s.strip() for s in sentences if len(s.strip()) > 5]
    
    def _structural_score(self, prompt: str, answer: str) -> float:
        score = 0.0
        p_lower, a_lower = prompt.lower(), answer.lower()
        
        # Check for comparative consistency
        if re.search(r'(greater|more|larger)', p_lower):
            if re.search(r'(greater|more|larger|yes|true)', a_lower):
                score += 0.3
        
        # Check for negation consistency
        if re.search(r'(not|no|never)', p_lower):
            if re.search(r'(not|no|never|false)', a_lower):
                score += 0.3
        
        # Conditional structure
        if 'if' in p_lower and 'then' in p_lower:
            if any(w in a_lower for w in ['yes', 'true', 'correct']):
                score += 0.2
        
        return min(score, 1.0)
    
    def _computational_score(self, prompt: str, answer: str) -> float:
        # Numeric computation
        nums_p = re.findall(r'\d+\.?\d*', prompt)
        nums_a = re.findall(r'\d+\.?\d*', answer)
        
        if nums_p and nums_a:
            try:
                vals_p = [float(n) for n in nums_p]
                vals_a = [float(n) for n in nums_a]
                
                # Check arithmetic relationships
                if len(vals_p) >= 2:
                    expected = vals_p[0] + vals_p[1]
                    if any(abs(v - expected) < 0.01 for v in vals_a):
                        return 1.0
            except:
                pass
        
        return 0.0
    
    def _computational_confidence(self, prompt: str, answer: str) -> float:
        nums_p = re.findall(r'\d+\.?\d*', prompt)
        nums_a = re.findall(r'\d+\.?\d*', answer)
        
        if len(nums_p) >= 2 and nums_a:
            return 0.85
        return 0.0
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        return (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))
    
    def _meta_confidence(self, prompt: str) -> float:
        p_lower = prompt.lower()
        
        # Presupposition detection
        if re.search(r'have you (stopped|quit|ceased)', p_lower):
            return 0.2
        if re.search(r'why (did|does|is) \w+ (fail|stop|wrong)', p_lower):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every \w+.*?\s+a\s+\w+', p_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they)\s+was', p_lower) and 'who' in p_lower:
            return 0.2
        
        # False dichotomy
        if re.search(r'either\s+\w+\s+or\s+\w+', p_lower) and '?' in prompt:
            return 0.3
        
        # Subjectivity
        if re.search(r'(best|worst|favorite|most|least)\s+\w+', p_lower):
            return 0.3
        
        # Insufficient information
        if '?' in prompt and len(prompt.split()) < 8:
            return 0.4
        
        return 1.0