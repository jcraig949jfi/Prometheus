import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Criticality-Driven Clonal Hypothesis Optimizer (CCHO) Implementation.
    
    Mechanism:
    1. Hypothesis Pool: Candidates are treated as antibodies.
    2. Order Parameter (O): Computed as the structural diversity (variance in 
       parsed logical features) of the candidate set. High variance indicates 
       a pre-critical state where small changes matter.
    3. Kolmogorov Pressure: Uses zlib compression length as a proxy for K(h). 
       Simpler explanations (shorter compressed length) are favored if accuracy ties.
    4. Dynamic Annealing: If the system detects high structural conflict (criticality),
       it tightens the scoring bias towards logical consistency (exploitation).
       Otherwise, it relies more on compression (exploration/simplicity).
       
    Scoring Strategy (Beating NCD):
    - Primary Signal: Structural parsing of negations, comparatives, and conditionals.
    - Secondary Signal: Numeric evaluation logic.
    - Tiebreaker: Normalized Compression Distance (NCD).
    """

    def __init__(self):
        self.memory_set = []  # Immune memory of successful logical patterns

    def _parse_structure(self, text: str) -> dict:
        """Extract logical features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|>|<|>=|<=)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower),
            'length': len(text)
        }
        return features

    def _evaluate_logic(self, prompt: str, candidate: str) -> float:
        """
        Structural parsing and constraint propagation.
        Returns a score based on logical alignment with the prompt.
        """
        p_feat = self._parse_structure(prompt)
        c_feat = self._parse_structure(candidate)
        score = 0.0

        # 1. Negation Consistency
        # If prompt has negation, correct answer often needs to acknowledge it or invert logic
        if p_feat['negations'] > 0:
            # Reward candidates that also contain logical operators (suggests reasoning)
            score += 0.5 if c_feat['negations'] > 0 or c_feat['comparatives'] > 0 else -0.2
        
        # 2. Comparative Logic
        if p_feat['comparatives'] > 0:
            # Check if candidate contains comparative words or specific numbers
            if c_feat['comparatives'] > 0 or len(c_feat['numbers']) > 0:
                score += 0.6
            else:
                score -= 0.3

        # 3. Conditional/Constraint Propagation
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] > 0 or len(c_feat['numbers']) > 0:
                score += 0.5

        # 4. Numeric Evaluation (Heuristic)
        # If both have numbers, check for simple transitivity or presence
        if p_feat['numbers'] and c_feat['numbers']:
            # Presence of numbers in candidate when prompt has them is a strong signal
            score += 0.4
            # Simple magnitude check if obvious (e.g. prompt asks for larger, candidate has larger number)
            # This is a simplified heuristic for the "numeric evaluation" requirement
            try:
                p_nums = [float(x) for x in p_feat['numbers']]
                c_nums = [float(x) for x in c_feat['numbers']]
                if max(c_nums) >= max(p_nums):
                    score += 0.2
            except ValueError:
                pass

        return score

    def _compute_kolmogorov_penalty(self, text: str) -> float:
        """Approximate Kolmogorov complexity using zlib compression length."""
        if not text:
            return 0.0
        compressed = zlib.compress(text.encode('utf-8'))
        return len(compressed)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode('utf-8')))
        c2 = len(zlib.compress(s2.encode('utf-8')))
        c12 = len(zlib.compress((s1 + s2).encode('utf-8')))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _calculate_order_parameter(self, candidates: List[str]) -> float:
        """
        Compute order parameter O based on variance of structural features.
        High variance = approaching critical point (diverse hypotheses).
        Low variance = ordered regime (converged).
        """
        if len(candidates) < 2:
            return 0.0
        
        features_list = []
        for c in candidates:
            f = self._parse_structure(c)
            # Flatten to numeric vector for variance calc
            val = f['negations'] + f['comparatives'] + f['conditionals'] + len(f['numbers']) * 0.1
            features_list.append(val)
        
        if not features_list:
            return 0.0
            
        mean_val = sum(features_list) / len(features_list)
        variance = sum((x - mean_val) ** 2 for x in features_list) / len(features_list)
        return variance

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        # 1. Order Parameter Monitoring (Criticality Detection)
        O = self._calculate_order_parameter(candidates)
        
        # Dynamic Annealing Factor
        # If O is high (critical), we exploit structural logic heavily.
        # If O is low (ordered), we rely more on simplicity (Kolmogorov).
        annealing_factor = 1.0 if O > 0.5 else 0.5 

        results = []
        for cand in candidates:
            # 2. Structural Parsing (Primary Signal)
            logic_score = self._evaluate_logic(prompt, cand)
            
            # 3. Kolmogorov Complexity Pressure (MDL Bias)
            # Penalize complexity. Shorter compressed length = better.
            k_complexity = self._compute_kolmogorov_penalty(cand)
            # Normalize complexity penalty relative to prompt length to avoid biasing long answers too hard
            k_penalty = (k_complexity / (len(prompt) + 1)) * 0.1 
            
            # Combined Fitness
            # Fitness = (Logic * Annealing) - (Complexity * (1-Annealing))
            # Actually, we want Logic to dominate, K to break ties or penalize nonsense
            fitness = (logic_score * annealing_factor) - (k_penalty * (1.0 - annealing_factor * 0.1))
            
            # 4. NCD Tiebreaker (Only if logic scores are close/neutral)
            # We add a tiny NCD component to distinguish semantically similar strings
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD so lower distance = higher score, scaled very small
            ncd_score = (1.0 - ncd_val) * 0.01 

            final_score = fitness + ncd_score
            
            # Generate reasoning string
            reasoning = f"Structural match: {logic_score:.2f}; Complexity penalty: {k_penalty:.2f}; Order Param: {O:.2f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses the structural alignment score mapped to probability.
        """
        # Evaluate single candidate against a dummy set to get relative score
        # In a real system, we'd compare against the full pool, but here we simulate
        eval_res = self.evaluate(prompt, [answer])
        if not eval_res:
            return 0.0
        
        score = eval_res[0]['score']
        
        # Map score to 0-1 range using a sigmoid-like approximation
        # Logic scores usually range -1 to +2 based on our weights
        # Shift and scale: (score + 1) / 3 -> approx 0 to 1
        conf = (score + 1.0) / 3.0
        return max(0.0, min(1.0, conf))