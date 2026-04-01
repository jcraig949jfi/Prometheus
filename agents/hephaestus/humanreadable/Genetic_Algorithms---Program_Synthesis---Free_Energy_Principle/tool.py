import re
import numpy as np
import zlib
from typing import List, Dict, Tuple, Any, Optional
from itertools import combinations

class ReasoningTool:
    """
    Evolving Predictive Programs (EPP) Implementation.
    
    Mechanism:
    1. Parsing: Extracts a formal intermediate representation (FIR) of the prompt using regex.
       This includes numeric constants, logical operators, temporal markers, and entities.
    2. Computation (The "Program"): Instead of evolving a full GA population per query (too slow),
       we instantiate a set of deterministic "candidate programs" (solvers) derived from the 
       theoretical GA-DSL. These solvers execute specific logical/arithmetic operations on the FIR.
    3. Free Energy Minimization: We treat the "prediction error" as the distance between the 
       computed result of a solver and the candidate answer. Complexity is penalized.
    4. Epistemic Honesty: A meta-cognitive layer checks for ambiguity patterns (Tier B) before
       scoring. If ambiguity is high, confidence is capped low regardless of match quality.
    
    Score Decomposition: Structural (50%), Computation (35%), NCD (15%).
    """

    def __init__(self):
        # DSL Primitives extraction patterns
        self.num_pattern = re.compile(r'-?\d+(?:\.\d+)?')
        self.negation_words = {'not', 'no', 'never', 'none', 'neither', 'nobody'}
        self.comparators = {'>', '<', '>=', '<=', 'more', 'less', 'greater', 'smaller', 'equal'}
        self.logic_ops = {'and', 'or', 'if', 'then', 'else', 'because', 'therefore'}
        
        # Tier B Ambiguity Patterns
        self.presupposition_triggers = re.compile(r'(have you stopped|did you stop|why did .*(?:fail|stop|quit)|when did .*(?:stop|fail))', re.IGNORECASE)
        self.scope_ambiguity = re.compile(r'every .*(?:a|an) .*\?', re.IGNORECASE) # Simplified heuristic
        self.pronoun_ambiguity = re.compile(r'(told|said to) .* (he|she|him|her) .* who', re.IGNORECASE)
        self.false_dichotomy = re.compile(r'either .+ or .+', re.IGNORECASE)
        self.subjectivity = re.compile(r'(best|worst|favorite|most beautiful|ugliest)', re.IGNORECASE)

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Deterministic parsing to build the Factor Graph nodes."""
        features = {
            'numbers': [float(n) for n in self.num_pattern.findall(text)],
            'has_negation': any(w in text.lower().split() for w in self.negation_words),
            'has_comparator': any(c in text.lower() for c in self.comparators),
            'has_logic': any(l in text.lower() for l in self.logic_ops),
            'word_count': len(text.split()),
            'raw_lower': text.lower()
        }
        return features

    def _check_ambiguity(self, prompt: str) -> float:
        """
        Meta-cognitive check for Tier B traps.
        Returns a penalty score (0.0 = clear, 1.0 = highly ambiguous).
        """
        penalty = 0.0
        p_lower = prompt.lower()
        
        if self.presupposition_triggers.search(prompt): penalty = max(penalty, 0.8)
        if self.scope_ambiguity.search(prompt): penalty = max(penalty, 0.6)
        if self.pronoun_ambiguity.search(prompt): penalty = max(penalty, 0.7)
        if self.false_dichotomy.search(prompt) and 'otherwise' not in p_lower: penalty = max(penalty, 0.5)
        if self.subjectivity.search(prompt): penalty = max(penalty, 0.6)
        
        # Check for insufficient info markers
        if 'cannot be determined' in p_lower or 'insufficient' in p_lower:
            penalty = 0.9
            
        return penalty

    def _execute_computation(self, prompt: str) -> Optional[Any]:
        """
        Executes the 'Program Synthesis' step by running specific solvers on the parsed features.
        Returns the computed ground truth if derivable, else None.
        """
        p_lower = prompt.lower()
        features = self._extract_features(prompt)
        nums = features['numbers']
        
        # 1. Numeric Comparison / Arithmetic
        if len(nums) >= 2:
            # Pattern: "Which is larger, 9.11 or 9.9?" or simple math
            if 'larger' in p_lower or 'greater' in p_lower or 'more' in p_lower:
                return max(nums)
            if 'smaller' in p_lower or 'less' in p_lower:
                return min(nums)
            # Simple addition/subtraction heuristics for "bat-and-ball" or sum problems
            if 'total' in p_lower or 'sum' in p_lower or 'combined' in p_lower:
                return sum(nums)
            if 'difference' in p_lower:
                return abs(nums[0] - nums[1])
                
        # 2. Logic: Modus Tollens / Transitivity (Simplified)
        # Pattern: "If A then B. Not B. Therefore?" -> Not A
        if 'if' in p_lower and 'then' in p_lower:
            if 'not' in p_lower and ('therefore' in p_lower or 'what' in p_lower):
                # Heuristic: If prompt implies negation of consequence, answer is negation of antecedent
                # This is a placeholder for full logical graph execution
                return "negation_of_antecedent" 

        # 3. Counting / Fencepost
        if 'how many' in p_lower or 'count' in p_lower:
            if 'fencepost' in p_lower or 'posts' in p_lower:
                if len(nums) >= 2: # length and interval
                    return int(nums[0] / nums[1]) + 1
            if len(nums) == 1 and 'items' in p_lower:
                return int(nums[0])

        # 4. Probability / Base Rate (Simple detection)
        if 'probability' in p_lower or 'chance' in p_lower:
            if len(nums) >= 2:
                # Assume first is event, second is total if context suggests
                return nums[0] / nums[1] if nums[1] != 0 else 0.0

        return None

    def _compute_free_energy(self, candidate: str, computed_val: Any, prompt: str) -> Tuple[float, float, float]:
        """
        Computes the Free Energy components: Prediction Error, Complexity, Constraint Violation.
        F = <log q - log p> approximated by distance metrics.
        """
        # 1. Prediction Error (Distance between candidate and computed truth)
        pred_error = 1.0
        cand_lower = candidate.lower()
        
        if computed_val is not None:
            # Try to match numeric computed value
            cand_nums = self.num_pattern.findall(candidate)
            if cand_nums:
                val = float(cand_nums[0])
                # Normalized error
                scale = max(abs(computed_val), 1e-6)
                pred_error = min(1.0, abs(val - computed_val) / scale)
            else:
                # If we computed a number but candidate is text, high error unless semantic match
                pred_error = 0.9 
        else:
            # No computation possible, rely on structural match (NCD fallback later)
            pred_error = 0.5 

        # 2. Complexity (Length of candidate vs prompt information density)
        complexity = len(candidate) / (len(prompt) + 1)
        
        # 3. Constraint Violation (Logical consistency)
        # Check if candidate contradicts explicit negations in prompt
        violation = 0.0
        features = self._extract_features(prompt)
        if features['has_negation']:
            # If prompt says "not X" and candidate is "X", violation
            # Simplified check: if candidate word appears in prompt but prompt has "not [candidate]"
            if any(candidate.lower() in s for s in prompt.split('.')) and 'not' in prompt.lower():
                 # Very rough heuristic for demo
                 violation = 0.5

        return pred_error, complexity, violation

    def _meta_confidence(self, prompt: str) -> float:
        """Public wrapper for ambiguity check."""
        return 1.0 - self._check_ambiguity(prompt)

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.3 if ambiguity detected.
        Caps at 0.9 unless computation was definitive.
        """
        # 1. Check Epistemic Honesty (Tier B)
        ambiguity_penalty = self._check_ambiguity(prompt)
        if ambiguity_penalty > 0.4:
            return 0.1 + (0.2 * (1.0 - ambiguity_penalty)) # Return < 0.3

        # 2. Attempt Computation
        computed = self._execute_computation(prompt)
        features = self._extract_features(prompt)
        
        base_conf = 0.5
        
        if computed is not None:
            # We have a computed ground truth
            cand_nums = self.num_pattern.findall(answer)
            if cand_nums:
                val = float(cand_nums[0])
                if abs(val - computed) < 1e-6:
                    base_conf = 0.95 # Definitive match
                else:
                    base_conf = 0.1 # Definitive mismatch
            else:
                base_conf = 0.4 # Computed number, text answer
        else:
            # No computation, rely on structural similarity
            # Penalize if no structural features found
            if not features['has_negation'] and not features['has_comparator'] and len(features['numbers']) == 0:
                base_conf = 0.4 # Low info prompt

        # Cap confidence if no computation was performed (to avoid overconfidence on pattern matching)
        if computed is None:
            base_conf = min(base_conf, 0.85)
            
        return max(0.0, min(1.0, base_conf))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Main entry point. Ranks candidates based on EPP scoring.
        """
        results = []
        computed_truth = self._execute_computation(prompt)
        ambiguity = self._check_ambiguity(prompt)
        
        # Pre-calculate NCD matrix for tie-breaking (max 15% weight)
        prompt_comp = zlib.compress(prompt.encode())
        
        for cand in candidates:
            # 1. Compute Free Energy Components
            pred_err, complexity, violation = self._compute_free_energy(cand, computed_truth, prompt)
            
            # 2. Structural Score (Inverse of prediction error)
            # If we have a computed truth, this dominates
            if computed_truth is not None:
                struct_score = (1.0 - pred_err) * 0.6
            else:
                # Fallback to keyword overlap if no computation possible
                overlap = len(set(cand.lower().split()) & set(prompt.lower().split()))
                struct_score = min(1.0, overlap / 5.0) * 0.5

            # 3. Computational Score (Direct match to computed truth)
            comp_score = 0.0
            if computed_truth is not None:
                c_nums = self.num_pattern.findall(cand)
                if c_nums and abs(float(c_nums[0]) - computed_truth) < 1e-6:
                    comp_score = 0.35
            
            # 4. NCD Score (Tie breaker, max 15%)
            cand_comp = zlib.compress(cand.encode())
            joint_comp = zlib.compress((prompt + cand).encode())
            ncd = (len(joint_comp) - min(len(prompt_comp), len(cand_comp))) / max(len(prompt_comp), len(cand_comp), 1)
            ncd_score = (1.0 - ncd) * 0.15
            
            # Total Score
            # S = -F - lambda*complexity ... approximated here as weighted sum
            total_score = struct_score + comp_score + ncd_score
            
            # Apply Ambiguity Penalty (Epistemic Honesty)
            if ambiguity > 0.4:
                total_score *= 0.3 # Severely penalize scores on ambiguous prompts
            
            results.append({
                "candidate": cand,
                "score": float(total_score),
                "reasoning": f"Comp:{computed_truth is not None}, Err:{pred_err:.2f}, Ambig:{ambiguity:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results