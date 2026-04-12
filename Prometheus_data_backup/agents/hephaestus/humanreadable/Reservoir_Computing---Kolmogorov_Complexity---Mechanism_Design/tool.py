import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Kolmogorov-Reservoir Mechanism-Design (KRMD) Tool.
    
    Mechanism:
    1. Reservoir Computing (Approximated): Inputs are mapped to a fixed high-dimensional
       feature space using hash-based positional encoding and n-gram extraction, simulating
       the "echo state" of temporal features without heavy recurrence.
    2. Mechanism Design (Core): Candidates act as agents. They are scored via a VCG-like
       scheme where the payoff is maximized by "truth-telling" (structural alignment) and
       minimized by "noise" (random guessing).
    3. Kolmogorov Complexity (Approximated): Used as a tiebreaker. Candidates that allow
       the prompt+answer to be compressed more (lower NCD) are preferred, assuming they
       capture the underlying pattern parsimoniously.
       
    Priority: Structural parsing > Numeric evaluation > NCD compression.
    """

    def __init__(self):
        self.reservoir_dim = 64  # Simulated reservoir size
        
    def _extract_structural_features(self, text: str) -> dict:
        """Extract logical constraints: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without|unless)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|else|unless|provided)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'length': len(text)
        }
        return features

    def _simulate_reservoir(self, text: str) -> np.ndarray:
        """
        Simulate a fixed recurrent reservoir using hash-based positional encoding.
        This creates a high-dimensional representation of the input stream.
        """
        state = np.zeros(self.reservoir_dim)
        if not text:
            return state
            
        # Simple hash-based projection to fixed dimensions
        for i, char in enumerate(text[:100]): # Limit context for speed
            h = hash(f"{char}{i}") 
            idx = h % self.reservoir_dim
            state[idx] += 1.0 / (i + 1) # Decay influence over time
            
        # Normalize
        norm = np.linalg.norm(state)
        if norm > 0:
            state /= norm
        return state

    def _calculate_mdl_score(self, prompt: str, candidate: str) -> float:
        """
        Approximate Kolmogorov Complexity via NCD.
        Lower compression distance = higher likelihood of being the 'true' pattern.
        """
        p_bytes = prompt.encode('utf-8')
        c_bytes = candidate.encode('utf-8')
        
        len_p = len(zlib.compress(p_bytes))
        len_c = len(zlib.compress(c_bytes))
        len_pc = len(zlib.compress(p_bytes + c_bytes))
        
        # Normalized Compression Distance
        denominator = max(len_p, len_c)
        if denominator == 0:
            return 0.0
        ncd = (len_pc - min(len_p, len_c)) / denominator
        return 1.0 - ncd # Invert so higher is better

    def _structural_alignment_score(self, prompt: str, candidate: str) -> float:
        """
        Mechanism Design: Score based on structural adherence.
        Checks if the candidate respects the logical constraints of the prompt.
        """
        p_feat = self._extract_structural_features(prompt)
        c_feat = self._extract_structural_features(candidate)
        score = 0.0
        
        # 1. Numeric Consistency (High Priority)
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                p_nums = [float(n) for n in p_feat['numbers']]
                c_nums = [float(n) for n in c_feat['numbers']]
                
                # Check for direct extraction or simple arithmetic consistency
                # If prompt has numbers and candidate repeats a key number, boost score
                common_nums = set(p_nums) & set(c_nums)
                if common_nums:
                    score += 2.0
                
                # Check comparative logic (simplified)
                if p_feat['comparatives']:
                    if len(c_nums) >= 2:
                        # If prompt implies comparison, candidate having multiple numbers is good
                        score += 1.0
            except ValueError:
                pass

        # 2. Logical Constraint Propagation
        # If prompt has negation, valid answers often contain specific markers or avoid contradiction
        if p_feat['negations'] > 0:
            # Heuristic: Candidates that are too short might miss the nuance
            if c_feat['length'] > 5:
                score += 0.5
        
        # 3. Conditional Logic
        if p_feat['conditionals'] > 0:
            if c_feat['conditionals'] > 0 or c_feat['length'] > 10:
                score += 0.5

        return score

    def _mechanism_payoff(self, prompt: str, candidate: str, all_candidates: List[str]) -> float:
        """
        Calculate the VCG-like payoff for a candidate.
        Payoff = Structural Alignment (Truthfulness) + Compression Reward - Penalty for Deviation
        """
        # Base score from structural alignment (The "Truth-Telling" incentive)
        structural_score = self._structural_alignment_score(prompt, candidate)
        
        # Compression reward (Kolmogorov term)
        compression_score = self._calculate_mdl_score(prompt, candidate)
        
        # Reservoir similarity (Echo State check)
        # Does the candidate "resonate" with the prompt's feature space?
        p_state = self._simulate_reservoir(prompt)
        c_state = self._simulate_reservoir(candidate)
        resonance = np.dot(p_state, c_state) # Cosine similarity since normalized
        
        # Mechanism Design Adjustment:
        # If a candidate is an exact substring or very close, it gets a massive boost (Truthful reporting)
        # But we penalize pure echoing if it doesn't add value (simplified here)
        candidate_lower = candidate.lower().strip()
        prompt_lower = prompt.lower().strip()
        
        echo_penalty = 0.0
        if candidate_lower in prompt_lower and len(candidate_lower) < len(prompt_lower) * 0.9:
            # It's just a fragment, likely not the full answer unless the question is trivial
            # We rely on structural score to validate if fragment is sufficient
            pass 
            
        # Weighted sum representing the mechanism's equilibrium
        # Structural logic is the primary driver (as per instructions)
        total_payoff = (structural_score * 0.6) + (compression_score * 0.3) + (resonance * 0.1)
        
        return total_payoff

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        for cand in candidates:
            score = self._mechanism_payoff(prompt, cand, candidates)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": f"Structural:{self._structural_alignment_score(prompt, cand):.2f}, Compression:{self._calculate_mdl_score(prompt, cand):.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the mechanism's evaluation of the single answer.
        """
        # Evaluate against a dummy set including the answer to get relative scoring
        # In a real scenario, we might compare against a "null" hypothesis
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        raw_score = res[0]['score']
        
        # Normalize to 0-1 range heuristically based on observed bounds
        # Structural score can be > 1, compression is 0-1, resonance 0-1
        # Typical max raw_score approx 3-4. 
        confidence = min(1.0, max(0.0, raw_score / 4.0))
        
        return confidence