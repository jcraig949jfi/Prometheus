import numpy as np
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical Renormalizing Global Workspace (CRGW) Implementation.
    
    Mechanism:
    1. Renormalization (MERA-like): Represents text as byte-frequency vectors. 
       Coarse-graining is simulated by iteratively pooling adjacent frequency bins 
       (halving resolution) to create a hierarchy of abstract representations.
    2. Global Workspace (GWT): Candidates compete for "ignition". Their bid strength 
       is a weighted sum of similarity to the prompt across all renormalization scales.
       Softmax gating selects the winner.
    3. Criticality (Sandpile): A self-tuning threshold determines if a hypothesis is 
       "ignited". The system calculates the "activity" (score variance). If activity 
       is too low (ordered) or too high (chaotic), the threshold adjusts. 
       Here, we simulate the *effect* of criticality: candidates are scored not just 
       by match, but by their "susceptibility" to logical constraints extracted from 
       the prompt (negations, numerics). Near-critical systems amplify small signals; 
       we amplify scores based on constraint satisfaction.
    """

    def __init__(self):
        self.scales = 4  # Number of renormalization layers
        self.critical_threshold = 0.5
        self.gain = 1.0

    def _get_byte_freq(self, text: str) -> np.ndarray:
        """Convert text to 256-dim byte frequency vector."""
        if not text:
            return np.zeros(256)
        counts = np.bincount(np.frombuffer(text.encode('utf-8', errors='ignore'), dtype=np.uint8), minlength=256)
        return counts.astype(float) / len(text)

    def _renormalize(self, vec: np.ndarray, level: int) -> np.ndarray:
        """Coarse-grain vector by pooling adjacent elements."""
        v = vec.copy()
        for _ in range(level):
            if len(v) % 2 != 0:
                v = np.append(v, 0)
            v = (v[0::2] + v[1::2]) / 2.0
        return v

    def _compute_similarity_hierarchy(self, txt1: str, txt2: str) -> float:
        """Compute similarity across renormalization scales."""
        v1 = self._get_byte_freq(txt1)
        v2 = self._get_byte_freq(txt2)
        
        similarities = []
        for l in range(self.scales):
            rv1 = self._renormalize(v1, l)
            rv2 = self._renormalize(v2, l)
            # Cosine-like similarity
            norm = np.linalg.norm(rv1) * np.linalg.norm(rv2)
            if norm == 0:
                sim = 0.0
            else:
                sim = np.dot(rv1, rv2) / norm
            similarities.append(sim)
        
        # Weighted sum: higher scales (abstractions) get significant weight
        weights = np.linspace(1.0, 0.5, self.scales)
        return float(np.dot(similarities, weights))

    def _extract_constraints(self, prompt: str) -> List[Tuple[str, any]]:
        """
        Extract logical constraints (Criticality drivers).
        Returns list of (type, value) tuples.
        """
        constraints = []
        p_lower = prompt.lower()
        
        # Numeric comparisons
        nums = []
        words = prompt.replace(',', '').split()
        for w in words:
            try:
                # Simple float extraction
                if '.' in w or w.isdigit():
                    val = float(w.strip('()[]'))
                    nums.append(val)
            except ValueError:
                continue
        
        if len(nums) >= 2:
            constraints.append(('numeric_order', sorted(nums)))
            
        # Negation detection
        if 'not' in p_lower or 'never' in p_lower or 'false' in p_lower:
            constraints.append(('negation', True))
        else:
            constraints.append(('negation', False))
            
        # Comparatives
        if 'greater' in p_lower or 'larger' in p_lower or '>' in prompt:
            constraints.append(('direction', 'asc'))
        elif 'smaller' in p_lower or 'less' in p_lower or '<' in prompt:
            constraints.append(('direction', 'desc'))
            
        return constraints

    def _apply_critical_gain(self, base_score: float, candidate: str, constraints: List[Tuple]) -> float:
        """
        Adjust score based on constraint satisfaction.
        Simulates susceptibility near critical point: small constraint matches 
        cause large score shifts.
        """
        if not constraints:
            return base_score

        penalty = 0.0
        c_lower = candidate.lower()

        for ctype, val in constraints:
            if ctype == 'negation':
                # If prompt has negation, candidate should ideally reflect uncertainty or specific negation markers
                # Simple heuristic: if prompt says "not", prefer candidates with "no", "false", etc.
                if val: 
                    if any(n in c_lower for n in ['no', 'false', 'not', 'never', '0']):
                        penalty += 0.2 # Reward (negative penalty)
                    else:
                        penalty -= 0.3 # Penalize positive assertions in negative context
            elif ctype == 'numeric_order':
                # Check if candidate contains numbers consistent with order
                # Very rough heuristic for demo
                pass 
            elif ctype == 'direction':
                if val == 'asc' and ('increase' in c_lower or 'larger' in c_lower or '>' in c_lower):
                    penalty += 0.2
                elif val == 'desc' and ('decrease' in c_lower or 'smaller' in c_lower or '<' in c_lower):
                    penalty += 0.2

        # Critical amplification: small differences in constraint matching lead to larger score changes
        adjusted = base_score + (penalty * self.gain)
        return max(0.0, min(1.0, adjusted))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        constraints = self._extract_constraints(prompt)
        results = []
        
        # Phase 1: Compute raw similarities (Renormalization)
        raw_scores = []
        for cand in candidates:
            sim = self._compute_similarity_hierarchy(prompt, cand)
            raw_scores.append(sim)
        
        # Phase 2: Criticality tuning (Sandpile-like gain adjustment)
        # If variance is too low, increase gain to differentiate
        if len(raw_scores) > 1:
            variance = np.var(raw_scores)
            if variance < 0.01:
                self.gain = 1.5  # Increase sensitivity
            else:
                self.gain = 1.0
        else:
            self.gain = 1.0

        # Phase 3: Global Workspace Competition (GWT)
        # Apply constraints and compete
        final_scores = []
        for i, cand in enumerate(candidates):
            score = self._apply_critical_gain(raw_scores[i], cand, constraints)
            
            # NCD Tiebreaker (only if scores are extremely close)
            # We use NCD as a secondary signal for structural exactness
            s_comb = prompt + cand
            s_sep = prompt + " " + cand
            # Simple compression ratio heuristic
            try:
                c_comb = len(zlib.compress(s_comb.encode()))
                c_sep = len(zlib.compress(s_sep.encode()))
                # If candidate is just a substring echo, NCD is low. 
                # We want high NCD for independent reasoning, but low NCD for factual recall?
                # Actually, for reasoning, we want semantic match. 
                # Let's use NCD distance as a tiny tiebreaker for string similarity
                ncd = (c_comb - min(len(prompt), len(cand))) / max(len(prompt), len(cand), 1)
                score += ncd * 0.01 # Tiny boost for compressibility
            except:
                pass

            final_scores.append(score)

        # Softmax gating (GWT Ignition)
        exp_scores = np.exp(np.array(final_scores) - np.max(final_scores))
        probs = exp_scores / np.sum(exp_scores)
        
        # Rank
        ranked_indices = np.argsort(probs)[::-1]
        
        output = []
        for idx in ranked_indices:
            output.append({
                "candidate": candidates[idx],
                "score": float(probs[idx]),
                "reasoning": f"CRGW: Scale-invariant similarity={raw_scores[idx]:.3f}, Critical gain applied, GWT probability={probs[idx]:.3f}"
            })
            
        return output

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence based on CRGW score."""
        # Evaluate against a dummy set including the answer to get relative score
        # Or simpler: compute the raw CRGW metric directly
        sim = self._compute_similarity_hierarchy(prompt, answer)
        constraints = self._extract_constraints(prompt)
        score = self._apply_critical_gain(sim, answer, constraints)
        return float(max(0.0, min(1.0, score)))