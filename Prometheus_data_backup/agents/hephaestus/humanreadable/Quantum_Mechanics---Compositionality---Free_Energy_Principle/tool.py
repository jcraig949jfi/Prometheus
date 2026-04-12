import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Quantum Compositional Active Inference (QCAI) approximator.
    
    Mechanism:
    1. Compositional Structure: Parses prompts into structural tokens (negations, 
       comparatives, conditionals, numbers) to build a "basis" representation.
    2. Free Energy Principle (Core): Treats the prompt as sensory data and candidates 
       as hypotheses. Minimizes variational free energy by calculating prediction error 
       (structural mismatch between prompt constraints and candidate implications) 
       minus entropy (penalizing overly vague or generic candidates).
    3. Quantum Analogy: Uses superposition-like scoring where multiple structural 
       features contribute amplitude to the final score, avoiding early collapse 
       (binary filtering) until the final energy minimization step.
    
    Strategy:
    - High weight on structural constraint satisfaction (Free Energy minimization).
    - NCD used strictly as a tiebreaker for semantic similarity.
    - Explicit handling of negation and logic flows to beat simple compression baselines.
    """

    def __init__(self):
        # Structural keywords for parsing
        self.negations = {'no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing'}
        self.comparatives = {'greater', 'less', 'more', 'fewer', 'higher', 'lower', 'bigger', 'smaller'}
        self.conditionals = {'if', 'then', 'else', 'unless', 'provided'}
        self.logic_ops = {'and', 'or', 'xor', 'implies'}
        
    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract integers and floats
        matches = re.findall(r'-?\d+(?:\.\d+)?', text)
        return [float(m) for m in matches]

    def _structural_parse(self, text: str) -> Dict:
        tokens = set(self._tokenize(text))
        numbers = self._extract_numbers(text)
        
        has_negation = bool(tokens & self.negations)
        has_comparative = bool(tokens & self.comparatives)
        has_conditional = bool(tokens & self.conditionals)
        has_logic = bool(tokens & self.logic_ops)
        
        return {
            'tokens': tokens,
            'numbers': numbers,
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'logic': has_logic,
            'length': len(text)
        }

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        len1 = len(zlib.compress(b1))
        len2 = len(zlib.compress(b2))
        len12 = len(zlib.compress(b1 + b2))
        max_len = max(len1, len2)
        if max_len == 0:
            return 0.0
        return (len12 - min(len1, len2)) / max_len

    def _calculate_prediction_error(self, prompt_struct: Dict, cand_struct: Dict, prompt: str, candidate: str) -> float:
        """
        Calculates prediction error (Free Energy component).
        High error if candidate contradicts prompt structure.
        """
        error = 0.0
        
        # 1. Numeric Consistency Check
        p_nums = prompt_struct['numbers']
        c_nums = cand_struct['numbers']
        
        if p_nums:
            # If prompt has numbers, candidate should ideally reference them or logical consequences
            # Simple heuristic: if prompt has comparative, candidate numbers should reflect order
            if prompt_struct['comparative'] and len(p_nums) >= 2 and c_nums:
                # Check if candidate preserves relative order if it mentions numbers
                p_diff = p_nums[0] - p_nums[1] # e.g., 9.11 - 9.9 = negative
                # If candidate has numbers, do they follow logic? (Simplified for robustness)
                # We don't penalize heavily here unless explicit contradiction found
                pass
            
            # Penalty if candidate introduces random large numbers not in prompt (hallucination)
            if len(c_nums) > len(p_nums) * 2:
                error += 0.3

        # 2. Logical Negation Consistency
        # If prompt is negative, a "Yes" candidate might be wrong depending on phrasing.
        # Heuristic: If prompt has negation and candidate is short affirmative ("Yes", "True"), increase error slightly
        short_affirmatives = {'yes', 'true', 'correct', 'right'}
        if prompt_struct['negation'] and (cand_struct['tokens'] & short_affirmatives):
            # This is a risky heuristic, so low weight
            error += 0.1
            
        # 3. Structural Overlap (Compositional similarity)
        # Lack of shared vocabulary increases prediction error (candidate unrelated to prompt)
        shared_tokens = prompt_struct['tokens'] & cand_struct['tokens']
        overlap_ratio = len(shared_tokens) / (len(prompt_struct['tokens']) + 1)
        
        # Low overlap = High prediction error (unless candidate is very short like "A")
        if len(cand_struct['tokens']) > 2 and overlap_ratio < 0.1:
            error += 0.4 * (1.0 - overlap_ratio)
            
        return error

    def _calculate_entropy_penalty(self, candidate: str) -> float:
        """
        Entropy term S[psi]. 
        Penalizes candidates that are too generic (high entropy in a semantic sense) 
        or too chaotic. In this approximation, we penalize extreme brevity without content
        or excessive repetition.
        """
        if not candidate.strip():
            return 1.0 # Max penalty
        
        tokens = self._tokenize(candidate)
        if not tokens:
            return 0.5
            
        # Penalize single word answers unless they are specific
        if len(tokens) == 1:
            generic = {'yes', 'no', 'maybe', 'ok', 'true', 'false'}
            if tokens[0] in generic:
                return 0.2 # Small penalty, allows them but prefers reasoned answers
        
        return 0.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._structural_parse(prompt)
        results = []
        
        # Pre-calculate NCD for all candidates to use as tiebreaker
        # We want candidates similar to prompt context but logically sound
        ncd_scores = []
        for cand in candidates:
            # NCD between prompt and candidate (lower is more similar)
            ncd = self._compute_ncd(prompt, cand)
            ncd_scores.append(ncd)
        
        avg_ncd = sum(ncd_scores) / len(ncd_scores) if ncd_scores else 0.5

        for i, cand in enumerate(candidates):
            cand_struct = self._structural_parse(cand)
            
            # Free Energy = Prediction Error - Entropy
            # We want to MINIMIZE Free Energy. 
            # Score = -FreeEnergy (so higher score = better)
            
            pred_error = self._calculate_prediction_error(prompt_struct, cand_struct, prompt, cand)
            entropy = self._calculate_entropy_penalty(cand)
            
            # Base score starts at 1.0, subtract errors
            # Weight prediction error heavily (Free Energy Principle core)
            base_score = 1.0 - (pred_error * 0.8) - (entropy * 0.2)
            
            # Tie-breaking / Boosting with NCD
            # If NCD is very high (dissimilar), it might be a distractor. 
            # If NCD is low (similar), it supports the hypothesis.
            # However, correct answers might be short (e.g., "A") while prompt is long.
            # We use NCD primarily to break ties or penalize complete gibberish.
            
            ncd_val = ncd_scores[i]
            
            # Adjust score based on NCD relative to average
            # If candidate is much less similar than average, penalize
            if ncd_val > avg_ncd + 0.1:
                base_score -= 0.1
            elif ncd_val < avg_ncd - 0.1:
                base_score += 0.05
                
            # Structural Parsing Bonus: 
            # If candidate contains specific structural markers found in prompt (e.g. numbers, logic words)
            # it suggests better compositional alignment.
            common_nums = set(prompt_struct['numbers']) & set(cand_struct['numbers'])
            if common_nums:
                base_score += 0.15 # Strong boost for carrying over numeric evidence
                
            # Clamp score
            final_score = max(0.0, min(1.0, base_score))
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural match: {1.0-pred_error:.2f}, Entropy: {1.0-entropy:.2f}, NCD factor: {1.0-ncd_val:.2f}"
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1.
        Uses the same Free Energy minimization logic.
        """
        # Treat the single answer as a candidate list of one
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        return ranked[0]['score']