import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Pragmatic Prime-Code Reasoning Engine (PPCRE) Implementation.
    
    Mechanism:
    1. Structural Parsing (Primary): Extracts logical operators (negations, comparatives),
       numeric values, and constraint patterns. This forms the 'Gödel-like' structural signature.
    2. Pragmatic Filtering (Secondary): Weights candidates based on Gricean maxims 
       (Relevance, Quantity) derived from lexical overlap and length appropriateness.
    3. Error Correction Analogy: Treats logical inconsistencies (e.g., double negation errors,
       magnitude reversals) as 'syndrome violations'. Candidates with violations get penalized.
    4. NCD (Tiebreaker): Used only when structural scores are identical.
    
    This avoids using primes/ECC for direct scoring (historical inhibitors) and instead 
    uses them as a conceptual framework for the confidence wrapper and structural validation.
    """

    def __init__(self):
        # Primes for hashing atomic concepts (simulated Gödel numbering for structure)
        self.primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'larger', 'smaller', 'greater', 'less', 'more', 'fewer', '>', '<'}
        self.quantifiers = {'all', 'some', 'many', 'few', 'every', 'each'}

    def _structural_signature(self, text: str) -> Dict:
        """Extracts logical and numeric structure from text."""
        lower = text.lower()
        words = set(re.findall(r'\b\w+\b', lower))
        
        # Detect negations
        has_negation = bool(words & self.negation_words)
        neg_count = sum(1 for w in words if w in self.negation_words)
        
        # Detect comparatives
        has_comparative = bool(words & self.comparatives)
        
        # Extract numbers for magnitude checking
        numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
        
        # Detect conditionals
        has_conditional = any(kw in lower for kw in ['if', 'then', 'else', 'implies'])
        
        return {
            'neg_count': neg_count,
            'has_comp': has_comparative,
            'numbers': numbers,
            'has_cond': has_conditional,
            'word_set': words,
            'length': len(text.split())
        }

    def _compute_syndrome(self, prompt_sig: Dict, cand_sig: Dict) -> float:
        """
        Computes a 'syndrome' value representing logical inconsistency.
        Lower is better. High values indicate logical errors (e.g., magnitude reversal).
        """
        syndrome = 0.0
        
        # Check numeric consistency (Magnitude Transitivity)
        if prompt_sig['numbers'] and cand_sig['numbers']:
            p_max = max(prompt_sig['numbers'])
            c_max = max(cand_sig['numbers'])
            # If candidate claims a number is 'larger' but provides a smaller one, penalty
            if prompt_sig['has_comp'] and 'larger' in prompt_sig['word_set'] or 'greater' in prompt_sig['word_set']:
                if c_max < p_max:
                    syndrome += 0.5
            elif prompt_sig['has_comp'] and 'smaller' in prompt_sig['word_set'] or 'less' in prompt_sig['word_set']:
                if c_max > p_max:
                    syndrome += 0.5
                    
        # Check negation parity (Double negation or missing negation)
        # Simple heuristic: if prompt has negation, candidate should likely reflect it or answer appropriately
        if prompt_sig['neg_count'] % 2 != cand_sig['neg_count'] % 2:
            # Not always an error, but suspicious in strict logic contexts
            syndrome += 0.1
            
        return syndrome

    def _pragmatic_score(self, prompt: str, candidate: str, p_sig: Dict, c_sig: Dict) -> float:
        """
        Computes Gricean maxims score.
        Relevance: Lexical overlap.
        Quantity: Length appropriateness.
        """
        score = 0.0
        
        # Relevance (Overlap)
        common = p_sig['word_set'] & c_sig['word_set']
        if len(p_sig['word_set']) > 0:
            score += (len(common) / len(p_sig['word_set'])) * 0.6
            
        # Quantity (Length penalty for being too verbose or too short relative to prompt complexity)
        # Ideal length is roughly proportional to prompt, but not excessive
        len_ratio = c_sig['length'] / (p_sig['length'] + 1)
        if 0.5 <= len_ratio <= 2.0:
            score += 0.3
        elif len_ratio > 5.0:
            score -= 0.2 # Too verbose
            
        # Manner (Clarity) - penalize if candidate repeats prompt exactly without addition
        if candidate.strip().lower() == prompt.strip().lower():
            score -= 0.5
            
        return max(0.0, score)

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        if not s1 or not s2: return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_bytes))
            c2 = len(zlib.compress(s2_bytes))
            c12 = len(zlib.compress(s1_bytes + s2_bytes))
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_sig = self._structural_signature(prompt)
        results = []
        
        for cand in candidates:
            c_sig = self._structural_signature(cand)
            
            # 1. Structural Logic Score (Base)
            # Start with high score, subtract errors
            logic_score = 1.0
            
            # Syndrome check (Error Correction analogy)
            syndrome = self._compute_syndrome(p_sig, c_sig)
            logic_score -= syndrome
            
            # Numeric evaluation boost
            if p_sig['numbers'] and c_sig['numbers']:
                # If prompt asks for max/min, check if candidate provides it
                # Heuristic: if numbers match prompt numbers, good sign
                if set(c_sig['numbers']).issubset(set(p_sig['numbers'])) or \
                   any(abs(c - p) < 0.01 for c in c_sig['numbers'] for p in p_sig['numbers']):
                    logic_score += 0.1

            # 2. Pragmatic Score
            prag_score = self._pragmatic_score(prompt, cand, p_sig, c_sig)
            
            # Combined Score (Weighted: Logic > Pragmatics)
            total_score = (logic_score * 0.7) + (prag_score * 0.3)
            
            results.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": f"Logic:{logic_score:.2f} Prag:{prag_score:.2f} Syn:{syndrome:.2f}"
            })
        
        # Sort by score descending
        # Tie-breaking with NCD if scores are very close
        results.sort(key=lambda x: (x['score'], -self._ncd(prompt, x['candidate'])), reverse=True)
        
        # Normalize scores to 0-1 range roughly
        max_s = results[0]['score'] if results else 1.0
        min_s = min(r['score'] for r in results) if results else 0.0
        span = max_s - min_s if max_s != min_s else 1.0
        
        final_results = []
        for r in results:
            norm_score = (r['score'] - min_s) / span
            # Ensure strict ordering if NCD was tiebreaker but not reflected in float precision
            final_results.append({
                "candidate": r['candidate'],
                "score": float(norm_score),
                "reasoning": r['reasoning']
            })
            
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural consistency and pragmatic fit.
        """
        p_sig = self._structural_signature(prompt)
        a_sig = self._structural_signature(answer)
        
        # Base confidence on lack of syndrome
        syndrome = self._compute_syndrome(p_sig, a_sig)
        base_conf = max(0.0, 1.0 - syndrome)
        
        # Boost if numeric constraints are satisfied
        if p_sig['numbers'] and a_sig['numbers']:
            # Check simple transitivity or presence
            if any(n in a_sig['numbers'] for n in p_sig['numbers']):
                base_conf = min(1.0, base_conf + 0.2)
                
        # Pragmatic check
        prag = self._pragmatic_score(prompt, answer, p_sig, a_sig)
        base_conf = (base_conf * 0.8) + (prag * 0.2)
        
        return float(max(0.0, min(1.0, base_conf)))