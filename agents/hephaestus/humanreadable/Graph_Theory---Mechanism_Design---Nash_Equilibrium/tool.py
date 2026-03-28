import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Strategic Graphical Game Solver for Hypothesis Testing.
    
    Mechanism:
    1. Graph Formulation: Candidates are nodes. Edges represent logical conflicts 
       (negations) or dependencies (shared constraints).
    2. Mechanism Design (VCG-inspired): We simulate a truth-telling game. 
       Candidates gain 'utility' for satisfying structural constraints (logic) 
       and lose utility for conflicting with high-confidence truths. 
       This mimics VCG by penalizing deviations from logical consistency.
    3. Nash Equilibrium: We iterate candidate scores until convergence (equilibrium),
       where no candidate can improve its 'truth score' by changing its status 
       relative to the prompt's constraints.
       
    Primary Signal: Structural parsing (negations, comparatives, conditionals).
    Tiebreaker: Normalized Compression Distance (NCD).
    """

    def __init__(self):
        self.comparators = ['greater than', 'less than', 'equal to', 'larger', 'smaller', 'more', 'less']
        self.negations = ['not', 'no', 'never', 'none', 'cannot', 'impossible']
        self.conditionals = ['if', 'then', 'unless', 'only if']

    def _extract_structure(self, text: str) -> dict:
        """Extract logical primitives: negations, comparatives, numbers."""
        text_lower = text.lower()
        has_negation = any(n in text_lower for n in self.negations)
        has_conditional = any(c in text_lower for c in self.conditionals)
        has_comparative = any(c in text_lower for c in self.comparators)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r"-?\d+\.?\d*", text)
        nums = [float(n) for n in numbers]
        
        return {
            "negation": has_negation,
            "conditional": has_conditional,
            "comparative": has_comparative,
            "numbers": nums,
            "length": len(text.split())
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def _logical_consistency_score(self, prompt: str, candidate: str) -> float:
        """
        Compute a score based on logical consistency (Mechanism Design).
        Rewards structural alignment, penalizes contradictions.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        score = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt implies negation, candidate should reflect it or not contradict
        if p_struct["negation"]:
            if c_struct["negation"]:
                score += 0.4 # Aligned negation
            else:
                # Heuristic: if prompt says "X is not Y", and candidate is "X is Y", penalize
                # Simple keyword overlap check for contradiction
                p_words = set(prompt.lower().split())
                c_words = set(candidate.lower().split())
                if len(p_words & c_words) > 2: # Significant overlap suggests same topic
                    score -= 0.5 
        else:
            # Prompt is positive, candidate introduces unwarranted negation?
            if c_struct["negation"] and len(c_struct["numbers"]) == 0:
                score -= 0.2

        # 2. Numeric Evaluation
        if p_struct["numbers"] and c_struct["numbers"]:
            # Check if candidate preserves numeric logic (simplified)
            # If prompt has numbers and candidate has numbers, reward similarity in magnitude/order
            p_nums = sorted(p_struct["numbers"])
            c_nums = sorted(c_struct["numbers"])
            if len(p_nums) == len(c_nums):
                match = all(abs(p - c) < 1e-6 for p, c in zip(p_nums, c_nums))
                if match:
                    score += 0.5
            # Check for explicit comparison words if prompt has comparatives
            if p_struct["comparative"] and c_struct["comparative"]:
                score += 0.3

        # 3. Conditional Logic
        if p_struct["conditional"]:
            if c_struct["conditional"]:
                score += 0.3
            # If prompt is conditional, absolute statements might be weaker
            elif not c_struct["negation"]:
                score += 0.1 

        # 4. Length/Complexity penalty for gibberish
        if c_struct["length"] < 2:
            score -= 0.2
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        n = len(candidates)
        if n == 0:
            return []
            
        # Initialize scores (Strategies)
        # Start with structural consistency as the base utility
        utilities = [self._logical_consistency_score(prompt, c) for c in candidates]
        
        # Graphical Game Iteration (Converging to Nash Equilibrium)
        # Nodes influence each other. If two candidates are similar (high NCD proximity),
        # they reinforce. If they are contradictory (one has negation, one doesn't, same topic),
        # they suppress.
        
        # Precompute NCD matrix (sparse approximation: only care about self vs others for ranking)
        # To save compute, we use NCD primarily as a tie-breaker or cluster check.
        # Here we simulate 3 rounds of "regret matching" style updates.
        
        for _ in range(3):
            new_utils = utilities[:]
            for i in range(n):
                neighbor_influence = 0.0
                count = 0
                for j in range(n):
                    if i == j: continue
                    # Simple interaction: if candidate j is very different (low NCD) 
                    # but has high utility, it might indicate a distinct valid hypothesis.
                    # If candidate j is similar (high NCD ~ low distance) and high utility, reinforce.
                    dist = self._compute_ncd(candidates[i], candidates[j])
                    if dist < 0.5: # Similar candidates
                        neighbor_influence += utilities[j] * (1.0 - dist)
                        count += 1
                
                if count > 0:
                    # VCG-like adjustment: Utility depends on local neighborhood consistency
                    # This creates the "Potential Game" dynamic
                    adjustment = 0.1 * (neighbor_influence / count)
                    new_utils[i] = utilities[i] + adjustment
            
            utilities = new_utils

        # Final Scoring: Combine Equilibrium Utility with NCD tie-breaking
        results = []
        for i, cand in enumerate(candidates):
            # Primary Score: Equilibrium Utility
            score = utilities[i]
            
            # NCD Tie-Breaker / Calibration
            # Prefer candidates that are compressible with the prompt (relevant) 
            # but not identical (trivial).
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Adjust score: High NCD (dissimilar) is bad for relevance, unless it's a specific answer
            # We want low NCD (high similarity in information content) for relevance
            relevance_bonus = (1.0 - ncd_val) * 0.2
            
            final_score = score + relevance_bonus
            
            # Reasoning string generation
            reasoning = f"Structural Score: {score:.2f}; NCD Relevance: {1.0-ncd_val:.2f}"
            if p_struct := self._extract_structure(prompt):
                parts = []
                if p_struct["negation"]: parts.append("negation detected")
                if p_struct["comparative"]: parts.append("comparative detected")
                if p_struct["numbers"]: parts.append(f"nums:{p_struct['numbers']}")
                if parts:
                    reasoning += f"; Prompt Context: {', '.join(parts)}"

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the equilibrium score of the single answer.
        """
        # Evaluate against itself and a dummy to get relative standing
        # Or simply use the internal scoring mechanism normalized
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]["score"]
        
        # Map raw score (approx -1.0 to 2.0 range) to 0-1
        # Baseline 0 is neutral. >0.5 is strong.
        confidence = 1.0 / (1.0 + 2.718 ** (-raw_score)) # Sigmoid mapping
        
        return max(0.0, min(1.0, confidence))