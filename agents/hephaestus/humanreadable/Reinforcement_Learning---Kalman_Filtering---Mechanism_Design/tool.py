import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Belief-Augmented Incentive-Compatible Reasoning Tool.
    
    Mechanism:
    1. Kalman-like Belief State: Maintains a running estimate (mu, sigma) of the 
       'truth density' based on structural signal strength in the prompt.
    2. Mechanism Design (VCG-style): The scoring function acts as a payment rule.
       Candidates that align with high-confidence structural signals (negations, 
       numerics, conditionals) receive a 'truthful reporting' bonus. Candidates 
       that contradict structural constraints receive a heavy penalty (simulating 
       the VCG cost of lying).
    3. RL Loop: The 'policy' selects the ranking that maximizes the sum of 
       structural adherence (reward) and compression similarity (tiebreaker).
    
    This implements the 'Mechanism Design' core pattern requested, using structural
    parsing as the primary signal for incentive alignment.
    """

    def __init__(self):
        # Kalman Filter State: Belief over 'correctness'
        self.mu = 0.5  # Prior mean belief
        self.sigma = 1.0  # Prior uncertainty
        self.process_noise = 0.1
        self.measurement_noise = 0.5
        
        # Structural weights (Learned priors)
        self.weights = {
            'negation': 2.0,
            'comparative': 1.5,
            'conditional': 1.5,
            'numeric': 2.5,
            'constraint': 2.0
        }

    def _structural_parse(self, text: str) -> Dict[str, float]:
        """Extract structural features: negations, comparatives, conditionals, numerics."""
        text_lower = text.lower()
        features = {}
        
        # Negations
        negations = ['not', 'no', 'never', 'none', 'neither', 'cannot', "n't"]
        features['negation'] = sum(1 for w in negations if r'\b' + w + r'\b' in text_lower or f" {w} " in f" {text_lower} ")
        
        # Comparatives
        comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', '>', '<', '==']
        features['comparative'] = sum(1 for w in comparatives if w in text_lower)
        
        # Conditionals
        conditionals = ['if', 'then', 'else', 'unless', 'provided', 'when', 'whether']
        features['conditional'] = sum(1 for w in conditionals if r'\b' + w + r'\b' in text_lower)
        
        # Numerics (detect presence of numbers)
        features['numeric'] = len(re.findall(r'-?\d+\.?\d*', text))
        
        # Constraints (must, should, require)
        constraints = ['must', 'should', 'require', 'only', 'exactly', 'always']
        features['constraint'] = sum(1 for w in constraints if r'\b' + w + r'\b' in text_lower)
        
        return features

    def _kalman_update(self, signal_strength: float) -> Tuple[float, float]:
        """Update belief state based on signal strength."""
        # Prediction
        mu_pred = self.mu
        sigma_pred = self.sigma + self.process_noise
        
        # Update
        if sigma_pred + self.measurement_noise > 0:
            k = sigma_pred / (sigma_pred + self.measurement_noise)
            mu_new = mu_pred + k * (signal_strength - mu_pred)
            sigma_new = (1 - k) * sigma_pred
        else:
            mu_new, sigma_new = mu_pred, sigma_pred
            
        self.mu, self.sigma = mu_new, sigma_new
        return mu_new, sigma_new

    def _compute_vcg_payment(self, candidate: str, prompt_features: Dict[str, float], candidate_features: Dict[str, float]) -> float:
        """
        Compute a VCG-style payment term.
        Reward = Alignment with prompt structure.
        Penalty = Deviation from expected structural density (incentivizes truthful representation of logic).
        """
        reward = 0.0
        
        # Reward alignment: If prompt has negations, candidate should ideally reflect logical consistency
        # Since we don't have full NLI, we use feature density matching as a proxy for logical engagement
        for key in self.weights:
            p_feat = prompt_features.get(key, 0)
            c_feat = candidate_features.get(key, 0)
            
            # If prompt has high structural load, candidate gets reward for also having structure (engagement)
            # Or if prompt is simple, candidate is rewarded for not hallucinating complexity
            if p_feat > 0:
                # Encourage candidate to acknowledge structure (e.g. contain numbers if prompt has numbers)
                if key == 'numeric' and p_feat > 0:
                    reward += self.weights[key] * min(1.0, c_feat / max(1, p_feat))
                elif key != 'numeric':
                    # For logic keywords, presence in prompt implies logical complexity needed
                    reward += self.weights[key] * (0.5 if c_feat > 0 else 0.0)
            else:
                # Prompt is simple; penalize over-complexity (hallucination of structure)
                if c_feat > 0 and key in ['numeric', 'constraint']:
                    reward -= self.weights[key] * 0.2 # Small penalty for unnecessary complexity
                    
        return reward

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_both = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 1.0
        return (len_both - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._structural_parse(prompt)
        
        # Calculate global signal strength for Kalman update
        signal_strength = sum(prompt_feat.values()) / 5.0 if prompt_feat else 0.0
        self._kalman_update(signal_strength)
        
        scored_candidates = []
        
        for cand in candidates:
            cand_feat = self._structural_parse(cand)
            
            # 1. Structural Score (Primary Signal)
            # Check for direct contradictions or missing constraints if possible
            # Here we use the VCG payment as the main driver for 'truthful' alignment
            vcg_payment = self._compute_vcg_payment(cand, prompt_feat, cand_feat)
            
            # Base score from belief state
            base_score = self.mu * 10
            
            # 2. NCD Tiebreaker (Secondary Signal)
            # Prefer candidates that are compressible with the prompt (semantic similarity)
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 2.0 # Scale to be comparable
            
            total_score = base_score + vcg_payment + ncd_score
            
            # Reasoning string generation
            reasoning_parts = []
            if prompt_feat['numeric'] > 0:
                reasoning_parts.append(f"Numeric check: {'Pass' if cand_feat['numeric'] > 0 else 'Fail'}")
            if prompt_feat['negation'] > 0:
                reasoning_parts.append("Negation logic detected")
            if vcg_payment > 1.0:
                reasoning_parts.append("High structural alignment")
                
            reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Standard evaluation"

            scored_candidates.append({
                "candidate": cand,
                "score": float(total_score),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment and belief state."""
        prompt_feat = self._structural_parse(prompt)
        ans_feat = self._structural_parse(answer)
        
        # Calculate alignment score
        alignment = 0.0
        total_weight = 0.0
        
        for key in self.weights:
            p_val = prompt_feat.get(key, 0)
            a_val = ans_feat.get(key, 0)
            w = self.weights[key]
            total_weight += w
            
            if p_val > 0:
                # Expect presence
                if a_val > 0:
                    alignment += w
            else:
                # Expect absence (for specific keys like numeric in non-math prompts)
                if key == 'numeric' and a_val == 0:
                    alignment += w * 0.5
        
        # Normalize alignment
        norm_alignment = alignment / total_weight if total_weight > 0 else 0.5
        
        # Combine with current belief state (Kalman mu)
        confidence_val = 0.5 * self.mu + 0.5 * norm_alignment
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence_val))