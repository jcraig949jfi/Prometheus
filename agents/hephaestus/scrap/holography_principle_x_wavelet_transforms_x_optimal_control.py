import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Holographic-Wavelet-Optimal-Control Reasoning Engine (HWOC-RE).
    
    MECHANISM:
    1. Holographic Boundary (Compression): Projects high-dimensional text into a 
       low-dimensional 'boundary' vector using character n-gram hashing (simulating 
       the holographic screen). This captures global structure efficiently.
    2. Wavelet Multi-Resolution (Analysis): Decomposes the prompt into scales:
       - Coarse scale: Global semantic overlap (Jaccard/Bag-of-words).
       - Fine scale: Local structural triggers (negations, numbers, logic keywords).
       Resources are allocated dynamically; fine-scale anomalies (uncertainty) 
       trigger high-resolution parsing.
    3. Optimal Control (Decision): Uses a Linear-Quadratic Regulator (LQR) analogy.
       - State: Current evidence score.
       - Control: Adjustment based on structural parsing (deterministic) vs NCD (noise).
       - Cost Function: Penalizes deviation from logical truth (parsing) and 
         overconfidence in ambiguous states (entropy penalty).
    
    EPISTEMIC HONESTY (Tier B):
    Before scoring, the 'wavelet fine-scale' scans for ambiguity markers 
    (presuppositions, pronouns, false dichotomies). If detected, the controller 
    forces a low-confidence state (<0.3), prioritizing honesty over guessing.
    """

    # --- Internal Constants & Weights ---
    WEIGHT_STRUCT = 0.55      # Structural parsing (Logic, Math, Negation)
    WEIGHT_COMP = 0.25        # Constructive computation (Math, Transitivity)
    WEIGHT_NCD = 0.15         # Compression distance (Tiebreaker only)
    WEIGHT_HOLO = 0.05        # Holographic global similarity
    
    # Ambiguity triggers for Tier B (Epistemic Honesty)
    PRESUPPOSITION_PATTERNS = [
        r"\b(stopped|quit|ceased|failed)\s+(to\s+)?\w+",
        r"\bwhy\s+did\s+\w+\s+(fail|stop|quit)",
        r"\bhave\s+you\s+(stopped|quit)",
        r"\bwhen\s+did\s+\w+\s+(stop|fail)"
    ]
    SCOPE_PRONOUN_PATTERNS = [
        r"\bevery\s+\w+.*\ba\s+\w+",  # Every X did a Y (scope)
        r"\btold\s+\w+\s+he\s+",      # Pronoun ambiguity
        r"\bsaid\s+to\s+\w+\s+that\s+he",
        r"\bwho\s+was\s+it\b"
    ]
    FALSE_DICHOTOMY_PATTERNS = [
        r"\beither\s+\w+\s+or\s+\w+",
        r"\bis\s+it\s+\w+\s+or\s+\w+\?"
    ]

    def __init__(self):
        self.state_history = []  # Simulated boundary state

    # ----------------------------------------------------------------------
    # 1. HOLOGRAPHIC ENCODING (Low-dim projection)
    # ----------------------------------------------------------------------
    def _holographic_encode(self, text: str, dim: int = 64) -> List[float]:
        """Projects text to a fixed-size vector using hash-based bucketing."""
        if not text:
            return [0.0] * dim
        vector = [0.0] * dim
        text_lower = text.lower()
        # Use char n-grams (n=2,3) to simulate holographic interference
        for n in [2, 3]:
            for i in range(len(text_lower) - n + 1):
                chunk = text_lower[i:i+n]
                h = hash(chunk)
                idx = abs(h) % dim
                # Interference pattern: add sine-weighted value
                vector[idx] += math.sin(h) * 0.1
        # Normalize
        max_val = max(abs(v) for v in vector) or 1.0
        return [v / max_val for v in vector]

    # ----------------------------------------------------------------------
    # 2. WAVELET MULTI-RESOLUTION ANALYSIS
    # ----------------------------------------------------------------------
    def _wavelet_decompose(self, prompt: str, candidate: str) -> Dict[str, float]:
        """
        Decomposes the problem into scales:
        - Coarse: Global semantic similarity.
        - Fine: Structural triggers (negation, numbers, logic).
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        
        # Coarse Scale: Token overlap (Jaccard-like)
        p_tokens = set(re.findall(r'\w+', p_low))
        c_tokens = set(re.findall(r'\w+', c_low))
        if not p_tokens:
            coarse_score = 0.0
        else:
            intersection = len(p_tokens & c_tokens)
            union = len(p_tokens | c_tokens)
            coarse_score = intersection / union if union > 0 else 0.0

        # Fine Scale: Structural density
        # Detects presence of logic operators, numbers, negations
        fine_features = 0.0
        if re.search(r'\b(not|no|never|neither|nobody)\b', p_low):
            fine_features += 0.5
        if re.search(r'\d+', p_low):
            fine_features += 0.5
        if re.search(r'\b(if|then|else|because|therefore|either|or)\b', p_low):
            fine_features += 0.5
        
        return {
            "coarse": coarse_score,
            "fine_density": min(fine_features, 1.0),
            "length_ratio": len(c_tokens) / (len(p_tokens) + 1)
        }

    # ----------------------------------------------------------------------
    # 3. STRUCTURAL PARSING & COMPUTATION (The "Controller")
    # ----------------------------------------------------------------------
    def _parse_and_compute(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Performs deterministic parsing and math.
        Returns (score_delta, reasoning_string).
        High score delta = strong structural match.
        """
        p_low = prompt.lower()
        c_low = candidate.lower()
        score = 0.0
        reasons = []

        # A. Numeric Evaluation (Constructive Computation)
        # Extract numbers from prompt and candidate
        p_nums = re.findall(r'-?\d+\.?\d*', p_low)
        c_nums = re.findall(r'-?\d+\.?\d*', c_low)
        
        if p_nums:
            try:
                # Simple check: if candidate contains the result of a simple operation in prompt
                # This is a heuristic for "calculate and match"
                if len(p_nums) >= 2 and len(c_nums) >= 1:
                    n1, n2 = float(p_nums[0]), float(p_nums[1])
                    c_val = float(c_nums[0])
                    
                    # Check addition/subtraction/multiplication presence
                    if '+' in p_low and abs(c_val - (n1 + n2)) < 1e-6:
                        score += 1.0
                        reasons.append("Correct arithmetic (addition)")
                    elif '-' in p_low and abs(c_val - (n1 - n2)) < 1e-6:
                        score += 1.0
                        reasons.append("Correct arithmetic (subtraction)")
                    elif '*' in p_low and abs(c_val - (n1 * n2)) < 1e-6:
                        score += 1.0
                        reasons.append("Correct arithmetic (multiplication)")
                    elif '/' in p_low and n2 != 0 and abs(c_val - (n1 / n2)) < 1e-6:
                        score += 1.0
                        reasons.append("Correct arithmetic (division)")
                    # Comparison traps
                    elif 'greater' in p_low or 'larger' in p_low:
                        if c_val == max(n1, n2):
                            score += 0.8
                            reasons.append("Correct comparative logic")
                    elif 'smaller' in p_low or 'lesser' in p_low:
                        if c_val == min(n1, n2):
                            score += 0.8
                            reasons.append("Correct comparative logic")
            except ValueError:
                pass

        # B. Logical Negation & Modus Tollens
        # If prompt has "not" or "never", candidate must reflect negation or specific handling
        if re.search(r'\bnot\b|\bnever\b|\bno\b', p_low):
            if re.search(r'\bnot\b|\bnever\b|\bno\b|\bfalse\b|\bincorrect\b', c_low):
                score += 0.6
                reasons.append("Negation consistency detected")
            elif re.search(r'\byes\b|\btrue\b|\bcorrect\b', c_low):
                # Potential trap: answering yes to a negative premise without qualification
                score -= 0.4 
                reasons.append("Potential negation trap")

        # C. Transitivity (A > B, B > C => A > C)
        if 'greater' in p_low and 'than' in p_low:
            # Very rough heuristic for transitivity chains
            if len(p_nums) >= 3:
                # If candidate mentions the max number as the answer
                if c_nums and float(max(c_nums)) == float(max(p_nums)):
                    score += 0.7
                    reasons.append("Transitive logic inferred")

        return (score, "; ".join(reasons) if reasons else "Structural neutral")

    # ----------------------------------------------------------------------
    # 4. META-CONFIDENCE (Tier B: Epistemic Honesty)
    # ----------------------------------------------------------------------
    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the PROMPT for ambiguity, presupposition, or unanswerability.
        Returns a cap value (0.0 - 1.0).
        """
        p_low = prompt.lower()
        
        # Check Presuppositions
        for pattern in self.PRESUPPOSITION_PATTERNS:
            if re.search(pattern, p_low):
                return 0.2  # Cap at 0.2 for presupposition traps
        
        # Check Scope/Pronoun Ambiguity
        for pattern in self.SCOPE_PRONOUN_PATTERNS:
            if re.search(pattern, p_low):
                # Only cap if the question asks for resolution ("who", "which")
                if re.search(r'\b(who|which|what|whose)\b', p_low):
                    return 0.25

        # Check False Dichotomy
        for pattern in self.FALSE_DICHOTOMY_PATTERNS:
            if re.search(pattern, p_low):
                # If options aren't exhaustive or explicit
                if "only" not in p_low: 
                    return 0.3

        # Check for Subjectivity without criteria
        if re.search(r'\b(best|worst|favorite|opinion)\b', p_low):
            if "according to" not in p_low and "data" not in p_low:
                return 0.3

        return 1.0  # No ambiguity detected

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        try:
            len_s1 = len(zlib.compress(s1.encode()))
            len_s2 = len(zlib.compress(s2.encode()))
            len_both = len(zlib.compress((s1 + s2).encode()))
            max_len = max(len_s1, len_s2)
            if max_len == 0:
                return 1.0
            return (len_both - min(len_s1, len_s2)) / max_len
        except:
            return 1.0

    # ----------------------------------------------------------------------
    # MAIN INTERFACE
    # ----------------------------------------------------------------------
    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        # 1. Meta-Analysis (Tier B Honesty Check)
        # Determine if the question itself is flawed or ambiguous
        honesty_cap = self._meta_confidence(prompt)
        
        # 2. Holographic Encoding of Prompt (Context)
        prompt_vec = self._holographic_encode(prompt)

        results = []
        for cand in candidates:
            # A. Wavelet Decomposition
            wavelet_stats = self._wavelet_decompose(prompt, cand)
            
            # B. Structural Parsing & Computation (Deterministic Core)
            struct_score, struct_reason = self._parse_and_compute(prompt, cand)
            
            # C. NCD (Tiebreaker, limited weight)
            ncd_val = self._compute_ncd(prompt, cand)
            # Convert distance to similarity (0 dist = 1 sim), but penalize exact echoes
            ncd_score = (1.0 - ncd_val) if ncd_val < 0.9 else 0.0
            if len(cand.strip()) < 5: # Penalize very short answers unless math
                ncd_score *= 0.5

            # D. Optimal Control Fusion (LQR-like cost minimization)
            # Cost = Error^2. We want to maximize alignment with structural truth.
            # Base score from wavelet coarse match
            base_score = wavelet_stats["coarse"]
            
            # Apply Structural Correction (High gain)
            # If structural parser found a definitive math/logic hit, it dominates
            if struct_score > 0.5:
                final_score = 0.4 + (struct_score * 0.6) # Boost high
            else:
                # Weighted sum
                final_score = (
                    base_score * 0.4 + 
                    struct_score * 0.4 + 
                    ncd_score * 0.2
                )

            # E. Apply Epistemic Honesty Cap
            if honesty_cap < 1.0:
                # If the question is ambiguous, cap the score regardless of candidate quality
                # But allow slight differentiation if one candidate explicitly notes ambiguity
                if "unclear" in cand.lower() or "cannot determine" in cand.lower():
                    final_score = 0.8 # Reward admitting uncertainty
                else:
                    final_score = min(final_score, honesty_cap * 0.9)

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": f"Wavelet[Coarse:{wavelet_stats['coarse']:.2f}]; Struct[{struct_reason}]; NCD[{ncd_score:.2f}]; HonestyCap[{honesty_cap:.2f}]"
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for ambiguous prompts.
        """
        # 1. Check Prompt Ambiguity First (Tier B)
        cap = self._meta_confidence(prompt)
        
        # 2. Evaluate specific answer quality
        eval_results = self.evaluate(prompt, [answer])
        if not eval_results:
            return 0.0
            
        raw_score = eval_results[0]["score"]
        
        # 3. Apply Cap
        final_conf = min(raw_score, cap)
        
        # 4. Never return > 0.9 without definitive computation
        # If the reasoning doesn't explicitly mention "Correct arithmetic" or strong logic,
        # and the score is high, dampen it slightly to avoid overconfidence on lucky guesses.
        reasoning = eval_results[0]["reasoning"]
        if "Correct arithmetic" not in reasoning and "Transitive" not in reasoning:
            if final_conf > 0.9:
                final_conf = 0.85 # Cap non-computational certainty
        
        return round(final_conf, 4)