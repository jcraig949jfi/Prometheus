import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic-Ecological Reasoning Engine (TERE) Implementation.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values. Candidates are scored by 
       constraint satisfaction (0.0 to 1.0).
    2. Ecological Coupling (Modifier): Candidates sharing structural features 
       (e.g., same numeric magnitude or logical polarity) receive a 'mutualistic' 
       boost, while contradictory ones (explicit negation matches) are penalized.
    3. Thermodynamic Ranking: Final score is a Boltzmann-weighted fitness combining 
       structural likelihood and ecological stability. 
    4. NCD (Tiebreaker): Used only when structural scores are indistinguishable.
    
    This avoids the 'Ecosystem Dynamics' trap by not using population ODEs for 
    direct scoring, but rather as a static interaction term for robustness.
    """

    def __init__(self):
        self.negation_words = {"no", "not", "never", "none", "neither", "false", "incorrect"}
        self.comparatives = {"greater", "less", "more", "fewer", "larger", "smaller", ">", "<"}
        self.conditionals = {"if", "then", "unless", "otherwise", "provided"}

    def _extract_structure(self, text: str) -> dict:
        """Extract logical and numeric features from text."""
        lower_text = text.lower()
        features = {
            "has_negation": any(w in lower_text for w in self.negation_words),
            "has_comparative": any(w in lower_text for w in self.comparatives),
            "has_conditional": any(w in lower_text for w in self.conditionals),
            "numbers": [],
            "length": len(text)
        }
        # Extract numbers
        features["numbers"] = [float(n) for n in re.findall(r"-?\d+\.?\d*", text)]
        return features

    def _check_constraint_satisfaction(self, prompt_feats: dict, cand_feats: dict, candidate: str) -> float:
        """
        Evaluate how well the candidate satisfies implicit structural constraints 
        derived from the prompt.
        """
        score = 0.5  # Base prior
        
        # 1. Numeric Consistency
        if prompt_feats["numbers"] and cand_feats["numbers"]:
            # If prompt has numbers, candidate matching magnitude or logic gets boost
            p_nums = prompt_feats["numbers"]
            c_nums = cand_feats["numbers"]
            
            # Simple heuristic: if prompt implies comparison, check order
            if prompt_feats["has_comparative"]:
                if len(p_nums) >= 2 and len(c_nums) >= 1:
                    # Check if candidate number aligns with comparative direction
                    # This is a simplified proxy for complex logic
                    if p_nums[0] > p_nums[1] and "greater" in str(c_nums).lower() or "larger" in str(c_nums).lower():
                        score += 0.3
                    elif p_nums[0] < p_nums[1] and "less" in str(c_nums).lower() or "smaller" in str(c_nums).lower():
                        score += 0.3
            else:
                # Exact match bonus for simple numeric prompts
                if any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                    score += 0.4
        
        # 2. Negation Alignment
        # If prompt asks a negative question or contains negation, candidate should reflect it
        if prompt_feats["has_negation"]:
            if cand_feats["has_negation"]:
                score += 0.2 # Reinforcement
            else:
                score -= 0.2 # Potential contradiction penalty
        
        # 3. Conditional Logic Presence
        if prompt_feats["has_conditional"]:
            if cand_feats["has_conditional"]:
                score += 0.1
            # Length heuristic: conditional answers often need more tokens
            if cand_feats["length"] > 10:
                score += 0.1

        return min(1.0, max(0.0, score))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        min_len = min(c1, c2)
        if min_len == 0: return 1.0
        return (c12 - min_len) / max(c1, c2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        prompt_feats = self._extract_structure(prompt)
        results = []
        
        # Phase 1: Compute Structural Scores (Microscopic Likelihood)
        raw_scores = []
        for cand in candidates:
            cand_feats = self._extract_structure(cand)
            struct_score = self._check_constraint_satisfaction(prompt_feats, cand_feats, cand)
            raw_scores.append((cand, struct_score, cand_feats))
        
        # Phase 2: Ecological Coupling (Interaction Terms)
        # Calculate 'fitness' based on diversity and agreement with high-scoring candidates
        final_scores = []
        max_struct = max(r[1] for r in raw_scores) if raw_scores else 0.5
        
        for i, (cand, struct_score, feats) in enumerate(raw_scores):
            ecological_bonus = 0.0
            
            # Mutualism: Boost if similar structural profile to top candidates
            # Inhibition: Penalty if contradictory to high-probability structural norms
            for j, (other_cand, other_score, other_feats) in enumerate(raw_scores):
                if i == j: continue
                if other_score > 0.7: # Interact with strong candidates
                    # Simple synergy: same negation status
                    if feats["has_negation"] == other_feats["has_negation"]:
                        ecological_bonus += 0.02
                    else:
                        ecological_bonus -= 0.03 # Competition
            
            # Thermodynamic Fitness: Boltzmann-like weighting
            # F = Structural_Likelihood + Ecological_Interaction
            fitness = struct_score + ecological_bonus
            
            # Apply Emergence Modifier: 
            # If the system is uncertain (max_struct < 0.6), boost diversity (length variance)
            if max_struct < 0.6:
                if abs(len(cand) - sum(len(c[0]) for c in raw_scores)/len(raw_scores)) > 5:
                    fitness += 0.05 # Reward outlier in low-confidence regime

            final_scores.append((cand, fitness))
        
        # Phase 3: Ranking with NCD Tiebreaker
        # Sort primarily by fitness, use NCD for ties or very close calls
        def sort_key(item):
            cand, score = item
            # NCD to prompt: Lower distance (more similar structure) is better for ties
            ncd_val = self._compute_ncd(prompt, cand)
            return (-score, ncd_val) 
        
        sorted_results = sorted(final_scores, key=sort_key)
        
        output = []
        for cand, score in sorted_results:
            # Normalize score to 0-1 range roughly
            norm_score = min(1.0, max(0.0, score))
            output.append({
                "candidate": cand,
                "score": round(norm_score, 4),
                "reasoning": f"Structural fit: {norm_score:.2f}, Ecological stability applied."
            })
            
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and compression stability.
        """
        p_feats = self._extract_structure(prompt)
        a_feats = self._extract_structure(answer)
        
        # Base confidence from structural match
        conf = 0.5
        
        # Numeric alignment
        if p_feats["numbers"] and a_feats["numbers"]:
            if any(abs(p - a) < 1e-6 for p in p_feats["numbers"] for a in a_feats["numbers"]):
                conf += 0.3
        
        # Logical consistency (Negation)
        if p_feats["has_negation"] == a_feats["has_negation"]:
            conf += 0.1
            
        # Conditional presence
        if p_feats["has_conditional"] and a_feats["has_conditional"]:
            conf += 0.1
            
        # Penalty for length mismatch in complex prompts
        if p_feats["has_conditional"] and len(a_feats["numbers"]) == 0 and len(answer.split()) < 5:
            conf -= 0.2
            
        return min(1.0, max(0.0, conf))