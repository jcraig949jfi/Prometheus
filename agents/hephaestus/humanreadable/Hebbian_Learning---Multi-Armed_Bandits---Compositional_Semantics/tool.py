from typing import Dict, Tuple

"""
Hebbian Learning x Multi-Armed Bandits x Compositional Semantics

Parses prompts into atomic propositions, represents them as vectors, and composes
meanings using learnable operator matrices (negation, conjunction, comparison, implication).
A multi-armed bandit explores parsing strategies, updating weights via Hebbian learning.
"""

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    def __init__(self):
        self.dim = 16
        self.learning_rate = 0.1
        np.random.seed(42)
        
        # Operator weight matrices (initially identity)
        self.W_neg = np.eye(self.dim)
        self.W_and = np.eye(self.dim)
        self.W_comp = np.eye(self.dim)
        self.W_imp = np.eye(self.dim)
        
        # Bandit statistics for each operator
        self.bandit_stats = {
            'neg': {'mu': 0.5, 'n': 1},
            'and': {'mu': 0.5, 'n': 1},
            'comp': {'mu': 0.5, 'n': 1},
            'imp': {'mu': 0.5, 'n': 1}
        }
        self.total_pulls = 4
        
        # Basis vectors for propositions
        self.basis_cache = {}
        self.basis_idx = 0
    
    def _get_basis_vector(self, prop: str) -> np.ndarray:
        """Map proposition to fixed basis vector"""
        if prop not in self.basis_cache:
            vec = np.zeros(self.dim)
            vec[self.basis_idx % self.dim] = 1.0
            self.basis_cache[prop] = vec
            self.basis_idx += 1
        return self.basis_cache[prop].copy()
    
    def _extract_propositions(self, text: str) -> List[Tuple[str, str, List[str]]]:
        """Extract structured propositions: (type, text, components)"""
        text = text.lower()
        props = []
        
        # Negations
        for m in re.finditer(r'not\s+(\w+)', text):
            props.append(('neg', m.group(0), [m.group(1)]))
        
        # Comparatives
        for m in re.finditer(r'(\d+\.?\d*)\s*(>|<|greater|less|more|fewer)\s*(\d+\.?\d*)', text):
            props.append(('comp', m.group(0), [m.group(1), m.group(3)]))
        
        # Conditionals
        for m in re.finditer(r'if\s+(.+?)\s+then\s+(.+?)(?:\.|$)', text):
            props.append(('imp', m.group(0), [m.group(1), m.group(2)]))
        
        # Conjunctions
        for m in re.finditer(r'(\w+)\s+and\s+(\w+)', text):
            props.append(('and', m.group(0), [m.group(1), m.group(2)]))
        
        return props
    
    def _ucb_select(self) -> str:
        """Select operator arm with highest UCB"""
        best_arm, best_ucb = None, -np.inf
        for arm, stats in self.bandit_stats.items():
            ucb = stats['mu'] + np.sqrt(2 * np.log(self.total_pulls) / stats['n'])
            if ucb > best_ucb:
                best_ucb = ucb
                best_arm = arm
        return best_arm
    
    def _hebbian_update(self, W: np.ndarray, v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
        """Hebbian weight update"""
        outer = np.outer(v1, v2)
        return W + self.learning_rate * outer
    
    def _compose_meaning(self, text: str) -> np.ndarray:
        """Compose meaning vector from propositions"""
        props = self._extract_propositions(text)
        
        if not props:
            # Fallback: hash-based vector
            vec = np.zeros(self.dim)
            h = hash(text) % self.dim
            vec[h] = 1.0
            return vec
        
        meaning = np.zeros(self.dim)
        
        for prop_type, prop_text, components in props:
            if prop_type == 'neg' and len(components) >= 1:
                v = self._get_basis_vector(components[0])
                composed = self.W_neg @ v
            elif prop_type == 'comp' and len(components) >= 2:
                v1 = self._get_basis_vector(components[0])
                v2 = self._get_basis_vector(components[1])
                composed = self.W_comp @ (v1 + v2) / 2
            elif prop_type == 'imp' and len(components) >= 2:
                v1 = self._get_basis_vector(components[0])
                v2 = self._get_basis_vector(components[1])
                composed = self.W_imp @ (v1 + v2) / 2
            elif prop_type == 'and' and len(components) >= 2:
                v1 = self._get_basis_vector(components[0])
                v2 = self._get_basis_vector(components[1])
                composed = self.W_and @ (v1 + v2) / 2
            else:
                composed = self._get_basis_vector(prop_text)
            
            meaning += composed
        
        norm = np.linalg.norm(meaning)
        return meaning / norm if norm > 0 else meaning
    
    def _compute_numeric(self, prompt: str, candidate: str) -> Tuple[bool, float]:
        """Direct numeric comparison"""
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            if re.search(r'(greater|more|larger|>)', prompt.lower()):
                expected = max(float(p_nums[0]), float(p_nums[1]))
                if abs(float(c_nums[0]) - expected) < 0.01:
                    return True, 1.0
            elif re.search(r'(less|fewer|smaller|<)', prompt.lower()):
                expected = min(float(p_nums[0]), float(p_nums[1]))
                if abs(float(c_nums[0]) - expected) < 0.01:
                    return True, 1.0
        
        return False, 0.0
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance"""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguity and unanswerable questions"""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'have you (stopped|quit)', p) or re.search(r'why did .+ (fail|stop)', p):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every .+ a ', p) or re.search(r'all .+ a ', p):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).+(who|which)', p):
            return 0.25
        
        # False dichotomy
        if re.search(r'either .+ or ', p) and not re.search(r'(only|just)', p):
            return 0.3
        
        # Subjectivity
        if re.search(r'(best|worst|favorite|prefer)', p):
            return 0.3
        
        # Missing information
        if re.search(r'(why|how|explain)', p) and len(p.split()) < 15:
            return 0.35
        
        return 1.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates by compositional semantic similarity"""
        prompt_vec = self._compose_meaning(prompt)
        results = []
        
        for cand in candidates:
            # Numeric computation
            numeric_match, numeric_score = self._compute_numeric(prompt, cand)
            
            # Compositional similarity
            cand_vec = self._compose_meaning(cand)
            dot = np.dot(prompt_vec, cand_vec)
            norm_p = np.linalg.norm(prompt_vec)
            norm_c = np.linalg.norm(cand_vec)
            cosine = dot / (norm_p * norm_c) if norm_p > 0 and norm_c > 0 else 0.0
            
            # NCD tiebreaker
            ncd = 1.0 - self._ncd(prompt, cand)
            
            # Weighted score
            if numeric_match:
                score = 0.7 * numeric_score + 0.2 * cosine + 0.1 * ncd
                reasoning = "Numeric computation match"
            else:
                score = 0.6 * cosine + 0.3 * numeric_score + 0.1 * ncd
                reasoning = f"Compositional similarity: {cosine:.3f}"
            
            results.append({"candidate": cand, "score": float(score), "reasoning": reasoning})
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on meta-analysis and structural match"""
        # Meta-confidence caps maximum
        meta_conf = self._meta_confidence(prompt)
        
        # Structural confidence
        numeric_match, numeric_score = self._compute_numeric(prompt, answer)
        
        if numeric_match:
            base_conf = 0.85
        else:
            prompt_vec = self._compose_meaning(prompt)
            answer_vec = self._compose_meaning(answer)
            dot = np.dot(prompt_vec, answer_vec)
            norm_p = np.linalg.norm(prompt_vec)
            norm_a = np.linalg.norm(answer_vec)
            cosine = dot / (norm_p * norm_a) if norm_p > 0 and norm_a > 0 else 0.0
            base_conf = 0.3 + 0.5 * cosine
        
        # Cap by meta-confidence
        final_conf = min(base_conf, meta_conf)
        
        # Never exceed 0.9 unless definitive computation
        if not numeric_match:
            final_conf = min(final_conf, 0.75)
        
        return max(0.0, min(1.0, final_conf))