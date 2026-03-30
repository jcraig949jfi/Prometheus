import re
import zlib
import math
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Differentiable Ecosystem-augmented MCTS (DE-MCTS) Reasoning Tool.
    
    Mechanism:
    This tool simulates the theoretical DE-MCTS framework by combining:
    1. Structural Parsing (The "Tree Selection"): Rigorously extracts logical 
       constraints (negations, comparatives, conditionals) to filter candidates.
    2. Constructive Computation (The "Differentiable Rollout"): Executes numeric 
       and logical operations to derive ground-truth answers where possible.
    3. Epistemic Honesty (The "Meta-Constraint"): Before scoring, it analyzes the 
       prompt for ambiguity, presupposition, or unanswerability (Tier B traps). 
       If detected, confidence is capped low (<0.3) regardless of candidate quality.
    4. NCD Tiebreaker: Used only when structural and computational signals are weak.
    
    The "Ecosystem" analogy is applied to the candidate evaluation: candidates 
    compete for "biomass" (score) based on how well they satisfy the logical 
    "environmental constraints" of the prompt.
    """

    def __init__(self):
        # Patterns for structural parsing
        self.negation_patterns = [r'\bnot\b', r'\bnever\b', r'\bno\b', r'\bwithout\b', r'\bunless\b']
        self.comparative_patterns = [r'(more|less|greater|smaller|higher|lower)\s+than', r'[<>=]']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\belse\b', r'\bunless\b']
        
        # Patterns for Tier B (Epistemic Honesty) traps
        self.presupposition_triggers = [
            r'have you stopped', r'have you quit', r'why did.*fail', r'why did.*stop',
            r'when did.*stop', r'is it true that.*failed'
        ]
        self.scope_ambiguity_triggers = [r'every.*a.*same', r'all.*same']
        self.pronoun_triggers = [r'(he|she|him|her|they)\s+was', r'told.*he', r'told.*she']
        self.false_dichotomy_triggers = [r'either.*or', r'must choose between']
        self.subjectivity_triggers = [r'best', r'worst', r'favorite', r'beautiful', r'ugly']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for Tier B traps (Ambiguity, Presupposition, Unanswerability).
        Returns a confidence cap. If traps are found, returns < 0.3.
        """
        p_lower = prompt.lower()
        
        # 1. Check for Presupposition traps
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.2  # Strong cap for loaded questions

        # 2. Check for Subjectivity (Unanswerable without criteria)
        # Only flag if it looks like an opinion question, not a defined optimization
        if re.search(r'\b(is|who|what)\s+.*\s+(best|worst|favorite)', p_lower):
            # Allow if it's a math max/min problem context, but strict for now
            if not re.search(r'\d', prompt): # If no numbers, likely subjective
                return 0.25

        # 3. Check for False Dichotomy
        if re.search(r'either.*or', p_lower) and not re.search(r'logic|math|code', p_lower):
             # Heuristic: if it's not a formal logic puzzle, assume potential fallacy
            if len(prompt.split()) < 50: 
                return 0.3

        # 4. Check for Pronoun Ambiguity in "Who" questions
        if re.search(r'who\s+(is|was|did)', p_lower):
            if re.search(r'(he|she|him|her)', p_lower) and re.search(r'told|said|gave', p_lower):
                return 0.25

        return 1.0  # No obvious traps detected

    def _extract_numbers(self, text: str) -> List[float]:
        """Extracts floating point numbers from text for constructive computation."""
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Scores based on structural alignment (Negations, Comparatives, Conditionals).
        Returns a score between 0.0 and 1.0.
        """
        p_lower = self._normalize(prompt)
        c_lower = self._normalize(candidate)
        score = 0.5  # Base score
        
        # Negation Check: If prompt has 'not', candidate should reflect negation or absence
        has_negation = any(re.search(p, p_lower) for p in self.negation_patterns)
        cand_has_negation = any(re.search(p, c_lower) for p in self.negation_patterns)
        
        if has_negation:
            if cand_has_negation:
                score += 0.3
            else:
                # Penalty if prompt denies something and candidate affirms it blindly
                # Simple heuristic: if prompt says "X is not Y", candidate "X is Y" is bad
                score -= 0.4
        
        # Comparative Check
        if any(re.search(p, p_lower) for p in self.comparative_patterns):
            # Candidate should ideally contain comparative words or numbers
            if any(re.search(p, c_lower) for p in self.comparative_patterns) or self._extract_numbers(candidate):
                score += 0.2
        
        return max(0.0, min(1.0, score))

    def _constructive_compute(self, prompt: str, candidate: str) -> Optional[float]:
        """
        Attempts to solve the problem computationally.
        Returns a definitive score (1.0 for correct, 0.0 for wrong) if solvable,
        or None if the problem is not computationally tractable via simple parsing.
        """
        p_lower = self._normalize(prompt)
        c_lower = self._normalize(candidate)
        
        # Extract numbers from prompt and candidate
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        # Case 1: Direct Numeric Comparison (e.g., "Is 9.11 > 9.9?")
        if len(p_nums) >= 2 and len(c_nums) == 0:
            # Check for yes/no candidates
            if c_lower in ['yes', 'true', '1']:
                # Determine truth
                if '>' in prompt or 'greater' in p_lower:
                    return 1.0 if p_nums[0] > p_nums[1] else 0.0
                elif '<' in prompt or 'less' in p_lower:
                    return 1.0 if p_nums[0] < p_nums[1] else 0.0
            elif c_lower in ['no', 'false', '0']:
                if '>' in prompt or 'greater' in p_lower:
                    return 1.0 if p_nums[0] <= p_nums[1] else 0.0
                elif '<' in prompt or 'less' in p_lower:
                    return 1.0 if p_nums[0] >= p_nums[1] else 0.0
                    
        # Case 2: Candidate contains the result of a simple operation found in prompt
        # e.g., Prompt: "What is 2 + 2?", Candidate: "4"
        if len(p_nums) >= 2 and len(c_nums) == 1:
            if '+' in prompt and abs(c_nums[0] - (p_nums[0] + p_nums[1])) < 1e-6:
                return 1.0
            if '-' in prompt and abs(c_nums[0] - (p_nums[0] - p_nums[1])) < 1e-6:
                return 1.0
            if '*' in prompt or 'times' in p_lower and abs(c_nums[0] - (p_nums[0] * p_nums[1])) < 1e-6:
                return 1.0
                
        return None

    def _ncd_score(self, prompt: str, candidate: str) -> float:
        """Calculates Normalized Compression Distance (tiebreaker only)."""
        def zlib_len(s):
            return len(zlib.compress(s.encode()))
        
        p_enc = zlib_len(prompt)
        c_enc = zlib_len(candidate)
        pc_enc = zlib_len(prompt + " " + candidate)
        
        if max(p_enc, c_enc) == 0:
            return 0.5
        
        ncd = (pc_enc - min(p_enc, c_enc)) / max(p_enc, c_enc)
        # Invert so higher is better (similarity), though for reasoning, 
        # we usually want specific alignment, not just similarity.
        # Here we use it as a weak tiebreaker for relevance.
        return 1.0 - min(1.0, ncd)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Tier B: Epistemic Honesty Check
        meta_cap = self._meta_confidence(prompt)
        
        for candidate in candidates:
            reasoning_parts = []
            final_score = 0.0
            
            # 1. Constructive Computation (Highest Priority if applicable)
            comp_score = self._constructive_compute(prompt, candidate)
            if comp_score is not None:
                # If we can compute the answer, this dominates the score
                final_score = comp_score
                reasoning_parts.append(f"Computed verification: {'Match' if comp_score > 0.5 else 'Mismatch'}")
            else:
                # 2. Structural Parsing (Primary Signal for non-computable)
                struct_score = self._structural_score(prompt, candidate)
                
                # 3. NCD (Tiebreaker, max 15% weight effectively)
                ncd = self._ncd_score(prompt, candidate)
                
                # Weighted combination: Structural (85%) + NCD (15%)
                # But scaled by meta_cap
                base_score = (struct_score * 0.85) + (ncd * 0.15)
                final_score = base_score * meta_cap
                
                if comp_score is None:
                    reasoning_parts.append(f"Structural alignment: {struct_score:.2f}")
                    if meta_cap < 0.3:
                        reasoning_parts.append("Flagged as ambiguous/unanswerable (Tier B)")

            # Apply Meta Cap explicitly if not already handled by multiplication logic above
            if meta_cap < 0.3:
                final_score = min(final_score, 0.29) # Ensure cap is respected
            
            results.append({
                "candidate": candidate,
                "score": round(final_score, 4),
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Evaluated via DE-MCTS simulation"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1. 
        Caps at 0.25 if Tier B traps are detected.
        Caps at 0.9 unless computation produced a definitive answer.
        """
        # 1. Meta Confidence (Trap Detection)
        meta_cap = self._meta_confidence(prompt)
        
        # 2. Constructive Verification
        comp_result = self._constructive_compute(prompt, answer)
        
        if comp_result is not None:
            # Definitive computation result
            if comp_result == 1.0:
                return min(1.0, meta_cap) # Can be 1.0 if no traps
            else:
                return 0.0 # Definitely wrong computationally
        
        # 3. Structural Heuristic Confidence
        # If we can't compute, we rely on structural fit, but cap confidence
        struct_score = self._structural_score(prompt, answer)
        
        # Base confidence on structural strength, but heavily penalized by ambiguity
        raw_conf = struct_score * 0.8 
        
        # Apply meta cap
        final_conf = min(raw_conf, meta_cap)
        
        # Never return > 0.9 without computation
        if final_conf > 0.9:
            final_conf = 0.9
            
        return round(final_conf, 4)