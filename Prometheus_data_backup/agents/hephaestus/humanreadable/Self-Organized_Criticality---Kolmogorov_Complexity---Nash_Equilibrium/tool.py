import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Critical-Complexity Game Learner (Approximated).
    
    Mechanism:
    1. Structural Parsing (The Tester): Extracts logical constraints (negations, comparatives, 
       conditionals, numeric relations) from the prompt. This acts as the 'falsification' pressure.
    2. SOC-inspired Perturbation (The Generator): Instead of random noise, we simulate the 
       'avalanche' by evaluating candidates against a hierarchy of structural rules. Small 
       deviations (missing a keyword) yield small penalties; large logical contradictions 
       (violating a numeric constraint) trigger 'avalanche' rejections.
    3. Kolmogorov Complexity (The Penalty): We approximate KC via zlib compression length. 
       Candidates that are overly verbose relative to their content are penalized (Occam's razor).
    4. Nash Equilibrium: The final score balances passing the structural tests (survival) 
       with minimizing description length (simplicity). The system 'settles' on candidates 
       that satisfy constraints with minimal complexity.
       
    This approach prioritizes structural logic (beating the baseline) while using NCD only 
    as a tiebreaker or secondary filter, adhering to the causal intelligence constraints.
    """

    def __init__(self):
        # Precompile regex patterns for structural parsing (The Tester's strategies)
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|fail|false)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|when|whenever)\b', re.I),
            'numeric': re.compile(r'\d+(\.\d+)?'),
            'logic_op': re.compile(r'\b(and|or|but|however|therefore|thus)\b', re.I)
        }

    def _get_ncd_length(self, text: str) -> int:
        """Approximate Kolmogorov Complexity using zlib compression length."""
        if not text:
            return 0
        return len(zlib.compress(text.encode('utf-8')))

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Parse text for logical structures (The Tester's move)."""
        lower_text = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(lower_text)),
            'has_comparative': bool(self.patterns['comparative'].search(lower_text)),
            'has_conditional': bool(self.patterns['conditional'].search(lower_text)),
            'numbers': [float(x) for x in self.patterns['numeric'].findall(text)],
            'word_count': len(text.split()),
            'raw': text
        }
        return features

    def _check_logical_consistency(self, prompt_feats: Dict, cand_feats: Dict, candidate: str) -> float:
        """
        Evaluate candidate against prompt constraints.
        Returns a penalty score (0.0 = perfect, >0.0 = violation).
        Simulates the SOC avalanche: small errors add up, logical contradictions cause large drops.
        """
        penalty = 0.0
        
        # 1. Negation Consistency (Modus Tollens check approximation)
        # If prompt has negation, candidate should ideally reflect awareness or not contradict it blindly
        if prompt_feats['has_negation']:
            # Heuristic: If prompt negates X, and candidate asserts X strongly without qualification
            # We check for simple contradiction patterns (simplified for this scope)
            if cand_feats['has_negation'] != prompt_feats['has_negation']:
                # Soft penalty for mismatched negation density, simulating a small perturbation
                penalty += 0.1 

        # 2. Numeric Consistency (Transitivity/Comparison)
        if prompt_feats['numbers'] and cand_feats['numbers']:
            # Check if candidate numbers are wildly off or nonsensical compared to prompt scale
            # This is a crude approximation of numeric reasoning
            p_max = max(prompt_feats['numbers']) if prompt_feats['numbers'] else 0
            c_max = max(cand_feats['numbers']) if cand_feats['numbers'] else 0
            
            # If prompt implies a range and candidate violates it (heuristic)
            if p_max > 0 and c_max > p_max * 10: 
                penalty += 0.5 # Large penalty for magnitude errors

        # 3. Structural Overlap (Constraint Propagation)
        # Candidate must share logical operators to be considered relevant
        prompt_ops = set(re.findall(r'\b(and|or|but|if|then|not)\b', prompt_feats['raw'].lower()))
        cand_ops = set(re.findall(r'\b(and|or|but|if|then|not)\b', cand_feats['raw'].lower()))
        
        if prompt_ops and not prompt_ops.intersection(cand_ops):
            # If prompt has logic ops and candidate has none, it's likely a non-reasoning echo
            penalty += 0.2

        return penalty

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_structure(prompt)
        results = []

        for cand in candidates:
            cand_feats = self._extract_structure(cand)
            
            # 1. Structural Score (The Tester)
            # Higher is better. Base score 1.0, subtract penalties.
            logic_penalty = self._check_logical_consistency(prompt_feats, cand_feats, cand)
            structural_score = max(0.0, 1.0 - logic_penalty)
            
            # 2. Complexity Penalty (Kolmogorov)
            # Prefer shorter descriptions that convey same info. 
            # We normalize by prompt length to avoid penalizing long answers to complex questions unfairly.
            cand_kc = self._get_ncd_length(cand)
            prompt_kc = self._get_ncd_length(prompt)
            
            # Ideal complexity ratio (heuristic): Answer should be proportional to prompt complexity
            # Too short (0.5 ratio) or too long (2.0 ratio) gets penalized slightly
            ratio = cand_kc / (prompt_kc + 1)
            complexity_penalty = 0.0
            if ratio < 0.2: # Too brief, likely missing info
                complexity_penalty = 0.1
            elif ratio > 3.0: # Too verbose, likely noise
                complexity_penalty = 0.2
                
            # 3. NCD Similarity (Tiebreaker only)
            # Used only to distinguish between structurally identical candidates
            combined = f"{prompt} {cand}"
            ncd_val = (self._get_ncd_length(combined) - min(self._get_ncd_length(prompt), self._get_ncd_length(cand))) / max(self._get_ncd_length(prompt), self._get_ncd_length(cand), 1)
            ncd_score = 1.0 - ncd_val # Higher is more similar

            # Final Score: Structural integrity is primary (90%), Complexity/NCD secondary (10%)
            # This ensures we beat the NCD baseline by prioritizing logic
            final_score = (structural_score * 0.9) + ((1.0 - complexity_penalty) * 0.1) + (ncd_score * 0.05)
            
            # Reasoning string generation
            reason_parts = []
            if logic_penalty > 0:
                reason_parts.append(f"Logical mismatch detected (penalty: {logic_penalty:.2f})")
            if complexity_penalty > 0:
                reason_parts.append(f"Complexity deviation (penalty: {complexity_penalty:.2f})")
            if not reason_parts:
                reason_parts.append("Structurally consistent and concise")
                
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": "; ".join(reason_parts)
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment and complexity.
        """
        # Reuse evaluation logic for single pair
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        score = res[0]['score']
        
        # Map score to confidence: 
        # High structural score + low penalty -> High confidence
        # The evaluation already penalized logical flaws heavily.
        confidence_val = min(1.0, max(0.0, score))
        
        return round(confidence_val, 4)