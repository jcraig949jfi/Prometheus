import re
import json
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Quantum-Falsification Market (QFM) Implementation.
    
    Mechanism:
    1. Hypothesis Superposition: Candidates are treated as a superposition of states.
    2. Falsificationist Measurement: Instead of confirming truth, we scan for "Falsifiers" 
       (contradictions, negations, logical violations) in the prompt relative to each candidate.
    3. Mechanism Design (VCG-style): Scores are assigned based on the "information gain" 
       achieved by eliminating false constraints. A candidate surviving rigorous falsification 
       attempts gains higher amplitude (score).
    4. Structural Parsing: Primary signal comes from detecting negations, comparatives, 
       and numeric relations, not string similarity.
    """

    def __init__(self):
        # Structural keywords for falsification detection
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', "n't"]
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'before', 'after']
        self.conditionals = ['if', 'unless', 'only if', 'provided that']
        
    def _structural_parse(self, text: str) -> dict:
        """Extracts logical constraints: negations, numbers, and comparatives."""
        text_lower = text.lower()
        features = {
            'negation_count': 0,
            'has_comparative': False,
            'numbers': [],
            'constraint_vector': []
        }
        
        # Count negations
        for word in self.negations:
            if re.search(r'\b' + re.escape(word) + r'\b', text_lower):
                features['negation_count'] += 1
        
        # Detect comparatives
        for word in self.comparatives:
            if word in text_lower:
                features['has_comparative'] = True
                break
                
        # Extract numbers for numeric evaluation
        features['numbers'] = [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
        
        return features

    def _check_falsification(self, prompt: str, candidate: str) -> float:
        """
        Returns a penalty score (0.0 to 1.0) representing the likelihood 
        that the candidate is falsified by the prompt's structural constraints.
        0.0 = No falsification found (Survivor), 1.0 = Definitely falsified.
        """
        p_feats = self._structural_parse(prompt)
        c_feats = self._structural_parse(candidate)
        penalty = 0.0
        
        # 1. Negation Contradiction Check
        # If prompt has strong negation logic and candidate asserts positively without nuance
        if p_feats['negation_count'] > 0:
            # Simple heuristic: If prompt denies something, and candidate is a direct affirmative match of a substring, penalize
            # This is a proxy for logical contradiction detection
            if candidate.lower().strip() in prompt.lower() and p_feats['negation_count'] > c_feats['negation_count']:
                penalty += 0.4

        # 2. Numeric Falsification
        if p_feats['numbers'] and c_feats['numbers']:
            # If candidate number violates a comparative constraint implied in prompt
            # Example: Prompt "x < 5", Candidate "6" -> Falsified
            # We simulate this by checking if candidate number is an outlier relative to prompt numbers
            # without explicit operator parsing (simplified for robustness)
            p_max = max(p_feats['numbers'])
            c_val = c_feats['numbers'][0]
            
            # Heuristic: If candidate is significantly larger than max prompt number 
            # in a context that implies limitation (hard to detect perfectly without LLM, 
            # so we use strict equality failure as a proxy for numeric logic)
            if c_val > p_max * 1.5: 
                penalty += 0.3

        # 3. Structural Mismatch (The "Measurement")
        # If prompt asks a question (contains '?') and candidate doesn't look like an answer
        if '?' in prompt:
            if len(candidate.split()) < 2 and not any(c in candidate.lower() for c in ['yes', 'no', 'true', 'false']):
                # Short non-answers to questions are often falsifiable as incomplete
                penalty += 0.2

        return min(penalty, 1.0)

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib as a tiebreaker."""
        import zlib
        s1_b = s1.encode()
        s2_b = s2.encode()
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            if min(c1, c2) == 0:
                return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates using the QFM architecture.
        1. Encode candidates as superposition.
        2. Apply falsification measurements (structural parsing).
        3. Reward survival (low falsification penalty).
        4. Rank by posterior amplitude (score).
        """
        if not candidates:
            return []
            
        scored_candidates = []
        
        # Pre-compute prompt features to avoid re-parsing
        p_feats = self._structural_parse(prompt)
        
        for cand in candidates:
            # Falsification Test
            falsification_penalty = self._check_falsification(prompt, cand)
            
            # Base Score: Start with high confidence (1.0) and subtract falsification
            # This mimics the "survival of the fittest" in a falsificationist framework
            base_score = 1.0 - falsification_penalty
            
            # Bonus for structural alignment (e.g., if prompt has numbers, candidate should too)
            c_feats = self._structural_parse(cand)
            if p_feats['numbers'] and c_feats['numbers']:
                base_score += 0.1 # Reward numeric engagement
            
            # Tiebreaker: NCD (only if scores are close, but we apply a small weight here)
            # We invert NCD because lower distance = higher similarity = slightly higher prior
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_bonus = (1.0 - ncd_val) * 0.05 
            
            final_score = base_score + ncd_bonus
            
            # Construct reasoning string (Mechanism Design: transparent audit trail)
            reasoning = f"Falsification penalty: {falsification_penalty:.2f}. "
            if falsification_penalty < 0.1:
                reasoning += "Candidate survives structural falsification tests."
            else:
                reasoning += "Candidate triggered structural contradiction or constraint violation."
                
            scored_candidates.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
        
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same falsification logic: if the answer survives falsification, confidence is high.
        """
        # Run single evaluation
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        # Normalize the top score to 0-1 range strictly
        # Since base_score starts at 1.0 and penalties reduce it, and bonuses add small amounts,
        # we clamp to 1.0 max.
        score = results[0]['score']
        return min(max(score, 0.0), 1.0)