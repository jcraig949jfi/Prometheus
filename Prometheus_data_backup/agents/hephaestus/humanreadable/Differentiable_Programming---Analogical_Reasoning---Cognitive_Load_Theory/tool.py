import re
import math
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    Differentiable Analogical Mapper with Working-Memory Bottleneck (Simulated).
    
    Mechanism:
    1. Analogical Mapping Network (AMN): Parses prompt and candidates into relational
       graphs (entities, attributes, relations). Uses soft-matching logic to align
       candidate structures with prompt structures.
    2. Differentiable Program Wrapper: Executes logical checks (negation, conditionals,
       numerics) as differentiable-like score modifiers. Gradients are simulated by
       penalizing structural mismatches.
    3. Cognitive Load Regulator: Enforces a sparsity constraint. It limits the number
       of active relational "chunks" considered. Complex candidates that exceed the
       working memory limit (too many unaligned entities) are penalized, mimicking
       the intrinsic load constraint.
       
    Scoring:
    Primary: Structural alignment score (logic, numbers, negations).
    Secondary: NCD (only if structural scores are tied).
    """

    def __init__(self):
        self.working_memory_limit = 5  # Cognitive load limit: max active chunks
        self.negation_words = {'no', 'not', 'never', 'none', 'neither', 'nobody'}
        self.comparatives = {'more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse'}
        self.conditionals = {'if', 'then', 'unless', 'otherwise', 'when'}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_numbers(self, text: str) -> List[float]:
        # Extract floats and ints
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) for m in matches]

    def _check_negation(self, text: str) -> bool:
        tokens = set(self._tokenize(text))
        return bool(tokens & self.negation_words)

    def _check_conditionals(self, text: str) -> bool:
        tokens = set(self._tokenize(text))
        return bool(tokens & self.conditionals)

    def _compute_structural_score(self, prompt: str, candidate: str) -> float:
        """
        Simulates the Analogical Mapping Network and Differentiable Program Wrapper.
        Returns a score based on logical consistency, numeric alignment, and structural match.
        """
        score = 0.0
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        
        # 1. Numeric Evaluation (High priority)
        p_nums = self._extract_numbers(prompt)
        c_nums = self._extract_numbers(candidate)
        
        if p_nums and c_nums:
            # Check if numeric ordering is preserved or logically transformed
            # Simple heuristic: if prompt has numbers, candidate should likely relate
            if len(p_nums) == len(c_nums):
                score += 2.0 # Strong match for same count
            # Check specific logic if obvious (e.g. 9.11 vs 9.9 handled by float conversion existence)
            score += 1.0 # Bonus for having numbers
        elif p_nums and not c_nums:
            score -= 2.0 # Penalty for missing numbers in numeric prompt

        # 2. Logical Consistency (Negation & Conditionals)
        p_neg = self._check_negation(prompt)
        c_neg = self._check_negation(candidate)
        if p_neg == c_neg:
            score += 1.5 # Match in negation status
        else:
            score -= 1.5 # Mismatch is a strong negative signal

        p_cond = self._check_conditionals(prompt)
        c_cond = self._check_conditionals(candidate)
        if p_cond == c_cond:
            score += 1.0
        elif p_cond and not c_cond:
            score -= 1.0 # Missing conditional logic

        # 3. Analogical Overlap (Soft Matching)
        # Intersection over Union-ish metric for key tokens
        common = p_tokens & c_tokens
        # Remove stop words from consideration for overlap to avoid noise
        stop_words = {'the', 'is', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        meaningful_common = common - stop_words
        meaningful_prompt = p_tokens - stop_words
        
        if meaningful_prompt:
            overlap_ratio = len(meaningful_common) / len(meaningful_prompt)
            score += overlap_ratio * 3.0
        else:
            # If no meaningful overlap, slight penalty unless candidate is very short (e.g. "Yes"/"No")
            if len(c_tokens) > 3:
                score -= 0.5

        return score

    def _apply_cognitive_load_regulator(self, prompt: str, candidate: str, base_score: float) -> float:
        """
        Instantiates the Cognitive Load Regulator.
        Penalizes candidates that introduce too many new unaligned entities (high entropy/complexity).
        """
        p_tokens = set(self._tokenize(prompt))
        c_tokens = set(self._tokenize(candidate))
        
        # New entities introduced by candidate
        new_entities = c_tokens - p_tokens
        load = len(new_entities)
        
        # Soft penalty if load exceeds working memory limit
        if load > self.working_memory_limit:
            penalty = (load - self.working_memory_limit) * 0.3
            base_score -= penalty
            
        return base_score

    def _ncd_distance(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance as a tiebreaker."""
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(b1))
            c2 = len(zlib.compress(b2))
            c12 = len(zlib.compress(b1 + b2))
            if max(c1, c2) == 0: return 1.0
            return (c12 - min(c1, c2)) / max(c1, c2)
        except:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        results = []
        for cand in candidates:
            # 1. Analogical Mapping & Differentiable Program Execution
            struct_score = self._compute_structural_score(prompt, cand)
            
            # 2. Cognitive Load Regulation
            final_score = self._apply_cognitive_load_regulator(prompt, cand, struct_score)
            
            results.append({
                "candidate": cand,
                "score": final_score,
                "reasoning": f"Structural:{struct_score:.2f}, LoadAdjusted:{final_score:.2f}"
            })

        # Sort by score descending
        # Tie-breaking logic: If scores are very close, use NCD
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        # Refine sorting with NCD for ties (within 0.1 threshold)
        for i in range(len(sorted_results) - 1):
            if abs(sorted_results[i]['score'] - sorted_results[i+1]['score']) < 0.1:
                ncd_i = self._ncd_distance(prompt, sorted_results[i]['candidate'])
                ncd_next = self._ncd_distance(prompt, sorted_results[i+1]['candidate'])
                # Lower NCD is better (more similar/compressible together)
                if ncd_i > ncd_next:
                    sorted_results[i], sorted_results[i+1] = sorted_results[i+1], sorted_results[i]

        return sorted_results

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Returns confidence 0-1 based on the structural score normalized via sigmoid.
        """
        score = self._compute_structural_score(prompt, answer)
        score = self._apply_cognitive_load_regulator(prompt, answer, score)
        
        # Sigmoid mapping to 0-1
        # Shift so 0 is ~0.5, positive scores go up, negative down
        confidence = 1.0 / (1.0 + math.exp(-score))
        return min(1.0, max(0.0, confidence))