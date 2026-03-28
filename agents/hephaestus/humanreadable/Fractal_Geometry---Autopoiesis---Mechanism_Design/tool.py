import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal Autopoietic Mechanism-Design Engine (FAMDE) Implementation.
    
    Mechanism:
    1. Fractal Geometry + Mechanism Design (Synergistic Core): 
       The system parses the prompt into a structural vector (negations, comparatives, 
       conditionals, numerics). This vector acts as the "Iterated Function System" (IFS) 
       seed. We apply a recursive scaling factor to the structural features, simulating 
       self-similar policy modules at different resolutions. Mechanism design principles 
       are embedded by assigning higher "rewards" (scores) to candidates that preserve 
       structural invariants (e.g., if prompt has "not", candidate must reflect negation).
       
    2. Autopoiesis (Restricted Role):
       Per causal analysis, autopoiesis is restricted to the confidence() wrapper.
       It validates the internal consistency of the answer against the prompt's 
       logical closure without altering the primary scoring logic.
       
    3. Scoring:
       Primary signal: Structural alignment (logic, numbers, constraints).
       Secondary signal: NCD (tiebreaker only).
    """

    def __init__(self):
        self.structural_weight = 0.85
        self.ncd_weight = 0.15

    def _extract_structure(self, text: str) -> Dict[str, float]:
        """Extract structural features: negations, comparatives, conditionals, numerics."""
        text_lower = text.lower()
        features = {
            "negation": 0.0,
            "comparative": 0.0,
            "conditional": 0.0,
            "numeric": 0.0,
            "length": len(text)
        }
        
        # Negations
        negations = ["not", "no ", "never", "without", "unless", "neither"]
        features["negation"] = sum(1 for n in negations if n in text_lower)
        
        # Comparatives
        comparatives = ["more", "less", "greater", "smaller", "better", "worse", ">", "<", "vs"]
        features["comparative"] = sum(1 for c in comparatives if c in text_lower)
        
        # Conditionals
        conditionals = ["if", "then", "else", "unless", "provided", "when"]
        features["conditional"] = sum(1 for c in conditionals if c in text_lower)
        
        # Numerics (simple detection)
        nums = re.findall(r"[-+]?\d*\.?\d+", text)
        features["numeric"] = len(nums)
        
        return features

    def _fractal_scale(self, base_features: Dict[str, float], depth: int = 2) -> Dict[str, float]:
        """
        Simulate fractal scaling of features.
        Applies self-similar transformation to structural weights based on depth.
        """
        scaled = {}
        scale_factor = 0.5  # Fractal dimension proxy
        for key, val in base_features.items():
            if key == "length":
                scaled[key] = val
                continue
            # Recursive accumulation simulating self-similar policy modules
            accumulation = val
            current_val = val
            for d in range(depth):
                current_val *= scale_factor
                accumulation += current_val
            scaled[key] = accumulation
        return scaled

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _check_logical_consistency(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> float:
        """
        Mechanism Design: Reward truthful reporting of structural properties.
        If prompt has high negation, candidate should likely reflect it (simplified heuristic).
        """
        score = 0.0
        
        # Numeric consistency check
        if prompt_feats["numeric"] > 0 and cand_feats["numeric"] > 0:
            # Extract numbers to check for gross contradictions (simple version)
            p_nums = re.findall(r"[-+]?\d*\.?\d+", prompt.lower())
            c_nums = re.findall(r"[-+]?\d*\.?\d+", candidate.lower())
            if p_nums and c_nums:
                # Reward if numbers are present in both (basic presence check)
                score += 0.2
        
        # Negation consistency (simplified)
        if prompt_feats["negation"] > 0:
            if cand_feats["negation"] > 0:
                score += 0.2
            # Note: In complex logic, absence might be correct, but presence is safer for "reasoning"
            
        # Conditional presence
        if prompt_feats["conditional"] > 0 and cand_feats["conditional"] > 0:
            score += 0.1
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_structure(prompt)
        # Apply fractal scaling to prompt features to generate the "incentive architecture"
        fractal_prompt_feats = self._fractal_scale(prompt_feats)
        
        results = []
        
        for cand in candidates:
            cand_feats = self._extract_structure(cand)
            
            # 1. Structural Alignment Score (Primary)
            # Compare scaled prompt features with candidate features
            struct_match = 0.0
            count = 0
            for key in ["negation", "comparative", "conditional", "numeric"]:
                # Normalize by prompt intensity to avoid bias
                p_val = fractal_prompt_feats.get(key, 0)
                c_val = cand_feats.get(key, 0)
                
                if p_val > 0:
                    # Reward proportional presence
                    match_ratio = min(c_val, p_val) / max(p_val, 1)
                    struct_match += match_ratio
                elif c_val == 0:
                    # True negative
                    struct_match += 1.0
                count += 1
            
            struct_score = (struct_match / max(count, 1)) if count > 0 else 0
            
            # Add logical consistency bonus (Mechanism Design)
            logic_bonus = self._check_logical_consistency(prompt_feats, cand_feats, prompt, cand)
            
            final_struct_score = min(1.0, struct_score * 0.8 + logic_bonus * 0.2)

            # 2. NCD Score (Tiebreaker/Secondary)
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD so higher is better, but keep it low weight
            ncd_score = (1.0 - ncd_val) * 0.3 

            # Combined Score
            total_score = (final_struct_score * self.structural_weight) + (ncd_score * self.ncd_weight)
            
            results.append({
                "candidate": cand,
                "score": round(total_score, 6),
                "reasoning": f"Structural alignment: {final_struct_score:.3f}, NCD synergy: {ncd_score:.3f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Autopoietic closure check.
        Validates if the answer maintains the structural integrity of the prompt.
        Returns 0-1 confidence.
        """
        p_feats = self._extract_structure(prompt)
        a_feats = self._extract_structure(answer)
        
        # Self-production check: Does the answer reproduce the necessary logical operators?
        consistency = 0.5 # Base confidence
        
        # Check negation preservation
        if p_feats["negation"] > 0:
            if a_feats["negation"] > 0:
                consistency += 0.3
            else:
                consistency -= 0.2
        
        # Check numeric presence
        if p_feats["numeric"] > 0:
            if a_feats["numeric"] > 0:
                consistency += 0.2
        
        # Check length plausibility (autopoietic size constraint)
        if len(answer) < 0.1 * len(prompt) and len(prompt) > 20:
            consistency -= 0.3 # Too short to be self-sustaining
            
        return max(0.0, min(1.0, consistency))