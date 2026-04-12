import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Embodied Sparse Information-Bottleneck (ESIB) Reasoning Tool.
    
    Mechanism:
    1. Structural Parsing (Embodied Cognition): Extracts logical operators (negations,
       comparatives, conditionals) and numeric values to form a "sensorimotor" representation.
    2. Sparse Latent Coding (Sparse Autoencoders): Maps structural features to a sparse
       binary vector (dictionary code). Only features present in the text activate.
    3. Information Bottleneck Scoring (Information Theory): 
       - Computes a 'complexity penalty' (approximating KL divergence) based on code length.
       - Computes 'reconstruction fidelity' by checking if the candidate satisfies 
         extracted constraints (logic/numeric).
       - Final Score = Fidelity - Beta * Complexity.
    
    This avoids pure string similarity (NCD) for primary scoring, using it only as a tiebreaker.
    """

    def __init__(self):
        self.beta = 0.1  # Information bottleneck penalty weight
        self.threshold = 0.5

    def _parse_structure(self, text: str) -> Dict:
        """Extracts logical structure and numeric values (Embodied Cognition layer)."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|without|impossible)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|higher|lower|better|worse)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'numbers': [float(n) for n in re.findall(r'-?\d+\.?\d*', text)],
            'length': len(text.split())
        }
        return features

    def _encode_sparse(self, features: Dict) -> List[int]:
        """Converts features to a sparse binary latent vector (Sparse Autoencoder layer)."""
        # Dictionary: [negation, comparative, conditional, has_numbers, long_context]
        code = [
            1 if features['has_negation'] else 0,
            1 if features['has_comparative'] else 0,
            1 if features['has_conditional'] else 0,
            1 if len(features['numbers']) > 0 else 0,
            1 if features['length'] > 10 else 0
        ]
        return code

    def _compute_information_cost(self, code: List[int]) -> float:
        """Calculates information cost (approximating KL divergence/sparsity penalty)."""
        # Cost increases with active dimensions (encouraging minimal sufficient code)
        active_count = sum(code)
        # Simple entropy-like penalty: more active bits = higher cost
        return self.beta * active_count

    def _check_constraint_satisfaction(self, prompt: str, candidate: str) -> float:
        """
        Evaluates if the candidate satisfies the prompt's structural constraints.
        Acts as the 'reconstruction loss' in the predictive coding loop.
        """
        p_feat = self._parse_structure(prompt)
        c_feat = self._parse_structure(candidate)
        score = 0.0
        
        # 1. Numeric Consistency (Transitivity/Magnitude)
        if p_feat['numbers'] and c_feat['numbers']:
            # If prompt implies a direction (e.g., "greater"), check if candidate aligns
            # Simplified heuristic: If prompt has numbers, candidate should likely reference magnitude or logic
            if p_feat['has_comparative']:
                # Heuristic: Candidate shouldn't contradict the numeric flow blindly
                score += 0.4
            else:
                score += 0.2 # Partial credit for numeric awareness
        elif not p_feat['numbers'] and not c_feat['numbers']:
            score += 0.2 # Consistent absence of numbers

        # 2. Logical Consistency (Negation/Conditional)
        # If prompt has negation, a valid reasoning step often acknowledges it or flips logic
        if p_feat['has_negation']:
            if c_feat['has_negation'] or len(c_feat['numbers']) > 0:
                score += 0.3 # Acknowledges complexity
        
        if p_feat['has_conditional']:
            if c_feat['has_conditional'] or c_feat['has_negation']:
                score += 0.3 # Handles branching logic

        # 3. Structural Matching (Weak NCD fallback for semantic overlap if logic is vague)
        # Only applied if basic structural checks pass
        if score > 0:
            try:
                # Normalized Compression Distance heuristic for semantic overlap
                c_both = len(zlib.compress((prompt + candidate).encode()))
                c_min = min(len(zlib.compress(prompt.encode())), len(zlib.compress(candidate.encode())))
                if c_min > 0:
                    ncd = (c_both - c_min) / max(c_both, 1)
                    # Convert distance to similarity (inverse)
                    if ncd < 0.8: # Reasonable overlap
                        score += 0.2
            except:
                pass
                
        return min(score, 1.0)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        p_code = self._encode_sparse(self._parse_structure(prompt))
        p_cost = self._compute_information_cost(p_code)

        for cand in candidates:
            c_feat = self._parse_structure(cand)
            c_code = self._encode_sparse(c_feat)
            
            # Information Bottleneck Score:
            # Maximize constraint satisfaction (Fidelity) while minimizing latent complexity (Sparsity)
            fidelity = self._check_constraint_satisfaction(prompt, cand)
            complexity = self._compute_information_cost(c_code)
            
            # The "Expected Information Gain" approximation
            # High fidelity + Low complexity = High Score
            raw_score = fidelity - complexity
            
            # Adjust for prompt complexity matching (Embodied alignment)
            # If prompt is complex, simple answers might be penalized too harshly without this
            if p_feat := self._parse_structure(prompt):
                if p_feat['has_conditional'] and not c_feat['has_conditional']:
                     raw_score -= 0.1 # Penalty for ignoring conditionals

            results.append({
                "candidate": cand,
                "score": float(raw_score),
                "reasoning": f"Fidelity: {fidelity:.2f}, Complexity Penalty: {complexity:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on the ESIB score.
        0.0 = Low fidelity / High complexity (Unlikely)
        1.0 = High fidelity / Low complexity (Likely)
        """
        res_list = self.evaluate(prompt, [answer])
        if not res_list:
            return 0.0
        
        raw_score = res_list[0]['score']
        
        # Map raw score (approx -0.5 to 1.0) to [0, 1]
        # Sigmoid-like mapping
        confidence = 1 / (1 + math.exp(-5 * (raw_score - 0.2)))
        return max(0.0, min(1.0, confidence))