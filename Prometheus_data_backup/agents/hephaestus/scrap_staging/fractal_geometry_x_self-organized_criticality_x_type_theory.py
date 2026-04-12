import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    FractalSOC Type-Theoretic Proof Search (FSTT) Engine.
    
    Mechanism:
    1. Epistemic Honesty (Meta-Confidence): Before scoring, analyzes the prompt for 
       logical traps (presuppositions, ambiguity, false dichotomies). If detected, 
       confidence is capped low (<0.3) regardless of candidate quality.
    2. Structural Parsing (Type Theory Analogy): Extracts logical constraints 
       (negations, comparatives, conditionals) as "types" that candidates must inhabit.
    3. Fractal/SOC Dynamics: 
       - Candidates are scored on structural match (coarse grain).
       - If structural score is high, an "avalanche" triggers numeric/computational 
         verification (fine grain).
       - Scores cascade: Structural (50%) + Computation (35%) + NCD (15%).
    """

    def __init__(self):
        # Thresholds for SOC avalanche
        self.critical_threshold = 0.6
        self.ncd_weight = 0.15
        self.struct_weight = 0.50
        self.comp_weight = 0.35

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B: Detects ambiguity, presupposition, and unanswerability.
        Returns a cap value. If < 0.3, the question is considered 'unsafe'.
        """
        p = prompt.lower()
        
        # 1. Presupposition Traps ("Have you stopped...", "Why did X fail...")
        presupposition_patterns = [
            r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy was.*wrong\b",
            r"\bwhen did.*stop\b", r"\bhow often.*fail\b", r"\bcontinue to\b"
        ]
        for pat in presupposition_patterns:
            if re.search(pat, p):
                return 0.25

        # 2. False Dichotomy ("Either A or B", "Is it X or Y?" without context)
        # Simple heuristic: "either...or" or "is it x or y" without exhaustive lists
        if re.search(r"\beither\b.*\bor\b", p):
            # Check if it looks like a forced choice without options provided in a list
            if "which of the following" not in p:
                return 0.25
        
        # 3. Subjectivity without criteria ("Best", "Worst" without metrics)
        subjective_traps = [r"\bwho is the best\b", r"\bwhat is the worst\b", r"\bwhich is favorite\b"]
        for pat in subjective_traps:
            if re.search(pat, p):
                if "based on" not in p and "according to" not in p:
                    return 0.25

        # 4. Pronoun Ambiguity (He said to him... who?)
        if re.search(r"\b(he|she|him|her)\b.*\b(he|she|him|her)\b", p):
            if re.search(r"\bwho\b", p):
                return 0.25

        return 1.0  # No meta-traps detected

    def _extract_structure(self, prompt: str) -> dict:
        """
        Extracts logical 'types' from the prompt: negations, comparatives, numbers.
        """
        p = prompt.lower()
        return {
            "has_negation": bool(re.search(r"\b(not|no|never|neither|nor)\b", p)),
            "has_comparative": bool(re.search(r"\b(more|less|greater|smaller|higher|lower|before|after)\b", p)),
            "has_conditional": bool(re.search(r"\b(if|then|unless|only if)\b", p)),
            "numbers": re.findall(r"-?\d+(?:\.\d+)?", p),
            "entities": re.findall(r"\b[A-Z][a-z]+\b", p) # Simple proper noun capture
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        try:
            c1 = len(zlib.compress(s1.encode()))
            c2 = len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            max_len = max(c1, c2)
            if max_len == 0:
                return 1.0
            return (c12 - min(c1, c2)) / max_len
        except:
            return 1.0

    def _evaluate_computation(self, prompt: str, candidate: str) -> float:
        """
        Attempts to verify numeric or logical consistency.
        Returns 1.0 if consistent, 0.0 if contradictory, 0.5 if neutral.
        """
        p_nums = self._extract_structure(prompt)["numbers"]
        
        # If prompt has numbers, check if candidate contradicts obvious math
        # This is a simplified constructive check
        if len(p_nums) >= 2:
            try:
                # Check for simple comparison in candidate vs prompt logic
                # E.g., Prompt: "9.11 < 9.9?", Candidate: "True"
                if "true" in candidate.lower() or "false" in candidate.lower():
                    # Extract floats from prompt to verify
                    vals = [float(x) for x in p_nums]
                    if len(vals) >= 2:
                        # Heuristic: if prompt asks comparison, assume standard order
                        if "less" in prompt.lower() or "<" in prompt:
                            expected = vals[0] < vals[1]
                        elif "greater" in prompt.lower() or ">" in prompt:
                            expected = vals[0] > vals[1]
                        else:
                            return 0.5 # Unknown operation
                        
                        if ("true" in candidate.lower()) == expected:
                            return 1.0
                        else:
                            return 0.0
            except:
                pass
        return 0.5

    def _score_candidate(self, prompt: str, candidate: str, struct_features: dict) -> Tuple[float, str]:
        """
        Core scoring engine combining structural match, computation, and NCD.
        """
        score = 0.0
        reasons = []

        # 1. Structural Score (Type Inhabitation Check)
        # Does the candidate respect the logical constraints (negation, etc)?
        struct_score = 0.0
        c_lower = candidate.lower()
        
        if struct_features["has_negation"]:
            # If prompt has negation, correct answer often contains "no", "not", or implies difference
            if any(x in c_lower for x in ["no", "not", "false", "different"]):
                struct_score += 0.4
            else:
                struct_score += 0.1 # Penalty for ignoring negation
        else:
            struct_score += 0.3 # Baseline

        if struct_features["has_comparative"]:
            if any(x in c_lower for x in ["more", "less", "greater", "smaller", "yes", "true", "false"]):
                struct_score += 0.4
            else:
                struct_score += 0.1
        
        if struct_features["has_conditional"]:
            if any(x in c_lower for x in ["if", "then", "only", "yes", "no"]):
                struct_score += 0.3
            else:
                struct_score += 0.1

        # Normalize struct score to 0-1 range roughly
        struct_score = min(1.0, struct_score)
        
        # 2. Computational Score (SOC Avalanche Trigger)
        # Only compute deeply if structural score exceeds threshold (Self-Organized Criticality)
        comp_score = 0.5 # Neutral default
        if struct_score > self.critical_threshold:
            comp_score = self._evaluate_computation(prompt, candidate)
            if comp_score != 0.5:
                reasons.append(f"Computation verified: {comp_score}")

        # 3. NCD Score (Similarity as tiebreaker)
        # High NCD means dissimilar. We want some similarity but not echo.
        ncd_val = self._compute_ncd(prompt, candidate)
        # Invert and scale: Low NCD (similar) -> High score, but penalize exact echo
        if len(candidate) < 5: 
            ncd_score = 0.5 # Too short to judge by NCD
        elif ncd_val < 0.2:
            ncd_score = 0.8 # Very similar
        elif ncd_val > 0.9:
            ncd_score = 0.2 # Very different
        else:
            ncd_score = 1.0 - ncd_val # Moderate similarity

        # Weighted Sum
        final_score = (struct_score * self.struct_weight) + \
                      (comp_score * self.comp_weight) + \
                      (ncd_score * self.ncd_weight)
        
        reasons.append(f"Struct:{struct_score:.2f}, Comp:{comp_score:.2f}, NCD:{ncd_score:.2f}")
        
        return final_score, "; ".join(reasons)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates against the prompt using FSTT logic.
        """
        # 1. Meta-Confidence Check (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Extract Structural Features (Type Signatures)
        struct_features = self._extract_structure(prompt)
        
        results = []
        for cand in candidates:
            score, reason_str = self._score_candidate(prompt, cand, struct_features)
            
            # Apply Meta-Confidence Cap
            if meta_cap < 0.3:
                score = min(score, meta_cap)
                reason_str += f" | capped by meta-check ({meta_cap})"
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason_str
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Capped by meta-analysis of the prompt's ambiguity.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Quick structural check
        struct_features = self._extract_structure(prompt)
        score, _ = self._score_candidate(prompt, answer, struct_features)
        
        # If meta says ambiguous, cap it
        if meta_cap < 0.3:
            return min(score, meta_cap)
        
        # If computation was definitive (1.0 or 0.0), allow high confidence
        # Otherwise, dampen slightly to avoid overconfidence on heuristic matches
        if score > 0.85:
            return min(0.95, score) # Cap at 0.95 unless computed
        elif score < 0.2:
            return max(0.05, score)
        else:
            return score * 0.9 # Dampen uncertain middle ground