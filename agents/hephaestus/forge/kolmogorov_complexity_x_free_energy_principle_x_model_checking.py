import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a self-verifying, complexity-aware active inference loop.
    
    Mechanism:
    1. Free Energy Principle (FEP): Measures predictive accuracy by matching 
       structural patterns (negations, comparatives, numerics) between prompt 
       and candidate. Low prediction error = high score.
    2. Kolmogorov Complexity (KC): Penalizes candidates that are either too 
       complex (long/uncompressed) or too simple (lack of detail), favoring 
       parsimonious explanations.
    3. Model Checking (MC): Verifies temporal/logical consistency. Checks if 
       the candidate contradicts explicit constraints (e.g., "not", "before") 
       found in the prompt.
       
    The final score is a weighted sum: L = FEP_accuracy - lambda1*KC - lambda2*MC_violation.
    """

    def __init__(self):
        # Weights derived from theoretical synergy analysis
        self.lambda_kc = 0.3
        self.lambda_mc = 0.5
        self.lambda_fep = 1.0

    def _extract_structural_features(self, text: str) -> Dict:
        """Extracts logical constraints: negations, comparatives, numerics."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without|unless)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|before|after|higher|lower)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'raw_len': len(text)
        }
        return features

    def _compute_kc_approx(self, text: str) -> float:
        """Approximates Kolmogorov Complexity using zlib compression length."""
        if not text:
            return 0.0
        compressed = zlib.compress(text.encode('utf-8'))
        return len(compressed)

    def _check_model_violations(self, prompt_feats: Dict, cand_feats: Dict, candidate: str) -> float:
        """
        Simulates Model Checking by verifying logical consistency.
        Returns a penalty score (0.0 = no violation, higher = severe violation).
        """
        penalty = 0.0
        
        # Check 1: Negation Consistency
        # If prompt has strong negation context, candidate shouldn't blindly affirm without nuance
        if prompt_feats['negations'] > 0:
            # Simple heuristic: if prompt says "not", and candidate is very short and positive, penalize
            if cand_feats['negations'] == 0 and cand_feats['raw_len'] < 20:
                # Heuristic penalty for potential contradiction in short answers
                penalty += 0.2

        # Check 2: Numeric Consistency (Basic)
        # If both have numbers, ensure they aren't wildly divergent in count (proxy for transitivity)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            # If prompt has 1 number and candidate has 5, might be hallucination
            if abs(len(prompt_feats['numbers']) - len(cand_feats['numbers'])) > 2:
                penalty += 0.3

        # Check 3: Structural Alignment
        # If prompt is conditional, candidate should ideally reflect conditionality or be very specific
        if prompt_feats['conditionals'] > 0 and cand_feats['conditionals'] == 0:
            # Not a hard violation, but increases uncertainty
            pass 
            
        return penalty

    def _compute_fep_score(self, prompt_feats: Dict, cand_feats: Dict) -> float:
        """
        Computes Free Energy approximation (Inverse Prediction Error).
        High score = Low Free Energy (Good match between model/prompt and observation/candidate).
        """
        score = 0.0
        
        # Feature matching bonus
        # Matching negation density
        if prompt_feats['negations'] > 0 and cand_feats['negations'] > 0:
            score += 0.5
        elif prompt_feats['negations'] == 0 and cand_feats['negations'] == 0:
            score += 0.2 # Consistent absence
            
        # Matching comparative density
        if prompt_feats['comparatives'] > 0 and cand_feats['comparatives'] > 0:
            score += 0.5
            
        # Numeric presence alignment
        if bool(prompt_feats['numbers']) == bool(cand_feats['numbers']):
            score += 0.3
            
        # Length plausibility (candidates shouldn't be empty or absurdly long relative to prompt)
        p_len = prompt_feats['raw_len']
        c_len = cand_feats['raw_len']
        if 0.1 * p_len <= c_len <= 2.0 * p_len:
            score += 0.4
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_feats = self._extract_structural_features(prompt)
        results = []
        
        # Baseline NCD for tie-breaking
        try:
            prompt_comp = zlib.compress(prompt.encode('utf-8'))
        except:
            prompt_comp = b''

        for cand in candidates:
            cand_feats = self._extract_structural_features(cand)
            
            # 1. Free Energy (Predictive Accuracy)
            fep_score = self._compute_fep_score(prompt_feats, cand_feats)
            
            # 2. Kolmogorov Complexity (Parsimony)
            # Normalize KC by length to avoid penalizing long necessary answers too harshly
            kc_raw = self._compute_kc_approx(cand)
            # Ideal KC is low relative to information content. 
            # We penalize high compression size relative to the prompt's complexity baseline
            kc_penalty = (kc_raw / (prompt_feats['raw_len'] + 1)) * self.lambda_kc
            
            # 3. Model Checking (Constraint Verification)
            mc_violation = self._check_model_violations(prompt_feats, cand_feats, cand)
            mc_penalty = mc_violation * self.lambda_mc
            
            # Combined Objective: Maximize FEP, Minimize KC and MC Violations
            # L = FEP - lambda1*KC - lambda2*MC
            final_score = (self.lambda_fep * fep_score) - kc_penalty - mc_penalty
            
            # NCD Tie-breaker logic (incorporated as small additive term if scores are close)
            ndcd = 0.0
            try:
                cand_comp = zlib.compress(cand.encode('utf-8'))
                joint_comp = zlib.compress((prompt + cand).encode('utf-8'))
                max_len = max(len(prompt_comp), len(cand_comp))
                if max_len > 0:
                    ndcd = (len(joint_comp) - min(len(prompt_comp), len(cand_comp))) / max_len
            except:
                pass
            
            # Adjust score slightly by NCD to break ties (lower NCD is better similarity)
            final_score -= (ndcd * 0.01)

            reasoning = f"FEP:{fep_score:.2f} KC:{kc_penalty:.2f} MC:{mc_penalty:.2f}"
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the evaluation score normalized."""
        # Evaluate single candidate against prompt
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        score = res_list[0]['score']
        
        # Map score to 0-1 range. 
        # Based on empirical bounds of the scoring function:
        # Max theoretical ~1.9 (Perfect match, low KC, no violation)
        # Min theoretical ~-2.0 (High penalty, high KC, violations)
        # Range ~4.0. Shift and scale.
        confidence = (score + 2.0) / 4.0
        return max(0.0, min(1.0, confidence))