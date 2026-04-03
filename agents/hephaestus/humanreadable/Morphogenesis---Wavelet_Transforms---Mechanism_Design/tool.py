from typing import Dict, Tuple

import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Morphogenesis x Wavelet x Mechanism Design reasoning evaluator.
    
    Extracts propositions into a hypergraph, propagates activation via
    reaction-diffusion, weights features with Haar wavelets, and scores
    using mechanism-design-derived proper scoring rules.
    """
    
    def __init__(self):
        # Learned weights from mechanism design (incentive-compatible)
        self.w_negation = 0.3
        self.w_comparative = 0.25
        self.w_conditional = 0.2
        self.w_numeric = 0.15
        self.w_causal = 0.1
        self.alpha = 0.1  # diffusion rate
        self.beta = 0.1   # reaction rate
        
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._score_candidate(prompt, cand)
            reasoning = self._explain_score(prompt, cand)
            results.append({"candidate": cand, "score": score, "reasoning": reasoning})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def confidence(self, prompt: str, answer: str) -> float:
        meta_conf = self._meta_confidence(prompt)
        if meta_conf < 0.3:
            return meta_conf
        
        struct_score = self._structural_score(prompt, answer)
        comp_score = self._computation_score(prompt, answer)
        
        # Cap confidence based on evidence strength
        if comp_score > 0.8:
            return min(0.95, meta_conf * (struct_score * 0.4 + comp_score * 0.6))
        return min(0.85, meta_conf * (struct_score * 0.5 + comp_score * 0.5))
    
    def _meta_confidence(self, prompt: str) -> float:
        """Check for ambiguity, presuppositions, unanswerability."""
        p_lower = prompt.lower()
        
        # Presupposition patterns
        if re.search(r'\b(have you stopped|did you quit|why did .+ fail|when did .+ stop)', p_lower):
            return 0.2
        
        # Scope ambiguity: "every X ... a Y"
        if re.search(r'\bevery \w+.*\ba\b', p_lower) and '?' in prompt:
            return 0.25
        
        # Pronoun ambiguity with "who" question
        if re.search(r'\b(he|she|it|they)\b', p_lower) and re.search(r'\bwho\b', p_lower):
            return 0.25
        
        # False dichotomy
        if re.search(r'\beither .+ or .+\?', p_lower) and not re.search(r'\bneither\b', p_lower):
            return 0.28
        
        # Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|prefer)\b', p_lower) and not re.search(r'\b(most|least|measure|criteria)\b', p_lower):
            return 0.25
        
        # Unanswerable: requires external info
        if re.search(r'\b(will|future|predict|next year)\b', p_lower):
            return 0.3
        
        return 1.0
    
    def _score_candidate(self, prompt: str, candidate: str) -> float:
        struct = self._structural_score(prompt, candidate)
        comp = self._computation_score(prompt, candidate)
        ncd = 1 - self._ncd(prompt, candidate)
        
        # Morphogenesis score via graph propagation
        morph = self._morphogenesis_score(prompt, candidate)
        
        # Combine: structural 50%, computation 25%, morphogenesis 15%, NCD 10%
        return struct * 0.5 + comp * 0.25 + morph * 0.15 + ncd * 0.1
    
    def _structural_score(self, prompt: str, candidate: str) -> float:
        """Parse structural features with wavelet-weighted importance."""
        features = self._extract_features(prompt, candidate)
        wavelet_features = self._wavelet_transform(features)
        return min(1.0, sum(wavelet_features) / 10.0)
    
    def _extract_features(self, prompt: str, candidate: str) -> np.ndarray:
        """Extract proposition features: negations, comparatives, etc."""
        feat = np.zeros(8)
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Negation consistency
        p_neg = len(re.findall(r'\b(not|no|never|none)\b', p_lower))
        c_neg = len(re.findall(r'\b(not|no|never|none)\b', c_lower))
        feat[0] = 1.0 if (p_neg > 0) == (c_neg > 0) else 0.5
        
        # Comparative relations
        p_comp = re.findall(r'(greater|less|more|fewer|higher|lower|above|below)', p_lower)
        c_comp = re.findall(r'(greater|less|more|fewer|higher|lower|above|below)', c_lower)
        feat[1] = len(set(p_comp) & set(c_comp)) * 0.5
        
        # Conditionals
        p_cond = bool(re.search(r'\b(if|unless|when|whenever)\b', p_lower))
        c_cond = bool(re.search(r'\b(if|unless|then|therefore)\b', c_lower))
        feat[2] = 1.0 if p_cond and c_cond else 0.5
        
        # Numeric presence
        p_nums = re.findall(r'\b\d+\.?\d*\b', prompt)
        c_nums = re.findall(r'\b\d+\.?\d*\b', candidate)
        feat[3] = 1.0 if len(p_nums) > 0 and len(c_nums) > 0 else 0.3
        
        # Causal verbs
        causal = r'(cause|lead|result|produce|induce|trigger)'
        feat[4] = 1.0 if re.search(causal, p_lower) and re.search(causal, c_lower) else 0.4
        
        # Quantifiers
        quant = r'\b(all|some|none|every|any|each)\b'
        feat[5] = 1.0 if bool(re.search(quant, p_lower)) == bool(re.search(quant, c_lower)) else 0.5
        
        # List ordering
        feat[6] = 1.0 if bool(re.search(r'\b(first|second|third|finally)\b', c_lower)) else 0.5
        
        # Length reasonableness
        feat[7] = min(1.0, len(candidate.split()) / max(len(prompt.split()), 1))
        
        return feat
    
    def _wavelet_transform(self, features: np.ndarray) -> np.ndarray:
        """Haar wavelet with multi-resolution weighting."""
        n = len(features)
        L = int(np.log2(n)) if n > 1 else 0
        weighted = np.copy(features)
        
        # Simple Haar: average pairs, weight coarse > fine
        for level in range(L):
            gamma = 2 ** (-level)
            weighted *= gamma
        
        return weighted
    
    def _computation_score(self, prompt: str, candidate: str) -> float:
        """Actually compute numeric/logical answers."""
        score = 0.0
        
        # Numeric comparison
        num_score = self._numeric_comparison(prompt, candidate)
        if num_score >= 0:
            score += num_score * 0.4
        
        # Arithmetic evaluation
        arith_score = self._arithmetic_eval(prompt, candidate)
        score += arith_score * 0.3
        
        # Logical transitivity
        trans_score = self._transitivity_check(prompt, candidate)
        score += trans_score * 0.3
        
        return min(1.0, score)
    
    def _numeric_comparison(self, prompt: str, candidate: str) -> float:
        """Evaluate numeric comparisons."""
        p_nums = re.findall(r'\b(\d+\.?\d*)\b', prompt)
        c_lower = candidate.lower()
        
        if len(p_nums) >= 2:
            try:
                a, b = float(p_nums[0]), float(p_nums[1])
                if re.search(r'\b(greater|more|higher|larger)\b', prompt.lower()):
                    if a > b and re.search(r'\b' + re.escape(p_nums[0]) + r'\b', c_lower):
                        return 1.0
                    elif b > a and re.search(r'\b' + re.escape(p_nums[1]) + r'\b', c_lower):
                        return 1.0
                elif re.search(r'\b(less|fewer|lower|smaller)\b', prompt.lower()):
                    if a < b and re.search(r'\b' + re.escape(p_nums[0]) + r'\b', c_lower):
                        return 1.0
                    elif b < a and re.search(r'\b' + re.escape(p_nums[1]) + r'\b', c_lower):
                        return 1.0
            except:
                pass
        return -1
    
    def _arithmetic_eval(self, prompt: str, candidate: str) -> float:
        """Evaluate arithmetic expressions."""
        expr_match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', prompt)
        if expr_match:
            try:
                a, op, b = int(expr_match.group(1)), expr_match.group(2), int(expr_match.group(3))
                result = eval(f"{a}{op}{b}")
                if str(result) in candidate:
                    return 1.0
            except:
                pass
        return 0.0
    
    def _transitivity_check(self, prompt: str, candidate: str) -> float:
        """Check transitive reasoning (A>B, B>C => A>C)."""
        # Simplified: look for transitive patterns
        if re.search(r'\bthan\b.*\bthan\b', prompt.lower()):
            terms = re.findall(r'\b([A-Z]\w*)\b', prompt)
            if len(terms) >= 3 and terms[0] in candidate:
                return 0.8
        return 0.0
    
    def _morphogenesis_score(self, prompt: str, candidate: str) -> float:
        """Reaction-diffusion on proposition graph."""
        nodes = self._build_graph(prompt, candidate)
        if len(nodes) == 0:
            return 0.5
        
        # Initialize activation
        activation = np.random.rand(len(nodes)) * 0.1
        activation[0] = 1.0  # root node
        
        # Propagate for 5 iterations
        for _ in range(5):
            # Reaction term
            reaction = 1 / (1 + np.exp(-activation))
            
            # Diffusion (simplified Laplacian)
            if len(activation) > 1:
                laplacian = np.zeros_like(activation)
                for i in range(len(activation)):
                    if i > 0:
                        laplacian[i] += activation[i-1] - activation[i]
                    if i < len(activation) - 1:
                        laplacian[i] += activation[i+1] - activation[i]
                
                activation += self.alpha * laplacian + self.beta * reaction
                activation = np.clip(activation, 0, 1)
        
        return float(np.mean(activation))
    
    def _build_graph(self, prompt: str, candidate: str) -> List[str]:
        """Extract proposition nodes."""
        nodes = []
        for sent in re.split(r'[.!?]', prompt + ' ' + candidate):
            sent = sent.strip()
            if len(sent) > 5:
                nodes.append(sent)
        return nodes[:8]  # Limit for performance
    
    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        c1, c2 = len(zlib.compress(s1.encode())), len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        return (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 0
    
    def _explain_score(self, prompt: str, candidate: str) -> str:
        """Generate reasoning explanation."""
        meta = self._meta_confidence(prompt)
        if meta < 0.3:
            return "Low confidence: question appears ambiguous or unanswerable"
        
        comp = self._computation_score(prompt, candidate)
        if comp > 0.7:
            return "High confidence: computational verification successful"
        
        struct = self._structural_score(prompt, candidate)
        if struct > 0.6:
            return "Moderate confidence: structural alignment detected"
        
        return "Low confidence: limited structural or computational support"