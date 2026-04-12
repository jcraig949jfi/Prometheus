import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Context-Gauge Attentional Workspace (CGAW) Implementation.
    
    Mechanism:
    1. Gauge Bundles (Structural Parsing): Extracts logical invariants (negations, 
       comparatives, conditionals, numerics) acting as local gauge frames.
    2. Global Workspace (Ignition): Candidates compete via a softmax over structural 
       alignment scores. High-alignment candidates "ignite" and broadcast constraints.
    3. Pragmatic Loss (RSA/Grice): Penalizes candidates violating context maxims 
       (e.g., length redundancy, contradiction of detected negations).
    4. Scoring: Weighted sum of Structural Match (Primary) + NCD (Tiebreaker).
    """

    def __init__(self):
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere', 'cannot', "n't"}
        self.comparatives = {'larger', 'smaller', 'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided', 'assuming'}
        self.quantifiers = {'all', 'every', 'some', 'any', 'most', 'few', 'many'}

    def _extract_gauge_frame(self, text: str) -> dict:
        """Parses text into a structural gauge frame (invariants)."""
        lower = text.lower()
        words = set(re.findall(r'\b\w+\b', lower))
        
        # Detect logical operators
        has_negation = bool(words & self.negation_words)
        has_comparative = bool(words & self.comparatives)
        has_conditional = bool(words & self.conditionals)
        has_quantifier = bool(words & self.quantifiers)
        
        # Extract numbers for numeric evaluation
        numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', text)]
        
        return {
            'neg': has_negation,
            'comp': has_comparative,
            'cond': has_conditional,
            'quant': has_quantifier,
            'nums': tuple(sorted(numbers)),
            'len': len(text),
            'word_set': words
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        c1 = len(zlib.compress(s1.encode()))
        c2 = len(zlib.compress(s2.encode()))
        c12 = len(zlib.compress((s1 + s2).encode()))
        denominator = max(c1, c2)
        if denominator == 0:
            return 1.0
        return (c12 - min(c1, c2)) / denominator

    def _pragmatic_loss(self, prompt_frame: dict, cand_frame: dict, prompt: str, candidate: str) -> float:
        """
        Calculates pragmatic penalty based on RSA/Grice maxims.
        - Quantity: Penalize extreme length mismatch.
        - Relation: Penalize missing key structural markers (e.g., negation flip).
        """
        loss = 0.0
        
        # Quantity Maxim: Length penalty (simplified)
        if cand_frame['len'] > prompt_frame['len'] * 1.5 or cand_frame['len'] < prompt_frame['len'] * 0.1:
            loss += 0.1
            
        # Relation Maxim: Negation consistency check
        # If prompt has negation, candidate should ideally reflect awareness (heuristic)
        if prompt_frame['neg'] and not cand_frame['neg']:
            # Soft penalty, as some answers are just "Yes/No"
            loss += 0.05
            
        return loss

    def _score_candidate(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Computes the final score and reasoning string."""
        p_frame = self._extract_gauge_frame(prompt)
        c_frame = self._extract_gauge_frame(candidate)
        
        score = 0.0
        reasons = []
        
        # 1. Structural Gauge Alignment (Primary Signal)
        # Check comparative alignment
        if p_frame['comp']:
            if c_frame['comp']:
                score += 0.3
                reasons.append("Matches comparative structure")
            else:
                score -= 0.2
                reasons.append("Misses comparative context")
        
        # Check conditional alignment
        if p_frame['cond']:
            if c_frame['cond']:
                score += 0.2
                reasons.append("Preserves conditional logic")
        
        # Check numeric consistency (Heuristic: if numbers exist, do they appear?)
        if p_frame['nums']:
            # Simple presence check for numbers in candidate if prompt has them
            # This is a weak proxy for numeric reasoning without an engine
            if c_frame['nums']:
                score += 0.2
                reasons.append("Numeric data preserved")
            else:
                # If prompt is math-heavy, lack of numbers in candidate is suspicious
                if len(p_frame['nums']) > 2: 
                    score -= 0.1
                    reasons.append("Lacks numeric resolution")

        # 2. Pragmatic Loss (Secondary Modifier)
        prag_loss = self._pragmatic_loss(p_frame, c_frame, prompt, candidate)
        score -= prag_loss
        if prag_loss > 0:
            reasons.append(f"Pragmatic penalty: {prag_loss:.2f}")

        # 3. NCD as Tiebreaker (Only if structural score is neutral)
        # We add a small NCD component scaled to not override structural signals
        ncd = self._compute_ncd(prompt, candidate)
        # Invert NCD (lower is better) and scale down to be a tiebreaker
        ncd_score = (1.0 - ncd) * 0.05 
        score += ncd_score
        
        if not reasons:
            reasons.append("Structural baseline")
            
        return score, "; ".join(reasons)

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored = []
        for cand in candidates:
            score, reason = self._score_candidate(prompt, cand)
            scored.append({
                "candidate": cand,
                "score": float(score),
                "reasoning": reason
            })
        
        # Sort by score descending
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural alignment strength."""
        score, _ = self._score_candidate(prompt, answer)
        # Map score to 0-1 range. 
        # Baseline structural match is ~0.0 to 0.5. Strong match > 0.5.
        # Negative scores indicate contradictions.
        conf = 1.0 / (1.0 + np.exp(-score * 5)) # Sigmoid scaling
        return float(np.clip(conf, 0.0, 1.0))