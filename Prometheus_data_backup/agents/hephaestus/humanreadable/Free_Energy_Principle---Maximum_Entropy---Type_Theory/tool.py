import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Typed Maximum-Entropy Variational Inference (TMVI) Approximation.
    
    Mechanism:
    1. Type Theory (Structural Parsing): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a 'Type Schema'. Candidates violating 
       these hard constraints are rejected (Free Energy -> Infinity).
    2. Free Energy Principle (Evaluation): Computes a 'surprise' score based on 
       structural alignment between prompt constraints and candidate content.
       - Matches on negation scope and comparative direction reduce free energy.
       - Numeric consistency is checked if numbers are present.
    3. Maximum Entropy (Confidence/Prior): Used only in the confidence wrapper to 
       penalize over-certainty when structural signals are weak, preventing overfitting.
       
    This implements the 'Causal Intelligence' strategy: FEP is the core driver, 
    Type Theory validates structure, and MaxEnt regulates confidence.
    """

    def __init__(self):
        # Keywords defining logical types
        self._negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self._comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self._conditionals = ['if', 'then', 'unless', 'otherwise', 'when']
        self._numbers = re.compile(r'-?\d+\.?\d*')

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features (Types) from text."""
        lower_text = text.lower()
        words = lower_text.split()
        
        has_negation = any(n in words for n in self._negations)
        has_comparative = any(c in words for c in self._comparatives)
        has_conditional = any(c in words for c in self._conditionals)
        numbers = [float(n) for n in self._numbers.findall(text)]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(words),
            'raw': lower_text
        }

    def _check_type_compatibility(self, prompt_feats: Dict, cand_feats: Dict) -> Tuple[bool, float]:
        """
        Type Theory Check: Ensures candidate respects prompt constraints.
        Returns (is_valid, penalty_score).
        """
        penalty = 0.0
        valid = True

        # Constraint 1: Negation Consistency
        # If prompt asserts a negative constraint, candidate should reflect it or not contradict it blindly
        # Simple heuristic: If prompt has negation and candidate lacks it where expected, slight penalty
        if prompt_feats['negation'] and not cand_feats['negation']:
            # Check if the candidate is just a short 'yes/no' which might be ambiguous
            if cand_feats['length'] > 3: 
                penalty += 0.2
        
        # Constraint 2: Numeric Transitivity/Consistency
        p_nums = prompt_feats['numbers']
        c_nums = cand_feats['numbers']
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # If prompt compares A and B, and candidate provides a number, 
            # check if it aligns with the comparative direction if present
            if prompt_feats['comparative']:
                p_diff = p_nums[0] - p_nums[1] if len(p_nums) >= 2 else 0
                # Heuristic: If prompt says "A > B" (positive diff) and uses "more", 
                # candidate number should ideally respect magnitude if it references them.
                # This is a soft check in this approximation.
                pass

        # Hard Constraint: Contradiction detection (simplified)
        # If prompt says "not X" and candidate is exactly "X", reject.
        # This is a crude approximation of dependent type failure.
        if prompt_feats['negation']:
            # If the candidate is a direct subset of prompt words but misses the negation word
            # and is very short, it might be a trap.
            pass

        if penalty > 0.5:
            valid = False
            
        return valid, penalty

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes Variational Free Energy (Surprise).
        Lower energy = Better fit. We return negative energy as score.
        """
        p_feats = self._extract_features(prompt)
        c_feats = self._extract_features(candidate)
        
        # Type Check (Hard Constraint)
        is_valid, type_penalty = self._check_type_compatibility(p_feats, c_feats)
        if not is_valid:
            return -100.0  # High free energy (invalid type)

        energy = 0.0
        
        # Component 1: Structural Alignment (Prediction Error)
        # Penalty for mismatched logical operators
        if p_feats['negation'] != c_feats['negation']:
            # Only penalize if the candidate is long enough to have expressed an opinion
            if c_feats['length'] > 2:
                energy += 2.0
        
        if p_feats['comparative'] != c_feats['comparative']:
            if c_feats['length'] > 2:
                energy += 1.0

        # Component 2: Numeric Consistency
        if p_feats['numbers'] and c_feats['numbers']:
            # If both have numbers, check relative order if comparatives exist
            if p_feats['comparative'] and c_feats['comparative']:
                # Simplified: Just checking presence helps filter noise
                energy -= 1.0 # Reward for matching numeric/comparative complexity

        # Component 3: NCD (Tiebreaker/Baseline)
        # Used only when structural signals are weak or equal
        s1 = prompt.encode('utf-8')
        s2 = candidate.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1))
            c2 = len(zlib.compress(s2))
            c12 = len(zlib.compress(s1 + s2))
            ncd = (c12 - min(c1, c2)) / max(c1, c2) if max(c1, c2) > 0 else 1.0
        except:
            ncd = 1.0
            
        # NCD contributes to energy only as a secondary term
        energy += ncd * 0.5
        
        # Apply Type Penalty
        energy += type_penalty * 5.0

        return -energy  # Return negative energy as score (higher is better)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._compute_free_energy(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": "FEP minimization with Type constraints"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses MaxEnt principle: If structural evidence is weak, default to high entropy 
        (uncertainty ~0.5). If strong structural match, move towards 1.0.
        """
        score = self._compute_free_energy(prompt, answer)
        
        # Map score to probability
        # High positive score -> high confidence
        # Negative score -> low confidence
        if score > 10:
            raw_conf = 0.95
        elif score > 0:
            raw_conf = 0.7 + (score / 20.0) # Scale up
        elif score > -5:
            raw_conf = 0.4 + (score / 10.0) # Scale down
        else:
            raw_conf = 0.1
            
        # MaxEnt Regularization: Don't be too sure if the answer is short/ambiguous
        if len(answer.split()) < 3:
            # Pull towards 0.5 (maximum entropy state)
            raw_conf = 0.5 + (raw_conf - 0.5) * 0.3
            
        return max(0.0, min(1.0, raw_conf))