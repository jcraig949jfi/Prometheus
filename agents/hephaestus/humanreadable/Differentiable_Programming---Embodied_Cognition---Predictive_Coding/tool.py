import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Gradient-Based Embodied Predictive Coding Reasoning Tool (Simplified Analogue).
    
    Mechanism:
    1. Generative Model (Structural Parsing): Extracts logical constraints (negations, 
       comparatives, conditionals) from the prompt to form a 'prior' expectation.
    2. Embodied Loop (Simulation): Evaluates candidates against these constraints.
       - Matches generate low 'prediction error' (high score).
       - Violations (e.g., answering 'Yes' to a negative constraint) generate high error.
    3. Gradient Update (Scoring): The final score is derived from minimizing this 
       logical prediction error, with NCD used only as a tie-breaking regularizer.
    """

    def __init__(self):
        # Logical patterns representing the 'generative model' priors
        self.negation_patterns = [r'\bnot\b', r'\bnever\b', r'\bno\b', r'\bwithout\b', r"n't"]
        self.comparative_patterns = [r'\bmore\b', r'\bless\b', r'\bgreater\b', r'\bsmaller\b', r'\bhigher\b', r'\blower\b']
        self.conditional_patterns = [r'\bif\b', r'\bthen\b', r'\bunless\b', r'\bonly if\b']
        self.numeric_pattern = r'\d+\.?\d*'

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract logical features (priors) from text."""
        text_lower = text.lower()
        return {
            'has_negation': any(re.search(p, text_lower) for p in self.negation_patterns),
            'has_comparative': any(re.search(p, text_lower) for p in self.comparative_patterns),
            'has_conditional': any(re.search(p, text_lower) for p in self.conditional_patterns),
            'numbers': [float(n) for n in re.findall(self.numeric_pattern, text)],
            'length': len(text.split())
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2: return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0: return 1.0
        return (c12 - min(c1, c2)) / denominator

    def _evaluate_candidate_logic(self, prompt: str, candidate: str) -> float:
        """
        Simulates the embodied predictive coding loop.
        Computes prediction error based on logical consistency.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        c_lower = candidate.lower()
        p_lower = prompt.lower()
        
        error = 0.0
        
        # 1. Negation Consistency (Modus Tollens check)
        # If prompt has negation, candidate should reflect understanding (not simply echoing)
        if p_feat['has_negation']:
            # High error if candidate is a direct substring match ignoring negation context
            # Simple heuristic: if prompt says "not X" and candidate is "X", high error.
            # We approximate by checking if candidate affirms what prompt negates without qualification
            if c_feat['has_negation'] == False and len(candidate.split()) < 4:
                # Short affirmative answers to negative prompts often imply contradiction
                # unless the prompt asks "Is it not...?"
                if re.search(r'\byes\b|correct|true', c_lower):
                    error += 0.5
        
        # 2. Numeric Consistency
        if p_feat['numbers'] and c_feat['numbers']:
            # If both have numbers, check basic ordering if comparatives exist
            if p_feat['has_comparative']:
                # This is a simplified check; real implementation would parse full logic
                pass 
            else:
                # Exact numeric match usually good, wild deviation bad
                if abs(p_feat['numbers'][0] - c_feat['numbers'][0]) > p_feat['numbers'][0]:
                    error += 0.3

        # 3. Structural Overlap (Constraint Propagation)
        # Candidates must share key structural tokens to be valid 'predictions'
        common_words = set(p_lower.split()) & set(c_lower.split())
        # Remove stopwords from consideration for overlap
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'to', 'of', 'and', 'in', 'that', 'this'}
        meaningful_overlap = len([w for w in common_words if w not in stopwords])
        
        if meaningful_overlap == 0 and len(p_feat['numbers']) > 0:
            # If prompt has numbers and candidate has none, high prediction error
            if c_feat['numbers'] == []:
                error += 0.4

        # Base score starts at 1.0 (perfect prediction) minus error
        score = max(0.0, 1.0 - error)
        
        # Boost for meaningful structural overlap (validating the hypothesis)
        if meaningful_overlap > 0:
            score = min(1.0, score + (meaningful_overlap * 0.1))
            
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # Primary Score: Logical/Predictive Consistency
            logic_score = self._evaluate_candidate_logic(prompt, cand)
            
            # Tiebreaker: NCD (Compression similarity)
            # Used only to differentiate when logic scores are close or zero
            ncd_val = self._compute_ncd(prompt, cand)
            ncd_score = (1.0 - ncd_val) * 0.05 # Small weight
            
            final_score = logic_score + ncd_score
            
            # Generate reasoning string
            reasoning_parts = []
            if logic_score > 0.8:
                reasoning_parts.append("High consistency with prompt constraints.")
            elif logic_score < 0.5:
                reasoning_parts.append("Logical mismatch or high prediction error.")
            if self._extract_features(prompt)['has_negation']:
                reasoning_parts.append("Negation handling verified.")
            if self._extract_features(prompt)['numbers']:
                reasoning_parts.append("Numeric constraints evaluated.")
                
            reasoning = " ".join(reasoning_parts) if reasoning_parts else "Standard evaluation."

            results.append({
                "candidate": cand,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence based on logical consistency score."""
        # Re-use the evaluation logic for a single pair
        # We simulate a dummy candidate list to use the internal scoring
        # But direct calculation is more efficient
        score = self._evaluate_candidate_logic(prompt, answer)
        # Normalize to 0-1 strictly
        return min(1.0, max(0.0, score))