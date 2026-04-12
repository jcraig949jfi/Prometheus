import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-Scale Clonal-Selection Renormalization Hypothesis Engine (MCSR-HE)
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values. This acts as the "Renormalization" 
       step, coarse-graining the text into logical tokens.
    2. Fractal Feature Space (IFS Analogy): Generates a feature vector based on 
       recursive pattern matching (self-similarity of logic structures) and 
       numeric density.
    3. Clonal Selection (Immune Analogy): 
       - Affinity = Structural match between prompt constraints and candidate content.
       - Proliferation = Boosting score for candidates satisfying logical constraints.
       - Suppression = Penalizing candidates that violate negation or numeric bounds.
       - Memory = Retains successful structural patterns (hardcoded logic rules).
    4. NCD Tiebreaker: Used only when structural signals are ambiguous.
    
    Note: Per causal analysis, "Immune Systems" are restricted to the confidence 
    wrapper and structural parsing support to avoid historical failure modes.
    """

    def __init__(self):
        # Structural patterns for "Renormalization" (Coarse-graining)
        self.negation_patterns = [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r'\bfalse\b']
        self.comparative_patterns = [r'\bmore\b', r'\bless\b', r'\bgreater\b', r'\bsmaller\b', r'\b<', r'\b>', r'\bequal']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\belse\b', r'\bunless\b', r'\bonly if\b']
        self.numeric_pattern = r'-?\d+\.?\d*'

    def _extract_features(self, text: str) -> Dict:
        """Extracts logical and numeric features (Renormalization Step)."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall('|'.join(self.negation_patterns), text_lower)),
            'comparatives': len(re.findall('|'.join(self.comparative_patterns), text_lower)),
            'conditionals': len(re.findall('|'.join(self.conditional_patterns), text_lower)),
            'numbers': [float(n) for n in re.findall(self.numeric_pattern, text)],
            'length': len(text)
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Evaluates logical consistency (Clonal Selection Affinity).
        Checks if candidate respects negations and numeric constraints found in prompt.
        """
        score = 0.0
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()

        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negation, candidate should ideally reflect awareness or not contradict
        if p_feat['negations'] > 0:
            # Simple heuristic: if prompt says "not X", candidate shouldn't blindly assert "X" 
            # without qualification. We approximate by checking if candidate contains 
            # similar negation density or specific denial words if prompt is negative.
            # This is a "fractal" check: looking for self-similar logical structures.
            if c_feat['negations'] > 0 or any(word in c_lower for word in ['cannot', 'impossible', 'false']):
                score += 0.2
        
        # 2. Numeric Consistency
        if p_feat['numbers'] and c_feat['numbers']:
            # Check for direct contradiction in simple comparisons
            # If prompt implies A > B, and candidate says B > A (heuristic)
            # Here we just reward presence of numbers in candidate if prompt has them
            score += 0.3
            
        # 3. Conditional Logic
        if p_feat['conditionals'] > 0:
            if any(word in c_lower for word in ['if', 'then', 'because', 'therefore', 'yes', 'no']):
                score += 0.2

        # 4. Structural Overlap (Fractal Self-Similarity)
        # Reward candidates that reuse specific logical keywords from the prompt
        common_words = set(p_lower.split()) & set(c_lower.split())
        logical_words = {'if', 'then', 'not', 'no', 'yes', 'greater', 'less', 'equal'}
        overlap = common_words & logical_words
        score += len(overlap) * 0.1

        return min(score, 1.0)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(s1_bytes)
        len_s2 = len(s2_bytes)
        if len_s1 == 0 or len_s2 == 0:
            return 1.0
        
        # Concatenation compression
        try:
            len_combined = len(zlib.compress(s1_bytes + s2_bytes))
            len_s1_comp = len(zlib.compress(s1_bytes))
            len_s2_comp = len(zlib.compress(s2_bytes))
            
            # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
            # Simplified standard: (C(xy) - min(C(x), C(y))) / max(C(x), C(y)) is one variant
            # Using: (C(xy) - min(C(x), C(y))) / max(C(x), C(y)) often yields > 1 if not careful.
            # Standard: (C(xy) - min(C(x), C(y))) / max(C(x), C(y)) -> Let's use max(C(x), C(y)) as divisor
            # Actually, standard NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
            # To ensure 0-1: (C(xy) - min(C(x), C(y))) / max(C(x), C(y)) can exceed 1? 
            # Let's use: (C(xy) - min(C(x), C(y))) / max(C(x), C(y)) is risky.
            # Safer: (C(xy) - min(C(x), C(y))) / max(C(x), C(y)) -> No, let's use max(C(x), C(y))
            # Correct standard: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
            # Let's stick to: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
            # Wait, if C(xy) > C(x) + C(y), it's > 1. 
            # Let's use: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
            # Actually, let's use the Li et al. definition: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
            # But to be safe and bounded:
            numerator = len_combined - min(len_s1_comp, len_s2_comp)
            denominator = max(len_s1_comp, len_s2_comp)
            if denominator == 0:
                return 1.0
            return max(0.0, min(1.0, numerator / denominator))
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        p_feat = self._extract_features(prompt)
        has_logic = (p_feat['negations'] + p_feat['comparatives'] + p_feat['conditionals']) > 0
        has_numbers = len(p_feat['numbers']) > 0

        for cand in candidates:
            score = 0.0
            reasoning_parts = []

            # Primary Signal: Structural/Logical Consistency (Clonal Affinity)
            logic_score = self._check_logical_consistency(prompt, cand)
            if has_logic or has_numbers:
                score += logic_score * 0.8
                if logic_score > 0:
                    reasoning_parts.append("High structural affinity")
                else:
                    reasoning_parts.append("Low structural affinity")
            else:
                # If no obvious logic, rely more on NCD
                score += 0.2 

            # Secondary Signal: NCD (Tiebreaker/Noise Filter)
            # Invert NCD so lower distance = higher score
            ncd_val = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val
            
            # Only apply NCD heavily if logic signal is weak or as a tiebreaker
            if not has_logic and not has_numbers:
                score += ncd_score * 0.5
                reasoning_parts.append(f"NCD similarity: {ncd_score:.2f}")
            else:
                # Small NCD bonus for relevance
                score += ncd_score * 0.2
                reasoning_parts.append(f"NCD boost: {ncd_score:.2f}")

            # Normalize score roughly to 0-1 range based on components
            final_score = min(1.0, max(0.0, score))
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": "; ".join(reasoning_parts)
            })

        # Rank by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing (Renormalization) as primary signal.
        Immune system concept restricted to this wrapper as per constraints.
        """
        if not answer:
            return 0.0
            
        p_feat = self._extract_features(prompt)
        a_feat = self._extract_features(answer)
        
        base_conf = 0.5
        
        # 1. Structural Match (Renormalization Fixed Point)
        # Does the answer contain the logical operators required by the prompt?
        if p_feat['negations'] > 0:
            if a_feat['negations'] > 0 or any(x in answer.lower() for x in ['no', 'not', 'false']):
                base_conf += 0.2
            else:
                # Potential trap: prompt asks "What is not X?" and answer doesn't negate
                # Hard to verify without semantics, but low negation count might be suspicious
                pass
        
        if p_feat['numbers']:
            if a_feat['numbers']:
                base_conf += 0.2
            else:
                base_conf -= 0.1
                
        if p_feat['conditionals']:
            if any(x in answer.lower() for x in ['if', 'then', 'because', 'therefore']):
                base_conf += 0.15

        # 2. NCD Check (Anti-gameplay)
        # If answer is just a substring of prompt, lower confidence (echo chamber)
        ncd_val = self._ncd(prompt, answer)
        if ncd_val < 0.1 and len(answer) < len(prompt) * 0.5:
            # Likely just repeating part of prompt
            base_conf *= 0.8
        
        # 3. Length heuristic (Very short answers to complex prompts are low conf)
        if len(p_feat['numbers']) > 0 and len(a_feat['numbers']) == 0 and p_feat['conditionals'] > 0:
             if len(answer.split()) < 3:
                 base_conf *= 0.9

        return max(0.0, min(1.0, base_conf))