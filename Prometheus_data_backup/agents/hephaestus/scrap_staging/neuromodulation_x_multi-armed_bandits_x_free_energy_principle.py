import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuromodulated Active-Inference Bandit Reasoner.
    
    Mechanism:
    1. Generative Model (Free Energy Core): Parses prompt structure (negations, 
       comparatives, conditionals) to establish a logical baseline. This acts as 
       the 'prior' belief state.
    2. Neuromodulation (Precision Weighting): Computes a 'surprise' metric based 
       on the mismatch between structural expectations and candidate content. 
       High surprise (high prediction error) increases exploration weight; 
       low surprise increases exploitation of structural matches.
    3. Multi-Armed Bandit (Hypothesis Selection): Treats each candidate as an 'arm'.
       The reward function combines structural adherence (exploitation) with 
       information gain potential (exploration via NCD diversity). 
       Scores are ranked by negative free energy (minimizing surprise + complexity).
    """

    def __init__(self):
        # State for bandit history (simplified for stateless evaluate interface)
        self._structural_keywords = {
            'negation': ['not', 'no', 'never', 'neither', 'without', 'fail'],
            'comparative': ['more', 'less', 'greater', 'smaller', 'better', 'worse', '>', '<'],
            'conditional': ['if', 'then', 'unless', 'otherwise', 'provided'],
            'numeric': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        }

    def _extract_structure(self, text: str) -> Dict[str, float]:
        """Extracts structural features acting as the generative model's priors."""
        text_lower = text.lower()
        features = {
            'negation_count': 0,
            'comparative_count': 0,
            'conditional_count': 0,
            'has_numbers': False,
            'length': len(text)
        }
        
        for word in self._structural_keywords['negation']:
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                features['negation_count'] += 1
        
        for word in self._structural_keywords['comparative']:
            if word in text_lower:
                features['comparative_count'] += 1
                
        for word in self._structural_keywords['conditional']:
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                features['conditional_count'] += 1
                
        if any(c.isdigit() for c in text):
            features['has_numbers'] = True
            
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker for complexity."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _numeric_evaluation(self, prompt: str, candidate: str) -> float:
        """Detects and evaluates numeric comparisons within the text."""
        # Extract numbers from prompt and candidate
        def get_nums(t):
            return [float(x) for x in re.findall(r"-?\d+\.?\d*", t)]
        
        p_nums = get_nums(prompt)
        c_nums = get_nums(candidate)
        
        if not p_nums or not c_nums:
            return 0.5 # Neutral if no numbers
        
        # Simple heuristic: If prompt implies ordering (e.g., contains "greater"),
        # check if candidate numbers respect it. 
        # Since we don't parse full logic trees here, we reward candidates that 
        # contain the specific numbers found in the prompt (constraint propagation).
        match_count = 0
        for n in c_nums:
            if n in p_nums:
                match_count += 1
        
        return min(1.0, match_count / max(1, len(c_nums)))

    def _calculate_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes negative Free Energy.
        F = Accuracy (Structure match) - Complexity (NCD)
        Lower F is better. We return -F as the score.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        # 1. Prediction Error (Surprise) based on structural mismatch
        # If prompt has negations, good candidates should likely reflect logical handling 
        # (simplified here to presence/absence correlation for robustness)
        error_term = 0.0
        
        # Penalize if prompt has strong structure but candidate ignores it
        if p_struct['negation_count'] > 0 and c_struct['negation_count'] == 0:
            # Potential penalty, but not absolute (context matters)
            error_term += 0.2 
            
        if p_struct['conditional_count'] > 0 and c_struct['conditional_count'] == 0:
            error_term += 0.1
            
        # 2. Numeric Constraint Propagation
        numeric_score = self._numeric_evaluation(prompt, candidate)
        if numeric_score < 0.5:
            error_term += 0.3 # High surprise if numbers don't match
            
        # 3. Complexity (NCD) - Occam's razor
        # We want the candidate to be compressible relative to the prompt context
        complexity = self._compute_ncd(prompt, candidate)
        
        # Free Energy Approximation: Surprise + Complexity
        # We weight structural error heavily (Reasoning requirement)
        free_energy = (error_term * 2.0) + (complexity * 0.5)
        
        return -free_energy # Return negative free energy as score (higher is better)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates using neuromodulated active-inference logic.
        Precision weighting is applied to structural matches.
        """
        if not candidates:
            return []
            
        results = []
        p_struct = self._extract_structure(prompt)
        
        # Calculate base scores (Free Energy minimization)
        scores = []
        for cand in candidates:
            score = self._calculate_free_energy(prompt, cand)
            
            # Neuromodulatory Gain: Adjust score based on 'precision' of the match
            # If the candidate length is wildly different, reduce precision (gain)
            len_ratio = min(len(cand), len(prompt)) / max(len(cand), len(prompt), 1)
            gain = 0.8 + (0.2 * len_ratio) # Gain between 0.8 and 1.0
            
            final_score = score * gain
            scores.append((cand, final_score))
        
        # Bandit-style ranking: Sort by score (exploitation of best hypothesis)
        # In a real loop, we would add UCB bonus for untested arms, 
        # but here we rank existing candidates.
        scores.sort(key=lambda x: x[1], reverse=True)
        
        for cand, score in scores:
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Minimized free energy via structural alignment (neg:{self._extract_structure(cand)['negation_count']}, comp:{self._extract_structure(cand)['comparative_count']}) and complexity control."
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence (0-1) based on negative free energy normalized.
        """
        # Get raw score
        raw_score = self._calculate_free_energy(prompt, answer)
        
        # Map to 0-1 range. 
        # Theoretically, perfect match has low free energy (high negative F? No, low F).
        # Our function returns -F. So high score = good.
        # Max theoretical score approx 0 (perfect), min could be -2.0 or lower.
        # Let's normalize: score + 2.0 / 2.0 -> clamp to 0-1
        
        # Heuristic normalization based on typical error ranges
        # Perfect structural match + low complexity ~ -0.2 to 0.0
        # Bad match ~ -1.0 to -3.0
        normalized = (raw_score + 2.0) / 2.0
        return max(0.0, min(1.0, normalized))