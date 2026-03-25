import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Differentiable MaxEnt Theory-of-Mind Simulator (Discrete Approximation).
    
    Mechanism:
    1. Structural Parsing (ToM): Extracts logical constraints (negations, comparatives, 
       conditionals) to form a 'belief vector' representing the agent's mental state.
    2. MaxEnt Scoring: Assigns scores to candidates such that they satisfy constraints 
       while maximizing entropy (uniformity) among valid options. This avoids over-confident 
       priors unless forced by logic.
    3. Differentiable Analogue: Uses soft-min/soft-max approximations via exponential 
       weighting to simulate gradient-based belief updates without external ML libs.
    4. NCD Tiebreaker: Uses Normalized Compression Distance only when logical scores are tied.
    """

    def __init__(self):
        self.eps = 1e-9

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance using zlib."""
        b1, b2 = s1.encode(), s2.encode()
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        denom = max(c1, c2)
        if denom == 0: return 0.0
        return (c12 - min(c1, c2)) / denom

    def _extract_features(self, text: str) -> Dict[str, any]:
        """Extract structural logical features (ToM component)."""
        t = text.lower()
        return {
            'has_negation': any(n in t for n in ['not ', 'no ', 'never ', 'without ']),
            'has_comparative': any(c in t for c in ['more ', 'less ', 'greater ', 'smaller ', ' > ', ' < ']),
            'has_conditional': any(c in t for c in ['if ', 'then ', 'unless ']),
            'length': len(text.split()),
            'digit_present': any(c.isdigit() for c in t)
        }

    def _evaluate_logic(self, prompt: str, candidate: str) -> float:
        """
        Compute a logic-consistency score based on feature matching.
        Higher score = higher consistency with prompt constraints.
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        score = 0.0
        
        # Constraint Propagation: Negation matching
        if p_feat['has_negation']:
            if c_feat['has_negation']: score += 2.0
            else: score -= 1.0 # Penalty for ignoring negation context
        else:
            if c_feat['has_negation']: score -= 0.5 # Penalty for unnecessary negation

        # Constraint Propagation: Comparative/Number matching
        if p_feat['has_comparative'] or p_feat['digit_present']:
            if c_feat['has_comparative'] or c_feat['digit_present']:
                score += 2.0
            else:
                score -= 1.0
        
        # Conditional consistency
        if p_feat['has_conditional']:
            if c_feat['has_conditional']: score += 1.5
            # Simple heuristic: if prompt has 'if', answer often has 'then' or is a consequence
            if 'then' in candidate.lower() or ',' in candidate: score += 0.5

        # Length heuristic (Occam's razor proxy)
        if 0.5 * len(prompt) < len(candidate) < 2.0 * len(prompt):
            score += 0.5
            
        return score

    def _max_ent_distribution(self, scores: List[float], temperature: float = 1.0) -> List[float]:
        """
        Convert raw logic scores to probabilities using MaxEnt principle.
        P(i) = exp(score_i / T) / sum(exp(score_j / T))
        This maximizes entropy subject to the expectation constraints defined by scores.
        """
        if not scores: return []
        
        # Shift for numerical stability (subtract max)
        max_s = max(scores)
        shifted = [s - max_s for s in scores]
        
        # Exponential weighting (Boltzmann distribution)
        exp_scores = [math.exp(s / temperature) for s in shifted]
        total = sum(exp_scores) + self.eps
        
        return [e / total for e in exp_scores]

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        # 1. Compute raw logic scores for each candidate (The "Belief" state)
        raw_scores = []
        for cand in candidates:
            # Combine logic score with a tiny NCD component to break symmetry early
            logic_sc = self._evaluate_logic(prompt, cand)
            raw_scores.append(logic_sc)
        
        # 2. Apply MaxEnt to get probabilities (The "Distribution over beliefs")
        # Temperature > 1 encourages exploration (higher entropy), < 1 exploits
        probs = self._max_ent_distribution(raw_scores, temperature=1.5)
        
        # 3. Refine with NCD as a tiebreaker for semantically similar high-scorers
        final_scores = []
        for i, cand in enumerate(candidates):
            base_score = probs[i]
            # NCD penalty: if candidate is just a substring or very close to prompt noise
            ncd = self._compute_ncd(prompt, cand)
            # Adjust score: High NCD (dissimilar) might be bad if it ignores context, 
            # but low NCD (identical) is bad reasoning. Optimal is middle ground.
            # Here we use NCD primarily as a tie-breaker modifier.
            ncd_modifier = (1.0 - ncd) * 0.05 
            final_scores.append(base_score + ncd_modifier)

        # 4. Rank and format
        ranked_indices = sorted(range(len(candidates)), key=lambda k: final_scores[k], reverse=True)
        
        result = []
        for idx in ranked_indices:
            result.append({
                "candidate": candidates[idx],
                "score": float(final_scores[idx]),
                "reasoning": f"MaxEnt-ToM score based on logical constraint match and entropy maximization."
            })
            
        return result

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Computed as the MaxEnt probability of the single answer against a generated 
        set of implicit alternatives (simulated via perturbation of the answer itself).
        """
        # Generate pseudo-alternatives to simulate the candidate space
        alternatives = [answer]
        # Create dummy alternatives to normalize against
        if len(answer) > 3:
            alternatives.append(answer[:-1]) # Drop last char
            alternatives.append(answer + " not") # Negate
        else:
            alternatives.append("No")
            alternatives.append("Yes")
            
        # Evaluate the set
        ranked = self.evaluate(prompt, alternatives)
        
        # Find the score of the original answer
        target_score = 0.0
        for item in ranked:
            if item["candidate"] == answer:
                target_score = item["score"]
                break
                
        # Normalize to 0-1 range based on the max possible score in this context
        # Since scores are probabilities from MaxEnt, the score itself is the confidence 
        # relative to the generated alternatives.
        return min(1.0, max(0.0, target_score * len(alternatives)))