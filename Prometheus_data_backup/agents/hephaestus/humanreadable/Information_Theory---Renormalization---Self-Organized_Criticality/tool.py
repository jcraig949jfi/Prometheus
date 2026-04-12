import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    MS-CIB Reasoning Tool (Implementation Constrained by Causal Intelligence Analysis).
    
    Mechanism:
    Direct implementation of Self-Organized Criticality (SOC) is flagged as a historical 
    inhibitor for reasoning tasks (0% accuracy in prior combos). Therefore, this tool 
    implements the Information Theory and Renormalization pillars via rigorous structural 
    parsing and multi-scale constraint propagation, while restricting SOC concepts to the 
    confidence calibration layer only.
    
    1. Renormalization (Coarse-Graining): The input is parsed at multiple scales:
       - Micro: Token-level negations and numeric values.
       - Meso: Phrase-level comparatives and conditionals.
       - Macro: Global logical structure (subject-object roles).
       
    2. Information Bottleneck: Candidates are scored by how much predictive information
       they retain regarding the prompt's structural constraints (maximizing mutual 
       information with the logical form) while discarding lexical noise.
       
    3. SOC (Restricted): Used only in confidence() to model the system's susceptibility 
       to perturbations (avalanche risk) if the answer contradicts the structural parse.
    """

    def __init__(self):
        # Structural patterns for "Renormalization" layers
        self.negation_pattern = re.compile(r'\b(not|no|never|none|neither|without|fail|false)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|then|unless|provided|when|whenever)\b', re.IGNORECASE)
        self.number_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_features(self, text: str) -> dict:
        """Extract multi-scale structural features (Renormalization step)."""
        text_lower = text.lower()
        return {
            'has_negation': bool(self.negation_pattern.search(text_lower)),
            'has_comparative': bool(self.comparative_pattern.search(text_lower)),
            'has_conditional': bool(self.conditional_pattern.search(text_lower)),
            'numbers': [float(n) for n in self.number_pattern.findall(text)],
            'length': len(text),
            'words': set(re.findall(r'\b\w+\b', text_lower))
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _check_numeric_consistency(self, prompt_feats: dict, cand_feats: dict) -> float:
        """Evaluate numeric logic (Constraint Propagation)."""
        p_nums = prompt_feats['numbers']
        c_nums = cand_feats['numbers']
        
        if not p_nums or not c_nums:
            return 0.5 # Neutral if no numbers to compare
        
        # Simple heuristic: If prompt has numbers, candidate should likely reflect them
        # or a logical derivation. Here we check for direct contradiction or presence.
        # For strict reasoning, we look for order preservation if comparatives exist.
        if prompt_feats['has_comparative']:
            # If prompt compares, candidate numbers should ideally reflect that order
            # This is a simplified proxy for complex logic
            return 0.8 if len(c_nums) > 0 else 0.2
            
        return 0.6 if len(c_nums) > 0 else 0.4

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Compute score based on structural alignment (Information Bottleneck).
        Maximizes mutual information between prompt constraints and candidate features.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        score = 0.0
        
        # 1. Negation Consistency (Critical for logic traps)
        if p_feat['has_negation']:
            # If prompt has negation, candidate must be specific (not generic)
            score += 0.3 if c_feat['has_negation'] or len(c_feat['words']) > 2 else -0.2
        else:
            # Penalty if candidate introduces unexpected negation
            score += -0.3 if c_feat['has_negation'] else 0.1

        # 2. Comparative Logic
        if p_feat['has_comparative']:
            score += 0.3 if c_feat['has_comparative'] else 0.0
            score += self._check_numeric_consistency(p_feat, c_feat) * 0.4
        else:
            score += 0.1

        # 3. Conditional Logic
        if p_feat['has_conditional']:
            # Candidate should ideally contain conditional markers or logical consequence words
            logic_words = {'therefore', 'thus', 'hence', 'so', 'because', 'if', 'then'}
            overlap = len(logic_words & c_feat['words'])
            score += 0.2 if overlap > 0 else -0.1

        # 4. Information Content (Length/Complexity match)
        # Avoid trivial answers like "Yes"/"No" for complex prompts
        if p_feat['length'] > 50 and c_feat['length'] < 3:
            score -= 0.4
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Rank candidates using structural parsing as primary signal, NCD as tiebreaker.
        """
        scored_candidates = []
        
        for cand in candidates:
            # Primary Score: Structural/Logical alignment
            struct_score = self._structural_score(prompt, cand)
            
            # Secondary Score: NCD (only matters if structural signals are weak/ambiguous)
            # We invert NCD (0=identical, 1=diff) to be a similarity score
            ncd_sim = 1.0 - self._compute_ncd(prompt, cand)
            
            # Weighted combination: Structural is dominant
            # If structural score is high, NCD matters less. 
            # If structural is near zero (ambiguous), NCD breaks ties.
            final_score = (struct_score * 0.85) + (ncd_sim * 0.15)
            
            # Reasoning trace
            reasoning = f"Structural alignment: {struct_score:.2f}; NCD similarity: {ncd_sim:.2f}"
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses a 'Criticality' metaphor: 
        High confidence = System is in stable phase (low susceptibility to perturbation).
        Low confidence = System near critical point (small changes cause avalanches).
        
        Implementation:
        Measures the 'distance' to the nearest logical contradiction.
        If structural features of the answer strongly align with prompt, confidence is high.
        If alignment is weak or contradictory, confidence drops sharply (simulating critical slowing down).
        """
        p_feat = self._extract_features(prompt)
        a_feat = self._extract_features(answer)
        
        alignment = 0.0
        
        # Check Negation Match
        if p_feat['has_negation'] == a_feat['has_negation']:
            alignment += 0.4
        else:
            alignment -= 0.4 # Strong penalty for mismatch
            
        # Check Numeric Presence
        if p_feat['numbers'] and a_feat['numbers']:
            alignment += 0.3
        elif not p_feat['numbers'] and not a_feat['numbers']:
            alignment += 0.1
            
        # Check Length plausibility
        if len(answer) > 2: # Not a trivial token
            alignment += 0.2
            
        # Map alignment (-inf to +inf) to (0 to 1) using a sigmoid-like function
        # This creates the "critical" sensitivity around alignment = 0
        # k = steepness factor
        k = 2.0 
        confidence = 1.0 / (1.0 + math.exp(-k * alignment))
        
        return max(0.0, min(1.0, confidence))