import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Variational Bandit Ecosystem (VBE) Implementation.
    
    Mechanism:
    1. Ecosystem Dynamics: Candidates are "species" competing for precision (score).
    2. Free Energy Principle: 'Energy' is prediction error. We estimate error via 
       Normalized Compression Distance (NCD) between the candidate and a synthesized 
       "ideal" answer derived from prompt constraints. Lower energy = higher fitness.
    3. Multi-Armed Bandits: We apply an Upper Confidence Bound (UCB) bonus to candidates 
       with high structural complexity (uncertainty/variance proxy) to encourage 
       exploration of non-trivial answers, balancing exploitation of low-energy matches.
       
    The final score is a precision-weighted combination of model evidence (low NCD) 
    and exploration bonus (complexity), normalized to [0, 1].
    """

    def __init__(self):
        self._state = {}

    def _get_compressed_length(self, text: str) -> int:
        """Returns byte length of zlib compressed text."""
        if not text:
            return 0
        return len(zlib.compress(text.encode('utf-8')))

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance between two strings."""
        if not s1 or not s2:
            return 1.0 if s1 != s2 else 0.0
        
        c1 = self._get_compressed_length(s1)
        c2 = self._get_compressed_length(s2)
        c12 = self._get_compressed_length(s1 + s2)
        
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        
        return (c12 - min(c1, c2)) / max_len

    def _extract_numerical_constraint(self, prompt: str) -> Tuple[bool, float, str]:
        """
        Simple parser to detect numeric comparisons (e.g., "9.11 < 9.9").
        Returns (found, value, operator).
        """
        import re
        # Look for pattern: number operator number
        match = re.search(r'(\d+\.?\d*)\s*([<>=]+)\s*(\d+\.?\d*)', prompt)
        if match:
            v1 = float(match.group(1))
            op = match.group(2)
            v2 = float(match.group(3))
            
            # Determine expected truth value based on operator
            # We want the candidate that satisfies the condition
            if op == '<':
                return True, v1 if v1 < v2 else v2, op
            elif op == '>':
                return True, v1 if v1 > v2 else v2, op
            elif op == '==' or op == '=':
                return True, v1 if v1 == v2 else (v1+v2)/2, op
        return False, 0.0, ""

    def _compute_structural_features(self, text: str) -> Dict[str, float]:
        """Extracts reasoning-relevant features: negations, comparatives, length."""
        t_lower = text.lower()
        has_neg = 1.0 if any(w in t_lower for w in ['not', 'no ', 'never', 'false']) else 0.0
        has_comp = 1.0 if any(w in t_lower for w in ['less', 'more', 'greater', 'smaller', '<', '>']) else 0.0
        length = len(text)
        complexity = self._get_compressed_length(text)
        
        return {
            "negation": has_neg,
            "comparative": has_comp,
            "length": length,
            "complexity": complexity
        }

    def _generate_hypothesis_target(self, prompt: str, candidates: List[str]) -> str:
        """
        Synthesizes a 'target' hypothesis string based on prompt constraints.
        In a full VBE, this would be a generative model output. 
        Here, we approximate by selecting the candidate that best satisfies 
        explicit numeric constraints, or fallback to prompt keywords.
        """
        found_num, val, op = self._extract_numerical_constraint(prompt)
        
        if found_num:
            # If numeric constraint exists, the "target" is effectively the logic 
            # that satisfies it. We don't generate a string, but the evaluation 
            # step will use this logic. For NCD purposes, we construct a pseudo-target.
            return f"result {val}"
        
        # Fallback: Use the most common words in prompt as a "consensus" target
        words = prompt.lower().split()
        common = [w for w in words if len(w) > 4 and w not in ['which', 'following', 'answer', 'question', 'choose']]
        if common:
            return " ".join(common[:5])
        return prompt[:50]

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        results = []
        target = self._generate_hypothesis_target(prompt, candidates)
        found_num, expected_val, op = self._extract_numerical_constraint(prompt)
        
        # Pre-calculate features for all candidates to determine ecosystem "variance"
        candidate_features = []
        for c in candidates:
            feats = self._compute_structural_features(c)
            candidate_features.append(feats)
        
        # Calculate mean complexity for UCB variance estimation
        complexities = [f["complexity"] for f in candidate_features]
        mean_complexity = sum(complexities) / len(complexities) if complexities else 1
        variance_proxy = sum((c - mean_complexity)**2 for c in complexities) / len(complexities) if len(complexities) > 1 else 1.0
        std_dev = math.sqrt(variance_proxy) if variance_proxy > 0 else 1.0

        for i, cand in enumerate(candidates):
            feats = candidate_features[i]
            
            # 1. Free Energy Calculation (Prediction Error)
            # Distance from target (lower is better)
            ncd_val = self._ncd(cand, target)
            
            # Numeric constraint penalty (High energy if violates math)
            numeric_penalty = 0.0
            if found_num:
                try:
                    # Check if candidate contains the expected number or logic
                    # Simple heuristic: if candidate is a number string
                    cand_clean = ''.join(ch for ch in cand if ch.isdigit() or ch == '.')
                    if cand_clean:
                        cand_val = float(cand_clean)
                        if op == '<' and not (cand_val < expected_val or cand_val == min(expected_val, 100)):
                             # Loose check: does it satisfy the relation roughly?
                             # Actually, let's just penalize if it's the wrong side of the bound
                             if op == '<' and cand_val > expected_val: numeric_penalty = 0.5
                             if op == '>' and cand_val < expected_val: numeric_penalty = 0.5
                except:
                    pass

            free_energy = ncd_val + numeric_penalty

            # 2. Multi-Armed Bandit Bonus (Exploration)
            # Bonus for complexity (uncertainty) - UCB style
            # Bonus = sqrt(2 * ln(total_trials) / visits). 
            # Here approximated by normalized complexity deviation.
            exploration_bonus = (feats["complexity"] - mean_complexity) / (std_dev + 1e-6)
            exploration_bonus = 0.1 * max(0, exploration_bonus) # Only bonus positive deviations

            # 3. Precision Weighted Score
            # Score = exp(-Energy + Bonus)
            raw_score = math.exp(-(free_energy * 2.0) + exploration_bonus)
            
            results.append({
                "candidate": cand,
                "score": raw_score,
                "reasoning": f"NCD:{ncd_val:.2f}, NumPen:{numeric_penalty}, ExpBonus:{exploration_bonus:.2f}"
            })

        # Normalize scores to [0, 1] range roughly
        max_score = max(r["score"] for r in results) if results else 1.0
        min_score = min(r["score"] for r in results) if results else 0.0
        range_score = max_score - min_score if (max_score - min_score) > 1e-6 else 1.0
        
        final_results = []
        for r in results:
            normalized = (r["score"] - min_score) / range_score
            # Ensure strictly non-negative and capped
            normalized = max(0.0, min(1.0, normalized))
            
            # Boost if it satisfies numeric constraint explicitly
            if found_num:
                try:
                    cand_clean = ''.join(ch for ch in r["candidate"] if ch.isdigit() or ch == '.')
                    if cand_clean:
                        val = float(cand_clean)
                        valid = False
                        if op == '<': valid = val < expected_val
                        elif op == '>': valid = val > expected_val
                        elif op == '==': valid = val == expected_val
                        
                        if valid:
                            normalized = max(normalized, 0.9) # Strong prior for correct math
                except:
                    pass

            final_results.append({
                "candidate": r["candidate"],
                "score": normalized,
                "reasoning": r["reasoning"]
            })

        # Sort descending by score
        final_results.sort(key=lambda x: x["score"], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluates confidence by simulating an ecosystem where the answer 
        competes against a set of synthetic distractors.
        """
        # Generate dummy distractors
        distractors = [
            "No", "Yes", "Unknown", "Error", 
            str(len(answer)), 
            answer[::-1], # Reversed answer
            "The opposite of " + answer
        ]
        candidates = [answer] + distractors
        
        ranked = self.evaluate(prompt, candidates)
        
        # Find rank of the actual answer
        for i, item in enumerate(ranked):
            if item["candidate"] == answer:
                # Confidence is inverse rank normalized
                return max(0.0, min(1.0, 1.0 - (i / len(ranked))))
        
        return 0.0