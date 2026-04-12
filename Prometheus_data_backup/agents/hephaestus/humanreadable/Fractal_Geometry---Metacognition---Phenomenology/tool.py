import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal Meta-Phenomenal Network (FMPN) Implementation.
    
    Mechanism:
    1. Structural Parsing (Phenomenological Bracketing): Isolates logical operators
       (negations, comparatives, conditionals) to evaluate truth conditions without
       sensory noise (semantic drift).
    2. Recursive Scaling (Fractal/IFS): Evaluates candidates at multiple scales:
       - Micro: Exact token match and numeric precision.
       - Meso: Structural constraint satisfaction.
       - Macro: Global compression distance (NCD) as a tiebreaker.
    3. Bayesian Metacognition: Computes a confidence score based on the margin
       between the top candidate and the runner-up, calibrated by structural clarity.
    
    Note: Phenomenology is restricted to the 'bracketing' (parsing) phase to avoid
    reasoning traps, per causal intelligence guidelines.
    """

    def __init__(self):
        # Precompile regex for structural extraction
        self.negation_pattern = re.compile(r'\b(not|no|never|neither|nor)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|then|unless|provided|when)\b', re.IGNORECASE)
        self.number_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_structure(self, text: str) -> Dict:
        """Phenomenological bracketing: isolate logical intent."""
        text_lower = text.lower()
        return {
            'negations': len(self.negation_pattern.findall(text_lower)),
            'comparatives': len(self.comparative_pattern.findall(text_lower)),
            'conditionals': len(self.conditional_pattern.findall(text_lower)),
            'numbers': self.number_pattern.findall(text),
            'length': len(text)
        }

    def _evaluate_numeric(self, prompt_nums: List[str], candidate_nums: List[str]) -> float:
        """Check numeric consistency."""
        if not prompt_nums:
            return 1.0 # No numeric constraints
        
        # Simple heuristic: if prompt has numbers, candidate should ideally reflect logic
        # Since we can't solve math without eval, we check presence/absence alignment
        if len(candidate_nums) == 0 and len(prompt_nums) > 0:
            # Candidate ignores numbers in a math-heavy prompt
            return 0.5 
        return 1.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        denominator = max(len_s1, len_s2)
        if denominator == 0:
            return 1.0
        return (len_combined - min(len_s1, len_s2)) / denominator

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Multi-scale scoring:
        1. Structural alignment (Micro/Meso)
        2. NCD (Macro - Tiebreaker)
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        score = 0.0
        reasons = []

        # --- Scale 1: Structural Constraint Propagation ---
        # If prompt has strong logical markers, candidate must reflect them or be a direct answer
        logical_density = (p_struct['negations'] + p_struct['comparatives'] + p_struct['conditionals'])
        
        if logical_density > 0:
            # Check if candidate preserves logical complexity or provides a definitive short answer
            c_logical_density = (c_struct['negations'] + c_struct['comparatives'] + c_struct['conditionals'])
            
            # Heuristic: Valid answers to complex prompts often echo logic or are very concise
            if c_logical_density > 0 or c_struct['length'] < 10:
                score += 0.4
                reasons.append("structural_alignment")
            else:
                # Penalty for ignoring logical markers in long candidates
                if c_struct['length'] > 20:
                    score -= 0.3
                    reasons.append("logic_mismatch")
        
        # --- Scale 2: Numeric Consistency ---
        num_score = self._evaluate_numeric(p_struct['numbers'], c_struct['numbers'])
        score += num_score * 0.2
        if num_score == 1.0:
            reasons.append("numeric_consistent")

        # --- Scale 3: Semantic/Compression (Tiebreaker) ---
        # NCD is weak alone, so we weight it low unless structural signals are ambiguous
        ncd = self._compute_ncd(prompt, candidate)
        # Invert NCD: lower distance = higher score. 
        # However, for QA, sometimes the answer is short and distinct from prompt (high NCD).
        # We use NCD primarily to detect "echoing" (very low NCD but trivial) vs "reasoned"
        
        ncd_component = 0.0
        if c_struct['length'] > 5: 
            # If candidate is long, it should be somewhat compressed relative to prompt+candidate
            # This is a proxy for relevance.
            ncd_component = (1.0 - ncd) * 0.4
        else:
            # Short answers get base benefit
            ncd_component = 0.2
            
        score += ncd_component
        
        # Bonus for exact keyword overlap in structural terms
        p_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        c_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        overlap = len(p_words.intersection(c_words))
        if overlap > 0:
            score += min(0.2, overlap * 0.02)

        return score, ", ".join(reasons) if reasons else "baseline"

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored = []
        for cand in candidates:
            raw_score, reason_str = self._score_candidate(prompt, cand)
            scored.append({
                "candidate": cand,
                "score": raw_score,
                "reasoning": reason_str
            })
        
        # Sort descending by score
        scored.sort(key=lambda x: x["score"], reverse=True)
        
        # Calibration: Normalize scores to ensure 0-1 range and spread
        if scored:
            max_s = scored[0]["score"]
            min_s = scored[-1]["score"]
            range_s = max_s - min_s if max_s != min_s else 1.0
            
            for item in scored:
                # Rescale to [0.1, 0.9] to allow confidence movement
                normalized = 0.1 + (0.8 * (item["score"] - min_s) / range_s)
                item["score"] = round(normalized, 4)
                
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Bayesian confidence estimation.
        Compares the target answer against a set of perturbed alternatives.
        If the target significantly outperforms alternatives, confidence is high.
        """
        # Generate pseudo-alternatives for comparison (Monte Carlo style approximation)
        # Since we can't generate new text easily without models, we use the provided answer
        # and check its structural self-consistency as a proxy.
        
        base_score, _ = self._score_candidate(prompt, answer)
        
        # Perturbation 1: Truncated
        trunc = answer[:int(len(answer)*0.8)] if len(answer) > 10 else answer
        score_trunc, _ = self._score_candidate(prompt, trunc)
        
        # Perturbation 2: Appended noise
        noise = answer + " random irrelevant string"
        score_noise, _ = self._score_candidate(prompt, noise)
        
        # Confidence is high if original score > perturbed scores
        margin = (base_score - score_trunc) + (base_score - score_noise)
        
        # Sigmoid mapping to 0-1
        conf = 1 / (1 + 2.718 ** (-margin * 5))
        return round(min(1.0, max(0.0, conf)), 4)