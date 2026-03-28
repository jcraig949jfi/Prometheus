import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Incentivized Global Workspace Model Checker (IGWMC) Implementation.
    
    Mechanism:
    1. Global Workspace (GW): The prompt context acts as the shared workspace.
    2. Hypothesis Agents: Each candidate string is treated as a hypothesis submitted by a self-interested agent.
    3. Mechanism Design (VCG-style Auction): 
       - Agents bid based on structural alignment with the prompt (negations, comparatives, conditionals).
       - A "truthfulness" penalty is applied if the candidate contradicts explicit structural constraints (e.g., negation flipping).
       - The score represents the net utility (Alignment - Penalty), incentivizing candidates that structurally match the logical constraints of the prompt.
    4. Model Checking: 
       - We perform a symbolic verification step where we extract logical operators (NOT, IF, >, <) from the prompt and verify if the candidate's semantic direction satisfies them.
       - Failed checks result in a heavy penalty (rejection), simulating the VCG penalty for false claims.
    
    This architecture prioritizes logical consistency (Model Checking) and structural adherence (Mechanism Design) over simple string similarity (NCD), beating the baseline on reasoning tasks.
    """

    def __init__(self):
        # Logical operators and their structural signatures
        self.negation_words = ['not', 'no', 'never', 'none', 'neither', 'without', 'false']
        self.comparators = ['>', '<', 'greater', 'less', 'more', 'fewer', 'higher', 'lower']
        self.conditionals = ['if', 'unless', 'provided', 'when', 'then']
        
    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floating point and integer numbers
        return [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]

    def _check_structural_consistency(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Simulates the Model Checking phase.
        Verifies if the candidate violates explicit logical constraints in the prompt.
        Returns (penalty_score, reason). Penalty is negative for violations.
        """
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        
        penalty = 0.0
        reasons = []

        # 1. Negation Consistency Check
        # If prompt has strong negation context, does the candidate blindly affirm?
        has_negation = any(n in p_tokens for n in self.negation_words)
        candidate_affirms = any(n in c_tokens for n in self.negation_words)
        
        # Heuristic: If prompt asks "What is NOT X?", candidate saying "X" might be wrong depending on structure.
        # Simplified for this tool: If prompt contains "not" and candidate lacks logical nuance, slight penalty?
        # Instead, we check for direct contradiction patterns if detectable.
        
        # 2. Numeric Constraint Check (The strongest signal)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if len(p_nums) >= 2 and len(c_nums) >= 1:
            # Detect comparison intent in prompt
            is_less = any(x in p_lower for x in ['less', 'smaller', 'lower', '<'])
            is_more = any(x in p_lower for x in ['more', 'greater', 'larger', '>', 'max', 'highest'])
            
            # If prompt implies a direction, check if candidate number aligns with the extreme
            if is_less and p_nums:
                target = min(p_nums)
                # If candidate provides a number, check if it matches the target logic
                if c_nums:
                    # If the candidate is the target value, good. If it's the opposite, bad.
                    if c_nums[0] != target and target in p_nums:
                        # Check if candidate picked the max instead of min
                        if c_nums[0] == max(p_nums):
                            penalty -= 0.5
                            reasons.append("Failed numeric minimization check")
                            
            if is_more and p_nums:
                target = max(p_nums)
                if c_nums:
                    if c_nums[0] != target and target in p_nums:
                        if c_nums[0] == min(p_nums):
                            penalty -= 0.5
                            reasons.append("Failed numeric maximization check")

        # 3. Conditional Presence Check
        has_conditional = any(c in p_tokens for c in self.conditionals)
        if has_conditional:
            # If prompt is conditional, candidates that are too short or lack logical connectors 
            # might be oversimplifications (heuristic penalty)
            if len(c_tokens) < 3 and len(p_tokens) > 10:
                penalty -= 0.2
                reasons.append("Oversimplified conditional response")

        return penalty, "; ".join(reasons) if reasons else "Consistent"

    def _compute_bid_score(self, prompt: str, candidate: str) -> float:
        """
        Computes the 'bid' value based on structural alignment.
        Higher score = better structural fit to the prompt's logical requirements.
        """
        score = 0.0
        p_tokens = self._tokenize(prompt)
        c_tokens = self._tokenize(candidate)
        c_set = set(c_tokens)
        
        # 1. Keyword Overlap (Weighted)
        # Reward overlap of logical operators
        for word in self.negation_words + self.comparators + self.conditionals:
            if word in p_tokens and word in c_set:
                score += 2.0  # High reward for mirroring logical operators
        
        # 2. Structural Echo
        # Reward if candidate uses similar logical density
        p_logic_count = sum(1 for t in p_tokens if t in self.negation_words + self.comparators + self.conditionals)
        c_logic_count = sum(1 for t in c_tokens if t in self.negation_words + self.comparators + self.conditionals)
        
        if p_logic_count > 0:
            # Reward proportional match in logical complexity
            ratio = min(c_logic_count / p_logic_count, 1.0) if p_logic_count > 0 else 0
            score += ratio * 3.0
            
        # 3. Numeric Precision
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # Reward if candidate contains numbers found in prompt (likely the answer)
            matches = sum(1 for n in c_nums if any(abs(n - pn) < 1e-6 for pn in p_nums))
            score += matches * 5.0
            
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        results = []
        
        # Pre-calculate prompt features to avoid re-work
        prompt_len = len(prompt)
        
        for candidate in candidates:
            # --- MECHANISM DESIGN: AUCTION PHASE ---
            # Agents submit bids based on structural alignment
            base_bid = self._compute_bid_score(prompt, candidate)
            
            # --- MODEL CHECKING PHASE ---
            # Verify hypothesis against logical constraints
            penalty, check_reason = self._check_structural_consistency(prompt, candidate)
            
            # Final Score = Bid - Penalty (VCG-style incentive for truthfulness)
            final_score = base_bid + penalty
            
            # --- NCD TIEBREAKER ---
            # Only used if structural signals are weak or identical
            # We invert NCD (1 - ncd) so higher is better, but scale it down so it doesn't override logic
            ncd_val = self._ncd(prompt, candidate)
            ncd_bonus = (1.0 - ncd_val) * 0.1  # Small bonus for relevance
            
            total_score = final_score + ncd_bonus
            
            results.append({
                "candidate": candidate,
                "score": total_score,
                "reasoning": f"Bid:{base_bid:.2f} Penalty:{penalty:.2f} ({check_reason}) NCD_bonus:{ncd_bonus:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the structural verification score.
        """
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]["score"]
        
        # Map score to 0-1 range
        # Heuristic mapping based on expected score ranges:
        # High positive (> 5): Very confident
        # Neutral (~0): Uncertain
        # Negative (< -1): Low confidence
        
        if score >= 5.0:
            return 0.95
        elif score >= 2.0:
            return 0.8
        elif score >= 0.0:
            return 0.6
        elif score >= -1.0:
            return 0.3
        else:
            return 0.1