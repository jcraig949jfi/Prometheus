from typing import Dict, Set, Tuple

"""
Reasoning tool combining Chaos Theory, Gene Regulatory Networks, and Sensitivity Analysis.
Parses text into signed weighted directed graphs, simulates GRN dynamics, and uses Lyapunov
exponent approximation + attractor distance to score reasoning robustness.
"""
import re
import numpy as np
from collections import defaultdict
from typing import List, Dict, Tuple, Set

class ReasoningTool:
    def __init__(self):
        self.T = 20  # simulation steps
        self.alpha = 0.5  # attractor weight
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # Try computational approaches first
            comp_score = self._compute_answer(prompt, cand)
            if comp_score is not None:
                score = comp_score
                reasoning = "Computational"
            else:
                # GRN dynamics approach
                score = self._grn_score(prompt, cand)
                reasoning = "GRN_dynamics"
            
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        comp_score = self._compute_answer(prompt, answer)
        if comp_score is not None and comp_score > 0.8:
            return min(0.95, meta_conf)
        
        score = self._grn_score(prompt, answer)
        base_conf = min(0.7, (score + 1) / 2)
        return min(base_conf, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        # Presupposition
        if re.search(r'\b(have you stopped|have you quit|why did \w+ (fail|stop))', p):
            return 0.2
        # Scope ambiguity
        if re.search(r'\bevery \w+.*\ba \w+', p):
            return 0.25
        # Pronoun ambiguity with "who?"
        if re.search(r'\b(he|she)\b', p) and 'who' in p:
            return 0.25
        # False dichotomy
        if re.search(r'\beither \w+ or \w+\b', p) and 'only' not in p:
            return 0.3
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p) and not re.search(r'\b(most|least|tallest|shortest|largest|smallest)\b', p):
            return 0.3
        return 0.8
    
    def _compute_answer(self, prompt: str, answer: str) -> float:
        # Numeric comparison
        nums_p = re.findall(r'\d+\.?\d*', prompt)
        if len(nums_p) >= 2 and any(w in prompt.lower() for w in ['greater', 'less', 'larger', 'smaller', 'more', 'fewer']):
            try:
                a, b = float(nums_p[0]), float(nums_p[1])
                if 'greater' in prompt.lower() or 'larger' in prompt.lower() or 'more' in prompt.lower():
                    correct = a > b
                else:
                    correct = a < b
                if (correct and 'yes' in answer.lower()) or (not correct and 'no' in answer.lower()):
                    return 1.0
                return 0.0
            except:
                pass
        
        # Bat-and-ball algebra
        if 'bat and ball' in prompt.lower() or 'cost' in prompt.lower() and 'more than' in prompt.lower():
            m = re.search(r'total.*\$?(\d+\.?\d*)', prompt.lower())
            m2 = re.search(r'more than.*\$?(\d+\.?\d*)', prompt.lower())
            if m and m2:
                total, diff = float(m.group(1)), float(m2.group(1))
                ball = (total - diff) / 2
                nums_a = re.findall(r'\d+\.?\d*', answer)
                if nums_a and abs(float(nums_a[0]) - ball) < 0.01:
                    return 1.0
                return 0.0
        
        # Modus tollens
        if 'if' in prompt.lower() and 'then' in prompt.lower():
            return self._logical_inference(prompt, answer)
        
        return None
    
    def _logical_inference(self, prompt: str, answer: str) -> float:
        # Simple modus tollens / ponens
        if_match = re.search(r'if (.*?) then (.*?)[\.\?]', prompt.lower())
        if if_match:
            antecedent = if_match.group(1).strip()
            consequent = if_match.group(2).strip()
            
            # Check for negations
            not_conseq = any(w in prompt.lower() for w in ['not ' + consequent, consequent + ' is false'])
            has_ante = antecedent in prompt.lower()
            
            if not_conseq and 'not ' + antecedent in answer.lower():
                return 0.9
            if has_ante and consequent in answer.lower():
                return 0.9
        return 0.5
    
    def _grn_score(self, prompt: str, candidate: str) -> float:
        combined = prompt + " " + candidate
        G, vocab = self._parse_graph(combined)
        n = len(vocab)
        if n == 0:
            return self._ncd(prompt, candidate)
        
        # Initialize state
        x = np.full(n, 0.5)
        prompt_words = set(prompt.lower().split())
        for i, word in enumerate(vocab):
            if word in prompt_words:
                x[i] = 0.7
        
        # Dynamics
        S, W, b = G
        trajectory = [x.copy()]
        for t in range(self.T):
            z = b + (S * W) @ x
            x = 1 / (1 + np.exp(-np.clip(z, -10, 10)))
            trajectory.append(x.copy())
        
        # Sensitivity
        lambda_max = 0.0
        v = np.random.randn(n)
        v /= np.linalg.norm(v) + 1e-9
        for t in range(self.T):
            x_t = trajectory[t]
            z = b + (S * W) @ x_t
            sigma_prime = np.exp(-z) / (1 + np.exp(-z))**2
            J = np.diag(sigma_prime) @ (S * W)
            v = J @ v
            norm_v = np.linalg.norm(v) + 1e-9
            lambda_max += np.log(norm_v)
            v /= norm_v
        lambda_max /= self.T
        
        # Attractor distance
        x_final = trajectory[-1]
        x_star = x_final.copy()
        for _ in range(10):
            z = b + (S * W) @ x_star
            x_star = 1 / (1 + np.exp(-np.clip(z, -10, 10)))
        
        dist = np.linalg.norm(x_final - x_star)
        score = -lambda_max - self.alpha * dist
        
        # Add NCD tiebreaker (< 15%)
        ncd = self._ncd(prompt, candidate)
        return 0.85 * score + 0.15 * (1 - ncd)
    
    def _parse_graph(self, text: str) -> Tuple[Tuple[np.ndarray, np.ndarray, np.ndarray], List[str]]:
        words = re.findall(r'\b\w+\b', text.lower())
        vocab = list(dict.fromkeys(words))
        n = len(vocab)
        word_to_idx = {w: i for i, w in enumerate(vocab)}
        
        S = np.zeros((n, n))
        W = np.zeros((n, n))
        b = np.zeros(n)
        
        # Causal patterns
        causal = re.findall(r'(\w+)\s+(causes?|leads? to|results? in|implies)\s+(\w+)', text.lower())
        for src, _, tgt in causal:
            if src in word_to_idx and tgt in word_to_idx:
                i, j = word_to_idx[src], word_to_idx[tgt]
                S[j, i] = 1
                W[j, i] = 0.8
        
        # Conditionals
        cond = re.findall(r'if\s+(\w+)\s+then\s+(\w+)', text.lower())
        for ante, cons in cond:
            if ante in word_to_idx and cons in word_to_idx:
                i, j = word_to_idx[ante], word_to_idx[cons]
                S[j, i] = 1
                W[j, i] = 0.9
        
        # Negations
        neg = re.findall(r'not\s+(\w+)', text.lower())
        for word in neg:
            if word in word_to_idx:
                idx = word_to_idx[word]
                S[:, idx] *= -1
        
        # Comparatives
        comp = re.findall(r'(\w+)\s+(much more|more|less|slightly)\s+(\w+)', text.lower())
        for src, strength, tgt in comp:
            if src in word_to_idx and tgt in word_to_idx:
                i, j = word_to_idx[src], word_to_idx[tgt]
                weight = {'much more': 0.9, 'more': 0.7, 'less': 0.3, 'slightly': 0.2}.get(strength, 0.5)
                sign = 1 if 'more' in strength else -1
                S[j, i] = sign
                W[j, i] = weight
        
        # Numbers as bias
        for word in vocab:
            try:
                val = float(word)
                b[word_to_idx[word]] = np.tanh(val / 10.0)
            except:
                pass
        
        return (S, W, b), vocab
    
    def _ncd(self, s1: str, s2: str) -> float:
        import zlib
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2, 1)