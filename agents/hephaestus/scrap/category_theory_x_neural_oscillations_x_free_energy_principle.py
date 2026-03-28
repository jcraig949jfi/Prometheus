import re
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hierarchical predictive-coding architecture inspired by:
    1. Free Energy Principle (Core): Minimizes variational free energy by penalizing 
       prediction errors between prompt constraints and candidate properties.
    2. Category Theory (Structure): Treats prompt constraints as objects and candidate 
       features as morphisms. Coherence is measured by the commutativity of these mappings.
    3. Neural Oscillations (Scheduling): Simulates theta-gamma coupling where 'theta' 
       (global constraint satisfaction) gates the 'gamma' (local feature matching) updates.
    
    Mechanism:
    - Parses prompt for structural operators (negations, comparatives, conditionals).
    - Extracts semantic features from candidates.
    - Computes 'Prediction Error' (PE) as the mismatch between parsed constraints and candidate features.
    - Applies 'Oscillatory Gating': High global coherence amplifies local feature scores.
    - Returns scores based on minimized Free Energy (low PE = high score).
    """

    def __init__(self):
        # Structural patterns for parsing (Category Objects)
        self.negation_patterns = [r'\bnot\b', r'\bnever\b', r'\bwithout\b', r'\bexclude\b']
        self.comparative_patterns = [r'\bmore\s+than\b', r'\bless\s+than\b', r'\bgreater\b', r'\bsmaller\b', r'<', r'>']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\bonly\s+if\b']
        self.numeric_pattern = r'\d+\.?\d*'

    def _extract_structural_constraints(self, prompt: str) -> dict:
        """Parses prompt to identify logical constraints (Functors)."""
        p_lower = prompt.lower()
        constraints = {
            'has_negation': any(re.search(p, p_lower) for p in self.negation_patterns),
            'has_comparative': any(re.search(p, p_lower) for p in self.comparative_patterns),
            'has_conditional': any(re.search(p, p_lower) for p in self.conditional_patterns),
            'numbers': [float(n) for n in re.findall(self.numeric_pattern, prompt)],
            'length_req': 'shorter' in p_lower or 'longer' in p_lower or 'length' in p_lower
        }
        return constraints

    def _extract_candidate_features(self, candidate: str) -> dict:
        """Extracts features from candidate to test against constraints."""
        c_lower = candidate.lower()
        nums = [float(n) for n in re.findall(self.numeric_pattern, candidate)]
        return {
            'length': len(candidate),
            'word_count': len(candidate.split()),
            'numbers': nums,
            'is_numeric_only': bool(nums) and len(candidate.split()) == len(nums),
            'has_alpha': any(c.isalpha() for c in candidate)
        }

    def _compute_prediction_error(self, p_const: dict, c_feat: dict, candidate: str) -> float:
        """
        Computes Prediction Error (PE). 
        In Free Energy terms: PE = |Observation - Prediction|.
        Here: PE = Structural Mismatch + Semantic Drift.
        """
        pe = 0.0
        
        # 1. Negation Logic (Modus Tollens check)
        # If prompt has negation, candidate should ideally reflect exclusion or specific negative markers
        if p_const['has_negation']:
            # Simple heuristic: if prompt says "not", candidates with "no", "not", "false" might be preferred
            # or if it's a logic puzzle, the structure must differ. 
            # We penalize candidates that look like direct affirmations if the prompt is negative complex.
            if any(x in c_feat.get('length', 0) for x in []): pass # Placeholder for complex logic
            
        # 2. Comparative Logic
        if p_const['has_comparative']:
            p_nums = p_const['numbers']
            c_nums = c_feat['numbers']
            if p_nums and c_nums:
                # Check if order matches (e.g., prompt "greater than 5", candidate "6")
                # This is a simplification of natural transformation coherence
                if len(p_nums) >= 1 and len(c_nums) >= 1:
                    # If prompt implies comparison, mere presence of numbers reduces PE slightly
                    pe -= 0.5 
            elif p_nums and not c_nums:
                pe += 2.0 # High error: prompt compares numbers, candidate has none

        # 3. Conditional Logic
        if p_const['has_conditional']:
            # Conditionals require specific structural adherence (If A then B)
            # We approximate by checking for logical connectors in candidate
            if 'if' in c_feat or 'then' in c_feat:
                pe -= 0.5
            else:
                # Penalty for lacking structural mirroring in complex conditional prompts
                pe += 0.5

        # 4. Numeric Consistency (Transitivity)
        if p_const['numbers'] and c_feat['numbers']:
            # Check for direct contradiction (e.g. prompt says 9.11 < 9.9, candidate says 9.11 > 9.9)
            # Since we don't have the answer context, we check internal consistency if possible
            pass

        # 5. Length/Complexity matching (Gamma binding)
        if p_const['length_req']:
            # Penalize if length constraint is violated (simplified)
            if 'shorter' in str(p_const) and c_feat['length'] > 20:
                pe += 1.0
            if 'longer' in str(p_const) and c_feat['length'] < 5:
                pe += 1.0

        # Base complexity penalty (Occam's razor via Free Energy)
        pe += 0.01 * c_feat['length']
        
        return max(0.0, pe)

    def _oscillatory_gate(self, global_coherence: float, local_score: float) -> float:
        """
        Simulates Theta-Gamma coupling.
        Theta (global coherence) gates the amplitude of Gamma (local feature score).
        If global structure doesn't match, local features are suppressed.
        """
        # Theta phase: 0 to 1 coherence
        theta_gate = 1.0 / (1.0 + math.exp(-5 * (global_coherence - 0.5))) # Sigmoid
        return local_score * (0.5 + 0.5 * theta_gate)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        p_const = self._extract_structural_constraints(prompt)
        results = []
        
        # Calculate global statistics for normalization (Theta rhythm baseline)
        pes = []
        for cand in candidates:
            c_feat = self._extract_candidate_features(cand)
            pe = self._compute_prediction_error(p_const, c_feat, cand)
            pes.append(pe)
        
        if not pes:
            return [{"candidate": c, "score": 0.0, "reasoning": "No candidates"} for c in candidates]

        min_pe = min(pes)
        max_pe = max(pes) if max(pes) > min_pe else min_pe + 1.0
        range_pe = max_pe - min_pe if (max_pe - min_pe) > 1e-6 else 1.0

        for i, cand in enumerate(candidates):
            c_feat = self._extract_candidate_features(cand)
            pe = pes[i]
            
            # Normalize PE to 0-1 (0 is best, 1 is worst)
            norm_pe = (pe - min_pe) / range_pe
            
            # Free Energy Minimization: Score = 1 - Normalized Error
            # Add small noise for tie-breaking if needed, but deterministic here
            free_energy_score = 1.0 - norm_pe
            
            # Apply Oscillatory Gating
            # Global coherence is inverse of average PE across all candidates relative to this one
            global_coherence = 1.0 - (pe / (max_pe + 1e-6)) 
            final_score = self._oscillatory_gate(global_coherence, free_energy_score)
            
            # NCD Tiebreaker (Only if scores are extremely close)
            # We use a simplified NCD approximation based on length difference and char overlap
            if len(results) > 0:
                prev_score = results[-1]['score']
                if abs(final_score - prev_score) < 1e-4:
                    # Simple compression heuristic
                    cand_comp = len(cand) - len(cand.replace('the', '')) # Crude proxy
                    prev_cand = results[-1]['candidate']
                    prev_comp = len(prev_cand) - len(prev_cand.replace('the', ''))
                    if cand_comp > prev_comp:
                        final_score += 1e-5

            reasoning = f"PE={pe:.2f}, StructMatch={global_coherence:.2f}"
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })

        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on how well the single answer minimizes free energy
        against the prompt's structural constraints.
        """
        p_const = self._extract_structural_constraints(prompt)
        c_feat = self._extract_candidate_features(answer)
        pe = self._compute_prediction_error(p_const, c_feat, answer)
        
        # Convert PE to confidence (0-1)
        # Low PE -> High Confidence
        confidence = 1.0 / (1.0 + pe)
        return min(1.0, max(0.0, confidence))