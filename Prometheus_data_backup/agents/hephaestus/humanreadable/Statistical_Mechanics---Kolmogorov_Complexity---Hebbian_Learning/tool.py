import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Implements a local-learning energy-based model inspired by Statistical Mechanics,
    Kolmogorov Complexity, and Hebbian Learning.
    
    Mechanism:
    1. Structural Parsing (The "Data" Term): Extracts logical constraints (negations, 
       comparatives, conditionals) and numeric values. This forms the likelihood term 
       <E>_data. Candidates are scored on how well they satisfy these explicit structural 
       constraints (Hebbian strengthening of valid co-occurrences).
       
    2. Complexity Regularization (The "Kolmogorov" Term): Calculates the description 
       length of the candidate using zlib compression. Overly verbose or noisy candidates 
       are penalized (Occam's razor), simulating the L(w) term.
       
    3. Free Energy Minimization: The final score is a balance of fitting the structural 
       constraints (high likelihood) and maintaining low complexity (low description length).
       Score = Structural_Fit - lambda * Complexity_Penalty.
       
    This approach prioritizes logical structure over string similarity, using NCD only 
    as a secondary tie-breaker when structural signals are weak.
    """

    def __init__(self):
        self.lambda_complexity = 0.05  # Weight for complexity penalty
        self.threshold_numeric = 0.1   # Tolerance for float comparisons

    def _extract_structure(self, text: str) -> dict:
        """Extracts logical and numeric features from text."""
        text_lower = text.lower()
        features = {
            'negations': len(re.findall(r'\b(not|no|never|neither|nor)\b', text_lower)),
            'comparatives': len(re.findall(r'\b(more|less|greater|smaller|higher|lower|before|after)\b', text_lower)),
            'conditionals': len(re.findall(r'\b(if|then|unless|otherwise)\b', text_lower)),
            'numbers': [],
            'length': len(text)
        }
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        features['numbers'] = [float(n) for n in nums]
        return features

    def _check_logical_consistency(self, prompt_feats: dict, cand_feats: dict, prompt: str, candidate: str) -> float:
        """
        Evaluates if the candidate satisfies structural constraints implied by the prompt.
        Returns a score between 0 and 1.
        """
        score = 0.0
        count = 0

        # 1. Numeric Consistency
        if prompt_feats['numbers'] and cand_feats['numbers']:
            count += 1
            # Simple heuristic: If prompt has numbers, candidate should likely relate logically.
            # Since we don't have the full context tree, we check if the candidate 
            # preserves the order if it repeats numbers, or simply exists.
            # Stronger signal: If prompt implies a comparison (e.g. "greater"), 
            # does the candidate number satisfy it? 
            # Without explicit operator parsing, we use a proxy: 
            # If prompt has 'less' and candidate number < prompt max number, boost.
            p_max = max(prompt_feats['numbers'])
            c_val = cand_feats['numbers'][0] # Take first number in candidate
            
            if 'less' in prompt.lower() or 'smaller' in prompt.lower():
                if c_val < p_max: score += 1.0
                else: score += 0.2
            elif 'more' in prompt.lower() or 'greater' in prompt.lower():
                if c_val > p_max: score += 1.0
                else: score += 0.2
            else:
                # Neutral numeric presence
                score += 0.5
        elif not prompt_feats['numbers'] and not cand_feats['numbers']:
            score += 0.5 # Neutral
            count += 1

        # 2. Logical Keyword Alignment (Hebbian Co-activation)
        # If prompt has negation, valid answers often acknowledge it or flip logic.
        # Here we simply reward structural richness matching the prompt type.
        if prompt_feats['negations'] > 0:
            count += 1
            # Heuristic: Valid answers to negated prompts often contain negations or specific modifiers
            if cand_feats['negations'] > 0 or len(cand_feats['numbers']) > 0:
                score += 1.0
            else:
                score += 0.3
        
        if prompt_feats['conditionals'] > 0:
            count += 1
            # Candidates answering conditionals often contain logical connectors
            if cand_feats['conditionals'] > 0 or cand_feats['comparatives'] > 0:
                score += 1.0
            else:
                score += 0.4

        # 3. Constraint Propagation (Transitivity proxy)
        # If prompt says A > B and B > C, and candidate is "A", it's good.
        # We approximate this by checking if candidate length is reasonable (not too short to be empty, not too long to be noise)
        if 0.5 * prompt_feats['length'] <= cand_feats['length'] <= 2.0 * prompt_feats['length']:
            score += 0.5
            count += 1

        return (score / max(count, 1)) if count > 0 else 0.5

    def _compute_complexity_penalty(self, candidate: str) -> float:
        """
        Approximates Kolmogorov complexity via compressed length.
        Normalized to [0, 1] range roughly based on typical string lengths.
        """
        if not candidate:
            return 1.0
        compressed = zlib.compress(candidate.encode('utf-8'))
        # Complexity proportional to compressed size
        return len(compressed) / 100.0  # Normalize loosely

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denom = max(c1, c2)
        if denom == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denom

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_feats = self._extract_structure(prompt)
        results = []

        for cand in candidates:
            cand_feats = self._extract_structure(cand)
            
            # 1. Structural/Logical Score (The "Energy" term)
            logic_score = self._check_logical_consistency(prompt_feats, cand_feats, prompt, cand)
            
            # 2. Complexity Penalty (The "Kolmogorov" term)
            complexity = self._compute_complexity_penalty(cand)
            
            # 3. Free Energy Calculation
            # Minimize F = Energy - Complexity. 
            # Here we maximize: Logic_Score - Lambda * Complexity
            final_score = logic_score - (self.lambda_complexity * complexity)
            
            # Tie-breaking with NCD if scores are very close or logic is ambiguous
            if final_score > 0.4: 
                ncd_bonus = 0.0
            else:
                # If logic fails, use NCD to see if it's just a rephrasing
                ncd_val = self._compute_ncd(prompt, cand)
                if ncd_val < 0.6: # High similarity
                    final_score += 0.1

            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": f"Logic:{logic_score:.2f}, Complexity:{complexity:.2f}"
            })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence based on the gap between the answer's score and a theoretical minimum.
        """
        # Evaluate single candidate against itself to get relative standing isn't possible without others.
        # Instead, we re-run evaluation with a dummy set to get normalized score.
        # Or simpler: Use the internal scoring mechanism directly.
        
        prompt_feats = self._extract_structure(prompt)
        cand_feats = self._extract_structure(answer)
        
        logic_score = self._check_logical_consistency(prompt_feats, cand_feats, prompt, answer)
        complexity = self._compute_complexity_penalty(answer)
        raw_score = logic_score - (self.lambda_complexity * complexity)
        
        # Map raw score (approx -0.5 to 1.5) to [0, 1]
        confidence = max(0.0, min(1.0, (raw_score + 0.5) / 2.0))
        return float(confidence)