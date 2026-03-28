import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hierarchical Predictive-Coding Controller with Oscillatory Bandit Policy.
    
    Mechanism:
    1. Free Energy Principle (Core): The 'score' is an inverse measure of variational 
       free energy (surprise). We minimize free energy by maximizing structural consistency 
       between the prompt's logical constraints and the candidate's assertions.
    2. Neural Oscillations (Confidence Wrapper): Per causal analysis, oscillatory concepts 
       are restricted to the confidence() method. We simulate Theta-Gamma coupling where 
       Theta (slow wave) modulates the exploration rate (uncertainty) and Gamma (fast burst) 
       represents the precision of the match. High precision (low error) yields high confidence.
    3. Multi-Armed Bandit (Selection): We treat candidate selection as a Thompson Sampling 
       problem. The 'reward' is the structural match score. The system 'exploits' the 
       candidate with the highest expected reward (lowest free energy) while using the 
       oscillatory confidence to gauge if 'exploration' (rejecting all/uncertainty) is needed.
    4. Structural Parsing: We explicitly extract negations, comparatives, and numeric values 
       to compute the prediction error (mismatch) rather than relying on string similarity.
    """

    def __init__(self):
        self.epsilon_base = 0.1  # Base exploration rate
        self.precision_gamma = 1.0  # Precision scaling factor

    def _structural_parse(self, text: str) -> dict:
        """Extract logical primitives: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower),
            'length': len(text.split())
        }
        # Convert numbers to float for comparison
        try:
            features['numeric_vals'] = [float(n) for n in features['numbers']]
        except ValueError:
            features['numeric_vals'] = []
        return features

    def _compute_free_energy(self, prompt: str, candidate: str) -> float:
        """
        Compute variational free energy (F) as a proxy for prediction error.
        F = Complexity - Accuracy (simplified). 
        Lower F is better. We invert this for scoring later.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        error = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negation, candidate should ideally reflect it or not contradict
        if p_feat['negations'] > 0:
            # Penalty if candidate ignores negation context entirely (simple heuristic)
            if c_feat['negations'] == 0 and p_feat['negations'] > 1:
                error += 0.5 * p_feat['negations']
        
        # 2. Numeric Consistency
        if p_feat['numeric_vals'] and c_feat['numeric_vals']:
            # Check if relative order is preserved or if values match
            p_nums = sorted(p_feat['numeric_vals'])
            c_nums = sorted(c_feat['numeric_vals'])
            
            # Simple transitivity check: does the candidate contain numbers from prompt?
            # Or if it introduces new numbers, is it logically consistent? 
            # Heuristic: Penalty for completely disjoint numeric ranges if prompt has specific constraints
            if len(p_nums) == len(c_nums):
                for p, c in zip(p_nums, c_nums):
                    error += abs(p - c) * 0.1
            else:
                # Mismatch in count implies potential error unless logical operator changes it
                error += 0.2 * abs(len(p_nums) - len(c_nums))

        # 3. Conditional/Logical Flow
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] == 0:
                # Candidate might be answering the condition, so not always an error
                # But if prompt is complex conditional and answer is too short, likely error
                if c_feat['length'] < p_feat['length'] * 0.2:
                    error += 0.3

        # 4. NCD as Tiebreaker (only adds small amount to error if structural signals are weak)
        # We use NCD only when structural features are ambiguous
        structural_signal = p_feat['negations'] + p_feat['comparatives'] + p_feat['conditionals']
        if structural_signal == 0:
            try:
                combined = (prompt + candidate).encode('utf-8')
                comp_both = len(zlib.compress(combined))
                comp_c = len(zlib.compress(candidate.encode('utf-8')))
                comp_p = len(zlib.compress(prompt.encode('utf-8')))
                ncd = (comp_both - min(comp_p, comp_c)) / max(comp_p, comp_c) if max(comp_p, comp_c) > 0 else 1.0
                error += ncd * 0.1 # Low weight tiebreaker
            except:
                error += 0.5

        return error

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluate candidates using Free Energy minimization.
        Returns ranked list by score (higher is better).
        """
        if not candidates:
            return []
            
        results = []
        free_energies = []
        
        # Phase 1: Compute Free Energy (Prediction Error) for all hypotheses
        for cand in candidates:
            fe = self._compute_free_energy(prompt, cand)
            free_energies.append(fe)
        
        # Phase 2: Convert Free Energy to Score (Precision-weighted)
        # Score = exp(-F) normalized. Lower F -> Higher Score.
        # Add small epsilon to avoid division by zero if all FE are 0
        min_fe = min(free_energies)
        max_fe = max(free_energies) if len(free_energies) > 1 else min_fe + 1.0
        
        scores = []
        for fe in free_energies:
            # Normalize FE to 0-1 range roughly, then invert
            # Using a soft-max like approach on negative free energy
            raw_score = math.exp(-fe * 2.0) 
            scores.append(raw_score)
            
        # Normalize scores to 0-1
        sum_scores = sum(scores) + 1e-9
        normalized_scores = [s / sum_scores for s in scores]
        
        # Phase 3: Thompson Sampling Analogue (Exploration-Exploitation)
        # We add noise proportional to uncertainty (variance in scores) to simulate 
        # the bandit sampling. High uncertainty -> higher noise (Theta modulation).
        import random
        variance = 0.0
        if len(normalized_scores) > 1:
            mean_s = sum(normalized_scores) / len(normalized_scores)
            variance = sum((s - mean_s)**2 for s in normalized_scores) / len(normalized_scores)
        
        final_results = []
        for i, cand in enumerate(candidates):
            # Sample from posterior (approximated by adding noise to score)
            noise = random.gauss(0, math.sqrt(variance) * 0.1) if variance > 0 else 0
            sampled_score = normalized_scores[i] + noise
            sampled_score = max(0.0, min(1.0, sampled_score)) # Clamp
            
            final_results.append({
                "candidate": cand,
                "score": sampled_score,
                "reasoning": f"Free Energy: {free_energies[i]:.4f}, Structural Match: {'High' if free_energies[i] < 0.5 else 'Low'}"
            })
            
        # Rank by score descending
        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Compute confidence using Oscillatory Analogy (Theta-Gamma Coupling).
        Theta (slow): Global uncertainty based on structural complexity.
        Gamma (fast): Local precision of the match.
        Confidence = Gamma Precision * (1 - Theta Uncertainty)
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(answer)
        
        # Gamma: Instantaneous likelihood (Precision of match)
        # Based on inverse free energy of this specific pair
        fe = self._compute_free_energy(prompt, answer)
        gamma_precision = math.exp(-fe * 2.0) # High precision if FE is low
        
        # Theta: Meta-exploration envelope (Uncertainty)
        # Driven by complexity of the prompt (more conditions/negations = higher uncertainty)
        complexity = p_feat['negations'] + p_feat['conditionals'] + (len(p_feat['numbers']) * 0.5)
        theta_uncertainty = 1.0 - math.exp(-complexity * 0.3) # Sigmoidal rise with complexity
        
        # Coupling: Confidence is high only if precision is high AND uncertainty is managed
        # If theta (uncertainty) is too high, it dampens the effective confidence unless gamma is extremely strong
        raw_conf = gamma_precision * (1.0 - 0.5 * theta_uncertainty)
        
        return float(max(0.0, min(1.0, raw_conf)))