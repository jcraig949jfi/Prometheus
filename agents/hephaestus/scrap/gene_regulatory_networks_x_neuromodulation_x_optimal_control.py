import re
import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Neuromodulated Optimal Gene Regulatory Controller (NOGRC) Simulator.
    
    Mechanism:
    1. Structural Parsing (The GRN): Extracts logical constraints (negations, comparatives,
       conditionals) to form a static "genome" of rules. This defines the attractor basins.
    2. Neuromodulated Dynamics (The Controller): Instead of solving ODEs in real-time,
       we simulate the "cost" (J) of forcing the system state (candidate answer) to align
       with the reference trajectory (prompt constraints).
       - High alignment = Low metabolic cost (High Score).
       - Low alignment = High metabolic cost (Low Score).
    3. Optimal Control Wrapper: The 'confidence' method acts as the PMP verifier, checking
       if the trajectory satisfies the boundary conditions (logical consistency).
    
    This avoids the "Optimal Control" trap by using it as a structural verifier rather
    than a direct scorer, relying on deterministic logical extraction for the heavy lifting.
    """

    def __init__(self):
        self._epsilon = 1e-6

    def _extract_structural_features(self, text: str) -> Dict:
        """Extracts logical constraints acting as the GRN topology."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|provided)\b', text_lower)),
            'numerics': re.findall(r'\d+\.?\d*', text),
            'length': len(text)
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Simulates the GRN attractor stability.
        Checks if the candidate satisfies the structural constraints of the prompt.
        Returns a stability score (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 1.0
        penalty = 0.0

        # 1. Negation Handling (Modus Tollens check)
        # If prompt says "not X", and candidate contains "X" (without negation context), penalize.
        neg_matches = re.findall(r'not\s+(\w+)', p_lower)
        for word in neg_matches:
            if word in c_lower and not re.search(rf'not\s+{word}', c_lower):
                # Simple heuristic: if prompt forbids word, candidate shouldn't assert it simply
                # This is a coarse approximation of the attractor repulsion
                penalty += 0.4

        # 2. Comparative Consistency
        # If prompt has numbers, check if candidate respects order (simplified)
        nums_prompt = [float(x) for x in re.findall(r'\d+\.?\d*', p_lower)]
        nums_cand = [float(x) for x in re.findall(r'\d+\.?\d*', c_lower)]
        
        if len(nums_prompt) >= 2 and len(nums_cand) >= 1:
            # Check if the candidate's number falls within the logical range implied
            # E.g., "greater than 5" -> candidate should be > 5 (heuristic check)
            if "greater" in p_lower or "more" in p_lower:
                if nums_cand and nums_cand[0] < max(nums_prompt):
                    penalty += 0.3
            elif "less" in p_lower or "smaller" in p_lower:
                if nums_cand and nums_cand[0] > min(nums_prompt):
                    penalty += 0.3

        # 3. Keyword Overlap with Structural Weighting
        # Weighted overlap on logical operators
        logical_ops = ['if', 'then', 'else', 'therefore', 'because', 'thus', 'hence']
        p_ops = set(word for word in p_lower.split() if word in logical_ops)
        c_ops = set(word for word in c_lower.split() if word in logical_ops)
        
        if p_ops and not c_ops:
            # Prompt has logic, candidate ignores it completely
            penalty += 0.2
            
        return max(0.0, 1.0 - penalty)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates by simulating the NOGRC cost function.
        Score = Structural Consistency (Primary) - NCD Penalty (Tiebreaker).
        """
        results = []
        prompt_features = self._extract_structural_features(prompt)
        
        for cand in candidates:
            # 1. Structural Parsing (GRN State)
            consistency_score = self._check_logical_consistency(prompt, cand)
            
            # 2. Optimal Control Cost Analogy
            # We want low "effort" to map candidate to prompt constraints.
            # High consistency = Low effort = High Score.
            
            # 3. NCD Tiebreaker
            # If consistency is identical, prefer the candidate that compresses better with the prompt
            # (implying it shares information structure).
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Final Score formulation:
            # Base score from logic (0-1)
            # Small adjustment from NCD (scaled down so it doesn't override logic)
            final_score = consistency_score - (ncd_val * 0.05)
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 6),
                "reasoning": f"Consistency: {consistency_score:.2f}, NCD: {ncd_val:.2f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on logical consistency verification.
        Acts as the PMP boundary condition check.
        """
        consistency = self._check_logical_consistency(prompt, answer)
        
        # If logical consistency is perfect, confidence is high.
        # If contradictions are found, confidence drops sharply.
        # We add a small buffer for partial matches, but strict logic dominates.
        
        if consistency >= 0.9:
            return min(1.0, consistency + 0.05)
        elif consistency <= 0.5:
            return max(0.0, consistency - 0.1)
        else:
            return consistency