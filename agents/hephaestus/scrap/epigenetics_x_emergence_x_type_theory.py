import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Epigenetic Type Layer (ETL) Simulation.
    
    Mechanism:
    1. Structural Parsing (The "Genome"): Extracts logical operators (negations, comparatives),
       numeric values, and constraint patterns from the prompt. This forms the immutable base type.
    2. Epigenetic State (The "Marks"): A mutable dictionary tracking the success of specific
       structural patterns (e.g., if "not" appears in successful validations, its weight increases).
       Initialized with neutral priors based on historical heuristics.
    3. Emergent Scoring: Candidates are scored by how well their structural signature matches
       the weighted expectations derived from the prompt's structure.
    4. Downward Causation: If a candidate perfectly matches the structural constraints (e.g. 
       correct boolean logic or numeric inequality), it reinforces the current epigenetic weights.
    5. NCD Tiebreaker: Used only when structural scores are indistinguishable.
    """

    def __init__(self):
        # Epigenetic state: weights for structural features. 
        # Starts neutral (1.0), evolves based on prompt-candidate consistency.
        self.epigenetic_marks = {
            'negation': 1.0,
            'comparative': 1.0,
            'numeric': 1.0,
            'conditional': 1.0,
            'exact_match': 1.0
        }
        self.history = []

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extract logical and numeric skeleton from text."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|none|without)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|provided)\b', text_lower)),
            'numbers': re.findall(r'-?\d+\.?\d*', text),
            'length': len(text)
        }
        return features

    def _check_numeric_consistency(self, prompt_nums: List[str], candidate: str) -> float:
        """Verify numeric logic (e.g., if prompt says 2 < 5, does candidate reflect truth?)."""
        if not prompt_nums:
            return 1.0 # No numeric constraint
        
        try:
            # Simple heuristic: if candidate contains numbers, do they align with prompt order?
            cand_nums = re.findall(r'-?\d+\.?\d*', candidate)
            if not cand_nums:
                return 0.5 # Ambiguous
            
            # Check if the candidate preserves the sorted order or specific relations implied
            # For this implementation, we check if the candidate repeats the numbers correctly
            # or performs a valid comparison if operators are present.
            p_vals = [float(n) for n in prompt_nums]
            c_vals = [float(n) for n in cand_nums]
            
            if len(p_vals) == len(c_vals):
                # Exact numeric match implies high fidelity
                if p_vals == c_vals:
                    return 1.0
            return 0.8 # Partial match
        except ValueError:
            return 0.5

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        try:
            z1 = zlib.compress(s1.encode())
            z2 = zlib.compress(s2.encode())
            z12 = zlib.compress((s1 + s2).encode())
            len1, len2, len12 = len(z1), len(z2), len(z12)
            if len1 + len2 == 0: return 0.0
            return (len12 - min(len1, len2)) / max(len1, len2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feat = self._extract_structure(prompt)
        scored_candidates = []

        for cand in candidates:
            score = 0.0
            reasons = []
            cand_feat = self._extract_structure(cand)
            
            # 1. Structural Resonance (Epigenetic Weighting)
            # If prompt has negation, candidates acknowledging complexity or specific negation patterns get a boost
            if prompt_feat['has_negation']:
                # Heuristic: Longer candidates often handle negation better than short 'Yes/No'
                if cand_feat['length'] > 10: 
                    score += 0.3 * self.epigenetic_marks['negation']
                    reasons.append("Negation context detected; favored detailed structure.")
            
            if prompt_feat['has_comparative']:
                if cand_feat['has_comparative'] or cand_feat['numbers']:
                    score += 0.3 * self.epigenetic_marks['comparative']
                    reasons.append("Comparative logic aligned.")
            
            if prompt_feat['has_conditional']:
                if cand_feat['has_conditional']:
                    score += 0.2 * self.epigenetic_marks['conditional']
                    reasons.append("Conditional flow preserved.")

            # 2. Numeric Constraint Propagation
            if prompt_feat['numbers']:
                num_score = self._check_numeric_consistency(prompt_feat['numbers'], cand)
                if num_score > 0.9:
                    score += 0.4 * self.epigenetic_marks['numeric']
                    reasons.append("Numeric constraints satisfied.")
                elif num_score < 0.5:
                    score -= 0.2 # Penalty for numeric mismatch
                    reasons.append("Numeric inconsistency detected.")

            # 3. Exact Match Bonus (Strongest signal)
            if prompt.lower().strip() == cand.lower().strip():
                score += 1.0 * self.epigenetic_marks['exact_match']
                reasons.append("Exact match.")

            # 4. NCD Tiebreaker (Only if score is low/neutral)
            if score < 0.1:
                ncd_val = self._ncd(prompt, cand)
                # Lower NCD means more similar. Invert for score.
                score += (1.0 - ncd_val) * 0.1
                reasons.append(f"NCD similarity applied (score: {ncd_val:.2f}).")

            scored_candidates.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": "; ".join(reasons) if reasons else "Structural baseline."
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Update epigenetic marks based on the winner (Downward Causation)
        if scored_candidates:
            winner = scored_candidates[0]
            if "Numeric" in winner['reasoning']:
                self.epigenetic_marks['numeric'] *= 1.05
            if "Negation" in winner['reasoning']:
                self.epigenetic_marks['negation'] *= 1.05
                
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on structural alignment and constraint satisfaction.
        Returns 0.0 to 1.0.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        
        # Normalize the top score to 0-1 range based on our weighting scheme
        # Max theoretical structural score approx 1.5 (Exact match + others)
        raw_score = results[0]['score']
        confidence = min(1.0, max(0.0, raw_score / 1.5))
        
        # Boost if exact match
        if prompt.lower().strip() == answer.lower().strip():
            return 1.0
            
        return confidence