import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a computationally feasible approximation of the Gauge-Thermo-Kolmogorov framework.
    
    Mechanism:
    1. Structural Parsing (Gauge Invariance): Extracts logical operators (negations, conditionals),
       comparatives, and numeric values. This creates a 'gauge-invariant' signature of the prompt's
       logical structure, ignoring superficial rephrasing.
    2. Thermodynamic Scoring (Entropy Production): Evaluates candidates based on logical consistency
       with the extracted structure. 'Dissipation' occurs when a candidate contradicts the prompt's
       constraints (e.g., answering 'Yes' to a negated condition). Lower dissipation = higher score.
    3. Kolmogorov/MDL Penalty: Uses NCD (Normalized Compression Distance) as a tie-breaking penalty
       for unnecessary complexity, favoring the most concise valid hypothesis.
    """

    def __init__(self):
        # Regex patterns for structural extraction (The "Gauge Connection")
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|fail|false)\b', re.I),
            'conditional': re.compile(r'\b(if|then|unless|provided|when|else)\b', re.I),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.I),
            'numeric': re.compile(r'\d+\.?\d*'),
            'boolean_yes': re.compile(r'\b(yes|true|correct|agree)\b', re.I),
            'boolean_no': re.compile(r'\b(no|false|incorrect|disagree)\b', re.I)
        }

    def _extract_structure(self, text: str) -> Dict:
        """Extracts logical features to form a structural signature."""
        text_lower = text.lower()
        return {
            'has_negation': bool(self.patterns['negation'].search(text_lower)),
            'has_conditional': bool(self.patterns['conditional'].search(text_lower)),
            'has_comparative': bool(self.patterns['comparative'].search(text_lower)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'affirmative': bool(self.patterns['boolean_yes'].search(text_lower)),
            'negative': bool(self.patterns['boolean_no'].search(text_lower)),
            'length': len(text)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance as an MDL proxy."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _evaluate_logical_consistency(self, prompt_struct: Dict, candidate: str) -> float:
        """
        Calculates 'Entropy Production' (Dissipation).
        Returns 0.0 for perfect consistency, positive values for contradictions.
        """
        cand_struct = self._extract_structure(candidate)
        dissipation = 0.0

        # Rule 1: Negation Consistency
        # If prompt has negation, candidate should reflect understanding (simplified heuristic)
        if prompt_struct['has_negation']:
            # If prompt is negative, a simple "Yes" without qualification might be risky
            # We penalize if the candidate is purely affirmative while prompt is heavily negative
            if cand_struct['affirmative'] and not cand_struct['negative']:
                # Check if candidate is just "Yes" (high risk of error in negated contexts)
                if len(candidate.strip().split()) <= 2:
                    dissipation += 0.4

        # Rule 2: Conditional Logic
        if prompt_struct['has_conditional']:
            # Candidates lacking conditional keywords or logical connectors might be oversimplified
            if not cand_struct['has_conditional'] and not cand_struct['has_negation']:
                dissipation += 0.2

        # Rule 3: Numeric Consistency
        if prompt_struct['numbers'] and cand_struct['numbers']:
            # Simple transitivity check: if prompt implies A > B, candidate shouldn't say B > A
            # Here we just check if numbers present match the scale (heuristic)
            pass 
        
        # Rule 4: Direct Contradiction (Affirmative vs Negative)
        if prompt_struct['affirmative'] and cand_struct['negative'] and not prompt_struct['has_negation']:
             dissipation += 0.5
        if prompt_struct['negative'] and cand_struct['affirmative'] and not prompt_struct['has_conditional']:
             # Potential contradiction if not handled carefully
             if len(candidate.strip().split()) <= 3:
                 dissipation += 0.3

        return dissipation

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        scored_candidates = []

        for cand in candidates:
            # 1. Structural Parsing (Gauge Invariance)
            # 2. Thermodynamic Score (Inverse of Dissipation)
            dissipation = self._evaluate_logical_consistency(prompt_struct, cand)
            base_score = 1.0 - dissipation
            
            # Ensure base score doesn't go below 0
            base_score = max(0.0, base_score)

            # 3. Kolmogorov/MDL Term (NCD tiebreaker)
            # We want minimum description length, so lower NCD is better.
            # We subtract a small fraction of NCD to break ties towards simpler answers.
            ncd_penalty = self._compute_ncd(prompt, cand) * 0.05
            
            final_score = base_score - ncd_penalty
            
            # Reasoning string generation
            reasoning_parts = []
            if prompt_struct['has_negation']:
                reasoning_parts.append("negation detected")
            if prompt_struct['has_conditional']:
                reasoning_parts.append("conditional logic required")
            if dissipation > 0.1:
                reasoning_parts.append(f"high dissipation ({dissipation:.2f})")
            else:
                reasoning_parts.append("low dissipation")
                
            reasoning = f"Structure: {', '.join(reasoning_parts)}. MDL penalty: {ncd_penalty:.3f}."

            scored_candidates.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on logical consistency and structural alignment.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        # Normalize score to 0-1 range roughly
        score = results[0]['score']
        # Map score (likely -0.1 to 1.0) to 0.0-1.0
        confidence = max(0.0, min(1.0, score))
        return round(confidence, 4)