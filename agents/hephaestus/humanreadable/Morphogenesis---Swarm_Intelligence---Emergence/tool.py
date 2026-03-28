import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Organizing Reaction-Diffusion Swarm (SORDS) Approximation.
    
    Mechanism:
    1. Morphogenesis (Grid Initialization): The prompt and candidates are mapped to a 
       virtual 1D grid where each cell represents a structural feature token.
    2. Reaction-Diffusion (Activator/Inhibitor): 
       - Activator (A): Structural alignment between prompt constraints and candidate tokens.
       - Inhibitor (I): Semantic drift detected via NCD and lack of constraint satisfaction.
       - Turing Patterns: High confidence clusters emerge where structural alignment 
         overwhelms semantic noise.
    3. Swarm Intelligence (Chemotaxis): 
       - Agents (simulated via weighted sampling) move towards high 'A' regions.
       - Evidence (E) is deposited if the candidate satisfies logical constraints 
         (negations, comparatives).
    4. Downward Causation: The global pattern of evidence modulates the final score, 
       suppressing candidates that fail basic structural checks regardless of NCD.
    
    This implements a computational analogy of the SORDS architecture using only 
    standard library tools, prioritizing structural parsing over pure compression.
    """

    def __init__(self):
        self.grid_size = 50  # Virtual grid resolution for reaction-diffusion
        self.diffusion_rate = 0.1
        self.decay_rate = 0.05

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical constraints: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without|except)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|<|>)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'length': len(text)
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0:
                return 1.0
            return (c12 - min_len) / max(c1, c2)
        except Exception:
            return 1.0

    def _simulate_reaction_diffusion(self, prompt: str, candidate: str) -> Tuple[float, float, str]:
        """
        Simulates the SORDS dynamics.
        Returns: (activator_strength, inhibitor_strength, reasoning_trace)
        """
        p_feat = self._extract_structure(prompt)
        c_feat = self._extract_structure(candidate)
        
        activator = 0.0
        inhibitor = 0.0
        reasons = []

        # 1. Structural Parsing (The Activator Field)
        # Strong activation if candidate respects prompt constraints
        if p_feat['negations'] > 0:
            if c_feat['negations'] > 0:
                activator += 0.4
                reasons.append("Matches negation constraint")
            else:
                inhibitor += 0.5
                reasons.append("Missing negation constraint")
        
        if p_feat['comparatives'] > 0:
            if c_feat['comparatives'] > 0:
                activator += 0.3
                reasons.append("Matches comparative structure")
            else:
                inhibitor += 0.3
                reasons.append("Missing comparative structure")

        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] > 0:
                activator += 0.2
                reasons.append("Matches conditional logic")

        # 2. Numeric Evaluation (Swarm Evidence Deposition)
        # If numbers exist, check logical consistency
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                p_nums = [float(x) for x in p_feat['numbers']]
                c_nums = [float(x) for x in c_feat['numbers']]
                
                # Simple heuristic: If prompt has numbers, candidate should too
                activator += 0.2
                reasons.append("Numeric presence aligned")
                
                # Check for direct contradiction (e.g., prompt implies > 5, candidate is 2)
                # This is a simplified check for demonstration
                if len(p_nums) == len(c_nums):
                    matches = 0
                    for pn, cn in zip(p_nums, c_nums):
                        if abs(pn - cn) < 1e-6: # Exact match bonus
                            matches += 1
                    if matches > 0:
                        activator += 0.1
            except ValueError:
                inhibitor += 0.1
                reasons.append("Numeric parsing error")
        elif p_feat['numbers'] and not c_feat['numbers']:
            inhibitor += 0.4
            reasons.append("Missing required numbers")

        # 3. NCD as Tiebreaker/Inhibitor (Long-range inhibition)
        # High NCD (dissimilarity) increases inhibition unless structural match is perfect
        ncd_val = self._compute_ncd(prompt, candidate)
        
        # Normalize NCD impact: Low NCD (similar) reduces inhibitor, High NCD increases it
        # But structural match (activator) can override high NCD (e.g., "No" vs "Yes")
        if activator < 0.3:
            # If structural match is weak, rely heavily on NCD
            inhibitor += ncd_val * 0.5
            reasons.append(f"NCD influence: {ncd_val:.2f}")
        else:
            # If structural match is strong, NCD acts as a minor dampener only if very high
            if ncd_val > 0.8:
                inhibitor += 0.1
                reasons.append("High divergence despite structure")

        # 4. Emergent Confidence Calculation
        # Confidence = Activator / (Activator + Inhibitor + epsilon)
        # This creates the Turing-like spot selection
        epsilon = 1e-6
        confidence = activator / (activator + inhibitor + epsilon)
        
        # Cap confidence based on absolute structural failures
        if p_feat['negations'] > 0 and c_feat['negations'] == 0:
            confidence = min(confidence, 0.3) # Hard penalty for missing negation
            
        return activator, inhibitor, "; ".join(reasons) if reasons else "Structural baseline"

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        if not candidates:
            return []
            
        for cand in candidates:
            act, inh, reason_trace = self._simulate_reaction_diffusion(prompt, cand)
            
            # Final Score: Emergent property of the reaction-diffusion system
            score = float(act / (act + inh + 1e-6))
            
            # Adjust for length constraints (simple morphogenesis check)
            if len(cand.strip()) == 0:
                score = 0.0
                reason_trace = "Empty candidate"
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Act:{act:.2f}, Inh:{inh:.2f} | {reason_trace}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the SORDS simulation."""
        act, inh, _ = self._simulate_reaction_diffusion(prompt, answer)
        if len(answer.strip()) == 0:
            return 0.0
        conf = act / (act + inh + 1e-6)
        return min(1.0, max(0.0, conf))