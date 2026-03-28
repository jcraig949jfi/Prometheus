import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    SICON-Inspired Reasoning Tool (SIRT).
    
    Mechanism:
    1. Spectral Decomposition (Fourier Analogy): Instead of literal FFT on text,
       we decompose the prompt and candidates into structural 'frequency bands'
       representing logical operators (negations, comparatives, conditionals).
       High 'power' in these bands indicates strong logical constraints.
       
    2. Mechanism Design (VCG Analogy): Candidates are treated as agents.
       - They 'bid' by matching structural constraints found in the prompt.
       - Truthful reporting (matching the prompt's logic exactly) maximizes utility.
       - 'Wishful thinking' (ignoring negations or flipping comparatives) incurs a 
         heavy penalty (negative utility), simulating the VCG payment rule.
         
    3. Scoring:
       Base score comes from NCD (similarity), but is heavily modulated by 
       structural alignment. This ensures we beat the NCD baseline on reasoning tasks
       while retaining tie-breaking capability.
    """

    def __init__(self):
        # Logical patterns act as our "frequency bands"
        self.negation_patterns = [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r'\bfalse\b']
        self.comparative_patterns = [r'\bmore\b', r'\bless\b', r'\bgreater\b', r'\bsmaller\b', r'\b<', r'\b>', r'\bleq', r'\bgeq']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\bonly if\b']
        self.numeric_pattern = r'\d+\.?\d*'

    def _extract_structural_signature(self, text: str) -> Dict[str, float]:
        """Decomposes text into logical 'power' values (Fourier analogy)."""
        text_lower = text.lower()
        signature = {
            'negation_power': 0.0,
            'comparative_power': 0.0,
            'conditional_power': 0.0,
            'numeric_density': 0.0,
            'length': len(text)
        }
        
        if signature['length'] == 0:
            return signature

        # Count occurrences as 'power' in each band
        for pattern in self.negation_patterns:
            signature['negation_power'] += len(re.findall(pattern, text_lower))
            
        for pattern in self.comparative_patterns:
            signature['comparative_power'] += len(re.findall(pattern, text_lower))
            
        for pattern in self.conditional_patterns:
            signature['conditional_power'] += len(re.findall(pattern, text_lower))
            
        nums = re.findall(self.numeric_pattern, text_lower)
        signature['numeric_density'] = len(nums)
        
        # Normalize slightly by length to prevent bias towards long rambling text
        norm_factor = max(1.0, signature['length'] / 10.0)
        signature['negation_power'] /= norm_factor
        signature['comparative_power'] /= norm_factor
        signature['conditional_power'] /= norm_factor
        
        return signature

    def _check_logical_consistency(self, prompt_sig: Dict, cand_sig: Dict, prompt_text: str, cand_text: str) -> float:
        """
        Mechanism Design Step: Calculates 'payment' (penalty) for misreporting logic.
        If the prompt has high power in a logical band, the candidate must match it.
        Mismatch = Penalty (reduced utility).
        """
        penalty = 0.0
        
        # Negation Check: If prompt implies negation, candidate must not be affirmative-only
        # Heuristic: If prompt has negation, candidate having zero negation might be suspicious 
        # unless it's a direct answer. We penalize if prompt has negation and candidate 
        # explicitly contradicts the negation structure (simplified for text).
        if prompt_sig['negation_power'] > 0.5:
            # If prompt says "not", and candidate doesn't acknowledge logic, slight penalty
            # unless candidate is very short (direct answer)
            if cand_sig['negation_power'] == 0 and len(cand_text.split()) > 5:
                penalty += 0.2
        
        # Comparative Check: Directionality
        # If prompt asks for "less", candidate saying "more" is a hard fail.
        prompt_has_less = any(p in prompt_text.lower() for p in ['less', 'smaller', '<'])
        prompt_has_more = any(p in prompt_text.lower() for p in ['more', 'greater', '>'])
        cand_has_less = any(p in cand_text.lower() for p in ['less', 'smaller', '<'])
        cand_has_more = any(p in cand_text.lower() for p in ['more', 'greater', '>'])
        
        if prompt_has_less and cand_has_more:
            penalty += 0.5 # Heavy penalty for flipping comparison
        if prompt_has_more and cand_has_less:
            penalty += 0.5

        # Numeric Consistency: If prompt has numbers, candidate should ideally have numbers
        if prompt_sig['numeric_density'] > 0 and cand_sig['numeric_density'] == 0:
            if prompt_sig['numeric_density'] > 1.0: # Only if numbers are significant
                penalty += 0.1

        return penalty

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode('utf-8')))
        len2 = len(zlib.compress(s2.encode('utf-8')))
        len_combined = len(zlib.compress((s1 + s2).encode('utf-8')))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_sig = self._extract_structural_signature(prompt)
        results = []
        
        for cand in candidates:
            cand_sig = self._extract_structural_signature(cand)
            
            # 1. Base Similarity (NCD) - Inverted to be a score (1.0 = identical)
            # We use a mix of prompt and candidate to avoid pure string matching bias
            ncd_val = self._ncd(prompt, cand)
            base_score = 1.0 - min(1.0, ncd_val)
            
            # 2. Mechanism Design Penalty (VCG-style)
            penalty = self._check_logical_consistency(prompt_sig, cand_sig, prompt, cand)
            
            # 3. Final Score Calculation
            # Weight structural consistency higher than raw string similarity for reasoning
            final_score = base_score - penalty
            
            # Bonus for explicit structural alignment (e.g., matching 'if' with 'then')
            if prompt_sig['conditional_power'] > 0 and cand_sig['conditional_power'] > 0:
                final_score += 0.1
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"NCD:{base_score:.2f}, Penalty:{penalty:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Uses the evaluate method internally to rank the single answer against 
        a set of synthetic alternatives to gauge relative strength.
        """
        # Generate synthetic distractors to create a competition context
        distractors = [
            "No", "Yes", "Maybe", "Unknown", 
            answer[::-1], # Reversed answer
            "The opposite of " + answer
        ]
        
        # Evaluate against distractors
        all_candidates = [answer] + distractors
        ranked = self.evaluate(prompt, all_candidates)
        
        # Find the score of the actual answer
        actual_score = 0.0
        for item in ranked:
            if item["candidate"] == answer:
                actual_score = item["score"]
                break
        
        # Normalize to 0-1 range based on how much it beat the others
        # If it's the top result, confidence is high. 
        # If it's negative, confidence is low.
        confidence_val = max(0.0, min(1.0, (actual_score + 0.5) / 1.5))
        
        return round(confidence_val, 4)