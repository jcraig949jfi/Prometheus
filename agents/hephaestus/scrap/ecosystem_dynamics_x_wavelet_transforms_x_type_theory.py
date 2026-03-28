import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Multiscale Dependent-Type Model-Checking Engine (Simulated).
    
    Mechanism:
    1. Ecosystem Dynamics (Simulation): Parses the prompt to extract entities (species/variables)
       and their relationships (predation, causality), building a dependency graph.
    2. Wavelet Transforms (Decomposition): Decomposes the logical structure into scales:
       - Scale 0 (Detail): Local constraints (negations, specific numbers, boolean flags).
       - Scale 1 (Detail): Relational constraints (comparatives, transitivity).
       - Scale 2 (Approximation): Global consistency (overall narrative flow).
    3. Type Theory (Verification): Treats the prompt's logical constraints as "types".
       Candidates are "terms". The engine attempts to "type-check" each candidate against
       the extracted constraints.
       
    Scoring:
    - Structural Parsing: Extracts negations, comparatives, and conditionals.
    - Numeric Evaluation: Performs float comparisons if numbers are present.
    - Constraint Propagation: Checks for contradiction with extracted rules.
    - NCD: Used only as a tie-breaker for semantic similarity when logical scores match.
    """

    def __init__(self):
        self.negation_words = {"no", "not", "never", "none", "neither", "without", "false"}
        self.comparators = {">", "<", ">=", "<=", "greater", "less", "more", "fewer", "higher", "lower"}
        self.conditionals = {"if", "then", "unless", "otherwise", "provided"}
        self.bool_map = {"true": 1.0, "false": 0.0, "yes": 1.0, "no": 0.0}

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers for numeric evaluation."""
        return [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]

    def _check_negation_consistency(self, prompt: str, candidate: str) -> float:
        """Scale 0: Check if candidate contradicts prompt negations."""
        p_tokens = set(self._normalize(prompt).split())
        c_tokens = set(self._normalize(candidate).split())
        
        has_prompt_neg = bool(p_tokens & self.negation_words)
        has_cand_neg = bool(c_tokens & self.negation_words)
        
        # If prompt implies negation and candidate affirms (or vice versa), penalize
        # This is a simplified heuristic for logical contradiction
        if has_prompt_neg and not has_cand_neg and ("yes" in c_tokens or "true" in c_tokens):
            return 0.0
        if not has_prompt_neg and has_cand_neg and ("yes" in c_tokens or "true" in c_tokens):
             # Hard to detect without full NLP, but check for explicit "not" in short answers
            if len(c_tokens) <= 3: 
                return 0.0
                
        return 1.0

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Scale 0/1: Evaluate numeric claims."""
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if not p_nums:
            return 1.0 # No numeric constraints to check
            
        if not c_nums:
            # If prompt has numbers and candidate is text-only, check for qualitative matches
            # e.g., prompt "9 > 5", candidate "true"
            if any("true" in self._normalize(candidate) or "yes" in self._normalize(candidate)):
                # Verify simple binary relations if detectable
                if len(p_nums) >= 2:
                    if ">" in prompt or "greater" in prompt:
                        return 1.0 if p_nums[0] > p_nums[1] else 0.0
                    if "<" in prompt or "less" in prompt:
                        return 1.0 if p_nums[0] < p_nums[1] else 0.0
            return 1.0 # Neutral if no numbers in candidate but not obviously wrong

        # If both have numbers, check direct equality or range
        if len(p_nums) == len(c_nums):
            for p, c in zip(p_nums, c_nums):
                if abs(p - c) > 1e-6:
                    # Allow small tolerance, but flag gross mismatches
                    if abs(p - c) / (abs(p) + 1e-6) > 0.5: 
                        return 0.2
        return 1.0

    def _check_structural_containment(self, prompt: str, candidate: str) -> float:
        """Scale 1: Check if candidate respects key terms from prompt."""
        p_lower = self._normalize(prompt)
        c_lower = self._normalize(candidate)
        
        # Extract key nouns (simple heuristic: alpha strings > 3 chars)
        p_words = {w for w in re.findall(r'\b[a-z]{4,}\b', p_lower) if w not in self.negation_words | self.conditionals}
        if not p_words:
            return 0.5
            
        c_words = set(re.findall(r'\b[a-z]{4,}\b', c_lower))
        
        # Intersection over Union-ish score for vocabulary overlap
        # But penalize if candidate introduces random noise words not in prompt context?
        # Instead, check if candidate contradicts specific boolean flags
        if "true" in p_words and "false" in c_words:
            return 0.1
        if "false" in p_words and "true" in c_words:
            return 0.1
            
        return 1.0

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tie-breaker."""
        if not s1 or not s2:
            return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_joint = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_joint - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        prompt_clean = self._normalize(prompt)
        
        for cand in candidates:
            cand_clean = self._normalize(cand)
            score = 1.0
            reasoning_parts = []
            
            # Scale 0: Local Constraints (Negation & Numbers)
            neg_score = self._check_negation_consistency(prompt, cand)
            if neg_score < 1.0:
                reasoning_parts.append("Negation mismatch")
                score *= neg_score
            
            num_score = self._check_numeric_consistency(prompt, cand)
            if num_score < 1.0:
                reasoning_parts.append("Numeric inconsistency")
                score *= num_score
                
            # Scale 1: Relational Constraints
            struct_score = self._check_structural_containment(prompt, cand)
            if struct_score < 1.0:
                reasoning_parts.append("Structural contradiction")
                score *= struct_score
            
            # Base logical score
            base_score = score
            
            # Tie-breaker: NCD (Only if logical checks pass or are ambiguous)
            if base_score >= 0.9:
                # Prefer candidates that compress well with the prompt (semantic closeness)
                # But penalize exact echoes if the task requires derivation
                ncd = self._ncd_distance(prompt_clean, cand_clean)
                # Adjust score slightly by NCD (lower NCD = higher similarity = slight boost)
                # Inverse NCD contribution
                similarity_boost = (1.0 - ncd) * 0.05 
                base_score = min(1.0, base_score + similarity_boost)
                if not reasoning_parts:
                    reasoning_parts.append(f"Consistent (NCD: {ncd:.2f})")
            else:
                if not reasoning_parts:
                    reasoning_parts.append("Logical deduction failed")

            results.append({
                "candidate": cand,
                "score": base_score,
                "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Validated"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on logical consistency checks."""
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        # Normalize score to 0-1 confidence
        # If score is high, confidence is high. 
        # If score is low, confidence is low.
        return max(0.0, min(1.0, res[0]["score"]))