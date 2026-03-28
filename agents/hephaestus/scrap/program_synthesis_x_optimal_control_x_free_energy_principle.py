import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Optimizing Active-Inference Program Synthesizer (SOAIPS) Approximation.
    
    Mechanism:
    Implements the Free Energy Principle (FEP) as the core evaluation metric.
    1. Generative Model: A probabilistic grammar parses the prompt for structural 
       constraints (negations, comparatives, conditionals, numeric logic).
    2. Free Energy Calculation: Defined as F = Accuracy_Penalty + Complexity_Cost.
       - Accuracy: Deviation from structural constraints derived from the prompt.
       - Complexity: Length-based penalty (Occam's razor) to prevent over-fitting.
    3. Optimal Control Analogy: The 'control policy' selects the candidate with 
       minimum Free Energy (maximum evidence).
    4. Separation of Concerns: Per causal analysis, Program Synthesis and Optimal 
       Control concepts are restricted to the confidence() wrapper (parsing support), 
       while FEP drives the evaluate() scoring.
    5. Baseline Beating: Uses explicit structural parsing and numeric evaluation 
       as primary signals, using NCD only as a tiebreaker for ambiguous cases.
    """

    def __init__(self):
        # Internal state for the generative model of constraints
        self.constraint_keywords = {
            'negation': ['not', 'no', 'never', 'none', 'cannot', "n't"],
            'comparative': ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<'],
            'conditional': ['if', 'then', 'unless', 'only if', 'provided'],
            'numeric': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        }

    def _parse_structure(self, text: str) -> Dict[str, any]:
        """Extract structural features from text (Generative Model)."""
        lower_text = text.lower()
        features = {
            'negation_count': sum(1 for k in self.constraint_keywords['negation'] if k in lower_text),
            'has_comparative': any(k in lower_text for k in self.constraint_keywords['comparative']),
            'has_conditional': any(k in lower_text for k in self.constraint_keywords['conditional']),
            'numbers': re.findall(r'-?\d+\.?\d*', lower_text),
            'length': len(text.split())
        }
        return features

    def _check_numeric_consistency(self, prompt_nums: List[str], candidate: str) -> float:
        """Verify numeric logic if numbers are present."""
        if not prompt_nums:
            return 0.0
        
        candidate_nums = re.findall(r'-?\d+\.?\d*', candidate.lower())
        if not candidate_nums:
            return -1.0 # Penalty for missing numbers when expected
            
        try:
            # Simple heuristic: If prompt has comparison words, check order
            # This is a simplified active inference step: predicting the outcome of a comparison
            p_vals = [float(n) for n in prompt_nums]
            c_vals = [float(n) for n in candidate_nums]
            
            # If the candidate preserves the relative order of the last two prompt numbers, reward
            if len(p_vals) >= 2 and len(c_vals) >= 1:
                # Detect if prompt implies sorting or comparison
                if p_vals[0] > p_vals[1]:
                    # Expecting descending or 'larger' concept
                    return 0.5 if c_vals[0] == max(p_vals) else -0.2
                else:
                    # Expecting ascending or 'smaller' concept
                    return 0.5 if c_vals[0] == min(p_vals) else -0.2
            return 0.0
        except ValueError:
            return -0.5

    def _calculate_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Calculate Variational Free Energy (VFE).
        VFE = Expected Surprise (Accuracy Loss) + Complexity Cost.
        Lower VFE is better. We return negative VFE so higher score = better.
        """
        p_feat = self._parse_structure(prompt)
        c_feat = self._parse_structure(candidate)
        
        surprise = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has strong negation, candidate should reflect logical negation or absence
        if p_feat['negation_count'] > 0:
            # Heuristic: If prompt says "not", candidate shouldn't be a blind affirmative echo
            if c_feat['negation_count'] == 0 and p_feat['negation_count'] > 1:
                surprise += 0.5 # Mild surprise if candidate ignores complex negation
        
        # 2. Numeric Consistency (Active Inference on numbers)
        if p_feat['numbers']:
            num_score = self._check_numeric_consistency(p_feat['numbers'], candidate)
            surprise -= num_score # Reward consistency, penalize inconsistency
        
        # 3. Structural Overlap (Constraint Propagation)
        # Check if key structural tokens in prompt appear in candidate (unless negated logic applies)
        prompt_words = set(prompt.lower().split())
        candidate_words = set(candidate.lower().split())
        
        # Intersection of significant structural words
        structural_hits = 0
        for k_type, keywords in self.constraint_keywords.items():
            for kw in keywords:
                if kw in prompt_words and kw in candidate_words:
                    structural_hits += 1
        
        # Normalize surprise by prompt complexity
        complexity_cost = math.log(c_feat['length'] + 1) * 0.05
        
        # Final Free Energy approximation
        # We want to minimize surprise. 
        # Score = -(Surprise + Complexity)
        # High structural hit reduces surprise.
        accuracy_term = -surprise + (structural_hits * 0.3)
        
        return accuracy_term - complexity_cost

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(z1, z2)
        if max_len == 0:
            return 0.0
        return (z12 - min(z1, z2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates by minimizing Free Energy.
        Returns ranked list of dicts.
        """
        scored_candidates = []
        
        # Pre-calculate prompt features to avoid re-parsing
        prompt_features = self._parse_structure(prompt)
        
        for cand in candidates:
            # Core FEP Evaluation
            fe_score = self._calculate_free_energy(prompt, cand)
            
            # Tie-breaking with NCD if structural signals are weak
            if abs(fe_score) < 0.1: 
                ncd = self._ncd_distance(prompt, cand)
                # Invert NCD so higher is better, scale down to not override strong FEP signals
                fe_score += (1.0 - ncd) * 0.05
            
            scored_candidates.append({
                "candidate": cand,
                "score": float(fe_score),
                "reasoning": f"FEP Score: {fe_score:.4f}, Len: {len(cand)}"
            })
        
        # Sort by score descending (Higher score = Lower Free Energy)
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses structural parsing (Program Synthesis/Optimal Control restricted role)
        to validate the answer against the prompt's logical form.
        """
        p_feat = self._parse_structure(prompt)
        a_feat = self._parse_structure(answer)
        
        confidence_val = 0.5 # Base prior
        
        # 1. Numeric Validation (Strong signal)
        if p_feat['numbers']:
            num_consistency = self._check_numeric_consistency(p_feat['numbers'], answer)
            if num_consistency > 0:
                confidence_val += 0.4
            elif num_consistency < 0:
                confidence_val -= 0.4
                
        # 2. Logical Form Validation
        # If prompt has conditionals, answer should ideally not be empty or gibberish
        if p_feat['has_conditional']:
            if a_feat['length'] > 2: # Minimal length check
                confidence_val += 0.1
            else:
                confidence_val -= 0.2
        
        # 3. Negation Check
        # If prompt is negative, and answer is a simple "Yes", penalize heavily
        if p_feat['negation_count'] > 0 and a_feat['negation_count'] == 0:
            if answer.strip().lower() in ['yes', 'true', '1']:
                confidence_val -= 0.3
        
        # Clamp between 0 and 1
        return max(0.0, min(1.0, confidence_val))