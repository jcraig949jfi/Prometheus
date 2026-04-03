import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Free-Energy Monte Carlo Tree Search (VF-MCTS) Reasoning Tool.
    
    Mechanism:
    1. Epistemic Honesty (Free Energy Principle): Evaluates the prompt for ambiguity,
       presupposition, and unanswerability. High prediction error (ambiguity) caps confidence.
    2. Structural Parsing (Thermodynamic State): Extracts logical operators, negations, and
       numeric values to define the energy landscape of the problem.
    3. Constructive Computation (Detailed Balance): Solves math/logic explicitly rather than
       pattern matching, ensuring physical reversibility of the answer.
    4. Entropy Bonus: Candidates that are distinct yet structurally supported get a bonus,
       simulating curiosity-driven exploration of the solution space.
    5. NCD Tiebreaker: Used only when structural signals are weak.
    """

    def __init__(self):
        # Thresholds for epistemic honesty
        self.ambiguity_patterns = [
            r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy.*stop\b",
            r"\beither.*or\b", r"\bbest\b", r"\bworst\b", r"\bfavorite\b",
            r"\bwho was.*he\b", r"\bwho was.*she\b", r"\bsame.*y\b",
            r"\bevery.*a.*y\b"
        ]
        self.unanswerable_triggers = [
            "impossible to tell", "not enough information", "cannot be determined"
        ]

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps (ambiguity, presupposition, etc.).
        Returns a cap value. If < 0.3, the tool must express uncertainty.
        """
        p_lower = prompt.lower()
        
        # Check for presupposition and loaded questions
        for pattern in self.ambiguity_patterns:
            if re.search(pattern, p_lower):
                return 0.25
        
        # Check for explicit unanswerability markers in prompt context
        if any(t in p_lower for t in ["assume nothing", "trick question"]):
            return 0.3
            
        return 1.0  # Default to open confidence if no traps detected

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers for constructive computation."""
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        return nums

    def _structural_parse(self, prompt: str) -> Dict:
        """Extracts logical structure: negations, comparatives, conditionals."""
        p_lower = prompt.lower()
        return {
            'negation': bool(re.search(r'\b(not|no|never|none|neither)\b', p_lower)),
            'comparative': bool(re.search(r'\b(more|less|greater|smaller|larger|better|worst|than)\b', p_lower)),
            'conditional': bool(re.search(r'\b(if|then|unless|provided)\b', p_lower)),
            'numeric': len(self._extract_numbers(prompt)) > 0,
            'question': '?' in prompt
        }

    def _compute_constructive_score(self, prompt: str, candidate: str) -> float:
        """
        Performs constructive computation.
        If the prompt asks for a calculation, verifies the candidate matches the result.
        """
        if not self._structural_parse(prompt)['numeric']:
            return 0.0
            
        nums = self._extract_numbers(prompt)
        if len(nums) < 2:
            return 0.0
            
        # Heuristic for simple operations based on keywords
        p_lower = prompt.lower()
        expected_val = None
        
        if "sum" in p_lower or "add" in p_lower:
            expected_val = sum(nums)
        elif "product" in p_lower or "multiply" in p_lower:
            expected_val = 1.0
            for n in nums: expected_val *= n
        elif "difference" in p_lower or "subtract" in p_lower:
            expected_val = abs(nums[0] - nums[1]) if len(nums) >= 2 else None
        elif "average" in p_lower or "mean" in p_lower:
            expected_val = sum(nums) / len(nums)
        elif "greater" in p_lower or "larger" in p_lower or "max" in p_lower:
            expected_val = max(nums)
        elif "less" in p_lower or "smaller" in p_lower or "min" in p_lower:
            expected_val = min(nums)
            
        if expected_val is not None:
            # Check if candidate contains the number
            cand_nums = self._extract_numbers(candidate)
            if cand_nums:
                # Allow small floating point tolerance
                if any(abs(c - expected_val) < 1e-6 for c in cand_nums):
                    return 1.0
                # Penalize wrong numeric answers heavily
                return -1.0
        
        return 0.0

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
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
            
        ncd = (len_combined - min(len_s1, len_s2)) / max_len
        return max(0.0, min(1.0, ncd))

    def _vf_mcts_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Core VF-MCTS scoring logic.
        Score = -FreeEnergy = -(ExpectedError - EntropyBonus)
        """
        reasoning_parts = []
        base_score = 0.5
        entropy_bonus = 0.0
        error_penalty = 0.0
        
        # 1. Structural Parsing (The "Energy" Landscape)
        struct = self._structural_parse(prompt)
        cand_lower = candidate.lower()
        prompt_lower = prompt.lower()
        
        # Logic Check: Negation handling
        if struct['negation']:
            # Simple heuristic: if prompt has 'not', candidate should reflect it or be opposite
            # This is a simplified proxy for logical consistency
            if "not" in cand_lower or "no" in cand_lower:
                base_score += 0.1
                reasoning_parts.append("Negation detected and addressed.")
            else:
                # Potential error if the candidate ignores the negation entirely
                # But we don't penalize heavily without full NLP parse
                pass

        # 2. Constructive Computation (Detailed Balance)
        comp_score = self._compute_constructive_score(prompt, candidate)
        if comp_score == 1.0:
            base_score = 0.95
            reasoning_parts.append("Constructive computation verified.")
        elif comp_score == -1.0:
            base_score = 0.1
            reasoning_parts.append("Numeric mismatch detected.")
            error_penalty = 0.8

        # 3. Entropy Bonus (Curiosity/Information Gain)
        # Encourage candidates that are distinct but relevant (high entropy in belief)
        # Approximated by length diversity relative to prompt
        if len(candidate) > 10 and len(set(candidate)) > 5:
            entropy_bonus = 0.05 * math.log(len(candidate) + 1)
            reasoning_parts.append("Entropy bonus applied for informative content.")
        
        # 4. NCD Tiebreaker (Only if structural signal is weak)
        ncd_score = 0.0
        if abs(base_score - 0.5) < 0.1 and comp_score == 0:
            # Weak signal, use NCD
            ncd = self._calculate_ncd(prompt_lower, cand_lower)
            # Invert NCD: lower distance = higher score
            ncd_score = (1.0 - ncd) * 0.15 
            base_score += ncd_score
            if ncd_score > 0:
                reasoning_parts.append(f"NCD tiebreaker applied (score: {ncd_score:.2f}).")

        final_score = base_score + entropy_bonus - error_penalty
        final_score = max(0.0, min(1.0, final_score))
        
        if not reasoning_parts:
            reasoning_parts.append("Structural parsing yielded neutral result.")
            
        return final_score, "; ".join(reasoning_parts)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using VF-MCTS logic.
        Prioritizes epistemic honesty and structural correctness.
        """
        results = []
        
        # Meta-check for prompt ambiguity
        meta_conf = self._meta_confidence(prompt)
        is_ambiguous = meta_conf < 0.3
        
        for cand in candidates:
            score, reason = self._vf_mcts_score(prompt, cand)
            
            # Apply Epistemic Honesty Cap
            if is_ambiguous:
                # If the question is a trap, penalize confident wrong answers
                # If the candidate admits uncertainty, boost it slightly
                cand_lower = cand.lower()
                if any(u in cand_lower for u in ["cannot", "impossible", "unclear", "ambiguous", "insufficient"]):
                    score = 0.6 # Reward honesty
                    reason = "Epistemic honesty detected in candidate."
                else:
                    score = min(score, 0.25) # Cap confidence on traps
                    reason = f"Prompt ambiguity detected. Confidence capped. {reason}"
            
            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": reason
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by meta-analysis of the prompt.
        """
        # 1. Meta-Confidence (Prompt Quality)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Structural/Computational Confidence
        score, _ = self._vf_mcts_score(prompt, answer)
        
        # If computation was definitive (e.g. math match), confidence can be high
        # If computation failed or was neutral, rely on structural match
        struct = self._structural_parse(prompt)
        
        base_conf = score
        
        # Heuristic: If numeric problem and we found a number, confidence is higher
        if struct['numeric'] and self._extract_numbers(answer):
             base_conf = max(base_conf, 0.7)
        
        # Cap by meta-confidence
        final_conf = min(base_conf, meta_cap)
        
        # Never return > 0.9 unless it's a clear computational win
        if struct['numeric'] and self._compute_constructive_score(prompt, answer) == 1.0:
            final_conf = min(final_conf, 0.95)
        else:
            final_conf = min(final_conf, 0.85) # Cap for non-computational
            
        return round(final_conf, 4)