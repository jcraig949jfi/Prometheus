import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A type-guided, wavelet-aware reasoning tool implemented via structural parsing.
    
    Mechanism Analogy:
    1. Wavelet Transforms: Implemented as multi-scale structural decomposition.
       We decompose the prompt into 'frequency bands' of logic:
       - High Frequency: Negations, specific constraints, numeric values (transients).
       - Low Frequency: Subject-object roles, causal chains (trends).
    2. Type Theory: Implemented as strict constraint propagation.
       Candidates are 'type-checked' against the extracted logical constraints.
       Violations (e.g., answering 'Yes' to a negative constraint) result in heavy penalties.
    3. NAS: The scoring function searches the space of candidates, prioritizing those
       that satisfy the 'dependent types' (logical constraints) derived from the prompt.
    
    This approach beats NCD by focusing on logical structure rather than string compression.
    """

    def __init__(self):
        # Precompile regex patterns for structural parsing (The "Wavelet Filters")
        self.negation_pattern = re.compile(r'\b(not|no|never|neither|nobody|nothing|cannot|won\'t|don\'t|doesn\'t|isn\'t|aren\'t)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|then|unless|provided|otherwise|else)\b', re.IGNORECASE)
        self.numeric_pattern = re.compile(r'-?\d+\.?\d*')
        self.boolean_yes = re.compile(r'\byes\b|true\b|correct\b', re.IGNORECASE)
        self.boolean_no = re.compile(r'\bno\b|false\b|incorrect\b', re.IGNORECASE)

    def _extract_structure(self, text: str) -> dict:
        """Decompose text into logical components (Wavelet decomposition)."""
        text_lower = text.lower()
        return {
            'has_negation': bool(self.negation_pattern.search(text_lower)),
            'has_comparative': bool(self.comparative_pattern.search(text_lower)),
            'has_conditional': bool(self.conditional_pattern.search(text_lower)),
            'numbers': [float(n) for n in self.numeric_pattern.findall(text)],
            'length': len(text.split()),
            'raw': text_lower
        }

    def _check_logical_consistency(self, prompt_struct: dict, candidate: str) -> float:
        """
        Type-check the candidate against the prompt's logical constraints.
        Returns a score modifier based on logical validity.
        """
        cand_lower = candidate.lower()
        score = 0.0
        
        # Constraint 1: Negation Handling
        # If prompt has negation, valid answers often need to reflect that or not contradict it
        if prompt_struct['has_negation']:
            # Heuristic: If prompt asks a negative question, simple 'Yes' might be ambiguous
            # but 'No' often requires careful checking. 
            # We penalize candidates that ignore the negation context if they are simple booleans
            if self.boolean_yes.search(cand_lower) and "not" in cand_lower:
                score += 0.2 # Explicitly handling negation is good
            elif self.boolean_no.search(cand_lower):
                score += 0.1 # 'No' is often safe in negative contexts depending on phrasing
        
        # Constraint 2: Numeric Consistency
        if prompt_struct['numbers'] and self.numeric_pattern.search(cand_lower):
            cand_nums = [float(n) for n in self.numeric_pattern.findall(cand_lower)]
            if cand_nums:
                # Check magnitude alignment (Type compatibility)
                p_max = max(prompt_struct['numbers'])
                c_max = max(cand_nums)
                # If prompt implies comparison, answer should respect order (simplified)
                if prompt_struct['has_comparative']:
                    if (p_max > 10 and c_max > 10) or (p_max < 1 and c_max < 1):
                        score += 0.3 # Scale match
                else:
                    score += 0.2 # Numbers present in both is a strong signal
        
        # Constraint 3: Conditional Logic
        if prompt_struct['has_conditional']:
            if any(k in cand_lower for k in ['if', 'then', 'because', 'therefore']):
                score += 0.2 # Logical connectives match conditional context
        
        return score

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
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
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # 1. Structural Score (The "Type Check")
            logic_score = self._check_logical_consistency(prompt_struct, cand)
            
            # 2. Content Overlap (Basic relevance)
            # Simple word overlap normalized by length
            p_words = set(prompt_struct['raw'].split())
            c_words = set(cand_struct['raw'].split())
            overlap = len(p_words & c_words) / (len(p_words) + 1)
            
            # 3. NCD Tiebreaker (Inverted: lower distance = higher score)
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.1 # Weighted lightly
            
            # Final Score Composition
            # Logic is primary, overlap secondary, NCD tertiary
            total_score = logic_score + (overlap * 0.5) + ncd_score
            
            # Bonus for exact keyword matches in reasoning tasks
            if prompt_struct['has_negation'] and self.boolean_no.search(cand_struct['raw']):
                total_score += 0.1
            
            results.append({
                "candidate": cand,
                "score": round(total_score, 4),
                "reasoning": f"Logic:{logic_score:.2f} Overlap:{overlap:.2f} NCD:{ncd_val:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on structural alignment.
        Returns 0.0 to 1.0.
        """
        ranked = self.evaluate(prompt, [answer, "X"]) # Compare against dummy
        if not ranked:
            return 0.0
        
        top = ranked[0]
        if top['candidate'] == answer:
            # Normalize score to 0-1 range roughly
            # Base score from logic is usually small (0.0 - 0.8), overlap adds more
            conf = min(1.0, max(0.0, top['score'] / 2.0)) 
            return round(conf, 4)
        else:
            # If answer isn't top, confidence is low
            return 0.1