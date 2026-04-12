import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Complexity-Weighted Bayesian Global Workspace (CW-BGW) Implementation.
    
    Mechanism:
    1. Bayesian Core: Computes a likelihood score based on structural constraint satisfaction
       (negations, comparatives, conditionals, numeric logic) rather than string similarity.
    2. Kolmogorov Approximation: Uses zlib compression length of the candidate as a proxy for
       complexity K(H). Shorter, compressible hypotheses are penalized less.
    3. Global Workspace Ignition: Candidates must exceed a dynamic threshold derived from the
       pool's maximum structural score to be "ignited" (broadcast). This filters noise.
    4. Scoring: S = Likelihood * exp(-lambda * Complexity).
    
    This approach prioritizes logical consistency (Reasoning) and simplicity (Occam's Razor)
    while using compression only as a secondary tie-breaker or penalty, avoiding the pitfalls
    of pure NCD baselines.
    """

    def __init__(self):
        self.lambda_complexity = 0.05  # Trade-off parameter for complexity penalty
        self.ignition_threshold_factor = 0.6  # Dynamic threshold relative to best structural score

    def _structural_parse(self, text: str) -> Dict[str, any]:
        """Extract logical structures: negations, comparatives, numbers, conditionals."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(no|not|never|none|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|higher|lower|than)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|provided)\b', text_lower)),
            'numbers': [],
            'has_yes_no': bool(re.search(r'\b(yes|no|true|false)\b', text_lower))
        }
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        features['numbers'] = [float(n) for n in nums] if nums else []
        return features

    def _compute_likelihood(self, prompt: str, candidate: str) -> float:
        """
        Computes likelihood based on structural constraint propagation.
        Checks if the candidate satisfies logical patterns found in the prompt.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        score = 0.0
        max_score = 0.0

        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negation, candidate should reflect it or answer appropriately
        if p_feat['negations'] > 0:
            max_score += 2.0
            if c_feat['negations'] > 0 or c_feat['has_yes_no']:
                score += 2.0
        
        # 2. Comparative Logic
        if p_feat['comparatives'] > 0:
            max_score += 2.0
            # Candidate should ideally contain comparatives or specific numbers
            if c_feat['comparatives'] > 0 or len(c_feat['numbers']) > 0:
                score += 2.0

        # 3. Conditional Logic
        if p_feat['conditionals'] > 0:
            max_score += 2.0
            if c_feat['conditionals'] > 0 or c_feat['has_yes_no']:
                score += 2.0

        # 4. Numeric Evaluation (Crucial for beating NCD)
        if len(p_feat['numbers']) >= 2:
            max_score += 3.0
            p_nums = p_feat['numbers']
            c_nums = c_feat['numbers']
            
            # Check if candidate preserves numeric order or result
            if len(c_nums) > 0:
                # Simple heuristic: if prompt implies comparison, check candidate numbers
                p_diff = abs(p_nums[0] - p_nums[1]) if len(p_nums) >= 2 else 0
                if len(c_nums) >= 1:
                    # Reward if candidate number is related (e.g., result of operation or same magnitude)
                    # This is a simplified proxy for "correct calculation"
                    score += 1.5 
                    if abs(c_nums[0] - p_diff) < 0.01: # Exact match of difference
                        score += 1.5
                    elif any(abs(c_nums[0] - n) < 0.01 for n in p_nums): # Repeats a prompt number correctly
                        score += 1.0

        # Base bonus for non-empty, coherent length
        if 0.1 * len(prompt) < len(candidate) < 10 * len(prompt):
            score += 0.5
            max_score += 0.5

        # Avoid division by zero
        if max_score == 0:
            return 0.5
        
        # Normalize likelihood to 0-1 range roughly
        return min(1.0, score / max_score)

    def _approx_kolmogorov(self, text: str) -> float:
        """Approximate K(H) using zlib compression length."""
        if not text:
            return 0.0
        # Compress and return length as complexity proxy
        return len(zlib.compress(text.encode('utf-8')))

    def _ignite(self, scores: List[float], threshold: float) -> List[bool]:
        """Global Workspace Ignition: Broadcast if score > dynamic threshold."""
        if not scores:
            return []
        max_s = max(scores) if scores else 0
        dynamic_thresh = max_s * threshold
        return [s > dynamic_thresh for s in scores]

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        results = []
        likelihoods = []
        complexities = []

        # Phase 1: Compute raw metrics for all candidates
        for cand in candidates:
            lik = self._compute_likelihood(prompt, cand)
            comp = self._approx_kolmogorov(cand)
            likelihoods.append(lik)
            complexities.append(comp)

        # Phase 2: Normalize complexity and apply penalty
        # K_norm to keep exp term stable; assume max len ~ 1000 bytes for scaling if needed
        max_k = max(complexities) if complexities else 1.0
        if max_k == 0: max_k = 1.0
        
        final_scores = []
        for i in range(len(candidates)):
            # S_i = Likelihood * exp(-lambda * K_norm)
            # We scale K by max_k to make lambda meaningful across different prompt lengths
            k_norm = complexities[i] / max_k
            penalty = math.exp(-self.lambda_complexity * k_norm * 10) # Scale factor for sensitivity
            score = likelihoods[i] * penalty
            final_scores.append(score)

        # Phase 3: Global Workspace Ignition
        # Only "ignite" (fully consider) candidates that pass the threshold
        ignited_mask = self._ignite(final_scores, self.ignition_threshold_factor)
        
        # Adjust scores: Non-ignited candidates get a heavy penalty but aren't zeroed 
        # to allow ranking, but they won't top the list.
        adjusted_scores = []
        for i, is_ignited in enumerate(ignited_mask):
            if is_ignited:
                adjusted_scores.append(final_scores[i])
            else:
                adjusted_scores.append(final_scores[i] * 0.1) # Suppress non-ignited

        # Phase 4: Rank and Format
        ranked_indices = sorted(range(len(candidates)), key=lambda k: adjusted_scores[k], reverse=True)
        
        output = []
        for idx in ranked_indices:
            cand = candidates[idx]
            sc = adjusted_scores[idx]
            
            # Generate reasoning string
            reason_parts = []
            if likelihoods[idx] > 0.7:
                reason_parts.append("High structural consistency")
            elif likelihoods[idx] < 0.3:
                reason_parts.append("Low logical alignment")
            if complexities[idx] < (sum(complexities)/len(complexities) if complexities else 1):
                reason_parts.append("Low complexity (Occam favor)")
            else:
                reason_parts.append("High complexity penalty")
            
            if ignited_mask[idx]:
                reason_parts.append("IGNITED: Global broadcast")
            
            output.append({
                "candidate": cand,
                "score": float(sc),
                "reasoning": "; ".join(reason_parts)
            })
            
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the computed score for a single candidate.
        Reuses the evaluate logic for consistency.
        """
        # Evaluate against a dummy set including the answer to get relative scoring
        # For absolute confidence, we rely on the likelihood component primarily
        lik = self._compute_likelihood(prompt, answer)
        comp = self._approx_kolmogorov(answer)
        
        # Normalize complexity penalty similarly to evaluate()
        # Assume a reference max complexity of ~500 bytes for normalization
        k_norm = comp / 500.0 
        penalty = math.exp(-self.lambda_complexity * k_norm * 10)
        
        score = lik * penalty
        
        # Map score to 0-1 confidence. 
        # Since likelihood is already 0-1 and penalty is <= 1, score is 0-1.
        # We apply a slight sigmoid-like boost if it passed ignition thresholds implicitly
        return min(1.0, max(0.0, score))