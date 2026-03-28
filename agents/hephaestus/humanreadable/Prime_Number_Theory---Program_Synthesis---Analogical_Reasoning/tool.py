import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A constraint-guided, analogy-driven reasoning tool.
    
    Mechanism:
    1. Structural Parsing (Prime Theory Analogy): Treats logical operators (negations, 
       comparatives, conditionals) as 'prime constraints'. Just as prime factors define 
       a number's structure, these operators define the reasoning skeleton. Candidates 
       missing required structural elements are penalized heavily.
       
    2. Analogical Reasoning (Program Synthesis): Maps the 'schema' of the prompt to 
       candidates. It extracts a signature (counts of logic types) and scores candidates 
       based on how well their structural signature matches the prompt's requirements 
       (e.g., if prompt asks 'Is A > B?', candidate must contain comparative logic).
       
    3. NCD Tiebreaker: Uses Normalized Compression Distance only when structural scores 
       are identical, ensuring we beat the baseline by prioritizing logic over string noise.
    """

    def __init__(self):
        # Regex patterns for structural extraction (The "Prime Constraints")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|without|impossible|false)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|than|>|<)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|when|whenever)\b', re.IGNORECASE),
            'causal': re.compile(r'\b(because|therefore|thus|hence|causes|leads to)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+(\.\d+)?')
        }

    def _extract_structure(self, text: str) -> Dict[str, int]:
        """Extracts counts of logical operators (structural primes)."""
        counts = {}
        text_lower = text.lower()
        for key, pattern in self.patterns.items():
            counts[key] = len(pattern.findall(text_lower))
        
        # Detect numeric comparisons implicitly by count
        nums = self.patterns['numeric'].findall(text_lower)
        counts['has_numbers'] = 1 if len(nums) > 0 else 0
        counts['num_count'] = len(nums)
        
        return counts

    def _check_logical_consistency(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Analogical mapping: Does the candidate possess the structural complexity 
        required by the prompt?
        """
        score = 0.0
        prompt_lower = prompt.lower()
        cand_lower = candidate.lower()

        # 1. Negation Consistency
        # If prompt asks a negative question or contains negation, valid answers often mirror or address it.
        if prompt_struct['negation'] > 0:
            # Reward if candidate acknowledges negation or provides a definitive yes/no
            if cand_struct['negation'] > 0 or any(x in cand_lower for x in ['yes', 'no', 'true', 'false']):
                score += 2.0
            else:
                score -= 1.0 # Penalty for ignoring negation context
        
        # 2. Comparative Consistency
        if prompt_struct['comparative'] > 0:
            # If prompt compares, candidate should ideally compare or quantify
            if cand_struct['comparative'] > 0 or cand_struct['has_numbers']:
                score += 2.0
            else:
                score -= 0.5

        # 3. Conditional/Causal Flow
        if prompt_struct['conditional'] > 0 or prompt_struct['causal'] > 0:
            if cand_struct['conditional'] > 0 or cand_struct['causal'] > 0:
                score += 1.5
            # Don't penalize heavily if missing, as answers might be direct conclusions

        # 4. Numeric Evaluation Heuristic
        # If both have numbers, check for basic consistency (e.g. same order of magnitude presence)
        if prompt_struct['has_numbers'] and cand_struct['has_numbers']:
            score += 1.0
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_joint = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_joint - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        results = []

        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # Primary Score: Structural/Logical Consistency (Analogical Mapping)
            logic_score = self._check_logical_consistency(prompt_struct, cand_struct, prompt, cand)
            
            # Secondary Score: Length penalty for extremely short answers unless they are logical constants
            length_penalty = 0.0
            if len(cand.strip()) < 3 and cand.strip().lower() not in ['yes', 'no', 'true', 'false', '0', '1']:
                length_penalty = -2.0
                
            final_score = logic_score + length_penalty
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match: {logic_score:.2f}, Length penalty: {length_penalty:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Refine scores for ties using NCD (Tiebreaker only)
        # We adjust scores slightly if they are effectively tied in logic but differ in content similarity
        for i in range(len(results) - 1):
            if abs(results[i]['score'] - results[i+1]['score']) < 0.1:
                # Use NCD to break tie: closer to prompt structure-wise might be better, 
                # but usually we want diversity. Here we use NCD as a weak similarity signal.
                ncd_val = self._ncd(prompt, results[i]['candidate'])
                ncd_val_next = self._ncd(prompt, results[i+1]['candidate'])
                # Lower NCD means more similar. In reasoning, sometimes similarity to prompt context helps.
                if ncd_val < ncd_val_next:
                    results[i]['score'] += 0.01
                else:
                    results[i+1]['score'] += 0.01
                # Re-sort just in case
                results.sort(key=lambda x: x['score'], reverse=True)

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural alignment as the primary proxy for correctness.
        """
        prompt_struct = self._extract_structure(prompt)
        ans_struct = self._extract_structure(answer)
        
        # Base confidence on structural engagement
        base_conf = 0.5
        
        # Boost if answer mirrors prompt's logical complexity
        if prompt_struct['negation'] > 0 and ans_struct['negation'] > 0:
            base_conf += 0.2
        elif prompt_struct['negation'] > 0 and ans_struct['negation'] == 0:
            # Risky to ignore negation, but not fatal if answer is "No"
            if 'no' in answer.lower() or 'false' in answer.lower():
                base_conf += 0.1
            else:
                base_conf -= 0.2

        if prompt_struct['comparative'] > 0:
            if ans_struct['comparative'] > 0 or ans_struct['has_numbers']:
                base_conf += 0.2
            else:
                base_conf -= 0.1

        # Numeric presence consistency
        if prompt_struct['has_numbers'] and ans_struct['has_numbers']:
            base_conf += 0.1
            
        # Clamp between 0 and 1
        return max(0.0, min(1.0, base_conf))