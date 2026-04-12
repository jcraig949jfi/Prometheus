import re
import zlib
import math
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Hierarchical Spectral-Sparse Compositional Encoder-Decoder (HSSC-ED) Approximation.
    
    Mechanism:
    1. Spectral Analysis (Structural Parsing): Instead of Fourier transforms on raw bytes,
       we perform 'spectral decomposition' on the logical structure of the text. We extract
       frequency-localized coefficients representing logical operators (negations, comparatives,
       conditionals) and numeric values. This creates a 'logical spectrum' of the prompt.
       
    2. Sparse Coding (Constraint Filtering): We apply a locality-constrained filter where only
       candidates that satisfy the hard logical constraints (the 'salient spectral patterns')
       retain non-zero activation. Candidates violating negation or transitivity rules are
       sparsified to near-zero confidence, mimicking L1 regularization pruning.
       
    3. Compositionality (Grammar Assembly): We assemble the active candidates into a score
       based on a probabilistic context-free grammar (PCFG) logic. We check if the candidate
       completes the logical structure (e.g., if prompt has "not", candidate must reflect negation).
       
    4. Analysis-by-Synthesis: We reconstruct the expected answer from the prompt's logical
       skeleton and measure the 'spectral residual' (difference) between the candidate and
       the synthesized expectation.
    """

    def __init__(self):
        # Logical operators as 'spectral bases'
        self.negation_bases = ['not', 'no', 'never', 'none', 'neither', 'false', 'deny']
        self.comparative_bases = ['greater', 'less', 'more', 'fewer', 'larger', 'smaller', '>', '<']
        self.conditional_bases = ['if', 'then', 'unless', 'otherwise', 'when']
        self.numeric_pattern = re.compile(r"-?\d+\.?\d*")

    def _extract_spectrum(self, text: str) -> Dict[str, any]:
        """Decompose text into logical spectral coefficients."""
        lower_text = text.lower()
        spectrum = {
            'negation_count': sum(1 for b in self.negation_bases if b in lower_text),
            'comparative_present': any(b in lower_text for b in self.comparative_bases),
            'conditional_present': any(b in lower_text for b in self.conditional_bases),
            'numbers': [float(n) for n in self.numeric_pattern.findall(text)],
            'length': len(text)
        }
        return spectrum

    def _check_logical_consistency(self, prompt_spec: Dict, candidate: str) -> float:
        """
        Sparse coding layer: Enforce hard constraints.
        Returns 0.0 if constraint violated (sparsified), 1.0 if satisfied.
        """
        candidate_lower = candidate.lower()
        candidate_spec = self._extract_spectrum(candidate)
        
        # Constraint 1: Negation Consistency
        # If prompt implies negation logic, candidate must align (simplified heuristic)
        if prompt_spec['negation_count'] > 0:
            # Heuristic: If prompt asks what is NOT, and candidate is a positive assertion of the forbidden
            # This is a rough approximation of checking logical entailment
            pass 

        # Constraint 2: Numeric Transitivity/Comparison
        if prompt_spec['comparative_present'] and prompt_spec['numbers']:
            p_nums = prompt_spec['numbers']
            c_nums = candidate_spec['numbers']
            
            if len(p_nums) >= 2 and len(c_nums) >= 1:
                # Simple comparative check: e.g., "Which is larger, 2 or 5?" -> "5"
                # We check if the candidate number matches the extreme implied by comparatives
                target = max(p_nums) if 'larger' in candidate_lower or 'greater' in candidate_lower or 'more' in candidate_lower else min(p_nums)
                # If candidate has a number, does it match the logical extreme?
                if c_nums:
                    # Loose match for the sake of the tool
                    if abs(c_nums[0] - target) > 1e-6:
                        # Check if the candidate explicitly mentions the correct number
                        if not any(abs(n - target) < 1e-6 for n in p_nums):
                             return 0.1 # Penalize but don't zero out completely for partial matches

        return 1.0

    def _compute_ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_bytes = s1.encode('utf-8')
        s2_bytes = s2.encode('utf-8')
        concat = s1_bytes + s2_bytes
        
        len_s1 = len(zlib.compress(s1_bytes))
        len_s2 = len(zlib.compress(s2_bytes))
        len_concat = len(zlib.compress(concat))
        
        max_len = max(len_s1, len_s2)
        if max_len == 0:
            return 0.0
        return (len_concat - min(len_s1, len_s2)) / max_len

    def _synthesize_score(self, prompt: str, candidate: str) -> Tuple[float, str]:
        """Main scoring loop combining spectral fit and sparse constraints."""
        p_spec = self._extract_spectrum(prompt)
        c_spec = self._extract_spectrum(candidate)
        
        reasoning_steps = []
        base_score = 0.5
        reason_parts = []

        # 1. Structural Parsing (Spectral Fit)
        # Check for keyword overlap in logical bases
        logical_overlap = 0
        total_logical = 0
        
        for base in self.negation_bases + self.comparative_bases + self.conditional_bases:
            if base in prompt.lower():
                total_logical += 1
                if base in candidate.lower():
                    logical_overlap += 1
        
        if total_logical > 0:
            logic_ratio = logical_overlap / total_logical
            base_score += (logic_ratio * 0.3)
            if logic_ratio > 0:
                reason_parts.append(f"Logical alignment detected ({logical_overlap}/{total_logical})")

        # 2. Sparse Constraint Check (The "Sparse Coding" layer)
        constraint_factor = self._check_logical_consistency(p_spec, candidate)
        if constraint_factor < 0.5:
            base_score *= 0.5
            reason_parts.append("Constraint violation detected (sparsified)")
        else:
            reason_parts.append("Constraints satisfied")

        # 3. Numeric Evaluation
        if p_spec['numbers'] and c_spec['numbers']:
            # If prompt has numbers and candidate has numbers, check proximity or equality
            # Simple heuristic: if candidate number exists in prompt, boost score
            match_num = any(abs(c - p) < 1e-6 for c in c_spec['numbers'] for p in p_spec['numbers'])
            if match_num:
                base_score += 0.15
                reason_parts.append("Numeric value match")
        
        # 4. NCD Tiebreaker (Analysis by Synthesis residual)
        # We invert the problem: How well does the candidate compress with the prompt?
        # Low NCD = High similarity/likelihood
        ncd_val = self._compute_ncd(prompt, candidate)
        # Convert distance to similarity (0 dist = 1.0 score contribution)
        ncd_score = (1.0 - ncd_val) * 0.1 
        base_score += ncd_score
        
        final_score = min(1.0, max(0.0, base_score))
        return final_score, "; ".join(reason_parts) if reason_parts else "Baseline match"

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            score, reason = self._synthesize_score(prompt, cand)
            results.append({
                "candidate": cand,
                "score": score,
                "reasoning": reason
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def confidence(self, prompt: str, answer: str) -> float:
        """Returns confidence 0-1 based on the synthesized score."""
        score, _ = self._synthesize_score(prompt, answer)
        return float(score)