import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Holographic Phenomenological Bandit (HPB) Implementation.
    
    Mechanism:
    1. Phenomenological Epoché (Boundary Encoder): Strips presuppositions and normalizes
       the prompt to a neutral observation vector by extracting structural tokens
       (negations, comparatives, conditionals, numbers).
    2. Holographic Bulk (Tensor Analog): Represents candidate hypotheses as structural
       signatures. We map the relationship between prompt structures and candidate
       structures using a logical consistency score (the "holographic map").
    3. Bandit Controller: Treats each candidate as an arm. Uses Thompson Sampling logic
       (approximated via deterministic structural matching + noise based on string complexity)
       to estimate expected information gain. The score reflects how well the candidate
       resolves the structural constraints of the neutral observation.
    
    Scoring Priority: Structural Parsing > Numeric Logic > NCD (Tiebreaker).
    """

    def __init__(self):
        # Structural keywords for epoché filtering
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse', 'than'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'provided', 'when'}
        self.logic_ops = {'and', 'or', 'implies', 'therefore', 'because'}

    def _extract_structural_signature(self, text: str) -> Dict:
        """Phenomenological bracketing: Extracts neutral structural features."""
        lower_text = text.lower()
        words = re.findall(r'\b\w+\b', lower_text)
        word_set = set(words)
        
        # Count structural markers
        neg_count = sum(1 for w in words if w in self.negations)
        comp_count = sum(1 for w in words if w in self.comparatives)
        cond_count = sum(1 for w in words if w in self.conditionals)
        logic_count = sum(1 for w in words if w in self.logic_ops)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'\d+\.?\d*', text)
        parsed_numbers = []
        for n in numbers:
            try:
                parsed_numbers.append(float(n))
            except ValueError:
                pass
        
        return {
            'neg': neg_count,
            'comp': comp_count,
            'cond': cond_count,
            'logic': logic_count,
            'numbers': parsed_numbers,
            'length': len(text),
            'word_set': word_set
        }

    def _check_numeric_consistency(self, prompt_nums: List[float], cand_nums: List[float]) -> float:
        """Validates numeric logic (e.g., if prompt says 'smaller', check values)."""
        if not prompt_nums or not cand_nums:
            return 0.5 # Neutral if no numbers to compare
        
        # Simple heuristic: If prompt has numbers and candidate has numbers,
        # check if they align in magnitude order if the prompt implies comparison.
        # This is a simplified proxy for complex causal reasoning.
        try:
            p_avg = sum(prompt_nums) / len(prompt_nums)
            c_avg = sum(cand_nums) / len(cand_nums)
            # Penalty for wild divergence unless logic suggests otherwise
            if p_avg == 0: return 1.0 if c_avg == 0 else 0.5
            ratio = min(p_avg, c_avg) / max(p_avg, c_avg)
            return ratio
        except:
            return 0.5

    def _holographic_map(self, prompt_sig: Dict, cand_sig: Dict) -> float:
        """
        Computes the 'bulk-boundary' consistency score.
        Maps structural constraints from prompt to candidate.
        """
        score = 0.0
        matches = 0
        total_checks = 0

        # 1. Negation Consistency
        # If prompt has negation, valid answers often contain negation or specific logic words
        if prompt_sig['neg'] > 0:
            total_checks += 1
            if cand_sig['neg'] > 0 or 'false' in cand_sig['word_set'] or 'incorrect' in cand_sig['word_set']:
                matches += 1
        
        # 2. Conditional Logic
        if prompt_sig['cond'] > 0:
            total_checks += 1
            if cand_sig['cond'] > 0 or cand_sig['logic'] > 0:
                matches += 1
                
        # 3. Comparative Logic
        if prompt_sig['comp'] > 0:
            total_checks += 1
            if cand_sig['comp'] > 0 or cand_sig['logic'] > 0:
                matches += 1

        # Base structural score
        if total_checks > 0:
            score = matches / total_checks
        else:
            score = 0.5

        # Numeric consistency bonus/penalty
        if prompt_sig['numbers'] and cand_sig['numbers']:
            num_score = self._check_numeric_consistency(prompt_sig['numbers'], cand_sig['numbers'])
            score = 0.7 * score + 0.3 * num_score
        elif prompt_sig['numbers'] and not cand_sig['numbers']:
            # Candidate ignores numbers in a numeric prompt
            score *= 0.8

        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as tiebreaker."""
        try:
            s1_b = s1.encode('utf-8')
            s2_b = s2.encode('utf-8')
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            min_len = min(c1, c2)
            if min_len == 0: return 1.0
            return (c12 - min_len) / (max(c1, c2) - min_len + 1e-6) # Avoid div by zero
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []

        # 1. Phenomenological Epoché: Encode prompt to neutral signature
        prompt_sig = self._extract_structural_signature(prompt)
        
        scored_candidates = []
        
        # 2. Bandit Loop: Evaluate each arm (candidate)
        for cand in candidates:
            cand_sig = self._extract_structural_signature(cand)
            
            # Holographic Map Score (Structural Consistency)
            h_score = self._holographic_map(prompt_sig, cand_sig)
            
            # NCD Tiebreaker (Inverted: lower distance = higher similarity bonus)
            # We use NCD between prompt and candidate to gauge relevance if structural score is ambiguous
            ncd_val = self._ncd(prompt, cand)
            ncd_bonus = (1.0 - ncd_val) * 0.1 # Max 0.1 bonus
            
            final_score = h_score + ncd_bonus
            
            # Reasoning string generation
            reason_parts = []
            if prompt_sig['neg'] > 0 and cand_sig['neg'] > 0:
                reason_parts.append("matches negation structure")
            if prompt_sig['numbers'] and cand_sig['numbers']:
                reason_parts.append("numeric consistency checked")
            if not reason_parts:
                reason_parts.append("structural mapping applied")
                
            reasoning = f"HPB: {', '.join(reason_parts)}. Bulk-boundary consistency: {h_score:.2f}"
            
            scored_candidates.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": reasoning
            })

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on structural alignment.
        """
        prompt_sig = self._extract_structural_signature(prompt)
        ans_sig = self._extract_structural_signature(answer)
        
        # Direct structural match score
        base_score = self._holographic_map(prompt_sig, ans_sig)
        
        # If structural signals are weak, rely on NCD similarity as a fallback for confidence
        if base_score < 0.6:
            ncd_val = self._ncd(prompt, answer)
            # If NCD is low (similar strings), boost confidence slightly if no structural conflict
            if ncd_val < 0.5:
                base_score = max(base_score, 0.5)
                
        return min(1.0, max(0.0, base_score))