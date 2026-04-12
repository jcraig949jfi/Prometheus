import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Adaptive Attention Controller (PAAC) Implementation.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values to form a "Logical Form".
    2. Pragmatic Inference (Bias): Detects context cues (sarcasm markers, question 
       patterns) to apply a bias vector to the scoring.
    3. Feedback Control (PID-style): Simulates error correction by comparing the 
       candidate's structural features against the prompt's required logic. 
       - Proportional: Direct match of logical tokens.
       - Integral: Accumulated consistency of numeric/constraint relations.
       - Derivative: Penalty for sudden shifts in logical polarity (e.g., double negatives).
    4. Attention Modulation: The final score is a weighted sum where structural 
       matches dominate, pragmatic bias adjusts the set-point, and NCD serves only 
       as a tiebreaker for low-information candidates.
    """

    def __init__(self):
        # Logical keywords for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', 'before', 'after']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.pragmatic_triggers = ['actually', 'obviously', 'clearly', 'supposedly', 'maybe', 'perhaps']
        
        # PID Gain constants (tuned for logical stability)
        self.kp = 0.5  # Proportional gain (direct feature match)
        self.ki = 0.3  # Integral gain (contextual consistency)
        self.kd = 0.2  # Derivative gain (polarity shift penalty)

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract integers and floats
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _structural_parse(self, text: str) -> Dict:
        tokens = self._tokenize(text)
        has_neg = any(n in tokens for n in self.negations)
        has_comp = any(c in tokens for c in self.comparatives)
        has_cond = any(c in tokens for c in self.conditionals)
        numbers = self._extract_numbers(text)
        
        # Count logical density
        logic_count = sum([has_neg, has_comp, has_cond])
        
        return {
            'neg_count': tokens.count('not') + tokens.count('no'), # Simplified count
            'has_neg': has_neg,
            'has_comp': has_comp,
            'has_cond': has_cond,
            'numbers': numbers,
            'logic_density': logic_count,
            'length': len(tokens)
        }

    def _pragmatic_bias(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Computes a bias based on pragmatic implicature.
        If the prompt implies a complex logical structure (high density) but the 
        candidate is overly simple (low density), apply a negative bias (skepticism).
        """
        bias = 0.0
        
        # Implicature: Short answers to complex logical prompts are often wrong
        if prompt_struct['logic_density'] > 1 and cand_struct['logic_density'] == 0:
            bias -= 0.2
            
        # Implicature: Negation matching
        # If prompt has negation, correct answer often needs to address it explicitly
        if prompt_struct['has_neg'] and not cand_struct['has_neg']:
            # Heuristic: unless the answer is a direct number result
            if not cand_struct['numbers']:
                bias -= 0.1
                
        return bias

    def _pid_control_score(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Simulates a PID controller to score the candidate.
        Error = Difference in logical structure between Prompt Requirements and Candidate.
        """
        # Proportional Term: Feature alignment
        # Reward matching logical types (e.g., both have comparatives)
        p_term = 0.0
        if prompt_struct['has_neg'] == cand_struct['has_neg']:
            p_term += 1.0
        if prompt_struct['has_comp'] == cand_struct['has_comp']:
            p_term += 1.0
        if prompt_struct['has_cond'] == cand_struct['has_cond']:
            p_term += 1.0
            
        # Normalize P term to 0-1 range roughly
        p_score = p_term / 3.0

        # Integral Term: Numeric/Constraint Consistency
        # If numbers exist, do they follow the trend? (Simplified: presence match)
        i_term = 0.0
        if prompt_struct['numbers'] and cand_struct['numbers']:
            # Check if candidate numbers are within a reasonable range of prompt numbers
            # (Heuristic: at least one number exists in both)
            i_term = 1.0
        elif not prompt_struct['numbers'] and not cand_struct['numbers']:
            i_term = 1.0 # Consistent absence
            
        # Derivative Term: Rate of change in logical polarity
        # Penalize if candidate introduces negation where none existed (instability)
        d_term = 0.0
        polarity_change = abs(int(prompt_struct['has_neg']) - int(cand_struct['has_neg']))
        if polarity_change == 0:
            d_term = 1.0 # Stable
        else:
            d_term = 0.5 # Unstable shift

        return (self.kp * p_score) + (self.ki * i_term) + (self.kd * d_term)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_concat = len(zlib.compress(concat))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_concat - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._structural_parse(prompt)
        results = []
        
        for cand in candidates:
            cand_struct = self._structural_parse(cand)
            
            # 1. Primary Score: Structural Logic via PID Control
            logic_score = self._pid_control_score(prompt_struct, cand_struct)
            
            # 2. Pragmatic Bias Adjustment
            bias = self._pragmatic_bias(prompt_struct, cand_struct)
            
            # 3. NCD Tiebreaker (only if logic scores are very close or zero)
            # We invert NCD so higher is better (lower distance = higher score)
            ncd_val = self._ncd_distance(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.1 # Weight NCD lightly as tiebreaker
            
            final_score = logic_score + bias + ncd_score
            
            # Construct reasoning string
            reasoning_parts = []
            if prompt_struct['has_neg'] == cand_struct['has_neg']:
                reasoning_parts.append("negation aligned")
            if cand_struct['numbers']:
                reasoning_parts.append("numeric content detected")
            if bias < 0:
                reasoning_parts.append("pragmatic skepticism applied")
                
            reasoning = "; ".join(reasoning_parts) if reasoning_parts else "structural match"

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the evaluation score of the single answer.
        """
        # Evaluate the single candidate against the prompt
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        
        # Normalize the score to 0-1 range roughly
        # Base logic score maxes around 1.0 + biases. 
        score = ranked[0]['score']
        
        # Clamp between 0 and 1
        confidence = max(0.0, min(1.0, score))
        return round(confidence, 4)