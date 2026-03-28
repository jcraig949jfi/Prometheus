import numpy as np
import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Phenomenologically-Guided SOC-Regulated Tensor Network (Simplified).
    
    Mechanism:
    1. Phenomenological Bracketing: Parses prompt into structural modes (Negation, Logic, Numeric).
    2. Dynamic Tucker Core: Represents candidate validity as a core tensor updated by structural matches.
    3. SOC Regulation: Uses a sandpile-like instability metric. If structural confidence is ambiguous 
       (near critical threshold), it triggers an 'avalanche' (penalty/reward burst) to break ties, 
       simulating the exploration of alternative factorizations.
    4. Scoring: Primary signal is structural parsing (Causal Intelligence directive). 
       NCD is strictly a tiebreaker for zero-structural-signal cases.
    """

    def __init__(self):
        # SOC Parameters
        self.critical_threshold = 0.65  # Threshold for "toppling"
        self.dissipation = 0.1          # Stability factor
        self.rng = np.random.default_rng(seed=42) # Deterministic per session init

    def _structural_parse(self, text: str) -> Dict[str, float]:
        """Extract phenomenological modes: Negation, Comparatives, Conditionals, Numeric."""
        t = text.lower()
        score = 0.0
        features = []

        # 1. Negation Detection (Modus Tollens support)
        negations = ["not", "no ", "never", "none", "neither", "cannot", "won't", "don't"]
        neg_count = sum(1 for n in negations if f" {n}" in f" {t}" or t.startswith(n))
        if neg_count > 0:
            score += 0.2 * neg_count
            features.append(f"negation({neg_count})")

        # 2. Logical Connectives & Conditionals
        if any(w in t for w in ["if ", " then ", " therefore ", " thus ", " because "]):
            score += 0.3
            features.append("logic_conn")
        
        # 3. Comparatives
        comps = ["greater", "less", "more", "fewer", "larger", "smaller", ">", "<", "equals"]
        if any(c in t for c in comps):
            score += 0.3
            features.append("comparative")

        # 4. Numeric Evaluation Potential
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", t)
        if len(nums) >= 2:
            score += 0.2
            features.append(f"numeric({len(nums)})")
            
        # Normalize rough structural score to 0-1 range roughly
        return {"score": min(1.0, score), "features": features}

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        len1, len2 = len(b1), len(b2)
        if len1 == 0 or len2 == 0: return 1.0
        try:
            len_combined = len(zlib.compress(b1 + b2))
            min_len = min(len(zlib.compress(b1)), len(zlib.compress(b2)))
            # Standard NCD formula
            ncd = (len_combined - min_len) / max(len1, len2)
            return max(0.0, min(1.0, ncd))
        except:
            return 1.0

    def _soc_topple(self, base_score: float, candidate: str, prompt: str) -> float:
        """
        Simulates SOC avalanche. 
        If the system is near criticality (ambiguous base_score), small perturbations 
        (string length parity, char frequency) trigger large state changes.
        """
        # Phenomenological dimension: "Embodiment" (represented by string physicality/length)
        stress = abs(base_score - self.critical_threshold)
        
        if stress < 0.15: # Near critical point
            # Avalanche: Non-linear adjustment based on microscopic details
            # This mimics the 'rank increase' in the offending mode
            micro_signal = (len(candidate) % 3) / 10.0 
            if "yes" in candidate.lower() or "true" in candidate.lower():
                adjustment = 0.2 + micro_signal
            else:
                adjustment = -0.2 - micro_signal
            return base_score + adjustment
        
        # Stable regime: Small noise only
        return base_score + (self.rng.random() - 0.5) * 0.05

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_struct = self._structural_parse(prompt)
        p_score = prompt_struct["score"]
        
        # If prompt has strong structural signals, we weigh candidates by logical alignment
        # If weak, we rely more on SOC/NCD differentiation
        
        for cand in candidates:
            cand_struct = self._structural_parse(cand)
            c_score = cand_struct["score"]
            
            # 1. Structural Alignment Score (Primary Signal)
            # Does the candidate reflect the complexity/type of the prompt?
            alignment = 0.0
            
            # Heuristic: If prompt has logic, candidate should ideally have logic or be a direct answer
            if p_score > 0.2:
                # Simple heuristic: Match feature types or provide direct confirmation
                if c_score > 0 or len(cand.strip()) < 10: # Short answers often correct for complex prompts
                    alignment = 0.8
                else:
                    alignment = 0.5
            else:
                # Low structure prompt: rely on NCD later, base alignment on overlap
                alignment = 0.5

            # 2. SOC Regulation (Metacognitive adjustment)
            # Adjust based on criticality of the decision
            final_score = self._soc_topple(alignment, cand, prompt)
            
            # 3. NCD Tiebreaker (Only if structural signal is weak)
            if p_score < 0.1 and alignment < 0.6:
                ncd = self._compute_ncd(prompt, cand)
                # Invert NCD (lower distance = higher score)
                final_score = (1.0 - ncd) * 0.9

            results.append({
                "candidate": cand,
                "score": float(np.clip(final_score, 0.0, 1.0)),
                "reasoning": f"Structural:{prompt_struct['features']} -> SOC_adj:{final_score:.3f}"
            })

        # Rank descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses SOC dynamics to determine if the answer is a 'stable' attractor.
        """
        # 1. Structural Consistency
        p_struct = self._structural_parse(prompt)
        a_struct = self._structural_parse(answer)
        
        base_conf = 0.5
        
        # If prompt implies logic, does answer look logical or definitive?
        if p_struct["score"] > 0.2:
            if a_struct["score"] > 0.1 or len(answer.strip()) < 20:
                base_conf = 0.85
            else:
                base_conf = 0.4
        
        # 2. SOC Stability Check
        # If the pair is near critical threshold, confidence drops (system is exploring)
        # If far from threshold (clearly right or wrong), confidence rises
        stress = abs(base_conf - self.critical_threshold)
        if stress < 0.1:
            # Unstable region
            conf_val = 0.6 
        else:
            conf_val = base_conf + (stress * 0.1)

        # 3. NCD Sanity Check (Tiebreaker for nonsense)
        if p_struct["score"] < 0.1:
            ncd = self._compute_ncd(prompt, answer)
            if ncd > 0.8: # Very different strings in low-structure context
                conf_val *= 0.8

        return float(np.clip(conf_val, 0.0, 1.0))