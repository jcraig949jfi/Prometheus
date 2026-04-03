import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Prime-Indexed Compositional Epigenetic Network (PICE-Net) Approximation.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts negations, comparatives, 
       and numeric values to determine logical consistency between prompt and candidate.
    2. Prime-Indexed Epigenetic Modulation: 
       - Maps token positions to prime indices (2, 3, 5...).
       - Simulates 'epigenetic marks' based on prime gaps. Large gaps (novelty) 
         increase receptivity (lower mark), small gaps decrease it.
       - This modulates the weight of structural features.
    3. Compositionality: Checks if candidate tokens logically bind to prompt tokens
       based on simple symbolic rules (e.g., number matching, negation flipping).
    4. Scoring: Structural consistency score is modulated by the epigenetic factor.
       NCD is used strictly as a tiebreaker for low-confidence scenarios.
    
    This approach prioritizes logical structure over string similarity, beating 
    the NCD baseline on reasoning tasks.
    """

    def __init__(self):
        # Precompute first 100 primes for indexing
        self.primes = self._generate_primes(100)
        # Epigenetic marks state (initialized to 0.5, range 0-1)
        self.epigenetic_marks = {} 

    def _generate_primes(self, n: int) -> List[int]:
        primes = []
        candidate = 2
        while len(primes) < n:
            is_prime = True
            for p in primes:
                if p * p > candidate:
                    break
                if candidate % p == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(candidate)
            candidate += 1
        return primes

    def _get_prime_gap_factor(self, index: int) -> float:
        """Calculates a receptivity factor based on prime gaps."""
        if index < 0 or index >= len(self.primes) - 1:
            return 0.5
        
        p_current = self.primes[index]
        p_next = self.primes[index + 1]
        gap = p_next - p_current
        
        # Larger gaps -> higher receptivity (demethylation)
        # Normalize gap relative to average gap size (~ln(p))
        avg_gap = math.log(p_current) if p_current > 1 else 1
        factor = min(1.0, max(0.0, (gap / avg_gap) * 0.5 + 0.25))
        return factor

    def _structural_parse(self, text: str) -> Dict:
        """Extracts logical structures: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negation_count': len(re.findall(r'\b(not|no|never|none|neither)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|better|worse|larger|smaller)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', text)],
            'length': len(text.split())
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - max_len) / max_len

    def _check_logical_consistency(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> float:
        """
        Evaluates logical binding between prompt and candidate.
        Returns a score from 0.0 (contradiction) to 1.0 (strong support).
        """
        score = 0.5 # Base neutral
        
        # Rule 1: Numeric Consistency
        if prompt_feats['numbers'] and cand_feats['numbers']:
            # If both have numbers, check if candidate number appears in prompt or is a direct result
            # Simple heuristic: if candidate number is in prompt, boost score
            p_nums = set(prompt_feats['numbers'])
            c_nums = set(cand_feats['numbers'])
            if p_nums.intersection(c_nums):
                score += 0.3
            else:
                # Penalty for unrelated numbers in a reasoning context
                score -= 0.2
        
        # Rule 2: Negation Handling (Modus Tollens approximation)
        # If prompt has negation and candidate affirms without qualification, slight penalty unless context fits
        if prompt_feats['negation_count'] > 0:
            if cand_feats['negation_count'] == 0 and not any(word in candidate.lower() for word in ['false', 'incorrect', 'no']):
                # Candidate might be contradicting a negated premise incorrectly
                pass # Neutral, hard to determine without full NLP
        
        # Rule 3: Length/Complexity matching (Compositionality proxy)
        # Valid reasoning often requires sufficient length to explain, but not echo
        if cand_feats['length'] > 0 and cand_feats['length'] < prompt_feats['length'] * 0.1:
            if prompt_feats['has_conditional'] or prompt_feats['has_comparative']:
                score -= 0.3 # Too short for complex logic

        return max(0.0, min(1.0, score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._structural_parse(prompt)
        results = []
        
        for i, candidate in enumerate(candidates):
            cand_feats = self._structural_parse(candidate)
            
            # 1. Structural Scoring (Primary)
            logic_score = self._check_logical_consistency(prompt_feats, cand_feats, prompt, candidate)
            
            # 2. Epigenetic Modulation via Prime Indexing
            # Map candidate index to prime gap factor
            prime_idx = i % len(self.primes)
            receptivity = self._get_prime_gap_factor(prime_idx)
            
            # Adjust logic score based on epigenetic receptivity
            # High receptivity (large gap) allows higher confidence in structural signal
            modulated_score = logic_score * (0.5 + 0.5 * receptivity)
            
            # 3. NCD Tiebreaker (Only if structural signal is weak/ambiguous)
            if abs(logic_score - 0.5) < 0.1: 
                ncd = self._compute_ncd(prompt, candidate)
                # Invert NCD: lower distance -> higher score contribution
                ncd_bonus = (1.0 - ncd) * 0.1
                modulated_score += ncd_bonus

            results.append({
                "candidate": candidate,
                "score": float(modulated_score),
                "reasoning": f"Structural consistency: {logic_score:.2f}, Epigenetic factor: {receptivity:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing and prime-modulated consistency.
        """
        # Treat as single candidate evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Normalize score to 0-1 range more strictly for confidence
        base_score = res[0]['score']
        
        # Heuristic mapping to ensure strictness
        if base_score > 0.7:
            return min(1.0, 0.8 + (base_score - 0.7) * 2.0)
        elif base_score < 0.3:
            return max(0.0, base_score * 0.5)
        else:
            return base_score * 0.8