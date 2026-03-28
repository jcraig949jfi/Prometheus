import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Functorial Minimum Description Length (fMDL) Reasoning Tool.
    
    Mechanism:
    1. Hypothesis Category (H): The set of candidate answers.
    2. Observation Category (O): The structural signature of the prompt.
    3. Functor F: Maps a candidate to a predicted structural outcome.
       - We approximate the 'Functor Image' by analyzing how well the candidate 
         satisfies the structural constraints (negations, comparatives, conditionals) 
         extracted from the prompt.
    4. Scoring (MDL + MaxEnt):
       - K(F(h)): Approximated by the complexity of the structural match. 
         A perfect structural match yields low complexity (high score).
         Mismatches or ignored constraints increase complexity (penalty).
       - MaxEnt Regularizer: Used ONLY in confidence() to assess if the answer 
         is a generic placeholder (low entropy/high uncertainty) vs specific.
         Per safety guidelines, MaxEnt is restricted to the confidence wrapper.
    5. Optimization: Candidates are ranked by their structural adherence score,
       with NCD used strictly as a tiebreaker for candidates with identical structural scores.
    """

    def __init__(self):
        self._keywords = {
            'negation': ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'],
            'comparative': ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'better', 'worse', 'than'],
            'conditional': ['if', 'then', 'unless', 'otherwise', 'provided'],
            'logic_ops': ['and', 'or', 'but', 'however']
        }

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extracts structural features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        features = {
            'has_negation': any(k in text_lower for k in self._keywords['negation']),
            'has_comparative': any(k in text_lower for k in self._keywords['comparative']),
            'has_conditional': any(k in text_lower for k in self._keywords['conditional']),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'word_count': len(words)
        }
        
        # Detect numeric comparisons explicitly
        features['numeric_comparison'] = False
        if len(features['numbers']) >= 2:
            # Simple heuristic: if prompt has 2+ numbers, it likely implies comparison
            features['numeric_comparison'] = True
            
        return features

    def _evaluate_structural_fit(self, prompt: str, candidate: str) -> float:
        """
        Computes the 'Functorial Score'. 
        Measures how well the candidate respects the prompt's structural constraints.
        Lower penalty = better fit (lower Kolmogorov complexity of the mapping).
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        score = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negation, a valid answer often acknowledges it or doesn't contradict it blindly
        if p_struct['has_negation']:
            # Heuristic: If prompt negates, and candidate is a simple 'yes' without context, penalize?
            # Instead, we check if the candidate contradicts the negation logic if detectable.
            # Simplified: If prompt has negation, we reward candidates that are not trivially short 
            # (assuming trivial answers miss the nuance) OR contain specific negation words if appropriate.
            if c_struct['has_negation']:
                score += 2.0 # Reward matching negation logic
            elif len(candidate.split()) < 3:
                score -= 1.5 # Penalty for oversimplification in negated contexts

        # 2. Comparative/Numeric Consistency
        if p_struct['numeric_comparison'] or p_struct['has_comparative']:
            # If prompt compares numbers, candidate should ideally contain a number or a comparative word
            if c_struct['numbers'] or c_struct['has_comparative']:
                score += 2.0
            else:
                # Heavy penalty for ignoring numeric/comparative constraints
                score -= 3.0
        
        # 3. Conditional Logic
        if p_struct['has_conditional']:
            # Candidates that are too short often fail conditional logic
            if len(candidate.split()) < 4:
                score -= 1.0
                
        # 4. Length/Complexity Regularization (Occam's Razor)
        # Prefer concise but sufficient answers. 
        # Penalize extreme verbosity (overfitting) and extreme brevity (underfitting)
        p_len = p_struct['word_count']
        c_len = len(candidate.split())
        
        if c_len == 0:
            score -= 10.0
        elif c_len > p_len * 1.5:
            score -= (c_len - p_len) * 0.1 # Penalty for excessive length
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
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
        results = []
        
        # Pre-calculate prompt structure to ensure consistency
        # In a real functor, this is the domain object O
        
        for cand in candidates:
            # 1. Compute Structural Score (The Functorial Mapping Quality)
            struct_score = self._evaluate_structural_fit(prompt, cand)
            
            # 2. Compute NCD Tiebreaker (Only used if structural scores are close/equal)
            # We invert NCD because lower distance is better, but we want higher score = better
            ncd_val = self._ncd(prompt, cand)
            ncd_score = -ncd_val # Negative because lower NCD is better
            
            # Primary sort key: Structural Score
            # Secondary sort key: NCD (as a float tiebreaker)
            results.append({
                "candidate": cand,
                "score": struct_score,
                "ncd_backup": ncd_score,
                "reasoning": f"Structural fit: {struct_score:.2f}, NCD backup: {ncd_score:.4f}"
            })

        # Sort: Primary by structural score (desc), Secondary by NCD backup (desc, i.e., min NCD)
        results.sort(key=lambda x: (x['score'], x['ncd_backup']), reverse=True)
        
        # Normalize scores to be more interpretable (optional, but good for ranking)
        # Just returning the raw calculated score is fine per interface, 
        # but let's ensure the 'score' field reflects the final ranking logic clearly.
        # We will strip the internal 'ncd_backup' from the final output to match interface strictly if needed,
        # but the interface says return list of dicts with specific keys. 
        # We will clean the dict to match the requested format exactly.
        
        final_results = []
        for r in results:
            final_results.append({
                "candidate": r["candidate"],
                "score": r["score"], # Higher is better
                "reasoning": r["reasoning"]
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses MaxEnt principle restricted to structural parsing:
        - High confidence if the answer satisfies structural constraints uniquely.
        - Low confidence if the answer is a high-entropy generic string (e.g., "I don't know", random noise)
          or if it fails basic structural checks (negation/numbers).
        """
        if not answer or not answer.strip():
            return 0.0
            
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        confidence = 1.0
        
        # MaxEnt Regularizer: Penalize high-entropy (generic) responses in constrained contexts
        # If prompt has specific constraints (numbers, logic), generic answers have low probability of being correct.
        if p_struct['has_negation'] or p_struct['numeric_comparison'] or p_struct['has_conditional']:
            # If the answer is very short and the prompt was complex, uncertainty rises
            if len(answer.split()) < 3:
                confidence -= 0.4
            
            # If prompt has numbers but answer has none, confidence drops significantly
            if p_struct['numeric_comparison'] and not a_struct['numbers']:
                confidence -= 0.5
                
            # If prompt has negation and answer ignores it (no negation words, very short)
            if p_struct['has_negation'] and not a_struct['has_negation'] and len(answer.split()) < 4:
                confidence -= 0.3

        # Bonus for structural alignment
        if self._evaluate_structural_fit(prompt, answer) > 0:
            confidence += 0.2
            
        return max(0.0, min(1.0, confidence))