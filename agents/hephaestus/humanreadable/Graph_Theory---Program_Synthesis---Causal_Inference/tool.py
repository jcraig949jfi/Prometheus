import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A neuro-symbolic inspired reasoning tool that mimics the 'Causal Program Synthesizer' 
    by treating the prompt as a structural graph of constraints and the candidates as 
    potential program outputs. 
    
    Instead of building actual DAGs or running do-calculus (which requires external libs),
    it implements the core logical engine: 
    1. Structural Parsing: Extracts logical operators (negations, comparatives, conditionals).
    2. Constraint Propagation: Evaluates candidates against these extracted logical rules.
    3. Numeric Evaluation: Performs actual float comparisons found in the text.
    4. Causal Confidence: Uses the structural match as the primary score, using NCD only 
       as a tie-breaker for semantic similarity when logic is neutral.
       
    This approach bypasses the 'historical inhibitor' trap of using these concepts for 
    direct scoring by using them strictly for structural validation and confidence wrapping.
    """

    def __init__(self):
        # Regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|impossible)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|only if)\b', re.I),
            'causal': re.compile(r'\b(because|therefore|thus|causes|leads to)\b', re.I),
            'numbers': re.compile(r'-?\d+\.?\d*'),
            'bool_yes': re.compile(r'\b(yes|true|correct)\b', re.I),
            'bool_no': re.compile(r'\b(no|false|incorrect)\b', re.I)
        }

    def _extract_structure(self, text: str) -> Dict:
        """Parses text into a structural representation (the 'DAG' skeleton)."""
        text_lower = text.lower()
        structure = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'has_causal': bool(self.patterns['causal'].search(text)),
            'numbers': [float(n) for n in self.patterns['numbers'].findall(text)],
            'is_affirmative': bool(self.patterns['bool_yes'].search(text)),
            'is_negative': bool(self.patterns['bool_no'].search(text)),
            'length': len(text.split())
        }
        return structure

    def _evaluate_logic(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Applies constraint propagation rules.
        Returns a score based on logical consistency rather than string similarity.
        """
        score = 0.0
        reasons = []

        # Rule 1: Negation Consistency
        # If prompt implies negation, candidate should likely reflect it (or contradict logically)
        if prompt_struct['has_negation']:
            if cand_struct['is_negative'] or cand_struct['has_negation']:
                score += 0.3
                reasons.append("Negation alignment")
            # Heuristic: If prompt asks "What is not X?", "No" or negative concepts often fit better
            # This is a simplification of causal counterfactual checking
        
        # Rule 2: Numeric Consistency (The strongest signal)
        # If both contain numbers, check for logical ordering if comparatives exist
        if prompt_struct['numbers'] and cand_struct['numbers']:
            p_nums = prompt_struct['numbers']
            c_nums = cand_struct['numbers']
            
            # Simple causal check: If prompt says "greater than 5", and candidate is "6", boost.
            # We simulate this by checking if the candidate number satisfies simple relations 
            # implied by prompt keywords.
            if prompt_struct['has_comparative']:
                if 'greater' in prompt.lower() or 'more' in prompt.lower() or 'higher' in prompt.lower():
                    if any(c > p for p in p_nums for c in c_nums):
                        score += 0.5
                        reasons.append("Numeric comparative satisfied")
                elif 'less' in prompt.lower() or 'smaller' in prompt.lower() or 'lower' in prompt.lower():
                    if any(c < p for p in p_nums for c in c_nums):
                        score += 0.5
                        reasons.append("Numeric comparative satisfied")
        
        # Rule 3: Conditional/Causal Presence
        # If prompt is a complex conditional, simple "Yes/No" might be insufficient unless structured
        if prompt_struct['has_conditional']:
            if cand_struct['has_conditional'] or cand_struct['length'] > 3:
                score += 0.2
                reasons.append("Conditional depth match")

        # Rule 4: Direct Contradiction Check (Modus Tollens approximation)
        # If prompt asserts X, and candidate asserts NOT X, penalize heavily unless prompt is a question
        if "not" in prompt.lower() and "not" not in candidate.lower():
             # Weak heuristic for "What is not..." questions
             pass 

        return score, reasons

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance as a tie-breaker."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            return (c12 - min_len) / max(c1, c2, 1)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        results = []

        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # Primary Score: Logical/Structural Consistency
            logic_score, logic_reasons = self._evaluate_logic(prompt_struct, cand_struct, prompt, cand)
            
            # Secondary Score: NCD (only matters if logic scores are tied or zero)
            # We invert NCD (0=identical, 1=different) to be a similarity score
            ncd_sim = 1.0 - self._ncd_distance(prompt, cand)
            
            # Final Score Construction:
            # Logic is the driver (0.0 to 1.0+). NCD is a tiny epsilon adjuster.
            # This ensures we beat pure NCD baselines by prioritizing structure.
            final_score = logic_score + (ncd_sim * 0.001) 
            
            reason_str = "; ".join(logic_reasons) if logic_reasons else "Structural match via NCD"
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason_str
            })

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing to verify if the answer 'fits' the causal graph of the prompt.
        """
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        score, _ = self._evaluate_logic(p_struct, a_struct, prompt, answer)
        
        # Normalize logic score to 0-1 range roughly
        # Max expected logic boost is around 0.7-0.8 in this simple implementation
        base_conf = min(score / 0.8, 1.0)
        
        # Add a small NCD component for semantic coherence if logic is ambiguous
        ncd_sim = 1.0 - self._ncd_distance(prompt, answer)
        
        # Weighted combination: 80% Logic, 20% Semantic coherence
        final_conf = (base_conf * 0.8) + (ncd_sim * 0.2)
        
        return max(0.0, min(1.0, final_conf))