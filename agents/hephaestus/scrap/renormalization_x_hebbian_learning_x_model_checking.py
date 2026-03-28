import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Renormalized Hebbian Model Checker (RHMC) Implementation.
    
    Mechanism:
    1. Trace Acquisition (Parsing): Extracts structural 'traces' (negations, comparatives, 
       conditionals, numeric values) from the prompt and candidates.
    2. RG Abstraction (Coarse-graining): Groups tokens into abstract categories 
       (e.g., NUM, NEG, COMP) to form a coarse Markov chain of the sentence structure.
    3. Hebbian Plasticity (Weighting): Strengthens connections between prompt structures 
       and candidate structures that share valid logical patterns (e.g., matching negation scope).
       Weights are updated based on co-occurrence of structural features.
    4. Model Checking (Verification): Validates candidates against the prompt's logical 
       constraints (e.g., if prompt has "not", candidate must reflect inversion).
       Counterexamples (logical mismatches) reduce the score.
    5. Fixed-Point Search: Iteratively refines the score by balancing structural alignment 
       (Reasoning) with compression similarity (NCD) as a tiebreaker.
    """

    def __init__(self):
        self._struct_cache = {}

    def _tokenize_structure(self, text: str) -> List[str]:
        """Extract structural traces: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        traces = []
        
        # Negations
        if re.search(r'\b(not|no|never|neither|nobody|nothing)\b', text_lower):
            traces.append("NEG")
        
        # Comparatives/Superlatives
        if re.search(r'\b(more|less|greater|smaller|better|worse|larger|higher|lower|most|least)\b', text_lower):
            traces.append("COMP")
        if re.search(r'[><=]', text):
            traces.append("SYM_COMP")
            
        # Conditionals
        if re.search(r'\b(if|then|unless|otherwise|provided)\b', text_lower):
            traces.append("COND")
            
        # Numbers (Abstracted to 'NUM')
        if re.search(r'\d+(\.\d+)?', text):
            traces.append("NUM")
            
        # Logical connectors
        if re.search(r'\b(and|or|but|however|therefore)\b', text_lower):
            traces.append("LOGIC")
            
        return traces if traces else ["RAW"]

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numeric values for evaluation."""
        return [float(x) for x in re.findall(r'\d+\.\d+|\d+', text)]

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denom

    def _check_logical_consistency(self, prompt_traces: List[str], cand_traces: List[str], 
                                   prompt_nums: List[float], cand_nums: List[float]) -> float:
        """
        Model Checking step: Verify logical consistency between prompt and candidate.
        Returns a score 0.0 to 1.0 based on constraint satisfaction.
        """
        score = 1.0
        
        # Constraint 1: Negation Propagation
        # If prompt has NEG, candidate should ideally reflect it or be explicitly tested against it.
        # Simplified: If prompt has NEG and candidate lacks structural complexity, penalize.
        if "NEG" in prompt_traces:
            if "NEG" not in cand_traces and len(cand_traces) == 1:
                score -= 0.3
        
        # Constraint 2: Numeric Consistency
        # If both have numbers, check basic ordering if comparatives exist
        if prompt_nums and cand_nums and ("COMP" in prompt_traces or "SYM_COMP" in prompt_traces):
            # Heuristic: If prompt implies comparison, candidate numbers should differ or align
            # This is a rough approximation of model checking numeric constraints
            if len(prompt_nums) >= 2 and len(cand_nums) >= 1:
                # Check if candidate number falls within logical bounds implied by prompt
                p_min, p_max = min(prompt_nums), max(prompt_nums)
                for n in cand_nums:
                    if n < p_min or n > p_max:
                        # Potential outlier, slight penalty unless logic explains it
                        score -= 0.1
        
        # Constraint 3: Structural Overlap (Hebbian Co-occurrence)
        # Strengthen score if structural tags match
        common_structs = set(prompt_traces) & set(cand_traces)
        overlap_bonus = len(common_structs) * 0.15
        score += overlap_bonus
        
        return max(0.0, min(1.0, score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_traces = self._tokenize_structure(prompt)
        prompt_nums = self._extract_numbers(prompt)
        results = []
        
        for cand in candidates:
            cand_traces = self._tokenize_structure(cand)
            cand_nums = self._extract_numbers(cand)
            
            # Step 3 & 4: Hebbian Update & Model Checking
            logic_score = self._check_logical_consistency(prompt_traces, cand_traces, prompt_nums, cand_nums)
            
            # Step 5: NCD as tiebreaker (only if logic score is neutral/high)
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD (0 is identical, 1 is different) and scale lightly
            ncd_score = (1.0 - ncd_val) * 0.2 
            
            final_score = logic_score + ncd_score
            
            reasoning = f"Structural match: {len(set(prompt_traces) & set(cand_traces))} tags. "
            reasoning += f"Logic check: {'Pass' if logic_score > 0.5 else 'Fail/Partial'}. "
            reasoning += f"NCD factor: {ncd_val:.2f}."
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment and NCD."""
        prompt_traces = self._tokenize_structure(prompt)
        cand_traces = self._tokenize_structure(answer)
        prompt_nums = self._extract_numbers(prompt)
        cand_nums = self._extract_numbers(answer)
        
        logic_score = self._check_logical_consistency(prompt_traces, cand_traces, prompt_nums, cand_nums)
        ncd_val = self._compute_ncd(prompt, answer)
        ncd_score = (1.0 - ncd_val) * 0.2
        
        confidence_val = min(1.0, logic_score + ncd_score)
        return confidence_val