import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Thermodynamic Symbiotic Type-Checker (TSTC) Approximation.
    
    Mechanism:
    1. Structural Parsing (The Proof-Producer): Extracts logical constraints 
       (negations, comparatives, conditionals) to form a 'type skeleton'.
    2. Energy Calculation (The Resource-Regulator): 
       - Candidates are evaluated against the skeleton.
       - Violations (e.g., missing negation, wrong comparative direction) add 'Energy Cost'.
       - Semantic consistency (via NCD) acts as the 'Entropy' term.
    3. Symbiotic Loop: The final score is a Free Energy minimization where 
       low logical cost and high compression similarity yield high scores.
       
    This implements the 'Thermodynamics' and 'Type Theory' concepts as primary 
    scoring drivers (structural logic), while restricting 'Symbiosis' to the 
    confidence wrapper and internal state management to avoid historical inhibitors.
    """

    def __init__(self):
        # Patterns for structural extraction (Type constraints)
        self.negation_pattern = re.compile(r'\b(not|no|never|neither|without)\b', re.IGNORECASE)
        self.comparative_pattern = re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE)
        self.conditional_pattern = re.compile(r'\b(if|then|unless|provided)\b', re.IGNORECASE)
        self.number_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_structure(self, text: str) -> Dict:
        """Extracts logical 'types' from text: negations, comparatives, numbers."""
        return {
            'has_negation': bool(self.negation_pattern.search(text)),
            'has_comparative': bool(self.comparative_pattern.search(text)),
            'has_conditional': bool(self.conditional_pattern.search(text)),
            'numbers': [float(n) for n in self.number_pattern.findall(text)],
            'length': len(text.split())
        }

    def _check_logical_consistency(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Calculates 'Energy Cost' based on logical violations.
        Lower cost = higher plausibility.
        """
        cost = 0.0
        
        # Constraint 1: Negation Preservation
        # If prompt asserts a negative constraint, candidate should likely reflect it or not contradict it
        if prompt_struct['has_negation'] and not cand_struct['has_negation']:
            # Heuristic: Check if the candidate explicitly contradicts the negation context
            # Simple approximation: if prompt has 'not' and candidate lacks it, slight penalty unless candidate is very short
            if cand_struct['length'] > 3: 
                cost += 0.2
        
        # Constraint 2: Comparative Direction (Numeric)
        # If prompt has numbers and comparatives, check candidate numbers
        if prompt_struct['has_comparative'] and prompt_struct['numbers'] and cand_struct['numbers']:
            p_max = max(prompt_struct['numbers'])
            c_max = max(cand_struct['numbers'])
            
            # Heuristic: If prompt implies "greater", candidate number should arguably be significant
            # This is a rough approximation of type-checking numeric relations
            if 'greater' in prompt.lower() or 'more' in prompt.lower():
                if c_max < p_max:
                    cost += 0.3
            elif 'less' in prompt.lower() or 'smaller' in prompt.lower():
                if c_max > p_max:
                    cost += 0.3

        # Constraint 3: Conditional Presence
        if prompt_struct['has_conditional'] and not cand_struct['has_conditional']:
            # If prompt is conditional, a valid answer often needs to handle the condition
            # Penalize absolute statements if prompt is conditional
            if cand_struct['length'] > 5:
                cost += 0.1

        return cost

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            denominator = max(c1, c2)
            if denominator == 0:
                return 0.0
            return (c12 - min(c1, c2)) / denominator
        except Exception:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate prompt entropy baseline (self-similarity)
        # In a full TSTC, this would be dynamic. Here we use it to normalize NCD.
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # 1. Logical Work (Energy Cost)
            logical_cost = self._check_logical_consistency(prompt_struct, cand_struct, prompt, cand)
            
            # 2. Entropy (NCD based uncertainty)
            # Lower NCD means candidate is "close" to prompt context (high similarity)
            entropy = self._ncd(prompt, cand)
            
            # 3. Free Energy Calculation (F = E - TS)
            # We invert logic: We want Low Cost and Low Entropy (high similarity/relevance)
            # Score = 1.0 - (weighted_cost + weighted_entropy)
            # Weights tuned to prioritize structural logic (Type Theory) over raw string match
            
            # Normalize cost impact (max expected cost ~0.6)
            normalized_cost = min(logical_cost, 1.0)
            
            # Free Energy heuristic: 
            # High structural match (low cost) + High semantic match (low NCD) = High Score
            raw_score = 1.0 - (0.6 * normalized_cost + 0.4 * entropy)
            
            # Symbiotic adjustment: If logical cost is 0, boost slightly (reward for perfect type check)
            if logical_cost < 0.05:
                raw_score = min(raw_score + 0.05, 1.0)
                
            results.append({
                "candidate": cand,
                "score": max(0.0, min(1.0, raw_score)), # Clamp 0-1
                "reasoning": f"Logical Cost: {logical_cost:.2f}, Entropy: {entropy:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing as primary signal, NCD as tiebreaker.
        Symbiosis concept restricted to this wrapper (monitoring state).
        """
        if not answer:
            return 0.0
            
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        # Base confidence on structural alignment
        conf = 0.5
        
        # Negation check
        if p_struct['has_negation'] == a_struct['has_negation']:
            conf += 0.2
        else:
            conf -= 0.2
            
        # Number presence check
        if p_struct['numbers']:
            if a_struct['numbers']:
                conf += 0.1
            else:
                conf -= 0.1
                
        # NCD Tiebreaker/Validator
        ncd_val = self._ncd(prompt, answer)
        if ncd_val < 0.6: # Reasonable similarity
            conf += 0.1
        else:
            conf -= 0.1
            
        return max(0.0, min(1.0, conf))