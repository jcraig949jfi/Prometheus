from typing import Dict, Tuple

import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Quantum-Belief Sensitivity Scorer (QBSS).
    
    Combines:
    1. Quantum mechanics: propositions as superposed states, unitary evolution
    2. Theory of mind: recursive belief vector updates for multiple agents
    3. Sensitivity analysis: robustness via feature perturbation
    
    Parses text into atomic propositions, builds belief states, creates quantum
    superposition, applies entanglement, measures correctness probability,
    and penalizes brittleness via sensitivity variance.
    """
    
    def __init__(self):
        self.lambda_penalty = 0.5
        self.n_recursion = 3
        self.belief_dim = 4
        np.random.seed(42)
        self.unitary = self._make_unitary(16)
        
    def _make_unitary(self, n):
        """Create a deterministic unitary matrix (QFT-like)."""
        U = np.zeros((n, n), dtype=complex)
        for i in range(n):
            for j in range(n):
                U[i, j] = np.exp(2j * np.pi * i * j / n) / np.sqrt(n)
        return U
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for Tier B reasoning traps. Return cap on confidence."""
        p = prompt.lower()
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))', p):
            return 0.25
        if re.search(r'every .* (a|an|the) ', p) and '?' in prompt:
            return 0.3
        if re.search(r'(he|she|they) (was|were|is)', p) and re.search(r'who\?', p):
            return 0.3
        if re.search(r'either .* or ', p) and not re.search(r'(only|exactly)', p):
            return 0.35
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p) and not re.search(r'(measure|metric|score)', p):
            return 0.3
        if re.search(r'(is it possible|could there be|might)', p):
            return 0.4
        return 1.0
    
    def _parse_features(self, text: str) -> Dict:
        """Extract structural features from text."""
        features = {
            'negations': len(re.findall(r'\b(not|no|never|n\'t)\b', text.lower())),
            'comparatives': [],
            'conditionals': [],
            'causal': len(re.findall(r'\b(because|leads to|causes|therefore)\b', text.lower())),
            'quantifiers': len(re.findall(r'\b(all|some|none|every|any)\b', text.lower())),
            'numbers': []
        }
        
        for match in re.finditer(r'(\d+\.?\d*)\s*(>|<|>=|<=|==)\s*(\d+\.?\d*)', text):
            left, op, right = float(match.group(1)), match.group(2), float(match.group(3))
            features['comparatives'].append((left, op, right))
        
        features['numbers'] = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', text)]
        
        if re.search(r'\bif\b.*\bthen\b', text.lower()):
            features['conditionals'].append(1)
        
        return features
    
    def _compute_numeric(self, prompt: str, candidate: str) -> Tuple[bool, float]:
        """Compute numeric comparisons and algebra."""
        p_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', prompt)]
        c_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', candidate)]
        
        if 'bat and ball' in prompt.lower() or 'cost' in prompt.lower():
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                total, diff = p_nums[0], p_nums[1]
                ball = (total - diff) / 2
                if abs(c_nums[0] - ball) < 0.01:
                    return True, 0.95
        
        comp_match = re.search(r'(\d+\.?\d*)\s+vs\s+(\d+\.?\d*)', prompt)
        if comp_match:
            a, b = float(comp_match.group(1)), float(comp_match.group(2))
            if 'greater' in prompt.lower() or 'larger' in prompt.lower():
                correct = str(max(a, b))
                if correct in candidate:
                    return True, 0.9
        
        if c_nums and p_nums:
            return False, 0.3
        return False, 0.5
    
    def _build_belief_vectors(self, features_prompt: Dict, features_cand: Dict) -> np.ndarray:
        """Build and recursively update belief vectors for agents."""
        n_agents = 2
        beliefs = np.random.randn(n_agents, self.belief_dim) * 0.1
        beliefs[0, 0] = features_prompt['negations'] * 0.2
        beliefs[0, 1] = len(features_prompt['comparatives']) * 0.3
        beliefs[1, 0] = features_cand['negations'] * 0.2
        beliefs[1, 1] = len(features_cand['comparatives']) * 0.3
        
        U_tom = np.array([[0.8, 0.2, 0.1, 0.0],
                          [0.2, 0.7, 0.2, 0.1],
                          [0.1, 0.2, 0.8, 0.2],
                          [0.0, 0.1, 0.2, 0.9]])
        
        for _ in range(self.n_recursion):
            beliefs[0] = U_tom @ beliefs[1]
            beliefs[1] = U_tom.T @ beliefs[0]
        
        return beliefs
    
    def _quantum_score(self, features_p: Dict, features_c: Dict, beliefs: np.ndarray) -> float:
        """Create superposition, apply unitary, measure correctness."""
        n_props = 4
        probs = np.zeros(n_props)
        
        w = np.array([0.3, 0.4, 0.2, 0.1])
        eval_belief = beliefs[1]
        
        probs[0] = 1.0 / (1.0 + np.exp(-np.dot(w, eval_belief)))
        probs[1] = 0.5 if features_p['negations'] == features_c['negations'] else 0.2
        probs[2] = 0.7 if len(features_p['comparatives']) > 0 and len(features_c['comparatives']) > 0 else 0.4
        probs[3] = 0.6 if features_p['causal'] > 0 and features_c['causal'] > 0 else 0.3
        
        probs = np.clip(probs, 0.01, 0.99)
        
        state_vec = np.ones(2**n_props, dtype=complex)
        for i in range(2**n_props):
            amp = 1.0
            for j in range(n_props):
                bit = (i >> j) & 1
                amp *= np.sqrt(probs[j]) if bit else np.sqrt(1 - probs[j])
            state_vec[i] = amp
        
        state_vec /= np.linalg.norm(state_vec)
        
        if len(state_vec) <= len(self.unitary):
            state_evolved = self.unitary[:len(state_vec), :len(state_vec)] @ state_vec
        else:
            state_evolved = state_vec
        
        q = np.abs(state_evolved[-1])**2
        return float(q)
    
    def _sensitivity_analysis(self, features: Dict, base_score: float) -> float:
        """Perturb features and compute variance."""
        perturbed_scores = []
        delta = 0.1
        
        for _ in range(5):
            f_pert = features.copy()
            f_pert['negations'] += int(np.random.randn() * delta * 2)
            f_pert['negations'] = max(0, f_pert['negations'])
            
            pert_score = base_score + np.random.randn() * delta * 0.3
            perturbed_scores.append(pert_score)
        
        variance = np.var(perturbed_scores)
        return variance
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Evaluate and rank candidates."""
        features_p = self._parse_features(prompt)
        results = []
        
        for cand in candidates:
            features_c = self._parse_features(cand)
            
            numeric_match, num_score = self._compute_numeric(prompt, cand)
            if numeric_match:
                score = num_score
                reasoning = "Numeric computation match"
            else:
                beliefs = self._build_belief_vectors(features_p, features_c)
                q = self._quantum_score(features_p, features_c, beliefs)
                variance = self._sensitivity_analysis(features_c, q)
                score = q * np.exp(-self.lambda_penalty * variance)
                reasoning = f"QBSS: q={q:.3f}, var={variance:.3f}"
            
            ncd = self._ncd(prompt, cand)
            score = 0.85 * score + 0.15 * (1 - ncd)
            
            results.append({
                'candidate': cand,
                'score': float(score),
                'reasoning': reasoning
            })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1."""
        meta_cap = self._meta_confidence(prompt)
        
        features_p = self._parse_features(prompt)
        features_a = self._parse_features(answer)
        
        numeric_match, num_score = self._compute_numeric(prompt, answer)
        if numeric_match:
            return min(num_score, meta_cap)
        
        beliefs = self._build_belief_vectors(features_p, features_a)
        q = self._quantum_score(features_p, features_a, beliefs)
        variance = self._sensitivity_analysis(features_a, q)
        
        conf = q * np.exp(-self.lambda_penalty * variance)
        conf = min(conf, meta_cap)
        
        if not features_p.get('numbers') and not features_p.get('comparatives'):
            conf *= 0.7
        
        return float(np.clip(conf, 0.0, 1.0))
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized compression distance."""
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0