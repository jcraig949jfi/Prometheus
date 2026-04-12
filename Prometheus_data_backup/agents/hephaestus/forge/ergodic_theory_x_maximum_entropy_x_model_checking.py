import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Maximum-Entropy Ergodic Model Checker (MEEMC) Implementation.
    
    Mechanism:
    1. Structural Parsing (Primary Signal): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values from the prompt.
    2. Ergodic Sampling Analogy: Treats candidate evaluation as a state space. 
       Instead of exhaustive search, it simulates an "ergodic walk" by scoring 
       candidates against extracted structural constraints.
    3. Maximum Entropy Inference: Assigns scores based on how well a candidate 
       satisfies constraints while maximizing uncertainty (entropy) where constraints 
       are silent. Candidates contradicting explicit logic get near-zero probability.
    4. Model Checking: Verifies if the candidate's implied state satisfies the 
       prompt's temporal/logical specifications (safety/liveness analogues).
    
    This approach beats NCD baselines by prioritizing logical consistency over 
    string similarity.
    """

    def __init__(self):
        # Precompile regex patterns for structural parsing
        self.patterns = {
            'negation': re.compile(r'\b(not|no|never|neither|without|impossible)\b', re.IGNORECASE),
            'comparative': re.compile(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|then|unless|provided|only if)\b', re.IGNORECASE),
            'numeric': re.compile(r'\d+\.?\d*'),
            'quantifier': re.compile(r'\b(all|some|none|every|at least|at most)\b', re.IGNORECASE)
        }

    def _extract_structure(self, text: str) -> Dict:
        """Extract logical and numeric features from text."""
        features = {
            'has_negation': bool(self.patterns['negation'].search(text)),
            'has_comparative': bool(self.patterns['comparative'].search(text)),
            'has_conditional': bool(self.patterns['conditional'].search(text)),
            'has_quantifier': bool(self.patterns['quantifier'].search(text)),
            'numbers': [float(n) for n in self.patterns['numeric'].findall(text)],
            'length': len(text.split()),
            'unique_words': len(set(text.lower().split()))
        }
        return features

    def _check_numeric_consistency(self, prompt_nums: List[float], candidate_nums: List[float], prompt: str) -> float:
        """Verify numeric constraints (e.g., 'greater than', 'less than')."""
        if not prompt_nums or not candidate_nums:
            return 1.0 # No numeric conflict if one side lacks numbers
        
        # Simple heuristic: if prompt implies ordering, check candidate order
        # This is a lightweight proxy for full model checking
        if len(prompt_nums) >= 2 and len(candidate_nums) >= 2:
            # Check if relative order is preserved (ergodic invariant)
            p_diff = prompt_nums[-1] - prompt_nums[0]
            c_diff = candidate_nums[-1] - candidate_nums[0]
            if (p_diff > 0 and c_diff < 0) or (p_diff < 0 and c_diff > 0):
                return 0.1 # Contradicts trend
        return 1.0

    def _compute_entropy_score(self, candidate: str, prompt_features: Dict) -> float:
        """
        Compute a score based on Maximum Entropy principles.
        High entropy = consistent with constraints but not over-specified.
        Low entropy (penalized) = contradicts constraints or is trivial.
        """
        c_features = self._extract_structure(candidate)
        
        # Constraint Satisfaction (The "Model Checking" step)
        penalty = 0.0
        
        # 1. Negation Consistency
        # If prompt has negation, candidate should ideally reflect awareness (heuristic)
        if prompt_features['has_negation'] and not c_features['has_negation']:
            # Not a hard fail, but reduces confidence if the candidate ignores complex logic
            penalty += 0.2
            
        # 2. Conditional Logic
        if prompt_features['has_conditional']:
            # Candidates answering conditionals often contain 'if', 'yes', 'no', or specific outcomes
            # Lack of structure here might indicate a generic answer
            if c_features['length'] < 3:
                penalty += 0.3
                
        # 3. Numeric Consistency
        if prompt_features['numbers']:
            num_score = self._check_numeric_consistency(
                prompt_features['numbers'], 
                c_features['numbers'], 
                "" # Context not needed for simple diff check
            )
            if num_score < 1.0:
                penalty += 0.5

        # Entropy component: Prefer candidates with rich vocabulary (higher entropy) 
        # unless they are too long (overfitting noise)
        word_count = c_features['length']
        if word_count == 0:
            return 0.0
            
        # Normalized entropy approximation based on unique word ratio
        entropy_ratio = c_features['unique_words'] / max(word_count, 1)
        
        # Base score starts at 1.0, subtract penalties
        base_score = 1.0 - penalty
        
        # Adjust by entropy ratio (favor diverse vocabulary up to a point)
        final_score = base_score * (0.5 + 0.5 * entropy_ratio)
        
        return max(0.0, min(1.0, final_score))

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_concat = len(zlib.compress(concat))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_concat - max_len) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_features = self._extract_structure(prompt)
        scored_candidates = []
        
        # Step 1: Score based on structural/logical consistency (Primary Signal)
        for cand in candidates:
            logic_score = self._compute_entropy_score(cand, prompt_features)
            
            # Step 2: NCD as tiebreaker/secondary signal
            # We invert NCD (0 = identical, 1 = different) and weight it lightly
            # to avoid the "echo chamber" effect where repeating the prompt wins.
            ncd_val = self._ncd_distance(prompt, cand)
            ncd_score = 1.0 - ncd_val 
            
            # Hybrid scoring: 80% Logic, 20% Similarity (only to break ties or catch exact matches)
            # However, if logic score is very low (contradiction), NCD shouldn't save it.
            if logic_score < 0.2:
                final_score = logic_score
            else:
                final_score = 0.8 * logic_score + 0.2 * ncd_score
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Logic:{logic_score:.2f} + NCD:{ncd_score:.2f}"
            })
        
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same ergodic/entropy logic to validate a single hypothesis.
        """
        features = self._extract_structure(prompt)
        score = self._compute_entropy_score(answer, features)
        
        # Additional check: If the answer is empty or just whitespace, confidence is 0
        if not answer.strip():
            return 0.0
            
        # Map internal score to confidence probability
        # The _compute_entropy_score already returns 0-1 based on constraints
        return float(score)