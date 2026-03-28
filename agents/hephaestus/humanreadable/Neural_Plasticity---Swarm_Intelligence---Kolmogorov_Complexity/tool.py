import zlib
import re
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Plastic Swarm MDL Learner (PSML) Approximation.
    
    Mechanism:
    1. Neural Plasticity (Local Update): Agents (hypotheses) adapt to local data features
       by adjusting weights based on structural matches (negations, comparatives) in the prompt.
    2. Swarm Intelligence (Global Search): Candidates move in a conceptual weight-space.
       Their position is determined by the overlap of structural features with the prompt.
       They are attracted to regions of high 'pheromone' density (structural consistency).
    3. Kolmogorov Complexity (MDL): The fitness function penalizes description length.
       Score = (Structural Consistency) - (Complexity Penalty).
       
    This implementation approximates the swarm dynamics via feature-vector similarity
    and uses zlib compression length as the MDL proxy for complexity.
    """

    def __init__(self):
        # Structural patterns for "Plasticity" - detecting logical forms
        self.negation_words = {'no', 'not', 'never', 'none', 'nobody', 'nothing', 'neither', 'nor'}
        self.comparative_ops = ['>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided']
        self.numeric_pattern = re.compile(r"-?\d+\.?\d*")

    def _get_structural_signature(self, text: str) -> Tuple[set, set, set, List[float]]:
        """Extract logical features: negations, comparatives, conditionals, numbers."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        negations = words.intersection(self.negation_words)
        comparatives = {c for c in self.comparative_ops if c in lower_text}
        conditionals = {c for c in self.conditionals if c in lower_text}
        
        numbers = []
        for match in self.numeric_pattern.findall(text):
            try:
                numbers.append(float(match))
            except ValueError:
                pass
                
        return negations, comparatives, conditionals, numbers

    def _compute_complexity(self, text: str) -> float:
        """Approximate Kolmogorov complexity via zlib compression length."""
        if not text:
            return 0.0
        return len(zlib.compress(text.encode('utf-8')))

    def _structural_similarity(self, sig1: Tuple, sig2: Tuple) -> float:
        """
        Calculate similarity between two structural signatures.
        Mimics swarm attraction based on feature overlap.
        """
        n1, c1, cond1, num1 = sig1
        n2, c2, cond2, num2 = sig2
        
        score = 0.0
        total_features = 0
        
        # Negation match (Critical for reasoning)
        if n1 or n2:
            total_features += 1
            if n1 == n2:
                score += 1.0
            elif not n1 and not n2:
                score += 0.5 # Both lack negation is weak positive
        
        # Comparative match
        if c1 or c2:
            total_features += 1
            if c1 == c2:
                score += 1.0
        
        # Conditional match
        if cond1 or cond2:
            total_features += 1
            if cond1 == cond2:
                score += 1.0

        # Numeric consistency (Order preservation)
        if num1 and num2:
            total_features += 1
            # Check if relative order is preserved (simple transitivity check)
            if len(num1) >= 2 and len(num2) >= 2:
                order1 = num1[0] < num1[1]
                order2 = num2[0] < num2[1]
                if order1 == order2:
                    score += 1.0
            elif len(num1) == len(num2):
                 score += 0.5 # Same count is weakly positive
        
        if total_features == 0:
            return 0.5 # Neutral if no structural features found
            
        return score / max(1.0, total_features)

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_sig = self._get_structural_signature(prompt)
        prompt_complexity = self._compute_complexity(prompt)
        
        scored_candidates = []
        
        # Pre-calculate prompt-candidate NCD for tie-breaking
        # We invert NCD so higher is better (1.0 - NCD)
        candidate_data = []
        for cand in candidates:
            cand_sig = self._get_structural_signature(cand)
            cand_complexity = self._compute_complexity(cand)
            
            # 1. Swarm Attraction (Structural Consistency)
            # How well does the candidate's logic fit the prompt's logic?
            swarm_score = self._structural_similarity(prompt_sig, cand_sig)
            
            # 2. MDL Penalty (Complexity Regularization)
            # Prefer simpler explanations unless complexity is warranted by the prompt
            # Normalize complexity relative to prompt length to avoid penalizing long answers unfairly
            # if the prompt itself is complex.
            complexity_ratio = cand_complexity / max(1.0, prompt_complexity)
            
            # Heuristic: If prompt is complex, allow complex answers. 
            # If prompt is simple, penalize complex answers heavily.
            mdl_penalty = 0.0
            if prompt_complexity < 50 and cand_complexity > 100:
                mdl_penalty = 0.3 # Heavy penalty for over-complexity on simple prompts
            elif complexity_ratio > 2.0:
                mdl_penalty = 0.2 # Penalty if answer is 2x more complex than prompt
            
            # Base score combines swarm attraction and MDL penalty
            base_score = swarm_score - mdl_penalty
            
            # 3. NCD Tiebreaker / Baseline correction
            # NCD is often noisy for short strings, so it's a secondary signal here
            ncd_val = self._calculate_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Invert so higher is better
            
            # Final Score: Weighted sum favoring structural reasoning
            # Structural match (70%) + NCD (30%) - MDL Penalty
            final_score = (base_score * 0.7) + (ncd_score * 0.3)
            
            # Reasoning string generation
            reasoning_parts = []
            if swarm_score > 0.8:
                reasoning_parts.append("High structural alignment")
            elif swarm_score < 0.3:
                reasoning_parts.append("Low structural alignment")
            if mdl_penalty > 0:
                reasoning_parts.append("Penalized for complexity")
            if not reasoning_parts:
                reasoning_parts.append("Moderate fit")
                
            reasoning_str = "; ".join(reasoning_parts)
            
            candidate_data.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning_str,
                "swarm_score": swarm_score,
                "mdl_penalty": mdl_penalty
            })

        # Sort by score descending
        candidate_data.sort(key=lambda x: x["score"], reverse=True)
        
        # Format output
        result = []
        for item in candidate_data:
            result.append({
                "candidate": item["candidate"],
                "score": item["score"],
                "reasoning": item["reasoning"]
            })
            
        return result

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same scoring logic as evaluate but normalized.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
            
        raw_score = results[0]["score"]
        
        # Map raw score (approx -0.2 to 1.0) to 0.0 - 1.0
        # Assuming max theoretical score ~1.0 and min ~ -0.5
        confidence = (raw_score + 0.5) / 1.5
        return max(0.0, min(1.0, confidence))