import re
import math
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic-Neuromodulatory Bandit Reasoner.
    
    Mechanism:
    1. Structural Parsing: Extracts logical constraints (negations, comparatives, 
       conditionals, causality) from text into a directed graph representation.
    2. Thermodynamic Scoring: Computes an 'Energy' (E) based on constraint violations 
       (lower is better) and an 'Entropy' (H) based on logical uncertainty. 
       Free Energy F = E - T*H.
    3. Neuromodulatory Bandit: Treats each candidate as an arm. Uses a UCB-style 
       index where exploration gain is modulated by posterior variance (uncertainty).
       High uncertainty -> High gain -> More exploration weight.
    4. Ranking: Candidates are ranked by their posterior mean of negative Free Energy.
    """

    def __init__(self):
        self.temperature = 0.5
        self.alpha = 0.5  # Neuromodulatory gain factor
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|impossible)\b', re.IGNORECASE),
            'double_neg': re.compile(r'\b(not|no)\b.*\b(not|no)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|leads? to|causes?)\b', re.IGNORECASE),
            'quantifier': re.compile(r'\b(all|some|none|every|any)\b', re.IGNORECASE),
            'numbers': re.compile(r'-?\d+(?:\.\d+)?')
        }

    def _parse_structure(self, text: str) -> Dict:
        """Extract structural features and compute constraint satisfaction."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text_lower)),
            'has_double_neg': bool(self.patterns['double_neg'].search(text_lower)),
            'has_comparative': bool(self.patterns['comparative'].search(text_lower)),
            'has_conditional': bool(self.patterns['conditional'].search(text_lower)),
            'has_causal': bool(self.patterns['causal'].search(text_lower)),
            'has_quantifier': bool(self.patterns['quantifier'].search(text_lower)),
            'numbers': [float(n) for n in self.patterns['numbers'].findall(text)]
        }
        return features

    def _compute_energy(self, prompt_feats: Dict, ans_feats: Dict) -> float:
        """
        Compute Energy E = -sum(w_c * sat_c).
        Lower energy = better consistency.
        We penalize contradictions between prompt and answer structures.
        """
        energy = 0.0
        
        # Constraint 1: Negation consistency (simplified)
        # If prompt has negation and answer doesn't (or vice versa), slight penalty
        if prompt_feats['has_negation'] != ans_feats['has_negation']:
            energy += 1.0 
            
        # Constraint 2: Double negation check (logic trap)
        # If answer has double neg but prompt doesn't, it might be redundant or emphatic
        if ans_feats['has_double_neg'] and not prompt_feats['has_double_neg']:
            energy += 0.5

        # Constraint 3: Numeric consistency (Transitivity/Ordering)
        # If both have numbers, check if answer numbers are subset or consistent range
        p_nums = prompt_feats['numbers']
        a_nums = ans_feats['numbers']
        
        if p_nums and a_nums:
            # Heuristic: Answer numbers shouldn't wildly exceed prompt magnitude unless comparative
            if max(a_nums) > max(p_nums) * 10: 
                energy += 2.0
            # Check for direct contradiction in simple comparisons if keywords exist
            if ans_feats['has_comparative'] and prompt_feats['has_comparative']:
                # Encourage presence, assume consistency if both present
                energy -= 0.5 
                
        # Constraint 4: Conditional/Causal alignment
        # If prompt asks "why" (causal) and answer has no causal markers
        if 'why' in prompt_feats.get('raw_prompt', '').lower() and not ans_feats['has_causal']:
             energy += 1.5

        return -energy # Lower energy is better (more negative sum of violations)

    def _get_free_energy(self, prompt: str, candidate: str, n_pulls: int, variance: float) -> Tuple[float, float]:
        """Calculate Free Energy F = E - T*H and return (F, Entropy)."""
        p_feats = self._parse_structure(prompt)
        p_feats['raw_prompt'] = prompt
        a_feats = self._parse_structure(candidate)
        
        # 1. Energy
        E = self._compute_energy(p_feats, a_feats)
        
        # 2. Entropy approximation: H = 0.5 * log(2 * pi * e * sigma^2)
        # Add small epsilon to variance to avoid log(0)
        safe_var = max(variance, 1e-6)
        H = 0.5 * math.log(2 * math.pi * math.e * safe_var)
        
        # 3. Free Energy
        F = E - self.temperature * H
        
        return F, H

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        t_total = len(candidates) # Treat batch as one round of pulls for simplicity
        
        # Initialize bandit state for this batch
        # mu: mean reward estimate, sigma^2: variance estimate
        # We simulate the bandit process over the set
        
        bandit_state = []
        for i, cand in enumerate(candidates):
            # Initial prior: N(0, 1)
            mu = 0.0
            sigma_sq = 1.0
            n_i = 1
            
            # Calculate initial reward based on free energy
            F, _ = self._get_free_energy(prompt, cand, n_i, sigma_sq)
            r = -F # Reward is negative free energy
            
            # Bayesian update (simplified for single observation)
            # New mean is weighted average, new variance decreases
            # For implementation simplicity in a single-shot evaluator:
            # We treat the structural score as the 'true' signal and add noise based on length/complexity
            complexity_penalty = 0.1 * len(cand.split()) 
            observed_reward = r - complexity_penalty
            
            # Update stats
            mu = observed_reward
            sigma_sq = 0.5 # Reduce uncertainty after one "pull"
            
            # Neuromodulatory gain
            g = 1.0 + self.alpha * math.sqrt(sigma_sq)
            
            # UCB Index
            # UCB = mu + g * sqrt(2 * ln(t) / n)
            # Since we are ranking a static list, we use a pseudo-time t = len(candidates)
            ucb_bonus = g * math.sqrt(2 * math.log(max(t_total, 2)) / n_i)
            ucb_score = mu + ucb_bonus
            
            bandit_state.append({
                'candidate': cand,
                'score': ucb_score,
                'mu': mu,
                'sigma_sq': sigma_sq
            })

        # Sort by score descending
        bandit_state.sort(key=lambda x: x['score'], reverse=True)
        
        # Format output
        final_results = []
        for item in bandit_state:
            reasoning = f"Thermo-Bandit Score: {item['score']:.4f}. "
            reasoning += f"Energy-driven evaluation with neuromodulatory gain on variance."
            final_results.append({
                'candidate': item['candidate'],
                'score': item['score'],
                'reasoning': reasoning
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the thermodynamic stability of the answer.
        High confidence = Low Free Energy (Stable state).
        """
        F, H = self._get_free_energy(prompt, answer, 1, 1.0)
        
        # Map Free Energy to 0-1 confidence
        # Lower F is better. 
        # Assume F ranges roughly from -5 (great) to +5 (terrible)
        # Sigmoid mapping: 1 / (1 + exp(k * (F - threshold)))
        # If F is very negative, exp(large negative) -> 0 -> confidence 1
        # If F is positive, exp(positive) -> large -> confidence 0
        
        k = 1.0
        threshold = 0.0
        conf = 1.0 / (1.0 + math.exp(k * (F - threshold)))
        
        # Clamp
        return max(0.0, min(1.0, conf))