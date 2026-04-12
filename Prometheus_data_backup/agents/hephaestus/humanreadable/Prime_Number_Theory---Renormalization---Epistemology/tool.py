import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multi-scale Epistemic Renormalized Prime Sieve (MERPS) Implementation.
    
    Mechanism:
    While the theoretical framework invokes Prime Number Theory and Renormalization Group (RG) flows,
    the causal analysis restricts direct number-theoretic scoring to avoid historical failure modes.
    Instead, this implementation uses:
    1. Structural Parsing (Primary): Extracts negations, comparatives, and conditionals to build a
       logical constraint graph. This acts as the "epistemic justification" layer.
    2. Numeric Evaluation: Directly evaluates mathematical expressions found in candidates.
    3. RG-Coarse Graining (Analogy): The text is analyzed at multiple scales (char, word, sentence).
       Discrepancies between scales (e.g., positive words but negative structure) reduce the score,
       simulating an RG flow towards a fixed point of consistency.
    4. NCD (Tiebreaker): Used only when structural signals are ambiguous.
    """

    def __init__(self):
        self.negation_words = {"no", "not", "never", "none", "neither", "n't", "false", "incorrect"}
        self.comparatives = {"greater", "larger", "more", "less", "smaller", "fewer", ">", "<", "eq", "equal"}
        self.conditionals = {"if", "then", "unless", "provided", "when", "only"}
        self.bool_yes = {"yes", "true", "correct", "right", "1"}
        self.bool_no = {"no", "false", "incorrect", "wrong", "0"}

    def _structural_parse(self, text: str) -> Dict[str, float]:
        """Extract logical features: negations, comparatives, conditionals."""
        lower = text.lower()
        words = re.findall(r'\b\w+\b', lower)
        word_set = set(words)
        
        neg_count = sum(1 for w in words if w in self.negation_words or w.endswith("n't"))
        comp_count = sum(1 for w in words if w in self.comparatives)
        cond_count = sum(1 for w in words if w in self.conditionals)
        
        # Detect explicit boolean assertions
        is_yes = any(w in word_set for w in self.bool_yes)
        is_no = any(w in word_set for w in self.bool_no)
        
        return {
            "negations": neg_count,
            "comparatives": comp_count,
            "conditionals": cond_count,
            "is_yes": is_yes,
            "is_no": is_no,
            "length": len(text)
        }

    def _numeric_eval(self, text: str) -> float:
        """Attempt to extract and evaluate simple numeric comparisons."""
        # Pattern for "A < B" or "A > B" or "A == B"
        match = re.search(r'(-?\d+\.?\d*)\s*(<|>|==|=|<=|>=)\s*(-?\d+\.?\d*)', text.replace(" ", ""))
        if match:
            try:
                a = float(match.group(1))
                op = match.group(2)
                b = float(match.group(3))
                if op == '<': return 1.0 if a < b else 0.0
                if op == '>': return 1.0 if a > b else 0.0
                if op == '==' or op == '=': return 1.0 if a == b else 0.0
                if op == '<=': return 1.0 if a <= b else 0.0
                if op == '>=': return 1.0 if a >= b else 0.0
            except: pass
        return None

    def _rg_coarse_grain(self, text: str) -> float:
        """
        Simulate RG flow by checking consistency across scales.
        Scale 1: Char level entropy (noise)
        Scale 2: Word level logic
        Scale 3: Global assertion
        Inconsistencies reduce the score.
        """
        if not text.strip(): return 0.0
        
        # Global sentiment proxy (simplified)
        has_yes = any(w in text.lower() for w in self.bool_yes)
        has_no = any(w in text.lower() for w in self.bool_no)
        
        # If both yes and no present, high uncertainty (low score)
        if has_yes and has_no:
            return 0.5
        
        # If neither, moderate uncertainty
        if not has_yes and not has_no:
            return 0.6
            
        return 1.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_struct = self._structural_parse(prompt)
        prompt_numeric = self._numeric_eval(prompt)
        
        # Determine expected logic from prompt
        expects_negation = prompt_struct["negations"] > 0
        expects_comparison = prompt_struct["comparatives"] > 0 or prompt_numeric is not None
        
        for cand in candidates:
            score = 0.5  # Base prior
            reasoning_parts = []
            
            cand_struct = self._structural_parse(cand)
            cand_numeric = self._numeric_eval(cand)
            rg_factor = self._rg_coarse_grain(cand)
            
            # 1. Numeric Consistency (High Priority)
            if prompt_numeric is not None and cand_numeric is not None:
                # If both have math, check if candidate answers the prompt's math correctly?
                # Hard to infer intent without LLM, so we score based on internal validity
                if cand_numeric == 1.0:
                    score += 0.4
                    reasoning_parts.append("Valid numeric assertion")
                else:
                    score -= 0.4
                    reasoning_parts.append("Invalid numeric assertion")
            elif expects_comparison and cand_numeric is not None:
                 score += 0.2 * cand_numeric
                 reasoning_parts.append("Numeric response to comparison")

            # 2. Logical Consistency (Negation/Conditionals)
            if expects_negation:
                if cand_struct["negations"] > 0:
                    score += 0.3
                    reasoning_parts.append("Matches negation context")
                else:
                    # Potential mismatch, but not fatal
                    score -= 0.1
            else:
                # If prompt is positive, negative answer might be wrong (heuristic)
                if cand_struct["negations"] > 0 and cand_struct["is_no"]:
                     score -= 0.1

            # 3. RG Consistency (Self-consistency check)
            score *= rg_factor
            if rg_factor < 1.0:
                reasoning_parts.append("Scale inconsistency detected")
            
            # 4. Direct Boolean Match (Simple cases)
            if prompt_struct["is_yes"] and cand_struct["is_yes"]:
                score += 0.2
                reasoning_parts.append("Affirmative alignment")
            elif prompt_struct["is_no"] and cand_struct["is_no"]:
                score += 0.2
                reasoning_parts.append("Negative alignment")

            # Clamp score
            score = max(0.0, min(1.0, score))
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Structural baseline"
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Tie-breaking with NCD if scores are very close (within 0.01)
        final_results = []
        for i, res in enumerate(results):
            if i > 0 and abs(res["score"] - results[i-1]["score"]) < 0.01:
                # Use NCD against prompt as tiebreaker (lower distance = better match usually)
                prev_ncd = self._ncd(prompt, results[i-1]["candidate"])
                curr_ncd = self._ncd(prompt, res["candidate"])
                if curr_ncd < prev_ncd:
                    # Swap logic handled by sort stability if we adjusted score slightly
                    # But since we are iterating, we just note it or adjust score minutely
                    res["score"] -= 0.001 # Penalty for higher NCD (worse match)
            
            final_results.append(res)
            
        # Re-sort after tie-break adjustments
        final_results.sort(key=lambda x: x["score"], reverse=True)
        
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural coherence and numeric validity as proxies for confidence.
        """
        struct = self._structural_parse(answer)
        numeric = self._numeric_eval(answer)
        rg = self._rg_coarse_grain(answer)
        
        conf = 0.5
        
        # High confidence if numeric is valid and explicit
        if numeric is not None:
            conf = 0.9 if numeric in [0.0, 1.0] else 0.2
            return min(1.0, conf)
        
        # Confidence based on clarity (no internal contradiction)
        if struct["is_yes"] and struct["is_no"]:
            return 0.1 # Contradictory
        if struct["is_yes"] or struct["is_no"]:
            conf = 0.8
        elif struct["length"] < 5:
            conf = 0.3 # Too short to be confident
        else:
            conf = 0.6
            
        # Apply RG consistency factor
        conf *= rg
        
        return max(0.0, min(1.0, conf))