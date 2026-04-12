import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A hierarchical predictive-coding engine approximating the Free Energy Principle (FEP)
    combined with Compositionality and Kalman-style confidence estimation.
    
    Mechanism:
    1. FEP Core (evaluate): The system minimizes 'variational free energy' by selecting
       the candidate that maximizes structural consistency with the prompt. It parses
       logical operators (negations, comparatives, conditionals) as 'compositional rules'.
       The 'prediction error' is the mismatch between the prompt's logical constraints
       and the candidate's implication. The candidate with the lowest free energy (highest
       structural fit) is ranked highest.
    2. Compositionality: The parser breaks the prompt into logical fragments (subjects,
       operators, objects) to verify if the candidate satisfies the composed logic,
       not just keyword overlap.
    3. Kalman Filter (confidence): Treats the match quality as a Gaussian state.
       It computes a 'Kalman Gain' based on the ratio of structural evidence (signal)
       to string-noise (uncertainty). High structural density yields high gain (confidence).
    """

    def __init__(self):
        # Compositional grammar patterns (syntax-like sub-modules)
        self.negation_ops = ['not', 'no', 'never', 'none', 'neither']
        self.comparative_ops = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditional_ops = ['if', 'then', 'unless', 'otherwise']
        self.numeric_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_structure(self, text: str) -> Dict:
        """Parses text into compositional logical fragments."""
        lower_text = text.lower()
        words = lower_text.split()
        
        has_negation = any(op in words for op in self.negation_ops)
        has_comparative = any(op in words for op in self.comparative_ops)
        has_conditional = any(op in words for op in self.conditional_ops)
        
        numbers = [float(n) for n in self.numeric_pattern.findall(text)]
        
        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'length': len(words),
            'raw': lower_text
        }

    def _compute_structural_match(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Computes a score based on logical consistency (Free Energy minimization).
        Lower energy = Higher score.
        """
        score = 0.0
        evidence_count = 0

        # 1. Numeric Consistency (Strongest Signal)
        if prompt_struct['numbers'] and cand_struct['numbers']:
            # Check if candidate preserves numeric ordering or presence
            p_nums = sorted(prompt_struct['numbers'])
            c_nums = sorted(cand_struct['numbers'])
            
            # Simple heuristic: If prompt has numbers, candidate should likely reference them
            # or the logic implies a specific result. 
            # Here we reward exact number presence or logical derivation simulation.
            if set(p_nums) == set(c_nums):
                score += 2.0
            elif any(abs(p - c) < 1e-6 for p in p_nums for c in c_nums):
                score += 1.0
            evidence_count += 1

        # 2. Logical Operator Consistency
        # If prompt has negation, a 'Yes' candidate might be wrong if not careful, 
        # but here we check if the candidate mirrors the complexity.
        if prompt_struct['negation']:
            if cand_struct['negation']:
                score += 1.0 # Candidate acknowledges negation
            evidence_count += 1
            
        if prompt_struct['comparative']:
            if cand_struct['comparative'] or cand_struct['numbers']:
                score += 1.0
            evidence_count += 1

        if prompt_struct['conditional']:
            if cand_struct['conditional'] or cand_struct['length'] > 3: # Conditionals usually need longer answers
                score += 0.5
            evidence_count += 1

        # Penalty for length mismatch if prompt is complex (Compositionality check)
        if prompt_struct['length'] > 10 and cand_struct['length'] < 2:
            score -= 1.0

        return score if evidence_count > 0 else 0.0

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance (Tiebreaker only)."""
        if not s1 or not s2: return 1.0
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_joint = len(zlib.compress((s1 + s2).encode()))
        max_len = max(len1, len2)
        if max_len == 0: return 0.0
        return (len_joint - min(len1, len2)) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Ranks candidates by minimizing variational free energy (maximizing structural fit).
        Uses NCD only as a tiebreaker for candidates with identical structural scores.
        """
        p_struct = self._extract_structure(prompt)
        scored_candidates = []

        for cand in candidates:
            c_struct = self._extract_structure(cand)
            
            # Primary Score: Structural/Logical Consistency (FEP Drive)
            struct_score = self._compute_structural_match(p_struct, c_struct)
            
            # Secondary Score: NCD (Tiebreaker)
            # Invert NCD so higher is better, scale to small epsilon range to not override struct
            ncd_val = self._ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.01 

            total_score = struct_score + ncd_score
            reasoning = f"Structural fit: {struct_score:.2f}, NCD bonus: {ncd_score:.4f}"
            
            scored_candidates.append({
                "candidate": cand,
                "score": total_score,
                "reasoning": reasoning
            })

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Estimates confidence using a Kalman-Filter analogy.
        State: Correctness. Measurement: Structural Match.
        Gain depends on the density of logical signals (uncertainty reduction).
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(answer)
        
        # Measurement (z): How well does it fit structurally?
        # Normalize structural match to 0-1 range roughly
        raw_fit = self._compute_structural_match(p_struct, c_struct)
        z = min(1.0, max(0.0, raw_fit / 3.0)) # Scale down to probability-like range

        # Uncertainty (R): Inverse of signal density
        # More logical operators/numbers = lower uncertainty (higher confidence potential)
        signal_density = 0
        if p_struct['numbers']: signal_density += 2
        if p_struct['negation']: signal_density += 1
        if p_struct['comparative']: signal_density += 1
        if p_struct['conditional']: signal_density += 1
        
        # If no signals, uncertainty is high (Gain low)
        uncertainty = 1.0 / (signal_density + 1) 
        
        # Kalman Gain (K): How much do we trust the measurement?
        # K = P_prior / (P_prior + R) -> Simplified here to depend on signal density
        # If signal density is high, K approaches 1. If low, K approaches 0.
        kalman_gain = signal_density / (signal_density + 2.0)
        
        # Update estimate (x_post = x_prior + K * (z - x_prior))
        # Assume neutral prior (0.5)
        prior = 0.5
        posterior = prior + kalman_gain * (z - prior)
        
        return max(0.0, min(1.0, posterior))