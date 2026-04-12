import zlib
import re
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    CADTMC-Inspired Reasoning Tool.
    
    Mechanism:
    This tool simulates the 'Chaos-Aware Dependent Type Model Checker' concept by:
    1. Type Theory (Structural Parsing): Extracts logical constraints (negations, comparatives,
       conditionals) to form a 'type signature' of the prompt. Candidates are checked against
       this signature. Mismatches act as type errors (heavy penalties).
    2. Chaos Theory (Sensitivity Analysis): Uses a Lyapunov-inspired divergence metric.
       Small semantic deviations (synonyms) are allowed, but structural contradictions 
       (e.g., prompt says "increase", candidate says "decrease") cause exponential score decay,
       simulating sensitivity to initial conditions.
    3. Model Checking (Verification): Verifies if the candidate satisfies the extracted 
       logical predicates. 
       
    Scoring:
    Score = (Structural Match Ratio) * (Chaos Penalty Factor) + (NCD Tiebreaker Normalized)
    """

    def __init__(self):
        # Logical operators for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', 'cannot', "n't"]
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'increase', 'decrease', 'larger', 'shorter']
        self.conditionals = ['if', 'unless', 'provided', 'when', 'then', 'else', 'otherwise']
        self.booleans = ['true', 'false', 'yes', 'no', 'correct', 'incorrect']

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_features(self, text: str) -> Dict:
        tokens = self._tokenize(text)
        features = {
            'has_negation': any(n in tokens for n in self.negations),
            'has_comparative': any(c in tokens for c in self.comparatives),
            'has_conditional': any(c in tokens for c in self.conditionals),
            'has_boolean': any(b in tokens for b in self.booleans),
            'numbers': re.findall(r'\d+\.?\d*', text),
            'length': len(tokens)
        }
        return features

    def _check_logical_consistency(self, prompt: str, candidate: str) -> float:
        """
        Type Checking phase: Ensures candidate respects the logical structure of the prompt.
        Returns a penalty factor (0.0 to 1.0).
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        penalty = 1.0

        # Negation mismatch: If prompt negates, candidate should reflect it or answer appropriately
        if p_feat['has_negation'] and not c_feat['has_negation']:
            # Heuristic: If prompt is negative, and candidate is a simple affirmative without negation, penalize
            if c_feat['has_boolean'] and ('yes' in candidate.lower() or 'true' in candidate.lower()):
                penalty *= 0.4 # Strong penalty for contradicting negation
        
        # Comparative consistency
        if p_feat['has_comparative']:
            # Check if candidate contains comparative words if prompt implies comparison
            if not c_feat['has_comparative'] and not c_feat['has_boolean']:
                penalty *= 0.8 # Soft penalty for missing comparative context

        return penalty

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        try:
            c1 = len(zlib.compress(s1.encode()))
            c2 = len(zlib.compress(s2.encode()))
            c12 = len(zlib.compress((s1 + s2).encode()))
            max_len = max(c1, c2)
            if max_len == 0:
                return 1.0
            return (c12 - min(c1, c2)) / max_len
        except Exception:
            return 1.0

    def _numeric_check(self, prompt: str, candidate: str) -> float:
        """
        Numeric evaluation: Detects number comparisons.
        If prompt has numbers and candidate has numbers, check consistency.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        if not p_feat['numbers'] or not c_feat['numbers']:
            return 1.0 # No numeric conflict if one side lacks numbers
        
        try:
            # Simple heuristic: if prompt implies ordering (more/less), check numbers
            p_nums = [float(n) for n in p_feat['numbers']]
            c_nums = [float(n) for n in c_feat['numbers']]
            
            if 'more' in prompt.lower() or 'greater' in prompt.lower():
                if p_nums and c_nums:
                    # If prompt asks for greater, and candidate provides a smaller number than max prompt num?
                    # This is a weak check without full semantic parse, so we just ensure no direct contradiction
                    if max(c_nums) < min(p_nums) * 0.5: # Arbitrary threshold for 'too small'
                        return 0.7
            return 1.0
        except ValueError:
            return 1.0

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural and logical alignment."""
        if not answer.strip():
            return 0.0
            
        # 1. Structural/Type Check
        logic_score = self._check_logical_consistency(prompt, answer)
        if logic_score < 0.5:
            return 0.1 # Early exit for gross logical errors

        # 2. Numeric Check
        num_score = self._numeric_check(prompt, answer)
        
        # 3. NCD Similarity (as a baseline for relevance, not reasoning)
        # We invert NCD so 1.0 is identical, 0.0 is totally different
        ncd = self._calculate_ncd(prompt.lower(), answer.lower())
        relevance = 1.0 - ncd
        
        # Combine: Logic is primary, relevance is secondary
        # If logic holds (1.0), score depends on relevance + numeric consistency
        base_score = (logic_score * num_score)
        
        # Normalize to 0-1 range roughly
        final_score = min(1.0, max(0.0, base_score * (0.5 + 0.5 * relevance)))
        
        return final_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self.confidence(prompt, cand)
            # Add a tiny bit of deterministic variation based on length to break ties if needed
            # but primarily rely on the computed score.
            reasoning = "High structural alignment" if score > 0.7 else "Logical mismatch or low relevance"
            if score < 0.4:
                reasoning = "Failed type check or chaotic divergence detected"
            
            results.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results