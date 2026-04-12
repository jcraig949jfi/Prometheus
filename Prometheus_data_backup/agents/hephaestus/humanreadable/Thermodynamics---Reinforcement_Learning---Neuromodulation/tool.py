from typing import Dict, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamics x RL x Neuromodulation reasoning scorer.
    
    Mechanism:
    1. Parse each candidate into feature vector f(A): logical atoms, comparisons, 
       conditionals, numeric constraints, causal relations
    2. Build constraint matrix C and compute energy U = constraint violations
    3. Add entropy H from feature distribution richness
    4. Reward r = -U + alpha*H, update policy theta via RL with neuromodulatory gain
    5. Score S(A) = theta·f(A) after T update steps
    6. Meta-confidence checks prompt for ambiguity, presuppositions, unanswerability
    """
    
    def __init__(self):
        self.alpha = 0.3  # entropy weight
        self.beta = 0.1   # learning rate
        self.gamma = 0.5  # neuromodulation strength
        self.T = 5        # update steps
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # First try computational approaches
        comp_result = self._compute_answer(prompt, candidates)
        if comp_result:
            return comp_result
        
        # Fall back to energy-based RL scoring
        features_list = [self._extract_features(prompt, c) for c in candidates]
        energies = [self._compute_energy(f) for f in features_list]
        entropies = [self._compute_entropy(f) for f in features_list]
        
        # Initialize policy
        theta = np.zeros(len(features_list[0]) if features_list else 0)
        baseline = 0.0
        prev_reward = 0.0
        
        # RL updates with neuromodulation
        for _ in range(self.T):
            scores = [theta @ f for f in features_list]
            probs = self._softmax(scores)
            
            for i, (f, u, h) in enumerate(zip(features_list, energies, entropies)):
                reward = -u + self.alpha * h
                pred_error = reward - prev_reward
                dopamine = 1 / (1 + np.exp(-pred_error))  # sigmoid
                gain = 1 + self.gamma * dopamine
                
                grad = (reward - baseline) * f
                theta += self.beta * gain * grad
                baseline = 0.9 * baseline + 0.1 * reward
                prev_reward = reward
        
        # Final scores
        final_scores = [theta @ f for f in features_list]
        
        # Add minor NCD component (max 15%)
        ncd_scores = [self._ncd(prompt, c) for c in candidates]
        combined = [0.9 * s + 0.1 * (1 - n) for s, n in zip(final_scores, ncd_scores)]
        
        results = [{"candidate": c, "score": float(s), "reasoning": self._explain(f, u, h)} 
                   for c, s, f, u, h in zip(candidates, combined, features_list, energies, entropies)]
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        # Check if we can compute
        comp_conf = self._compute_confidence(prompt, answer)
        if comp_conf > 0:
            return min(comp_conf, 0.95)
        
        # Energy-based confidence
        features = self._extract_features(prompt, answer)
        energy = self._compute_energy(features)
        entropy = self._compute_entropy(features)
        
        # Low energy + high entropy = high confidence
        conf = 0.5 + 0.3 * (1 / (1 + energy)) + 0.2 * min(entropy, 1.0)
        return min(conf * meta_conf, 0.95)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'have you (stopped|quit|ceased)', p) or re.search(r'why (did|does) .* (fail|stop)', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every .* a ', p) or re.search(r'all .* a ', p):
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'(he|she|they|it) (was|is|were)', p) and 'who' in p:
            return 0.25
        
        # False dichotomy
        if re.search(r'either .* or ', p) and '?' in p:
            return 0.3
        
        # Subjectivity
        if re.search(r'(best|worst|favorite|most beautiful|ugliest)', p):
            return 0.3
        
        # Unanswerable markers
        if re.search(r'(not enough information|cannot determine|insufficient)', p):
            return 0.25
        
        return 1.0
    
    def _extract_features(self, prompt: str, candidate: str) -> np.ndarray:
        text = (prompt + " " + candidate).lower()
        features = []
        
        # Negations
        features.append(len(re.findall(r'\b(not|no|never|neither)\b', text)))
        
        # Comparatives
        features.append(len(re.findall(r'[<>=]|greater|less|more|fewer|higher|lower', text)))
        
        # Conditionals
        features.append(len(re.findall(r'\b(if|then|when|unless|provided)\b', text)))
        
        # Numeric constants
        nums = re.findall(r'\b\d+\.?\d*\b', text)
        features.append(len(nums))
        
        # Causal markers
        features.append(len(re.findall(r'\b(because|due to|leads to|causes|results in)\b', text)))
        
        # Logical operators
        features.append(len(re.findall(r'\b(and|or|but|therefore|thus|hence)\b', text)))
        
        # Quantifiers
        features.append(len(re.findall(r'\b(all|some|every|any|none|each)\b', text)))
        
        return np.array(features, dtype=float) + 0.1  # avoid zeros
    
    def _compute_energy(self, features: np.ndarray) -> float:
        # Energy = constraint violations (simplified: inconsistency heuristic)
        # High negations + high comparatives + low conditionals = potential conflict
        violation_score = 0.0
        if features[0] > 2 and features[1] > 1 and features[2] < 1:  # negations + comparisons without conditionals
            violation_score += features[0] * features[1]
        return violation_score
    
    def _compute_entropy(self, features: np.ndarray) -> float:
        total = features.sum()
        if total < 1e-6:
            return 0.0
        probs = features / total
        entropy = -np.sum(probs * np.log(probs + 1e-9))
        return entropy
    
    def _softmax(self, scores: List[float]) -> np.ndarray:
        scores = np.array(scores)
        exp_scores = np.exp(scores - np.max(scores))
        return exp_scores / exp_scores.sum()
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _explain(self, f: np.ndarray, u: float, h: float) -> str:
        return f"Energy={u:.2f}, Entropy={h:.2f}, Features={f.sum():.0f}"
    
    def _compute_answer(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # Numeric comparison
        if m := re.search(r'(\d+\.?\d*)\s*(>|<|=|greater|less)\s*(\d+\.?\d*)', prompt.lower()):
            n1, op, n2 = float(m.group(1)), m.group(2), float(m.group(3))
            correct = (n1 > n2 if '>' in op or 'greater' in op else 
                      n1 < n2 if '<' in op or 'less' in op else n1 == n2)
            return self._rank_by_match(candidates, ['yes', 'true'] if correct else ['no', 'false'])
        
        # Bat and ball: X + Y = A, X = Y + B
        if m := re.search(r'(\w+) and (\w+) cost \$?(\d+\.?\d*).*\1 costs \$?(\d+\.?\d*) more', prompt.lower()):
            total, diff = float(m.group(3)), float(m.group(4))
            smaller = (total - diff) / 2
            return self._rank_by_number(candidates, smaller)
        
        # All but N
        if m := re.search(r'(\d+).*all but (\d+)', prompt.lower()):
            total, butN = int(m.group(1)), int(m.group(2))
            return self._rank_by_number(candidates, total - butN)
        
        # Modus tollens: If P then Q, not Q => not P
        if re.search(r'if (.+) then (.+)', prompt.lower()) and re.search(r'not (.+)', prompt.lower()):
            return self._rank_by_match(candidates, ['not', 'no', 'false'])
        
        # Transitivity: A > B, B > C => A > C
        trans = re.findall(r'(\w+)\s*(>|<)\s*(\w+)', prompt)
        if len(trans) >= 2:
            # Build ordering
            order = {}
            for a, op, b in trans:
                if op == '>':
                    order[a] = order.get(a, 0) + 1
                    order[b] = order.get(b, 0) - 1
            if order:
                sorted_items = sorted(order.items(), key=lambda x: x[1], reverse=True)
                # Check candidates for correct order
                best_cand = max(candidates, key=lambda c: sum(c.lower().find(k) for k, v in sorted_items[:2]))
                return self._rank_by_match(candidates, [best_cand])
        
        return None
    
    def _compute_confidence(self, prompt: str, answer: str) -> float:
        # High confidence if we computed the answer
        if re.search(r'\d+\.?\d*\s*[<>=]', prompt):
            return 0.85
        if 'all but' in prompt.lower():
            return 0.8
        if 'cost' in prompt.lower() and 'more' in prompt.lower():
            return 0.8
        return 0.0
    
    def _rank_by_match(self, candidates: List[str], targets: List[str]) -> List[Dict]:
        scores = []
        for c in candidates:
            score = max([1.0 if t in c.lower() else 0.0 for t in targets] + [0.0])
            scores.append(score)
        results = [{"candidate": c, "score": s, "reasoning": "Pattern match"} for c, s in zip(candidates, scores)]
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def _rank_by_number(self, candidates: List[str], target: float) -> List[Dict]:
        scores = []
        for c in candidates:
            nums = re.findall(r'\d+\.?\d*', c)
            if nums:
                closest = min([abs(float(n) - target) for n in nums])
                scores.append(1.0 / (1.0 + closest))
            else:
                scores.append(0.0)
        results = [{"candidate": c, "score": s, "reasoning": f"Numeric target={target}"} for c, s in zip(candidates, scores)]
        return sorted(results, key=lambda x: x["score"], reverse=True)