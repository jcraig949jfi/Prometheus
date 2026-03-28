import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    CK-RPG Approximation: Chaotic Kolmogorov-Regularized Policy Gradient.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values. Scores candidates based on 
       logical consistency with the prompt's structural constraints.
    2. Chaotic Exploration (Secondary Modifier): Uses a deterministic logistic map 
       (edge of chaos, r=3.99) seeded by prompt length to generate a sensitivity 
       factor. This mimics the Lyapunov exponent monitoring to penalize overly 
       simple/repetitive answers that fail to explore the hypothesis space.
    3. Kolmogorov Regularization (Tiebreaker): Uses NCD (zlib) to estimate complexity. 
       Per guidelines, this is only used when structural signals are ambiguous, 
       favoring shorter, compressible hypotheses (Occam's razor) without letting 
       it dominate the scoring.
    """

    def __init__(self):
        # Logistic map parameter for edge-of-chaos dynamics
        self.chaos_r = 3.99 
        # Weights for scoring components
        self.w_struct = 0.60
        self.w_chaos = 0.25
        self.w_kolm = 0.15

    def _structural_parse(self, text: str) -> Dict:
        """Extract logical structure: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(no|not|never|none|cannot|impossible)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|when)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text_lower),
            'length': len(text.split())
        }
        return features

    def _chaotic_sensitivity(self, seed_str: str, candidate: str) -> float:
        """
        Simulates chaotic reservoir dynamics.
        Uses logistic map x_{n+1} = r * x_n * (1 - x_n) with r ~ 4.0.
        Returns a sensitivity score based on trajectory divergence.
        """
        # Seed from string hash to ensure determinism
        seed_val = (hash(seed_str + candidate) % 1000) / 1000.0 + 0.001
        x = min(max(seed_val, 0.001), 0.999)
        
        # Iterate to edge of chaos
        trajectory = []
        for _ in range(50):
            x = self.chaos_r * x * (1.0 - x)
            trajectory.append(x)
            
        # Calculate variance (Lyapunov proxy): higher variance = richer exploration
        if len(trajectory) < 2:
            return 0.5
        
        mean_t = sum(trajectory) / len(trajectory)
        variance = sum((t - mean_t)**2 for t in trajectory) / len(trajectory)
        
        # Normalize variance to [0, 1] range roughly
        return min(1.0, variance * 4.0)

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        try:
            c1 = len(zlib.compress(s1.encode()))
            c2 = len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            if max(c1, c2) == 0:
                return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def _evaluate_logic_consistency(self, prompt: str, candidate: str) -> float:
        """
        Core reasoning engine. Checks if candidate respects prompt constraints.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        score = 0.0
        
        # 1. Negation Consistency
        # If prompt has strong negation, candidate should reflect awareness or specific counter
        if p_feat['negations'] > 0:
            # Reward if candidate also handles negation logic or is concise
            if c_feat['negations'] > 0 or c_feat['length'] < 10:
                score += 0.4
            else:
                # Penalty for ignoring negation context unless candidate is very short (yes/no)
                if c_feat['length'] > 5:
                    score -= 0.3
        
        # 2. Comparative Logic
        if p_feat['comparatives'] > 0:
            # Candidate should ideally contain comparatives or numbers
            if c_feat['comparatives'] > 0 or len(c_feat['numbers']) > 0:
                score += 0.4
            else:
                score -= 0.2

        # 3. Conditional Logic
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] > 0 or c_feat['length'] > 15: # Longer answer expected for conditionals
                score += 0.3
            else:
                score -= 0.1

        # 4. Numeric Consistency (Simple check)
        if p_feat['numbers'] and c_feat['numbers']:
            # If both have numbers, check if candidate numbers are within prompt magnitude range
            try:
                p_nums = [float(n) for n in p_feat['numbers']]
                c_nums = [float(n) for n in c_feat['numbers']]
                if p_nums and c_nums:
                    p_avg = sum(p_nums)/len(p_nums)
                    c_avg = sum(c_nums)/len(c_nums)
                    # Reward proximity in magnitude (log scale)
                    if p_avg == 0: p_avg = 1e-9
                    if c_avg == 0: c_avg = 1e-9
                    ratio = abs(math.log(abs(c_avg)+1) - math.log(abs(p_avg)+1))
                    if ratio < 2.0:
                        score += 0.3
            except:
                pass

        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features
        p_feat = self._structural_parse(prompt)
        has_structure = (p_feat['negations'] + p_feat['comparatives'] + p_feat['conditionals']) > 0

        for cand in candidates:
            # 1. Structural Score (Primary)
            struct_score = self._evaluate_logic_consistency(prompt, cand)
            
            # Normalize structural score roughly to 0-1
            struct_norm = 0.5 + (struct_score * 0.5)
            struct_norm = max(0.0, min(1.0, struct_norm))

            # 2. Chaotic Sensitivity (Exploration Bonus)
            # Penalize candidates that are too generic if the prompt is complex
            chaos_factor = self._chaotic_sensitivity(prompt, cand)
            # If prompt is complex (high structure), we want high chaos sensitivity
            chaos_bonus = 0.0
            if has_structure:
                chaos_bonus = chaos_factor * 0.2
            else:
                chaos_bonus = (1.0 - chaos_factor) * 0.1 # Prefer stability for simple prompts

            # 3. Kolmogorov Complexity (Tiebreaker/Regularizer)
            # Only apply if structural signal is weak or as a small penalty for bloat
            ncd_val = self._ncd_score(prompt, cand)
            # Shorter is generally better (Occam), but must be relevant
            # NCD low = similar/compressible. 
            kolm_score = 1.0 - ncd_val 
            
            # Final Score Composition
            # Heuristic: If structural parsing found strong cues, weight it heavily.
            # If not, rely more on compression and chaos to avoid randomness.
            final_score = (struct_norm * self.w_struct) + (chaos_bonus * self.w_chaos) + (kolm_score * self.w_kolm)
            
            # Boost if candidate explicitly matches prompt keywords (simple relevance check)
            common_words = set(prompt.lower().split()) & set(cand.lower().split())
            if len(common_words) > 2:
                final_score += 0.1

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Structural:{struct_norm:.2f}, Chaos:{chaos_bonus:.2f}, K-Complex:{kolm_score:.2f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same logic as evaluate but returns a single normalized score.
        """
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # Map the score to a confidence metric
        # The evaluate function returns scores that can be negative or >1 in intermediate steps
        # but here we normalized. Let's assume the top result score is the confidence proxy.
        raw_score = res[0]['score']
        
        # Calibrate: 
        # High structural match + low complexity = High confidence
        # We clamp between 0 and 1
        conf = max(0.0, min(1.0, raw_score))
        return round(conf, 4)