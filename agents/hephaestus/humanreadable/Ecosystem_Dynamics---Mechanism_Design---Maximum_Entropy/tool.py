import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Maximum-Entropy Incentive-Compatible Trophic Allocation Mechanism (ME-ITAM)
    
    Implementation Strategy:
    1. Structural Parsing (Primary Signal): Extracts negations, comparatives, and conditionals.
       This addresses the 'Ecosystem Dynamics' and 'MaxEnt' inhibitor warning by focusing on
       logical structure rather than semantic content.
    2. Mechanism Design (Scoring Modifier): Implements a VCG-like penalty. Candidates that
       merely echo the prompt (high overlap) without structural alignment are penalized,
       simulating the cost of untruthful reporting in an auction.
    3. MaxEnt/Confidence Wrapper: Uses structural consistency to estimate confidence,
       avoiding direct probabilistic modeling which is flagged as an inhibitor.
    4. NCD (Tiebreaker): Used only when structural signals are indistinguishable.
    """

    def __init__(self):
        # Keywords for structural parsing
        self.negations = ['not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', 'than']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided', 'when']
        self.numerics = re.compile(r'\d+\.?\d*')

    def _extract_structure(self, text: str) -> Dict:
        """Extracts logical structures: negations, comparatives, conditionals, numbers."""
        lower_text = text.lower()
        words = re.findall(r'\w+', lower_text)
        
        return {
            'neg_count': sum(1 for w in words if w in self.negations),
            'comp_count': sum(1 for w in words if w in self.comparatives),
            'cond_count': sum(1 for w in words if w in self.conditionals),
            'numbers': [float(n) for n in self.numerics.findall(text)],
            'length': len(words),
            'has_question': '?' in text
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Computes Normalized Compression Distance as a tiebreaker."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        c1 = len(zlib.compress(s1_bytes))
        c2 = len(zlib.compress(s2_bytes))
        c12 = len(zlib.compress(s1_bytes + s2_bytes))
        
        denominator = max(c1, c2)
        if denominator == 0:
            return 0.0
        return (c12 - min(c1, c2)) / denominator

    def _structural_score(self, prompt: str, candidate: str) -> float:
        """
        Computes a score based on structural alignment and logical consistency.
        Higher score = better structural match to the reasoning requirements.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        score = 0.0
        
        # 1. Negation Consistency (Critical for reasoning traps)
        # If prompt has negation, correct answer often needs to acknowledge it or flip logic
        if p_struct['neg_count'] > 0:
            # Reward candidates that also handle negation logic (either by having it or being short/direct)
            if c_struct['neg_count'] > 0 or c_struct['length'] < 5:
                score += 2.0
            else:
                score -= 1.0 # Penalty for ignoring negation context
        
        # 2. Comparative/Quantitative Alignment
        if p_struct['comp_count'] > 0 or p_struct['numbers']:
            if c_struct['comp_count'] > 0 or c_struct['numbers']:
                score += 2.5 # Strong reward for matching quantitative logic
            else:
                score -= 0.5
        
        # 3. Conditional Logic
        if p_struct['cond_count'] > 0:
            if c_struct['cond_count'] > 0:
                score += 2.0
            elif c_struct['length'] > 10: # Long answers without conditionals when prompt has them are suspect
                score -= 1.0

        # 4. Numeric Evaluation (Direct check)
        if p_struct['numbers'] and c_struct['numbers']:
            # Simple heuristic: if prompt asks for comparison, does candidate reflect magnitude?
            # This is a proxy; exact math requires parsing the specific question type.
            # Here we reward presence of numbers in response to numbers in prompt.
            score += 1.5

        # 5. Mechanism Design: VCG-like Truthfulness Penalty
        # Penalize candidates that are too similar to the prompt (echoing) unless they add structure
        ncd_val = self._compute_ncd(prompt, candidate)
        if ncd_val < 0.3: # High similarity (low distance)
            # If it's just a restatement without adding logical operators, penalize heavily
            if c_struct['comp_count'] == 0 and c_struct['cond_count'] == 0 and p_struct['comp_count'] + p_struct['cond_count'] > 0:
                score -= 3.0
        
        return score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
        
        scored_candidates = []
        
        # Calculate structural scores first
        struct_scores = [(c, self._structural_score(prompt, c)) for c in candidates]
        max_struct = max(s[1] for _, s in struct_scores)
        min_struct = min(s[1] for _, s in struct_scores)
        range_struct = max_struct - min_struct if max_struct != min_struct else 1.0

        for candidate, s_score in struct_scores:
            # Normalize structural score to 0.5 - 0.9 range to leave room for NCD tiebreaking
            norm_struct = 0.5 + (0.4 * (s_score - min_struct) / range_struct)
            
            # NCD as tiebreaker (small weight)
            ncd = self._compute_ncd(prompt, candidate)
            # Invert NCD so lower distance (higher similarity) is higher score, 
            # but only as a tiebreaker within the structural bucket
            ncd_bonus = (1.0 - ncd) * 0.05 
            
            final_score = norm_struct + ncd_bonus
            
            # Reasoning summary
            reasoning = f"Structural alignment score: {s_score:.2f}. "
            if s_score > 1.0:
                reasoning += "Matches logical constraints (negation/comparatives)."
            elif s_score < 0:
                reasoning += "Failed logical constraint checks or echoed prompt without value."
            else:
                reasoning += "Neutral structural match."

            scored_candidates.append({
                "candidate": candidate,
                "score": round(final_score, 4),
                "reasoning": reasoning
            })

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Estimates confidence based on structural consistency between prompt and answer.
        Returns 0.0 to 1.0.
        """
        p_struct = self._extract_structure(prompt)
        a_struct = self._extract_structure(answer)
        
        confidence = 0.5 # Base confidence
        
        # Boost if both have complex logic or both are simple
        p_complex = p_struct['neg_count'] + p_struct['comp_count'] + p_struct['cond_count']
        a_complex = a_struct['neg_count'] + a_struct['comp_count'] + a_struct['cond_count']
        
        if p_complex > 0 and a_complex > 0:
            confidence += 0.3
        elif p_complex == 0 and a_complex == 0:
            confidence += 0.2
            
        # Penalty for length mismatch in complex queries
        if p_complex > 0 and a_struct['length'] < 3:
            confidence -= 0.4
            
        # NCD check for obvious gibberish or total mismatch
        ncd = self._compute_ncd(prompt, answer)
        if ncd > 0.95: # Very different strings
            confidence -= 0.2
            
        return max(0.0, min(1.0, confidence))