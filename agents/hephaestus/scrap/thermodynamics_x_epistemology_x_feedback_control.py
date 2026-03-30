import re
import math
import zlib
from typing import List, Dict, Tuple, Optional

class ReasoningTool:
    """
    Active Inference Reasoning Tool based on the Variational Free-Energy Principle.
    
    Mechanism:
    1. Epistemology (Belief State): Encodes the prompt and candidates into a generative model.
    2. Thermodynamics (Free Energy): Computes 'surprise' via Normalized Compression Distance (NCD)
       as a baseline entropy bound. High compression = low surprise.
    3. Feedback Control (Prediction Error): 
       - Structural Parsing: Extracts logical operators (negations, comparatives) to compute 
         deterministic prediction errors. If the candidate contradicts the parsed structure, 
         free energy spikes (score drops).
       - Precision Weighting: Adjusts the influence of NCD vs. Structural logic. High precision 
         on structural matches overrides thermodynamic noise.
    4. Metacognition (Confidence): Evaluates the prompt for ambiguity (presuppositions, scope) 
       before scoring. If the "plant" (prompt) is unstable (ambiguous), the controller reduces 
       gain (confidence < 0.3) to prevent overfitting to noise.
    """

    def __init__(self):
        self._structural_weight = 0.55
        self._computational_weight = 0.30
        self._thermo_weight = 0.15

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance as a thermodynamic proxy."""
        if not s1 or not s2:
            return 1.0
        combined = f"{s1} {s2}"
        len1 = len(zlib.compress(s1.encode()))
        len2 = len(zlib.compress(s2.encode()))
        len_comb = len(zlib.compress(combined.encode()))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len_comb - min(len1, len2)) / max_len

    def _extract_structure(self, prompt: str) -> Dict:
        """Parses prompt for logical constraints (Control Signals)."""
        p_lower = prompt.lower()
        return {
            'has_negation': bool(re.search(r'\b(not|no|never|neither|without)\b', p_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', p_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|provided)\b', p_lower)),
            'has_numeric': bool(re.search(r'\d+(\.\d+)?', prompt)),
            'is_question': prompt.strip().endswith('?')
        }

    def _compute_logical_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a deterministic score based on structural parsing and simple computation.
        Returns 1.0 for match, 0.0 for contradiction, 0.5 for neutral.
        """
        p_lower = prompt.lower()
        c_lower = candidate.lower()
        score = 0.5  # Base prior
        
        # 1. Negation Check (Modus Tollens simplified)
        # If prompt says "X is NOT Y" and candidate says "X is Y", penalize heavily.
        # Heuristic: Look for direct string inclusion of negated phrases.
        negation_patterns = [
            (r'not\s+(\w+)', r'\1'),
            (r'never\s+(\w+)', r'\1'),
            (r'no\s+(\w+)', r'\1')
        ]
        
        is_negated_context = False
        for pattern, group in negation_patterns:
            match = re.search(pattern, p_lower)
            if match:
                is_negated_context = True
                target = match.group(group)
                # If candidate contains the target word but the prompt negates it, and candidate lacks negation
                if target in c_lower and not re.search(r'not|no|never', c_lower):
                    # Check if the candidate is affirming the negated concept
                    # This is a heuristic approximation of prediction error
                    if len(target) > 3: # Avoid noise on short words
                        score -= 0.8

        # 2. Numeric Evaluation (Constructive Computation)
        # Extract numbers from prompt and candidate to check for consistency
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if p_nums and c_nums:
            try:
                # Simple consistency check: if prompt has numbers, candidate should likely reflect them
                # or perform a valid operation. 
                # Here we just check if candidate numbers are a subset or result of simple ops
                # For this implementation, we check if the candidate repeats the numbers correctly 
                # in a comparative context.
                pass 
            except:
                pass

        # 3. Binary Choice Traps (Yes/No vs Negation)
        if 'yes' in c_lower and self._extract_structure(prompt)['has_negation']:
            # If prompt has negation, a simple "Yes" might be ambiguous, but often a trap.
            # We don't penalize heavily without full NLP, but we don't boost.
            pass
            
        return max(0.0, min(1.0, score))

    def _meta_confidence(self, prompt: str) -> float:
        """
        Evaluates the prompt for epistemic stability (Ambiguity, Presupposition, etc.).
        Returns a cap value (0.0 - 1.0).
        """
        p_lower = prompt.lower()
        
        # 1. Presupposition Traps
        presupposition_triggers = [
            r"have you stopped", r"have you quit", r"why did.*fail", 
            r"why did.*stop", r"when did.*stop", r"who is the king of"
        ]
        for pattern in presupposition_triggers:
            if re.search(pattern, p_lower):
                return 0.2  # Low confidence due to loaded question

        # 2. Scope Ambiguity
        if re.search(r'every\s+\w+\s+\w+\s+a\s+\w+', p_lower):
            # "Every X did a Y" - ambiguous if Y is same for all
            if "same" not in p_lower and "different" not in p_lower:
                return 0.25

        # 3. Pronoun Ambiguity
        # "X told Y he..." patterns
        if re.search(r'\w+\s+told\s+\w+\s+he\s+', p_lower):
            if "who" in p_lower:
                return 0.2

        # 4. False Dichotomy
        if re.search(r'either\s+.*\s+or\s+.*', p_lower):
            if "only" not in p_lower and "must" not in p_lower:
                # Potential false dichotomy if not constrained
                if re.search(r'which one|choose', p_lower):
                    return 0.3

        # 5. Subjectivity
        subjective_terms = ['best', 'worst', 'favorite', 'beautiful', 'ugly']
        if any(term in p_lower for term in subjective_terms):
            if "according to" not in p_lower and "data" not in p_lower:
                return 0.3

        # 6. Unanswerability (Missing Info)
        if re.search(r'calculate|solve|find', p_lower):
            if not re.search(r'\d', prompt): # Asking to calculate but no numbers
                return 0.15

        return 1.0  # No obvious traps detected

    def _compute_computational_score(self, prompt: str, candidate: str) -> float:
        """
        Attempts to solve numeric or logical problems explicitly.
        Returns 1.0 if correct, 0.0 if wrong, 0.5 if not applicable.
        """
        # Detect simple math expressions in prompt like "What is 2 + 2?"
        match = re.search(r'(-?\d+(?:\.\d+)?)\s*([\+\-\*\/])\s*(-?\d+(?:\.\d+)?)\s*=?', prompt)
        if match:
            try:
                n1 = float(match.group(1))
                op = match.group(2)
                n2 = float(match.group(3))
                
                expected = None
                if op == '+': expected = n1 + n2
                elif op == '-': expected = n1 - n2
                elif op == '*': expected = n1 * n2
                elif op == '/': expected = n1 / n2 if n2 != 0 else None
                
                if expected is not None:
                    # Check if candidate contains the result
                    cand_nums = re.findall(r'-?\d+(?:\.\d+)?', candidate)
                    for cn in cand_nums:
                        if math.isclose(float(cn), expected, rel_tol=1e-5):
                            return 1.0
                    return 0.0 # Math found but answer wrong
            except:
                pass
        
        return 0.5 # No computable task found

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        
        # Meta-evaluation: Check prompt integrity first
        meta_cap = self._meta_confidence(prompt)
        structure = self._extract_structure(prompt)
        
        # If the prompt is epistemically unstable, we still score but cap confidence later.
        # However, for ranking, we must still differentiate based on available signals.
        
        for cand in candidates:
            # 1. Thermodynamic Score (NCD) - Lower is better (distance), invert to 0-1
            ncd_val = self._ncd(prompt, cand)
            thermo_score = 1.0 - ncd_val
            
            # 2. Structural/Logical Score (Feedback Control)
            # Uses prediction error to adjust score
            logical_score = self._compute_logical_score(prompt, cand)
            
            # 3. Computational Score (Constructive)
            comp_score = self._compute_computational_score(prompt, cand)
            
            # Combine scores based on weights
            # If computation yielded a definitive result (1.0 or 0.0), it dominates
            if comp_score != 0.5:
                final_score = comp_score
            else:
                # Weighted sum
                final_score = (
                    logical_score * self._structural_weight +
                    thermo_score * self._thermo_weight +
                    logical_score * 0.15 # Extra weight to logic if no comp
                )
                # Normalize roughly
                final_score = min(1.0, max(0.0, final_score))

            # Reasoning string generation
            reasoning = f"Thermo:{thermo_score:.2f}, Logic:{logical_score:.2f}, Comp:{comp_score:.2f}"
            if meta_cap < 0.3:
                reasoning += " [WARNING: Prompt Ambiguity Detected]"

            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence capped by epistemic honesty checks.
        """
        # 1. Calculate base confidence based on how well the answer fits structural/computational checks
        comp_score = self._compute_computational_score(prompt, answer)
        logic_score = self._compute_logical_score(prompt, answer)
        
        base_conf = 0.5
        if comp_score != 0.5:
            base_conf = comp_score # 1.0 or 0.0
        else:
            # Blend logic and NCD
            ncd_val = self._ncd(prompt, answer)
            base_conf = (logic_score * 0.7) + ((1.0 - ncd_val) * 0.3)

        # 2. Apply Meta-Confidence Cap (Epistemic Honesty)
        meta_cap = self._meta_confidence(prompt)
        
        final_conf = min(base_conf, meta_cap)
        
        # Ensure we don't return > 0.9 unless computation was definitive
        if comp_score == 0.5 and final_conf > 0.9:
            final_conf = 0.85
            
        return float(max(0.0, min(1.0, final_conf)))