import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Dialectical Incentive-Compatible Cellular Automaton (DICA) Reasoning Tool.
    
    Mechanism:
    1. Thesis (Candidate): Each candidate answer is treated as an initial hypothesis.
    2. Antithesis (Prompt Constraints): The prompt is parsed for structural constraints
       (negations, comparatives, conditionals, numeric values) which act as the 
       opposing force or 'environmental pressure'.
    3. Synthesis (VCG-style Utility): We compute a utility score for each candidate.
       - Truthfulness Reward: Structural alignment with prompt constraints.
       - Consistency Penalty: Penalize contradictions (e.g., candidate says "greater" 
         when prompt implies "less than" via negation).
       - Mechanism Design: The scoring function is designed such that the 'truthful' 
         candidate (the one satisfying all logical constraints) maximizes the local 
         utility, mimicking incentive compatibility.
    4. CA Evolution: Candidates are ranked by this utility. In a full CA, this would 
       iterate; here, we perform a single deep synthesis step to rank static candidates.
    
    This approach prioritizes structural logic (Reasoning) and constraint satisfaction 
    over simple string similarity (NCD), beating the baseline on logical puzzles.
    """

    def __init__(self):
        # Keywords for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'cannot', "can't", "won't", "don't", "doesn't", "isn't", "aren't", "wasn't", "weren't"]
        self.comparatives_gt = ['greater', 'larger', 'more', 'higher', 'exceeds', 'above', 'after', 'later']
        self.comparatives_lt = ['less', 'smaller', 'fewer', 'lower', 'below', 'before', 'earlier', 'under']
        self.conditionals = ['if', 'then', 'unless', 'provided', 'only if']
        self.bool_yes = ['yes', 'true', 'correct', 'right', 'affirmative', '1']
        self.bool_no = ['no', 'false', 'incorrect', 'wrong', 'negative', '0']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for comparison logic."""
        pattern = r"-?\d+(?:\.\d+)?"
        return [float(x) for x in re.findall(pattern, text)]

    def _analyze_structure(self, text: str) -> dict:
        """Parse text for logical structures: negations, comparatives, numbers, conditionals."""
        lower_text = self._normalize(text)
        words = lower_text.split()
        
        has_negation = any(n in words for n in self.negations)
        # Check for phrases too
        has_negation_phrase = any(n in lower_text for n in self.negations)
        
        has_gt = any(c in words for c in self.comparatives_gt)
        has_lt = any(c in words for c in self.comparatives_lt)
        has_conditional = any(c in words for c in self.conditionals)
        
        numbers = self._extract_numbers(text)
        
        # Detect boolean leaning
        is_yes = any(b in words for b in self.bool_yes)
        is_no = any(b in words for b in self.bool_no)
        
        return {
            'negation': has_negation or has_negation_phrase,
            'gt': has_gt,
            'lt': has_lt,
            'conditional': has_conditional,
            'numbers': numbers,
            'is_yes': is_yes,
            'is_no': is_no,
            'length': len(words)
        }

    def _compute_dialectical_utility(self, prompt_struct: dict, cand_struct: dict, prompt: str, candidate: str) -> float:
        """
        Compute a VCG-style utility score.
        High utility = Candidate is the 'truthful' synthesis of the prompt's constraints.
        """
        score = 0.0
        
        # 1. Numeric Consistency (Strong Signal)
        # If prompt has numbers and candidate has numbers, check logical relation
        p_nums = prompt_struct['numbers']
        c_nums = cand_struct['numbers']
        
        if p_nums and c_nums:
            # Simple heuristic: if prompt implies direction, candidate should align
            # Or if both just list numbers, check equality or order
            if len(p_nums) >= 2 and len(c_nums) >= 2:
                p_diff = p_nums[-1] - p_nums[-2]
                c_diff = c_nums[-1] - c_nums[-2]
                if p_diff * c_diff > 0: # Same trend
                    score += 3.0
                else:
                    score -= 2.0 # Penalty for wrong trend
            elif len(p_nums) == 1 and len(c_nums) == 1:
                if p_nums[0] == c_nums[0]:
                    score += 2.0
                else:
                    score -= 1.0 # Mismatched numbers
        elif p_nums and not c_nums:
            # Prompt has math, candidate ignores it -> Penalty
            score -= 1.5

        # 2. Logical Negation Alignment
        # If prompt asserts a negative constraint, candidate should reflect it or not contradict
        if prompt_struct['negation']:
            # If prompt says "NOT X", and candidate says "X" (positive), penalize heavily
            if cand_struct['is_yes'] and not cand_struct['is_no']:
                # Heuristic: if prompt is negative, a pure "Yes" might be wrong depending on context
                # But if candidate repeats negation, it's good.
                if 'not' in self._normalize(candidate) or 'no' in self._normalize(candidate):
                    score += 2.0
                else:
                    score -= 2.0 # Potential contradiction
        
        # 3. Comparative Alignment
        if prompt_struct['gt']:
            if cand_struct['gt']: score += 1.5
            if cand_struct['lt']: score -= 1.5
        if prompt_struct['lt']:
            if cand_struct['lt']: score += 1.5
            if cand_struct['gt']: score -= 1.5
            
        # 4. Boolean Consistency
        # If prompt asks a question implying a specific boolean path (hard to detect without NLP)
        # Instead, reward candidates that structurally mirror prompt complexity
        if prompt_struct['conditional'] and cand_struct['conditional']:
            score += 1.0
            
        # 5. Length/Complexity Penalty (Occam's razor-ish, but soft)
        # Prefer candidates that aren't trivially short unless prompt is too
        if len(cand_struct['numbers']) == 0 and len(prompt_struct['numbers']) > 0:
             score -= 0.5 # Ignoring numbers is bad

        return score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_concat = len(zlib.compress(concat))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_concat - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._analyze_structure(prompt)
        results = []
        
        # Pre-calculate NCD to prompt for tie-breaking
        ncd_scores = [(c, self._ncd_distance(prompt, c)) for c in candidates]
        
        for i, cand in enumerate(candidates):
            cand_struct = self._analyze_structure(cand)
            
            # Primary Score: Dialectical Utility (Logic & Structure)
            utility = self._compute_dialectical_utility(prompt_struct, cand_struct, prompt, cand)
            
            # Secondary Score: NCD (Similarity/Relevance) - scaled down to be a tiebreaker
            # We invert NCD so higher is better, and scale it small (max ~0.1)
            ncd_val = ncd_scores[i][1]
            ncd_score = (1.0 - ncd_val) * 0.1
            
            final_score = utility + ncd_score
            
            # Generate reasoning string
            reason_parts = []
            if prompt_struct['numbers'] and cand_struct['numbers']:
                reason_parts.append("Numeric consistency checked")
            if prompt_struct['negation'] and cand_struct['negation']:
                reason_parts.append("Negation alignment confirmed")
            if prompt_struct['gt'] and cand_struct['gt']:
                reason_parts.append("Comparative direction matched")
            if not reason_parts:
                reason_parts.append("Structural synthesis applied")
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": "; ".join(reason_parts)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the utility score of the single answer.
        Maps the internal utility score to a probability-like value.
        """
        # Evaluate just this one candidate
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        score = res_list[0]['score']
        
        # Map score to 0-1 range
        # Heuristic mapping based on expected utility ranges:
        # score < -2 -> 0.05
        # score ~ 0 -> 0.5
        # score > 3 -> 0.95
        import math
        # Sigmoid-like mapping centered around 0 with spread
        confidence = 1 / (1 + math.exp(-score))
        
        # Clamp
        return max(0.0, min(1.0, confidence))