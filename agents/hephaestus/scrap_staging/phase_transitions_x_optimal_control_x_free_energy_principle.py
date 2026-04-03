import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical Active-Inference Controller (CAIC) for Reasoning.
    
    Mechanism:
    1. Core (Free Energy Principle): Evaluates candidates based on structural 
       consistency (negations, conditionals, numeric logic) with the prompt. 
       This acts as the variational free energy minimization, penalizing 
       prediction errors in logic structure.
    2. Modulator (Phase Transitions): Implements a 'critical slowing down' 
       effect. If structural evidence is ambiguous (near a bifurcation point), 
       the system delays commitment (lowers confidence/score variance). 
       If evidence crosses a critical threshold, it triggers a discontinuous 
       jump to high confidence.
    3. Constraint (Optimal Control): Used ONLY in the confidence() wrapper 
       to penalize high-control-effort answers (those requiring many 
       assumption flips from the prompt), avoiding direct use in scoring 
       to prevent historical inhibition patterns.
    """

    def __init__(self):
        # Critical threshold for the phase transition (bifurcation point)
        self.lambda_c = 0.65 
        # Precision parameter controlling the sharpness of the transition
        self.precision = 4.0 

    def _structural_parse(self, text: str) -> dict:
        """Extract structural logic features: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without|unless)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|else|unless|provided)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|best|worst)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text_lower),
            'length': len(text.split())
        }
        return features

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Calculate Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        c1 = len(zlib.compress(s1_bytes))
        c2 = len(zlib.compress(s2_bytes))
        c12 = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _evaluate_logic_consistency(self, prompt: str, candidate: str) -> float:
        """
        Core FEP Engine: Computes a score based on structural alignment.
        Minimizes 'free energy' by rewarding structural matches and penalizing contradictions.
        """
        p_feat = self._structural_parse(prompt)
        c_feat = self._structural_parse(candidate)
        
        score = 0.0
        total_weight = 0.0

        # 1. Negation Consistency (Modus Tollens check proxy)
        # If prompt has negation, candidate should reflect understanding (simplified heuristic)
        if p_feat['negations'] > 0:
            weight = 2.0
            total_weight += weight
            # Reward if candidate also handles negation context or explicitly resolves it
            if c_feat['negations'] > 0 or (len(c_feat['numbers']) > 0 and len(p_feat['numbers']) > 0):
                score += weight * 1.0
            else:
                # Penalty for ignoring negation context (high free energy)
                score -= weight * 0.5

        # 2. Conditional Logic
        if p_feat['conditionals'] > 0:
            weight = 1.5
            total_weight += weight
            if c_feat['conditionals'] > 0 or any(k in candidate.lower() for k in ['therefore', 'thus', 'so', 'result']):
                score += weight * 1.0
            else:
                score += weight * 0.2 # Partial credit

        # 3. Numeric Evaluation
        if p_feat['numbers'] and c_feat['numbers']:
            weight = 2.5
            total_weight += weight
            try:
                p_nums = [float(x) for x in p_feat['numbers']]
                c_nums = [float(x) for x in c_feat['numbers']]
                
                # Check for direct number presence (often the answer)
                if any(abs(c - p_nums[0]) < 1e-6 for c in c_nums):
                    score += weight * 1.5 # Bonus for extracting correct number
                elif len(c_nums) == len(p_nums):
                     score += weight * 0.8 # Structural match in count
                else:
                    score += weight * 0.1
            except ValueError:
                pass

        # 4. Length/Complexity Match (Occam's razor proxy)
        len_ratio = min(len(c_feat['length']), len(p_feat['length'])) / (max(len(c_feat['length']), 1) + 1)
        score += len_ratio * 0.5
        total_weight += 0.5

        # Normalize score to roughly 0-1 range before phase transition
        base_score = score / (total_weight + 1e-6)
        return min(1.0, max(0.0, base_score))

    def _phase_transition_score(self, base_score: float) -> float:
        """
        Applies the Critical Phase Transition.
        Uses a sigmoid-like function centered at lambda_c to simulate the 
        discontinuous jump from uncertainty to belief.
        """
        # Distance from critical point
        delta = base_score - self.lambda_c
        
        # Critical slowing down / Bifurcation function
        # If near 0 (critical point), small changes in base_score cause large shifts
        # The precision parameter controls the steepness of the transition
        transitioned_score = 1.0 / (1.0 + math.exp(-self.precision * delta))
        
        return transitioned_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate NCD for all candidates to use as tiebreaker
        candidate_scores = []
        for cand in candidates:
            logic_score = self._evaluate_logic_consistency(prompt, cand)
            phase_score = self._phase_transition_score(logic_score)
            ncd_val = self._compute_ncd(prompt, cand)
            candidate_scores.append((cand, logic_score, phase_score, ncd_val))

        # Ranking logic:
        # Primary: Phase-transitioned score (FEP + Phase Transition synergy)
        # Tiebreaker: NCD (lower is better similarity/compression)
        
        # Sort by phase_score desc, then ncd asc
        candidate_scores.sort(key=lambda x: (-x[2], x[3]))

        for cand, logic, phase, ncd in candidate_scores:
            results.append({
                "candidate": cand,
                "score": round(phase, 4),
                "reasoning": f"FEP-Logic:{logic:.2f} -> Critical-Phase:{phase:.2f} (NCD:{ncd:.2f})"
            })
            
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses Optimal Control concept strictly as a 'control cost' wrapper.
        High control cost (many assumption flips) reduces confidence.
        """
        # Base evaluation
        logic_score = self._evaluate_logic_consistency(prompt, answer)
        phase_score = self._phase_transition_score(logic_score)
        
        # Optimal Control Wrapper: Estimate 'Control Effort' (u)
        # Heuristic: If the answer length diverges significantly from prompt expectation
        # or if structural features mismatch heavily, control effort is high.
        p_feat = self._structural_parse(prompt)
        a_feat = self._structural_parse(answer)
        
        # Control cost lambda * ||u||^2 approximation
        # Penalize large deviations in structural feature counts
        neg_diff = abs(p_feat['negations'] - a_feat['negations'])
        cond_diff = abs(p_feat['conditionals'] - a_feat['conditionals'])
        
        # Control effort penalty (simulating the minimization of J in the prompt)
        control_effort = 0.1 * (neg_diff + cond_diff) 
        if len(answer.split()) > len(prompt.split()) * 2:
            control_effort += 0.2 # Penalty for excessive verbosity (high energy)
            
        # Apply control cost to the phase score
        # Confidence = PhaseScore * exp(-control_cost)
        # This ensures we don't use Optimal Control for direct scoring, 
        # but only to modulate confidence based on 'effort'
        final_confidence = phase_score * math.exp(-control_effort)
        
        return round(min(1.0, max(0.0, final_confidence)), 4)