import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a 'Chaos-Wavelet-Adaptive' inspired reasoning engine.
    
    Mechanism Analogy:
    1. Wavelet Feature Extraction: The prompt and candidates are decomposed into 
       structural 'coefficients' (negations, comparatives, conditionals, numbers).
       This acts as a multi-resolution filter, ignoring raw text noise (bag-of-words)
       and focusing on logical syntax.
       
    2. Chaos Quantification (Lyapunov Estimation): We measure the 'sensitivity to 
       initial conditions' by comparing the structural signature of the candidate 
       against the prompt's required logic. Small deviations in logical operators 
       (e.g., 'not' vs 'is') cause large divergence in the score, mimicking 
       chaotic sensitivity.
       
    3. Adaptive Control: The scoring law adapts based on the presence of specific 
       logical constraints. If a prompt contains a negation, the 'control parameter' 
       flips the scoring weight for matching affirmative statements.
       
    Primary Signal: Structural parsing (logic, numbers, constraints).
    Secondary Signal: NCD (compression distance) used only as a tie-breaker.
    """

    def __init__(self):
        # Logical keywords for structural parsing
        self.negations = {'not', 'no', 'never', 'none', 'cannot', 'impossible'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'provided'}
        self.booleans = {'true', 'false', 'yes', 'no'}
        
    def _extract_structure(self, text: str) -> dict:
        """Extracts logical coefficients from text (Wavelet decomposition analogy)."""
        t = text.lower()
        words = set(re.findall(r'\b\w+\b', t))
        
        # Count logical operators
        neg_count = len(words.intersection(self.negations))
        comp_count = len(words.intersection(self.comparatives))
        cond_count = len(words.intersection(self.conditionals))
        
        # Extract numbers for numeric evaluation
        numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', t)]
        
        # Extract boolean targets
        has_true = 'true' in words or 'yes' in words
        has_false = 'false' in words or 'no' in words
        
        return {
            'neg': neg_count,
            'comp': comp_count,
            'cond': cond_count,
            'nums': numbers,
            'bool_true': has_true,
            'bool_false': has_false,
            'len': len(text)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance as a tie-breaker."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def _evaluate_logic_match(self, prompt_struct: dict, cand_struct: dict) -> float:
        """
        Adaptive control law: Adjusts score based on logical consistency.
        Simulates Lyapunov sensitivity: Logical mismatches penalize heavily.
        """
        score = 1.0
        
        # 1. Negation Adaptation (Chaos sensitivity)
        # If prompt has negation, candidate should ideally reflect constraint handling
        if prompt_struct['neg'] > 0:
            # Penalize if candidate ignores negation context (simplified heuristic)
            # In a real system, this would check semantic entailment.
            # Here we boost candidates that are distinct from simple affirmations if prompt is complex
            if prompt_struct['neg'] > cand_struct.get('neg', 0):
                # Candidate lacks the negation depth of the prompt
                score -= 0.2 * (prompt_struct['neg'] - cand_struct.get('neg', 0))
        
        # 2. Numeric Evaluation (Constraint propagation)
        p_nums = prompt_struct['nums']
        c_nums = cand_struct['nums']
        
        if p_nums and c_nums:
            # Check for direct number presence or logical derivation
            # If prompt asks "is 9.11 < 9.9", candidate containing "True" gets boost
            if len(p_nums) >= 2 and len(c_nums) == 0:
                # Prompt has math, candidate has no numbers (maybe it's a boolean answer)
                if cand_struct['bool_true'] or cand_struct['bool_false']:
                    score += 0.3
            elif len(c_nums) > 0:
                # If both have numbers, check proximity or exact match depending on context
                # Simple heuristic: if candidate numbers are a subset of prompt, it's likely extraction
                if any(abs(c - p) < 1e-6 for c in c_nums for p in p_nums):
                    score += 0.2
                    
        # 3. Conditional/Comparative Structure
        if prompt_struct['cond'] > 0:
            if cand_struct['cond'] > 0 or cand_struct['bool_true'] or cand_struct['bool_false']:
                score += 0.1
            else:
                # Missing conditional logic in long form answer
                if cand_struct['len'] > 20: 
                    score -= 0.15

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # Primary Score: Structural Logic Match
            logic_score = self._evaluate_logic_match(prompt_struct, cand_struct)
            
            # Base similarity (NCD) - kept low weight to avoid bag-of-words traps
            # But used here as a baseline for "relevance" before tie-breaking
            ncd_val = self._compute_ncd(prompt, cand)
            
            # Hybrid Score: Logic dominant, NCD as secondary relevance filter
            # High NCD (dissimilar) is bad, Low NCD (similar) is good.
            # We invert NCD so 1.0 is perfect match, 0.0 is total mismatch
            ncd_similarity = 1.0 - ncd_val
            
            # Weighted combination: 80% Logic, 20% Textual Relevance
            final_score = (0.8 * max(0, logic_score)) + (0.2 * ncd_similarity)
            
            # Deterministic tie-breaking using NCD if scores are close
            results.append({
                "candidate": cand,
                "score": round(final_score, 6),
                "reasoning": f"Logic:{logic_score:.2f}, NCD:{ncd_similarity:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural alignment as the primary metric.
        """
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        # Calculate logic alignment
        logic_score = self._evaluate_logic_match(p_struct, a_struct)
        
        # Normalize logic score to 0-1 range roughly
        # Base assumption: logic_score centers around 1.0 for good matches
        conf = max(0.0, min(1.0, logic_score))
        
        # Boost if boolean consistency detected in simple Q&A
        p_lower = prompt.lower()
        a_lower = answer.lower()
        
        if ('true' in p_lower or 'false' in p_lower) and ('true' in a_lower or 'false' in a_lower):
            if ('true' in p_lower and 'true' in a_lower) or ('false' in p_lower and 'false' in a_lower):
                conf = min(1.0, conf + 0.3)
            elif ('true' in p_lower and 'false' in a_lower) or ('false' in p_lower and 'true' in a_lower):
                conf = max(0.0, conf - 0.5)

        return round(conf, 4)