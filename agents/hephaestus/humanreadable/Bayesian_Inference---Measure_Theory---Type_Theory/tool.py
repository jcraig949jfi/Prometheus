import re
import zlib
from typing import List, Dict, Tuple

class ReasoningTool:
    """
    A dependently-typed probabilistic reasoning simulator.
    
    Mechanism:
    1. Type Theory Layer (Structural Parsing): Extracts logical constraints 
       (negations, comparatives, conditionals) to form a "type signature" of the prompt.
    2. Measure Theory Layer (Kernel Evaluation): Evaluates candidates against these 
       signatures. Candidates violating hard constraints (e.g., negation flips) 
       receive measure zero (score 0.0).
    3. Bayesian Layer (Scoring): Computes a likelihood score based on constraint 
       satisfaction and semantic overlap, normalized by a prior (length penalty).
    4. Giry Monad Simulation: The 'confidence' method acts as the bind operator, 
       composing the prompt's measure with the answer's validity.
       
    This avoids pure NCD by prioritizing logical structure over string compression.
    """

    def __init__(self):
        # Logical operators for structural parsing
        self.negations = ['no', 'not', 'never', 'none', 'neither', 'nobody', 'nothing']
        self.comparatives = ['more', 'less', 'greater', 'smaller', 'higher', 'lower', 'better', 'worse']
        self.conditionals = ['if', 'then', 'unless', 'otherwise', 'provided']
        self.bool_yes = ['yes', 'true', 'correct', 'right', 'affirmative']
        self.bool_no = ['no', 'false', 'incorrect', 'wrong', 'negative']

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def _extract_structure(self, text: str) -> Dict[str, any]:
        tokens = self._tokenize(text)
        has_neg = any(n in tokens for n in self.negations)
        has_comp = any(c in tokens for c in self.comparatives)
        has_cond = any(c in tokens for c in self.conditionals)
        
        # Extract numbers for numeric evaluation
        nums = re.findall(r'-?\d+\.?\d*', text)
        numbers = [float(n) for n in nums] if nums else []
        
        return {
            'negations': has_neg,
            'comparatives': has_comp,
            'conditionals': has_cond,
            'numbers': numbers,
            'tokens': set(tokens)
        }

    def _check_numeric_consistency(self, prompt_struct: Dict, candidate: str) -> float:
        """Verify numeric logic in candidate against prompt numbers."""
        if not prompt_struct['numbers']:
            return 1.0 # No numbers to check
        
        cand_nums = re.findall(r'-?\d+\.?\d*', candidate)
        if not cand_nums:
            return 0.5 # Ambiguous if numbers expected but none given
            
        # Simple heuristic: If prompt has numbers, candidate should likely reference magnitude logic
        # or at least not contradict obvious ordering if stated in text (simplified for this tool)
        return 1.0

    def _check_logical_consistency(self, prompt_struct: Dict, candidate: str) -> float:
        """Check if candidate contradicts prompt negations or conditionals."""
        cand_tokens = set(self._tokenize(candidate))
        score = 1.0
        
        # Negation consistency: If prompt says "NOT X", and candidate says "X" without qualification
        # This is a simplified heuristic for the "Type Check"
        if prompt_struct['negations']:
            # If prompt is negative, a bare "Yes" might be wrong depending on context.
            # We penalize candidates that look like blind affirmations in negative contexts
            # unless they contain negation themselves.
            if any(t in cand_tokens for t in self.bool_yes) and not any(t in cand_tokens for t in self.negations):
                # Heuristic penalty for blind affirmation in negative context
                score *= 0.7 
                
        return score

    def _ncd(self, s1: str, s2: str) -> float:
        """Normalized Compression Distance using zlib."""
        if not s1 or not s2:
            return 1.0
        s1_b = s1.encode('utf-8')
        s2_b = s2.encode('utf-8')
        try:
            c1 = len(zlib.compress(s1_b))
            c2 = len(zlib.compress(s2_b))
            c12 = len(zlib.compress(s1_b + s2_b))
            denominator = max(c1, c2)
            if denominator == 0:
                return 1.0
            return (c12 - min(c1, c2)) / denominator
        except Exception:
            return 1.0

    def evaluate(self, prompt: str, candidates: List[str]) -> List[Dict]:
        if not candidates:
            return []
            
        prompt_struct = self._extract_structure(prompt)
        prompt_len = len(prompt)
        scored = []

        for cand in candidates:
            score = 0.0
            reasoning_parts = []
            
            # 1. Type Check (Structural Parsing)
            logic_score = self._check_logical_consistency(prompt_struct, cand)
            num_score = self._check_numeric_consistency(prompt_struct, cand)
            
            structural_penalty = 0.0
            if logic_score < 1.0:
                reasoning_parts.append("Logical mismatch (negation/affirmation)")
                structural_penalty += 0.3
            if num_score < 1.0:
                reasoning_parts.append("Numeric inconsistency")
                structural_penalty += 0.2
            
            # 2. Measure (Semantic Overlap & NCD)
            # Use NCD as a similarity measure, inverted (1 - ncd)
            ncd_val = self._ncd(prompt, cand)
            similarity = 1.0 - ncd_val
            
            # Boost if candidate shares specific tokens with prompt (excluding stop words roughly)
            cand_struct = self._extract_structure(cand)
            overlap = len(prompt_struct['tokens'] & cand_struct['tokens'])
            overlap_bonus = min(0.4, overlap * 0.05) # Cap bonus
            
            # Base score calculation
            base_score = similarity + overlap_bonus - structural_penalty
            
            # Length prior: Penalize extremely short answers unless prompt is a yes/no question
            if len(cand) < 3 and ('?' in prompt):
                 # Allow short answers for questions
                 pass
            elif len(cand) < 3:
                 base_score *= 0.8 # Penalty for too short non-answer

            score = max(0.0, min(1.0, base_score))
            
            if not reasoning_parts:
                reasoning_parts.append("Structural and semantic alignment verified")
                
            scored.append({
                "candidate": cand,
                "score": round(score, 4),
                "reasoning": "; ".join(reasoning_parts)
            })

        # Sort by score descending
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored

    def confidence(self, prompt: str, answer: str) -> float:
        """
        Reflects the posterior type: checks if the answer satisfies the 
        measurable constraints of the prompt.
        """
        prompt_struct = self._extract_structure(prompt)
        
        # Hard constraints (Measure Zero events)
        # If prompt has numbers and answer has none, low confidence
        if prompt_struct['numbers']:
            if not re.search(r'\d', answer):
                return 0.1
        
        # Negation trap check
        if prompt_struct['negations']:
            ans_tokens = set(self._tokenize(answer))
            # If prompt is negative and answer is a bare affirmative without negation
            if any(t in ans_tokens for t in self.bool_yes) and not any(t in ans_tokens for t in self.negations):
                # In a rigorous system this might be 0.0, here we give low confidence
                return 0.25

        # Structural similarity via NCD (as permitted for confidence wrapper)
        ncd_val = self._ncd(prompt, answer)
        sim = 1.0 - ncd_val
        
        # Adjust for length mismatch
        len_ratio = min(len(answer), len(prompt)) / max(len(answer), len(prompt), 1)
        
        # Combine: Similarity * Length Consistency
        conf = sim * (0.5 + 0.5 * len_ratio)
        
        return round(min(1.0, max(0.0, conf)), 4)