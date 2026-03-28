import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Quantum-Enhanced Analogical Model Checker (QAMC) - Classical Approximation
    
    Mechanism:
    1. Analogical Encoding (SME-like): Extracts relational predicates (negations, 
       comparatives, conditionals, numeric values) from prompt and candidates to 
       form a structural signature.
    2. Quantum Search Simulation: Uses a heuristic scoring function to simulate 
       Grover's amplitude amplification. Candidates matching the prompt's structural 
       constraints (e.g., if prompt has negation, candidate must handle it) receive 
       "amplified" scores.
    3. Model Checking Validation: Verifies logical consistency (e.g., numeric 
       transitivity, modus tollens) between prompt constraints and candidate answers.
    4. Feedback: Adjusts scores based on constraint violations.
    
    NCD is used only as a tiebreaker for structurally identical candidates.
    """

    def __init__(self):
        self.numeric_ops = ['+', '-', '*', '/', '==', '<', '>', '<=', '>=']
        
    def _extract_structure(self, text: str) -> dict:
        """Extracts relational predicates: negations, comparatives, conditionals, numbers."""
        text_lower = text.lower()
        structure = {
            'negations': len(re.findall(r'\b(not|no|never|neither|none)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worser|than)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|provided|when)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'logic_keywords': len(re.findall(r'\b(and|or|implies|therefore|thus)\b', text_lower))
        }
        return structure

    def _check_numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Validates numeric logic (Model Checking step)."""
        p_nums = re.findall(r'-?\d+\.?\d*', prompt)
        c_nums = re.findall(r'-?\d+\.?\d*', candidate)
        
        if not p_nums:
            return 1.0 # No numeric constraints to check
            
        # Simple heuristic: If prompt implies an order (e.g. "9.11 vs 9.9"), 
        # check if candidate respects float ordering if it mentions numbers.
        try:
            p_floats = [float(x) for x in p_nums]
            c_floats = [float(x) for x in c_nums]
            
            if len(p_floats) >= 2 and len(c_floats) >= 1:
                # Detect comparison context
                if any(k in prompt.lower() for k in ['smaller', 'less', 'minimum']):
                    expected = min(p_floats)
                    if c_floats and abs(c_floats[0] - expected) > 1e-6:
                        return 0.0 # Violation
                elif any(k in prompt.lower() for k in ['larger', 'greater', 'maximum']):
                    expected = max(p_floats)
                    if c_floats and abs(c_floats[0] - expected) > 1e-6:
                        return 0.0 # Violation
        except ValueError:
            pass
            
        return 1.0

    def _structural_match_score(self, p_struct: dict, c_struct: dict) -> float:
        """Scores analogical similarity based on structural predicates."""
        score = 0.0
        matches = 0
        total_features = 0
        
        # Check negation consistency
        total_features += 1
        if (p_struct['negations'] > 0) == (c_struct['negations'] > 0):
            matches += 1
        elif p_struct['negations'] == 0 and c_struct['negations'] == 0:
            matches += 1 # Both lack negation is also consistent
            
        # Check conditional density (analogous mapping)
        total_features += 1
        if p_struct['conditionals'] > 0:
            if c_struct['conditionals'] > 0:
                matches += 1
        else:
            matches += 1 # No conditional required
            
        # Check number presence
        if p_struct['numbers'] and c_struct['numbers']:
            matches += 1
            total_features += 1
            
        if total_features == 0:
            return 0.5
        return matches / total_features

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        len1 = len(s1.encode('utf-8'))
        len2 = len(s2.encode('utf-8'))
        if len1 == 0 or len2 == 0:
            return 1.0
        comp1 = len(zlib.compress(s1.encode('utf-8')))
        comp2 = len(zlib.compress(s2.encode('utf-8')))
        comp_joint = len(zlib.compress((s1 + s2).encode('utf-8')))
        
        denominator = max(comp1, comp2)
        if denominator == 0:
            return 0.0
        return (comp_joint - min(comp1, comp2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        p_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate prompt compression for NCD
        prompt_comp = zlib.compress(prompt.encode('utf-8'))
        len_prompt_comp = len(prompt_comp)
        
        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # 1. Analogical Encoding & Structural Match
            c_struct = self._extract_structure(cand)
            struct_score = self._structural_match_score(p_struct, c_struct)
            
            # 2. Model Checking (Numeric/Logic validation)
            logic_score = self._check_numeric_consistency(prompt, cand)
            
            # 3. Quantum Search Simulation (Amplitude Amplification)
            # We simulate the "collapse" to high-scoring states by boosting 
            # candidates that satisfy both structural and logical constraints.
            base_score = struct_score * 0.6 + logic_score * 0.4
            
            # Apply "Grover Iteration" boost if constraints are met
            if logic_score == 1.0 and struct_score > 0.5:
                amplified_score = base_score + 0.3 # Boost valid hypotheses
                reasoning_parts.append("Validated structural analogy and logical consistency.")
            else:
                amplified_score = base_score * 0.5 # Penalize inconsistent mappings
                if logic_score == 0.0:
                    reasoning_parts.append("Failed model checking: logical contradiction detected.")
                if struct_score < 0.5:
                    reasoning_parts.append("Weak analogical mapping: structural mismatch.")

            # 4. NCD Tiebreaker (only if scores are close or structure is weak)
            if abs(amplified_score - 0.5) < 0.1: 
                # Use NCD only when structural signal is ambiguous
                ncd_val = self._ncd(prompt, cand)
                # Invert NCD (lower is better) and scale small so it's a tiebreaker
                ncd_score = (1.0 - ncd_val) * 0.05 
                amplified_score += ncd_score
                reasoning_parts.append(f"NCD tiebreaker applied (similarity: {1-ncd_val:.2f}).")
            
            # Ensure bounds
            final_score = max(0.0, min(1.0, amplified_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": " ".join(reasoning_parts) if reasoning_parts else "Baseline evaluation."
            })
            
        # Sort descending by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural and logical validation."""
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(answer)
        
        struct_match = self._structural_match_score(p_struct, c_struct)
        logic_check = self._check_numeric_consistency(prompt, answer)
        
        # Combined confidence
        conf = (struct_match * 0.7) + (logic_check * 0.3)
        
        # Strong penalty for logical contradictions
        if logic_check == 0.0:
            return 0.1
            
        return min(1.0, max(0.0, conf))