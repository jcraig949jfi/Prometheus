import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Closed-Loop Hypothesis Testing Engine.
    
    Mechanism:
    1. Bandit Layer (Selection): Treats candidates as arms. Uses Thompson Sampling logic
       (Gaussian sampling) based on structural match scores to select the 'best' hypothesis
       while maintaining exploration variance.
    2. Feedback Layer (Control): Computes error e(t) between candidate structure and prompt
       structure. Applies a PID-like penalty: large structural mismatches (e.g., negation flips)
       generate high error, driving the score down. Stability is ensured by bounding scores.
    3. Adaptive Layer (Estimation): Uses Recursive Least Squares (RLS) logic to update
       parameter weights for structural features (negations, numbers, conditionals) based
       on the immediate error signal, adapting the scoring criteria per-prompt.
       
    Priority: Structural parsing > Numeric evaluation > NCD (tiebreaker).
    """

    def __init__(self):
        # Adaptive parameters (theta): weights for [negation_match, number_match, conditional_match, length_match]
        self.theta = [0.4, 0.3, 0.2, 0.1] 
        self.lambda_rls = 0.95  # Forgetting factor for adaptation
        self.h_scale = 10.0     # Scaling for RLS gain

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Structural parsing: negations, comparatives, conditionals, numbers."""
        t_lower = text.lower()
        has_neg = bool(re.search(r'\b(not|no|never|neither|without|fail|false)\b', t_lower))
        has_cond = bool(re.search(r'\b(if|unless|provided|when|then)\b', t_lower))
        has_comp = bool(re.search(r'\b(more|less|greater|smaller|better|worser|than|>=|<=|!=)\b', t_lower))
        nums = re.findall(r'\d+\.?\d*', t_lower)
        numbers = [float(n) for n in nums] if nums else []
        return {
            'neg': has_neg,
            'cond': has_cond,
            'comp': has_comp,
            'nums': numbers,
            'len': len(text)
        }

    def _compute_structural_score(self, p_feat: Dict, c_feat: Dict) -> Tuple[float, List[float]]:
        """Calculate error components and return (total_error, feature_vector)."""
        # Feature vector x: [neg_match, num_match, cond_match, len_ratio]
        neg_match = 1.0 if p_feat['neg'] == c_feat['neg'] else 0.0
        
        num_match = 0.0
        if p_feat['nums'] and c_feat['nums']:
            # Check relative ordering or exact match
            if len(p_feat['nums']) == len(c_feat['nums']):
                if all(abs(p - c) < 1e-6 for p, c in zip(p_feat['nums'], c_feat['nums'])):
                    num_match = 1.0
                # Check order preservation for non-equal values
                elif len(p_feat['nums']) >= 2 and len(c_feat['nums']) >= 2:
                    p_ord = [p_feat['nums'][i] < p_feat['nums'][i+1] for i in range(len(p_feat['nums'])-1)]
                    c_ord = [c_feat['nums'][i] < c_feat['nums'][i+1] for i in range(len(c_feat['nums'])-1)]
                    if p_ord == c_ord: num_match = 0.8
        
        cond_match = 1.0 if p_feat['cond'] == c_feat['cond'] else 0.0
        len_ratio = 1.0 / (1.0 + abs(p_feat['len'] - c_feat['len']) / 10.0)
        
        x = [neg_match, num_match, cond_match, len_ratio]
        
        # Weighted error calculation (Feedback Layer)
        # Error is inverse of match quality
        errors = [1.0 - v for v in x] 
        total_error = sum(e * w for e, w in zip(errors, self.theta))
        
        return total_error, x

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        z = zlib.compress
        l1, l2, l12 = len(z(s1.encode())), len(z(s2.encode())), len(z((s1+s2).encode()))
        if min(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_feat = self._extract_features(prompt)
        scored_candidates = []
        
        # 1. Bandit Layer: Calculate base scores and add exploration noise
        base_scores = []
        for cand in candidates:
            c_feat = self._extract_features(cand)
            error, _ = self._compute_structural_score(p_feat, c_feat)
            # Convert error to reward (lower error = higher reward)
            # Base reward = 1 / (1 + error)
            base_reward = 1.0 / (1.0 + error)
            base_scores.append(base_reward)
        
        # Normalize base scores for stability
        max_base = max(base_scores) if base_scores else 1.0
        min_base = min(base_scores) if base_scores else 0.0
        range_base = max_base - min_base if max_base != min_base else 1.0
        
        final_results = []
        
        for i, cand in enumerate(candidates):
            c_feat = self._extract_features(cand)
            error, x_vec = self._compute_structural_score(p_feat, c_feat)
            
            # 2. Adaptive Layer: Update theta based on error (Simplified RLS/LMS)
            # If error is high, we penalize the features that matched poorly
            # Gradient descent step: theta_new = theta_old - lr * error * x_vec
            # Note: We adapt locally for this evaluation step to simulate "learning" the prompt type
            lr = 0.1
            for j in range(len(self.theta)):
                # Adjust weight based on how much this feature contributed to error
                feature_error = (1.0 - x_vec[j]) 
                self.theta[j] += lr * error * (feature_error - 0.5) * 0.1
                # Clamp weights
                self.theta[j] = max(0.05, min(0.5, self.theta[j]))

            # 3. Bandit Selection Logic (Thompson Sampling approximation)
            # Sample from Gaussian(Normalized_Score, Uncertainty)
            norm_score = (base_scores[i] - min_base) / range_base
            uncertainty = 0.1 * (1.0 - norm_score) # Higher uncertainty for lower scores
            sampled_score = norm_score + (hash(cand + prompt) % 100 / 100 - 0.5) * uncertainty
            
            # Final Score: Structural dominance + NCD tiebreaker
            ncd_val = self._ncd(prompt, cand)
            # NCD is only used if structural score is ambiguous, but here we blend slightly
            # to ensure strict ordering. Structural is 90%, NCD 10%.
            final_score = 0.9 * sampled_score + 0.1 * (1.0 - ncd_val)
            
            # Reasoning string generation
            reasoning = f"Structural match: {norm_score:.2f}. "
            if p_feat['neg'] != c_feat['neg']:
                reasoning += "Negation mismatch detected. "
            if p_feat['nums'] and c_feat['nums']:
                if len(p_feat['nums']) != len(c_feat['nums']):
                    reasoning += "Number count mismatch. "
                else:
                    reasoning += "Numeric structure aligned. "
            if p_feat['cond'] != c_feat['cond']:
                reasoning += "Conditional logic mismatch. "
            
            scored_candidates.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning.strip()
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment."""
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(answer)
        error, _ = self._compute_structural_score(p_feat, c_feat)
        
        # Convert error to confidence
        # Error 0 -> Conf 1.0, Error 1 -> Conf ~0.5, High error -> 0
        conf = 1.0 / (1.0 + error * 2.0)
        
        # Hard constraints (Modus Tollens check)
        if p_feat['neg'] != c_feat['neg']:
            conf *= 0.5 # Penalty for negation flip
        if p_feat['nums'] and c_feat['nums']:
             if len(p_feat['nums']) != len(c_feat['nums']):
                 conf *= 0.6
        
        return max(0.0, min(1.0, conf))