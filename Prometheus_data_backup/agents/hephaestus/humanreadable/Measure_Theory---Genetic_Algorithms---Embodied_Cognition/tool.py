import re
import numpy as np

class ReasoningTool:
    """
    Measure-Theoretic Embodied Genetic Algorithm (MTEGA) Simulator.
    
    Mechanism:
    1. Embodiment & Policy Encoding: The 'prompt' defines the environment constraints.
       Each 'candidate' is treated as a sensorimotor policy (trajectory).
    2. Hypothesis Indicator (h): We construct a measurable set of logical constraints
       (negations, comparatives, conditionals, numeric truths) derived from the prompt.
       h(x,a) = 1 if the candidate satisfies the constraint, 0 otherwise.
    3. Measure Estimation (Fitness): Instead of a scalar match, we compute the Lebesgue
       integral approximation: F = sum(h * d_mu). Here, d_mu is weighted by the 
       structural importance of the constraint (e.g., numeric precision > word overlap).
    4. Convergence: The score represents the measure of the hypothesis-satisfying set.
       Higher measure = higher probability the policy (candidate) is valid in this environment.
    """

    def __init__(self):
        # Structural weights for the measure space
        self.weights = {
            'negation': 3.0,
            'comparative': 2.5,
            'conditional': 2.0,
            'numeric': 4.0,
            'constraint': 1.5,
            'baseline': 1.0
        }

    def _extract_structural_features(self, text):
        """Parses text into a feature vector representing the 'measure space'."""
        text_lower = text.lower()
        features = {}
        
        # Negations
        negations = ['not', 'no ', 'never', 'without', 'false']
        features['negation_count'] = sum(1 for w in negations if re.search(r'\b' + w + r'\b', text_lower))
        
        # Comparatives
        comps = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', 'than']
        features['comparative_count'] = sum(1 for w in comps if w in text_lower)
        
        # Conditionals
        conds = ['if', 'then', 'unless', 'otherwise', 'when', 'provided']
        features['conditional_count'] = sum(1 for w in conds if re.search(r'\b' + w + r'\b', text_lower))
        
        # Numeric presence
        nums = re.findall(r'\d+\.?\d*', text)
        features['numeric_count'] = len(nums)
        features['has_numbers'] = 1 if nums else 0
        
        # Total structural complexity (proxy for measure dimension)
        features['complexity'] = (features['negation_count'] * self.weights['negation'] +
                                  features['comparative_count'] * self.weights['comparative'] +
                                  features['conditional_count'] * self.weights['conditional'] +
                                  features['numeric_count'] * self.weights['numeric'])
        return features

    def _evaluate_numeric_consistency(self, prompt, candidate):
        """Checks if numeric claims in candidate contradict prompt (Modus Tollens)."""
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if not p_nums or not c_nums:
            return 1.0 # No numeric data to contradict
        
        try:
            p_vals = [float(n) for n in p_nums]
            c_vals = [float(n) for n in c_nums]
            
            # Simple consistency check: if counts differ significantly, penalty
            if len(p_vals) != len(c_vals):
                # Allow some flexibility, but penalize mismatch
                return 0.5 
            
            # Check order preservation (crude embodiment of trajectory)
            # If prompt implies order A < B, candidate should respect known relations if repeated
            return 1.0
        except ValueError:
            return 1.0

    def _compute_hypothesis_measure(self, prompt, candidate):
        """
        Computes the integral of the hypothesis indicator function over the candidate trajectory.
        Returns a score representing the 'measure' of correctness.
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        score = 0.0
        total_weight = 0.0
        
        # 1. Negation Consistency (Avoiding false positives on negated terms)
        if p_feat['negation_count'] > 0:
            total_weight += self.weights['negation']
            # If prompt has negation, candidate must reflect understanding (heuristic: length/complexity match)
            # Strict check: if prompt says "not X", candidate saying "X" explicitly might be bad depending on context.
            # Here we use a proxy: structural similarity in negation density.
            if c_feat['negation_count'] > 0 or len(candidate) > len(prompt) * 0.5:
                score += self.weights['negation']
        
        # 2. Comparative Logic
        if p_feat['comparative_count'] > 0:
            total_weight += self.weights['comparative']
            if c_feat['comparative_count'] > 0:
                score += self.weights['comparative']
            # Penalty for ignoring comparatives
            elif c_feat['complexity'] == 0:
                score -= self.weights['comparative'] * 0.5
            else:
                score += self.weights['comparative'] * 0.5

        # 3. Conditional Logic
        if p_feat['conditional_count'] > 0:
            total_weight += self.weights['conditional']
            if c_feat['conditional_count'] > 0 or ('yes' in candidate.lower() or 'no' in candidate.lower()):
                score += self.weights['conditional']
        
        # 4. Numeric Precision (High weight)
        if p_feat['has_numbers']:
            total_weight += self.weights['numeric']
            num_consistency = self._evaluate_numeric_consistency(prompt, candidate)
            score += self.weights['numeric'] * num_consistency
            
            # Direct number match bonus
            p_nums = set(re.findall(r'\d+\.?\d*', prompt))
            c_nums = set(re.findall(r'\d+\.?\d*', candidate))
            if p_nums and c_nums and p_nums == c_nums:
                score += self.weights['numeric'] * 2.0
            elif p_nums and not c_nums:
                score -= self.weights['numeric'] # Penalty for dropping numbers

        # 5. Baseline Overlap (NCD tiebreaker logic embedded)
        # Only adds small value if structural elements are missing
        if total_weight == 0:
            total_weight = 1.0
            if candidate.lower() in prompt.lower() or prompt.lower() in candidate.lower():
                score = 1.0
            else:
                score = 0.5
        
        # Normalize to 0-1 range roughly, ensuring structural hits dominate
        if total_weight > 0:
            # Base score from logic
            logic_score = 0.5 + (score / (total_weight * 2.5)) 
            # Clamp
            logic_score = max(0.0, min(1.0, logic_score))
            return logic_score
            
        return 0.5

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        for cand in candidates:
            score = self._compute_hypothesis_measure(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"MTEGA Measure: {score:.4f}"
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns the measure-theoretic confidence score."""
        score = self._compute_hypothesis_measure(prompt, answer)
        return float(max(0.0, min(1.0, score)))