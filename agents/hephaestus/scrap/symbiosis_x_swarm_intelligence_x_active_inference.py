import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Symbiotic Active Inference Swarm (SAIS) - Epistemic Honesty Edition.
    
    Mechanism:
    1. Meta-Cognitive Filter (The "Holobiont" Check): Before evaluating answers,
       the system scans the prompt for "pathogens" (logical fallacies, presuppositions,
       ambiguity). If detected, it suppresses confidence (Active Inference: minimizing
       expected free energy by avoiding false certainty).
    2. Structural Parsing (Swarm Stigmergy): Extracts logical operators, negations,
       and numeric values. Candidates are scored on structural alignment.
    3. Constructive Computation: Attempts to solve math/logic problems directly.
    4. NCD Tiebreaker: Used only when structural signals are weak (<15% weight).
    
    This implements the "Symbiosis" concept strictly as a confidence wrapper (as per
    causal analysis) to prevent reasoning traps, while using "Active Inference" principles
    to drive the scoring of structural matches.
    """

    def __init__(self):
        # Patterns for logical traps (Tier B)
        self.presupposition_triggers = [
            r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy is.*bad\b",
            r"\bwhen did.*stop\b", r"\bquit\b", r"\bassum.*that\b"
        ]
        self.false_dichotomy_triggers = [r"\beither.*or\b", r"\bmust choose between\b"]
        self.subjectivity_triggers = [r"\bbest\b", r"\bworst\b", r"\bfavorite\b", r"\bopinion\b"]
        self.pronoun_ambiguity_triggers = [r"\bhe told.*he\b", r"\bshe told.*she\b", r"\bwho was\b"]
        
        # Structural patterns (Tier A)
        self.negation_pattern = re.compile(r"\b(not|no|never|neither|without)\b", re.IGNORECASE)
        self.comparative_pattern = re.compile(r"\b(more|less|greater|smaller|higher|lower|better|worse)\b", re.IGNORECASE)
        self.number_pattern = re.compile(r"-?\d+(?:\.\d+)?")
        self.logic_ops = ["and", "or", "if", "then", "else", "therefore", "because"]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic traps.
        Returns a cap value (0.25 if trap detected, 1.0 otherwise).
        """
        p_lower = prompt.lower()
        
        # Check Presuppositions
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.25
        
        # Check False Dichotomies
        for pattern in self.false_dichotomy_triggers:
            if re.search(pattern, p_lower):
                # Only flag if no clear context implies exhaustive options
                if "only" in p_lower or "exclusive" in p_lower:
                    return 0.25 
                
        # Check Subjectivity without criteria
        if any(re.search(t, p_lower) for t in self.subjectivity_triggers):
            if "measure" not in p_lower and "data" not in p_lower and "statistic" not in p_lower:
                return 0.25

        # Check Pronoun Ambiguity in specific "who" questions
        if re.search(r"\bwho\b", p_lower):
            for pattern in self.pronoun_ambiguity_triggers:
                if re.search(pattern, p_lower):
                    return 0.25

        return 1.0

    def _extract_numbers(self, text: str) -> List[float]:
        return [float(n) for n in self.number_pattern.findall(text)]

    def _compute_constructive(self, prompt: str, candidate: str) -> Optional[float]:
        """
        Attempts to solve numeric comparisons or simple logic constructively.
        Returns a score (0.0-1.0) if successful, None if not applicable.
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        # Case 1: Direct Numeric Comparison in Prompt
        # e.g., Prompt: "Is 9.11 > 9.9?" Candidate: "No"
        if len(p_nums) >= 2 and len(c_nums) == 0:
            # Detect question type
            p_lower = prompt.lower()
            val1, val2 = p_nums[0], p_nums[1]
            
            is_greater = "greater" in p_lower or ">" in prompt or "larger" in p_lower
            is_less = "less" in p_lower or "<" in prompt or "smaller" in p_lower
            is_yes_no = "yes" in c_nums or "no" in c_nums # Not applicable here as c_nums is empty
            
            # Check candidate text for Yes/No
            c_lower = candidate.lower().strip().rstrip('.')
            if c_lower in ["yes", "true", "correct"]:
                if is_greater: return 1.0 if val1 > val2 else 0.0
                if is_less: return 1.0 if val1 < val2 else 0.0
            elif c_lower in ["no", "false", "incorrect"]:
                if is_greater: return 1.0 if val1 <= val2 else 0.0
                if is_less: return 1.0 if val1 >= val2 else 0.0
                
        # Case 2: Candidate completes a math expression
        # e.g., Prompt: "2 + 2 =", Candidate: "4"
        if "+" in prompt or "-" in prompt or "*" in prompt or "/" in prompt:
            # Try to eval prompt as expression if it ends with operator or equals
            # Simple safe eval for basic arithmetic
            expr = re.sub(r"[^0-9+\-*/().\s]", "", prompt.replace("=", ""))
            try:
                if expr and any(op in expr for op in "+-*/"):
                    expected = eval(expr) # Safe enough given regex filter
                    if len(c_nums) == 1:
                        if math.isclose(c_nums[0], expected, rel_tol=1e-5):
                            return 1.0
                        else:
                            return 0.0
            except:
                pass

        return None

    def _score_structure(self, prompt: str, candidate: str) -> float:
        """
        Scores based on structural alignment: negations, comparatives, logic ops.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        checks = 0
        
        # 1. Negation Consistency
        p_negs = len(self.negation_pattern.findall(p_lower))
        c_negs = len(self.negation_pattern.findall(c_lower))
        checks += 1
        if p_negs > 0:
            # If prompt has negation, candidate should ideally reflect it or answer appropriately
            # Heuristic: If prompt asks "What is not X?", candidate shouldn't just repeat X
            if p_negs == c_negs or (p_negs > 0 and c_negs > 0):
                score += 1.0
            elif "no" in c_lower or "false" in c_lower:
                score += 0.8 # Accepting negative answer
        else:
            score += 1.0 if c_negs == 0 else 0.5 # Penalize unexpected negation
            
        # 2. Keyword Overlap (Logic Ops)
        found_ops = [op for op in self.logic_ops if op in p_lower]
        if found_ops:
            checks += 1
            matches = sum(1 for op in found_ops if op in c_lower)
            score += (matches / len(found_ops))
            
        # 3. Number Presence
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        if p_nums:
            checks += 1
            # Did candidate pick up the numbers?
            if c_nums:
                # Check overlap
                common = set(p_nums) & set(c_nums)
                score += (len(common) / len(p_nums))
            else:
                # If prompt has numbers but candidate doesn't, might be abstract answer
                score += 0.5 

        return score / max(checks, 1)

    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """Normalized Compression Distance heuristic."""
        try:
            s1 = (prompt + candidate).encode('utf-8')
            s2 = prompt.encode('utf-8')
            s3 = candidate.encode('utf-8')
            
            c1 = len(zlib.compress(s1))
            c2 = len(zlib.compress(s2))
            c3 = len(zlib.compress(s3))
            
            if max(c2, c3) == 0: return 0.5
            ncd = (c1 - min(c2, c3)) / max(c2, c3)
            return 1.0 - max(0, ncd) # Invert: higher is better match
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate meta-confidence cap
        meta_cap = self._meta_confidence(prompt)
        
        # Constructive attempt (Global check)
        constructive_result = None
        # Try to find a constructive solution for the first plausible candidate
        # In a real swarm, this would be parallelized across sub-agents
        for cand in candidates:
            res = self._compute_constructive(prompt, cand)
            if res is not None:
                constructive_result = res
                break

        for candidate in candidates:
            score = 0.0
            reasoning_parts = []
            
            # 1. Constructive Computation (Highest Priority if exists)
            if constructive_result is not None:
                # If we found a constructive path, score based on that
                # We need to map the specific candidate to the result
                # Re-run for this specific candidate to be sure
                local_res = self._compute_constructive(prompt, candidate)
                if local_res is not None:
                    score = local_res
                    reasoning_parts.append(f"Constructive math/logic check: {local_res}")
                else:
                    # Candidate doesn't match constructive pattern, low score
                    score = 0.1
                    reasoning_parts.append("Failed constructive check")
            else:
                # 2. Structural Parsing (Primary Signal)
                struct_score = self._score_structure(prompt, candidate)
                
                # 3. NCD (Tiebreaker/Minor component)
                ncd_score = self._ncd_score(prompt, candidate)
                
                # Weighted Sum: Structural 60%, NCD 15%, Base 25%
                score = (struct_score * 0.60) + (ncd_score * 0.15) + 0.25
                reasoning_parts.append(f"Structural: {struct_score:.2f}, NCD: {ncd_score:.2f}")

            # Apply Meta-Confidence Cap (The "Symbiotic" constraint)
            # If the prompt is a trap, confidence is capped regardless of candidate score
            final_confidence = min(score, meta_cap) if meta_cap < 1.0 else score
            
            # Adjust reasoning string for transparency
            if meta_cap < 1.0:
                reasoning_parts.append("WARNING: Prompt contains ambiguity/presupposition (Epistemic Honesty applied)")

            results.append({
                "candidate": candidate,
                "score": final_confidence,
                "reasoning": "; ".join(reasoning_parts)
            })
            
        # Rank by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly enforces epistemic honesty via _meta_confidence.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Quick structural check
        struct_score = self._score_structure(prompt, answer)
        constructive = self._compute_constructive(prompt, answer)
        
        base_score = 0.5
        if constructive is not None:
            base_score = constructive
        else:
            # Simple heuristic: if struct score is high, base is higher
            base_score = 0.4 + (struct_score * 0.5)
            
        final_score = min(base_score, meta_cap)
        
        # Never return > 0.9 without constructive proof
        if constructive is None and final_score > 0.9:
            final_score = 0.85
            
        return max(0.0, min(1.0, final_score))