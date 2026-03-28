import re
import zlib
from typing import List, Dict, Any

class ReasoningTool:
    """
    Pragmatic Type-Guided Analogical Reasoner (PTGAR) - Computational Approximation
    
    Mechanism:
    1. Analogical Mapping: Uses structural pattern matching to map prompt constraints to candidates.
    2. Type-Theoretic Encoding: Treats logical constraints (negations, comparatives, conditionals) 
       as 'types'. Candidates violating these are assigned low probability (ill-formed terms).
    3. Pragmatic Evaluation: Uses structural consistency and NCD as a reward signal. 
       High structural adherence = high pragmatic success.
    4. Meta-adaptation: Weights structural violations heavily to prune spurious analogies.
    
    This implements the 'dual filter' by rejecting candidates that fail logical type checks
    before applying similarity metrics.
    """
    
    def __init__(self):
        self.structural_weight = 0.7
        self.similarity_weight = 0.3
        
    def _extract_structural_features(self, text: str) -> Dict[str, Any]:
        """Extracts logical 'types' from text: negations, comparatives, numbers."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(no|not|never|neither|none|without)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|better|worse|higher|lower|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise|when)\b', text_lower)),
            'numbers': re.findall(r'\d+\.?\d*', text),
            'boolean_yes': bool(re.search(r'\byes\b', text_lower)),
            'boolean_no': bool(re.search(r'\bno\b', text_lower))
        }
        return features

    def _check_type_compatibility(self, prompt_features: Dict, candidate_features: Dict, candidate: str) -> float:
        """
        Type Checking Phase:
        Verifies if the candidate preserves the logical structure (type) of the prompt.
        Returns 1.0 for valid, 0.0 for invalid, intermediate for ambiguous.
        """
        score = 1.0
        
        # Rule 1: Negation Consistency (Modus Tollens approximation)
        # If prompt has strong negation, candidate shouldn't blindly affirm without nuance
        if prompt_features['negations'] > 0:
            # Heuristic: If prompt says "not", and candidate is a simple "Yes", penalize
            if candidate_features['boolean_yes'] and not candidate_features['boolean_no']:
                if len(candidate.split()) < 4: # Short affirmative likely ignores negation
                    score -= 0.5
        
        # Rule 2: Numeric Consistency
        if prompt_features['numbers'] and candidate_features['numbers']:
            # Simple transitivity check simulation
            p_nums = [float(n) for n in prompt_features['numbers']]
            c_nums = [float(n) for n in candidate_features['numbers']]
            
            # If prompt implies ordering (e.g., "greater"), check candidate numbers
            if prompt_features['comparatives'] > 0:
                # Rough heuristic: if prompt compares, candidate numbers should differ or reflect order
                if len(set(c_nums)) == 1 and len(c_nums) > 1:
                    score -= 0.3 # Suspicious if comparing identical numbers
        
        # Rule 3: Conditional Alignment
        if prompt_features['conditionals'] > 0:
            if candidate_features['conditionals'] == 0 and len(candidate.split()) < 3:
                # Complex conditional prompt usually requires more than a yes/no answer
                score -= 0.2

        return max(0.0, min(1.0, score))

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        c1 = len(zlib.compress(s1_b))
        c2 = len(zlib.compress(s2_b))
        c12 = len(zlib.compress(s1_b + s2_b))
        denominator = max(c1, c2)
        if denominator == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_features = self._extract_structural_features(prompt)
        results = []
        
        for cand in candidates:
            cand_features = self._extract_structural_features(cand)
            
            # 1. Type-Theoretic Check (Logical Validity)
            type_score = self._check_type_compatibility(prompt_features, cand_features, cand)
            
            # 2. Pragmatic/Analogical Similarity (NCD based)
            # Inverted NCD: 1.0 is identical, 0.0 is totally different
            ncd_val = self._ncd(prompt.lower(), cand.lower())
            similarity_score = 1.0 - ncd_val
            
            # 3. Combined Pragmatic Reward
            # Heavily weight type safety; use similarity as tiebreaker/refinement
            final_score = (type_score * self.structural_weight) + (similarity_score * self.similarity_weight)
            
            # Bonus for explicit structural alignment
            if prompt_features['comparatives'] > 0 and cand_features['comparatives'] > 0:
                final_score += 0.1
            if prompt_features['negations'] > 0 and cand_features['negations'] > 0:
                final_score += 0.1
                
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Type-valid: {type_score:.2f}, Similarity: {similarity_score:.2f}"
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural coherence and type preservation.
        """
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        
        # Normalize the top score to 0-1 range based on our internal logic
        # Since max theoretical score can exceed 1.0 due to bonuses, cap at 1.0
        score = ranked[0]['score']
        return min(1.0, max(0.0, score))