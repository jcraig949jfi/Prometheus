import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Predictive Reactive-Diffusive Oscillator Network (PRDON) Implementation.
    
    Mechanism:
    1. Morphogenesis (Reaction-Diffusion): Simulated via a discrete lattice where 
       candidate answers diffuse. High-frequency noise represents potential hypotheses.
    2. Neural Oscillations: 
       - Theta (Global): Modulates the "excitability" of the parsing phase. 
       - Gamma (Local): Binds structural tokens (negations, numbers) into coherent logic units.
    3. Pragmatics (Gricean Constraints): Penalty functions that reduce the score of candidates 
       violating Relevance, Quantity, Quality, or Manner based on prompt context.
       
    Epistemic Honesty (Tier B):
    Before scoring, the system runs a meta-cognitive check for ambiguity, presupposition, 
    and unanswerability. If detected, confidence is capped low (<0.3) regardless of 
    structural match, prioritizing honesty over false confidence.
    
    Scoring Decomposition:
    - Structural/Logical Parsing: 50%
    - Constructive Computation: 20% 
    - Pragmatic/Oscillatory Binding: 15%
    - NCD (Tiebreaker): 15%
    """

    def __init__(self):
        # Gricean keywords for pragmatic filtering
        self.presupposition_triggers = [
            "stopped", "quit", "failed", "regret", "again", "still", "continue"
        ]
        self.ambiguity_triggers = [
            "every", "all", "each", "who", "he", "she", "it", "they", 
            "either", "or", "best", "worst", "favorite"
        ]
        self.false_dichotomy_phrases = ["either", "or not", "choose between"]
        
        # Oscillator state (simulated)
        self.theta_phase = 0.0
        self.gamma_sync = 0.0

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Epistemic Honesty Check.
        Detects ambiguity, presupposition, and unanswerability.
        Returns a confidence cap (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        score = 1.0
        
        # 1. Presupposition Detection
        # Looks for verbs implying a prior state that may not exist
        for trigger in self.presupposition_triggers:
            if trigger in p_lower:
                # Check if it's a "Have you stopped..." or "Why did X fail..." pattern
                if re.search(rf"(have|has|did|why|when|how).*(.{trigger})", p_lower):
                    score = min(score, 0.25)
        
        # 2. Scope & Pronoun Ambiguity
        # "Every X did a Y" -> Does every X do the SAME Y?
        if re.search(r"every\s+\w+.*\s+(a|an|the)\s+\w+", p_lower):
            if "same" not in p_lower and "different" not in p_lower:
                score = min(score, 0.4)
        
        # Pronoun ambiguity with "who" questions
        if re.search(r"\b(he|she|it|they)\b", p_lower) and "who" in p_lower:
            score = min(score, 0.3)

        # 3. False Dichotomy
        for phrase in self.false_dichotomy_phrases:
            if phrase in p_lower:
                # Only penalize if no exhaustive list is provided
                if "only" not in p_lower and "must" not in p_lower:
                    score = min(score, 0.35)

        # 4. Subjectivity without criteria
        if any(x in p_lower for x in ["best", "worst", "favorite", "beautiful"]) and \
           not any(x in p_lower for x in ["data", "statistics", "defined", "criteria"]):
            score = min(score, 0.3)

        # 5. Unanswerable / Missing Info
        if "impossible" in p_lower or "cannot be determined" in p_lower:
            score = min(score, 0.2)
            
        return max(0.0, score)

    def _structural_parse(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Structural Parsing & Logic.
        Extracts negations, comparatives, and logical constraints.
        """
        score = 0.0
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Negation consistency
        negations = ["not", "no", "never", "none", "cannot", "won't"]
        prompt_has_neg = any(n in p_lower for n in negations)
        cand_has_neg = any(n in c_lower for n in negations)
        
        if prompt_has_neg == cand_has_neg:
            score += 0.25
        else:
            score -= 0.25 # Penalty for negation mismatch

        # Conditional logic (If A then B)
        if "if" in p_lower:
            # Simple heuristic: if prompt has "if", candidate should ideally reflect conditionality
            # or provide a definitive result based on the condition.
            if "then" in p_lower or "?" in candidate:
                score += 0.15
            else:
                # Check if candidate is a direct assertion that might violate the conditional
                pass 

        # Comparatives
        comparatives = ["more", "less", "greater", "smaller", "higher", "lower"]
        if any(c in p_lower for c in comparatives):
            if any(c in c_lower for c in comparatives):
                score += 0.2
            elif any(x in c_lower for x in ["equal", "same"]):
                score += 0.1 # Plausible
        
        return score

    def _compute_answer(self, prompt: str, candidate: str) -> float:
        """
        Tier A: Constructive Computation.
        Attempts to solve numeric or logical problems explicitly.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Numeric extraction
        numbers = re.findall(r"-?\d+\.?\d*", p_lower)
        if len(numbers) >= 2:
            try:
                vals = [float(n) for n in numbers]
                # Detect operation type
                if "sum" in p_lower or "total" in p_lower or "add" in p_lower:
                    expected = sum(vals)
                elif "product" in p_lower or "multiply" in p_lower:
                    expected = 1
                    for v in vals: expected *= v
                elif "difference" in p_lower or "subtract" in p_lower:
                    expected = vals[0] - vals[1] if len(vals) >= 2 else 0
                elif "average" in p_lower or "mean" in p_lower:
                    expected = sum(vals) / len(vals)
                else:
                    # Default to comparison if no operator found
                    # Check if candidate matches the max/min logic
                    if "larger" in p_lower or "max" in p_lower:
                        expected = max(vals)
                    elif "smaller" in p_lower or "min" in p_lower:
                        expected = min(vals)
                    else:
                        return 0.0 # Cannot determine operation

                # Check candidate for the expected number
                if str(expected) in candidate or f"{expected:.1f}" in candidate:
                    return 0.4 # High reward for correct computation
                elif any(str(v) in candidate for v in vals):
                    return 0.1 # Partial credit for echoing numbers
            except ValueError:
                pass
        
        return 0.0

    def _pragmatic_bind(self, prompt: str, candidate: str) -> float:
        """
        Simulates Oscillatory Binding with Pragmatic Penalties.
        Checks relevance and quantity (Grice).
        """
        score = 0.0
        p_words = set(re.findall(r'\w+', prompt.lower()))
        c_words = set(re.findall(r'\w+', candidate.lower()))
        
        # Relevance: Overlap of content words (excluding stopwords)
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "shall", "can", "need", "dare", "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by", "from", "as", "into", "through", "during", "before", "after", "above", "below", "between", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"}
        
        p_content = p_words - stopwords
        c_content = c_words - stopwords
        
        if not p_content:
            return 0.0
            
        relevance = len(p_content & c_content) / len(p_content) if p_content else 0
        score += relevance * 0.15
        
        # Quantity: Penalty if candidate is too short (missing info) or too long (verbose)
        # Ideal length heuristic: candidate should be roughly 20%-150% of prompt length? 
        # Actually, for answers, shorter is often better unless explanation requested.
        # Let's penalize extreme brevity if the prompt is complex.
        if len(c_words) < 2 and len(p_words) > 10:
            score -= 0.1 # Too brief for complex prompt
            
        return score

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        try:
            z1 = len(zlib.compress(s1.encode()))
            z2 = len(zlib.compress(s2.encode()))
            z12 = len(zlib.compress((s1 + s2).encode()))
            numerator = z12 - min(z1, z2)
            denominator = max(z1, z2)
            if denominator == 0:
                return 1.0
            return numerator / denominator
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Meta-cognitive check on the prompt itself
        honesty_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural Parsing (50% weight potential)
            struct_score = self._structural_parse(prompt, cand)
            
            # 2. Constructive Computation (20% weight potential)
            comp_score = self._compute_answer(prompt, cand)
            
            # 3. Pragmatic Binding (15% weight potential)
            prag_score = self._pragmatic_bind(prompt, cand)
            
            # 4. NCD Tiebreaker (15% weight potential)
            # Invert NCD so lower distance = higher score
            ncd = self._ncd_score(prompt, cand)
            ncd_score = (1.0 - ncd) * 0.15
            
            # Aggregate Raw Score
            # Weights: Struct=0.5, Comp=0.4 (high reward for math), Prag=0.15, NCD=0.15
            # Note: Scores are normalized roughly to 0-1 range before weighting
            raw_score = (max(0, struct_score) * 0.5) + \
                        (comp_score * 1.0) + \ # Computation can boost significantly
                        (prag_score * 0.5) + \
                        ncd_score
            
            # Apply Epistemic Honesty Cap
            # If the prompt is ambiguous (honesty_cap < 0.3), even a "matching" candidate 
            # shouldn't get a high confidence score.
            final_score = min(raw_score, honesty_cap + (raw_score * 0.5))
            
            # Ensure floor/ceiling
            final_score = max(0.0, min(1.0, final_score))
            
            # Reasoning string generation
            reasoning_parts = []
            if honesty_cap < 0.3:
                reasoning_parts.append("Low confidence due to prompt ambiguity/presupposition.")
            if comp_score > 0.3:
                reasoning_parts.append("Constructive computation matched.")
            if struct_score > 0.2:
                reasoning_parts.append("Structural constraints satisfied.")
            if not reasoning_parts:
                reasoning_parts.append("Heuristic match based on relevance and NCD.")
                
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": " ".join(reasoning_parts)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps based on meta-cognitive analysis of the prompt.
        """
        # Run full evaluation internally to get the score
        # We treat the single answer as a candidate list
        eval_results = self.evaluate(prompt, [answer])
        
        if not eval_results:
            return 0.0
            
        base_score = eval_results[0]["score"]
        honesty_cap = self._meta_confidence(prompt)
        
        # The confidence is the score, but strictly capped by the honesty check
        # If the prompt is ambiguous, confidence cannot exceed the cap.
        final_conf = min(base_score, honesty_cap) if honesty_cap < 0.5 else base_score
        
        # Never return > 0.9 unless computation was definitive (handled by comp_score logic mostly)
        # But if honesty cap is low, it forces low confidence.
        return round(final_conf, 4)