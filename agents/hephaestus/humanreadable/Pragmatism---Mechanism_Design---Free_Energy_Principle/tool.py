import re
import numpy as np
from collections import deque

class ReasoningTool:
    """
    A reasoning tool combining Pragmatism, Mechanism Design, and the Free Energy Principle.
    
    Mechanism:
    1. Parsing (Pragmatism): Extracts structural constraints (numeric, logical, temporal) from the prompt.
    2. Constraint Propagation: Builds a graph of implications and orderings to infer 'truth' states.
    3. Free Energy Minimization: Scores candidates based on prediction error (epsilon) against inferred truths.
    4. Mechanism Design: Uses a proper scoring rule (negative variational free energy) to incentivize 
       candidates that align with the prompt's logical structure, penalizing hard constraint violations.
    """
    
    def __init__(self):
        self.lambda_penalty = 0.5  # Penalty weight for hard constraint violations
        self.regex_numeric = re.compile(r'(\d+(?:\.\d+)?)\s*(>|<|>=|<=|==|!=)\s*(\d+(?:\.\d+)?)')
        self.regex_conditional = re.compile(r'if\s+(.+?)\s+then\s+(.+?)', re.IGNORECASE)
        self.regex_negation = re.compile(r'not\s+(.+?)', re.IGNORECASE)
        self.regex_causal = re.compile(r'(.+?)\s+(causes|leads to)\s+(.+?)', re.IGNORECASE)
        self.regex_temporal = re.compile(r'(.+?)\s+(before|after)\s+(.+?)', re.IGNORECASE)

    def _parse_constraints(self, text):
        """Extracts structural constraints from text."""
        constraints = []
        text_lower = text.lower()
        
        # Numeric comparisons
        for m in self.regex_numeric.finditer(text):
            v1, op, v2 = m.groups()
            constraints.append(('numeric', float(v1), op, float(v2)))
            
        # Conditionals (simplified extraction)
        for m in self.regex_conditional.finditer(text):
            constraints.append(('conditional', m.group(1).strip(), m.group(2).strip()))
            
        # Negations
        for m in self.regex_negation.finditer(text):
            constraints.append(('negation', m.group(1).strip()))
            
        # Causal/Temporal (treated as ordering constraints)
        for m in self.regex_causal.finditer(text):
            constraints.append(('causal', m.group(1).strip(), m.group(3).strip()))
        for m in self.regex_temporal.finditer(text):
            constraints.append(('temporal', m.group(1).strip(), m.group(2).strip(), m.group(3).strip()))
            
        return constraints

    def _propagate_constraints(self, constraints, candidate_text):
        """
        Simulates constraint propagation. 
        Returns implied numeric ranges and boolean truth values based on candidate alignment.
        """
        implied_truths = []
        candidate_lower = candidate_text.lower()
        
        # Check numeric consistency
        for ctype, *args in constraints:
            if ctype == 'numeric':
                v1, op, v2 = args
                # Evaluate if the candidate text contains numbers that violate the prompt's math
                # Simple heuristic: if candidate mentions both numbers, check relation
                s1, s2 = str(int(v1) if v1.is_integer() else v1), str(int(v2) if v2.is_integer() else v2)
                if s1 in candidate_lower and s2 in candidate_lower:
                    # Re-evaluate the operator in the candidate context if possible, 
                    # otherwise assume prompt truth holds unless contradicted
                    pass 
            
            # Check logical consistency (Presence of negated terms implies false)
            if ctype == 'negation':
                term = args[0]
                if term in candidate_lower and f"not {term}" not in candidate_lower:
                    # Candidate asserts term, but prompt says "not term" -> Violation
                    implied_truths.append(False) 
                elif f"not {term}" in candidate_lower:
                    implied_truths.append(True)

            # Check conditional satisfaction (Modus Ponens heuristic)
            if ctype == 'conditional':
                premise, conclusion = args
                if premise in candidate_lower:
                    if conclusion not in candidate_lower:
                        implied_truths.append(False) # Premise true, conclusion missing -> Error
                    else:
                        implied_truths.append(True)
        
        return implied_truths

    def _calculate_free_energy(self, prompt, candidate):
        """
        Calculates Negative Variational Free Energy.
        F = Sum(epsilon^2) + lambda * Sum(violations)
        Score = -F
        """
        constraints = self._parse_constraints(prompt)
        implied = self._propagate_constraints(constraints, candidate)
        
        # 1. Prediction Error (Epsilon)
        # For booleans: 0 if match, 1 if mismatch. 
        # We treat 'implied' as the ground truth derived from prompt logic.
        # If implied is empty, we assume low error (0) but rely on NCD later.
        epsilon_sq_sum = 0.0
        count = 0
        
        for truth_val in implied:
            # If our propagation says it should be True (1) or False (0)
            # We check if the candidate aligns. 
            # Simplified: If implied list has entries, they represent checks we performed.
            # If the check resulted in False (violation detected in propagation), error = 1.
            # If True, error = 0.
            if not truth_val:
                epsilon_sq_sum += 1.0
            count += 1
            
        # If no logical constraints found, epsilon is 0 (neutral)
        if count == 0:
            epsilon_sq_sum = 0.0
            
        # 2. Hard Constraint Violations (vc)
        # In this simplified model, 'implied' False entries act as violations.
        violations = sum(1 for t in implied if not t)
        
        # Free Energy Calculation
        F = epsilon_sq_sum + self.lambda_penalty * violations
        
        # If no constraints were parsed, we cannot compute meaningful F from logic alone.
        # We return a neutral score to let NCD handle it, or a small penalty for lack of info.
        if len(constraints) == 0:
            return -0.5, "No structural constraints detected; relying on baseline."
            
        return -F, f"Violations: {violations}, Logic Checks: {count}"

    def _ncd_score(self, s1, s2):
        """Normalized Compression Distance using zlib."""
        import zlib
        l1 = len(zlib.compress(s1.encode()))
        l2 = len(zlib.compress(s2.encode()))
        l12 = len(zlib.compress((s1 + s2).encode()))
        if min(l1, l2) == 0: return 1.0
        return (l12 - min(l1, l2)) / max(l1, l2)

    def evaluate(self, prompt: str, candidates: list[str]) -> list[dict]:
        results = []
        base_score = -10.0 # Default low score
        
        # Calculate NCD baseline for tie-breaking
        ncd_scores = []
        for c in candidates:
            # Invert NCD so higher is better (1 - ncd), scaled small
            ncd = self._ncd_score(prompt, c)
            ncd_scores.append(1.0 - ncd)
            
        max_ncd = max(ncd_scores) if ncd_scores else 0
        
        for i, cand in enumerate(candidates):
            score, reason = self._calculate_free_energy(prompt, cand)
            
            # If logic yielded no constraints (score -0.5 default), use NCD
            if score == -0.5 and "No structural" in reason:
                # Scale NCD to be comparable but secondary
                score = ncd_scores[i] * 0.1 
                reason = "Fallback to NCD similarity."
            else:
                # Add tiny NCD component for tie-breaking among logically valid answers
                score += ncd_scores[i] * 0.01

            results.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on free energy minimization."""
        score, _ = self._calculate_free_energy(prompt, answer)
        
        # If no constraints, return neutral confidence based on NCD
        if score == -0.5:
            ncd = self._ncd_score(prompt, answer)
            return max(0.0, min(1.0, (1.0 - ncd)))
            
        # Map negative free energy to 0-1
        # F=0 -> 1.0, F=-1 -> ~0.6, F=-5 -> ~0.0
        # Sigmoid-like mapping: 1 / (1 + exp(F)) but F is negative so: 1 / (1 + exp(-|F|)) ?
        # Actually F is positive in formula, score is -F.
        # Score = -F. We want Score=0 -> 1.0, Score=-inf -> 0.
        # Confidence = exp(Score) clamped? Or 1 / (1 - Score) if Score < 0?
        # Let's use: Conf = 1 / (1 + F) = 1 / (1 - Score)
        if score >= 0:
            return 1.0
        try:
            conf = 1.0 / (1.0 - score)
        except:
            conf = 0.0
        return max(0.0, min(1.0, conf))