from typing import Dict, Optional, Tuple

"""
Neuromodulation x Pragmatics x Compositional Semantics Reasoning Tool

Combines logical parsing, pragmatic scoring, and gain control for robust evaluation.
"""

import re
import numpy as np
from collections import Counter
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    def __init__(self):
        self.max_prop_id = 0
        self.prop_to_id = {}
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            conf = self.confidence(prompt, cand)
            reasoning = self._explain_score(prompt, cand, score)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        computed = self._compute_answer(prompt)
        if computed is not None and str(computed).lower().strip() in answer.lower():
            return min(0.95, meta_conf)
        structural_match = self._has_structural_match(prompt, answer)
        if not structural_match:
            return min(0.25, meta_conf)
        return min(0.7, meta_conf)
    
    def _meta_confidence(self, prompt: str) -> float:
        p = prompt.lower()
        # Presupposition detection
        if re.search(r'\b(have you stopped|have you quit|why did .+ (fail|stop|end))\b', p):
            return 0.2
        # Scope ambiguity
        if re.search(r'\bevery .{1,50} a \w+', p) and 'same' not in p:
            return 0.25
        # Pronoun ambiguity with explicit "who" question
        if re.search(r'\b(he|she|they|it)\b', p) and re.search(r'\bwho\b', p):
            return 0.25
        # False dichotomy
        if re.search(r'\b(either .+ or .+|only two)', p) and 'only' not in p:
            return 0.3
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', p) and not re.search(r'\b(most|least|faster|slower|cheaper)\b', p):
            return 0.3
        # Insufficient information
        if re.search(r'\b(not enough|cannot determine|insufficient)\b', p):
            return 0.2
        return 1.0
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        structural_score = self._structural_score(prompt, candidate)
        computation_score = self._computation_score(prompt, candidate)
        ncd_score = self._ncd_score(prompt, candidate)
        return 0.55 * structural_score + 0.3 * computation_score + 0.15 * ncd_score
    
    def _structural_score(self, prompt: str, candidate: str) -> float:
        self.max_prop_id = 0
        self.prop_to_id = {}
        
        prompt_props = self._extract_propositions(prompt)
        cand_props = self._extract_propositions(candidate)
        
        if not prompt_props and not cand_props:
            return 0.5
        
        n = max(self.max_prop_id, 1)
        imp_matrix = np.zeros((n, n))
        pol_prompt = np.zeros(n)
        pol_cand = np.zeros(n)
        
        for prop, polarity, prop_type in prompt_props:
            pid = self._get_prop_id(prop)
            pol_prompt[pid] = 1 if polarity else -1
        
        for prop, polarity, prop_type in cand_props:
            pid = self._get_prop_id(prop)
            pol_cand[pid] = 1 if polarity else -1
        
        # Extract implications
        implications = self._extract_implications(prompt) + self._extract_implications(candidate)
        for ant, cons in implications:
            ant_id = self._get_prop_id(ant)
            cons_id = self._get_prop_id(cons)
            imp_matrix[ant_id, cons_id] = 1
        
        # Neuromodulatory gain
        gain = self._compute_gain(prompt, candidate, n)
        
        # Pragmatic weights
        weights = self._compute_pragmatic_weights(prompt, candidate, n)
        
        # Truth propagation
        t_prompt = (pol_prompt + 1) / 2
        t_cand = (pol_cand + 1) / 2
        t_prompt[t_prompt == 0.5] = 0.5
        
        for _ in range(5):
            t_prompt = np.clip(t_prompt + (imp_matrix.T @ t_prompt) * 0.1, 0, 1)
            t_cand = np.clip(t_cand + (imp_matrix.T @ t_cand) * 0.1, 0, 1)
        
        consistency = 1 - np.mean(np.abs(t_prompt - t_cand) * (weights + 0.1))
        activated_score = np.dot(t_cand, gain * weights + 0.01)
        
        return float(np.clip(0.5 * consistency + 0.5 * activated_score / (n + 1), 0, 1))
    
    def _computation_score(self, prompt: str, candidate: str) -> float:
        computed = self._compute_answer(prompt)
        if computed is None:
            return 0.5
        cand_lower = candidate.lower().strip()
        comp_str = str(computed).lower().strip()
        if comp_str in cand_lower or cand_lower in comp_str:
            return 1.0
        try:
            cand_num = float(re.search(r'-?\d+\.?\d*', candidate).group())
            if abs(float(computed) - cand_num) < 0.01:
                return 1.0
        except:
            pass
        return 0.0
    
    def _compute_answer(self, prompt: str) -> Optional[float]:
        # Numeric comparison
        nums = re.findall(r'\b(\d+\.?\d*)\b', prompt)
        if len(nums) == 2 and re.search(r'\b(greater|larger|bigger|more)\b', prompt.lower()):
            return max(float(nums[0]), float(nums[1]))
        if len(nums) == 2 and re.search(r'\b(less|smaller|fewer)\b', prompt.lower()):
            return min(float(nums[0]), float(nums[1]))
        
        # Bat and ball: X + Y = A, X = Y + B => Y = (A - B) / 2
        match = re.search(r'(\w+) and (\w+) cost \$?(\d+\.?\d*).+\1 costs \$?(\d+\.?\d*) more', prompt, re.IGNORECASE)
        if match:
            total, diff = float(match.group(3)), float(match.group(4))
            return (total - diff) / 2
        
        # All but N: total - N
        match = re.search(r'(\d+) .+ all but (\d+)', prompt, re.IGNORECASE)
        if match:
            return int(match.group(1)) - int(match.group(2))
        
        # PEMDAS expression
        match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)\s*([+\-*/])\s*(\d+)', prompt)
        if match:
            try:
                expr = f"{match.group(1)}{match.group(2)}{match.group(3)}{match.group(4)}{match.group(5)}"
                return eval(expr)
            except:
                pass
        
        # Simple arithmetic
        match = re.search(r'(\d+\.?\d*)\s*([+\-*/])\s*(\d+\.?\d*)', prompt)
        if match:
            a, op, b = float(match.group(1)), match.group(2), float(match.group(3))
            if op == '+': return a + b
            if op == '-': return a - b
            if op == '*': return a * b
            if op == '/' and b != 0: return a / b
        
        return None
    
    def _ncd_score(self, prompt: str, candidate: str) -> float:
        cx = len(zlib.compress(prompt.encode()))
        cy = len(zlib.compress(candidate.encode()))
        cxy = len(zlib.compress((prompt + candidate).encode()))
        ncd = (cxy - min(cx, cy)) / max(cx, cy)
        return float(np.clip(1 - ncd, 0, 1))
    
    def _extract_propositions(self, text: str) -> List[Tuple[str, bool, str]]:
        props = []
        sentences = re.split(r'[.!?]', text)
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            # Negation detection
            negated = bool(re.search(r'\b(not|no|never|none)\b', sent.lower()))
            # Extract subject-verb-object
            match = re.search(r'(\w+(?:\s+\w+)?)\s+(is|are|was|were|has|have|does|do)\s+(.+)', sent, re.IGNORECASE)
            if match:
                prop = f"{match.group(1)}_{match.group(2)}_{match.group(3)[:20]}"
                props.append((prop, not negated, 'atomic'))
            else:
                prop = sent[:30].replace(' ', '_')
                props.append((prop, not negated, 'atomic'))
        return props
    
    def _extract_implications(self, text: str) -> List[Tuple[str, str]]:
        implications = []
        # if...then
        for match in re.finditer(r'if (.+?) then (.+?)(?:[.,;]|$)', text, re.IGNORECASE):
            ant = match.group(1).strip()[:30].replace(' ', '_')
            cons = match.group(2).strip()[:30].replace(' ', '_')
            implications.append((ant, cons))
        # because (reversed)
        for match in re.finditer(r'(.+?) because (.+?)(?:[.,;]|$)', text, re.IGNORECASE):
            cons = match.group(1).strip()[:30].replace(' ', '_')
            ant = match.group(2).strip()[:30].replace(' ', '_')
            implications.append((ant, cons))
        return implications
    
    def _compute_gain(self, prompt: str, candidate: str, n: int) -> np.ndarray:
        text = (prompt + ' ' + candidate).lower()
        dopamine = len(re.findall(r'\b(because|leads to|therefore|causes|results in)\b', text))
        serotonin = len(re.findall(r'\b(maybe|might|could|possibly|perhaps)\b', text))
        acetylcholine = len(re.findall(r'\b(more|less|most|least|\w+est)\b', text))
        
        g = 1 / (1 + np.exp(-(0.3 * dopamine + 0.2 * serotonin + 0.25 * acetylcholine - 1)))
        return np.ones(n) * g
    
    def _compute_pragmatic_weights(self, prompt: str, candidate: str, n: int) -> np.ndarray:
        prompt_words = Counter(re.findall(r'\w+', prompt.lower()))
        cand_words = Counter(re.findall(r'\w+', candidate.lower()))
        
        common = sum((prompt_words & cand_words).values())
        total = sum(prompt_words.values()) + 1
        relevance = common / total
        
        extra = len(cand_words - prompt_words)
        quantity = 1 / (1 + extra / 10)
        
        manner = 1 / (1 + len(candidate) / 100)
        
        weight = relevance * quantity * manner
        return np.ones(n) * weight
    
    def _get_prop_id(self, prop: str) -> int:
        if prop not in self.prop_to_id:
            self.prop_to_id[prop] = self.max_prop_id
            self.max_prop_id += 1
        return self.prop_to_id[prop]
    
    def _has_structural_match(self, prompt: str, answer: str) -> bool:
        return len(self._extract_propositions(prompt)) > 0 or self._compute_answer(prompt) is not None
    
    def _explain_score(self, prompt: str, candidate: str, score: float) -> str:
        computed = self._compute_answer(prompt)
        if computed is not None:
            return f"Computed: {computed}, Score: {score:.2f}"
        return f"Structural consistency score: {score:.2f}"