import zlib
import math
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-scale Free-Energy Minimization Engine (Approximated).
    
    Mechanism:
    1. RG Coarse-Graining: Simulates Renormalization Group flow by compressing text
       at different 'scales' (block sizes). This extracts structural features while
       ignoring fine-grained noise (high-frequency fluctuations).
    2. Order Parameter Monitor: Calculates the variance of prediction errors (compression
       inefficiency) across scales. High variance indicates proximity to a 'phase transition'
       (high uncertainty/criticality).
    3. Active Inference Modulation:
       - Near Criticality (High Variance): Switches to 'Epistemic Foraging'. The scoring
         function prioritizes candidates that reduce model entropy (sharper distinction
         between compressed states) and penalizes ambiguity, effectively forcing a decision
         to resolve the phase transition.
       - Away from Criticality (Low Variance): Prioritizes 'Exploitation', relying on
         standard semantic similarity (NCD) to the prompt context.
    4. Scoring: Combines structural constraint satisfaction (negations, numerics) with
       the RG-modulated similarity score.
    """

    def __init__(self):
        self._scale_factors = [1, 2, 4, 8]  # RG block sizes

    def _compress_len(self, s: str) -> int:
        """Returns byte length of zlib compressed string."""
        if not s:
            return 0
        return len(zlib.compress(s.encode('utf-8')))

    def _coarse_grain(self, text: str, block_size: int) -> str:
        """
        Simulates RG coarse-graining by grouping characters and keeping only 
        the first char of each block (majority vote approximation).
        """
        if block_size <= 1:
            return text
        return ''.join(text[i] for i in range(0, len(text), block_size))

    def _calculate_rg_variance(self, text: str) -> float:
        """
        Calculates the 'Order Parameter' variance across scales.
        High variance implies the text structure changes significantly under coarse-graining,
        indicating criticality (high information content or noise).
        """
        if len(text) < 4:
            return 0.0
        
        lengths = []
        base_len = len(text)
        
        for k in self._scale_factors:
            coarse = self._coarse_grain(text, k)
            # Normalized compression distance proxy at this scale
            c_len = self._compress_len(coarse)
            lengths.append(c_len / (base_len / k + 1e-6))
            
        if len(lengths) < 2:
            return 0.0
            
        mean_l = sum(lengths) / len(lengths)
        variance = sum((x - mean_l) ** 2 for x in lengths) / len(lengths)
        return variance

    def _extract_structural_features(self, text: str) -> Dict[str, float]:
        """
        Extracts deterministic reasoning features:
        - Negation count
        - Numeric presence
        - Comparative keywords
        """
        text_lower = text.lower()
        score = 0.0
        
        # Negation handling (Modus Tollens support)
        negations = ['not', 'no', 'never', 'none', 'cannot', "n't"]
        neg_count = sum(1 for n in negations if n in text_lower)
        score += neg_count * 0.1
        
        # Numeric evaluation hint
        if re.search(r'\d+(\.\d+)?', text):
            score += 0.2
            
        # Comparatives
        comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller']
        if any(c in text_lower for c in comparatives):
            score += 0.15
            
        return {'structural_bonus': score}

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        if not s1 or not s2:
            return 1.0
        c1 = self._compress_len(s1)
        c2 = self._compress_len(s2)
        c12 = self._compress_len(s1 + s2)
        min_len = min(c1, c2)
        if min_len == 0:
            return 1.0
        return (c12 - min_len) / max(c1, c2, 1)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        # 1. Analyze Prompt Criticality (Order Parameter)
        # We treat the prompt + candidate as the system state
        prompt_variance = self._calculate_rg_variance(prompt)
        prompt_features = self._extract_structural_features(prompt)
        
        # Base structural bonus from prompt
        base_structural = prompt_features['structural_bonus']

        results = []
        for cand in candidates:
            # 2. RG Flow & Active Inference Modulation
            # Combine prompt and candidate to simulate the generative model's prediction
            system_state = f"{prompt} {cand}"
            state_variance = self._calculate_rg_variance(system_state)
            
            # Calculate NCD (Semantic Similarity)
            similarity = 1.0 - self._ncd(prompt, cand)
            
            # Criticality Detection
            # If variance is high, we are near a phase transition (uncertainty)
            is_critical = state_variance > 0.05 
            
            score = similarity
            
            if is_critical:
                # EPISTEMIC FORAGING MODE
                # Near criticality, we penalize ambiguity. 
                # We favor candidates that result in 'cleaner' compression (lower entropy)
                # when combined with the prompt, simulating free-energy minimization.
                compression_efficiency = 1.0 / (1.0 + self._compress_len(system_state)/1000.0)
                score = 0.4 * similarity + 0.6 * compression_efficiency
                
                # Boost structural adherence during uncertainty
                cand_features = self._extract_structural_features(cand)
                score += cand_features['structural_bonus']
            else:
                # EXPLOITATION MODE
                # Rely mostly on semantic similarity (NCD)
                score = 0.8 * similarity + 0.2 * base_structural

            # Deterministic tie-breaking using candidate hash (stable sort key)
            # but incorporated into score slightly to ensure uniqueness if needed
            # (Though the requirement asks for list of dicts, sorting happens outside or via 'score')
            # We keep score float purely for reasoning quality.
            
            reasoning = f"RG_Var:{state_variance:.4f} | Crit:{is_critical} | NCD:{similarity:.4f}"
            
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on RG-modulated NCD and structural consistency.
        """
        # Calculate similarity
        sim = 1.0 - self._ncd(prompt, answer)
        
        # Check criticality
        variance = self._calculate_rg_variance(f"{prompt} {answer}")
        is_critical = variance > 0.05
        
        base_conf = sim
        
        if is_critical:
            # In critical regions, confidence is dampened unless structural features align
            struct_bonus = self._extract_structural_features(answer)['structural_bonus']
            # Dampen confidence slightly in critical zones unless structure is strong
            base_conf = 0.7 * sim + 0.3 * (struct_bonus * 2.0) 
            base_conf = min(1.0, max(0.0, base_conf))
        
        # Clamp
        return float(min(1.0, max(0.0, base_conf)))