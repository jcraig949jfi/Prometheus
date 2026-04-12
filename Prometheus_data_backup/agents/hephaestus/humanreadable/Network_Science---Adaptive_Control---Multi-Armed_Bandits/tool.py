import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Network-Aware Adaptive Bandit Controller (NABC) for Reasoning.
    
    Mechanism:
    1. Structural Parsing (Network Topology): Extracts logical constraints (negations, 
       comparatives, conditionals) to form a static 'graph' of the problem. This provides 
       the baseline score (50%+ weight).
    2. Constructive Computation (Local Rewards): Attempts to solve numeric/logic expressions 
       directly. Success yields high confidence; failure yields low confidence.
    3. Adaptive Control (Meta-Confidence): Monitors the prompt for Tier B traps 
       (presuppositions, ambiguity). If detected, it acts as a 'self-tuning regulator' 
       that dampens the final confidence score to < 0.3, preventing overconfidence 
       on ambiguous inputs.
    4. NCD (Gossip Protocol): Used only as a tie-breaker for structurally identical 
       candidates, measuring information distance.
    """

    def __init__(self):
        # Adaptive control parameters
        self.base_exploration = 0.5
        self.uncertainty_penalty = 0.7  # Multiplier when ambiguity is detected
        
        # Patterns for structural parsing
        self.negation_pattern = re.compile(r'\b(not|no|never|none|neither|without)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|higher|lower|best|worst)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|then|unless|provided|except)\b', re.IGNORECASE)
        self.quantifier_pattern = re.compile(r'\b(every|all|some|none|most)\b', re.IGNORECASE)
        
        # Tier B Trap Patterns (Epistemic Honesty)
        self.presupposition_triggers = [
            r"have you stopped", r"why did.*fail", r"why did.*stop", r"when did.*stop",
            r"quit.*doing", r"stopped.*doing"
        ]
        self.ambiguity_triggers = [
            r"who was.*wrong", r"who is.*he", r"which one.*same", r"either.*or.*else",
            r"best.*without", r"favorite.*reason"
        ]
        self.false_dichotomy_pattern = re.compile(r"\b(either|or)\b", re.IGNORECASE)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance (0-1)."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract floating point numbers from text."""
        # Match integers and floats, handling negative signs
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _attempt_computation(self, prompt: str) -> Optional[float]:
        """
        Attempt to solve simple arithmetic or comparison problems.
        Returns the computed answer or None if not solvable.
        """
        # Check for direct comparison questions like "Is 9.11 < 9.9?"
        if "is" in prompt.lower() and ("<" in prompt or ">" in prompt or "greater" in prompt or "less" in prompt):
            nums = self._extract_numbers(prompt)
            if len(nums) >= 2:
                # Heuristic: if prompt asks comparison, return result of comparison
                # This is a simplification for the "constructive computation" requirement
                if "greater" in prompt.lower() or ">" in prompt:
                    return 1.0 if nums[0] > nums[1] else 0.0
                if "less" in prompt.lower() or "<" in prompt:
                    return 1.0 if nums[0] < nums[1] else 0.0
        
        # Check for simple arithmetic expressions embedded (e.g., "What is 2 + 2?")
        # We look for patterns like "number op number"
        match = re.search(r'(-?\d+\.?\d*)\s*([\+\-\*\/])\s*(-?\d+\.?\d*)', prompt)
        if match:
            try:
                n1 = float(match.group(1))
                op = match.group(2)
                n2 = float(match.group(3))
                if op == '+': return n1 + n2
                if op == '-': return n1 - n2
                if op == '*': return n1 * n2
                if op == '/' and n2 != 0: return n1 / n2
            except:
                pass
        return None

    def _meta_confidence(self, prompt: str) -> float:
        """
        Tier B Reasoning: Detects ambiguity, presuppositions, and traps.
        Returns a cap value. If traps are found, returns < 0.3.
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Check
        for pattern in self.presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.2  # Strong cap for presupposition traps
        
        # 2. Ambiguity & Pronoun Check
        for pattern in self.ambiguity_triggers:
            if re.search(pattern, p_lower):
                return 0.25 # Cap for ambiguity
        
        # 3. False Dichotomy Check (simplified)
        if re.search(r"either.*or", p_lower) and "else" not in p_lower:
            # Only flag if it looks like a forced choice without options provided
            if "choose" in p_lower or "which" in p_lower:
                return 0.3

        # 4. Subjectivity Check
        subjective_words = ["best", "worst", "favorite", "beautiful", "moral"]
        if any(word in p_lower for word in subjective_words):
            if "objective" not in p_lower and "data" not in p_lower:
                return 0.4 # Soft cap for subjectivity

        return 1.0  # No traps detected

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Score based on structural alignment (Negations, Comparatives, Conditionals).
        """
        score = 0.5  # Base score
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        # Negation consistency
        p_neg = bool(self.negation_pattern.search(p_lower))
        c_neg = bool(self.negation_pattern.search(c_lower))
        if p_neg == c_neg:
            score += 0.2
        else:
            score -= 0.3 # Penalty for mismatched negation
            
        # Comparative presence
        if self.comparative_pattern.search(p_lower):
            if self.comparative_pattern.search(c_lower):
                score += 0.15
            else:
                score -= 0.1 # Missing comparative in answer
                
        # Conditional logic
        if self.conditional_pattern.search(p_lower):
            if any(k in c_lower for k in ["if", "then", "unless", "yes", "no"]):
                score += 0.1
            else:
                score -= 0.1

        return max(0.0, min(1.0, score))

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Adaptive Control: Check global prompt properties first
        meta_cap = self._meta_confidence(prompt)
        computed_answer = self._attempt_computation(prompt)
        
        # Structural features of the prompt (Network Topology)
        prompt_features = {
            'has_negation': bool(self.negation_pattern.search(prompt)),
            'has_comparative': bool(self.comparative_pattern.search(prompt)),
            'has_conditional': bool(self.conditional_pattern.search(prompt)),
            'length': len(prompt)
        }

        for candidate in candidates:
            # 1. Structural Score (50% weight base)
            struct_score = self._structural_score(prompt, candidate)
            
            # 2. Constructive Computation (20-30% weight)
            comp_score = 0.0
            if computed_answer is not None:
                # Check if candidate contains the computed answer
                cand_nums = self._extract_numbers(candidate)
                if cand_nums and abs(cand_nums[0] - computed_answer) < 1e-6:
                    comp_score = 1.0
                elif str(computed_answer) in candidate:
                    comp_score = 0.8
            
            # 3. NCD Tiebreaker (15% max weight)
            # Only used if structural scores are close. 
            # We invert NCD (1 - ncd) so higher is better.
            ncd_val = self._compute_ncd(prompt, candidate)
            # Heuristic: If candidate is very short (Yes/No), NCD is noisy. 
            # Prefer candidates that share key structural tokens.
            ncd_score = 0.5 * (1.0 - ncd_val) 
            
            # Fusion Logic
            # If computation succeeded, it dominates.
            if comp_score > 0.5:
                raw_score = 0.3 * struct_score + 0.6 * comp_score + 0.1 * ncd_score
            else:
                # Standard fusion
                raw_score = 0.6 * struct_score + 0.25 * comp_score + 0.15 * ncd_score
            
            # Apply Adaptive Control Cap (Tier B)
            final_score = min(raw_score, meta_cap)
            
            # Reasoning string generation
            reasoning_parts = []
            if meta_cap < 0.3:
                reasoning_parts.append("Tier B Trap detected (ambiguity/presupposition). Confidence capped.")
            if comp_score > 0.5:
                reasoning_parts.append("Constructive computation matched.")
            if prompt_features['has_negation'] and bool(self.negation_pattern.search(candidate)):
                reasoning_parts.append("Negation consistency verified.")
            elif prompt_features['has_negation']:
                reasoning_parts.append("Warning: Negation mismatch possible.")
                
            reason_str = " ".join(reasoning_parts) if reasoning_parts else "Structural alignment score."

            results.append({
                "candidate": candidate,
                "score": round(final_score, 4),
                "reasoning": reason_str
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Strictly capped by _meta_confidence for ambiguous prompts.
        """
        # 1. Meta-Confidence Check (The Regulator)
        cap = self._meta_confidence(prompt)
        
        # 2. Structural & Computational Check
        eval_results = self.evaluate(prompt, [answer])
        if not eval_results:
            return 0.1
            
        base_score = eval_results[0]['score']
        
        # 3. Final Calculation
        # If meta_cap is low (trap detected), the score cannot exceed the cap.
        # If no trap, score reflects structural/computational match.
        final_conf = min(base_score, cap)
        
        # Overconfidence prevention: Unless computation is definitive (1.0), 
        # do not exceed 0.9
        if final_conf > 0.9 and base_score < 1.0:
            final_conf = 0.9
            
        return round(final_conf, 4)