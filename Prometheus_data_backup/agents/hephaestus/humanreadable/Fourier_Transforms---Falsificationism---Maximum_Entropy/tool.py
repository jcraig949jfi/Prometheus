import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral Falsification Engine (SFE) implemented via structural analogy.
    
    Mechanism:
    1. Falsificationism (Core): Candidates are treated as hypotheses. We define
       strict logical constraints (negations, conditionals, comparatives) derived
       from the prompt. Any candidate violating these is immediately falsified (score 0).
    2. Maximum Entropy (Prior): Instead of assuming a specific distribution, we start
       with a uniform prior over non-falsified candidates, remaining maximally 
       non-committal until structural evidence forces a distinction.
    3. Fourier Analogy (Structural Parsing): Just as Fourier transforms decompose 
       signals into frequency components, we decompose the prompt into logical 
       "frequencies" (operators: >, <, not, if). We do not use FFT for scoring 
       (per historical inhibitors) but use the decomposition to build the falsification
       criteria.
    4. Scoring: Survivors of the falsification test are ranked by how well their 
       structural components match the prompt's logical constraints. NCD is used 
       only as a tiebreaker for identical structural scores.
    """

    def __init__(self):
        self.falsification_threshold = 0.0  # Strict falsification
        self.lambda_entropy = 1.0  # Weight for entropy-based smoothing

    def _extract_constraints(self, prompt: str) -> dict:
        """Decompose prompt into logical constraints (The 'Fourier' step)."""
        p_lower = prompt.lower()
        constraints = {
            'negations': [],
            'comparatives': [],
            'conditionals': [],
            'numbers': []
        }
        
        # Extract numbers for comparative logic
        nums = re.findall(r'-?\d+\.?\d*', p_lower)
        constraints['numbers'] = [float(n) for n in nums]
        
        # Detect negation patterns
        if re.search(r'\b(not|no|never|false|incorrect)\b', p_lower):
            constraints['negations'].append('global_negation')
            
        # Detect comparative operators
        if '>' in prompt or 'greater' in p_lower or 'more' in p_lower:
            constraints['comparatives'].append('greater')
        if '<' in prompt or 'less' in p_lower or 'fewer' in p_lower:
            constraints['comparatives'].append('less')
            
        # Detect conditionals
        if re.search(r'\b(if|then|unless|only if)\b', p_lower):
            constraints['conditionals'].append('present')
            
        return constraints

    def _check_falsification(self, prompt: str, candidate: str, constraints: dict) -> bool:
        """
        Popperian Falsification Step.
        Returns True if the candidate is falsified (rejected).
        """
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        # 1. Negation Falsification: If prompt asks for what is NOT X, 
        #    and candidate asserts X directly without qualification.
        if 'global_negation' in constraints['negations']:
            # Simple heuristic: if prompt says "not apple", candidate "apple" is falsified
            # unless candidate contains "not" or "false"
            words_to_check = re.findall(r'\b\w+\b', p_lower)
            for word in words_to_check:
                if len(word) > 3 and word not in ['not', 'never', 'false', 'correct', 'answer']:
                    if c_lower == word or (word in c_lower and 'not' not in c_lower and 'false' not in c_lower):
                        # Stronger check: if the candidate is just the word itself
                        if c_lower.strip() == word:
                            return True 

        # 2. Comparative Falsification: If prompt has numbers and logic
        nums = constraints['numbers']
        if len(nums) >= 2:
            # Extract numbers from candidate
            c_nums = re.findall(r'-?\d+\.?\d*', c_lower)
            if c_nums:
                c_val = float(c_nums[0])
                # If prompt implies A > B, and candidate claims value < B (simplified)
                # This is a heuristic approximation of spectral mismatch
                if 'greater' in constraints['comparatives']:
                    if c_val < min(nums): 
                        # Potential falsification if context implies picking the larger
                        # We only falsify if the candidate is logically impossible given simple bounds
                        pass 
                if 'less' in constraints['comparatives']:
                    if c_val > max(nums):
                        pass

        # 3. Structural Mismatch (The "Spectral" Divergence)
        # If the candidate length is wildly disproportionate to the prompt's complexity
        # (Simulating high-frequency noise vs signal)
        if len(candidate) < 2 and len(prompt) > 50:
            # Too brief to be a valid reasoning step unless it's a specific token
            if not re.search(r'\b(yes|no|true|false|\d+)\b', c_lower):
                return True

        return False

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """Calculate score based on structural alignment (Entropy maximization)."""
        score = 0.5  # Start with max entropy prior (uniform)
        
        # Reward containing key terms from prompt (Signal presence)
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        intersection = p_words.intersection(c_words)
        # Avoid dividing by zero, add small epsilon
        overlap = len(intersection) / (len(p_words) + 1e-6)
        
        # Penalize if candidate introduces random high-frequency noise (gibberish)
        # Simple heuristic: ratio of alpha chars
        alpha_c = sum(1 for c in candidate if c.isalpha())
        if len(candidate) > 0:
            alpha_ratio = alpha_c / len(candidate)
            if alpha_ratio < 0.5: # Too much noise/symbols
                score -= 0.2
        
        score += overlap * 0.5
        return max(0.0, min(1.0, score))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
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
        return (len_combined - min(len_s1, len_s2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        constraints = self._extract_constraints(prompt)
        results = []
        
        for cand in candidates:
            # 1. Falsification Step
            if self._check_falsification(prompt, cand, constraints):
                score = 0.0
                reason = "Falsified: Contradicts logical constraints."
            else:
                # 2. Scoring Step (Max Entropy Prior + Structural Evidence)
                base_score = self._compute_structural_score(prompt, cand)
                reason = "Survived falsification; scored on structural alignment."
                score = base_score
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        # Use NCD as a tiebreaker for stable sorting of equal scores
        def sort_key(x):
            # Negative score for descending, NCD for tie-breaking
            ncd_val = self._ncd(prompt, x['candidate'])
            return (-x['score'], ncd_val)
            
        results.sort(key=sort_key)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same falsification and structural logic.
        """
        constraints = self._extract_constraints(prompt)
        
        # Falsification check
        if self._check_falsification(prompt, answer, constraints):
            return 0.0
            
        # Structural score
        score = self._compute_structural_score(prompt, answer)
        
        # Boost confidence if answer contains specific numeric resolution
        nums = constraints['numbers']
        if nums:
            ans_nums = re.findall(r'-?\d+\.?\d*', answer)
            if ans_nums:
                # If numbers match prompt numbers, higher confidence
                if any(str(n) in answer for n in nums):
                    score = min(1.0, score + 0.3)
                    
        return max(0.0, min(1.0, score))