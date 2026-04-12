import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral Incentive-Compatible Reasoning Tool (SICRT).
    
    Mechanism:
    1. Spectral Analysis (Frequency Domain): Converts text into a frequency spectrum
       based on token repetition patterns. This detects 'periodicities' (repeated logic)
       and 'noise' (random guessing).
    2. Mechanism Design (VCG-style Truthfulness): 
       - Agents (candidates) are scored on structural alignment with the prompt.
       - A 'payment' (score boost) is awarded for truthful structural matching 
         (e.g., if prompt has negation, candidate must reflect it).
       - Misreporting (ignoring structural constraints) incurs a 'penalty' derived 
         from the spectral divergence between prompt and candidate.
    3. Reasoning: Uses structural parsing (negations, comparatives, numbers) as the 
       primary ground truth for the mechanism, with NCD as a tiebreaker.
    """

    def __init__(self):
        self.structural_keywords = {
            'negations': ['not', 'no', 'never', 'neither', 'none', 'cannot', "n't"],
            'comparatives': ['more', 'less', 'greater', 'smaller', 'larger', 'fewer', 'better', 'worse'],
            'conditionals': ['if', 'then', 'unless', 'otherwise', 'when', 'provided'],
            'logic_ops': ['and', 'or', 'implies', 'therefore', 'because']
        }
        self.number_pattern = re.compile(r"-?\d+\.?\d*")

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _compute_spectrum(self, text: str) -> Dict[str, float]:
        """
        Spectral Analysis: Computes a simplified Power Spectral Density (PSD) 
        analog based on token frequency distribution.
        """
        tokens = self._tokenize(text)
        if not tokens:
            return {}
        counts = {}
        for t in tokens:
            counts[t] = counts.get(t, 0) + 1
        
        # Normalize to get 'power' per token
        total = len(tokens)
        return {k: v/total for k, v in counts.items()}

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """
        Extracts structural features for Mechanism Design validation.
        """
        lower_text = text.lower()
        tokens = self._tokenize(text)
        
        # 1. Negation Count
        neg_count = sum(lower_text.count(w) for w in self.structural_keywords['negations'])
        
        # 2. Comparative Count
        comp_count = sum(lower_text.count(w) for w in self.structural_keywords['comparatives'])
        
        # 3. Conditional Count
        cond_count = sum(lower_text.count(w) for w in self.structural_keywords['conditionals'])
        
        # 4. Numeric Extraction (sorted for comparison)
        numbers = [float(n) for n in self.number_pattern.findall(text)]
        numbers.sort()
        
        return {
            'negations': neg_count,
            'comparatives': comp_count,
            'conditionals': cond_count,
            'numbers': numbers,
            'length': len(tokens)
        }

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        len1, len2 = len(b1), len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _spectral_divergence(self, spec1: Dict[str, float], spec2: Dict[str, float]) -> float:
        """
        Computes a distance metric between two spectral profiles.
        Analogous to KL-divergence or Euclidean distance in frequency domain.
        """
        all_keys = set(spec1.keys()) | set(spec2.keys())
        if not all_keys:
            return 0.0
        
        dist = 0.0
        for k in all_keys:
            p = spec1.get(k, 0.0)
            q = spec2.get(k, 0.0)
            # Euclidean component
            dist += (p - q) ** 2
        return math.sqrt(dist)

    def _mechanism_score(self, prompt_struct: Dict, cand_struct: Dict, prompt_spec: Dict, cand_spec: Dict) -> float:
        """
        Mechanism Design Layer:
        Calculates a 'truthful payment' score.
        - High reward for matching structural constraints (e.g., if prompt has numbers, answer should too).
        - Penalty for spectral divergence (indicating the candidate doesn't 'resonate' with the prompt's logic).
        """
        score = 1.0
        
        # Constraint 1: Numeric Consistency
        # If prompt has numbers, candidate must have numbers to be valid (heuristic)
        if len(prompt_struct['numbers']) > 0:
            if len(cand_struct['numbers']) == 0:
                score -= 0.4 # Heavy penalty for ignoring numeric context
            else:
                # Check magnitude alignment (loose)
                p_avg = sum(prompt_struct['numbers']) / len(prompt_struct['numbers'])
                c_avg = sum(cand_struct['numbers']) / len(cand_struct['numbers'])
                if p_avg != 0:
                    ratio = abs(c_avg - p_avg) / (abs(p_avg) + 1e-6)
                    score -= min(0.3, ratio * 0.1) # Small penalty for magnitude drift

        # Constraint 2: Logical Operator Alignment
        # If prompt is conditional, ideal answer might acknowledge it (hard to verify perfectly, so use spectral overlap)
        
        # Spectral Residual Test (The 'PSD' check)
        # Low divergence = high resonance = truthful alignment
        divergence = self._spectral_divergence(prompt_spec, cand_spec)
        score -= divergence * 0.5 # Penalty scales with spectral mismatch

        # Constraint 3: Negation/Logic Flip Detection
        # If prompt asks "What is NOT...", and candidate contains high negation count, it might be right.
        # This is a simple proxy: if prompt has negations, candidate having SOME negations is often good 
        # (unless it's a double negative trap, but we aim for baseline beating).
        if prompt_struct['negations'] > 0:
            if cand_struct['negations'] == 0:
                score -= 0.1 # Slight penalty for ignoring negation context

        return max(0.0, score)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        prompt_spec = self._compute_spectrum(prompt)
        
        scored_candidates = []
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            cand_spec = self._compute_spectrum(cand)
            
            # 1. Structural Parsing Score (Primary Signal)
            # We use the mechanism design layer to combine structural checks
            mech_score = self._mechanism_score(prompt_struct, cand_struct, prompt_spec, cand_spec)
            
            # 2. NCD Tiebreaker (Secondary Signal)
            # NCD is good for semantic similarity when structure is ambiguous
            ncd_val = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val # Convert distance to similarity
            
            # Combine: Weight structural/mechanism heavily, NCD as tiebreaker/refiner
            # If mechanism score is high (truthful), boost it. 
            # If mechanism score is low, NCD can't save it if it's structurally wrong.
            final_score = (mech_score * 0.7) + (ncd_score * 0.3)
            
            reasoning = f"Structural alignment: {mech_score:.2f}, Spectral resonance: {1.0 - self._spectral_divergence(prompt_spec, cand_spec):.2f}"
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the evaluation score of the single candidate.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        # Normalize score to 0-1 range roughly, though evaluate already produces ~0-1
        return min(1.0, max(0.0, results[0]["score"]))