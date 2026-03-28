import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    HM-ICE Approximation: Holographic-Measure-Theoretic Incentive-Compatible Engine.
    
    Mechanism Analogy:
    1. Measure Theory (Restricted): Used only for structural parsing (counting logical 
       operators, negations, conditionals) to define a 'logic measure' on the text space.
       Avoided for direct scoring to prevent historical failure modes.
    2. Holography Principle: Projects high-dimensional text into a low-dimensional 
       'boundary' vector (counts of specific structural tokens). This compresses the 
       hypothesis space while preserving logical topology.
    3. Mechanism Design (VCG-style): Candidates are scored by their marginal contribution 
       to the 'logical consistency' of the prompt-answer pair. The scoring rule penalizes 
       deviation from the prompt's structural constraints (e.g., if prompt has negation, 
       answer must reflect it). This simulates incentive compatibility where 'truthful' 
       answers align best with structural constraints.
    
    Strategy:
    - Primary Signal: Structural parsing (negations, comparatives, conditionals, numbers).
    - Secondary Signal: NCD (Compression) used strictly as a tiebreaker.
    - Separation: Holographic projection and Mechanism scoring are distinct steps.
    """

    def __init__(self):
        # Structural keywords defining the "measure" space
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'better', 'worse', '>', '<']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided', 'when']
        self.booleans = ['true', 'false', 'yes', 'no']
        
    def _extract_structure(self, text: str) -> Dict[str, float]:
        """Projects text to holographic boundary (structural counts)."""
        t = text.lower()
        words = re.findall(r'\b\w+\b', t)
        
        counts = {
            'neg': sum(words.count(w) for w in self.negations),
            'comp': sum(words.count(w) for w in self.comparatives),
            'cond': sum(words.count(w) for w in self.conditionals),
            'bool': sum(words.count(w) for w in self.booleans),
            'nums': len(re.findall(r'\d+\.?\d*', t)),
            'len': len(words)
        }
        return counts

    def _check_numeric_consistency(self, prompt: str, answer: str) -> float:
        """Evaluates numeric logic if present."""
        p_nums = re.findall(r'\d+\.?\d*', prompt.lower())
        a_nums = re.findall(r'\d+\.?\d*', answer.lower())
        
        if not p_nums:
            return 1.0 # No numeric constraint
        
        # Simple heuristic: If prompt asks for comparison, check if answer contains numbers
        has_comp = any(w in prompt.lower() for w in self.comparatives)
        
        if has_comp and not a_nums:
            # Prompt implies comparison but answer has no numbers -> likely wrong
            return 0.2
            
        if a_nums and p_nums:
            # Check if answer numbers are subset or derived (loose check)
            # In a full engine, this would solve the math. Here we check presence.
            return 1.0
            
        return 0.5

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            max_len = max(z1, z2)
            if max_len == 0: return 0.0
            return (z12 - min(z1, z2)) / max_len
        except:
            return 1.0

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Computes VCG-style score based on structural alignment.
        Returns (score, reasoning_string).
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        score = 0.0
        reasons = []
        
        # 1. Negation Consistency (Measure Theoretic Constraint)
        # If prompt has negation, valid answers often need to acknowledge it or be carefully phrased.
        # Heuristic: High negation in prompt requires precise structural match.
        if p_struct['neg'] > 0:
            if c_struct['neg'] > 0 or any(b in candidate.lower() for b in ['yes', 'no']):
                score += 2.0
                reasons.append("Negation handled")
            else:
                score -= 1.0
                reasons.append("Negation mismatch")
        
        # 2. Comparative Logic
        if p_struct['comp'] > 0:
            if c_struct['comp'] > 0 or c_struct['nums'] > 0:
                score += 2.5
                reasons.append("Comparative logic detected")
            else:
                score -= 0.5
                reasons.append("Missing comparative response")

        # 3. Conditional Flow
        if p_struct['cond'] > 0:
            if c_struct['cond'] > 0 or c_struct['len'] > 5: # Detailed answer expected
                score += 1.5
                reasons.append("Conditional flow preserved")
        
        # 4. Numeric Evaluation
        num_score = self._check_numeric_consistency(prompt, candidate)
        score += num_score * 2.0
        if num_score < 1.0:
            reasons.append("Numeric inconsistency")

        # 5. Length Penalty (Occam's Razor / Mechanism Design)
        # Penalize overly verbose answers that don't add structural value
        if c_struct['len'] > p_struct['len'] * 1.5 and c_struct['len'] > 50:
            score -= 0.5
            reasons.append("Verbosity penalty")
        else:
            score += 0.5

        # Tiebreaker: NCD (Holographic compression similarity)
        ncd = self._compute_ncd(prompt, candidate)
        # Lower NCD is better (more similar structure), so we subtract it
        score -= (ncd * 0.1) 
        
        return score, "; ".join(reasons) if reasons else "Structural baseline"

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment score.
        """
        score, _ = self._score_candidate(prompt, answer)
        
        # Map score to 0-1 range using a sigmoid-like clamp
        # Baseline score is roughly 0-4. 
        # < 0 -> low confidence, > 3 -> high confidence
        conf = 1.0 / (1.0 + math.exp(-score + 1.0))
        
        # Hard constraints for obvious failures
        if "no" in answer.lower() and "yes" in answer.lower():
            return 0.1 # Contradiction
            
        return max(0.0, min(1.0, conf))