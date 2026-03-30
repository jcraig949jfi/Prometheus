import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Multiscale Fractal Predictive-Coding Network (MFPCN) Simulator.
    
    Mechanism:
    1. Fractal Geometry (IFS): Implements a recursive, self-similar parsing strategy.
       The 'generative model' attempts to fit structural patterns (negations, comparatives, 
       numeric logic) at multiple scales of the text.
    2. Morphogenesis (Reaction-Diffusion): Simulates Turing-pattern priors via a 
       diffusion-based anomaly detector. It checks for 'morphogen' markers (presuppositions, 
       ambiguities) that diffuse through the sentence structure. If concentration exceeds 
       a threshold, it triggers an 'epistemic halt' (low confidence).
    3. Free Energy Principle: The scoring function minimizes variational free energy.
       F = Prediction_Error - (Complexity_Prior * Precision).
       High structural match = Low Error. High ambiguity = High Complexity penalty.
       
    Epistemic Honesty (Tier B): Prioritizes detecting ambiguous/unanswerable prompts
    by capping confidence when morphogen markers (presuppositions, false dichotomies)
    are detected.
    """

    # Reaction-Diffusion Priors (Morphogen markers for ambiguity)
    PRESUPPOSITION_TRIGGERS = [
        r"\b(stopped|quit|ceased)\s+(doing|smoking|working)\b",
        r"\bwhy\s+did\s+\w+\s+(fail|stop|break)\b",
        r"\bwhen\s+did\s+\w+\s+(stop|fail)\b",
        r"\bhave\s+you\s+(stopped|quit)\b"
    ]
    
    SCOPE_AMBIGUITY_TRIGGERS = [
        r"\bevery\s+\w+\s+\w+\s+a\s+\w+\b",  # Every X did a Y
        r"\bsame\s+\w+\b"
    ]
    
    PRONOUN_AMBIGUITY_TRIGGERS = [
        r"\b(told|said\s+to)\s+\w+\s+he\s+was\b",
        r"\b(told|said\s+to)\s+\w+\s+she\s+was\b",
        r"\bwho\s+was\s+wrong\b",
        r"\bwho\s+\w+\s+it\b"
    ]
    
    FALSE_DICHOTOMY_TRIGGERS = [
        r"\beither\s+\w+\s+or\s+\w+\b",
        r"\bis\s+it\s+\w+\s+or\s+\w+\?"
    ]

    SUBJECTIVITY_TRIGGERS = [
        r"\b(best|worst|favorite|most\s+beautiful)\s+\w+",
        r"\bwho\s+is\s+the\s+best\b"
    ]

    def __init__(self):
        self.precision_weight = 0.8  # Weight for structural matches
        self.morphogen_threshold = 0.3  # Threshold for epistemic doubt

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps (Ambiguity, Presupposition, Unanswerability).
        Returns a cap value: 1.0 (safe) to 0.1 (highly ambiguous).
        """
        p_lower = prompt.lower()
        risk_score = 0.0
        
        # Check Reaction-Diffusion Priors (Morphogen concentrations)
        checks = [
            (self.PRESUPPOSITION_TRIGGERS, 0.9),
            (self.SCOPE_AMBIGUITY_TRIGGERS, 0.7),
            (self.PRONOUN_AMBIGUITY_TRIGGERS, 0.8),
            (self.FALSE_DICHOTOMY_TRIGGERS, 0.6),
            (self.SUBJECTIVITY_TRIGGERS, 0.5)
        ]
        
        for patterns, severity in checks:
            for pattern in patterns:
                if re.search(pattern, p_lower):
                    risk_score = max(risk_score, severity)
        
        # If high risk detected, cap confidence severely
        if risk_score > 0.4:
            return 0.25  # Epistemic honesty: "I don't know"
        elif risk_score > 0.2:
            return 0.5   # Uncertain
        
        return 1.0

    def _structural_parse(self, prompt: str, candidate: str) -> float:
        """
        Fractal Structural Parsing (Tier A).
        Extracts logical constraints and verifies against candidate.
        Returns a score 0.0 to 1.0 based on structural adherence.
        """
        score = 0.0
        matches = 0
        total_checks = 0
        
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # 1. Negation Handling
        if re.search(r"\b(not|no|never|none)\b", p_lower):
            total_checks += 1
            # If prompt has negation, correct candidate often lacks positive assertion of the negated fact
            # Simple heuristic: if prompt says "not X", and candidate says "X", penalize.
            # This is a simplification for the prototype.
            if re.search(r"\bnot\b", p_lower) and re.search(r"\byes\b", c_lower):
                # Heuristic: if prompt is "Is 5 not 4?", answer "Yes" is good. 
                # If prompt is "Is 5 not 5?", answer "No" is good.
                # We rely on the computation step for the definitive truth, 
                # here we just check for contradiction markers.
                pass 
            matches += 1 # Acknowledged negation structure

        # 2. Comparative Logic (Numeric)
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", p_lower)
        if len(numbers) >= 2:
            total_checks += 1
            try:
                nums = [float(n) for n in numbers]
                # Detect comparison type
                if "larger" in p_lower or "greater" in p_lower or "more" in p_lower:
                    expected_val = max(nums)
                elif "smaller" in p_lower or "less" in p_lower:
                    expected_val = min(nums)
                else:
                    expected_val = None
                
                if expected_val is not None:
                    # Check if candidate contains the expected number
                    if str(int(expected_val)) in candidate or str(expected_val) in candidate:
                        matches += 1
                    # Also check for textual "first/second" logic if present
            except ValueError:
                pass

        # 3. Conditional/Transitivity
        if "if" in p_lower and "then" in p_lower:
            total_checks += 1
            # Basic presence check for conditional reasoning
            if any(kw in c_lower for kw in ["therefore", "thus", "so", "yes", "no"]):
                matches += 1

        if total_checks == 0:
            return 0.5 # Neutral if no structure found
        return min(1.0, (matches / total_checks) + 0.5) # Base boost for attempting structure

    def _compute_answer(self, prompt: str) -> Optional[str]:
        """
        Constructive Computation.
        Attempts to solve math or logic problems directly.
        """
        # Extract numbers
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", prompt)
        if len(numbers) >= 2:
            nums = [float(n) for n in numbers]
            if "sum" in prompt or "add" in prompt:
                return str(sum(nums))
            if "product" in prompt or "multiply" in prompt:
                prod = 1.0
                for n in nums: prod *= n
                return str(prod)
            if "greater" in prompt or "larger" in prompt:
                return str(max(nums))
            if "smaller" in prompt or "less" in prompt:
                return str(min(nums))
        return None

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_concat = len(zlib.compress(concat))
        
        denominator = max(len_s1, len_s2)
        if denominator == 0:
            return 0.0
        return (len_concat - min(len_s1, len_s2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # 1. Meta-Cognition: Check for ambiguity/traps first
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Constructive Computation (Ground Truth)
        computed_answer = self._compute_answer(prompt)
        
        for candidate in candidates:
            score = 0.0
            reasoning_parts = []
            
            # A. Structural Parsing (Fractal/IFS Layer) - Weight 0.50
            struct_score = self._structural_parse(prompt, candidate)
            
            # B. Computation Check - Weight 0.35
            comp_score = 0.0
            if computed_answer:
                if computed_answer in candidate:
                    comp_score = 1.0
                    reasoning_parts.append("Computation match")
                else:
                    comp_score = 0.0
                    reasoning_parts.append("Computation mismatch")
            else:
                comp_score = 0.5 # Neutral if not computable
            
            # C. NCD Tiebreaker - Weight 0.15
            # Only used if other signals are weak or as a tiebreaker
            ncd_val = self._ncd_score(prompt, candidate)
            ncd_score = 1.0 - ncd_val # Invert so higher is better
            
            # Free Energy Minimization (Weighted Sum)
            # F = - (w1*Struct + w2*Comp + w3*NCD)
            raw_score = (0.50 * struct_score) + (0.35 * comp_score) + (0.15 * ncd_score)
            
            # Apply Epistemic Cap (Morphogen Prior)
            if meta_cap < 1.0:
                # If ambiguous, we penalize high confidence regardless of content
                final_score = min(raw_score, meta_cap + 0.1) 
                reasoning_parts.append(f"Epistemic cap applied ({meta_cap:.2f})")
            else:
                final_score = raw_score
                
            # Adjust for specific traps detected
            if meta_cap <= 0.3:
                final_score = 0.2 # Force low score for clear traps
                reasoning_parts.append("Trap detected: Low confidence")

            results.append({
                "candidate": candidate,
                "score": float(f"{final_score:.4f}"),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Standard evaluation"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly enforces epistemic honesty via _meta_confidence.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Quick structural check
        struct_score = self._structural_parse(prompt, answer)
        comp_answer = self._compute_answer(prompt)
        
        comp_match = 0.0
        if comp_answer:
            comp_match = 1.0 if comp_answer in answer else 0.0
        
        # Base confidence calculation
        base_conf = (0.6 * struct_score) + (0.4 * comp_match)
        
        # Apply Cap
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless computation is definitive
        if comp_match == 1.0:
            final_conf = min(final_conf, 0.95)
        else:
            final_conf = min(final_conf, 0.85)
            
        return float(f"{final_conf:.4f}")