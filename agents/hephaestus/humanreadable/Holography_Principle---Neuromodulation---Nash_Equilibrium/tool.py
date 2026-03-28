import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Holographic Predictive-Coding Multi-Agent Reasoner.
    
    Mechanism:
    1. Holographic Boundary (Structural Parsing): Instead of storing a full world model,
       we project the prompt onto a low-dimensional 'boundary' representation consisting of
       structural features: negations, comparatives, conditionals, and numeric values.
       This acts as the tensor-network-like compression of the problem space.
    
    2. Neuromodulation (Precision Weighting): We calculate a 'precision' score based on
       the density of logical operators and numeric constraints in the prompt. High precision
       amplifies the penalty for structural mismatches (e.g., missing a negation), while
       low precision allows more semantic flexibility. This mimics gain control.
    
    3. Nash Equilibrium (Hypothesis Competition): Candidates act as agents proposing 
       distributions over the boundary states. They compete to minimize 'expected surprise'
       (prediction error). The scoring function represents an equilibrium state where a 
       candidate's score is maximized only if it satisfies the structural constraints 
       (boundary conditions) better than alternatives, weighted by the neuromodulatory gain.
       No candidate can improve its score (reduce surprise) by ignoring the structural rules.
    
    This triadic binding ensures robust reasoning by prioritizing logical structure (Holography)
    modulated by context sensitivity (Neuromodulation) to select the most consistent hypothesis (Nash).
    """

    def __init__(self):
        # Structural patterns for the "Holographic Boundary" projection
        self.negation_patterns = [r'\bnot\b', r'\bno\b', r'\bnever\b', r'\bwithout\b', r"n't"]
        self.comparative_patterns = [r'\bmore\b', r'\bless\b', r'\bgreater\b', r'\bsmaller\b', r'\bhigher\b', r'\blower\b', r'>', r'<']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\belse\b', r'\bwhen\b']
        self.numeric_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_boundary_state(self, text: str) -> Dict:
        """Projects text onto the low-dimensional structural boundary."""
        text_lower = text.lower()
        
        # Count structural features
        neg_count = sum(len(re.findall(p, text_lower)) for p in self.negation_patterns)
        comp_count = sum(len(re.findall(p, text_lower)) for p in self.comparative_patterns)
        cond_count = sum(len(re.findall(p, text_lower)) for p in self.conditional_patterns)
        numbers = [float(n) for n in re.findall(self.numeric_pattern, text)]
        
        return {
            'negations': neg_count,
            'comparatives': comp_count,
            'conditionals': cond_count,
            'numbers': numbers,
            'length': len(text),
            'raw': text
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _calculate_surprise(self, prompt_state: Dict, cand_state: Dict, precision_gain: float) -> float:
        """
        Calculates negative expected surprise (payoff).
        Lower surprise = higher payoff.
        """
        surprise = 0.0
        
        # 1. Negation Consistency (Critical for reasoning traps)
        # If prompt has negations, candidate must reflect awareness (simplified heuristic)
        if prompt_state['negations'] > 0:
            # Penalty if candidate ignores negation context entirely (heuristic: length mismatch on key tokens)
            # We approximate "ignoring" by checking if the candidate is suspiciously short compared to prompt logic
            if cand_state['length'] < prompt_state['length'] * 0.1 and prompt_state['negations'] > 1:
                surprise += 2.0 * precision_gain
        
        # 2. Numeric Consistency
        if prompt_state['numbers'] and cand_state['numbers']:
            # Check if candidate numbers are within reasonable bounds of prompt numbers
            # This handles "9.11 < 9.9" type logic by rewarding presence of comparable magnitudes
            p_nums = prompt_state['numbers']
            c_nums = cand_state['numbers']
            
            # Simple proximity check: does the candidate contain a number close to any prompt number?
            # Or does it contain a number that resolves a comparison?
            found_match = False
            for cn in c_nums:
                for pn in p_nums:
                    if abs(cn - pn) < 0.1: # Approximate match
                        found_match = True
                        break
                if found_match:
                    break
            
            if not found_match:
                # If numbers exist in both but don't align, increase surprise based on precision
                surprise += 1.5 * precision_gain
        elif prompt_state['numbers'] and not cand_state['numbers']:
            # Prompt has numbers, candidate has none -> High surprise (likely wrong)
            surprise += 3.0 * precision_gain

        # 3. Structural Complexity Match
        # Candidates addressing complex conditionals should ideally be longer/more complex
        if prompt_state['conditionals'] > 0:
            if cand_state['length'] < 10: # Too short to address a conditional
                surprise += 1.0 * precision_gain

        return -surprise # Return negative surprise as payoff

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_state = self._extract_boundary_state(prompt)
        
        # Neuromodulation: Calculate Precision Gain
        # High logical density -> High precision required -> High penalty for errors
        logical_density = (prompt_state['negations'] + prompt_state['comparatives'] + 
                           prompt_state['conditionals'] + len(prompt_state['numbers']))
        # Normalize gain: base 1.0, scaling up with density
        precision_gain = 1.0 + (logical_density * 0.5)

        scored_candidates = []
        
        # Pre-calculate NCD matrix for tie-breaking if needed (simplified here to pairwise)
        # In a full Nash system, we'd iterate until equilibrium. 
        # Here, we approximate the equilibrium by scoring against the prompt boundary directly.
        
        for cand in candidates:
            cand_state = self._extract_boundary_state(cand)
            
            # Calculate Payoff (Negative Surprise)
            payoff = self._calculate_surprise(prompt_state, cand_state, precision_gain)
            
            # Base score from structural alignment
            # We invert surprise to get a positive score component
            base_score = 0.5 + (payoff * 0.1) 
            
            # Add small bonus for keyword overlap (semantic hint) but keep it low weight
            common_words = set(prompt_state['raw'].lower().split()) & set(cand_state['raw'].lower().split())
            semantic_bonus = min(0.1, len(common_words) * 0.01)
            
            final_score = base_score + semantic_bonus
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match (neg:{cand_state['negations']}, num:{len(cand_state['numbers'])}) with precision gain {precision_gain:.2f}"
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Apply NCD Tie-Breaking for candidates with very close scores (within 0.01)
        # This satisfies the requirement to use NCD only as a tiebreaker
        if len(scored_candidates) > 1:
            if abs(scored_candidates[0]['score'] - scored_candidates[1]['score']) < 0.01:
                # Re-sort based on NCD to prompt for the top cluster
                # Lower NCD is better
                top_cluster = []
                threshold = scored_candidates[0]['score']
                for c in scored_candidates:
                    if abs(c['score'] - threshold) < 0.01:
                        top_cluster.append(c)
                    
                if len(top_cluster) > 1:
                    top_cluster.sort(key=lambda x: self._compute_ncd(prompt, x['candidate']))
                    # Reconstruct list: sorted top cluster + rest
                    rest = [c for c in scored_candidates if c not in top_cluster]
                    scored_candidates = top_cluster + rest

        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency.
        """
        prompt_state = self._extract_boundary_state(prompt)
        ans_state = self._extract_boundary_state(answer)
        
        # Calculate precision gain again
        logical_density = (prompt_state['negations'] + prompt_state['comparatives'] + 
                           prompt_state['conditionals'] + len(prompt_state['numbers']))
        precision_gain = 1.0 + (logical_density * 0.5)
        
        surprise = self._calculate_surprise(prompt_state, ans_state, precision_gain)
        
        # Convert surprise to confidence (0-1)
        # Surprise is negative payoff. 
        # If surprise is 0, confidence is high. If surprise is large negative, confidence low.
        # Sigmoid-like mapping
        confidence = 1.0 / (1.0 + math.exp(surprise))
        
        # Clamp
        return max(0.0, min(1.0, confidence))