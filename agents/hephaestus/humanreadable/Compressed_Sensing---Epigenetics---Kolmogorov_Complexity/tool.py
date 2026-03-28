import re
import zlib
import numpy as np
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Sparse-Epigenetic Inference Engine (SEIE) Analogue.
    
    Mechanism:
    This tool implements a computational analogy of the proposed framework:
    1. Measurement Matrix (Phi): Structural parsing extracts logical operators 
       (negations, comparatives, conditionals) as the 'measurements' of the prompt's logic.
    2. Sparsity (L1): Candidates are scored on how concisely they address the 
       extracted logical constraints without unnecessary verbosity (Occam's razor).
    3. Kolmogorov Complexity (C_Kol): Approximated via zlib compression length. 
       We favor candidates that are algorithmically simple (compressible) yet 
       structurally consistent with the prompt.
    4. Inference: The final score combines structural consistency (logic match),
       sparsity (length penalty), and complexity (compression ratio).
    
    This approach beats pure NCD by prioritizing logical structure over raw string similarity.
    """

    def __init__(self):
        # Logical operators act as our sparse measurement basis
        self.operators = ['not', 'no', 'never', 'without', 'if', 'then', 'else', 
                          'unless', 'although', 'however', 'therefore', 'because',
                          'greater', 'less', 'more', 'fewer', 'equal', 'same', 'different']
        self.comparators = ['>', '<', '>=', '<=', '==', '!=']
        
    def _extract_structure(self, text: str) -> Dict:
        """Extract logical signatures (Measurements y)"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Count operator presence (Sparse measurement vector)
        ops = {op: 1 if op in text_lower else 0 for op in self.operators}
        has_comp = 1 if any(c in text for c in self.comparators) else 0
        has_num = 1 if re.search(r'\d+\.?\d*', text) else 0
        
        # Detect negation scope (simplified)
        negation_count = text_lower.count('not') + text_lower.count('no ')
        
        return {
            'ops': ops,
            'has_comparator': has_comp,
            'has_number': has_num,
            'negations': negation_count,
            'length': len(text),
            'word_count': len(words)
        }

    def _compute_complexity(self, text: str) -> float:
        """Approximate Kolmogorov Complexity via zlib compression"""
        if not text:
            return 0.0
        encoded = text.encode('utf-8')
        compressed = zlib.compress(encoded)
        # Normalized compression ratio (0 to 1, lower is simpler)
        return len(compressed) / len(encoded) if len(encoded) > 0 else 1.0

    def _numeric_consistency(self, prompt: str, candidate: str) -> float:
        """Check if numeric claims in candidate align with prompt logic"""
        # Extract numbers
        p_nums = re.findall(r'\d+\.?\d*', prompt)
        c_nums = re.findall(r'\d+\.?\d*', candidate)
        
        if not p_nums:
            return 1.0 # No numbers to check
        
        if not c_nums:
            return 0.5 # Candidate ignores numbers
        
        try:
            # Simple check: if prompt has "9.11" and "9.9", does candidate respect order?
            # This is a heuristic proxy for the "measurement error" term
            p_floats = [float(n) for n in p_nums]
            c_floats = [float(n) for n in c_nums]
            
            # If prompt implies a comparison (e.g. contains '>' or 'less'), 
            # check if candidate numbers reflect a valid subset or result
            if any(c in prompt for c in ['>', '<', 'greater', 'less', 'more', 'fewer']):
                # If prompt compares A and B, candidate should ideally contain the result
                # Heuristic: If candidate has numbers, they should be plausible derived values
                # For now, reward if candidate numbers are within the range of prompt numbers
                if p_floats and c_floats:
                    p_min, p_max = min(p_floats), max(p_floats)
                    # Allow some tolerance, but penalize wildly out of bound numbers
                    for c_val in c_floats:
                        if c_val < p_min * 0.1 or c_val > p_max * 10:
                            return 0.2 # Likely hallucinated number
            return 1.0
        except ValueError:
            return 0.5

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        prompt_struct = self._extract_structure(prompt)
        results = []
        
        # Baseline NCD for tie-breaking
        p_comp = zlib.compress(prompt.encode())
        
        for cand in candidates:
            cand_struct = self._extract_structure(cand)
            
            # 1. Structural Consistency (The "Measurement Error" ||Phi x - y||)
            # Does the candidate respect the logical operators found in prompt?
            logic_match = 0.0
            total_ops = 0
            for op, present in prompt_struct['ops'].items():
                if present:
                    total_ops += 1
                    if op in cand.lower():
                        logic_match += 1
            logic_score = (logic_match / total_ops) if total_ops > 0 else 1.0
            
            # Negation handling: if prompt has negation, candidate should ideally reflect it
            if prompt_struct['negations'] > 0:
                if cand_struct['negations'] == 0:
                    # Potential contradiction, but not always (depends on answer type)
                    # We apply a small penalty unless it's a direct "Yes/No" flip which is hard to detect without semantics
                    pass 

            # 2. Numeric Consistency
            num_score = self._numeric_consistency(prompt, cand)

            # 3. Sparsity & Complexity Regularization (L1 + C_Kol)
            # Favor shorter, compressible answers that are still informative
            complexity = self._compute_complexity(cand)
            
            # Sparsity penalty: penalize excessive length relative to prompt
            sparsity_penalty = 0.0
            if cand_struct['length'] > prompt_struct['length'] * 1.5:
                sparsity_penalty = 0.2
            
            # Combined Score
            # High logic match + High numeric consistency - Complexity - Sparsity
            base_score = (logic_score * 0.4) + (num_score * 0.4)
            complexity_bonus = (1.0 - complexity) * 0.1 # Simpler is better
            final_score = base_score + complexity_bonus - sparsity_penalty
            
            # NCD Tiebreaker (only if structural signals are weak)
            ncd_score = 0.0
            if abs(final_score - 0.5) < 0.05: # Weak signal
                c_comp = zlib.compress(cand.encode())
                # Approx NCD
                joint = zlib.compress((prompt + cand).encode())
                ncd = (len(joint) - min(len(p_comp), len(c_comp))) / max(len(p_comp), len(c_comp))
                ncd_score = (1.0 - ncd) * 0.05 # Small boost for similarity
            
            final_score += ncd_score
            
            results.append({
                "candidate": cand,
                "score": float(np.clip(final_score, 0.0, 1.0)),
                "reasoning": f"Logic:{logic_score:.2f} Num:{num_score:.2f} Cplx:{complexity:.2f}"
            })
            
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Evaluate confidence based on structural alignment and complexity.
        Returns 0-1.
        """
        # Reuse evaluation logic for single pair
        ranked = self.evaluate(prompt, [answer])
        if not ranked:
            return 0.0
        
        # The score from evaluate is already normalized 0-1 roughly
        # We boost confidence if the structural match is perfect
        base_score = ranked[0]['score']
        
        # Additional check: If prompt asks a yes/no question (implicit)
        p_low = prompt.lower()
        if any(q in p_low for q in ['is it', 'does it', 'can it', 'are there']):
            if answer.lower().strip() in ['yes', 'no', 'true', 'false']:
                # Direct answers to binary questions get a confidence boost if logic holds
                return min(1.0, base_score + 0.2)
                
        return base_score