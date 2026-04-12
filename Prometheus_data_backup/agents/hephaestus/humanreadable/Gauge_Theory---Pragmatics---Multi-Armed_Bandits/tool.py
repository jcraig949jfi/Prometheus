from typing import Dict, Tuple

import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-Armed Bandit + Gauge Theory + Constraint Propagation reasoning.
    
    Treats each candidate as a bandit arm, extracts propositions with context-dependent
    gauge transformations, propagates constraints through a logical graph, and uses
    UCB to iteratively evaluate consistency and pragmatic plausibility.
    """
    
    def __init__(self):
        self.w_cons = 0.5
        self.w_prag = 0.35
        self.w_ncd = 0.15
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        n = len(candidates)
        if n == 0:
            return []
        if n == 1:
            return [{"candidate": candidates[0], "score": 0.5, "reasoning": "single"}]
        
        # Compute once for NCD
        p_comp = zlib.compress(prompt.encode())
        
        # Multi-armed bandit state
        counts = np.zeros(n)
        rewards = np.zeros(n)
        total_evals = 0
        budget = min(20, n * 5)
        
        for _ in range(budget):
            total_evals += 1
            ucb = np.where(counts > 0, 
                          rewards / counts + np.sqrt(2 * np.log(total_evals) / counts),
                          1e9)
            arm = np.argmax(ucb)
            
            # Evaluate arm
            r = self._evaluate_arm(prompt, candidates[arm], p_comp)
            counts[arm] += 1
            rewards[arm] += r
        
        # Final scores
        scores = np.where(counts > 0, rewards / counts, 0.0)
        results = [{"candidate": candidates[i], "score": float(scores[i]), 
                   "reasoning": f"ucb_eval_{int(counts[i])}"} 
                  for i in range(n)]
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def _evaluate_arm(self, prompt: str, candidate: str, p_comp: bytes) -> float:
        # Numeric computation
        num_score = self._numeric_eval(prompt, candidate)
        if num_score >= 0:
            return 0.4 * num_score + 0.6 * self._structural_eval(prompt, candidate, p_comp)
        
        # Structural + constraint propagation
        props = self._extract_propositions(candidate)
        gauge_adj = self._gauge_transform(props)
        contras = self._constraint_propagate(props)
        
        cons_score = 1.0 - min(1.0, contras / max(1, len(props)))
        prag_score = np.mean(gauge_adj) if len(gauge_adj) > 0 else 0.5
        
        # NCD tiebreaker
        c_comp = zlib.compress(candidate.encode())
        pc_comp = zlib.compress((prompt + candidate).encode())
        ncd = (len(pc_comp) - min(len(p_comp), len(c_comp))) / max(len(p_comp), len(c_comp))
        ncd_score = max(0, 1 - ncd)
        
        return self.w_cons * cons_score + self.w_prag * prag_score + self.w_ncd * ncd_score
    
    def _numeric_eval(self, prompt: str, candidate: str) -> float:
        # Version comparison (9.11 vs 9.9)
        if re.search(r'\d+\.\d+.*\d+\.\d+', prompt):
            nums = re.findall(r'\d+\.\d+', prompt)
            if len(nums) >= 2:
                v1, v2 = float(nums[0]), float(nums[1])
                if 'greater' in prompt.lower() or 'larger' in prompt.lower():
                    return 1.0 if (str(v1) in candidate and v1 > v2) or (str(v2) in candidate and v2 > v1) else 0.0
                elif 'less' in prompt.lower() or 'smaller' in prompt.lower():
                    return 1.0 if (str(v1) in candidate and v1 < v2) or (str(v2) in candidate and v2 < v1) else 0.0
        
        # Probability computation
        if 'probability' in prompt.lower() or 'percent' in prompt.lower():
            prob_nums = re.findall(r'(\d+(?:\.\d+)?)%', prompt)
            if prob_nums:
                ans_nums = re.findall(r'(\d+(?:\.\d+)?)%', candidate)
                if ans_nums:
                    return 0.8
        
        return -1.0
    
    def _structural_eval(self, prompt: str, candidate: str, p_comp: bytes) -> float:
        # Negation matching
        p_neg = bool(re.search(r'\b(no|not|never|neither|cannot|n\'t)\b', prompt.lower()))
        c_neg = bool(re.search(r'\b(no|not|never|neither|cannot|n\'t)\b', candidate.lower()))
        
        neg_match = 0.7 if p_neg == c_neg else 0.3
        
        # NCD
        c_comp = zlib.compress(candidate.encode())
        pc_comp = zlib.compress((prompt + candidate).encode())
        ncd = (len(pc_comp) - min(len(p_comp), len(c_comp))) / max(len(p_comp), len(c_comp))
        
        return 0.6 * neg_match + 0.4 * max(0, 1 - ncd)
    
    def _extract_propositions(self, text: str) -> List[Tuple[str, str, str, bool, str]]:
        props = []
        sents = re.split(r'[.!?]', text)
        
        for s in sents:
            s = s.strip()
            if len(s) < 5:
                continue
            
            # Polarity
            neg = bool(re.search(r'\b(no|not|never|neither|none|cannot|n\'t)\b', s.lower()))
            
            # Modality
            modal = 'must' if re.search(r'\b(must|have to|required)\b', s.lower()) else \
                   'might' if re.search(r'\b(might|may|could|possibly)\b', s.lower()) else 'certain'
            
            # Simple subject-verb-object
            words = s.split()
            subj = words[0] if words else ''
            pred = words[1] if len(words) > 1 else ''
            obj = ' '.join(words[2:]) if len(words) > 2 else ''
            
            props.append((subj, pred, obj, neg, modal))
        
        return props
    
    def _gauge_transform(self, props: List[Tuple]) -> np.ndarray:
        if not props:
            return np.array([0.5])
        
        truth = np.ones(len(props))
        
        for i, (_, _, _, neg, modal) in enumerate(props):
            # Context gauge: modality scales truth
            if modal == 'might':
                truth[i] *= 0.5
            elif modal == 'must':
                truth[i] *= 1.0
            
            # Negation inverts
            if neg:
                truth[i] = 1.0 - truth[i]
        
        return truth
    
    def _constraint_propagate(self, props: List[Tuple]) -> int:
        n = len(props)
        if n == 0:
            return 0
        
        # Build adjacency matrix
        edges = np.zeros((n, n), dtype=bool)
        
        for i in range(n):
            for j in range(i + 1, n):
                # Same subject/object -> constraint
                if props[i][0] == props[j][0] or props[i][2] == props[j][2]:
                    edges[i, j] = True
        
        # Transitive closure (Floyd-Warshall style)
        reach = edges.copy()
        for _ in range(n):
            reach = reach | (reach @ reach)
        
        # Detect contradictions
        contras = 0
        for i in range(n):
            for j in range(i + 1, n):
                if reach[i, j] and reach[j, i]:
                    if props[i][3] != props[j][3]:  # Opposite polarity
                        contras += 1
        
        return contras
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta = self._meta_confidence(prompt)
        
        # Numeric computation confidence
        if re.search(r'\d+\.\d+', prompt) and re.search(r'\d+\.\d+', answer):
            base = 0.75
        else:
            base = 0.5
        
        # Structural match
        p_words = set(prompt.lower().split())
        a_words = set(answer.lower().split())
        overlap = len(p_words & a_words) / max(len(p_words), 1)
        
        struct_conf = min(0.85, 0.3 + 0.5 * overlap)
        
        return min(meta, base * 0.4 + struct_conf * 0.6)
    
    def _meta_confidence(self, prompt: str) -> float:
        p_low = prompt.lower()
        
        # Presupposition
        if re.search(r'\b(have you stopped|did you quit|why did.*fail|when did.*stop)\b', p_low):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'\bevery\b.*\ba\b', p_low):
            return 0.28
        
        # Pronoun ambiguity
        if re.search(r'\b(he|she|it|they)\b', p_low) and 'who' in p_low:
            return 0.27
        
        # False dichotomy
        if re.search(r'\beither\b.*\bor\b', p_low) and 'only' not in p_low:
            return 0.26
        
        # Subjectivity
        if re.search(r'\b(best|worst|favorite|most beautiful|ugliest)\b', p_low):
            return 0.29
        
        # Question marks suggest uncertainty
        if p_low.count('?') > 2:
            return 0.35
        
        return 0.95