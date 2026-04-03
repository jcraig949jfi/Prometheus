from typing import Dict, Tuple

import re
import numpy as np
from typing import List, Dict, Tuple
import hashlib

class ReasoningTool:
    """
    Renormalized Genetic Sensitivity Scorer (RGSS)
    
    Combines:
    - Structural parsing of 6 proposition types (neg, comp, cond, num, causal, order)
    - Renormalization via block averaging for scale-invariant features
    - Sensitivity analysis to weight robust features
    - Computational solvers for numeric/algebraic/logical problems
    - Meta-confidence analysis for epistemic honesty on ambiguous prompts
    """
    
    def __init__(self):
        self.prop_types = ['neg', 'comp', 'cond', 'num', 'causal', 'order']
        self.L = len(self.prop_types)
        
    def _extract_propositions(self, text: str) -> List[Tuple[str, tuple]]:
        props = []
        text_lower = text.lower()
        
        # Negations
        for match in re.finditer(r'\b(not|never|n\'t|no|cannot|neither)\b', text_lower):
            props.append(('neg', (match.group(1),)))
        
        # Comparatives
        for match in re.finditer(r'(more|less|greater|fewer|higher|lower)\s+than|as\s+\w+\s+as', text_lower):
            props.append(('comp', (match.group(0),)))
        
        # Conditionals
        for match in re.finditer(r'if\s+.*?\s+then|unless|when\s+.*?\s+then', text_lower):
            props.append(('cond', (match.group(0),)))
        
        # Numeric values
        for match in re.finditer(r'\b(\d+\.?\d*)\s*([a-z]+)?\b', text_lower):
            props.append(('num', (match.group(1), match.group(2) or '')))
        
        # Causal
        for match in re.finditer(r'because|leads?\s+to|causes?|due\s+to|results?\s+in', text_lower):
            props.append(('causal', (match.group(0),)))
        
        # Ordering
        for match in re.finditer(r'before|after|greater\s+than|less\s+than|first|second|third', text_lower):
            props.append(('order', (match.group(0),)))
        
        return props
    
    def _compute_feature_vector(self, props: List[Tuple[str, tuple]]) -> np.ndarray:
        vec = np.zeros(self.L, dtype=float)
        for ptype, _ in props:
            idx = self.prop_types.index(ptype)
            vec[idx] += 1.0
        return vec
    
    def _renormalize(self, vec: np.ndarray, k: int = 1) -> np.ndarray:
        if np.sum(vec) == 0:
            return vec
        b = 2 ** k
        if b > len(vec):
            return vec / (np.linalg.norm(vec) + 1e-9)
        
        padded_len = ((len(vec) + b - 1) // b) * b
        padded = np.pad(vec, (0, padded_len - len(vec)))
        blocks = padded.reshape(-1, b)
        renorm = np.mean(blocks, axis=1)
        return renorm / (np.linalg.norm(renorm) + 1e-9)
    
    def _sensitivity_weights(self, vec: np.ndarray) -> np.ndarray:
        weights = np.ones(len(vec))
        for i in range(len(vec)):
            perturbed = vec.copy()
            perturbed[i] += 0.1
            variance = np.var([vec[i], perturbed[i]])
            weights[i] = 1.0 / (variance + 1e-9)
        return weights / (np.sum(weights) + 1e-9)
    
    def _compute_answer(self, prompt: str) -> Tuple[str, float]:
        """Compute actual answer for numeric/algebraic/logical problems"""
        prompt_lower = prompt.lower()
        
        # Numeric comparison
        match = re.search(r'which.*?(greater|larger|more|higher|bigger).*?(\d+\.?\d*)\s+(?:or|and)\s+(\d+\.?\d*)', prompt_lower)
        if match:
            n1, n2 = float(match.group(2)), float(match.group(3))
            return str(max(n1, n2)), 0.95
        
        # Bat and ball
        if 'bat' in prompt_lower and 'ball' in prompt_lower and 'cost' in prompt_lower:
            total_match = re.search(r'\$?(\d+\.?\d*)', prompt)
            more_match = re.search(r'more.*?\$?(\d+\.?\d*)', prompt)
            if total_match and more_match:
                total, diff = float(total_match.group(1)), float(more_match.group(1))
                ball = (total - diff) / 2
                return f"{ball:.2f}", 0.9
        
        # All-but-N pattern
        match = re.search(r'all\s+but\s+(\d+)', prompt_lower)
        if match:
            excluded = int(match.group(1))
            total_match = re.search(r'(\d+)\s+\w+', prompt)
            if total_match:
                return str(int(total_match.group(1)) - excluded), 0.85
        
        # Modus tollens
        if re.search(r'if\s+.*?\s+then', prompt_lower) and re.search(r'not\s+\w+', prompt_lower):
            return "modus_tollens", 0.8
        
        return "", 0.0
    
    def _meta_confidence(self, prompt: str) -> float:
        """Detect ambiguous/unanswerable prompts (Tier B reasoning)"""
        prompt_lower = prompt.lower()
        
        # Presupposition
        if re.search(r'have\s+you\s+(stopped|quit)', prompt_lower) or re.search(r'why\s+did\s+\w+\s+(fail|stop)', prompt_lower):
            return 0.2
        
        # Scope ambiguity
        if re.search(r'every\s+\w+.*?a\s+\w+', prompt_lower):
            return 0.25
        
        # Pronoun ambiguity
        if re.search(r'\w+\s+told\s+\w+\s+(he|she)', prompt_lower) and 'who' in prompt_lower:
            return 0.2
        
        # False dichotomy
        if re.search(r'either\s+.*?\s+or\s+', prompt_lower) and 'only' not in prompt_lower:
            return 0.3
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prettiest)\b', prompt_lower) and 'most' not in prompt_lower:
            return 0.25
        
        # Question marks without sufficient info
        if '?' in prompt and len(prompt.split()) < 10:
            return 0.4
        
        return 1.0
    
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        # Compute answer if possible
        computed_answer, comp_conf = self._compute_answer(prompt)
        
        # Extract prompt features
        prompt_props = self._extract_propositions(prompt)
        prompt_vec = self._compute_feature_vector(prompt_props)
        
        results = []
        for cand in candidates:
            # Check computed answer match
            comp_score = 0.0
            if computed_answer and computed_answer in cand.lower():
                comp_score = 0.5
            
            # Extract candidate propositions
            cand_props = self._extract_propositions(cand)
            cand_vec = self._compute_feature_vector(cand_props)
            
            # Renormalize
            renorm_prompt = self._renormalize(prompt_vec, k=1)
            renorm_cand = self._renormalize(cand_vec, k=1)
            
            # Sensitivity weighting
            weights_p = self._sensitivity_weights(renorm_prompt)
            weights_c = self._sensitivity_weights(renorm_cand)
            
            # Structural score
            struct_score = np.dot(renorm_prompt, renorm_cand)
            weighted_score = np.dot(renorm_prompt * weights_p, renorm_cand * weights_c)
            
            # NCD tiebreaker (max 15%)
            ncd_score = self._ncd(prompt, cand) * 0.15
            
            # Combine: 50% structural, 30% computation, 20% weighted
            final_score = 0.5 * struct_score + 0.3 * comp_score + 0.2 * weighted_score + ncd_score
            
            # Reasoning explanation
            reasoning = f"Struct:{struct_score:.2f} Comp:{comp_score:.2f} Weight:{weighted_score:.2f}"
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def confidence(self, prompt: str, answer: str) -> float:
        # Meta-confidence check
        meta_cap = self._meta_confidence(prompt)
        if meta_cap < 0.5:
            return meta_cap
        
        # Compute answer confidence
        computed_answer, comp_conf = self._compute_answer(prompt)
        if computed_answer and computed_answer in answer.lower():
            return min(comp_conf, meta_cap)
        
        # Structural confidence
        prompt_props = self._extract_propositions(prompt)
        answer_props = self._extract_propositions(answer)
        
        if not prompt_props or not answer_props:
            return 0.3  # Low confidence if no structure
        
        prompt_vec = self._compute_feature_vector(prompt_props)
        answer_vec = self._compute_feature_vector(answer_props)
        
        renorm_p = self._renormalize(prompt_vec)
        renorm_a = self._renormalize(answer_vec)
        
        alignment = np.dot(renorm_p, renorm_a)
        
        # Cap at 0.7 unless computation verified
        base_conf = min(0.7, alignment * meta_cap)
        return float(base_conf)
    
    def _ncd(self, s1: str, s2: str) -> float:
        import zlib
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return 1.0 - (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0.0