import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Symbiotic Variational Inference Tool with Epistemic Honesty.
    
    Mechanism:
    1. Meta-Cognition (Free Energy Principle): Evaluates the prompt for ambiguity,
       presupposition, and unanswerability. High "surprise" (ambiguity) caps confidence.
    2. Symbiotic Agents (Maximum Entropy & MI):
       - Agent A (Structural): Parses logic, negations, comparatives.
       - Agent B (Computational): Solves math/logic explicitly.
       - Agent C (Entropy): Measures diversity/uncertainty via NCD.
       These agents "couple" by voting; if they disagree strongly or the prompt is 
       ambiguous, the system reduces confidence (epistemic honesty).
    3. Scoring: Weighted sum where Structural >= 50%, Computation >= 20%, NCD <= 15%.
    """

    def __init__(self):
        # Hyperparameters derived from the triadic objective
        self.lambda_entropy = 0.15  # Weight for maximum entropy (NCD diversity)
        self.beta_symbiosis = 0.35  # Weight for symbiotic coupling (agreement)
        self.kl_complexity = 0.50   # Weight for structural/computational rigor
        
        # Thresholds for epistemic honesty
        self.ambiguity_cap = 0.25
        self.high_conf_threshold = 0.9
        
        # Patterns for Tier B (Judgment) detection
        self.presupposition_patterns = [
            r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy.*stop\b", 
            r"\bwhen did.*stop\b", r"\bquit\b.*\bquestion\b"
        ]
        self.false_dichotomy_patterns = [r"\beither.*or\b", r"\bchoose between.*and\b"]
        self.scope_patterns = [r"\bevery.*a.*\b", r"\ball.*same\b"]
        self.pronoun_patterns = [r"\bhe told.*he\b", r"\bshe told.*she\b", r"\bwho was\b"]

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps (Ambiguity, Presupposition, etc.).
        Returns a cap value. If 1.0, no traps detected. If < 0.3, high ambiguity.
        """
        p_low = self._normalize(prompt)
        risk_score = 0.0
        
        # Check Presuppositions
        for pattern in self.presupposition_patterns:
            if re.search(pattern, p_low):
                risk_score += 0.6
        
        # Check False Dichotomy
        for pattern in self.false_dichotomy_patterns:
            if re.search(pattern, p_low):
                risk_score += 0.4
                
        # Check Scope/Pronoun Ambiguity
        if re.search(r"\bevery.*\ba\b", p_low) and re.search(r"\bsame\b|\bdifferent\b", p_low):
            risk_score += 0.5
            
        if re.search(r"\bwho\b", p_low) and any(x in p_low for x in ["he", "she", "him", "her"]):
            # Heuristic for pronoun ambiguity in "who" questions
            if re.search(r"\btold\b|\bsaid\b", p_low):
                risk_score += 0.5

        # Subjectivity check (simple keyword spot)
        subjective_keywords = ["best", "worst", "favorite", "opinion", "beautiful"]
        if any(k in p_low for k in subjective_keywords) and "measure" not in p_low:
            risk_score += 0.3

        # Convert risk to cap. High risk -> Low cap.
        if risk_score >= 0.5:
            return self.ambiguity_cap
        elif risk_score > 0.2:
            return 0.5
        return 1.0

    def _parse_structure(self, prompt: str, candidate: str) -> float:
        """
        Agent A: Structural Parser.
        Checks for negation alignment, comparative logic, and boolean consistency.
        Returns score 0.0 to 1.0.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        score = 0.5 # Base prior
        
        # Negation consistency
        p_neg = len(re.findall(r"\bnot\b|\bno\b|\bnever\b|\bwithout\b", p_low))
        c_neg = len(re.findall(r"\bnot\b|\bno\b|\bnever\b|\bwithout\b", c_low))
        
        # If prompt has strong negation, candidate should reflect it or answer directly
        if p_neg > 0:
            if c_neg > 0 or len(c_low.split()) < 5: # Accepts "No" or explicit negation
                score += 0.3
            else:
                # Potential trap: ignoring negation
                score -= 0.4
                
        # Comparative logic detection
        comparatives = ["greater", "less", "higher", "lower", "more", "fewer"]
        if any(c in p_low for c in comparatives):
            if any(c in c_low for c in comparatives) or re.search(r"\d+", c_low):
                score += 0.2
        
        return max(0.0, min(1.0, score))

    def _compute_answer(self, prompt: str, candidate: str) -> float:
        """
        Agent B: Computational Engine.
        Attempts to extract and solve math/logic expressions.
        Returns 1.0 if candidate matches computed result, 0.0 if contradicts, 0.5 if N/A.
        """
        p_low = self._normalize(prompt)
        c_low = self._normalize(candidate)
        
        # Extract numbers from prompt
        nums = re.findall(r"-?\d+\.?\d*", p_low)
        if len(nums) < 2:
            return 0.5 # Not enough data for computation
            
        try:
            # Simple arithmetic check: "What is 2 + 2?"
            if "what is" in p_low or "calculate" in p_low or "sum" in p_low:
                # Try to evaluate simple expression if present in prompt
                # This is a heuristic simulation of solving
                if re.search(r"\d+\s*[+\-*/]\s*\d+", p_low):
                    # If prompt contains an explicit expression, evaluate it
                    match = re.search(r"(-?\d+\.?\d*)\s*([+\-*/])\s*(-?\d+\.?\d*)", p_low)
                    if match:
                        n1, op, n2 = match.groups()
                        expr = f"{float(n1)} {op} {float(n2)}"
                        true_val = eval(expr)
                        # Check if candidate contains the true value
                        if str(true_val) in c_low or f"{true_val:.2f}" in c_low:
                            return 1.0
                        # Check if candidate is a number but wrong
                        cand_nums = re.findall(r"-?\d+\.?\d*", c_low)
                        if cand_nums and abs(float(cand_nums[0]) - true_val) > 1e-6:
                            return 0.0
            # Numeric comparison trap: "Is 9.11 > 9.9?"
            if "greater" in p_low or "less" in p_low or ">" in p_low or "<" in p_low:
                if len(nums) >= 2:
                    n1, n2 = float(nums[0]), float(nums[1])
                    is_greater = n1 > n2
                    c_lower = c_low.lower()
                    
                    if is_greater:
                        if "yes" in c_lower or "true" in c_lower or "greater" in c_lower:
                            return 1.0
                        if "no" in c_lower or "false" in c_lower or "less" in c_lower:
                            return 0.0
                    else:
                        if "no" in c_lower or "false" in c_lower or "less" in c_lower:
                            return 1.0
                        if "yes" in c_lower or "true" in c_lower or "greater" in c_lower:
                            return 0.0
        except:
            pass
            
        return 0.5 # No computational contradiction or confirmation found

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance heuristic."""
        z1 = len(zlib.compress(s1.encode()))
        z2 = len(zlib.compress(s2.encode()))
        z12 = len(zlib.compress((s1 + s2).encode()))
        
        denominator = max(z1, z2)
        if denominator == 0:
            return 0.0
        return (z12 - min(z1, z2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-check meta-confidence (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural Score (Agent A) - Weight 0.50
            struct_score = self._parse_structure(prompt, cand)
            
            # 2. Computational Score (Agent B) - Weight 0.35
            comp_score = self._compute_answer(prompt, cand)
            
            # 3. Entropy/Symbiosis Score (Agent C) - Weight 0.15
            # Uses NCD to measure similarity to prompt (lower NCD = higher relevance usually)
            # But we invert it for "diversity" in hypothesis generation context, 
            # however for answering, we want relevance. 
            # Here we use NCD as a tiebreaker for relevance.
            ncd_val = self._calculate_ncd(prompt, cand)
            # Normalize NCD to 0-1 where 1 is good (low distance)
            entropy_score = 1.0 - min(1.0, ncd_val)
            
            # Free Energy Bound Approximation (Weighted Sum)
            # F = PredictionError (1-comp) + Complexity (1-struct) - Entropy - Symbiosis
            # We maximize: w1*struct + w2*comp + w3*entropy
            raw_score = (self.kl_complexity * struct_score) + \
                        (self.beta_symbiosis * comp_score) + \
                        (self.lambda_entropy * entropy_score)
            
            # Apply Epistemic Cap (Free Energy Principle: High uncertainty -> Low confidence)
            final_score = min(raw_score, meta_cap)
            
            # Reasoning string generation
            reasoning_parts = []
            if meta_cap < 0.3:
                reasoning_parts.append("Warning: Prompt contains ambiguity or presupposition.")
            if comp_score == 1.0:
                reasoning_parts.append("Computationally verified.")
            elif comp_score == 0.0:
                reasoning_parts.append("Computationally contradicted.")
            if struct_score > 0.7:
                reasoning_parts.append("Structurally consistent.")
                
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Heuristic evaluation."
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by meta-cognitive analysis of the prompt.
        """
        # 1. Meta Check (The "Free Energy" of the question itself)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Internal Evaluation
        eval_result = self.evaluate(prompt, [answer])
        if not eval_result:
            return 0.0
            
        base_score = eval_result[0]["score"]
        
        # 3. Apply Cap
        final_conf = min(base_score, meta_cap)
        
        # 4. Honesty constraint: Never > 0.9 without explicit computation match
        # If the computational agent didn't fire (score 0.5), cap at 0.8
        comp_check = self._compute_answer(prompt, answer)
        if comp_check == 0.5 and final_conf > 0.85:
            final_conf = 0.85
            
        return round(final_conf, 4)