import zlib
import re
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A self-calibrating reasoning tool implementing Neural Plasticity x Metacognition x ECC.
    
    Mechanism:
    1. Structural Parsing (Fault-Tolerant Inference): Extracts logical constraints 
       (negations, comparatives, conditionals) to form a 'syndrome' of the prompt.
    2. ECC-LDPC Analogy (Error Correction): Candidates are checked against these 
       structural parity bits. Violations (e.g., missing negation) flip the 'syndrome',
       reducing the score significantly. This corrects for surface-level similarity errors.
    3. Metacognitive Confidence: Computes a confidence score based on the ratio of 
       satisfied constraints vs. total constraints. High syndrome magnitude (many violations)
       lowers confidence.
    4. Neural Plasticity (Confidence-Gated Learning): The final score is modulated by 
       confidence. High confidence reinforces the NCD similarity; low confidence triggers
       'pruning' (penalty) to prevent committing to uncertain hypotheses.
    """

    def __init__(self):
        # Logical patterns to extract structural "parity checks"
        self.negation_words = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing', 'nowhere']
        self.comparative_ops = ['>', '<', 'greater', 'less', 'more', 'fewer', 'larger', 'smaller']
        self.conditional_words = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.numeric_pattern = re.compile(r'-?\d+\.?\d*')

    def _extract_structure(self, text: str) -> Dict:
        """Extracts logical constraints acting as parity check bits."""
        lower_text = text.lower()
        words = lower_text.split()
        
        has_negation = any(w in words for w in self.negation_words)
        has_comparative = any(op in lower_text for op in self.comparative_ops)
        has_conditional = any(w in words for w in self.conditional_words)
        numbers = [float(n) for n in self.numeric_pattern.findall(text)]
        
        # Simple numeric logic extraction
        numeric_constraint = None
        if len(numbers) >= 2:
            # Assume standard comparison intent if keywords exist
            if has_comparative or ('>' in text) or ('<' in text):
                numeric_constraint = (numbers[0], numbers[1]) 

        return {
            'negation': has_negation,
            'comparative': has_comparative,
            'conditional': has_conditional,
            'numbers': numbers,
            'numeric_constraint': numeric_constraint
        }

    def _check_parity(self, prompt_struct: Dict, candidate: str) -> Tuple[float, List[str]]:
        """
        Checks candidate against prompt structure (ECC Layer).
        Returns a penalty score (0.0 = perfect match, 1.0 = total failure) and list of errors.
        """
        errors = []
        penalty = 0.0
        candidate_lower = candidate.lower()
        candidate_words = candidate_lower.split()
        
        # Check Negation Parity
        if prompt_struct['negation']:
            # If prompt has negation, candidate should ideally reflect it or not contradict it.
            # Heuristic: If prompt says "not X", and candidate is just "X", penalize.
            # This is a simplified syndrome check.
            has_cand_neg = any(w in candidate_words for w in self.negation_words)
            if not has_cand_neg:
                # Soft penalty for missing negation in candidate when prompt has it
                # unless the candidate is explicitly denying something else.
                penalty += 0.3
                errors.append("Missing negation context")

        # Check Numeric Consistency
        if prompt_struct['numeric_constraint']:
            n1, n2 = prompt_struct['numeric_constraint']
            cand_nums = [float(x) for x in self.numeric_pattern.findall(candidate)]
            
            if len(cand_nums) >= 1:
                # If prompt implies order (e.g., 9.11 < 9.9), check if candidate respects magnitude
                # This is a heuristic proxy for logical consistency
                if prompt_struct['comparative']:
                    if 'less' in candidate_lower or 'smaller' in candidate_lower or '<' in candidate_lower:
                        if cand_nums[0] > cand_nums[-1]: # Inconsistent internal logic
                            penalty += 0.4
                            errors.append("Numeric logic inversion")
        
        # Check for direct contradiction markers (Simple heuristic)
        if 'contradicts' in candidate_lower or 'false' in candidate_lower:
             if 'true' not in candidate_lower: # Unless it says "false statement is true"
                 pass # Context dependent, skip hard penalty

        return min(penalty, 1.0), errors

    def _ncd(self, s1: str, s2: str) -> float:
        """Calculates Normalized Compression Distance."""
        b1, b2, b12 = zlib.compress(s1.encode()), zlib.compress(s2.encode()), zlib.compress((s1+s2).encode())
        max_len = max(len(b1), len(b2))
        if max_len == 0: return 0.0
        return (len(b12) - min(len(b1), len(b2))) / max_len

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Pre-calculate NCD for all candidates to find baseline similarity
        ncd_scores = []
        for cand in candidates:
            ncd_scores.append(self._ncd(prompt, cand))
        
        # Normalize NCD to similarity (1 - ncd), handled carefully for edge cases
        max_ncd = max(ncd_scores) if ncd_scores else 1.0
        min_ncd = min(ncd_scores) if ncd_scores else 0.0
        
        for i, cand in enumerate(candidates):
            # 1. ECC Parity Check (Structural Validation)
            parity_penalty, errors = self._check_parity(prompt_struct, cand)
            
            # 2. Base Similarity (NCD)
            # Lower NCD is better. Convert to similarity score 0-1.
            raw_ncd = ncd_scores[i]
            # Normalize roughly to 0-1 range where 1 is best match
            # If max_ncd is 0 (identical strings), score is 1.
            if max_ncd == 0:
                base_score = 1.0
            else:
                # Invert: 0 distance = 1 score. 
                base_score = 1.0 - (raw_ncd / (max_ncd + 0.01))
            
            # 3. Metacognitive Confidence
            # Confidence is high if parity errors are low. 
            # Confidence = 1.0 - parity_penalty
            confidence = max(0.0, 1.0 - parity_penalty)
            
            # 4. Plasticity Modulation (Confidence-Gated Scoring)
            # If confidence is low (high uncertainty/parity violation), prune the score.
            # Score = base_score * confidence_modifier
            # Strong penalty if structural constraints are violated.
            final_score = base_score * (confidence ** 2) # Squared to amplify confidence gating
            
            # Construct reasoning string
            reason_parts = []
            if parity_penalty > 0:
                reason_parts.append(f"ECC Check Failed: {', '.join(errors)}.")
            else:
                reason_parts.append("ECC Check Passed: Structural constraints satisfied.")
            
            reason_parts.append(f"Metacognitive Confidence: {confidence:.2f}.")
            reason_parts.append(f"Plasticity Gate: Score modulated by confidence.")
            
            results.append({
                "candidate": cand,
                "score": float(final_score),
                "reasoning": " ".join(reason_parts)
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on structural integrity."""
        prompt_struct = self._extract_structure(prompt)
        parity_penalty, _ = self._check_parity(prompt_struct, answer)
        
        # Base confidence from NCD similarity
        ncd_val = self._ncd(prompt, answer)
        # Heuristic: Very long distances imply low confidence regardless of structure
        ncd_conf = max(0.0, 1.0 - ncd_val)
        
        # Structural confidence
        struct_conf = 1.0 - parity_penalty
        
        # Combined metacognitive signal
        return float(min(1.0, (ncd_conf + struct_conf) / 2.0))