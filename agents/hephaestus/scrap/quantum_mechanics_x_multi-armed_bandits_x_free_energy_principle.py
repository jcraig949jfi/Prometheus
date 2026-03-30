import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Quantum-Variational Active Inference (QVAI) Reasoning Tool.
    
    Mechanism:
    1. Epistemic Honesty (Free Energy Minimization): Before evaluating answers, the system 
       analyzes the prompt for "high free energy" states: ambiguity, presuppositions, 
       false dichotomies, and unanswerability. If detected, confidence is capped low (<0.3)
       to prevent premature collapse into a wrong hypothesis.
    2. Structural Parsing (Quantum Superposition Analogy): Instead of string matching, we 
       extract structural features (negations, comparatives, conditionals) representing 
       the "basis states" of the reasoning problem.
    3. Constructive Computation: Detects and solves numeric/logic traps explicitly.
    4. Scoring: A weighted combination of Structural Match (50%), Computation (20%), 
       and NCD similarity (15%), heavily penalized if Epistemic Honesty flags are raised.
    """

    def __init__(self):
        # Patterns for structural parsing
        self.negation_patterns = [r"\bnot\b", r"\bnever\b", r"\bno\b", r"\bwithout\b", r"\bunless\b"]
        self.comparative_patterns = [r"\bmore\b", r"\bless\b", r"\bgreater\b", r"\bsmaller\b", r"\better\b", r"\bworse\b", r">", r"<"]
        self.conditional_patterns = [r"\bif\b", r"\bthen\b", r"\belse\b", r"\bunless\b", r"\bonly if\b"]
        
        # Patterns for Epistemic Honesty (High Free Energy States)
        self.presupposition_triggers = [
            r"have you stopped", r"did you stop", r"why did .* fail", r"why is .* bad",
            r"when did .* stop", r"how often do you .*" # Loaded questions
        ]
        self.false_dichotomy_triggers = [r"\beither .* or\b", r"\bchoose between .* and\b", r"is it .* or .*\?"]
        self.subjectivity_triggers = [r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bopinion\b"]
        self.pronoun_ambiguity_triggers = [r"\bhe\b.*\bwho\b", r"\bshe\b.*\bwho\b", r"\bthey\b.*\bwho\b"]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for ambiguity, presupposition, or unanswerability.
        Returns a cap value: 1.0 if clear, <0.3 if ambiguous/trapped.
        """
        p_lower = prompt.lower()
        
        # Check for presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.25 # High risk of loaded question
        
        # Check for false dichotomies (simplified)
        if re.search(r"either.*or", p_lower) and not re.search(r"both", p_lower):
            # Heuristic: if "either/or" exists without context of exhaustiveness
            if len(p_lower.split()) < 50: # Short prompts with either/or are often traps
                return 0.25

        # Check for subjectivity without criteria
        if any(re.search(t, p_lower) for t in self.subjectivity_triggers):
            if "measure" not in p_lower and "data" not in p_lower and "statistic" not in p_lower:
                return 0.30 # Subjective questions need external data

        # Check for pronoun ambiguity in specific "who" contexts
        if re.search(r"\bwho\b", p_lower) and re.search(r"\bhe\b|\bshe\b|\bthey\b", p_lower):
             # Simple heuristic: if asking "who" in a sentence with multiple potential subjects
             if p_lower.count(" told ") > 0 or p_lower.count(" said ") > 0:
                 return 0.25

        return 1.0

    def _extract_structural_features(self, text: str) -> Dict[str, bool]:
        """Extracts logical structures from text."""
        t_lower = text.lower()
        return {
            "has_negation": any(re.search(p, t_lower) for p in self.negation_patterns),
            "has_comparative": any(re.search(p, t_lower) for p in self.comparative_patterns),
            "has_conditional": any(re.search(p, t_lower) for p in self.conditional_patterns),
            "length": len(text)
        }

    def _compute_numeric_answer(self, prompt: str) -> Optional[float]:
        """Attempts to solve simple numeric comparisons or extractions."""
        # Extract numbers
        numbers = re.findall(r"-?\d+\.?\d*", prompt)
        if len(numbers) >= 2:
            try:
                vals = [float(n) for n in numbers]
                # Detect comparison keywords
                if any(k in prompt.lower() for k in ["larger", "greater", "more", "max"]):
                    return max(vals)
                if any(k in prompt.lower() for k in ["smaller", "less", "min"]):
                    return min(vals)
                # If just asking for a calculation result implicitly? 
                # Hard to do safely without eval, so we skip pure arithmetic unless explicit
            except ValueError:
                pass
        return None

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance."""
        z = zlib.compress
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 1.0
        concat = s1 + s2
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximating C(x) with len(z(x))
        c1 = len(z(s1.encode('utf-8')))
        c2 = len(z(s2.encode('utf-8')))
        c12 = len(z(concat.encode('utf-8')))
        
        min_c = min(c1, c2)
        max_c = max(c1, c2)
        
        if max_c == 0:
            return 0.0
        return (c12 - min_c) / max_c

    def _score_candidate_structural(self, prompt: str, candidate: str) -> float:
        """
        Scores based on structural alignment.
        Does the candidate address the logical operators in the prompt?
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        
        score = 0.0
        matches = 0
        total = 0
        
        # Negation consistency
        if p_feat["has_negation"]:
            total += 1
            if c_feat["has_negation"]:
                matches += 1
        else:
            # If prompt has no negation, candidate shouldn't randomly introduce it (heuristic)
            total += 0.5
            if not c_feat["has_negation"]:
                matches += 0.5

        # Comparative consistency
        if p_feat["has_comparative"]:
            total += 1
            if c_feat["has_comparative"]:
                matches += 1
        
        if total > 0:
            score = matches / total
        else:
            score = 0.5 # Neutral if no structural markers
            
        return score

    def _score_candidate_computation(self, prompt: str, candidate: str) -> float:
        """
        Checks if the prompt requires a numeric answer and if the candidate matches.
        """
        expected_val = self._compute_numeric_answer(prompt)
        if expected_val is not None:
            # Try to extract number from candidate
            cand_nums = re.findall(r"-?\d+\.?\d*", candidate)
            if cand_nums:
                cand_val = float(cand_nums[0])
                if math.isclose(cand_val, expected_val, rel_tol=0.01):
                    return 1.0
                else:
                    return 0.0 # Explicitly wrong number
        return 0.5 # Not applicable or inconclusive

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using QVAI-inspired logic:
        1. Check Epistemic Honesty (Meta-Confidence).
        2. Score based on Structure (50%), Computation (20%), NCD (15%).
        3. Apply honesty cap.
        """
        results = []
        
        # 1. Epistemic Honesty Check
        honesty_cap = self._meta_confidence(prompt)
        
        # Pre-calculate prompt features to avoid re-work
        p_struct = self._extract_structural_features(prompt)
        
        for candidate in candidates:
            # Structural Score (Max 0.5 weight)
            struct_score = self._score_candidate_structural(prompt, candidate)
            
            # Computational Score (Max 0.2 weight)
            comp_score = self._score_candidate_computation(prompt, candidate)
            
            # NCD Score (Max 0.15 weight) - Inverted because NCD is distance
            ncd_dist = self._calculate_ncd(prompt, candidate)
            ncd_score = 1.0 - min(1.0, ncd_dist) 
            
            # Base Raw Score
            # Weights: Struct 0.5, Comp 0.2, NCD 0.15, Base Prior 0.15
            raw_score = (struct_score * 0.50) + (comp_score * 0.20) + (ncd_score * 0.15) + 0.15
            
            # Apply Epistemic Honesty Cap
            if honesty_cap < 1.0:
                # If the question is ambiguous, even the "best" answer shouldn't score high
                final_score = min(raw_score, honesty_cap + 0.1) # Small buffer for relative ranking
            else:
                final_score = raw_score
                
            # Generate Reasoning String
            reasoning_parts = []
            if honesty_cap < 0.4:
                reasoning_parts.append("Warning: Prompt contains ambiguity or presupposition.")
            if p_struct["has_negation"] and not self._extract_structural_features(candidate)["has_negation"]:
                reasoning_parts.append("Candidate may miss negation logic.")
            if comp_score == 1.0:
                reasoning_parts.append("Numeric computation verified.")
                
            reasoning = " ".join(reasoning_parts) if reasoning_parts else "Structural alignment analysis."

            results.append({
                "candidate": candidate,
                "score": final_score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at <0.3 for ambiguous/unanswerable prompts.
        Caps at <0.9 unless computation definitively proves correctness.
        """
        # 1. Meta-Confidence (Honesty Check)
        meta_conf = self._meta_confidence(prompt)
        
        if meta_conf < 1.0:
            # If the prompt is flagged as tricky, confidence is strictly capped
            return min(0.29, meta_conf) 
        
        # 2. Structural & Computational Verification
        struct_score = self._score_candidate_structural(prompt, answer)
        comp_score = self._score_candidate_computation(prompt, answer)
        
        # If computation confirms the answer, we can be highly confident
        if comp_score == 1.0:
            return 0.95
        
        # If structure aligns well
        if struct_score > 0.8:
            return 0.85
            
        # If structural mismatch (e.g. missing negation)
        if struct_score < 0.3:
            return 0.2
            
        # Default moderate confidence for non-verified but structurally sound answers
        return 0.65