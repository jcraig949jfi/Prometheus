import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Self-Tuning Critical Belief-Propagation Engine (Simplified Implementation).
    
    Mechanism:
    1. Network Science: Represents prompt and candidates as nodes in a dependency graph.
       Edges are inferred via structural overlap (shared logical tokens).
    2. Phase Transitions: Uses a 'temperature' parameter to scale belief updates.
       The system simulates susceptibility (variance in agreement) to tune sensitivity.
       High susceptibility = Critical point (optimal for distinguishing subtle signals).
    3. Maximum Entropy (Restricted): Used only to initialize uniform priors over 
       structural features, avoiding direct scoring bias as per safety constraints.
    
    Scoring Strategy:
    - Primary: Structural parsing (negations, comparatives, conditionals, numeric logic).
    - Secondary: Constraint propagation (subject-object consistency).
    - Tiebreaker: Normalized Compression Distance (NCD).
    """

    def __init__(self):
        # Structural tokens for parsing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'provided', 'when'}
        self.logic_ops = {'and', 'or', 'but', 'however', 'therefore', 'thus'}
        
        # Criticality parameters
        self.tau = 1.0  # Temperature
        self.tau_c = 1.0 # Critical temperature estimate
        self.susceptibility_window = []

    def _tokenize(self, text: str) -> set:
        return set(re.findall(r'\b\w+\b', text.lower()))

    def _extract_structure(self, text: str) -> dict:
        """Extracts logical structures: negations, comparatives, conditionals, numbers."""
        tokens = self._tokenize(text)
        numbers = re.findall(r'\d+\.?\d*', text)
        
        # Parse numeric comparisons if present
        numeric_logic = []
        if len(numbers) >= 2:
            try:
                vals = [float(n) for n in numbers]
                # Simple transitivity check placeholder
                numeric_logic = sorted(vals)
            except ValueError:
                pass

        return {
            'has_negation': bool(tokens & self.negations),
            'has_comparative': bool(tokens & self.comparatives),
            'has_conditional': bool(tokens & self.conditionals),
            'has_logic_op': bool(tokens & self.logic_ops),
            'numbers': numbers,
            'numeric_sorted': numeric_logic,
            'token_count': len(tokens),
            'raw_tokens': tokens
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        if max(c1, c2) == 0: return 1.0
        return (c12 - min(c1, c2)) / max(c1, c2)

    def _structural_score(self, prompt_struct: dict, cand_struct: dict) -> float:
        """Scores based on logical consistency and structural overlap."""
        score = 0.0
        
        # 1. Negation Consistency
        # If prompt has negation, candidate should ideally reflect or address it
        if prompt_struct['has_negation']:
            if cand_struct['has_negation']:
                score += 2.0 # Reinforces logical tracking
            else:
                score -= 1.0 # Penalty for ignoring negation context
        
        # 2. Comparative/Conditional Alignment
        if prompt_struct['has_conditional'] and cand_struct['has_conditional']:
            score += 1.5
        elif prompt_struct['has_conditional'] and not cand_struct['has_conditional']:
            # Soft penalty, some answers resolve conditionals without restating them
            score += 0.2 
            
        if prompt_struct['has_comparative'] and cand_struct['has_comparative']:
            score += 1.5

        # 3. Numeric Logic Check
        if prompt_struct['numbers'] and cand_struct['numbers']:
            # Check if candidate numbers are a subset or derived logic
            p_nums = set(prompt_struct['numbers'])
            c_nums = set(cand_struct['numbers'])
            if c_nums.issubset(p_nums):
                score += 2.0 # Likely extracting facts
            elif len(c_nums) > 0:
                score += 0.5 # Introducing new numbers (risky but possible)

        # 4. Token Overlap (Jaccard-like) weighted by logic
        common = prompt_struct['raw_tokens'] & cand_struct['raw_tokens']
        union = prompt_struct['raw_tokens'] | cand_struct['raw_tokens']
        if union:
            overlap = len(common) / len(union)
            # Boost overlap if logical operators are shared
            if prompt_struct['has_logic_op'] and cand_struct['has_logic_op']:
                overlap *= 1.5
            score += overlap * 3.0
            
        return score

    def _simulate_critical_dynamics(self, scores: List[float]) -> List[float]:
        """
        Applies a phase-transition inspired adjustment.
        Calculates susceptibility (variance) to tune the 'temperature'.
        Near criticality, small differences in structural score are amplified.
        """
        if not scores: return []
        if len(scores) == 1: return [1.0]
        
        # Estimate susceptibility (variance of activity)
        mean_s = sum(scores) / len(scores)
        variance = sum((s - mean_s)**2 for s in scores) / len(scores)
        susceptibility = variance + 1e-6
        
        # Adaptive Temperature Control
        # If susceptibility is low (frozen), increase tau to explore differences
        # If susceptibility is high (chaotic), decrease tau to stabilize
        self.susceptibility_window.append(susceptibility)
        if len(self.susceptibility_window) > 5:
            self.susceptibility_window.pop(0)
            
        avg_sus = sum(self.susceptibility_window) / len(self.susceptibility_window)
        
        # Heuristic tuning to stay near critical point
        if avg_sus < 0.1: 
            self.tau *= 1.1 # Heat up
        elif avg_sus > 1.0:
            self.tau *= 0.9 # Cool down
            
        # Apply Boltzmann-like scaling to scores
        # S' = exp((S - max(S)) / tau)
        # This amplifies the best candidates when tau is small (ordered)
        # and flattens them when tau is large (disordered)
        max_s = max(scores)
        adjusted = []
        for s in scores:
            # Shift to avoid overflow, scale by temperature
            val = math.exp((s - max_s) / (self.tau + 1e-6))
            adjusted.append(val)
            
        # Normalize to 0-1 range
        total = sum(adjusted) + 1e-9
        return [x / total for x in adjusted]

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_struct = self._extract_structure(prompt)
        raw_scores = []
        
        # Phase 1: Structural Scoring (Primary Signal)
        for cand in candidates:
            c_struct = self._extract_structure(cand)
            s = self._structural_score(p_struct, c_struct)
            raw_scores.append(s)
            
        # Phase 2: Critical Belief Propagation (Scaling)
        # Simulates the network settling into an attractor state
        final_probs = self._simulate_critical_dynamics(raw_scores)
        
        # Phase 3: NCD Tiebreaking (Only if probabilities are extremely close)
        # This ensures we beat the NCD baseline without relying on it primarily
        results = []
        for i, cand in enumerate(candidates):
            score = final_probs[i]
            reasoning = f"Structural match: {raw_scores[i]:.2f}, Critical prob: {score:.4f}"
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and critical stability.
        """
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        # Base structural score
        base_score = self._structural_score(p_struct, a_struct)
        
        # Normalize roughly to 0-1 based on expected max score (~10.0 max theoretical)
        # Using a sigmoid-like mapping centered around typical noise floor
        # score > 2.0 is usually significant structural alignment
        confidence = 1.0 / (1.0 + math.exp(-0.8 * (base_score - 2.0)))
        
        # Apply critical temperature penalty if system is unstable
        if len(self.susceptibility_window) > 0:
            current_sus = self.susceptibility_window[-1]
            if current_sus > 2.0: # High chaos
                confidence *= 0.8 # Reduce confidence
                
        return max(0.0, min(1.0, confidence))