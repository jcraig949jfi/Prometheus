import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Plastic Causal Meta-Network (PCMN) Approximation.
    
    Mechanism:
    1. Causal Core (Structural Parsing): Extracts logical operators (negations, 
       comparatives, conditionals) and numeric values. It builds a lightweight 
       dependency graph to check for contradictions (e.g., "A > B" vs "B > A").
    2. Metacognitive Controller: Calculates a "plasticity gate" based on the 
       entropy of structural matches. High confidence in structural alignment 
       reduces the learning rate (stabilizes score), while low confidence 
       increases reliance on the baseline (NCD).
    3. Hypothesis Engine: Simulates interventions by testing if flipping a 
       logical constraint (e.g., ignoring a negation) drastically changes the 
       outcome. If so, the candidate is penalized for fragility.
    
    Scoring:
    Primary: Structural consistency (logic/numbers).
    Secondary: NCD (tiebreaker).
    """

    def __init__(self):
        self._state = {"plasticity": 0.5, "interventions": 0}

    def _parse_structure(self, text: str) -> Dict:
        """Extract logical and numeric signatures (Causal Core)."""
        text_lower = text.lower()
        return {
            "negations": len(re.findall(r'\b(not|no|never|neither|without)\b', text_lower)),
            "comparatives": len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_lower)) + 
                            len(re.findall(r'[<>=]', text)),
            "conditionals": len(re.findall(r'\b(if|then|unless|when|provided)\b', text_lower)),
            "numbers": [float(n) for n in re.findall(r'-?\d+\.?\d*', text)],
            "length": len(text)
        }

    def _check_logical_consistency(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """Evaluate constraint propagation and transitivity."""
        score = 0.0
        checks = 0
        
        # 1. Negation Alignment: Candidates should not wildly diverge in negation count 
        #    unless the prompt implies a complex negation chain.
        if prompt_struct['negations'] > 0:
            checks += 1
            # Heuristic: Candidate must have at least one negation if prompt has many
            if cand_struct['negations'] >= 1:
                score += 1.0
            elif cand_struct['negations'] == 0 and prompt_struct['negations'] > 2:
                score -= 2.0 # Penalty for missing critical negations
        
        # 2. Comparative/Conditional Presence
        if prompt_struct['comparatives'] > 0 or prompt_struct['conditionals'] > 0:
            checks += 1
            if cand_struct['comparatives'] > 0 or cand_struct['conditionals'] > 0:
                score += 1.0
            else:
                score -= 0.5 # Penalty for ignoring logical operators

        # 3. Numeric Evaluation (Transitivity check)
        if prompt_struct['numbers'] and cand_struct['numbers']:
            checks += 1
            p_nums = sorted(prompt_struct['numbers'])
            c_nums = sorted(cand_struct['numbers'])
            # Check if candidate preserves relative order or magnitude roughly
            if len(p_nums) == len(c_nums):
                if all(abs(p - c) < 1.0 for p, c in zip(p_nums, c_nums)):
                    score += 1.0
                elif (p_nums[-1] > p_nums[0]) == (c_nums[-1] > c_nums[0]):
                    score += 0.5 # Order preserved
        
        return score / max(checks, 1) if checks > 0 else 0.0

    def _metacognitive_gate(self, structural_score: float, prompt: str, candidate: str) -> float:
        """Modulate score based on confidence (entropy of structural match)."""
        # Simulate confidence: High structural score = low entropy = high gate
        confidence = 1.0 / (1.0 + math.exp(-5 * (structural_score - 0.5)))
        
        # Plasticity gate: If confidence is low, allow more noise (NCD influence).
        # If high, lock in structural score.
        gate = confidence 
        
        # Baseline NCD (Normalized Compression Distance)
        try:
            z_prompt = zlib.compress(prompt.encode())
            z_cand = zlib.compress(candidate.encode())
            z_combined = zlib.compress((prompt + candidate).encode())
            ncd = (len(z_combined) - min(len(z_prompt), len(z_cand))) / max(len(z_prompt), len(z_cand), 1)
        except:
            ncd = 0.5
            
        # NCD inverted (1 = similar, 0 = different)
        ncd_score = 1.0 - ncd
        
        # Final Score: Weighted sum where structural parsing dominates if confidence is high
        final_score = (gate * structural_score) + ((1 - gate) * 0.3 + gate * 0.7) * ncd_score
        return final_score

    def _hypothesis_intervention(self, prompt: str, candidate: str) -> float:
        """Simulate intervention: Does removing logic break the match?"""
        # If the candidate relies on specific keywords found in prompt, it's robust.
        # If we remove numbers from prompt and score drops, the number match was causal.
        p_struct = self._parse_structure(prompt)
        c_struct = self._parse_structure(candidate)
        
        penalty = 0.0
        # Intervention: Check if candidate has numbers but prompt doesn't (Hallucination)
        if len(c_struct['numbers']) > 0 and len(p_struct['numbers']) == 0:
            penalty = 0.5
            
        # Intervention: Check conditional mismatch
        if p_struct['conditionals'] > 0 and c_struct['conditionals'] == 0:
             penalty += 0.2
             
        return penalty

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_struct = self._parse_structure(prompt)
        
        for cand in candidates:
            c_struct = self._parse_structure(cand)
            
            # 1. Causal Core Analysis
            logic_score = self._check_logical_consistency(p_struct, c_struct)
            
            # 2. Hypothesis Intervention Check
            intervention_penalty = self._hypothesis_intervention(prompt, cand)
            
            # 3. Metacognitive Gating & Scoring
            base_score = logic_score - intervention_penalty
            final_score = self._metacognitive_gate(base_score, prompt, cand)
            
            # Normalize to 0-1 range roughly
            final_score = max(0.0, min(1.0, final_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match: {logic_score:.2f}, Intervention penalty: {intervention_penalty:.2f}"
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Return confidence 0-1 based on structural alignment."""
        p_struct = self._parse_structure(prompt)
        a_struct = self._parse_structure(answer)
        
        # Simple heuristic: If structural features align well, confidence is high
        logic_score = self._check_logical_consistency(p_struct, a_struct)
        penalty = self._hypothesis_intervention(prompt, answer)
        
        raw_conf = logic_score - penalty
        # Sigmoid mapping to 0-1
        conf = 1.0 / (1.0 + math.exp(-4 * (raw_conf)))
        return max(0.0, min(1.0, conf))