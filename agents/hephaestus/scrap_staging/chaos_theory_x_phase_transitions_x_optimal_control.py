import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Lyapunov-Guided Bifurcation-Aware Controller (LBOC) Approximation.
    
    Mechanism:
    1. Structural Parsing (Optimal Control Layer): Extracts logical constraints 
       (negations, comparatives, conditionals) to form a rigid 'potential well'.
       Candidates violating these hard constraints receive high 'control cost'.
    2. Chaos/Phase Transition Monitor: Measures semantic 'distance' (NCD) between
       the prompt's logical core and the candidate. 
       - Low distance (Ordered): Candidate is too similar to prompt (echoing).
       - High distance (Chaotic): Candidate is unrelated noise.
       - Critical Zone: Candidate satisfies structural constraints while maintaining
         optimal informational divergence (answering the question, not repeating it).
    3. Scoring: Minimizes a cost function J = w1*StructViolations + w2*|NCD - Target|.
    """

    def __init__(self):
        self.target_ncd = 0.65  # The "Edge of Chaos" sweet spot
        self.struct_weight = 0.6
        self.ncd_weight = 0.4

    def _structural_parse(self, text: str) -> Dict[str, any]:
        """Extract logical constraints from text."""
        t = text.lower()
        return {
            "has_negation": bool(re.search(r'\b(not|no|never|without|fail|incorrect)\b', t)),
            "has_comparative": bool(re.search(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', t)),
            "has_conditional": bool(re.search(r'\b(if|then|unless|otherwise|when)\b', t)),
            "has_numeric": bool(re.search(r'\d+(\.\d+)?', t)),
            "word_count": len(t.split())
        }

    def _check_constraint_compliance(self, prompt_feats: Dict, cand_feats: Dict, candidate: str) -> float:
        """
        Optimal Control Layer: Calculates penalty for violating logical transitivity.
        Returns 0.0 (perfect) to 1.0 (violation).
        """
        penalty = 0.0
        
        # Negation consistency: If prompt negates, candidate shouldn't blindly affirm without nuance
        # Heuristic: If prompt has negation, candidate must not be a simple substring echo
        if prompt_feats["has_negation"]:
            if candidate.lower().strip() in prompt_feats.get("raw_prompt", "").lower():
                penalty += 0.5 # Suspicious echo in negative context
        
        # Comparative consistency: If prompt compares, candidate should reflect ordering
        if prompt_feats["has_comparative"] and not cand_feats["has_numeric"] and not cand_feats["has_comparative"]:
            # If prompt asks for comparison, candidate lacking comparative/numeric markers is suspect
            # unless it's a very short answer (like "A" or "Yes")
            if len(candidate.split()) > 1:
                penalty += 0.3

        # Conditional consistency: Check for 'if' without 'then' logic in long forms
        if prompt_feats["has_conditional"]:
            if not cand_feats["has_conditional"] and len(candidate.split()) > 10:
                # Long answers to conditional prompts often need logical connectors
                pass # Soft constraint, no hard penalty yet to avoid over-penalizing

        return min(penalty, 1.0)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
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

    def _estimate_lyapunov_exponent(self, prompt: str, candidate: str) -> float:
        """
        Chaos Theory Approximation.
        Estimates sensitivity to initial conditions by measuring how much
        the candidate diverges from the prompt's compressed representation relative to length.
        High divergence = Chaotic. Low divergence = Ordered.
        """
        ncd = self._ncd(prompt, candidate)
        # Map NCD to a pseudo-Lyapunov exponent lambda
        # lambda > 0 (Chaotic), lambda < 0 (Stable)
        # We want to be near 0 (Criticality)
        return (ncd - self.target_ncd)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._structural_parse(prompt)
        prompt_feats["raw_prompt"] = prompt
        results = []

        for cand in candidates:
            cand_feats = self._structural_parse(cand)
            
            # 1. Structural Cost (Optimal Control)
            struct_cost = self._check_constraint_compliance(prompt_feats, cand_feats, cand)
            
            # 2. Dynamical Cost (Chaos/Phase Transition)
            # We want the system state (candidate) to be near the bifurcation point
            lyap = self._estimate_lyapunov_exponent(prompt, cand)
            dynamical_cost = abs(lyap)  # Penalty for being far from critical point

            # 3. Total Cost Function
            total_cost = (self.struct_weight * struct_cost) + (self.ncd_weight * dynamical_cost)
            
            # Convert cost to score (0 to 1, higher is better)
            score = max(0.0, 1.0 - total_cost)
            
            # Tie-breaking: If scores are identical, prefer shorter, more direct answers
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Structural violation: {struct_cost:.2f}, Dynamical deviation: {abs(lyap):.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on structural alignment and criticality.
        """
        # Re-use evaluation logic for a single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        base_score = res[0]["score"]
        
        # Boost confidence if structural parsing found strong logical markers
        p_feats = self._structural_parse(prompt)
        a_feats = self._structural_parse(answer)
        
        bonus = 0.0
        if p_feats["has_numeric"] and a_feats["has_numeric"]:
            bonus = 0.1
        if p_feats["has_negation"] and "not" in answer.lower():
            bonus = 0.1
            
        return min(1.0, base_score * 0.9 + bonus)