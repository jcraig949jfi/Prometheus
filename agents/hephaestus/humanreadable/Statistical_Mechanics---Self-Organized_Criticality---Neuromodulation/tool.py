import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuromodulated Critical Boltzmann Machine (NCBM) Approximation.
    
    Mechanism:
    1. Structural Parsing (The Lattice): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a rigid energy landscape. This replaces 
       the Boltzmann weights with deterministic logical scores.
    2. SOC Avalanche Layer (The Dynamics): Instead of random walks, we simulate 
       "activity charge" accumulation on candidate tokens. If a candidate violates 
       a hard logical constraint (e.g., negation mismatch), it triggers an "avalanche" 
       (large penalty). If it satisfies complex structural patterns, it gains charge.
       This mimics the power-law distribution of updates: small tweaks for syntax, 
       large jumps for logical consistency.
    3. Neuromodulation (The Gain): A global gain factor scales the penalty/reward 
       based on the "prediction error" (disagreement between simple NCD similarity 
       and structural score). High error -> High Gain (exploration/strictness); 
       Low error -> Low Gain (exploitation/smoothing).
       
    This approach prioritizes structural reasoning (high accuracy) while using 
    SOC-inspired dynamics to handle edge cases and NCD as a tiebreaker.
    """

    def __init__(self):
        # SOC Parameters
        self.threshold = 1.0  # Avalanche trigger threshold
        self.dissipation = 0.1  # Charge lost per step
        self.neuromod_gain = 1.0  # Global scaling factor
        
        # Structural patterns
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'unless', 'provided', 'when', 'while']

    def _structural_parse(self, text: str) -> Dict[str, float]:
        """Extract logical features from text."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        score = 0.0
        has_negation = any(n in words for n in self.negations)
        has_comparative = any(c in words for c in self.comparatives)
        has_conditional = any(c in words for c in self.conditionals)
        
        # Basic counting heuristics
        nums = re.findall(r'\d+\.?\d*', text)
        numeric_density = len(nums) / (len(words) + 1)
        
        return {
            'negation': 1.0 if has_negation else 0.0,
            'comparative': 1.0 if has_comparative else 0.0,
            'conditional': 1.0 if has_conditional else 0.0,
            'numeric_density': numeric_density,
            'length': len(words)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _simulate_avalanche(self, prompt_feats: Dict, cand_feats: Dict, base_score: float) -> float:
        """
        Simulate SOC dynamics. 
        Accumulate 'charge' based on feature alignment. 
        If misalignment exceeds threshold, trigger avalanche (large penalty).
        """
        charge = 0.0
        
        # Rule 1: Negation Consistency (Critical Constraint)
        # If prompt has negation, candidate must reflect it (simplified heuristic)
        neg_diff = abs(prompt_feats['negation'] - cand_feats['negation'])
        charge += neg_diff * 2.0
        
        # Rule 2: Comparative/Conditional presence
        # Reward candidates that match the complexity type of the prompt
        comp_match = 1.0 if (prompt_feats['comparative'] > 0) == (cand_feats['comparative'] > 0) else 0.0
        charge -= comp_match * 0.5  # Reduce charge (good)
        
        # Rule 3: Numeric density alignment
        num_diff = abs(prompt_feats['numeric_density'] - cand_feats['numeric_density'])
        charge += num_diff * 1.5

        # SOC Toppling Rule
        if charge > self.threshold:
            # Avalanche: Large reorganization (penalty for logical inconsistency)
            # The magnitude follows a power-law-like penalty scaled by neuromodulation
            penalty = (charge ** 2) * self.neuromod_gain
            return base_score - penalty
        else:
            # Small relaxation
            return base_score - (charge * 0.1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._structural_parse(prompt)
        results = []
        
        # Phase 1: Initial Scoring based on structural alignment and NCD
        base_scores = []
        for cand in candidates:
            cand_feats = self._structural_parse(cand)
            
            # Heuristic 1: Structural Compatibility
            struct_score = 0.5
            if prompt_feats['negation'] == cand_feats['negation']:
                struct_score += 0.2
            if prompt_feats['comparative'] == cand_feats['comparative']:
                struct_score += 0.1
            
            # Heuristic 2: NCD Similarity (as a baseline prior)
            ncd = self._compute_ncd(prompt, cand)
            # Invert NCD (0 is identical, 1 is different) -> similarity
            ncd_sim = 1.0 - ncd
            
            base_score = (struct_score * 0.6) + (ncd_sim * 0.4)
            base_scores.append((cand, base_score, cand_feats))
        
        # Phase 2: Neuromodulated SOC Adjustment
        # Calculate global "prediction error" (variance in base scores)
        if len(base_scores) > 1:
            scores_np = np.array([b[1] for b in base_scores])
            error_signal = np.std(scores_np) 
            # Neuromodulation: High variance -> High Gain (strict filtering)
            # Low variance -> Low Gain (fine discrimination)
            self.neuromod_gain = 1.0 + (error_signal * 2.0)
        else:
            self.neuromod_gain = 1.0

        for cand, base_score, cand_feats in base_scores:
            final_score = self._simulate_avalanche(prompt_feats, cand_feats, base_score)
            # Normalize to 0-1 range roughly
            final_score = max(0.0, min(1.0, final_score))
            
            reasoning = f"Structural match: {1.0 - abs(prompt_feats['negation'] - cand_feats['negation']):.2f}. "
            reasoning += f"SOC adjustment applied with gain {self.neuromod_gain:.2f}."
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on structural consistency and SOC stability.
        Returns 0-1.
        """
        prompt_feats = self._structural_parse(prompt)
        ans_feats = self._structural_parse(answer)
        
        # 1. Structural Consistency Check
        consistency = 1.0
        if prompt_feats['negation'] != ans_feats['negation']:
            # Major logical conflict
            consistency -= 0.5
        if prompt_feats['numeric_density'] > 0.1 and ans_feats['numeric_density'] == 0:
            # Missing numbers when expected
            consistency -= 0.3
            
        # 2. SOC Stability Check (Simulated)
        # If the answer triggers an avalanche (high charge), confidence drops
        charge = abs(prompt_feats['negation'] - ans_feats['negation']) * 2.0
        charge += abs(prompt_feats['numeric_density'] - ans_feats['numeric_density']) * 1.5
        
        if charge > self.threshold:
            # Avalanche occurred: Low confidence
            soc_factor = 0.2
        else:
            soc_factor = 0.8
            
        base_ncd = 1.0 - self._compute_ncd(prompt, answer)
        
        # Weighted combination
        conf = (consistency * 0.4) + (soc_factor * 0.4) + (base_ncd * 0.2)
        return max(0.0, min(1.0, conf))