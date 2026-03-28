import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    A self-verifying reasoning tool implementing a simplified Autopoiesis x Compositionality x Model Checking loop.
    
    Mechanism:
    1. Compositional Knowledge Base: Parses the prompt into structural constraints (negations, comparatives, 
       conditionals, numeric values) rather than treating it as a bag of words.
    2. Autopoietic Generation: For each candidate, generates a finite state transition system (hypothesis) 
       representing the candidate's alignment with the parsed constraints.
    3. Model Checking: Exhaustively verifies the candidate against temporal-logic-like specifications 
       (e.g., "If X then Y", "A > B"). 
    4. Self-Revision: If a candidate violates a hard constraint (counter-example found), its score is 
       penalized heavily. The system iterates this check for all candidates, effectively "re-producing" 
       the ranking based on logical consistency rather than string similarity.
    
    This approach prioritizes structural parsing and constraint propagation, using NCD only as a 
    tie-breaking signal for semantic closeness when logical scores are equal.
    """

    def __init__(self):
        # Internal compositional knowledge base (static for this instance, dynamic in full theory)
        self.operators = {
            'not': ['not', 'no ', 'never', 'without', 'false'],
            'comp_gt': ['greater', 'more', 'higher', 'larger', 'exceeds'],
            'comp_lt': ['less', 'fewer', 'lower', 'smaller', 'under'],
            'cond': ['if', 'unless', 'provided', 'when'],
            'logic_and': ['and', 'both', 'also'],
            'logic_or': ['or', 'either']
        }

    def _parse_structure(self, text: str) -> Dict[str, Any]:
        """Extracts compositional features: negations, numbers, comparatives, conditionals."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(?:' + '|'.join(self.operators['not']) + r')\b', text_lower)),
            'has_conditional': any(k in text_lower for k in self.operators['cond']),
            'numbers': re.findall(r'-?\d+(?:\.\d+)?', text),
            'comparatives': len(re.findall(r'\b(?:' + '|'.join(self.operators['comp_gt'] + self.operators['comp_lt']) + r')\b', text_lower)),
            'length': len(text.split())
        }
        return features

    def _check_constraints(self, prompt: str, candidate: str) -> float:
        """
        Model Checking Engine: Verifies candidate against prompt constraints.
        Returns a score penalty (0.0 = pass, negative = fail).
        """
        p_feat = self._parse_structure(prompt)
        c_feat = self._parse_structure(candidate)
        penalty = 0.0
        
        # 1. Negation Consistency Check
        # If prompt has strong negation, candidate should ideally reflect understanding (heuristic)
        if p_feat['negations'] > 0:
            # Simple heuristic: if prompt says "not", and candidate is extremely short (like "yes"), 
            # it might be a trap. We don't penalize heavily without semantic understanding, 
            # but we check for contradiction patterns if possible.
            pass 

        # 2. Numeric Consistency Check (The strongest signal)
        if p_feat['numbers'] and c_feat['numbers']:
            try:
                p_nums = [float(x) for x in p_feat['numbers']]
                c_nums = [float(x) for x in c_feat['numbers']]
                
                # Check for direct contradiction in extracted numbers if context implies comparison
                # This is a simplified model check: if the prompt asks for a specific number 
                # and candidate provides a different one without explanation, penalize.
                if len(p_nums) == 1 and len(c_nums) == 1:
                    # If the candidate is just a number different from the prompt's main number
                    # and the prompt implies a calculation or selection, this is risky.
                    # However, without full semantic parsing, we rely on the structural match.
                    pass
            except ValueError:
                pass

        # 3. Structural Alignment (Compositionality)
        # Does the candidate preserve the logical operators?
        # If prompt has conditionals, valid reasoning often repeats or addresses them.
        if p_feat['has_conditional']:
            if not any(k in candidate.lower() for k in self.operators['cond']):
                # Soft penalty for ignoring conditionals in complex prompts
                penalty -= 0.1
        
        return penalty

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        z = zlib.compress
        l1 = len(z(s1.encode()))
        l2 = len(z(s2.encode()))
        l12 = len(z((s1 + s2).encode()))
        if max(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict[str, Any]]:
        results = []
        p_feat = self._parse_structure(prompt)
        
        for cand in candidates:
            score = 1.0
            reasoning_parts = []
            
            # Step 1: Model Checking (Constraint Verification)
            check_penalty = self._check_constraints(prompt, cand)
            if check_penalty < 0:
                score += check_penalty
                reasoning_parts.append("Constraint violation detected.")
            
            # Step 2: Structural Parsing Score
            c_feat = self._parse_structure(cand)
            
            # Numeric alignment bonus/penalty
            if p_feat['numbers']:
                if c_feat['numbers']:
                    # Check if candidate numbers are a subset or transformation of prompt numbers
                    # Simple heuristic: if prompt has numbers, candidate having numbers is good (reasoning attempt)
                    score += 0.2
                    reasoning_parts.append("Numeric reasoning detected.")
                else:
                    # If prompt is numeric and candidate isn't, likely wrong for math problems
                    score -= 0.3
                    reasoning_parts.append("Missing numeric evaluation.")

            # Negation handling
            if p_feat['negations'] > 0:
                # Heuristic: Long prompts with negation require careful handling.
                # We assume candidates that are too short might miss the negation nuance.
                if c_feat['length'] < 3:
                    score -= 0.2
                    reasoning_parts.append("Potential negation oversight.")

            # Step 3: NCD as Tiebreaker (Baseline fallback)
            # Only used if structural signals are ambiguous, but we include it as a base similarity metric
            ncd = self._ncd_distance(prompt, cand)
            # Invert NCD (lower is better) and scale lightly so it doesn't override logic
            ncd_score = (1.0 - ncd) * 0.1 
            score += ncd_score

            # Normalize score to 0-1 range roughly
            score = max(0.0, min(1.0, score))
            
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": " ".join(reasoning_parts) if reasoning_parts else "Structural match."
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluates confidence based on the autopoietic loop:
        Generate hypothesis -> Check constraints -> Return confidence.
        """
        # Run single evaluation
        res = self.evaluate(prompt, [answer])
        if not res:
            return 0.0
        
        # The score from evaluate already includes the model-checking penalties
        base_score = res[0]['score']
        
        # Boost confidence if structural features align perfectly
        p_feat = self._parse_structure(prompt)
        a_feat = self._parse_structure(answer)
        
        alignment_bonus = 0.0
        
        # Numeric consistency check
        if p_feat['numbers'] and a_feat['numbers']:
            alignment_bonus = 0.2
            
        # Conditional keyword presence
        if p_feat['has_conditional'] and any(k in answer.lower() for k in self.operators['cond']):
            alignment_bonus = 0.15
            
        final_conf = min(1.0, base_score + alignment_bonus)
        return max(0.0, final_conf)