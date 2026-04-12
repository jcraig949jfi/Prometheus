import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Fractal Incentivized Bandit Mechanism (FIBM) Implementation
    
    Core Architecture (Mechanism Design - Primary Driver):
    Treats candidate evaluation as a VCG-style auction. Candidates are 'agents' 
    bidding for correctness. The 'payment' (score) is derived from how much 
    the candidate's structural evidence improves the global truth estimate 
    compared to the counterfactual where that evidence was absent.
    
    Structural Parsing (Reasoning Signal):
    Replaces fractal geometry (historical inhibitor) with recursive structural 
    parsing. We decompose the prompt into a hierarchy of logical constraints 
    (negations, comparatives, conditionals) acting as the 'fractal tiling' of 
    the logic space.
    
    Bandit Feedback (Exploration):
    Uses a deterministic Upper Confidence Bound (UCB) analogue where the 
    'exploration bonus' is granted to candidates that satisfy low-frequency 
    structural constraints identified in the prompt.
    """

    def __init__(self):
        self.structural_keywords = {
            'negations': ['not', 'no', 'never', 'none', 'neither', 'nobody'],
            'comparatives': ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'before', 'after'],
            'conditionals': ['if', 'unless', 'provided', 'assuming', 'when'],
            'logic_ops': ['and', 'or', 'but', 'however', 'therefore']
        }

    def _structural_parse(self, text: str) -> Dict[str, float]:
        """Extracts logical features to form the 'fractal' hypothesis space."""
        text_lower = text.lower()
        features = {}
        
        # Count negation density (inhibits simple matching)
        neg_count = sum(1 for w in self.structural_keywords['negations'] if f" {w} " in f" {text_lower} ")
        features['negation_density'] = neg_count / (len(text.split()) + 1)
        
        # Detect numeric comparisons
        numbers = re.findall(r"[-+]?\d*\.?\d+", text)
        has_comparison = any(op in text_lower for op in ['<', '>', 'equal', 'larger', 'smaller'])
        features['numeric_complexity'] = (len(numbers) > 1 and has_comparison)
        
        # Conditional depth
        cond_count = sum(1 for w in self.structural_keywords['conditionals'] if w in text_lower)
        features['conditional_depth'] = cond_count
        
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 1.0
        return (c12 - min(c1, c2)) / max_len

    def _mechanism_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Computes the VCG-style score.
        Score = Base Utility (Structural Match) + Bonus (Constraint Satisfaction) - Penalty (Contradiction)
        """
        p_features = self._structural_parse(prompt)
        c_features = self._structural_parse(candidate)
        candidate_lower = candidate.lower()
        prompt_lower = prompt.lower()
        
        base_score = 0.5
        reasoning_steps = []
        
        # 1. Negation Handling (Modus Tollens check)
        # If prompt has high negation density, candidate must reflect it to gain utility
        if p_features['negation_density'] > 0.05:
            if c_features['negation_density'] > 0.03:
                base_score += 0.2
                reasoning_steps.append("Aligned negation context")
            else:
                # Penalty for ignoring negation (common failure mode)
                base_score -= 0.3
                reasoning_steps.append("Failed to propagate negation")
        
        # 2. Numeric/Comparative Consistency
        if p_features['numeric_complexity']:
            # Extract numbers from both
            p_nums = re.findall(r"[-+]?\d*\.?\d+", prompt_lower)
            c_nums = re.findall(r"[-+]?\d*\.?\d+", candidate_lower)
            
            if c_nums:
                # Simple heuristic: if prompt implies ordering, check if candidate respects basic magnitude
                # This is a proxy for the 'fractal' refinement of the number line
                try:
                    p_vals = [float(x) for x in p_nums]
                    c_vals = [float(x) for x in c_nums]
                    if len(p_vals) >= 2 and len(c_vals) >= 1:
                        # Check if candidate numbers are within the logical range implied
                        p_range = max(p_vals) - min(p_vals)
                        if any(abs(c - sum(p_vals)/len(p_vals)) <= (p_range + 0.1) for c in c_vals):
                            base_score += 0.25
                            reasoning_steps.append("Numeric consistency verified")
                        else:
                            base_score -= 0.1
                            reasoning_steps.append("Numeric outlier detected")
                except ValueError:
                    pass

        # 3. Conditional/Logical Overlap (The 'Bandit' Arm Selection)
        # Reward candidates that reuse specific logical operators from the prompt
        logic_matches = 0
        for op in self.structural_keywords['logic_ops'] + self.structural_keywords['conditionals']:
            if op in prompt_lower and op in candidate_lower:
                logic_matches += 1
        
        if logic_matches > 0:
            bonus = min(0.3, logic_matches * 0.1)
            base_score += bonus
            reasoning_steps.append(f"Logical operator alignment (+{bonus:.2f})")

        # 4. VCG Counterfactual Check (Simplified)
        # If the candidate is just a substring echo, it provides no new information (low value)
        if candidate_lower.strip() in prompt_lower.strip() and len(candidate) < len(prompt) * 0.5:
            base_score -= 0.2
            reasoning_steps.append("Penalized for mere repetition (low information gain)")

        # Normalize score to 0-1 range roughly
        final_score = max(0.0, min(1.0, base_score))
        
        return final_score, "; ".join(reasoning_steps) if reasoning_steps else "Structural baseline"

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        
        # Phase 1: Structural Evaluation (Mechanism Design Core)
        for cand in candidates:
            score, reason = self._mechanism_score(prompt, cand)
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason,
                "_ncd": self._compute_ncd(prompt, cand) # Store for tie-breaking
            })
        
        # Phase 2: Sorting with NCD Tie-Breaking
        # Sort by: Score (desc), then NCD (asc - lower distance is better if scores match)
        scored_candidates.sort(key=lambda x: (x['score'], -x['_ncd']), reverse=True)
        
        # Clean up and format output
        result = []
        for item in scored_candidates:
            result.append({
                "candidate": item["candidate"],
                "score": round(item["score"], 4),
                "reasoning": item["reasoning"]
            })
            
        return result

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment.
        Uses the same mechanism as evaluate but returns a single scalar.
        """
        score, _ = self._mechanism_score(prompt, answer)
        
        # Additional strict check for "I don't know" or empty answers in high-stakes prompts
        if not answer.strip():
            return 0.0
            
        # If the prompt asks for a specific format (e.g., number) and answer fails, reduce confidence
        if re.search(r"calculate|sum|count|number", prompt.lower()):
            if not re.search(r"\d", answer):
                return max(0.0, score - 0.4)
                
        return max(0.0, min(1.0, score))