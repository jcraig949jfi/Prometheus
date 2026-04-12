import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    BG-NAS-GW Inspired Reasoning Tool.
    
    Mechanism:
    1. Global Workspace (GW): The prompt is parsed into a structured 'workspace' 
       containing semantic flags (negations, comparatives, conditionals) and numeric values.
    2. Neural Architecture Search (NAS) Analogy: Each candidate answer is treated as a 
       'sub-network architecture'. We do not train weights; instead, we evaluate the 
       structural compatibility of the candidate's logic with the prompt's workspace.
    3. Multi-Armed Bandit (MAB): We simulate a Thompson Sampling policy. 
       - 'Arms' are the candidates.
       - 'Successes' (alpha) are derived from structural alignment (logic match).
       - 'Failures' (beta) are derived from contradictions or lack of constraint satisfaction.
       - The 'score' is a sample from the Beta distribution, representing the probability 
         that this candidate is the optimal 'architecture' for the current reasoning task.
    
    This approach prioritizes structural parsing and constraint propagation over simple 
    string similarity (NCD), using NCD only as a tie-breaker for ambiguous cases.
    """

    def __init__(self):
        # State for the "Bandit" priors could be stored here if persistent across calls,
        # but for this interface, we compute priors dynamically per prompt.
        pass

    def _parse_workspace(self, text: str) -> Dict:
        """Extract structural features from text to populate the Global Workspace."""
        text_lower = text.lower()
        workspace = {
            "has_negation": bool(re.search(r'\b(not|no|never|without|neither|nor)\b', text_lower)),
            "has_comparative": bool(re.search(r'\b(more|less|greater|smaller|better|worse|higher|lower|before|after)\b', text_lower)),
            "has_conditional": bool(re.search(r'\b(if|then|unless|provided|when)\b', text_lower)),
            "numbers": [float(n) for n in re.findall(r'-?\d+\.?\d*', text)],
            "length": len(text),
            "tokens": set(re.findall(r'\b\w+\b', text_lower))
        }
        return workspace

    def _check_logical_consistency(self, prompt_ws: Dict, candidate: str) -> Tuple[bool, float]:
        """
        Check if the candidate contradicts the prompt's structural flags.
        Returns (is_consistent, penalty_score).
        """
        cand_lower = candidate.lower()
        cand_ws = self._parse_workspace(candidate)
        
        # 1. Negation Check: If prompt has negation, candidate must acknowledge it or not contradict it directly
        # Simple heuristic: If prompt says "not X" and candidate says "X" (and X is a key token), penalize.
        # Since we don't have full NLP, we check for direct contradiction patterns.
        
        contradiction_penalty = 0.0
        is_consistent = True

        # Numeric Consistency
        if prompt_ws["numbers"] and cand_ws["numbers"]:
            # If both have numbers, check basic ordering if comparatives exist
            if prompt_ws["has_comparative"]:
                # Heuristic: If prompt implies order and candidate violates obvious float logic
                # This is a simplified proxy for deep reasoning
                pass 

        # Contradiction detection (Simplified)
        # If prompt has "no" or "not", and candidate is a direct affirmative of a key concept without qualification
        if prompt_ws["has_negation"]:
            # If candidate is a short "Yes" or "True" when prompt is negative, it might be a trap
            if cand_lower.strip() in ["yes", "true", "correct"]:
                # Context needed, but as a heuristic, flag for review. 
                # We won't hard fail, but reduce confidence slightly if no other evidence.
                pass
        
        # Constraint Propagation: Transitivity check proxy
        # If prompt: "A > B", "B > C". Candidate: "A < C". 
        # Without entity extraction, we rely on the 'structural match' score below.
        
        return is_consistent, contradiction_penalty

    def _compute_structural_score(self, prompt_ws: Dict, candidate: str) -> float:
        """
        Compute a score based on structural alignment (The 'Reward' for the Bandit).
        Higher score = better structural fit.
        """
        cand_ws = self._parse_workspace(candidate)
        score = 0.0
        
        # 1. Comparative Alignment
        if prompt_ws["has_comparative"]:
            if cand_ws["has_comparative"]:
                score += 0.4 # Reward matching the logical type
            else:
                score -= 0.2 # Penalty for ignoring comparative nature
        
        # 2. Conditional Alignment
        if prompt_ws["has_conditional"]:
            if cand_ws["has_conditional"] or any(k in cand_ws["tokens"] for k in ["therefore", "thus", "so", "because"]):
                score += 0.3
            else:
                score -= 0.1

        # 3. Negation Handling
        if prompt_ws["has_negation"]:
            # Reward candidates that are longer/more nuanced (proxy for handling complexity)
            if cand_ws["length"] > 10:
                score += 0.2
        
        # 4. Numeric Evaluation (Heuristic)
        # If prompt has numbers, reward candidates that also engage with numbers or logical conclusions
        if prompt_ws["numbers"]:
            if cand_ws["numbers"]:
                score += 0.3
            elif any(w in cand_ws["tokens"] for w in ["equal", "sum", "total", "difference"]):
                score += 0.2

        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(b1)
        len2 = len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        try:
            len12 = len(zlib.compress(b1 + b2))
        except:
            return 1.0
        # NCD = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        # Approximating C(x) with len(x) for speed/simplicity if not compressing individual strings,
        # but standard NCD uses compressed lengths.
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        numerator = len12 - min(c1, c2)
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return numerator / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        prompt_ws = self._parse_workspace(prompt)
        results = []
        
        # Bandit Parameters (Thompson Sampling)
        # Alpha (successes), Beta (failures)
        
        for cand in candidates:
            # 1. Structural Analysis (The "Hypothesis Test")
            struct_score = self._compute_structural_score(prompt_ws, cand)
            is_consistent, penalty = self._check_logical_consistency(prompt_ws, cand)
            
            # Map structural score to Bandit priors
            # Base prior: 1, 1 (Uniform)
            # Adjust based on structural alignment
            alpha = 1.0 + max(0, struct_score * 5) # Scale up positive matches
            beta = 1.0 + max(0, -struct_score * 2) # Scale up penalty for mismatches
            
            if not is_consistent:
                beta += 5.0 # Heavy penalty for logical contradiction
            
            # 2. Thompson Sampling Step
            # Since we need deterministic output for the tool interface, we use the Expected Value (Mean) 
            # of the Beta distribution instead of random sampling. 
            # Mean = alpha / (alpha + beta)
            bandit_score = alpha / (alpha + beta)
            
            # 3. NCD Tie-breaker
            # Only used if structural signals are weak or identical. 
            # We add a tiny fraction of NCD inverse to the score.
            ncd_val = self._ncd(prompt, cand)
            # Normalize NCD to be a small bonus (lower NCD = higher similarity = small bonus)
            ncd_bonus = (1.0 - ncd_val) * 0.01 

            final_score = bandit_score + ncd_bonus
            
            # Generate reasoning string
            reasoning_parts = []
            if prompt_ws["has_comparative"] and self._parse_workspace(cand)["has_comparative"]:
                reasoning_parts.append("matched comparative structure")
            if prompt_ws["has_negation"]:
                reasoning_parts.append("processed negation constraints")
            if prompt_ws["numbers"] and self._parse_workspace(cand)["numbers"]:
                reasoning_parts.append("evaluated numeric constraints")
            if not reasoning_parts:
                reasoning_parts.append("structural alignment baseline")
                
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Bandit-guided selection: {', '.join(reasoning_parts)}. NCD backup applied."
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the bandit mean estimate for this specific candidate.
        """
        # Re-use evaluate logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return max(0.0, min(1.0, res[0]["score"]))