import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Renormalization-Guided Optimal Sparse Encoder (ROSE) Approximation.
    
    Mechanism:
    1. Structural Parsing (Optimal Control Proxy): Extracts logical operators 
       (negations, comparatives, conditionals) and numeric values. This acts as 
       the 'control policy' determining the cost landscape, avoiding direct 
       heavy optimal control solvers which are historically inhibitors.
    2. Multiscale Sparse Coding (Renormalization + Sparse Coding): 
       - Scale 1 (Fine): Exact token overlap between prompt and candidate.
       - Scale 2 (Coarse): Semantic block overlap (splitting by logical delimiters).
       - Scale 3 (Renormalized): Compressed representation similarity (NCD).
       The 'sparsity' is approximated by penalizing candidates that require 
       many active tokens to represent the prompt's core constraints.
    3. Scoring: A weighted sum of structural adherence (highest weight), 
       multiscale overlap, and compression distance (tiebreaker).
    """

    def __init__(self):
        # Logical operators for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'n\'t']
        self.comparatives = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<', '>=', '<=']
        self.conditionals = ['if', 'then', 'else', 'unless', 'provided']
        self.delimiters = re.compile(r'[,\.;\?\!:]')

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer: lowercase and split by non-alphanumeric."""
        return re.findall(r'[a-z0-9]+', text.lower())

    def _extract_structure(self, text: str) -> Dict[str, any]:
        """Extract logical structure: negations, comparatives, conditionals, numbers."""
        lower_text = text.lower()
        tokens = self._tokenize(text)
        
        has_negation = any(n in lower_text for n in self.negations)
        has_comparative = any(c in lower_text for c in self.comparatives)
        has_conditional = any(c in lower_text for c in self.conditionals)
        
        # Extract numbers for numeric evaluation
        numbers = re.findall(r'-?\d+\.?\d*', text)
        nums = [float(n) for n in numbers]
        
        return {
            'neg_count': sum(tokens.count(n) for n in self.negations),
            'comp_count': sum(1 for c in self.comparatives if c in lower_text),
            'cond_count': sum(1 for c in self.conditionals if c in lower_text),
            'numbers': nums,
            'num_count': len(nums)
        }

    def _structural_match_score(self, prompt_struct: Dict, cand_struct: Dict) -> float:
        """
        Evaluate if the candidate respects the logical constraints of the prompt.
        This is the primary scoring signal (Optimal Control Proxy).
        """
        score = 0.0
        
        # Negation consistency: If prompt has negation, candidate should ideally reflect it 
        # or not contradict it. Simple heuristic: match counts roughly.
        if prompt_struct['neg_count'] > 0:
            if cand_struct['neg_count'] > 0:
                score += 0.4
            else:
                score -= 0.5 # Penalty for missing negation
        
        # Comparative consistency
        if prompt_struct['comp_count'] > 0:
            if cand_struct['comp_count'] > 0:
                score += 0.3
            # Missing comparative in answer when prompt asks for one is a soft penalty
            # unless the answer is purely numeric
        
        # Conditional consistency
        if prompt_struct['cond_count'] > 0:
            if cand_struct['cond_count'] > 0:
                score += 0.2
                
        # Numeric evaluation: If both have numbers, check simple relations if detectable
        # (e.g., if prompt implies "larger", answer should be larger)
        # For this general implementation, we reward presence of numbers if prompt has them
        if prompt_struct['num_count'] > 0:
            if cand_struct['num_count'] > 0:
                score += 0.3
            else:
                score -= 0.4

        return score

    def _sparse_coding_score(self, prompt: str, candidate: str) -> float:
        """
        Multiscale sparse coding approximation.
        Scale 1: Token overlap (Fine)
        Scale 2: Block/Phrase overlap (Coarse)
        """
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        
        if not p_tokens or not c_tokens:
            return 0.0

        # Scale 1: Jaccard similarity on tokens (Sparse activation)
        intersection = p_tokens.intersection(c_tokens)
        union = p_tokens.union(c_tokens)
        scale1 = len(intersection) / len(union) if union else 0.0

        # Scale 2: Coarse graining by splitting on delimiters
        p_blocks = set(b.strip().lower() for b in self.delimiters.split(prompt) if b.strip())
        c_blocks = set(b.strip().lower() for b in self.delimiters.split(candidate) if b.strip())
        
        # Filter to significant blocks (length > 3 to avoid noise)
        p_blocks = {b for b in p_blocks if len(b) > 3}
        c_blocks = {b for b in c_blocks if len(b) > 3}
        
        scale2 = 0.0
        if p_blocks and c_blocks:
            # Check how many prompt blocks are covered by candidate blocks (or vice versa)
            # Since candidate is usually short, check if candidate block exists in prompt
            matches = sum(1 for b in c_blocks if b in p_blocks)
            scale2 = matches / max(len(c_blocks), 1)
        elif not c_blocks and not p_blocks:
            scale2 = 1.0 # Both empty at this scale

        return 0.6 * scale1 + 0.4 * scale2

    def _ncd_score(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_s1_s2 = len(zlib.compress(s1_bytes + s2_bytes))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
            
        ncd = (len_s1_s2 - min(len_s1, len_s2)) / max_len
        return 1.0 - ncd # Convert distance to similarity

    def _compute_cost(self, prompt: str, candidate: str) -> float:
        """
        Compute the total cost (inverted to score).
        Low representational cost = High Score.
        """
        p_struct = self._extract_structure(prompt)
        c_struct = self._extract_structure(candidate)
        
        # 1. Structural Control Signal (Weight: 0.6)
        struct_score = self._structural_match_score(p_struct, c_struct)
        # Normalize struct_score roughly to 0-1 range based on max possible (1.2)
        struct_normalized = (struct_score + 1.0) / 2.0 
        struct_normalized = max(0.0, min(1.0, struct_normalized))

        # 2. Multiscale Sparse Coding Signal (Weight: 0.3)
        sparse_score = self._sparse_coding_score(prompt, candidate)

        # 3. NCD Tiebreaker (Weight: 0.1)
        ncd_score = self._ncd_score(prompt, candidate)

        # Combined Score
        total_score = (0.6 * struct_normalized) + (0.3 * sparse_score) + (0.1 * ncd_score)
        return total_score

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score = self._compute_cost(prompt, cand)
            reasoning = f"Structural match and multiscale overlap yielded score {score:.4f}"
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reasoning
            })
        
        # Rank by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the computed cost/score.
        Uses the same internal mechanism as evaluate but for a single pair.
        """
        score = self._compute_cost(prompt, answer)
        # Ensure bounded [0, 1]
        return max(0.0, min(1.0, score))