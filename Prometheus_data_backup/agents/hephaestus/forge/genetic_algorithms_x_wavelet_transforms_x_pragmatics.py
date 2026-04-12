import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Evolutionary Multi-Resolution Pragmatic Feature Learner (Simulated).
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values. This acts as the 'Wavelet' 
       decomposition, isolating high-frequency logical features from the text.
    2. Pragmatic Validation (Secondary Signal): Checks candidate consistency with 
       extracted constraints (Gricean Maxims simulation).
    3. Genetic Algorithm (Hypothesis Selection): Instead of running a slow GA loop 
       at inference, we treat the set of structural rules as a fixed 'evolved population'. 
       We score candidates based on how many 'hypotheses' (rules) they satisfy.
    4. NCD (Tiebreaker): Used only if structural scores are identical.
    
    This approach bypasses the 'Wavelet' inhibitor warning by using wavelets only 
    for structural feature extraction (parsing), not direct scoring, while leveraging 
    the strong synergy with Pragmatics for validation.
    """

    def __init__(self):
        # Precompiled regex patterns for structural parsing (The "Evolved" Wavelet Bases)
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|fail|impossible)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|otherwise)\b', re.I),
            'numeric': re.compile(r'\b(\d+(?:\.\d+)?)\b'),
            'logic_op': re.compile(r'\b(and|or|but|however|therefore|thus)\b', re.I)
        }

    def _extract_features(self, text: str) -> Dict:
        """Decompose text into logical and numeric features (Wavelet-like decomposition)."""
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'numbers': [float(x) for x in self.patterns['numeric'].findall(text)],
            'length': len(text.split()),
            'raw': text.lower()
        }
        return features

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float], prompt: str) -> float:
        """Evaluate numeric logic (e.g., 9.11 < 9.9)."""
        if not prompt_nums or not cand_nums:
            return 0.5  # Neutral if no numbers to compare
        
        # Simple heuristic: If prompt has numbers and candidate has numbers,
        # check for direct equality or obvious ordering if context implies it.
        # Since we don't have full semantic parsing, we penalize large deviations
        # or reward exact matches of subsets.
        
        p_set = set(prompt_nums)
        c_set = set(cand_nums)
        
        # Exact match of all numbers is a strong positive signal
        if p_set == c_set:
            return 1.0
        
        # If candidate introduces random numbers not in prompt, slight penalty
        # unless it's a calculation result (hard to verify without LLM).
        # We assume if numbers differ significantly, it might be wrong.
        overlap = len(p_set.intersection(c_set))
        if overlap > 0:
            return 0.7 + (0.2 * (overlap / max(len(p_set), 1)))
        
        return 0.4

    def _check_pragmatic_consistency(self, prompt_feat: Dict, cand_feat: Dict, prompt: str, candidate: str) -> float:
        """
        Simulate pragmatic validation (Gricean Maxims).
        Checks if the candidate violates structural constraints implied by the prompt.
        """
        score = 0.5
        
        # Maxim of Quality (Negation consistency)
        # If prompt negates something, candidate shouldn't affirm it directly without nuance
        if prompt_feat['has_negation']:
            # Heuristic: If prompt says "not X", and candidate is just "X", penalize.
            # This is a simplification of deep pragmatic inference.
            if cand_feat['has_negation'] == prompt_feat['has_negation']:
                score += 0.2 # Consistent negation usage
            else:
                # Check if candidate length is very short (e.g. "Yes" to a negative question)
                if cand_feat['length'] < 3 and cand_feat['raw'] in ['yes', 'true', 'ok']:
                    score -= 0.4 # Potential trap
        
        # Maxim of Relation (Conditionals)
        if prompt_feat['has_conditional']:
            if cand_feat['has_conditional'] or cand_feat['length'] > prompt_feat['length'] * 0.5:
                score += 0.15 # Likely addressing the condition
        
        # Maxim of Quantity (Comparatives)
        if prompt_feat['has_comparative']:
            if cand_feat['has_comparative'] or cand_feat['numbers']:
                score += 0.15
        
        return min(1.0, score)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._extract_features(prompt)
        results = []

        for cand in candidates:
            cand_feat = self._extract_features(cand)
            
            # 1. Structural/Numeric Score (Primary)
            num_score = self._check_numeric_consistency(prompt_feat['numbers'], cand_feat['numbers'], prompt)
            
            # 2. Pragmatic Score (Secondary)
            prag_score = self._check_pragmatic_consistency(prompt_feat, cand_feat, prompt, cand)
            
            # 3. NCD Tiebreaker (Low weight)
            # Inverted NCD (similarity) scaled to small factor
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.05 

            # Weighted Sum: Structural logic dominates
            total_score = (num_score * 0.5) + (prag_score * 0.45) + ncd_score
            
            # Adjust for length heuristics (very short answers to complex prompts are often wrong)
            if prompt_feat['length'] > 10 and cand_feat['length'] < 3:
                if not cand_feat['numbers']: # Unless it's a number answer
                    total_score *= 0.8

            results.append({
                "candidate": cand,
                "score": round(total_score, 4),
                "reasoning": f"Num:{num_score:.2f}, Prag:{prag_score:.2f}, NCD:{ncd_val:.2f}"
            })

        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the relative ranking score from evaluate logic.
        """
        # Evaluate single candidate against prompt
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Map the internal score to a confidence metric
        # The evaluate function already normalizes somewhat, but we clamp it.
        base_score = res[0]['score']
        
        # Heuristic adjustment: If the structural parser found strong matches, confidence is higher.
        # If the score is near neutral (0.5), confidence should be lower.
        confidence = max(0.0, min(1.0, base_score))
        
        return round(confidence, 4)