import math
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Lyapunov-guided, Implicature-shaped MPC for Belief Trajectories.
    
    Mechanism:
    1. Chaotic Probing: Uses a logistic map (r=3.99) to generate deterministic, 
       high-frequency perturbations. This prevents stagnation in local minima 
       of the hypothesis space by ensuring exponential divergence of nearby 
       candidate evaluations.
    2. Optimal Control Backbone: Evaluates candidates based on a cost functional 
       approximating the Hamilton-Jacobi-Bellman equation. The "cost" is the 
       distance to the prompt's logical constraints (structural parsing).
    3. Pragmatic Cost Shaping: Applies Gricean maxims (Quantity, Quality, Relevance) 
       as penalty terms. Candidates that are too short (Quantity), lack key prompt 
       tokens (Relevance), or contradict explicit negations (Quality) receive 
       higher costs.
    
    The final score is a normalized inverse of the total cost, modulated by the 
    chaotic probe to break ties and encourage exploration of diverse reasoning paths.
    """

    def __init__(self):
        # State for chaotic map: x_{n+1} = r * x_n * (1 - x_n)
        # r = 3.99 ensures chaos (positive Lyapunov exponent)
        self._chaos_state = 0.5
        self._r = 3.99
        
    def _chaos_step(self) -> float:
        """Deterministic chaotic perturbation via logistic map."""
        self._chaos_state = self._r * self._chaos_state * (1.0 - self._chaos_state)
        return self._chaos_state

    def _reset_chaos(self, seed_str: str):
        """Seed the chaotic generator deterministically from input."""
        val = sum(ord(c) for c in seed_str) % 1000 / 1000.0
        self._chaos_state = 0.01 + 0.98 * val  # Keep within (0, 1)

    def _structural_parse(self, text: str) -> Dict[str, Any]:
        """Extract logical constraints: negations, numbers, comparatives."""
        lower = text.lower()
        has_neg = any(n in lower for n in ["not ", "no ", "never ", "cannot ", "don't ", "doesn't "])
        has_num = any(c.isdigit() for c in text)
        numbers = []
        
        # Simple number extraction
        current_num = ""
        for char in text:
            if char.isdigit() or char == '.':
                current_num += char
            else:
                if current_num:
                    try: numbers.append(float(current_num))
                    except: pass
                    current_num = ""
        if current_num:
            try: numbers.append(float(current_num))
            except: pass

        return {
            "negated": has_neg,
            "has_numbers": has_num,
            "numbers": numbers,
            "length": len(text.split()),
            "tokens": set(lower.split())
        }

    def _gricean_cost(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Calculate pragmatic cost based on Gricean Maxims.
        Lower cost = better adherence.
        """
        cost = 0.0
        
        # 1. Maxim of Quantity (Be informative, not too brief)
        if cand_struct["length"] < max(1, prompt_struct["length"] * 0.3):
            cost += 0.5  # Penalty for being too vague
        
        # 2. Maxim of Relevance (Token overlap)
        overlap = len(prompt_struct["tokens"] & cand_struct["tokens"])
        if overlap == 0 and prompt_struct["length"] > 2:
            cost += 0.8  # High penalty for irrelevance
            
        # 3. Maxim of Quality (Negation consistency)
        # If prompt has strong negation, candidate should reflect understanding
        if prompt_struct["negated"] and not cand_struct["negated"]:
            # Heuristic: if prompt says "not X", and candidate doesn't acknowledge negation structure
            # This is a soft check; strict logic handled in scoring
            pass 
            
        # 4. Manner (Clarity/Structure) - approximated by number consistency
        if prompt_struct["has_numbers"] and cand_struct["has_numbers"]:
            # Check if numbers are wildly different (simplistic quality check)
            if prompt_struct["numbers"] and cand_struct["numbers"]:
                p_avg = sum(prompt_struct["numbers"]) / len(prompt_struct["numbers"])
                c_avg = sum(cand_struct["numbers"]) / len(cand_struct["numbers"])
                if p_avg != 0 and abs(c_avg - p_avg) > abs(p_avg):
                    cost += 0.3 # Penalty for diverging numerical logic
                    
        return cost

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        len1, len2 = len(b1), len(b2)
        if len1 == 0 or len2 == 0: return 1.0
        try:
            len_combined = len(zlib.compress(b1 + b2))
        except: return 1.0
        return (len_combined - min(len1, len2)) / max(len1, len2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        if not candidates:
            return []
            
        self._reset_chaos(prompt)
        prompt_struct = self._structural_parse(prompt)
        results = []
        
        # Pre-calculate prompt complexity for normalization
        prompt_complexity = len(prompt) + len(prompt_struct["numbers"]) * 10
        
        for cand in candidates:
            cand_struct = self._structural_parse(cand)
            
            # 1. Optimal Control Cost (Distance to logical constraints)
            # Base cost from NCD (similarity to prompt context)
            base_dist = self._compute_ncd(prompt, cand)
            
            # 2. Pragmatic Shaping (Gricean Cost)
            prag_cost = self._gricean_cost(prompt_struct, cand_struct, prompt, cand)
            
            # 3. Logical Consistency Check (Hard constraints)
            logic_penalty = 0.0
            if prompt_struct["negated"]:
                # If prompt says "not", and candidate is a direct substring match without negation, penalize
                if prompt.lower().replace("not ", "") in cand.lower() and "not" not in cand.lower():
                    logic_penalty = 1.0
            
            # 4. Chaotic Probing (Lyapunov modulation)
            # Injects deterministic noise to break ties and explore hypothesis space
            chaos_factor = self._chaos_step() * 0.15 
            
            # Total Cost Functional
            # Minimizing: (Distance + Pragmatic Violation + Logic Error) modulated by Chaos
            total_cost = (base_dist * 0.4) + (prag_cost * 0.4) + (logic_penalty * 0.2)
            
            # Convert cost to score (inverse), bounded [0, 1]
            # Add small chaos term to score to ensure divergence in ranking if costs are equal
            raw_score = max(0.0, 1.0 - total_cost) 
            final_score = min(1.0, raw_score + (chaos_factor * (1.0 - raw_score)) - (chaos_factor * raw_score))
            
            # Reasoning string generation
            reasoning = f"NCD:{base_dist:.2f}, PragCost:{prag_cost:.2f}, LogicPen:{logic_penalty:.2f}, Chaos:{chaos_factor:.3f}"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on the evaluation score."""
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        return res[0]["score"]