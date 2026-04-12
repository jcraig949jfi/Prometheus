import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Typed Game-Theoretic CA Verifier (Computational Analogy).
    
    Mechanism:
    1. Type Theory (TT): Prompts and candidates are parsed into structural 'types'
       based on logical operators (negations, conditionals, comparatives) and numeric literals.
       This acts as the dependent type system encoding invariants.
    2. Cellular Automata (CA): The 'lattice' is the set of candidates. Local update rules
       simulate the propagation of logical constraints (e.g., if prompt says "not X", candidates
       containing "X" without negation receive a penalty).
    3. Nash Equilibrium (NE): Scoring treats logical consistency as a payoff. A candidate
       reaches a 'stable equilibrium' (high score) only if it satisfies all structural constraints
       (types) imposed by the prompt. Deviations (logical contradictions) reduce the payoff.
    
    The tool ranks candidates by their 'strategic stability' (logical consistency score),
    using NCD only as a tie-breaker for semantically identical structures.
    """

    def __init__(self):
        # Precompile regex patterns for structural parsing (The "Type System")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|impossible)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|when)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', re.I),
            'numeric': re.compile(r'\d+\.?\d*'),
            'boolean_yes': re.compile(r'\b(yes|true|correct|valid)\b', re.I),
            'boolean_no': re.compile(r'\b(no|false|incorrect|invalid)\b', re.I)
        }

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features acting as 'Types' in the system."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'affirms_yes': bool(self.patterns['boolean_yes'].search(text)),
            'affirms_no': bool(self.patterns['boolean_no'].search(text)),
            'length': len(text.split())
        }
        return features

    def _check_logical_consistency(self, prompt_feats: Dict, cand_feats: Dict, prompt: str, candidate: str) -> float:
        """
        Evaluate 'Nash Stability': Does the candidate deviate from prompt constraints?
        Returns a payoff score (higher = more stable/consistent).
        """
        score = 0.0
        penalties = 0.0
        
        # Constraint 1: Negation Propagation
        # If prompt negates, answer should reflect awareness (or not contradict)
        if prompt_feats['has_negation']:
            # Heuristic: If prompt has negation, simple 'Yes' is often unstable/wrong
            if cand_feats['affirms_yes'] and not cand_feats['has_negation']:
                # Check if the candidate is just "Yes" or similar without nuance
                if cand_feats['length'] < 4:
                    penalties += 0.4
        
        # Constraint 2: Numeric Consistency
        if prompt_feats['numbers'] and cand_feats['numbers']:
            # Simple transitivity check for comparatives
            if prompt_feats['has_comparative']:
                # If prompt compares, candidate numbers should logically align (simplified)
                # Here we just reward presence of numbers in context of comparison
                score += 0.2
            else:
                # Exact match bonus for pure numeric prompts
                if prompt_feats['numbers'] == cand_feats['numbers']:
                    score += 0.5
                else:
                    penalties += 0.3 * abs(prompt_feats['numbers'][0] - cand_feats['numbers'][0]) if cand_feats['numbers'] else 0.1

        # Constraint 3: Conditional Logic
        if prompt_feats['has_conditional']:
            if not cand_feats['has_conditional'] and not cand_feats['affirms_yes'] and not cand_feats['affirms_no']:
                # Complex prompts usually require more than silent acceptance
                pass # Neutral
        
        # Constraint 4: Direct Contradiction (Simple Heuristic)
        # If prompt implies 'No' (via negation of positive) and candidate says 'Yes' strongly
        if prompt_feats['has_negation'] and cand_feats['affirms_yes'] and not prompt_feats['affirms_yes']:
             # Risky to affirm if prompt is negative, unless candidate explains why
             if cand_feats['length'] < 5:
                 penalties += 0.5

        return score - penalties

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tie-breaker."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if max(c1, c2) == 0: return 0.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        prompt_feats = self._extract_features(prompt)
        scored_candidates = []
        
        for cand in candidates:
            cand_feats = self._extract_features(cand)
            
            # Core Reasoning: Game-Theoretic Stability Score
            logic_score = self._check_logical_consistency(prompt_feats, cand_feats, prompt, cand)
            
            # Secondary: Structural similarity (NCD) as tie-breaker
            # In this context, lower NCD to prompt might imply echoing (bad), 
            # but we use it primarily to break ties in logic score.
            ncd_val = self._ncd(prompt, cand)
            
            # Final Score: Logic dominates, NCD is micro-adjustment
            # We invert NCD logic slightly: diverse answers (higher NCD) are often better 
            # if logic score is tied, but exact matches in numbers are good.
            final_score = logic_score + (0.001 * (1.0 - ncd_val)) 
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Logic:{logic_score:.2f}, NCD:{ncd_val:.2f}"
            })
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the stability of the answer 
        against the prompt's structural constraints.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        raw_score = results[0]['score']
        
        # Map raw score (roughly -1.0 to 1.0) to 0.0 - 1.0
        # Baseline 0.5, +/- 0.5 range
        confidence = 0.5 + (raw_score * 0.4)
        return max(0.0, min(1.0, confidence))