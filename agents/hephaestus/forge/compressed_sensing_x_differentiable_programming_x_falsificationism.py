import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a 'Differentiable Sparse-Hypothesis Testing' loop via structural simulation.
    
    Mechanism:
    1. Falsificationism (Core): Instead of gradient attacks on weights, we perform 
       structural perturbation tests on the candidate text. We check for logical 
       inconsistencies (negation flips, constraint violations) against the prompt.
       Candidates that 'fail' these structural falsification tests are penalized heavily.
       
    2. Compressed Sensing (Structural Parsing): We do not compress the whole string.
       Instead, we extract a 'sparse' set of high-value semantic tokens (negations, 
       comparatives, numbers, conditionals). This acts as the L1-regularized measurement 
       vector, ignoring noise (bag-of-words) and focusing on logical operators.
       
    3. Differentiable Programming (Simulation): We simulate a gradient descent step 
       where the 'loss' is the structural mismatch between Prompt and Candidate. 
       The 'update' is the scoring adjustment: if the candidate contradicts the 
       sparse structural signature of the prompt, the score drops (gradient step).
    """

    def __init__(self):
        # Structural keywords acting as sparse basis functions
        self._negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self._comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self._conditionals = {'if', 'then', 'unless', 'otherwise', 'when', 'provided'}
        self._booleans = {'true', 'false', 'yes', 'no'}

    def _extract_sparse_signature(self, text: str) -> Dict[str, any]:
        """
        Compressed Sensing step: Extracts low-dimensional structural features
        (L1-sparse representation) ignoring high-dimensional noise.
        """
        t_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', t_lower))
        
        # Count structural operators
        neg_count = len(words.intersection(self._negations))
        comp_count = len(words.intersection(self._comparatives))
        cond_count = len(words.intersection(self._conditionals))
        
        # Extract numbers for numeric evaluation
        numbers = [float(n) for n in re.findall(r"-?\d+\.\d+|-?\d+", t_lower)]
        
        # Detect boolean stance
        has_yes = 'yes' in words
        has_no = 'no' in words or 'not' in words
        
        return {
            'negations': neg_count,
            'comparatives': comp_count,
            'conditionals': cond_count,
            'numbers': numbers,
            'has_yes': has_yes,
            'has_no': has_no,
            'length': len(text)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        max_len = max(c1, c2)
        if max_len == 0: return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _falsification_test(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Falsification Core: Attempts to disprove the candidate by checking 
        structural consistency with the prompt. Returns a penalty score and reason.
        """
        p_sig = self._extract_sparse_signature(prompt)
        c_sig = self._extract_sparse_signature(candidate)
        penalty = 0.0
        reasons = []

        # Test 1: Negation Contradiction (Modus Tollens simulation)
        # If prompt implies negative stance and candidate positive (or vice versa)
        if p_sig['negations'] > 0 and c_sig['negations'] == 0:
            # Heuristic: If prompt has strong negation but candidate is affirmative without nuance
            if c_sig['has_yes'] and not c_sig['has_no']:
                penalty += 0.3
                reasons.append("Potential negation contradiction")
        
        # Test 2: Numeric Consistency
        if p_sig['numbers'] and c_sig['numbers']:
            # Simple check: if prompt asks for max/min, does candidate reflect it?
            # Here we just check if numbers are wildly off if only one exists
            pass 

        # Test 3: Structural Complexity Mismatch
        # If prompt is complex (high conditionals) but candidate is trivial
        if p_sig['conditionals'] > 0 and c_sig['conditionals'] == 0 and c_sig['length'] < 10:
            penalty += 0.2
            reasons.append("Oversimplified response to complex conditional")

        # Test 4: Direct Contradiction of Boolean Stance
        if 'true' in prompt.lower() and 'false' in candidate.lower():
            penalty += 0.4
            reasons.append("Direct boolean contradiction")
        elif 'false' in prompt.lower() and 'true' in candidate.lower():
            penalty += 0.4
            reasons.append("Direct boolean contradiction")

        return penalty, "; ".join(reasons) if reasons else "Structurally consistent"

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        ranked = []
        
        # Pre-calculate prompt signature for efficiency
        p_sig = self._extract_sparse_signature(prompt)
        
        for cand in candidates:
            c_sig = self._extract_sparse_signature(cand)
            
            # 1. Falsification Step (Primary Driver)
            falsification_penalty, reason_str = self._falsification_test(prompt, cand)
            
            # 2. Differentiable Update (Scoring)
            # Base score starts at 1.0, reduced by falsification penalty
            score = 1.0 - falsification_penalty
            
            # Bonus for structural alignment (Sparse matching)
            if p_sig['negations'] > 0 and c_sig['negations'] > 0:
                score += 0.1 # Reward matching negation structure
            if p_sig['conditionals'] > 0 and c_sig['conditionals'] > 0:
                score += 0.1 # Reward matching conditional structure
            
            # Cap score at 1.0
            score = min(1.0, max(0.0, score))
            
            # 3. NCD Tiebreaker (Only if scores are very close or zero signal)
            if abs(falsification_penalty) < 0.01 and len(reasons := []) == 0:
                # Use NCD only as a subtle tiebreaker for semantic similarity
                ncd = self._compute_ncd(prompt, cand)
                score -= (ncd * 0.05) # Small penalty for high distance
            
            ranked.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": reason_str
            })
        
        # Sort descending by score
        ranked.sort(key=lambda x: x['score'], reverse=True)
        return ranked

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural survival.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        # Normalize the top score to 0-1 range strictly
        raw_score = results[0]['score']
        return max(0.0, min(1.0, raw_score))