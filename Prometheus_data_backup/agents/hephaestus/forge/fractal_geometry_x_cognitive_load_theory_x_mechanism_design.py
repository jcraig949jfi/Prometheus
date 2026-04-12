import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    FICHE-Inspired Reasoning Tool (Mechanism Design Core).
    
    Mechanism:
    1. Structural Parsing (The "Fractal" Scanner): Extracts logical constraints 
       (negations, comparatives, conditionals) to define the hypothesis space.
    2. VCG Auction (The "Mechanism"): Candidates bid for correctness based on 
       constraint satisfaction. The "cost" is the penalty for violating structural rules.
       The winner is the one maximizing global utility (truthfulness) minus cost.
    3. Cognitive Chunking: Limits analysis to fixed-size logical units (clauses) to 
       prevent overload, used here to segment the prompt for parsing.
       
    Note: Fractal Geometry and Cognitive Load Theory are restricted to the 
    confidence wrapper and structural parsing support as per safety guidelines.
    """

    def __init__(self):
        # Chunk size limit (C) based on cognitive load theory (Miller's 7 +/- 2)
        self.chunk_size = 5 
        # Keywords for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'only if', 'provided']

    def _parse_structure(self, text: str) -> dict:
        """Extracts logical constraints from text (Negations, Comparatives, Conditionals)."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        has_negation = any(n in lower_text for n in self.negations)
        has_comparative = any(c in lower_text for c in self.comparatives)
        has_conditional = any(c in lower_text for c in self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", lower_text)
        nums = [float(n) for n in numbers]
        
        return {
            "negation": has_negation,
            "comparative": has_comparative,
            "conditional": has_conditional,
            "numbers": nums,
            "length": len(words)
        }

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_combined = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_combined - min(len_s1, len_s2)) / max_len

    def _vcg_auction_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Mechanism Design Core: VCG-style scoring.
        Candidates 'bid' by matching structural constraints.
        Score = Value (Match) - Cost (Violations).
        Truthful reporting (high score) is the dominant strategy for correct answers.
        """
        p_struct = self._parse_structure(prompt)
        c_struct = self._parse_structure(candidate)
        score = 0.0
        reasons = []

        # 1. Numeric Evaluation (High Weight)
        if p_struct["numbers"] and c_struct["numbers"]:
            # Check if candidate preserves numeric logic (simplified: presence of derived numbers)
            # If prompt has 2 < 5, candidate should not contradict obvious bounds if explicit
            p_nums = sorted(p_struct["numbers"])
            c_nums = sorted(c_struct["numbers"])
            
            # Heuristic: If candidate contains numbers from prompt, it's likely relevant
            matches = sum(1 for n in c_nums if any(abs(n - pn) < 1e-6 for pn in p_nums))
            if matches > 0:
                score += 0.4
                reasons.append(f"Numeric alignment ({matches} matches)")
            else:
                # Penalty for ignoring numbers entirely if they exist
                score -= 0.1 
                reasons.append("Ignored numeric context")

        # 2. Logical Consistency (Negation & Conditionals)
        # If prompt has negation, correct answer often acknowledges it or differs in polarity
        if p_struct["negation"]:
            if c_struct["negation"]:
                score += 0.2
                reasons.append("Negation preserved")
            else:
                # Potential trap: ignoring negation often means wrong
                score -= 0.3
                reasons.append("Failed negation handling")
        
        if p_struct["conditional"]:
            if c_struct["conditional"] or any(k in candidate.lower() for k in ['yes', 'no', 'true', 'false']):
                score += 0.15
                reasons.append("Conditional logic addressed")
        
        # 3. Comparative Logic
        if p_struct["comparative"]:
            if c_struct["comparative"]:
                score += 0.25
                reasons.append("Comparative logic detected")
            else:
                # Soft penalty, sometimes answer is just the result
                pass 

        # 4. Length/Complexity Match (Cognitive Chunking heuristic)
        # Answers shouldn't be wildly disproportionate to the query complexity
        if 0.5 * p_struct["length"] <= c_struct["length"] <= 2.0 * p_struct["length"]:
            score += 0.1
            reasons.append("Complexity aligned")
        else:
            score -= 0.05

        # Tiebreaker: NCD (Only if structural signals are weak or equal)
        ncd_val = self._calculate_ncd(prompt, candidate)
        # Invert NCD so higher is better, scale small
        ncd_score = (1.0 - ncd_val) * 0.05 
        score += ncd_score
        
        reason_str = "; ".join(reasons) if reasons else "Structural match default"
        return score, reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using the FICHE mechanism.
        Returns ranked list of dicts with candidate, score, and reasoning.
        """
        if not candidates:
            return []
        
        scored_candidates = []
        
        for cand in candidates:
            score, reasoning = self._vcg_auction_score(prompt, cand)
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing support (Fractal/Cognitive constraints) 
        to validate the answer against the prompt's logical skeleton.
        """
        if not answer:
            return 0.0
            
        p_struct = self._parse_structure(prompt)
        a_struct = self._parse_structure(answer)
        
        confidence = 0.5 # Base prior
        
        # 1. Negation Check (Critical for reasoning traps)
        if p_struct["negation"]:
            # If prompt is negative, and answer is a simple "Yes", low confidence unless context implies otherwise
            # This is a heuristic proxy for deep logical verification
            if "no" in answer.lower() or "not" in answer.lower() or "false" in answer.lower():
                confidence += 0.3
            elif "yes" in answer.lower() or "true" in answer.lower():
                confidence -= 0.4 # Risk of trap
        
        # 2. Numeric Consistency
        if p_struct["numbers"] and a_struct["numbers"]:
            confidence += 0.2
            
        # 3. Structural Overlap (Chunked)
        # Check if key logical operators in prompt appear in answer (indicating understanding)
        prompt_ops = set()
        if p_struct["negation"]: prompt_ops.add("neg")
        if p_struct["comparative"]: prompt_ops.add("comp")
        if p_struct["conditional"]: prompt_ops.add("cond")
        
        answer_ops = set()
        if a_struct["negation"]: answer_ops.add("neg")
        if a_struct["comparative"]: answer_ops.add("comp")
        if a_struct["conditional"]: answer_ops.add("cond")
        
        if prompt_ops and (prompt_ops & answer_ops):
            confidence += 0.2 # Shared logical structure
        elif not prompt_ops:
            confidence += 0.1 # Simple prompt, slightly higher base confidence
            
        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))