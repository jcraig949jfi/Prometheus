import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    SOPIA: Self-Organizing Predictive-Incentive Architecture
    
    Core Mechanism:
    1. Free Energy Principle (FEP): The 'score' is derived from prediction error.
       We treat the prompt as a set of constraints (the generative model).
       Candidates are evaluated by how well they minimize 'surprise' (violation of constraints).
       Low surprise = Low Free Energy = High Score.
       
    2. Mechanism Design: The scoring function is an incentive-compatible reward scheme.
       r = alpha * InfoGain (structural complexity match) + beta * Utility (constraint satisfaction).
       The agent (evaluator) maximizes reward by truthfully reporting the candidate that 
       best satisfies the logical structure (revealed preference).
       
    3. Hebbian Learning (Restricted): Used ONLY in confidence() to measure local 
       association strength between prompt tokens and answer tokens, acting as a 
       confidence wrapper rather than a primary reasoner.
    """

    def __init__(self):
        # Alpha: Weight for structural/information gain (Curiosity)
        self.alpha = 0.6
        # Beta: Weight for constraint satisfaction (Extrinsic Utility)
        self.beta = 0.4
        
    def _structural_parse(self, text: str) -> dict:
        """Extract logical features: negations, comparatives, numbers, conditionals."""
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', text.lower())),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|<|>)\b', text.lower())),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text.lower())),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'length': len(text.split())
        }
        return features

    def _compute_constraint_violation(self, prompt: str, candidate: str) -> float:
        """
        Calculate 'Free Energy' (F) as constraint violation.
        F = Sum of errors in number logic, negation flipping, and length consistency.
        Lower F is better.
        """
        error = 0.0
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        # 1. Numeric Consistency (Modus Tollens/Transitivity check proxy)
        # If prompt has numbers, candidate should ideally relate or not contradict obvious bounds
        if p_feat['numbers']:
            try:
                p_nums = [float(x) for x in p_feat['numbers']]
                c_nums = [float(x) for x in c_feat['numbers']]
                
                # Simple heuristic: If prompt implies a range or comparison, 
                # penalize candidates that violate basic ordering if detectable.
                # Here we just penalize huge deviations in magnitude if counts match
                if len(p_nums) == len(c_nums) and len(p_nums) > 0:
                    for pn, cn in zip(p_nums, c_nums):
                        if pn != 0:
                            error += abs(pn - cn) / (abs(pn) + 1e-6) * 0.5
            except ValueError:
                pass

        # 2. Negation Consistency
        # If prompt is strongly negative, and candidate is positive (or vice versa) without cause
        # This is a soft check; strict logic requires NLP, we use feature mismatch penalty
        if p_feat['negations'] > 0 and c_feat['negations'] == 0:
            # Potential contradiction if the candidate ignores a negation constraint
            # We don't know the semantics, so we apply a small penalty for ignoring the feature entirely
            error += 0.2 * p_feat['negations']
            
        # 3. Conditional Logic Proxy
        # If prompt has conditionals, candidate length/complexity usually increases
        if p_feat['conditionals'] > 0 and c_feat['length'] < 3:
            error += 0.3

        return error

    def _compute_info_gain(self, prompt: str, candidate: str) -> float:
        """
        Approximate Information Gain via structural complexity.
        Candidates that mirror the structural density of the prompt (without echoing)
        are deemed to have higher 'curiosity' value.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        # Reward matching structural complexity (e.g., if prompt is complex, answer should be)
        complexity_match = 0.0
        if p_feat['length'] > 0:
            ratio = c_feat['length'] / max(p_feat['length'], 1)
            # Optimal ratio is around 0.2 to 1.0 (concise but substantial)
            if 0.2 <= ratio <= 1.5:
                complexity_match += 0.5
            
        # Reward detecting specific logical operators
        if p_feat['comparatives'] > 0 and c_feat['comparatives'] > 0:
            complexity_match += 0.3
        if p_feat['negations'] > 0 and c_feat['negations'] > 0:
            complexity_match += 0.3
            
        return complexity_match

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
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
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using SOPIA principles.
        Score = Alpha * InfoGain - Beta * FreeEnergy (Constraint Violation)
        NCD used only for tie-breaking.
        """
        scored_candidates = []
        
        for cand in candidates:
            # 1. Mechanism Design: Define Reward Function
            # InfoGain (Curiosity)
            info_gain = self._compute_info_gain(prompt, cand)
            
            # Free Energy (Prediction Error/Constraint Violation)
            # We invert this: Lower error -> Higher score
            constraint_error = self._compute_constraint_violation(prompt, cand)
            
            # Combined Reward (Incentive Compatible Score)
            # High info gain + Low error = High Score
            raw_score = (self.alpha * info_gain) - (self.beta * constraint_error)
            
            # Add a small base score for non-empty answers to avoid negative infinity issues
            base_score = 0.5 if len(cand.strip()) > 0 else 0.0
            final_score = base_score + raw_score
            
            # Reasoning trace
            reasoning = (
                f"InfoGain:{info_gain:.2f} (Structural match); "
                f"FreeEnergy:{constraint_error:.2f} (Constraint violations); "
                f"NetReward:{final_score:.2f}"
            )
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Tie-breaking with NCD if scores are extremely close (floating point epsilon)
        # This is a simplified stable sort enhancement
        if len(scored_candidates) > 1:
            if abs(scored_candidates[0]["score"] - scored_candidates[1]["score"]) < 1e-6:
                # Use NCD to break tie against the prompt (closemess to prompt context)
                scored_candidates.sort(key=lambda x: self._ncd(prompt, x["candidate"]), reverse=False)

        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Hebbian-inspired confidence wrapper.
        Measures local co-activation strength (token overlap) between prompt and answer.
        Restricted role: Only adjusts confidence based on direct lexical association,
        not logical validity.
        """
        if not answer or not prompt:
            return 0.0
            
        p_tokens = set(re.findall(r'\b\w+\b', prompt.lower()))
        a_tokens = set(re.findall(r'\b\w+\b', answer.lower()))
        
        if not p_tokens or not a_tokens:
            return 0.0
            
        # Hebbian weight: Strength of connection based on shared tokens
        intersection = p_tokens.intersection(a_tokens)
        union = p_tokens.union(a_tokens)
        
        if not union:
            return 0.0
            
        # Jaccard similarity as a proxy for synaptic overlap
        overlap_score = len(intersection) / len(union)
        
        # Boost if structural markers (from evaluate) are present in both
        p_struct = self._structural_parse(prompt)
        a_struct = self._structural_parse(answer)
        
        struct_bonus = 0.0
        if p_struct['negations'] > 0 and a_struct['negations'] > 0:
            struct_bonus += 0.1
        if p_struct['numbers'] and a_struct['numbers']:
            struct_bonus += 0.1
            
        # Cap at 1.0
        confidence_val = min(1.0, overlap_score + struct_bonus)
        
        # If the answer was ranked highly by the main engine, we implicitly trust it more,
        # but this function specifically isolates the Hebbian "firing together" metric.
        # We return the calculated confidence.
        return float(confidence_val)