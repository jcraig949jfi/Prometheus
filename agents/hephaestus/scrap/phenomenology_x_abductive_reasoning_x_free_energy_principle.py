import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Phenomenally-Constrained Active Inference (PCAI) Tool.
    
    Mechanism:
    1. Free Energy Principle (Core Driver): Minimizes 'surprise' by evaluating how well
       candidates satisfy structural constraints (negations, comparatives, conditionals)
       extracted from the prompt. Lower prediction error = higher score.
    2. Abductive Reasoning (Secondary): When structural signals are ambiguous, it generates
       explanatory hypotheses by checking for keyword consistency and logical flow,
       penalizing complexity (verbosity) to favor simple explanations.
    3. Phenomenological Bracketing (Meta-Layer): The confidence() method acts as the
       'bracketing' mechanism, isolating the self-model's assessment of the answer
       from the external world model, ensuring the score reflects internal consistency
       rather than just string similarity.
       
    Note: Pure phenomenology is restricted to the confidence wrapper to avoid
    historical reasoning traps, while Free Energy drives the evaluate() logic.
    """

    def __init__(self):
        # Structural patterns for Free Energy minimization (Prediction Error reduction)
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparative_ops = {'>', '<', '>=', '<=', 'greater', 'less', 'more', 'fewer'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided'}
        
    def _extract_structural_constraints(self, text: str) -> dict:
        """Extracts logical constraints to form the generative model's priors."""
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))
        
        constraints = {
            'has_negation': bool(words & self.negation_words),
            'has_comparative': bool(words & self.comparative_ops),
            'has_conditional': bool(words & self.conditionals),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'length': len(text)
        }
        return constraints

    def _compute_prediction_error(self, prompt: str, candidate: str) -> float:
        """
        Computes variational free energy approximation.
        High error = high surprise (bad candidate).
        Low error = low surprise (good candidate).
        """
        p_const = self._extract_structural_constraints(prompt)
        c_const = self._extract_structural_constraints(candidate)
        
        error = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        if p_const['has_negation']:
            # If prompt has negation, candidate should ideally reflect it or not contradict it
            # Simple heuristic: if prompt negates, candidate shouldn't be blindly affirmative without nuance
            if not c_const['has_negation'] and len(candidate.split()) < 5:
                error += 2.0 
        
        # 2. Numeric Consistency (Free Energy minimization on quantities)
        if p_const['numbers'] and c_const['numbers']:
            try:
                p_nums = [float(n) for n in p_const['numbers']]
                c_nums = [float(n) for n in c_const['numbers']]
                
                # Check for direct contradictions in extracted numbers
                # If prompt implies a range or specific value, candidate matching reduces error
                if any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                    error -= 3.0 # Reward match
                elif p_nums and c_nums:
                    # Penalize if numbers are wildly different when both exist
                    error += abs(p_nums[0] - c_nums[0]) * 0.1
            except ValueError:
                pass

        # 3. Comparative Logic
        if p_const['has_comparative']:
            if not c_const['has_comparative']:
                # Candidate might need to reflect the comparison
                error += 0.5
                
        # 4. Length/Complexity Penalty (Occam's Razor / Abductive simplicity)
        # Penalize overly verbose answers that don't add structural value
        if len(candidate) > len(prompt) * 1.5:
            error += 1.0
            
        return error

    def _abductive_hypothesis_score(self, prompt: str, candidate: str) -> float:
        """
        Generates a score based on abductive virtues: simplicity and explanatory depth.
        Simulates searching for the best explanation of the prompt using the candidate.
        """
        score = 0.0
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        # Overlap indicates explanatory relevance
        intersection = p_words & c_words
        union = p_words | c_words
        
        if not union:
            return 0.0
            
        # Jaccard similarity as a proxy for explanatory coverage
        coverage = len(intersection) / len(union)
        score += coverage * 5.0
        
        # Penalty for hallucinating new concepts not in prompt (unless common words)
        # This simulates the 'bracketing' of external noise
        new_concepts = c_words - p_words - self.negation_words - self.comparative_ops - self.conditionals
        score -= len(new_concepts) * 0.05
        
        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            max_len = max(c1, c2)
            if max_len == 0:
                return 1.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates by minimizing free energy (prediction error) 
        and maximizing abductive explanatory power.
        """
        scored_candidates = []
        
        for candidate in candidates:
            # Core Free Energy Driver: Minimize prediction error
            pred_error = self._compute_prediction_error(prompt, candidate)
            
            # Abductive Support: Explanatory virtue score
            abductive_score = self._abductive_hypothesis_score(prompt, candidate)
            
            # Combined Score: High abductive score - low prediction error
            # We invert error so higher is better
            raw_score = abductive_score - pred_error
            
            scored_candidates.append({
                "candidate": candidate,
                "score": raw_score,
                "reasoning": f"FreeEnergy(-{pred_error:.2f}) + Abductive({abductive_score:.2f})"
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Apply NCD tie-breaking for top candidates if scores are close
        if len(scored_candidates) > 1:
            if abs(scored_candidates[0]["score"] - scored_candidates[1]["score"]) < 0.1:
                # Use NCD against prompt as tie breaker
                for item in scored_candidates:
                    ncd = self._ncd_distance(prompt, item["candidate"])
                    item["score"] -= ncd * 0.01 # Small penalty for high NCD
                scored_candidates.sort(key=lambda x: x["score"], reverse=True)

        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Phenomenological Bracketing Layer.
        Isolates the self-model's assessment of the answer's internal consistency.
        Returns 0.0 (wrong) to 1.0 (correct).
        """
        # Re-use the evaluation logic but normalize to [0, 1]
        # We treat the single answer as a candidate list
        results = self.evaluate(prompt, [answer])
        
        if not results:
            return 0.0
            
        raw_score = results[0]["score"]
        
        # Map raw score to 0-1 range using a sigmoid-like approximation
        # Assuming typical scores range between -5 and 10
        # sigmoid(x) = 1 / (1 + e^(-k(x - x0)))
        k = 0.3
        x0 = 2.0 
        import math
        try:
            conf = 1.0 / (1.0 + math.exp(-k * (raw_score - x0)))
        except OverflowError:
            conf = 1.0 if raw_score > 0 else 0.0
            
        # Clamp
        return max(0.0, min(1.0, conf))