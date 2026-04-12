import re
import math
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Embodied Bandit Reasoning Tool.
    Mechanism: Treats candidate answers as arms in a contextual multi-armed bandit.
    Context is derived from 'embodied' structural features (negation, causality, spatial verbs).
    Scoring is based on Expected Information Gain (Mutual Information) of the Beta posterior
    regarding the answer's correctness, updated via simulated Thompson Sampling rounds.
    NCD is used strictly as a tiebreaker for low-signal candidates.
    """

    # Structural patterns for embodied feature extraction
    PATTERNS = {
        'negation': [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b'],
        'comparative': [r'\bmore\b', r'\bless\b', r'\best\b', r'\bmost\b', r'\bthan\b'],
        'conditional': [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\belse\b'],
        'causal': [r'\bbecause\b', r'\btherefore\b', r'\bleads?\s+to\b', r'\bthus\b'],
        'spatial_temporal': [r'\bpush\b', r'\bhold\b', r'\bbefore\b', r'\bafter\b', r'\babove\b', r'\bbelow\b'],
        'numeric': [r'\d+\.?\d*'],
        'entity_person': [r'\bhe\b', r'\bshe\b', r'\bthey\b', r'\bperson\b', r'\bman\b', r'\bwoman\b'],
        'entity_object': [r'\bit\b', r'\bobject\b', r'\bthing\b', r'\bbox\b', r'\bball\b']
    }

    def __init__(self):
        self.epsilon = 1e-6

    def _extract_features(self, text: str) -> np.ndarray:
        """Extract binary structural feature vector from text."""
        text_lower = text.lower()
        features = []
        for category, patterns in self.PATTERNS.items():
            match_count = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    match_count += 1
            # Binary presence for this category
            features.append(1 if match_count > 0 else 0)
        return np.array(features, dtype=float)

    def _beta_entropy(self, alpha: float, beta: float) -> float:
        """Calculate entropy of Beta distribution using gammaln."""
        if alpha <= 0 or beta <= 0:
            return 0.0
        ln_b = math.lgamma(alpha) + math.lgamma(beta) - math.lgamma(alpha + beta)
        term1 = (alpha - beta) / (alpha + beta)
        term2 = (math.digamma(alpha) - math.digamma(alpha + beta)) * alpha
        term3 = (math.digamma(beta) - math.digamma(alpha + beta)) * beta
        # Approximation for stability
        try:
            return ln_b - term1 * (math.digamma(alpha) - math.digamma(beta)) + term2 + term3 # Simplified logic for stability
            # Using standard entropy formula approximation for Beta:
            # H = ln(B(a,b)) - (a-1)*psi(a) - (b-1)*psi(b) + (a+b-2)*psi(a+b) ... 
            # Let's use the direct definition via expectation for robustness in code golf
            return 0.5 * math.log(2 * math.pi * math.e * (alpha * beta) / ((alpha + beta)**2 * (alpha + beta + 1)))
        except:
            return 0.0

    def _calculate_info_gain(self, alpha: float, beta: float, reward: int) -> float:
        """Calculate expected reduction in entropy (Information Gain)."""
        h_prior = self._beta_entropy(alpha, beta)
        h_post = 0.0
        if reward == 1:
            h_post = self._beta_entropy(alpha + 1, beta)
        else:
            h_post = self._beta_entropy(alpha, beta + 1)
        
        gain = h_prior - h_post
        return max(0.0, gain)

    def _simulate_bandit(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Run simulated bandit rounds to score a candidate."""
        combined = f"{prompt} {candidate}"
        x = self._extract_features(combined)
        
        # Initialize Beta prior (uninformative)
        alpha, beta_param = 1.0, 1.0
        
        # Weights for features (theta_k), default 1.0
        # In a real system, these would be tuned. Here we assume uniform importance.
        theta = np.ones(len(x))
        
        # Simulate 3 rounds of Thompson Sampling / Evaluation
        total_ig = 0.0
        reasoning_steps = []
        
        for round_idx in range(3):
            # Sample p from Beta
            sampled_p = np.random.beta(alpha, beta_param)
            
            # Determine synthetic reward based on structural consistency
            # Heuristic: If features exist in prompt, they should ideally appear in candidate 
            # or the combined logic holds. 
            # Simplified embodied logic: 
            # 1. Check if prompt has strong structural cues (negation, numbers)
            prompt_x = self._extract_features(prompt)
            cand_x = self._extract_features(candidate)
            
            # Reward logic: 
            # High reward if candidate mirrors structural complexity of prompt (embodied match)
            # Or if candidate resolves a conditional/negation correctly (simplified here as presence match)
            match_score = 0.0
            count = 0
            for k in range(len(x)):
                if prompt_x[k] > 0: # If prompt has this feature
                    count += 1
                    if cand_x[k] > 0: # And candidate acknowledges it
                        match_score += 1
            
            # Probability of reward increases with feature alignment
            prob_reward = (match_score / max(1, count)) if count > 0 else 0.5
            
            # Stochastic reward generation based on alignment
            r = 1 if np.random.random() < prob_reward else 0
            
            # Update posterior
            alpha += r
            beta_param += (1 - r)
            
            # Calculate IG for this step
            ig = self._calculate_info_gain(alpha - r, beta_param - (1-r), r)
            total_ig += ig
            reasoning_steps.append(f"Round {round_idx+1}: Feature alignment {match_score}/{max(1,count)}, Reward={r}, IG={ig:.4f}")

        return total_ig, "; ".join(reasoning_steps)

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        try:
            z1 = len(repr(s1.encode('utf-8'))) # Dummy compression proxy for pure stdlib
            # Real NCD needs zlib, using length ratio as fallback if zlib restricted, 
            # but prompt allows stdlib. Let's use zlib properly.
            import zlib
            c1 = len(zlib.compress(s1.encode()))
            c2 = len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            max_len = max(c1, c2)
            if max_len == 0: return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reason = self._simulate_bandit(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are very close (within epsilon)
        # This is a simplified stable sort enhancement
        final_results = []
        if len(results) > 1:
            # Group by score proximity
            groups = []
            if results:
                current_group = [results[0]]
                for i in range(1, len(results)):
                    if abs(results[i]['score'] - results[i-1]['score']) < self.epsilon:
                        current_group.append(results[i])
                    else:
                        groups.append(current_group)
                        current_group = [results[i]]
                groups.append(current_group)
            
            for group in groups:
                if len(group) > 1:
                    # Apply NCD tiebreaker within group
                    group.sort(key=lambda x: self._ncd_score(prompt, x['candidate']))
                final_results.extend(group)
        else:
            final_results = results
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the bandit score normalized."""
        score, _ = self._simulate_bandit(prompt, answer)
        # Normalize score: Theoretical max IG per round is small, sum over 3 rounds.
        # Map to 0-1 range heuristically. Max IG for Beta(1,1) -> Beta(2,1) is approx 0.3.
        # 3 rounds max ~ 0.9. 
        conf = min(1.0, max(0.0, score / 1.0))
        return conf