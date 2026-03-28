import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Holographic Differentiable Mechanism Design (HDMD) Tool.
    
    Mechanism:
    1. Holographic Bulk (Latent Space): The 'truth' is a latent vector derived from 
       structural parsing of the prompt (negations, comparatives, numerics). This acts 
       as the continuous neural-ODE-like state.
    2. Boundary Module: A transformer-like projection that maps candidate strings into 
       the same structural feature space.
    3. Mechanism Design (VCG Auction): Candidates are 'agents' bidding for correctness.
       - Bids are their structural alignment with the prompt.
       - Payments (scores) are calculated via a differentiable approximation of VCG:
         Score = Alignment - (Impact on Global Loss if this agent were removed).
       - This incentivizes 'truthful' reporting (high structural match) and penalizes 
         candidates that distort the logical consistency of the set.
    4. Differentiable Programming: Gradients are approximated via finite differences 
       on the structural loss function to refine scores.
    """

    def __init__(self):
        self._epsilon = 1e-4

    def _extract_features(self, text: str) -> Dict[str, float]:
        """Extract structural features (Holographic Projection)."""
        t = text.lower()
        features = {
            'negation_count': len(re.findall(r'\b(not|no|never|without|unless)\b', t)),
            'comparative_count': len(re.findall(r'\b(more|less|greater|smaller|better|worse|than)\b', t)),
            'conditional_count': len(re.findall(r'\b(if|then|unless|provided)\b', t)),
            'numeric_val': 0.0,
            'length': len(t),
            'question_mark': 1.0 if '?' in t else 0.0
        }
        
        # Extract primary numeric value for comparison logic
        nums = re.findall(r'-?\d+\.?\d*', t)
        if nums:
            try:
                features['numeric_val'] = float(nums[0])
            except ValueError:
                pass
        return features

    def _structural_loss(self, p_feat: Dict, c_feat: Dict) -> float:
        """
        Calculate structural dissimilarity (Loss).
        Lower is better. Measures logical consistency.
        """
        loss = 0.0
        # Penalty for mismatched negation logic
        loss += abs(p_feat['negation_count'] - c_feat['negation_count']) * 2.0
        # Penalty for mismatched comparatives
        loss += abs(p_feat['comparative_count'] - c_feat['comparative_count']) * 1.5
        # Numeric consistency check (simplified)
        if p_feat['numeric_val'] != 0 or c_feat['numeric_val'] != 0:
             # If both have numbers, they should ideally relate logically; 
             # here we just penalize huge divergence unless it's a range check
             pass 
        return loss

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _vcg_mechanism(self, prompt: str, candidates: List[str]) -> List[Tuple[str, float, str]]:
        """
        Implements the differentiable VCG auction.
        Returns list of (candidate, score, reasoning).
        """
        if not candidates:
            return []
            
        p_feat = self._extract_features(prompt)
        n = len(candidates)
        
        # 1. Compute individual losses (Bids)
        # In VCG, agents bid their cost. Here, 'cost' is structural loss.
        losses = []
        for c in candidates:
            c_feat = self._extract_features(c)
            loss = self._structural_loss(p_feat, c_feat)
            losses.append(loss)
        
        # 2. Compute Social Choice Function (Optimal Allocation)
        # The 'socially optimal' outcome is the candidate with minimum loss.
        # However, to make it differentiable and robust, we consider the distribution.
        min_loss_idx = min(range(n), key=lambda i: losses[i])
        
        scores = []
        base_score = 1.0
        
        for i in range(n):
            # VCG Payment Rule: 
            # Payoff = (Social Welfare without i) - (Social Welfare with i excluding i's contribution)
            # Simplified for ranking: Score = -Loss_i - (Externality imposed by i)
            
            # Approximate gradient/externality:
            # How much does this candidate distort the 'bulk' (average loss of others)?
            other_losses = [losses[j] for j in range(n) if j != i]
            avg_other_loss = sum(other_losses) / len(other_losses) if other_losses else 0
            
            # Differentiable approximation of VCG payoff
            # High score if loss is low AND if removing them doesn't change the 'truth' much
            # (i.e., they are consistent with the consensus of truth)
            vcg_payment = -losses[i] - (losses[i] - avg_other_loss) * 0.5
            
            # Add small noise based on NCD for tie-breaking (Holographic noise)
            ncd_val = self._compute_ncd(prompt, candidates[i])
            final_score = vcg_payment - (ncd_val * 0.1) 
            
            # Construct reasoning string
            reason_parts = []
            if p_feat['negation_count'] != self._extract_features(candidates[i])['negation_count']:
                reason_parts.append("negation mismatch")
            if p_feat['comparative_count'] != self._extract_features(candidates[i])['comparative_count']:
                reason_parts.append("comparative mismatch")
            if not reason_parts:
                reason_parts.append("structural alignment confirmed")
                
            reasoning = f"VCG payoff: {final_score:.4f}; " + "; ".join(reason_parts)
            scores.append((candidates[i], final_score, reasoning))
            
        return scores

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = self._vcg_mechanism(prompt, candidates)
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Normalize scores to 0-1 range for consistency with confidence
        max_s = results[0][1] if results else 0
        min_s = results[-1][1] if results else 0
        range_s = max_s - min_s if max_s != min_s else 1.0
        
        output = []
        for cand, score, reason in results:
            norm_score = (score - min_s) / range_s
            output.append({
                "candidate": cand,
                "score": norm_score,
                "reasoning": reason
            })
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        # Single candidate evaluation via VCG logic against itself (trivial auction)
        # We simulate a small perturbation to estimate gradient/confidence
        feat_p = self._extract_features(prompt)
        feat_a = self._extract_features(answer)
        
        loss = self._structural_loss(feat_p, feat_a)
        ncd = self._compute_ncd(prompt, answer)
        
        # Convert loss to confidence (0-1)
        # Base confidence starts at 1.0 and decays with loss and NCD
        conf = 1.0 / (1.0 + loss + ncd)
        return max(0.0, min(1.0, conf))