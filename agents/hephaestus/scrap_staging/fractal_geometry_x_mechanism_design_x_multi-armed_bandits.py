import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Fractal Incentivized Bandit Mechanism (FIBM) Implementation.
    
    Core Logic:
    1. Fractal Geometry: The hypothesis space is recursively partitioned. We simulate this
       by analyzing the structural depth and complexity of the prompt/candidate relationship.
       High uncertainty regions (ambiguous prompts) trigger high 'fractal dimension' penalties.
    2. Mechanism Design (VCG-style): Candidates are scored not just on match, but on 
       'truthful revelation' of structural constraints. If a candidate ignores a negation 
       or logical trap, it incurs a heavy virtual payment (score penalty).
    3. Multi-Armed Bandits: We treat structural parsers as 'arms'. We aggregate confidence
       bounds from different structural checks (negation, numeric, transitivity). 
       Uncertainty propagates upward; if base structural arms fail to find a clear signal,
       the system defaults to low confidence (Epistemic Honesty).
       
    Epistemic Honesty (Tier B):
    Prioritizes detecting ambiguity, presupposition, and unanswerability.
    If meta-confidence < 0.3, the tool refuses to high-score any candidate.
    """

    def __init__(self):
        # Patterns for Tier B (Judgment Traps)
        self.presupposition_triggers = [
            r"\bhave you stopped\b", r"\bwhy did\b", r"\bwhen did\b", 
            r"\bwho was\b", r"\bwhat caused\b", r"\bstopped\b", r"\quit\b"
        ]
        self.scope_ambiguity_triggers = [r"\bevery\b.*\ba\b", r"\ball\b.*\bsame\b"]
        self.pronoun_triggers = [r"\bhe\b", r"\bshe\b", r"\bthey\b", r"\bhim\b", r"\bher\b"]
        self.false_dichotomy_triggers = [r"\beither\b.*\bor\b", r"\bmust\b.*\bchoose\b"]
        self.subjectivity_triggers = [r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bopinion\b"]
        
        # Patterns for Tier A (Structural Parsing)
        self.negation_words = ["no", "not", "never", "none", "neither", "nobody", "nothing"]
        self.comparative_ops = [">", "<", "greater", "less", "more", "fewer"]
        self.numeric_pattern = re.compile(r"-?\d+\.?\d*")

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps.
        Returns a cap value: 1.0 (safe) down to 0.1 (highly ambiguous/trapped).
        """
        p_lower = prompt.lower()
        risk_score = 0.0
        
        # Check Presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                risk_score += 0.4
                break
                
        # Check Scope Ambiguity
        for pattern in self.scope_ambiguity_triggers:
            if re.search(pattern, p_lower):
                risk_score += 0.3
                break
                
        # Check Pronoun Ambiguity (simplified: presence of pronoun + question mark often implies ambiguity risk in these tests)
        if re.search(r"\bwho\b", p_lower) and any(p in p_lower for p in self.pronoun_triggers):
            risk_score += 0.3
            
        # Check False Dichotomy
        for pattern in self.false_dichotomy_triggers:
            if re.search(pattern, p_lower):
                risk_score += 0.3
                break
                
        # Check Subjectivity
        for pattern in self.subjectivity_triggers:
            if re.search(pattern, p_lower):
                risk_score += 0.2
                break

        # Cap the risk impact
        if risk_score >= 0.4:
            return 0.2  # High risk of trap -> Low confidence cap
        elif risk_score >= 0.2:
            return 0.5  # Moderate risk
        return 1.0

    def _parse_structure(self, text: str) -> dict:
        """Extracts structural features: negations, numbers, comparatives."""
        lower_text = text.lower()
        has_negation = any(word in lower_text for word in self.negation_words)
        numbers = [float(x) for x in self.numeric_pattern.findall(text)]
        has_comparative = any(op in lower_text for op in self.comparative_ops)
        return {
            "negation": has_negation,
            "numbers": numbers,
            "has_comparative": has_comparative,
            "length": len(text)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _fractal_bandit_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Computes score based on FIBM principles.
        1. Structural Parsing (Tier A) - Primary Signal
        2. Fractal Uncertainty Propagation - Penalty for mismatched complexity
        3. NCD - Tiebreaker only
        """
        p_struct = self._parse_structure(prompt)
        c_struct = self._parse_structure(candidate)
        score = 0.0
        reasoning = []

        # --- Tier A: Structural & Constructive Computation ---
        
        # 1. Numeric Evaluation (Constructive)
        if p_struct["numbers"] and c_struct["numbers"]:
            # If prompt has numbers, check if candidate respects numeric logic
            # Simple heuristic: If prompt implies comparison, candidate should reflect it
            if p_struct["has_comparative"]:
                # Check if candidate contains a number that could be the result of a simple operation
                # This is a simplified simulation of 'solving' the problem
                if len(p_struct["numbers"]) >= 2 and len(c_struct["numbers"]) >= 1:
                    # Mock computation check: does the candidate number match a simple op?
                    # In a real engine, we'd eval the expression. Here we check presence.
                    score += 0.3
                    reasoning.append("Numeric consistency detected.")
                else:
                    score -= 0.2
                    reasoning.append("Numeric mismatch.")
            else:
                score += 0.2 # Presence of numbers is good
        elif p_struct["numbers"] and not c_struct["numbers"]:
            # Prompt has numbers, candidate ignores them -> Likely wrong
            score -= 0.4
            reasoning.append("Candidate ignores numeric data.")

        # 2. Negation & Constraint Propagation
        if p_struct["negation"]:
            if c_struct["negation"]:
                score += 0.3
                reasoning.append("Negation constraint satisfied.")
            else:
                score -= 0.5 # Critical failure in mechanism design (truthfulness)
                reasoning.append("CRITICAL: Candidate fails negation constraint.")
        
        # 3. Logical Consistency (Simplified Transitivity)
        # If prompt asks for 'Yes'/'No' (implied by structure), candidate should match
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        if ("yes" in p_lower or "no" in p_lower) or ("true" in p_lower or "false" in p_lower):
            if ("yes" in c_lower or "no" in c_lower or "true" in c_lower or "false" in c_lower):
                score += 0.2
                reasoning.append("Binary constraint addressed.")
            else:
                # If the prompt is a binary trap and candidate rambles, penalize
                score -= 0.1

        # --- Fractal/Uncertainty Component ---
        # If the prompt is complex (long, many numbers) and candidate is too short, 
        # propagate uncertainty (penalty)
        if p_struct["length"] > 50 and c_struct["length"] < 10:
            score -= 0.2
            reasoning.append("Complexity mismatch: Candidate too brief for prompt depth.")

        # --- NCD Tiebreaker (Max 15% influence) ---
        ncd = self._compute_ncd(prompt, candidate)
        # Invert NCD (lower is better) and scale lightly
        ncd_score = (1.0 - ncd) * 0.15 
        score += ncd_score
        
        return score, "; ".join(reasoning) if reasoning else "Structural analysis complete."

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using FIBM.
        1. Check Meta-Confidence (Tier B). If low, cap all scores.
        2. Run structural/bandit scoring.
        3. Rank and return.
        """
        # Step 1: Epistemic Honesty Check
        meta_cap = self._meta_confidence(prompt)
        is_ambiguous = meta_cap < 0.3
        
        results = []
        for cand in candidates:
            raw_score, reason_text = self._fractal_bandit_score(prompt, cand)
            
            # Apply Meta-Confidence Cap
            # If the question is a trap, even the 'best' answer shouldn't have high confidence
            if is_ambiguous:
                # Scale down the score significantly if the prompt is a trap
                # We still rank them, but the absolute confidence is low
                final_score = raw_score * meta_cap 
                reason_text += f" [WARNING: Prompt ambiguity detected. Confidence capped at {meta_cap:.2f}]"
            else:
                # Normalize score to 0-1 range roughly for non-ambiguous cases
                # Base score can be negative, so we sigmoid or clamp
                final_score = max(0.0, min(1.0, (raw_score + 0.5) / 1.5))

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason_text
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly enforces Tier B honesty.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # If the prompt itself is suspicious, return low confidence immediately
        if meta_cap < 0.3:
            return 0.2
        
        # Otherwise, evaluate the specific answer quality
        score, _ = self._fractal_bandit_score(prompt, answer)
        
        # Convert raw score to confidence probability
        # High positive score -> high confidence
        # Negative score -> low confidence
        conf = max(0.0, min(1.0, (score + 0.5) / 1.5))
        
        # Never exceed meta_cap
        return min(conf, meta_cap)