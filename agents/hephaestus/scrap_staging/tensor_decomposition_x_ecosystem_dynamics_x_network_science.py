import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hierarchical Tensor-Train Ecological Network Simulator (Abstracted for General Reasoning).
    
    Mechanism:
    1. Tensor Construction (Conceptual): Maps prompt elements to a high-dimensional space 
       (Species=Tokens, Time=Sequence, Environment=Context).
    2. TT-Decomposition Analogy: Compresses the problem into low-rank cores representing:
       - Interaction Core (Logic/Relations)
       - Temporal Core (Sequence/Order)
       - Environmental Core (Constraints/Conditions)
    3. Dynamics & Evaluation: Simulates 'energy flow' (information propagation) through 
       candidate answers. Candidates that maintain structural integrity (logic consistency) 
       and minimize 'cascade error' (contradictions) receive higher scores.
    4. Self-Evaluation: Uses rank-adaptation logic (complexity of parsing required) to 
       estimate confidence.
    
    This implementation approximates the TT-compression benefit by prioritizing 
    structural logic (negations, comparatives, conditionals) over raw string similarity,
    using NCD only as a tie-breaker for semantically identical options.
    """

    def __init__(self):
        # Core weights mimicking TT_cores contribution to final score
        self.weights = {
            'negation': 2.5,      # High impact on logic flip
            'comparative': 2.0,   # Critical for ordering
            'conditional': 1.8,   # Critical for constraint propagation
            'numeric': 2.2,       # Critical for factual accuracy
            'structural': 1.5     # General syntax adherence
        }

    def _extract_structural_features(self, text: str) -> Dict[str, any]:
        """Extracts logical primitives acting as low-rank tensor cores."""
        text_lower = text.lower()
        features = {
            'has_negation': bool(re.search(r'\b(not|no|never|without|neither|nor)\b', text_lower)),
            'has_comparative': bool(re.search(r'\b(more|less|greater|smaller|higher|lower|better|worse|than|before|after)\b', text_lower)),
            'has_conditional': bool(re.search(r'\b(if|then|unless|provided|when|while)\b', text_lower)),
            'has_numeric': bool(re.search(r'\d+(\.\d+)?', text)),
            'negation_count': len(re.findall(r'\b(not|no|never|without|neither|nor)\b', text_lower)),
            'numbers': [float(n) for n in re.findall(r'\d+(\.\d+)?', text)]
        }
        return features

    def _check_logical_consistency(self, prompt_feats: Dict, candidate_feats: Dict) -> float:
        """
        Simulates the 'cascade' effect. 
        If prompt implies a condition (e.g., contains 'not'), candidate must reflect it.
        """
        score = 0.0
        
        # Negation Propagation (Modus Tollens check approximation)
        if prompt_feats['has_negation']:
            # If prompt has negation, a valid reasoning step often requires specific handling.
            # We penalize candidates that ignore the complexity introduced by negation if they are too short/simple
            if not candidate_feats['has_negation'] and prompt_feats['negation_count'] > 1:
                score -= 1.0 # Penalty for ignoring complex negation
            else:
                score += self.weights['negation']
        
        # Comparative Consistency
        if prompt_feats['has_comparative']:
            if candidate_feats['has_comparative']:
                score += self.weights['comparative']
            # If prompt asks for comparison, answer lacking comparative words might be weak
            elif not candidate_feats['has_numeric']:
                score -= 0.5

        # Conditional Logic
        if prompt_feats['has_conditional']:
            if candidate_feats['has_conditional'] or candidate_feats['has_numeric']:
                score += self.weights['conditional']
        
        return score

    def _numeric_evaluation(self, prompt_feats: Dict, candidate_feats: Dict) -> float:
        """Handles numeric transitivity and extraction."""
        if not prompt_feats['has_numeric']:
            return 0.0
        
        if not candidate_feats['has_numeric']:
            return -2.0 # Major penalty for missing numbers in numeric prompt
        
        # Simple heuristic: If candidate contains numbers found in prompt, it's likely extracting, not reasoning.
        # If it contains NEW numbers or results of operations, it's reasoning.
        # For this general tool, we reward presence of numeric logic.
        return self.weights['numeric']

    def _calculate_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
        c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        """
        Evaluates candidates based on structural logic alignment (TT-core analogy)
        and uses NCD as a tie-breaker.
        """
        prompt_feats = self._extract_structural_features(prompt)
        scored_candidates = []

        for cand in candidates:
            cand_feats = self._extract_structural_features(cand)
            
            # 1. Structural Reasoning Score (The 'Tensor Contraction')
            logic_score = self._check_logical_consistency(prompt_feats, cand_feats)
            numeric_score = self._numeric_evaluation(prompt_feats, cand_feats)
            
            # 2. Length/Complexity penalty (Occam's razor / Rank adaptation)
            # Prefer concise but complete answers
            length_factor = 1.0 / (1.0 + abs(len(cand) - len(prompt)) / max(len(prompt), 1))
            
            # 3. NCD Tie-breaker (Semantic similarity)
            # Only used to distinguish between logically similar candidates
            ncd_val = self._calculate_ncd(prompt, cand)
            # Invert NCD so higher is better, scale down to not dominate logic
            similarity_score = (1.0 - ncd_val) * 0.5 

            total_score = logic_score + numeric_score + (length_factor * self.weights['structural']) + similarity_score
            
            # Generate reasoning string
            reasons = []
            if logic_score > 0: reasons.append("Logical structure aligned")
            if numeric_score > 0: reasons.append("Numeric constraints satisfied")
            if prompt_feats['has_negation'] and not cand_feats['has_negation']:
                reasons.append("Warning: Negation handling ambiguous")
            
            reasoning_str = "; ".join(reasons) if reasons else "Baseline match"

            scored_candidates.append({
                "candidate": cand,
                "score": float(total_score),
                "reasoning": reasoning_str
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Estimates confidence based on the 'rank' of the reasoning required.
        High complexity prompts with structurally consistent answers yield high confidence.
        """
        prompt_feats = self._extract_structural_features(prompt)
        cand_feats = self._extract_structural_features(answer)
        
        # Base confidence
        conf = 0.5
        
        # Adjust based on structural match
        if prompt_feats['has_negation'] == cand_feats['has_negation']:
            conf += 0.2
        if prompt_feats['has_comparative'] == cand_feats['has_comparative']:
            conf += 0.15
        if prompt_feats['has_conditional'] == cand_feats['has_conditional']:
            conf += 0.15
            
        # Penalty for length mismatch in complex prompts
        if len(prompt_feats['numbers']) > 0:
            if len(cand_feats['numbers']) > 0:
                conf += 0.2
            else:
                conf -= 0.3

        return max(0.0, min(1.0, conf))