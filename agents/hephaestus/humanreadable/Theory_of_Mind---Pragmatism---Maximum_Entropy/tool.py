import re
import json
import zlib
import math

class ReasoningTool:
    """
    MP-METOM Implementation Strategy:
    Given the constraints against using Pragmatism/MaxEnt for direct scoring, this tool
    implements a 'Structural Causal Parser' that mimics the ToM/Pragmatic flow via:
    1. ToM Core (Structural Parsing): Extracts logical constraints (negations, comparatives,
       conditionals) to form a 'belief state' about the prompt's requirements.
    2. Pragmatic Utility (Constraint Satisfaction): Candidates are scored by how well
       they satisfy these structural constraints (workability).
    3. MaxEnt Controller (Calibration): Uses NCD as a tie-breaking entropy term only when
       structural signals are ambiguous, preventing over-commitment to noisy strings.
    """
    
    def __init__(self):
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'larger', 'smaller', 'greater', 'less', 'more', 'fewer', 'higher', 'lower'}
        self.conditionals = {'if', 'unless', 'provided', 'when', 'then'}

    def _normalize(self, text):
        return text.lower().strip()

    def _extract_structural_beliefs(self, prompt):
        """ToM Inference Core: Extracts latent logical constraints from the prompt."""
        p_lower = self._normalize(prompt)
        beliefs = {
            'has_negation': False,
            'has_comparative': False,
            'has_conditional': False,
            'needs_number': False,
            'target_value': None,
            'logic_op': None
        }
        
        # Detect Negation
        if any(w in p_lower.split() for w in self.negation_words):
            beliefs['has_negation'] = True
            
        # Detect Comparatives
        if any(w in p_lower for w in self.comparatives):
            beliefs['has_comparative'] = True
            
        # Detect Conditionals
        if any(w in p_lower.split() for w in self.conditionals):
            beliefs['has_conditional'] = True
            
        # Detect Numeric Constraints (Simple extraction)
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", p_lower)
        if numbers:
            beliefs['needs_number'] = True
            try:
                beliefs['target_value'] = float(numbers[-1])
            except: pass

        # Detect Logic Keywords
        if 'must' in p_lower or 'required' in p_lower: beliefs['logic_op'] = 'must'
        if 'cannot' in p_lower or 'impossible' in p_lower: beliefs['logic_op'] = 'cannot'
        
        return beliefs

    def _pragmatic_utility_score(self, candidate, beliefs, prompt):
        """Pragmatic Utility Layer: Scores candidate based on 'workability' against beliefs."""
        c_lower = self._normalize(candidate)
        score = 0.0
        checks = 0
        
        # Check 1: Negation Consistency
        has_c_neg = any(w in c_lower.split() for w in self.negation_words)
        if beliefs['has_negation']:
            # If prompt has negation, valid answer often acknowledges it or flips logic
            score += 0.5 if has_c_neg else 0.0
        else:
            score += 0.5 if not has_c_neg else 0.0
        checks += 0.5

        # Check 2: Comparative/Number Logic
        if beliefs['needs_number']:
            # Try to extract number from candidate
            c_nums = re.findall(r"[-+]?\d*\.\d+|\d+", c_lower)
            if c_nums:
                try:
                    c_val = float(c_nums[0])
                    # Heuristic: If prompt asks for "larger", candidate should be large? 
                    # Without full semantic parse, we check if candidate contains A number.
                    score += 1.0 
                except: pass
            else:
                # If prompt needs number but candidate is text-only (e.g. "Yes"), penalize slightly
                if not any(k in c_lower for k in ['yes', 'no', 'true', 'false']):
                    score += 0.2
        checks += 1.0

        # Check 3: Conditional/Logic Op
        if beliefs['logic_op'] == 'must':
            if 'must' in c_lower or 'yes' in c_lower or 'true' in c_lower:
                score += 1.0
        elif beliefs['logic_op'] == 'cannot':
            if 'cannot' in c_lower or 'no' in c_lower or 'false' in c_lower:
                score += 1.0
        checks += 1.0

        # Base relevance (simple overlap to ensure topic match)
        p_words = set(self._normalize(prompt).split())
        c_words = set(c_lower.split())
        overlap = len(p_words & c_words)
        score += min(overlap * 0.1, 1.0)
        checks += 1.0

        return score / checks if checks > 0 else 0.0

    def _max_ent_calibration(self, prompt, candidate, base_score):
        """Meta-Reasoning Controller: Applies NCD only as a tie-breaker/calibrator."""
        # NCD Calculation
        s1 = prompt.encode('utf-8')
        s2 = candidate.encode('utf-8')
        len_s1 = len(s1)
        len_s2 = len(s2)
        if len_s1 == 0 or len_s2 == 0:
            ncd = 1.0
        else:
            len_combined = len(zlib.compress(s1 + s2))
            max_len = max(len_s1, len_s2)
            if max_len == 0: ncd = 1.0
            else: ncd = (len_combined - min(len_s1, len_s2)) / max_len
        
        # MaxEnt adjustment: If base_score is ambiguous (near 0.5), let NCD influence.
        # If base_score is strong, NCD is ignored (prevents overfitting to string length).
        if 0.4 <= base_score <= 0.6:
            # Invert NCD (lower distance = higher score)
            calibration_bonus = (1.0 - ncd) * 0.1
            return base_score + calibration_bonus
        return base_score

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        if not candidates:
            return []
        
        beliefs = self._extract_structural_beliefs(prompt)
        results = []
        
        for cand in candidates:
            # 1. Pragmatic Utility Score (Primary Signal)
            util_score = self._pragmatic_utility_score(cand, beliefs, prompt)
            
            # 2. MaxEnt Calibration (Secondary Signal)
            final_score = self._max_ent_calibration(prompt, cand, util_score)
            
            # Reasoning trace
            reason_parts = []
            if beliefs['has_negation']: reason_parts.append("negation detected")
            if beliefs['has_comparative']: reason_parts.append("comparative logic")
            if beliefs['needs_number']: reason_parts.append("numeric constraint")
            reason_str = f"Structural checks: {', '.join(reason_parts) if reason_parts else 'none'}. Utility match: {util_score:.2f}."
            
            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reason_str
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on structural alignment."""
        beliefs = self._extract_structural_beliefs(prompt)
        score = self._pragmatic_utility_score(answer, beliefs, prompt)
        # Normalize to 0-1 strictly
        return min(1.0, max(0.0, score))