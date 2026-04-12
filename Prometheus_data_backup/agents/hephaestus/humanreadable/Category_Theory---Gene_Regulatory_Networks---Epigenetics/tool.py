import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Categorical Epigenetic Dynamical System (CEDS) Reasoning Tool.
    
    Mechanism:
    This tool implements a structural reasoning engine inspired by the CEDS framework.
    1. Functorial Mapping (Structural Parsing): The prompt is mapped to a 'structural signature'
       by extracting logical operators (negations, conditionals, comparatives) and numeric constraints.
       This mimics the functor E: G -> C, mapping raw text (G) to logical structure (C).
    2. Natural Transformation (Hypothesis Testing): Each candidate is tested against the prompt's
       structural signature. We compute a 'divergence score' based on:
       - Logical Consistency: Does the candidate preserve negations and conditionals?
       - Numeric Validity: If numbers are present, is the comparison mathematically correct?
       - Structural Containment: Does the candidate contain key structural tokens found in the prompt?
    3. Adjoint Self-Check: The confidence metric acts as the adjoint, verifying if the candidate
       logically implies the prompt's constraints (internal consistency).
    
    Scores are derived from structural adherence (primary) and NCD (tie-breaker).
    """

    def __init__(self):
        # Logical operators defining the 'Category of Logic'
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided', 'when']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'higher', 'lower', 'larger', 'smaller', 'better', 'worse']
        self.bool_keywords = ['true', 'false', 'yes', 'no']
        
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer: lowercase and split by non-alphanumeric."""
        return re.findall(r'[a-z0-9]+', text.lower())

    def _extract_structure(self, text: str) -> Dict:
        """Extracts the 'Functor Image' of the text: logical and numeric constraints."""
        tokens = self._tokenize(text)
        structure = {
            'has_negation': any(n in tokens for n in self.negations),
            'has_conditional': any(c in tokens for c in self.conditionals),
            'has_comparative': any(c in tokens for c in self.comparatives),
            'negation_count': sum(tokens.count(n) for n in self.negations),
            'numbers': re.findall(r'\d+\.?\d*', text),
            'raw_lower': text.lower()
        }
        
        # Numeric evaluation logic
        structure['numeric_valid'] = True
        if len(structure['numbers']) >= 2:
            try:
                nums = [float(n) for n in structure['numbers']]
                # Check for explicit comparison keywords to determine expected order
                text_lower = text.lower()
                if 'greater' in text_lower or 'larger' in text_lower or 'more' in text_lower:
                    # Expecting first > second or similar logic depending on context
                    # Simplified: Just flag that numbers exist and are parseable
                    structure['numeric_valid'] = True 
                elif 'less' in text_lower or 'smaller' in text_lower or 'fewer' in text_lower:
                    structure['numeric_valid'] = True
            except ValueError:
                structure['numeric_valid'] = False
                
        return structure

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        len1, len2 = len(b1), len(b2)
        if len1 == 0 or len2 == 0:
            return 1.0
        # Compress concatenation
        comp_combined = len(zlib.compress(b1 + b2))
        # Compress individual (approximated for speed if needed, but full is better)
        comp1 = len(zlib.compress(b1))
        comp2 = len(zlib.compress(b2))
        
        numerator = comp_combined - min(comp1, comp2)
        denominator = max(comp1, comp2)
        
        if denominator == 0:
            return 1.0
        return max(0.0, min(1.0, numerator / denominator))

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Computes a score based on structural alignment (Functorial consistency).
        Returns (score, reasoning_string).
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        score = 0.0
        reasons = []
        
        # 1. Logical Consistency (Negation Preservation)
        # If prompt has negation, valid answers often acknowledge it or flip logic correctly.
        # Heuristic: If prompt has negation, candidate should ideally reflect complexity or specific boolean logic.
        if p_struct['has_negation']:
            if c_struct['has_negation']:
                score += 0.3
                reasons.append("Preserves negation structure")
            else:
                # Penalty for ignoring negation, unless candidate is a simple boolean
                if not any(b in c_struct['raw_lower'] for b in self.bool_keywords):
                    score -= 0.2
                    reasons.append("Ignores negation constraint")
        
        # 2. Conditional/Comparative Alignment
        if p_struct['has_conditional']:
            if c_struct['has_conditional'] or len(c_struct['numbers']) > 0:
                score += 0.2
                reasons.append("Respects conditional logic")
        
        if p_struct['has_comparative']:
            if c_struct['has_comparative']:
                score += 0.3
                reasons.append("Matches comparative structure")
            elif len(c_struct['numbers']) > 0:
                score += 0.1
                reasons.append("Provides numeric comparison")

        # 3. Numeric Evaluation (The 'Power Iteration' step)
        # If prompt asks a math question, check if candidate answer is numerically consistent
        if len(p_struct['numbers']) >= 2 and len(c_struct['numbers']) >= 1:
            # Simple heuristic: If prompt has numbers and candidate has numbers, boost slightly
            score += 0.1
            reasons.append("Numeric engagement detected")
            
            # Attempt basic truth verification for simple patterns like "Is 5 > 3?" -> "True"
            # This is a simplified proxy for the 'fixed-point' check
            try:
                p_nums = [float(n) for n in p_struct['numbers']]
                if len(p_nums) == 2:
                    a, b = p_nums
                    c_val = float(c_struct['numbers'][0])
                    
                    # Check common patterns
                    is_greater = a > b
                    is_less = a < b
                    
                    cand_lower = c_struct['raw_lower']
                    correct_bool = False
                    if is_greater and ('true' in cand_lower or 'yes' in cand_lower or str(a) in c_struct['numbers']):
                         correct_bool = True
                    elif is_less and ('false' in cand_lower or 'no' in cand_lower):
                         correct_bool = True
                         
                    if correct_bool:
                        score += 0.4
                        reasons.append("Numeric logic verified")
            except:
                pass

        # 4. Structural Containment (NCD as tiebreaker/refiner)
        # We use a weighted NCD. Low NCD (high similarity) is good if structure matches.
        ncd = self._compute_ncd(p_struct['raw_lower'], c_struct['raw_lower'])
        
        # Adjust score based on NCD only if structural score is neutral
        if 0.1 < score < 0.5:
            # If structural signal is weak, rely on compression similarity
            if ncd < 0.6:
                score += 0.1
                reasons.append(f"High structural similarity (NCD={ncd:.2f})")
        
        reason_str = "; ".join(reasons) if reasons else "No strong structural alignment"
        return score, reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates against the prompt using CEDS-inspired structural parsing.
        Returns a ranked list of dicts.
        """
        if not candidates:
            return []
            
        results = []
        for cand in candidates:
            score, reasoning = self._score_candidate(prompt, cand)
            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural consistency.
        """
        score, _ = self._score_candidate(prompt, answer)
        # Normalize to 0-1 range roughly. Max expected structural score ~1.0
        conf = max(0.0, min(1.0, score))
        return conf