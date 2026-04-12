import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic Variational Reasoning Tool (TVRT).
    
    Mechanism:
    Implements a computational analogy of the Free Energy Principle (FEP) combined 
    with Thermodynamic constraints. 
    1. Free Energy (FEP): The core score is derived from the structural alignment 
       between the prompt's logical constraints and the candidate's content. 
       Lower 'variational free energy' (higher score) corresponds to better 
       satisfaction of prompt conditions (negations, comparatives, logic).
    2. Thermodynamics: We apply a 'detailed balance' check. If a candidate 
       contradicts explicit structural constraints (e.g., says 'Yes' when prompt 
       has 'NOT'), it incurs a high 'energy penalty'. 
    3. Maximum Entropy (MaxEnt): Used ONLY in the confidence wrapper. Instead of 
       maximizing entropy for scoring (which fails reasoning traps), we use 
       entropy production as a 'plausibility flag'. If the distribution of 
       logical features in the answer is too uniform (high entropy) relative 
       to the sharp constraints of the prompt, confidence is reduced.
       
    This avoids the 'MaxEnt inhibitor' trap by restricting MaxEnt to a 
    meta-cognitive confidence modifier, while FEP drives the primary ranking.
    """

    def __init__(self):
        # Temperature parameter for the thermodynamic analogy
        self.temperature = 0.5
        # Weights for the hybrid score
        self.w_struct = 0.6
        self.w_ncd = 0.4

    def _extract_structural_features(self, text: str) -> dict:
        """Extract logical constraints: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|none)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'boolean_yes': 1 if re.search(r'\byes\b', text_lower) else 0,
            'boolean_no': 1 if re.search(r'\bno\b', text_lower) else 0,
        }
        return features

    def _check_logical_consistency(self, prompt_feats: dict, cand_feats: dict) -> float:
        """
        Thermodynamic consistency check (Detailed Balance).
        Returns a penalty (energy) if constraints are violated.
        """
        energy = 0.0
        
        # Negation consistency: If prompt has strong negation, 'yes' is penalized
        if prompt_feats['negations'] > 0:
            if cand_feats['boolean_yes'] > 0:
                energy += 2.0  # High energy penalty
            if cand_feats['boolean_no'] > 0:
                energy -= 0.5  # Slight reward for aligning with negation
        
        # Conditional consistency (simplified): If prompt has conditionals, 
        # candidates lacking logical connectors might be suspect (soft penalty)
        if prompt_feats['conditionals'] > 0:
            if cand_feats['conditionals'] == 0 and cand_feats['negations'] == 0:
                energy += 0.5

        # Number consistency: If numbers exist, check basic ordering if possible
        # (Simplified for this implementation: presence match)
        if prompt_feats['numbers'] and not cand_feats['numbers']:
            # If prompt has numbers but candidate has none, slight penalty unless it's a pure logic word
            if len(cand_feats) < 5: # Heuristic for short non-numeric answers
                pass # Ignore for very short answers
            else:
                energy += 0.3

        return energy

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        denominator = max(len_s1, len_s2)
        if denominator == 0:
            return 1.0
        return (len_combined - min(len_s1, len_s2)) / denominator

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Compute the Free Energy bound approximation.
        Lower energy = higher score.
        Based on structural parsing and constraint propagation.
        """
        p_feats = self._extract_structural_features(prompt)
        c_feats = self._extract_structural_features(candidate)
        
        # 1. Thermodynamic Penalty (Consistency)
        energy_penalty = self._check_logical_consistency(p_feats, c_feats)
        
        # 2. Structural Overlap (Variational Free Energy minimization)
        # Reward matching specific logical tokens
        logic_match = 0
        if p_feats['negations'] > 0 and c_feats['negations'] > 0:
            logic_match += 1.0
        if p_feats['comparatives'] > 0 and c_feats['comparatives'] > 0:
            logic_match += 1.0
        if p_feats['conditionals'] > 0 and c_feats['conditionals'] > 0:
            logic_match += 1.0
            
        # Numeric evaluation heuristic
        numeric_score = 0.0
        if p_feats['numbers'] and c_feats['numbers']:
            # Simple presence bonus, detailed float comparison handled in specific logic if needed
            numeric_score = 0.5
            
        # Base score starts at 1.0, subtract energy, add matches
        # Normalize to roughly 0-1 range
        raw_score = 1.0 - (energy_penalty * 0.2) + (logic_match * 0.3) + numeric_score
        
        # Clamp
        return max(0.0, min(1.0, raw_score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using thermodynamic variational inference analogy.
        Ranks by structural consistency (Free Energy) and NCD tie-breaking.
        """
        scored_candidates = []
        
        for cand in candidates:
            # Primary Signal: Structural/Logical Consistency (FEP)
            struct_score = self._compute_structural_score(prompt, cand)
            
            # Secondary Signal: NCD (Tiebreaker only)
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD so higher is better, scale to small epsilon range for tie-breaking
            ncd_score = (1.0 - ncd_val) * 0.01 
            
            # Combined Score: Structural dominates, NCD breaks ties
            final_score = struct_score + ncd_score
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural alignment: {struct_score:.4f}, NCD tiebreak: {ncd_score:.4f}"
            })
        
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Compute confidence using MaxEnt as a meta-cognitive filter.
        High entropy in logical features relative to prompt constraints reduces confidence.
        """
        p_feats = self._extract_structural_features(prompt)
        a_feats = self._extract_structural_features(answer)
        
        # Calculate a simple 'logical entropy' of the answer
        # If the answer has mixed signals (both yes and no, or high complexity without structure)
        vector = [
            a_feats['boolean_yes'],
            a_feats['boolean_no'],
            a_feats['negations'],
            a_feats['conditionals']
        ]
        
        total = sum(vector) + 1e-9
        probs = [v / total for v in vector if v > 0]
        
        # Shannon Entropy
        entropy = 0.0
        for p in probs:
            if p > 0:
                entropy -= p * math.log2(p)
        
        # Max possible entropy for 4 categories
        max_entropy = math.log2(4) 
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        # Base confidence from structural evaluation
        base_score = self._compute_structural_score(prompt, answer)
        
        # MaxEnt Penalty: 
        # If the prompt is highly constrained (low entropy expected) but answer is high entropy -> lower confidence
        # If the prompt is open, entropy matters less.
        prompt_constraint_level = (p_feats['negations'] + p_feats['conditionals']) / 5.0
        
        # Adjustment factor
        adjustment = normalized_entropy * prompt_constraint_level * 0.4
        
        final_conf = base_score - adjustment
        return max(0.0, min(1.0, final_conf))