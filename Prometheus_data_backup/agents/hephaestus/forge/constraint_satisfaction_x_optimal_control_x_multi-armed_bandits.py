import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Constraint-Guided Bandit-Optimal Control (CBOC) Reasoning Tool.
    
    Mechanism:
    1. Hypothesis Generation (Bandit): Candidates are treated as arms. 
       Initial scores are boosted by an "optimism" factor based on structural 
       alignment with the prompt (negations, comparatives, conditionals).
    2. Constraint Satisfaction (CSP): Candidates are parsed for logical constraints.
       Hard constraints (e.g., explicit negations in prompt not reflected in answer)
       result in immediate feasibility pruning (score penalty).
    3. Optimal Control (Cost Function): Instead of physical trajectories, we compute
       a "logical cost" based on the distance between prompt constraints and 
       candidate assertions. Lower cost = higher score.
    4. Feedback Loop: The final score combines structural parsing (primary), 
       logical feasibility (CSP), and NCD (tiebreaker only).
       
    This implements the CBOC loop by using Bandit-style exploration bonuses for 
    structurally complex candidates, CSP for hard logical filtering, and a 
    control-like cost minimization for ranking.
    """

    def __init__(self):
        self._epsilon = 1e-6

    def _structural_parse(self, text: str) -> dict:
        """Extract logical features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|none|cannot|won\'t|didn\'t|isn\'t|aren\'t)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|larger|fewer|better|worse|than|>=|<=|>|<)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|whether)\b', text_lower)),
            'numbers': re.findall(r'\d+(?:\.\d+)?', text_lower),
            'has_question': '?' in text
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        CSP Feasibility Check.
        Returns a feasibility score (0.0 to 1.0). 
        0.0 indicates a hard constraint violation (infeasible).
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        score = 1.0
        
        # Constraint 1: Negation Consistency
        # If prompt has strong negation context and candidate ignores it (simple yes/no)
        if p_feat['negations'] > 0 and c_feat['negations'] == 0:
            if candidate.lower().strip() in ['yes', 'no', 'true', 'false']:
                # Heuristic: If prompt is negative, a bare "Yes" is often wrong without context
                # We don't prune completely but apply a heavy cost
                score -= 0.4
        
        # Constraint 2: Number Presence
        # If prompt asks for a number (has numbers in context or "how many"), candidate should ideally have numbers
        if p_feat['numbers'] and not c_feat['numbers']:
            # Check if prompt is a calculation request
            if any(op in prompt for op in ['+', '-', '*', '/', 'sum', 'total', 'difference']):
                score -= 0.5 # High cost for missing numbers in math contexts
                
        return max(0.0, score)

    def _compute_control_cost(self, prompt: str, candidate: str) -> float:
        """
        Optimal Control Cost Function.
        Computes a 'cost' based on structural alignment. Lower is better.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        cost = 0.0
        
        # Cost term 1: Comparative mismatch
        # If prompt compares things, candidate should ideally reflect comparison or specific value
        if p_feat['comparatives'] > 0:
            if c_feat['comparatives'] == 0 and not c_feat['numbers']:
                cost += 2.0 # High cost for ignoring comparison structure
        
        # Cost term 2: Conditional logic
        if p_feat['conditionals'] > 0:
            # If prompt is conditional, candidate lacking conditional keywords might be oversimplified
            # But often the answer is just the result. We check for contradiction instead.
            pass 
            
        # Cost term 3: Numeric consistency (Simple evaluation)
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                # If prompt implies a simple operation like "9.11 vs 9.9", check order
                p_nums = [float(n) for n in p_feat['numbers']]
                c_nums = [float(n) for n in c_feat['numbers']]
                
                # Heuristic: If prompt has two numbers and asks "which is larger", 
                # and candidate has one number, check if it's the max.
                if len(p_nums) >= 2 and len(c_nums) == 1:
                    if 'larger' in prompt.lower() or 'greater' in prompt.lower():
                        if c_nums[0] != max(p_nums):
                            cost += 5.0 # Massive cost for wrong max
                    elif 'smaller' in prompt.lower() or 'less' in prompt.lower():
                        if c_nums[0] != min(p_nums):
                            cost += 5.0 # Massive cost for wrong min
            except ValueError:
                pass

        return cost

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            return (c12 - min(c1, c2)) / max(c1, c2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features to avoid re-computation
        p_feat = self._structural_parse(prompt)
        
        for cand in candidates:
            # 1. CSP Feasibility Check (Pruning/Feasibility Score)
            feasibility = self._check_logical_consistency(prompt, cand)
            
            if feasibility < 0.1:
                # Hard prune via low score
                final_score = 0.0
                reason = "Infeasible: Violates hard logical constraints (CSP)."
            else:
                # 2. Optimal Control Cost Calculation
                cost = self._compute_control_cost(prompt, cand)
                
                # 3. Bandit-style Scoring (Optimism + Structural Reward)
                # Base score starts high, reduced by cost
                base_score = 1.0 - (cost * 0.1)
                
                # Structural Reward: Bonus if candidate matches prompt complexity type
                c_feat = self._structural_parse(cand)
                structural_bonus = 0.0
                if p_feat['negations'] > 0 and c_feat['negations'] > 0:
                    structural_bonus += 0.1
                if p_feat['comparatives'] > 0 and (c_feat['comparatives'] > 0 or c_feat['numbers']):
                    structural_bonus += 0.1
                
                # NCD Tiebreaker (only used if structural signals are weak)
                ncd_val = self._ncd(prompt, cand)
                # Invert NCD so lower distance = higher score, but weight it lightly
                ncd_bonus = (1.0 - ncd_val) * 0.05 
                
                raw_score = (base_score * feasibility) + structural_bonus + ncd_bonus
                final_score = max(0.0, min(1.0, raw_score))
                
                reason = f"Feasibility: {feasibility:.2f}, Control Cost: {cost:.2f}, Structural Bonus: {structural_bonus:.2f}"

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on CBOC evaluation.
        Uses the evaluate method internally to maintain consistency.
        """
        # Evaluate single candidate against itself and empty string to gauge relative strength
        # Actually, just run the scoring logic directly for efficiency
        feasibility = self._check_logical_consistency(prompt, answer)
        if feasibility < 0.1:
            return 0.0
            
        cost = self._compute_control_cost(prompt, answer)
        base_score = 1.0 - (cost * 0.1)
        final_score = max(0.0, min(1.0, base_score * feasibility))
        
        return float(final_score)