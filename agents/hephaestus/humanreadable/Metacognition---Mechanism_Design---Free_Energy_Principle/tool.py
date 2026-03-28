import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Incentive-Compatible Active Inference (ICAI) Reasoning Tool.
    
    Mechanism:
    1. Free Energy Principle (FEP): Candidates are evaluated by their 'surprisal' 
       (negative log-likelihood) relative to structural constraints extracted from the prompt.
       Lower free energy = better fit.
    2. Mechanism Design: A proper scoring rule (Logarithmic Scoring Rule) is applied.
       The 'reward' (score) is maximized only if the system's internal confidence 
       (precision) matches the structural truth. Deviating from honest assessment 
       (e.g., over-confident wrong answers) incurs a high energy penalty.
    3. Metacognition: Used strictly as a confidence wrapper. It monitors the variance 
       between structural signals and lexical similarity to adjust the final confidence score,
       preventing over-confident hypothesis locking on superficially similar but logically wrong answers.
    
    Implementation:
    - Extracts structural tokens (negations, comparatives, numbers).
    - Computes a 'structural match' score (proxy for prediction error minimization).
    - Applies an incentive-compatible score transformation.
    - Uses NCD only as a tie-breaker for low-information candidates.
    """

    def __init__(self):
        # Structural keywords indicating logical constraints
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'provided'}
        self.bool_yes = {'yes', 'true', 'correct', 'y'}
        self.bool_no = {'no', 'false', 'incorrect', 'n'}

    def _extract_structure(self, text: str) -> Dict:
        """Parse text for logical constraints and numeric values."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_negation = any(w in self.negations for w in words)
        has_comparative = any(w in self.comparatives for w in words)
        has_conditional = any(w in self.conditionals for w in words)
        
        # Extract numbers
        numbers = [float(n) for n in re.findall(r'\d+\.?\d*', lower_text)]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(words)
        }

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Compute a score based on structural alignment (Free Energy minimization).
        High score = low prediction error relative to logical constraints.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        score = 0.0
        
        # 1. Negation Consistency Check
        # If prompt has negation, correct answer often implies specific handling.
        # Heuristic: If prompt asks a negative question, simple 'yes' might be wrong depending on context.
        # Here we reward detecting the negation in the candidate if present in prompt logic.
        if p_struct['negation']:
            if c_struct['negation']:
                score += 2.0  # Reward acknowledging negation
            elif any(w in self.bool_yes for w in c_lower.split()):
                # Penalty for blind 'yes' to negative constraint (common failure mode)
                score -= 3.0 
                
        # 2. Numeric Consistency
        if p_struct['numbers'] and c_struct['numbers']:
            # If both have numbers, check magnitude consistency if comparatives exist
            if p_struct['comparative'] or c_struct['comparative']:
                # Simple heuristic: if prompt says "greater", candidate number should be relevant
                # Since we don't have full semantic parse, we reward numeric presence in comparative contexts
                score += 1.5
            else:
                # Exact match bonus for numbers in non-comparative contexts
                if set(p_struct['numbers']) == set(c_struct['numbers']):
                    score += 3.0
                elif len(c_struct['numbers']) > 0:
                    score += 0.5 # Partial credit for attempting numeric answer

        # 3. Logical Operator Presence
        if p_struct['conditional'] and c_struct['conditional']:
            score += 1.0
            
        # 4. Length/Complexity matching (Occam's razor / Efficiency)
        # Penalize extremely verbose answers for simple prompts, or too short for complex
        if p_struct['length'] > 10 and c_struct['length'] < 2:
            score -= 1.0 # Too short for complex prompt
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 1.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        ranked = []
        
        # Pre-calculate prompt structure to avoid re-parsing
        p_struct = self._extract_structure(prompt)
        p_lower = prompt.lower()
        
        # Determine if the prompt is likely a Yes/No question based on structure
        is_binary_style = ('yes' in p_lower or 'no' in p_lower or '?' in prompt) and p_struct['length'] < 15

        for cand in candidates:
            # 1. Free Energy Calculation (Structural Match)
            # Lower free energy = higher raw score
            fe_score = self._compute_structural_score(prompt, cand)
            
            # 2. Mechanism Design: Incentive Compatibility via Proper Scoring
            # We transform the raw structural score into a probability-like estimate (p)
            # using a sigmoid-like mapping, then apply Log Score: S = ln(p) if correct, but 
            # since we don't know ground truth, we maximize expected utility by rewarding 
            # consistency between structural signals and the candidate's form.
            
            # Base probability estimate from structural score (mapped to 0.1 - 0.9)
            # Shift score to avoid log(0). 
            raw_prob = 1.0 / (1.0 + math.exp(-fe_score)) 
            # Clamp to avoid extremes
            raw_prob = max(0.05, min(0.95, raw_prob))
            
            # 3. Metacognitive Adjustment (Confidence Wrapper)
            # Check for "Over-confidence" traps. 
            # If prompt has negation but candidate is a short "Yes", lower confidence drastically.
            c_lower = cand.lower().strip()
            meta_penalty = 0.0
            
            if p_struct['negation']:
                if any(c_lower == w for w in self.bool_yes):
                    meta_penalty = -2.0 # Heavy penalty for blind yes on negative prompt
            
            # Adjust final score
            final_score = math.log(raw_prob + 1e-9) + meta_penalty
            
            # 4. NCD Tie-Breaker
            # If structural signals are weak (score near 0), use NCD to prefer closer string match
            if abs(fe_score) < 0.5:
                ncd_val = self._ncd(prompt, cand)
                final_score -= ncd_val * 0.1 # Small nudge
            
            ranked.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural fit: {fe_score:.2f}, Meta-adjust: {meta_penalty:.2f}"
            })

        # Sort descending by score
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns a confidence score 0-1.
        Uses metacognition to monitor variance between structural expectation and answer form.
        """
        # Re-use evaluation logic to get the score
        # We simulate a small candidate set to get relative scoring if needed, 
        # but here we just assess the specific pair.
        
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(answer)
        c_lower = answer.lower().strip()
        
        confidence = 0.5 # Base uncertainty
        
        # Structural alignment boosts confidence
        if p_struct['negation'] and c_struct['negation']:
            confidence += 0.3
        elif p_struct['numbers'] and c_struct['numbers']:
            if set(p_struct['numbers']) == set(c_struct['numbers']):
                confidence += 0.4
            else:
                confidence += 0.1
        
        # Metacognitive penalty: High variance detection
        # If the prompt is complex (long, conditionals) but answer is trivial, confidence drops
        if p_struct['length'] > 15 and (p_struct['conditional'] or p_struct['comparative']):
            if c_struct['length'] < 3:
                confidence -= 0.4 # Suspiciously simple answer for complex problem
        
        # Binary trap check
        if p_struct['negation'] and any(c_lower == w for w in self.bool_yes):
            confidence -= 0.5 # Likely wrong
            
        return max(0.0, min(1.0, confidence))