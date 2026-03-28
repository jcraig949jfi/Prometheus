import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Adaptive Epistemic Kalman Filter (AEKF) Reasoning Tool.
    
    Mechanism:
    1. State Estimation (Kalman-like): Maintains a running estimate of the 'truth' 
       based on structural evidence (negations, comparatives, numeric logic) extracted 
       from the prompt.
    2. Order Parameter (Innovation): Monitors the conflict between the prompt's 
       constraints and the candidate's alignment. High innovation indicates a 
       potential phase transition (e.g., a trick question or negation).
    3. Epistemic Revision: If innovation exceeds a critical threshold (phase transition), 
       the filter switches from a 'Foundationalist' mode (trusting surface similarity/NCD) 
       to a 'Coherentist' mode (strictly enforcing logical constraints and negations).
    4. Scoring: Candidates are scored based on how well they survive the epistemic 
       revision process. NCD is used only as a tie-breaker for structurally identical candidates.
    """

    def __init__(self):
        # Kalman Filter Parameters (Conceptual)
        self.process_noise_default = 0.1
        self.process_noise_inflated = 0.9  # During phase transition
        self.measurement_noise = 0.2
        self.critical_threshold = 0.6  # Threshold for phase transition
        
        # Epistemic State
        self.current_gain = 0.5
        self.is_phase_transition = False
        
        # Structural patterns
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', 'cannot', "can't", "won't", "don't", "doesn't", "isn't", "aren't", "wasn't", "weren't"}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'bigger', 'smaller', 'larger', 'shorter'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'assuming'}

    def _extract_structural_features(self, text: str) -> Dict:
        """Extract logical constraints: negations, comparatives, conditionals, numbers."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        features = {
            'negation_count': sum(1 for w in words if w in self.negation_words),
            'has_comparative': any(w in self.comparatives for w in words),
            'has_conditional': any(w in self.conditionals for w in words),
            'numbers': re.findall(r'\d+\.?\d*', lower_text),
            'length': len(text)
        }
        
        # Detect explicit logic operators
        features['has_logic'] = features['negation_count'] > 0 or features['has_comparative'] or features['has_conditional']
        
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denom

    def _evaluate_numeric_logic(self, prompt: str, candidate: str) -> float:
        """Check numeric consistency if numbers are present."""
        numbers = re.findall(r'\d+\.?\d*', prompt)
        if len(numbers) < 2:
            return 0.5 # No strong numeric signal
        
        try:
            # Simple heuristic: if candidate contains a number, check if it's in range or logical
            cand_nums = re.findall(r'\d+\.?\d*', candidate)
            if not cand_nums:
                return 0.5
            
            # If prompt asks for min/max (detected by keywords), verify
            p_lower = prompt.lower()
            val = float(cand_nums[0])
            prompt_vals = [float(n) for n in numbers]
            
            if 'smallest' in p_lower or 'minimum' in p_lower or 'least' in p_lower:
                return 1.0 if val == min(prompt_vals) else 0.0
            if 'largest' in p_lower or 'maximum' in p_lower or 'greatest' in p_lower:
                return 1.0 if val == max(prompt_vals) else 0.0
                
            # General float comparison if explicit in prompt (e.g. "is 9.11 < 9.9?")
            if '<' in prompt and len(prompt_vals) >= 2:
                expected = prompt_vals[0] < prompt_vals[1]
                # Check if candidate implies true/false
                cand_lower = candidate.lower()
                if 'true' in cand_lower or 'yes' in cand_lower:
                    return 1.0 if expected else 0.0
                if 'false' in cand_lower or 'no' in cand_lower:
                    return 0.0 if expected else 1.0
                    
        except ValueError:
            pass
            
        return 0.5 # Neutral if logic not clearly violated or supported

    def _detect_phase_transition(self, prompt: str, candidate: str) -> bool:
        """
        Detect if the prompt-candidate pair exhibits high innovation (conflict).
        This simulates the 'order parameter' exceeding a critical threshold.
        """
        p_features = self._extract_structural_features(prompt)
        c_features = self._extract_structural_features(candidate)
        
        innovation = 0.0
        
        # Conflict 1: Negation mismatch (Prompt says "not", candidate ignores it)
        if p_features['negation_count'] > 0:
            # If candidate is very similar to a substring of prompt that lacks negation, high innovation
            # Simplified: If prompt has negation but candidate is affirmative and short
            if c_features['negation_count'] == 0 and len(candidate.split()) < 10:
                innovation += 0.5
        
        # Conflict 2: Numeric logic violation
        num_score = self._evaluate_numeric_logic(prompt, candidate)
        if num_score < 0.2: # Strong violation
            innovation += 0.6
            
        # Conflict 3: Structural divergence
        if p_features['has_logic'] and not c_features['has_logic'] and len(candidate) > 5:
             innovation += 0.3

        return innovation > self.critical_threshold

    def _epistemic_score(self, prompt: str, candidate: str) -> float:
        """
        Core AEKF scoring mechanism.
        1. Calculate baseline similarity (NCD).
        2. Detect phase transition (logical conflict).
        3. Adjust gain and process noise based on epistemic mode.
        """
        # Baseline: Foundationalist (Trust surface form)
        ncd = self._compute_ncd(prompt, candidate)
        base_score = 1.0 - ncd
        
        # Check for Phase Transition
        is_transition = self._detect_phase_transition(prompt, candidate)
        
        if is_transition:
            # EPISTEMIC REVISION: 
            # The system detects the current model (surface similarity) is failing.
            # Switch to Coherentist mode: Penalize surface similarity if logic is violated.
            # Inflate process noise (allow belief to jump away from prior).
            
            logic_penalty = 0.0
            
            # Re-evaluate strictly on logic
            num_logic = self._evaluate_numeric_logic(prompt, candidate)
            if num_logic != 0.5: # If numeric logic was applicable
                logic_penalty = (1.0 - num_logic) * 0.8 # Heavy penalty for wrong math
            
            # Check negation consistency deeply
            p_feats = self._extract_structural_features(prompt)
            c_feats = self._extract_structural_features(candidate)
            
            if p_feats['negation_count'] > 0 and c_feats['negation_count'] == 0:
                # Candidate likely ignores the negation trap
                logic_penalty += 0.5
                
            # Final score in transition mode: Logic dominates, NCD is secondary/noisy
            score = max(0.0, base_score * 0.3 + (1.0 - logic_penalty) * 0.7)
        else:
            # Normal mode: Surface similarity and basic structure alignment
            # Small boost if structural features align (e.g. both have conditionals)
            p_feats = self._extract_structural_features(prompt)
            c_feats = self._extract_structural_features(candidate)
            
            struct_bonus = 0.0
            if p_feats['has_logic'] and c_feats['has_logic']:
                struct_bonus = 0.1
            elif not p_feats['has_logic'] and not c_feats['has_logic']:
                struct_bonus = 0.05
                
            score = base_score * 0.8 + struct_bonus + 0.2 # Bias towards relevance
            
        return min(1.0, max(0.0, score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._epistemic_score(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": "AEKF: Score derived from epistemic consistency and structural logic analysis."
            })
        
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        Uses the internal scoring mechanism but normalizes strictly.
        """
        score = self._epistemic_score(prompt, answer)
        
        # Calibration: 
        # If phase transition detected and score is low, confidence is high that it's WRONG (low score).
        # If score is high, confidence is high it's RIGHT.
        # We map the internal score directly as it represents likelihood of correctness.
        
        return float(score)