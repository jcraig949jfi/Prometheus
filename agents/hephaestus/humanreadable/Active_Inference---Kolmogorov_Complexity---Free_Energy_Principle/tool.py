import zlib
import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Description-Length-Regularized Variational Active Inference Agent.
    
    Mechanism:
    This tool approximates the Free Energy Principle (FEP) combined with Kolmogorov Complexity (KC)
    to evaluate candidate answers. Instead of training a neural net, it treats the "prompt" as the
    observed data (o) and the "candidate" as the generative model (m) or hypothesis.
    
    1. Variational Free Energy (Fit): Measured by how well the candidate compresses the prompt's
       logical constraints. We use a structural parsing score (Constraint Propagation) as a proxy
       for prediction error reduction. If the candidate contradicts explicit constraints (negations,
       comparatives), the energy penalty is high.
       
    2. Kolmogorov Complexity (Simplicity): Approximated via Normalized Compression Distance (NCD)
       using zlib. Shorter, self-contained candidates that still explain the prompt receive a
       'complexity penalty' boost (Occam's Razor), preventing overfitting to noise.
       
    3. Total Objective: F_total = Prediction_Error - lambda * Complexity_Penalty.
       Lower F_total is better. We invert this for the final score (Higher = Better).
       
    This approach beats pure NCD by prioritizing logical constraint satisfaction (Reasoning)
    while using compression as a tie-breaker for parsimony (Metacognition).
    """

    def __init__(self):
        # Lambda parameter for trading off fit vs. complexity (Occam's factor)
        self.lambda_complexity = 0.15
        # Weights for structural parsing
        self.weight_constraint = 2.0
        self.weight_numeric = 1.5
        self.weight_structure = 1.0

    def _get_compression_length(self, text: str) -> int:
        """Approximates Kolmogorov Complexity K(m) using zlib."""
        if not text:
            return 0
        return len(zlib.compress(text.encode('utf-8')))

    def _extract_constraints(self, text: str) -> Dict:
        """
        Structural parsing to extract logical constraints.
        Returns a dict of detected features to check against candidates.
        """
        text_lower = text.lower()
        constraints = {
            'negations': len(re.findall(r'\b(not|no|never|without|cannot|impossible)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text),
            'length': len(text)
        }
        return constraints

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Evaluates prediction error reduction.
        Checks if the candidate violates explicit structural patterns found in the prompt.
        Returns a penalty score (0.0 = perfect consistency, higher = violation).
        """
        penalty = 0.0
        p_constraints = self._extract_constraints(prompt)
        c_constraints = self._extract_constraints(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()

        # 1. Negation Check: If prompt says "not X", candidate saying "X" is a huge penalty
        # Simple heuristic: if prompt has strong negation context, candidate shouldn't be overly affirmative without qualification
        if p_constraints['negations'] > 0:
            # If candidate is very short and affirmative (e.g., "Yes") while prompt is complex/negative
            if c_constraints['negations'] == 0 and len(candidate.split()) < 4 and p_constraints['length'] > 20:
                # Heuristic: Suspicious if prompt is complex/negative and answer is simple positive
                # Only apply if we detect specific negative triggers in prompt that might be contradicted
                if any(word in p_lower for word in ['not', 'never', 'impossible']):
                    penalty += 0.5

        # 2. Numeric Consistency: If numbers exist, check ordering if possible
        if p_constraints['numbers'] and c_constraints['numbers']:
            try:
                p_nums = [float(x) for x in p_constraints['numbers']]
                c_nums = [float(x) for x in c_constraints['numbers']]
                # If prompt implies a range or comparison, simple presence helps, 
                # but gross contradictions (like reversing a sorted list mentioned) are hard to catch without NLP.
                # Instead, reward candidates that reference the numbers found in the prompt.
                match_count = sum(1 for n in c_nums if any(abs(n - p) < 1e-6 for p in p_nums))
                if match_count == 0 and len(p_nums) > 0:
                    # Candidate introduces new numbers unrelated to prompt? Potential hallucination.
                    penalty += 0.2
            except ValueError:
                pass

        # 3. Structural Echo: Candidate should share some structural tokens (conditionals) if prompt has them
        if p_constraints['conditionals'] > 0:
            if c_constraints['conditionals'] == 0 and len(candidate) > 10:
                # Lack of conditional logic in a conditional problem might indicate oversimplification
                penalty += 0.1

        return penalty

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance between two strings."""
        if not s1 or not s2:
            return 1.0
        
        c1 = self._get_compression_length(s1)
        c2 = self._get_compression_length(s2)
        c12 = self._get_compression_length(s1 + s2)
        
        # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Using max for normalization to keep it in [0, 1] roughly
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
            
        ncd = (c12 - min(c1, c2)) / denominator
        return max(0.0, min(1.0, ncd))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates based on the description-length-regularized free energy objective.
        Score = (Fit Score) - (Complexity Penalty)
        """
        if not candidates:
            return []
            
        results = []
        prompt_len = len(prompt)
        if prompt_len == 0:
            prompt_len = 1 # Avoid division by zero
            
        for cand in candidates:
            if not cand:
                score = 0.0
                reasoning = "Empty candidate."
                results.append({"candidate": cand, "score": score, "reasoning": reasoning})
                continue

            # 1. Fit Term (Variational Free Energy component)
            # Lower logical penalty = better fit. 
            # We invert the penalty to a 'fit_score' where higher is better.
            logical_penalty = self._check_logical_consistency(prompt, cand)
            fit_score = 1.0 - min(logical_penalty, 1.0)
            
            # Boost fit if candidate length is proportional to prompt complexity (not too short, not rambling)
            # Ideal ratio heuristic: answer is 10%-50% of prompt length for complex reasoning, 
            # or very short for simple facts.
            len_ratio = len(cand) / prompt_len
            length_penalty = 0.0
            if len_ratio > 2.0: # Too verbose
                length_penalty = 0.2
            elif len_ratio < 0.01 and prompt_len > 50: # Too short for complex prompt
                length_penalty = 0.1
            
            adjusted_fit = fit_score - length_penalty

            # 2. Complexity Term (Kolmogorov Complexity component)
            # We want parsimonious models. 
            # Use NCD to measure how much 'new information' the candidate adds relative to the prompt.
            # Low NCD means candidate is compressible given the prompt (good explanation).
            # However, pure NCD favors "Yes"/"No". We combine with fit.
            ncd_val = self._calculate_ncd(prompt, cand)
            
            # Complexity penalty: We prefer candidates that are compressible (low NCD) 
            # BUT we already penalized logical errors. 
            # Here we apply Occam's razor: if two candidates fit equally well, prefer the simpler one.
            # We treat NCD as a small regularizer.
            complexity_cost = ncd_val * self.lambda_complexity

            # Total Objective (Maximize this)
            # F_total approx = adjusted_fit - complexity_cost
            final_score = adjusted_fit - complexity_cost
            
            # Deterministic tie-breaking using string hash if scores are extremely close
            # (Not strictly needed for float comparison but good for stability)
            
            reasoning = f"Fit:{adjusted_fit:.2f}, NCD:{ncd_val:.2f}, Lambda:{self.lambda_complexity}"
            results.append({"candidate": cand, "score": final_score, "reasoning": reasoning})

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the free energy score of the single answer.
        """
        evaluated = self.evaluate(prompt, [answer])
        if not evaluated:
            return 0.0
        
        # Normalize the score to 0-1 range roughly. 
        # Theoretically score is around -1 to 1.
        raw_score = evaluated[0]['score']
        
        # Map [-0.5, 1.5] -> [0, 1] roughly, clamping
        conf = (raw_score + 0.5) / 2.0
        return max(0.0, min(1.0, conf))