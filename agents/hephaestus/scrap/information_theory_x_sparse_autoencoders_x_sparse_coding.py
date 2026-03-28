import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Information-Theoretic Sparse Predictive Coding Tool.
    
    Mechanism:
    Instead of training a neural network (which violates the 'no external deps' constraint),
    we simulate the objective function L = Reconstruction + Sparsity - InfoGain using 
    structural symbolic analysis.
    
    1. Reconstruction (Data Fidelity): Measures how well the candidate's structural 
       signature (negations, numbers, logic operators) matches the prompt's requirements.
       High match = Low reconstruction error.
       
    2. Sparsity (Complexity Penalty): Penalizes candidates that are overly verbose 
       or contain unnecessary tokens relative to the prompt context (Occam's razor).
       
    3. Information Gain (Predictive Power): Estimates I(z;x) by checking if the candidate
       resolves specific constraints (conditionals, comparatives) found in the prompt.
       Candidates that satisfy more logical constraints gain higher scores.
       
    The final score balances these three terms, using NCD only as a tiebreaker for 
    semantically similar structural matches.
    """

    def __init__(self):
        # Structural parsers
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere'}
        self.comparatives = {'>', '<', '>=', '<=', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'when'}
        self.logic_ops = {'and', 'or', 'xor', 'but', 'however'}

    def _extract_features(self, text: str) -> Dict:
        """Extract structural features: negations, numbers, comparatives, conditionals."""
        lower_text = text.lower()
        words = set(re.findall(r'\b\w+\b', lower_text))
        
        # Numbers
        numbers = re.findall(r'-?\d+\.?\d*', text)
        nums = [float(n) for n in numbers] if numbers else []
        
        return {
            'negations': len(words & self.negation_words),
            'has_comparative': bool(words & self.comparatives),
            'has_conditional': bool(words & self.conditionals),
            'has_logic': bool(words & self.logic_ops),
            'numbers': nums,
            'length': len(text),
            'word_count': len(words)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Compute Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        max_len = max(c1, c2)
        if max_len == 0:
            return 0.0
        return (c12 - min(c1, c2)) / max_len

    def _evaluate_hypothesis(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """
        Evaluate a single candidate against the prompt using the sparse coding analogy.
        Returns (score, reasoning_string).
        """
        p_feat = self._extract_features(prompt)
        c_feat = self._extract_features(candidate)
        
        score = 0.0
        reasons = []

        # 1. Reconstruction Term (Constraint Matching)
        # Does the candidate reflect the structural complexity of the prompt?
        recon_error = 0.0
        
        # Negation consistency
        if p_feat['negations'] > 0:
            if c_feat['negations'] == 0:
                recon_error += 0.3
                reasons.append("Missing negation detected in prompt")
            else:
                score += 0.2
                reasons.append("Negation preserved")
        
        # Conditional logic presence
        if p_feat['has_conditional']:
            if not c_feat['has_conditional']:
                # Not strictly required to repeat 'if', but must handle logic
                pass 
            else:
                score += 0.1
        
        # Number handling (Critical for reasoning traps)
        if p_feat['numbers'] and c_feat['numbers']:
            # Check if candidate numbers are consistent with prompt numbers (simplified)
            # If prompt has comparison, candidate should reflect result
            score += 0.2
            reasons.append("Numeric content present")
        elif p_feat['numbers'] and not c_feat['numbers']:
            # If prompt has numbers but candidate doesn't, might be abstract (ok) or ignoring data (bad)
            # We penalize slightly if the prompt is heavily numeric
            if len(p_feat['numbers']) > 2:
                recon_error += 0.2
                reasons.append("Numeric data ignored")

        # 2. Sparsity Term (Lambda1 * ||z||_1)
        # Penalize excessive length without information gain
        length_ratio = c_feat['length'] / (p_feat['length'] + 1)
        sparsity_penalty = 0.0
        if length_ratio > 2.0:
            sparsity_penalty = 0.1 * (length_ratio - 1.0)
            reasons.append("Verbose")
        
        # 3. Information Gain Term (-Lambda2 * I(z;x))
        # Reward candidates that resolve specific logical structures
        info_gain = 0.0
        
        # Check for comparative resolution
        if p_feat['has_comparative'] and c_feat['has_comparative']:
            info_gain += 0.3
            reasons.append("Comparative logic resolved")
        elif p_feat['has_comparative'] and not c_feat['has_comparative']:
            # Did it answer the comparison? Check for specific answer words
            ans_words = {'yes', 'no', 'true', 'false', 'correct', 'incorrect'}
            if not (set(candidate.lower().split()) & ans_words):
                info_gain -= 0.2 # Penalty for missing resolution
                reasons.append("Comparative unresolved")

        # Logic consistency
        if p_feat['has_logic']:
            if c_feat['has_logic'] or c_feat['has_conditional']:
                info_gain += 0.2
                reasons.append("Logical structure maintained")

        # Final Score Calculation
        # Score = (Reconstruction Bonus) - (Sparsity Penalty) + (Info Gain) - (Reconstruction Error)
        final_score = (0.5 - recon_error) - sparsity_penalty + info_gain
        
        # Normalize roughly to 0-1 range based on empirical bounds of these heuristics
        final_score = max(0.0, min(1.0, final_score + 0.5)) 
        
        reason_str = "; ".join(reasons) if reasons else "Structural match"
        return final_score, reason_str

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        
        # First pass: Structural Scoring
        for cand in candidates:
            score, reason = self._evaluate_hypothesis(prompt, cand)
            scored_candidates.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason,
                "ncd": 0.0 # Placeholder
            })
        
        # Second pass: NCD Tie-breaking for close calls
        # Sort by score first to identify clusters
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Apply NCD adjustment for candidates with very similar structural scores
        # This implements the "NCD as tiebreaker" requirement
        for i in range(len(scored_candidates)):
            current = scored_candidates[i]
            # Compare with top candidate to see if they are structurally equivalent but string-different
            if i > 0:
                diff = abs(current["score"] - scored_candidates[0]["score"])
                if diff < 0.05: # Close enough to need tiebreaker
                    ncd_val = self._compute_ncd(prompt, current["candidate"])
                    # Lower NCD to prompt is generally better for relevance, 
                    # but we want diversity. Let's use NCD to prompt as a relevance booster.
                    # Actually, for reasoning, if scores are tied, the one closer to prompt structure (lower NCD) 
                    # is often the safer bet unless it's a trick.
                    current["ncd"] = ncd_val
                    # Small boost for lower NCD (higher similarity) if scores are tied
                    current["score"] -= (ncd_val * 0.01) 

        # Final sort
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Format output
        return [
            {
                "candidate": c["candidate"],
                "score": round(c["score"], 4),
                "reasoning": c["reasoning"]
            }
            for c in scored_candidates
        ]

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same structural evaluation logic.
        """
        results = self.evaluate(prompt, [answer])
        if not results:
            return 0.0
        # Normalize the score from evaluate (which is already roughly 0-1) to strict 0-1
        score = results[0]["score"]
        return max(0.0, min(1.0, score))