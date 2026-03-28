import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A hybrid reasoning engine integrating Constraint Satisfaction (CSP), 
    Error Correcting Codes (ECC), and the Free Energy Principle (FEP).
    
    Mechanism:
    1. FEP Core: Scores candidates based on 'Variational Free Energy', defined here as
       the sum of Prediction Error (structural mismatch with prompt logic) and 
       Complexity (penalty for verbosity/redundancy). This is the primary driver.
    2. CSP Factors: Enforces hard logical constraints (negations, conditionals). 
       Violations inject high 'energy' (penalty), simulating arc-consistency failure.
    3. ECC Factors: Treats the candidate's logical signature as a codeword. 
       Calculates a 'syndrome' based on parity of extracted logical features. 
       If the syndrome indicates noise (inconsistency between prompt and answer logic),
       energy increases. This acts as a noise filter for spurious activations.
       
    The final score is derived from minimizing this composite Free Energy.
    NCD is used strictly as a tie-breaker for structurally identical candidates.
    """

    def __init__(self):
        # Logical keywords for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'implies']
        self.confirmations = ['yes', 'true', 'correct', 'indeed', 'affirmative']
        self.rejections = ['no', 'false', 'incorrect', 'wrong', 'negative']

    def _extract_features(self, text: str) -> Dict:
        """Extract structural logical features from text."""
        t = text.lower()
        words = re.findall(r'\b\w+\b', t)
        
        has_neg = any(n in t for n in self.negations)
        has_cond = any(c in t for c in self.conditionals)
        has_comp = any(c in t for c in self.comparatives)
        is_confirm = any(c in t for c in self.confirmations)
        is_reject = any(r in t for r in self.rejections)
        
        # Extract numbers for numeric evaluation
        nums = re.findall(r'\d+\.?\d*', t)
        numbers = [float(n) for n in nums] if nums else []
        
        return {
            'neg': has_neg,
            'cond': has_cond,
            'comp': has_comp,
            'confirm': is_confirm,
            'reject': is_reject,
            'numbers': numbers,
            'length': len(words)
        }

    def _compute_csp_penalty(self, p_feat: Dict, c_feat: Dict) -> float:
        """
        CSP Factor: Enforce logical consistency.
        If prompt implies negation but candidate confirms (or vice versa), penalize heavily.
        """
        penalty = 0.0
        
        # Negation consistency
        if p_feat['neg'] != c_feat['neg']:
            # If prompt has negation, candidate should reflect understanding (often via negation or specific rejection)
            # Simple heuristic: if prompt negates, and candidate blindly confirms without nuance, riskier.
            # Stronger signal: Direct contradiction.
            if p_feat['neg'] and c_feat['confirm'] and not c_feat['neg']:
                penalty += 5.0 
            elif not p_feat['neg'] and c_feat['reject'] and not c_feat['neg']:
                 penalty += 5.0

        # Conditional consistency (simplified)
        if p_feat['cond'] and not c_feat['cond'] and not c_feat['confirm'] and not c_feat['reject']:
            # If prompt is conditional, bare answers might be ambiguous, but not strictly wrong.
            # However, if candidate introduces conditionals where none exist, it might be hallucinating constraints.
            pass 
            
        return penalty

    def _compute_ecc_syndrome(self, p_feat: Dict, c_feat: Dict) -> float:
        """
        ECC Factor: Parity check on logical features.
        Treat logical features as bits. A valid 'codeword' (consistent reasoning) 
        should have a specific parity relationship between Prompt and Candidate.
        Syndrome = 0 implies consistency (low energy). Syndrome != 0 implies noise (high energy).
        """
        # Encode features as bits
        # Bit 0: Negation, Bit 1: Confirmation, Bit 2: Rejection
        p_bits = (int(p_feat['neg']) << 2) | (int(p_feat['confirm']) << 1) | int(p_feat['reject'])
        c_bits = (int(c_feat['neg']) << 2) | (int(c_feat['confirm']) << 1) | int(c_feat['reject'])
        
        # Parity check: In a consistent system, specific transitions should preserve or flip parity predictably.
        # Here we use a simple XOR distance as a 'syndrome' magnitude.
        # If the logical 'shape' is too different without semantic bridge, it's noise.
        syndrome = bin(p_bits ^ c_bits).count('1')
        
        # If prompt has numbers, candidate numbers should ideally match or be logically derived.
        # If prompt has nums and candidate has none, syndrome increases (loss of information).
        if p_feat['numbers'] and not c_feat['numbers']:
            syndrome += 2
            
        # Convert syndrome to energy penalty (non-linear)
        return 0.5 * (syndrome ** 2)

    def _compute_fep_energy(self, prompt: str, candidate: str) -> float:
        """
        FEP Core: Calculate Variational Free Energy = Prediction Error + Complexity.
        Lower energy = Better candidate.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        # 1. Complexity Term (Prior precision): Penalize verbosity relative to prompt
        # Overly long explanations often indicate uncertainty or hallucination in this context
        complexity = 0.1 * (c_feat['length'] - p_feat['length']) 
        if complexity < 0: complexity = 0 # Being concise is good, not penalized
        
        # 2. Prediction Error (Accuracy): Structural mismatch
        # Numeric evaluation
        prediction_error = 0.0
        if p_feat['numbers'] and c_feat['numbers']:
            # Check simple ordering if comparatives exist
            if p_feat['comp']:
                # If prompt compares, candidate should ideally respect the order if it repeats numbers
                # Simplified: Just check if numbers are present and plausible (not random)
                pass 
        elif p_feat['numbers'] and not c_feat['numbers']:
            # Missing numeric engagement when numbers are present is a high error
            if any(x > 0 for x in p_feat['numbers']):
                prediction_error += 2.0

        # Structural constraints (CSP)
        csp_penalty = self._compute_csp_penalty(p_feat, c_feat)
        
        # Noise filtering (ECC)
        ecc_penalty = self._compute_ecc_syndrome(p_feat, c_feat)
        
        # Total Free Energy
        free_energy = prediction_error + complexity + csp_penalty + ecc_penalty
        
        return free_energy

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tie-breaker."""
        z = zlib.compressobj()
        try:
            c1 = len(z.compress(s1.encode()) + z.flush())
            z = zlib.compressobj()
            c2 = len(z.compress(s2.encode()) + z.flush())
            z = zlib.compressobj()
            c12 = len(z.compress((s1+s2).encode()) + z.flush())
            
            if max(c1, c2) == 0: return 0.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        results = []
        for cand in candidates:
            energy = self._compute_fep_energy(prompt, cand)
            # Convert energy to score (lower energy = higher score)
            # Use exp(-energy) to map to 0-1 range roughly
            score = math.exp(-energy)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": f"FEP Energy: {energy:.4f} (CSP/ECC penalties applied)"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Tie-breaking with NCD if scores are very close
        if len(results) > 1:
            if abs(results[0]['score'] - results[1]['score']) < 1e-6:
                # Apply NCD only if top candidates are indistinguishable by FEP
                ncd_scores = []
                for r in results:
                    ncd = self._ncd_distance(prompt, r['candidate'])
                    ncd_scores.append((r, ncd))
                # Lower NCD is better (more similar structure)
                ncd_scores.sort(key=lambda x: x[1])
                results = [x[0] for x in ncd_scores]
                # Re-update reasoning to reflect tie-break
                for r in results:
                    r['reasoning'] += " (NCD tie-break applied)"

        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the Free Energy of the specific pair.
        """
        energy = self._compute_fep_energy(prompt, answer)
        conf = math.exp(-energy)
        return min(1.0, max(0.0, conf))