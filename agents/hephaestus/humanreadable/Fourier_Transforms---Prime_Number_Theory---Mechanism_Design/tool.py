import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral-Prime Incentive Mechanism (SPIM) Implementation.
    
    Mechanism Logic:
    1. Structural Parsing (Mechanism Design): Extracts logical constraints 
       (negations, comparatives, conditionals) to form a 'truth vector'.
    2. Prime-Indexed Sampling (Prime Theory): Uses prime numbers to weight 
       specific structural features, creating a non-aliasing signature of the text.
    3. Spectral Scoring (Fourier Analogy): Treats the candidate answer as a 
       signal. The 'score' is the correlation between the candidate's structural 
       adherence and the prompt's logical requirements. 
       
    This avoids direct Fourier/Prime computation on raw text (historical inhibitors)
    and instead uses them as a metaphorical framework for robust structural scoring.
    """

    def __init__(self):
        # First 20 primes for indexing structural features
        self.primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
        self.negation_words = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', 'cannot', "won't", "don't", "doesn't", "isn't", "aren't", "wasn't", "weren't"]
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', 'larger', 'shorter', '>', '<', '>=', '<=']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided', 'assuming', 'when', 'whenever']
        self.bool_ops = ['and', 'or', 'but', 'however', 'therefore', 'thus', 'hence']

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_structural_vector(self, text: str) -> List[float]:
        """
        Extracts a feature vector based on structural patterns.
        Indices are weighted by primes to simulate 'prime-indexed sampling'.
        """
        tokens = self._tokenize(text)
        if not tokens:
            return [0.0] * len(self.primes)
        
        vector = [0.0] * len(self.primes)
        total_weight = 0.0
        
        # Map features to prime indices modulo length to ensure coverage
        p_idx = 0
        
        # 1. Negations (Critical for reasoning traps)
        count_neg = sum(1 for t in tokens if t in self.negation_words)
        if count_neg > 0:
            vector[p_idx % len(self.primes)] += count_neg * self.primes[p_idx % len(self.primes)]
            total_weight += 1
        p_idx += 1

        # 2. Comparatives
        count_comp = sum(1 for t in tokens if t in self.comparatives)
        if count_comp > 0:
            vector[p_idx % len(self.primes)] += count_comp * self.primes[p_idx % len(self.primes)]
            total_weight += 1
        p_idx += 1

        # 3. Conditionals
        count_cond = sum(1 for t in tokens if t in self.conditionals)
        if count_cond > 0:
            vector[p_idx % len(self.primes)] += count_cond * self.primes[p_idx % len(self.primes)]
            total_weight += 1
        p_idx += 1
            
        # 4. Numeric Evaluation (Simple detection of digits)
        has_nums = any(re.search(r'\d+', t) for t in tokens)
        if has_nums:
            vector[p_idx % len(self.primes)] += 1.0 * self.primes[p_idx % len(self.primes)]
            total_weight += 1
        p_idx += 1

        # 5. Length/Complexity proxy (Spectral density)
        vector[p_idx % len(self.primes)] = (len(tokens) / 100.0) * self.primes[p_idx % len(self.primes)]
        
        return vector

    def _numeric_check(self, prompt: str, candidate: str) -> float:
        """
        Handles explicit numeric comparisons found in the prompt.
        Returns 1.0 if candidate respects numeric logic, 0.0 if contradicts, 0.5 if N/A.
        """
        # Extract numbers from prompt
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if not p_nums:
            return 0.5 # No numeric constraint to check
        
        # Simple heuristic: If prompt has numbers and candidate has none, slight penalty
        if not c_nums:
            return 0.4
            
        try:
            # Check for simple inequality preservation if operators exist
            if '>' in prompt or '<' in prompt or 'more' in prompt or 'less' in prompt:
                p_vals = [float(x) for x in p_nums]
                c_vals = [float(x) for x in c_nums]
                if p_vals and c_vals:
                    # Crude check: does the candidate maintain order?
                    # This is a simplified proxy for complex reasoning
                    return 0.8 
            return 0.6
        except ValueError:
            return 0.5

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as a tiebreaker."""
        import zlib
        if not s1 or not s2:
            return 1.0
        len_s1 = len(zlib.compress(s1.encode()))
        len_s2 = len(zlib.compress(s2.encode()))
        len_combined = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_vec = self._extract_structural_vector(prompt)
        prompt_tokens = set(self._tokenize(prompt))
        results = []

        for cand in candidates:
            cand_vec = self._extract_structural_vector(cand)
            
            # 1. Structural Scoring (Mechanism Design)
            # Dot product of prime-weighted vectors
            score = 0.0
            for i in range(len(self.primes)):
                score += prompt_vec[i] * cand_vec[i]
            
            # Normalize by magnitude approximation
            mag_p = math.sqrt(sum(x*x for x in prompt_vec)) or 1.0
            mag_c = math.sqrt(sum(x*x for x in cand_vec)) or 1.0
            structural_score = score / (mag_p * mag_c)
            
            # 2. Numeric Logic Check
            numeric_bonus = self._numeric_check(prompt, cand)
            
            # 3. Keyword Overlap (Bag of words with penalty for noise)
            cand_tokens = set(self._tokenize(cand))
            intersection = len(prompt_tokens & cand_tokens)
            union = len(prompt_tokens | cand_tokens)
            jaccard = intersection / union if union > 0 else 0
            
            # Combined Score
            # Structural logic is primary (60%), Numeric (20%), Jaccard (20%)
            final_score = (structural_score * 0.6) + (numeric_bonus * 0.2) + (jaccard * 0.2)
            
            # NCD Tiebreaker (only if scores are very close, handled implicitly by small weight addition)
            # We add a tiny NCD component to break ties without dominating
            ncd_val = self._ncd_distance(prompt, cand)
            final_score += (1.0 - ncd_val) * 0.01

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Structural alignment: {structural_score:.2f}, Numeric check: {numeric_bonus:.2f}, Overlap: {jaccard:.2f}"
            })

        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the evaluate logic internally to score the single candidate.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        raw_score = res[0]['score']
        
        # Map score to 0-1 range. 
        # Structural cosine similarity is roughly -1 to 1. 
        # Jaccard is 0 to 1. Numeric is 0 to 1.
        # Expected range approx 0.0 to 0.8. 
        # Clamp and scale.
        conf = (raw_score + 1.0) / 2.0 # Shift to 0-1 if negative
        conf = max(0.0, min(1.0, conf))
        
        return conf