import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamically Constrained Active Inference Mechanism Design Tool.
    
    Core Mechanism:
    1. Thermodynamics (Entropy Budget): Candidates are penalized based on 
       'entropy production' (structural disorder/length) relative to a budget.
       Shorter, more structured answers have lower thermodynamic cost.
    2. Mechanism Design (Incentive Compatibility): The 'designer' (global goal)
       sets an incentive contract. Candidates gain 'utility' by matching 
       structural constraints (negations, comparatives) extracted from the prompt.
       Misalignment (hallucination) incurs a penalty (KL-divergence analog).
    3. Free Energy Principle (Variational Optimization): The final score is 
       a Free Energy functional G = Accuracy (Surprise minimization) + 
       Lambda * Cost (Entropy production). We minimize G to rank candidates.
    
    This implements a recursive ADMM-like update where structural parsing 
    provides the dual variables (constraints) and NCD provides the baseline distance.
    """

    def __init__(self):
        # Thermodynamic budget constant (E_max analog)
        self.max_entropy_budget = 100.0
        # Lagrange multiplier for energy constraint (lambda)
        self.beta = 0.5 
        # Incentive weight for structural alignment
        self.incentive_weight = 2.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode('utf-8')))
        c2 = len(zlib.compress(s2.encode('utf-8')))
        c12 = len(zlib.compress((s1 + s2).encode('utf-8')))
        max_c = max(c1, c2)
        if max_c == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_c

    def _extract_structural_features(self, text: str) -> Dict[str, any]:
        """Extract logical structure: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|neither|none)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worse|than|<|>)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'length': len(text.split())
        }
        return features

    def _thermodynamic_cost(self, candidate: str) -> float:
        """
        Calculate entropy production cost.
        Analogous to expected entropy production <sigma>.
        Penalizes excessive length and lack of structure (disorder).
        """
        length = len(candidate)
        # Simple entropy proxy: length normalized. Longer = higher entropy production.
        # We want to minimize this cost.
        raw_cost = length / 100.0 
        return raw_cost

    def _mechanism_design_utility(self, prompt_features: Dict, cand_features: Dict, candidate: str) -> float:
        """
        Calculate utility based on incentive compatibility.
        The 'contract' rewards matching structural properties of the prompt.
        """
        utility = 0.0
        
        # Incentive 1: Negation alignment (Crucial for reasoning)
        if prompt_features['has_negation']:
            if cand_features['has_negation']:
                utility += 1.0 # Reward matching negation
            else:
                utility -= 2.0 # Heavy penalty for ignoring negation (Hallucination)
        else:
            # If prompt has no negation but candidate does, slight penalty for unnecessary complexity
            if cand_features['has_negation']:
                utility -= 0.5

        # Incentive 2: Comparative alignment
        if prompt_features['has_comparative']:
            if cand_features['has_comparative']:
                utility += 1.0
            else:
                utility -= 1.5

        # Incentive 3: Numeric consistency (Simple check)
        if prompt_features['numbers'] and cand_features['numbers']:
            # If both have numbers, reward proximity or presence
            utility += 0.5
        elif prompt_features['numbers'] and not cand_features['numbers']:
            # Prompt asks for math/numbers, candidate ignores -> Penalty
            utility -= 1.0
            
        return utility

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute Variational Free Energy G = Expected Surprise - Utility + Energy_Cost
        Minimizing G maximizes likelihood of correctness under constraints.
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        # 1. Surprise term (approximated by NCD distance to prompt context)
        # Lower NCD = Lower Surprise
        surprise = self._compute_ncd(prompt, candidate)
        
        # 2. Utility term (Mechanism Design alignment)
        # Higher utility = Lower Free Energy (since we subtract it or treat as negative cost)
        utility = self._mechanism_design_utility(p_feat, c_feat, candidate)
        
        # 3. Energy Cost (Thermodynamics)
        energy_cost = self._thermodynamic_cost(candidate)
        
        # Free Energy Functional: G = Surprise - (Incentive_Weight * Utility) + (Beta * Energy_Cost)
        # We want to MINIMIZE G. 
        # So high utility reduces G. High surprise increases G. High energy increases G.
        free_energy = surprise - (self.incentive_weight * utility) + (self.beta * energy_cost)
        
        return free_energy

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        
        # Pre-compute prompt features once
        prompt_features = self._extract_structural_features(prompt)
        
        # Check for numeric evaluation opportunity (Strong structural signal)
        prompt_nums = prompt_features['numbers']
        has_math_op = any(op in prompt for op in ['+', '-', '*', '/', 'greater', 'smaller', 'larger', 'less'])
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # Primary Signal: Structural Parsing & Numeric Evaluation
            cand_features = self._extract_structural_features(cand)
            cand_nums = cand_features['numbers']
            
            structural_match = False
            
            # Case A: Direct Numeric Evaluation
            if has_math_op and prompt_nums and cand_nums:
                try:
                    # Attempt to verify simple comparisons if possible
                    # This is a heuristic proxy for "computing" the answer
                    p_val = float(prompt_nums[0])
                    c_val = float(cand_nums[0])
                    
                    if 'greater' in prompt.lower() or '>' in prompt:
                        if c_val > p_val: structural_match = True
                    elif 'less' in prompt.lower() or '<' in prompt:
                        if c_val < p_val: structural_match = True
                    elif '=' in prompt:
                        if abs(c_val - p_val) < 1e-6: structural_match = True
                    else:
                        # General numeric presence boost
                        structural_match = True 
                except:
                    pass
            
            # Case B: Logical Structure Matching (Negation/Conditionals)
            if prompt_features['has_negation'] and cand_features['has_negation']:
                structural_match = True
                reasoning_parts.append("Aligned negation structure")
            elif prompt_features['has_comparative'] and cand_features['has_comparative']:
                structural_match = True
                reasoning_parts.append("Aligned comparative structure")
            elif prompt_features['has_conditional'] and cand_features['has_conditional']:
                structural_match = True
                reasoning_parts.append("Aligned conditional structure")
            elif not prompt_features['has_negation'] and not cand_features['has_negation']:
                 # Absence of negation in both is neutral/slightly positive
                 structural_match = True

            # Compute Core Thermodynamic-Free-Energy Score
            fe_score = self._compute_free_energy(prompt, cand)
            
            # Convert Free Energy to a maximization score (Negative FE is good)
            # Base score inverted: lower FE -> higher score
            base_score = -fe_score
            
            # Boost for explicit structural matches detected above
            if structural_match:
                base_score += 0.5
                if not reasoning_parts:
                    reasoning_parts.append("Structural alignment detected")
            
            # Tie-breaker: NCD (already part of FE, but emphasized here if needed)
            # If scores are very close, the one with lower NCD (more relevant) wins.
            # This is implicitly handled in FE, but we add a tiny epsilon based on pure NCD
            # to ensure deterministic ordering for identical logical structures.
            ncd_val = self._compute_ncd(prompt, cand)
            base_score -= (ncd_val * 0.01) # Minor penalty for high NCD
            
            scored_candidates.append({
                "candidate": cand,
                "score": base_score,
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Thermodynamic optimization applied"
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the Free Energy gap.
        High confidence if the answer minimizes free energy significantly compared to a random baseline.
        """
        # Evaluate single candidate against prompt
        fe_score = self._compute_free_energy(prompt, answer)
        
        # Baseline: Random string of same length (approximated by high entropy)
        # If FE is very low (negative), confidence is high.
        # Map FE to [0, 1]. 
        # Heuristic: FE < -1.0 is very confident. FE > 1.0 is low confidence.
        # Sigmoid mapping: 1 / (1 + exp(fe_score))
        confidence = 1.0 / (1.0 + math.exp(feat_score := fe_score))
        
        # Clamp
        return max(0.0, min(1.0, confidence))