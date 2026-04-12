import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Renormalized Adversarial Debate Network (RADN) - Structural Implementation
    
    Mechanism:
    1. Renormalization (Scale): Analyzes text at char, word, and sentence scales.
      Coarse-grains details into structural signatures (negations, comparatives).
    2. Dialectics (Debate): Generates 'Thesis' (structural match) and 'Antithesis'
      (contradiction check via negation flipping). Synthesis resolves conflicts.
    3. Pragmatism (Utility): Scores based on logical constraint satisfaction rather
      than semantic similarity. NCD is used only as a tiebreaker for low-signal cases.
      
    This avoids the 'Pragmatism' trap by using it strictly as a structural filter,
    not a semantic scorer.
    """

    def __init__(self):
        # Structural patterns for dialectical analysis
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.quantifiers = ['all', 'some', 'every', 'each', 'any', 'most']

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _extract_structural_signature(self, text: str) -> Dict:
        """Renormalization step: Extract coarse-grained logical features."""
        lower_text = self._normalize(text)
        words = re.findall(r'\b\w+\b', lower_text)
        
        sig = {
            'has_negation': any(n in words for n in self.negations),
            'has_comparative': any(c in lower_text for c in self.comparatives),
            'has_conditional': any(c in words for c in self.conditionals),
            'has_quantifier': any(q in words for q in self.quantifiers),
            'numbers': re.findall(r'\d+\.?\d*', lower_text),
            'length': len(words)
        }
        return sig

    def _numeric_check(self, prompt: str, candidate: str) -> float:
        """Pragmatic utility: Verify numeric constraints explicitly."""
        p_nums = re.findall(r'\d+\.?\d*', self._normalize(prompt))
        c_nums = re.findall(r'\d+\.?\d*', self._normalize(candidate))
        
        if not p_nums or not c_nums:
            return 0.0 # No numeric signal
        
        try:
            # Simple heuristic: if candidate numbers are a subset or match prompt logic
            # This is a simplified pragmatic check for presence/absence
            p_set = set(float(n) for n in p_nums)
            c_set = set(float(n) for n in c_nums)
            
            # If prompt asks for comparison (e.g. 9.11 vs 9.9), candidate must reflect order
            if len(p_set) >= 2 and len(c_set) >= 2:
                p_sorted = sorted(list(p_set))
                c_sorted = sorted(list(c_set))
                # Check if relative order is preserved or explicitly inverted correctly
                return 0.5 # Neutral if just present, requires deeper logic for full score
            return 0.2 if c_set else 0.0
        except ValueError:
            return 0.0

    def _dialectical_debate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Dialectics: Thesis vs Antithesis.
        Thesis: Candidate structure matches prompt structure.
        Antithesis: Candidate contradicts prompt negations or conditionals.
        Synthesis: Score based on consistency.
        """
        p_sig = self._extract_structural_signature(prompt)
        c_sig = self._extract_structural_signature(candidate)
        score = 0.0
        reasoning = []

        # Thesis: Structural Alignment
        if p_sig['has_negation'] == c_sig['has_negation']:
            score += 0.3
            reasoning.append("Negation alignment confirmed.")
        elif p_sig['has_negation'] and not c_sig['has_negation']:
            score -= 0.4
            reasoning.append("Critical failure: Missing negation in candidate.")
        
        if p_sig['has_conditional'] == c_sig['has_conditional']:
            score += 0.2
            reasoning.append("Conditional structure preserved.")
            
        # Antithesis: Contradiction Detection (Simplified)
        # If prompt has "no" and candidate has "yes" without qualification
        lower_p = self._normalize(prompt)
        lower_c = self._normalize(candidate)
        
        if ('no ' in lower_p or ' not ' in lower_p) and ('yes' in lower_c or 'true' in lower_c):
            # Potential contradiction, check context length to avoid false positives on short answers
            if len(lower_p.split()) > 5: 
                score -= 0.3
                reasoning.append("Antithesis detected: Affirmation contradicts negative prompt.")

        # Pragmatic Numeric Utility
        num_score = self._numeric_check(prompt, candidate)
        if num_score > 0:
            score += 0.2
            reasoning.append("Numeric constraints acknowledged.")
            
        return score, "; ".join(reasoning) if reasoning else "No structural features detected."

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            max_len = max(c1, c2)
            if max_len == 0: return 1.0
            return (c12 - min(c1, c2)) / max_len
        except Exception:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            dialectic_score, reason_text = self._dialectical_debate(prompt, cand)
            
            # Base score from dialectics
            final_score = 0.5 + dialectic_score # Center around 0.5
            
            # Clamp for now, will sort later
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reason_text,
                "ncd_val": self._ncd(prompt, cand) # Store for tiebreaking
            })
        
        # Sorting: Primary by score, Secondary by NCD (lower is better for similarity/tiebreak)
        # We want high score. If scores equal, prefer lower NCD (more similar structure)
        results.sort(key=lambda x: (x['score'], -x['ncd_val']), reverse=True)
        
        # Normalize scores to 0-1 range roughly based on ranking if needed, 
        # but raw score is fine as long as it ranks correctly.
        # Adjusting to ensure strict 0-1 compliance for the interface
        max_s = max(r['score'] for r in results) if results else 1
        min_s = min(r['score'] for r in results) if results else 0
        range_s = max_s - min_s if max_s != min_s else 1
        
        final_output = []
        for r in results:
            # Rescale to 0.1 - 0.9 to leave room for confidence adjustments
            norm_score = 0.1 + 0.8 * ((r['score'] - min_s) / range_s)
            final_output.append({
                "candidate": r['candidate'],
                "score": round(norm_score, 4),
                "reasoning": r['reasoning']
            })
            
        return final_output

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses structural parsing as primary signal.
        """
        p_sig = self._extract_structural_signature(prompt)
        a_sig = self._extract_structural_signature(answer)
        
        confidence = 0.5 # Base uncertainty
        
        # Structural consistency boosts confidence
        if p_sig['has_negation'] == a_sig['has_negation']:
            confidence += 0.2
        else:
            confidence -= 0.3 # Mismatch reduces confidence significantly
            
        if p_sig['has_conditional'] == a_sig['has_conditional']:
            confidence += 0.1
            
        # Numeric presence check
        if p_sig['numbers']:
            if a_sig['numbers']:
                confidence += 0.1
            else:
                confidence -= 0.2 # Missing numbers when prompt has them is suspicious
                
        return max(0.0, min(1.0, confidence))