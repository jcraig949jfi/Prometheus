import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    RC-HBM Implementation (Simplified for Constraints):
    Uses structural parsing (negations, comparatives, numerics) as the primary 
    'emergent' signal generator. Kolmogorov Complexity (via zlib) is used strictly 
    as a tie-breaker for description length minimization. Theory of Mind is restricted 
    to the confidence wrapper to avoid historical failure modes.
    """
    
    def __init__(self):
        # Structural keywords for parsing
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'higher', 'lower']
        self.conditionals = ['if', 'unless', 'provided', 'assuming']
        self.bool_yes = ['yes', 'true', 'correct', 'right']
        self.bool_no = ['no', 'false', 'incorrect', 'wrong']

    def _get_compression_length(self, text: str) -> int:
        """Approximates Kolmogorov Complexity using zlib compression length."""
        if not text:
            return 0
        return len(zlib.compress(text.encode('utf-8')))

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from text."""
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text.lower())
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _analyze_structure(self, text: str) -> Dict:
        """Parses text for logical constraints and numeric values."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_negation = any(n in words for n in self.negations)
        has_comparative = any(c in words for c in self.comparatives)
        has_conditional = any(c in words for c in self.conditionals)
        numbers = self._extract_numbers(text)
        
        # Simple boolean detection
        is_yes = any(b in words for b in self.bool_yes)
        is_no = any(b in words for b in self.bool_no)
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'is_yes': is_yes,
            'is_no': is_no,
            'length': len(text)
        }

    def _compute_structural_score(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Computes a score based on logical consistency between prompt and candidate.
        This acts as the 'Emergent' layer where high-level logic overrides raw string similarity.
        """
        score = 0.0
        
        # 1. Numeric Consistency (High Priority)
        p_nums = prompt_struct['numbers']
        c_nums = cand_struct['numbers']
        
        if p_nums and c_nums:
            # If prompt has numbers and candidate has numbers, check ordering if comparatives exist
            if prompt_struct['comparative'] or cand_struct['comparative']:
                # Heuristic: If prompt implies comparison, candidate numbers should reflect valid logic
                # Since we don't know the exact operation, we reward presence of relevant numbers
                score += 2.0 
            else:
                # Exact match bonus for numbers in non-comparative contexts
                if set(p_nums) == set(c_nums):
                    score += 1.5
                elif any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                    score += 0.5

        # 2. Logical Negation Consistency
        # If prompt has negation, a 'No' answer or negated candidate is often structurally consistent
        if prompt_struct['negation']:
            if cand_struct['negation'] or cand_struct['is_no']:
                score += 1.0
            # Penalty for blind 'Yes' in negative context without negation in candidate
            elif cand_struct['is_yes'] and not cand_struct['negation']:
                score -= 0.5
        
        # 3. Conditional/Comparative Presence
        if prompt_struct['conditional'] or prompt_struct['comparative']:
            if cand_struct['conditional'] or cand_struct['comparative']:
                score += 0.8 # Reward structural mirroring of complexity
        
        # 4. Length Penalty (MDL principle): Prefer concise candidates if scores are close
        # But don't penalize too heavily if the candidate is just "Yes"/"No"
        if cand_struct['length'] > 0:
            # Normalize length penalty relative to prompt
            len_ratio = cand_struct['length'] / max(prompt_struct['length'], 1)
            if len_ratio > 2.0: # Candidate is more than 2x longer than prompt
                score -= 0.2 * (len_ratio - 1.0)
                
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._analyze_structure(prompt)
        p_comp = self._get_compression_length(prompt)
        
        scored_candidates = []
        
        for cand in candidates:
            cand_struct = self._analyze_structure(cand)
            c_comp = self._get_compression_length(cand)
            
            # Primary Score: Structural Logic
            struct_score = self._compute_structural_score(prompt_struct, cand_struct)
            
            # Tie-Breaker: Kolmogorov Complexity (MDL)
            # We want the candidate that compresses well relative to the prompt context
            # Lower compression length of (prompt + candidate) implies higher redundancy/coherence
            combined_text = f"{prompt} {cand}"
            combined_comp = self._get_compression_length(combined_text)
            
            # NCD-like metric for tie-breaking: 
            # Lower is better. We invert it for scoring so higher is better.
            # Using a small epsilon to avoid division by zero if needed, though lengths > 0
            ncd_score = 0.0
            max_comp = max(p_comp, c_comp, 1)
            if max_comp > 0:
                # Simplified NCD approximation for ranking
                ncd_val = (combined_comp - min(p_comp, c_comp)) / max_comp
                ncd_score = 1.0 / (1.0 + ncd_val) # Transform to 0-1 range roughly
            
            # Combine: Structural score dominates, NCD breaks ties
            # Scaling struct_score to be dominant (e.g., multiply by 10)
            final_score = (struct_score * 10.0) + (ncd_score * 0.1)
            
            reasoning = f"Structural:{struct_score:.2f} + MDL:{ncd_score:.2f}"
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Restricted ToM: Only evaluates structural coherence and compression.
        Does not attempt to model user intent directly to avoid failure traps.
        """
        p_struct = self._analyze_structure(prompt)
        a_struct = self._analyze_structure(answer)
        
        # Check for basic logical contradictions
        # If prompt asks a yes/no question (implied by structure) and answer is nonsense
        has_numbers = bool(p_struct['numbers'])
        answer_has_numbers = bool(a_struct['numbers'])
        
        score = 0.5 # Base confidence
        
        # Boost if structural features align (e.g., numbers in both)
        if has_numbers and answer_has_numbers:
            score += 0.3
            
        # Boost if logical negation matches context
        if p_struct['negation'] and (a_struct['negation'] or a_struct['is_no']):
            score += 0.2
        elif not p_struct['negation'] and (a_struct['is_yes'] or not a_struct['negation']):
            score += 0.1
            
        # Penalize extreme length mismatch (hallucination indicator)
        if len(answer) > len(prompt) * 5:
            score -= 0.4
            
        # Compression check: Does the answer add unnecessary complexity?
        p_len = self._get_compression_length(prompt)
        a_len = self._get_compression_length(answer)
        combined_len = self._get_compression_length(f"{prompt} {answer}")
        
        # If combined is much larger than sum of parts, it might be incoherent
        if combined_len > (p_len + a_len) * 1.2:
            score -= 0.2
            
        return max(0.0, min(1.0, score))