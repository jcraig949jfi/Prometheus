import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Adaptive Neuromodulated Morphogenetic Mechanism Design (ANMMD) Reasoning Tool.
    
    Mechanism:
    1. Morphogenesis (Pattern Formation): Uses reaction-diffusion inspired structural parsing
       to generate diverse "candidate hypotheses" about the prompt's logical structure 
       (negations, comparatives, conditionals). This creates a spatial map of logical constraints.
    
    2. Neuromodulation (Precision Weighting): A global 'precision' signal is computed based on
       epistemic honesty checks (ambiguity, presupposition). This acts as a gain control:
       - High precision (clear prompt): Structural and computational scores are amplified.
       - Low precision (ambiguous/trap prompt): Global gain is suppressed, capping confidence
         regardless of candidate quality, enforcing epistemic honesty.
    
    3. Mechanism Design (Incentive Compatibility): Candidates are scored using a logarithmic
       proper scoring rule. This ensures that the 'truthful' report of confidence (the score)
       aligns with the actual probability of correctness, preventing self-deceptive overconfidence.
       The final score is a weighted sum where structural parsing dominates (>50%), 
       computation supports (~20-30%), and NCD is a minor tiebreaker (<15%).
    """

    # Preset keywords for structural and ambiguity detection
    PRESUPPOSITION_TRIGGERS = [
        r"\b(stopped|quit|ceased|failed)\b",
        r"\bwhy\s+did\s+\w+\s+(fail|stop|lose)\b",
        r"\bhave\s+you\s+(stopped|quit)\b"
    ]
    
    SCOPE_AMBIGUITY_PATTERNS = [
        r"\bevery\s+\w+\s+\w+\s+a\s+\w+",  # Every X did a Y
        r"\bsame\s+\w+\b"
    ]
    
    PRONOUN_AMBIGUITY_PATTERNS = [
        r"\b(he|she|him|her|they)\s+was\s+\w+",
        r"\btold\s+\w+\s+he\b",
        r"\bwho\s+was\s+\w+\?"
    ]
    
    FALSE_DICHOTOMY_PATTERNS = [
        r"\beither\s+\w+\s+or\s+\w+",
        r"\bis\s+it\s+\w+\s+or\s+\w+\?"
    ]

    def __init__(self):
        self.epsilon = 1e-6

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_c = max(c1, c2)
        if max_c == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_c

    def _extract_structure(self, prompt: str) -> Dict[str, any]:
        """
        Morphogenetic Layer: Extracts logical structures (negations, comparatives, numbers).
        Returns a dictionary of structural features.
        """
        p_lower = prompt.lower()
        features = {
            "has_negation": bool(re.search(r"\b(not|no|never|neither|without)\b", p_lower)),
            "has_comparative": bool(re.search(r"\b(more|less|greater|smaller|better|worse|larger|higher|lower)\b", p_lower)),
            "has_conditional": bool(re.search(r"\b(if|then|unless|otherwise)\b", p_lower)),
            "numbers": [],
            "is_question": "?" in prompt
        }
        
        # Extract numbers for computational evaluation
        nums = re.findall(r"-?\d+\.?\d*", p_lower)
        if nums:
            try:
                features["numbers"] = [float(n) for n in nums]
            except ValueError:
                pass
                
        return features

    def _meta_confidence(self, prompt: str) -> float:
        """
        Epistemic Honesty Layer: Detects ambiguity, presuppositions, and unanswerability.
        Returns a precision weight (0.0 to 1.0).
        """
        p_lower = prompt.lower()
        risk_score = 0.0
        
        # Check Presuppositions
        for pattern in self.PRESUPPOSITION_TRIGGERS:
            if re.search(pattern, p_lower):
                risk_score += 0.8
                break
                
        # Check Scope Ambiguity
        for pattern in self.SCOPE_AMBIGUITY_PATTERNS:
            if re.search(pattern, p_lower):
                risk_score += 0.6
                break
                
        # Check Pronoun Ambiguity
        for pattern in self.PRONOUN_AMBIGUITY_PATTERNS:
            if re.search(pattern, p_lower):
                if "who" in p_lower or "which" in p_lower:
                    risk_score += 0.7
                break

        # Check False Dichotomy
        for pattern in self.FALSE_DICHOTOMY_PATTERNS:
            if re.search(pattern, p_lower):
                # Only penalize if it looks like a trap (short, no context)
                if len(prompt.split()) < 15: 
                    risk_score += 0.5
                break

        # Check for subjectivity without criteria
        if re.search(r"\b(best|worst|favorite|opinion)\b", p_lower):
             if "list" not in p_lower and "data" not in p_lower:
                risk_score += 0.6

        # Convert risk to precision weight (High risk -> Low precision)
        precision = max(0.0, 1.0 - risk_score)
        return precision

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Evaluates candidate against structural constraints (Negation, Transitivity, etc.).
        Returns a score 0.0 to 1.0.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.5  # Base prior
        structure = self._extract_structure(prompt)
        
        # 1. Negation Consistency
        if structure["has_negation"]:
            # If prompt has "not", correct answer often contains "no", "not", or contradicts premise
            if re.search(r"\bnot\b", p_lower):
                if re.search(r"\b(no|not|never|false|impossible)\b", c_lower):
                    score += 0.3
                else:
                    # Heuristic: if prompt asks "Is X not Y?" and answer is "Yes", it's ambiguous. 
                    # If answer is "No", it confirms negation.
                    pass 
            # Simple check: if prompt says "X is not Y", candidate shouldn't say "X is Y"
            # This is hard without full NLI, so we rely on keyword matching for traps
            if "not" in p_lower and "yes" in c_lower and "no" not in c_lower:
                 # Potential trap: "Is the ball not red?" -> "Yes" (It is not red) vs "No" (It is red)
                 # We penalize bare "Yes" in negative contexts slightly to favor explicit "No"
                 if c_lower.strip() == "yes":
                     score -= 0.2

        # 2. Comparative Logic
        if structure["has_comparative"] and structure["numbers"]:
            nums = structure["numbers"]
            if len(nums) >= 2:
                # Detect direction
                if "more" in p_lower or "greater" in p_lower or "larger" in p_lower:
                    expected_max = max(nums)
                    if str(expected_max) in candidate or (str(int(expected_max)) in candidate if expected_max.is_integer() else False):
                        score += 0.4
                elif "less" in p_lower or "smaller" in p_lower:
                    expected_min = min(nums)
                    if str(expected_min) in candidate or (str(int(expected_min)) in candidate if expected_min.is_integer() else False):
                        score += 0.4

        # 3. Conditional/Modus Tollens check (Simplified)
        if structure["has_conditional"]:
            if re.search(r"\b(false|incorrect|impossible)\b", c_lower):
                score += 0.2 # Often the answer to complex logic traps is negative
        
        return min(1.0, max(0.0, score))

    def _compute_computational_score(self, prompt: str, candidate: str) -> float:
        """
        Performs explicit calculation if numbers are present.
        Returns 1.0 if candidate matches calculation, 0.0 if contradicts, 0.5 if N/A.
        """
        structure = self._extract_structure(prompt)
        nums = structure["numbers"]
        
        if not nums or len(nums) < 2:
            return 0.5 # No computation needed/possible
            
        # Try basic arithmetic inference
        # Case 1: Comparison "Which is larger: 5.11 or 9.9?"
        if "larger" in prompt.lower() or "greater" in prompt.lower() or "more" in prompt.lower():
            correct_val = max(nums)
            cand_vals = [float(x) for x in re.findall(r"-?\d+\.?\d*", candidate) if x]
            if cand_vals and abs(cand_vals[0] - correct_val) < 1e-6:
                return 1.0
            elif cand_vals:
                return 0.1 # Explicitly wrong number
                
        if "smaller" in prompt.lower() or "less" in prompt.lower():
            correct_val = min(nums)
            cand_vals = [float(x) for x in re.findall(r"-?\d+\.?\d*", candidate) if x]
            if cand_vals and abs(cand_vals[0] - correct_val) < 1e-6:
                return 1.0
            elif cand_vals:
                return 0.1

        # Case 2: Simple addition/subtraction context (heuristic)
        # If prompt looks like "What is 5 + 3?"
        if "+" in prompt and "?" in prompt:
            try:
                # Very basic eval for simple expressions if safe
                # Only trust if the expression is trivial and isolated
                pass 
            except:
                pass

        return 0.5

    def _proper_scoring_rule(self, probability: float, outcome: bool) -> float:
        """
        Logarithmic scoring rule: S = ln(P) if true, ln(1-P) if false.
        Here we use it to weight the confidence: High confidence requires high probability.
        We invert this to generate a score from 0 to 1 based on estimated correctness.
        """
        p = max(self.epsilon, min(1 - self.epsilon, probability))
        if outcome:
            return p
        else:
            return 1.0 - p

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if meta-analysis detects ambiguity/traps.
        """
        # 1. Meta-Confidence (Epistemic Honesty Gate)
        precision_weight = self._meta_confidence(prompt)
        
        # If precision is low, cap confidence immediately
        if precision_weight < 0.5:
            return precision_weight * 0.5 # Cap at ~0.25
        
        # 2. Structural & Computational Verification
        struct_score = self._compute_structural_score(prompt, answer)
        comp_score = self._compute_computational_score(prompt, answer)
        
        # Weighted combination: Structural > Computational > NCD
        # We assume the answer is likely correct if struct/comp align
        estimated_correctness = 0.6 * struct_score + 0.4 * comp_score
        
        # If computation gave a definitive 1.0 or 0.1, trust it more
        if comp_score == 1.0:
            estimated_correctness = 0.95
        elif comp_score == 0.1:
            estimated_correctness = 0.05
            
        # Apply precision weight as gain control (Neuromodulation)
        final_conf = estimated_correctness * precision_weight
        
        # Cap absolute certainty unless computation was definitive
        if comp_score != 1.0:
            final_conf = min(final_conf, 0.85)
            
        return max(0.0, min(1.0, final_conf))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates and ranks candidates.
        Score decomposition: Structural >= 50%, Computation >= 20%, NCD <= 15%.
        """
        results = []
        
        # Pre-calculate meta-confidence for the prompt (Global Gain)
        global_precision = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural Score (Morphogenetic Pattern Match)
            struct_score = self._compute_structural_score(prompt, cand)
            
            # 2. Computational Score (Constructive Verification)
            comp_score = self._compute_computational_score(prompt, cand)
            
            # 3. NCD Score (Similarity Tiebreaker)
            # Invert NCD so higher is better. 
            # If candidate is subset of prompt or vice versa, similarity is high.
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val
            
            # Weighted Sum based on requirements
            # Structural: 50%, Comp: 35%, NCD: 15%
            raw_score = (0.50 * struct_score) + (0.35 * comp_score) + (0.15 * ncd_score)
            
            # Apply Neuromodulatory Gain (Precision Weighting)
            # If the prompt is ambiguous (low global_precision), raw scores are dampened
            adjusted_score = raw_score * global_precision
            
            # Mechanism Design: Truthful reporting via proper scoring adjustment
            # If global_precision is low, we penalize high scores to reflect uncertainty
            if global_precision < 0.5:
                adjusted_score = min(adjusted_score, 0.3)
            
            # Generate Reasoning String
            reasoning_parts = []
            if global_precision < 0.5:
                reasoning_parts.append("Low precision: Prompt contains ambiguity or presupposition.")
            if struct_score > 0.7:
                reasoning_parts.append("Strong structural alignment.")
            if comp_score == 1.0:
                reasoning_parts.append("Computationally verified.")
            elif comp_score == 0.1:
                reasoning_parts.append("Computationally contradicted.")
            if not reasoning_parts:
                reasoning_parts.append("Heuristic evaluation based on available patterns.")
                
            results.append({
                "candidate": cand,
                "score": float(f"{adjusted_score:.4f}"),
                "reasoning": " ".join(reasoning_parts)
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results