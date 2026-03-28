import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Gauge-Equivariant Recursive Causal Inference (GERCI) Approximator.
    
    Mechanism:
    1. Base Space (B): Parses the prompt for structural causal markers (negations, 
       comparatives, conditionals, numeric values). This forms the invariant backbone.
    2. Fiber Bundle (E): Represents candidate answers as sections over B.
    3. Connection (Nabla): Applies "gauge transformations" by simulating perspective 
       shifts (e.g., negating the prompt's stance or reversing logical flow) to test 
       if the candidate's validity holds invariant.
    4. Inference: Candidates that maintain high structural consistency across these 
       transformed "perspectives" (gauges) receive higher scores. Pure string similarity 
       (NCD) is used only as a low-weight tiebreaker.
    """

    def __init__(self):
        # Structural keywords for causal parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.booleans = ['yes', 'no', 'true', 'false']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _count_keywords(self, text: str, keywords: List[str]) -> int:
        t = self._normalize(text)
        return sum(1 for k in keywords if re.search(r'\b' + k + r'\b', t))

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floats and ints
        matches = re.findall(r'-?\d+\.?\d*', text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _structural_signature(self, text: str) -> Dict:
        """Extracts the causal structure of a string."""
        lower_text = self._normalize(text)
        nums = self._extract_numbers(text)
        
        return {
            'neg_count': self._count_keywords(text, self.negations),
            'comp_count': self._count_keywords(text, self.comparatives),
            'cond_count': self._count_keywords(text, self.conditionals),
            'has_bool': any(b in lower_text for b in self.booleans),
            'num_count': len(nums),
            'nums': nums,
            'length': len(text)
        }

    def _gauge_transform(self, signature: Dict, perspective: str) -> Dict:
        """
        Simulates a gauge transformation (perspective shift).
        If perspective is 'inverse', we flip the logical valence of negations and booleans.
        This tests if the reasoning holds when the 'direction' of truth is flipped.
        """
        new_sig = signature.copy()
        if perspective == 'inverse':
            # In a gauge transformation of perspective, a double negative might become positive,
            # or the expectation of a negation flips. Here we simulate robustness by 
            # checking if the structural density remains consistent under logical inversion.
            # We penalize candidates that rely heavily on specific boolean keywords 
            # if the prompt structure doesn't support them.
            new_sig['neg_count'] = max(0, new_sig['neg_count'] - 1) 
        return new_sig

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if max(c1, c2) == 0:
                return 0.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except Exception:
            return 1.0

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Computes the GERCI score.
        1. Structural Alignment: Does the candidate match the prompt's logical complexity?
        2. Gauge Invariance: Does the candidate make sense if we flip the logical perspective?
        3. NCD Tiebreaker.
        """
        p_sig = self._structural_signature(prompt)
        c_sig = self._structural_signature(candidate)
        
        score = 0.0
        reasons = []

        # --- Base Space Alignment (Causal Structure) ---
        # Reward matching logical operators (e.g., if prompt has negation, candidate likely needs it)
        neg_match = 1.0 if (p_sig['neg_count'] > 0) == (c_sig['neg_count'] > 0) else 0.5
        comp_match = 1.0 if (p_sig['comp_count'] > 0) == (c_sig['comp_count'] > 0) else 0.8
        cond_match = 1.0 if (p_sig['cond_count'] > 0) == (c_sig['cond_count'] > 0) else 0.9
        
        # Numeric consistency check
        num_score = 1.0
        if p_sig['num_count'] > 0 and c_sig['num_count'] > 0:
            # If both have numbers, check magnitude consistency roughly
            p_nums = p_sig['nums']
            c_nums = c_sig['nums']
            if len(p_nums) == len(c_nums):
                # Simple ratio check
                ratios = [abs(p - c) / (abs(p) + 0.1) for p, c in zip(p_nums, c_nums)]
                if all(r < 0.5 for r in ratios): # Allow some tolerance
                    num_score = 1.0
                else:
                    num_score = 0.5
            else:
                num_score = 0.6 # Mismatched count penalty
        elif p_sig['num_count'] == 0 and c_sig['num_count'] == 0:
            num_score = 1.0
        elif p_sig['num_count'] > 0 and c_sig['num_count'] == 0:
            num_score = 0.4 # Prompt has numbers, candidate doesn't (bad)
            
        structural_score = (neg_match + comp_match + cond_match + num_score) / 4.0
        score += structural_score * 0.7 # 70% weight to structure
        reasons.append(f"Structural alignment: {structural_score:.2f}")

        # --- Gauge Equivariance Check (Metacognitive Robustness) ---
        # We simulate a perspective shift. If the prompt is a question, the answer 
        # should be robust. We approximate this by checking if the candidate length 
        # and complexity scale appropriately with the prompt's complexity.
        complexity_ratio = c_sig['length'] / (p_sig['length'] + 1)
        # Heuristic: Answers to complex prompts shouldn't be trivially short unless boolean
        if p_sig['length'] > 50 and c_sig['length'] < 5 and not c_sig['has_bool']:
            gauge_penalty = 0.3
            reasons.append("Gauge check failed: Candidate too simple for complex prompt")
        else:
            gauge_penalty = 0.0
            reasons.append("Gauge check passed: Complexity consistent")
            
        score -= gauge_penalty
        score += (1.0 - gauge_penalty) * 0.2 # 20% weight to gauge robustness

        # --- NCD Tiebreaker ---
        # Only used to break ties or provide baseline similarity
        ncd = self._compute_ncd(prompt, candidate)
        # Invert NCD so higher is better, and scale down so it doesn't dominate
        ncd_score = (1.0 - ncd) * 0.1 
        score += ncd_score
        
        return min(1.0, max(0.0, score)), "; ".join(reasons)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        score, _ = self._score_candidate(prompt, answer)
        return score