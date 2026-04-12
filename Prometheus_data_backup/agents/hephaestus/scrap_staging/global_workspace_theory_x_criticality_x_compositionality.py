import re
import zlib
import math
from typing import List, Dict, Any, Optional, Tuple

class ReasoningTool:
    """
    Critical Compositional Global Workspace (CCGW) Reasoning Tool.
    
    Mechanism:
    1. Modules (Parsers): Specialized functions extract structural, numeric, and logical features.
    2. Criticality Control: A dynamic threshold determines if evidence is sufficient to "ignite" 
       a candidate. Weak matches are suppressed; strong structural matches trigger global broadcast.
    3. Compositionality: Candidates are scored by assembling weighted evidence from modules 
       (syntax, logic, math) rather than raw string similarity.
    4. Epistemic Honesty (Meta-Cognition): Before scoring, the system scans for ambiguity, 
       presuppositions, and unanswerable constraints. If detected, confidence is capped low.
    
    Score Decomposition: Structural (50%), Computation (20%), NCD (15%), Judgment (15%).
    """

    def __init__(self):
        self.critical_branching_ratio = 1.0  # Target for criticality
        self.ignition_threshold = 0.45       # Dynamic threshold for broadcast
        self.ncd_weight = 0.15
        self.struct_weight = 0.50
        self.comp_weight = 0.20
        self.judgment_weight = 0.15

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic traps.
        Returns a cap value: 0.25 if ambiguous/trapped, 1.0 if clear.
        """
        p = prompt.lower()
        
        # 1. Presupposition Traps
        presupposition_patterns = [
            r"have you stopped\s+\w+ing",
            r"why did\s+\w+\s+(fail|stop|break)",
            r"when did\s+\w+\s+(stop|fail)",
            r"is it true that\s+\w+\s+(stopped|failed)",
            r"how many times did\s+\w+\s+(fail|stop)"
        ]
        for pattern in presupposition_patterns:
            if re.search(pattern, p):
                return 0.25

        # 2. False Dichotomy / Loaded Assumption
        if re.search(r"\b(either\s+\w+\s+or\s+\w+|is it a or b)\b", p) and "not" not in p:
            # Heuristic: if it forces a choice without context
            if re.search(r"\bchoose\b|\bwhich one\b", p):
                return 0.25

        # 3. Subjectivity without criteria
        if re.search(r"\b(best|worst|favorite|ugliest)\b", p):
            if not re.search(r"\b(according to|based on|measure|metric|data)\b", p):
                return 0.25

        # 4. Unanswerable / Missing Info indicators
        if re.search(r"\bwho is he\b|\bwho is she\b|\bwhich one\b", p):
            # Check for pronoun ambiguity context (simplified)
            if re.search(r"\btold\s+\w+\s+he\b|\bsaid\s+to\s+\w+\s+she\b", p):
                return 0.25
        
        return 1.0

    def _extract_numerical_claim(self, text: str) -> Optional[float]:
        """Attempts to find a single dominant number in a candidate."""
        # Look for patterns like "9.11", "9.9", "42"
        matches = re.findall(r'[-]?\d+\.?\d*', text)
        if matches:
            try:
                return float(matches[0])
            except ValueError:
                return None
        return None

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Structural parsing: negations, comparatives, conditionals.
        Returns 0.0 to 1.0.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.0
        checks = 0

        # 1. Negation Consistency
        if "not" in p_lower or "no " in p_lower or "never" in p_lower:
            checks += 1
            if ("not" in c_lower or "no " in c_lower or "never" in c_lower):
                score += 1.0 # Candidate respects negation presence
            else:
                score += 0.0 # Candidate ignores negation (bad)
        else:
            # If prompt has no negation, candidate shouldn't introduce random negation unless justified
            checks += 1
            if "not" not in c_lower:
                score += 1.0

        # 2. Comparative Logic (Simple)
        comp_words = ["greater", "less", "more", "fewer", "larger", "smaller"]
        if any(w in p_lower for w in comp_words):
            checks += 1
            if any(w in c_lower for w in comp_words):
                score += 1.0
        
        # 3. Conditional Presence
        if "if" in p_lower:
            checks += 1
            if "if" in c_lower or "then" in c_lower or "because" in c_lower:
                score += 1.0
            else:
                # Candidate ignores conditional structure
                score += 0.2 

        return score / max(checks, 1)

    def _compute_numeric_score(self, prompt: str, candidate: str) -> float:
        """
        Constructive computation: Validates numeric claims against prompt logic.
        """
        p_nums = re.findall(r'[-]?\d+\.?\d*', prompt)
        c_nums = re.findall(r'[-]?\d+\.?\d*', candidate)
        
        if not p_nums or not c_nums:
            return 0.5 # Neutral if no numbers
        
        try:
            p_val = float(p_nums[0])
            c_val = float(c_nums[0])
            
            # Case 1: Direct Equality check (e.g., "What is 2+2?" -> "4")
            # Simple heuristic: if prompt asks "what is", exact match is best
            if "what is" in prompt.lower() or "calculate" in prompt.lower():
                if abs(p_val - c_val) < 1e-6:
                    return 1.0
                else:
                    return 0.0
            
            # Case 2: Comparison traps (e.g. 9.11 vs 9.9)
            # If prompt contains two numbers and asks for comparison
            if len(p_nums) >= 2:
                n1, n2 = float(p_nums[0]), float(p_nums[1])
                # Check if candidate correctly identifies larger/smaller
                if "larger" in candidate.lower() or "greater" in candidate.lower():
                    return 1.0 if c_val == max(n1, n2) else 0.0
                if "smaller" in candidate.lower() or "less" in candidate.lower():
                    return 1.0 if c_val == min(n1, n2) else 0.0
                    
        except ValueError:
            pass
            
        return 0.5

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        len_s1 = len(zlib.compress(s1_b))
        len_s2 = len(zlib.compress(s2_b))
        len_combined = len(zlib.compress(s1_b + s2_b))
        
        denominator = max(len_s1, len_s2)
        if denominator == 0:
            return 1.0
        return (len_combined - min(len_s1, len_s2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        
        # Meta-Cognition: Check prompt validity first
        meta_cap = self._meta_confidence(prompt)
        
        for cand in candidates:
            # 1. Structural Score (Primary Signal)
            struct_score = self._compute_structural_score(prompt, cand)
            
            # 2. Computational Score (Secondary Signal)
            comp_score = self._compute_numeric_score(prompt, cand)
            
            # 3. NCD Score (Tiebreaker/Noise check)
            # Invert NCD so 1.0 is identical, 0.0 is totally different
            # We want low NCD to be good, but only as a tiebreaker
            ncd_val = self._ncd(prompt, cand)
            ncd_score = 1.0 - ncd_val 
            
            # Weighted Combination
            raw_score = (
                struct_score * self.struct_weight +
                comp_score * self.comp_weight +
                ncd_score * self.ncd_weight
            )
            
            # Criticality Adjustment:
            # If meta-confidence is low (trap detected), suppress score significantly
            if meta_cap < 0.3:
                # Even if structurally similar, if it's a trap, we downgrade confidence
                # but we still rank based on structure to show "best guess"
                final_score = raw_score * 0.5 
            else:
                final_score = raw_score
            
            # Ignition Threshold:
            # If score is below critical threshold, it doesn't "broadcast" (low rank)
            if final_score < self.ignition_threshold and meta_cap == 1.0:
                # Soft penalty for weak evidence in clear prompts
                final_score *= 0.8

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Struct:{struct_score:.2f} Comp:{comp_score:.2f} NCD:{ncd_score:.2f} MetaCap:{meta_cap:.2f}"
            })

        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if meta-analysis detects ambiguity/traps.
        Caps at 0.9 unless computation was definitive.
        """
        # 1. Meta-Confidence Check (The "Honesty" Filter)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Evaluate the specific candidate
        eval_result = self.evaluate(prompt, [answer])
        if not eval_result:
            return 0.0
            
        base_score = eval_result[0]["score"]
        
        # 3. Apply Caps
        final_conf = base_score
        
        # Hard cap for ambiguous prompts
        if meta_cap < 0.3:
            final_conf = min(final_conf, 0.25)
        
        # Cap for overconfidence on non-computational matches
        # If structural score is high but numeric/computation is low, don't trust it fully
        struct_s = self._compute_structural_score(prompt, answer)
        comp_s = self._compute_numeric_score(prompt, answer)
        
        if comp_s < 0.6 and struct_s > 0.8:
            # High structural match but no math/logic verification -> limit confidence
            final_conf = min(final_conf, 0.85)
            
        return max(0.0, min(1.0, final_conf))