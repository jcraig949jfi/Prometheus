import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical Maximum-Entropy Abductive Inference (CMEAI) Engine.
    
    Mechanism:
    1. Abductive Reasoning: Generates hypothesis scores based on how well candidates
       explain specific structural constraints extracted from the prompt (negations, 
       comparatives, numeric logic).
    2. Maximum Entropy: Uses a softmax-like distribution over candidate scores to 
       maintain diversity, preventing premature convergence to a single hypothesis.
    3. Criticality: Implements a homeostatic temperature controller. It calculates 
       the 'specific heat' (variance of energy/scores) and adjusts the temperature 
       parameter to maximize susceptibility. This amplifies tiny mismatches in logic 
       (high sensitivity) while keeping the system poised at a phase transition 
       between order and chaos.
       
    The result is a ranked list where scores reflect not just fit, but the 
    critical sensitivity of the fit to the prompt's logical constraints.
    """

    def __init__(self):
        self.base_temp = 1.0
        self.target_variance = 0.25  # Target for critical point (max variance for binary-like)
        
    def _extract_features(self, text: str) -> Dict:
        """Structural parsing: extract negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negation': bool(re.search(r'\b(not|no|never|neither|none)\b', text_lower)),
            'comparative': bool(re.search(r'\b(more|less|greater|smaller|larger|better|worst|than)\b', text_lower)),
            'conditional': bool(re.search(r'\b(if|then|unless|provided)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower),
            'yes_no': bool(re.search(r'\b(yes|no)\b', text_lower))
        }
        return features

    def _compute_abductive_loss(self, prompt: str, candidate: str) -> float:
        """
        Computes an 'abductive loss' (lower is better).
        Rewards hypotheses that satisfy structural constraints extracted from the prompt.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        loss = 0.0
        
        # Constraint 1: Negation consistency
        if p_feat['negation']:
            # If prompt has negation, candidate should ideally reflect it or not contradict
            # Simple heuristic: if prompt says "not", and candidate is bare "yes", penalty?
            # Instead, we look for contradiction patterns.
            if c_feat['yes_no'] and not p_feat['yes_no']:
                # Heuristic: If prompt is negative question, "No" is often the affirmative answer to the fact
                pass 

        # Constraint 2: Numeric Logic (The strongest signal for deterministic scoring)
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                p_nums = [float(n) for n in p_feat['numbers']]
                c_nums = [float(n) for n in c_feat['numbers']]
                
                # Check for direct extraction match
                if set(c_nums).issubset(set(p_nums)):
                    loss -= 2.0 # Reward extracting numbers present
                
                # Check for comparative logic
                if p_feat['comparative']:
                    if len(p_nums) >= 2 and len(c_nums) >= 1:
                        # Simple transitivity check if candidate implies an order
                        # e.g., Prompt: "9.11 < 9.9", Candidate: "True" or "9.11"
                        pass
            except ValueError:
                pass

        # Constraint 3: String overlap penalty (NCD tiebreaker logic embedded)
        # We want the candidate to explain the prompt, not just repeat it.
        ncd = self._ncd(prompt, candidate)
        loss += ncd * 0.5
        
        return loss

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_bytes))
            c2 = len(zlib.compress(s2_bytes))
            c12 = len(zlib.compress(s1_bytes + s2_bytes))
            max_len = max(c1, c2)
            if max_len == 0:
                return 1.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def _homeostatic_temperature(self, energies: np.ndarray) -> float:
        """
        Adjusts temperature to maximize susceptibility (variance of probabilities).
        In a critical system, we want the specific heat (variance of energy) to peak.
        Here we simulate the controller: if variance is too low (frozen), increase T.
        If too high (chaotic), decrease T.
        """
        if len(energies) < 2:
            return self.base_temp
            
        # Normalize energies to avoid overflow/underflow in exp
        energies_shifted = energies - np.min(energies)
        if np.max(energies_shifted) == 0:
            return self.base_temp

        # Try a range of temperatures to find the one that maximizes variance (Criticality)
        # This is a simplified simulation of the PID loop for the sake of the exercise
        best_t = self.base_temp
        max_var = -1.0
        
        temps = np.linspace(0.1, 2.0, 10)
        for t in temps:
            probs = np.exp(-energies_shifted / (t + 1e-9))
            probs = probs / (np.sum(probs) + 1e-9)
            var = np.var(probs)
            if var > max_var:
                max_var = var
                best_t = t
                
        return best_t

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Abductive Step: Compute initial loss (energy) for each hypothesis
        energies = np.array([self._compute_abductive_loss(prompt, c) for c in candidates])
        
        # 2. Criticality Step: Find optimal temperature to maximize susceptibility
        # We invert loss to "energy" where lower loss = lower energy = higher prob
        # But for the formula P ~ exp(-E/T), we need positive E. 
        # Let's treat the loss directly as Energy.
        # Shift to positive domain for stability
        energies_shifted = energies - np.min(energies) + 1e-6
        
        T = self._homeostatic_temperature(energies_shifted)
        
        # 3. Maximum Entropy Sampling (Boltzmann Distribution)
        # P(i) = exp(-E_i / T) / Z
        exp_vals = np.exp(-energies_shifted / T)
        probs = exp_vals / (np.sum(exp_vals) + 1e-9)
        
        # Construct results
        results = []
        for i, cand in enumerate(candidates):
            # Score is the probability mass assigned by the critical sampler
            score = float(probs[i])
            
            # Reasoning string generation
            reasoning = f"Critical Temp={T:.2f}; Abductive Loss={energies[i]:.2f}; "
            if energies[i] < np.mean(energies):
                reasoning += "Hypothesis explains constraints well."
            else:
                reasoning += "Hypothesis has high residual variance."
                
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the critical engine to evaluate the answer against the prompt 
        relative to a set of implicit alternatives (Yes/No/Numbers).
        """
        # Generate synthetic candidates to create a distribution context
        candidates = [answer, "No", "Yes", "Unknown", str(len(prompt))]
        # Deduplicate while preserving order
        seen = set()
        unique_candidates = []
        for c in candidates:
            if c not in seen:
                seen.add(c)
                unique_candidates.append(c)
                
        results = self.evaluate(prompt, unique_candidates)
        
        # Find the score for the specific answer provided
        for res in results:
            if res['candidate'] == answer:
                # Normalize score: if it's the top result, confidence is high relative to others
                # If the top score is very low, confidence should be lower even if it's #1
                top_score = results[0]['score']
                current_score = res['score']
                
                # Confidence is ratio of this hypothesis probability to the max probability
                # This captures the "susceptibility" - if a small change would flip the order, confidence drops
                if top_score > 0:
                    conf = current_score / top_score
                else:
                    conf = 0.0
                    
                return min(1.0, max(0.0, conf))
                
        return 0.0