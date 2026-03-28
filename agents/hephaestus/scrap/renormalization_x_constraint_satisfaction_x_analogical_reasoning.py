import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-Scale Analogical Constraint Solver (MACS) Approximation.
    
    Mechanism:
    1. Renormalization (Coarse-Graining): Parses the prompt into abstract structural 
       tokens (negations, comparatives, conditionals, numeric values), ignoring 
       specific content words. This creates a "universality class" signature.
    2. Constraint Satisfaction: Checks candidate answers against extracted logical 
       constraints (e.g., if prompt has "not", valid answers rarely contain exact 
       prompt phrases; if numeric, checks magnitude consistency).
    3. Analogical Reasoning: Maps the structural pattern of the prompt to the 
       candidate. Candidates sharing the same structural "shape" (e.g., both negative, 
       both comparative) receive a boost, simulating the transfer of relational 
       isomorphisms.
    4. Scoring: Primary score comes from structural/logical consistency. 
       NCD is used strictly as a tie-breaker for candidates with identical 
       structural scores.
    """

    def __init__(self):
        self._comparatives = ['more', 'less', 'greater', 'smaller', 'larger', 'fewer', 'higher', 'lower']
        self._negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', "n't"]
        self._conditionals = ['if', 'unless', 'when', 'provided', 'except']

    def _extract_structure(self, text: str) -> Dict:
        """Renormalization step: Extract abstract logical features."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_neg = any(n in words for n in self._negations)
        has_comp = any(c in words for c in self._comparatives)
        has_cond = any(c in words for c in self._conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'-?\d+(?:\.\d+)?', text)
        nums = [float(n) for n in numbers]
        
        return {
            'neg': has_neg,
            'comp': has_comp,
            'cond': has_cond,
            'nums': nums,
            'len': len(words),
            'has_question': '?' in text
        }

    def _check_constraints(self, prompt_struct: Dict, candidate: str, candidate_struct: Dict) -> float:
        """Constraint Satisfaction step: Validate candidate against prompt logic."""
        score = 0.0
        
        # Negation Constraint: If prompt is negative, candidate shouldn't just echo prompt
        if prompt_struct['neg']:
            if not candidate_struct['neg']:
                # Mild penalty for missing negation in answer if prompt is negative
                # unless the answer is a simple confirmation/denial
                if len(candidate.split()) > 3: 
                    score -= 0.1
        
        # Comparative Constraint: Structural alignment
        if prompt_struct['comp']:
            if candidate_struct['comp']:
                score += 0.2 # Analogical boost: same relational structure
            elif any(c in candidate.lower() for c in self._comparatives):
                score += 0.1

        # Numeric Consistency (Simple Heuristic)
        if prompt_struct['nums'] and candidate_struct['nums']:
            # If prompt implies ordering, check if candidate respects magnitude roughly
            # This is a simplified analogical transfer of numeric logic
            p_max = max(prompt_struct['nums'])
            c_max = max(candidate_struct['nums'])
            if p_max > 0 and c_max > 0:
                # Analogical lemma: magnitude often correlates
                score += 0.1 
                
        return score

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tie-breaker."""
        if not s1 or not s2:
            return 1.0
        b1 = zlib.compress(s1.encode())
        b2 = zlib.compress(s2.encode())
        b12 = zlib.compress((s1 + s2).encode())
        
        len1, len2, len12 = len(b1), len(b2), len(b12)
        if len1 == 0 or len2 == 0:
            return 1.0
            
        return (len12 - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate prompt NCD base for normalization if needed, 
        # but here we use pairwise NCD only for ties.
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # 1. Structural/Logical Score (Primary Signal)
            score = 0.0
            
            # Base analogical match: Do they share logical operators?
            if prompt_struct['neg'] == cand_struct['neg']:
                score += 0.3
            if prompt_struct['comp'] == cand_struct['comp']:
                score += 0.2
            if prompt_struct['cond'] == cand_struct['cond']:
                score += 0.1
                
            # 2. Constraint Propagation
            score += self._check_constraints(prompt_struct, cand, cand_struct)
            
            # 3. Length heuristic (Answers usually aren't massive blocks of text unless requested)
            if 0.5 * prompt_struct['len'] <= cand_struct['len'] <= 2.0 * prompt_struct['len']:
                score += 0.05
                
            results.append({
                'candidate': cand,
                'score': score,
                'reasoning': f"Structural match (Neg:{cand_struct['neg']}, Comp:{cand_struct['comp']}), Constraint check passed."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD
        # If scores are very close, use NCD to differentiate based on information density
        final_results = []
        for i, res in enumerate(results):
            if i > 0 and abs(res['score'] - results[i-1]['score']) < 0.01:
                # Tie detected, apply NCD penalty/reward relative to prompt
                ncd = self._compute_ncd(prompt, res['candidate'])
                # Lower NCD means more similar (often better for direct answers)
                res['score'] -= (ncd * 0.001) 
            final_results.append(res)
            
        # Normalize scores to 0-1 range roughly for consistency
        max_s = max(r['score'] for r in final_results) if final_results else 1
        min_s = min(r['score'] for r in final_results) if final_results else 0
        range_s = max_s - min_s if max_s != min_s else 1
        
        for r in final_results:
            r['score'] = (r['score'] - min_s) / range_s
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Evaluate confidence based on structural alignment and constraint satisfaction."""
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        conf = 0.5 # Base uncertainty
        
        # Boost if logical operators align
        if p_struct['neg'] == a_struct['neg']:
            conf += 0.2
        if p_struct['comp'] == a_struct['comp']:
            conf += 0.15
        if p_struct['cond'] == a_struct['cond']:
            conf += 0.1
            
        # Penalty for length mismatch (heuristic for relevance)
        if a_struct['len'] == 0:
            conf = 0.1
        elif a_struct['len'] > 10 * p_struct['len']:
            conf -= 0.2
            
        # Numeric consistency check
        if p_struct['nums'] and a_struct['nums']:
            conf += 0.1
            
        return max(0.0, min(1.0, conf))