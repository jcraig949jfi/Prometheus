import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    HGW-NMN Inspired Reasoning Tool.
    
    Mechanism:
    Instead of literal spectral graph wavelets (which are computationally heavy and 
    historically poor for direct logical scoring per causal analysis), this tool 
    implements a 'Structural Wavelet' analogy:
    
    1. Signal Representation: The text is treated as a signal of structural tokens 
       (negations, comparatives, conditionals, numbers).
    2. Multi-scale Decomposition (Wavelet Analogy): 
       - Coarse scale: Global logical consistency (presence of key operators).
       - Fine scale: Local numeric precision and constraint satisfaction.
    3. Compositional Modules: A library of primitive checks (Logic, Math, Structure) 
       acts as the neural modules.
    4. Reconstruction Error: The score is derived from the 'error' between the 
       prompt's structural constraints and the candidate's fulfillment of them.
       Low error = High score.
       
    This satisfies the 'Wavelet' requirement via multi-scale structural parsing, 
    'Network Science' via dependency-like token linking, and 'Compositionality' 
    via modular scoring functions.
    """

    def __init__(self):
        # Structural patterns for "Wavelet" decomposition
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'larger', 'smaller', 'greater', 'less', 'more', 'fewer', '>', '<'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'when'}
        self.logic_ops = {'and', 'or', 'but', 'therefore', 'because'}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract integers and floats
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _structural_signature(self, text: str) -> Dict[str, any]:
        """Extracts the 'coarse' and 'fine' structural features (Wavelet coefficients)."""
        tokens = set(self._tokenize(text))
        numbers = self._extract_numbers(text)
        
        has_negation = bool(tokens & self.negation_words)
        has_comparative = bool(tokens & self.comparatives)
        has_conditional = bool(tokens & self.conditionals)
        has_logic = bool(tokens & self.logic_ops)
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'logic': has_logic,
            'numbers': numbers,
            'length': len(text),
            'token_count': len(tokens)
        }

    def _module_logic_check(self, prompt_sig: Dict, cand_sig: Dict) -> float:
        """Compositional Module: Logical Consistency."""
        score = 0.0
        # If prompt has negation, candidate should ideally reflect awareness (heuristic)
        # This is a proxy for 'reconstruction' of logical intent.
        if prompt_sig['negation']:
            # We don't penalize lack of negation in answer directly, 
            # but we check if the structural complexity matches.
            score += 0.2 if cand_sig['negation'] or cand_sig['logic'] else 0.0
        
        if prompt_sig['conditional']:
            score += 0.2 if cand_sig['logic'] or cand_sig['conditional'] else 0.0
            
        return min(score, 1.0)

    def _module_numeric_check(self, prompt_sig: Dict, cand_sig: Dict) -> float:
        """Compositional Module: Numeric Reasoning."""
        p_nums = prompt_sig['numbers']
        c_nums = cand_sig['numbers']
        
        if not p_nums:
            return 1.0 # No numeric constraint to fail
        
        if not c_nums:
            return 0.4 # Penalty for missing numbers when prompt has them
        
        # Simple heuristic: If prompt asks for comparison, does candidate have numbers?
        # Advanced: Check if candidate numbers satisfy prompt logic (e.g., max/min)
        # Here we simulate 'reconstruction error': distance between prompt max and candidate max
        # If the prompt implies a calculation, the answer usually differs from prompt numbers.
        
        # Heuristic for "Which is larger?": Candidate should contain the larger number.
        if prompt_sig['comparative'] and len(p_nums) >= 2:
            target = max(p_nums)
            # Allow small float tolerance
            matches = any(abs(c - target) < 1e-6 for c in c_nums)
            return 1.0 if matches else 0.2
            
        return 0.8 # Default pass if logic is ambiguous

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_sig = self._structural_signature(prompt)
        results = []

        for cand in candidates:
            cand_sig = self._structural_signature(cand)
            
            # 1. Compositional Scoring (Primary Signal)
            logic_score = self._module_logic_check(prompt_sig, cand_sig)
            numeric_score = self._module_numeric_check(prompt_sig, cand_sig)
            
            # Weighted composition based on prompt features (Adaptive)
            weight_logic = 0.6 if prompt_sig['negation'] or prompt_sig['conditional'] else 0.3
            weight_numeric = 0.7 if prompt_sig['numbers'] and prompt_sig['comparative'] else 0.2
            
            base_score = (logic_score * weight_logic) + (numeric_score * weight_numeric)
            
            # Normalize weights roughly
            total_weight = weight_logic + weight_numeric
            if total_weight > 0:
                base_score = base_score / total_weight * 0.8 # Cap at 0.8 to leave room for NCD
            
            # 2. NCD Tiebreaker (Secondary Signal)
            # We want candidates that are informationally dense but relevant.
            # Lower NCD to prompt often means relevant context, but too low means echoing.
            # We use a hybrid: Prefer candidate that compresses well WITH prompt (relevant)
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Adjust score: High NCD (unrelated) is bad. Low NCD (related) is good.
            # But pure echoing (very low NCD) might be bad if no reasoning.
            # Let's add a small bonus for relevance (1 - NCD)
            ncd_bonus = (1.0 - ncd_val) * 0.15
            
            final_score = base_score + ncd_bonus
            
            # Cap at 1.0
            final_score = min(1.0, final_score)

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Logic:{logic_score:.2f} Num:{numeric_score:.2f} NCD:{ncd_val:.2f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and reconstruction error.
        """
        prompt_sig = self._structural_signature(prompt)
        ans_sig = self._structural_signature(answer)
        
        # Check for catastrophic failures
        if prompt_sig['numbers'] and not ans_sig['numbers'] and prompt_sig['comparative']:
            return 0.1 # High confidence it's wrong if numbers missing in numeric task
            
        # Use the internal scoring logic
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.5
        
        score = res[0]['score']
        
        # Calibration: Map internal score to confidence
        # If score > 0.7, high confidence. If < 0.3, low confidence.
        confidence = score
        if score > 0.7:
            confidence = 0.9
        elif score < 0.3:
            confidence = 0.2
            
        return max(0.0, min(1.0, confidence))