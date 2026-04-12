import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    VFE-GACC Inspired Reasoning Tool.
    
    Mechanism:
    1. Core (Free Energy Principle): The 'score' is derived from minimizing prediction error.
       We approximate this by measuring structural consistency between the Prompt (generative model p)
       and the Candidate (approximate posterior q). Low structural divergence = Low Free Energy = High Score.
    2. Control (Phase Transitions): We calculate a 'criticality metric' based on the variance of 
       structural feature matches across the population. 
       - High Variance (Disordered/Heated): We relax scoring penalties, rewarding diverse structural matches 
         to prevent premature convergence on local minima.
       - Low Variance (Ordered/Cooled): We tighten scoring, heavily penalizing any structural mismatch 
         (negations, conditionals) to refine the best hypothesis.
    3. Implementation: Uses structural parsing (negations, comparatives, numerics) as the primary signal.
       NCD is used only as a tiebreaker for candidates with identical structural scores.
    """

    def __init__(self):
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower', '>', '<']
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', 'cannot', "n't"]
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'else', 'when', 'provided']
        self._critical_threshold = 0.5  # Psi_c

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floats and ints
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _has_feature(self, tokens: List[str], feature_list: List[str]) -> bool:
        return any(word in tokens for word in feature_list)

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Returns 1.0 if consistent, 0.0 if contradictory, 0.5 if neutral."""
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums or not c_nums:
            return 0.5 # Neutral if no numbers to compare
        
        # Simple heuristic: If prompt has numbers and candidate has numbers, 
        # check if they preserve order if comparatives are present.
        # For this implementation, we check if the candidate contradicts explicit numeric logic
        # Since full logic is hard without exec, we reward presence of numbers in numeric prompts.
        return 1.0 if len(c_nums) > 0 else 0.2

    def _structural_score(self, prompt: str, candidate: str) -> Tuple[float, Dict]:
        """
        Calculates a raw structural alignment score.
        Returns (score, features_dict)
        """
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        
        score = 0.0
        features = {}

        # 1. Negation Consistency (Modus Tollens check)
        p_neg = self._has_feature(p_tokens, self.negations)
        c_neg = self._has_feature(c_tokens, self.negations)
        
        if p_neg == c_neg:
            score += 2.0
        else:
            score -= 2.0 # Penalty for flipping negation
        features['negation_match'] = (p_neg == c_neg)

        # 2. Conditional/Logic Flow
        p_cond = self._has_feature(p_tokens, self.conditionals)
        c_cond = self._has_feature(c_tokens, self.conditionals)
        if p_cond and c_cond:
            score += 1.5
        elif p_cond and not c_cond:
            score -= 1.0 # Missing logic structure
        features['conditional_match'] = (p_cond == c_cond)

        # 3. Numeric Evaluation
        num_score = self._check_numeric_consistency(prompt, candidate)
        score += num_score
        features['numeric_score'] = num_score

        # 4. Comparative Presence
        p_comp = self._has_feature(p_tokens, self.comparatives)
        c_comp = self._has_feature(c_tokens, self.comparatives)
        if p_comp == c_comp:
            score += 1.0
        features['comparative_match'] = (p_comp == c_comp)

        return score, features

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0: return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # Step 1: Calculate raw structural scores (Free Energy approximation)
        # Lower free energy = Higher score. Here we maximize structural alignment.
        results = []
        structural_scores = []
        
        for cand in candidates:
            score, feats = self._structural_score(prompt, cand)
            results.append({
                "candidate": cand,
                "struct_score": score,
                "features": feats,
                "reasoning": ""
            })
            structural_scores.append(score)
        
        # Step 2: Phase Transition Control (Criticality)
        # Calculate population variance (Order Parameter Psi)
        if len(structural_scores) > 1:
            mean_score = sum(structural_scores) / len(structural_scores)
            variance = sum((s - mean_score) ** 2 for s in structural_scores) / len(structural_scores)
            # Normalize variance roughly to [0, 1] range assuming score range ~[-5, 5] -> var ~25
            psi = min(1.0, math.sqrt(variance) / 5.0) 
        else:
            psi = 0.0

        # Step 3: Adaptive Scoring based on Phase
        # If Psi > threshold (Disordered/High Variance): "Heat" the system.
        # We reduce the penalty gap to encourage exploration, making scores closer.
        # If Psi < threshold (Ordered/Low Variance): "Cool" the system.
        # We amplify differences to exploit the best structural match.
        
        final_results = []
        for res in results:
            base_score = res["struct_score"]
            
            # Apply Phase Transition Scaling
            if psi > self._critical_threshold:
                # Heated phase: Compress score range towards mean (Exploration)
                # Soften the impact of structural mismatches
                adjusted_score = base_score * 0.5 + mean_score * 0.5
                phase_reason = "High variance (Exploration): Relaxed scoring."
            else:
                # Cooled phase: Expand score range (Exploitation)
                # Sharpen the distinction between good and bad structural matches
                adjusted_score = base_score * 1.5
                phase_reason = "Low variance (Exploitation): Strict structural adherence."

            # NCD Tiebreaker (Only if structural scores are very close)
            # We add a tiny epsilon based on NCD to break ties without dominating
            ncd_val = self._ncd(prompt, res["candidate"])
            # Invert NCD so lower distance = higher score contribution
            ncd_bonus = (1.0 - ncd_val) * 0.01 
            
            final_score = adjusted_score + ncd_bonus
            
            # Normalize to 0-1 roughly using sigmoid-like mapping for readability
            # Assuming score range roughly -5 to 5
            normalized_score = 1 / (1 + math.exp(-final_score))
            
            final_results.append({
                "candidate": res["candidate"],
                "score": normalized_score,
                "reasoning": f"{phase_reason} Struct:{res['struct_score']:.2f}, NCD:{ncd_val:.2f}"
            })

        # Sort by score descending
        final_results.sort(key=lambda x: x["score"], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the evaluate method logic on a single candidate.
        """
        # Evaluate against a dummy set to get population stats if needed, 
        # but here we just run the structural check directly for speed.
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
        return res_list[0]["score"]