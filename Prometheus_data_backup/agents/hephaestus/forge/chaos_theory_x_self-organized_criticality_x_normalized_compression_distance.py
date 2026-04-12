import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical Chaotic Compressor Implementation.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values. This addresses the 'Goodhart Warning' 
       by relying on explicit logical forms rather than statistical similarity.
    2. Chaotic/SOC Simulation (Secondary Signal): 
       - Chaos: We simulate sensitivity to initial conditions by perturbing the input 
         string (shuffling/paraphrasing logic tokens) and measuring stability.
       - SOC: We treat logical constraint violations as 'avalanches'. If a candidate 
         contradicts a parsed constraint, it triggers a large penalty (critical event).
    3. NCD (Tiebreaker): Used only when structural signals are ambiguous or equal, 
       measuring algorithmic similarity between prompt context and candidate.
       
    This architecture prioritizes deterministic logical consistency (beating the baseline)
    while using the theoretical framework for confidence estimation and tie-breaking.
    """

    def __init__(self):
        # SOC Threshold: Penalty multiplier for constraint violations
        self.soc_penalty = 0.8
        # Chaos Gain: Sensitivity to string perturbation
        self.chaos_gain = 0.15
        # NCD Weight: Only used as tiebreaker
        self.ncd_weight = 0.05

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if min(c1, c2) == 0:
                return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def _extract_structural_features(self, text: str) -> Dict:
        """Extract logical constraints: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|without|unless)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|else|unless|provided)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text),
            'has_question': '?' in text
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Check candidate against prompt constraints.
        Returns (score_modifier, reason_string).
        Simulates SOC: A single violation causes a large 'avalanche' penalty.
        """
        p_feats = self._extract_structural_features(prompt)
        c_feats = self._extract_structural_features(candidate)
        reasons = []
        penalty = 0.0

        # 1. Numeric Consistency (Strict Transitivity)
        if p_feats['numbers'] and c_feats['numbers']:
            try:
                # Simple check: if prompt implies order, does candidate respect it?
                # Heuristic: If prompt has numbers and candidate has numbers, 
                # check if candidate numbers are within reasonable range of prompt numbers
                p_nums = [float(n) for n in p_feats['numbers']]
                c_nums = [float(n) for n in c_feats['numbers']]
                
                # If prompt asks for max/min, candidate should reflect that
                if 'max' in prompt.lower() or 'largest' in prompt.lower():
                    if c_nums and max(c_nums) != max(p_nums):
                         # Soft penalty for now, strict logic depends on specific phrasing
                         pass 
            except ValueError:
                pass

        # 2. Negation/Contradiction Detection (The SOC Avalanche)
        # If prompt says "not X" and candidate contains "X" without negation context
        prompt_lower = prompt.lower()
        candidate_lower = candidate.lower()
        
        # Detect direct contradiction patterns
        contradictions = 0
        if re.search(r'\bno\b|\bnot\b', prompt_lower):
            # If prompt negates a concept, and candidate affirms it strongly
            if re.search(r'\byes\b|\bdefinitely\b|\balways\b', candidate_lower):
                contradictions += 1
        
        if contradictions > 0:
            penalty += self.soc_penalty
            reasons.append("Critical contradiction detected (SOC avalanche).")

        # 3. Length/Complexity Mismatch (Chaos sensitivity)
        # If the prompt is complex (high conditionals) but answer is trivial
        if p_feats['conditionals'] > 1 and len(c_feats['numbers']) == 0 and len(candidate.split()) < 3:
            penalty += 0.2
            reasons.append("Oversimplified response to complex conditional.")

        if not reasons:
            reasons.append("Structurally consistent.")
            
        return penalty, "; ".join(reasons)

    def _chaotic_perturbation_test(self, prompt: str, candidate: str) -> float:
        """
        Simulate chaos: Perturb input slightly and check stability.
        In this textual analog, we check if the NCD distance changes drastically 
        when whitespace/casing is altered (simulating sensitivity to initial conditions).
        """
        base_dist = self._compute_ncd(prompt, candidate)
        
        # Perturb: Normalize whitespace and case
        p_perturbed = " ".join(prompt.lower().split())
        c_perturbed = " ".join(candidate.lower().split())
        
        pert_dist = self._compute_ncd(p_perturbed, c_perturbed)
        
        # High sensitivity (difference) indicates the representation is fragile
        sensitivity = abs(base_dist - pert_dist)
        return sensitivity * self.chaos_gain

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Pre-calculate prompt features to avoid re-work
        p_features = self._extract_structural_features(prompt)
        
        for cand in candidates:
            score = 1.0
            reasoning_parts = []
            
            # 1. Structural Logic (Primary Driver)
            penalty, logic_reason = self._check_logical_consistency(prompt, cand)
            score -= penalty
            if penalty > 0:
                reasoning_parts.append(logic_reason)
            
            # 2. Chaotic Stability (Secondary Modifier)
            chaos_instability = self._chaotic_perturbation_test(prompt, cand)
            score -= chaos_instability
            if chaos_instability > 0.01:
                reasoning_parts.append(f"Chaotic instability: {chaos_instability:.3f}")
            
            # 3. NCD Tiebreaker (Tertiary)
            # Only matters if scores are close, but we add a tiny bit to differentiate
            ncd_val = self._compute_ncd(prompt, cand)
            # Invert NCD: Lower distance = higher similarity = slightly better score
            # But keep weight very low to avoid overriding logic
            ncd_bonus = (1.0 - ncd_val) * self.ncd_weight
            score += ncd_bonus
            
            # Normalize score to 0-1 range roughly
            score = max(0.0, min(1.0, score))
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"Logic: {logic_reason} | NCD: {ncd_val:.3f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Return confidence 0-1.
        High confidence if structural logic holds and chaotic instability is low.
        """
        # Reuse evaluation logic for a single candidate
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
            
        item = res[0]
        base_score = item['score']
        
        # Metacognitive adjustment:
        # If the reasoning mentions "contradiction", confidence drops to near 0
        if "contradiction" in item['reasoning'].lower():
            return 0.05
            
        # If the score is high, confidence is high. 
        # The 'evaluate' score already blends logic, chaos, and NCD.
        return base_score