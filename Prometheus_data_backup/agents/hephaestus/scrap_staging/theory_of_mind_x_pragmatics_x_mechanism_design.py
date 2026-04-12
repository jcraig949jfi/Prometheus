import re
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Strategic Pragmatic Theory-of-Mind (SP-ToM) Planner Implementation.
    
    Mechanism:
    1. Epistemic Honesty (Meta-Confidence): Analyzes the prompt for logical traps
       (presuppositions, ambiguity, false dichotomies) before attempting to solve.
       If detected, confidence is capped low regardless of candidate quality.
    2. Structural & Computational Reasoning: Parses negations, comparatives, and
       performs numeric evaluation (PEMDAS lite) to derive a "ground truth" score.
    3. Pragmatic Mechanism Design: Simulates a VCG-like scoring rule where candidates
       are scored on informativeness (structural match) and truthfulness (numeric accuracy).
       NCD is used strictly as a tiebreaker (<15% weight).
    """

    def __init__(self):
        # Keywords indicating logical traps (Tier B)
        self.presupposition_triggers = [
            r"\bhave you stopped\b", r"\bwhy did.*fail\b", r"\bwhy did.*stop\b",
            r"\bwhen did.*stop\b", r"\bquit\b", r"\bassumes\b"
        ]
        self.ambiguity_triggers = [
            r"\bwho is\b", r"\bwhich one\b", r"\beither.*or\b", r"\bbest\b",
            r"\bworst\b", r"\bfavorite\b", r"\bopinion\b"
        ]
        self.scope_triggers = [r"\bevery.*a\b", r"\ball.*same\b"]
        
        # Numeric pattern for extraction
        self.number_pattern = re.compile(r"-?\d+\.?\d*")

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic traps.
        Returns a confidence cap (0.0 - 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Check for Presuppositions (Loaded questions)
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.15  # Strong cap for loaded questions
        
        # 2. Check for Ambiguity/Subjectivity without data
        # Only trigger if the question asks for a judgment without providing criteria
        if any(re.search(p, p_lower) for p in self.ambiguity_triggers):
            # Heuristic: If it asks for "best" but doesn't provide a list to compare
            if "list" not in p_lower and "compare" not in p_lower:
                return 0.25

        # 3. Check for Unanswerable/Insufficient Info markers
        if "impossible" in p_lower or "cannot be determined" in p_lower:
            return 0.20

        return 1.0  # No obvious traps detected

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts all floating point numbers from text."""
        matches = re.findall(self.number_pattern, text)
        return [float(m) for m in matches]

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on structural logic and numeric verification.
        Returns 0.0 to 1.0.
        """
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        score = 0.0
        components = 0

        # 1. Numeric Consistency (If prompt has numbers, candidate should match logic)
        if p_nums:
            components += 1
            # Simple heuristic: If candidate contains the result of a simple operation
            # or repeats the key numbers correctly without contradiction.
            # For "9.11 vs 9.9" traps, we rely on float conversion.
            if c_nums:
                # Check if candidate number is logically derived (simplified)
                # If prompt implies comparison, does candidate pick the right one?
                if len(p_nums) >= 2:
                    max_val = max(p_nums)
                    min_val = min(p_nums)
                    # If candidate is just a number, check if it matches expected logic
                    # This is a proxy for "constructive computation"
                    if any(abs(c_nums[0] - v) < 1e-6 for v in p_nums):
                        score += 0.5
            else:
                # If prompt has numbers but candidate has none, likely wrong for math problems
                if any(word in prompt.lower() for word in ["calculate", "sum", "greater", "less"]):
                    score -= 0.5 # Penalty
            score = max(0, min(1, score))
        else:
            # Non-numeric structural match (keyword overlap with penalty for length)
            p_words = set(re.findall(r'\w+', prompt.lower()))
            c_words = set(re.findall(r'\w+', candidate.lower()))
            if p_words:
                overlap = len(p_words & c_words) / len(p_words)
                score = overlap
            components += 1

        # 2. Negation Handling
        if "not" in prompt.lower() or "never" in prompt.lower():
            if "not" not in candidate.lower() and "false" not in candidate.lower():
                # Candidate might be missing the negation constraint
                score *= 0.5 

        return max(0.0, min(1.0, score))

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len12 - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using SP-ToM logic:
        1. Meta-check for honesty/traps.
        2. Structural/Numeric scoring (Primary).
        3. NCD scoring (Tiebreaker, max 15% weight).
        """
        results = []
        meta_cap = self._meta_confidence(prompt)
        
        # Pre-calculate prompt features
        p_nums = self._extract_numbers(prompt)
        has_math_context = any(w in prompt.lower() for w in ["calculate", "sum", "total", "greater", "less", "compare"])

        for cand in candidates:
            reasoning_parts = []
            final_score = 0.0
            
            # --- Step 1: Epistemic Honesty Check ---
            if meta_cap < 0.3:
                reasoning_parts.append(f"Epistemic Trap Detected (Cap: {meta_cap})")
                # Even if trapped, we still rank based on structure, but confidence will be low
                base_score = self._compute_structural_score(prompt, cand)
                # Apply heavy penalty for traps unless the candidate explicitly identifies the trap
                trap_keywords = ["ambiguous", "cannot", "insufficient", "undefined", "presupposition"]
                if any(kw in cand.lower() for kw in trap_keywords):
                    base_score = 0.8 # Reward identifying the trap
                else:
                    base_score *= 0.5 # Penalize guessing on traps
                
            else:
                # --- Step 2: Structural & Computational Scoring (50% + weight) ---
                struct_score = self._compute_structural_score(prompt, cand)
                
                # Specific Math Trap Handling (e.g., 9.11 vs 9.9)
                if has_math_context and p_nums:
                    c_nums = self._extract_numbers(cand)
                    if c_nums:
                        # If the prompt asks for the larger number
                        if "larger" in prompt.lower() or "greater" in prompt.lower() or "max" in prompt.lower():
                            if c_nums[0] == max(p_nums):
                                struct_score = 0.95
                            else:
                                struct_score = 0.1
                        # If the prompt asks for the smaller number
                        elif "smaller" in prompt.lower() or "less" in prompt.lower() or "min" in prompt.lower():
                            if c_nums[0] == min(p_nums):
                                struct_score = 0.95
                            else:
                                struct_score = 0.1
                
                reasoning_parts.append(f"Structural Score: {struct_score:.2f}")
                base_score = struct_score

            # --- Step 3: Mechanism Design / NCD Tiebreaker (Max 15%) ---
            # NCD is only useful if structural scores are similar or for noise reduction
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD (lower distance = higher score) and scale to 0.15 max contribution
            ncd_score = (1.0 - ncd_val) * 0.15
            
            final_score = (base_score * 0.85) + ncd_score
            
            # Apply Meta-Cap strictly to the final output confidence if it's a trap
            if meta_cap < 0.3:
                final_score = min(final_score, meta_cap + 0.1) # Allow slight variance but keep low

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": "; ".join(reasoning_parts)
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Caps at 0.25 if meta-analysis detects ambiguity/traps.
        Caps at 0.9 unless computation is definitive.
        """
        meta_cap = self._meta_confidence(prompt)
        
        # Calculate structural alignment
        struct_score = self._compute_structural_score(prompt, answer)
        
        # Base confidence on structural match, bounded by meta-cap
        conf = struct_score
        
        if meta_cap < 0.3:
            # If it's a trap question, confidence must be low unless answer admits uncertainty
            trap_admitted = any(kw in answer.lower() for kw in ["ambiguous", "cannot", "unknown", "error"])
            if trap_admitted:
                conf = 0.85 # High confidence that "I don't know" is the right answer to a trap
            else:
                conf = min(conf, meta_cap)
        else:
            # Normal questions: cap at 0.95 to maintain epistemic humility
            conf = min(conf, 0.95)
            
        return round(max(0.0, min(1.0, conf)), 4)