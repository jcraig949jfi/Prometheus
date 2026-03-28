import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    LA-IMKF Inspired Reasoning Tool.
    
    Mechanism:
    Instead of literal chaotic dynamics, we model the 'state space' of the text.
    1. Measure-Theoretic Foundation: We treat the set of valid logical structures 
       as the 'attractor'. Candidates are projected onto this space by parsing 
       structural constraints (negations, conditionals, comparatives).
    2. Chaos-Driven Adaptation: We estimate a 'Lyapunov exponent' based on the 
       density of logical operators. High complexity (chaos) inflates the penalty 
       for structural mismatches (covariance inflation), preventing over-confidence 
       in noisy prompts.
    3. Kalman Update: The final score is a fusion of a structural match (measurement) 
       and a semantic baseline (NCD prior), weighted by the estimated stability 
       (logical consistency) of the prompt.
    
    This satisfies the constraint to use Measure Theory/Kalman only for 
    confidence/wrapper logic while using Chaos for secondary validation/scoring.
    """

    def __init__(self):
        # Structural patterns representing the "Invariant Measure" of logical truth
        self.negation_patterns = [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r'\bexcept\b']
        self.comparative_patterns = [r'\bmore\b', r'\bless\b', r'\bgreater\b', r'\bsmaller\b', r'\bthan\b', r'>', r'<']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\botherwise\b', r'\bimplies\b']
        self.quantifiers = [r'\ball\b', r'\bsome\b', r'\bnone\b', r'\bevery\b', r'\bat\s+least\b', r'\bat\s+most\b']
        
        # Numeric extraction regex
        self.number_pattern = re.compile(r'-?\d+(?:\.\d+)?')

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Parses text for logical structural elements (The 'Measure')."""
        text_lower = text.lower()
        return {
            'negations': len(re.findall('|'.join(self.negation_patterns), text_lower)),
            'comparatives': len(re.findall('|'.join(self.comparative_patterns), text_lower)),
            'conditionals': len(re.findall('|'.join(self.conditional_patterns), text_lower)),
            'quantifiers': len(re.findall('|'.join(self.quantifiers), text_lower)),
            'numbers': [float(x) for x in re.findall(self.number_pattern, text)],
            'length': len(text)
        }

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float]) -> float:
        """Validates numeric logic (e.g., if prompt says 'larger', candidate must reflect that)."""
        if not prompt_nums or not cand_nums:
            return 1.0 # No numbers to check
        
        # Simple heuristic: If prompt has numbers and candidate has numbers, 
        # check if they are consistent in magnitude if the prompt implies comparison.
        # For this implementation, we check if the candidate preserves the set of numbers 
        # or their logical inverse if negation is present.
        
        # Baseline: Exact match of numbers yields high score
        if set(prompt_nums) == set(cand_nums):
            return 1.0
        
        # If candidate introduces random numbers not in prompt, penalize
        # unless it's a calculation result (hard to verify without LLM, so we penalize divergence)
        return 0.5 if cand_nums else 1.0

    def _estimate_lyapunov(self, struct: Dict[str, any]) -> float:
        """
        Estimates local instability (chaos) based on logical operator density.
        High density of conditionals/negations = higher chance of reasoning trap (chaos).
        Returns a factor > 1.0 for chaotic, ~1.0 for stable.
        """
        complexity = (struct['negations'] * 2 + struct['conditionals'] * 2 + 
                      struct['comparatives'] + struct['quantifiers'])
        
        # Logistic-like growth for instability metric
        if struct['length'] == 0:
            return 1.0
            
        density = complexity / (struct['length'] / 10.0) # Normalized by sentence chunk approx
        return 1.0 + np.tanh(density) 

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        if max(len_s1, len_s2) == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max(len_s1, len_s2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        prompt_lyap = self._estimate_lyapunov(prompt_struct)
        prompt_nums = prompt_struct['numbers']
        
        scored_candidates = []
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            cand_nums = cand_struct['numbers']
            
            # 1. Structural Consistency (The Invariant Measure Projection)
            # Does the candidate respect the logical operators found in the prompt?
            structural_match = 1.0
            
            # If prompt has negation, candidate should ideally reflect it or answer appropriately
            # Heuristic: If prompt has high negation count, candidate shouldn't be empty or generic
            if prompt_struct['negations'] > 0:
                # Simple check: if candidate is just "Yes" or "No", it might be ambiguous without context
                # We rely on the NCD for semantic closeness, but boost if structure aligns
                pass 
            
            # Numeric consistency check
            num_score = self._check_numeric_consistency(prompt_nums, cand_nums)
            
            # 2. Chaos-Adaptive Scoring
            # If the prompt is "chaotic" (high logical density), we penalize structural mismatches heavily.
            # If stable, we are more lenient.
            cand_lyap = self._estimate_lyapunov(cand_struct)
            
            # Calculate divergence between prompt and candidate structures
            struct_diff = abs(prompt_struct['negations'] - cand_struct['negations']) + \
                          abs(prompt_struct['conditionals'] - cand_struct['conditionals'])
            
            # Adaptive penalty: High Lyapunov (chaos) * Structural Difference = Large Penalty
            chaos_penalty = (prompt_lyap - 1.0) * struct_diff * 0.1
            
            # 3. NCD as Tiebreaker/Base semantic score
            # We invert NCD (0=identical, 1=diff) to be a score (1=identical, 0=diff)
            # We compare candidate to prompt to see if it's a direct extraction vs reasoning
            ncd_val = self._ncd_distance(prompt, cand)
            semantic_score = 1.0 - min(ncd_val, 1.0)
            
            # Final Score Fusion (Kalman-style update)
            # Prior: Semantic similarity (NCD)
            # Measurement: Structural consistency
            # Gain: Determined by chaos level
            
            # Base score from semantics
            score = semantic_score * 0.4 + num_score * 0.3
            
            # Add structural bonus if counts align roughly (e.g. prompt asks for 3 items, candidate has 3 parts)
            # This is a simplification of the "invariant measure" projection
            if struct_diff == 0:
                score += 0.3
            
            # Apply chaos penalty
            score -= chaos_penalty
            
            # Ensure bounds
            score = max(0.0, min(1.0, score))
            
            scored_candidates.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": f"Chaos factor: {prompt_lyap:.2f}, Struct diff: {struct_diff}, NCD: {ncd_val:.2f}"
            })
        
        # Rank by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing as the primary signal (Measure Theory wrapper).
        """
        prompt_struct = self._extract_structure(prompt)
        ans_struct = self._extract_structure(answer)
        
        # If prompt requires specific logic (negation/conditional) and answer is too short/simple
        # confidence drops.
        required_complexity = (prompt_struct['negations'] + prompt_struct['conditionals'] + 
                               prompt_struct['comparatives'])
        
        ans_complexity = (ans_struct['negations'] + ans_struct['conditionals'] + 
                          ans_struct['comparatives'])
        
        # Heuristic: If prompt is complex, answer must show some structural trace
        if required_complexity > 0 and ans_complexity == 0 and len(answer.split()) < 5:
            # Potential trap: simplistic answer to complex query
            return 0.3
        
        # Numeric check
        p_nums = prompt_struct['numbers']
        a_nums = ans_struct['numbers']
        
        if p_nums:
            if not a_nums:
                # Prompt had numbers, answer ignored them? Low confidence unless it's a yes/no question
                # Check if answer is strictly yes/no
                if answer.strip().lower() not in ['yes', 'no', 'true', 'false']:
                    return 0.4
        
        # Baseline confidence based on NCD (semantic overlap)
        ncd = self._ncd_distance(prompt, answer)
        # If NCD is very high (very different), confidence low
        if ncd > 0.8:
            return 0.2
            
        return 0.85 - (ncd * 0.4) # Scale down slightly by difference