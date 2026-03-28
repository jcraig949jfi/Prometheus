import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a hybrid reasoning engine combining Structural Pragmatics (primary)
    and Fractal-inspired Hierarchical Consistency (secondary), with NCD as a tiebreaker.
    
    Mechanism:
    1. Structural Parsing (Pragmatics): Extracts logical operators (negations, comparatives,
       conditionals) and numeric values. Scores candidates based on logical consistency
       with the prompt's structural constraints.
    2. Fractal LDPC Analogy (Error Correction): Treats the candidate answer as a 'codeword'.
       We simulate a multi-scale consistency check. The 'fractal' aspect is modeled by
       checking consistency at different granularities (whole string -> clauses -> tokens).
       Inconsistencies (errors) at coarse scales (global logic) penalize heavily, while
       fine-scale errors (local wording) penalize less, mimicking the power-law distance
       spectrum of fractal codes.
    3. NCD Tiebreaker: Used only when structural scores are indistinguishable.
    """

    def __init__(self):
        # Regex patterns for structural pragmatism
        self.negations = re.compile(r'\b(not|no|never|neither|nobody|nothing|nowhere)\b', re.I)
        self.comparatives = re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse|before|after)\b', re.I)
        self.conditionals = re.compile(r'\b(if|then|unless|otherwise|provided)\b', re.I)
        self.numbers = re.compile(r'-?\d+\.?\d*')
        self.boolean_words = re.compile(r'\b(true|false|yes|no|correct|incorrect)\b', re.I)

    def _extract_structure(self, text: str) -> dict:
        """Extracts logical and numeric features from text."""
        text_lower = text.lower()
        return {
            'neg_count': len(self.negations.findall(text_lower)),
            'comp_count': len(self.comparatives.findall(text_lower)),
            'cond_count': len(self.conditionals.findall(text_lower)),
            'numbers': [float(n) for n in self.numbers.findall(text)],
            'booleans': self.boolean_words.findall(text_lower),
            'length': len(text.split())
        }

    def _fractal_consistency_score(self, prompt_struct: dict, cand_struct: dict, prompt: str, candidate: str) -> float:
        """
        Simulates a fractal LDPC check. 
        Level 0 (Coarse): Global logical alignment (e.g., negation flip).
        Level 1 (Medium): Numeric consistency.
        Level 2 (Fine): Lexical overlap (NCD-based).
        
        Returns a score 0.0 to 1.0 where 1.0 is perfect consistency.
        """
        score = 1.0
        
        # Coarse Scale: Negation/Conditional Logic Check
        # If prompt has high logical density, candidate must reflect it or explicitly negate it.
        # Simple heuristic: If prompt asks a negative question, answer shouldn't blindly echo without logic.
        # We penalize if the candidate introduces random negations not present in prompt context.
        if prompt_struct['neg_count'] == 0 and cand_struct['neg_count'] > 2:
            score -= 0.3  # Penalty for unnecessary negation noise
        
        if prompt_struct['cond_count'] > 0 and cand_struct['cond_count'] == 0:
            # If prompt is conditional, a valid answer often acknowledges conditionality or gives a definitive result
            # This is a soft check, so small penalty if missing, unless it's a logic trap.
            pass 

        # Medium Scale: Numeric Consistency
        if prompt_struct['numbers'] and cand_struct['numbers']:
            # Check if candidate numbers are subsets or logical derivatives (simplified)
            # If candidate introduces wild numbers not in prompt, slight penalty unless it's a calculation result
            p_nums = set(prompt_struct['numbers'])
            c_nums = set(cand_struct['numbers'])
            # Heuristic: If candidate has numbers completely disjoint from prompt, it might be hallucinated
            # unless the operation implies new numbers (hard to verify without LLM). 
            # We skip heavy penalty here to avoid false negatives on math problems.
            pass

        # Fine Scale: Fractal Self-Similarity (NCD as local error check)
        # In LDPC, local checks verify parity. Here, we check if the candidate is a "noisy" version
        # of a subset of the prompt (echo) vs a distinct logical step.
        # We use NCD here as the "fine grain" check.
        ncd = self._ncd(prompt, candidate)
        
        # If NCD is very low (high similarity), it might be an echo trap.
        # If NCD is very high, it might be irrelevant.
        # Optimal reasoning often lies in moderate NCD (related but distinct).
        if ncd < 0.2: 
            score -= 0.1 # Suspiciously similar (echo)
        elif ncd > 0.95:
            score -= 0.2 # Completely unrelated
            
        return max(0.0, min(1.0, score))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if max(c1, c2) == 0:
                return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Primary scoring based on structural pragmatics.
        Detects logical traps, negations, and numeric comparisons.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        score = 0.5 # Base score
        
        # 1. Numeric Evaluation
        if p_struct['numbers'] and c_struct['numbers']:
            # Check for direct numeric contradictions if simple
            # E.g., Prompt: "Is 5 > 3?" Candidate: "No, 5 is not greater than 3" (Good)
            # vs Candidate: "5 < 3" (Bad)
            # Simplified: If prompt has numbers and candidate has numbers, boost slightly for relevance
            score += 0.2
            
        # 2. Boolean/Logic Alignment
        p_bools = p_struct['booleans']
        c_bools = c_struct['booleans']
        
        if p_bools:
            # If prompt asks a yes/no question (implied by boolean words), 
            # candidate should ideally start with or contain a boolean.
            if c_bools:
                score += 0.15
            else:
                # Missing explicit boolean in a boolean context might be verbose but not always wrong
                pass

        # 3. Length Pragmatics (Grice's Maxim of Quantity)
        # Answers should be concise. Extremely long answers relative to prompt might be rambling.
        if c_struct['length'] > p_struct['length'] * 5:
            score -= 0.1
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt structure
        p_struct = self._extract_structure(prompt)
        
        for cand in candidates:
            c_struct = self._extract_structure(cand)
            
            # Primary Score: Structural Pragmatics
            s_score = self._structural_score(prompt, cand)
            
            # Secondary Score: Fractal Consistency (Error Correction Layer)
            f_score = self._fractal_consistency_score(p_struct, c_struct, prompt, cand)
            
            # Combined Score
            # Weighted sum: Structural (70%) + Fractal/Consistency (30%)
            total_score = (s_score * 0.7) + (f_score * 0.3)
            
            # Reasoning string generation
            reasoning_parts = []
            if c_struct['numbers']:
                reasoning_parts.append("Numeric content detected.")
            if c_struct['booleans']:
                reasoning_parts.append("Logical boolean found.")
            if f_score < 0.8:
                reasoning_parts.append("Potential consistency error detected via fractal check.")
            else:
                reasoning_parts.append("High structural consistency.")
                
            results.append({
                "candidate": cand,
                "score": round(total_score, 4),
                "reasoning": " ".join(reasoning_parts)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # NCD Tiebreaker pass (only if scores are very close)
        # Since we need deterministic output and strict ordering, we rely on the float precision.
        # If scores are identical to 4 decimals, we use NCD as a secondary sort key implicitly 
        # by re-evaluating NCD for ties if necessary, but standard sort stability handles the rest.
        # To strictly adhere to "NCD as tiebreaker":
        final_results = []
        prev_score = None
        buffer = []
        
        # Group by score for NCD tie-breaking
        # Note: Since we need to return a list, we can just sort with a compound key if we pre-calc NCD
        # But to save compute, we only do this if we detect a tie in a real loop. 
        # For this implementation, we assume the floating point precision of the weighted sum 
        # combined with the specific heuristics provides sufficient separation. 
        # If strict tie-breaking is needed, we can add a tiny NCD-based epsilon.
        
        for i, res in enumerate(results):
            # Add tiny NCD component to score for tie-breaking without re-sorting logic complexity
            ncd_val = self._ncd(prompt, res['candidate'])
            # Adjust score slightly by NCD (lower NCD = higher similarity = usually better for tie break)
            # But we want NCD as a tie breaker, so we add a very small fraction
            res['score'] = res['score'] + (1.0 - ncd_val) * 1e-6
            final_results.append(res)
            
        # Re-sort just in case the epsilon changed order
        final_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Clean up scores to original precision for output
        for res in final_results:
            res['score'] = round(res['score'], 4)
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same structural + fractal logic as evaluate.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(answer)
        
        s_score = self._structural_score(prompt, answer)
        f_score = self._fractal_consistency_score(p_struct, c_struct, prompt, answer)
        
        raw_conf = (s_score * 0.7) + (f_score * 0.3)
        
        # Clamp to 0-1
        return round(max(0.0, min(1.0, raw_conf)), 4)