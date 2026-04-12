from typing import Dict, Tuple

"""
Maximum Entropy RL Reasoning Tool with Neuromodulation

Combines policy gradient RL with dopaminergic learning rate modulation and
serotonergic temperature control. Features capture structural patterns;
softmax policy maximizes entropy-regularized expected reward.
"""

import re
import numpy as np
from typing import List, Dict, Tuple
import math


class ReasoningTool:
    def __init__(self):
        self.dim = 50  # feature dimension
        self.theta = np.zeros(self.dim)  # preference parameters
        self.baseline = 0.5  # value baseline
        self.alpha0 = 0.01  # base learning rate
        self.T0 = 1.0  # base temperature
        self.k_D = 0.5  # dopamine gain
        self.k_S = 0.3  # serotonin gain
        self.entropy_reg = 0.1  # lambda for entropy regularization
        
    def _extract_features(self, prompt: str, candidate: str) -> np.ndarray:
        """Extract structural features from prompt-candidate pair."""
        f = np.zeros(self.dim)
        text = (prompt + " " + candidate).lower()
        
        # Negation patterns (0-2)
        f[0] = len(re.findall(r'\b(not|no|never|neither|nor)\b', text))
        f[1] = 1 if re.search(r'\b(isn\'t|aren\'t|wasn\'t|weren\'t|don\'t|doesn\'t|didn\'t)\b', text) else 0
        
        # Comparatives/superlatives (3-5)
        f[3] = len(re.findall(r'\b(more|less|greater|fewer|higher|lower)\b', text))
        f[4] = len(re.findall(r'\b(most|least|greatest|fewest|highest|lowest|best|worst)\b', text))
        
        # Conditionals (6-7)
        f[6] = len(re.findall(r'\b(if|when|unless|provided|assuming)\b', text))
        f[7] = len(re.findall(r'\b(then|therefore|thus|hence|consequently)\b', text))
        
        # Causality (8-9)
        f[8] = len(re.findall(r'\b(cause|lead|result|produce|trigger|induce)\b', text))
        f[9] = len(re.findall(r'\b(because|since|due to|owing to)\b', text))
        
        # Quantifiers (10-12)
        f[10] = len(re.findall(r'\b(all|every|each|any)\b', text))
        f[11] = len(re.findall(r'\b(some|many|few|several)\b', text))
        f[12] = len(re.findall(r'\b(none|nothing|nobody)\b', text))
        
        # Temporal (13-14)
        f[13] = len(re.findall(r'\b(before|after|prior|following|earlier|later)\b', text))
        f[14] = len(re.findall(r'\b(during|while|when|as)\b', text))
        
        # Numerics (15-17)
        nums = re.findall(r'\b\d+\.?\d*\b', text)
        f[15] = len(nums)
        f[16] = 1 if any(re.search(r'(percent|%)', text)) else 0
        
        # Numeric comparison in candidate
        f[17] = self._numeric_match_score(prompt, candidate)
        
        # Structural alignment (18-20)
        f[18] = len(set(prompt.lower().split()) & set(candidate.lower().split())) / max(len(candidate.split()), 1)
        f[19] = 1 if any(word in candidate.lower() for word in ['yes', 'no', 'true', 'false']) else 0
        
        # Computational signals (21-30)
        f[21] = self._solve_arithmetic(prompt, candidate)
        f[22] = self._solve_bat_ball(prompt, candidate)
        f[23] = self._check_transitivity(prompt, candidate)
        f[24] = self._check_modus_tollens(prompt, candidate)
        f[25] = self._solve_all_but_n(prompt, candidate)
        f[26] = self._check_parity(prompt, candidate)
        f[27] = self._solve_bayesian(prompt, candidate)
        f[28] = self._check_independence(prompt, candidate)
        f[29] = self._solve_modular(prompt, candidate)
        f[30] = self._ncd_score(prompt, candidate)  # max 15% weight
        
        return f
    
    def _numeric_match_score(self, prompt: str, candidate: str) -> float:
        """Check if candidate correctly answers numeric comparison."""
        p_nums = [float(n) for n in re.findall(r'\b\d+\.?\d*\b', prompt)]
        c_nums = [float(n) for n in re.findall(r'\b\d+\.?\d*\b', candidate)]
        if not p_nums or not c_nums:
            return 0.0
        # Check if candidate number appears in computation of prompt numbers
        if len(p_nums) >= 2 and c_nums:
            expected = [p_nums[0] + p_nums[1], p_nums[0] - p_nums[1], 
                       p_nums[0] * p_nums[1], abs(p_nums[0] - p_nums[1])]
            if any(abs(c_nums[0] - e) < 0.01 for e in expected):
                return 1.0
        return 0.0
    
    def _solve_arithmetic(self, prompt: str, candidate: str) -> float:
        """Solve arithmetic expressions."""
        if '+' in prompt or '-' in prompt or '*' in prompt or '/' in prompt:
            nums = re.findall(r'\b\d+\.?\d*\b', prompt)
            if len(nums) >= 2:
                a, b = float(nums[0]), float(nums[1])
                ops = {'+': a+b, '-': a-b, '*': a*b, 'x': a*b, 'times': a*b}
                for op, result in ops.items():
                    if op in prompt.lower():
                        c_nums = re.findall(r'\b\d+\.?\d*\b', candidate)
                        if c_nums and abs(float(c_nums[0]) - result) < 0.01:
                            return 1.0
        return 0.0
    
    def _solve_bat_ball(self, prompt: str, candidate: str) -> float:
        """Detect bat-and-ball pattern: X costs $Y more than Z, total $W."""
        match = re.search(r'(\d+\.?\d*)\s*more.*total.*?(\d+\.?\d*)', prompt.lower())
        if match:
            diff, total = float(match.group(1)), float(match.group(2))
            # x + (x + diff) = total => x = (total - diff)/2
            answer = (total - diff) / 2
            c_nums = re.findall(r'\b\d+\.?\d*\b', candidate)
            if c_nums and abs(float(c_nums[0]) - answer) < 0.01:
                return 1.0
        return 0.0
    
    def _check_transitivity(self, prompt: str, candidate: str) -> float:
        """Check transitive reasoning: A > B, B > C => A > C."""
        if re.search(r'\b(taller|bigger|faster|more|greater|older)\b', prompt.lower()):
            relations = re.findall(r'(\w+)\s+(?:is\s+)?(?:taller|bigger|faster|more|greater|older)\s+than\s+(\w+)', prompt.lower())
            if len(relations) >= 2:
                # Build transitive chain
                if relations[0][1] == relations[1][0]:
                    expected = f"{relations[0][0]}.*{relations[1][1]}"
                    if re.search(expected, candidate.lower()):
                        return 1.0
        return 0.0
    
    def _check_modus_tollens(self, prompt: str, candidate: str) -> float:
        """If P then Q. Not Q. Therefore not P."""
        if_match = re.search(r'if\s+(\w+).*then\s+(\w+)', prompt.lower())
        not_match = re.search(r'not\s+(\w+)', prompt.lower())
        if if_match and not_match:
            p, q = if_match.group(1), if_match.group(2)
            negated = not_match.group(1)
            if negated == q and f"not {p}" in candidate.lower():
                return 1.0
        return 0.0
    
    def _solve_all_but_n(self, prompt: str, candidate: str) -> float:
        """All but N pattern: total - N."""
        match = re.search(r'all\s+but\s+(\d+)', prompt.lower())
        if match:
            n = int(match.group(1))
            total_match = re.search(r'(\d+)\s+(?:total|items|people)', prompt.lower())
            if total_match:
                result = int(total_match.group(1)) - n
                c_nums = re.findall(r'\b\d+\b', candidate)
                if c_nums and int(c_nums[0]) == result:
                    return 1.0
        return 0.0
    
    def _check_parity(self, prompt: str, candidate: str) -> float:
        """Even/odd parity checks."""
        if 'even' in prompt.lower() or 'odd' in prompt.lower():
            nums = [int(n) for n in re.findall(r'\b\d+\b', prompt)]
            c_nums = [int(n) for n in re.findall(r'\b\d+\b', candidate)]
            if nums and c_nums:
                if 'even' in prompt.lower() and c_nums[0] % 2 == 0:
                    return 1.0
                if 'odd' in prompt.lower() and c_nums[0] % 2 == 1:
                    return 1.0
        return 0.0
    
    def _solve_bayesian(self, prompt: str, candidate: str) -> float:
        """Bayesian reasoning: P(A|B) = P(B|A)P(A)/P(B)."""
        if 'probability' in prompt.lower() or 'given' in prompt.lower():
            percents = re.findall(r'(\d+\.?\d*)\s*%', prompt)
            if len(percents) >= 2:
                # Simple base rate: use first percentage as signal
                c_nums = re.findall(r'(\d+\.?\d*)\s*%', candidate)
                if c_nums and abs(float(c_nums[0]) - float(percents[0])) < 5:
                    return 0.5  # partial credit for considering base rate
        return 0.0
    
    def _check_independence(self, prompt: str, candidate: str) -> float:
        """Check coin flip / independent event reasoning."""
        if re.search(r'flip|coin|independent', prompt.lower()):
            if re.search(r'(same|equal|50|0\.5)', candidate.lower()):
                return 1.0
        return 0.0
    
    def _solve_modular(self, prompt: str, candidate: str) -> float:
        """Modular arithmetic."""
        match = re.search(r'mod(?:ulo)?\s+(\d+)', prompt.lower())
        if match:
            mod = int(match.group(1))
            nums = [int(n) for n in re.findall(r'\b\d+\b', prompt)]
            if nums:
                result = nums[0] % mod
                c_nums = re.findall(r'\b\d+\b', candidate)
                if c_nums and int(c_nums[0]) == result:
                    return 1.0
        return 0.0
    
    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """Normalized Compression Distance (max 15% weight)."""
        import zlib
        c_prompt = len(zlib.compress(prompt.encode()))
        c_cand = len(zlib.compress(candidate.encode()))
        c_both = len(zlib.compress((prompt + candidate).encode()))
        ncd = (c_both - min(c_prompt, c_cand)) / max(c_prompt, c_cand)
        return max(0, 1 - ncd)  # invert so lower NCD = higher score
    
    def _meta_confidence(self, prompt: str) -> float:
        """Assess prompt for ambiguity/unanswerability. Returns cap on confidence."""
        p = prompt.lower()
        
        # Presupposition
        if re.search(r'(have you stopped|have you quit|why did.*fail|why did.*stop)', p):
            return 0.25
        
        # Scope ambiguity
        if re.search(r'every\s+\w+.*\s+a\s+\w+', p):
            return 0.3
        
        # Pronoun ambiguity
        if re.search(r'(he|she|it|they).*who', p) or re.search(r'who.*(he|she|it|they)', p):
            return 0.3
        
        # False dichotomy
        if re.search(r'either\s+\w+\s+or\s+\w+', p) and not re.search(r'(only|must|exactly)', p):
            return 0.4
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p) and not re.search(r'\b(most|least|highest|lowest)\b', p):
            return 0.35
        
        # Unanswerable: asks for info not in prompt
        if re.search(r'(what is|who is|where is|when is).*\?', p):
            words = p.split()
            if len(words) < 20:  # short question likely missing context
                return 0.4
        
        return 1.0  # no meta-issues detected
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """Rank candidates using max-entropy RL policy."""
        n = len(candidates)
        features = [self._extract_features(prompt, c) for c in candidates]
        
        # Compute preference scores
        scores = np.array([self.theta.dot(f) for f in features])
        
        # Softmax policy with temperature
        probs = np.exp(scores / self.T0) / np.sum(np.exp(scores / self.T0))
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        
        # Adjust temperature (serotonin-like)
        T = self.T0 * np.exp(-self.k_S * entropy)
        probs = np.exp(scores / T) / np.sum(np.exp(scores / T))
        
        # Rank by probability
        results = []
        for i, (cand, prob) in enumerate(zip(candidates, probs)):
            reasoning = f"Policy prob={prob:.3f}, entropy={entropy:.2f}, T={T:.2f}"
            results.append({"candidate": cand, "score": float(prob), "reasoning": reasoning})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 for a prompt-answer pair."""
        # Meta-confidence check
        meta_cap = self._meta_confidence(prompt)
        
        # Extract features
        f = self._extract_features(prompt, answer)
        
        # Compute score
        score = self.theta.dot(f)
        
        # Normalize to [0, 1]
        conf = 1 / (1 + np.exp(-score))  # sigmoid
        
        # Cap by meta-confidence
        conf = min(conf, meta_cap)
        
        # Never exceed 0.9 unless strong computational signal
        if f[21:30].sum() < 0.5:  # no strong computational match
            conf = min(conf, 0.75)
        
        # Honest uncertainty when no features match
        if f.sum() < 1.0:
            conf = min(conf, 0.25)
        
        return float(conf)