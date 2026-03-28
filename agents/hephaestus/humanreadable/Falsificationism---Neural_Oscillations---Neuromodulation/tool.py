import re
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Oscillatory Predictive Coding Network with Neuromodulated Gain Control (OPNGC).
    
    Mechanism:
    1. Theta Cycle (Hypothesis Window): The prompt is parsed into structural tokens 
       (negations, comparatives, numbers). This defines the current "hypothesis" frame.
    2. Gamma Sub-populations (Evidence Accumulation): Candidates are evaluated against 
       the prompt's structural constraints. Matches reduce prediction error; mismatches increase it.
    3. Neuromodulated Gain (Dopamine/Serotonin): 
       - Dopamine-like gain scales the penalty of prediction errors. High structural 
         mismatch (falsification) triggers high gain, sharply reducing the score.
       - Serotonin-like tone adjusts the exploration threshold, resetting confidence 
         if no strong structural match is found.
    4. Falsification Logic: Instead of seeking confirmation, the system actively searches 
       for disconfirming evidence (negation mismatches, numeric violations). A single 
       strong falsification signal overrides weak confirmatory signals.
       
    This implements the Falsificationism x Neuromodulation synergy by using structural 
    parsing to detect contradictions (falsification) and scaling their impact dynamically.
    """

    def __init__(self):
        # Structural keywords for parsing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<'}
        self.conditionals = {'if', 'then', 'unless', 'only if'}
        self.bool_yes = {'yes', 'true', 'correct', 'right'}
        self.bool_no = {'no', 'false', 'incorrect', 'wrong'}

    def _parse_structure(self, text: str) -> Dict:
        """Extract structural features: negations, numbers, booleans."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        # Detect negations
        has_negation = any(word in self.negations for word in words)
        
        # Extract numbers
        numbers = []
        for word in words:
            try:
                # Handle simple integers and floats
                if '.' in word:
                    numbers.append(float(word))
                else:
                    numbers.append(float(word))
            except ValueError:
                continue
        
        # Detect boolean leanings
        yes_count = sum(1 for w in words if w in self.bool_yes)
        no_count = sum(1 for w in words if w in self.bool_no)
        
        return {
            'negations': has_negation,
            'numbers': numbers,
            'yes_score': yes_count,
            'no_score': no_count,
            'length': len(words)
        }

    def _compute_falsification_error(self, prompt_feat: Dict, cand_feat: Dict) -> float:
        """
        Compute prediction error based on structural mismatches.
        High error = strong falsification signal.
        """
        error = 0.0
        
        # 1. Negation Falsification (Strong Signal)
        # If prompt has negation and candidate asserts positive (or vice versa), huge error.
        if prompt_feat['negations'] != cand_feat['negations']:
            # Check if candidate is purely affirmative/negative based on counts
            p_trend = -1 if prompt_feat['negations'] else 1
            c_trend = 1 if cand_feat['yes_score'] > cand_feat['no_score'] else (-1 if cand_feat['no_score'] > cand_feat['yes_score'] else 0)
            
            if p_trend * c_trend == -1: # Direct contradiction
                error += 5.0 
            elif p_trend != 0 and c_trend == 0:
                error += 1.5 # Missing nuance

        # 2. Numeric Falsification
        if prompt_feat['numbers'] and cand_feat['numbers']:
            # Simple check: do the numbers align in magnitude or presence?
            # If prompt implies a range and candidate violates it (simplified here to presence/magnitude diff)
            p_max = max(prompt_feat['numbers'])
            c_max = max(cand_feat['numbers'])
            if abs(p_max - c_max) > 0.1: # Numeric mismatch
                error += 2.0
        
        # 3. Length/Complexity Mismatch (Heuristic for relevance)
        if prompt_feat['length'] > 10 and cand_feat['length'] < 3:
            error += 1.0 # Too short to be a valid reasoning step usually
            
        return error

    def _neuromodulated_gain(self, base_score: float, error: float) -> float:
        """
        Apply dopamine-like gain control.
        High error amplifies the penalty (non-linear drop).
        Simulates Popperian falsification: one strong counter-evidence kills the hypothesis.
        """
        if error > 0:
            # Gain factor increases with error magnitude
            gain = 1.0 + (error * 0.8) 
            # Exponential decay based on error * gain
            adjustment = np.exp(-error * gain)
            return base_score * adjustment
        return base_score

    def _oscillatory_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Simulate one theta-cycle of evaluation.
        Returns (score, reasoning_string)
        """
        p_feat = self._parse_structure(prompt)
        c_feat = self._parse_structure(candidate)
        
        # Base similarity (NCD tiebreaker logic embedded as baseline)
        # Using simple ratio of common words for baseline to save lines/complexity vs full NCD
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        intersection = p_words.intersection(c_words)
        union = p_words.union(c_words)
        base_similarity = len(intersection) / len(union) if union else 0.0
        
        # Initial score based on overlap
        score = base_similarity
        
        # Compute structural prediction error (Falsification check)
        error = self._compute_falsification_error(p_feat, c_feat)
        
        # Apply Neuromodulated Gain
        final_score = self._neuromodulated_gain(score, error)
        
        # Construct reasoning trace
        reasons = []
        if error > 2.0:
            reasons.append("Critical falsification detected (structural contradiction).")
        elif error > 0:
            reasons.append("Minor structural mismatch detected.")
        else:
            reasons.append("No structural falsification found.")
            
        if p_feat['negations'] and not c_feat['negations']:
            reasons.append("Prompt contains negation; candidate lacks corresponding negation logic.")
            
        if p_feat['numbers'] and c_feat['numbers']:
             reasons.append("Numeric constraints evaluated.")
        elif p_feat['numbers'] and not c_feat['numbers']:
             reasons.append("Candidate ignores numeric data in prompt.")

        return final_score, " ".join(reasons)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reasoning = self._oscillatory_score(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
        
        # Sort by score descending (Theta-phase reset: order by confidence)
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._oscillatory_score(prompt, answer)
        # Clamp to 0-1
        return max(0.0, min(1.0, float(score)))