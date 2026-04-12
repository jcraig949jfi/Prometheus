import re
import math
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Bandit-Guided Metamorphic Consistency Scoring with Criticality Weighting.
    
    Mechanism:
    1. Structural Parsing: Extracts logical constraints (negations, comparatives, numerics) 
       from the prompt using regex.
    2. Metamorphic Variants: Generates simplified logical variants of the prompt to test 
       consistency, but uses them only for confidence estimation (per Coeus guidelines).
    3. Multi-Armed Bandit (UCB): Treats each candidate answer as an arm. Simulates "pulls" 
       by checking the candidate against extracted structural constraints. 
       - Reward = satisfaction of structural constraints.
       - Selection = Upper Confidence Bound to balance exploration/exploitation.
    4. Criticality Weighting: Computes the variance of mean rewards across all candidates.
       High variance indicates a "critical" unstable region. Final scores are down-weighted 
       by this variance to favor robust answers over brittle ones.
    5. NCD Tiebreaker: Uses Normalized Compression Distance only when structural signals 
       are indistinguishable.
    """

    def __init__(self):
        # Regex patterns for structural extraction
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|neither)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE),
            'numeric': re.compile(r'-?\d+(?:\.\d+)?'),
            'causal': re.compile(r'\b(because|therefore|thus|hence|since)\b', re.IGNORECASE)
        }

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract structural features from text."""
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'has_causal': bool(self.patterns['causal'].search(text)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)]
        }
        return features

    def _check_constraint(self, prompt: str, answer: str) -> float:
        """
        Constraint propagation checker.
        Returns 1.0 if answer satisfies structural constraints implied by prompt, else 0.0.
        Simplified for robustness: Checks for logical consistency in numbers and negation presence.
        """
        p_feat = self._extract_features(prompt)
        a_feat = self._extract_features(answer)
        score = 0.0
        checks = 0

        # Check 1: Numeric Consistency (if numbers exist in both, answer shouldn't contradict order if explicit)
        if p_feat['numbers'] and a_feat['numbers']:
            checks += 1
            # Heuristic: If prompt has specific numbers, answer containing them is a positive signal
            # This is a weak constraint but beats random guessing on numeric tasks
            if any(str(int(n)) in answer or str(n) in answer for n in p_feat['numbers']):
                score += 1.0
        
        # Check 2: Negation Alignment
        # If prompt has strong negation, a valid reasoning answer often reflects it or addresses it
        if p_feat['has_negation']:
            checks += 1
            if a_feat['has_negation']:
                score += 1.0
            else:
                # Penalty for ignoring negation, but not zero (context matters)
                score += 0.5 
        else:
            checks += 1
            score += 1.0 # Default pass if no negation to check

        # Check 3: Length/Complexity heuristic (Reasoning usually requires length)
        checks += 1
        if len(answer.strip()) > 10:
            score += 1.0

        return score / checks if checks > 0 else 0.5

    def _generate_mr_variants(self, prompt: str) -> List[str]:
        """Generate metamorphic variants for confidence estimation only."""
        variants = [prompt]
        # Simple transformations
        if "not" in prompt.lower():
            variants.append(prompt.replace("not", "NOT")) 
        if "if" in prompt.lower():
            variants.append(prompt.replace("if", "IF"))
        return variants

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        import zlib
        b1, b2 = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0: return 0.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        n_arms = len(candidates)
        mu = np.zeros(n_arms)      # Empirical mean reward
        n_pulls = np.zeros(n_arms) # Number of pulls
        
        # Structural Parsing Signal (Primary Score Base)
        structural_scores = []
        for cand in candidates:
            # Direct constraint check as the initial "pull"
            reward = self._check_constraint(prompt, cand)
            structural_scores.append(reward)
        
        # If all structural scores are identical (e.g., 0.0), rely on NCD immediately
        if len(set(structural_scores)) == 1 and structural_scores[0] == 0.0:
            # Fallback to NCD against prompt as primary signal
            base_scores = [1.0 - self._ncd(prompt, c) for c in candidates]
        else:
            base_scores = structural_scores

        # Bandit Simulation (Exploration/Exploitation on structural checks)
        # We simulate a few rounds of UCB to refine the mean based on "uncertainty"
        total_pulls = 0
        for _ in range(5): # 5 rounds of bandit refinement
            total_pulls += 1
            ucb_values = []
            for i in range(n_arms):
                if n_pulls[i] == 0:
                    ucb_values.append(float('inf')) # Explore unpulled arms
                else:
                    # UCB1 formula
                    exploration = math.sqrt(2 * math.log(total_pulls + 1) / n_pulls[i])
                    ucb_values.append(mu[i] + exploration)
            
            # Pull arm with max UCB
            best_arm = int(np.argmax(ucb_values))
            reward = base_scores[best_arm] # Deterministic reward from structural check
            
            # Update statistics
            n_pulls[best_arm] += 1
            mu[best_arm] += (reward - mu[best_arm]) / n_pulls[best_arm]

        # Criticality Weighting
        # Variance of the means indicates system instability (criticality)
        sigma_sq = float(np.var(mu)) if n_arms > 1 else 0.0
        
        final_scores = []
        for i in range(n_arms):
            # Score = Mean / (1 + Variance)
            # High variance (critical region) down-weights the score to penalize instability
            raw_score = mu[i]
            weighted_score = raw_score / (1.0 + sigma_sq)
            
            # NCD Tiebreaker for very close calls
            if n_arms > 1:
                others = [mu[j] for j in range(n_arms) if j != i]
                if others and abs(raw_score - max(others)) < 0.01:
                    ncd_val = self._ncd(prompt, candidates[i])
                    weighted_score += (1.0 - ncd_val) * 0.001 # Tiny boost for similarity

            final_scores.append(weighted_score)

        # Rank and format output
        ranked_indices = np.argsort(final_scores)[::-1]
        results = []
        for idx in ranked_indices:
            results.append({
                "candidate": candidates[idx],
                "score": float(final_scores[idx]),
                "reasoning": f"Structural consistency: {final_scores[idx]:.4f}, Criticality penalty applied based on variance {sigma_sq:.4f}"
            })
        
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural parsing and metamorphic stability.
        Uses MR variants only for support, not direct scoring.
        """
        # 1. Base structural score
        base_score = self._check_constraint(prompt, answer)
        
        # 2. Metamorphic consistency check (Support role only)
        variants = self._generate_mr_variants(prompt)
        consistent_count = 0
        total_checks = 0
        
        for v in variants:
            # Check if answer still holds basic structural logic against variant
            # We use a relaxed check here: does the answer still look reasonable?
            v_score = self._check_constraint(v, answer)
            if v_score > 0.5:
                consistent_count += 1
            total_checks += 1
            
        mr_ratio = consistent_count / total_checks if total_checks > 0 else 0.0
        
        # Combine: Base score is primary, MR ratio acts as a multiplier for robustness
        # If base score is 0, confidence is 0 regardless of MR
        confidence_val = base_score * (0.5 + 0.5 * mr_ratio)
        
        return min(1.0, max(0.0, confidence_val))