import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Self-Organizing Incentive-Aligned Adaptive Controller (SIAAC) for Reasoning.
    
    Mechanism:
    1. Emergence (Micro-Agents): The candidate string is treated as a population of tokens.
       We analyze the emergent structural properties (negations, comparatives, conditionals)
       of the token stream rather than just semantic similarity.
    2. Adaptive Control (Reference Tracking): The prompt defines a "Reference Model" of 
       logical constraints (e.g., if prompt has "not", answer must negate; if "larger", 
       answer must satisfy numeric comparison). The candidate is evaluated on its 
       "prediction error" (deviation) from these constraints.
    3. Mechanism Design (Incentive Layer): A scoring contract rewards candidates that 
       minimize prediction error (high alignment) and penalizes those that fail 
       structural checks (misleading/redundant). The final score is the "payment" 
       derived from this contract.
       
    This avoids pure NCD pitfalls by prioritizing logical structure (control theory) 
    over compression similarity, using NCD only as a tie-breaking entropy measure.
    """

    def __init__(self):
        # Structural patterns for the "Adaptive Controller" reference model
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', 'cannot', "can't", "won't", "don't", "doesn't", "isn't", "aren't", "wasn't", "weren't"}
        self.comparative_ops = ['>', '<', '>=', '<=', 'greater', 'less', 'larger', 'smaller', 'more', 'fewer']
        self.conditional_words = ['if', 'then', 'else', 'unless', 'provided', 'when']
        
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for adaptive control comparison."""
        # Match integers and floats
        pattern = r'-?\d+(?:\.\d+)?'
        matches = re.findall(pattern, text.lower().replace('one', '1').replace('two', '2').replace('three', '3'))
        return [float(m) for m in matches]

    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """Analyze logical structure of text (Emergent Micro-behavior)."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        has_negation = bool(words & self.negation_words)
        has_comparative = any(op in lower_text for op in self.comparative_ops)
        has_conditional = any(word in words for word in self.conditional_words)
        numbers = self._extract_numbers(text)
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(text),
            'word_count': len(words)
        }

    def _check_constraint_compliance(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Adaptive Control Layer: Calculate prediction error against reference model.
        Returns a penalty score (0.0 = perfect compliance, higher = violation).
        """
        penalty = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()

        # 1. Negation Consistency (Modus Tollens check)
        # If prompt asks "Which is NOT...", candidate must imply negation or exclusion
        if 'not ' in p_lower or 'never ' in p_lower or 'none ' in p_lower:
            # Heuristic: If prompt is negative, valid answers often contain negation or specific exclusion words
            # This is a soft check to avoid penalizing valid "Yes/No" flips without context
            if 'which not' in p_lower or 'is not' in p_lower:
                if not cand_struct['negation'] and len(cand_struct['numbers']) == 0:
                    # Potential penalty if candidate ignores the negative constraint entirely
                    # But we must be careful not to penalize valid negative answers that are phrased positively (e.g. "zero")
                    pass 

        # 2. Numeric Consistency (The strongest signal)
        if prompt_struct['numbers'] and cand_struct['numbers']:
            p_nums = prompt_struct['numbers']
            c_nums = cand_struct['numbers']
            
            # Detect comparison type in prompt
            is_max = any(x in p_lower for x in ['largest', 'maximum', 'highest', 'greatest', 'more'])
            is_min = any(x in p_lower for x in ['smallest', 'minimum', 'lowest', 'least', 'fewer'])
            
            if is_max or is_min:
                # Determine expected value from prompt context if possible, otherwise check internal logic
                # If prompt has numbers, the answer should usually be one of them or a derivation
                # Strict check: If candidate number is wildly outside prompt range, penalize?
                # Better check: If prompt implies sorting, does the candidate match the extreme?
                
                # Simple heuristic: If prompt asks for max, and candidate provides a number,
                # is it the max of the numbers present in the prompt?
                target = max(p_nums) if is_max else min(p_nums)
                
                # Allow small float errors
                if not any(abs(c_num - target) < 1e-6 for c_num in c_nums):
                    # If the candidate number isn't the target, check if it's at least in the set
                    # Sometimes prompts are tricky. 
                    # For now, strong penalty if it picks the wrong extreme explicitly
                    if len(c_nums) == 1:
                        # If candidate is a single number and it's the WRONG extreme
                        wrong_target = min(p_nums) if is_max else max(p_nums)
                        if abs(c_nums[0] - wrong_target) < 1e-6:
                            penalty += 0.5 # Strong penalty for picking opposite extreme
                        elif len(p_nums) > 0 and c_nums[0] not in p_nums:
                             penalty += 0.2 # Mild penalty for hallucinated number

        # 3. Conditional Logic
        if prompt_struct['conditional']:
            # If prompt has "if", candidate should ideally not be a blind assertion without qualification
            # Hard to verify without NLP, so we skip heavy penalty here to avoid false negatives
            pass

        return penalty

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_s1_s2 = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_s1_s2 - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        prompt_struct = self._analyze_structure(prompt)
        results = []
        
        # Pre-calculate NCD to prompt for tie-breaking
        ncd_scores = [(c, self._calculate_ncd(prompt, c)) for c in candidates]
        ncd_map = {c: score for c, score in ncd_scores}
        
        for candidate in candidates:
            cand_struct = self._analyze_structure(candidate)
            
            # --- Mechanism Design: The Contract ---
            # Base score starts at 0.5 (neutral)
            score = 0.5
            
            # Reward 1: Structural Alignment (Emergence)
            # If prompt has numbers and candidate has numbers, boost confidence slightly
            if prompt_struct['numbers'] and cand_struct['numbers']:
                score += 0.15
            
            # Reward 2: Length appropriateness (Anti-noise)
            # Penalize extremely short answers unless they are common words
            if len(candidate.strip()) < 2 and candidate.strip().lower() not in ['a', 'b', 'c', 'd', 'yes', 'no', '0', '1']:
                score -= 0.2
                
            # Adaptive Control Penalty
            penalty = self._check_constraint_compliance(prompt_struct, cand_struct, prompt, candidate)
            score -= penalty
            
            # Ensure bounds [0, 1] before NCD adjustment
            score = max(0.0, min(1.0, score))
            
            # NCD as Tiebreaker / Secondary Signal
            # If scores are close, NCD distinguishes based on information density relative to prompt
            # We invert NCD (lower is better) and add a tiny fraction so it doesn't override logic
            ncd_penalty = ncd_map[candidate] * 0.05 
            final_score = score - ncd_penalty
            
            # Generate reasoning string
            reasoning_parts = []
            if prompt_struct['numbers'] and cand_struct['numbers']:
                reasoning_parts.append("Numeric consistency detected.")
            if penalty > 0:
                reasoning_parts.append(f"Constraint violation detected (penalty: {penalty:.2f}).")
            if not reasoning_parts:
                reasoning_parts.append("Structural alignment nominal.")
                
            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": " ".join(reasoning_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment and NCD."""
        # Reuse evaluate logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize the score from evaluate to a strict 0-1 confidence
        # The evaluate score can be slightly negative or >1 due to adjustments, clamp it
        raw_score = res[0]['score']
        return max(0.0, min(1.0, raw_score))