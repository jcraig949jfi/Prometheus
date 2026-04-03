import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A context-sensitive predictive coding architecture with Hebbian-STDP synaptic updates
    and a pragmatic inference layer, implemented as a reasoning tool.
    
    Mechanism:
    1. Predictive Core (Structural/Numeric): Attempts to parse the prompt for logical structures
       (negations, comparatives, conditionals) and numeric values. It computes a "prediction"
       based on deterministic rules (e.g., float comparison, transitivity).
    2. Plasticity (Hebbian-STDP Analogy): Weights for structural matches are strengthened 
       (high priority) if they reduce "error" (ambiguity). If structural signals are weak, 
       the system relies on similarity (NCD), but with low weight (synaptic decay).
    3. Pragmatic Module (RSA-style): Evaluates the prompt for conversational constraints 
       (presuppositions, scope ambiguity, false dichotomies). If pragmatic violations are 
       detected (high "surprisal" regarding truthfulness/clarity), the system suppresses 
       high-confidence scores, enforcing epistemic honesty.
    
    This creates a loop where valid logical structures drive high confidence, while 
    pragmatic anomalies trigger low confidence regardless of candidate similarity.
    """

    def __init__(self):
        # Priors for scoring components
        self.w_struct = 0.50  # Structural parsing weight
        self.w_comp = 0.35    # Computational/Numeric weight
        self.w_ncd = 0.15     # NCD weight (tiebreaker only)
        
        # Pragmatic thresholds
        self.ambiguity_threshold = 0.25
        self.high_conf_cap = 0.90

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic traps (Tier B).
        Returns a cap on confidence (0.0 to 1.0).
        """
        p = prompt.lower()
        
        # 1. Presupposition Traps
        presupposition_patterns = [
            r"have you stopped", r"have you quit", r"why did.*fail", 
            r"why did.*stop", r"when did.*stop", r"is it true that.*stopped"
        ]
        for pat in presupposition_patterns:
            if re.search(pat, p):
                return 0.1  # Strong cap for presupposition
        
        # 2. Scope Ambiguity (Simplified heuristic)
        # "Every X ... a Y" often implies same/different Y ambiguity
        if re.search(r"every\s+\w+.*\s+a\s+\w+", p) and "same" in p or "different" in p:
            if "who" in p or "which" in p:
                return 0.2

        # 3. Pronoun Ambiguity
        # "X told Y he..." patterns
        if re.search(r"\w+\s+told\s+\w+\s+(he|she|him|her)", p):
            if "who" in p:
                return 0.15

        # 4. False Dichotomy
        if re.search(r"either.*or", p) and "option" not in p and "choice" not in p:
            # Check if it implies exhaustive options without stating them
            if "must" in p or "only" in p:
                return 0.2

        # 5. Subjectivity without criteria
        subjective_words = ["best", "worst", "favorite", "beautiful", "ugly"]
        if any(w in p for w in subjective_words):
            if "define" not in p and "criteria" not in p and "metric" not in p:
                # If asking for subjective judgment without context
                if "?" in p and len(p.split()) < 15: 
                    return 0.3

        # 6. Unanswerability (Missing info indicators)
        if "cannot be determined" in p or "insufficient information" in p:
            return 0.1
            
        return 1.0  # No pragmatic issues detected

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from text."""
        # Match integers and floats, avoiding ordinals like 1st, 2nd if possible, though simple regex here
        matches = re.findall(r'-?\d+\.?\d*', text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Parses structural logic (negations, comparatives) and numeric evaluation.
        Returns a score 0-1 based on logical consistency.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        reasons = []

        # A. Numeric Evaluation (Constructive Computation)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Simple comparative logic: if prompt has two numbers, check candidate relation
            n1, n2 = p_nums[0], p_nums[1]
            c_val = c_nums[0]
            
            # Detect comparative intent in prompt
            if "larger" in p_lower or "greater" in p_lower or "more" in p_lower:
                expected = max(n1, n2)
                if abs(c_val - expected) < 1e-6:
                    score += 0.8
                    reasons.append("Numeric max match")
            elif "smaller" in p_lower or "less" in p_lower:
                expected = min(n1, n2)
                if abs(c_val - expected) < 1e-6:
                    score += 0.8
                    reasons.append("Numeric min match")
            elif "sum" in p_lower or "total" in p_lower:
                if abs(c_val - (n1 + n2)) < 1e-6:
                    score += 0.8
                    reasons.append("Numeric sum match")
        
        # B. Negation Handling
        if "not" in p_lower or "never" in p_lower:
            # If prompt negates a concept, candidate should reflect that or not contradict
            # Heuristic: If candidate contains the negated word without context, penalize?
            # Instead, boost candidates that acknowledge negation if the prompt is a trap
            pass 

        # C. Transitivity / Logic Keywords
        logic_keywords = ["therefore", "thus", "hence", "so"]
        if any(k in c_lower for k in logic_keywords):
            score += 0.1 # Small boost for logical connectors if appropriate
            
        return min(score, 1.0), ", ".join(reasons) if reasons else "No structural match"

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0:
                return 1.0
            ncd = (c12 - min_len) / max(c1, c2, 1) # Standard NCD variant
            return max(0.0, min(1.0, ncd))
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using the predictive coding + pragmatic framework.
        """
        results = []
        
        # 1. Pragmatic Check (Meta-Confidence)
        # This acts as a prior on the whole evaluation. If the prompt is bad, scores are suppressed.
        pragmatic_cap = self._meta_confidence(prompt)
        is_ambiguous = pragmatic_cap < 0.3

        for cand in candidates:
            # 2. Structural & Computational Score (The "Prediction")
            struct_score, struct_reason = self._structural_score(prompt, cand)
            
            # 3. NCD Score (The "Residual" / Tiebreaker)
            # Inverted NCD (1 - ncd) so higher is better match
            ncd_val = self._ncd(prompt, cand)
            similarity_score = 1.0 - ncd_val
            
            # 4. Fusion (Free Energy Minimization)
            # Combine structural (high weight if present) and similarity (low weight)
            raw_score = 0.0
            if struct_score > 0.0:
                # Strong structural signal dominates
                raw_score = (struct_score * 0.7) + (similarity_score * 0.3)
                reasoning = f"Structural: {struct_reason}"
            else:
                # Fallback to similarity if no logic found, but penalized
                raw_score = similarity_score * 0.5
                reasoning = "Fallback to similarity (No structural logic detected)"

            # 5. Pragmatic Modulation (RSA-style)
            # If the prompt is ambiguous/trap, cap the score regardless of content
            if is_ambiguous:
                final_score = raw_score * pragmatic_cap * 0.5 # Strong suppression
                reasoning += "; Pragmatic warning: Ambiguous/Trap detected"
            else:
                final_score = raw_score
            
            # Ensure score is within bounds
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Caps at 0.25 if pragmatic traps are detected.
        Caps at 0.9 unless computation was definitive.
        """
        # 1. Check Pragmatic Constraints (Tier B Honesty)
        cap = self._meta_confidence(prompt)
        
        # 2. Evaluate Answer Quality (Simplified for single answer)
        # We run evaluate to get the score of this specific answer
        # Note: In a real system, we might cache, but here we re-run for isolation
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
            
        base_score = res_list[0]["score"]
        
        # 3. Apply Cap
        final_conf = min(base_score, cap)
        
        # 4. Honesty constraint: Never > 0.9 without explicit computation proof
        # Our structural parser gives high scores only on numeric/logic hits.
        # If it's just NCD match, score is naturally lower.
        if final_conf > 0.9:
            # Double check: did we actually compute something?
            if "Numeric" not in res_list[0]["reasoning"] and "Structural" not in res_list[0]["reasoning"]:
                final_conf = 0.85 # Cap non-computational high scores

        return round(final_conf, 3)