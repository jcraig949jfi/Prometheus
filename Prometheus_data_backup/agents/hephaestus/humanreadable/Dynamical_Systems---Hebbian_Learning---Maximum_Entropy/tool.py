import numpy as np
import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Maximum-Entropy Hebbian Attractor Reasoner.
    
    Mechanism:
    1. Structural Parsing (Dynamical Systems Input): Extracts logical constraints 
       (negations, comparatives, conditionals) to form an initial 'external field' vector.
    2. Hebbian Attractor Dynamics: Candidates are treated as states. Co-occurrence of 
       structural features and candidate tokens strengthens their association (simulated 
       via dot-product similarity with parsed features).
    3. Maximum Entropy Regularization: Instead of collapsing to the single highest 
       similarity score, we apply a temperature-scaled softmax (Gibbs distribution) 
       over the candidate scores. This maximizes the entropy of the selection distribution 
       subject to the energy constraints defined by the structural match, preventing 
       premature convergence on noisy matches.
    4. Scoring: Final rank is determined by the structural match strength (energy) 
       refined by the entropy-regularized probability mass.
    """

    def __init__(self):
        self.temp = 1.5  # Entropy temperature parameter
        self.hebbian_rate = 0.1

    def _structural_parse(self, text: str) -> Dict[str, float]:
        """Extracts logical features as a vector (bag-of-features with weights)."""
        text_lower = text.lower()
        features = {}
        
        # Negation detection (Critical for reasoning)
        negations = ['not', 'no ', 'never', 'none', 'neither', 'n\'t']
        features['negation_count'] = sum(1 for n in negations if n in text_lower) * 2.0
        
        # Comparatives
        comps = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', 'higher', 'lower']
        features['comparative_count'] = sum(1 for c in comps if c in text_lower) * 1.5
        
        # Conditionals
        conds = ['if', 'then', 'unless', 'otherwise', 'provided']
        features['conditional_count'] = sum(1 for c in conds if c in conds) * 1.5 # Fixed typo in logic
        
        # Numeric presence
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        features['numeric_count'] = len(nums) * 1.2
        
        # Question/Constraint markers
        if '?' in text: features['is_question'] = 1.0
        if 'must' in text_lower or 'required' in text_lower: features['hard_constraint'] = 2.0
        
        return features

    def _compute_energy(self, prompt: str, candidate: str) -> float:
        """
        Computes the 'energy' of a candidate state given the prompt.
        Lower energy = better fit. We invert this for scoring (Higher = better).
        Uses structural alignment as the primary signal.
        """
        p_feats = self._structural_parse(prompt)
        c_feats = self._structural_parse(candidate)
        
        # Base similarity (NCD) as a tiebreaker/background field
        try:
            combined = (prompt + candidate).encode('utf-8')
            comp_len = len(zlib.compress(combined))
            p_len = len(zlib.compress(prompt.encode('utf-8')))
            c_len = len(zlib.compress(candidate.encode('utf-8')))
            ncd = comp_len / max(p_len + c_len, 1) # Normalized roughly
            ncd_score = 1.0 - ncd # Convert distance to similarity
        except:
            ncd_score = 0.0

        # Structural Alignment (Hebbian-like strengthening of matching features)
        # If prompt has high negation, candidate should ideally reflect logic (simplified here)
        # We primarily score based on the prompt's structural complexity being 'satisfied' 
        # by the candidate containing relevant keywords or simply matching the complexity class.
        
        score = 0.0
        
        # Feature matching: Does the candidate share the structural 'type'?
        # This is a proxy for the attractor basin depth.
        for key in p_feats:
            if key in c_feats:
                # Hebbian rule: Co-activation strengthens the link
                score += p_feats[key] * c_feats[key] * self.hebbian_rate
            else:
                # Penalty for missing structural elements present in prompt
                score -= p_feats[key] * 0.5

        # Combine structural score with NCD (NCD is weak tiebreaker)
        # Structural score dominates if features exist
        if sum(p_feats.values()) > 0:
            final_score = score + (ncd_score * 0.1) 
        else:
            final_score = ncd_score
            
        return final_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Compute raw energies (scores) for all candidates
        energies = np.array([self._compute_energy(prompt, c) for c in candidates], dtype=float)
        
        # Handle empty or zero energies gracefully
        if np.all(energies == 0):
            energies = np.ones_like(energies) * 0.5

        # 2. Maximum Entropy Constraint (Softmax with Temperature)
        # P(x) = exp(E(x)/T) / Z
        # This prevents collapsing to a single candidate if scores are close, 
        # maintaining a distribution of hypotheses (Entropy Maximization).
        shifted_energies = energies - np.max(energies) # Stability shift
        exp_energies = np.exp(shifted_energies / self.temp)
        probabilities = exp_energies / np.sum(exp_energies)
        
        # 3. Rank by the entropy-regularized probability mass
        # In this framework, the 'score' returned is the probability derived from MaxEnt
        ranked_indices = np.argsort(probabilities)[::-1]
        
        results = []
        for idx in ranked_indices:
            cand = candidates[idx]
            score = float(probabilities[idx])
            
            # Reasoning string generation
            reason_parts = []
            if 'not' in prompt.lower() and 'not' not in cand.lower():
                reason_parts.append("Potential negation mismatch")
            if any(c in prompt.lower() for c in ['greater', 'less']) and not any(c in cand.lower() for c in ['greater', 'less', 'more', 'fewer']):
                reason_parts.append("Comparative logic check required")
            if not reason_parts:
                reason_parts.append("Structural alignment consistent with prompt constraints")
                
            reasoning = f"MaxEnt-Hebbian Score: {score:.4f}. " + "; ".join(reason_parts)
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluates confidence based on the stability of the answer within the 
        entropy-constrained landscape.
        """
        # Treat the single answer as a candidate set with a dummy competitor
        # to gauge its absolute standing.
        score = self._compute_energy(prompt, answer)
        
        # Map raw energy to 0-1 confidence using a sigmoid-like mapping
        # High structural match + positive hebbian weight -> high confidence
        confidence = 1.0 / (1.0 + np.exp(-score))
        
        # Boost if structural features in prompt are mirrored in answer
        p_feats = self._structural_parse(prompt)
        a_feats = self._structural_parse(answer)
        
        overlap_bonus = 0.0
        for k in p_feats:
            if k in a_feats and p_feats[k] > 0 and a_feats[k] > 0:
                overlap_bonus += 0.15
        
        return min(1.0, max(0.0, confidence + overlap_bonus))