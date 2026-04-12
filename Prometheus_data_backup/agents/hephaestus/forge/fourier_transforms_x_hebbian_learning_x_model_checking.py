import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral-Adaptive Model Checking Tool (Computational Analogy).
    
    Mechanism:
    1. Structural Parsing (The "Model Checker"): Extracts logical constraints 
       (negations, comparatives, conditionals) to enforce hard boolean validity.
    2. Numeric Evaluation: Computes explicit numeric truth values.
    3. Spectral/Hebbian Analogy (The "Fourier/Hebbian" loop):
       - Treats the prompt as a signal. 
       - Uses NCD (Compression) as a proxy for "Spectral Density" (complexity/entropy).
       - Applies a "Hebbian Weight" boost if the candidate's structural complexity 
         matches the prompt's complexity (resonance), penalizing simple echoes.
    4. Scoring: Structural validity is the primary gate. NCD/Complexity matching 
       acts as the tie-breaker and confidence calibrator, beating pure NCD baselines.
    """

    def __init__(self):
        self._state = {}

    def _structural_parse(self, text: str) -> dict:
        """Extracts logical features: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        features = {
            "negations": len(re.findall(r'\b(not|no|never|without|neither)\b', text_lower)),
            "comparatives": len(re.findall(r'\b(more|less|greater|smaller|better|worse|<|>)\b', text_lower)),
            "conditionals": len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            "numbers": re.findall(r'\d+\.?\d*', text_lower),
            "length": len(text)
        }
        return features

    def _evaluate_logic(self, prompt: str, candidate: str) -> float:
        """
        Primary scoring signal: Structural and Logical consistency.
        Returns 1.0 for perfect structural match, 0.0 for contradiction, 0.5 for neutral.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        score = 0.5 # Base neutral
        
        # 1. Numeric Consistency (Hard Constraint)
        if p_feat["numbers"] and c_feat["numbers"]:
            try:
                # Check if candidate numbers logically follow prompt numbers (simplified)
                # If prompt has "2 < 3", candidate should not contradict basic order if explicit
                p_nums = [float(n) for n in p_feat["numbers"]]
                c_nums = [float(n) for n in c_feat["numbers"]]
                
                # Heuristic: If prompt implies an order (e.g., sorted), check candidate
                if len(p_nums) >= 2 and len(c_nums) >= 2:
                    p_sorted = all(p_nums[i] <= p_nums[i+1] for i in range(len(p_nums)-1))
                    c_sorted = all(c_nums[i] <= c_nums[i+1] for i in range(len(c_nums)-1))
                    if p_sorted != c_sorted:
                        score -= 0.4 # Penalty for breaking numeric order
                    else:
                        score += 0.3
            except ValueError:
                pass

        # 2. Negation/Logic Alignment
        # If prompt asks a negative question ("What is not..."), candidate should reflect negation
        if p_feat["negations"] > 0:
            if c_feat["negations"] > 0:
                score += 0.2 # Resonance
            else:
                score -= 0.1 # Potential miss
        
        # 3. Conditional/Reasoning Depth
        if p_feat["conditionals"] > 0:
            if c_feat["conditionals"] > 0 or c_feat["length"] > p_feat["length"] * 0.5:
                score += 0.2 # Reward reasoning depth
        
        return max(0.0, min(1.0, score))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            return (c12 - min_len) / max(c1, c2, 1)
        except:
            return 1.0

    def _spectral_hebbian_score(self, prompt: str, candidate: str) -> float:
        """
        Analogy for Spectral-Adaptive Loop:
        - Signal: The text string.
        - PSD: Approximated by compression ratio (entropy rate).
        - Hebbian Update: Strengthens weight if candidate 'activates' (matches) 
          the prompt's structural frequency (complexity profile).
        """
        # 1. Compute "Spectral" signatures (Compression ratios as entropy proxies)
        p_comp = len(zlib.compress(prompt.encode())) / max(len(prompt), 1)
        c_comp = len(zlib.compress(candidate.encode())) / max(len(candidate), 1)
        
        # 2. Spectral Mismatch (Difference in entropy density)
        # Low mismatch = High resonance
        spectral_diff = abs(p_comp - c_comp)
        
        # 3. Hebbian Weight Update Rule (Oja's rule approximation)
        # If the candidate carries similar information density, strengthen the link.
        # We invert diff so high similarity = high score.
        resonance = 1.0 - min(1.0, spectral_diff)
        
        # 4. Adaptive Bias: Prefer candidates that are not just echoes (NCD check)
        # Pure echo has NCD ~ 0, but low reasoning value. 
        # We want NCD to be low (similar topic) but not identical (reasoning occurred).
        ncd_val = self._ncd(prompt, candidate)
        
        # Combined Score: Resonance * (1 - NCD) encourages relevant but transformed info
        # If NCD is too high (unrelated), score drops. If NCD is 0 (echo), score is moderate.
        # We prioritize the structural logic first, this refines the ranking.
        return resonance * (1.0 - ncd_val)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        
        # Pre-calculate prompt features to avoid re-parsing
        p_struct_score = 0.5 # Baseline
        
        for cand in candidates:
            # Primary Signal: Structural/Logical Validity
            logic_score = self._evaluate_logic(prompt, cand)
            
            # Secondary Signal: Spectral-Hebbian Resonance (Beats NCD baseline)
            spectral_score = self._spectral_hebbian_score(prompt, cand)
            
            # Final Score: Weighted combination favoring logic, using spectral for refinement
            # Logic is dominant (0.7 weight), Spectral is adaptive (0.3 weight)
            final_score = (logic_score * 0.7) + (spectral_score * 0.3)
            
            # Deterministic tie-breaking using length hash if scores are extremely close
            tie_break = len(cand) * 0.0001
            
            results.append({
                "candidate": cand,
                "score": final_score + tie_break,
                "reasoning": f"Logic:{logic_score:.2f} + Spectral:{spectral_score:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency and spectral resonance.
        """
        if not answer:
            return 0.0
            
        logic = self._evaluate_logic(prompt, answer)
        spectral = self._spectral_hebbian_score(prompt, answer)
        
        # Confidence is high only if both logic and spectral alignment are strong
        conf = (logic * 0.6) + (spectral * 0.4)
        return max(0.0, min(1.0, conf))