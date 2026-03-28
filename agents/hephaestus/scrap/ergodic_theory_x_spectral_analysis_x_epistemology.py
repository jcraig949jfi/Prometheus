import zlib
import re
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Spectral-Ergodic Epistemic Reasoner (SEER) Implementation.
    
    Mechanism:
    1. Structural Parsing (Epistemic Layer): Extracts logical constraints 
       (negations, comparatives, conditionals) to form a deterministic 'belief vector'.
       This acts as the high-reliability generator, avoiding the negative synergy 
       between pure ergodic sampling and epistemic rules by keeping them distinct.
    2. Spectral-Ergodic Scoring (Spectral + Ergodic Layers): 
       - Treats the character/byte sequence as a time-series signal.
       - Computes a 'spectral flatness' proxy using byte-frequency entropy vs 
         local block variance (simulating PSD peak detection).
       - Uses NCD (Compression) as the ergodic baseline (ensemble average).
       - Combines structural match (high weight) with spectral consistency (low weight)
         to rank candidates.
    3. Reliability Weighting: Structural matches dominate; NCD/Spectral acts as tiebreaker.
    """

    def __init__(self):
        self.structural_weight = 0.85
        self.spectral_weight = 0.15

    def _structural_parse(self, text: str) -> Dict[str, float]:
        """Extract logical features: negations, comparatives, conditionals, numbers."""
        t = text.lower()
        features = {
            'negation': len(re.findall(r'\b(no|not|never|none|neither|without)\b', t)),
            'comparative': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worst|than)\b', t)),
            'conditional': len(re.findall(r'\b(if|then|unless|otherwise|provided|when)\b', t)),
            'numeric': len(re.findall(r'\d+(\.\d+)?', t)),
            'length': len(t)
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denom

    def _spectral_ergodic_score(self, prompt: str, candidate: str) -> float:
        """
        Simulates Spectral-Ergodic analysis.
        1. Ergodic: Uses NCD to measure global distribution similarity.
        2. Spectral: Analyzes byte-frequency distribution (proxy for PSD flatness).
           High entropy in byte distribution = 'white noise' (mixing).
           Low entropy = 'peaks' (stagnation/metastable mode).
        """
        # Ergodic baseline (NCD)
        # We invert NCD because higher similarity (lower distance) is better
        ergodic_score = 1.0 - self._compute_ncd(prompt, candidate)
        
        # Spectral Proxy: Byte frequency entropy
        # A 'flat' spectrum (high entropy) indicates good mixing/diversity.
        # A 'peaked' spectrum (low entropy) indicates stagnation.
        if not candidate:
            return 0.0
            
        byte_counts = {}
        total = 0
        for char in candidate:
            byte_counts[char] = byte_counts.get(char, 0) + 1
            total += 1
            
        if total == 0:
            return 0.0
            
        entropy = 0.0
        for count in byte_counts.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        
        # Normalize entropy (0 to 1) based on max possible (log2(unique_chars))
        max_entropy = math.log2(len(byte_counts)) if len(byte_counts) > 1 else 0
        spectral_flatness = entropy / max_entropy if max_entropy > 0 else 0.0
        
        # Combine: We want candidates that are structurally similar (high ergodic score)
        # but not overly repetitive (high spectral flatness), though for QA, 
        # relevance (ergodic) is primary.
        return (ergodic_score * 0.7) + (spectral_flatness * 0.3)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_features = self._structural_parse(prompt)
        scored_candidates = []
        
        for cand in candidates:
            cand_features = self._structural_parse(cand)
            
            # Structural Comparison (Epistemic Layer)
            # Check for logical consistency in features (e.g., if prompt has numbers, answer should)
            struct_match = 0.0
            count = 0
            
            # Logic: If prompt has negation, valid answer often acknowledges it or contrasts
            # Simplified heuristic: Feature overlap ratio
            for key in prompt_features:
                if prompt_features[key] > 0:
                    count += 1
                    if cand_features[key] > 0:
                        struct_match += 1
                else:
                    # If prompt lacks feature, candidate having it might be noise (penalty)
                    if cand_features[key] > 0:
                        struct_match -= 0.1
            
            struct_score = (struct_match / max(count, 1)) if count > 0 else 0.5
            # Normalize structural score to 0-1 range roughly
            struct_score = max(0.0, min(1.0, struct_score))
            
            # Spectral-Ergodic Score
            se_score = self._spectral_ergodic_score(prompt, cand)
            
            # Final Weighted Sum
            final_score = (self.structural_weight * struct_score) + (self.spectral_weight * se_score)
            
            # Bonus for exact string match in logical operators (hard constraint)
            if prompt.lower().strip() == cand.lower().strip():
                final_score = 1.0

            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural: {struct_score:.2f}, Spectral-Ergodic: {se_score:.2f}"
            })
        
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation score."""
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        return results[0]["score"]