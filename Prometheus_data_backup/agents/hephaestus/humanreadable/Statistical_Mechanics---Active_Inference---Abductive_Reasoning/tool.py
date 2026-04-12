import math
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Annealed Particle-Based Active Abductive Inference Engine (APA-AIE) Approximation.
    
    Mechanism:
    1. Abductive Hypothesis Generation: Treats each candidate as a particle representing a 
       hypothesis about the world state implied by the prompt.
    2. Statistical Mechanics Energy: Computes an energy E(h) = -log(Likelihood) - lambda*log(Prior).
       - Likelihood: Structural match to prompt constraints (negations, comparatives, logic).
       - Prior: Simplicity bias (compression length) and semantic coherence (keyword overlap).
    3. Simulated Annealing: Applies a temperature-scaled Boltzmann weight to scores. 
       This allows the system to be less sensitive to noise in short prompts (high T) 
       and strictly discriminative for clear logical matches (low T).
    4. Active Inference Proxy: The 'confidence' score acts as the expected free energy minimization,
       measuring how much the candidate reduces uncertainty relative to the prompt's constraints.
    """

    def __init__(self):
        # Annealing schedule parameters
        self.beta_start = 0.5
        self.beta_end = 5.0
        self.lambda_complexity = 0.1
        
        # Structural keywords for abductive constraint checking
        self.negations = ['no', 'not', 'never', 'none', 'cannot', "n't"]
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.logic_ops = ['if', 'then', 'else', 'therefore', 'because', 'unless']

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0: return 1.0
        return (c12 - min(c1, c2)) / denom

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Structural parsing for negations, numbers, and logic."""
        lower_text = text.lower()
        words = lower_text.split()
        
        has_negation = any(n in words for n in self.negations)
        has_comparative = any(c in words for c in self.comparatives)
        has_logic = any(l in words for l in self.logic_ops)
        
        # Numeric extraction
        numbers = []
        for w in words:
            clean_w = ''.join(c for c in w if c.isdigit() or c == '.')
            if clean_w:
                try:
                    numbers.append(float(clean_w))
                except ValueError:
                    pass
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'logic': has_logic,
            'numbers': numbers,
            'length': len(text),
            'word_set': set(words)
        }

    def _compute_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes energy E(h) = -log(Likelihood) - lambda*log(Prior).
        Lower energy = better hypothesis.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        # 1. Likelihood Term: Constraint Satisfaction
        # Penalize mismatched structural features (Active Inference: minimizing surprise)
        likelihood_penalty = 0.0
        
        # Negation consistency check (simplified)
        if p_feat['negation'] != c_feat['negation']:
            # If prompt has negation and candidate doesn't (or vice versa), high penalty
            # unless the candidate is explicitly denying something (heuristic)
            likelihood_penalty += 2.0
            
        # Number consistency (if prompt has numbers, candidate should likely relate)
        if p_feat['numbers'] and c_feat['numbers']:
            # Check for transitivity or direct match if only one number exists
            if len(p_feat['numbers']) == 1 and len(c_feat['numbers']) == 1:
                if abs(p_feat['numbers'][0] - c_feat['numbers'][0]) > 1e-6:
                    # Allow some tolerance for unit conversion logic not implemented here
                    likelihood_penalty += 0.5 
        elif p_feat['numbers'] and not c_feat['numbers']:
            # Candidate ignores numeric data
            likelihood_penalty += 1.0

        # Logical operator presence
        if p_feat['logic'] and not c_feat['logic']:
            likelihood_penalty += 0.5

        # 2. Prior Term: Simplicity (MDL)
        # Shorter explanations are preferred (Occam's razor)
        complexity_cost = self.lambda_complexity * len(candidate)
        
        # 3. Semantic Overlap (Abductive Prior)
        # Candidates sharing specific non-stopwords with prompt are more likely
        common_words = p_feat['word_set'].intersection(c_feat['word_set'])
        # Remove generic stop words from consideration for bonus
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'to', 'of', 'and', 'in', 'that', 'for', 'on', 'it', 'with', 'as', 'at', 'by', 'this', 'which'}
        meaningful_overlap = len([w for w in common_words if w not in stop_words])
        prior_bonus = -0.3 * meaningful_overlap # Reduces energy

        energy = likelihood_penalty + complexity_cost + prior_bonus
        return energy

    def _anneal_score(self, energy: float, beta: float) -> float:
        """Convert energy to probability-like score via Boltzmann distribution."""
        # w ~ exp(-beta * E)
        # Clamp energy to avoid overflow
        clipped_e = max(-100, min(100, energy))
        return math.exp(-beta * clipped_e)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        # Determine beta based on prompt complexity (Adaptive Annealing)
        # More complex prompts (more constraints) -> Higher beta (sharper selection)
        p_feat = self._extract_features(prompt)
        constraint_count = sum([p_feat['negation'], p_feat['comparative'], p_feat['logic'], len(p_feat['numbers'])])
        beta = self.beta_start + (self.beta_end - self.beta_start) * (constraint_count / 5.0)
        beta = min(beta, self.beta_end)

        results = []
        energies = []
        
        # Phase 1: Compute Energies for all particles (candidates)
        for cand in candidates:
            e = self._compute_energy(prompt, cand)
            energies.append(e)
        
        # Phase 2: Boltzmann Weighting (Annealing)
        # Shift energies so max is 0 for numerical stability before exp
        if energies:
            min_e = min(energies)
            shifted_energies = [e - min_e for e in energies]
        else:
            shifted_energies = energies
            
        weights = [self._anneal_score(e, beta) for e in shifted_energies]
        
        # Normalize weights to 0-1 range for scoring
        max_w = max(weights) if weights else 1.0
        min_w = min(weights) if weights else 0.0
        range_w = max_w - min_w if max_w != min_w else 1.0
        
        for i, cand in enumerate(candidates):
            # Normalize score to 0-1
            norm_score = (weights[i] - min_w) / range_w
            
            # Add NCD as a tie-breaker/secondary signal (as per successful patterns)
            ncd_val = self._compute_ncd(prompt, cand)
            # Adjust score slightly by NCD (lower NCD is better, so subtract)
            # But keep primary logic dominant
            final_score = 0.8 * norm_score + 0.2 * (1.0 - ncd_val)
            
            # Generate reasoning string
            reasoning = f"Energy={energies[i]:.2f}, Beta={beta:.2f}. "
            if p_feat['negation'] and not self._extract_features(cand)['negation']:
                reasoning += "Warning: Negation mismatch detected. "
            if p_feat['numbers'] and not self._extract_features(cand)['numbers']:
                reasoning += "Warning: Numeric data ignored. "
            if not reasoning.endswith(". "):
                reasoning += "Structural alignment verified."

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the normalized Boltzmann weight 
        of the single candidate against a null hypothesis (empty string).
        """
        # Evaluate against a dummy set to get relative scoring
        # We compare the answer against a 'random' alternative to gauge separation
        candidates = [answer, ""] 
        ranked = self.evaluate(prompt, candidates)
        
        if not ranked:
            return 0.0
            
        # If the answer is the top result, its score is our confidence proxy
        if ranked[0]['candidate'] == answer:
            # Scale the score: if it's significantly better than the alternative, score is high
            base_score = ranked[0]['score']
            # Boost if it's the clear winner
            if len(ranked) > 1 and base_score > ranked[1]['score']:
                return min(1.0, 0.5 + 0.5 * base_score)
            return float(base_score)
        else:
            # If a blank string or something else scored higher, confidence is low
            return float(ranked[0]['score'] * 0.5)