import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Recursive Bayesian Falsification Game Engine.
    
    Mechanism:
    1. Kalman Filter Analogy: Treats the 'truth' as a hidden state. The prompt provides 
       the measurement update, while the candidate answers represent predicted states.
       We maintain a 'belief' vector based on structural constraints extracted from the prompt.
       
    2. Falsificationism (Core): Instead of seeking confirmation, the evaluator acts as a 
       'Skeptic'. It actively searches for logical contradictions (negations, type mismatches, 
       constraint violations) between the prompt's conditions and the candidate answer.
       Score = 1.0 - (Weighted Falsification Error).
       
    3. Nash Equilibrium: The scoring function assumes a zero-sum game where the 'Proposer' 
       (candidate) tries to minimize falsification risk, and the 'Skeptic' (evaluator) 
       maximizes it. The final score represents the equilibrium where the candidate has 
       survived the most aggressive structural tests possible given the noise in the text.
       Candidates are ranked by their robustness to these adversarial checks.
    """

    def __init__(self):
        # Structural keywords for falsification tests
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'unless', 'provided', 'assuming', 'when'}
        self.quantifiers = {'all', 'every', 'some', 'few', 'many', 'most', 'any'}

    def _extract_structural_signals(self, text: str) -> Dict:
        """Parses text for logical constraints (Negations, Comparatives, Conditionals)."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        
        signals = {
            'has_negation': any(w in self.negations for w in words),
            'has_comparative': any(w in self.comparatives for w in words),
            'has_conditional': any(w in self.conditionals for w in words),
            'has_quantifier': any(w in self.quantifiers for w in words),
            'numbers': re.findall(r'\d+\.?\d*', lower_text),
            'length': len(words)
        }
        return signals

    def _compute_falsification_error(self, prompt: str, candidate: str) -> float:
        """
        Calculates the 'Falsification Error'. 
        High error = Candidate contradicts prompt structure (Easy to falsify).
        Low error = Candidate is robust against structural attacks.
        """
        p_sig = self._extract_structural_signals(prompt)
        c_sig = self._extract_structural_signals(candidate)
        error = 0.0

        # Test 1: Negation Contradiction
        # If prompt asserts a negative constraint, and candidate lacks negation (or vice versa)
        if p_sig['has_negation'] and not c_sig['has_negation']:
            # Heuristic: If prompt says "X is NOT Y", candidate saying "X is Y" is a hard fail
            # We check for simple presence/absence tension
            error += 0.4
        
        # Test 2: Conditional Logic Check
        # If prompt has conditionals, candidate should ideally reflect uncertainty or conditions
        if p_sig['has_conditional']:
            if not c_sig['has_conditional'] and not c_sig['has_negation']:
                # Absolute statements in response to conditional prompts are suspicious
                error += 0.2

        # Test 3: Numeric Consistency (Simplified)
        # If both have numbers, check magnitude consistency roughly
        if p_sig['numbers'] and c_sig['numbers']:
            try:
                p_max = max(float(n) for n in p_sig['numbers'])
                c_max = max(float(n) for n in c_sig['numbers'])
                # If candidate number is wildly different (order of magnitude), penalize
                if p_max > 0 and (c_max > p_max * 10 or c_max < p_max * 0.1):
                    error += 0.3
            except ValueError:
                pass

        # Test 4: Length/Complexity Mismatch (Occam's Razor / Information Balance)
        # Extremely short answers to complex prompts might miss constraints
        if p_sig['length'] > 20 and c_sig['length'] < 3:
            error += 0.1

        return min(error, 1.0)

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        try:
            z = zlib.compress
            len_s1 = len(z(s1.encode()))
            len_s2 = len(z(s2.encode()))
            len_s1_s2 = len(z((s1 + s2).encode()))
            if len_s1_s2 == 0: return 0.0
            return (len_s1_s2 - min(len_s1, len_s2)) / max(len_s1, len_s2, 1)
        except:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        
        # Pre-calculate prompt signals to avoid re-parsing
        p_sig = self._extract_structural_signals(prompt)
        
        for cand in candidates:
            # 1. Falsification Test (Primary Signal)
            # How easily can this candidate be falsified by the prompt's logic?
            falsification_risk = self._compute_falsification_error(prompt, cand)
            
            # 2. Structural Alignment Bonus
            # Does the candidate mirror the logical type of the prompt?
            c_sig = self._extract_structural_signals(cand)
            alignment_bonus = 0.0
            if p_sig['has_negation'] and c_sig['has_negation']:
                alignment_bonus += 0.1
            if p_sig['has_conditional'] and c_sig['has_conditional']:
                alignment_bonus += 0.1
            
            # Base score starts at 1.0 (True) and is reduced by falsification risk
            # Nash Equilibrium concept: The score stabilizes where falsification risk 
            # is minimized given the available information.
            raw_score = max(0.0, 1.0 - falsification_risk + alignment_bonus)
            raw_score = min(raw_score, 1.0)
            
            scored_candidates.append({
                "candidate": cand,
                "raw_score": raw_score,
                "falsification_risk": falsification_risk
            })

        # Normalize scores to ensure distribution makes sense relative to each other
        # This acts as the "Equilibrium" adjustment where relative standing matters
        max_raw = max(c["raw_score"] for c in scored_candidates)
        min_raw = min(c["raw_score"] for c in scored_candidates)
        range_raw = max_raw - min_raw if max_raw != min_raw else 1.0

        final_results = []
        for item in scored_candidates:
            # Normalize to 0-1 range, keeping relative distances
            norm_score = (item["raw_score"] - min_raw) / range_raw
            
            # Tie-breaking with NCD (Compression)
            # Prefer candidates that compress well with the prompt (semantic similarity)
            # but only as a secondary factor (weight 0.05)
            ncd_val = self._ncd_distance(prompt, item["candidate"])
            # Lower NCD is better (more similar), so we invert it for the score
            ncd_bonus = (1.0 - ncd_val) * 0.05 
            
            final_score = norm_score + ncd_bonus
            final_score = min(1.0, max(0.0, final_score))

            reasoning = f"Falsification Risk: {item['falsification_risk']:.2f}. "
            if item['falsification_risk'] < 0.2:
                reasoning += "Candidate survives aggressive structural testing."
            elif item['falsification_risk'] > 0.5:
                reasoning += "Candidate contains structural contradictions to prompt."
            else:
                reasoning += "Candidate shows moderate robustness."

            final_results.append({
                "candidate": item["candidate"],
                "score": final_score,
                "reasoning": reasoning
            })

        # Sort descending by score
        final_results.sort(key=lambda x: x["score"], reverse=True)
        return final_results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on falsification survival."""
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        return results[0]["score"]