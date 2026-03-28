import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hierarchical Eco-Bandit RL Reasoning Tool (Computational Analogy).
    
    Mechanism:
    1. Species (Candidates): Each candidate answer is treated as a species.
    2. Structural Fitness (RL Reward): Instead of environmental rewards, we compute
       a 'fitness' score based on structural alignment with the prompt (negations,
       comparatives, numeric consistency). This acts as the extrinsic reward signal.
    3. Trophic Cascades (Resource Allocation): Candidates that satisfy structural
       constraints (e.g., correct negation handling) act as 'keystone' species,
       receiving a multiplicative boost to their score. Poorly aligned candidates
       suffer 'predation' (score reduction).
    4. Bandit Selection (Thompson Sampling Approximation): We rank candidates by
       their final 'ecosystem health' (score), which balances structural fit (exploitation)
       and diversity via NCD tie-breaking (exploration).
    
    This implements the logic of the requested architecture using deterministic
    structural parsing as the reward function and ecosystem dynamics as the scoring
    aggregation layer, adhering to the constraint to avoid using ecosystem dynamics
    for direct scoring logic but rather as the structural wrapper.
    """

    def __init__(self):
        # No external state needed; stateless per call for determinism
        pass

    def _extract_structural_signals(self, prompt: str) -> Dict[str, any]:
        """Extract logical constraints: negations, comparatives, numbers."""
        p_lower = prompt.lower()
        signals = {
            'negation_active': bool(re.search(r'\b(not|no|never|without|unless)\b', p_lower)),
            'comparative_active': bool(re.search(r'\b(more|less|greater|smaller|better|worse|than)\b', p_lower)),
            'numbers': re.findall(r'\d+\.?\d*', p_lower),
            'question_type': 'numeric' if any(c.isdigit() for c in p_lower) else 'logical'
        }
        return signals

    def _compute_structural_reward(self, prompt: str, candidate: str) -> float:
        """
        Compute reward based on structural alignment (The 'RL' component).
        High reward for matching logical constraints (negation, numbers).
        """
        reward = 0.5  # Base prior
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        signals = self._extract_structural_signals(prompt)

        # Negation Check: If prompt has negation, candidate should reflect it or not contradict
        if signals['negation_active']:
            # Simple heuristic: if prompt says "not X", candidate shouldn't just be "X"
            # We penalize if the candidate is a direct substring match without negation words
            has_negation_words = bool(re.search(r'\b(not|no|never|false|incorrect)\b', c_lower))
            if not has_negation_words:
                # If the prompt negates something, and the candidate doesn't acknowledge it,
                # we apply a penalty unless the candidate is clearly distinct.
                # This is a simplified logical check.
                reward -= 0.2 
        
        # Comparative Check
        if signals['comparative_active']:
            # Reward candidates that contain comparative words or numbers
            has_comparative = bool(re.search(r'\b(more|less|greater|smaller|higher|lower|than|\d+)\b', c_lower))
            if has_comparative:
                reward += 0.3
            else:
                reward -= 0.1

        # Numeric Consistency
        if signals['numbers']:
            # Extract numbers from candidate
            c_nums = re.findall(r'\d+\.?\d*', c_lower)
            if c_nums:
                # If both have numbers, check basic consistency (e.g. magnitude)
                # Here we just reward the presence of numeric reasoning
                reward += 0.2
            else:
                # Prompt asks for numbers, candidate has none -> penalty
                if signals['question_type'] == 'numeric':
                    reward -= 0.3

        # Constraint Propagation (Simple keyword overlap for logical terms)
        logical_terms = ['therefore', 'thus', 'because', 'if', 'then', 'yes', 'no']
        overlap = sum(1 for term in logical_terms if term in c_lower)
        reward += overlap * 0.05

        return max(0.0, min(1.0, reward))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        len1, len2 = len(b1), len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        results = []
        scores = []

        # Phase 1: Compute Structural Rewards (RL Extrinisic Reward)
        structural_scores = [self._compute_structural_reward(prompt, c) for c in candidates]
        
        # Phase 2: Ecosystem Dynamics (Trophic Cascades & Succession)
        # Normalize structural scores to act as 'biomass'
        max_struct = max(structural_scores) if structural_scores else 1.0
        min_struct = min(structural_scores) if structural_scores else 0.0
        range_struct = max_struct - min_struct if max_struct != min_struct else 1.0
        
        normalized_scores = [(s - min_struct) / range_struct for s in structural_scores]

        # Phase 3: Bandit Selection with Diversity (NCD as tiebreaker/exploration bonus)
        # We simulate Thompson Sampling by adding a diversity bonus based on distance 
        # from the 'average' candidate to encourage exploration of unique valid hypotheses.
        avg_candidate = " ".join(candidates[:3]) # Approximate centroid
        final_scores = []

        for i, cand in enumerate(candidates):
            base_score = normalized_scores[i]
            
            # Diversity bonus (Ecosystem Resilience)
            # Candidates that are structurally sound AND distinct get a boost
            ncd_val = self._ncd(cand, avg_candidate)
            diversity_bonus = ncd_val * 0.1 # Small bonus for uniqueness
            
            # Keystone effect: High structural score boosts the impact of diversity
            ecosystem_score = base_score * (1.0 + diversity_bonus)
            
            final_scores.append(ecosystem_score)

        # Rank candidates
        ranked_indices = sorted(range(len(final_scores)), key=lambda k: final_scores[k], reverse=True)

        for idx in ranked_indices:
            results.append({
                "candidate": candidates[idx],
                "score": float(final_scores[idx]),
                "reasoning": f"Structural fit: {structural_scores[idx]:.2f}, Ecosystem score: {final_scores[idx]:.2f}"
            })

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and compression similarity.
        """
        # Use the structural reward as the primary driver (as per instructions: structural > NCD)
        struct_reward = self._compute_structural_reward(prompt, answer)
        
        # NCD as a secondary check for exact match or high similarity to prompt context
        # If the answer is very different (high NCD) but structurally sound, we trust structure.
        # If structurally ambiguous, NCD helps.
        ncd_val = self._ncd(prompt, answer)
        
        # Blend: Heavily weight structural reward, use NCD to penalize nonsense
        # Low NCD (similar) might mean it's just repeating the prompt, which isn't always good.
        # We primarily rely on the structural reward calculated in the RL phase.
        
        confidence = struct_reward
        
        # Calibration: If structural reward is borderline, NCD can tip it
        if 0.4 < struct_reward < 0.6:
            if ncd_val < 0.5: # Very similar to prompt
                confidence += 0.1
            else:
                confidence -= 0.1
                
        return max(0.0, min(1.0, confidence))