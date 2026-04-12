from typing import Dict, Tuple

"""
Functor-Driven Constraint-Propagation Scorer with PID Feedback Control.

Maps text to categorical objects (proposition vectors), applies functorial morphisms
(linear operators for logical relations), and uses PID control to iteratively align
candidate answers with the question context.
"""

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    def __init__(self):
        # PID gains
        self.Kp, self.Ki, self.Kd = 0.1, 0.01, 0.05
        self.T = 5  # PID iterations
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = self.confidence(prompt, cand)
            reasoning = self._explain_score(prompt, cand)
            results.append({"candidate": cand, "score": score * conf, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        struct_match = self._structural_match(prompt, answer)
        numeric_conf = self._numeric_confidence(prompt, answer)
        return min(0.95, max(meta_conf, struct_match * 0.7, numeric_conf))
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        # Presupposition traps
        if re.search(r'\b(have you stopped|have you quit|why did .* (fail|stop))', p):
            return 0.2
        # Scope ambiguity
        if re.search(r'\bevery .* a \b', p):
            return 0.25
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p) and 'who' in p:
            return 0.25
        # False dichotomy
        if re.search(r'\beither .* or\b', p) and '?' in p:
            return 0.3
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|most beautiful)\b', p) and not re.search(r'\b(by|according to|measured)\b', p):
            return 0.3
        # Unanswerable meta-questions
        if re.search(r'\b(can (we|you) know|is it possible to determine)\b', p):
            return 0.35
        return 0.6
    
    def _parse_propositions(self, text: str) -> Tuple[np.ndarray, List[str]]:
        text = text.lower()
        # Extract atomic propositions (simple subject-predicate-object)
        props = re.findall(r'\b([a-z]+)\s+(is|are|was|were|has|have|does|do)\s+([a-z]+)', text)
        props += re.findall(r'\b([a-z]+)\s+([a-z]+ed|[a-z]+ing)\s+([a-z]+)', text)
        props = [' '.join(p) for p in props] if props else [text[:30]]
        
        # Build basis
        basis = list(set(props))
        if not basis:
            basis = ['default']
        
        # One-hot vector for text
        vec = np.zeros(max(8, len(basis)))
        for i, p in enumerate(basis[:len(vec)]):
            if p in text:
                vec[i] = 1.0
        
        # Extract numbers
        nums = re.findall(r'\b\d+\.?\d*\b', text)
        if nums:
            vec[0] = float(nums[0]) if len(nums) == 1 else len(nums)
        
        return vec, basis
    
    def _get_relation_operators(self, text: str, dim: int) -> np.ndarray:
        M = np.eye(dim)
        text = text.lower()
        
        # Negation: flip sign
        if re.search(r'\b(not|no|never|neither)\b', text):
            M = -np.eye(dim)
        
        # Comparatives: shift
        if re.search(r'\b(greater|more|higher|larger)\b', text):
            M = np.roll(M, 1, axis=0)
        elif re.search(r'\b(less|fewer|lower|smaller)\b', text):
            M = np.roll(M, -1, axis=0)
        
        # Conditionals: scale
        if re.search(r'\b(if|then|implies)\b', text):
            M *= 0.8
        
        # Causals: dampen
        if re.search(r'\b(because|causes|leads to)\b', text):
            M *= 0.5
        
        return M
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        # Parse to vectors
        q_vec, q_basis = self._parse_propositions(prompt)
        a_vec, a_basis = self._parse_propositions(candidate)
        
        dim = max(len(q_vec), len(a_vec))
        q_vec = np.pad(q_vec, (0, dim - len(q_vec)))
        a_vec = np.pad(a_vec, (0, dim - len(a_vec)))
        
        # Get morphism from candidate
        M_ans = self._get_relation_operators(candidate, dim)
        
        # Apply functor
        a_hat = M_ans @ q_vec
        
        # PID loop
        w = 1.0
        e_sum = 0.0
        e_prev = 0.0
        
        for t in range(self.T):
            e = np.linalg.norm(a_vec - a_hat)
            e_sum += e
            w += self.Kp * e + self.Ki * e_sum + self.Kd * (e - e_prev)
            e_prev = e
            if e < 1e-3:
                break
        
        # Structural score
        struct_score = 1.0 / (1.0 + np.exp(-w * np.linalg.norm(a_hat)))
        
        # Numeric computation
        numeric_score = self._numeric_match(prompt, candidate)
        
        # NCD tiebreaker (max 15%)
        ncd = self._ncd(prompt, candidate)
        
        # Weighted combination
        final = 0.55 * struct_score + 0.30 * numeric_score + 0.15 * (1 - ncd)
        return final
    
    def _numeric_match(self, prompt: str, candidate: str) -> float:
        # Extract and compare numbers
        p_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', prompt)]
        c_nums = [float(x) for x in re.findall(r'\b\d+\.?\d*\b', candidate)]
        
        if not p_nums or not c_nums:
            return 0.5
        
        # Check comparative relations
        if re.search(r'\b(greater|more|larger)\b', prompt):
            if c_nums and p_nums and c_nums[0] > p_nums[0]:
                return 1.0
            return 0.0
        elif re.search(r'\b(less|fewer|smaller)\b', prompt):
            if c_nums and p_nums and c_nums[0] < p_nums[0]:
                return 1.0
            return 0.0
        
        # Numeric proximity
        if c_nums and p_nums:
            diff = abs(c_nums[0] - p_nums[0])
            return np.exp(-diff / (1.0 + abs(p_nums[0])))
        
        return 0.5
    
    def _structural_match(self, prompt: str, answer: str) -> float:
        score = 0.5
        p, a = prompt.lower(), answer.lower()
        
        # Negation consistency
        p_neg = bool(re.search(r'\b(not|no|never)\b', p))
        a_neg = bool(re.search(r'\b(not|no|never)\b', a))
        if p_neg == a_neg:
            score += 0.2
        
        # Conditional structure
        if 'if' in p and 'then' in a:
            score += 0.15
        
        return min(1.0, score)
    
    def _numeric_confidence(self, prompt: str, answer: str) -> float:
        # High confidence if we computed a definitive numeric answer
        if re.search(r'\b\d+\.?\d*\b', answer) and re.search(r'(calculate|compute|how many)', prompt.lower()):
            return 0.85
        return 0.5
    
    def _ncd(self, s1: str, s2: str) -> float:
        c1, c2 = zlib.compress(s1.encode()), zlib.compress(s2.encode())
        c12 = zlib.compress((s1 + s2).encode())
        ncd = (len(c12) - min(len(c1), len(c2))) / max(len(c1), len(c2))
        return min(1.0, max(0.0, ncd))
    
    def _explain_score(self, prompt: str, candidate: str) -> str:
        meta = self._meta_confidence(prompt)
        if meta < 0.35:
            return "Low confidence: prompt contains ambiguity or presupposition"
        
        num_match = self._numeric_match(prompt, candidate)
        if num_match > 0.8:
            return "High structural + numeric alignment via functor mapping"
        elif num_match < 0.2:
            return "Numeric mismatch detected"
        else:
            return "Moderate semantic alignment via PID-controlled vector projection"